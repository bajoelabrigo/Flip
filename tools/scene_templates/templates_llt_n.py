"""Red and navy lower thirds, fourteenth set (2026-11-07): the thirteen of 1127426.mp4 (960×540 at 30 fps), Josefin
Sans (Century Gothic-like titles, justified paragraphs, light italic in the two big boxes) in navy, white and red
(#D6193D) with navy (#0B2747) and translucent slate boxes. The reference carries a stock-site logo and name: here the
logo is a logo slot (the Flip play symbol as the sample) and the names are neutral placeholders. Moves: the logo
square pops in, bars and boxes grow from their left (or down from a red band), lines grow, texts are uncovered by
their boxes or slide out from behind a square; each piece leaves with its entrance backwards. Measured on the 960
frame, ×1.6 (0.8 of the reference's size: its boxes are big) and laid out bottom-left (left 120, bottom 960), with no
background. Order 8730-8742. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import label, wide
from llt_motion import frames_of
from scene import Box, gradient, no_stroke
from templates_llt_f import Piece, table

f6._FILES[("Josefin Sans", 400)] = "fonts.extra/fonts/josefinsans/JosefinSans-Regular.ttf"
f6._FILES[("Josefin Sans", 600)] = "fonts.extra/fonts/josefinsans/JosefinSans-SemiBold.ttf"
FONT = "Josefin Sans"
RED = "#D6193D"
NAVY = "#0B2747"
WHITE = "#FFFFFF"
SLATE = "#3A4860"
FPS = 30.0
S = 1.6
EASE = table({0: 0.0, 2: 0.2, 4: 0.45, 6: 0.65, 8: 0.79, 10: 0.88, 12: 0.94, 14: 0.975, 16: 0.99, 18: 1.0})
POP = table({0: 0.0, 3: 0.55, 6: 1.08, 8: 1.04, 10: 1.0})
LOREM = ("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the "
         "industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and "
         "scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into "
         "electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release "
         "of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software "
         "like Aldus PageMaker including versions of Lorem Ipsum.")
SHORT = ("This text tells who is speaking and what they do. Write a sentence or two here: it wraps inside the box "
         "and the box keeps its size, so a longer line simply runs on to the next one.")


def E(fr, start, frames):
    return EASE((fr - start) * 18 / frames)


class RedPiece(Piece):
    """Laid out in 960 px: `bbox` lands with its left at 120 and bottom at 960."""

    def __init__(self, t, dur, bbox):
        super().__init__(t, dur, 0)
        self.bx0, self.by1 = bbox[0], bbox[3]

    def frame(self, u):
        return min(u, self.dur - u) * FPS

    def R(self, r):
        return (120 + (r[0] - self.bx0) * S, 960 - (self.by1 - r[1]) * S, 120 + (r[2] - self.bx0) * S,
                960 - (self.by1 - r[3]) * S)


def piece(id, es, en, order, D, bbox, tags=()):
    t = wide(f"llt14-{id}", es, en, "ytkit", D, order=order,
             tags=["kit:lowerthirds", "tercio", "rojo", "azul marino"] + list(tags), thumb_at=round(D / 2, 1))
    return t, RedPiece(t, D, bbox)


def grow(p, full, kind, start, frames=16):
    """fr -> screen rect of `full` (960 px) growing from frame `start`: ltr, rtl, ttb, btt, or pop (from its
    middle, a little past full size)."""
    x0, y0, x1, y1 = p.R(full)

    def r(fr):
        if kind == "pop":
            k = POP(fr - start)
            cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 * k, (y1 - y0) / 2 * k
            return (cx - hw, cy - hh, cx + hw, cy + hh)
        k = E(fr, start, frames)
        if kind == "ltr":
            return (x0, y0, x0 + (x1 - x0) * k, y1)
        if kind == "rtl":
            return (x1 - (x1 - x0) * k, y0, x1, y1)
        if kind == "ttb":
            return (x0, y0, x1, y0 + (y1 - y0) * k)
        return (x0, y1 - (y1 - y0) * k, x1, y1)
    return r


def shape(p, name, colour, full, fn, layers=None, kind=None, alpha=1.0, skew=0.0):
    clip = p.shape(name, colour, p.R(full), fn, alpha=alpha, skew=skew)
    if layers:
        clip["shapeStyle"]["layers"] = layers
    if kind:
        clip["shapeStyle"]["kind"] = kind
    return clip


def text(p, content, ink, colour, name, weight=400, align="left", reveal=None, shift=None):
    """One line whose capitals span `ink` (960 px); shift(fr) = (dx, dy) in 960 px."""
    x0, y0, x1, y1 = p.R(ink)
    edge = x0 if align == "left" else x1 if align == "right" else (x0 + x1) / 2
    sh = (lambda fr: tuple(v * S for v in shift(fr))) if shift else None
    return p.text(content, edge, y0, y1, x1 - x0, FONT, weight, colour, name, align=align, case="none", shift=sh,
                  reveal=reveal)


def paragraph(p, content, rect, size, name, colour=WHITE, italic=False, reveal=None, line=1.25):
    """Justified text wrapping inside `rect` (960 px), `size` in 960 px."""
    from llt_motion import mask_track
    x0, y0, x1, y1 = p.R(rect)
    box = Box(x0, y0, x1 - x0, y1 - y0)
    clip = label(p.t, p.t.track("text", name), content, 0.0, p.dur, box, FONT, round(size * S, 1), colour,
                 weight=400, align="justify", valign="top", line=line, name=name, italic=italic)
    if reveal:
        def local(u):
            a = reveal(p.frame(u))
            if a[2] - a[0] < 0.5 or a[3] - a[1] < 0.5:
                return (-4000.0, -4000.0, -3999.0, -3999.0)
            return a
        mask_track(p.t, clip, box, local, p.dur)
    return clip


def logo(p, rect, start, square=True, inset=0.2):
    """The logo slot popping in at frame `start`, on a red square (or alone, white)."""
    if square:
        shape(p, "Cuadro del logo", RED, rect, grow(p, rect, "pop", start))
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    inner = (x0 + w * inset, y0 + h * inset, x1 - w * inset, y1 - h * inset)
    sx0, sy0, sx1, sy1 = p.R(inner)
    box = Box(sx0, sy0, sx1 - sx0, sy1 - sy0)
    motion = [(u, {"s": max(1e-4, POP(p.frame(u) - start - 2))}, "linear") for u in frames_of(p.dur)]
    p.t.photo(p.t.track("video", "Logo"), "logo-flip", 0.0, p.dur, box, motion, label="Tu logo", brandRole="logo")


def rise(dist, start, frames=16):
    return lambda fr: (0.0, dist * (1 - E(fr, start, frames)))


def slide(dist, start, frames=16):
    return lambda fr: (-dist * (1 - E(fr, start, frames)), 0.0)


# --- The thirteen -------------------------------------------------------------------------------------------------


def hexagon():
    t, p = piece("hexagono", "Tercio rojo: logo en hexágono y ficha blanca", "Red lower third: hexagon logo, white tag",
                 8730, 5.0, (50, 314, 468, 412), ["logo"])
    box = (137, 336, 468, 388)
    w = grow(p, box, "ltr", 10, 16)
    shape(p, "Ficha", WHITE, box, w)
    text(p, "LOWER THIRDS", (145, 345, 461, 381), NAVY, "Nombre", reveal=w)
    shape(p, "Hexágono", RED, (50, 314, 137, 412), grow(p, (50, 314, 137, 412), "pop", 0), kind="hexagon")
    logo(p, (50, 314, 137, 412), 2, square=False, inset=0.24)
    return t


def brand():
    t, p = piece("marca", "Tercio rojo: logo, barra inclinada y nombre", "Red lower third: logo, slash and name", 8731,
                 4.5, (113, 114, 581, 202), ["logo"])

    def slash(fr):
        # A red block that thins down to the slash.
        k = E(fr, 10, 16)
        w = 24 + (52 - 24) * (1 - k)
        return p.R((186, 114, 186 + w, 201))
    shape(p, "Barra", RED, (186, 114, 210, 201), slash, skew=11)
    shape(p, "Subrayado", NAVY, (211, 199, 581, 202), grow(p, (211, 199, 581, 202), "ltr", 30, 16))
    logo(p, (113, 118, 180, 198), 38, square=False, inset=0.0)
    text(p, "YOUR BRAND", (211, 143, 575, 185), WHITE, "Nombre", reveal=lambda fr: p.R((205, 100, 600, 188)),
         shift=rise(60, 40))
    return t


def first_title():
    t, p = piece("primer-titulo", "Tercio rojo: logo, título y caja con texto", "Red lower third: logo, title, text box",
                 8732, 4.8, (50, 239, 688, 414), ["logo", "caja"])
    nb = grow(p, (109, 329, 688, 414), "ltr", 4, 18)
    shape(p, "Caja", NAVY, (109, 329, 688, 414), nb)
    wb = grow(p, (61, 285, 410, 329), "ltr", 8, 16)
    shape(p, "Ficha", WHITE, (61, 285, 410, 329), wb)
    text(p, "Your First Title", (145, 297, 323, 318), NAVY, "Título", align="left", reveal=wb)
    text(p, "Lower Third - Text 2", (120, 340, 275, 352), WHITE, "Subtítulo", reveal=nb)
    paragraph(p, SHORT, (120, 368, 677, 410), 14.0, "Texto", reveal=nb, line=1.15)
    logo(p, (50, 239, 108, 295), 0)
    return t


def two_squares():
    t, p = piece("dos-cuadros", "Tercio rojo: dos cuadros y dos líneas", "Red lower third: two squares, two lines",
                 8733, 6.0, (95, 77, 342, 171))
    cut = lambda fr: p.R((119, 70, 360, 175))  # noqa: E731
    text(p, "YOUR TEXT 1", (127, 86, 338, 115), NAVY, "Nombre", reveal=cut, shift=slide(230, 54, 16))
    text(p, "YOUR TEXT 2", (127, 135, 342, 165), WHITE, "Cargo", reveal=cut, shift=slide(230, 58, 16))
    shape(p, "Cuadro", RED, (95, 77, 119, 123), grow(p, (95, 77, 119, 123), "ttb", 0, 24))
    shape(p, "Cuadro 2", NAVY, (95, 125, 119, 171), grow(p, (95, 125, 119, 171), "btt", 30, 12))
    return t


def logo_text():
    t, p = piece("logo-texto", "Tercio rojo: logo y caja con párrafo", "Red lower third: logo and a paragraph box",
                 8734, 6.0, (53, 273, 653, 416), ["logo", "caja"])
    line = grow(p, (153, 295, 653, 416), "ltr", 30, 14)
    open_ = grow(p, (153, 295, 653, 416), "ttb", 46, 14)

    def nb(fr):
        # A thin line runs to the right along the top, then the box opens down from it.
        a, b = line(fr), open_(fr)
        return (a[0], a[1], a[2], max(a[1] + 2.5 * S, b[3]))
    shape(p, "Caja", NAVY, (153, 295, 653, 416), nb)
    paragraph(p, LOREM, (161, 299, 646, 412), 12.2, "Texto", reveal=nb, line=1.25)
    shape(p, "Marco del logo", RED, (53, 273, 153, 372), grow(p, (53, 273, 153, 372), "pop", 0))
    logo(p, (53, 273, 153, 372), 2, square=False, inset=0.18)
    return t


def logo_lines():
    t, p = piece("logo-lineas", "Tercio rojo: logo, línea y dos líneas", "Red lower third: logo, line and two lines",
                 8735, 6.0, (55, 96, 330, 174), ["logo"])
    logo(p, (55, 96, 122, 172), 0, square=False, inset=0.0)
    shape(p, "Línea", RED, (133, 96, 136, 174), grow(p, (133, 96, 136, 174), "ttb", 4, 10))
    cut = lambda fr: p.R((136, 90, 350, 180))  # noqa: E731
    text(p, "YOUR TEXT 1", (142, 102, 330, 127), NAVY, "Nombre", reveal=cut, shift=slide(200, 8, 16))
    text(p, "TEXT 2", (142, 139, 226, 164), WHITE, "Cargo", reveal=cut, shift=slide(200, 12, 16))
    return t


def designer():
    t, p = piece("disenador", "Tercio rojo: nombre en un marco rojo", "Red lower third: name in a red frame", 8736,
                 6.0, (164, 297, 588, 373))
    shape(p, "Marco abajo", RED, (270, 369, 588, 373), grow(p, (270, 369, 588, 373), "ltr", 0, 30))
    shape(p, "Marco lado", RED, (585, 297, 588, 373), grow(p, (585, 297, 588, 373), "btt", 28, 10))
    shape(p, "Marco arriba", RED, (476, 297, 588, 300), grow(p, (476, 297, 588, 300), "rtl", 36, 10))
    text(p, "Creative Designer", (164, 324, 579, 352), WHITE, "Nombre", weight=600,
         reveal=lambda fr: p.R((150, 290, 600, 355)), shift=rise(45, 30))
    return t


def big_box():
    t, p = piece("caja-grande", "Tercio rojo: caja grande con título y párrafo", "Red lower third: big box, title, text",
                 8737, 6.0, (211, 67, 811, 388), ["caja"])
    shape(p, "Banda", RED, (211, 67, 811, 76), grow(p, (211, 67, 811, 76), "ltr", 0, 12))
    box = grow(p, (211, 76, 811, 364), "ttb", 10, 16)
    shape(p, "Caja", SLATE, (211, 76, 811, 364), box, alpha=0.88)
    text(p, "YOUR TEXT 1", (222, 89, 448, 116), WHITE, "Título", reveal=box)
    paragraph(p, LOREM, (222, 144, 803, 356), 16.6, "Texto", italic=True, reveal=box, line=1.3)
    shape(p, "Pestaña", RED, (211, 364, 252, 388), grow(p, (211, 364, 252, 388), "ttb", 22, 8))
    logo(p, (219, 366, 244, 386), 26, square=False, inset=0.0)
    return t


def tall_box():
    t, p = piece("caja-alta", "Tercio rojo: caja alta con borde rojo", "Red lower third: tall box, red edge", 8738, 6.0,
                 (358, 78, 664, 378), ["caja"])
    shape(p, "Borde", RED, (658, 78, 664, 378), grow(p, (658, 78, 664, 378), "ttb", 0, 24))
    box = grow(p, (358, 78, 658, 378), "rtl", 36, 16)
    shape(p, "Caja", SLATE, (358, 78, 658, 378), box, alpha=0.88)
    text(p, "YOUR TEXT 1", (420, 94, 646, 123), WHITE, "Título", reveal=box)
    paragraph(p, LOREM, (362, 155, 648, 372), 14.6, "Texto", italic=True, reveal=box, line=1.3)
    logo(p, (360, 96, 390, 122), 50)
    return t


def navy_bar():
    t, p = piece("barra-azul", "Tercio rojo: logo y barra azul marino", "Red lower third: logo and navy bar", 8739, 6.0,
                 (51, 345, 898, 414), ["logo", "barra"])
    bar = grow(p, (129, 345, 898, 414), "ltr", 30, 18)
    shape(p, "Barra", NAVY, (129, 345, 898, 414), bar)
    text(p, "Lower Third 01 - Text", (156, 364, 511, 396), WHITE, "Nombre", reveal=bar, shift=slide(60, 34, 16))
    logo(p, (51, 345, 121, 414), 0)
    return t


def slate_bar():
    t, p = piece("barra-gris", "Tercio rojo: logo, barra gris y ficha", "Red lower third: logo, slate bar and tag",
                 8740, 6.0, (145, 111, 780, 221), ["logo", "barra"])
    bar = grow(p, (214, 115, 775, 176), "ltr", 70, 16)
    shape(p, "Barra", SLATE, (214, 115, 775, 176), bar,
          layers=[gradient([(0.0, "#2F3B52", 0.95), (1.0, "#7C8698", 0.8)], angle=0), no_stroke()])
    shape(p, "Borde", RED, (774, 111, 780, 180), grow(p, (774, 111, 780, 180), "ttb", 84, 8))
    text(p, "Lower Third 02 - Text 1", (228, 131, 610, 162), WHITE, "Nombre", reveal=bar, shift=slide(60, 72, 16))
    tag = grow(p, (239, 182, 416, 215), "ltr", 92, 12)
    shape(p, "Ficha", "#E9EDF2", (239, 182, 416, 215), tag)
    shape(p, "Subrayado", RED, (237, 215, 419, 221), grow(p, (237, 215, 419, 221), "ltr", 96, 12))
    text(p, "L. T. - Text 2", (269, 190, 388, 206), NAVY, "Cargo", reveal=tag)
    logo(p, (145, 111, 214, 180), 0)
    return t


def tab_box():
    t, p = piece("pestana", "Tercio rojo: logo, pestaña y caja con texto", "Red lower third: logo, tab and text box",
                 8741, 5.8, (53, 303, 652, 400), ["logo", "caja"])
    tab = grow(p, (154, 303, 303, 332), "ltr", 8, 12)
    shape(p, "Pestaña", "#E9EDF2", (154, 303, 303, 332), tab)
    text(p, "L. T. - Text 1", (177, 314, 278, 325), "#55606F", "Título", reveal=tab)
    nb = grow(p, (154, 333, 652, 400), "ltr", 10, 18)
    shape(p, "Caja", NAVY, (154, 333, 652, 400), nb)
    text(p, "Lower Third - Text 2", (159, 344, 292, 354), WHITE, "Subtítulo", reveal=nb)
    paragraph(p, SHORT, (159, 366, 640, 398), 12.6, "Texto", reveal=nb, line=1.15)
    shape(p, "Marco del logo", RED, (53, 303, 152, 400), grow(p, (53, 303, 152, 400), "pop", 0))
    logo(p, (53, 303, 152, 400), 2, square=False, inset=0.18)
    return t


def red_line():
    t, p = piece("linea-roja", "Tercio rojo: logo, línea roja y caja ancha", "Red lower third: logo, red line, wide box",
                 8742, 6.0, (51, 186, 890, 390), ["logo", "caja"])
    shape(p, "Línea", RED, (51, 263, 890, 270), grow(p, (51, 263, 890, 270), "ltr", 10, 20))
    box = grow(p, (51, 270, 890, 390), "ttb", 28, 14)
    shape(p, "Caja", SLATE, (51, 270, 890, 390), box, alpha=0.85)
    text(p, "Lower Third 03 - Text", (72, 282, 249, 297), WHITE, "Título", reveal=box)
    paragraph(p, LOREM, (72, 312, 870, 386), 14.5, "Texto", reveal=box, line=1.15)
    logo(p, (51, 186, 121, 256), 4)
    return t


TEMPLATES = [hexagon, brand, first_title, two_squares, logo_text, logo_lines, designer, big_box, tall_box, navy_bar,
             slate_bar, tab_box, red_line]
