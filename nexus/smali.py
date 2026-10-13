"""All Nexus smali templates plus the render() entry points.

The single-file patcher assembled these at *import* time (SWITCH_NEW = ...,
POWER_METHODS_NEW = ...), which made them impossible to unit test and forced
resource ids to be frozen in as hex literals. Here they are functions: ids are
interpolated from the lock file at call time, and GG-owned view ids are
resolved by name from the tree's public.xml.

Register discipline used throughout: p0 is the implicit `this` in a private
instance method, so `.registers N` yields locals v0..v(N-2). Wide operands
(const-wide/16, and the J argument of setDuration) consume two consecutive
registers.
"""

from __future__ import annotations

import re

from .anchors import PatchError, replace_once
from .modules import modules_methods, transform_activity_result

REGISTERS_ANCHOR = '''\
.method public onClick(Landroid/view/View;)V
    .registers 4'''
REGISTERS_NEW = '''\
.method public onClick(Landroid/view/View;)V
    .registers 12'''

COUNT_ANCHOR = '''\
    const/4 v1, 0x6

    new-array v2, v1, [I'''
COUNT_NEW = '''\
    const/16 v1, 0x10

    new-array v2, v1, [I'''

ARRAY_ANCHOR = '''\
    :array_0
    .array-data 4
        0x7f050016
        0x7f050015
        0x7f050025
        0x7f050097
        0x7f0500c0
        0x7f0500a5
    .end array-data'''
# Order matters: this array is indexed by the y(Z) listener dispatch, so entry
# N must stay paired with handler N. The first six are GameGuardian views
# resolved BY NAME; the rest are Nexus ids from the lock file.
_ARRAY_GG = ("btn_stop_service", "btn_start_usage", "check", "fix_it",
             "language", "help")
_ARRAY_NEXUS = ("nexus_tab_home", "nexus_tab_modules", "nexus_tab_settings",
                "nexus_power_card", "nexus_row_exit", "nexus_row_check",
                "nexus_row_language", "nexus_row_help", "nexus_row_fix",
                "nexus_modules_add")


def _array_new(ids) -> str:
    values = [ids.gg(n) for n in _ARRAY_GG] + [ids.hex(n) for n in _ARRAY_NEXUS]
    body = "\n".join(f"        {v}" for v in values)
    return ("    :array_0\n"
            "    .array-data 4\n"
            f"{body}\n"
            "    .end array-data")


SWITCH_ANCHOR = '''\
    :goto_1
    return-void

    :sswitch_data_0
    .sparse-switch
        0x7f050015 -> :sswitch_5
        0x7f050016 -> :sswitch_4
        0x7f050025 -> :sswitch_3
        0x7f050097 -> :sswitch_2
        0x7f0500a5 -> :sswitch_1
        0x7f0500c0 -> :sswitch_0
    .end sparse-switch'''
def _nav_find(id_hex: str, dest: str) -> str:
    return f'''\
    const v0, {id_hex}

    invoke-virtual {{p0, v0}}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object {dest}
'''


def _panel_vis(id_hex: str, vis: str, tag: str) -> str:
    insn = "const/4" if vis == "0x0" else "const/16"
    return f'''
    const v0, {id_hex}

    invoke-virtual {{p0, v0}}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_sk_{tag}

    {insn} v1, {vis}

    invoke-virtual {{v0, v1}}, Landroid/view/View;->setVisibility(I)V

    :nexus_sk_{tag}
'''


def _state_on(pill: str, lbl: str, icon: str, tag: str, ids) -> str:
    return (_nav_find(pill, "v3") + _nav_find(lbl, "v4") + _nav_find(icon, "v5")
            + f'''\
    if-eqz v3, :nexus_sk_{tag}0

    const v0, {ids.hex("nexus_bg_pill")}

    invoke-virtual {{v3, v0}}, Landroid/view/View;->setBackgroundResource(I)V

    const/high16 v0, 0x41800000

    mul-float v0, v0, v9

    float-to-int v1, v0

    const/4 v2, 0x0

    invoke-virtual {{v3, v1, v2, v1, v2}}, Landroid/view/View;->setPadding(IIII)V

    const/4 v0, 0x0

    invoke-virtual {{v3, v0}}, Landroid/view/View;->setAlpha(F)V

    invoke-virtual {{v3}}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;

    move-result-object v6

    const/high16 v0, 0x3f800000

    invoke-virtual {{v6, v0}}, Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v6

    const-wide/16 v0, 0x96

    invoke-virtual {{v6, v0, v1}}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;

    move-result-object v6

    new-instance v7, Landroid/view/animation/DecelerateInterpolator;

    invoke-direct {{v7}}, Landroid/view/animation/DecelerateInterpolator;-><init>()V

    invoke-virtual {{v6, v7}}, Landroid/view/ViewPropertyAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)Landroid/view/ViewPropertyAnimator;

    move-result-object v6

    invoke-virtual {{v6}}, Landroid/view/ViewPropertyAnimator;->start()V

    :nexus_sk_{tag}0
    if-eqz v4, :nexus_sk_{tag}1

    const/4 v0, 0x0

    invoke-virtual {{v4, v0}}, Landroid/view/View;->setVisibility(I)V

    :nexus_sk_{tag}1
    if-eqz v5, :nexus_sk_{tag}2

    check-cast v5, Landroid/widget/ImageView;

    const v0, 0xff1a1a1c

    sget-object v1, Landroid/graphics/PorterDuff$Mode;->SRC_IN:Landroid/graphics/PorterDuff$Mode;

    invoke-virtual {{v5, v0, v1}}, Landroid/widget/ImageView;->setColorFilter(ILandroid/graphics/PorterDuff$Mode;)V

    :nexus_sk_{tag}2
''')


