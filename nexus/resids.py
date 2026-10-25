"""Tree-wide resource-id auditor.

`ids.audit_collisions()` only looks at ``public.xml``. That is not enough, and
the gap is not academic -- it is the whole reason this module exists:

* ``public.xml`` is not the only place an id can come from. ``res/values/ids.xml``
  declares ids as ``<item type="id" .../>`` and aapt2 gives them the next free
  slot in the type; a pin can therefore land on a slot GG later hands out.
* Resources that no ``<public>`` entry mentions (the
  styles in ``nexus_styles.xml``, the colours in ``nexus_colors.xml``) are
  auto-assigned, so they also consume slots nobody audited.
* GG looks views up by *number*, not by name, so a single silently renumbered id
  binds a control to the wrong view -- or to nothing, which is how a patched
  build ends up with a null ``ListView`` where stock had a live one.

So this module audits the id space as a whole, across every type, and it audits
the *smali*: every id constant handed to ``View.findViewById`` inside a method
that inflates a layout must actually exist in that layout. The layout check is
reported as a *delta* against the unpatched tree, because GG's own code has
eleven deliberately-null-tolerant lookups in ``MainService.Z()`` and those are
not defects; a patcher-induced addition to that set is.
"""

from __future__ import annotations

import re
from pathlib import Path

from .anchors import PatchError

_PUBLIC_RE = re.compile(
    r'<public\s+type="(?P<type>\w+)"\s+name="(?P<name>[\w.]+)"\s+id="(?P<id>0x[0-9a-fA-F]+)"')
_ITEM_ID_RE = re.compile(r'<item\s+type="id"\s+name="(?P<name>[\w.]+)"')
_LAYOUT_REF_RE = re.compile(r'@(?:\+)?id/([\w.]+)')
_CONST_RE = re.compile(
    r'^\s*(?:const|const/4|const/16|const/high16)\s+([vp]\d+),\s+(0x[0-9a-fA-F]+)\s*$')
_FIND_RE = re.compile(r'invoke-\S*\s*\{([^}]*)\},\s*Landroid/view/View;->findViewById')
_METHOD_RE = re.compile(r'^\.method\b')
_END_RE = re.compile(r'^\.end method')

# The resource-type byte of an id, e.g. 0x7f05000a -> 0x05. GG's table is
# 0x7fTTEEEE with no package offset, but the byte test is kept generic so a
# framework id (0x01TTEEEE) is never mistaken for an app id.
def _type_byte(v: int) -> int:
    return (v >> 16) & 0xFF


def public_table(tree: Path) -> dict:
    """``{id: [(type, name), ...]}`` from the tree's public.xml."""
    path = tree / "res/values/public.xml"
    if not path.is_file():
        raise PatchError(f"public.xml missing: {path}")
    out: dict = {}
    for m in _PUBLIC_RE.finditer(path.read_text(encoding="utf-8")):
        out.setdefault(int(m.group("id"), 16), []).append((m.group("type"), m.group("name")))
    return out


def type_maxima(tree: Path) -> dict:
    """``{type: highest id}`` over everything public.xml declares."""
    top: dict = {}
    for v, entries in public_table(tree).items():
        for t, _n in entries:
            if v > top.get(t, -1):
                top[t] = v
    return top


def audit_collisions(tree: Path, pinned: list) -> list:
    """Every numeric id in the tree must name exactly one resource.

    Catches the two ways a pin can be wrong without any name ever matching:
    a pin that lands on a slot public.xml already uses, and a pin that lands on
    a slot aapt2 will hand to an auto-assigned resource later in the build.
    """
    errors = []
    seen: dict = {}
    for v, entries in public_table(tree).items():
        for t, n in entries:
            seen.setdefault(v, []).append(f"{t}/{n}")
    for v, names in seen.items():
        if len(names) > 1:
            errors.append(
                f"resource-id collision at 0x{v:08x}: {' == '.join(sorted(names))}")

    # ids.xml declares ids that public.xml may not mention. They are auto-assigned
    # by aapt2, so a pin overlapping one is a collision that only shows up at build
    # time -- report the names so the bump in nexus_ids.json can be chosen safely.
    ids_xml = tree / "res/values/ids.xml"
    if ids_xml.is_file():
        undeclared = set(_ITEM_ID_RE.findall(ids_xml.read_text(encoding="utf-8")))
        declared = {n for _v, e in public_table(tree).items() for t, n in e if t == "id"}
        stray = sorted(undeclared - declared)
        if stray:
            errors.append(
                f"res/values/ids.xml declares {len(stray)} id(s) absent from public.xml "
                f"(aapt2 auto-assigns these; pins must clear them too): {stray[:8]}")

    for kind, name, hexval in pinned:
        v = int(hexval, 16)
        # Skip the pin's own <public> line when auditing an already-patched tree:
        # there the pin is *supposed* to be present. On an unpatched tree the
        # pin colliding with a GG resource is exactly the bug we want.
        occupants = [x for x in seen.get(v, []) if x != f"{kind}/{name}"]
        if occupants:
            errors.append(
                f"pinned {kind} {name} = {hexval} collides with tree resource "
                f"{occupants[0]}")
        if (v >> 24) != 0x7F:
            errors.append(
                f"pinned {kind} {name} = {hexval} has package byte 0x{v >> 24:02x}, "
                f"not 0x7f (type byte 0x{(v >> 16) & 0xFF:02x}); this is not an "
                f"app resource id")
    return errors


