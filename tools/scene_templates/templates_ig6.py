"""INSTAGRAM folder video as Stock templates (ig6-*). See docs/plan-instagram.md.

2656838.mp4 (1920×1080 at 29.97 fps), source seconds 140–210: the «update version 04» Christmas stories (five) and
twelve «swipe up» elements, and the «update version 05» six new stories. The Halloween stories (update 03) are
skipped (Stock is for the whole world), as are the update cards and the «Thanks for watching» / author end. Each
story was 486×864 px in the reference (three or two side by side), laid out here ×2.222 on 1080×1920; studied on
10 fps sheets (sheet index i = reference frame 3·i). Photos are slots. The swipe-up elements are transparent
overlays (no background of their own), drawn at about 2.4× their size in the reference near the bottom of the
story, looping like the original. Kit de Instagram; ids `ig6-*`, order 15800-. Notes in
tienda/plantillas/estudio-2656838/NOTAS-ig6.md.

Stories play their entrance, hold, and leave with the entrance backwards at 2.5× speed (S.frame).
"""

from __future__ import annotations

import math
import random

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of, mask_track
from scene import gradient, keys, no_stroke
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, poly, regular, ring
from templates_tk3 import blur_in, scatter

W, H = 1080, 1920
WHITE, BLACK = "#FFFFFF", "#111111"
KS, YT, BB, LG, M = "Kaushan Script", "Yellowtail", "Bebas Neue", "League Gothic", "Montserrat"
CK = "Cookie"
f6._FILES[(KS, 400)] = "fonts.basic/fonts/kaushanscript/KaushanScript-Regular.ttf"
f6._FILES[(CK, 400)] = "fonts.extra/fonts/cookie/Cookie-Regular.ttf"
f6._FILES[(YT, 400)] = "fonts.extra/fonts/yellowtail/Yellowtail-Regular.ttf"
f6._FILES[(BB, 400)] = "fonts.basic/fonts/bebasneue/BebasNeue-Regular.ttf"
f6._FILES[(LG, 400)] = "fonts.extra/fonts/leaguegothic/LeagueGothic-Regular.ttf"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"ig6-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.55, 1))


def dur_for(entrance_frames, hold=1.5):
    e = entrance_frames / FPS
    return round(e + hold + e / EXIT, 1)


def back(x):
    x = min(1.0, max(0.0, x))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def kb(fr, at, n):
    return back((fr - at) / max(1e-6, n))


def kout(fr, at, n):
    x = min(1.0, max(0.0, (fr - at) / max(1e-6, n)))
    return 1 - (1 - x) ** 3


def lerp(a, b, p):
    return a + (b - a) * p


class T(S):
    def __init__(self, t, dur, loop=False):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)
        if loop:  # overlays loop: no mirrored exit
            self.frame = lambda u: u * FPS


def argb(colour, alpha=1.0):
    return "#" + format(round(max(0.0, min(1.0, alpha)) * 255), "02x") + colour.lstrip("#")[-6:].lower()


def fillc(colour, alpha=1.0):
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "solid", "color": argb(colour, alpha)}}, no_stroke()]


def stroke(colour, width, cap="round", dash=None):
    s = ring(colour, width)
    s[1].update(cap=cap, join="round")
    if dash:
        s[1].update(dash="dash", dashPattern=dash)
    return s


def vgrad(c0, c1, a0=1.0, a1=1.0, angle=90):
    return [gradient([(0.0, c0, a0), (1.0, c1, a1)], angle=angle), no_stroke()]


def radial(c0, c1):
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": argb(c0),
                       "gradient": {"kind": "radial", "space": "block", "angle": 0,
                                    "stops": [{"pos": 0.0, "color": argb(c0)}, {"pos": 1.0, "color": argb(c1)}]}}},
            no_stroke()]


def backdrop(clip):
    clip["layoutRole"] = "backdrop"
    return clip


def bg(s, layers):
    return backdrop(s.rect("Fondo", layers, lambda fr, u: (-10, -10, W + 10, H + 10)))


def blur(s, clip, fn):
    return s.fx(clip, "builtin.effects.gaussian_blur", animated={"u_blurRadius": fn}, u_blurRadius=0.0)


# --- little drawings (paths on a 100 box) -----------------------------------------------------------------------

def star(n=5, inner=0.45, phase=-90.0):
    pts = []
    for i in range(2 * n):
        r = 50 if i % 2 == 0 else 50 * inner
        a = math.radians(phase + 180 * i / n)
        pts.append((50 + r * math.cos(a), 50 + r * math.sin(a)))
    return poly(pts)


def bars(segments, half):
    """Thick lines (x0, y0, x1, y1) in a 100 box as one path."""
    out = []
    for x0, y0, x1, y1 in segments:
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln * half, dx / ln * half
        out.append(poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]))
    return " ".join(out)


SNOW = bars([(50, 2, 50, 98), (8.4, 26, 91.6, 74), (8.4, 74, 91.6, 26)], 7.5)
BURST = star(9, 0.58)
STAR5 = star(5, 0.48)
CHEVRON = "M 0 70 L 50 20 L 100 70"
ZIGZAG = "M 8 34 L 22 22 L 36 34 L 50 22 L 64 34 L 78 22 L 92 34 M 4 56 L 18 44 L 32 56 L 46 44 L 60 56 L 74 44 " \
         "L 88 56 L 96 50 M 10 76 L 24 64 L 38 76 L 52 64 L 66 76 L 80 64 L 90 72"
CANE = "M 30 100 L 30 32 C 30 4, 80 4, 80 32 L 80 42"
HAND = poly([(30, 48), (30, 8), (33, 1), (41, 1), (44, 8), (44, 38), (47, 33), (53, 32), (57, 37), (57, 42), (60, 38),
             (66, 37), (70, 42), (70, 47), (73, 44), (79, 44), (83, 50), (83, 72), (79, 88), (71, 100), (37, 100),
             (28, 90), (15, 72), (7, 61), (9, 54), (16, 53), (24, 61), (30, 64)])


def pop(s, name, layers, cx, cy, w, h, at, n=9, path=None, kind="rectangle", rot=0.0):
    def g(fr, u):
        p = kb(fr, at, n)
        return cx, cy, w * max(0.0, p), h * max(0.0, p), rot - 40 * (1 - k(fr, at, n)), 1.0 if fr > at else 0.0
    return s.obj(name, layers, g, kind=kind, path=path, base=(w * 1.12, h * 1.12))


def ornament(s, name, cx, cy, d, colour, inner, kind, at, tilt=-25.0, rng=None):
    """A bauble: the ball, its cap and hook, and a zigzag (inner colour) or a star cut out."""
    def g(dx, dy, w, h, path=None):
        def f(fr, u):
            p = max(0.0, kb(fr, at, 9))
            a = math.radians(tilt)
            x, y = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
            return cx + x * p, cy + y * p, w * p, h * p, tilt, 1.0 if fr > at else 0.0
        return f
    s.obj(f"{name} (gancho)", stroke(colour, d * 0.03), g(0, -d * 0.62, d * 0.18, d * 0.2), path="M 50 100 L 50 0",
          base=(d * 0.2, d * 0.22))
    s.obj(f"{name} (tapa)", fillc(colour), g(0, -d * 0.5, d * 0.22, d * 0.12), base=(d * 0.24, d * 0.14))
    s.obj(name, fillc(colour), g(0, 0, d, d), kind="ellipse", base=(d * 1.1, d * 1.1))
    if kind == "zigzag":
        s.obj(f"{name} (dibujo)", stroke(inner, d * 0.035, cap="butt"), g(0, 0, d * 0.82, d * 0.82), path=ZIGZAG,
              base=(d * 0.9, d * 0.9))
    else:
        s.obj(f"{name} (estrella)", fillc(inner), g(0, d * 0.02, d * 0.42, d * 0.42), path=STAR5,
              base=(d * 0.46, d * 0.46))


def cane(s, name, cx, cy, h, rot, colour, at):
    def g(fr, u):
        p = max(0.0, kb(fr, at, 9))
        return cx, cy, h * 0.5 * p, h * p, rot, 1.0 if fr > at else 0.0
    return s.obj(name, stroke(colour, h * 0.075, cap="round", dash=[h * 0.05, h * 0.045]), g, path=CANE,
                 base=(h * 0.55, h * 1.05))


