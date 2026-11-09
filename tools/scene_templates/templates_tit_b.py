"""Black and white typography, second TITLE set (2026-11-08): the sixteen of 52060224.mp4 (1920×1080 at 29.97 fps), a
minimal typography pack: big black or white words (Archivo Black, Montserrat, Kanit), black boxes and bars, three
over a photo. Each is a full-frame slide: its white or black background is a layer of its own («Fondo», which the
user can hide to put the words over a video); photos are slots. Laid out where the reference has them.
Kit de YouTube › Tipografía; ids `tit2-*`, order 8820-. Study notes in tienda/plantillas/estudio-52060224/NOTAS.md.
Every piece leaves with its entrance played backwards (the reference does exactly that). The author's credit in
the reference («Designe By Team_shop») is replaced by neutral words.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import keys, tanim
from templates_llt_f import table

FPS = 30000 / 1001
WHITE, BLACK = "#FFFFFF", "#000000"
f6._FILES[("Kanit", 600)] = "fonts.extra/fonts/kanit/Kanit-SemiBold.ttf"
f6._FILES[("Kanit", 700)] = "fonts.extra/fonts/kanit/Kanit-Bold.ttf"
for w, file in ((500, "Montserrat-Medium"), (700, "Montserrat-Bold"), (800, "Montserrat-ExtraBold"),
                (900, "Montserrat-Black"), (801, "Montserrat-ExtraBoldItalic")):
    f6._FILES[("Montserrat", w)] = f"fonts.basic/fonts/montserrat/{file}.ttf"


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"tit2-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:tipografia", "tipografía", "blanco y negro"] + tags, **kw)


class Slide:
    """One slide: u (seconds) → frame of the entrance (from the first that shows anything); it leaves with the
    entrance backwards."""

    def __init__(self, t, dur):
        self.t, self.dur = t, dur

    def frame(self, u):
        return min(u, self.dur - u) * FPS

    def background(self, colour):
        clip = self.t.solid(self.t.track("shape", "Fondo"), colour, 0.0, self.dur)
        clip["name"] = "Fondo"
        return clip

    def text(self, content, ink, family, weight, colour=WHITE, name="Título", case="none", italic=False,
             align="center", layers=None, reveal=None, editable=True, shift=None):
        """A line whose ink spans ink = (x0, top, x1, bottom) at rest, unturned; reveal(frame) = the screen rect
        it shows in."""
        x0, y0, x1, y1 = ink
        p = f6.Piece(self.t, self.dur, 0)
        p.frame = self.frame
        edge = (x0 + x1) / 2 if align == "center" else x0 if align == "left" else x1
        clip = p.text(content, edge, y0, y1, x1 - x0, family, weight, colour, name, align=align, case=case,
                      layers=layers, reveal=reveal, editable=editable, shift=shift)
        # 801 / 701 are the italic files of 800 / 700 (only to measure): the clip asks for the weight in italics.
        if weight in (801, 701):
            clip["textStyle"]["fontWeight"] = weight - 1
            italic = True
        if italic or (family == "Montserrat" and weight == 400 and "Italic" in f6._FILES[(family, weight)]):
            clip["textStyle"]["italic"] = True
        return clip

    def letters(self, clip, start, stagger, duration, preset="fade", unit="character", order_in="forward", **kw):
        """The text comes in letter by letter from frame `start` and goes out the same way backwards."""
        n = len(clip.get("textContent", "")) if unit == "character" else len(clip.get("textContent", "").split())
        whole = (n - 1) * stagger + duration
        lead = round(start / FPS, 3)
        clip["textStyle"]["animation"] = {
            "in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=lead,
                        order=order_in, **kw),
            "out": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeIn", delay=lead,
                         order="backward" if order_in == "forward" else order_in, **kw)}
        return whole

    def fade(self, clip, op):
        clip["opacity"] = keys([(u, round(op(self.frame(u)), 4), "linear") for u in frames_of(self.dur)])

    def box(self, name, colour, rect):
        """A solid box covering rect(frame) = (x0, y0, x1, y1) every frame."""
        p = f6.Piece(self.t, self.dur, 0)
        p.frame = self.frame
        return p.shape(name, colour, (0, 0, 1920, 1080), rect)

    def turn(self, clip, deg):
        clip["rotation"] = keys([(0.0, deg, "hold")])

    def move(self, clip, shift=None, scale=None):
        """Moves a still clip by shift(frame) = (dx, dy) and scales it by scale(frame) about its centre."""
        x, y = clip["x"]["keyframes"][0]["value"], clip["y"]["keyframes"][0]["value"]
        w, h = clip["width"]["keyframes"][0]["value"], clip["height"]["keyframes"][0]["value"]
        size = clip.get("textStyle", {}).get("pixelSize")
        xs, ys, ws, hs, sizes = [], [], [], [], []
        for u in frames_of(self.dur):
            fr = self.frame(u)
            dx, dy = shift(fr) if shift else (0.0, 0.0)
            k = max(1e-3, scale(fr)) if scale else 1.0
            xs.append((u, x + w / 2 + dx - w * k / 2, "linear"))
            ys.append((u, y + h / 2 + dy - h * k / 2, "linear"))
            ws.append((u, w * k, "linear"))
            hs.append((u, h * k, "linear"))
            sizes.append((u, (size or 0) * k, "linear"))
        clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
        if size and scale:
            clip["textStyle"]["keyframes"] = {"pixelSize": keys(sizes)}


def creative_tilt():
    """1: a huge «creative» turned 21.8°, its letters lighting up one by one; a two-line caption types in."""
    D = 4.4
    t = _kit("creative-inclinado", "Título: palabra gigante inclinada", "Title: huge tilted word", D, 8820,
             ["inclinado", "negro"], thumb_at=2.2)
    s = Slide(t, D)
    s.background(BLACK)
    # Measured: the word's box (unturned) is 2114 × 336 about (933, 567), turned −21.8°; the letters show from
    # 0.0 s every 0.075 s, each in 0.15 s.
    # Its type is wider than Archivo Black: set 5 % bigger so it runs as long, a little further along its line.
    import math
    a = math.radians(-21.8)
    cx, cy, half = 933 + 60 * math.cos(a), 567 + 60 * math.sin(a), 1057 * 1.05
    word = s.text("creative", (cx - half, cy - 168 * 1.05, cx + half, cy + 168 * 1.05), "Archivo", 900, WHITE)
    s.turn(word, -21.8)
    s.letters(word, 0, 0.075, 0.15)
    cap = s.text("Typography Pack //", (1162, 892, 1630, 925), "Kanit", 600, WHITE, "Texto", align="left")
    s.letters(cap, 4, 0.035, 0.1)
    cap2 = s.text("Designed by You", (1162, 943, 1702, 980), "Kanit", 600, WHITE, "Texto 2", align="left")
    s.letters(cap2, 12, 0.035, 0.1)
    return t


OUTLINE = [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
           {"id": "stroke", "kind": "stroke", "enabled": True, "width": 7, "strokeAlign": "outside", "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ffffffff"}}]


def new_trend():
    """2: on white, «New» darkens in, then «Trend» and «Creative»; a black panel rises from the bottom and over
    it the words turn to white outlines."""
    D = 4.6
    t = _kit("new-trend", "Título: New Trend que se invierte", "Title: New Trend that turns inside out", D, 8821,
             ["contorno", "blanco"], thumb_at=1.4)
    s = Slide(t, D)
    s.background(WHITE)
    top = table({21: 1080, 23: 892, 26: 795, 28: 697, 29: 645, 30: 577, 32: 420, 34: 200, 36: 0})
    s.box("Panel", BLACK, lambda fr: (0, top(fr), 1920, 1080))
    lines = [("New", (273, 357, 852, 538), "Título", table({0: 0.0, 14: 1.0}), None),
             ("Trend", (943, 357, 1720, 538), "Título 2", table({16: 0.0, 22: 1.0}), None),
             ("Creative", (633, 556, 1302, 677), "Título 3", table({16: 0.0, 22: 1.0}), table({16: 18, 22: 0}))]
    for text, ink, name, op, rise in lines:
        black = s.text(text, ink, "Montserrat", 800, BLACK, name)
        s.fade(black, op)
        if rise:
            s.move(black, shift=lambda fr, r=rise: (0.0, r(fr)))
        # The same words as white outlines, only over the panel (a second copy: edit both).
        s.text(text, ink, "Montserrat", 800, WHITE, name + " (contorno)", layers=OUTLINE,
               reveal=lambda fr: (0, top(fr), 1920, 1080))
    return t


f6._FILES[("Montserrat", 400)] = "fonts.basic/fonts/montserrat/Montserrat-Italic.ttf"
f6._FILES[("Montserrat", 701)] = "fonts.basic/fonts/montserrat/Montserrat-BoldItalic.ttf"
# A soft dark drop shadow (it goes before the fill: the first layer is drawn underneath).
SHADOW = {"id": "shadow", "kind": "shadow", "enabled": True, "paint": {"kind": "solid", "color": "#ff000000"},
          "offsetX": 8, "offsetY": 12, "blur": 12, "opacity": 0.85}


def solid_fill(colour):
    return {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def ease_in(a, b, f0, f1, curve=None):
    """a → b from frame f0 to f1 (smooth), held outside."""
    tb = table({0.0: 0.0, 0.25: 0.12, 0.5: 0.45, 0.75: 0.82, 1.0: 1.0})
    return lambda fr: a + (b - a) * tb(min(1.0, max(0.0, (fr - f0) / max(1e-6, f1 - f0))))


def big_black():
    """3: BIG / BLACK light up letter by letter (both lines at once); a white line runs under BIG and opens into
    the «Stylish» label."""
    D = 6.3
    t = _kit("big-black", "Título: BIG BLACK con etiqueta", "Title: BIG BLACK with a label", D, 8822,
             ["negro", "etiqueta"], thumb_at=3.0)
    s = Slide(t, D)
    s.background(BLACK)
    for text, ink, name in (("BIG", (709, 277, 1145, 453), "Título"), ("BLACK", (710, 538, 1585, 714), "Título 2")):
        s.letters(s.text(text, ink, "Montserrat", 900, WHITE, name), 0, 0.13, 0.3)
    wide_ = ease_in(0, 356, 38, 50)
    tall = ease_in(6, 73, 50, 58)
    s.box("Etiqueta", WHITE, lambda fr: (715, 458, 715 + wide_(fr), 458 + (tall(fr) if fr > 38 else 0)))
    lab = s.text("Stylish", (740, 470, 1000, 515), "Montserrat", 700, BLACK, "Etiqueta")
    s.fade(lab, ease_in(0, 1, 58, 66))
    return t


def montserrat_bold():
    """4: a black bar runs right and holds «Montserrat», a thin line under it runs on and opens down into the
    second bar; «BOLD» lightens in it."""
    D = 7.1
    t = _kit("montserrat-bold", "Título: dos barras negras con texto", "Title: two black bars with words", D, 8823,
             ["barras", "blanco"], thumb_at=3.5)
    s = Slide(t, D)
    s.background(WHITE)
    w1 = ease_in(0, 798, 0, 22)
    s.box("Barra", BLACK, lambda fr: (447, 315, 447 + w1(fr), 438))
    w2 = ease_in(0, 1122, 32, 42)
    h2 = ease_in(8, 261, 42, 52)
    s.box("Barra 2", BLACK, lambda fr: (444, 453, 444 + w2(fr), 453 + (h2(fr) if fr > 32 else 0)))
    rise = ease_in(110, 0, 38, 54)
    s.text("Montserrat", (480, 333, 1212, 420), "Montserrat", 800, WHITE, "Título",
           reveal=lambda fr: (447, 315, 1245, 438), shift=lambda fr: (0.0, rise(fr)))
    bold = s.text("BOLD", (500, 485, 1290, 682), "Montserrat", 700, WHITE, "Título 2")
    s.fade(bold, ease_in(0, 1, 56, 92))
    return t


def trend_line(s, dy=0, colour=WHITE, names=("Título", "Texto", "Texto 2")):
    """«trend» rising letter by letter, then «new / typography» beside it."""
    s.letters(s.text("trend", (405, 435 + dy, 1140, 630 + dy), "Kanit", 700, colour, names[0]), 0, 0.13, 0.35,
              "slide-up", distance=0.25)
    for text, ink, name, at in (("new", (1230, 478 + dy, 1362, 535 + dy), names[1], 34),
                                ("typography", (1225, 553 + dy, 1700, 605 + dy), names[2], 36)):
        s.letters(s.text(text, ink, "Montserrat", 400, colour, name, italic=True), at, 0.03, 0.25, "slide-up",
                  distance=0.3)


def trend():
    """5: «trend» rises letter by letter on black, «new typography» after it."""
    D = 5.4
    t = _kit("trend", "Título: trend new typography", "Title: trend new typography", D, 8824, ["negro"],
             thumb_at=2.7)
    s = Slide(t, D)
    s.background(BLACK)
    trend_line(s)
    return t


def hello_world():
    """6: «Hello World!» rises letter by letter, «// Minimal Typography» fades in under it."""
    D = 5.6
    t = _kit("hello-world", "Título: Hello World! en cursiva", "Title: Hello World! in italics", D, 8825,
             ["cursiva", "blanco"], thumb_at=2.8)
    s = Slide(t, D)
    s.background(WHITE)
    s.letters(s.text("Hello World!", (248, 461, 1671, 619), "Montserrat", 801, BLACK, "Título"), 4, 0.09, 0.3,
              "slide-up", distance=0.4)
    cap = s.text("// Minimal Typography", (543, 650, 1362, 708), "Montserrat", 400, BLACK, "Texto", italic=True)
    s.fade(cap, ease_in(0, 1, 30, 36))
    return t


