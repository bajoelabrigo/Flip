"""INSTAGRAM folder video 57447063.mp4 as Stock templates (ig9-*). See docs/plan-instagram.md.

57447063.mp4 (960×540 at 25 fps, 30 s): five grey / black / red typographic stories shown side by side, then one by
one (the story is 216×384 px there, x 372 y 78; laid out ×5 on 1080×1920). Each story comes in behind a panel that
wipes in from the left, then builds with type: letter tiles that fall into a row, giant cut letters, a wall of
turned letters, a red band that turns level, a vertical word in a drawn frame. Moves copied from 10 fps sheets
(times below are frames at 29.97 fps from the start of each story's wipe). The brand word in big type is a neutral
editable word («TYPOGRAPHY», «STORIES») and the address is «www.yourwebsite.com». Kit de Instagram; ids `ig9-*`,
order 16200-. Study notes in tienda/plantillas/estudio-57447063/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed (S.frame). The helpers
below (wipe, drawn frames, words placed by their letters) are shared with templates_ig10 and templates_ig12.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import tall
from templates_ig1 import Story as _Story
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, rot_pt, shadow
from templates_yp4 import art_except

W, H = 1080, 1920
WHITE, BLACK = "#FFFFFF", "#000000"
GREY, DARK, RED, G17, INK, LABEL = "#CFC8C7", "#120C02", "#FF1800", "#171717", "#141414", "#C9C7C5"
URB = "Urbanist"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
               (900, "Black")):
    f6._FILES[(URB, _w)] = f"fonts.extra/fonts/urbanist/Urbanist-{_f}.ttf"
URL = "www.yourwebsite.com"
LOREM = ["Lorem ipsum dolor sit amet, consectetur adipiscing elit,", "sed do eiusmod tempor incididunt ut labore",
         "et dolore magna aliqua."]


# --- easing and tables ---------------------------------------------------------------------------------------------

def ko(fr, at, n, p=3.0):
    """0 → 1 from frame at over n frames, easing out (power p)."""
    x = min(1.0, max(0.0, (fr - at) / max(1e-6, n)))
    return 1 - (1 - x) ** p


def ki(fr, at, n, p=3.0):
    x = min(1.0, max(0.0, (fr - at) / max(1e-6, n)))
    return x ** p


def lerp(a, b, t):
    return a + (b - a) * t


def table(pts):
    """fr → value, linear between the (frame, value) points, held outside them."""
    pts = sorted(pts)

    def f(fr):
        if fr <= pts[0][0]:
            return pts[0][1]
        for (a, va), (b, vb) in zip(pts, pts[1:]):
            if fr <= b:
                return va + (vb - va) * (fr - a) / max(1e-6, b - a)
        return pts[-1][1]
    return f


def spline(pts):
    """fr → tuple, a Catmull-Rom curve through (frame, (values…)) points, held outside them."""
    pts = sorted(pts)

    def f(fr):
        if fr <= pts[0][0]:
            return pts[0][1]
        if fr >= pts[-1][0]:
            return pts[-1][1]
        i = max(j for j in range(len(pts) - 1) if pts[j][0] <= fr)
        a, b = pts[i], pts[i + 1]
        p0 = pts[i - 1][1] if i > 0 else a[1]
        p3 = pts[i + 2][1] if i + 2 < len(pts) else b[1]
        t = (fr - a[0]) / max(1e-6, b[0] - a[0])
        t2, t3 = t * t, t * t * t
        return tuple(0.5 * (2 * q1 + (-q0 + q2) * t + (2 * q0 - 5 * q1 + 4 * q2 - q3) * t2 + (-q0 + 3 * q1 - 3 * q2 + q3) * t3)
                     for q0, q1, q2, q3 in zip(p0, a[1], b[1], p3))
    return f


def dur_for(entrance_frames, hold=2.4):
    e = entrance_frames / FPS
    return round(e + hold + e / EXIT, 1)


def wipe(fr, at=0, n=36):
    """The right edge of a panel that wipes in from the left (all the stories of the pack come in this way)."""
    return W * ko(fr, at, n)


# --- the story ------------------------------------------------------------------------------------------------------

class Story(_Story):
    """ig1's story (photo slots with mattes, bars, words) plus drawn frames, words placed letter by letter, turned
    words and a black cover for the wipe."""

    def frame_lines(self, name, colour, rect, th, drawn, start="tr"):
        """A frame of stroke th inside rect(fr) = (x0, y0, x1, y1) that draws itself clockwise from the corner
        `start` (tl, tr, br, bl); drawn(fr) = px of the outline drawn so far."""
        sides = ["top", "right", "bottom", "left"]
        first = {"tl": 0, "tr": 1, "br": 2, "bl": 3}[start]
        order = sides[first:] + sides[:first]

        def side_rect(side, d, x0, y0, x1, y1):
            if side == "top":  # left → right
                return x0, y0, x0 + d, y0 + th
            if side == "right":  # top → bottom
                return x1 - th, y0, x1, y0 + d
            if side == "bottom":  # right → left
                return x1 - d, y1 - th, x1, y1
            return x0, y1 - d, x0 + th, y1  # left: bottom → top

        def length(side, x0, y0, x1, y1):
            return x1 - x0 if side in ("top", "bottom") else y1 - y0

        for i, side in enumerate(order):
            def r(fr, u, i=i, side=side):
                x0, y0, x1, y1 = rect(fr)
                before = sum(length(s, x0, y0, x1, y1) for s in order[:i])
                d = max(0.0, min(length(side, x0, y0, x1, y1), drawn(fr) - before))
                if d <= 0.01:
                    return x1, y1, x1, y1
                return side_rect(side, d, x0, y0, x1, y1)
            self.rect(f"{name} ({i + 1})", solid(colour), r,
                      op=lambda fr, u, i=i, side=side: 1.0 if drawn(fr) > 0.5 else 0.0)

    def cover(self, colour=BLACK, at=0, n=36):
        """The page outside the story while its panel wipes in from the left (drawn on top of everything)."""
        c = self.rect("Fondo (cortina)", solid(colour), lambda fr, u: (wipe(fr, at, n) - 1, -10, W + 10, H + 10),
                      op=lambda fr, u: 1.0 if wipe(fr, at, n) < W - 1 else 0.0)
        return c

    def line(self, content, ink, family, weight, colour, name, geom=None, align="center", reveal=None, shift=None,
             op=None, rot=None, layers=None, editable=True, spacing=0.0):
        """A one-line text at ink = (x0, caps top, x1, caps bottom), its box kept about as wide as the words."""
        c = self.say(content, ink, family, weight, colour, name, align=align, layers=layers, reveal=reveal,
                     shift=shift, editable=editable)
        st = c["textStyle"]
        st["wordWrap"] = False
        if spacing:
            st["letterSpacing"] = spacing * st["pixelSize"]
        if geom:
            self.tmove(c, geom)
        if op:
            from scene import keys
            c["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr, u))), 4), "linear") for u, fr in self.each()])
        if rot:
            from scene import keys
            c["rotation"] = keys([(u, round(rot(fr, u), 3), "linear") for u, fr in self.each()])
        return c

    def matte(self, clip, name, r):
        """Show clip only inside rect r(fr) = (x0, y0, x1, y1) (a track matte, so it can turn and move freely)."""
        m = self.rect(name, solid(WHITE), r)
        clip["matte"] = {"clip": m["id"], "mode": "alpha"}
        return m


def word_metrics(word, family, weight, cap):
    """(size, ink width, [(x0, x1) of each letter from the ink's left]) of word whose capitals are cap px tall."""
    f = f6._font(family, weight)
    hb = f.getbbox("H")
    size = cap * 400 / (hb[3] - hb[1])
    bb = f.getbbox(word)
    sc = size / 400
    letters = []
    for i, ch in enumerate(word):
        adv = f.getlength(word[:i])
        b = f.getbbox(ch)
        letters.append(((adv + b[0] - bb[0]) * sc, (adv + b[2] - bb[0]) * sc))
    ink = (f.getlength(word[:-1]) + f.getbbox(word[-1])[2] - bb[0]) * sc
    return size, ink, letters


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"ig9-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels", "tipografía"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.5, 1))


