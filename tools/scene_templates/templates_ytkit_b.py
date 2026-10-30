"""Kit de YouTube, batch b (2026-10-30): Tipografía (typographic title blocks, order 7200-7249) and Títulos con
estilo (styled titles over the user's photo or video, order 7300-7349). Same palette, fonts and rules as the
approved prototypes in templates_ytkit.py (see BRIEF-ytkit.md): a text born from a line or bar is revealed with a
wipe from that line and never crosses it; every text editable; the background is its own track.
"""

from __future__ import annotations

from kit import (Box, bg, bg_gradient, centered, fill, gradient, hollow, keys, label, no_stroke, outline, photo_bg,
                 pill, rrect, shade_full, shadow, stroke, tall, tanim, wide)

NAVY = "#0B1A2E"
DEEP = "#06101F"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MIST = "#A9B8CC"
PAPER = "#F4F7FB"


def _kit(id, es, en, section, duration, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", duration, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _kit_tall(id, es, en, section, duration, order, tags, **kw):
    return tall(f"ytk-{id}", es, en, "ytkit", duration, order=order,
                tags=[f"kit:{section}", "youtube", "vertical"] + tags, **kw)


def wipe(angle=0, duration=0.6, softness=0.15):
    return tanim("wipe", duration=duration, angle=angle, softness=softness)


def fade(duration=0.35):
    return tanim("fade", duration=duration)


def outlined(colour, width=4):
    """Letters drawn only by their outline."""
    return [hollow(), stroke(width, colour)]


_START = {
    "x": lambda b: {"sx": 0.0, "dx": -b.w / 2},   # draws from its left edge
    "xr": lambda b: {"sx": 0.0, "dx": b.w / 2},   # from its right edge
    "y": lambda b: {"sy": 0.0, "dy": -b.h / 2},   # from its top edge
    "yb": lambda b: {"sy": 0.0, "dy": b.h / 2},   # from its bottom edge
    "c": lambda b: {"sx": 0.0},                   # from its middle, sideways
}


def bar(t, track, colour, t0, dur, box, grow="x", length=0.45, out=0.3, **extra):
    """A bar that draws itself in and, `out` seconds before its end, draws itself back to where it came from."""
    start = _START[grow](box)
    motion = [(0, start, "out"), (length, {}, "hold")]
    if out:
        motion = [(0, start, "out"), (length, {}, "hold"), (dur - out, {}, "in"), (dur, start)]
    return t.solid(track, colour, t0, dur, box, motion, **extra)


def exit_fade(dur, at_end=0.3):
    """Opacity 1 that fades to 0 over the last `at_end` seconds of a clip."""
    return keys([(0, 1.0, "hold"), (dur - at_end, 1.0, "smooth"), (dur, 0.0)])


# ================================================================================================
# Tipografía
# ================================================================================================

def tipo_capitulo():
    t = _kit("tipo-capitulo", "Capítulo con número", "Numbered chapter", "tipografia", 4.5, 7200,
             ["capítulo", "número", "título", "tipografía"], thumb_at=2.4, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    num = Box(100, 200, 520, 680)
    label(t, t.track("text", "Número"), "01", 0.2, 3.9, num, "Anton", 560, TEAL, weight=400, align="right",
          layers=outlined(TEAL, 5), anim_in=tanim("fade-up-char", duration=0.6), anim_out=fade(0.3),
          name="Número (contorno)")
    label(t, t.track("text", "Número"), "01", 1.0, 3.1, num, "Anton", 560, TEAL, weight=400, align="right",
          anim_in=wipe(-90, 0.9, 0.2), anim_out=fade(0.3), name="Número")
    bar(t, t.track("shape", "Barra"), TEAL, 0.4, 3.8, Box(670, 320, 12, 440), grow="y", length=0.4, out=0.3)
    label(t, t.track("text", "Antetítulo"), "CAPÍTULO", 0.7, 3.35, Box(724, 332, 1100, 66), "Inter", 44, TEAL,
          weight=700, align="left", spacing=20, anim_in=wipe(0, 0.5), anim_out=wipe(0, 0.3), name="Antetítulo")
    label(t, t.track("text", "Título"), "El comienzo", 0.85, 3.2, Box(720, 404, 1120, 200), "Sora", 150, WHITE,
          weight=800, align="left", anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Título")
    label(t, t.track("text", "Detalle"), "todo lo que necesitas saber", 1.1, 2.95, Box(726, 628, 1100, 72), "Inter",
          48, MIST, weight=400, align="left", anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Detalle")
    return t


def _stacked(t, words, x, ys, h, size, kicker, detail, bar_box, kicker_y, detail_y, det_size=32, kick_size=28,
             kick_h=44, det_h=56, spacing=12, stroke_w=4):
    """Stacked words born from a vertical bar; the bar leaves with the last of them."""
    bar(t, t.track("shape", "Barra"), TEAL, 0.2, 4.15, bar_box, grow="y", length=0.5, out=0.3)
    label(t, t.track("text", "Antetítulo"), kicker, 0.5, 3.5, Box(x + 4, kicker_y, 1000, kick_h), "Inter",
          kick_size, TEAL, weight=700, align="left", spacing=spacing, anim_in=wipe(0, 0.5), anim_out=wipe(0, 0.3),
          name="Antetítulo")
    for i, (w, colour, hollow_word) in enumerate(words):
        layers = outlined(colour, stroke_w) if hollow_word else None
        label(t, t.track("text", "Palabra"), w, 0.6 + i * 0.15, 3.4 - i * 0.05, Box(x, ys[i], 1300, h), "Anton",
              size, colour, weight=400, align="left", spacing=2, layers=layers, anim_in=wipe(0, 0.55),
              anim_out=wipe(0, 0.3), name=f"Palabra {i + 1}")
    label(t, t.track("text", "Detalle"), detail, 1.2, 2.8, Box(x + 4, detail_y, 1000, det_h), "Inter", det_size,
          MIST, weight=400, align="left", anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Detalle")


def tipo_apilado():
    t = _kit("tipo-apilado", "Palabras apiladas", "Stacked words", "tipografia", 4.5, 7201,
             ["apilado", "palabras", "título", "tipografía", "contorno"], thumb_at=2.4, background=DEEP)
    bg(t, DEEP)
    _stacked(t, [("CREA", WHITE, False), ("SIN", WHITE, True), ("MIEDO", CORAL, False)], 566, [150, 395, 640],
             340, 280, "EPISODIO 04", "una serie de tu canal", Box(520, 96, 12, 890), 96, 922, det_size=44,
             kick_size=38, kick_h=56, det_h=64, spacing=16, stroke_w=5)
    return t


def tipo_dividido():
    t = _kit("tipo-dividido", "Palabra partida en dos colores", "Split-colour word", "tipografia", 4.5, 7202,
             ["dos colores", "título", "tipografía", "impacto"], thumb_at=2.4, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=135)
    bar(t, t.track("shape", "Línea"), CORAL, 0.2, 4.0, Box(100, 537, 1720, 6), grow="c", length=0.5, out=0.3)
    word = Box(80, 405, 1760, 270)
    label(t, t.track("text", "Título"), "IMPARABLE", 0.45, 3.6, word, "Archivo Black", 210, WHITE, weight=400,
          spacing=2, anim_in=tanim("imf-slit-opening", duration=0.6), anim_out=fade(0.35), name="Título")
    # The same word in teal, cut to its lower half: the word reads in two colours split by the line.
    low = t.track("text", "Título (mitad de abajo)")
    half = label(t, low, "IMPARABLE", 0.45, 3.6, word, "Archivo Black", 210, TEAL, weight=400, spacing=2,
                 anim_in=tanim("imf-slit-opening", duration=0.6), anim_out=fade(0.35),
                 name="Título (mitad de abajo)")
    t.mask(low, half, "rectangle", x=0.5, y=0.75, w=1.0, h=0.5)
    label(t, t.track("text", "Antetítulo"), "TEMPORADA 2", 0.9, 3.2, Box(80, 290, 1760, 64), "Inter", 42, TEAL,
          weight=700, spacing=22, anim_in=tanim("fade-up-char", duration=0.5), anim_out=fade(0.3),
          name="Antetítulo")
    label(t, t.track("text", "Detalle"), "estreno · viernes 20:00", 1.1, 3.0, Box(80, 720, 1760, 72), "Inter", 48,
          MIST, weight=400, spacing=2, anim_in=fade(0.5), anim_out=fade(0.3), name="Detalle")
    return t


def tipo_recuadro():
    t = _kit("tipo-recuadro", "Título en recuadro", "Boxed title", "tipografia", 4.5, 7203,
             ["recuadro", "marco", "título", "tipografía", "reportaje"], thumb_at=2.4, background=DEEP)
    bg(t, DEEP)
    x, y, w, h, k = 210, 240, 1500, 560, 6
    sides = [(Box(x, y, w, k), "x", 0.2), (Box(x + w - k, y, k, h), "y", 0.45), (Box(x, y + h - k, w, k), "xr", 0.7),
             (Box(x, y, k, h), "yb", 0.95)]
    for box, grow, at in sides:
        dur = 4.25 - at
        bar(t, t.track("shape", "Marco"), WHITE, at, dur, box, grow=grow, length=0.3, out=0,
            opacity=exit_fade(dur, 0.35))
    # The kicker cuts the top side: a patch of the background colour behind it.
    t.solid(t.track("shape", "Corte"), DEEP, 0.15, 4.1, Box(730, 208, 460, 70))
    label(t, t.track("text", "Antetítulo"), "REPORTAJE", 0.6, 3.5, Box(730, 208, 460, 70), "Inter", 40, TEAL,
          weight=700, spacing=16, anim_in=tanim("fade-up-char", duration=0.5), anim_out=fade(0.3),
          name="Antetítulo")
    label(t, t.track("text", "Título"), "LO QUE NADIE\nTE CUENTA", 0.9, 3.2, Box(260, 290, 1400, 460), "Sora", 134,
          WHITE, weight=800, line=1.1, anim_in=tanim("rise-by-word", duration=0.5), anim_out=fade(0.35),
          name="Título")
    label(t, t.track("text", "Detalle"), "una historia de tu canal", 1.4, 2.75, Box(210, 840, 1500, 68), "Inter", 46,
          MIST, weight=400, spacing=2, anim_in=fade(0.5), anim_out=fade(0.3), name="Detalle")
    return t


def tipo_contorno():
    t = _kit("tipo-contorno", "Contorno que se llena", "Outline that fills", "tipografia", 4.5, 7204,
             ["contorno", "relleno", "frase", "tipografía"], thumb_at=2.6, background=NAVY)
    bg(t, NAVY)
    label(t, t.track("text", "Antetítulo"), "IDEA DEL DÍA", 0.2, 3.9, Box(160, 110, 1600, 60), "Inter", 40, MIST,
          weight=700, spacing=20, anim_in=tanim("fade-up-char", duration=0.5), anim_out=fade(0.3),
          name="Antetítulo")
    word = Box(160, 186, 1600, 360)
    label(t, t.track("text", "Palabra 1"), "MENOS", 0.3, 3.8, word, "Anton", 300, WHITE, weight=400, spacing=8,
          layers=outlined(WHITE, 5), anim_in=tanim("blur-in", duration=0.5), anim_out=fade(0.3),
          name="Palabra 1 (contorno)")
    label(t, t.track("text", "Palabra 1"), "MENOS", 1.1, 3.0, word, "Anton", 300, TEAL, weight=400, spacing=8,
          anim_in=wipe(-90, 0.9, 0.1), anim_out=fade(0.3), name="Palabra 1")
    label(t, t.track("text", "Palabra 2"), "ES MÁS", 0.6, 3.5, Box(160, 536, 1600, 360), "Anton", 300, WHITE,
          weight=400, spacing=8, anim_in=tanim("rise", duration=0.5), anim_out=fade(0.3), name="Palabra 2")
    bar(t, t.track("shape", "Línea"), SUN, 1.4, 2.85, Box(820, 884, 280, 8), grow="c", length=0.4, out=0.3)
    label(t, t.track("text", "Detalle"), "una frase para recordar", 1.6, 2.5, Box(160, 906, 1600, 68), "Inter", 44,
          MIST, weight=400, spacing=2, anim_in=wipe(90, 0.5), anim_out=wipe(90, 0.3), name="Detalle")
    return t


def tipo_editorial():
    t = _kit("tipo-editorial", "Título editorial claro", "Light editorial title", "tipografia", 5.0, 7205,
             ["editorial", "revista", "claro", "elegante", "tipografía"], thumb_at=2.8, background=PAPER)
    bg(t, PAPER)
    bar(t, t.track("shape", "Línea"), CORAL, 0.2, 4.35, Box(154, 222, 96, 6), grow="x", length=0.35, out=0.3)
    label(t, t.track("text", "Antetítulo"), "N.º 12 — OCTUBRE", 0.4, 4.0, Box(270, 196, 1000, 58), "Inter", 36,
          CORAL, weight=700, align="left", spacing=12, anim_in=wipe(0, 0.5), anim_out=wipe(0, 0.3),
          name="Antetítulo")
    label(t, t.track("text", "Título"), "El arte de\nempezar", 0.6, 3.85, Box(144, 250, 1200, 480),
          "Playfair Display", 210, NAVY, weight=700, align="left", line=1.0,
          anim_in=tanim("rise-by-word", duration=0.6), anim_out=fade(0.4), name="Título")
    label(t, t.track("text", "Número"), "12", 0.9, 3.55, Box(1240, 230, 530, 520), "Playfair Display", 440, CORAL,
          weight=700, align="right", italic=True, anim_in=tanim("fade-up-char", duration=0.7), anim_out=fade(0.4),
          name="Número")
    bar(t, t.track("shape", "Línea"), NAVY, 1.1, 3.45, Box(150, 772, 1620, 4), grow="x", length=0.6, out=0.3)
    label(t, t.track("text", "Detalle"), "Una guía corta para dar el primer paso", 1.4, 3.0, Box(150, 796, 1500, 72),
          "Inter", 48, NAVY, weight=400, align="left", anim_in=wipe(90, 0.5), anim_out=wipe(90, 0.3),
          name="Detalle")
    return t


def tipo_subrayado():
    t = _kit("tipo-subrayado", "Título con marcador", "Highlighted title", "tipografia", 4.5, 7206,
             ["marcador", "subrayado", "tutorial", "título", "tipografía"], thumb_at=2.4, background=NAVY)
    bg(t, NAVY)
    pill(t, t.track("shape", "Etiqueta"), TEAL, 0.2, 3.85, Box(200, 236, 330, 76),
         [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (3.55, {}, "in"), (3.85, {"s": 0.0})])
    label(t, t.track("text", "Etiqueta"), "TUTORIAL", 0.35, 3.6, Box(200, 236, 330, 76), "Inter", 36, NAVY,
          weight=800, spacing=8, anim_in=fade(0.3), anim_out=fade(0.2), name="Etiqueta")
    bar(t, t.track("shape", "Marcador"), CORAL, 1.1, 3.05, Box(176, 612, 1000, 78), grow="x", length=0.45, out=0.3)
    label(t, t.track("text", "Título"), "Cómo editar", 0.5, 3.55, Box(190, 330, 1640, 200), "Sora", 160, WHITE,
          weight=800, align="left", anim_in=tanim("rise-by-word", duration=0.5), anim_out=fade(0.3),
          name="Título 1")
    label(t, t.track("text", "Título"), "más rápido", 0.7, 3.35, Box(190, 530, 1640, 200), "Sora", 160, WHITE,
          weight=800, align="left", anim_in=tanim("rise-by-word", duration=0.5), anim_out=fade(0.3),
          name="Título 2")
    label(t, t.track("text", "Detalle"), "5 trucos en 5 minutos", 1.3, 2.75, Box(200, 770, 1400, 72), "Inter", 48,
          MIST, weight=400, align="left", anim_in=fade(0.5), anim_out=fade(0.3), name="Detalle")
    return t


def tipo_top():
    t = _kit("tipo-top", "Número de lista", "Countdown number", "tipografia", 5.0, 7207,
             ["top", "lista", "ranking", "número", "tipografía"], thumb_at=2.6, background=DEEP)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=120)
    label(t, t.track("text", "Número"), "10", 0.3, 4.25, Box(120, 240, 640, 720), "Anton", 640, TEAL, weight=400,
          align="right", anim_in=tanim("fade-up-char", duration=0.6), anim_out=fade(0.4), name="Número")
    label(t, t.track("text", "Antetítulo"), "TOP", 0.2, 4.35, Box(120, 130, 640, 110), "Sora", 80, WHITE,
          weight=800, align="right", spacing=28, anim_in=tanim("fade-up-char", duration=0.5), anim_out=fade(0.4),
          name="Top")
    bar(t, t.track("shape", "Barra"), CORAL, 0.6, 3.95, Box(820, 360, 12, 440), grow="y", length=0.45, out=0.3)
    label(t, t.track("text", "Antetítulo"), "RANKING 2026", 0.85, 3.6, Box(874, 370, 966, 58), "Inter", 38, CORAL,
          weight=700, align="left", spacing=16, anim_in=wipe(0, 0.5), anim_out=wipe(0, 0.3), name="Antetítulo")
    label(t, t.track("text", "Título"), "Los mejores lugares\npara viajar", 1.0, 3.45, Box(870, 440, 970, 230),
          "Sora", 84, WHITE, weight=800, align="left", line=1.1, anim_in=wipe(0, 0.7), anim_out=wipe(0, 0.3),
          name="Título")
    label(t, t.track("text", "Detalle"), "elegidos por la comunidad", 1.3, 3.15, Box(876, 700, 966, 68), "Inter",
          44, MIST, weight=400, align="left", anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Detalle")
    return t


def tipo_lineas():
    t = _kit("tipo-lineas", "Título entre líneas", "Title between rules", "tipografia", 4.5, 7208,
             ["líneas", "episodio", "título", "tipografía", "elegante"], thumb_at=2.4, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=90)
    label(t, t.track("text", "Antetítulo"), "NUEVO EPISODIO", 0.3, 3.8, Box(560, 286, 800, 66), "Inter", 42, TEAL,
          weight=700, spacing=18, anim_in=tanim("fade-up-char", duration=0.5), anim_out=fade(0.3),
          name="Antetítulo")
    bar(t, t.track("shape", "Línea"), TEAL, 0.5, 3.75, Box(160, 317, 400, 4), grow="xr", length=0.5, out=0.3)
    bar(t, t.track("shape", "Línea"), TEAL, 0.5, 3.75, Box(1360, 317, 400, 4), grow="x", length=0.5, out=0.3)
    label(t, t.track("text", "Título"), "TU HISTORIA", 0.6, 3.5, Box(80, 360, 1760, 330), "Bebas Neue", 300, WHITE,
          weight=400, spacing=10, anim_in=tanim("blur-in", duration=0.6), anim_out=fade(0.35), name="Título")
    bar(t, t.track("shape", "Línea"), MIST, 1.0, 3.25, Box(860, 712, 200, 4), grow="c", length=0.4, out=0.3)
    label(t, t.track("text", "Detalle"), "contada desde el principio", 1.2, 2.85, Box(260, 734, 1400, 72), "Inter",
          46, MIST, weight=400, spacing=2, anim_in=wipe(90, 0.5), anim_out=wipe(90, 0.3), name="Detalle")
    return t


def tipo_bloques():
    t = _kit("tipo-bloques", "Palabras en bloques de color", "Words on colour blocks", "tipografia", 4.5, 7209,
             ["bloques", "pasos", "palabras", "tipografía", "color"], thumb_at=2.4, background=DEEP)
    bg(t, DEEP)
    label(t, t.track("text", "Antetítulo"), "3 PASOS PARA", 0.2, 3.9, Box(464, 176, 1000, 60), "Inter", 40, MIST,
          weight=700, align="left", spacing=16, anim_in=wipe(0, 0.5), anim_out=fade(0.3), name="Antetítulo")
    rows = [("APRENDE", TEAL, NAVY, 460, 870), ("EDITA", CORAL, WHITE, 620, 650), ("CRECE", SUN, NAVY, 780, 650)]
    for i, (word, back, ink, x, w) in enumerate(rows):
        y, at = 256 + i * 230, 0.4 + i * 0.15
        dur = 4.05 - i * 0.1 - at
        bar(t, t.track("shape", "Bloque"), back, at, dur, Box(x, y, w, 200), grow="x", length=0.4, out=0.3)
        # The word wipes back into its block as the block draws back in.
        label(t, t.track("text", "Palabra"), word, at + 0.15, dur - 0.2, Box(x + 50, y, w - 50, 200),
              "Archivo Black", 150, ink, weight=400, align="left", anim_in=wipe(0, 0.5), anim_out=wipe(0, 0.25),
              name=f"Paso {i + 1}")
    return t


def tipo_antes_despues():
    t = _kit("tipo-antes-despues", "Antes y después", "Before and after", "tipografia", 4.5, 7210,
             ["antes", "después", "comparación", "dos tonos", "tipografía"], thumb_at=2.4, background=NAVY)
    fondo = t.track("shape", "Fondo")
    t.solid(fondo, PAPER, 0, 4.5, Box(0, 0, 960, 1080))
    t.solid(fondo, NAVY, 0, 4.5, Box(960, 0, 960, 1080))
    bar(t, t.track("shape", "Línea"), CORAL, 0.2, 4.0, Box(954, 250, 12, 580), grow="y", length=0.45, out=0.3)
    label(t, t.track("text", "Palabra 1"), "ANTES", 0.5, 3.45, Box(80, 360, 830, 300), "Anton", 250, NAVY,
          weight=400, align="right", spacing=4, anim_in=wipe(180, 0.6), anim_out=wipe(180, 0.3), name="Palabra 1")
    label(t, t.track("text", "Palabra 2"), "DESPUÉS", 0.65, 3.3, Box(1010, 360, 830, 300), "Anton", 250, WHITE,
          weight=400, align="left", spacing=4, anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Palabra 2")
    label(t, t.track("text", "Detalle 1"), "cómo empecé", 0.9, 3.05, Box(100, 680, 810, 72), "Inter", 48, NAVY,
          weight=500, align="right", anim_in=wipe(180, 0.5), anim_out=wipe(180, 0.3), name="Detalle 1")
    label(t, t.track("text", "Detalle 2"), "cómo voy hoy", 1.0, 2.95, Box(1010, 680, 810, 72), "Inter", 48, MIST,
          weight=500, align="left", anim_in=wipe(0, 0.5), anim_out=wipe(0, 0.3), name="Detalle 2")
    return t


def tipo_indice():
    t = _kit("tipo-indice", "Índice de capítulos", "Chapter index", "tipografia", 5.0, 7211,
             ["índice", "capítulos", "contenido", "lista", "tipografía"], thumb_at=2.8, background=NAVY)
    bg(t, NAVY)
    bar(t, t.track("shape", "Barra"), TEAL, 0.2, 4.35, Box(160, 150, 12, 110), grow="y", length=0.35, out=0.3)
    label(t, t.track("text", "Título"), "EN ESTE VIDEO", 0.4, 3.95, Box(204, 145, 1500, 120), "Sora", 92, WHITE,
          weight=800, align="left", spacing=2, anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Título")
    rows = [("01", "Introducción", "0:00"), ("02", "Materiales", "1:24"), ("03", "Paso a paso", "3:05")]
    for i, (n, name, time) in enumerate(rows):
        y, at = 300 + i * 190, 0.6 + i * 0.18
        dur = 4.35 - at - (2 - i) * 0.08
        bar(t, t.track("shape", "Línea"), MIST, at, dur + 0.1, Box(160, y, 1600, 3), grow="x", length=0.5, out=0.3,
            alpha=0.45)
        label(t, t.track("text", "Número"), n, at + 0.15, dur - 0.25, Box(160, y + 20, 180, 170), "Sora", 76, TEAL,
              weight=700, align="left", anim_in=wipe(90, 0.45), anim_out=fade(0.25), name=f"Número {i + 1}")
        label(t, t.track("text", "Capítulo"), name, at + 0.22, dur - 0.32, Box(350, y + 20, 1100, 170), "Sora", 80,
              WHITE, weight=600, align="left", anim_in=wipe(90, 0.5), anim_out=fade(0.25), name=f"Capítulo {i + 1}")
        label(t, t.track("text", "Tiempo"), time, at + 0.3, dur - 0.4, Box(1460, y + 20, 300, 170), "Inter", 52,
              MIST, weight=500, align="right", anim_in=wipe(90, 0.45), anim_out=fade(0.25), name=f"Tiempo {i + 1}")
    bar(t, t.track("shape", "Línea"), MIST, 1.2, 3.25, Box(160, 870, 1600, 3), grow="x", length=0.5, out=0.3,
        alpha=0.45)
    return t


def tipo_apilado_vertical():
    t = _kit_tall("tipo-apilado-vertical", "Palabras apiladas (vertical)", "Stacked words (vertical)", "tipografia",
                  4.5, 7212, ["apilado", "palabras", "título", "tipografía", "contorno"], thumb_at=2.4,
                  background=DEEP)
    bg(t, DEEP)
    _stacked(t, [("HAZ", WHITE, False), ("QUE", WHITE, True), ("PASE", CORAL, False)], 156, [640, 900, 1160],
             290, 270, "EPISODIO 04", "una serie de tu canal", Box(120, 560, 10, 940), 560, 1460, det_size=40,
             kick_size=34, kick_h=50, det_h=60)
    return t


def tipo_capitulo_vertical():
    t = _kit_tall("tipo-capitulo-vertical", "Capítulo con número (vertical)", "Numbered chapter (vertical)",
                  "tipografia", 4.5, 7213, ["capítulo", "número", "título", "tipografía"], thumb_at=2.4,
                  background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    num = Box(140, 420, 800, 560)
    label(t, t.track("text", "Número"), "02", 0.2, 3.9, num, "Anton", 480, TEAL, weight=400,
          layers=outlined(TEAL, 5), anim_in=tanim("fade-up-char", duration=0.6), anim_out=fade(0.3),
          name="Número (contorno)")
    label(t, t.track("text", "Número"), "02", 1.0, 3.1, num, "Anton", 480, TEAL, weight=400,
          anim_in=wipe(-90, 0.9, 0.2), anim_out=fade(0.3), name="Número")
    bar(t, t.track("shape", "Barra"), TEAL, 0.4, 3.8, Box(340, 1010, 400, 8), grow="c", length=0.45, out=0.35)
    label(t, t.track("text", "Antetítulo"), "CAPÍTULO", 0.7, 3.35, Box(140, 1040, 800, 60), "Inter", 36, TEAL,
          weight=700, spacing=16, anim_in=wipe(90, 0.5), anim_out=wipe(90, 0.3), name="Antetítulo")
    label(t, t.track("text", "Título"), "El comienzo", 0.85, 3.2, Box(90, 1110, 900, 140), "Sora", 100, WHITE,
          weight=800, anim_in=wipe(90, 0.6), anim_out=wipe(90, 0.3), name="Título")
    label(t, t.track("text", "Detalle"), "todo lo que necesitas saber", 1.1, 2.95, Box(90, 1260, 900, 60), "Inter",
          40, MIST, weight=400, anim_in=fade(0.5), anim_out=fade(0.3), name="Detalle")
    return t


# ================================================================================================
# Títulos con estilo (over the user's photo or video)
# ================================================================================================

TXT_SHADOW = shadow("#000000", 0, 4, 14, 0.55)


def _photo(t, sample, dim=0.3):
    photo_bg(t, sample, s1=1.06, label="Tu foto o video")
    if dim:
        shade_full(t, dim)


def _side_shade(t, width=1200, alpha=0.65):
    t.solid(t.track("shape", "Sombra"), "#000000", 0, t.duration, Box(0, 0, width, t.h),
            layers=[gradient([(0, "#000000", alpha), (1, "#000000", 0.0)], angle=0), no_stroke()])


def _blocks(t, rows, x, y0, step, h, font_size, end=4.55):
    """Words on colour blocks; each word wipes back into its block as the block draws back in."""
    for i, (word, back, ink, w) in enumerate(rows):
        y, at = y0 + i * step, 0.3 + i * 0.15
        dur = end - at + i * 0.05
        bar(t, t.track("shape", "Bloque"), back, at, dur, Box(x, y, w, h), grow="x", length=0.45, out=0.3)
        label(t, t.track("text", "Título"), word, at + 0.2, dur - 0.25, Box(x + 36, y, w - 36, h), "Montserrat",
              font_size, ink, weight=900, align="left", anim_in=wipe(0, 0.55), anim_out=wipe(0, 0.25),
              name=f"Título {i + 1}")


def estilo_resaltado():
    t = _kit("estilo-resaltado", "Título resaltado", "Highlighted title", "titulos-estilo", 5.0, 7300,
             ["resaltado", "bloques", "receta", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-cooking-02", 0.15)
    label(t, t.track("text", "Antetítulo"), "COCINA EN CASA", 0.3, 4.3, Box(164, 538, 800, 50), "Inter", 30, WHITE,
          weight=700, align="left", spacing=10, layers=[TXT_SHADOW, fill(WHITE)], anim_in=wipe(-90, 0.5),
          anim_out=fade(0.3), name="Antetítulo")
    _blocks(t, [("LA RECETA", SUN, NAVY, 760), ("MÁS FÁCIL", WHITE, NAVY, 700)], 160, 600, 140, 130, 88)
    return t


def estilo_corchetes():
    t = _kit("estilo-corchetes", "Título entre corchetes", "Bracketed title", "titulos-estilo", 5.0, 7301,
             ["corchetes", "rutina", "título", "foto", "minimalista"], thumb_at=2.6)
    _photo(t, "h-nature-02", 0.35)
    k, hh, arm, cy = 13, 364, 72, 510
    top = cy - hh / 2
    for side, x in ((-1, 400), (1, 1507)):
        dx = -side * 480
        mo = [(0, {"dx": dx}, "out"), (0.55, {}, "hold"), (3.95, {}, "in"), (4.35, {"dx": dx})]
        op = keys([(0, 0.0, "smooth"), (0.25, 1.0, "hold"), (4.1, 1.0, "smooth"), (4.35, 0.0)])
        arm_x = x if side < 0 else x + k - arm
        for box in (Box(x, top, k, hh), Box(arm_x, top, arm, k), Box(arm_x, top + hh - k, arm, k)):
            t.solid(t.track("shape", "Corchete"), WHITE, 0.2, 4.35, box, mo, opacity=op)
    label(t, t.track("text", "Título"), "MI RUTINA", 0.55, 3.85, Box(440, 340, 1040, 340), "Bebas Neue", 275, WHITE,
          weight=400, spacing=8, layers=[TXT_SHADOW, fill(WHITE)], anim_in=tanim("imf-centre-curtain", duration=0.6),
          anim_out=fade(0.3), name="Título")
    label(t, t.track("text", "Detalle"), "DE CADA MAÑANA", 0.9, 3.45, Box(440, 728, 1040, 66), "Inter", 44, TEAL,
          weight=800, spacing=16, layers=[TXT_SHADOW, fill(TEAL)], anim_in=tanim("fade-up-char", duration=0.5),
          anim_out=fade(0.3), name="Detalle")
    return t


def _corners(t, box, colour, t0, dur, arm=90, k=10, offset=70):
    """Four L-shaped corners that close in on `box` and open out again before the end."""
    corners = [(box.x, box.y, -1, -1), (box.x + box.w, box.y, 1, -1), (box.x, box.y + box.h, -1, 1),
               (box.x + box.w, box.y + box.h, 1, 1)]
    op = keys([(0, 0.0, "smooth"), (0.25, 1.0, "hold"), (dur - 0.35, 1.0, "smooth"), (dur, 0.0)])
    for cx, cy, sx, sy in corners:
        mo = [(0, {"dx": sx * offset, "dy": sy * offset}, "out"), (0.5, {}, "hold"), (dur - 0.4, {}, "in"),
              (dur, {"dx": sx * offset, "dy": sy * offset})]
        hx = cx if sx < 0 else cx - arm
        vy = cy if sy < 0 else cy - arm
        hy = cy if sy < 0 else cy - k
        vx = cx if sx < 0 else cx - k
        t.solid(t.track("shape", "Esquina"), colour, t0, dur, Box(hx, hy, arm, k), mo, opacity=op)
        t.solid(t.track("shape", "Esquina"), colour, t0, dur, Box(vx, vy, k, arm), mo, opacity=op)


def estilo_esquinas():
    t = _kit("estilo-esquinas", "Título con esquinas", "Corner-framed title", "titulos-estilo", 5.0, 7302,
             ["esquinas", "marco", "viaje", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-travel-02", 0.35)
    _corners(t, Box(240, 270, 1440, 540), TEAL, 0.2, 4.2, arm=118, k=13, offset=90)
    label(t, t.track("text", "Antetítulo"), "VLOG 07", 0.5, 3.7, Box(240, 360, 1440, 60), "Inter", 40, TEAL,
          weight=800, spacing=18, layers=[TXT_SHADOW, fill(TEAL)], anim_in=tanim("fade-up-char", duration=0.5),
          anim_out=fade(0.3), name="Antetítulo")
    label(t, t.track("text", "Título"), "VIAJE A LA MONTAÑA", 0.6, 3.6, Box(270, 430, 1380, 150), "Sora", 94, WHITE,
          weight=800, layers=[TXT_SHADOW, fill(WHITE)], anim_in=tanim("fade-up-char", duration=0.6),
          anim_out=fade(0.3), name="Título")
    label(t, t.track("text", "Detalle"), "un fin de semana en la ruta", 0.9, 3.3, Box(240, 600, 1440, 66), "Inter", 42,
          WHITE, weight=400, spacing=2, layers=[TXT_SHADOW, fill(WHITE)], anim_in=fade(0.5), anim_out=fade(0.3),
          name="Detalle")
    return t


def estilo_pildoras():
    t = _kit("estilo-pildoras", "Título con etiquetas", "Title with tags", "titulos-estilo", 5.0, 7303,
             ["etiquetas", "píldoras", "vlog", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-portrait-02", 0)
    _side_shade(t, 1400, 0.72)
    x = 156
    for i, (tag, back, ink, w) in enumerate([("VLOG", TEAL, NAVY, 196), ("VIAJES", CORAL, WHITE, 246),
                                              ("2026", SUN, NAVY, 196)]):
        at = 0.3 + i * 0.1
        dur = 4.4 - at - (2 - i) * 0.05
        mo = [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (dur - 0.3, {}, "in"), (dur, {"s": 0.0})]
        pill(t, t.track("shape", "Etiqueta"), back, at, dur, Box(x, 300, w, 68), mo)
        label(t, t.track("text", "Etiqueta"), tag, at + 0.12, dur - 0.4, Box(x, 300, w, 68), "Inter", 31, ink,
              weight=800, spacing=5, anim_in=fade(0.25), anim_out=fade(0.15), name=f"Etiqueta {i + 1}")
        x += w + 20
    label(t, t.track("text", "Título"), "Un día\nconmigo", 0.6, 3.7, Box(150, 384, 1300, 400), "Poppins", 162, WHITE,
          weight=800, align="left", line=0.88, layers=[TXT_SHADOW, fill(WHITE)],
          anim_in=tanim("rise-by-word", duration=0.5), anim_out=fade(0.3), name="Título")
    label(t, t.track("text", "Detalle"), "rutina, café y mucho trabajo", 1.1, 3.2, Box(156, 800, 1200, 70), "Inter",
          44, WHITE, weight=400, align="left", layers=[TXT_SHADOW, fill(WHITE)], anim_in=fade(0.5),
          anim_out=fade(0.3), name="Detalle")
    return t


def estilo_degradado():
    t = _kit("estilo-degradado", "Título en barra degradada", "Gradient bar title", "titulos-estilo", 5.0, 7304,
             ["degradado", "barra", "ciudad", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-city-05", 0.15)
    # The bar draws back in while its title wipes out.
    t.solid(t.track("shape", "Barra"), TEAL, 0.3, 4.2, Box(0, 590, 1540, 196),
            [(0, {"sx": 0.0, "dx": -770}, "out"), (0.5, {}, "hold"), (3.85, {}, "in"), (4.2, {"sx": 0.0, "dx": -770})],
            layers=[shadow("#000000", 0, 10, 30, 0.35), gradient([(0, TEAL), (1, CORAL)], angle=0), no_stroke()])
    label(t, t.track("text", "Título"), "CIUDAD DE NOCHE", 0.6, 3.85, Box(160, 590, 1360, 196), "Montserrat", 110,
          WHITE, weight=900, align="left", layers=[shadow("#000000", 0, 3, 10, 0.35), fill(WHITE)],
          anim_in=wipe(0, 0.6), anim_out=wipe(0, 0.3), name="Título")
    label(t, t.track("text", "Antetítulo"), "EPISODIO 03 · URBANO", 0.8, 3.55, Box(164, 514, 1200, 64), "Inter", 38,
          WHITE, weight=700, align="left", spacing=10, layers=[TXT_SHADOW, fill(WHITE)], anim_in=wipe(-90, 0.5),
          anim_out=wipe(-90, 0.3), name="Antetítulo")
    bar(t, t.track("shape", "Línea"), WHITE, 1.0, 3.35, Box(160, 806, 390, 6), grow="x", length=0.45, out=0.3)
    label(t, t.track("text", "Detalle"), "lo que no ves de día", 1.2, 3.0, Box(164, 822, 1200, 70), "Inter", 44,
          WHITE, weight=400, align="left", layers=[TXT_SHADOW, fill(WHITE)], anim_in=wipe(90, 0.5),
          anim_out=wipe(90, 0.3), name="Detalle")
    return t


def estilo_dos_tonos():
    t = _kit("estilo-dos-tonos", "Título en dos tonos", "Two-tone title", "titulos-estilo", 5.0, 7305,
             ["dos tonos", "viaje", "aventura", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-nature-05", 0.35)
    label(t, t.track("text", "Antetítulo"), "DIARIO DE VIAJE", 0.3, 4.1, Box(260, 300, 1400, 60), "Inter", 38, WHITE,
          weight=700, spacing=18, layers=[TXT_SHADOW, fill(WHITE)], anim_in=tanim("fade-up-char", duration=0.5),
          anim_out=fade(0.3), name="Antetítulo")
    title = label(t, t.track("text", "Título"), "PRIMER DÍA", 0.4, 4.0, Box(80, 370, 1760, 290), "Montserrat", 210,
                  WHITE, weight=900, spacing=2, layers=[shadow("#000000", 0, 6, 20, 0.45), fill(WHITE)],
                  anim_in=tanim("fade-up-char", duration=0.6), anim_out=fade(0.35), name="Título")
    title["textStyle"]["accent"] = {"rule": "lastWord", "colorEnabled": True, "color": "#ff2ee6c8"}
    bar(t, t.track("shape", "Línea"), CORAL, 0.9, 3.5, Box(830, 684, 260, 8), grow="c", length=0.4, out=0.3)
    label(t, t.track("text", "Detalle"), "de una aventura en el lago", 1.1, 3.25, Box(260, 708, 1400, 72), "Inter",
          46, WHITE, weight=400, spacing=2, layers=[TXT_SHADOW, fill(WHITE)], anim_in=wipe(90, 0.5),
          anim_out=wipe(90, 0.3), name="Detalle")
    return t


def estilo_cortes():
    t = _kit("estilo-cortes", "Título con cortes", "Slashed title", "titulos-estilo", 5.0, 7306,
             ["cortes", "diagonal", "juego", "título", "foto", "energía"], thumb_at=2.6)
    _photo(t, "h-tech-02", 0.25)
    t.solid(t.track("shape", "Corte"), CORAL, 0.3, 4.0, Box(100, 400, 1330, 222),
            [(0, {"sx": 0.0, "dx": -665}, "out"), (0.45, {}, "hold"), (3.7, {}, "in"), (4.0, {"sx": 0.0, "dx": -665})],
            kind="parallelogram", layers=[shadow("#000000", 0, 10, 26, 0.4), fill(CORAL), no_stroke()])
    for i, (x, c) in enumerate([(1450, WHITE), (1528, TEAL)]):
        at = 0.55 + i * 0.08
        dur = 4.15 - at
        t.solid(t.track("shape", "Corte"), c, at, dur, Box(x, 400, 58, 222),
                [(0, {"dy": -110}, "out"), (0.35, {}, "hold"), (dur - 0.3, {}, "in"), (dur, {"dy": 110})],
                kind="parallelogram", opacity=keys([(0, 0.0, "smooth"), (0.2, 1.0, "hold"), (dur - 0.2, 1.0, "smooth"),
                                                   (dur, 0.0)]))
    label(t, t.track("text", "Título"), "MODO JUEGO", 0.55, 3.7, Box(190, 400, 1150, 222), "Anton", 182, WHITE,
          weight=400, align="left", spacing=5, anim_in=wipe(0, 0.55), anim_out=wipe(0, 0.3), name="Título")
    label(t, t.track("text", "Detalle"), "directo todos los viernes", 0.9, 3.2, Box(194, 646, 1200, 70), "Inter", 44,
          WHITE, weight=600, align="left", spacing=2, layers=[TXT_SHADOW, fill(WHITE)], anim_in=wipe(90, 0.5),
          anim_out=wipe(90, 0.3), name="Detalle")
    return t


def estilo_cinta():
    t = _kit("estilo-cinta", "Título en cinta", "Ribbon title", "titulos-estilo", 5.0, 7307,
             ["cinta", "banda", "verano", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-beach-02", 0.1)
    rot = keys([(0, -4)])
    t.solid(t.track("shape", "Cinta"), NAVY, 0.3, 4.2, Box(-120, 440, 2160, 200),
            [(0, {"sx": 0.0, "dx": -1080}, "out"), (0.55, {}, "hold"), (3.9, {}, "in"), (4.2, {"sx": 0.0, "dx": -1080})],
            rotation=rot, layers=[shadow("#000000", 0, 12, 30, 0.45), fill(NAVY), no_stroke()])
    label(t, t.track("text", "Título"), "VERANO SIN FILTRO", 0.65, 3.7, Box(160, 440, 1600, 200), "Anton", 150, SUN,
          weight=400, spacing=6, rotation=rot, anim_in=wipe(0, 0.7), anim_out=wipe(0, 0.3), name="Título")
    pill(t, t.track("shape", "Etiqueta"), CORAL, 0.9, 3.5, Box(250, 352, 300, 60),
         [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (3.2, {}, "in"), (3.5, {"s": 0.0})], rotation=rot)
    label(t, t.track("text", "Etiqueta"), "NUEVA SERIE", 1.0, 3.3, Box(250, 352, 300, 60), "Inter", 26, WHITE,
          weight=800, spacing=6, rotation=rot, anim_in=fade(0.3), anim_out=fade(0.2), name="Etiqueta")
    return t


def estilo_sello():
    t = _kit("estilo-sello", "Título con sello", "Title with a stamp", "titulos-estilo", 5.0, 7308,
             ["sello", "nuevo", "podcast", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-podcast-01", 0.45)
    label(t, t.track("text", "Título"), "MI PRIMER\nPODCAST", 0.4, 3.9, Box(150, 320, 1300, 380), "Sora", 146,
          WHITE, weight=800, align="left", line=1.0, layers=[TXT_SHADOW, fill(WHITE)],
          anim_in=tanim("rise-by-word", duration=0.5), anim_out=fade(0.3), name="Título")
    label(t, t.track("text", "Detalle"), "episodio 1 · con invitados", 0.9, 3.4, Box(156, 716, 1200, 70), "Inter", 44,
          WHITE, weight=400, align="left", layers=[TXT_SHADOW, fill(WHITE)], anim_in=fade(0.5), anim_out=fade(0.3),
          name="Detalle")
    rot = keys([(0, -12)])
    stamp = centered(1230, 290, 300, 300)
    mo = [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (2.8, {}, "in"), (3.1, {"s": 0.0})]
    t.solid(t.track("shape", "Sello"), SUN, 1.1, 3.1, stamp, mo, kind="ellipse", rotation=rot,
            layers=[shadow("#000000", 0, 10, 24, 0.4), fill(SUN), no_stroke()])
    ring_mo = [(0, {"s": 0.6}, "out"), (0.5, {}, "hold"), (2.7, {}, "in"), (3.0, {"s": 0.0})]
    outline(t, t.track("shape", "Sello"), NAVY, 5, 1.2, 3.0, centered(1230, 290, 256, 256), ring_mo, kind="ellipse")
    label(t, t.track("text", "Sello"), "¡NUEVO!", 1.25, 2.9, stamp, "Archivo Black", 58, NAVY, weight=400,
          rotation=rot, anim_in=tanim("pop", duration=0.35), anim_out=fade(0.2), name="Sello")
    return t


def estilo_caja():
    t = _kit("estilo-caja", "Título en caja de contorno", "Outlined box title", "titulos-estilo", 5.0, 7309,
             ["caja", "contorno", "ciudad", "título", "foto", "minimalista"], thumb_at=2.6)
    _photo(t, "h-city-06", 0.35)
    box = Box(310, 320, 1300, 390)
    mo = [(0, {"s": 1.15}, "out"), (0.6, {}, "hold"), (4.0, {}, "in"), (4.4, {"s": 1.1})]
    op = keys([(0, 0.0, "smooth"), (0.4, 1.0, "hold"), (4.0, 1.0, "smooth"), (4.4, 0.0)])
    outline(t, t.track("shape", "Caja"), WHITE, 8, 0.2, 4.4, box, mo, opacity=op)
    label(t, t.track("text", "Título"), "MI CIUDAD", 0.5, 3.95, Box(330, 320, 1260, 390), "Bebas Neue", 275, WHITE,
          weight=400, spacing=12, layers=[TXT_SHADOW, fill(WHITE)], anim_in=tanim("blur-in", duration=0.6),
          anim_out=fade(0.35), name="Título")
    tag = Box(258, 276, 262, 84)
    tmo = [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (3.5, {}, "in"), (3.8, {"s": 0.0})]
    t.solid(t.track("shape", "Etiqueta"), CORAL, 0.7, 3.8, tag, tmo,
            layers=[shadow("#000000", 0, 6, 16, 0.35), fill(CORAL), no_stroke()])
    label(t, t.track("text", "Etiqueta"), "EP. 05", 0.8, 3.6, tag, "Inter", 40, WHITE, weight=800, spacing=5,
          anim_in=fade(0.25), anim_out=fade(0.2), name="Etiqueta")
    label(t, t.track("text", "Detalle"), "rincones que casi nadie conoce", 1.0, 3.3, Box(310, 744, 1300, 66), "Inter",
          42, WHITE, weight=400, spacing=2, layers=[TXT_SHADOW, fill(WHITE)], anim_in=fade(0.5), anim_out=fade(0.3),
          name="Detalle")
    return t


def estilo_ventana():
    t = _kit("estilo-ventana", "Título en ventana", "Window card title", "titulos-estilo", 5.0, 7310,
             ["ventana", "tarjeta", "tutorial", "título", "foto"], thumb_at=2.6)
    _photo(t, "h-desk-02", 0.15)
    t0, dur = 0.3, 4.3
    mo = [(0, {"dy": 70}, "out"), (0.5, {}, "hold"), (dur - 0.4, {}, "in"), (dur, {"dy": 70})]
    op = keys([(0, 0.0, "smooth"), (0.35, 1.0, "hold"), (dur - 0.35, 1.0, "smooth"), (dur, 0.0)])
    x, y, w = 160, 560, 900
    rrect(t, t.track("shape", "Ventana"), NAVY, t0, dur, Box(x, y, w, 320), radius=16, motion=mo, opacity=op,
          layers=[shadow("#000000", 0, 16, 40, 0.5), fill(NAVY, 0.95), no_stroke()])
    rrect(t, t.track("shape", "Ventana"), TEAL, t0, dur, Box(x, y, w, 56), radius=16, motion=mo, opacity=op)
    t.solid(t.track("shape", "Ventana"), TEAL, t0, dur, Box(x, y + 30, w, 26), mo, opacity=op)
    for i, c in enumerate([CORAL, SUN, WHITE]):
        t.solid(t.track("shape", "Puntos"), c, t0, dur, centered(x + 32 + i * 30, y + 28, 18, 18), mo, kind="ellipse",
                opacity=op)
    label(t, t.track("text", "Etiqueta"), "TUTORIAL", t0 + 0.4, dur - 0.7, Box(x + 500, y, 370, 56), "Inter", 24,
          NAVY, weight=800, align="right", spacing=8, anim_in=fade(0.3), anim_out=fade(0.2), name="Etiqueta")
    label(t, t.track("text", "Título"), "Aprende a editar\nen 10 minutos", t0 + 0.5, dur - 0.85,
          Box(x + 44, y + 86, w - 88, 190), "Sora", 66, WHITE, weight=800, align="left", line=1.1,
          anim_in=tanim("fade-up-char", duration=0.6), anim_out=fade(0.25), name="Título")
    return t


def estilo_sombra():
    t = _kit("estilo-sombra", "Título con sombra de color", "Colour-shadow title", "titulos-estilo", 5.0, 7311,
             ["sombra", "color", "atardecer", "título", "foto", "impacto"], thumb_at=2.6)
    _photo(t, "h-city-03", 0.25)
    label(t, t.track("text", "Título"), "ATARDECER", 0.4, 4.0, Box(160, 380, 1600, 220), "Archivo Black", 150, WHITE,
          weight=400, spacing=4, layers=[shadow(CORAL, 12, 12, 0, 1.0), fill(WHITE)],
          anim_in=tanim("pop", duration=0.45), anim_out=tanim("fade-scale", duration=0.35), name="Título")
    mo = [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (3.4, {}, "in"), (3.7, {"s": 0.0})]
    pill(t, t.track("shape", "Etiqueta"), TEAL, 0.8, 3.7, Box(740, 630, 440, 72), mo)
    label(t, t.track("text", "Etiqueta"), "EN LA CIUDAD", 0.95, 3.4, Box(740, 630, 440, 72), "Inter", 32, NAVY,
          weight=800, spacing=6, anim_in=fade(0.25), anim_out=fade(0.2), name="Etiqueta")
    return t


def estilo_resaltado_vertical():
    t = _kit_tall("estilo-resaltado-vertical", "Título resaltado (vertical)", "Highlighted title (vertical)",
                  "titulos-estilo", 5.0, 7312, ["resaltado", "bloques", "receta", "título", "foto"], thumb_at=2.6)
    _photo(t, "cooking-03", 0.1)
    label(t, t.track("text", "Antetítulo"), "COCINA EN CASA", 0.3, 4.3, Box(94, 1110, 800, 56), "Inter", 36, WHITE,
          weight=700, align="left", spacing=10, layers=[TXT_SHADOW, fill(WHITE)], anim_in=wipe(-90, 0.5),
          anim_out=fade(0.3), name="Antetítulo")
    _blocks(t, [("TU RECETA", SUN, NAVY, 720), ("EN 5", WHITE, NAVY, 380), ("MINUTOS", CORAL, WHITE, 620)], 90,
            1180, 150, 136, 96)
    return t


def estilo_esquinas_vertical():
    t = _kit_tall("estilo-esquinas-vertical", "Título con esquinas (vertical)", "Corner-framed title (vertical)",
                  "titulos-estilo", 5.0, 7313, ["esquinas", "marco", "viaje", "título", "foto"], thumb_at=2.6)
    _photo(t, "nature-01", 0.3)
    _corners(t, Box(120, 680, 840, 560), TEAL, 0.2, 4.2)
    label(t, t.track("text", "Antetítulo"), "VLOG 07", 0.5, 3.7, Box(140, 760, 800, 56), "Inter", 36, TEAL,
          weight=700, spacing=14, anim_in=tanim("fade-up-char", duration=0.5), anim_out=fade(0.3), name="Antetítulo")
    label(t, t.track("text", "Título"), "VIAJE A LA\nMONTAÑA", 0.6, 3.6, Box(140, 830, 800, 260), "Sora", 100, WHITE,
          weight=800, line=1.05, layers=[TXT_SHADOW, fill(WHITE)], anim_in=tanim("fade-up-char", duration=0.6),
          anim_out=fade(0.3), name="Título")
    label(t, t.track("text", "Detalle"), "un fin de semana en la ruta", 0.9, 3.3, Box(140, 1110, 800, 56), "Inter",
          38, WHITE, weight=400, spacing=2, layers=[TXT_SHADOW, fill(WHITE)], anim_in=fade(0.5), anim_out=fade(0.3),
          name="Detalle")
    return t


TEMPLATES = [tipo_capitulo, tipo_apilado, tipo_dividido, tipo_recuadro, tipo_contorno, tipo_editorial,
             tipo_subrayado, tipo_top, tipo_lineas, tipo_bloques, tipo_antes_despues, tipo_indice,
             tipo_apilado_vertical, tipo_capitulo_vertical,
             estilo_resaltado, estilo_corchetes, estilo_esquinas, estilo_pildoras, estilo_degradado,
             estilo_dos_tonos, estilo_cortes, estilo_cinta, estilo_sello, estilo_caja, estilo_ventana,
             estilo_sombra, estilo_resaltado_vertical, estilo_esquinas_vertical]
