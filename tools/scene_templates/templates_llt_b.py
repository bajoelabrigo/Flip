"""Logo lower thirds, second set (2026-10-31): the four of «Lower Third V2» (52324162.mp4, 1920×1080 at 60 fps), a
dark rounded card with a vivid green accent and Poppins. Every edge plays the curve measured at 60 fps
(lt_ref/lt2a…lt2d.json, summarised in tienda/plantillas/estudio-52324162/NOTAS.md); each piece leaves with its
entrance played backwards, as the reference does. Laid out where the reference has them, then moved to the bottom
left as it shows each one alone over a video. The logo is a slot («Tu logo», the premium flame as the sample).
Order 8570-8573. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

from pathlib import Path

from kit import Box, label, photo_bg, wide
from llt_motion import frames_of, mask_track
from scene import fill, glow, keys

FONT = "Poppins"
DARK = "#1C1C1C"
GREEN = "#3DFA7D"
DEEP = "#1F6B3C"  # the progress line's unfilled part
WHITE = "#FFFFFF"
GREY = "#9A9A9A"
FPS = 60.0  # the measurements' rate: frame numbers below are 60 fps frames
_FONT_DIR = Path(__file__).resolve().parents[4] / "codigo" / "flip-addons" / "build" / "stage" / "fonts.basic" / \
    "fonts" / "poppins"
_FACES = {600: "SemiBold", 700: "Bold"}


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt2-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "logo"] + tags,
                **kw)


def fit(text: str, width: float, weight: int = 700) -> float:
    """The Poppins size at which `text`'s ink is `width` px wide (what the reference measures)."""
    from PIL import ImageFont
    f = ImageFont.truetype(str(_FONT_DIR / f"Poppins-{_FACES[weight]}.ttf"), 200)
    bb = f.getbbox(text)
    return round(width / (bb[2] - bb[0]) * 200, 1)


def curve(points):
    """[(frame, value), ...] at 60 fps -> f(frame), linear between, held outside."""
    def f(fr):
        if fr <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if fr <= b:
                return va + (vb - va) * (fr - a) / (b - a)
        return points[-1][1]
    return f


class Piece:
    """One lower third: its reference coordinates moved by (dx, dy); its entrance mirrored into the exit."""

    def __init__(self, t, dur, dx, dy, start=0):
        self.t, self.dur, self.dx, self.dy, self.start = t, dur, dx, dy, start

    def frame(self, u):
        """The reference frame (60 fps) clip time u plays: the entrance, then the same backwards at the end."""
        mirrored = min(u, self.dur - u)
        return self.start + mirrored * FPS

    def box(self, x0, y0, x1, y1):
        return Box(x0 + self.dx, y0 + self.dy, x1 - x0, y1 - y0)

    def shape(self, name, colour, full, rect, radius, kind="rounded-rectangle", layers=None):
        """A shape laid out in `full` (reference x0, y0, x1, y1) that covers rect(frame) every frame."""
        box = self.box(*full)
        motion = []
        for u in frames_of(self.dur):
            x0, y0, x1, y1 = rect(self.frame(u))
            w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
            motion.append((u, {"sx": w / box.w, "sy": h / box.h, "dx": (x0 + x1) / 2 + self.dx - box.cx,
                               "dy": (y0 + y1) / 2 + self.dy - box.cy}, "linear"))
        clip = self.t.solid(self.t.track("shape", name), colour, 0.0, self.dur, box, motion, radius=radius, kind=kind,
                            layers=layers)
        clip["name"] = name
        return clip

    def text(self, content, ink_left, centre_y, width, weight, colour, name, align="left", opacity=None,
             reveal=None, editable=True, shift=None):
        """A Poppins line whose ink is `width` wide from `ink_left` (or centred on it), centred on `centre_y`;
        opacity(frame) fades it, reveal(frame) = (x0, y0, x1, y1) shows only that part of it."""
        size = fit(content, width, weight)
        h = size * 1.6
        w = width + size * 2
        x = ink_left - size * 0.06 if align == "left" else ink_left - w / 2
        box = Box(x + self.dx, centre_y - h / 2 + self.dy, w, h)
        sh = (lambda fr: (lambda v: v if isinstance(v, tuple) else (v, 0.0))(shift(fr))) if shift else None
        motion = [(u, dict(zip(("dx", "dy"), sh(self.frame(u)))), "linear") for u in frames_of(self.dur)]             if shift else None
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, box, FONT, size, colour,
                     weight=weight, align=align, name=name, line=1.0, editable=editable, motion=motion)
        if opacity:
            clip["opacity"] = keys([(u, opacity(self.frame(u)), "linear") for u in frames_of(self.dur)])
        if reveal:
            def local(u):
                x0, y0, x1, y1 = self._moved(reveal(self.frame(u)))
                dx, dy = sh(self.frame(u)) if shift else (0.0, 0.0)
                return (x0 - dx, y0 - dy, x1 - dx, y1 - dy)
            mask_track(self.t, clip, box, local, self.dur)
        return clip

    def _moved(self, r):
        x0, y0, x1, y1 = r
        return (x0 + self.dx, y0 + self.dy, x1 + self.dx, y1 + self.dy)


