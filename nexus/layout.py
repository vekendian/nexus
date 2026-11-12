"""main.xml blocks: navbar, the three panels, ENVIRONMENT cards and settings rows.

Everything here is a template rendered at call time rather than a module-level
constant, so resource ids can be interpolated from the nexus_ids.json lock file
instead of being frozen in as hex literals.

The floating interface (the icon and its panels that sit over a game screen)
lives at the bottom of this file: it is GameGuardian's own layout, so it is
restyled in place rather than replaced.
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
        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>
        <item name="android:colorAccent">@color/nexus_orange</item>
        <item name="android:colorPrimary">@color/nexus_surface</item>
        <item name="android:colorPrimaryDark">@color/nexus_bg</item>
        <item name="android:buttonStyle">@style/NexusDialogContentButton</item>'''

# The theme items above are the ones the platform tints widgets with.
# Without them the spinners, checkboxes, switches and text selection in
# GameGuardian's own screens stay the stock blue-grey, which is the loudest
# piece of GG left in the app. The buttonStyle item is what makes a Button
# built in code the global orange pill: the XML rule covers only what the
# layout writes down.
STYLES_ITEMS = (
    "<item name=\"android:windowNoTitle\">true</item>",
    "<item name=\"android:windowBackground\">@color/nexus_bg</item>",
    "<item name=\"android:statusBarColor\">@color/nexus_bg</item>",
    "<item name=\"android:navigationBarColor\">@color/nexus_surface</item>",
    "<item name=\"android:windowLayoutInDisplayCutoutMode\">shortEdges</item>",
    "<item name=\"android:colorAccent\">@color/nexus_orange</item>",
    "<item name=\"android:colorPrimary\">@color/nexus_surface</item>",
    "<item name=\"android:colorPrimaryDark\">@color/nexus_bg</item>",
    "<item name=\"android:buttonStyle\">@style/NexusDialogContentButton</item>",
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
                        android:layout_marginBottom="16.0dip"
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
                        android:layout_marginTop="16.0dip"
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


PANEL_EXTENSIONS = '''\
                <android.fix.LinearLayout
                    android:id="@id/nexus_panel_extensions"
                    android:layout_width="fill_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:visibility="gone">
                    <android.fix.TextView
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:layout_marginLeft="6.0dip"
                        android:layout_marginTop="8.0dip"
                        android:layout_marginBottom="16.0dip"
                        android:letterSpacing="0.1"
                        android:text="@string/nexus_str_header_extensions"
                        android:textColor="@color/nexus_text2"
                        android:textSize="12.0sp"
                        android:textStyle="bold" />
                    <android.fix.LinearLayout
                        android:id="@+id/nexus_extensions_list"
                        android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical" />
                    <android.fix.TextView
                        android:id="@+id/nexus_extensions_empty"
                        android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:background="@drawable/nexus_bg_card_sm"
                        android:gravity="center"
                        android:orientation="vertical"
                        android:padding="24.0dip"
                        android:text="@string/nexus_str_no_extensions"
                        android:textColor="@color/nexus_text2"
                        android:textSize="13.0sp" />

                </android.fix.LinearLayout>'''

# Floating add button, spliced into GG's `starter` LinearLayout between the
# button rows and the navbar. In the flow rather than overlaid: a FrameLayout
# with layout_gravity="bottom|end" anchors to the bottom of everything below
# the navbar, which put the button ON the navbar rather than above it. As a
# sibling row it always sits directly above it, at any density or font scale,
# with no height arithmetic to get wrong.
EXTENSIONS_FAB = '''\
        <android.fix.ImageView
            android:id="@+id/nexus_extensions_add"
            android:layout_width="56.0dip"
            android:layout_height="56.0dip"
            android:layout_gravity="end"
            android:layout_marginRight="20.0dip"
            android:layout_marginBottom="20.0dip"
            android:background="@drawable/nexus_bg_fab"
            android:clickable="true"
            android:contentDescription="@string/nexus_str_extensions_add"
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
        margin = "" if i == 0 else f'android:layout_marginTop="12.0dip"\n                        '
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
                        android:layout_marginBottom="16.0dip"
                        android:letterSpacing="0.1"
                        android:text="@string/nexus_str_header_settings"
                        android:textColor="@color/nexus_text2"
                        android:textSize="12.0sp"
                        android:textStyle="bold" />
{body}
                </android.fix.LinearLayout>'''


def _nav_tab(tab_id: str, icon: str, label: str, active: bool) -> str:
    # The active tab's icon sits on the orange pill, so it is dark on orange --
    # the same pairing the code applies at runtime. The XML default used to be
    # the accent itself, which made the icon invisible for the frame before
    # the code ran.
    color = "@color/nexus_on_orange" if active else "@color/nexus_text2"
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
            android:paddingTop="11.0dip"
            android:paddingBottom="11.0dip">
''' + "\n".join([
    _nav_tab("nexus_tab_home", "nexus_ic_home", "@string/nexus_str_tab_home", active=True),
    _nav_tab("nexus_tab_extensions", "nexus_ic_extensions", "@string/nexus_str_tab_extensions", active=False),
    _nav_tab("nexus_tab_settings", "nexus_ic_settings", "@string/nexus_str_tab_settings", active=False),
]) + "\n        </android.fix.LinearLayout>"


def _scroll_view_block(version: str) -> str:
    front = FRONT_TEXT_GONE
    home = PANEL_HOME.replace("{version}", version)
    return f'''\
        <android.fix.ScrollView
            android:layout_width="fill_parent"
            android:layout_height="0.0dip"
            android:layout_weight="1.0">
            <android.fix.LinearLayout
                android:layout_width="fill_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:paddingLeft="20.0dip"
                android:paddingRight="20.0dip"
                android:paddingTop="20.0dip"
                android:paddingBottom="12.0dip">
{front}
{home}

{PANEL_EXTENSIONS}

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
    # The add button and the navbar are spliced in as sibling rows of GG's
    # `starter` LinearLayout: button first, then navbar, so the button always
    # lands directly above the navbar whatever the navbar's height turns out
    # to be. An earlier version wrapped both in a FrameLayout to float the
    # button; bottom|end anchored it below the navbar instead of above it.
    main = replace_once(main, START_ANCHOR,
                        START_ANCHOR.replace(
                            "</android.fix.LinearLayout>\n    </android.fix.LinearLayout>",
                            "</android.fix.LinearLayout>\n"
                            f"{EXTENSIONS_FAB}\n{NAVBAR}\n"
                            f"    </android.fix.LinearLayout>"),
                        "navbar insert")
    # main.xml is not in GG_SURFACE_LAYOUTS: Nexus owns its ScrollView. The
    # buttons round it, on the installer screen the app shows before GG is
    # enabled, are GameGuardian's, so they take the same global rule here.
    main = _patch_tags(main, GG_BTN_RE, GG_BTN_ATTRS)
    return _tint_install_bar(main)


# GG's installer screen shows a horizontal progress bar while it installs.
# The theme's accent covers the circular spinners, but a horizontal bar's
# track is not the accent, so it gets the same rounded drawable the float's
# bars use.
INSTALL_BAR_RE = re.compile(
    r'(<android\.fix\.ProgressBar\b[^>]*\bandroid:id="@id/progress_bar"[^>]*?)(/>)')


def _tint_install_bar(main: str) -> str:
    def tint(match: re.Match) -> str:
        tag = match.group(1)
        if "android:progressDrawable" in tag:
            return match.group(0)
        return tag + ' android:progressDrawable="@drawable/nexus_progress_float" />'

    out, n = INSTALL_BAR_RE.subn(tint, main)
    if n != 1:
        raise PatchError(
            f"main.xml: install progress bar found {n}x (expected 1x)")
    return out


# The two greys GameGuardian writes into its own styles, and what they become.
# GG's text styles are #ffffffff and #ffaaaaaa, hardcoded: one white and one
# grey. Nexus has one white and one grey, and every screen now uses them, so
# a label in a GG dialog is the same colour as a label in the Nexus tab.
STYLE_TEXT_REPLACEMENTS = (
    ('android:textColor">#ffffffff', 'android:textColor">@color/nexus_text', 4),
    ('android:textColorAlertDialogListItem">#ffffffff',
     'android:textColorAlertDialogListItem">@color/nexus_text', 1),
    ('android:textColor">#ffaaaaaa', 'android:textColor">@color/nexus_text2', 1),
)


def transform_styles(styles: str) -> str:
    """Add the Nexus theme to GameGuardian's, then retint its text styles.

    The theme is where the accent comes from: without colorAccent every
    spinner, checkbox, switch and text selection in GG's own screens stays
    the stock blue-grey.
    """
    styles = replace_once(styles, STYLES_ANCHOR, STYLES_NEW,
                          "styles windowActionBar")
    for old, new, count in STYLE_TEXT_REPLACEMENTS:
        n = styles.count(old)
        if n != count:
            raise PatchError(
                f"styles.xml: {old} found {n}x (expected {count}x)")
        styles = styles.replace(old, new)
    return styles


# ---------------------------------------------------------- GG surfaces ---

# GameGuardian ships 47 layouts and Nexus owns six of them. The rest are
# restyled by rule rather than one at a time, because the rules are by
# element kind: every field gets the Nexus text colours, every horizontal bar
# gets the rounded track, every divider gets the divider token.
#
# The three colours GameGuardian hardcodes in those layouts are a white
# divider, a black panel and a translucent backdrop. The first is a divider
# token, the second is a surface, and the third keeps its translucency so
# the game still shows through the overlay.
GG_BACKGROUND_REPLACEMENTS = (
    ('android:background="#c0ffffff"', 'android:background="@color/nexus_divider"'),
    ('android:background="#ffffffff"', 'android:background="@color/nexus_divider"'),
    ('android:background="#ff000000"', 'android:background="@color/nexus_surface"'),
    ('android:background="#c0000000"', 'android:background="@color/nexus_scrim"'),
)

# The field. GameGuardian's EditTexts take their colours from the platform
# theme, so their text is whatever the theme says and their hint is a
# platform grey. The theme's accent already paints their underline, which is
# most of the work; these two are the rest.
GG_FIELD_ATTRS = [
    'android:textColor="@color/nexus_text"',
    'android:textColorHint="@color/nexus_text2"',
]

# The bar. The platform's horizontal bar is a square-ended rectangle; the
# float already has the rounded one, and this is the same drawable.
GG_BAR_ATTRS = [
    'android:progressDrawable="@drawable/nexus_progress_float"',
]

# GameGuardian's own EditText classes, and the horizontal ProgressBar.
GG_FIELD_RE = re.compile(r"<android\.ext\.EditText[A-Za-z]*\b[^>]*>")
GG_BAR_RE = re.compile(
    r'<android\.fix\.ProgressBar\b[^>]*style="[^"]*progressBarStyleHorizontal"[^>]*>')

# The button. GameGuardian lays out its dialogs, editor bars, goto chips and
# installer screen with one table-styled class, android.fix.Button, and the
# platform theme painted each one a flat grey box. The global button is
# nexus_bg_button's orange pill with the app's label colour; the theme's
# android:buttonStyle carries the same surface for hypers that the class
# builds in code (android.ext.PathSelector subclasses it, so it cannot be
# matched from the layout without missing variants). Nothing here changes a
# layout's structure: the attributes Nexus writes replace stock ones of the
# same name when present, and are idempotent over an already-patched layout.
GG_BTN_RE = re.compile(r"<android\.fix\.Button\b[^>]*>")
GG_BTN_ATTRS = [
    'android:background="@drawable/nexus_bg_button"',
    'android:textColor="@color/nexus_btn_text"',
    'android:textAllCaps="false"',
]


def _patch_tags(xml: str, pattern: re.Pattern, attrs: list) -> str:
    """Add attributes to every element a pattern matches."""
    return pattern.sub(lambda m: _insert_attrs(m.group(0), attrs), xml)


# The rows GameGuardian lists. They are transparent over the panel's
# surface, so a tapped row gives no feedback at all; the ripple is what
# says the touch landed.
GG_ROW_LAYOUTS = (
    "history_item.xml", "path_item.xml", "select_dialog_item.xml",
    "service_address_item.xml", "service_memory_item.xml",
    "service_saved_item.xml", "timer_row.xml",
)


def transform_gg_surface(xml: str, rel: str) -> str:
    """Carry the Nexus look into one of GameGuardian's own layouts.

    Nothing here is allowed to change a layout's structure: only colours and
    the button surface, and only the ones that are hardcoded. A GameGuardian
    release that renames an element changes what is restyled, not what
    breaks.
    """
    for old, new in GG_BACKGROUND_REPLACEMENTS:
        xml = xml.replace(old, new)
    xml = _patch_tags(xml, GG_FIELD_RE, GG_FIELD_ATTRS)
    xml = _patch_tags(xml, GG_BAR_RE, GG_BAR_ATTRS)
    xml = _patch_tags(xml, GG_BTN_RE, GG_BTN_ATTRS)
    if rel in GG_ROW_LAYOUTS:
        xml = _patch_root(xml, rel, ['android:background="@drawable/nexus_bg_row"'])
    return xml


# The layouts Nexus does not own. The float's own two and the keyboard are
# transformed separately, and main.xml is Nexus's own screen.
GG_SURFACE_LAYOUTS = (
    "alloc.xml", "dialog_title.xml", "dump.xml", "execute.xml",
    "history_item.xml", "list_speeds_config.xml", "logcat.xml",
    "main_new_version.xml", "memory_copy.xml", "memory_filter.xml",
    "memory_range.xml", "option_edit.xml", "option_seek.xml",
    "path_item.xml", "path_selector.xml", "path_suggestion.xml",
    "prompt.xml", "prompt_item.xml", "save.xml", "select_dialog_item.xml",
    "service_address_editor.xml", "service_address_item.xml",
    "service_busy_dialog.xml", "service_config_hide.xml",
    "service_config_icon.xml", "service_dialog.xml", "service_editor.xml",
    "service_filter_search.xml", "service_fuzzy_equal.xml", "service_goto.xml",
    "service_memory_item.xml", "service_offset.xml", "service_saved_item.xml",
    "service_searcher.xml", "show_app.xml", "tab_indicator_holo.xml",
    "temp_path_config.xml", "time_jump.xml", "timer_header.xml",
    "timer_row.xml", "timer_table.xml", "unrand.xml",
)


# ---------------------------------------------------------- service_config ---

# GG's settings screen hardcodes its section-header band as an opaque purple in
# five places, one per Separator. There is no other purple in res/, so this is
# the whole recolour job for this screen.
SERVICE_SEPARATOR_BG = 'android:background="#ff422654"'
SERVICE_SEPARATOR_NEW = 'android:background="@color/nexus_orange"'
SERVICE_SEPARATOR_COUNT = 5
# The Permissions section adds one more orange band. Keep the stock count above
# for the recolour assertion; this is what the finished screen contains.
SERVICE_SEPARATOR_TOTAL = SERVICE_SEPARATOR_COUNT + 1

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

# The floating settings screen keeps the same row shape as GG's own actions.
# Permissions and the two module actions live in their own section, directly
# above GG's game settings. The main Settings panel no longer has a row.
NEXUS_EXTENSIONS_SEPARATOR = ('<android.fix.TextView android:textAppearance="@style/Separator" '
                          'android:textColor="@color/nexus_on_orange" '
                          'android:layout_gravity="center_vertical" '
                          'android:background="@color/nexus_orange" '
                          'android:focusable="false" '
                          'android:focusableInTouchMode="false" '
                          'android:layout_width="fill_parent" '
                          'android:layout_height="wrap_content" '
                          'android:text="@string/nexus_str_permissions_section" />')

PERMISSIONS_ROW = ('<android.fix.TextView android:textAppearance="@style/MediumText" '
                   'android:layout_gravity="center_vertical" '
                   'android:id="@id/nexus_row_permissions" android:paddingLeft="20.0dip" '
                   'android:paddingTop="10.0dip" android:paddingBottom="10.0dip" '
                   'android:layout_width="fill_parent" android:layout_height="wrap_content" '
                   'android:text="@string/nexus_str_permissions" />')

GAME_SECTION_ROW_RE = re.compile(
    r'(?m)^([ \t]*)<android\.fix\.TextView\b[^>]*'
    r'android:id="@id/game_section"[^>]*/>[ \t]*\r?\n')


# The panel's surface goes on the screen's container. The root of the real
# layout is one; a fragment of rows has none, and then there is nothing to
# put a background on.
GG_CONTAINER_TAGS = ("LinearLayout", "FrameLayout", "RelativeLayout",
                      "ScrollView", "TableLayout", "GridLayout")


def _patch_root(xml: str, what: str, attrs: list) -> str:
    """Add attributes to a layout's root container.

    The root is the first container in the file, which is true of both the
    pretty-printed (MT Manager) and inline (apktool) decodes.
    """
    for _tag in GG_CONTAINER_TAGS:
        m = re.search(r"<android\.(?:fix\.|widget\.)?" + _tag + r"\b[^>]*>", xml)
        if m:
            return xml[:m.start()] + _insert_attrs(m.group(0), attrs) + xml[m.end():]
    return xml


def transform_service_config(xml: str, bands: int = SERVICE_SEPARATOR_COUNT) -> str:
    """Remove donate, recolour GG's bands, and add the Nexus permissions group.

    Permissions lives in a Nexus-owned group: its "Nexus modules" band
    immediately above GG's game-settings band, instead of a row among GG's
    action rows. ConfigListAdapter dispatches the row by id; the section band
    itself has no id and is ignored by the click handler.

    The panel also gets a surface of its own. It is a floating list over a
    game, and white rows on a transparent background are unreadable over a
    bright one.
    """
    xml, n = DONATE_ROW_RE.subn("", xml)
    if n != 1:
        raise PatchError(f"service_config: donate row found {n}x (expected 1x)")
    # Recolour GG's five stock bands before adding Nexus's band: the new band
    # already carries the final colours, so it must not inflate the stock counts.
    xml = replace_exact(xml, SERVICE_SEPARATOR_BG, SERVICE_SEPARATOR_NEW,
                        "service_config separator bands", count=bands)
    xml = replace_exact(xml, SERVICE_SEPARATOR_TEXT, SERVICE_SEPARATOR_TEXT_NEW,
                        "service_config separator text", count=bands)

    def insert_section(match: re.Match) -> str:
        indent = match.group(1)
        return (f"{indent}{NEXUS_EXTENSIONS_SEPARATOR}\n"
                f"{indent}{PERMISSIONS_ROW}\n"
                f"{match.group(0)}")

    xml, n = GAME_SECTION_ROW_RE.subn(insert_section, xml, count=1)
    if n != 1:
        raise PatchError(
            f"service_config: game_section row found {n}x (expected 1x)")
    xml = _patch_root(xml, "service_config", [
        'android:background="@color/nexus_surface"'])
    return xml


# ------------------------------------------------------- floating interface ---

# GameGuardian's floating interface is three surfaces: the draggable icon with
# its speed buttons (hot_point_view.xml), the time-jump panel that hangs off
# it (time_jump_panel.xml), and the menu, which is an AlertDialog and already
# picks up the Nexus dialog theme.
#
# The icon and the panels are GG's own layouts, so they are restyled in place
# rather than replaced. The edits are element-scoped instead of literal-block
# matching: the two decoders disagree about whether an attribute sits on its
# own line, and what actually needs to change is a view's attributes, not the
# bytes around them.

# Quoted values may contain ">", so the scanner has to skip over quoted
# regions rather than stopping at the first angle bracket it sees.
_ELEMENT_RE = re.compile(r"""<[A-Za-z][\w.]*\b(?:[^>"']|"[^"]*"|'[^']*')*?>""")


def _element(xml: str, what: str, view_id: str | None = None,
             tag: str | None = None):
    """The start tag of the element named by `view_id` or `tag`."""
    for m in _ELEMENT_RE.finditer(xml):
        t = m.group(0)
        if view_id is not None:
            if f'android:id="{view_id}"' in t:
                return m
        elif tag is not None and re.match(rf"<{re.escape(tag)}\b", t):
            return m
    raise PatchError(f"{what}: element not found ({view_id or tag})")


def _attr_value(tag: str, name: str) -> str | None:
    """The value of an attribute in a start tag, or None if it has none."""
    m = re.search(rf'\b{re.escape(name)}\s*=\s*"([^"]*)"', tag)
    return m.group(1) if m else None


def _set_attr(tag: str, name: str, value: str, what: str) -> str:
    """Replace one attribute's value inside a start tag."""
    if _attr_value(tag, name) is None:
        raise PatchError(f"{what}: attribute {name} not found")
    return re.sub(rf'({re.escape(name)}\s*=\s*")([^"]*)(")',
                  lambda m: m.group(1) + value + m.group(3), tag, count=1)


def _add_attr(tag: str, attr: str) -> str:
    """Add one attribute to a start tag, keeping the file's own layout style."""
    if "\n" in tag:
        lines = tag.splitlines()
        last = lines[-1]
        indent = " " * (len(last) - len(last.lstrip()))
        stripped = last.rstrip()
        if stripped.endswith("/>"):
            head = last[: last.rindex("/>")].rstrip()
            new_last = head + "\n" + indent + attr + " />"
        else:
            head = last[: last.rindex(">")].rstrip()
            new_last = head + "\n" + indent + attr + ">"
        return "\n".join(lines[:-1] + [new_last])
    stripped = tag.rstrip()
    if stripped.endswith("/>"):
        return stripped[:-2].rstrip() + " " + attr + " />"
    return stripped[:-1].rstrip() + " " + attr + ">"


def _insert_attrs(tag: str, attrs: list) -> str:
    """Add attributes to a start tag, keeping the file's own layout style.

    An attribute the tag already carries is replaced, not skipped: Nexus's
    value has to win, and a GameGuardian release that starts setting its own
    background must not silently keep it. An attribute already carrying
    Nexus's value is left alone, so running the transform over an
    already-patched layout changes nothing.
    """
    for attr in attrs:
        name, _, raw = attr.partition("=")
        value = raw.strip().strip('"')
        current = _attr_value(tag, name)
        if current is None:
            tag = _add_attr(tag, attr)
        elif current != value:
            tag = _set_attr(tag, name, value, "floating interface")
    return tag


def _patch_element(xml: str, what: str, view_id: str | None = None,
                   tag: str | None = None, attrs: list | None = None,
                   set_attrs: dict | None = None) -> str:
    """Rewrite one element's attributes in place."""
    m = _element(xml, what, view_id=view_id, tag=tag)
    t = m.group(0)
    for name, value in (set_attrs or {}).items():
        t = _set_attr(t, name, value, what)
    if attrs:
        t = _insert_attrs(t, attrs)
    return xml[: m.start()] + t + xml[m.end():]


# The float icon is already Nexus artwork: an opaque near-black disc with an
# orange outline N, so it reads over any game frame. It still needs a plate
# like the home screen's cards so the whole float reads as one flat surface
# instead of a bare icon dropped on the game. The plate goes on hot_frame --
# the view GameGuardian puts the click listener on -- and uses the home
# screen's surface colour with a hairline edge so it stays visible over both
# a dark game and a bright one.
FLOAT_FRAME_ATTRS = [
    'android:contentDescription="@string/nexus_str_float_icon"',
    'android:background="@drawable/nexus_bg_float_badge"',
]
FLOAT_ICON_ATTRS = [
    'android:importantForAccessibility="no"',
]

# The speed buttons. GameGuardian draws them as bare white arrows with no
# surface behind them, so over a bright game they are white on white. These
# are a round surface with a hairline edge and a Nexus ripple, and the arrow
# sits inside it rather than filling it.
FLOAT_SPEED_ATTRS = [
    'android:background="@drawable/nexus_bg_float_button"',
    'android:padding="12.0dp"',
]

# The readout that covers the icon during a scan: a dense disc the same shape
# as the icon, so the scan state reads as the icon showing its progress.
# GameGuardian's own is a flat 50% black rectangle with square corners.
FLOAT_READOUT_ATTRS = [
    'android:background="@drawable/nexus_bg_float_readout"',
    'android:gravity="center"',
]
# The percentage sits on that disc, so it must not carry a background of its
# own: the stock one is the flat black scrim this replaces.
FLOAT_READOUT_TEXT_ATTRS = [
    'android:background="@null"',
]

# The bars. The platform's horizontal bar is a square-ended rectangle; these
# are the design system's rounded track and fill, clipped so the fill keeps
# its radius as it grows. The bar's height is set at runtime by
# GameGuardian (14/48 of the icon's size), which is why the drawable's
# radius is small enough to look right at every size the float can take.
FLOAT_BAR_ATTRS = [
    'android:progressDrawable="@drawable/nexus_progress_float"',
]
FLOAT_BAR_STAGE_ATTRS = [
    'android:progressDrawable="@drawable/nexus_progress_float_stage"',
]


def transform_hot_point(xml: str) -> str:
    """Restyle the floating icon, its speed controls and its readout.

    The icon is the only part of the app a user sees over another app, and it
    is the one surface GameGuardian's own chrome leaks through: the badge is a
    purple glow, the readout scrim is flat black, the progress bars are stock
    blue and green, the speed arrows have no surface under them at all, and
    none of the controls have a name.
    """
    xml = _patch_element(xml, "hot_point_view: hot_frame", view_id="@id/hot_frame",
                         attrs=FLOAT_FRAME_ATTRS)
    xml = _patch_element(xml, "hot_point_view: icon", view_id="@id/hot_point_icon",
                         attrs=FLOAT_ICON_ATTRS)
    xml = _patch_element(
        xml, "hot_point_view: speed_dec", view_id="@id/speed_dec",
        attrs=FLOAT_SPEED_ATTRS +
        ['android:contentDescription="@string/nexus_str_float_speed_dec"'])
    xml = _patch_element(
        xml, "hot_point_view: speed_inc", view_id="@id/speed_inc",
        attrs=FLOAT_SPEED_ATTRS +
        ['android:contentDescription="@string/nexus_str_float_speed_inc"'])
    xml = _patch_element(
        xml, "hot_point_view: readout", view_id="@id/progress_layout",
        attrs=FLOAT_READOUT_ATTRS)
    xml = _patch_element(
        xml, "hot_point_view: readout text", view_id="@id/progress_bar_text",
        attrs=FLOAT_READOUT_TEXT_ATTRS)
    xml = _patch_element(
        xml, "hot_point_view: progress_bar",
        view_id="@id/progress_bar", attrs=FLOAT_BAR_ATTRS)
    xml = _patch_element(
        xml, "hot_point_view: progress_bar_stage",
        view_id="@id/progress_bar_stage", attrs=FLOAT_BAR_STAGE_ATTRS)
    xml = _patch_element(
        xml, "hot_point_view: speed_text", view_id="@id/speed_text",
        set_attrs={"android:background": "@drawable/nexus_bg_float_badge"},
        attrs=['android:textColor="@color/nexus_text"'])
    return xml


# The time-jump panel: GG hangs it off the float with a purple glow behind
# two stock Material buttons, which is the brightest thing in a dark overlay.
# Their size is left alone on purpose: TimeJumpPanel.setMinSize() resizes
# both buttons to the float icon's size at runtime, so anything set here is
# overwritten the moment the panel appears.
FLOAT_BUTTON_ATTRS = [
    'android:background="@drawable/nexus_bg_float_button"',
    'android:textColor="@color/nexus_text"',
]


def transform_time_jump(xml: str) -> str:
    """Restyle the time-jump panel that hangs off the floating icon."""
    xml = _patch_element(
        xml, "time_jump_panel: root", tag="android.ext.TimeJumpPanel",
        set_attrs={"android:background": "@drawable/nexus_bg_float_badge"},
        attrs=['android:padding="12.0dip"'])
    xml = _patch_element(
        xml, "time_jump_panel: time_jump_last", view_id="@id/time_jump_last",
        attrs=FLOAT_BUTTON_ATTRS +
        ['android:contentDescription="@string/nexus_str_float_time_jump_last"'])
    xml = _patch_element(
        xml, "time_jump_panel: time_jump", view_id="@id/time_jump",
        attrs=FLOAT_BUTTON_ATTRS +
        ['android:contentDescription="@string/nexus_str_float_time_jump"'])
    return xml


# MainService's two tabs each carry an empty-state block: the search page's
# never-found hint (which composes nothing_found with try_fuzzy_search and
# try_more_ranges) and the saved page's "empty list" scroller. They are fed by
# AdapterView.setEmptyView — cut in MainService.smali by transform_empty_views,
# because the framework's own toggle overrides any XML state — and by nothing
# else, so marking them gone here removes them for good. The TextViews inside
# must stay: MainService's startup block reads and rewrites their text blind,
# so a missing element would crash before the first paint.
def transform_dialog_empty_state(xml: str) -> str:
    """Kill both empty-state blocks and give the lists back their show state.

    Half of the story is the two scrollers: marked gone here, while their
    TextViews survive untouched (MainService's startup scramble reads and
    rewrites that text, so the elements must exist).

    The other half is the lists behind them, and this is what the first take
    got wrong. Cutting AdapterView.setEmptyView in MainService is not only
    what keeps the scrollers hidden — *every* updateEmptyStatus call site is
    gated on an empty view being registered, so with the wiring gone the
    framework never touches the lists either. addr_list is stock-gone in this
    layout and was only ever shown by that cut path, so search results could
    not appear; the saved-list tab leans on the same mechanism. Both lists
    therefore carry an explicit "visible": an empty tab shows nothing (the
    scroller is gone and an empty ListView paints no rows), and a tab with
    results shows the rows again.
    """
    xml = _patch_element(xml, "service_dialog: nothing_found_view",
                         view_id="@id/nothing_found_view",
                         attrs=['android:visibility="gone"'])
    xml = _patch_element(xml, "service_dialog: empty_list_view",
                         view_id="@id/empty_list_view",
                         attrs=['android:visibility="gone"'])
    # addr_list is stock-gone; with the wiring cut nothing else would show it.
    xml = _patch_element(xml, "service_dialog: addr_list",
                         view_id="@id/addr_list",
                         set_attrs={"android:visibility": "visible"})
    # saved_list ships attribute-free; set the same explicit state so the
    # stock default stays out of the story.
    return _patch_element(xml, "service_dialog: saved_list",
                          view_id="@id/saved_list",
                          attrs=['android:visibility="visible"'])


# ---------------------------------------------------------- service_searcher ---

# The searcher dialogs -- the main search form and the "How has the value
# changed?" sub-dialog -- are GameGuardian's most crowded screens. The stock
# file gives its rows no margins at all: the title sits on the top edge, the
# 2x2 fuzzy-button grid kisses in both directions, and the limit row, the
# memory range and the Cancel/More row all touch their neighbours with a
# hairline between them. transform_gg_surface recolours this file but is
# forbidden from changing its structure, so the rhythm itself lives here.
#
# Every block that is a direct child of the scroll's column gets the same
# 12dip tail. In the changed-value dialog only message, fuzzy_row and
# memory_range show -- the rest belong to the main search form and are hidden
# there -- and a margin on a GONE view is ignored, so one rhythm serves both.
SEARCHER_BLOCK_IDS = (
    "message", "value_row", "edit_mask_row", "offset_row", "type_row",
    "mode_hacking_row", "fuzzy_row", "memory_range",
)
SEARCHER_BLOCK_MARGIN = 'android:layout_marginBottom="12.0dip"'
# The two stock only-inset values the root ScrollView carries; a release that
# moves them means the insets changed shape and this transform must be
# re-read, not silently half-applied.
SEARCHER_STOCK_PADS = ('android:paddingLeft="6.0dip"',
                       'android:paddingRight="6.0dip"')


def _patch_enclosing_row(xml: str, anchor: str, attr: str, what: str) -> str:
    """Add one attribute to the LinearLayout row whose child carries `anchor`.

    Two searcher rows ship without an id (the limit row, the Cancel/More
    row), so their start tag is found from the nearest unique child literal:
    the row opener is always the closest `<android.fix.LinearLayout ` before
    the anchor, because the child that carries the anchor is a direct
    first-level child of that row.
    """
    n = xml.count(anchor)
    if n != 1:
        raise PatchError(f"{what}: anchor found {n}x (expected 1x)")
    i = xml.index(anchor)
    marker = "<android.fix.LinearLayout "
    start = xml.rindex(marker, 0, i) + len(marker)
    return xml[:start] + attr + " " + xml[start:]


def transform_searcher_space(xml: str) -> str:
    """Give both searcher dialogs breathing room.

    Same treatment as the rest of the Nexus spacing work but with the file's
    own numbers: 12dip around the dialog and between its blocks, 6dip inside
    the fuzzy button grid (3+3 centre gutter, 6 row gap). Texts, ids and the
    view structure are untouched -- the surface recolour pass runs next to
    this one and only carries colours, so neither can undo the other.
    """
    if xml.count("<android.fix.ScrollView") != 1:
        raise PatchError("service_searcher: expected exactly one root ScrollView")
    for pad in SEARCHER_STOCK_PADS:
        if pad not in xml:
            raise PatchError(
                f"service_searcher: stock inset {pad} not found — "
                "the root insets moved, re-read this transform")
    # The dialog inset. Stock insets only the sides and by half.
    xml = _patch_element(xml, "service_searcher: root ScrollView",
                         tag="android.fix.ScrollView",
                         attrs=['android:paddingLeft="12.0dip"',
                                'android:paddingRight="12.0dip"',
                                'android:paddingTop="12.0dip"',
                                'android:paddingBottom="12.0dip"'])
    # The block rhythm: every direct child row ends 12dip before its sibling.
    for vid in SEARCHER_BLOCK_IDS:
        xml = _patch_element(xml, f"service_searcher: {vid}",
                             view_id=f"@id/{vid}",
                             attrs=[SEARCHER_BLOCK_MARGIN])
    # The two id-less rows: the limit row breathes after the buttons, and the
    # Cancel/More row follows the memory range.
    xml = _patch_enclosing_row(xml, 'android:text="@string/limit"',
                               SEARCHER_BLOCK_MARGIN,
                               "service_searcher: limit row")
    # The 2x2 grid: 3dip right + 3dip left = 6dip column gutter, and the
    # second button row drops 6dip below the first.
    xml = _patch_element(xml, "service_searcher: equal_btn",
                         view_id="@id/equal_btn",
                         attrs=['android:layout_marginRight="3.0dip"'])
    xml = _patch_element(xml, "service_searcher: not_equal_btn",
                         view_id="@id/not_equal_btn",
                         attrs=['android:layout_marginLeft="3.0dip"'])
    xml = _patch_element(xml, "service_searcher: larger_btn",
                         view_id="@id/larger_btn",
                         attrs=['android:layout_marginTop="6.0dip"',
                                'android:layout_marginRight="3.0dip"'])
    xml = _patch_element(xml, "service_searcher: smaller_btn",
                         view_id="@id/smaller_btn",
                         attrs=['android:layout_marginTop="6.0dip"',
                                'android:layout_marginLeft="3.0dip"'])
    return xml
