"""LOGO folder video 2 as Stock templates (lg2-*). See docs/plan-logo.md.

The eight reveals of 47586149.mp4 («simple and flat corporate logo pack», 1920×1080 at 29.97 fps). From 5.5 s the
video is split in two 960 px halves showing each reveal twice, in green (left) and in blue (right), with the same
motion: one template per reveal, laid out at the same pixel scale in the middle of the 1920×1080 frame, the colours
alternating green / blue between templates so both looks are there. The brand mark is always the `logo-flip` slot;
the brand word becomes «YOUR BRAND». Each piece plays forward and holds (the reference cuts, no exit). Study notes
in tienda/plantillas/estudio-47586149/NOTAS.md; frame numbers in comments are 29.97 fps frames from the piece start.
"""

from __future__ import annotations

import math
import os

from kit import wide
from scene import effect, keys
from templates_tit_c import FPS
from templates_tit_e import solid
from templates_tit_h import lin, poly, ring, rot_pt
from templates_yp7 import Y as _Y

M = "Montserrat"
BG = "#0F0F0F"
TITLE, TAGC = "#EAEAEA", "#E2E2E2"
SCHEMES = {
    "green": {"acc": "#84C14A", "dark": "#3E6326", "glow": "#2E8A22", "flash": "#3A9F2C",
              "title": "FOLLOW ME ON", "tag": "#yourtagline", "tagw": 293},
    "blue": {"acc": "#33B0DC", "dark": "#1E5D72", "glow": "#1F7A8C", "flash": "#2E8FA6",
             "title": "SUBSCRIBE ME", "tag": "@yourlink", "tagw": 250},
}
WORD = "YOUR BRAND"
# Layouts (screen px): logo slot (cx, cy, size); text lines (x0, x1, cy) = ink width and its middle.
WORD_L = {"logo": (670, 548, 132), "word": (748, 1302, 560), "tag": (813, 1106, 642)}
VERT_L = {"logo": (959, 458, 310), "title": (703, 1216, 681), "tag": (835, 1084, 768)}
HOR_L = {"logo": (650, 544, 210), "title": (788, 1357, 507), "tag": (785, 1106, 606)}


class Y(_Y):
    """Forward piece; the frame number is rounded so frame tests (fr >= 21) are exact."""

    def frame(self, u):
        return round(u * FPS, 6)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):
    """Ease out (cubic)."""
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def seg(fr, at, n, f=eo):
    return f(clamp((fr - at) / max(1e-6, n)))


def path(fr, pts, f=eio):
    """Piecewise eased value: pts = [(frame, value), ...]; values may be tuples."""
    if fr <= pts[0][0]:
        return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if fr <= b:
            q = f((fr - a) / max(1e-6, b - a))
            if isinstance(va, tuple):
                return tuple(x + (y - x) * q for x, y in zip(va, vb))
            return va + (vb - va) * q
    return pts[-1][1]


def _p(id, es, en, order, dur, section, tags=()):
    return wide(f"lg2-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "logo", "plano", "corporativo"] + list(tags), thumb_at=round(dur - 0.8, 1))


def bg(s, colour=BG):
    return s.rect("Fondo", solid(colour), lambda fr, u: (-10, -10, 1930, 1090))


def place(cx, cy, g, pivot):
    """Where (cx, cy) goes under g = (dx, dy, scale, rot, op) about pivot."""
    dx, dy, sc, rot, _ = g
    px, py = pivot
    nx, ny = px + (cx - px) * sc, py + (cy - py) * sc
    nx, ny = rot_pt(nx, ny, rot, px, py)
    return nx + dx, ny + dy


NONE = (lambda fr: (0.0, 0.0, 1.0, 0.0, 1.0))


def logo(s, spec, g=NONE, pivot=(960, 540), name="Logo", reuse=None):
    """The user's logo (slot) at spec = (cx, cy, size), moved by g(fr) = (dx, dy, scale, rot, op) about pivot."""
    cx, cy, size = spec

    def geom(fr, u):
        v = g(fr)
        x, y = place(cx, cy, v, pivot)
        return x, y, size * v[2], size * v[2], v[3], v[4]
    kw = {"reuse": reuse} if reuse else {}
    return s.pic(name, "logo-flip", geom, label="Tu logo", base=(size, size), brandRole="logo", **kw)


def line(s, content, spec, weight, colour, name, g=NONE, pivot=(960, 540), editable=True):
    """A text line whose ink spans spec = (x0, x1, cy), moved by g(fr) about pivot."""
    x0, x1, cy = spec
    ink = (x0, cy - 60, x1, cy + 60)

    def geom(fr, u):
        dx, dy, sc, rot, op = g(fr)
        ax, ay = s.about(ink, pivot[0], pivot[1], sc, rot)
        return ax + dx, ay + dy, sc, rot, op
    return s.say(content, ink, M, weight, colour, name, geom=geom, editable=editable)


def per_frame(s, fn):
    return keys([(u, round(fn(fr), 4), "linear") for u, fr in s.each()])


def ellipse_twice():
    return "M " + " L ".join(f"{50 + 50 * math.cos(math.radians(a)):.2f} {50 + 50 * math.sin(math.radians(a)):.2f}"
                             for a in range(0, 721, 5))


def orbit(s, name, colour, width, geom, start, span):
    """A stroke along an ellipse: geom(fr, u) = (cx, cy, w, h, rot, op); start(fr) / span(fr) in degrees pick the
    visible part (the path goes round twice so the window can travel)."""
    clip = s.obj(name, ring(colour, width), geom, path=ellipse_twice())

    def window(fr):
        a = start(fr) % 360.0
        b = a + clamp(span(fr), 0.0, 359.0)
        return a / 7.2, b / 7.2
    clip["shapeStyle"]["keyframes"] = {"trimStart": per_frame(s, lambda fr: window(fr)[0]),
                                       "trimEnd": per_frame(s, lambda fr: window(fr)[1])}
    return clip


def radial(colour, alpha=1.0):
    a = format(round(alpha * 255), "02x")
    c = colour.lstrip("#").lower()
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": f"#{a}{c}",
                       "gradient": {"kind": "radial", "space": "block",
                                    "stops": [{"pos": 0.0, "color": f"#{a}{c}"},
                                              {"pos": 1.0, "color": f"#00{c}"}]}}},
            {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0,
             "paint": {"kind": "solid", "color": "#00000000"}}]


