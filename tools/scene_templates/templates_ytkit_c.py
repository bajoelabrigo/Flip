"""YouTube kit, batch c (see BRIEF-ytkit.md): Títulos cinéticos (order 7400-7449) and Frases (order 7600-7649).

12 wide + 3 vertical pieces per section, in the kit palette (navy / teal / coral / sun, light variants on #F4F7FB).
Every text editable with a Spanish name, every picture a slot, the background its own «Fondo» track. Words born from
a line or bar are revealed with a wipe from that line, never slid across it.
"""

from __future__ import annotations

from kit import (Box, bg, bg_gradient, centered, circle_photo, confetti, dots, effect, fill, flash, gradient, keys,
                 label, line, no_stroke, outline, photo_bg, pill, pop, ring, rrect, shade_full, shadow, slide_in, song,
                 spike, tall, tanim, text_style, wide)

NAVY = "#0B1A2E"
DEEP = "#06101F"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MIST = "#A9B8CC"
LIGHT = "#F4F7FB"

KIN = "titulos-cineticos"
QUO = "frases"


def _kit(id, es, en, section, duration, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", duration, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _tall(id, es, en, section, duration, order, tags, **kw):
    return tall(f"ytk-{id}", es, en, "ytkit", duration, order=order,
                tags=[f"kit:{section}", "youtube", "vertical", "shorts"] + tags, **kw)


def word(t, track, content, t0, dur, box, font, size, colour, *, slam=1.6, land=0.16, grow=0.04, weight=400,
         layers=None, name=None, editable=True, align="center", spacing=0.0, italic=False, anim_in=None,
         anim_out=None, line=1.05, **extra):
    """A word that lands on the beat: its size snaps from `slam` x down to the size, then keeps growing a touch."""
    if slam and slam != 1.0:
        kf = keys([(0, round(size * slam), "out"), (land, size, "linear"), (dur, round(size * (1 + grow)))])
    else:
        kf = keys([(0, size, "linear"), (dur, round(size * (1 + grow)))])
    style = text_style(font, size, layers or [fill(colour)], weight=weight, align=align, spacing=spacing,
                       italic=italic, line=line, anim_in=anim_in, anim_out=anim_out, keyframes={"pixelSize": kf})
    return t.text(track, content, t0, dur, box, style, label=name or content, editable=editable, **extra)


def pulses(t, times, peak=0.3, fall=0.22):
    t.adjust([effect("zoom_pulse", animated={"punch": spike(times, peak, fall)})], name="Golpe")


def burst(t, colour, at, cx, cy, size, width=8, length=0.6, grow=2.4, s0=0.5):
    ring(t, t.track("shape", "Onda"), colour, width, at, length, centered(cx, cy, size, size),
         [(0, {"s": s0}, "out"), (length, {"s": grow})], opacity=keys([(0, 1.0), (length, 0.0)]))


# ================================================================================================
# Títulos cinéticos
# ================================================================================================

def cin_cortes():
    t = _kit("cinetico-cortes", "Cortes de color", "Colour-cut words", KIN, 4.0, 7400,
             ["cinético", "palabras", "ritmo", "cortes", "energía"], thumb_at=2.9, background=NAVY)
    fondo = t.track("shape", "Fondo")
    words = [("NO", NAVY, WHITE), ("TE", CORAL, WHITE), ("LO", TEAL, NAVY), ("PIERDAS", SUN, NAVY)]
    texto = t.track("text", "Palabra")
    for i, (w, back, ink) in enumerate(words):
        at = i * 0.5
        t.solid(fondo, back, at, 0.5)
        word(t, texto, w, at, 0.5, Box(60, 240, 1800, 600), "Anton", 380, ink, slam=1.45, land=0.12,
             name=f"Palabra {i + 1}")
    t.solid(fondo, NAVY, 2.0, 2.0)
    word(t, t.track("text", "Frase"), "NO TE LO", 2.0, 2.0, Box(160, 250, 1600, 240), "Anton", 200, WHITE,
         slam=1.5, land=0.14, spacing=6, name="Frase 1")
    word(t, t.track("text", "Frase"), "PIERDAS", 2.25, 1.75, Box(160, 470, 1600, 320), "Anton", 260, TEAL,
         slam=1.5, land=0.14, spacing=6, name="Frase 2")
    line(t, t.track("shape", "Subrayado"), CORAL, 2.55, 1.45, Box(760, 800, 400, 16), grow="c", length=0.35)
    burst(t, WHITE, 2.25, 960, 630, 700, width=10, length=0.7)
    pulses(t, [0.0, 0.5, 1.0, 1.5, 2.0, 2.25])
    song(t, "electro", 0)
    return t


def cin_escala():
    t = _kit("cinetico-escala", "Palabras que crecen", "Scaling words", KIN, 5.0, 7401,
             ["cinético", "palabras", "escala", "ritmo"], thumb_at=2.2, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    label(t, t.track("text", "Antetítulo"), "LO QUE IMPORTA", 0.2, 4.8, Box(160, 250, 1600, 70), "Inter", 40, MIST,
          weight=700, spacing=14, anim_in=tanim("tracking-drift", duration=0.9), name="Antetítulo")
    for i, (w, c, at) in enumerate([("IDEAS", TEAL, 0.5), ("RITMO", CORAL, 1.5), ("ENERGÍA", SUN, 2.5),
                                    ("TÚ", WHITE, 3.5)]):
        dur = (1.0 if i < 3 else 1.5)
        burst(t, c, at + 0.1, 960, 540, 600, width=8, length=0.7, grow=2.8, s0=1.45)
        word(t, t.track("text", "Palabra"), w, at, dur, Box(160, 330, 1600, 420), "Anton", 300, c, slam=0.25,
             land=0.3, grow=0.1, spacing=4, name=f"Palabra {i + 1}")
    line(t, t.track("shape", "Línea"), TEAL, 0.4, 4.4, Box(860, 790, 200, 8), grow="c", length=0.4)
    pulses(t, [0.5, 1.5, 2.5, 3.5], 0.25)
    song(t, "electro", 1)
    return t


def cin_pila():
    t = _kit("cinetico-pila", "Pila giratoria", "Rotating stack", KIN, 4.4, 7402,
             ["cinético", "palabras", "giro", "lista"], thumb_at=2.4, background=DEEP)
    bg(t, DEEP)
    outline(t, t.track("shape", "Adorno"), TEAL, 6, 0.0, 4.3, centered(1450, 540, 460, 460),
            [(0, {"s": 0.0}, "back"), (0.6, {}, "hold"), (3.9, {}, "in"), (4.3, {"s": 0.0})],
            alpha=0.25, rotation=keys([(0, 0, "linear"), (4.3, 90)]))
    outline(t, t.track("shape", "Adorno"), CORAL, 6, 0.15, 4.1, centered(1450, 540, 300, 300),
            [(0, {"s": 0.0}, "back"), (0.6, {}, "hold"), (3.7, {}, "in"), (4.1, {"s": 0.0})],
            alpha=0.35, rotation=keys([(0, 45, "linear"), (4.1, -45)]))
    line(t, t.track("shape", "Barra"), TEAL, 0.1, 4.2, Box(400, 270, 14, 540), grow="y", length=0.4,
         opacity=keys([(0, 1.0, "hold"), (3.9, 1.0, "smooth"), (4.2, 0.0)]))
    for i, (w, c) in enumerate([("PIENSA", TEAL), ("CREA", WHITE), ("REPITE", CORAL)]):
        at = 0.35 + i * 0.4
        t.text(t.track("text", "Palabra"), w, at, 3.8 - at,
               Box(450, 270 + i * 180, 520, 180),
               text_style("Anton", 170, [fill(c)], weight=400, align="left", spacing=4, line=1.0,
                          anim_in=tanim("fade", duration=0.15), anim_out=tanim("fade", duration=0.3)),
               [(0, {"dy": -120}, "back"), (0.45, {})], label=f"Palabra {i + 1}",
               rotation=keys([(0, -90, "back"), (0.45, 0)]))
    label(t, t.track("text", "Detalle"), "tu método en tres pasos", 1.7, 2.1, Box(452, 820, 900, 60), "Inter", 36,
          MIST, weight=500, align="left", spacing=2, anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.3), name="Detalle")
    pulses(t, [0.35, 0.75, 1.15], 0.2)
    song(t, "electro", 2)
    return t


def cin_contador():
    t = _kit("cinetico-contador", "Contador al ritmo", "Counting-up title", KIN, 5.0, 7403,
             ["cinético", "contador", "números", "celebración", "suscriptores"], thumb_at=3.2, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=120)
    dots(t, [TEAL, MIST], 16, 0.0, 5.0, seed=5, size=(4, 10), drift=60, alpha=0.5)
    label(t, t.track("text", "Antetítulo"), "YA SOMOS", 0.2, 4.8, Box(160, 220, 1600, 70), "Inter", 44, MIST,
          weight=700, spacing=16, anim_in=tanim("tracking-drift", duration=0.9), name="Antetítulo")
    st = text_style("Anton", 300, [shadow("#000000", 0, 8, 24, 0.4), fill(TEAL)], weight=400, spacing=6)
    st.update(counter=True, counterFrom=0, counterSeconds=2.0)
    st["keyframes"] = {"pixelSize": keys([(0, 300, "hold"), (2.0, 300, "out"), (2.12, 336, "inout"), (2.32, 300)])}
    t.text(t.track("text", "Número"), "100.000", 0.4, 4.6, Box(160, 290, 1600, 380), st, label="Número final")
    burst(t, TEAL, 2.4, 960, 480, 700, width=10, length=0.8)
    word(t, t.track("text", "Gracias"), "¡GRACIAS!", 2.5, 2.5, Box(160, 690, 1600, 160), "Sora", 110, CORAL,
         weight=800, slam=1.8, land=0.14, spacing=6, name="Gracias")
    confetti(t, [TEAL, CORAL, SUN, WHITE], 2.4, 2.6, seed=11, lanes=4, density=0.35)
    pulses(t, [2.4, 2.5], 0.3)
    song(t, "upbeat", 0)
    return t


def cin_linea():
    t = _kit("cinetico-linea", "Palabras desde la línea", "Words from a line", KIN, 4.5, 7404,
             ["cinético", "palabras", "línea", "minimalista"], thumb_at=2.5, background=DEEP)
    bg(t, DEEP)
    x0, gap, y_line = 246, 50, 610
    t.solid(t.track("shape", "Línea"), TEAL, 0.1, 4.3, Box(x0, y_line, 1430, 8),
            [(0, {"sx": 0.0}, "out"), (0.5, {}, "hold"), (3.9, {}, "in"), (4.3, {"sx": 0.0})])
    x = x0
    for i, (w, wd, c) in enumerate([("CADA", 388, WHITE), ("DÍA", 393, WHITE), ("CUENTA", 548, TEAL)]):
        at = 0.5 + i * 0.4
        label(t, t.track("text", "Palabra"), w, at, 3.85 - at, Box(x - 10, y_line - 302, wd + 20, 300), "Anton", 200,
              c, weight=400, valign="bottom", line=1.0,
              anim_in=tanim("wipe", duration=0.4, angle=-90, softness=0.1), anim_out=tanim("fade", duration=0.3),
              name=f"Palabra {i + 1}")
        x += wd + gap
    label(t, t.track("text", "Detalle"), "un paso a la vez", 1.8, 2.05, Box(x0, y_line + 24, 1430, 80), "Inter", 52,
          MIST, weight=500, valign="top", spacing=4,
          anim_in=tanim("wipe", duration=0.5, angle=90, softness=0.1), anim_out=tanim("fade", duration=0.3),
          name="Detalle")
    pulses(t, [0.5, 0.9, 1.3], 0.18)
    song(t, "cine", 1)
    return t


def cin_dividida():
    t = _kit("cinetico-dividida", "Pantalla dividida", "Split-screen words", KIN, 4.5, 7405,
             ["cinético", "pantalla dividida", "contraste", "palabras"], thumb_at=2.6, background=DEEP)
    bg(t, DEEP)
    t.solid(t.track("shape", "Mitad"), NAVY, 0.0, 4.5, Box(0, 0, 960, 1080),
            [(0, {"dy": -1080}, "out"), (0.45, {}, "hold"), (3.9, {}, "in"), (4.4, {"dy": -1080})])
    t.solid(t.track("shape", "Mitad"), CORAL, 0.0, 4.5, Box(960, 0, 960, 1080),
            [(0, {"dy": 1080}, "out"), (0.45, {}, "hold"), (3.9, {}, "in"), (4.4, {"dy": 1080})])
    line(t, t.track("shape", "Divisor"), WHITE, 0.45, 3.4, Box(956, 180, 8, 720), grow="y", length=0.4,
         opacity=keys([(0, 1.0, "hold"), (3.1, 1.0, "smooth"), (3.4, 0.0)]))
    for i, (w, x, y, c, at) in enumerate([("MENOS", 60, 290, WHITE, 0.6), ("EXCUSAS", 60, 520, TEAL, 1.0),
                                          ("MÁS", 1020, 290, NAVY, 1.4), ("ACCIÓN", 1020, 520, WHITE, 1.8)]):
        word(t, t.track("text", "Palabra"), w, at, 3.8 - at, Box(x, y, 840, 240), "Anton", 190, c, slam=1.3,
             land=0.14, spacing=4, anim_out=tanim("fade", duration=0.25), name=f"Palabra {i + 1}")
    pulses(t, [0.6, 1.0, 1.4, 1.8], 0.2)
    song(t, "electro", 3)
    return t


def cin_rebote():
    t = _kit("cinetico-rebote", "Palabras que rebotan", "Bouncing words", KIN, 4.0, 7406,
             ["cinético", "rebote", "divertido", "palabras"], thumb_at=2.6, background=SUN)
    bg(t, SUN)
    for i, (x, y, s, c) in enumerate([(260, 220, 60, NAVY), (1660, 260, 44, CORAL), (1580, 860, 70, NAVY),
                                      (340, 860, 40, CORAL)]):
        t.solid(t.track("shape", "Adorno"), c, 0.2 + i * 0.1, 3.8 - i * 0.1, centered(x, y, s, s),
                [(0, {"dy": -300, "s": 0.4}, "in"), (0.35, {}, "out"), (0.6, {"dy": -60}, "in"), (0.85, {}, "out"),
                 (1.05, {"dy": -20}, "in"), (1.2, {})], kind="ellipse")
    label(t, t.track("text", "Línea 1"), "¡ESTO SE PONE", 0.3, 3.7, Box(160, 250, 1600, 200), "Archivo Black", 150,
          NAVY, weight=400, anim_in=tanim("im-bounce-drop", unit="word", stagger=0.14), name="Línea 1")
    t.solid(t.track("shape", "Placa"), NAVY, 1.05, 2.95, centered(960, 640, 820, 250),
            [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.7, {"s": 1.04}, "smooth"), (1.0, {})],
            radius=36, kind="rounded-rectangle", rotation=keys([(0, -3)]),
            layers=[shadow("#000000", 0, 14, 0, 0.18), fill(NAVY), no_stroke()])
    label(t, t.track("text", "Línea 2"), "BUENO!", 1.25, 2.75, centered(960, 640, 820, 250), "Archivo Black", 180,
          SUN, weight=400, anim_in=tanim("pop", unit="character", stagger=0.06, duration=0.35), rotation=keys([(0, -3)]),
          name="Línea 2")
    pulses(t, [1.05, 1.25], 0.2)
    song(t, "fun", 0)
    return t


