"""Static invoke-arity and register-budget audit of the injected smali.

ART's verifier rejects a class at load time if any `invoke` disagrees with its
callee's signature, or if a method touches a register its `.registers` frame
never declared. Both are *runtime* failures: baksmali accepts them, `apktool b`
assembles them, and every patch-shape test passes -- then the app dies at
launch, before anything renders.

That happened. `nexusModulesName` passed 7 registers to
`ContentResolver.query` (receiver + 5 args = 6), with the receiver last in the
range instead of first:

    VerifyError: android.ext.r.nexusModulesName(...) failed to verify:
    [0x13] invalid argument count (7) exceeds outsSize (6)

So these are checked here instead, offline, against the smali the patcher
actually emits. Descriptor words are counted straight out of the invoke line,
so no signature database is needed -- the callee is named in the instruction.

Checked:

  arity     every invoke supplies exactly the registers its descriptor needs,
            counting the receiver for non-static calls. A non-range invoke may
            not exceed the 5-register limit of the format. A /range invoke must
            span exactly that many registers, contiguously, receiver first.

  budget    no instruction may name a register at or above `.registers`, and
            the frame must be large enough for the widest range invoke.

Deliberately NOT checked: whether a method overwrites one of its own parameter
registers. That is legal dalvik and compiler output does it routinely
(nexusModulesSave overwrites `this` and never reads it again). Distinguishing
that from the fatal variant -- overwrite `this`, then read it -- needs real
dataflow and type analysis; a register-identity heuristic flags the harmless
case too, so it would only produce noise.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexus.tree import RES_DIR

# The files Nexus rewrites wholesale or heavily. f.smali carries the dialog
# injection, ConfigListAdapter the settings highlight, r.smali everything else.
#
# The extension engine is GENERATED (resources/java/host -> baksmali), which is
# exactly why it is audited: compiler output is usually right, and the failure
# mode when the pipeline changes is that it is right for a different reason than
# anyone checked. Same audits, same bar.
AUDITED = [
    "smali/android/ext/r.smali",
    "smali/android/ext/f.smali",
    "smali/android/ext/ConfigListAdapter.smali",
    "smali/org/vekendian/nexus/ModulePicker.smali",
    "smali/org/vekendian/nexus/api/ExtensionApi.smali",
    "smali/org/vekendian/nexus/api/ExtensionType.smali",
    "smali/org/vekendian/nexus/api/ExtensionInfo.smali",
    "smali/org/vekendian/nexus/api/ExtensionInfo$Type.smali",
    "smali/org/vekendian/nexus/api/ExtensionManifest.smali",
    "smali/org/vekendian/nexus/api/NexusExecutor.smali",
    "smali/org/vekendian/nexus/extensions/NexusHost.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionApiImpl.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionCards.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionLoader.smali",
    # The Lua namespaceTemplates are hand-written smali -- exactly the kind of
    # file the static audits exist for.
    "smali/org/vekendian/nexus/lua/NexusLua.smali",
    "smali/org/vekendian/nexus/lua/NexusLua$Extensions.smali",
    "smali/org/vekendian/nexus/lua/NexusLua$Extensions$Fn.smali",
    "smali/org/vekendian/nexus/lua/NexusLua$Perm.smali",
    "smali/org/vekendian/nexus/lua/NexusLua$Perm$Ask.smali",
]

PICKER = "smali/org/vekendian/nexus/ModulePicker.smali"
ENGINE_SHIPPED = [
    "smali/org/vekendian/nexus/ModulePicker.smali",
    "smali/org/vekendian/nexus/extensions/NexusHost.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionLoader.smali",
]


def _tree_root() -> Path | None:
    for base in Path("/mnt/sdcard/#Vekendian/nexus/gameguardian").glob("*/*_nexus_output"):
        if (base / "apktool.yml").is_file():
            return base
    return None


def descriptor_words(desc: str) -> int:
    """Register words a parameter descriptor consumes. J and D take two."""
    n = i = 0
    while i < len(desc):
        c = desc[i]
        if c == "L":
            i = desc.index(";", i) + 1
            n += 1
        elif c == "[":
            i += 1                      # array of the next type; one word
        else:
            n += 2 if c in "JD" else 1
            i += 1
    return n


RANGE_RE = re.compile(
    r"^\s*(invoke-\S+/range)\s*\{\s*([vp]\d+)\s*\.\.\s*([vp]\d+)\s*\},\s*"
    r"(\S+?)->(\S+?)\(([^)]*)\)")
NORM_RE = re.compile(
    r"^\s*(invoke-\S+)\s*\{([^}]*)\},\s*(\S+?)->(\S+?)\(([^)]*)\)")
# Capture the whole .method line and split it explicitly. A regex that skips
# modifiers with (?:\S+\s+)*? will match across newlines and let "<init>"
# swallow the method below it.
METHOD_RE = re.compile(r"^\.method[ \t]+(.*)$", re.M)
REGS_RE = re.compile(r"^\s*\.registers\s+(\d+)", re.M)
# Opcodes that may use the /range form and therefore reference vA .. vB.
RANGE_OP_RE = re.compile(
    r"^\s*([a-z][\w-]*)(?:/[\w-]+)?\s*\{\s*(v\d+)\s*\.\.\s*(v\d+)\s*\}")
REG_TOKEN_RE = re.compile(r"\b([vp])(\d+)\b")
NEW_INSTANCE_RE = re.compile(r"^new-instance\s+(v\d+),\s*(.+)$")
INVOKE_HEAD_RE = re.compile(r"^invoke-\S+\s*\{([^}]*)\}")


def _split_header(header: str):
    """'.method constructor <init>(Lfoo;)V' -> ('<init>', ['constructor'], 'Lfoo;')"""
    mods = []
    for tok in header.split():
        i = tok.find("(")
        if i >= 0:
            return tok[:i], mods, tok[i + 1:tok.index(")")]
        mods.append(tok)
    return None, mods, ""


def _methods(src: str):
    for m in METHOD_RE.finditer(src):
        name, mods, params = _split_header(m.group(1))
        if name is None:
            continue
        end = src.find("\n.end method", m.end())
        yield name, mods, params, src[m.end():end if end != -1 else len(src)]


def arity_problems(src: str):
    out = []
    for name, _mods, _params, body in _methods(src):
        for line in (l.strip() for l in body.splitlines()):
            g = RANGE_RE.match(line)
            if g:
                op, a, b, _c, _m, params = g.groups()
                got = int(b[1:]) - int(a[1:]) + 1
                need = descriptor_words(params) + (0 if op.startswith("invoke-static") else 1)
                if got != need:
                    out.append((name, line,
                                f"range spans {got} registers, callee needs {need}"))
                continue
            g = NORM_RE.match(line)
            if not g:
                continue
            op, regs, _c, _m, params = g.groups()
            need = descriptor_words(params) + (0 if op.startswith("invoke-static") else 1)
            got = len([r for r in regs.split(",") if r.strip()])
            if not op.endswith("/range") and got > 5:
                out.append((name, line,
                            f"non-range invoke with {got} registers (format max 5)"))
            elif got != need:
                out.append((name, line, f"passes {got} registers, callee needs {need}"))
    return out


def zero_local_problems(src: str):
    """v-registers touched in a frame that declares no locals.

    ins counts `this` plus every declared argument, so a method whose
    .registers equals its ins has no local registers at all and v0 IS the
    first parameter. Writing an int over `this` and then invoking a method on
    it is rejected with

        [0xF] tried to get class from non-reference register v0 (type=Conflict)

    There is never a legitimate reason to name a v-register in such a frame,
    so this is always a bug, with no false positives to tune away.
    """
    out = []
    for name, mods, params, body in _methods(src):
        rm = REGS_RE.search(body[:200])
        if not rm:
            continue
        regs = int(rm.group(1))
        ins = descriptor_words(params) + (0 if "static" in mods else 1)
        if regs > ins:
            continue                              # frame has locals; vN is fine
        for line in (l.strip() for l in body.splitlines()):
            if not line or line.startswith("."):
                continue
            for m in re.finditer(r"\bv\d+\b", line):
                out.append((name, line,
                            f".registers {regs} == ins {ins}, so {m.group(0)} "
                            f"is a parameter register, not a local"))
    return out


def uninitialized_problems(src: str):
    """Calls on a `new-instance` reference before its <init> has run.

    ART rejects these at class-load time:

        void android.ext.r.nexusModulesPick(): [0x4] 'this' arg must be
        initialized

    `new-instance` produces an uninitialized reference; the verifier permits
    only <init> to be invoked on it. Calling any other method first -- e.g.
    setClassName on a freshly constructed Intent -- is rejected.
    """
    out = []
    for name, _mods, _params, body in _methods(src):
        lines = [l.strip() for l in body.splitlines()
                 if l.strip() and not l.strip().startswith(("#", "."))]
        fresh = {}
        for line in lines:
            n = NEW_INSTANCE_RE.match(line)
            if n:
                fresh[n.group(1)] = False
                continue
            u = INVOKE_HEAD_RE.match(line)
            if not u:
                continue
            regs = [r.strip() for r in u.group(1).split(",") if r.strip()]
            if regs and regs[0] in fresh and not fresh[regs[0]]:
                if "-><init>(" not in line:
                    out.append((name, line,
                                "receiver was new-instance'd but not <init>'d yet"))
                else:
                    fresh[regs[0]] = True
    return out


def budget_problems(src: str):
    """Instructions naming a register the method's frame does not declare."""
    out = []
    for name, mods, params, body in _methods(src):
        head = body[:200]
        rm = REGS_RE.search(head)
        if not rm:
            continue
        regs = int(rm.group(1))
        ins = descriptor_words(params) + (0 if "static" in mods else 1)
        p_base = regs - ins
        for line in (l.strip() for l in body.splitlines()):
            if not line or line.startswith("."):
                continue
            r = RANGE_OP_RE.match(line)
            if r:
                hi = int(r.group(3)[1:])
                if hi >= regs:
                    out.append((name, line,
                                f"range reaches v{hi} but .registers is {regs}"))
                continue
            for kind, num in REG_TOKEN_RE.findall(line):
                idx = int(num) + (p_base if kind == "p" else 0)
                if idx >= regs:
                    out.append((name, line,
                                f"names {kind}{num} -> v{idx} but .registers is {regs}"))
    return out


