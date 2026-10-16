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


def wide_sample(name: str) -> Path:
    """A landscape sample of the same theme (h-<theme>-NN.jpg) when there is one."""
    theme = name.split("-")[0]
    found = sorted(SAMPLES.glob(f"h-{theme}-*.jpg"))
    return found[0] if found else SAMPLES / name


def build(d: designs.Design, wide: bool = False) -> str:
    """wide=True renders the 16:9 version (1920 x 1080) as its own item, id + '-h'."""
    t0 = time.time()
    oid = d.id + ("-h" if wide else "")
    full, thumb, prevs = ((FULL[1], FULL[0]), (THUMB[1], THUMB[0]), (PREV[1], PREV[0])) if wide else (FULL, THUMB, PREV)
    folder = OUT / oid
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(sum(map(ord, d.id)) * 7919)
    w, h = (d.res[1], d.res[0]) if wide else d.res
    frame = d.make(w, h, d.seconds, rng)
    n = int(round(d.seconds * FPS))
    sample = wide_sample(d.sample) if wide else SAMPLES / d.sample
    photo_t = cover(sample, thumb)
    photo_p = cover(sample, prevs)

    webm = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(FPS),
         "-i", "-", "-vf", f"scale={full[0]}:{full[1]}:flags=bicubic", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
         "-crf", str(d.crf), "-b:v", "0", "-row-mt", "1", "-cpu-used", "4", "-deadline", "good", "-auto-alt-ref", "0",
         "-an", str(folder / f"{oid}.webm")], stdin=subprocess.PIPE)
    prev = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{prevs[0]}x{prevs[1]}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-preset", "medium",
         "-movflags", "+faststart", "-an", str(folder / "preview.mp4")], stdin=subprocess.PIPE)
    thumb_frame = int(d.thumb_at * (n - 1))
    for i in range(n):
        rgba = frame(i / FPS).to_rgba8()
        webm.stdin.write(rgba.tobytes())
        prev.stdin.write(np.asarray(over(photo_p, rgba, prevs)).tobytes())
        if i == thumb_frame:
            over(photo_t, rgba, thumb).save(folder / "thumbnail.png", optimize=True)
    for p in (webm, prev):
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError(f"ffmpeg failed for {d.id}")
    names = {"es": d.names["es"] + " (horizontal)", "en": d.names["en"] + " (landscape)"} if wide else d.names
    tags = d.tags + (["horizontal", "landscape", "16:9", "youtube"] if wide else ["vertical", "9:16", "reels"])
    meta = {"id": oid, "names": names, "category": d.category, "durationSec": d.seconds, "loop": d.loop,
            "tags": tags, "width": full[0], "height": full[1], "fps": FPS}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    size = (folder / f"{oid}.webm").stat().st_size
    return f"{oid}: {n} frames, {size / 1e6:.1f} MB, {time.time() - t0:.0f} s"


def _run(job) -> str:
    did, wide = job
    try:
        return build(designs.DESIGNS[did], wide)
    except Exception as e:  # keep the others going
        return f"{did}: FAILED {e!r}"


def contact_sheet():
    cards = sorted(p for p in OUT.iterdir() if (p / "thumbnail.png").exists() and not p.name.endswith("-h"))
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
    ap.add_argument("--wide", choices=["no", "yes", "both"], default="no", help="also (or only) the 16:9 versions")
    args = ap.parse_args()
    ids = [i for i in args.only.split(",") if i] or list(designs.DESIGNS)
    jobs = [(i, False) for i in ids] if args.wide in ("no", "both") else []
    jobs += [(i, True) for i in ids] if args.wide in ("yes", "both") else []
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(min(args.jobs, len(jobs))) as pool:
        for line in pool.imap_unordered(_run, jobs):
            print(line, flush=True)
    contact_sheet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
