"""INSTAGRAM folder video as Stock templates (ig7-*). See docs/plan-instagram.md.

«Typo Instagram stories» (28897023.mp4, 960×540 at 25 fps, 68 s): ten colourful typography stories shown one by
one on a 221×392 screen at (572, 74) beside the pack title, numbered 10 → 01. Each story is laid out flat on
1080×1920 (×4.89 from the screen; ×4 from the 270×480 study crops in estudio-28897023/holds) and its moves copied
from 10 fps sheets. Times inside a story are seconds of the reference video (`Story(t, start)`), so every number
can be checked against the sheets. The title card, the numbers and the «Typo / Instagram / Envato Market» labels
are not copied; brand words (Instagram in big type, «ENVATO») become neutral words. Study notes in
tienda/plantillas/estudio-28897023/NOTAS.md.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import tall
from scene import fill, no_stroke
from templates_tk1 import Seq

W, H = 1080, 1920
M = "Montserrat"  # registered by templates_tk1

YEL, PUR, GRN, COR = "#FCCC00", "#666DE2", "#52A77F", "#E87060"
CYA, PNK, ORA, LIME, AMB = "#29D7E7", "#F351AC", "#FD7300", "#75E600", "#FDB402"
WHITE, RED = "#FFFFFF", "#E8483A"
TAGS = ["instagram", "historia", "reels", "tipografía", "colores"]


# --- curves ---------------------------------------------------------------------------------------------------------

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):
    """Ease out (cubic)."""
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def r_(T, a, n, f=eo):
    """0 → 1 between seconds a and a + n."""
    return f((T - a) / max(1e-6, n))


def lerp(a, b, x):
    return a + (b - a) * x


def lrect(a, b, x):
    return tuple(lerp(p, q, x) for p, q in zip(a, b))


def curve(T, pts, f=eio):
    """Piecewise curve through (time, value) points, eased between them."""
    if T <= pts[0][0]:
        return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if T <= b:
            return lerp(va, vb, f((T - a) / max(1e-6, b - a)))
    return pts[-1][1]


# --- paths (0..100 box) ---------------------------------------------------------------------------------------------

def poly(points):
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points) + " Z"


PLUS = poly([(36, 0), (64, 0), (64, 36), (100, 36), (100, 64), (64, 64), (64, 100), (36, 100), (36, 64), (0, 64),
             (0, 36), (36, 36)])


def _rot(points, deg):
    a = math.radians(deg)
    return [(50 + (x - 50) * math.cos(a) - (y - 50) * math.sin(a), 50 + (x - 50) * math.sin(a) + (y - 50) * math.cos(a))
            for x, y in points]


CROSS = poly(_rot([(36, 0), (64, 0), (64, 36), (100, 36), (100, 64), (64, 64), (64, 100), (36, 100), (36, 64),
                   (0, 64), (0, 36), (36, 36)], 45))


def arc_path(a0=40, a1=310, thick=0.28, n=28):
    """A C-shaped ring sector (degrees, 0 = right, clockwise in screen y)."""
    ro, ri = 50, 50 * (1 - thick * 2)
    out = [(50 + ro * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            50 + ro * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inn = [(50 + ri * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
            50 + ri * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return poly(out + inn)


ARC = arc_path()
HALF = arc_path(90, 270, 0.28)  # left half of a ring


def zig_path(lines=3, waves=3):
    """«≋»: three thin wavy vertical strokes."""
    out = []
    for i in range(lines):
        x = 15 + 35 * i
        left = [(x + 9 * math.sin(j / 12 * waves * 2 * math.pi), 100 * j / 12) for j in range(13)]
        right = [(px + 7, py) for px, py in reversed(left)]
        out.append(poly(left + right))
    return " ".join(out)


ZIG = zig_path()


def stepped(n=4):
    """A pixel diamond: stacked bars, wide in the middle (the stepped cross of story 05)."""
    pts = []
    for i in range(n):
        y0, y1 = 50 - 50 * (n - i) / n, 50 - 50 * (n - i - 1) / n
        x = 50 - 50 * (i + 1) / n
        pts.append(poly([(x, y0), (100 - x, y0), (100 - x, 100 - y0), (x, 100 - y0)]))
        _ = y1
    return " ".join(pts)


STEP = stepped(3)


def outline(colour, width):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
             "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


# --- the story builder ----------------------------------------------------------------------------------------------

class Story(Seq):
    """Seq with every function of absolute reference time T; tracks bottom-up by group."""

    LAYERS = (("bg", "shape", "Fondo", 9), ("big", "text", "Letras de fondo", 5), ("shp", "shape", "Forma", 14),
              ("mat", "shape", "Mate", 5), ("txt", "text", "Texto", 14), ("fr", "shape", "Marco", 12),
              ("deco", "shape", "Adorno", 20), ("top", "shape", "Cortinilla", 8), ("toptxt", "text", "Texto 2", 10),
              ("cover", "shape", "Cortinilla 2", 24))

    def __init__(self, t, start, end):
        Seq.__init__(self, t, start)
        self.start, self.end = start, end
        for key, ttype, name, n in self.LAYERS:
            self.group(key, ttype, name, n)

    def done(self):
        self.t.tracks = [tr for tr in self.t.tracks if tr.clips]
        return self.t

    def box(self, t0, t1, colour, r, op=None, rot=None, key="shp", name="Forma", kind="rectangle", path=None,
            layers=None, radius=0.0, role=None):
        """A shape covering r(T) = (x0, y0, x1, y1); op(T), rot(T) optional. role None: layoutfit guesses it
        (full-width bands and panels become backdrops, the rest art)."""
        m = None
        if op or rot:
            m = lambda u, d: dict(op=op(t0 + u) if op else 1.0, rot=rot(t0 + u) if rot else 0.0)  # noqa: E731
        c = self.rect(t0, t1, lambda u, d: r(t0 + u), colour, layers=layers, key=key, name=name, kind=kind,
                      path=path, m=m, role=role, radius=radius)
        if role is None:
            c.pop("layoutRole", None)
        return c

    def full(self, t0, t1, colour, key="bg", name="Fondo"):
        c = self.box(t0, t1, colour, lambda T: (-20, -20, W + 20, H + 20), key=key, name=name, role="cover")
        return c

    def txt(self, text, t0, t1, width, colour, cx=540, cy=960, font=(M, 800), sp=0.0, key="txt", name="Texto",
            s=None, dx=None, dy=None, op=None, rot=None, blur=None, editable=True, layers=None, role="art"):
        """A line whose ink is `width` px wide at rest, centred at (cx, cy); s/dx/dy/op/rot/blur(T)."""
        def m(u, d):
            T = t0 + u
            v = {}
            for k_, fn in (("s", s), ("dx", dx), ("dy", dy), ("op", op), ("rot", rot), ("blur", blur)):
                if fn:
                    v[k_] = fn(T)
            return v
        c = self.word(text, t0, t1, width, colour, m, cy=cy, cx=cx, font=font, sp=sp, key=key, name=name,
                      editable=editable, layers=layers, role=role)
        if key == "big" or not editable and width > W:
            c["layoutRole"] = "backdrop"
        return c

    # --- little decorations -----------------------------------------------------------------------------------------
    def deco(self, what, t0, t1, cx, cy, size, colour, at=None, rot=0.0, spin=0.0, drift=(0.0, 0.0), width=None,
             h=None, out=None, key="deco"):
        """ring | dot | plus | cross | arc | sq | orect | zig | line, popping in at `at` (default t0)."""
        at = t0 if at is None else at
        hh = h if h is not None else size
        kind, path, layers = "rectangle", None, None
        if what == "ring":
            kind, layers = "ellipse", outline(colour, width or max(3.0, size * 0.2))
        elif what == "dot":
            kind = "ellipse"
        elif what in ("plus", "cross", "arc", "zig"):
            kind, path = "rectangle", {"plus": PLUS, "cross": CROSS, "arc": ARC, "zig": ZIG}[what]
        elif what == "orect":
            layers = outline(colour, width or 6.0)

        def r(T):
            k = r_(T, at, 0.25, lambda x: 1 - (1 - clamp(x)) ** 2 * (1 - 2.2 * clamp(x)) if x < 1 else 1.0)
            if out is not None:
                k *= 1 - r_(T, out, 0.2)
            fx, fy = drift
            u = T - t0
            x, y = cx + fx * u, cy + fy * u
            return (x - size / 2 * k, y - hh / 2 * k, x + size / 2 * k, y + hh / 2 * k)
        return self.box(t0, t1, colour, r, rot=(lambda T: rot + spin * (T - t0)) if (rot or spin) else None,
                        key=key, name="Adorno", kind=kind, path=path, layers=layers)

    def bar(self, t0, t1, colour, r, key="fr", name="Línea", op=None):
        return self.box(t0, t1, colour, r, key=key, name=name, op=op)


def story(sid, es, en, start, end, order, tags=(), thumb=None):
    t = tall(f"ig7-{sid}", es, en, "instagram", round(end - start, 2), order=order, tags=TAGS + list(tags),
             thumb_at=round((thumb if thumb is not None else end - 0.6) - start, 2))
    return Story(t, start, end)


def matte(clip, src):
    clip["matte"] = {"clip": src["id"], "mode": "alpha"}
    return clip


# ====================================================================================================================
# 10 — TYPO (10.2 – 14.7)
# ====================================================================================================================

def typo():
    A, B = 10.2, 14.7
    s = story("typo", "Historia tipográfica: TYPO", "Typography story: TYPO", A, B, 16000, ["tarjeta"], thumb=13.9)
    shift = lambda T: 560 * r_(T, 12.32, 0.3, eio)  # noqa: E731  scene 1 pushed right by the green wipe
    # scene 1: the white screen shrinks into a card over yellow while a pink band falls away
    s.full(A, 12.65, YEL)
    s.box(11.05, 11.8, PNK, lambda T: (-20, lerp(0.37 * H, H + 10, r_(T, 11.05, 0.65)), W + 20, H + 20),
          key="bg", name="Banda rosa")
    card = (260, 452, 828, 1460)
    def card_r(T):
        x0, y0, x1, y1 = lrect((-20, -20, W + 20, H + 20), card, r_(T, 10.98, 0.55))
        return x0 + shift(T), y0, x1 + shift(T), y1
    s.box(A, 12.65, WHITE, card_r, name="Tarjeta", key="shp")
    lift = lambda T: 700 * (1 - r_(T, 11.0, 0.55))  # noqa: E731
    for colour, op in ((PNK, lambda T: 1 - r_(T, 11.28, 0.15)), (YEL, lambda T: r_(T, 11.28, 0.15))):
        o = lambda T, op=op: op(T) * (1.0 if T >= 11.05 else 0.0)  # noqa: E731
        ed = colour == YEL
        s.txt("TYPO", 11.0, 12.65, 424, colour, cy=900, dy=lift, dx=shift, op=o, editable=ed, name="Título")
        s.txt("TYPOGRAPHIC", 11.0, 12.65, 300, colour, cy=975, font=(M, 700), dy=lift, dx=shift, op=o, editable=ed,
              name="Subtítulo")
        s.txt("STORY", 11.0, 12.65, 440, colour, cy=1058, dy=lift, dx=shift, op=o, editable=ed, name="Título 2")
    s.txt("YOUR BRAND", 11.35, 12.65, 592, WHITE, cy=1728, font=(M, 700),
          dy=lambda T: 320 * (1 - r_(T, 11.35, 0.4)), dx=shift, name="Marca")
    # decorations
    s.deco("arc", A, 11.0, 778, 1310, 64, ORA, rot=-30)
    s.deco("plus", A, 11.0, 130, 1627, 64, GRN)
    for what, x, y, sz, c, at in (("ring", 80, 160, 26, WHITE, 11.5), ("ring", 980, 132, 30, RED, 11.4),
                                  ("arc", 660, 368, 52, WHITE, 11.6), ("ring", 240, 492, 32, GRN, 11.5),
                                  ("ring", 760, 492, 30, RED, 11.6), ("arc", 780, 1300, 60, AMB, 11.5),
                                  ("orect", 740, 1480, 70, WHITE, 11.7), ("plus", 128, 1620, 70, GRN, 11.4),
                                  ("ring", 88, 1800, 26, WHITE, 11.6), ("ring", 980, 1800, 30, RED, 11.7)):
        s.deco(what, at, 12.65, x, y, sz, c, rot=-40 if what == "arc" else 0.0, spin=8 if what == "arc" else 0.0)
    # the green wipe and scene 2
    s.box(12.3, B, GRN, lambda T: (-20, -20, lerp(-20, W + 20, r_(T, 12.3, 0.3, eio)), H + 20), key="top",
          name="Fondo verde", role="cover")
    k2 = "toptxt"
    s.box(12.5, B, PUR, lambda T: (-20 - 300 * (1 - r_(T, 12.5, 0.2)), -20, 104 - 300 * (1 - r_(T, 12.5, 0.2)), H + 20),
          key="top", name="Franja morada")
    s.txt("TYPO", 12.5, B, 2500, PUR, cx=90, cy=1000, rot=lambda T: -90.0, key=k2, editable=False,
          dx=lambda T: -300 * (1 - r_(T, 12.5, 0.2)), name="Letras de fondo")
    s.txt("T", 12.65, B, 470, WHITE, cx=540, cy=470, op=lambda T: r_(T, 12.65, 0.25, eio),
          dy=lambda T: -60 * (1 - r_(T, 12.65, 0.25)), key=k2, name="Letra")
    s.txt("TYPO", 12.55, B, 652, WHITE, cx=546, cy=932, dx=lambda T: 700 * (1 - r_(T, 12.55, 0.3)), key=k2,
          name="Título")
    s.txt("TYPOGRAPHIC", 12.75, B, 250, WHITE, cx=576, cy=1086, font=(M, 700), op=lambda T: r_(T, 12.75, 0.2),
          key=k2, name="Subtítulo")
    s.txt("STORY", 12.75, B, 352, WHITE, cx=576, cy=1150, op=lambda T: r_(T, 12.75, 0.2), key=k2, name="Título 2")
    sl = lambda T: -720 * (1 - r_(T, 12.85, 0.4))  # noqa: E731
    s.box(12.85, B, COR, lambda T: (200 + sl(T), 1260, 832 + sl(T), 1792), key="cover", name="Cuadro")
    for i, colour in enumerate((PUR, GRN)):
        s.box(12.85, B, colour, lambda T: (516 - 205 + sl(T), 1526 - 205, 516 + 205 + sl(T), 1526 + 205),
              rot=lambda T, i=i: 180 * i - 25 + 40 * (T - 12.85), key="cover", name="Aro", path=HALF)
    s.box(12.85, B, COR, lambda T: (516 - 95 + sl(T), 1526 - 95, 516 + 95 + sl(T), 1526 + 95), key="cover",
          name="Punto", kind="ellipse")
    return s.done()


# ====================================================================================================================
# 09 — COLOR / social (14.7 – 19.4)
# ====================================================================================================================

def color_social():
    A, B = 14.7, 19.4
    s = story("color", "Historia tipográfica: COLOR", "Typography story: COLOR", A, B, 16001, ["marco"], thumb=19.0)
    s.full(A, B, YEL)
    # bands that fall away: boundaries in fractions of H, tilted early on
    b1 = [(14.7, 0), (15.1, 0), (15.2, .2), (15.3, .42), (15.4, .6), (15.5, .67), (15.6, .75), (16.0, .92), (16.4, 1.05)]
    b2 = [(14.7, 0), (14.95, 0), (15.0, .2), (15.1, .3), (15.2, .5), (15.3, .62), (15.4, .75), (15.5, .8), (15.6, .83),
          (16.0, .94), (16.4, 1.06)]
    b3 = [(14.7, 0), (14.8, .35), (14.9, .42), (15.0, .5), (15.1, .7), (15.2, .75), (15.3, .8), (15.4, .88),
          (15.5, .9), (15.6, .9), (16.0, .96), (16.4, 1.07)]
    tilt = lambda T: curve(T, [(14.75, 30), (15.2, 18), (15.6, 0)])  # noqa: E731
    flat = lambda T: 0.0  # noqa: E731
    lin = lambda a, b, x: a + (b - a) * x  # noqa: E731
    lin1 = lambda x: x  # noqa: E731
    s.box(A, 16.5, PUR, lambda T: (-300, curve(T, b3, lin1) * H - 40, W + 300, H + 400), key="bg", name="Banda")
    for colour, pts in ((CYA, b3), (PNK, b2), (YEL, b1)):
        s.box(A, 16.5, colour, lambda T, pts=pts: (-300, curve(T, pts, lin1) * H - 520, W + 300,
                                                   curve(T, pts, lin1) * H), key="bg", name="Banda")
    _ = lin
    # the COLOR block (scaled about its frame centre when the wave comes)
    PX, PY = 546, 1020

    def blk(T):
        return lerp(1.0, 0.65, r_(T, 18.1, 0.45, eio))

    def at(x, y, T):
        k = blk(T)
        return PX + (x - PX) * k, PY + (y - PY) * k - 4 * r_(T, 18.1, 0.45, eio)

    def bx(r, T):
        x0, y0 = at(r[0], r[1], T)
        x1, y1 = at(r[2], r[3], T)
        return x0, y0, x1, y1
    word_s = lambda T: curve(T, [(14.78, 2.8), (14.9, 2.3), (15.0, 1.9), (15.2, 1.4), (15.4, 1.1), (15.6, 1.0)]) * blk(T)  # noqa: E731
    word_y = lambda T: curve(T, [(14.78, 380), (14.9, 520), (15.0, 700), (15.2, 1000), (15.4, 970), (15.6, 960)])  # noqa: E731
    s.txt("COLOR", 14.78, B, 760, PUR, cx=540, cy=960, s=word_s,
          dy=lambda T: (word_y(T) - 960) if T < 15.6 else at(540, 960, T)[1] - 960,
          rot=tilt, name="Título")
    s.bar(15.55, B, PUR, lambda T: bx((160, 1078, lerp(160, 920, r_(T, 15.55, 0.25)), 1098), T))
    s.txt("COLORFUL STORIES", 16.0, B, 740, PUR, cy=1168, font=(M, 700), op=lambda T: r_(T, 16.0, 0.2),
          s=blk, dy=lambda T: at(540, 1168, T)[1] - 1168, name="Subtítulo")
    th = 18
    for (a, r) in ((16.0, (lambda T: (lerp(992, 100, r_(T, 16.0, 0.35)), 780, 992, 780 + th))),
                   (16.0, (lambda T: (992 - th, 780, 992, lerp(780, 1260, r_(T, 16.0, 0.3))))),
                   (16.15, (lambda T: (100, 1260 - th, lerp(100, 992, r_(T, 16.15, 0.35)), 1260))),
                   (16.15, (lambda T: (100, lerp(1260, 780, r_(T, 16.15, 0.3)), 100 + th, 1260)))):
        s.bar(a, B, PUR, lambda T, r=r: bx(r(T), T), name="Marco")
    # decorations
    for what, x, y, sz, c, a in (("ring", 760, 1528, 44, RED, 16.3), ("cross", 768, 1632, 30, "#2B4DB8", 16.4),
                                 ("arc", 640, 1630, 34, ORA, 16.4), ("plus", 140, 1600, 60, GRN, 16.6),
                                 ("cross", 932, 300, 26, RED, 16.5)):
        s.deco(what, a, B, x, y, sz, c, rot=30 if what == "arc" else 0.0)
    s.box(16.95, B, WHITE, lambda T: (868, 88, 972, lerp(88, 760, r_(T, 16.95, 0.6))), layers=outline(WHITE, 9),
          key="deco", name="Rectángulo")
    s.deco("ring", 17.3, B, 920, 172, 44, ORA)
    s.deco("sq", 17.6, B, 772, 228, 40, CYA)
    s.deco("sq", 17.7, B, 772, 400, 40, "#4B2FE0")
    # the cyan wave with the giant «social», then «social» in purple
    rise = lambda T: 1000 * (1 - r_(T, 17.65, 0.8, eio))  # noqa: E731
    s.box(17.65, B, CYA, lambda T: (-20, 1080 + rise(T), W + 20, H + 20), key="shp", name="Ola")
    s.txt("social", 17.65, B, 1700, CYA, cx=640, cy=820, font=(M, 700), dy=rise, key="big", editable=False,
          name="Letras de fondo")
    s.txt("social", 18.05, B, 912, PUR, cx=544, cy=1560, font=(M, 700),
          dy=lambda T: 420 * (1 - r_(T, 18.05, 0.45, eio)), key="toptxt", name="Palabra")
    return s.done()


# ====================================================================================================================
# 08 — YOUR BRAND / STORIES (19.4 – 24.9)
# ====================================================================================================================

def stories():
    A, B = 19.4, 24.9
    s = story("stories", "Historia tipográfica: STORIES", "Typography story: STORIES", A, B, 16002, ["letra gigante"],
              thumb=24.5)
    lin1 = lambda x: x  # noqa: E731
    s.full(A, 20.05, PUR)
    s.txt("N", A, 20.05, 2200, PNK, cx=540, cy=1000, dx=lambda T: lerp(1500, -1700, r_(T, 19.45, 0.6, lin1)),
          key="big", editable=False, name="Letra gigante")
    s.full(20.0, 22.8, CYA, key="bg")
    cols = [YEL, COR, GRN, PUR, YEL, CYA, GRN, YEL, COR, PUR]
    for i, c in enumerate(cols):
        x = 80 + i * 150
        go = lambda T: 600 - 2200 * r_(T, 20.0, 0.7, lin1)  # noqa: E731
        s.box(20.0, 20.7, c, lambda T, x=x, i=i, go=go: (x + go(T), -20, x + 70 + 20 * (i % 3) + go(T), H + 20),
              key="shp", name="Raya")
    s.txt("S", 20.15, 20.7, 1700, PUR, cx=540, cy=980, dx=lambda T: lerp(1400, -1400, r_(T, 20.15, 0.5, lin1)),
          key="txt", editable=False, name="Letra gigante")
    lab = [(20.6, (486, 100, 594, 1820)), (20.7, (324, 326, 810, 1632)), (20.8, (216, 576, 864, 1402)),
           (20.9, (160, 700, 920, 1220)), (21.0, (140, 770, 940, 1150)), (21.4, (160, 864, 928, 1052))]

    def wipe(T):
        return curve(T, [(22.12, W + 40), (22.3, 600), (22.5, 300), (22.65, -140)])

    def out(T):
        return -0.6 * (W + 40 - wipe(T))

    def lab_r(T):
        x0, y0, x1, y1 = (curve(T, [(t_, r[i]) for t_, r in lab]) for i in range(4))
        return x0 + out(T), y0, x1 + out(T), y1
    s.box(20.6, 22.8, PUR, lab_r, key="fr", name="Etiqueta")
    s.txt("YOUR BRAND", 20.65, 22.8, 580, WHITE, cy=960, dx=out, key="toptxt", name="Marca")
    for what, x, y, sz, c, a in (("plus", 132, 1620, 70, GRN, 21.5), ("cross", 820, 1300, 24, YEL, 21.6),
                                 ("arc", 860, 500, 40, YEL, 21.7), ("cross", 960, 1740, 26, WHITE, 21.7),
                                 ("plus", 470, 430, 50, GRN, 21.8)):
        def r(T, x=x, y=y, sz=sz, a=a):
            k = r_(T, a, 0.2)
            return x - sz / 2 * k + out(T), y - sz / 2 * k, x + sz / 2 * k + out(T), y + sz / 2 * k
        s.box(a, 22.8, c, r, key="deco", name="Adorno", path={"plus": PLUS, "cross": CROSS, "arc": ARC}[what])
    # the push: a green bar, then purple with giant pink letters
    s.box(22.1, B, PUR, lambda T: (wipe(T) + 130, -20, W + 640, H + 20), key="top", name="Fondo morado", role="cover")
    s.box(22.1, 22.9, GRN, lambda T: (wipe(T), -20, wipe(T) + 140, H + 20), key="top", name="Barra")
    letters = [("N", 22.3, 22.85, 1900, 760), ("O", 22.75, 23.4, 2000, 700), ("T", 23.3, 24.0, 1500, 600), ("R", 23.9, B, 2000, -40)]
    for ch, a, b, wd, lx in letters:
        last = ch == "R"

        def dx(T, a=a, b=b, last=last):
            v = 1500 * (1 - r_(T, a, 0.35)) - 60 * (T - a)
            if not last:
                v -= 1500 * r_(T, b - 0.3, 0.3, lambda q: clamp(q) ** 2)
            return v
        s.txt(ch, a, b, wd, PNK, cx=lx, cy=980, dx=dx, key="toptxt", editable=False,
              name="Letra gigante")
    s.txt("STORIES", 22.6, B, 640, WHITE, cy=960, dx=lambda T: 800 * (1 - r_(T, 22.6, 0.45)), key="toptxt",
          name="Título")
    s.txt("MODERN AND COLOR STORY", 22.65, B, 600, WHITE, cy=1052, font=(M, 700),
          dx=lambda T: 800 * (1 - r_(T, 22.65, 0.45)), key="toptxt", name="Subtítulo")
    for what, x, y, sz, c, a in (("plus", 480, 448, 70, GRN, 22.5), ("arc", 660, 380, 56, WHITE, 22.55),
                                 ("arc", 900, 420, 56, WHITE, 22.6), ("arc", 272, 208, 56, AMB, 22.5),
                                 ("arc", 792, 1288, 56, AMB, 22.6), ("plus", 132, 1620, 70, GRN, 22.55),
                                 ("cross", 1012, 1744, 50, WHITE, 22.6), ("plus", 950, 1690, 28, WHITE, 22.65)):
        s.deco(what, a, B, x, y, sz, c, rot=200 if what == "arc" else 0.0, spin=10 if what == "arc" else 0.0)
    s.bar(22.6, B, WHITE, lambda T: (964, 200, 972, lerp(200, 300, r_(T, 22.6, 0.3))), key="deco")
    return s.done()


# ====================================================================================================================
# 07 — NO PLUGINS (24.9 – 29.5)
# ====================================================================================================================

def no_plugins():
    A, B = 24.9, 29.5
    s = story("no-plugins", "Historia tipográfica: NO PLUGINS", "Typography story: NO PLUGINS", A, B, 16003,
              ["rectángulos"], thumb=28.6)
    s.full(A, 26.1, WHITE)
    s.full(25.95, B, PUR)
    nest = [(YEL, 24.95, (68, 108, 1028, 1808), (-80, -140, 1160, 2060)),
            (CYA, 25.15, (120, 208, 960, 1700), (-40, -100, 1120, 2020)),
            (PUR, 25.35, (228, 400, 860, 1512), (20, 60, 1060, 1860)),
            (PNK, 25.55, (488, 852, 600, 1060), (54, 154, 1026, 1766))]
    for colour, a, rest, big in nest:
        last = colour == PNK

        def r(T, a=a, rest=rest, big=big, last=last):
            k = r_(T, a, 0.45)
            cx, cy = 540, 960
            x0, y0, x1, y1 = (cx + (rest[0] - cx) * k, cy + (rest[1] - cy) * k, cx + (rest[2] - cx) * k,
                              cy + (rest[3] - cy) * k)
            g = r_(T, 25.72, 0.3, eio)
            x0, y0, x1, y1 = lrect((x0, y0, x1, y1), big, g)
            if last:
                up = r_(T, 26.0, 0.6, eio)
                x0, x1 = lerp(x0, -20, up), lerp(x1, W + 20, up)
                y0, y1 = lerp(y0, -20, up), lerp(y1, -10, up)
            return x0, y0, x1, y1
        s.box(a, 26.7 if last else 26.1, colour, r, key="shp", name="Rectángulo")
    faint = [fill(WHITE, 0.2), no_stroke()]
    for i in range(6):
        s.txt("NO PLUGINS", 25.85, B, 1010, WHITE, cy=60 + 400 * i, sp=0.08, layers=faint, editable=False,
              op=lambda T: r_(T, 25.85, 0.2), dy=lambda T: -55 * (T - 25.85), key="txt", name="Fila")
    ly = lambda T: curve(T, [(25.8, 960), (26.95, 960), (27.35, 356)])  # noqa: E731
    ls = lambda T: curve(T, [(25.75, 0.25), (26.0, 0.5), (26.3, 0.85), (27.6, 1.0)])  # noqa: E731

    def lab_box(T):
        k, cy = ls(T), ly(T)
        return 540 - 384 * k, cy - 114 * k, 540 + 384 * k, cy + 114 * k
    s.box(25.75, B, YEL, lab_box, key="fr", name="Etiqueta")
    s.txt("NO PLUGINS", 25.75, B, 616, PUR, cy=960, s=ls, dy=lambda T: ly(T) - 960, key="toptxt", name="Título")
    s.txt("SOCIAL STORIES", 26.15, B, 560, WHITE, cy=1110, font=(M, 700), op=lambda T: r_(T, 26.15, 0.2),
          dy=lambda T: ly(T) - 960, key="toptxt", name="Subtítulo")
    s.bar(26.3, B, YEL, lambda T: (168, ly(T) + 214, lerp(168, 920, r_(T, 26.3, 0.3)), ly(T) + 246), key="fr")
    # the cyan band with the giant yellow word (shown through a matte of the band)
    band_r = lambda T: (-20, lerp(H + 10, 1306, r_(T, 26.95, 0.65, eio)), W + 20, H + 20)  # noqa: E731
    s.box(26.95, B, CYA, band_r, key="top", name="Banda")
    mat = s.box(26.95, B, WHITE, band_r, key="mat", name="Mate")
    g = s.txt("GINS", 26.95, B, 2500, YEL, cx=-150, cy=1700, dx=lambda T: 40 * (T - 26.95),
              dy=lambda T: 600 * (1 - r_(T, 26.95, 0.65, eio)), key="toptxt", editable=False, name="Letras gigantes")
    matte(g, mat)
    for what, x, y, sz, c, a in (("cross", 400, 724, 26, WHITE, 26.6), ("cross", 300, 1060, 22, "#2B2BA8", 26.8),
                                 ("cross", 230, 1060, 22, RED, 26.9)):
        s.deco(what, a, B, x, y, sz, c, drift=(0, -20))
    s.box(26.7, B, WHITE, lambda T: (368, 1120 - 30 * (T - 26.7), lerp(368, 680, r_(T, 26.7, 0.3)),
                                     1176 - 30 * (T - 26.7)), layers=outline(WHITE, 6), key="deco", name="Rectángulo")
    s.deco("ring", 26.8, B, 400, 1148, 30, RED, drift=(0, -30))
    for i, c in enumerate((CYA, "#4B2FE0", YEL)):
        s.deco("sq", 27.0 + 0.08 * i, B, 440 + 80 * i, 1226, 30, c, drift=(0, -30))
    return s.done()


def polyshape(s, t0, t1, colour, pts, k=None, key="shp", name="Forma", dxy=None):
    """A filled polygon given in story px, scaled by k(T) about its centre and moved by dxy(T)."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    path = poly([((x - x0) / (x1 - x0) * 100, (y - y0) / (y1 - y0) * 100) for x, y in pts])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def r(T):
        kk = k(T) if k else 1.0
        ox, oy = dxy(T) if dxy else (0.0, 0.0)
        return (cx + (x0 - cx) * kk + ox, cy + (y0 - cy) * kk + oy, cx + (x1 - cx) * kk + ox, cy + (y1 - cy) * kk + oy)
    return s.box(t0, t1, colour, r, key=key, name=name, path=path)


