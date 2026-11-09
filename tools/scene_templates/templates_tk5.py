"""TIKTOK folder video 5 as Stock templates (tk5-*). See docs/plan-tiktok.md.

«Flow Reels» black and white (48372050.mp4, 1920×1080 at 29.97 fps): vertical photo-collage stories shown in the
reference inside phones, in a «PREVIEW OF ALL SCENES» grid and played one after another on a big phone (34–63 s).
Each story is laid out flat on 1080×1920 from the grid tiles (×4.74) and the big phone (screen ×3.8), with the moves
studied on 10 and 30 fps sheets. Kit de TikTok; ids `tk5-*`, order 14500-. Study notes in
tienda/plantillas/estudio-48372050/NOTAS.md.

The motion system (shared with tk6, which imports it): on the story's white ground, panels (dark gradient boxes or
photo slots) slide in from an edge or a corner, each one with a white border that makes the gaps between panels; the
words fade in letter by letter. Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5×.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of
from scene import effect, gradient, keys, no_stroke
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, ring
from templates_yp4 import art_except

W, H = 1080, 1920
G = 26  # the white gap between panels
WHITE, GREY = "#F2F2F2", "#9C9C9C"
M = "Montserrat"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
               (900, "Black")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
CAP = {M: 0.70}  # capital height in em, to size a line by its capitals
BW = [effect("color.basic", saturation=-1.0, contrast=0.12)]


def dark_tall():
    """The pack's dark panel: light grey at the top right to black at the bottom left."""
    return [gradient([(0.0, "#4E4E4E"), (1.0, "#040404")], angle=112), no_stroke()]


def dark_band():
    return [gradient([(0.0, "#3A3A3A"), (1.0, "#090909")], angle=0), no_stroke()]


def dur_for(entrance, hold=2.2):
    return round(entrance + hold + entrance / EXIT, 1)


