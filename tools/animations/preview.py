"""Quick local preview of the stickers, without the app (QPainter, shapes only).

    py tools/animations/preview.py --sheet out.png [--only id,id] [--module designs3] [--strip 6]

Draws a contact sheet: one row per sticker with `--strip` frames across the loop (or one card
per sticker at its `thumb` time without --strip). It understands the subset of Lottie our
writer (lottie.py) produces: el/rc/sr/sh, fill, stroke, trim, nested groups, layer ip/op and
eased keyframes. It is a design aid, not the reference: the cards that ship come from the app
(build.py), which renders with Skottie.
"""

from __future__ import annotations

import argparse
import importlib
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (QBrush, QColor, QFont, QGuiApplication, QImage, QPainter, QPainterPath,  # noqa: E402
                           QPen, QTransform)

KAPPA = 0.5522847498


def bezier_y(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """y of a CSS-style cubic easing at x (binary search on t)."""
    lo, hi = 0.0, 1.0
    for _ in range(30):
        t = (lo + hi) / 2
        bx = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3
        if bx < x:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3


def lerp(a, b, u):
    if isinstance(a, dict):
        return {"c": a["c"], "v": [lerp(p, q, u) for p, q in zip(a["v"], b["v"])],
                "i": [lerp(p, q, u) for p, q in zip(a["i"], b["i"])], "o": [lerp(p, q, u) for p, q in zip(a["o"], b["o"])]}
    if isinstance(a, list):
        return [lerp(p, q, u) for p, q in zip(a, b)]
    return a + (b - a) * u


def value(prop, t: float):
    if prop is None:
        return None
    if not prop.get("a"):
        return prop["k"]
    keys = prop["k"]

    def unwrap(v):
        if isinstance(v, list) and len(v) == 1:
            return v[0]
        return v
    if t <= keys[0]["t"]:
        return unwrap(keys[0]["s"])
    for k0, k1 in zip(keys, keys[1:]):
        if t < k1["t"]:
            if k0.get("h"):
                return unwrap(k0["s"])
            span = k1["t"] - k0["t"]
            x = (t - k0["t"]) / span if span else 1
            o, i = k0.get("o", {"x": [0], "y": [0]}), k0.get("i", {"x": [1], "y": [1]})
            u = bezier_y(x, o["x"][0], o["y"][0], i["x"][0], i["y"][0])
            return unwrap(lerp(k0["s"], k1["s"], u))
    return unwrap(keys[-1]["s"])


def matrix(tr: dict, t: float) -> QTransform:
    p = value(tr.get("p"), t) or [0, 0]
    a = value(tr.get("a"), t) or [0, 0]
    s = value(tr.get("s"), t) or [100, 100]
    r = value(tr.get("r"), t) or 0
    m = QTransform()
    m.translate(p[0], p[1])
    m.rotate(r)
    m.scale(s[0] / 100, s[1] / 100)
    m.translate(-a[0], -a[1])
    return m


def ellipse_path(c, size) -> QPainterPath:
    cx, cy = c
    rx, ry = size[0] / 2, size[1] / 2
    kx, ky = rx * KAPPA, ry * KAPPA
    path = QPainterPath(QPointF(cx, cy - ry))
    path.cubicTo(cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy)
    path.cubicTo(cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry)
    path.cubicTo(cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy)
    path.cubicTo(cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry)
    path.closeSubpath()
    return path


def star_path(item, t) -> QPainterPath:
    n = int(value(item["pt"], t))
    outer, inner = value(item["or"], t), value(item.get("ir"), t) if item.get("sy", 1) == 1 else None
    cx, cy = value(item["p"], t)
    rot = value(item.get("r"), t) or 0
    pts = []
    steps = n * 2 if inner is not None else n
    for k in range(steps):
        rad = outer if inner is None or k % 2 == 0 else inner
        a = math.radians(rot - 90 + k * 360 / steps)
        pts.append(QPointF(cx + rad * math.cos(a), cy + rad * math.sin(a)))
    path = QPainterPath(pts[0])
    for q in pts[1:]:
        path.lineTo(q)
    path.closeSubpath()
    return path


def bezier_path(shape) -> QPainterPath:
    v, i, o = shape["v"], shape["i"], shape["o"]
    path = QPainterPath(QPointF(*v[0]))
    n = len(v)
    segs = n if shape.get("c") else n - 1
    for k in range(segs):
        a, b = v[k], v[(k + 1) % n]
        path.cubicTo(a[0] + o[k][0], a[1] + o[k][1], b[0] + i[(k + 1) % n][0], b[1] + i[(k + 1) % n][1], b[0], b[1])
    if shape.get("c"):
        path.closeSubpath()
    return path


def geometry(item, t) -> QPainterPath | None:
    ty = item["ty"]
    if ty == "el":
        return ellipse_path(value(item["p"], t), value(item["s"], t))
    if ty == "rc":
        cx, cy = value(item["p"], t)
        w, h = value(item["s"], t)
        r = min(value(item["r"], t) or 0, w / 2, h / 2)
        path = QPainterPath()
        path.addRoundedRect(QRectF(cx - w / 2, cy - h / 2, w, h), r, r)
        return path
    if ty == "sr":
        return star_path(item, t)
    if ty == "sh":
        return bezier_path(value(item["ks"], t))
    return None


def trimmed(path: QPainterPath, s: float, e: float, off: float) -> QPainterPath:
    """Keeps the stretch [s, e] (percent) of the path's length, shifted by off (degrees)."""
    if s <= 0 and e >= 100:
        return path
    lo, hi = sorted((s / 100, e / 100))
    shift = off / 360
    lo, hi = lo + shift, hi + shift
    if hi - lo <= 1e-4:
        return QPainterPath()
    out = QPainterPath()
    steps = 160
    for k in range(steps + 1):
        u = (lo + (hi - lo) * k / steps) % 1.0 if path.length() else 0
        if hi - lo >= 1 and k == steps:
            u = lo % 1.0
        pt = path.pointAtPercent(min(max(u, 0), 1))
        if k == 0:
            out.moveTo(pt)
        else:
            out.lineTo(pt)
    return out


def colour(c, o) -> QColor:
    col = QColor.fromRgbF(c[0], c[1], c[2], 1)
    col.setAlphaF(max(0, min(1, o)))
    return col


def render_items(items, t, xf: QTransform, opacity: float):
    """Returns draw ops (top first): (kind, paint, [(path, xf)], opacity)."""
    tr = next((it for it in items if it["ty"] == "tr"), None)
    if tr:
        xf = matrix(tr, t) * xf
        opacity *= (value(tr.get("o"), t) if tr.get("o") else 100) / 100
    # Entries are [path, transform] lists shared with the paint ops, so a trim modifier changes what
    # every paint of the group draws (as Skottie does with our [path, stroke, trim] groups).
    geoms: list[list] = []
    ops = []
    for it in items:
        ty = it["ty"]
        if ty in ("el", "rc", "sr", "sh"):
            g = geometry(it, t)
            if g is not None:
                geoms.append([g, xf])
        elif ty == "gr":
            sub_ops, sub_geoms = render_group(it, t, xf, opacity)
            ops.extend(sub_ops)
            geoms.extend(sub_geoms)
        elif ty == "tm":
            s, e, o = value(it["s"], t), value(it["e"], t), value(it["o"], t)
            for entry in geoms:
                entry[0] = trimmed(entry[0], s, e, o)
        elif ty in ("fl", "st"):
            ops.append((ty, it, list(geoms), opacity))
    return ops, geoms


def render_group(group, t, xf, opacity):
    return render_items(group["it"], t, xf, opacity)


def draw(painter: QPainter, doc: dict, t: float, scale: float, slots: dict | None = None,
         post: QTransform | None = None):
    slots = slots or {}
    post = post or QTransform()
    for layer in reversed(doc["layers"]):
        if not (layer.get("ip", 0) <= t < layer.get("op", doc["op"])):
            continue
        ks = layer["ks"]
        xf = matrix(ks, t) * QTransform.fromScale(scale, scale)
        opacity = (value(ks.get("o"), t) if ks.get("o") else 100) / 100
        ops, _ = render_items(layer["shapes"] + [{"ty": "tr", "p": {"a": 0, "k": [0, 0]}}], t, xf, opacity)
        for kind, paint, geoms, op in reversed(ops):
            c = paint["c"]
            col = slots.get(c.get("sid")) or value(c, t)
            alpha = op * value(paint["o"], t) / 100
            for path, m in geoms:
                painter.setTransform(m * post)
                if kind == "fl":
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(colour(col, alpha)))
                    p = QPainterPath(path)
                    p.setFillRule(Qt.WindingFill)
                    painter.drawPath(p)
                else:
                    pen = QPen(colour(col, alpha), value(paint["w"], t))
                    pen.setCapStyle({1: Qt.FlatCap, 2: Qt.RoundCap, 3: Qt.SquareCap}.get(paint.get("lc", 2), Qt.RoundCap))
                    pen.setJoinStyle({1: Qt.MiterJoin, 2: Qt.RoundJoin, 3: Qt.BevelJoin}.get(paint.get("lj", 2), Qt.RoundJoin))
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path)
    painter.resetTransform()


