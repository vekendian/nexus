"""The extension system: the Java engine, its generated smali, and the dex asset.

Two failure classes are being kept offline here:

  * the engine's own classes are generated, so a compile error is caught at
    build time but a *wrong* compile (a class that stopped being generated, a
    stale asset) would only show up as an empty EXTENSIONS tab on device;
  * the generated smali is audited by the same two suites as hand-written smali
    -- tests/test_invoke_arity.py for register frames, test_api_resolve.py for
    framework members. Generated code is usually safe in both respects, which is
    exactly why nothing would notice if the pipeline started emitting something
    else.

The asset dex is asserted structurally (it parses, and it declares the entry
class) rather than byte-for-byte against a hash: d8 output is not guaranteed
stable across d8 versions, so a hash would turn every toolchain bump into a
false failure. `bash build-engine.sh --check` is the byte-level check, and it
runs the real pipeline.
"""

from __future__ import annotations

import re
import struct
import subprocess
from pathlib import Path

import pytest

from nexus.checks import ENGINE_ASSET, ENGINE_SMALI
from nexus.extensions import ENGINE, RENDER_DESC, RENDER_IDS, extensions_methods as modules_methods
from nexus.tree import RES_DIR

JAVA = RES_DIR / "java"
ASSET = RES_DIR / ENGINE_ASSET
PICKER = "smali/org/vekendian/nexus/ModulePicker.smali"


def _ids():
    """The delegate's ids, without loading the lock file twice."""
    from tests.test_modules_ui import _ids as _stub
    return _stub()


# --------------------------------------------------------------- the source ---

def test_api_types_exist_with_the_expected_shape():
    """The API is a contract with extension authors; its shape is the contract."""
    ann = (JAVA / "api/org/vekendian/nexus/api/ExtensionManifest.java").read_text()
    assert "@Retention(RetentionPolicy.RUNTIME)" in ann, \
        "CLASS retention is dropped by dexing and the loader reads it reflectively"
    assert "@Target(ElementType.TYPE)" in ann
    for member in ("String name()", "String description()", "int version()",
                   "boolean autostart()", "ExtensionType type()",
                   "String[] dependsOn()", "String entry()"):
        assert member in ann, member

    api = (JAVA / "api/org/vekendian/nexus/api/ExtensionApi.java").read_text()
    for member in ("Context context()", "Activity activity()", "void log(String message)",
                   "void toast(String message)", "String extensionsDir()", "String appVersion()",
                   "void extensionsChanged()",
                   "ClassLoader getExtensionClassLoader(String extensionId)",
                   "Object loadExtension(String extensionId)"):
        assert member in api, member

    ex = (JAVA / "api/org/vekendian/nexus/api/NexusExecutor.java").read_text()
    for member in ("List<ExtensionInfo> extensions()", "String add(Context context, Uri uri)",
                   "boolean remove(String id)", "boolean run(String id)",
                   "void stop(String id)", "void runAll()", "void stopAll()",
                   "String failure()", "ClassLoader loadLibrary(String extensionId)",
                   "Object loadExtension(String extensionId)"):
        assert member in ex, member

    info = (JAVA / "api/org/vekendian/nexus/api/ExtensionInfo.java").read_text()
    for state in ("STATE_IDLE", "STATE_RUNNING", "STATE_FINISHED", "STATE_STOPPED",
                  "STATE_ERROR"):
        assert state in info, state


def test_entry_candidates_are_isolated_by_owner():
    """The host loads exactly one private registry class -- nexus.ExtensionRegistry,
    a name user code has no reason to declare. Booting the loader itself (the
    pre-registry ENTRIES) made the host fail its NexusExecutor check before any
    extension ran, and any candidate a user extension might also declare would
    shadow it under parent-first loading."""
    host = (JAVA / "host/org/vekendian/nexus/extensions/ExtensionLoader.java").read_text()
    assert 'static final String[] ENTRIES = { "nexus.ExtensionRegistry" };' in host
    jar = (JAVA / "dexexec/nexus/JarExtensionLoader.java").read_text()
    # A per-JAR loader must not fall back to a class the engine itself ships:
    # parent-first resolves that outside the user's JAR every time.
    assert "REGISTRY_ENTRIES" not in jar
    assert '"nexus.JarExtensionLoader"' not in jar
    # The isolation check runs when a manifest has declared an entry class.
    assert "type.getClassLoader() != rec.loader" in jar


