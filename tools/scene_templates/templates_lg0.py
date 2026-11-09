"""LOGO folder video 0 as Stock templates (lg0-*). See docs/plan-logo.md.

The flat logo reveals of 19724440.mp4 (960×540 at 25 fps, laid out at 1920×1080), each studied frame by frame on 10
and 25 fps sheets and measured with colour trackers (study notes in tienda/plantillas/estudio-19724440/NOTAS.md):
a dot that flies round and opens into a disc on blue, a bouncing rounded square that opens into a framed square on
white, a line that draws a loop and drops a dot that grows into a hexagon that rolls aside for the words on coral,
two dots that spiral out drawing a ring that closes into a white disc on amber, ten social icons popping in on
blue, and the coral reveal again over a photo as a «FOLLOW ME / USERNAME» social logo. The brand mark is always the
user's logo slot (`logo-flip`); the social icons are our own glyphs. Every geometry is a function of the
reference's second v (25 fps samples, interpolated); each piece starts at its own `o` and ends where the reference
cuts to the next one. Kit de YouTube › Aperturas / Redes; order 13600-.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import keys, layout, shadow, shape_style
from templates_tit_e import solid
from templates_tit_h import poly, ring
from templates_yp0 import BIRD, W

OS, MONT = "Open Sans", "Montserrat"
for _w, _f in ((400, "Regular"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold")):
    f6._FILES[(OS, _w)] = f"fonts.basic/fonts/opensans/OpenSans-{_f}.ttf"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(MONT, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"

WHITE = "#FFFFFF"
BLUE, NAVY = "#00B7FD", "#054A85"
MINT, INK = "#00EBB4", "#272727"
CORAL, YELLOW, PALE = "#F66262", "#FFD65D", "#FBB0AE"
AMBER, DARK = "#FDAC06", "#413C39"
GREEN, LEMON = "#008156", "#F9E46A"
TRI = poly([(50, 4), (98, 90), (2, 90)])


# --- small helpers ---------------------------------------------------------------------------------------------
def tab(rows):
    """rows = [(v, a, b, …)] sampled at the reference's frames → f(v) = (a, b, …) interpolated, held at the ends."""
    rows = sorted(rows)

    def f(v):
        if v <= rows[0][0]:
            return rows[0][1:]
        for r0, r1 in zip(rows, rows[1:]):
            if v <= r1[0]:
                q = (v - r0[0]) / max(1e-9, r1[0] - r0[0])
                return tuple(a + (b - a) * q for a, b in zip(r0[1:], r1[1:]))
        return rows[-1][1:]
    return f


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ramp(v, a, d):
    return clamp((v - a) / max(1e-9, d))


def ink(text, family, weight, cap, x, top, align="left"):
    """The ink box (x0, top, x1, top + cap) of `text` whose capitals are `cap` px tall, from its left edge x (its
    centre with align="center")."""
    f = f6._font(family, weight)
    hb = f.getbbox("H")
    size = cap * 400 / (hb[3] - hb[1])
    bb = f.getbbox(text)
    w = (f.getlength(text[:-1]) + f.getbbox(text[-1])[2] - bb[0]) * size / 400
    x0 = x - w / 2 if align == "center" else x
    return x0, top, x0 + w, top + cap


def logo(s, g, name="Logo"):
    """The user's logo slot; g(v) = (cx, cy, size, rot, op)."""
    B = 200.0
    box = Box(960 - B / 2, 540 - B / 2, B, B)
    mo, op, rot = [], [], []
    for u in frames_of(s.dur):
        cx, cy, size, r, o = g(u + s.o)
        mo.append((u, {"s": max(1e-3, size / B), "dx": cx - 960, "dy": cy - 540}, "linear"))
        op.append((u, round(clamp(o if size > 0.5 else 0.0), 4), "linear"))
        rot.append((u, round(r, 3), "linear"))
    clip = s.t.photo(s.t.track("video", name), "logo-flip", 0.0, s.dur, box, mo, label="Tu logo", brandRole="logo")
    clip["opacity"] = keys(op)
    if any(abs(v[1]) > 1e-6 for v in rot):
        clip["rotation"] = keys(rot)
    return clip


def widen(clip, extra):
    for kf in clip["width"]["keyframes"]:
        kf["value"] += extra


def letters_in(clip, at, stagger, duration, preset="fade"):
    from scene import tanim
    clip["textStyle"]["animation"] = {"in": tanim(preset, duration=duration, unit="character", stagger=stagger,
                                                  ease="easeOut", delay=round(at, 3))}


def spacing(s, clip, fn):
    """letterSpacing (px) = fn(v) every frame."""
    clip["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
        [(u, round(fn(u + s.o), 3), "linear") for u in frames_of(s.dur)])


