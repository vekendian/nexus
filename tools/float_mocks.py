#!/usr/bin/env python3
"""Mock renders of the floating interface, for review before it ships.

The float is the one surface that sits over another app, so it cannot be
checked inside Nexus's own screens. This draws the candidates over a
stand-in game frame at phone scale, so the shape, the contrast and the
spacing can be judged without a device.

    python3 tools/float_mocks.py [outdir]

Writes float_v1.png (today), float_v2.png (the card) and float_v3.png (the
card with the scan readout live). Sizes are in dp and converted with the
phone's real density, so what is drawn is what the layout would produce.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# The Nexus palette, from resources/res/values/nexus_colors.xml.
SURFACE = (31, 31, 34)
SURFACE_ALT = (52, 52, 58)
ORANGE = (255, 122, 0)
ON_ORANGE = (26, 26, 28)
TEXT = (255, 255, 255)
ORANGE_DIM = (255, 179, 102)

# A 360dp-wide phone at 3x.
DP = 3
W_DP, H_DP = 360, 640
W, H = W_DP * DP, H_DP * DP


def dp(value: float) -> int:
    return int(round(value * DP))


def font(size_dp: float, bold: bool = False):
    for name in ("Roboto-Bold.ttf", "Roboto-Medium.ttf", "Roboto-Regular.ttf"):
        try:
            return ImageFont.truetype(
                f"/usr/share/fonts/truetype/roboto/{name}", dp(size_dp))
        except OSError:
            continue
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(
                f"/usr/share/fonts/truetype/{name}", dp(size_dp))
        except OSError:
            continue
    return ImageFont.load_default()


def game_frame() -> Image.Image:
    """A stand-in for a game: bright sky, dark ground, a wide luminance range.

    The point is a frame with light and dark behind it, so a surface that
    only reads over a dark game gets caught.
    """
    img = Image.new("RGB", (W, H), (30, 40, 60))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        if t < 0.55:
            k = t / 0.55
            c = (int(90 + 120 * k), int(140 - 20 * k), int(220 - 60 * k))
        else:
            k = (t - 0.55) / 0.45
            c = (int(30 - 20 * k), int(40 - 28 * k), int(50 - 30 * k))
        d.line([(0, y), (W, y)], fill=c)
    d.ellipse([dp(40), dp(100), dp(180), dp(240)], fill=(240, 240, 250))
    d.rectangle([dp(230), dp(400), dp(340), dp(500)], fill=(20, 20, 24))
    return img.filter(ImageFilter.GaussianBlur(dp(2)))


def rr(d, x, y, w, h, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle([dp(x), dp(y), dp(x + w), dp(y + h)],
                        radius=dp(radius), fill=fill, outline=outline,
                        width=dp(width))


def nexus_icon(d, cx, cy, size=48):
    """The float's own icon: a near-black disc with an orange N."""
    r = size / 2
    d.ellipse([dp(cx - r), dp(cy - r), dp(cx + r), dp(cy + r)],
              fill=(24, 24, 27), outline=ORANGE, width=dp(1.5))
    f = font(24, bold=True)
    box = d.textbbox((0, 0), "N", font=f)
    d.text((dp(cx) - (box[2] - box[0]) / 2,
            dp(cy) - (box[3] - box[1]) / 2 - box[1]),
           "N", font=f, fill=ORANGE)


def arrow(d, cx, cy, direction, colour, size=11):
    if direction < 0:
        pts = [(cx - size, cy - size * 0.7), (cx + size * 0.2, cy),
               (cx - size, cy + size * 0.7)]
    else:
        pts = [(cx + size, cy - size * 0.7), (cx - size * 0.2, cy),
               (cx + size, cy + size * 0.7)]
    d.polygon([(dp(px), dp(py)) for px, py in pts], fill=colour)


def bar(d, x, y, w, h, pct, fill, track=(51, 51, 51)):
    rr(d, x, y, w, h, h / 2, fill=track)
    if pct:
        rr(d, x, y, w * pct, h, h / 2, fill=fill)


def speed_chip(d, cx, y, text="9 000 000 000"):
    w = 96
    rr(d, cx - w / 2, y, w, 22, 11, fill=(31, 31, 34),
       outline=(70, 70, 78), width=1)
    f = font(11)
    box = d.textbbox((0, 0), text, font=f)
    d.text((dp(cx) - (box[2] - box[0]) / 2, dp(y + 6)), text, font=f, fill=TEXT)


def v1(img):
    """Today: three loose parts, floating on the game."""
    d = ImageDraw.Draw(img)
    cx, cy = 180, 300
    arrow(d, cx - 58, cy, -1, (235, 235, 235))
    nexus_icon(d, cx, cy)
    arrow(d, cx + 58, cy, 1, (235, 235, 235))
    rr(d, cx - 48, cy + 32, 96, 22, 4, fill=(60, 30, 90),
       outline=(140, 90, 200), width=1)
    f = font(11)
    d.text((dp(cx - 34), dp(cy + 37)), "9 000 000 000", font=f, fill=TEXT)
    return img


def v2(img):
    """The card: the controls and the icon on one surface."""
    d = ImageDraw.Draw(img)
    cx, cy = 180, 300
    card_w = 48 + 10 + 48 + 10 + 48 + 16   # buttons, margins, icon, padding
    rr(d, cx - card_w / 2, cy - 32, card_w, 64, 16, fill=SURFACE,
       outline=(70, 70, 78), width=1)
    for sx in (-1, 1):
        bx = cx + sx * 53
        d.ellipse([dp(bx - 24), dp(cy - 24), dp(bx + 24), dp(cy + 24)],
                  fill=SURFACE_ALT)
        arrow(d, bx, cy, sx, TEXT)
    nexus_icon(d, cx, cy)
    speed_chip(d, cx, cy + 40)
    return img


def v3(img):
    """The card with the scan readout live, as a player sees it."""
    d = ImageDraw.Draw(img)
    cx, cy = 180, 300
    card_w = 48 + 10 + 48 + 10 + 48 + 16
    rr(d, cx - card_w / 2, cy - 32, card_w, 64, 16, fill=SURFACE,
       outline=(70, 70, 78), width=1)
    for sx in (-1, 1):
        bx = cx + sx * 53
        d.ellipse([dp(bx - 24), dp(cy - 24), dp(bx + 24), dp(cy + 24)],
                  fill=SURFACE_ALT)
        arrow(d, bx, cy, sx, TEXT)
    # The readout covers the icon while a scan runs.
    rr(d, cx - 22, cy - 18, 44, 40, 8, fill=(20, 20, 22))
    f = font(11)
    d.text((dp(cx - 15), dp(cy - 14)), "30.9%", font=f, fill=TEXT)
    bar(d, cx - 18, cy + 2, 36, 4, 0.31, ORANGE)
    bar(d, cx - 18, cy + 10, 36, 4, 0.60, ORANGE_DIM)
    speed_chip(d, cx, cy + 40)
    return img


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/opencode")
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("v1", v1), ("v2", v2), ("v3", v3)):
        img = fn(game_frame())
        path = out / f"float_{name}.png"
        img.save(path)
        print(path)


if __name__ == "__main__":
    main()
