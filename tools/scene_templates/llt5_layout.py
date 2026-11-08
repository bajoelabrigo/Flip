"""Measures the rest layout of each lower third of 49176330.mp4 from a still frame: the photo's white frame (square
or round), the grey and dark bands, and every line of white text (ink box, outlined or filled).

    py llt5_layout.py <still.png> [...]
"""

from __future__ import annotations

import sys

import cv2
import numpy as np
from PIL import Image

GREY = (111, 113, 127)
DARK = (48, 49, 54)


def near(a, colour, tol=16):
    return (np.abs(a[..., 0] - colour[0]) < tol) & (np.abs(a[..., 1] - colour[1]) < tol) & \
        (np.abs(a[..., 2] - colour[2]) < tol)


def blobs(mask, min_area, close=(5, 25)):
    m = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones(close, np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    return [tuple(int(v) for v in (st[j, 0], st[j, 1], st[j, 0] + st[j, 2], st[j, 1] + st[j, 3]))
            for j in range(1, n) if st[j, 4] >= min_area]


def measure(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)[:1000]
    white = a.min(2) > 225
    out = {}
    # The photo's frame: a square one is the white rows/columns with a run of 300+ px; a round one is the biggest
    # white ring (a blob of white whose box is about square and mostly empty inside).
    def longest_run(v):
        best = cur = 0
        for on in v:
            cur = cur + 1 if on else 0
            best = max(best, cur)
        return best
    rows = [yy for yy in range(white.shape[0]) if white[yy].sum() > 300 and longest_run(white[yy]) > 300]
    cols = [xx for xx in range(white.shape[1]) if white[:, xx].sum() > 300 and longest_run(white[:, xx]) > 300]
    if rows and cols:
        out["frame"] = (min(cols), min(rows), max(cols) + 1, max(rows) + 1)
        out["round"] = False
    else:
        n, lab, st, _ = cv2.connectedComponentsWithStats(white.astype(np.uint8))
        best = None
        for j in range(1, n):
            x, y, w, h = (int(v) for v in st[j, :4])
            if w > 250 and abs(w - h) < 20 and st[j, 4] < 0.3 * w * h and (best is None or w > best[2] - best[0]):
                best = (x, y, x + w, y + h)
        out["frame"] = best
        out["round"] = True
    fx0, fy0, fx1, fy1 = out["frame"] or (0, 0, 0, 0)
    out["grey"] = blobs(near(a, GREY), 1500)
    out["dark"] = blobs(near(a, DARK, 10), 3000, close=(3, 3))
    # Text: white ink outside the frame, grouped in lines by rows.
    ink = white.copy()
    ink[fy0:fy1, fx0:fx1] = False
    rows = ink.sum(1) > 0
    lines, start = [], None
    for yy, on in enumerate(list(rows) + [False]):
        if on and start is None:
            start = yy
        elif not on and start is not None:
            if yy - start >= 8:
                cs = np.nonzero(ink[start:yy].sum(0) > 0)[0]
                filled = ink[start:yy, cs.min():cs.max() + 1].mean()
                lines.append({"box": (int(cs.min()), start, int(cs.max() + 1), yy), "fill": round(float(filled), 2)})
            start = None
    out["text"] = lines
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = measure(p)
        print(p.split("/")[-1], "frame", m["frame"], "round" if m["round"] else "square")
        for g in m["grey"]:
            print("   grey", g)
        for d in m["dark"]:
            print("   dark", d)
        for t in m["text"]:
            print("   text", t["box"], "fill", t["fill"])
