"""Video 36232731.mp4 as Kit de YouTube Stock templates (yp8-*). See docs/plan-youtube-pack-2.md.

The «lower thirds + social media» pack (1920×1080 at 29.97 fps, 57 s), each element studied on 10 fps and
frame-by-frame sheets and measured with colour trackers (study notes in tienda/plantillas/estudio-36232731/NOTAS.md):
the YouTube logo that builds itself (a red dot grows into the button, a chevron draws itself and flies in as the
play triangle, confetti, the name in pieces, the channel line swept by a coloured stroke) on white, on dark and in
white over a video; the like buttons in a dark and a white circle (they pop in, are pressed, turn blue and throw
confetti); the subscribe bars (the logo intro, a bar that opens with SUBSCRIBE, a hand clicks it into SUBSCRIBED and
rings the bell); the resizable lower thirds (a white line opens into a box and the words write themselves with
confetti) one by one and the seven of them together; the two gradient wipes; the shape openers that sweep over the
lockup and leave the user's logo with its address; and «enjoy». Every geometry is a function of the reference's
frame number n (tables measured on the video, interpolated); each piece starts at its own frame. Footage in the
reference → transparent background (the pieces sit on the user's video). Brands: the pack's marketplace names →
«/yourchannel», «johndoe» → «yourname»; the other logo → the user's logo slot.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, keys, no_stroke
from templates_lg0 import ink, logo, sh as lg_sh, stroke_path, tab
from templates_tit_c import FPS
from templates_tit_e import solid
from templates_tit_h import fill, poly, ring
from templates_yp0 import BELL, BIRD, HAND, HAND_LINES, TIP, W

WHITE, BLACK, RED = "#FFFFFF", "#000000", "#FF0000"
INK = "#282828"
DARK = "#272727"
GREY_T = "#909090"
BLUE = "#065FD3"
OSW, OS, RB = "Oswald", "Open Sans", "Roboto"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold")):
    f6._FILES[(OSW, _w)] = f"fonts.basic/fonts/oswald/Oswald-{_f}.ttf"
for _w, _f in ((400, "Regular"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(OS, _w)] = f"fonts.basic/fonts/opensans/OpenSans-{_f}.ttf"
for _w, _f in ((400, "Regular"), (500, "Medium"), (700, "Bold"), (900, "Black")):
    f6._FILES[(RB, _w)] = f"fonts.basic/fonts/roboto/Roboto-{_f}.ttf"

HANDLE = "@yourname"
CHANNEL = "/yourchannel"
URL = "youtube.com/yourchannel"
TRI = "M 0 0 L 100 50 L 0 100 Z"
# The like icon of the reference: a blocky thumb and its cuff (measured on a 143 × 142 px thumb).
THUMB = (poly([(0, 32.4), (19.6, 32.4), (19.6, 100), (0, 93.7)]) + " " +
         poly([(26.6, 31.7), (52.4, 0), (60.8, 0), (64.3, 4.9), (64.3, 31.7), (100, 31.7), (100, 54.2), (86, 100),
               (42, 100), (26.6, 94.4)]))
HOLLOW = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ramp(n, a, d):
    return clamp((n - a) / max(1e-9, d))


def sm(n, a, d):
    q = ramp(n, a, d)
    return q * q * (3 - 2 * q)


def eout(n, a, d, p=3.0):
    return 1 - (1 - ramp(n, a, d)) ** p


def stroke(colour, width):
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center", "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def _p(id, es, en, order, dur, section, tags=(), thumb=None):
    return wide(f"yp8-{id}", es, en, "ytkit", round(dur, 2), order=order,
                tags=[f"kit:{section}", "youtube"] + list(tags), thumb_at=round(thumb if thumb else dur * 0.6, 1))


class P(W):
    """A piece of the reference from frame f0: every geometry is fn(n), n = the reference's frame number."""

    def __init__(self, t, dur, f0):
        super().__init__(t, dur, f0 / FPS)
        self.f0 = f0

    def sh(self, name, layers, fn, **kw):
        return self.shp(name, layers, lambda v: fn(v * FPS), **kw)

    def rsh(self, name, layers, fn, base, radius=0.0, **kw):
        """A shape whose corner radius (at base) follows its size."""
        return lg_sh(self, name, layers, lambda v: fn(v * FPS), base, radius=radius, **kw)

    def tx(self, content, box, family, weight, colour, name, fn=None, align="left", editable=True):
        return self.txt(content, box, family, weight, colour, name, align=align, editable=editable,
                        g=(lambda v: fn(v * FPS)) if fn else None)

    def type_in(self, clip, n_at, stagger, dur, preset="fade", order="forward", **kw):
        """Letters come in from the reference's frame n_at (stagger / dur in seconds)."""
        from scene import tanim
        clip["textStyle"]["animation"] = {"in": tanim(preset, duration=dur, unit="character", stagger=stagger,
                                                      ease="easeOut", delay=round(max(0.0, (n_at - self.f0) / FPS), 3),
                                                      order=order, **kw)}
        clip["textStyle"]["wordWrap"] = False

    def matte(self, host, src, mode="alpha"):
        host["matte"] = {"clip": src["id"], "mode": mode}

    def gradrect(self, name, c0, c1, angle=90.0, op=None):
        """A full-frame screen-aligned gradient (top c0 → bottom c1 at angle 0), to be shown through a matte."""
        return self.sh(name, [gradient([(0.0, c0), (1.0, c1)], angle=angle), no_stroke()],
                       lambda n: (960, 540, 1920, 1080, 0, op(n) if op else 1.0))

    def hand(self, pts, n_in, n_out, clicks=(), size=(34, 44), name="Cursor"):
        """The pointing hand: its tip through [(frame, x, y)], a small press at each click frame."""
        f = tab([(a, x, y) for a, x, y in pts])

        def g(n):
            x, y = f(n)
            sc = 1 - sum(0.1 * math.sin(math.pi * ramp(n, c - 3, 6)) for c in clicks)
            cw, ch = size[0] * sc, size[1] * sc
            return x + (0.5 - TIP) * cw, y + 0.5 * ch, cw, ch, 0, ramp(n, n_in, 3) * (1 - ramp(n, n_out, 3))
        self.sh(name, [fill(WHITE), stroke(BLACK, 2.4)], g, path=HAND, base=size)
        self.sh(f"{name} (líneas)", ring(BLACK, 1.8), g, path=HAND_LINES, base=size)


