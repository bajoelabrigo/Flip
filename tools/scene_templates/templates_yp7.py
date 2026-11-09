"""YOUTUBE PACK video 7 as Stock templates (yp7-*). See docs/plan-youtube-pack.md.

The black-and-white fashion YouTube pack of «pack youtube 7.mp4» (960×540 at 30 fps, laid out at 1920×1080): logo
openers, phone scenes, subscribe cards, typography, icons, social cards, handwritten extras, elements, transitions
and end cards. The element list comes from the labelled 2×2 grids of the second half (1:50-3:53); looks and moves
from the full-screen uses of the first half, studied on 10 fps sheets. Study notes in
tienda/plantillas/estudio-pack-youtube-7/NOTAS.md.

Unlike the title sets, each piece plays forward in time (frame = u × FPS) and has its own exit, as the reference.
Pieces that sit on footage keep a transparent background; openers and the phone scenes bring a «Tu video» slot.
"""

from __future__ import annotations

import math
import os

import templates_llt_f as f6
from kit import Box, label, wide
from llt_motion import frames_of, mask_track
from scene import keys, tanim
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_f import outline_layers
from templates_tit_h import S, arc, fill, lin, poly, ring, rot_pt

WHITE, BLACK, RED = "#FFFFFF", "#000000", "#FF0000"
DARK, GREY = "#222222", "#9A9A9A"
M, P = "Montserrat", "Poppins"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
    f6._FILES[(P, _w)] = f"fonts.basic/fonts/poppins/Poppins-{_f}.ttf"
for _w, _f in ((400, "Regular"), (500, "Medium"), (700, "Bold")):
    f6._FILES[("Roboto", _w)] = f"fonts.basic/fonts/roboto/Roboto-{_f}.ttf"
f6._FILES[(P, 701)] = "fonts.basic/fonts/poppins/Poppins-BoldItalic.ttf"
f6._FILES[("Caveat", 400)] = "fonts.basic/fonts/caveat/Caveat-Regular.ttf"
f6._FILES[("Shadows Into Light", 400)] = "fonts.extra/fonts/shadowsintolight/ShadowsIntoLight-Regular.ttf"

CHANNEL = "Your Channel"
SUB = "Your favourite youtube channel"
VIDEO, VIDEO2, AVATAR = "fx-hair-02", "fx-hair-05", "fx-woman-08"
BELL = (poly([(50, 4), (60, 10), (68, 26), (70, 56), (84, 74), (84, 80), (16, 80), (16, 74), (30, 56), (32, 26),
              (40, 10)]) + " " + poly([(40, 84), (60, 84), (56, 95), (44, 95)]))
THUMB = (poly([(6, 44), (26, 44), (26, 96), (6, 96)]) + " " +
         poly([(32, 44), (52, 8), (64, 12), (60, 38), (92, 38), (96, 50), (86, 96), (32, 96)]))
SHARE = poly([(0, 100), (10, 55), (40, 35), (60, 35), (60, 10), (100, 50), (60, 90), (60, 62), (40, 62), (15, 75)])
TRIANGLE = "M 0 0 L 100 50 L 0 100 Z"
HAND = poly([(30, 0), (42, 0), (44, 42), (56, 38), (68, 42), (80, 46), (92, 54), (94, 80), (84, 100), (40, 100),
             (12, 70), (4, 56), (10, 50), (30, 64)])


def _p(id, es, en, order, dur, section, tags=()):
    return wide(f"yp7-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube", "blanco y negro", "moda"] + list(tags),
                thumb_at=round(dur * 0.5, 1))


def stroke_fill(colour, line, width):
    return [fill(colour)] + [ring(line, width)[1]]


class Y(S):
    """A piece that plays forward: frame = u × FPS. Exits are written per element."""

    def frame(self, u):
        return u * FPS

    def typed(self, clip, at, stagger=0.06, duration=0.05, preset="typewriter", order="forward", unit="character",
              **kw):
        clip["textStyle"]["animation"] = {
            "in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut",
                        delay=round(at / FPS, 3), order=order, **kw)}

    def spacing(self, clip, fn):
        """Letter spacing (px) per frame."""
        clip["textStyle"]["wordWrap"] = False
        clip["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
            [(u, round(fn(fr), 3), "linear") for u, fr in self.each()])

    def pic(self, name, sample, geom, label="Tu foto", base=(1920, 1080), **kw):
        """A photo slot whose geom(fr, u) = (cx, cy, w, h, rot, opacity) every frame (cover crop)."""
        bw, bh = base
        g = [(u, geom(fr, u)) for u, fr in self.each()]
        motion = [(u, {"sx": max(1e-4, v[2] / bw), "sy": max(1e-4, v[3] / bh), "dx": v[0] - 960, "dy": v[1] - 540},
                   "linear") for u, v in g]
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, Box(960 - bw / 2, 540 - bh / 2, bw, bh),
                            motion, label=label, **kw)
        if any(abs(v[4]) > 1e-6 for _, v in g):
            clip["rotation"] = keys([(u, round(v[4], 3), "linear") for u, v in g])
        if any(v[5] < 0.999 for _, v in g):
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[5])), 4), "linear") for u, v in g])
        return clip

    def video(self, geom=None, sample=VIDEO, name="Tu video"):
        return self.pic(name, sample, geom or (lambda fr, u: (960, 540, 1920, 1080, 0, 1)), label="Tu video")

    def clipped(self, clip, rect):
        """Clip `clip` to the screen rect(fr) = (x0, y0, x1, y1), following the clip's own (moving) box."""
        frames = frames_of(self.dur)
        def series(prop):
            ks = clip[prop]["keyframes"]
            return [kf["value"] for kf in ks] if len(ks) == len(frames) else [ks[0]["value"]] * len(frames)
        xs, ys, ws, hs = series("x"), series("y"), series("width"), series("height")
        track = next(tr for tr in self.t.tracks if clip in tr.clips)
        mk = {"x": [], "y": [], "w": [], "h": []}
        for i, u in enumerate(frames):
            x0, y0, x1, y1 = rect(self.frame(u))
            bx, by, bw, bh = xs[i], ys[i], max(1e-3, ws[i]), max(1e-3, hs[i])
            mk["x"].append((u, ((x0 + x1) / 2 - bx) / bw, "linear"))
            mk["y"].append((u, ((y0 + y1) / 2 - by) / bh, "linear"))
            mk["w"].append((u, max(0.0, x1 - x0) / bw, "linear"))
            mk["h"].append((u, max(0.0, y1 - y0) / bh, "linear"))
        self.t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
                    keyframes={kk: keys(v) for kk, v in mk.items()})


def step(fr, pts):
    """Piecewise smooth: pts = [(frame, value), ...] eased between."""
    if fr <= pts[0][0]:
        return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if fr <= b:
            return va + (vb - va) * k(fr, a, b - a)
    return pts[-1][1]


# ==== LOGO OPENER ==================================================================================================

def card_contents(s, y_of, show, avatar_at, spaced=True, cx=960, op=lambda fr: 1.0, name_y=630):
    """The opener card: avatar above, letter-spaced channel name and its line (LO3, LO4)."""
    s.pic("Foto de perfil", AVATAR, lambda fr, u: (cx, 500 + y_of(fr), 132, 132, 0, show(fr) * op(fr)),
          label="Tu foto de perfil", base=(132, 132))
    nm = s.say(CHANNEL.upper(), (cx - 200, name_y, cx + 200, name_y + 20), M, 500, WHITE, "Canal",
               geom=lambda fr, u: (0, y_of(fr), 1, 0, k(fr, avatar_at, 4) * op(fr)))
    if spaced:
        s.spacing(nm, lambda fr: 2 + 8 * k(fr, avatar_at, 15))
    s.say(SUB, (cx - 120, name_y + 40, cx + 120, name_y + 52), M, 500, "#BBBBBB", "Texto",
          geom=lambda fr, u: (0, y_of(fr), 1, 0, k(fr, avatar_at + 9, 6) * op(fr)))


# --- LO1: a red bar opens into a square, the black opens to a dark box, the square becomes the avatar ---------------
def opener_red():
    D = 5.0
    t = _p("apertura-cuadro-rojo", "Apertura: cuadro rojo y tarjeta del canal", "Opener: red square and channel card",
           13300, D, "aperturas", ["logo", "apertura"])
    s = Y(t, D)
    s.video()
    out = lambda fr: 1200 * k(fr, 130, 12)  # noqa: E731

    def box(fr, u):
        q = k(fr, 33, 21)
        w, h = 1920 - 480 * q, 1080 - 270 * q
        return 960, 540 + out(fr), w, h, 0, 1
    bx = s.obj("Caja", solid(BLACK), box)
    bx["shapeStyle"]["keyframes"] = {}
    bx["opacity"] = keys([(u, round(1 - 0.45 * k(fr, 33, 21), 4), "linear") for u, fr in s.each()])

    def sq(fr, u):
        w = step(fr, [(0, 6), (12, 170), (15, 40), (19, 170)])
        size = 170 - 38 * k(fr, 36, 18)
        cx = 960 - 192 * k(fr, 36, 18)
        return cx, 540 + out(fr), size if fr > 20 else w, size, 0, min(1.0, fr / 3)
    s.obj("Cuadro rojo", solid(RED), sq)
    s.pic("Foto de perfil", AVATAR, lambda fr, u: (sq(fr, u)[0], 540 + out(fr), 132, 132, 0, k(fr, 39, 12)),
          label="Tu foto de perfil", base=(132, 132))
    s.say(CHANNEL, (850, 512, 1150, 534), M, 700, WHITE, "Canal",
          geom=lambda fr, u: (0, out(fr), 1, 0, k(fr, 42, 12)))
    s.say(SUB, (850, 548, 1110, 560), M, 500, "#BBBBBB", "Texto",
          geom=lambda fr, u: (0, out(fr), 1, 0, k(fr, 48, 12)))
    return t


