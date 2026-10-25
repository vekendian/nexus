"""The `nexus.*` Lua namespace: templates, Script.smali registration, policy.

Three layers are kept honest here:

  * **templates** -- the five smali classes are rendered against the lock file,
    so a placeholder that does not resolve (or an op that is missing from the
    table) must fail a test, not an APK;
  * **the registration** -- Script.smali is GameGuardian's file. The one call
    line is asserted against the stock tree, including its exact position
    (after `gg`, before the next statement), and the helper's failure-proofing;
  * **the policy** -- PermRules is pure Java, so it is compiled and executed
    like nexus.Name instead of being asserted on source text. The prompt code
    around it (the latch, the button mapping) is only reachable on a device and
    is asserted structurally.

What these cannot assert: that a script sees the table, that the dialog shows,
or that a grant is honoured at runtime. That needs a device.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from nexus.anchors import PatchError, anchor_count
from nexus.ids import Ids
from nexus.luapatch import (HELP_ANCHOR, HELP_REL, SCRIPT_HELPER_MARK,
                            transform_help, transform_script)
from nexus.extensions import ENGINE, extensions_methods as modules_methods
from nexus.smali import (COUNT_NEW, _array_new, _sparse_switch, switch_new,
                         transform_config_adapter)
from nexus.tree import LOCK_PATH, RES_DIR

ANDROID = "{http://schemas.android.com/apk/res/android}"
GG_TREE = Path("/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/"
               "Kujtnodnookc_499.2_src")
LUA = RES_DIR / "smali_lua/org/vekendian/nexus/lua"

TEMPLATES = (
    "NexusLua.smali",
    "NexusLua$Extensions.smali",
    "NexusLua$Extensions$Fn.smali",
    "NexusLua$Extensions$Import.smali",
    "NexusLua$Extensions$Jfn.smali",
    "NexusLua$Perm.smali",
    "NexusLua$Perm$Ask.smali",
)
# The v1 surface, and nothing else: stopAll was dropped on purpose (it would
# silently kill every module, including ones the user started themselves), and
# run/stop went too: extensions load with require() and end with their script,
# so scripts have nothing to run or stop explicitly. import() is the exception
# in one way -- its capability is "extensions.import" for the builder and every
# function object it hands out, because importing, inspecting and calling one
# extension are one action.
OPS = ("extensions.install", "extensions.uninstall", "extensions.list")
TABLE_KEYS = ("install", "uninstall", "list", "import")


LUA_PREFIX = "org/vekendian/nexus/lua/"


def _ids() -> Ids:
    """The lock file plus the tree's public.xml when it is on disk, so the
    GG-name lookups (the click-target array, the sparse-switch) can resolve."""
    public = GG_TREE / "res/values/public.xml"
    return Ids.load(LOCK_PATH,
                    public.read_text(encoding="utf-8") if public.is_file() else None)


def _render(ids=None) -> dict:
    from nexus.luapatch import render
    return render(ids or _ids())


def _rendered(name: str, ids=None) -> str:
    return _render(ids)[LUA_PREFIX + name]


def _lua(rel: str) -> str:
    return (LUA / rel).read_text(encoding="utf-8")


def _code_only(smali: str) -> str:
    """Drop comments and directives so assertions cannot match prose."""
    keep = []
    for line in smali.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith("."):
            continue
        keep.append(s)
    return "\n".join(keep)


# ------------------------------------------------------------- the templates ---

def test_the_namespace_is_exactly_these_seven_classes():
    assert sorted(p.name for p in LUA.glob("*.smali")) == sorted(TEMPLATES)


def test_every_placeholder_resolves_against_the_lock_file():
    from nexus.luapatch import template_tokens
    ids = _ids()
    for rel, tokens in template_tokens().items():
        for token in tokens:
            ids.hex(token)  # raises PatchError when the name is not pinned
    for rel, text in _render(ids).items():
        assert "@@" not in text, f"{rel} has an unresolved placeholder"
        assert "@@ID:" not in text


def test_rendered_ids_are_the_pinned_ones():
    ids = _ids()
    out = _render(ids)
    ask = _rendered("NexusLua$Perm$Ask.smali", ids)
    for name in ("nexus_str_perm_title", "nexus_str_perm_msg",
                 "nexus_str_perm_allow_once", "nexus_str_perm_always",
                 "nexus_str_perm_deny"):
        assert f"const v1, {ids.hex(name)}" in ask, name


def test_every_op_is_registered_and_none_extra():
    text = _rendered("NexusLua$Extensions.smali")
    for key in TABLE_KEYS:
        assert f'"{key}"' in text, key
    assert text.count("NexusLua$Extensions$Fn;-><init>") == len(OPS), \
        "one Fn function object per plain op"
    assert text.count("NexusLua$Extensions$Import;-><init>") == 1, \
        "the import builder is registered once, with the environment as p2"
    for gone in ("modules.stopAll", "stopAll", '"run"', '"stop"'):
        assert gone not in text


def test_only_the_engine_category_owns_the_not_running_error():
    """`nexus` and `nexus.version` exist in every script; only a call that needs
    the engine may say the engine is not running."""
    assert "extension system is not running" in _code_only(
        _lua("NexusLua$Extensions$Fn.smali"))
    root = _code_only(_lua("NexusLua.smali"))
    assert "extension system is not running" not in root
    assert "version" in root
    assert "NexusLua$Extensions;->install" in root, \
        "the category table must be attached from the root installer"


def test_the_gate_order_is_ready_then_permission_then_call():
    code = _code_only(_lua("NexusLua$Extensions$Fn.smali"))
    i_ready = code.index("LuaBridge;->ready()Z")
    i_perm = code.index("NexusLua$Perm;->check(")
    i_call = code.index("LuaBridge;->call(")
    assert i_ready < i_perm < i_call, \
        "the engine check must precede the prompt, and the prompt the call"


def test_denial_is_a_lua_error_not_an_exception():
    code = _code_only(_lua("NexusLua$Extensions$Fn.smali"))
    assert "permission denied" in code
    # nil, err is produced by the error() helper for every failure.
    assert "LuaValue;->O2(" in code


# --------------------------------------------------- the Jfn import bridge ---


def test_jfn_gate_order_is_ready_then_permission_then_pack():
    code = _code_only(_lua("NexusLua$Extensions$Jfn.smali"))
    i_ready = code.index("LuaBridge;->ready()Z")
    i_perm = code.index("NexusLua$Perm;->check(")
    i_pack = code.index("StringBuilder;->append(Ljava/lang/String;")
    assert i_ready < i_perm < i_pack,         "engine check, then the prompt, then the packed record"


def test_jfn_writes_the_packed_record():
    """jar <tab> method <tab> pspec <tab> args, escaping inside args only."""
    code = _code_only(_lua("NexusLua$Extensions$Jfn.smali"))
    assert '"extensions.invoke"' in code
    # the record prefix order: jar, then method, then pspec, tab between each
    i_jar = code.index("->jar:Ljava/lang/String;")
    i_method = code.index("->method:Ljava/lang/String;")
    i_pspec = code.index("->pspec:Ljava/lang/String;")
    assert i_jar < i_method < i_pspec, "jar, method, pspec in record order"
    # tab separator constant 0x9, and the arg loop step
    assert "const/16 v7, 0x9" in code, "tab separator constant"
    assert "add-int/lit8 v2, v2, 0x1" in code, "arg loop step"


def test_jfn_retypes_by_declared_return():
    code = _code_only(_lua("NexusLua$Extensions$Jfn.smali"))
    assert "Double;->parseDouble" in code
    assert "Lluaj/LuaDouble;->J2(D)Lluaj/LuaNumber;" in code
    assert "Lluaj/LuaValue;->d:Lluaj/LuaBoolean;" in code  # 'v' -> true
    assert "Lluaj/LuaValue;->e:Lluaj/LuaBoolean;" in code  # 'b' -> false
    assert "Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;" in code
    for got in ("0x76", "0x73", "0x6e", "0x62"):  # v s n b
        assert got in code, f"ret type code {got}"


def test_jfn_relays_the_envelope():
    code = _code_only(_lua("NexusLua$Extensions$Jfn.smali"))
    assert '"e"' in code and '"r"' in code
    assert "malformed result from extension" in code


# ------------------------------------------------------- the import builder ---


def test_import_gate_order_is_ready_then_permission_then_probe():
    code = _code_only(_lua("NexusLua$Extensions$Import.smali"))
    i_ready = code.index("LuaBridge;->ready()Z")
    i_perm = code.index("NexusLua$Perm;->check(")
    i_spec = code.index('"extensions.spec"')
    i_source = code.index('"extensions.source"')
    assert i_ready < i_perm < i_spec < i_source,         "engine check, then the prompt, then spec, then source"


def test_import_loadstrings_in_the_callers_globals():
    code = _code_only(_lua("NexusLua$Extensions$Import.smali"))
    assert "Lluaj/Globals;->O3(Ljava/io/InputStream;Ljava/lang/String;Ljava/lang/String;Lluaj/LuaValue;)Lluaj/LuaValue;" in code
    assert "Lluaj/LuaValue;->call()Lluaj/LuaValue;" in code
    assert "check-cast v11, Lluaj/Globals;" in code
    assert "ByteArrayInputStream" in code
    # the load region is guarded: syntax and runtime errors of the module
    # degrade to nil, msg -- never a script-thread crash
    raw = _lua("NexusLua$Extensions$Import.smali")
    assert ":try_load" in raw and ":load_err" in raw


def test_import_skips_nothing_importable():
    code = _code_only(_lua("NexusLua$Extensions$Import.smali"))
    assert "nothing importable at " in code


# ------------------------------------------------------ the Script.smali edit ---

def _script_source() -> str:
    p = GG_TREE / "smali/android/ext/Script.smali"
    if not p.is_file():
        pytest.skip("no stock GG tree on disk")
    return p.read_text(encoding="utf-8")


def test_registration_lands_between_gg_and_the_next_statement():
    out = transform_script(_script_source())
    i_gg = out.index('    const-string p1, "gg"')
    i_call = out.index("Script;->nexusInstall")
    i_next = out.index('    const-string v0, "package"')
    assert i_gg < i_call < i_next
    assert out.count("Script;->nexusInstall"), "call present"
    assert out.count(SCRIPT_HELPER_MARK) == 1, "helper appended once"


def test_registration_helper_guards_and_swallows():
    """The helper runs inside GG's script startup: it must never throw, and it
    must not depend on the script having a path."""
    out = transform_script(_script_source())
    helper = _code_only(out[out.index(SCRIPT_HELPER_MARK):])
    assert "if-eqz p0," in helper and "if-eqz p1," in helper, \
        "null guards for the script and the environment"
    assert "if-eqz v0," in helper, "null guard for Script.U"
    assert "NexusLua;->install" in helper
    assert ".catch Ljava/lang/Throwable;" in out, \
        "a Throwable from the helper must be caught, not propagated"


def test_registration_refuses_a_double_patch():
    once = transform_script(_script_source())
    with pytest.raises(PatchError, match="already present"):
        transform_script(once)


def test_registration_anchor_is_unique_in_the_stock_tree():
    assert _script_source().count('    const-string p1, "gg"') == 1


# --------------------------------------------------- execute-script help ---

def _help_source() -> str:
    p = GG_TREE / HELP_REL
    if not p.is_file():
        pytest.skip("no stock GG tree on disk")
    return p.read_text(encoding="utf-8")


def _help_text() -> str:
    """The help string as the dialog shows it: quotes are resource syntax and
    ``\\n`` is Android's newline escape."""
    root = ET.fromstring(
        (RES_DIR / "res/values/nexus_strings.xml").read_text(encoding="utf-8"))
    for el in root.findall("string"):
        if el.get("name") == "nexus_str_lua_help":
            text = el.text or ""
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            return text.replace("\\n", "\n")
    raise AssertionError("nexus_str_lua_help is missing from nexus_strings.xml")