# ==== the YouTube button that builds itself (shared by the logo and the subscribe bars) ===========================
# The red button's box per reference frame (logo at 2.6 s, frames 79-160), (x0, y0, x1, y1).
LOGO_RECT = tab([(79, 1104, 537, 1112, 543), (80, 1088, 533, 1108, 547), (81, 1068, 528, 1102, 552),
                 (82, 1044, 522, 1094, 558), (83, 1018, 516, 1086, 564), (84, 992, 510, 1078, 570),
                 (85, 962, 503, 1068, 576), (86, 934, 496, 1060, 584), (87, 904, 489, 1050, 591),
                 (88, 878, 482, 1042, 598), (89, 848, 482, 1012, 598), (90, 824, 482, 988, 598),
                 (91, 808, 482, 972, 598), (92, 798, 482, 962, 598), (94, 794, 482, 958, 598),
                 (96, 806, 482, 970, 598), (98, 826, 482, 990, 598), (100, 850, 482, 1014, 598),
                 (102, 870, 482, 1034, 598), (104, 884, 482, 1048, 598), (106, 894, 482, 1058, 598),
                 (108, 896, 482, 1060, 598), (110, 896, 482, 1060, 598), (113, 890, 482, 1054, 598),
                 (116, 880, 482, 1044, 598), (119, 868, 482, 1032, 598), (122, 855, 482, 1019, 598),
                 (124, 844, 482, 1008, 598), (125, 837, 482, 1001, 598), (126, 827, 482, 992, 598),
                 (127, 812, 482, 976, 598), (128, 772, 482, 936, 598), (129, 738, 482, 902, 598),
                 (130, 726, 482, 890, 598), (132, 714, 482, 878, 598), (134, 708, 482, 872, 598),
                 (137, 704, 482, 868, 598), (140, 702, 482, 866, 598), (146, 700, 482, 864, 598),
                 (147, 700, 478, 864, 594), (148, 700, 474, 864, 590), (149, 700, 468, 864, 584),
                 (150, 700, 462, 864, 578), (151, 700, 454, 864, 570), (152, 700, 446, 864, 562),
                 (153, 700, 442, 864, 558), (154, 700, 438, 864, 554), (156, 700, 436, 864, 552),
                 (158, 700, 434, 864, 550)])
# The same button in the subscribe bar (frames 737-806 of the third shot).
SUB_RECT = tab([(737, 536, 910, 556, 924), (740, 468, 894, 534, 940), (743, 382, 874, 508, 962),
                (746, 296, 860, 460, 974), (749, 246, 860, 410, 974), (752, 246, 860, 412, 974),
                (755, 276, 860, 440, 974), (758, 308, 860, 472, 974), (761, 334, 860, 498, 974),
                (765, 340, 860, 504, 974), (770, 338, 860, 502, 974), (776, 316, 860, 480, 974),
                (779, 304, 860, 468, 974), (782, 286, 860, 450, 974), (785, 220, 860, 384, 974),
                (788, 170, 860, 334, 974), (791, 158, 860, 322, 974), (794, 152, 860, 316, 974),
                (797, 150, 860, 314, 974), (800, 148, 860, 313, 974)])


def yt_button(s, rect, n0, tri_n, chev_n, red=RED, tri=WHITE, chev=("#7B3BFF", "#1E9BFF", "#12E3B5"),
              hole=False, name="YouTube"):
    """The red button whose box is rect(n) (shifted so the reference's frame n0 is the logo's frame 79), the chevron
    that draws itself from frame chev_n left of it and flies in, and the white play triangle from frame tri_n."""
    def box(n):
        x0, y0, x1, y1 = rect(n)
        return x0, y0, x1, y1

    def g(n):
        x0, y0, x1, y1 = box(n)
        return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0, 1.0 if n >= n0 else 0.0
    btn = s.rsh(name, solid(red), g, (164, 116), radius=30)

    # the chevron: drawn bottom-left → tip → top-left → down (a hollow triangle), then into the button
    def anchor(n):
        x0, y0, x1, y1 = box(n)
        return x0 - 22 - 34 * (1 - ramp(n, chev_n + 7, 3)) + 45 * ramp(n, chev_n + 7, 3), (y0 + y1) / 2
    ax, ay = anchor(chev_n + 5)
    pts = [(ax - 50, ay + 24), (ax, ay), (ax - 50, ay - 24), (ax - 50, ay + 8)]
    lo = stroke_path(s, f"{name} (flecha)", pts, 7, chev[1], lambda v: (0.0, 0.0), smooth=False)
    # follow the anchor and draw it with trimEnd
    st = lo["shapeStyle"]
    us_ = frames_of(s.dur)
    st["keyframes"]["trimEnd"] = keys([(u, round(100 * (0.62 * eout(u * FPS + s.f0, chev_n, 6, 2)
                                                         + 0.38 * ramp(u * FPS + s.f0, chev_n + 6, 3)), 3), "linear")
                                       for u in us_])
    x0b, y0b = lo["x"]["keyframes"][0]["value"], lo["y"]["keyframes"][0]["value"]
    xs, ys, ops = [], [], []
    for u in us_:
        n = u * FPS + s.f0
        bx, by = anchor(n)
        xs.append((u, x0b + bx - ax, "linear"))
        ys.append((u, y0b + by - ay, "linear"))
        ops.append((u, 1.0 if chev_n <= n < tri_n else 0.0, "linear"))
    lo["x"], lo["y"], lo["opacity"] = keys(xs), keys(ys), keys(ops)
    lo["shapeStyle"]["layers"][1]["paint"] = gradient([(0.0, chev[0]), (0.5, chev[1]), (1.0, chev[2])], angle=90)["paint"]

    def tg(n):
        x0, y0, x1, y1 = box(n)
        w, h = x1 - x0, y1 - y0
        cx, cy = (x0 + x1) / 2 + w * 0.04, (y0 + y1) / 2
        q = ramp(n, tri_n, 2)
        cx -= (1 - q) * w * 0.42
        return cx, cy, 44 * (0.6 + 0.4 * q), 48 * (0.6 + 0.4 * q), 0, 1.0 if n >= tri_n else 0.0
    tclip = s.sh(f"{name} (play)", solid(tri), tg, path=TRI, base=(44, 48))
    if hole:
        s.matte(btn, tclip, "alphaInverted")
    return btn


