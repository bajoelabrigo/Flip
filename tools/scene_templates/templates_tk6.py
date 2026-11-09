"""TIKTOK folder video 6 as Stock templates (tk6-*). See docs/plan-tiktok.md.

«Flow Reels» teal (48513800.mp4, 1920×1080 at 29.97 fps): the same pack as tk5 in another look — rounded teal panels
with a white margin, photo collages and big bold words turned upright. Laid out on 1080×1920 from the «PREVIEW OF ALL
SCENES» grid (×4.72) and the big phone that plays every story (34–63 s), studied on 10 fps sheets. Kit de TikTok; ids
`tk6-*`, order 14600-. Study notes in tienda/plantillas/estudio-48513800/NOTAS.md.

The motion system is tk5's (`templates_tk5.Story`): panels and photo slots slide in from the edges with a white
border that makes the gaps, photo windows close in on their photo when a word panel pushes in, and the words fade in
letter by letter. Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5×.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import tall
from scene import effect, gradient, no_stroke
from templates_tit_c import k
from templates_tit_e import solid
from templates_tit_h import ring
from templates_tk5 import CAP, H, W, Story, dur_for, finish

OR, M = "Orbitron", "Montserrat"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold")):
    f6._FILES[(OR, _w)] = f"fonts.extra/fonts/orbitron/Orbitron-{_f}.ttf"
CAP[OR] = 0.72
INK = "#F4FFFC"
TEAL = "#2FAFA4"
R = 30.0   # corner radius
E = 32     # white margin round the story
GAP = 30   # white gap between panels (each panel's border is half of it... the whole of it over what it covers)
LOOK = [effect("duotone", strength=0.7, shadowColor="#06403D", highlightColor="#A8F2E6", contrast=0.5)]


def teal():
    """A word panel: teal, a little lighter at the bottom."""
    return [gradient([(0.0, "#2AA89E"), (1.0, "#3FC2B6")], angle=90), no_stroke()]


def teal_deep():
    return [gradient([(0.0, "#12948E"), (1.0, "#0E646D")], angle=90), no_stroke()]


def teal_cta():
    return [gradient([(0.0, "#2A948C"), (1.0, "#4FCBCB")], angle=90), no_stroke()]


def _p(id, es, en, order, dur, tags=()):
    return tall(f"tk6-{id}", es, en, "tiktok", dur, order=order,
                tags=["tiktok", "historia", "reels", "turquesa"] + list(tags), thumb_at=round(dur * 0.55, 1))


def story(id, es, en, order, entrance, tags=(), hold=2.2):
    D = dur_for(entrance, hold)
    t = _p(id, es, en, order, D, tags)
    s = Story(t, D)
    s.rect("Fondo", solid("#FFFFFF"), lambda fr, u: (-10, -10, W + 10, H + 10))
    return t, s


def pic(s, name, sample, rect, frm, at, n, label=None, **kw):
    return s.pic(name, sample, rect, frm, at, n, label=label or "Tu foto", radius=R, border=GAP, look=LOOK, **kw)


def box(s, name, rect, frm, at, n, layers=None):
    return s.panel(name, rect, frm, at, n, layers or teal(), radius=R, border=GAP)


def word(s, text, rect, off, at, name="Título", lines=None, fill=0.78, cap=None, stagger=0.05):
    """Bold words turned to read upwards, centred in panel rect: one line, or `lines` side by side (the first on the
    left); they take `fill` of the panel's height at most."""
    x0, y0, x1, y1 = rect
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rows = lines or [text]
    n = len(rows)
    width = x1 - x0
    cap = cap or min(width * 0.62 / n, 150)
    pitch = cap * 1.25
    out = []
    for i, row in enumerate(rows):
        lx = cx + (i - (n - 1) / 2) * pitch
        out.append(s.line(row, 0, (y1 - y0) * fill, 0, cap, INK, name if i == 0 else f"{name} {i + 1}", OR, 900,
                          off=off, at=at + 3 * i, stagger=stagger, duration=0.25, rot=-90, cx=lx, cy=cy,
                          spread=False, min_gap=0.02))
    return out