def _ramp(a, b):
    return curve([(a, 0.0), (b, 1.0)])


def card():
    """A: the dark card grows from its top-left corner with a little overshoot, the white logo badge pops, the white
    name card rises from the bottom inside it, the green web pill opens to the left and a ring pulses off the logo."""
    D = 6.0
    t = _kit("tarjeta", "Tercio con logo: tarjeta oscura y ficha blanca", "Logo lower third: dark card and white tag",
             D, 8570, ["nombre", "tarjeta", "verde", "web"], thumb_at=3.0)
    photo_bg(t, "h-office-01", s1=1.03, label="Tu video")
    p = Piece(t, D, -154, 358)
    right = curve([(0, 250), (2, 330), (4, 531), (6, 621), (8, 682), (10, 720), (12, 741), (14, 749), (16, 750),
                   (24, 735), (32, 728)])
    k = lambda fr: (right(fr) - 250) / 478  # noqa: E731  how open the card is (1 = its rest size)
    p.shape("Tarjeta", DARK, (250, 365, 728, 622), lambda fr: (250, 365, 250 + 478 * k(fr), 365 + 257 * k(fr)), 40)
    # The badge: a white disc with the logo, popping out with the card.
    pop = curve([(1, 0.0), (3, 0.6), (5, 1.08), (7, 1.0)])
    disc = lambda fr: (306 - 28 * pop(fr), 419 - 28 * pop(fr), 306 + 28 * pop(fr), 419 + 28 * pop(fr))  # noqa: E731
    # The pulse: a grey ring opens off the badge and fades (frames 52-80).
    ring_r = curve([(48, 28), (60, 41), (72, 47), (84, 50)])
    ring_o = curve([(48, 0.0), (52, 0.85), (64, 0.75), (84, 0.0)])
    ring = p.shape("Pulso", "#8C8C8C", (256, 369, 356, 469), lambda fr: (306 - ring_r(fr), 419 - ring_r(fr),
                                                                        306 + ring_r(fr), 419 + ring_r(fr)), 0,
                   kind="ellipse")
    ring["opacity"] = keys([(u, ring_o(p.frame(u)), "linear") for u in frames_of(D)])
    p.shape("Insignia", WHITE, (278, 391, 334, 447), disc, 0, kind="ellipse")
    logo = p.box(288, 401, 324, 437)
    motion = [(u, {"s": pop(p.frame(u))}, "linear") for u in frames_of(D)]
    t.photo(t.track("video", "Logo"), "logo-11", 0.0, D, logo, motion, label="Tu logo", brandRole="logo")
    # The white tag rises from below the card's bottom (its top edge measured), cut by the card.
    top = curve([(16, 640), (18, 625), (20, 579), (22, 525), (24, 507), (26, 497), (28, 491), (30, 487), (34, 483),
                 (38, 482)])
    p.shape("Ficha", WHITE, (273, 482, 704, 598), lambda fr: (273, top(fr), 704, min(622 - 22 * (1 - min(1, k(fr))),
                                                                                    top(fr) + 116)), 22)
    shown = lambda fr: (273, top(fr), 704, 622)  # noqa: E731
    p.text("Murad Guliyev", 300, 527, 297, 700, DARK, "Nombre", opacity=_ramp(18, 30), reveal=shown)
    p.text("motion designer", 301, 561, 181, 600, DARK, "Cargo", opacity=_ramp(22, 32), reveal=shown)
    # The green web pill opens to the left from its right end.
    left = curve([(26, 728), (28, 660), (30, 618), (32, 587), (34, 571), (36, 561), (38, 555), (40, 551), (44, 547)])
    p.shape("Web", GREEN, (547, 399, 700, 434), lambda fr: (left(fr), 399, min(728 - 6, left(fr) + 153), 434), 8,
            layers=[fill(GREEN), glow(GREEN, 22, 0.55)])
    p.text("www.tuweb.com", 623, 416, 116, 600, DARK, "Web", align="center", shift=lambda fr: left(fr) - 547,
           reveal=lambda fr: (left(fr), 399, min(722, left(fr) + 153), 434))
    return t