LABEL_DEF_RE = re.compile(r"^    :(\S+)\s*$", re.M)
CLASS_RE = re.compile(r"^\.class\s+(.*?)\s+(L\S+;)\s*$", re.M)
SPARSE_BLOCK_RE = re.compile(
    r"^    \.sparse-switch\s*$(.*?)^    \.end sparse-switch\s*$", re.M | re.S)


def switch_label_problems(src: str):
    """Every label a sparse-switch table names must be a :label in the SAME
    method. baksmali accepts the dangling row and apktool b dies at dex-write
    time with 'Cannot get the location of a label that hasn't been placed' --
    the exact failure the half-renamed extensions tab produced (table said
    sswitch_nexus_tab_extensions, cases said sswitch_nexus_tab_modules)."""
    out = []
    for name, mods, params, body in _methods(src):
        # Labels are method-scoped, so definitions are looked up in body alone.
        defined = {m.group(1) for m in LABEL_DEF_RE.finditer(body)}
        for block in SPARSE_BLOCK_RE.finditer(body):
            for row in block.group(1).splitlines():
                row = row.strip()
                if "-> :" not in row:
                    continue
                label = row.rsplit("-> :", 1)[1].strip()
                if label not in defined:
                    out.append((name, row,
                                "sparse-switch target has no case label in "
                                "the method"))
    return out


