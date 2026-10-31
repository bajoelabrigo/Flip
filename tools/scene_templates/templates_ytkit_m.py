"""Kit de YouTube, batch m (2026-10-30): the quotes and the call-out lines of Jorge's «pack youtube 6», almost the
same and our own (see templates_ytkit_i/j/k/l). Quotes: a white box with black quote-mark squares, an outlined
frame that draws itself, open corners, a free quote over the video, a coral panel and two bars that open. Call-outs:
a dot on the thing, a line that draws itself to the label, the label in a box (white, black or coral) with room
round the type. Our own sentences, never someone's famous quote. Order 8370-8399.
"""

from __future__ import annotations

import re

from kit import Box, centered, fill, keys, label, no_stroke, outline, photo_bg, shadow, tanim, wide
from templates_ytkit_a import OUT, path
from templates_ytkit_i import _text_width
from templates_ytkit_j import CORAL, INK, WHITE, _life
from templates_ytkit_k import _line_text, _wipe_box

FONT = "Montserrat"


def _kit(id, es, en, section, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


# --- Quote marks ------------------------------------------------------------------------------------------------------

def _mark(x0):
    """One heavy quote mark, «6» shaped, 45 wide in the 0..100 box."""
    return (f"M {x0} 62 Q {x0} 12 {x0 + 40} 0 L {x0 + 43} 13 Q {x0 + 21} 22 {x0 + 20} 44 "
            f"L {x0 + 45} 44 L {x0 + 45} 100 L {x0} 100 Z")


OPEN_QUOTE = _mark(0) + " " + _mark(55)
# The closing pair is the opening one turned half round.
CLOSE_QUOTE = re.sub(r"(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)",
                     lambda m: f"{100 - float(m.group(1)):g} {100 - float(m.group(2)):g}", OPEN_QUOTE)


def _quote(t, cx, cy, w, colour, t0, dur, closing=False, name="Comillas"):
    path(t, t.track("shape", name), colour, t0, dur, centered(cx, cy, w, w * 0.8), CLOSE_QUOTE if closing else OPEN_QUOTE,
         filled=True, motion=_life(dur))


def _quote_square(t, cx, cy, size, t0, dur, closing=False, bg=INK, fg=WHITE):
    """A square of colour with the quote mark inside it (the pack's black squares)."""
    t.solid(t.track("shape", "Comillas"), bg, t0, dur, centered(cx, cy, size, size), _life(dur))
    _quote(t, cx, cy, size * 0.52, fg, t0 + 0.05, dur - 0.05, closing)


def _lines_width(text, size):
    return max(_text_width(line, size) for line in text.split("\n"))


def _body(t, text, box, size, t0, dur, colour, align="left", anim="rise", name="Cita", line=1.15):
    return label(t, t.track("text", "Textos"), text, t0, dur, box, FONT, size, colour, weight=800, align=align,
                 anim_in=tanim(anim, duration=0.5), anim_out=OUT(0.25), name=name, line=line)


# --- Quotes -----------------------------------------------------------------------------------------------------------

def cita_caja_blanca():
    """A white box opens from the left; the quote in black inside, the author under it; black squares with white
    quote marks pop at the top-left and bottom-right corners."""
    D = 6.0
    t = _kit("cita-caja-blanca", "Cita en caja blanca", "Quote in a white box", "citas", D, 8370,
             ["cita", "frase", "caja", "autor"], thumb_at=3.0)
    photo_bg(t, "h-nature-06", s1=1.05, label="Tu video")
    text = "LO SIMPLE BIEN HECHO\nSIEMPRE SE RECUERDA.\nLO COMPLICADO SE OLVIDA."
    size, pad = 44, 56
    tw = _lines_width(text, size)
    th = 3 * size * 1.15
    box = Box(300, 360, tw + 2 * pad + 20, th + size * 1.2 + 2 * pad)
    _wipe_box(t, box.x, box.y, box.w, box.h, WHITE, 0.2, D - 0.4)
    _body(t, text, Box(box.x + pad, box.y + pad, tw + 20, th), size, 0.6, D - 1.0, INK)
    label(t, t.track("text", "Textos"), "Nombre del autor", 0.9, D - 1.3,
          Box(box.x + pad, box.y + pad + th + size * 0.3, tw, size * 0.9), FONT, 30, INK, weight=600, align="left",
          anim_in=tanim("fade", duration=0.4), anim_out=OUT(0.25), name="Autor")
    _quote_square(t, box.x, box.y, 84, 0.45, D - 0.85)
    _quote_square(t, box.x + box.w, box.y + box.h, 84, 0.55, D - 0.95, closing=True)
    return t


def cita_marco():
    """An outlined white frame draws itself round the quote; the open quote mark sits above its top-left corner,
    the closing one below the bottom-right, and the author in a white tag on the bottom edge."""
    D = 6.0
    t = _kit("cita-marco", "Cita en marco", "Quote in a frame", "citas", D, 8371,
             ["cita", "frase", "marco", "contorno"], thumb_at=3.0)
    photo_bg(t, "h-beach-03", s1=1.05, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.25)]))
    text = "CREAR NO ES TENER IDEAS:\nES TERMINARLAS\nY MOSTRARLAS."
    size, pad = 46, 60
    tw = _lines_width(text, size)
    th = 3 * size * 1.15
    frame = centered(960, 520, tw + 2 * pad + 20, th + 2 * pad + 30)
    path(t, t.track("shape", "Marco"), WHITE, 0.2, D - 0.4, frame, "M 0 0 L 100 0 L 100 100 L 0 100 Z", 6,
         draw=(0, 0.8), erase=(D - 0.4 - 0.5, 0.4))
    _body(t, text, Box(frame.x + pad, frame.y + pad, tw + 20, th), size, 0.7, D - 1.1, WHITE)
    _quote(t, frame.x + 10, frame.y - 46, 64, WHITE, 0.5, D - 0.9)
    _quote(t, frame.x + frame.w - 10, frame.y + frame.h + 58, 64, WHITE, 0.6, D - 1.0, closing=True)
    _line_text(t, "NOMBRE DEL AUTOR", Box(frame.x + 40, frame.y + frame.h - 26, 900, 52), 28, 1.0, D - 1.4,
               colour=INK, weight=800, anim="wipe", ad=0.4, name="Autor", box_bg=(WHITE, 1.0), pad=16, spacing=1)
    return t