def test_annotation_is_read_by_name_not_by_type():
    """The annotation lives in the host dex and the annotated class in the other
    dex. A direct annotation reference would not compile across that boundary;
    getAnnotation() plus a name comparison does, and the test pins it."""
    for rel in ("host/org/vekendian/nexus/extensions/ExtensionLoader.java",
                "dexexec/nexus/JarExtensionLoader.java"):
        src = (JAVA / rel).read_text()
        assert '"org.vekendian.nexus.api.ExtensionManifest"' in src, rel
        assert "getAnnotation(ExtensionManifest.class)" not in src, rel


def test_a_jar_needs_no_entry_class_to_load():
    """A JAR is a class library. The old fallback loaded the engine's own
    nexus.JarExtensionLoader through parent-first loading, so every entry-less
    JAR died with 'entry class resolved outside the module loader' -- and since
    nothing can name an entry class before reading a manifest, that fallback
    made the entry path dead for every JAR. The entry exists only when
    entryOverride names one; metadata failures are non-fatal either way."""
    src = (JAVA / "dexexec/nexus/JarExtensionLoader.java").read_text()
    assert "REGISTRY_ENTRIES" not in src
    assert '"nexus.JarExtensionLoader"' not in src
    assert "findAnnotatedClass" not in src and "hasAnnotation" not in src
    prepare = src[src.index("static String prepare("):src.index("/** Reads the @ExtensionManifest")]
    assert "if (rec.entryOverride != null && rec.entryOverride.length() > 0) {" in prepare
    assert 'return fail(rec, "entry class not found: " + rec.entryOverride);' in prepare
    # Parent-first loading must not resolve the entry through the engine dex.
    assert "type.getClassLoader() != rec.loader" in prepare
    # Metadata read failures are logged, not fatal: the classes work either way.
    assert "metaErr != null" in prepare and "return fail(rec, metaErr);" not in prepare
    # One loader per JAR, kept open: the old build made a second loader and then
    # closed both, leaving rec.loader null on the success path.
    assert prepare.count("new dalvik.system.DexClassLoader") == 1
    assert "closeLoader(rec);" not in prepare
    assert "rec.sharedLoader = rec.loader;" in prepare
    # A manifest-declared entry is instantiated for loadExtension()/LuaJava;
    # a library JAR has none, and either way the card gets a title.
    assert "rec.instance = type.newInstance();" in prepare
    assert "rec.name = rec.label();" in prepare
    assert "rec.description = \"\";" in prepare


def test_jar_extensions_appear_as_cards():
    """'Limited' for a JAR used to mean no Run/Stop control -- not an invisible
    card. Now no card carries a Run/Stop control at all (extensions run on
    install and end with their script), which is why the bind() signature has
    no action label left and the host's loop passes none.
    """
    reg = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    ex = reg[reg.index("public List<ExtensionInfo> extensions()"):]
    ex = ex[:ex.index("\n    @Override")]
    assert "out.add(records.get(i).info());" in ex
    assert "ExtensionType.JAR" not in ex
    host = (JAVA / "host/org/vekendian/nexus/extensions/NexusHost.java").read_text()
    loop = host[host.index("for (ExtensionInfo s : extensions)"):]
    loop = loop[:loop.index("        }\n        // The executor's card is infrastructure")]
    # Every card is Remove-only: the action control was deleted, so the loop
    # binds name/meta/desc/colour and the card — nothing else.
    assert "actionLabel" not in loop
    assert "I_ACTION" not in host
    assert "onActionClicked" not in host


def test_lua_extensions_run_through_gg_luaj_by_name():
    """A .lua extension must run in GameGuardian's own LuaJ, reached reflectively
    because the asset dex links against android.jar only. The obfuscated member
    names are pinned here so a GameGuardian reshuffle fails this test instead of
    failing on device with a bare NoSuchMethodException."""
    run = (JAVA / "dexexec/nexus/LuaExtensionLoader.java").read_text()
    for cls in ("luaj.Globals", "luaj.LuaValue", "android.ext.Script"):
        assert f'"{cls}"' in run
    # t1 installs one library; K3 installs gg.*; O3 is loadstring with a
    # (InputStream, chunkname, mode, env) frame -- GG 101.4's names.
    assert '"t1"' in run and '"K3"' in run and '"O3"' in run
    for lib in ("BaseLib", "Bit32Lib", "TableLib", "StringLib",
                "Utf8Lib", "MathLib", "OsLib"):
        assert f'"luaj.lib.{lib}"' in run
    # nexus.* comes through the same installer every GG script goes through,
    # labelled with the extension's path as the permission id.
    assert '"org.vekendian.nexus.lua.NexusLua"' in run
    assert 'getMethod("install", String.class, luaValueClass)' in run
    assert "installNexus.invoke(null, rec.path, env);" in run
    # Text chunk, from the extension's own file -- never precompiled bytecode.
    assert "invoke(env, in, rec.label(), \"t\", env);" in run
    assert "call.invoke(chunk);" in run
    # And the registry hands .lua records over rather than looking for a
    # run(ExtensionApi) method a Lua file has no way to declare.
    reg = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    assert "LuaExtensionLoader.start(host, rec);" in reg
    assert "no run(ExtensionApi) method" not in reg
    assert "rec.entry.newInstance()" not in reg


