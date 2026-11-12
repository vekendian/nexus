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
from nexus.modules import ENGINE, modules_methods as modules_methods
from nexus.smali import (COUNT_NEW, _array_new, _sparse_switch, switch_new,
                         transform_config_adapter)
from nexus.tree import LOCK_PATH, RES_DIR

ANDROID = "{http://schemas.android.com/apk/res/android}"
GG_TREE = Path("/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/"
               "Kujtnodnookc_499.2_src")
LUA = RES_DIR / "smali_lua/org/vekendian/nexus/lua"

TEMPLATES = (
    "NexusLua.smali",
    "NexusLua$Modules.smali",
    "NexusLua$Modules$Fn.smali",
    "NexusLua$Modules$Import.smali",
    "NexusLua$Modules$Jfn.smali",
    "NexusLua$Modules$Cls.smali",
    "NexusLua$Perm.smali",
    "NexusLua$Perm$Ask.smali",
)
# The v1 surface, and nothing else: stopAll was dropped on purpose (it would
# silently kill the whole namespace, including ones the user started themselves), and
# run/stop went too: extensions load with require() and end with their script,
# so scripts have nothing to run or stop explicitly. import() is the exception
# in one way -- its capability is "modules.import" for the builder and every
# function object it hands out, because importing, inspecting and calling one
# extension are one action.
OPS = ("modules.install", "modules.uninstall", "modules.list")
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

def test_the_namespace_is_exactly_these_eight_classes():
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
    text = _rendered("NexusLua$Modules.smali")
    for key in TABLE_KEYS:
        assert f'"{key}"' in text, key
    assert text.count("NexusLua$Modules$Fn;-><init>") == len(OPS), \
        "one Fn function object per plain op"
    assert text.count("NexusLua$Modules$Import;-><init>") == 1, \
        "the import builder is registered once, with the environment as p2"
    for gone in ("modules.stopAll", "stopAll", '"run"', '"stop"'):
        assert gone not in text


def test_only_the_engine_category_owns_the_not_running_error():
    """`nexus` and `nexus.version` exist in every script; only a call that needs
    the engine may say the engine is not running."""
    assert "module system is not running" in _code_only(
        _lua("NexusLua$Modules$Fn.smali"))
    root = _code_only(_lua("NexusLua.smali"))
    assert "module system is not running" not in root
    assert "version" in root
    assert "NexusLua$Modules;->install" in root, \
        "the category table must be attached from the root installer"


def test_the_nexus_global_is_bound_before_the_categories():
    """The Script-side helper runs this whole install under a silent Throwable
    catch. If a category could abort the install, the script would see a nil
    nexus outright -- even nexus.version unreadable. Binding the global first
    caps any such failure at a missing sub-table."""
    code = _code_only(_lua("NexusLua.smali"))
    assert code.index('"nexus"') < code.index("NexusLua$Modules;->install"), \
        "the nexus global must be installed before any category attaches"


# ------------------------------------------------ every luaj ref resolves ---


def _luaj_index():
    """Stock luaj classes -> {(name, params, return)} for methods and
    {name: type} for fields. Exact descriptor text, as both smali forms use
    it: the method name is the token before the first '(' -- plain parsing,
    because a regex over ".method public static K2(..." would happily hand
    back "2" as the name."""
    methods, fields = {}, {}
    # Stock first, then the port's overrides: a class the port re-ships (Hlp,
    # LuaUserdata) keeps every stock method and gains the port's, which is what
    # the applied tree actually contains.
    roots = (GG_TREE / "smali/luaj", RES_DIR / "smali_luajava/luaj")
    for p in [q for root in roots if root.is_dir() for q in sorted(root.glob("*.smali"))]:
        ms, fs = set(), {}
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith(".method "):
                head, tail = line.split("(", 1)
                params, ret = tail.split(")", 1)
                ms.add((head.rsplit(None, 1)[-1], params, ret.strip()))
            elif line.startswith(".field "):
                rest = line[7:]
                colon = rest.rfind(":")
                if colon > 0:
                    fs[rest[:colon].rsplit(None, 1)[-1]] = rest[colon + 1:].split(None, 1)[0]
        if ms:
            methods.setdefault(p.stem, set()).update(ms)
        if fs:
            fields.setdefault(p.stem, {}).update(fs)
    return methods, fields