def _gg_names() -> list:
    """The names Script.call registers on the gg table, from the stock tree."""
    text = (GG_TREE / "smali/android/ext/Script.smali").read_text(encoding="utf-8")
    names = re.findall(
        r'const-string (v\d+), "(\w+)"\s*\n\s*invoke-virtual \{[^,]+, \1, '
        r'[^}]+\}, Lluaj/LuaValue;->c2\(', text)
    return sorted(name for _, name in names)


def test_help_replaces_the_print_gg_example_with_a_static_dialog():
    ids = _ids()
    src = _help_source()
    out = transform_help(src, ids)
    assert "Script;->R3()" not in out, "the inline example script is gone"
    assert r"print(\'gg =\', gg)" not in out
    assert f"const v0, {ids.hex('nexus_str_lua_help')}" in out
    assert "Landroid/ext/Tools;->h(Ljava/lang/String;I)V" in out
    assert "Landroid/ext/b2;->f(I)Ljava/lang/String;" in out
    assert out.count(":cond_4") == src.count(":cond_4"), \
        "the case label itself (and its switch references) stay put"


def test_help_anchor_is_unique_in_the_stock_tree():
    assert anchor_count(_help_source(), HELP_ANCHOR) == 1


def test_help_refuses_a_double_patch():
    once = transform_help(_help_source(), _ids())
    with pytest.raises(PatchError, match="already patched"):
        transform_help(once, _ids())


