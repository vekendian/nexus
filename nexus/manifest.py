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
# GG also carries the package as a *descriptor literal* -- "Lcom/scmq;" -- which
# the slash-form replace below does not match. android/ext/i.smali uses it in the
# <clinit> fallback that rebuilds the package name at runtime:
#     literal.length() - pkg.length()   ->   literal.substring(0, that)
# Leaving it behind is not cosmetic. "Lcom/scmq;" is 11 characters and
# "org.vekendian.nexus" is 20, so the fallback computes a negative length and
# String.substring throws instead of recovering.
DESCRIPTOR_OLD = '"Lcom/scmq;"'
DESCRIPTOR_NEW = '"Lorg/vekendian/nexus;"'
APP_NAME_OLD = '<string name="app_name">GameGuardian</string>'
APP_NAME_NEW = '<string name="app_name">Nexus</string>'
NEW_VERSION_NAME = "1.0.0"
NEW_VERSION_CODE = "1"
# The version GG actually displays. The manifest is only part of it: the
# About screen and the float's own status line read
# `<string name="version_number">` (MainService, Script$prompt, the About
# dialog all resolve it at runtime), so rebranding the manifest alone would
# leave the interface still announcing GameGuardian's release number.
VERSION_NUMBER_ELEMENT_RE = re.compile(
    r'(<string name="version_number">)[^<]*(</string>)')


def set_display_version(strings: str) -> str:
    """Rewrite the display version to Nexus's, whatever value it carried.

    The element itself is pinned, never its text: every GameGuardian release
    carries its own number there, and the rewrite must keep working across
    releases exactly like the app-name swap above it.
    """
    new, n = VERSION_NUMBER_ELEMENT_RE.subn(
        rf"\g<1>{NEW_VERSION_NAME}\g<2>", strings)
    if n != 1:
        raise PatchError(f"strings.xml version_number entry found {n}x (expected 1x)")
    return new

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
    return _add_picker_activity(manifest)


# A standard-launch-mode proxy that exists solely to call
# startActivityForResult() on itself -- see resources/smali/org/vekendian/
# nexus/ModulePicker.smali for why the singleInstance host cannot. It must keep
# the DEFAULT launch mode, so android:launchMode is deliberately absent.
#
# The window MUST be opaque. A translucent proxy lets the singleInstance host
# resume while the proxy is still alive, so the host's onPostResume (where the
# parked Uri is drained) ran ~400ms BEFORE the picker returned, saw a null Uri,
# and no further resume ever came. Making the proxy opaque forces the host to
# resume strictly after the proxy has parked the Uri and called finish().
PICKER_ACTIVITY = '''    <activity
        android:name="org.vekendian.nexus.ModulePicker"
        android:excludeFromRecents="true"
        android:exported="false"
        android:theme="@style/FixTheme" />
'''


def _add_picker_activity(manifest: str) -> str:
    if "ModulePicker" in manifest:
        raise PatchError("manifest already declares ModulePicker (already patched?)")
    close = manifest.rindex("</application>")
    return manifest[:close] + PICKER_ACTIVITY + manifest[close:]


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
    # The descriptor literal is a separate token; see DESCRIPTOR_OLD. Rewriting
    # it is required for correctness (i.smali's <clinit> length arithmetic) and
    # the count is reported so a GG release that drops the literal is noticed.
    replace_in_smali(tree, DESCRIPTOR_OLD, DESCRIPTOR_NEW)
    write(tree, "AndroidManifest.xml",
          transform_manifest_identity(read(tree, "AndroidManifest.xml")))
    strings = tree / "res/values/strings.xml"
    if strings.is_file():
        txt = strings.read_text(encoding="utf-8")
        txt = set_app_name(txt)
        txt = set_display_version(txt)
        write(tree, "res/values/strings.xml", txt)
    yml = tree / "apktool.yml"
    if yml.is_file():
        write(tree, "apktool.yml", set_yml_version(yml.read_text(encoding="utf-8")))