def same_member_problems(src: str):
    """Every nexus* method an invoke runs on the file's own class must be
    declared in that same file. A drifting hook name assembles fine and
    installs fine, then the activity dies with NoSuchMethodError on first
    launch -- exactly what the stale nexusModulesRender call in z() did
    (the render methods were renamed to their extension-era names everywhere
    but that one line). Framework members inherited from Activity et al are
    out of scope: they are never ours to rename."""
    cm = CLASS_RE.search(src)
    if cm is None:
        return []
    declared = set()
    for m in METHOD_RE.finditer(src):
        name, mods, params = _split_header(m.group(1))
        if name:
            declared.add(name + "(" + params + ")")
    invoke_re = re.compile(
        r"^    invoke-\S+\s+\{[^}]*\},\s*" + re.escape(cm.group(2))
        + r"->([^\s(]+\(\S*?\))\S*$", re.M)
    out = []
    for m in invoke_re.finditer(src):
        sig = m.group(1)
        if not sig.startswith("nexus"):
            continue
        member = sig[:sig.index(")", 1) + 1]
        if member not in declared:
            out.append((cm.group(2), f"-> {sig}",
                        "the class does not declare this method"))
    return out


def _fmt(problems, rel):
    return "\n".join(f"{rel}: {m}: {why}\n    {line}" for m, line, why in problems)


