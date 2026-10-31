"""Logo lower thirds (2026-10-31), copied frame by frame from the second reference Jorge sent (15488414.mp4, 24 lower
thirds with a logo: «lo más parecido posible, casi iguales»). Every bar and edge plays its measured curve
(lt_ref/<name>.json, 25 fps scaled to 1080p); texts sit where the reference has them; the logo is a slot («Tu
logo»), shown with the app's premium flame as the sample (logo-09…14, Jorge: «el logo es el del fuego»). Order 8530-8569.
"""

from __future__ import annotations

from kit import Box, centered, photo_bg, wide
from llt_motion import RED, WHITE, caps_box, duration, edge, mask_track, name_text, rect_track
from lt_motion import Ref


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "logo"] + tags, **kw)


def _logo_square(t, r, sq: Box, dur, logo="logo-10", logo_share=0.74, colour=RED, white=WHITE):
    """The square logo of «francois»: a white corner (an L) thickens into a white square; the coloured square with the
    logo shows from the top and left while the white shrinks into the bottom-right corner. Bands: lgv (the square's
    right column, rows), lgh (its bottom rows, columns)."""
    x1, y1 = sq.x + sq.w, sq.y + sq.h
    yw = edge(r, "lgv", "warm", "max", before=sq.y, after=sq.y)          # the colour's bottom on the right column
    xw = edge(r, "lgh", "warm", "max", before=sq.x, after=sq.x)          # the colour's right end on the bottom rows
    wt = edge(r, "lgv", "white", "min", before=y1, after=y1)             # the white's top on the right column
    thick = lambda u: y1 - wt(u)  # noqa: E731  the L's stroke
    hole = lambda u: (xw(u), yw(u), x1, y1)  # noqa: E731  what the colour does not cover yet
    base = t.solid(t.track("shape", "Cuadro"), colour, 0.0, dur, sq)
    base["name"] = "Cuadro"
    mask_track(t, base, sq, hole, dur, invert=True)
    side = sq.w * logo_share
    mark = t.photo(t.track("video", "Logo"), logo, 0.0, dur, centered(sq.cx, sq.cy, side, side), label="Tu logo")
    mask_track(t, mark, centered(sq.cx, sq.cy, side, side), hole, dur, invert=True)
    rect_track(t, t.track("shape", "Esquina"), sq, lambda u: (xw(u), yw(u), xw(u) + thick(u), y1), dur, white,
               name="Esquina")
    rect_track(t, t.track("shape", "Esquina 2"), sq, lambda u: (xw(u), y1 - thick(u), x1, y1), dur, white,
               name="Esquina 2")


def francois():
    """A red line under the name's top grows into a block that slides down to become the role's bar, uncovering the
    name above it; the role shows inside the bar. The logo: a white corner fills a square, then the red square with
    the logo takes its place from the top left. The exit is the measured one (the bar climbs back over the name)."""
    r = Ref("francois")
    D = duration(r)
    t = _kit("francois", "Tercio con logo: nombre y barra roja", "Logo lower third: name over a red bar", D, 8530,
             ["nombre", "barra", "rojo"], thumb_at=2.5)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    _logo_square(t, r, Box(306, 700, 147, 148), D)
    bar = Box(463, 700, 881, 248)
    top = edge(r, "bar", "warm", "min", before=700, after=700)
    bottom = edge(r, "bar", "warm", "max", before=700, after=700)
    name = "FRANCOIS BERG"
    nbox, nsize = caps_box(477, 707, 841, name)
    clip = name_text(t, name, nbox, nsize, D, bold_from="BERG", spacing=-5.4, bold_spacing=7, word_spacing=9)
    mask_track(t, clip, nbox, lambda u: (nbox.x, 600, nbox.x + nbox.w, top(u)), D)
    rect_track(t, t.track("shape", "Barra"), bar, lambda u: (bar.x, top(u), bar.x + bar.w, bottom(u)), D, RED,
               name="Barra")
    role = "MECHANICAL ENGINEER"
    rbox, rsize = caps_box(477, 870, 937, role)
    clip = name_text(t, role, rbox, rsize, D, name="Cargo", spacing=-2.4, word_spacing=6)
    mask_track(t, clip, rbox, lambda u: (bar.x, top(u), bar.x + bar.w, bottom(u)), D)
    return t


TEMPLATES = [francois]