def glitch_text(s, c, at, layout=HOR_L, dx=lambda fr: 0.0):
    """The title comes in letter by letter, blurred, in the accent colour with its RGB channels apart, and turns
    white; the tagline blurs in under it a little later (the shared text of the side-logo reveals)."""
    title = line(s, c["title"], layout["title"], 700, TITLE, "Título", g=lambda fr: (dx(fr), 0, 1, 0, 1))
    s.typed(title, at, stagger=0.05, duration=0.3, preset="blur-in")
    s.fx(title, "layer.color_overlay", animated={"opacity": lambda fr, u: 1 - seg(fr, at + 9, 9)},
         color=c["acc"].lower())
    s.fx(title, "rgb_split", animated={"amount": lambda fr, u: 9 * (1 - seg(fr, at + 4, 16))}, angle=0)
    x0, x1, cy = layout["tag"]
    tag = line(s, c["tag"], (x0, x0 + c["tagw"], cy), 400, TAGC, "Texto",
               g=lambda fr: (dx(fr) - 30 * (1 - seg(fr, at + 11, 8)), 0, 1, 0, seg(fr, at + 11, 5)))
    s.fx(tag, "builtin.effects.gaussian_blur", animated={"u_blurRadius": lambda fr, u: 6 * (1 - seg(fr, at + 11, 9))})
    return title, tag


