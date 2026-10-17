"""Seventh batch: face-cam frames (category "camara-cara") for gaming and podcast videos.

Each frame has its own canvas (1080 x 1080 for round, hexagonal and square frames, 1280 x 720 or a bit
taller for 16:9 frames with a plate or a bar under them) so it can sit wherever the user puts the camera.
The hole is fully transparent: every frame is cut by its own hole mask at the end, and the same mask is
what build.py fills with a person for the card and the preview.
"""

from __future__ import annotations

import math

import numpy as np

import fx
from fx import TAU, Canvas
from designs import design
from kit import (Art, Pen, back_out, blur, damped, ease_io, grow, hexc, icon_heart, lerp, mix, put, seg, shift,
                 text_width)

CAM = ["camara", "webcam", "facecam", "face cam", "marco", "frame", "gaming", "streamer", "stream"]
WHITE = (1.0, 1.0, 1.0)
SQ = (1080, 1080)
WIDE = (1280, 720)


def cam(id, es, en, seconds, size, hole, *, loop=True, tags=(), sample="portrait-04.jpg",
        backdrop="h-gaming-01.jpg", thumb_at=0.5, crf=32):
    return design(id, es, en, "camara-cara", seconds, loop=loop, tags=CAM + list(tags), sample=sample,
                  size=size, hole=hole, backdrop=backdrop, thumb_at=thumb_at, crf=crf)


# ---------------------------------------------------------------- shapes and holes

def circle_hole(rf=0.40):
    def hole(w, h):
        p = Pen(w, h)
        p.circle(w / 2, h / 2, rf * min(w, h))
        return p.cov()
    return hole


def rect_hole(box, r):
    """box = (x0, y0, x1, y1) in pixels of the frame's own canvas."""
    def hole(w, h):
        p = Pen(w, h)
        p.rrect(box, r)
        return p.cov()
    return hole


def chamfer_pts(box, cut):
    x0, y0, x1, y1 = box
    return [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1),
            (x0, y1 - cut), (x0, y0 + cut)]


def poly_hole(pts):
    def hole(w, h):
        p = Pen(w, h)
        p.poly(pts)
        return p.cov()
    return hole


def hex_pts(cx, cy, R):
    return [(cx + R * math.cos(-math.pi / 2 + k * TAU / 6), cy + R * math.sin(-math.pi / 2 + k * TAU / 6))
            for k in range(6)]


def cut(c: Canvas, hole):
    keep = 1 - np.clip(hole, 0, 1)
    c.rgb *= keep[..., None]
    c.a *= keep


def band(w, h, outer, inner):
    """Coverage between two shapes drawn by callables on a Pen."""
    p = Pen(w, h)
    outer(p)
    inner(p, 0)
    return p.cov()


def angle_field(w, h, cx=None, cy=None):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    return (np.arctan2(yy - cy, xx - cx) / TAU) % 1.0


def palette(stops, u):
    """Colours along a cyclic ramp: stops are hex strings, u in 0-1 (any shape)."""
    pal = np.array([hexc(c) for c in stops] + [hexc(stops[0])], np.float32)
    idx = (u % 1.0) * (len(pal) - 1)
    lo = np.floor(idx).astype(int)
    f = (idx - lo)[..., None]
    return pal[lo] * (1 - f) + pal[np.minimum(lo + 1, len(pal) - 1)] * f


def stroke_poly(w, h, pts, width, closed=True):
    p = Pen(w, h)
    p.line(pts + ([pts[0], pts[1]] if closed else []), width)
    return p.cov()


def perimeter(pts, n=400):
    """Evenly spaced points along a closed polygon."""
    pts = pts + [pts[0]]
    seg_l = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg_l)
    out = []
    for i in range(n):
        d = total * i / n
        for (a, b), L in zip(zip(pts, pts[1:]), seg_l):
            if d <= L:
                f = d / L
                out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                break
            d -= L
    return out


def neon(c: Canvas, cov, color, k=1.0, wide=26.0, near=8.0):
    c.fill(color, np.clip(blur(cov, wide) * 2.4, 0, 1) * 0.8 * k)
    c.fill(color, np.clip(blur(cov, near) * 1.8, 0, 1) * k)
    c.fill(mix(color, WHITE, 0.7), cov * min(k * 1.1, 1))


# ================================================================ round frames (1080 x 1080)

R0 = 0.40 * 1080


def _ring(w, h, r_in, r_out):
    p = Pen(w, h)
    p.circle(w / 2, h / 2, r_out)
    p.circle(w / 2, h / 2, r_in, 0)
    return p.cov()


@cam("facecam-circulo-neon", "Círculo de neón", "Neon circle cam frame", 4, SQ, circle_hole(),
     tags=["circulo", "neon", "redondo", "round"], sample="portrait-04.jpg", backdrop="h-gaming-03.jpg")
def _circle_neon(w, h, T, rng):
    hole = circle_hole()(w, h)
    ring = _ring(w, h, R0 - 2, R0 + 12)
    ang = angle_field(w, h)
    g1, g2 = blur(ring, 30), blur(ring, 9)

    def frame(t):
        u = t / T
        col = palette(["#00e5ff", "#7a5cff", "#ff2fd0", "#7a5cff"], ang - u).astype(np.float32)
        c = Canvas(w, h)
        c.layer(col, np.clip(g1 * 2.4, 0, 1) * 0.85)
        c.layer(col, np.clip(g2 * 1.8, 0, 1))
        c.layer(np.clip(col * 0.35 + 0.65, 0, 1).astype(np.float32), ring)
        cut(c, hole)
        return c
    return frame