def pill():
    """B: a dark disc pops on the right with a green check badge, stretches left into a pill, the name shows from
    right to left with two flickers, and a green tab drops from behind it with the role."""
    D = 6.0
    t = _kit("pastilla", "Tercio con logo: pastilla oscura y pestaña verde", "Logo lower third: dark pill and green tab",
             D, 8571, ["nombre", "pastilla", "verde"], thumb_at=3.0)
    photo_bg(t, "h-office-01", s1=1.03, label="Tu video")
    p = Piece(t, D, -99, 58)
    # The tab first: it hangs behind the pill.
    drop = curve([(46, -72), (52, -40), (54, -25), (56, -17), (58, -13), (60, -9), (62, -8), (66, 0)])
    p.shape("Pestaña", GREEN, (273, 840, 704, 922), lambda fr: (273, 840 + drop(fr), 704, 922 + drop(fr)) if fr >= 46
            else (488, 860, 488, 860), 16)
    p.text("motion designer", 488, 893, 245, 600, DARK, "Cargo", align="center", opacity=_ramp(56, 66))
    seed = curve([(0, 0), (2, 35), (4, 66), (6, 90), (8, 106), (10, 116), (12, 120), (16, 118)])
    left = curve([(16, 819), (20, 814), (24, 803), (28, 775), (30, 748), (32, 699), (34, 477), (36, 328), (38, 284),
                  (40, 263), (42, 232), (44, 219), (46, 210), (48, 203), (50, 199), (54, 195)])

    def body(fr):
        if fr < 16:
            w = seed(fr)
            return (878 - w / 2, 801 - w / 2, 878 + w / 2, 801 + w / 2)
        return (left(fr), 742, 937, 860)
    p.shape("Pastilla", DARK, (195, 742, 937, 860), body, 59)
    badge = lambda fr: seed(fr) * 57 / 118  # noqa: E731  the green disc grows with the dark one
    p.shape("Insignia", GREEN, (850, 773, 908, 829), lambda fr: (879 - badge(fr) / 2, 801 - badge(fr) / 2,
                                                                 879 + badge(fr) / 2, 801 + badge(fr) / 2), 0,
            kind="ellipse")
    p.text("×", 879, 800, 22, 600, DARK, "Icono", align="center", opacity=_ramp(4, 10), editable=False)
    stroke = lambda colour, w: [{"id": "stroke", "kind": "stroke", "enabled": True,  # noqa: E731
                                 "paint": {"kind": "solid", "color": "#FF" + colour[1:]}, "width": w,
                                 "opacity": 1.0, "strokeAlign": "inside"}]
    p.shape("Aro", DARK, (865, 787, 893, 815), lambda fr: (879 - badge(fr) / 4, 801 - badge(fr) / 4,
                                                          879 + badge(fr) / 4, 801 + badge(fr) / 4), 0,
            kind="ellipse", layers=stroke(DARK, 2.5))
    ring = curve([(30, 0), (40, 35), (44, 34)])
    p.shape("Anillo", GREEN, (849, 771, 909, 831), lambda fr: (879 - ring(fr), 801 - ring(fr), 879 + ring(fr),
                                                              801 + ring(fr)), 0, kind="ellipse",
            layers=stroke(GREEN, 2.0))
    # The name: shown from the right edge leftwards (frames 34-44), flickering at 38 and 42.
    flick = curve([(34, 1), (37, 1), (38, 0.25), (39, 1), (41, 1), (42, 0.25), (43, 1)])
    p.text("Murad Guliyev", 256, 801, 357, 700, WHITE, "Nombre", opacity=flick,
           reveal=lambda fr: (body(fr)[0] + 20 if fr >= 16 else 940, 742, 800, 860))
    return t


