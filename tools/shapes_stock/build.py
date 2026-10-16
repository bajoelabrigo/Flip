"""Builds the 200 shapes of Stock › Formas (for the 0.14.0 «shape» delivery).

    py tools/shapes_stock/build.py [--only id,id]

<out>/<id>/<id>.json       what Stock downloads; the app installs it into AppData/shapes (format 1)
<out>/<id>/thumbnail.png   512 x 512 card
<out>/<id>/meta.json
and a contact sheet at tienda/formas/catalogo.png. <out> is tienda/formas/paquetes.

The path is an SVG "d" on a 0..100 box the shape fills on both axes (absolute M L Q C Z only);
`aspect` (w / h) is the box the app lays it out in. Every path is parsed back and checked.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geometry as g  # noqa: E402
from i18n import CATEGORY_NAMES, CATEGORY_SINGULAR, OTHER_LANGS  # noqa: E402
from shapes import SHAPES  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "formas"
OUT = ROOT / "paquetes"
CARD = 512
SS = 4  # supersampling

COLORS = {
    "hearts": ("#FF4D6D", "#C9184A"), "stars": ("#FFD60A", "#F48C06"), "bubbles": ("#4CC9F0", "#4361EE"),
    "clouds": ("#CFE6FF", "#7FA8E0"), "paper": ("#F4EBDD", "#C8B596"), "arrows": ("#FF8A4C", "#E0401E"),
    "badges": ("#A06CF0", "#6A2CBF"), "seals": ("#F15BB5", "#B5179E"), "frames": ("#2EE6C5", "#00A08A"),
    "nature": ("#86EFA0", "#2D9A5B"), "waves": ("#56CFE8", "#0077B6"), "splash": ("#FFB703", "#FB5607"),
    "shields": ("#7B7FF0", "#3A0CA3"), "labels": ("#FFA62B", "#E85D04"), "symbols": ("#18D9A6", "#118AB2"),
    "geometric": ("#A8C8FF", "#5A7DFF"),
}


def realize(shape):
    """(fills, holes) normalised to 0..100, the aspect, and the SVG string."""
    built = shape["build"]()
    fills, holes = built if isinstance(built, tuple) else (built, [])
    x0, y0, x1, y1 = g.bbox(fills)
    w, h = x1 - x0, y1 - y0
    f = lambda p: ((p[0] - x0) / w * 100.0, (p[1] - y0) / h * 100.0)  # noqa: E731
    fills = g.transform(fills, f)
    holes = g.transform(holes, f)
    if shape["rule"] == "nonzero":
        fills = [sp if g.signed_area(g.flatten_sub(sp, 8)) >= 0 else g.reverse_sub(sp) for sp in fills]
        holes = [sp if g.signed_area(g.flatten_sub(sp, 8)) < 0 else g.reverse_sub(sp) for sp in holes]
    return fills, holes, w / h, g.to_svg(fills + holes)


def mask_of(subpaths, box, size):
    """Union / XOR helper: one boolean mask per subpath, drawn into `box` (x, y, w, h) of `size`."""
    bx, by, bw, bh = box
    out = []
    for sp in subpaths:
        pts = [(bx + x / 100.0 * bw, by + y / 100.0 * bh) for x, y in g.flatten_sub(sp, 24)]
        im = Image.new("L", size, 0)
        ImageDraw.Draw(im).polygon(pts, fill=255)
        out.append(np.asarray(im) > 127)
    return out


def coverage(path_d, rule, box, size):
    """Rasterises the serialised path (so the card shows exactly what the app will get)."""
    subs = g.parse_svg(path_d)
    masks = mask_of(subs, box, size)
    if rule == "evenodd":
        acc = np.zeros(size[::-1], bool)
        for m in masks:
            acc ^= m
        return acc
    fill = np.zeros(size[::-1], bool)
    hole = np.zeros(size[::-1], bool)
    for sp, m in zip(subs, masks):
        if g.signed_area(g.flatten_sub(sp, 8)) >= 0:
            fill |= m
        else:
            hole |= m
    return fill & ~hole


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def card(path_d, rule, aspect, fill, deep, side=CARD):
    S = side * SS
    margin = 0.12 * S
    avail = S - 2 * margin
    bw, bh = (avail, avail / aspect) if aspect >= 1 else (avail * aspect, avail)
    box = ((S - bw) / 2, (S - bh) / 2, bw, bh)
    cov = coverage(path_d, rule, box, (S, S))
    bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.08), fill=(31, 33, 40, 255))
    top, bot = np.array(hex_rgb(fill), np.float32), np.array(hex_rgb(deep), np.float32)
    t = np.clip((np.arange(S, dtype=np.float32) - box[1]) / max(1.0, box[3]), 0, 1)[:, None, None]
    grad = top * (1 - t) + bot * t
    rgb = np.broadcast_to(grad, (S, S, 3)).copy()
    base = np.asarray(bg).astype(np.float32)
    a = cov[..., None].astype(np.float32)
    base[..., :3] = base[..., :3] * (1 - a) + rgb * a
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8), "RGBA")
    return img.resize((side, side), Image.LANCZOS)


def names_for(shape, index_in_cat):
    names = {"es": shape["es"], "en": shape["en"]}
    for lang in OTHER_LANGS:
        names[lang] = f"{CATEGORY_SINGULAR[shape['category']][lang]} {index_in_cat}"
    return names


def build_all(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    per_cat = {}
    results = []
    for shape in SHAPES:
        per_cat[shape["category"]] = per_cat.get(shape["category"], 0) + 1
        idx = per_cat[shape["category"]]
        if only and shape["id"] not in only:
            continue
        fills, holes, aspect, d = realize(shape)
        # Checks: parses back, stays in the box, not degenerate, not too big.
        back = g.parse_svg(d)
        assert len(back) == len(fills) + len(holes), shape["id"]
        x0, y0, x1, y1 = g.bbox(back)
        assert -0.6 <= x0 and x1 <= 100.6 and -0.6 <= y0 and y1 <= 100.6, (shape["id"], x0, y0, x1, y1)
        assert len(d) < 6500, (shape["id"], len(d))
        area = sum(abs(g.signed_area(g.flatten_sub(sp, 8))) for sp in back)
        assert area > 300, (shape["id"], area)
        fill, deep = COLORS[shape["category"]]
        cat = shape["category"]
        doc = {"format": 1, "id": shape["id"], "names": names_for(shape, idx), "category": cat,
               "categoryNames": CATEGORY_NAMES[cat], "aspect": round(aspect, 4), "path": d, "fillRule": shape["rule"],
               "fill": fill, "fillDeep": deep, "tags": shape["tags"]}
        folder = OUT / shape["id"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{shape['id']}.json").write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        img = card(d, shape["rule"], aspect, fill, deep)
        img.save(folder / "thumbnail.png", optimize=True)
        meta = {"id": shape["id"], "names": doc["names"], "category": cat, "categoryNames": CATEGORY_NAMES[cat],
                "order": shape["order"], "tags": shape["tags"], "width": CARD, "height": CARD, "aspect": doc["aspect"]}
        (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        results.append((shape, img))
    return results


def contact_sheet(results, path, cols=20, cell=128):
    rows = math.ceil(len(results) / cols)
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 16)), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except OSError:
        font = ImageFont.load_default()
    for i, (shape, img) in enumerate(results):
        x, y = (i % cols) * cell, (i // cols) * (cell + 16)
        sheet.paste(img.resize((cell - 4, cell - 4), Image.LANCZOS).convert("RGB"), (x + 2, y + 2))
        d.text((x + 3, y + cell), shape["id"][:22], fill=(200, 200, 210), font=font)
    sheet.save(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {i for i in args.only.split(",") if i}
    ids = [s["id"] for s in SHAPES]
    assert len(ids) == len(set(ids)) == 200, (len(ids), len(set(ids)))
    for sid in ids:
        assert __import__("re").fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", sid), sid
    results = build_all(only)
    if not only:
        contact_sheet(results, ROOT / "catalogo.png")
    print(f"{len(results)} shapes -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