def confetti(s, n_at, base, pieces, n_out, name="Confeti"):
    """Small shapes thrown out at frame n_at from base(n) = (x, y): pieces = [(kind, colour, dx, dy, size)], each
    reaching (dx, dy) from the base in 10 frames, drifting a little more and fading at n_out."""
    for i, (kind, col, dx, dy, size) in enumerate(pieces):
        def g(n, dx=dx, dy=dy, size=size, i=i):
            bx, by = base(n)
            q = eout(n, n_at + (i % 3), 10, 2.5)
            drift = 0.15 * ramp(n, n_at + 10, 14)
            on = 1.0 if n >= n_at + (i % 3) else 0.0
            return (bx + dx * (q + drift), by + dy * (q + drift), size * (0.4 + 0.6 * q), size * (0.4 + 0.6 * q),
                    60 * q * (1 if i % 2 else -1), on * (1 - ramp(n, n_out, 4)))
        if kind == "tri":
            s.sh(f"{name} {i + 1}", solid(col), g, path=TRI)
        elif kind == "sq":
            s.sh(f"{name} {i + 1}", solid(col), g)
        else:
            s.sh(f"{name} {i + 1}", solid(col), g, kind="ellipse")


LOGO_CONF = [("tri", "#F0109A", 86, -40, 26), ("dot", "#8A2BFF", 92, -12, 34), ("dot", "#3A73FF", 34, -10, 30),
             ("sq", "#12DCD8", -4, 14, 20), ("dot", "#8A2BFF", 50, 16, 16), ("tri", "#18A8FF", 120, -30, 16)]


# ==== 1-3. The YouTube logo: on white, on dark, in white over a video (2.57-6.0 s, 32.8-36.3 s, 46.5-50 s) ========
def yt_logo(variant):
    F0, END = 76, 200
    D = (END + 10 - F0) / FPS
    es, en, tags = {"claro": ("Logo de YouTube que se arma (fondo blanco)", "Self-building YouTube logo (white)", ["blanco"]),
                    "oscuro": ("Logo de YouTube que se arma (fondo oscuro)", "Self-building YouTube logo (dark)", ["oscuro"]),
                    "video": ("Logo de YouTube blanco sobre tu video", "White YouTube logo over your video", ["blanco"])}[variant]
    order = {"claro": 17000, "oscuro": 17001, "video": 17002}[variant]
    t = _p(f"logo-youtube-{variant}", es, en, order, D, "aperturas", ["logo", "apertura"] + tags, thumb=3.6)
    s = P(t, D, F0)
    out = lambda n: 1 - ramp(n, END, 8)  # noqa: E731
    if variant == "claro":
        s.sh("Fondo", solid(WHITE), lambda n: (960, 540, 1920, 1080, 0, 1))
    elif variant == "oscuro":
        s.sh("Fondo", solid(DARK), lambda n: (960, 540, 1920, 1080, 0, 1))
    red, tri, word, line, line2 = {"claro": (RED, WHITE, INK, "#F000E0", RED),
                                   "oscuro": (RED, WHITE, WHITE, "#05EAFF", "#00FA7B"),
                                   "video": (WHITE, BLACK, WHITE, "#05EAFF", "#00FA7B")}[variant]
    btn = yt_button(s, LOGO_RECT, 79, 101, 89, red=red, tri=tri, hole=(variant == "video"))
    btn["opacity"] = keys([(u, round(out(u * FPS + F0), 4), "linear") for u in frames_of(D)])
    confetti(s, 110, lambda n: (LOGO_RECT(n)[2] - 10, 530),
             [(a, WHITE if variant == "video" else c, dx, dy, z) for a, c, dx, dy, z in LOGO_CONF], 121)
    # «YouTube» in pieces, riding on the button's right (Oswald set 5 px tighter to the wordmark's width)
    bx = ink("YouTube", OSW, 500, 95, 885, 0)
    wbox = (885, 444, bx[2], 539)

    def wg(n):
        x0, y0, x1, y1 = LOGO_RECT(n)
        return x1 + 21 - 885, (y0 + y1) / 2 - 491.5, 1, 0, out(n)
    yt = s.tx("YouTube", wbox, OSW, 500, word, "Nombre", fn=wg)
    s.type_in(yt, 124, 0.045, 0.12, preset="rise", order="random", distance=0.25)
    # the channel line, swept by a stroke and a second short one
    cb = ink(CHANNEL, OS, 400, 33, 754, 578)
    s.type_in(s.tx(CHANNEL, cb, OS, 400, word, "Canal", fn=lambda n: (0, 0, 1, 0, out(n))), 153, 0.03, 0.2,
              preset="fade")
    e = cb[2]
    stroke_path(s, "Canal (raya)", [(728, 616), (e - 93, 616)], 10, line,
                lambda v: (ramp(v * FPS, 163, 6), eout(v * FPS, 155, 7, 2)), smooth=False)
    stroke_path(s, "Canal (raya 2)", [(e - 25, 616), (e + 69, 616)], 10, line2,
                lambda v: (ramp(v * FPS, 169, 6), eout(v * FPS, 162, 4, 2)), smooth=False)
    return t


def logo_light():
    return yt_logo("claro")


def logo_dark():
    return yt_logo("oscuro")


def logo_video():
    return yt_logo("video")


# ==== 4-5. Like buttons in a circle (6.6-12.2 s) ==================================================================
POP = tab([(199, 0.0), (200, 0.086), (210, 1.0), (213, 1.055), (216, 1.072), (219, 1.06), (222, 1.03), (226, 0.995),
           (230, 1.0)])
THUMB_IN = tab([(204, 0.0), (209, 0.45), (215, 1.0), (219, 1.07), (224, 1.06), (232, 1.0)])
PRESS = tab([(240, 1.0), (242, 0.85), (245, 0.58), (247, 0.86)])
BLUE_POP = tab([(247, 1.0), (248, 0.92 / 0.86), (250, 0.97 / 0.86), (252, 1.0 / 0.86)])
LIKE_CONF = {"blanco": [("tri", "#F0109A", -60, -330, 70), ("dot", "#8A3BFF", 40, -320, 75),
                        ("dot", "#12A8FF", 0, -270, 70), ("dot", "#9B30FF", 80, -260, 40),
                        ("sq", "#2EE0F0", 10, -170, 38), ("tri", "#1E7BFF", -40, -200, 30)],
             "oscuro": [("tri", "#F08A24", -50, -330, 60), ("dot", "#8BC34A", 40, -320, 66),
                        ("dot", "#7CB342", 0, -260, 60), ("tri", "#F0A23A", 70, -250, 40),
                        ("sq", "#F07070", 10, -170, 30), ("dot", "#8BC34A", -40, -200, 28)]}