def cin_maquina():
    t = _kit("cinetico-maquina", "Máquina de escribir", "Typewriter title", KIN, 5.0, 7407,
             ["cinético", "máquina de escribir", "texto", "tutorial"], thumb_at=3.6, background=DEEP)
    bg(t, DEEP)
    pill(t, t.track("shape", "Etiqueta"), TEAL, 0.2, 4.8, Box(260, 250, 210, 56), pop(0, 0.35))
    label(t, t.track("text", "Etiqueta"), "PASO 01", 0.3, 4.7, Box(260, 250, 210, 56), "Inter", 28, NAVY, weight=800,
          spacing=4, name="Etiqueta")
    label(t, t.track("text", "Texto"), "Hoy te enseño\nalgo que nadie\nte contó.", 0.6, 4.4, Box(260, 340, 1400, 480),
          "Sora", 96, WHITE, weight=700, align="left", valign="top", line=1.18,
          anim_in=tanim("typewriter", stagger=0.06, caret=True, hold=0.8), name="Texto")
    line(t, t.track("shape", "Subrayado"), SUN, 3.0, 2.0, Box(262, 772, 470, 12), grow="x", length=0.4)
    song(t, "jazz", 1)
    return t


def cin_grande_chico():
    t = _kit("cinetico-grande-chico", "Grande y pequeño", "Big-small rhythm", KIN, 4.5, 7408,
             ["cinético", "tipografía", "contraste", "palabras"], thumb_at=2.6, background=NAVY)
    bg(t, NAVY)
    rows = [("el", 150, 110, False, 0.2), ("SECRETO", 250, 290, True, 0.6), ("que nadie te", 540, 110, False, 1.1),
            ("CUENTA", 640, 290, True, 1.5)]
    for i, (w, y, h, big, at) in enumerate(rows):
        if big:
            word(t, t.track("text", "Palabra"), w, at, 4.5 - at, Box(160, y, 1600, h), "Anton", 260,
                 WHITE if i == 1 else CORAL, slam=1.5, land=0.14, spacing=8, name=f"Palabra {i + 1}")
        else:
            label(t, t.track("text", "Palabra"), w, at, 4.5 - at, Box(160, y, 1600, h), "Playfair Display", 90,
                  MIST if i == 0 else TEAL, weight=400, italic=True, anim_in=tanim("fade-up-char", duration=0.4),
                  name=f"Palabra {i + 1}")
    line(t, t.track("shape", "Línea"), TEAL, 1.2, 3.3, Box(440, 597, 220, 4), grow="c", length=0.4)
    line(t, t.track("shape", "Línea"), TEAL, 1.2, 3.3, Box(1260, 597, 220, 4), grow="c", length=0.4)
    pulses(t, [0.6, 1.5], 0.25)
    song(t, "cine", 0)
    return t