def _state_off(pill: str, lbl: str, icon: str, tag: str) -> str:
    """Deactivate a navbar tab.

    The pill background is cleared, NOT faded. nexus_pill_* is a LinearLayout
    that CONTAINS nexus_icon_* and nexus_lbl_* as children, and setAlpha() on a
    ViewGroup applies to the entire subtree — animating the pill to alpha 0
    would hide the icon along with the background. Clearing the drawable only
    touches the pill's own background, leaving the icon visible at its inactive
    colour filter.
    """
    return (_nav_find(pill, "v3") + _nav_find(lbl, "v4") + _nav_find(icon, "v5")
            + f'''\
    if-eqz v3, :nexus_sk_{tag}0

    const/4 v0, 0x0

    invoke-virtual {{v3, v0}}, Landroid/view/View;->setBackgroundResource(I)V

    const/high16 v0, 0x41200000

    mul-float v0, v0, v9

    float-to-int v1, v0

    const/4 v2, 0x0

    invoke-virtual {{v3, v1, v2, v1, v2}}, Landroid/view/View;->setPadding(IIII)V

    :nexus_sk_{tag}0
    if-eqz v4, :nexus_sk_{tag}1

    const/16 v0, 0x8

    invoke-virtual {{v4, v0}}, Landroid/view/View;->setVisibility(I)V

    :nexus_sk_{tag}1
    if-eqz v5, :nexus_sk_{tag}2

    check-cast v5, Landroid/widget/ImageView;

    const v0, 0xffa8a8b0

    sget-object v1, Landroid/graphics/PorterDuff$Mode;->SRC_IN:Landroid/graphics/PorterDuff$Mode;

    invoke-virtual {{v5, v0, v1}}, Landroid/widget/ImageView;->setColorFilter(ILandroid/graphics/PorterDuff$Mode;)V

    :nexus_sk_{tag}2
''')


DENSITY_BLOCK = '''\
    invoke-virtual {p0}, Landroid/ext/r;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v9, v0, Landroid/util/DisplayMetrics;->density:F
'''

TAB_KEYS = ("home", "modules", "settings")

# Which navbar pill/label/icon belongs to which tab, by NAME. Ids come from the
# lock file at render time.
_TAB_PILL = {"home": "nexus_pill_home", "modules": "nexus_pill_modules",
             "settings": "nexus_pill_settings"}
_TAB_LABEL = {"home": "nexus_lbl_home", "modules": "nexus_lbl_modules",
              "settings": "nexus_lbl_settings"}
_TAB_ICON = {"home": "nexus_icon_home", "modules": "nexus_icon_modules",
             "settings": "nexus_icon_settings"}
_TAB_PANEL = {"home": "nexus_panel_home", "modules": "nexus_panel_modules",
              "settings": "nexus_panel_settings"}
_TAB_INDEX = {"home": "0x0", "modules": "0x1", "settings": "0x2"}


def tabs_state(ids) -> list:
    return [(k, ids.hex(_TAB_PILL[k]), ids.hex(_TAB_LABEL[k]), ids.hex(_TAB_ICON[k]))
            for k in TAB_KEYS]


def tab_layout(ids) -> list:
    return [(k, ids.hex(_TAB_PANEL[k]),
             [ids.hex(_TAB_PANEL[o]) for o in TAB_KEYS if o != k])
            for k in TAB_KEYS]


def _tab_body(key: str, show: str, hides: list, tail: str, tabs_state: list, ids) -> str:
    """Panel visibility + navbar pill state for one tab.

    Shared by the onClick switch cases and nexusApplyTab() so the highlighted
    pill can never drift from the visible panel after a layout re-inflate.
    """
    lines = [_panel_vis(show, "0x0", f"{key}p").rstrip("\n")]
    for i, h in enumerate(hides):
        lines.append(_panel_vis(h, "0x8", f"{key}h{i}").rstrip("\n"))
    # The add button floats above the navbar and belongs to MODULES alone.
    fab_vis = "0x0" if key == "modules" else "0x8"
    lines.append(_panel_vis(ids.hex("nexus_modules_add"), fab_vis, f"{key}fab").rstrip("\n"))
    lines.append(DENSITY_BLOCK.rstrip("\n"))
    for tkey, tp, tl, ti in tabs_state:
        if tkey == key:
            lines.append(_state_on(tp, tl, ti, f"{key}on", ids).rstrip("\n"))
        else:
            lines.append(_state_off(tp, tl, ti, f"{key}x{tkey}").rstrip("\n"))
    lines.append(tail)
    return "\n".join(lines)