def _gg_usage(name: str) -> str:
    """GG's own usage string for one method: the k3() text each class carries.

    refineNumber/refineAddress inherit searchNumber/searchAddress and do not
    override k3, so their line is derived the same way the behaviour is.
    """
    base = GG_TREE / "smali/android/ext"
    text = (base / f"Script${name}.smali").read_text(encoding="utf-8")
    m = re.search(r'\.method [^\n]*k3\(\)Ljava/lang/String;.*?'
                  r'const-string v\d+, "(.*?)"\s*\n.*?return-object',
                  text, re.S)
    if m:
        return m.group(1).replace("\\'", "'").replace('\\"', '"') \
                         .replace("\\\\", "\\")
    if name in ("refineNumber", "refineAddress"):
        return _gg_usage("search" + name[len("refine"):]).replace(
            "gg.search", "gg.refine", 1)
    raise AssertionError(f"no usage string for gg.{name}")


def test_help_text_matches_every_gg_signature():
    text = _help_text()
    names = _gg_names()
    assert len(names) == 68, "gg's method count changed; regenerate the help"
    assert "68 methods" in text
    for name in names:
        assert _gg_usage(name) in text, name


def test_help_text_covers_the_nexus_surface():
    text = _help_text()
    assert "nexus.version = 1.0" in text
    assert "nexus.extensions.install(string path) -> true || string with error" in text
    assert "nexus.extensions.uninstall(string path) -> true || string with error" in text
    assert "nexus.extensions.list() -> table || string with error" in text
    assert "nexus.extensions.import(string name) -> module || nil + string with error" in text
    assert "nexus.extensions.install('/sdcard/Download/module.dex')" in text
    assert "import(name)  name is the file name without .jar/.dex/.lua" in text
    assert "local zip = nexus.extensions.import('zip')" in text
    assert "zip.compress('/sdcard/Download/folder', 5)" in text
    assert "path, name, state, version, autostart" in text
    assert "idle, running, finished, stopped, error" in text
    assert "install(path)" in text
    assert "uninstall  takes a path returned by install or list" in text
    assert "nexus.extensions.run" not in text
    assert "nexus.extensions.stop" not in text
    assert "Deny / Allow once / Always allow" in text
    assert "floating Settings > Permissions" in text
    assert "string, table, math, os, io, debug, package" in text