# --- LO2: YOUTUBE drawn letter by letter in outline, filled, pulled back, then a turning square closes it ----------
def opener_youtube():
    D = 5.0
    t = _p("apertura-youtube", "Apertura: YOUTUBE en contorno que se rellena", "Opener: outlined YOUTUBE that fills",
           13301, D, "aperturas", ["youtube", "apertura"])
    s = Y(t, D)
    s.video()
    end = 126
    shrink = lambda fr: 1 - k(fr, end, 22)  # noqa: E731
    turn = lambda fr: -35 * k(fr, end, 22)  # noqa: E731
    s.obj("Fondo", solid(BLACK), lambda fr, u: (960, 540, 2300 * shrink(fr) if fr > end else 2300,
                                                2300 * shrink(fr) if fr > end else 2300, turn(fr),
                                                1 - 0.35 * k(fr, 0, 30)))
    ink = (365, 445, 1555, 640)
    big = lambda fr: 1.33 - 0.33 * k(fr, 54, 21)  # noqa: E731

    def geo(op=lambda fr: 1.0, ink=ink):
        def g(fr, u):
            sc = big(fr) * shrink(fr)
            dx, dy = s.about(ink, 960, 540, sc, turn(fr))
            return dx, dy, sc, turn(fr), op(fr)
        return g
    c = s.say("YOUTUBE", ink, M, 900, GREY, "Título (contorno)", layers=outline_layers("#8C8C8C", 3), geom=geo(),
              editable=False)
    s.typed(c, 0, stagger=0.19, duration=0.25, preset="fade")
    c = s.say("YOUTUBE", ink, M, 900, "#C9C9C9", "Título", geom=geo())
    s.typed(c, 33, stagger=0.12, duration=0.18, preset="fade")
    sub = (460, 664, 1460, 686)
    s.say("YOUR FAVOURITE YOUTUBE CHANNEL", sub, M, 500, "#A0A0A0", "Texto",
          geom=geo(lambda fr: k(fr, 69, 9), sub))
    return t


# --- LO3: the shot turns and shrinks into the avatar, the name spreads, the black opens to a dark box -------------
def opener_avatar():
    D = 5.0
    t = _p("apertura-foto-perfil", "Apertura: la toma se vuelve foto de perfil", "Opener: shot turning into the avatar",
           13302, D, "aperturas", ["logo", "apertura"])
    s = Y(t, D)
    s.video(sample=VIDEO2, name="Tu video 2")
    out = lambda fr: 1100 * k(fr, 132, 12)  # noqa: E731

    def box(fr, u):
        q = k(fr, 30, 15)
        return 960, 540 + out(fr), 1920 - 480 * q, 1080 - 270 * q, 0, 1 - 0.45 * q
    s.obj("Caja", solid(BLACK), box)

    def av(fr, u):
        q = k(fr, 0, 15)
        w, h = 1920 + (132 - 1920) * q, 1080 + (132 - 1080) * q
        return 960, 540 - 40 * q + out(fr), w, h, -30 * math.sin(math.pi * min(1, fr / 15)), 1
    s.pic("Foto de perfil", VIDEO, av, label="Tu foto de perfil", base=(132, 132))
    s.say(CHANNEL.upper(), (760, 630, 1160, 650), M, 500, WHITE, "Canal",
          geom=lambda fr, u: (0, out(fr), 1, 0, k(fr, 15, 4)))
    nm = s.t.tracks[-1].clips[-1]
    s.spacing(nm, lambda fr: 2 + 8 * k(fr, 15, 15))
    s.say(SUB, (840, 670, 1080, 682), M, 500, "#BBBBBB", "Texto",
          geom=lambda fr, u: (0, out(fr), 1, 0, k(fr, 27, 6)))
    return t


# --- LO4: YOU ARE AWESOME / GET READY FOR AWESOME in white and black panels that drop in, then the card -----------
def opener_words():
    D = 5.6
    t = _p("apertura-palabras", "Apertura: palabras en paneles blanco y negro", "Opener: words on black and white panels",
           13303, D, "aperturas", ["palabras", "apertura"])
    s = Y(t, D)
    s.video(sample=VIDEO2, name="Tu video")
    words = ["YOU", "ARE", "AWESOME", "GET", "READY", "FOR", "AWESOME"]
    every = 10
    last = every * len(words)
    s.rect("Fondo", solid(BLACK), lambda fr, u: (-10, -10, 1930, 1090) if fr < 6 else (0, 0, 0, 0))
    for i, w in enumerate(words):
        at = i * every
        bg, ink = (WHITE, BLACK) if i % 2 == 0 else (BLACK, WHITE)
        gone = last + 4

        def panel(fr, u, at=at, gone=gone):
            y = -1080 * (1 - k(fr, at, 4))
            return (0, y, 1920, y + 1080) if fr < gone else (0, 0, 0, 0)
        s.rect(f"Panel {i + 1}", solid(bg), panel)
        s.say(w, (160, 470, 1760, 610), M, 900, ink, f"Palabra {i + 1}" if i else "Título",
              reveal=lambda fr: (0, 470, 1920, 610), shift=lambda fr, at=at: (0, 90 * (1 - k(fr, at + 1, 5))),
              op=lambda fr, u, at=at, gone=gone: (1.0 if at <= fr < gone + (every if False else 0) else 0.0)
              if fr < at + every + 4 or at == last - every else 0.0)
    # the last white panel is pushed up by the dark card that opens from the bottom
    out = lambda fr: 1100 * k(fr, 150, 12)  # noqa: E731

    def card(fr, u):
        q = k(fr, last + 4, 15)
        if fr < last:
            return 0, 0, 0, 0, 0, 0
        y0 = 1080 - 1080 * k(fr, last, 5)
        w, h = 1920 - 480 * q, 1080 - 270 * q
        return 960, max(540, y0 + 540) + out(fr), w, h, 0, 1 - 0.5 * q
    s.obj("Caja", solid(BLACK), card)
    show = lambda fr: 1.0 if fr >= last + 6 else 0.0  # noqa: E731
    card_contents(s, out, show, last + 8)
    return t


# ==== PHONE SCENE ==================================================================================================

