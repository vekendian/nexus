"""main.xml blocks: navbar, the three panels, ENVIRONMENT cards and settings rows.

Everything here is a template rendered at call time rather than a module-level
constant, so resource ids can be interpolated from the nexus_ids.json lock file
instead of being frozen in as hex literals.
"""

from __future__ import annotations

import re

from .anchors import PatchError, find_span, replace_exact, replace_once

FRONT_TEXT_BLOCK = '''\
            <android.fix.TextView
                android:id="@id/front_text"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content" />'''

FRONT_TEXT_GONE = '''\
                <android.fix.TextView
                    android:id="@id/front_text"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:visibility="gone" />'''

ROW_OPEN = '''\
        <android.fix.LinearLayout
            android:layout_width="fill_parent"
            android:layout_height="wrap_content"
            android:baselineAligned="false">'''

ROW_OPEN_NEW = '''\
        <android.fix.LinearLayout
            android:layout_width="fill_parent"
            android:layout_height="wrap_content"
            android:baselineAligned="false"
            android:visibility="gone">'''

START_ANCHOR = '''\
                android:text="@string/start"
                android:textAllCaps="false" />
        </android.fix.LinearLayout>
    </android.fix.LinearLayout>'''

STYLES_ANCHOR = '''\
        <item name="android:windowActionBar">false</item>'''

STYLES_NEW = '''\
        <item name="android:windowActionBar">false</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:windowBackground">@color/nexus_bg</item>
        <item name="android:statusBarColor">@color/nexus_bg</item>
        <item name="android:navigationBarColor">@color/nexus_surface</item>
        <item name="android:alertDialogTheme">@style/NexusDialog</item>
        <item name="android:dialogTheme">@style/NexusDialog</item>
        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>'''

STYLES_ITEMS = (
    "<item name=\"android:windowNoTitle\">true</item>",
    "<item name=\"android:windowBackground\">@color/nexus_bg</item>",
    "<item name=\"android:statusBarColor\">@color/nexus_bg</item>",
    "<item name=\"android:navigationBarColor\">@color/nexus_surface</item>",
    "<item name=\"android:windowLayoutInDisplayCutoutMode\">shortEdges</item>",
)


PANEL_HOME_HEAD = '''\
                <android.fix.LinearLayout
                    android:id="@id/nexus_panel_home"
                    android:layout_width="fill_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical">
                    <android.fix.LinearLayout
                        android:layout_width="fill_parent"
                        android:layout_height="40.0dip"
                        android:gravity="center_vertical"
                        android:orientation="horizontal">
                        <android.fix.TextView
                            android:layout_width="0.0dip"
                            android:layout_height="wrap_content"
                            android:layout_weight="1.0"
                            android:letterSpacing="0.3"
                            android:text="@string/nexus_str_header_nexus"
                            android:textColor="@color/nexus_orange"
                            android:textSize="18.0sp"
                            android:textStyle="bold" />
                        <android.fix.TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:background="@drawable/nexus_bg_tag"
                            android:paddingLeft="10.0dip"
                            android:paddingRight="10.0dip"
                            android:paddingTop="4.0dip"
                            android:paddingBottom="4.0dip"
                            android:text="{version}"
                            android:textColor="@color/nexus_text2"
                            android:textSize="12.0sp"
                            android:textStyle="bold" />
                    </android.fix.LinearLayout>
                    <android.fix.FrameLayout
                        android:id="@id/nexus_power_card"
                        android:layout_width="fill_parent"
                        android:layout_height="160.0dip"
                        android:layout_marginTop="16.0dip"
                        android:background="@drawable/nexus_bg_ring_off">
                        <View
                            android:id="@id/nexus_power_glow"
                            android:layout_width="fill_parent"
                            android:layout_height="fill_parent"
                            android:alpha="0.0"
                            android:background="@drawable/nexus_bg_glow" />
                        <android.fix.ImageView
                            android:id="@id/nexus_power_icon"
                            android:layout_width="96.0dip"
                            android:layout_height="96.0dip"
                            android:layout_gravity="right|bottom"
                            android:layout_marginRight="18.0dip"
                            android:layout_marginBottom="14.0dip"
                            android:alpha="0.6"
                            android:src="@drawable/nexus_ic_power"
                            android:tint="@color/nexus_text2" />
                        <android.fix.LinearLayout
                            android:layout_width="fill_parent"
                            android:layout_height="fill_parent"
                            android:gravity="top"
                            android:orientation="vertical"
                            android:padding="22.0dip">
                            <android.fix.TextView
                                android:id="@id/nexus_power_title"
                                android:layout_width="wrap_content"
                                android:layout_height="wrap_content"
                                android:text="@string/nexus_str_power_title"
                                android:textColor="@color/nexus_text"
                                android:textSize="28.0sp"
                                android:textStyle="bold" />
                            <android.fix.TextView
                                android:id="@id/nexus_power_sub"
                                android:layout_width="wrap_content"
                                android:layout_height="wrap_content"
                                android:layout_marginTop="4.0dip"
                                android:text="@string/nexus_str_power_sub"
                                android:textColor="@color/nexus_text2"
                                android:textSize="16.0sp" />
                        </android.fix.LinearLayout>
                    </android.fix.FrameLayout>
'''