def finish(t):
    return art_except(t, keep=("Fondo",))


def lorem(s, ys, widths, colour, cap, name="Texto", geom=None, op=None, family=URB, weight=700, cx=W / 2):
    out = []
    for i, (text, y, w) in enumerate(zip(LOREM, ys, widths)):
        out.append(s.line(text, (cx - w / 2, y - cap / 2, cx + w / 2, y + cap / 2), family, weight, colour,
                          name if i == 0 else f"{name} {i + 1}", geom=geom, op=op))
    return out


# ==================================================================================================================
# 1. TYPO: letter tiles tumble into a row, a frame draws itself above them and pushes them down, the title rises
def typo():
    D = dur_for(112)
    t = _p("typo", "Historia: TYPO en cuadros con marco", "Story: TYPO tiles with a drawn frame", 16200, D,
           ["letras", "marco", "gris"], thumb=round(D * 0.55, 1))
    s = Story(t, D)
    s.bg(BLACK)
    border = lambda fr: 36 * k(fr, 53, 12)  # noqa: E731  the dark edge that closes round the story
    s.bar("Fondo (marco)", G17, lambda fr, u: (0, 0, W, H))
    s.bar("Fondo (gris)", GREY, lambda fr, u: (border(fr), border(fr), W - border(fr), H - border(fr)))
    # The frame: top-right corner first, down, left, up, right; it slides down while drawn.
    top = table([(57, 105), (69, 105), (78, 201), (84, 360), (93, 405), (105, 423)])
    s.frame_lines("Marco", INK, lambda fr: (90, top(fr), 960, top(fr) + 762), 48,
                  table([(53, 0), (57, 150), (68, 1011), (78, 2940), (84, 3210), (93, 3264)]), start="tr")
    # The title and the address rise inside the frame.
    s.line("Typography", (291, 777, 771, 837), URB, 700, INK, "Título", reveal=lambda fr: (0, 700, W, 852),
           shift=lambda fr: (0.0, 90 * (1 - ko(fr, 90, 12))))
    s.line(URL, (233, 866, 847, 910), URB, 700, INK, "Web", reveal=lambda fr: (0, 852, W, 916),
           shift=lambda fr: (0.0, 60 * (1 - ko(fr, 100, 12))))
    # The tiles: T and Y come up from the lower left, P and O from the right; then they drop under the frame.
    paths = [spline([(8, (-150, 1060, -30)), (18, (45, 885, -6)), (24, (102, 939, 0)), (33, (189, 960, 0)),
                     (40, (195, 960, 0))]),
             spline([(10, (150, 1900, -45)), (18, (324, 1245, -20)), (24, (360, 1050, 6)), (33, (414, 966, -3)),
                     (40, (417, 960, 0))]),
             spline([(22, (1250, 1050, 25)), (33, (735, 960, 3)), (39, (672, 960, 1)), (50, (642, 960, 0))]),
             spline([(25, (1250, 560, 40)), (33, (984, 756, 15)), (39, (921, 891, 5)), (52, (867, 960, 0))])]
    firsts = (8, 10, 22, 25)
    for i, (ch, path) in enumerate(zip("TYPO", paths)):
        def pose(fr, i=i, path=path):
            x, y, r = path(fr)
            p = (fr - 63 - 3 * i) / 16
            y += 342 * k(fr, 63 + 3 * i, 16)
            r += -6 * math.sin(math.pi * min(1.0, max(0.0, p))) * (1 if i % 2 else -1) if 0 < p < 1 else 0.0
            return x, y, r
        vis = lambda fr, f0=firsts[i]: 1.0 if fr >= f0 else 0.0  # noqa: E731
        s.obj(f"Letra {i + 1} (cuadro)", solid(INK),
              lambda fr, u, pose=pose, vis=vis: (pose(fr)[0], pose(fr)[1], 180, 186, pose(fr)[2], vis(fr)))
        x0 = (195, 417, 642, 867)[i]
        s.line(ch, (x0 - 60, 960 - 55, x0 + 60, 960 + 55), URB, 600, WHITE, f"Letra {i + 1}",
               geom=lambda fr, u, pose=pose, vis=vis, x0=x0: (pose(fr)[0] - x0, pose(fr)[1] - 960, 1.0, pose(fr)[2],
                                                              vis(fr)))
    lorem(s, (1443, 1476, 1510), (852, 774, 330), INK, 19, geom=lambda fr, u: (0, 460 * (1 - ko(fr, 62, 28)), 1, 0, 1.0),
          op=lambda fr, u: 1.0 if fr > 62 else 0.0)
    s.cover()
    return finish(t)


