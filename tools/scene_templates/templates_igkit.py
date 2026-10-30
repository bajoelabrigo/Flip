"""Kit de Instagram (2026-10-30): stories 9:16. Jorge brought a commercial pack of fifty stories (event posters
with torn paint over a photo, sale posters with rings and shards, kinetic type on dark, photo grids...). These
are our own takes on those kinds of stories: our shapes instead of their paint videos, the kit's palette, every
text and photo editable. Prototypes first (three very different ones) for Jorge to pick the direction.
Category igkit; order 9000-9199; ids `igk-*`; the section in the first tag (`kit:<section>`).
"""

from __future__ import annotations

from kit import (Box, centered, fill, keys, label, no_stroke, outline, photo_bg, pill, rrect, shade_full, shadow,
                 tall, tanim)
from templates_c1 import count_fn
from scene import text_style

NAVY = "#0B1A2E"
DEEP = "#070F1D"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MINT = "#D3F3EE"

W, H = 1080, 1920
OUT = lambda d=0.3: tanim("fade", duration=d)  # noqa: E731


def _ig(id, es, en, dur, order, section, tags, **kw):
    return tall(f"igk-{id}", es, en, "igkit", dur, order=order,
                tags=[f"kit:{section}", "instagram", "historia", "story"] + tags, **kw)


def _custom(t, track, colour, t0, dur, box, d, motion=None, **extra):
    c = t.solid(track, colour, t0, dur, box, motion, kind="custom", layers=[fill(colour), no_stroke()], **extra)
    c["shapeStyle"]["customPath"] = d
    return c


def _bar(t, colour, t0, dur, box, angle=-8.0, out_at=None, name="Trazos"):
    """A slanted slab that shoots in from the left and leaves to the right: the stroke under a line of type."""
    out_at = dur - 0.45 if out_at is None else out_at
    m = [(0, {"sx": 0.0, "dx": -box.w / 2}, "out"), (0.4, {}, "hold"), (out_at, {}, "in"),
         (out_at + 0.35, {"sx": 0.0, "dx": box.w / 2})]
    return t.solid(t.track("shape", name), colour, t0, out_at + 0.35, box, m, rotation=keys([(0, angle)]))


# --- 1. Póster de evento -----------------------------------------------------------------------------------------------

TORN = ("M 0 8 L 14 0 L 26 10 L 41 2 L 55 12 L 70 3 L 84 11 L 100 4 L 100 92 L 86 100 L 72 90 L 58 98 L 44 88 "
        "L 30 97 L 16 89 L 0 96 Z")