ENV_CARDS = [
    ("@string/nexus_str_env_android", "nexus_env_android"),
    ("@string/nexus_str_env_abi", "nexus_env_abi"),
    ("@string/nexus_str_env_vspace", "nexus_env_vspace"),
    ("@string/nexus_str_env_root", "nexus_env_root"),
]


def _env_card(label: str, value_id: str, left: bool) -> str:
    margin = ('android:layout_marginLeft="6.0dip"'
              if left else 'android:layout_marginRight="6.0dip"')
    return f'''\
                        <android.fix.LinearLayout
                            android:layout_width="0.0dip"
                            android:layout_height="wrap_content"
                            android:layout_weight="1.0"
                            {margin}
                            android:background="@drawable/nexus_bg_card_sm"
                            android:orientation="vertical"
                            android:padding="16.0dip">
                            <android.fix.TextView
                                android:layout_width="wrap_content"
                                android:layout_height="wrap_content"
                                android:text="{label}"
                                android:textColor="@color/nexus_text2"
                                android:textSize="12.0sp" />
                            <android.fix.TextView
                                android:id="@id/{value_id}"
                                android:layout_width="wrap_content"
                                android:layout_height="wrap_content"
                                android:layout_marginTop="2.0dip"
                                android:text="--"
                                android:textColor="@color/nexus_text"
                                android:textSize="15.0sp"
                                android:textStyle="bold" />
                        </android.fix.LinearLayout>'''


ENV_SECTION = '''\
                    <android.fix.TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginLeft="6.0dip"
                        android:layout_marginTop="28.0dip"
                        android:layout_marginBottom="12.0dip"
                        android:letterSpacing="0.1"
                        android:text="@string/nexus_str_header_env"
                        android:textColor="@color/nexus_text2"
                        android:textSize="12.0sp"
                        android:textStyle="bold" />
                    <android.fix.LinearLayout
                        android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:baselineAligned="false"
                        android:orientation="horizontal">
''' + "\n".join(
    f"{_env_card(ENV_CARDS[0][0], ENV_CARDS[0][1], False)}\n"
    f"{_env_card(ENV_CARDS[1][0], ENV_CARDS[1][1], True)}"
    for _ in [0]
) + '''
                    </android.fix.LinearLayout>
                    <android.fix.LinearLayout
                        android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:layout_marginTop="12.0dip"
                        android:baselineAligned="false"
                        android:orientation="horizontal">
''' + "\n".join(
    f"{_env_card(ENV_CARDS[2][0], ENV_CARDS[2][1], False)}\n"
    f"{_env_card(ENV_CARDS[3][0], ENV_CARDS[3][1], True)}"
    for _ in [0]
) + '''
                    </android.fix.LinearLayout>
                </android.fix.LinearLayout>'''

PANEL_HOME = PANEL_HOME_HEAD + ENV_SECTION


