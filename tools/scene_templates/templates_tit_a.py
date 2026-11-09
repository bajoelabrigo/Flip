"""Social titles, first TITLE set (2026-11-08): the nine of 57033946.mp4 (1920×1080 at 29.97 fps), big white
titles in a heavy wide type with hand-drawn pink strokes and green, purple and orange doodles, over the user's video
(no background). Laid out where the reference has them (the middle of the frame). Kit de YouTube › Títulos con
estilo; ids `tit1-*`, order 8800-. Study notes in tienda/plantillas/estudio-57033946/NOTAS.md.

The moves, measured frame by frame:
- the whole title zooms in from about half its size, overshoots to ~112 % and settles back with a small bounce
  (S below); each word does it on its own clock, the second line a few frames after the first, and fades up from
  dark while it grows (O);
- the pink strokes draw themselves from their outer ends (trim, DRAW), growing with the title;
- the doodles pop in one by one;
- it leaves with its entrance played backwards (the reference does exactly that).
The strokes and doodles keep the exact shapes of the reference: their centre lines were traced from a still with
title_trace.py and are kept in title_data/<title>.json.

Not like the reference: the type. Its letters (a wide black grotesque with spurs on I and T) are not in our fonts;
Archivo Black is the closest, a little narrower, so each word is set to the reference's width.
"""

from __future__ import annotations

import json
from pathlib import Path

import templates_llt_f as f6
from kit import Box, outline, wide
from llt_motion import frames_of
from scene import keys, layout, shape_style
from templates_llt_f import table

FPS = 30000 / 1001
WHITE = "#FFFFFF"
DATA = Path(__file__).resolve().parent / "title_data"
FONT, WEIGHT = "Archivo", 900

# Measured on CREATIVE TITLES (frames from the first one that shows anything).
S = table({2: 0.46, 3: 0.67, 4: 0.85, 5: 0.99, 6: 1.06, 7: 1.09, 8: 1.115, 9: 1.11, 10: 1.086, 11: 1.053, 12: 1.025,
           13: 1.0, 14: 0.986, 15: 0.977, 16: 0.976, 17: 0.979, 18: 0.985, 19: 0.989, 20: 0.994, 22: 0.998, 24: 1.0})
O = table({1: 0.0, 2: 0.15, 3: 0.22, 4: 0.29, 5: 0.40, 6: 0.51, 7: 0.60, 8: 0.67, 9: 0.73, 10: 0.79, 11: 0.83,
           12: 0.86, 13: 0.9, 14: 0.92, 16: 0.95, 18: 0.98, 22: 1.0})
DRAW = table({3: 0.0, 4: 0.02, 5: 0.06, 6: 0.19, 7: 0.37, 8: 0.55, 9: 0.66, 10: 0.75, 12: 0.82, 14: 0.85, 16: 0.89,
              18: 0.95, 20: 0.98, 24: 1.0})
POP = table({0: 0.0, 2: 0.55, 4: 1.15, 6: 0.97, 8: 1.0})


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"tit1-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:titulos-estilo", "título", "redes"] + tags, **kw)


