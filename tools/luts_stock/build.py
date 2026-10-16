"""Builds the LUTs of Stock › LUTs (for the 0.14.0 «lut» delivery).

    py tools/luts_stock/build.py [--only id,id]

<out>/<id>/<id>.cube       33-point 3D LUT (what Stock downloads; the app installs it with importLut)
<out>/<id>/thumbnail.png   768 x 432 card: the sample photo, original on the left, the look on the right
<out>/<id>/meta.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scene_templates"))

import grade  # noqa: E402
import looks  # noqa: E402
from kit import BLOCKED  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
OUT = ROOT / "luts" / "paquetes"
SAMPLES = ROOT / "plantillas" / "muestras"
CARD = (768, 432)

# Brand-carrying sample photos (CLAUDE.md) on top of the template kit's list.
NO = {"product-01", "product-02", "product-03", "product-04", "gym-03", "fashion-05", "fashion-06", "family-06",
      "barber-04", "bakery-01", "sport-01", "sport-02", "nails-01", "skate-02", "skate-03", "city-03", "city-04"} | set(BLOCKED)


def brightness(path: Path) -> float:
    with Image.open(path) as im:
        return float(np.asarray(im.convert("L").resize((64, 36)), np.float32).mean() / 255)


def sample_for(theme: str, lid: str) -> Path:
    """A mid-bright photo of the theme: on a very dark one the look does not show on the card."""
    pool = [p for p in sorted(SAMPLES.glob(f"h-{theme}-*.jpg")) if p.stem not in NO]
    pool += [p for p in sorted(SAMPLES.glob(f"{theme}-*.jpg")) if p.stem not in NO and not p.stem.startswith(("car", "cusco", "muertos"))]
    good = [p for p in pool if 0.3 <= brightness(p) <= 0.72]
    pool = good or pool or [SAMPLES / "h-nature-01.jpg"]
    return pool[zlib.crc32(lid.encode()) % len(pool)]


def cover(path: Path, size) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    w, h = size
    k = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return np.asarray(im.crop((x, y, x + w, y + h)), np.float32) / 255.0


def build(entry) -> str:
    lid, es, en, cat, steps, tags, theme = entry
    folder = OUT / lid
    folder.mkdir(parents=True, exist_ok=True)
    try:
        grade.write_cube(folder / f"{lid}.cube", en, steps)
        photo = cover(sample_for(theme or "nature", lid), CARD)
        graded = grade.apply_look(photo, steps)
        split = int(CARD[0] * 0.38)
        card = graded.copy()
        card[:, :split] = photo[:, :split]
        img = Image.fromarray((np.clip(card, 0, 1) * 255 + 0.5).astype(np.uint8))
        d = ImageDraw.Draw(img)
        d.line([(split, 0), (split, CARD[1])], fill=(255, 255, 255), width=3)
        d.ellipse([split - 14, CARD[1] / 2 - 14, split + 14, CARD[1] / 2 + 14], fill=(255, 255, 255))
        d.polygon([(split - 8, CARD[1] / 2), (split - 3, CARD[1] / 2 - 5), (split - 3, CARD[1] / 2 + 5)], fill=(40, 40, 48))
        d.polygon([(split + 8, CARD[1] / 2), (split + 3, CARD[1] / 2 - 5), (split + 3, CARD[1] / 2 + 5)], fill=(40, 40, 48))
        img.save(folder / "thumbnail.png", optimize=True)
    except Exception as e:  # keep the others going
        return f"{lid}: FAILED {e!r}"
    meta = {"id": lid, "names": {"es": es, "en": en}, "category": cat, "tags": tags + ["lut", "filtro", "filter", "color", "look"],
            "durationSec": 0, "width": CARD[0], "height": CARD[1]}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return f"{lid}: {(folder / f'{lid}.cube').stat().st_size / 1e3:.0f} kB"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    only = {i for i in args.only.split(",") if i}
    todo = [l for l in looks.LOOKS if not only or l[0] in only]
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(min(args.jobs, len(todo))) as pool:
        for line in pool.imap_unordered(build, todo):
            if "FAILED" in line:
                print(line, flush=True)
    print(len(todo), "LUTs ->", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
