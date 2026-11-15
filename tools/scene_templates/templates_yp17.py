"""Video 55227068.mp4 as Kit de YouTube Stock templates (yp17-*). See docs/plan-youtube-pack-2.md.

Flat channel cards over footage (1920×1080, 30 fps, 27 s), each one studied on 10 fps sheets: white cards with a
thin dark outline and a solid dark shadow down to the left, a wide grotesque (Anybody Expanded), round photos with a
ring, and a black «Subscribe» pill that a hand cursor clicks: it greys under the finger, turns red, then yellow
«Subscribed» with a bell (yellow stars and red dots fly), and settles white with a grey outline. Every piece pops in
tilted and bouncing (the card, then the photo and the pill a little later, the words typed), and leaves shrinking
and turning the other way.

Skipped: the pack cover, the settings panel (colour swatches and sliders) and the small «Name» card, which is only
the opening of the round-photo card. The YouTube play button only where the reference shows it. Photos are slots.
Kit de YouTube › Redes / Tercios; order 18800-. Study notes in tienda/plantillas/estudio-55227068/NOTAS.md.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import keys, tanim
from templates_tit_e import solid
from templates_tit_h import rot_pt, shadow
from templates_yp0 import BELL, E, W

AE = "Anybody Expanded"
for _w, _f in ((500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")):
    f6._FILES[(AE, _w)] = f"fonts.extra/fonts/anybodyexpanded/AnybodyExpanded-{_f}.ttf"
WHITE, INK, CARD = "#FFFFFF", "#1E1E1E", "#FDFDFD"
RED, YELLOW, GREY = "#E5484D", "#F2C531", "#8E8E8E"
BACKDROP = "#DCE2E2"   # the reference's light grey demo
SH = 10                # the shadow's offset (left and down)


def back(q):
    """0 → 1 with the small overshoot of the reference's pops."""
    if q <= 0:
        return 0.0
    if q >= 1:
        return 1.0
    c1 = 1.9
    return 1 + (c1 + 1) * (q - 1) ** 3 + c1 * (q - 1) ** 2


def stroke(colour, width):
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
            "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def card_layers(fill_colour=CARD, line=INK, width=3.0, sh=True):
    out = [shadow(INK, -SH, SH, 0, 1.0)] if sh else []
    out += [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "solid", "color": "#ff" + fill_colour.lstrip("#").lower()}}, stroke(line, width)]
    return out


