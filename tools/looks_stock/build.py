"""Builds the looks of Stock › Looks (one-click «Ajustar» presets) and renders their cards with the app.

    py tools/looks_stock/build.py [--only id,id] [--no-render]

<out>/<id>/<id>.json        the effect-stack preset (what Stock downloads; AppController::importUserEffectPreset)
<out>/<id>/thumbnail.png    768 x 432 card: the sample photo, original on the left, the look on the right,
                            both frames rendered by the app (so glow, grain and vignette are the real ones)
<out>/<id>/meta.json
<out>/../catalogo-*.png     contact sheets

One project holds every look as a clip of its sample photo with the look's effects (and one clip of each
photo without them); the app renders a frame of each.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "transitions_stock"))
sys.path.append(str(HERE.parent / "scene_templates"))

import designs  # noqa: E402
from scene import Box, cover, layout  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
OUT = ROOT / "looks" / "paquetes"
WORK = ROOT / "looks" / "trabajo"
SAMPLES = ROOT / "plantillas" / "muestras"
W, H = 1280, 720
CARD = (768, 432)
SPLIT = 0.38

# Brand-carrying or local-only sample photos (CLAUDE.md, scene_templates/kit.BLOCKED and the LUT cards).
NO = {"h-desk-01", "h-community-03", "h-truck-02", "h-soccer-04", "h-product-02", "h-studio-03", "h-gaming-04",
      "h-tools-01", "bakery-01", "winter-02", "spring-03", "skincare-01", "music-01", "product-01", "product-02",
      "product-03", "product-04", "gym-03", "fashion-05", "fashion-06", "family-06", "barber-04", "nails-01",
      "skate-02", "skate-03", "sport-01", "sport-02", "sport-03", "restaurant-05", "car-01", "car-02", "car-03",
      "city-03", "city-04", "h-travel-04", "h-travel-05", "coffee-02", "cake-03", "fashion-03",
      "h-city-02", "friends-08"}


def brightness(path: Path) -> float:
    with Image.open(path) as im:
        return float(np.asarray(im.convert("L").resize((64, 36)), np.float32).mean() / 255)


# Hand-picked pools where the theme's own photos do not suit a card (sunset skylines for «city», cars on
# most travel photos, a character toy on a cake).
POOLS = {
    "city": ["h-city-04", "h-city-06", "h-house-03", "h-shop-01", "night-04"],
    "night": ["night-01", "night-03", "night-04", "concert-03", "h-christmas-04"],
    "travel": ["h-travel-02", "h-travel-07", "h-nature-02", "h-nature-06", "h-beach-04"],
    "fashion": ["fashion-02", "fashion-04", "man-04", "h-man-05"],
    "man": ["h-man-01", "h-man-04", "h-man-05", "man-04"],
    "friends": ["h-birthday-02", "friends-07", "friends-11", "friends-12", "friends-03"],
    "coffee": ["coffee-01", "coffee-03", "h-cafe-04"],
    "cake": ["cake-01", "h-birthday-04", "h-birthday-05"],
    "flowers": ["h-spring-01", "h-spring-02", "h-spring-03"],
}


def sample_for(look) -> Path:
    """A mid-bright landscape photo of the look's theme (a portrait one when there is no landscape set)."""
    theme = "night" if look.category == "noche" and look.theme == "city" else look.theme
    if theme in POOLS:
        pool = [SAMPLES / f"{n}.jpg" for n in POOLS[theme]]
        return pool[zlib.crc32(look.id.encode()) % len(pool)]
    pool = [p for p in sorted(SAMPLES.glob(f"h-{theme}-*.jpg")) if p.stem not in NO]
    if not pool:
        pool = [p for p in sorted(SAMPLES.glob(f"{theme}-*.jpg")) if p.stem not in NO]
    lo, hi = (0.2, 0.75) if look.category in ("noche", "moody") else (0.3, 0.72)
    good = [p for p in pool if lo <= brightness(p) <= hi]
    pool = good or pool or [SAMPLES / "h-nature-01.jpg"]
    return pool[zlib.crc32(look.id.encode()) % len(pool)]


def clip(path: Path, t0: float, effects: list) -> tuple[dict, dict]:
    with Image.open(path) as im:
        pw, ph = im.size
    aid = f"a-{path.stem}"
    asset = {"id": aid, "kind": "image", "name": path.name, "path": str(path), "width": pw, "height": ph}
    c = {"id": f"c{t0:g}", "type": "image", "assetId": aid, "path": str(path), "timelineStartUs": round(t0 * 1e6),
         "timelineDurationUs": 1_000_000, "srcInUs": 0, "srcOutUs": 1_000_000, "sourceFrame": cover(pw, ph, W, H),
         "effects": effects, **layout(Box(0, 0, W, H), None)}
    return asset, c