PANEL_MODULES = '''\
                <android.fix.LinearLayout
                    android:id="@id/nexus_panel_modules"
                    android:layout_width="fill_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:visibility="gone">
                    <android.fix.TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginLeft="6.0dip"
                        android:layout_marginTop="8.0dip"
                        android:layout_marginBottom="12.0dip"
                        android:letterSpacing="0.1"
                        android:text="@string/nexus_str_header_modules"
                        android:textColor="@color/nexus_text2"
                        android:textSize="12.0sp"
                        android:textStyle="bold" />
                    <android.fix.LinearLayout
                        android:id="@+id/nexus_modules_list"
                        android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical">
                        <android.fix.TextView
                            android:id="@+id/nexus_modules_empty"
                            android:layout_width="fill_parent"
                            android:layout_height="wrap_content"
                            android:background="@drawable/nexus_bg_card_sm"
                            android:gravity="center"
                            android:orientation="vertical"
                            android:padding="24.0dip"
                            android:text="@string/nexus_str_no_modules"
                            android:textColor="@color/nexus_text2"
                            android:textSize="13.0sp" />
                    </android.fix.LinearLayout>
                </android.fix.LinearLayout>'''

# Floating add button. Lives outside the ScrollView (below) so it does not scroll
# with the panel list; visibility follows the active tab via nexusApplyTab().
MODULES_FAB = '''\
        <android.fix.ImageView
            android:id="@+id/nexus_modules_add"
            android:layout_width="56.0dip"
            android:layout_height="56.0dip"
            android:layout_gravity="bottom|end"
            android:layout_marginRight="20.0dip"
            android:layout_marginBottom="16.0dip"
            android:background="@drawable/nexus_bg_fab"
            android:clickable="true"
            android:contentDescription="@string/nexus_str_modules_add"
            android:focusable="true"
            android:src="@drawable/nexus_ic_plus"
            android:visibility="gone" />'''

# Labels reuse GameGuardian's own string resources so they inherit the 54
# shipped locales for free. Note @string/check renders "Verification" in
# English (that is GG's own wording for the button).
SETTINGS_ROWS = [
    ("nexus_row_check", "@string/check"),
    ("nexus_row_language", "@string/language"),
    ("nexus_row_help", "@string/help"),
    ("nexus_row_fix", "@string/fix_it"),
    ("nexus_row_exit", "@string/exit"),
]


def _settings_panel() -> str:
    rows = []
    for i, (rid, label) in enumerate(SETTINGS_ROWS):
        margin = "" if i == 0 else f'android:layout_marginTop="8.0dip"\n                        '
        rows.append(f'''\
                    <android.fix.LinearLayout
                        android:id="@id/{rid}"
                        {margin}android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:background="@drawable/nexus_bg_card_click"
                        android:clickable="true"
                        android:focusable="true"
                        android:orientation="vertical"
                        android:padding="16.0dip">
                        <android.fix.TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="{label}"
                            android:textColor="@color/nexus_text"
                            android:textSize="15.0sp" />
                    </android.fix.LinearLayout>''')
    body = "\n".join(rows)
    return f'''\
                <android.fix.LinearLayout
                    android:id="@id/nexus_panel_settings"
                    android:layout_width="fill_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:visibility="gone">
                    <android.fix.TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginLeft="6.0dip"
                        android:layout_marginTop="8.0dip"
                        android:layout_marginBottom="12.0dip"
                        android:letterSpacing="0.1"
                        android:text="@string/nexus_str_header_settings"
                        android:textColor="@color/nexus_text2"
                        android:textSize="12.0sp"
                        android:textStyle="bold" />
{body}
                </android.fix.LinearLayout>'''