@cam("facecam-circulo-blanco", "Círculo blanco", "White circle cam frame", 2, SQ, circle_hole(),
     tags=["circulo", "blanco", "minimal", "simple", "podcast"], sample="man-01.jpg", backdrop="h-podcast-02.jpg")
def _circle_white(w, h, T, rng):
    hole = circle_hole()(w, h)
    ring = _ring(w, h, R0 - 2, R0 + 16)
    art = Art(w, h)
    art.shadow(ring, 0, 8, 14, 0.45)
    art.vgrad(ring, WHITE, hexc("#e6e8ee"))
    cut(art, hole)
    return lambda t: art


@cam("facecam-circulo-degradado", "Círculo degradado", "Gradient ring cam frame", 4, SQ, circle_hole(0.385),
     tags=["circulo", "degradado", "gradient", "historia", "aesthetic"], sample="portrait-02.jpg",
     backdrop="h-portrait-01.jpg")
def _circle_grad(w, h, T, rng):
    r = 0.385 * w
    hole = circle_hole(0.385)(w, h)
    white = _ring(w, h, r - 2, r + 12)
    ring = _ring(w, h, r + 18, r + 46)
    ang = angle_field(w, h)

    def frame(t):
        u = t / T
        col = palette(["#ffb347", "#ff5f6d", "#d63c9b", "#7b4dff", "#ff5f6d"], ang + 0.25 - u).astype(np.float32)
        c = Canvas(w, h)
        c.fill((0, 0, 0), shift(blur(np.maximum(ring, white), 12), 0, 8) * 0.35)
        c.layer(col, ring)
        c.fill(WHITE, white)
        cut(c, hole)
        return c
    return frame


@cam("facecam-circulo-ondas", "Círculo que habla", "Speaking pulse cam frame", 2, SQ, circle_hole(0.37),
     tags=["circulo", "ondas", "voz", "hablando", "podcast", "pulso"], sample="h-portrait-04.jpg",
     backdrop="h-podcast-01.jpg")
def _circle_waves(w, h, T, rng):
    r = 0.37 * w
    hole = circle_hole(0.37)(w, h)
    ring = _ring(w, h, r - 2, r + 12)
    teal = hexc("#2ee6a8")

    def frame(t):
        c = Canvas(w, h)
        for k in range(3):
            u = (t / T + k / 3) % 1.0
            rr = r + 12 + u * 120
            c.fill(teal, _ring(w, h, rr, rr + 6 + 10 * (1 - u)) * (1 - u) ** 1.6 * 0.8)
        c.fill(teal, np.clip(blur(ring, 14) * 1.6, 0, 1) * 0.6)
        c.fill(WHITE, ring)
        c.fill(teal, ring * 0.25)
        cut(c, hole)
        return c
    return frame


def _live_badge(text, s=1.0):
    th = 46 * s
    tw = text_width(text, "Montserrat-Black.ttf", th)
    bw, bh = tw + 110 * s, 84 * s
    pad = 30 * s
    art = Art(bw + 2 * pad, bh + 2 * pad)
    p = art.pen(1, pad, pad)
    p.rrect((0, 0, bw, bh), 18 * s)
    cov = p.cov()
    art.shadow(cov, 0, 8 * s, 12 * s, 0.4)
    art.vgrad(cov, hexc("#ff3b4a"), hexc("#d4001c"), pad, pad + bh)
    o = art.pen(1, pad, pad)
    o.rrect_line((0, 0, bw, bh), 18 * s, 5 * s)
    art.paint(o.cov(), WHITE)
    tp = art.pen(1, pad, pad)
    tp.text((bw / 2 + 24 * s, bh / 2 + 2 * s), text, "Montserrat-Black.ttf", th)
    art.paint(tp.cov(), WHITE)
    return art.sprite(), (pad + 42 * s, pad + bh / 2)


def _live(text):
    def make(w, h, T, rng):
        hole = circle_hole()(w, h)
        ring = _ring(w, h, R0 - 2, R0 + 16)
        red = hexc("#ff2a3d")
        badge, dot_at = _live_badge(text)
        dot = Art(40, 40)
        dp = dot.pen(1, 20, 20)
        dp.circle(0, 0, 12)
        dot.paint(dp.cov(), WHITE)
        dot = dot.sprite()

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            k = 0.75 + 0.25 * math.cos(TAU * u)
            c.fill(red, np.clip(blur(ring, 22) * 2.0, 0, 1) * 0.7 * k)
            c.fill(WHITE, ring)
            c.fill(red, ring * 0.55)
            cut(c, hole)
            bx, by = w / 2, h / 2 + R0 + 4
            put(c, badge, bx, by)
            put(c, dot, bx - badge.w / 2 + dot_at[0], by - badge.h / 2 + dot_at[1], opacity=0.35 + 0.65 * k,
                scale=0.8 + 0.2 * k)
            return c
        return frame
    return make