def cita_esquinas():
    """Two open corners (top-left and bottom-right) slide in from the sides and frame the quote; small quote marks
    beside them and the author left under the text."""
    D = 6.0
    t = _kit("cita-esquinas", "Cita entre esquinas", "Quote between corners", "citas", D, 8372,
             ["cita", "frase", "esquinas", "líneas"], thumb_at=3.0)
    photo_bg(t, "h-beach-04", s1=1.05, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.3)]))
    text = "CADA ERROR ES UN PASO\nHACIA LO QUE QUIERES\nHACER BIEN."
    size = 48
    tw = _lines_width(text, size)
    th = 3 * size * 1.15
    frame = centered(960, 530, tw + 180, th + 170)
    corner = Box(frame.x, frame.y, frame.w * 0.55, frame.h * 0.62)
    path(t, t.track("shape", "Esquinas"), WHITE, 0.2, D - 0.4, corner, "M 100 0 L 0 0 L 0 100", 6,
         draw=(0, 0.6), erase=(D - 0.4 - 0.45, 0.35))
    corner2 = Box(frame.x + frame.w * 0.45, frame.y + frame.h * 0.38, frame.w * 0.55, frame.h * 0.62)
    path(t, t.track("shape", "Esquinas"), WHITE, 0.3, D - 0.5, corner2, "M 0 100 L 100 100 L 100 0", 6,
         draw=(0, 0.6), erase=(D - 0.5 - 0.45, 0.35))
    _body(t, text, centered(960, 515, tw + 40, th), size, 0.7, D - 1.1, WHITE, align="center")
    label(t, t.track("text", "Textos"), "NOMBRE DEL AUTOR", 1.0, D - 1.4, Box(frame.x + 90, frame.y + frame.h - 70, 600, 40),
          FONT, 26, WHITE, weight=800, align="left", spacing=1, anim_in=tanim("fade", duration=0.4), anim_out=OUT(0.25),
          name="Autor")
    _quote(t, frame.x - 10, frame.y - 40, 52, WHITE, 0.5, D - 0.9)
    _quote(t, frame.x + frame.w + 10, frame.y + frame.h + 40, 52, WHITE, 0.6, D - 1.0, closing=True)
    return t