def test_an_extension_must_be_a_valid_lua_or_jar():
    loader = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    assert "isJar(f)" in loader
    assert "not a valid .jar file" in loader
    assert "not a .lua file" in loader
    assert "return fail(rec," in loader, "a rejected prepare must release its record"


def test_a_rejected_import_leaves_no_card_or_file():
    entry = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    add = entry[entry.index("public String add(Context context, Uri uri)"):]
    add = add[:add.index("\n    @Override")]
    assert "if (err != null)" in add
    assert "releaseRecord(rec);" in add
    assert "store.delete(imported);" in add
    assert "return null;" in add


def test_extension_runs_on_its_own_thread_and_stops_by_interrupt():
    """A body that runs to completion on its own thread, stopped by setting a
    flag and interrupting. run() returning is success. Since the registry stops
    looking for run(ExtensionApi), the thread itself lives in the runner -- the
    stop path and the terminal state machine stay in the registry."""
    src = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    # The stop path: ask first, then interrupt the extension's thread.
    assert "rec.stopRequested = true;" in src
    assert "t.interrupt();" in src
    # The finished/error split lives in the executor, which owns the state machine.
    assert "STATE_FINISHED" in src and "STATE_ERROR" in src
    assert "stopRequested ? ExtensionInfo.STATE_STOPPED" in src
    assert "rec.thread != Thread.currentThread()" in src
    assert "rec.thread = null;" in src
    # .lua records are sent to the runner rather than reflected on for a method
    # a Lua file has no way to declare.
    assert "LuaExtensionLoader.start(host, rec);" in src
    run = (JAVA / "dexexec/nexus/LuaExtensionLoader.java").read_text()
    assert 'new Thread(new Runnable() {\n            public void run() {' in run
    assert "t.start();" in run
    assert "rec.thread = t;" in run
    assert "rec.stopRequested = false;" in run
    assert "host.finished(rec, rec.stopRequested);" in run
    assert "host.failed(rec, e);" in run


def test_async_restore_repaints_the_tab():
    """restore() runs off the UI thread; without a callback its cards would only
    appear on the next onPostResume, after the UI had already drawn an empty tab."""
    entry = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    restore = entry[entry.index("private void restore()"):]
    restore = restore[:restore.index("// ------------------------------------------------------------- executor ---")]
    assert "changed();" in restore
    assert "a.extensionsChanged();" in entry
    host_api = (JAVA / "host/org/vekendian/nexus/extensions/ExtensionApiImpl.java").read_text()
    assert "public void extensionsChanged()" in host_api
    assert "NexusHost.rerender();" in host_api


def test_runall_does_not_restart_finished_or_crashed_extensions():
    """Otherwise every resume re-runs a completed extension, or crashes one again
    into the same crash, forever."""
    entry = (JAVA / "dexexec/nexus/ExtensionRegistry.java").read_text()
    body = entry[entry.index("public void runAll()"):]
    body = body[:body.index("\n    @Override")]
    assert "rec.state != ExtensionInfo.STATE_FINISHED" in body
    assert "rec.state != ExtensionInfo.STATE_ERROR" in body
    assert "rec.autostart" in body
    # JAR extensions don't run
    assert "rec.type == ExtensionType.JAR" in body


def test_import_copies_the_document_and_keeps_only_the_path():
    """The clean-path rule: a SAF document is not a file, so it is copied into
    files/extensions/<sanitised>.lua|.jar and only that is persisted."""
    store = (JAVA / "dexexec/nexus/ExtensionStore.java").read_text()
    assert "openInputStream(uri)" in store
    assert "KEY_ENTRIES = \"entries\"" in store
    assert "PREFS = \"nexus_extensions\"" in store
    assert "takePersistableUriPermission" in store
    assert "releasePersistableUriPermission" in store
    assert "copyUri(uri)" in store
    # And the old key is drained once, not read forever.
    assert "LEGACY_PREFS = \"nexus_modules\"" in store
    assert "LEGACY_URIS = \"uris\"" in store
    assert "legacy.edit().remove(LEGACY_URIS)" in store