def scatter_decor(s, items, colour_w, colour_y, colour_in, start, rng_seed=3):
    """The snowflakes, bursts, baubles and canes around a Christmas title, popping in random order."""
    rng = random.Random(rng_seed)
    order = list(range(len(items)))
    rng.shuffle(order)
    for i, it in enumerate(items):
        at = start + order[i] * 1.2
        kind, cx, cy, size = it[:4]
        name = {"snow": "Copo", "burst": "Estrella", "ball": "Bola", "ballstar": "Bola", "gold": "Bola dorada",
                "goldstar": "Bola dorada", "cane": "Bastón"}[kind] + f" {i + 1}"
        if kind == "snow":
            pop(s, name, fillc(colour_w), cx, cy, size, size, at, path=SNOW)
        elif kind == "burst":
            pop(s, name, fillc(colour_y), cx, cy, size, size, at, path=BURST, rot=rng.uniform(0, 30))
        elif kind in ("ball", "gold"):
            ornament(s, name, cx, cy, size, colour_w if kind == "ball" else colour_y, colour_in, "zigzag", at,
                     tilt=it[4] if len(it) > 4 else -25)
        elif kind in ("ballstar", "goldstar"):
            ornament(s, name, cx, cy, size, colour_w, colour_in, "star", at, tilt=it[4] if len(it) > 4 else 30)
        else:
            cane(s, name, cx, cy, size, it[4], colour_w, at)


def letters(clip, at, stagger=0.06, dur=0.35, blur_px=10, dx=26.0, order="forward"):
    """Hand lettering written left to right: each letter fades in sharpening from the left."""
    blur_in(clip, at, stagger=stagger, dur=dur, dx=dx, blur=blur_px, order=order)
    return clip


# =================================================================================================================
# Christmas stories (update 04, source 172.2–181.5 s)
# =================================================================================================================

def merry_bright():
    D = dur_for(54, 2.0)
    t = _p("feliz-brillante", "Historia navideña: Merry & Bright en gris", "Christmas story: Merry & Bright on grey",
           15800, D, ["navidad", "christmas", "fiestas"])
    s = T(t, D)
    bg(s, vgrad("#7E7E7E", "#727272"))
    GREY_IN = "#777777"
    items = [("snow", 222, 112, 105), ("snow", 930, 240, 105), ("snow", 118, 552, 105), ("snow", 126, 1248, 105),
             ("snow", 962, 1388, 105), ("snow", 755, 1740, 100),
             ("burst", 472, 135, 120), ("burst", 508, 468, 125), ("burst", 915, 543, 120), ("burst", 116, 953, 120),
             ("burst", 932, 1148, 125), ("burst", 383, 1385, 120), ("burst", 935, 1608, 120),
             ("burst", 515, 1765, 110),
             ("ball", 280, 368, 135, -25), ("ball", 686, 1495, 135, 25),
             ("ballstar", 952, 880, 130, 50), ("ballstar", 205, 1795, 130, -30),
             ("cane", 718, 285, 270, 200), ("cane", 238, 1545, 230, -35)]
    scatter_decor(s, items, WHITE, "#FFC200", GREY_IN, 18)
    letters(s.say("Merry", (215, 600, 830, 880), CK, 400, WHITE, "Título"), 0, stagger=0.09)
    letters(s.say("&", (482, 880, 590, 1035), CK, 400, "#FFC200", "Y"), 9)
    letters(s.say("Bright", (250, 990, 815, 1235), CK, 400, WHITE, "Título 2"), 6, stagger=0.09)
    return t


def santa():
    D = dur_for(96, 1.6)
    t = _p("santa", "Historia navideña: cara de Papá Noel con Merry Xmas",
           "Christmas story: Santa face with Merry Xmas", 15801, D, ["navidad", "christmas", "papá noel"], thumb=4.0)
    s = T(t, D)
    bg(s, fillc("#FBFBFB"))
    SKIN, RED, ORANGE, PINK, GREY = "#F2CB9C", "#FF6142", "#F7A22B", "#F57A6C", "#DCD9D4"
    sc = lambda fr: 0.3 + 0.7 * kout(fr, 0, 27)  # noqa: E731
    PX, PY = 540, 1060

    def face(cx, cy, w, h, rot=0.0, op=None):
        def g(fr, u):
            z = sc(fr)
            return (PX + (cx - PX) * z, PY + (cy - PY) * z, w * z, h * z, rot,
                    min(1.0, fr / 6) * (op(fr) if op else 1.0))
        return g
    rng = random.Random(5)
    for i in range(26):  # the beard strokes
        x, y = rng.uniform(60, 1030), rng.uniform(1330, 1960)
        s.obj(f"Barba {i + 1}", fillc(GREY), (lambda x=x, y=y, r=rng.uniform(-25, 25), j=i: lambda fr, u: (
            x, y + 40 * (1 - kout(fr, 9 + j % 6, 18)), 18, 130, r, k(fr, 9 + j % 6, 12)))(), radius=9)
    s.obj("Cara", fillc(SKIN), face(540, 1030, 1050, 680), kind="ellipse")
    for side, x in (("izquierdo", 330), ("derecho", 750)):
        s.obj(f"Bigote {side}", [fillc(WHITE)[0], {"id": "stroke", "kind": "stroke", "enabled": True, "width": 8,
                                                  "strokeAlign": "inside", "opacity": 1.0,
                                                  "paint": {"kind": "solid", "color": argb(GREY)}}],
              face(x, 1190, 520, 210, -14 if x < 540 else 14), kind="ellipse")
    for side, x in (("izquierda", 305), ("derecha", 780)):
        s.obj(f"Lente {side}", fillc("#FFF4DD", 0.55), face(x, 1130, 205, 205), kind="ellipse")
        s.obj(f"Gafa {side}", ring(ORANGE, 17), face(x, 1130, 205, 205), kind="ellipse")
    s.obj("Puente", stroke(ORANGE, 14), face(540, 1100, 280, 40), path="M 0 100 C 30 0, 70 0, 100 100")
    s.obj("Nariz", fillc(PINK), face(540, 1060, 190, 180), kind="ellipse")
    s.obj("Nariz (brillo)", fillc(WHITE, 0.35), face(578, 1030, 70, 52), kind="ellipse")
    blink = lambda fr: 1.0 - 0.88 * (k(fr, 102, 2) - k(fr, 106, 3))  # noqa: E731
    for side, x in (("izquierdo", 285), ("derecho", 797)):
        s.obj(f"Ceja {side}", fillc(WHITE), face(x, 880, 140, 36, -4 if x < 540 else 4), radius=18)

        def eye(fr, u, x=x):
            g = face(x, 955, 62, 62)(fr, u)
            return g[0], g[1], g[2], g[3] * blink(fr), 0, g[5]
        s.obj(f"Ojo {side}", fillc(BLACK), eye, kind="ellipse", base=(70, 70))
        s.obj(f"Ojo {side} (brillo)", fillc(WHITE), face(x + 12, 942, 18, 18, op=lambda fr: 1 - k(fr, 101, 1)
                                                                                  + k(fr, 107, 1)), kind="ellipse")
    hat = s.rect("Gorro", fillc(RED), lambda fr, u: (-10, -10, W + 10, lerp(-10, 662, kout(fr, 6, 24))))
    blur(s, hat, lambda fr, u: 40 * (1 - k(fr, 15, 45)))
    s.rect("Piel del gorro", fillc(WHITE), lambda fr, u: (-10, 650, W + 10, 780),
           op=lambda fr, u: k(fr, 6, 15))
    s.rect("Piel del gorro (sombra)", fillc("#E2E2E2"), lambda fr, u: (-10, 776, W + 10, 800),
           op=lambda fr, u: k(fr, 6, 15))
    letters(s.say("Merry Xmas", (122, 150, 965, 390), KS, 400, WHITE, "Título"), 60, stagger=0.08)
    letters(s.say("& HAPPY NEW YEAR", (205, 435, 880, 510), BB, 400, WHITE, "Texto"), 62, stagger=0.05, blur_px=6)
    return t