# --- 1. Spin: the logo and the word spin in a radial blur, the word unbends, a thin ring and a small ring -----------
def spin():
    D = 4.9
    t = _p("giro", "Logo: giro que se desenrolla", "Logo: unwinding spin", 13800, D, "aperturas", ["giro"])
    s = Y(t, D)
    c = SCHEMES["green"]
    bg(s)
    P = (960, 548)

    def g(fr, extra=0.0):
        a = 620 * (1 - seg(fr, 0, 30)) + extra
        sc = 1 + 1.0 * (1 - seg(fr, 0, 26)) + 0.1 * lin(fr, 26, 120)
        return 0.0, 0.0, sc, a, seg(fr, 0, 5) * (1.0 if not extra else 0.7 * (1 - seg(fr, 10, 12)))
    main = logo(s, WORD_L["logo"], g, P)
    for extra in (120.0, 240.0):
        gg = (lambda fr, extra=extra: g(fr, extra))
        logo(s, WORD_L["logo"], gg, P, name=f"Logo (aspa {int(extra)})", reuse=main["placeholderId"])
        line(s, WORD, WORD_L["word"], 600, "#FFFFFF", f"Título (aspa {int(extra)})",
             lambda fr, gg=gg: gg(fr)[:4] + (gg(fr)[4] * (0.3 + 0.7 * seg(fr, 6, 10)),), P, editable=False)
    line(s, WORD, WORD_L["word"], 600, "#FFFFFF", "Título",
         lambda fr: g(fr)[:4] + (g(fr)[4] * (0.3 + 0.7 * seg(fr, 6, 10)),), P)
    x0, x1, cy = WORD_L["tag"]
    line(s, c["tag"], (x0 + (293 - c["tagw"]) / 2, x0 + (293 + c["tagw"]) / 2, cy), 400, TAGC, "Texto",
         lambda fr: (0, 24 * (1 - seg(fr, 26, 7)), g(fr)[2], 0, seg(fr, 26, 5)), P)
    t.adjust([effect("stylize.twirl", {"angle": per_frame(s, lambda fr: path(fr, [(8, 0.0), (17, -240.0), (29, 0.0)]))},
                     radius=0.62, centerX=0.5, centerY=0.507),
              effect("spin_blur", {"amount": per_frame(s, lambda fr: 1 - seg(fr, 4, 22))}, centerX=0.5,
                     centerY=0.507, samples=24)], name="Giro")
    # the thin ring round it: arcs that turn and shorten, gone by frame 34
    orbit(s, "Aro", "#BFBFBF", 2.0, lambda fr, u: (960, 540, 800, 800, 0, seg(fr, 1, 5) * (1 - seg(fr, 24, 10))),
          start=lambda fr: -60 + 9 * fr, span=lambda fr: 240 - 150 * seg(fr, 14, 18))
    # a small ring runs up the right side, another one grows at the left
    def small(fr, u):
        a = math.radians(40 - 75 * seg(fr, 20, 9, lambda x: x))
        return 960 + 410 * math.cos(a), 540 + 410 * math.sin(a), 36, 36, 0, seg(fr, 20, 2) * (1 - seg(fr, 28, 4))
    s.obj("Aro chico", ring("#D0D0D0", 3), small, kind="ellipse", base=(36, 36))
    s.obj("Aro chico 2", ring("#BDBDBD", 3), lambda fr, u: (585, 622, 10 + 30 * seg(fr, 28, 8), 10 + 30 * seg(fr, 28, 8),
                                                            0, seg(fr, 28, 2) * (1 - seg(fr, 34, 6))),
          kind="ellipse", base=(40, 40))
    return t


# --- 2. Dots: a row of dots rolls left to right over the word and uncovers it ------------------------------------
def dots():
    D = 4.9
    t = _p("puntos", "Logo: puntos que ruedan", "Logo: rolling dots", 13801, D, "aperturas", ["puntos"])
    s = Y(t, D)
    c = SCHEMES["blue"]
    bg(s)
    wipe = lambda fr: 640 + 760 * seg(fr, 12, 30, lambda x: x)  # noqa: E731
    logo(s, WORD_L["logo"], lambda fr: (0, 0, 0.9 + 0.1 * seg(fr, 26, 6), 0, seg(fr, 26, 4)))
    word = s.say(WORD, (WORD_L["word"][0], 500, WORD_L["word"][1], 620), M, 600, "#FFFFFF", "Título",
                 reveal=lambda fr: (0, 0, wipe(fr), 1080))
    del word
    x0, x1, cy = WORD_L["tag"]
    tw = c["tagw"]
    s.say(c["tag"], (x0 + (293 - tw) / 2, cy - 60, x0 + (293 + tw) / 2, cy + 60), M, 400, TAGC, "Texto",
          reveal=lambda fr: (0, 0, 820 + 320 * seg(fr, 30, 6, lambda x: x), 1080))
    # each dot rolls 30 px a frame for 22 frames: dark, then the colour, white, light grey, and it fades out dark
    speed, life, d = 30.0, 22.0, 210.0
    for i, t0 in enumerate((-3, 2, 7, 12, 17)):
        def x_of(fr, t0=t0):
            return 640 + speed * (fr - t0)

        def age(fr, t0=t0):
            return (fr - t0) / life

        def disc(colour, op_fn, name, t0=t0):
            def geom(fr, u):
                a = age(fr)
                on = 0.0 if a < 0 or a > 1 else op_fn(a)
                return x_of(fr), 548, d, d, 0, on
            clip = s.obj(name, solid(colour), geom, kind="ellipse", base=(d, d))
            s.mblur(clip)
            return clip
        tri = lambda a, c0, c1, c2: clamp(min((a - c0) / (c1 - c0), (c2 - a) / (c2 - c1)))  # noqa: E731
        disc("#8C8C8C", lambda a: clamp(a / 0.15) * (0.35 + 0.5 * tri(a, 0.5, 0.78, 1.0)) * (1 - clamp((a - 0.85) / 0.15)),
             f"Punto {i + 1}")
        disc(c["acc"], lambda a: 0.75 * tri(a, 0.08, 0.3, 0.55), f"Punto {i + 1} (color)")
        disc("#FFFFFF", lambda a: 0.88 * tri(a, 0.32, 0.55, 0.8), f"Punto {i + 1} (blanco)")
    return t