def test_every_luaj_reference_in_the_templates_resolves():
    """Our smali targets the luaj inside GG's obfuscated build -- and LuaJ here
    has NO LuaValue.valueOf at all: Lluaj/LuaValue;->valueOf(...) assembled
    fine (an unresolvable reference is just a symbolic link) and then died with
    NoSuchMethodError on the first script, which Script.nexusInstall eats
    silently -- the symptom was a bare nil `nexus`. So every Lluaj/X;->...(...)
    method call and every ->field:L...; field reference the templates make
    must exist in the stock tree, by full shape, not by hope."""
    index_m, index_f = _luaj_index()
    if not index_m and not index_f:
        pytest.skip("no stock GG tree on disk")
    bad = []
    for tpl in TEMPLATES:
        src = (LUA / tpl).read_text(encoding="utf-8")
        for m in re.finditer(r"Lluaj/([A-Za-z0-9_$]+);->([A-Za-z0-9_$<>]+)\(([^)]*)\)"
                             r"(L[^;\s]+;|V|Z|I|J|D|F|B|C|S)", src):
            cls, name, params, ret = m.groups()
            known = index_m.get(cls)
            if known is None:
                bad.append(f"{tpl}: class {cls} has no stock smali")
            elif (name, params, ret) not in known:
                bad.append(f"{tpl}: no Lluaj/{cls};->{name}({params}){ret} in stock")
        for m in re.finditer(r"Lluaj/([A-Za-z0-9_$]+);->([A-Za-z0-9_$]+):"
                             r"(L[^;\s]+;|Z|I|J|D|F|B|C|S)", src):
            cls, name, ftype = m.groups()
            known = index_f.get(cls)
            if known is None:
                bad.append(f"{tpl}: class {cls} has no stock smali")
            elif ftype != known.get(name):
                bad.append(f"{tpl}: no field Lluaj/{cls};->{name}:{ftype} in stock")
    assert not bad, "unresolvable luaj references:\n  " + "\n  ".join(bad)


def test_no_template_calls_a_private_method_virtually():
    """ART rejects the whole class when invoke-virtual/invoke-super names a
    private method of the same class (method_verifier.cc fails with
    VERIFY_ERROR_BAD_CLASS_HARD: "invoke-super/virtual can't be used on private
    method"). The rejection surfaces as a VerifyError at the first
    new-instance, so a private helper reached with invoke-virtual kills its
    caller. Inside NexusLua$Modules.install that is swallowed by
    Script.nexusInstall's Throwable catch, and the only visible symptom is a
    nil nexus.modules beside a working nexus.version. Private instance
    methods are reached with invoke-direct."""
    bad = []
    for tpl in TEMPLATES:
        src = (LUA / tpl).read_text(encoding="utf-8")
        cls = re.search(r"^\.class[^\n]*\sL([A-Za-z0-9_$/$]+);\s*$", src, re.M)
        if not cls:
            bad.append(f"{tpl}: no .class line")
            continue
        private = set()
        for line in src.splitlines():
            if not line.startswith(".method "):
                continue
            head, tail = line[len(".method "):].split("(", 1)
            params, ret = tail.split(")", 1)
            flags = head.split()[:-1]
            name = head.rsplit(None, 1)[-1]
            if ("private" in flags and "static" not in flags
                    and name not in ("<init>", "<clinit>")):
                private.add((name, params, ret.strip()))
        for m in re.finditer(r"invoke-(virtual|super)\s*\{[^}]*\},\s*"
                             r"L([A-Za-z0-9_$/$]+);->(\w+)\(([^)]*)\)(\S+)", src):
            kind, target, name, params, ret = m.groups()
            if target != cls.group(1):
                continue
            if (name, params, ret) in private:
                bad.append(f"{tpl}: invoke-{kind} on private {name}({params}){ret}")
    assert not bad, "ART would reject these classes:\n  " + "\n  ".join(bad)


# Visibility is checked when the instruction resolves, not when the class is
# verified: a package-private member named from another package throws
# IllegalAccessError on the first execution, after the APK builds cleanly and
# after any earlier lines have already run. That is how
# NexusLua$Modules$Cls -> JavaClass.forClass broke import() on the device
# while every local check passed.

_INVOKE = re.compile(r"invoke-\w+ \{[^}]*\}, L([^;]+);->([^(\s]+)\(([^)]*)\)(\S+)")
_FIELD = re.compile(r"(?:sget|sput|iget|iput)-\w+ \{[^}]*\}, L([^;]+);->([^:\s]+):(\S+)")


def _class_descriptor(text):
    """The class a smali file declares, without its L...; wrapper. Splitting the
    .class line is deliberate: a greedy regex stops at the last L in the name
    (LuajavaLib -> "ib") and then every lookup silently misses."""
    for line in text.splitlines():
        if line.startswith(".class "):
            for token in line.split():
                if len(token) > 2 and token[0] == "L" and token.endswith(";"):
                    return token[1:-1]
    return None