def ribbon_tree():
    D = dur_for(100, 1.4)
    t = _p("arbol-cinta", "Historia navideña: árbol de cinta dorada", "Christmas story: golden ribbon tree", 15802, D,
           ["navidad", "christmas", "árbol"], thumb=4.2)
    s = T(t, D)
    GOLD = "#F2B31B"
    bg(s, radial("#C9301C", "#8C1A0E"))
    rng = random.Random(11)
    for i in range(22):  # soft red bokeh
        x, y, d = rng.uniform(40, 1040), rng.uniform(40, 1880), rng.uniform(40, 110)
        backdrop(s.obj(f"Destello {i + 1}", fillc("#E0432E", 0.35), lambda fr, u, x=x, y=y, d=d, j=i: (
            x, y - 20 * math.sin(u * 0.8 + j), d, d, 0, 0.7 + 0.3 * math.sin(u * 2 + j)), kind="ellipse"))
    # the ribbon: a zigzag spiral drawn from the bottom star upwards (the reference's spiral tree)
    pts = []
    for i in range(241):
        q = i / 240
        y = 1255 - 1010 * q
        amp = 410 * (1 - q) ** 0.9 + 12
        a = 2 * math.pi * 4.2 * q + math.pi * 1.1
        pts.append((540 + amp * math.cos(a), y + 30 * math.sin(a) * (1 - q)))
    pts[0] = (300, 1254)
    rib = s.outline("Cinta", pts, 26, GOLD, at=3, n=42, closed=False)
    rib["shapeStyle"]["layers"][1].update(cap="round", join="round")
    for i, (x, y, d) in enumerate(((300, 1254, 46), (150, 665, 34), (225, 650, 40), (195, 718, 44), (700, 565, 44),
                                   (765, 625, 52), (830, 1040, 40), (885, 1035, 32), (870, 1095, 52))):
        pop(s, f"Estrellita {i + 1}", fillc(GOLD), x, y, d, d, 12 + i * 3, path=STAR5)
    pop(s, "Estrella", fillc(GOLD), 540, 262, 120, 120, 63, n=9, path=STAR5)
    glow = s.obj("Estrella (luz)", radial("#FFD866", "#FFD86600"), lambda fr, u: (540, 262, 330, 330, 0,
                                                                                    0.8 * k(fr, 63, 6)), kind="ellipse")
    glow["shapeStyle"]["layers"][0]["paint"]["gradient"]["stops"][1]["color"] = "#00ffd866"
    for i in range(14):  # golden bokeh bursting from the star
        a = rng.uniform(0, 2 * math.pi)
        dist, d = rng.uniform(120, 520), rng.uniform(50, 120)
        s.obj(f"Brillo {i + 1}", fillc("#FFC21A", 0.9), lambda fr, u, a=a, dist=dist, d=d: (
            540 + math.cos(a) * dist * kout(fr, 66, 24), 262 + math.sin(a) * dist * kout(fr, 66, 24) * 1.3,
            d * k(fr, 66, 6), d * k(fr, 66, 6), 0, 1 - k(fr, 78, 21)), kind="ellipse", base=(d, d))
    letters(s.say("Merry", (300, 1295, 860, 1435), YT, 400, GOLD, "Título"), 30, stagger=0.08)
    letters(s.say("Christmas", (190, 1480, 885, 1640), YT, 400, GOLD, "Título 2"), 36, stagger=0.06)
    letters(s.say("and Happy New Year!", (245, 1728, 840, 1768), M, 500, GOLD, "Texto"), 45, stagger=0.03,
            blur_px=6)
    return t


def _gift(s, at=0):
    """The blue dotted gift box with its red ribbon and bow: it drops in, squashes, bounces and is still."""
    BLUE, RIB = "#1E62AE", "#F35A3F"

    def bounce(fr):
        y = lerp(-1300, 0, min(1.0, ((fr - at) / 14) ** 2)) if fr < at + 14 else 0.0
        y -= 70 * math.sin(math.pi * min(1.0, max(0.0, (fr - at - 14) / 8))) if fr > at + 14 else 0
        sq = 1.0 + (0.1 * math.sin(math.pi * min(1.0, max(0.0, (fr - at - 13) / 5))) if fr > at + 13 else 0)
        return y, sq

    def part(cx, cy, w, h):
        def g(fr, u):
            y, sq = bounce(fr)
            return 540 + (cx - 540) * sq, 1500 + (cy - 1500) / sq + y, w * sq, h / sq, 0, 1.0
        return g
    s.obj("Regalo", fillc(BLUE), part(540, 1040, 760, 760), radius=24, base=(800, 800))
    dots = " ".join(poly([(x + 2.2 * math.cos(a * math.pi / 4), y + 2.2 * math.sin(a * math.pi / 4)) for a in range(8)])
                    for x in range(7, 100, 11) for y in range(6, 100, 11))
    s.obj("Regalo (lunares)", fillc(WHITE), part(540, 1040, 760, 760), path=dots, base=(800, 800))
    s.obj("Tapa", fillc("#1A579C"), part(540, 690, 820, 120), radius=16, base=(860, 140))
    s.obj("Tapa (lunares)", fillc(WHITE), part(540, 690, 820, 120), path=dots, base=(860, 140))
    s.obj("Cinta", fillc(RIB), part(540, 1040, 110, 760), base=(120, 800))
    s.obj("Cinta 2", fillc(RIB), part(540, 900, 760, 100), base=(800, 110))
    s.obj("Cinta 3", fillc(RIB), part(540, 690, 120, 120), base=(130, 140))
    lazo = "M 50 100 C 20 70, 0 10, 25 5 C 45 0, 50 50, 50 100 Z M 50 100 C 80 70, 100 10, 75 5 C 55 0, 50 50, 50 100 Z"
    s.obj("Lazo", [fillc(RIB)[0], {"id": "stroke", "kind": "stroke", "enabled": True, "width": 20,
                                   "strokeAlign": "inside", "opacity": 1.0,
                                   "paint": {"kind": "solid", "color": argb("#C8402B")}}],
          part(540, 520, 420, 280), path=lazo, base=(440, 300))


def winter_sale():
    D = dur_for(75, 1.8)
    t = _p("rebajas-invierno", "Historia navideña: regalo que se abre en «winter sell XMAS 50%off»",
           "Christmas story: gift opening into «winter sell XMAS 50%off»", 15803, D,
           ["navidad", "christmas", "rebajas", "descuento"], thumb=3.6)
    s = T(t, D)
    bg(s, vgrad("#BAB29E", "#A39A83"))
    GOLD, IN = "#F7CE5B", "#ABA28C"
    gift_start = len(s.t.tracks)
    _gift(s)
    for track in s.t.tracks[gift_start:]:  # the gift leaves at the burst
        for c in track.clips:
            c["opacity"] = keys([(u, round(1 - k(fr, 30, 4), 4), "linear") for u, fr in s.each()])
    s.obj("Estallido", fillc("#C9C0A8"), lambda fr, u: (540, 1000, 1400 * kout(fr, 28, 10), 1400 * kout(fr, 28, 10),
                                                         10, 1 - k(fr, 36, 9)), path=star(8, 0.55), base=(1400, 1400))
    rng = random.Random(4)
    for i in range(26):  # confetti flying out of the burst
        a = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(250, 760)
        col = rng.choice(("#3A9BE8", "#3A9BE8", "#F05A3A", "#E9B4F0", "#F7CE5B"))
        d = rng.uniform(40, 110) if col == "#3A9BE8" else rng.uniform(16, 30)
        s.obj(f"Confeti {i + 1}", fillc(col), lambda fr, u, a=a, dist=dist, d=d: (
            540 + math.cos(a) * dist * kout(fr, 30, 24), 1000 + math.sin(a) * dist * kout(fr, 30, 24) + 300 * k(fr, 42, 30),
            d, d if d > 35 else d * 2.2, math.degrees(a), 1.0 if 30 < fr < 66 else 0.0), kind="ellipse" if d > 35 else
              "rectangle", base=(d, d * 2.2))
    items = [("snow", 230, 145, 70), ("snow", 905, 120, 75), ("snow", 112, 352, 75), ("snow", 645, 352, 75),
             ("snow", 115, 1580, 75), ("snow", 640, 1622, 75), ("snow", 890, 1820, 75),
             ("gold", 330, 372, 120, -25), ("gold", 872, 1572, 120, 25),
             ("ballstar", 905, 340, 120, 60), ("ballstar", 460, 1780, 115, -30),
             ("cane", 535, 110, 210, 200), ("cane", 225, 1720, 230, 215)]
    scatter_decor(s, items, WHITE, GOLD, IN, 36)
    letters(s.say("winter sell", (178, 540, 1000, 700), CK, 400, WHITE, "Título"), 30, stagger=0.05)
    letters(s.say("XMAS", (195, 730, 1000, 1040), CK, 400, GOLD, "Título 2"), 33, stagger=0.06)
    letters(s.say("50%off", (180, 1075, 1000, 1395), CK, 400, WHITE, "Descuento"), 36, stagger=0.06)
    return t


