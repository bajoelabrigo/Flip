"""Kit de YouTube (2026-10-30): prototypes, one per section of the kit (Aperturas, Tipografía, Títulos con estilo,
Títulos cinéticos, Tercios inferiores, Frases, Transiciones, Barras de información, Pantallas finales, Redes sociales,
Elementos). 1920x1080. Our own designs and palette (turquoise / navy / coral / sun), no platform logos or platform
red. Every text is editable and every picture a slot; the background is its own «Fondo» track so it can be deleted
and the piece laid over the user's video. Category ytkit; order 7000-7099; ids `ytk-*`. The section of each one
goes in the first tag (`kit:<section>`).
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, dots, effect, fill, flash, glow, gradient, keys,
                 label, line, no_stroke, outline, panels, photo_bg, pill, pop, ring, rrect, shade_bottom, shade_full,
                 shadow, slide_in, song, spike, tanim, wide)

NAVY = "#0B1A2E"
DEEP = "#06101F"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MIST = "#A9B8CC"


def _kit(id, es, en, section, duration, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", duration, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


# 1 Aperturas -------------------------------------------------------------------------------------

def apertura_hexagono():
    t = _kit("apertura-hexagono", "Apertura hexágono", "Hexagon opener", "aperturas", 5.0, 7000,
             ["intro", "canal", "logo", "apertura"], thumb_at=3.0, background=NAVY)
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    dots(t, [TEAL, WHITE, MIST], 22, 0.0, 5.0, seed=7, size=(5, 12), drift=50, alpha=0.6)
    for i, (c, d) in enumerate([(TEAL, 0.0), (CORAL, 0.12)]):
        ring(t, t.track("shape", "Onda"), c, 6, 0.5 + d, 1.2, centered(560, 540, 300, 300),
             [(0, {"s": 0.6}, "out"), (1.2, {"s": 2.6})], opacity=keys([(0, 1.0), (1.2, 0.0)]))
    hexa = t.track("shape", "Hexágono")
    t.solid(hexa, TEAL, 0.3, 4.7, centered(560, 540, 320, 320),
            [(0, {"s": 0.0}, "back"), (0.55, {})], kind="hexagon",
            layers=[shadow("#000000", 0, 16, 40, 0.45), fill(TEAL), no_stroke()],
            rotation=keys([(0, -90, "out"), (0.7, 0)]))
    t.photo(t.track("video", "Logo"), "logo-07", 0.6, 4.4, centered(560, 540, 190, 190), pop(0, 0.45),
            label="Tu logo")
    bar = t.track("shape", "Barra")
    line(t, bar, TEAL, 1.0, 4.0, Box(780, 470, 8, 140), grow="y", length=0.35)
    label(t, t.track("text", "Canal"), "TU CANAL", 1.2, 3.8, Box(820, 440, 1000, 130), "Sora", 104, WHITE,
          weight=800, align="left", spacing=4,
          anim_in=tanim("wipe", duration=0.6, angle=0, softness=0.15), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 1.6, 3.4, Box(824, 570, 1000, 60), "Inter", 40,
          MIST, weight=500, align="left", spacing=2, anim_in=tanim("fade", duration=0.5), name="Lema")
    song(t, "upbeat", 1)
    return t


# 2 Tipografía ------------------------------------------------------------------------------------

def tipografia_bloque():
    t = _kit("tipografia-bloque", "Bloque tipográfico", "Type block", "tipografia", 4.5, 7010,
             ["título", "texto", "tipografía", "minimalista"], thumb_at=2.4, background=DEEP)
    bg(t, DEEP)
    line(t, t.track("shape", "Línea"), WHITE, 0.2, 4.1, Box(560, 400, 800, 3), grow="c", length=0.5)
    line(t, t.track("shape", "Línea"), WHITE, 0.3, 4.0, Box(560, 680, 800, 3), grow="c", length=0.5)
    label(t, t.track("text", "Antetítulo"), "NUEVO VIDEO", 0.5, 3.8, Box(560, 420, 800, 50), "Inter", 30, TEAL,
          weight=700, spacing=16, anim_in=tanim("tracking-drift", duration=1.0), name="Antetítulo")
    label(t, t.track("text", "Título"), "TU GRAN TÍTULO", 0.7, 3.6, Box(460, 470, 1000, 150), "Anton", 132, WHITE,
          weight=400, spacing=6, anim_in=tanim("wipe", duration=0.6), anim_out=tanim("fade", duration=0.4),
          name="Título")
    label(t, t.track("text", "Detalle"), "capítulo 01 · temporada 2", 1.2, 3.1, Box(560, 625, 800, 50), "Inter", 30,
          MIST, weight=400, spacing=4, anim_in=tanim("fade", duration=0.5), name="Detalle")
    return t


# 3 Títulos con estilo ----------------------------------------------------------------------------

def titulo_barras():
    t = _kit("titulo-barras", "Título con barras", "Slash title", "titulos-estilo", 5.0, 7020,
             ["título", "canal", "estilo", "foto"], thumb_at=2.6)
    photo_bg(t, "h-travel-03", s1=1.08, label="Tu foto o video")
    shade_full(t, 0.3)
    for i in range(3):
        t.solid(t.track("shape", "Barra"), TEAL if i < 2 else CORAL, 0.3 + i * 0.08, 4.4 - i * 0.08,
                Box(330 + i * 46, 430, 22, 140), slide_in(dy=-60, length=0.35), rotation=keys([(0, 20)]))
    label(t, t.track("text", "Título"), "TU CANAL", 0.6, 4.2, Box(500, 410, 1200, 130), "Montserrat", 110, WHITE,
          weight=900, align="left", spacing=2, layers=[shadow("#000000", 0, 6, 18, 0.5), fill(WHITE)],
          anim_in=tanim("wipe", duration=0.6, angle=0, softness=0.15), name="Título")
    rrect(t, t.track("shape", "Etiqueta"), TEAL, 1.0, 3.8, Box(504, 548, 420, 54), radius=6,
          motion=[(0, {"sx": 0.0, "dx": -210}, "out"), (0.4, {})])
    label(t, t.track("text", "Subtítulo"), "POR TU NOMBRE", 1.2, 3.6, Box(504, 548, 420, 54), "Inter", 28, NAVY,
          weight=800, spacing=8, anim_in=tanim("fade", duration=0.3), name="Subtítulo")
    return t


# 4 Títulos cinéticos -----------------------------------------------------------------------------

def titulo_cinetico():
    t = _kit("titulo-cinetico", "Palabras al ritmo", "Kinetic words", "titulos-cineticos", 4.0, 7030,
             ["cinético", "palabras", "ritmo", "energía"], thumb_at=2.2, background=NAVY)
    words = [("HAZLO", NAVY, WHITE), ("HOY", CORAL, WHITE), ("MISMO", TEAL, NAVY), ("¡YA!", SUN, NAVY)]
    each = 1.0
    fondo = t.track("shape", "Fondo")
    texto = t.track("text", "Palabra")
    for i, (w, back, ink) in enumerate(words):
        at = i * each
        t.solid(fondo, back, at, each, None, [(0, {"dx": 0 if i == 0 else 1920}, "out"), (0.25, {})])
        label(t, texto, w, at + 0.08, each - 0.08, Box(160, 330, 1600, 420), "Anton", 340, ink, weight=400, spacing=4,
              anim_in=tanim("stamp", duration=0.3), name=f"Palabra {i + 1}")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.0, 1.0, 2.0, 3.0], 0.35, 0.25)})], name="Golpe")
    song(t, "electro", 0)
    return t


# 5 Tercios inferiores ----------------------------------------------------------------------------

def tercio_doble():
    t = _kit("tercio-doble", "Tercio inferior doble", "Two-line lower third", "tercios", 5.0, 7040,
             ["nombre", "rótulo", "entrevista", "tercio inferior"], thumb_at=2.4)
    photo_bg(t, "h-podcast-02", s1=1.05, label="Tu video")
    line(t, t.track("shape", "Acento"), TEAL, 0.3, 4.4, Box(120, 790, 12, 150), grow="y", length=0.3,
         opacity=keys([(0, 1.0, "hold"), (4.1, 1.0, "smooth"), (4.4, 0.0)]))
    rrect(t, t.track("shape", "Placa"), WHITE, 0.45, 4.2, Box(132, 790, 620, 90), radius=0,
          motion=[(0, {"sx": 0.0, "dx": -310}, "out"), (0.45, {}, "hold"), (3.85, {}, "in"), (4.2, {"sx": 0.0, "dx": -310})])
    rrect(t, t.track("shape", "Placa"), NAVY, 0.6, 4.0, Box(132, 880, 480, 60), radius=0,
          motion=[(0, {"sx": 0.0, "dx": -240}, "out"), (0.45, {}, "hold"), (3.65, {}, "in"), (4.0, {"sx": 0.0, "dx": -240})])
    label(t, t.track("text", "Nombre"), "Nombre Apellido", 0.75, 3.8, Box(160, 790, 600, 90), "Sora", 54, NAVY,
          weight=800, align="left", anim_in=tanim("slide-up", duration=0.4), anim_out=tanim("fade", duration=0.25),
          name="Nombre")
    label(t, t.track("text", "Cargo"), "Cargo o tema", 0.9, 3.6, Box(160, 880, 460, 60), "Inter", 32, TEAL,
          weight=600, align="left", spacing=2, anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.25), name="Cargo")
    return t


# 6 Frases ----------------------------------------------------------------------------------------

def frase_comillas():
    t = _kit("frase-comillas", "Frase con comillas", "Quote card", "frases", 6.0, 7050,
             ["frase", "cita", "motivación", "texto"], thumb_at=3.6, background=DEEP)
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=135)
    label(t, t.track("text", "Comillas"), "“", 0.2, 5.6, Box(260, 180, 300, 300), "Playfair Display", 380, TEAL,
          weight=700, anim_in=tanim("pop", duration=0.4), editable=False, name="Comillas")
    label(t, t.track("text", "Frase"), "Lo que haces cada día\nimporta más que lo que\nhaces de vez en cuando.",
          0.6, 5.2, Box(380, 340, 1200, 380), "Playfair Display", 70, WHITE, weight=600, align="left", line=1.2,
          anim_in=tanim("rise-by-word", duration=1.6), anim_out=tanim("fade", duration=0.4), name="Frase")
    line(t, t.track("shape", "Línea"), CORAL, 2.2, 3.6, Box(384, 760, 90, 6), grow="x", length=0.4)
    label(t, t.track("text", "Autor"), "AUTOR DE LA FRASE", 2.4, 3.4, Box(494, 738, 900, 50), "Inter", 30, MIST,
          weight=700, align="left", spacing=8, anim_in=tanim("fade", duration=0.5), name="Autor")
    song(t, "calm", 0)
    return t


# 7 Transiciones de formas ------------------------------------------------------------------------

def transicion_paneles():
    t = _kit("transicion-paneles", "Transición de paneles", "Panel wipe", "transiciones", 3.0, 7060,
             ["transición", "cortinilla", "formas", "cambio de escena"], thumb_at=1.35)
    trk = t.track("video", "Escenas")
    a = t.photo(trk, "h-city-02", 0.0, 1.45, None, [(0, {"s": 1.0}, "linear"), (1.45, {"s": 1.08})],
                label="Escena 1")
    b = t.photo(trk, "h-nature-03", 1.45, 1.55, None, [(0, {"s": 1.08}, "out"), (1.55, {"s": 1.0})],
                label="Escena 2")
    panels(t, [TEAL, NAVY, CORAL], 0.75, direction="left", length=0.55, hold=0.05, stagger=0.07, angle=-14)
    ring(t, t.track("shape", "Aro"), WHITE, 14, 1.35, 0.7, centered(960, 540, 200, 200),
         [(0, {"s": 0.2}, "out"), (0.7, {"s": 6.0})], opacity=keys([(0, 1.0), (0.7, 0.0)]))
    return t


# 8 Barras de información -------------------------------------------------------------------------

def barra_info():
    t = _kit("barra-info", "Barra de información", "Info bar", "barras-info", 6.0, 7070,
             ["barra", "información", "noticia", "rótulo"], thumb_at=2.8)
    photo_bg(t, "h-city-04", s1=1.05, label="Tu video")
    shade_bottom(t, 360, 0.6)
    rrect(t, t.track("shape", "Barra"), NAVY, 0.3, 5.4, Box(0, 900, 1920, 90), radius=0, alpha=0.92,
          motion=slide_in(dy=120, length=0.4))
    pill(t, t.track("shape", "Etiqueta"), CORAL, 0.6, 5.1, Box(80, 918, 200, 54), pop(0, 0.35))
    label(t, t.track("text", "Etiqueta"), "EN VIVO", 0.7, 5.0, Box(112, 918, 160, 54), "Inter", 28, WHITE,
          weight=800, spacing=4, name="Etiqueta")
    t.solid(t.track("shape", "Punto"), WHITE, 0.7, 5.0, centered(106, 945, 12, 12), kind="ellipse",
            opacity=blink(5.0, 1.0, 0.2))
    label(t, t.track("text", "Titular"), "Escribe aquí el titular de tu video", 0.9, 4.8, Box(310, 905, 1400, 80),
          "Sora", 44, WHITE, weight=700, align="left", anim_in=tanim("typewriter", duration=1.0), name="Titular")
    pill(t, t.track("shape", "Episodio"), TEAL, 0.8, 4.9, Box(1600, 70, 240, 60), slide_in(dx=300, length=0.4))
    label(t, t.track("text", "Episodio"), "EPISODIO 12", 0.9, 4.8, Box(1600, 70, 240, 60), "Inter", 28, NAVY,
          weight=800, spacing=3, name="Episodio")
    return t


# 9 Pantallas finales -----------------------------------------------------------------------------

def pantalla_final():
    t = _kit("pantalla-final", "Pantalla final con dos videos", "Two-video end screen", "pantallas-finales", 12.0,
             7080, ["pantalla final", "suscríbete", "cierre", "siguiente video"], thumb_at=3.0, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=120)
    dots(t, [TEAL, MIST], 18, 0.0, 12.0, seed=21, size=(4, 10), drift=80, alpha=0.5)
    label(t, t.track("text", "Gracias"), "¡GRACIAS POR VER!", 0.3, 11.7, Box(160, 110, 1600, 110), "Sora", 78, WHITE,
          weight=800, spacing=4, anim_in=tanim("rise-by-word", duration=0.7), name="Gracias")
    # The YouTube end-screen elements go on these frames: two videos on the left, subscribe on the right.
    for i, (x, sample, cap) in enumerate([(160, "h-travel-05", "VIDEO SIGUIENTE"), (160, "h-food-02", "TE PUEDE GUSTAR")]):
        y = 300 + i * 360
        rrect(t, t.track("shape", "Marco"), TEAL, 0.6 + i * 0.2, 11.4 - i * 0.2, Box(x - 8, y - 8, 556, 316), radius=18,
              motion=slide_in(dx=-80, length=0.5))
        clip = t.photo(t.track("video", "Video"), sample, 0.6 + i * 0.2, 11.4 - i * 0.2, Box(x, y, 540, 300),
                       slide_in(dx=-80, length=0.5), label=f"Video {i + 1}")
        pill(t, t.track("shape", "Rótulo"), NAVY, 0.9 + i * 0.2, 11.1 - i * 0.2, Box(x + 24, y + 228, 300, 50))
        label(t, t.track("text", "Rótulo"), cap, 0.9 + i * 0.2, 11.1 - i * 0.2, Box(x + 24, y + 228, 300, 50), "Inter",
              24, WHITE, weight=800, spacing=3, name=f"Rótulo {i + 1}")
    ring(t, t.track("shape", "Aro"), TEAL, 10, 1.0, 11.0, centered(1360, 560, 340, 340), pop(0, 0.5))
    t.photo(t.track("video", "Logo"), "logo-07", 1.1, 10.9, centered(1360, 560, 200, 200), pop(0, 0.5), label="Tu logo")
    pill(t, t.track("shape", "Botón"), CORAL, 1.5, 10.5, Box(1170, 790, 380, 80), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "SUSCRÍBETE", 1.6, 10.4, Box(1170, 790, 380, 80), "Sora", 38, WHITE,
          weight=800, spacing=4, anim_loop=tanim("pulse"), name="Botón")
    song(t, "upbeat", 3)
    return t


# 10 Redes sociales -------------------------------------------------------------------------------

def redes_lista():
    t = _kit("redes-lista", "Tus redes", "Social handles", "redes", 6.0, 7090,
             ["redes", "sígueme", "usuario", "contacto"], thumb_at=3.0, background=DEEP)
    bg(t, DEEP)
    label(t, t.track("text", "Título"), "SÍGUEME", 0.2, 5.6, Box(360, 230, 1200, 110), "Anton", 100, WHITE,
          weight=400, spacing=12, anim_in=tanim("wipe", duration=0.5), name="Título")
    rows = [(TEAL, "@", "@tuusuario"), (CORAL, "♪", "/tucanal"), (SUN, "#", "tusitio.com")]
    for i, (c, glyph, handle) in enumerate(rows):
        at, y = 0.6 + i * 0.25, 400 + i * 150
        t.solid(t.track("shape", "Icono"), c, at, 5.4 - i * 0.25, centered(700, y + 50, 96, 96), pop(0, 0.4),
                kind="ellipse")
        label(t, t.track("text", "Icono"), glyph, at + 0.05, 5.35 - i * 0.25, centered(700, y + 50, 96, 96), "Inter",
              52, DEEP, weight=900, name=f"Icono {i + 1}")
        label(t, t.track("text", "Usuario"), handle, at + 0.15, 5.25 - i * 0.25, Box(780, y + 10, 900, 80), "Sora",
              56, WHITE, weight=700, align="left", anim_in=tanim("slide-right", duration=0.4),
              name=f"Usuario {i + 1}")
    return t


# 11 Elementos ------------------------------------------------------------------------------------

def elementos_set():
    t = _kit("elementos-set", "Elementos animados", "Animated elements", "elementos", 4.0, 7095,
             ["elementos", "formas", "adornos", "gráficos"], thumb_at=1.8, background=DEEP)
    bg(t, DEEP)
    # Slashes
    for i in range(3):
        t.solid(t.track("shape", "Barras"), TEAL, 0.2 + i * 0.08, 3.6, Box(300 + i * 50, 280, 22, 150),
                slide_in(dy=-50, length=0.3), rotation=keys([(0, 22)]))
    # Ring that draws and pulses
    ring(t, t.track("shape", "Aro"), CORAL, 12, 0.4, 3.4, centered(960, 355, 180, 180),
         [(0, {"s": 0.0}, "back"), (0.5, {}, "smooth"), (1.6, {"s": 1.12}, "smooth"), (2.7, {})])
    # Three dots that blink in turn
    for i in range(3):
        t.solid(t.track("shape", "Puntos"), SUN, 0.5 + i * 0.15, 3.3, centered(1500 + i * 60, 355, 34, 34),
                pop(0, 0.3), kind="ellipse", opacity=blink(3.3, 0.6 + i * 0.1, 0.25))
    # Cross that spins
    t.solid(t.track("shape", "Cruz"), WHITE, 0.6, 3.2, centered(450, 760, 110, 110), pop(0, 0.4), kind="cross",
            rotation=keys([(0, 0, "linear"), (3.2, 180)]))
    # Arrow that nudges
    t.solid(t.track("shape", "Flecha"), TEAL, 0.7, 3.1, centered(960, 760, 220, 110),
            [(0, {"dx": -60}, "out"), (0.4, {}, "smooth"), (1.0, {"dx": 30}, "smooth"), (1.6, {}, "smooth"),
             (2.2, {"dx": 30}, "smooth"), (2.8, {})], kind="arrow")
    # Underline that draws itself
    line(t, t.track("shape", "Subrayado"), CORAL, 0.8, 3.0, Box(1350, 755, 320, 12), grow="x", length=0.5)
    return t


TEMPLATES = [apertura_hexagono, tipografia_bloque, titulo_barras, titulo_cinetico, tercio_doble, frase_comillas,
             transicion_paneles, barra_info, pantalla_final, redes_lista, elementos_set]