cam("facecam-en-vivo-es", "En vivo con círculo (español)", "Live circle cam frame (Spanish)", 2, SQ, circle_hole(),
    tags=["en vivo", "directo", "live", "transmision", "español"], sample="portrait-06.jpg",
    backdrop="h-gaming-02.jpg")(_live("EN VIVO"))
cam("facecam-live-en", "Live con círculo (inglés)", "Live circle cam frame (English)", 2, SQ, circle_hole(),
    tags=["live", "en vivo", "stream", "english", "ingles"], sample="man-04.jpg",
    backdrop="h-gaming-05.jpg")(_live("LIVE"))


@cam("facecam-circulo-dorado", "Círculo dorado", "Gold ring cam frame", 3, SQ, circle_hole(0.39),
     tags=["circulo", "dorado", "gold", "elegante", "podcast", "premium"], sample="portrait-03.jpg",
     backdrop="h-podcast-04.jpg")
def _circle_gold(w, h, T, rng):
    r = 0.39 * w
    hole = circle_hole(0.39)(w, h)
    ring = _ring(w, h, r - 2, r + 36)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2)
    across = np.clip((d - r) / 36, 0, 1)
    ang = angle_field(w, h)
    bevel = 0.55 + 0.45 * np.cos((across - 0.4) * math.pi * 1.2)
    metal = 0.75 + 0.25 * np.cos(ang * TAU * 3 + 0.6)
    base = np.array(hexc("#c8932e"), np.float32)
    hi = np.array(hexc("#fff1b8"), np.float32)
    lines = _ring(w, h, r - 2, r + 1.5) + _ring(w, h, r + 34.5, r + 38)

    def frame(t):
        u = t / T
        da = np.abs(((ang - u + 0.5) % 1.0) - 0.5)
        sheen = np.exp(-(da / 0.05) ** 2)
        v = np.clip(bevel * metal * 0.85 + sheen * 0.6, 0, 1.4)[..., None]
        col = np.clip(base * v + hi * np.clip(v - 0.85, 0, 1) * 1.6, 0, 1).astype(np.float32)
        c = Canvas(w, h)
        c.fill((0, 0, 0), shift(blur(ring, 14), 0, 10) * 0.45)
        c.layer(col, ring)
        c.fill(hexc("#6b4a12"), np.clip(lines, 0, 1) * 0.6)
        cut(c, hole)
        return c
    return frame


@cam("facecam-burbuja", "Burbuja de diálogo", "Speech bubble cam frame", 2, SQ, circle_hole(0.37),
     tags=["burbuja", "dialogo", "speech bubble", "comic", "blanco", "habla"], sample="selfie-01.jpg",
     backdrop="h-desk-03.jpg")
def _bubble(w, h, T, rng):
    r = 0.37 * w
    hole = circle_hole(0.37)(w, h)
    p = Pen(w, h)
    p.circle(w / 2, h / 2, r + 26)
    a = math.radians(128)
    bx, by = w / 2 + (r + 10) * math.cos(a), h / 2 + (r + 10) * math.sin(a)
    tip = (w / 2 + (r + 150) * math.cos(a + 0.12), h / 2 + (r + 150) * math.sin(a + 0.12))
    p.poly([(bx - 60, by - 30), tip, (bx + 50, by + 40)])
    shape = p.cov()
    art = Art(w, h)
    art.shadow(shape, 0, 10, 16, 0.45)
    art.vgrad(shape, WHITE, hexc("#eceef3"))
    o = Pen(w, h)
    o.circle(w / 2, h / 2, r + 2)
    art.paint(o.cov(), hexc("#1d1d22"), 0.9)

    def frame(t):
        c = Canvas(w, h)
        c.merge(art)
        cut(c, hole)
        return c
    return frame


HR = 0.42 * 1080


@cam("facecam-hexagono-neon", "Hexágono de neón", "Neon hexagon cam frame", 3, SQ,
     poly_hole(hex_pts(540, 540, HR)), tags=["hexagono", "hexagon", "neon", "verde", "gamer"], sample="selfie-03.jpg",
     backdrop="h-gaming-04.jpg")
def _hex_neon(w, h, T, rng):
    hole = poly_hole(hex_pts(w / 2, h / 2, HR))(w, h)
    pts = hex_pts(w / 2, h / 2, HR + 8)
    line = stroke_poly(w, h, pts, 12)
    path = perimeter(pts, 360)
    col = hexc("#39ff8a")

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        neon(c, line, col, 0.85 + 0.15 * math.sin(TAU * 2 * u))
        for k in range(2):
            i0 = int(((u + k * 0.5) % 1.0) * len(path))
            run = [path[(i0 + j) % len(path)] for j in range(45)]
            p = Pen(w, h, ss=2)
            p.line(run, 14)
            rc = p.cov()
            c.fill(WHITE, np.clip(blur(rc, 18) * 2, 0, 1) * 0.6)
            c.fill(WHITE, rc)
        cut(c, hole)
        return c
    return frame


@cam("facecam-hexagono-tech", "Hexágono tecnológico", "Tech hexagon cam frame", 4, SQ,
     poly_hole(hex_pts(540, 540, 0.4 * 1080)),
     tags=["hexagono", "tech", "hud", "futurista", "metal", "gamer", "sci-fi"], sample="h-portrait-01.jpg",
     backdrop="h-tech-02.jpg")
