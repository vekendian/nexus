# Nexus UX truthfulness, design system, float redesign, and release portability

**Date:** 2026-10-21
**Status:** approved, in progress
**Decisions:** UX first, portability last. Float = full visual redesign, no GG
smali changes. Allow/Ask = two buttons, corrected semantics. Every GG surface
pulled into the Nexus look.

Repo `/mnt/sdcard/#Vekendian/nexus/nexus`; GG tree
`/mnt/sdcard/#Vekendian/nexus/gameguardian/101.4/Kujtnodnookc_499.2_src`;
design source of truth `/mnt/sdcard/#Vekendian/nexus/nexus_ref`.

---

## Why

Six defects, each confirmed in the code:

1. **The "Stop modules" row stops every module.** `nexus/layout.py:527-532` reuses
   the *permission capability* string `nexus_str_perm_stop` ("Stop modules") for a
   settings action that calls `NexusHost.stopModules` -> `executor.stopAll()`
   -> stops every record, unfiltered, with no confirmation. The same literal is
   also the permissions-dialog capability for letting a script stop *one*
   module. Its sibling "Run autostart" is not symmetric: it starts only modules
   whose author set `autostart = true` - a flag with no UI anywhere. The only
   accurate description in the app is the toast: "All modules stopped".
2. **The Allow/Ask chooser points its colour the wrong way.**
   `NexusHost.java:541-553` marks the in-effect option `setSelected(true)`, so
   it gets an orange *fill* with a dark `nexus_on_orange` *label* (reads dim),
   while the inactive option gets a grey fill with a bright orange label (reads
   active). Neither selector has a `state_enabled` item, so the
   `setEnabled(!on)` inversion is invisible. There is no check, no bold, no
   switch - two plain buttons whose only state cue is a hue that lies. Orange
   also means "emphasised action" elsewhere in the same dialog.
3. **The patcher is welded to one GG release.** 112 GG-specific literals in
   `nexus/checks.py`, 111 in `nexus/smali.py`. `smali.py:40-49,70-82` embed GG's
   view id hexes literally, defeating the name resolution in `ids.py:104-116`:
   a renumbered release dies with "anchor found 0x (expected exactly 1x)".
   `ids.audit_gg_bindings()` exists but is test-only. Pin headroom is one slot.
   `apicheck.py` skips GG classes, so a renamed obfuscated member fails at
   runtime, not build time.
4. **The visual system is inconsistent.** No `android:colorAccent` in
   `FixTheme`, so every bar and spinner outside the float is platform blue.
   Nexus's own toasts are stock Android. Nine corner radii, `dp`/`dip` mixed,
   three ripple alphas, four dead colour tokens, GG's purple/olive row tints
   still in `b3.smali`.
5. **The float is a recolour.** `nexus/layout.py:698+` swaps backgrounds and
   tints on GG's views. No geometry, no elevation, square-ended stock bars.
6. **Plus twenty-odd further defects** found during the audit (module status
   has no state colour, autostart invisible, the destructive global stop is
   the least marked control in the group, the module picker opens stock
   DocumentsUI, the FAB "+" is white on orange where everything else uses
   `nexus_on_orange`, five oranges in play, seven text sizes in `main.xml`,
   and `checks.py` reads `_scx` in the wrong branch so a missing
   `service_config.xml` raises `NameError` instead of reporting).

---

## W0 - Make the UI tell the truth