# ------------------------------------------------------- the source asset ---

@pytest.mark.parametrize("rel", ENGINE_SHIPPED)
def test_shipped_classes_are_clean(rel):
    """Hand-written smali assets, auditable without an applied tree."""
    src = (RES_DIR / rel).read_text(encoding="utf-8")
    assert arity_problems(src) == [], _fmt(arity_problems(src), rel)
    assert budget_problems(src) == [], _fmt(budget_problems(src), rel)
    assert uninitialized_problems(src) == [], _fmt(uninitialized_problems(src), rel)
    assert zero_local_problems(src) == [], _fmt(zero_local_problems(src), rel)


def test_zero_local_check_catches_the_regression():
    """Guard the guard: .registers 4 with 4 params means v0 is `this`."""
    bad = ('.method protected onActivityResult(IILandroid/content/Intent;)V\n'
           "    .registers 4\n"
           "    const v0, 0x4e58\n"
           "    if-ne p1, v0, :end\n"
           "    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;"
           "->onActivityResult(IILandroid/content/Intent;)V\n"
           "    :end\n    return-void\n.end method\n")
    problems = zero_local_problems(bad)
    assert problems, "v0 in a zero-local frame must be flagged"
    assert "parameter register, not a local" in problems[0][2]

    good = ('.method protected onActivityResult(IILandroid/content/Intent;)V\n'
            "    .registers 6\n"
            "    const v0, 0x4e58\n"
            "    if-ne p1, v0, :end\n"
            "    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;"
            "->onActivityResult(IILandroid/content/Intent;)V\n"
            "    :end\n    return-void\n.end method\n")
    assert zero_local_problems(good) == []


def test_uninitialized_check_catches_the_regression():
    """Guard the guard: setClassName straight onto new-instance must fail."""
    bad = ('.method private p()V\n    .registers 4\n'
           "    new-instance v0, Landroid/content/Intent;\n"
           "    invoke-virtual {v0, v0, v1}, Landroid/content/Intent;"
           "->setClassName(Landroid/content/Context;Ljava/lang/String;)Landroid/content/Intent;\n"
           "    return-void\n.end method\n")
    assert uninitialized_problems(bad), "must flag a call before <init>"

    good = ('.method private p()V\n    .registers 4\n'
            "    new-instance v0, Landroid/content/Intent;\n"
            "    invoke-direct {v0}, Landroid/content/Intent;-><init>()V\n"
            "    invoke-virtual {v0, v0, v1}, Landroid/content/Intent;"
            "->setClassName(Landroid/content/Context;Ljava/lang/String;)Landroid/content/Intent;\n"
            "    return-void\n.end method\n")
    assert uninitialized_problems(good) == []


# --------------------------------------------------------- the applied tree ---

@pytest.mark.parametrize("rel", AUDITED)
def test_switch_tables_only_target_labels_the_method_defines(applied, rel):
    """The onClick switch is the one place where a *renaming* bug turns into a
    dead build instead of a wrong id: the table and the cases come from two
    different blocks, so any drift between their key names never surfaces
    until the dex writer runs."""
    src = (applied / rel).read_text(encoding="utf-8")
    assert switch_label_problems(src) == \
        [], _fmt(switch_label_problems(src), rel)


def test_switch_check_catches_the_unplaced_label():
    """The rename-era regression in miniature: a case emitted under the old
    tab key while the table row uses the new one. Nothing upstream catches it,
    and the file assembles -- it dies inside dexlib when the APK is built."""
    src = (""".method public onClick(Landroid/view/View;)V
    .locals 2

    sparse-switch p1, :sswitch_data_0

    :goto_1
    return-void

    :sswitch_nexus_tab_modules
    const/4 v0, 0x1

    sput v0, Landroid/ext/r;->nexusTab:I

    goto :goto_1

    :sswitch_data_0
    .sparse-switch
        0x7f050161 -> :sswitch_nexus_tab_modules
    .end sparse-switch
.end method

.method public other()V
    .locals 0

    sparse-switch p1, :sswitch_data_0

    :goto_1
    return-void

    :sswitch_nexus_tab_extensions
    goto :goto_1

    :sswitch_data_0
    .sparse-switch
        0x7f050161 -> :sswitch_nexus_tab_extensions
    .end sparse-switch
.end method
""")
    assert switch_label_problems(src) == [], "clean methods must not flag"
    src = src.replace("-> :sswitch_nexus_tab_modules",
                      "-> :sswitch_nexus_tab_extensions")
    problems = switch_label_problems(src)
    assert len(problems) == 1, _fmt(problems, "x.smali")
    assert problems[0][0] == "onClick"
    assert problems[0][1] == "0x7f050161 -> :sswitch_nexus_tab_extensions"
    # Labels are method-scoped: the extension case exists, but in OTHER().
    assert "in the method" in problems[0][2]


    # Labels are method-scoped: the extension case exists, but in OTHER().
    assert "in the method" in problems[0][2]


