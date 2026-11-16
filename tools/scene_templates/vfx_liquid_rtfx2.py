"""Second round of the six RTFX liquid elements (Jorge, 2026-11-16: «se parece bastante, pero si lo puedes mejorar
mucho mejor»). Same idea as vfx_liquid_rtfx.py — every frame measured, every drawing redrawn with our own shapes on
the same frames — plus:

- the inside of each drawing: its dark pockets and its white shines are measured as their own regions (by colour
  inside the piece) and drawn as their own contours, in a clipping group (0.32: the parts above the bottom one show
  only inside it), so each pocket and each shine has its own outline and keys;
- finer outlines (a point every ~0.5 % of the way round, sharp kinks kept), the light rim, and the faint remnants at
  the end (a lower threshold for the last specks);
- racimo: the overview page scrolls down ~870 px in the middle of that element (frames 135–151), so the crop follows
  the page (the scroll measured by phase correlation) and ours stays put instead of copying the reflow.

    py tools/scene_templates/vfx_liquid_rtfx2.py --exe <portable flipstudio.exe> [--only goteo]

Output in E:\\FlipStudio\\tienda\\vfx-estudio\\liquido\\prototipos: <name>-v2.mp4, comparacion-<name>-v2.mp4 and
hoja-<name>-v2.png (reference and ours, frame by frame).
"""

from __future__ import annotations

import argparse
import glob
import math
import os
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

import vfx
import vfx_demo
from scene import Box, Template
from vfx_liquid_rtfx import ELEMENTS as V1, OUT, PAGE, VIDEO

K = 3
BODY, DARK, SHINE, RIM = "#5ebab1", "#216b66", "#ecfbfb", "#a6dcd6"
EMPTY = "M 0 0 L 0.01 0 L 0.01 0.01 Z"
# racimo follows the page: (w, h, x, y at the anchor frame), anchor frame, first, last
ELEMENTS = {name: (crop, f0, f1, es, None) for name, (crop, f0, f1, es) in V1.items()}
ELEMENTS["salpicadura"] = ((446, 340, 837, 460), 54, 75, "Salpicadura doble", None)
ELEMENTS["racimo"] = ((290, 210, 1255, 785), 142, 155, "Racimo que se separa", 152)


def page_frames(f0, f1):
    tmp = tempfile.mkdtemp(prefix="vfxliq2_")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{PAGE + f0 / 30.0:.4f}",
                    "-t", f"{(f1 - f0 + 1) / 30.0:.4f}", "-i", str(VIDEO), os.path.join(tmp, "f%04d.png")], check=True)
    return [cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB) for f in sorted(glob.glob(os.path.join(tmp, "f*.png")))]


def crops(name):
    """The reference crop of every frame; for a tracked element the crop rides the page's scroll."""
    (w, h, x, y), f0, f1, _, anchor = ELEMENTS[name]
    frames = page_frames(f0, f1)
    if anchor is None:
        return [f[y:y + h, x:x + w].copy() for f in frames]
    grey = [cv2.cvtColor(f[150:980, 362:1852], cv2.COLOR_RGB2GRAY).astype(np.float32) for f in frames]
    acc = [0.0]
    for a, b in zip(grey, grey[1:]):
        (_, dy), _ = cv2.phaseCorrelate(a, b)
        acc.append(acc[-1] + dy)
    ref = acc[anchor - f0]
    out = []
    for f, s in zip(frames, acc):
        yy = int(round(y - (ref - s)))
        tile = np.zeros((h, w, 3), np.uint8)
        top, bottom = max(0, yy), min(f.shape[0], yy + h)
        if bottom > top:
            tile[top - yy:bottom - yy] = f[top:bottom, x:x + w]
        out.append(tile)
    return out


