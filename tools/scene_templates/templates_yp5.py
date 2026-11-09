"""YOUTUBE PACK video 5 as Stock templates (yp5-*). See docs/plan-youtube-pack.md.

The pieces of «pack youtube 5.mp4» (a YouTube promo pack, 960×540 at 30 fps, laid out at 1920×1080): titles,
subscribe lower thirds, channel openers, end screens, social bars, quotes, call-out lines and counters, most of them
shown in 2×2 grids (each quarter is one piece, scaled ×4). Each was studied on 10 fps sheets (study notes in
tienda/plantillas/estudio-pack-youtube-5/NOTAS.md). Pieces that sit over footage have no background (transparent)
and are laid out where they sit; end screens and openers bring their own background and photo slots.

Each piece plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed (templates_tit_h.S).
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import wide
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, TRIANGLE, S, arc, fill, grad, lin, poly, regular, ring, rot_pt, shadow  # noqa: F401
from templates_tit_i import bg  # noqa: F401
from templates_tit_j import photo  # noqa: F401
from llt_motion import frames_of
from scene import keys, tanim

M = "Montserrat"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
f6._FILES[(M, 401)] = "fonts.basic/fonts/montserrat/Montserrat-Italic.ttf"
f6._FILES[("Lato", 700)] = "fonts.basic/fonts/lato/Lato-Bold.ttf"
f6._FILES[("Lato", 900)] = "fonts.basic/fonts/lato/Lato-Black.ttf"
f6._FILES[(M, 801)] = "fonts.basic/fonts/montserrat/Montserrat-ExtraBoldItalic.ttf"
WHITE, BLACK, RED = "#FFFFFF", "#000000", "#F2283C"
YTRED = "#FF0000"


DARK, LIGHT = "#D40000", "#F0251C"  # the pack's two-tone play button (left half darker)
TWO = [__import__("scene").gradient([(0.0, DARK), (0.5, DARK), (0.5, LIGHT), (1.0, LIGHT)], angle=0),
       __import__("scene").no_stroke()]


def ytb(s, name, geom, w, h, body=None, tri=WHITE, tri_op=None, tri_rot=None, radius=0.24, wscale=None):
    """The pack's play button: geom(fr, u) = (cx, cy, scale, rot, opacity); tri_op / tri_rot(fr) for the triangle."""
    ws = wscale or (lambda fr: 1.0)
    s.obj(name, body or TWO, lambda fr, u: (lambda g: (g[0], g[1], w * g[2] * ws(fr), h * g[2], g[3], g[4]))(geom(fr, u)),
          radius=h * radius, base=(w, h))

    def tg(fr, u):
        cx, cy, sc, rot, op = geom(fr, u)
        ox, oy = rot_pt(cx + w * 0.03 * sc, cy, rot, cx, cy)
        r = rot + (tri_rot(fr) if tri_rot else 0)
        return ox, oy, w * 0.3 * sc * ws(fr), h * 0.4 * sc, r, op * (tri_op(fr) if tri_op else 1)
    s.obj(f"{name} (play)", solid(tri), tg, path=TRIANGLE)


# --- engine features used by the second pass (2026-11-09): holes, 3D turns, masks, patterns -------------------------
def track_of(s, clip):
    return next(tr for tr in s.t.tracks if clip in tr.clips)


def new_clips(s, fn):
    """Runs fn() and returns the clips it added (one per new track)."""
    n = len(s.t.tracks)
    fn()
    return [c for tr in s.t.tracks[n:] for c in tr.clips]


def per_frame(s, fn, ease="linear"):
    return keys([(u, round(fn(fr, u), 5), ease) for u, fr in s.each()])


def hole(s, clip, path=TRIANGLE, x=0.53, y=0.5, w=0.3, h=0.4, size=None):
    """Cuts `path` (0..100 box, laid on x, y, w, h of the clip's own box) out of a clip: an inverted mask, so what is
    behind shows through. size(fr, u) scales the hole (0 closes it)."""
    kf = None
    if size:
        kf = {"w": per_frame(s, lambda fr, u: w * size(fr, u)), "h": per_frame(s, lambda fr, u: h * size(fr, u))}
    s.t.mask(track_of(s, clip), clip, "path", x=x, y=y, w=w, h=h, pathData=path, invert=True,
             **({"keyframes": kf} if kf else {}))


def screen_mask(s, clip, box, rect, invert=False):
    """A rectangle mask on a clip laid out in box = (x0, y0, w, h) on screen, following rect(fr) = screen px."""
    bx, by, bw, bh = box
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u, fr in s.each():
        x0, y0, x1, y1 = rect(fr)
        mk["x"].append((u, ((x0 + x1) / 2 - bx) / bw, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - by) / bh, "linear"))
        mk["w"].append((u, max(0.0, x1 - x0) / bw, "linear"))
        mk["h"].append((u, max(0.0, y1 - y0) / bh, "linear"))
    s.t.mask(track_of(s, clip), clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1],
             h=mk["h"][0][1], invert=invert, keyframes={k_: keys(v) for k_, v in mk.items()})


def stripes_in_circle(n=22, width=0.42, steps=10):
    """Diagonal stripes («\\», n across) cut to the circle of a 100 box, as one path: a striped disc."""
    out = []
    p = 100.0 * math.sqrt(2) / n  # pitch measured across the stripes
    for j in range(-n, n + 1):
        # band between two lines x - y = c0 and x - y = c1 (45°), cut by the circle centred at (50, 50), r = 50
        c0, c1 = j * p, j * p + width * p
        pts = []
        for c, sign in ((c0, 1), (c1, -1)):
            # chord of x - y = c: points (50 + t + c/2, 50 + t - c/2), |(t + c/2, t - c/2)| <= 50
            half = 2500 - c * c / 4
            if half <= 0:
                pts = []
                break
            tmax = math.sqrt(half / 2)
            a, b = (-tmax, tmax) if sign > 0 else (tmax, -tmax)
            pts.append((50 + a + c / 2, 50 + a - c / 2))
            pts.append((50 + b + c / 2, 50 + b - c / 2))
        if len(pts) == 4:
            # arcs between the chords' ends so the band follows the circle
            def ang(pt):
                return math.atan2(pt[1] - 50, pt[0] - 50)

            def arc_pts(p0, p1):
                a0, a1 = ang(p0), ang(p1)
                d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
                return [(50 + 50 * math.cos(a0 + d * i / steps), 50 + 50 * math.sin(a0 + d * i / steps))
                        for i in range(1, steps)]
            ring_ = [pts[0], pts[1]] + arc_pts(pts[1], pts[2]) + [pts[2], pts[3]] + arc_pts(pts[3], pts[0])
            out.append(poly(ring_))
    return " ".join(out)


def dots_in_circle(n=34, size=0.42):
    """A grid of small squares (n across, `size` of the cell) inside the circle of a 100 box: a dotted disc."""
    cell = 100.0 / n
    out = []
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            if math.hypot(cx - 50, cy - 50) > 50 - cell * 0.6:
                continue
            r = cell * size / 2
            out.append(poly([(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]))
    return " ".join(out)


# Opaque 3D layers on screen together are depth-sorted by the engine; since engine 0109b a layer drawn later wins
# against one practically in its plane, so a glyph (after its card in track order) stays on top. Lifted 2 px too.
GLYPH_LIFT = 2.0


def card3d(s, name, geom, w, h, rx=None, ry=None, persp=1600, front=None, back=None, edge=None, radius=0.24,
           tri=True, depth=12.0, z=None):
    """A card turned in 3D by the engine: geom(fr, u) = (cx, cy, scale, rot, opacity); rx / ry(fr) in degrees.
    front: layers of the face (with a play-triangle hole when tri); back: layers seen when it faces away; edge: a
    copy `depth` px behind (+z comes toward the eye) that shows as the card's thickness while it turns; z(fr) moves
    the whole card in depth."""
    rx_ = rx or (lambda fr: 0.0)
    ry_ = ry or (lambda fr: 0.0)
    z_ = z or (lambda fr: 0.0)

    def facing(fr):
        return math.cos(math.radians(rx_(fr))) * math.cos(math.radians(ry_(fr))) >= 0

    def g(side):
        def f(fr, u):
            cx, cy, sc, rot, op = geom(fr, u)
            show = 1.0 if side is None else (1.0 if facing(fr) == side else 0.0)
            return cx, cy, w * sc, h * sc, rot, op * show
        return f
    clips = []
    if edge:
        c = s.obj(f"{name} (canto)", edge, g(None), radius=h * radius, base=(w, h))
        s.d3(c, rx=lambda fr, u: rx_(fr), ry=lambda fr, u: ry_(fr), z=lambda fr, u: z_(fr) - depth * geom(fr, u)[2],
             persp=persp)
        if tri:
            hole(s, c)
        clips.append(c)
    if back:
        c = s.obj(f"{name} (dorso)", back, g(False), radius=h * radius, base=(w, h))
        s.d3(c, rx=lambda fr, u: rx_(fr), ry=lambda fr, u: ry_(fr), z=lambda fr, u: z_(fr), persp=persp)
        clips.append(c)
    c = s.obj(name, front, g(True if back else None), radius=h * radius, base=(w, h))
    s.d3(c, rx=lambda fr, u: rx_(fr), ry=lambda fr, u: ry_(fr), z=lambda fr, u: z_(fr), persp=persp)
    if tri:
        hole(s, c)
    clips.append(c)
    return clips


def hatch(n=24, lean=0.6):
    """Diagonal stripes across a 100 box (n stripes), as one path."""
    step = 100.0 / n
    out = []
    for i in range(-2, n + 2):
        a = i * step
        pts = [(a, 100), (a + step / 2, 100), (a + step / 2 + 100 * lean / 4, 0), (a + 100 * lean / 4, 0)]
        pts = [(min(100.0, max(0.0, x)), y) for x, y in pts]
        if max(x for x, _ in pts) - min(x for x, _ in pts) > 0.01:
            out.append(poly(pts))
    return " ".join(out)


def pop(fr, at, n=6, over=0.12):
    """0 → 1 with a small overshoot (a pop)."""
    q = lin(fr, at, n)
    if q <= 0:
        return 0.0
    return min(1.0 + over, (1 + over) * math.sin(q * math.pi / 2)) if q < 0.7 else 1 + over * (1 - (q - 0.7) / 0.3)


def dur_for(entrance, hold=1.6):
    return round(entrance + hold + entrance / EXIT, 1)


def _p(id, es, en, order, dur, section, tags=(), thumb=None):
    return wide(f"yp5-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube"] + list(tags),
                thumb_at=round(thumb if thumb is not None else dur * 0.55, 1))


def words(line, x0, x1, family, weight, gap=" "):
    """Splits a line whose ink spans x0..x1 into one ink span per word (same font, spaces kept)."""
    f = f6._font(family, weight)
    parts = line.split(" ")
    total = f.getlength(line)
    out, pos = [], 0.0
    for i, w in enumerate(parts):
        a = f.getlength(" ".join(parts[:i]) + (gap if i else ""))
        b = a + f.getlength(w)
        out.append((w, x0 + (x1 - x0) * a / total, x0 + (x1 - x0) * b / total))
        pos = b
    return out


def zoom_about(ink, sc, px=960.0, py=540.0):
    cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
    return px + (cx - px) * sc - cx, py + (cy - py) * sc - cy


def qx(x):
    """A quarter's x (0..480 of its 960×540 source quarter) on the 1920 frame."""
    return x * 4


def drop_in(s, text, ink, at, dist, name="Título", family=M, weight=800, colour=WHITE, sc=None, n=6,
            align="center", layers=None):
    """A word that slides into place from dist px away (negative = from above), seen only past its caps edge
    (a mask on the side it comes from); sc(fr, u) zooms the whole thing about the frame centre."""
    x0, y0, x1, y1 = ink
    pad = 400
    rev = (lambda fr: (-pad, y0 - 2, 1920 + pad, 1080 + pad)) if dist < 0 else \
        (lambda fr: (-pad, -pad, 1920 + pad, y1 + 2))
    sh = lambda fr: (0.0, dist * (1 - k(fr, at, n)))  # noqa: E731
    c = s.say(text, ink, family, weight, colour, name, reveal=rev, shift=sh, align=align, layers=layers,
              op=lambda fr, u: 1.0 if fr >= at else 0.0)
    if sc:
        base = sh(s.frame(0.0))[1]  # the first key already holds the shift at u = 0
        s.tmove(c, lambda fr, u: (lambda z: (zoom_about(ink, z)[0], zoom_about(ink, z)[1] + sh(fr)[1] * z - base, z, 0,
                                             1.0 if fr >= at else 0.0))(sc(fr, u)))
    return c


# --- P. YOUTUBE PROMO PACK (55.4-60.1 s): the words drop in, a black box opens behind, PACK types; slow zoom out ---
def promo_pack():
    D = dur_for(1.3, 2.6)
    t = _p("promo-pack", "Título: YOUTUBE PROMO en caja negra", "Title: YOUTUBE PROMO in a black box", 12900, D,
           "titulos-estilo", ["caja", "negro"])
    s = S(t, D)
    sc = lambda fr, u: 1 - 0.09 * min(1.0, max(0.0, (u - 1.0) / 3.4))  # noqa: E731
    box = (296, 445, 1624, 568)
    s.obj("Caja", solid(BLACK), lambda fr, u: (960 + zoom_about(box, sc(fr, u))[0], 506.5 + zoom_about(box, sc(fr, u))[1],
                                               1328 * sc(fr, u), 123 * sc(fr, u) * k(fr, 31, 5), 0, 1))
    for i, (w, a, b) in enumerate(words("YOUTUBE PROMO", 350, 1570, M, 800)):
        drop_in(s, w, (a, 475, b, 560), 4 + 5 * i, -90, "Título" if i == 0 else "Título 2", weight=900, sc=sc)
    pk = (896, 604, 1024, 636)
    c = s.say("PACK", pk, M, 800, WHITE, "Texto",
              geom=lambda fr, u: (*zoom_about(pk, sc(fr, u)), sc(fr, u), 0, 1))
    s.typed(c, 31, stagger=0.03, duration=0.03)
    return t


def cross(s, name, cx, cy, size, at, colour=WHITE, w=5):
    for j, r in enumerate((45, -45)):
        s.obj(f"{name}" + (" b" if j else ""), solid(colour),
              lambda fr, u, r=r: (cx, cy, size * pop(fr, at), w, r, 1.0 if fr >= at else 0.0))


def diamond(s, name, cx, cy, size, at, colour=WHITE, w=4):
    s.obj(name, ring(colour, w), lambda fr, u: (cx, cy, size * pop(fr, at), size * pop(fr, at), 45,
                                                1.0 if fr >= at else 0.0), base=(size, size))


# --- G1 (13.9-18.0 s), 2×2 grid of play-button lower thirds ------------------------------------------------------
def big_live_story():
    """q1: a giant play button zooms down from the full frame, slides left spinning its triangle; the name slides
    out from behind it and a white bar with CHANNEL opens."""
    D = dur_for(1.5, 2.0)
    t = _p("big-live-story", "Tercio: botón de YouTube que se aleja y nombre", "Lower third: play button zooming down "
           "and a name", 12901, D, "lowerthirds", ["botón", "suscribirse"])
    s = S(t, D)
    sc = lambda fr: 1.15 + 14 * (1 - k(fr, 2, 13)) ** 2 - 0.15 * k(fr, 27, 12)  # noqa: E731
    cx = lambda fr: 960 - 470 * k(fr, 27, 12)  # noqa: E731
    s.say("BIG LIVE STORY", (640, 468, 1360, 540), M, 700, WHITE, align="left",
          reveal=lambda fr: (cx(fr) + 130 * sc(fr), 0, 1920, 1080), shift=lambda fr: (-700 * (1 - k(fr, 27, 12)), 0),
          op=lambda fr, u: 1.0 if fr >= 27 else 0.0)
    s.rect("Barra", solid(WHITE), lambda fr, u: (740, 556, 740 + 460 * k(fr, 33, 9), 612))
    s.say("CHANNEL", (830, 569, 1090, 599), M, 800, LIGHT, "Texto", reveal=lambda fr: (740, 0, 740 + 460 * k(fr, 33, 9), 1080))
    # while it is big, the triangle is a hole (the video shows through); it turns white as the button lands
    body = new_clips(s, lambda: ytb(s, "Botón", lambda fr, u: (cx(fr), 532 + 8 * (1 - k(fr, 27, 12)), sc(fr), 0,
                                                              1.0 if fr >= 2 else 0.0), 260, 184,
                                    tri_op=lambda fr: k(fr, 12, 4), tri_rot=lambda fr: 360 * k(fr, 27, 15)))[0]
    hole(s, body, size=lambda fr, u: 1.0 if fr < 17 else 0.0)
    return t


def travel_blog():
    """q2: a white pill rises, a red triangle drops above it; the pill turns into a red play button, a line draws
    under it and the name rises from the line as the button goes up."""
    D = dur_for(3.2, 1.6)
    t = _p("travel-blog", "Tercio: botón que sube y nombre", "Lower third: rising button and a name", 12902, D,
           "lowerthirds", ["botón"])
    s = S(t, D)
    up = lambda fr: 74 * k(fr, 84, 12)  # noqa: E731
    by = lambda fr: 1180 - 620 * k(fr, 2, 7) - up(fr)  # noqa: E731
    s.obj("Píldora", solid(WHITE), lambda fr, u: (714, by(fr), 148, 108, 0, 1.0 - k(fr, 51, 3)), radius=26)
    s.obj("Triángulo", solid(LIGHT), lambda fr, u: (714, -40 + 416 * k(fr, 12, 18) + 184 * k(fr, 48, 4), 40, 30, 90,
                                                   1.0 - k(fr, 50, 3)), path=TRIANGLE)
    ytb(s, "Botón", lambda fr, u: (714, by(fr), 1, 0, k(fr, 51, 3)), 148, 108)
    s.rect("Línea", solid(WHITE), lambda fr, u: (714 - 300 * k(fr, 84, 6), 622, 714 + 300 * k(fr, 84, 6), 628),
           op=lambda fr, u: 1 - k(fr, 93, 4))
    s.say("TRAVEL BLOG", (612, 548, 1312, 620), M, 900, WHITE, reveal=lambda fr: (0, 0, 1920, 622),
          shift=lambda fr: (0, 90 * (1 - k(fr, 87, 9))), op=lambda fr, u: 1.0 if fr >= 87 else 0.0)
    return t


def channel_name_tilted():
    """q3: a play button pops in the middle; it goes up-left and tilts while YOUTUBE CHANNEL zooms up, a striped
    red bar draws and NAME rises."""
    D = dur_for(3.2, 1.6)
    t = _p("channel-name", "Tercio: nombre del canal inclinado con rayas", "Lower third: tilted channel name with "
           "stripes", 12903, D, "lowerthirds", ["botón", "rayas"])
    s = S(t, D)
    tilt = lambda fr: -6 * k(fr, 66, 12)  # noqa: E731
    q = lambda fr: k(fr, 66, 15)  # noqa: E731
    ytb(s, "Botón", lambda fr, u: (960 - 396 * q(fr), 560 - 154 * q(fr), pop(fr, 16, 10), tilt(fr),
                                   1.0 if fr >= 16 else 0.0), 232, 172)
    ink = (340, 444, 1580, 532)
    z = lambda fr: 0.3 + 0.7 * k(fr, 68, 14)  # noqa: E731
    s.say("YOUTUBE CHANNEL", ink, M, 900, WHITE,
          geom=lambda fr, u: (*s.about(ink, 960, 488, z(fr), tilt(fr)), z(fr), tilt(fr), 1.0 if fr >= 68 else 0.0))
    for name, layers in (("Barra", solid(RED)), ("Barra (rayas)", solid(WHITE))):
        s.obj(name, layers, lambda fr, u: (*rot_pt(420 + 560 * k(fr, 80, 9), 594, tilt(fr), 960, 540),
                                           1120 * k(fr, 80, 9), 56, tilt(fr), 1.0),
              path=hatch(28) if "rayas" in name else None)
    nm = (800, 568, 1120, 632)
    s.say("NAME", nm, M, 900, WHITE, "Texto",
          geom=lambda fr, u: (*s.about(nm, 960, 540, 1, tilt(fr)), 1, tilt(fr), k(fr, 82, 4)))
    return t


def your_channel_label():
    """q4: a red label flies up turning, the play button pops above it, the name wipes in and crosses and diamonds
    pop around."""
    D = dur_for(2.5, 1.8)
    t = _p("your-channel-label", "Tercio: etiqueta roja con botón y destellos", "Lower third: red label with button and "
           "sparkles", 12904, D, "lowerthirds", ["botón", "etiqueta"])
    s = S(t, D)
    fly = lambda fr: 1 - k(fr, 3, 21)  # noqa: E731
    for name, layers, path in (("Etiqueta", solid(RED), None), ("Etiqueta (rayas)", solid(WHITE), hatch(40))):
        h, cy = (108, 646) if path is None else (14, 693)
        s.obj(name, layers, lambda fr, u, h=h, cy=cy: (*rot_pt(960, cy + 600 * fly(fr), 50 * fly(fr), 960, 646 + 600 * fly(fr)),
                                                       480, h, 50 * fly(fr), 1.0 if fr >= 3 else 0.0), path=path)
    s.say("YourChannel", (720, 616, 1200, 668), M, 700, WHITE, reveal=lambda fr: (960 - 260 * k(fr, 27, 9), 0, 960 + 260 * k(fr, 27, 9), 1080))
    ytb(s, "Botón", lambda fr, u: (960, 476, pop(fr, 27, 9), 0, 1.0 if fr >= 27 else 0.0), 216, 168)
    cross(s, "Cruz", 584, 500, 40, 66)
    cross(s, "Cruz 2", 1288, 500, 40, 69)
    cross(s, "Cruz 3", 616, 620, 24, 72)
    diamond(s, "Rombo", 1152, 568, 24, 70)
    diamond(s, "Rombo 2", 1048, 768, 30, 74)
    return t


HAND = poly([(34, 0), (50, 0), (50, 40), (88, 46), (96, 58), (90, 100), (30, 100), (4, 62), (14, 52), (34, 64)])
THUMB = poly([(0, 42), (24, 42), (24, 100), (0, 100), (0, 42), (30, 42), (48, 0), (62, 6), (58, 36), (100, 38),
              (96, 96), (30, 100)])
HORN = poly([(0, 34), (40, 34), (100, 0), (100, 100), (40, 66), (30, 66), (36, 100), (18, 100), (12, 66), (0, 66)])
BUBBLE = poly([(0, 0), (100, 0), (100, 78), (30, 78), (12, 100), (14, 78), (0, 78)])


def white_button(s, name, geom, w, h, red=LIGHT, tri_rot=None, wscale=None):
    """A white rounded box with a red play triangle (the pack's second button)."""
    ytb(s, name, geom, w, h, body=solid(WHITE), tri=red, tri_rot=tri_rot, wscale=wscale)


# --- G2 (18.0-22.1 s), 2×2 grid ---------------------------------------------------------------------------------
def click_channel():
    """q1: the play button drops in, a hand clicks it, a red bar wipes in with the name and CHANNEL rises."""
    D = dur_for(2.8, 1.6)
    t = _p("click-channel", "Tercio: clic en el botón y barra roja", "Lower third: click on the button and a red bar",
           12905, D, "lowerthirds", ["botón", "clic"])
    s = S(t, D)
    ytb(s, "Botón", lambda fr, u: (960, -100 + 540 * k(fr, 6, 15), 1 - 0.08 * math.sin(math.pi * lin(fr, 42, 4)), 0,
                                   1.0 if fr >= 12 else 0.0), 240, 176,
        tri_rot=lambda fr: 180 * k(fr, 54, 6) - 180 * k(fr, 60, 6))
    s.obj("Mano", solid(WHITE), lambda fr, u: (1150 - 70 * k(fr, 30, 12) + 10 * math.sin(math.pi * lin(fr, 42, 4)),
                                               700 - 170 * k(fr, 30, 12), 70, 92, -10, k(fr, 30, 3) * (1 - k(fr, 66, 4))),
          path=HAND)
    s.rect("Barra", solid(RED), lambda fr, u: (488, 552, 488 + 952 * k(fr, 63, 9), 644))
    s.say("YOUR YOUTUBE", (608, 572, 1320, 628), M, 900, WHITE, reveal=lambda fr: (488, 0, 488 + 952 * k(fr, 63, 9), 1080),
          shift=lambda fr: (-300 * (1 - k(fr, 63, 12)), 0))
    s.say("CHANNEL", (752, 652, 1172, 712), M, 800, WHITE, "Texto", reveal=lambda fr: (0, 646, 1920, 1080),
          shift=lambda fr: (0, -70 * (1 - k(fr, 75, 9))))
    return t


def triangle_box():
    """q2: a white play triangle grows, spins and drops into a white box; the box slides left and lets the name
    out; a small red pill pops."""
    D = dur_for(2.9, 1.6)
    t = _p("triangle-box", "Tercio: triángulo que se vuelve botón blanco", "Lower third: triangle turning into a white "
           "button", 12906, D, "lowerthirds", ["botón", "blanco"])
    s = S(t, D)
    cx = lambda fr: 960 - 278 * k(fr, 60, 18)  # noqa: E731
    s.obj("Triángulo", solid(WHITE), lambda fr, u: (968, 540, 70 * (0.4 + 0.6 * k(fr, 9, 27)), 84 * (0.4 + 0.6 * k(fr, 9, 27)),
                                                   200 * k(fr, 39, 6), (1.0 if fr >= 9 else 0) * (1 - k(fr, 44, 2))),
          path=TRIANGLE)
    white_button(s, "Botón", lambda fr, u: (cx(fr), 548 - 10 * k(fr, 45, 6), pop(fr, 45, 6), -12 * (1 - k(fr, 48, 6)),
                                            1.0 if fr >= 45 else 0.0), 260, 180)
    s.say("YourChannel", (848, 504, 1372, 564), M, 700, WHITE, align="left",
          reveal=lambda fr: (cx(fr) + 130, 0, 1920, 1080), shift=lambda fr: (-560 * (1 - k(fr, 60, 18)), 0),
          op=lambda fr, u: 1.0 if fr >= 60 else 0.0)
    s.obj("Píldora", solid(RED), lambda fr, u: (1300, 610, 120 * pop(fr, 81), 44 * pop(fr, 81), 0, 1.0 if fr >= 81 else 0.0),
          radius=8, base=(120, 44))
    for i, x in enumerate((1276, 1324)):
        s.obj(f"Ícono {i + 1}", solid(WHITE), lambda fr, u, x=x: (x, 610, 22 * pop(fr, 84), 22 * pop(fr, 84), 0,
                                                                 1.0 if fr >= 84 else 0.0),
              path=THUMB if i == 0 else regular(3, 90))
    return t


