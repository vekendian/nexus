"""Exact-anchor engine.

Every edit Nexus makes targets an exact run of tokens copied verbatim from a
known GameGuardian release. If GG changes that run in a weekly update the
patch must fail loudly with the anchor's name, never silently produce a
broken APK. `replace_once` is the only sanctioned way to rewrite text.

Matching ignores insignificant whitespace. Decoders disagree on XML layout:
MT Manager puts each attribute on its own line, apktool collapses them onto
the element's line, and both describe the same GG resource. Anchors are
written in one style and match either, so a tree decodes with MT Manager or
with apktool (`tools/apktool-2.8.1.jar`) without re-authoring a single anchor.
Attribute names, values and tags are never normalised, so a genuine content
change in GameGuardian still fails the anchor.
"""

from __future__ import annotations


class PatchError(Exception):
    """A patch could not be applied safely. Always aborts; never degrades."""


def _collapse(text: str) -> tuple:
    """Whitespace-collapsed view of `text` plus a map back to source offsets.

    Each whitespace run becomes a single space and the result is trimmed, so
    the returned string is directly comparable. The offset list is aligned
    index-for-index with it, which is what lets a match found in collapsed
    space be spliced out of the original text.
    """
    chars: list = []
    offsets: list = []
    in_ws = False
    for i, ch in enumerate(text):
        if ch.isspace():
            if in_ws:
                continue
            chars.append(" ")
            offsets.append(i)
            in_ws = True
        else:
            chars.append(ch)
            offsets.append(i)
            in_ws = False
    start = 0
    while start < len(chars) and chars[start] == " ":
        start += 1
    end = len(chars)
    while end > start and chars[end - 1] == " ":
        end -= 1
    return "".join(chars[start:end]), offsets[start:end]


def _count(text: str, anchor: str) -> int:
    norm, _ = _collapse(text)
    target, _ = _collapse(anchor)
    return norm.count(target)


def _span(text: str, anchor: str):
    """Source range of `anchor` inside `text`, or None if absent."""
    norm, offsets = _collapse(text)
    target, _ = _collapse(anchor)
    i = norm.find(target)
    if i < 0:
        return None
    return offsets[i], offsets[i + len(target) - 1] + 1


def _fail(what: str, anchor: str, n: int, expected: int) -> "PatchError":
    return PatchError(
        f"{what}: anchor found {n}x (expected exactly {expected}x).\n"
        f"--- anchor ---\n{anchor}\n"
        "GameGuardian changed this block; update the anchor or the transform."
    )


def anchor_count(text: str, anchor: str) -> int:
    """Occurrences of `anchor`, ignoring insignificant whitespace."""
    return _count(text, anchor)


def find_span(text: str, anchor: str):
    """Source range of `anchor` in `text` (whitespace-tolerant), or None."""
    return _span(text, anchor)


def cut_once(text: str, anchor: str, what: str) -> str:
    """Remove `anchor` from `text`, requiring exactly one occurrence."""
    n = _count(text, anchor)
    if n != 1:
        raise _fail(what, anchor, n, 1)
    start, end = _span(text, anchor)
    return text[:start] + text[end:]


def replace_once(text: str, old: str, new: str, what: str) -> str:
    """Replace `old` with `new`, requiring exactly one occurrence.

    `what` names the anchor and appears in every error message, so a failure
    names the exact block that drifted rather than just reporting a diff.
    """
    n = _count(text, old)
    if n != 1:
        raise _fail(what, old, n, 1)
    start, end = _span(text, old)
    return text[:start] + new + text[end:]


def replace_exact(text: str, old: str, new: str, what: str, count: int) -> str:
    """Replace every occurrence, asserting the count matches `count`.

    Used for anchors that legitimately repeat (e.g. two pre-existing button rows).
    """
    n = _count(text, old)
    if n != count:
        raise _fail(what, old, n, count)
    out, cursor = [], 0
    for _ in range(count):
        span = _span(text[cursor:], old)
        start, end = span[0] + cursor, span[1] + cursor
        out.append(text[cursor:start])
        out.append(new)
        cursor = end
    out.append(text[cursor:])
    return "".join(out)
