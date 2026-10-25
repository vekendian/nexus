"""The design system has rules, and this file is what makes them true.

A design system that is only a convention decays the moment somebody is in a
hurry. These checks turn the convention into a build failure, so the next
change cannot quietly add a ninth grey, a fifth orange or a stray hex value.

The rules:

* every resource file is well-formed XML (a double hyphen in a comment is
  not, and it cost a build once);
* a colour is a token, never a literal, except where a literal is the design;
* radii come from one scale, each value with a role;
* units are dp, not dip;
* ripples use one of three alphas;
* every colour token and every drawable is used.

What these cannot check: whether a colour is legible on the surface it is
used on, or whether the app looks right. That needs a screenshot.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from nexus.tree import RES_DIR

ROOT = Path(__file__).resolve().parent.parent

RES = RES_DIR / "res"
VALUES = RES / "values"
DRAWABLE = RES / "drawable"
COLOR = RES / "color"
LAYOUT = RES / "layout"

# Every file the patcher owns, in every folder that holds resources.
NEXUS_RES_FILES = sorted(
    p for p in RES.rglob("*")
    if p.is_file() and p.suffix in (".xml", ".png", ".webp")
)

# The radii the design system allows, and what each one is for.
#
#   3dp   a progress bar's track and fill
#   8dp   a small chip: the tag on a module card, the float's badge
#   16dp  a button: the tonal, the primary, the choice
#   20dp  the nav pill, which is a stadium on a 40dp row
#   24dp  a settings row
#   26dp  a toast
#   28dp  a dialog, and the power card's ring
#   32dp  the navbar
RADIUS_SCALE = {3, 8, 16, 20, 24, 26, 28, 32}

# The only raw colours a resource may carry. Everything else is a token.
#   #FFFFFFFF  a vector's fill: the icons are white by design
#   #FFFFFF     a ripple mask, which is never drawn
#   #33FFFFFF / #26FFFFFF / #33000000  the three ripple alphas
LITERAL_COLOURS = {
    "#ffffffff", "#ffffff", "#33ffffff", "#26ffffff", "#33000000",
    "#00ffffff",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tokens() -> dict:
    text = _text(VALUES / "nexus_colors.xml")
    return {m.group(1): m.group(2).lower()
            for m in re.finditer(r'<color name="([\w]+)">(#[\da-fA-F]{6,8})</color>',
                                 text)}


def _everything_the_patcher_writes() -> str:
    """Every place a Nexus drawable or colour can be named."""
    parts = []
    for base in (RES, RES_DIR / "java", RES_DIR / "smali",
                 RES_DIR / "smali_lua", ROOT / "nexus"):
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in (".xml", ".java", ".smali",
                                                  ".py"):
                parts.append(_text(path))
    return "\n".join(parts)


# ------------------------------------------------------------ well-formed ---

def test_every_resource_file_is_well_formed():
    """A double hyphen inside an XML comment is not well-formed, and aapt2
    says so only when it is already building the APK."""
    broken = []
    for path in NEXUS_RES_FILES:
        if path.suffix != ".xml":
            continue
        try:
            ET.fromstring(_text(path))
        except ET.ParseError as e:
            broken.append(f"{path.relative_to(RES_DIR)}: {e}")
    assert not broken, "not well-formed:\n" + "\n".join(broken)


# ------------------------------------------------------------------ colour ---

def test_colours_are_tokens_not_literals():
    """A literal in a drawable is a colour nobody can find in the table."""
    offenders = []
    for path in NEXUS_RES_FILES:
        if path.suffix != ".xml":
            continue
        if path == VALUES / "nexus_colors.xml":
            continue  # the table itself: this is where a literal belongs
        for m in re.finditer(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b', _text(path)):
            value = m.group(0).lower()
            if value in LITERAL_COLOURS:
                continue
            offenders.append(f"{path.relative_to(RES_DIR)}: {value}")
    assert not offenders, "raw colours in resources:\n" + "\n".join(offenders)


def test_every_colour_token_is_used():
    """A token nobody reads is a fifth grey waiting to happen."""
    tokens = _tokens()
    used = _everything_the_patcher_writes()
    # Reserved: kept because the design system has a place for them even
    # though the current screens do not reach for them yet.
    reserved = {"nexus_indicator"}
    unused = [name for name in tokens
              if name not in reserved
              and f"@color/{name}" not in used
              and f'"{name}"' not in used]
    assert not unused, f"unused colour tokens: {sorted(unused)}"


def test_only_one_orange():
    """The accent is one colour. A second orange is a second meaning."""
    tokens = _tokens()
    oranges = {name: value for name, value in tokens.items()
               if value.startswith("#ff7a") or value.startswith("#33ff7a")
               or value.startswith("#40ff7a")}
    # The accent, its "on accent" ink, the dimmed stage fill and the edge
    # tint. Anything else orange is a new colour wearing an old name.
    assert set(oranges) <= {"nexus_orange", "nexus_orange_dim",
                             "nexus_float_badge_edge"}, \
        f"unexpected orange tokens: {sorted(oranges)}"


# ------------------------------------------------------------------- shape ---

def test_radii_come_from_the_scale():
    """Nine radii once meant nine roles for a shape nobody could name."""
    offenders = []
    for path in NEXUS_RES_FILES:
        if path.suffix != ".xml":
            continue
        for m in re.finditer(r'android:radius="([0-9.]+)(dp|dip)"', _text(path)):
            value = int(float(m.group(1)))
            if value not in RADIUS_SCALE:
                offenders.append(f"{path.relative_to(RES_DIR)}: {value}")
    assert not offenders, "radii off the scale:\n" + "\n".join(offenders)


def test_units_are_dp():
    """dip and dp are the same thing on every device Android has shipped, and
    having both in one file means somebody was not reading the other."""
    offenders = []
    for path in NEXUS_RES_FILES:
        if path.suffix != ".xml":
            continue
        if re.search(r'="[0-9.]+dip"', _text(path)):
            offenders.append(str(path.relative_to(RES_DIR)))
    assert not offenders, f"dip in resources: {offenders}"


def test_ripples_use_one_of_three_alphas():
    """A ripple's alpha is the app's press feedback. Four alphas is four
    different answers to "is this pressed"."""
    allowed = {"#26ffffff", "#33ffffff", "#33000000"}
    offenders = []
    for path in NEXUS_RES_FILES:
        if path.suffix != ".xml":
            continue
        for m in re.finditer(r'android:color="(#[0-9a-fA-F]{8})"', _text(path)):
            if m.group(1).lower() not in allowed:
                offenders.append(f"{path.relative_to(RES_DIR)}: {m.group(1)}")
    assert not offenders, "stray ripple alphas:\n" + "\n".join(offenders)


# ------------------------------------------------------------------ assets ---

def test_every_drawable_is_referenced():
    """A drawable nothing draws is dead weight that still gets an id."""
    used = _everything_the_patcher_writes()
    orphans = []
    for path in sorted(DRAWABLE.glob("*.xml")):
        name = path.stem
        if (f"@drawable/{name}" in used or f'"{name}"' in used
                or f"@@ID:{name}@@" in used):
            continue
        orphans.append(name)
    assert not orphans, f"drawables nothing references: {orphans}"


def test_the_primitives_the_design_system_needs_exist():
    """The pieces the reference app had and the patcher did not."""
    for name in ("nexus_bg_toast", "nexus_bg_track", "nexus_bg_fill",
                 "nexus_bg_row", "nexus_ic_check", "nexus_bg_button_bar"):
        assert (DRAWABLE / f"{name}.xml").is_file(), f"{name} is missing"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__]))