def line_at(s, t0, t1, colour, p0, p1, width, at=None, n=0.3, key="deco", name="Línea"):
    """A straight stroke from p0 to p1 that draws itself from p0 at `at`."""
    at = t0 if at is None else at
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])

    def r(T):
        k = r_(T, at, n)
        cx, cy = p0[0] + (p1[0] - p0[0]) * k / 2, p0[1] + (p1[1] - p0[1]) * k / 2
        return cx - ln * k / 2, cy - width / 2, cx + ln * k / 2, cy + width / 2
    return s.box(t0, t1, colour, r, rot=lambda T: ang, key=key, name=name)


# ====================================================================================================================
# 06 — BRAND (29.5 – 34.6); the reference word «ENVATO» becomes «BRAND»
# ====================================================================================================================

def brand():
    A, B = 29.5, 34.6
    s = story("brand", "Historia tipográfica: BRAND", "Typography story: BRAND", A, B, 16004, ["letra a"], thumb=33.5)
    s.full(A, 30.6, COR)
    s.full(30.45, B, YEL)
    rot = lambda T: curve(T, [(A, 0.0), (30.45, 90.0)], eo)  # noqa: E731
    thick = lambda T: curve(T, [(A, 1040), (30.45, 1260)])  # noqa: E731
    s.box(A, 30.6, YEL, lambda T: (540 - 1700, 960 - thick(T) / 2, 540 + 1700, 960 + thick(T) / 2), rot=rot,
          key="bg", name="Banda")
    # the coral box: a line that opens, then follows the word to the top left
    box = [(30.75, (330, 955, 970, 965)), (30.9, (194, 900, 1026, 1020)), (31.0, (194, 538, 842, 1382)),
           (31.45, (170, 170, 370, 770))]
    s.box(30.75, B, COR, lambda T: tuple(curve(T, [(t_, r[i]) for t_, r in box]) for i in range(4)), key="txt",
          name="Caja")
    ws = lambda T: curve(T, [(31.05, 1.0), (31.5, 0.31)])  # noqa: E731
    s.txt("BRAND", A, B, 1680, WHITE, cx=520, cy=960, rot=rot, s=ws, key="toptxt", name="Marca",
          dx=lambda T: lerp(0, 270 - 520, r_(T, 31.05, 0.45, eio)), dy=lambda T: lerp(0, 470 - 960, r_(T, 31.05, 0.45, eio)))
    # the big letter A in shapes
    shapes = [(GRN, [(784, 0), (1080, 0), (1080, 660)], 31.15), (GRN, [(624, 170), (790, 570), (544, 570), (544, 360)], 31.25),
              (GRN, [(544, 760), (870, 760), (950, 960), (544, 960)], 31.3), (PUR, [(544, 960), (1080, 960), (1080, 1360), (544, 1130)], 31.3),
              (PNK, [(0, 960), (200, 960), (150, 1090), (0, 1090)], 31.2), (PNK, [(460, 960), (544, 960), (544, 1360), (270, 1360)], 31.25),
              (PNK, [(0, 1270), (70, 1270), (40, 1360), (0, 1360)], 31.3)]
    for colour, pts, a in shapes:
        polyshape(s, a, B, colour, pts, k=lambda T, a=a: r_(T, a, 0.3), key="shp", name="Letra A")
    rise = lambda T: 640 * (1 - r_(T, 31.0, 0.3))  # noqa: E731
    s.box(31.0, B, WHITE, lambda T: (-20, 1476 + rise(T), W + 20, H + 20), key="fr", name="Pie", role="backdrop")
    s.box(31.0, B, CYA, lambda T: (-20, 1360 + rise(T), W + 20, 1476 + rise(T)), key="fr", name="Franja", role="backdrop")
    s.txt("COLOR", 31.0, B, 680, CYA, cx=550, cy=1690, dy=rise, key="toptxt", name="Título")
    s.txt("create and colorful stories", 31.5, B, 770, WHITE, cx=562, cy=1418, font=(M, 700),
          op=lambda T: r_(T, 31.5, 0.2), key="toptxt", name="Subtítulo")
    s.box(31.6, B, WHITE, lambda T: (660, 624, 724, lerp(624, 984, r_(T, 31.6, 0.3))), layers=outline(WHITE, 6),
          key="deco", name="Rectángulo")
    for what, x, y, sz, c, a in (("ring", 692, 666, 30, RED, 31.8), ("sq", 776, 704, 36, CYA, 32.0),
                                 ("sq", 776, 794, 36, "#4B2FE0", 32.1), ("sq", 776, 876, 36, YEL, 32.2),
                                 ("cross", 606, 320, 22, PNK, 31.7), ("cross", 606, 512, 22, "#2B2BA8", 31.8),
                                 ("ring", 190, 1526, 30, RED, 31.7), ("cross", 190, 1590, 24, "#2B2BA8", 31.8),
                                 ("arc", 256, 1584, 24, ORA, 31.9), ("cross", 610, 1800, 22, LIME, 31.9),
                                 ("arc", 680, 1796, 22, "#2B2BA8", 32.0)):
        s.deco(what, a, B, x, y, sz, c, rot=90 if what == "arc" else 0.0)
    return s.done()


