"""Kit de YouTube, batch i (2026-10-30): Jorge's «pack youtube 6» (a commercial promo pack, 140 elements), done
almost the same as he asked but our own: the kit's coral instead of their red, no platform logos (generic icons
for the socials, a channel picture instead of the play logo), our fonts, every text and picture editable.
Prototypes first: the «Hello!» greeting that shrinks into a tag, box titles revealed line by line, and the coral
end screen with next/previous video. Order 8300-8399.
"""

from __future__ import annotations

import os

from kit import Box, centered, circle_photo, fill, keys, label, no_stroke, outline, photo_bg, pill, rrect, shadow, tanim, wide
from templates_ytkit_a import OUT, _stroke, path
from brand_logos import LOGOS

CORAL = "#FF4F64"
CORAL_DARK = "#E63E53"
WHITE = "#FFFFFF"
INK = "#101010"
FONT = "Montserrat"


def _kit(id, es, en, section, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _ellipse(cx, cy, rx, ry):
    k = 0.5523
    return (f"M {cx + rx} {cy} C {cx + rx} {cy + k * ry} {cx + k * rx} {cy + ry} {cx} {cy + ry} "
            f"C {cx - k * rx} {cy + ry} {cx - rx} {cy + k * ry} {cx - rx} {cy} "
            f"C {cx - rx} {cy - k * ry} {cx - k * rx} {cy - ry} {cx} {cy - ry} "
            f"C {cx + k * rx} {cy - ry} {cx + rx} {cy - k * ry} {cx + rx} {cy} Z")


# --- 1. ¡Hola! y bienvenidos -------------------------------------------------------------------------------------

def hola_bienvenidos():
    """A huge «¡HOLA!» pops in, then shrinks up into a coral tag in the middle; under it «Y BIENVENIDOS A / MI
    CANAL» comes in word by word. Over the user's video."""
    D = 6.0
    t = _kit("hola-bienvenidos", "¡Hola! y bienvenidos a mi canal", "Hello! and welcome to my channel", "frases",
             D, 8300, ["hola", "bienvenida", "saludo", "intro", "canal"], thumb_at=3.6)
    photo_bg(t, "h-city-05", s1=1.04, label="Tu video")
    land = 1.55
    out_at = D - 0.5
    tag = centered(960, 470, 560, 96)
    # The tag first (its track under the word): it stretches out from the middle as the word lands on it.
    t.solid(t.track("shape", "Etiqueta"), CORAL, land - 0.15, out_at - land + 0.15 + 0.3, tag,
            [(0, {"sx": 0.0}, "out"), (0.35, {}, "hold"), (out_at - land + 0.15, {}, "in"),
             (out_at - land + 0.45, {"sx": 0.0})])
    # One word: huge and high up, then down onto the tag at its size (the letters redrawn at each size, so they
    # stay sharp and whole), and it stays there.
    hola = label(t, t.track("text", "Hola"), "¡HOLA!", 0.25, out_at - 0.25, centered(960, 470, 1500, 330), FONT, 250,
                 WHITE, weight=900, anim_in=tanim("pop", duration=0.35), anim_out=OUT(0.2),
                 motion=[(0, {"dy": -150}, "hold"), (land - 0.25 - 0.4, {"dy": -150}, "inout"), (land - 0.25, {})],
                 layers=[shadow("#000000", 0, 6, 20, 0.35), fill(WHITE)], name="Hola")
    hola["textStyle"]["keyframes"] = {"pixelSize": keys([(0, 250, "hold"), (land - 0.25 - 0.4, 250, "inout"),
                                                          (land - 0.25, 66)])}
    for i, (text, name) in enumerate([("Y BIENVENIDOS A", "Línea 1"), ("MI CANAL", "Línea 2")]):
        a = land + 0.25 + i * 0.45
        label(t, t.track("text", "Textos"), text, a, out_at - a, Box(360, 530 + i * 82, 1200, 86), FONT, 66, WHITE,
              weight=800, anim_in=tanim("rise-by-word", duration=0.5), anim_out=OUT(0.25), name=name,
              layers=[shadow("#000000", 0, 4, 16, 0.4), fill(WHITE)])
    return t


# --- 2. Títulos en cajas --------------------------------------------------------------------------------------------

# Montserrat ExtraBold, from flip-addons next to this repo: measures a line so the cursor lands after it.
MONTSERRAT_800 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "flip-addons", "build",
                              "src", "fonts", "montserrat", "Montserrat-ExtraBold.ttf")


def _text_width(text, size):
    """The line's width in px at this size, measured with the font itself."""
    try:
        from PIL import ImageFont
        return ImageFont.truetype(MONTSERRAT_800, size).getlength(text)
    except Exception:
        return len(text) * size * 0.68