def doodle_channel():
    """q3: a white button pops, a red bar opens under it, the name types, and doodles (a thumb, a megaphone, chat
    bubbles) pop around."""
    D = dur_for(2.6, 1.6)
    t = _p("doodle-channel", "Tercio: botón blanco, barra roja y dibujos", "Lower third: white button, red bar and "
           "doodles", 12907, D, "lowerthirds", ["botón", "dibujos"])
    s = S(t, D)
    white_button(s, "Botón", lambda fr, u: (936, 386 + 160 * (1 - k(fr, 15, 18)), pop(fr, 15, 9), 0, 1.0 if fr >= 15 else 0.0),
                 248, 172)
    s.rect("Barra", solid(RED), lambda fr, u: (924 - 356 * k(fr, 48, 8), 500, 924 + 356 * k(fr, 48, 8), 620))
    c = s.say("YourChannel", (608, 528, 1228, 592), M, 700, WHITE)
    s.typed(c, 57, stagger=0.05, duration=0.03)
    s.obj("Pulgar", solid(WHITE), lambda fr, u: (640, 462, 70 * pop(fr, 69), 70 * pop(fr, 69), -10, 1.0 if fr >= 69 else 0.0),
          path=THUMB)
    s.obj("Megáfono", solid(WHITE), lambda fr, u: (1218, 438, 84 * pop(fr, 72), 66 * pop(fr, 72), -15, 1.0 if fr >= 72 else 0.0),
          path=HORN)
    for i, (x, y, r) in enumerate(((1000, 660, 0), (1060, 652, 180))):
        s.obj(f"Globo {i + 1}", ring(WHITE, 4), lambda fr, u, x=x, y=y, r=r, i=i: (
            x, y, 72 * pop(fr, 75 + 2 * i), 56 * pop(fr, 75 + 2 * i), r, 1.0 if fr >= 75 + 2 * i else 0.0), path=BUBBLE)
    return t


def stacked_channel():
    """q4: YOUR / YOUTUBE / CHANNEL zoom up from small, slightly tilted; three chat bubbles pop around."""
    D = dur_for(1.0, 2.6)
    t = _p("stacked-channel", "Tercio: nombre en tres líneas con globos", "Lower third: three-line name with chat "
           "bubbles", 12908, D, "lowerthirds", ["globos"])
    s = S(t, D)
    z = lambda fr: 0.15 + 0.85 * k(fr, 6, 12)  # noqa: E731
    for i, (word, ink) in enumerate((("YOUR", (768, 392, 1136, 488)), ("YOUTUBE", (680, 496, 1240, 600)),
                                     ("CHANNEL", (720, 604, 1192, 672)))):
        s.say(word, ink, M, 900, WHITE, ["Título", "Título 2", "Texto"][i],
              geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 540, z(fr), -3), z(fr), -3, 1.0 if fr >= 6 else 0.0))
    for i, (x0, y0, x1, y1, flip, at) in enumerate(((432, 392, 584, 464, 1, 15), (1252, 380, 1492, 452, 0, 18),
                                                    (1120, 752, 1328, 824, 1, 21))):
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        s.obj(f"Globo {i + 1}", solid(WHITE), lambda fr, u, cx=cx, cy=cy, w=w, h=h, at=at: (
            cx, cy, w * pop(fr, at), h * pop(fr, at), 0, 1.0 if fr >= at else 0.0), radius=h * 0.4, base=(w, h))
        for j in range(3):
            dx = (j - 1) * w * 0.22
            s.obj(f"Globo {i + 1} (punto {j + 1})", solid(RED), lambda fr, u, cx=cx, cy=cy, h=h, at=at, dx=dx: (
                cx + dx * pop(fr, at), cy, h * 0.3 * pop(fr, at + 3), h * 0.3 * pop(fr, at + 3), 0,
                1.0 if fr >= at + 3 else 0.0), kind="ellipse")
    return t


def shape_photo(s, sample, geom, shape="ellipse", name="Foto", label="Tu foto", op=None):
    """A photo slot over the whole frame cut to an ellipse (or rectangle) geom(fr, u) = (cx, cy, w, h)."""
    t = s.t
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, None, None, label=label)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(s.dur):
        cx, cy, w, h = geom(s.frame(u), u)
        mk["x"].append((u, cx / 1920, "linear"))
        mk["y"].append((u, cy / 1080, "linear"))
        mk["w"].append((u, max(1e-3, w / 1920), "linear"))
        mk["h"].append((u, max(1e-3, h / 1080), "linear"))
    t.mask(track, clip, shape, x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={kk: keys(v) for kk, v in mk.items()})
    if op:
        clip["opacity"] = keys([(u, round(op(s.frame(u), u), 4), "linear") for u in frames_of(s.dur)])
    return clip


def squares_row(n, size, step, offset=0.0, width=2400.0):
    """A path (0..100 box of width × size) of n squares `size` px every `step` px."""
    out = []
    for i in range(n):
        x = offset + i * step
        if 0 <= x and x + size <= width:
            out.append(poly([(x / width * 100, 0), ((x + size) / width * 100, 0), ((x + size) / width * 100, 100),
                             (x / width * 100, 100)]))
    return " ".join(out)


def circles_in(s, at=0, colours=(("#FF0000", 0, 9), ("#FF1A1A", 1, 10), ("#000000", 3, 7), ("#E60000", 3.5, 8),
                                  (WHITE, 5, 7)), cx=960, cy=540, reach=2300):
    """The pack's record transition: concentric discs grow from the centre one after another; the second is white
    with red diagonal stripes and the fourth red with a grid of dark dots (patterns cut to the circle, one path)."""
    for i, (colour, lag, n) in enumerate(colours):
        lag, n = 3 * lag, 3 * n  # given at 10 fps
        g = lambda fr, u, lag=lag, n=n: (cx, cy, reach * k(fr, at + lag, n), reach * k(fr, at + lag, n), 0,  # noqa: E731
                                         1.0 if fr >= at + lag else 0.0)
        s.obj(f"Círculo {i + 1}", solid(WHITE if i == 1 else colour), g, kind="ellipse", base=(reach, reach))
        if i == 1:
            s.obj(f"Círculo {i + 1} (rayas)", solid(colour), g, path=stripes_in_circle(28), base=(reach, reach))
        elif i == 3:
            s.obj(f"Círculo {i + 1} (puntos)", solid("#5A0000", 0.85), g, path=dots_in_circle(40, 0.45),
                  base=(reach, reach))


# --- O1 (22.1-26.5 s): red discs open onto a white opener: rows of squares, an avatar, the button and the name ---
def white_opener():
    D = dur_for(3.0, 1.8)
    t = _p("white-opener", "Apertura: círculos rojos y canal sobre blanco", "Opener: red discs and a channel on white",
           12909, D, "aperturas", ["círculos", "avatar"], thumb=3.4)
    s = S(t, D)
    circles_in(s, 0)
    for j, (y, size, step, alpha) in enumerate(((60, 56, 102, 0.85), (142, 44, 82, 0.8), (203, 26, 64, 0.6),
                                               (252, 16, 46, 0.25))):
        for side, yy in ((0, y), (1, 1080 - y)):
            for c, (colour, off) in enumerate((("#8C8C8C", 0), ("#D06A6A", step / 2 + 10))):
                d = 1 if (j + side) % 2 else -1
                s.obj(f"Cuadros {j + 1}{'ab'[side]}{c + 1}", solid(colour, alpha),
                      lambda fr, u, yy=yy, size=size, d=d: (960 + d * 60 * u, yy, 2400, size, 0, 1.0 if fr >= 30 else 0.0),
                      path=squares_row(40, size, step, off))
    shape_photo(s, "fx-man-01", lambda fr, u: (960, 476, 228 * pop(fr, 25, 9), 228 * pop(fr, 25, 9)),
                op=lambda fr, u: 1.0 if fr >= 25 else 0.0, label="Tu foto de perfil")
    s.obj("Aro", ring("#E8202A", 6), lambda fr, u: (960, 476, 234 * pop(fr, 25, 9), 234 * pop(fr, 25, 9), 0,
                                                    1.0 if fr >= 25 else 0.0), kind="ellipse", base=(234, 234))
    bx = lambda fr: 662 + 660 * (1 - k(fr, 33, 15))  # noqa: E731
    s.say("ChannelName", (752, 610, 1256, 666), "Lato", 700, "#F0262E", align="left",
          reveal=lambda fr: (bx(fr) + 58, 0, 1920, 1080), op=lambda fr, u: 1.0 if fr >= 33 else 0.0)
    ytb(s, "Botón", lambda fr, u: (bx(fr), 640, pop(fr, 33, 6), 0, 1.0 if fr >= 33 else 0.0), 116, 80,
        body=solid("#FF4B4B"))
    s.say("50k subscribers", (1006, 686, 1242, 712), "Lato", 700, "#F0262E", "Texto",
          reveal=lambda fr: (1006, 0, 1006 + 240 * k(fr, 48, 9), 1080))
    return t


OPRED = "#EC1E3C"


def box_text(s, name, text, box, ink, at, colour=BLACK, ink_colour=WHITE, weight=800, way="mid", n=6, family=M):
    """A box that opens (way: mid = from its middle line up and down, ltr = left to right) with its text."""
    x0, y0, x1, y1 = box
    if way == "mid":
        def r(fr):
            h = (y1 - y0) / 2 * k(fr, at, n)
            return x0, (y0 + y1) / 2 - h, x1, (y0 + y1) / 2 + h
    else:
        def r(fr):
            return x0, y0, x0 + (x1 - x0) * k(fr, at, n), y1
    s.rect(name, solid(colour), lambda fr, u: r(fr))
    return s.say(text, ink, family, weight, ink_colour, f"{name} (texto)", reveal=r)


CROSS = poly([(40, 0), (60, 0), (60, 40), (100, 40), (100, 60), (60, 60), (60, 100), (40, 100), (40, 60), (0, 60),
              (0, 40), (40, 40)])


def red_bg(s, kind):
    """The four backgrounds of the red openers: dark triangles, black blobs, striped circles, a grid of crosses."""
    bg(s, OPRED)
    if kind == "triangles":
        for i, (x, y, sz, r) in enumerate(((140, 80, 150, 10), (520, 60, 140, -20), (1500, 120, 210, 15),
                                           (300, 420, 200, 25), (1640, 520, 170, -10), (1260, 760, 230, 5),
                                           (260, 820, 260, -15), (900, 980, 180, 20))):
            s.obj(f"Fondo (triángulo {i + 1})", solid("#A80E26", 0.7), lambda fr, u, x=x, y=y, sz=sz, r=r: (
                x + 30 * u, y + 15 * u, sz * 1.5, sz * 1.2, r, 1), path=regular(3, 90))
    elif kind == "blobs":
        s.rect("Fondo (líneas)", solid("#C8102E", 0.6), lambda fr, u: (0, 0, 1920, 1080),
               path=" ".join(poly([(i * 2.5, 0), (i * 2.5 + 0.12, 0), (i * 2.5 + 0.12, 100), (i * 2.5, 100)])
                             for i in range(40)))
        for i, (x, y, w, h) in enumerate(((180, 160, 70, 50), (650, 170, 30, 26), (1150, 140, 50, 40),
                                          (1800, 240, 90, 90), (420, 610, 40, 34), (210, 860, 90, 120),
                                          (1240, 480, 46, 38), (1880, 800, 50, 70), (1300, 960, 60, 46),
                                          (820, 980, 40, 36))):
            s.obj(f"Fondo (mancha {i + 1})", solid("#2A0006", 0.85), lambda fr, u, x=x, y=y, w=w, h=h, i=i: (
                x, y - 20 * u, w, h, 30 * i, 1), kind="ellipse")
    elif kind == "circles":
        s.rect("Fondo (rayas)", solid("#D81A35", 0.55), lambda fr, u: (-200, -200, 2120, 1280), path=hatch(60, 0.5))
        for i, (x, y, d) in enumerate(((180, 300, 900), (1340, 760, 640), (1380, 140, 120), (360, 1100, 420))):
            s.obj(f"Fondo (círculo {i + 1})", grad("#F5435A", "#D41530", 135), lambda fr, u, x=x, y=y, d=d: (
                x, y + 10 * u, d, d, 0, 1), kind="ellipse")
    elif kind == "crosses":
        for j in range(9):
            s.rect(f"Fondo (cruces {j + 1})", solid("#B50E26", 0.8),
                   lambda fr, u, j=j: (-80, 29 + 120 * j - 20 * u, 2000, 51 + 120 * j - 20 * u),
                   path=" ".join(poly([((100 + 120 * i + a * 22) / 2080 * 100, b * 100) for a, b in
                                       ((0.4, 0), (0.6, 0), (0.6, 0.4), (1, 0.4), (1, 0.6), (0.6, 0.6), (0.6, 1),
                                        (0.4, 1), (0.4, 0.6), (0, 0.6), (0, 0.4), (0.4, 0.4))]) for i in range(17)))


# --- G3 (26.5-29.3 s), 2×2 grid of red channel openers -----------------------------------------------------------
def opener_boxes():
    D = dur_for(1.3, 2.0)
    t = _p("opener-boxes", "Apertura roja: nombre en cajas negras", "Red opener: name in black boxes", 12910, D,
           "aperturas", ["rojo", "cajas"])
    s = S(t, D)
    red_bg(s, "triangles")
    white_button(s, "Botón", lambda fr, u: (950, 380, pop(fr, 5, 9), 0, 1.0 if fr >= 5 else 0.0), 260, 176)
    s.rect("Línea", solid(BLACK), lambda fr, u: (952 - 440 * k(fr, 18, 6), 557, 952 + 440 * k(fr, 18, 6), 563),
           op=lambda fr, u: 1.0 if fr < 27 else 0.0)
    box_text(s, "Caja", "YOUTUBECHANNEL", (512, 512, 1392, 608), (560, 532, 1352, 590), 24)
    box_text(s, "Caja 2", "100K SUBSCRIBERS", (632, 628, 1272, 712), (648, 652, 1256, 690), 33)
    return t


def opener_typed():
    D = dur_for(1.2, 2.0)
    t = _p("opener-typed", "Apertura roja: nombre tecleado", "Red opener: typed name", 12911, D, "aperturas",
           ["rojo", "tecleado"])
    s = S(t, D)
    red_bg(s, "blobs")
    c = s.say("YOURCHANNEL", (456, 488, 1472, 584), M, 900, WHITE)
    s.typed(c, 3, stagger=0.06, duration=0.05)
    white_button(s, "Botón", lambda fr, u: (960, 360 + 40 * (1 - k(fr, 12, 9)), 1, 0, k(fr, 12, 9)), 224, 160)
    box_text(s, "Caja", "200K SUBSCRIBERS", (1016, 592, 1460, 648), (1030, 606, 1446, 636), 27, way="ltr")
    return t


def opener_divider():
    D = dur_for(1.8, 1.8)
    t = _p("opener-divider", "Apertura roja: botón, línea y nombre", "Red opener: button, divider and name", 12912, D,
           "aperturas", ["rojo", "suscribirse"])
    s = S(t, D)
    red_bg(s, "circles")
    # 26.5-28.0 s: a line grows in the middle; then it slides left while the button swings out of it like a door
    # (hinged on the line, a real turn round its vertical axis) and the name slides out of the line to the right
    lx = lambda fr: 630 + 378 * (1 - k(fr, 22, 15))  # noqa: E731
    s.rect("Línea", solid(WHITE), lambda fr, u: (lx(fr) - 3, 536 - 96 * k(fr, 3, 6), lx(fr) + 3, 536 + 96 * k(fr, 3, 6)))
    w, h = 212, 144
    turn = lambda fr: -90 * (1 - k(fr, 24, 9))  # noqa: E731  (-Y: the hinge side comes forward)
    card3d(s, "Botón", lambda fr, u: (lx(fr) - 10 - w / 2 * math.cos(math.radians(turn(fr))), 532, 1, 0,
                                      toggle(fr, 24)), w, h, ry=turn, persp=1400, front=solid(WHITE),
           z=lambda fr: -w / 2 * abs(math.sin(math.radians(turn(fr)))))
    s.say("ChannelName", (680, 500, 1560, 588), M, 700, WHITE, align="left",
          reveal=lambda fr: (lx(fr) + 4, 0, 1920, 1080), shift=lambda fr: (-500 * (1 - k(fr, 23, 14)), 0))
    s.obj("Píldora", solid(BLACK), lambda fr, u: (1052, 654, 440 * k(fr, 44, 6), 52, 0, 1), radius=26, base=(440, 52))
    s.say("SUBSCRIBE", (982, 644, 1122, 666), M, 800, WHITE, "Texto", op=lambda fr, u: k(fr, 47, 4))
    return t


def opener_fade():
    D = dur_for(1.2, 2.0)
    t = _p("opener-fade", "Apertura roja: botón y nombre que aparecen", "Red opener: button and name fading in", 12913,
           D, "aperturas", ["rojo"])
    s = S(t, D)
    red_bg(s, "crosses")
    white_button(s, "Botón", lambda fr, u: (938, 384, pop(fr, 6, 9), 0, 1.0 if fr >= 6 else 0.0), 180, 128)
    s.say("YourChannel", (560, 492, 1360, 580), M, 700, WHITE,
          geom=lambda fr, u: (0, 0, 0.9 + 0.1 * k(fr, 12, 12), 0, k(fr, 12, 12)))
    box_text(s, "Caja", "500k subscribers", (732, 600, 1168, 668), (752, 616, 1148, 650), 27, weight=700)
    return t


def opener_flip():
    """29.3-32.2 s: on red waves, a white box flips round into the play button; it slides left and lets the name
    out; the handle types under it."""
    D = dur_for(1.9, 1.8)
    t = _p("opener-flip", "Apertura roja: botón que gira y nombre", "Red opener: flipping button and name", 12914, D,
           "aperturas", ["rojo", "ondas"], thumb=2.4)
    s = S(t, D)
    bg(s, OPRED)
    for i, (x, y, w, h, r) in enumerate(((300, 1000, 2400, 700, -8), (1500, -80, 1800, 600, 12),
                                         (900, 620, 2600, 380, -4))):
        s.obj(f"Fondo (onda {i + 1})", solid("#D4122E", 0.6), lambda fr, u, x=x, y=y, w=w, h=h, r=r: (
            x - 20 * u, y, w, h, r + 2 * math.sin(u), 1), kind="ellipse")
    # the button tumbles in from far away: a full turn round its vertical axis (grey back, white front with the
    # triangle cut out), a little tilt and spin, growing to its size (measured on 29.3-30.1 s at 30 fps)
    ry = f6.curve([(3, 0), (7, 90), (10, 180), (13, 270), (16, 325), (19, 350), (23, 360)])
    rx = f6.curve([(4, 30), (10, 20), (16, 8), (21, 0)])
    rz = f6.curve([(4, -40), (8, -10), (11, -20), (15, -8), (19, -3), (22, 0)])
    sc = f6.curve([(4, 0.03), (5, 0.1), (6, 0.18), (7, 0.3), (8, 0.45), (9, 0.55), (10, 0.65), (11, 0.8),
                   (12, 0.92), (15, 1.0)])
    bx = lambda fr: 528 + 462 * (1 - k(fr, 30, 15))  # noqa: E731
    s.say("YourChannel", (690, 480, 1500, 582), M, 900, WHITE, align="left",
          reveal=lambda fr: (bx(fr) + 100, 0, 1920, 1080), shift=lambda fr: (-800 * (1 - k(fr, 30, 15)), 0),
          op=lambda fr, u: 1.0 if fr >= 30 else 0.0)
    card3d(s, "Botón", lambda fr, u: (bx(fr), 532, sc(fr), rz(fr), toggle(fr, 3)), 216, 144, rx=rx, ry=ry,
           persp=1600, front=solid(WHITE), back=solid("#BDBDBD"), edge=solid("#9E9E9E"))
    c = s.say("@yourchannel", (720, 606, 1100, 652), M, 800, "#FFB3BD", "Texto", align="left")
    s.typed(c, 51, stagger=0.05, duration=0.03)
    return t


# --- G4 (32.2-37.0 s), 2×2 grid of titles over footage ------------------------------------------------------------
def best_video():
    """q1: a red line grows from the middle, BEST VIDEO rises out of it, ON YOUTUBE rises under it and a red box
    opens behind the second line."""
    D = dur_for(2.2, 1.6)
    t = _p("best-video", "Título: línea roja y caja roja", "Title: red line and red box", 12915, D, "titulos-estilo",
           ["rojo"])
    s = S(t, D)
    s.rect("Caja", solid("#F0141E"), lambda fr, u: (608, 548, 608 + 704 * k(fr, 57, 9), 640))
    s.rect("Línea", solid("#F0141E"), lambda fr, u: (960 - 330 * k(fr, 9, 9), 527, 960 + 330 * k(fr, 9, 9), 535),
           op=lambda fr, u: 1 - k(fr, 30, 6))
    s.say("BEST VIDEO", (664, 452, 1252, 520), M, 800, WHITE, reveal=lambda fr: (0, 0, 1920, 527),
          shift=lambda fr: (0, 76 * (1 - k(fr, 18, 9))), op=lambda fr, u: 1.0 if fr >= 18 else 0.0)
    s.say("ON YOUTUBE", (660, 564, 1272, 624), M, 800, WHITE, "Texto", reveal=lambda fr: (0, 535, 1920, 1080),
          shift=lambda fr: (0, -90 * (1 - k(fr, 36, 9))), op=lambda fr, u: 1.0 if fr >= 36 else 0.0)
    return t


def watch_next():
    """q2: a white box opens from the left and then down; WATCH NEXT types, the video title fades, a red frame
    shows behind."""
    D = dur_for(2.8, 1.6)
    t = _p("watch-next", "Tercio: siguiente video en caja blanca", "Lower third: watch next in a white box", 12916, D,
           "lowerthirds", ["caja", "blanco"])
    s = S(t, D)
    s.rect("Marco rojo", solid("#E8141E"), lambda fr, u: (152, 784, 172 + 916 * k(fr, 78, 9), 960),
           op=lambda fr, u: 1.0 if fr >= 78 else 0.0)
    s.rect("Caja", solid(WHITE), lambda fr, u: (160, 882 - 86 * k(fr, 9, 6), 160 + 928 * k(fr, 2, 9), 882 + 86 * k(fr, 9, 6)))
    s.rect("Borde", ring(BLACK, 3), lambda fr, u: (160, 796, 1088, 968), op=lambda fr, u: k(fr, 12, 4))
    c = s.say("WATCH NEXT", (212, 824, 592, 864), M, 800, BLACK, align="left")
    s.typed(c, 12, stagger=0.07, duration=0.03)
    s.say("HOW TO BECOME A POPULAR BLOGGER?", (212, 888, 980, 920), M, 500, BLACK, "Texto", align="left",
          op=lambda fr, u: k(fr, 36, 6))
    return t


def modern_titles():
    """q3: a white frame draws in the middle, then moves left as the three lines slide out of it."""
    D = dur_for(1.8, 1.6)
    t = _p("modern-titles", "Título: marco blanco y tres líneas", "Title: white frame and three lines", 12917, D,
           "titulos-estilo", ["marco"])
    s = S(t, D)
    # a square frame (388 px, measured at 33.1 s) moves left, turns 44° round its vertical axis and sinks 50 px back,
    # so it ends with its left side 404 px tall at x 496 and its right side 356 px tall at x 808, as at 35.5 s (fitted
    # to those four numbers with the engine's projection about the frame's centre, eye 2050 px away)
    side, persp = 388.0, 2050.0
    q = lambda fr: k(fr, 28, 16)  # noqa: E731
    fx = lambda fr: 920 - 245 * q(fr)  # noqa: E731  (fitted 655; +20 measured on the render)
    turn = lambda fr: 44 * q(fr)  # noqa: E731  (+Y swings the right edge back)
    sink = lambda fr: -50 * q(fr)  # noqa: E731

    def edges(fr):
        """The frame's left and right edges on screen (its 3D pose projected about the canvas centre)."""
        a_, th = side / 2, math.radians(turn(fr))
        zl, zr = sink(fr) + a_ * math.sin(th), sink(fr) - a_ * math.sin(th)
        return (960 + (fx(fr) - a_ * math.cos(th) - 960) * persp / (persp - zl),
                960 + (fx(fr) + a_ * math.cos(th) - 960) * persp / (persp - zr))
    # it draws itself as a stroke from the top right corner, down, along the bottom, up and back along the top
    c = s.obj("Marco", ring(WHITE, 22), lambda fr, u: (fx(fr), 538, side, side, 0, toggle(fr, 3)), base=(side, side),
              path="M 100 0 L 100 100 L 0 100 L 0 0 Z")
    c["shapeStyle"]["keyframes"] = {"trimEnd": per_frame(s, lambda fr, u: 100 * min(1.0, lin(fr, 3, 12)))}
    c["shapeStyle"]["trimStart"], c["shapeStyle"]["trimEnd"] = 0.0, 100.0
    s.d3(c, ry=lambda fr, u: turn(fr), z=lambda fr, u: sink(fr), persp=persp)
    for i, (line, ink) in enumerate((("MODERN TITLES", (540, 400, 1500, 480)), ("FOR YOUR", (540, 504, 1160, 576)),
                                     ("CHANNEL", (540, 592, 1108, 668)))):
        s.say(line, ink, M, 900, "#111111", ["Título", "Texto", "Texto 2"][i], align="left",
              reveal=lambda fr: (edges(fr)[0] + 11, 0, 1920 if fr >= 45 else edges(fr)[1] - 11, 1080),
              shift=lambda fr, i=i: (420 * (1 - k(fr, 30 + 2 * i, 15)), 0), op=lambda fr, u: 1.0 if fr >= 30 else 0.0)
    return t


def subscribe_to():
    """q4: the two white lines rise, then a white box wipes in from the left and the words turn black."""
    D = dur_for(1.6, 1.6)
    t = _p("subscribe-to", "Título: suscríbete en caja blanca", "Title: subscribe in a white box", 12918, D,
           "titulos-estilo", ["suscribirse", "caja"])
    s = S(t, D)
    edge = lambda fr: 160 + 1460 * k(fr, 36, 12)  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: (160, 428, edge(fr), 640))
    for colour, name, op in ((WHITE, "Título (blanco)", lambda fr: 1.0), (BLACK, "Título", lambda fr: 1.0)):
        for i, (line, ink) in enumerate((("SUBSCRIBE TO", (228, 452, 1044, 524)),
                                         ("OUR YOUTUBE CHANNEL", (220, 544, 1560, 616)))):
            dx = lambda fr: 62 * (1 - k(fr, 36, 12))  # noqa: E731
            black = colour == BLACK
            s.say(line, ink, M, 900, colour, name if i == 0 else name.replace("Título", "Texto"), align="left",
                  reveal=(lambda fr: (0, 0, edge(fr), 1080)) if black else
                  (lambda fr, ink=ink: (edge(fr), ink[1] - 8, 1920, ink[3] + 4)),
                  shift=lambda fr, ink=ink, dx=dx: (dx(fr), 90 * (1 - k(fr, 3 + 3 * (ink[1] > 500), 9))),
                  editable=black)
    return t


