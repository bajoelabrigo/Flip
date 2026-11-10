"""Blue bar lower thirds, seventh set (2026-11-07): the two of 3569039.mp4 (960×540 at 29.97 fps, measured scaled
to 1080p): a slanted logo block (a logo slot, the Flip play symbol as the sample) slides in from the left, a light
panel comes in from the right and the blue bar grows over it, and the line(s) slide out from behind the logo
block. Josefin Sans. Laid out where the reference has them, with no background; each leaves with its entrance
played backwards. Order 8610-8611. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from templates_llt_f import Piece, table

f6._FILES[("Josefin Sans", 400)] = "fonts.extra/fonts/josefinsans/JosefinSans-Regular.ttf"
f6._FILES[("Josefin Sans", 600)] = "fonts.extra/fonts/josefinsans/JosefinSans-SemiBold.ttf"
FONT = "Josefin Sans"
FPS = 29.97
LOGO_BLUE = "#2160C8"
BAR_BLUE = "#1048A0"
PANEL = "#DCDCDE"
LINE = "#D2D2D2"
BAND = "#2F3130"
WHITE = "#FFFFFF"
TOP, LOGO_BOT = 834, 1006
SLANT_TOP, SLANT_BOT = 530, 458  # the logo block's right edge at its top and bottom
LEAN = (SLANT_TOP - SLANT_BOT) / (LOGO_BOT - TOP)
SKEW = math.degrees(math.atan(LEAN))
RIGHT = 1818


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt7-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "logo"] + tags,
                **kw)


# The logo block's slide (its left edge from 120), the bar's right edge and the panel's left edge, frames from the
# piece's first frame; the line's slide (its right end from rest).
SLIDE = table({0: -420, 3: -390, 6: -230, 9: -54, 10: -4, 11: 36, 12: 50, 13: 52, 14: 50, 15: 40, 16: 32, 17: 24,
               18: 16, 19: 12, 20: 10, 21: 4, 22: 4, 24: 0})
BAR = table({14: 520, 15: 630, 16: 730, 17: 830, 18: 930, 19: 1030, 20: 1130, 21: 1226, 22: 1320, 23: 1410,
             24: 1500, 25: 1590, 26: 1680, 27: 1770, 28: 1818})
PANEL_L = table({7: 1410, 8: 1320, 9: 1220, 10: 1100, 11: 1010, 12: 920, 13: 830, 14: 740, 15: 670})
TEXT = table({20: -900, 21: -806, 22: -706, 24: -530, 25: -446, 26: -366, 27: -296, 28: -226, 29: -150, 30: -116,
              31: -72, 32: -32, 33: -10, 34: -2, 35: 0})


class BluePiece(Piece):
    def __init__(self, t, dur):
        super().__init__(t, dur, 0)

    def frame(self, u):
        return min(u, self.dur - u) * FPS


def _build(t, D, bar_bottom, band=None):
    p = BluePiece(t, D)
    dx = lambda fr: SLIDE(fr)  # noqa: E731

    def bar(fr):
        if fr < 14:
            return (SLANT_TOP + dx(fr) - 2, TOP, SLANT_TOP + dx(fr) - 1, bar_bottom)
        return (SLANT_BOT - (bar_bottom - TOP) * 0 + dx(fr) - 80, TOP, BAR(fr) + dx(fr), bar_bottom)
    # The light panel the bar pushes, then the bar, the line under it and the dark band (two-line version).
    p.shape("Panel", PANEL, (670, TOP, RIGHT, bar_bottom),
            lambda fr: (PANEL_L(fr) if fr < 15 else BAR(fr), TOP, RIGHT, bar_bottom) if 7 <= fr < 28
            else (RIGHT, TOP, RIGHT, bar_bottom))
    p.shape("Barra", BAR_BLUE, (SLANT_BOT - 80, TOP, RIGHT, bar_bottom), bar)
    if band:
        p.shape("Franja", BAND, (SLANT_BOT - 60, band[0], RIGHT, band[1]),
                lambda fr: (SLANT_BOT - 60 + dx(fr), band[0], max(SLANT_BOT - 60.0, BAR(fr)) + dx(fr), band[1])
                if fr >= 14 else (SLANT_BOT, band[0], SLANT_BOT, band[1]))
    line_y = (band[1] if band else bar_bottom) + 2
    p.shape("Línea", LINE, (SLANT_BOT, line_y, RIGHT, line_y + 5),
            lambda fr: (SLANT_BOT + dx(fr), line_y, max(SLANT_BOT + 0.0, BAR(fr)) + dx(fr), line_y + 5)
            if fr >= 14 else (SLANT_BOT, line_y, SLANT_BOT, line_y + 5))
    return p, dx


def _logo_block(t, p, dx, D):
    """The slanted logo block and the logo slot in it (drawn over the bar and the lines)."""
    # A straight left side: a rectangle, and a parallelogram for the slanted right side whose own left side hides
    # under the rectangle.
    p.shape("Bloque del logo", LOGO_BLUE, (120, TOP, SLANT_BOT, LOGO_BOT),
            lambda fr: (120 + dx(fr), TOP, SLANT_BOT + dx(fr), LOGO_BOT))
    p.shape("Bloque del logo (bisel)", LOGO_BLUE, (300, TOP, SLANT_TOP, LOGO_BOT),
            lambda fr: (300 + dx(fr), TOP, SLANT_TOP + dx(fr), LOGO_BOT), skew=SKEW)
    logo = Box(255, 870, 100, 100)
    motion = [(u, {"dx": dx(p.frame(u))}, "linear") for u in frames_of(D)]
    t.photo(t.track("video", "Logo"), "logo-flip", 0.0, D, logo, motion, label="Tu logo", brandRole="logo")


def _behind_block(dx, y0, y1):
    """Text shows only right of the logo block's slanted edge (taken at the line's middle) and inside the bar."""
    mid = (y0 + y1) / 2
    edge = SLANT_TOP - (mid - TOP) * LEAN
    return lambda fr: (edge + dx(fr), y0, RIGHT + dx(fr), y1)


def one_line():
    """1: one line on the blue bar."""
    D = 9.6
    t = _kit("barra-azul", "Tercio: barra azul con logo y una línea", "Lower third: blue bar with logo, one line", D,
             8610, ["azul", "logo"], thumb_at=4.0)
    p, dx = _build(t, D, 995)
    p.text("1 line lower third", 696, 911, 955, 670, FONT, 400, WHITE, "Título", spacing_em=0.03,
           shift=lambda fr: TEXT(fr) + dx(fr), reveal=_behind_block(dx, 840, 995))
    _logo_block(t, p, dx, D)
    return t


def two_lines():
    """2: two lines, the second on a dark band under the blue bar."""
    D = 9.6
    t = _kit("barra-azul-2", "Tercio: barra azul con logo y dos líneas", "Lower third: blue bar with logo, two lines",
             D, 8611, ["azul", "logo"], thumb_at=4.0)
    p, dx = _build(t, D, 964, band=(966, 1007))
    p.text("2 lines lower third", 612, 893, 925, 506, FONT, 400, WHITE, "Título", spacing_em=0.03,
           shift=lambda fr: TEXT(fr) + dx(fr), reveal=_behind_block(dx, 840, 964))
    p.text("More information can be added here", 612, 976, 999, 620, FONT, 400, WHITE, "Subtítulo",
           spacing_em=0.02, shift=lambda fr: TEXT(fr - 2) + dx(fr), reveal=_behind_block(dx, 966, 1007))
    _logo_block(t, p, dx, D)
    return t


TEMPLATES = [one_line, two_lines]