def cin_claro():
    t = _kit("cinetico-claro", "Cinético claro", "Light kinetic title", KIN, 4.0, 7409,
             ["cinético", "claro", "minimalista", "palabras"], thumb_at=3.0, background=LIGHT)
    bg(t, LIGHT)
    # Line 1: UNA IDEA (909) + gap 40 + SIMPLE on a coral bar (679 + 40); line 2: LO CAMBIA (1052) + 50 + TODO (539).
    x1, x2 = 125, 139
    word(t, t.track("text", "Palabra"), "UNA IDEA", 0.3, 3.7, Box(x1, 290, 1250, 220), "Montserrat", 170, NAVY,
         weight=900, slam=1.25, land=0.12, grow=0.0, align="left", name="Palabra 1")
    bar_x = x1 + 909 + 40
    line(t, t.track("shape", "Marcador"), CORAL, 0.8, 3.2, Box(bar_x, 302, 720, 196), grow="x", length=0.3)
    label(t, t.track("text", "Palabra"), "SIMPLE", 0.95, 3.05, Box(bar_x, 290, 720, 220), "Montserrat", 170, WHITE,
          weight=900, anim_in=tanim("wipe", duration=0.4, angle=0, softness=0.1), name="Palabra 2")
    word(t, t.track("text", "Palabra"), "LO CAMBIA", 1.5, 2.5, Box(x2, 540, 1400, 220), "Montserrat", 170, NAVY,
         weight=900, slam=1.25, land=0.12, grow=0.0, align="left", name="Palabra 3")
    todo_cx = x2 + 1052 + 50 + 270
    word(t, t.track("text", "Palabra"), "TODO", 1.9, 2.1, centered(todo_cx, 650, 800, 220), "Montserrat", 170, NAVY,
         weight=900, slam=0.5, land=0.2, grow=0.0, name="Palabra 4")
    line(t, t.track("shape", "Subrayado"), SUN, 2.15, 1.85, Box(todo_cx - 270, 772, 540, 26), grow="x", length=0.35)
    for i, (x, y, c) in enumerate([(160, 200, TEAL), (1760, 880, CORAL), (1780, 190, SUN)]):
        t.solid(t.track("shape", "Adorno"), c, 0.4 + i * 0.3, 3.6 - i * 0.3, centered(x, y, 40, 40), pop(0, 0.35),
                kind="ellipse")
    pulses(t, [0.3, 0.95, 1.5, 1.9], 0.15)
    song(t, "upbeat", 2)
    return t