def creative_emboss():
    """7: a white «creative» with a soft shadow on white, a smaller one inside it; the letters blur in one by
    one."""
    D = 5.3
    t = _kit("creative-relieve", "Título: creative en relieve", "Title: embossed creative", D, 8826,
             ["relieve", "sombra", "blanco"], thumb_at=2.6)
    s = Slide(t, D)
    s.background(WHITE)
    big = s.text("creative", (395, 470, 1530, 645), "Montserrat", 801, WHITE, "Título",
                 layers=[SHADOW, solid_fill(WHITE)])
    s.letters(big, 6, 0.1, 0.4, "fade")  # (blur-in lost the italics of this one)
    small = s.text("creative", (660, 512, 1232, 597), "Montserrat", 801, WHITE, "Título 2",
                   layers=[SHADOW, solid_fill(WHITE)])
    s.letters(small, 2, 0.05, 0.3, "blur-in")
    return t


def be_awesome():
    """8: a white panel slides in over the right of a photo and the stacked words flicker in."""
    D = 6.4
    t = _kit("be-awesome", "Título: Be awesome con foto", "Title: Be awesome with a photo", D, 8827,
             ["foto", "vertical"], thumb_at=3.2)
    s = Slide(t, D)
    t.photo(t.track("video", "Foto"), "portrait-01", 0.0, D, Box(0, 0, 1920, 1080), None, label="Tu foto")
    x0 = ease_in(1920, 1218, 10, 28)
    s.box("Panel", WHITE, lambda fr: (x0(fr), 0, 1920, 1080))
    words = [("BE", 1596, 84, 216, 36), ("AWE", 1419, 240, 378, 48), ("SOME", 1320, 396, 534, 42),
             ("BE", 1596, 555, 690, 54), ("CO", 1569, 714, 849, 40), ("OL", 1599, 876, 1011, 50)]
    for i, (text, x, y0, y1, at) in enumerate(words):
        w = s.text(text, (x, y0, 1830, y1), "Montserrat", 900, BLACK, "Título" if i == 0 else f"Título {i + 1}",
                   align="right")
        # Each word flickers in on its own: dim, bright, dim, on.
        s.fade(w, table({at - 1: 0.0, at: 0.35, at + 2: 0.1, at + 4: 0.6, at + 6: 0.3, at + 9: 1.0}))
    return t


