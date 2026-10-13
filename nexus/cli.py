"""Command-line interface: argument parsing, dispatch, exit codes.

Exit codes:
    0  success / PASS
    1  check failed, or apply aborted (the source tree is never modified)
    2  bad invocation or unusable input (missing tree, bad lock file)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .anchors import PatchError, replace_once
from .checks import is_patched, postflight, preflight
from .ids import Ids
from .layout import transform_main, transform_service_config
from .manifest import NEW_VERSION_NAME, rebrand
from .smali import (CONFIG_ADAPTER, DOWNLOAD_URL_NEW, DOWNLOAD_URL_OLD,
                    KBD_LAYOUT_ANCHOR, KBD_LAYOUT_NEW, KBD_SELECTOR_NEW,
                    transform_dialogs, transform_settings_highlight,
                    transform_smali)
from .tree import (LOCK_PATH, copy_resources, default_output, detect_version,
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


def transform_styles(styles: str) -> str:
    return replace_once(styles,
                        '        <item name="android:windowActionBar">false</item>',
                        '''        <item name="android:windowActionBar">false</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:windowBackground">@color/nexus_bg</item>
        <item name="android:statusBarColor">@color/nexus_bg</item>
        <item name="android:navigationBarColor">@color/nexus_surface</item>
        <item name="android:alertDialogTheme">@style/NexusDialog</item>
        <item name="android:dialogTheme">@style/NexusDialog</item>
        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>''',
                        "styles windowActionBar")


def transform_keyboard_layout(layout: str) -> str:
    return replace_once(layout, KBD_LAYOUT_ANCHOR, KBD_LAYOUT_NEW, "keyboard background")


def transform_kbd_selector(xml: str) -> str:
    """Swap GG's 10-item key selector (six 9-patch PNGs per density) for the
    two-state Nexus one."""
    start, end = xml.find("<selector"), xml.find("</selector>")
    if start == -1 or end == -1:
        raise PatchError("keyboard selector <selector> not found")
    return xml[:start] + KBD_SELECTOR_NEW + xml[end + len("</selector>"):]


# --------------------------------------------------------------- commands ---

def cmd_apply(args) -> int:
    try:
        src = resolve_tree(args.src)
        ids = _load_ids(src)
        out = Path(args.out).expanduser().resolve() if args.out else default_output(src)
        errors = preflight(src, ids)
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
        _patch(out, ids)
    except (PatchError, OSError) as e:
        shutil.rmtree(out, ignore_errors=True)
        print(f"APPLY ABORTED: {e}", file=sys.stderr)
        print(f"Partial output removed; {src} was not touched.", file=sys.stderr)
        return 1
    post = postflight(out, ids)
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


def _patch(tree: Path, ids: Ids) -> None:
    """Apply every edit to ``tree`` (always the output copy, never the source)."""
    ensure_apktool_yml(tree)
    copy_resources(tree)
    write(tree, "res/values/public.xml",
          transform_public(read(tree, "res/values/public.xml"), ids))
    write(tree, "res/values/styles.xml",
          transform_styles(read(tree, "res/values/styles.xml")))
    write(tree, "res/layout/main.xml",
          transform_main(read(tree, "res/layout/main.xml"), NEW_VERSION_NAME))
    write(tree, TRACK, transform_smali(read(tree, TRACK), ids))
    # Dialog chrome. android/ext/f.smali method t() is the one funnel every
    # GG dialog reaches, so this is a single edit rather than a theme item.
    write(tree, DIALOG_FILE, transform_dialogs(read(tree, DIALOG_FILE), ids))
    # Settings screen: orange section bands, no donate row, and the "this
    # setting is on" highlight retinted from GG's yellow to Nexus orange.
    write(tree, "res/layout/service_config.xml",
          transform_service_config(read(tree, "res/layout/service_config.xml")))
    write(tree, CONFIG_ADAPTER,
          transform_settings_highlight(read(tree, CONFIG_ADAPTER)))
    # Download URL rewrite across the three sites that actually display/open
    # it. r$n/ShowApp carry it bare; r.smali carries it Lua-commented ("#...").
    for rel in ("smali/android/ext/r$n.smali", "smali/android/ext/ShowApp.smali"):
        t = read(tree, rel)
        n = t.count(DOWNLOAD_URL_OLD)
        if n != 1:
            raise PatchError(f"{rel}: expected 1 download-URL literal, found {n}")
        write(tree, rel, t.replace(DOWNLOAD_URL_OLD, DOWNLOAD_URL_NEW))
    rt = read(tree, TRACK)
    if rt.count("#" + DOWNLOAD_URL_OLD) != 1:
        raise PatchError("r.smali: expected 1 commented download-URL literal")
    write(tree, TRACK, rt.replace("#" + DOWNLOAD_URL_OLD, "#" + DOWNLOAD_URL_NEW))
    write(tree, "res/layout/keyboard.xml",
          transform_keyboard_layout(read(tree, "res/layout/keyboard.xml")))
    write(tree, "res/drawable/btn_keyboard_key_lxx_dark.xml",
          transform_kbd_selector(read(tree, "res/drawable/btn_keyboard_key_lxx_dark.xml")))
    rebrand(tree)


def cmd_check(args) -> int:
    try:
        tree = resolve_tree(args.src)
        ids = _load_ids(tree)
    except PatchError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    if is_patched(tree):
        errors, label = postflight(tree, ids), "POSTFLIGHT"
        state = "patched tree"
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
    for kind in ("id", "drawable", "layout", "string"):
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