# --- 3. Slices: the big icon is built from shifted strips, coloured bars sweep and uncover the text ----------------
def slices():
    D = 4.9
    t = _p("franjas", "Sígueme: logo en franjas y rayas", "Follow me: logo in slices and bars", 13802, D, "redes",
           ["sígueme", "franjas"])
    s = Y(t, D)
    c = SCHEMES["green"]
    bg(s)
    cx, cy, size = VERT_L["logo"]
    top = cy - size / 2
    n = 10
    h = size / n
    order = [0, 9, 1, 8, 2, 7, 6, 3, 5, 4]
    starts = [2, 3, 5, 6, 7, 9, 10, 12, 14, 16]
    full = logo(s, VERT_L["logo"], lambda fr: (0, 0, 1, 0, 1.0 if fr >= 21 else 0.0))
    first = full["placeholderId"]
    for rank, i in enumerate(order):
        at = starts[rank]
        side = -1 if i % 2 else 1
        far = 90 + 40 * ((i * 7) % 3)

        def g(fr, at=at, side=side, far=far):
            shift = side * far * (1 - seg(fr, at, 6))
            jitter = -side * 22 if round(fr) in (at + 7, at + 8) and at < 14 else 0.0
            return shift + jitter, 0, 1, 0, (1.0 if fr >= at else 0.0) * (0.0 if fr >= 21 else 1.0)
        strip = logo(s, VERT_L["logo"], g, name=f"Logo (franja {i + 1})", reuse=first)
        y0 = top + i * h
        s.clipped(strip, lambda fr, y0=y0: (0, y0 - 0.5, 1920, y0 + h + 0.5))
    title = line(s, c["title"], VERT_L["title"], 700, TITLE, "Título")
    # the title opens from both ends: two background-coloured covers (upper and lower half) shrink to the middle
    tx0, tx1, tcy = VERT_L["title"]
    mid = tx0 + (tx1 - tx0) * 0.55
    for j, (a, b, at) in enumerate(((tcy - 26, tcy, 19), (tcy, tcy + 26, 21))):
        s.rect(f"Tapa {j + 1}", solid(BG),
               lambda fr, u, a=a, b=b, at=at: (mid - (mid - tx0 + 8) * (1 - seg(fr, at, 7)), a,
                                               mid + (tx1 + 8 - mid) * (1 - seg(fr, at, 7)), b)
               if fr < at + 7 else (0, 0, 0, 0))
    del title
    x0, x1, ty = VERT_L["tag"]
    tw = c["tagw"] * 0.85
    s.say(c["tag"], ((x0 + x1) / 2 - tw / 2, ty - 60, (x0 + x1) / 2 + tw / 2, ty + 60), M, 400, TAGC, "Texto",
          reveal=lambda fr: (0, 0, 820 + 330 * seg(fr, 30, 5, lambda x: x), 1080))
    # the bars: thin slanted parallelograms whose head runs right and whose tail follows
    para = poly([(3, 0), (100, 0), (97, 100), (0, 100)])
    bars = [(630, 8, 14, 8, 660, 1300), (722, 14, 17, 8, 650, 1270), (768, 18, 27, 7, 700, 1300),
            (560, 6, 7, 6, 640, 900), (770, 10, 9, 6, 1000, 1280),
            (630, 4, 24, 6, 1200, 1340), (768, 5, 31, 5, 1150, 1330)]
    for j, (y, th, at, n_, xa, xb) in enumerate(bars):
        def r(fr, u, y=y, th=th, at=at, n_=n_, xa=xa, xb=xb):
            head = xa + (xb - xa) * seg(fr, at, n_)
            tail = xa + (xb - xa) * seg(fr, at + 4, n_ + 3)
            if fr < at or tail >= xb - 1:
                return (0, 0, 0, 0)
            return (tail, y - th / 2, head, y + th / 2)
        s.rect(f"Raya {j + 1}", solid(c["acc"]), r, path=para)
    return t


