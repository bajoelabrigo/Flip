"""White box lower thirds, tenth set (2026-11-07): the twelve of 51639729.mp4 (1920×1080 at 29.97 fps), Montserrat
(ExtraBold names in capitals, Bold roles), white boxes with black type and white type over video. Moves: words slide
into place inside their own edges, letters pop in one by one, and white boxes grow from a line; each piece leaves
with its entrance played backwards. Laid out where the reference has them (left, middle or right), with no
background. Order 8650-8661. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import wide
from scene import tanim
from templates_llt_f import Piece, table

for w, file in ((700, "Montserrat-Bold"), (800, "Montserrat-ExtraBold"), (900, "Montserrat-Black")):
    f6._FILES[("Montserrat", w)] = f"fonts.basic/fonts/montserrat/{file}.ttf"
FONT = "Montserrat"
WHITE = "#FFFFFF"
INK = "#111111"
FPS = 29.97
EASE = table({0: 0.0, 2: 0.2, 4: 0.45, 6: 0.65, 8: 0.79, 10: 0.88, 12: 0.94, 14: 0.975, 16: 0.99, 18: 1.0})


class BoxPiece(Piece):
    def __init__(self, t, dur):
        super().__init__(t, dur, 0)

    def frame(self, u):
        return min(u, self.dur - u) * FPS


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt10-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "blanco"] + tags,
                **kw)


def caps_of(top, bottom, descenders):
    """The capitals' rows of an ink box (mixed case with descenders: the top 78 %)."""
    return (top, top + (bottom - top) * 0.78) if descenders else (top, bottom)


def slide(p, content, ink, weight, colour, name, way, start, align="left", descenders=False, dist=None, frames=18):
    """A line sliding into place from `way` (left, right, up, down), shown only inside its own ink box."""
    x0, y0, x1, y1 = ink
    caps = caps_of(y0, y1, descenders)
    d = dist if dist is not None else ((x1 - x0) if way in ("left", "right") else (y1 - y0) * 1.3)
    sign = {"left": (-1, 0), "right": (1, 0), "up": (0, 1), "down": (0, -1)}[way]
    k = lambda fr: 1 - EASE((fr - start) * 18 / frames)  # noqa: E731
    shift = lambda fr: (sign[0] * d * k(fr), sign[1] * d * k(fr))  # noqa: E731
    edge = x0 if align == "left" else x1 if align == "right" else (x0 + x1) / 2
    clip = p.text(content, edge, caps[0], caps[1], x1 - x0, FONT, weight, colour, name, align=align, case="none",
                  shift=shift, reveal=lambda fr: (x0 - 6, y0 - 8, x1 + 6, y1 + 8))
    return clip


def letters(p, content, ink, weight, colour, name, start, align="left", backward=False, descenders=False,
            stagger=0.07):
    x0, y0, x1, y1 = ink
    caps = caps_of(y0, y1, descenders)
    edge = x0 if align == "left" else x1 if align == "right" else (x0 + x1) / 2
    clip = p.text(content, edge, caps[0], caps[1], x1 - x0, FONT, weight, colour, name, align=align, case="none")
    wait = round(start / FPS, 2)
    order, back = ("backward", "forward") if backward else ("forward", "backward")
    clip["textStyle"]["animation"] = {
        "in": tanim("pop", duration=0.3, unit="character", stagger=stagger, ease="easeOut", delay=wait, order=order,
                    **{"from": 0}),
        "out": tanim("pop", duration=0.3, unit="character", stagger=stagger, ease="easeIn", delay=wait, order=back,
                     **{"from": 0})}
    return clip


def box(p, name, rect, grows, start, frames=14, colour=WHITE):
    """A white box growing from frame `start`: ltr, rtl, ttb, btt, hline (a full-width line first, then its height
    from the middle), vline (an upright line first, then to the right), vline_rtl (an upright line on its right
    first, then to the left)."""
    x0, y0, x1, y1 = rect

    def r(fr):
        k = EASE((fr - start) * 18 / frames)
        if grows == "ltr":
            return (x0, y0, x0 + (x1 - x0) * k, y1)
        if grows == "rtl":
            return (x1 - (x1 - x0) * k, y0, x1, y1)
        if grows == "ttb":
            return (x0, y0, x1, y0 + (y1 - y0) * k)
        if grows == "btt":
            return (x0, y1 - (y1 - y0) * k, x1, y1)
        if grows == "hline":
            kh = EASE((fr - start) * 18 / frames * 2)
            kv = EASE((fr - start - frames / 2) * 18 / frames * 2)
            cy = (y0 + y1) / 2
            return (x0, cy - 3 - (cy - 3 - y0) * kv, x0 + (x1 - x0) * kh, cy + 3 + (y1 - cy - 3) * kv)
        kv = EASE((fr - start) * 18 / frames * 2)
        kh = EASE((fr - start - frames / 2) * 18 / frames * 2)
        cy = (y0 + y1) / 2
        if grows == "vline_rtl":
            return (x1 - 8 - (x1 - 8 - x0) * kh, cy - (cy - y0) * kv, x1, cy + (y1 - cy) * kv)
        return (x0, cy - (cy - y0) * kv, x0 + 8 + (x1 - x0 - 8) * kh, cy + (y1 - cy) * kv)
    return p.shape(name, colour, rect, r)