# ====================================================================================================================
# 05 — STORY / STORIES EASY PROJECT (34.6 – 39.4); «INSTA» becomes «STORY»
# ====================================================================================================================

def easy_project():
    A, B = 34.6, 39.4
    s = story("easy-project", "Historia tipográfica: STORIES EASY PROJECT", "Typography story: STORIES EASY PROJECT",
              A, B, 16005, ["píxeles"], thumb=39.0)
    s.full(A, 35.7, WHITE)

    def grow(a, b, size, aspect=1.8):
        def r(T):
            w = curve(T, [(a, 0.0), (b, size)], eo)
            return 540 - w / 2, 960 - w * aspect / 2, 540 + w / 2, 960 + w * aspect / 2
        return r
    s.box(A, 35.75, YEL, grow(34.55, 35.6, 2600), key="bg", name="Píxeles", path=STEP)
    s.box(34.85, 36.4 + 0.8, CYA, grow(34.85, 35.75, 2900), key="bg", name="Píxeles", path=STEP)
    s.full(35.55, 37.3, CYA, key="bg")
    ls = lambda T: lerp(0.15, 1.0, r_(T, 34.95, 0.6))  # noqa: E731
    down = lambda T: r_(T, 36.4, 0.3, eio)  # noqa: E731

    def lab(T):
        k = ls(T)
        x0, y0, x1, y1 = 540 - 332 * k, 960 - 136 * k, 540 + 332 * k, 960 + 136 * k
        return lrect((x0, y0, x1, y1), (195, 1400, 864, 1590), down(T))
    s.box(34.95, 37.35, YEL, lab, key="fr", name="Etiqueta", op=lambda T: r_(T, 36.42, 0.08))
    s.box(34.95, 36.6, PUR, lab, key="fr", name="Marco", layers=outline(PUR, 32), op=lambda T: 1 - r_(T, 36.45, 0.1))
    s.txt("STORY", 34.95, 37.35, 536, WHITE, cy=960, s=lambda T: ls(T) * lerp(1, 0.88, down(T)),
          dy=lambda T: lerp(0, 535, down(T)), key="toptxt", name="Título")
    s.box(36.35, 37.35, PUR, lambda T: (-20, -20, W + 20, curve(T, [(36.35, -20), (36.5, 864), (36.6, 1286), (36.8, 1536),
                                                                   (37.0, 1840), (37.1, H + 20)])),
          key="shp", name="Fondo morado")
    s.full(37.05, B, PUR, key="bg")
    s.txt("STORIES", 36.55, 37.35, 1000, YEL, cx=540, cy=560, rot=lambda T: -90.0,
          dy=lambda T: -900 * (1 - r_(T, 36.55, 0.45)), key="txt", name="Vertical")
    # second wipe: white and yellow pixels, then the purple card opens
    s.box(37.3, 38.6, WHITE, grow(37.3, 38.3, 3000, 1.4), key="top", name="Píxeles", path=STEP)
    s.box(37.4, 38.6, YEL, grow(37.4, 38.4, 2600, 1.4), key="top", name="Píxeles", path=STEP)
    card = [(37.5, (540, 960, 540, 960)), (37.6, (292, 480, 778, 1498)), (37.7, (281, 384, 810, 1536)),
            (37.8, (184, 230, 918, 1632)), (37.9, (151, 154, 929, 1728)), (38.0, (130, 96, 972, 1766)),
            (38.5, (32, 38, 1048, 1882)), (39.0, (-20, -20, W + 20, H + 20))]
    s.box(37.5, B, PUR, lambda T: tuple(curve(T, [(t_, r[i]) for t_, r in card]) for i in range(4)), key="top",
          name="Tarjeta")
    rise = lambda a: (lambda T: 520 * (1 - r_(T, a, 0.9)))  # noqa: E731
    s.txt("STORIES", 37.6, B, 600, WHITE, cy=812, dy=rise(37.6), key="toptxt", name="Título")
    s.txt("EASY", 37.7, B, 600, WHITE, cy=1020, dy=rise(37.7), key="toptxt", name="Título 2")
    s.txt("PROJECT", 37.8, B, 580, WHITE, cy=1160, dy=rise(37.8), key="toptxt", name="Título 3")
    s.box(37.9, B, WHITE, lambda T: (260, 1236 + rise(37.9)(T), lerp(260, 840, r_(T, 38.3, 0.3)), 1252 + rise(37.9)(T)),
          key="cover", name="Línea")
    s.box(38.2, B, WHITE, lambda T: (72, 132, lerp(72, 392, r_(T, 38.2, 0.3)), 192), layers=outline(WHITE, 6),
          key="cover", name="Rectángulo")
    s.box(38.3, B, WHITE, lambda T: (428, 1680, lerp(428, 748, r_(T, 38.3, 0.3)), 1740), layers=outline(WHITE, 6),
          key="cover", name="Rectángulo")
    for what, x, y, sz, c, a in (("ring", 100, 162, 26, RED, 38.4), ("sq", 148, 248, 34, CYA, 38.4),
                                 ("sq", 236, 248, 34, "#4B2FE0", 38.5), ("sq", 320, 248, 34, YEL, 38.6),
                                 ("arc", 660, 372, 50, WHITE, 38.5), ("sq", 496, 1632, 34, YEL, 38.5),
                                 ("sq", 580, 1632, 34, "#4B2FE0", 38.6), ("sq", 664, 1632, 34, CYA, 38.7),
                                 ("ring", 700, 1710, 26, RED, 38.6), ("plus", 136, 1620, 64, CYA, 38.5),
                                 ("arc", 780, 1292, 56, ORA, 38.6), ("cross", 856, 1790, 22, "#2B2BA8", 38.7)):
        s.deco(what, a, B, x, y, sz, c, rot=200 if what == "arc" else 0.0, spin=12 if what == "arc" else 0.0,
               key="cover")
    s.bar(38.5, B, WHITE, lambda T: (964, 200, 972, lerp(200, 300, r_(T, 38.5, 0.3))), key="cover")
    return s.done()