# 2. Giant cut letters: the dark panel wipes in, grey falls from the top over the letters, grey blocks slide in
#    under them and close, the title rises into a frame that draws itself, the addresses rise, two lines draw
def giant_cut():
    D = dur_for(100)
    t = _p("letras-cortadas", "Historia: palabra gigante cortada y tres enlaces",
           "Story: giant cut word and three links", 16201, D, ["letras", "enlaces", "gris", "negro"],
           thumb=round(D * 0.55, 1))
    s = Story(t, D)
    s.bg(BLACK)
    s.bar("Fondo (panel)", DARK, lambda fr, u: (0, 0, W, H))
    s.bar("Fondo (gris)", GREY, lambda fr, u: (0, 0, W, 960 * k(fr, 3, 19)))
    # The giant word (its O G R in the window), sliding left as it comes, cut at 966 by the grey blocks.
    word, cap, top = "TYPOGRAPHY", 400, 650
    size, ink, lets = word_metrics(word, URB, 800, cap)
    gx = 600 - (lets[4][0] + lets[4][1]) / 2  # the G's centre at x 600 at rest
    big = s.line(word, (gx, top, gx + ink, top + cap), URB, 800, DARK, "Palabra gigante",
                 geom=lambda fr, u: (180 * (1 - ko(fr, 12, 36, 2.0)), 0, 1.0, 0, 1.0))
    s.matte(big, "Palabra gigante (máscara)", lambda fr, u: (0, 0, W, H))  # stays inside the story in a wide video
    for i in range(3):
        s.bar(f"Fondo (bloque {i + 1})", GREY,
              lambda fr, u, i=i: (lambda L: (L, 966, L + 309 + 51 * k(fr, 36 + 6 * i, 16), 1311))(
                  360 * i + (W + 60 - 360 * i) * (1 - ko(fr, 14 + 8 * i, 34))))
    s.bar("Fondo (línea)", DARK, lambda fr, u: (W - W * ko(fr, 72, 9), 984, W, 1008), op=lambda fr, u: 1.0 if fr > 72 else 0)
    s.bar("Fondo (línea 2)", DARK, lambda fr, u: (0, 597, W * ko(fr, 84, 15), 618), op=lambda fr, u: 1.0 if fr > 84 else 0)
    s.line("Typography", (234, 318, 906, 400), URB, 700, INK, "Título", reveal=lambda fr: (0, 280, W, 428),
           shift=lambda fr: (0.0, 120 * (1 - ko(fr, 36, 14))))
    s.frame_lines("Marco", INK, lambda fr: (147, 246, 978, 465), 15,
                  table([(40, 0), (48, 180), (54, 714), (63, 1850), (75, 2100)]), start="tr")
    lorem(s, (510, 540, 570), (750, 681, 300), INK, 13, geom=lambda fr, u: (0, 27 * (1 - ko(fr, 45, 10)), 1, 0, 1.0),
          op=lambda fr, u: k(fr, 45, 9))
    for i, yf in enumerate((1404, 1551, 1695)):
        y = lambda fr, i=i, yf=yf: yf + (2000 - yf) * (1 - ko(fr, 50 + 5 * i, 30))  # noqa: E731
        s.bar(f"Enlace {i + 1} (fondo)", GREY, lambda fr, u, y=y: (171, y(fr) - 38, 906, y(fr) + 38))
        s.line(URL, (205, yf - 24, 875, yf + 24), URB, 700, DARK, f"Enlace {i + 1}",
               geom=lambda fr, u, y=y, yf=yf: (0, y(fr) - yf, 1.0, 0, 1.0))
    s.cover(at=-3)
    return finish(t)