class Story(S):
    """A vertical story slide on 1080×1920 (white ground)."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)

    # --- panels ---------------------------------------------------------------------------------------------------
    @staticmethod
    def mover(frm, at, n):
        """(dx, dy)(fr): from offset frm to rest, easing over n frames from frame at."""
        return lambda fr: (frm[0] * (1 - k(fr, at, n)), frm[1] * (1 - k(fr, at, n)))

    def panel(self, name, rect, frm, at, n, layers=None, radius=0.0, border=G, border_op=None, ground=WHITE):
        """A box at rect = (x0, y0, x1, y1) that slides in from offset frm = (dx, dy); a ground-coloured border of
        `border` px around it makes the gap where it lands on other panels. Returns its offset fn(fr)."""
        off = self.mover(frm, at, n)
        x0, y0, x1, y1 = rect
        if border:
            def edge(fr, u):
                dx, dy = off(fr)
                return x0 - border + dx, y0 - border + dy, x1 + border + dx, y1 + border + dy
            self.rect(f"{name} (borde)", solid(ground), edge, op=border_op,
                      radius=radius + border if radius else 0.0, base=(x1 - x0 + 2 * border, y1 - y0 + 2 * border))
        if layers is not None:
            self.rect(name, layers, lambda fr, u: (x0 + off(fr)[0], y0 + off(fr)[1], x1 + off(fr)[0], y1 + off(fr)[1]),
                      radius=radius, base=(x1 - x0, y1 - y0))
        return off

    def pic(self, name, sample, rect, frm, at, n, label="Tu foto", radius=0.0, border=G, look=None, reuse=None,
            ground=WHITE, zoom=None, crop=None):
        """A photo slot filling rect, sliding in with its panel; cut to the panel by a track matte (so rounded
        corners work). zoom(fr, u) scales the photo inside its panel; crop(fr) = (x0, y0, x1, y1) narrows the
        window it shows (the photo stays put, its frame closes in)."""
        x0, y0, x1, y1 = rect
        win = crop or (lambda fr: rect)
        off = self.mover(frm, at, n)
        if border:
            self.rect(f"{name} (marco)", solid(ground),
                      lambda fr, u: (win(fr)[0] - border + off(fr)[0], win(fr)[1] - border + off(fr)[1],
                                     win(fr)[2] + border + off(fr)[0], win(fr)[3] + border + off(fr)[1]),
                      radius=radius + border if radius else 0.0, base=(x1 - x0 + 2 * border, y1 - y0 + 2 * border))
        matte = self.rect(f"{name} (forma)", solid("#FFFFFF"),
                          lambda fr, u: (win(fr)[0] + off(fr)[0], win(fr)[1] + off(fr)[1], win(fr)[2] + off(fr)[0],
                                         win(fr)[3] + off(fr)[1]),
                          radius=radius, base=(x1 - x0, y1 - y0))
        box = Box(x0, y0, x1 - x0, y1 - y0)
        motion = []
        for u in frames_of(self.dur):
            fr = self.frame(u)
            sc = zoom(fr, u) if zoom else 1.0
            motion.append((u, {"s": sc, "dx": off(fr)[0], "dy": off(fr)[1]}, "linear"))
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, box, motion, label=label,
                            reuse=reuse)
        clip["name"] = name
        if look:
            clip["effects"] = [dict(e) for e in look]
        clip["matte"] = {"clip": matte["id"], "mode": "alpha"}
        return clip

    # --- words ----------------------------------------------------------------------------------------------------
    def line(self, content, x0, x1, top, bottom, colour=WHITE, name="Título", family=M, weight=400, off=None,
             at=0, stagger=0.04, duration=0.3, order="random", rot=0.0, cx=None, cy=None, editable=True,
             min_gap=0.03, spread=True, preset="fade"):
        """One line of capitals: its ink spans x0..x1 and its capitals top..bottom (letter spacing makes both fit),
        riding a panel's offset off(fr); the letters fade in from frame `at`. With rot (−90 = reading upwards) the
        line is laid out level about (cx, cy) and turned there."""
        width, cap = x1 - x0, bottom - top
        unit, _ = f6.fit(content.upper(), 1000, family, weight)
        ink_em = 1000 / unit
        n = max(1, len(content) - 1)
        # sized by the capitals unless the letters would then have to overlap to fit: then by the width
        size = min(cap / CAP.get(family, 0.70), width / (ink_em + min_gap * n))
        spacing = (width / size - ink_em) / n if spread else min_gap
        if not spread:
            width = size * (ink_em + min_gap * n)
        if cx is None:
            cx, cy = (x0 + x1) / 2, (top + bottom) / 2
        p = f6.Piece(self.t, self.dur, 0)
        p.frame = self.frame
        shift = (lambda fr: off(fr)) if off else None
        clip = p.text(content, cx, cy - cap / 2, cy + cap / 2, width, family, weight, colour, name, align="center",
                      spacing_em=spacing, shift=shift, editable=editable)
        if rot:
            clip["rotation"] = keys([(0.0, rot, "hold")])
        self.typed(clip, at, stagger=stagger, duration=duration, preset=preset, order=order)
        return clip

    def logo(self, cx, cy, size, op=None, off=None):
        """The user's logo in a size × size box centred at (cx, cy)."""
        box = Box(cx - size / 2, cy - size / 2, size, size)
        motion = [(u, {"dx": off(self.frame(u))[0] if off else 0.0, "dy": off(self.frame(u))[1] if off else 0.0},
                   "linear") for u in frames_of(self.dur)]
        clip = self.t.photo(self.t.track("video", "Logo"), "logo-flip", 0.0, self.dur, box, motion, label="Tu logo",
                            brandRole="logo")
        clip["name"] = "Logo"
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(self.frame(u)))), 4), "linear")
                                    for u in frames_of(self.dur)])
        return clip

    def swipe_up(self, at, cy=1800, colour="#FFFFFF", text_colour=None, word="SWIPE UP", family=M, weight=900,
                 width=272, cap=40, off=None):
        """The call-to-action button: a line grows into a pill around the letters, the pill opens and two chevrons
        stack up above the words."""
        o = off or (lambda fr: (0.0, 0.0))
        cx = W / 2

        def line_(fr, u):
            dx, dy = o(fr)
            w = 190 * k(fr, at, 5)
            return cx + dx, cy + 34 + dy, w, 6, 0, 1.0 - k(fr, at + 5, 3)
        self.obj("Botón (línea)", solid(colour), line_)

        def pill(fr, u):
            dx, dy = o(fr)
            h = 6 + 70 * k(fr, at + 4, 5)
            return cx + dx, cy + 37 - h / 2 + dy, 330, h, 0, k(fr, at + 4, 2) * (1 - k(fr, at + 11, 5))
        self.obj("Botón (píldora)", ring(colour, 6), pill, radius=38, base=(330, 76))
        chev = "M 0 100 L 50 0 L 100 100"
        for i, (y, a) in enumerate(((cy - 74, at + 12), (cy - 104, at + 16))):
            def ch(fr, u, y=y, a=a):
                dx, dy = o(fr)
                q = k(fr, a, 5)
                return cx + dx, y + 12 * (1 - q) + dy, 92, 4 + 28 * q, 0, k(fr, a, 2)
            self.obj(f"Botón (flecha {i + 1})", ring(colour, 7), ch, path=chev, base=(92, 32))
        return self.line(word, cx - width / 2, cx + width / 2, cy - cap / 2, cy + cap / 2, text_colour or colour,
                         "Botón", family, weight, off=off, at=at + 5, stagger=0.03, duration=0.12)


