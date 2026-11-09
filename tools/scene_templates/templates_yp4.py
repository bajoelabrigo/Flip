"""YOUTUBE PACK video 4 as Stock templates (yp4-*). See docs/plan-youtube-pack.md.

«Youtube Channel Stories Pack» (pack youtube 4.mp4, 960×540 at 30 fps): vertical red, white and yellow stories with
photo slots, shown in the reference inside phones and side by side. Each story is laid out on 1080×1920 (measured
where it shows largest, ×5.24 from the 206 px wide stories of the reference) with the moves studied on 10 fps sheets.
Kit de YouTube › Redes; ids `yp4-*`, order 12700-. Study notes in tienda/plantillas/estudio-pack-youtube-4/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of, mask_track
from scene import keys, tanim
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, TRIANGLE, arc, fill, lin, poly, ring, rot_pt, shadow

W, H = 1080, 1920
WHITE, BLACK, RED, YELLOW = "#FFFFFF", "#000000", "#FC1E1F", "#FBF451"
ANTON, ANTONIO, M = "Anton", "Antonio", "Montserrat"
f6._FILES[(ANTON, 400)] = "fonts.basic/fonts/anton/Anton-Regular.ttf"
for w, f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(ANTONIO, w)] = f"fonts.extra/fonts/antonio/Antonio-{f}.ttf"
for w, f in ((500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")):
    f6._FILES[(M, w)] = f"fonts.basic/fonts/montserrat/Montserrat-{f}.ttf"


def _p(id, es, en, order, dur, tags=()):
    return tall(f"yp4-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:redes", "historia", "youtube", "vertical"] + list(tags), thumb_at=round(dur * 0.55, 1))


def dur_for(entrance, hold=2.0):
    return round(entrance + hold + entrance / EXIT, 1)


class T(S):
    """A story slide on 1080×1920."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)

    def letters(self, clip, at, stagger=0.05, duration=0.2, preset="rise", order="forward", unit="character", **kw):
        n = len(clip.get("textContent", "")) if unit == "character" else len(clip.get("textContent", "").split())
        lead = round(at / FPS, 3)
        clip["textStyle"]["animation"] = {
            "in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=lead,
                        order=order, **kw),
            "out": tanim(preset, duration=duration / EXIT, unit=unit, stagger=stagger / EXIT, ease="easeIn",
                         delay=round(lead / EXIT, 3), order="backward" if order == "forward" else order, **kw)}
        return n


def art_except(t, keep=("Fondo",)):
    """In a normal (horizontal) video the story keeps its own shape: every clip is design ("art", scaled and placed
    together as one column) except the tracks named with `keep` (backgrounds that stretch with the frame). For stories
    whose big discs and bands the layout guess would stretch apart from the rest (see layoutfit.py)."""
    for track in t.tracks:
        for clip in track.clips:
            if clip.get("type") in ("audio", "adjustment", "composite") or "layoutRole" in clip:
                continue
            name = clip.get("name") or track.name
            clip["layoutRole"] = "backdrop" if name.startswith(tuple(keep)) else "art"
    return t


def bg(s, colour, name="Fondo"):
    return s.rect(name, solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))


def photo(s, sample, box=None, rect=None, name="Foto", op=None, geom=None, oval=False, label="Tu foto"):
    """A photo slot laid out in box = (x0, y0, x1, y1) (whole frame when None), cut to rect(fr, u) (screen px) or
    to an ellipse filling the box (oval); geom(fr, u) = (dx, dy, scale) moves it."""
    t = s.t
    x0, y0, x1, y1 = box or (0, 0, W, H)
    b = Box(x0, y0, x1 - x0, y1 - y0)
    motion = None
    if geom:
        motion = [(u, (lambda g: {"sx": g[2], "sy": g[2], "dx": g[0], "dy": g[1]})(geom(s.frame(u), u)), "linear")
                  for u in frames_of(s.dur)]
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, b, motion, label=label)
    clip["name"] = name
    if rect:
        mask_track(t, clip, b, lambda u: rect(s.frame(u), u), s.dur)
    if oval:
        track = next(tr for tr in t.tracks if clip in tr.clips)
        t.mask(track, clip, "ellipse")
    if op:
        clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(s.frame(u), u))), 4), "linear")
                                for u in frames_of(s.dur)])
    return clip


# --- 1. CHANNEL: the letters rise on red, the word opens and a black ball with a play sign rolls in ------------------
def channel():
    D = dur_for(1.8)
    t = _p("canal", "Historia: CHANNEL con botón de play", "Story: CHANNEL with a play button", 12700, D, ["canal"])
    s = T(t, D)
    bg(s, RED)
    c = s.say("YOUTUBE", (62, 796, 208, 832), ANTON, 400, WHITE, "Texto", align="left")
    s.letters(c, 9, stagger=0.03, duration=0.25, preset="fade")
    gap = lambda fr: 214 * k(fr, 41, 7)  # noqa: E731
    base = lambda fr: (0, -10, W, 1066)  # noqa: E731
    c = s.say("CHANN", (60, 862, 606, 1064), ANTON, 400, WHITE, align="left", reveal=base)
    s.letters(c, 17, stagger=0.033, duration=0.2, distance=1.2)
    c = s.say("EL", (630, 862, 762, 1064), ANTON, 400, WHITE, "Título 2", align="left", reveal=base,
              shift=lambda fr: (gap(fr), 0))
    s.letters(c, 22, stagger=0.033, duration=0.2, distance=1.2)
    size = lambda fr: 200 * k(fr, 42, 9)  # noqa: E731
    s.obj("Botón", solid(BLACK), lambda fr, u: (728, 966, size(fr), size(fr), 0, 1.0 if fr >= 42 else 0.0),
          kind="ellipse", base=(200, 200))

    def tri(fr, u):
        a = math.radians(180 * k(fr, 45, 12))
        r = 60 * size(fr) / 200
        return 728 + r * math.cos(a), 966 + r * math.sin(a) * 0.6, 46 * size(fr) / 200, 56 * size(fr) / 200, 0, \
            1.0 if fr >= 45 else 0.0
    s.obj("Botón (play)", solid(RED), tri, path=TRIANGLE)
    return t