def phone(s, cx, tag):
    """A phone showing a video page; the shot zooms out into it, a hand likes, subscribes and rings the bell, and
    the camera pushes back into the video."""
    vx0, vy0, vx1, vy1 = cx - 186, 150, cx + 186, 360
    vcx, vcy = cx, (vy0 + vy1) / 2
    Z = 1920 / (vx1 - vx0)
    zin = lambda fr: k(fr, 0, 33)  # noqa: E731
    zout = lambda fr: k(fr, 270, 21)  # noqa: E731
    zf = lambda fr: Z + (1 - Z) * zin(fr) + (Z - 1) * zout(fr)  # noqa: E731

    def P(x, y, fr):
        z = zf(fr)
        a = (z - 1) / (Z - 1)
        ax, ay = vcx + a * (960 - vcx), vcy + a * (540 - vcy)
        return ax + (x - vcx) * z, ay + (y - vcy) * z

    def at(x0, y0, x1, y1, op=lambda fr: 1.0, rot=0.0):
        def g(fr, u):
            z = zf(fr)
            px, py = P((x0 + x1) / 2, (y0 + y1) / 2, fr)
            return px, py, (x1 - x0) * z, (y1 - y0) * z, rot, op(fr)
        return g

    def tx(ink, op=lambda fr: 1.0):
        def g(fr, u):
            z = zf(fr)
            px, py = P((ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2, fr)
            return px - (ink[0] + ink[2]) / 2, py - (ink[1] + ink[3]) / 2, z, 0, op(fr)
        return g
    s.obj("Teléfono", solid("#1B1B1B"), at(cx - 206, 110, cx + 206, 990), radius=56, base=(412, 880))
    s.obj("Pantalla", solid(WHITE), at(cx - 188, 128, cx + 188, 972), radius=40, base=(376, 844))
    s.obj("Barra de estado", solid("#ECECEC"), at(cx - 186, 136, cx + 186, 150))
    ink = "#202020"

    def say(text, x0, y0, y1, weight=400, colour=ink, name="Texto", x1=None, op=lambda fr: 1.0, align="left"):
        x1 = x1 or x0 + 0.75 * (y1 - y0) * len(text)
        c = s.say(text, (x0, y0, x1, y1), "Roboto", weight, colour, name, align=align, geom=tx((x0, y0, x1, y1), op))
        return c
    say("10 super awesome video", cx - 172, 377, 390, name="Título del video")
    say("Your video title", cx - 172, 395, 408, name="Título del video 2")
    say("96K views", cx - 172, 421, 430, colour="#777777", name="Vistas")
    liked = lambda fr: k(fr, 99, 3)  # noqa: E731
    icons = [("Me gusta", THUMB, "539"), ("No me gusta", THUMB, "54"), ("Compartir", SHARE, "Share"),
             ("Descargar", None, "Download"), ("Guardar", None, "Add to")]
    for i, (nm, path, label) in enumerate(icons):
        x = cx - 140 + 70 * i
        rot = 180.0 if i == 1 else 0.0
        if path:
            s.obj(nm, solid("#606060"), at(x - 11, 444, x + 11, 466, rot=rot), path=path)
        elif i == 3:
            s.obj(nm, solid("#606060"), at(x - 11, 444, x + 11, 466), kind="ellipse")
        else:
            s.obj(nm, solid("#606060"), at(x - 11, 452, x + 7, 456))
            s.obj(f"{nm} 2", solid("#606060"), at(x - 4, 445, x, 463))
        say(label, x - 30, 474, 482, colour="#606060", name=f"{nm} (texto)", x1=x + 30, align="center")
    s.obj("Me gusta (hecho)", solid("#202020"), at(cx - 151, 444, cx - 129, 466, op=liked), path=THUMB)
    s.obj("Línea", solid("#E4E4E4"), at(cx - 186, 496, cx + 186, 498))
    av = s.pic("Foto de perfil", AVATAR, at(cx - 172, 510, cx - 136, 546), label="Tu foto de perfil", base=(36, 36))
    s.t.mask(s.t.tracks[-1], av, "ellipse")
    say(CHANNEL, cx - 124, 514, 527, name="Canal")
    say("109K subscribers", cx - 124, 535, 543, colour="#777777", name="Suscriptores")
    sub = lambda fr: k(fr, 168, 2)  # noqa: E731
    s.obj("Botón rojo", solid(RED), at(cx + 60, 521, cx + 80, 535, op=lambda fr: 1 - sub(fr)), radius=3, base=(20, 14))
    s.obj("Botón rojo (play)", solid(WHITE), at(cx + 67, 525, cx + 74, 531, op=lambda fr: 1 - sub(fr)), path=TRIANGLE)
    say("SUBSCRIBE", cx + 86, 522, 534, weight=700, colour=RED, name="Suscribirse", op=lambda fr: 1 - sub(fr))
    s.obj("Botón gris", solid("#9E9E9E"), at(cx + 40, 521, cx + 60, 535, op=sub), radius=3, base=(20, 14))
    say("SUBSCRIBED", cx + 66, 522, 534, weight=700, colour="#7A7A7A", name="Suscrito", op=sub)
    s.obj("Campana", solid("#606060"), at(cx + 160, 518, cx + 178, 538, op=sub), path=BELL)
    s.obj("Línea 2", solid("#E4E4E4"), at(cx - 186, 560, cx + 186, 562))
    say("Up next", cx - 172, 578, 588, colour="#606060", name="A continuación")
    say("Autoplay", cx + 50, 578, 590, colour="#606060", name="Reproducción automática")
    s.obj("Interruptor", solid("#A8C7FA"), at(cx + 128, 578, cx + 160, 590), radius=6, base=(32, 12))
    s.obj("Interruptor (botón)", solid("#3E82F7"), at(cx + 146, 574, cx + 166, 594), kind="ellipse")
    for j, y in enumerate((612, 712)):
        s.pic(f"Miniatura {j + 1}", ["fx-face-03", "fx-face-05"][j], at(cx - 176, y, cx - 26, y + 84),
              label=f"Tu miniatura {j + 1}", base=(150, 84))
        say("10 super awesome", cx - 14, y + 4, y + 16, weight=700, name=f"Video {j + 1}")
        say("video | Your video title", cx - 14, y + 22, y + 34, weight=700, name=f"Video {j + 1} (título)")
        say(CHANNEL, cx - 14, y + 42, y + 52, colour="#777777", name=f"Video {j + 1} (canal)")
        say("68K views", cx - 14, y + 58, y + 66, colour="#777777", name=f"Video {j + 1} (vistas)")
    s.pic("Video del teléfono", VIDEO, at(vx0, vy0, vx1, vy1), label="Tu video", base=(372, 210))
    word = s.say(tag, (vcx - 120, vcy - 14, vcx + 120, vcy + 14), M, 400, WHITE, "Título en el video",
                 geom=tx((vcx - 120, vcy - 14, vcx + 120, vcy + 14), lambda fr: k(fr, 36, 9)))
    s.spacing(word, lambda fr: 12)

    # the hand: in from the bottom right, taps like, subscribe, then the bell
    path = [(0, cx + 260, 900), (60, cx + 260, 900), (90, cx - 138, 470), (102, cx - 138, 470),
            (150, cx + 110, 540), (170, cx + 110, 540), (210, cx + 170, 542), (240, cx + 170, 542),
            (262, cx + 300, 760)]

    def hand_xy(fr):
        if fr <= path[0][0]:
            return path[0][1:]
        for (a, xa, ya), (b, xb, yb) in zip(path, path[1:]):
            if fr <= b:
                q = k(fr, a, b - a)
                return xa + (xb - xa) * q, ya + (yb - ya) * q
        return path[-1][1:]

    def ripple(t0):
        def g(fr, u):
            x, y = hand_xy(fr)
            q = lin(fr, t0, 9)
            z = zf(fr)
            px, py = P(x, y, fr)
            return px, py, 40 * q * z, 40 * q * z, 0, 0.7 * (1 - q) if t0 <= fr < t0 + 9 else 0
        return g
    for i, t0 in enumerate((96, 164, 230)):
        s.obj(f"Toque {i + 1}", solid("#3E82F7"), ripple(t0), kind="ellipse")

    def hand(fr, u):
        x, y = hand_xy(fr)
        press = 0.85 if any(t0 <= fr < t0 + 4 for t0 in (96, 164, 230)) else 1.0
        z = zf(fr)
        px, py = P(x + 8, y + 22, fr)
        return px, py, 36 * press * z, 48 * press * z, 0, k(fr, 60, 4) * (1 - k(fr, 255, 6))
    s.obj("Mano", stroke_fill(WHITE, BLACK, 2.5), hand, path=HAND, base=(36, 48))


def phone_center():
    D = 10.0
    t = _p("telefono", "Escena: teléfono con me gusta y suscribirse", "Scene: phone with like and subscribe", 13304, D,
           "elementos", ["teléfono", "suscribirse"])
    s = Y(t, D)
    s.video(sample=VIDEO2, name="Fondo (video)")
    phone(s, 960, "CLARA")
    return t


def phone_left():
    D = 10.0
    t = _p("telefono-izquierda", "Escena: teléfono a la izquierda", "Scene: phone on the left", 13305, D, "elementos",
           ["teléfono", "suscribirse"])
    s = Y(t, D)
    s.video(sample=VIDEO2, name="Fondo (video)")
    phone(s, 403, "CLARA")
    return t


# ==== SUBSCRIBE CARD ===============================================================================================

def sub_buttons(s, x, y0, y1, click, out, like=None, bell_x=None, op=lambda fr: 1.0):
    """Red SUBSCRIBE that flashes pink when clicked and turns into a white SUBSCRIBED; the bell box (and LIKE) pop."""
    h = y1 - y0
    w = 253 if like is None else 247
    pre = lambda fr: (1 - k(fr, click + 4, 3))  # noqa: E731
    s.rect("Suscribirse", solid(RED), lambda fr, u: (x + w - w * k(fr, 18, 9) + out(fr)[0], y0 + out(fr)[1],
                                                     x + w + out(fr)[0], y1 + out(fr)[1]),
           op=lambda fr, u: pre(fr) * op(fr))
    s.rect("Suscribirse (clic)", solid("#F48A8A"), lambda fr, u: (x + out(fr)[0], y0 + out(fr)[1], x + w + out(fr)[0],
                                                                  y1 + out(fr)[1]),
           op=lambda fr, u: k(fr, click, 2) * pre(fr) * op(fr))
    s.say("SUBSCRIBE", (x + 70, y0 + h * 0.36, x + w - 70, y1 - h * 0.36), M, 700, WHITE, "Suscribirse (texto)",
          geom=lambda fr, u: (out(fr)[0], out(fr)[1], 1, 0, k(fr, 24, 4) * pre(fr) * op(fr)))
    s.rect("Suscrito", solid(WHITE), lambda fr, u: (x + out(fr)[0], y0 + out(fr)[1], x + w + out(fr)[0],
                                                    y1 + out(fr)[1]),
           op=lambda fr, u: k(fr, click + 4, 3) * op(fr))
    s.say("SUBSCRIBED", (x + 62, y0 + h * 0.37, x + w - 62, y1 - h * 0.37), M, 700, BLACK, "Suscrito (texto)",
          geom=lambda fr, u: (out(fr)[0], out(fr)[1], 1, 0, k(fr, click + 4, 3) * op(fr)))
    nx = x + w + 20
    if like is not None:
        lw = 147
        s.rect("Me gusta", solid(WHITE), lambda fr, u: (nx + out(fr)[0], y0 + out(fr)[1],
                                                        nx + lw * k(fr, click + 2, 6) + out(fr)[0], y1 + out(fr)[1]),
               op=lambda fr, u: op(fr))
        s.obj("Me gusta (icono)", solid(BLACK), lambda fr, u: (nx + 52 + out(fr)[0], (y0 + y1) / 2 + out(fr)[1],
                                                                h * 0.3, h * 0.3, 0, k(fr, click + 6, 3) * op(fr)),
              path=THUMB)
        s.say("LIKE", (nx + 66, y0 + h * 0.37, nx + 108, y1 - h * 0.37), M, 700, BLACK, "Me gusta (texto)",
              geom=lambda fr, u: (out(fr)[0], out(fr)[1], 1, 0, k(fr, click + 6, 3) * op(fr)))
        nx += lw + 20
    bx = bell_x or nx
    s.rect("Campana (caja)", solid(WHITE), lambda fr, u: (bx + out(fr)[0], y0 + out(fr)[1] + h / 2 * (1 - k(fr, click + 4, 6)),
                                                          bx + h + out(fr)[0], y1 + out(fr)[1] - h / 2 * (1 - k(fr, click + 4, 6))),
           op=lambda fr, u: op(fr))
    s.obj("Campana", solid(BLACK), lambda fr, u: (bx + h / 2 + out(fr)[0], (y0 + y1) / 2 + out(fr)[1], h * 0.42,
                                                  h * 0.42, 0, k(fr, click + 8, 3) * op(fr)), path=BELL)


def subscribe_bar():
    D = 5.0
    t = _p("suscribirse-barra", "Suscribirse: barra con foto de perfil", "Subscribe: bar with avatar", 13306, D,
           "barras-info", ["suscribirse"])
    s = Y(t, D)
    end = 126
    w = lambda fr: 1253 * k(fr, 3, 12) * (1 - k(fr, end, 12)) + 74  # noqa: E731
    gone = lambda fr: 1 - k(fr, end + 9, 6)  # noqa: E731
    s.obj("Barra", solid("#111111", 0.85), lambda fr, u: (973, 533, w(fr), 200, 0, k(fr, 0, 3) * gone(fr)))
    show = lambda fr: k(fr, 9, 6) * (1 - k(fr, end - 3, 4))  # noqa: E731
    s.pic("Foto de perfil", AVATAR, lambda fr, u: (453, 533, 107, 107, 0, show(fr)), label="Tu foto de perfil",
          base=(107, 107))
    s.say(CHANNEL, (527, 500, 800, 524), M, 700, WHITE, "Canal", align="left",
          geom=lambda fr, u: (-30 * (1 - k(fr, 9, 9)), 0, 1, 0, show(fr)))
    s.say(SUB, (527, 544, 780, 556), M, 500, "#AAAAAA", "Texto", align="left",
          geom=lambda fr, u: (-30 * (1 - k(fr, 12, 9)), 0, 1, 0, show(fr)))
    sub_buttons(s, 1200, 493, 567, 48, lambda fr: (0, 0), bell_x=1473, op=show)
    return t


def subscribe_photo():
    D = 5.0
    t = _p("suscribirse-tarjeta", "Suscribirse: tarjeta con foto", "Subscribe: card with photo", 13307, D,
           "barras-info", ["suscribirse"])
    s = Y(t, D)
    end = 126
    w = lambda fr: 1173 * k(fr, 3, 12) * (1 - k(fr, end, 12)) + 74  # noqa: E731
    gone = lambda fr: 1 - k(fr, end + 9, 6)  # noqa: E731
    s.obj("Tarjeta", solid("#111111", 0.85), lambda fr, u: (970, 533, w(fr), 373, 0, k(fr, 0, 3) * gone(fr)))
    show = lambda fr: k(fr, 9, 6) * (1 - k(fr, end - 3, 4))  # noqa: E731
    s.rect("Marco de la foto", solid(WHITE), lambda fr, u: (360, 360, 360 + 600 * k(fr, 6, 9), 713),
           op=lambda fr, u: 1 - k(fr, end - 3, 6))
    ph = s.pic("Foto", "fx-face-03", lambda fr, u: (660, 537, 574, 327, 0, 1), base=(574, 327))
    mask_track(s.t, ph, Box(373, 373, 574, 327), lambda u: (373, 373, 373 + 574 * k(s.frame(u), 9, 9)
                                                             * (1 - k(s.frame(u), end - 3, 6)), 700), D)
    s.say(CHANNEL, (1020, 440, 1300, 464), M, 700, WHITE, "Canal", align="left",
          geom=lambda fr, u: (-30 * (1 - k(fr, 12, 9)), 0, 1, 0, show(fr)))
    s.say(SUB, (1020, 486, 1270, 498), M, 500, "#AAAAAA", "Texto", align="left",
          geom=lambda fr, u: (-30 * (1 - k(fr, 15, 9)), 0, 1, 0, show(fr)))
    sub_buttons(s, 1020, 547, 613, 54, lambda fr: (0, 0), like=True, op=show)
    return t


def subscribe_band(photo):
    D = 5.5
    id_, es, en = (("suscribirse-banda-foto", "Suscribirse: banda inferior con foto", "Subscribe: bottom band with photo")
                   if photo else ("suscribirse-banda", "Suscribirse: banda inferior", "Subscribe: bottom band"))
    t = _p(id_, es, en, 13309 if photo else 13308, D, "barras-info", ["suscribirse", "banda"])
    s = Y(t, D)
    end = 141
    rise = lambda fr: 200 * k(fr, 0, 12) * (1 - k(fr, end + 6, 9))  # noqa: E731
    inset = lambda fr: 193 * k(fr, 24, 9) * (1 - k(fr, end, 6))  # noqa: E731
    s.rect("Banda", solid("#111111", 0.9), lambda fr, u: (inset(fr), 1080 - rise(fr), 1920 - inset(fr), 1080))
    show = lambda fr: k(fr, 33, 6) * (1 - k(fr, end - 6, 6))  # noqa: E731
    if photo:
        ph = s.pic("Foto", "fx-face-05", lambda fr, u: (360, 980, 334, 200, 0, show(fr)), base=(334, 200))
        del ph
        x = 560
    else:
        s.pic("Foto de perfil", AVATAR, lambda fr, u: (317, 980, 100, 100, 0, show(fr)), label="Tu foto de perfil",
              base=(100, 100))
        x = 407
    s.say(CHANNEL, (x, 955, x + 270, 979), M, 700, WHITE, "Canal", align="left",
          geom=lambda fr, u: (-30 * (1 - k(fr, 33, 9)), 0, 1, 0, show(fr)))
    s.say(SUB, (x, 997, x + 250, 1009), M, 500, "#AAAAAA", "Texto", align="left",
          geom=lambda fr, u: (-30 * (1 - k(fr, 36, 9)), 0, 1, 0, show(fr)))
    if photo:
        sub_buttons(s, 1213, 947, 1013, 69, lambda fr: (0, 0), like=True, op=show)
    else:
        sub_buttons(s, 1313, 947, 1027, 69, lambda fr: (0, 0), bell_x=1580, op=show)
    return t


# ==== TYPOGRAPHY ===================================================================================================
# These play the entrance, hold, and leave with the entrance backwards at 2.5× (as S).

class YR(Y):
    frame = S.frame
    typed = S.typed


def dur_r(entrance, hold=2.4):
    return round(entrance + hold + entrance / 2.5, 1)


def para(s, content, x, top, size, colour, name, weight=400, line=0.9, bold=(), family=P, align="left"):
    """A block of lines (newlines) whose first line's top is near `top`."""
    f = f6._font(family, weight)
    lines = content.split("\n")
    w = max(f.getlength(ln) for ln in lines) / 400 * size + size
    h = len(lines) * size * 2.0 + size
    if align == "center":
        x = x - w / 2
    clip = label(s.t, s.t.track("text", name), content, 0.0, s.dur, Box(x, top - size * 0.4, w, h), family,
                 size, colour, weight=weight, align=align, valign="top", name=name, line=line)
    runs = []
    for word in bold:
        i = content.find(word)
        if i >= 0:
            runs.append({"start": i, "end": i + len(word), "boldEnabled": True, "bold": True})
    if runs:
        clip["textStyle"]["runs"] = runs
    return clip


def _t(id, es, en, order, dur, tags=()):
    return _p(id, es, en, order, dur, "tipografia", ["tipografía"] + list(tags))


def greatness():
    D = dur_r(1.6)
    t = _t("greatness", "Tipografía: letras que caen en su lugar", "Typography: letters falling into place", 13310, D)
    s = YR(t, D)
    c = s.say("GREATNESS", (210, 452, 1710, 628), P, 800, WHITE)
    s.typed(c, 6, stagger=0.07, duration=0.35, preset="rise", order="random")
    s.spacing(c, lambda fr: 110 * (1 - k(fr, 6, 42)))
    return t


def super_life():
    D = dur_r(2.4)
    t = _t("super-awesome-life", "Tipografía: tres líneas que suben y se juntan", "Typography: three lines rising and "
           "closing in", 13311, D)
    s = YR(t, D)
    sc = lambda fr: 1.35 - 0.35 * k(fr, 42, 30)  # noqa: E731
    for i, (word, ink) in enumerate((("SUPER", (640, 286, 1280, 413)), ("AWESOME", (416, 460, 1512, 603)),
                                     ("LIFE", (768, 635, 1160, 778)))):
        c = s.say(word, ink, P, 800, WHITE, ["Título", "Texto", "Texto 2"][i],
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 532, sc(fr)), sc(fr), 0, 1))
        s.typed(c, 9 + 3 * i, stagger=0.0, duration=0.4, preset="rise", unit="line")
        s.spacing(c, lambda fr: 40 * (1 - k(fr, 30, 42)))
    return t