def piece(id, es, en, order, D, tags=()):
    t = _kit(id, es, en, D, order, list(tags), thumb_at=round(D / 2, 1))
    return t, BoxPiece(t, D)


def amanda():
    t, p = piece("amanda", "Tercio blanco: nombre y cargo en ficha", "White lower third: name, role on a tag", 8650, 4.3)
    slide(p, "AMANDA CARTER", (261, 644, 1222, 716), 800, WHITE, "Nombre", "left", 0)
    box(p, "Ficha", (237, 735, 1248, 798), "ltr", 2, frames=12)
    slide(p, "Digital Marketing Manager", (261, 749, 841, 790), 700, INK, "Cargo", "left", 6, descenders=True)
    slide(p, "eCommerce Marketing Specialist", (260, 814, 977, 854), 700, WHITE, "Cargo 2", "left", 17,
          descenders=True)
    return t


def elena():
    t, p = piece("elena", "Tercio blanco: nombre en caja", "White lower third: name in a box", 8651, 4.2)
    box(p, "Caja", (249, 688, 1233, 812), "hline", 0, frames=12)
    slide(p, "ELENA", (278, 713, 560, 786), 800, INK, "Nombre", "up", 8)
    slide(p, "MCCONTY", (590, 713, 1203, 786), 800, INK, "Apellido", "down", 13)
    slide(p, "CONTENT MARKETING MANAGER", (274, 834, 912, 863), 700, WHITE, "Cargo", "up", 17)
    return t


def hanna():
    t, p = piece("hanna", "Tercio blanco: apellido en caja", "White lower third: last name in a box", 8652, 5.0)
    box(p, "Caja", (264, 712, 861, 836), "vline", 1, frames=16)
    letters(p, "BARBERA", (300, 739, 828, 809), 800, INK, "Apellido", 12)
    letters(p, "HANNA", (300, 622, 698, 691), 800, WHITE, "Nombre", 24)
    slide(p, "MEDIA BUYER", (289, 855, 562, 883), 700, WHITE, "Cargo", "up", 26)
    return t


def erica():
    t, p = piece("erica", "Tercio blanco: dos fichas con el cargo", "White lower third: two tags with the role", 8653,
                 3.7)
    slide(p, "ERICA", (299, 611, 510, 657), 800, WHITE, "Nombre", "up", 0)
    slide(p, "CAVALLE", (299, 677, 788, 749), 800, WHITE, "Apellido", "up", 0)
    box(p, "Ficha", (274, 768, 814, 827), "ttb", 2, frames=10)
    box(p, "Ficha 2", (274, 836, 814, 895), "ttb", 5, frames=10)
    slide(p, "Fashion design", (299, 780, 616, 820), 700, INK, "Cargo", "up", 9, descenders=True)
    slide(p, "Brand Manager", (299, 847, 624, 884), 700, INK, "Cargo 2", "up", 14, descenders=True)
    return t


def emily():
    t, p = piece("emily", "Tercio blanco: nombre partido en caja y fuera", "White lower third: name half in a box",
                 8654, 4.8)
    box(p, "Caja", (569, 647, 944, 771), "vline", 0, frames=12)
    letters(p, "EMILY", (598, 674, 918, 744), 800, INK, "Nombre", 6)
    slide(p, "THOMAS", (960, 674, 1440, 744), 800, WHITE, "Apellido", "left", 12)
    box(p, "Línea", (944, 769, 1461, 772), "ltr", 14)
    slide(p, "Media Relations Coordinator", (694, 794, 1285, 824), 700, WHITE, "Cargo", "up", 24, align="center",
          descenders=True)
    slide(p, "Vice President of Marketing", (698, 846, 1278, 884), 700, WHITE, "Cargo 2", "up", 28, align="center",
          descenders=True)
    return t


def iren():
    t, p = piece("iren", "Tercio blanco: centrado con ficha", "White lower third: centred with a tag", 8655, 3.8,
                 ["centrado"])
    slide(p, "IREN KLAIRIE", (605, 695, 1315, 764), 800, WHITE, "Nombre", "up", 0, align="center")
    box(p, "Ficha", (579, 784, 1341, 843), "ltr", 2, frames=8)
    slide(p, "Marketing Director", (754, 793, 1166, 834), 700, INK, "Cargo", "up", 6, align="center", descenders=True)
    slide(p, "Marketing Manager", (748, 858, 1172, 898), 700, WHITE, "Cargo 2", "up", 15, align="center",
          descenders=True)
    return t


