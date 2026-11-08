"""Minimal black and white lower thirds, fifteenth set (2026-11-07): the seven of 11806797.mp4 (3840×2160 at 29.97 fps,
measured on its catalogue frame scaled to 1920×1080), Inter (Bold names, Medium roles): a white name tag with black
type and black boxes with white type, small rounded corners, and a logo square or block (a logo slot, the Flip play
symbol as the sample, instead of the stock-site wordmark). Moves: the name types in letter by letter while its tag
grows with it, the role box drops from behind the tag, the logo pops in and black bars grow from behind it; each
piece leaves with its entrance backwards. ×1.25 (the reference is a 4K design: at 1080 its type is small), laid out
bottom-left (left 120, bottom 960), with no background. Order 8750-8756. Not published until Jorge says the group
is complete.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import label, wide
from llt_motion import frames_of
from scene import Box, tanim
from templates_llt_f import Piece, table

f6._FILES[("Inter", 500)] = "fonts.basic/fonts/inter/Inter-Medium.ttf"
f6._FILES[("Inter", 600)] = "fonts.basic/fonts/inter/Inter-SemiBold.ttf"
f6._FILES[("Inter", 700)] = "fonts.basic/fonts/inter/Inter-Bold.ttf"
FONT = "Inter"
WHITE = "#FFFFFF"
INK = "#000000"
FPS = 29.97
S = 1.25
D = 4.5
RADIUS = 6
STAGGER = 0.02
EASE = table({0: 0.0, 2: 0.2, 4: 0.45, 6: 0.65, 8: 0.79, 10: 0.88, 12: 0.94, 14: 0.975, 16: 0.99, 18: 1.0})
POP = table({0: 0.0, 3: 0.6, 6: 1.06, 8: 1.02, 10: 1.0})
NAME = "Prof. Henry Wallace"
ABOUT = ("Use this space for a short description: who they are, what they do, where they come from and why they "
         "are on screen today, told in a few clean and simple lines.")


def E(fr, start, frames):
    return EASE((fr - start) * 18 / frames)


class TagPiece(Piece):
    """Laid out in catalogue px: `bbox` lands with its left at 120 and bottom at 960."""

    def __init__(self, t, dur, bbox):
        super().__init__(t, dur, 0)
        self.bx0, self.by1 = bbox[0], bbox[3]

    def frame(self, u):
        return min(u, self.dur - u) * FPS

    def X(self, x):
        return 120 + (x - self.bx0) * S

    def R(self, r):
        return (self.X(r[0]), 960 - (self.by1 - r[1]) * S, self.X(r[2]), 960 - (self.by1 - r[3]) * S)


def piece(id, es, en, order, bbox, tags=()):
    t = wide(f"llt15-{id}", es, en, "ytkit", D, order=order,
             tags=["kit:lowerthirds", "tercio", "minimalista", "negro"] + list(tags), thumb_at=round(D / 2, 1))
    return t, TagPiece(t, D, bbox)


def box(p, name, colour, full, fn):
    clip = p.shape(name, colour, p.R(full), fn)
    clip["shapeStyle"]["cornerRadius"] = RADIUS * S
    return clip


def typing_end(p, content, ink, weight, start, align="left"):
    """fr -> the screen x where the typed part of `content` (ink `ink`, catalogue px) ends (its left, align right)."""
    x0, _, x1, _ = p.R(ink)
    size, _ = f6.fit(content, x1 - x0, FONT, weight)
    font = f6._font(FONT, weight)
    full = x1 - x0

    def done(fr):
        if fr < start:
            return 0.0
        n = min(len(content), int((fr - start) / FPS / STAGGER) + 1)
        return min(full, font.getlength(content[:n]) * size / 400)
    return (lambda fr: x0 + done(fr)) if align == "left" else (lambda fr: x1 - done(fr))


def typed(p, content, ink, weight, colour, name, start, align="left", desc=False, reveal=None, shift=None):
    """A line of ink `ink` (catalogue px) typing in from frame `start`."""
    x0, y0, x1, y1 = p.R(ink)
    if desc:
        y1 = y0 + (y1 - y0) * 0.78
    edge = x0 if align == "left" else x1
    clip = p.text(content, edge, y0, y1, x1 - x0, FONT, weight, colour, name, align=align, case="none",
                  reveal=reveal, shift=shift)
    wait = round(start / FPS, 2)
    clip["textStyle"]["animation"] = {
        "in": tanim("typewriter", unit="character", stagger=STAGGER, delay=wait, caret=False, lead=0.0, hold=0.0),
        "out": tanim("typewriter", unit="character", stagger=STAGGER, delay=wait, caret=False, lead=0.0, hold=0.0,
                     order="backward")}
    return clip


def tag_for(p, rect, end, start, minw=34):
    """fr -> the white tag `rect` whose right edge follows the typed text (`end` + the tag's right padding)."""
    x0, y0, x1, y1 = p.R(rect)
    pad = 25 * S

    def r(fr):
        if fr < start:
            return (x0, y0, x0, y1)
        k = POP(fr - start)
        right = max(x0 + minw * S, end(fr) + pad)
        cy, hh = (y0 + y1) / 2, (y1 - y0) / 2 * min(1.0, k)
        return (x0, cy - hh, min(x1, right), cy + hh)
    return r


def drop(p, rect, top_from, start, frames=8):
    """fr -> `rect` sliding down from behind the tag (its top from `top_from`)."""
    x0, y0, x1, y1 = p.R(rect)
    t0 = 960 - (p.by1 - top_from) * S

    def r(fr):
        k = E(fr, start, frames)
        dy = (y0 - t0) * (1 - k)
        return (x0, y0 - dy, x1, y1 - dy)
    return r


def logo(p, rect, start, inset=0.22):
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    m = min(w, h) * inset
    side = min(w, h) - 2 * m
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sx0, sy0, sx1, sy1 = p.R((cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2))
    bx = Box(sx0, sy0, sx1 - sx0, sy1 - sy0)
    motion = [(u, {"s": max(1e-4, POP(p.frame(u) - start - 2))}, "linear") for u in frames_of(p.dur)]
    p.t.photo(p.t.track("video", "Logo"), "logo-flip", 0.0, p.dur, bx, motion, label="Tu logo", brandRole="logo")


def pop(p, rect, start):
    x0, y0, x1, y1 = p.R(rect)

    def r(fr):
        k = POP(fr - start)
        cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 * k, (y1 - y0) / 2 * k
        return (cx - hw, cy - hh, cx + hw, cy + hh)
    return r


def name_tag(p, top, right, start=0):
    """The white name tag (catalogue rect left 96, from `top`, 77 tall, up to `right`) typing the name."""
    rect = (96, top, right, top + 77)
    ink = (120, top + 25, 482 + (right - 507), top + 53)
    end = typing_end(p, NAME, ink, 700, start + 2)
    box(p, "Ficha", WHITE, rect, tag_for(p, rect, end, start))
    typed(p, NAME, ink, 700, INK, "Nombre", start + 2)
    return rect


def role_box(p, rect, under_top, start):
    fn = drop(p, rect, under_top, start)
    box(p, "Caja", INK, rect, fn)
    return fn


def moving(fn, rect, p, tag_bottom):
    """A text reveal and shift that ride with a dropping box `fn` laid out at `rect`: shown only below the name
    tag's bottom (`tag_bottom`, catalogue px), so it slides out from behind the tag."""
    y_rest = p.R(rect)[1]
    yb = 960 - (p.by1 - tag_bottom) * S
    x0, _, x1, y1 = p.R(rect)
    return (lambda fr: (x0 - 20, yb, x1 + 20, y1 + 400)), (lambda fr: (0.0, fn(fr)[1] - y_rest))


# --- The seven ----------------------------------------------------------------------------------------------------


def name_only():
    t, p = piece("nombre", "Tercio minimalista: nombre en ficha blanca", "Minimal lower third: name on a white tag",
                 8750, (96, 96, 507, 173))
    name_tag(p, 96, 507)
    return t


def name_role():
    t, p = piece("nombre-cargo", "Tercio minimalista: nombre y cargo", "Minimal lower third: name and role", 8751,
                 (96, 219, 507, 360))
    rect = (98, 292, 507, 360)
    fn = role_box(p, rect, 230, 16)
    name_tag(p, 219, 507)
    rev, sh = moving(fn, rect, p, 296)
    typed(p, "Senior Broadcast Producer", (121, 320, 404, 337), 600, WHITE, "Cargo", 18, reveal=rev, shift=sh)
    return t


def two_lines():
    t, p = piece("dos-lineas", "Tercio minimalista: nombre y cargo en dos líneas", "Minimal lower third: two-line role",
                 8752, (96, 407, 507, 576))
    rect = (98, 480, 507, 576)
    fn = role_box(p, rect, 420, 16)
    name_tag(p, 407, 506)
    rev, sh = moving(fn, rect, p, 484)
    typed(p, "Senior Broadcast Producer", (121, 509, 413, 525), 600, WHITE, "Cargo", 18, reveal=rev, shift=sh)
    typed(p, "Live Studio Operations", (121, 536, 364, 558), 600, WHITE, "Cargo 2", 22, desc=True, reveal=rev,
          shift=sh)
    return t


def about():
    t, p = piece("descripcion", "Tercio minimalista: nombre y descripción", "Minimal lower third: name and description",
                 8753, (96, 623, 516, 844))
    rect = (98, 696, 516, 844)
    role_box(p, rect, 640, 16)
    name_tag(p, 623, 516)
    x0, y0, x1, y1 = p.R((120, 718, 494, 840))
    clip = label(t, t.track("text", "Texto"), ABOUT, 0.0, D, Box(x0, y0, x1 - x0, y1 - y0), FONT, round(19.5 * S, 1),
                 WHITE, weight=500, align="left", valign="top", line=1.3, name="Texto")
    # It types in word by word once its box has dropped.
    wait = round(24 / FPS, 2)
    clip["textStyle"]["animation"] = {
        "in": tanim("typewriter", unit="word", stagger=0.02, delay=wait, caret=False, lead=0.0, hold=0.0),
        "out": tanim("typewriter", unit="word", stagger=0.02, delay=wait, caret=False, lead=0.0, hold=0.0,
                     order="backward")}
    return t


def logo_name():
    t, p = piece("logo-nombre", "Tercio minimalista: bloque del logo y nombre", "Minimal lower third: logo block, name",
                 8754, (961, 96, 1592, 173), ["logo"])
    rect = (1177, 96, 1592, 173)
    end = typing_end(p, NAME, (1205, 121, 1567, 149), 700, 8)
    box(p, "Ficha", WHITE, rect, tag_for(p, rect, end, 6))
    typed(p, NAME, (1205, 121, 1567, 149), 700, INK, "Nombre", 8)
    block = (961, 96, 1182, 173)
    box(p, "Bloque del logo", INK, block, pop(p, block, 0))
    logo(p, block, 0, inset=0.18)
    return t


def logo_card():
    t, p = piece("logo-ficha", "Tercio minimalista: cuadro del logo y dos líneas", "Minimal lower third: logo square, two lines",
                 8755, (960, 219, 1372, 312), ["logo"])
    rect = (1054, 220, 1372, 312)
    grow = lambda fr: (p.R(rect)[0], p.R(rect)[1], p.R(rect)[0] + (p.R(rect)[2] - p.R(rect)[0]) * E(fr, 6, 12),  # noqa: E731
                       p.R(rect)[3])
    box(p, "Caja", INK, rect, grow)
    typed(p, NAME, (1096, 243, 1305, 265), 500, WHITE, "Nombre", 8, desc=True)
    typed(p, "Live Studio Operations", (1096, 271, 1340, 293), 600, WHITE, "Cargo", 14, desc=True)
    square = (960, 219, 1064, 312)
    box(p, "Cuadro del logo", WHITE, square, pop(p, square, 0))
    logo(p, square, 0)
    return t


def long_bar():
    # The bar runs nearly the width of the frame: at ×1.25 it would not fit, so this one is ×0.97 (right edge 1800).
    global S
    keep, S = S, 0.97
    try:
        return _long_bar()
    finally:
        S = keep


def _long_bar():
    t, p = piece("barra-larga", "Tercio minimalista: barra larga con logo y fecha", "Minimal lower third: long bar, logo, date",
                 8756, (96, 891, 1824, 984), ["logo", "barra"])
    rect = (192, 892, 1824, 983)
    r = p.R(rect)
    box(p, "Barra", INK, rect, lambda fr: (r[0], r[1], r[0] + (r[2] - r[0]) * E(fr, 4, 18), r[3]))
    typed(p, NAME, (232, 916, 441, 938), 500, WHITE, "Nombre", 8, desc=True)
    typed(p, "Live Studio Operations", (232, 944, 476, 966), 600, WHITE, "Cargo", 16, desc=True)
    typed(p, "Monday", (1706, 915, 1791, 936), 500, WHITE, "Día", 16, align="right", desc=True)
    typed(p, "Live Update", (1665, 943, 1791, 964), 500, WHITE, "Estado", 20, align="right", desc=True)
    square = (96, 891, 200, 984)
    box(p, "Cuadro del logo", WHITE, square, pop(p, square, 0))
    logo(p, square, 0)
    return t


TEMPLATES = [name_only, name_role, two_lines, about, logo_name, logo_card, long_bar]