def cita_libre():
    """The quote straight over the video, centred, with a soft shadow; big quote marks at its corners and the
    author in a small white box under it."""
    D = 6.0
    t = _kit("cita-libre", "Cita sobre el video", "Quote over the video", "citas", D, 8373,
             ["cita", "frase", "centrada", "autor"], thumb_at=3.0)
    photo_bg(t, "h-nature-02", s1=1.05, label="Tu video")
    text = "EL ESPACIO VACÍO TAMBIÉN HABLA:\nDEJA RESPIRAR TU IDEA."
    size = 56
    tw = _lines_width(text, size)
    label(t, t.track("text", "Textos"), text, 0.4, D - 0.8, centered(960, 500, tw + 60, 2 * size * 1.2), FONT, size,
          WHITE, weight=800, align="center", line=1.15, anim_in=tanim("rise", duration=0.6), anim_out=OUT(0.25),
          layers=[shadow("#000000", 0, 4, 18, 0.45), fill(WHITE)], name="Cita")
    _quote(t, 960 - tw / 2 - 75, 420, 70, WHITE, 0.3, D - 0.7)
    _quote(t, 960 + tw / 2 + 75, 600, 70, WHITE, 0.4, D - 0.8, closing=True)
    _line_text(t, "NOMBRE DEL AUTOR", Box(0, 640, 1920, 52), 30, 0.9, D - 1.3, colour=INK, weight=800, align="center",
               anim="fade", ad=0.4, name="Autor", box_bg=(WHITE, 1.0), pad=16, spacing=1)
    return t


def cita_coral():
    """A coral panel slides in over the left of the video with a big white quote mark; the quote and the author on
    it, the video still showing on the right."""
    D = 6.0
    t = _kit("cita-coral", "Cita en panel coral", "Quote on a coral panel", "citas", D, 8374,
             ["cita", "frase", "panel", "coral"], thumb_at=3.0)
    photo_bg(t, "h-nature-04", s1=1.05, label="Tu video")
    t.solid(t.track("shape", "Panel"), CORAL, 0.1, D - 0.2, Box(0, 0, 900, 1080),
            [(0, {"dx": -900}, "out"), (0.55, {}, "hold"), (D - 0.2 - 0.5, {}, "in"), (D - 0.2, {"dx": -900})],
            layers=[shadow("#000000", 8, 0, 40, 0.35), fill(CORAL), no_stroke()])
    _quote(t, 190, 330, 120, WHITE, 0.6, D - 1.0)
    _body(t, "HAZLO HOY.\nMAÑANA\nYA ES TARDE.", Box(130, 420, 700, 3 * 84 * 1.1), 84, 0.75, D - 1.15, WHITE, line=1.05)
    t.solid(t.track("shape", "Línea"), WHITE, 1.1, D - 1.5, Box(134, 730, 90, 8),
            [(0, {"sx": 0.0, "dx": -45}, "out"), (0.35, {})])
    label(t, t.track("text", "Textos"), "Nombre del autor", 1.2, D - 1.6, Box(130, 760, 700, 50), FONT, 34, WHITE,
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), anim_out=OUT(0.25), name="Autor")
    return t


