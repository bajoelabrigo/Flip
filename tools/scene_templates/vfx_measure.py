"""Measures a reference VFX element frame by frame (study only: docs/plan-vfx.md) so ours can be rebuilt to the same
silhouette sizes, motion and timing with our own shapes.

    py tools/scene_templates/vfx_measure.py VIDEO START DUR w:h:x:y OUT.json [--thr 70]

For every native frame of the crop: the liquid mask (turquoise / white pixels on the dark background), its pieces
(connected components bigger than a few px) with centroid, area, bounding box, the ellipse that fits each, and a
coarse outline description (the first few Fourier harmonics of its radius about the centroid, so a lobe or a neck
shows); plus which frames are new drawings (the picture changed) and which hold. Nothing of the picture itself is
kept.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import tempfile

import cv2
import numpy as np

HARMONICS = 5


def liquid_mask(rgb, thr):
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    teal = (g > thr) & (b > thr - 10) & (g - r > 18)
    white = (r > 170) & (g > 170) & (b > 170)
    return (teal | white).astype(np.uint8)


def describe(contour, cx, cy):
    """Radius about the centroid at 64 angles → mean radius and the first harmonics (amplitude, phase)."""
    pts = contour.reshape(-1, 2).astype(float)
    ang = np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx)
    rad = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)
    bins = np.linspace(-np.pi, np.pi, 65)
    prof = []
    for i in range(64):
        sel = (ang >= bins[i]) & (ang < bins[i + 1])
        prof.append(float(rad[sel].max()) if sel.any() else np.nan)
    prof = np.array(prof)
    if np.isnan(prof).all():
        return 0.0, []
    idx = np.arange(64)
    good = ~np.isnan(prof)
    prof = np.interp(idx, idx[good], prof[good], period=64)
    spec = np.fft.rfft(prof) / 64
    harm = [(float(2 * abs(spec[k])), float(np.angle(spec[k]))) for k in range(1, HARMONICS + 1)]
    return float(abs(spec[0])), harm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("start", type=float)
    ap.add_argument("dur", type=float)
    ap.add_argument("crop")
    ap.add_argument("out")
    ap.add_argument("--thr", type=int, default=70)
    ap.add_argument("--min-area", type=int, default=6)
    args = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="vfxmeasure_")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(args.start), "-t", str(args.dur), "-i", args.video,
                    "-vf", f"crop={args.crop}", os.path.join(tmp, "f%04d.png")], check=True)
    files = sorted(glob.glob(os.path.join(tmp, "f*.png")))
    frames, prev = [], None
    for i, f in enumerate(files):
        rgb = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB)
        mask = liquid_mask(rgb, args.thr)
        new = prev is None or float(np.abs(mask.astype(int) - prev.astype(int)).mean()) > 0.0015
        prev = mask
        n, labels, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
        pieces = []
        for k in range(1, n):
            area = int(stats[k, cv2.CC_STAT_AREA])
            if area < args.min_area:
                continue
            comp = (labels == k).astype(np.uint8)
            cs, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            c = max(cs, key=cv2.contourArea)
            cx, cy = float(cents[k][0]), float(cents[k][1])
            r0, harm = describe(c, cx, cy)
            ell = cv2.fitEllipse(c) if len(c) >= 5 else ((cx, cy), (2.0, 2.0), 0.0)
            holes = 0
            cs2, hier = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            if hier is not None:
                holes = int(sum(1 for j, h in enumerate(hier[0]) if h[3] >= 0 and cv2.contourArea(cs2[j]) > 8))
            x, y, w, h = (int(stats[k, cv2.CC_STAT_LEFT]), int(stats[k, cv2.CC_STAT_TOP]),
                          int(stats[k, cv2.CC_STAT_WIDTH]), int(stats[k, cv2.CC_STAT_HEIGHT]))
            # A coarse outline (a handful of points, about one every 3 % of the way round) for our own smooth redraw;
            # the holes the same way.
            eps = max(1.2, 0.03 * cv2.arcLength(c, True))
            poly = cv2.approxPolyDP(c, eps, True).reshape(-1, 2).tolist()
            hole_polys = []
            if hier is not None:
                for j, hh in enumerate(hier[0]):
                    if hh[3] >= 0 and cv2.contourArea(cs2[j]) > 8:
                        e2 = max(1.0, 0.05 * cv2.arcLength(cs2[j], True))
                        hole_polys.append(cv2.approxPolyDP(cs2[j], e2, True).reshape(-1, 2).tolist())
            pieces.append({"poly": poly, "holes_poly": hole_polys,
                           "cx": round(cx, 1), "cy": round(cy, 1), "area": area, "box": [x, y, w, h],
                           "ellipse": [round(ell[1][0], 1), round(ell[1][1], 1), round(ell[2], 1)],
                           "r0": round(r0, 2), "harm": [[round(a, 2), round(p, 3)] for a, p in harm],
                           "holes": holes})
        pieces.sort(key=lambda p: -p["area"])
        frames.append({"i": i, "t": round(i / 30.0, 4), "new": bool(new),
                       "area": int(mask.sum()), "pieces": pieces})
    json.dump({"start": args.start, "crop": args.crop, "fps": 30, "frames": frames}, open(args.out, "w"), indent=0)
    drawings = sum(1 for f in frames if f["new"])
    print(f"{len(frames)} frames, {drawings} drawings; area " +
          " ".join(str(f["area"] // 10) for f in frames[::3]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