def _p(id, es, en, order, dur, tags=()):
    return tall(f"tk5-{id}", es, en, "tiktok", dur, order=order,
                tags=["tiktok", "historia", "reels", "blanco y negro"] + list(tags), thumb_at=round(dur * 0.55, 1))


def story(id, es, en, order, entrance, tags=()):
    D = dur_for(entrance)
    t = _p(id, es, en, order, D, tags)
    s = Story(t, D)
    s.rect("Fondo", solid("#FFFFFF"), lambda fr, u: (-10, -10, W + 10, H + 10))
    return t, s


def finish(t):
    return art_except(t)


# --- 1. SUNSHINE FILLS SKIES: a photo from the left over the top half, a dark panel rises under it ----------------
def sunshine():
    t, s = story("sunshine", "Historia: SUNSHINE FILLS SKIES con foto", "Story: SUNSHINE FILLS SKIES with a photo",
                 14500, 1.6, ["foto", "collage"])
    s.pic("Foto", "couple-06", (0, 0, W, 962), (-W, 0), 0, 16, look=BW)
    off = s.panel("Panel", (0, 988, W, H), (0, H - 988), 4, 16, dark_tall())
    s.line("SUNSHINE", 188, 888, 1187, 1295, WHITE, "Texto", off=off, at=14, stagger=0.035)
    s.line("FILLS", 180, 895, 1372, 1588, WHITE, "Título", off=off, at=18, stagger=0.05)
    s.line("SKIES", 180, 895, 1648, 1858, WHITE, "Título 2", off=off, at=22, stagger=0.05)
    return finish(t)


# --- 2. FIND HIDDEN GEMS: a dark panel sweeps in from the left over a strip from the right; the words fade in ------
def find_gems():
    t, s = story("find", "Historia: FIND HIDDEN GEMS", "Story: FIND HIDDEN GEMS", 14501, 1.4, ["texto"])
    s.panel("Franja", (W - 120, 0, W, H), (160, 0), 0, 9, dark_tall())
    off = s.panel("Panel", (0, 0, W, H), (-W - G, 0), 0, 15, dark_tall())
    s.line("FIND", 180, 888, 612, 837, WHITE, "Título", off=off, at=6, stagger=0.06)
    s.line("HIDDEN", 180, 895, 920, 1055, WHITE, "Texto", off=off, at=9, stagger=0.05)
    s.line("GEMS", 180, 895, 1130, 1305, WHITE, "Título 2", off=off, at=13, stagger=0.06)
    return finish(t)


# --- 3. CAREFREE LIVING: a photo column from the top right corner, a dark column from the bottom left -------------
def carefree():
    t, s = story("carefree", "Historia: CAREFREE LIVING en vertical", "Story: vertical CAREFREE LIVING", 14502, 1.6,
                 ["foto", "vertical"])
    s.pic("Foto", "couple-07", (558, 0, W, H), (W - 558, -H), 0, 18, look=BW)
    off = s.panel("Panel", (0, 0, 532, H), (-532, H), 4, 18, dark_tall())
    s.line("CAREFREE LIVING", 250, 1663, 0, 138, WHITE, off=off, at=18, stagger=0.03, rot=-90, cx=266, cy=956)
    return finish(t)


