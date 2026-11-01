"""The rebrand follows the package the tree declares.

GameGuardian randomizes its package per build, so a literal "com.scmq" in the
patcher only works on the release it was copied from. AndroidManifest.xml is
the source; apktool copies the same value into its metadata.
"""

import pytest

from nexus.anchors import PatchError
from nexus.manifest import rebrand
from nexus.resids import audit_rebrand_complete
from nexus.tree import detect_package

MANIFEST = """<manifest package="com.r4nd0m">
    <application android:label="Kujtnodnookc">
        <activity android:name="com.r4nd0m.MainActivity" android:label="Game">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LEANBACK_LAUNCHER"/>
            </intent-filter>
        </activity>
        <activity android:name="com.r4nd0m.ActivityMain" android:label="Game"
                  android:icon="@mipmap/ic_hw_48dp">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LEANBACK_LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

SMALI = """\
.class public Lcom/r4nd0m/Application;
.super Landroid/app/Application;

.method static constructor <clinit>()V
    const-string v0, "Lcom/r4nd0m;"
    return-void
.end method
"""


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "smali/com/r4nd0m").mkdir(parents=True)
    (tmp_path / "smali/com/r4nd0m/Application.smali").write_text(
        SMALI, encoding="utf-8")
    (tmp_path / "res/values").mkdir(parents=True)
    (tmp_path / "res/values/strings.xml").write_text(
        '<resources><string name="app_name">GameGuardian</string>'
        '<string name="version_number">101.4</string></resources>',
        encoding="utf-8")
    (tmp_path / "AndroidManifest.xml").write_text(MANIFEST, encoding="utf-8")
    (tmp_path / "apktool.yml").write_text(
        "apkFileName: random.apk\nversionInfo:\n"
        "  versionCode: '11929'\n  versionName: 499.2\n", encoding="utf-8")
    return tmp_path


def test_the_package_is_read_from_the_manifest(tree):
    assert detect_package(tree) == "com.r4nd0m"


def test_the_package_falls_back_to_apktool_metadata(tmp_path):
    (tmp_path / "apktool.yml").write_text(
        "packageInfo:\n  renameManifestPackage: com.fallback\n",
        encoding="utf-8")
    assert detect_package(tmp_path) == "com.fallback"


def test_a_tree_without_a_package_fails_loudly(tmp_path):
    with pytest.raises(PatchError):
        detect_package(tmp_path)


def test_rebrand_moves_the_declared_package_not_a_literal(tree):
    rebrand(tree)
    assert not (tree / "smali/com/r4nd0m").exists()
    smali = (tree / "smali/org/vekendian/nexus/Application.smali").read_text(
        encoding="utf-8")
    assert "Lorg/vekendian/nexus/Application;" in smali
    assert "Lcom/r4nd0m" not in smali
    manifest = (tree / "AndroidManifest.xml").read_text(encoding="utf-8")
    assert 'package="org.vekendian.nexus"' in manifest
    assert "com.r4nd0m" not in manifest
    assert "ModulePicker" in manifest


def test_the_leftover_audit_uses_the_declared_package(tmp_path):
    (tmp_path / "smali").mkdir()
    (tmp_path / "smali/X.smali").write_text(
        "Lcom/r4nd0m/X;", encoding="utf-8")
    assert audit_rebrand_complete(tmp_path, "com.r4nd0m")
    assert not audit_rebrand_complete(tmp_path, "com.other")
    assert not audit_rebrand_complete(tmp_path, None)
