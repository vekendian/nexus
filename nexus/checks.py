"""Preflight / postflight / ID audit.

Both checks return a list of human-readable errors. Preflight runs against an
unpatched tree and asserts every anchor and id will be findable; postflight
runs after apply and asserts every marker landed exactly where it should.

Anchors are matched as exact literals so a weekly GG change fails here, loudly,
rather than producing an APK that is subtly wrong.
"""

from __future__ import annotations

import re
from pathlib import Path

from .anchors import PatchError
from .ids import Ids
from .layout import FRONT_TEXT_BLOCK, FRONT_TEXT_GONE, ROW_OPEN, ROW_OPEN_NEW, START_ANCHOR
from .manifest import (APP_NAME_NEW, APP_NAME_OLD, NEW_VERSION_NAME, PKG_NEW,
                        PKG_OLD, SMALI_NEW, SMALI_OLD)
from .smali import (ARRAY_ANCHOR, COUNT_ANCHOR, COUNT_NEW,
                    DOWNLOAD_URL_NEW, DOWNLOAD_URL_OLD, KBD_LAYOUT_ANCHOR,
                    KBD_LAYOUT_NEW, ON_PAUSE_ANCHOR,
                    ON_PAUSE_NEW, POSTRESUME_ANCHOR, POSTRESUME_NEW, POWER_METHODS_ANCHOR,
                    REGISTERS_ANCHOR, REGISTERS_NEW, RESUME_ANCHOR, RESUME_NEW,
                    SWITCH_ANCHOR, Z_ANCHOR, Z_NEW)
from .tree import RES_DIR, icon_resource_files, read, smali_roots

MARKER = "nexus_tab_home"  # smali const added by the patch => idempotency

# 15 ids that must exist (main.xml contract, y(true) findViewById loop + z()).
CONTRACT_IDS = [
    "root", "loader", "installer", "starter", "front_text",
    "btn_stop_service", "btn_start_usage", "check", "fix_it",
    "language", "help", "installing", "progress_bar",
    "progress_bar_text", "abort_button",
]

STYLES_ANCHOR = '''\
        <item name="android:windowActionBar">false</item>'''

STYLES_ITEMS = (
    "<item name=\"android:windowNoTitle\">true</item>",
    "<item name=\"android:windowBackground\">@color/nexus_bg</item>",
    "<item name=\"android:statusBarColor\">@color/nexus_bg</item>",
    "<item name=\"android:navigationBarColor\">@color/nexus_surface</item>",
    "<item name=\"android:windowLayoutInDisplayCutoutMode\">shortEdges</item>",
)


def is_patched(tree: Path) -> bool:
    return MARKER in read(tree, "smali/android/ext/r.smali")