def cita_barras():
    """Two white bars meet in the middle and slide apart; the quote grows between them, the author in coral below."""
    D = 6.0
    t = _kit("cita-barras", "Cita entre barras", "Quote between bars", "citas", D, 8375,
             ["cita", "frase", "barras", "centrada"], thumb_at=3.0)
    photo_bg(t, "h-beach-05", s1=1.05, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.3)]))
    text = "LA CONSTANCIA\nLE GANA AL TALENTO."
    size = 64
    tw = _lines_width(text, size)
    half = tw / 2 + 70
    for side in (-1, 1):
        t.solid(t.track("shape", "Barras"), WHITE, 0.2, D - 0.4, centered(960, 520, 10, 240),
                [(0, {"sy": 0.0}, "out"), (0.3, {}, "inout"), (0.8, {"dx": side * half}, "hold"),
                 (D - 0.4 - 0.7, {"dx": side * half}, "inout"), (D - 0.4 - 0.3, {}, "in"), (D - 0.4, {"sy": 0.0})])
    label(t, t.track("text", "Textos"), text, 1.0, D - 1.6, centered(960, 500, tw + 40, 2 * size * 1.15), FONT, size,
          WHITE, weight=800, align="center", line=1.1, anim_in=tanim("pop", duration=0.5), anim_out=OUT(0.25),
          name="Cita")
    _line_text(t, "NOMBRE DEL AUTOR", Box(0, 600, 1920, 50), 28, 1.3, D - 1.9, colour=WHITE, weight=800, align="center",
               anim="fade", ad=0.4, name="Autor", box_bg=(CORAL, 1.0), pad=14, spacing=1)
    return t


# --- Call-out lines ---------------------------------------------------------------------------------------------------

def _dot(t, cx, cy, t0, dur, colour=WHITE):
    """The point the line comes from: a ring with a dot inside, a soft shadow so it reads on light pictures."""
    t.solid(t.track("shape", "Punto"), colour, t0, dur, centered(cx, cy, 44, 44), _life(dur), kind="ellipse",
            layers=[shadow("#000000", 0, 2, 10, 0.4), {"id": "fill", "kind": "fill", "enabled": False,
                                                        "paint": {"kind": "solid", "color": "#00000000"}},
                    {"id": "stroke", "kind": "stroke", "enabled": True, "width": 5, "strokeAlign": "inside",
                     "paint": {"kind": "solid", "color": colour}, "opacity": 1.0}])
    t.solid(t.track("shape", "Punto"), colour, t0 + 0.05, dur - 0.05, centered(cx, cy, 16, 16), _life(dur - 0.05),
            kind="ellipse")


def _leader(t, pts, t0, dur, colour=WHITE, width=4, at=0.15, ln=0.45, name="Línea"):
    """A line through the points (screen px) that draws itself from the first one and, at the end, rubs out from
    it. The box gets a margin so a straight line never has a zero side."""
    m = width * 3
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    box = Box(min(xs) - m, min(ys) - m, max(xs) - min(xs) + 2 * m, max(ys) - min(ys) + 2 * m)
    d = "M " + " L ".join(f"{(x - box.x) / box.w * 100:.3f} {(y - box.y) / box.h * 100:.3f}" for x, y in pts)
    path(t, t.track("shape", name), colour, t0, dur, box, d, width, draw=(at, ln), erase=(dur - 0.45, 0.35),
         layers=[shadow("#000000", 0, 2, 8, 0.35), {"id": "fill", "kind": "fill", "enabled": False,
                                                     "paint": {"kind": "solid", "color": "#00000000"}},
                 {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
                  "paint": {"kind": "solid", "color": colour}, "opacity": 1.0}])


def _tag(t, text, x, y, size, t0, dur, fg=INK, bg=WHITE, align="left", name=None, spacing=1, weight=800):
    """A label in its own box, opened left to right, with room round the type. For align="right", x is the
    box's right edge; for "left", its left edge."""
    pad = size * 0.4
    w = _lines_width(text, size)
    left = x + pad if align == "left" else x - pad - 1600
    return _line_text(t, text, Box(left, y, 1600, size * 1.6), size, t0, dur, colour=fg, weight=weight, align=align,
                      anim="wipe", ad=min(0.6, 0.2 + 0.03 * len(text)), name=name or text, box_bg=(bg, 1.0), pad=pad,
                      spacing=spacing), w + 2 * pad