def like(variant):
    F0, END = 197, 340
    D = (END + 9 - F0) / FPS
    dark = variant == "oscuro"
    t = _p(f"me-gusta-{variant}", "Me gusta en círculo oscuro" if dark else "Me gusta en círculo blanco",
           "Like in a dark circle" if dark else "Like in a white circle", 17010 + (0 if dark else 1), D, "elementos",
           ["me gusta", "botón", "círculo"], thumb=2.4)
    s = P(t, D, F0)
    cx, cy, d = (549, 293, 310) if dark else (1198, 407, 486)
    out = lambda n: 1 - eout(n, END, 8, 2)  # noqa: E731
    s.sh("Círculo", solid(DARK if dark else WHITE), lambda n: (cx, cy, d * POP(n)[0] * out(n), d * POP(n)[0] * out(n),
                                                               0, 1.0 if n >= 199 else 0.0), kind="ellipse",
         base=(d, d))
    tw = 0.295 * d
    tcx, tcy = cx + 0.004 * d, cy - 0.012 * d

    def tg(n, after):
        sc = THUMB_IN(n)[0] * (PRESS(n)[0] if not after else 0.86 * BLUE_POP(n)[0]) * out(n)
        hit = n >= 248
        return tcx, tcy, tw * sc, tw * sc, 0, (1.0 if hit == after else 0.0) * (1.0 if n >= 204 else 0.0)
    s.sh("Me gusta", solid(GREY_T), lambda n: tg(n, False), path=THUMB, base=(tw, tw))
    s.sh("Me gusta (activo)", solid(BLUE), lambda n: tg(n, True), path=THUMB, base=(tw, tw))
    k = d / 486
    confetti(s, 249, lambda n: (tcx, tcy), [(a, c, dx * k, dy * k, sz * k ** 0.25) for a, c, dx, dy, sz in LIKE_CONF[variant]],
             261)
    return t


def like_dark():
    return like("oscuro")


def like_white():
    return like("blanco")


# ==== 6-7. Subscribe bar: the button builds itself, a bar opens with SUBSCRIBE, a hand clicks it (24.5-29.0 s) ====
BAR_END = tab([(778, 468), (782, 534), (785, 570), (788, 606), (791, 630), (794, 645), (797, 660), (800, 675),
               (803, 684), (806, 693), (812, 701)])


def sub_rect(n0, dx=0.0, dy=0.0):
    """The subscribe bar's button box, its dot appearing at frame n0 (737 in the reference), moved by (dx, dy)."""
    def r(n):
        x0, y0, x1, y1 = SUB_RECT(n + 737 - n0)
        return x0 + dx, y0 + dy, x1 + dx, y1 + dy
    return r


def yt_bar(s, n0, x_end, bar_colour, dx=0.0, dy=0.0, end=None, name="Barra"):
    """The red button of the subscribe bars and the bar that opens from it to x_end (at the reference's place; dx,
    dy move the whole thing). Returns (button box fn, bar right-edge fn)."""
    rect = sub_rect(n0, dx, dy)
    sh = 737 - n0
    span = x_end - 701

    def right(n):
        b = BAR_END(n + sh)[0]
        return b + dx + span * ramp(b, 468, 233)

    def bg(n):
        x0, y0, x1, y1 = rect(n)
        cx = (x0 + x1) / 2
        r = max(cx + 1, right(n))
        return (cx + r) / 2, 916.5 + dy, r - cx, 107, 0, (1.0 if n >= 777 - sh else 0.0) * (end(n) if end else 1.0)
    s.sh(name, solid(bar_colour), bg)
    btn = yt_button(s, rect, n0, 758 - sh, 747 - sh)
    if end:
        btn["opacity"] = keys([(u, round(end(u * FPS + s.f0), 4), "linear") for u in frames_of(s.dur)])
    confetti(s, 779 - sh, lambda n: (right(n) - 6, 905 + dy), LOGO_CONF, 789 - sh, name=f"{name} (confeti)")
    return rect, right