def year():
    """9: a white «20» with a shadow and a black «22» rising digit by digit; «Year» beside it."""
    D = 5.1
    t = _kit("2022", "Título: año en relieve", "Title: embossed year", D, 8828, ["año", "relieve"], thumb_at=2.5)
    s = Slide(t, D)
    s.background(WHITE)
    # The black «22» is under the white «20» (its «0» covers the first «2»).
    b = s.text("22", (905, 420, 1215, 630), "Montserrat", 900, BLACK, "Título 2")
    s.letters(b, 16, 0.2, 0.3, "slide-up", distance=0.5)
    a = s.text("20", (635, 425, 975, 625), "Montserrat", 900, WHITE, "Título", layers=[SHADOW, solid_fill(WHITE)])
    s.fade(a, ease_in(0, 1, 2, 8))
    y = s.text("Year", (1220, 588, 1325, 625), "Montserrat", 700, WHITE, "Texto", layers=[SHADOW, solid_fill(WHITE)])
    s.fade(y, ease_in(0, 1, 32, 36))
    return t


def creative_pack():
    """10: «Creative / Pack» letters drop in from above in a random order."""
    D = 3.6
    t = _kit("creative-pack", "Título: letras que caen", "Title: falling letters", D, 8829, ["cursiva", "blanco"],
             thumb_at=1.8)
    s = Slide(t, D)
    s.background(WHITE)
    for text, ink, name in (("Creative", (306, 262, 1674, 492), "Título"), ("Pack", (528, 505, 1367, 720), "Título 2")):
        clip = s.text(text, ink, "Montserrat", 801, BLACK, name)
        s.letters(clip, 8, 0.05, 0.35, "slide-down", distance=0.6, order_in="random")
    return t