# --- H (37.0-41.0 s): HELLO! types in huge, a coral box grows behind it, all shrinks; the welcome rises word by word
def hello_welcome():
    D = dur_for(2.0, 2.0)
    t = _p("hello-welcome", "Título: HELLO! y bienvenida al canal", "Title: HELLO! and welcome to my channel", 12919,
           D, "titulos-estilo", ["bienvenida", "coral"])
    s = S(t, D)
    coral = "#FF4F4F"
    z = lambda fr: (0.35 + 2.95 * k(fr, 2, 9)) if fr < 39 else 3.3 - 2.3 * k(fr, 39, 6)  # noqa: E731
    off = lambda fr: (89 * (z(fr) - 1) / 2.3, 6 * (z(fr) - 1) / 2.3)  # noqa: E731
    px, py = 961, 459

    def place(x, y, fr):
        return px + (x - px) * z(fr) + off(fr)[0], py + (y - py) * z(fr) + off(fr)[1]

    def box(fr, u):
        q = k(fr, 33, 6)
        x0, y0 = place(1442 - 964 * q, 400, fr)
        x1, y1 = place(1442, 518, fr)
        return x0, y0, x1, y1
    s.rect("Caja", solid(coral), box, op=lambda fr, u: 1.0 if fr >= 33 else 0.0)
    ink = (770, 420, 1152, 498)
    c = s.say("HELLO!", ink, M, 800, WHITE,
              geom=lambda fr, u: (place((ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2, fr)[0] - (ink[0] + ink[2]) / 2,
                                  place((ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2, fr)[1] - (ink[1] + ink[3]) / 2,
                                  z(fr), 0, 1))
    s.typed(c, 2, stagger=0.045, duration=0.02)
    for i, (line, ink2) in enumerate((("AND WELCOME TO", (502, 556, 1420, 612)), ("MY CHANNEL", (640, 636, 1282, 704)))):
        c = s.say(line, ink2, M, 800, WHITE, "Texto" if i == 0 else "Texto 2")
        s.typed(c, 45 + 8 * i, stagger=0.07, duration=0.15, preset="rise", unit="word")
    return t


def rect_pts(x0, y0, x1, y1, start="tr"):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    i = {"tl": 0, "tr": 1, "br": 2, "bl": 3}[start]
    return pts[i:] + pts[:i]


def pill_pts(x0, y0, x1, y1, steps=8):
    """The outline of a pill (rounded ends) from the top middle, clockwise."""
    r = (y1 - y0) / 2
    cy = (y0 + y1) / 2
    pts = [((x0 + x1) / 2, y0), (x1 - r, y0)]
    pts += [(x1 - r + r * math.sin(math.pi * i / steps), cy - r * math.cos(math.pi * i / steps)) for i in range(1, steps)]
    pts += [(x1 - r, y1), (x0 + r, y1)]
    pts += [(x0 + r - r * math.sin(math.pi * i / steps), cy + r * math.cos(math.pi * i / steps)) for i in range(1, steps)]
    pts += [(x0 + r, y0)]
    return pts


# --- G5 (41.0-45.3 s), 2×2 grid of titles over footage ------------------------------------------------------------
def best_solution():
    """q1: a white line drops in the middle, a white and a black box open sideways with the two lines rising in
    them, and a thin black frame draws round them."""
    D = dur_for(2.4, 1.6)
    t = _p("best-solution", "Título: cajas blanca y negra con marco", "Title: white and black boxes in a frame", 12920,
           D, "titulos-estilo", ["caja", "marco"])
    s = S(t, D)
    s.rect("Línea", solid(WHITE), lambda fr, u: (956, 300, 964, 300 + 92 * k(fr, 3, 4)),
           op=lambda fr, u: 1.0 if 3 <= fr < 9 else 0.0)
    for name, (x0, y0, x1, y1), colour, text, ink, ink_col in (
            ("Caja", (372, 392, 1552, 516), WHITE, "THE BEST SOLUTION", (428, 416, 1496, 496), BLACK),
            ("Caja 2", (500, 524, 1428, 628), BLACK, "FOR YOUR TEXT", (540, 540, 1388, 608), WHITE)):
        cx = (x0 + x1) / 2
        w = lambda fr, x0=x0, x1=x1: 80 + (x1 - x0 - 80) * k(fr, 7, 8)  # noqa: E731
        s.rect(name, solid(colour), lambda fr, u, w=w, cx=cx, y0=y0, y1=y1: (
            cx - w(fr) / 2, y0, cx + w(fr) / 2, y1), op=lambda fr, u: 1.0 if fr >= 7 else 0.0)
        s.say(text, ink, M, 900, ink_col, f"{name} (texto)", reveal=lambda fr, w=w, cx=cx, y0=y0, y1=y1: (
            cx - w(fr) / 2, y0, cx + w(fr) / 2, y1), shift=lambda fr, y1=y1, y0=y0: (0, (y1 - y0) * (1 - k(fr, 10, 8))))
    s.outline("Marco", rect_pts(320, 336, 1600, 680, "tr"), 6, BLACK, at=48, n=21)
    return t


def how_do_i():
    """q2: a white box rises from the bottom edge with the question; WATCH NEXT slides up beside it, turned."""
    D = dur_for(1.4, 1.8)
    t = _p("how-do-i", "Tercio: pregunta en caja blanca", "Lower third: question in a white box", 12921, D,
           "lowerthirds", ["caja", "blanco"])
    s = S(t, D)
    top = lambda fr: 1090 - 398 * k(fr, 2, 8)  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: (188, top(fr), 628, 1090))
    for i, (line, y) in enumerate((("HOW DO", 816), ("I MAKE A", 880), ("GOOD VIDEO?", 944))):
        s.say(line, (220, y, 612, y + 48), M, 900, BLACK,
              ["Título", "Título 2", "Título 3"][i], align="left", reveal=lambda fr: (188, top(fr), 628, 1090),
              shift=lambda fr: (0, 398 * (1 - k(fr, 2, 8))))
    ink = (156 - 132, 900 - 24, 156 + 132, 900 + 24)
    s.say("WATCH NEXT", ink, M, 900, "#111111", "Texto",
          geom=lambda fr, u: (0, 120 * (1 - k(fr, 33, 9)), 1, -90, k(fr, 33, 6)))
    return t


def good_design():
    """q3: Good Design / for your / YouTube Titles. fade in word by word; a small square pops."""
    D = dur_for(1.8, 1.6)
    t = _p("good-design", "Título: tres líneas que aparecen palabra por palabra", "Title: three lines fading in word "
           "by word", 12922, D, "titulos-estilo", ["minimal"])
    s = S(t, D)
    for i, (line, ink, weight, at) in enumerate((("Good Design", (148, 140, 788, 216), 700, 1),
                                                 ("for your", (148, 240, 568, 304), 500, 12),
                                                 ("YouTube Titles.", (148, 328, 912, 408), 700, 21))):
        c = s.say(line, ink, M, weight, WHITE, ["Título", "Texto", "Título 2"][i], align="left")
        s.typed(c, at, stagger=0.15, duration=0.2, preset="fade", unit="word")
    s.obj("Cuadro", solid(WHITE), lambda fr, u: (988, 120, 32 * pop(fr, 51), 32 * pop(fr, 51), 0, 1.0 if fr >= 51 else 0.0))
    return t


def clean_modern():
    """q4: a black numbered dot pops, the two lines type and a white pill outline draws round them."""
    D = dur_for(1.6, 1.8)
    t = _p("clean-modern", "Tercio: número y texto en píldora", "Lower third: number and text in a pill", 12923, D,
           "lowerthirds", ["número", "píldora"])
    s = S(t, D)
    s.outline("Píldora", pill_pts(792, 836, 1324, 988), 8, WHITE, at=24, n=12, closed=False)
    s.obj("Número (círculo)", solid("#111111"), lambda fr, u: (776, 816, 84 * pop(fr, 6), 84 * pop(fr, 6), 0,
                                                              1.0 if fr >= 6 else 0.0), kind="ellipse")
    s.say("1", (764, 798, 788, 834), M, 900, WHITE, "Número", op=lambda fr, u: k(fr, 9, 3))
    for i, (line, ink, at) in enumerate((("CLEAN AND", (828, 856, 1160, 904), 15),
                                         ("MODERN TITLES", (828, 912, 1292, 960), 24))):
        c = s.say(line, ink, M, 900, WHITE, "Título" if i == 0 else "Título 2", align="left")
        s.typed(c, at, stagger=0.04, duration=0.03)
    return t


def rise(s, text, ink, at, name="Título", family=M, weight=800, colour=WHITE, n=8, align="left", dist=None,
         reveal_x=(0, 1920)):
    """A line that rises into place from under its own baseline (seen only above it)."""
    d = dist if dist is not None else (ink[3] - ink[1]) * 1.4
    return s.say(text, ink, family, weight, colour, name, align=align,
                 reveal=lambda fr: (reveal_x[0], -100, reveal_x[1], ink[3] + 4),
                 shift=lambda fr: (0, d * (1 - k(fr, at, n))), op=lambda fr, u: 1.0 if fr >= at else 0.0)


# --- SUB (45.3-49.3 s): SUBSCRIBE NOW / ON MY CHANNEL! falling in letter by letter ---------------------------------
def subscribe_now():
    D = dur_for(1.6, 2.0)
    t = _p("subscribe-now", "Título: suscríbete letra por letra", "Title: subscribe now letter by letter", 12924, D,
           "titulos-estilo", ["suscribirse"])
    s = S(t, D)
    for i, (line, ink, at) in enumerate((("SUBSCRIBE NOW", (490, 474, 1264, 528), 9),
                                         ("ON MY CHANNEL!", (664, 550, 1436, 612), 21))):
        c = s.say(line, ink, M, 900, WHITE, "Título" if i == 0 else "Título 2", align="left",
                  geom=lambda fr, u: (30 * u, 0, 1, 0, 1))
        s.typed(c, at, stagger=0.045, duration=0.18, preset="drop")
    return t


# --- G6 (49.3-55.4 s), 2×2 grid of titles over footage ------------------------------------------------------------
def best_show():
    """q1: BEST SHOW rises word by word, then ON YOUTUBE.; a play button pops and a line draws beside them."""
    D = dur_for(1.4, 1.8)
    t = _p("best-show", "Tercio: botón, línea y dos renglones", "Lower third: button, divider and two lines", 12925,
           D, "lowerthirds", ["botón"])
    s = S(t, D)
    c = s.say("BEST SHOW", (704, 452, 1240, 516), M, 800, WHITE, "Título", align="left")
    s.typed(c, 9, stagger=0.12, duration=0.15, preset="rise", unit="word")
    c = s.say("ON YOUTUBE.", (704, 532, 1448, 612), M, 900, WHITE, "Título 2", align="left")
    s.typed(c, 30, stagger=0.1, duration=0.15, preset="rise", unit="word")
    white_button(s, "Botón", lambda fr, u: (576, 536, pop(fr, 33, 6), 0, 1.0 if fr >= 33 else 0.0), 128, 96)
    s.rect("Línea", solid(WHITE), lambda fr, u: (673, 536 - 88 * k(fr, 33, 9), 679, 536 + 88 * k(fr, 33, 9)))
    return t


def new_video():
    """q2: a black bar grows, its words rise one by one; JUST WATCH IT! rises under it and is underlined."""
    D = dur_for(2.0, 1.6)
    t = _p("new-video", "Tercio: video nuevo en barra negra", "Lower third: new video in a black bar", 12926, D,
           "lowerthirds", ["barra", "negro"])
    s = S(t, D)
    s.rect("Barra", solid(BLACK), lambda fr, u: (312, 448, 312 + 1368 * k(fr, 3, 9), 528))
    c = s.say("THE NEW VIDEO HAS ALREADY BEEN RELEASED", (364, 468, 1596, 508), M, 800, WHITE)
    s.typed(c, 12, stagger=0.06, duration=0.12, preset="rise", unit="word")
    c = s.say("JUST WATCH IT!", (628, 536, 1280, 600), M, 900, WHITE, "Título 2")
    s.typed(c, 39, stagger=0.1, duration=0.12, preset="rise", unit="word")
    s.rect("Subrayado", solid(WHITE), lambda fr, u: (628, 620, 628 + 652 * k(fr, 51, 9), 628))
    return t


def clean_titles():
    """q3: a white square frame grows from a small square and the four lines rise inside it."""
    D = dur_for(1.2, 1.8)
    t = _p("clean-titles", "Título: cuatro renglones en marco blanco", "Title: four lines in a white frame", 12927, D,
           "titulos-estilo", ["marco"])
    s = S(t, D)
    g = lambda fr: k(fr, 6, 12)  # noqa: E731
    s.obj("Marco", ring(WHITE, 10), lambda fr, u: (408, 538, 120 + 464 * g(fr), 120 + 460 * g(fr), 0,
                                                   1.0 if fr >= 9 else 0.0), base=(584, 580))
    for i, (line, ink) in enumerate((("CLEAN", (232, 368, 548, 432)), ("TITLES", (232, 464, 584, 528)),
                                     ("FOR YOUR", (152, 568, 656, 632)), ("CHANNEL", (168, 664, 636, 728)))):
        rise(s, line, ink, 13 + 2 * i, ["Título", "Título 2", "Título 3", "Título 4"][i], align="center")
    return t


def modern_universal():
    """q4: MODERN / AND / UNIVERSAL. rise one after another; a thin line draws at their left."""
    D = dur_for(1.6, 1.6)
    t = _p("modern-universal", "Tercio: tres renglones y línea", "Lower third: three lines and a line", 12928, D,
           "lowerthirds", ["minimal"])
    s = S(t, D)
    for i, (line, ink) in enumerate((("MODERN", (100, 756, 460, 808)), ("AND", (100, 828, 290, 876)),
                                     ("UNIVERSAL.", (100, 892, 580, 940)))):
        rise(s, line, ink, 3 + 4 * i, ["Título", "Título 2", "Título 3"][i])
    s.rect("Línea", solid(WHITE), lambda fr, u: (72, 760, 78, 760 + 180 * k(fr, 39, 9)))
    return t


ARROW = poly([(0, 0), (0, 80), (22, 62), (38, 100), (52, 94), (36, 58), (64, 58)])
BELL = poly([(50, 0), (60, 8), (76, 30), (78, 62), (96, 82), (4, 82), (22, 62), (24, 30), (40, 8)]) + " " + \
    poly([(40, 86), (60, 86), (56, 100), (44, 100)])
SUBRED, GREYBOX = "#F21B26", "#BDBDBD"


def toggle(fr, at):
    return 1.0 if fr >= at else 0.0


def icon(s, name, path, cx, cy, size, at, colour=WHITE, rot=0.0, layers=None):
    s.obj(name, layers or solid(colour), lambda fr, u: (cx, cy, size * pop(fr, at), size * pop(fr, at), rot,
                                                       toggle(fr, at)), path=path)


def subscribe_box(s, name, rect, at_on, at_switch, on_text="SUBSCRIBE", off_text="SUBSCRIBED", before=GREYBOX,
                  after=SUBRED, ink_pad=0.22, outline_after=False, grow_at=None):
    """A small box that pops (or grows from its left) as SUBSCRIBE and switches to SUBSCRIBED when clicked."""
    x0, y0, x1, y1 = rect
    w = lambda fr: (x1 - x0) * (k(fr, grow_at, 6) if grow_at is not None else pop(fr, at_on))  # noqa: E731
    r = (lambda fr: (x0, y0, x0 + w(fr), y1)) if grow_at is not None else \
        (lambda fr: ((x0 + x1) / 2 - w(fr) / 2, (y0 + y1) / 2 - (y1 - y0) / 2 * pop(fr, at_on),
                     (x0 + x1) / 2 + w(fr) / 2, (y0 + y1) / 2 + (y1 - y0) / 2 * pop(fr, at_on)))
    s.rect(name, solid(before), lambda fr, u: r(fr), op=lambda fr, u: toggle(fr, at_on) * (1 - toggle(fr, at_switch)))
    s.rect(f"{name} (activo)", ring(after, 5) if outline_after else solid(after), lambda fr, u: r(fr),
           op=lambda fr, u: toggle(fr, at_switch))
    h = (y1 - y0) * ink_pad
    ink = (x0 + 14, y0 + (y1 - y0) / 2 - h, x1 - 14, y0 + (y1 - y0) / 2 + h)
    s.say(on_text, ink, M, 800, WHITE, f"{name} (texto)", op=lambda fr, u: toggle(fr, at_on + 4) * (1 - toggle(fr, at_switch)))
    s.say(off_text, ink, M, 800, after if outline_after else WHITE, f"{name} (texto 2)",
          op=lambda fr, u: toggle(fr, at_switch))


def cursor(s, keys_, kind="arrow", size=64, click=None):
    """A white mouse pointer (arrow or hand) moving through keys_ = [(frame, x, y)…]; it dips at click frames."""
    def pos(fr):
        if fr <= keys_[0][0]:
            return keys_[0][1], keys_[0][2]
        for (a, xa, ya), (b, xb, yb) in zip(keys_, keys_[1:]):
            if fr <= b:
                q = k(fr, a, b - a)
                return xa + (xb - xa) * q, ya + (yb - ya) * q
        return keys_[-1][1], keys_[-1][2]

    def geom(fr, u):
        x, y = pos(fr)
        dip = 0.85 if click and any(c <= fr < c + 4 for c in click) else 1.0
        return x + size * 0.32, y + size * 0.5, size * 0.64 * dip, size * dip, 0, toggle(fr, keys_[0][0])
    s.obj("Cursor", solid(WHITE), geom, path=ARROW if kind == "arrow" else HAND)


# --- G7 (60.1-64.9 s), 2×2 grid of subscribe lower thirds ---------------------------------------------------------
def sub_avatar_pill():
    """q1: the avatar pops, a white pill with the channel name opens beside it, a grey SUBSCRIBE box and a bell
    pop, the pointer clicks it red and goes to the bell."""
    D = dur_for(3.4, 1.4)
    t = _p("sub-avatar-pill", "Tercio: suscribirse con avatar y clic", "Lower third: subscribe with avatar and click",
           12929, D, "lowerthirds", ["suscribirse", "avatar", "clic"])
    s = S(t, D)
    ax = lambda fr: 720 - 252 * k(fr, 30, 9)  # noqa: E731
    s.rect("Píldora", solid(WHITE), lambda fr, u: (ax(fr), 856, ax(fr) + 484 * k(fr, 30, 9), 968),
           op=lambda fr, u: toggle(fr, 31), radius=56, base=(484, 112))
    s.say("CHANNEL NAME", (584, 896, 896, 928), M, 800, SUBRED, reveal=lambda fr: (ax(fr), 0, 952 * k(fr, 30, 9) + 1, 1080))
    shape_photo(s, "fx-man-02", lambda fr, u: (ax(fr), 916, 152 * pop(fr, 3), 152 * pop(fr, 3)),
                op=lambda fr, u: toggle(fr, 3), label="Tu foto de perfil")
    s.obj("Avatar (aro)", ring(WHITE, 6), lambda fr, u: (ax(fr), 916, 156 * pop(fr, 3), 156 * pop(fr, 3), 0,
                                                         toggle(fr, 3)), kind="ellipse", base=(156, 156))
    subscribe_box(s, "Suscribirse", (972, 876, 1300, 948), 48, 78)
    icon(s, "Campana", BELL, 1360, 912, 64, 51)
    cursor(s, [(54, 1500, 1120), (72, 1150, 930), (84, 1150, 930), (96, 1432, 1020)], click=[78])
    return t


def sub_red_pill():
    """q2: a red pill with the channel name pops; a hand clicks it, it widens into a like icon, a white SUBSCRIBE
    box and a bell icon."""
    D = dur_for(2.2, 1.6)
    t = _p("sub-red-pill", "Tercio: píldora roja que se vuelve suscribirse", "Lower third: red pill turning into "
           "subscribe", 12930, D, "lowerthirds", ["suscribirse", "clic"])
    s = S(t, D)
    wide_ = lambda fr: k(fr, 45, 9)  # noqa: E731
    s.obj("Píldora", solid("#FF3D4A"), lambda fr, u: (980, 908, (340 + 284 * wide_(fr)) * pop(fr, 3), 96 * pop(fr, 3), 0,
                                                     toggle(fr, 3)), radius=48, base=(624, 96))
    s.say("CHANNEL NAME", (860, 896, 1100, 922), M, 800, WHITE, "Texto", op=lambda fr, u: toggle(fr, 6) * (1 - k(fr, 39, 6)))
    s.rect("Caja", solid(WHITE), lambda fr, u: (982 - 162 * k(fr, 54, 6), 876, 982 + 162 * k(fr, 54, 6), 944))
    s.say("SUBSCRIBE", (850, 894, 1114, 926), M, 800, SUBRED, op=lambda fr, u: k(fr, 57, 4))
    for name, x, path, colour in (("Me gusta", 760, THUMB, "#2F7BEA"), ("Campana", 1200, BELL, "#9E9E9E")):
        s.obj(f"{name} (fondo)", solid(WHITE), lambda fr, u, x=x: (x, 908, 72 * pop(fr, 57), 64 * pop(fr, 57), 0,
                                                                   toggle(fr, 57)), radius=10, base=(72, 64))
        icon(s, name, path, x, 908, 40, 60, colour)
    cursor(s, [(24, 1100, 1120), (36, 990, 960), (48, 990, 960), (60, 990, 975)], kind="hand", click=[39])
    return t


def sub_center_avatar():
    """q3: the avatar pops, a white pill opens on both sides of it with the name and icons on the left and a red
    SUBSCRIBE on the right, which turns into an outlined SUBSCRIBED."""
    D = dur_for(3.8, 1.2)
    t = _p("sub-center-avatar", "Tercio: avatar al centro de la píldora", "Lower third: avatar in the middle of the "
           "pill", 12931, D, "lowerthirds", ["suscribirse", "avatar"])
    s = S(t, D)
    s.obj("Píldora", solid(WHITE), lambda fr, u: (912, 938, 808 * k(fr, 30, 9), 148, 0, toggle(fr, 30)), radius=30,
          base=(808, 148))
    s.say("CHANNEL NAME", (568, 906, 796, 930), M, 800, SUBRED, op=lambda fr, u: k(fr, 36, 6))
    for i, (x, colour, path) in enumerate(((600, "#2F7BEA", THUMB), (660, "#444444", THUMB), (740, "#F5B800", BELL))):
        icon(s, f"Ícono {i + 1}", path, x, 968, 30, 39 + 2 * i, colour, rot=180 if i == 1 else 0)
    subscribe_box(s, "Suscribirse", (1028, 918, 1244, 962), 40, 114, before=SUBRED, outline_after=True)
    shape_photo(s, "fx-woman-01", lambda fr, u: (914, 942, 164 * pop(fr, 6), 164 * pop(fr, 6)),
                op=lambda fr, u: toggle(fr, 6), label="Tu foto de perfil")
    s.obj("Avatar (aro)", ring(WHITE, 8), lambda fr, u: (914, 942, 168 * pop(fr, 6), 168 * pop(fr, 6), 0,
                                                         toggle(fr, 6)), kind="ellipse", base=(168, 168))
    return t


def sub_logo_box():
    """q4: a white box with the play button pops; a red SUBSCRIBE bar grows from it with bell and like icons; the
    pointer clicks it and it turns into an outlined SUBSCRIBED."""
    D = dur_for(3.8, 1.2)
    t = _p("sub-logo-box", "Tercio: logo en caja blanca y suscribirse", "Lower third: logo in a white box and "
           "subscribe", 12932, D, "lowerthirds", ["suscribirse", "botón"])
    s = S(t, D)
    s.obj("Caja", solid(WHITE), lambda fr, u: (784, 960, 168 * pop(fr, 9), 128 * pop(fr, 9), 0, toggle(fr, 9)),
          radius=16, base=(168, 128))
    ytb(s, "Botón", lambda fr, u: (784, 960, pop(fr, 12), 0, toggle(fr, 12)), 104, 72)
    subscribe_box(s, "Suscribirse", (872, 932, 1080, 972), 48, 114, before=SUBRED, outline_after=True, grow_at=48)
    for i, (x, path) in enumerate(((1112, BELL), (1168, THUMB))):
        s.obj(f"Ícono {i + 1} (fondo)", solid(SUBRED), lambda fr, u, x=x, i=i: (x, 952, 44 * pop(fr, 54 + 2 * i),
                                                                               40 * pop(fr, 54 + 2 * i), 0,
                                                                               toggle(fr, 54 + 2 * i)),
              radius=8, base=(44, 40))
        icon(s, f"Ícono {i + 1}", path, x, 952, 26, 56 + 2 * i)
    cursor(s, [(90, 1300, 1100), (108, 980, 960), (118, 980, 960), (126, 1164, 968)], kind="hand", click=[112])
    return t


BLUE, GOLD = "#2F7BEA", "#F5B800"


def swap_op(fr, a, b, n=4):
    """Shown from frame a to frame b (fading n frames at each end)."""
    return k(fr, a, n) * (1 - k(fr, b, n)) if b is not None else k(fr, a, n)


# --- G8 (64.9-71.4 s), 2×2 grid of like / subscribe / notify lower thirds -----------------------------------------
def sub_red_to_white():
    """q1: a red SUBSCRIBE pill opens; it turns white as SUBSCRIBED, and a red bell and a red like square pop."""
    D = dur_for(2.2, 2.0)
    t = _p("sub-red-white", "Tercio: suscribirse que pasa a suscrito", "Lower third: subscribe turning subscribed",
           12933, D, "lowerthirds", ["suscribirse", "campana"])
    s = S(t, D)
    r = lambda fr: (800, 832, 800 + 280 * k(fr, 3, 9), 888)  # noqa: E731
    s.rect("Píldora", solid(SUBRED), lambda fr, u: r(fr), op=lambda fr, u: 1 - toggle(fr, 42), radius=10, base=(280, 56))
    s.rect("Píldora (blanca)", solid(WHITE), lambda fr, u: r(fr), op=lambda fr, u: toggle(fr, 42), radius=10,
           base=(280, 56))
    ytb(s, "Botón", lambda fr, u: (836, 860, toggle(fr, 9), 0, 1 - toggle(fr, 42)), 44, 32, body=solid(WHITE), tri=SUBRED)
    ytb(s, "Botón (rojo)", lambda fr, u: (836, 860, 1, 0, toggle(fr, 42)), 44, 32, body=solid(SUBRED))
    s.say("SUBSCRIBE", (872, 848, 1060, 872), M, 800, WHITE, "Texto", reveal=lambda fr: r(fr),
          op=lambda fr, u: 1 - toggle(fr, 42))
    s.say("SUBSCRIBED", (872, 848, 1066, 872), M, 800, SUBRED, "Texto 2", op=lambda fr, u: toggle(fr, 42))
    for name, (cx, cy), path, at in (("Campana", (1098, 816), BELL, 48), ("Me gusta", (778, 914), THUMB, 60)):
        s.obj(f"{name} (fondo)", solid(SUBRED), lambda fr, u, cx=cx, cy=cy, at=at: (
            cx, cy, 68 * pop(fr, at), 64 * pop(fr, at), 0, toggle(fr, at)), radius=10, base=(68, 64))
        icon(s, name, path, cx, cy, 36, at + 3)
    return t


def like_card():
    """q2: a like circle pops and opens into LIKE THE VIDEO; a hand clicks it; a card drops under it with
    SUBSCRIBE and GET NOTIFIED."""
    D = dur_for(4.0, 1.4)
    t = _p("like-card", "Tercio: me gusta, suscribirse y notificaciones", "Lower third: like, subscribe and notify",
           12934, D, "lowerthirds", ["me gusta", "suscribirse", "campana"])
    s = S(t, D)
    drop = lambda fr: k(fr, 102, 12)  # noqa: E731
    s.rect("Tarjeta", solid(WHITE), lambda fr, u: (188, 760, 572, 760 + 224 * drop(fr)), radius=24, base=(384, 224))
    for i, (text, y, path, colour) in enumerate((("SUBSCRIBE", 848, None, SUBRED), ("GET NOTIFIED", 924, BELL, GOLD))):
        if path:
            icon(s, f"Ícono {i + 1}", path, 236, y, 34, 108 + 4 * i, colour)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, y=y, i=i: (236, y, pop(fr, 108 + 4 * i), 0, toggle(fr, 108 + 4 * i)),
                48, 34, body=solid(SUBRED))
        s.say(text, (280, y - 14, 280 + 15 * len(text) * 1.15, y + 14), M, 800, SUBRED, f"Texto {i + 2}",
              align="left", op=lambda fr, u, i=i: k(fr, 110 + 4 * i, 4))
    s.rect("Píldora", solid(WHITE), lambda fr, u: (188, 704, 188 + 392 * k(fr, 12, 9) * pop(fr, 3) / 1.12, 792),
           op=lambda fr, u: toggle(fr, 3), radius=44, base=(392, 88))
    s.obj("Me gusta (círculo)", solid(BLUE), lambda fr, u: (232, 748, 64 * pop(fr, 3), 64 * pop(fr, 3), 0, toggle(fr, 3)),
          kind="ellipse")
    icon(s, "Me gusta", THUMB, 232, 746, 34, 6)
    s.say("LIKE THE VIDEO", (280, 732, 556, 764), M, 800, "#222222", "Texto", align="left",
          reveal=lambda fr: (188, 0, 188 + 392 * k(fr, 12, 9), 1080))
    cursor(s, [(18, 760, 1040), (33, 500, 800), (45, 500, 800), (60, 640, 1000)], kind="hand", click=[36])
    return t