def _sparse_switch(ids) -> str:
    """onClick sparse-switch.

    The GG cases mirror SWITCH_ANCHOR exactly (same id -> same handler) so the
    pre-existing click behaviour is preserved; the Nexus cases are appended.
    """
    gg = [("btn_start_usage", "sswitch_5"), ("btn_stop_service", "sswitch_4"),
          ("check", "sswitch_3"), ("fix_it", "sswitch_2"),
          ("help", "sswitch_1"), ("language", "sswitch_0")]
    nexus = [("nexus_tab_home", "sswitch_nexus_tab_home"),
             ("nexus_tab_modules", "sswitch_nexus_tab_modules"),
             ("nexus_tab_settings", "sswitch_nexus_tab_settings"),
             ("nexus_power_card", "sswitch_nexus_power"),
             ("nexus_row_exit", "sswitch_4"), ("nexus_row_check", "sswitch_3"),
             ("nexus_row_language", "sswitch_0"), ("nexus_row_help", "sswitch_1"),
             ("nexus_row_fix", "sswitch_2"),
             ("nexus_modules_add", "sswitch_nexus_modules_add")]
    rows = [f"        {ids.gg(n)} -> :{lbl}" for n, lbl in gg]
    rows += [f"        {ids.hex(n)} -> :{lbl}" for n, lbl in nexus]
    return ("    :sswitch_data_0\n"
            "    .sparse-switch\n" + "\n".join(rows) + "\n"
            "    .end sparse-switch")


def _switch_new(ids) -> str:
    tabs = tab_layout(ids)
    parts = ["    :goto_1\n    return-void"]
    for key, show, hides in tabs:
        # nexusApplyTab() already performs the panel/navbar update. The tap then
        # layers a fade on top of the incoming panel only; the resume path skips
        # that so returning to the app never replays an animation.
        case = [f"    :sswitch_nexus_tab_{key}",
                "    const/4 v0, " + _TAB_INDEX[key] + "\n",
                "    sput v0, Landroid/ext/r;->nexusTab:I\n",
                "    invoke-direct {p0}, Landroid/ext/r;->nexusApplyTab()V\n",
                "    invoke-direct {p0}, Landroid/ext/r;->nexusFadeIn()V",
                "    goto :goto_1"]
        parts.append("\n".join(case))

    # Power card: the sole authority for the float interface. The tap flips the
    # nexusPower:Z static; nexusPowerApply() then force-enforces the new state
    # (e1() to show / j.e() to hide) and re-syncs the card UI. Stop never calls
    # n(), which sets sticky m=true and would block re-show forever.
    parts.append('''\
    :sswitch_nexus_power
    sget-boolean v1, Landroid/ext/r;->nexusPower:Z

    xor-int/lit8 v1, v1, 0x1

    sput-boolean v1, Landroid/ext/r;->nexusPower:Z

    invoke-direct {p0}, Landroid/ext/r;->nexusPowerApply()V

    goto :goto_1''')

    # Add button: opens the SAF picker. The result comes back through the
    # onActivityResult hook in modules.py.
    parts.append('''\
    :sswitch_nexus_modules_add
    invoke-direct {p0}, Landroid/ext/r;->nexusModulesPick()V

    goto :goto_1''')

    parts.append(_sparse_switch(ids))
    return "\n\n".join(parts)


def _apply_tab_method(ids) -> str:
    """nexusApplyTab(): panel + navbar state for the persisted nexusTab.

    Called from the three tap cases, from onPostResume after y(true) re-inflates
    the layout, and from z(). It deliberately does NOT animate -- see
    _fade_in_method().
    """
    head = [
        ".method private nexusApplyTab()V",
        "    .registers 12",
        "",
        "    sget v0, Landroid/ext/r;->nexusTab:I",
        "",
        "    if-eqz v0, :nexus_apply_home",
        "",
        "    const/4 v1, 0x1",
        "",
        "    if-eq v0, v1, :nexus_apply_modules",
        "",
        "    const/4 v1, 0x2",
        "",
        "    if-eq v0, v1, :nexus_apply_settings",
        "",
        "    goto :nexus_apply_end",
        "",
    ]
    tabs = tab_layout(ids)
    body = [f"    :nexus_apply_{k}\n" + _tab_body(k, s_, h, "    goto :nexus_apply_end", tabs_state(ids), ids)
            for k, s_, h in tabs]
    tail = [
        "    :nexus_apply_end",
        "    return-void",
        ".end method",
    ]
    return "\n\n".join(head + body + tail)