def cin_foto():
    t = _kit("cinetico-foto", "Palabras sobre tu video", "Words over your video", KIN, 5.0, 7410,
             ["cinético", "palabras", "foto", "viaje", "ritmo"], thumb_at=4.0)
    photo_bg(t, "h-travel-02", s1=1.12, label="Tu video")
    shade_full(t, 0.45)
    texto = t.track("text", "Palabra")
    for i, (w, at) in enumerate([("VIAJA.", 0.3), ("COME.", 1.2), ("REPITE.", 2.1)]):
        word(t, texto, w, at, 0.9, Box(160, 300, 1600, 480), "Anton", 280, WHITE, slam=1.6, land=0.14,
             layers=[shadow("#000000", 0, 8, 24, 0.5), fill(WHITE)], spacing=6, name=f"Palabra {i + 1}")
        flash(t, at, 0.2, peak=0.18)
    t.solid(t.track("shape", "Barra"), TEAL, 3.0, 1.8, Box(375, 640, 1170, 10),
            [(0, {"sx": 0.0}, "out"), (0.4, {}, "hold"), (1.3, {}, "in"), (1.7, {"sx": 0.0})])
    label(t, t.track("text", "Frase"), "VIAJA · COME · REPITE", 3.1, 1.6, Box(160, 470, 1600, 170), "Anton", 130,
          WHITE, weight=400, valign="bottom", line=1.0, layers=[shadow("#000000", 0, 6, 18, 0.5), fill(WHITE)],
          anim_in=tanim("wipe", duration=0.45, angle=-90, softness=0.1), anim_out=tanim("fade", duration=0.3),
          name="Frase")
    label(t, t.track("text", "Detalle"), "diario de viaje · capítulo 3", 3.4, 1.3, Box(160, 666, 1600, 60), "Inter",
          40, WHITE, weight=600, valign="top", spacing=6,
          anim_in=tanim("wipe", duration=0.45, angle=90, softness=0.1), anim_out=tanim("fade", duration=0.3),
          name="Detalle")
    pulses(t, [0.3, 1.2, 2.1, 3.1], 0.25)
    song(t, "upbeat", 0)
    return t


def cin_barras():
    t = _kit("cinetico-barras", "Palabras en barras", "Words on bars", KIN, 4.5, 7411,
             ["cinético", "barras", "lista", "palabras", "pasos"], thumb_at=2.4, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    for i, (w, wd, c) in enumerate([("APRENDE", 870, TEAL), ("PRACTICA", 922, CORAL), ("DOMINA", 757, SUN)]):
        at = 0.3 + i * 0.45
        y = 160 + i * 270
        bw = wd + 150
        end = 4.3 - at - (2 - i) * 0.1          # the bars leave one after another, last in first out
        out = end - 0.4                        # bar and word leave together
        t.solid(t.track("shape", "Barra"), c, at, end, Box(330, y, bw, 225),
                [(0, {"sx": 0.0, "dx": -bw / 2}, "out"), (0.35, {}, "hold"), (out, {}, "inout"),
                 (end, {"sx": 0.0, "dx": -bw / 2})])
        label(t, t.track("text", "Palabra"), w, at + 0.2, end - 0.2, Box(405, y, wd + 50, 225), "Montserrat",
              165, NAVY, weight=900, align="left", anim_in=tanim("wipe", duration=0.45, angle=0, softness=0.1),
              anim_out=tanim("fade", duration=0.35), name=f"Palabra {i + 1}")
        label(t, t.track("text", "Número"), f"0{i + 1}", at + 0.3, end - 0.4, Box(130, y, 170, 225), "Sora", 80,
              c, weight=800, align="right", anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.15),
              name=f"Número {i + 1}")
    pulses(t, [0.3, 0.75, 1.2], 0.18)
    song(t, "upbeat", 4)
    return t


# --- vertical ------------------------------------------------------------------------------------

def cin_cortes_v():
    t = _tall("cinetico-cortes-vertical", "Cortes de color vertical", "Colour-cut words (vertical)", KIN, 4.0, 7440,
              ["cinético", "palabras", "ritmo", "cortes"], thumb_at=2.9, background=NAVY)
    fondo = t.track("shape", "Fondo")
    texto = t.track("text", "Palabra")
    for i, (w, back, ink) in enumerate([("NO", NAVY, WHITE), ("TE", CORAL, WHITE), ("LO", TEAL, NAVY),
                                         ("PIERDAS", SUN, NAVY)]):
        at = i * 0.5
        t.solid(fondo, back, at, 0.5)
        word(t, texto, w, at, 0.5, Box(40, 560, 1000, 800), "Anton", 300 if i < 3 else 230, ink,
             slam=1.4 if i < 3 else 1.3, land=0.12, name=f"Palabra {i + 1}")
    t.solid(fondo, NAVY, 2.0, 2.0)
    word(t, t.track("text", "Frase"), "NO TE LO", 2.0, 2.0, Box(60, 640, 960, 240), "Anton", 190, WHITE, slam=1.4,
         land=0.14, spacing=4, name="Frase 1")
    word(t, t.track("text", "Frase"), "PIERDAS", 2.25, 1.75, Box(60, 870, 960, 300), "Anton", 230, TEAL, slam=1.3,
         land=0.14, spacing=4, name="Frase 2")
    line(t, t.track("shape", "Subrayado"), CORAL, 2.55, 1.45, Box(340, 1190, 400, 16), grow="c", length=0.35)
    burst(t, WHITE, 2.25, 540, 960, 600, width=10, length=0.7)
    pulses(t, [0.0, 0.5, 1.0, 1.5, 2.0, 2.25])
    song(t, "electro", 0)
    return t


