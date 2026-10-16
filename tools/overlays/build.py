"""Renders the overlays of Stock › Superposiciones.

    py tools/overlays/build.py [--only id,id] [--jobs 6]

<out>/<id>/<id>.webm       1080 x 1920, VP9 with alpha, 30 fps (what Stock downloads)
<out>/<id>/meta.json       names, category, tags, duration, loop
<out>/<id>/thumbnail.png   432 x 768 card: the overlay over a sample photo
<out>/<id>/preview.mp4     360 x 640 hover preview over the same photo
<out>/../catalogo.png      contact sheet of every card

The sample photos (Pexels, see CREDITS.json in muestras) only appear in cards and previews: the
overlay itself is transparent and ours.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import designs  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
OUT = ROOT / "superposiciones" / "paquetes"
SAMPLES = ROOT / "plantillas" / "muestras"
FPS = 30
FULL = (1080, 1920)
THUMB = (432, 768)
PREV = (360, 640)


def cover(path: Path, size) -> Image.Image:
    im = Image.open(path).convert("RGB")
    w, h = size
    scale = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def over(photo: Image.Image, rgba: np.ndarray, size) -> Image.Image:
    layer = Image.fromarray(rgba, "RGBA").convert("RGBa").resize(size, Image.BICUBIC).convert("RGBA")
    out = photo.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def build(d: designs.Design) -> str:
    t0 = time.time()
    folder = OUT / d.id
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(sum(map(ord, d.id)) * 7919)
    w, h = d.res
    frame = d.make(w, h, d.seconds, rng)
    n = int(round(d.seconds * FPS))
    photo_t = cover(SAMPLES / d.sample, THUMB)
    photo_p = cover(SAMPLES / d.sample, PREV)

    webm = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(FPS),
         "-i", "-", "-vf", f"scale={FULL[0]}:{FULL[1]}:flags=bicubic", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
         "-crf", str(d.crf), "-b:v", "0", "-row-mt", "1", "-cpu-used", "4", "-deadline", "good", "-auto-alt-ref", "0",
         "-an", str(folder / f"{d.id}.webm")], stdin=subprocess.PIPE)
    prev = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{PREV[0]}x{PREV[1]}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-preset", "medium",
         "-movflags", "+faststart", "-an", str(folder / "preview.mp4")], stdin=subprocess.PIPE)
    thumb_frame = int(d.thumb_at * (n - 1))
    for i in range(n):
        rgba = frame(i / FPS).to_rgba8()
        webm.stdin.write(rgba.tobytes())
        prev.stdin.write(np.asarray(over(photo_p, rgba, PREV)).tobytes())
        if i == thumb_frame:
            over(photo_t, rgba, THUMB).save(folder / "thumbnail.png", optimize=True)
    for p in (webm, prev):
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError(f"ffmpeg failed for {d.id}")
    meta = {"id": d.id, "names": d.names, "category": d.category, "durationSec": d.seconds, "loop": d.loop,
            "tags": d.tags, "width": FULL[0], "height": FULL[1], "fps": FPS}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    size = (folder / f"{d.id}.webm").stat().st_size
    return f"{d.id}: {n} frames, {size / 1e6:.1f} MB, {time.time() - t0:.0f} s"


def _run(did: str) -> str:
    try:
        return build(designs.DESIGNS[did])
    except Exception as e:  # keep the others going
        return f"{did}: FAILED {e!r}"


def contact_sheet():
    cards = sorted(p for p in OUT.iterdir() if (p / "thumbnail.png").exists())
    cols = 8
    tw, th = 216, 384
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (24, 24, 28))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    for i, p in enumerate(cards):
        im = Image.open(p / "thumbnail.png").resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + th + 4), p.name, fill=(220, 220, 220))
    sheet.save(OUT.parent / "catalogo.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()
    ids = [i for i in args.only.split(",") if i] or list(designs.DESIGNS)
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(min(args.jobs, len(ids))) as pool:
        for line in pool.imap_unordered(_run, ids):
            print(line, flush=True)
    contact_sheet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