def _fade_in_method(ids) -> str:
    """nexusFadeIn(): alpha 0->1 on the incoming panel.

    Fade-in only, and only on the tap path. Deliberately a separate method
    rather than a parameter on nexusApplyTab(): that method also runs from
    onPostResume and z() right after y(true) re-inflates the layout, and folding
    the fade in there would replay a 150ms fade of the whole panel on every
    return to the app.
    """
    tabs = tab_layout(ids)
    head = [
        ".method private nexusFadeIn()V",
        "    .registers 6",
        "",
        "    sget v0, Landroid/ext/r;->nexusTab:I",
        "",
        "    if-eqz v0, :nexus_fade_home",
        "",
        "    const/4 v1, 0x1",
        "",
        "    if-eq v0, v1, :nexus_fade_modules",
        "",
        "    const/4 v1, 0x2",
        "",
        "    if-eq v0, v1, :nexus_fade_settings",
        "",
        "    goto :nexus_fade_end",
        "",
        "    :nexus_fade_home",
        "    const v1, " + tabs[0][1],
        "    goto :nexus_fade_run",
        "",
        "    :nexus_fade_modules",
        "    const v1, " + tabs[1][1],
        "    goto :nexus_fade_run",
        "",
        "    :nexus_fade_settings",
        "    const v1, " + tabs[2][1],
        "",
        "    :nexus_fade_run",
        "    invoke-virtual {p0, v1}, Landroid/ext/r;->findViewById(I)Landroid/view/View;",
        "",
        "    move-result-object v1",
        "",
        "    if-eqz v1, :nexus_fade_end",
        "",
        "    const/4 v2, 0x0",
        "",
        "    invoke-virtual {v1, v2}, Landroid/view/View;->setAlpha(F)V",
        "",
        "    invoke-virtual {v1}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;",
        "",
        "    move-result-object v2",
        "",
        "    const/high16 v3, 0x3f800000",
        "",
        "    invoke-virtual {v2, v3}, Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;",
        "",
        "    move-result-object v2",
        "",
        "    const-wide/16 v3, 0x96",
        "",
        "    invoke-virtual {v2, v3, v4}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;",
        "",
        "    move-result-object v2",
        "",
        "    new-instance v3, Landroid/view/animation/DecelerateInterpolator;",
        "",
        "    invoke-direct {v3}, Landroid/view/animation/DecelerateInterpolator;-><init>()V",
        "",
        "    invoke-virtual {v2, v3}, Landroid/view/ViewPropertyAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)Landroid/view/ViewPropertyAnimator;",
        "",
        "    move-result-object v2",
        "",
        "    invoke-virtual {v2}, Landroid/view/ViewPropertyAnimator;->start()V",
        "",
        "    :nexus_fade_end",
        "    return-void",
        ".end method",
    ]
    return "\n\n".join(head)


POWER_METHODS_ANCHOR = "\n.method protected onSaveInstanceState(Landroid/os/Bundle;)V"

POWER_METHODS_ANCHOR = "\n.method protected onSaveInstanceState(Landroid/os/Bundle;)V"