def not_down():
    D = dur_r(2.4)
    t = _t("frase-inclinada", "Tipografía: frase inclinada entre dos líneas", "Typography: tilted phrase between lines",
           13312, D, ["frase"])
    s = YR(t, D)
    rot = -8.0
    sc = lambda fr: 1.3 - 0.3 * k(fr, 66, 24)  # noqa: E731
    f = f6._font(P, 800)
    lines = (("IT IS NOT DOWN", 470, 400), ("IN ANY MAP, TRUE", 590, 494), ("PLACES NEVER ARE", 710, 588))
    for i, (txt, x0, y0) in enumerate(lines):
        ink = (x0, y0, x0 + 1400, y0 + 76)
        c = s.say(txt, ink, P, 701, WHITE, ["Título", "Texto", "Texto 2"][i], align="left",
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 532, sc(fr), rot), sc(fr), rot, 1))
        s.typed(c, 9 + 6 * i, stagger=0.12, duration=0.3, preset="fade", order="random", unit="word")
    for i, (y, x0, x1) in enumerate(((372, 560, 1380), (700, 640, 1500))):
        def g(fr, u, y=y, x0=x0, x1=x1, i=i):
            q = k(fr, 66 + 3 * i, 15)
            cx, cy = (x0 + x1) / 2, y
            nx, ny = rot_pt(960 + (cx - 960) * sc(fr), 532 + (cy - 532) * sc(fr), rot, 960, 532)
            return nx, ny, (x1 - x0) * q * sc(fr), 4, rot, 1
        s.obj(f"Línea {i + 1}", solid(WHITE), g)
    return t