def _nav_tab(tab_id: str, icon: str, label: str, active: bool) -> str:
    color = "@color/nexus_orange" if active else "@color/nexus_text2"
    key = tab_id.replace("nexus_tab_", "")
    pill_attrs = (
        'android:background="@drawable/nexus_bg_pill"\n'
        '                    android:paddingLeft="16.0dip"\n'
        '                    android:paddingRight="16.0dip"'
        if active else
        'android:paddingLeft="10.0dip"\n'
        '                    android:paddingRight="10.0dip"')
    lbl_vis = "" if active else '\n                        android:visibility="gone"'
    return f'''\
            <android.fix.LinearLayout
                android:id="@id/{tab_id}"
                android:layout_width="0.0dip"
                android:layout_height="wrap_content"
                android:layout_weight="1.0"
                android:clickable="true"
                android:focusable="true"
                android:gravity="center"
                android:orientation="vertical">
                <android.fix.LinearLayout
                    android:id="@id/nexus_pill_{key}"
                    android:layout_width="wrap_content"
                    android:layout_height="40.0dip"
                    android:gravity="center_vertical"
                    android:orientation="horizontal"
                    {pill_attrs}>
                    <android.fix.ImageView
                        android:id="@id/nexus_icon_{key}"
                        android:layout_width="24.0dip"
                        android:layout_height="24.0dip"
                        android:src="@drawable/{icon}"
                        android:tint="{color}" />
                    <android.fix.TextView
                        android:id="@id/nexus_lbl_{key}"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginLeft="8.0dip"
                        android:text="{label}"
                        android:textColor="@color/nexus_on_orange"
                        android:textSize="14.0sp"
                        android:textStyle="bold"{lbl_vis} />
                </android.fix.LinearLayout>
            </android.fix.LinearLayout>'''


NAVBAR = '''\
        <android.fix.LinearLayout
            android:id="@+id/nexus_navbar"
            android:layout_width="fill_parent"
            android:layout_height="wrap_content"
            android:background="@drawable/nexus_bg_nav"
            android:baselineAligned="false"
            android:gravity="center"
            android:layout_marginLeft="16.0dip"
            android:layout_marginRight="16.0dip"
            android:layout_marginBottom="10.0dip"
            android:orientation="horizontal"
            android:paddingTop="8.0dip"
            android:paddingBottom="8.0dip">
''' + "\n".join([
    _nav_tab("nexus_tab_home", "nexus_ic_home", "@string/nexus_str_tab_home", active=True),
    _nav_tab("nexus_tab_modules", "nexus_ic_modules", "@string/nexus_str_tab_modules", active=False),
    _nav_tab("nexus_tab_settings", "nexus_ic_settings", "@string/nexus_str_tab_settings", active=False),
]) + "\n        </android.fix.LinearLayout>"


def _overlay_open() -> str:
    """Open the FrameLayout the navbar and the add button share.

    Opened immediately before the ScrollView (see _scroll_view_block) and
    closed after the navbar in transform_main, so the two become siblings
    inside a FrameLayout instead of siblings in GG's vertical LinearLayout.
    """
    return '''\
        <android.fix.FrameLayout
            android:id="@+id/nexus_overlay"
            android:layout_width="fill_parent"
            android:layout_height="0.0dip"
            android:layout_weight="1.0">
            <android.fix.LinearLayout
                android:id="@+id/nexus_shell"
                android:layout_width="fill_parent"
                android:layout_height="fill_parent"
                android:orientation="vertical">
'''


def _scroll_view_block(version: str) -> str:
    front = FRONT_TEXT_GONE
    home = PANEL_HOME.replace("{version}", version)
    return f'''\
{_overlay_open()}        <android.fix.ScrollView
            android:layout_width="fill_parent"
            android:layout_height="0.0dip"
            android:layout_weight="1.0">
            <android.fix.LinearLayout
                android:layout_width="fill_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:paddingLeft="16.0dip"
                android:paddingRight="16.0dip"
                android:paddingTop="16.0dip"
                android:paddingBottom="8.0dip">
{front}
{home}

{PANEL_MODULES}

{_settings_panel()}
            </android.fix.LinearLayout>
        </android.fix.ScrollView>'''


def render(version: str) -> str:
    """The whole ScrollView body Nexus injects in place of GG's."""
    return _scroll_view_block(version)


