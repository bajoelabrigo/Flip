"""Trace the centre lines of the strokes of one colour in a still (2026-11-08, TITLE videos): the strokes come back
as ordered point lists in screen px, plus their width, to rebuild them as custom paths drawn with trim.

    py title_trace.py <frame.png> <#rrggbb> [tolerance] [min_px]

Prints one JSON object per stroke: {"width": px, "points": [[x, y], ...]} with points every ~6 px, walked from one
end to the other (at a crossing it keeps going the straightest way, so loops come out whole).
"""
from __future__ import annotations

import json
import sys

import cv2
import numpy as np


def mask_of(img, colour, tol):
    c = np.array([int(colour[i:i + 2], 16) for i in (5, 3, 1)], np.int32)  # BGR
    d = np.abs(img.astype(np.int32) - c).max(axis=2)
    return (d <= tol).astype(np.uint8)


def thin(m):
    """Zhang-Suen thinning."""
    m = m.copy()
    while True:
        changed = False
        for step in (0, 1):
            p = np.pad(m, 1)
            P2, P3, P4, P5 = p[:-2, 1:-1], p[:-2, 2:], p[1:-1, 2:], p[2:, 2:]
            P6, P7, P8, P9 = p[2:, 1:-1], p[2:, :-2], p[1:-1, :-2], p[:-2, :-2]
            ring = [P2, P3, P4, P5, P6, P7, P8, P9, P2]
            B = sum(x.astype(np.int32) for x in ring[:8])
            A = sum(((ring[i] == 0) & (ring[i + 1] == 1)).astype(np.int32) for i in range(8))
            if step == 0:
                c = (P2 * P4 * P6 == 0) & (P4 * P6 * P8 == 0)
            else:
                c = (P2 * P4 * P8 == 0) & (P2 * P6 * P8 == 0)
            kill = (m == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if kill.any():
                m[kill] = 0
                changed = True
        if not changed:
            return m


def walk(sk):
    """Ordered paths over the skeleton pixels."""
    ys, xs = np.nonzero(sk)
    left = set(zip(xs.tolist(), ys.tolist()))
    nb = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neigh(p):
        return [(p[0] + dx, p[1] + dy) for dx, dy in nb if (p[0] + dx, p[1] + dy) in left]
    paths = []
    while left:
        ends = [p for p in left if len(neigh(p)) == 1]
        p = min(ends) if ends else min(left)
        path, prev_dir = [p], None
        left.discard(p)
        while True:
            cand = neigh(p)
            if not cand:
                # Jump small gaps (crossings eaten by the thinning): look a few px ahead.
                far = [(p[0] + dx, p[1] + dy) for dx in range(-4, 5) for dy in range(-4, 5)
                       if (p[0] + dx, p[1] + dy) in left]
                if not far or prev_dir is None:
                    break
                cand = far
            if prev_dir is None:
                q = cand[0]
            else:
                def score(c):
                    v = np.array([c[0] - p[0], c[1] - p[1]], float)
                    return -float(v @ prev_dir) / (np.linalg.norm(v) + 1e-9)
                q = min(cand, key=score)
            v = np.array([q[0] - p[0], q[1] - p[1]], float)
            v /= np.linalg.norm(v) + 1e-9
            prev_dir = v if prev_dir is None else 0.6 * prev_dir + 0.4 * v
            path.append(q)
            left.discard(q)
            p = q
        paths.append(path)
    return paths


def main():
    img = cv2.imread(sys.argv[1])
    colour = sys.argv[2]
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    min_px = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    m = mask_of(img, colour, tol)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    sk = thin(m)
    for path in walk(sk):
        if len(path) < min_px:
            continue
        width = 2 * float(np.median([dist[y, x] for x, y in path]))
        pts = [path[i] for i in range(0, len(path), 6)] + [path[-1]]
        print(json.dumps({"width": round(width, 1), "points": [[int(x), int(y)] for x, y in pts]}))



def outlines(img_path, colour, tol=60, min_area=150, eps=0.8):
    """The filled outlines of each blob of a colour: [[outer, hole, ...], ...] polygons in screen px (holes so an
    even-odd fill keeps rings and triangles hollow), for doodles that pop in whole."""
    img = cv2.imread(img_path)
    m = mask_of(img, colour, tol)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    blobs = []
    for i in range(1, n):
        if st[i, 4] < min_area:
            continue
        comp = (lab == i).astype(np.uint8)
        cnts, _ = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        polys = []
        for c in cnts:
            if cv2.contourArea(c) < 12:
                continue
            ap = cv2.approxPolyDP(c, eps, True).reshape(-1, 2)
            polys.append([[int(x), int(y)] for x, y in ap])
        x, y, w, h = st[i, :4]
        blobs.append({"box": [int(x), int(y), int(w), int(h)], "polys": polys})
    return blobs

PALETTE = {"pink": "#FB527C", "green": "#62FC01", "purple": "#9C59F6", "orange": "#FCB52B", "yellow": "#FCE454"}


def palette_blobs(img_path, palette=PALETTE, min_sat=70, min_area=120, eps=0.8, close=3):
    """Every saturated pixel goes to its nearest palette colour; returns the filled outlines of each blob as
    [{"name", "colour", "box", "polys"}] (polys: outer + holes, for an even-odd fill)."""
    img = cv2.imread(img_path).astype(np.int32)
    sat = img.max(axis=2) - img.min(axis=2)
    names = list(palette)
    cols = np.array([[int(palette[n][i:i + 2], 16) for i in (5, 3, 1)] for n in names])
    d = ((img[:, :, None, :] - cols[None, None, :, :]) ** 2).sum(axis=3)
    best = d.argmin(axis=2)
    out = []
    for k, name in enumerate(names):
        m = ((best == k) & (sat >= min_sat)).astype(np.uint8)
        m[1040:] = 0  # the credit line at the bottom
        if close:
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            if st[i, 4] < min_area:
                continue
            comp = (lab == i).astype(np.uint8)
            cnts, _ = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            polys = [[[int(x), int(y)] for x, y in cv2.approxPolyDP(c, eps, True).reshape(-1, 2)]
                     for c in cnts if cv2.contourArea(c) >= 12]
            x, y, w, h = st[i, :4]
            out.append({"name": name, "colour": palette[name], "box": [int(x), int(y), int(w), int(h)],
                        "polys": polys})
    return out


if __name__ == "__main__":
    main()
