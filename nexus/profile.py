"""What a GameGuardian release looks like.

The patcher used to know one GameGuardian by heart: its file names, its
layout names, how many separator bands its settings screen has, which
density buckets it ships its icons in, which package it calls itself. All of
that is data, and data belongs in a file: a release profile.

A profile says *where* the things are. It does not say what to do with them:
the transforms are the same for every release, and they ask the profile where
to look. Adding a GameGuardian release means adding one JSON file. If the
release renamed a file, the profile says the new name. If it renumbered its
views, nothing changes at all, because the ids are resolved by name from the
tree's own public.xml at apply time.

What a profile must not do is hold a decision. "The settings screen has five
orange bands" is a fact about the release and belongs here; "the bands are
orange" is a decision and belongs in the transform.
"""

from __future__ import annotations

import json
from pathlib import Path

from .anchors import PatchError

PROFILE_DIR = Path(__file__).resolve().parent.parent / "profiles"

# The profile's own shape, so a typo in a profile is an error rather than a
# silent default.
REQUIRED = ("gg_release", "files", "layouts", "counts")


class Profile:
    """One GameGuardian release, as data."""

    def __init__(self, data: dict, source: Path | None = None) -> None:
        self.data = data
        self.source = source
        for key in REQUIRED:
            if key not in data:
                raise PatchError(
                    f"profile {source or '<inline>'}: missing {key!r}")
        self.gg_release = str(data["gg_release"])
        self.files = dict(data.get("files", {}))
        self.layouts = dict(data.get("layouts", {}))
        self.counts = dict(data.get("counts", {}))
        self.icons = dict(data.get("icons", {}))
        self.url = dict(data.get("url", {}))

    # -- loading ----------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> "Profile":
        if not path.is_file():
            raise PatchError(f"profile not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise PatchError(f"profile {path} is not valid JSON: {e}") from e
        return cls(data, path)

    @classmethod
    def for_release(cls, release: str, explicit: str | None = None) -> "Profile":
        """The profile for a release, by name or by what the tree says."""
        if explicit:
            path = Path(explicit)
            if path.is_file():
                return cls.load(path)
            path = PROFILE_DIR / explicit
            if path.is_file():
                return cls.load(path)
            if path.suffix != ".json":
                path = PROFILE_DIR / f"gg-{explicit}.json"
            return cls.load(path)
        if release != "unknown":
            path = PROFILE_DIR / f"gg-{release}.json"
            if path.is_file():
                return cls.load(path)
        # Fallback to the known working profile
        path = PROFILE_DIR / "gg-101.4.json"
        if path.is_file():
            return cls.load(path)
        raise PatchError(
            f"no profile for GameGuardian {release}. Expected {PROFILE_DIR}/gg-101.4.json")

    # -- lookups ----------------------------------------------------------

    def file(self, key: str) -> str:
        """A path inside the tree, e.g. the main activity's smali."""
        value = self.files.get(key)
        if not value:
            raise PatchError(
                f"profile {self.gg_release}: no file named {key!r}")
        return value

    def files_list(self, key: str) -> list:
        value = self.files.get(key)
        if not value:
            raise PatchError(
                f"profile {self.gg_release}: no file list named {key!r}")
        if isinstance(value, str):
            return [value]
        return list(value)

    def layout(self, key: str) -> str:
        """A layout's path inside the tree."""
        value = self.layouts.get(key)
        if not value:
            raise PatchError(
                f"profile {self.gg_release}: no layout named {key!r}")
        return value

    def count(self, key: str) -> int:
        """A number about the release, e.g. how many bands its settings screen
        has."""
        value = self.counts.get(key)
        if value is None:
            raise PatchError(
                f"profile {self.gg_release}: no count named {key!r}")
        return int(value)

    def icon_files(self) -> list:
        """Every icon file the release ships, per density bucket."""
        out = []
        for family, buckets in self.icons.get("buckets", {}).items():
            for bucket in buckets:
                for name in self.icons.get("names", {}).get(family, []):
                    out.append(f"res/{family}-{bucket}/{name}")
        return out

    def url_scheme(self) -> tuple:
        """The plain URL and the shift its obfuscator applies."""
        plain = self.url.get("plain")
        if not plain:
            raise PatchError(f"profile {self.gg_release}: no url.plain")
        return plain, int(self.url.get("caesar_shift", 3))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Profile gg-{self.gg_release}>"


def gg_version_from_tree(tree: Path) -> str:
    """The version string a tree declares, for picking a profile.

    Delegates to the tree reader so the patcher has one answer to "which
    release is this?" -- GameGuardian's manifest versionName is stale.
    """
    from .tree import detect_version
    return detect_version(tree)