def stroke_path(s, name, pts, width, colour, trim, alpha=1.0, smooth=True):
    """An open line through screen points `pts` (Catmull-Rom smoothed) showing from trim(v) = (start, end) in
    fractions of its length, every frame."""
    if smooth:
        out = []
        P = [pts[0]] + list(pts) + [pts[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            for j in range(8):
                t = j / 8
                out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k])
                                        * t * t + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
        out.append(pts[-1])
        pts = out
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    m = width + 4
    bx0, by0 = min(xs) - m, min(ys) - m
    bw, bh = max(xs) - min(xs) + 2 * m, max(ys) - min(ys) + 2 * m
    path = "M " + " L ".join(f"{(x - bx0) / bw * 100:.3f} {(y - by0) / bh * 100:.3f}" for x, y in pts)
    st = {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "opacity": 1.0, "cap": "round",
          "join": "round", "strokeAlign": "center",
          "paint": {"kind": "solid", "color": "#" + format(round(alpha * 255), "02x") + colour.lstrip("#").lower()}}
    hollow = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}
    style = shape_style("custom", [hollow, st], customPath=path, customEvenOdd=False)
    us_ = frames_of(s.dur)
    style["keyframes"] = {"trimStart": keys([(u, round(100 * trim(u + s.o)[0], 3), "linear") for u in us_]),
                          "trimEnd": keys([(u, round(100 * trim(u + s.o)[1], 3), "linear") for u in us_])}
    clip = s.t._clip("shape", 0.0, s.dur, shapeStyle=style, **layout(Box(bx0, by0, bw, bh), None))
    clip["name"] = name
    vis = [(u, 1.0 if trim(u + s.o)[1] - trim(u + s.o)[0] > 1e-4 else 0.0, "hold") for u in us_]
    clip["opacity"] = keys(vis)
    s.t.track("shape", name).clips.append(clip)
    return clip


def sh(s, name, layers, g, base, radius=0.0, stroke=0.0, **kw):
    """W.shp whose corner radius and stroke width (given at the base size) follow its size every frame: the engine
    lays a shape out at its size in px, so neither grows with it by itself."""
    clip = s.shp(name, layers, g, base=base, radius=radius, **kw)
    us_ = frames_of(s.dur)
    sc = [(u, min(g(u + s.o)[2] / base[0], g(u + s.o)[3] / base[1])) for u in us_]
    kf = clip["shapeStyle"].setdefault("keyframes", {})
    if radius:
        kf["cornerRadius"] = keys([(u, round(max(0.0, radius * v), 3), "linear") for u, v in sc])
    if stroke:
        kf["layer.stroke.width"] = keys([(u, round(max(0.0, stroke * v), 3), "linear") for u, v in sc])
    return clip


def background(s, colour):
    clip = s.shp("Fondo", solid(colour), lambda v: (960, 540, 1920, 1080, 0, 1))
    return clip


# --- the burst every reveal throws when the logo opens (measured on 1.04–1.84 s) ----------------------------------
# (kind, place when it shows (v0 + 0.08), place 0.64 s later, turn) relative to the logo's centre, 1920 px.
_SHAPES = (("tri", (-160, -92), (-376, -152), 60), ("circ", (-186, 24), (-505, 13), 0),
           ("sq", (-190, 118), (-447, 169), 35), ("sq", (194, -58), (443, -105), -30),
           ("circ", (184, 34), (505, 51), 0), ("tri", (148, 148), (377, 218), -50))
# (side, y at v0, y at the end, tilt, length factor)
_DASHES = ((-1, -32, -62, 8, 1.0), (-1, 68, 68, 0, 1.2), (1, -6, -8, 0, 1.0), (1, 88, 112, 8, 1.1))
_DASH_X = tab([(0.0, 190), (0.08, 242), (0.16, 298), (0.24, 338), (0.32, 370), (0.44, 400), (0.48, 405)])
_DASH_L = tab([(0.0, 50), (0.08, 60), (0.16, 48), (0.24, 36), (0.32, 28), (0.44, 8), (0.48, 0)])


def burst(s, cx, cy, v0, colour, k=1.0):
    """Four short dashes fly out sideways and shorten from v0; six hollow shapes (triangle, circle, square each
    side) come out from behind the logo from v0 + 0.04, slowing down, and fade from v0 + 0.44."""
    for i, (side, y0, y1, tilt, lf) in enumerate(_DASHES):
        def g(v, side=side, y0=y0, y1=y1, tilt=tilt, lf=lf):
            d = v - v0
            if d < 0 or d > 0.48:
                return cx, cy, 1, 8, 0, 0.0
            q = d / 0.48
            x = cx + side * (_DASH_X(d)[0] + (8 if lf > 1.05 else 0)) * k
            return x, cy + (y0 + (y1 - y0) * q) * k, max(1.0, _DASH_L(d)[0] * lf * k), 8 * k, tilt, 1.0
        s.shp(f"Rayita {i + 1}", solid(colour), g, radius=4, base=(60, 8))
    for i, (kind, p0, p1, turn) in enumerate(_SHAPES):
        size = {"tri": 36, "circ": 28, "sq": 26}[kind] * k

        def g(v, p0=p0, p1=p1, turn=turn, size=size):
            d = v - v0
            if d < 0.04:
                return cx, cy, size, size, 0, 0.0
            if d < 0.08:
                f = 0.75 + 0.25 * (d - 0.04) / 0.04
                x, y = p0[0] * f, p0[1] * f
                q = 0.0
            else:
                q = 1 - (1 - clamp((d - 0.08) / 0.64)) ** 1.6
                x, y = p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q
            return cx + x * k, cy + y * k, size, size, turn * q, 1 - ramp(d, 0.44, 0.36)
        kw = {"kind": "ellipse"} if kind == "circ" else {"path": TRI} if kind == "tri" else {"radius": 4 * k}
        s.shp(f"Figura {i + 1}", ring(colour, 7 * k), g, base=(size, size), **kw)


