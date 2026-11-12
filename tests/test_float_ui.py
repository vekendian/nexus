"""The floating interface: the icon, the speed controls and the time-jump panel.

The float is the one part of Nexus a user sees over another app. It is
GameGuardian's own layout, so Nexus restyles it in place: a plate under the
icon, Nexus chrome on the speed badge, Nexus tints on the scan progress bars,
and a name on every control the float owns.

What these cannot assert: that the plate looks right over a bright game
frame, or that a screen reader announces the controls. That needs a device.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nexus.anchors import PatchError
from nexus.layout import transform_hot_point, transform_time_jump
from nexus.tree import RES_DIR

ROOT = Path(__file__).resolve().parent.parent

GG_TREE = Path("/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/"
               "Kujtnodnookc_499.2_src")

# The two shapes the decoders produce for the same GG layout: MT Manager
# pretty-prints one attribute per line, apktool collapses them onto the
# element's line.
PRETTY = '''\
<?xml version="1.0" encoding="utf-8"?>
<android.ext.HotPoint
    android:orientation="vertical"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    xmlns:android="http://schemas.android.com/apk/res/android">
    <android.fix.LinearLayout
        android:layout_gravity="center"
        android:orientation="horizontal"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content">
        <android.fix.ImageButtonView
            android:gravity="center"
            android:id="@id/speed_dec"
            android:padding="0.0dip"
            android:layout_width="48.0dip"
            android:layout_height="48.0dip"
            android:layout_marginRight="10.0dip"
            android:src="@drawable/ic_rewind_white_48dp" />
        <android.ext.HotFrame
            android:id="@id/hot_frame"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:minWidth="24.0dip"
            android:minHeight="24.0dip">
            <android.fix.ImageView
                android:id="@id/hot_point_icon"
                android:layout_width="48.0dip"
                android:layout_height="48.0dip"
                android:src="@drawable/ic_gg_48dp"
                android:minWidth="24.0dip"
                android:minHeight="24.0dip" />
            <android.fix.LinearLayout
                android:orientation="vertical"
                android:id="@id/progress_layout"
                android:layout_width="fill_parent"
                android:layout_height="fill_parent"
                android:minWidth="24.0dip"
                android:minHeight="24.0dip">
                <android.fix.TextView
                    android:textSize="10.0dip"
                    android:gravity="center"
                    android:id="@id/progress_bar_text"
                    android:background="#80000000"
                    android:padding="0.0dip"
                    android:layout_width="fill_parent"
                    android:layout_height="0.0dip"
                    android:minWidth="24.0dip"
                    android:minHeight="10.0dip"
                    android:text="30.9%"
                    android:layout_weight="10.0" />
                <android.fix.ProgressBar
                    android:id="@id/progress_bar"
                    android:padding="0.0dip"
                    android:layout_width="fill_parent"
                    android:layout_height="0.0dip"
                    android:max="100"
                    android:progress="30"
                    android:indeterminate="false"
                    android:minWidth="24.0dip"
                    android:minHeight="0.0dip"
                    android:layout_weight="7.0"
                    style="?android:progressBarStyleHorizontal" />
                <android.fix.ProgressBar
                    android:id="@id/progress_bar_stage"
                    android:padding="0.0dip"
                    android:layout_width="fill_parent"
                    android:layout_height="0.0dip"
                    android:max="100"
                    android:progress="60"
                    android:indeterminate="false"
                    android:minWidth="24.0dip"
                    android:minHeight="0.0dip"
                    android:layout_weight="7.0"
                    style="?android:progressBarStyleHorizontal" />
            </android.fix.LinearLayout>
        </android.ext.HotFrame>
        <android.fix.ImageButtonView
            android:gravity="center"
            android:id="@id/speed_inc"
            android:padding="0.0dip"
            android:layout_width="48.0dip"
            android:layout_height="48.0dip"
            android:layout_marginLeft="10.0dip"
            android:src="@drawable/ic_fast_forward_white_48dp" />
    </android.fix.LinearLayout>
    <android.fix.TextView
        android:textAppearance="@style/MediumText"
        android:gravity="center"
        android:layout_gravity="center"
        android:id="@id/speed_text"
        android:background="@drawable/txt_bg"
        android:paddingLeft="5.0dip"
        android:paddingRight="5.0dip"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="9 000 000 000" />
</android.ext.HotPoint>
'''

INLINE = (
    '<android.ext.HotPoint android:orientation="vertical"'
    ' android:layout_width="wrap_content" android:layout_height="wrap_content"\n'
    '  xmlns:android="http://schemas.android.com/apk/res/android">\n'
    '    <android.fix.LinearLayout android:layout_gravity="center"'
    ' android:orientation="horizontal" android:layout_width="wrap_content"'
    ' android:layout_height="wrap_content">\n'
    '        <android.fix.ImageButtonView android:gravity="center"'
    ' android:id="@id/speed_dec" android:padding="0.0dip"'
    ' android:layout_width="48.0dip" android:layout_height="48.0dip"'
    ' android:layout_marginRight="10.0dip"'
    ' android:src="@drawable/ic_rewind_white_48dp" />\n'
    '        <android.ext.HotFrame android:id="@id/hot_frame"'
    ' android:layout_width="wrap_content" android:layout_height="wrap_content"'
    ' android:minWidth="24.0dip" android:minHeight="24.0dip">\n'
    '            <android.fix.ImageView android:id="@id/hot_point_icon"'
    ' android:layout_width="48.0dip" android:layout_height="48.0dip"'
    ' android:src="@drawable/ic_gg_48dp" android:minWidth="24.0dip"'
    ' android:minHeight="24.0dip" />\n'
    '            <android.fix.LinearLayout android:orientation="vertical"'
    ' android:id="@id/progress_layout" android:layout_width="fill_parent"'
    ' android:layout_height="fill_parent" android:minWidth="24.0dip"'
    ' android:minHeight="24.0dip">\n'
    '                <android.fix.TextView android:textSize="10.0dip"'
    ' android:gravity="center" android:id="@id/progress_bar_text"'
    ' android:background="#80000000" android:padding="0.0dip"'
    ' android:layout_width="fill_parent" android:layout_height="0.0dip"'
    ' android:minWidth="24.0dip" android:minHeight="10.0dip"'
    ' android:text="30.9%" android:layout_weight="10.0" />\n'
    '                <android.fix.ProgressBar android:id="@id/progress_bar"'
    ' android:padding="0.0dip" android:layout_width="fill_parent"'
    ' android:layout_height="0.0dip" android:max="100" android:progress="30"'
    ' android:indeterminate="false" android:minWidth="24.0dip"'
    ' android:minHeight="0.0dip" android:layout_weight="7.0"'
    ' style="?android:progressBarStyleHorizontal" />\n'
    '                <android.fix.ProgressBar'
    ' android:id="@id/progress_bar_stage" android:padding="0.0dip"'
    ' android:layout_width="fill_parent" android:layout_height="0.0dip"'
    ' android:max="100" android:progress="60" android:indeterminate="false"'
    ' android:minWidth="24.0dip" android:minHeight="0.0dip"'
    ' android:layout_weight="7.0"'
    ' style="?android:progressBarStyleHorizontal" />\n'
    '            </android.fix.LinearLayout>\n'
    '        </android.ext.HotFrame>\n'
    '        <android.fix.ImageButtonView android:gravity="center"'
    ' android:id="@id/speed_inc" android:padding="0.0dip"'
    ' android:layout_width="48.0dip" android:layout_height="48.0dip"'
    ' android:layout_marginLeft="10.0dip"'
    ' android:src="@drawable/ic_fast_forward_white_48dp" />\n'
    '    </android.fix.LinearLayout>\n'
    '    <android.fix.TextView android:textAppearance="@style/MediumText"'
    ' android:gravity="center" android:layout_gravity="center"'
    ' android:id="@id/speed_text" android:background="@drawable/txt_bg"'
    ' android:paddingLeft="5.0dip" android:paddingRight="5.0dip"'
    ' android:layout_width="wrap_content" android:layout_height="wrap_content"'
    ' android:text="9 000 000 000" />\n'
    '</android.ext.HotPoint>\n'
)

TIME_JUMP_PRETTY = '''\
<?xml version="1.0" encoding="utf-8"?>
<android.ext.TimeJumpPanel
    android:orientation="horizontal"
    android:background="@drawable/txt_bg"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    xmlns:android="http://schemas.android.com/apk/res/android">
    <android.fix.Button
        android:textSize="@dimen/button_text_size"
        android:id="@id/time_jump_last"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:minWidth="24.0dip"
        android:text="1"
        android:textAllCaps="false" />
    <android.fix.Button
        android:textSize="@dimen/button_text_size"
        android:id="@id/time_jump"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:minWidth="24.0dip"
        android:text="..."
        android:textAllCaps="false" />
</android.ext.TimeJumpPanel>
'''

TIME_JUMP_INLINE = (
    '<android.ext.TimeJumpPanel android:orientation="horizontal"'
    ' android:background="@drawable/txt_bg" android:layout_width="wrap_content"'
    ' android:layout_height="wrap_content"\n'
    '  xmlns:android="http://schemas.android.com/apk/res/android">\n'
    '    <android.fix.Button android:textSize="@dimen/button_text_size"'
    ' android:id="@id/time_jump_last" android:layout_width="wrap_content"'
    ' android:layout_height="wrap_content" android:minWidth="24.0dip"'
    ' android:text="1" android:textAllCaps="false" />\n'
    '    <android.fix.Button android:textSize="@dimen/button_text_size"'
    ' android:id="@id/time_jump" android:layout_width="wrap_content"'
    ' android:layout_height="wrap_content" android:minWidth="24.0dip"'
    ' android:text="..." android:textAllCaps="false" />\n'
    '</android.ext.TimeJumpPanel>\n'
)


@pytest.mark.parametrize("sample", [PRETTY, INLINE])
def test_hot_point_nexus_chrome(sample):
    out = transform_hot_point(sample)
    # the name goes on hot_frame, the view GG puts the click listener on;
    # the icon itself is decorative and says so
    assert 'android:contentDescription="@string/nexus_str_float_icon"' in out
    assert 'android:importantForAccessibility="no"' in out
    # hot_frame is the icon's plate: a home-screen-style surface card so the
    # float reads as one flat surface instead of a bare icon on the game
    assert 'android:background="@drawable/nexus_bg_float_badge"' in out
    # the speed controls get names: they are the only interactive parts
    assert 'android:contentDescription="@string/nexus_str_float_speed_dec"' in out
    assert 'android:contentDescription="@string/nexus_str_float_speed_inc"' in out
    # GG's purple badge and flat black scrim are gone
    assert 'android:background="@drawable/txt_bg"' not in out
    assert 'android:background="#80000000"' not in out
    # the speed buttons get a surface: a white arrow on a bright game is a
    # white arrow on white
    assert 'android:background="@drawable/nexus_bg_float_button"' in out
    assert 'android:padding="12.0dp"' in out
    # the readout is a disc over the icon, not a black rectangle
    assert 'android:background="@drawable/nexus_bg_float_readout"' in out
    assert 'android:background="@null"' in out
    # the bars are the rounded track and fill, not the platform's rectangle
    assert 'android:progressDrawable="@drawable/nexus_progress_float"' in out
    assert 'android:progressDrawable="@drawable/nexus_progress_float_stage"' in out
    assert "android:progressTint=" not in out
    # the speed badge is the Nexus surface
    assert 'android:background="@drawable/nexus_bg_float_badge"' in out
    assert 'android:textColor="@color/nexus_text"' in out


@pytest.mark.parametrize("sample", [TIME_JUMP_PRETTY, TIME_JUMP_INLINE])
def test_time_jump_nexus_chrome(sample):
    out = transform_time_jump(sample)
    assert 'android:background="@drawable/txt_bg"' not in out
    assert 'android:background="@drawable/nexus_bg_float_badge"' in out
    assert 'android:background="@drawable/nexus_bg_float_button"' in out
    assert 'android:textColor="@color/nexus_text"' in out
    assert 'android:contentDescription="@string/nexus_str_float_time_jump"' in out
    assert ('android:contentDescription="@string/nexus_str_float_time_jump_last"'
            in out)
    # the button size is left to GG: TimeJumpPanel.setMinSize() resizes both
    # buttons to the float icon's size at runtime
    assert 'android:minWidth="24.0dip"' in out


def test_no_duplicate_attributes():
    """A duplicate attribute is a hard XML error, so the output must parse."""
    import xml.etree.ElementTree as ET
    ET.fromstring(transform_hot_point(PRETTY))
    ET.fromstring(transform_hot_point(INLINE))
    ET.fromstring(transform_time_jump(TIME_JUMP_PRETTY))
    ET.fromstring(transform_time_jump(TIME_JUMP_INLINE))


def test_transform_is_idempotent():
    """Re-running over an already-patched layout must not double the tags."""
    once = transform_hot_point(PRETTY)
    twice = transform_hot_point(once)
    assert once == twice
    once = transform_time_jump(TIME_JUMP_PRETTY)
    assert transform_time_jump(once) == once


def test_missing_element_fails_loudly():
    """A GG release that renames a view must abort, not half-apply."""
    broken = PRETTY.replace('android:id="@id/hot_point_icon"', 'android:id="@id/nope"')
    with pytest.raises(PatchError):
        transform_hot_point(broken)
    broken = TIME_JUMP_PRETTY.replace('android:id="@id/time_jump"',
                                      'android:id="@id/nope"')
    with pytest.raises(PatchError):
        transform_time_jump(broken)


def test_existing_attribute_is_replaced_not_skipped():
    """If GG starts setting the same attribute, Nexus's value has to win."""
    sample = PRETTY.replace(
        'android:minWidth="24.0dip"\n                android:minHeight="24.0dip" />',
        'android:importantForAccessibility="yes" />')
    out = transform_hot_point(sample)
    assert 'android:importantForAccessibility="no"' in out
    assert 'android:importantForAccessibility="yes"' not in out