# --- 2. WELCOME TO MY: a play sign spins into a red button, circles stack up and scroll, the words slide in ------
def welcome():
    D = dur_for(3.6)
    t = _p("bienvenida", "Historia: bienvenida con discos rojo y negro", "Story: welcome with red and black discs", 12701,
           D, ["bienvenida", "círculo"])
    s = T(t, D)
    pink, soft, grey = "#FF9A9A", "#FF5454", "#2E2E2E"
    bg(s, WHITE)
    up = lambda fr: -2100 * k(fr, 57, 24)  # noqa: E731  the red stack scrolls away
    s.rect("Fondo rojo", solid(RED), lambda fr, u: (-10, -10 + up(fr), W + 10, H + 10 + up(fr)),
           op=lambda fr, u: 0.0 if 13 <= fr < 28 else 1.0)
    s.obj("Disco claro", solid(soft), lambda fr, u: (540, 300 + up(fr), 1600 * k(fr, 36, 9), 1600 * k(fr, 36, 9), 0, 1),
          kind="ellipse", base=(1600, 1600))
    s.obj("Disco de arriba", solid(WHITE), lambda fr, u: (540, 330 - 600 * (1 - k(fr, 39, 9)) + up(fr), 1000, 1000, 0,
                                                          1.0 if fr >= 39 else 0.0), kind="ellipse")
    s.obj("Aro fino", ring(RED, 3), lambda fr, u: (540, 340 - 600 * (1 - k(fr, 39, 9)) + up(fr), 620 * k(fr, 42, 9),
                                                   620 * k(fr, 42, 9), 0, 1), kind="ellipse", base=(620, 620))
    f = f6.curve([(12, 2600), (27, 2600), (33, 1250), (40, 992), (46, 712), (51, 460)])
    cy = f6.curve([(40, 960), (51, 960)])
    s.obj("Disco blanco", solid(WHITE), lambda fr, u: (540, cy(fr) + up(fr), f(fr), f(fr), 0, 1.0 if fr >= 12 else 0.0),
          kind="ellipse", base=(2600, 2600))
    # the red cap where the top disc overlaps the middle one: a red copy of the middle disc cut by an ellipse mask the
    # size and place of the top disc (an intersection of the two shapes)
    top = lambda fr: 330 - 600 * (1 - k(fr, 39, 9))  # noqa: E731
    cap = s.obj("Casquete", solid(RED), lambda fr, u: (540, cy(fr) + up(fr), f(fr), f(fr), 0, 1.0 if fr >= 39 else 0.0),
                kind="ellipse", base=(2600, 2600))
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u, fr in s.each():
        d = max(1.0, f(fr))
        mk["x"].append((u, 0.5, "linear"))
        mk["y"].append((u, 0.5 + (top(fr) - cy(fr)) / d, "linear"))
        mk["w"].append((u, 1000 / d, "linear"))
        mk["h"].append((u, 1000 / d, "linear"))
    track = next(tr for tr in t.tracks if cap in tr.clips)
    t.mask(track, cap, "ellipse", x=0.5, y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={key: keys(v) for key, v in mk.items()})
    s.obj("Halo", solid(pink), lambda fr, u: (540, 960, 1080 * (1 - k(fr, 21, 9)) + 40, 1080 * (1 - k(fr, 21, 9)) + 40, 0,
                                              1.0 if 15 <= fr < 30 else 0.0), kind="ellipse", base=(1120, 1120))
    rb = f6.curve([(12, 1300), (21, 848), (33, 448), (40, 200), (46, 200)])
    ry = f6.curve([(40, 960), (48, 350)])
    s.obj("Botón", solid(RED), lambda fr, u: (540, ry(fr) + up(fr), rb(fr), rb(fr), 0, 1.0 if fr >= 12 else 0.0),
          kind="ellipse", base=(1300, 1300))
    s.obj("Punto rosa", solid(pink), lambda fr, u: (540, 960 + up(fr), 200 * k(fr, 36, 4) * (1 - k(fr, 42, 6)),
                                                    200 * k(fr, 36, 4) * (1 - k(fr, 42, 6)), 0, 1), kind="ellipse",
          base=(200, 200))
    s.obj("Triángulo claro", solid(soft), lambda fr, u: (560, 980, 1500 * (1 - 0.7 * k(fr, 0, 15)),
                                                         1300 * (1 - 0.7 * k(fr, 0, 15)), 160 + 6 * fr,
                                                         1.0 if fr < 15 else 0.0), path=TRIANGLE, base=(1500, 1300))
    tsz = f6.curve([(0, 1400), (15, 400), (21, 180), (33, 120), (40, 70), (46, 70)])
    s.obj("Play", solid(WHITE), lambda fr, u: (540 + tsz(fr) * 0.05, ry(fr) + up(fr), tsz(fr) * 0.86, tsz(fr), 
                                               180 + 7.5 * min(fr, 40), 1.0), path=TRIANGLE, base=(1204, 1400))
    for i, (x, y, at) in enumerate(((248, 850, 45), (740, 1014, 48), (1000, 1080, 51))):
        s.obj(f"Punto {i + 1}", solid(BLACK), lambda fr, u, x=x, y=y, at=at: (x, y + up(fr), 40 * k(fr, at, 4),
                                                                             40 * k(fr, at, 4), 0, 1), kind="ellipse",
              base=(40, 40))
    bx, by, bd = f6.curve([(57, 540), (81, 536)]), f6.curve([(42, 2500), (54, 1671), (57, 1671), (81, 160)]), \
        f6.curve([(57, 842), (81, 680)])
    s.obj("Disco negro (sombra)", solid(grey), lambda fr, u: (540, by(fr) + 420 + up(fr), 1100, 900, 0,
                                                              1 - k(fr, 57, 4)), kind="ellipse")
    s.obj("Disco negro", solid(BLACK), lambda fr, u: (bx(fr), by(fr), bd(fr), bd(fr), 0, 1), kind="ellipse",
          base=(842, 842))
    s.obj("Disco negro (punto)", solid(RED), lambda fr, u: (bx(fr), by(fr), 130 * k(fr, 48, 6), 130 * k(fr, 48, 6), 0, 1),
          kind="ellipse", base=(130, 130))
    ry2 = f6.curve([(60, 2600), (84, 1740)])
    s.obj("Disco rojo", solid(RED), lambda fr, u: (556, ry2(fr), 660, 660, 0, 1), kind="ellipse")
    s.obj("Disco rojo (punto)", solid(WHITE), lambda fr, u: (552, ry2(fr) - 10, 128, 128, 0, 1), kind="ellipse")
    s.say("WELCOME", (80, 750, 970, 950), ANTON, 400, BLACK, shift=lambda fr: (-1100 * (1 - k(fr, 78, 9)), 0),
          reveal=lambda fr: (0, 700, W, 960))
    s.say("TO MY", (280, 970, 820, 1180), ANTON, 400, BLACK, "Título 2", shift=lambda fr: (900 * (1 - k(fr, 87, 9)), 0),
          reveal=lambda fr: (0, 960, W, 1190))
    s.rect("Subrayado", solid(RED), lambda fr, u: (556, 1196, 556 + 252 * k(fr, 99, 9), 1212))
    return art_except(t)


def half(bulge=1.0, n=16):
    """A circle segment: flat side on the left (x = 0), the arc bulging right to x = 100."""
    return poly([(100 * bulge * math.cos(math.radians(a)) if bulge else 0, 50 + 50 * math.sin(math.radians(a)))
                 for a in [-90 + 180 * i / n for i in range(n + 1)]])


# --- 3. Human Rights: a white eye on yellow, a slice orbits it, it grows, the words fade in over a red pill ---------
def human_rights():
    D = dur_for(1.9)
    t = _p("derechos", "Historia: círculo blanco sobre amarillo", "Story: white circle on yellow", 12702, D,
           ["amarillo", "círculo"])
    s = T(t, D)
    bg(s, YELLOW)
    cx = f6.curve([(3, 760), (9, 487), (27, 568), (36, 566), (42, 560)])
    cy = f6.curve([(3, 1007), (27, 906), (36, 705), (42, 635)])
    d = f6.curve([(3, 0), (6, 400), (9, 566), (27, 603), (36, 996), (42, 1210)])
    sl = f6.curve([(9, 0), (12, 45), (33, 60), (36, 0)])
    ang = f6.curve([(12, -5), (21, -40), (33, -125)])

    def slice_(fr, u):
        a = math.radians(ang(fr))
        r = d(fr) / 2 + 30
        x, y = cx(fr) + (r + 0.18 * d(fr)) * math.cos(a), cy(fr) + (r + 0.18 * d(fr)) * math.sin(a)
        return x, y, 0.36 * d(fr), d(fr) * 0.95, ang(fr), 1.0 if 12 <= fr < 36 else 0.0
    s.obj("Rodaja", solid(WHITE), slice_, path=half())
    s.obj("Círculo", solid(WHITE), lambda fr, u: (cx(fr), cy(fr), d(fr), d(fr), 0, 1), kind="ellipse", base=(1210, 1210))
    s.obj("Punto", solid(BLACK), lambda fr, u: (cx(fr), cy(fr) - 0.02 * d(fr), 0.16 * d(fr), 0.16 * d(fr), 0, 1),
          kind="ellipse", base=(194, 194))
    wx = lambda fr: -900 * (1 - k(fr, 36, 12))  # noqa: E731
    s.obj("Media luna", solid(WHITE), lambda fr, u: (430 + wx(fr), 1575 + 0.2 * wx(fr), 380, 1000,
                                                     100 + 40 * (1 - k(fr, 36, 12)), 1.0 if fr >= 36 else 0.0),
          path=half(), base=(380, 1000))
    s.obj("Aro", ring("#555555", 3), lambda fr, u: (810, 1466, 220, 220, 0, k(fr, 3, 6)), kind="ellipse")
    s.obj("Aro (play)", solid(RED), lambda fr, u: (810, 1466, 20, 16, 90, k(fr, 3, 6)), path=TRIANGLE)
    c = s.say("FASHION", (784, 96, 886, 120), ANTON, 400, BLACK, "Texto")
    s.letters(c, 6, stagger=0.02, duration=0.2, preset="fade")
    s.say("YOUTUBE - PROMO", (-28, 1702, 202, 1728), ANTON, 400, BLACK, "Texto 2", rot=lambda fr, u: -90,
          op=lambda fr, u: k(fr, 6, 6))
    s.rect("Línea", solid(RED), lambda fr, u: (0, 1912, W, 1920))
    c = s.say("Human Rights", (66, 824, 1024, 970), ANTON, 400, BLACK)
    s.letters(c, 39, stagger=0.3, duration=0.25, preset="fade", unit="word")

    def pill(fr, u):
        x0 = 530 - 160 * k(fr, 48, 3)
        x1 = 530 + 190 * k(fr, 45, 6)
        h = 4 + 86 * k(fr, 51, 4)
        return x0, 1079 - h / 2 - 25 * (1 - k(fr, 51, 4)), x1, 1079 + h / 2 - 25 * (1 - k(fr, 51, 4))
    s.rect("Píldora", solid(RED), pill, op=lambda fr, u: 1.0 if fr >= 45 else 0.0)
    s.say("ALL ABOUT FASHION", (420, 1068, 670, 1090), ANTON, 400, WHITE, "Texto 3",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 54, 3)))
    return art_except(t)