# columns of the grid stories
C2 = ((E, E + (W - 2 * E - GAP) / 2), (E + (W - 2 * E - GAP) / 2 + GAP, W - E))
_c3 = (W - 2 * E - 2 * GAP) / 3
C3 = tuple((E + i * (_c3 + GAP), E + i * (_c3 + GAP) + _c3) for i in range(3))


# --- 1. DISCOVERY / SPACESUIT: six cells close in round a flamingo photo, two word columns -------------------------
def discovery():
    t, s = story("discovery", "Historia: DISCOVERY y SPACESUIT en collage", "Story: DISCOVERY and SPACESUIT collage",
                 14600, 1.7, ["foto", "collage", "vertical"])
    top, mid, bot = (E, 480), (510, 1475), (1505, H - E)
    pic(s, "Foto", "h-nature-04", (C2[0][0], top[0], C2[0][1], top[1]), (-W, 0), 0, 14, "Foto 1")
    pic(s, "Foto 2", "flowers-02", (C2[1][0], top[0], C2[1][1], top[1]), (W, 0), 3, 14, "Foto 2")
    pic(s, "Foto 3", "fx-fashion-06", (325, mid[0], 755, mid[1]), (0, -H), 6, 15, "Foto 3")
    pic(s, "Foto 4", "city-03", (C2[0][0], bot[0], C2[0][1], bot[1]), (-W, 0), 9, 14, "Foto 4")
    pic(s, "Foto 5", "summer-04", (C2[1][0], bot[0], C2[1][1], bot[1]), (W, 0), 12, 14, "Foto 5")
    a = (E, mid[0], 295, mid[1])
    b = (785, mid[0], W - E, mid[1])
    oa = box(s, "Panel", a, (0, H), 14, 14)
    ob = box(s, "Panel 2", b, (0, -H), 16, 14)
    word(s, "DISCOVERY", a, oa, 26)
    word(s, "SPACESUIT", b, ob, 29, name="Título 2")
    return finish(t)


# --- 2. FLOWER BEAUTY: six photo cells slide in round a word panel --------------------------------------------------
def flower():
    t, s = story("flower", "Historia: FLOWER BEAUTY en collage", "Story: FLOWER BEAUTY collage", 14601, 1.7,
                 ["foto", "collage", "vertical"])
    top, mid, bot = (E, 645), (675, 1250), (1280, H - E)
    pic(s, "Foto", "travel-05", (C2[0][0], top[0], C2[0][1], top[1]), (0, -H), 0, 14, "Foto 1")
    pic(s, "Foto 2", "beach-04", (C2[1][0], top[0], C2[1][1], top[1]), (W, 0), 3, 14, "Foto 2")
    pic(s, "Foto 3", "fx-woman-07", (C3[0][0], mid[0], C3[0][1], mid[1]), (-W, 0), 6, 14, "Foto 3")
    pic(s, "Foto 4", "y6-dessert-02", (C3[2][0], mid[0], C3[2][1], mid[1]), (W, 0), 8, 14, "Foto 4")
    pic(s, "Foto 5", "fx-beach-02", (C2[0][0], bot[0], C2[0][1], bot[1]), (-W, 0), 10, 14, "Foto 5")
    pic(s, "Foto 6", "h-nature-03", (C2[1][0], bot[0], C2[1][1], bot[1]), (0, H), 12, 14, "Foto 6")
    a = (C3[1][0], mid[0], C3[1][1], mid[1])
    off = box(s, "Panel", a, (0, H), 14, 14)
    word(s, "FLOWER BEAUTY", a, off, 26, lines=["FLOWER", "BEAUTY"], fill=0.8)
    return finish(t)