def pine_path(n=16, length=100.0):
    """A pine sprig along the x axis of a 100×50 box: the stem and pairs of needles that shorten to the tip."""
    segs = [(0, 50, 100, 50)]
    for i in range(n):
        x = 3 + i * 95 / n
        ln = 46 * (1 - i / (n + 4))
        for sgn in (-1, 1):
            segs.append((x, 50, x + ln * 0.45, 50 + sgn * ln))
    return bars(segs, 2.2)


def pine_red():
    D = dur_for(54, 2.0)
    t = _p("pino-rojo", "Historia navideña: ramas de pino y Merry Christmas en rojo",
           "Christmas story: pine branches and Merry Christmas on red", 15804, D,
           ["navidad", "christmas", "rebajas", "pino"], thumb=3.2)
    s = T(t, D)
    YEL = "#FFC51C"
    bg(s, radial("#F0421E", "#8E1A0F"))
    sprig = pine_path()
    # (anchor x, y, angle, length, colour, start frame): sprigs grow from the corners
    sprigs = [(-20, 40, 35, 520, "#2E7A1E", 0), (60, -30, 70, 420, "#2A6E1B", 3), (-30, 300, 10, 360, "#357F22", 6),
              (1100, 20, 150, 520, "#2E7A1E", 2), (980, -30, 112, 420, "#2A6E1B", 5), (1110, 260, 175, 360, "#357F22", 8),
              (-30, 1900, -35, 520, "#2E7A1E", 4), (140, 1960, -75, 420, "#2A6E1B", 7), (-30, 1640, -12, 360, "#357F22", 10),
              (1110, 1890, -145, 520, "#2E7A1E", 6), (940, 1960, -105, 420, "#2A6E1B", 9), (1110, 1620, -168, 360,
                                                                                            "#357F22", 12)]
    for i, (ax, ay, ang, ln, col, at) in enumerate(sprigs):
        a = math.radians(ang)

        def g(fr, u, ax=ax, ay=ay, a=a, ln=ln, at=at):
            p = kout(fr, at, 24)
            sway = 2.0 * math.sin(u * 1.6 + ax)
            L = ln * p
            return ax + math.cos(a) * L / 2, ay + math.sin(a) * L / 2, L, ln * 0.5 * p, math.degrees(a) + sway, 1.0
        s.obj(f"Rama {i + 1}", fillc(col), g, path=sprig, base=(ln, ln * 0.5))
    for i, (x, y, d, c0, c1) in enumerate(((128, 268, 145, "#F2B12C", "#9C5A0C"), (790, 118, 125, "#3876D8", "#123C8C"),
                                           (968, 186, 150, "#F2B12C", "#9C5A0C"))):
        s.obj(f"Bola {i + 1} (hilo)", fillc("#D9A43A"), lambda fr, u, x=x, y=y, d=d: (
            x, y - d * 0.7 - 400 * (1 - kout(fr, 12 + i * 3, 21)), 4, d * 0.5, 0, 1.0))
        s.obj(f"Bola {i + 1}", radial(c0, c1), lambda fr, u, x=x, y=y, d=d, j=i: (
            x + 6 * math.sin(u * 2 + j), y - 400 * (1 - kout(fr, 12 + j * 3, 21)), d, d, 0, 1.0), kind="ellipse")
    letters(s.say("Merry", (215, 690, 870, 875), YT, 400, YEL, "Título"), 21, stagger=0.08)
    letters(s.say("Christmas", (215, 880, 870, 1060), YT, 400, YEL, "Título 2"), 27, stagger=0.06)
    letters(s.say("WINTER SELL 40% OFF", (218, 1148, 868, 1188), M, 600, YEL, "Texto"), 39, stagger=0.03, blur_px=6)
    return t


# =================================================================================================================
# Swipe-up elements (source 181.5–187.4 s): transparent overlays that loop
# =================================================================================================================

SX, SY, Z = 540, 1640, 2.4  # where an element sits on the story, and its size against the reference


def cyc(fr, period):
    return fr % period


def _sw(id, es, en, order, tags=(), dur=5.0):
    t = _p(id, es, en, order, dur, ["swipe up", "desliza", "flecha", "superposición", "elemento"] + list(tags),
           thumb=round(dur * 0.4, 1))
    return t, T(t, dur, loop=True)


def sw_glow():
    Z = 2.4 * 1.2  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-brillo", "Swipe up: flechas blancas con brillo que suben", "Swipe up: glowing white arrows rising",
               15820)
    P = 33
    for j in range(3):
        def g(fr, u, j=j):
            c = cyc(fr, P)
            rise = c / 24
            op = (1 - k(c, 14, 10)) * k(c, 0, 4) * (1.0, 0.65, 0.4)[j]
            return SX, SY + 60 * Z - 120 * Z * kout(c, 0, 24) + j * 24 * Z * (1 - 0.3 * rise), 98 * Z, 54 * Z, 0, op
        s.obj(f"Flecha {j + 1}", vgrad(WHITE, WHITE, 1.0, 0.0), g, path=poly([(50, 0), (100, 100), (0, 100)]),
              base=(98 * Z, 54 * Z))
    return t


def sw_toggle():
    t, s = _sw("swipe-interruptor", "Swipe up: interruptor con bola azul que sube",
               "Swipe up: toggle with a blue knob that slides up", 15821)
    P = 51
    BLUE = "#13A9F2"
    pw, ph = 45 * Z, 115 * Z
    top, bot = SY - ph / 2 + pw / 2, SY + ph / 2 - pw / 2
    knob_y = lambda fr: lerp(bot, top, kout(cyc(fr, P), 0, 12))  # noqa: E731
    s.obj("Rastro", vgrad(BLUE, BLUE, 0.0, 0.7), lambda fr, u: (
        SX, (knob_y(fr) + bot) / 2 + pw * 0.2, pw * 0.8, max(1.0, bot - knob_y(fr)), 0,
        1 - k(cyc(fr, P), 12, 12)), radius=pw * 0.4, base=(pw, ph))
    s.obj("Interruptor", ring(WHITE, 4.5 * Z), lambda fr, u: (SX, SY, pw, ph, 0, 1.0), radius=pw / 2)
    s.obj("Bola", fillc(BLUE), lambda fr, u: (SX, knob_y(fr), pw * 0.8, pw * 0.8, 0, 1.0), kind="ellipse")
    s.obj("Bola (flecha)", stroke(BLACK, 2.2 * Z), lambda fr, u: (SX, knob_y(fr), pw * 0.36, pw * 0.42, 0, 1.0),
          path="M 50 100 L 50 4 M 14 40 L 50 4 L 86 40")
    return t


def _letter_xs(word, family, size, cx):
    f = f6._font(family, 400, size)
    widths = [f.getlength(ch) for ch in word]
    total = sum(widths)
    x, out = cx - total / 2, []
    for w in widths:
        out.append((x, x + w))
        x += w
    return out