def new_york():
    """11: over a photo, a turned «NEW YORK CITY» and three small lines slide up into place."""
    D = 5.3
    t = _kit("ciudad", "Título: ciudad inclinado sobre foto", "Title: tilted city title over a photo", D, 8830,
             ["foto", "ciudad", "inclinado"], thumb_at=2.6)
    s = Slide(t, D)
    t.photo(t.track("video", "Foto"), "city-03", 0.0, D, Box(0, 0, 1920, 1080), None, label="Tu foto")
    title = s.text("NEW YORK CITY", (615, 352, 1485, 452), "Montserrat", 800, WHITE, "Título")
    s.turn(title, -13.4)
    s.letters(title, 6, 0.04, 0.3, "slide-up", distance=0.6)
    for i, (text, dy, x1) in enumerate((("US Post Office Museum", 0, 1180), ("NY November 21.2022", 52, 1120),
                                         ("New York", 104, 880))):
        line = s.text(text, (650, 470 + dy, x1, 510 + dy), "Montserrat", 500, WHITE, f"Texto {i + 1}",
                      align="left")
        s.turn(line, -13.4)
        s.letters(line, 12 + 3 * i, 0.03, 0.3, "slide-up", distance=0.6)
    return t


def circles():
    """12: six black circles grow from dots; «MADE WITH LOVE» types into the last; a caption bottom right."""
    D = 5.2
    t = _kit("circulos", "Título: seis círculos", "Title: six circles", D, 8831, ["círculos", "blanco"],
             thumb_at=2.6)
    s = Slide(t, D)
    s.background(WHITE)
    grow = ease_in(0.0, 1.0, 1, 18)
    for i, (cx, cy) in enumerate((x, y) for y in (216, 640) for x in (272, 702, 1132)):
        c = s.box(f"Círculo {i + 1}", BLACK, lambda fr, cx=cx, cy=cy: (cx - 196 * grow(fr), cy - 196 * grow(fr),
                                                                      cx + 196 * grow(fr), cy + 196 * grow(fr)))
        c["shapeStyle"]["kind"] = "ellipse"
    for text, ink, name, at in (("MADE", (996, 606, 1164, 642), "Título", 40),
                                ("WITH LOVE", (996, 652, 1305, 686), "Título 2", 44)):
        s.letters(s.text(text, ink, "Montserrat", 801, WHITE, name, align="left"), at, 0.04, 0.2)
    s.letters(s.text("trend  typography 1.0", (1295, 968, 1841, 1004), "Montserrat", 701, BLACK, "Texto",
                     italic=True, align="left"), 44, 0.03, 0.2)
    return t