# --- 3. DREAMS: two rows of three columns, the word in the top middle one -------------------------------------------
def dreams():
    t, s = story("dreams", "Historia: DREAMS en collage", "Story: DREAMS collage", 14602, 1.6,
                 ["foto", "collage", "vertical"])
    top, bot = (E, 945), (975, H - E)
    pic(s, "Foto", "fx-beach-03", (C3[0][0], top[0], C3[0][1], top[1]), (0, -H), 0, 14, "Foto 1")
    pic(s, "Foto 2", "garden-02", (C3[2][0], top[0], C3[2][1], top[1]), (0, -H), 4, 14, "Foto 2")
    pic(s, "Foto 3", "h-nature-06", (C3[0][0], bot[0], C3[0][1], bot[1]), (0, H), 2, 14, "Foto 3")
    pic(s, "Foto 4", "fx-man-04", (C3[1][0], bot[0], C3[1][1], bot[1]), (0, H), 6, 14, "Foto 4")
    pic(s, "Foto 5", "travel-08", (C3[2][0], bot[0], C3[2][1], bot[1]), (0, H), 10, 14, "Foto 5")
    a = (C3[1][0], top[0], C3[1][1], top[1])
    off = box(s, "Panel", a, (0, -H), 12, 14)
    word(s, "DREAMS", a, off, 24, fill=0.82)
    return finish(t)


# --- 4. STARRY NIGHTS: a deep teal panel opens from a strip with the words; it shrinks to the top cell and three
# photos close in round it ---------------------------------------------------------------------------------------
def starry():
    t, s = story("starry", "Historia: STARRY NIGHTS que se encoge al collage", "Story: STARRY NIGHTS shrinking into a collage",
                 14603, 2.4, ["foto", "collage", "vertical"], hold=2.0)
    full = (E, E, W - E, H - E)
    cell = (C3[1][0], E, C3[1][1], 580)
    q = lambda fr: k(fr, 36, 14)  # noqa: E731  full panel → cell
    o = lambda fr: k(fr, 0, 10)  # noqa: E731  the strip opens

    def rect(fr):
        x0 = 520 + (full[0] - 520) * o(fr)
        x1 = 560 + (full[2] - 560) * o(fr)
        r0 = (x0, full[1], x1, full[3])
        return tuple(r0[i] + (cell[i] - r0[i]) * q(fr) for i in range(4))
    pic(s, "Foto 3", "fx-citynight-05", (E, 610, W - E, H - E), (0, H), 36, 16, "Foto 3")
    pic(s, "Foto", "fx-man-05", (C3[0][0], E, C3[0][1], 580), (-W, 0), 38, 14, "Foto 1")
    pic(s, "Foto 2", "h-nature-04", (C3[2][0], E, C3[2][1], 580), (W, 0), 40, 14, "Foto 2")
    s.rect("Panel (borde)", solid("#FFFFFF"), lambda fr, u: (rect(fr)[0] - GAP, rect(fr)[1] - GAP, rect(fr)[2] + GAP,
                                                             rect(fr)[3] + GAP), radius=R + GAP,
           base=(full[2] - full[0] + 2 * GAP, full[3] - full[1] + 2 * GAP))
    s.rect("Panel", teal_deep(), lambda fr, u: rect(fr), radius=R, base=(full[2] - full[0], full[3] - full[1]))
    # the words are laid out for the full panel and scale with it
    big = (full[2] - full[0]) / 2.0
    sc = lambda fr: 1 + ((cell[2] - cell[0]) / (full[2] - full[0]) - 1) * q(fr)  # noqa: E731
    fcx, fcy = (full[0] + full[2]) / 2, (full[1] + full[3]) / 2
    ccx, ccy = (cell[0] + cell[2]) / 2, (cell[1] + cell[3]) / 2
    for i, row in enumerate(("STARRY", "NIGHTS")):
        lx = fcx + (i - 0.5) * 300
        clip = s.line(row, 0, 1300, 0, 230, INK, "Título" if i == 0 else "Título 2", OR, 900, at=6 + 3 * i,
                      stagger=0.05, duration=0.25, rot=-90, cx=lx, cy=fcy, spread=False, min_gap=0.02)

        def geom(fr, u, lx=lx):
            c = sc(fr)
            px = fcx + (ccx - fcx) * q(fr) + (lx - fcx) * c
            py = fcy + (ccy - fcy) * q(fr)
            return px - lx, py - fcy, c, -90, 1.0
        s.tmove(clip, geom)
    del big
    return finish(t)