def subscribe(variant):
    F0, END = 733, 880
    D = (END + 10 - F0) / FPS
    dark = variant == "oscuro"
    t = _p(f"suscribirse-{variant}", "Barra de suscribirse con clic y campana" + (" (oscura)" if dark else ""),
           "Subscribe bar with click and bell" + (" (dark)" if dark else ""), 17020 + (1 if dark else 0), D,
           "elementos", ["suscríbete", "botón", "clic", "campana"], thumb=4.6)
    s = P(t, D, F0)
    end = lambda n: 1 - ramp(n, END, 8)  # noqa: E731
    rect, right = yt_bar(s, 737, 701, "#262626" if dark else WHITE, end=end)
    clip = lambda v: (SUB_RECT(v * FPS)[2], 860, max(SUB_RECT(v * FPS)[2] + 1, right(v * FPS)), 974)  # noqa: E731
    # SUBSCRIBE (dark red) slides out from behind the button; a flash when pressed; then the grey SUBSCRIBED
    bx = lambda n: 250 + 158 * eout(n, 787, 10, 2.5) - 28 * sm(n, 825, 9)  # noqa: E731
    pre = s.sh("Suscribirse", solid("#CC0000"), lambda n: (bx(n) + 107, 918, 214, 76, 0, (1.0 if 786 <= n < 823 else 0.0)
                                                         * end(n)))
    flash = s.sh("Suscribirse (pulsado)", solid("#E87575"), lambda n: (bx(n) + 107, 918, 214, 76, 0,
                                                                     (1.0 if 819 <= n < 823 else 0.0)))
    cap = ink("SUBSCRIBE", RB, 500, 18, 515, 909, align="center")
    w1 = s.tx("SUBSCRIBE", cap, RB, 500, WHITE, "Suscribirse (texto)", align="center",
              fn=lambda n: (bx(n) - 408, 0, 1, 0, (1.0 if 786 <= n < 823 else 0.0) * end(n)))
    s.sh("Suscrito", solid("#EEEEEE"), lambda n: (bx(n) + 107, 918, 214, 76, 0, (1.0 if n >= 823 else 0.0) * end(n)))
    cap2 = ink("SUBSCRIBED", RB, 500, 18, 515, 909, align="center")
    s.tx("SUBSCRIBED", cap2, RB, 500, "#606060", "Suscrito (texto)", align="center",
         fn=lambda n: (bx(n) - 408, 0, 1, 0, (1.0 if n >= 823 else 0.0) * end(n)))
    for m in (pre, flash, w1):
        s.mask_to(m, clip)
    # the bell: an outline that pops in after the click, filled and ringing after its own click
    bc = "#B0B0B0" if dark else "#606060"

    def bell(n, after):
        q = eout(n, 829, 7, 2) * (1 + 0.15 * math.sin(math.pi * ramp(n, 829, 7)))
        hit = n >= 862
        wig = 16 * math.sin(2 * math.pi * (n - 862) / 7) * math.exp(-(n - 862) / 12) if hit else 0.0
        return 642, 917, 30 * q, 36 * q, wig, (1.0 if hit == after else 0.0) * (1.0 if n >= 829 else 0.0) * end(n)
    s.sh("Campana", [HOLLOW, stroke(bc, 3)], lambda n: bell(n, False), path=BELL, base=(30, 36))
    s.sh("Campana (sonando)", solid(bc), lambda n: bell(n, True), path=BELL, base=(30, 36))
    for i, f in enumerate((1.25, 1.6)):
        s.sh(f"Campana (ondas {i + 1})", [HOLLOW, stroke(bc, 3)],
             lambda n, f=f, i=i: (642, 914, 36 * f, 36 * f, 0, (1.0 if n >= 864 + 2 * i else 0.0) * end(n)),
             path="M 4 30 C 0 42 0 58 4 70 M 96 30 C 100 42 100 58 96 70", base=(36 * f, 36 * f))
    s.hand([(797, 580, 1060), (806, 525, 935), (812, 515, 922), (840, 515, 922), (852, 648, 925), (900, 648, 925)],
           797, END, clicks=(819, 862))
    return t


def sub_white():
    return subscribe("blanco")


def sub_dark():
    return subscribe("oscuro")


# ==== 8-15. Lower thirds: a white line opens into a box and the words write themselves (13.4-24.1 s) ============
OPEN = tab([(0, 0.0), (1, 0.005), (3, 0.07), (6, 0.30), (9, 0.55), (12, 0.70), (15, 0.79), (18, 0.86), (21, 0.90),
            (24, 0.935), (27, 0.96), (30, 0.98), (35, 0.995), (40, 1.0)])
IG_GLYPH = ("M 30 5 L 70 5 C 84 5 95 16 95 30 L 95 70 C 95 84 84 95 70 95 L 30 95 C 16 95 5 84 5 70 L 5 30 "
            "C 5 16 16 5 30 5 Z M 50 28 C 62 28 72 38 72 50 C 72 62 62 72 50 72 C 38 72 28 62 28 50 C 28 38 38 28 "
            "50 28 Z M 76 18 C 79 18 82 21 82 24 C 82 27 79 30 76 30 C 73 30 70 27 70 24 C 70 21 73 18 76 18 Z")
# kind: (width, height, box colour, confetti colour)
BOXES = {"nombre": (557, 85, WHITE, "#F2A0A8"), "instagram": (442, 86, WHITE, "#B5317F"),
         "twitter": (422, 86, "#1DA1F2", WHITE), "facebook": (692, 85, WHITE, "#3B5998"),
         "youtube": (1131, 85, WHITE, "#FF4040")}


# kind: (words, family, weight, colour, cap height, text x from the box's left)
WORDS = {"nombre": ("YOUR NAME / GRAPHIC DESIGNER", OSW, 500, "#222222", 36, 40),
         "instagram": (HANDLE, RB, 700, "#222222", 29, 154),
         "twitter": ("#yourname", RB, 700, WHITE, 29, 154),
         "facebook": ("follow us on facebook", OS, 400, "#444444", 27, 151),
         "youtube": ("subscribe to my channel on youtube.com/yourname", RB, 700, "#111111", 29, 152)}
MARGIN = {"nombre": 39, "instagram": 112, "twitter": 105, "facebook": 70, "youtube": 98}


def text_box(kind, x0, y0):
    words, fam, wt, col, cap, dx = WORDS[kind]
    h = BOXES[kind][1]
    return ink(words, fam, wt, cap, x0 + dx, y0 + h / 2 - cap / 2)


def lt_box(s, kind, x0, y0, L, end):
    """One resizable lower third of the pack with its top-left at (x0, y0); its line shows at frame L."""
    w, h, colour, cc = BOXES[kind]
    w = text_box(kind, x0, y0)[2] + MARGIN[kind] - x0  # the box fits its words (resizable lower thirds)
    op = lambda n: (1.0 if n >= L else 0.0) * end(n)  # noqa: E731
    s.sh(f"Caja {kind}", solid(colour), lambda n: (x0 + max(3, w * OPEN(n - L)[0]) / 2, y0 + h / 2,
                                                   max(3, w * OPEN(n - L)[0]), h, 0, op(n)))
    cy = y0 + h / 2
    pop = lambda n: eout(n, L + 8, 6, 2) * (1 + 0.12 * math.sin(math.pi * ramp(n, L + 8, 8)))  # noqa: E731
    icon_op = lambda n: (1.0 if n >= L + 8 else 0.0) * end(n)  # noqa: E731
    if kind == "instagram":
        s.sh("Icono instagram", [HOLLOW, stroke("#C13584", 4.5)], lambda n: (x0 + 64, cy, 44 * pop(n), 44 * pop(n), 0,
                                                                            icon_op(n)), path=IG_GLYPH, base=(44, 44))
    elif kind == "twitter":
        s.sh("Icono twitter", solid(WHITE), lambda n: (x0 + 64, cy, 46 * pop(n), 38 * pop(n), 0, icon_op(n)),
             path=BIRD, base=(46, 38))
    elif kind == "facebook":
        fb = ink("f", RB, 900, 34, x0 + 64, cy - 17, align="center")
        s.tx("f", fb, RB, 900, "#1E2A4A", "Icono facebook", align="center",
             fn=lambda n: (0, 0, max(1e-3, pop(n)), 0, icon_op(n)), editable=False)
    elif kind == "youtube":
        s.sh("Icono youtube", solid(RED), lambda n: (x0 + 64, cy, 50 * pop(n), 35 * pop(n), 0, icon_op(n)), radius=9,
             base=(50, 35))
        s.sh("Icono youtube (play)", solid(WHITE), lambda n: (x0 + 66, cy, 15 * pop(n), 17 * pop(n), 0, icon_op(n)),
             path=TRI)
    words, fam, wt, col, cap, _ = WORDS[kind]
    box = text_box(kind, x0, y0)
    c = s.tx(words, box, fam, wt, col, "Texto", fn=lambda n: (0, 0, 1, 0, end(n)))
    s.type_in(c, L + 9, 13 / FPS / len(words), 0.12, preset="rise", distance=0.5)
    head = lambda n: (box[0] + (box[2] - box[0]) * ramp(n, L + 9, 14), cy)  # noqa: E731
    confetti(s, L + 9, head, [("dot", cc, -14, -30, 36), ("tri", cc, 14, -40, 30), ("sq", cc, -34, 20, 22),
                              ("dot", cc, 22, 16, 26)], L + 22, name=f"Confeti {kind}")


