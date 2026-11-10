"""Measures a still of a type lower third over video: the lines of white ink (with their own height and width),
red areas, and long white strokes (thin lines), in the band y0..y1.

    py llt6_layout.py <still.png> [y0 y1]
"""

from __future__ import annotations

import sys

import cv2
import numpy as np
from PIL import Image


def main():
    path = sys.argv[1]
    y0, y1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (560, 1080)
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)[y0:y1]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = (a.min(2) > 215)
    red = (r > 170) & (g < 90) & (b < 90)
    # Red areas.
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE,
                                                                      np.ones((5, 5), np.uint8)))
    for j in range(1, n):
        if st[j, 4] > 300:
            x, y, w, h = st[j, :4]
            print(f"red   ({x}, {y + y0}, {x + w}, {y + h + y0})  colour {np.median(a[lab == j], axis=0)}")
    # Thin long white strokes: rows (or columns) whose longest white run exceeds 150 px while the row's ink is thin.
    for yy in range(white.shape[0]):
        row = white[yy]
        best = cur = 0
        start = s = 0
        for xx, on in enumerate(row):
            if on:
                if cur == 0:
                    s = xx
                cur += 1
                if cur > best:
                    best, start = cur, s
            else:
                cur = 0
        if best > 150 and white[max(0, yy - 3):yy + 4, start:start + best].mean() < 0.6:
            print(f"hline y {yy + y0}  x {start}-{start + best}")
    for xx in range(white.shape[1]):
        col = white[:, xx]
        if col.sum() > 60:
            runs = np.diff(np.concatenate([[0], col.astype(int), [0]]))
            st_, en_ = np.nonzero(runs == 1)[0], np.nonzero(runs == -1)[0]
            ln = (en_ - st_).max()
            if ln > 60 and white[:, max(0, xx - 3):xx + 4].mean() < 0.35:
                k = int(np.argmax(en_ - st_))
                print(f"vline x {xx}  y {st_[k] + y0}-{en_[k] + y0}")
    # White text lines: row groups of white ink (ignoring rows that are only a thin stroke).
    ink = white.copy()
    rows = ink.sum(1) > 2
    start = None
    for yy, on in enumerate(list(rows) + [False]):
        if on and start is None:
            start = yy
        elif not on and start is not None:
            if yy - start >= 6:
                cs = np.nonzero(ink[start:yy].sum(0) > 0)[0]
                print(f"text  y {start + y0}-{yy + y0} (h {yy - start})  x {cs.min()}-{cs.max() + 1} "
                      f"fill {ink[start:yy, cs.min():cs.max() + 1].mean():.2f}")
            start = None


if __name__ == "__main__":
    main()