def _plain(t, text, box, size, t0, dur, colour=WHITE, align="left", name=None, weight=800, line=1.15):
    return label(t, t.track("text", "Textos"), text, t0, dur, box, FONT, size, colour, weight=weight, align=align,
                 line=line, anim_in=tanim("fade", duration=0.4), anim_out=OUT(0.25), name=name or text,
                 layers=[shadow("#000000", 0, 2, 10, 0.5), fill(colour)])


def llamada_contorno():
    """A dot on the thing, a line up to an elbow and along; the label over the line, right-aligned, white with a
    shadow (the pack's «outline» call-out)."""
    D = 5.0
    t = _kit("llamada-contorno", "Llamada con línea", "Call-out line", "llamadas", D, 8380,
             ["llamada", "línea", "señalar", "punto"], thumb_at=2.5)
    photo_bg(t, "h-interior-02", s1=1.03, label="Tu video")
    _dot(t, 1060, 500, 0.2, D - 0.4)
    _leader(t, [(1060, 500), (900, 330), (560, 330)], 0.3, D - 0.6)
    _plain(t, "LLAMADA\nCON LÍNEA", Box(500, 214, 380, 2 * 44 * 1.15), 44, 0.8, D - 1.2, align="right", name="Título")
    return t


def llamada_etiqueta():
    """The line runs up and left from the dot to a coral label, a smaller white one under it."""
    D = 5.0
    t = _kit("llamada-etiqueta", "Llamada con etiqueta coral", "Call-out with a coral label", "llamadas", D, 8381,
             ["llamada", "etiqueta", "coral", "línea"], thumb_at=2.5)
    photo_bg(t, "h-food-01", s1=1.03, label="Tu video")
    _dot(t, 840, 680, 0.2, D - 0.4)
    _leader(t, [(840, 680), (700, 420), (560, 420)], 0.3, D - 0.6)
    _tag(t, "TEXTO PRINCIPAL", 560, 350, 40, 0.75, D - 1.15, fg=WHITE, bg=CORAL, align="right", name="Título")
    _tag(t, "segunda línea", 560, 432, 28, 0.95, D - 1.35, fg=INK, bg=WHITE, align="right", name="Subtítulo", spacing=0)
    return t


def llamada_vertical():
    """A coral line drops from the dot; beside it the title in coral and two lines of description in white."""
    D = 5.0
    t = _kit("llamada-vertical", "Llamada con línea vertical", "Call-out with a vertical line", "llamadas", D, 8382,
             ["llamada", "vertical", "descripción", "coral"], thumb_at=2.5)
    photo_bg(t, "h-travel-03", s1=1.03, label="Tu video")
    _dot(t, 1120, 900, 0.2, D - 0.4)
    _leader(t, [(1120, 900), (1120, 760), (1260, 620)], 0.3, D - 0.6, colour=CORAL, width=6)
    t.solid(t.track("shape", "Barra"), CORAL, 0.7, D - 1.1, Box(1290, 560, 8, 170),
            [(0, {"sy": 0.0, "dy": -85}, "out"), (0.35, {}, "hold"), (D - 1.1 - 0.3, {}, "in"), (D - 1.1, {"sy": 0.0})])
    _plain(t, "TÍTULO DE LA LLAMADA", Box(1320, 560, 600, 56), 40, 0.85, D - 1.25, colour=CORAL, name="Título")
    _plain(t, "Escribe aquí una descripción corta\nde lo que quieres mostrar.", Box(1320, 625, 600, 2 * 28 * 1.3), 28,
           1.05, D - 1.45, weight=600, line=1.3, name="Descripción")
    return t


