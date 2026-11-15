"""Video 59446629.mp4 as Kit de YouTube Stock templates (yp16-*). See docs/plan-youtube-pack-2.md.

Frosted glass subscribe bubbles over footage (1920×1080, 30 fps, 27 s), each one studied on 10 fps sheets: the
round photo pops first, the glass grows out of it (a blur of what is under it, masked to the bubble frame by frame,
with a light tint and a thin white edge), the letters fade in in random order, and an arrow cursor clicks the glass
«Subscribe»: it turns pink, becomes «Subscribed» with a bell (little pink sparks fly), and fades back to glass. The
exit is the entrance backwards: letters fade out, the bubble shrinks into the photo and the photo closes.

Skipped: the settings panel shots (colour swatches and sliders) and the «Custom Editing» card, which is the Elaine
card again. Photos are slots. Kit de YouTube › Redes / Tercios; order 18700-. Study notes in
tienda/plantillas/estudio-59446629/NOTAS.md.
"""

from __future__ import annotations

import math

from kit import Box, wide
from llt_motion import frames_of
from scene import keys, tanim
from templates_tit_e import solid
from templates_yp0 import BELL, E, L
from templates_yp15 import LATO, WHITE, G, glass_layers, argb

PINK = "#E8247E"
BACKDROP = "#2A2C31"
# An arrow pointer (tip at the top left) on a 11 × 18 grid.
ARROW = "M 0 0 L 0 88 L 22 68 L 38 100 L 52 93 L 37 62 L 100 62 Z"


def bubble(rect, ox, oy, d0, a, n, b, m):
    """A rounded box (x0, y0, x1, y1, r) that grows out of a small circle of size d0 at (ox, oy) from second a
    over n, and shrinks back into it from second b over m; None while shut."""
    x0, y0, x1, y1, r = rect

    def at(v):
        if v < a or v > b + m:
            return None
        q = E(v, a, n) * (1 - E(v, b, m))
        if q <= 0.0:
            return None
        s0 = (ox - d0 / 2, oy - d0 / 2, ox + d0 / 2, oy + d0 / 2)
        bx0, by0 = s0[0] + (x0 - s0[0]) * q, s0[1] + (y0 - s0[1]) * q
        bx1, by1 = s0[2] + (x1 - s0[2]) * q, s0[3] + (y1 - s0[3]) * q
        return (bx0, by0, bx1, by1, min(r if q > 0.999 else max(r, (by1 - by0) / 2), (by1 - by0) / 2,
                                        (bx1 - bx0) / 2))
    return at