# 3. A wall of giant turned letters scrolling on red, a grey label pops up with its shadow, the address drops
def red_wall():
    D = dur_for(56, 3.0)
    t = _p("letras-rojas", "Historia: muro de letras giradas sobre rojo", "Story: wall of turned letters on red",
           16202, D, ["letras", "rojo", "etiqueta"], thumb=round(D * 0.55, 1))
    s = Story(t, D)
    s.bg(RED)
    # Five lines of «STORIES STORIES» turned 45°, a line every 620 px, sliding along themselves.
    cap = 500
    word = "STORIES STORIES STORIES"
    size, ink, lets = word_metrics(word, URB, 800, cap)
    a = math.radians(45)
    for j in range(-2, 3):
        cx = W / 2 - 620 * j * math.sin(a) + (j * 731) % 1500 * math.cos(a) - 750 * math.cos(a)
        cy = H / 2 + 620 * j * math.cos(a) + (j * 731) % 1500 * math.sin(a) - 750 * math.sin(a)
        s.line(word, (cx - ink / 2, cy - cap / 2, cx + ink / 2, cy + cap / 2), URB, 800, BLACK,
               f"Fondo (letras {j + 3})", geom=lambda fr, u: (4.5 * fr * math.cos(a), 4.5 * fr * math.sin(a), 1.0,
                                                             45.0, 1.0))
    # The label: grey box with a black shadow, growing from the left of the middle.
    g = lambda fr: k(fr, 15, 25)  # noqa: E731

    def box(dx, dy):
        def r(fr, u):
            sc = max(1e-3, g(fr))
            cx, cy = 540 - 120 * (1 - sc) + dx * sc, 958 + dy * sc
            return cx - 440 * sc, cy - 132 * sc, cx + 440 * sc, cy + 132 * sc
        return r
    vis = lambda fr, u: 1.0 if g(fr) > 0.005 else 0.0  # noqa: E731
    s.bar("Etiqueta (sombra)", BLACK, box(22, 22), op=vis)
    s.bar("Etiqueta", GREY, box(0, 0), op=vis)

    def inside(cy):
        return lambda fr, u: (-120 * (1 - g(fr)) + (540 * g(fr) - 540), (958 + (cy - 958) * g(fr)) - cy,
                              max(1e-3, g(fr)), 0, vis(fr, u))
    s.line("STORIES", (256, 894, 850, 962), URB, 800, INK, "Título", geom=inside(928))
    s.line("Typography", (380, 984, 700, 1024), URB, 700, INK, "Subtítulo", geom=inside(1004))
    # The address on a grey tab drops from the top; the lines rise from below.
    drop = lambda fr, u: -125 * (1 - ko(fr, 40, 12))  # noqa: E731
    s.bar("Web (fondo)", GREY, lambda fr, u: (166, -20 + drop(fr, u), 924, 110 + drop(fr, u)))
    s.line(URL, (180, 36, 904, 78), URB, 700, INK, "Web", geom=lambda fr, u: (0, drop(fr, u), 1, 0, 1.0))
    lorem(s, (1184, 1220, 1257), (908, 726, 394), WHITE, 22,
          geom=lambda fr, u: (0, 760 * (1 - ko(fr, 30, 22)), 1, 0, 1.0))
    s.cover()
    return finish(t)