POWER_METHODS_NEW_RAW = r'''.field public static nexusTab:I
.field public static nexusPower:Z


@@NEXUS_APPLY_TAB@@


@@NEXUS_FADE_IN@@


@@NEXUS_ENV@@


@@NEXUS_MODULES@@


.method private nexusHasPrivPerms()Z
    .registers 5

    invoke-static {}, Landroid/ext/Tools;->B0()Landroid/content/pm/PackageManager;

    move-result-object v0

    if-eqz v0, :nhp_no

    sget-object v1, Landroid/ext/Config;->E:Ljava/lang/String;

    if-eqz v1, :nhp_no

    const/4 v2, 0x0

    const-string v3, "android.permission.UPDATE_APP_OPS_STATS"

    invoke-virtual {v0, v3, v1}, Landroid/content/pm/PackageManager;->checkPermission(Ljava/lang/String;Ljava/lang/String;)I

    move-result v3

    if-eqz v3, :nhp_yes

    const-string v3, "android.permission.READ_LOGS"

    invoke-virtual {v0, v3, v1}, Landroid/content/pm/PackageManager;->checkPermission(Ljava/lang/String;Ljava/lang/String;)I

    move-result v3

    if-eqz v3, :nhp_yes

    const-string v3, "android.permission.INTERACT_ACROSS_USERS_FULL"

    invoke-virtual {v0, v3, v1}, Landroid/content/pm/PackageManager;->checkPermission(Ljava/lang/String;Ljava/lang/String;)I

    move-result v3

    if-eqz v3, :nhp_yes

    const-string v3, "android.permission.ACCESS_SUPERUSER"

    invoke-virtual {v0, v3, v1}, Landroid/content/pm/PackageManager;->checkPermission(Ljava/lang/String;Ljava/lang/String;)I

    move-result v3

    if-eqz v3, :nhp_yes

    :nhp_no
    const/4 v2, 0x0

    goto :nhp_done

    :nhp_yes
    const/4 v2, 0x1

    :nhp_done
    return v2
.end method


.method private nexusEnv()V
    .registers 6

    sget-object v0, Landroid/os/Build$VERSION;->RELEASE:Ljava/lang/String;

    if-eqz v0, :ne_android_done

    const v1, @@ID:nexus_env_android@@

    invoke-virtual {p0, v1}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v1

    check-cast v1, Landroid/widget/TextView;

    if-eqz v1, :ne_android_done

    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :ne_android_done
    sget-object v0, Landroid/os/Build;->SUPPORTED_ABIS:[Ljava/lang/String;

    if-eqz v0, :ne_abi_done

    const/4 v1, 0x0

    aget-object v0, v0, v1

    if-eqz v0, :ne_abi_done

    const v1, @@ID:nexus_env_abi@@

    invoke-virtual {p0, v1}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v1

    check-cast v1, Landroid/widget/TextView;

    if-eqz v1, :ne_abi_done

    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :ne_abi_done
    sget-boolean v0, Landroid/ext/Config;->vSpaceReal:Z

    if-eqz v0, :ne_vs_no

    const v0, @@ID:nexus_str_yes@@

    invoke-virtual {p0, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v0

    goto :ne_vs_set

    :ne_vs_no
    const v0, @@ID:nexus_str_no@@

    invoke-virtual {p0, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v0

    :ne_vs_set
    const v1, @@ID:nexus_env_vspace@@

    invoke-virtual {p0, v1}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v1

    check-cast v1, Landroid/widget/TextView;

    if-eqz v1, :ne_root_go

    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :ne_root_go
    invoke-direct {p0}, Landroid/ext/r;->nexusHasPrivPerms()Z

    move-result v0

    if-eqz v0, :ne_root_no

    const v0, @@ID:nexus_str_yes@@

    invoke-virtual {p0, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v0

    goto :ne_root_set

    :ne_root_no
    const v0, @@ID:nexus_str_no@@

    invoke-virtual {p0, v0}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v0

    :ne_root_set
    const v1, @@ID:nexus_env_root@@

    invoke-virtual {p0, v1}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v1

    check-cast v1, Landroid/widget/TextView;

    if-eqz v1, :ne_done

    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :ne_done
    return-void
.end method


.method private nexusPowerApply()V
    .registers 4

    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    if-eqz v0, :npa_ui

    iget-object v0, v0, Landroid/ext/MainService;->j:Landroid/ext/HotPoint;

    if-eqz v0, :npa_ui

    sget-boolean v1, Landroid/ext/r;->nexusPower:Z

    if-eqz v1, :npa_hide

    sget-object v1, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    invoke-virtual {v1}, Landroid/ext/MainService;->e1()V

    goto :npa_ui

    :npa_hide
    invoke-virtual {v0}, Landroid/ext/FloatPanel;->e()V

    :npa_ui
    sget-boolean v1, Landroid/ext/r;->nexusPower:Z

    if-eqz v1, :npa_uioff

    invoke-direct {p0}, Landroid/ext/r;->nexusPowerOn()V

    goto :npa_done

    :npa_uioff
    invoke-direct {p0}, Landroid/ext/r;->nexusPowerOff()V

    :npa_done
    return-void
.end method


.method private nexusPowerOn()V
    .registers 6

    const v0, @@ID:nexus_power_title@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_on_title

    check-cast v0, Landroid/widget/TextView;

    const v1, @@ID:nexus_str_iface_running@@

    invoke-virtual {p0, v1}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nexus_power_on_title
    const v0, @@ID:nexus_power_sub@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_on_sub

    check-cast v0, Landroid/widget/TextView;

    const v1, @@ID:nexus_str_tap_stop@@

    invoke-virtual {p0, v1}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nexus_power_on_sub
    const v0, @@ID:nexus_power_card@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_on_card

    const v1, @@ID:nexus_bg_ring_on@@

    invoke-virtual {v0, v1}, Landroid/view/View;->setBackgroundResource(I)V

    :nexus_power_on_card
    const v0, @@ID:nexus_power_icon@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_on_icon

    check-cast v0, Landroid/widget/ImageView;

    const v1, 0xffffe3cc

    sget-object v2, Landroid/graphics/PorterDuff$Mode;->SRC_IN:Landroid/graphics/PorterDuff$Mode;

    invoke-virtual {v0, v1, v2}, Landroid/widget/ImageView;->setColorFilter(ILandroid/graphics/PorterDuff$Mode;)V

    :nexus_power_on_icon
    const v0, @@ID:nexus_power_glow@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_on_done

    invoke-virtual {v0}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    const/high16 v1, 0x3f800000

    invoke-virtual {v0, v1}, Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    const-wide/16 v1, 0x12c

    invoke-virtual {v0, v1, v2}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/ViewPropertyAnimator;->start()V

    :nexus_power_on_done
    return-void
.end method


.method private nexusPowerOff()V
    .registers 6

    const v0, @@ID:nexus_power_title@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_off_title

    check-cast v0, Landroid/widget/TextView;

    const v1, @@ID:nexus_str_iface_stopped@@

    invoke-virtual {p0, v1}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nexus_power_off_title
    const v0, @@ID:nexus_power_sub@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_off_sub

    check-cast v0, Landroid/widget/TextView;

    const v1, @@ID:nexus_str_power_sub@@

    invoke-virtual {p0, v1}, Landroid/content/Context;->getString(I)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    :nexus_power_off_sub
    const v0, @@ID:nexus_power_card@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_off_card

    const v1, @@ID:nexus_bg_ring_off@@

    invoke-virtual {v0, v1}, Landroid/view/View;->setBackgroundResource(I)V

    :nexus_power_off_card
    const v0, @@ID:nexus_power_icon@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_off_icon

    check-cast v0, Landroid/widget/ImageView;

    const v1, 0xffa8a8b0

    sget-object v2, Landroid/graphics/PorterDuff$Mode;->SRC_IN:Landroid/graphics/PorterDuff$Mode;

    invoke-virtual {v0, v1, v2}, Landroid/widget/ImageView;->setColorFilter(ILandroid/graphics/PorterDuff$Mode;)V

    :nexus_power_off_icon
    const v0, @@ID:nexus_power_glow@@

    invoke-virtual {p0, v0}, Landroid/ext/r;->findViewById(I)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :nexus_power_off_done

    invoke-virtual {v0}, Landroid/view/View;->animate()Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/view/ViewPropertyAnimator;->alpha(F)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    const-wide/16 v1, 0x12c

    invoke-virtual {v0, v1, v2}, Landroid/view/ViewPropertyAnimator;->setDuration(J)Landroid/view/ViewPropertyAnimator;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/ViewPropertyAnimator;->start()V

    :nexus_power_off_done
    return-void
.end method'''