class P(W):
    """A piece that pops in at second a about (px, py) and leaves from second b; every part rides on that pose
    and may pop on its own a little later (d = its delay)."""

    def __init__(self, t, dur, a, b, px, py, tilt=-14.0, n_in=0.42, n_out=0.32):
        super().__init__(t, dur, 0.0)
        self.a, self.b, self.px, self.py, self.tilt, self.n_in, self.n_out = a, b, px, py, tilt, n_in, n_out

    def pose(self, v, d=0.0):
        """(scale, turn) of a part that pops d seconds after the piece."""
        q = back(min(1.0, max(0.0, (v - self.a - d) / self.n_in)))
        o = E(v, self.b - d * 0.4, self.n_out)
        sc = q * (1 - o)
        rot = self.tilt * (1 - E(v, self.a + d, self.n_in)) - self.tilt * 0.8 * o
        return sc, rot

    def at(self, x, y, v, d=0.0, own=None):
        """Where (x, y) goes: first its own pop about `own` (a part's centre), then the piece's pose."""
        sc, rot = self.pose(v, 0.0)
        if own is not None and d > 0:
            s2, _ = self.pose(v, d)
            s2 = s2 / max(1e-4, sc) if sc > 1e-4 else 0.0
            x, y = own[0] + (x - own[0]) * s2, own[1] + (y - own[1]) * s2
        nx, ny = self.px + (x - self.px) * sc, self.py + (y - self.py) * sc
        return rot_pt(nx, ny, rot, self.px, self.py)

    def scale(self, v, d=0.0):
        return self.pose(v, d)[0]

    def part(self, name, layers, cx, cy, w, h, d=0.0, op=None, **kw):
        """A shape whose rest box is centred at (cx, cy); op(v) = its own opacity."""
        def g(v):
            sc, rot = self.pose(v, 0.0)
            s2 = self.scale(v, d)
            x, y = self.at(cx, cy, v)
            return x, y, w * s2, h * s2, rot, (op(v) if op else 1.0) * (1.0 if s2 > 0.01 else 0.0)
        return self.shp(name, layers, g, base=(w, h), **kw)

    def card(self, rect, name="Tarjeta", r=18, d=0.0):
        x0, y0, x1, y1 = rect
        return self.part(name, card_layers(), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, d, radius=r)

    def line(self, content, ink, name, typed_at, weight=800, colour=INK, align="center", d=0.0, op=None):
        """A line of words; it rides on the pose and types itself in from typed_at."""
        cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2

        def g(v):
            sc, rot = self.pose(v, 0.0)
            s2 = self.scale(v, d)
            x, y = self.at(cx, cy, v)
            return x - cx, y - cy, max(1e-3, s2), rot, (op(v) if op else 1.0)
        clip = self.say(content, ink, AE, weight, colour, name, align=align, geom=lambda fr, u: g(u))
        if typed_at is not None:
            n = max(1, len(content))
            clip["textStyle"]["animation"] = {
                "in": tanim("typewriter", duration=0.03, unit="character", stagger=min(0.045, 0.4 / n),
                            ease="easeOut", delay=round(typed_at, 3), order="forward")}
        return clip

    def face(self, sample, cx, cy, r, d=0.12, ring=7.0, name="Foto"):
        """A round photo in a white ring with a dark outline; it pops d seconds after the piece."""
        self.part(f"{name} (aro)", [shadow(INK, -SH * 0.6, SH * 0.6, 0, 1.0) if ring > 9 else shadow(INK, 0, 0, 0, 0),
                                    {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                     "paint": {"kind": "solid", "color": "#ffffffff"}}, stroke(INK, 2.5)],
                  cx, cy, 2 * (r + ring), 2 * (r + ring), d, kind="ellipse")
        track = self.t.track("video", name)
        mo, rots, ops = [], [], []
        for u in frames_of(self.dur):
            sc, rot = self.pose(u, 0.0)
            s2 = self.scale(u, d)
            x, y = self.at(cx, cy, u)
            mo.append((u, {"s": max(1e-3, s2), "dx": x - cx, "dy": y - cy}, "linear"))
            rots.append((u, round(rot, 3), "linear"))
            ops.append((u, 1.0 if s2 > 0.01 else 0.0, "hold"))
        clip = self.t.photo(track, sample, 0.0, self.dur, Box(cx - r, cy - r, 2 * r, 2 * r), mo, label="Tu foto")
        clip["name"] = name
        clip["rotation"] = keys(rots)
        clip["opacity"] = keys(ops)
        self.t.mask(track, clip, "ellipse")
        return clip

    def photo_rect(self, sample, rect, d=0.12, name="Foto"):
        """A photo inside the card (a straight box) that pops with it."""
        x0, y0, x1, y1 = rect
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        track = self.t.track("video", name)
        mo, rots, ops = [], [], []
        for u in frames_of(self.dur):
            sc, rot = self.pose(u, 0.0)
            s2 = self.scale(u, d)
            x, y = self.at(cx, cy, u)
            mo.append((u, {"s": max(1e-3, s2), "dx": x - cx, "dy": y - cy}, "linear"))
            rots.append((u, round(rot, 3), "linear"))
            ops.append((u, 1.0 if s2 > 0.01 else 0.0, "hold"))
        clip = self.t.photo(track, sample, 0.0, self.dur, Box(x0, y0, x1 - x0, y1 - y0), mo, label="Tu foto")
        clip["name"] = name
        clip["rotation"] = keys(rots)
        clip["opacity"] = keys(ops)
        return clip

    def ytb(self, cx, cy, w, h, d=0.2, name="YouTube"):
        def g(fr, u):
            sc, rot = self.pose(u, 0.0)
            s2 = self.scale(u, d)
            x, y = self.at(cx, cy, u)
            return x, y, max(1e-3, s2), rot, 1.0 if s2 > 0.01 else 0.0
        self.yt(name, g, w=w, h=h, red="#E62117", tri=WHITE)

    def subscribe(self, rect, click, d=0.25, name="Suscribirse"):
        """The pill: black «Subscribe» → grey under the finger → red → yellow «Subscribed» with a bell → white with
        a grey outline."""
        x0, y0, x1, y1 = rect
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        c = click
        press = lambda v: 1 - 0.07 * math.sin(math.pi * min(1, max(0, (v - c + 0.08) / 0.24)))  # noqa: E731
        states = [  # (name, fill, outline, from, to)
            ("negro", INK, INK, -1, c), ("gris", "#D9D9D9", "#9A9A9A", c, c + 0.12), ("rojo", RED, RED, c + 0.12, c + 0.45),
            ("amarillo", YELLOW, INK, c + 0.45, c + 1.0), ("blanco", WHITE, GREY, c + 1.0, 99)]
        for nm, fc, lc, t0, t1 in states:
            self.part(f"{name} ({nm})", [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                          "paint": {"kind": "solid", "color": "#ff" + fc.lstrip("#").lower()}},
                                         stroke(lc, 2.2)],
                      cx, cy, w * 1.0, h, d, op=lambda v, t0=t0, t1=t1: 1.0 if t0 <= v < t1 else 0.0, radius=h / 2)
        cap = h * 0.31
        ty0, ty1 = cy - cap / 2 - h * 0.02, cy + cap / 2 - h * 0.02
        ww = cap * 9.0
        self.line("Subscribe", (cx - ww / 2, ty0, cx + ww / 2, ty1), f"{name} (texto)", None, weight=500, colour=WHITE,
                  d=d, op=lambda v: 1.0 if v < c + 0.45 else 0.0)
        gw = cap * 1.3
        tw = cap * 9.8
        left = cx - (gw + cap * 0.7 + tw) / 2
        self.line("Subscribed", (left + gw + cap * 0.7, ty0, left + gw + cap * 0.7 + tw, ty1),
                  f"{name} (suscrito)", None, weight=500, colour=INK, align="left", d=d,
                  op=lambda v: 1.0 if v >= c + 0.45 else 0.0)
        bx = left + gw / 2
        self.part(f"{name} (campana)", [{"id": "fill", "kind": "fill", "enabled": False,
                                         "paint": {"kind": "solid", "color": "#00000000"}}, stroke(INK, 2.0)],
                  bx, cy, gw, gw * 1.15, d, op=lambda v: 1.0 if v >= c + 0.45 else 0.0, path=BELL)
        self.sparks(cx, cy, c + 0.45, w, h)

    def sparks(self, cx, cy, c, w, h, n=6):
        """Yellow stars and red dots that fly off the pill when it turns yellow."""
        for i in range(n):
            ang = 360 * i / n + 30
            star = i % 2 == 0

            def g(v, ang=ang, star=star):
                q = min(1.0, max(0.0, (v - c) / 0.55))
                ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                rx, ry = w * (0.35 + 0.35 * (1 - (1 - q) ** 2)), h * (0.6 + 0.9 * (1 - (1 - q) ** 2))
                d = (22 if star else 12) * (1 - 0.6 * q)
                return cx + ca * rx, cy + sa * ry, d, d, 40 * q, 1.0 if c <= v < c + 0.55 else 0.0
            self.shp(f"{'Estrella' if star else 'Punto'} {i + 1}", solid(YELLOW if star else RED), g,
                     kind="star" if star else "ellipse", base=(22, 22) if star else (12, 12))


