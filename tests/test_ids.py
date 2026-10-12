"""ID resolver tests.

Covers the three behaviours that matter: pinned Nexus ids come back exactly as
written in the lock file, GameGuardian ids resolve by NAME, and a name that
disappears is a hard error rather than a silent fallback.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nexus.anchors import PatchError          # noqa: E402
from nexus.ids import Ids, parse_public       # noqa: E402
from nexus.tree import LOCK_PATH              # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def public():
    return (FIXTURES / "fake_public.xml").read_text(encoding="utf-8")


@pytest.fixture
def ids(public):
    return Ids.load(LOCK_PATH, public)


def test_lock_file_loads():
    data = Ids.load(LOCK_PATH)
    assert data.nexus["id"]["nexus_tab_home"] == "0x7f050160"
    assert data.nexus["drawable"]["nexus_bg_pill"] == "0x7f040070"


def test_parse_public_indexes_by_type_and_name(public):
    seen = parse_public(public)
    assert seen[("id", "check")] == "0x7f050025"
    assert ("string", "app_name") in seen


def test_pinned_ids_are_returned_lowercase_eight_digit(ids):
    assert ids.hex("nexus_panel_home") == "0x7f050163"
    assert ids.hex("nexus_env_root") == "0x7f05017c"
    assert ids.upper_hex("nexus_panel_home") == "0x7F050163"


def test_hex_and_smali_are_the_same_accessor(ids):
    assert ids.smali("nexus_power_card") == ids.hex("nexus_power_card")


def test_unknown_pinned_name_is_an_error(ids):
    with pytest.raises(PatchError, match="no pinned Nexus ID"):
        ids.hex("nexus_does_not_exist")


def test_gg_ids_resolve_by_name(ids):
    """The whole point: GG ids come from public.xml, not a hardcoded literal."""
    assert ids.gg("check") == "0x7f050025"
    assert ids.gg("btn_stop_service") == "0x7f050016"


def test_missing_gg_name_is_a_hard_error(ids):
    with pytest.raises(PatchError, match="not found in the tree"):
        ids.gg("btn_that_gg_removed")


def test_drift_is_reported_but_not_an_error(public):
    """A renamed/moved GG id must not fail the patch -- only be surfaced."""
    moved = public.replace('name="check" id="0x7f050025"',
                           'name="check" id="0x7f050099"')
    ids = Ids.load(LOCK_PATH, moved)
    assert ids.gg("check") == "0x7f050099"
    assert ("check", "0x7f050099", "0x7f050025") in ids.drift()


def test_no_drift_when_unchanged(ids):
    assert ids.drift() == []


def test_collision_detection_finds_an_existing_name(public):
    clashing = public.replace('name="check" id="0x7f050025"',
                              'name="nexus_tab_home" id="0x7f040099"')
    errs = Ids.load(LOCK_PATH, clashing).audit_collisions(clashing)
    assert any("nexus_tab_home" in e for e in errs)


def test_collision_detection_finds_a_taken_id(public):
    clashing = public.replace('id="0x7f050158"', 'id="0x7f050160"')
    errs = Ids.load(LOCK_PATH, clashing).audit_collisions(clashing)
    assert any("0x7f050160" in e for e in errs)


def test_clean_fixture_reports_no_collisions(ids, public):
    assert ids.audit_collisions(public) == []


def test_audit_gg_bindings_passes_on_the_fixture(ids):
    assert ids.audit_gg_bindings() == []


def test_audit_gg_bindings_flags_a_missing_view(public):
    stripped = "\n".join(l for l in public.splitlines() if 'name="help"' not in l)
    errs = Ids.load(LOCK_PATH, stripped).audit_gg_bindings()
    assert any("help" in e for e in errs)


def test_public_id_lines_emits_all_three_kinds(ids):
    lines = ids.public_id_lines().splitlines()
    assert len(lines) == len(ids.pinned_table())
    assert any('type="id" name="nexus_tab_home"' in l for l in lines)
    assert any('type="drawable" name="nexus_bg_pill"' in l for l in lines)
    assert any('type="string" name="nexus_str_yes"' in l for l in lines)


def test_pinned_ids_are_unique_across_kinds(ids):
    values = [h.lower() for _, _, h in ids.pinned_table()]
    assert len(values) == len(set(values)), "pinned ids must not alias"