def sw_letters():
    Z = 2.4 * 2.0  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-letras", "Swipe up: letras SWIPE UP que saltan", "Swipe up: jumping SWIPE UP letters", 15822,
               ["texto"], dur=6.0)
    P = 90
    word = "SWIPEUP"
    cap = 30 * Z
    xs = _letter_xs(word, BB, 400, SX)
    scale = cap / (f6._font(BB, 400, 400).getbbox("H")[3] - f6._font(BB, 400, 400).getbbox("H")[1])
    rng = random.Random(9)
    offs = [[rng.uniform(-22, 22) * Z for _ in word] for _ in range(4)]
    for i, ch in enumerate(word):
        x0, x1 = xs[i]
        cx = SX + ((x0 + x1) / 2 - SX) * scale
        w = (x1 - x0) * scale
        gap = 6 * Z if i >= 5 else 0

        def g(fr, u, i=i):
            c, n = cyc(fr, P), int(fr // P)
            settle = kout(c, 6 + i, 30)
            jump = offs[n % 4][i] * (1 - settle) + offs[(n + 1) % 4][i] * k(c, 66, 16)
            return gap, jump, 1.0, 0.0, k(c, i * 2, 6) if n == 0 else 1.0
        s.say(ch, (cx - w / 2, SY - cap / 2, cx + w / 2, SY + cap / 2), BB, 400, WHITE, f"Letra {i + 1}", geom=g)
    for j in range(5):  # the little red bars that bounce while the letters move
        h0 = (6, 12, 18, 10, 7)[j] * Z

        def bar(fr, u, j=j, h0=h0):
            c = cyc(fr, P)
            on = 1 - k(c, 30, 9) + k(c, 66, 6)
            h = h0 * (0.5 + 0.5 * abs(math.sin(fr * 0.5 + j)))
            return SX - 16 * Z + j * 8 * Z, SY - cap / 2 - 18 * Z - h / 2, 4 * Z, h, 0, min(1.0, on)
        s.obj(f"Barra {j + 1}", fillc("#E8221A"), bar, base=(5 * Z, 20 * Z))
    return t


def sw_flag():
    Z = 2.4 * 1.2  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-bandera", "Swipe up: bandera SWIPE UP que sale de un cañón de confeti",
               "Swipe up: SWIPE UP flag popping out of a party popper", 15823, ["bandera"], dur=6.0)
    P = 90
    RED = "#F2401E"
    bx, by = SX - 30 * Z, SY + 20 * Z  # the popper's mouth (the stick's foot)

    def pose(fr):
        c = cyc(fr, P)
        rise = kb(c, 12, 6)
        tip = k(c, 54, 9)
        fall = k(c, 60, 18)
        rot = -60 * tip - 60 * fall + 4 * math.sin(c * 0.6) * (1 - tip)
        return rise, rot, (-110 * fall * Z, 160 * fall * Z), 1.0 if 12 < c < 76 else 0.0

    def on_stick(dx, dy, w, h):
        def g(fr, u):
            rise, rot, (ox, oy), op = pose(fr)
            a = math.radians(rot)
            px, py = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
            return bx + ox + px, by + oy + py - 0 * rise, w * max(0.0, rise), h * max(0.0, rise), rot, op
        return g
    s.obj("Cañón", vgrad("#F7C531", "#E0702A"), lambda fr, u: (bx, by + 40 * Z, 38 * Z, 60 * Z, 0, 1.0),
          path=poly([(0, 0), (100, 0), (62, 100), (38, 100)]))
    s.obj("Cañón (raya)", fillc("#7B4BD8"), lambda fr, u: (bx, by + 30 * Z, 30 * Z, 8 * Z, 0, 1.0))
    s.obj("Palo", fillc(WHITE), on_stick(0, -40 * Z, 2.2 * Z, 80 * Z), base=(3 * Z, 82 * Z))
    flag = poly([(0, 0), (100, 0), (88, 50), (100, 100), (0, 100)])
    s.obj("Bandera", fillc(RED), on_stick(52 * Z, -62 * Z, 104 * Z, 38 * Z), path=flag, base=(106 * Z, 40 * Z))
    ink = (bx + 4 * Z, by - 72 * Z, bx + 92 * Z, by - 52 * Z)
    c = s.say("SWIPE UP", ink, BB, 400, WHITE, "Texto")

    def tg(fr, u):
        rise, rot, (ox, oy), op = pose(fr)
        a = math.radians(rot)
        dx, dy = 48 * Z, -62 * Z
        px, py = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
        cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
        return bx + ox + px - cx, by + oy + py - cy, max(0.01, rise), rot, op
    s.tmove(c, tg)
    rng = random.Random(2)
    for i in range(7):  # sparks at the pop
        a = math.radians(rng.uniform(180, 300))
        d = rng.uniform(25, 50) * Z
        s.obj(f"Chispa {i + 1}", fillc("#F2B21B"), lambda fr, u, a=a, d=d: (
            bx + math.cos(a) * d * kout(cyc(fr, P), 12, 12), by - 10 * Z + math.sin(a) * d * kout(cyc(fr, P), 12, 12),
            7 * Z, 2.5 * Z, math.degrees(a), 1.0 if 12 < cyc(fr, P) < 40 else 0.0))
    return t


def sw_hand():
    t, s = _sw("swipe-mano", "Swipe up: mano que desliza hacia arriba con chevrones",
               "Swipe up: hand swiping up with a chevron trail", 15824, ["mano"])
    P = 42
    BLUE = "#2563E0"

    def hand_pose(fr):
        c = cyc(fr, P)
        p = kout(c, 15, 9)
        back_ = k(c, 36, 6)
        y = SY + 20 * Z - 70 * Z * p + 70 * Z * back_ * p
        rot = 32 * (1 - p) + 32 * back_
        return SX + 20 * Z * (1 - p), y, rot
    for j in range(7):
        def chev(fr, u, j=j):
            c = cyc(fr, P)
            x, y, rot = hand_pose(fr)
            vis = k(c, 15 + j * 0.6, 2) * (1 - k(c, 24 + j * 0.8, 4))
            return x - 34 * Z, y - 40 * Z + j * 20 * Z, 30 * Z, 14 * Z, 0, vis * (1 - j / 9)
        s.obj(f"Chevrón {j + 1}", stroke(BLUE, 3 * Z), chev, path=CHEVRON, base=(31 * Z, 15 * Z))
    s.obj("Mano", [fillc(WHITE)[0], {"id": "stroke", "kind": "stroke", "enabled": True, "width": 1.2 * Z,
                                     "strokeAlign": "inside", "opacity": 1.0,
                                     "paint": {"kind": "solid", "color": argb("#9A9A9A")}}],
          lambda fr, u: (*hand_pose(fr)[:2], 100 * Z, 118 * Z, hand_pose(fr)[2], 1.0), path=HAND)
    return t


def sw_circle():
    Z = 2.4 * 2.3  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-circulo", "Swipe up: círculo blanco con triángulo que sube y se desenfoca",
               "Swipe up: white circle with a triangle that rises and blurs", 15825)
    P = 36

    def g(fr, u, sz):
        c = cyc(fr, P)
        y = SY + 20 * Z - 40 * Z * kout(c, 3, 15)
        return SX, y, sz, sz, 0, k(c, 0, 4) * (1 - k(c, 21, 12))
    a = s.obj("Círculo", fillc(WHITE), lambda fr, u: g(fr, u, 34 * Z), kind="ellipse")
    b = s.obj("Triángulo", fillc(BLACK), lambda fr, u: (lambda v: (v[0], v[1] - 1 * Z, 14 * Z, 12 * Z, 0, v[5]))(
        g(fr, u, 0)), path=poly([(50, 0), (100, 100), (0, 100)]))
    for c in (a, b):
        blur(s, c, lambda fr, u: 2 + 26 * k(cyc(fr, P), 18, 12) + 26 * (1 - k(cyc(fr, P), 0, 9)))
    return t


def sw_box():
    Z = 2.4 * 2.85  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-cuadro", "Swipe up: cuadro turquesa con flecha y reflejo", "Swipe up: teal box with an arrow "
               "and its reflection", 15826)
    P = 48
    TEAL = "#0E8B8B"

    def g(fr, u, dy=0.0, alpha=1.0, flip=1):
        c = cyc(fr, P)
        y = SY + 25 * Z - 50 * Z * kout(c, 0, 24)
        return SX, y + dy, 28 * Z, 28 * Z * flip, 0, alpha * k(c, 0, 6) * (1 - k(c, 18, 8))
    s.obj("Reflejo", vgrad(TEAL, TEAL, 0.45, 0.0), lambda fr, u: g(fr, u, 23 * Z, 1.0, 0.65))
    s.obj("Cuadro", fillc(TEAL), lambda fr, u: g(fr, u))
    s.obj("Flecha", fillc("#0A0A0A"), lambda fr, u: (lambda v: (v[0], v[1], 18 * Z, 7 * Z, 0, v[5]))(g(fr, u)),
          path=poly([(0, 100), (50, 0), (100, 100), (50, 70)]))
    return t


def sw_morph():
    Z = 2.4 * 2.5  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-figuras", "Swipe up: aro verde que se vuelve triángulo con SWIPE UP",
               "Swipe up: green ring turning into a triangle with SWIPE UP", 15827, ["texto"])
    P = 51
    GREEN = "#19C68E"
    seq = [("Aro", None, 0, 6), ("Hexágono", regular(6), 6, 9), ("Pentágono", regular(5), 9, 12),
           ("Cuadro", regular(4), 12, 15), ("Triángulo", regular(3), 15, 30)]

    def drift(c):
        return SY - 30 * Z * kout(c, 0, 30)
    for name, path, a, b in seq:
        def g(fr, u, a=a, b=b, last=(b == 30)):
            c = cyc(fr, P)
            on = 1.0 if a <= c < b else 0.0
            if last:
                on = (1.0 if c >= a else 0.0) * (1 - k(c, 27, 6))
            return SX, drift(c) - 10 * Z, 34 * Z, 32 * Z, (c - a) * 25 if not last else 15 * (1 - k(c, 15, 3)), on
        s.obj(f"Figura: {name}", ring(GREEN, 6 * Z), g, kind="ellipse" if path is None else "rectangle", path=path,
              base=(36 * Z, 34 * Z))
    ink = (SX - 32 * Z, SY + 14 * Z, SX + 32 * Z, SY + 21 * Z)
    c = s.say("SWIPE UP", ink, M, 800, WHITE, "Texto",
              geom=lambda fr, u: (0, drift(cyc(fr, P)) - SY, 1.0, 0.0, k(cyc(fr, P), 6, 9) * (1 - k(cyc(fr, P), 27, 6))))
    return t