def bar_tag():
    """C: a dark bar sweeps in from the left with the name, and a green tag grows inside its right end."""
    D = 6.0
    t = _kit("barra-etiqueta", "Tercio con logo: barra oscura y etiqueta verde", "Logo lower third: dark bar and green tag",
             D, 8572, ["nombre", "barra", "verde"], thumb_at=3.0)
    photo_bg(t, "h-office-01", s1=1.03, label="Tu video")
    p = Piece(t, D, -927, 461, start=20)
    right = curve([(24, 1023), (26, 1023), (28, 1071), (30, 1178), (32, 1472), (34, 1581), (36, 1632), (38, 1663),
                   (40, 1684), (42, 1697), (44, 1705), (50, 1714), (56, 1717)])
    # The whole bar slides in from the left with the name inside it, widening a little as it lands.
    left = lambda fr: right(fr) - 661 - 33 * min(1.0, max(0.0, (right(fr) - 1660) / 57))  # noqa: E731
    p.shape("Barra", DARK, (1023, 425, 1717, 519), lambda fr: (left(fr), 425, right(fr), 519), 22)
    p.text("Murad Guliyev", 1060, 470, 336, 700, WHITE, "Nombre", shift=lambda fr: left(fr) - 1023,
           reveal=lambda fr: (max(0, left(fr)), 425, right(fr) - 8, 519))
    tl = curve([(42, 1690), (44, 1673), (46, 1536), (48, 1494), (50, 1472), (52, 1459), (54, 1450), (56, 1445),
                (60, 1440)])
    tr = curve([(42, 1690), (44, 1717), (52, 1700), (60, 1690)])
    p.shape("Etiqueta", GREEN, (1440, 446, 1690, 498), lambda fr: (tl(fr), 446, min(tr(fr), 1711), 498), 10,
            layers=[fill(GREEN), glow(GREEN, 22, 0.5)])
    # Its text rides in on the tag's left edge, cut by the bar's right end.
    p.text("motion designer", 1565, 472, 208, 600, DARK, "Cargo", align="center", opacity=_ramp(43, 46),
           shift=lambda fr: tl(fr) - 1440, reveal=lambda fr: (tl(fr), 446, min(tr(fr), 1711), 498))
    return t


def big_name():
    """D: a dark bar rises with a big name that flickers in, a green tab rises from behind it with the role, and a
    green line along its bottom fills like a progress bar while it shows."""
    D = 6.0
    t = _kit("nombre-grande", "Tercio con logo: nombre grande y barra de progreso",
             "Logo lower third: big name and progress line", D, 8573, ["nombre", "barra", "verde", "progreso"],
             thumb_at=3.0)
    photo_bg(t, "h-office-01", s1=1.03, label="Tu video")
    p = Piece(t, D, -923, 102, start=24)
    rise = curve([(26, 899), (28, 826), (30, 795), (32, 778), (34, 768), (36, 760), (38, 755), (40, 751), (44, 746),
                  (48, 744)])
    k = lambda fr: (899 - rise(fr)) / (899 - 744)  # noqa: E731
    bottom = lambda fr: 899 - 30 * k(fr)  # noqa: E731
    tab = curve([(44, 760), (50, 718), (52, 704), (54, 694), (56, 690), (60, 685)])
    p.shape("Pestaña", GREEN, (1110, 685, 1623, 760), lambda fr: (1110, tab(fr), 1623, tab(fr) + 75) if fr >= 44
            else (1366, 760, 1366, 760), 16)
    p.text("motion designer", 1366, 713, 295, 600, DARK, "Cargo", align="center", opacity=_ramp(46, 52),
           reveal=lambda fr: (1110, 600, 1623, 744))
    p.shape("Barra", DARK, (1019, 744, 1715, 878), lambda fr: (1019, rise(fr), 1715, bottom(fr) + 9), 6)
    p.shape("Línea", DEEP, (1019, 869, 1715, 878), lambda fr: (1019, bottom(fr), 1715, bottom(fr) + 9) if k(fr) > 0.05
            else (1019, 899, 1019, 899), 0, kind="rectangle")
    # The progress fill: from frame 40 it runs 1.8 px a frame (it plays forwards, also during the exit).
    fill_box = p.box(1019, 869, 1715, 878)
    motion = []
    for u in frames_of(D):
        fr = p.frame(u)
        x1 = min(1715, 1019 + max(0.0, (24 + u * FPS) - 28) * 2.0) if k(fr) > 0.05 else 1019
        y0 = bottom(fr)
        w = x1 - 1019
        motion.append((u, {"sx": w / fill_box.w, "sy": 1.0, "dx": 1019 + w / 2 + p.dx - fill_box.cx,
                           "dy": y0 + 4.5 + p.dy - fill_box.cy}, "linear"))
    line = t.solid(t.track("shape", "Progreso"), GREEN, 0.0, D, fill_box, motion)
    line["name"] = "Progreso"
    flick = curve([(26, 0.0), (28, 0.45), (36, 0.45), (38, 1.0), (40, 0.4), (42, 1.0)])
    # The name rides up with the bar, in its middle.
    p.text("Murad Guliyev", 1362, 807, 446, 700, WHITE, "Nombre", align="center", opacity=flick,
           shift=lambda fr: (0.0, (rise(fr) + bottom(fr)) / 2 - (744 + 869) / 2),
           reveal=lambda fr: (1019, rise(fr), 1715, bottom(fr)))
    return t


TEMPLATES = [card, pill, bar_tag, big_name]