def _smali_index(roots):
    """descriptor -> path, first root wins (the stock tree before our additions)."""
    index = {}
    for root in roots:
        for path in Path(root).rglob("*.smali"):
            desc = _class_descriptor(path.read_text(encoding="utf-8", errors="replace"))
            if desc:
                index.setdefault(desc, path)
    return index


def _declaration_flags(path, name, kind, signature):
    """Flag lists for the exact member, [] when the file does not declare it.
    The signature keeps overloads apart: android.ext.Tools.a(Context)V says
    nothing about android.ext.Tools.a(String, Object[])String."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if kind == "method":
        pat = re.compile(r"^\.method ([^\n]*?)\b" + re.escape(name) + r"\("
                         + re.escape(signature) + r"\s*$", re.M)
    else:
        pat = re.compile(r"^\.field ([^\n]*?)\b" + re.escape(name) + r":"
                         + re.escape(signature) + r"\s*$", re.M)
    return [m.group(1).split() for m in pat.finditer(text)]


def _super_of(text):
    for line in text.splitlines():
        if line.startswith(".super "):
            token = line.split()[1]
            if token.startswith("L") and token.endswith(";"):
                return token[1:-1]
    return None


def _is_subclass(caller, target, index):
    """Protected static members are reachable from subclasses in other packages."""
    seen = set()
    desc = caller
    while desc and desc not in seen:
        seen.add(desc)
        path = index.get(desc)
        if not path:
            return False
        desc = _super_of(path.read_text(encoding="utf-8", errors="replace"))
        if desc == target:
            return True
    return False


def _member_is_reachable(path, name, kind, signature, caller, target, index):
    """True/False, or None when the target file does not declare the member."""
    flags = _declaration_flags(path, name, kind, signature)
    if not flags:
        return None
    for mods in flags:
        if "public" in mods:
            return True
        if "protected" in mods and _is_subclass(caller, target, index):
            return True
    return False


def _nonpublic_cross_package_calls(callers, index):
    bad = []
    for path in callers:
        text = path.read_text(encoding="utf-8", errors="replace")
        caller = _class_descriptor(text)
        if not caller:
            continue
        caller_pkg = caller.rsplit("/", 1)[0] if "/" in caller else ""
        for kind, pattern in (("method", _INVOKE), ("field", _FIELD)):
            for hit in pattern.finditer(text):
                target, name = hit.group(1), hit.group(2)
                if kind == "method":
                    signature = f"{hit.group(3)}){hit.group(4)}"
                else:
                    signature = hit.group(3)
                if target not in index:
                    continue
                target_pkg = target.rsplit("/", 1)[0] if "/" in target else ""
                if target_pkg == caller_pkg:
                    continue
                reachable = _member_is_reachable(index[target], name, kind, signature,
                                                 caller, target, index)
                if reachable is False:
                    bad.append(f"{path.name}: {kind} {target}->{name}({signature})"
                               " is neither public nor protected-for-a-subclass")
    return bad


def test_no_added_class_reaches_a_non_public_member_across_packages():
    index = _smali_index([GG_TREE / "smali", RES_DIR / "smali_luajava",
                          RES_DIR / "smali_lua"])
    callers = list(LUA.rglob("*.smali")) + list((RES_DIR / "smali_luajava").rglob("*.smali"))
    bad = _nonpublic_cross_package_calls(callers, index)
    assert not bad, "IllegalAccessError on the device:\n  " + "\n  ".join(bad)


def test_the_visibility_scan_flags_a_package_private_target(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a/A.smali").write_text(
        ".class public La/A;\n"
        ".method public static run()V\n"
        "    invoke-static {}, Lb/B;->hidden()V\n"
        ".end method\n", encoding="utf-8")
    (tmp_path / "b/B.smali").write_text(
        ".class public Lb/B;\n"
        ".method static hidden()V\n"
        "    return-void\n"
        ".end method\n", encoding="utf-8")
    index = _smali_index([tmp_path])
    bad = _nonpublic_cross_package_calls([tmp_path / "a/A.smali"], index)
    assert bad and "hidden" in bad[0]


# --------------------------------------------- classes from an imported module ---

def _method_body(smali: str, header: str) -> str:
    """One method, comments dropped. _code_only cannot be used here because it
    drops the ".method" line the slice needs to start from."""
    start = smali.index(header)
    end = smali.index(".end method", start)
    return "\n".join(line for line in smali[start:end].splitlines()
                     if not line.strip().startswith("#"))


def test_both_jar_paths_register_the_module_loader():
    """A module with exports and a module with only classes both hand their
    ClassLoader to luaj: either kind can carry classes worth reaching. The
    helper is the only caller, so one bridge op and one registry write."""
    code = _code_only(_lua("NexusLua$Modules$Import.smali"))
    assert code.count("->registerLoader(Ljava/lang/String;)Z") == 2, \
        "one call for the export table, one for the class-only table"
    assert '"modules.loader"' in code
    assert "Lluaj/Hlp;->registerDex(Ljava/lang/ClassLoader;)V" in code


def test_an_empty_spec_still_imports_a_class_only_module():
    """No @Export records used to mean "nothing importable". A module with a
    loader returns the class table instead; a .lua, which has no loader, keeps
    going to the source probe."""
    code = _code_only(_lua("NexusLua$Modules$Import.smali"))
    assert "if-lez v1, :class_only" in code, "empty spec is a branch, not an exit"
    assert "if-eqz v0, :source" in code, "no loader means the source probe"
    assert "NexusLua$Modules$Import;->classTable(" in code


def test_the_class_table_is_a_metatable_index():
    """LuaTable.get consults __index only after the raw lookup misses, so
    exports -- real keys -- win over a same-named class, and resolution stays
    lazy: nothing enumerates the dex."""
    import_code = _code_only(_lua("NexusLua$Modules$Import.smali"))
    assert '"__index"' in import_code
    assert "Lluaj/LuaTable;->k2(Lluaj/LuaValue;)Lluaj/LuaValue;" in import_code
    cls = _code_only(_lua("NexusLua$Modules$Cls.smali"))
    assert "Lluaj/Hlp;->classForNameInDexes(Ljava/lang/String;)Ljava/lang/Class;" in cls
    # JavaClass and its forClass are package-private, so naming them from this class
    # throws IllegalAccessError on the device. CoerceJavaToLua.coerce is the public
    # door to the same per-Class cache and returns the very same JavaClass.
    assert "Lluaj/lib/jse/CoerceJavaToLua;->coerce(Ljava/lang/Object;)Lluaj/LuaValue;" in cls
    assert "JavaClass;->forClass" not in cls
    # a miss is nil, never an error: __index runs on every absent key
    assert "Lluaj/LuaValue;->c:Lluaj/LuaValue;" in cls


def test_class_lookup_prefers_the_module_id_as_the_package():
    cls = _code_only(_lua("NexusLua$Modules$Cls.smali"))
    i_id = cls.index("->id:Ljava/lang/String;")
    i_dot = cls.index('const-string v1, "."')
    i_first = cls.index("classForNameInDexes")
    assert i_id < i_dot < i_first, "id + '.' + key is tried first, bare key second"


def test_the_bare_key_path_returns_a_hit_and_only_a_miss_is_nil():
    """if-eqz/if-nez branch on ZERO. The bare-key path was written as
    `if-eqz v2, :found`, which is exactly backwards: a found class (v2 != 0)
    fell into :nil and a miss (v2 == 0) went to coerce with null. import()
    then returned nil for every bare class name -- silently, since nothing
    throws. A hit has to jump back to the shared coerce block; a miss exits
    through :nil."""
    cls = _code_only(_lua("NexusLua$Modules$Cls.smali"))
    assert "if-eqz v2, :nil" in cls, "a null lookup is the nil case"
    assert "goto :found" in cls, "a hit reaches the coerce block"
    # if-nez branches on non-zero: `if-nez v2, :nil` sends every HIT to nil.
    assert "if-nez v2, :nil" not in cls, "inverted guard: a hit would be dropped"
    assert "if-eqz v2, :found" not in cls, "the original inversion: a miss coerces null"
    i_bare = cls.index(":bare")
    i_nil_guard = cls.index("if-eqz v2, :nil", i_bare)
    i_found = cls.index("goto :found", i_bare)
    assert i_bare < i_nil_guard < i_found, "guard, then jump back to :found"


def test_luajava_bind_class_falls_back_to_the_module_loaders():
    """bindClass still throws for a name nothing knows -- only the miss path
    changed, so the app classloader keeps priority."""
    text = (RES_DIR / "smali_luajava/luaj/lib/jse/LuajavaLib.smali").read_text(encoding="utf-8")
    body = _method_body(text, ".method protected classForName(")
    assert "Lluaj/Hlp;->classForNameInDexes(Ljava/lang/String;)Ljava/lang/Class;" in body
    assert "move-exception" in body, "the original ClassNotFoundException is kept"
    assert "throw" in body, "and rethrown when no loader knows the name"


def test_register_dex_stores_a_loader_once_and_ignores_a_missing_one():
    """Hlp.dexes is the list classForNameInDexes walks, so a guard inverted here
    fails silently: every import still reports success, the table still builds,
    and only the first class lookup shows the loss. `if-eqz` returns on a null
    loader (a .lua module, or a jar that failed to prepare); `if-nez` returns on
    "already registered"; the add is reached exactly once per new loader."""
    text = (RES_DIR / "smali_luajava/luaj/Hlp.smali").read_text(encoding="utf-8")
    body = _method_body(text, ".method public static registerDex(")
    assert "if-eqz p0, :return" in body, "a null loader is skipped, not stored"
    assert "if-nez v0, :return" in body, "a loader already in the list is not added twice"
    assert "ArrayList;->add(Ljava/lang/Object;)Z" in body, "add returns boolean"
    assert "if-nez p0" not in body, "inverted null guard: dexes stays empty"
    assert "if-eqz v0, :return" not in body, "inverted contains guard: same"


def test_collection_add_keeps_its_boolean_return():
    """ArrayList.add returns boolean. A `)V` descriptor assembles without a
    warning and only fails on the device, the first time the list is actually
    written -- NoSuchMethodError: No virtual method add(Ljava/lang/Object;)V.
    That is one error past "the guards are right", so it is checked here."""
    bad = []
    for path in sorted((RES_DIR / "smali_luajava").rglob("*.smali")):
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if "->add(" in line and not line.rstrip().endswith(")Z"):
                bad.append(f"{path.relative_to(RES_DIR)}:{i}: {line.strip()}")
    assert not bad, "add() must return Z:\n  " + "\n  ".join(bad)


def test_the_loader_op_is_dispatched_and_silent_for_a_lua_module():
    bridge = (RES_DIR / "java/host/org/vekendian/nexus/modules/LuaBridge.java"
              ).read_text(encoding="utf-8")
    assert 'if ("loader".equals(fn))' in bridge
    assert "LuaModules.loader(executor, path)" in bridge
    host = (RES_DIR / "java/host/org/vekendian/nexus/modules/LuaModules.java"
            ).read_text(encoding="utf-8")
    assert "static Object loader(NexusExecutor executor, String id)" in host
    assert "executor.loadLibrary(id)" in host


def test_install_accepts_a_table_with_content():
    """install{content=...} copies the Lua string's bytes; the host Java side
    cannot reference luaj, so the slicing happens in the smali caller."""
    fn = _code_only(_lua("NexusLua$Modules$Fn.smali"))
    assert "Lluaj/LuaString;->P:[B" in fn
    assert "Lluaj/LuaString;->Q:I" in fn
    assert "Lluaj/LuaString;->R:I" in fn
    assert "Ljava/util/Arrays;->copyOfRange([BII)[B" in fn
    assert "LuaBridge;->installBytes(" in fn
    assert "LuaBridge;->installPath(" in fn


def test_install_table_metadata_fields():
    fn = _code_only(_lua("NexusLua$Modules$Fn.smali"))
    for key in ('"content"', '"path"', '"name"', '"description"',
                '"version"', '"type"'):
        assert key in fn, key


def test_list_split_keeps_trailing_empty_fields():
    """Java's String.split drops trailing empties. A module with an empty
    description and message would then split to 7 fields while table() reads
    nine, and list() would throw ArrayIndexOutOfBoundsException."""
    body = _method_body(_lua("NexusLua$Modules$Fn.smali"),
                        ".method private static table(")
    assert "split(Ljava/lang/String;I)[Ljava/lang/String;" in body
    assert "const/4 v6, -0x1" in body
    assert "split(Ljava/lang/String;)[Ljava/lang/String;" not in body


def test_list_records_carry_the_hash_fields():
    """list() returns a table per module with named fields, not a flat record
    a script has to index positionally."""
    host = (RES_DIR / "java/host/org/vekendian/nexus/modules/LuaModules.java"
            ).read_text(encoding="utf-8")
    for field in ("s.path()", "s.name()", "idOf(s.path())", "state(s.state())",
                  "s.version()", "s.autostart()", "type(s.type())",
                  "s.description()", "s.message()"):
        assert field in host, field
    fn = _lua("NexusLua$Modules$Fn.smali")
    for key in ("path", "name", "id", "state", "version", "autostart",
                "type", "description", "message"):
        assert f'const-string v5, "{key}"' in fn, key


def test_the_gate_order_is_ready_then_permission_then_call():
    code = _code_only(_lua("NexusLua$Modules$Fn.smali"))
    i_ready = code.index("LuaBridge;->ready()Z")
    i_perm = code.index("NexusLua$Perm;->check(")
    i_call = code.index("LuaBridge;->call(")
    assert i_ready < i_perm < i_call, \
        "the engine check must precede the prompt, and the prompt the call"


def test_denial_is_a_lua_error_not_an_exception():
    code = _code_only(_lua("NexusLua$Modules$Fn.smali"))
    assert "permission denied" in code
    # nil, err is produced by the error() helper for every failure.
    assert "LuaValue;->O2(" in code


# --------------------------------------------------- the Jfn import bridge ---


def test_jfn_gate_order_is_ready_then_permission_then_pack():
    code = _code_only(_lua("NexusLua$Modules$Jfn.smali"))
    i_ready = code.index("LuaBridge;->ready()Z")
    i_perm = code.index("NexusLua$Perm;->check(")
    i_pack = code.index("StringBuilder;->append(Ljava/lang/String;")
    assert i_ready < i_perm < i_pack,         "engine check, then the prompt, then the packed record"


def test_jfn_writes_the_packed_record():
    """jar <tab> method <tab> pspec <tab> args, escaping inside args only."""
    code = _code_only(_lua("NexusLua$Modules$Jfn.smali"))
    assert '"modules.invoke"' in code
    # the record prefix order: jar, then method, then pspec, tab between each
    i_jar = code.index("->jar:Ljava/lang/String;")
    i_method = code.index("->method:Ljava/lang/String;")
    i_pspec = code.index("->pspec:Ljava/lang/String;")
    assert i_jar < i_method < i_pspec, "jar, method, pspec in record order"
    # tab separator constant 0x9, and the arg loop step
    assert "const/16 v7, 0x9" in code, "tab separator constant"
    assert "add-int/lit8 v2, v2, 0x1" in code, "arg loop step"


def test_jfn_retypes_by_declared_return():
    code = _code_only(_lua("NexusLua$Modules$Jfn.smali"))
    assert "Double;->parseDouble" in code
    assert "Lluaj/LuaDouble;->J2(D)Lluaj/LuaNumber;" in code
    assert "Lluaj/LuaValue;->d:Lluaj/LuaBoolean;" in code  # 'v' -> true
    assert "Lluaj/LuaValue;->e:Lluaj/LuaBoolean;" in code  # 'b' -> false
    assert "Lluaj/LuaValue;->K2(Ljava/lang/String;)Lluaj/LuaString;" in code
    for got in ("0x76", "0x73", "0x6e", "0x62"):  # v s n b
        assert got in code, f"ret type code {got}"


def test_jfn_relays_the_envelope():
    code = _code_only(_lua("NexusLua$Modules$Jfn.smali"))
    assert '"e"' in code and '"r"' in code
    assert "malformed result from module" in code


def test_jfn_treats_only_the_e_tag_as_an_error():
    """The envelope is {"e", msg} or {"r", value}. The tag test was written
    `if-nez v1, :envelope_error`, which branches when the strings are NOT
    equal: an error envelope fell through and reported "malformed result from
    module", and a success envelope was handed to the error helper as its
    message. Every @Export call was affected; Eclipse never reaches here, which
    is why it survived the first on-device run."""
    code = _code_only(_lua("NexusLua$Modules$Jfn.smali"))
    assert "if-eqz v1, :tag_r" in code, "not \"e\" -> check for \"r\""
    assert "goto :envelope_error" in code, "an \"e\" tag relays the message"
    assert "if-nez v1, :envelope_error" not in code, "inverted tag guard"
    i_e = code.index('const-string v7, "e"')
    i_tag_r = code.index(":tag_r")
    i_r = code.index('const-string v7, "r"', i_tag_r)
    assert i_e < i_tag_r < i_r, "the e test, then the r test"
    # and only a non-"r" tag is malformed
    i_bad = code.index("if-eqz v1, :bad_envelope", i_r)
    assert i_bad > i_r


# ------------------------------------------------------- the import builder ---


def test_import_gate_order_is_ready_then_permission_then_probe():
    code = _code_only(_lua("NexusLua$Modules$Import.smali"))
    i_ready = code.index("LuaBridge;->ready()Z")
    i_perm = code.index("NexusLua$Perm;->check(")
    i_spec = code.index('"modules.spec"')
    i_source = code.index('"modules.source"')
    assert i_ready < i_perm < i_spec < i_source,         "engine check, then the prompt, then spec, then source"


def test_import_loadstrings_in_the_callers_globals():
    code = _code_only(_lua("NexusLua$Modules$Import.smali"))
    assert "Lluaj/Globals;->O3(Ljava/io/InputStream;Ljava/lang/String;Ljava/lang/String;Lluaj/LuaValue;)Lluaj/LuaValue;" in code
    assert "Lluaj/LuaValue;->call()Lluaj/LuaValue;" in code
    assert "check-cast v11, Lluaj/Globals;" in code
    assert "ByteArrayInputStream" in code
    # the load region is guarded: syntax and runtime errors of the extension
    # degrade to nil, msg -- never a script-thread crash
    raw = _lua("NexusLua$Modules$Import.smali")
    assert ":try_load" in raw and ":load_err" in raw


def test_import_skips_nothing_importable():
    code = _code_only(_lua("NexusLua$Modules$Import.smali"))
    assert "nothing importable at " in code


def test_engine_sends_the_source_envelope_import_loads():
    """The engine's luaSource answer must match the envelope the Import builder
    loads: {"r", source} on success, {"e", message} on failure. A one-element
    array -- the engine used to send -- fails the builder's length check and
    every .lua import surfaced as "nothing importable at <id>"."""
    reg = (RES_DIR / "java/dexexec/nexus/ModuleRegistry.java").read_text()
    assert 'return new String[]{"r", source};' in reg
    assert '"e", "cannot read lua source: "' in reg


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


def _gg_variables() -> list:
    """The uppercase constants Script.B3 registers on the gg table."""
    text = (GG_TREE / "smali/android/ext/Script.smali").read_text(encoding="utf-8")
    start = text.index(".method static B3(Lluaj/LuaTable;Ljava/util/ArrayList;)V")
    body = text[start:text.index(".end method", start)]
    names = re.findall(r'const-string v\d+, "([A-Z][A-Z0-9_]*)"', body)
    return sorted(set(names))


def test_help_text_documents_every_gg_constant():
    text = _help_text()
    names = _gg_variables()
    assert len(names) == 56, "gg's constant count changed; regenerate the help"
    assert "gg constants" in text
    for name in names:
        assert name in text, name


def test_help_text_covers_the_nexus_surface():
    text = _help_text()
    assert "nexus.version = 1.0" in text
    assert "nexus.modules.install(string path) -> true || string with error" in text
    assert "nexus.modules.uninstall(string path) -> true || string with error" in text
    assert "nexus.modules.list() -> table || string with error" in text
    assert "nexus.modules.import(string name) -> table || nil + string with error" in text
    assert "nexus.modules.install('/sdcard/Download/hello.dex')" in text
    assert "import(name)  name is the file name without .jar/.dex/.lua" in text
    assert "local zip = nexus.modules.import('zip')" in text
    assert "zip.compress('/sdcard/Download/folder', 5)" in text
    assert "path, name, id, state, version, autostart, type, description, message" in text
    assert "idle, running, finished, stopped, error" in text
    assert "install(path)" in text
    assert "uninstall  takes a path returned by install or list" in text
    assert "nexus.modules.run" not in text
    assert "nexus.modules.stop" not in text
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


def test_ask_policy_raises_the_prompt_and_allow_policy_skips_it():
    """ALLOW (1) skips the dialog; ASK (0) falls through to it.

    The branch used to be `if-ne`, so ASK -- the one policy whose whole
    purpose is to raise the prompt -- jumped straight to :granted. The dialog
    never appeared and every capability was silently allowed. ALLOW then fell
    through and prompted for something already granted.
    """
    code = _code_only(_lua("NexusLua$Perm.smali"))
    i_policy = code.index("LuaBridge;->policy(")
    i_prompt = code.index("Ljava/util/concurrent/CountDownLatch;-><init>")
    between = code[i_policy:i_prompt]
    assert "const/4 v1, 0x1" in between, "ALLOW is 1"
    assert "if-eq v0, v1, :granted" in between, \
        "policy == ALLOW must jump over the prompt; ASK must fall through"
    assert "if-ne v0, v1" not in between, "ASK would skip its own prompt"


def test_allowed_reports_the_allow_decision():
    """Both allow buttons store decision 1; allowed() must return true for it.

    The comparison was `if-ne`, so Allow returned false and Deny (2) or a
    back-button dismissal (0) returned true: the gate denied exactly the calls
    the user had just approved.
    """
    raw = _lua("NexusLua$Perm$Ask.smali")
    start = raw.index(".method public allowed()Z")
    body = raw[start:raw.index(".end method", start)]
    assert "const/4 v1, 0x1" in body, "decision 1 is allow"
    assert "if-eq v0, v1, :yes" in body
    assert "if-ne v0, v1" not in body


def test_prompt_uses_the_nexus_dialog_theme():
    code = _code_only(_lua("NexusLua$Perm$Ask.smali"))
    assert "NexusHost;->dialogBuilder()Landroid/app/AlertDialog$Builder;" in code
    assert "Landroid/ext/f;->b()Landroid/app/AlertDialog$Builder;" not in code
    assert "if-eqz v0, :nexus_dialog_done" in code


def test_prompt_buttons_map_to_once_always_deny():
    raw = _lua("NexusLua$Perm$Ask.smali")
    start = raw.index(".method public onClick(")
    onclick = _code_only(raw[start:raw.index(".end method", start)])

    assert "const/4 v0, -0x1" in onclick, "positive button is -1"
    assert "const/4 v1, -0x3" in onclick, "neutral button is -3"
    assert "if-eq p2, v0, :positive" in onclick
    assert "if-eq p2, v1, :neutral" in onclick

    pos = onclick.index("\n:positive")
    neu = onclick.index("\n:neutral")
    cnt = onclick.index("\n:count")

    positive = onclick[pos:neu]
    assert "const/4 v2, 0x1" in positive
    assert "iput-byte v2" in positive
    assert "const/4 v2, 0x0" in positive
    assert "iput-boolean v2" in positive

    neutral = onclick[neu:cnt]
    assert "const/4 v2, 0x1" in neutral
    assert "iput-byte v2" in neutral
    assert "iput-boolean v2" in neutral

    deny = onclick[:pos]
    assert "const/4 v2, 0x2" in deny
    assert "iput-byte v2" in deny

    assert "countDown()V" in onclick, "every click releases the script thread"


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


def test_the_perm_bridge_calls_modules_classes_by_full_descriptor():
    """The gate and the prompt hand work to LuaBridge / NexusHost with the FULL
    package descriptor. The rename era left an org.vekendian.nexus.modules path
    compiled into one of these templates: it linked fine and then threw
    NoSuchMethodError the first time a script asked for a capability."""
    for rel, needle in (
        ("NexusLua$Perm.smali",
         "invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaBridge;->policy(Ljava/lang/String;Ljava/lang/String;)I"),
        ("NexusLua$Perm.smali",
         "invoke-static {p0, p1}, Lorg/vekendian/nexus/modules/LuaBridge;->remember(Ljava/lang/String;Ljava/lang/String;)V"),
        ("NexusLua$Perm$Ask.smali",
         "invoke-static {}, Lorg/vekendian/nexus/modules/NexusHost;->dialogBuilder()Landroid/app/AlertDialog$Builder;"),
        ("NexusLua$Perm$Ask.smali",
         "invoke-static {v1, v2, v3}, Lorg/vekendian/nexus/modules/LuaBridge;->permMessage(ILjava/lang/String;Ljava/lang/String;)Ljava/lang/String;"),
    ):
        assert needle in _lua(rel), rel


def test_prompt_message_uses_the_formatted_string_resource():
    java = (RES_DIR / "java/host/org/vekendian/nexus/modules/LuaBridge.java"
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
    ("/storage/emulated/0/Download/probe.lua", "modules.install"),
    ("/storage/emulated/0/Download/probe.lua", "modules"),
    ("", "*"),
    ("/storage/emulated/0/Download/probe.lua", "modules.import"),
]


def _policy_runner(tmp_path):
    """Compile PermRules.java and drive it through a small Runner."""
    javac, java = shutil.which("javac"), shutil.which("java")
    if not (javac and java):
        pytest.skip("no JDK on this machine; run build-engine.sh to compile instead")
    src = RES_DIR / "java/host/org/vekendian/nexus/modules/PermRules.java"
    assert src.is_file()
    work = tmp_path / "perm"
    work.mkdir()
    (work / "Runner.java").write_text(
        "public class Runner {\n"
        "  public static void main(String[] a) throws Exception {\n"
        "    Class<?> c = Class.forName(\"org.vekendian.nexus.modules.PermRules\");\n"
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
        "g:modules.*",
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
    assert cases[1]["keys"] == [f"s:{digest}:modules", "g:modules", "g:*"]


def test_the_import_capability_uses_the_same_four_candidates(tmp_path):
    """import/spec/invoke/source all gate on one capability and it must ride the
    exact same key order as every other capability: per-script digest first."""
    cases = _policy_runner(tmp_path)
    script, cap = _POLICY_CASES[3]
    digest = hashlib.sha1(script.encode("utf-8")).hexdigest()
    assert cases[3]["keys"] == [
        f"s:{digest}:{cap}",
        f"g:{cap}",
        "g:modules.*",
        "g:*",
    ]


def test_candidates_never_repeat(tmp_path):
    """Capabilities that are also groups ("*", "modules.*") must not emit the
    same key twice."""
    for case in _policy_runner(tmp_path):
        assert len(case["keys"]) == len(set(case["keys"])), case["keys"]