def _p(id, es, en, order, dur, thumb, section="redes", tags=()):
    t = wide(f"yp17-{id}", es, en, "ytkit", dur, order=order,
             tags=[f"kit:{section}", "youtube", "tarjeta", "plano"] + list(tags), thumb_at=thumb)
    t.background = BACKDROP
    return t


# --- 1. «Watch More» small card (8.85–9.75 s; it then stretches into the channel bar) ------------------------------
def watch_more():
    D = 2.3
    t = _p("watch-more", "Tarjeta plana: ver más", "Flat card: watch more", 18800, D, 1.2, "elementos", ["ver más"])
    s = P(t, D, 0.0, D - 0.35, 603, 832, tilt=-16)
    s.card((495, 777, 711, 888))
    s.line("Watch", (528, 800, 678, 824), "Texto 1", 0.15)
    s.line("More", (548, 834, 658, 858), "Texto 2", 0.3)
    return t


# --- 2. «Join Us» with the play button (9.0–9.75 s; it then stretches into the channel card) ----------------------
def join_us():
    D = 2.3
    t = _p("join-us", "Tarjeta plana: únete con YouTube", "Flat card: join us with YouTube", 18801, D, 1.2,
           "elementos", ["únete"])
    s = P(t, D, 0.0, D - 0.35, 1554, 359, tilt=14)
    s.card((1480, 302, 1628, 416))
    s.line("Join", (1515, 321, 1601, 345), "Texto 1", 0.15)
    s.line("Us", (1505, 358, 1557, 382), "Texto 2", 0.3, align="left")
    s.ytb(1590, 371, 36, 25, d=0.25)
    return t