def llamada_marca_precio():
    """The dot on the product, the line up and right to an outlined box with the brand's name, the price in a
    coral tag under it."""
    D = 5.0
    t = _kit("llamada-marca-precio", "Llamada con marca y precio", "Call-out with brand and price", "llamadas", D, 8383,
             ["llamada", "precio", "marca", "producto"], thumb_at=2.5)
    photo_bg(t, "h-food-02", s1=1.03, label="Tu video")
    _dot(t, 1020, 840, 0.2, D - 0.4)
    _leader(t, [(1020, 840), (1200, 640), (1360, 640)], 0.3, D - 0.6)
    size = 38
    w = _text_width("NOMBRE DE MARCA", size) + size * 1.2
    box = Box(1360, 610, w, size * 1.7)
    outline(t, t.track("shape", "Marco"), WHITE, 5, 0.75, D - 1.15, box,
            [(0, {"sx": 0.0, "dx": -w / 2}, "out"), (0.35, {}, "hold"), (D - 1.15 - 0.3, {}, "in"), (D - 1.15, {"sx": 0.0})])
    _plain(t, "NOMBRE DE MARCA", box, size, 0.9, D - 1.3, align="center", name="Marca")
    _tag(t, "$39", 1360, box.y + box.h + 10, 36, 1.05, D - 1.45, fg=WHITE, bg=CORAL, name="Precio")
    return t


def llamada_caja_coral():
    """From the dot the line goes down and right to a coral box with two lines of white text."""
    D = 5.0
    t = _kit("llamada-caja-coral", "Llamada en caja coral", "Call-out in a coral box", "llamadas", D, 8384,
             ["llamada", "caja", "coral", "línea"], thumb_at=2.5)
    photo_bg(t, "h-interior-03", s1=1.03, label="Tu video")
    _dot(t, 880, 290, 0.2, D - 0.4)
    _leader(t, [(880, 290), (1080, 560)], 0.3, D - 0.6, colour=CORAL, width=6)
    _tag(t, "LLAMADAS PARA\nTUS VIDEOS", 1080, 540, 44, 0.75, D - 1.15, fg=WHITE, bg=CORAL, name="Título")
    return t


def llamada_describe():
    """The dot on the person's hands, the line up and right to an outlined box: a three-line title and a short
    description under it."""
    D = 5.5
    t = _kit("llamada-describe", "Describe tu producto", "Describe your product", "llamadas", D, 8385,
             ["llamada", "producto", "descripción", "marco"], thumb_at=2.8)
    photo_bg(t, "h-office-01", s1=1.03, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.4, 0.2)]))
    _dot(t, 760, 640, 0.2, D - 0.4)
    _leader(t, [(760, 640), (960, 420), (1060, 420)], 0.3, D - 0.6)
    box = Box(1060, 220, 440, 380)
    t.solid(t.track("shape", "Fondo del marco"), "#000000", 0.7, D - 1.1, box,
            [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (D - 1.1 - 0.3, {}, "in"), (D - 1.1, {"s": 0.0})], alpha=0.35)
    outline(t, t.track("shape", "Marco"), WHITE, 5, 0.7, D - 1.1, box,
            [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (D - 1.1 - 0.3, {}, "in"), (D - 1.1, {"s": 0.0})])
    _plain(t, "DESCRIBE\nTU\nPRODUCTO", Box(box.x + 40, box.y + 36, box.w - 80, 3 * 50 * 1.05), 50, 0.95, D - 1.35,
           line=1.05, name="Título")
    _plain(t, "Escribe aquí lo que hace\nespecial a tu producto\ny por qué lo necesitan.",
           Box(box.x + 40, box.y + 36 + 3 * 50 * 1.05 + 20, box.w - 80, 3 * 26 * 1.3), 26, 1.15, D - 1.55, weight=600,
           line=1.3, name="Descripción")
    return t


def llamada_titular():
    """A coral headline tag and a black one under it, with a short line down to the dot."""
    D = 5.0
    t = _kit("llamada-titular", "Titular y descripción", "Headline and description", "llamadas", D, 8386,
             ["llamada", "titular", "negro", "coral"], thumb_at=2.5)
    photo_bg(t, "h-podcast-01", s1=1.03, label="Tu video")
    _dot(t, 1560, 450, 0.2, D - 0.4)
    _leader(t, [(1560, 450), (1460, 300)], 0.3, D - 0.6)
    _tag(t, "TITULAR", 1180, 180, 40, 0.65, D - 1.05, fg=WHITE, bg=CORAL, name="Titular")
    _tag(t, "DESCRIBE AQUÍ", 1180, 252, 40, 0.85, D - 1.25, fg=WHITE, bg=INK, name="Descripción")
    return t


