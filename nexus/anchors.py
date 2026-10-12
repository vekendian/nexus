"""Exact-anchor engine.

Every edit Nexus makes targets an exact literal block copied verbatim from a
known GameGuardian release. If GG changes that block in a weekly update the
patch must fail loudly with the anchor's name, never silently produce a broken
APK. `replace_once` is the only sanctioned way to rewrite text.
"""

from __future__ import annotations


class PatchError(Exception):
    """A patch could not be applied safely. Always aborts; never degrades."""


def replace_once(text: str, old: str, new: str, what: str) -> str:
    """Replace `old` with `new`, requiring exactly one occurrence.

    `what` names the anchor and appears in every error message, so a failure
    names the exact block that drifted rather than just reporting a diff.
    """
    n = text.count(old)
    if n != 1:
        raise PatchError(
            f"{what}: anchor found {n}x (expected exactly 1x).\n"
            f"--- anchor ---\n{old}\n"
            f"GameGuardian changed this block; update the anchor or the transform."
        )
    return text.replace(old, new, 1)


def replace_exact(text: str, old: str, new: str, what: str, count: int) -> str:
    """Replace every occurrence, asserting the count matches `count`.

    Used for anchors that legitimately repeat (e.g. two legacy button rows).
    """
    n = text.count(old)
    if n != count:
        raise PatchError(
            f"{what}: anchor found {n}x (expected exactly {count}x).\n"
            f"--- anchor ---\n{old}\n"
            f"GameGuardian changed this block; update the anchor or the transform."
        )
    return text.replace(old, new)