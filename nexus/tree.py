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
    """Read a file from the tree, or "" when it is not there.

    A missing file is a finding, not a crash: the checks that call this are
    there to report what is wrong with a tree, and dying on a traceback
    hides every other finding behind the first one. An empty string makes
    the anchor counts fail, which is the report.
    """
    path = tree / rel
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def write(tree: Path, rel: str, text: str) -> None:
    (tree / rel).write_text(text, encoding="utf-8")


def smali_roots(tree: Path) -> list:
    return [tree / "smali"] + sorted(p for p in (tree / "smali_classes2").glob("*")
                                    if p.is_dir())


def detect_version(tree: Path) -> str:
    """Best-effort GG version for display: the tree's own version_number
    string, then apktool.json, then apktool.yml.

    GameGuardian's AndroidManifest carries a stale versionName, so it is not
    read: the app's About screen shows res/values/strings.xml's version_number,
    and that is the release the tree actually is. Only used for human-readable
    output and the lock file's drift note, so it degrades to "unknown" rather
    than raising.
    """
    strings = tree / "res/values/strings.xml"
    if strings.is_file():
        m = re.search(r'<string name="version_number">([^<]*)</string>',
                      strings.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
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
    return "unknown"


def copy_resources(tree: Path) -> None:
    shutil.copytree(RES_DIR / "res", tree / "res", dirs_exist_ok=True)


def copy_smali(tree: Path) -> None:
    """Copy the hand-written smali classes in resources/smali into the tree.

    Must run AFTER rebrand(). These classes live in the rebranded namespace
    (org/vekendian/nexus/...), which is exactly the directory rebrand() creates
    by moving com/scmq. Copying them first would make rebrand() refuse with
    "already exists -- tree may be rebranded", because it cannot tell our
    classes apart from GG's.

    Also copies the luajava/pivot port in resources/smali_luajava (see
    copy_luajava) into the same primary root.

    Only the primary root: GG is single-dex, and copying the same class into
    every root would be a duplicate-definition build error the moment it ships
    more than one.
    """
    src = RES_DIR / "smali"
    if src.is_dir():
        shutil.copytree(src, tree / "smali", dirs_exist_ok=True)
        # The init probe is a diagnostic, not a feature: it deliberately calls
        # findViewById on an id it expects to be ABSENT, so shipping it would trip
        # the reachability audit and add a class nothing can reach. Only present
        # when NEXUS_DIAG=1 asked for it.
        if not diag_enabled():
            stale = tree / "smali" / "org" / "vekendian" / "nexus" / "Diag.smali"
            if stale.is_file():
                stale.unlink()
    copy_luajava(tree)


_CLASS_RE = re.compile(r"^\.class\s+(?:[\w.]+\s+)*(L[^;]+;)", re.M)


def _class_of(path: Path) -> str | None:
    """The descriptor a smali file declares, or None if unreadable."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return None
    m = _CLASS_RE.search(head)
    return m.group(1) if m else None


def copy_luajava(tree: Path) -> None:
    """Copy resources/smali_luajava into the primary root, refusing collisions.

    The port adds classes to packages GG already owns -- luaj/, lasm/ and
    android/{c,ext}. Two failure modes are unrecoverable after the fact, so both
    are refused here rather than discovered at build time:

      * **path collision** -- a file landing on top of an existing one silently
        deletes a GG class (or, on a re-run, its own twin);
      * **descriptor collision** -- two files declaring the same class from
        different paths is a duplicate-definition build error, the kind apktool
        reports only after smali has already run.

    A byte-identical file already in the tree is neither failure: it is the
    re-run case, and is skipped so the audit stays idempotent.
    """
    src = RES_DIR / "smali_luajava"
    if not src.is_dir():
        return
    dst = tree / "smali"
    if not dst.is_dir():
        raise PatchError(f"{dst} missing: cannot place smali_luajava additions")

    existing = {p.relative_to(dst).as_posix(): p for p in dst.rglob("*.smali")}
    described = set()
    for rel, p in existing.items():
        d = _class_of(p)
        if d:
            described.add(d)

    checked = 0
    added = 0
    for p in sorted(src.rglob("*.smali")):
        rel = p.relative_to(src).as_posix()
        checked += 1
        hit = existing.get(rel)
        if hit is not None:
            try:
                same = hit.read_bytes() == p.read_bytes()
            except OSError:
                same = False
            if same:
                continue          # already in the tree from a previous run
            raise PatchError(
                f"smali_luajava/{rel} would overwrite the existing smali/{rel} "
                f"rather than add a class")
        desc = _class_of(p)
        if desc and desc in described:
            raise PatchError(
                f"smali_luajava/{rel} declares {desc}, which another file in "
                f"the tree already defines (duplicate-definition build error)")
        existing[rel] = p
        if desc:
            described.add(desc)
        added += 1

    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"smali_luajava: {added} class(es) copied, "
          f"{checked - added} already present, 0 collisions")


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


def diag_enabled() -> bool:
    """``NEXUS_DIAG=1`` ships the MainService init probe. Off by default."""
    return os.environ.get("NEXUS_DIAG", "0") == "1"


def ui_enabled() -> bool:
    """``NEXUS_UI=0`` applies the rebrand and nothing else.

    No main.xml rewrite, no FixTheme change, no r.smali injection, no service
    config or ConfigListAdapter edits, no keyboard work, no URL rewrite. The
    Nexus resources and public.xml entries still land, so ids stay consistent.

    This is the one bisect axis that has never been run. Every transform skipped
    here edits a file GG owns; a build without them answers "is the crash in the
    UI injection at all", which the engine-stubbed build could not -- that one
    only stopped NexusHost.boot() from running while leaving the whole UI in
    place. Lives here because tree.py is the lowest module in the package and
    both cli.py and checks.py need it without importing each other.
    """
    return os.environ.get("NEXUS_UI", "1") != "0"