def brand_words(s, top, colour, t1, t2, cap=26, cx=962, fade=0.04, way=1):
    """«YOUR» (regular) and «BRAND» (bold) centred under the logo; each rises from below (t1, t2)."""
    a = ink("YOUR", OS, 400, cap, 0, top)
    b = ink("BRAND", OS, 700, cap, 0, top)
    gap = 0.55 * cap
    x0 = cx - (a[2] - a[0] + gap + b[2] - b[0]) / 2
    ia = (x0, top, x0 + a[2] - a[0], top + cap)
    ib = (ia[2] + gap, top, ia[2] + gap + b[2] - b[0], top + cap)
    r1 = tab([(t1, 96), (t1 + .04, 70), (t1 + .08, 44), (t1 + .12, 18), (t1 + .16, -4), (t1 + .2, -12),
              (t1 + .24, -6), (t1 + .32, 0)])
    r2 = tab([(t2 - .04, 96), (t2, 62), (t2 + .04, 28), (t2 + .08, 0), (t2 + .12, -4), (t2 + .2, 0)])
    s.txt("YOUR", ia, OS, 400, colour, "Texto", g=lambda v: (0, way * r1(v)[0], 1, 0, ramp(v, t1, fade)))
    s.txt("BRAND", ib, OS, 700, colour, "Marca", g=lambda v: (0, way * r2(v)[0], 1, 0, ramp(v, t2 - 0.04, fade)))