# --- 4. Photo in two strokes: the photo drops from the top, then rises again from the bottom over it ------------
def photo_drop():
    t, s = story("foto-cae", "Historia: foto que baja y sube", "Story: photo dropping and rising", 14503, 1.0,
                 ["foto"])
    first = s.pic("Foto", "fx-couple-04", (0, 0, W, H), (0, -H), 0, 13, look=BW)
    s.pic("Foto (segunda)", "fx-couple-04", (0, 0, W, H), (0, H + G), 8, 16, look=BW, reuse=first["placeholderId"])
    return finish(t)


# --- 5. LAUGHTER OF A LOVED ONE: a photo rises full screen, a dark panel drops over its top -----------------------
def laughter():
    t, s = story("laughter", "Historia: LAUGHTER OF A LOVED ONE", "Story: LAUGHTER OF A LOVED ONE", 14504, 1.9,
                 ["foto"])
    s.pic("Foto", "friends-11", (0, 0, W, H), (0, H + G), 0, 18, look=BW)
    off = s.panel("Panel", (0, 0, W, 937), (0, -937 - G), 16, 13, dark_tall())
    s.line("LAUGHTER", 194, 875, 212, 300, WHITE, "Texto", off=off, at=22, stagger=0.035)
    s.line("OF A LOVED", 194, 875, 375, 462, GREY, "Texto 2", off=off, at=26, stagger=0.035)
    s.line("ONE", 202, 870, 525, 750, WHITE, "Título", off=off, at=30, stagger=0.07)
    return finish(t)


# --- 6. ENDLESS LOVING CONVERSATIONS: a dark panel rises, a band drops over its top; the words fade in -------------
def endless():
    t, s = story("endless", "Historia: ENDLESS LOVING CONVERSATIONS", "Story: ENDLESS LOVING CONVERSATIONS", 14505,
                 1.4, ["texto"])
    off = s.panel("Panel", (0, 0, W, H), (0, H + G), 0, 16, dark_tall())
    s.panel("Banda", (0, 0, W, 300), (0, -300 - G), 8, 12, dark_band(), border_op=lambda fr, u: 1 - k(fr, 18, 4))
    s.line("ENDLESS", 112, 962, 625, 762, WHITE, "Título", off=off, at=10, stagger=0.04)
    s.line("LOVING", 112, 962, 825, 980, WHITE, "Título 2", off=off, at=13, stagger=0.045)
    s.line("CONVERSATIONS", 103, 977, 1032, 1107, GREY, "Texto", off=off, at=18, stagger=0.025)
    return finish(t)


# --- 7. FREEDOM / PLEASING: two photos meet in the middle, a band drops at the top and another rises at the bottom -
def freedom():
    t, s = story("freedom", "Historia: FREEDOM y PLEASING con dos fotos", "Story: FREEDOM and PLEASING with two photos",
                 14506, 1.6, ["foto", "collage"])
    s.pic("Foto", "couple-04", (0, 0, W, 950), (0, -950 - G), 0, 14, look=BW, label="Foto 1")
    s.pic("Foto 2", "fx-couple-02", (0, 976, W, H), (0, H - 976 + G), 3, 14, look=BW, label="Foto 2")
    top = s.panel("Banda", (0, 0, W, 430), (0, -430 - G), 16, 10, dark_band())
    bot = s.panel("Banda 2", (0, 1475, W, H), (0, H - 1475 + G), 16, 10, dark_band())
    s.line("FREEDOM", 146, 932, 175, 287, WHITE, "Título", off=top, at=20, stagger=0.04, order="forward")
    s.line("PLEASING", 150, 925, 1637, 1750, WHITE, "Título 2", off=bot, at=20, stagger=0.04, order="forward")
    return finish(t)


