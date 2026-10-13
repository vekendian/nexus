"""MT Manager trees: apktool.json instead of apktool.yml.

MT Manager's decode carries the older `apktool.json` metadata file and no
`apktool.yml`, but the apktool CLI only reads the latter. The patcher has to
accept such a tree and synthesize the .yml in apktool 2.8.1's schema — the
apktool 1.x schema is rejected with "versionInfo lines not found".
"""

from __future__ import annotations

import json

import pytest

from nexus.anchors import PatchError
from nexus.tree import ensure_apktool_yml, resolve_tree

MT_JSON = {
    "apkFileName": "Kujtnoodnookc_499.2.apk",
    "isFrameworkApk": False,
    "sparseResources": True,
    "sharedLibrary": False,
    "VersionInfo": {"versionName": "499.2", "versionCode": "11929"},
    "sdkInfo": {"minSdkVersion": "21", "targetSdkVersion": "24"},
}


@pytest.fixture
def mt_tree(tmp_path):
    (tmp_path / "res").mkdir()
    (tmp_path / "smali").mkdir()
    (tmp_path / "AndroidManifest.xml").write_text(
        '<manifest package="com.scmq" />', encoding="utf-8")
    (tmp_path / "apktool.json").write_text(json.dumps(MT_JSON), encoding="utf-8")
    return tmp_path


def test_resolve_tree_accepts_apktool_json_only(mt_tree):
    assert resolve_tree(str(mt_tree)) == mt_tree.resolve()


def test_resolve_tree_rejects_a_plain_directory(tmp_path):
    plain = tmp_path / "not_a_tree"
    plain.mkdir()
    with pytest.raises(PatchError):
        resolve_tree(str(plain))


def test_resolve_tree_rejects_missing_path(tmp_path):
    with pytest.raises(PatchError):
        resolve_tree(str(tmp_path / "nope"))


def test_ensure_apktool_yml_synthesizes_281_schema(mt_tree):
    ensure_apktool_yml(mt_tree)
    yml = (mt_tree / "apktool.yml").read_text(encoding="utf-8")
    assert yml.startswith("!!brut.androlib.apk.ApkInfo")
    assert "versionInfo:" in yml
    assert "  versionCode: '11929'" in yml
    assert "  versionName: 499.2" in yml
    assert "sdkInfo:" in yml
    assert "  targetSdkVersion: '24'" in yml


def test_synthesized_yml_is_never_the_apktool_1x_schema(mt_tree):
    """apktool 2.8.1 rejects the old layout; assert we do not emit it."""
    ensure_apktool_yml(mt_tree)
    yml = (mt_tree / "apktool.yml").read_text(encoding="utf-8")
    assert "MetaInfo" not in yml
    # 2.8.1 reads versionInfo; a top-level `versionCode:` is the 1.x spelling.
    assert not any(line.startswith("versionCode:") for line in yml.splitlines())


def test_ensure_apktool_yml_leaves_apktool_trees_alone(tmp_path):
    decoded = tmp_path / "apktool"
    decoded.mkdir()
    original = "!!brut.androlib.apk.ApkInfo\nversion: 2.8.1\n"
    (decoded / "apktool.yml").write_text(original, encoding="utf-8")
    ensure_apktool_yml(decoded)
    assert (decoded / "apktool.yml").read_text(encoding="utf-8") == original


def test_ensure_apktool_yml_is_a_noop_without_metadata(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    ensure_apktool_yml(bare)
    assert not (bare / "apktool.yml").exists()
