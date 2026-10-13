"""apply writes a patched COPY; the source tree must never be modified."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nexus.anchors import PatchError                              # noqa: E402
from nexus.cli import main                                        # noqa: E402
from nexus.tree import default_output, make_output                # noqa: E402


@pytest.fixture
def src(tmp_path):
    t = tmp_path / "gg_src"
    (t / "res").mkdir(parents=True)
    (t / "apktool.yml").write_text("x: 1\n", encoding="utf-8")
    (t / "res" / "a.xml").write_text("<a/>", encoding="utf-8")
    return t


def test_default_output_is_a_sibling(src):
    assert default_output(src) == src.parent / "gg_src_nexus_output"


def test_make_output_copies_and_leaves_source_alone(src):
    out = default_output(src)
    make_output(src, out)
    assert (out / "res" / "a.xml").read_text(encoding="utf-8") == "<a/>"
    (out / "res" / "a.xml").write_text("changed", encoding="utf-8")
    assert (src / "res" / "a.xml").read_text(encoding="utf-8") == "<a/>"


def test_existing_output_needs_force(src):
    out = default_output(src)
    make_output(src, out)
    with pytest.raises(PatchError):
        make_output(src, out)
    (out / "stale.txt").write_text("old", encoding="utf-8")
    make_output(src, out, force=True)
    assert not (out / "stale.txt").exists()


def test_force_refuses_to_delete_a_non_tree(src, tmp_path):
    other = tmp_path / "precious"
    other.mkdir()
    (other / "file.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(PatchError):
        make_output(src, other, force=True)
    assert (other / "file.txt").exists()


@pytest.mark.parametrize("where", ["same", "inside", "parent"])
def test_output_may_not_overlap_source(src, where):
    out = {"same": src, "inside": src / "out", "parent": src.parent}[where]
    with pytest.raises(PatchError):
        make_output(src, out, force=True)
    assert (src / "apktool.yml").is_file()


def test_failed_preflight_writes_no_output(src):
    # fake tree lacks the GG files, so apply must fail and create nothing
    assert main(["apply", "--src", str(src)]) != 0
    assert not default_output(src).exists()