def sw_chevrons():
    Z = 2.4 * 2.75  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-chevrones", "Swipe up: tres chevrones azules que suben", "Swipe up: three blue chevrons rising",
               15828)
    P = 45
    for j in range(3):
        def g(fr, u, j=j):
            c = cyc(fr, P)
            y = SY + 30 * Z - 45 * Z * kout(c, 0, 24) + (j - 1) * 15 * Z
            op = k(c, 0, 6) * (1 - k(c, 15 + 2 * (2 - j), 9)) * (1.0 if j == 0 else (0.85 if j == 1 else 0.7))
            return SX, y, 26 * Z, 13 * Z, 0, op
        s.obj(f"Chevrón {j + 1}", stroke("#1E5BFF", 3.2 * Z), g, path=CHEVRON, base=(28 * Z, 15 * Z))
    return t


def sw_button():
    Z = 2.4 * 2.5  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-boton", "Swipe up: botón blanco que pasa de cuadro a círculo",
               "Swipe up: white button morphing from square to circle", 15829)
    P = 39

    def roundness(fr):
        c = cyc(fr, P)
        return k(c, 12, 6) * (1 - k(c, 33, 6))
    s.obj("Botón (cuadro)", fillc(WHITE), lambda fr, u: (SX, SY, 34 * Z, 34 * Z, 0, 1 - roundness(fr)), radius=6 * Z)
    s.obj("Botón (círculo)", fillc(WHITE), lambda fr, u: (SX, SY, 34 * Z, 34 * Z, 0, roundness(fr)), kind="ellipse")
    s.obj("Chevrón", stroke(BLACK, 2.6 * Z), lambda fr, u: (SX, SY - 6 * Z, 20 * Z, 9 * Z, 0, 1.0), path=CHEVRON)
    s.obj("Chevrón 2", stroke("#4A4A4A", 2.6 * Z), lambda fr, u: (SX, SY + 5 * Z, 20 * Z, 9 * Z, 0, 1.0),
          path=CHEVRON)
    s.obj("Chevrón 2 (gris)", stroke("#8A8A8A", 2.6 * Z), lambda fr, u: (SX, SY + 5 * Z, 20 * Z, 9 * Z, 0,
                                                                        roundness(fr)), path=CHEVRON)
    return t


def sw_arrow():
    Z = 2.4 * 2.55  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-flecha", "Swipe up: flecha azul sobre una línea que late", "Swipe up: blue arrow over a "
               "pulsing line", 15830)
    P = 45

    def lift(fr):
        return 0.5 - 0.5 * math.cos(2 * math.pi * cyc(fr, P) / P)
    s.obj("Flecha", stroke("#1FB0E6", 2.6 * Z), lambda fr, u: (SX, SY - 4 * Z - 10 * Z * lift(fr), 18 * Z, 30 * Z,
                                                                0, 1.0), path="M 50 100 L 50 3 M 8 40 L 50 3 L 92 40")
    s.obj("Bulto", fillc(WHITE), lambda fr, u: (SX, SY + 18 * Z, 12 * Z, 7 * Z * (1 - lift(fr)), 0, 1.0),
          kind="ellipse")
    s.obj("Línea", fillc(WHITE), lambda fr, u: (SX, SY + 19 * Z, 22 * Z, 2.2 * Z, 0, 1.0), radius=1.1 * Z)
    return t


def sw_triangle():
    Z = 2.4 * 2.5  # this element's size in the reference against the measured unit
    t, s = _sw("swipe-triangulo", "Swipe up: triángulo blanco con punto rojo que sube",
               "Swipe up: white triangle with a red dot rising", 15831)
    P = 39
    TRI = poly([(50, 0), (100, 100), (0, 100)])

    def dot_y(fr, lag=0.0):
        c = cyc(fr - lag, P)
        return SY + 8 * Z - 16 * Z * (k(c, 0, 12) - k(c, 18, 12))
    s.obj("Triángulo", fillc(WHITE), lambda fr, u: (SX, SY - 1.5 * Z * math.sin(fr / P * 2 * math.pi), 36 * Z, 31 * Z,
                                                     0, 1.0), path=TRI)
    for j, a in ((2, 0.25), (1, 0.45), (0, 1.0)):
        s.obj(f"Punto{' (rastro ' + str(j) + ')' if j else ''}", fillc("#F04A3A", a),
              lambda fr, u, j=j: (SX, dot_y(fr, j * 1.5), 11 * Z, 11 * Z, 0, 1.0), kind="ellipse")
    return t


# =================================================================================================================
# Six new stories (update 05, source 189.7–198.5 s)
# =================================================================================================================