def frame_image(doc: dict, t: float, box: int) -> QImage:
    w, h = doc["w"], doc["h"]
    scale = box / max(w, h)
    img = QImage(box, box, QImage.Format_ARGB32)
    img.fill(QColor("#1d1f27"))
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    ox, oy = (box - w * scale) / 2, (box - h * scale) / 2
    p.setClipRect(QRectF(ox, oy, w * scale, h * scale))
    draw(p, doc, t, scale, post=QTransform.fromTranslate(ox, oy))
    p.end()
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", type=Path, required=True)
    ap.add_argument("--module", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--strip", type=int, default=0)
    ap.add_argument("--box", type=int, default=160)
    ap.add_argument("--cols", type=int, default=8)
    args = ap.parse_args()
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))
    _app = QGuiApplication.instance() or QGuiApplication(["preview", "-platform", "offscreen"])
    makers = []
    mods = [m for m in args.module.split(",") if m] or ["designs"]
    for name in mods:
        mod = importlib.import_module(name)
        makers += mod.STICKERS
    only = {s for s in args.only.split(",") if s}
    stickers = [m() for m in makers]
    stickers = [s for s in stickers if not only or s.id in only]
    box, label = args.box, 18
    if args.strip:
        cols, rows = args.strip, len(stickers)
    else:
        cols = min(args.cols, len(stickers))
        rows = math.ceil(len(stickers) / cols)
    sheet = QImage(cols * box, rows * (box + label), QImage.Format_RGB32)
    sheet.fill(QColor("#0d0e12"))
    p = QPainter(sheet)
    p.setFont(QFont("Segoe UI", 8))
    for idx, st in enumerate(stickers):
        doc = st.document()
        frames = [st.frames * (k + 0.5) / args.strip for k in range(args.strip)] if args.strip else [st.frames * st.thumb]
        for k, t in enumerate(frames):
            c, r = (k, idx) if args.strip else (idx % cols, idx // cols)
            img = frame_image(doc, t, box)
            p.drawImage(c * box, r * (box + label), img)
            p.setPen(QColor("#d0d0d0"))
            p.drawText(QRectF(c * box + 3, r * (box + label) + box, box - 6, label), Qt.AlignLeft | Qt.AlignVCenter,
                       f"{st.id} @{t:.0f}" if args.strip else st.id)
    p.end()
    args.sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(args.sheet))
    print(f"{len(stickers)} stickers -> {args.sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
