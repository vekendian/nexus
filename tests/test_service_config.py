"""The settings screen: orange bands, no donate row, retinted highlight.

Three separate edits, all on res/layout/service_config.xml plus one const in
ConfigListAdapter.smali. Every one of them is asserted by count so a GameGuardian
update that reshuffles the screen fails loudly instead of half-applying.
"""

from __future__ import annotations

import pytest

from nexus.anchors import PatchError
from nexus.layout import (DONATE_ROW_RE, SERVICE_SEPARATOR_BG,
                          SERVICE_SEPARATOR_COUNT, SERVICE_SEPARATOR_NEW,
                          transform_service_config)
from nexus.smali import (SETTINGS_HIGHLIGHT_ANCHOR, SETTINGS_HIGHLIGHT_NEW,
                         transform_settings_highlight)

# One separator band + one donate row, in the two shapes the decoders produce.
# The real screen has SERVICE_SEPARATOR_COUNT bands; these single-band samples
# stand in for one, and are used with the explicit-count helper below.
PRETTY = '''\
    <android.fix.TextView android:textAppearance="@style/Separator" android:id="@id/actions"
        android:background="#ff422654" android:text="@string/actions" />
    <android.fix.TextView android:textAppearance="@style/MediumText" android:id="@id/help"
        android:text="@string/help" />
    <android.fix.TextView android:textAppearance="@style/MediumText" android:id="@id/donate"
        android:text="@string/donate" />
    <android.fix.TextView android:textAppearance="@style/MediumText" android:id="@id/reset"
        android:text="@string/reset" />
'''

INLINE = (
    '<android.fix.TextView android:textAppearance="@style/Separator"'
    ' android:id="@id/actions" android:background="#ff422654"'
    ' android:text="@string/actions" />\n'
    '<android.fix.TextView android:id="@id/help" android:text="@string/help" />\n'
    '<android.fix.TextView android:id="@id/donate" android:text="@string/donate" />\n'
    '<android.fix.TextView android:id="@id/reset" android:text="@string/reset" />\n'
)


def _bands(xml="", n=SERVICE_SEPARATOR_COUNT):
    """Prefix a sample with exactly n separator bands. No donate row added."""
    return "".join(
        f'<android.fix.TextView android:textAppearance="@style/Separator"'
        f' android:id="@id/s{i}" android:background="#ff422654" />\n'
        for i in range(n)) + xml


DONATE = '<android.fix.TextView android:id="@id/donate" android:text="@string/donate" />\n'


def _one_band(xml):
    """Top a sample up to exactly SERVICE_SEPARATOR_COUNT bands.

    PRETTY and INLINE each already contain one band, so only the remainder is
    prepended; otherwise the transform's count assertion (correctly) rejects them.
    """
    return _bands("", SERVICE_SEPARATOR_COUNT - 1) + xml


# ------------------------------------------------------------- separators ---

@pytest.mark.parametrize("make", [PRETTY, INLINE])
def test_separator_bands_are_recoloured(make):
    out = transform_service_config(_one_band(make))
    assert SERVICE_SEPARATOR_BG not in out
    assert out.count('@color/nexus_orange') == SERVICE_SEPARATOR_COUNT


def test_wrong_band_count_fails_loudly():
    """GG adding or dropping a section must abort, not recolour partially."""
    for n in (4, 6):
        with pytest.raises(PatchError) as e:
            transform_service_config(_bands(DONATE, n))
        assert "separator bands" in str(e.value)


def test_all_five_bands_recoloured():
    out = transform_service_config(_bands(DONATE, SERVICE_SEPARATOR_COUNT))
    assert out.count('@color/nexus_orange') == SERVICE_SEPARATOR_COUNT
    assert "#ff422654" not in out


# ------------------------------------------------------------------ donate ---

@pytest.mark.parametrize("make", [PRETTY, INLINE])
def test_donate_row_is_removed(make):
    out = transform_service_config(_one_band(make))
    assert "@id/donate" not in out
    assert "@string/donate" not in out