# ====================================================================================================================
# 04 — SOCIAL (39.4 – 45.1)
# ====================================================================================================================

def social():
    A, B = 39.4, 45.1
    s = story("social", "Historia tipográfica: SOCIAL", "Typography story: SOCIAL", A, B, 16006, ["tarjetas", "promoción"],
              thumb=44.5)
    s.full(A, B, COR)
    # spinning cards; the coral one ends covering the screen
    cards = [(GRN, A, 0.62, 1.5, -15, -110), (WHITE, A, 0.5, 1.4, -5, -70), (YEL, A, 0.2, 1.3, 40, -35),
             (COR, 39.6, 0.15, 1.08, 70, 0)]
    for colour, a, k0, k1, a0, a1 in cards:
        k = lambda T, a=a, k0=k0, k1=k1: curve(T, [(a, k0), (40.65, k1)], eo)  # noqa: E731
        rt = lambda T, a=a, a0=a0, a1=a1: curve(T, [(a, a0), (40.7, a1)], eo)  # noqa: E731
        s.box(a, 40.7 if colour != COR else B, colour,
              lambda T, k=k: (540 - W * k(T) / 2, 960 - H * k(T) / 2, 540 + W * k(T) / 2, 960 + H * k(T) / 2),
              rot=rt, key="shp", name="Tarjeta")
    kc = lambda T: curve(T, [(39.6, 0.15), (40.65, 1.0)], eo)  # noqa: E731
    shrink = lambda T: lerp(1.0, 0.505, r_(T, 41.2, 0.3, eio))  # noqa: E731
    s.txt("SOCIAL", 39.6, B, 840, WHITE, cy=960, s=lambda T: kc(T) * shrink(T),
          rot=lambda T: curve(T, [(39.6, 70), (40.7, 0)], eo), name="Título")
    # brackets
    th = 16
    br = [(41.2, lambda k: (248, 840, 264, 840 + 220 * k)), (41.25, lambda k: (248, 840, 248 + 152 * k, 856)),
          (41.3, lambda k: (248, 1044, 248 + 52 * k, 1060)), (41.2, lambda k: (816, 1060 - 220 * k, 832, 1060)),
          (41.25, lambda k: (832 - 152 * k, 1044, 832, 1060)), (41.3, lambda k: (832 - 52 * k, 840, 832, 856))]
    for a, f in br:
        s.bar(a, B, WHITE, lambda T, a=a, f=f: f(r_(T, a, 0.25)))
    _ = th
    s.txt("BIG PROMOTION", 41.4, B, 600, WHITE, cy=752, font=(M, 700), op=lambda T: r_(T, 41.4, 0.2),
          dy=lambda T: 40 * (1 - r_(T, 41.4, 0.3)), name="Subtítulo")
    py = lambda T: curve(T, [(41.4, 1170), (42.6, 1170), (43.3, 1784)])  # noqa: E731
    s.txt("BIG PROMOTION", 41.4, B, 608, WHITE, cy=1170, font=(M, 800), op=lambda T: r_(T, 41.4, 0.2),
          dy=lambda T: py(T) - 1170, key="toptxt", name="Subtítulo 2")
    # the band at the foot
    for colour, a, top in ((YEL, 42.4, 1596), (CYA, 42.55, 1604), (GRN, 42.75, 1612), (PUR, 42.9, 1620)):
        s.box(a, B, colour, lambda T, a=a, top=top: (-20, lerp(H + 10, top, r_(T, a, 0.6, eio)), W + 20, H + 20),
              key="top", name="Banda", role="backdrop")
    s.txt("SOCIAL MEDIA PLATFORM", 43.3, B, 600, WHITE, cy=1732, font=(M, 700), op=lambda T: r_(T, 43.3, 0.2),
          key="toptxt", name="Subtítulo 3")
    # decorations
    line_at(s, 41.5, B, WHITE, (144, 180), (440, 392), 14, n=0.3)
    line_at(s, 41.6, B, WHITE, (210, 110), (380, 232), 14, n=0.3)
    s.box(41.6, B, WHITE, lambda T: (888, 112, 960, lerp(112, 352, r_(T, 41.6, 0.3))), layers=outline(WHITE, 6),
          key="deco", name="Rectángulo")
    s.deco("zig", 41.7, B, 936, 1000, 56, WHITE, h=84)
    s.deco("ring", 41.6, B, 168, 936, 40, WHITE, width=6)
    rp = [(41.8, (90, 1830)), (42.6, (90, 1830)), (43.5, (516, 1584))]
    s.box(41.8, B, WHITE, lambda T: (curve(T, [(t_, p[0]) for t_, p in rp]) - 56 * r_(T, 41.8, 0.25),
                                     curve(T, [(t_, p[1]) for t_, p in rp]) - 56 * r_(T, 41.8, 0.25),
                                     curve(T, [(t_, p[0]) for t_, p in rp]) + 56 * r_(T, 41.8, 0.25),
                                     curve(T, [(t_, p[1]) for t_, p in rp]) + 56 * r_(T, 41.8, 0.25)),
          kind="ellipse", layers=outline(WHITE, 8), key="cover", name="Aro")
    return s.done()