BELL = poly([(50, 4), (63, 10), (72, 28), (73, 58), (88, 76), (12, 76), (27, 58), (28, 28), (37, 10)]) + " " + \
    poly([(40, 82), (60, 82), (56, 94), (44, 94)])
THUMB = poly([(6, 44), (26, 44), (26, 96), (6, 96)]) + " " + \
    poly([(32, 44), (48, 12), (56, 6), (64, 14), (60, 38), (90, 38), (96, 48), (88, 94), (32, 94)])
HEART = "M 50 92 L 10 50 Q 0 38 6 24 Q 14 8 30 8 Q 44 8 50 22 Q 56 8 70 8 Q 86 8 94 24 Q 100 38 90 50 Z"


def icon_box(s, name, rect, back, glyph, ink, at):
    x0, y0, x1, y1 = rect
    cx, cy, w = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0
    s.obj(name, solid(back), lambda fr, u: (cx, cy, w * k(fr, at, 6), (y1 - y0) * k(fr, at, 6), 0, 1),
          base=(w, y1 - y0))
    s.obj(f"{name} (icono)", solid(ink), lambda fr, u: (cx, cy, w * 0.5 * k(fr, at + 3, 6), w * 0.5 * k(fr, at + 3, 6),
                                                        0, 1), path=glyph, base=(w * 0.5, w * 0.5))


# --- 4. love: the camera climbs a face with big black words, a red «love» drops in, a subscribe card ---------------
def love():
    D = dur_for(2.6)
    t = _p("love", "Historia: love con tarjeta de suscripción", "Story: love with a subscribe card", 12703, D,
           ["foto", "suscribirse"])
    s = T(t, D)
    bg(s, WHITE)  # hidden by the photo in the story; the ground beside it in a normal video
    pan = lambda fr: -760 * (1 - k(fr, 0, 72))  # noqa: E731
    photo(s, "fx-face-04", box=(0, 0, W, 2680), geom=lambda fr, u: (0, pan(fr), 1))
    for i, (word, y) in enumerate((("bodily", 2050), ("integrity", 2280))):
        # cut at the story's right edge (the words run off it), also when a normal video shows the story as a column
        s.say(word, (300, y, 1400, y + 200), ANTON, 400, "#141414", f"Texto {i + 1}", align="left", editable=i == 0,
              shift=lambda fr: (0, pan(fr)), reveal=lambda fr: (0, 0, W, H))
    s.say("love", (94, 146, 972, 724), ANTONIO, 700, "#E3131B", geom=lambda fr, u: (0, -900 * (1 - k(fr, 27, 15)), 1, 0, 1))
    s.rect("Marco", solid(WHITE), lambda fr, u: (441, 877, 972, 1401))
    photo(s, "portrait-02", box=(500, 882, 967, 1344), name="Foto 2")
    s.say("2021", (806, 924, 948, 1007), ANTONIO, 500, WHITE, "Texto 3")
    s.rect("Suscribirse", solid(RED), lambda fr, u: (441, 1408, 972, 1613))
    s.say("SUBSCRIBE", (590, 1486, 823, 1537), ANTONIO, 500, WHITE, "Botón")
    icon_box(s, "Campana", (689, 1636, 818, 1754), WHITE, BELL, RED, 36)
    icon_box(s, "Me gusta", (844, 1636, 972, 1754), RED, THUMB, WHITE, 42)
    s.rect("Panel", solid(RED), lambda fr, u: (0, 1450 + 462 * k(fr, 0, 18), W, H + 10))
    return art_except(t)


# --- 5. 2/6: photos, a yellow frame and red columns, with a like counter that ticks up -------------------------------
def counter():
    D = dur_for(1.2, 2.6)
    t = _p("contador", "Historia: 2/6 con fotos y marco amarillo", "Story: 2/6 with photos and a yellow frame", 12704, D,
           ["foto", "amarillo", "contador"])
    s = T(t, D)
    bg(s, WHITE)
    photo(s, "fx-woman-05", box=(0, 0, 826, 639), rect=lambda fr, u: (0, 0, 826 * k(fr, 0, 12), 639))
    s.rect("Columna", solid(RED), lambda fr, u: (826, -10, W, 639 * k(fr, 3, 12)))
    s.say("UNIQUE TECHNOLOGY", (871, 304, 1024, 322), ANTON, 400, WHITE, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.say("2/6", (40, 705, 174, 796), ANTONIO, 500, BLACK, align="left",
          geom=lambda fr, u: (0, 40 * (1 - k(fr, 12, 9)), 1, 0, k(fr, 12, 6)))
    s.say("CLEAN DESIGN", (40, 1238, 200, 1260), ANTON, 400, BLACK, "Texto 2", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.rect("Marco amarillo", solid(YELLOW), lambda fr, u: (240 + 840 * (1 - k(fr, 6, 12)), 650, W, 1296))
    photo(s, "food-01", box=(369, 784, 944, 1155), name="Foto 2", rect=lambda fr, u: (369, 784, 369 + 575 * k(fr, 12, 12), 1155))
    s.obj("Flecha", ring(BLACK, 4), lambda fr, u: (308, 1228, 52, 52, 0, k(fr, 21, 6)),
          path="M 0 100 L 100 0 M 35 0 L 100 0 L 100 65")
    photo(s, "fx-face-06", box=(0, 1308, 803, 1920), name="Foto 3", rect=lambda fr, u: (0, 1308, 803 * k(fr, 6, 12), 1920))
    s.rect("Columna 2", solid(RED), lambda fr, u: (803, 1920 - 612 * k(fr, 9, 12), W + 10, 1920))
    s.say("3/6", (873, 1367, 1014, 1472), ANTONIO, 500, WHITE, "Título 2",
          geom=lambda fr, u: (0, 40 * (1 - k(fr, 18, 9)), 1, 0, k(fr, 18, 6)))
    s.say("MODERN STYLE", (880, 1860, 1040, 1882), ANTON, 400, WHITE, "Texto 3", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 6)))
    s.obj("Me gusta", solid(RED), lambda fr, u: (632, 438, 130 * k(fr, 24, 6), 70 * k(fr, 24, 6), 0, 1), radius=8,
          base=(130, 70))
    s.obj("Me gusta (pico)", solid(RED), lambda fr, u: (600, 480, 22 * k(fr, 24, 6), 18 * k(fr, 24, 6), 90, 1),
          path=TRIANGLE)
    s.obj("Me gusta (corazón)", solid(WHITE), lambda fr, u: (668, 438, 22 * k(fr, 27, 4), 20 * k(fr, 27, 4), 0, 1),
          path=HEART, base=(22, 20))
    c = s.say("714", (580, 424, 640, 452), ANTONIO, 500, WHITE, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 4)))
    c["textStyle"].update(counter=True, counterFrom=668, counterSeconds=2.4)
    return t