def event_music():
    """13: on white, «EVENT / MUSIC» rises in; a photo comes down from the top over everything and over it the
    words are white."""
    D = 6.7
    t = _kit("event-music", "Título: evento con foto que baja", "Title: event title, a photo comes down", D, 8832,
             ["foto", "evento", "cursiva"], thumb_at=3.3)
    s = Slide(t, D)
    s.background(WHITE)
    from llt_motion import mask_track
    bottom = ease_in(0, 1080, 30, 56)
    ph = t.photo(t.track("video", "Foto"), "concert-01", 0.0, D, Box(0, 0, 1920, 1080), None, label="Tu foto")
    mask_track(t, ph, Box(0, 0, 1920, 1080), lambda u: (0, 0, 1920, max(0.5, bottom(s.frame(u)))), D)
    for text, ink, name, at in (("EVENT", (660, 435, 1296, 555), "Título", 2), ("MUSIC", (636, 560, 1230, 690),
                                                                               "Título 2", 4)):
        dark = s.text(text, ink, "Montserrat", 801, BLACK, name, reveal=lambda fr: (0, bottom(fr), 1920, 1080))
        s.letters(dark, at, 0.03, 0.3, "slide-up", distance=0.5)
        light = s.text(text, ink, "Montserrat", 801, WHITE, name + " (sobre la foto)",
                       reveal=lambda fr: (0, 0, 1920, max(0.5, bottom(fr))))
        s.letters(light, at, 0.03, 0.3, "slide-up", distance=0.5)
    return t