# --- 5. WIND / AURA: two photo rows; a word panel pushes in from each side and the photos' windows close in --------
def wind():
    t, s = story("wind", "Historia: WIND y AURA con dos fotos", "Story: WIND and AURA with two photos", 14604, 1.6,
                 ["foto", "collage", "vertical"])
    top, bot = (E, 945), (975, H - E)
    pic(s, "Foto", "y5-h-ocean-01", (E, top[0], W - E, top[1]), (0, -H), 0, 14, "Foto 1",
        crop=lambda fr: (E, top[0], W - E - (W - E - 645) * k(fr, 16, 12), top[1]))
    pic(s, "Foto 2", "fx-fashion-04", (E, bot[0], W - E, bot[1]), (0, H), 2, 14, "Foto 2",
        crop=lambda fr: (E + (420 - E) * k(fr, 18, 12), bot[0], W - E, bot[1]))
    a = (675, top[0], W - E, top[1])
    b = (E, bot[0], 390, bot[1])
    oa = box(s, "Panel", a, (W - 675 + GAP, 0), 16, 12)
    ob = box(s, "Panel 2", b, (-390 - GAP, 0), 18, 12)
    word(s, "WIND", a, oa, 26, fill=0.8)
    word(s, "AURA", b, ob, 28, name="Título 2", fill=0.8)
    return finish(t)


# --- 6. TIME'S NOW: two photo columns; a word panel rises in the left one and its photo's window closes up ---------
def times_now():
    t, s = story("times-now", "Historia: TIME'S NOW con dos fotos", "Story: TIME'S NOW with two photos", 14605, 1.5,
                 ["foto", "vertical"])
    col_l, col_r = C2
    pic(s, "Foto 2", "fx-woman-05", (col_r[0], E, col_r[1], H - E), (W, 0), 0, 14, "Foto 2")
    pic(s, "Foto", "flowers-03", (col_l[0], E, col_l[1], H - E), (0, -H), 3, 14, "Foto 1",
        crop=lambda fr: (col_l[0], E, col_l[1], H - E - (H - E - 945) * k(fr, 16, 12)))
    a = (col_l[0], 975, col_l[1], H - E)
    off = box(s, "Panel", a, (0, H - 975 + GAP), 16, 12)
    word(s, "TIME'S NOW", a, off, 26, lines=["TIME'S", "NOW"], fill=0.85)
    return finish(t)


# --- 7. FREEDOM: a tall word column from the left beside a photo column from the right ------------------------------
def freedom():
    t, s = story("freedom", "Historia: FREEDOM en columna", "Story: FREEDOM column", 14606, 1.3, ["foto", "vertical"])
    col_l, col_r = C2
    pic(s, "Foto", "fx-figure-03", (col_r[0], E, col_r[1], H - E), (0, -H), 0, 15)
    a = (col_l[0], E, col_l[1], H - E)
    off = box(s, "Panel", a, (0, H), 4, 15)
    word(s, "FREEDOM", a, off, 18, fill=0.86, cap=200)
    return finish(t)


# --- 8. MODERN STORIES: two photo columns, then a word panel rises on the left and two photos close in on the right
def modern():
    t, s = story("modern", "Historia: MODERN STORIES en collage", "Story: MODERN STORIES collage", 14607, 1.9,
                 ["foto", "collage", "vertical"])
    col_l, col_r = C2
    pic(s, "Foto", "y5-h-street-03", (col_l[0], E, col_l[1], H - E), (0, -H), 0, 14, "Foto 1",
        crop=lambda fr: (col_l[0], E, col_l[1], H - E - (H - E - 830) * k(fr, 26, 12)))
    pic(s, "Foto 2", "fx-woman-08", (col_r[0], E, col_r[1], H - E), (0, H), 2, 14, "Foto 2",
        crop=lambda fr: (col_r[0], E + (530 - E) * k(fr, 28, 12), col_r[1], H - E - (H - E - 1230) * k(fr, 30, 12)))
    pic(s, "Foto 3", "flowers-01", (col_r[0], E, col_r[1], 500), (0, -560), 28, 12, "Foto 3")
    pic(s, "Foto 4", "fx-figure-05", (col_r[0], 1260, col_r[1], H - E), (0, H - 1260 + GAP), 30, 12, "Foto 4")
    a = (col_l[0], 860, col_l[1], H - E)
    off = box(s, "Panel", a, (0, H - 860 + GAP), 26, 12)
    word(s, "MODERN STORIES", a, off, 36, lines=["MODERN", "STORIES"], fill=0.8)
    return finish(t)