def kristina():
    t, p = piece("kristina", "Tercio blanco: caja con dos líneas de cargo", "White lower third: box with a two-line role",
                 8656, 5.2, ["centrado"])
    box(p, "Caja", (444, 748, 1476, 872), "vline", 1, frames=18)
    letters(p, "Program Administrator", (726, 769, 1209, 809), 700, INK, "Cargo", 16, stagger=0.04, align="center",
            descenders=True)
    letters(p, "Administrative Analyst", (721, 821, 1199, 860), 700, INK, "Cargo 2", 18, stagger=0.04,
            align="center", descenders=True)
    slide(p, "KRISTINA LAPTSO", (478, 650, 1442, 722), 800, WHITE, "Nombre", "up", 30, align="center")
    return t


def monica():
    t, p = piece("monica", "Tercio blanco: nombre en dos líneas y ficha", "White lower third: two-line name, tag",
                 8657, 4.7, ["centrado"])
    box(p, "Ficha", (600, 812, 1320, 871), "btt", 3, frames=10)
    slide(p, "Quality Control Coordinator", (672, 822, 1248, 861), 700, INK, "Cargo", "up", 8, align="center",
          descenders=True)
    slide(p, "GARCIA-SALMONES", (617, 745, 1303, 791), 800, WHITE, "Apellido", "up", 15, align="center")
    slide(p, "MONICA", (737, 652, 1182, 724), 800, WHITE, "Nombre", "up", 24, align="center")
    return t


def gabriela():
    t, p = piece("gabriela", "Tercio blanco: a la derecha con nombre largo", "White lower third: right, long name",
                 8658, 4.5, ["derecha"])
    slide(p, "RODRIGUEZ", (984, 683, 1619, 755), 800, WHITE, "Apellido", "right", 0, align="right")
    slide(p, "DE BUKELE", (1023, 777, 1622, 847), 800, WHITE, "Apellido 2", "right", 2, align="right")
    box(p, "Ficha", (1203, 582, 1618, 666), "vline_rtl", 0, frames=20)
    letters(p, "GABRIELA", (1234, 600, 1593, 648), 800, INK, "Nombre", 12, backward=True, align="right")
    box(p, "Línea", (950, 865, 1623, 868), "rtl", 14)
    slide(p, "Administrative Assistant", (1097, 885, 1621, 917), 700, WHITE, "Cargo", "right", 16, align="right",
          descenders=True)
    slide(p, "Bookkeeper", (1364, 936, 1620, 972), 700, WHITE, "Cargo 2", "right", 22, align="right",
          descenders=True)
    return t


def monika():
    t, p = piece("monika", "Tercio blanco: línea y cargo a la derecha", "White lower third: line, role on the right",
                 8659, 3.7, ["derecha"])
    slide(p, "MONIKA GOMES", (812, 659, 1673, 731), 800, WHITE, "Nombre", "down", 0, align="right")
    box(p, "Línea", (780, 749, 1668, 752), "rtl", 2)
    slide(p, "Administrative Manager", (1148, 764, 1673, 804), 700, WHITE, "Cargo", "up", 8, align="right",
          descenders=True)
    slide(p, "Chief Executive Officer", (1171, 817, 1673, 849), 700, WHITE, "Cargo 2", "up", 12, align="right")
    return t


def lora():
    t, p = piece("lora", "Tercio blanco: apellido en caja a la derecha", "White lower third: last name in a box, right",
                 8660, 4.4, ["derecha"])
    box(p, "Caja", (1175, 717, 1655, 841), "ttb", 0, frames=8)
    slide(p, "LUKASH", (1202, 742, 1630, 815), 800, INK, "Apellido", "up", 3)
    letters(p, "LORA", (1344, 625, 1639, 697), 800, WHITE, "Nombre", 10, backward=True, align="right")
    slide(p, "Business Manager", (1237, 857, 1630, 897), 700, WHITE, "Cargo", "right", 12, align="center",
          descenders=True)
    slide(p, "Business Analyst", (1262, 908, 1629, 948), 700, WHITE, "Cargo 2", "right", 18, align="center",
          descenders=True)
    return t


def elizabeth():
    t, p = piece("elizabeth", "Tercio blanco: nombre y ficha a la derecha", "White lower third: name and tag, right",
                 8661, 4.6, ["derecha"])
    slide(p, "ELIZABETH LEE", (805, 689, 1626, 758), 800, WHITE, "Nombre", "right", 0, align="right")
    box(p, "Ficha", (782, 779, 1649, 839), "rtl", 10, frames=14)
    slide(p, "Assistant Manager", (1216, 788, 1622, 828), 700, INK, "Cargo", "right", 18, align="right",
          descenders=True)
    return t


TEMPLATES = [amanda, elena, hanna, erica, emily, iren, kristina, monica, gabriela, monika, lora, elizabeth]