# --- 4. Orbit: two grey strokes swoop in and close into an orbit, the icon turns in 3D inside and drops left -------
def orbit_piece():
    D = 4.9
    t = _p("orbita", "Suscríbete: logo en órbita", "Subscribe: logo in orbit", 13803, D, "redes",
           ["suscríbete", "órbita"])
    s = Y(t, D)
    c = SCHEMES["blue"]
    bg(s)
    lx, ly, size = HOR_L["logo"]
    centre = lambda fr: path(fr, [(0, (690.0, 495.0)), (3, (770.0, 470.0)), (8, (900.0, 475.0)),  # noqa: E731
                                  (12, (870.0, 522.0)), (17, (800.0, 528.0)), (23, (720.0, 540.0)),
                                  (30, (lx, ly))], f=lambda x: x)
    grow = lambda fr: 0.32 + 0.68 * seg(fr, 9, 18)  # noqa: E731
    clip = logo(s, HOR_L["logo"], lambda fr: (centre(fr)[0] - lx, centre(fr)[1] - ly, grow(fr),
                                              -28 * (1 - seg(fr, 9, 20)), seg(fr, 9, 3)), pivot=(lx, ly))
    s.d3(clip, ry=lambda fr, u: 540 * (1 - seg(fr, 9, 20)), persp=900)
    s.mblur(clip)
    for j in range(2):
        def geom(fr, u, j=j):
            x, y = centre(fr)
            w = path(fr, [(0, 330.0), (8, 250.0), (18, 300.0), (26, 330.0)])
            return x, y, w, w * 0.36, -22.0, seg(fr, 0, 2) * (1 - seg(fr, 19, 7))
        o = orbit(s, f"Órbita {j + 1}", "#9C9C9C", 4.0, geom, start=lambda fr, j=j: 150 + 180 * j + 16 * fr,
                  span=lambda fr: 55 + 25 * seg(fr, 6, 6))
        s.mblur(o)
    glitch_text(s, c, 14)
    return t


# --- 5. Ribbons: strips of the icon turn in 3D with a white back, speed lines, the icon builds up --------------------
def ribbons():
    D = 4.9
    t = _p("cintas", "Sígueme: logo de cintas que giran", "Follow me: logo of turning ribbons", 13804, D, "redes",
           ["sígueme", "3d"])
    s = Y(t, D)
    c = SCHEMES["green"]
    bg(s)
    lx, ly, size = HOR_L["logo"]
    cx = lambda fr: path(fr, [(2, 560.0), (16, 690.0), (28, lx)])  # noqa: E731
    full = logo(s, HOR_L["logo"], lambda fr: (cx(fr) - lx, 0, 1, 0, 1.0 if fr >= 28 else 0.0))
    first = full["placeholderId"]
    n = 6
    w = size / n
    order = [2, 4, 0, 5, 1, 3]
    for rank, i in enumerate(order):
        at = 3 + 2 * rank
        spread = 1.25

        def turn(fr, at=at):
            return 300 * (1 - seg(fr, at, 15))

        def g(fr, i=i, at=at, back=False):
            ang = turn(fr)
            front = math.cos(math.radians(ang)) >= 0
            on = fr >= at and fr < 28 and (front != back)
            off = (i - (n - 1) / 2) * w * (spread - 1) * (1 - seg(fr, at, 15))
            return cx(fr) - lx + off, 0, 0.8 + 0.2 * seg(fr, at, 10), -20 * (1 - seg(fr, at, 15)), 1.0 if on else 0.0
        for back in (False, True):
            strip = logo(s, HOR_L["logo"], lambda fr, g=g, back=back: g(fr, back=back),
                         name=f"Logo (cinta {i + 1}{', dorso' if back else ''})", reuse=first, pivot=(lx, ly))
            x0 = lx - size / 2 + i * w

            def rect(fr, x0=x0, i=i, at=at):
                off = (i - (n - 1) / 2) * w * (spread - 1) * (1 - seg(fr, at, 15))
                sc = 0.8 + 0.2 * seg(fr, at, 10)
                left = cx(fr) + (x0 - lx) * sc + off
                return (left - 0.5, 0, left + w * sc + 0.5, 1080)
            s.clipped(strip, rect)
            s.d3(strip, ry=lambda fr, u, at=at: turn(fr, at), persp=700)
            s.mblur(strip)
            if back:
                s.fx(strip, "layer.color_overlay", color="#ffffff", opacity=1.0)
    s.obj("Chispa", solid("#FFFFFF"), lambda fr, u: (555 + 10 * fr, 540, 14, 7, 0, 1.0 if 1 <= fr <= 5 else 0.0))
    for j, (y, ln, at, sp) in enumerate(((505, 120, 4, 46), (560, 80, 6, 52), (590, 140, 8, 40), (470, 60, 10, 58),
                                         (620, 100, 12, 44), (530, 70, 14, 50), (575, 110, 16, 48))):
        s.obj(f"Raya {j + 1}", solid("#8E8E8E"),
              lambda fr, u, y=y, ln=ln, at=at, sp=sp: (640 + sp * (fr - at), y, ln, 3, 0,
                                                     0.8 if at <= fr <= at + 9 else 0.0))
    glitch_text(s, c, 15)
    return t