def win_photo(s, sample, box, rect, zoom=lambda fr: 1.0, label="Foto", name="Foto", track=None, shift=None):
    """A photo slot laid out in box = (x0, y0, x1, y1), seen through rect(fr) (screen px), zoomed by zoom(fr) and
    moved by shift(fr) = (dx, dy)."""
    t = s.t
    x0, y0, x1, y1 = box
    b = Box(x0, y0, x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    motion = []
    for u, fr in s.each():
        dx, dy = shift(fr) if shift else (0.0, 0.0)
        motion.append((u, {"s": zoom(fr), "dx": dx, "dy": dy}, "linear"))
    clip = t.photo(track or t.track("video", name), sample, 0.0, s.dur, b, motion, label=label)
    clip["name"] = name

    def r(u):
        fr = s.frame(u)
        q = rect(fr)
        if q[2] - q[0] < 0.5 or q[3] - q[1] < 0.5:
            return (-4000.0, -4000.0, -3999.0, -3999.0)
        z = zoom(fr)
        dx, dy = shift(fr) if shift else (0.0, 0.0)
        return tuple(c0 + (v - c0 - d) / z for v, c0, d in ((q[0], cx, dx), (q[1], cy, dy), (q[2], cx, dx),
                                                             (q[3], cy, dy)))
    mask_track(t, clip, b, r, s.dur)
    return clip


def say_in(s, content, ink, weight, colour, name, at, how="scatter", align="left", family=M, **kw):
    c = s.say(content, ink, family, weight, colour, name, align=align)
    if how == "scatter":
        scatter(c, at, stagger=kw.get("stagger", 0.035), dur=0.3, amp=0, blur=8, seed=kw.get("seed", 7))
    else:
        blur_in(c, at, stagger=kw.get("stagger", 0.05), dur=0.35, dx=kw.get("dx", 30), blur=kw.get("blur", 10))
    return c


def swipe_button(s, at, colour="#0050E6"):
    """The little white swipe-up square at the foot of a story, bobbing."""
    g = lambda fr, u: (540, 1830 - 10 * abs(math.sin(u * 3)), 100, 100, 0, k(fr, at, 6))  # noqa: E731
    s.obj("Botón", fillc(WHITE), g)
    s.obj("Botón (flecha)", fillc(colour), lambda fr, u: (lambda v: (v[0], v[1] + 2, 52, 22, 0, v[5]))(g(fr, u)),
          path=poly([(0, 100), (50, 0), (100, 100), (50, 72)]))


def artist():
    D = dur_for(78, 1.6)
    t = _p("artista", "Historia: You are the artist of your life con #YLIFE", "Story: You are the artist of your "
           "life with #YLIFE", 15840, D, ["foto", "azul", "estilo de vida"], thumb=3.6)
    s = T(t, D)
    BLUE, ORANGE = "#0050E6", "#FF571E"
    bg(s, fillc(WHITE))

    def circ(fr, u):
        p = kout(fr, 0, 33)
        cy, r = lerp(260, 1991, p), lerp(640, 991, p)
        return 540, cy, 2 * r, 2 * r, 0, 1.0
    s.obj("Círculo", fillc(BLUE), circ, kind="ellipse", base=(1982, 1982))
    win_photo(s, "fx-man-04", (180, 312, 906, 1606),
              lambda fr: (lerp(118, 180, kout(fr, 0, 30)), lerp(268, 312, kout(fr, 0, 30)),
                          lerp(938, 906, kout(fr, 0, 30)), lerp(700, 1606, kout(fr, 0, 36))),
              zoom=lambda fr: 1.25 - 0.25 * kout(fr, 0, 45))
    say_in(s, "YOU ARE THE ARTIST", (188, 143, 712, 170), 700, BLACK, "Texto", 36, seed=3)
    say_in(s, "OF YOUR LIFE", (188, 200, 552, 227), 700, BLACK, "Texto 2", 40, seed=5)
    s.rect("Caja", fillc(ORANGE), lambda fr, u: (126, 1132, lerp(126, 696, kout(fr, 36, 12)), 1344),
           op=lambda fr, u: 1.0 if fr > 36 else 0.0)
    c = s.say("#YLIFE", (188, 1196, 630, 1283), M, 800, WHITE, "Título",
              reveal=lambda fr: (126, 1132, 696, 1344), shift=lambda fr: (220 * (1 - kout(fr, 42, 18)), 0))
    s.fade(c, lambda fr: k(fr, 42, 6))
    say_in(s, "2020", (426, 1376, 686, 1442), 700, WHITE, "Año", 48, how="blur", dx=0, stagger=0.08)
    swipe_button(s, 75, BLUE)
    return t


def cozy_light():
    D = dur_for(80, 1.6)
    t = _p("luz-calida", "Historia: Cozy Light con rombos y #WARM", "Story: Cozy Light with diamonds and #WARM", 15841,
           D, ["foto", "hogar", "producto", "rombo"], thumb=3.6)
    s = T(t, D)
    DIAMOND = poly([(50, 0), (100, 50), (50, 100), (0, 50)])
    bg(s, fillc(WHITE))
    s.obj("Rombo amarillo", fillc("#F0BB2B"), lambda fr, u: (
        lerp(540, 1095, kout(fr, 18, 24)), lerp(967, 560, kout(fr, 18, 24)), lerp(1000, 560, kout(fr, 18, 24)),
        lerp(1000, 560, kout(fr, 18, 24)), 0, 1.0 if fr > 16 else 0.0), path=DIAMOND, base=(1000, 1000))
    win_photo(s, "ig3-lamp-03", (112, 530, 972, 1390),
              lambda fr: (112, 530, 972, 1390) if fr > 24 else (0, 0, 0, 0),
              zoom=lambda fr: 1.0)
    photo_track = s.t.tracks[-1]
    pc = photo_track.clips[0]
    keys_ = [(u, {"s": lerp(0.55, 1.0, kout(fr, 24, 21)), "dx": lerp(80, 0, kout(fr, 24, 21)),
                  "dy": lerp(-260, 0, kout(fr, 24, 21))}) for u, fr in s.each()]
    from scene import layout as _layout
    lay = _layout(Box(112, 530, 860, 860), [(u, v, "linear") for u, v in keys_])
    pc.update({kk: lay[kk] for kk in ("x", "y", "width", "height")})
    pc["rotation"] = keys([(u, round(-14 * (1 - kout(fr, 24, 21)), 3), "linear") for u, fr in s.each()])
    s.obj("Rombo azul", fillc("#4A97B6"), lambda fr, u: (
        lerp(540, 0, kout(fr, 15, 27)), lerp(967, 1520, kout(fr, 15, 27)), lerp(1000, 740, kout(fr, 15, 27)),
        lerp(1000, 740, kout(fr, 15, 27)), 0, 1.0), path=DIAMOND, base=(1000, 1000))
    say_in(s, "COZY LIGHT", (226, 232, 856, 305), 600, BLACK, "Título", 33, align="center", stagger=0.05)
    s.rect("Caja", fillc("#000000"), lambda fr, u: (lerp(395, 290, kout(fr, 57, 6)),
                                                     1600 - lerp(4, 100, kout(fr, 60, 8)),
                                                     lerp(685, 790, kout(fr, 57, 6)), 1600 + lerp(4, 100, kout(fr, 60, 8))),
           op=lambda fr, u: 1.0 if fr > 57 else 0.0)
    say_in(s, "#WARM", (348, 1566, 738, 1638), 800, "#F4B400", "Etiqueta", 63, align="center", how="blur", dx=0,
           stagger=0.06)
    say_in(s, "TAKE A PAUSE & ENJOY", (340, 1796, 745, 1824), 600, BLACK, "Texto", 66, align="center")
    return t


def adventures():
    D = dur_for(126, 1.8)
    t = _p("aventuras", "Historia: My Adventures con dos fotos y montaña verde",
           "Story: My Adventures with two photos and a green mountain", 15842, D, ["foto", "viajes", "aventura"],
           thumb=2.6)
    s = T(t, D)
    GREEN = "#00925A"
    bg(s, fillc(WHITE))
    s.obj("Montaña", fillc(GREEN), lambda fr, u: (540, 1456 + 920 * (1 - kout(fr, 3, 15)), 1080, 927, 0, 1.0),
          path=poly([(0, 56.1), (50, 0), (100, 56.1), (100, 100), (0, 100)]), base=(1080, 927))
    slide = lambda fr: kout(fr, 108, 18)  # noqa: E731
    win = lambda fr: (180, 440, 902, lerp(470, 1640, kout(fr, 27, 18)) if fr > 26 else 440)  # noqa: E731
    for i, (sample, x0) in enumerate((("fx-lighthouse-03", 180), ("fx-couple-02", 1002), ("fx-lighthouse-02", 1824))):
        shift = (lambda x0=x0: lambda fr: (-822 * slide(fr), 0))()
        c = win_photo(s, sample, (x0, 440, x0 + 722, 1640),
                      (lambda x0=x0: lambda fr: (lambda r: (r[0] + x0 - 180 - 822 * slide(fr), r[1],
                                                            r[2] + x0 - 180 - 822 * slide(fr), r[3])
                                                  if (x0 == 180 or fr > 107) else (0, 0, 0, 0))(win(fr)))(),
                      label=f"Foto {i + 1}", name=f"Foto {i + 1}", shift=shift)
        if i == 0:
            blur(s, c, lambda fr, u: 30 * (1 - k(fr, 30, 18)))
    s.obj("Rombo", fillc("#000000"), lambda fr, u: (540, lerp(-80, 437, kb(fr, 6, 12)), 100, 100, 0, 1.0),
          path=poly([(50, 0), (100, 50), (50, 100), (0, 50)]))
    c = s.say("- MY -", (386, 128, 700, 198), M, 800, BLACK, "Texto", align="center",
              geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 6)))
    c = s.say("ADVENTURES", (186, 238, 900, 318), M, 800, BLACK, "Título", align="center",
              geom=lambda fr, u: (0, -40 * (1 - kout(fr, 27, 9)), 1, 0, k(fr, 27, 6)))
    say_in(s, "#followme", (352, 1748, 734, 1798), 600, WHITE, "Etiqueta", 39, align="center")
    return t


def clear_interior():
    D = dur_for(75, 1.8)
    t = _p("interior", "Historia: Clear Interior con caja negra", "Story: Clear Interior with a black box", 15843, D,
           ["foto", "hogar", "interiorismo"], thumb=3.6)
    s = T(t, D)
    bg(s, fillc(WHITE))
    win_photo(s, "interior-01", (544, 100, 1080, 1820), lambda fr: (544, 100, 1080, 1820),
              shift=lambda fr: (540 * (1 - kout(fr, 3, 36)), 0))
    say_in(s, "Your style", (82, 108, 455, 163), 700, BLACK, "Texto", 36, how="blur", dx=0)
    s.rect("Caja", fillc("#000000"), lambda fr, u: (lerp(425, 0, kout(fr, 48, 12)), 642, lerp(445, 850, kout(fr, 48, 12)),
                                                     1280), op=lambda fr, u: 1.0 if fr > 48 else 0.0)
    say_in(s, "CLEAR", (86, 772, 515, 858), 800, WHITE, "Título", 60, how="blur", dx=0, stagger=0.04)
    c = s.say("INTERIOR", (86, 886, 715, 975), M, 800, WHITE, "Título 2",
              reveal=lambda fr: (0, 870, 850, 990), shift=lambda fr: (0, 100 * (1 - kout(fr, 64, 9))))
    for i, ln in enumerate(("THE BEST ROOMS HAVE", "SOMETHING TO SAY ABOUT", "THE PEOPLE", "WHO LIVE IN THEM")):
        say_in(s, ln, (92, 1012 + i * 34, 620, 1036 + i * 34), 600, WHITE, f"Texto {i + 2}", 66 + i * 2)
    say_in(s, "#follow", (86, 1772, 335, 1822), 700, BLACK, "Etiqueta", 69)
    return t