def _p(id, es, en, order, dur, thumb, tags=(), section="aperturas"):
    return wide(f"lg0-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "logo", "revelación de logo", "plano"] + list(tags), thumb_at=thumb)


# --- 1. Blue: a dot flies round and opens into a disc with the logo (0.00–3.00 s) --------------------------------
_DOT1 = tab([(0.10, 1073, 360, 0), (0.12, 1073, 360, 3), (0.16, 1081, 367, 4), (0.20, 1085, 376, 6),
             (0.24, 1102, 387, 8), (0.28, 1118, 399, 9), (0.32, 1228, 422, 10), (0.36, 1287, 402, 11),
             (0.40, 1342, 383, 12), (0.44, 1394, 326, 14), (0.48, 1382, 287, 15), (0.52, 1369, 249, 15),
             (0.56, 1288, 183, 16), (0.60, 1228, 165, 17), (0.64, 1168, 148, 19), (0.68, 999, 168, 18),
             (0.72, 896, 208, 20), (0.76, 795, 248, 21), (0.80, 658, 419, 23), (0.84, 640, 523, 23),
             (0.88, 633, 620, 24), (0.92, 847, 669, 36), (0.96, 896, 621, 77), (1.00, 944, 600, 170),
             (1.04, 958, 514, 352), (1.08, 959, 512, 376), (1.12, 960, 512, 356), (1.16, 960, 512, 336),
             (1.20, 960, 512, 320), (1.24, 960, 512, 312), (1.28, 960, 512, 304), (1.36, 960, 512, 300)])
_LOGO1 = tab([(0.98, 0.0), (1.00, 0.85), (1.04, 0.56), (1.10, 0.5)])


def blue_disc():
    O, D = 0.0, 3.0
    t = _p("disco-azul", "Logo: punto que vuela y se abre en un disco (azul)",
           "Logo: flying dot that opens into a disc (blue)", 13600, D, 2.0, ["azul", "disco", "punto"])
    s = W(t, D, O)
    background(s, BLUE)
    burst(s, 960, 512, 1.04, NAVY)
    brand_words(s, 738, NAVY, 0.84, 1.00)

    def disc(v):
        x, y, d = _DOT1(v)
        return x, y, d, d, 0, 1.0 if v >= 0.11 else 0.0
    s.shp("Disco", [shadow("#003C7A", 0, 8, 12, 0.6)] + solid(NAVY), disc, kind="ellipse", base=(376, 376))
    logo(s, lambda v: (lambda x, y, d: (x, y, d * _LOGO1(v)[0], 0, 1.0 if v >= 0.99 else 0.0))(*_DOT1(v)))
    return t


# --- 2. White: a rounded square bounces twice and opens into a framed square (3.04–6.00 s) -----------------------
# (v, cy, w, h, turn): the square's screen size; past 45° its local w / h are swapped.
_SQ = tab([(3.14, 451, 0, 0, 0), (3.16, 451, 32, 32, 0), (3.20, 461, 72, 68, 0), (3.24, 530, 72, 74, 0),
           (3.28, 682, 74, 26, 0), (3.32, 649, 74, 28, 0), (3.36, 499, 70, 66, 10), (3.40, 431, 72, 72, 25),
           (3.44, 402, 72, 72, 40), (3.48, 387, 72, 72, 50), (3.52, 379, 72, 72, 60), (3.56, 376, 72, 72, 70),
           (3.60, 382, 72, 72, 78), (3.64, 399, 72, 74, 86), (3.68, 434, 72, 76, 90), (3.72, 497, 72, 76, 90),
           (3.76, 682, 80, 26, 90), (3.80, 683, 96, 40, 90), (3.84, 648, 132, 124, 90), (3.88, 615, 112, 112, 90),
           (3.92, 557, 96, 94, 90), (3.96, 531, 120, 120, 90), (4.00, 529, 248, 248, 90),
           (4.04, 527, 320, 320, 90), (4.08, 520, 350, 350, 90), (4.12, 507, 368, 368, 90),
           (4.16, 497, 376, 376, 90), (4.20, 494, 382, 382, 90), (4.24, 495, 352, 352, 90),
           (4.28, 498, 344, 344, 90)])
# (v, white square, inner square, frame opacity): the frame's white and inner mint squares while it opens.
_IN = tab([(3.94, 0, 0, 1), (3.96, 40, 12, 1), (4.00, 128, 72, 1), (4.04, 256, 140, 1), (4.08, 300, 226, 1),
           (4.12, 340, 284, 1), (4.16, 356, 320, 1), (4.20, 370, 340, 1), (4.24, 350, 340, 0.5),
           (4.28, 336, 336, 0), (4.32, 334, 334, 0), (4.36, 320, 320, 0), (4.40, 310, 310, 0),
           (4.44, 306, 306, 0), (4.48, 304, 304, 0)])
_CY2 = tab([(4.20, 494), (4.24, 495), (4.28, 498), (4.32, 500), (4.36, 502), (4.44, 504), (4.56, 505)])


def white_square():
    O, D = 3.04, 3.0
    t = _p("cuadro-blanco", "Logo: cuadrado que rebota y se abre (blanco)",
           "Logo: bouncing square that opens (white)", 13601, D, 2.2, ["blanco", "cuadrado", "rebote", "menta"])
    s = W(t, D, O)
    background(s, WHITE)
    burst(s, 960, 505, 4.04, INK)
    brand_words(s, 738, INK, 4.08, 4.28, way=-1)  # they drop from behind the square

    def outer(v):
        cy, w, h, turn = _SQ(v)
        if turn >= 45:
            w, h = h, w
        op = 1.0 if v >= 3.15 else 0.0
        if v > 4.20:
            op = 1 - ramp(v, 4.20, 0.08)
        return 960, cy, w, h, turn, op
    sh(s, "Marco", [shadow("#7A6FD0", 0, 6, 10, 0.35)] + solid(MINT), outer, (382, 382), radius=84)
    cy = lambda v: _SQ(v)[0] if v < 4.20 else _CY2(v)[0]  # noqa: E731
    sh(s, "Marco (blanco)", solid(WHITE), lambda v: (960, cy(v), _IN(v)[0], _IN(v)[0], 0,
                                                     1.0 if 3.95 <= v and _IN(v)[2] > 0 else 0.0),
       (370, 370), radius=78)
    inner = sh(s, "Cuadro", solid(MINT), lambda v: (960, cy(v), _IN(v)[1], _IN(v)[1], 0, 1.0 if v >= 3.95 else 0.0),
               (340, 340), radius=70)
    lg = logo(s, lambda v: (960, cy(v) + _IN(v)[1] * 0.75 * (1 - ramp(v, 4.06, 0.14)) ** 1.5,
                            _IN(v)[1] * 0.5, 0, 1.0 if v >= 4.05 else 0.0))
    lg["matte"] = {"clip": inner["id"], "mode": "alpha", "keepSource": True}
    return t


# --- 3. Coral: a line draws a loop, drops a dot that grows into a hexagon that rolls aside (6.00–10.04 s) ---------
_LINE = [(680, 262), (760, 265), (840, 280), (910, 310), (965, 350), (1010, 410), (1040, 480), (1050, 560),
         (1040, 640), (1010, 710), (965, 775), (905, 822), (860, 832), (810, 820), (770, 785), (750, 730), (758, 665),
         (790, 610), (840, 560), (900, 515), (960, 475), (1030, 435), (1100, 390), (1150, 350), (1180, 300),
         (1185, 262), (1170, 228), (1140, 207), (1105, 200), (1060, 210), (1020, 235), (990, 275), (970, 320),
         (962, 370), (960, 430), (960, 520), (960, 700), (960, 870)]
_TRIM = tab([(6.04, 0, 0), (6.08, 0, .101), (6.12, 0, .213), (6.16, 0, .311), (6.20, .113, .403),
             (6.24, .253, .483), (6.28, .369, .560), (6.32, .469, .629), (6.36, .554, .687), (6.40, .626, .742),
             (6.44, .689, .791), (6.48, .748, .832), (6.52, .796, .869), (6.56, .837, .902), (6.60, .871, .927),
             (6.64, .902, .950), (6.68, .925, .969), (6.72, .946, .983), (6.76, .962, .995), (6.80, .974, .997),
             (6.84, .983, .997), (6.88, .990, .997), (6.92, .997, .997)])
# (v, cy, w, h) of the dot / circle (its diameter on screen) until it lands.
_BALL = tab([(6.86, 896, 0, 0), (6.88, 896, 16, 16), (6.92, 952, 68, 66), (6.96, 839, 176, 176),
             (7.00, 588, 228, 224), (7.04, 427, 256, 248), (7.08, 363, 272, 264), (7.12, 329, 280, 272),
             (7.16, 310, 288, 278), (7.20, 301, 288, 284), (7.24, 298, 288, 282), (7.28, 302, 288, 282),
             (7.32, 312, 290, 286), (7.36, 327, 294, 286), (7.40, 349, 296, 292), (7.44, 378, 288, 302),
             (7.48, 418, 290, 308), (7.52, 540, 325, 325), (7.56, 540, 290, 290), (7.60, 540, 284, 284),
             (7.64, 540, 290, 290)])
_SLIDE = tab([(7.96, 960, 0), (8.00, 954, -5), (8.04, 920, -12), (8.08, 850, -20), (8.12, 800, -25),
              (8.16, 770, -28), (8.20, 750, -30), (8.24, 736, -30), (8.28, 728, -30), (8.32, 720, -30),
              (8.36, 714, -30), (8.44, 710, -30)])
HEX_BASE = 340.0


def _polar(rf, n=96):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = rf(a) / HEX_BASE * 100
        pts.append((50 + r * math.cos(a), 50 + r * math.sin(a)))
    return poly(pts)


def _hex_r(a, R=166.3, p=8.0):
    """A rounded flat-top hexagon (vertices left and right) of circumradius R, in polar form."""
    tot = sum(max(0.0, math.cos(a - math.radians(30 + 60 * j))) ** p for j in range(6))
    return R * math.cos(math.radians(30)) * tot ** (-1 / p)


CIRCLE_PATH = _polar(lambda a: 145.0)
HEX_PATH = _polar(_hex_r)
# The dribbble-like ball (our own glyph): curves in a 100 box.
BALL_LINES = "M 32 4 C 50 28 66 60 74 96 M 3 42 C 30 50 70 40 92 22 M 16 84 C 34 60 64 52 98 58"


def hex_reveal(s, bg_line, line, pale, ball, mark, words, under, txt_colour, fonts):
    """The coral reveal (scene times 6.00–10.04 s): `mark(cx_fn)` draws what sits in the hexagon; words =
    (first, second); fonts = ((family, weight), (family, weight))."""
    trim = lambda v: _TRIM(v) if v < 6.93 else (1.0, 1.0)  # noqa: E731
    stroke_path(s, "Línea (sombra)", [(x + 6, y - 6) for x, y in _LINE], 4, pale, trim, alpha=0.55)
    stroke_path(s, "Línea", _LINE, 4, line, trim)
    burst(s, 960, 540, 7.52, ball)

    def hexa(v):
        if v < 7.64:
            cy, w, h = _BALL(v)
            return 960, cy, w * HEX_BASE / 290, h * HEX_BASE / 290, 0, 1.0 if v >= 6.87 else 0.0
        x, rot = _SLIDE(v)
        return x, 540, HEX_BASE, HEX_BASE, rot, 1.0
    hx = s.shp("Hexágono", [shadow("#000000", 0, 6, 10, 0.18)] + solid(ball), hexa, path=CIRCLE_PATH,
               base=(HEX_BASE, HEX_BASE))
    st = hx["shapeStyle"]
    st["pathShapes"] = [CIRCLE_PATH, HEX_PATH]
    st.setdefault("keyframes", {})["path"] = keys([(0.0, 0, "hold"), (round(7.36 - s.o, 4), 0, "linear"),
                                                   (round(7.52 - s.o, 4), 1, "hold")])
    pop = tab([(7.50, 0.0), (7.52, 1.12), (7.56, 1.0), (7.60, 0.98), (7.64, 1.0)])
    cx = lambda v: _SLIDE(v)[0] if v >= 7.64 else 960  # noqa: E731
    rise = lambda v: 1 - ramp(v, 7.50, 0.08)  # noqa: E731 - the mark rises into the shape as it lands
    made = mark(cx, lambda v: pop(v)[0] if v < 7.64 else 1.0, lambda v: 0.6 * rise(v) ** 1.5)
    for c in made:
        c["matte"] = {"clip": hx["id"], "mode": "alpha", "keepSource": True}
    # The words: they slide in from the right with their letters apart, closing up and lighting left to right.
    (f1, w1), (f2, w2) = fonts
    a = ink(words[0], f1, w1, 52, 886, 468)
    b = ink(words[1], f2, w2, 82, 888, 556)
    dx1 = tab([(7.98, 400), (8.00, 394), (8.04, 330), (8.08, 244), (8.12, 150), (8.16, 78), (8.20, 38),
               (8.24, 18), (8.28, 4), (8.32, -2), (8.36, -6), (8.44, 0)])
    dx2 = tab([(8.06, 520), (8.08, 462), (8.12, 348), (8.16, 218), (8.20, 128), (8.24, 68), (8.28, 36),
               (8.32, 16), (8.36, 2), (8.44, 0)])
    sp1 = tab([(7.98, 64), (8.00, 60), (8.12, 46), (8.20, 24), (8.28, 14), (8.36, 2), (8.44, 0)])
    sp2 = tab([(8.06, 130), (8.08, 120), (8.12, 105), (8.20, 60), (8.28, 40), (8.36, 11), (8.44, 0)])
    c1 = s.txt(words[0], a, f1, w1, txt_colour, "Texto", align="left",
               g=lambda v: (dx1(v)[0], 0, 1, 0, 1.0 if v >= 7.97 else 0.0))
    c2 = s.txt(words[1], b, f2, w2, txt_colour, "Marca", align="left",
               g=lambda v: (dx2(v)[0], 0, 1, 0, 1.0 if v >= 8.05 else 0.0))
    fin1, fin2 = 0.08 * c1["textStyle"]["pixelSize"], 0.05 * c2["textStyle"]["pixelSize"]
    spacing(s, c1, lambda v: sp1(v)[0] + fin1)
    spacing(s, c2, lambda v: sp2(v)[0] + fin2)
    widen(c1, 600)
    widen(c2, 900)
    letters_in(c1, 7.97 - s.o, 0.05, 0.22)
    letters_in(c2, 8.05 - s.o, 0.05, 0.24)
    ul = tab([(8.02, 1390, 0), (8.04, 1340, 100), (8.08, 1230, 180), (8.12, 1140, 210), (8.16, 1070, 230),
              (8.20, 1016, 244), (8.24, 976, 260), (8.28, 940, 280), (8.32, 916, 288), (8.36, 904, 292),
              (8.44, 886, under)])
    s.shp("Raya", solid(ball if bg_line is None else bg_line),
          lambda v: (lambda x, w: (x + w / 2, 540, max(1.0, w), 8, 0, 1.0 if v >= 8.03 else 0.0))(*ul(v)),
          base=(under, 8))


def coral_hexagon():
    O, D = 6.0, 4.04
    t = _p("hexagono-coral", "Logo: línea, círculo y hexágono que rueda con tu marca (coral)",
           "Logo: line, circle and rolling hexagon with your brand (coral)", 13602, D, 3.2,
           ["coral", "hexágono", "línea", "amarillo"])
    s = W(t, D, O)
    background(s, CORAL)

    def mark(cx, pop, low):
        return [logo(s, lambda v: (cx(v), 540 + 150 * low(v), 150 * pop(v), 0, 1.0 if v >= 7.50 else 0.0))]
    hex_reveal(s, None, WHITE, PALE, YELLOW, mark, ("YOUR", "BRAND"), 300, WHITE, ((MONT, 400), (MONT, 700)))
    return t


# --- 4. Amber: two dots spiral out drawing a ring that closes into a white disc (10.04–14.04 s) --------------------
_SPIN = tab([(10.04, 0, 0, 20), (10.08, 0, 5, 20), (10.12, -3, 22, 20), (10.16, -7, 95, 20), (10.20, -11, 161, 20),
             (10.24, -17, 191, 20), (10.28, -26, 207, 20), (10.32, -37, 215, 20), (10.36, -54, 221, 20),
             (10.40, -75, 224, 20), (10.44, -99, 225, 20), (10.48, -132, 225, 20), (10.52, -178, 225, 20),
             (10.56, -226, 225, 20), (10.60, -267.5, 225, 20), (10.64, -302, 225, 20), (10.68, -331, 225, 20),
             (10.72, -356, 225, 20), (10.76, -376.5, 225, 20), (10.80, -394, 225, 20), (10.84, -408, 225, 20),
             (10.88, -420, 225, 24), (10.92, -429.5, 225, 26), (10.96, -437, 225, 27), (11.00, -442.6, 225, 14),
             (11.03, -446, 225, 0)])
_TRAIL = tab([(10.48, 0), (10.56, 48), (10.64, 96), (10.72, 132), (10.80, 160), (10.88, 174), (10.96, 180)])
# (v, outer radius, hole radius): the thin ring grows, thickens and closes into a dot; then the dark disc.
_RING = tab([(10.98, 225, 222), (11.08, 227, 224), (11.16, 251, 248), (11.24, 263, 260), (11.32, 267, 264),
             (11.36, 270, 260), (11.40, 260, 248), (11.44, 240, 218), (11.48, 180, 151), (11.52, 96, 72),
             (11.56, 52, 33), (11.60, 32, 6), (11.64, 20, 0), (11.68, 77, 0), (11.72, 120, 0), (11.76, 152, 0),
             (11.80, 176, 30), (11.84, 192, 92), (11.88, 200, 146), (11.92, 204, 175), (11.96, 204, 188),
             (12.00, 170, 160), (12.04, 150, 140)])
_WHITE = tab([(11.72, 0), (11.76, 12), (11.80, 26), (11.84, 44), (11.88, 70), (11.92, 108), (11.96, 180),
              (12.00, 180), (12.04, 178), (12.08, 172), (12.12, 168), (12.16, 162), (12.20, 160), (12.30, 158)])
_CY4 = tab([(12.00, 539), (12.04, 535), (12.08, 530), (12.12, 528), (12.16, 527), (12.20, 525), (12.28, 515),
            (12.36, 509), (12.44, 506)])


def amber_circle():
    O, D = 10.04, 4.0
    t = _p("circulo-ambar", "Logo: dos puntos que dibujan un aro y se cierra en un disco (ámbar)",
           "Logo: two dots draw a ring that closes into a disc (amber)", 13603, D, 3.0,
           ["ámbar", "amarillo", "círculo", "aro", "puntos"])
    s = W(t, D, O)
    background(s, AMBER)
    burst(s, 960, 530, 12.0, DARK)
    brand_words(s, 711, DARK, 12.14, 12.32, fade=0.1)
    # The two half-circle trails: a circle path starting at 0° going round counter-clockwise (screen), trimmed
    # to the TRAIL degrees behind each dot.
    circ = [(960 + 225 * math.cos(math.radians(-a)), 539 + 225 * math.sin(math.radians(-a))) for a in range(0, 721, 4)]
    for i in range(2):
        def trim(v, i=i):
            if v < 10.48 or v > 11.0:
                return (0.0, 0.0)
            head = (-_SPIN(v)[0] + 180 * i) / 720
            return max(0.0, head - _TRAIL(v)[0] / 720), head
        stroke_path(s, f"Trazo {i + 1}", circ, 3, DARK, trim, smooth=False)
    for i in range(2):
        def dot(v, i=i):
            a, r, d = _SPIN(v)
            a = math.radians(a + 180 * i)
            on = 10.03 <= v <= 11.02 and (i == 0 or v >= 10.10)
            return 960 + r * math.cos(a), 539 + r * math.sin(a), d, d, 0, 1.0 if on else 0.0
        s.shp(f"Punto {i + 1}", solid(DARK), dot, kind="ellipse", base=(28, 28))
    cy = lambda v: _CY4(v)[0]  # noqa: E731
    on_ring = lambda v: 10.99 <= v  # noqa: E731
    s.shp("Aro", solid(DARK), lambda v: (960, cy(v), 2 * _RING(v)[0], 2 * _RING(v)[0], 0, 1.0 if on_ring(v) else 0.0),
          kind="ellipse", base=(540, 540))
    s.shp("Aro (hueco)", solid(AMBER), lambda v: (960, cy(v), 2 * _RING(v)[1], 2 * _RING(v)[1], 0,
                                                  1.0 if on_ring(v) and _RING(v)[1] > 0.5 else 0.0),
          kind="ellipse", base=(528, 528))
    s.shp("Disco", [shadow("#7A4A00", 0, 8, 12, 0.35)] + solid(WHITE),
          lambda v: (960, cy(v), 2 * _WHITE(v)[0], 2 * _WHITE(v)[0], 0, 1.0 if v >= 11.73 else 0.0),
          kind="ellipse", base=(360, 360))
    logo(s, lambda v: (960, cy(v), _WHITE(v)[0] * 1.0, 0, 1.0 if v >= 11.77 else 0.0))
    return t


# --- 5. Blue: ten social icons pop in one after another (14.04–17.24 s) ----------------------------------------
_POP = tab([(0.0, 0.0), (0.04, .08), (0.08, .18), (0.12, .32), (0.16, .52), (0.20, .70), (0.24, .84), (0.28, .94),
            (0.32, 1.0), (0.36, 1.02), (0.40, 1.01), (0.44, 1.0)])
F_PATH = ("M 38 100 L 38 40 L 26 40 L 26 24 L 38 24 L 38 17 C 38 5 45 0 57 0 L 72 0 L 72 16 L 62 16 "
          "C 58 16 57 18 57 22 L 57 24 L 72 24 L 70 40 L 57 40 L 57 100 Z")
IN_PATH = ("M 9 32 L 25 32 L 25 98 L 9 98 Z M 36 98 L 36 32 L 51 32 L 51 40 C 56 33 63 30 72 30 C 88 30 96 40 96 58 "
           "L 96 98 L 80 98 L 80 62 C 80 52 76 46 68 46 C 58 46 52 52 52 62 L 52 98 Z")
PIN_PATH = "M 34 98 L 50 42 M 30 66 C 14 54 16 24 40 12 C 66 0 92 12 92 38 C 92 62 76 76 58 74 C 48 73 44 66 46 58"
VIMEO_PATH = "M 4 34 C 14 22 22 22 26 36 L 38 84 C 40 92 44 92 50 84 C 70 60 86 36 90 22 C 94 8 82 2 70 12"
VINE_PATH = "M 8 24 L 34 92 C 60 72 80 46 84 28 C 88 10 72 4 62 16 C 54 28 60 46 72 50"


def social_icons():
    O, D = 14.04, 3.2
    t = _p("iconos-redes", "Diez iconos de redes sociales que aparecen (azul)",
           "Ten social media icons popping in (blue)", 13604, D, 1.6,
           ["redes", "iconos", "facebook", "instagram", "twitter", "youtube", "azul"], section="redes")
    s = W(t, D, O)
    background(s, BLUE)
    SZ = 180.0
    cols = (472, 712, 957, 1202, 1447)

    def at(i):
        return (cols[i % 5], 484 if i < 5 else 766), 14.07 + 0.04 * i

    def part(i, name, layers, box, radius=0.0, stroke=0.0, **kw):
        """A part of icon i in its 0..100 box (x0, y0, x1, y1)."""
        (cx, cy), t0 = at(i)
        bx = ((box[0] + box[2]) / 2 - 50) * SZ / 100
        by = ((box[1] + box[3]) / 2 - 50) * SZ / 100
        bw, bh = (box[2] - box[0]) * SZ / 100, (box[3] - box[1]) * SZ / 100

        def g(v):
            sc = _POP(v - t0)[0]
            return cx + bx * sc, cy + by * sc, bw * sc, bh * sc, 0, 1.0 if v > t0 + 0.01 else 0.0
        return sh(s, name, layers, g, (bw, bh), radius=radius, stroke=stroke, **kw)
    # 1 a ball
    part(0, "Icono balón", ring(NAVY, 17), stroke=17, box=(6, 6, 94, 94), kind="ellipse")
    part(0, "Icono balón (líneas)", ring(NAVY, 14), stroke=14, box=(6, 6, 94, 94), path=BALL_LINES)
    # 2 f
    part(1, "Icono f", solid(NAVY), (14, 2, 98, 100), path=F_PATH)
    # 3 camera
    part(2, "Icono cámara", ring(NAVY, 18), stroke=18, box=(6, 6, 94, 94), radius=34)
    part(2, "Icono cámara (lente)", ring(NAVY, 18), stroke=18, box=(29, 29, 71, 71), kind="ellipse")
    part(2, "Icono cámara (punto)", solid(NAVY), (68, 18, 80, 30), kind="ellipse")
    # 4 in
    part(3, "Icono in", solid(NAVY), (4, 4, 100, 100), path=IN_PATH)
    part(3, "Icono in (punto)", solid(NAVY), (6, 2, 28, 24), kind="ellipse")
    # 5 a pin
    part(4, "Icono pin", ring(NAVY, 22), stroke=22, box=(10, 2, 96, 100), path=PIN_PATH)
    # 6 a cloud with an S
    part(5, "Icono nube", solid(NAVY), (4, 4, 96, 96), kind="ellipse")
    part(5, "Icono nube (arriba)", solid(NAVY), (-2, -2, 46, 46), kind="ellipse")
    part(5, "Icono nube (abajo)", solid(NAVY), (54, 54, 102, 102), kind="ellipse")
    (cx, cy), t0 = at(5)
    sink = ink("S", OS, 700, 0.5 * SZ, cx, cy - 0.25 * SZ, align="center")
    s.txt("S", sink, OS, 700, BLUE, "Icono nube (S)", editable=False,
          g=lambda v: (0, 0, max(1e-3, _POP(v - t0)[0]), 0, 1.0 if v > t0 + 0.01 else 0.0))
    # 7 a bird
    part(6, "Icono pájaro", solid(NAVY), (-6, 0, 106, 100), path=BIRD)
    # 8 a curly v
    part(7, "Icono v", ring(NAVY, 26), stroke=26, box=(-2, 0, 102, 102), path=VIMEO_PATH)
    # 9 a vine
    part(8, "Icono hoja", ring(NAVY, 22), stroke=22, box=(4, -2, 96, 102), path=VINE_PATH)
    # 10 a play button
    part(9, "Icono play", solid(NAVY), (-4, 12, 104, 88), radius=34)
    part(9, "Icono play (triángulo)", solid(BLUE), (38, 34, 68, 66), path=poly([(0, 0), (100, 50), (0, 100)]))
    return t


# --- 6. Photo: the coral reveal as a «FOLLOW ME / USERNAME» social logo (21.28–25.32 s) ----------------------------
def follow_me():
    D = 4.04
    t = _p("sigueme", "Logo social: sígueme con balón en hexágono sobre foto",
           "Social logo: follow me with a ball in a hexagon over a photo", 13605, D, 3.2,
           ["sígueme", "usuario", "hexágono", "foto", "verde"], section="redes")
    s = W(t, D, 6.0)  # the same scene times as the coral reveal
    ph = t.photo(t.track("video", "Foto"), "h-nature-02", 0.0, D, None, None, label="Tu foto")
    ph["effects"] = [{"catalogId": "stylize.grayscale", "parameters": {}, "enabled": True}]
    ph["layoutRole"] = "cover"
    shade = s.shp("Sombra", solid("#000000", 0.55), lambda v: (960, 540, 1920, 1080, 0, 1))
    shade["layoutRole"] = "cover"

    def mark(cx, pop, low):
        def g(v, d=240):
            sc = pop(v)
            return cx(v), 540 + d * low(v), d * sc, d * sc, 0, 1.0 if v >= 7.50 else 0.0
        return [sh(s, "Balón", ring(LEMON, 22), g, (240, 240), stroke=22, kind="ellipse"),
                sh(s, "Balón (líneas)", ring(LEMON, 18),
                   lambda v: (lambda c: (c[0], c[1], c[2] * 0.92, c[3] * 0.92, 0, c[5]))(g(v)), (221, 221), stroke=18,
                   path=BALL_LINES)]
    hex_reveal(s, GREEN, LEMON, "#9A9A9A", GREEN, mark, ("FOLLOW ME", "USERNAME"), 442, WHITE, ((OS, 400), (OS, 700)))
    return t


TEMPLATES = [blue_disc, white_square, coral_hexagon, amber_circle, social_icons, follow_me]