def cin_grande_chico_v():
    t = _tall("cinetico-grande-chico-vertical", "Grande y pequeño vertical", "Big-small rhythm (vertical)", KIN, 4.5,
              7441, ["cinético", "tipografía", "contraste"], thumb_at=2.6, background=NAVY)
    bg(t, NAVY)
    rows = [("el", 560, 110, False, 0.2), ("SECRETO", 660, 250, True, 0.6), ("que nadie te", 910, 110, False, 1.1),
            ("CUENTA", 1010, 250, True, 1.5)]
    for i, (w, y, h, big, at) in enumerate(rows):
        if big:
            word(t, t.track("text", "Palabra"), w, at, 4.5 - at, Box(40, y, 1000, h), "Anton", 220,
                 WHITE if i == 1 else CORAL, slam=1.35, land=0.14, spacing=6, name=f"Palabra {i + 1}")
        else:
            label(t, t.track("text", "Palabra"), w, at, 4.5 - at, Box(40, y, 1000, h), "Playfair Display", 84,
                  MIST if i == 0 else TEAL, weight=400, italic=True, anim_in=tanim("fade-up-char", duration=0.4),
                  name=f"Palabra {i + 1}")
    line(t, t.track("shape", "Línea"), TEAL, 1.2, 3.3, Box(110, 963, 180, 4), grow="c", length=0.4)
    line(t, t.track("shape", "Línea"), TEAL, 1.2, 3.3, Box(790, 963, 180, 4), grow="c", length=0.4)
    pulses(t, [0.6, 1.5], 0.25)
    song(t, "cine", 0)
    return t


def cin_foto_v():
    t = _tall("cinetico-foto-vertical", "Palabras sobre tu video vertical", "Words over your video (vertical)", KIN,
              5.0, 7442, ["cinético", "palabras", "foto", "viaje"], thumb_at=4.0)
    photo_bg(t, "travel-01", s1=1.12, label="Tu video")
    shade_full(t, 0.4)
    texto = t.track("text", "Palabra")
    for i, (w, at) in enumerate([("SUBE.", 0.3), ("RESPIRA.", 1.2), ("MIRA.", 2.1)]):
        word(t, texto, w, at, 0.9, Box(40, 660, 1000, 600), "Anton", 210, WHITE, slam=1.4, land=0.14,
             layers=[shadow("#000000", 0, 8, 24, 0.5), fill(WHITE)], spacing=4, name=f"Palabra {i + 1}")
        flash(t, at, 0.2, peak=0.18)
    t.solid(t.track("shape", "Barra"), TEAL, 3.0, 1.8, Box(140, 1000, 800, 10),
            [(0, {"sx": 0.0}, "out"), (0.4, {}, "hold"), (1.3, {}, "in"), (1.7, {"sx": 0.0})])
    label(t, t.track("text", "Frase"), "SUBE · RESPIRA\nMIRA", 3.1, 1.6, Box(60, 640, 960, 360), "Anton", 150, WHITE,
          weight=400, valign="bottom", line=1.0, layers=[shadow("#000000", 0, 6, 18, 0.5), fill(WHITE)],
          anim_in=tanim("wipe", duration=0.5, angle=-90, softness=0.1), anim_out=tanim("fade", duration=0.3),
          name="Frase")
    label(t, t.track("text", "Detalle"), "ruta del día · parte 2", 3.4, 1.3, Box(60, 1026, 960, 70), "Inter", 44,
          WHITE, weight=600, valign="top", spacing=4,
          anim_in=tanim("wipe", duration=0.45, angle=90, softness=0.1), anim_out=tanim("fade", duration=0.3),
          name="Detalle")
    pulses(t, [0.3, 1.2, 2.1, 3.1], 0.25)
    song(t, "upbeat", 5)
    return t


# ================================================================================================
# Frases
# ================================================================================================

def fra_editorial():
    t = _kit("frase-editorial", "Frase editorial clara", "Light editorial quote", QUO, 6.0, 7600,
             ["frase", "cita", "editorial", "claro", "elegante"], thumb_at=3.8, background=LIGHT)
    bg(t, LIGHT)
    line(t, t.track("shape", "Línea"), NAVY, 0.2, 5.8, Box(160, 220, 1600, 4), grow="c", length=0.7)
    t.solid(t.track("shape", "Corte"), LIGHT, 0.2, 5.8, centered(960, 222, 230, 30))
    label(t, t.track("text", "Comillas"), "“", 0.5, 5.5, centered(960, 270, 300, 330), "Playfair Display", 340, CORAL,
          weight=700, anim_in=tanim("pop", duration=0.4), editable=False, name="Comillas")
    label(t, t.track("text", "Frase"), "El talento te abre la puerta;\nla constancia te mantiene dentro.", 0.8, 5.2,
          Box(120, 330, 1680, 380), "Playfair Display", 100, NAVY, weight=400, line=1.25,
          anim_in=tanim("rise-by-word", duration=1.6), name="Frase")
    line(t, t.track("shape", "Línea"), NAVY, 0.3, 5.7, Box(160, 760, 1600, 4), grow="c", length=0.7)
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.4, 3.6, Box(160, 800, 1600, 70), "Inter", 44, NAVY,
          weight=700, spacing=14, layers=[fill(NAVY, 0.6)], anim_in=tanim("fade", duration=0.6), name="Autor")
    song(t, "classic", 0)
    return t


def fra_foto():
    t = _kit("frase-foto", "Frase sobre foto", "Quote over a photo", QUO, 6.0, 7601,
             ["frase", "cita", "foto", "inspiración"], thumb_at=3.8)
    photo_bg(t, "h-nature-02", s1=1.1, label="Tu foto o video")
    shade_full(t, 0.55)
    label(t, t.track("text", "Frase"), "No tienes que verlo todo;\nsolo el siguiente paso.", 0.5, 5.2,
          Box(120, 230, 1680, 430), "Cormorant Garamond", 140, WHITE, weight=600, italic=True, line=1.1,
          layers=[shadow("#000000", 0, 6, 24, 0.45), fill(WHITE)], anim_in=tanim("blur-in", duration=1.2),
          anim_out=tanim("fade", duration=0.4), name="Frase")
    t.solid(t.track("shape", "Línea"), CORAL, 1.6, 4.1, Box(870, 720, 180, 8),
            [(0, {"sx": 0.0}, "out"), (0.5, {}, "hold"), (3.7, {}, "in"), (4.1, {"sx": 0.0})])
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 1.9, 3.7, Box(160, 760, 1600, 70), "Inter", 46, WHITE,
          weight=700, spacing=14, valign="top", anim_in=tanim("wipe", duration=0.5, angle=90, softness=0.1),
          anim_out=tanim("fade", duration=0.4), name="Autor")
    song(t, "calm", 1)
    return t