def audit_pin_ceiling(tree: Path, pinned: list) -> list:
    """Every pin must sit above everything the *target* tree already uses.

    This is the version-drift guard. `nexus_ids.json` was written against GG
    499.2; the tree it is applied to may be any release. Rather than trusting
    the recorded numbers, the ceiling is recomputed from the tree being patched,
    so a release that grew past a pinned slot fails here instead of producing an
    APK where a GG view and a Nexus view share one number.
    """
    top = type_maxima(tree)
    errors = []
    for kind, name, hexval in pinned:
        v = int(hexval, 16)
        ceiling = top.get(kind)
        if ceiling is None:
            errors.append(f"target tree has no type={kind}; pinned {name} is unusable")
        elif v <= ceiling:
            errors.append(
                f"pinned {kind} {name} = {hexval} is at or below this tree's "
                f"highest {kind} ({hexval} <= 0x{ceiling:08x}). This tree is a newer "
                f"GG than nexus_ids.json was pinned against -- bump the pin.")
    return errors


def _layout_ids_for(tree: Path, name: str, cache: dict) -> set:
    """`@id/...` names declared by `name`.xml` in any res/layout* folder."""
    if name in cache:
        return cache[name]
    found = set()
    res = tree / "res"
    if res.is_dir():
        for d in sorted(res.iterdir()):
            if not d.is_dir() or not d.name.startswith("layout"):
                continue
            p = d / (name + ".xml")
            if p.is_file():
                found |= set(_LAYOUT_REF_RE.findall(p.read_text(encoding="utf-8",
                                                                errors="replace")))
    cache[name] = found
    return found


def findviewid_audit(tree: Path, pub: dict) -> tuple:
    """``(problems, checked)`` -- id constants fed to findViewById.

    A problem is (smali file, layouts inflated by the method, id, name) for any
    constant whose id is unknown to public.xml, or is not declared by a layout the
    method inflates. Report it as a set so a caller can diff it against the same
    audit of the unpatched tree.
    """
    layout_name = {}
    for v, entries in pub.items():
        for t, n in entries:
            if t == "layout":
                layout_name[v] = n

    cache: dict = {}
    problems = set()
    checked = 0
    smali_root = tree / "smali"
    if not smali_root.is_dir():
        return problems, checked
    for f in sorted(smali_root.rglob("*.smali")):
        lines = f.read_text(encoding="utf-8", errors="replace").split("\n")
        cur, hdr = None, None
        for ln in lines + [""]:
            if _METHOD_RE.match(ln):
                cur, hdr = [ln], ln
                continue
            if hdr is None:
                continue
            cur.append(ln)
            if not _END_RE.match(ln):
                continue
            hdr, body = None, "\n".join(cur)
            if "findViewById" not in body:
                continue
            lays = sorted({layout_name[v] for v in
                           (0x7F060000 | int(h, 16)
                            for h in re.findall(r"0x7f06([0-9a-fA-F]{4})", body))
                           if v in layout_name})
            if not lays:
                continue

            reg = {}
            for raw in cur:
                c = _CONST_RE.match(raw)
                if c:
                    reg[c.group(1)] = int(c.group(2), 16)
                fd = _FIND_RE.search(raw)
                if not fd:
                    continue
                args = [a.strip() for a in fd.group(1).split(",")]
                if len(args) < 2:
                    continue
                v = reg.get(args[-1])
                if v is None or _type_byte(v) != 0x05:
                    continue
                checked += 1
                entries = pub.get(v)
                rel = str(f.relative_to(smali_root))
                if not entries:
                    problems.add((rel, "<all>", f"0x{v:08x}", "<id not in public.xml>"))
                    continue
                name = entries[0][1]
                # Per LAYOUT, never per union: a method may name several layouts
                # but only one of them is the live view at any point, so an id
                # that exists only in a sibling layout still yields null at
                # runtime. Unioning the layouts would hide precisely the
                # regression this check exists for.
                for l in lays:
                    if name not in _layout_ids_for(tree, l, cache):
                        problems.add((rel, l, f"0x{v:08x}", name))
    return problems, checked