def tag(s, name, text, rect, at, colour=BLACK, back=WHITE):
    x0, y0, x1, y1 = rect
    s.obj(name, solid(back), lambda fr, u: ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * k(fr, at, 6), y1 - y0, 0,
                                            1.0 if fr >= at else 0.0), base=(x1 - x0, y1 - y0))
    s.obj(f"{name} (pico)", solid(back), lambda fr, u: (x0 + 30, y1 + 8, 18, 16 * k(fr, at + 3, 3), 90, 1),
          path=TRIANGLE)
    h = (y1 - y0) * 0.36
    s.say(text, (x0 + 16, (y0 + y1) / 2 - h / 2, x1 - 16, (y0 + y1) / 2 + h / 2), ANTON, 400, colour, f"{name} (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, at + 4, 4)))


def ring_path(r_share):
    """A closed circle of radius r_share (percent of the box) round the box centre, from the top clockwise (four
    cubics: the path parser has no arcs), for textStyle pathSvg: the baseline runs round it, letters outward."""
    p, q = r_share, r_share * 0.5523
    return (f"M 50 {50 - p:.3f} C {50 + q:.3f} {50 - p:.3f} {50 + p:.3f} {50 - q:.3f} {50 + p:.3f} 50 "
            f"C {50 + p:.3f} {50 + q:.3f} {50 + q:.3f} {50 + p:.3f} 50 {50 + p:.3f} "
            f"C {50 - q:.3f} {50 + p:.3f} {50 - p:.3f} {50 + q:.3f} {50 - p:.3f} 50 "
            f"C {50 - p:.3f} {50 - q:.3f} {50 - q:.3f} {50 - p:.3f} 50 {50 - p:.3f} Z")


def circle_text(s, text, cx, cy, r, cap, colour, span, geom, name="Texto circular"):
    """One text on a circle (the engine's text on a path): its baseline runs clockwise round (cx, cy) at radius r from
    the top, the letters spaced to cover `span` degrees; geom(fr, u) = (scale, turn, opacity) grows it about the centre
    and turns the whole ring (the start of the text sits at `turn` degrees clockwise from the top)."""
    c = s.say(text, (cx - 300, cy - cap / 2, cx + 300, cy + cap / 2), ANTON, 400, colour, name, align="left")
    st = c["textStyle"]
    f = f6._font(ANTON, 400)
    cap_px = f.getbbox("H")[3] - f.getbbox("H")[1]
    natural = f.getlength(text) * st["pixelSize"] / f.size if hasattr(f, "size") else f.getlength(text) * cap / cap_px
    arc_len = math.radians(span) * r
    st["letterSpacing"] = round(max(0.0, (arc_len - natural) / max(1, len(text) - 1)), 2)
    st["wordWrap"] = False
    side = 2 * (r + 3 * cap)
    st["pathSvg"] = ring_path(100 * r / side)
    for key, v in (("x", cx - side / 2), ("y", cy - side / 2), ("width", side), ("height", side)):
        c[key] = keys([(0.0, v, "hold")])
    s.tmove(c, lambda fr, u: (lambda g: (0, 0, g[0], g[1], g[2]))(geom(fr, u)))
    return c


# --- 6. Anna Martin (a singer's name in the reference): a red panel slides in beside a round photo, the name and its age --------------------------------
def alice_circle():
    D = dur_for(1.6)
    t = _p("nombre-circulo", "Historia: nombre junto a una foto redonda", "Story: name beside a round photo", 12705, D,
           ["foto", "nombre"])
    s = T(t, D)
    photo(s, "fx-fashion-04", geom=lambda fr, u: (0, 0, 1.08 - 0.08 * k(fr, 0, 30)))
    s.rect("Franja", solid(YELLOW), lambda fr, u: (0, 0, 44, H * k(fr, 0, 9)))
    s.say("YOUTUBE", (90, 92, 200, 118), ANTON, 400, WHITE, "Texto", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 3, 6)))
    s.rect("Panel", solid(RED), lambda fr, u: (424 + 660 * (1 - k(fr, 9, 12)), 600, W + 10, 1290))
    s.obj("Aro fino", ring(WHITE, 3), lambda fr, u: (710, 710, 232 * k(fr, 15, 9), 232 * k(fr, 15, 9), 0, 0.7),
          kind="ellipse", base=(232, 232))
    sc = lambda fr: 0.2 + 0.8 * k(fr, 0, 15)  # noqa: E731
    s.obj("Círculo", solid(WHITE), lambda fr, u: (540, 930, 628 * sc(fr), 628 * sc(fr), 0, 1), kind="ellipse",
          base=(628, 628))
    photo(s, "portrait-07", box=(245, 635, 835, 1225), name="Foto 2", oval=True,
          geom=lambda fr, u: (0, 0, sc(fr)))
    s.obj("Punto rojo", solid(RED), lambda fr, u: (250, 864, 36 * k(fr, 18, 4), 36 * k(fr, 18, 4), 0, 1),
          kind="ellipse", base=(36, 36))
    s.obj("Medio punto", solid(WHITE), lambda fr, u: (1060, 956, 80, 80, 0, k(fr, 18, 4)), kind="ellipse")
    s.say("24Y.O", (820, 682, 894, 708), ANTON, 400, "#3A0000", "Texto 2", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 33, 6)))
    c = s.say("Anna", (580, 960, 800, 1064), ANTON, 400, BLACK, align="left")
    s.letters(c, 30, stagger=0.04, duration=0.15, preset="fade")
    c = s.say("Martin", (580, 1080, 930, 1190), ANTON, 400, BLACK, "Título 2", align="left")
    s.letters(c, 39, stagger=0.04, duration=0.15, preset="fade")
    s.rect("Subrayado", solid(YELLOW), lambda fr, u: (580, 1200, 580 + 384 * k(fr, 39, 9), 1212))
    s.obj("Aro", ring(WHITE, 3), lambda fr, u: (170, 1690, 200, 200, 0, k(fr, 9, 9)), kind="ellipse")
    s.say("WATCH", (130, 1680, 210, 1700), ANTON, 400, WHITE, "Texto 3", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 12, 6)))
    return t