def _hex_tech(w, h, T, rng):
    R = 0.4 * w
    hole = poly_hole(hex_pts(w / 2, h / 2, R))(w, h)
    p = Pen(w, h)
    p.poly(hex_pts(w / 2, h / 2, R + 34))
    p.poly(hex_pts(w / 2, h / 2, R - 2), 0)
    body = p.cov()
    art = Art(w, h)
    art.shadow(body, 0, 10, 16, 0.5)
    art.lgrad(body, hexc("#5a6270"), hexc("#1a1d24"), (0, 0), (w, h))
    art.paint(stroke_poly(w, h, hex_pts(w / 2, h / 2, R + 6), 4), hexc("#2fd8ff"))
    art.paint(stroke_poly(w, h, hex_pts(w / 2, h / 2, R + 33), 2.5), WHITE, 0.25)
    cyan = hexc("#2fd8ff")
    Ro = R + 70

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.merge(art)
        q = Pen(w, h, ss=2)
        for k in range(3):
            a0 = TAU * (u + k / 3)
            pts = [(w / 2 + Ro * math.cos(a), h / 2 + Ro * math.sin(a)) for a in np.linspace(a0, a0 + 0.9, 40)]
            q.line(pts, 7)
        for k in range(3):
            a0 = -TAU * (u + k / 3) + 0.5
            pts = [(w / 2 + (Ro + 26) * math.cos(a), h / 2 + (Ro + 26) * math.sin(a))
                   for a in np.linspace(a0, a0 + 0.35, 20)]
            q.line(pts, 3)
        arcs = q.cov()
        neon(c, arcs, cyan, 0.9, 16, 5)
        cut(c, hole)
        return c
    return frame


SQB = (100, 100, 980, 980)


@cam("facecam-cuadrado", "Cuadrado redondeado", "Rounded square cam frame", 2, SQ, rect_hole(SQB, 130),
     tags=["cuadrado", "square", "redondeado", "minimal", "blanco", "podcast"], sample="h-portrait-05.jpg",
     backdrop="h-podcast-03.jpg")
def _square(w, h, T, rng):
    hole = rect_hole(SQB, 130)(w, h)
    p = Pen(w, h)
    x0, y0, x1, y1 = SQB
    p.rrect((x0 - 20, y0 - 20, x1 + 20, y1 + 20), 150)
    p.rrect(SQB, 130, 0)
    b = p.cov()
    art = Art(w, h)
    art.shadow(b, 0, 10, 18, 0.45)
    art.vgrad(b, WHITE, hexc("#e4e6ec"))
    cut(art, hole)
    return lambda t: art


# ================================================================ 16:9 frames

WB = (56, 56, 1224, 664)


@cam("facecam-gamer-neon", "Gamer neón", "Neon gamer cam frame", 3, WIDE,
     poly_hole(chamfer_pts(WB, 48)), tags=["gamer", "neon", "rosa", "cian", "twitch"], sample="h-portrait-05.jpg",
     backdrop="h-gaming-01.jpg")