| # | Change | Where |
|---|---|---|
| 0.1 | New strings: `nexus_str_modules_stop_all` "Stop all modules", `nexus_str_modules_run_autostart` "Start autostart modules"; capability labels become single-module scope ("Run a module", "Stop a module", "Install a module", "Remove a module") so the literal "Stop modules" stops meaning two things | `nexus/layout.py:520-532`, `nexus/modules.py:206-230`, `resources/res/values/nexus_strings.xml:70,85-89` |
| 0.2 | Confirm before the global stop (reuse the remove-module confirm pattern) | `NexusHost.java:823-835`, new delegate in `nexus/modules.py`, new case in `nexus/smali.py:1320-1391` |
| 0.3 | Show the autostart flag on the module card; colour the status line with the unused `nexus_ok`/`nexus_bad` | `resources/res/layout/nexus_module_card.xml`, `ModuleCards.java:59-68`, `NexusHost.java:706-755` |
| 0.4 | Allow/Ask rebuild: in-effect = orange fill + `nexus_on_orange` label + check glyph; not-in-effect = surface fill + `nexus_text`; footer actions use `nexus_bg_button` + `nexus_text`. Orange then means only "active" | `NexusHost.java:518-553`, `resources/res/color/nexus_choice_text.xml`, `resources/res/drawable/nexus_bg_choice.xml`, port `nexus_ic_check` from the ref |
| 0.5 | Relabel the permissions dialog "Default access for all scripts" and mark rows where a script has its own stored choice (the global grant currently misreports a script that holds "Always allow") | `PermRules.java:55-85`, `LuaPerms.java:38-57` |
| 0.6 | Fix the `_scx` `NameError` (postflight must report, not crash) and add a regression test | `nexus/checks.py:486-542` |
| 0.7 | Call `ids.audit_gg_bindings()` in preflight so a renamed GG view fails at `check`, not `apply` | `nexus/ids.py:143-149`, `nexus/checks.py` |

Verify: `pytest tests/`; new tests - no two scopes share a label literal;
confirm-dialog dispatch; Allow/Ask state semantics; postflight on a tree
missing `service_config.xml` returns errors instead of raising.

---

## W1 - One design system

| # | Change | Where |
|---|---|---|
| 1.1 | Port the ref's missing primitives: `nexus_bg_toast`, `nexus_bg_btn_primary/tonal/text` (16dp + ripple), `nexus_bg_track`/`nexus_bg_fill` (3dp rounded), `nexus_ic_check`, the ref's dialog surface (`nexus_surface_high` + 1dp `nexus_surface_alt` stroke, 28dp) | new files in `resources/res/drawable/` |
| 1.2 | One scale: radii {8, 16, 28}dp, text {12, 13, 15, 18, 28}sp, one ripple alpha, `dp` everywhere, one orange family | `resources/res/**` |
| 1.3 | `android:colorAccent` = `nexus_orange` in `FixTheme` | tree `res/values/styles.xml:18-23` |
| 1.4 | Nexus toast for Nexus's own toasts (surface + 1dp stroke, 26dp, status dot, 14sp, elevation) | `NexusHost.java:249,392,634`, `HostApi.java:53,60` |
| 1.5 | Kill the leaks: `b3.smali:185,194` purple/olive row tints -> orange; raw hex in the tree's `styles.xml` -> tokens; nav Home tint mismatch (`main.xml:445` vs `:479,:514`); FAB "+" white -> `nexus_on_orange`; `nexus_bg_ring_on` raw hex -> `nexus_indicator`; `r.smali`'s hardcoded colour constants resolved from the token table at build time | as cited |
| 1.6 | Delete or wire the dead resources (`nexus_bg_card`, `nexus_kbd_key`); collapse `nexus_bg_pill` == `nexus_bg_primary` | `resources/res/drawable/`, `nexus/checks.py` |
| 1.7 | **The guardrail:** `tests/test_design_system.py` - no raw hex outside an allowlist, radii on the scale, no `dip`, every colour token used, every drawable referenced, one orange family | new test |

---

## W2 - Floating interface redesign

Visual only. GG's view ids and class names stay exactly as they are; no GG
smali is touched.

| # | Change |
|---|---|
| 2.1 | Design the float as one rounded card (16dp, `nexus_surface`, 1dp divider, elevation 8dp) in the same language as the main screen: rounded 3dp track/fill bars at 6dp, a readout chip with the percentage in `nexus_orange` on `nexus_text`, a time-jump panel of two tonal buttons (16dp), 48dp targets with ripple |
| 2.2 | **Mock-render 2-3 variants offline** (Pillow; no SDK on this host) over a game frame, and pick one before anything ships |
| 2.3 | Implement the chosen variant in `transform_hot_point`/`transform_time_jump`; keep every id (`hot_frame`, `hot_point_icon`, `speed_dec/inc`, `progress_bar`, `progress_bar_stage`, `progress_bar_text`, `speed_text`, `time_jump`, `time_jump_last`) |