# --- 9. Photo from the top: a rounded photo drops in with its white frame ---------------------------------------
def photo_drop():
    t, s = story("foto-cae", "Historia: foto con marco que baja", "Story: framed photo dropping in", 14608, 0.8,
                 ["foto"], hold=2.0)
    pic(s, "Foto", "flowers-02", (E, E, W - E, H - E), (0, -H), 0, 16)
    return finish(t)


# --- 10. Photo from the side: a rounded photo sweeps in from the left -----------------------------------------------
def photo_side():
    t, s = story("foto-lado", "Historia: foto con marco que entra de lado", "Story: framed photo sliding in", 14609,
                 0.8, ["foto"], hold=2.0)
    pic(s, "Foto", "travel-09", (E, E, W - E, H - E), (-W, 0), 0, 16)
    return finish(t)


# --- 11. SAVOR LIFE'S GOODNESS: a teal panel from the right, the logo lights up, the words rise, a swipe-up tab -----
def savor():
    t, s = story("savor", "Historia: llamada a la acción SAVOR LIFE'S GOODNESS",
                 "Story: SAVOR LIFE'S GOODNESS call to action", 14610, 1.9, ["llamada a la acción", "logo", "deslizar"])
    off = s.panel("Panel", (E, E, W - E, H - E), (W, 0), 0, 12, teal_cta(), radius=R, border=GAP)
    s.logo(540, 640, 430, op=lambda fr: 0.3 * k(fr, 3, 6) + 0.7 * k(fr, 8, 24), off=off)
    for i, (word_, cap, w, y) in enumerate((("SAVOR", 54, 270, 990), ("LIFE'S", 104, 430, 1066),
                                            ("GOODNESS", 54, 430, 1196))):
        c = s.line(word_, 540 - w / 2, 540 + w / 2, y, y + cap, INK, ("Texto", "Título", "Texto 2")[i], M, 900,
                   at=24 + 4 * i, stagger=0.03, duration=0.3, spread=False, min_gap=0.03)
        s.tmove(c, lambda fr, u, i=i: (off(fr)[0], off(fr)[1] + 24 * (1 - k(fr, 24 + 4 * i, 9)), 1, 0, 1))
    # the tab: a white pill rising from the bottom edge with teal chevrons and the words
    tab = lambda fr: (H - E - 10) + 260 * (1 - k(fr, 30, 10))  # noqa: E731  top of the tab
    s.rect("Botón", solid("#FFFFFF"), lambda fr, u: (470, tab(fr) - 170, 610, tab(fr) + 200), radius=70,
           base=(140, 370))
    chev = "M 0 100 L 50 0 L 100 100"
    for i, dy in enumerate((-120, -92, -64)):
        s.obj(f"Botón (flecha {i + 1})", ring("#2FAFA4", 7),
              lambda fr, u, dy=dy, i=i: (540, tab(fr) + dy, 64, 22, 0, k(fr, 36 + 3 * i, 5)), path=chev, base=(64, 22))
    c = s.line("SWIPE UP", 488, 592, 0, 18, "#2FAFA4", "Botón", M, 900, at=46, stagger=0.03, duration=0.15,
               spread=False, min_gap=0.04, cx=540, cy=H - E - 34)
    s.tmove(c, lambda fr, u: (0, 260 * (1 - k(fr, 30, 10)), 1, 0, 1))
    return finish(t)


TEMPLATES = [discovery, flower, dreams, starry, wind, times_now, freedom, modern, photo_drop, photo_side, savor]