class B(G):
    """A glass subscribe bubble; times are seconds of this piece (o = 0)."""

    def letters(self, content, ink, weight, colour, name, a, b, align="center", each=0.25, span=0.35):
        """The letters fade in in random order from second a over ~span, and out the same way from second b."""
        clip = self.say(content, ink, LATO, weight, colour, name, align=align)
        n = max(1, len(content.replace(" ", "")))
        gap = max(0.004, (span - each) / n)
        out_end = b + span
        clip["textStyle"]["animation"] = {
            "in": tanim("fade", duration=each, unit="character", stagger=gap, ease="easeOut", delay=round(a, 3),
                        order="random"),
            "out": tanim("fade", duration=each, unit="character", stagger=gap, ease="easeIn",
                         delay=round(max(0.0, self.dur - out_end), 3), order="random")}
        return clip

    def face(self, sample, cx, cy, r, a, b, ring_w=3.0, name="Foto"):
        """A round photo with a thin white ring that pops at a and closes from b."""
        sc = lambda v: (E(v, a, 0.3) * (1 - E(v, b, 0.22)))  # noqa: E731
        self.shp(f"{name} (aro)", [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                    "paint": {"kind": "solid", "color": "#ffe9e9ea"}}],
                 lambda v: (cx, cy, (2 * r + 2 * ring_w) * sc(v), (2 * r + 2 * ring_w) * sc(v), 0,
                            1.0 if sc(v) > 0.01 else 0.0), kind="ellipse", base=(2 * r + 2 * ring_w,) * 2)
        track = self.t.track("video", name)
        mo = [(u, {"s": max(1e-3, sc(u))}, "linear") for u in frames_of(self.dur)]
        clip = self.t.photo(track, sample, 0.0, self.dur, Box(cx - r, cy - r, 2 * r, 2 * r), mo, label="Tu foto")
        clip["name"] = name
        clip["opacity"] = keys([(u, 1.0 if sc(u) > 0.01 else 0.0, "hold") for u in frames_of(self.dur)])
        self.t.mask(track, clip, "ellipse")
        return clip

    def subscribe(self, rect, cap, a, b, click, bell_first=False, name="Suscribirse"):
        """A glass button with «Subscribe»; clicked at `click` it turns pink, then «Subscribed» with a bell, and
        fades back to glass with «Subscribed». cap = (top, baseline) of its words."""
        x0, y0, x1, y1 = rect
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        show = lambda v: E(v, a, 0.25) * (1 - E(v, b, 0.2))  # noqa: E731

        def press(v):
            if click is None or v < click - 0.12:
                return 1.0
            if v < click:
                return 1 - 0.08 * E(v, click - 0.12, 0.12)
            return 0.92 + 0.08 * E(v, click, 0.18)
        pink = lambda v: 0.0 if click is None else E(v, click, 0.06) * (1 - E(v, click + 0.75, 0.3))  # noqa: E731
        self.shp(name, [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                         "paint": {"kind": "solid", "color": argb(WHITE, 0.2)}}],
                 lambda v: (cx, cy, w * press(v) * (0.6 + 0.4 * show(v)), h * press(v) * (0.6 + 0.4 * show(v)), 0,
                            show(v)), radius=h / 2, base=(w, h))
        self.shp(f"{name} (rosa)", solid(PINK), lambda v: (cx, cy, w * press(v), h * press(v), 0, pink(v) * show(v)),
                 radius=h / 2, base=(w, h))
        ch = cap[1] - cap[0]
        after = lambda v: click is not None and v >= click + 0.3  # noqa: E731
        bw = ch * 1.15
        word_w = ch * 5.6
        # «Subscribe» centred; «Subscribed» shifted right of a bell.
        s1 = self.txt("Subscribe", (cx - word_w * 0.5, cap[0], cx + word_w * 0.5, cap[1]), LATO, 400, WHITE,
                      f"{name} (texto)", g=lambda v: (0, 0, press(v), 0, show(v) * (0.0 if after(v) else 1.0)))
        gw = bw * 0.6
        total = gw + ch * 0.45 + word_w * 1.07
        left = cx - total / 2
        s2 = self.txt("Subscribed", (left + gw + ch * 0.45, cap[0], left + total, cap[1]), LATO, 400, WHITE,
                      f"{name} (suscrito)", align="left",
                      g=lambda v: (0, 0, press(v), 0, show(v) * (1.0 if after(v) else 0.0)))
        self.shp(f"{name} (campana)", solid(WHITE),
                 lambda v: (left + gw / 2, (cap[0] + cap[1]) / 2, gw, bw, 0,
                            show(v) * (1.0 if after(v) else 0.0)), path=BELL, base=(gw, bw))
        if click is not None:
            self.sparks(cx, cy, click, max(w, h) * 0.5)
        return s1, s2

    def sparks(self, x, y, c, r0, n=7):
        """Small pink sparks that fly out of the click."""
        for i in range(n):
            ang = 360 * i / n + 20

            def g(v, ang=ang, i=i):
                q = L(v, c + 0.02, 0.45)
                rr = r0 * (0.4 + 0.75 * (1 - (1 - q) ** 2))
                ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                d = (9 if i % 2 else 6) * (1 - 0.5 * q)
                return x + ca * rr, y + sa * rr * 0.6, d, d, 0, 1.0 if c + 0.02 <= v < c + 0.47 else 0.0
            self.shp(f"Chispa {i + 1}", solid(PINK), g, kind="ellipse" if i % 2 else "star", base=(9, 9))

    def arrow(self, pts, t_in, t_out, click, size=(34, 52), name="Cursor"):
        """The arrow pointer: its tip through waypoints [(second, x, y)], a small press at the click."""
        from templates_yp0 import path_at

        def g(v):
            x, y = path_at(pts, v)
            sc = 1 - 0.1 * math.sin(math.pi * L(v, click - 0.1, 0.2))
            cw, ch = size[0] * sc, size[1] * sc
            return x + cw / 2, y + ch / 2, cw, ch, 0, E(v, t_in, 0.12) * (1 - E(v, t_out, 0.12))
        self.shp(name, [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                         "paint": {"kind": "solid", "color": "#ffffffff"}},
                        {"id": "stroke", "kind": "stroke", "enabled": True, "width": 2.0, "strokeAlign": "center",
                         "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff1a1a1a"}}], g, path=ARROW,
                 base=size)