# 4. A red band turns level and stretches, the giant word inside slides left, the address drops, the lines rise
#    into a red frame that draws itself
def red_band():
    D = dur_for(60, 2.6)
    t = _p("banda-roja", "Historia: banda roja con palabra gigante", "Story: red band with a giant word", 16203, D,
           ["banda", "rojo", "negro", "letras"], thumb=round(D * 0.55, 1))
    s = Story(t, D)
    s.bg(G17)
    p = lambda fr: ko(fr, 2, 30)  # noqa: E731

    def band(fr):
        q = p(fr)
        return (540 - 220 * (1 - q), 957 + 140 * (1 - q), 1006 + 520 * (1 - k(fr, 45, 22)), 1074, 70 * (1 - q))
    vis = lambda fr: 1.0 if fr >= 2 else 0.0  # noqa: E731
    s.obj("Banda", solid(RED), lambda fr, u: band(fr) + (vis(fr),))
    # The word turns with the band about its centre and slides left inside it (8.8 px a frame).
    word, cap = "TYPOGRAPHY", 640
    size, ink, lets = word_metrics(word, URB, 800, cap)
    gx = 300 - (lets[4][0] + lets[4][1]) / 2  # the G's centre at x 300 when the band has turned level
    wcx = gx + ink / 2

    def wgeom(fr, u):
        bx, by, bw, bh, r = band(fr)
        slide = 260 - 8.8 * max(0.0, fr - 10)
        x, y = rot_pt(wcx + slide - 540 + bx, by, r, bx, by)
        return x - wcx, y - 957, 1.0, r, vis(fr)
    c = s.line(word, (gx, 957 - cap / 2, gx + ink, 957 + cap / 2), URB, 800, G17, "Palabra gigante", geom=wgeom)
    m = s.obj("Banda (máscara)", solid(WHITE), lambda fr, u: band(fr) + (vis(fr),))
    c["matte"] = {"clip": m["id"], "mode": "alpha"}
    s.line(URL, (225, 128, 876, 172), URB, 700, RED, "Web", reveal=lambda fr: (0, 0, W, 200),
           shift=lambda fr: (0.0, -260 * (1 - ko(fr, 50, 12))))
    s.frame_lines("Marco", RED, lambda fr: (105, 1615, 1015, 1840), 25,
                  table([(42, 0), (46, 280), (55, 1800), (64, 2270)]), start="tr")
    lorem(s, (1702, 1732, 1762), (690, 600, 325), RED, 14,
          geom=lambda fr, u: (0, 90 * (1 - ko(fr, 34, 12)), 1, 0, 1.0), op=lambda fr, u: k(fr, 34, 6))
    s.cover()
    return finish(t)