def test_the_scrim_anchor_is_required_by_the_preflight():
    """A GameGuardian release that drops the flat scrim must fail loudly.

    The transform itself is tolerant -- a missing background is simply set to
    null -- so the loud failure lives in the preflight, which insists the
    stock scrim is still there before it is replaced.
    """
    broken = PRETTY.replace('                    android:background="#80000000"\n', "")
    out = transform_hot_point(broken)
    assert 'android:background="@null"' in out
    checks = (ROOT / "nexus" / "checks.py").read_text(encoding="utf-8")
    assert 'android:background="#80000000"' in checks


def test_scrim_value_is_replaced():
    """A GG release that changes the scrim colour still gets Nexus's."""
    sample = PRETTY.replace('android:background="#80000000"',
                            'android:background="#40000000"')
    out = transform_hot_point(sample)
    assert 'android:background="@null"' in out
    assert 'android:background="#40000000"' not in out


def test_the_readout_is_a_disc_over_the_icon():
    """The readout covers the icon, so it has to be the icon's shape.

    A rounded rectangle of the same size would put its corners outside the
    disc and leave them floating over the game.
    """
    readout = (RES_DIR / "res/drawable/nexus_bg_float_readout.xml").read_text(
        encoding="utf-8")
    assert 'android:shape="oval"' in readout