# --- 8. Photo from below: a full photo rises over the white ------------------------------------------------------
def photo_rise():
    t, s = story("foto-sube", "Historia: foto que sube", "Story: rising photo", 14507, 0.8, ["foto"])
    s.pic("Foto", "couple-08", (0, 0, W, H), (0, H + G), 0, 16, look=BW)
    return finish(t)


# --- 9. STARS / DREAMS: two photo columns slide past each other, dark panels close them --------------------------
def stars():
    t, s = story("stars", "Historia: STARS y DREAMS en columnas", "Story: STARS and DREAMS in columns", 14508, 1.6,
                 ["foto", "collage", "vertical"])
    s.pic("Foto", "fx-woman-04", (535, 728, W, H), (0, -H), 0, 15, look=BW, label="Foto 1")
    s.pic("Foto 2", "creator-02", (0, 0, 505, 885), (0, H), 4, 15, look=BW, label="Foto 2")
    top = s.panel("Panel", (535, 0, W, 702), (0, -702 - G), 14, 11, dark_tall())
    bot = s.panel("Panel 2", (0, 911, 505, H), (0, H - 911 + G), 16, 11, dark_tall())
    s.line("STARS", 0, 488, 0, 130, WHITE, "Título", off=top, at=22, stagger=0.05, rot=-90, cx=807, cy=351)
    s.line("DREAMS", 0, 640, 0, 124, WHITE, "Título 2", off=bot, at=24, stagger=0.05, rot=-90, cx=252, cy=1430)
    return finish(t)


# --- 10. FOLLOW YOUR DREAM: a dark panel sweeps in from the right over a strip from the left -------------------
def follow():
    t, s = story("follow", "Historia: FOLLOW YOUR DREAM", "Story: FOLLOW YOUR DREAM", 14509, 1.4, ["texto"])
    s.panel("Franja", (0, 0, 120, H), (-160, 0), 0, 9, dark_tall())
    off = s.panel("Panel", (0, 0, W, H), (W + G, 0), 0, 15, dark_tall())
    s.line("FOLLOW", 216, 864, 580, 680, WHITE, "Texto", off=off, at=7, stagger=0.045)
    s.line("YOUR", 222, 858, 730, 905, WHITE, "Título", off=off, at=10, stagger=0.06)
    s.line("DREAM", 222, 858, 945, 1095, WHITE, "Título 2", off=off, at=13, stagger=0.05)
    return finish(t)


# --- 11. Photo from the left: a full photo sweeps in over the white ----------------------------------------------
def photo_side():
    t, s = story("foto-lado", "Historia: foto que entra de lado", "Story: photo sliding in sideways", 14510, 0.8,
                 ["foto"])
    s.pic("Foto", "fx-walk-05", (0, 0, W, H), (-W - G, 0), 0, 16, look=BW)
    return finish(t)


# --- 12. JOIN THE JOURNEY: a dark panel from the left, the logo lights up, the words and a swipe-up button --------
def join():
    t, s = story("join", "Historia: llamada a la acción JOIN THE JOURNEY", "Story: JOIN THE JOURNEY call to action",
                 14511, 2.0, ["llamada a la acción", "logo", "deslizar"])
    s.panel("Franja", (W - 120, 0, W, H), (160, 0), 0, 9, dark_tall())
    off = s.panel("Panel", (0, 0, W, H), (-W - G, 0), 0, 15, dark_tall())
    s.logo(540, 780, 470, op=lambda fr: 0.25 * k(fr, 6, 6) + 0.75 * k(fr, 10, 24), off=off)
    s.line("JOIN", 409, 603, 1162, 1255, WHITE, "Título", off=off, at=24, stagger=0.06, spread=False)
    s.line("THE", 420, 590, 1300, 1392, WHITE, "Título 2", off=off, at=28, stagger=0.06, spread=False)
    s.line("JOURNEY", 260, 820, 1442, 1530, WHITE, "Título 3", off=off, at=32, stagger=0.045, spread=False)
    s.swipe_up(30, cy=1800, off=off)
    return finish(t)


TEMPLATES = [sunshine, find_gems, carefree, photo_drop, laughter, endless, freedom, photo_rise,
             stars, follow, photo_side, join]