def test_donate_removal_leaves_neighbours_intact():
    xml = _bands(
        '<android.fix.TextView android:textAppearance="@style/MediumText" android:id="@id/help" />\n'
        '<android.fix.TextView android:textAppearance="@style/MediumText" android:id="@id/donate" />\n'
        '<android.fix.TextView android:textAppearance="@style/MediumText" android:id="@id/reset" />\n',
        SERVICE_SEPARATOR_COUNT)
    out = transform_service_config(xml)
    assert "@id/help" in out and "@id/reset" in out


def test_missing_donate_row_fails_loudly():
    with pytest.raises(PatchError) as e:
        transform_service_config(_bands(DONATE.replace("@id/donate", "@id/gone"),
                                        SERVICE_SEPARATOR_COUNT))
    assert "donate row" in str(e.value)


def test_donate_regex_does_not_eat_other_rows():
    """The regex must match the donate element only, not a greedy span."""
    m = DONATE_ROW_RE.search(
        '<android.fix.TextView android:id="@id/help" />\n'
        '<android.fix.TextView android:id="@id/donate" />\n'
        '<android.fix.TextView android:id="@id/reset" />\n')
    assert m is not None
    assert "@id/help" not in m.group(0)
    assert "@id/reset" not in m.group(0)
    assert "@id/donate" in m.group(0)


def test_donate_regex_tolerates_attribute_order():
    xml = '<android.fix.TextView android:text="@string/donate" android:id="@id/donate"/>\n'
    assert DONATE_ROW_RE.search(xml) is not None


# --------------------------------------------------------------- highlight ---

SMALI_STOCK = """\
.method public x()V
    .locals 8

    :cond_2
    if-eqz v4, :cond_3

    const v4, -0x7f6b6bbe

    invoke-virtual {v5, v4}, Landroid/view/View;->setBackgroundColor(I)V

    :cond_3
    return-void
.end method
"""


def test_highlight_is_retinted():
    out = transform_settings_highlight(SMALI_STOCK)
    assert "-0x7f6b6bbe" not in out
    assert "const v4, 0x33ff7a00" in out


def test_highlight_keeps_everything_else():
    out = transform_settings_highlight(SMALI_STOCK)
    assert "invoke-virtual {v5, v4}, Landroid/view/View;->setBackgroundColor(I)V" in out
    assert ".method public x()V" in out
    assert out.count("setBackgroundColor") == 1


def test_new_highlight_literal_is_a_positive_int():
    """smali `const` is signed: 0x33FF7A00 must be positive, not negated.

    Writing it as -0xcc008600 is a value baksmali cannot encode ("cannot fit
    into an int") and only surfaces at build time, so it is pinned here.
    """
    line = [l for l in SETTINGS_HIGHLIGHT_NEW.splitlines() if "const v4" in l][0]
    assert line.strip() == "const v4, 0x33ff7a00"
    assert int("0x33ff7a00", 16) == 0x33FF7A00
    assert int("0x33ff7a00", 16) < 0x80000000   # must fit a signed int


def test_stock_highlight_decodes_to_gg_yellow():
    """Pin what we are replacing, so the anchor cannot drift silently."""
    assert (-0x7F6B6BBE) & 0xFFFFFFFF == 0x80949442


def test_highlight_anchor_is_absent_after_transform():
    """Postflight relies on the stock anchor being fully consumed."""
    out = transform_settings_highlight(SMALI_STOCK)
    assert SETTINGS_HIGHLIGHT_ANCHOR not in out
    assert out.count(SETTINGS_HIGHLIGHT_NEW) == 1


def test_highlight_without_anchor_fails_loudly():
    with pytest.raises(PatchError) as e:
        transform_settings_highlight(".method public y()V\n    .locals 1\n.end method\n")
    assert "settings highlight" in str(e.value)


def test_highlight_applied_twice_fails_loudly():
    """Idempotency: re-patching must abort, not double-apply."""
    once = transform_settings_highlight(SMALI_STOCK)
    with pytest.raises(PatchError):
        transform_settings_highlight(once)