# The sanitiser, actually run ----------------------------------------------

_SANITISE_CASES = [
    # (input, expected)
    ("rish_shizuku.zip", "rish_shizuku"),
    ("rish_shizuku.dex", "rish_shizuku"),
    ("Eclipse_1.0.0.apk", "Eclipse_1.0.0"),
    ("My Module v2.apk", "My_Module_v2"),
    ("a  b   c.jar", "a_b_c"),
    ("__weird__.dex", "weird"),
    ("   ", "module"),
    ("....", "module"),
    ("", "module"),
    ("/sdcard/Download/nested.file.zip", "nested.file"),
]


def _javac_and_java():
    import shutil
    return shutil.which("javac"), shutil.which("java")


def _sanitise_all(tmp_path):
    """Compile Name.java and run every case through it.

    The engine is Java and the test env has a JDK (build-engine.sh needs one), so
    the alternative would be asserting on source text -- which cannot tell a
    working sanitiser from a subtly broken one.
    """
    javac, java = _javac_and_java()
    if not (javac and java):
        pytest.skip("no JDK on this machine; run build-engine.sh to compile instead")
    src = JAVA / "dexexec/nexus/Name.java"
    assert src.is_file(), f"{src} is missing"
    work = tmp_path / "name"
    work.mkdir()
    (work / "Runner.java").write_text(
        "public class Runner {\n"
        "  public static void main(String[] a) throws Exception {\n"
        "    Class<?> c = Class.forName(\"nexus.Name\");\n"
        "    java.lang.reflect.Method m = c.getDeclaredMethod(\"sanitise\", String.class);\n"
        "    m.setAccessible(true);\n"
        "    java.io.BufferedReader in = new java.io.BufferedReader("
        "new java.io.InputStreamReader(System.in, \"UTF-8\"));\n"
        "    String line;\n"
        "    while ((line = in.readLine()) != null) {\n"
        "      System.out.println(m.invoke(null, (Object) line));\n"
        "    }\n"
        "  }\n"
        "}\n", encoding="utf-8")
    subprocess.run([javac, "-nowarn", "-proc:none", "-d", str(work),
                    str(src), str(work / "Runner.java")], check=True,
                   capture_output=True)
    stdin = "\n".join(i for i, _ in _SANITISE_CASES) + "\n"
    out = subprocess.run([java, "-cp", str(work), "Runner"],
                         input=stdin.encode("utf-8"), check=True,
                         capture_output=True)
    return out.stdout.decode("utf-8").splitlines()


def test_sanitiser_reduces_a_document_name(tmp_path):
    got = _sanitise_all(tmp_path)
    assert len(got) == len(_SANITISE_CASES), "one output per input"
    for (raw, want), actual in zip(_SANITISE_CASES, got):
        assert actual == want, f"sanitise({raw!r}) -> {actual!r}, wanted {want!r}"


def test_sanitiser_never_returns_an_empty_or_trailing_dot_name(tmp_path):
    got = _sanitise_all(tmp_path)
    for (raw, _), actual in zip(_SANITISE_CASES, got):
        assert actual, raw
        assert not actual.endswith(".") and not actual.endswith("_"), raw
        assert not actual.startswith(".") and not actual.startswith("_"), raw


# ------------------------------------------------------- what gets generated ---

@pytest.mark.parametrize("rel", ENGINE_SMALI)
def test_engine_class_is_present(rel):
    assert (RES_DIR / rel).is_file(), f"{rel} is missing — run build-engine.sh"