def fra_palabra():
    t = _kit("frase-palabra", "Una palabra y una frase", "Big word and quote", QUO, 6.0, 7602,
             ["frase", "cita", "palabra", "tipografía"], thumb_at=3.8, background=DEEP)
    bg(t, DEEP)
    label(t, t.track("text", "Palabra"), "CALMA", 0.2, 5.8, Box(120, 90, 1680, 460), "Anton", 380, TEAL,
          weight=400, spacing=40, anim_in=tanim("tracking-drift", duration=1.4), name="Palabra")
    line(t, t.track("shape", "Línea"), CORAL, 1.0, 5.0, Box(890, 575, 140, 8), grow="c", length=0.4)
    label(t, t.track("text", "Frase"), "Lo que se hace con calma\nse hace dos veces bien.", 1.2, 4.8,
          Box(120, 610, 1680, 290), "Playfair Display", 86, WHITE, weight=400, italic=True, line=1.2,
          anim_in=tanim("rise-by-word", duration=1.2), name="Frase")
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.6, 3.4, Box(160, 910, 1600, 60), "Inter", 40, MIST,
          weight=700, spacing=14, anim_in=tanim("fade", duration=0.5), name="Autor")
    song(t, "calm", 0)
    return t


def fra_testimonio():
    t = _kit("frase-testimonio", "Testimonio", "Testimonial", QUO, 6.0, 7603,
             ["frase", "testimonio", "opinión", "reseña", "cliente"], thumb_at=3.8, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=120)
    circle_photo(t, "portrait-04", 0.3, 5.7, centered(420, 540, 480, 480), pop(0, 0.5), ring_colour=TEAL,
                 ring_width=14, label="Foto de la persona")
    for i in range(5):
        t.solid(t.track("shape", "Estrella"), SUN, 0.8 + i * 0.08, 5.2 - i * 0.08,
                centered(782 + i * 92, 290, 72, 72), pop(0, 0.35), kind="star")
    label(t, t.track("text", "Frase"), "“Este canal me cambió\nla forma de cocinar.”", 1.0, 5.0,
          Box(740, 340, 1100, 280), "Sora", 76, WHITE, weight=700, align="left", line=1.2,
          anim_in=tanim("rise-by-word", duration=1.0), name="Frase")
    line(t, t.track("shape", "Línea"), CORAL, 1.8, 4.2, Box(744, 660, 12, 150), grow="y", length=0.3)
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 2.0, 4.0, Box(786, 650, 1050, 86), "Sora", 60, TEAL,
          weight=800, align="left", anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15), name="Nombre")
    label(t, t.track("text", "Detalle"), "suscriptora desde 2024", 2.2, 3.8, Box(786, 734, 1050, 66), "Inter", 44,
          MIST, weight=500, align="left", anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          name="Detalle")
    song(t, "upbeat", 7)
    return t


def fra_minimal():
    t = _kit("frase-minimal", "Frase minimalista", "Minimal quote", QUO, 6.0, 7604,
             ["frase", "cita", "minimalista", "oscuro"], thumb_at=3.8, background=DEEP)
    bg(t, DEEP)
    label(t, t.track("text", "Frase"), "Menos ruido, más trabajo.", 0.4, 5.6, Box(120, 380, 1680, 190), "Sora", 104,
          WHITE, weight=600, anim_in=tanim("fade-up-char", duration=1.2), name="Frase")
    line(t, t.track("shape", "Línea"), TEAL, 1.4, 4.6, Box(810, 610, 300, 5), grow="c", length=0.6)
    t.solid(t.track("shape", "Punto"), TEAL, 1.7, 4.3, centered(960, 668, 18, 18), pop(0, 0.3), kind="ellipse")
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 1.9, 4.1, Box(160, 705, 1600, 70), "Inter", 42, MIST,
          weight=600, spacing=18, anim_in=tanim("fade", duration=0.6), name="Autor")
    song(t, "calm", 2)
    return t


def fra_mitad():
    t = _kit("frase-mitad", "Frase con foto a un lado", "Half-photo quote", QUO, 6.0, 7605,
             ["frase", "cita", "foto", "entrevista"], thumb_at=3.8, background=NAVY)
    bg(t, NAVY)
    t.photo(t.track("video", "Foto"), "h-portrait-01", 0.0, 6.0, Box(0, 0, 700, 1080),
            [(0, {"dx": -700}, "out"), (0.6, {}, "linear"), (6.0, {"s": 1.05})], label="Tu foto")
    line(t, t.track("shape", "Borde"), TEAL, 0.5, 5.5, Box(700, 0, 12, 1080), grow="y", length=0.5)
    label(t, t.track("text", "Comillas"), "“", 0.8, 5.2, Box(780, 70, 400, 380), "Playfair Display", 440, TEAL,
          weight=700, align="left", anim_in=tanim("pop", duration=0.4), editable=False, name="Comillas")
    label(t, t.track("text", "Frase"), "Cada día es una página.\nEscríbela como si\nfuera la mejor.", 1.0, 5.0,
          Box(800, 340, 1060, 400), "Playfair Display", 80, WHITE, weight=600, align="left", line=1.2,
          anim_in=tanim("rise-by-word", duration=1.4), name="Frase")
    line(t, t.track("shape", "Línea"), CORAL, 2.4, 3.6, Box(806, 812, 120, 8), grow="x", length=0.3)
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.6, 3.4, Box(950, 781, 900, 70), "Inter", 42, MIST,
          weight=700, align="left", spacing=12, anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          name="Autor")
    song(t, "calm", 3)
    return t