def evento():
    """The photo full, darkened; a torn teal strip tears in across the middle, slanted coral strokes shoot under
    the day, the city and the venue, which slide in one after another; a hashtag on top, «more info» below."""
    D = 7.0
    t = _ig("evento-poster", "Póster de evento", "Event poster", D, 9000, "eventos",
            ["evento", "fecha", "póster", "concierto", "fiesta"], thumb_at=3.2)
    photo_bg(t, "concert-02", s1=1.12, label="Tu foto o video")
    shade_full(t, 0.38)
    strip = Box(-40, 700, W + 80, 560)
    _custom(t, t.track("shape", "Franja"), TEAL, 0.25, D - 0.25, strip, TORN,
            [(0, {"dx": -W - 120}, "out"), (0.55, {}, "hold"), (D - 0.25 - 0.6, {}, "in"), (D - 0.25, {"dx": W + 120})],
            rotation=keys([(0, -6.0)]), opacity=keys([(0, 0.92)]))
    lines = [("SÁBADO 14", "Barlow Condensed", 120, NAVY, Box(110, 760, 860, 140), CORAL, "Fecha"),
             ("TU CIUDAD", "Anton", 210, WHITE, Box(90, 880, 900, 240), NAVY, "Ciudad"),
             ("Nombre del lugar · 21:00", "Barlow Condensed", 64, NAVY, Box(120, 1120, 840, 90), SUN, "Lugar")]
    for i, (text, font, size, colour, box, under, name) in enumerate(lines):
        a = 0.7 + i * 0.25
        out = D - 0.5 - (2 - i) * 0.1
        _bar(t, under, a - 0.05, out - a + 0.05, Box(box.x - 20, box.y + box.h * 0.55, box.w * 0.62, box.h * 0.32),
             out_at=out - a - 0.3)
        label(t, t.track("text", "Textos"), text, a, out - a, box, font, size, colour, weight=900, italic=True,
              align="left", anim_in=tanim("slide-right", duration=0.45), anim_out=OUT(0.25), name=name)
    label(t, t.track("text", "Textos"), "#TuEvento", 0.4, D - 0.8, Box(90, 230, 700, 80), "Barlow Condensed", 56,
          WHITE, weight=700, italic=True, align="left", anim_in=tanim("typewriter", duration=0.6), anim_out=OUT(0.25),
          name="Etiqueta")
    pill(t, t.track("shape", "Botón"), WHITE, 1.6, D - 2.1, centered(W / 2, 1640, 520, 92),
         [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (D - 2.1 - 0.3, {}, "in"), (D - 2.1, {"s": 0.0})])
    label(t, t.track("text", "Botón"), "MÁS INFO EN EL ENLACE", 1.75, D - 2.3, centered(W / 2, 1640, 520, 92), "Barlow Condensed",
          40, NAVY, weight=800, spacing=2, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Botón")
    return t


# --- 2. Rebajas ------------------------------------------------------------------------------------------------------

def rebajas():
    """A pale mint story with big rings turning off the corner and coral shards flying across; «SUPER REBAJA»
    stamps in, the percentage counts up to 50 and lands with a pop, «Solo por tiempo limitado» and a button."""
    D = 6.5
    t = _ig("rebajas-super", "Súper rebaja", "Super sale", D, 9001, "rebajas",
            ["rebajas", "oferta", "descuento", "venta", "tienda"], thumb_at=3.6)
    t.solid(t.track("shape", "Fondo"), MINT)
    # Rings off the top right corner, drawing outwards one after another and turning slowly.
    for i in range(6):
        d = 380 + i * 230
        outline(t, t.track("shape", "Anillos"), TEAL, 38, 0.05 * i, D - 0.05 * i, centered(W - 60, 520, d, d),
                [(0, {"s": 0.6}, "out"), (0.8, {}, "linear"), (D - 0.05 * i, {"s": 1.08})], kind="ellipse",
                alpha=0.55, opacity=keys([(0, 0.0), (0.4, 1.0)]))
    # Shards: thin slanted slabs crossing the story.
    shards = [(CORAL, Box(-200, 330, 760, 34), -28, 0.3), (SUN, Box(560, 1470, 700, 26), -28, 0.5),
              (NAVY, Box(-160, 1660, 520, 20), -28, 0.65), (CORAL, Box(700, 120, 520, 22), -28, 0.8)]
    for colour, box, angle, at in shards:
        t.solid(t.track("shape", "Destellos"), colour, at, D - at,
                box, [(0, {"dx": -900, "dy": 480}, "out"), (0.5, {}, "linear"), (D - at - 0.4, {"dx": 60, "dy": -32}, "in"),
                      (D - at, {"dx": 1200, "dy": -640})], rotation=keys([(0, angle)]))
    a = 0.6
    label(t, t.track("text", "Textos"), "SUPER", a, D - a - 0.35, Box(90, 560, 900, 220), "Barlow Condensed", 230,
          CORAL, weight=900, italic=True, align="left", anim_in=tanim("stamp", duration=0.4), anim_out=OUT(0.25),
          name="Título 1")
    label(t, t.track("text", "Textos"), "REBAJA", a + 0.2, D - a - 0.55, Box(90, 760, 900, 220), "Barlow Condensed", 230,
          CORAL, weight=900, italic=True, align="left", anim_in=tanim("stamp", duration=0.4), anim_out=OUT(0.25),
          name="Título 2")
    label(t, t.track("text", "Textos"), "Solo por tiempo limitado", a + 0.6, D - a - 0.9, Box(100, 1000, 880, 90),
          "Barlow Condensed", 66, NAVY, weight=700, italic=True, align="left",
          anim_in=tanim("typewriter", duration=0.7), anim_out=OUT(0.25), name="Subtítulo")
    # The percentage counts up with the engine's counter and lands with a pop.
    pct_box = Box(380, 1130, 640, 330)

    def pct_style():
        return text_style("Barlow Condensed", 300, [fill(NAVY)], weight=900, italic=True, align="right",
                          anim_out=OUT(0.25))
    count_fn(t, t.track("text", "Descuento"), lambda f: 0.0, lambda v: f"{int(v)}%", 1.4, 1.2, "50%", pct_box,
             pct_style, end=D - 0.35, name="Descuento")
    label(t, t.track("text", "Textos"), "DE DESCUENTO", 1.9, D - 2.3, Box(380, 1420, 600, 70), "Barlow Condensed", 54,
          CORAL, weight=800, italic=True, align="right", spacing=3, anim_in=tanim("fade", duration=0.3),
          anim_out=OUT(0.2), name="Debajo del descuento")
    btn = centered(W / 2, 1700, 480, 100)
    pill(t, t.track("shape", "Botón"), NAVY, 2.4, D - 2.75, btn,
         [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (D - 2.75 - 0.3, {}, "in"), (D - 2.75, {"s": 0.0})])
    label(t, t.track("text", "Botón"), "COMPRAR AHORA", 2.55, D - 2.95, btn, "Barlow Condensed", 46, WHITE, weight=800,
          spacing=2, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Botón")
    return t


# --- 3. Texto cinético ----------------------------------------------------------------------------------------------

def cinetico():
    """Kinetic type on dark: three beats of words that pop and stamp («¿TE GUSTA?», «HAZLO AHORA», «50 IDEAS PARA
    EMPEZAR»), glitch bars flashing between them, and at the end the photo opens through strips that slide away
    up and down alternately, with the last line on it."""
    D = 8.0
    t = _ig("texto-cinetico", "Texto cinético con foto", "Kinetic type with photo", D, 9002, "texto",
            ["texto", "cinético", "tipografía", "frases", "glitch"], thumb_at=6.6)
    reveal = 5.0
    t.photo(t.track("video", "Tu foto o video"), "fashion-03", 0.0, D, None,
            [(0, {"s": 1.18}, "hold"), (reveal, {"s": 1.18}, "out"), (D, {"s": 1.0})], label="Tu foto o video")
    # The dark cover: seven strips that slide away up and down, alternately, from the middle out.
    n = 7
    sw = W / n
    order = [3, 2, 4, 1, 5, 0, 6]
    for i in range(n):
        at = reveal + order.index(i) * 0.06
        dy = -H if i % 2 == 0 else H
        t.solid(t.track("shape", "Cortina"), DEEP, 0.0, at + 0.6, Box(i * sw - 1, 0, sw + 2, H),
                [(0, {}, "hold"), (at, {}, "in"), (at + 0.6, {"dy": dy})])

    def beat(a, b, lines):
        for j, (text, font, size, colour, box, anim, name) in enumerate(lines):
            label(t, t.track("text", "Frases"), text, a + j * 0.12, b - a - j * 0.12, box, font, size, colour,
                  weight=900, italic=True, anim_in=anim, anim_out=tanim("fade", duration=0.12), name=name)

    beat(0.3, 1.9, [("¿TE", "Barlow Condensed", 150, WHITE, Box(140, 760, 360, 180), tanim("pop", duration=0.3), "Frase 1a"),
                    ("GUSTA?", "Barlow Condensed", 230, CORAL, Box(140, 900, 800, 260), tanim("stamp", duration=0.35),
                     "Frase 1b")])
    beat(2.0, 3.5, [("HAZLO", "Anton", 220, WHITE, Box(80, 700, 920, 260), tanim("stamp", duration=0.3), "Frase 2a"),
                    ("AHORA", "Anton", 260, TEAL, Box(80, 940, 920, 300), tanim("stamp", duration=0.3), "Frase 2b")])
    beat(3.6, 5.1, [("50", "Barlow Condensed", 300, CORAL, Box(90, 720, 360, 330), tanim("pop", duration=0.3), "Frase 3a"),
                    ("IDEAS PARA", "Barlow Condensed", 110, WHITE, Box(430, 760, 600, 130), tanim("slide-left", duration=0.3),
                     "Frase 3b"),
                    ("EMPEZAR", "Barlow Condensed", 170, SUN, Box(90, 1040, 900, 200), tanim("slide-up", duration=0.3),
                     "Frase 3c")])
    # Glitch bars between the beats.
    for at in (1.85, 3.45, 4.95):
        for k, (y, h, c, dx) in enumerate([(820, 60, TEAL, -60), (960, 24, CORAL, 90), (1100, 40, WHITE, -30)]):
            t.solid(t.track("shape", "Glitch"), c, at + k * 0.02, 0.16, Box(0, y, W, h),
                    [(0, {"dx": dx}, "linear"), (0.16, {"dx": -dx})], opacity=keys([(0, 0.85)]))
    # The last line, on the photo.
    label(t, t.track("text", "Frases"), "@tucuenta", reveal + 0.6, D - reveal - 0.9, Box(90, 1560, 900, 90),
          "Barlow Condensed", 64, WHITE, weight=800, italic=True, align="left",
          anim_in=tanim("typewriter", duration=0.5), anim_out=OUT(0.25), name="Cuenta",
          layers=[shadow("#000000", 0, 4, 14, 0.6), fill(WHITE)])
    t.solid(t.track("shape", "Trazos"), CORAL, reveal + 0.5, D - reveal - 0.8, Box(90, 1650, 260, 14),
            [(0, {"sx": 0.0, "dx": -130}, "out"), (0.4, {}, "hold"), (D - reveal - 1.1, {}, "in"), (D - reveal - 0.8, {"sx": 0.0})])
    return t


TEMPLATES = [evento, rebajas, cinetico]
