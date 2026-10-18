"""The "before" photo of each effect card (0.18): the hover preview on Effects wipes between it and the
thumbnail, as Filters does with the LUTs.

    py tools/effects/before_bases.py <drift-addons>/assets/thumbs [--check out.png]

Picks, for every effects/<name>/effect.json, the photo its thumbnail was rendered from with the same rules
as tools/effectthumbs.cpp (tools/effects/thumb_bases.json: per effect, then a face category for face effects, chroma for the
keyer, then the category, then the default), crops it square to 256 px like `squareCrop`, and writes
resources/effectbases/<photo>.jpg plus resources/effectbases/map.json (effect id -> photo). An effect is
left out when its thumbnail does not look like its photo at all (the closest of the photos is another
one): then the card keeps its plain thumbnail.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "resources" / "effectbases"
SIZE = 256
# Thumbnails that are not the photo with the effect on it: a badge drawn over (face swap), a title the
# subject hides (behind subject).
SKIP = {"face_swap", "behind_subject"}
# Checked by eye (2026-10-18): the photo is right, but the effect leaves too few edges for the check.
# The LUT cards' photos (AppController::lutThumbnail picks one per look): always written.
LUT_PHOTOS = ["landscape.jpg", "sunset.jpg", "city-night.jpg", "portrait.jpg", "tulips.jpg", "vintage-car.jpg",
              "stag.jpg", "macaw.jpg", "cyclist.jpg", "mountains.jpg", "face-warp.jpg", "beauty.jpg", "aerial.jpg"]
KEEP = {"builtin.effects.gaussian_blur", "stylize.blur", "kaleidoscope", "stylize.pixelate", "strobe_flash"}


def square(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = max(SIZE / w, SIZE / h)
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    w, h = im.size
    x, y = (w - SIZE) // 2, (h - SIZE) // 2
    return im.crop((x, y, x + SIZE, y + SIZE))


def edges(im: Image.Image) -> np.ndarray:
    e = np.asarray(im.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    e -= e.mean()
    return e / (np.linalg.norm(e) + 1e-6)


def main():
    bases_dir = Path(sys.argv[1])
    check = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--check" else None
    rules = json.loads((Path(__file__).resolve().parent / "thumb_bases.json").read_text(encoding="utf-8"))
    photos = {name: square(bases_dir / name) for name in sorted({p.name for p in bases_dir.glob("*.jpg")})}
    photo_edges = {name: edges(im) for name, im in photos.items()}

    def chosen(meta: dict) -> str:
        eid, cat = meta["id"], meta.get("category", "")
        if eid in rules["effects"]:
            return rules["effects"][eid]
        if meta.get("requires") in ("face", "faces") or "face" in str(meta.get("requires", "")):
            return rules["categories"].get(cat, rules["face"])
        if eid == "key.chroma":
            return rules["chroma"]
        return rules["categories"].get(cat, rules["default"])

    mapping, dropped, rows = {}, [], []
    for meta_path in sorted((ROOT / "effects").glob("*/effect.json")):
        folder = meta_path.parent
        thumb = folder / "thumbnail.png"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not thumb.exists() or folder.name in SKIP or meta["id"] in SKIP:
            continue
        pick = chosen(meta)
        t = edges(Image.open(thumb).convert("RGB").resize((SIZE, SIZE)))
        scores = {name: float((t * e).sum()) for name, e in photo_edges.items()}
        best = max(scores, key=scores.get)
        if best != pick and meta["id"] not in KEEP:
            dropped.append((meta["id"], pick, best, round(scores[pick], 2), round(scores[best], 2)))
            continue
        mapping[meta["id"]] = pick
        rows.append((thumb, pick))

    OUT.mkdir(parents=True, exist_ok=True)
    for name in sorted(set(mapping.values()) | set(LUT_PHOTOS)):
        photos[name].save(OUT / name, quality=88)
    (OUT / "map.json").write_text(json.dumps(mapping, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="")
    print(len(mapping), "effects with a before photo;", len(set(mapping.values())), "photos")
    for d in dropped:
        print("left out (thumbnail closer to another photo):", *d)
    if check:
        sheet = Image.new("RGB", (SIZE * 2 * 4, SIZE * ((len(rows) + 3) // 4)))
        for i, (thumb, pick) in enumerate(rows):
            x, y = (i % 4) * SIZE * 2, (i // 4) * SIZE
            sheet.paste(photos[pick], (x, y))
            sheet.paste(Image.open(thumb).convert("RGB").resize((SIZE, SIZE)), (x + SIZE, y))
        sheet.resize((sheet.width // 2, sheet.height // 2)).save(check)


if __name__ == "__main__":
    main()
