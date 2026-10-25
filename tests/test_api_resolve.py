"""Every framework method the injected smali calls must actually exist.

Two runtime-only failures have shipped from this patcher. Neither is visible to
`apktool b`, and the first was not caught by an arity check either:

    java.lang.VerifyError: invalid argument count (7) exceeds outsSize (6)
        -> register count wrong (tests/test_invoke_arity.py covers this)

    java.lang.NoSuchMethodError: No direct method
        <init>(Landroid/content/Context;Ljava/lang/Class;)Landroid/content/Intent;
        -> the descriptor does not name a real member

That second one was a genuine mistake: a constructor's descriptor ends in `V`,
not in the class type. It had been written as `...Landroid/content/Intent;`.

Members are resolved against framework/android-34.jar by parsing class files'
constant pools, which yields real dex descriptors without invoking javap once
per class.

Limits, stated plainly:

  * Framework classes only. Calls into GameGuardian's obfuscated classes are
    skipped -- those are covered by the arity audit and by running the app.
  * android.jar is API 34; the device is API 36. A member present in 34 but
    gone in 36 passes here and can still fail on device.
"""

from __future__ import annotations

import pytest

from nexus.apicheck import ANDROID_JAR, declared_methods, unresolved, _fmt
from nexus.tree import RES_DIR

# The extension engine is generated smali, audited for the same reason as
# hand-written: apicheck resolves the framework members it calls, which is the
# one failure mode a compiler cannot catch (a member that does not exist on the
# device, or never existed).
APPLIED = [
    "smali/android/ext/r.smali",
    "smali/android/ext/f.smali",
    "smali/android/ext/ConfigListAdapter.smali",
    "smali/org/vekendian/nexus/ModulePicker.smali",
    "smali/org/vekendian/nexus/api/ExtensionApi.smali",
    "smali/org/vekendian/nexus/api/ExtensionManifest.smali",
    "smali/org/vekendian/nexus/api/ExtensionInfo.smali",
    "smali/org/vekendian/nexus/api/ExtensionType.smali",
    "smali/org/vekendian/nexus/api/NexusExecutor.smali",
    "smali/org/vekendian/nexus/extensions/NexusHost.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionApiImpl.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionCards.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionLoader.smali",
]
SHIPPED = [
    "smali/org/vekendian/nexus/ModulePicker.smali",
    "smali/org/vekendian/nexus/extensions/NexusHost.smali",
    "smali/org/vekendian/nexus/extensions/ExtensionLoader.smali",
]


@pytest.fixture(scope="module", autouse=True)
def jar_available():
    if not ANDROID_JAR.is_file():
        pytest.skip(f"{ANDROID_JAR} not present")


def _tree_root():
    from pathlib import Path
    for base in Path("/mnt/sdcard/#Vekendian/nexus/gameguardian").glob("*/*_nexus_output"):
        if (base / "apktool.yml").is_file():
            return base
    return None


# ------------------------------------------------------- the parser itself ---

def test_jar_parses():
    """A broken constant-pool reader would report every call as missing."""
    d = declared_methods("Landroid/content/Intent;")
    assert d is not None and len(d) > 100, "Intent should expose many members"


@pytest.mark.parametrize("name,desc", [
    ("setClassName", "(Landroid/content/Context;Ljava/lang/String;)Landroid/content/Intent;"),
    ("setType", "(Ljava/lang/String;)Landroid/content/Intent;"),
    ("addCategory", "(Ljava/lang/String;)Landroid/content/Intent;"),
    ("putExtra", "(Ljava/lang/String;[Ljava/lang/String;)Landroid/content/Intent;"),
    ("getData", "()Landroid/net/Uri;"),
    ("startActivityForResult", "(Landroid/content/Intent;I)V"),
    ("setVisibility", "(I)V"),
    ("query", "(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;"
              "[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;"),
])
def test_known_members_resolve(name, desc):
    for cls in ("Landroid/content/Intent;", "Landroid/app/Activity;",
                "Landroid/view/View;", "Landroid/content/ContentResolver;"):
        if (name, desc) in (declared_methods(cls) or set()):
            return
    pytest.fail(f"{name}{desc} should exist in some framework class")


def test_constructors_end_in_v_not_the_class_type():
    """The descriptor that caused the NoSuchMethodError, pinned both ways."""
    d = declared_methods("Landroid/content/Intent;")
    assert ("<init>", "(Landroid/content/Context;Ljava/lang/Class;)V") in d, \
        "Intent(Context, Class) exists -- but its descriptor returns void"
    assert ("<init>", "(Landroid/content/Context;Ljava/lang/Class;)Landroid/content/Intent;") not in d, \
        "no constructor may be declared as returning the class type"


def test_missing_class_and_member_are_both_reported():
    src = ('.method private x()V\n    .registers 4\n'
           "    invoke-virtual {v0, v1}, Landroid/content/Intent;"
           "->noSuchMethodHere(Ljava/lang/String;)V\n"
           "    invoke-virtual {v0, v1}, Landroid/content/NoSuchClassHere;"
           "->doThing()V\n"
           "    return-void\n.end method\n")
    problems = unresolved(src)
    assert any("noSuchMethodHere" in w for _m, _l, w in problems)
    # The unknown class is simply not a framework class, so it is skipped.
    assert all("NoSuchClassHere" not in w for _m, _l, w in problems)


# ------------------------------------------------------------- the smali ---

@pytest.mark.parametrize("rel", SHIPPED)
def test_shipped_classes_resolve(rel):
    src = (RES_DIR / rel).read_text(encoding="utf-8")
    assert unresolved(src) == [], _fmt(unresolved(src), rel)


@pytest.mark.parametrize("rel", APPLIED)
def test_patched_smali_resolves(rel):
    root = _tree_root()
    if root is None:
        pytest.skip("no applied tree on disk")
    src = (root / rel).read_text(encoding="utf-8")
    assert unresolved(src) == [], _fmt(unresolved(src), rel)


def test_engine_avoids_the_constructor_that_failed():
    """Guard the guard: nothing may reintroduce Intent(Context, Class).

    The engine builds the proxy's Intent and uses setClassName(Context, String),
    not the Intent(Context, Class) constructor whose descriptor was written with
    a class return type and blew up with "No direct method <init>" at runtime.
    The call moved from smali into Java when the engine was written, so the guard
    moves with it.
    """
    from nexus.tree import RES_DIR

    engine = (RES_DIR / "smali/org/vekendian/nexus/extensions/NexusHost.smali").read_text()
    assert "setClassName" in engine
    # Narrow to the Intent constructors: java.lang.Class itself is legitimately
    # used by the engine (getClassLoader, and the Class[] the reflective
    # onLoad lookup takes). It was only ever forbidden as the second argument of
    # an Intent constructor.
    assert "Landroid/content/Context;Ljava/lang/Class;" not in engine
    assert "Ljava/lang/Class;)Landroid/content/Intent;" not in engine
