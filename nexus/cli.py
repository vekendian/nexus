"""Command-line interface: argument parsing, dispatch, exit codes.

Exit codes:
    0  success / PASS
    1  check failed, or apply aborted (the source tree is never modified)
    2  bad invocation or unusable input (missing tree, bad lock file)
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from .anchors import PatchError, replace_once
from .checks import delta_audits_skipped, is_patched, postflight, preflight
from .ids import KINDS, Ids
from .layout import (GG_SURFACE_LAYOUTS, transform_dialog_empty_state,
                     transform_gg_surface, transform_hot_point,
                     transform_main, transform_searcher_space,
                     transform_service_config, transform_styles,
                     transform_time_jump)
from .luapatch import apply as apply_lua
from .manifest import NEW_VERSION_NAME, rebrand
from .profile import Profile, gg_version_from_tree
from .smali import (CONFIG_ADAPTER, DOWNLOAD_URL_NEW, DOWNLOAD_URL_OLD,
                    KBD_GRAVITY_ANCHOR, KBD_GRAVITY_NEW, KBD_LAYOUT_ANCHOR,
                    KBD_LAYOUT_NEW, KBD_SELECTOR_NEW,
                    ROW_TINT_FILES, transform_config_adapter, transform_dialogs,
                    transform_dialog_builder, transform_empty_views,
                    transform_row_tints,
                    transform_settings_highlight, transform_smali)
from .tree import (LOCK_PATH, OUTPUT_SUFFIX, copy_resources, copy_smali, default_output, detect_version, ui_enabled,
                   ensure_apktool_yml, make_output, read, resolve_tree, write)

TRACK = "smali/android/ext/r.smali"
# GameGuardian's obfuscated Alert helper; method t() is the dialog funnel.
DIALOG_FILE = "smali/android/ext/f.smali"


def _load_ids(tree: Path) -> Ids:
    """Lock file + the tree's public.xml, so GG ids resolve by name."""
    public = tree / "res/values/public.xml"
    return Ids.load(LOCK_PATH,
                    public.read_text(encoding="utf-8") if public.is_file() else None)


def _stages(out: Path) -> str:
    return ("Build:\n"
            f"  bash build.sh --src {out} --out nexus-1.0.0.apk\n"
            "  (run it with `bash` — Android shared storage cannot set the exec bit)")


def transform_public(public: str, ids: Ids) -> str:
    if "</resources>" not in public:
        raise PatchError("public.xml: </resources> missing")
    return public.replace("</resources>", ids.public_id_lines() + "\n</resources>")


def transform_keyboard_layout(layout: str) -> str:
    layout = replace_once(layout, KBD_LAYOUT_ANCHOR, KBD_LAYOUT_NEW,
                          "keyboard background")
    return replace_once(layout, KBD_GRAVITY_ANCHOR, KBD_GRAVITY_NEW,
                        "keyboard centering")


def transform_kbd_selector(xml: str) -> str:
    """Swap GG's 10-item key selector (six 9-patch PNGs per density) for the
    pressed-only Nexus one: resting keys paint nothing, so the dialog surface
    behind the keyboard becomes the keys' background."""
    start, end = xml.find("<selector"), xml.find("</selector>")
    if start == -1 or end == -1:
        raise PatchError("keyboard selector <selector> not found")
    return xml[:start] + KBD_SELECTOR_NEW + xml[end + len("</selector>"):]


# --------------------------------------------------------------- commands ---

