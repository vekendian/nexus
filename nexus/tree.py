"""Locating, reading, writing and cloning an apktool tree."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from .anchors import PatchError

PATCHER_DIR = Path(__file__).resolve().parent.parent
RES_DIR = PATCHER_DIR / "resources"
LOCK_PATH = PATCHER_DIR / "nexus_ids.json"
OUTPUT_SUFFIX = "_nexus_output"

# Overridable so the tool is not welded to one machine's paths. apktool defaults
# to whatever is on PATH; set NEXUS_APKTOOL=<jar> to pin a specific build.
APKTOOL = os.environ.get("NEXUS_APKTOOL", "apktool")
AAPT = os.environ.get("NEXUS_AAPT", "aapt2")

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
    """Locate an apktool-decoded GG tree, MT Manager's layout included.

    MT Manager writes apktool.json rather than apktool.yml, so a missing .yml
    is not by itself fatal: accept a tree that carries apktool.json too. The
    .yml is synthesized later, during apply, via ensure_apktool_yml().
    """
    tree = Path(src).expanduser().resolve()
    if not tree.is_dir():
        raise PatchError(f"tree not found: {tree}")
    if not (tree / "apktool.yml").is_file() and not (tree / "apktool.json").is_file():
        raise PatchError(f"not an apktool decode (no apktool.yml or apktool.json): {tree}")
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


def copy_resources(tree: Path) -> None:
    shutil.copytree(RES_DIR / "res", tree / "res", dirs_exist_ok=True)


def default_output(tree: Path) -> Path:
    """``<parent>/<treeName>_nexus_output``, a sibling of the source tree."""
    return tree.with_name(tree.name + OUTPUT_SUFFIX)


def make_output(tree: Path, out: Path, force: bool = False) -> None:
    """Clone ``tree`` into ``out`` so the patcher never touches the source.

    Refuses anything that could clobber the source: ``out`` equal to, inside,
    or containing ``tree``. An existing ``out`` is only replaced with
    ``force`` and only if it looks like an apktool tree (so a typo in --out
    cannot rmtree an arbitrary directory).
    """
    tree, out = tree.resolve(), out.resolve()
    if out == tree or tree in out.parents or out in tree.parents:
        raise PatchError(f"output {out} overlaps the source tree {tree}")
    if out.exists():
        if not force:
            raise PatchError(f"{out} already exists (use --force to replace it)")
        if not out.is_dir() or not any((out / n).is_file()
                                       for n in ("apktool.yml", "apktool.json")):
            raise PatchError(f"{out} exists and is not an apktool tree; refusing to delete it")
        shutil.rmtree(out)
    shutil.copytree(tree, out, symlinks=True)


# ---------------------------------------------------------------- helpers ---

def ensure_apktool_yml(tree: Path) -> None:
    """MT Manager trees carry apktool.json, but the apktool CLI needs apktool.yml.

    The keys written here are apktool 2.8.1's schema (`versionInfo`, `sdkInfo`,
    `packageInfo`); the older MetaInfo layout apktool 1.x accepted is rejected
    by 2.8.1 with "versionInfo lines not found".
    """
    yml = tree / "apktool.yml"
    j = tree / "apktool.json"
    if yml.is_file() or not j.is_file():
        return
    import json
    meta = json.loads(j.read_text(encoding="utf-8"))
    ver = meta.get("VersionInfo") or {}
    sdk = meta.get("sdkInfo") or {}
    lines = [
        "!!brut.androlib.apk.ApkInfo",
        f"apkFileName: {meta.get('apkFileName', 'unknown.apk')}",
        "doNotCompress:",
        "- resources.arsc",
        f"isFrameworkApk: {str(meta.get('isFrameworkApk', False)).lower()}",
        "packageInfo:",
        "  forcedPackageId: '127'",
        "  renameManifestPackage: null",
        f"resourcesAreCompressed: {str(not meta.get('sparseResources', False)).lower()}",
        "sdkInfo:",
        f"  minSdkVersion: '{sdk.get('minSdkVersion', '21')}'",
        f"  targetSdkVersion: '{sdk.get('targetSdkVersion', '24')}'",
        f"sharedLibrary: {str(bool(meta.get('sharedLibrary', False))).lower()}",
        f"sparseResources: {str(bool(meta.get('sparseResources', False))).lower()}",
        "unknownFiles: {}",
        "usesFramework:",
        "  ids:",
        "  - 1",
        "  tag: null",
        "version: 2.8.1",
        "versionInfo:",
        f"  versionCode: '{ver.get('versionCode', '1')}'",
        f"  versionName: {ver.get('versionName', 'unknown')}",
        "",
    ]
    yml.write_text("\n".join(lines), encoding="utf-8")