def test_help_text_is_plain_static_and_has_no_format_wildcards():
    text = _help_text()
    assert text.isascii()
    assert "%" not in text, "string formatting would eat percent signs"
    assert "stopAll" not in text, "stopAll is not part of the v1 surface"


# ------------------------------------------------------- prompt mechanics ---

def test_prompt_blocks_on_a_count_down_latch_with_a_timeout():
    code = _code_only(_lua("NexusLua$Perm.smali"))
    assert "Ljava/util/concurrent/CountDownLatch;-><init>(I)V" in code
    assert "await(JLjava/util/concurrent/TimeUnit;)Z" in code
    assert "0x927c0" in code, "600000 ms timeout (10 minutes)"
    assert "Landroid/ext/n2;->i(Ljava/lang/Runnable;)V" in code, \
        "the dialog must be posted to the main thread"


def test_prompt_uses_the_nexus_dialog_theme():
    code = _code_only(_lua("NexusLua$Perm$Ask.smali"))
    assert "NexusHost;->dialogBuilder()Landroid/app/AlertDialog$Builder;" in code
    assert "Landroid/ext/f;->b()Landroid/app/AlertDialog$Builder;" not in code
    assert "if-eqz v0, :nexus_dialog_done" in code


def test_prompt_buttons_map_to_once_always_deny():
    code = _code_only(_lua("NexusLua$Perm$Ask.smali"))
    # BUTTON_POSITIVE -1 -> allow once (remember stays 0)
    assert "const/4 v1, -0x1" in code
    assert "const/4 v1, -0x3" in code
    # BUTTON_NEGATIVE is "the rest": volatilize nothing, decision 2
    assert "const/4 v1, 0x2" in code
    assert code.count("iput-byte v0,") == 2, "positive and neutral both allow"
    assert code.count("iput-boolean v0,") == 1, "only neutral remembers"
    assert "countDown()V" in code, "every click releases the script thread"