# ====================================================================================================================
# 03 — B / BIG (45.1 – 50.4)
# ====================================================================================================================

def big():
    A, B = 45.1, 50.4
    s = story("big", "Historia tipográfica: BIG", "Typography story: BIG", A, B, 16007, ["letra gigante"], thumb=49.5)
    lin1 = lambda x: x  # noqa: E731
    s.full(A, 46.2, PNK)
    for i, colour in enumerate((GRN, YEL, CYA, PUR)):
        a = 45.25 + 0.1 * i
        last = colour == PUR

        def r(T, a=a, last=last):
            cx = curve(T, [(a, 2300), (a + 0.6, 540 if last else -900)], eo if last else lin1)
            w = 2700 if last else 1500
            return cx - w / 2, 960 - 1800, cx + w / 2, 960 + 1800
        s.box(a, 46.2 if not last else 46.0, colour, r, kind="ellipse", key="bg", name="Arco")
    s.full(45.75, 48.3, WHITE, key="bg")
    slide = lambda T: curve(T, [(45.7, 500), (46.0, 250), (47.9, -650)], lin1)  # noqa: E731
    s.txt("B", 45.7, 48.3, 2000, PUR, cx=50, cy=1000, s=lambda T: curve(T, [(45.7, 1.6), (46.05, 1.0)], eo),
          dx=slide, key="big", name="Letra gigante")
    s.box(45.2, 48.3, AMB, lambda T: (820 + slide(T) - 250, lerp(96, 96, 0), 875 + slide(T) - 250,
                                      lerp(96, 346, r_(T, 45.2, 0.25))), key="deco", name="Barra")
    s.box(A, 47.4, LIME, lambda T: (108, 1766, lerp(108, 918, r_(T, A, 0.3)), 1824), key="deco", name="Barra verde",
          op=lambda T: 1 - r_(T, 45.85, 0.1))
    lp = [(45.9, (885, 1747)), (47.4, (885, 1747)), (47.6, (1000, 1280)), (47.8, (880, 800)), (48.05, (160, 250))]
    s.box(45.9, 48.25, LIME, lambda T: (curve(T, [(t_, p[0]) for t_, p in lp]) - 50, curve(T, [(t_, p[1]) for t_, p in lp]) - 36,
                                        curve(T, [(t_, p[0]) for t_, p in lp]) + 50, curve(T, [(t_, p[1]) for t_, p in lp]) + 36),
          key="deco", name="Cuadro verde")
    # panels from the right: yellow, pink, purple
    for colour, pts, end in ((YEL, [(47.7, W + 20), (47.9, 788), (48.0, 162), (48.1, -20)], 48.3),
                             (PNK, [(47.85, W + 20), (48.0, 886), (48.1, 670), (48.2, -20)], 48.9),
                             (PUR, [(48.15, W + 20), (48.2, 1026), (48.3, 540), (48.4, 292), (48.5, 194), (48.6, 108),
                                    (48.7, 54), (48.8, -20)], B)):
        s.box(pts[0][0], end, colour, lambda T, pts=pts: (curve(T, pts), -20, W + 20, H + 20), key="top",
              name="Panel", role="cover")
    s.txt("BIG", 48.45, B, 480, AMB, cy=960, dx=lambda T: curve(T, [(48.45, 640), (48.7, 50), (49.0, 0)]),
          key="toptxt", name="Título")
    s.txt("COLORFUL STORY", 48.9, B, 460, AMB, cy=1088, font=(M, 700), op=lambda T: r_(T, 48.9, 0.2), key="toptxt",
          name="Subtítulo")
    for what, x, y, sz, c, a in (("ring", 72, 152, 30, WHITE, 48.6), ("ring", 88, 1792, 30, WHITE, 48.7),
                                 ("ring", 240, 492, 30, GRN, 48.6), ("ring", 820, 220, 56, WHITE, 48.7),
                                 ("ring", 820, 220, 26, PNK, 48.75), ("ring", 760, 492, 26, RED, 48.8),
                                 ("ring", 240, 1504, 30, AMB, 48.7), ("ring", 968, 1792, 28, RED, 48.8),
                                 ("ring", 980, 128, 26, RED, 48.7)):
        s.deco(what, a, B, x, y, sz, c, width=5, key="cover")
    s.deco("zig", 48.7, B, 260, 632, 50, WHITE, h=72, key="cover")
    for (r0, a) in (((728, 452, 792, 772), 48.6), ((248, 1120, 300, 1288), 48.7), ((672, 1440, 780, 1512), 48.8)):
        s.box(a, B, WHITE, lambda T, r0=r0, a=a: (r0[0], r0[1], r0[2], lerp(r0[1], r0[3], r_(T, a, 0.3))),
              layers=outline(WHITE, 5), key="cover", name="Rectángulo")
    line_at(s, 48.7, B, WHITE, (620, 1100), (832, 1240), 10, key="cover")
    line_at(s, 48.8, B, WHITE, (672, 1200), (800, 1288), 10, key="cover")
    s.deco("dot", 48.9, B, 740, 1476, 16, WHITE, key="cover")
    return s.done()


