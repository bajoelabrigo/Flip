"""Renders the animated backgrounds of Stock › Fondos.

    py tools/backgrounds/build.py [--only id,id|prefix*] [--jobs 8]

<out>/<id>/<id>.mp4        1080 x 1920 H.264, 30 fps, seamless loop (what Stock downloads)
<out>/<id>/thumbnail.png   432 x 768 card
<out>/<id>/preview.mp4     360 x 640 hover preview
<out>/<id>/meta.json
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
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import designs  # noqa: E402

OUT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "fondos" / "paquetes"
FPS = 30
FULL = (1080, 1920)
THUMB = (432, 768)
PREV = (360, 640)


def to8(rgb):
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)


def build(bid: str) -> str:
    t0 = time.time()
    b = designs.BACKGROUNDS[bid]
    folder = OUT / bid
    folder.mkdir(parents=True, exist_ok=True)
    w, h = b.res
    rng = np.random.default_rng(sum(map(ord, bid.split("-")[0])) * 7919)   # palettes share the motif's layout
    try:
        frame = b.make(w, h, b.seconds, rng, b.pal)
        n = int(round(b.seconds * FPS))
        enc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
             "-i", "-", "-vf", f"scale={FULL[0]}:{FULL[1]}:flags=bicubic,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
             "-crf", "20", "-tune", "film", "-movflags", "+faststart", "-an", str(folder / f"{bid}.mp4")], stdin=subprocess.PIPE)
        prev = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
             "-i", "-", "-vf", f"scale={PREV[0]}:{PREV[1]}:flags=bicubic,format=yuv420p", "-c:v", "libx264", "-crf", "26",
             "-movflags", "+faststart", "-an", str(folder / "preview.mp4")], stdin=subprocess.PIPE)
        thumb_i = int(0.4 * n)
        for i in range(n):
            img = to8(frame(i / FPS))
            data = img.tobytes()
            enc.stdin.write(data)
            prev.stdin.write(data)
            if i == thumb_i:
                Image.fromarray(img).resize(THUMB, Image.BICUBIC).save(folder / "thumbnail.png", optimize=True)
        for p in (enc, prev):
            p.stdin.close()
            if p.wait() != 0:
                raise RuntimeError("ffmpeg failed")
    except Exception as e:
        return f"{bid}: FAILED {e!r}"
    meta = {"id": bid, "names": b.names, "category": b.category, "durationSec": b.seconds, "loop": True, "tags": b.tags,
            "width": FULL[0], "height": FULL[1], "fps": FPS}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    size = (folder / f"{bid}.mp4").stat().st_size
    return f"{bid}: {size / 1e6:.1f} MB, {time.time() - t0:.0f} s"


def select(spec: str):
    if not spec:
        return list(designs.BACKGROUNDS)
    out = []
    for s in spec.split(","):
        out += [i for i in designs.BACKGROUNDS if i == s or (s.endswith("*") and i.startswith(s[:-1]))]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    ids = select(args.only)
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(min(args.jobs, len(ids))) as pool:
        for line in pool.imap_unordered(build, ids):
            print(line, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
