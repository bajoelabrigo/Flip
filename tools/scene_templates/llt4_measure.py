"""Measures the lower thirds of 50962342.mp4 frame by frame at its own 60 fps: for each frame, the box of the dark
card (#181818, neutral), of the white parts and of the green text, inside a region of the 1920×1080 frame.

    py llt4_measure.py <video> <start s> <frames> <x0,y0,x1,y1> [out.json]

Prints one line per frame: frame, dark box, white box, green box (x0 y0 x1 y1, x1/y1 one past; '-' when absent).
Dark and white are the largest connected blob of the class (opened 3×3); green is every row/column with 3+ pixels.
"""

from __future__ import annotations

import json
import subprocess
import sys

import numpy as np


def classes(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    hi, lo = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    dark = (hi < 33) & (hi - lo < 6)
    white = (lo > 238)
    green = (g > 120) & (g - r > 35) & (g - b > 70)
    return {"dark": dark, "white": white, "green": green}


def box(m, ox, oy, need=3, largest=False):
    if largest:
        import cv2
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        if n <= 1:
            return None
        i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        if st[i, cv2.CC_STAT_AREA] < 30:
            return None
        x, y, w, h = st[i, :4]
        return [int(x + ox), int(y + oy), int(x + w + ox), int(y + h + oy)]
    cols = np.nonzero(m.sum(0) >= need)[0]
    rows = np.nonzero(m.sum(1) >= need)[0]
    if len(cols) == 0 or len(rows) == 0:
        return None
    return [int(cols.min() + ox), int(rows.min() + oy), int(cols.max() + 1 + ox), int(rows.max() + 1 + oy)]


def main():
    video, start, n, region = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    x0, y0, x1, y1 = (int(v) for v in region.split(","))
    w, h = x1 - x0, y1 - y0
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start}", "-i", video, "-frames:v", str(n),
           "-vf", f"crop={w}:{h}:{x0}:{y0}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    out = []
    for i in range(len(raw) // (w * h * 3)):
        a = np.frombuffer(raw, np.uint8, w * h * 3, i * w * h * 3).reshape(h, w, 3)
        c = classes(a)
        row = {"f": i}
        for k, m in c.items():
            row[k] = box(m, x0, y0, largest=(k != "green"))
        out.append(row)
        print(i, *(" ".join(map(str, row[k])) if row[k] else "-" for k in ("dark", "white", "green")), sep=" | ")
    if len(sys.argv) > 5:
        with open(sys.argv[5], "w", newline="") as fh:
            json.dump({"video": video, "start": start, "region": [x0, y0, x1, y1], "frames": out}, fh)


if __name__ == "__main__":
    main()