def test_dismissal_counts_down_too():
    """A back-button dismissal must read as decline, not deadlock."""
    raw = _lua("NexusLua$Perm$Ask.smali")
    on_dismiss = _code_only(raw[raw.index("public onDismiss"):])
    assert "countDown()V" in on_dismiss


def test_only_always_allow_is_persisted():
    code = _code_only(_lua("NexusLua$Perm.smali"))
    assert "NexusLua$Perm$Ask;->remember()Z" in code
    assert code.count("LuaBridge;->remember(") == 1
    # remember() sits on the allowed+remember path, not on allow-once.
    i_allowed = code.index("$Ask;->allowed()Z")
    i_remember = code.index("LuaBridge;->remember(")
    assert i_allowed < i_remember


def test_the_perm_bridge_calls_extensions_classes_by_full_descriptor():
    """The gate and the prompt hand work to LuaBridge / NexusHost with the FULL
    package descriptor. The rename era left an org.vekendian.nexus.modules path
    compiled into one of these templates: it linked fine and then threw
    NoSuchMethodError the first time a script asked for a capability."""
    for rel, needle in (
        ("NexusLua$Perm.smali",
         "invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/LuaBridge;->policy(Ljava/lang/String;Ljava/lang/String;)I"),
        ("NexusLua$Perm.smali",
         "invoke-static {p0, p1}, Lorg/vekendian/nexus/extensions/LuaBridge;->remember(Ljava/lang/String;Ljava/lang/String;)V"),
        ("NexusLua$Perm$Ask.smali",
         "invoke-static {}, Lorg/vekendian/nexus/extensions/NexusHost;->dialogBuilder()Landroid/app/AlertDialog$Builder;"),
        ("NexusLua$Perm$Ask.smali",
         "invoke-static {v1, v2, v3}, Lorg/vekendian/nexus/extensions/LuaBridge;->permMessage(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;"),
    ):
        assert needle in _lua(rel), rel