def _box_line(t, text, x, y, size, colour, box_colour, at, until, cursor=CORAL, name="Línea", align="left"):
    """One line in its own box, opened left to right as the pack does; then a coral block cursor blinks just after
    the last letter (never over them). It closes the same way."""
    box = Box(x, y, 1500, size * 1.6)
    reveal = min(0.8, 0.035 * len(text) + 0.2)
    # Room round the type (Jorge: «cuida los márgenes de los textos cuando van en una caja»).
    pad_x = size * 0.34
    c = label(t, t.track("text", "Títulos"), text, at, until - at, box, FONT, size, colour, weight=800, align=align,
              anim_in=tanim("wipe", duration=reveal, angle=0, softness=0.0),
              anim_out=tanim("wipe", duration=0.35, angle=180, softness=0.0),
              box_bg=(box_colour, 1.0), box_pad=pad_x, name=name)
    c["textStyle"]["boxStyle"] = "line"
    c["textStyle"]["boxPaddingX"] = pad_x
    c["textStyle"]["boxPaddingY"] = size * 0.16
    # The cursor: just past the box's right edge, blinking twice once the line is open.
    end_x = x + _text_width(text, size) + pad_x + size * 0.12
    dur = 1.0
    t.solid(t.track("shape", "Cursor"), cursor, at + reveal, dur, Box(end_x, y + size * 0.16, size * 0.3, size * 1.13),
            opacity=keys([(0, 1.0, "hold"), (0.25, 0.0, "hold"), (0.5, 1.0, "hold"), (0.75, 0.0, "hold"), (dur, 0.0)]))


def titulos_cajas():
    """Box titles: white boxes with black type, line by line, each revealed by a coral block cursor; then a
    second title in black boxes with white type. Over the user's video, lower left."""
    D = 7.0
    t = _kit("titulos-cajas", "Títulos en cajas", "Box titles", "titulos-estilo", D, 8301,
             ["cajas", "títulos", "máquina de escribir", "cursor", "subtítulo"], thumb_at=2.4)
    photo_bg(t, "h-travel-02", s1=1.04, label="Tu video")
    x = 150
    lines = [("TÍTULOS EN CAJAS", 74, "Línea 1"), ("PARA TU VIDEO", 74, "Línea 2")]
    for i, (text, size, name) in enumerate(lines):
        _box_line(t, text, x, 620 + i * 118, size, INK, WHITE, 0.3 + i * 0.35, 3.3 - (1 - i) * 0.1, name=name)
    second = [("ESCRIBE TU TEXTO", 64, "Línea 3"), ("FUNCIONA CON CUALQUIER FUENTE", 44, "Línea 4")]
    for i, (text, size, name) in enumerate(second):
        # Up in the bright sky: black boxes need a light picture behind them, as the pack places them.
        _box_line(t, text, x, 120 + i * 104, size, WHITE, INK, 3.6 + i * 0.35, D - 0.4 - (1 - i) * 0.1, cursor=CORAL,
                  name=name)
    return t


# --- 3. Pantalla final coral ---------------------------------------------------------------------------------------

