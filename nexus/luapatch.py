"""The Lua-facing `nexus.*` namespace, rendered and injected.

Four jobs, one file, because they share one contract:

* **Templates** live in ``resources/smali_lua/org/vekendian/nexus/lua/`` with
  ``@@ID:name@@`` placeholders and are rendered against the id lock file at
  apply time. They cannot live in ``resources/smali`` (which copy_smali copies
  verbatim) because a placeholder must never reach the tree.

* **Script.smali** gets one call line (``nexusInstall``) right after
  GameGuardian registers ``gg``, the helper method it calls, and the
  LuajavaLib install in ``u3()`` (fault-tolerant, recorded in
  ``_G.luajava_error`` on failure).

* **BaseLib.smali** gets the ``import`` registration Pivot has and stock 101.4
  dropped, so ``BaseLib$import`` (shipped but never instantiated) becomes the
  ``_G.import`` global scripts expect.

* **o0$b.smali** (the Execute script dialog) gets its "?" (examples) action
  replaced. It used to run ``print('gg =', gg)`` and show a table reference;
  now it opens the static ``nexus_str_lua_help`` dialog, which documents the
  gg API and the nexus.* surface in GameGuardian's scrollable/copyable text
  window.

Everything else is the ordinary Java pipeline: ``resources/java/host`` compiles
to the tree's ``org/vekendian/nexus/modules`` package, and the smali here only
builds the Lua tables, blocks on the permission prompt, and dispatches into
``LuaBridge``. See ``resources/java/host/org/vekendian/nexus/modules/LuaBridge.java``
for the category registry and the reason the split is where it is.
"""

from __future__ import annotations

import re
from pathlib import Path

from .anchors import PatchError, replace_once
from .tree import RES_DIR, read, write

TEMPLATE_DIR = RES_DIR / "smali_lua"
# Where rendered classes land in the tree. Same root as ModulePicker.smali.
TREE_SMALI = "smali"

SCRIPT_REL = "smali/android/ext/Script.smali"
SCRIPT_CLASS = "Landroid/ext/Script;"

TOKEN_RE = re.compile(r"@@ID:(\w+)@@")

# The registration point in Script.call: the line after the script environment
# receives `gg`. The call is spliced BETWEEN the i2("gg", ...) store and the
# next statement, and runs before the script body is executed (call() builds the
# environment and only then runs the chunk), so `nexus` is visible to the
# script's top level.
SCRIPT_ANCHOR = '''\
    const-string p1, "gg"

    invoke-virtual {p2, p1, v5}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    const-string v0, "package"
'''

SCRIPT_CALL_RE = re.compile(
    r"^    invoke-static \{p0, p2\}, Landroid/ext/Script;->nexusInstall"
    r"\(Landroid/ext/Script;Lluaj/LuaValue;\)V$", re.M)

SCRIPT_HELPER_MARK = ".method private static nexusInstall(Landroid/ext/Script;Lluaj/LuaValue;)V"

# Appended as one method. Two properties matter and both are deliberate:
#
#   * the call site passes the Script instance, and the helper reads U (the
#     File or String the script was created from, package-private) to label the
#     permission prompt with the script's own path;
#   * every failure mode is swallowed. This code runs inside GameGuardian's
#     script startup: a missing class (NEXUS_UI=0 build half-copied), a null
#     environment, a broken template must never stop the user's script from
#     starting. The Lua side reports "module system is not running" instead.
SCRIPT_HELPER = '''\

.method private static nexusInstall(Landroid/ext/Script;Lluaj/LuaValue;)V
    .locals 2

    :nexus_install_try
    if-eqz p0, :nexus_install_end

    if-eqz p1, :nexus_install_end

    iget-object v0, p0, Landroid/ext/Script;->U:Ljava/lang/Object;

    if-eqz v0, :nexus_install_end

    invoke-static {v0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0, p1}, Lorg/vekendian/nexus/lua/NexusLua;->install(Ljava/lang/String;Lluaj/LuaValue;)V

    :nexus_install_end
    return-void

    .catch Ljava/lang/Throwable; {:nexus_install_try .. :nexus_install_end} :nexus_install_cleanup

    :nexus_install_cleanup
    return-void
.end method

# Records why the luajava install failed instead of letting it kill the app.
# The port is third-party and has already shipped broken twice (a missing
# dispatch field, then a stubbed table builder), and GameGuardian does not catch
# Throwables raised while Script.<init> builds its Globals -- the click just force
# closes. u3() only has v0/v1 to spare, so the Throwable is flattened to its
# String on the caller's side and only the message is stored here. The script
# reads _G.luajava_error and prints it, which is how the failure gets reported
# without a logcat capture.
.method private static nexusLuajavaFail(Lluaj/LuaValue;Ljava/lang/String;)V
    .locals 2

    invoke-static {p1}, Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;

    move-result-object v0

    const-string v1, "luajava_error"

    invoke-virtual {p0, v1, v0}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    return-void
.end method
'''