def life_box():
    D = dur_r(2.4)
    t = _t("caja-negra", "Tipografía: frase en caja negra", "Typography: phrase in a black box", 13313, D, ["caja"])
    s = YR(t, D)
    sc = lambda fr: 1.3 - 0.3 * k(fr, 66, 24)  # noqa: E731

    def box(fr, u):
        a = k(fr, 12, 12)
        b = k(fr, 24, 9)
        w = 133 * a + (933 - 133) * b
        return 960, 534, w * sc(fr), 133 * a * sc(fr), 0, 1
    s.obj("Caja", solid("#1E1E1E"), box)
    ink = (540, 505, 1380, 563)
    c = s.say("LIFE IS BEAUTIFULL", ink, P, 800, WHITE, geom=lambda fr, u: (*s.about(ink, 960, 534, sc(fr)), sc(fr), 0, 1))
    s.typed(c, 33, stagger=0.06, duration=0.08, preset="fade")
    s.spacing(c, lambda fr: 18 * (1 - k(fr, 45, 24)))
    s.clipped(c, lambda fr: (960 - box(fr, 0)[2] / 2, 0, 960 + box(fr, 0)[2] / 2, 1080))
    return t


def awesomeness():
    D = dur_r(2.4)
    t = _t("awesomeness", "Tipografía: palabra en marco blanco", "Typography: word in a white frame", 13314, D, ["marco"])
    s = YR(t, D)
    sc = lambda fr: 1.4 - 0.4 * k(fr, 54, 18)  # noqa: E731

    def box(fr, u):
        a = k(fr, 15, 9)
        b = k(fr, 24, 15)
        w = 90 * a + (1248 - 90) * b
        h = 90 * a + (190 - 90) * b
        return 960, 556, w * sc(fr), h * sc(fr), 0, 1 if fr > 15 else 0
    s.obj("Marco", ring(WHITE, 5), box)
    ink = (400, 508, 1520, 604)
    c = s.say("AWESOMENESS", ink, P, 800, WHITE, geom=lambda fr, u: (*s.about(ink, 960, 556, sc(fr)), sc(fr), 0, 1))
    s.typed(c, 33, stagger=0.06, duration=0.3, preset="rise", order="random")
    s.spacing(c, lambda fr: 30 * (1 - k(fr, 36, 24)))
    s.clipped(c, lambda fr: (960 - box(fr, 0)[2] / 2, 0, 960 + box(fr, 0)[2] / 2, 1080))
    return t


def quote_bars():
    D = dur_r(2.6)
    t = _t("frase-entre-barras", "Tipografía: frase entre dos barras", "Typography: phrase between two bars", 13315, D,
           ["frase"])
    s = YR(t, D)
    sc = lambda fr: 1.45 - 0.45 * k(fr, 69, 12)  # noqa: E731

    def bar(side):
        def g(fr, u):
            a = k(fr, 12, 12)
            q = k(fr, 27, 18)
            lx = side * (33 * a + (604 - 33) * q) if fr >= 27 else 0.0
            w = 133 * a if fr < 27 else (66 - 56 * k(fr, 42, 6))
            h = 133 * a + 65 * k(fr, 42, 6)
            return 960 + lx * sc(fr), 536, w * sc(fr), h * sc(fr), 0, 1
        return g
    for i, side in enumerate((-1, 1)):
        s.obj(f"Barra {i + 1}", solid("#1E1E1E"), bar(side))
    for i, (txt, y0) in enumerate((("QUIT YOUR JOB, BUY A TICKET, GET", 482), ("A TAN FALL IN LOVE, NEVER RETURN", 551))):
        ink = (430, y0, 1490, y0 + 39)
        c = s.say(txt, ink, P, 800, WHITE, ["Título", "Texto"][i],
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 536, sc(fr)), sc(fr), 0, 1))
        s.typed(c, 45 + 3 * i, stagger=0.02, duration=0.2, preset="fade")
        s.spacing(c, lambda fr: 26 * (1 - k(fr, 45, 24)))
    return t


def be_happy():
    D = dur_r(2.2)
    t = _t("be-happy", "Tipografía: frase que se alinea y cambia de color", "Typography: phrase that lines up and changes "
           "colour", 13316, D, ["frase"])
    s = YR(t, D)
    f = f6._font(P, 800)
    rows = (("BE", 300, 200, 0, -48, 57), ("HAPPY", 300, 372, 1, -144, 57), ("FOR", 300, 544, 2, -244, 45),
            ("THIS", 300 + f.getlength("FOR ") / (f.getbbox("H")[3] - f.getbbox("H")[1]) * 130, 544, 3, -66, 45),
            ("MOMENT", 300, 717, 4, 0, 51))
    for word, x, y, i, dx0, flip in rows:
        ink = (x, y, x + 1500, y + 130)
        mv = lambda fr, dx0=dx0: dx0 * (1 - k(fr, 42, 18))  # noqa: E731
        name = "Título" if i == 0 else f"Texto {i}"
        white = s.say(word, ink, P, 800, WHITE, f"{name} (blanco)", align="left", editable=False,
                      geom=lambda fr, u, mv=mv, flip=flip: (mv(fr), 0, 1, 0, 1 - k(fr, flip, 6)))
        s.typed(white, 9 + 4 * i, stagger=0.06, duration=0.08, preset="fade")
        s.say(word, ink, P, 800, "#111111", name, align="left",
              geom=lambda fr, u, mv=mv, flip=flip: (mv(fr), 0, 1, 0, k(fr, flip, 6)))
    return t


QUOTES = [
    ("Travel at its best should change the way\nyou see the world, open your mind and\nleave you with more questions than\n"
     "answers, and a little more patience\nfor the people you meet on the road.\n- Laura Gómez", "- Laura Gómez"),
    ("When you pack for a trip, take half the\nclothes you planned and twice the money.\nThe rest you will find on the way.\n"
     "- Sara Méndez", "- Sara Méndez"),
    ("What you did yesterday shapes what you\ndo today. When you travel you are only\nwhat you are right now: no past, no\n"
     "plans, just the road in front of you\nand the people who walk it with you.\nKeep your eyes open and your bag light.\n"
     "- Daniel Ruiz", "- Daniel Ruiz"),
    ("Happiness is letting go of what you think your life should look like\nand enjoying it for everything it is. "
     "- Ana Torres", "- Ana Torres"),
    ("At its best, travel should shake what we think we know and change our\nmost cherished views, making us more "
     "curious, broader minded\nand more understanding. - Marco Silva", "- Marco Silva"),
]


def quote_box(id, es, en, order, rect, squares, q, size, from_x, text_top):
    """A small square slides in and grows into a dark box (the corner squares stay); the quote fades in by line."""
    D = dur_r(2.2, 2.8)
    t = _t(id, es, en, order, D, ["cita", "caja"])
    s = YR(t, D)
    x0, y0, x1, y1 = rect
    sq = 60
    ax, ay = squares[0]
    slide = lambda fr: (from_x - ax) * (1 - k(fr, 0, 30))  # noqa: E731
    grow = lambda fr: k(fr, 30, 18)  # noqa: E731
    # the box grows from the first square's spot (its corner) to the final rect
    cx0, cy0 = (x1 - sq, y1 - sq) if ax > x1 - 1 else (x0, y1 - sq)
    cx0 = min(max(cx0, x0), x1 - sq)

    def box(fr, u):
        g = grow(fr)
        return (cx0 + (x0 - cx0) * g, cy0 + (y0 - cy0) * g, cx0 + sq + (x1 - cx0 - sq) * g, cy0 + sq + (y1 - cy0 - sq) * g)
    s.rect("Caja", solid("#1E1E1E"), lambda fr, u: box(fr, u) if fr >= 30 else (0, 0, 0, 0))
    for i, (sx, sy) in enumerate(squares):
        def r(fr, u, sx=sx, sy=sy, i=i):
            if i == 0:
                return sx + slide(fr), sy - sq, sx + sq + slide(fr), sy
            a = k(fr, 36, 6)
            return sx, sy - sq * a, sx + sq * a, sy
        s.rect(f"Cuadro {i + 1}", solid("#1E1E1E"), r)
    text, author = QUOTES[q]
    c = para(s, text, x0 + 40, text_top, size, "#E6E6E6", "Cita", bold=(author,))
    s.typed(c, 36, stagger=0.15, duration=0.4, preset="fade", unit="line")
    return t


def quote_square():
    return quote_box("cita-cuadro", "Tipografía: cita en caja cuadrada", "Typography: quote in a square box", 13317,
                     (667, 213, 1267, 813), [(1287, 820)], 0, 26, 1600, 400)


def quote_square_left():
    return quote_box("cita-cuadro-2", "Tipografía: cita en caja con cuadro abajo", "Typography: quote box with a corner "
                     "square", 13318, (653, 240, 1260, 840), [(573, 840)], 1, 26, 1500, 453)


def quote_square_two():
    return quote_box("cita-cuadro-3", "Tipografía: cita con dos cuadros", "Typography: quote with two squares", 13319,
                     (660, 240, 1260, 840), [(573, 840), (1280, 293)], 2, 26, 1500, 373)


def quote_bar():
    return quote_box("cita-barra", "Tipografía: cita en barra", "Typography: quote on a bar", 13320,
                     (347, 427, 1593, 627), [(347, 693)], 3, 26, 1600, 478)


def quote_bar_two():
    return quote_box("cita-barra-2", "Tipografía: cita en barra con dos cuadros", "Typography: quote bar with two "
                     "squares", 13321, (347, 433, 1593, 627), [(347, 700), (1540, 413)], 4, 26, 1600, 463)


# ==== ICONS ========================================================================================================
# A dot grows into a dark square that widens into the button; the label and glyph come in; out = backwards.

def grow_button(s, rect, at=9):
    """A dark box from a dot at the centre: square (133) by at+15, full rect by at+24. Returns its geom."""
    x0, y0, x1, y1 = rect
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = min(133.0, y1 - y0)

    def g(fr, u):
        a = k(fr, at, 15)
        b = k(fr, at + 15, 9)
        w = side * a + (x1 - x0 - side) * b
        h = side * a + (y1 - y0 - side) * b
        return cx, cy, w, h, 0, 1 if fr >= at else 0
    s.obj("Botón", solid("#1E1E1E"), g)
    return g