# ====================================================================================================================
# 02 — STORY on a colour grid (50.4 – 55.7); «INSTA» becomes «STORY»
# ====================================================================================================================

def grid():
    A, B = 50.4, 55.7
    s = story("grid", "Historia tipográfica: cuadrícula de colores", "Typography story: colour grid", A, B, 16008,
              ["cuadrícula"], thumb=55.0)
    s.full(A, 52.4, ORA)
    cols = [[COR, GRN], [YEL, PUR], [WHITE, CYA], [COR, YEL]]
    order = [50.45, 50.55, 50.6, 50.7, 50.75, 50.85, 50.9, 50.95]
    for r in range(4):
        for c in range(2):
            a = order[r * 2 + c]
            s.box(a, 52.4, cols[r][c], lambda T, r=r, c=c: (c * 540, r * 480, (c + 1) * 540, (r + 1) * 480),
                  op=lambda T, a=a: r_(T, a, 0.2), key="bg", name="Cuadro", role="cover")
    s.txt("STORY", 50.6, 52.4, 880, ORA, cy=960, sp=0.25, op=lambda T: r_(T, 50.6, 0.2), name="Título")
    # purple panel from the left with the boxed word
    px = lambda T: curve(T, [(51.75, 0), (51.9, 86), (52.0, 756), (52.1, 864), (52.25, W + 20)])  # noqa: E731
    s.box(51.75, B, PUR, lambda T: (-20, -20, px(T), H + 20), key="shp", name="Panel", role="cover")
    L = lambda T: lerp(1.0, 0.47, r_(T, 52.3, 0.6, eio))  # noqa: E731

    def lab(T):
        k = L(T)
        cx = min(540, px(T) - 485 * k) if T < 52.25 else 540
        return cx - 485 * k, 960 - 80 * k * 1.0 - 8, cx + 485 * k, 960 + 80 * k + 8
    lab_cx = lambda T: (lab(T)[0] + lab(T)[2]) / 2 - 540  # noqa: E731
    s.box(51.75, B, WHITE, lab, layers=outline(WHITE, 10), key="fr", name="Marco")
    s.box(52.3, B, WHITE, lab, op=lambda T: r_(T, 52.3, 0.12) * (1 - r_(T, 53.55, 0.2)), key="fr", name="Etiqueta")
    s.txt("STORY", 51.75, B, 860, WHITE, cy=960, sp=0.12, s=L, dx=lab_cx, op=lambda T: 1 - r_(T, 52.3, 0.12) + r_(T, 53.55, 0.2),
          key="toptxt", name="Título 2")
    s.txt("STORY", 52.3, 53.8, 860, PUR, cy=960, sp=0.12, s=L, op=lambda T: r_(T, 52.3, 0.12) * (1 - r_(T, 53.55, 0.2)),
          key="toptxt", editable=False, name="Título 2 (morado)")
    tiles = [(COR, (288, 592, 548, 819), 53.45), (GRN, (548, 592, 808, 819), 53.6), (YEL, (288, 819, 548, 1046), 53.7),
             (COR, (548, 819, 808, 1046), 53.75), (WHITE, (288, 1046, 548, 1272), 53.85), (CYA, (548, 1046, 808, 1272), 53.9)]
    for colour, r0, a in tiles:
        s.box(a, B, colour, lambda T, r0=r0: r0, op=lambda T, a=a: r_(T, a, 0.2), key="shp", name="Cuadro")
    sy = lambda T: curve(T, [(53.0, 1076), (53.8, 1076), (54.3, 1820)])  # noqa: E731
    s.txt("SOCIAL TYPO SCENES", 52.95, B, 812, WHITE, cy=1076, font=(M, 700), sp=0.08, op=lambda T: r_(T, 52.95, 0.2),
          s=lambda T: lerp(0.75, 1.0, r_(T, 53.8, 0.5)), dy=lambda T: sy(T) - 1076, key="toptxt", name="Subtítulo")
    for colour, a in ((CYA, 53.85), (GRN, 53.95), (PNK, 54.05), ("#E26B5D", 54.15)):
        s.box(a, B, colour, lambda T, a=a: (-20, lerp(H + 10, 1720, r_(T, a, 0.3, eio)), W + 20, H + 20),
              key="top", name="Banda", role="backdrop")
    ap = [(52.4, (848, 180, 876, 180)), (52.6, (848, 180, 876, 330)), (53.4, (848, 340, 876, 640)),
          (54.0, (212, 320, 240, 620))]
    s.box(52.4, B, AMB, lambda T: tuple(curve(T, [(t_, p[i]) for t_, p in ap]) for i in range(4)), key="deco",
          name="Barra")
    lp = [(52.4, (640, 780, 640, 820)), (52.6, (640, 780, 860, 820)), (53.5, (720, 780, 820, 820)),
          (54.5, (760, 772, 832, 848))]
    s.box(52.4, B, LIME, lambda T: tuple(curve(T, [(t_, p[i]) for t_, p in lp]) for i in range(4)), key="deco",
          name="Cuadro verde")
    for what, x, y, sz, c, a in (("arc", 652, 352, 40, "#B8B8F0", 53.6), ("sq", 220, 1460, 24, CYA, 54.6),
                                 ("sq", 220, 1520, 24, "#4B2FE0", 54.7), ("sq", 220, 1584, 24, "#9090A0", 54.8),
                                 ("plus", 132, 1620, 64, CYA, 53.5), ("arc", 780, 1300, 50, AMB, 53.4)):
        s.deco(what, a, B, x, y, sz, c, rot=200 if what == "arc" else 0.0)
    s.bar(53.0, B, WHITE, lambda T: (968, 200, 974, lerp(200, 300, r_(T, 53.0, 0.3))), key="deco")
    return s.done()