def _gamer_neon(w, h, T, rng):
    hole = poly_hole(chamfer_pts(WB, 48))(w, h)
    inner = stroke_poly(w, h, chamfer_pts((52, 52, 1228, 668), 50), 8)
    outer = stroke_poly(w, h, chamfer_pts((34, 34, 1246, 686), 60), 5)
    path = perimeter(chamfer_pts((34, 34, 1246, 686), 60), 500)
    mag, cy_ = hexc("#ff2fd0"), hexc("#21e6ff")

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        neon(c, inner, cy_, 0.9 + 0.1 * math.sin(TAU * 3 * u), 20, 6)
        neon(c, outer, mag, 0.9 + 0.1 * math.cos(TAU * 3 * u), 20, 6)
        i0 = int(u * len(path))
        for k in (0, len(path) // 2):
            run = [path[(i0 + k + j) % len(path)] for j in range(70)]
            p = Pen(w, h, ss=2)
            p.line(run, 9)
            rc = p.cov()
            c.fill(WHITE, np.clip(blur(rc, 14) * 2, 0, 1) * 0.7)
            c.fill(WHITE, rc)
        cut(c, hole)
        return c
    return frame


@cam("facecam-gamer-rgb", "Gamer RGB", "RGB gamer cam frame", 3, WIDE, rect_hole(WB, 34),
     tags=["gamer", "rgb", "arcoiris", "rainbow", "luces", "pc"], sample="h-portrait-04.jpg",
     backdrop="h-gaming-04.jpg")
def _gamer_rgb(w, h, T, rng):
    hole = rect_hole(WB, 34)(w, h)
    p = Pen(w, h)
    p.rrect((40, 40, 1240, 680), 48)
    p.rrect(WB, 34, 0)
    ring = p.cov()
    ang = angle_field(w, h)
    g = blur(ring, 22)

    def frame(t):
        u = t / T
        col = np.stack([0.5 + 0.5 * np.cos(TAU * (ang - u) + k * TAU / 3) for k in range(3)], -1)
        col = np.clip(col * 1.15, 0, 1).astype(np.float32)
        c = Canvas(w, h)
        c.layer(col, np.clip(g * 2.2, 0, 1) * 0.8)
        c.layer(np.clip(col * 0.6 + 0.4, 0, 1).astype(np.float32), ring)
        cut(c, hole)
        return c
    return frame


@cam("facecam-glitch", "Glitch", "Glitch cam frame", 2, WIDE, rect_hole(WB, 20),
     tags=["glitch", "error", "rgb", "digital", "gamer", "tech"], sample="h-portrait-03.jpg",
     backdrop="h-gaming-02.jpg")
def _glitch(w, h, T, rng):
    hole = rect_hole(WB, 20)(w, h)
    p = Pen(w, h)
    p.rrect((44, 44, 1236, 676), 28)
    p.rrect(WB, 20, 0)
    ring = p.cov()
    n = int(T * 30)
    r = np.random.default_rng(7)
    events = []
    for i in range(n):
        g = r.random() < 0.22 or (i % 20) in (0, 1)
        events.append((g, r.integers(-26, 27), r.integers(0, h - 80, 4), r.integers(20, 90, 4),
                       r.integers(-60, 61, 4)))

    def frame(t):
        g, off, ys, hs, dx = events[int(round(t * 30)) % n]
        c = Canvas(w, h)
        base = ring
        if g:
            base = ring.copy()
            for y, hh, d in zip(ys, hs, dx):
                base[y:y + hh] = np.roll(ring[y:y + hh], int(d), axis=1)
            c.fill(hexc("#ff1f4b"), np.roll(base, int(off), axis=1) * 0.9)
            c.fill(hexc("#1ff4ff"), np.roll(base, -int(off), axis=1) * 0.9)
        c.fill(WHITE, base)
        cut(c, hole)
        return c
    return frame


@cam("facecam-minimal", "Minimalista", "Minimal cam frame", 2, WIDE, rect_hole((40, 40, 1240, 680), 30),
     tags=["minimal", "simple", "blanco", "limpio", "podcast"], sample="h-portrait-01.jpg",
     backdrop="h-podcast-02.jpg")
def _minimal(w, h, T, rng):
    box = (40, 40, 1240, 680)
    p = Pen(w, h)
    p.rrect((32, 32, 1248, 688), 38)
    p.rrect(box, 30, 0)
    ring = p.cov()
    art = Art(w, h)
    art.shadow(ring, 0, 6, 10, 0.45)
    art.paint(ring, WHITE, 0.95)
    cut(art, rect_hole(box, 30)(w, h))
    return lambda t: art


@cam("facecam-esquinas", "Esquinas", "Corner brackets cam frame", 2, WIDE, rect_hole((60, 60, 1220, 660), 12),
     tags=["esquinas", "corners", "visor", "hud", "minimal"], sample="h-portrait-06.jpg",
     backdrop="h-gaming-05.jpg")
def _corners(w, h, T, rng):
    hole = rect_hole((60, 60, 1220, 660), 12)(w, h)
    thin = Pen(w, h)
    thin.rrect_line((60, 60, 1220, 660), 12, 3)
    thin = thin.cov()

    def frame(t):
        u = t / T
        gap = 16 + 7 * math.sin(TAU * u)
        L = 120
        p = Pen(w, h, ss=2)
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x = w / 2 + sx * (580 + gap)
            y = h / 2 + sy * (300 + gap)
            p.line([(x, y - sy * L), (x, y), (x - sx * L, y)], 10)
        cov = p.cov()
        c = Canvas(w, h)
        c.fill((0, 0, 0), shift(blur(cov, 6), 0, 4) * 0.45)
        c.fill(WHITE, cov)
        c.fill(WHITE, thin * 0.35)
        cut(c, hole)
        return c
    return frame


@cam("facecam-madera", "Marco de madera", "Wooden cam frame", 2, WIDE, rect_hole((64, 64, 1216, 656), 6),
     tags=["madera", "wood", "podcast", "rustico", "estudio", "calido"], sample="h-portrait-02.jpg",
     backdrop="h-podcast-01.jpg")
def _wood(w, h, T, rng):
    box = (64, 64, 1216, 656)
    hole = rect_hole(box, 6)(w, h)
    p = Pen(w, h)
    p.rrect((8, 8, w - 8, h - 8), 14)
    p.rrect(box, 6, 0)
    frame_c = p.cov()
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d_top, d_bot, d_l, d_r = yy, h - yy, xx, w - xx
    horiz = np.minimum(d_top, d_bot) < np.minimum(d_l, d_r)
    n1 = fx.sample_tile(fx.tile_noise(512, 21, falloff=2.0), w, h, 0, 0, 0.5)
    n2 = fx.sample_tile(fx.tile_noise(512, 22, falloff=1.4), w, h, 0, 0, 1.0)
    along = np.where(horiz, yy, xx)
    grain = 0.5 + 0.5 * np.sin(along / 3.2 + n1 * 26 + n2 * 3)
    grain = grain ** 2.2
    dark, mid, light = (np.array(hexc(c), np.float32) for c in ("#5a3518", "#9a6334", "#c58e57"))
    col = mid * (1 - grain[..., None] * 0.45) + dark * grain[..., None] * 0.45
    col = col + (light - mid) * (n2[..., None] - 0.5) * 0.6
    edge_in = np.minimum.reduce([np.abs(yy - 64), np.abs(yy - 656), np.abs(xx - 64), np.abs(xx - 1216)])
    bevel = np.clip(1 - edge_in / 10, 0, 1)
    art = Art(w, h)
    art.shadow(frame_c, 0, 8, 12, 0.5)
    art.layer(np.clip(col, 0, 1).astype(np.float32), frame_c)
    art.paint(frame_c * bevel * (yy < h / 2) * (xx > 50) * (xx < w - 50), (0, 0, 0), 0.35)
    art.paint(frame_c * bevel * (yy > h / 2) * (xx > 50) * (xx < w - 50), hexc("#f0c08a"), 0.3)
    hi = Pen(w, h)
    hi.rrect_line((10, 10, w - 10, h - 10), 14, 3)
    art.paint(hi.cov(), hexc("#e8b07a"), 0.5)
    for sx, sy in ((36, 36), (w - 36, 36), (w - 36, h - 36), (36, h - 36)):
        sp = Pen(w, h)
        sp.circle(sx, sy, 11)
        sc = sp.cov()
        art.shadow(sc, 1, 2, 2, 0.5)
        art.rgrad(sc, sx - 4, sy - 4, 15, [(0, hexc("#f2f2f2")), (1, hexc("#8a8a8a"))])
        sl = Pen(w, h)
        sl.line([(sx - 7, sy + 4), (sx + 7, sy - 4)], 2.6)
        art.paint(sl.cov(), hexc("#4a4a4a"), 0.9)
    cut(art, hole)
    return lambda t: art


STUDIO = (1280, 820)
SB = (40, 40, 1240, 715)


@cam("facecam-estudio", "Estudio de podcast", "Podcast studio cam frame", 2, STUDIO, rect_hole(SB, 22),
     tags=["podcast", "estudio", "microfono", "mic", "ecualizador", "radio", "audio"], sample="h-podcast-04.jpg",
     backdrop="h-podcast-03.jpg")
def _studio(w, h, T, rng):
    hole = rect_hole(SB, 22)(w, h)
    p = Pen(w, h)
    p.rrect((12, 12, w - 12, h - 12), 40)
    body = p.cov()
    art = Art(w, h)
    art.shadow(body, 0, 10, 16, 0.5)
    art.vgrad(body, hexc("#2c2c33"), hexc("#141418"))
    o = Pen(w, h)
    o.rrect_line(SB, 22, 4)
    art.paint(o.cov(), hexc("#ff4d5e"), 0.9)
    mp = Pen(w, h)
    mx, my = 82, 768
    mp.rrect((mx - 12, my - 30, mx + 12, my + 6), 12)
    mp.line([(mx - 22, my - 6), (mx - 22, my + 2), (mx, my + 20), (mx + 22, my + 2), (mx + 22, my - 6)], 4,
            caps=False)
    mp.line([(mx, my + 20), (mx, my + 30)], 4)
    mp.line([(mx - 12, my + 31), (mx + 12, my + 31)], 4)
    art.paint(mp.cov(), WHITE)
    dot = Pen(w, h)
    dot.circle(w - 70, 767, 10)
    dc = dot.cov()
    bars = 40
    ph = np.random.default_rng(4).uniform(0, TAU, (bars, 2))
    fr = np.random.default_rng(5).integers(1, 4, (bars, 2))

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.merge(art)
        q = Pen(w, h, ss=2)
        x0, x1 = 140, w - 120
        for i in range(bars):
            x = x0 + (x1 - x0) * (i + 0.5) / bars
            env = math.sin(math.pi * (i + 0.5) / bars) ** 0.6
            v = 0.15 + 0.85 * env * (0.5 + 0.25 * math.sin(TAU * fr[i, 0] * u + ph[i, 0])
                                     + 0.25 * math.sin(TAU * fr[i, 1] * 2 * u + ph[i, 1])) ** 1.5
            hh = 6 + 52 * v
            q.line([(x, 767 - hh / 2), (x, 767 + hh / 2)], 8)
        eq = q.cov()
        c.layer(palette(["#ff4d5e", "#ff9a3d", "#ff4d5e"], np.linspace(0, 0.5, w)[None, :] * np.ones((h, 1)))
                .astype(np.float32), eq)
        c.fill(hexc("#ff2a3d"), dc * (0.4 + 0.6 * (0.5 + 0.5 * math.cos(TAU * u))))
        cut(c, hole)
        return c
    return frame


PLATE = (1280, 880)
PB = (40, 40, 1240, 715)


@cam("facecam-placa-nombre", "Con placa para tu nombre", "Name plate cam frame", 2, PLATE, rect_hole(PB, 26),
     tags=["nombre", "name", "placa", "plate", "tercio inferior", "lower third", "podcast", "entrevista"],
     sample="h-portrait-05.jpg", backdrop="h-podcast-02.jpg")
def _plate(w, h, T, rng):
    hole = rect_hole(PB, 26)(w, h)
    p = Pen(w, h)
    p.rrect((28, 28, 1252, 727), 36)
    p.rrect(PB, 26, 0)
    ring = p.cov()
    art = Art(w, h)
    art.shadow(ring, 0, 8, 14, 0.45)
    art.vgrad(ring, WHITE, hexc("#e6e8ee"))
    pl = Pen(w, h)
    pl.rrect((28, 752, 760, 852), 22)
    pc = pl.cov()
    art.shadow(pc, 0, 8, 14, 0.45)
    art.lgrad(pc, hexc("#ff4655"), hexc("#c3001b"), (28, 752), (760, 852))
    ac = Pen(w, h)
    ac.rrect((28, 752, 54, 852), 13)
    art.paint(ac.cov() * pc, hexc("#ffd23f"))
    gl = Pen(w, h)
    gl.rrect((34, 756, 754, 800), 18)
    art.gloss(gl.cov() * pc, 752, 805, 0.18)
    cut(art, hole)
    return lambda t: art


CYB = chamfer_pts((70, 60, 1210, 660), 36)


@cam("facecam-cyber", "Cyber HUD", "Cyber HUD cam frame", 3, WIDE, poly_hole(CYB),
     tags=["cyber", "hud", "futurista", "sci-fi", "tech", "cian", "gamer"], sample="h-portrait-03.jpg",
     backdrop="h-tech-03.jpg")
def _cyber(w, h, T, rng):
    hole = poly_hole(CYB)(w, h)
    cyan = hexc("#26f0ff")
    base = Pen(w, h)
    base.line(CYB + [CYB[0], CYB[1]], 4)
    for x0, x1, y in ((440, 840, 52), (440, 840, 668)):
        base.poly([(x0, y - 6), (x1, y - 6), (x1 - 18, y + 6), (x0 + 18, y + 6)] if y < 100 else
                  [(x0 + 18, y - 6), (x1 - 18, y - 6), (x1, y + 6), (x0, y + 6)])
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        cx, cy = w / 2 + sx * 612, h / 2 + sy * 322
        base.line([(cx, cy - sy * 60), (cx, cy), (cx - sx * 60, cy)], 5)
    for i in range(12):
        y = 160 + i * 34
        base.line([(36, y), (36 + (16 if i % 3 == 0 else 8), y)], 3)
        base.line([(w - 36, y), (w - 36 - (16 if i % 3 == 0 else 8), y)], 3)
    bc = base.cov()
    top_path = perimeter(CYB, 600)

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        neon(c, bc, cyan, 0.85, 14, 4)
        i0 = int(u * len(top_path))
        run = [top_path[(i0 + j) % len(top_path)] for j in range(90)]
        p = Pen(w, h, ss=2)
        p.line(run, 6)
        neon(c, p.cov(), WHITE, 1.0, 12, 4)
        q = Pen(w, h, ss=2)
        for k, (x, y) in enumerate(((112, 30), (140, 30), (168, 30), (w - 112, h - 30), (w - 140, h - 30))):
            if (int(u * 6) + k) % 3:
                q.rect((x - 8, y - 8, x + 8, y + 8))
        c.fill(cyan, q.cov())
        cut(c, hole)
        return c
    return frame


TV = (1280, 860)
TVB = (70, 60, 1210, 701)


@cam("facecam-tv-retro", "Televisor retro", "Retro TV cam frame", 2, TV, rect_hole(TVB, 70),
     tags=["tv", "televisor", "retro", "vintage", "antiguo", "tele", "podcast"], sample="h-portrait-06.jpg",
     backdrop="h-interior-02.jpg")
def _tv(w, h, T, rng):
    hole = rect_hole(TVB, 70)(w, h)
    p = Pen(w, h)
    p.rrect((12, 12, w - 12, h - 12), 60)
    body = p.cov()
    art = Art(w, h)
    art.shadow(body, 0, 12, 18, 0.5)
    art.vgrad(body, hexc("#f1e6cf"), hexc("#d2bf9a"))
    b = Pen(w, h)
    x0, y0, x1, y1 = TVB
    b.rrect((x0 - 26, y0 - 26, x1 + 26, y1 + 26), 90)
    bez = b.cov()
    art.vgrad(bez, hexc("#3a3632"), hexc("#1d1b19"))
    gl = Pen(w, h)
    gl.rrect((x0 - 26, y0 - 26, x1 + 26, y0 + 40), 90)
    art.paint(gl.cov() * bez, WHITE, 0.08)
    for i in range(14):
        g = Pen(w, h)
        g.rrect((90 + i * 34, 744, 108 + i * 34, 818), 9)
        art.paint(g.cov(), hexc("#7a6a52"), 0.75)
    for kx in (1010, 1130):
        k = Pen(w, h)
        k.circle(kx, 781, 40)
        kc = k.cov()
        art.shadow(kc, 0, 4, 6, 0.5)
        art.rgrad(kc, kx - 12, 768, 52, [(0, hexc("#6b625a")), (1, hexc("#2a2622"))])
        m = Pen(w, h)
        m.line([(kx, 781), (kx + 22, 762)], 7)
        art.paint(m.cov(), hexc("#e8dcc4"))
    led = Pen(w, h)
    led.circle(900, 781, 9)
    art.paint(led.cov(), hexc("#ff3a2a"))
    cut(art, hole)
    return lambda t: art


@cam("facecam-comic", "Cómic pop", "Pop comic cam frame", 2, WIDE, rect_hole((60, 50, 1190, 650), 14),
     tags=["comic", "pop art", "historieta", "amarillo", "divertido"], sample="h-portrait-04.jpg",
     backdrop="h-kids-02.jpg")
def _comic(w, h, T, rng):
    box = (60, 50, 1190, 650)
    hole = rect_hole(box, 14)(w, h)
    sh = Pen(w, h)
    sh.rrect((86, 80, 1250, 694), 20)
    shc = sh.cov()
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cell = 16
    dx = (xx % cell) - cell / 2
    dy = (yy % cell) - cell / 2
    dots = np.clip(5.5 - np.sqrt(dx * dx + dy * dy) + 0.5, 0, 1)
    art = Art(w, h)
    art.paint(shc, hexc("#ffd400"))
    art.paint(shc * dots, hexc("#ff3d6e"), 0.9)
    out = Pen(w, h)
    out.rrect_line((86, 80, 1250, 694), 20, 8)
    art.paint(out.cov(), hexc("#111111"))
    fr = Pen(w, h)
    fr.rrect((48, 38, 1202, 662), 22)
    fr.rrect(box, 14, 0)
    fc = fr.cov()
    art.paint(fc, hexc("#111111"))
    cut(art, hole)
    return lambda t: art


@cam("facecam-pastel", "Pastel con corazones", "Pastel hearts cam frame", 2, WIDE, rect_hole((70, 70, 1210, 650), 40),
     tags=["pastel", "rosa", "lindo", "cute", "kawaii", "corazones", "aesthetic"], sample="h-portrait-02.jpg",
     backdrop="h-desk-03.jpg")
def _pastel(w, h, T, rng):
    box = (70, 70, 1210, 650)
    hole = rect_hole(box, 40)(w, h)
    p = Pen(w, h)
    p.rrect((24, 24, w - 24, h - 24), 70)
    p.rrect(box, 40, 0)
    ring = p.cov()
    art = Art(w, h)
    art.shadow(ring, 0, 8, 14, 0.35)
    art.lgrad(ring, hexc("#ffc2dc"), hexc("#c9b8ff"), (0, 0), (w, h))
    route = perimeter([(47, 47), (w - 47, 47), (w - 47, h - 47), (47, h - 47)], 300)
    st = Pen(w, h)
    for i in range(0, len(route), 2):
        a, b = route[i], route[(i + 1) % len(route)]
        st.line([a, (lerp(a[0], b[0], 0.6), lerp(a[1], b[1], 0.6))], 3.5)
    art.paint(st.cov() * ring, WHITE, 0.85)
    hearts = []
    for (x, y, r, col) in ((40, 40, 46, "#ff5d8f"), (w - 40, 40, 38, "#ff8fb1"), (w - 44, h - 44, 48, "#ff5d8f"),
                           (44, h - 44, 36, "#ff8fb1")):
        a = Art(r * 2.6, r * 2.6)
        hp = a.pen(r * 2 / 100, r * 0.3, r * 0.3)
        icon_heart(hp)
        hc = hp.cov()
        a.shadow(hc, 0, 3, 4, 0.3)
        a.paint(grow(hc, 4), WHITE)
        a.vgrad(hc, mix(hexc(col), WHITE, 0.2), hexc(col))
        hearts.append((a.sprite(), x, y))

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.merge(art)
        cut(c, hole)
        for i, (spr, x, y) in enumerate(hearts):
            k = 1 + 0.12 * max(0.0, math.sin(TAU * (u + i / 4))) ** 2
            put(c, spr, x, y, scale=k, rot=(-12 if i % 2 else 12))
        return c
    return frame


@cam("facecam-rayos", "Rayos eléctricos", "Electric cam frame", 2, WIDE, rect_hole(WB, 18),
     tags=["rayos", "electrico", "lightning", "energia", "azul", "gamer", "poder"], sample="h-portrait-05.jpg",
     backdrop="h-gaming-03.jpg")
def _electric(w, h, T, rng):
    hole = rect_hole(WB, 18)(w, h)
    p = Pen(w, h)
    p.rrect((48, 48, 1232, 672), 24)
    p.rrect(WB, 18, 0)
    ring = p.cov()
    path = perimeter([(52, 52), (1228, 52), (1228, 668), (52, 668)], 700)
    n = int(T * 15)
    r = np.random.default_rng(11)
    plans = []
    for i in range(n):
        bolts = []
        for _ in range(4):
            i0 = int(r.integers(0, len(path)))
            L = int(r.integers(60, 160))
            jit = r.normal(0, 9, L)
            bolts.append((i0, L, jit))
        plans.append(bolts)
    blue = hexc("#4fb8ff")

    def frame(t):
        bolts = plans[int(t * 15) % n]
        q = Pen(w, h, ss=2)
        for i0, L, jit in bolts:
            pts = []
            for j in range(0, L, 4):
                a = path[(i0 + j) % len(path)]
                b = path[(i0 + j + 1) % len(path)]
                nx, ny = -(b[1] - a[1]), b[0] - a[0]
                nl = math.hypot(nx, ny) or 1
                pts.append((a[0] + nx / nl * jit[j], a[1] + ny / nl * jit[j]))
            q.line(pts, 3.5)
        bc = q.cov()
        c = Canvas(w, h)
        neon(c, ring, blue, 0.7, 18, 5)
        neon(c, bc, blue, 1.0, 16, 4)
        cut(c, hole)
        return c
    return frame