def inside(s, clip, g):
    """Clip a clip to the growing box g."""
    s.clipped(clip, lambda fr: (lambda v: (v[0] - v[2] / 2, v[1] - v[3] / 2, v[0] + v[2] / 2, v[1] + v[3] / 2))(
        g(fr, 0)))


def _i(id, es, en, order, tags=()):
    D = dur_r(1.3, 3.0)
    return _p(id, es, en, order, D, "elementos", ["icono"] + list(tags)), D


def icon_subscribe():
    t, D = _i("icono-suscribirse", "Icono: botón Suscribirse", "Icon: Subscribe button", 13322, ["suscribirse"])
    s = YR(t, D)
    g = grow_button(s, (587, 420, 1333, 667))
    c = s.say("SUBSCRIBE", (757, 520, 1163, 566), M, 700, WHITE, geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 6)))
    inside(s, c, g)
    return t


def icon_label(id, es, en, order, word, glyph, tags):
    t, D = _i(id, es, en, order, tags)
    s = YR(t, D)
    rect = (733, 420, 1180, 667)
    g = grow_button(s, rect)
    gx = 820
    c = s.say(word, (868, 523, 1110, 563), M, 700, WHITE, align="left",
              geom=lambda fr, u: (60 * (1 - k(fr, 27, 9)), 0, 1, 0, k(fr, 27, 6)))
    inside(s, c, g)
    glyph(s, gx, 543, lambda fr: k(fr, 30, 6), lambda fr: -60 * (1 - k(fr, 27, 9)))
    return t


def glyph_share(s, x, y, op, dx):
    s.obj("Icono", solid(WHITE), lambda fr, u: (x + dx(fr), y, 56, 46, 0, op(fr)), path=SHARE)


def glyph_thumb(s, x, y, op, dx):
    s.obj("Icono", solid(WHITE), lambda fr, u: (x + dx(fr), y - 4, 54, 54, 0, op(fr)), path=THUMB)


def icon_share():
    return icon_label("icono-compartir", "Icono: botón Compartir", "Icon: Share button", 13323, "SHARE", glyph_share,
                      ["compartir"])


def icon_like():
    return icon_label("icono-me-gusta", "Icono: botón Me gusta", "Icon: Like button", 13324, "LIKE", glyph_thumb,
                      ["me gusta"])


def icon_bell():
    t, D = _i("icono-campana", "Icono: campana que suena", "Icon: ringing bell", 13325, ["campana"])
    s = YR(t, D)
    s_ = s
    grow_button(s_, (733, 413, 1180, 660))
    ring_ = lambda u: 14 * math.sin(2 * math.pi * u * 3.0) * k(u * FPS, 42, 6) if u * FPS > 42 else 0.0  # noqa: E731
    s.obj("Campana", solid(WHITE), lambda fr, u: (956, 530 - 60 * (1 - k(fr, 27, 9)), 66, 72, ring_(u) if s.frame(u) >= 42
                                                                                       else 0, k(fr, 27, 6)),
          path=BELL)
    for i, (a0, a1, cx) in enumerate(((200, 250, 956), (290, 340, 956))):
        s.obj(f"Sonido {i + 1}", ring(WHITE, 5), lambda fr, u, a0=a0, a1=a1: (956, 528, 120, 120, 0, k(fr, 42, 4)),
              path=arc(a0, a1, 8))
    return t


# ==== SOCIAL CARD ==================================================================================================

def glyph_text(txt, family=M, weight=900):
    def g(s, cx, cy, op):
        s.say(txt, (cx - 34, cy - 30, cx + 34, cy + 30), family, weight, BLACK, "Icono (letra)", editable=False,
              geom=lambda fr, u: (0, 0, 1, 0, op(fr)))
    return g


def glyph_bird(s, cx, cy, op):
    bird = poly([(0, 30), (18, 46), (8, 52), (26, 60), (14, 70), (40, 80), (70, 70), (88, 44), (92, 22), (100, 12),
                 (90, 14), (96, 4), (84, 10), (70, 2), (56, 8), (50, 24), (50, 32), (26, 26)])
    s.obj("Icono", solid(BLACK), lambda fr, u: (cx, cy, 64, 54, 0, op(fr)), path=bird)


def glyph_insta(s, cx, cy, op):
    s.obj("Icono", ring(BLACK, 6), lambda fr, u: (cx, cy, 62, 62, 0, op(fr)), radius=16, base=(62, 62))
    s.obj("Icono 2", ring(BLACK, 6), lambda fr, u: (cx, cy, 28, 28, 0, op(fr)), kind="ellipse")
    s.obj("Icono 3", solid(BLACK), lambda fr, u: (cx + 17, cy - 17, 8, 8, 0, op(fr)), kind="ellipse")


def glyph_pin(s, cx, cy, op):
    s.obj("Icono", solid(BLACK), lambda fr, u: (cx, cy, 68, 68, 0, op(fr)), kind="ellipse")
    s.say("P", (cx - 18, cy - 24, cx + 18, cy + 24), M, 900, WHITE, "Icono (letra)", editable=False,
          geom=lambda fr, u: (0, 0, 1, 0, op(fr)))


def glyph_ball(s, cx, cy, op):
    s.obj("Icono", ring(BLACK, 5), lambda fr, u: (cx, cy, 64, 64, 0, op(fr)), kind="ellipse")
    for i, (a0, a1) in enumerate(((150, 300), (330, 480), (230, 400))):
        s.obj(f"Icono {i + 2}", ring(BLACK, 4), lambda fr, u, i=i: (cx + (-14, 14, 0)[i], cy + (0, 0, -18)[i], 60, 60, 0,
                                                                    op(fr)), path=arc(a0, a1, 10))


def glyph_phone(s, cx, cy, op):
    s.obj("Icono", ring(BLACK, 5), lambda fr, u: (cx + 2, cy - 2, 60, 60, 0, op(fr)), kind="ellipse")
    s.obj("Icono 2", solid(BLACK), lambda fr, u: (cx - 22, cy + 24, 18, 18, 0, op(fr)),
          path=poly([(0, 100), (30, 0), (100, 60)]))
    s.obj("Icono 3", solid(BLACK), lambda fr, u: (cx + 2, cy - 2, 26, 26, 45, op(fr)), radius=6, base=(26, 26))


SOCIALS = [
    ("facebook", "Facebook", glyph_text("f"), "facebook.com/yourchannel", "Like Us"),
    ("twitter", "Twitter", glyph_bird, "twitter.com/yourchannel", "Follow Us"),
    ("google-plus", "Google Plus", glyph_text("G+"), "plus.google.com/+YourChannel", "Follow Us"),
    ("instagram", "Instagram", glyph_insta, "instagram.com/yourchannel", "Follow Us"),
    ("linkedin", "LinkedIn", glyph_text("in", M, 800), "linkedin.com/yourchannel", "Follow Us"),
    ("pinterest", "Pinterest", glyph_pin, "pinterest.com/yourchannel", "Follow Us"),
    ("dribbble", "Dribbble", glyph_ball, "dribbble.com/yourchannel", "Follow Us"),
    ("whatsapp", "WhatsApp", glyph_phone, "+00-0000000000", "Connect with Us"),
]


def social(i):
    key, nice, glyph, url, button = SOCIALS[i]
    D = dur_r(1.5, 3.0)
    t = _p(f"red-{key}", f"Redes: tarjeta de {nice}", f"Social: {nice} card", 13326 + i, D, "redes", ["redes", key])
    s = YR(t, D)
    g = grow_button(s, (344, 427, 1597, 628))
    show = lambda fr: k(fr, 33, 6)  # noqa: E731
    s.rect("Icono (fondo)", solid(WHITE), lambda fr, u: (391 - 80 * (1 - k(fr, 33, 9)), 477, 491 - 80 * (1 - k(fr, 33, 9)),
                                                         577), op=lambda fr, u: show(fr))
    glyph(s, 441, 527, show)
    big = i == 7
    c = s.say(url, (524, 512, 1250, 546 if not big else 552), M, 700 if big else 600, WHITE, "Dirección", align="left",
              geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 6)))
    inside(s, c, g)
    s.rect("Botón blanco", solid(WHITE), lambda fr, u: (1296 + 80 * (1 - k(fr, 33, 9)), 487, 1547 + 80 * (1 - k(fr, 33, 9)),
                                                        564), op=lambda fr, u: show(fr))
    s.say(button, (1330, 518, 1513, 533), M, 700, BLACK, "Botón",
          geom=lambda fr, u: (80 * (1 - k(fr, 33, 9)), 0, 1, 0, show(fr)))
    return t


def social_0():
    return social(0)


def social_1():
    return social(1)


def social_2():
    return social(2)


def social_3():
    return social(3)


def social_4():
    return social(4)


def social_5():
    return social(5)


def social_6():
    return social(6)


def social_7():
    return social(7)


# ==== EXTRA: handwritten calls with an arrow ======================================================================

def hand_note(id, es, en, order, text, ink, arrow, head):
    D = 4.0
    t = _p(id, es, en, order, D, "elementos", ["flecha", "a mano"])
    s = Y(t, D)
    n = len(text)
    out = 96
    c = s.say(text, ink, "Shadows Into Light", 400, WHITE, align="left")
    c["textStyle"]["animation"] = {
        "in": tanim("fade", duration=0.05, unit="character", stagger=0.04, ease="easeOut", delay=0.0),
        "out": tanim("fade", duration=0.04, unit="character", stagger=0.025, ease="easeIn", delay=0.0,
                     order="backward")}
    del n
    a = s.outline("Flecha", arrow, 4, WHITE, at=15, n=15, closed=False)
    a["shapeStyle"]["keyframes"]["trimStart"] = keys([(u, round(100 * k(fr, out, 9), 3), "linear") for u, fr in s.each()])
    for j, p in enumerate(head):
        h = s.outline(f"Flecha (punta {j + 1})", p, 4, WHITE, at=30, n=4, closed=False)
        s.fade(h, lambda fr: 1 - k(fr, out - 6, 4))
    return t


