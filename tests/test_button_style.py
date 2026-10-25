"""The global button.

The decision is small and written everywhere against it: a button is an
orange pill with the app's label colour, on every surface GameGuardian lays
out with android.fix.Button and on every Button the theme carries. A decision
woven through eleven layouts decays quietly, so these checks hold it
together: the rule lands per layout (snippet and applied tree), the theme
carries the same surface for buttons the code builds, and the disabled state
stays inside the language.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from nexus.layout import GG_BTN_ATTRS, transform_gg_surface

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resources" / "res"

# Layouts whose buttons the rule must cover. time_jump_panel.xml is not on
# the list: transform_time_jump styles its two buttons with the float's own
# surface, a deliberate exception.
BUTTON_LAYOUTS = (
    "res/layout/dump.xml", "res/layout/execute.xml", "res/layout/main.xml",
    "res/layout/memory_range.xml",
    "res/layout/service_busy_dialog.xml", "res/layout/service_editor.xml",
    "res/layout/service_goto.xml", "res/layout/service_searcher.xml",
    "res/layout/temp_path_config.xml", "res/layout/time_jump.xml",
)

MINI = """<android.fix.LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical">
    <android.fix.Button
        android:id="@id/cancel"
        android:layout_width="fill_parent"
        android:layout_height="wrap_content"
        android:text="@string/cancel" />
    <android.fix.Button android:id="@id/more" android:text="@string/more" />
    <android.fix.TextView android:id="@id/label" android:text="keep me" />
</android.fix.LinearLayout>
"""


def test_every_button_takes_the_pill():
    out = transform_gg_surface(MINI, "service_searcher.xml")
    tags = re.findall(r"<android\.fix\.Button\b[^>]*>", out)
    assert len(tags) == 2, "both buttons must remain present"
    for tag in tags:
        missing = [a for a in GG_BTN_ATTRS if a not in tag]
        assert not missing, f"button lost {missing}"
    assert 'android:id="@id/label"' in out
    assert out.count("nexus_bg_button") == 2


def test_the_rule_is_idempotent():
    once = transform_gg_surface(MINI, "service_searcher.xml")
    twice = transform_gg_surface(once, "service_searcher.xml")
    assert twice == once


def test_multiline_buttons_are_matched_too():
    """MT Manager pretty-prints the same layouts apktool keeps inline; the
    tag spanning five lines must still be caught."""
    out = transform_gg_surface(MINI, "service_searcher.xml")
    assert out.count('android:background="@drawable/nexus_bg_button"') == 2


def test_the_disabled_state_stays_in_the_language():
    src = (RES / "drawable" / "nexus_bg_button.xml").read_text(encoding="utf-8")
    state = src.find('android:state_enabled="false"')
    off = src.find("@color/nexus_surface_alt")
    on = src.find("@color/nexus_orange")
    assert -1 not in (state, off, on), "a state or a colour is missing"
    assert state < off < on, \
        "the disabled item must come first and switch to the orange default"


def test_the_theme_carries_the_same_surface():
    styles = (RES / "values" / "nexus_styles.xml").read_text(encoding="utf-8")
    assert "android:backgroundTint" not in styles, \
        "the transparent tint would hide the orange pill again"
    assert '<item name="android:buttonStyle">@style/NexusDialogContentButton' \
        "</item>" in styles, "NexusDialog lost its buttonStyle"
    assert '<item name="android:textColor">@color/nexus_btn_text</item>' \
        in styles
    assert (RES / "color" / "nexus_btn_text.xml").is_file()


def _style_block(styles: str, name: str) -> str:
    start = styles.index(f'<style name="{name}"')
    return styles[start:styles.index("</style>", start)]


def test_the_pill_is_the_slimmer_shape():
    styles = (RES / "values" / "nexus_styles.xml").read_text(encoding="utf-8")
    block = _style_block(styles, "NexusDialogContentButton")
    for item in ('android:minHeight">35dp', 'android:minWidth">64dp',
                 'android:paddingLeft">10dp'):
        assert f'<item name="{item}</item>' in block, \
            f"missing {item} on the global pill"


def test_the_button_bar_wears_the_pill():
    """The bar's negative/positive/neutral buttons are the global orange pill
    inside a 3dp horizontal inset: the alert bar stretches its equal-weight
    buttons edge to edge, so the gap between three pills has to live in the
    drawable — layout margins from a style are ignored on these code-created
    buttons."""
    styles = (RES / "values" / "nexus_styles.xml").read_text(encoding="utf-8")
    for slot in ("buttonBarPositiveButtonStyle", "buttonBarNegativeButtonStyle",
                 "buttonBarNeutralButtonStyle"):
        assert f'android:{slot}">@style/NexusDialogBarButton<' in styles, slot
    assert '<item name="android:background">@drawable/nexus_bg_button_bar</item>' \
        in styles, "the bar style must point at the inset wrapper"
    assert '<style name="NexusDialogButton"' not in styles


# ---------------------------------------------------------------- applied ---

def _tree_root() -> Path | None:
    for base in Path("/mnt/sdcard/#Vekendian/nexus/gameguardian") \
            .glob("*/*_nexus_output"):
        if (base / "apktool.yml").is_file():
            return base
    return None


@pytest.fixture(scope="module")
def applied() -> Path:
    root = _tree_root()
    if root is None:
        pytest.skip("no applied tree on disk; run nexus.py apply first")
    return root


@pytest.mark.parametrize("rel", BUTTON_LAYOUTS)
def test_every_button_in_the_applied_tree_wears_the_pill(applied, rel):
    xml = (applied / rel).read_text(encoding="utf-8")
    tags = re.findall(r"<android\.fix\.Button\b[^>]*>", xml)
    assert tags, f"{rel}: expected buttons to audit"
    for tag in tags:
        missing = [a for a in GG_BTN_ATTRS if a not in tag]
        assert not missing, f"{rel}: button lacks {missing}"


def test_fixtheme_carries_the_button_style(applied):
    styles = (applied / "res" / "values" / "styles.xml").read_text(encoding="utf-8")
    assert '<item name="android:buttonStyle">@style/NexusDialogContentButton' \
        "</item>" in styles, "FixTheme lost the global button style"