# --- Script.W3() main-looper guard -------------------------------------------
# GameGuardian's decoded tree at smali/android/ext/Script.smali method
# W3(Ljava/lang/Object;)V just does `Object.wait()`. n2.i() targets the main
# looper (index 0) and, per n2.f with flag false, runs its Runnable *inline*
# when already on the main thread — i.e. before W3() reaches wait(). A thread
# that waits there loses that wakeup and deadlocks the main thread.
# n2.e()Z (already present in this GG build) returns true iff myLooper() ==
# getMainLooper(), so W3() returns immediately on the main thread and keeps the
# original wait() + InterruptedException handling off-main.
# Caveat: dialog-based APIs (alert/choice/prompt/multiChoice/makeRequest...)
# display the dialog and return after showing it; they do not block until the
# user interacts, so on the main thread these calls return once the dialog is
# posted rather than waiting for user interaction.
W3_REL = SCRIPT_REL
W3_GUARD_MARK = "Landroid/ext/n2;->e()Z"
W3_ENTRY_ANCHOR = '''.method static W3(Ljava/lang/Object;)V
    .locals 1

    .line 1
    :try_start_0
    invoke-virtual {p0}, Ljava/lang/Object;->wait()V'''

W3_ENTRY_NEW = '''.method static W3(Ljava/lang/Object;)V
    .locals 3

    .line 1
    # Main-looper guard: n2.i() targets the main looper (index 0) and runs its
    # Runnable inline when already on the main thread (n2.f with flag false),
    # i.e. before W3() reaches wait(). Waiting here would lose that wakeup and
    # deadlock the main thread, so return immediately on the main thread.
    # Off-main threads keep the original wait() + InterruptedException handling
    # exactly as before.
    # Caveat: dialog-based APIs (alert/choice/prompt/multiChoice/makeRequest...)
    # display the dialog and return after showing it; they do not block until
    # the user interacts, so on the main thread these calls return once the
    # dialog is posted rather than waiting for user interaction.
    invoke-static {}, Landroid/ext/n2;->e()Z
    move-result v0

    if-eqz v0, :cond_w3_main

    # Main-thread deadlock prevented: notify the user via GG's own toast path.
    const-string v1, "Nexus: deadlock prevented"
    const/4 v2, 0x0
    invoke-static {v1, v2}, Landroid/ext/Tools;->K1(Ljava/lang/String;I)V

    return-void

    :cond_w3_main
    :try_start_0
    invoke-virtual {p0}, Ljava/lang/Object;->wait()V'''


def transform_w3_guard(smali: str) -> str:
    """Insert the main-looper guard into Script.W3().

    Idempotent: raises PatchError if the guard is already present, so re-applying
    to an output tree fails loudly instead of duplicating the guard.
    """
    if W3_GUARD_MARK in smali:
        raise PatchError("Script.smali: W3 main-looper guard already present "
                         "(already patched?)")
    return replace_once(smali, W3_ENTRY_ANCHOR, W3_ENTRY_NEW,
                        "Script.W3 main-looper guard")

HELP_REL = "smali/android/ext/o0$b.smali"

