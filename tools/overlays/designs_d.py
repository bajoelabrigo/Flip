"""Fourth batch: hand-drawn doodles (the white-marker trend of Reels and TikTok), frames and textures.

Doodles are polylines in unit coordinates. They draw on over the first `draw` seconds and then
"boil" (redrawn with a slightly different wobble every three frames), like hand animation.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import fx
from fx import TAU, Canvas
from designs import GOLD, PARTY, design, wrap

WHITE = (1, 1, 1)
BLACK = (0.06, 0.06, 0.07)
PINK = fx.hex_rgb("#ff6fb5")
NEON = fx.hex_rgb("#e6ff3a")
GOLDC = fx.hex_rgb("#ffcf4a")


# ---------------------------------------------------------------- shapes (unit coordinates, y down)

def _curve(fn, n=48, closed=False):
    pts = [fn(i / n) for i in range(n + (1 if closed else 0))]
    return pts


def heart():
    def f(u):
        t = u * TAU
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        return (x / 17, (y + 2) / 17)
    return [_curve(f, 56, True)]


def star():
    pts = []
    for i in range(11):
        r = 1.0 if i % 2 == 0 else 0.45
        t = i / 10 * TAU
        pts.append((math.sin(t) * r, -math.cos(t) * r))
    return [pts]


def sparkle():
    pts = []
    for i in range(65):
        t = i / 64 * TAU
        c, s = math.cos(t), math.sin(t)
        pts.append((math.copysign(abs(c) ** 3, c), math.copysign(abs(s) ** 3, s)))
    return [pts]


def arrow(bend=0.4):
    shaft = [(-1 + 2 * u, -bend * math.sin(math.pi * u)) for u in np.linspace(0, 1, 24)]
    tip = shaft[-1]
    a = math.atan2(shaft[-1][1] - shaft[-3][1], shaft[-1][0] - shaft[-3][0])
    head = [(tip[0] - 0.4 * math.cos(a - 0.5), tip[1] - 0.4 * math.sin(a - 0.5)), tip,
            (tip[0] - 0.4 * math.cos(a + 0.5), tip[1] - 0.4 * math.sin(a + 0.5))]
    return [shaft, head]


def crown():
    zig = [(-1, 0.5), (-1, -0.45), (-0.5, 0.05), (0, -0.7), (0.5, 0.05), (1, -0.45), (1, 0.5), (-1, 0.5)]
    dots = [[(x + 0.09 * math.cos(t), y - 0.12 + 0.09 * math.sin(t)) for t in np.linspace(0, TAU, 12)]
            for x, y in ((-1, -0.45), (0, -0.7), (1, -0.45))]
    return [zig] + dots


def smiley():
    face = _curve(lambda u: (math.cos(u * TAU), math.sin(u * TAU)), 48, True)
    eyes = [[(-0.35, -0.35), (-0.35, -0.12)], [(0.35, -0.35), (0.35, -0.12)]]
    mouth = [(0.6 * math.cos(t), 0.15 + 0.45 * math.sin(t)) for t in np.linspace(0.25, math.pi - 0.25, 20)]
    return [face] + eyes + [mouth]


def cloud():
    pts = []
    bumps = [(-0.6, 0.1, 0.4), (-0.15, -0.25, 0.5), (0.4, -0.05, 0.42), (0.75, 0.25, 0.28)]
    for cx, cy, r in bumps:
        pts += [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(math.pi * 0.9, math.pi * 2.1, 12)]
    pts.append((-0.95, 0.45))
    pts.append(pts[0])
    return [pts]


def sun():
    disc = _curve(lambda u: (0.45 * math.cos(u * TAU), 0.45 * math.sin(u * TAU)), 36, True)
    rays = [[(0.65 * math.cos(a), 0.65 * math.sin(a)), (0.98 * math.cos(a), 0.98 * math.sin(a))]
            for a in np.linspace(0, TAU, 9)[:-1]]
    return [disc] + rays


def flower():
    petals = []
    for k in range(5):
        a = k / 5 * TAU
        petals.append([((0.2 + 0.8 * math.sin(v)) * math.cos(a + 0.45 * math.cos(v)),
                        (0.2 + 0.8 * math.sin(v)) * math.sin(a + 0.45 * math.cos(v))) for v in np.linspace(0, math.pi, 14)])
    center = _curve(lambda u: (0.18 * math.cos(u * TAU), 0.18 * math.sin(u * TAU)), 20, True)
    return petals + [center]


def underline():
    return [[(-1 + 2 * u, 0.08 * math.sin(u * 9)) for u in np.linspace(0, 1, 30)],
            [(-0.8 + 1.7 * u, 0.25 + 0.06 * math.sin(u * 7 + 1)) for u in np.linspace(0, 1, 24)]]


def scribble_circle():
    return [[(math.cos(t) * (1 + 0.06 * t), 0.8 * math.sin(t) * (1 + 0.04 * t)) for t in np.linspace(-0.3, TAU * 1.15, 70)]]


def shine():
    return [[(0.35 * math.cos(a), 0.35 * math.sin(a)), (math.cos(a), math.sin(a))]
            for a in (-math.pi * 0.75, -math.pi * 0.5, -math.pi * 0.25)]


def burst():
    return [[(0.55 * math.cos(a), 0.55 * math.sin(a)), (math.cos(a), math.sin(a))] for a in np.linspace(0, TAU, 13)[:-1]]


def butterfly():
    up = [(0.05 + 0.9 * math.sin(v) * math.cos(v * 0.5 - 0.4), -0.9 * math.sin(v) * math.sin(v * 0.9 + 0.3))
          for v in np.linspace(0, math.pi, 20)]
    lo = [(0.05 + 0.6 * math.sin(v) * math.cos(v * 0.5 + 0.6), 0.75 * math.sin(v) * math.sin(v * 0.9 + 0.3))
          for v in np.linspace(0, math.pi, 16)]
    mirror = lambda p: [(-x, y) for x, y in p]
    body = [(0, -0.5), (0, 0.6)]
    ant = [[(0, -0.5), (-0.25, -0.9)], [(0, -0.5), (0.25, -0.9)]]
    return [up, mirror(up), lo, mirror(lo), body] + ant


def note():
    head = _curve(lambda u: (-0.35 + 0.3 * math.cos(u * TAU), 0.6 + 0.22 * math.sin(u * TAU)), 24, True)
    return [head, [(-0.07, 0.6), (-0.07, -0.85)], [(-0.07, -0.85), (0.35, -0.6), (0.4, -0.25)]]


def double_note():
    h1 = _curve(lambda u: (-0.65 + 0.25 * math.cos(u * TAU), 0.65 + 0.18 * math.sin(u * TAU)), 20, True)
    h2 = _curve(lambda u: (0.35 + 0.25 * math.cos(u * TAU), 0.5 + 0.18 * math.sin(u * TAU)), 20, True)
    return [h1, h2, [(-0.42, 0.65), (-0.42, -0.6)], [(0.58, 0.5), (0.58, -0.75)], [(-0.42, -0.6), (0.58, -0.75)],
            [(-0.42, -0.4), (0.58, -0.55)]]


def exclaim():
    return [[(0, -1), (0.05, 0.35)], _curve(lambda u: (0.02 + 0.08 * math.cos(u * TAU), 0.75 + 0.08 * math.sin(u * TAU)),
                                             12, True)]


def question():
    hook = [(0.5 * math.sin(t), -0.45 - 0.45 * math.cos(t)) for t in np.linspace(-1.6, 2.4, 22)] + [(0.0, 0.3)]
    dot = _curve(lambda u: (0.08 * math.cos(u * TAU), 0.72 + 0.08 * math.sin(u * TAU)), 12, True)
    return [hook, dot]


def spiral():
    return [[(t / 18 * math.cos(t), t / 18 * math.sin(t)) for t in np.linspace(0, 18, 80)]]


def bolt():
    return [[(0.15, -1), (-0.45, 0.1), (0.05, 0.1), (-0.2, 1), (0.5, -0.25), (0.0, -0.25), (0.35, -1), (0.15, -1)]]


def wing(side=1):
    """Shoulder at the origin; the top edge sweeps up and out, the lower edge is a row of feather scallops."""
    top = [(side * 0.95 * u, -0.15 - 0.75 * math.sin(u * math.pi * 0.62)) for u in np.linspace(0, 1, 18)]
    tip = top[-1]
    scallops = []
    n = 5
    for k in range(n):
        x0 = tip[0] - side * (0.95 / n) * k * 0.95
        y0 = tip[1] + 0.25 + k * 0.17
        x1 = x0 - side * 0.95 / n
        y1 = y0 + 0.17
        for v in np.linspace(0, math.pi, 8):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            r = math.dist((x0, y0), (x1, y1)) / 2
            ang = math.atan2(y1 - y0, x1 - x0)
            scallops.append((mx + r * math.cos(ang + math.pi - v) + 0.12 * side * math.sin(v),
                             my + r * math.sin(ang + math.pi - v) + 0.12 * math.sin(v)))
    outline = top + [(tip[0], tip[1] + 0.25)] + scallops + [(0, 0.35), (0, -0.15)]
    inner = [[(side * (0.25 + 0.14 * k), -0.05 + 0.08 * k), (side * (0.55 + 0.1 * k), 0.12 + 0.12 * k)] for k in range(3)]
    return [outline] + inner


def halo():
    return [_curve(lambda u: (math.cos(u * TAU), 0.28 * math.sin(u * TAU)), 40, True)]


def horn(side=1):
    return [[(side * 0.0, 0.5), (side * 0.25, -0.2), (side * 0.65, -1.0), (side * 0.6, -0.1), (side * 0.6, 0.5)]]


def tail():
    line = [(-0.9 + 1.5 * u, 0.4 * math.sin(u * 5)) for u in np.linspace(0, 1, 26)]
    tip = line[-1]
    spade = [(tip[0], tip[1] - 0.2), (tip[0] + 0.35, tip[1]), (tip[0], tip[1] + 0.2), (tip[0] + 0.08, tip[1])]
    return [line, spade]


def blob_frame(w, h, s, m=60):
    """A scribbled rectangle just inside the frame, in pixels."""
    pts = []
    corners = [(m, m), (w - m, m), (w - m, h - m), (m, h - m)]
    for lap in range(2):
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            for u in np.linspace(0, 1, 18, endpoint=False):
                pts.append((a[0] + (b[0] - a[0]) * u + lap * 10 * s, a[1] + (b[1] - a[1]) * u + lap * 8 * s))
    pts.append(pts[0])
    return [pts]


SHAPES = dict(heart=heart, star=star, sparkle=sparkle, arrow=arrow, crown=crown, smiley=smiley, cloud=cloud, sun=sun,
              flower=flower, underline=underline, circle=scribble_circle, shine=shine, burst=burst, butterfly=butterfly,
              note=note, notes=double_note, exclaim=exclaim, question=question, spiral=spiral, bolt=bolt, halo=halo,
              wing_l=lambda: wing(-1), wing_r=lambda: wing(1), horn_l=lambda: horn(-1), horn_r=lambda: horn(1), tail=tail,
              arrow_down=lambda: arrow(-0.4))


# ---------------------------------------------------------------- doodle renderer

def _place(polys, x, y, scale, rot):
    c, s_ = math.cos(rot), math.sin(rot)
    return [[(x + (px * c - py * s_) * scale, y + (px * s_ + py * c) * scale) for px, py in p] for p in polys]


def _length(p):
    return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))


def _partial(polys, frac):
    """The first `frac` of the total length of all polylines, in order."""
    total = sum(_length(p) for p in polys)
    left = total * frac
    out = []
    for p in polys:
        if left <= 0:
            break
        q = [p[0]]
        for i in range(len(p) - 1):
            d = math.dist(p[i], p[i + 1])
            if d >= left:
                k = left / d if d else 1
                q.append((p[i][0] + (p[i + 1][0] - p[i][0]) * k, p[i][1] + (p[i + 1][1] - p[i][1]) * k))
                left = 0
                break
            q.append(p[i + 1])
            left -= d
        out.append(q)
    return out


def _wobble(polys, seed, amp):
    r = np.random.default_rng(seed)
    out = []
    for p in polys:
        off = r.normal(0, amp, (2,))
        out.append([(x + off[0] + r.normal(0, amp * 0.5), y + off[1] + r.normal(0, amp * 0.5)) for x, y in p])
    return out


def _stroke(draw, polys, width, ss):
    for p in polys:
        pts = [(x * ss, y * ss) for x, y in p]
        if len(pts) > 1:
            draw.line(pts, fill=255, width=int(width * ss), joint="curve")
        rr = width * ss / 2
        for x, y in (pts[0], pts[-1]):
            draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=255)


def _doodle(items, color=WHITE, width=13, draw=0.9, shadow=True, glow=False, spin=None, fill_alpha=0.0):
    """items: (shape, x, y, size, rotation_deg, delay) in frame fractions / 1080-wide pixels.
    spin: (cx, cy) in fractions: the whole set turns around that point once per loop."""
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        ss = 2
        frames = int(T * 30)

        def frame(t):
            i = int(round(t * 30))
            boil = i // 3
            im = Image.new("L", (w * ss, h * ss), 0)
            d = ImageDraw.Draw(im)
            for k, (shape, x, y, size, rot, delay) in enumerate(items):
                prog = 1.0 if draw <= 0 else min(max((t - delay) / draw, 0), 1)
                if prog <= 0:
                    continue
                base = SHAPES[shape]()
                ang = math.radians(rot)
                cx, cy = x * w, y * h
                if spin:
                    px, py = spin[0] * w, spin[1] * h
                    a = TAU * t / T
                    dx, dy = cx - px, cy - py
                    cx, cy = px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a)
                    ang += a
                polys = _place(base, cx, cy, size * 1.25 * s / 2, ang)
                polys = _wobble(polys, boil * 131 + k * 7, 2.2 * s)
                _stroke(d, _partial(polys, fx.ease_out(prog) if prog < 1 else 1), width * s, ss)
            cov = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255.0
            c = Canvas(w, h)
            if glow:
                g = np.asarray(Image.fromarray((cov * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10 * s)),
                               np.float32) / 255.0
                c.fill(color, np.clip(g * 1.6, 0, 1) * 0.8)
            elif shadow:
                sh = np.roll(np.roll(cov, int(4 * s), 0), int(4 * s), 1)
                c.fill((0, 0, 0), sh * 0.28)
            c.fill(color if not glow else (1, 1, 1), cov)
            if glow:
                c.fill(color, cov * 0.35)
            return c
        return frame
    return make


DOODLE_TAGS = ["garabatos", "doodle", "dibujado a mano", "hand drawn", "aesthetic", "scrapbook", "lindo"]


def doodle(id, es, en, items, *, tags=(), sample="portrait-01.jpg", seconds=4, **kw):
    design(id, es, en, "garabatos", seconds, loop=False, thumb_at=0.9, tags=DOODLE_TAGS + list(tags), sample=sample)(
        _doodle(items, **kw))


HEARTS = [("heart", 0.18, 0.18, 150, -12, 0.0), ("heart", 0.82, 0.22, 110, 14, 0.15), ("heart", 0.12, 0.62, 90, -20, 0.3),
          ("heart", 0.86, 0.7, 140, 10, 0.45), ("heart", 0.7, 0.1, 70, 0, 0.6), ("sparkle", 0.3, 0.08, 60, 0, 0.7),
          ("sparkle", 0.92, 0.45, 50, 0, 0.8)]
STARS = [("star", 0.17, 0.15, 140, -10, 0.0), ("sparkle", 0.83, 0.2, 120, 0, 0.15), ("star", 0.88, 0.62, 100, 15, 0.3),
         ("sparkle", 0.12, 0.55, 90, 0, 0.45), ("star", 0.75, 0.88, 80, -8, 0.55), ("sparkle", 0.25, 0.85, 70, 0, 0.65),
         ("sparkle", 0.5, 0.06, 55, 0, 0.75)]
ARROWS = [("arrow", 0.2, 0.3, 230, 35, 0.0), ("arrow", 0.8, 0.32, 230, 145, 0.2), ("arrow_down", 0.22, 0.75, 200, -30, 0.4),
          ("arrow_down", 0.8, 0.74, 200, -150, 0.6)]
MIX = [("heart", 0.16, 0.16, 120, -12, 0.0), ("star", 0.84, 0.14, 100, 10, 0.12), ("smiley", 0.85, 0.82, 120, 8, 0.24),
       ("sparkle", 0.12, 0.5, 80, 0, 0.36), ("arrow", 0.25, 0.86, 200, -20, 0.48), ("cloud", 0.5, 0.07, 150, 0, 0.6),
       ("sparkle", 0.9, 0.48, 60, 0, 0.7), ("heart", 0.6, 0.93, 60, 12, 0.8)]

doodle("garabato-corazones", "Garabatos de corazones", "Doodle hearts", HEARTS, tags=["corazones", "amor"],
       sample="couple-07.jpg")
doodle("garabato-corazones-rosa", "Corazones rosa a mano", "Pink doodle hearts", HEARTS, color=PINK, shadow=False,
       tags=["corazones", "rosa", "amor"], sample="selfie-01.jpg")
doodle("garabato-estrellas", "Garabatos de estrellas", "Doodle stars", STARS, tags=["estrellas", "stars", "brillos"],
       sample="friends-08.jpg")
doodle("garabato-estrellas-doradas", "Estrellas doradas a mano", "Gold doodle stars", STARS, color=GOLDC,
       tags=["estrellas", "dorado", "gold"], sample="graduation-05.jpg")
doodle("garabato-flechas", "Flechas a mano", "Doodle arrows", ARROWS, tags=["flechas", "arrows", "señalar", "mira"],
       sample="outfit-03.jpg")
doodle("garabato-flechas-neon", "Flechas neón", "Neon doodle arrows", ARROWS, color=NEON, shadow=False,
       tags=["flechas", "neon", "amarillo", "señalar"], sample="outfit-01.jpg")
doodle("garabato-mix", "Garabatos variados", "Doodle mix", MIX, tags=["mix", "variado", "scrapbook", "diario"],
       sample="selfie-02.jpg")
doodle("garabato-mix-negro", "Garabatos negros", "Black doodle mix", MIX, color=BLACK, shadow=False,
       tags=["negro", "black", "mix", "minimal"], sample="outfit-02.jpg")
doodle("garabato-mix-rosa", "Garabatos rosa", "Pink doodle mix", MIX, color=PINK, shadow=False,
       tags=["rosa", "pink", "mix", "kawaii"], sample="selfie-03.jpg")
doodle("garabato-corona", "Corona a mano", "Doodle crown", [("crown", 0.5, 0.16, 330, -6, 0.0),
                                                          ("sparkle", 0.28, 0.12, 60, 0, 0.5), ("sparkle", 0.72, 0.1, 50, 0, 0.6)],
       tags=["corona", "crown", "rey", "reina", "queen", "king"], sample="portrait-02.jpg")
doodle("garabato-corona-dorada", "Corona dorada a mano", "Gold doodle crown",
       [("crown", 0.5, 0.16, 330, -6, 0.0), ("sparkle", 0.28, 0.12, 60, 0, 0.5), ("sparkle", 0.72, 0.1, 50, 0, 0.6)],
       color=GOLDC, tags=["corona", "dorada", "gold", "reina", "cumpleaños"], sample="quince-01.jpg")
doodle("garabato-caritas", "Caritas a mano", "Doodle smileys",
       [("smiley", 0.18, 0.15, 150, -10, 0.0), ("smiley", 0.83, 0.8, 160, 12, 0.3), ("sparkle", 0.85, 0.18, 70, 0, 0.5),
        ("heart", 0.15, 0.82, 90, -10, 0.6)], tags=["caritas", "smiley", "feliz", "happy"], sample="friends-06.jpg")
doodle("garabato-cielo", "Nubes y sol a mano", "Doodle sky",
       [("sun", 0.8, 0.12, 200, 0, 0.0), ("cloud", 0.25, 0.12, 220, 0, 0.3), ("cloud", 0.65, 0.25, 140, 0, 0.5)],
       tags=["nubes", "sol", "cielo", "verano", "summer", "dia"], sample="beach-03.jpg")
doodle("garabato-flores", "Flores a mano", "Doodle flowers",
       [("flower", 0.15, 0.16, 150, 0, 0.0), ("flower", 0.86, 0.24, 120, 20, 0.2), ("flower", 0.1, 0.78, 110, 10, 0.4),
        ("flower", 0.88, 0.82, 150, -15, 0.6), ("sparkle", 0.5, 0.06, 50, 0, 0.75)],
       tags=["flores", "flowers", "primavera", "spring", "dia de la madre"], sample="mother-02.jpg")
doodle("garabato-subrayado", "Subrayado a mano", "Hand underline", [("underline", 0.5, 0.72, 520, -3, 0.0)],
       tags=["subrayado", "underline", "resaltar", "highlight", "texto"], sample="study-02.jpg", draw=0.6)
doodle("garabato-circulo", "Círculo a mano", "Hand-drawn circle", [("circle", 0.5, 0.45, 600, -4, 0.0)],
       tags=["circulo", "circle", "resaltar", "highlight", "señalar", "mira esto"], sample="pet-03.jpg", draw=0.8)
doodle("garabato-circulo-rojo", "Círculo rojo a mano", "Red hand-drawn circle", [("circle", 0.5, 0.45, 600, -4, 0.0)],
       color=fx.hex_rgb("#ff2b2b"), shadow=False, tags=["circulo", "rojo", "red", "resaltar", "señalar"],
       sample="interior-03.jpg", draw=0.8)
doodle("garabato-brillo", "Líneas de brillo", "Shine lines",
       [("shine", 0.24, 0.24, 140, 0, 0.0), ("shine", 0.76, 0.24, 140, 90, 0.1)],
       tags=["brillo", "shine", "destacar", "nuevo", "wow"], sample="coffee-01.jpg", draw=0.5)
doodle("garabato-estallido", "Estallido a mano", "Doodle burst", [("burst", 0.5, 0.42, 820, 0, 0.0)],
       tags=["estallido", "burst", "rayos", "sorpresa", "wow", "impacto"], sample="portrait-05.jpg", draw=0.5)
doodle("garabato-mariposas", "Mariposas a mano", "Doodle butterflies",
       [("butterfly", 0.2, 0.18, 150, -15, 0.0), ("butterfly", 0.82, 0.3, 110, 15, 0.25),
        ("butterfly", 0.15, 0.7, 90, 10, 0.5)], tags=["mariposas", "butterflies", "primavera", "aesthetic"],
       sample="garden-02.jpg")
doodle("garabato-musica", "Notas musicales a mano", "Doodle music notes",
       [("note", 0.18, 0.2, 140, -12, 0.0), ("notes", 0.82, 0.16, 150, 8, 0.2), ("note", 0.86, 0.66, 110, 14, 0.4),
        ("notes", 0.14, 0.72, 120, -8, 0.6)], tags=["musica", "notas", "music", "cantar", "baile"], sample="podcast-03.jpg")
doodle("garabato-signos", "Signos a mano", "Doodle marks",
       [("exclaim", 0.2, 0.18, 150, -10, 0.0), ("question", 0.82, 0.18, 150, 10, 0.25), ("exclaim", 0.87, 0.72, 110, 12, 0.5),
        ("spiral", 0.13, 0.72, 120, 0, 0.6)], tags=["signos", "pregunta", "sorpresa", "duda", "humor", "que"],
       sample="man-01.jpg")
doodle("garabato-rayos", "Rayos a mano", "Doodle lightning",
       [("bolt", 0.18, 0.16, 180, -15, 0.0), ("bolt", 0.84, 0.2, 150, 15, 0.2), ("bolt", 0.86, 0.75, 130, 10, 0.4)],
       tags=["rayos", "lightning", "energia", "power", "fuerza", "gym"], sample="gym-01.jpg", color=NEON, shadow=False)
doodle("garabato-angel", "Alas de ángel y aureola", "Angel wings and halo",
       [("halo", 0.5, 0.12, 280, 0, 0.0), ("wing_l", 0.3, 0.42, 420, 0, 0.3), ("wing_r", 0.7, 0.42, 420, 0, 0.3)],
       tags=["angel", "alas", "wings", "aureola", "halo", "bueno", "tierno"], sample="baby-02.jpg")
doodle("garabato-angel-dorado", "Alas doradas", "Gold angel wings",
       [("halo", 0.5, 0.12, 280, 0, 0.0), ("wing_l", 0.3, 0.42, 420, 0, 0.3), ("wing_r", 0.7, 0.42, 420, 0, 0.3)],
       color=GOLDC, glow=True, tags=["angel", "alas", "dorado", "halo", "brillo"], sample="portrait-07.jpg")
doodle("garabato-diablito", "Cuernos de diablito", "Little devil",
       [("horn_l", 0.36, 0.12, 200, 0, 0.0), ("horn_r", 0.64, 0.12, 200, 0, 0.15), ("tail", 0.8, 0.78, 260, -20, 0.4)],
       color=fx.hex_rgb("#ff2b2b"), shadow=False, tags=["diablito", "cuernos", "devil", "travieso", "humor"],
       sample="halloween-01.jpg")
doodle("garabato-diablito-blanco", "Cuernos a mano", "Doodle horns",
       [("horn_l", 0.36, 0.12, 200, 0, 0.0), ("horn_r", 0.64, 0.12, 200, 0, 0.15), ("tail", 0.8, 0.78, 260, -20, 0.4)],
       tags=["cuernos", "horns", "travieso", "humor"], sample="halloween-04.jpg")
doodle("garabato-neon-corazones", "Corazones de neón a mano", "Neon doodle hearts", HEARTS, color=fx.hex_rgb("#ff2fb3"),
       glow=True, tags=["neon", "corazones", "noche", "aesthetic"], sample="concert-01.jpg")

design("garabato-flechas-girando", "Flechas que giran", "Spinning arrows", "garabatos", 3,
       tags=DOODLE_TAGS + ["flechas", "girando", "spinning", "mira", "atencion", "señalar"], sample="cooking-04.jpg")(
    _doodle([("arrow", 0.5, 0.2, 260, 0, 0.0), ("arrow", 0.5, 0.7, 260, 180, 0.0)], draw=0, spin=(0.5, 0.45)))


# ================================================================ Marcos y texturas

@lru_cache(maxsize=8)
def _torn_edge(w, h, s, seed, inset, kind):
    """Coverage of a white paper border with a torn inner edge (inset in px)."""
    r = np.random.default_rng(seed)
    big = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(big)
    pts = []
    m = inset
    n = 70
    for side in range(4):
        for k in range(n):
            u = k / n
            j = r.normal(0, 7 * s) + (r.uniform(-14, 14) * s if r.random() < 0.15 else 0)
            if side == 0:
                pts.append((m + (w - 2 * m) * u, m + j))
            elif side == 1:
                pts.append((w - m + j, m + (h - 2 * m) * u))
            elif side == 2:
                pts.append((w - m - (w - 2 * m) * u, h - m + j))
            else:
                pts.append((m + j, h - m - (h - 2 * m) * u))
    if kind == "round":
        d.rounded_rectangle([m, m, w - m, h - m], radius=int(40 * s), fill=0)
    else:
        d.polygon(pts, fill=0)
    return np.asarray(big, np.float32) / 255.0


def _paper_frame(color=(0.98, 0.97, 0.94), inset=70, stop_motion=True, tape=False):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        grain = fx.tile_noise(256, 5, falloff=0.6)

        def frame(t):
            step = int(t * 8) % 4 if stop_motion else 0     # 8 fps paper jitter, like cut-out animation
            cov = _torn_edge(w, h, round(s, 3), 40 + step, int(inset * s), "torn")
            shadow = np.asarray(Image.fromarray((cov * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12 * s)),
                                np.float32) / 255.0
            c = Canvas(w, h)
            c.fill((0, 0, 0), np.clip(shadow - cov, 0, 1) * 0.55)
            tex = 0.92 + 0.08 * fx.sample_tile(grain, w, h, 0, 0, 0.25)
            col = np.asarray(color, np.float32)[None, None, :] * tex[..., None]
            c.layer(col.astype(np.float32), cov)
            if tape:
                for (x, y, a) in ((0.12, 0.05, -35), (0.88, 0.05, 35), (0.12, 0.95, 35), (0.88, 0.95, -35)):
                    im = Image.new("L", (int(260 * s), int(70 * s)), 210)
                    im = im.rotate(a + (step - 1.5) * 1.5, expand=True)
                    c.image(im, int(x * w - im.width / 2), int(y * h - im.height / 2), fx.hex_rgb("#f3e3b8"), 0.85)
            return c
        return frame
    return make


MARCO = ["marco", "frame", "borde", "border"]
design("marco-papel-recortado", "Papel recortado", "Cut-out paper frame", "marcos", 3,
       tags=MARCO + ["papel", "recortado", "cutout", "paper", "stop motion", "scrapbook", "collage"],
       sample="friends-09.jpg")(_paper_frame())
design("marco-papel-cinta", "Papel con cinta", "Taped paper frame", "marcos", 3,
       tags=MARCO + ["papel", "cinta", "tape", "scrapbook", "recuerdo", "collage"], sample="family-02.jpg")(
    _paper_frame(tape=True))
design("marco-papel-negro", "Papel recortado negro", "Black cut-out frame", "marcos", 3,
       tags=MARCO + ["papel", "negro", "black", "recortado", "collage"], sample="fashion-03.jpg")(
    _paper_frame(color=(0.08, 0.08, 0.09)))


@design("marco-polaroid", "Marco Polaroid", "Instant photo frame", "marcos", 3,
        tags=MARCO + ["polaroid", "instantanea", "foto", "recuerdo", "vintage", "retro"], sample="couple-04.jpg")
def _instant(w, h, T, rng):
    s = min(w, h) / 1080
    m, bottom = int(70 * s), int(330 * s)
    im, d = fx.draw_layer(w, h)
    d.rectangle([0, 0, w, h], fill=255)
    d.rectangle([m, m, w - m, h - bottom], fill=0)

    def frame(t):
        c = Canvas(w, h)
        c.image(im, 0, 0, (0.97, 0.96, 0.93), 1)
        inner = np.zeros((h, w), np.float32)
        inner[m:m + int(6 * s), m:w - m] = 0.25
        inner[m:h - bottom, m:m + int(6 * s)] = 0.25
        c.fill((0, 0, 0), inner)
        return c
    return frame


def _neon_frame(col, radius=50):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        im, d = fx.draw_layer(w, h)
        m = int(60 * s)
        d.rounded_rectangle([m, m, w - m, h - m], radius=int(radius * s), outline=255, width=int(10 * s))
        cov = np.asarray(im, np.float32) / 255
        glow = np.asarray(im.filter(ImageFilter.GaussianBlur(22 * s)), np.float32) / 255
        frames = int(T * 30)
        flick = [1.0 if np.random.default_rng(i).random() > 0.06 else 0.45 for i in range(frames)]

        def frame(t):
            k = flick[int(round(t * 30)) % frames]
            c = Canvas(w, h)
            c.fill(col, np.clip(glow * 2.2, 0, 1) * 0.85 * k)
            c.fill((1, 1, 1), cov * k)
            c.fill(col, cov * 0.3 * k)
            return c
        return frame
    return make


design("marco-neon-rosa", "Marco de neón rosa", "Pink neon frame", "marcos", 4,
       tags=MARCO + ["neon", "rosa", "luces", "noche", "fiesta"], sample="concert-02.jpg")(_neon_frame(fx.hex_rgb("#ff2fb3")))
design("marco-neon-azul", "Marco de neón azul", "Blue neon frame", "marcos", 4,
       tags=MARCO + ["neon", "azul", "cyber", "gaming", "noche"], sample="gym-05.jpg")(_neon_frame(fx.hex_rgb("#2fd8ff")))


@design("marco-brillos", "Marco de brillos", "Sparkle frame", "marcos", 6,
        tags=MARCO + ["brillos", "sparkle", "dorado", "elegante", "boda", "quince"], sample="quince-03.jpg")
def _sparkle_frame(w, h, T, rng):
    s = min(w, h) / 1080
    n = 120
    per = 2 * (w + h)
    pos = rng.uniform(0, per, n)
    off = rng.normal(0, 22, n) * s
    ph = rng.uniform(0, TAU, n)
    k = rng.integers(1, 4, n)
    sz = rng.uniform(20, 60, n) * s
    m = 60 * s

    def at(p, o):
        if p < w:
            return p, m + o
        if p < w + h:
            return w - m + o, p - w
        if p < 2 * w + h:
            return 2 * w + h - p, h - m + o
        return m + o, per - p

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            x, y = at(pos[i], off[i])
            b = max(0.0, math.sin(TAU * k[i] * u + ph[i])) ** 2
            c.splat(fx.glow(int(sz[i] * 0.5)), x, y, GOLD[i % len(GOLD)], 0.5 * b, add=True)
            c.splat(fx.sparkle(int(sz[i] * (0.5 + 0.5 * b))), x, y, (1, 1, 1), 0.3 + 0.7 * b, add=True)
        return c
    return frame


def _speed_lines(radial=True):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        frames = int(T * 30)

        def frame(t):
            i = int(round(t * 30)) % frames
            r = np.random.default_rng(1500 + i // 2)
            im = Image.new("L", (w, h), 0)
            d = ImageDraw.Draw(im)
            cx, cy = w / 2, h * 0.45
            if radial:
                for _ in range(90):
                    a = r.uniform(0, TAU)
                    r0 = r.uniform(0.32, 0.5) * h
                    wd = r.uniform(0.004, 0.018)
                    R = h
                    d.polygon([(cx + math.cos(a - wd) * R, cy + math.sin(a - wd) * R),
                               (cx + math.cos(a) * r0, cy + math.sin(a) * r0),
                               (cx + math.cos(a + wd) * R, cy + math.sin(a + wd) * R)], fill=255)
            else:
                for _ in range(40):
                    y = r.uniform(0, h)
                    L = r.uniform(0.2, 0.6) * w
                    th = r.uniform(2, 9) * s
                    x0 = -20 if r.random() < 0.5 else w - L
                    d.polygon([(x0, y), (x0 + L, y + th / 2 if x0 < 0 else y), (x0 + (L if x0 >= 0 else 0), y + th)],
                              fill=255)
            c = Canvas(w, h)
            c.image(im, 0, 0, (1, 1, 1), 0.9)
            return c
        return frame
    return make


design("marco-lineas-velocidad", "Líneas de velocidad", "Speed lines", "marcos", 2,
       tags=["lineas de velocidad", "speed lines", "anime", "manga", "comic", "impacto", "dramatico", "zoom"],
       sample="man-03.jpg")(_speed_lines(True))
design("marco-lineas-laterales", "Líneas de movimiento", "Motion lines", "marcos", 2,
       tags=["lineas", "movimiento", "motion lines", "anime", "rapido", "velocidad", "comic"], sample="man-01.jpg")(
    _speed_lines(False))


@design("marco-semitono", "Semitono de cómic", "Comic halftone", "marcos", 3,
        tags=["semitono", "halftone", "comic", "pop art", "puntos", "retro", "marco"], sample="friends-07.jpg")
def _halftone(w, h, T, rng):
    s = min(w, h) / 1080
    step = int(26 * s)
    vg = fx.vignette(w, h, 0.35, 1.15)

    def frame(t):
        u = t / T
        im = Image.new("L", (w * 2, h * 2), 0)
        d = ImageDraw.Draw(im)
        for y in range(0, h, step):
            for x in range((y // step % 2) * step // 2, w, step):
                v = vg[min(y, h - 1), min(x, w - 1)] * (0.85 + 0.15 * math.sin(TAU * u + x * 0.01))
                r = v * step * 0.6
                if r > 0.6:
                    d.ellipse([(x - r) * 2, (y - r) * 2, (x + r) * 2, (y + r) * 2], fill=255)
        im = im.resize((w, h), Image.LANCZOS)
        c = Canvas(w, h)
        c.image(im, 0, 0, (0.05, 0.05, 0.08), 0.85)
        return c
    return frame


@design("textura-papel", "Textura de papel", "Paper texture", "marcos", 2,
        tags=["textura", "papel", "paper", "texture", "vintage", "collage", "artesanal"], sample="cafe-01.jpg")
def _paper_tex(w, h, T, rng):
    fibre = fx.tile_noise(512, 99, falloff=1.1)
    blot = fx.tile_noise(512, 98, falloff=2.4)

    def frame(t):
        i = int(round(t * 12)) % 4   # a slow boil, like a scanned page
        a = fx.sample_tile(fibre, w, h, i * 37, i * 53, 0.8)
        b = fx.sample_tile(blot, w, h, 0, 0, 0.4)
        c = Canvas(w, h)
        c.fill(fx.hex_rgb("#f1e6cf"), 0.12 + 0.1 * b)
        c.fill((0.25, 0.2, 0.12), np.clip((a - 0.55) * 0.8, 0, 0.25))
        return c
    return frame


@design("textura-grunge", "Textura grunge", "Grunge texture", "marcos", 2,
        tags=["grunge", "textura", "texture", "sucio", "rock", "urbano", "rayado"], sample="man-02.jpg")
def _grunge(w, h, T, rng):
    stains = fx.tile_noise(512, 31, falloff=1.4)
    vg = fx.vignette(w, h, 0.4, 1.2)

    def frame(t):
        i = int(round(t * 12)) % 6
        r = np.random.default_rng(i)
        n = fx.sample_tile(stains, w, h, i * 71, i * 29, 0.6)
        im, d = fx.draw_layer(w, h)
        for _ in range(40):
            x, y = r.uniform(0, w), r.uniform(0, h)
            a = r.uniform(0, TAU)
            L = r.uniform(30, 260) * w / 1080
            d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=int(r.uniform(80, 200)), width=1)
        c = Canvas(w, h)
        c.fill((0.05, 0.04, 0.03), np.clip((n - 0.5) * 1.4, 0, 0.55) * (0.4 + 0.6 * vg))
        c.image(im, 0, 0, (0.95, 0.93, 0.88), 0.5)
        return c
    return frame