def like_column():
    """q3: a red dot grows up into a column with the like, play and bell icons; white tags slide out of it: LIKE,
    SUBSCRIBE, GET NOTIFIED."""
    D = dur_for(3.4, 1.6)
    t = _p("like-column", "Tercio: columna roja con tres etiquetas", "Lower third: red column with three tags", 12935,
           D, "lowerthirds", ["me gusta", "suscribirse", "campana"])
    s = S(t, D)
    rows = (("LIKE", 752, THUMB, 320), ("SUBSCRIBE", 860, None, 400), ("GET NOTIFIED", 968, BELL, 440))
    for i, (text, y, path, x1) in enumerate(rows):
        at = 78 + 6 * i
        s.rect(f"Etiqueta {i + 1}", solid(WHITE), lambda fr, u, y=y, x1=x1, at=at: (
            150, y - 32, 150 + (x1 - 150) * k(fr, at, 9), y + 32), radius=32, base=(x1 - 150, 64))
        s.say(text, (216, y - 13, 216 + 15 * len(text) * 1.1, y + 13), M, 800, SUBRED, f"Texto {i + 1}", align="left",
              reveal=lambda fr, x1=x1, at=at: (150, 0, 150 + (x1 - 150) * k(fr, at, 9), 1080))
    s.rect("Columna", solid("#FF3D4A"), lambda fr, u: (100, 1032 - 328 * k(fr, 12, 18) - 100 * (1 - toggle(fr, 3)),
                                                       200, 1032), op=lambda fr, u: toggle(fr, 3), radius=50,
           base=(100, 328))
    for i, (text, y, path, x1) in enumerate(rows):
        if path:
            icon(s, f"Ícono {i + 1}", path, 150, y, 40, 30 + 6 * i, rot=0)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, y=y, i=i: (150, y, pop(fr, 30 + 6 * i), 0, toggle(fr, 30 + 6 * i)),
                52, 36, body=solid(WHITE), tri=SUBRED)
    return t


def avatar_cycle():
    """q4: the avatar pops and a white tag beside it changes: LIKE THE VIDEO, SUBSCRIBE, GET NOTIFIED."""
    D = dur_for(4.0, 1.4)
    t = _p("avatar-cycle", "Tercio: avatar y etiqueta que cambia", "Lower third: avatar and a changing tag", 12936, D,
           "lowerthirds", ["avatar", "me gusta", "suscribirse"])
    s = S(t, D)
    shape_photo(s, "fx-man-03", lambda fr, u: (276, 864, 168 * pop(fr, 6), 168 * pop(fr, 6)),
                op=lambda fr, u: toggle(fr, 6), label="Tu foto de perfil")
    stages = ((9, 57, "LIKE THE VIDEO", THUMB, BLUE), (60, 108, "SUBSCRIBE", None, SUBRED),
              (111, None, "GET NOTIFIED", BELL, GOLD))
    for i, (a, b, text, path, colour) in enumerate(stages):
        w = 60 + 22 * len(text)
        r = lambda fr, a=a, b=b, w=w: (400, 828, 400 + w * k(fr, a, 8) * (1 - (k(fr, b, 6) if b else 0)), 900)  # noqa: E731
        s.rect(f"Etiqueta {i + 1}", solid(WHITE), lambda fr, u, r=r: r(fr), radius=36, base=(w, 72))
        s.say(text, (430, 850, 430 + 19 * len(text), 878), M, 800, SUBRED, f"Texto {i + 1}", align="left",
              reveal=lambda fr, r=r: r(fr))
        if path:
            s.obj(f"Ícono {i + 1}", solid(colour), lambda fr, u, a=a, b=b, w=w: (
                400 + w - 44, 864, 34 * pop(fr, a + 6), 34 * pop(fr, a + 6), 0, swap_op(fr, a + 6, b, 2)), path=path)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, a=a, b=b, w=w: (400 + w - 44, 864, pop(fr, a + 6), 0,
                                                                  swap_op(fr, a + 6, b, 2)), 44, 30, body=solid(SUBRED))
    return t


SPEECH = poly([(0, 0), (100, 0), (100, 82), (62, 82), (50, 100), (38, 82), (0, 82)])


# --- G9 (71.4-75.2 s), 2×2 grid of subscribe lower thirds ---------------------------------------------------------
def sub_grey_bell():
    """q1: a white SUBSCRIBE pill opens, the pointer clicks it, it turns grey SUBSCRIBED; a white circle with the play
    button pops at its left and a bell lights yellow at its right."""
    D = dur_for(2.6, 1.4)
    t = _p("sub-grey-bell", "Tercio: suscribirse que se vuelve gris y campana", "Lower third: subscribe turning grey "
           "and a bell", 12937, D, "lowerthirds", ["suscribirse", "campana", "clic"])
    s = S(t, D)
    r = lambda fr: (960 - 180 * k(fr, 2, 9), 844, 960 + 180 * k(fr, 2, 9), 920)  # noqa: E731
    s.rect("Píldora", solid(WHITE), lambda fr, u: r(fr), op=lambda fr, u: 1 - toggle(fr, 30), radius=12, base=(360, 76))
    s.rect("Píldora (gris)", solid("#9A9A9A"), lambda fr, u: r(fr), op=lambda fr, u: toggle(fr, 30), radius=12,
           base=(360, 76))
    s.say("SUBSCRIBE", (860, 868, 1060, 896), M, 800, SUBRED, "Texto", op=lambda fr, u: toggle(fr, 6) * (1 - toggle(fr, 30)))
    s.say("SUBSCRIBED", (856, 868, 1064, 896), M, 800, WHITE, "Texto 2", op=lambda fr, u: toggle(fr, 30))
    s.obj("Círculo", solid(WHITE), lambda fr, u: (664, 884, 184 * pop(fr, 42), 184 * pop(fr, 42), 0, toggle(fr, 42)),
          kind="ellipse")
    s.obj("Círculo (aro)", ring(SUBRED, 8), lambda fr, u: (664, 884, 168 * pop(fr, 42), 168 * pop(fr, 42), 0,
                                                           toggle(fr, 42)), kind="ellipse", base=(168, 168))
    ytb(s, "Botón", lambda fr, u: (664, 884, pop(fr, 45), 0, toggle(fr, 45)), 100, 70, body=solid(SUBRED))
    icon(s, "Campana", BELL, 1204, 884, 68, 45, "#9A9A9A")
    s.obj("Campana (encendida)", solid(GOLD), lambda fr, u: (1204, 884, 68, 68, 12 * math.sin(fr / 2) * (1 - k(fr, 84, 12)),
                                                              toggle(fr, 72)), path=BELL)
    cursor(s, [(9, 1200, 1100), (24, 990, 900), (36, 990, 900), (48, 1240, 1060)], click=[27])
    return t


def sub_channel_tag():
    """q2: a red dot opens into a SUBSCRIBE pill, the pointer clicks it into SUBSCRIBED, a small CHANNEL NAME tag
    pops above it and a bell tab slides out at its right."""
    D = dur_for(2.4, 1.6)
    t = _p("sub-channel-tag", "Tercio: suscrito con nombre del canal", "Lower third: subscribed with the channel name",
           12938, D, "lowerthirds", ["suscribirse", "clic"])
    s = S(t, D)
    s.rect("Pestaña", solid(WHITE), lambda fr, u: (1080, 872, 1080 + 120 * k(fr, 57, 9), 932), radius=30, base=(120, 60))
    icon(s, "Campana", BELL, 1166, 902, 34, 63, GOLD)
    s.obj("Píldora", solid(SUBRED), lambda fr, u: (968, 902, 40 + 264 * k(fr, 6, 9), 68 * pop(fr, 3), 0, toggle(fr, 3)),
          radius=34, base=(304, 68))
    s.say("SUBSCRIBE", (876, 888, 1060, 916), M, 800, WHITE, "Texto", op=lambda fr, u: toggle(fr, 12) * (1 - toggle(fr, 36)))
    s.say("SUBSCRIBED", (868, 888, 1068, 916), M, 800, WHITE, "Texto 2", op=lambda fr, u: toggle(fr, 36))
    s.obj("Etiqueta", solid(WHITE), lambda fr, u: (970, 834, 236 * pop(fr, 48), 36 * pop(fr, 48), 0, toggle(fr, 48)),
          radius=18, base=(236, 36))
    s.say("CHANNEL NAME", (900, 826, 1040, 844), M, 800, SUBRED, "Texto 3", op=lambda fr, u: toggle(fr, 51))
    cursor(s, [(18, 1200, 1080), (30, 980, 920), (42, 980, 920), (54, 1220, 1060)], click=[33])
    return t


def sub_stack():
    """q3: three red tags slide out one under the other (like, notify, subscribed), the channel name types over
    them and the avatar pops."""
    D = dur_for(1.6, 2.0)
    t = _p("sub-stack", "Tercio: avatar y tres etiquetas rojas", "Lower third: avatar and three red tags", 12939, D,
           "lowerthirds", ["suscribirse", "avatar"])
    s = S(t, D)
    for i, (text, y, path) in enumerate((("LIKE THE VIDEO", 854, THUMB), ("GET NOTIFIED", 918, BELL),
                                         ("SUBSCRIBED", 986, None))):
        at = 6 + 4 * i
        r = lambda fr, y=y, at=at, i=i: (412, y - 22 - 4 * (i == 2), 412 + 248 * k(fr, at, 8), y + 22 + 4 * (i == 2))  # noqa: E731
        s.rect(f"Etiqueta {i + 1}", solid("#FF3D4A"), lambda fr, u, r=r: r(fr), radius=22, base=(248, 44))
        s.say(text, (438, y - 9, 438 + 11.5 * len(text), y + 9), M, 800, WHITE, f"Texto {i + 1}", align="left",
              reveal=lambda fr, r=r: r(fr))
        if path:
            icon(s, f"Ícono {i + 1}", path, 630, y, 22, at + 6)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, y=y, at=at: (630, y, pop(fr, at + 6), 0, toggle(fr, at + 6)), 30, 22,
                body=solid(WHITE), tri=SUBRED)
    c = s.say("CHANNEL NAME", (400, 756, 668, 784), M, 800, WHITE, "Título", align="left")
    s.typed(c, 18, stagger=0.03, duration=0.03)
    shape_photo(s, "fx-woman-02", lambda fr, u: (534, 654, 140 * pop(fr, 24), 140 * pop(fr, 24)),
                op=lambda fr, u: toggle(fr, 24), label="Tu foto de perfil")
    s.obj("Avatar (aro)", ring(WHITE, 5), lambda fr, u: (534, 654, 144 * pop(fr, 24), 144 * pop(fr, 24), 0,
                                                         toggle(fr, 24)), kind="ellipse", base=(144, 144))
    return t


def bubble_swap():
    """q4: a red speech bubble pops tilted with a like and LIKE THE VIDEO; it spins and comes back as the play
    button with SUBSCRIBE."""
    D = dur_for(2.8, 1.4)
    t = _p("bubble-swap", "Tercio: globo rojo que cambia de me gusta a suscribirse", "Lower third: red bubble from like "
           "to subscribe", 12940, D, "lowerthirds", ["me gusta", "suscribirse", "globo"])
    s = S(t, D)
    spin = lambda fr: -20 * (1 - k(fr, 3, 9)) + 360 * k(fr, 69, 9)  # noqa: E731
    sz = lambda fr: pop(fr, 3) * (1 - 0.4 * math.sin(math.pi * k(fr, 69, 9)))  # noqa: E731
    s.obj("Globo", solid("#F5323F"), lambda fr, u: (284, 876, 152 * sz(fr), 152 * sz(fr), spin(fr), toggle(fr, 3)),
          path=SPEECH)
    s.obj("Me gusta", solid(WHITE), lambda fr, u: (284, 864, 64 * sz(fr), 64 * sz(fr), spin(fr),
                                                   toggle(fr, 6) * (1 - toggle(fr, 73))), path=THUMB)
    ytb(s, "Botón", lambda fr, u: (284, 864, sz(fr), spin(fr), toggle(fr, 73)), 76, 54, body=solid(WHITE), tri="#F5323F")
    s.say("LIKE THE VIDEO", (400, 844, 680, 876), M, 800, WHITE, "Texto",
          reveal=lambda fr: (380, 0, 380 + 320 * k(fr, 6, 9), 1080), op=lambda fr, u: 1 - k(fr, 66, 3))
    s.say("SUBSCRIBE", (400, 844, 608, 876), M, 800, WHITE, "Texto 2",
          reveal=lambda fr: (380, 0, 380 + 260 * k(fr, 75, 9), 1080))
    return t


SPARK = " ".join(poly([(50 + 46 * math.cos(math.radians(a)) - 4, 50 + 46 * math.sin(math.radians(a)) - 4),
                        (50 + 46 * math.cos(math.radians(a)) + 4, 50 + 46 * math.sin(math.radians(a)) - 4),
                        (50 + 46 * math.cos(math.radians(a)) + 4, 50 + 46 * math.sin(math.radians(a)) + 4),
                        (50 + 46 * math.cos(math.radians(a)) - 4, 50 + 46 * math.sin(math.radians(a)) + 4)])
                  for a in range(0, 360, 30))


def sparkle(s, name, cx, cy, size, at):
    """A ring of small squares that bursts out and fades (a click sparkle)."""
    s.obj(name, solid(WHITE), lambda fr, u: (cx, cy, size * (0.6 + 0.6 * k(fr, at, 9)), size * (0.6 + 0.6 * k(fr, at, 9)),
                                             0, toggle(fr, at) * (1 - k(fr, at + 6, 6))), path=SPARK)


# --- G10 (75.2-80.3 s), 2×2 grid of subscribe lower thirds ---------------------------------------------------------
def tilted_cycle():
    """q1: a tilted outlined tag with a red dot changes word: LIKE, SUBSCRIBE, GET NOTIFIED."""
    D = dur_for(4.2, 1.2)
    t = _p("tilted-cycle", "Tercio: etiqueta inclinada que cambia de palabra", "Lower third: tilted tag changing words",
           12941, D, "lowerthirds", ["me gusta", "suscribirse", "campana"])
    s = S(t, D)
    stages = ((6, 48, "LIKE", THUMB, 220), (63, 111, "SUBSCRIBE", None, 330), (120, None, "GET NOTIFIED", BELL, 380))
    for i, (a, b, text, path, w) in enumerate(stages):
        sc = lambda fr, a=a, b=b: pop(fr, a, 6) * (1 - (k(fr, b, 6) if b else 0))  # noqa: E731
        s.obj(f"Etiqueta {i + 1}", ring(WHITE, 5), lambda fr, u, sc=sc, w=w: (
            228 + w / 2, 912, w * sc(fr), 120 * sc(fr), -6, 1.0 if sc(fr) > 0.01 else 0.0), radius=12, base=(w, 120))
        ink = (228 + 28, 896, 228 + w - 28, 932)
        s.say(text, ink, M, 800, WHITE, f"Texto {i + 1}", geom=lambda fr, u, sc=sc, ink=ink, w=w: (
            *s.about(ink, 228 + w / 2, 912, sc(fr), -6), max(0.01, sc(fr)), -6, 1.0 if sc(fr) > 0.01 else 0.0))
        s.obj(f"Punto {i + 1}", solid("#F5323F"), lambda fr, u, sc=sc: (244, 856, 84 * sc(fr), 84 * sc(fr), 0,
                                                                        1.0 if sc(fr) > 0.01 else 0.0), kind="ellipse")
        if path:
            s.obj(f"Ícono {i + 1}", solid(WHITE), lambda fr, u, sc=sc, path=path: (244, 856, 44 * sc(fr), 44 * sc(fr), 0,
                                                                                    1.0 if sc(fr) > 0.01 else 0.0),
                  path=path)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, sc=sc: (244, 856, max(0.01, sc(fr)), 0, 1.0 if sc(fr) > 0.01 else 0.0),
                48, 34, body=solid(WHITE), tri="#F5323F")
    s.rect("Línea", solid(WHITE), lambda fr, u: (160, 958, 160 + 60 * k(fr, 3, 6), 962), rot=lambda fr, u: -40)
    return t


def three_icons():
    """q2: three faint icons appear in a row; the like turns blue with a sparkle, then the play button red, then the
    bell yellow."""
    D = dur_for(3.0, 1.4)
    t = _p("three-icons", "Tercio: me gusta, play y campana que se encienden", "Lower third: like, play and bell "
           "lighting up", 12942, D, "lowerthirds", ["me gusta", "campana"])
    s = S(t, D)
    for i, (x, path, colour, at) in enumerate(((508, THUMB, BLUE, 24), (952, None, "#F5323F", 54), (1368, BELL, GOLD, 84))):
        if path:
            s.obj(f"Ícono {i + 1}", solid(WHITE, 0.5), lambda fr, u, x=x, i=i, at=at: (x, 904, 88 * pop(fr, 6 + 3 * i), 88 * pop(fr, 6 + 3 * i),
                                                                           0, toggle(fr, 6 + 3 * i) * (1 - toggle(fr, at))),
                  path=path)
            s.obj(f"Ícono {i + 1} (color)", solid(colour), lambda fr, u, x=x, at=at: (x, 904, 88 * pop(fr, at), 88 * pop(fr, at),
                                                                                    0, toggle(fr, at)), path=path)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, x=x, i=i, at=at: (x, 904, pop(fr, 6 + 3 * i), 0, toggle(fr, 6 + 3 * i) * (1 - toggle(fr, at))),
                112, 76, body=solid(WHITE, 0.5), tri="#999999")
            ytb(s, f"Ícono {i + 1} (color)", lambda fr, u, x=x, at=at: (x, 904, pop(fr, at), 0, toggle(fr, at)), 112, 76,
                body=solid(colour))
        sparkle(s, f"Destello {i + 1}", x, 904, 170, at)
    return t


def subscribed_click():
    """q3: a red SUBSCRIBE bar opens, the pointer clicks it into SUBSCRIBED and sparkles burst."""
    D = dur_for(2.2, 1.6)
    t = _p("subscribed-click", "Tercio: barra roja de suscribirse con clic", "Lower third: red subscribe bar with a "
           "click", 12943, D, "lowerthirds", ["suscribirse", "clic"])
    s = S(t, D)
    s.rect("Barra", solid("#F5323F"), lambda fr, u: (916 - 256 * k(fr, 3, 9), 904, 916 + 256 * k(fr, 3, 9), 992),
           radius=12, base=(512, 88))
    ytb(s, "Botón", lambda fr, u: (724, 948, pop(fr, 9), 0, toggle(fr, 9)), 76, 54, body=solid(WHITE), tri="#F5323F")
    s.say("SUBSCRIBE", (790, 930, 1060, 966), M, 800, WHITE, "Texto", op=lambda fr, u: toggle(fr, 9) * (1 - toggle(fr, 45)))
    s.say("SUBSCRIBED", (790, 930, 1150, 966), M, 800, WHITE, "Texto 2", op=lambda fr, u: toggle(fr, 45))
    cursor(s, [(21, 1300, 1080), (36, 1000, 970), (48, 1000, 970), (60, 1100, 1060)], kind="hand", click=[42])
    for i, (x, y) in enumerate(((1190, 900), (1230, 960), (640, 900))):
        sparkle(s, f"Destello {i + 1}", x, y, 60, 45 + 2 * i)
    return t


def profile_card():
    """q4: a small white card opens upwards with the avatar, an outlined SUBSCRIBE and a bell and a like."""
    D = dur_for(1.2, 2.0)
    t = _p("profile-card", "Tercio: tarjeta blanca con avatar", "Lower third: white card with an avatar", 12944, D,
           "lowerthirds", ["avatar", "suscribirse"])
    s = S(t, D)
    s.rect("Tarjeta", solid(WHITE), lambda fr, u: (344, 988 - 264 * k(fr, 9, 9), 548, 988), radius=18, base=(204, 264))
    shape_photo(s, "fx-man-04", lambda fr, u: (446, 800, 112 * pop(fr, 18), 112 * pop(fr, 18)),
                op=lambda fr, u: toggle(fr, 18), label="Tu foto de perfil")
    s.obj("Suscribirse", ring("#F5323F", 3), lambda fr, u: (446, 888, 140 * pop(fr, 21), 30 * pop(fr, 21), 0,
                                                            toggle(fr, 21)), radius=15, base=(140, 30))
    s.say("SUBSCRIBE", (404, 882, 488, 894), M, 800, "#F5323F", "Texto", op=lambda fr, u: k(fr, 24, 3))
    icon(s, "Campana", BELL, 420, 944, 28, 24, GOLD)
    icon(s, "Me gusta", THUMB, 472, 944, 28, 26, BLUE)
    return t


# --- G11 (80.3-86.2 s), 2×2 grid of call-to-action lower thirds ---------------------------------------------------
def notify_bell():
    """q1: GET NOTIFIED types and a yellow bell pops beside it and keeps ringing."""
    D = dur_for(0.8, 2.6)
    t = _p("notify-bell", "Tercio: notificaciones con campana que suena", "Lower third: notifications with a ringing "
           "bell", 12945, D, "lowerthirds", ["campana"])
    s = S(t, D)
    c = s.say("GET NOTIFIED", (692, 856, 1000, 896), M, 800, WHITE, align="left")
    s.typed(c, 3, stagger=0.04, duration=0.03)
    s.obj("Campana", solid(GOLD), lambda fr, u: (1104, 876, 88 * pop(fr, 12), 88 * pop(fr, 12),
                                                 16 * math.sin(2 * math.pi * u * 2.5), toggle(fr, 12)), path=BELL)
    return t


def subscribe_icon():
    """q2: SUBSCRIBE types and a red play button spins in beside it."""
    D = dur_for(1.0, 2.4)
    t = _p("subscribe-icon", "Tercio: suscribirse con botón que gira", "Lower third: subscribe with a spinning button",
           12946, D, "lowerthirds", ["suscribirse", "botón"])
    s = S(t, D)
    c = s.say("SUBSCRIBE", (700, 876, 960, 912), M, 800, WHITE, align="left")
    s.typed(c, 3, stagger=0.04, duration=0.03)
    ytb(s, "Botón", lambda fr, u: (1078, 894, pop(fr, 9, 9), -40 * (1 - k(fr, 9, 18)), toggle(fr, 9)), 132, 92,
        body=solid("#F5323F"))
    return t


def like_hand():
    """q3: LIKE THE VIDEO types and a white like hand pops beside it with a yellow sparkle."""
    D = dur_for(1.0, 2.4)
    t = _p("like-hand", "Tercio: me gusta con mano", "Lower third: like the video with a hand", 12947, D, "lowerthirds",
           ["me gusta"])
    s = S(t, D)
    c = s.say("LIKE THE VIDEO", (640, 860, 992, 900), M, 800, WHITE, align="left")
    s.typed(c, 3, stagger=0.035, duration=0.03)
    s.obj("Me gusta (borde)", solid("#F5323F"), lambda fr, u: (1100, 872, 120 * pop(fr, 9), 120 * pop(fr, 9),
                                                               -15 * (1 - k(fr, 9, 9)), toggle(fr, 9)), path=THUMB)
    s.obj("Me gusta", solid(WHITE), lambda fr, u: (1104, 876, 96 * pop(fr, 9), 96 * pop(fr, 9), -15 * (1 - k(fr, 9, 9)),
                                                   toggle(fr, 9)), path=THUMB)
    sparkle(s, "Destello", 1100, 872, 220, 12)
    return t


def three_pills():
    """q4: three red circles with white tags pop one after another along the bottom: LIKE THE VIDEO, SUBSCRIBE,
    GET NOTIFIED; the pointer clicks each one."""
    D = dur_for(4.4, 1.2)
    t = _p("three-pills", "Tercio: tres botones en fila", "Lower third: three buttons in a row", 12948, D, "lowerthirds",
           ["me gusta", "suscribirse", "campana"])
    s = S(t, D)
    rows = ((340, "LIKE THE VIDEO", THUMB, 6), (868, "SUBSCRIBE", None, 48), (1368, "GET NOTIFIED", BELL, 114))
    for i, (cx, text, path, at) in enumerate(rows):
        w = 264 if i != 1 else 248
        s.rect(f"Etiqueta {i + 1}", solid(WHITE), lambda fr, u, cx=cx, w=w, at=at: (cx + 30, 904, cx + 30 + w * k(fr, at + 3, 8),
                                                                                  952), radius=24, base=(w, 48))
        s.say(text, (cx + 76, 918, cx + 76 + 13 * len(text), 938), M, 800, "#F5323F", f"Texto {i + 1}", align="left",
              reveal=lambda fr, cx=cx, w=w, at=at: (cx, 0, cx + 30 + w * k(fr, at + 3, 8), 1080))
        s.obj(f"Círculo {i + 1}", solid("#F5323F"), lambda fr, u, cx=cx, at=at: (cx, 928, 112 * pop(fr, at), 112 * pop(fr, at),
                                                                                0, toggle(fr, at)), kind="ellipse")
        if path:
            icon(s, f"Ícono {i + 1}", path, cx, 926, 52, at + 2)
        else:
            ytb(s, f"Ícono {i + 1}", lambda fr, u, cx=cx, at=at: (cx, 928, pop(fr, at + 2), 0, toggle(fr, at + 2)), 60, 42,
                body=solid(WHITE), tri="#F5323F")
    cursor(s, [(9, 600, 1060), (18, 380, 960), (30, 380, 960), (45, 900, 960), (57, 900, 960), (108, 1400, 960),
               (120, 1400, 960), (132, 1472, 1028)], click=[21, 51, 117])
    return t