class Title:
    """One title: u (seconds) → frame of the entrance; it leaves with the entrance backwards."""

    def __init__(self, t, dur, pivot, group=None):
        self.t, self.dur, self.pivot = t, dur, pivot
        self.group = group or S  # how the doodles grow with the title
        self.own_pivot = None

    def frame(self, u):
        return 1 + min(u, self.dur - u) * FPS

    def place(self, clip, scale, own=None, size=None, shift=None, pivot=None, own_pivot=None):
        """Rewrites a still clip's box every frame: scaled by scale(frame) about the title's pivot (or `pivot`),
        by own(frame) about its own centre (or `own_pivot`), and moved by shift(frame) = (dx, dy); a text's type
        size too."""
        x, y = clip["x"]["keyframes"][0]["value"], clip["y"]["keyframes"][0]["value"]
        w, h = clip["width"]["keyframes"][0]["value"], clip["height"]["keyframes"][0]["value"]
        cx, cy = x + w / 2, y + h / 2
        px, py = pivot or self.pivot
        xs, ys, ws, hs, sizes = [], [], [], [], []
        for u in frames_of(self.dur):
            fr = self.frame(u)
            k = scale(fr)
            o = own(fr) if own else 1.0
            ncx, ncy = px + (cx - px) * k, py + (cy - py) * k
            if own_pivot:
                ox, oy = px + (own_pivot[0] - px) * k, py + (own_pivot[1] - py) * k
                ncx, ncy = ox + (ncx - ox) * o, oy + (ncy - oy) * o
            dx, dy = shift(fr) if shift else (0.0, 0.0)
            kk = max(1e-3, k * o)
            xs.append((u, ncx + dx - w * kk / 2, "linear"))
            ys.append((u, ncy + dy - h * kk / 2, "linear"))
            ws.append((u, w * kk, "linear"))
            hs.append((u, h * kk, "linear"))
            sizes.append((u, (size or 0) * kk, "linear"))
        clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
        if size:
            clip.setdefault("textStyle", {})["keyframes"] = {"pixelSize": keys(sizes)}

    def turn(self, clip, rot):
        """Rotation in degrees, rot(frame)."""
        clip["rotation"] = keys([(u, round(rot(self.frame(u)), 3), "linear") for u in frames_of(self.dur)])

    def opacity(self, clip, op):
        clip["opacity"] = keys([(u, round(op(self.frame(u)), 4), "linear") for u in frames_of(self.dur)])

    def word(self, text, ink, delay=0, name="Título", colour=WHITE, scale=None, own=None, fade=O, shift=None,
             rot=None, weight=WEIGHT, case="upper", blur=False):
        """A word whose ink spans ink = (x0, y0 caps top, x1, y1 baseline) at rest. By default it zooms with the
        title (S about the pivot) and fades in (O), `delay` frames late; scale/own/shift/rot/fade replace those
        (own: about its own centre)."""
        x0, y0, x1, y1 = ink
        p = f6.Piece(self.t, self.dur, 0)
        p.frame = lambda u: 0  # laid out still; place() moves it
        # Our type is narrower than the reference's: set to its width but never taller than its capitals.
        f = f6._font(FONT, weight)
        shown = text.upper() if case == "upper" else text
        bb, cap = f.getbbox(shown), f.getbbox("H")
        ratio = (bb[2] - bb[0]) / (cap[3] - cap[1])
        width = min(x1 - x0, (y1 - y0) * ratio)
        clip = p.text(text, (x0 + x1) / 2, y0, y1, width, FONT, weight, colour, name, align="center", case=case)
        size = clip["textStyle"]["pixelSize"]
        late = lambda f: (lambda fr: f(fr - delay)) if f else None  # noqa: E731
        if scale is None and own is None:
            scale = S
        self.place(clip, late(scale) or (lambda fr: 1.0), own=late(own), size=size, shift=late(shift))
        if fade:
            self.opacity(clip, late(fade))
        if rot:
            self.turn(clip, late(rot))
        if blur:
            clip["motionBlur"] = True
        return clip

    def _path_clip(self, name, pts_list, width, colour, closed=False):
        xs = [p[0] for pts in pts_list for p in pts]
        ys = [p[1] for pts in pts_list for p in pts]
        pad = width
        bx0, by0, bx1, by1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
        bw, bh = bx1 - bx0, by1 - by0
        P = lambda x, y: f"{(x - bx0) / bw * 100:.3f} {(y - by0) / bh * 100:.3f}"  # noqa: E731
        path = " ".join("M " + " L ".join(P(*p) for p in pts) + (" Z" if closed else "") for pts in pts_list)
        s = {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "opacity": 1.0,
             "strokeAlign": "center", "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}
        hollow = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}
        style = shape_style("custom", [hollow, s], customPath=path, customEvenOdd=False)
        clip = self.t._clip("shape", 0.0, self.dur, shapeStyle=style, **layout(Box(bx0, by0, bw, bh), None))
        clip["name"] = name
        self.t.track("shape", name).clips.append(clip)
        return clip

    def stroke(self, name, pts, width, colour, draw=DRAW, delay=0):
        """A hand-drawn stroke along pts that draws itself from its first point."""
        clip = self._path_clip(name, [pts], width, colour)
        clip["shapeStyle"]["keyframes"] = {
            "trimStart": keys([(0.0, 0.0, "hold")]),
            "trimEnd": keys([(u, round(100 * draw(self.frame(u) - delay), 3), "linear") for u in frames_of(self.dur)])}
        self.place(clip, S)
        return clip

    def doodle(self, name, segments, width, colour, at, closed=False):
        """A doodle (one or more polylines) that pops in at frame `at`."""
        clip = self._path_clip(name, segments, width, colour, closed)
        self.place(clip, S, own=lambda fr: POP(fr - at))
        return clip

    def blob(self, name, polys, colour, at, pop=None):
        """A doodle kept as its filled outline (polygons; holes by even-odd) that pops in at frame `at`."""
        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        bx0, by0, bw, bh = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        P = lambda x, y: f"{(x - bx0) / bw * 100:.3f} {(y - by0) / bh * 100:.3f}"  # noqa: E731
        path = " ".join("M " + " L ".join(P(*p) for p in poly) + " Z" for poly in polys)
        fill_ = {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                 "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}
        off = {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0, "strokeAlign": "inside",
               "paint": {"kind": "solid", "color": "#ffffffff"}}
        style = shape_style("custom", [fill_, off], customPath=path, customEvenOdd=True)
        clip = self.t._clip("shape", 0.0, self.dur, shapeStyle=style, **layout(Box(bx0, by0, bw, bh), None))
        clip["name"] = name
        self.t.track("shape", name).clips.append(clip)
        self.place(clip, self.group, own=pop or (lambda fr: POP(fr - at)), own_pivot=self.own_pivot)
        return clip

    def ring(self, name, c, r, width, colour, at):
        rr = r + width / 2
        clip = outline(self.t, self.t.track("shape", name), colour, width, 0.0, self.dur,
                       Box(c[0] - rr, c[1] - rr, 2 * rr, 2 * rr), kind="ellipse")
        clip["name"] = name
        self.place(clip, S, own=lambda fr: POP(fr - at))
        return clip


_CIRCLE = [(__import__("math").cos(a / 24 * 6.2832), __import__("math").sin(a / 24 * 6.2832)) for a in range(24)]


def _data(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def creative():
    d = _data("creative")
    D = 3.2
    t = _kit("creative", "Título: Creative titles con garabatos", "Title: Creative titles with doodles", D, 8800,
             ["garabatos", "rosa"], thumb_at=1.6)
    T = Title(t, D, (955, 510))
    for i, s in enumerate(d["strokes"]):
        T.stroke("Trazo" if i == 0 else f"Trazo {i + 1}", s["points"], s["width"], d["pink"])
    # The loop on the top stroke closes into a round blob as the stroke passes it.
    pts = d["strokes"][0]["points"]
    near = min(range(len(pts)), key=lambda i: (pts[i][0] - 880) ** 2 + (pts[i][1] - 252) ** 2)
    k = near / (len(pts) - 1)
    first = next(f / 4 for f in range(0, 200) if DRAW(f / 4) >= k)
    T.blob("Trazo (lazo)", [[[880 + 25 * c, 252 + 23 * s] for c, s in _CIRCLE]], d["pink"], 0,
           pop=lambda fr: 1.0 if fr >= first else 0.0)
    # Doodles in the order they pop (frames measured on the reference), each its own filled outline.
    when = {(1296, 140): 4, (1465, 212): 5, (672, 768): 7, (402, 720): 8, (1372, 240): 10, (530, 785): 11,
            (570, 882): 12, (1468, 198): 14}
    names = {"#62FC01": "Zigzag", "#9C59F6": "Aro", "#FCB52B": "Triángulo"}
    count = {}
    for dd in d["doodles"]:
        n = names[dd["colour"]]
        count[n] = count.get(n, 0) + 1
        T.blob(f"{n} {count[n]}", dd["polys"], dd["colour"], when[tuple(dd["box"][:2])])
    w1, w2 = d["words"]
    T.word(w1["text"], w1["ink"], 0, "Título")
    T.word(w2["text"], w2["ink"], 5, "Título 2")
    return t


f6._FILES[("Archivo", 800)] = "fonts.extra/fonts/archivo/Archivo-ExtraBold.ttf"
NAMES = {"pink": "Trazo", "pinkdark": "Trazo (sombra)", "green": "Zigzag", "purple": "Aro", "orange": "Triángulo",
         "yellow": "Adorno"}


def groups(doodles, pad=8):
    """Doodle blobs of one colour whose boxes touch go together (a smiley's face, eyes and mouth)."""
    out = []
    for d in doodles:
        x, y, w, h = d["box"]
        for g in out:
            if g["name"] != d["name"]:
                continue
            gx0, gy0, gx1, gy1 = g["bbox"]
            if x - pad < gx1 and gx0 < x + w + pad and y - pad < gy1 and gy0 < y + h + pad:
                g["polys"] += d["polys"]
                g["bbox"] = [min(gx0, x), min(gy0, y), max(gx1, x + w), max(gy1, y + h)]
                break
        else:
            out.append({"name": d["name"], "colour": d["colour"], "polys": list(d["polys"]),
                        "bbox": [x, y, x + w, y + h]})
    return out


def pop_doodles(T, gs, first, last, order=None):
    """Each group pops in turn between frames first..last (in the order given, else left to right)."""
    gs = sorted(gs, key=order or (lambda g: g["bbox"][0]))
    count = {}
    for i, g in enumerate(gs):
        n = NAMES.get(g["name"], "Adorno")
        count[n] = count.get(n, 0) + 1
        at = first + (last - first) * i / max(1, len(gs) - 1)
        T.blob(f"{n} {count[n]}", g["polys"], g["colour"], round(at, 1))


def wipe_in(T, clip, box, way, start, frames):
    """Uncovers a still clip with a mask that runs `way` (ltr, btt) from frame `start` over `frames` (drawn on)."""
    from llt_motion import mask_track
    x0, y0, x1, y1 = box
    ease = table({0: 0.0, 0.3: 0.1, 0.6: 0.35, 0.8: 0.7, 1.0: 1.0})

    def rect(u):
        k = ease(min(1.0, max(0.0, (T.frame(u) - start) / frames)))
        if way == "ltr":
            return (x0 - 40, y0 - 40, x0 - 40 + (x1 - x0 + 80) * max(0.001, k), y1 + 40)
        return (x0 - 40, y1 + 40 - (y1 - y0 + 80) * max(0.001, k), x1 + 40, y1 + 40)
    b = Box(clip["x"]["keyframes"][0]["value"], clip["y"]["keyframes"][0]["value"],
            clip["width"]["keyframes"][0]["value"], clip["height"]["keyframes"][0]["value"])
    mask_track(T.t, clip, b, rect, T.dur)


ONE = lambda fr: 1.0  # noqa: E731


def design():
    d = _data("design")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("design", "Título: Design en una nube", "Title: Design in a cloud", D, 8801, ["nube", "garabatos"],
             thumb_at=1.6)
    # Measured: the cloud overshoots to 1.2, the word (5 frames later) to 1.33.
    C = table({1: 0.1, 2: 0.276, 3: 0.58, 4: 0.847, 5: 1.043, 6: 1.157, 7: 1.2, 8: 1.193, 9: 1.153, 10: 1.10,
               11: 1.048, 12: 1.01, 13: 0.983, 14: 0.969, 15: 0.967, 16: 0.97, 17: 0.98, 18: 0.988, 19: 0.996,
               20: 1.002, 21: 1.007, 24: 1.007, 26: 1.0})
    W = table({6: 0.05, 7: 0.36, 8: 0.81, 9: 1.16, 10: 1.33, 11: 1.32, 12: 1.21, 13: 1.07, 14: 0.96, 15: 0.91,
               16: 0.91, 17: 0.95, 18: 0.99, 19: 1.025, 20: 1.04, 22: 1.03, 24: 1.0})
    T = Title(t, D, (962, 540), group=C)
    gs = groups(d["doodles"])
    cloud = max(gs, key=lambda g: (g["bbox"][2] - g["bbox"][0]) * (g["bbox"][3] - g["bbox"][1]))
    T.blob("Nube", cloud["polys"], cloud["colour"], 0, pop=ONE)
    pop_doodles(T, [g for g in gs if g is not cloud], 3, 14)
    T.word("DESIGN", (514, 474, 1405, 605), name="Título", scale=ONE, own=W, fade=None)
    return t


def follow():
    d = _data("follow")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("follow", "Título: Follow me con cinta rosa", "Title: Follow me with a pink ribbon", D, 8802,
             ["instagram", "seguir", "cinta"], thumb_at=1.6)
    T = Title(t, D, (960, 520), group=ONE)
    # The ribbon draws itself from the left; its dark side goes with it.
    pinks = [g for g in d["doodles"] if g["name"] in ("pink", "pinkdark")]
    for name in ("pinkdark", "pink"):
        polys = [poly for g in pinks if g["name"] == name for poly in g["polys"]]
        clip = T.blob(NAMES[name], polys, pinks[[g["name"] for g in pinks].index(name)]["colour"], 0, pop=ONE)
        wipe_in(T, clip, (290, 280, 1540, 745), "ltr", 1, 15)
    pop_doodles(T, groups([g for g in d["doodles"] if g["name"] not in ("pink", "pinkdark")]), 4, 15)
    # The words swing in turning, grow past their size and settle.
    G = table({0: 0.2, 1: 0.3, 2: 0.55, 3: 0.8, 4: 0.95, 5: 1.05, 6: 1.1, 7: 1.12, 8: 1.1, 9: 1.05, 10: 1.02, 12: 1.0})
    R = table({0: -30, 1: -25, 2: -15, 3: -8, 4: 0, 5: 6, 6: 8, 7: 7, 8: 4, 9: 2, 10: 1, 12: 0})
    T.word("FOLLOW ME", (400, 418, 1519, 530), name="Título", scale=ONE, own=G, rot=R,
           fade=table({0: 0.0, 1: 1.0}))
    T.word("on Instagram", (563, 558, 1356, 632), delay=5, name="Título 2", scale=ONE, own=G,
           rot=table({0: -20, 2: -10, 4: 5, 6: 4, 8: 1, 10: 0}), fade=table({0: 0.0, 1: 1.0}), weight=800,
           case="none")
    return t


def smile():
    d = _data("smile")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("smile", "Título: Smile and be happy", "Title: Smile and be happy", D, 8803,
             ["feliz", "sonrisa", "caritas"], thumb_at=1.6)
    T = Title(t, D, (960, 540), group=ONE)
    pop_doodles(T, groups(d["doodles"]), 2, 15)
    # Each line falls from above, overshoots downwards and springs back: HAPPY, AND BE 3 frames later, SMILE 6.
    F = table({-1: -900, 0: -600, 1: -528, 2: -306, 3: -108, 4: 30, 5: 120, 6: 150, 7: 144, 8: 114, 9: 78,
               10: 30, 12: 0})
    fall = lambda fr: (0.0, F(fr))  # noqa: E731
    on = table({-1: 0.0, 0: 1.0})
    T.word("HAPPY", (568, 633, 1348, 758), 0, "Título 3", scale=ONE, shift=fall, fade=on)
    T.word("AND BE", (553, 476, 1366, 603), 3, "Título 2", scale=ONE, shift=fall, fade=on)
    T.word("SMILE", (587, 318, 1332, 449), 6, "Título", scale=ONE, shift=fall, fade=on)
    return t


def subscribe():
    d = _data("subscribe")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("subscribe", "Título: Subscribe con flores", "Title: Subscribe with flowers", D, 8804,
             ["suscribirse", "flores", "youtube"], thumb_at=1.6)
    T = Title(t, D, (960, 540), group=ONE)
    # Two flowers: the yellow one grows up from its stem first, then the pink one.
    gs = groups(d["doodles"])
    for g, (at, n) in zip(sorted(gs, key=lambda g: g["colour"] != "#FCB52B"), [(8, 6), (11, 7)]):
        clip = T.blob("Flor" if g["colour"] == "#FCB52B" else "Flor 2", g["polys"], g["colour"], 0, pop=ONE)
        wipe_in(T, clip, g["bbox"], "btt", at, n)
    # A fast whoosh in from the right (motion blur), past its place, and back.
    X = table({0: 1700, 1: 1300, 2: 870, 3: 480, 4: 150, 5: -80, 6: -205, 7: -252, 8: -245, 9: -200, 10: -140,
               11: -73, 12: -13, 13: 21, 14: 41, 15: 48, 16: 41, 17: 34, 18: 20, 20: 6, 22: 0})
    whoosh = lambda fr: (X(fr), 0.0)  # noqa: E731
    T.word("SUBSCRIBE", (648, 463, 1820, 574), 0, "Título", scale=ONE, shift=whoosh, fade=None, blur=True)
    T.word("my channel", (647, 597, 1294, 676), 3, "Título 2", scale=ONE, shift=whoosh, fade=None, blur=True,
           weight=800, case="none")
    return t


def likenew():
    d = _data("likenew")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("likenew", "Título: Like new video con flecha", "Title: Like new video with an arrow", D, 8805,
             ["like", "video nuevo", "flecha"], thumb_at=1.6)
    T = Title(t, D, (960, 540), group=ONE)
    gs = groups(d["doodles"])
    arrow = max(gs, key=lambda g: (g["bbox"][2] - g["bbox"][0]) * (g["bbox"][3] - g["bbox"][1]))
    a = T.blob("Flecha", arrow["polys"], arrow["colour"], 0, pop=ONE)
    T.place(a, ONE, shift=lambda fr: (table({0: -420, 1: -390, 2: -330, 3: -260, 4: -190, 5: -110, 6: -50, 8: 0})(fr),
                                       0.0))
    T.opacity(a, table({0: 0.0, 1: 0.3, 4: 1.0}))
    pop_doodles(T, [g for g in gs if g is not arrow], 3, 14)
    # Each word pops big and settles: LIKE, NEW 3 frames later, VIDEO 6.
    P = table({0: 0.05, 1: 0.3, 2: 0.9, 3: 1.5, 4: 1.35, 5: 1.21, 6: 1.17, 7: 1.15, 8: 1.13, 9: 1.07, 10: 1.0,
               11: 0.96, 12: 0.95, 14: 0.975, 16: 0.99, 18: 1.0})
    on = table({-1: 0.0, 0: 1.0})
    T.word("LIKE", (230, 322, 782, 447), 0, "Título", scale=ONE, own=P, fade=on)
    T.word("NEW", (237, 478, 716, 603), 3, "Título 2", scale=ONE, own=P, fade=on)
    T.word("VIDEO", (230, 630, 973, 761), 6, "Título 3", scale=ONE, own=P, fade=on)
    return t


def likecount():
    d = _data("likecount")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("likecount", "Título: Like con contador y WOW", "Title: Like with a counter and WOW", D, 8806,
             ["like", "contador", "wow", "corazones"], thumb_at=2.4)
    T = Title(t, D, (960, 540), group=ONE)
    pop_doodles(T, groups(d["doodles"]), 2, 16, order=lambda g: abs((g["bbox"][0] + g["bbox"][2]) / 2 - 960))
    G = table({0: 0.2, 1: 0.35, 2: 0.6, 3: 0.85, 4: 1.0, 5: 1.08, 6: 1.1, 7: 1.08, 8: 1.05, 10: 1.02, 13: 1.0})
    R = table({0: -30, 1: -25, 2: -15, 3: -6, 4: 0, 5: 5, 6: 9, 7: 9, 8: 7, 9: 5, 11: 2, 13: 0})
    T.word("LIKE", (683, 396, 1236, 521), 0, "Título", scale=ONE, own=G, rot=R, fade=table({0: 0.0, 1: 1.0}))
    n = T.word("229K", (653, 555, 1265, 683), 3, "Número", scale=ONE, own=G, rot=R, fade=table({0: 0.0, 1: 1.0}),
               blur=True)
    # The engine's counter counts it up from 0 (the user types the final number).
    n["textStyle"].update(counter=True, counterFrom=0, counterSeconds=0.75)
    return t


def likethis():
    d = _data("likethis")
    D = 3.35  # on screen 3.3 s, as the reference
    t = _kit("likethis", "Título: Like this video con flor", "Title: Like this video with a flower", D, 8807,
             ["like", "flor"], thumb_at=1.6)
    T = Title(t, D, (960, 540), group=ONE)
    gs = groups(d["doodles"])
    flower = max(gs, key=lambda g: (g["bbox"][2] - g["bbox"][0]) * (g["bbox"][3] - g["bbox"][1]))
    clip = T.blob("Flor", flower["polys"], flower["colour"], 0, pop=ONE)
    wipe_in(T, clip, flower["bbox"], "btt", 7, 6)
    pop_doodles(T, [g for g in gs if g is not flower], 10, 13)
    # The lines cross in sideways, swing past their place and back: LIKE from the left, THIS from the right 3
    # frames later, VIDEO from the left 6 frames later.
    L = table({0: -1500, 1: -1000, 2: -620, 3: -230, 4: 62, 5: 225, 6: 297, 7: 277, 8: 240, 9: 135, 10: 67, 11: 7,
               12: -33, 13: -53, 14: -46, 15: -53, 16: -39, 17: -12, 20: 0})
    T.word("LIKE", (683, 479, 1236, 605), 0, "Título", scale=ONE, shift=lambda fr: (L(fr), 0.0), fade=None)
    T.word("THIS", (666, 632, 1253, 761), 3, "Título 2", scale=ONE, shift=lambda fr: (-L(fr), 0.0), fade=None)
    T.word("VIDEO", (588, 784, 1331, 914), 6, "Título 3", scale=ONE, shift=lambda fr: (L(fr), 0.0), fade=None)
    return t


TEMPLATES = [creative, design, follow, smile, subscribe, likenew, likecount, likethis]