# The Execute script dialog's "?" (examples) case. GG builds a one-line Script
# around print('gg =', gg) and runs it: the user sees a table address and the
# dialog documents nothing. The whole case block is the anchor, so a GG dialog
# reshuffle fails loudly instead of editing the wrong branch.
HELP_ANCHOR = r'''
    :cond_4
    new-instance p1, Landroid/ext/Script;

    const-string v0, "print(\'gg =\', gg)"

    invoke-direct {p1, v0, v4, v6}, Landroid/ext/Script;-><init>(Ljava/lang/String;ILjava/lang/String;)V

    invoke-virtual {p1}, Landroid/ext/Script;->R3()Landroid/ext/Script;

    goto/16 :goto_3
'''

# Static help. b2.f(id) is the raw getString path: b2.h only Caesar-decodes ids
# present in its cache (GG's own encoded pack), so Nexus's plain resource is
# returned unchanged. Tools.h(text, 0) is GG's scrollable, copyable text dialog
# (Copy stays enabled at flags 0). The case runs inside onClick (.locals 10)
# with v0/v1 free here.
HELP_BLOCK = '''\
:cond_4
    const v0, @@ID:nexus_str_lua_help@@

    invoke-static {v0}, Landroid/ext/b2;->f(I)Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    invoke-static {v0, v1}, Landroid/ext/Tools;->h(Ljava/lang/String;I)V

    goto/16 :goto_3'''

# LuajavaLib ships in the additions tree but nothing in GameGuardian ever
# constructs it: its only <init> call site in the whole tree is inside
# JsePlatform.standardGlobals(), and no code calls JsePlatform. So every script
# sees `luajava` as nil until it is installed here.
#
# The install is the same three lines JsePlatform uses, because that is the
# proven wiring for this exact class: `new-instance` -> `<init>()` ->
# `globals.t1(lib)`. LuaValue.t1 is `library.call(LuaValue.L, this)`, the same
# call every other library (BaseLib, PackageLib, ...) is installed with; for a
# VarArgFunction that lands in LuajavaLib.invoke(Varargs), where the `aj`
# dispatch field is never written and so defaults to 0 -- the branch that builds
# a table from NAMES, sets globals["luajava"], package.loaded["luajava"] and the
# primitive type classes.
#
# u3() and not F3() for two reasons, both load-bearing:
#   * u3() installs into this.T, the real script environment, and both Script
#     constructors call it; F3() builds a throwaway Globals that only
#     android/ext/j2.smali uses;
#   * u3() loads PackageLib. LuajavaLib's install path indexes
#     package.loaded, so in F3()'s package-less Globals the second get() on a
#     nil would throw and take the script environment down with it.
#
# u3() ends with the DebugLib load followed by the v3() stream setup, and that
# exact pair occurs once. u3() has .locals 2 with v0 = Globals and v1 the
# scratch register each library is built in, so this needs no register change.
#
# The block below deliberately starts at column 0 and ends without a newline:
# replace_once matches on a whitespace-collapsed view and splices at the first
# NON-whitespace character, so the anchor's own leading indentation and trailing
# newline survive the splice. A block indented on both its first and last line
# would come out doubled. Same convention HELP_BLOCK follows.
LUAJAVA_CLASS_REL = "smali/luaj/lib/jse/LuajavaLib.smali"

LUAJAVA_MARK = "new-instance v1, Lluaj/lib/jse/LuajavaLib;"

# `import` is the second luajava global Pivot exposes (after the `luajava`
# table itself). Stock 101.4 ships no BaseLib registration for it -- its
# BaseLib has no "import" literal at all -- while the ported additions tree
# carries BaseLib$import.smali as an orphan nobody instantiates. Pivot's fix
# is four instructions at the end of BaseLib.call(); this replicates them so
# `_G.import` exists exactly the way it does on Pivot.
BASELIB_REL = "smali/luaj/lib/BaseLib.smali"
BASEIMPORT_CLASS_REL = "smali/luaj/lib/BaseLib$import.smali"

BASEIMPORT_MARK = "new-instance v0, Lluaj/lib/BaseLib$import;"