def new_typography():
    """14: two black bars run out, then «NEW» and «TYPOGRAPHY» rise in them in white."""
    D = 5.5
    t = _kit("new-typography", "Título: barras con texto en cursiva", "Title: bars with italic words", D, 8833,
             ["barras", "cursiva", "blanco"], thumb_at=2.7)
    s = Slide(t, D)
    s.background(WHITE)
    w1, w2 = ease_in(0, 477, 4, 22), ease_in(0, 913, 8, 28)
    s.box("Barra", BLACK, lambda fr: (583, 476, 583 + w1(fr), 568))
    s.box("Barra 2", BLACK, lambda fr: (584, 583, 584 + w2(fr), 675))
    rise = ease_in(100, 0, 34, 48)
    for text, ink, box, name in (("NEW", (605, 490, 800, 555), (583, 476, 1060, 568), "Título"),
                                 ("TYPOGRAPHY", (605, 597, 1470, 662), (584, 583, 1497, 675), "Título 2")):
        s.text(text, ink, "Montserrat", 801, WHITE, name, align="left", reveal=lambda fr, b=box: b,
               shift=lambda fr: (0.0, rise(fr)))
    return t


def trend_split():
    """15: the trend title twice, white on a black top half and black on a white bottom half."""
    D = 5.2
    t = _kit("trend-doble", "Título: trend en dos mitades", "Title: trend in two halves", D, 8834,
             ["negro", "blanco", "doble"], thumb_at=2.6)
    s = Slide(t, D)
    s.background(WHITE)
    s.box("Mitad", BLACK, lambda fr: (0, 0, 1920, 546))
    trend_line(s, dy=-270, colour=WHITE)
    trend_line(s, dy=255, colour=BLACK, names=("Título 2", "Texto 3", "Texto 4"))
    return t


def typo_slide():
    """16: a white card grows from a dot on black; «TYPO / NEW / SLIDE.» rises in it line by line."""
    D = 5.5
    t = _kit("typo-slide", "Título: tarjeta blanca", "Title: white card", D, 8835, ["tarjeta", "negro"],
             thumb_at=2.7)
    s = Slide(t, D)
    s.background(BLACK)
    k = ease_in(0.0, 1.0, 1, 22)
    cx, cy = 981, 576
    s.box("Tarjeta", WHITE, lambda fr: (cx - 210 * k(fr), cy - 252 * k(fr), cx + 210 * k(fr), cy + 252 * k(fr)))
    for i, (text, y0, y1) in enumerate((("TYPO", 369, 450), ("NEW", 474, 555), ("SLIDE.", 573, 654))):
        r = ease_in(90, 0, 34 + 4 * i, 46 + 4 * i)
        s.text(text, (801, y0, 801 + (273 if i == 0 else 231 if i == 1 else 309), y1), "Montserrat", 900, BLACK,
               "Título" if i == 0 else f"Título {i + 1}", align="left",
               reveal=lambda fr, a=y0, b=y1: (771, a - 6, 1191, b + 6), shift=lambda fr, r=r: (0.0, r(fr)))
    v = s.text("V.1", (1077, 762, 1131, 792), "Montserrat", 900, BLACK, "Texto", align="left")
    s.fade(v, ease_in(0, 1, 54, 58))
    return t


TEMPLATES = [creative_tilt, new_trend, big_black, montserrat_bold, trend, hello_world, creative_emboss, be_awesome,
             year, creative_pack, new_york, circles, event_music, new_typography, trend_split, typo_slide]