def llamada_negra():
    """A small white headline over a black box; a line goes straight down from the box to the dot."""
    D = 5.0
    t = _kit("llamada-negra", "Llamada en caja negra", "Call-out in a black box", "llamadas", D, 8387,
             ["llamada", "negro", "vertical", "titular"], thumb_at=2.5)
    photo_bg(t, "h-office-03", s1=1.03, label="Tu video")
    _dot(t, 1040, 720, 0.2, D - 0.4)
    _leader(t, [(1040, 720), (1040, 520)], 0.3, D - 0.6)
    w = _text_width("LÍNEA DE LLAMADA", 40) + 40 * 0.8
    _plain(t, "TITULAR", Box(1040 - w / 2, 380, w, 40), 28, 0.9, D - 1.3, align="center", name="Titular")
    _tag(t, "LÍNEA DE LLAMADA", 1040 - w / 2, 425, 40, 0.7, D - 1.1, fg=WHITE, bg=INK, name="Título")
    return t


def llamada_creativa():
    """A small coral word on top of a white box with the call-out in black; the line from its corner to the dot."""
    D = 5.0
    t = _kit("llamada-creativa", "Llamada creativa", "Creative call-out", "llamadas", D, 8388,
             ["llamada", "creativa", "blanco", "coral"], thumb_at=2.5)
    photo_bg(t, "h-interior-05", s1=1.03, label="Tu video")
    _dot(t, 260, 980, 0.2, D - 0.4)
    _leader(t, [(260, 980), (420, 800), (520, 800)], 0.3, D - 0.6)
    _tag(t, "CREATIVA", 540, 690, 30, 0.7, D - 1.1, fg=WHITE, bg=CORAL, name="Titular")
    _tag(t, "LÍNEAS DE LLAMADA.", 540, 742, 42, 0.85, D - 1.25, fg=INK, bg=WHITE, name="Título")
    return t


def llamada_parrafo():
    """The line runs right from the dot to a long rule; the title sits over it and a coral box with a short
    paragraph hangs under it."""
    D = 5.5
    t = _kit("llamada-parrafo", "Llamada con párrafo", "Call-out with a paragraph", "llamadas", D, 8389,
             ["llamada", "párrafo", "descripción", "coral"], thumb_at=2.8)
    photo_bg(t, "h-interior-04", s1=1.03, label="Tu video")
    _dot(t, 1160, 860, 0.2, D - 0.4)
    _leader(t, [(1160, 860), (1300, 700), (1800, 700)], 0.3, D - 0.6)
    _plain(t, "ESCRIBE TU TEXTO", Box(1310, 640, 490, 50), 36, 0.8, D - 1.2, name="Título")
    para = Box(1310, 718, 490, 4 * 25 * 1.3 + 40)
    t.solid(t.track("shape", "Caja"), CORAL, 0.9, D - 1.3, para,
            [(0, {"sy": 0.0, "dy": -para.h / 2}, "out"), (0.35, {}, "hold"), (D - 1.3 - 0.3, {}, "in"),
             (D - 1.3, {"sy": 0.0, "dy": -para.h / 2})])
    _plain(t, "Cuenta aquí en pocas palabras\nlo que se ve en esta parte\nde tu video: el lugar, la cosa\no el momento.",
           Box(para.x + 22, para.y + 20, para.w - 44, para.h - 40), 25, 1.1, D - 1.5, weight=600, line=1.3,
           name="Párrafo")
    return t


TEMPLATES = [cita_caja_blanca, cita_marco, cita_esquinas, cita_libre, cita_coral, cita_barras,
             llamada_contorno, llamada_etiqueta, llamada_vertical, llamada_marca_precio, llamada_caja_coral,
             llamada_describe, llamada_titular, llamada_negra, llamada_creativa, llamada_parrafo]