def yt_lt(s, kind, n0, dx, dy, end):
    """The two YouTube bars of the set: SUBSCRIBE ON @… on dark, @… on white."""
    if kind == "yt-oscuro":
        x_end, colour, words, col = 954, "#262626", "SUBSCRIBE ON " + HANDLE, WHITE
    else:
        x_end, colour, words, col = 676, WHITE, HANDLE, "#8A8A8A"
    rect, right = yt_bar(s, n0, x_end, colour, dx=dx, dy=dy, end=end, name=f"Barra {kind}")
    sh = 737 - n0
    cxm = (148 + 82 + x_end) / 2 + dx
    box = ink(words, RB, 400, 29, cxm, 902 + dy, align="center")
    c = s.tx(words, box, RB, 400, col, "Texto", align="center", fn=lambda n: (0, 0, 1, 0, end(n)))
    s.type_in(c, 786 - sh, 10 / FPS / len(words), 0.12, preset="fade")
    s.mask_to(c, lambda v: (rect(v * FPS)[2], 0, max(rect(v * FPS)[2] + 1, right(v * FPS)), 1080))


LT_NAMES = {"nombre": ("Tercio: nombre y cargo", "Lower third: name and job"),
            "instagram": ("Tercio: usuario de Instagram", "Lower third: Instagram handle"),
            "twitter": ("Tercio: usuario de Twitter", "Lower third: Twitter handle"),
            "facebook": ("Tercio: síguenos en Facebook", "Lower third: follow us on Facebook"),
            "youtube": ("Tercio: suscríbete a mi canal", "Lower third: subscribe to my channel"),
            "yt-oscuro": ("Tercio: suscríbete en YouTube (oscuro)", "Lower third: subscribe on YouTube (dark)"),
            "yt-blanco": ("Tercio: usuario de YouTube", "Lower third: YouTube handle")}


def lower_third(kind, order):
    def make():
        L = 575 if kind != "instagram" else 659
        F0 = L - 3
        END = L + 69 if kind != "instagram" else 713
        if kind.startswith("yt"):
            F0, END = 733, 850
        D = (END + 9 - F0) / FPS
        es, en = LT_NAMES[kind]
        t = _p(f"tercio-{kind}", es, en, order, D, "tercios", ["tercio", "redes"], thumb=D - 0.8)
        s = P(t, D, F0)
        end = lambda n: 1 - ramp(n, END, 8)  # noqa: E731
        if kind.startswith("yt"):
            yt_lt(s, kind, 737, 0, 0, end)
        else:
            x0, y0 = (184, 863) if kind == "instagram" else (172, 840)
            lt_box(s, kind, x0, y0, L, end)
        return t
    make.__name__ = f"lt_{kind.replace('-', '_')}"
    return make


def social_set():
    F0, END = 400, 548
    D = (END + 9 - F0) / FPS
    t = _p("redes-tercios", "Siete tercios de redes sociales", "Seven social media lower thirds", 17040, D, "redes",
           ["redes", "tercio", "instagram", "twitter", "facebook"], thumb=D - 1.0)
    s = P(t, D, F0)
    end = lambda n: 1 - ramp(n, END, 8)  # noqa: E731
    lt_box(s, "youtube", 689, 484, 404, end)
    lt_box(s, "instagram", 116, 575, 404, end)
    lt_box(s, "nombre", 1105, 632, 404, end)
    lt_box(s, "twitter", 1106, 764, 404, end)
    lt_box(s, "facebook", 1105, 891, 404, end)
    yt_lt(s, "yt-oscuro", 409, -32, -144, end)
    yt_lt(s, "yt-blanco", 409, -32, 18, end)
    return t


# ==== 16-17. Gradient wipes (28.8-30.3 s and 30.7-31.9 s) =======================================================
BLUE_GRAD = ("#02ABFD", "#BA01FF")
GREEN_GRAD = ("#02DEFE", "#01FD84")


def capsule(s, name, ends):
    """A capsule (a pill, rounded ends) through ends(n) = (xa, ya, xb, yb, r): its two end circles' centres and
    radius, every frame. Returned solid; it is used as a matte (screen-aligned gradient on top)."""
    def g(n):
        xa, ya, xb, yb, r = ends(n)
        ln = math.hypot(xb - xa, yb - ya)
        return (xa + xb) / 2, (ya + yb) / 2, ln + 2 * r, 2 * r, math.degrees(math.atan2(yb - ya, xb - xa)), 1.0
    clip = s.sh(name, solid(WHITE), g, base=(4000, 1400))
    clip["shapeStyle"].setdefault("keyframes", {})["cornerRadius"] = keys(
        [(u, round(ends(u * FPS + s.f0)[4], 2), "linear") for u in frames_of(s.dur)])
    return clip


def through(s, name, grad, shape):
    g = s.gradrect(name, *grad)
    s.matte(g, shape)
    return g