# --- 6. Target: corners open round a diamond, a square, a ring, a disc that becomes a ring round the icon ----------
def target():
    D = 4.95
    t = _p("mira", "Suscríbete: mira que se abre", "Subscribe: opening target", 13805, D, "redes",
           ["suscríbete", "mira"])
    s = Y(t, D)
    c = SCHEMES["blue"]
    bg(s)
    T = (932.0, 540.0)
    lx, ly, size = HOR_L["logo"]
    slide = lambda fr: T[0] + (lx - T[0]) * seg(fr, 30, 40)  # noqa: E731
    W = "#FFFFFF"
    s.obj("Rombo", ring(W, 3), lambda fr, u: (T[0], T[1], 16, 16, 45, 1.0 if 1 <= fr <= 2 else 0.0))
    corner = "M 0 100 L 0 0 L 100 0"
    for j in range(4):
        def g(fr, u, j=j):
            r = 20 + 210 * seg(fr, 2, 9)
            th = math.radians(90 * j - 90)
            arm = 30 + 110 * seg(fr, 2, 9)
            x, y = T[0] + r * math.cos(th), T[1] + r * math.sin(th)
            # the corner of the L points away from the centre
            return x, y, arm, arm, math.degrees(th) - 225, (1.0 if fr >= 2 else 0.0) * (1 - seg(fr, 11, 5))
        s.obj(f"Esquina {j + 1}", ring(W, 4), g, path=corner)
    s.obj("Corchetes", ring("#6A6A6A", 2),
          lambda fr, u: (T[0], T[1], 60 + 90 * seg(fr, 4, 8), 60 + 90 * seg(fr, 4, 8), 0,
                         seg(fr, 4, 2) * (1 - seg(fr, 10, 5))))
    s.obj("Cuadrado", ring(W, 8), lambda fr, u: (T[0], T[1], path(fr, [(8, 30.0), (13, 270.0), (17, 330.0)]),
                                               path(fr, [(8, 30.0), (13, 270.0), (17, 330.0)]), 0,
                                               (1.0 if fr >= 8 else 0.0) * (1 - seg(fr, 16, 5))))
    ringd = lambda fr: path(fr, [(13, 10.0), (14, 90.0), (16, 165.0), (18, 255.0), (20, 300.0)])  # noqa: E731
    s.obj("Aro", ring(W, 7), lambda fr, u: (T[0], T[1], ringd(fr), ringd(fr), 0,
                                           (1.0 if fr >= 13 else 0.0) * (1 - seg(fr, 22, 4))), kind="ellipse",
          base=(300, 300))
    for j in range(3):
        def tick(fr, u, j=j):
            a = math.radians(-90 + 120 * j + 4 * fr)
            r = ringd(fr) / 2
            return T[0] + r * math.cos(a), T[1] + r * math.sin(a), 14, 3, math.degrees(a), \
                (1.0 if fr >= 15 else 0.0) * (1 - seg(fr, 26, 4))
        s.obj(f"Marca {j + 1}", solid(W), tick)
    discd = lambda fr: 310 * seg(fr, 19, 7)  # noqa: E731
    s.obj("Disco", solid(c["acc"]), lambda fr, u: (T[0], T[1], discd(fr), discd(fr), 0,
                                                  0.85 if 19 <= fr < 27 else 0.0), kind="ellipse", base=(310, 310))
    ring_r = lambda fr: path(fr, [(26, 78.0), (29, 141.0), (36, 178.0)])  # noqa: E731
    halo = s.obj("Aro de color", ring(c["acc"], 4),
                 lambda fr, u: (slide(fr), T[1], 2 * ring_r(fr), 2 * ring_r(fr), 0,
                                (1.0 if fr >= 26 else 0.0) * (1 - seg(fr, 31, 6))), kind="ellipse", base=(356, 356))
    halo["shapeStyle"].setdefault("keyframes", {})["layer.stroke.width"] = per_frame(
        s, lambda fr: path(fr, [(26, 156.0), (29, 32.0), (33, 6.0), (36, 3.0)]))
    logo(s, HOR_L["logo"], lambda fr: (slide(fr) - lx, T[1] - ly, 0.85 + 0.15 * seg(fr, 26, 5), 0,
                                       1.0 if fr >= 26 else 0.0), pivot=(lx, ly))
    glitch_text(s, c, 28, dx=lambda fr: slide(fr) - lx)
    return t