# --- 3. «Your Channel» vertical card: round photo with the play button, Subscribe clicked (9.85–13.8 s) -----------
def tarjeta_vertical():
    D = 4.0
    t = _p("tarjeta-vertical", "Tarjeta vertical plana con suscribirse", "Flat vertical card with subscribe", 18802,
           D, 2.6, "redes", ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 1553, 358, tilt=12)
    s.card((1430, 183, 1677, 533))
    s.line("Your", (1515, 206, 1599, 230), "Texto 1", 0.2)
    s.line("Channel", (1484, 240, 1630, 264), "Texto 2", 0.3)
    s.face("h-portrait-05", 1557, 354, 66, d=0.15, ring=4)
    s.ytb(1557, 421, 45, 31, d=0.3)
    s.subscribe((1452, 459, 1662, 504), 1.45)
    s.cursor([(0.95, 1640, 640), (1.3, 1575, 505), (1.5, 1560, 485), (1.8, 1562, 488), (2.2, 1660, 640)], 0.9,
             2.1, clicks=(1.42,))
    return t


# --- 4. «Youtube Channel» bar: photo popping out above, Subscribe clicked (9.70–13.8 s) ---------------------------
def barra_canal():
    D = 4.1
    t = _p("barra-canal", "Barra plana con foto y suscribirse", "Flat bar with photo and subscribe", 18803, D, 2.7,
           "tercios", ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 600, 832, tilt=-10)
    s.card((248, 780, 953, 885))
    s.face("portrait-04", 358, 790, 70, d=0.12, ring=4)
    s.line("Youtube", (474, 800, 654, 824), "Texto 1", 0.25, align="left")
    s.line("Channel", (474, 834, 650, 858), "Texto 2", 0.35, align="left")
    s.subscribe((716, 810, 926, 855), 1.35)
    s.cursor([(0.8, 860, 990), (1.15, 830, 860), (1.35, 820, 838), (1.7, 822, 840), (2.1, 900, 990)], 0.75, 2.0,
             clicks=(1.32,))
    return t


# --- 5. Square photo card beside a Subscribe bar (14.4–19.6 s) ----------------------------------------------------
def foto_cuadrada():
    D = 4.4
    t = _p("foto-cuadrada", "Foto cuadrada y barra con suscribirse", "Square photo and subscribe bar", 18804, D, 2.8,
           "redes", ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 468, 240, tilt=-12)
    s.card((248, 183, 362, 296), name="Tarjeta (foto)")
    s.photo_rect("man-01", (253, 188, 357, 291), d=0.1)
    s.part("Marco de la foto", [{"id": "fill", "kind": "fill", "enabled": False,
                                 "paint": {"kind": "solid", "color": "#00000000"}}, stroke(INK, 3.0)],
           305, 239.5, 114, 113, 0.1, radius=18)
    s.card((387, 183, 687, 296), d=0.08)
    s.subscribe((462, 218, 612, 261), 1.55, d=0.3)
    s.cursor([(1.0, 620, 360), (1.35, 548, 262), (1.55, 538, 245), (1.9, 540, 248), (2.3, 640, 380)], 0.95, 2.2,
             clicks=(1.52,))
    return t


# --- 6. «Channel Name» bar with the photo in the middle and Subscribe at the left (14.6–19.6 s) -------------------
def barra_foto():
    D = 4.4
    t = _p("barra-foto", "Barra plana con foto al centro", "Flat bar with a photo in the middle", 18805, D, 2.8,
           "tercios", ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 1350, 832, tilt=10)
    s.card((1023, 776, 1677, 888))
    s.photo_rect("h-portrait-01", (1290, 779, 1422, 885), d=0.12)
    s.line("Channel", (1462, 802, 1629, 827), "Texto 1", 0.3, align="left")
    s.line("Name", (1462, 837, 1560, 861), "Texto 2", 0.4, align="left")
    s.subscribe((1063, 807, 1254, 853), 1.6, d=0.2)
    s.cursor([(1.05, 1240, 980), (1.4, 1175, 858), (1.6, 1160, 838), (1.95, 1163, 842), (2.35, 1260, 990)], 1.0,
             2.25, clicks=(1.57,))
    return t