def wipe_side():
    F0, F1 = 862, 912
    D = (F1 - F0) / FPS
    t = _p("transicion-ola", "Transición: ola azul y verde", "Transition: blue and green wave", 17050, D,
           "transiciones", ["transición", "degradado"], thumb=D * 0.5)
    s = P(t, D, F0)
    # the blue pill's right end (leading) and left end (trailing), measured on the reference
    lead = tab([(862, -1000, 120, 693), (866, -647, 298, 701), (869, -509, 386, 693), (872, -368, 482, 693),
                (875, -212, 583, 693), (878, -80, 690, 740), (881, 120, 760, 927), (884, 600, 700, 1100),
                (887, 1500, 620, 1100), (890, 2700, 540, 1100), (912, 9000, 540, 1100)])
    trail = tab([(862, -9000, 540, 1100), (889, -900, 540, 900), (891, 300, 540, 760), (893, 704, 497, 694),
                 (895, 1085, 424, 703), (897, 1496, 348, 762), (899, 1942, 263, 889), (901, 2455, 161, 1121),
                 (903, 3155, 29, 1575), (906, 4400, -100, 1700), (912, 6500, -200, 1700)])

    def blue(n):
        xa, ya, ra = trail(n)
        xb, yb, rb = lead(n)
        if n < 889:
            r = rb
            return xb - 5000, yb, xb, yb, r
        return xa, ya, xa + 6000, ya, ra
    gtrail = tab([(889, -1500, 540, 900), (893, 300, 500, 700), (895, 650, 420, 720), (897, 1015, 341, 767),
                  (899, 1524, 255, 897), (901, 2106, 152, 1134), (903, 2860, 22, 1585), (906, 4000, -100, 1700),
                  (912, 6000, -200, 1700)])

    def green(n):
        xa, ya, ra = gtrail(n)
        if n < 889:
            return -20000, 540, -19000, 540, 10
        return xa, ya, xa + 6000, ya, ra
    gm = capsule(s, "Forma verde", green)
    through(s, "Fondo verde", GREEN_GRAD, gm)
    bm = capsule(s, "Forma azul", blue)
    through(s, "Fondo azul", BLUE_GRAD, bm)
    return t


def diamond(s, name, path, S=3400, R=750):
    """A rounded square turned 45° whose bottom corner point (x, y) = path(n)."""
    d = (S / 2 - R) * math.sqrt(2) + R

    def g(n):
        x, y = path(n)
        return x, y - d, S, S, 45, 1.0
    return s.sh(name, solid(WHITE), g, radius=R, base=(S, S))


def wipe_up():
    F0, F1 = 917, 962
    D = (F1 - F0) / FPS
    t = _p("transicion-rombo", "Transición: rombo azul y verde que sube", "Transition: rising blue and green diamond",
           17051, D, "transiciones", ["transición", "degradado"], thumb=D * 0.4)
    s = P(t, D, F0)
    ext = 2 * ((3400 / 2 - 750) * math.sqrt(2) + 750)
    # blue: its top corner rises from the bottom (entry), its bottom corner leaves through the top (exit)
    top = tab([(917, 900, 1200), (921, 780, 800), (927, 1050, 300), (933, 1150, -350), (939, 1160, -1900),
               (945, 1170, 589 - ext)])
    bot = tab([(945, 1170, 589), (951, 943, 115), (957, 715, -360), (962, 530, -760)])
    blue = lambda n: (top(n)[0], top(n)[1] + ext) if n < 945 else bot(n)  # noqa: E731
    green = tab([(917, 600, 9000), (932, 1350, 2700), (935, 1350, 2300), (941, 1300, 1400), (947, 1125, 941), (951, 990, 457),
                 (955, 817, 102), (959, 650, -300), (962, 520, -560)])
    gm = diamond(s, "Forma verde", green)
    gm["opacity"] = keys([(u, 1.0 if u * FPS + F0 >= 932 else 0.0, "hold") for u in frames_of(D)])
    through(s, "Fondo verde", GREEN_GRAD, gm)
    bm = diamond(s, "Forma azul", blue)
    through(s, "Fondo azul", BLUE_GRAD, bm)
    return t


# ==== 18-20. Shape opener: gradient shapes sweep across and leave the user's logo (36.4-39.0 s, 43.4-46 s, 50-53.8 s)
RTRI = ("M 18 6 C 24 1 33 1 40 5 L 92 38 C 100 43 100 57 92 62 L 40 95 C 33 99 24 99 18 94 C 12 89 10 82 10 75 "
        "L 10 25 C 10 18 12 11 18 6 Z")  # a rounded triangle pointing right
PALETTES = {
    "oscuro": dict(bg=DARK, t1=("#9A2BFF", "#1E9BFF"), blob=("#00F59B", "#00D9E8"), dot1="#3A6BFF", dot2="#A020F0",
                   big="#00D9E8", t2=("#00F0A0", "#00DCEB"), line=("#05EAFF", "#00FA7B"), word=WHITE),
    "claro": dict(bg=WHITE, t1=("#F23A0E", "#F5A300"), blob=("#F06A10", "#F5B000"), dot1="#F59A10", dot2="#F01818",
                  big="#F5C000", t2=("#F27A10", "#FFC400"), line=("#C000C0", RED), word=INK),
    "video": dict(bg=None, t1=(WHITE, WHITE), blob=(WHITE, WHITE), dot1=WHITE, dot2=WHITE, big=WHITE,
                  t2=(WHITE, WHITE), line=("#05EAFF", "#00FA7B"), word=WHITE),
}