Z_ANCHOR = '''    const/4 v0, 0x1

    invoke-direct {p0, v0}, Landroid/ext/r;->y(Z)V

    return-void
.end method'''

Z_NEW = '''    const/4 v0, 0x1

    invoke-direct {p0, v0}, Landroid/ext/r;->y(Z)V

    invoke-direct {p0}, Landroid/ext/r;->nexusApplyTab()V

    invoke-direct {p0}, Landroid/ext/r;->nexusPowerApply()V

    invoke-direct {p0}, Landroid/ext/r;->nexusEnv()V

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesRender()V

    return-void
.end method'''

RESUME_ANCHOR = '''    sget-boolean v0, Landroid/ext/m2;->a:Z

    if-eqz v0, :cond_2

    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    invoke-virtual {v0}, Landroid/ext/MainService;->g1()V

    goto :goto_1

    :cond_2
    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    iget-object v0, v0, Landroid/ext/MainService;->n:Landroid/ext/i1;

    if-nez v0, :cond_3

    invoke-static {}, Landroid/ext/r;->S()V

    :cond_3
    :goto_1
    return-void
.end method'''

RESUME_NEW = '''    sget-boolean v0, Landroid/ext/m2;->a:Z

    if-eqz v0, :cond_2

    goto :cond_3

    :cond_2
    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    iget-object v0, v0, Landroid/ext/MainService;->n:Landroid/ext/i1;

    if-nez v0, :cond_3

    invoke-static {}, Landroid/ext/r;->S()V

    :cond_3
    :goto_1
    return-void
.end method'''

# onPostResume runs AFTER onResume and calls y(true) again. y(false) detaches
# @id/starter (Tools.O0 removes it from its parent), so the following y(true)
# re-inflates the whole layout from XML — wiping any tab applied in onResume.
# This is where the rebuilt tree is finally stable, so apply here.
POSTRESUME_ANCHOR = '''    invoke-direct {p0, v0}, Landroid/ext/r;->y(Z)V

    invoke-super {p0}, La/a;->onPostResume()V

    return-void
.end method'''

POSTRESUME_NEW = '''    invoke-direct {p0, v0}, Landroid/ext/r;->y(Z)V

    invoke-direct {p0}, Landroid/ext/r;->nexusApplyTab()V

    invoke-direct {p0}, Landroid/ext/r;->nexusPowerApply()V

    invoke-direct {p0}, Landroid/ext/r;->nexusEnv()V

    invoke-direct {p0}, Landroid/ext/r;->nexusModulesRender()V

    invoke-super {p0}, La/a;->onPostResume()V

    return-void
.end method'''

# onPause re-showed the float (e1()) on leaving the app regardless of the power
# card. Now the card is authoritative: only re-show when nexusPower is ON.
# onPause is .registers 3; only v0 is used.
ON_PAUSE_ANCHOR = """    sget-boolean v0, Landroid/ext/m2;->a:Z

    if-eqz v0, :cond_1

    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    invoke-virtual {v0}, Landroid/ext/MainService;->e1()V"""

ON_PAUSE_NEW = """    sget-boolean v0, Landroid/ext/r;->nexusPower:Z

    if-eqz v0, :cond_1

    sget-boolean v0, Landroid/ext/m2;->a:Z

    if-eqz v0, :cond_1

    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    if-eqz v0, :cond_1

    iget-object v0, v0, Landroid/ext/MainService;->j:Landroid/ext/HotPoint;

    if-eqz v0, :cond_1

    invoke-virtual {v0}, Landroid/ext/FloatPanel;->g()Z

    move-result v0

    if-eqz v0, :cond_1

    sget-object v0, Landroid/ext/MainService;->instance:Landroid/ext/MainService;

    invoke-virtual {v0}, Landroid/ext/MainService;->e1()V"""

# Density-bucket icon overrides: family -> {bucket: px}. Every bucket the
# original occupies must be overridden or the old GG icon wins at that density.


# ---------------------------------------------------------------- render ---

def switch_new(ids) -> str:
    """The full onClick sparse-switch block, with ids interpolated."""
    return _switch_new(ids)


def apply_tab_method(ids) -> str:
    return _apply_tab_method(ids)


def fade_in_method(ids) -> str:
    return _fade_in_method(ids)


def power_methods(ids) -> str:
    """Fields + nexusApplyTab/nexusFadeIn/nexusEnv/power methods."""
    out = (POWER_METHODS_NEW_RAW
           .replace("@@NEXUS_APPLY_TAB@@", _apply_tab_method(ids))
           .replace("@@NEXUS_FADE_IN@@", _fade_in_method(ids))
           .replace("@@NEXUS_ENV@@", "")
           .replace("@@NEXUS_MODULES@@", modules_methods(ids)))
    # @@ID:name@@ rather than {ids.hex(...)}: the raw template is full of smali
    # braces ({p0}, {v0, v1}) which str.format would try to interpret.
    out = re.sub(r"@@ID:(\w+)@@", lambda m: ids.hex(m.group(1)), out)
    return out


