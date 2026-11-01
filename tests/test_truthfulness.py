"""The UI must say what it does.

Every rule in this file is a promise the app makes to the user, and each one
is cheap to break by accident: a renamed string, a swapped colour, a moved
check. They live together because they are the same rule from four sides --
the label, the scope, the colour and the check.

The failures these catch are the ones no screenshot review would find: a
button that stops everything but says "Stop modules", a selected option whose
label points at the other one, a postflight that crashes instead of reporting.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexus.checks import postflight, preflight
from nexus.ids import Ids
from nexus.tree import RES_DIR

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "nexus_ids.json"
STRINGS = RES_DIR / "res/values/nexus_strings.xml"
GG_TREE = Path("/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/"
               "Kujtnodnookc_499.2_src")


def _strings() -> dict:
    text = STRINGS.read_text(encoding="utf-8")
    return dict(re.findall(r'<string name="([^"]+)">(.*?)</string>', text, re.S))


def _java(rel: str) -> str:
    return (RES_DIR / "java" / rel).read_text(encoding="utf-8")


# ------------------------------------------------------------------ labels ---

def test_no_two_strings_say_the_same_thing():
    """Two scopes, one wording, one wrong answer.

    "Stop modules" was both the settings row that stops every module and the
    permission that lets a script stop one. The fix is not a longer label --
    it is a different label for each thing.
    """
    seen: dict[str, list[str]] = {}
    for name, value in _strings().items():
        seen.setdefault(value, []).append(name)
    dupes = {v: names for v, names in seen.items() if len(names) > 1}
    assert not dupes, f"two resources share a wording: {dupes}"


def test_the_rows_name_their_scope():
    """The permission capabilities are about ONE module, so they say one."""
    strings = _strings()
    assert strings["nexus_str_perm_install"] == "Install a module"
    assert strings["nexus_str_perm_uninstall"] == "Uninstall a module"
    assert "nexus_str_perm_run" not in strings
    assert "nexus_str_perm_stop" not in strings


def test_every_new_string_is_defined_and_known():
    """A string nobody reads is a lie waiting to happen; a string read by
    nobody is dead weight. Both are caught here."""
    from nexus.checks import RES_DIR as CHECKS_RES
    text = STRINGS.read_text(encoding="utf-8")
    for name in ("nexus_str_extension_autostart", "nexus_str_perm_default_note",
                 "nexus_str_perm_script_override"):
        assert f'name="{name}"' in text, f"{name} is not defined"
        assert name in CHECKS_RES.joinpath(
            "res/values/nexus_strings.xml").read_text(encoding="utf-8")


def test_the_lock_file_and_the_strings_agree():
    """A pinned name that no longer exists is an id pointing at nothing."""
    lock = Ids.load(LOCK)
    text = STRINGS.read_text(encoding="utf-8")
    for name in lock.nexus.get("string", {}):
        assert f'name="{name}"' in text, f"pinned string {name} is not defined"


def test_the_interface_does_not_claim_gameguardians_version():
    """Version 101.4 is announced from `<string name="version_number">` --

    the About screen, the script console prompt and the float's status line
    all resolve that element at runtime -- while the manifest only covers the
    installer-level identity. Rebranding must rewrite the element, and must
    do so by pinning the element, never the release's number, or the next GG
    release would break the swap."""
    from nexus.manifest import NEW_VERSION_NAME, set_display_version

    gg_strings = (GG_TREE / "res/values/strings.xml").read_text(encoding="utf-8")
    before = re.search(r'<string name="version_number">([^<]*)</string>',
                       gg_strings).group(1)
    assert before and before != NEW_VERSION_NAME, "stock display version moved"

    out = set_display_version(gg_strings)
    got = re.search(r'<string name="version_number">([^<]*)</string>', out).group(1)
    assert got == NEW_VERSION_NAME, "display version not rewritten"
    # Only the version element changed: the app-name swap's input survives
    # byte for byte, so rebrand's two passes compose.
    assert out.replace(
        f'<string name="version_number">{NEW_VERSION_NAME}</string>',
        f'<string name="version_number">{before}</string>') == gg_strings
    # Idempotent by value: running it over already-rewritten text is a no-op,
    # and a release that dropped the element fails loudly instead.
    assert set_display_version(out) == out
    # A release that dropped the element fails loudly instead of silently
    # skipping the rewrite (an empty-value element still gets Nexus's
    # version — the element is pinned, not its text).
    gone = gg_strings.replace(
        f'<string name="version_number">{before}</string>', "", 1)
    with pytest.raises(Exception):
        set_display_version(gone)


# ------------------------------------------------------------------ colour ---

def test_orange_means_active_and_nothing_else():
    """The one rule the whole colour system rests on.

    Orange is the accent, so it is the first thing the eye goes to. In the
    permissions dialog it therefore means exactly one thing: this option is
    the one in effect. The active option wears orange fill; the inactive
    option does not. Text colour is white on both, so the orange background
    is the only colour signal. """
    colors = (RES_DIR / "res/color/nexus_choice_text.xml").read_text(encoding="utf-8")
    items = re.findall(r"<item\b(.*?)/>", colors, re.S)
    selected = [i for i in items if 'state_selected="true"' in i]
    assert len(selected) == 1
    assert "@color/nexus_text" in selected[0]
    rest = [i for i in items if 'state_selected="true"' not in i]
    assert rest, "the selector has no default item"
    for item in rest:
        assert "@color/nexus_orange" not in item, (
            "orange on an option that is not in effect points at the wrong one")


def test_the_check_glyph_exists_and_is_ink_on_orange():
    """The state is carried by three channels, so it survives a greyscale
    screen: the fill, the check and the label."""
    check = RES_DIR / "res/drawable/nexus_ic_check.xml"
    assert check.is_file()
    assert "@color/nexus_text" in check.read_text(encoding="utf-8")


def test_the_allow_ask_pair_is_rebuilt_in_java():
    java = _java("host/org/vekendian/nexus/modules/NexusHost.java")
    assert "syncPermissionButtons(Context ui" in java
    assert "markChosen(" in java
    assert "setCompoundDrawablesRelativeWithIntrinsicBounds" in java


def test_the_permissions_dialog_says_what_it_edits():
    """The rows are the defaults for every script; a script that answered
    for itself keeps its own answer, and the row has to say so."""
    java = _java("host/org/vekendian/nexus/modules/NexusHost.java")
    assert "nexus_str_perm_default_note" in java
    assert "nexus_str_perm_script_override" in java
    assert "LuaBridge.scriptOverride(cap)" in java
    perms = _java("host/org/vekendian/nexus/modules/LuaPerms.java")
    assert "anyScriptOverride" in perms
    assert "KEY_PREFIX_SCRIPT" in perms


# ------------------------------------------------------------------- tools ---

def test_postflight_reports_a_missing_service_config_instead_of_crashing(tmp_path):
    """Postflight is a report, not a program that dies.

    The service_config checks used to read a variable that only existed when
    the file did, so a tree missing that file raised NameError on the way to
    printing the very error that would have explained it.
    """
    for rel in ("res/layout/main.xml", "res/values/public.xml",
                "res/values/styles.xml", "smali/android/ext/r.smali"):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    ids = Ids.load(LOCK)
    errors = postflight(tmp_path, ids)
    assert isinstance(errors, list)
    assert any("service_config.xml missing" in e for e in errors)


def test_preflight_reports_a_renamed_gg_view():
    """A GG view Nexus binds to must still be there.

    The names are resolved at apply time, so a renamed view used to get past
    the preflight and fail later, after the tree had been copied.
    """
    ids = Ids.load(LOCK, "")
    # Pretend GG renamed a bound view.
    ids.tree_public = {("id", "check"): "0x7f050025"}
    ids.gg_observed = {"check": "0x7f050025", "renamed_away": "0x7f050199"}
    errors = ids.audit_gg_bindings()
    assert any("renamed_away" in e for e in errors)
    assert not any("'check'" in e for e in errors)


def test_the_checks_cover_the_new_strings():
    """A string that exists but is not in the checked set can be deleted
    without a single test failing."""
    from nexus.checks import RES_DIR as CHECKS_RES
    src = (ROOT / "nexus/checks.py").read_text(encoding="utf-8")
    for name in ("nexus_str_extension_autostart", "nexus_str_perm_default_note",
                 "nexus_str_perm_script_override"):
        assert f'"{name}"' in src, f"{name} is not in the checked set"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__]))