def waves_path(n=8):
    out = []
    for j in range(n):
        y0 = 5 + j * 12
        pts = [(x, y0 + 4 * math.sin(x / 100 * 2 * math.pi * 1.2 + j) + x * 0.05) for x in range(0, 101, 4)]
        out.append("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts))
    return " ".join(out)


def design_passion():
    D = dur_for(75, 1.8)
    t = _p("diseno-pasion", "Historia: Design is my passion en rosa", "Story: Design is my passion on pink", 15844, D,
           ["foto", "diseño", "arquitectura", "rosa"], thumb=3.6)
    s = T(t, D)
    PINK = "#FFA8A4"
    bg(s, fillc(PINK))
    sl = lambda fr: (1 - kout(fr, 45, 15))  # noqa: E731
    s.rect("Marco azul", fillc("#0B3BF0"), lambda fr, u: (214 - 120 * sl(fr), 206 - 120 * sl(fr),
                                                         970 - 120 * sl(fr), 1224 - 120 * sl(fr)),
           op=lambda fr, u: k(fr, 45, 3))
    s.obj("Ondas", stroke("#FFB8CE", 4), lambda fr, u: (592 - 120 * sl(fr), 715 - 120 * sl(fr), 756, 1018, 0,
                                                        k(fr, 45, 3)),
          path=waves_path(), base=(756, 1018))
    win_photo(s, "city-04", (114, 120, 866, 1130), lambda fr: (114, 120, 866, 1130))
    rows = 12
    rng = random.Random(6)
    order = list(range(rows))
    rng.shuffle(order)
    hgt = (1130 - 120) / rows
    for r in range(rows):
        y0 = 120 + r * hgt

        def cover(fr, u, y0=y0, at=12 + order[r] * 2.2):
            h = hgt * (1 - kout(fr, at, 12))
            return 110, y0 + hgt / 2 - h / 2, 870, y0 + hgt / 2 + h / 2
        s.rect(f"Persiana {r + 1}", fillc(PINK), cover)
    say_in(s, "DESIGN", (112, 1378, 440, 1432), 800, WHITE, "Título", 54, how="blur", stagger=0.04)
    say_in(s, "IS", (466, 1378, 540, 1432), 300 if (M, 300) in f6._FILES else 400, WHITE, "Título 2", 58, how="blur")
    say_in(s, "MY PASSION", (112, 1462, 615, 1522), 400, WHITE, "Título 3", 60, how="blur", stagger=0.04)
    s.rect("Línea", fillc(WHITE), lambda fr, u: (112, 1603, lerp(112, 970, kout(fr, 66, 12)), 1607))
    say_in(s, "THE DETAILS ARE NOT THE DETAILS,", (112, 1712, 690, 1738), 500, WHITE, "Texto", 69)
    say_in(s, "THEY MAKE THE DESIGN", (112, 1768, 500, 1794), 500, WHITE, "Texto 2", 72)
    return t


def _clip_line(p0, p1, poly_pts):
    """Cyrus–Beck: the part of segment p0-p1 inside a convex polygon (clockwise or not)."""
    t0, t1 = 0.0, 1.0
    d = (p1[0] - p0[0], p1[1] - p0[1])
    n = len(poly_pts)
    cx = sum(p[0] for p in poly_pts) / n
    cy = sum(p[1] for p in poly_pts) / n
    for i in range(n):
        a, b = poly_pts[i], poly_pts[(i + 1) % n]
        nx, ny = -(b[1] - a[1]), b[0] - a[0]
        if nx * (cx - a[0]) + ny * (cy - a[1]) < 0:
            nx, ny = -nx, -ny
        num = nx * (p0[0] - a[0]) + ny * (p0[1] - a[1])
        den = nx * d[0] + ny * d[1]
        if abs(den) < 1e-9:
            if num < 0:
                return None
            continue
        tt = -num / den
        if den > 0:
            t0 = max(t0, tt)
        else:
            t1 = min(t1, tt)
        if t0 > t1:
            return None
    return (p0[0] + d[0] * t0, p0[1] + d[1] * t0), (p0[0] + d[0] * t1, p0[1] + d[1] * t1)


def sale_50():
    D = dur_for(69, 1.8)
    t = _p("rebajas-50", "Historia: SALE con etiqueta 50% OFF y rayas azules",
           "Story: SALE with a 50% OFF tag and blue stripes", 15845, D, ["foto", "rebajas", "descuento", "moda"],
           thumb=3.4)
    s = T(t, D)
    bg(s, fillc(WHITE))
    # the striped L behind the photo (top band and right band), one path of short diagonal strokes
    bx0, by0, bx1, by1 = 72, 320, 1080, 1846
    parts = [[(72, 400), (152, 320), (1080, 320), (1080, 400)], [(886, 400), (1080, 400), (1080, 1652), (886, 1846)]]
    segs = []
    for c0 in range(-2000, 2200, 22):
        p0, p1 = (c0, 2000), (c0 + 1900, 100)
        for part in parts:
            r = _clip_line(p0, p1, part)
            if r:
                segs.append(r)
    sw, sh = bx1 - bx0, by1 - by0
    path = bars([((a[0] - bx0) / sw * 100, (a[1] - by0) / sh * 100, (b[0] - bx0) / sw * 100, (b[1] - by0) / sh * 100)
                 for a, b in segs], 0.32)
    stripes = s.obj("Rayas", fillc("#2147E0"), lambda fr, u: (
        (bx0 + bx1) / 2 - 194 * (1 - kout(fr, 45, 18)), (by0 + by1) / 2 + 80 * (1 - kout(fr, 45, 18)), sw, sh, 0,
        1.0 if fr > 45 else 0.0), path=path, base=(sw, sh))
    stripes["shapeStyle"]["customEvenOdd"] = False
    edge = lambda fr: lerp(72, 990, kout(fr, 3, 30))  # noqa: E731
    win_photo(s, "fx-woman-02", (72, 400, 886, 1846), lambda fr: (72, 400, min(886, edge(fr) - 120), 1846))
    s.obj("Franja roja", fillc("#FF2A00"), lambda fr, u: (edge(fr) - 60, 1123, 380 * (1 - k(fr, 24, 12)) + 1, 1446, 0,
                                                          1.0 if 3 < fr < 36 else 0.0),
          path=poly([(0, 0), (40, 0), (100, 100), (60, 100)]), base=(380, 1446))
    s.rect("Caja negra", fillc("#000000"), lambda fr, u: (72, -10, 744, lerp(-10, 322, kout(fr, 45, 12))))
    c = s.say("SALE", (76, 178, 570, 312), M, 800, WHITE, "Título",
              reveal=lambda fr: (0, 0, 1080, 322), shift=lambda fr: (0, 160 * (1 - kout(fr, 54, 12))))
    tag_g = lambda fr, u: (842, 1062, 390 * kb(fr, 48, 12), 118 * kb(fr, 48, 12), -45, 1.0 if fr > 48 else 0.0)  # noqa
    s.obj("Etiqueta", fillc("#FF2A00"), tag_g, base=(440, 130))
    c = s.say("50% OFF", (720, 1035, 964, 1089), M, 800, WHITE, "Descuento", align="center",
              geom=lambda fr, u: (0, 0, max(0.01, kb(fr, 51, 12)), -45, 1.0 if fr > 51 else 0.0))
    return t


def art(make, every=False):
    """In a horizontal video the story keeps its shape: every clip but the backdrop is design ("art")."""
    def wrapped():
        t = make()
        for track in t.tracks:
            for clip in track.clips:
                if clip.get("type") in ("audio", "adjustment", "composite") or "layoutRole" in clip:
                    continue
                clip["layoutRole"] = "art"
        return t
    wrapped.__name__ = make.__name__
    wrapped.__module__ = make.__module__
    return wrapped


TEMPLATES = [art(f) for f in (
    merry_bright, santa, ribbon_tree, winter_sale, pine_red,
    sw_glow, sw_toggle, sw_letters, sw_flag, sw_hand, sw_circle,
    sw_box, sw_morph, sw_chevrons, sw_button, sw_arrow, sw_triangle,
    artist, cozy_light, adventures, clear_interior, design_passion, sale_50)]