def shapes_logo(variant):
    F0, END = 1091, 1166
    D = (END + 9 - F0) / FPS
    pal = PALETTES[variant]
    names = {"oscuro": ("Apertura: formas que revelan tu logo (oscuro)", "Opener: shapes reveal your logo (dark)"),
             "claro": ("Apertura: formas naranjas que revelan tu logo", "Opener: orange shapes reveal your logo"),
             "video": ("Apertura: formas blancas y tu logo sobre tu video", "Opener: white shapes and your logo over "
                       "your video")}[variant]
    t = _p(f"logo-formas-{variant}", *names, 17060 + ["oscuro", "claro", "video"].index(variant), D, "aperturas",
           ["logo", "apertura", "formas"], thumb=D - 0.7)
    s = P(t, D, F0)
    out = lambda n: 1 - ramp(n, END, 8)  # noqa: E731
    if pal["bg"]:
        s.sh("Fondo", solid(pal["bg"]), lambda n: (960, 540, 1920, 1080, 0, 1))
    # the user's logo and its address, revealed behind the shapes
    logo(s, lambda v: (942, 470, 330 * eout(v * FPS, 1109, 6, 2), 0, out(v * FPS)))
    ub = ink(URL, OS, 400, 42, 942, 735, align="center")
    s.type_in(s.tx(URL, ub, OS, 400, pal["word"], "Dirección", align="center", fn=lambda n: (0, 0, 1, 0, out(n))),
              1123, 9 / FPS / len(URL), 0.15, preset="fade")
    stroke_path(s, "Dirección (raya)", [(ub[0] - 8, ub[1] + 28), (ub[2] - 40, ub[1] + 28)], 5, pal["line"][0],
                lambda v: (ramp(v * FPS, 1131, 9), eout(v * FPS, 1125, 8, 2)), smooth=False)
    stroke_path(s, "Dirección (raya 2)", [(ub[2] - 10, ub[1] + 28), (ub[2] + 30, ub[1] + 28)], 5, pal["line"][1],
                lambda v: (ramp(v * FPS, 1141, 6), eout(v * FPS, 1134, 5, 2)), smooth=False)

    def grad(c):
        return [gradient([(0.0, c[0]), (1.0, c[1])], angle=0), no_stroke()]
    # second rounded triangle (teal / orange): sweeps from the left over the logo and out to the right
    t2 = tab([(1110, -500, 450, 600, 20), (1114, 330, 435, 840, 0), (1117, 720, 390, 840, 30), (1120, 1110, 420, 840,
                                                                                                 90),
              (1123, 1440, 420, 840, 150), (1126, 1700, 420, 840, 180), (1129, 1950, 420, 840, 190),
              (1134, 2500, 420, 840, 200)])
    s.sh("Forma 4", grad(pal["t2"]), lambda n: (t2(n)[0], t2(n)[1], t2(n)[2], t2(n)[2], t2(n)[3],
                                                 1.0 if 1110 <= n < 1134 else 0.0), path=RTRI, base=(840, 840))
    # the big circle and the small dots
    big = tab([(1109, 1300, 520, 0), (1111, 1450, 510, 420), (1114, 1545, 510, 500), (1117, 1900, 500, 480),
               (1121, 2400, 500, 460)])
    s.sh("Círculo grande", solid(pal["big"]), lambda n: (big(n)[0], big(n)[1], big(n)[2], big(n)[2], 0,
                                                        1.0 if 1109 <= n < 1121 else 0.0), kind="ellipse",
         base=(500, 500))
    dot = tab([(1103, 120, 360, 0), (1105, 120, 360, 250), (1108, 750, 288, 252), (1111, 1248, 252, 240),
               (1114, 1608, 270, 240), (1118, 2150, 270, 240)])
    dot = (lambda f: lambda n: f(n - 3))(dot)  # the reference is 3 frames later than measured
    s.sh("Punto", solid(pal["dot1"]), lambda n: (dot(n)[0], dot(n)[1], dot(n)[2], dot(n)[2], 0,
                                                 1.0 if 1103 <= n < 1107 else 0.0), kind="ellipse", base=(250, 250))
    s.sh("Punto 2", solid(pal["dot2"]), lambda n: (dot(n)[0], dot(n)[1], dot(n)[2], dot(n)[2], 0,
                                                   1.0 if 1107 <= n < 1118 else 0.0), kind="ellipse", base=(250, 250))
    # the blob, then the first big rounded triangle on top
    blob = tab([(1100, 300, 1000, 0, 0), (1102, 420, 900, 260, 10), (1105, 420, 820, 560, 20),
                (1108, 760, 690, 700, 40), (1111, 1180, 560, 740, 60), (1114, 1700, 520, 700, 80),
                (1118, 2400, 500, 680, 90)])
    blob = (lambda f: lambda n: f(n - 3))(blob)  # the reference is 3 frames later than measured
    s.sh("Forma 2", grad(pal["blob"]), lambda n: (blob(n)[0], blob(n)[1], blob(n)[2], blob(n)[2] * 0.62,
                                                  blob(n)[3], 1.0 if 1100 <= n < 1118 else 0.0), kind="ellipse",
         base=(740, 460))
    t1 = tab([(1091, -700, 520, 900, -55), (1093, -420, 520, 950, -50), (1096, -50, 480, 1050, -40),
              (1099, 330, 470, 1150, -30), (1102, 700, 430, 1200, -20), (1105, 1100, 420, 1200, -5),
              (1108, 1480, 420, 1200, 10), (1111, 1850, 420, 1150, 20), (1115, 2600, 420, 1100, 30)])
    t1 = (lambda f: lambda n: f(n - 3))(t1)  # the reference is 3 frames later than measured
    s.sh("Forma 1", grad(pal["t1"]), lambda n: (t1(n)[0], t1(n)[1], t1(n)[2], t1(n)[2], t1(n)[3],
                                                 1.0 if n < 1115 else 0.0), path=RTRI, base=(1200, 1200))
    return t


def shapes_dark():
    return shapes_logo("oscuro")


def shapes_light():
    return shapes_logo("claro")


def shapes_video():
    return shapes_logo("video")


# ==== 21. «enjoy» (53.9-57 s) =====================================================================================
def enjoy():
    F0, END = 1616, 1700
    D = (END + 10 - F0) / FPS
    t = _p("disfruta", "Cierre: enjoy", "Closing: enjoy", 17070, D, "tipografia", ["cierre", "texto"], thumb=1.5)
    s = P(t, D, F0)
    s.sh("Fondo", solid(WHITE), lambda n: (960, 540, 1920, 1080, 0, 1))
    b = ink("enjoy", RB, 700, 54, 960, 503, align="center")
    c = s.tx("enjoy", b, RB, 700, "#222222", "Texto", align="center",
             fn=lambda n: (0, 0, 1, 0, 1 - ramp(n, END, 10)))
    s.type_in(c, 1619, 0.0, 0.2, preset="fade")
    return t


TEMPLATES = [logo_light, logo_dark, logo_video, like_dark, like_white, sub_white, sub_dark,
             lower_third("nombre", 17030), lower_third("instagram", 17031), lower_third("twitter", 17032),
             lower_third("facebook", 17033), lower_third("youtube", 17034), lower_third("yt-oscuro", 17035),
             lower_third("yt-blanco", 17036), social_set, wipe_side, wipe_up, shapes_dark, shapes_light, shapes_video, enjoy]