CORAL = "#F65456"
BIRD = poly([(0, 78), (20, 82), (8, 60), (0, 40), (22, 52), (30, 20), (54, 10), (72, 18), (100, 8), (88, 26), (98, 30),
             (82, 40), (76, 70), (52, 94), (24, 100)])


def social_icons(s, xs, y, at, colour=WHITE, size=40, labels=True, label_dy=44, kinds=("ig", "fb", "tw"), ys=None,
                 label_right=False):
    """Instagram, Facebook and Twitter glyphs (simple shapes) in a row, each with an @username under it."""
    for i, (x, kind) in enumerate(zip(xs, kinds)):
        a = at + 2 * i
        y = ys[i] if ys else y
        if kind == "ig":
            s.obj(f"Instagram {i + 1}", ring(colour, 4), lambda fr, u, x=x, a=a, y=y: (x, y, size * pop(fr, a), size * pop(fr, a), 0,
                                                                                 toggle(fr, a)), radius=size * 0.28,
                  base=(size, size))
            s.obj(f"Instagram {i + 1} (lente)", ring(colour, 4), lambda fr, u, x=x, a=a, y=y: (
                x, y, size * 0.45 * pop(fr, a), size * 0.45 * pop(fr, a), 0, toggle(fr, a)), kind="ellipse",
                base=(size * 0.45, size * 0.45))
        elif kind == "fb":
            s.say("f", (x - size * 0.22, y - size * 0.5, x + size * 0.22, y + size * 0.5), "Lato", 900, colour,
                  f"Facebook {i + 1}", editable=False, op=lambda fr, u, a=a: toggle(fr, a))
        elif kind == "yt":
            ytb(s, f"YouTube {i + 1}", lambda fr, u, x=x, a=a, y=y: (x, y, pop(fr, a), 0, toggle(fr, a)), size * 1.2, size * 0.85,
                body=solid(colour), tri=CORAL)
        else:
            s.obj(f"Twitter {i + 1}", solid(colour), lambda fr, u, x=x, a=a, y=y: (x, y, size * pop(fr, a), size * 0.85 * pop(fr, a),
                                                                             0, toggle(fr, a)), path=BIRD)
        if labels and label_right:
            s.say("@username", (x + size * 0.8, y - size * 0.24, x + size * 0.8 + 4 * size, y + size * 0.24), M, 700, colour,
                  f"Usuario {i + 1}", align="left", op=lambda fr, u, a=a: k(fr, a + 3, 4))
        elif labels:
            s.say("@username", (x - size * 1.15, y + label_dy - 9, x + size * 1.15, y + label_dy + 9), M, 700, colour,
                  f"Usuario {i + 1}", op=lambda fr, u, a=a: k(fr, a + 3, 4))


def video_slot(s, name, rect, sample, at, border=WHITE, width=6, n=9):
    """A photo slot in a white frame: the frame draws, then the photo opens inside it."""
    x0, y0, x1, y1 = rect
    photo(s, sample, lambda fr, u: (x0 + width, y0 + width, x0 + width + (x1 - x0 - 2 * width) * k(fr, at + n - 3, 6),
                                    y1 - width), name=name)
    s.outline(f"{name} (marco)", rect_pts(x0, y0, x1, y1, "tl"), width, border, at=at, n=n)


def avatar(s, sample, cx, cy, d, at, ring_colour=WHITE, ring_w=8, name="Avatar"):
    shape_photo(s, sample, lambda fr, u: (cx, cy, d * pop(fr, at), d * pop(fr, at)), op=lambda fr, u: toggle(fr, at),
                label="Tu foto de perfil", name=name)
    s.obj(f"{name} (aro)", ring(ring_colour, ring_w), lambda fr, u: (cx, cy, (d + ring_w) * pop(fr, at),
                                                                     (d + ring_w) * pop(fr, at), 0, toggle(fr, at)),
          kind="ellipse", base=(d + ring_w, d + ring_w))


def pill_text(s, name, text, rect, at, fill_colour=WHITE, ink_colour=CORAL, outline=False):
    x0, y0, x1, y1 = rect
    s.rect(name, ring(fill_colour, 4) if outline else solid(fill_colour), lambda fr, u: (
        (x0 + x1) / 2 - (x1 - x0) / 2 * k(fr, at, 6), y0, (x0 + x1) / 2 + (x1 - x0) / 2 * k(fr, at, 6), y1),
        radius=0 if outline else (y1 - y0) / 2, base=(x1 - x0, y1 - y0))
    h = (y1 - y0) * 0.26
    s.say(text, (x0 + 18, (y0 + y1) / 2 - h, x1 - 18, (y0 + y1) / 2 + h), M, 800, ink_colour, f"{name} (texto)",
          op=lambda fr, u: k(fr, at + 3, 4))


# --- E1 (86.2-91.3 s), 2×2 grid of end screens -------------------------------------------------------------------
def end_circle():
    """q1: a white dot grows into the avatar, a coral circle rises from the bottom, the thanks types, the
    recommended video opens and the socials and buttons pop."""
    D = dur_for(2.4, 1.8)
    t = _p("end-circle", "Pantalla final: semicírculo coral y video recomendado", "End screen: coral half circle and "
           "a recommended video", 12949, D, "pantallas-finales", ["agradecimiento", "coral"], thumb=3.2)
    s = S(t, D)
    s.obj("Semicírculo", solid(CORAL), lambda fr, u: (1040, 1920 + 680 * (1 - k(fr, 27, 12)), 2400, 2400, 0, 1), kind="ellipse")
    c = s.say("THANK YOU", (152, 232, 788, 292), M, 900, WHITE, "Título")
    s.typed(c, 33, stagger=0.04, duration=0.03)
    c = s.say("FOR WATCHING!", (152, 308, 788, 368), M, 900, WHITE, "Título 2")
    s.typed(c, 39, stagger=0.04, duration=0.03)
    social_icons(s, (220, 456, 704), 500, 48)
    video_slot(s, "Video", (1024, 60, 1592, 520), "fx-couple-01", 42)
    pill_text(s, "Recomendado", "RECOMMENDED VIDEO", (1272, 558, 1592, 598), 51)
    avatar(s, "fx-woman-03", 964, 680, 216, 6)
    pill_text(s, "Suscribirse", "SUBSCRIBE", (592, 906, 912, 962), 54)
    for i, line in enumerate(("DON'T FORGET", "TO LIKE & COMMENT")):
        s.say(line, (1000, 898 + 36 * i, 1000 + 15.5 * len(line), 922 + 36 * i), M, 800, WHITE, f"Texto {i + 1}",
              align="left", op=lambda fr, u: k(fr, 57, 6))
    return t


def end_side_panel():
    """q2: a coral panel slides in from the left with a white edge; the thanks, the avatar, SUBSCRIBE and the
    socials appear in it; on the right, under a dark veil, the previous and next videos open."""
    D = dur_for(2.4, 1.8)
    t = _p("end-side-panel", "Pantalla final: panel coral y dos videos", "End screen: coral panel and two videos", 12950,
           D, "pantallas-finales", ["agradecimiento", "coral"], thumb=3.2)
    s = S(t, D)
    s.rect("Velo", solid(BLACK, 0.45), lambda fr, u: (840, -10, 1930, 1090), op=lambda fr, u: k(fr, 18, 9))
    edge = lambda fr: 840 * k(fr, 9, 12)  # noqa: E731
    s.rect("Panel (borde)", solid(WHITE), lambda fr, u: (edge(fr) - 10, -10, edge(fr) + 70 * (1 - k(fr, 21, 6)), 1090))
    s.rect("Panel", solid(CORAL), lambda fr, u: (-10, -10, edge(fr), 1090))
    for i, line in enumerate(("THANK YOU", "FOR WATCHING!")):
        rise(s, line, (420 - 150 - 28 * (i == 1), 64 + 54 * i, 420 + 150 + 28 * (i == 1), 104 + 54 * i), 21 + 3 * i,
             f"Título {i + 1}" if i else "Título", align="center", weight=900)
    avatar(s, "fx-man-05", 420, 388, 272, 30)
    s.obj("Avatar (arco)", ring(WHITE, 4), lambda fr, u: (420, 388, 320, 320, 200 * k(fr, 30, 18), k(fr, 30, 6)),
          path=arc(-60, 160))
    pill_text(s, "Suscribirse", "SUBSCRIBE", (260, 600, 580, 656), 39)
    s.say("DON'T FORGET TO LIKE & COMMENT", (196, 756, 644, 776), M, 800, WHITE, "Texto", op=lambda fr, u: k(fr, 45, 6))
    social_icons(s, (188, 420, 660), 940, 48)
    for i, (label, y0, sample) in enumerate((("PREVIOUS VIDEO", 168, "fx-walk-01"), ("NEXT VIDEO", 668, "fx-walk-02"))):
        s.say(label, (1452 - 9 * len(label) * 1.3, 116 + 500 * i, 1452 + 9 * len(label) * 1.3, 148 + 500 * i), M, 800,
              WHITE, f"Etiqueta {i + 1}", op=lambda fr, u, i=i: k(fr, 36 + 6 * i, 6))
        video_slot(s, f"Video {i + 1}", (1160, y0, 1748, y0 + 348), sample, 33 + 6 * i)
    return t


def end_diagonal():
    """q3: a coral panel with a slanted edge sweeps in from the right with the thanks, the avatar and SUBSCRIBE; on
    the darkened left the next video opens with the socials under it."""
    D = dur_for(2.4, 1.8)
    t = _p("end-diagonal", "Pantalla final: panel coral inclinado y siguiente video", "End screen: slanted coral panel "
           "and the next video", 12951, D, "pantallas-finales", ["agradecimiento", "coral"], thumb=3.2)
    s = S(t, D)
    s.rect("Velo", solid("#3A3A3A", 0.55), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: k(fr, 6, 9))
    off = lambda fr: 1500 * (1 - k(fr, 0, 12))  # noqa: E731
    s.rect("Panel", solid(CORAL), lambda fr, u: (772 + off(fr), -10, 2400 + off(fr), 1090),
           path=poly([(0, 0), (100, 0), (100, 100), (25, 100)]))
    for i, line in enumerate(("THANK YOU", "FOR WATCHING!")):
        rise(s, line, (1532 - 150 - 32 * (i == 1), 172 + 52 * i, 1532 + 150 + 32 * (i == 1), 214 + 52 * i), 15 + 3 * i,
             f"Título {i + 1}" if i else "Título", align="center", weight=900)
    avatar(s, "fx-woman-04", 1532, 456, 272, 24, ring_colour=CORAL, ring_w=2)
    for i, line in enumerate(("SUBSCRIBE", "FOR MORE VIDEOS")):
        s.say(line, (1532 - 11.5 * len(line), 676 + 44 * i, 1532 + 11.5 * len(line), 706 + 44 * i), M, 800, WHITE,
              f"Texto {i + 1}", op=lambda fr, u: k(fr, 33, 6))
    s.rect("Subrayado", solid(WHITE), lambda fr, u: (1532 - 242 * k(fr, 36, 9), 766, 1532 + 242 * k(fr, 36, 9), 770))
    pill_text(s, "Suscribirse", "SUBSCRIBE", (1372, 804, 1696, 864), 42)
    s.say("NEXT VIDEO", (300, 300, 740, 340), M, 900, WHITE, "Etiqueta", op=lambda fr, u: k(fr, 30, 6))
    video_slot(s, "Video", (100, 360, 840, 812), "fx-woman-05", 30)
    social_icons(s, (232, 460, 712), 860, 45)
    return t


def end_big_arc():
    """q4: a huge coral circle drops from the top with a white rim; the thanks, the avatar between the previous
    and next videos, the reminder box and a column of socials appear."""
    D = dur_for(2.2, 2.0)
    t = _p("end-big-arc", "Pantalla final: gran arco coral y dos videos", "End screen: big coral arc and two videos",
           12952, D, "pantallas-finales", ["agradecimiento", "coral"], thumb=3.2)
    s = S(t, D)
    cy = lambda fr: 13 - 1300 * (1 - k(fr, 0, 15))  # noqa: E731
    s.obj("Arco (borde)", solid(WHITE), lambda fr, u: (960, cy(fr), 2134, 2134, 0, 1), kind="ellipse")
    s.obj("Arco", solid(CORAL), lambda fr, u: (960, cy(fr), 2118, 2118, 0, 1), kind="ellipse")
    c = s.say("THANK YOU FOR WATCHING!", (400, 88, 1512, 148), M, 900, WHITE)
    s.typed(c, 15, stagger=0.025, duration=0.03)
    for i, (rect, sample, label) in enumerate((((188, 260, 728, 572), "h-city-01",
                                                "PREVIOUS VIDEO"), ((1184, 260, 1724, 572), "fx-beach-01", "NEXT VIDEO"))):
        video_slot(s, f"Video {i + 1}", rect, sample, 18 + 3 * i)
        cx = (rect[0] + rect[2]) / 2
        s.say(label, (cx - 8.6 * len(label), 600, cx + 8.6 * len(label), 618), M, 800, WHITE, f"Etiqueta {i + 1}",
              op=lambda fr, u: k(fr, 30, 6))
    avatar(s, "fx-man-06", 960, 408, 224, 15, ring_colour=WHITE, ring_w=10)
    pill_text(s, "Recordatorio", "DON'T FORGET TO LIKE & COMMENT", (528, 728, 1384, 804), 33, outline=True,
              ink_colour=WHITE)
    social_icons(s, (112, 112, 112), 0, 39, size=36, ys=(848, 908, 972), label_right=True)
    return t


def logo_pattern(s, colour="#F03E42", tri="#F94B4D", alpha=1.0, tilt=-15.0, drift=(-30.0, -20.0)):
    """The pack's background: rows of play buttons, a shade darker than the coral, tilted and drifting."""
    W, H = 2800.0, 2000.0
    bodies, tris = [], []
    for j in range(12):
        for i in range(16):
            x = i * 280 + (140 if j % 2 else 0)
            y = j * 200
            bx0, by0, bx1, by1 = x, y, x + 120, y + 84
            bodies.append(poly([(bx0 / W * 100, by0 / H * 100), (bx1 / W * 100, by0 / H * 100),
                                (bx1 / W * 100, by1 / H * 100), (bx0 / W * 100, by1 / H * 100)]))
            tris.append(poly([((x + 46) / W * 100, (y + 26) / H * 100), ((x + 80) / W * 100, (y + 42) / H * 100),
                              ((x + 46) / W * 100, (y + 58) / H * 100)]))
    for name, layers, path in (("Fondo (logos)", solid(colour, alpha), " ".join(bodies)),
                               ("Fondo (logos, play)", solid(tri), " ".join(tris))):
        s.obj(name, layers, lambda fr, u: (960 + drift[0] * u, 540 + drift[1] * u, W, H, tilt, 1), path=path)


# --- E2 (91.3-95.8 s): coral end screen with the avatar, two videos and the socials across the top ---------------
def end_coral_full():
    D = dur_for(2.2, 1.8)
    t = _p("end-coral", "Pantalla final coral: avatar, dos videos y redes", "Coral end screen: avatar, two videos and "
           "socials", 12953, D, "pantallas-finales", ["agradecimiento", "coral"], thumb=3.0)
    s = S(t, D)
    bg(s, "#F94B4D")
    logo_pattern(s)
    z = lambda fr: 0.3 + 0.7 * k(fr, 3, 12)  # noqa: E731
    shape_photo(s, "fx-man-01", lambda fr, u: (960, 256 + 180 * (1 - z(fr)), 184 * z(fr), 184 * z(fr)),
                label="Tu foto de perfil", op=lambda fr, u: toggle(fr, 3))
    s.obj("Avatar (aro)", ring(WHITE, 8), lambda fr, u: (960, 256 + 180 * (1 - z(fr)), 208 * z(fr), 208 * z(fr),
                                                         0, toggle(fr, 3)), kind="ellipse", base=(208, 208))
    ink = (444, 400, 1484, 464)
    s.say("THANKS FOR WATCHING!", ink, M, 900, WHITE,
          geom=lambda fr, u: (*s.about(ink, 960, 300, z(fr)), z(fr), 0, toggle(fr, 3)))
    c = s.say("MORE VIDEOS:", (798, 512, 1124, 540), M, 800, WHITE, "Texto")
    s.typed(c, 15, stagger=0.04, duration=0.03)
    for i, (rect, sample) in enumerate((((192, 582, 924, 994), "h-beach-01"), ((994, 582, 1728, 994), "fx-walk-03"))):
        x0, y0, x1, y1 = rect
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        g = lambda fr, i=i: k(fr, 21 + 3 * i, 12)  # noqa: E731
        s.rect(f"Video {i + 1} (marco)", solid(WHITE), lambda fr, u, g=g, cx=cx, cy=cy, x0=x0, y0=y0: (
            cx - (cx - x0) * g(fr), cy - (cy - y0) * g(fr), cx + (cx - x0) * g(fr), cy + (cy - y0) * g(fr)))
        photo(s, sample, lambda fr, u, g=g, cx=cx, cy=cy, x0=x0, y0=y0: (
            cx - (cx - x0 - 6) * g(fr), cy - (cy - y0 - 6) * g(fr), cx + (cx - x0 - 6) * g(fr), cy + (cy - y0 - 6) * g(fr)),
            name=f"Video {i + 1}")
    social_icons(s, (224, 864, 1456), 82, 33, size=56, label_right=True)
    return t


def corners(s, name, rect, at, colour=SUBRED, arm=40, w=6):
    """Red corner brackets at the top-right and bottom-left of a slot."""
    x0, y0, x1, y1 = rect
    for i, pts in enumerate((((x1 - arm, y0 - 10), (x1 + 10, y0 - 10), (x1 + 10, y0 + arm)),
                             ((x0 - 10, y1 - arm), (x0 - 10, y1 + 10), (x0 + arm, y1 + 10)))):
        s.outline(f"{name} {i + 1}", list(pts), w, colour, at=at, n=6, closed=False)


# --- E3 (95.8-100.9 s), 2×2 grid of end screens ------------------------------------------------------------------
def end_white_curve():
    """q1: a white panel with a coral curved edge slides in from the right with the next and recommended videos;
    on the left the avatar, the channel name, SUBSCRIBE and the socials appear."""
    D = dur_for(2.6, 1.6)
    t = _p("end-white-curve", "Pantalla final: panel blanco curvo y dos videos", "End screen: curved white panel and "
           "two videos", 12954, D, "pantallas-finales", ["agradecimiento", "blanco"], thumb=3.2)
    s = S(t, D)
    off = lambda fr: 1500 * (1 - k(fr, 18, 15))  # noqa: E731
    s.obj("Panel (borde)", solid(CORAL), lambda fr, u: (2140 + off(fr) - 40, 540, 2600, 2600, 0, 1), kind="ellipse")
    s.obj("Panel", solid(WHITE), lambda fr, u: (2140 + off(fr), 540, 2600, 2600, 0, 1), kind="ellipse")
    for i, (label, rect, sample, at) in enumerate((("NEXT VIDEO", (1092, 132, 1772, 492), "fx-couple-02", 27),
                                                   ("RECOMMENDED", (1092, 592, 1772, 960), "friends-01", 33))):
        s.say(label, (1440 - 9.5 * len(label), 96 + 460 * i, 1440 + 9.5 * len(label), 122 + 460 * i), M, 800,
              "#111111", f"Etiqueta {i + 1}", op=lambda fr, u, at=at: k(fr, at, 6))
        photo(s, sample, lambda fr, u, rect=rect: (rect[0] + off(fr) * 0.6, rect[1], rect[2] + off(fr) * 0.6, rect[3]),
              name=f"Video {i + 1}")
        corners(s, f"Esquina {i + 1}", rect, at + 6)
    avatar(s, "fx-woman-06", 380, 452, 224, 30)
    s.say("YOUR CHANNEL", (192, 588, 580, 632), M, 900, WHITE, "Título", op=lambda fr, u: k(fr, 36, 6))
    pill_text(s, "Suscribirse", "SUBSCRIBE", (220, 656, 544, 708), 45, fill_colour="#F5323F", ink_colour=WHITE)
    social_icons(s, (152, 388, 632), 856, 54)
    return t


def end_white_band():
    """q2: the thanks types over the footage, the avatar pops, a white band rises from the bottom with a dip in the
    middle; the previous and next videos open in it with the reminder between them; the socials pop."""
    D = dur_for(2.8, 1.6)
    t = _p("end-white-band", "Pantalla final: banda blanca con dos videos", "End screen: white band with two videos",
           12955, D, "pantallas-finales", ["agradecimiento", "blanco"], thumb=3.2)
    s = S(t, D)
    rise_ = lambda fr: 760 * (1 - k(fr, 12, 12))  # noqa: E731
    s.rect("Banda", solid(WHITE), lambda fr, u: (-10, 352 + rise_(fr), 1930, 1100 + rise_(fr)),
           path=poly([(0, 0), (50, 21.4), (100, 0), (100, 100), (0, 100)]))
    c = s.say("THANK YOU FOR WATCHING!", (480, 104, 1440, 160), M, 900, WHITE)
    s.typed(c, 3, stagger=0.03, duration=0.03)
    social_icons(s, (720, 952, 1192), 280, 60, size=36)
    avatar(s, "fx-woman-07", 960, 540, 216, 6, ring_colour=WHITE, ring_w=10)
    for i, (label, rect, sample) in enumerate((("PREVIOUS VIDEO", (80, 620, 708, 972), "h-city-02"),
                                               ("NEXT VIDEO", (1204, 620, 1828, 972), "fx-man-02"))):
        cx = (rect[0] + rect[2]) / 2
        s.say(label, (cx - 8 * len(label), 588, cx + 8 * len(label), 606), M, 800, "#111111", f"Etiqueta {i + 1}",
              op=lambda fr, u: k(fr, 30, 6))
        video_slot(s, f"Video {i + 1}", rect, sample, 24 + 3 * i, border="#111111", width=5)
    for i, line in enumerate(("DON'T FORGET", "TO LIKE & COMMENT")):
        s.say(line, (960 - 12 * len(line), 700 + 44 * i, 960 + 12 * len(line), 724 + 44 * i), M, 800, "#111111",
              f"Texto {i + 1}", op=lambda fr, u: k(fr, 39, 6))
    return t


def end_subscribe_arrow():
    """q3: on darkened footage the thanks and the reminder appear, the recommended video rises; on the right the
    avatar pops, an arrow points to a big SUBSCRIBE with the socials and the handle."""
    D = dur_for(2.6, 1.6)
    t = _p("end-subscribe-arrow", "Pantalla final: video recomendado y gran SUBSCRIBE", "End screen: recommended video "
           "and a big SUBSCRIBE", 12956, D, "pantallas-finales", ["agradecimiento", "suscribirse"], thumb=3.2)
    s = S(t, D)
    s.rect("Velo", solid(BLACK, 0.4), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: k(fr, 0, 6))
    c = s.say("THANKS FOR WATCHING!", (192, 232, 960, 288), M, 900, WHITE, "Título")
    s.typed(c, 6, stagger=0.03, duration=0.03)
    s.say("DON'T FORGET TO LIKE & COMMENT", (320, 320, 812, 336), M, 800, WHITE, "Texto", op=lambda fr, u: k(fr, 18, 6))
    photo(s, "h-city-03", lambda fr, u: (198, 542 + 440 * (1 - k(fr, 9, 12)), 954, 966))
    s.outline("Video (marco)", rect_pts(192, 536, 960, 972, "tl"), 6, WHITE, at=12, n=9)
    pill_text(s, "Recomendado", "RECOMMENDED VIDEO", (408, 974, 740, 1006), 24, ink_colour="#F5323F")
    avatar(s, "fx-man-03", 1400, 520, 224, 30, ring_colour=WHITE, ring_w=6)
    s.outline("Flecha", [(1600, 588), (1610, 650), (1560, 700)], 6, WHITE, at=36, n=6, closed=False)
    s.outline("Flecha (punta)", [(1540, 668), (1556, 702), (1594, 698)], 6, WHITE, at=42, n=3, closed=False)
    c = s.say("SUBSCRIBE", (1160, 744, 1640, 808), M, 900, WHITE, "Título 2")
    s.typed(c, 39, stagger=0.04, duration=0.04, preset="pop")
    s.rect("Subrayado", solid(WHITE), lambda fr, u: (1400 - 240 * k(fr, 45, 9), 826, 1400 + 240 * k(fr, 45, 9), 830))
    social_icons(s, (1320, 1388, 1456), 860, 51, size=32, labels=False)
    s.say("@username", (1256, 916, 1640, 956), M, 800, WHITE, "Usuario", op=lambda fr, u: k(fr, 57, 6))
    return t


def end_white_arrow():
    """q4: a white triangle with a red arrow at its tip slides in from the left; the thanks types, the avatar and
    the reminder pop in the triangle, the next video slides in with SUBSCRIBE under it and the socials pop."""
    D = dur_for(2.6, 1.6)
    t = _p("end-white-arrow", "Pantalla final: triángulo blanco con flecha roja", "End screen: white triangle with a "
           "red arrow", 12957, D, "pantallas-finales", ["agradecimiento", "flecha"], thumb=3.2)
    s = S(t, D)
    off = lambda fr: -800 * (1 - k(fr, 6, 12))  # noqa: E731
    s.rect("Triángulo", solid(WHITE), lambda fr, u: (0 + off(fr), 100, 720 + off(fr), 980),
           path=poly([(0, 0), (100, 49), (0, 100)]))
    s.obj("Flecha", solid("#F5323F"), lambda fr, u: (650 + off(fr), 532, 152, 140, 0, 1), path=TRIANGLE)
    c = s.say("THANK YOU FOR WATCHING!", (404, 136, 1512, 200), M, 900, WHITE)
    s.typed(c, 12, stagger=0.03, duration=0.03)
    avatar(s, "fx-woman-08", 236, 444, 172, 24, ring_colour="#F5323F", ring_w=6)
    for i, line in enumerate(("DON'T FORGET", "TO LIKE & COMMENT")):
        s.say(line, (240 - 12 * len(line), 562 + 44 * i, 240 + 12 * len(line), 586 + 44 * i), M, 800, "#F5323F",
              f"Texto {i + 1}", op=lambda fr, u: k(fr, 30, 6))
    photo(s, "h-beach-02", lambda fr, u: (896 + 1100 * (1 - k(fr, 18, 12)), 312, 1712 + 1100 * (1 - k(fr, 18, 12)), 764),
          name="Video")
    s.say("NEXT VIDEO", (1340, 796, 1540, 820), M, 900, WHITE, "Etiqueta", op=lambda fr, u: k(fr, 33, 6))
    pill_text(s, "Suscribirse", "SUBSCRIBE", (1188, 864, 1476, 912), 39, fill_colour="#F5323F", ink_colour=WHITE)
    social_icons(s, (208, 608, 1032), 1000, 48, size=40, label_right=True)
    return t