# 5. The red panel falls away, a tall frame draws itself, the vertical word rises in it, a red ribbon drops, the tag,
#    the address and the lines come
def vertical_word():
    D = dur_for(66)
    t = _p("palabra-vertical", "Historia: palabra vertical en marco con cinta roja",
           "Story: vertical word in a frame with a red ribbon", 16204, D, ["vertical", "marco", "cinta", "gris"],
           thumb=round(D * 0.55, 1))
    s = Story(t, D)
    s.bg(GREY)
    s.bar("Fondo (rojo)", RED, lambda fr, u: (0, 1920 * ko(fr, 6, 30), W, H + 10),
          op=lambda fr, u: 1.0 if ko(fr, 6, 30) < 0.999 else 0.0)
    fx0, fy0, fx1, fy1 = 330, 249, 750, 1665
    s.frame_lines("Marco", INK, lambda fr: (fx0, fy0, fx1, fy1), 15,
                  table([(22, 0), (25, 105), (34, 531), (43, 3042), (49, 3627), (55, 3672)]), start="br")
    # «STORIES» reads upwards, rising into the frame.
    c = s.line("STORIES", (540 - 540, 960 - 75, 540 + 540, 960 + 75), URB, 800, INK, "Título",
               geom=lambda fr, u: (0, 1150 * (1 - ko(fr, 40, 21)), 1.0, -90.0, 1.0))
    s.matte(c, "Título (máscara)", lambda fr, u: (fx0 + 15, fy0 + 15, fx1 - 15, fy1 - 15))
    # The ribbon with its notch drops from the top.
    s.obj("Cinta", solid(RED), lambda fr, u: (540, 105 - 230 * (1 - ko(fr, 46, 10)), 408, 210, 0, 1.0),
          path="M 0 0 L 100 0 L 100 100 L 50 64 L 0 100 Z")
    rise = lambda fr: 120 * (1 - ko(fr, 46, 14))  # noqa: E731
    s.bar("Etiqueta", RED, lambda fr, u: (285, 1731 + rise(fr), 795, 1800 + rise(fr)),
          op=lambda fr, u: 1.0 if fr > 46 else 0.0)
    s.line("Typography", (395, 1748, 685, 1784), URB, 600, WHITE, "Subtítulo",
           geom=lambda fr, u: (0, rise(fr), 1, 0, 1.0 if fr > 46 else 0.0))
    # The address up the left of the frame, the lines up its right (they read upwards too).
    w = s.line(URL, (280 - 300, 1350 - 22, 280 + 300, 1350 + 22), URB, 700, INK, "Web",
               geom=lambda fr, u: (0, 620 * (1 - ko(fr, 58, 12)), 1.0, -90.0, 1.0 if fr > 58 else 0.0))
    s.matte(w, "Web (máscara)", lambda fr, u: (230, 0, 330, fy1))
    for i, (text, wd) in enumerate(zip(LOREM, (1200, 1080, 520))):
        x = 789 + 36 * i
        cy = 255 + wd / 2
        ln = s.line(text, (x - wd / 2, cy - 12, x + wd / 2, cy + 12), URB, 700, INK, "Texto" if i == 0 else
                    f"Texto {i + 1}", geom=lambda fr, u, x=x, cy=cy: (-140 * (1 - ko(fr, 61, 14)), 0, 1.0, -90.0, 1.0 if fr > 61 else 0.0))
        s.matte(ln, f"Texto {i + 1} (máscara)", lambda fr, u: (fx1, 0, W, H))
    s.cover()
    return finish(t)


TEMPLATES = [typo, giant_cut, red_wall, red_band, vertical_word]