def _p(id, es, en, order, dur, thumb, section="redes", tags=()):
    t = wide(f"yp16-{id}", es, en, "ytkit", dur, order=order,
             tags=[f"kit:{section}", "youtube", "cristal"] + list(tags), thumb_at=thumb)
    t.background = BACKDROP
    return t


GROW, SHRINK = 0.3, 0.28


# --- 1. «Watch More» bubble (8.80–9.70 s) --------------------------------------------------------------------------
def watch_more():
    D = 2.3
    t = _p("watch-more", "Burbuja de cristal: ver más", "Glass bubble: watch more", 18700, D, 1.2, "elementos",
           ["ver más"])
    s = B(t, D, 0.0)
    X = D - 0.55
    s.glass([bubble((1418, 296, 1613, 437, 42), 1515, 366, 40, 0.0, GROW, X + 0.2, SHRINK)], blur=20)
    s.letters("Watch", (1447, 333, 1583, 367), 700, WHITE, "Texto 1", 0.15, X)
    s.letters("More", (1460, 401, 1570, 435), 700, WHITE, "Texto 2", 0.2, X + 0.03)
    return t


# --- 2. Bar: name, round photo, Subscribe clicked (8.70–13.60 s) -------------------------------------------------
def barra_nombre():
    D = 4.9
    t = _p("barra-nombre", "Barra de cristal con nombre y suscribirse", "Glass bar with name and subscribe", 18701, D,
           2.6, "tercios", ["suscríbete", "clic", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.45
    s.glass([bubble((243, 758, 1029, 906, 74), 636, 831, 120, 0.35, GROW, X + 0.12, SHRINK)], blur=20)
    s.face("portrait-04", 636, 831, 60, 0.0, X + 0.22)
    s.letters("Beverly", (308, 783, 452, 818), 700, WHITE, "Nombre", 0.55, X, align="left")
    s.letters("Matthews", (308, 837, 522, 872), 700, WHITE, "Apellido", 0.6, X + 0.03, align="left")
    s.subscribe((732, 802, 989, 861), (819, 845), 0.65, X + 0.05, 1.7)
    s.arrow([(1.1, 1000, 1010), (1.45, 905, 880), (1.65, 880, 840), (1.95, 885, 845), (2.4, 1010, 1010)], 1.05,
            2.3, 1.7)
    return t


# --- 3. Vertical card: name, round photo, Subscribe clicked (9.50–13.50 s) ---------------------------------------
def tarjeta_vertical():
    D = 4.0
    t = _p("tarjeta-vertical", "Tarjeta vertical de cristal con suscribirse", "Vertical glass card with subscribe",
           18702, D, 2.2, "redes", ["suscríbete", "clic", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.45
    s.glass([bubble((1360, 162, 1671, 568, 42), 1515, 378, 150, 0.0, GROW, X + 0.12, SHRINK)], blur=20)
    s.letters("Jeanne", (1452, 196, 1578, 232), 700, WHITE, "Nombre", 0.12, X)
    s.letters("Edwards", (1432, 250, 1598, 286), 700, WHITE, "Apellido", 0.16, X + 0.03)
    s.face("fx-face-04", 1515, 378, 75, 0.2, X + 0.2)
    s.subscribe((1387, 471, 1644, 531), (489, 515), 0.3, X + 0.05, 1.35)
    s.arrow([(0.8, 1580, 640), (1.15, 1530, 530), (1.35, 1515, 505), (1.7, 1520, 510), (2.1, 1640, 650)], 0.75,
            2.0, 1.35)
    return t


# --- 4. «Stay Tuned» circle (14.0–14.90 s) -----------------------------------------------------------------------
def stay_tuned():
    D = 2.2
    t = _p("stay-tuned", "Círculo de cristal: no te lo pierdas", "Glass circle: stay tuned", 18703, D, 1.1,
           "elementos", ["círculo"])
    s = B(t, D, 0.0)
    X = D - 0.55
    s.glass([bubble((1185, 705, 1413, 933, 114), 1299, 819, 50, 0.0, GROW, X + 0.2, SHRINK)], blur=20)
    s.letters("Stay", (1250, 772, 1348, 810), 700, WHITE, "Texto 1", 0.15, X)
    s.letters("Tuned", (1236, 825, 1362, 863), 700, WHITE, "Texto 2", 0.2, X + 0.03)
    return t


# --- 5. Pill with the photo in the middle: Youtube · Channel (14.80–16.0 s) -------------------------------------
def pildora_canal():
    D = 2.5
    t = _p("pildora-canal", "Píldora de cristal con foto al centro", "Glass pill with a photo in the middle", 18704,
           D, 1.3, "redes", ["canal", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.5
    s.glass([bubble((174, 261, 825, 342, 40), 500, 302, 80, 0.15, GROW, X + 0.15, SHRINK)], blur=20)
    s.face("h-portrait-05", 500, 302, 72, 0.0, X + 0.25)
    s.letters("Youtube", (215, 284, 392, 320), 700, WHITE, "Texto 1", 0.35, X)
    s.letters("Channel", (608, 284, 782, 320), 700, WHITE, "Texto 2", 0.38, X + 0.03)
    return t


# --- 6. Bubble: round photo and two lines (14.80–16.0 s) ---------------------------------------------------------
def burbuja_canal():
    D = 2.5
    t = _p("burbuja-canal", "Burbuja de cristal con foto y canal", "Glass bubble with photo and channel", 18705, D,
           1.3, "redes", ["canal", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.5
    s.glass([bubble((1090, 745, 1509, 894, 74), 1164, 819, 132, 0.15, GROW, X + 0.15, SHRINK)], blur=20)
    s.face("h-man-05", 1164, 819, 62, 0.0, X + 0.25)
    s.letters("Youtube", (1268, 772, 1443, 807), 700, WHITE, "Texto 1", 0.35, X, align="left")
    s.letters("Channel", (1266, 826, 1440, 861), 700, WHITE, "Texto 2", 0.38, X + 0.03, align="left")
    return t


# --- 7. Card: round photo, name on two lines, Subscribe under it, clicked (15.95–20.40 s) --------------------------
def tarjeta_nombre():
    D = 4.45
    t = _p("tarjeta-nombre", "Tarjeta de cristal con nombre y suscribirse", "Glass card with name and subscribe",
           18706, D, 2.3, "tercios", ["suscríbete", "clic", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.45
    s.glass([bubble((228, 180, 772, 423, 120), 350, 275, 150, 0.15, GROW, X + 0.15, SHRINK)], blur=20)
    s.face("h-portrait-05", 350, 275, 75, 0.0, X + 0.25)
    s.letters("Elaine", (457, 214, 585, 249), 700, WHITE, "Nombre", 0.3, X, align="left")
    s.letters("Goodman", (457, 268, 665, 303), 700, WHITE, "Apellido", 0.33, X + 0.03, align="left")
    s.subscribe((459, 326, 663, 387), (344, 371), 0.4, X + 0.05, 1.15)
    s.arrow([(0.45, 600, 520), (0.8, 568, 400), (1.0, 562, 370), (1.4, 566, 372), (1.9, 700, 520)], 0.4, 1.8,
            1.15)
    return t


# --- 8. Bar: round photo, name on two lines, Subscribe at the right, clicked (15.95–20.40 s) ----------------------
def barra_derecha():
    D = 4.45
    t = _p("barra-suscribete", "Barra de cristal con foto y suscribirse", "Glass bar with photo and subscribe", 18707,
           D, 2.3, "tercios", ["suscríbete", "clic", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.45
    s.glass([bubble((933, 745, 1665, 895, 75), 1010, 819, 132, 0.15, GROW, X + 0.15, SHRINK)], blur=20)
    s.face("h-man-05", 1010, 819, 66, 0.0, X + 0.25)
    s.letters("Joseph", (1108, 772, 1256, 807), 700, WHITE, "Nombre", 0.3, X, align="left")
    s.letters("Robertson", (1108, 826, 1328, 861), 700, WHITE, "Apellido", 0.33, X + 0.03, align="left")
    s.subscribe((1368, 790, 1571, 850), (808, 834), 0.4, X + 0.05, 1.2)
    s.arrow([(0.5, 1560, 990), (0.85, 1480, 850), (1.05, 1468, 828), (1.45, 1472, 832), (1.95, 1600, 990)], 0.45,
            1.85, 1.2)
    return t


# --- 9. «Join us now» dark glass pill (21.05–22.0 s) --------------------------------------------------------------
def join_us():
    D = 2.2
    t = _p("join-us", "Píldora de cristal oscuro: únete", "Dark glass pill: join us now", 18708, D, 1.1, "elementos",
           ["únete"])
    s = B(t, D, 0.0)
    X = D - 0.5
    s.glass([bubble((1344, 289, 1684, 369, 40), 1514, 329, 50, 0.0, GROW, X + 0.18, SHRINK)], blur=20,
            layers=glass_layers("#1A1D22", 0.55, 0.45))
    s.letters("Join us now", (1390, 308, 1636, 345), 700, WHITE, "Texto", 0.15, X)
    return t


# --- 10. Big glass circle: photo, name, Subscribe clicked (21.0–25.90 s) ------------------------------------------
def circulo():
    D = 4.9
    t = _p("circulo", "Círculo de cristal con foto y suscribirse", "Glass circle with photo and subscribe", 18709, D,
           2.9, "redes", ["suscríbete", "clic", "foto", "círculo"])
    s = B(t, D, 0.0)
    X = D - 0.5
    s.face("h-man-01", 445, 609, 63, 0.0, X + 0.25, name="Foto (pequeña)")
    s.glass([bubble((255, 530, 635, 910, 190), 445, 609, 126, 0.45, 0.35, X + 0.12, SHRINK)], blur=20)
    s.face("h-man-01", 445, 609, 63, 0.0, X + 0.25)
    s.letters("Charles", (364, 688, 522, 722), 700, WHITE, "Nombre", 0.75, X)
    s.letters("Anderson", (343, 741, 546, 775), 700, WHITE, "Apellido", 0.78, X + 0.03)
    s.subscribe((339, 798, 553, 860), (816, 843), 0.85, X + 0.05, 1.65)
    s.arrow([(1.05, 470, 990), (1.4, 450, 880), (1.6, 447, 845), (1.95, 452, 850), (2.4, 560, 990)], 1.0, 2.3, 1.65)
    return t


# --- 11. Square card: round photo and Subscribe with a bell, clicked (21.85–26.0 s) -------------------------------
def tarjeta_cuadrada():
    D = 4.1
    t = _p("tarjeta-cuadrada", "Tarjeta cuadrada de cristal con suscribirse", "Square glass card with subscribe",
           18710, D, 2.1, "redes", ["suscríbete", "clic", "foto"])
    s = B(t, D, 0.0)
    X = D - 0.45
    s.glass([bubble((1365, 180, 1662, 477, 45), 1513, 281, 150, 0.0, GROW, X + 0.15, SHRINK)], blur=20)
    s.face("man-01", 1513, 281, 75, 0.12, X + 0.25)
    s.subscribe((1398, 380, 1630, 444), (398, 426), 0.3, X + 0.05, 1.15)
    s.arrow([(0.55, 1620, 560), (0.9, 1535, 445), (1.05, 1520, 418), (1.4, 1524, 420), (1.9, 1650, 560)], 0.5,
            1.8, 1.15)
    return t


TEMPLATES = [watch_more, barra_nombre, tarjeta_vertical, stay_tuned, pildora_canal, burbuja_canal, tarjeta_nombre,
             barra_derecha, join_us, circulo, tarjeta_cuadrada]