def fra_cursiva():
    t = _kit("frase-cursiva", "Frase en cursiva", "Italic serif quote", QUO, 6.0, 7606,
             ["frase", "cita", "elegante", "cursiva", "amor"], thumb_at=3.8, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    dots(t, [SUN, WHITE], 16, 0.0, 6.0, seed=3, size=(4, 9), drift=40, alpha=0.4)
    label(t, t.track("text", "Frase"), "Hazlo con amor\no no lo hagas.", 0.4, 5.6, Box(120, 150, 1680, 520),
          "Cormorant Garamond", 190, WHITE, weight=400, italic=True, line=1.0,
          anim_in=tanim("fade-up-char", duration=1.8), name="Frase")
    t.solid(t.track("shape", "Adorno"), SUN, 2.0, 4.0, centered(960, 740, 28, 28), pop(0, 0.35), kind="diamond")
    line(t, t.track("shape", "Línea"), SUN, 2.1, 3.9, Box(640, 739, 280, 3), grow="c", length=0.5)
    line(t, t.track("shape", "Línea"), SUN, 2.1, 3.9, Box(1000, 739, 280, 3), grow="c", length=0.5)
    label(t, t.track("text", "Autor"), "Autor de la frase", 2.4, 3.6, Box(160, 785, 1600, 90), "Cormorant Garamond",
          70, SUN, weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Autor")
    song(t, "romantic", 0)
    return t


def fra_marco():
    t = _kit("frase-marco", "Frase enmarcada", "Framed quote", QUO, 6.0, 7607,
             ["frase", "cita", "marco", "moderno"], thumb_at=3.8, background=DEEP)
    bg(t, DEEP)
    outline(t, t.track("shape", "Marco"), TEAL, 6, 0.2, 5.8, Box(110, 160, 1700, 780),
            [(0, {"s": 1.05}, "out"), (0.7, {})], opacity=keys([(0, 0.0, "smooth"), (0.5, 1.0)]))
    t.solid(t.track("shape", "Corte"), DEEP, 0.2, 5.8, centered(960, 163, 260, 40))
    label(t, t.track("text", "Comillas"), "“", 0.6, 5.4, centered(960, 225, 260, 300), "Playfair Display", 300, TEAL,
          weight=700, anim_in=tanim("pop", duration=0.4), editable=False, name="Comillas")
    label(t, t.track("text", "Frase"), "Cree en ti antes\nde que nadie más lo haga.", 0.9, 5.1,
          Box(180, 350, 1560, 380), "Sora", 100, WHITE, weight=600, line=1.2,
          anim_in=tanim("rise-by-word", duration=1.2), name="Frase")
    t.solid(t.track("shape", "Corte"), DEEP, 2.2, 3.8, centered(960, 937, 760, 40))
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.3, 3.7, centered(960, 937, 740, 70), "Inter", 42, CORAL,
          weight=800, spacing=14, anim_in=tanim("fade", duration=0.5), name="Autor")
    song(t, "calm", 4)
    return t


def fra_coral():
    t = _kit("frase-coral", "Frase coral", "Coral quote card", QUO, 6.0, 7608,
             ["frase", "cita", "color", "motivación"], thumb_at=3.8, background=CORAL)
    bg(t, CORAL)
    label(t, t.track("text", "Comillas"), "“", 0.2, 5.8, Box(120, 0, 600, 560), "Playfair Display", 700, NAVY,
          weight=900, align="left", layers=[fill(NAVY, 0.9)], anim_in=tanim("pop", duration=0.5), editable=False,
          name="Comillas")
    label(t, t.track("text", "Frase"), "Crecer duele menos\nque quedarse igual.", 0.6, 5.4, Box(200, 340, 1640, 400),
          "Sora", 132, WHITE, weight=800, align="left", line=1.1, anim_in=tanim("rise-by-word", duration=1.2),
          name="Frase")
    line(t, t.track("shape", "Línea"), NAVY, 2.0, 4.0, Box(206, 812, 140, 12), grow="x", length=0.3)
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.2, 3.8, Box(376, 783, 1300, 70), "Inter", 46, NAVY,
          weight=800, align="left", spacing=12, anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          name="Autor")
    song(t, "upbeat", 5)
    return t


def fra_sol():
    t = _kit("frase-sol", "Frase amarilla", "Sun quote card", QUO, 6.0, 7609,
             ["frase", "cita", "color", "motivación", "fuerte"], thumb_at=3.8, background=SUN)
    bg(t, SUN)
    for i, (x, y, s) in enumerate([(170, 150, 100), (1750, 930, 130), (1740, 140, 60)]):
        ring(t, t.track("shape", "Adorno"), NAVY, 9, 0.3 + i * 0.15, 5.7 - i * 0.15, centered(x, y, s, s),
             pop(0, 0.4))
    label(t, t.track("text", "Frase"), "SI NO TE DA MIEDO,\nNO ES TAN GRANDE.", 0.4, 5.6, Box(120, 270, 1680, 400),
          "Archivo Black", 130, NAVY, weight=400, line=1.12,
          anim_in=tanim("pop", unit="word", stagger=0.12, duration=0.4), name="Frase")
    t.solid(t.track("shape", "Marcador"), CORAL, 1.6, 4.4, Box(760, 712, 400, 20),
            [(0, {"sx": 0.0}, "out"), (0.4, {})])
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.0, 4.0, Box(160, 760, 1600, 70), "Inter", 46, NAVY,
          weight=800, spacing=14, anim_in=tanim("fade", duration=0.5), name="Autor")
    song(t, "upbeat", 6)
    return t


def fra_leccion():
    t = _kit("frase-leccion", "Lección numerada", "Numbered lesson quote", QUO, 6.0, 7610,
             ["frase", "lección", "consejo", "número", "tutorial"], thumb_at=3.8, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    label(t, t.track("text", "Etiqueta"), "LECCIÓN", 0.2, 5.8, Box(110, 170, 600, 80), "Inter", 50, MIST, weight=700,
          align="right", spacing=20, anim_in=tanim("fade", duration=0.5), name="Etiqueta")
    word(t, t.track("text", "Número"), "03", 0.3, 5.7, Box(60, 230, 660, 640), "Anton", 560, TEAL, slam=0.6,
         land=0.4, grow=0.03, align="right", name="Número")
    line(t, t.track("shape", "Línea"), CORAL, 0.7, 5.3, Box(770, 220, 12, 640), grow="y", length=0.5)
    label(t, t.track("text", "Frase"), "Lo que no se mide\nno se puede mejorar.", 1.1, 4.9, Box(830, 330, 1010, 300),
          "Playfair Display", 96, WHITE, weight=600, align="left", line=1.2,
          anim_in=tanim("wipe", duration=0.8, angle=0, softness=0.15), name="Frase")
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 1.9, 4.1, Box(834, 660, 1000, 70), "Inter", 42, MIST,
          weight=700, align="left", spacing=12, anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          name="Autor")
    song(t, "calm", 3)
    return t