def note_subscribe():
    return hand_note("nota-suscribete", "Extra: «Subscribe us» a mano con flecha", "Extra: handwritten «Subscribe us» "
                     "with an arrow", 13334, "Subscribe us", (1102, 845, 1540, 905),
                     [(1563, 862), (1610, 856), (1650, 880), (1676, 930), (1687, 995)],
                     [[(1660, 972), (1687, 997)], [(1712, 968), (1687, 997)]])


def note_comment():
    return hand_note("nota-comenta", "Extra: «Comment below» a mano con flecha", "Extra: handwritten «Comment below» "
                     "with an arrow", 13335, "Comment below", (137, 845, 648, 905),
                     [(685, 862), (732, 856), (772, 880), (798, 930), (805, 995)],
                     [[(778, 972), (805, 997)], [(830, 968), (805, 997)]])


def note_bell():
    return hand_note("nota-campana", "Extra: «Click the bell icon» a mano", "Extra: handwritten «Click the bell icon»",
                     13336, "Click the bell icon", (989, 838, 1540, 898),
                     [(1563, 868), (1610, 862), (1650, 886), (1676, 936), (1687, 995)],
                     [[(1660, 972), (1687, 997)], [(1712, 968), (1687, 997)]])


def note_video():
    return hand_note("nota-video", "Extra: «Check out the video here» a mano", "Extra: handwritten «Check out the video "
                     "here»", 13337, "Check out the video here", (888, 244, 1700, 304),
                     [(1730, 268), (1780, 262), (1818, 236), (1838, 190), (1847, 137)],
                     [[(1822, 160), (1847, 135)], [(1868, 162), (1847, 135)]])


# ==== ELEMENTS: glyphs that pop around, dot grids and scan lines that flash =========================================

def _dots(cols, rows):
    return " ".join(f"M {100 * (i + 0.3) / cols:.2f} {100 * (j + 0.3) / rows:.2f} h {40 / cols:.2f} v {40 / rows:.2f} "
                    f"h {-40 / cols:.2f} Z" for i in range(cols) for j in range(rows))


def _lines(n):
    return " ".join(f"M 0 {100 * i / n:.2f} H 100 V {100 * i / n + 35 / n:.2f} H 0 Z" for i in range(n))


GLYPHS = {
    "rombo": (lambda: ring(WHITE, 5), "M 50 0 L 100 50 L 50 100 L 0 50 Z", 46),
    "cruz": (lambda: solid(WHITE), poly([(20, 0), (50, 30), (80, 0), (100, 20), (70, 50), (100, 80), (80, 100), (50, 70),
                                         (20, 100), (0, 80), (30, 50), (0, 20)]), 36),
    "cuadro": (lambda: ring(WHITE, 3), poly([(0, 0), (100, 0), (100, 100), (0, 100)]), 22),
    "onda": (lambda: ring(WHITE, 4), "M 0 60 L 12 40 L 25 60 L 37 40 L 50 60 L 62 40 L 75 60 L 87 40 L 100 60", 56),
    "aro": (lambda: ring(WHITE, 4), None, 26),
}


def overlay(id, es, en, order, events, extra=None):
    """events: (start s, end s, kind, x, y)."""
    D = 9.6
    t = _p(id, es, en, order, D, "elementos", ["superposición", "glitch"])
    s = Y(t, D)
    if extra:
        extra(s)
    for i, (a, b, kind, x, y) in enumerate(events):
        A, B = a * FPS, b * FPS
        if kind in ("puntos", "rayas"):
            w, h = x[2] - x[0], x[3] - x[1]
            path = _dots(max(4, int(w / 14)), max(4, int(h / 14))) if kind == "puntos" else _lines(max(4, int(h / 12)))
            s.obj(f"{kind.capitalize()} {i + 1}", solid(WHITE, 0.35),
                  lambda fr, u, A=A, B=B, x=x, w=w, h=h: ((x[0] + x[2]) / 2, (x[1] + x[3]) / 2, w, h, 0,
                                                          1.0 if A <= fr < B else 0.0), path=path)
            continue
        layers, path, size = GLYPHS[kind]

        def g(fr, u, A=A, B=B, x=x, y=y, size=size):
            sc = k(fr, A, 3) * (1 - k(fr, B - 3, 3))
            return x, y, size * sc, size * sc, 0, 1.0 if A <= fr < B else 0.0
        if path:
            s.obj(f"{kind.capitalize()} {i + 1}", layers(), g, path=path)
        else:
            s.obj(f"{kind.capitalize()} {i + 1}", layers(), g, kind="ellipse")
    return t


def _events(seed, n, kinds, blocks, block_kind):
    import random
    r = random.Random(seed)
    ev = []
    for i in range(n):
        a = r.uniform(0.2, 9.0)
        ev.append((a, a + r.uniform(0.4, 1.4), r.choice(kinds), r.uniform(140, 1780), r.uniform(120, 960)))
    for i in range(blocks):
        a = r.uniform(0.2, 9.2)
        w, h = r.uniform(400, 900), r.uniform(150, 600)
        x0, y0 = r.uniform(0, 1920 - w), r.uniform(0, 1080 - h)
        ev.append((a, a + r.uniform(0.1, 0.3), block_kind, (x0, y0, x0 + w, y0 + h), 0))
    return ev


def overlay_1():
    return overlay("elementos-1", "Elementos: figuras y puntos que destellan", "Elements: flashing shapes and dots", 13338,
                   _events(1, 26, ["rombo", "cruz", "cuadro", "onda"], 10, "puntos"))


def overlay_2():
    return overlay("elementos-2", "Elementos: figuras, aros y tramas", "Elements: shapes, rings and dot screens", 13339,
                   _events(2, 26, ["rombo", "cruz", "onda", "aro"], 10, "puntos"))


def overlay_3():
    def lines(s):
        for i, (cx, rot) in enumerate(((700, 45), (1300, -45), (1500, 45))):
            s.obj(f"Diagonal {i + 1}", solid(WHITE, 0.6), lambda fr, u, cx=cx, rot=rot, i=i: (
                cx + 120 * math.sin(u * 0.8 + i), 540, 2, 2400, rot, 1.0 if int(u * 2.5 + i) % 3 else 0.0))
        for i in range(4):
            a = 0.6 + 2.2 * i
            s.obj(f"Rombo de puntos {i + 1}", solid(WHITE, 0.25), lambda fr, u, a=a, i=i: (
                (500, 1300, 800, 1500)[i], (700, 600, 420, 800)[i], 600, 600, 45,
                1.0 if a * FPS <= fr < (a + 0.5) * FPS else 0.0), path=_dots(30, 30))
    return overlay("elementos-3", "Elementos: diagonales y rombos de puntos", "Elements: diagonals and dot diamonds",
                   13340, _events(3, 22, ["rombo", "cruz", "cuadro", "onda", "aro"], 0, "puntos"), lines)


def overlay_4():
    def big_ring(s):
        for i, (a, x, y) in enumerate(((0.9, 1500, 200), (5.2, 900, 1000))):
            s.obj(f"Aro grande {i + 1}", ring("#9A9A9A", 150), lambda fr, u, a=a, x=x, y=y: (
                x, y, 900, 900, 0, 0.8 if a * FPS <= fr < (a + 0.6) * FPS else 0.0), kind="ellipse", base=(900, 900))
    return overlay("elementos-4", "Elementos: líneas de escaneo y aro", "Elements: scan lines and a ring", 13341,
                   _events(4, 22, ["rombo", "cruz", "cuadro", "onda"], 14, "rayas"), big_ring)


# ==== TRANSITIONS: white then black cover, black then white uncover ================================================
# Over the previous clip it closes to black at 0.6 s, holds 0.2 s and opens onto the next (transparent) by 1.4 s.

def _tr(id, es, en, order):
    D = 1.6
    return _p(id, es, en, order, D, "transiciones", ["transición", "blanco y negro"]), D


def band_transition(id, es, en, order, axis, sign):
    """Wipe along an axis: white edge leads, black follows; then the hole opens the same way behind a white edge."""
    t, D = _tr(id, es, en, order)
    s = Y(t, D)
    L = 1080 if axis == "y" else 1920
    W = 1920 if axis == "y" else 1080

    def edges(fr):
        w_in = L * k(fr, 0, 15)
        b_in = L * k(fr, 4, 14)
        w_out = L * k(fr, 24, 14)
        b_out = L * k(fr, 27, 15)
        return w_in, b_in, w_out, b_out

    def rect(lo, hi):
        if sign > 0:
            a, b = L - hi, L - lo
        else:
            a, b = lo, hi
        return (0, a, W, b) if axis == "y" else (a, 0, b, W)

    def white(fr, u):
        w_in, b_in, w_out, b_out = edges(fr)
        if fr < 24:
            return rect(0, w_in)
        return rect(b_out, max(b_out, w_out))
    def black(fr, u):
        w_in, b_in, w_out, b_out = edges(fr)
        if fr < 24:
            return rect(0, b_in)
        return rect(w_out, L)
    s.rect("Blanco", solid(WHITE), white)
    s.rect("Negro", solid(BLACK), black)
    return t


def tr_up():
    return band_transition("transicion-sube", "Transición: franjas que suben", "Transition: bands rising", 13342, "y", 1)


def tr_left():
    return band_transition("transicion-izquierda", "Transición: barrido a la izquierda", "Transition: wipe to the left",
                           13343, "x", 1)


