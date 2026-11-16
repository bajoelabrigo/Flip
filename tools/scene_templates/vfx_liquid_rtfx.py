"""Liquid VFX rebuilt «casi igual» to six elements of the RTFX liquid family (docs/plan-vfx.md «Líquidos»), for Jorge
to judge side by side. Nothing goes to Stock.

    py tools/scene_templates/vfx_liquid_rtfx.py --exe <portable flipstudio.exe> [--only columna,goteo]

Jorge (2026-11-16): «hazlo lo más parecido al original… no inventes nada», as the lower thirds were remade. The
reference video is licensed to Jorge for study, so nothing of its picture is used: every frame of each element is
measured (vfx_measure.liquid_mask: its pieces, their coarse outlines of a handful of points, holes, sizes and where
they sit), and each drawing is redrawn with our own shapes — a smooth custom path per piece, the turquoise fill, the
dark side as an inner tone, a white rim and a white shine of our own on each big piece — keyed on the same frames
(held in between, so the stepping is theirs), at the same size relation, direction and duration.

Output in E:\\FlipStudio\\tienda\\vfx-estudio\\liquido\\prototipos:
  <name>.mp4                  ours alone on black
  comparacion-<name>.mp4      «Referencia RTFX» | «Nuestro (Flip)», in sync, three times round
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

import vfx
import vfx_demo
from scene import Box, Template, fill, stroke
from vfx_measure import liquid_mask

VIDEO = Path.home() / "Videos" / "aTubeCatcher" / \
    "RTFX Generator Plugin for Cartoon or Anime effects in After Effects and Premiere.mkv"
PAGE = 241.4  # the liquid overview page starts here; frames below count from it at 30 fps
OUT = Path(r"E:\FlipStudio\tienda\vfx-estudio\liquido\prototipos")
BODY, DARK, RIM, SHINE = "#58aca8", "#22706e", "#8fd0cc", "#f0fbfb"
K = 3  # our canvas is the reference crop × K

# name: (crop w, h, x, y in the 1920×1080 video, first frame, last frame, Spanish name)
ELEMENTS = {
    "columna": ((146, 310, 677, 670), 106, 125, "Columna que se parte en gotas"),
    "goteo": ((196, 530, 1297, 150), 57, 108, "Goteo en T"),
    "salpicadura": ((446, 300, 837, 500), 54, 75, "Salpicadura doble"),
    "racimo": ((235, 160, 1297, 820), 144, 160, "Racimo que se separa"),
    "anillo": ((240, 340, 712, 150), 55, 68, "Anillo de arcos"),
    "gota": ((110, 200, 822, 290), 35, 52, "Gota que sube y se parte"),
}


def frames_of(crop, f0, f1):
    w, h, x, y = crop
    tmp = tempfile.mkdtemp(prefix="vfxliq_")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{PAGE + f0 / 30.0:.4f}",
                    "-t", f"{(f1 - f0 + 1) / 30.0:.4f}", "-i", str(VIDEO), "-vf", f"crop={w}:{h}:{x}:{y}",
                    os.path.join(tmp, "f%04d.png")], check=True)
    return [cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB) for f in sorted(glob.glob(os.path.join(tmp, "f*.png")))]


def pieces_of(rgb, min_area=5):
    """The drawing's pieces: [(outline points, hole outlines, area, (cx, cy), (ew, eh, angle))] in crop px."""
    mask = liquid_mask(rgb, 70)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, labels, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
    out = []
    for k in range(1, n):
        area = int(stats[k, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        bx, by, bw, bh = (int(stats[k, cv2.CC_STAT_LEFT]), int(stats[k, cv2.CC_STAT_TOP]),
                          int(stats[k, cv2.CC_STAT_WIDTH]), int(stats[k, cv2.CC_STAT_HEIGHT]))
        # A piece cut by the crop's edge belongs to a neighbouring cell of the overview grid, not to this element.
        if bx <= 0 or by <= 0 or bx + bw >= mask.shape[1] or by + bh >= mask.shape[0]:
            continue
        comp = (labels == k).astype(np.uint8)
        cs, hier = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        outer = [c for j, c in enumerate(cs) if hier[0][j][3] < 0]
        c = max(outer, key=cv2.contourArea)
        cx, cy = float(cents[k][0]), float(cents[k][1])
        if area < 40 or len(c) < 8:
            r = math.sqrt(area / math.pi)
            pts = [(cx + r * math.cos(2 * math.pi * i / 8), cy + r * math.sin(2 * math.pi * i / 8)) for i in range(8)]
            out.append((pts, [], area, (cx, cy), (2 * r, 2 * r, 0.0)))
            continue
        hull = cv2.contourArea(cv2.convexHull(c))
        solid = cv2.contourArea(c) / hull if hull > 0 else 1.0
        if area < 400 and len(c) >= 5 and solid > 0.88:
            # A round drop: our own ellipse where it sits, its size and its turn (a thin arc keeps its outline).
            (ex, ey), (ew, eh), ang = cv2.fitEllipse(c)
            a = math.radians(ang)
            pts = [(ex + ew / 2 * math.cos(t) * math.cos(a) - eh / 2 * math.sin(t) * math.sin(a),
                    ey + ew / 2 * math.cos(t) * math.sin(a) + eh / 2 * math.sin(t) * math.cos(a))
                   for t in (2 * math.pi * i / 12 for i in range(12))]
            out.append((pts, [], area, (cx, cy), (ew, eh, ang)))
            continue
        eps = max(0.6, 0.008 * cv2.arcLength(c, True))
        pts = [tuple(map(float, p)) for p in cv2.approxPolyDP(c, eps, True).reshape(-1, 2)]
        holes = []
        for j, hh in enumerate(hier[0]):
            if hh[3] >= 0 and cv2.contourArea(cs[j]) > 10:
                e2 = max(1.0, 0.05 * cv2.arcLength(cs[j], True))
                holes.append([tuple(map(float, p)) for p in cv2.approxPolyDP(cs[j], e2, True).reshape(-1, 2)])
        (ex, ey), (ew, eh), ang = cv2.fitEllipse(c)
        out.append((pts, holes, area, (cx, cy), (ew, eh, ang)))
    return out


def oriented(pts, hole):
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return list(reversed(pts)) if (a < 0) != hole else pts


def shine_of(piece):
    """Our highlight for a big piece: a white streak up and to the left of its middle, along its long side."""
    pts, holes, area, (cx, cy), (ew, eh, ang) = piece
    if area < 150:
        return None
    long_, short = max(ew, eh), min(ew, eh)
    a = math.radians(ang + (90 if eh > ew else 0))  # along the long axis
    sx, sy = cx - short * 0.2, cy - long_ * 0.22
    L, W = long_ * 0.1, short * 0.07
    return [(sx + L * math.cos(t) * math.cos(a) - W * math.sin(t) * math.sin(a),
             sy + L * math.cos(t) * math.sin(a) + W * math.sin(t) * math.cos(a))
            for t in (2 * math.pi * i / 12 for i in range(12))]


EMPTY = "M 0 0 L 0.01 0 L 0.01 0.01 Z"


def build(name):
    crop, f0, f1, es = ELEMENTS[name]
    w, h = crop[0], crop[1]
    W, H = (w * K) // 2 * 2, (h * K) // 2 * 2
    frames = frames_of(crop, f0, f1)
    dur = len(frames) / 30.0
    t = Template(f"vfx-liquido-{name}", es, name, "vfx", dur, size=(W, H), background="#000000")
    tr_body = t.track("video")
    tr_shine = t.track("video")
    box = (0.0, 0.0, float(w), float(h))
    bodies, shines, times = [], [], []
    last = None
    for i, rgb in enumerate(frames):
        ps = pieces_of(rgb)
        contours = []
        for pts, holes, *_ in ps:
            contours.append((oriented(pts, False), True, [], ))
            for hpts in holes:
                contours.append((oriented(hpts, True), True, []))
        svg = vfx.smooth_path(contours, box, corner_angle=160) if contours else EMPTY
        sh = [s for s in (shine_of(p) for p in ps) if s]
        ssvg = vfx.smooth_path([(s, True) for s in sh], box) if sh else EMPTY
        if svg == last:
            continue  # held: the same drawing as the frame before
        last = svg
        bodies.append(svg)
        shines.append(ssvg)
        times.append(i / 30.0)

    def keyed(track, svgs, layers):
        clip = t.solid(track, "#ffffff", 0.0, dur, box=Box(0, 0, W, H), kind="custom", layers=layers)
        st = clip["shapeStyle"]
        st["customPath"] = svgs[0]
        st["pathShapes"] = svgs
        st["keyframes"] = {"path": vfx.keys([(tm, j, "hold") for j, tm in enumerate(times)])}
        return clip

    rim = stroke(1.2 * K, RIM)
    rim["strokeAlign"] = "inside"
    keyed(tr_body, bodies, [fill(BODY), rim, vfx.inner_tone(DARK, dx=-5.0 * K, dy=-6.0 * K),
                            vfx.inner_tone(SHINE, dx=0.8 * K, dy=1.0 * K, lid="shine")])
    keyed(tr_shine, shines, [fill(SHINE), {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0,
                                           "paint": {"kind": "solid", "color": "#00000000"}}])
    return t, dur, len(times)


FONT = "C\\:/Windows/Fonts/arialbd.ttf"


def comparison(name, ours: Path, out: Path):
    crop, f0, f1, _ = ELEMENTS[name]
    w, h, x, y = crop
    n = f1 - f0 + 1
    target = out / f"comparacion-{name}.mp4"
    H = 900
    lab = lambda s: (f"drawtext=fontfile='{FONT}':text='{s}':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=12:"
                     "box=1:boxcolor=black@0.7:boxborderw=8")
    flt = (f"[0:v]crop={w}:{h}:{x}:{y},scale=-2:{H},setsar=1,fps=30,trim=end_frame={n},setpts=PTS-STARTPTS,"
           f"loop=2:{n}:0,pad=iw:ih+60:0:60:black,{lab('Referencia RTFX')}[l];"
           f"[1:v]scale=-2:{H},setsar=1,fps=30,trim=end_frame={n},setpts=PTS-STARTPTS,loop=2:{n}:0,"
           f"pad=iw:ih+60:0:60:black,{lab('Nuestro (Flip)')}[r];[l][r]hstack=inputs=2[v]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{PAGE + f0 / 30.0:.4f}", "-t", f"{n / 30.0:.4f}",
                    "-i", str(VIDEO), "-i", str(ours), "-filter_complex", flt, "-map", "[v]", "-an",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(target)], check=True)
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    out = Path(args.out)
    work = out / "_proyectos"
    work.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name in ELEMENTS:
        if args.only and name not in args.only.split(","):
            continue
        t, dur, keys = build(name)
        print(f"{name}: {dur:.2f} s, {keys} drawings", flush=True)
        jobs.append((name, vfx_demo.write_doc(t, work, name), dur))
    vfx_demo.render(jobs, args.exe, out, capture_at=0.3)
    for name, _, _ in jobs:
        if (out / f"{name}.mp4").exists():
            print("comparison", comparison(name, out / f"{name}.mp4", out), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
