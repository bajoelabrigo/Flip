"""Draws the made-up sample logos (transparent PNG) that logo slots show in thumbnails and previews.

    python tools/scene_templates/make_sample_logos.py [--out <muestras>]

Invented names and simple marks, ours: nothing that looks like a real brand. They live next to the sample
photos (outside the repo) as logo-01.png ... and never go inside a package (slots ship empty).
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "codigo" / "flip-addons" / "build" / "src" / "fonts"
OUT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "muestras"
S = 4  # supersampling


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(next(FONTS.rglob(name))), size * S)


def text_c(d: ImageDraw.ImageDraw, xy, txt, f, fill):
    d.text((xy[0] * S, xy[1] * S), txt, font=f, fill=fill, anchor="mm")


def mountain(d, c):
    d.polygon([(150 * S, 520 * S), (330 * S, 220 * S), (430 * S, 380 * S), (500 * S, 290 * S), (650 * S, 520 * S)],
              fill=c)
    d.polygon([(330 * S, 220 * S), (375 * S, 295 * S), (330 * S, 270 * S), (290 * S, 290 * S)], fill=(255, 255, 255, 255))


def logo(i: int) -> Image.Image:
    im = Image.new("RGBA", (800 * S, 800 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if i == 1:
        mountain(d, (31, 58, 95, 255))
        text_c(d, (400, 640), "NORTE", font("Montserrat-Bold.ttf", 120), (31, 58, 95, 255))
    elif i == 2:
        d.ellipse([200 * S, 120 * S, 600 * S, 520 * S], fill=(255, 107, 53, 255))
        d.ellipse([290 * S, 120 * S, 690 * S, 520 * S], fill=(0, 0, 0, 0))
        text_c(d, (400, 650), "luma", font("Poppins-SemiBold.ttf", 140), (40, 40, 48, 255))
    elif i == 3:
        for k in range(3):
            a = math.radians(-90 + k * 120)
            cx, cy = 400 + 110 * math.cos(a), 330 + 110 * math.sin(a)
            d.ellipse([(cx - 120) * S, (cy - 120) * S, (cx + 120) * S, (cy + 120) * S],
                      fill=[(0, 194, 168, 220), (91, 103, 255, 220), (255, 196, 61, 220)][k])
        text_c(d, (400, 650), "TRÍADA", font("Montserrat-ExtraBold.ttf", 110), (20, 20, 30, 255))
    elif i == 4:
        d.rounded_rectangle([230 * S, 110 * S, 570 * S, 450 * S], 70 * S, fill=(17, 17, 17, 255))
        d.polygon([(420 * S, 150 * S), (300 * S, 300 * S), (390 * S, 300 * S), (360 * S, 420 * S), (500 * S, 250 * S),
                   (410 * S, 250 * S)], fill=(255, 214, 0, 255))
        text_c(d, (400, 600), "VOLTA", font("Anton-Regular.ttf", 140), (17, 17, 17, 255))
    elif i == 5:
        d.ellipse([250 * S, 120 * S, 550 * S, 420 * S], outline=(185, 140, 70, 255), width=18 * S)
        text_c(d, (400, 272), "A", font("PlayfairDisplay-Bold.ttf", 170), (185, 140, 70, 255))
        text_c(d, (400, 560), "AURORA", font("PlayfairDisplay-Regular.ttf", 96), (60, 40, 30, 255))
        text_c(d, (400, 650), "CAFÉ · PANADERÍA", font("Montserrat-Medium.ttf", 40), (120, 90, 60, 255))
    elif i == 7:  # light versions, for dark templates
        mountain(d, (255, 255, 255, 255))
        d.polygon([(330 * S, 220 * S), (375 * S, 295 * S), (330 * S, 270 * S), (290 * S, 290 * S)], fill=(120, 200, 255, 255))
        text_c(d, (400, 640), "NORTE", font("Montserrat-Bold.ttf", 120), (255, 255, 255, 255))
    elif i == 8:
        d.polygon([(420 * S, 110 * S), (270 * S, 300 * S), (385 * S, 300 * S), (345 * S, 450 * S), (530 * S, 240 * S),
                   (415 * S, 240 * S)], fill=(255, 214, 0, 255))
        text_c(d, (400, 600), "VOLTA", font("Anton-Regular.ttf", 140), (255, 255, 255, 255))
    else:
        d.rounded_rectangle([170 * S, 170 * S, 630 * S, 630 * S], 110 * S, fill=(226, 61, 112, 255))
        text_c(d, (400, 390), "k", font("Poppins-Bold.ttf", 330), (255, 255, 255, 255))
    return im.resize((800, 800), Image.LANCZOS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    for i in range(1, 9):
        logo(i).save(args.out / f"logo-{i:02d}.png")
    print("8 logos ->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