def ring_pattern(s, colour="#E83A3C", step=160, r=44, drift=(-20.0, 0.0)):
    """Rows of thin rings over the whole frame (the second coral background of the pack)."""
    W, H = 2400.0, 1400.0
    rings = []
    for j in range(10):
        for i in range(16):
            cx, cy = i * step + (step / 2 if j % 2 else 0), j * step * 0.9
            rings.append(poly([((cx + r * math.cos(a * math.pi / 10)) / W * 100,
                                (cy + r * math.sin(a * math.pi / 10)) / H * 100) for a in range(20)]))
    s.obj("Fondo (aros)", ring(colour, 10), lambda fr, u: (960 + drift[0] * u, 540 + drift[1] * u, W, H, 0, 1),
          path=" ".join(rings))


# --- E4 (100.9-106.9 s): coral end screen with next and previous videos, socials in a column and the avatar ------
def end_coral_column():
    D = dur_for(2.2, 1.8)
    t = _p("end-coral-column", "Pantalla final coral: dos videos, redes y avatar", "Coral end screen: two videos, "
           "socials and avatar", 12958, D, "pantallas-finales", ["agradecimiento", "coral"], thumb=3.0)
    s = S(t, D)
    bg(s, "#F94B4D")
    ring_pattern(s)
    for i, (label, y, rect, sample) in enumerate((("NEXT VIDEO", 82, (214, 118, 850, 476), "fx-car-01"),
                                                  ("PREVIOUS VIDEO", 572, (214, 606, 850, 962), "fx-couple-03"))):
        s.say(label, (532 - 12.5 * len(label), y - 15, 532 + 12.5 * len(label), y + 15), M, 900, WHITE,
              f"Etiqueta {i + 1}", op=lambda fr, u: k(fr, 18, 6))
        s.rect(f"Video {i + 1} (marco)", solid(WHITE), lambda fr, u, rect=rect: rect, op=lambda fr, u: k(fr, 3, 9))
        photo(s, sample, lambda fr, u, rect=rect: (rect[0] + 6, rect[1] + 6, rect[2] - 6, rect[3] - 6),
              op=lambda fr: 0.3 + 0.7 * k(fr, 3, 12), name=f"Video {i + 1}")
    c = s.say("THANK YOU", (1140, 186, 1590, 240), M, 900, WHITE, "Título")
    s.typed(c, 6, stagger=0.04, duration=0.03)
    c = s.say("FOR WATCHING!", (1056, 262, 1696, 316), M, 900, WHITE, "Título 2")
    s.typed(c, 12, stagger=0.04, duration=0.03)
    s.obj("Avatar (paso)", solid(WHITE), lambda fr, u: (1592 + 500 * (1 - k(fr, 6, 9)), 540, 228, 228, 0, toggle(fr, 6)),
          kind="ellipse")
    shape_photo(s, "fx-man-04", lambda fr, u: (1592 + 500 * (1 - k(fr, 6, 9)), 540, 216, 216),
                op=lambda fr, u: toggle(fr, 6), label="Tu foto de perfil")
    pill_text(s, "Suscribirse", "SUBSCRIBE", (1444, 800, 1768, 854), 36, ink_colour="#F94B4D")
    for i, line in enumerate(("DON'T FORGET", "TO LIKE & COMMENT")):
        c = s.say(line, (1608 - 11 * len(line), 700 + 42 * i, 1608 + 11 * len(line), 724 + 42 * i), M, 800, WHITE,
                  f"Texto {i + 1}")
        s.typed(c, 45 + 6 * i, stagger=0.03, duration=0.03)
    social_icons(s, (988, 988, 988), 0, 54, size=50, kinds=("tw", "fb", "ig"), ys=(468, 582, 700), label_right=True)
    return t