# onClick(Landroid/view/View;)V is an instance method, so its frame is
# `.registers` (params + locals) or, as apktool's baksmali writes it,
# `.locals` (locals only, params implied). Both encode the same 2-register
# frame, and Nexus's injected switch needs room for v0..v9. Widening the
# frame is therefore +8 whichever spelling the decoder chose.
ONCLICK_METHOD = ".method public onClick(Landroid/view/View;)V"
ONCLICK_METHOD_RE = re.compile(r"^\.method public onClick\(Landroid/view/View;\)V$", re.M)
ONCLICK_REGISTER_GROWTH = 8


def widen_onclick_frame(smali: str) -> str:
    """Give onClick enough registers for the injected tab switch.

    Reads whichever directive the decoder emitted and writes the widened
    count back in the same spelling, so an apktool tree stays `.locals` and
    an MT Manager tree stays `.registers`.
    """
    m = re.search(r"^(" + re.escape(ONCLICK_METHOD) + r")\n(\s*\.(?:registers|locals)\s+\d+)\s*$",
                  smali, re.M)
    if not m:
        raise PatchError("onClick frame: method header or register directive not found")
    head = re.match(r"^(\s*)(\.(?:registers|locals))\s+(\d+)$", m.group(2))
    indent, directive, count = head.group(1), head.group(2), int(head.group(3))
    # `.registers` counts params too, so both spellings widen by the same delta.
    want = count + ONCLICK_REGISTER_GROWTH
    line = f"{indent}{directive} {want}"
    return smali[:m.start()] + m.group(1) + "\n" + line + smali[m.end():]


def render(ids) -> dict:
    """Everything that gets spliced into r.smali, built fresh each call."""
    return {
        "switch": _switch_new(ids),
        "power_methods": power_methods(ids),
    }


def transform_smali(smali: str, ids) -> str:
    parts = render(ids)
    smali = widen_onclick_frame(smali)
    smali = replace_once(smali, COUNT_ANCHOR, COUNT_NEW, "button-count const")
    smali = replace_once(smali, ARRAY_ANCHOR, _array_new(ids), ":array_0 payload")
    smali = replace_once(smali, SWITCH_ANCHOR, parts["switch"], "onClick sparse-switch")
    smali = replace_once(smali, RESUME_ANCHOR, RESUME_NEW, "onResume float-restore + power-refresh")
    smali = replace_once(smali, POWER_METHODS_ANCHOR,
                         parts["power_methods"] + "\n\n.method protected onSaveInstanceState(Landroid/os/Bundle;)V",
                         "power methods + tab restore insert")
    smali = replace_once(smali, ON_PAUSE_ANCHOR, ON_PAUSE_NEW, "onPause float guard")
    smali = replace_once(smali, POSTRESUME_ANCHOR, POSTRESUME_NEW, "onPostResume re-apply")
    smali = replace_once(smali, Z_ANCHOR, Z_NEW, "z() tab + power apply")
    smali = transform_activity_result(smali)
    return smali


# ---------------------------------------------------------------- dialogs ---

# android/ext/f.smali is GameGuardian's obfuscated Alert helper. Method
# c(Context) builds every AlertDialog.Builder, and every one of them ends up in
# t(AlertDialog), which calls show() and then does post-show window fixups.
# Method t() is therefore the single funnel for dialog styling: 46 of 46
# creation sites reach it.
#
# The anchor pins the show() call together with the h() install-mode check that
# follows it, because t() must stay unique and h() is what decides whether the
# remaining fixups run at all (it returns true when MainService is absent, i.e.
# install mode). The surface goes BEFORE show() so the Window has its
# background before the decor is drawn; the button goes AFTER show() because
# getButton() is only non-null once the dialog exists, and crucially BEFORE the
# h() call so it still runs in install mode.
DIALOG_ANCHOR = '''\
    invoke-virtual {p0}, Landroid/app/Dialog;->show()V

    invoke-static {}, Landroid/ext/f;->h()Z
'''

DIALOG_SURFACE = '''\
    invoke-virtual {p0}, Landroid/app/AlertDialog;->getContext()Landroid/content/Context;
    move-result-object v1
    invoke-virtual {v1}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v1
    const v2, @@ID:nexus_bg_dialog@@
    invoke-virtual {v1, v2}, Landroid/content/res/Resources;->getDrawable(I)Landroid/graphics/drawable/Drawable;
    move-result-object v1
    invoke-virtual {p0}, Landroid/app/AlertDialog;->getWindow()Landroid/view/Window;
    move-result-object v2
    invoke-virtual {v2, v1}, Landroid/view/Window;->setBackgroundDrawable(Landroid/graphics/drawable/Drawable;)V
'''