def masks(rgb):
    """Liquid (with the faint specks), dark, shine and body masks of a reference frame."""
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    teal = (g > 58) & (b > 50) & (g - r > 14)
    # White counts only next to turquoise (a shine on a drop), not the embers and stars of the cells around.
    near = cv2.dilate(teal.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    liquid = teal | ((r > 165) & (g > 165) & (b > 165) & near)
    liquid = cv2.morphologyEx(liquid.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    dark = liquid & (g < 126) & (g - r > 30)
    shine = liquid & (r > 175) & (g > 205) & (b > 205)
    return liquid, dark, shine


def outlines(mask, min_area, eps_frac, round_small=True):
    """Each region of the mask → (points, holes). Coarse but fine enough: a point every eps_frac of its perimeter."""
    m = mask.astype(np.uint8)
    n, labels, stats, cents = cv2.connectedComponentsWithStats(m, 8)
    out = []
    H, W = m.shape
    for k in range(1, n):
        area = int(stats[k, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        x, y, w, h = (int(stats[k, i]) for i in (cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP, cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT))
        if x <= 0 or y <= 0 or x + w >= W or y + h >= H:
            continue  # cut by the crop: a neighbouring cell's
        comp = (labels == k).astype(np.uint8)
        cs, hier = cv2.findContours(comp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        outer = [c for j, c in enumerate(cs) if hier[0][j][3] < 0]
        c = max(outer, key=cv2.contourArea)
        if round_small and (area < 30 or len(c) < 8):
            cx, cy = cents[k]
            r = max(0.7, math.sqrt(area / math.pi))
            pts = [(cx + r * math.cos(2 * math.pi * i / 8), cy + r * math.sin(2 * math.pi * i / 8)) for i in range(8)]
            out.append((pts, []))
            continue
        eps = max(0.5, eps_frac * cv2.arcLength(c, True))
        pts = [tuple(map(float, p)) for p in cv2.approxPolyDP(c, eps, True).reshape(-1, 2)]
        if len(pts) < 3:
            continue
        holes = []
        for j, hh in enumerate(hier[0]):
            if hh[3] >= 0 and cv2.contourArea(cs[j]) > 6:
                e2 = max(0.5, 0.02 * cv2.arcLength(cs[j], True))
                hp = [tuple(map(float, p)) for p in cv2.approxPolyDP(cs[j], e2, True).reshape(-1, 2)]
                if len(hp) >= 3:
                    holes.append(hp)
        out.append((pts, holes))
    return out


def oriented(pts, hole):
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return list(reversed(pts)) if (a < 0) != hole else pts


def svg_of(regions, box):
    contours = []
    for pts, holes in regions:
        contours.append((oriented(pts, False), True, []))
        contours.extend((oriented(hp, True), True, []) for hp in holes)
    return vfx.smooth_path(contours, box, corner_angle=80) if contours else EMPTY


def part(pid, name, w, h, colour, svgs, times, rim=None):
    layers = [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
               "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#")}}]
    if rim:
        layers.append({"id": "stroke", "kind": "stroke", "enabled": True, "width": rim[0], "strokeAlign": "inside",
                       "cap": "round", "join": "round", "opacity": 1.0,
                       "paint": {"kind": "solid", "color": "#ff" + rim[1].lstrip("#")}})
    return {"id": pid, "name": name, "width": w, "height": h,
            "shape": {"kind": "custom", "customPath": svgs[0], "customEvenOdd": False, "layers": layers,
                      "pathShapes": svgs,
                      "keyframes": {"path": vfx.keys([(tm, j, "hold") for j, tm in enumerate(times)])}}}


def build(name):
    (w, h, _, _), f0, f1, es, _ = ELEMENTS[name]
    refs = crops(name)
    W, H = (w * K) // 2 * 2, (h * K) // 2 * 2
    dur = len(refs) / 30.0
    box = (0.0, 0.0, float(w), float(h))
    bodies, darks, shines, times = [], [], [], []
    last = None
    for i, rgb in enumerate(refs):
        liquid, dark, shine = masks(rgb)
        body = outlines(liquid, 3, 0.005)
        keep = np.zeros(liquid.shape, np.uint8)
        for pts, _ in body:  # pockets and shines only inside the pieces we keep
            cv2.fillPoly(keep, [np.array(pts, np.int32)], 1)
        keep = keep.astype(bool)
        b, d, s = svg_of(body, box), svg_of(outlines(dark & keep, 6, 0.02, False), box), \
            svg_of(outlines(shine & keep, 3, 0.03), box)
        if (b, d, s) == last:
            continue
        last = (b, d, s)
        bodies.append(b)
        darks.append(d)
        shines.append(s)
        times.append(i / 30.0)
    t = Template(f"vfx-liquido-{name}-v2", es, name, "vfx", dur, size=(W, H), background="#000000")
    tr = t.track("video")
    clip = t.solid(tr, "#ffffff", 0.0, dur, box=Box(0, 0, W, H), kind="rectangle")
    st = clip["shapeStyle"]
    st["layers"] = []
    st["partsRef"] = [W, H]
    st["parts"] = [{"id": "g1", "name": "Gota", "group": True, "clip": True, "children": [
        part("p1", "Brillo", W, H, SHINE, shines, times),
        part("p2", "Lado oscuro", W, H, DARK, darks, times),
        part("p3", "Cuerpo", W, H, BODY, bodies, times, rim=(1.0 * K, RIM)),
    ]}]
    return t, dur, len(times), refs


FONT = "C\\:/Windows/Fonts/arialbd.ttf"


def comparison(name, refs, ours: Path, out: Path):
    tmp = tempfile.mkdtemp(prefix="vfxref_")
    for i, f in enumerate(refs):
        cv2.imwrite(os.path.join(tmp, f"r{i:04d}.png"), cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
    n = len(refs)
    HH = 900
    lab = lambda s: (f"drawtext=fontfile='{FONT}':text='{s}':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=12:"
                     "box=1:boxcolor=black@0.7:boxborderw=8")
    flt = (f"[0:v]scale=-2:{HH}:flags=lanczos,setsar=1,loop=2:{n}:0,pad=iw:ih+60:0:60:black,{lab('Referencia RTFX')}[l];"
           f"[1:v]scale=-2:{HH},setsar=1,fps=30,trim=end_frame={n},setpts=PTS-STARTPTS,loop=2:{n}:0,"
           f"pad=iw:ih+60:0:60:black,{lab('Nuestro (Flip)')}[r];[l][r]hstack=inputs=2[v]")
    target = out / f"comparacion-{name}-v2.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(tmp, "r%04d.png"),
                    "-i", str(ours), "-filter_complex", flt, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", str(target)], check=True)
    sheet = out / f"hoja-{name}-v2.png"
    step = max(1, n // 8)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(target), "-vf",
                    f"select=not(mod(n\\,{step}))*lt(n\\,{n}),scale=-2:330,tile=4x2", "-frames:v", "1", str(sheet)],
                   check=True)
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
    jobs, refs_of = [], {}
    for name in ELEMENTS:
        if args.only and name not in args.only.split(","):
            continue
        t, dur, nkeys, refs = build(name)
        refs_of[name] = refs
        print(f"{name}: {dur:.2f} s, {nkeys} drawings", flush=True)
        jobs.append((f"{name}-v2", vfx_demo.write_doc(t, work, f"{name}-v2"), dur))
    vfx_demo.render(jobs, args.exe, out, capture_at=0.3)
    for name, refs in refs_of.items():
        if (out / f"{name}-v2.mp4").exists():
            print("comparison", comparison(name, refs, out / f"{name}-v2.mp4", out), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
