"""Command-line interface: argument parsing, dispatch, exit codes.

Exit codes:
    0  success / PASS
    1  check failed, or apply aborted (tree left recoverable via `revert`)
    2  bad invocation or unusable input (missing tree, bad lock file)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .anchors import PatchError, replace_once
from .checks import is_patched, postflight, preflight
from .ids import Ids
from .layout import transform_main
from .manifest import NEW_VERSION_NAME, rebrand, unrebrand
from .smali import (DOWNLOAD_URL_NEW, DOWNLOAD_URL_OLD, KBD_LAYOUT_ANCHOR,
                    KBD_LAYOUT_NEW, KBD_SELECTOR_NEW, transform_smali)
from .tree import (BACKUP_DIR, LOCK_PATH, RES_DIR, backup, copy_resources,
                   detect_version, ensure_apktool_yml, read, resolve_tree,
                   restore_backup, write)

TRACK = "smali/android/ext/r.smali"


def _load_ids(tree: Path) -> Ids:
    """Lock file + the tree's public.xml, so GG ids resolve by name."""
    public = tree / "res/values/public.xml"
    return Ids.load(LOCK_PATH,
                    public.read_text(encoding="utf-8") if public.is_file() else None)


def _stages() -> str:
    return ("Build:\n"
            "  bash build.sh --src <tree> --out nexus-1.0.0.apk\n"
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
        tree = resolve_tree(args.src)
        ids = _load_ids(tree)
    except PatchError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    errors = preflight(tree, ids)
    if errors:
        print("PREFLIGHT FAILED — tree untouched:")
        for e in errors:
            print(f"  - {e}")
        return 1
    version = detect_version(tree)
    try:
        ensure_apktool_yml(tree)
        backup(tree)
        copy_resources(tree)
        write(tree, "res/values/public.xml",
              transform_public(read(tree, "res/values/public.xml"), ids))
        write(tree, "res/values/styles.xml",
              transform_styles(read(tree, "res/values/styles.xml")))
        write(tree, "res/layout/main.xml",
              transform_main(read(tree, "res/layout/main.xml"), NEW_VERSION_NAME))
        write(tree, TRACK, transform_smali(read(tree, TRACK), ids))
        # Download URL rewrite across the three sites that actually display/open
        # it. r$n/ShowApp carry it bare; r.smali carries it Lua-commented ("#...").
        for rel in ("smali/android/ext/r$n.smali", "smali/android/ext/ShowApp.smali"):
            f = tree / rel
            t = f.read_text(encoding="utf-8")
            n = t.count(DOWNLOAD_URL_OLD)
            if n != 1:
                raise PatchError(f"{rel}: expected 1 download-URL literal, found {n}")
            f.write_text(t.replace(DOWNLOAD_URL_OLD, DOWNLOAD_URL_NEW), encoding="utf-8")
        r = tree / TRACK
        rt = r.read_text(encoding="utf-8")
        if rt.count("#" + DOWNLOAD_URL_OLD) != 1:
            raise PatchError("r.smali: expected 1 commented download-URL literal")
        r.write_text(rt.replace("#" + DOWNLOAD_URL_OLD, "#" + DOWNLOAD_URL_NEW),
                     encoding="utf-8")
        write(tree, "res/layout/keyboard.xml",
              transform_keyboard_layout(read(tree, "res/layout/keyboard.xml")))
        write(tree, "res/drawable/btn_keyboard_key_lxx_dark.xml",
              transform_kbd_selector(read(tree, "res/drawable/btn_keyboard_key_lxx_dark.xml")))
        rebrand(tree)
    except PatchError as e:
        print(f"APPLY ABORTED mid-edit: {e}", file=sys.stderr)
        print(f"Restore with: {Path(sys.argv[0]).name} revert --src {tree}", file=sys.stderr)
        return 1
    post = postflight(tree, ids)
    if post:
        print("POSTFLIGHT FAILED (files written, backup kept):")
        for e in post:
            print(f"  - {e}")
        return 1
    print(f"APPLIED OK — GG {version}, 4 files patched + nexus_* resources copied.")
    print(f"Backup: {tree / BACKUP_DIR}")
    print("Build:")
    print(_stages())
    return 0


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


def cmd_revert(args) -> int:
    try:
        tree = resolve_tree(args.src)
    except PatchError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 2
    bdir = tree / BACKUP_DIR
    if not bdir.is_dir():
        print("no backup found — nothing to revert", file=sys.stderr)
        return 1
    try:
        restore_backup(tree)
    except PatchError as e:
        print(f"REVERT FAILED: {e}", file=sys.stderr)
        return 1
    unrebrand(tree)
    if (RES_DIR / "res").is_dir():
        import shutil
        for src in (RES_DIR / "res").rglob("*"):
            if src.is_file():
                dst = tree / "res" / src.relative_to(RES_DIR / "res")
                if dst.is_file():
                    dst.unlink()
    shutil.rmtree(bdir)
    print("REVERTED — main.xml/public.xml/styles.xml/r.smali restored, "
          "nexus_* resources removed")
    return _verify_revert(tree)


def _verify_revert(tree: Path) -> int:
    """Catch a revert that reported success but left Nexus markers behind.

    An earlier version restored only MODIFIED_FILES and printed REVERTED while
    the tree still carried edits made outside that list. Scanning afterwards
    turns that silent partial state into a visible failure.
    """
    from .tree import MODIFIED_FILES
    stray = []
    for path in sorted((tree / "res/layout").glob("*.xml")):
        rel = f"res/layout/{path.name}"
        if rel in MODIFIED_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if 'style="@style/NexusRow"' in text or 'style="@style/NexusButton"' in text:
            stray.append(rel)
    for path in sorted((tree / "res/drawable").glob("nexus_*.xml")):
        rel = f"res/drawable/{path.name}"
        if rel not in MODIFIED_FILES and not (RES_DIR / rel).is_file():
            stray.append(rel)
    if stray:
        print("WARNING — revert reported success but these files still look patched:",
              file=sys.stderr)
        for rel in stray:
            print(f"  - {rel}", file=sys.stderr)
        print("Restore them from the tree's own pristine copy, then re-check.",
              file=sys.stderr)
        return 1
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
    for kind in ("id", "drawable", "string"):
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
    ap.add_argument("command", choices=["check", "apply", "revert", "ids"],
                    help="check: verify anchors/ids. apply: patch the tree. "
                         "revert: restore from backup. ids: show the ID lock "
                         "file and audit it against the tree.")
    ap.add_argument("--src", required=True, help="apktool-decoded GG tree")
    args = ap.parse_args(argv)
    return {"check": cmd_check, "apply": cmd_apply,
            "revert": cmd_revert, "ids": cmd_ids}[args.command](args)