def tr_diagonal():
    t, D = _tr("transicion-diagonal", "Transición: barrido diagonal", "Transition: diagonal wipe", 13344)
    s = Y(t, D)
    rot = 30.0
    span = 1920 + 1300

    def band(lo, hi):
        lo, hi = -650 + span * lo, -650 + span * hi
        return lambda: ((lo + hi) / 2, 540, max(0.0, hi - lo), 2600, rot, 1)
    s.obj("Negro", solid(BLACK), lambda fr, u: band(k(fr, 24, 14), k(fr, 4, 14))())
    s.obj("Blanco", solid(WHITE), lambda fr, u: band(k(fr, 4, 14), k(fr, 0, 15))() if fr < 24 else
          band(k(fr, 27, 15), k(fr, 24, 14))())
    return t


def holed(s, name, colour, cx, cy, r, hole, at):
    """Colour over the whole frame from frame `at`, with a hole (inverted mask, "circle" or "rect") of radius /
    half-width r(fr) about (cx, cy)."""
    clip = s.t.solid(s.t.track("shape", name), colour, 0.0, s.dur)
    clip["name"] = name
    clip["opacity"] = keys([(u, 1.0 if fr >= at else 0.0, "hold") for u, fr in s.each()])
    track = s.t.tracks[-1]
    aspect = 1.0 if hole == "circle" else 0.5625
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u, fr in s.each():
        rr = max(0.0, r(fr))
        mk["x"].append((u, cx / 1920, "linear"))
        mk["y"].append((u, cy / 1080, "linear"))
        mk["w"].append((u, 2 * rr / 1920, "linear"))
        mk["h"].append((u, 2 * rr * aspect / 1080, "linear"))
    s.t.mask(track, clip, "ellipse" if hole == "circle" else "rectangle", x=cx / 1920, y=cy / 1080, w=0.0, h=0.0,
             invert=True, keyframes={kk: keys(v) for kk, v in mk.items()})


def ring_transition(id, es, en, order, cx, cy, R, hole="circle", kind="ellipse", aspect=1.0):
    """From (cx, cy): a white shape then a black one cover; then a hole opens behind a white edge."""
    t, D = _tr(id, es, en, order)
    s = Y(t, D)

    def disc(r):
        return cx, cy, 2 * max(0.0, r), 2 * max(0.0, r) * aspect, 0, 1
    s.obj("Blanco", solid(WHITE), lambda fr, u: disc(R * k(fr, 0, 15)) if fr < 24 else disc(0), kind=kind)
    s.obj("Negro", solid(BLACK), lambda fr, u: disc(R * k(fr, 4, 14)) if fr < 24 else disc(0), kind=kind)
    holed(s, "Blanco (salida)", WHITE, cx, cy, lambda fr: R * k(fr, 27, 15), hole, 24)
    holed(s, "Negro (salida)", BLACK, cx, cy, lambda fr: R * k(fr, 24, 14), hole, 24)
    return t


def tr_circle():
    return ring_transition("transicion-circulo", "Transición: círculo desde el centro", "Transition: circle from the "
                           "centre", 13345, 960, 540, 1110)


def tr_circle_left():
    return ring_transition("transicion-circulo-izquierda", "Transición: círculo desde la izquierda", "Transition: circle "
                           "from the left", 13346, -900, 540, 2900)


def tr_circle_top():
    return ring_transition("transicion-circulo-arriba", "Transición: círculo desde arriba", "Transition: circle from the "
                           "top", 13347, 960, -700, 2100)


def tr_lines():
    t, D = _tr("transicion-lineas", "Transición: líneas desde el centro", "Transition: lines from the centre", 13348)
    s = Y(t, D)

    def split(h, name, colour, gone):
        # two halves above and below the centre line, each covering h from it
        s.rect(f"{name} arriba", solid(colour), lambda fr, u: (0, 540 - h(fr), 1920, 540) if not gone(fr) else (0, 0, 0, 0))
        s.rect(f"{name} abajo", solid(colour), lambda fr, u: (0, 540, 1920, 540 + h(fr)) if not gone(fr) else (0, 0, 0, 0))
    split(lambda fr: 545 * k(fr, 0, 15), "Blanco", WHITE, lambda fr: fr >= 24)
    for i, (off, n) in enumerate(((0, 14), (2, 13), (4, 14))):
        split(lambda fr, off=off, n=n: 545 * k(fr, 3 + off, n) * (0.55 + 0.15 * i), f"Raya {i + 1}", BLACK if i % 2 == 0
              else WHITE, lambda fr: fr >= 24)
    split(lambda fr: 545 * k(fr, 9, 12), "Negro", BLACK, lambda fr: fr >= 24)
    # out: black outside a growing gap, a white edge
    s.rect("Negro (salida) arriba", solid(BLACK), lambda fr, u: (0, -10, 1920, 540 - 545 * k(fr, 24, 14))
           if fr >= 24 else (0, 0, 0, 0))
    s.rect("Negro (salida) abajo", solid(BLACK), lambda fr, u: (0, 540 + 545 * k(fr, 24, 14), 1920, 1090)
           if fr >= 24 else (0, 0, 0, 0))
    s.rect("Blanco (salida) arriba", solid(WHITE), lambda fr, u: (0, 540 - 545 * k(fr, 24, 14), 1920, 540 - 545 * k(fr, 27, 15))
           if fr >= 24 else (0, 0, 0, 0))
    s.rect("Blanco (salida) abajo", solid(WHITE), lambda fr, u: (0, 540 + 545 * k(fr, 27, 15), 1920, 540 + 545 * k(fr, 24, 14))
           if fr >= 24 else (0, 0, 0, 0))
    return t


def tr_rect():
    return ring_transition("transicion-rectangulo", "Transición: rectángulo desde el centro", "Transition: rectangle "
                           "from the centre", 13349, 960, 540, 980, hole="rect", kind="rectangle", aspect=0.5625)


# ==== END CARD =====================================================================================================

def end_card(id, es, en, order, cards):
    """cards: (x0, y0, from_dx, from_dy) of each 575×447 card (photo on top, dark bar with NEXT VIDEO)."""
    D = dur_r(1.0, 4.0)
    t = _p(id, es, en, order, D, "pantallas-finales", ["pantalla final", "videos"])
    s = YR(t, D)
    samples = ["fx-hair-01", "fx-face-03", "fx-face-05", "fx-hair-02"]
    for i, (x0, y0, fdx, fdy) in enumerate(cards):
        x1, y1 = x0 + 575, y0 + 447
        cx, cy = x0 + 287, y0 + 223
        sq = 133

        def g(fr, u, cx=cx, cy=cy, fdx=fdx, fdy=fdy, x0=x0, x1=x1, y0=y0, y1=y1):
            a = k(fr, 0, 9)
            b = k(fr, 9, 6)
            w = sq * a + (575 - sq) * b
            h = sq * a + (447 - sq) * b
            return cx + fdx * (1 - a), cy + fdy * (1 - a), w, h, 0, 1
        s.obj(f"Tarjeta {i + 1}", solid("#1E1E1E"), g)
        ph = s.pic(f"Video {i + 1}", samples[i % 4], lambda fr, u, x0=x0, y0=y0: (x0 + 287, y0 + 165, 575, 330, 0,
                                                                                  k(fr, 12, 4)),
                   label=f"Tu video {i + 1}", base=(575, 330))
        s.clipped(ph, lambda fr, g=g: (lambda v: (v[0] - v[2] / 2, v[1] - v[3] / 2, v[0] + v[2] / 2, v[1] + v[3] / 2))(
            g(fr, 0)))
        s.say("NEXT VIDEO", (x0 + 65, y0 + 354, x0 + 300, y0 + 380), M, 700, WHITE, f"Tarjeta {i + 1}" if i else "Título",
              align="left", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 15, 4)))
        s.say("YOUR AWESOME VIDEO", (x0 + 65, y0 + 397, x0 + 300, y0 + 415), M, 600, "#DDDDDD",
              f"Tarjeta {i + 1} (título)", align="left", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 4)))
    return t


def end_one():
    return end_card("final-1", "Pantalla final: un video", "End card: one video", 13350, [(680, 318, 0, 0)])


def end_two_stacked():
    return end_card("final-2", "Pantalla final: dos videos apilados", "End card: two stacked videos", 13351,
                    [(134, 73, -700, 0), (134, 555, -700, 0)])


def end_two_side():
    return end_card("final-3", "Pantalla final: dos videos lado a lado", "End card: two videos side by side", 13352,
                    [(377, 317, -300, 300), (985, 317, -300, 300)])


def end_four():
    return end_card("final-4", "Pantalla final: cuatro videos", "End card: four videos", 13353,
                    [(374, 80, 0, 0), (975, 80, 0, 0), (374, 555, 0, 0), (975, 555, 0, 0)])


def band_avatar():
    return subscribe_band(False)


def band_photo():
    return subscribe_band(True)


TEMPLATES = [opener_red, opener_youtube, opener_avatar, opener_words, phone_center, phone_left, subscribe_bar,
             subscribe_photo, band_avatar, band_photo, greatness, super_life, not_down, life_box, awesomeness,
             quote_bars, be_happy, quote_square, quote_square_left, quote_square_two, quote_bar, quote_bar_two,
             icon_subscribe, icon_share, icon_like, icon_bell, social_0, social_1, social_2, social_3, social_4,
             social_5, social_6, social_7, note_subscribe, note_comment, note_bell, note_video, overlay_1, overlay_2,
             overlay_3, overlay_4, tr_up, tr_left, tr_diagonal, tr_circle, tr_circle_left, tr_circle_top, tr_lines,
             tr_rect, end_one, end_two_stacked, end_two_side, end_four]

_ONLY = os.environ.get("YP7_ONLY")
if _ONLY:
    TEMPLATES = [f for f in TEMPLATES if f.__name__ in _ONLY.split(",")]