# Anchored on the ipairs registration plus return that end call(): ipairs is
# the last function BaseLib registers, so the pair occurs once and pins both
# the method and the register frame (p0=this, p1=func, p2=env under
# .locals 2 -- the guard below refuses to patch if that frame changes).
BASEIMPORT_ANCHOR = '''\
    invoke-direct {p1}, Lluaj/lib/BaseLib$ipairs;-><init>()V

    const-string v0, "ipairs"

    invoke-virtual {p2, v0, p1}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    return-object p2
'''

# Column-0 first line, no trailing newline: replace_once splices at the
# anchor's first non-whitespace character, whose indentation is preserved
# outside the splice. v0/v1 are dead at this point (last writer was the pairs
# registration; the anchor itself rewrites v0 with "ipairs" after our block),
# p1 holds the not-yet-registered ipairs instance and is left untouched.
BASEIMPORT_BLOCK = '''\
new-instance v0, Lluaj/lib/BaseLib$import;

    invoke-direct {v0, p0}, Lluaj/lib/BaseLib$import;-><init>(Lluaj/lib/BaseLib;)V

    const-string v1, "import"

    invoke-virtual {p2, v1, v0}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    invoke-direct {p1}, Lluaj/lib/BaseLib$ipairs;-><init>()V

    const-string v0, "ipairs"

    invoke-virtual {p2, v0, p1}, Lluaj/LuaValue;->i2(Ljava/lang/String;Lluaj/LuaValue;)V

    return-object p2
'''

# Pivot's LuaValue carries a real `uservalue` field and a virtual
# setuservalue(LuaValue) that JavaMethod / JavaMethod$Overload inherit. The
# JavaInstance lookup paths (U0 getter/method branches, j2 setter branch) call
# it to bind the receiver onto the method value. Stock 101.4 has no userdata
# support and no such method; the porter rewired those calls to LuaValue.c1(),
# an empty hook, so every looked-up JavaMethod kept uservalue == null and
# Method.invoke got a null receiver ("null receiver (method 'append')").
# This adds the virtual slot back (Pivot parity): the base is a no-op, and
# JavaMethod / JavaMethod$Overload override it.
LUAVALUE_REL = "smali/luaj/LuaValue.smali"
LUAVALUE_SETUSERVALUE_MARK = ".method public setuservalue(Lluaj/LuaValue;)V"
LUAVALUE_SETUSERVALUE = '''\

.method public setuservalue(Lluaj/LuaValue;)V
    .locals 0

    return-void
.end method
'''


LUAJAVA_ANCHOR = '''\
    new-instance v1, Lluaj/lib/DebugLib;

    invoke-direct {v1}, Lluaj/lib/DebugLib;-><init>()V

    invoke-virtual {v0, v1}, Lluaj/LuaValue;->t1(Lluaj/LuaValue;)Lluaj/LuaValue;

    invoke-direct {p0}, Landroid/ext/Script;->v3()V
'''

LUAJAVA_BLOCK = '''\
new-instance v1, Lluaj/lib/DebugLib;

    invoke-direct {v1}, Lluaj/lib/DebugLib;-><init>()V

    invoke-virtual {v0, v1}, Lluaj/LuaValue;->t1(Lluaj/LuaValue;)Lluaj/LuaValue;

    :nexus_luajava_try
    check-cast v0, Lluaj/Globals;

    sput-object v0, Lluaj/Hlp;->G:Lluaj/Globals;

    new-instance v1, Lluaj/lib/jse/LuajavaLib;

    invoke-direct {v1}, Lluaj/lib/jse/LuajavaLib;-><init>()V

    invoke-virtual {v0, v1}, Lluaj/LuaValue;->t1(Lluaj/LuaValue;)Lluaj/LuaValue;
    :nexus_luajava_end

    goto :nexus_luajava_done

    .catch Ljava/lang/Throwable; {:nexus_luajava_try .. :nexus_luajava_end} :nexus_luajava_cleanup

    :nexus_luajava_cleanup
    move-exception v1

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/ext/Script;->nexusLuajavaFail(Lluaj/LuaValue;Ljava/lang/String;)V

    :nexus_luajava_done
    invoke-direct {p0}, Landroid/ext/Script;->v3()V'''


def templates() -> list:
    """Template paths relative to TEMPLATE_DIR, sorted for determinism."""
    if not TEMPLATE_DIR.is_dir():
        return []
    return sorted(p.relative_to(TEMPLATE_DIR).as_posix()
                  for p in TEMPLATE_DIR.rglob("*.smali"))