def card(original: Image.Image, graded: Image.Image) -> Image.Image:
    a = original.convert("RGB").resize(CARD, Image.LANCZOS)
    img = graded.convert("RGB").resize(CARD, Image.LANCZOS)
    split = int(CARD[0] * SPLIT)
    img.paste(a.crop((0, 0, split, CARD[1])), (0, 0))
    d = ImageDraw.Draw(img)
    cy = CARD[1] / 2
    d.line([(split, 0), (split, CARD[1])], fill=(255, 255, 255), width=3)
    d.ellipse([split - 14, cy - 14, split + 14, cy + 14], fill=(255, 255, 255))
    d.polygon([(split - 8, cy), (split - 3, cy - 5), (split - 3, cy + 5)], fill=(40, 40, 48))
    d.polygon([(split + 8, cy), (split + 3, cy - 5), (split + 3, cy + 5)], fill=(40, 40, 48))
    return img


def contact_sheets(looks) -> None:
    cards = [OUT / l.id for l in looks if (OUT / l.id / "thumbnail.png").exists()]
    per, cols, tw, th = 48, 6, 320, 180
    for page in range(0, len(cards), per):
        chunk = cards[page:page + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (22, 22, 26))
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(chunk):
            x, y = (i % cols) * tw, (i // cols) * (th + 18)
            sheet.paste(Image.open(c / "thumbnail.png").convert("RGB").resize((tw, th)), (x, y))
            d.text((x + 4, y + th + 3), c.name, fill=(225, 225, 225))
        sheet.save(OUT.parent / f"catalogo-{page // per + 1}.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    looks = [l for l in designs.LOOKS if not only or l.id in only]
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    for look in looks:
        folder = OUT / look.id
        folder.mkdir(exist_ok=True)
        (folder / f"{look.id}.json").write_text(json.dumps(look.preset(), ensure_ascii=False, indent=1), encoding="utf-8")
        meta = {"id": look.id, "names": {"es": look.es, "en": look.en}, "category": look.category,
                "categoryNames": designs.CATEGORIES[look.category], "sample": sample_for(look).stem,
                "effects": [e["catalogId"] for e in look.effects()],
                "tags": sorted(set(look.tags + ["look", "filtro", "filter", "ajustar", "color", "preset",
                                                designs.CATEGORIES[look.category]["es"].lower()])),
                "width": CARD[0], "height": CARD[1]}
        (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(looks)} looks written to {OUT}", flush=True)
    if args.no_render:
        contact_sheets(designs.LOOKS)
        return 0

    # One timeline: the bare photos first, then every look.
    photos = sorted({sample_for(l) for l in looks})
    assets, clips, at = {}, [], {}
    t = 0.0
    for p in photos:
        a, c = clip(p, t, [])
        assets[a["id"]] = a
        clips.append(c)
        at[("photo", p)] = t + 0.5
        t += 1.0
    for look in looks:
        a, c = clip(sample_for(look), t, look.effects())
        assets[a["id"]] = a
        clips.append(c)
        at[("look", look.id)] = t + 0.5
        t += 1.0
    doc = {"version": 14, "projectName": "Looks", "width": W, "height": H, "fps": 30, "sampleRate": 48000,
           "background": {"kind": "color", "color": "#ff000000"}, "assets": list(assets.values()),
           "tracks": [{"id": "t-video", "type": "video", "name": "Video", "clips": clips, "transitions": []}]}
    project = WORK / "looks.json"
    project.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    import appsession
    frames = WORK / "frames"
    frames.mkdir(exist_ok=True)
    with appsession.session(WORK) as app:
        if not app.load(project):
            return 1
        for p in photos:
            app.capture(at[("photo", p)], frames / f"_{p.stem}.png")
        for look in looks:
            if app.capture(at[("look", look.id)], frames / f"{look.id}.png"):
                print(f"rendered {look.id}", flush=True)
    for look in looks:
        graded = frames / f"{look.id}.png"
        original = frames / f"_{sample_for(look).stem}.png"
        if graded.exists() and original.exists():
            with Image.open(original) as o, Image.open(graded) as g:
                card(o, g).save(OUT / look.id / "thumbnail.png", optimize=True)
    contact_sheets(designs.LOOKS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
