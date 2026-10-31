"""Measures a lower third of the reference video frame by frame (30 fps): for each band of rows, the runs of warm
(orange-red) and of white columns, or for a vertical band the runs of rows. Saves lt_ref/<name>.json, which the
templates read (lt_motion.Ref), so a bar or a text moves exactly as in the reference.

    py lt_measure.py <video> <name> <start> <seconds> [fps=25] band=x0,y0,x1,y1[,v] ...

fps=N keeps the video's own frame rate (no frames repeated or dropped); a smaller video is scaled to 1920×1080
first, so the bands are always in 1080p pixels.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

W, H = 1920, 1080


def runs(mask, offset, minlen=2):
    out, s = [], None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        if not v and s is not None:
            if i - s >= minlen:
                out.append([s + offset, i - 1 + offset])
            s = None
    if s is not None and len(mask) - s >= minlen:
        out.append([s + offset, len(mask) - 1 + offset])
    return out


def main():
    video, name, start, seconds = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    bands, fps = {}, 30
    for arg in sys.argv[5:]:
        key, spec = arg.split("=")
        if key == "fps":
            fps = int(spec)
            continue
        parts = spec.split(",")
        bands[key] = ([int(v) for v in parts[:4]], len(parts) > 4 and parts[4] == "v",
                      float(parts[5]) if len(parts) > 5 else 0.3)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", str(seconds), "-vf", f"scale={W}:{H}:flags=bicubic,fps={fps}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frames = []
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        a = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(int)
        row = {}
        for key, ((x0, y0, x1, y1), vertical, share) in bands.items():
            c = a[y0:y1, x0:x1]
            warm = (c[..., 0] > 160) & (c[..., 2] < 110) & (c[..., 0] - c[..., 1] > 40)
            white = (c > 200).all(-1)
            axis = 1 if vertical else 0
            off = y0 if vertical else x0
            row[key] = {"warm": runs(warm.mean(axis) > 0.5, off), "white": runs(white.mean(axis) > share, off)}
        frames.append(row)
    out = Path(__file__).with_name("lt_ref") / f"{name}.json"
    out.write_text(json.dumps({"start": start, "fps": fps, "frames": frames}, separators=(",", ":")), encoding="utf-8")
    print(f"{out.name}: {len(frames)} frames")


if __name__ == "__main__":
    main()
