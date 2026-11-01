"""The release profile names the release, and the tree names the release.

GameGuardian's AndroidManifest carries a stale versionName, so the reader
trusts the version_number string the app itself shows instead. A tree that
lacks that string still gets a best-effort answer from apktool's metadata.
"""

from pathlib import Path

from nexus.profile import Profile, gg_version_from_tree
from nexus.tree import detect_version

ROOT = Path(__file__).resolve().parent.parent


def test_the_profile_is_named_for_gg_101_4():
    p = Profile.load(ROOT / "profiles/gg-101.4.json")
    assert p.gg_release == "101.4"
    assert not (ROOT / "profiles/gg-499.2.json").exists()


def test_an_unknown_release_falls_back_to_the_101_4_profile():
    assert Profile.for_release("unknown").gg_release == "101.4"


def test_the_reader_uses_version_number_not_the_stale_manifest(tmp_path):
    values = tmp_path / "res/values"
    values.mkdir(parents=True)
    (values / "strings.xml").write_text(
        '<resources><string name="version_number">101.4</string></resources>',
        encoding="utf-8")
    (tmp_path / "AndroidManifest.xml").write_text(
        '<manifest android:versionName="499.2"/>', encoding="utf-8")
    assert detect_version(tmp_path) == "101.4"
    assert gg_version_from_tree(tmp_path) == "101.4"


def test_the_reader_falls_back_to_apktool_metadata(tmp_path):
    (tmp_path / "apktool.yml").write_text(
        "versionInfo:\n  versionName: 101.4\n", encoding="utf-8")
    assert detect_version(tmp_path) == "101.4"


def test_the_reader_says_unknown_without_any_version(tmp_path):
    assert detect_version(tmp_path) == "unknown"