# --- 7. MY PLAN: a red panel multiplied over the photo, a yellow sticker that turns, a list and a YouTube tab -------
def my_plan():
    D = dur_for(1.6, 2.6)
    t = _p("mi-plan", "Historia: mi plan con lista y etiqueta", "Story: my plan with a list and a label", 12706, D,
           ["foto", "lista", "youtube"])
    s = T(t, D)
    photo(s, "friends-08")
    s.obj("Arco", ring(BLACK, 80), lambda fr, u: (1150, 1150, 2200, 2200, -20 + 20 * k(fr, 0, 24), k(fr, 0, 6)),
          path=arc(215, 262))
    pan = s.rect("Panel", solid(RED), lambda fr, u: (370, 90, 1024, 90 + 960 * k(fr, 0, 12)))
    pan["blendMode"] = "multiply"
    sz = lambda fr: k(fr, 3, 9)  # noqa: E731
    s.obj("Pegatina", solid(YELLOW), lambda fr, u: (366, 280, 250 * sz(fr), 250 * sz(fr), 0, 1), kind="ellipse",
          base=(250, 250))
    s.obj("Pegatina (punto)", solid(WHITE), lambda fr, u: (366, 280, 40 * sz(fr), 40 * sz(fr), 0, 1), kind="ellipse",
          base=(40, 40))
    # the words run round the sticker's edge and the ring keeps turning anticlockwise (fast at first, then steady)
    circle_text(s, "WHO DICTATES FASHION?", 366, 280, 80, 21, "#2A1A00", 195,
                lambda fr, u: (max(1e-3, sz(fr)), 24 - 36 * u + 90 * (1 - k(fr, 3, 21)), 1.0 if fr >= 3 else 0.0))
    c = s.say("MY PLAN:", (500, 464, 700, 510), ANTON, 400, WHITE, "Título", align="left")
    s.letters(c, 12, stagger=0.04, duration=0.1, preset="fade")
    s.rect("Línea", solid(WHITE), lambda fr, u: (500, 624, 504, 624 + 240 * k(fr, 18, 9)))
    for i, (item, x1, at) in enumerate((("interviews with influencers", 926, 21), ("sculpture exhibition", 824, 27),
                                        ("blog editing", 708, 33))):
        y = 626 + 105 * i
        c = s.say(item, (540, y, x1, y + 34), ANTON, 400, WHITE, f"Texto {i + 1}", align="left")
        s.letters(c, at, stagger=0.015, duration=0.06, preset="fade")
    s.rect("Caja", solid(WHITE), lambda fr, u: (90, 1470, 90 + 744 * k(fr, 6, 12), 1656))
    c = s.say("FASHION IN REAL TIME", (194, 1530, 732, 1594), ANTON, 400, BLACK, "Título 2")
    s.letters(c, 15, stagger=0.02, duration=0.1, preset="fade")
    s.yt("YouTube", lambda fr, u: (300, 1463, k(fr, 12, 6), 0, 1), w=108, h=58, red=RED)
    s.rect("Barra", solid(RED), lambda fr, u: (10, 1680, 10 + 530 * k(fr, 9, 12), 1730))
    s.say("SOCIAL BLOG", (190, 1693, 336, 1717), ANTON, 400, WHITE, "Texto 4",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.rect("Línea de abajo", solid(RED), lambda fr, u: (0, 1890, W * k(fr, 0, 12), 1906))
    s.rect("Línea amarilla", solid(YELLOW), lambda fr, u: (100, 1890, 100 + 500 * k(fr, 3, 12), 1906))
    return t


# --- 8. For instance: yellow words slide in on red, a photo opens over them, tags pop on the photo below ----------
def for_instance():
    D = dur_for(1.6, 2.4)
    t = _p("por-ejemplo", "Historia: frase amarilla sobre rojo con fotos", "Story: yellow phrase on red with photos",
           12707, D, ["foto", "frase"])
    s = T(t, D)
    photo(s, "fx-woman-07", box=(0, 900, W, 1900), name="Foto")
    s.rect("Fondo", solid(RED), lambda fr, u: (-10, -10, W + 10, 930 + 900 * (1 - k(fr, 0, 9))))
    for i, line in enumerate(("For", "instance", "a business", "small")):
        y = 76 + 205 * i
        s.say(line, (236, y, 1400, y + 164), ANTONIO, 400, "#FFE234", f"Título {i + 1}" if i else "Título",
              align="left", reveal=lambda fr: (0, 0, W, 930),
              shift=lambda fr, i=i: (-1200 * (1 - k(fr, 3 + 2 * i, 12)), 0))
    sc = lambda fr: 0.15 + 0.85 * k(fr, 0, 15)  # noqa: E731
    photo(s, "fx-fashion-01", box=(330, 190, 810, 760), name="Foto 2", geom=lambda fr, u: (0, 0, sc(fr)))
    s.rect("Línea", solid(WHITE), lambda fr, u: (360, 314, 360 + 440 * k(fr, 27, 9), 318), op=lambda fr, u: 0.8)
    s.say("2021", (670, 222, 790, 298), ANTONIO, 400, WHITE, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 33, 6)))
    s.obj("Corazón", solid(WHITE), lambda fr, u: (906, 114, 48 * k(fr, 18, 6), 44 * k(fr, 18, 6), 0, 1), path=HEART,
          base=(48, 44))
    s.obj("Corazón rojo", solid(RED), lambda fr, u: (110, 1016, 40 * k(fr, 24, 6), 36 * k(fr, 24, 6), 0, 1),
          path=HEART, base=(40, 36))
    tag(s, "Etiqueta", "#HAIRSTYLES", (710, 1310, 880, 1370), 27)
    tag(s, "Etiqueta 2", "#FRESHFRUITS", (316, 1794, 500, 1850), 33)
    s.obj("Aro", ring(WHITE, 3), lambda fr, u: (710, 1700, 240, 240, 0, 0.6 * k(fr, 30, 9)), kind="ellipse")
    s.rect("Línea de abajo", solid(YELLOW), lambda fr, u: (0, 1890, W, 1920))
    return t


# --- 9. VLOGGER: the word grows on the photo with little hearts floating, a subscribe bar slides in ----------------
def vlogger():
    D = dur_for(1.4, 2.6)
    t = _p("vlogger", "Historia: VLOGGER con corazones y suscribirse", "Story: VLOGGER with hearts and subscribe", 12708,
           D, ["foto", "suscribirse", "corazones"])
    s = T(t, D)
    photo(s, "fx-woman-03", geom=lambda fr, u: (0, 0, 1.06 - 0.06 * k(fr, 0, 40)))
    ink = (116, 1380, 980, 1640)
    sc = lambda fr: 0.18 + 0.82 * k(fr, 0, 9)  # noqa: E731
    s.say("VLOGGER", ink, ANTONIO, 700, WHITE, geom=lambda fr, u: (*s.about(ink, 548, 1510, sc(fr)), sc(fr), 0,
                                                                     k(fr, 0, 2)))
    for i, (x, y, at, size) in enumerate(((300, 1560, 6, 34), (420, 1480, 10, 26), (560, 1600, 14, 30), (640, 1420, 8, 22),
                                          (780, 1540, 12, 34), (880, 1470, 16, 24), (350, 1440, 20, 20),
                                          (700, 1620, 18, 26))):
        def hg(fr, u, x=x, y=y, at=at, size=size, i=i):
            ph = ((u * FPS - at) / 45.0) % 1.0 if u * FPS >= at else 0.0
            return (x + 14 * math.sin(6.28 * ph + i), y - 90 * ph, size, size * 0.9, 0,
                    k(fr, at, 3) * (1 - ph) if u * FPS >= at else 0.0)
        s.obj(f"Corazón {i + 1}", solid(RED), hg, path=HEART, base=(34, 31))
    s.rect("Suscribirse", solid(RED), lambda fr, u: (464 + 640 * (1 - k(fr, 27, 9)), 1680, W + 640 * (1 - k(fr, 27, 9)) - 40,
                                                       1776))
    s.say("SUBSCRIBE", (524, 1710, 700, 1744), ANTON, 400, WHITE, "Botón", align="left",
          shift=lambda fr: (640 * (1 - k(fr, 30, 9)), 0), reveal=lambda fr: (464, 1680, W, 1776))
    s.obj("Flecha", ring(WHITE, 3), lambda fr, u: (910 + 640 * (1 - k(fr, 30, 9)), 1724, 120, 24, 0, 1),
          path="M 0 50 L 100 50 M 80 10 L 100 50 L 80 90")
    return t