# --- 7. Glitch: the logo whips in from the right; RGB apart, turned frames, slices, a green glow that flickers -----
def glitch():
    D = 3.3
    t = _p("glitch", "Logo: glitch sobre verde", "Logo: glitch on green", 13806, D, "aperturas", ["glitch"])
    s = Y(t, D)
    c = SCHEMES["green"]
    bg(s, "#142414")
    # the glow: two soft spots in the corners and full flashes, level per frame
    level = [0.5, 0.6, 0.7, 0.7, 0.6, 0.5, 0.5, 0.5, 0.45, 0.5, 0.4, 0.4, 0.4, 0.5, 0.6, 0.7, 0.9, 1.0, 1.0, 0.9,
             0.8, 0.3, 0.2, 0.25, 0.4, 0.3, 0.2, 0.3, 0.5, 0.8, 1.0, 0.3, 0.2, 0.3, 0.6, 1.0, 0.8, 0.4, 0.3, 0.3]
    lv = lambda fr: level[int(round(fr)) % len(level)]  # noqa: E731
    s.obj("Fondo (brillo 1)", radial(c["glow"], 1.0), lambda fr, u: (1650, 950, 2000, 1700, 0, lv(fr)), kind="ellipse")
    s.obj("Fondo (brillo 2)", radial(c["glow"], 0.85), lambda fr, u: (150, 100, 1700, 1400, 0, lv(fr + 7) * 0.8),
          kind="ellipse")
    flash = {30: 0.75, 31: 0.5, 35: 0.35, 50: 0.6, 51: 0.3, 74: 0.5}
    s.rect("Fondo (destello)", solid(c["flash"]), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: flash.get(int(round(fr)), 0.0))
    G = {"logo": (620, 545, 150), "word": (720, 1345, 556), "tag": (815, 1105, 664)}
    P = (960, 548)

    def g(fr):
        dx = path(fr, [(0, 1150.0), (1, 700.0), (2, 330.0), (3, 110.0), (4, 25.0), (5, 0.0)], f=lambda x: x)
        sc = path(fr, [(0, 1.7), (4, 1.12), (6, 1.0)], f=lambda x: x)
        if 10 <= fr <= 12:
            return 0.0, 0.0, 1.55, -90.0, 1.0
        return dx, 0.0, sc, 0.0, 1.0
    for clip in (logo(s, G["logo"], g, P), line(s, WORD, G["word"], 600, "#FFFFFF", "Título", g, P)):
        s.fx(clip, "motion_trail", animated={"amount": lambda fr, u: 1.0 if fr < 5 else 0.0}, angle=0.0, length=1.0)
    tw = c["tagw"]
    tag = line(s, c["tag"], (G["tag"][0], G["tag"][0] + tw, G["tag"][2]), 400, TAGC, "Texto",
               lambda fr: (-125.0, 82.0, 1.0, -90.0, 1.0)
               if 17 <= fr <= 18 else (0.0, 0.0, 1.0, 0.0, 1.0 if fr >= 19 else 0.0), P)
    del tag
    for j, (x, y, on) in enumerate(((530, 700, (3, 4, 5, 6, 18, 19, 20)), (1462, 368, (9, 10, 11, 12, 13)),
                                    (1380, 760, (22, 23, 24, 25, 40, 41)), (700, 330, (28, 29, 60, 61)))):
        for k_, (w, h) in enumerate(((22, 4), (4, 22))):
            s.obj(f"Cruz {j + 1}{'ab'[k_]}", solid("#FFFFFF"),
                  lambda fr, u, x=x, y=y, w=w, h=h, on=on: (x, y, w, h, 0, 1.0 if int(round(fr)) in on else 0.0))
    rgb = [0, 0, 0, 0, 2, 4, 9, 10, 10, 9, 10, 10, 10, 10, 9, 9, 8, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 4, 5, 6, 6, 5, 6, 7,
           7, 6, 5, 6, 0, 0, 0, 0, 2, 2, 0, 4, 6, 7, 7, 6, 3, 0, 0, 0, 0, 2, 5, 6, 6, 5, 0, 0, 0, 3, 3, 0, 0, 5, 6, 7,
           6, 5, 0, 0, 0, 0, 4, 4, 0, 0, 0, 6, 7, 6, 0, 0, 0, 3, 3, 0, 0, 5, 6, 6, 5, 0, 0, 0, 0, 0]
    t.adjust([effect("rgb_split", {"amount": per_frame(s, lambda fr: 1.2 * rgb[min(len(rgb) - 1, int(round(fr)))])},
                     angle=0),
              effect("block_glitch", {"intensity": per_frame(s, lambda fr: 0.9 if int(round(fr)) in (26, 70) else 0.0)},
                     blockSize=40, shiftAmount=90, frequency=1.0, seed=7)], name="Glitch")
    return t