def typed_count(s, text, at, cps, u):
    """How many characters of `text` (a prefix, spaces included) the engine's typewriter, as S.typed sets it, shows
    at clip time u. The unit «character» counts letters only (spaces take no turn); in: letter i from lead + i·stagger;
    out (backwards, EXIT× faster): while the time left is at least lead/EXIT + i·stagger/EXIT. Same arithmetic as
    the engine, in microseconds."""
    letters = [i for i, ch in enumerate(text) if not ch.isspace()]
    n = len(letters)
    lead, st = round(at / FPS, 3), 1.0 / cps
    t_us = round(u * 1e6)
    e = t_us - round(lead * 1e6)
    shown_in = 0 if e < 0 else min(n, int(e // (round(st, 4) * 1e6)) + 1)
    rem = round(s.dur * 1e6) - round(round(lead / EXIT, 3) * 1e6) - t_us
    shown_out = 0 if rem < 0 else min(n, int(rem // (st / EXIT * 1e6)) + 1)
    k_ = min(shown_in, shown_out)
    return 0 if k_ == 0 else letters[k_ - 1] + 1


def typed_box(s, name, text, ink, box, at, cps=36.0, border=True, colour=BLACK, ink_colour=WHITE, weight=900,
              align="left", cursor=None, preset="typewriter"):
    """A box title: the line types letter by letter and its box hugs the letters already shown (their ink measured
    with the font, the count taken from the engine's own timing). align="center" keeps the typed part centred (the
    line slides by half of what is still hidden) and the box grows from its middle; cursor = the colour of a bar at
    the box's right end while it types."""
    f = f6._font(M, weight)
    n = len(text)
    x0, y0, x1, y1 = box
    ix0, iy0, ix1, iy1 = ink
    # the size the slide gives the line: as wide as the ink, but never taller than its capitals (templates_tit_e)
    bbt, cap = f.getbbox(text), f.getbbox("H")
    w_eff = min(ix1 - ix0, (iy1 - iy0) * (bbt[2] - bbt[0]) / max(1, cap[3] - cap[1]))
    size = f6.fit(text, w_eff, M, weight)[0]
    bb0 = f.getbbox(text)[0]
    pad_l, pad_r = ix0 - x0, x1 - ix1

    def ink_w(m):
        """Ink width of the first m characters at the line's size, from the line's ink start (the engine sets these
        lines without pair kerning: measured on the renders, PIL's plain advances match it)."""
        p_ = text[:m].rstrip()
        if not p_:
            return 0.0
        return (f.getlength(p_[:-1]) + f.getbbox(p_[-1])[2] - bb0) * size / 400

    def rect(fr, u):
        m = typed_count(s, text, at, cps, u)
        if align == "center":
            cx, half = (ix0 + ix1) / 2, ink_w(m) / 2 + pad_l
            return cx - half, y0, cx + half, y1
        return x0, y0, ix0 + ink_w(m) + pad_r, y1
    layers = [fill(colour), ring(WHITE, 4)[1]] if border else solid(colour)
    s.rect(name, layers, rect, op=lambda fr, u: 1.0 if typed_count(s, text, at, cps, u) > 0 or fr >= at else 0.0)
    if cursor:
        s.rect(f"{name} (cursor)", solid(cursor), lambda fr, u: (rect(fr, u)[2] - 16, y0, rect(fr, u)[2], y1),
               op=lambda fr, u: 1.0 if 0 < typed_count(s, text, at, cps, u) < n else 0.0)
    if align == "center":
        # the typed part stays centred: the line is laid out from the left and slides by half of what is still hidden
        W = ix1 - ix0
        c = s.say(text, ink, M, weight, ink_colour, f"{name} (texto)", align="left",
                  geom=lambda fr, u: ((W - ink_w(typed_count(s, text, at, cps, u))) / 2, 0, 1, 0, 1))
    else:
        c = s.say(text, ink, M, weight, ink_colour, f"{name} (texto)", align=align)
    lead, st = round(at / FPS, 3), round(1 / cps, 4)
    extra = {"from": 30} if preset == "pop" else {}
    dur_ = 0.1 if preset == "pop" else 0.02
    c["textStyle"]["animation"] = {
        "in": tanim(preset, duration=dur_, unit="character", stagger=st, ease="easeOut", delay=lead, order="forward",
                    **extra),
        "out": tanim(preset, duration=dur_ / EXIT, unit="character", stagger=1 / cps / EXIT, ease="easeIn",
                     delay=round(lead / EXIT, 3), order="backward", **extra)}
    return c


def typed_box_ahead(s, name, text, ink, box, at, cps=36.0, border=True, colour=BLACK, ink_colour=WHITE, weight=900,
                    align="left"):
    """The first pass's box title, kept for the pieces whose box runs ahead of the letters (best-choice, any-fonts,
    great-design): the box leads the text by about 0.7 of its height."""
    f = f6._font(M, weight)
    total = f.getlength(text)
    n = len(text)
    x0, y0, x1, y1 = box
    ix0, iy0, ix1, iy1 = ink
    grow = lambda fr: min(n, max(0.0, (fr - at) / FPS * cps))  # noqa: E731

    def right(fr):
        m = grow(fr)
        if m >= n:
            return x1
        part = f.getlength(text[:int(m)]) / total * (ix1 - ix0)
        return min(x1, ix0 + part + (iy1 - iy0) * 0.7 + (x1 - ix1))
    layers = [fill(colour), ring(WHITE, 4)[1]] if border else solid(colour)
    s.rect(name, layers, lambda fr, u: (x0, y0, right(fr) if fr >= at else x0, y1), op=lambda fr, u: toggle(fr, at))
    c = s.say(text, ink, M, weight, ink_colour, f"{name} (texto)", align=align)
    s.typed(c, at, stagger=round(1 / cps, 4), duration=0.02)
    return c


# --- B1 (106.9-113.0 s), 2×2 grid of box titles (each line types and its box grows with it) ----------------------
def box_auto_resized():
    D = dur_for(2.0, 1.8)
    t = _p("box-auto-resized", "Título en cajas que crecen al escribir", "Box title growing as it types", 12959, D,
           "titulos-estilo", ["caja", "tecleado"])
    s = S(t, D)
    typed_box(s, "Caja", "AUTO-RESIZED BOX TITLES", (296, 504, 1624, 552), (272, 480, 1648, 572), 3)
    typed_box(s, "Caja 2", "FOR YOUR VIDEO", (524, 616, 1360, 664), (500, 592, 1384, 684), 35)
    return t


def box_best_choice():
    D = dur_for(1.6, 2.0)
    t = _p("box-best-choice", "Título en tres cajas negras", "Title in three black boxes", 12960, D, "titulos-estilo",
           ["caja", "tecleado"])
    s = S(t, D)
    typed_box_ahead(s, "Caja", "BEST CHOICE", (208, 700, 856, 756), (188, 680, 876, 776), 6, border=False)
    typed_box_ahead(s, "Caja 2", "FOR YOUR", (208, 804, 700, 860), (188, 784, 720, 876), 21, border=False)
    typed_box_ahead(s, "Caja 3", "IDEAS", (208, 904, 480, 956), (188, 884, 500, 972), 33, border=False)
    return t


def box_write_text():
    D = dur_for(0.9, 2.4)
    t = _p("box-write-text", "Título en una caja con borde", "Title in one outlined box", 12961, D, "titulos-estilo",
           ["caja", "tecleado"])
    s = S(t, D)
    typed_box(s, "Caja", "WRITE YOUR TEXT", (504, 508, 1376, 560), (480, 488, 1400, 584), 3)
    return t


def box_any_fonts():
    D = dur_for(1.8, 1.8)
    t = _p("box-any-fonts", "Título en dos cajas centradas", "Title in two centred boxes", 12962, D, "titulos-estilo",
           ["caja", "tecleado"])
    s = S(t, D)
    typed_box_ahead(s, "Caja", "BOX TITLES", (708, 484, 1200, 532), (688, 464, 1220, 552), 3, border=False)
    typed_box_ahead(s, "Caja 2", "WORKS WITH ANY FONTS.", (380, 592, 1520, 644), (360, 572, 1540, 664), 18, border=False)
    return t


# --- B2 (113.0-119.0 s), 2×2 grid of box titles -------------------------------------------------------------------
def box_we_created():
    D = dur_for(1.6, 2.0)
    t = _p("box-we-created", "Título en tres cajas negras que se escriben", "Title in three black boxes typing", 12963,
           D, "titulos-estilo", ["caja", "tecleado"])
    s = S(t, D)
    for i, (text, ink, box, at) in enumerate((("WE HAVE CREATED", (288, 400, 1088, 456), (264, 384, 1112, 472), 0),
                                              ("A GREAT SOLUTION FOR YOU", (288, 512, 1528, 564), (264, 492, 1552, 584), 5),
                                              ("WANT TO TRY IT?", (288, 620, 1028, 668), (264, 604, 1052, 688), 10))):
        # lines 1-2 black with a red bar at the end while they type, line 3 white with a black one (113.0 s)
        typed_box(s, ["Caja", "Caja 2", "Caja 3"][i], text, ink, box, at, cps=20, border=False,
                  colour=WHITE if i == 2 else BLACK, ink_colour=BLACK if i == 2 else WHITE,
                  cursor=BLACK if i == 2 else SUBRED, preset="pop")
    return t


def box_great_design():
    D = dur_for(1.8, 1.8)
    t = _p("box-great-design", "Título en dos cajas blancas", "Title in two white boxes", 12964, D, "titulos-estilo",
           ["caja", "tecleado"])
    s = S(t, D)
    typed_box_ahead(s, "Caja", "GREAT DESIGN", (296, 512, 884, 556), (280, 496, 900, 572), 5, border=False, colour=WHITE,
              ink_colour=BLACK)
    typed_box_ahead(s, "Caja 2", "FOR YOUR YOUTUBE CHANNEL.", (296, 604, 1552, 648), (280, 588, 1572, 664), 20, border=False,
              colour=WHITE, ink_colour=BLACK)
    return t


def box_motion_design():
    """q3: a white box types «Motion design» and turns to a slant; a small credit types under it."""
    D = dur_for(2.0, 1.8)
    t = _p("box-motion-design", "Título en caja blanca inclinada", "Title in a slanted white box", 12965, D,
           "titulos-estilo", ["caja", "inclinado"])
    s = S(t, D)
    tilt = lambda fr: -8 * k(fr, 12, 36)  # noqa: E731
    f = f6._font(M, 800)
    text, n = "Motion design", 13
    total = f.getlength(text)
    ink = (500, 508, 1324, 580)

    def box(fr, u):
        m = min(n, max(0.0, (fr - 3) / FPS * 14))
        w = 140 + (f.getlength(text[:int(m)]) / total) * 824 if m < n else 964
        cx, cy = rot_pt(452 + w / 2, 544, tilt(fr), 912, 544)
        return cx, cy, w, 144, tilt(fr), toggle(fr, 3)
    s.obj("Caja", solid(WHITE), box)
    c = s.say(text, ink, M, 800, BLACK, geom=lambda fr, u: (*s.about(ink, 912, 544, 1, tilt(fr)), 1, tilt(fr), 1))
    s.typed(c, 3, stagger=0.07, duration=0.03)
    cr = (1084, 610, 1320, 646)
    c = s.say("By Your Name", cr, M, 800, WHITE, "Texto", geom=lambda fr, u: (*s.about(cr, 912, 544, 1, tilt(fr)), 1,
                                                                            tilt(fr), 1))
    s.typed(c, 33, stagger=0.05, duration=0.03)
    return t


def box_dont_forget():
    D = dur_for(1.4, 2.0)
    t = _p("box-dont-forget", "Título centrado en tres cajas blancas", "Title centred in three white boxes", 12966, D,
           "titulos-estilo", ["caja", "suscribirse"])
    s = S(t, D)
    for i, (text, ink, box, at) in enumerate((("DON'T FORGET TO", (468, 432, 1472, 492), (448, 412, 1492, 512), 3),
                                              ("SUBSCRIBE", (660, 540, 1284, 596), (640, 520, 1304, 616), 8),
                                              ("AND LIKE", (724, 644, 1220, 700), (704, 624, 1240, 716), 13))):
        typed_box(s, ["Caja", "Caja 2", "Caja 3"][i], text, ink, box, at, cps=18, border=False, colour=WHITE,
                  ink_colour=BLACK, align="center")
    return t


def mid_box(s, name, text, ink, box, at, n=12, colour=WHITE, ink_colour=BLACK, edge=SUBRED, weight=900):
    """A box that opens from its middle with red edges on both sides, showing its text as it opens."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    r = lambda fr: (cx - (cx - x0) * k(fr, at, n), y0, cx + (cx - x0) * k(fr, at, n), y1)  # noqa: E731
    s.rect(name, solid(colour), lambda fr, u: r(fr), op=lambda fr, u: toggle(fr, at))
    for j, side in enumerate((0, 2)):
        s.rect(f"{name} (borde {j + 1})", solid(edge), lambda fr, u, side=side: (
            r(fr)[side] - 6, y0 - 4, r(fr)[side] + 6, y1 + 4), op=lambda fr, u: toggle(fr, at) * (1 - k(fr, at + n, 4)))
    return s.say(text, ink, M, weight, ink_colour, f"{name} (texto)", reveal=r)


# --- B3 (119.0-123.9 s), 2×2 grid of box titles -------------------------------------------------------------------
def box_enjoy():
    D = dur_for(1.6, 2.0)
    t = _p("box-enjoy", "Título en cajas con borde blanco", "Title in white outlined boxes", 12967, D, "titulos-estilo",
           ["caja", "contorno"])
    s = S(t, D)
    hollow = [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
              ring(WHITE, 5)[1]]
    for name, text, ink, box, at in (("Caja", "ENJOY", (832, 420, 1084, 472), (812, 400, 1104, 492), 5),
                                     ("Caja 2", "AND USE THE YOUTUBE PACK", (340, 532, 1584, 584), (316, 512, 1604, 604), 5)):
        f = f6._font(M, 900)
        total, n = f.getlength(text), len(text)

        def right(fr, text=text, ink=ink, box=box, at=at, f=f, total=total, n=n):
            m = min(n, max(0.0, (fr - at) / FPS * 20))
            return box[2] if m >= n else ink[0] + f.getlength(text[:int(m)]) / total * (ink[2] - ink[0]) + 30
        s.rect(name, hollow, lambda fr, u, box=box, right=right: (box[0], box[1], right(fr), box[3]),
               op=lambda fr, u, at=at: toggle(fr, at))
        c = s.say(text, ink, M, 900, WHITE, f"{name} (texto)")
        s.typed(c, at, stagger=0.05, duration=0.02)
    return t


def box_automatically():
    D = dur_for(1.4, 2.0)
    t = _p("box-automatically", "Título en caja blanca y caja negra", "Title in a white box and a black box", 12968, D,
           "titulos-estilo", ["caja", "tecleado"])
    s = S(t, D)
    typed_box(s, "Caja", "AUTOMATICALLY", (488, 464, 1420, 532), (468, 440, 1440, 552), 3, cps=14, border=False,
              colour=WHITE, ink_colour=BLACK, align="center")
    typed_box(s, "Caja 2", "DESCRIBE YOUR VIDEO", (596, 580, 1316, 624), (580, 564, 1332, 640), 3, cps=20, border=False,
              colour=WHITE, ink_colour=BLACK, align="center")
    return t


def box_thank_support():
    """q3: a thin line draws, flashes red and opens into a white box with the words; the subtitle types under it."""
    D = dur_for(1.8, 1.8)
    t = _p("box-thank-support", "Título: línea que se abre en caja blanca", "Title: a line opening into a white box",
           12969, D, "titulos-estilo", ["caja"])
    s = S(t, D)
    s.rect("Línea", solid("#CFCFCF"), lambda fr, u: (256, 546, 256 + 1328 * k(fr, 0, 5), 550),
           op=lambda fr, u: 1 - toggle(fr, 6))
    s.rect("Línea roja", solid(SUBRED), lambda fr, u: (312, 540, 1528, 556), op=lambda fr, u: toggle(fr, 3) * (1 - toggle(fr, 9)))
    r = lambda fr: (312, 548 - 44 * k(fr, 6, 6), 1528, 548 + 44 * k(fr, 6, 6))  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: r(fr), op=lambda fr, u: toggle(fr, 6))
    s.say("THANK YOU FOR SUPPORT", (336, 520, 1504, 572), M, 900, BLACK, reveal=r)
    c = s.say("NEW VIDEO WILL BE RELEASED SOON", (496, 620, 1352, 652), M, 800, WHITE, "Texto")
    s.typed(c, 39, stagger=0.025, duration=0.02)
    return t


def box_like_that():
    D = dur_for(1.4, 2.0)
    t = _p("box-like-that", "Título en cajas que se abren del centro", "Title in boxes opening from the middle", 12970,
           D, "titulos-estilo", ["caja", "suscribirse"])
    s = S(t, D)
    mid_box(s, "Caja", "LIKE THAT VIDEO", (548, 492, 1364, 556), (528, 472, 1384, 576), 3)
    mid_box(s, "Caja 2", "AND SUBSCRIBE TO OUR CHANNEL", (480, 604, 1432, 640), (464, 588, 1448, 656), 6, weight=800)
    return t


# --- N (123.9-129.0 s), 2×2 grid of name lower thirds ------------------------------------------------------------
def name_white_box():
    D = dur_for(1.4, 2.0)
    t = _p("name-white-box", "Tercio: nombre en caja blanca que se escribe", "Lower third: name typing in a white box",
           12971, D, "lowerthirds", ["nombre", "caja"])
    s = S(t, D)
    typed_box(s, "Caja", "EDEN FORD", (304, 832, 656, 880), (192, 816, 760, 896), 3, cps=14, border=False,
              colour=WHITE, ink_colour=BLACK)
    c = s.say("MOTION DESIGNER", (192, 912, 568, 944), M, 800, WHITE, "Texto", align="left")
    s.typed(c, 24, stagger=0.03, duration=0.02)
    return t


def name_square_line():
    """q2: a small white square appears, a line runs out of it, the name rises above the line and the role
    under it."""
    D = dur_for(2.4, 1.6)
    t = _p("name-square-line", "Tercio: cuadrito, línea y nombre", "Lower third: small square, line and name", 12972,
           D, "lowerthirds", ["nombre", "línea"])
    s = S(t, D)
    s.obj("Cuadro", solid(WHITE), lambda fr, u: (156, 892, 24 * pop(fr, 9), 24 * pop(fr, 9), 45 * (1 - k(fr, 9, 9)),
                                                 toggle(fr, 9)))
    s.rect("Línea", solid(WHITE), lambda fr, u: (168, 889, 168 + 604 * k(fr, 48, 12), 895))
    rise(s, "ROBBIE BACKER", (192, 828, 772, 876), 57, weight=800)
    s.say("MOTION DESIGNER", (192, 908, 640, 944), M, 800, WHITE, "Texto", align="left",
          reveal=lambda fr: (0, 895, 1920, 1080), shift=lambda fr: (0, -60 * (1 - k(fr, 60, 9))))
    return t


def name_red_box():
    """q3: a red line draws under the name, the name rises, the line fills up into a red box and the role types."""
    D = dur_for(1.6, 2.0)
    t = _p("name-red-box", "Tercio: nombre en caja roja", "Lower third: name in a red box", 12973, D, "lowerthirds",
           ["nombre", "rojo"])
    s = S(t, D)
    s.rect("Caja", solid("#F5323F"), lambda fr, u: (108, 930 - 70 * k(fr, 30, 8), 108 + 604 * k(fr, 6, 9), 936))
    rise(s, "GWEN CROSSMAN", (124, 876, 696, 920), 12, weight=800)
    c = s.say("MOTION DESIGNER", (120, 952, 600, 988), M, 800, "#111111", "Texto", align="left")
    s.typed(c, 36, stagger=0.03, duration=0.02)
    return t


def name_bar():
    """q4: a white bar stands up at the left and the name and role slide out from behind it."""
    D = dur_for(1.2, 2.0)
    t = _p("name-bar", "Tercio: barra blanca y nombre que sale de ella", "Lower third: white bar and a name sliding "
           "out", 12974, D, "lowerthirds", ["nombre", "barra"])
    s = S(t, D)
    s.rect("Barra", solid(WHITE), lambda fr, u: (64, 1024 - 200 * k(fr, 3, 8), 80, 1024))
    s.say("COLIN CRAMER", (108, 856, 704, 912), M, 800, WHITE, align="left", reveal=lambda fr: (80, 0, 1920, 1080),
          shift=lambda fr: (-640 * (1 - k(fr, 9, 15)), 0))
    s.say("MOTION DESIGNER", (108, 932, 588, 968), M, 800, WHITE, "Texto", align="left",
          reveal=lambda fr: (80, 0, 1920, 1080), shift=lambda fr: (-520 * (1 - k(fr, 13, 15)), 0))
    return t


NETS = (("fb", "Facebook", "#3B5998", "@username"), ("ig", "Instagram", "#E1306C", "@username"),
        ("tw", "Twitter", "#1DA1F2", "@username"), ("yt", "YouTube", "#F0262E", "@channelname"))


def glyph(s, name, kind, geom, size, colour, back=WHITE):
    """A network's glyph drawn in `colour`: geom(fr, u) = (cx, cy, scale, rot, opacity)."""
    def g(w, h, dx=0.0):
        return lambda fr, u: (lambda v: (v[0] + dx * v[2], v[1], w * v[2], h * v[2], v[3], v[4]))(geom(fr, u))
    if kind == "fb":
        s.obj(name, solid(colour), g(size * 0.42, size * 0.8),
              path=poly([(36, 100), (36, 52), (14, 52), (14, 34), (36, 34), (36, 22), (44, 6), (62, 0), (86, 0),
                         (86, 18), (68, 18), (62, 24), (62, 34), (86, 34), (82, 52), (62, 52), (62, 100)]))
    elif kind == "ig":
        s.obj(name, ring(colour, max(3, size * 0.09)), g(size * 0.78, size * 0.78), radius=size * 0.22,
              base=(size * 0.78, size * 0.78))
        s.obj(f"{name} (lente)", ring(colour, max(3, size * 0.09)), g(size * 0.36, size * 0.36), kind="ellipse",
              base=(size * 0.36, size * 0.36))
    elif kind == "tw":
        s.obj(name, solid(colour), g(size * 0.8, size * 0.66), path=BIRD)
    else:
        ytb(s, name, lambda fr, u: (lambda v: (v[0], v[1], v[2] * size / 100, v[3], v[4]))(geom(fr, u)), 100, 70,
            body=solid(colour), tri=back)


def _net_p(design, n, kind, net, es, en, order, D):
    return _p(f"social-{design}-{kind}", f"Barra de redes: {net} ({es})", f"Social bar: {net} ({en})", order, D, "redes",
              ["redes", net.lower()])


def shade(colour, f):
    """colour mixed with white (f > 0) or black (f < 0)."""
    r, g, b = (int(colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    t_ = 255 if f > 0 else 0
    f = abs(f)
    return "#%02X%02X%02X" % tuple(round(c + (t_ - c) * f) for c in (r, g, b))


def glyph3d(s, name, kind, geom, size, colour, back, rx=None, ry=None, persp=1600, show=None, z=None):
    """A glyph that turns with its card: every piece gets the card's 3D pose (they share its centre)."""
    g = lambda fr, u: (lambda v: (*v[:4], v[4] * (show(fr) if show else 1.0)))(geom(fr, u))  # noqa: E731
    for c in new_clips(s, lambda: glyph(s, name, kind, g, size, colour, back=back)):
        # a hair in front of its card (+z comes toward the eye), so the depth test keeps it on top
        s.d3(c, rx=(lambda fr, u: rx(fr)) if rx else None, ry=(lambda fr, u: ry(fr)) if ry else None,
             z=lambda fr, u: (z(fr) if z else 0.0) + GLYPH_LIFT, persp=persp)


def social_tilted(kind, net, colour, handle, order):
    """S1 (129.0 s): the coloured tile flies up from below flipping over its horizontal axis (its plain back, then
    its face with the glyph), lands, then slides left turning a little while a white bar with the handle and a
    FOLLOW US tab grow out of it (measured at 15 fps on 129.0-131.4 s)."""
    D = dur_for(2.3, 1.6)
    t = _net_p("baldosa", 1, kind, net, "baldosa que vuela", "flying tile", order, D)
    s = S(t, D)
    x = f6.curve([(4, 508), (8, 512), (12, 518), (46, 518), (50, 450), (54, 370), (58, 320), (62, 280), (66, 264)])
    y = f6.curve([(4, 1018), (6, 980), (8, 940), (10, 912), (12, 888), (14, 884)])
    rx = lambda fr: -200 * (1 - lin(fr, 3, 13)) ** 1.7  # noqa: E731
    rz = lambda fr: -20 * (1 - k(fr, 3, 13))  # noqa: E731
    ry = lambda fr: 28 * math.sin(math.pi * lin(fr, 46, 22))  # noqa: E731
    right = lambda fr: 520 + 288 * k(fr, 46, 18)  # noqa: E731
    bar = lambda fr: (max(320.0, x(fr)), 824, max(x(fr), right(fr)), 920)  # noqa: E731
    s.rect("Barra", solid(WHITE), lambda fr, u: bar(fr), op=lambda fr, u: toggle(fr, 47))
    tab = lambda fr: (max(320.0, x(fr)), 916, max(x(fr), 320 + 288 * k(fr, 56, 9)), 944)  # noqa: E731
    s.rect("Seguir", solid(colour), lambda fr, u: tab(fr), op=lambda fr, u: toggle(fr, 56))
    s.say("FOLLOW US", (368, 922, 520, 938), M, 800, WHITE, "Texto", reveal=tab)
    s.say(handle, (356, 848, 356 + 296 * len(handle) / 9, 896), M, 800, colour, align="left",
          reveal=bar, shift=lambda fr: (-150 * (1 - k(fr, 48, 16)), 0))
    geom = lambda fr, u: (x(fr), y(fr), 1, rz(fr), toggle(fr, 4))  # noqa: E731
    card3d(s, "Ícono", geom, 128, 136, rx=rx, ry=ry, persp=1600, front=solid(colour), back=solid(shade(colour, -0.1)),
           edge=solid(shade(colour, 0.35)), radius=0.06, tri=False)
    facing = lambda fr: 1.0 if math.cos(math.radians(rx(fr))) * math.cos(math.radians(ry(fr))) >= 0 else 0.0  # noqa: E731
    glyph3d(s, "Ícono (glifo)", kind, geom, 96, WHITE, colour, rx=rx, ry=ry, show=facing)
    return t


def social_bars(kind, net, colour, handle, order):
    """S2 (132.4 s): a coloured bar flies in turning, splits into two and they slide apart opening a white box with
    the glyph, the handle and a FOLLOW US pill."""
    D = dur_for(2.3, 1.6)
    t = _net_p("barras", 2, kind, net, "dos barras que se abren", "two bars opening", order, D)
    s = S(t, D)
    q = lambda fr: k(fr, 57, 9)  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: (520 - 280 * q(fr), 772, 520 + 280 * q(fr), 920))
    glyph(s, "Ícono", kind, lambda fr, u: (332, 846, 1, 0, toggle(fr, 63)), 104, colour)
    s.say(handle, (448, 816, 448 + 232 * len(handle) / 9, 848), M, 800, colour, align="left",
          op=lambda fr, u: k(fr, 63, 4))
    s.rect("Seguir", solid(colour), lambda fr, u: (452, 862, 452 + 236 * k(fr, 66, 6), 882), radius=10, base=(236, 20))
    s.say("FOLLOW US", (520, 866, 620, 878), M, 800, WHITE, "Texto", op=lambda fr, u: k(fr, 69, 4))
    fly = lambda fr: 1 - k(fr, 36, 12)  # noqa: E731
    for j, side in enumerate((-1, 1)):
        s.obj(f"Barra {j + 1}", solid(colour), lambda fr, u, side=side: (
            520 - 200 * fly(fr) + side * (308 * q(fr) + 6 * toggle(fr, 54)), 840 + 200 * fly(fr), 40, 176,
            -40 * fly(fr), toggle(fr, 36)))
    return t


def social_circle(kind, net, colour, handle, order):
    """S3 (137.3 s): a white circle with a coloured rim pops with the glyph; a white pill with the handle slides out
    from behind it."""
    D = dur_for(1.5, 1.8)
    t = _net_p("circulo", 3, kind, net, "círculo y píldora", "circle and pill", order, D)
    s = S(t, D)
    s.rect("Píldora", solid(WHITE), lambda fr, u: (420, 824, 420 + 520 * k(fr, 30, 12), 912), radius=44, base=(520, 88))
    s.say(handle, (540, 852, 540 + 280 * len(handle) / 9, 888), M, 800, colour, align="left",
          reveal=lambda fr: (500, 0, 420 + 520 * k(fr, 30, 12), 1080), shift=lambda fr: (-300 * (1 - k(fr, 30, 12)), 0))
    s.obj("Círculo", solid(WHITE), lambda fr, u: (412, 868, 192 * pop(fr, 3, 8), 192 * pop(fr, 3, 8), 0, toggle(fr, 3)),
          kind="ellipse")
    s.obj("Círculo (aro)", ring(colour, 8), lambda fr, u: (412, 868, 184 * pop(fr, 3, 8), 184 * pop(fr, 3, 8), 0,
                                                           toggle(fr, 3)), kind="ellipse", base=(184, 184))
    glyph(s, "Ícono", kind, lambda fr, u: (412, 868, pop(fr, 6, 8), 0, toggle(fr, 6)), 104, colour)
    return t


def xyz_of(spin, turn):
    """(rx, ry, rz) in degrees with Rx·Ry·Rz = Rz(spin)·Ry(turn): a turn round an axis lying in the screen at `spin`
    degrees, in the engine's order (tilt X, then Y, then the in-plane spin)."""
    p_, t_ = math.radians(spin), math.radians(turn)
    cp, sp, ct, st = math.cos(p_), math.sin(p_), math.cos(t_), math.sin(t_)
    r00, r01, r02, r12, r22 = cp * ct, -sp, cp * st, sp * st, ct  # R = Rz(p)·Ry(t)
    b = math.asin(max(-1.0, min(1.0, r02)))
    return math.degrees(math.atan2(-r12, r22)), math.degrees(b), math.degrees(math.atan2(-r01, r00))


def social_tile(kind, net, colour, handle, order):
    """S4 (140.4 s): an outlined square grows spinning; a white tile swings out of its left edge like a door (a real
    turn round its vertical axis) and settles upright with the glyph; a white bar with the handle and a FOLLOW US tab
    grow out of it (measured at 30 fps on 140.4-141.6 s)."""
    D = dur_for(2.4, 1.6)
    t = _net_p("cuadro", 4, kind, net, "cuadro que gira", "flipping tile", order, D)
    s = S(t, D)
    s.rect("Barra", solid(WHITE), lambda fr, u: (392, 788, 392 + 596 * k(fr, 48, 9), 912))
    s.say(handle, (432, 828, 432 + 372 * len(handle) / 9, 880), M, 800, colour, align="left",
          reveal=lambda fr: (392, 0, 392 + 596 * k(fr, 48, 9), 1080))
    s.rect("Seguir", solid(WHITE), lambda fr, u: (988 - 300 * k(fr, 63, 8), 924, 988, 964))
    s.say("FOLLOW US", (720, 934, 956, 954), M, 800, colour, "Texto", op=lambda fr, u: k(fr, 66, 4))
    cx, cy, w, h = 296, 852, 192, 200
    grow = f6.curve([(9, 0.16), (10, 0.33), (11, 0.5), (12, 0.66), (13, 0.75), (14, 0.85), (15, 0.93), (16, 1.0)])
    rot = f6.curve([(9, 45), (14, 0), (17, -35), (19, -38), (22, -25), (26, -12), (30, -3), (33, 0)])
    swing = lambda fr: 90 * (1 - k(fr, 17, 11))  # noqa: E731  (+Y: the right edge swings back)

    def hinge(fr):
        """The tile's centre: its left edge stays on the outline's left edge, turned with it."""
        off = -w / 2 + w / 2 * math.cos(math.radians(swing(fr)))
        a = math.radians(rot(fr))
        return cx + off * math.cos(a), cy + off * math.sin(a)
    s.obj("Cuadro (borde)", ring(WHITE, 4), lambda fr, u: (cx, cy, w * grow(fr), h * grow(fr), rot(fr), toggle(fr, 9)),
          radius=8, base=(w, h))
    # pushed back by half its turned width so the hinge (its left edge, nearer the eye) stays in the screen's plane;
    # the right edge swings away from the eye (as in the reference)
    push = lambda fr: -w / 2 * abs(math.sin(math.radians(swing(fr))))  # noqa: E731
    # the door turns round its own (spun) left edge: the engine tilts X, then Y, then spins, so the turn about a
    # spun axis, spin(rot) · turnY(swing), is handed over as the equivalent X / Y / spin angles
    pose = lambda fr: xyz_of(rot(fr), swing(fr))  # noqa: E731
    geom = lambda fr, u: (*hinge(fr), 1, pose(fr)[2], toggle(fr, 17))  # noqa: E731
    # a long lens: far from the frame's centre a short eye distance pulls the far edge toward the middle
    card3d(s, "Cuadro", geom, w, h, rx=lambda fr: pose(fr)[0], ry=lambda fr: pose(fr)[1], persp=3200,
           front=solid(WHITE), radius=0.04, tri=False, z=push)
    glyph3d(s, "Ícono", kind, geom, 136, colour, WHITE, rx=lambda fr: pose(fr)[0], ry=lambda fr: pose(fr)[1],
            persp=3200, z=push)
    return t


# The brush stroke of S5 (146.0 s, on 100..1090 × 775..975): a tapered left end, a lump under the words and a dry,
# streaky right end.
BRUSH = poly([(0, 38), (5, 25), (15, 14), (28, 8), (40, 2), (60, 0), (80, 6), (90, 10), (95, 12), (100, 16), (94, 20),
              (99, 26), (93, 30), (100, 36), (92, 40), (98, 48), (90, 52), (97, 60), (88, 64), (94, 72), (86, 76),
              (90, 84), (82, 88), (70, 98), (55, 100), (37, 96), (36, 80), (25, 70), (12, 62), (3, 50)])


def social_brush(kind, net, colour, handle, order):
    """S5 (144.4 s): a coloured brush stroke is uncovered from right to left (a moving rectangle mask on the shape),
    the glyph and the handle with it; FOLLOW US is uncovered the same way a moment later."""
    D = dur_for(0.8, 2.4)
    t = _net_p("pincel", 5, kind, net, "pincelada", "brush stroke", order, D)
    s = S(t, D)
    x0 = lambda fr: 1110 - 1030 * k(fr, 4, 10)  # noqa: E731
    wipe = lambda fr: (x0(fr), 0, 1920, 1080)  # noqa: E731
    box = (100, 775, 990, 200)
    c = s.rect("Pincel", solid(colour), lambda fr, u: (box[0], box[1], box[0] + box[2], box[1] + box[3]), path=BRUSH,
               op=lambda fr, u: toggle(fr, 4))
    screen_mask(s, c, box, lambda fr: (x0(fr), 700, 1200, 1060))
    # the glyph is uncovered as the wipe passes it (it is narrow: the wipe crosses it in a frame)
    glyph(s, "Ícono", kind, lambda fr, u: (370, 855, 1, 0, 1.0 if x0(fr) <= 372 and fr >= 4 else 0.0), 68, WHITE,
          back=colour)
    s.say(handle, (432, 828, 432 + 308 * len(handle) / 9, 880), M, 800, WHITE, align="left", reveal=wipe)
    s.say("FOLLOW US", (528, 924, 740, 948), M, 800, WHITE, "Texto",
          reveal=lambda fr: (760 - 240 * k(fr, 17, 6), 0, 1920, 1080))
    return t


def _social_all():
    out = []
    order = 12975
    for design in (social_tilted, social_bars, social_circle, social_tile, social_brush):
        for kind, net, colour, handle in NETS:
            out.append(lambda design=design, kind=kind, net=net, colour=colour, handle=handle, order=order:
                       design(kind, net, colour, handle, order))
            out[-1].__name__ = f"{design.__name__}_{kind}"
            order += 1
    return out


SOCIAL = _social_all()


def quote_mark(s, name, cx, cy, size, at, colour=WHITE, closing=False, rot=0.0):
    """Typographic quotation marks («“» or «”») as two filled commas."""
    for j, dx in enumerate((-0.22, 0.22)):
        pts = [(50, 0), (100, 30), (100, 100), (0, 100), (0, 60), (30, 60), (30, 40), (50, 0)] if not closing else \
            [(0, 0), (100, 0), (100, 40), (50, 100), (0, 70), (70, 40), (0, 40)]
        s.obj(f"{name}" + (f" {j + 1}" if j else ""), solid(colour), lambda fr, u, dx=dx: (
            cx + dx * size * pop(fr, at), cy, size * 0.36 * pop(fr, at), size * 0.5 * pop(fr, at), rot, toggle(fr, at)),
            path=poly(pts))


def quote_lines(s, lines, x0, x1, top, step, caps, colour=WHITE, align="left", at=0, how="fade", names=None,
                reveal=None, shift=None):
    out = []
    for i, line in enumerate(lines):
        y = top + step * i
        c = s.say(line, (x0, y, x1, y + caps), M, 800, colour, (names or [])[i] if names else
                  ("Título" if i == 0 else f"Título {i + 1}"), align=align, reveal=reveal, shift=shift)
        if how == "type":
            s.typed(c, at + 4 * i, stagger=0.02, duration=0.02)
        elif how == "fade":
            s.fade(c, lambda fr, i=i: k(fr, at + 2 * i, 6))
        out.append(c)
    return out


# --- Q1 (148.2-152.4 s), 2×2 grid of quotes (the quotes and authors are replaced by neutral words) ----------------
def quote_line_left():
    D = dur_for(1.6, 2.0)
    t = _p("quote-line", "Cita: línea vertical y comillas en cuadros", "Quote: vertical line and quote marks in boxes",
           12995, D, "frases", ["cita"])
    s = S(t, D)
    s.obj("Comillas (fondo)", solid(WHITE), lambda fr, u: (464, 304, 88 * pop(fr, 3), 88 * pop(fr, 3), 0, toggle(fr, 3)))
    quote_mark(s, "Comillas", 464, 304, 56, 6, BLACK)
    s.rect("Línea", solid(WHITE), lambda fr, u: (541, 376, 547, 376 + 320 * k(fr, 6, 9)))
    quote_lines(s, ("EVERY GREAT STORY STARTS", "WITH ONE SIMPLE IDEA, AND", "THE COURAGE TO SHARE IT", "WITH THE PEOPLE WHO",
                    "NEED TO HEAR IT TODAY."), 564, 1432, 404, 56, 32, how=None,
                reveal=lambda fr: (547, 0, 1920, 1080), shift=lambda fr: (-900 * (1 - k(fr, 15, 15)), 0))
    s.say("Your Name", (608, 720, 900, 752), M, 700, WHITE, "Texto", align="left", op=lambda fr, u: k(fr, 36, 6))
    s.obj("Cierre (fondo)", solid(BLACK), lambda fr, u: (1404, 752, 88 * pop(fr, 36), 88 * pop(fr, 36), 0, toggle(fr, 36)))
    quote_mark(s, "Cierre", 1404, 752, 56, 39, WHITE, closing=True)
    return t


def quote_brackets():
    D = dur_for(1.4, 2.0)
    t = _p("quote-brackets", "Cita entre dos esquinas", "Quote between two corners", 12996, D, "frases", ["cita"])
    s = S(t, D)
    s.outline("Esquina", [(680, 364), (1304, 364), (1304, 600)], 6, WHITE, at=3, n=9, closed=False)
    s.outline("Esquina 2", [(1240, 640), (612, 640), (612, 396)], 6, WHITE, at=3, n=9, closed=False)
    quote_mark(s, "Comillas", 616, 360, 48, 6)
    quote_mark(s, "Cierre", 1292, 646, 48, 12, closing=True)
    quote_lines(s, ("A SIMPLE IDEA", "CAN CHANGE THE STORY.", "SHARE IT WITH", "THE WORLD."), 688, 1240, 440, 44, 30,
                at=12)
    s.say("YOUR NAME", (832, 688, 1108, 720), M, 700, WHITE, "Texto", op=lambda fr, u: k(fr, 27, 6))
    return t


def quote_frame():
    D = dur_for(1.6, 2.0)
    t = _p("quote-frame", "Cita en marco con etiqueta negra", "Quote in a frame with a black tag", 12997, D, "frases",
           ["cita", "marco"])
    s = S(t, D)
    s.outline("Marco", [(916, 324), (1408, 324), (1408, 708), (428, 708), (428, 324), (916, 324)], 6, WHITE, at=3, n=12,
              closed=False)
    s.obj("Comillas (fondo)", solid(BLACK), lambda fr, u: (916, 300, 104 * pop(fr, 3), 104 * pop(fr, 3), 0, toggle(fr, 3)))
    s.obj("Comillas (borde)", ring(WHITE, 5), lambda fr, u: (916, 300, 88 * pop(fr, 3), 88 * pop(fr, 3), 0, toggle(fr, 3)),
          base=(88, 88))
    quote_mark(s, "Comillas", 916, 300, 44, 6)
    quote_lines(s, ("THE WORK YOU LOVE TODAY", "BUILDS THE PERSON YOU WILL", "BE TOMORROW. KEEP GOING", "EVERY DAY."),
                468, 1368, 420, 56, 32, align="center", at=12)
    s.rect("Etiqueta", solid(BLACK), lambda fr, u: (920 - 180 * k(fr, 30, 8), 752, 920 + 180 * k(fr, 30, 8), 828))
    s.say("Your Name", (790, 774, 1050, 806), M, 800, WHITE, "Texto", op=lambda fr, u: k(fr, 33, 4))
    return t


def quote_two_lines():
    D = dur_for(1.6, 2.0)
    t = _p("quote-two-lines", "Cita entre dos líneas", "Quote between two lines", 12998, D, "frases", ["cita"])
    s = S(t, D)
    s.rect("Línea", solid(WHITE), lambda fr, u: (1552 - 1184 * k(fr, 3, 9), 389, 1552, 395))
    s.rect("Línea 2", solid(WHITE), lambda fr, u: (368, 681, 368 + 1184 * k(fr, 3, 9), 687))
    quote_mark(s, "Comillas", 332, 448, 52, 9)
    quote_mark(s, "Cierre", 1584, 628, 52, 9, closing=True)
    quote_lines(s, ("GOOD DESIGN AND GOOD STORIES WORK TOGETHER", "TO GIVE PEOPLE THE BEST MOMENTS", "WHEN THEY ARE SHARED."),
                420, 1500, 466, 56, 28, align="center", at=9, how="type")
    s.say("YOUR NAME", (870, 712, 1050, 744), M, 800, WHITE, "Texto", op=lambda fr, u: k(fr, 33, 6))
    return t


# --- Q2 (152.4-156.0 s): a line drops into a white quote box, the words appear one by one ------------------------
def quote_white_box():
    D = dur_for(1.6, 2.0)
    t = _p("quote-white-box", "Cita en caja blanca con comillas negras", "Quote in a white box with black marks", 12999,
           D, "frases", ["cita", "caja"])
    s = S(t, D)
    s.rect("Caja", solid(WHITE), lambda fr, u: (428 + 600 * (1 - k(fr, 0, 6)) * 0, 420, 1492, 432 + 228 * k(fr, 6, 6)),
           op=lambda fr, u: toggle(fr, 0))
    for name, (cx, cy), closing in (("Comillas", (406, 450), False), ("Cierre", (1514, 630), True)):
        s.obj(f"{name} (fondo)", solid(BLACK), lambda fr, u, cx=cx, cy=cy: (cx, cy, 80 * pop(fr, 9), 80 * pop(fr, 9), 0,
                                                                            toggle(fr, 9)))
        quote_mark(s, name, cx, cy, 48, 10, WHITE, closing=closing)
    for i, line in enumerate(("A GOOD IDEA IS ONLY THE BEGINNING,", "THE REST IS MADE BY THE WORK.",
                              "KEEP CREATING, KEEP SHARING.")):
        c = s.say(line, (492, 456 + 44 * i, 1440, 490 + 44 * i), M, 900, BLACK, "Título" if i == 0 else f"Título {i + 1}",
                  align="left")
        s.typed(c, 9 + 9 * i, stagger=0.09, duration=0.12, preset="fade", unit="word")
    s.say("Your Name", (492, 600, 692, 626), M, 700, BLACK, "Texto", align="left", op=lambda fr, u: k(fr, 39, 6))
    return t


# --- Q4 (161.0-164.7 s): centred words rise one by one between two quote marks; a white name tag opens -----------
def quote_centred():
    D = dur_for(1.6, 2.0)
    t = _p("quote-centred", "Cita centrada con etiqueta blanca", "Centred quote with a white tag", 13004, D, "frases",
           ["cita"])
    s = S(t, D)
    quote_mark(s, "Comillas", 512, 464, 44, 3, BLACK)
    quote_mark(s, "Cierre", 1476, 624, 44, 30, BLACK, closing=True)
    for i, line in enumerate(("GOOD IDEAS NEED ROOM:", "GIVE THEM SPACE TO BREATHE.")):
        c = s.say(line, (492, 488 + 46 * i, 1428, 518 + 46 * i), M, 800, WHITE, "Título" if i == 0 else "Título 2")
        s.typed(c, 3 + 9 * i, stagger=0.1, duration=0.15, preset="rise", unit="word")
    s.rect("Etiqueta", solid(WHITE), lambda fr, u: (780, 610, 780 + 360 * k(fr, 18, 8), 652))
    s.say("YOUR NAME", (860, 620, 1060, 642), M, 800, BLACK, "Texto", reveal=lambda fr: (780, 0, 780 + 360 * k(fr, 18, 8), 1080))
    return t


# --- Q3 (156.0-161.0 s), 2×2 grid of quotes ----------------------------------------------------------------------
def quote_black_frame():
    D = dur_for(1.6, 2.0)
    t = _p("quote-black-frame", "Cita en marco negro con etiqueta", "Quote in a black frame with a tag", 13000, D,
           "frases", ["cita", "marco"])
    s = S(t, D)
    turn = lambda fr: 10 * (1 - k(fr, 3, 12))  # noqa: E731
    s.obj("Marco", ring(BLACK, 8), lambda fr, u: (978, 558, 628 * (0.8 + 0.2 * k(fr, 3, 12)), 444 * (0.8 + 0.2 * k(fr, 3, 12)),
                                                  turn(fr), toggle(fr, 3)), base=(628, 444))
    quote_mark(s, "Comillas", 728, 328, 52, 9, BLACK)
    quote_mark(s, "Cierre", 1212, 780, 52, 30, BLACK, closing=True)
    for i, line in enumerate(("A STORY IS NOT", "ONLY ABOUT HOW", "IT LOOKS AND FEELS.", "A STORY IS HOW", "IT MOVES YOU.")):
        c = s.say(line, (724, 420 + 60 * i, 1200, 456 + 60 * i), M, 800, WHITE, "Título" if i == 0 else f"Título {i + 1}",
                  align="left")
        s.typed(c, 12 + 3 * i, stagger=0.08, duration=0.12, preset="fade", unit="word")
    s.rect("Etiqueta", solid(BLACK), lambda fr, u: (692, 784, 692 + 316 * k(fr, 36, 8), 840))
    s.say("YOUR NAME", (740, 798, 960, 826), M, 800, WHITE, "Texto", reveal=lambda fr: (692, 0, 692 + 316 * k(fr, 36, 8), 1080))
    return t


def quote_bubble():
    D = dur_for(1.6, 2.0)
    t = _p("quote-bubble", "Cita en globo de diálogo", "Quote in a speech bubble", 13001, D, "frases", ["cita", "globo"])
    s = S(t, D)
    s.outline("Globo", [(960, 292), (1380, 292), (1420, 332), (1420, 732), (1380, 772), (840, 772), (800, 820),
                        (800, 772), (540, 772), (500, 732), (500, 332), (540, 292), (960, 292)], 6, WHITE, at=0, n=18,
              closed=False)
    quote_mark(s, "Comillas", 560, 352, 44, 12)
    quote_mark(s, "Cierre", 1352, 732, 44, 24, closing=True)
    lines = ("A GOOD PRODUCT DOES ITS JOB,", "BUT A GREAT ONE ALSO BRINGS", "A SMILE TO THE PEOPLE WHO USE IT,",
             "SOME JOY, SOME SURPRISE,", "AND A LITTLE MAGIC", "TO EVERY DAY.")
    for i, line in enumerate(lines):
        c = s.say(line, (560, 410 + 44 * i, 1360, 438 + 44 * i), M, 800, WHITE, "Título" if i == 0 else f"Título {i + 1}")
        s.fade(c, lambda fr, i=i: k(fr, 18 + 2 * i, 6))
    s.say("Your Name", (1120, 802, 1320, 830), M, 700, WHITE, "Texto", op=lambda fr, u: k(fr, 33, 6))
    return t


def quote_corners():
    D = dur_for(1.6, 2.0)
    t = _p("quote-corners", "Cita entre dos esquinas blancas", "Quote between two white corners", 13002, D, "frases",
           ["cita"])
    s = S(t, D)
    s.outline("Esquina", [(416, 568), (416, 424), (864, 424)], 6, WHITE, at=3, n=9, closed=False)
    s.outline("Esquina 2", [(1428, 448), (1428, 652), (980, 652)], 6, WHITE, at=6, n=9, closed=False)
    quote_mark(s, "Comillas", 444, 384, 44, 6)
    quote_mark(s, "Cierre", 1400, 692, 44, 12, closing=True)
    for i, line in enumerate(("EVERY MISTAKE IS A STEP", "THAT HELPS YOU GROW. YOU HAVE", "TO TRY AGAIN IN ORDER TO GET GOOD.")):
        c = s.say(line, (520, 482 + 48 * i, 1336, 510 + 48 * i), M, 800, WHITE, "Título" if i == 0 else f"Título {i + 1}")
        s.typed(c, 12 + 6 * i, stagger=0.06, duration=0.12, preset="fade", unit="word")
    s.say("YOUR NAME", (480, 640, 680, 664), M, 800, BLACK, "Texto", align="left", op=lambda fr, u: k(fr, 33, 6))
    return t


def quote_split_bar():
    """q4: a white bar stands up in the middle, splits in two and the halves slide apart revealing the words."""
    D = dur_for(2.2, 1.8)
    t = _p("quote-split-bar", "Cita que se abre entre dos barras", "Quote opening between two bars", 13003, D, "frases",
           ["cita"])
    s = S(t, D)
    q = lambda fr: k(fr, 39, 18)  # noqa: E731
    for j, side in enumerate((-1, 1)):
        s.rect(f"Barra {j + 1}", solid(WHITE), lambda fr, u, side=side: (
            956 + side * 332 * q(fr) - (8 * (1 - q(fr)) + 3), 540 - 168 * k(fr, 24, 9),
            956 + side * 332 * q(fr) + (8 * (1 - q(fr)) + 3), 540 + 168 * k(fr, 24, 9)), op=lambda fr, u: toggle(fr, 24))
    rv = lambda fr: (960 - 330 * q(fr), 0, 960 + 330 * q(fr), 1080)  # noqa: E731
    for i, line in enumerate(("YOU DON'T WAIT FOR", "GREAT IDEAS TO COME.", "YOU WORK YOUR WAY", "TO GREAT IDEAS.")):
        s.say(line, (680, 432 + 46 * i, 1240, 464 + 46 * i), M, 800, WHITE, "Título" if i == 0 else f"Título {i + 1}",
              reveal=rv)
    s.say("Your Name", (860, 640, 1060, 672), M, 800, WHITE, "Texto", reveal=rv)
    quote_mark(s, "Comillas", 576, 404, 44, 54)
    quote_mark(s, "Cierre", 1336, 668, 44, 57, closing=True)
    return t


def target_dot(s, name, cx, cy, at, d=64, colour=WHITE):
    s.obj(name, ring(colour, 5), lambda fr, u: (cx, cy, d * pop(fr, at), d * pop(fr, at), 0, toggle(fr, at)), kind="ellipse",
          base=(d, d))
    s.obj(f"{name} (centro)", solid(colour), lambda fr, u: (cx, cy, d * 0.45 * pop(fr, at + 2), d * 0.45 * pop(fr, at + 2),
                                                            0, toggle(fr, at + 2)), kind="ellipse")


# --- C1 (164.7-169.0 s), 2×2 grid of call-out lines ---------------------------------------------------------------
def callout_outline():
    D = dur_for(2.4, 1.6)
    t = _p("callout-outline", "Línea de llamada con punto y texto", "Call-out line with a dot and text", 13005, D,
           "elementos", ["llamada"])
    s = S(t, D)
    target_dot(s, "Punto", 1100, 460, 9)
    s.outline("Línea", [(1084, 444), (900, 252)], 4, WHITE, at=30, n=12, closed=False)
    for i, (line, y) in enumerate((("YOUTUBE CALL OUT", 160), ("OUTLINE", 208))):
        c = s.say(line, (440, y, 900, y + 38), M, 800, WHITE, "Título" if i == 0 else "Título 2", align="right")
        s.typed(c, 51 + 6 * i, stagger=0.03, duration=0.02)
    return t


def callout_red_box():
    D = dur_for(2.0, 1.8)
    t = _p("callout-red-box", "Línea de llamada con caja roja", "Call-out line with a red box", 13006, D, "elementos",
           ["llamada", "rojo"])
    s = S(t, D)
    target_dot(s, "Punto", 900, 440, 21, d=24)
    s.outline("Línea", [(900, 440), (688, 320)], 4, WHITE, at=24, n=12, closed=False)
    s.rect("Caja", solid("#F5323F"), lambda fr, u: (688 - 436 * k(fr, 39, 8), 212, 688, 284))
    s.say("MAIN LINE HERE", (300, 232, 640, 264), M, 800, WHITE, reveal=lambda fr: (688 - 436 * k(fr, 39, 8), 0, 700, 1080))
    s.rect("Caja 2", solid(WHITE), lambda fr, u: (688 - 232 * k(fr, 45, 8), 292, 688, 320))
    s.say("SECOND LINE", (490, 298, 654, 314), M, 800, BLACK, "Texto", reveal=lambda fr: (688 - 232 * k(fr, 45, 8), 0, 700, 1080))
    return t


def callout_title_bar():
    D = dur_for(2.2, 1.6)
    t = _p("callout-title-bar", "Llamada: barra roja y título", "Call-out: red bar and title", 13007, D, "elementos",
           ["llamada", "rojo"])
    s = S(t, D)
    s.rect("Barra", solid("#F5323F"), lambda fr, u: (1180, 580 - 68 * k(fr, 30, 8), 1196, 580 + 68 * k(fr, 30, 8)))
    s.say("CALL OUT TITLE", (1220, 520, 1620, 564), M, 900, WHITE, align="left", reveal=lambda fr: (1196, 0, 1920, 1080),
          shift=lambda fr: (-420 * (1 - k(fr, 45, 12)), 0))
    for i, line in enumerate(("WRITE A SHORT TEXT ABOUT IT,", "ONE OR TWO LINES THAT EXPLAIN",
                              "WHAT THE VIEWER IS LOOKING AT.")):
        s.say(line, (1220, 580 + 22 * i, 1560, 594 + 22 * i), M, 700, "#E8E8E8", f"Texto {i + 1}", align="left",
              op=lambda fr, u, i=i: k(fr, 54 + 3 * i, 6))
    return t


def callout_brand():
    D = dur_for(2.2, 1.6)
    t = _p("callout-brand", "Llamada: marca y precio", "Call-out: brand and price", 13008, D, "elementos",
           ["llamada", "precio"])
    s = S(t, D)
    target_dot(s, "Punto", 680, 520, 9, d=40)
    s.obj("Destello", ring(WHITE, 4), lambda fr, u: (680, 520, 220 * k(fr, 24, 9), 220 * k(fr, 24, 9), 0,
                                                     toggle(fr, 24) * (1 - k(fr, 30, 6))), kind="ellipse", base=(220, 220))
    s.outline("Línea", [(690, 506), (900, 372), (904, 372)], 4, WHITE, at=24, n=12, closed=False)
    s.outline("Caja", rect_pts(904, 304, 1348, 380, "tl"), 5, WHITE, at=39, n=9)
    s.say("BRAND NAME", (980, 324, 1272, 360), M, 800, WHITE, op=lambda fr, u: k(fr, 45, 6))
    s.rect("Precio", solid("#F5323F"), lambda fr, u: (904, 384, 904 + 196 * k(fr, 48, 8), 444))
    s.say("$390", (944, 398, 1060, 430), M, 800, WHITE, "Texto", reveal=lambda fr: (904, 0, 904 + 196 * k(fr, 48, 8), 1080))
    return t


# --- C2 (169.0-173.0 s): a red dot, a red line and a red box with the call-out -----------------------------------
def callout_red_line():
    D = dur_for(3.2, 1.4)
    t = _p("callout-red-line", "Llamada: línea roja y caja roja", "Call-out: red line and red box", 13009, D,
           "elementos", ["llamada", "rojo"])
    s = S(t, D)
    red = "#F2283C"
    target_dot(s, "Punto", 1072, 596, 18, d=36, colour=red)
    s.outline("Línea", [(1082, 610), (1290, 824)], 5, red, at=42, n=15, closed=False)
    s.rect("Caja", solid(red), lambda fr, u: (1292, 824, 1292 + 432 * k(fr, 57, 9), 914))
    for i, (line, y) in enumerate((("YOUTUBE CALL OUT", 842), ("LINES FOR YOU", 876))):
        c = s.say(line, (1312, y, 1696, y + 24), M, 900, WHITE, "Título" if i == 0 else "Título 2", align="left")
        s.typed(c, 69 + 9 * i, stagger=0.04, duration=0.02)
    return t


# --- C4 (177.0-181.8 s): a white dot and an elbow line lead to a title over a red box of text --------------------
def callout_elbow():
    D = dur_for(2.0, 1.8)
    t = _p("callout-elbow", "Llamada: línea en codo y caja roja de texto", "Call-out: elbow line and red text box",
           13014, D, "elementos", ["llamada", "rojo"])
    s = S(t, D)
    target_dot(s, "Punto", 1016, 890, 9, d=26)
    s.outline("Línea", [(1024, 882), (1190, 770), (1544, 770)], 4, WHITE, at=15, n=15, closed=False)
    s.rect("Caja", solid("#F2283C"), lambda fr, u: (1190, 776, 1544, 776 + 98 * k(fr, 33, 8)))
    c = s.say("TYPE YOUR TEXT", (1194, 742, 1394, 760), M, 900, WHITE, "Título", align="left")
    s.typed(c, 30, stagger=0.03, duration=0.02)
    for i, line in enumerate(("WRITE A SHORT DESCRIPTION OF WHAT", "THE VIEWER SEES IN THIS PART OF THE",
                              "VIDEO, IN TWO OR THREE SHORT LINES.")):
        s.say(line, (1202, 790 + 22 * i, 1530, 802 + 22 * i), M, 800, WHITE, f"Texto {i + 1}", align="left",
              op=lambda fr, u, i=i: k(fr, 42 + 3 * i, 6))
    return t


# --- C3 (173.0-177.0 s), 2×2 grid of call-out lines ---------------------------------------------------------------
def callout_product():
    D = dur_for(1.8, 1.8)
    t = _p("callout-product", "Llamada: línea y recuadro de producto", "Call-out: line and product frame", 13010, D,
           "elementos", ["llamada", "producto"])
    s = S(t, D)
    target_dot(s, "Punto", 1040, 680, 6, d=56)
    s.outline("Línea", [(1064, 666), (1364, 540)], 4, WHITE, at=12, n=12, closed=False)
    s.outline("Recuadro", [(1364, 540), (1364, 164), (1744, 164), (1744, 540), (1364, 540)], 5, WHITE, at=27, n=12,
              closed=False)
    for i, (line, y) in enumerate((("DESCRIBE", 184), ("YOUR", 248), ("PRODUCT", 300))):
        c = s.say(line, (1400, y, 1712, y + 44), M, 900, WHITE, "Título" if i == 0 else f"Título {i + 1}", align="left")
        s.typed(c, 39 + 3 * i, stagger=0.03, duration=0.02)
    s.rect("Subrayado", solid("#F2283C"), lambda fr, u: (1400, 356, 1400 + 308 * k(fr, 45, 8), 364))
    for i, line in enumerate(("WRITE A FEW WORDS", "ABOUT WHAT YOU", "ARE SHOWING, ITS", "PRICE OR WHERE", "TO FIND IT.")):
        s.say(line, (1400, 384 + 25 * i, 1640, 398 + 25 * i), M, 800, WHITE, f"Texto {i + 1}", align="left",
              op=lambda fr, u, i=i: k(fr, 48 + 2 * i, 6))
    return t


def callout_headline():
    D = dur_for(2.2, 1.6)
    t = _p("callout-headline", "Llamada: titular rojo y caja negra", "Call-out: red headline and black box", 13011, D,
           "elementos", ["llamada", "rojo"])
    s = S(t, D)
    s.outline("Línea", [(900, 872), (1080, 700)], 4, BLACK, at=33, n=9, closed=False)
    s.rect("Titular", solid("#F2283C"), lambda fr, u: (1092, 480, 1092 + 448 * k(fr, 42, 8), 576))
    s.say("HEADLINE", (1132, 508, 1500, 548), M, 900, WHITE, reveal=lambda fr: (1092, 0, 1092 + 448 * k(fr, 42, 8), 1080))
    s.rect("Caja", solid(BLACK), lambda fr, u: (1092, 588, 1092 + 672 * k(fr, 48, 8), 680))
    s.say("DESCRIBE HERE", (1132, 614, 1724, 654), M, 900, WHITE, "Texto",
          reveal=lambda fr: (1092, 0, 1092 + 672 * k(fr, 48, 8), 1080))
    return t


def callout_line_up():
    D = dur_for(2.2, 1.6)
    t = _p("callout-line-up", "Llamada: línea que sube a una caja negra", "Call-out: line rising to a black box", 13012,
           D, "elementos", ["llamada"])
    s = S(t, D)
    target_dot(s, "Punto", 1320, 920, 21, d=24)
    s.rect("Línea", solid(BLACK), lambda fr, u: (1318, 920 - 252 * k(fr, 24, 9), 1322, 920))
    s.rect("Caja", solid(BLACK), lambda fr, u: (1326 - 286 * k(fr, 33, 8), 584, 1326 + 286 * k(fr, 33, 8), 668))
    s.say("CALL OUT LINE", (1076, 608, 1576, 644), M, 900, WHITE, reveal=lambda fr: (1326 - 286 * k(fr, 33, 8), 0,
                                                                                  1326 + 286 * k(fr, 33, 8), 1080))
    rise(s, "HEAD LINE", (1240, 536, 1412, 560), 54, "Texto", align="center", weight=800)
    return t


def callout_creative():
    D = dur_for(2.2, 1.6)
    t = _p("callout-creative", "Llamada: línea punteada y dos cajas", "Call-out: dotted line and two boxes", 13013, D,
           "elementos", ["llamada", "rojo"])
    s = S(t, D)
    dash = " ".join(poly([(i * 10, 0), (i * 10 + 5, 0), (i * 10 + 5, 100), (i * 10, 100)]) for i in range(10))
    s.obj("Línea", solid(WHITE), lambda fr, u: (1024 + 96 * (1 - k(fr, 6, 12)) / 2, 710 - 90 * (1 - k(fr, 6, 12)) / 2,
                                                264 * k(fr, 6, 12), 4, -43, toggle(fr, 6)), path=dash)
    s.rect("Caja", solid(WHITE), lambda fr, u: (180, 872, 180 + 724 * k(fr, 18, 9), 948))
    s.say("CALL OUT LINES.", (220, 892, 864, 928), M, 900, BLACK, reveal=lambda fr: (180, 0, 180 + 724 * k(fr, 18, 9), 1080))
    s.rect("Titular", solid("#F2283C"), lambda fr, u: (344, 800, 344 + 456 * k(fr, 51, 8), 868))
    s.say("CREATIVE", (452, 816, 692, 852), M, 900, WHITE, "Texto", reveal=lambda fr: (344, 0, 344 + 456 * k(fr, 51, 8), 1080))
    return t


PERSON = poly([(30, 0), (70, 0), (78, 12), (78, 38), (70, 50), (30, 50), (22, 38), (22, 12)]) + " " + \
    poly([(0, 100), (4, 74), (18, 60), (82, 60), (96, 74), (100, 100)])
HEART = poly([(50, 100), (6, 50), (0, 30), (4, 12), (16, 2), (32, 0), (44, 8), (50, 18), (56, 8), (68, 0), (84, 2),
              (96, 12), (100, 30), (94, 50)])
CHAT = poly([(10, 0), (90, 0), (100, 12), (100, 70), (90, 82), (40, 82), (20, 100), (22, 82), (10, 82), (0, 70), (0, 12)])
CORAL2 = "#FA5A5A"


def counter(clip, first, seconds):
    clip["textStyle"].update(counter=True, counterFrom=first, counterSeconds=round(seconds, 3))


def bubble(s, name, cx, cy, w, h, at, glyph_path, number=None, number_from=None, extra=None):
    """A notification bubble (rounded box with a tail) that pops turning, with its glyph and an optional count."""
    tilt = lambda fr: 25 * (1 - k(fr, at, 9))  # noqa: E731
    s.obj(name, solid(CORAL2), lambda fr, u: (cx, cy, w * pop(fr, at), h * pop(fr, at), tilt(fr), toggle(fr, at)),
          path=poly([(8, 0), (92, 0), (100, 10), (100, 78), (92, 86), (58, 86), (50, 100), (42, 86), (8, 86), (0, 78),
                     (0, 10)]))
    gx = cx - (w * 0.22 if number else 0)
    s.obj(f"{name} (ícono)", solid(WHITE), lambda fr, u: (gx, cy - h * 0.08, h * 0.42 * pop(fr, at + 2),
                                                          h * 0.42 * pop(fr, at + 2), tilt(fr), toggle(fr, at + 2)),
          path=glyph_path)
    if number:
        c = s.say(number, (cx - w * 0.05, cy - h * 0.2, cx + w * 0.4, cy + h * 0.06), M, 800, WHITE, f"{name} (número)",
                  align="left", op=lambda fr, u: toggle(fr, at + 3))
        counter(c, number_from, 2.4)


# --- X (181.8-183.6 s): the pack's counters page -----------------------------------------------------------------
def counter_bubbles():
    D = dur_for(1.0, 2.6)
    t = _p("counter-bubbles", "Contadores: globos de notificación", "Counters: notification bubbles", 13015, D,
           "elementos", ["contador", "me gusta"])
    s = S(t, D)
    rows = ((370, HEART), (560, PERSON), (750, CHAT))
    for j, (y, g) in enumerate(rows):
        bubble(s, f"Globo {j + 1}", 300, y, 184, 136, 3 * j, g)
        bubble(s, f"Globo {j + 4}", 530, y, 184, 136, 3 * j + 2, g, "120", 101)
        bubble(s, f"Globo {j + 7}", 820, y, 280, 120, 3 * j + 4, HEART if j < 2 else CHAT, "120", 101)
    return t


def counter_heart():
    D = dur_for(0.6, 3.0)
    t = _p("counter-heart", "Contador de me gusta con corazón", "Like counter with a heart", 13016, D, "elementos",
           ["contador", "me gusta"])
    s = S(t, D)
    s.obj("Corazón", solid(CORAL2), lambda fr, u: (900, 750, 90 * pop(fr, 0), 80 * pop(fr, 0), 0, 1), path=HEART)
    c = s.say("76", (970, 726, 1060, 776), M, 800, WHITE, "Número", align="left")
    counter(c, 3, 2.6)
    return t


def counter_subscribers():
    D = dur_for(0.8, 2.8)
    t = _p("counter-subscribers", "Contador de suscriptores", "Subscriber counter", 13017, D, "elementos",
           ["contador", "suscribirse"])
    s = S(t, D)
    s.rect("Píldora", solid(CORAL2), lambda fr, u: (1360, 344, 1360 + 324 * k(fr, 0, 9), 394), radius=25, base=(324, 50))
    s.say("SUBSCRIBERS", (1396, 356, 1648, 382), M, 900, WHITE, reveal=lambda fr: (1360, 0, 1360 + 324 * k(fr, 0, 9), 1080))
    s.rect("Número (caja)", solid(WHITE), lambda fr, u: (1483 - 77 * k(fr, 9, 6), 404, 1483 + 77 * k(fr, 9, 6), 436),
           radius=16, base=(154, 32))
    c = s.say("12812", (1424, 410, 1520, 430), M, 800, CORAL2, "Número")
    counter(c, 12700, 2.6)
    s.say("K", (1524, 412, 1540, 428), M, 800, CORAL2, "Texto", op=lambda fr, u: toggle(fr, 9))
    return t


def counter_link():
    D = dur_for(0.8, 2.6)
    t = _p("counter-link", "Enlace en la descripción", "Link in description", 13018, D, "elementos", ["enlace"])
    s = S(t, D)
    s.rect("Píldora", solid(WHITE), lambda fr, u: (1360, 524, 1360 + 324 * k(fr, 0, 9), 576), radius=26, base=(324, 52))
    s.say("LINK IN DESCRIPTION", (1392, 540, 1652, 560), M, 800, CORAL2,
          reveal=lambda fr: (1360, 0, 1360 + 324 * k(fr, 0, 9), 1080))
    s.obj("Flecha (círculo)", solid(WHITE), lambda fr, u: (1484, 624, 36 * pop(fr, 9), 36 * pop(fr, 9), 0, toggle(fr, 9)),
          kind="ellipse")
    s.obj("Flecha", solid(CORAL2), lambda fr, u: (1484, 624 + 4 * math.sin(u * 6), 16, 10, 0, toggle(fr, 12)),
          path=poly([(0, 0), (20, 0), (50, 60), (80, 0), (100, 0), (50, 100)]))
    return t


def counter_person():
    D = dur_for(0.6, 3.0)
    t = _p("counter-person", "Contador de seguidores", "Follower counter", 13019, D, "elementos", ["contador"])
    s = S(t, D)
    s.obj("Persona", solid(CORAL2), lambda fr, u: (1390, 750, 80 * pop(fr, 0), 80 * pop(fr, 0), 0, 1), path=PERSON)
    c = s.say("76", (1468, 726, 1560, 776), M, 800, WHITE, "Número", align="left")
    counter(c, 3, 2.6)
    return t


# --- R (183.6-185.5 s): the record transition: discs grow from the centre and a window opens in them -------------
# Radius (px on the 960 source, from the centre) of a disc of the record transition, frame by frame after it starts;
# every disc follows the same curve, later (measured on 183.0-184.6 s).
IRIS_R = [5, 12, 22, 36, 53, 73, 97, 124, 154, 187, 222, 258, 296, 334, 370, 406, 440, 472, 502, 530, 556, 580, 602,
          622, 640, 656, 670, 682, 692, 700]
# The window that opens in the middle, from the first frame it shows.
IRIS_HOLE = [4, 14, 23, 33, 48, 66, 88, 116, 150, 192, 238, 289, 341, 390, 433, 470, 505, 535, 560, 580]


def record_iris():
    """183.0-184.6 s: coral, black, white and coral discs grow from the centre one after another; then a window with a
    thin white rim opens in the middle of all of them (an inverted ellipse mask on each disc) and shows the video."""
    D = 2.0
    t = _p("record-iris", "Transición: círculos de grabar que se abren", "Transition: record circles opening", 13020, D,
           "transiciones", ["transición", "círculos"], thumb=0.7)
    s = S(t, D)
    s.frame = lambda u: u * FPS  # a transition runs once, no exit

    def radius(table, fr, lag):
        q = fr - lag
        if q < 0:
            return 0.0
        i = int(q)
        if i >= len(table) - 1:
            return float(table[-1])
        return table[i] + (table[i + 1] - table[i]) * (q - i)
    HOLE_AT = 18
    hole_d = lambda fr: 4 * radius(IRIS_HOLE, fr, HOLE_AT)  # noqa: E731  (diameter on the 1920 frame)
    big = 4 * IRIS_R[-1]
    for i, (colour, lag) in enumerate(((CORAL2, 0), (BLACK, 2), (WHITE, 5), (CORAL2, 7))):
        d = lambda fr, lag=lag: 4 * radius(IRIS_R, fr, lag)  # noqa: E731
        c = s.obj(f"Círculo {i + 1}", solid(colour), lambda fr, u, d=d, lag=lag: (
            960, 540, max(1.0, d(fr)), max(1.0, d(fr)), 0, toggle(fr, lag)), kind="ellipse", base=(big, big))
        size = lambda fr, d=d: min(1.0, hole_d(fr) / max(1.0, d(fr)))  # noqa: E731
        s.t.mask(track_of(s, c), c, "ellipse", x=0.5, y=0.5, w=0.0, h=0.0, invert=True,
                 keyframes={"w": per_frame(s, lambda fr, u, size=size: size(fr)),
                            "h": per_frame(s, lambda fr, u, size=size: size(fr))})
    # the rim: about 5.7 % of the window's radius, just outside it (a white disc with the window cut out of it)
    rim = s.obj("Borde", solid(WHITE), lambda fr, u: (960, 540, max(1.0, hole_d(fr) * 1.057),
                                                      max(1.0, hole_d(fr) * 1.057), 0, toggle(fr, HOLE_AT + 1)),
                kind="ellipse", base=(big, big))
    s.t.mask(track_of(s, rim), rim, "ellipse", x=0.5, y=0.5, w=1 / 1.057, h=1 / 1.057, invert=True)
    return t


# --- TY (185.5-189.2 s): THANKS FOR WATCHING! word by word ------------------------------------------------------
def thanks_watching():
    D = dur_for(0.9, 2.4)
    t = _p("thanks-watching", "Título: gracias por ver", "Title: thanks for watching", 13021, D, "titulos-estilo",
           ["agradecimiento"])
    s = S(t, D)
    c = s.say("THANKS FOR WATCHING!", (450, 506, 1470, 574), M, 900, WHITE,
              geom=lambda fr, u: (0, 0, 1 + 0.04 * u, 0, 1))
    s.typed(c, 0, stagger=0.2, duration=0.2, preset="rise", unit="word")
    return t


TEMPLATES = [big_live_story, travel_blog, channel_name_tilted, your_channel_label, click_channel, triangle_box,
             doodle_channel, stacked_channel, white_opener, promo_pack, opener_boxes, opener_typed, opener_divider,
             opener_fade, opener_flip, best_video, watch_next, modern_titles, subscribe_to, hello_welcome,
             best_solution, how_do_i, good_design, clean_modern, subscribe_now, best_show, new_video, clean_titles,
             modern_universal, sub_avatar_pill, sub_red_pill, sub_center_avatar, sub_logo_box, sub_red_to_white,
             like_card, like_column, avatar_cycle, sub_grey_bell, sub_channel_tag, sub_stack, bubble_swap,
             tilted_cycle, three_icons, subscribed_click, profile_card, notify_bell, subscribe_icon, like_hand,
             three_pills, end_circle, end_side_panel, end_diagonal, end_big_arc, end_coral_full, end_white_curve,
             end_white_band, end_subscribe_arrow, end_white_arrow, end_coral_column, box_auto_resized,
             box_best_choice, box_write_text, box_any_fonts, box_we_created, box_great_design, box_motion_design,
             box_dont_forget, box_enjoy, box_automatically, box_thank_support, box_like_that, name_white_box,
             name_square_line, name_red_box, name_bar, *SOCIAL, quote_line_left, quote_brackets, quote_frame,
             quote_two_lines, quote_white_box, quote_centred, quote_black_frame, quote_bubble, quote_corners,
             quote_split_bar, callout_outline, callout_red_box, callout_title_bar, callout_brand, callout_red_line,
             callout_elbow, callout_product, callout_headline, callout_line_up, callout_creative, counter_bubbles,
             counter_heart, counter_subscribers, counter_link, counter_person, record_iris, thanks_watching]