# --- 10. Social Media: the photo wipes down from the top, the words ride its edge, «follow me» lines slide in -------
def social_media():
    D = dur_for(1.6, 2.4)
    t = _p("social-media", "Historia: Social Media con follow me", "Story: Social Media with follow me", 12709, D,
           ["foto", "seguir"])
    s = T(t, D)
    bg(s, WHITE)
    edge = lambda fr: H * k(fr, 0, 21)  # noqa: E731
    photo(s, "fx-woman-04", rect=lambda fr, u: (0, 0, W, edge(fr)))
    ride = lambda fr: -560 * (1 - k(fr, 3, 21))  # noqa: E731
    s.obj("Punto", solid(BLACK), lambda fr, u: (123, 810, 66 * k(fr, 24, 4), 66 * k(fr, 24, 4), 0, 1), kind="ellipse",
          base=(66, 66))
    s.say("Social", (510, 974, 940, 1160), ANTONIO, 400, WHITE, align="left",
          geom=lambda fr, u: (0, ride(fr), 1, 0, 1.0 if fr >= 6 else 0.0))
    s.say("Media", (530, 1190, 960, 1360), ANTONIO, 400, WHITE, "Título 2", align="left",
          geom=lambda fr, u: (0, ride(fr), 1, 0, 1.0 if fr >= 6 else 0.0))
    s.rect("Caja", solid(RED), lambda fr, u: (516, 1396 + ride(fr), 980, 1396 + ride(fr) + 448 * k(fr, 6, 9)))
    for i in range(4):
        y0 = 1430 + 100 * i

        def rv(fr, y0=y0):
            return (516, y0 - 10 + ride(fr), 980, y0 + 100 + ride(fr))
        s.say("follow me", (544, y0, 936, y0 + 90), ANTONIO, 700, BLACK, f"Texto {i + 1}", align="left",
              editable=i == 0, reveal=rv, shift=lambda fr, i=i: (-420 * (1 - k(fr, 9 + 3 * i, 9)), ride(fr)))
    s.rect("Línea", solid(RED), lambda fr, u: (0, 1904, W * k(fr, 12, 12), 1920))
    return t


def outlined(colour, width):
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "solid", "color": "#ffffffff"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
             "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


# --- 11. Anna Martin: a round photo in a red ring, dots in a thin circle, a red ball, the giant name drifting ------
def name_white():
    D = dur_for(1.4, 2.6)
    t = _p("nombre-blanco", "Historia: nombre con foto redonda sobre blanco", "Story: name with a round photo on white",
           12710, D, ["foto", "nombre"])
    s = T(t, D)
    bg(s, WHITE)
    giant = "Anna Martin"
    size_h = 335
    f = f6._font(ANTON, 400)
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    px = size_h / cap
    full = f.getlength(giant) * px
    pre = f.getlength("Anna M") * px
    a_w = f.getlength("a") * px
    x0 = 560 - pre
    drift = lambda fr, u: -40 * u - 60 * (1 - k(fr, 0, 30))  # noqa: E731
    s.say(giant, (x0, 1548, x0 + full, 1883), ANTON, 400, "#F4F4F4", "Fondo (texto)", align="left",
          layers=outlined("#E6CFCF", 2), geom=lambda fr, u: (drift(fr, u), 0, 1, 0, k(fr, 0, 9)))
    s.say("a", (560, 1548, 560 + a_w, 1883), ANTON, 400, RED, "Letra", align="left",
          geom=lambda fr, u: (drift(fr, u), 0, 1, 0, k(fr, 6, 6)))
    s.obj("Aro fino", ring("#D6D6D6", 3), lambda fr, u: (374, 393, 554 * k(fr, 0, 12), 554 * k(fr, 0, 12), 0, 1),
          kind="ellipse", base=(554, 554))
    orbit = lambda fr, u: 30 * u  # noqa: E731
    s.obj("Punto negro", solid(BLACK), lambda fr, u: (*rot_pt(432, 420, orbit(fr, u), 374, 393), 100 * k(fr, 6, 6),
                                                      100 * k(fr, 6, 6), 0, 1), kind="ellipse", base=(100, 100))
    s.obj("Punto rojo", solid(RED), lambda fr, u: (*rot_pt(504, 307, orbit(fr, u) * 1.5, 374, 393), 50 * k(fr, 9, 6),
                                                   50 * k(fr, 9, 6), 0, 1), kind="ellipse", base=(50, 50))
    sc = lambda fr: k(fr, 3, 12)  # noqa: E731
    s.obj("Aro rojo", solid(RED), lambda fr, u: (538, 866, 462 * sc(fr), 462 * sc(fr), 0, 1), kind="ellipse",
          base=(462, 462))
    photo(s, "portrait-07", box=(328, 656, 748, 1076), name="Foto", oval=True, geom=lambda fr, u: (0, 0, max(0.001, sc(fr))))
    bx = f6.curve([(0, 300), (21, 300), (33, 892)])
    by = f6.curve([(0, 1300), (21, 1300), (33, 1363)])
    s.obj("Bola roja", solid(RED), lambda fr, u: (bx(fr), by(fr), 240 * k(fr, 0, 9), 240 * k(fr, 0, 9), 0, 1),
          kind="ellipse", base=(240, 240))
    c = s.say("Anna Martin", (342, 1197, 739, 1270), ANTON, 400, BLACK, "Título")
    s.letters(c, 24, stagger=0.03, duration=0.1, preset="fade")
    s.say("SOCIAL BLOGGER", (430, 1284, 647, 1312), ANTON, 400, RED, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 33, 6)))
    s.rect("Línea", solid(RED), lambda fr, u: (0, 1898, W * k(fr, 0, 15), 1912))
    return t


SEARCH = "M 42 8 A 34 34 0 1 1 41.9 8 Z"