@pytest.mark.parametrize("rel", AUDITED)
def test_nexus_calls_in_own_class_are_declared(applied, rel):
    """A nexus-named hook calling a member the file does not declare is
    invisible to every assemble-time check and kills the app in onCreate on
    the first launch."""
    src = (applied / rel).read_text(encoding="utf-8")
    assert same_member_problems(src) == \
        [], _fmt(same_member_problems(src), rel)


def test_member_check_catches_the_launch_crash():
    """The rename-era launch crash in miniature, from the z() hook: r.smali
    called nexusModulesRender()V, a method that had been renamed to
    nexusExtensionsRender()V everywhere but that line."""
    src = (""".class public Landroid/ext/r;
.super Landroid/app/Activity;

.method public onCreate(Landroid/os/Bundle;)V
    .locals 1

    invoke-direct {p0}, Landroid/ext/r;->nexusExtensionsRender()V

    return-void
.end method

.method private nexusExtensionsRender()V
    .locals 0

    return-void
.end method
""")
    assert same_member_problems(src) == [], "clean file must not flag"
    stale = src.replace("->nexusExtensionsRender()V\n\n    return-void\n.end method\n\n.method private",
                        "->nexusModulesRender()V\n\n    return-void\n.end method\n\n.method private")
    assert stale != src, "the stale-name substitution must land"
    problems = same_member_problems(stale)
    assert len(problems) == 1, _fmt(problems, "x.smali")
    assert "nexusModulesRender" in problems[0][1]
    assert problems[0][0] == "Landroid/ext/r;"


@pytest.fixture(scope="module")
def applied() -> Path:
    root = _tree_root()
    if root is None:
        pytest.skip("no applied tree on disk; run nexus.py apply first")
    return root


@pytest.mark.parametrize("rel", AUDITED)
def test_invoke_arity_matches_callee_signature(applied, rel):
    src = (applied / rel).read_text(encoding="utf-8")
    assert arity_problems(src) == [], _fmt(arity_problems(src), rel)


@pytest.mark.parametrize("rel", AUDITED)
def test_every_register_fits_the_declared_frame(applied, rel):
    src = (applied / rel).read_text(encoding="utf-8")
    assert budget_problems(src) == [], _fmt(budget_problems(src), rel)


@pytest.mark.parametrize("rel", AUDITED)
def test_no_call_on_an_uninitialized_reference(applied, rel):
    src = (applied / rel).read_text(encoding="utf-8")
    assert uninitialized_problems(src) == [], _fmt(uninitialized_problems(src), rel)


@pytest.mark.parametrize("rel", AUDITED)
def test_frames_that_declare_no_locals_use_no_v_registers(applied, rel):
    src = (applied / rel).read_text(encoding="utf-8")
    assert zero_local_problems(src) == [], _fmt(zero_local_problems(src), rel)


# ------------------------------------------------- the regression itself ---

def test_the_six_register_contentquery_is_gone_from_smali():
    """The VerifyError that started this suite, and its cure.

    ContentResolver.query needs receiver + 5 args, which does not fit the
    non-range form; it shipped as /range {v0 .. v6} with the receiver last and
    was rejected at class-load. Reading a document's display name is now Java
    (ScriptStore.displayNameOf), so there is no such call in smali at all --
    and if one comes back, it is hand-written again and will be wrong again.
    """
    from nexus.extensions import extensions_methods as modules_methods

    class _I:
        def hex(self, name):
            return "0x0"

    assert "->query(" not in modules_methods(_I())
    engine = (RES_DIR / "smali/org/vekendian/nexus/extensions").rglob("*.smali")
    for f in engine:
        assert "->query(" not in f.read_text(encoding="utf-8"), f