def pantalla_final_coral():
    """Coral end screen with a faint pattern of rings: «Video siguiente» and «Video anterior» on the left (two
    slots for the user's videos), «¡GRACIAS POR VER!» typed on the right, three handles with generic icons, the
    channel's picture, «No olvides dar me gusta y comentar» and a white «SUSCRÍBETE»."""
    D = 10.0
    t = _kit("pantalla-final-roja", "Pantalla final coral con dos videos", "Coral end screen with two videos",
             "pantallas-finales", D, 8302, ["pantalla final", "gracias", "video siguiente", "redes", "suscríbete"],
             thumb_at=4.5)
    t.solid(t.track("shape", "Fondo"), CORAL, 0.0, D, None, [(0, {"s": 1.08}, "out"), (0.6, {})],
            opacity=keys([(0, 0.0), (0.3, 1.0)]))
    # The pattern: rings in a grid, drifting slowly.
    rings = []
    for row in range(6):
        for col in range(10):
            cx = (col * 220 + (110 if row % 2 else 0)) / 1920 * 100
            cy = (row * 200 + 40) / 1080 * 100
            rings.append(_ellipse(cx, cy, 70 / 1920 * 100, 70 / 1080 * 100))
            rings.append(_ellipse(cx, cy, 40 / 1920 * 100, 40 / 1080 * 100))
    path(t, t.track("shape", "Patrón"), WHITE, 0.0, D, Box(-60, -40, 2100, 1200), " ".join(rings),
         layers=[{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                 _stroke(WHITE, 10, "center", 0.08)],
         motion=[(0, {}, "linear"), (D, {"dx": -110})])
    # Left: the two videos with their labels.
    for i, (lab, name, sample) in enumerate([("VIDEO SIGUIENTE", "Video siguiente", "h-travel-02"),
                                             ("VIDEO ANTERIOR", "Video anterior", "h-nature-05")]):
        a = 0.45 + i * 0.25
        slot = Box(215, 140 + i * 470, 660, 372)
        rrect(t, t.track("shape", "Marcos"), WHITE, a, D - a, Box(slot.x - 8, slot.y - 8, slot.w + 16, slot.h + 16),
              radius=6, motion=[(0, {"dx": -900}, "out"), (0.55, {}, "hold"), (D - a - 0.4, {}, "in"), (D - a, {"dx": -900})],
              layers=[shadow("#000000", 0, 12, 30, 0.3), fill(WHITE), no_stroke()])
        t.photo(t.track("video", name), sample, a, D - a, slot,
                [(0, {"dx": -900}, "out"), (0.55, {}, "hold"), (D - a - 0.4, {}, "in"), (D - a, {"dx": -900})], label=name)
        label(t, t.track("text", "Textos"), lab, a + 0.45, D - a - 0.8, Box(slot.x, slot.y - 66, slot.w, 54), FONT, 34,
              WHITE, weight=800, spacing=1.5, anim_in=tanim("typewriter", duration=0.5), anim_out=OUT(0.25),
              name=f"Etiqueta: {name.lower()}")
    # Right: thanks, handles, picture, call to action.
    label(t, t.track("text", "Textos"), "¡GRACIAS\nPOR VER!", 0.9, D - 1.3, Box(1000, 150, 820, 250), FONT, 96, WHITE,
          weight=900, align="left", line=1.0, anim_in=tanim("typewriter", duration=0.8), anim_out=OUT(0.3),
          name="Gracias")
    # The platforms' official glyphs, in white beside the user's handles (their brand guidelines).
    socials = [(LOGOS["instagram"], "@tuusuario", "Usuario 1"), (LOGOS["facebook"], "/tupagina", "Usuario 2"),
               (LOGOS["x"], "@tuusuario", "Usuario 3")]
    for i, (icon, handle, name) in enumerate(socials):
        a = 1.6 + i * 0.18
        y = 470 + i * 92
        path(t, t.track("shape", "Iconos"), WHITE, a, D - a - 0.3, centered(1030, y + 30, 38, 38), icon, filled=True,
             motion=[(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (D - a - 0.6, {}, "in"), (D - a - 0.3, {"s": 0.0})])
        label(t, t.track("text", "Redes"), handle, a + 0.1, D - a - 0.5, Box(1075, y, 380, 60), FONT, 36, WHITE,
              weight=700, align="left", anim_in=tanim("slide-left", duration=0.35), anim_out=OUT(0.25), name=name)
    av = (1600, 540)
    t.solid(t.track("shape", "Aro"), WHITE, 1.4, D - 1.7, centered(av[0], av[1], 232, 232),
            [(0, {"s": 0.0}, "back"), (0.5, {}, "hold"), (D - 2.0, {}, "in"), (D - 1.7, {"s": 0.0})], kind="ellipse")
    circle_photo(t, "h-portrait-03", 1.45, D - 1.75, centered(av[0], av[1], 214, 214),
                 [(0, {"s": 0.0}, "back"), (0.5, {}, "hold"), (D - 2.05, {}, "in"), (D - 1.75, {"s": 0.0})],
                 label="Foto del canal")
    label(t, t.track("text", "Textos"), "NO OLVIDES DAR\nME GUSTA Y COMENTAR", 2.0, D - 2.4, Box(1340, 680, 520, 110),
          FONT, 34, WHITE, weight=800, line=1.1, anim_in=tanim("fade", duration=0.4), anim_out=OUT(0.25),
          name="Llamado")
    btn = centered(av[0], 840, 330, 74)
    pill(t, t.track("shape", "Botón"), WHITE, 2.3, D - 2.6, btn,
         [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (2.5, {}, "inout"), (2.65, {"s": 1.08}, "inout"), (2.8, {}, "hold"),
          (D - 2.9, {}, "in"), (D - 2.6, {"s": 0.0})],
         layers=[shadow("#000000", 0, 8, 20, 0.25), fill(WHITE), no_stroke()])
    label(t, t.track("text", "Botón"), "SUSCRÍBETE", 2.4, D - 2.8, btn, FONT, 38, CORAL, weight=900, spacing=1,
          anim_in=tanim("fade", duration=0.25), anim_out=OUT(0.2), name="Botón")
    return t


TEMPLATES = [hola_bienvenidos, titulos_cajas, pantalla_final_coral]