# --- 12. 01 → 02: a numbered story; a red wipe brings slide 02 with its phrase typed and a search tag ---------------
def numbers():
    D = dur_for(4.4, 1.8)
    t = _p("numeros", "Historia: diapositivas 01 y 02", "Story: slides 01 and 02", 12711, D, ["foto", "números"])
    s = T(t, D)
    bg(s, WHITE)
    c = s.say("01", (120, 240, 705, 1100), ANTONIO, 700, RED, "Número", align="left", reveal=lambda fr: (0, 0, W, 879),
              shift=lambda fr: (0, 900 * (1 - k(fr, 3, 12))))
    s.say("YOUTUBE - PROMO", (883, 670, 1139, 696), ANTON, 400, RED, "Texto", rot=lambda fr, u: 90,
          op=lambda fr, u: k(fr, 9, 6))
    photo(s, "fx-woman-06", box=(0, 879, W, 1920), name="Foto", rect=lambda fr, u: (0, 1920 - 1041 * k(fr, 0, 12), W, 1920))
    photo(s, "fx-woman-04", box=(321, 714, 774, 1050), name="Foto 2",
          rect=lambda fr, u: (321, 714, 774, 714 + 336 * k(fr, 9, 9)))
    s.obj("Aro", ring("#F2D36B", 3), lambda fr, u: (594, 1575, 252 * k(fr, 12, 9), 252 * k(fr, 12, 9), 0, 1),
          kind="ellipse", base=(252, 252))
    for i, (line, x1) in enumerate((("Clothes separate people", 636), ("into groups.", 420))):
        y = 1701 + 45 * i
        c = s.say(line, (144, y, x1, y + 33), ANTON, 400, WHITE, f"Texto {i + 2}", align="left")
        s.letters(c, 15 + 4 * i, stagger=0.02, duration=0.08, preset="fade")
    # the wipe to 02
    wipe = lambda fr: W * k(fr, 75, 12)  # noqa: E731
    s.rect("Rojo", solid(RED), lambda fr, u: (0, -10, wipe(fr), 857))
    s.say("02", (103, 280, 843, 1100), ANTONIO, 700, WHITE, "Número 2", align="left",
          reveal=lambda fr: (0, 0, wipe(fr), 857))
    s.say("YOUTUBE - PROMO", (891, 652, 1147, 678), ANTON, 400, YELLOW, "Texto 4", rot=lambda fr, u: 90,
          op=lambda fr, u: k(fr, 87, 6))
    s.rect("Cuadro", solid(WHITE), lambda fr, u: (1036, 0, W, 47 * k(fr, 90, 6)))
    photo(s, "fx-woman-07", box=(0, 857, W, 1920), name="Foto 3",
          rect=lambda fr, u: (W - W * k(fr, 81, 12), 857, W, 1920))
    for i, (line, x1) in enumerate((("Fashion is an endless", 543), ("popularity contest.", 500))):
        y = 67 + 69 * i
        c = s.say(line, (112, y, x1, y + 46), ANTON, 400, WHITE, f"Texto {i + 5}", align="left")
        s.letters(c, 93 + 12 * i, stagger=0.025, duration=0.08, preset="fade")
    s.obj("Lupa (fondo)", solid(RED), lambda fr, u: (466, 986, 72 * k(fr, 114, 6), 72 * k(fr, 114, 6), 0, 1),
          kind="ellipse", base=(72, 72))
    s.obj("Lupa", ring(WHITE, 4), lambda fr, u: (462, 982, 28 * k(fr, 117, 4), 28 * k(fr, 117, 4), 0, 1),
          kind="ellipse", base=(28, 28))
    s.obj("Lupa (mango)", solid(WHITE), lambda fr, u: (478, 998, 14 * k(fr, 117, 4), 4, 45, 1))
    s.obj("Píldora", solid(WHITE), lambda fr, u: (527 + 79 * k(fr, 117, 6), 986, 158 * k(fr, 117, 6), 76, 0, 1),
          radius=38, base=(158, 76))
    s.say("YOUTUBE PROMO", (548, 978, 664, 994), ANTON, 400, RED, "Texto 7", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 123, 4)))
    s.obj("Aro 2", ring("#F2D36B", 3), lambda fr, u: (195, 1247, 245 * k(fr, 96, 9), 245 * k(fr, 96, 9), 0, 1),
          kind="ellipse", base=(245, 245))
    s.obj("Aro 2 (play)", solid(WHITE), lambda fr, u: (198, 1247, 22 * k(fr, 102, 4), 26 * k(fr, 102, 4), 0, 1),
          path=TRIANGLE, base=(22, 26))
    s.rect("Línea", solid(RED), lambda fr, u: (320, 1904, 320 + 404 * k(fr, 100, 12), 1912))
    return art_except(t)


# --- 13. FOUNDATIONS OF FASHION: a photo, a white half-moon on top, a tilted red pill and a credits line ----------
def foundations():
    D = dur_for(1.2, 2.6)
    t = _p("fundamentos", "Historia: etiqueta roja inclinada sobre foto", "Story: tilted red label over a photo", 12712,
           D, ["foto", "etiqueta", "youtube"])
    s = T(t, D)
    photo(s, "fx-woman-07", geom=lambda fr, u: (0, 0, 1.04 - 0.04 * k(fr, 0, 30)))
    s.obj("Papel", solid(WHITE), lambda fr, u: (540, 1790 + 300 * (1 - k(fr, 0, 12)), 1200, 300, -3, 1))
    s.say("BLOG", (640, 1700, 1300, 1990), ANTON, 400, "#3A3A3A", "Fondo (texto)", align="left", rot=lambda fr, u: -3,
          op=lambda fr, u: 0.85 * k(fr, 6, 9), editable=False)
    s.obj("Media luna", solid(WHITE), lambda fr, u: (559, 42, 194 * k(fr, 0, 9), 194 * k(fr, 0, 9), 0, 1),
          kind="ellipse", base=(194, 194))
    s.obj("Media luna (punto)", solid(BLACK), lambda fr, u: (559, 42, 50 * k(fr, 3, 6), 50 * k(fr, 3, 6), 0, 1),
          kind="ellipse", base=(50, 50))
    tilt = -3
    g = lambda fr: k(fr, 6, 9)  # noqa: E731
    s.obj("Píldora", solid(RED), lambda fr, u: (538 - 140 * (1 - g(fr)), 1645, 462 * (0.4 + 0.6 * g(fr)), 138, tilt,
                                                1.0 if fr >= 6 else 0.0), radius=69, base=(462, 138))
    ink = (330, 1630, 746, 1662)
    s.say("FOUNDATIONS OF FASHION", ink, ANTON, 400, WHITE, "Título",
          geom=lambda fr, u: (*s.about(ink, 538, 1645, 1, tilt), 1, tilt, k(fr, 12, 6)))
    s.obj("Punto", solid(WHITE), lambda fr, u: (734, 1568, 78 * k(fr, 15, 6), 78 * k(fr, 15, 6), 0, 1), kind="ellipse",
          base=(78, 78))
    s.obj("Punto (rojo)", solid(RED), lambda fr, u: (734, 1568, 24 * k(fr, 18, 4), 24 * k(fr, 18, 4), 0, 1),
          kind="ellipse", base=(24, 24))
    s.say("Anna Martin", (152, 1763, 365, 1797), ANTON, 400, BLACK, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.say("SOCIAL BLOGGER, INFLUENCER", (152, 1806, 365, 1820), ANTON, 400, RED, "Texto 2",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 6)))
    s.yt("YouTube", lambda fr, u: (548, 1795, k(fr, 21, 6), 0, 1), w=52, h=34, red=RED)
    s.say("@annamartin", (799, 1790, 977, 1812), ANTON, 400, BLACK, "Texto 3", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    s.rect("Línea", solid(RED), lambda fr, u: (0, 1898, W * k(fr, 0, 15), 1912))
    return t


# --- 14. next / Watch: a photo pops, a strip beside «next» opens into a second photo, a red button, a thin ring ------
def next_watch():
    D = dur_for(1.4, 2.6)
    t = _p("siguiente", "Historia: dos fotos con next y Watch", "Story: two photos with next and Watch", 12713, D,
           ["foto", "siguiente"])
    s = T(t, D)
    bg(s, WHITE)
    photo(s, "fx-fashion-06", box=(0, 936, W, 1920), name="Foto 3", rect=lambda fr, u: (0, 936, W, 936 + 984 * k(fr, 0, 9)))
    s.rect("Línea", solid(RED), lambda fr, u: (0, 0, W * k(fr, 0, 9), 24))
    s.say("YOUTUBE", (917, 122, 1025, 142), ANTON, 400, BLACK, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 6, 6)))
    s.obj("Aro", ring("#F0C4C4", 3), lambda fr, u: (497, 552, 912, 912, -90 + 60 * k(fr, 0, 30), 1),
          path=arc(150, 450))
    s.obj("Punto", solid(RED), lambda fr, u: (53, 420, 20 * k(fr, 9, 4), 20 * k(fr, 9, 4), 0, 1), kind="ellipse",
          base=(20, 20))
    sc = lambda fr: 0.6 + 0.4 * k(fr, 0, 9)  # noqa: E731
    photo(s, "portrait-04", box=(137, 264, 547, 768), name="Foto", geom=lambda fr, u: (0, 0, sc(fr)),
          op=lambda fr, u: k(fr, 0, 3))
    photo(s, "fx-fashion-03", box=(586, 264, 994, 751), name="Foto 2",
          rect=lambda fr, u: (586 + 120 * (1 - k(fr, 3, 6)), 560 - 296 * k(fr, 12, 12), 994, 610 + 141 * k(fr, 12, 12)))
    s.obj("Botón", solid(RED), lambda fr, u: (974, 379, 106 * k(fr, 9, 6), 106 * k(fr, 9, 6), 0, 1), kind="ellipse",
          base=(106, 106))
    s.obj("Botón (punto)", solid(WHITE), lambda fr, u: (974, 379, 18 * k(fr, 12, 4), 18 * k(fr, 12, 4), 0, 1),
          kind="ellipse", base=(18, 18))
    s.say("next", (833, 792, 996, 871), ANTON, 400, BLACK, "Título", align="right", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 0, 4)))
    c = s.say("Watch", (137, 1044, 370, 1121), ANTON, 400, WHITE, "Título 2", align="left")
    s.letters(c, 9, stagger=0.05, duration=0.12, preset="fade")
    s.rect("Caja", solid("#C0000C", 0.85), lambda fr, u: (0, 1620, 384 * k(fr, 15, 9), 1831))
    s.say("+3", (240, 1708, 290, 1744), ANTON, 400, WHITE, "Texto 2", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 6)))
    return t