# --- 7. Round photo above a «Channel Name» card (20.1–25.9 s) -----------------------------------------------------
def foto_arriba():
    D = 4.6
    t = _p("foto-arriba", "Foto redonda sobre tarjeta con suscribirse", "Round photo above a subscribe card", 18806,
           D, 2.9, "redes", ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 1555, 400, tilt=12)
    s.face("man-06", 1556, 255, 70, d=0.0, ring=10)
    s.card((1432, 357, 1677, 528), d=0.2)
    s.line("Channel", (1474, 378, 1638, 402), "Texto 1", 0.45)
    s.line("Name", (1502, 412, 1610, 436), "Texto 2", 0.55)
    s.subscribe((1458, 459, 1653, 504), 1.8, d=0.35)
    s.cursor([(1.25, 1640, 640), (1.6, 1572, 505), (1.8, 1560, 485), (2.15, 1562, 488), (2.55, 1660, 640)], 1.2,
             2.45, clicks=(1.77,))
    return t


# --- 8. «Your Channel Name» card: round photo, play button in the corner, Subscribe (20.9–25.9 s) -----------------
def tarjeta_nombre():
    D = 4.6
    t = _p("tarjeta-nombre", "Tarjeta plana con foto, YouTube y suscribirse", "Flat card with photo, YouTube and subscribe",
           18807, D, 2.9, "redes", ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 474, 776, tilt=-12)
    s.card((255, 668, 693, 885))
    s.face("h-portrait-04", 354, 774, 72, d=0.12, ring=4)
    s.ytb(651, 699, 36, 25, d=0.3)
    s.line("Your", (455, 698, 539, 722), "Texto 1", 0.3, align="left")
    s.line("Channel", (455, 734, 606, 758), "Texto 2", 0.4, align="left")
    s.line("Name", (455, 768, 561, 792), "Texto 3", 0.5, align="left")
    s.subscribe((455, 815, 663, 858), 1.45, d=0.3)
    s.cursor([(0.95, 640, 990), (1.3, 575, 862), (1.5, 562, 843), (1.85, 564, 846), (2.25, 660, 990)], 0.9, 2.15,
             clicks=(1.42,))
    return t


# --- 9. «Advanced Editing» bar: photo popping out at the left, Subscribe (grid 1.5–4.6 s, 5.0–8.6 s) ------------
def barra_titulo():
    D = 4.2
    t = _p("barra-titulo", "Barra plana con foto y título", "Flat bar with photo and title", 18808, D, 2.8, "tercios",
           ["suscríbete", "clic", "foto"])
    s = P(t, D, 0.0, D - 0.35, 626, 887, tilt=-10)
    s.card((220, 827, 1032, 948))
    s.face("portrait-04", 345, 833, 82, d=0.12, ring=4)
    s.line("Advanced", (477, 849, 720, 876), "Texto 1", 0.25, align="left")
    s.line("Editing", (477, 890, 650, 917), "Texto 2", 0.35, align="left")
    s.subscribe((758, 863, 999, 912), 1.5, d=0.25)
    s.cursor([(0.95, 960, 1050), (1.3, 895, 915), (1.5, 880, 893), (1.85, 882, 896), (2.25, 980, 1050)], 0.9, 2.15,
             clicks=(1.47,))
    return t


# --- 10. The YouTube play button on a small card (20.2–20.9 s) -----------------------------------------------------
def boton_youtube():
    D = 2.3
    t = _p("boton-youtube", "Tarjeta plana con botón de YouTube", "Flat card with the YouTube button", 18809, D, 1.2,
           "elementos", ["botón", "play"])
    s = P(t, D, 0.0, D - 0.35, 471, 778, tilt=-16)
    s.card((400, 723, 543, 834))
    s.ytb(474, 776, 66, 47, d=0.15)
    return t


TEMPLATES = [watch_more, join_us, tarjeta_vertical, barra_canal, foto_cuadrada, barra_foto, foto_arriba,
             tarjeta_nombre, barra_titulo, boton_youtube]