# ====================================================================================================================
# 01 — AWESOME / R (55.7 – 62.7)
# ====================================================================================================================

def awesome():
    A, B = 55.7, 62.7
    s = story("awesome", "Historia tipográfica: AWESOME", "Typography story: AWESOME", A, B, 16009,
              ["franjas", "letra gigante"], thumb=62.0)
    lin1 = lambda x: x  # noqa: E731
    s.full(A, 57.5, WHITE)
    O = lambda T: curve(T, [(55.72, 1960), (55.8, 1400), (56.0, 634), (56.2, 300), (56.6, 60), (57.0, 0)], eo)  # noqa: E731
    ts = [(57.0, 57.7, 58.0, 58.1, 58.2, 58.3, 58.4, 58.5, 58.6, 58.7, 58.8, 58.9, 59.0, 59.2)]
    _ = ts
    bands = [(PUR, 0, [(57.0, 0), (57.7, -300)]),
             (CYA, 240, [(57.0, 240), (57.7, 0), (58.0, -300)]),
             (YEL, 560, [(57.0, 560), (57.7, 384), (58.0, 0), (58.1, -300)]),
             (COR, 868, [(57.0, 868), (57.7, 768), (58.0, 346), (58.1, 0), (58.2, -290)]),
             (WHITE, 1188, [(57.0, 1188), (57.7, 1152), (58.0, 806), (58.1, 634), (58.2, 288), (58.3, 0), (58.4, -200)]),
             (GRN, 1480, [(57.0, 1480), (57.7, 1440), (58.0, 1248), (58.1, 1114), (58.2, 883), (58.3, 672), (58.4, 192),
                          (58.5, 0), (59.0, -60)]),
             (PNK, 1720, [(57.0, 1720), (57.7, 1690), (58.0, 1632), (58.1, 1594), (58.2, 1478), (58.3, 1382), (58.4, 1152),
                          (58.5, 960), (58.6, 672), (58.7, 442), (58.8, 192), (58.9, 96), (59.0, 58), (59.2, -20)])]
    for i, (colour, top0, pts) in enumerate(bands):
        def r(T, i=i, top0=top0, pts=pts):
            y = top0 + O(T) * (1 + 0.1 * i) if T < 57.0 else curve(T, pts, lin1)
            return -20, y, W + 20, H + 20
        s.box(55.72, 59.3 if colour != PNK else 60.7, colour, r, key="bg", name="Franja", role="cover")
    # AWESOME with its open frame, rising out of the pink, later pushed down by the R
    ay = lambda T: curve(T, [(58.15, 1800), (58.4, 1290), (58.6, 1090), (59.0, 950), (59.95, 950), (60.1, 1160),  # noqa: E731
                             (60.2, 1440), (60.5, 1572)])
    hh = lambda T: lerp(100, 92, r_(T, 60.0, 0.5))  # noqa: E731
    s.txt("AWESOME", 58.15, B, 680, WHITE, cx=520, cy=950, dy=lambda T: ay(T) - 950, key="toptxt", name="Título")
    fx1 = lambda T: lerp(688, 940, r_(T, 60.0, 0.5))  # noqa: E731
    fx2 = lambda T: lerp(928, 940, r_(T, 60.0, 0.5))  # noqa: E731
    bars = [lambda T: (120, ay(T) - hh(T), fx1(T), ay(T) - hh(T) + 10), lambda T: (120, ay(T) - hh(T), 130, ay(T) + hh(T)),
            lambda T: (120, ay(T) + hh(T) - 10, fx2(T), ay(T) + hh(T)),
            lambda T: (fx2(T) - 10, ay(T) - hh(T), fx2(T), ay(T) + hh(T))]
    for f in bars:
        s.bar(58.15, B, WHITE, f, key="cover", name="Marco")
    # the yellow sweep and the coral ground
    yt = [(59.35, H + 10), (59.5, 1248), (59.6, 864), (59.7, 576), (59.8, 384), (59.9, 288), (60.0, 192), (60.3, 58),
          (60.6, -40)]
    yb = [(59.55, H + 10), (59.7, 1728), (59.8, 960), (59.9, 576), (60.0, 384), (60.3, 192), (60.6, -20)]
    s.box(59.35, 60.7, YEL, lambda T: (-20, curve(T, yt, lin1), W + 20, H + 20), key="shp", name="Barrido")
    s.box(59.55, B, COR, lambda T: (-20, curve(T, yb, lin1), W + 20, H + 20), key="shp", name="Fondo coral",
          role="cover")
    # the R rises from behind the frame (a matte above the frame's top edge)
    mat = s.box(59.95, B, WHITE, lambda T: (-20, -20, W + 20, ay(T) - hh(T)), key="mat", name="Mate")
    R = s.txt("R", 59.95, B, 820, WHITE, cx=530, cy=874, dy=lambda T: curve(T, [(59.95, 760), (60.55, 0)], eo),
              name="Letra")
    matte(R, mat)
    s.txt("TYPOGRAPHIC STORIES", 60.45, B, 828, WHITE, cy=1432, font=(M, 700), op=lambda T: r_(T, 60.45, 0.2),
          name="Subtítulo")
    rp = [(58.6, (152, 1572, 36)), (59.9, (152, 1572, 36)), (60.5, (512, 1588, 52))]

    def ring_r(T):
        x, y, rr = (curve(T, [(t_, p[i]) for t_, p in rp]) for i in range(3))
        rr *= r_(T, 58.6, 0.25)
        return x - rr, y - rr, x + rr, y + rr
    s.box(58.6, B, WHITE, ring_r, kind="ellipse", layers=outline(WHITE, 7), key="deco", name="Aro")
    line_at(s, 58.5, B, WHITE, (200, 100), (380, 232), 12)
    line_at(s, 58.55, B, WHITE, (140, 208), (440, 400), 12)
    for (r0, a) in (((888, 112, 952, 352), 58.5), ((140, 272, 168, 472), 58.6)):
        s.box(a, B, WHITE, lambda T, r0=r0, a=a: (r0[0], r0[1], r0[2], lerp(r0[1], r0[3], r_(T, a, 0.3))),
              layers=outline(WHITE, 5), key="deco", name="Rectángulo")
    for what, x, y, sz, c, a in (("sq", 104, 300, 16, CYA, 58.7), ("sq", 104, 352, 16, "#4B2FE0", 58.75),
                                 ("sq", 104, 400, 16, ORA, 58.8), ("ring", 96, 932, 40, WHITE, 60.4),
                                 ("dot", 430, 760, 10, RED, 58.8), ("dot", 432, 790, 10, "#4B2FE0", 58.85)):
        s.deco(what, a, B, x, y, sz, c, width=5)
    s.deco("zig", 58.7, B, 928, 992, 50, WHITE, h=72)
    return s.done()


TEMPLATES = [typo, color_social, stories, no_plugins, brand, easy_project, social, big, grid, awesome]
