"""Horizontal batch 2 (2026-10-16): lower thirds, text scenes and first endings, 1920x1080.
See BRIEF.md, «Las 400 nuevas». Categories lowerthird, text, outro; order 2100-2199.

A lower third sits over a full-frame slot («Tu video»), comes in at 0.5 s, holds and leaves before the
end, so it can be dropped over any shot and trimmed.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, line, math, no_stroke, outline, photo_bg, pill, pop,
                 random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides, song, spike,
                 stroke, tanim, vignette, wide)

IN, OUT = 0.5, 5.2  # lower third on screen


def _lt(id, es, en, sample, order, tags, duration=6.0, thumb_at=2.6, shade=420):
    t = wide(id, es, en, "lowerthird", duration, order=order, tags=["tercio inferior", "rótulo", "nombre"] + tags,
             thumb_at=thumb_at)
    photo_bg(t, sample, s1=1.05, label="Tu video")
    if shade:
        shade_bottom(t, shade, 0.55)
    return t


def _out(dur_from_in: float = OUT - IN, length: float = 0.35, dx: float = 0, dy: float = 0) -> list:
    """Motion that holds and then leaves (for clips that start at IN and end at OUT)."""
    return [(0, {}, "hold"), (dur_from_in - length, {}, "in"), (dur_from_in, {"dx": dx, "dy": dy})]


def _inout(dx_in=0, dy_in=0, dx_out=0, dy_out=0, length=0.45, dur=OUT - IN, ease="out"):
    return [(0, {"dx": dx_in, "dy": dy_in}, ease), (length, {}, "hold"), (dur - 0.35, {}, "in"),
            (dur, {"dx": dx_out, "dy": dy_out})]


# --- Lower thirds -------------------------------------------------------------------------------

def tercio_minimal_linea():
    t = _lt("h-tercio-minimal-linea", "Tercio minimal", "Minimal lower third", "h-man-01", 2100, ["minimal", "limpio"])
    line(t, t.track("shape", "Línea"), "#FFFFFF", IN, OUT - IN, Box(140, 800, 6, 150), grow="y", length=0.4)
    label(t, t.track("text", "Nombre"), "Daniel Ortega", IN + 0.2, OUT - IN - 0.2, Box(175, 790, 1000, 90), "Montserrat",
          66, "#FFFFFF", weight=700, align="left", anim_in=tanim("slide-right", duration=0.5, distance=0.2),
          anim_out=tanim("fade", duration=0.3), name="Nombre")
    label(t, t.track("text", "Cargo"), "Arquitecto · Estudio Norte", IN + 0.4, OUT - IN - 0.4, Box(178, 880, 1000, 60),
          "Montserrat", 36, "#E6E6E6", weight=400, align="left", spacing=2, anim_in=tanim("fade", duration=0.5),
          anim_out=tanim("fade", duration=0.3), name="Cargo")
    song(t, "calm", 0, 0.6)
    return t


def tercio_caja_color():
    t = _lt("h-tercio-caja-color", "Tercio en caja", "Boxed lower third", "h-portrait-02", 2101, ["caja", "color"],
            shade=0)
    t.solid(t.track("shape", "Caja"), "#FFD23F", IN, OUT - IN, Box(120, 760, 760, 120), _inout(dx_in=-900, dx_out=-900))
    t.solid(t.track("shape", "Caja"), "#111111", IN + 0.15, OUT - IN - 0.15, Box(120, 880, 560, 72),
            _inout(dx_in=-900, dx_out=-900, dur=OUT - IN - 0.15))
    label(t, t.track("text", "Nombre"), "Lucía Fernández", IN + 0.25, OUT - IN - 0.25, Box(150, 760, 720, 120),
          "Poppins", 62, "#111111", weight=800, align="left", anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Nombre")
    label(t, t.track("text", "Cargo"), "Fotógrafa de viajes", IN + 0.35, OUT - IN - 0.35, Box(150, 880, 520, 72),
          "Poppins", 34, "#FFFFFF", weight=500, align="left", anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Cargo")
    song(t, "upbeat", 1, 0.6)
    return t


def tercio_duotono():
    t = _lt("h-tercio-duotono", "Tercio duotono", "Duotone lower third", "h-office-04", 2102, ["duotono", "moderno"],
            shade=0)
    t.solid(t.track("shape", "Acento"), "#00C2A8", IN, OUT - IN, Box(120, 780, 150, 150),
            [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (OUT - IN - 0.3, {}, "in"), (OUT - IN, {"s": 0.0})])
    t.solid(t.track("shape", "Bloque"), "#1B1F3B", IN + 0.2, OUT - IN - 0.2, Box(270, 780, 760, 150),
            [(0, {"sx": 0.0, "dx": -380}, "out"), (0.45, {}, "hold"), (OUT - IN - 0.55, {}, "in"),
             (OUT - IN - 0.2, {"sx": 0.0, "dx": -380})])
    label(t, t.track("text", "Inicial"), "R", IN + 0.1, OUT - IN - 0.1, Box(120, 780, 150, 150), "Archivo Black", 96,
          "#1B1F3B", weight=400, anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2),
          name="Inicial")
    label(t, t.track("text", "Nombre"), "RAÚL MENDOZA", IN + 0.45, OUT - IN - 0.6, Box(305, 790, 720, 80),
          "Archivo Black", 54, "#FFFFFF", weight=400, align="left", spacing=2, anim_in=tanim("slide-right", duration=0.4),
          anim_out=tanim("fade", duration=0.2), name="Nombre")
    label(t, t.track("text", "Cargo"), "Director de marketing", IN + 0.55, OUT - IN - 0.7, Box(305, 862, 720, 54),
          "Inter", 34, "#00C2A8", weight=600, align="left", anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.2), name="Cargo")
    song(t, "upbeat", 2, 0.6)
    return t


def tercio_redondeado():
    t = _lt("h-tercio-redondeado", "Tercio con foto", "Rounded lower third with photo", "h-cafe-02", 2103,
            ["foto", "píldora", "perfil"], shade=0)
    pill(t, t.track("shape", "Píldora"), "#FFFFFF", IN, OUT - IN, Box(110, 790, 820, 160), _inout(dy_in=260, dy_out=260),
         layers=[shadow("#000000", 0, 10, 30, 0.35), fill("#FFFFFF"), no_stroke()])
    circle_photo(t, "h-man-02", IN + 0.15, OUT - IN - 0.15, centered(190, 870, 130, 130),
                 _inout(dy_in=260, dy_out=260, dur=OUT - IN - 0.15), label="Foto de perfil")
    label(t, t.track("text", "Nombre"), "Tomás Rivera", IN + 0.3, OUT - IN - 0.3, Box(280, 800, 620, 80), "Poppins", 56,
          "#1A1A2E", weight=700, align="left", anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.2),
          name="Nombre")
    label(t, t.track("text", "Cargo"), "Dueño · Café del Puerto", IN + 0.4, OUT - IN - 0.4, Box(282, 872, 620, 60),
          "Poppins", 34, "#7A7A8C", weight=500, align="left", anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Cargo")
    song(t, "jazz", 0, 0.6)
    return t


def tercio_noticias():
    t = _lt("h-tercio-noticias", "Rótulo de noticias", "News lower third", "h-city-06", 2104,
            ["noticias", "en vivo", "titular", "cinta"], duration=8.0, thumb_at=3.0, shade=0)
    dur = 8.0 - IN
    t.solid(t.track("shape", "Titular"), "#FFFFFF", IN, dur, Box(0, 820, 1920, 120), slide_in(dx=-1920, length=0.4))
    t.solid(t.track("shape", "Cinta"), "#0A1B3D", IN + 0.1, dur - 0.1, Box(0, 940, 1920, 70), slide_in(dx=1920, length=0.4))
    t.solid(t.track("shape", "En vivo"), "#E10600", IN + 0.3, dur - 0.3, Box(60, 760, 260, 70), pop(0, 0.3))
    label(t, t.track("text", "En vivo"), "EN VIVO", IN + 0.3, dur - 0.3, Box(60, 760, 260, 70), "Oswald", 44, "#FFFFFF",
          weight=700, spacing=6, anim_loop=tanim("flicker", intensity=0.25, speed=1.5), name="Etiqueta")
    label(t, t.track("text", "Titular"), "Gran feria del libro abre sus puertas este fin de semana", IN + 0.45,
          dur - 0.45, Box(60, 820, 1700, 120), "Oswald", 62, "#0A1B3D", weight=600, align="left",
          anim_in=tanim("slide-up", duration=0.4), name="Titular")
    label(t, t.track("text", "Cinta"), "ÚLTIMAS NOTICIAS  •  El clima: soleado, 24 °C  •  Deportes: mañana la final  •  "
          "Cultura: nueva exposición en el museo  •", IN + 0.5, dur - 0.5, Box(0, 940, 4200, 70), "Oswald", 38, "#FFFFFF",
          weight=500, align="left", spacing=2, motion=[(0, {"dx": 1900}, "linear"), (dur - 0.5, {"dx": -1500})],
          name="Cinta de noticias")
    t.solid(t.track("shape", "Reloj"), "#E10600", IN + 0.1, dur - 0.1, Box(1700, 940, 220, 70), slide_in(dx=300, length=0.4))
    label(t, t.track("text", "Hora"), "18:45", IN + 0.2, dur - 0.2, Box(1700, 940, 220, 70), "Oswald", 42, "#FFFFFF",
          weight=700, name="Hora")
    song(t, "epic", 5, 0.5)
    return t


def tercio_corporativo():
    t = _lt("h-tercio-corporativo", "Rótulo corporativo", "Corporate lower third", "h-office-05", 2105,
            ["corporativo", "empresa", "logo"], shade=0)
    rrect(t, t.track("shape", "Panel"), "#FFFFFF", IN, OUT - IN, Box(110, 790, 900, 160), 14,
          _inout(dx_in=-1100, dx_out=-1100), layers=[shadow("#000000", 0, 10, 26, 0.3), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Logo"), "logo-01", IN + 0.25, OUT - IN - 0.25, centered(200, 870, 130, 130),
            _inout(dx_in=-1100, dx_out=-1100, dur=OUT - IN - 0.25), label="Tu logo")
    t.solid(t.track("shape", "Divisor"), "#1E66F5", IN + 0.35, OUT - IN - 0.35, Box(290, 815, 4, 110),
            [(0, {"sy": 0.0}, "out"), (0.3, {}, "hold"), (OUT - IN - 0.65, {}, "in"), (OUT - IN - 0.35, {"sy": 0.0})])
    label(t, t.track("text", "Nombre"), "Mariana Costa", IN + 0.4, OUT - IN - 0.4, Box(320, 800, 680, 80), "Montserrat",
          54, "#0B3D91", weight=800, align="left", anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.2),
          name="Nombre")
    label(t, t.track("text", "Cargo"), "Gerente general · Grupo Norte", IN + 0.5, OUT - IN - 0.5, Box(322, 872, 680, 60),
          "Montserrat", 32, "#4A5568", weight=500, align="left", anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Cargo")
    song(t, "upbeat", 3, 0.55)
    return t


def tercio_redes():
    t = _lt("h-tercio-redes", "Tercio de redes", "Social handle lower third", "h-portrait-06", 2106,
            ["redes sociales", "usuario", "sígueme"], shade=0)
    pill(t, t.track("shape", "Píldora"), "#111111", IN, OUT - IN, Box(120, 840, 640, 110),
         [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (OUT - IN - 0.3, {}, "in"), (OUT - IN, {"s": 0.0})],
         layers=[shadow("#000000", 0, 8, 20, 0.35), fill("#111111", 0.9), no_stroke()])
    t.solid(t.track("shape", "Icono"), "#FF3CAC", IN + 0.15, OUT - IN - 0.15, centered(185, 895, 80, 80),
            pop(0, 0.4), kind="rounded-rectangle", radius=22,
            layers=[gradient([(0, "#FFC371"), (0.5, "#FF3CAC"), (1, "#784BA0")], angle=45), no_stroke()])
    ring(t, t.track("shape", "Icono"), "#FFFFFF", 6, IN + 0.2, OUT - IN - 0.2, centered(185, 895, 40, 40), pop(0, 0.4))
    label(t, t.track("text", "Usuario"), "@lauraviaja", IN + 0.3, OUT - IN - 0.3, Box(245, 840, 500, 110), "Poppins", 52,
          "#FFFFFF", weight=700, align="left", anim_in=tanim("typewriter", duration=0.6, unit="character"),
          anim_out=tanim("fade", duration=0.2), name="Usuario")
    song(t, "upbeat", 4, 0.55)
    return t


def tercio_ubicacion():
    t = _lt("h-tercio-ubicacion", "Ubicación", "Location lower third", "h-travel-08", 2107,
            ["ubicación", "lugar", "viaje", "ciudad"])
    pin = t.track("shape", "Pin")
    t.solid(pin, "#FF4D4D", IN, OUT - IN, centered(170, 830, 70, 70), [(0, {"dy": -300}, "back"), (0.5, {})],
            kind="ellipse")
    t.solid(t.track("shape", "Pin"), "#FF4D4D", IN, OUT - IN, centered(170, 870, 44, 44),
            [(0, {"dy": -300}, "back"), (0.5, {})], kind="triangle", rotation=keys([(0, 180)]))
    t.solid(t.track("shape", "Pin"), "#FFFFFF", IN, OUT - IN, centered(170, 830, 26, 26),
            [(0, {"dy": -300}, "back"), (0.5, {})], kind="ellipse")
    label(t, t.track("text", "Ciudad"), "Ruta 66", IN + 0.3, OUT - IN - 0.3, Box(230, 770, 1200, 120), "Bebas Neue", 110,
          "#FFFFFF", weight=400, align="left", spacing=6, layers=[shadow("#000000", 0, 4, 14, 0.5), fill("#FFFFFF")],
          anim_in=tanim("slide-right", duration=0.4, unit="character", stagger=0.03), anim_out=tanim("fade", duration=0.3),
          name="Lugar")
    line(t, t.track("shape", "Línea"), "#FF4D4D", IN + 0.5, OUT - IN - 0.5, Box(234, 892, 300, 6), length=0.5)
    label(t, t.track("text", "País"), "ARIZONA · ESTADOS UNIDOS", IN + 0.6, OUT - IN - 0.6, Box(234, 905, 1000, 60),
          "Montserrat", 34, "#FFFFFF", weight=600, align="left", spacing=6, anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.3), name="Región")
    song(t, "world", 3, 0.55)
    return t


def tercio_entrevista():
    t = _lt("h-tercio-entrevista", "Entrevista", "Interview lower third", "h-podcast-04", 2108,
            ["entrevista", "pregunta", "invitado"], shade=480)
    label(t, t.track("text", "Pregunta"), "«¿Cómo empezó todo?»", IN, OUT - IN, Box(120, 700, 1400, 90),
          "Playfair Display", 58, "#FFFFFF", weight=500, italic=True, align="left", anim_in=tanim("fade", duration=0.5),
          anim_out=tanim("fade", duration=0.3), name="Pregunta")
    t.solid(t.track("shape", "Caja"), "#F2C14E", IN + 0.3, OUT - IN - 0.3, Box(120, 810, 640, 100),
            _inout(dx_in=-760, dx_out=-760, dur=OUT - IN - 0.3))
    label(t, t.track("text", "Nombre"), "Javier Soto", IN + 0.45, OUT - IN - 0.45, Box(145, 810, 600, 100), "Oswald", 60,
          "#1B1B1B", weight=700, align="left", anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.2),
          name="Nombre")
    label(t, t.track("text", "Cargo"), "chef y fundador de La Huerta", IN + 0.55, OUT - IN - 0.55, Box(124, 918, 900, 60),
          "Oswald", 36, "#FFFFFF", weight=400, align="left", spacing=2, anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Cargo")
    song(t, "jazz", 1, 0.5)
    return t


def tercio_gaming():
    t = _lt("h-tercio-gaming", "Tercio gaming", "Gaming lower third", "h-gaming-02", 2109, ["gaming", "gamer", "neón"],
            shade=0)
    t.solid(t.track("shape", "Marco"), "#0B0014", IN, OUT - IN, Box(110, 800, 820, 140), _inout(dx_in=-1000, dx_out=-1000),
            kind="parallelogram", layers=[glow("#B026FF", 24, 0.9), fill("#0B0014", 0.9), stroke(3, "#B026FF")])
    t.solid(t.track("shape", "Acento"), "#08F7FE", IN + 0.15, OUT - IN - 0.15, Box(90, 800, 70, 140),
            _inout(dx_in=-1000, dx_out=-1000, dur=OUT - IN - 0.15), kind="parallelogram",
            layers=[glow("#08F7FE", 18, 0.9), fill("#08F7FE"), no_stroke()])
    label(t, t.track("text", "Gamer"), "SHADOWFOX", IN + 0.3, OUT - IN - 0.3, Box(190, 805, 700, 80), "Orbitron", 58,
          "#FFFFFF", weight=900, align="left", spacing=4, layers=[glow("#B026FF", 14, 0.8), fill("#FFFFFF")],
          anim_in=tanim("glitch-in", duration=0.4), anim_out=tanim("fade", duration=0.2), name="Nombre gamer")
    label(t, t.track("text", "Plataforma"), "▶ en vivo · todos los viernes", IN + 0.45, OUT - IN - 0.45,
          Box(195, 880, 700, 50), "Exo 2", 30, "#08F7FE", weight=700, align="left", anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Horario")
    song(t, "electro", 2, 0.55)
    return t


def tercio_elegante():
    t = _lt("h-tercio-elegante", "Tercio elegante", "Elegant lower third", "h-wedding-01", 2110,
            ["elegante", "dorado", "serif", "boda"])
    for y in (790, 960):
        line(t, t.track("shape", "Filete"), "#E8C27A", IN, OUT - IN, centered(560, y, 760, 2), grow="c", length=0.7)
    label(t, t.track("text", "Nombre"), "Isabel & Martín", IN + 0.3, OUT - IN - 0.3, Box(180, 800, 760, 110),
          "Playfair Display", 76, "#FFFFFF", weight=500, italic=True, anim_in=tanim("blur-in", duration=0.8, blur=12),
          anim_out=tanim("fade", duration=0.4), name="Nombres")
    label(t, t.track("text", "Detalle"), "PADRINOS DE BODA", IN + 0.6, OUT - IN - 0.6, Box(180, 905, 760, 50), "Cinzel",
          32, "#E8C27A", weight=500, spacing=10, anim_in=tanim("fade", duration=0.6), anim_out=tanim("fade", duration=0.4),
          name="Detalle")
    song(t, "romantic", 1, 0.55)
    return t


def tercio_a_mano():
    t = _lt("h-tercio-a-mano", "Tercio a mano", "Handwritten lower third", "h-family-03", 2111,
            ["a mano", "caligrafía", "familiar", "vlog"])
    label(t, t.track("text", "Nombre"), "la abuela Rosa", IN, OUT - IN, Box(130, 760, 1100, 140), "Caveat", 120,
          "#FFFFFF", weight=700, align="left", layers=[shadow("#000000", 0, 4, 12, 0.5), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.9, unit="character"), anim_out=tanim("fade", duration=0.3), name="Nombre")
    t.solid(t.track("shape", "Subrayado"), "#FFD166", IN + 0.8, OUT - IN - 0.8, Box(140, 905, 560, 14),
            [(0, {"sx": 0.0, "dx": -280}, "out"), (0.4, {})], radius=7, kind="rounded-rectangle",
            rotation=keys([(0, -1.5)]))
    label(t, t.track("text", "Detalle"), "← la mejor cocinera", IN + 1.0, OUT - IN - 1.0, Box(760, 860, 700, 90),
          "Caveat", 64, "#FFD166", weight=700, align="left", anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.3), name="Detalle")
    song(t, "calm", 2, 0.55)
    return t


def tercio_glass():
    t = _lt("h-tercio-glass", "Tercio de cristal", "Glass lower third", "h-nature-01", 2112,
            ["cristal", "translúcido", "moderno", "glass"], shade=0)
    rrect(t, t.track("shape", "Cristal"), "#FFFFFF", IN, OUT - IN, Box(120, 790, 820, 170), 28,
          [(0, {"s": 0.9, "dy": 40}, "out"), (0.5, {}, "hold"), (OUT - IN - 0.3, {}, "in"), (OUT - IN, {"s": 0.95, "dy": 30})],
          layers=[shadow("#000000", 0, 10, 30, 0.2), fill("#FFFFFF", 0.18),
                  {"id": "stroke", "kind": "stroke", "enabled": True, "width": 2, "strokeAlign": "inside",
                   "paint": {"kind": "solid", "color": "#66ffffff"}, "opacity": 1.0}],
          opacity=keys([(0, 0.0), (0.4, 1.0, "hold"), (OUT - IN - 0.3, 1.0), (OUT - IN, 0.0)]))
    label(t, t.track("text", "Nombre"), "Valeria Núñez", IN + 0.2, OUT - IN - 0.3, Box(160, 805, 760, 80), "Outfit", 58,
          "#FFFFFF", weight=700, align="left", anim_in=tanim("blur-in", duration=0.5), anim_out=tanim("fade", duration=0.3),
          name="Nombre")
    label(t, t.track("text", "Cargo"), "Bióloga marina", IN + 0.35, OUT - IN - 0.4, Box(162, 882, 760, 56), "Outfit", 36,
          "#E0F4FF", weight=400, align="left", anim_in=tanim("fade", duration=0.5), anim_out=tanim("fade", duration=0.3),
          name="Cargo")
    song(t, "calm", 3, 0.55)
    return t


def tercio_podcast():
    t = _lt("h-tercio-podcast", "Tercio de podcast", "Podcast lower third", "h-podcast-02", 2113,
            ["podcast", "episodio", "invitado"], shade=0)
    rrect(t, t.track("shape", "Panel"), "#1E1B2E", IN, OUT - IN, Box(110, 780, 980, 180), 24,
          _inout(dy_in=300, dy_out=300), layers=[shadow("#000000", 0, 10, 26, 0.4), fill("#1E1B2E", 0.95), no_stroke()])
    pill(t, t.track("shape", "Episodio"), "#FFB547", IN + 0.2, OUT - IN - 0.2, Box(140, 805, 190, 56),
         _inout(dy_in=300, dy_out=300, dur=OUT - IN - 0.2))
    label(t, t.track("text", "Episodio"), "EP. 24", IN + 0.25, OUT - IN - 0.25, Box(140, 805, 190, 56), "DM Sans", 32,
          "#1E1B2E", weight=800, spacing=2, anim_in=tanim("fade", duration=0.2), name="Episodio")
    label(t, t.track("text", "Micrófono"), "🎙", IN + 0.25, OUT - IN - 0.25, centered(1020, 870, 120, 120), "Inter", 70,
          "#FFFFFF", weight=400, editable=False, motion=pop(0, 0.4))
    label(t, t.track("text", "Título"), "Emprender sin miedo", IN + 0.35, OUT - IN - 0.35, Box(350, 795, 640, 80),
          "DM Serif Display", 54, "#FFFFFF", weight=400, align="left", anim_in=tanim("fade", duration=0.3),
          name="Título del episodio")
    label(t, t.track("text", "Invitado"), "con Sara Molina, fundadora de Brote", IN + 0.45, OUT - IN - 0.45,
          Box(142, 880, 860, 60), "DM Sans", 34, "#FFB547", weight=500, align="left", anim_in=tanim("fade", duration=0.3),
          name="Invitado")
    song(t, "jazz", 2, 0.5)
    return t


def tercio_deportes():
    t = _lt("h-tercio-deportes", "Tercio deportivo", "Sports lower third", "h-soccer-02", 2114,
            ["deportes", "jugador", "fútbol", "dorsal"], shade=0)
    t.solid(t.track("shape", "Dorsal"), "#E10600", IN, OUT - IN, Box(110, 770, 190, 200), _inout(dx_in=-500, dx_out=-500),
            kind="parallelogram")
    t.solid(t.track("shape", "Nombre"), "#FFFFFF", IN + 0.1, OUT - IN - 0.1, Box(260, 790, 760, 110),
            _inout(dx_in=-1100, dx_out=-1100, dur=OUT - IN - 0.1), kind="parallelogram")
    t.solid(t.track("shape", "Puesto"), "#111111", IN + 0.2, OUT - IN - 0.2, Box(250, 900, 520, 60),
            _inout(dx_in=-1100, dx_out=-1100, dur=OUT - IN - 0.2), kind="parallelogram")
    label(t, t.track("text", "Número"), "10", IN + 0.2, OUT - IN - 0.2, Box(110, 770, 190, 200), "Anton", 130, "#FFFFFF",
          weight=400, anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Número")
    label(t, t.track("text", "Jugador"), "MATEO SILVA", IN + 0.35, OUT - IN - 0.35, Box(320, 790, 680, 110), "Anton", 74,
          "#111111", weight=400, align="left", spacing=2, anim_in=tanim("slide-right", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Jugador")
    label(t, t.track("text", "Puesto"), "DELANTERO · 23 AÑOS", IN + 0.45, OUT - IN - 0.45, Box(300, 900, 460, 60),
          "Barlow Condensed", 36, "#FFFFFF", weight=700, align="left", spacing=4, anim_in=tanim("fade", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Puesto")
    song(t, "epic", 1, 0.5)
    return t


def tercio_tutorial_paso():
    t = _lt("h-tercio-tutorial-paso", "Paso de tutorial", "Tutorial step", "h-desk-03", 2115,
            ["tutorial", "paso", "instrucciones", "educación"], shade=0)
    rrect(t, t.track("shape", "Panel"), "#FFFFFF", IN, OUT - IN, Box(110, 800, 980, 150), 75,
          _inout(dy_in=300, dy_out=300), layers=[shadow("#000000", 0, 10, 26, 0.3), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Número"), "#5B5BD6", IN + 0.2, OUT - IN - 0.2, centered(185, 875, 120, 120),
            pop(0, 0.4), kind="ellipse")
    label(t, t.track("text", "Número"), "2", IN + 0.25, OUT - IN - 0.25, centered(185, 875, 120, 120), "Poppins", 72,
          "#FFFFFF", weight=800, anim_in=tanim("pop", duration=0.3), name="Número de paso")
    label(t, t.track("text", "Paso"), "PASO 2 DE 5", IN + 0.35, OUT - IN - 0.35, Box(270, 815, 780, 50), "Poppins", 30,
          "#5B5BD6", weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.3), name="Paso")
    label(t, t.track("text", "Instrucción"), "Abre el menú y elige «Exportar»", IN + 0.45, OUT - IN - 0.45,
          Box(270, 860, 800, 70), "Poppins", 44, "#1A1A2E", weight=600, align="left", anim_in=tanim("fade", duration=0.3),
          name="Instrucción")
    for k in range(5):
        t.solid(t.track("shape", "Progreso"), "#5B5BD6" if k < 2 else "#D7D7F5", IN + 0.5 + k * 0.05, OUT - IN - 0.5,
                centered(905 + k * 34, 832, 20, 20), pop(0, 0.3),
                kind="ellipse")
    song(t, "upbeat", 5, 0.5)
    return t


def tercio_cita():
    t = _lt("h-tercio-cita", "Cita en pantalla", "On-screen quote", "h-elderly-01", 2116, ["cita", "frase", "testimonio"],
            shade=520)
    label(t, t.track("text", "Comillas"), "“", IN, OUT - IN, Box(110, 640, 200, 220), "Playfair Display", 260, "#F2C14E",
          weight=800, align="left", editable=False, anim_in=tanim("pop", duration=0.4))
    label(t, t.track("text", "Cita"), "La familia es donde la vida empieza y el amor nunca termina.", IN + 0.3,
          OUT - IN - 0.3, Box(250, 720, 1300, 170), "Playfair Display", 56, "#FFFFFF", weight=500, italic=True,
          align="left", anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.07),
          anim_out=tanim("fade", duration=0.4), name="Cita")
    label(t, t.track("text", "Autor"), "— Carmen, 82 años", IN + 1.2, OUT - IN - 1.2, Box(252, 900, 900, 60), "Montserrat",
          36, "#F2C14E", weight=600, align="left", spacing=2, anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.4), name="Autor")
    song(t, "romantic", 2, 0.5)
    return t


def tercio_precio():
    t = _lt("h-tercio-precio", "Precio en pantalla", "On-screen price", "h-product-03", 2117,
            ["precio", "producto", "oferta", "tienda"], shade=0)
    rrect(t, t.track("shape", "Panel"), "#111111", IN, OUT - IN, Box(110, 820, 760, 130), 18,
          _inout(dx_in=-900, dx_out=-900))
    label(t, t.track("text", "Producto"), "Lámpara Nórdica", IN + 0.2, OUT - IN - 0.2, Box(140, 828, 520, 70), "Montserrat",
          46, "#FFFFFF", weight=700, align="left", anim_in=tanim("fade", duration=0.3), name="Producto")
    label(t, t.track("text", "Detalle"), "madera de roble · envío gratis", IN + 0.3, OUT - IN - 0.3, Box(140, 890, 560, 50),
          "Montserrat", 28, "#BDBDBD", weight=500, align="left", anim_in=tanim("fade", duration=0.3), name="Detalle")
    t.solid(t.track("shape", "Precio"), "#FF5A1F", IN + 0.45, OUT - IN - 0.45, centered(850, 820, 260, 260),
            [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (OUT - IN - 0.75, {}, "in"), (OUT - IN - 0.45, {"s": 0.0})],
            kind="burst", points=16, innerRatio=0.85, rotation=keys([(0, 0, "linear"), (OUT - IN, 40)]))
    label(t, t.track("text", "Precio"), "$49", IN + 0.5, OUT - IN - 0.5, centered(850, 820, 260, 160), "Anton", 110,
          "#FFFFFF", weight=400, anim_in=tanim("pop", duration=0.3), anim_loop=tanim("pulse", amount=4, speed=1.2),
          name="Precio")
    song(t, "upbeat", 6, 0.5)
    return t


def tercio_fecha():
    t = _lt("h-tercio-fecha", "Fecha y hora", "Date and time", "h-concert-04", 2118, ["fecha", "evento", "hora", "lugar"],
            shade=440)
    cal = t.track("shape", "Calendario")
    rrect(t, cal, "#FFFFFF", IN, OUT - IN, Box(120, 760, 190, 200), 22, pop(0, 0.45))
    t.solid(t.track("shape", "Calendario"), "#E63946", IN, OUT - IN, Box(120, 760, 190, 60), pop(0, 0.45), radius=22,
            kind="rounded-rectangle")
    label(t, t.track("text", "Mes"), "NOV", IN + 0.1, OUT - IN - 0.1, Box(120, 760, 190, 60), "Montserrat", 36, "#FFFFFF",
          weight=800, spacing=4, motion=pop(0, 0.45), name="Mes")
    label(t, t.track("text", "Día"), "12", IN + 0.1, OUT - IN - 0.1, Box(120, 820, 190, 140), "Montserrat", 100,
          "#1D3557", weight=800, motion=pop(0, 0.45), name="Día")
    label(t, t.track("text", "Evento"), "Concierto de otoño", IN + 0.35, OUT - IN - 0.35, Box(345, 765, 1200, 90),
          "Montserrat", 64, "#FFFFFF", weight=800, align="left", anim_in=tanim("slide-right", duration=0.4),
          anim_out=tanim("fade", duration=0.3), name="Evento")
    label(t, t.track("text", "Hora"), "Sábado · 19:00 · Teatro Central", IN + 0.5, OUT - IN - 0.5, Box(348, 860, 1200, 60),
          "Montserrat", 38, "#FFD166", weight=600, align="left", anim_in=tanim("fade", duration=0.4),
          anim_out=tanim("fade", duration=0.3), name="Hora y lugar")
    song(t, "upbeat", 7, 0.5)
    return t


def tercio_suscribete():
    t = _lt("h-tercio-suscribete", "Suscríbete en la esquina", "Corner subscribe button", "h-desk-05", 2119,
            ["suscríbete", "botón", "campana", "youtube"], shade=0, thumb_at=3.2)
    pill(t, t.track("shape", "Base"), "#FFFFFF", IN, OUT - IN, Box(1180, 860, 640, 120), pop(0, 0.4),
         layers=[shadow("#000000", 0, 8, 22, 0.35), fill("#FFFFFF"), no_stroke()])
    circle_photo(t, "h-portrait-04", IN + 0.1, OUT - IN - 0.1, centered(1250, 920, 90, 90), pop(0, 0.4),
                 label="Foto del canal")
    btn = t.track("shape", "Botón")
    pill(t, btn, "#E10600", IN + 0.2, 2.0, Box(1320, 880, 330, 80), pop(0, 0.35))
    pill(t, btn, "#9E9E9E", IN + 2.2, OUT - IN - 2.2, Box(1320, 880, 330, 80), [(0, {"s": 0.9}, "back"), (0.25, {})])
    txt = t.track("text", "Botón")
    label(t, txt, "SUSCRIBIRSE", IN + 0.2, 2.0, Box(1320, 880, 330, 80), "Roboto", 36, "#FFFFFF", weight=700,
          name="Botón")
    label(t, txt, "SUSCRITO ✓", IN + 2.2, OUT - IN - 2.2, Box(1320, 880, 330, 80), "Roboto", 36, "#FFFFFF", weight=700,
          name="Botón pulsado")
    label(t, t.track("text", "Campana"), "🔔", IN + 0.4, OUT - IN - 0.4, centered(1730, 920, 100, 100), "Inter", 60,
          "#111111", weight=400, editable=False, motion=pop(0, 0.4),
          rotation=keys([(0, 0, "hold"), (2.0, 0, "smooth"), (2.15, 22, "smooth"), (2.3, -18, "smooth"), (2.45, 12, "smooth"),
                         (2.6, 0)]))
    label(t, t.track("text", "Cursor"), "➤", IN + 1.0, 1.6, centered(1560, 960, 90, 90), "Inter", 70, "#FFFFFF",
          weight=400, editable=False, layers=[stroke(4, "#111111"), fill("#FFFFFF")],
          motion=[(0, {"dx": 260, "dy": 140}, "inout"), (0.9, {}, "hold"), (1.0, {"s": 0.85}), (1.1, {})],
          rotation=keys([(0, -125)]))
    song(t, "upbeat", 0, 0.5)
    return t


def tercio_chat():
    t = _lt("h-tercio-chat", "Comentario destacado", "Featured comment", "h-portrait-05", 2120,
            ["comentario", "chat", "pregunta", "seguidores"], shade=0)
    rrect(t, t.track("shape", "Burbuja"), "#FFFFFF", IN, OUT - IN, Box(110, 760, 1000, 200), 30,
          [(0, {"s": 0.6, "dy": 60}, "back"), (0.45, {}, "hold"), (OUT - IN - 0.3, {}, "in"), (OUT - IN, {"s": 0.0})],
          layers=[shadow("#000000", 0, 10, 26, 0.3), fill("#FFFFFF"), no_stroke()])
    circle_photo(t, "h-man-03", IN + 0.2, OUT - IN - 0.2, centered(205, 830, 100, 100), pop(0, 0.35), label="Foto del usuario")
    label(t, t.track("text", "Usuario"), "@carlos_m  ·  hace 2 h", IN + 0.3, OUT - IN - 0.3, Box(280, 780, 800, 50),
          "Roboto", 32, "#606060", weight=700, align="left", anim_in=tanim("fade", duration=0.3), name="Usuario")
    label(t, t.track("text", "Comentario"), "¿Puedes hacer un video sobre cómo editar en el celular?", IN + 0.4,
          OUT - IN - 0.4, Box(280, 830, 800, 110), "Roboto", 40, "#0F0F0F", weight=500, align="left", line=1.15,
          anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Comentario")
    label(t, t.track("text", "Me gusta"), "♥ 248", IN + 0.6, OUT - IN - 0.6, Box(940, 780, 150, 50), "Roboto", 32,
          "#E10600", weight=700, align="right", anim_in=tanim("pop", duration=0.3), name="Me gusta")
    song(t, "upbeat", 2, 0.5)
    return t


def tercio_doble():
    t = _lt("h-tercio-doble", "Dos personas", "Two-person lower third", "h-podcast-03", 2121,
            ["dos personas", "entrevista", "debate", "invitados"], shade=380)
    for side, (name, role, x) in enumerate([("Elena Paz", "Periodista", 120), ("Nico Herrera", "Músico", 1180)]):
        dxi = -800 if side == 0 else 800
        t.solid(t.track("shape", "Barra"), "#6C63FF", IN + side * 0.2, OUT - IN - side * 0.2, Box(x, 830, 10, 120),
                [(0, {"sy": 0.0}, "out"), (0.3, {})])
        label(t, t.track("text", "Nombre"), name, IN + 0.15 + side * 0.2, OUT - IN - 0.15 - side * 0.2,
              Box(x + 35, 825, 600, 80), "Sora", 58, "#FFFFFF", weight=700, align="left",
              anim_in=tanim("slide-right" if side == 0 else "slide-left", duration=0.4),
              anim_out=tanim("fade", duration=0.3), name=f"Nombre {side + 1}")
        label(t, t.track("text", "Cargo"), role, IN + 0.3 + side * 0.2, OUT - IN - 0.3 - side * 0.2,
              Box(x + 37, 900, 600, 54), "Sora", 34, "#C9C6FF", weight=400, align="left",
              anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.3), name=f"Cargo {side + 1}")
    song(t, "jazz", 3, 0.5)
    return t


def tercio_diagonal():
    t = _lt("h-tercio-diagonal", "Tercio diagonal", "Diagonal lower third", "h-city-04", 2122,
            ["diagonal", "dinámico", "urbano"], shade=0)
    for i, (c, x, w) in enumerate([("#FF6B35", 80, 900), ("#111111", 120, 760)]):
        t.solid(t.track("shape", "Banda"), c, IN + i * 0.1, OUT - IN - i * 0.1, Box(x, 790 + i * 100, w, 100 - i * 30),
                _inout(dx_in=-1200, dx_out=1400, dur=OUT - IN - i * 0.1), rotation=keys([(0, -3)]))
    label(t, t.track("text", "Nombre"), "NAOMI REYES", IN + 0.3, OUT - IN - 0.3, Box(120, 790, 860, 100), "Kanit", 66,
          "#111111", weight=800, align="left", spacing=3, rotation=keys([(0, -3)]),
          anim_in=tanim("slide-right", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Nombre")
    label(t, t.track("text", "Cargo"), "BAILARINA Y COREÓGRAFA", IN + 0.4, OUT - IN - 0.4, Box(150, 890, 700, 70), "Kanit",
          36, "#FFFFFF", weight=600, align="left", spacing=4, rotation=keys([(0, -3)]),
          anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Cargo")
    song(t, "electro", 1, 0.5)
    return t


def tercio_retro():
    t = _lt("h-tercio-retro", "Tercio retro", "Retro lower third", "h-summer-01", 2123, ["retro", "70s", "vintage"],
            shade=0)
    for i, c in enumerate(["#F4A259", "#E76F51", "#8C5E3C"]):
        rrect(t, t.track("shape", "Franja"), c, IN + i * 0.08, OUT - IN - i * 0.08, Box(110, 800 + i * 34, 900, 34), 17,
              _inout(dx_in=-1100, dx_out=-1100, dur=OUT - IN - i * 0.08))
    rrect(t, t.track("shape", "Panel"), "#FFF1D6", IN + 0.25, OUT - IN - 0.25, Box(150, 760, 640, 120), 60,
          [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (OUT - IN - 0.55, {}, "in"), (OUT - IN - 0.25, {"s": 0.0})],
          layers=[shadow("#8C5E3C", 0, 6, 0, 1.0), fill("#FFF1D6"), no_stroke()])
    label(t, t.track("text", "Nombre"), "Sol y Mar", IN + 0.4, OUT - IN - 0.4, Box(150, 760, 640, 120), "Shrikhand", 66,
          "#E76F51", weight=400, anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Nombre")
    song(t, "jazz", 0, 0.5)
    return t


def tercio_boda():
    t = _lt("h-tercio-boda", "Rótulo de boda", "Wedding lower third", "h-wedding-06", 2124, ["boda", "novios", "fecha"],
            shade=460)
    label(t, t.track("text", "Nombres"), "Camila & Andrés", IN, OUT - IN, Box(120, 760, 1100, 150), "Great Vibes", 120,
          "#FFFFFF", weight=400, align="left", layers=[glow("#E8C27A", 14, 0.5), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=1.0, unit="character", stagger=0.04, blur=12),
          anim_out=tanim("fade", duration=0.4), name="Nombres")
    label(t, t.track("text", "Fecha"), "20 · 06 · 2027  ·  Toscana", IN + 0.6, OUT - IN - 0.6, Box(132, 910, 900, 60),
          "Cinzel", 36, "#E8C27A", weight=500, align="left", spacing=6, anim_in=tanim("fade", duration=0.6),
          anim_out=tanim("fade", duration=0.4), name="Fecha y lugar")
    dots(t, ["#E8C27A", "#FFFFFF"], 10, IN + 0.4, OUT - IN - 0.6, seed=24, size=(8, 16), kinds=("star",),
         area=Box(120, 740, 900, 220), drift=30)
    song(t, "romantic", 3, 0.5)
    return t


# --- Text scenes --------------------------------------------------------------------------------

def texto_capitulo():
    t = wide("h-texto-capitulo", "Tarjeta de capítulo", "Chapter card", "text", 5.0, order=2125,
             tags=["capítulo", "título", "documental", "youtube", "sección"], thumb_at=3.6, background="#0F0F12")
    photo_bg(t, "h-nature-06", s1=1.08, label="Fondo")
    shade_full(t, 0.55, colour="#0F0F12")
    label(t, t.track("text", "Número"), "03", 0.2, 4.6, Box(120, 180, 900, 600), "Bebas Neue", 620, "#FFFFFF", weight=400,
          align="left", layers=[stroke(4, "#FFFFFF"), {"id": "fill", "kind": "fill", "enabled": False,
                                "paint": {"kind": "solid", "color": "#00000000"}}],
          anim_in=tanim("slide-up", duration=0.6), anim_out=tanim("fade", duration=0.4), name="Número")
    label(t, t.track("text", "Capítulo"), "CAPÍTULO TRES", 0.6, 4.2, Box(860, 380, 960, 60), "Montserrat", 40, "#FFD166",
          weight=700, spacing=12, align="left", anim_in=tanim("fade", duration=0.5), name="Capítulo")
    label(t, t.track("text", "Título"), "Hacia el norte", 0.8, 4.0, Box(860, 440, 960, 200), "DM Serif Display", 140,
          "#FFFFFF", weight=400, align="left", anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.15),
          anim_out=tanim("fade", duration=0.4), name="Título")
    song(t, "cine", 0, 0.7)
    return t


def texto_titulo_grande():
    t = wide("h-texto-titulo-grande", "Título grande", "Big title", "text", 6.0, order=2126,
             tags=["título", "portada", "grande", "impacto", "youtube"], thumb_at=3.2)
    photo_bg(t, "h-travel-02", s1=1.1, label="Tu foto")
    shade_full(t, 0.25)
    for i, (txt, y, c, tc) in enumerate([("ASÍ VIAJAMOS", 300, "#FFFFFF", "#111111"), ("CON POCO DINERO", 520, "#FFD23F",
                                                                                         "#111111")]):
        label(t, t.track("text", "Línea"), txt, 0.4 + i * 0.35, 5.6 - i * 0.35, Box(160, y, 1600, 200), "Anton", 170, tc,
              weight=400, spacing=2, box_bg=(c, 1.0), box_pad=24, anim_in=tanim("wipe", duration=0.5, angle=0),
              name=f"Línea {i + 1}", rotation=keys([(0, -2 + i * 2)]))
    song(t, "upbeat", 4, 0.7)
    return t


def texto_cita_serif():
    t = wide("h-texto-cita-serif", "Cita elegante", "Elegant quote", "text", 8.0, order=2127,
             tags=["cita", "frase", "inspiración", "reflexión", "motivación"], thumb_at=5.5)
    photo_bg(t, "h-nature-03", s1=1.08, label="Fondo",
             effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=6)])
    shade_full(t, 0.5)
    label(t, t.track("text", "Cita"), "No cuentes los días, haz que los días cuenten.", 0.4, 7.6, Box(260, 300, 1400, 380),
          "Cormorant Garamond", 110, "#FFFFFF", weight=500, italic=True, line=1.05,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.18, blur=8), name="Cita")
    line(t, t.track("shape", "Línea"), "#D9B26F", 3.0, 5.0, centered(960, 730, 160, 3), grow="c", length=0.6)
    label(t, t.track("text", "Autor"), "MUHAMMAD ALI", 3.3, 4.7, Box(560, 760, 800, 60), "Montserrat", 36, "#D9B26F",
          weight=600, spacing=12, anim_in=tanim("fade", duration=0.6), name="Autor")
    song(t, "calm", 2, 0.7)
    return t


def texto_lista_5():
    t = wide("h-texto-lista-5", "Lista de 5", "Top 5 list", "text", 9.0, order=2128,
             tags=["lista", "top 5", "consejos", "puntos", "resumen"], thumb_at=7.0, background="#F4F1EA")
    bg(t, "#F4F1EA")
    t.photo(t.track("video", "Foto"), "h-desk-02", 0, 9.0, Box(1100, 0, 820, 1080), kb(9.0, 1.06, 1.0), label="Foto")
    label(t, t.track("text", "Título"), "5 hábitos que cambian tu día", 0.2, 8.8, Box(110, 90, 940, 200), "DM Serif Display",
          84, "#1A1A1A", weight=400, align="left", anim_in=tanim("fade-up-char", duration=0.5, unit="character",
          stagger=0.015), name="Título")
    items = ["Levántate a la misma hora", "Bebe agua al despertar", "Haz 10 minutos de ejercicio",
             "Escribe tus 3 prioridades", "Deja el celular una hora"]
    for i, it in enumerate(items):
        at = 1.0 + i * 1.1
        y = 330 + i * 140
        t.solid(t.track("shape", "Marca"), "#2A9D8F", at, 9.0 - at, centered(150, y + 45, 70, 70), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Número"), str(i + 1), at, 9.0 - at, centered(150, y + 45, 70, 70), "Inter", 40, "#FFFFFF",
              weight=800, editable=False, motion=pop(0, 0.35))
        label(t, t.track("text", "Punto"), it, at + 0.1, 8.9 - at, Box(220, y, 860, 90), "Inter", 46, "#1A1A1A",
              weight=600, align="left", anim_in=tanim("slide-right", duration=0.4, distance=0.15), name=f"Punto {i + 1}")
    song(t, "upbeat", 2, 0.6)
    return t


def texto_dato_curioso():
    t = wide("h-texto-dato-curioso", "Dato curioso", "Fun fact", "text", 7.0, order=2129,
             tags=["dato curioso", "sabías que", "educación", "curiosidades", "ciencia"], thumb_at=4.5,
             background="#2B2D42")
    bg_gradient(t, [(0, "#3A3D5C"), (1, "#1E2033")], angle=120)
    t.photo(t.track("video", "Foto"), "h-nature-05", 0.2, 6.8, Box(1060, 160, 760, 760),
            [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (6.8, {"s": 1.04})], label="Foto",
            rotation=keys([(0, 3)]))
    outline(t, t.track("shape", "Marco"), "#FFD166", 10, 0.4, 6.6, Box(1040, 140, 800, 800),
            [(0, {"s": 0.8}, "back"), (0.5, {})], rotation=keys([(0, 3)]))
    label(t, t.track("text", "Bombilla"), "💡", 0.5, 6.5, centered(200, 230, 180, 180), "Inter", 120, "#FFD166",
          weight=400, editable=False, motion=pop(0, 0.4), anim_loop=tanim("float", amount=0.1, speed=0.6))
    label(t, t.track("text", "Pregunta"), "¿Sabías que…?", 0.7, 6.3, Box(320, 170, 700, 130), "Fredoka", 96, "#FFD166",
          weight=700, align="left", anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1), name="Pregunta")
    label(t, t.track("text", "Dato"), "Los pulpos tienen tres corazones y sangre de color azul.", 1.5, 5.5,
          Box(130, 380, 860, 420), "Fredoka", 74, "#FFFFFF", weight=500, align="left", line=1.15,
          anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.08), name="Dato")
    song(t, "fun", 3, 0.6)
    return t


def texto_estadistica():
    t = wide("h-texto-estadistica", "Estadística", "Big statistic", "text", 6.0, order=2130,
             tags=["estadística", "cifra", "porcentaje", "datos", "infografía"], thumb_at=4.6, background="#0E1A2B")
    bg(t, "#0E1A2B")
    nums = t.track("text", "Número")
    for i, v in enumerate(["0%", "12%", "27%", "41%", "55%", "66%", "74%", "80%", "84%"]):
        label(t, nums, v, 0.3 + i * 0.2, 0.2, Box(160, 220, 1600, 360), "Montserrat", 320, "#FFFFFF", weight=900,
              editable=False)
    label(t, nums, "87%", 0.3 + 9 * 0.2, 6.0 - (0.3 + 9 * 0.2), Box(160, 220, 1600, 360), "Montserrat", 320, "#4CC9F0",
          weight=900, anim_in=tanim("pop", duration=0.3), name="Cifra")
    rrect(t, t.track("shape", "Barra"), "#22324A", 0.3, 5.7, Box(360, 640, 1200, 40), 20)
    rrect(t, t.track("shape", "Barra"), "#4CC9F0", 0.3, 5.7, Box(360, 640, 1044, 40), 20,
          [(0, {"sx": 0.0, "dx": -522}, "out"), (1.9, {})])
    label(t, t.track("text", "Texto"), "de las personas prefiere ver un video antes que leer", 1.0, 5.0,
          Box(260, 720, 1400, 140), "Montserrat", 50, "#C9D6EA", weight=500, line=1.2,
          anim_in=tanim("fade", duration=0.6), name="Descripción")
    label(t, t.track("text", "Fuente"), "Fuente: encuesta propia, 2026", 2.0, 4.0, Box(260, 900, 1400, 50), "Montserrat",
          28, "#6B7A90", weight=400, anim_in=tanim("fade", duration=0.6), name="Fuente")
    song(t, "upbeat", 3, 0.6)
    return t


def texto_comparacion():
    t = wide("h-texto-comparacion", "Comparación", "Comparison", "text", 7.0, order=2131,
             tags=["comparación", "versus", "a o b", "cuál es mejor", "reseña"], thumb_at=4.0, background="#111111")
    for i, (s, c, name, x) in enumerate([("h-city-03", "#E63946", "CIUDAD", 0), ("h-nature-02", "#2A9D8F", "CAMPO", 960)]):
        t.photo(t.track("video", f"Opción {i + 1}"), s, 0.1 + i * 0.2, 6.9 - i * 0.2, Box(x, 0, 960, 1080),
                [(0, {"dy": 1080 if i else -1080}, "out"), (0.6, {}, "linear"), (6.9 - i * 0.2, {"s": 1.05})],
                label=f"Foto opción {i + 1}")
        t.solid(t.track("shape", "Etiqueta"), c, 0.8 + i * 0.2, 6.2 - i * 0.2, Box(x + 180, 820, 600, 140),
                pop(0, 0.4), radius=20, kind="rounded-rectangle")
        label(t, t.track("text", "Opción"), name, 0.85 + i * 0.2, 6.15 - i * 0.2, Box(x + 180, 820, 600, 140), "Anton",
              96, "#FFFFFF", weight=400, spacing=6, motion=pop(0, 0.4), name=f"Opción {i + 1}")
    t.solid(t.track("shape", "VS"), "#FFFFFF", 1.2, 5.8, centered(960, 500, 220, 220), pop(0, 0.45), kind="ellipse",
            layers=[shadow("#000000", 0, 10, 30, 0.5), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "VS"), "VS", 1.25, 5.75, centered(960, 500, 220, 220), "Anton", 110, "#111111", weight=400,
          motion=pop(0, 0.45), editable=False)
    label(t, t.track("text", "Pregunta"), "¿Dónde vivirías?", 1.6, 5.4, Box(460, 60, 1000, 130), "Montserrat", 80,
          "#FFFFFF", weight=900, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("drop", duration=0.5), name="Pregunta")
    song(t, "upbeat", 5, 0.6)
    return t


def texto_pregunta():
    t = wide("h-texto-pregunta", "Pregunta al público", "Ask the audience", "text", 6.0, order=2132,
             tags=["pregunta", "comentarios", "interacción", "comunidad", "opinión"], thumb_at=4.2, background="#5B5BD6")
    bg_gradient(t, [(0, "#6C63FF"), (1, "#3F3D9E")], angle=135)
    dots(t, ["#FFFFFF"], 18, 0, 6.0, seed=32, size=(10, 26), drift=50, alpha=0.25)
    label(t, t.track("text", "Pregunta"), "¿Qué harías con un día libre?", 0.3, 5.7, Box(160, 260, 1600, 380), "Poppins",
          120, "#FFFFFF", weight=800, line=1.05, anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.12, ease="back"),
          name="Pregunta")
    pill(t, t.track("shape", "Píldora"), "#FFFFFF", 2.0, 4.0, centered(960, 780, 980, 110), pop(0, 0.4))
    label(t, t.track("text", "Llamada"), "Déjalo en los comentarios 👇", 2.1, 3.9, centered(960, 780, 980, 110), "Poppins",
          50, "#3F3D9E", weight=700, name="Llamada")
    song(t, "fun", 4, 0.6)
    return t


def texto_cinetico():
    t = wide("h-texto-cinetico", "Texto cinético", "Kinetic typography", "text", 6.0, order=2133,
             tags=["texto cinético", "tipografía", "motivación", "ritmo", "palabras"], thumb_at=4.1, background="#000000")
    words = [("SUEÑA", "#000000", "#FFFFFF"), ("CREA", "#FFD23F", "#000000"), ("REPITE", "#000000", "#FFD23F"),
             ("NO", "#FF2E63", "#FFFFFF"), ("TE", "#FF2E63", "#FFFFFF"), ("RINDAS", "#FFFFFF", "#FF2E63")]
    bgs = t.track("shape", "Fondo")
    txt = t.track("text", "Palabras")
    at = 0.0
    for i, (w, b, c) in enumerate(words):
        d = 0.5 if i < 5 else 6.0 - at
        if i == 3:
            d = 1.0
        t.solid(bgs, b, at, d)
        label(t, txt, w if i != 4 else "NO TE", at, d, Box(0, 300, 1920, 480), "Anton", 400 if i < 3 else 330, c,
              weight=400, spacing=6, anim_in=tanim("zoom-out", duration=0.25, blur=6), name=f"Palabra {i + 1}")
        at += d
    t.adjust([effect("beat_shake", animated={"amount": spike([0.0, 0.5, 1.0, 1.5, 2.5, 3.0], 0.6, 0.18)})],
             name="Golpe")
    song(t, "electro", 0, 0.8)
    return t


def texto_maquina():
    t = wide("h-texto-maquina", "Máquina de escribir", "Typewriter", "text", 7.0, order=2134,
             tags=["máquina de escribir", "carta", "vintage", "historia", "texto"], thumb_at=5.6, background="#F1E9D8")
    bg_gradient(t, [(0, "#F5EEDF"), (1, "#E4D6BC")], angle=90)
    for k in range(9):
        t.solid(t.track("shape", "Renglón"), "#C9B999", 0, 7.0, Box(220, 300 + k * 78, 1480, 2), alpha=0.6)
    label(t, t.track("text", "Texto"), "Querida Ana:\nhoy encontré la foto de aquel verano y volví a sonreír como entonces…",
          0.3, 6.7, Box(230, 220, 1460, 640), "Special Elite", 62, "#2B2118", weight=400, align="left", valign="top",
          line=1.3, anim_in=tanim("typewriter", duration=4.5, unit="character", caret=True), name="Carta")
    t.photo(t.track("video", "Foto"), "h-family-01", 4.6, 2.4, Box(1500, 700, 300, 220),
            [(0, {"s": 1.3, "dy": -60}, "out"), (0.4, {})], label="Foto", rotation=keys([(0, 8)]))
    grain(t, 0.2)
    song(t, "classic", 2, 0.6)
    return t


def texto_titular_revista():
    t = wide("h-texto-titular-revista", "Titular de revista", "Magazine headline", "text", 6.0, order=2135,
             tags=["revista", "portada", "editorial", "moda", "titulares"], thumb_at=4.0)
    photo_bg(t, "h-portrait-06", s1=1.08, label="Foto de portada")
    shade_full(t, 0.15)
    label(t, t.track("text", "Cabecera"), "ESTILO", 0.2, 5.8, Box(100, 40, 1100, 260), "Bodoni Moda", 250, "#FFFFFF",
          weight=700, align="left", spacing=10, anim_in=tanim("drop", duration=0.6), name="Cabecera")
    heads = [("La nueva calma", 380, 70, "#FFFFFF"), ("12 ideas para tu casa", 480, 46, "#FFD6E0"),
             ("ENTREVISTA: Mar López", 560, 40, "#FFFFFF")]
    for i, (h, y, size, c) in enumerate(heads):
        label(t, t.track("text", "Titular"), h, 1.0 + i * 0.4, 5.0 - i * 0.4, Box(110, y, 800, size + 30), "Playfair Display",
              size, c, weight=600 if i == 0 else 400, italic=i == 0, align="left",
              layers=[shadow("#000000", 0, 3, 10, 0.5), fill(c)], anim_in=tanim("slide-right", duration=0.4),
              name=f"Titular {i + 1}")
    label(t, t.track("text", "Número"), "OTOÑO 2026 · Nº 48", 1.8, 4.2, Box(1400, 990, 480, 50), "Montserrat", 28,
          "#FFFFFF", weight=600, spacing=6, align="right", anim_in=tanim("fade", duration=0.4), name="Edición")
    song(t, "jazz", 3, 0.6)
    return t


def texto_advertencia():
    t = wide("h-texto-advertencia", "Aviso", "Warning", "text", 5.0, order=2136,
             tags=["aviso", "atención", "advertencia", "importante", "precaución"], thumb_at=3.0, background="#111111")
    bg(t, "#111111")
    for row, y in enumerate((80, 880)):
        tape = t.track("shape", "Cinta")
        t.solid(tape, "#FFD600", 0, 5.0, Box(-100, y, 2120, 120), rotation=keys([(0, -2 if row else 2)]))
        stripes = t.track("shape", "Rayas")
        for k in range(16):
            t.solid(stripes, "#111111", 0, 5.0, Box(-140 + k * 140, y + 10, 60, 100),
                    [(0, {}, "linear"), (5.0, {"dx": 280 * (-1 if row else 1)})], rotation=keys([(0, 35)]))
    label(t, t.track("text", "Título"), "⚠ ATENCIÓN", 0.3, 4.7, Box(160, 300, 1600, 220), "Anton", 190, "#FFD600",
          weight=400, spacing=6, anim_in=tanim("stamp", duration=0.3), anim_loop=tanim("pulse", amount=3, speed=1.5),
          name="Título")
    label(t, t.track("text", "Mensaje"), "Este video contiene escenas de mucha risa", 0.9, 4.1, Box(260, 540, 1400, 150),
          "Montserrat", 60, "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.5), name="Mensaje")
    song(t, "suspense", 1, 0.6)
    return t


def texto_agenda():
    t = wide("h-texto-agenda", "Agenda del video", "Video agenda", "text", 8.0, order=2137,
             tags=["agenda", "contenido", "temas", "capítulos", "índice"], thumb_at=6.5, background="#101820")
    photo_bg(t, "h-desk-04", s1=1.06, label="Fondo", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=10)])
    shade_full(t, 0.65, colour="#101820")
    label(t, t.track("text", "Título"), "EN ESTE VIDEO", 0.2, 7.8, Box(140, 110, 1000, 110), "Barlow Condensed", 90,
          "#F2AA4C", weight=800, spacing=8, align="left", anim_in=tanim("slide-right", duration=0.4), name="Título")
    items = [("00:00", "Introducción"), ("01:20", "Lo que necesitas"), ("03:45", "Paso a paso"),
             ("07:10", "Errores comunes"), ("09:30", "Resultado final")]
    for i, (tc, txt) in enumerate(items):
        at = 0.8 + i * 0.8
        y = 290 + i * 135
        pill(t, t.track("shape", "Tiempo"), "#F2AA4C", at, 8.0 - at, Box(140, y, 210, 80), slide_in(dx=-300, length=0.35))
        label(t, t.track("text", "Tiempo"), tc, at, 8.0 - at, Box(140, y, 210, 80), "Barlow Condensed", 48, "#101820",
              weight=800, motion=slide_in(dx=-300, length=0.35), name=f"Tiempo {i + 1}")
        label(t, t.track("text", "Tema"), txt, at + 0.15, 7.85 - at, Box(390, y, 1200, 80), "Barlow Condensed", 60,
              "#FFFFFF", weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Tema {i + 1}")
    song(t, "upbeat", 7, 0.55)
    return t


def texto_lecciones():
    t = wide("h-texto-lecciones", "Lo que aprenderás", "What you'll learn", "text", 7.0, order=2138,
             tags=["curso", "aprenderás", "lecciones", "educación", "tutorial"], thumb_at=5.0, background="#FFF8F0")
    bg(t, "#FFF8F0")
    label(t, t.track("text", "Título"), "Lo que aprenderás hoy", 0.2, 6.8, Box(160, 90, 1600, 140), "Lexend", 96,
          "#1D3557", weight=700, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.02), name="Título")
    cards = [("🎨", "Elegir colores", "#FFB4A2"), ("✍️", "Combinar letras", "#B5E48C"), ("📐", "Ordenar el diseño",
                                                                                         "#A0C4FF")]
    for i, (icon, txt, c) in enumerate(cards):
        x = 330 + i * 630
        at = 0.8 + i * 0.5
        rrect(t, t.track("shape", "Tarjeta"), c, at, 7.0 - at, centered(x, 600, 520, 560), 40, pop(0, 0.45, 0.6),
              layers=[shadow("#1D3557", 0, 14, 0, 0.12), fill(c), no_stroke()])
        label(t, t.track("text", "Icono"), icon, at + 0.1, 6.9 - at, centered(x, 520, 300, 220), "Inter", 150, "#1D3557",
              weight=400, editable=False, motion=pop(0, 0.45))
        label(t, t.track("text", "Lección"), txt, at + 0.2, 6.8 - at, centered(x, 740, 480, 140), "Lexend", 54,
              "#1D3557", weight=700, anim_in=tanim("fade", duration=0.3), name=f"Lección {i + 1}")
    song(t, "fun", 3, 0.55)
    return t


def texto_linea_tiempo():
    t = wide("h-texto-linea-tiempo", "Línea de tiempo", "Timeline", "text", 9.0, order=2139,
             tags=["línea de tiempo", "historia", "años", "trayectoria", "aniversario"], thumb_at=7.6, background="#0F172A")
    bg(t, "#0F172A")
    label(t, t.track("text", "Título"), "Nuestra historia", 0.2, 8.8, Box(160, 90, 1600, 140), "DM Serif Display", 104,
          "#FFFFFF", weight=400, anim_in=tanim("fade", duration=0.6), name="Título")
    line(t, t.track("shape", "Línea"), "#38BDF8", 0.6, 8.4, Box(160, 560, 1600, 6), length=6.0, ease="linear")
    events = [("2019", "La idea"), ("2021", "Primer local"), ("2023", "100 clientes"), ("2025", "Nueva sede"),
              ("2026", "¡Hoy!")]
    for i, (y, txt) in enumerate(events):
        x = 220 + i * 370
        at = 0.6 + (x - 160) / 1600 * 6.0
        t.solid(t.track("shape", "Hito"), "#38BDF8", at, 9.0 - at, centered(x, 563, 44, 44), pop(0, 0.35), kind="ellipse",
                layers=[glow("#38BDF8", 18, 0.8), fill("#38BDF8"), no_stroke()])
        up = i % 2 == 0
        label(t, t.track("text", "Año"), y, at + 0.1, 8.9 - at, centered(x, 440 if up else 690, 340, 110), "Montserrat",
              80, "#FFFFFF", weight=800, anim_in=tanim("slide-up" if up else "slide-down", duration=0.4),
              name=f"Año {i + 1}")
        label(t, t.track("text", "Hito"), txt, at + 0.2, 8.8 - at, centered(x, 360 if up else 770, 340, 70), "Montserrat",
              40, "#94A3B8", weight=500, anim_in=tanim("fade", duration=0.4), name=f"Hito {i + 1}")
    song(t, "upbeat", 6, 0.55)
    return t


def texto_receta_ingredientes():
    t = wide("h-texto-receta-ingredientes", "Ingredientes", "Recipe ingredients", "text", 8.0, order=2140,
             tags=["receta", "ingredientes", "cocina", "comida", "lista"], thumb_at=6.5, background="#FFF6E9")
    bg(t, "#FFF6E9")
    t.photo(t.track("video", "Plato"), "h-food-03", 0, 8.0, Box(980, 0, 940, 1080), kb(8.0, 1.0, 1.08),
            label="Foto del plato")
    label(t, t.track("text", "Receta"), "Ensalada mediterránea", 0.2, 7.8, Box(110, 90, 840, 200), "Lobster", 76, "#C2410C",
          weight=400, align="left", anim_in=tanim("fade", duration=0.5), name="Receta")
    label(t, t.track("text", "Sub"), "INGREDIENTES · 4 PORCIONES", 0.5, 7.5, Box(114, 280, 860, 60), "Montserrat", 32,
          "#7C2D12", weight=700, spacing=6, align="left", anim_in=tanim("fade", duration=0.5), name="Porciones")
    items = ["2 tomates maduros", "1 pepino", "100 g de queso feta", "aceitunas negras", "aceite de oliva y orégano"]
    for i, it in enumerate(items):
        at = 1.0 + i * 0.7
        t.solid(t.track("shape", "Viñeta"), "#16A34A", at, 8.0 - at, centered(140, 410 + i * 110, 22, 22), pop(0, 0.3),
                kind="ellipse")
        label(t, t.track("text", "Ingrediente"), it, at, 8.0 - at, Box(180, 375 + i * 110, 780, 70), "Montserrat", 46,
              "#292524", weight=600, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.1),
              name=f"Ingrediente {i + 1}")
    song(t, "jazz", 1, 0.55)
    return t


def texto_marcador():
    t = wide("h-texto-marcador", "Marcador final", "Final score", "text", 6.0, order=2141,
             tags=["marcador", "resultado", "partido", "deportes", "final"], thumb_at=4.0)
    photo_bg(t, "h-soccer-03", s1=1.06, label="Foto del partido")
    shade_full(t, 0.55, colour="#04110A")
    rrect(t, t.track("shape", "Marcador"), "#FFFFFF", 0.3, 5.7, centered(960, 520, 1300, 300), 30, pop(0, 0.45, 0.8),
          layers=[shadow("#000000", 0, 16, 40, 0.5), fill("#FFFFFF"), no_stroke()])
    for i, (team, c) in enumerate([("ÁGUILAS", "#1E5BFF"), ("LEONES", "#E10600")]):
        x = 520 if i == 0 else 1400
        t.solid(t.track("shape", "Escudo"), c, 0.6, 5.4, centered(x - 210 if i == 0 else x + 210, 520, 90, 110),
                pop(0, 0.4), kind="pentagon", rotation=keys([(0, 180)]))
        label(t, t.track("text", "Equipo"), team, 0.6, 5.4, centered(x, 520, 400, 120), "Oswald", 80, "#111111",
              weight=700, anim_in=tanim("fade", duration=0.3), name=f"Equipo {i + 1}")
    label(t, t.track("text", "Resultado"), "2 – 1", 0.9, 5.1, centered(960, 520, 420, 220), "Oswald", 170, "#111111",
          weight=700, anim_in=tanim("pop", duration=0.4), name="Resultado")
    pill(t, t.track("shape", "Final"), "#FFD23F", 1.3, 4.7, centered(960, 330, 360, 80), pop(0, 0.35))
    label(t, t.track("text", "Final"), "FINAL", 1.35, 4.65, centered(960, 330, 360, 80), "Oswald", 50, "#111111",
          weight=700, spacing=10, name="Etiqueta")
    label(t, t.track("text", "Torneo"), "COPA DE PRIMAVERA · JORNADA 8", 1.6, 4.4, centered(960, 760, 1200, 70), "Oswald",
          44, "#FFFFFF", weight=500, spacing=6, anim_in=tanim("fade", duration=0.4), name="Torneo")
    song(t, "epic", 4, 0.6)
    return t


def texto_portada_video():
    t = wide("h-texto-portada-video", "Portada de video", "Video thumbnail", "text", 4.0, order=2142,
             tags=["miniatura", "portada", "thumbnail", "youtube", "clickbait"], thumb_at=2.4, background="#FFE600")
    bg_gradient(t, [(0, "#FFE600"), (1, "#FF9F1C")], angle=135)
    t.photo(t.track("video", "Persona"), "h-portrait-05", 0.0, 4.0, Box(1080, 0, 840, 1080),
            [(0, {"dx": 400}, "out"), (0.4, {}, "linear"), (4.0, {"s": 1.04})], label="Tu foto (sorprendido)")
    label(t, t.track("text", "Línea 1"), "PROBÉ", 0.3, 3.7, Box(80, 120, 1000, 260), "Luckiest Guy", 230, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 12, 0, 1.0), stroke(14, "#000000"), fill("#FFFFFF")],
          anim_in=tanim("stamp", duration=0.3), rotation=keys([(0, -4)]), name="Línea 1")
    label(t, t.track("text", "Línea 2"), "ESTO 30 DÍAS", 0.6, 3.4, Box(60, 400, 1060, 260), "Luckiest Guy", 170,
          "#FF1E56", weight=400, layers=[shadow("#000000", 0, 12, 0, 1.0), stroke(14, "#000000"), fill("#FF1E56")],
          anim_in=tanim("stamp", duration=0.3), rotation=keys([(0, 3)]), name="Línea 2")
    label(t, t.track("text", "Flecha"), "➜", 1.0, 3.0, centered(980, 830, 300, 240), "Inter", 220, "#FF1E56", weight=900,
          editable=False, layers=[stroke(10, "#000000"), fill("#FF1E56")], motion=pop(0, 0.35),
          rotation=keys([(0, 20)]))
    song(t, "fun", 1, 0.6)
    return t


def texto_creditos():
    t = wide("h-texto-creditos", "Créditos finales", "End credits", "text", 12.0, order=2143,
             tags=["créditos", "final", "agradecimientos", "película", "equipo"], thumb_at=5.0, background="#000000")
    bg(t, "#000000")
    roll = ("DIRECCIÓN\nAna Torres\n\nGUION\nLuis Gómez\n\nFOTOGRAFÍA\nMarta Ríos\n\nEDICIÓN\nPablo Díaz\n\n"
            "MÚSICA\nFlip Studio\n\nGRACIAS A\nnuestras familias\ny a ti por ver")
    label(t, t.track("text", "Créditos"), roll, 0, 12.0, Box(460, 0, 1000, 2400), "Montserrat", 56, "#FFFFFF", weight=500,
          valign="top", line=1.35, spacing=2, motion=[(0, {"dy": 1100}, "linear"), (12.0, {"dy": -1500})],
          name="Créditos")
    vignette(t, 0.4)
    song(t, "calm", 0, 0.7)
    return t


def texto_frase_neon():
    t = wide("h-texto-frase-neon", "Frase neón", "Neon sign", "text", 6.0, order=2144,
             tags=["neón", "letrero", "frase", "noche", "aesthetic"], thumb_at=3.8, background="#120D16")
    photo_bg(t, "h-cafe-02", s1=1.04, label="Fondo",
             effects=[effect("color.basic", exposure=-0.6, saturation=-0.4),
                      effect("builtin.effects.gaussian_blur", u_blurRadius=4)])
    label(t, t.track("text", "Neón"), "abierto\ntoda la noche", 0.3, 5.7, Box(260, 260, 1400, 560), "Sacramento", 180,
          "#FFFFFF", weight=400, line=1.0, layers=[glow("#FF4FD8", 40, 1.0), glow("#FF4FD8", 12, 1.0, id="glow2"),
                                                   fill("#FFE6FA")],
          anim_in=tanim("flicker-in", duration=1.0), anim_loop=tanim("flicker", intensity=0.2, speed=3), name="Letrero")
    t.adjust([effect("bloom_glow", threshold=0.5, intensity=1.1, blurRadius=18)], name="Brillo")
    song(t, "jazz", 0, 0.6)
    return t


# --- Endings ------------------------------------------------------------------------------------

def cierre_gracias():
    t = wide("h-cierre-gracias", "Gracias por ver", "Thanks for watching", "outro", 7.0, order=2145,
             tags=["gracias", "final", "redes", "cierre", "despedida"], thumb_at=4.5)
    photo_bg(t, "h-portrait-01", s1=1.08, label="Tu foto")
    shade_full(t, 0.5)
    label(t, t.track("text", "Gracias"), "¡Gracias por ver!", 0.3, 6.7, Box(160, 250, 1600, 240), "Pacifico", 170,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 6, 18, 0.5), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.5, unit="word", stagger=0.15, ease="back"), name="Gracias")
    handles = [("▶", "Tu Canal", "#FF0033"), ("◎", "@tucanal", "#C13584"), ("♪", "@tucanal", "#111111")]
    for i, (g, h, c) in enumerate(handles):
        x = 420 + i * 540
        at = 1.4 + i * 0.25
        rrect(t, t.track("shape", "Icono"), c, at, 7.0 - at, centered(x - 150, 680, 90, 90), 24, pop(0, 0.4),
              layers=[shadow("#000000", 0, 6, 14, 0.4), fill(c), stroke(3, "#FFFFFF")])
        label(t, t.track("text", "Icono"), g, at, 7.0 - at, centered(x - 150, 680, 90, 90), "Inter", 50, "#FFFFFF",
              weight=700, editable=False, motion=pop(0, 0.4))
        label(t, t.track("text", "Red"), h, at + 0.1, 6.9 - at, Box(x - 90, 640, 400, 80), "Montserrat", 44, "#FFFFFF",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Red {i + 1}")
    song(t, "upbeat", 1, 0.7)
    return t


def cierre_suscribete_campana():
    t = wide("h-cierre-suscribete-campana", "Suscríbete y activa la campana", "Subscribe and ring the bell", "outro", 6.0,
             order=2146, tags=["suscríbete", "campana", "botón", "youtube", "cierre"], thumb_at=1.95, background="#0F0F0F")
    bg_gradient(t, [(0, "#202020"), (1, "#0A0A0A")], angle=90)
    btn = t.track("shape", "Botón")
    pill(t, btn, "#FF0033", 0.3, 2.4, centered(820, 540, 760, 180), pop(0, 0.45))
    pill(t, btn, "#3A3A3A", 2.7, 3.3, centered(820, 540, 760, 180), [(0, {"s": 0.92}, "back"), (0.3, {})])
    txt = t.track("text", "Botón")
    label(t, txt, "SUSCRÍBETE", 0.35, 2.35, centered(820, 540, 760, 180), "Roboto", 92, "#FFFFFF", weight=900,
          spacing=4, name="Botón")
    label(t, txt, "SUSCRITO ✓", 2.7, 3.3, centered(820, 540, 760, 180), "Roboto", 92, "#BBBBBB", weight=900, spacing=4,
          name="Botón pulsado")
    label(t, t.track("text", "Cursor"), "➤", 1.2, 1.8, centered(920, 640, 120, 120), "Inter", 96, "#FFFFFF", weight=400,
          editable=False, layers=[stroke(5, "#000000"), fill("#FFFFFF")],
          motion=[(0, {"dx": 520, "dy": 300}, "inout"), (1.3, {}, "hold"), (1.45, {"s": 0.8}), (1.6, {})],
          rotation=keys([(0, -125)]))
    label(t, t.track("text", "Campana"), "🔔", 1.0, 5.0, centered(1420, 540, 220, 220), "Inter", 150, "#FFD23F",
          weight=400, editable=False, motion=pop(0, 0.4),
          rotation=keys([(0, 0, "hold"), (2.2, 0, "smooth"), (2.35, 25, "smooth"), (2.5, -22, "smooth"), (2.65, 16, "smooth"),
                         (2.8, -10, "smooth"), (2.95, 0)]))
    label(t, t.track("text", "Texto"), "y activa la campana para no perderte nada", 1.5, 4.5, Box(260, 760, 1400, 90),
          "Roboto", 54, "#FFFFFF", weight=500, anim_in=tanim("fade", duration=0.5), name="Texto")
    flash(t, 2.65, 0.25, peak=0.3)
    song(t, "upbeat", 0, 0.7)
    return t


def cierre_like():
    t = wide("h-cierre-like", "Dale like", "Hit like", "outro", 5.0, order=2147,
             tags=["like", "me gusta", "pulgar", "cierre", "interacción"], thumb_at=2.6, background="#1565C0")
    bg_gradient(t, [(0, "#1E88E5"), (1, "#0D47A1")], angle=135)
    ring(t, t.track("shape", "Onda"), "#FFFFFF", 8, 1.0, 1.2, centered(960, 450, 400, 400), [(0, {"s": 0.6}, "out"),
                                                                                           (1.2, {"s": 2.2})],
         opacity=keys([(0, 0.8), (1.2, 0.0)]))
    label(t, t.track("text", "Pulgar"), "👍", 0.3, 4.7, centered(960, 430, 560, 560), "Inter", 420, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"s": 0.0}, "back"), (0.5, {}, "hold"), (0.7, {}), (0.8, {"s": 1.18}, "back"),
                                  (1.1, {})], rotation=keys([(0, -20, "back"), (0.5, 0)]))
    label(t, t.track("text", "Texto"), "¡Dale like si te gustó!", 1.2, 3.8, Box(160, 720, 1600, 160), "Poppins", 104,
          "#FFFFFF", weight=800, anim_in=tanim("rise", duration=0.4, unit="word", stagger=0.1), name="Texto")
    dots(t, ["#FFFFFF", "#90CAF9", "#FFD23F"], 22, 1.0, 4.0, seed=47, size=(14, 34), kinds=("heart", "star", "ellipse"),
         area=Box(500, 200, 920, 500), drift=160)
    song(t, "fun", 0, 0.7)
    return t


def cierre_redes():
    t = wide("h-cierre-redes", "Sígueme en redes", "Follow me", "outro", 6.0, order=2148,
             tags=["redes sociales", "sígueme", "usuario", "cierre", "contacto"], thumb_at=4.0, background="#FAF7F2")
    bg(t, "#FAF7F2")
    circle_photo(t, "h-portrait-02", 0.2, 5.8, centered(960, 300, 300, 300), pop(0, 0.5), ring_colour="#111111",
                 ring_width=6, label="Tu foto")
    label(t, t.track("text", "Título"), "Sígueme en redes", 0.8, 5.2, Box(260, 480, 1400, 140), "DM Serif Display", 104,
          "#111111", weight=400, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.02),
          name="Título")
    nets = [("▶", "#FF0033"), ("◎", "#C13584"), ("♪", "#111111"), ("f", "#1877F2")]
    for i, (g, c) in enumerate(nets):
        x = 660 + i * 200
        at = 1.4 + i * 0.15
        rrect(t, t.track("shape", "Icono"), c, at, 6.0 - at, centered(x, 720, 130, 130), 34, pop(0, 0.4))
        label(t, t.track("text", "Icono"), g, at, 6.0 - at, centered(x, 720, 130, 130), "Inter", 70, "#FFFFFF",
              weight=800, editable=False, motion=pop(0, 0.4))
    label(t, t.track("text", "Usuario"), "@tuusuario", 2.2, 3.8, Box(560, 830, 800, 90), "Montserrat", 56, "#111111",
          weight=700, anim_in=tanim("typewriter", duration=0.7, unit="character"), name="Usuario")
    song(t, "upbeat", 5, 0.7)
    return t


def cierre_proximo():
    t = wide("h-cierre-proximo", "En el próximo video", "In the next video", "outro", 7.0, order=2149,
             tags=["próximo video", "adelanto", "cierre", "siguiente", "episodio"], thumb_at=4.6, background="#111827")
    bg_gradient(t, [(0, "#1F2937"), (1, "#0B1120")], angle=120)
    label(t, t.track("text", "Antetítulo"), "EN EL PRÓXIMO VIDEO", 0.3, 6.7, Box(120, 120, 900, 70), "Montserrat", 44,
          "#F59E0B", weight=800, spacing=8, align="left", anim_in=tanim("slide-right", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "Cruzamos los Alpes en bicicleta", 0.6, 6.4, Box(120, 200, 820, 400),
          "Montserrat", 92, "#FFFFFF", weight=900, align="left", line=1.05,
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1), name="Título")
    label(t, t.track("text", "Fecha"), "este domingo · 18:00", 1.4, 5.6, Box(124, 640, 820, 70), "Montserrat", 44,
          "#9CA3AF", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Fecha")
    framed(t, "h-nature-05", 0.8, 6.2, Box(1000, 230, 800, 450), [(0, {"s": 0.7}, "back"), (0.5, {}, "linear"),
                                                                   (6.2, {"s": 1.03})], border=8, radius=18,
           label="Adelanto")
    t.solid(t.track("shape", "Play"), "#FFFFFF", 1.4, 5.6, centered(1400, 455, 140, 140), pop(0, 0.4), kind="ellipse",
            alpha=0.9)
    t.solid(t.track("shape", "Play"), "#111827", 1.5, 5.5, centered(1410, 455, 56, 64), pop(0, 0.4), kind="triangle",
            rotation=keys([(0, 90)]))
    song(t, "cine", 2, 0.7)
    return t


TEMPLATES = [tercio_minimal_linea, tercio_caja_color, tercio_duotono, tercio_redondeado, tercio_noticias,
             tercio_corporativo, tercio_redes, tercio_ubicacion, tercio_entrevista, tercio_gaming, tercio_elegante,
             tercio_a_mano, tercio_glass, tercio_podcast, tercio_deportes, tercio_tutorial_paso, tercio_cita,
             tercio_precio, tercio_fecha, tercio_suscribete, tercio_chat, tercio_doble, tercio_diagonal, tercio_retro,
             tercio_boda,
             texto_capitulo, texto_titulo_grande, texto_cita_serif, texto_lista_5, texto_dato_curioso,
             texto_estadistica, texto_comparacion, texto_pregunta, texto_cinetico, texto_maquina,
             texto_titular_revista, texto_advertencia, texto_agenda, texto_lecciones, texto_linea_tiempo,
             texto_receta_ingredientes, texto_marcador, texto_portada_video, texto_creditos, texto_frase_neon,
             cierre_gracias, cierre_suscribete_campana, cierre_like, cierre_redes, cierre_proximo]