def cmd_apply(args) -> int:
    try:
        src = resolve_tree(args.src)
        ids = _load_ids(src)
        profile = Profile.for_release(detect_version(src), getattr(args, 'profile', None))
        out = Path(args.out).expanduser().resolve() if args.out else default_output(src)
        errors = preflight(src, ids, Profile.for_release(detect_version(src)))
    except (PatchError, OSError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    if errors:
        print("PREFLIGHT FAILED — nothing written:")
        for e in errors:
            print(f"  - {e}")
        return 1
    version = detect_version(src)
    try:
        make_output(src, out, args.force)
    except (PatchError, OSError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    try:
        _patch(out, ids, profile)
    except (PatchError, OSError) as e:
        shutil.rmtree(out, ignore_errors=True)
        print(f"APPLY ABORTED: {e}", file=sys.stderr)
        print(f"Partial output removed; {src} was not touched.", file=sys.stderr)
        return 1
    post = postflight(out, ids, src)
    if post:
        print(f"POSTFLIGHT FAILED (output kept for inspection: {out}):")
        for e in post:
            print(f"  - {e}")
        return 1
    print(f"APPLIED OK — GG {version}")
    print(f"Source (untouched): {src}")
    print(f"Output:             {out}")
    print(_stages(out))
    return 0


def _patch(tree: Path, ids: Ids, profile) -> None:
    """Apply every edit to ``tree`` (always the output copy, never the source)."""
    ensure_apktool_yml(tree)
    copy_resources(tree)
    write(tree, "res/values/public.xml",
          transform_public(read(tree, "res/values/public.xml"), ids))
    if not ui_enabled():
        # Everything below edits a file GG owns. Skipping all of it leaves a
        # rebranded GG that still has its own UI, which is the only build that
        # can separate "the UI injection" from "everything else".
        rebrand(tree)
        copy_smali(tree)
        return
    write(tree, "res/values/styles.xml",
          transform_styles(read(tree, "res/values/styles.xml")))
    write(tree, profile.layout("main"),
          transform_main(read(tree, profile.layout("main")), NEW_VERSION_NAME))
    write(tree, profile.file("main_activity"),
          transform_smali(read(tree, profile.file("main_activity")), ids))
    # Dialog chrome. android/ext/f.smali method t() is the one funnel every
    # GG dialog reaches, so this is a single edit rather than a theme item.
    dh = read(tree, profile.file("dialog_helper"))
    dh = transform_dialogs(dh, ids)
    dh = transform_dialog_builder(dh)
    write(tree, profile.file("dialog_helper"), dh)
    # Settings screen: orange section bands, no donate row, and the "this
    # setting is on" highlight retinted from GG's yellow to Nexus orange.
    write(tree, profile.layout("service_config"),
          transform_service_config(
              read(tree, profile.layout("service_config")),
              profile.count("separator_bands")))
    # Floating interface: the icon and the time-jump panel that sit over a
    # game screen. GG's own layouts, restyled in place.
    write(tree, profile.layout("hot_point_view"),
          transform_hot_point(read(tree, profile.layout("hot_point_view"))))
    write(tree, profile.layout("time_jump_panel"),
          transform_time_jump(read(tree, profile.layout("time_jump_panel"))))
    # The search and value-changed dialogs' spacing pass. The surface recolour
    # below this only carries colours, so the two passes never undo each other.
    write(tree, profile.layout("service_searcher"),
          transform_searcher_space(read(tree, profile.layout("service_searcher"))))
    config_adapter = transform_settings_highlight(read(tree, profile.file("config_adapter")))
    config_adapter = transform_config_adapter(config_adapter, ids)
    write(tree, profile.file("config_adapter"), config_adapter)
    # The same "this row is marked" tint, in the two places that mark rows
    # outside the settings list.
    for rel in profile.files_list("row_tints"):
        write(tree, rel, transform_row_tints(read(tree, rel), rel))
    # Download URL rewrite across the three sites that actually display/open
    # it. r$n/ShowApp carry it bare; r.smali carries it Lua-commented ("#...").
    for rel in profile.files_list("url_sites"):
        t = read(tree, rel)
        n = t.count(DOWNLOAD_URL_OLD)
        if n != 1:
            raise PatchError(f"{rel}: expected 1 download-URL literal, found {n}")
        write(tree, rel, t.replace(DOWNLOAD_URL_OLD, DOWNLOAD_URL_NEW))
    rt = read(tree, profile.file("main_activity"))
    if rt.count("#" + DOWNLOAD_URL_OLD) != 1:
        raise PatchError("r.smali: expected 1 commented download-URL literal")
    write(tree, profile.file("main_activity"), rt.replace("#" + DOWNLOAD_URL_OLD, "#" + DOWNLOAD_URL_NEW))
    # The tabs' empty states never show: the search tab's nothing-found block
    # and the saved list's "empty list" scroller lose their setEmptyView wiring
    # (the framework toggles them by itself, so the XML would not hold) and are
    # marked gone in the layout. The TextViews inside stay — the startup
    # scramble reads and rewrites their text.
    write(tree, profile.file("main_service"),
          transform_empty_views(read(tree, profile.file("main_service")), ids))
    write(tree, profile.layout("service_dialog"),
          transform_dialog_empty_state(read(tree, profile.layout("service_dialog"))))
    write(tree, profile.layout("keyboard"),
          transform_keyboard_layout(read(tree, profile.layout("keyboard"))))
    write(tree, profile.layout("keyboard_selector"),
          transform_kbd_selector(read(tree, profile.layout("keyboard_selector"))))
    # Every other layout GameGuardian ships: the fields, the horizontal bars
    # and the hardcoded colours in them become the Nexus ones.
    for _rel in GG_SURFACE_LAYOUTS:
        _p = f"res/layout/{_rel}"
        write(tree, _p, transform_gg_surface(read(tree, _p), _rel))
    rebrand(tree)
    # Our own smali classes target the rebranded package, so they land after it.
    copy_smali(tree)
    # Lua namespace: rendered templates plus the one Script.smali call that
    # registers the table. Renders against the lock file, so it must run here
    # (ids are resolved once) and never against a copied template directory.
    apply_lua(tree, ids)


def _source_of(tree: Path) -> Path | None:
    """The unpatched tree a patched output was made from, if it is still there.

    `check` on an output folder needs the original to diff against: the two
    resource-id audits are *deltas* (no id may move, no new unreachable
    findViewById may appear), because GG's own code has lookups that legitimately
    miss. With no source to diff against those audits cannot run, so they are
    skipped rather than reported as clean.
    """
    if not tree.name.endswith(OUTPUT_SUFFIX):
        return None
    src = tree.with_name(tree.name[: -len(OUTPUT_SUFFIX)])
    return src if src.is_dir() else None


def cmd_check(args) -> int:
    try:
        tree = resolve_tree(args.src)
        ids = _load_ids(tree)
    except PatchError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    if is_patched(tree):
        src = _source_of(tree)
        errors, label = postflight(tree, ids, src), "POSTFLIGHT"
        state = "patched tree"
        if delta_audits_skipped(src):
            state += " (delta audits SKIPPED: source tree not found)"
    else:
        errors, label = preflight(tree, ids), "PREFLIGHT"
        state = "unpatched tree"
    print(f"{label} (GG {detect_version(tree)}, {state})")
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS")
    return 0


def cmd_ids(args) -> int:
    try:
        tree = resolve_tree(args.src)
        ids = _load_ids(tree)
    except PatchError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    print(f"ID lock file: {LOCK_PATH}")
    print(f"GG release recorded: {ids.data.get('gg_release')}   tree: {detect_version(tree)}")
    for kind in KINDS:
        table = ids.nexus.get(kind, {})
        print(f"\nNexus {kind} ids ({len(table)}):")
        for name, hexval in sorted(table.items(), key=lambda kv: int(kv[1], 16)):
            print(f"  {hexval}  {name}")
    print("\nGameGuardian bindings (resolved by name from public.xml):")
    bad = 0
    for name, recorded in sorted(ids.gg_observed.items()):
        try:
            got = ids.gg(name)
        except PatchError:
            print(f"  MISSING  {name} (recorded {recorded})")
            bad += 1
            continue
        flag = "" if got == recorded else f"   <- moved from {recorded}"
        print(f"  {got}  {name}{flag}")
    # On a patched tree the Nexus ids are already IN public.xml, so a collision
    # report would just be listing the patch's own output. Only meaningful on
    # an unpatched tree, where a collision means GG started using our ids.
    patched = is_patched(tree)
    if patched:
        print("\n(tree is patched — skipping the collision check, which would "
              "only list Nexus's own additions)")
        collisions = []
    else:
        collisions = ids.audit_collisions(read(tree, "res/values/public.xml"))
        if collisions:
            print("\nCollisions:")
            for c in collisions:
                print(f"  - {c}")
    drift = ids.drift()
    if drift:
        print("\nDrift vs the recorded lock (expected on a new GG release; not fatal):")
        for name, got, was in drift:
            print(f"  - {name}: {was} -> {got}")
    return 1 if (bad or collisions) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="nexus.py",
        description="Bring-your-own-GameGuardian patcher. decode -> check -> "
                    "apply -> build.sh -> install.")
    ap.add_argument("command", choices=["check", "apply", "ids"],
                    help="check: verify anchors/ids. apply: write a patched "
                         "COPY to <tree>_nexus_output (source untouched). "
                         "ids: show the ID lock file and audit it.")
    ap.add_argument("--src", required=True, help="apktool-decoded GG tree")
    ap.add_argument("--out", help="apply only: output folder "
                    "(default: <tree>_nexus_output, next to the source)")
    ap.add_argument("--force", action="store_true",
                    help="apply only: replace an existing output folder")
    args = ap.parse_args(argv)
    return {"check": cmd_check, "apply": cmd_apply,
            "ids": cmd_ids}[args.command](args)