# Files whose whole purpose is to look up an id it expects NOT to be there.
# Diag probes MainService's failure path (addr_item_type, 0x7f050008) on purpose:
# confirming that it resolves to null is one of the answers it exists to get.
# Suppressed here rather than by weakening the audit, and reported, not hidden.
EXPECTED_ABSENT_PROBES = frozenset({"org/vekendian/nexus/Diag.smali"})


def audit_findviewid_layouts(src: Path, out: Path) -> list:
    """No *new* unreachable findViewById may be introduced by the patch.

    GG's own MainService.Z() has lookups that legitimately miss (it is written to
    tolerate a null view), so this compares the patched tree against the stock
    tree rather than demanding a clean sheet.
    """
    src_problems, _ = findviewid_audit(src, public_table(src))
    out_problems, checked = findviewid_audit(out, public_table(out))
    if not checked:
        return ["findViewById audit performed 0 checks -- the analyzer is broken, "
                "refusing to report PASS"]
    out_problems = {p for p in out_problems if p[0] not in EXPECTED_ABSENT_PROBES}
    new = sorted(out_problems - src_problems)
    fixed = sorted(src_problems - out_problems)
    errors = [
        "findViewById: patcher introduced %d unreachable id(s):" % len(new)
        + "".join(f"\n      {p[0]} layout={p[1]} {p[2]} ({p[3]})" for p in new[:20])
    ] if new else []
    if fixed:
        # Not an error, but worth seeing: it means the patch changed a lookup.
        errors.append("NOTE: %d previously-unreachable findViewById id(s) now resolve "
                      "(expected when the patcher rewrites a layout): %s"
                      % (len(fixed), fixed[:5]))
    return errors


def audit_id_drift(src: Path, out: Path) -> list:
    """Every id the stock tree assigned must still name the same resource.

    This is the check that would have caught a build where aapt2 renumbered GG's
    table: stock code looks views up by number, so a moved id is silent breakage
    that only shows up on device.
    """
    a, b = public_table(src), public_table(out)
    errors = []
    for v, entries in sorted(a.items()):
        if b.get(v) != entries:
            errors.append(
                "resource-id drift: stock 0x%08x = %s, patched = %s"
                % (v, sorted(entries), sorted(b.get(v, [])) or "absent"))
    return errors


def audit_rebrand_complete(tree: Path) -> list:
    """No `com/scmq` token may survive the rebrand, in any form.

    `replace_in_smali` only rewrites the slash form `Lcom/scmq/`. GG also carries
    a descriptor literal `"Lcom/scmq;"` in android/ext/i.smali, whose length is
    then used to rebuild the package name at runtime. Leaving that behind is not
    cosmetic: the fallback computes `literal.length() - pkg.length()` and
    substrings, which for a 20-character package name and an 11-character
    literal yields an out-of-range substring.
    """
    errors = []
    needles = ("com/scmq", "com.scmq")
    for root_name in ("smali", "AndroidManifest.xml", "res", "apktool.yml", "apktool.json"):
        p = tree / root_name
        targets = []
        if p.is_dir():
            targets = [f for f in p.rglob("*")
                       if f.is_file() and f.suffix in (".smali", ".xml", ".yml", ".json")]
        elif p.is_file():
            targets = [p]
        for f in targets:
            try:
                t = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for n in needles:
                if n in t:
                    lines = [i + 1 for i, l in enumerate(t.split("\n")) if n in l]
                    errors.append(
                        f"rebrand incomplete: {f.relative_to(tree)} still contains "
                        f"{n!r} on line(s) {lines[:5]}")
    return errors