def test_the_asset_dex_is_a_dex_with_the_registry_entry_class():
    """Structural, not byte-for-byte: d8 output is not stable across d8
    versions, so a hash here would fail on every toolchain bump."""
    assert ASSET.is_file(), "resources/res/raw/ydw_nexus_dexexec is missing"
    data = ASSET.read_bytes()
    assert data[:4] == b"dex\n", "the asset must be a raw dex, not an archive"

    def u32(o):
        return struct.unpack_from("<I", data, o)[0]

    def uleb(o):
        r = s = 0
        while True:
            b = data[o]
            o += 1
            r |= (b & 0x7F) << s
            s += 7
            if not b & 0x80:
                return r, o

    n_str, off_str = u32(0x38), u32(0x3C)
    n_type, off_type = u32(0x40), u32(0x44)
    n_cls, off_cls = u32(0x60), u32(0x64)

    def s(i):
        o = u32(off_str + 4 * i)
        _, o = uleb(o)
        return data[o:data.index(b"\x00", o)].decode("utf-8", "replace")

    def t(i):
        return s(u32(off_type + 4 * i))

    classes = {t(struct.unpack_from("<I", data, off_cls + 32 * i)[0])
               for i in range(n_cls)}
    strings = {s(i) for i in range(n_str)}
    assert "Lnexus/ExtensionRegistry;" in classes, "the registry's entry class is missing"
    assert "Lorg/vekendian/nexus/api/ExtensionApi;" in strings, \
        "the registry must reference the API, not copy it"
    # The API classes must NOT be in the asset: they are in classes.dex already,
    # and a second copy in a child loader is a class that is not the same type.
    assert not any(c.startswith("Lorg/vekendian/nexus/") for c in classes), \
        "the asset dex must not duplicate host classes"


def test_the_delegate_descriptor_matches_the_generated_method():
    """The one check that would catch a signature drifting between the template
    and the Java.

    r.smali calls render(Landroid/app/Activity;IIIIIIIIIIIIIII)V by descriptor. If
    someone adds a view id to render() in Java and forgets the smali, the call
    does not fail to assemble and does not fail preflight -- it fails at runtime
    with NoSuchMethodError, on the first draw of the tab.
    """
    host = (RES_DIR / "smali/org/vekendian/nexus/extensions/NexusHost.smali").read_text()
    declared = {name: desc for name, desc in re.findall(
        r"^\.method [^\n]*?(\w+)\((\S*?)\)\S*$", host, re.M)}
    for method in ("pick", "boot", "render", "park", "powerOn", "powerOff"):
        assert method in declared, f"{method} is not declared in the generated host"

    want = re.search(r"->render\((\S*?)\)V", modules_methods(_ids())).group(1)
    assert want == declared["render"], (
        "extensions.py and NexusHost.render disagree:\n"
        f"  delegate  ({want})\n  generated  ({declared['render']})")
    assert f"({want})V" == RENDER_DESC, \
        "extensions_methods() must emit RENDER_DESC, built from RENDER_IDS"

    # Same for the one call that takes a scalar.
    drain = modules_methods(_ids())
    boot = re.search(r"->boot\((\S*?)\)V", drain).group(1)
    assert boot == declared["boot"], f"boot: {boot} vs {declared['boot']}"


def test_the_engine_never_loads_classes_it_should_merely_ask_for():
    """ExtensionRegistry is loaded BY the host. If the asset dex also contained a
    ExtensionLoader, there would be two of them and the wrong one could win.

    The engine's own loader class names carry the "ExtensionLoader" substring
    (the JAR loader, the Lua runner), so the check strips those known-good names
    and asserts nothing bare remains — a bare occurrence would be the host's
    loader class leaking into the asset.
    """
    data = ASSET.read_bytes().decode("latin-1")
    stripped = data.replace("JarExtensionLoader", "").replace("LuaExtensionLoader", "")
    assert "ExtensionLoader" not in stripped


def test_generated_smali_delegates_to_the_engine_and_to_nothing_else():
    host = (RES_DIR / "smali/org/vekendian/nexus/extensions/NexusHost.smali").read_text()
    assert ".class public final Lorg/vekendian/nexus/extensions/NexusHost;" in host
    for method in ("pick", "boot", "render", "park", "powerOn", "powerOff"):
        assert re.search(rf"^\.method [^\n]*\b{method}\(", host, re.M), \
            f"NexusHost->{method} is missing from the generated smali"

    # The classloader is created by the host's loader helper, once, for the
    # executor asset. Exactly one such call site exists in the whole engine.
    loader = (RES_DIR / "smali/org/vekendian/nexus/extensions/ExtensionLoader.smali").read_text()
    assert "Ldalvik/system/DexClassLoader;-><init>" in loader
    assert "ExtensionLoader;->load(Landroid/content/Context;" in host, \
        "NexusHost must go through ExtensionLoader.load, not build its own"
    for rel in ENGINE_SMALI:
        text = (RES_DIR / rel).read_text()
        if rel.endswith(("ExtensionLoader.smali",)):
            continue
        assert "Ldalvik/system/DexClassLoader;" not in text, \
            f"{rel} creates a DexClassLoader; only ExtensionLoader may"