DIALOG_PRIMARY = '''\
    const/4 v2, 0x0
    invoke-virtual {p0, v2}, Landroid/app/AlertDialog;->getButton(I)Landroid/widget/Button;
    move-result-object v1
    if-eqz v1, :nexus_primary_done
    const v2, @@ID:nexus_bg_primary@@
    invoke-virtual {v1, v2}, Landroid/widget/Button;->setBackgroundResource(I)V
    const v2, 0xff1a1a1c
    invoke-virtual {v1, v2}, Landroid/widget/Button;->setTextColor(I)V
    :nexus_primary_done
'''


def _dialog_new(ids) -> str:
    """t() with the surface and primary-button blocks spliced around show().

    v0 is left alone: t() reuses it as the constant-0 argument for the f.l,
    f.f and f.k calls that follow. v1/v2 are scratch and are dead at this point.
    """
    return (DIALOG_SURFACE
            + "\n    invoke-virtual {p0}, Landroid/app/Dialog;->show()V\n\n"
            + DIALOG_PRIMARY
            + "\n    invoke-static {}, Landroid/ext/f;->h()Z\n")


def dialog_new(ids) -> str:
    return _dialog_new(ids)


def transform_dialogs(smali: str, ids) -> str:
    new = re.sub(r"@@ID:(\w+)@@", lambda m: ids.hex(m.group(1)), _dialog_new(ids))
    return replace_once(smali, DIALOG_ANCHOR, new, "f.t dialog chrome")


# ----------------------------------------------------------------- url ---

def nexus_encode_url(url: str) -> str:
    """Encode a URL the way GameGuardian's obfuscator does.

    Every URL literal in the smali is stored with a uniform Caesar shift of +3.
    They are decoded at runtime by Tools.removeNewLinesChars(), which subtracts 3
    from each character (and additionally drops 0x0A newline chars — hence the
    misleading name). Never hand-write an encoded literal; always compute it.
    """
    return "".join(chr(ord(c) + 3) for c in url)


DOWNLOAD_URL_OLD_PLAIN = "http://gameguardian.net/download"
DOWNLOAD_URL_NEW_PLAIN = "https://github.com/vekendian/nexus"
DOWNLOAD_URL_OLD = nexus_encode_url(DOWNLOAD_URL_OLD_PLAIN)
DOWNLOAD_URL_NEW = nexus_encode_url(DOWNLOAD_URL_NEW_PLAIN)

# Deliberately NOT rewritten: MainService$m.smali uses the same literal, but as
# `charAt(11) - 0x6a` to derive an array index into the service list, not as a
# URL. Old char 11 is 'j' (106) -> index 0; the new literal's char 11 is 'k'
# (107) -> index 1, which would silently retarget the button. Left untouched.

KBD_LAYOUT_ANCHOR = 'android:background="@drawable/keyboard_background_lxx_dark"'
KBD_LAYOUT_NEW = 'android:background="@drawable/nexus_kbd_background"'

# NOTE: no <?xml?> declaration here — transform_kbd_selector keeps the original
# one that precedes <selector>, and a second declaration would be invalid XML.
# Only state_pressed is styled; activated/focused are omitted because
# InternalKeyboard is focusable="true" and a focused key would stay painted.
KBD_SELECTOR_NEW = '''<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:state_pressed="true"
        android:drawable="@drawable/nexus_kbd_key_pressed" />
    <item android:drawable="@drawable/nexus_kbd_key_normal" />
</selector>'''


# ------------------------------------------------------- settings highlight ---

# ConfigListAdapter.x() walks every settings row and, for rows whose Config$p
# reports a truthy value, paints the row with a hardcoded 0x80949442 — a
# half-alpha olive that reads as yellow over Nexus's dark background. In stock
# GG that yellow is the only cue that a game setting is toggled on, so it is
# replaced with an equally visible Nexus tone rather than dropped: the row keeps
# its "this is set" highlight, tinted to the theme.
CONFIG_ADAPTER = "smali/android/ext/ConfigListAdapter.smali"

# 0x80949442 (stock, half-alpha olive) -> 0x33FF7A00 (Nexus orange at 20%
# alpha). Opacity is kept low so the medium-weight row text stays legible on
# top of the tint, and so the tint reads as a highlight rather than a fill.
#
# smali's `const` takes a signed 32-bit int, so the literal's sign depends on
# the value: the stock colour has the high bit set and is written negative
# (-0x7f6b6bbe), whereas 0x33FF7A00 fits in a positive int and must be written
# as 0x33ff7a00. Writing the negated form makes baksmali reject the file with
# "cannot fit into an int".
SETTINGS_HIGHLIGHT_ANCHOR = '''\
    :cond_2
    if-eqz v4, :cond_3

    const v4, -0x7f6b6bbe

    invoke-virtual {v5, v4}, Landroid/view/View;->setBackgroundColor(I)V'''

SETTINGS_HIGHLIGHT_NEW = SETTINGS_HIGHLIGHT_ANCHOR.replace(
    "-0x7f6b6bbe", "0x33ff7a00")   # 0x33FF7A00 = 20% Nexus orange


def transform_settings_highlight(smali: str) -> str:
    """Retint the settings-row highlight from GG yellow to Nexus orange."""
    return replace_once(smali, SETTINGS_HIGHLIGHT_ANCHOR,
                        SETTINGS_HIGHLIGHT_NEW, "settings highlight")