def test_prompt_message_uses_the_formatted_string_resource():
    java = (RES_DIR / "java/host/org/vekendian/nexus/extensions/LuaBridge.java"
            ).read_text(encoding="utf-8")
    assert "getString(templateId)" in java
    xml = (RES_DIR / "res/values/nexus_strings.xml").read_text(encoding="utf-8")
    assert "Allow %1$s to call %2$s?" in xml
    assert 'name="nexus_str_perm_msg"' in xml


# --------------------------------------------------- settings screen wiring ---

def test_the_permissions_row_moved_to_the_floating_settings():
    ids = _ids()
    if not ids.tree_public:
        pytest.skip("no stock GG tree on disk (ids.gg needs its public.xml)")
    row = ids.hex("nexus_row_permissions")
    # It is no longer a main-panel click target.
    assert row not in _array_new(ids)
    assert f"{row} -> :sswitch_nexus_permissions" not in _sparse_switch(ids)
    assert ":sswitch_nexus_permissions" not in switch_new(ids)
    assert "const/16 v1, 0x10" in COUNT_NEW, "16 main-panel click targets now"

    # ...and ConfigListAdapter dispatches the floating row.
    src = GG_TREE / "smali/android/ext/ConfigListAdapter.smali"
    if not src.is_file():
        pytest.skip("no stock GG tree on disk")
    out = transform_config_adapter(src.read_text(encoding="utf-8"), ids)
    assert f"{row} -> :sswitch_nexus_permissions" in out
    assert "Landroid/ext/r;->nexusPermissionsOpen(Landroid/content/Context;)V" in out
    assert transform_config_adapter(out, ids) == out, "transform must be idempotent"


def test_the_delegate_hands_the_dialog_its_individual_ids():
    raw = modules_methods(_ids())
    assert ".method public static nexusPermissionsOpen(Landroid/content/Context;)V" in raw
    code = _code_only(raw)
    assert "new-array v0, v3, [I" in code
    assert "NexusHost;->permissions(Landroid/content/Context;[I)V" in code
    assert "const/16 v3, 0xc" in code, "title + 4 actions + 2 status + 4 caps"
    for name in ("nexus_str_perm_title", "nexus_str_perm_allow",
                 "nexus_str_perm_ask", "nexus_str_perm_allow_all",
                 "nexus_str_perm_ask_all", "nexus_str_perm_reset",
                 "nexus_str_perm_reset_done", "nexus_str_perm_close",
                 "nexus_str_perm_install", "nexus_str_perm_uninstall",
                 "nexus_str_perm_list", "nexus_str_perm_import"):
        assert f"@@ID:{name}@@" not in raw
    assert "nexus_str_perm_all@@" not in raw
    assert "nexus_str_perm_group@@" not in raw


# ------------------------------------------------------------ the policy ---

_POLICY_CASES = [
    # (script, capability)
    ("/storage/emulated/0/Download/probe.lua", "extensions.install"),
    ("/storage/emulated/0/Download/probe.lua", "extensions"),
    ("", "*"),
]


