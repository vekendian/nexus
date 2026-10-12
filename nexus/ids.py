"""Resource-ID resolver and lock file.

Two kinds of ID matter to Nexus:

* **Nexus IDs** — ids Nexus itself declares (view ids in main.xml, drawables
  referenced from smali, strings referenced from smali). These are *pinned* in
  ``nexus_ids.json`` so generated smali stays byte-stable across rebuilds.

* **GG bindings** — views GameGuardian owns that Nexus attaches to
  (``id:check``, ``id:fix_it``, ...). These are *resolved by name* from the
  tree's ``public.xml`` at apply time, so a weekly GG release that renumbers
  ids keeps working without a code change.

The old single-file patcher hardcoded six GG ids as hex literals and only ever
checked that their *names* still existed. If GG shifted ``check`` from
0x7f050025 to something else, preflight passed and the settings row silently
bound to the wrong view. Resolving by name closes that gap: a missing name is a
hard error, a changed number is reported but not fatal.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .anchors import PatchError

LOCK_NAME = "nexus_ids.json"

_PUBLIC_RE = re.compile(
    r'<public\s+type="(?P<type>\w+)"\s+name="(?P<name>[\w.]+)"\s+id="(?P<id>0x[0-9a-fA-F]+)"'
)


def parse_public(public_xml: str) -> dict:
    """Map ``(type, name) -> hex id`` from a public.xml document."""
    out = {}
    for m in _PUBLIC_RE.finditer(public_xml):
        out[(m.group("type"), m.group("name"))] = m.group("id").lower()
    return out


class Ids:
    """Resolved view over the lock file plus the target tree's public.xml."""

    def __init__(self, data: dict, tree_public: dict | None = None) -> None:
        self.data = data
        self.tree_public = tree_public or {}
        self.nexus = data.get("nexus", {})
        self.gg_observed = data.get("gg_observed", {})

    # -- loading ----------------------------------------------------------
    @classmethod
    def load(cls, lock_path: Path, public_xml: str | None = None) -> "Ids":
        if not lock_path.is_file():
            raise PatchError(f"ID lock file missing: {lock_path}")
        try:
            data = json.loads(lock_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise PatchError(f"ID lock file is not valid JSON: {lock_path}: {e}") from e
        tree_public = parse_public(public_xml) if public_xml is not None else {}
        return cls(data, tree_public)

    # -- Nexus (pinned) lookups -------------------------------------------
    def _pinned(self, name: str) -> int:
        for kind in ("id", "drawable", "string"):
            table = self.nexus.get(kind, {})
            if name in table:
                return int(table[name], 16)
        raise PatchError(f"no pinned Nexus ID named {name!r} in {LOCK_NAME}")

    def hex(self, name: str) -> str:
        """``'nexus_panel_home'`` -> ``'0x7f050163'`` (lowercase, smali style)."""
        return f"0x{self._pinned(name):08x}"

    def smali(self, name: str) -> str:
        """Alias for :meth:`hex`; reads better inside smali templates."""
        return self.hex(name)

    def upper_hex(self, name: str) -> str:
        return f"0x{self._pinned(name):08X}"

    def pinned_table(self) -> list:
        """``[(type, name, hex)]`` in the order public.xml lines must be emitted."""
        rows = []
        for kind in ("id", "drawable", "string"):
            for name, hexval in self.nexus.get(kind, {}).items():
                rows.append((kind, name, hexval))
        return rows

    def public_id_lines(self) -> str:
        return "\n".join(
            f'    <public type="{kind}" name="{name}" id="{hexval}" />'
            for kind, name, hexval in self.pinned_table()
        )

    # -- GG (name-resolved) lookups --------------------------------------
    def gg(self, name: str) -> str:
        """Resolve a GameGuardian-owned view id BY NAME from the tree.

        Hard error when the name is absent: GG removed or renamed a view Nexus
        binds to, and binding to something else silently would be worse.
        """
        got = self.tree_public.get(("id", name))
        if got is None:
            raise PatchError(
                f"GameGuardian id {name!r} not found in the tree's public.xml. "
                f"GG likely renamed or removed this view; Nexus binds to it."
            )
        return got

    def drift(self) -> list:
        """``[(name, observed, recorded)]`` where GG's number changed.

        Informational only — surfaced by the ``ids`` subcommand. A weekly GG
        release that renumbers is expected and must not fail the patch.
        """
        out = []
        for name, recorded in sorted(self.gg_observed.items()):
            got = self.tree_public.get(("id", name))
            if got is not None and got != recorded:
                out.append((name, got, recorded))
        return out

    # -- audits -----------------------------------------------------------
    def audit_collisions(self, public_xml: str) -> list:
        """Ensure no pinned Nexus name or number collides with an existing one."""
        errors = []
        seen = parse_public(public_xml)
        for kind, name, hexval in self.pinned_table():
            if (kind, name) in seen:
                errors.append(f"new {kind} name collision in public.xml: {name}")
            if hexval.lower() in {v.lower() for v in seen.values()}:
                errors.append(f"new {kind} id collision in public.xml: {hexval}")
        return errors

    def audit_gg_bindings(self) -> list:
        """Every GG view Nexus binds to must resolve by name."""
        errors = []
        for name in sorted(self.gg_observed):
            if self.tree_public and ("id", name) not in self.tree_public:
                errors.append(f"GameGuardian id {name!r} missing from public.xml")
        return errors