---

## W3 - Every GG surface in the Nexus look

47 GG layouts, 5 touched today. No layout declares `android:theme`; the app
theme is `FixTheme` and dialogs inherit `DarkAlertDialog`, so the palette moves
globally and the busy surfaces get hand treatment.

| # | Change |
|---|---|
| 3.1 | Global token swap in the tree's `res/values/styles.xml`: `MediumText`/`SmallText`/`LargeText`/`ListItemText` -> `nexus_text`/`nexus_text2`; `Separator` -> `nexus_text2`; `DarkAlertDialog` -> `@drawable/nexus_bg_dialog`; `FixTheme` gets `colorAccent` |
| 3.2 | Family transforms across all 47 layouts: 9 ProgressBars -> Nexus track/fill; 45 EditTexts -> Nexus field surface, `nexus_text`, hint colour; 17 raw-hex backgrounds -> tokens; the 8 row layouts (`service_memory_item`, `service_saved_item`, `service_address_item`, `path_item`, `history_item`, `timer_row`, `prompt_item`, `select_dialog_item`) -> Nexus row surface, consistent padding, ripple |
| 3.3 | Hand-treatment of the surfaces users actually see: `service_dialog` (search/saved/memory overlay - tab bar, counters, rows, backdrop), `service_config` (the float settings panel, which today has no background at all), `service_editor`, `service_filter_search`, `service_offset`, `service_searcher`, `memory_range`, `path_selector`, `service_busy_dialog` |
| 3.4 | GG's *content* colours stay (`pointer_*`, `daemon_*`, `address`/`alert` - Lua and log syntax highlighting). They are data, not chrome. |
| 3.5 | Postflight family assertions: no raw hex left in GG layouts outside the allowlist, no stock-blue bars, every GG dialog on the Nexus surface |

Risk: these 47 layouts change with every GG release, so the family transforms
must be anchor-based and fail loudly. W4 is what stops them being rewritten by
hand each week.

---

## W4 - Release portability (last)

| # | Change |
|---|---|
| 4.1 | `profiles/gg-<version>.json` (package, app name, file paths, layout paths, element ids, GG id bindings by name, count expectations, literal anchors, obfuscated member signatures, icon buckets, URL scheme) + `nexus/profile.py` |
| 4.2 | Anchors become templates resolved from `ids.gg(name)` - the measured counterfactual: today `smali.py:40-49,70-82` embed GG's id hexes literally, so a renumbered release dies with "anchor found 0x"; templated, it patches |
| 4.3 | Move the Nexus pins out of GG's growth zone (`0x7f05f000+`, `0x7f06f000`, `0x7f08f000`) - headroom is one slot today |
| 4.4 | Extend `apicheck` to resolve GG classes, so a renamed obfuscated member fails at build time instead of runtime |
| 4.5 | Split `nexus_ids.json` into global Nexus pins + per-profile GG bindings; call `audit_gg_bindings()` in preflight |
| 4.6 | Profile tests: a synthetic renumbered tree patches cleanly; a synthetic renamed view fails at preflight; a "port to a new GG release" runbook |

---

## Standing rules

1. One source of truth for colour (`nexus_colors.xml`); no raw hex anywhere;
   smali constants resolved from the table.
2. One source of truth for text (`nexus_strings.xml`); every label names what it
   does **and its scope**; no literal shared by two scopes (enforced by a test).
3. Every destructive action confirms first.
4. Anything communicated by colour is also communicated by shape, fill or
   position - and the reverse. Orange means one thing: *active*.

## What cannot be verified from here

The device is `unauthorized` over adb and there is no Android SDK on this host,
so no pixel of the result can be seen from here. The loop is: offline mock
renders -> install -> screenshots. Everything else is verified by tests and
`aapt2` inspection of the compiled APK. No screen is called "looking right"
without a screenshot.