def fra_tarjeta():
    t = _kit("frase-tarjeta", "Tarjeta de frase sobre video", "Quote card over video", QUO, 6.0, 7611,
             ["frase", "cita", "tarjeta", "foto", "superposición"], thumb_at=3.6)
    photo_bg(t, "h-nature-05", s1=1.08, label="Tu video")
    shade_full(t, 0.3)
    card = [(0, {"dy": 140, "s": 0.96}, "out"), (0.6, {}, "hold"), (4.7, {}, "in"), (5.2, {"dy": 140, "s": 0.96})]
    fade = keys([(0, 0.0, "smooth"), (0.4, 1.0, "hold"), (4.8, 1.0, "smooth"), (5.2, 0.0)])
    rrect(t, t.track("shape", "Tarjeta"), WHITE, 0.4, 5.2, Box(200, 190, 1520, 760), radius=40, motion=card,
          layers=[shadow("#000000", 0, 24, 60, 0.35), fill(WHITE), no_stroke()], opacity=fade)
    t.solid(t.track("shape", "Insignia"), CORAL, 0.7, 4.7, centered(960, 190, 150, 150), pop(0, 0.4),
            kind="ellipse", opacity=keys([(0, 1.0, "hold"), (4.3, 1.0, "smooth"), (4.6, 0.0)]))
    label(t, t.track("text", "Comillas"), "“", 0.8, 4.5, centered(960, 225, 150, 170), "Playfair Display", 190, WHITE,
          weight=700, editable=False, anim_out=tanim("fade", duration=0.3), name="Comillas")
    label(t, t.track("text", "Frase"), "Las montañas no se suben\ncon prisa, se suben\ncon ganas.", 1.0, 4.3,
          Box(260, 300, 1400, 420), "Playfair Display", 86, NAVY, weight=600, line=1.2,
          anim_in=tanim("rise-by-word", duration=1.2), anim_out=tanim("fade", duration=0.3), name="Frase")
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.0, 3.3, Box(260, 790, 1400, 70), "Inter", 42, CORAL,
          weight=800, spacing=14, anim_in=tanim("fade", duration=0.5), anim_out=tanim("fade", duration=0.3),
          name="Autor")
    song(t, "calm", 4)
    return t


# --- vertical ------------------------------------------------------------------------------------

def fra_editorial_v():
    t = _tall("frase-editorial-vertical", "Frase editorial clara vertical", "Light editorial quote (vertical)", QUO,
              6.0, 7640, ["frase", "cita", "editorial", "claro"], thumb_at=3.8, background=LIGHT)
    bg(t, LIGHT)
    line(t, t.track("shape", "Línea"), NAVY, 0.2, 5.8, Box(140, 620, 800, 3), grow="c", length=0.7)
    t.solid(t.track("shape", "Corte"), LIGHT, 0.2, 5.8, centered(540, 621, 150, 20))
    label(t, t.track("text", "Comillas"), "“", 0.5, 5.5, centered(540, 650, 200, 220), "Playfair Display", 220, CORAL,
          weight=700, anim_in=tanim("pop", duration=0.4), editable=False, name="Comillas")
    label(t, t.track("text", "Frase"), "El talento\nte abre la puerta;\nla constancia\nte mantiene dentro.", 0.8, 5.2,
          Box(90, 740, 900, 440), "Playfair Display", 76, NAVY, weight=400, line=1.3,
          anim_in=tanim("rise-by-word", duration=1.6), name="Frase")
    line(t, t.track("shape", "Línea"), NAVY, 0.3, 5.7, Box(140, 1240, 800, 3), grow="c", length=0.7)
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.4, 3.6, Box(90, 1275, 900, 50), "Inter", 30, NAVY,
          weight=700, spacing=10, layers=[fill(NAVY, 0.6)], anim_in=tanim("fade", duration=0.6), name="Autor")
    song(t, "classic", 0)
    return t


def fra_foto_v():
    t = _tall("frase-foto-vertical", "Frase sobre foto vertical", "Quote over a photo (vertical)", QUO, 6.0, 7641,
              ["frase", "cita", "foto", "inspiración"], thumb_at=3.8)
    photo_bg(t, "nature-04", s1=1.1, label="Tu foto o video")
    shade_full(t, 0.45)
    label(t, t.track("text", "Frase"), "No tienes\nque verlo todo;\nsolo el\nsiguiente paso.", 0.5, 5.2,
          Box(80, 620, 920, 520), "Cormorant Garamond", 108, WHITE, weight=600, italic=True, line=1.1,
          layers=[shadow("#000000", 0, 4, 18, 0.4), fill(WHITE)], anim_in=tanim("blur-in", duration=1.2),
          anim_out=tanim("fade", duration=0.4), name="Frase")
    t.solid(t.track("shape", "Línea"), CORAL, 1.6, 4.1, Box(480, 1190, 120, 6),
            [(0, {"sx": 0.0}, "out"), (0.5, {}, "hold"), (3.7, {}, "in"), (4.1, {"sx": 0.0})])
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 1.9, 3.7, Box(80, 1220, 920, 50), "Inter", 32, WHITE,
          weight=700, spacing=10, valign="top", anim_in=tanim("wipe", duration=0.5, angle=90, softness=0.1),
          anim_out=tanim("fade", duration=0.4), name="Autor")
    song(t, "calm", 1)
    return t


def fra_testimonio_v():
    t = _tall("frase-testimonio-vertical", "Testimonio vertical", "Testimonial (vertical)", QUO, 6.0, 7642,
              ["frase", "testimonio", "opinión", "reseña"], thumb_at=3.8, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=120)
    circle_photo(t, "h-man-01", 0.3, 5.7, centered(540, 560, 400, 400), pop(0, 0.5), ring_colour=TEAL, ring_width=10,
                 label="Foto de la persona")
    for i in range(5):
        t.solid(t.track("shape", "Estrella"), SUN, 0.8 + i * 0.08, 5.2 - i * 0.08, centered(416 + i * 62, 840, 50, 50),
                pop(0, 0.35), kind="star")
    label(t, t.track("text", "Frase"), "“Por fin entendí\nlas finanzas\nde mi negocio.”", 1.0, 5.0,
          Box(90, 910, 900, 330), "Sora", 72, WHITE, weight=700, line=1.2,
          anim_in=tanim("rise-by-word", duration=1.0), name="Frase")
    line(t, t.track("shape", "Línea"), CORAL, 1.8, 4.2, Box(490, 1290, 100, 6), grow="c", length=0.3)
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 2.0, 4.0, Box(90, 1320, 900, 70), "Sora", 46, TEAL,
          weight=800, anim_in=tanim("fade", duration=0.5), name="Nombre")
    label(t, t.track("text", "Detalle"), "cliente desde 2023", 2.2, 3.8, Box(90, 1390, 900, 56), "Inter", 34, MIST,
          weight=500, anim_in=tanim("fade", duration=0.5), name="Detalle")
    song(t, "upbeat", 7)
    return t


TEMPLATES = [cin_cortes, cin_escala, cin_pila, cin_contador, cin_linea, cin_dividida, cin_rebote, cin_maquina,
             cin_grande_chico, cin_claro, cin_foto, cin_barras, cin_cortes_v, cin_grande_chico_v, cin_foto_v,
             fra_editorial, fra_foto, fra_palabra, fra_testimonio, fra_minimal, fra_mitad, fra_cursiva, fra_marco,
             fra_coral, fra_sol, fra_leccion, fra_tarjeta, fra_editorial_v, fra_foto_v, fra_testimonio_v]
