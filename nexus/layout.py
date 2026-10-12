"""main.xml blocks: navbar, the three panels, ENVIRONMENT cards and settings rows.

Everything here is a template rendered at call time rather than a module-level
constant, so resource ids can be interpolated from the nexus_ids.json lock file
instead of being frozen in as hex literals.
"""

from __future__ import annotations

from .anchors import PatchError, replace_once

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
                        android:layout_width="fill_parent"
                        android:layout_height="wrap_content"
                        android:background="@drawable/nexus_bg_card_sm"
                        android:gravity="center"
                        android:orientation="vertical"
                        android:padding="24.0dip">
                        <android.fix.TextView
                            android:layout_width="wrap_content"
                            android:layout_height="wrap_content"
                            android:text="@string/nexus_str_no_modules"
                            android:textColor="@color/nexus_text2"
                            android:textSize="13.0sp" />
                    </android.fix.LinearLayout>
                </android.fix.LinearLayout>'''

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
    if FRONT_TEXT_BLOCK not in main:
        raise PatchError("front_text block disappeared mid-apply")
    main = replace_once(main, FRONT_TEXT_BLOCK, "", "front_text relocation")
    start = main.index("        <android.fix.ScrollView")
    end = main.index("        </android.fix.ScrollView>")
    end += len("        </android.fix.ScrollView>")
    main = main[:start] + _scroll_view_block(version) + main[end:]
    if main.count(ROW_OPEN) != 2:
        raise PatchError(f"button rows anchor found {main.count(ROW_OPEN)}x mid-apply")
    main = main.replace(ROW_OPEN, ROW_OPEN_NEW)
    main = replace_once(main, START_ANCHOR,
                        START_ANCHOR.replace(
                            "        </android.fix.LinearLayout>\n    </android.fix.LinearLayout>",
                            f"        </android.fix.LinearLayout>\n{NAVBAR}\n    </android.fix.LinearLayout>"),
                        "navbar insert")
    return main