def template_tokens() -> dict:
    """``{rel: [name, ...]}`` for every placeholder a template carries."""
    out = {}
    for rel in templates():
        text = (TEMPLATE_DIR / rel).read_text(encoding="utf-8")
        out[rel] = sorted(set(TOKEN_RE.findall(text)))
    return out


def render(ids) -> dict:
    """``{rel: smali text}`` with every ``@@ID:name@@`` resolved.

    Unknown names raise from the lock file, and a leftover ``@@`` is treated as
    an error rather than shipped: a template that grows a placeholder this
    function does not understand must fail the apply, not produce a tree whose
    smali still contains it.
    """
    out = {}
    for rel in templates():
        text = (TEMPLATE_DIR / rel).read_text(encoding="utf-8")
        text = TOKEN_RE.sub(lambda m: ids.hex(m.group(1)), text)
        if "@@" in text:
            raise PatchError(f"{rel}: unresolved placeholder after id interpolation")
        out[rel] = text
    return out


def install(tree: Path, ids) -> None:
    """Write the rendered namespace under the tree's primary smali root."""
    for rel, text in render(ids).items():
        dest = tree / TREE_SMALI / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")


def transform_script(smali: str) -> str:
    """Splice the nexusInstall() call into Script.call and append the helper.

    Anchored on GG's own lines, so a weekly release that changes the shape of
    call() fails in preflight instead of patching a random method.
    """
    if SCRIPT_HELPER_MARK in smali:
        raise PatchError("Script.smali: nexusInstall already present (already patched?)")
    smali = replace_once(smali, SCRIPT_ANCHOR,
                         SCRIPT_ANCHOR.replace(
                             '    const-string v0, "package"',
                             '    invoke-static {p0, p2}, Landroid/ext/Script;->nexusInstall'
                             '(Landroid/ext/Script;Lluaj/LuaValue;)V\n\n'
                             '    const-string v0, "package"'),
                         "Script.call nexus registration")
    return smali.rstrip("\n") + "\n\n" + SCRIPT_HELPER


def transform_luajava(smali: str) -> str:
    """Install LuajavaLib into Script.u3()'s library list.

    Anchored on the DebugLib load plus the v3() call that ends u3(): DebugLib is
    the last library, v3() sets up the streams, and that pair occurs once. A GG
    release that reshapes u3() fails here instead of patching a random method.
    """
    if LUAJAVA_MARK in smali:
        raise PatchError("Script.smali: LuajavaLib already wired (already patched?)")
    if LUAJAVA_ANCHOR not in smali:
        raise PatchError("Script.smali: u3() DebugLib -> v3() anchor not found")
    # The block spends v0 (Globals), v1 (scratch) and p0 (this) and nothing
    # else. p0 is an alias computed from .locals, so a GG release that widens
    # u3()'s register frame would silently shift it under a block whose text
    # still matches the anchor. Pin the count instead of trusting the names.
    at = smali.index(LUAJAVA_ANCHOR)
    sig = smali.index("\n", smali.rfind(".method", 0, at))
    loc = smali.index(".locals", sig)
    if smali[loc:smali.index("\n", loc)] != ".locals 2":
        raise PatchError(
            "Script.smali: u3() is %r, not '.locals 2' -- register frame "
            "changed, re-derive LUAJAVA_BLOCK" % smali[loc:smali.index("\n", loc)])
    return replace_once(smali, LUAJAVA_ANCHOR, LUAJAVA_BLOCK,
                        "Script.u3 LuajavaLib install")


def transform_help(smali: str, ids) -> str:
    """Replace the Execute script dialog's print(gg) example with a help screen.

    Static text on purpose: tapping "?" must not execute anything. The id is
    resolved here rather than baked into the anchor, so the dialog follows the
    lock file like every other Nexus string.
    """
    hex_id = ids.hex("nexus_str_lua_help")
    if hex_id in smali or "@@ID:nexus_str_lua_help@@" in smali:
        raise PatchError(f"{HELP_REL}: help dialog already patched")
    block = TOKEN_RE.sub(lambda m: ids.hex(m.group(1)), HELP_BLOCK)
    return replace_once(smali, HELP_ANCHOR, block,
                        "o0$b Execute-script help dialog")