def preflight(tree: Path, ids: Ids) -> list:
    errors = []
    main = read(tree, "res/layout/main.xml")
    public = read(tree, "res/values/public.xml")
    smali = read(tree, "smali/android/ext/r.smali")
    styles = read(tree, "res/values/styles.xml")
    nexus_styles = (tree / "res/values/nexus_styles.xml")
    nexus_styles = nexus_styles.read_text(encoding="utf-8") if nexus_styles.is_file() else ""

    if MARKER in smali:
        errors.append("already patched (marker %r in r.smali) — run 'revert' first" % MARKER)

    for cid in CONTRACT_IDS:
        if f'<public type="id" name="{cid}"' not in public:
            errors.append(f"contract id missing from public.xml: {cid}")

    errors.extend(ids.audit_collisions(public))
    _ns_path = RES_DIR / "res/values/nexus_strings.xml"
    _nexus_strings = _ns_path.read_text(encoding="utf-8") if _ns_path.is_file() else ""
    for _kind, _name, _hexval in ids.pinned_table():
        if _kind == "string" and _name not in _nexus_strings:
            errors.append(f"nexus_strings.xml: missing definition for {_name}")

    for _rel in ["res/values/nexus_strings.xml", "res/values/nexus_styles.xml",
                 "res/drawable/nexus_bg_dialog.xml", "res/drawable/nexus_bg_button.xml",
                 "res/drawable/nexus_kbd_background.xml", "res/drawable/nexus_kbd_key.xml",
                 "res/drawable/nexus_kbd_key_pressed.xml",
                 "res/drawable/nexus_kbd_key_normal.xml"]:
        if not (RES_DIR / _rel).is_file():
            errors.append(f"patcher resource missing: {_rel}")

    # download-URL anchors
    for _rel in ("smali/android/ext/r$n.smali", "smali/android/ext/ShowApp.smali",
                 "smali/android/ext/MainService$m.smali"):
        _p = tree / _rel
        if not _p.is_file():
            errors.append(f"url anchor file missing: {_rel}")
        elif DOWNLOAD_URL_OLD not in _p.read_text(encoding="utf-8"):
            errors.append(f"url anchor missing in {_rel}")
    if smali.count('"' + DOWNLOAD_URL_OLD + '"') != 0:
        errors.append("r.smali: download-URL literal unexpectedly bare")
    if smali.count('"#' + DOWNLOAD_URL_OLD + '"') != 1:
        errors.append("r.smali: commented download-URL literal not found")

    # keyboard anchors
    if read(tree, "res/layout/keyboard.xml").count(KBD_LAYOUT_ANCHOR) != 1:
        errors.append("keyboard.xml: background anchor not found")
    _ks = read(tree, "res/drawable/btn_keyboard_key_lxx_dark.xml")
    if "<selector" not in _ks or "</selector>" not in _ks:
        errors.append("btn_keyboard_key_lxx_dark.xml: <selector> not found")

    for what, blob, cnt in [
        ("front_text block", FRONT_TEXT_BLOCK, 1),
        ("button rows (visibility targets)", ROW_OPEN, 2),
        ("ScrollView open", "        <android.fix.ScrollView", 1),
        ("ScrollView close", "        </android.fix.ScrollView>", 1),
        ("start-button/navbar insert point", START_ANCHOR, 1),
    ]:
        got = main.count(blob)
        if got != cnt:
            errors.append(f"main.xml anchor {what!r} found {got}x (expected {cnt}x)")

    for what, blob in [
        ("onClick .registers", REGISTERS_ANCHOR),
        ("y(Z)V button-count const", COUNT_ANCHOR),
        (":array_0 payload", ARRAY_ANCHOR),
        ("onClick sparse-switch block", SWITCH_ANCHOR),
    ]:
        if smali.count(blob) != 1:
            errors.append(f"r.smali anchor {what!r} found {smali.count(blob)}x (expected 1x)")

    if styles.count(STYLES_ANCHOR) != 1:
        errors.append(f"styles.xml anchor found {styles.count(STYLES_ANCHOR)}x (expected 1x)")

    if not (RES_DIR / "res").is_dir():
        errors.append(f"resources missing: {RES_DIR / 'res'}")

    for rel in icon_resource_files():
        if not (RES_DIR / rel).is_file():
            errors.append(f"icon override missing: {RES_DIR / rel}")

    # rebrand anchors
    if not (tree / "smali" / "com" / "scmq").is_dir():
        errors.append("rebrand: smali/com/scmq missing (already rebranded?)")
    if SMALI_NEW in read(tree, "smali/android/ext/r.smali"):
        errors.append("rebrand: Lorg/vekendian/nexus/ already present (already rebranded?)")
    manifest = read(tree, "AndroidManifest.xml")
    if f'package="{PKG_OLD}"' not in manifest:
        errors.append(f"rebrand: manifest package is not {PKG_OLD}")
    if not re.search(r"<application\b[^>]*android:label=", manifest, re.DOTALL):
        errors.append("rebrand: application android:label not found in manifest")
    if manifest.count('android:label="Game"') != 2:
        errors.append('rebrand: expected 2 activity android:label="Game"')
    hw = ('<activity\n            android:label="Game"\n'
          '            android:icon="@mipmap/ic_hw_48dp"')
    if hw not in manifest:
        errors.append("rebrand: ActivityMain HW launcher block not found")
    if manifest.count('android.intent.category.LAUNCHER') != 2:
        errors.append("rebrand: expected 2 LAUNCHER categories in clean manifest")
    strings = tree / "res/values/strings.xml"
    if strings.is_file() and APP_NAME_OLD not in strings.read_text(encoding="utf-8"):
        errors.append("rebrand: strings.xml app_name is not GameGuardian")
    return errors