# --- 15. thank you: red words on white, two photos with names standing on their side, a red band ------------------
def thank_you():
    D = dur_for(1.4, 2.6)
    t = _p("gracias", "Historia: thank you con dos fotos y nombres", "Story: thank you with two photos and names", 12714,
           D, ["foto", "gracias"])
    s = T(t, D)
    bg(s, WHITE)
    c = s.say("thank you", (66, 104, 1014, 323), ANTONIO, 500, "#E3131B", reveal=lambda fr: (0, 0, W, 440))
    s.letters(c, 0, stagger=0.03, duration=0.25, distance=0.8)
    photo(s, "fx-man-03", box=(248, 384, 830, 972), name="Foto",
          rect=lambda fr, u: (248, 384, 248 + 582 * k(fr, 6, 12), 972))
    photo(s, "friends-01", box=(248, 1038, 830, 1628), name="Foto 2",
          rect=lambda fr, u: (830 - 582 * k(fr, 9, 12), 1038, 830, 1628))
    for i, (name, cx, cy, ln) in enumerate((("Sarah", 213, 503, 206), ("Duncan", 218, 1186, 250))):
        s.say(name, (cx - ln / 2, cy - 30, cx + ln / 2, cy + 30), ANTON, 400, "#E3131B", f"Texto {i + 1}",
              rot=lambda fr, u: -90, op=lambda fr, u, i=i: k(fr, 15 + 3 * i, 6))
    for i, (x, y) in enumerate(((243, 680), (830, 1336))):
        s.obj(f"Punto {i + 1}", solid("#F6F23A"), lambda fr, u, x=x, y=y, i=i: (x, y, 68 * k(fr, 18 + 3 * i, 6),
                                                                              68 * k(fr, 18 + 3 * i, 6), 0, 1),
              kind="ellipse", base=(68, 68))
        s.obj(f"Punto {i + 1} (centro)", solid(BLACK), lambda fr, u, x=x, y=y, i=i: (x, y, 16 * k(fr, 21 + 3 * i, 4),
                                                                                   16 * k(fr, 21 + 3 * i, 4), 0, 1),
              kind="ellipse", base=(16, 16))
    s.obj("Aro", ring("#CCCCCC", 2), lambda fr, u: (177, 1021, 122, 122, 0, k(fr, 15, 9)), kind="ellipse")
    s.say("2021", (156, 1014, 198, 1028), ANTON, 400, BLACK, "Texto 3", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.rect("Banda", solid(RED), lambda fr, u: (0, 1670 + 213 * (1 - k(fr, 3, 12)), W, 1883))
    s.say("YOUTUBE", (248, 1738, 352, 1762), ANTON, 400, WHITE, "Texto 4", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 12, 6)))
    s.rect("Línea", solid("#F6F23A"), lambda fr, u: (0, 1890, W * k(fr, 6, 12), 1912))
    return t


TWITTER = poly([(4, 78), (30, 82), (12, 66), (6, 50), (14, 50), (4, 32), (10, 14), (40, 34), (52, 16), (70, 10),
                (84, 16), (98, 10), (90, 24), (98, 26), (88, 34), (84, 56), (64, 82), (34, 94)])
FACEBOOK = poly([(38, 100), (38, 56), (22, 56), (22, 40), (38, 40), (38, 26), (46, 8), (70, 4), (78, 4), (78, 20),
                 (64, 20), (58, 26), (58, 40), (78, 40), (74, 56), (58, 56), (58, 100)])


# --- 16. Follow: big red word over the photo, a thin ring with an orbiting dot, a social card on stacked SUBSCRIBE --
def follow():
    D = dur_for(1.4, 2.6)
    t = _p("seguir", "Historia: Follow con tarjeta de redes", "Story: Follow with a social card", 12715, D,
           ["foto", "seguir", "redes", "suscribirse"])
    s = T(t, D)
    photo(s, "portrait-06", geom=lambda fr, u: (0, 0, 1.05 - 0.05 * k(fr, 0, 40)))
    s.say("Follow", (52, 40, 1004, 434), ANTONIO, 500, "#D9101A", geom=lambda fr, u: (0, -460 * (1 - k(fr, 6, 15)), 1, 0,
                                                                                       1))
    s.obj("Aro", ring("#555555", 2), lambda fr, u: (309, 812, 380 * k(fr, 6, 12), 380 * k(fr, 6, 12), 0, 1),
          kind="ellipse", base=(380, 380))
    s.obj("Punto", solid(BLACK), lambda fr, u: (*rot_pt(309, 622, -90 * k(u * FPS, 0, 90), 309, 812), 66 * k(fr, 9, 6),
                                                66 * k(fr, 9, 6), 0, 1), kind="ellipse", base=(66, 66))
    s.obj("Punto rojo", solid(RED), lambda fr, u: (858, 1130, 26 * k(fr, 15, 4), 26 * k(fr, 15, 4), 0, 1),
          kind="ellipse", base=(26, 26))
    s.rect("Bloque", solid(RED), lambda fr, u: (993 - 471 * k(fr, 9, 9), 1362, 993, 1814))
    for i in range(4):
        y0 = 1370 + 111 * i
        s.say("SUBSCRIBE", (530, y0, 985, y0 + 98), ANTON, 400, "#1A0A0A", f"Texto {i + 1}", align="right",
              editable=i == 3, reveal=lambda fr: (522, 1362, 993, 1814),
              shift=lambda fr, i=i: (480 * (1 - k(fr, 12 + 2 * i, 9)), 0))
    s.obj("Tarjeta", solid(WHITE), lambda fr, u: (696, 1534, 348 * k(fr, 18, 6), 343 * k(fr, 18, 6), 0, 1),
          base=(348, 343))
    for i, (glyph, colour, handle) in enumerate(((TWITTER, RED, "@annamartin"), (FACEBOOK, RED, "@anna_martin"),
                                                 (None, "#F06B8A", "@anna"))):
        y = 1446 + 86 * i
        at = 27 + 3 * i
        if glyph:
            s.obj(f"Icono {i + 1}", solid(colour), lambda fr, u, y=y, at=at: (568, y, 36, 34, 0, k(fr, at, 4)),
                  path=glyph)
        else:
            s.obj(f"Icono {i + 1}", ring(colour, 4), lambda fr, u, y=y, at=at: (568, y, 34, 34, 0, k(fr, at, 4)),
                  radius=10)
            s.obj(f"Icono {i + 1} (lente)", ring(colour, 4), lambda fr, u, y=y, at=at: (568, y, 14, 14, 0, k(fr, at, 4)),
                  kind="ellipse")
        s.say(handle, (626, y - 9, 800, y + 9), ANTON, 400, BLACK, f"Red {i + 1}", align="left",
              geom=lambda fr, u, at=at: (0, 0, 1, 0, k(fr, at + 2, 4)))
    s.rect("Línea", solid(RED), lambda fr, u: (0, 1906, W * k(fr, 0, 12), 1920))
    return t


TEMPLATES = [channel, welcome, human_rights, love, counter, alice_circle, my_plan, for_instance, vlogger, social_media, name_white, numbers, foundations, next_watch, thank_you, follow]
