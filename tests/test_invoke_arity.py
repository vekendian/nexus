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
# injection, ConfigListAdapter the settings highlight, r$ModuleRemove the card
# listener, r.smali everything else.
AUDITED = [
    "smali/android/ext/r.smali",
    "smali/android/ext/f.smali",
    "smali/android/ext/ConfigListAdapter.smali",
    "smali/android/ext/r$ModuleRemove.smali",
]

LISTENER = "smali/android/ext/r$ModuleRemove.smali"


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
    r"^\s*(invoke-\S+/range)\s*\{\s*(v\d+)\s*\.\.\s*(v\d+)\s*\},\s*"
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
            need = descriptor_words(params) + (0 if op == "invoke-static" else 1)
            got = len([r for r in regs.split(",") if r.strip()])
            if not op.endswith("/range") and got > 5:
                out.append((name, line,
                            f"non-range invoke with {got} registers (format max 5)"))
            elif got != need:
                out.append((name, line, f"passes {got} registers, callee needs {need}"))
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


def _fmt(problems, rel):
    return "\n".join(f"{rel}: {m}: {why}\n    {line}" for m, line, why in problems)


# ------------------------------------------------------- the source asset ---

def test_listener_class_is_clean():
    src = (RES_DIR / LISTENER).read_text(encoding="utf-8")
    assert arity_problems(src) == [], _fmt(arity_problems(src), LISTENER)
    assert budget_problems(src) == [], _fmt(budget_problems(src), LISTENER)


# --------------------------------------------------------- the applied tree ---

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


# ------------------------------------------------- the regression itself ---

def test_query_uses_a_contiguous_window_with_receiver_first():
    """The exact shape that shipped as a VerifyError.

    ContentResolver.query takes receiver + 5 args. The non-range form caps at 5
    registers, so /range is required -- and in a range invoke the RECEIVER is
    the low register, so the resolver must sit at the bottom of the window.
    """
    from nexus.modules import modules_methods

    class _I:
        def hex(self, name):
            return "0x0"

    out = modules_methods(_I())
    m = re.search(r"^\s*(invoke-\S+/range)\s*\{\s*(v\d+)\s*\.\.\s*(v\d+)\s*\},"
                  r"\s*\S+?->query\(", out, re.M)
    assert m, "query() must use the /range form: receiver + 5 args exceeds the limit"
    op, lo, hi = m.groups()
    assert int(lo[1:]) == 0, f"receiver must be the first register of the range, got {lo}"
    assert "invoke-static" not in op
    need = descriptor_words(
        "Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;"
        "[Ljava/lang/String;Ljava/lang/String;") + 1
    assert int(hi[1:]) - int(lo[1:]) + 1 == need


def test_query_cursor_is_read_from_outside_the_range_window():
    """The cursor result must not land back inside v0..v5."""
    from nexus.modules import modules_methods

    class _I:
        def hex(self, name):
            return "0x0"

    out = modules_methods(_I())
    m = re.search(r"query\([^)]*\)[^;]*?;\s*move-result-object (v\d+)", out, re.S)
    assert m, "query's result must be captured"
    assert int(m.group(1)[1:]) >= 6, \
        "the cursor register must sit outside the v0..v5 argument window"


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