def postflight(tree: Path, ids: Ids) -> list:
    errors = []
    main = read(tree, "res/layout/main.xml")
    public = read(tree, "res/values/public.xml")
    smali = read(tree, "smali/android/ext/r.smali")
    styles = read(tree, "res/values/styles.xml")
    nexus_styles = (tree / "res/values/nexus_styles.xml")
    nexus_styles = nexus_styles.read_text(encoding="utf-8") if nexus_styles.is_file() else ""

    for _kind, _name, _hexval in ids.pinned_table():
        if f'<public type="{_kind}" name="{_name}"' not in public:
            errors.append(f"public.xml: missing {_kind} {_name}")

    for _label in ("@string/check", "@string/language", "@string/help",
                   "@string/fix_it", "@string/exit"):
        if _label not in main:
            errors.append(f"main.xml: settings row label {_label} missing")
    for _str in ("@string/nexus_str_header_nexus", "@string/nexus_str_header_modules",
                 "@string/nexus_str_header_settings", "@string/nexus_str_no_modules",
                 "@string/nexus_str_tab_home", "@string/nexus_str_env_android",
                 "@string/nexus_str_env_abi", "@string/nexus_str_env_vspace",
                 "@string/nexus_str_env_root", "@string/nexus_str_power_title",
                 "@string/nexus_str_power_sub"):
        if _str not in main:
            errors.append(f"main.xml: missing {_str}")
    for _nm, _hexval in ids.nexus.get("string", {}).items():
        if _nm == "nexus_str_power_title":
            continue  # XML default only; never set from smali
        if f"const v1, {_hexval}" not in smali and f"const v0, {_hexval}" not in smali:
            errors.append(f"r.smali: {_nm} ({_hexval}) not referenced")
    if smali.count("Landroid/content/Context;->getString(I)Ljava/lang/String;") != 8:
        errors.append("r.smali: expected 8 Context.getString() calls")
    for _row_id in ("0x7f050167", "0x7f050168", "0x7f050169", "0x7f05016a", "0x7f05016b"):
        if smali.count(_row_id) != 2:
            errors.append(f"r.smali: settings row {_row_id} appears "
                          f"{smali.count(_row_id)}x (expected 2x: array + dispatch)")
    if "<public type=\"string\"" not in public:
        errors.append("public.xml: no string entries emitted")
    for what in ["nexus_panel_home", "nexus_panel_modules", "nexus_panel_settings",
                 "nexus_power_card", "nexus_navbar", "@id/nexus_tab_home",
                 "nexus_row_check", "nexus_row_exit"]:
        if what not in main:
            errors.append(f"main.xml: missing {what}")
    if FRONT_TEXT_GONE not in main:
        errors.append("main.xml: front_text is not hidden (visibility=gone)")
    if main.count(ROW_OPEN_NEW) != 2:
        errors.append("main.xml: button rows not hidden (visibility=gone)")
    if MARKER not in smali:
        errors.append("r.smali: marker missing")
    if "0x7f050160" not in smali or ":sswitch_nexus_tab_home" not in smali:
        errors.append("r.smali: tab wiring missing")
    if ".method public onClick(Landroid/view/View;)V\n    .registers 12" not in smali:
        errors.append("r.smali: onClick .registers is not 12")
    if "DecelerateInterpolator" not in smali:
        errors.append("r.smali: navbar animation missing")
    # Each _tab_body call emits 3 check-casts (one per navbar tab). The tap
    # cases no longer inline a copy of the body, so nexusApplyTab()'s 3 calls
    # are the only source.
    if smali.count("check-cast v5, Landroid/widget/ImageView;") != 9:
        errors.append("r.smali: missing ImageView check-cast before setColorFilter (VerifyError)")
    if smali.count(".method private nexusPowerOn()V") != 1:
        errors.append("r.smali: nexusPowerOn() missing")
    if smali.count(".method private nexusPowerOff()V") != 1:
        errors.append("r.smali: nexusPowerOff() missing")
    if smali.count(".method private nexusPowerApply()V") != 1:
        errors.append("r.smali: nexusPowerApply() missing")
    if smali.count(".method private nexusEnv()V") != 1:
        errors.append("r.smali: nexusEnv() missing")
    if smali.count(".method private nexusHasPrivPerms()Z") != 1:
        errors.append("r.smali: nexusHasPrivPerms() missing")
    if smali.count("invoke-direct {p0}, Landroid/ext/r;->nexusEnv()V") != 2:
        errors.append("r.smali: nexusEnv() must be called 2x (onPostResume, z())")
    for _name in ("nexus_env_android", "nexus_env_abi", "nexus_env_vspace", "nexus_env_root"):
        if f"@id/{_name}" not in main:
            errors.append(f"main.xml: missing ENVIRONMENT value {_name}")
        if f'name="{_name}"' not in public:
            errors.append(f"public.xml: missing {_name}")
    if 'android:text="@string/nexus_str_header_env"' not in main:
        errors.append('main.xml: ENVIRONMENT section header missing')
    if 'android:text="SYSTEM"' in main:
        errors.append("main.xml: old SYSTEM header still present")
    if smali.count(".method private nexusApplyTab()V") != 1:
        errors.append("r.smali: nexusApplyTab() missing")
    if ":sswitch_nexus_power" not in smali:
        errors.append("r.smali: :sswitch_nexus_power case missing")
    if "0x7f050166 -> :sswitch_nexus_power" not in smali:
        errors.append("r.smali: power card id 0x7f050166 not wired to power case")
    if smali.count("invoke-direct {p0}, Landroid/ext/r;->nexusPowerApply()V") != 3:
        errors.append("r.smali: nexusPowerApply() must be called 3x (switch, onPostResume, z)")
    if smali.count("invoke-direct {p0}, Landroid/ext/r;->nexusApplyTab()V") != 5:
        errors.append("r.smali: nexusApplyTab() must be called 5x (3 switch cases, onPostResume, z())")
    if smali.count(".method private nexusFadeIn()V") != 1:
        errors.append("r.smali: nexusFadeIn() missing")
    # 3 from _state_on (one per tab in nexusApplyTab) + 1 in nexusFadeIn().
    # _state_off must contribute NONE: nexus_pill_* CONTAINS nexus_icon_* as a
    # child, so driving the pill's alpha to 0 would hide the inactive icons too.
    if smali.count("setAlpha(F)V") != 4:
        errors.append("r.smali: setAlpha(F) count is "
                      f"{smali.count('setAlpha(F)V')} (expected 4) — _state_off must "
                      "clear the pill background, not fade it (would hide icons)")
    if smali.count("invoke-direct {p0}, Landroid/ext/r;->nexusFadeIn()V") != 3:
        errors.append("r.smali: nexusFadeIn() must be called 3x (one per tab tap)")
    # The fade must ride the tap path only. If it leaked into the resume hooks
    # it would replay a 150ms fade of the whole panel every time the app returns.
    if "nexusFadeIn()V\n\n    invoke-super" in smali or \
            "nexusFadeIn()V\n\n    :goto_1\n    return-void" in smali:
        errors.append("r.smali: nexusFadeIn() must not run on the resume path")
    if ":nexus_apply_home" not in smali or ":nexus_fade_home" not in smali:
        errors.append("r.smali: tab dispatch labels missing")
    if ("invoke-direct {p0}, Landroid/ext/r;->nexusApplyTab()V\n\n"
            "    invoke-direct {p0}, Landroid/ext/r;->nexusPowerApply()V\n\n"
            "    invoke-direct {p0}, Landroid/ext/r;->nexusEnv()V\n\n"
            "    invoke-super {p0}, La/a;->onPostResume()V") not in smali:
        errors.append("r.smali: hooks must sit in onPostResume AFTER y(true)")
    if ON_PAUSE_NEW not in smali:
        errors.append("r.smali: onPause float-show guard missing")
    if ON_PAUSE_ANCHOR in smali:
        errors.append("r.smali: onPause e1() is still unguarded")
    if RESUME_ANCHOR in smali:
        errors.append("r.smali: onResume still stops the float (g1) — unfixed")
    if RESUME_NEW not in smali:
        errors.append("r.smali: onResume float-neutered block missing")
    if "invoke-direct {p0}, Landroid/ext/r;->nexusApplyTab()V\n\n    invoke-direct {p0}, Landroid/ext/r;->nexusPowerApply()V\n\n    :goto_1" in smali:
        errors.append("r.smali: hooks must NOT be in onResume (onPostResume re-inflates after it)")
    if ".field public static nexusTab:I" not in smali:
        errors.append("r.smali: nexusTab static field missing")
    if ".field public static nexusPower:Z" not in smali:
        errors.append("r.smali: nexusPower static field missing")
    if smali.count("sput-boolean v1, Landroid/ext/r;->nexusPower:Z") != 1:
        errors.append("r.smali: power card must toggle the nexusPower flag")
    if ".method protected onRestoreInstanceState(Landroid/os/Bundle;)V" in smali:
        errors.append("r.smali: onRestoreInstanceState should be gone (in-memory tab only)")
    if "nexusPowerRefresh" in smali:
        errors.append("r.smali: nexusPowerRefresh is superseded by nexusPowerApply")
    if Z_ANCHOR in smali or Z_NEW not in smali:
        errors.append("r.smali: z() hooks missing")
    if smali.count("sput v0, Landroid/ext/r;->nexusTab:I") != 3:
        errors.append("r.smali: expected 3 tab-save sput writes")
    if smali.count("const/16 v1, 0xF") != 1:
        errors.append("r.smali: button count not updated to 0xF for 15-entry array")
    if smali.count("0x7f050166") < 1:
        errors.append("r.smali: power card id 0x7f050166 not present")
    for _id in ("0x7f05016c", "0x7f05016d", "0x7f05016e",
                "0x7f05016f", "0x7f050170", "0x7f050171",
                "0x7f050172", "0x7f050173", "0x7f050174"):
        # 3x, one per tab inside nexusApplyTab(). The tap cases no longer inline
        # a second copy of the body, so these ids are emitted exactly once each.
        if smali.count(_id) != 3:
            errors.append(f"r.smali: id {_id} appears {smali.count(_id)}x (expected 3x: one per tab in nexusApplyTab)")
    if "@id/nexus_pill_home" not in main or "@id/nexus_lbl_home" not in main:
        errors.append("main.xml: navbar pill structure missing")
    for rel in ["res/values/nexus_colors.xml", "res/drawable/nexus_bg_card.xml",
                "res/drawable/nexus_ic_home.xml", "res/values/nexus_strings.xml",
                "res/values/nexus_styles.xml", "res/drawable/nexus_bg_dialog.xml"]:
        if not (tree / rel).is_file():
            errors.append(f"resource not copied: {rel}")
    if "<style name=\"NexusDialog\"" not in nexus_styles:
        errors.append("nexus_styles.xml: NexusDialog style missing")
    if "<style name=\"NexusDialogButton\"" not in nexus_styles:
        errors.append("nexus_styles.xml: NexusDialogButton style missing")
    if "<style name=\"NexusDialogContentButton\"" not in nexus_styles:
        errors.append("nexus_styles.xml: NexusDialogContentButton style missing")
    if "<item name=\"android:buttonStyle\">" not in nexus_styles:
        errors.append("nexus_styles.xml: android:buttonStyle not set on NexusDialog")
    for _rel in ["res/drawable/nexus_bg_button.xml", "res/drawable/nexus_kbd_background.xml",
                 "res/drawable/nexus_kbd_key.xml", "res/drawable/nexus_kbd_key_pressed.xml",
                 "res/drawable/nexus_kbd_key_normal.xml"]:
        if not (tree / _rel).is_file():
            errors.append(f"resource not copied: {_rel}")

    # download-URL results
    for _rel in ("smali/android/ext/r$n.smali", "smali/android/ext/ShowApp.smali"):
        _t = read(tree, _rel)
        if DOWNLOAD_URL_NEW not in _t:
            errors.append(f"{_rel}: new download URL missing")
        if DOWNLOAD_URL_OLD in _t:
            errors.append(f"{_rel}: old download URL still present")
    if ("#" + DOWNLOAD_URL_NEW) not in smali:
        errors.append("r.smali: commented new download URL missing")
    # MainService$m must be untouched: the old literal is still its index key
    if DOWNLOAD_URL_OLD not in read(tree, "smali/android/ext/MainService$m.smali"):
        errors.append("MainService$m.smali: index-key literal was modified — "
                      "this changes a service-list index and must not be rewritten")

    # keyboard results
    if KBD_LAYOUT_NEW not in read(tree, "res/layout/keyboard.xml"):
        errors.append("keyboard.xml: Nexus background not applied")
    _ks = read(tree, "res/drawable/btn_keyboard_key_lxx_dark.xml")
    if "btn_keyboard_key_" in _ks:
        errors.append("btn_keyboard_key_lxx_dark.xml: GG key PNGs still referenced")
    if "nexus_kbd_key_pressed" not in _ks:
        errors.append("btn_keyboard_key_lxx_dark.xml: Nexus selector not applied")
    if "nexus_kbd_key_normal" not in _ks:
        errors.append("btn_keyboard_key_lxx_dark.xml: normal key state missing")
    # state_activated/state_focused must stay out: InternalKeyboard is
    # focusable, so either would leave a key stuck in the pressed colour.
    if "state_activated" in _ks or "state_focused" in _ks:
        errors.append("btn_keyboard_key_lxx_dark.xml: activated/focused states must not be styled")
    for _rel, _c in (("res/drawable/nexus_kbd_key_normal.xml", "nexus_surface_alt"),
                     ("res/drawable/nexus_kbd_key_pressed.xml", "nexus_surface_high")):
        _t = read(tree, _rel)
        if _c not in _t:
            errors.append(f"{_rel}: expected {_c}")
        if "<corners" in _t:
            errors.append(f"{_rel}: keys must be squared (no <corners>)")
    _bb = read(tree, "res/drawable/nexus_bg_button.xml")
    if "nexus_surface_alt" not in _bb:
        errors.append("nexus_bg_button.xml: must match nexus_kbd_key_normal (nexus_surface_alt)")
    if '<item name="android:backgroundTint">' not in nexus_styles:
        errors.append("nexus_styles.xml: content button backgroundTint not cleared")

    for rel in icon_resource_files():
        if not (tree / rel).is_file():
            errors.append(f"icon not copied: {rel}")
    for item in STYLES_ITEMS:
        if item not in styles:
            errors.append(f"styles.xml: missing {item}")

    # rebrand assertions
    manifest = read(tree, "AndroidManifest.xml")
    if f'package="{PKG_NEW}"' not in manifest:
        errors.append(f"manifest package is not {PKG_NEW}")
    if PKG_OLD in manifest:
        errors.append("manifest still contains com.scmq")
    if 'android:label="Nexus"' not in manifest:
        errors.append("manifest application label is not Nexus")
    if manifest.count('android:label="Game"') != 0:
        errors.append('manifest still has android:label="Game"')
    if manifest.count('android:label="Nexus"') != 3:
        errors.append("manifest expected 3 Nexus labels (app + 2 activities)")
    if manifest.count('android.intent.category.LAUNCHER') != 1:
        errors.append("manifest expected exactly 1 LAUNCHER category")
    if 'android:icon="@mipmap/ic_hw_48dp"' in manifest and 'category.LAUNCHER' in manifest[manifest.index('android:icon="@mipmap/ic_hw_48dp"'):manifest.index('android:icon="@mipmap/ic_hw_48dp"')+400]:
        errors.append("ActivityMain still has a LAUNCHER intent-filter")
    if not (tree / "smali/org/vekendian/nexus/R.smali").is_file():
        errors.append("smali/org/vekendian/nexus/R.smali missing (move failed)")
    if (tree / "smali/com/scmq").exists():
        errors.append("smali/com/scmq still exists (move failed)")
    for root in smali_roots(tree):
        if any(SMALI_OLD in f.read_text(encoding="utf-8")
               for f in root.rglob("*.smali") if f.stat().st_size < 2_000_000):
            errors.append(f"Lcom/scmq/ still present under {root.name}/")
            break
    strings = tree / "res/values/strings.xml"
    if strings.is_file() and APP_NAME_NEW not in strings.read_text(encoding="utf-8"):
        errors.append("strings.xml app_name is not Nexus")
    yml = tree / "apktool.yml"
    if yml.is_file():
        y = yml.read_text(encoding="utf-8")
        if f"versionName: {NEW_VERSION_NAME}" not in y:
            errors.append(f"apktool.yml versionName is not {NEW_VERSION_NAME}")
    return errors


# ------------------------------------------------------------------ apply ---

