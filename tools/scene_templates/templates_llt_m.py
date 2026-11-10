"""White italic lower thirds, thirteenth set (2026-11-07): the twelve of 57613079.mp4 (2160×1214 at 30 fps, here
measured on the catalogue grid scaled to 1920×1080), Barlow italic (Bold names, Regular first names and roles,
Bold capitals for small roles) in white with underlines and slanted bars. Moves: every line types in letter by
letter, each letter fading in from a little to its right (names), above (first names) or below (roles); lines
aligned right build from their end; underlines grow from the left and bars from the top. Each piece leaves with its
entrance backwards. The reference also shows them big beside a photo; only the type is the lower third. Grid ×1.2
(0.62 of the big version), laid out bottom-left (left 120, bottom 960), with no background. Order 8710-8721.
Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import wide
from scene import tanim
from templates_llt_f import Piece, table

# Every line is italic: measure with the italic files.
f6._FILES[("Barlow", 400)] = "fonts.extra/fonts/barlow/Barlow-Italic.ttf"
f6._FILES[("Barlow", 700)] = "fonts.extra/fonts/barlow/Barlow-BoldItalic.ttf"
FONT = "Barlow"
WHITE = "#FFFFFF"
FPS = 30.0
S = 1.2
EASE = table({0: 0.0, 2: 0.2, 4: 0.45, 6: 0.65, 8: 0.79, 10: 0.88, 12: 0.94, 14: 0.975, 16: 0.99, 18: 1.0})
D = 4.4


class GridPiece(Piece):
    """Laid out in grid px: `bbox` lands with its left at 120 and bottom at 960."""

    def __init__(self, t, dur, bbox):
        super().__init__(t, dur, 0)
        self.bx0, self.by1 = bbox[0], bbox[3]

    def frame(self, u):
        return min(u, self.dur - u) * FPS

    def R(self, r):
        return (120 + (r[0] - self.bx0) * S, 960 - (self.by1 - r[1]) * S, 120 + (r[2] - self.bx0) * S,
                960 - (self.by1 - r[3]) * S)


def piece(id, es, en, order, bbox, tags=()):
    t = wide(f"llt13-{id}", es, en, "ytkit", D, order=order,
             tags=["kit:lowerthirds", "tercio", "blanco", "cursiva"] + list(tags), thumb_at=round(D / 2, 1))
    return t, GridPiece(t, D, bbox)


# How each kind of line comes in: preset, from where.
COMES = {"name": ("slide-left", 0.5), "first": ("slide-down", 0.45), "role": ("slide-up", 0.5)}


def line(p, content, ink, weight, name, kind, start, align="left", desc=False, stagger=0.07):
    """A line of ink `ink` (grid px; with desc its bottom is the descenders') typing in from frame `start`."""
    x0, y0, x1, y1 = p.R(ink)
    if desc:
        y1 = y0 + (y1 - y0) * 0.78
    edge = x0 if align == "left" else x1
    clip = p.text(content, edge, y0, y1, x1 - x0, FONT, weight, WHITE, name, align=align, case="none")
    clip["textStyle"]["italic"] = True
    preset, dist = COMES[kind]
    if preset == "slide-left":
        # The distance is in the line's box: about one letter.
        dist = round(1.0 / max(4, len(content)), 3)
    wait = round(start / FPS, 2)
    order, back = ("backward", "forward") if align == "right" else ("forward", "backward")
    clip["textStyle"]["animation"] = {
        "in": tanim(preset, duration=0.2, unit="character", stagger=stagger, ease="easeOut", delay=wait, order=order,
                    distance=dist),
        "out": tanim(preset, duration=0.2, unit="character", stagger=stagger, ease="easeIn", delay=wait, order=back,
                     distance=dist)}
    return clip


def rule(p, name, rect, start, frames=12, kind="ltr", skew=0.0):
    """An underline growing from its left (ltr) or a bar growing from its top (ttb), from frame `start`; a slanted
    bar's rect holds its whole slant (thickness + height × tan skew)."""
    x0, y0, x1, y1 = p.R(rect)

    def r(fr):
        k = EASE((fr - start) * 18 / frames)
        if kind == "ttb":
            return (x0, y0, x1, y0 + (y1 - y0) * k)
        if kind == "rtl":
            return (x1 - (x1 - x0) * k, y0, x1, y1)
        return (x0, y0, x0 + (x1 - x0) * k, y1)
    return p.shape(name, WHITE, (x0, y0, x1, y1), r, skew=skew)


def emily():
    t, p = piece("emily", "Tercio en cursiva: nombre en dos líneas y subrayado", "Italic lower third: two-line name, underline",
                 8710, (194, 222, 370, 350))
    line(p, "Emily", (210, 226, 298, 259), 400, "Nombre", "first", 0, desc=True)
    line(p, "Smith", (205, 261, 365, 306), 700, "Apellido", "name", 0)
    rule(p, "Subrayado", (196, 316, 361, 323), 14)
    line(p, "Engineer", (199, 330, 290, 350), 400, "Cargo", "role", 6, desc=True)
    return t


def michael():
    t, p = piece("michael", "Tercio en cursiva: nombre subrayado", "Italic lower third: underlined name", 8711,
                 (481, 259, 878, 330))
    line(p, "Michael Johnson", (484, 259, 876, 297), 700, "Nombre", "name", 0, stagger=0.05)
    rule(p, "Subrayado", (482, 304, 875, 311), 14, frames=14)
    line(p, "DOCTOR", (488, 320, 537, 330), 700, "Cargo", "role", 6)
    return t


def sophia():
    t, p = piece("sophia", "Tercio en cursiva: barra y cargo al lado", "Italic lower third: bar, role beside", 8712,
                 (998, 222, 1267, 317), ["barra"])
    line(p, "Sophia", (1042, 222, 1180, 262), 400, "Nombre", "first", 0, desc=True)
    line(p, "Davis", (1000, 266, 1172, 316), 700, "Apellido", "name", 0)
    rule(p, "Barra", (1180, 223, 1202, 316), 6, frames=12, kind="ttb", skew=9.5)
    line(p, "CONTENT", (1194, 286, 1267, 297), 700, "Cargo", "role", 8)
    line(p, "WRITER", (1194, 304, 1251, 315), 700, "Cargo 2", "role", 10)
    return t


def david():
    t, p = piece("david", "Tercio en cursiva: cargo, barra y nombre", "Italic lower third: role, bar and name", 8713,
                 (1401, 220, 1727, 314), ["barra"])
    rule(p, "Barra", (1494, 220, 1513, 314), 6, frames=12, kind="ttb", skew=7.3)
    line(p, "David", (1514, 222, 1625, 252), 400, "Nombre", "first", 0)
    line(p, "Wilson", (1512, 267, 1727, 314), 700, "Apellido", "name", 0)
    line(p, "Teacher", (1401, 298, 1484, 314), 400, "Cargo", "role", 6, align="right")
    return t


def clark():
    t, p = piece("clark", "Tercio en cursiva: apellido grueso y nombre fino", "Italic lower third: bold last, light first",
                 8714, (180, 494, 487, 565))
    line(p, "Clark", (185, 494, 336, 538), 700, "Apellido", "name", 0)
    line(p, "Emily", (341, 494, 487, 550), 400, "Nombre", "name", 5, desc=True)
    rule(p, "Subrayado", (188, 541, 331, 547), 14)
    line(p, "DESIGNER", (186, 556, 249, 565), 700, "Cargo", "role", 8)
    return t


def olivia():
    t, p = piece("olivia", "Tercio en cursiva: cargo a la izquierda y subrayado", "Italic lower third: role left, underline",
                 8715, (603, 488, 874, 556))
    line(p, "Olivia", (697, 488, 872, 543), 700, "Nombre", "name", 0)
    line(p, "HUMAN", (644, 514, 689, 525), 700, "Cargo", "role", 6, align="right")
    line(p, "RESOURCES", (611, 532, 689, 543), 700, "Cargo 2", "role", 8, align="right")
    rule(p, "Subrayado", (603, 549, 874, 556), 14)
    return t


def dominic():
    t, p = piece("dominic", "Tercio en cursiva: apellido grande subrayado", "Italic lower third: big underlined last name",
                 8716, (997, 456, 1296, 575))
    line(p, "Dominic", (1015, 456, 1145, 482), 400, "Nombre", "first", 0)
    line(p, "Fairchild", (1007, 489, 1290, 544), 700, "Apellido", "name", 0)
    rule(p, "Subrayado", (999, 552, 1290, 559), 14)
    line(p, "FINANCIAL ADVISOR", (1003, 567, 1108, 575), 700, "Cargo", "role", 8, stagger=0.04)
    return t


def nathaniel():
    t, p = piece("nathaniel", "Tercio en cursiva a la derecha", "Italic lower third, aligned right", 8717,
                 (1407, 472, 1730, 591), ["derecha"])
    line(p, "Nathaniel", (1414, 472, 1729, 525), 700, "Nombre", "name", 0, align="right")
    rule(p, "Subrayado", (1407, 530, 1730, 537), 14, kind="rtl")
    line(p, "Bennett", (1592, 546, 1719, 572), 400, "Apellido", "role", 4, align="right")
    line(p, "MARKETING SPECIALIST", (1570, 582, 1719, 591), 700, "Cargo", "role", 8, align="right", stagger=0.04)
    return t


def maximilian():
    t, p = piece("maximilian", "Tercio en cursiva: nombre subrayado y apellido", "Italic lower third: underlined name, last",
                 8718, (191, 718, 551, 838))
    line(p, "Maximilian", (205, 718, 551, 773), 700, "Nombre", "name", 0)
    rule(p, "Subrayado", (198, 779, 547, 786), 14)
    line(p, "Price", (200, 794, 282, 820), 400, "Apellido", "role", 6)
    line(p, "FINANCIAL ADVISOR", (197, 829, 323, 838), 700, "Cargo", "role", 10, stagger=0.04)
    return t


def james():
    t, p = piece("james", "Tercio en cursiva: barra y cargo abajo", "Italic lower third: bar, role below right", 8719,
                 (683, 736, 962, 838), ["barra"])
    line(p, "James", (730, 736, 863, 772), 400, "Nombre", "first", 0)
    line(p, "Miller", (683, 783, 858, 836), 700, "Apellido", "name", 0)
    rule(p, "Barra", (866, 736, 884, 836), 6, frames=12, kind="ttb", skew=6.3)
    line(p, "Lawyer", (877, 817, 962, 838), 400, "Cargo", "role", 8, desc=True)
    return t


def foster():
    t, p = piece("foster", "Tercio en cursiva: cargo arriba y línea", "Italic lower third: role above, line", 8720,
                 (1086, 714, 1315, 837))
    line(p, "PRODUCT MANAGER", (1106, 714, 1255, 726), 700, "Cargo", "first", 0, stagger=0.04)
    rule(p, "Línea", (1104, 734, 1314, 741), 6)
    line(p, "Foster", (1097, 750, 1307, 803), 700, "Apellido", "name", 4)
    line(p, "Ethan", (1092, 811, 1185, 837), 400, "Nombre", "role", 8)
    return t


def kingsley():
    t, p = piece("kingsley", "Tercio en cursiva: nombre y barra a la derecha", "Italic lower third: name, bar on the right",
                 8721, (1431, 722, 1726, 836), ["barra", "derecha"])
    line(p, "Anastasia", (1599, 722, 1713, 743), 400, "Nombre", "first", 0, align="right")
    line(p, "Kingsley", (1431, 748, 1706, 820), 700, "Apellido", "name", 0, align="right", desc=True)
    rule(p, "Barra", (1708, 722, 1733, 836), 6, frames=12, kind="ttb", skew=8.5)
    line(p, "UX Researcher", (1596, 821, 1698, 836), 400, "Cargo", "role", 8, align="right")
    return t


TEMPLATES = [emily, michael, sophia, david, clark, olivia, dominic, nathaniel, maximilian, james, foster, kingsley]
