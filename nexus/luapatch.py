"""The Lua-facing `nexus.*` namespace, rendered and injected.

Three jobs, one file, because they share one contract:

* **Templates** live in ``resources/smali_lua/org/vekendian/nexus/lua/`` with
  ``@@ID:name@@`` placeholders and are rendered against the id lock file at
  apply time. They cannot live in ``resources/smali`` (which copy_smali copies
  verbatim) because a placeholder must never reach the tree.

* **Script.smali** gets one call line (``nexusInstall``) right after
  GameGuardian registers ``gg``, plus the helper method it calls.

* **o0$b.smali** (the Execute script dialog) gets its "?" (examples) action
  replaced. It used to run ``print('gg =', gg)`` and show a table reference;
  now it opens the static ``nexus_str_lua_help`` dialog, which documents the
  gg API and the nexus.* surface in GameGuardian's scrollable/copyable text
  window.

Everything else is the ordinary Java pipeline: ``resources/java/host`` compiles
to the tree's ``org/vekendian/nexus/extensions`` package, and the smali here only
builds the Lua tables, blocks on the permission prompt, and dispatches into
``LuaBridge``. See ``resources/java/host/org/vekendian/nexus/extensions/LuaBridge.java``
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
#     starting. The Lua side reports "extension system is not running" instead.
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
'''

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


def apply(tree: Path, ids) -> None:
    """install() + both smali transforms, the set cli._patch calls."""
    install(tree, ids)
    write(tree, SCRIPT_REL, transform_script(read(tree, SCRIPT_REL)))
    write(tree, HELP_REL, transform_help(read(tree, HELP_REL), ids))


def tree_files() -> list:
    """Tree-relative paths a completed apply must have produced."""
    return [f"{TREE_SMALI}/{rel}" for rel in templates()]