def test_real_gg_tree_layouts():
    """The transforms must work on the layout GG actually ships."""
    hot = GG_TREE / "res/layout/hot_point_view.xml"
    jump = GG_TREE / "res/layout/time_jump_panel.xml"
    if not hot.is_file() or not jump.is_file():
        pytest.skip("no GG tree on this machine")
    out = transform_hot_point(hot.read_text(encoding="utf-8"))
    assert '@string/nexus_str_float_icon' in out
    assert '@drawable/txt_bg' not in out
    out = transform_time_jump(jump.read_text(encoding="utf-8"))
    assert '@drawable/nexus_bg_float_badge' in out
    assert '@drawable/txt_bg' not in out


def test_flat_ui_has_no_gradients():
    for p in (RES_DIR / "res/drawable").glob("*.xml"):
        assert "<gradient" not in p.read_text(encoding="utf-8"), p.name


def test_flat_ui_has_no_elevation():
    for p in (RES_DIR / "java/host").rglob("*.java"):
        assert ".setElevation(" not in p.read_text(encoding="utf-8"), p.name


def test_power_card_has_no_glow_view():
    from nexus.layout import render
    out = render("1.0.0")
    assert "nexus_power_glow" not in out
    assert "@drawable/nexus_bg_glow" not in out


def test_float_surfaces_carry_hairlines():
    for name in ("nexus_bg_ring_off.xml", "nexus_bg_ring_on.xml",
                 "nexus_bg_float_readout.xml"):
        text = (RES_DIR / "res/drawable" / name).read_text(encoding="utf-8")
        assert '<stroke android:width="1dp"' in text, name


def test_float_resources_exist():
    for rel in ("res/drawable/nexus_bg_float_badge.xml",
                "res/drawable/nexus_bg_float_button.xml",
                "res/drawable/nexus_bg_float_readout.xml",
                "res/drawable/nexus_progress_float.xml",
                "res/drawable/nexus_progress_float_stage.xml"):
        assert (RES_DIR / rel).is_file(), rel
    strings = (RES_DIR / "res/values/nexus_strings.xml").read_text(encoding="utf-8")
    for name in ("nexus_str_float_icon", "nexus_str_float_speed_dec",
                 "nexus_str_float_speed_inc", "nexus_str_float_time_jump",
                 "nexus_str_float_time_jump_last"):
        assert f'name="{name}"' in strings, name
    colors = (RES_DIR / "res/values/nexus_colors.xml").read_text(encoding="utf-8")
    for name in ("nexus_float_badge", "nexus_float_badge_edge",
                 "nexus_float_readout", "nexus_orange_dim"):
        assert f'name="{name}"' in colors, name