def transform_main(main: str, version: str) -> str:
    main = replace_once(main, FRONT_TEXT_BLOCK, "", "front_text relocation")
    # The ScrollView is located by tag, not by indentation, so both the
    # pretty-printed (MT Manager) and inline (apktool) decodes match.
    span = find_span(main, "<android.fix.ScrollView")
    if span is None:
        raise PatchError("ScrollView open tag not found")
    start = span[0]
    close = main.find("</android.fix.ScrollView>", start)
    if close == -1:
        raise PatchError("ScrollView close tag not found")
    end = close + len("</android.fix.ScrollView>")
    main = main[:start] + _scroll_view_block(version) + main[end:]
    main = replace_exact(main, ROW_OPEN, ROW_OPEN_NEW,
                         "button rows", count=2)
    # The ScrollView and the navbar are siblings inside GG's `starter`
    # LinearLayout, so neither can overlap the other. Wrapping both in a
    # FrameLayout gives the add button a layer to float in, pinned
    # bottom|end just above the navbar. The inner LinearLayout keeps the
    # original vertical flow; the ScrollView loses layout_weight because the
    # wrapper is now what shares the parent's height.
    main = replace_once(main, START_ANCHOR,
                        START_ANCHOR.replace(
                            "</android.fix.LinearLayout>\n    </android.fix.LinearLayout>",
                            "</android.fix.LinearLayout>\n"
                            f"{NAVBAR}\n"
                            f"            </android.fix.LinearLayout>\n"
                            f"{MODULES_FAB}\n"
                            f"    </android.fix.FrameLayout>\n"
                            f"    </android.fix.LinearLayout>"),
                        "navbar insert")
    return main


# ---------------------------------------------------------- service_config ---

# GG's settings screen hardcodes its section-header band as an opaque purple in
# five places, one per Separator. There is no other purple in res/, so this is
# the whole recolour job for this screen.
SERVICE_SEPARATOR_BG = 'android:background="#ff422654"'
SERVICE_SEPARATOR_NEW = 'android:background="@color/nexus_orange"'
SERVICE_SEPARATOR_COUNT = 5

# Painted onto the same five rows. GG's Separator style is #AAAAAA grey, which
# sits at 1.12:1 against Nexus orange — unreadable — so each band carries its own
# dark text colour (nexus_on_orange, 6.65:1). Set per-row rather than by editing
# the shared Separator style, because that style is GG's and other screens use it.
SERVICE_SEPARATOR_TEXT = 'android:textAppearance="@style/Separator"'
SERVICE_SEPARATOR_TEXT_NEW = ('android:textAppearance="@style/Separator" '
                              'android:textColor="@color/nexus_on_orange"')

# The donate row is a self-closing TextView. Matched element-wise rather than by
# a literal string so it works for both the inline and pretty-printed decodes.
DONATE_ROW_RE = re.compile(
    r'^[ \t]*<android\.fix\.TextView\b[^>]*\bandroid:id="@id/donate"[^>]*/>[ \t]*\r?\n?',
    re.M)


def transform_service_config(xml: str) -> str:
    """Recolour the settings screen and drop the donate row.

    Removing the view is sufficient to hide the button: `donate` (0x7f050074) is
    referenced exactly once in all of smali, as a case in ConfigListAdapter's
    sparse-switch that maps a clicked row to an icon. With no view to click, the
    case is unreachable, and no code calls findViewById on it, so there is no
    null-deref risk. The dead case is left in place on purpose: editing the
    switch table would add risk for no visual gain.
    """
    xml, n = DONATE_ROW_RE.subn("", xml)
    if n != 1:
        raise PatchError(f"service_config: donate row found {n}x (expected 1x)")
    xml = replace_exact(xml, SERVICE_SEPARATOR_BG, SERVICE_SEPARATOR_NEW,
                        "service_config separator bands", count=SERVICE_SEPARATOR_COUNT)
    xml = replace_exact(xml, SERVICE_SEPARATOR_TEXT, SERVICE_SEPARATOR_TEXT_NEW,
                        "service_config separator text", count=SERVICE_SEPARATOR_COUNT)
    return xml