# --- 8. Horizon: a white line opens, the icon rises behind it, sinks and rises again; the text drops from the line --
def horizon():
    D = 5.0
    t = _p("horizonte", "Suscríbete: logo que sale del horizonte", "Subscribe: logo rising from the horizon", 13807,
           D, "redes", ["suscríbete", "horizonte"])
    s = Y(t, D)
    c = SCHEMES["blue"]
    bg(s)
    H = 633.0
    cx, cy, size = VERT_L["logo"][0], 466.0, 320.0
    ypos = lambda fr: path(fr, [(1, H + size / 2 + 10), (9, H - size / 2), (15, H - size / 2 - 14),  # noqa: E731
                               (23, 640.0), (31, cy)])
    icon = logo(s, (cx, cy, size), lambda fr: (0, ypos(fr) - cy, 1, 0, 1.0 if fr >= 1 else 0.0), pivot=(cx, cy))
    s.clipped(icon, lambda fr: (0, -200, 1920, H))
    tx0, tx1, ty = 761, 1158, 680
    title = s.say(c["title"], (tx0, ty - 60, tx1, ty + 60), M, 700, TITLE, "Título",
                  reveal=lambda fr: (0, H + 2, 1920, 1080), shift=lambda fr: (0, -60 * (1 - seg(fr, 27, 7))),
                  op=lambda fr, u: 1.0 if fr >= 27 else 0.0)
    del title
    tw = c["tagw"] * 0.9
    s.say(c["tag"], (960 - tw / 2, 695, 960 + tw / 2, 815), M, 400, TAGC, "Texto",
          reveal=lambda fr: (0, 712, 1920, 1080), shift=lambda fr: (0, -50 * (1 - seg(fr, 32, 7))),
          op=lambda fr, u: 1.0 if fr >= 32 else 0.0)
    W = "#E8E8E8"
    half = lambda fr: 30 + 380 * seg(fr, 1, 10, eio)  # noqa: E731
    gone = lambda fr: seg(fr, 27, 8, lambda x: x)  # noqa: E731

    def side(sign, dy, scale, thick, delay=0):
        def r(fr, u):
            if fr < 1 + delay:
                return (0, 0, 0, 0)
            hw = half(fr - delay) * scale
            inner = 960 + sign * (hw * 1.15 * gone(fr))
            outer = 960 + sign * hw * (1 + 0.15 * gone(fr))
            x0, x1 = sorted((inner, outer))
            return (x0, H + dy, x1, H + dy + thick) if x1 - x0 > 1 else (0, 0, 0, 0)
        return r
    for j, (dy, scale, thick, delay) in enumerate(((0, 1.0, 2.5, 0), (4, 0.7, 1.5, 2), (-3, 0.45, 1.5, 4))):
        for sign in (-1, 1):
            s.rect(f"Línea {j + 1}{'iz' if sign < 0 else 'de'}", solid(W), side(sign, dy, scale, thick, delay),
                   op=lambda fr, u, j=j: 1.0 if j == 0 else 0.6)
    return t


def tidy(t):
    """While a clip is hidden (opacity 0 or no size) keep its box where it is next seen, so the Short / Video fit
    measures the design and not where a hidden piece waits or flies off (the app fits the union of every box)."""
    for track in t.tracks:
        for clip in track.clips:
            props = [clip[n]["keyframes"] for n in ("x", "y", "width", "height") if isinstance(clip.get(n), dict)]
            if len(props) != 4 or len({len(ks) for ks in props}) != 1 or len(props[0]) < 2:
                continue
            n = len(props[0])
            op = clip.get("opacity", {}).get("keyframes") if isinstance(clip.get("opacity"), dict) else None
            op = op if op and len(op) == n else None

            def shown(i):
                return (op is None or op[i]["value"] > 0.01) and props[2][i]["value"] >= 1 and props[3][i]["value"] >= 1
            seen = [i for i in range(n) if shown(i)]
            if not seen or len(seen) == n:
                continue
            for i in range(n):
                if not shown(i):
                    j = min(seen, key=lambda v: abs(v - i))
                    for ks in props:
                        ks[i]["value"] = ks[j]["value"]
            if op is None:
                clip["opacity"] = keys([(kf["timeUs"] / 1e6, 1.0 if shown_i else 0.0, "linear")
                                        for kf, shown_i in zip(props[0], [i in seen for i in range(n)])])
    return t


TEMPLATES = [spin, dots, slices, orbit_piece, ribbons, target, glitch, horizon]


def _tidied(f):
    def g():
        return tidy(f())
    g.__name__ = f.__name__
    return g


TEMPLATES = [_tidied(f) for f in TEMPLATES]

_ONLY = os.environ.get("LG2_ONLY")
if _ONLY:
    TEMPLATES = [f for f in TEMPLATES if f.__name__ in _ONLY.split(",")]
