"""The EXTENSIONS tab: the SAF picker, the proxy activity, and the tab layout.

The engine itself (loading, registry, card binding) is Java and is asserted in
tests/test_module_engine.py. What is left to assert here is the shape of the
things this patcher owns: the three delegates in r.smali, the XML assets, and the
proxy activity that makes the picker work at all.

What these cannot assert: that the picker opens, or that an extension runs. That
needs a device.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from nexus.layout import EXTENSIONS_FAB, PANEL_EXTENSIONS, transform_main
from nexus.extensions import (API_PICKER, ENGINE, RENDER_DESC, RENDER_IDS,
                              RENDER_REGISTERS, extensions_methods)
from nexus.tree import RES_DIR

ANDROID = "{http://schemas.android.com/apk/res/android}"

GG_TREE = Path("/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/"
               "Kujtnodnookc_499.2_src")


def _code_only(smali: str) -> str:
    """Drop comments and directives so assertions cannot match prose."""
    keep = []
    for line in smali.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith("."):
            continue
        keep.append(s)
    return "\n".join(keep)


def _ids():
    """A tiny Ids stand-in: enough for the delegate templates."""

    class _I:
        def hex(self, name):
            return {
                "ydw_nexus_dexexec": "0x7f080021",
                "nexus_extensions_list": "0x7f05017d",
                "nexus_extensions_empty": "0x7f05017e",
                "nexus_extension_title": "0x7f050181",
                "nexus_extension_meta": "0x7f050182",
                "nexus_extension_desc": "0x7f050183",
                "nexus_extension_remove": "0x7f050184",
                "nexus_extension_card": "0x7f06002f",
                "nexus_str_extension_jar": "0x7f09036a",
                "nexus_str_extension_loaded": "0x7f09036b",
                "nexus_str_extension_idle": "0x7f09036c",
                "nexus_str_extension_running": "0x7f09036d",
                "nexus_str_extension_finished": "0x7f09036e",
                "nexus_str_extension_stopped": "0x7f09036f",
                "nexus_str_extension_error": "0x7f090370",
                "nexus_str_extension_remove_title": "0x7f090367",
                "nexus_str_extension_remove_msg": "0x7f090368",
                # permissions launcher
                "nexus_str_perm_title": "0x7f090372",
                "nexus_str_perm_allow": "0x7f09037e",
                "nexus_str_perm_ask": "0x7f09037f",
                "nexus_str_perm_allow_all": "0x7f090380",
                "nexus_str_perm_ask_all": "0x7f090381",
                "nexus_str_perm_close": "0x7f090382",
                "nexus_str_perm_install": "0x7f090383",
                "nexus_str_perm_uninstall": "0x7f090384",
                "nexus_str_perm_list": "0x7f090385",
                "nexus_str_perm_import": "0x7f090389",
                "nexus_str_perm_reset": "0x7f090379",
                "nexus_str_perm_reset_done": "0x7f09037a",
                "nexus_bg_dialog": "0x7f040073",
                "nexus_bg_primary": "0x7f040074",
                "nexus_row_permissions": "0x7f050185",
            }[name]
    return _I()


def _java(rel: str) -> str:
    p = RES_DIR / "java" / rel
    assert p.is_file(), f"{p} is missing — run build-engine.sh's inputs, not its output"
    return p.read_text(encoding="utf-8")


# ------------------------------------------------------------- XML assets ---

def test_fab_sits_in_the_flow_above_the_navbar():
    """Regression: overlaid with bottom|end, the button landed ON the navbar.

    A FrameLayout's bottom|end anchors below the navbar, so the button
    overlapped it. It is now a sibling row of `starter`, emitted before the
    navbar, which puts it directly above at any density or font scale.
    """
    src = GG_TREE / "res/layout/main.xml"
    if not src.is_file():
        pytest.skip("no stock GG tree on disk")
    out = transform_main(src.read_text(encoding="utf-8"), "1.0.0")
    i_fab = out.index("@+id/nexus_extensions_add")
    i_nav = out.index("@+id/nexus_navbar")
    assert i_fab < i_nav, "the add button must be emitted before the navbar"
    assert "bottom|end" not in out[max(0, i_fab - 400):i_fab + 400], \
        "bottom|end anchors below the navbar, not above it"
    assert "@+id/nexus_overlay" not in out, "the FrameLayout overlay is gone"


def test_fab_is_right_aligned_and_hidden_by_default():
    # The fragment is spliced into main.xml, so it carries no namespace of its
    # own; supply one so ElementTree can resolve the android: attributes.
    frag = ('<root xmlns:android="http://schemas.android.com/apk/res/android">'
            + EXTENSIONS_FAB + "</root>")
    root = list(ET.fromstring(frag))[0]
    assert root.get(ANDROID + "layout_gravity") == "end"
    assert root.get(ANDROID + "visibility") == "gone"
    assert root.get(ANDROID + "background") == "@drawable/nexus_bg_fab"
    assert root.get(ANDROID + "src") == "@drawable/nexus_ic_plus"
    assert root.get(ANDROID + "clickable") == "true"


def test_extensions_panel_has_a_list_container_and_empty_state():
    assert "@+id/nexus_extensions_list" in PANEL_EXTENSIONS
    assert "@+id/nexus_extensions_empty" in PANEL_EXTENSIONS


# ------------------------------------------------------------- card layout ---

def test_card_layout_carries_all_four_fields():
    p = RES_DIR / "res/layout/nexus_extension_card.xml"
    root = ET.fromstring(p.read_text(encoding="utf-8"))
    ids = {e.get(ANDROID + "id") for e in root.iter()}
    for want in ("@+id/nexus_extension_title", "@+id/nexus_extension_meta",
                 "@+id/nexus_extension_desc", "@+id/nexus_extension_remove"):
        assert want in ids, want
    assert "@+id/nexus_extension_action" not in ids, "Run/Stop control was removed"


def test_card_meta_row_is_reachable_by_id():
    """The engine fills the meta row with the clean path; a renamed view would
    silently drop it rather than fail."""
    src = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    assert "nexus_extension_meta" not in src, "ids arrive as arguments, not names"
    out = extensions_methods(_ids())
    assert "const v5, 0x7f050182" in out, "meta id is not loaded by the delegate"


def test_remove_control_is_a_sibling_not_a_child_of_the_text():
    """A nested remove button would let a long name push it off-card."""
    p = RES_DIR / "res/layout/nexus_extension_card.xml"
    root = ET.fromstring(p.read_text(encoding="utf-8"))
    remove = [e for e in root.iter()
              if e.get(ANDROID + "id") == "@+id/nexus_extension_remove"]
    assert len(remove) == 1
    assert remove[0] in list(root), "remove must be a direct child of the card root"


# ------------------------------------------------------------------- smali ---

def test_delegates_and_nothing_else():
    """r.smali keeps pick/boot/render + the permissions screen; the other 600
    lines moved to Java."""
    raw = extensions_methods(_ids())
    for want in (".method private nexusExtensionsPick()V",
                 ".method private nexusExtensionsDrain()V",
                 ".method private nexusExtensionsRender()V"):
        assert want in raw, want
    assert ".method public static nexusPermissionsOpen(Landroid/content/Context;)V" in raw
    for gone in ("nexusModulesAdd", "nexusModulesRemove", "nexusModulesCard",
                 "nexusModulesName", "nexusModulesPrefs", "nexusModulesSave"):
        assert gone not in raw, f"{gone} is engine logic now"


def test_delegates_interpolate_ids_and_the_engine_descriptor():
    out = _code_only(extensions_methods(_ids()))
    assert "@@ID:" not in out and "@@ENGINE@@" not in out
    assert ENGINE in out
    assert "const v0, 0x7f080021" in out           # the raw asset id, into boot()
    assert "const v1, 0x7f05017d" in out           # nexus_extensions_list


def test_render_delegate_uses_one_range_call_for_every_id():
    """Nineteen id arguments cannot fit the 5-register non-range form.

    They go out as a single invoke-static/range over v0..v19 (v0 is the activity,
    moved out of p0 first). tests/test_invoke_arity.py checks the span against the
    descriptor, so this only pins the intent.
    """
    out = extensions_methods(_ids())
    m = re.search(r"\.method private nexusExtensionsRender\(\)V\n\s+\.registers (\d+)", out)
    assert m, "render delegate must declare a frame"
    # p0 plus the range window v0..v(1 + len(RENDER_IDS)).
    assert int(m.group(1)) == RENDER_REGISTERS
    assert "move-object/from16 v0, p0" in out
    hi = f"v{RENDER_REGISTERS - 2}"
    assert f"invoke-static/range {{v0 .. {hi}}}, {ENGINE}->render{RENDER_DESC}" in out
    # v0 is the activity; the ids occupy v1..v(len(RENDER_IDS)), the top of the
    # window the range form spans.
    assert out.count(f"const v{len(RENDER_IDS)}, ") == 1, \
        "the last id must be loaded into the top of the range window"
    assert len(RENDER_IDS) == 16, "7 view ids + 9 strings (no Run/Stop action)"
    # No second render call, and no per-id getString(): the ids are handed over
    # and resolved in Java, which is why r.smali's getString count drops.
    assert out.count("->render(") == 1


def test_pick_delegate_never_requests_a_result():
    """A singleInstance host cannot receive one; it launches a proxy instead."""
    out = _code_only(extensions_methods(_ids()))
    assert "startActivityForResult" not in out
    assert "->pick(Landroid/app/Activity;)V" in out


def test_picker_is_named_not_referenced():
    """The engine names the proxy by string, so no compile-time link exists
    between the Java host and a hand-written smali activity."""
    assert API_PICKER == "org.vekendian.nexus.ModulePicker"
    src = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    assert f'PICKER_CLASS = "{API_PICKER}"' in src
    assert "i.setClassName(host, PICKER_CLASS);" in src


# ------------------------------------------------- the result proxy activity ---

def test_permissions_dialog_uses_nexus_theme_and_overlay_type():
    """The row's Context is a Service wrapper with GG's old theme and no
    overlay window. The dialog must use NexusDialog from the application
    context and become an overlay window so it lands above the floating panel."""
    src = (RES_DIR / "java/host/org/vekendian/nexus/extensions/NexusHost.java").read_text()
    start = src.index("private static Context dialogContext(")
    end = src.index("private static Button permissionButton", start)
    body = src[start:end]
    assert 'resourceId(base, "NexusDialog", "style")' in body
    assert "ContextThemeWrapper(base, theme)" in body
    assert "TYPE_APPLICATION_OVERLAY" in body
    assert "TYPE_PHONE" in body
    assert 'resourceId(ui, "nexus_bg_dialog", "drawable")' in body
    assert "new AlertDialog.Builder(ui)" in body
    assert "showDialog(ui, dialog[0]);" in src
    assert "new AlertDialog.Builder(host)" not in src
    # The stock Toast is gone: a toast is drawn behind GG's overlay windows.
    assert "Toast.makeText(" not in src
    assert "NexusToast.show(" in src


def test_the_extension_action_rows_are_gone():
    """The autostart-start row and the stop-all row were removed: extensions
    manage their own lifecycle, and the settings screen only hosts
    Permissions. ConfigListAdapter must dispatch nothing else."""
    from nexus.smali import transform_config_adapter
    stock = (GG_TREE / "smali/android/ext/ConfigListAdapter.smali").read_text()
    out = transform_config_adapter(stock, _ids())
    assert "sswitch_nexus_permissions" in out
    for gone in ("sswitch_nexus_extensions_run", "sswitch_nexus_extensions_stop",
                 "runAutostart", "confirmStopAllModules", "stopModules"):
        assert gone not in out


def test_the_keyboard_is_centered_and_transparent():
    """The key grid wraps its content and no gravity was set, so the pad sat
    top-left of the full-width screen: the scroll container is centered. The
    panel's own background goes null, and the key selector is pressed-only:
    a resting key paints nothing, so the dialog surface behind the keyboard
    becomes its background and the press is the only colour."""
    from nexus.cli import transform_keyboard_layout, transform_kbd_selector
    from nexus.smali import KBD_GRAVITY_ANCHOR, KBD_GRAVITY_NEW, \
        KBD_LAYOUT_ANCHOR, KBD_LAYOUT_NEW, KBD_SELECTOR_NEW
    stock = (GG_TREE / "res/layout/keyboard.xml").read_text()
    assert KBD_GRAVITY_ANCHOR in stock
    assert KBD_LAYOUT_ANCHOR in stock
    out = transform_keyboard_layout(stock)
    assert KBD_GRAVITY_NEW in out, "HorizontalScrollView must carry center_horizontal"
    assert 'android:background="@null"' in out, "keyboard panel must be transparent"
    assert KBD_LAYOUT_NEW in out
    out_sel = transform_kbd_selector(
        (GG_TREE / "res/drawable/btn_keyboard_key_lxx_dark.xml").read_text())
    assert "nexus_kbd_key_normal" not in out_sel, "resting keys must paint nothing"
    assert out_sel.count("<item") == 1, "pressed is the only styled state"
    assert 'state_pressed="true"' in out_sel
    assert (RES_DIR / "res/drawable/nexus_kbd_key_normal.xml").exists() is False
    assert KBD_SELECTOR_NEW in out_sel


def test_the_empty_states_never_show():
    """The search tab's nothing-found block and the saved list's "empty list"
    scroller are dead weight on an empty tab. Both are hidden two ways: the
    AdapterView.setEmptyView wiring is cut in MainService (the framework
    visibility-toggles the view itself, so an XML state would not hold), and
    the blocks are marked gone in service_dialog.xml. The TextViews inside
    must stay: MainService's startup block reads and rewrites their text, so
    a missing element would crash before the first paint.

    The wiring cut has a tail we learned the hard way: every
    updateEmptyStatus call site is gated on an empty view being registered,
    so with the wiring gone the framework never shows the LISTS either, and
    addr_list — stock-gone — could never appear. The transform therefore
    hands both lists an explicit "visible" of their own."""
    from nexus.layout import transform_dialog_empty_state
    from nexus.smali import PatchError, set_empty_view_pattern, transform_empty_views

    pub = (GG_TREE / "res/values/public.xml").read_text()
    hexes = {n: re.search(rf'name="{n}" id="(0x[0-9a-f]+)"', pub).group(1)
             for n in ("nothing_found_view", "empty_list_view")}

    class _Ids:
        @staticmethod
        def gg(name):
            return hexes[name]

    ms = (GG_TREE / "smali/android/ext/MainService.smali").read_text()
    for n, hx in hexes.items():
        assert len(set_empty_view_pattern(hx).findall(ms)) == 1, f"{n} wiring shape changed"
    out = transform_empty_views(ms, _Ids())
    assert "setEmptyView" not in out, "the wiring must be gone"
    assert out.count("    nop\n    nop\n    nop") == 2, "each cut call is 3 code units"
    # Nothing was deleted beyond the calls: the registers' producers survive.
    for hx in hexes.values():
        assert hx in out
    # Re-running over a patched file must fail loudly, not silently no-op.
    with pytest.raises(PatchError):
        transform_empty_views(out, _Ids())

    sd = (GG_TREE / "res/layout/service_dialog.xml").read_text()
    out_sd = transform_dialog_empty_state(sd)
    for nm in ("nothing_found_view", "empty_list_view"):
        # The stock file has visibility="gone" on unrelated tags (e.g. addr_list),
        # so we only assert the specific tags gain the attribute after the
        # transform, not that the whole file is attribute-free before.
        tag_before = re.search(rf'<[^>]*android:id="@id/{nm}"[^>]*>', sd).group(0)
        assert 'android:visibility' not in tag_before, f"{nm}: stock already has visibility"
        tag_after = re.search(rf'<[^>]*android:id="@id/{nm}"[^>]*>', out_sd).group(0)
        assert 'android:visibility="gone"' in tag_after, f"{nm} must be permanently gone"
    # The lists: stock states first (the transform keys on them), then the
    # transform's output state.
    al_before = re.search(r'<[^>]*android:id="@id/addr_list"[^>]*>', sd).group(0)
    assert 'android:visibility="gone"' in al_before, "stock addr_list is gone"
    sl_before = re.search(r'<[^>]*android:id="@id/saved_list"[^>]*>', sd).group(0)
    assert 'android:visibility' not in sl_before, "stock saved_list is attr-free"
    for nm in ("addr_list", "saved_list"):
        tag_after = re.search(rf'<[^>]*android:id="@id/{nm}"[^>]*>', out_sd).group(0)
        assert 'android:visibility="visible"' in tag_after, \
            f"{nm} must show its rows again once the wiring is cut"
    for nm in ("nothing_found_text", "empty_list_text"):
        assert f'android:id="@id/{nm}"' in out_sd, f"{nm} must stay for the startup scramble"


def test_search_dialog_gets_room():
    """The searcher dialogs stock-pack every row: the title sits on the top
    edge, the 2x2 fuzzy grid kisses its neighbours in both directions, and
    the limit, memory-range and Cancel/More rows are all flush. The spacing
    transform puts 12dip around the dialog and between blocks and 6dip inside
    the grid, keying on the stock file so a release that moved the anchors
    fails here instead of shipping a quietly wrong dialog."""
    from nexus.anchors import PatchError
    from nexus.layout import (SEARCHER_BLOCK_IDS, SEARCHER_STOCK_PADS,
                              transform_searcher_space)

    ss = (GG_TREE / "res/layout/service_searcher.xml").read_text()
    assert ss.count("<android.fix.ScrollView") == 1, "root ScrollView moved"
    for pad in SEARCHER_STOCK_PADS:
        assert pad in ss, f"stock inset {pad} moved — re-read the transform"

    out = transform_searcher_space(ss)
    for pad in ('android:paddingLeft="12.0dip"', 'android:paddingRight="12.0dip"',
                'android:paddingTop="12.0dip"', 'android:paddingBottom="12.0dip"'):
        assert pad in out, "dialog inset did not land"
    # One 12dip tail per block plus the id-less limit row.
    assert out.count('android:layout_marginBottom="12.0dip"') == \
        len(SEARCHER_BLOCK_IDS) + 1
    for pair in ('android:layout_marginRight="3.0dip"',
                 'android:layout_marginLeft="3.0dip"',
                 'android:layout_marginTop="6.0dip"'):
        assert out.count(pair) == 2, f"grid gutter {pair} wrong"
    # The limit row's margin belongs to its (id-less) row opener, not to some
    # earlier sibling: prove it sits in the opener directly before the label.
    label_at = out.index('android:text="@string/limit"')
    row_at = out.rindex("<android.fix.LinearLayout ", 0, label_at)
    assert 'android:layout_marginBottom="12.0dip"' in out[row_at:label_at]
    # Structure untouched: every id and text the dialogs need still exists.
    for vid in SEARCHER_BLOCK_IDS:
        assert f'android:id="@id/{vid}"' in out
    assert 'android:id="@id/cancel"' in out
    # Re-running over the patched file must fail loudly — the stock anchors
    # it keys on are gone.
    with pytest.raises(PatchError):
        transform_searcher_space(out)


def test_choice_buttons_have_a_selected_highlight():
    """Allow/Ask must show which value is active; disabled-only styling read
    as a dead control. The selected state is supplied by a selector, not by
    swapping colours by hand."""
    choice = (RES_DIR / "res/drawable/nexus_bg_choice.xml").read_text()
    assert 'android:state_selected="true"' in choice
    assert "@color/nexus_orange" in choice
    assert 'android:state_pressed="true"' in choice
    colors = (RES_DIR / "res/color/nexus_choice_text.xml").read_text()
    assert 'android:state_selected="true"' in colors
    java = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    assert 'choice ? "nexus_bg_choice" : "nexus_bg_button"' in java
    assert 'resourceId(host, "nexus_choice_text", "color")' in java
    assert "allow[i].setSelected(on);" in java
    assert "ask[i].setSelected(!on);" in java


def test_the_active_choice_is_the_one_that_looks_active():
    """Orange means "in effect", and nothing else wears it.

    The active option wears orange fill with white text; the inactive option
    wears surface color with white text. The orange background is the only
    colour signal, so the active option is unmistakable. """
    colors = (RES_DIR / "res/color/nexus_choice_text.xml").read_text()
    selected = colors.split('android:state_selected="true"')[1]
    assert "@color/nexus_text" in selected.split("</item>")[0]
    unselected = colors.split("</item>")[-1]
    assert "@color/nexus_text" in unselected
    assert "@color/nexus_orange" not in unselected

    java = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    # The footer buttons are actions: they get the tonal background, not the
    # choice background, and no check.
    assert "permissionButton(ui, r[3], false)" in java
    assert "permissionButton(ui, r[4], false)" in java
    assert "permissionButton(ui, r[5], false)" in java
    assert "permissionButton(ui, r[7], false)" in java
    # The check is the second channel for the same state.
    assert 'resourceId(ui, "nexus_ic_check", "drawable")' in java
    assert "setCompoundDrawablesRelativeWithIntrinsicBounds" in java
    check = (RES_DIR / "res/drawable/nexus_ic_check.xml").read_text()
    assert "@color/nexus_text" in check


def test_the_autostart_flag_is_visible_on_the_card():
    """Each extension card shows whether its manifest asks to autostart; the
    chip must name the flag it reports."""
    java = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    assert "s.autostart()" in java
    assert "nexus_str_extension_autostart" in java
    # The status line is coloured by state, not left grey for everything.
    assert "static int statusColor(Context host, ExtensionInfo s)" in java
    assert 'color(host, "nexus_ok")' in java
    assert 'color(host, "nexus_bad")' in java


def test_every_gg_dialog_builder_is_themed():
    """All 46 GG dialog sites go through android.ext.f.c; it must hand back a
    NexusDialog builder while preserving the caller's Context (and therefore
    an Activity window token for non-overlay dialogs)."""
    from nexus.smali import DIALOG_BUILDER_ANCHOR, transform_dialog_builder, transform_dialogs
    stock = (GG_TREE / "smali/android/ext/f.smali").read_text()
    assert stock.count(DIALOG_BUILDER_ANCHOR) == 1
    out = transform_dialog_builder(transform_dialogs(stock, _ids()))
    assert ("NexusHost;->dialogBuilder(Landroid/content/Context;)"
            "Landroid/app/AlertDialog$Builder;") in out
    assert "new-instance v0, Landroid/app/AlertDialog$Builder;" not in out
    java = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    assert "public static AlertDialog.Builder dialogBuilder(Context base)" in java
    assert "new AlertDialog.Builder(themedContext(base))" in java


def test_lua_prompt_uses_the_same_nexus_dialog_builder():
    src = (RES_DIR / "smali_lua/org/vekendian/nexus/lua/"
           "NexusLua$Perm$Ask.smali").read_text()
    assert "NexusHost;->dialogBuilder()Landroid/app/AlertDialog$Builder;" in src
    assert "Landroid/ext/f;->b()Landroid/app/AlertDialog$Builder;" not in src
    assert "Landroid/ext/f;->m(Landroid/app/AlertDialog;)" in src


def test_proxy_activity_is_standard_launch_mode():
    """The whole fix hinges on this: it must NOT inherit singleInstance."""
    from nexus.manifest import PICKER_ACTIVITY
    assert API_PICKER in PICKER_ACTIVITY
    assert "android:launchMode" not in PICKER_ACTIVITY, \
        "the proxy must keep the default launch mode"
    assert 'android:exported="false"' in PICKER_ACTIVITY
    assert 'android:excludeFromRecents="true"' in PICKER_ACTIVITY


def test_proxy_parks_the_uri_for_the_host():
    from nexus.tree import RES_DIR as _res
    src = (_res / "smali/org/vekendian/nexus/ModulePicker.smali").read_text()
    code = _code_only(src)
    assert "startActivityForResult" in code, \
        "the proxy is the thing that must request the result"
    assert (f"invoke-static {{p0, v0}}, {ENGINE}->"
            f"parkFromActivity(Landroid/app/Activity;Landroid/net/Uri;)V") in code, \
        "the persistable grant must be taken before the proxy finishes"
    # The static it used to park into is gone; parking on r's field would fail at
    # runtime with NoSuchFieldError the moment the field is dropped.
    assert "nexusPendingUri" not in code


def test_saf_result_prelude_parks_and_falls_through():
    """The SAF hook must be an insertion into onActivityResult, not a method
    replacement: the stock body below it (installer dispatch included) has to
    survive, or smaling fails and every APK build dies on r.smali."""
    from nexus.smali import transform_activity_result, SAF_REQUEST
    patched = transform_activity_result(
        ".method protected onActivityResult(IILandroid/content/Intent;)V\n"
        "    .locals 2\n"
        "\n"
        "    invoke-super {p0, p1, p2, p3}, STOCK_BODY\n"
        "    return-void\n.end method\n")
    headers = patched.count(".method protected onActivityResult")
    assert headers == 1, "the hook must not duplicate the method header"
    # The stock body's super call stays -- it is even the reason the hook must
    # be an insertion, not a method replacement.
    super_index = patched.index("invoke-super {")
    rest = patched.rindex(":nexus_aar_gg")       # the label definition, last
    assert rest < super_index, "the prelude must fall through to the stock body"
    # The park path leaves before GG's dispatch; the Uri comes from the Intent.
    assert f"const v0, {SAF_REQUEST}" in patched
    assert "return-void" in patched[:rest], "the park path returns early"
    assert "invoke-virtual {p3}, Landroid/content/Intent;->getData()" in patched


def test_proxy_survives_onresume_so_it_can_receive_the_result():
    """Theme.NoDisplay forbids surviving onResume, so it must not be used."""
    from nexus.manifest import PICKER_ACTIVITY
    from nexus.tree import RES_DIR as _res
    assert "Theme.NoDisplay" not in PICKER_ACTIVITY
    # Opaque, not translucent: a translucent proxy lets the singleInstance host
    # resume first, so its drain beat the picker result and the Uri was lost.
    assert "Theme.Translucent" not in PICKER_ACTIVITY
    assert 'android:theme="@style/FixTheme"' in PICKER_ACTIVITY
    src = (_res / "smali/org/vekendian/nexus/ModulePicker.smali").read_text()
    assert ".method protected onCreate(Landroid/os/Bundle;)V" in src


# --------------------------------------------------------------- tab wiring ---

def test_navbar_and_fab_are_sibling_rows_of_starter():
    """Both are spliced into GG's vertical `starter`, FAB first.

    Nothing may re-wrap them: the overlay FrameLayout that made the button
    overlap the navbar has been removed, so assert it stays removed and that
    the ScrollView is still a direct child (it carries the weight).
    """
    src = GG_TREE / "res/layout/main.xml"
    if not src.is_file():
        pytest.skip("no stock GG tree on disk")
    out = transform_main(src.read_text(encoding="utf-8"), "1.0.0")
    i_fab = out.index("@+id/nexus_extensions_add")
    i_nav = out.index("@+id/nexus_navbar")
    assert i_fab < i_nav, "FAB row is emitted above the navbar row"
    assert "android:layout_weight=\"1.0\"" in out[:i_fab], \
        "the ScrollView must still carry the weight"
    assert "@+id/nexus_overlay" not in out and "@+id/nexus_shell" not in out


# ------------------------------------------------------- engine call order ---

def test_boot_drains_the_parked_uri_before_starting_extensions():
    """Regression shape from the pre-engine code: the parked Uri was consumed
    after being cleared, so a re-entrant resume could not import it twice. The
    order has to survive the move to Java."""
    src = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    body = src[src.index("public static void boot("):]
    body = body[:body.index("\n    }")]
    clear = body.index("pending = null;")
    add = body.index("importUri(uri);")
    assert clear < add, "clear the parked Uri before handing it on"
    assert body.rindex("powerOn();") > add, "import first, then autostart"


def test_empty_state_is_driven_by_extension_count_not_by_the_registry():
    """The registry's own card is infrastructure; 'no extensions' must mean the
    user has none, not that the loader failed."""
    src = _java("host/org/vekendian/nexus/extensions/NexusHost.java")
    assert "count == 0 ? View.VISIBLE" in src
    assert "empty.setVisibility" in src