def transform_baseimport(smali: str) -> str:
    """Register `_G.import` at the end of BaseLib.call() (Pivot parity).

    BaseLib$import already ships in the additions tree but nothing ever
    instantiates it, so scripts see `import` as nil. This splices Pivot's
    four-instruction registration ahead of the return, reusing v0/v1 (dead
    scratch) and leaving the ipairs instance in p1 alone. The .locals pin and
    the method signature check follow transform_luajava's reasoning: p0/p1/p2
    are aliases computed from the frame, so a GG release that widens it must
    fail here instead of patching with shifted registers.
    """
    if BASEIMPORT_MARK in smali:
        raise PatchError("BaseLib.smali: import already registered (already patched?)")
    if BASEIMPORT_ANCHOR not in smali:
        raise PatchError("BaseLib.smali: ipairs -> return anchor not found")
    at = smali.index(BASEIMPORT_ANCHOR)
    msig_start = smali.rfind(".method", 0, at)
    msig = smali[msig_start:smali.index("\n", msig_start)]
    if "call(Lluaj/LuaValue;Lluaj/LuaValue;)Lluaj/LuaValue;" not in msig:
        raise PatchError(
            "BaseLib.smali: anchor sits in %r, not call() -- anchor drifted"
            % msig)
    loc = smali.index(".locals", msig_start)
    if smali[loc:smali.index("\n", loc)] != ".locals 2":
        raise PatchError(
            "BaseLib.smali: call() is %r, not '.locals 2' -- register frame "
            "changed, re-derive BASEIMPORT_BLOCK"
            % smali[loc:smali.index("\n", loc)])
    return replace_once(smali, BASEIMPORT_ANCHOR, BASEIMPORT_BLOCK,
                        "BaseLib.call import registration")


def transform_luavalue(smali: str) -> str:
    """Add the setuservalue() virtual slot stock 101.4 dropped (Pivot parity).

    Pivot's LuaValue.setuservalue stores the receiver on a looked-up
    JavaMethod; stock 101.4 has no userdata layer, and the porter mapped those
    calls to LuaValue.c1(), an empty hook. The ported JavaMethod /
    JavaMethod$Overload declare their own uservalue field and override this
    slot, so the JavaInstance binding calls dispatch to them again.
    """
    if LUAVALUE_SETUSERVALUE_MARK in smali:
        raise PatchError("LuaValue.smali: setuservalue already added (already patched?)")
    return smali.rstrip("\n") + "\n" + LUAVALUE_SETUSERVALUE


def apply(tree: Path, ids) -> None:
    """install() + all smali transforms, the set cli._patch calls.

    copy_smali (and with it copy_luajava) has already run by this point, so the
    class the wiring references is in the tree; if it is not, wiring it would
    leave a dangling descriptor, so that is refused rather than built.
    """
    install(tree, ids)
    if not (tree / LUAJAVA_CLASS_REL).is_file():
        raise PatchError(f"{LUAJAVA_CLASS_REL} missing: cannot wire LuajavaLib")
    if not (tree / BASEIMPORT_CLASS_REL).is_file():
        raise PatchError(f"{BASEIMPORT_CLASS_REL} missing: cannot wire import")
    write(tree, SCRIPT_REL, transform_luajava(read(tree, SCRIPT_REL)))
    write(tree, SCRIPT_REL, transform_script(read(tree, SCRIPT_REL)))
    write(tree, W3_REL, transform_w3_guard(read(tree, W3_REL)))
    write(tree, BASELIB_REL, transform_baseimport(read(tree, BASELIB_REL)))
    write(tree, LUAVALUE_REL, transform_luavalue(read(tree, LUAVALUE_REL)))
    write(tree, HELP_REL, transform_help(read(tree, HELP_REL), ids))


def tree_files() -> list:
    """Tree-relative paths a completed apply must have produced."""
    return [f"{TREE_SMALI}/{rel}" for rel in templates()]
