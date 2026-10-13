"""Rebrand: package name, launcher label, version.

com.scmq -> org.vekendian.nexus, launcher label -> Nexus, version -> 1.0.0/1.

The application label in GG is an obfuscated literal (e.g. "Kujtnodnookc") that
changes every release, so it is matched by regex on the <application> tag rather
than a fixed string.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .anchors import PatchError, replace_once
from .tree import read, smali_roots, write

PKG_OLD = "com.scmq"
PKG_NEW = "org.vekendian.nexus"
SMALI_OLD = "Lcom/scmq/"
SMALI_NEW = "Lorg/vekendian/nexus/"
APP_NAME_OLD = '<string name="app_name">GameGuardian</string>'
APP_NAME_NEW = '<string name="app_name">Nexus</string>'
NEW_VERSION_NAME = "1.0.0"
NEW_VERSION_CODE = "1"

def replace_in_smali(tree: Path, old: str, new: str) -> int:
    hits = 0
    for root in smali_roots(tree):
        for f in root.rglob("*.smali"):
            t = f.read_text(encoding="utf-8")
            if old in t:
                f.write_text(t.replace(old, new), encoding="utf-8")
                hits += 1
    return hits


def transform_manifest_identity(manifest: str) -> str:
    if f'package="{PKG_OLD}"' not in manifest:
        raise PatchError(f'manifest package is not "{PKG_OLD}" (already rebranded?)')
    manifest = manifest.replace(PKG_OLD, PKG_NEW)
    manifest, cnt = re.subn(
        r'(<application\b[^>]*?android:label=")[^"]*(")',
        r"\g<1>Nexus\2", manifest, count=1)
    if cnt != 1:
        raise PatchError(f"application android:label matched {cnt}x (expected 1x)")
    manifest, cnt = re.subn(r'android:label="Game"', 'android:label="Nexus"', manifest)
    if cnt != 2:
        raise PatchError(f'activity android:label="Game" matched {cnt}x (expected 2x)')
    # Drop the TV launcher from the ActivityMain entry so GG ships one icon,
    # not a TV one. The block is located by attribute rather than by
    # indentation: MT Manager pretty-prints attributes one per line while
    # apktool collapses them onto the element's line.
    m = re.search(r'<activity\b[^>]*?android:icon="@mipmap/ic_hw_48dp"[^>]*?>', manifest)
    if not m:
        raise PatchError("ActivityMain launcher block not found (icon changed?)")
    if 'ActivityMain' not in m.group(0):
        raise PatchError("TV launcher activity is not ActivityMain (icon reused?)")
    i = manifest.index('<intent-filter', m.end())
    j = manifest.index('</intent-filter>', i) + len('</intent-filter>')
    # Both filters (MAIN+LAUNCHER and MAIN+LEANBACK_LAUNCHER) go, leaving the
    # phone activity as the app's single launcher entry.
    k = manifest.index('</intent-filter>', j) + len('</intent-filter>')
    block = manifest[i:k]
    if "android.intent.category.LAUNCHER" not in block:
        raise PatchError("ActivityMain LAUNCHER intent-filter not found")
    if "android.intent.category.LEANBACK_LAUNCHER" not in block:
        raise PatchError("ActivityMain LEANBACK_LAUNCHER intent-filter not found")
    manifest = manifest[:i] + manifest[k:]
    if manifest.count('android.intent.category.LAUNCHER') != 1:
        raise PatchError("expected exactly 1 LAUNCHER category after HW removal")
    # MainActivity keeps its own LEANBACK filter; only ActivityMain's pair goes.
    if manifest.count('android.intent.category.LEANBACK_LAUNCHER') != 1:
        raise PatchError("expected exactly 1 LEANBACK_LAUNCHER category after HW removal")
    return manifest


def set_app_name(strings: str) -> str:
    if APP_NAME_OLD not in strings:
        raise PatchError("strings.xml app_name entry not found")
    return strings.replace(APP_NAME_OLD, APP_NAME_NEW, 1)


def set_yml_version(yml: str) -> str:
    yml, c1 = re.subn(r"(?m)^  versionCode: .*$",
                      f"  versionCode: '{NEW_VERSION_CODE}'", yml)
    yml, c2 = re.subn(r"(?m)^  versionName: .*$",
                      f"  versionName: {NEW_VERSION_NAME}", yml)
    if c1 != 1 or c2 != 1:
        raise PatchError(f"apktool.yml versionInfo lines not found (code={c1}, name={c2})")
    return yml


def rebrand(tree: Path) -> None:
    """com.scmq -> org.vekendian.nexus, label -> Nexus, version -> 1.0.0/1."""
    moved = 0
    for root in smali_roots(tree):
        src = root / "com" / "scmq"
        if not src.is_dir():
            continue
        dst = root / "org" / "vekendian" / "nexus"
        if dst.exists():
            raise PatchError(f"{dst} already exists — tree may be rebranded")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved += 1
        try:
            src.parent.rmdir()  # prune empty com/
        except OSError:
            pass
    if moved == 0:
        raise PatchError("smali/com/scmq not found in any smali root")
    if replace_in_smali(tree, SMALI_OLD, SMALI_NEW) == 0:
        raise PatchError("no smali file contained Lcom/scmq/ after the move")
    write(tree, "AndroidManifest.xml",
          transform_manifest_identity(read(tree, "AndroidManifest.xml")))
    strings = tree / "res/values/strings.xml"
    if strings.is_file():
        write(tree, "res/values/strings.xml",
              set_app_name(strings.read_text(encoding="utf-8")))
    yml = tree / "apktool.yml"
    if yml.is_file():
        write(tree, "apktool.yml", set_yml_version(yml.read_text(encoding="utf-8")))
