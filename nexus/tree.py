"""Locating, reading, writing, backing up and reverting an apktool tree."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from .anchors import PatchError

PATCHER_DIR = Path(__file__).resolve().parent.parent
RES_DIR = PATCHER_DIR / "resources"
LOCK_PATH = PATCHER_DIR / "nexus_ids.json"
BACKUP_DIR = ".nexus_backup"

# Overridable so the patcher is not welded to one device's paths.
ICON_SRC = Path(os.environ.get("NEXUS_ICON", "/storage/emulated/0/#Vekendian/nexus/icon.png"))
APKTOOL = os.environ.get("NEXUS_APKTOOL",
                         "/storage/emulated/0/#Vekendian/old_nexus_for_ref/patcher/tools/apktool-2.8.1.jar")
AAPT = os.environ.get("NEXUS_AAPT", "/usr/bin/aapt2")

# Files this patcher rewrites. revert() restores exactly this set, then removes
# the resources it copied. Anything outside this list is untouched.
MODIFIED_FILES = [
    "res/layout/main.xml",
    "res/values/public.xml",
    "res/values/styles.xml",
    "smali/android/ext/r.smali",
    "AndroidManifest.xml",
    "res/values/strings.xml",
    "apktool.yml",
    # download-URL rewrite (see smali.nexus_encode_url) — restored on revert
    "smali/android/ext/r$n.smali",
    "smali/android/ext/ShowApp.smali",
    # keyboard restyle
    "res/layout/keyboard.xml",
    "res/drawable/btn_keyboard_key_lxx_dark.xml",
]

ICON_BUCKETS = {
    "drawable": {"ldpi-v21": 36, "mdpi-v21": 48, "v21": 48, "hdpi-v21": 72,
                 "xhdpi-v21": 96, "xxhdpi-v21": 144, "xxxhdpi-v21": 192},
    "mipmap": {"ldpi-v21": 36, "mdpi-v21": 48, "v21": 48, "hdpi-v21": 72,
               "xhdpi-v21": 96, "xxhdpi-v21": 144, "xxxhdpi-v21": 192},
}
ICON_NAMES = {
    "drawable": ["ic_gg_48dp.png"],
    "mipmap": ["ic_sw_48dp.png", "ic_hw_48dp.png"],
}


def icon_resource_files() -> list:
    out = []
    for family, buckets in ICON_BUCKETS.items():
        for bucket in buckets:
            for name in ICON_NAMES[family]:
                out.append(f"res/{family}-{bucket}/{name}")
    return out


def resolve_tree(src: str) -> Path:
    tree = Path(src).expanduser().resolve()
    if not tree.is_dir():
        raise PatchError(f"tree not found: {tree}")
    if not (tree / "apktool.yml").is_file():
        raise PatchError(f"not an apktool decode (no apktool.yml): {tree}")
    return tree


def read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def write(tree: Path, rel: str, text: str) -> None:
    (tree / rel).write_text(text, encoding="utf-8")


def smali_roots(tree: Path) -> list:
    return [tree / "smali"] + sorted(p for p in (tree / "smali_classes2").glob("*")
                                    if p.is_dir())


def detect_version(tree: Path) -> str:
    """Best-effort GG version for display: apktool.json, then .yml, then manifest.

    Only used for human-readable output and the lock file's drift note, so it
    degrades to "unknown" rather than raising.
    """
    j = tree / "apktool.json"
    if j.is_file():
        m = re.search(r'"versionName":\s*"([^"]+)"', j.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    yml = tree / "apktool.yml"
    if yml.is_file():
        m = re.search(r"versionName:\s*['\"]?([^\s'\"]+)",
                      yml.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    manifest = tree / "AndroidManifest.xml"
    if manifest.is_file():
        m = re.search(r'android:versionName="([^"]+)"',
                      manifest.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return "unknown"


def backup(tree: Path) -> None:
    bdir = tree / BACKUP_DIR
    bdir.mkdir(exist_ok=True)
    for rel in MODIFIED_FILES:
        dst = bdir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():  # keep the first (original) backup
            shutil.copy2(tree / rel, dst)


def copy_resources(tree: Path) -> None:
    shutil.copytree(RES_DIR / "res", tree / "res", dirs_exist_ok=True)


def restore_backup(tree: Path) -> None:
    bdir = tree / BACKUP_DIR
    for rel in MODIFIED_FILES:
        src = bdir / rel
        if not src.is_file():
            raise PatchError(f"backup missing for {rel} — cannot revert cleanly")
    for rel in MODIFIED_FILES:
        shutil.copy2(bdir / rel, tree / rel)

# ---------------------------------------------------------------- helpers ---

def ensure_apktool_yml(tree: Path) -> None:
    """MT Manager trees carry apktool.json, but the apktool CLI needs apktool.yml."""
    yml = tree / "apktool.yml"
    j = tree / "apktool.json"
    if yml.is_file() or not j.is_file():
        return
    import json
    meta = json.loads(j.read_text(encoding="utf-8"))
    pkg = meta.get("PackageInfo", {})
    ver = meta.get("VersionInfo", {})
    lines = [
        "!!brut.androlib.meta.MetaInfo",
        f"apkFileName: {meta.get('apkFileName', 'unknown.apk')}",
        f"isFrameworkApk: {str(meta.get('isFrameworkApk', False)).lower()}",
        f"usesFramework:",
        f"  id: {pkg.get('id', 'unknown')}",
        f"  version: {ver.get('version', 'unknown')}",
        f"  versionCode: '{ver.get('versionCode', '1')}'",
        f"version: {ver.get('version', 'unknown')}",
        f"versionCode: '{ver.get('versionCode', '1')}'",
        "minSdkVersion: '21'",
        "targetSdkVersion: '21'",
        "",
    ]
    yml.write_text("\n".join(lines), encoding="utf-8")