def test_the_render_range_window_is_exact():
    """The one /range call left in r.smali: 16 ids plus the activity.

    A window wider or narrower than the descriptor is exactly the class of bug
    this suite exists for, so the specific shape is pinned as well as checked
    generically above.
    """
    from nexus.extensions import extensions_methods as modules_methods, RENDER_DESC, RENDER_REGISTERS

    class _I:
        def hex(self, name):
            return "0x0"

    out = modules_methods(_I())
    m = re.search(r"^\s*(invoke-static/range)\s*\{\s*(v\d+)\s*\.\.\s*(v\d+)\s*\},"
                  r"\s*\S+?->render\(", out, re.M)
    assert m, "render() must use /range: 20 words exceeds the 5-register format"
    _op, lo, hi = m.groups()
    assert lo == "v0", f"v0 holds the activity, moved out of p0 first; got {lo}"
    assert hi == f"v{RENDER_REGISTERS - 2}"
    words = descriptor_words(RENDER_DESC[1:-2])   # strip '(' and ')V'
    assert int(hi[1:]) - int(lo[1:]) + 1 == words == 17


# ------------------------------------------------------- the auditor itself ---

def test_descriptor_words():
    assert descriptor_words("I") == 1
    assert descriptor_words("J") == 2
    assert descriptor_words("D") == 2
    assert descriptor_words("Ljava/lang/Object;") == 1
    assert descriptor_words("[Ljava/lang/String;") == 1
    assert descriptor_words("[[I") == 1
    assert descriptor_words("Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;"
                            "[Ljava/lang/String;Ljava/lang/String;") == 5


def test_split_header_does_not_run_into_the_next_method():
    """<init> followed by onClick: the parser must not merge them."""
    src = (".method constructor <init>(Landroid/ext/r;Ljava/lang/String;)V\n"
           "    .registers 3\n    return-void\n.end method\n\n"
           ".method public onClick(Landroid/view/View;)V\n"
           "    .registers 4\n    return-void\n.end method\n")
    names = [n for n, _m, _p, _b in _methods(src)]
    assert names == ["<init>", "onClick"]


def test_auditor_catches_the_arity_bugs_it_exists_to_catch():
    """Guard the guard: a deliberately wrong invoke must be reported."""
    bad_range = ('.method private x()V\n    .registers 8\n'
                 "    invoke-virtual/range {v0 .. v6}, Landroid/content/ContentResolver;"
                 "->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;"
                 "[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;\n"
                 "    return-void\n.end method\n")
    problems = arity_problems(bad_range)
    assert problems, "the 7-register query() that shipped must be flagged"
    assert "spans 7 registers, callee needs 6" in problems[0][2]

    bad_norm = ('.method private y()V\n    .registers 8\n'
                "    invoke-virtual {v0, v1, v2, v3, v4, v5}, "
                "Ljava/lang/StringBuilder;->append(Ljava/lang/String;)"
                "Ljava/lang/StringBuilder;\n    return-void\n.end method\n")
    assert arity_problems(bad_norm), "2-arg call given 6 registers must be flagged"

    good = ('.method private z()V\n    .registers 6\n'
            "    invoke-virtual/range {v0 .. v5}, Landroid/content/ContentResolver;"
            "->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;"
            "[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;\n"
            "    return-void\n.end method\n")
    assert arity_problems(good) == []


def test_auditor_catches_registers_outside_the_frame():
    over = ('.method private q()V\n    .registers 4\n'
            "    const-string v7, \"x\"\n"
            "    return-void\n.end method\n")
    assert budget_problems(over), "v7 in a 4-register frame must be flagged"

    fits = ('.method private q()V\n    .registers 8\n'
            "    const-string v7, \"x\"\n"
            "    return-void\n.end method\n")
    assert budget_problems(fits) == []

    # p-registers map above v-registers: with .registers 4 and 2 ins, p0 is v2.
    param_over = ('.method private q(Ljava/lang/String;)V\n    .registers 4\n'
                  "    const-string p5, \"x\"\n"
                  "    return-void\n.end method\n")
    assert budget_problems(param_over), "p5 maps past the frame and must be flagged"