def _policy_runner(tmp_path):
    """Compile PermRules.java and drive it through a small Runner."""
    javac, java = shutil.which("javac"), shutil.which("java")
    if not (javac and java):
        pytest.skip("no JDK on this machine; run build-engine.sh to compile instead")
    src = RES_DIR / "java/host/org/vekendian/nexus/extensions/PermRules.java"
    assert src.is_file()
    work = tmp_path / "perm"
    work.mkdir()
    (work / "Runner.java").write_text(
        "public class Runner {\n"
        "  public static void main(String[] a) throws Exception {\n"
        "    Class<?> c = Class.forName(\"org.vekendian.nexus.extensions.PermRules\");\n"
        "    java.lang.reflect.Method keys = c.getDeclaredMethod("
        "\"candidateKeys\", String.class, String.class);\n"
        "    java.lang.reflect.Method granted = c.getDeclaredMethod("
        "\"granted\", java.util.Map.class, String.class, String.class);\n"
        "    keys.setAccessible(true);\n"
        "    granted.setAccessible(true);\n"
        "    java.io.BufferedReader in = new java.io.BufferedReader("
        "new java.io.InputStreamReader(System.in, \"UTF-8\"));\n"
        "    String line;\n"
        "    while ((line = in.readLine()) != null) {\n"
        "      String[] p = line.split(\"\\t\", -1);\n"
        "      String script = p[0], cap = p[1];\n"
        "      String[] ks = (String[]) keys.invoke(null, script, cap);\n"
        "      System.out.println(\"KEYS|\" + String.join(\"|\", ks));\n"
        "      for (int i = 0; i < ks.length; i++) {\n"
        "        java.util.Map<String, Boolean> m = new java.util.HashMap<>();\n"
        "        m.put(ks[i], Boolean.TRUE);\n"
        "        System.out.println(\"GRANT|\" + i + \"|\" + granted.invoke(null, m, script, cap));\n"
        "      }\n"
        "      System.out.println(\"NONE|\" + granted.invoke(null,"
        " new java.util.HashMap<String, Boolean>(), script, cap));\n"
        "    }\n"
        "  }\n"
        "}\n", encoding="utf-8")
    subprocess.run([javac, "-nowarn", "-proc:none", "-d", str(work),
                    str(src), str(work / "Runner.java")], check=True,
                   capture_output=True)
    stdin = "\n".join(f"{s}\t{c}" for s, c in _POLICY_CASES) + "\n"
    out = subprocess.run([java, "-cp", str(work), "Runner"],
                         input=stdin.encode("utf-8"), check=True,
                         capture_output=True)
    lines = out.stdout.decode("utf-8").splitlines()
    # Group the flat output back into one dict per case, in order.
    per_case, cur = [], None
    for line in lines:
        tag, rest = line.split("|", 1)
        if tag == "KEYS":
            cur = {"keys": rest.split("|")}
            per_case.append(cur)
        elif tag == "GRANT":
            i, ok = rest.split("|")
            cur.setdefault("grants", {})[int(i)] = ok == "true"
        elif tag == "NONE":
            cur["none"] = rest == "true"
    return per_case


def test_candidate_order_is_script_exact_then_cap_group_all(tmp_path):
    cases = _policy_runner(tmp_path)
    script, cap = _POLICY_CASES[0]
    digest = hashlib.sha1(script.encode("utf-8")).hexdigest()
    assert cases[0]["keys"] == [
        f"s:{digest}:{cap}",
        f"g:{cap}",
        "g:extensions.*",
        "g:*",
    ]


def test_each_candidate_key_grants_on_its_own(tmp_path):
    """Every key in the list must actually be honoured: a stored per-script
    choice, an exact global, a group grant and the catch-all."""
    for case in _policy_runner(tmp_path):
        n = len(case["keys"])
        assert case.get("grants") == {i: True for i in range(n)}, case
        assert case["none"] is False, "nothing stored must mean ask"


def test_an_op_without_a_dot_has_no_group_key(tmp_path):
    cases = _policy_runner(tmp_path)
    script = _POLICY_CASES[1][0]
    digest = hashlib.sha1(script.encode("utf-8")).hexdigest()
    assert cases[1]["keys"] == [f"s:{digest}:extensions", "g:extensions", "g:*"]


def test_candidates_never_repeat(tmp_path):
    """Capabilities that are also groups ("*", "extensions.*") must not emit the
    same key twice."""
    for case in _policy_runner(tmp_path):
        assert len(case["keys"]) == len(set(case["keys"])), case["keys"]
