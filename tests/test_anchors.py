"""Anchor-engine tests.

The patcher's safety rests entirely on anchors matching exactly once: too few
means GameGuardian changed the block, too many means our anchor is ambiguous
and we would edit the wrong place. Both must raise, naming the anchor.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nexus.anchors import PatchError, replace_exact, replace_once   # noqa: E402
from nexus.ids import Ids                                          # noqa: E402
from nexus.smali import (ARRAY_ANCHOR, COUNT_ANCHOR, COUNT_NEW, REGISTERS_ANCHOR,  # noqa: E402
                         REGISTERS_NEW, SWITCH_ANCHOR, transform_smali)
from nexus.tree import LOCK_PATH                                   # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def mini():
    return (FIXTURES / "mini_r.smali").read_text(encoding="utf-8")


@pytest.fixture
def ids():
    """Lock file WITH the fixture public.xml, so GG ids resolve by name.

    transform_smali() calls ids.gg() for six GameGuardian views; loading the
    lock alone leaves tree_public empty and every call would raise.
    """
    public = (FIXTURES / "fake_public.xml").read_text(encoding="utf-8")
    return Ids.load(LOCK_PATH, public)


# ------------------------------------------------------------ replace_once ---

def test_single_occurrence_is_replaced():
    assert replace_once("a b c", "b", "B", "x") == "a B c"


def test_missing_anchor_raises():
    with pytest.raises(PatchError) as e:
        replace_once("a b c", "zzz", "B", "windowActionBar")
    assert "windowActionBar" in str(e.value)


def test_ambiguous_anchor_raises_and_reports_the_count():
    with pytest.raises(PatchError) as e:
        replace_once("a b a b", "a b", "X", "legacy rows")
    assert "found 2x" in str(e.value)
    assert "legacy rows" in str(e.value)


def test_error_message_shows_the_anchor_body():
    with pytest.raises(PatchError) as e:
        replace_once("hello", "<item name=\"x\">", "Y", "styles")
    assert 'name="x"' in str(e.value)


def test_replace_exact_checks_the_expected_count():
    assert replace_exact("a a", "a", "b", "rows", 2) == "b b"
    with pytest.raises(PatchError, match="found 2x \\(expected exactly 3x\\)"):
        replace_exact("a a", "a", "b", "rows", 3)


def test_replacement_is_not_rescanned():
    """A replacement containing the old text must not loop."""
    assert replace_once("x", "x", "xx", "t") == "xx"


# -------------------------------------------------- anchors vs the fixture ---

def test_fixture_contains_every_anchor_exactly_once(mini):
    assert mini.count(REGISTERS_ANCHOR) == 1
    assert mini.count(COUNT_ANCHOR) == 1
    assert mini.count(ARRAY_ANCHOR) == 1
    assert mini.count(SWITCH_ANCHOR) == 1


def test_gg_anchor_ids_match_the_real_names(mini, ids):
    """The anchor is literal text, but it must agree with the id resolver.

    If a future GG release renumbers, the anchor stops matching (loudly). This
    test pins the relationship for the release we support.
    """
    assert ids.gg("check") in mini
    assert ids.gg("language") in mini


def test_full_transform_consumes_every_anchor(mini, ids):
    out = transform_smali(mini, ids)
    assert REGISTERS_NEW in out
    assert COUNT_NEW in out
    for anchor in (ARRAY_ANCHOR, SWITCH_ANCHOR):
        assert anchor not in out, f"{anchor!r} should have been consumed"


def test_transformed_output_carries_resolved_ids(mini, ids):
    out = transform_smali(mini, ids)
    assert f"        {ids.gg('check')} -> :sswitch_3" in out
    assert "        0x7f050160 -> :sswitch_nexus_tab_home" in out
    assert "0x7f050162 -> :sswitch_nexus_tab_settings" in out


def test_transform_is_deterministic(mini, ids):
    assert transform_smali(mini, ids) == transform_smali(mini, ids)