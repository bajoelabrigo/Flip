"""Horizontal batch 3 (2026-10-16): end screens, photo slideshows and celebrations, 1920x1080.
See BRIEF.md, «Las 400 nuevas». Categories outro, slideshow, celebration; order 2200-2299.

End screens leave room where YouTube puts its end-screen elements: each suggested-video box is a slot
(«Video sugerido»), so a screenshot of the video can fill it.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels,
                 photo_bg, pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides,
                 song, spike, stroke, tanim, vignette, wide)


def _video_slot(t, sample, box, t0, n, colour="#FFFFFF", radius=18, border=6, motion=None, glow_colour=None):
    m = motion or pop(0, 0.45, 0.6)
    layers = [shadow("#000000", 0, 12, 30, 0.45), fill(colour), no_stroke()]
    if glow_colour:
        layers = [glow(glow_colour, 28, 0.9), fill(colour), no_stroke()]
    t.solid(t.track("shape", "Marco"), colour, t0, t.duration - t0,
            Box(box.x - border, box.y - border, box.w + 2 * border, box.h + 2 * border), m, radius=radius + border,
            kind="rounded-rectangle", layers=layers)
    track = t.track("video", f"Video {n}")
    clip = t.photo(track, sample, t0, t.duration - t0, box, m, label=f"Video sugerido {n}")
    return clip


def _subscribe_circle(t, sample, cx, cy, size, t0, ring_colour="#FFFFFF", text_colour="#FFFFFF", caption="SUSCRÍBETE"):
    circle_photo(t, sample, t0, t.duration - t0, centered(cx, cy, size, size), pop(0, 0.5), ring_colour=ring_colour,
                 ring_width=8, label="Foto del canal")
    label(t, t.track("text", "Suscríbete"), caption, t0 + 0.3, t.duration - t0 - 0.3, centered(cx, cy + size / 2 + 60, 600, 70),
          "Montserrat", 40, text_colour, weight=800, spacing=6, anim_in=tanim("fade", duration=0.4), name="Suscríbete")


# --- End screens --------------------------------------------------------------------------------

def final_2_videos():
    t = wide("h-final-2-videos", "Pantalla final: 2 videos", "End screen: 2 videos", "outro", 10.0, order=2200,
             tags=["pantalla final", "end screen", "youtube", "videos sugeridos", "suscríbete"], thumb_at=3.0,
             background="#101828")
    bg_gradient(t, [(0, "#1D2B53"), (1, "#0B1023")], angle=135)
    for i, (c, x, y, s) in enumerate([("#7E5BEF", 200, 200, 800), ("#FF6B6B", 1700, 900, 900)]):
        t.solid(t.track("shape", "Luz"), c, 0, 10.0, centered(x, y, s, s),
                [(0, {}, "smooth"), (5.0, {"dx": 120 * (-1) ** i, "dy": 60}, "smooth"), (10.0, {})], kind="ellipse",
                layers=[gradient([(0, c, 0.5), (1, c, 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Título"), "Mira esto también", 0.2, 9.8, Box(160, 80, 1600, 120), "Montserrat", 80,
          "#FFFFFF", weight=900, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.02), name="Título")
    _video_slot(t, "h-travel-04", Box(160, 330, 720, 405), 0.5, 1)
    _video_slot(t, "h-cooking-01", Box(1040, 330, 720, 405), 0.7, 2)
    _subscribe_circle(t, "h-portrait-02", 960, 860, 150, 1.0)
    song(t, "upbeat", 0, 0.6)
    return t


def final_1_video():
    t = wide("h-final-1-video", "Pantalla final: 1 video", "End screen: 1 video", "outro", 10.0, order=2201,
             tags=["pantalla final", "end screen", "youtube", "siguiente video", "suscríbete"], thumb_at=3.0,
             background="#F5F5F0")
    bg(t, "#F5F5F0")
    t.solid(t.track("shape", "Bloque"), "#FFCF56", 0, 10.0, Box(1200, 0, 720, 1080), slide_in(dx=720, length=0.6))
    _video_slot(t, "h-nature-04", Box(120, 240, 1040, 585), 0.4, 1, colour="#111111", border=8)
    label(t, t.track("text", "Antetítulo"), "SIGUIENTE VIDEO", 0.6, 9.4, Box(120, 140, 800, 70), "Poppins", 44, "#111111",
          weight=800, spacing=8, align="left", anim_in=tanim("slide-right", duration=0.4), name="Antetítulo")
    _subscribe_circle(t, "h-man-05", 1560, 430, 300, 0.8, ring_colour="#111111", text_colour="#111111")
    label(t, t.track("text", "Gracias"), "¡Gracias por ver!", 1.4, 8.6, Box(1240, 720, 640, 120), "Pacifico", 72,
          "#111111", weight=400, anim_in=tanim("pop", duration=0.4), name="Gracias")
    song(t, "upbeat", 2, 0.6)
    return t


def final_oscura():
    t = wide("h-final-oscura", "Pantalla final oscura", "Dark end screen", "outro", 10.0, order=2202,
             tags=["pantalla final", "neón", "oscura", "youtube", "gaming"], thumb_at=3.2, background="#050507")
    bg(t, "#050507")
    for k in range(1, 10):
        t.solid(t.track("shape", "Rejilla"), "#1A1A2E", 0, 10.0, Box(0, k * 108, 1920, 2))
    _video_slot(t, "h-gaming-05", Box(170, 300, 720, 405), 0.4, 1, colour="#08F7FE", border=4, glow_colour="#08F7FE")
    _video_slot(t, "h-concert-01", Box(1030, 300, 720, 405), 0.6, 2, colour="#FF2EF7", border=4, glow_colour="#FF2EF7")
    label(t, t.track("text", "Título"), "NO TE VAYAS TODAVÍA", 0.2, 9.8, Box(160, 110, 1600, 120), "Orbitron", 70,
          "#FFFFFF", weight=900, spacing=6, layers=[glow("#08F7FE", 20, 0.8), fill("#FFFFFF")],
          anim_in=tanim("flicker-in", duration=0.6), name="Título")
    _subscribe_circle(t, "h-portrait-03", 960, 860, 140, 1.0, ring_colour="#FF2EF7")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.8)], name="Brillo")
    song(t, "electro", 3, 0.6)
    return t


def final_colorida():
    t = wide("h-final-colorida", "Pantalla final colorida", "Colourful end screen", "outro", 10.0, order=2203,
             tags=["pantalla final", "colores", "divertida", "youtube", "infantil"], thumb_at=3.2, background="#FFE066")
    bg(t, "#FFE066")
    rng = random.Random(203)
    for k in range(10):
        kind = rng.choice(["ellipse", "star", "triangle", "rounded-rectangle", "heart"])
        c = rng.choice(["#FF6B6B", "#4ECDC4", "#5F27CD", "#FF9F43", "#FFFFFF"])
        s = rng.uniform(60, 140)
        x, y = rng.uniform(40, 1880), rng.uniform(40, 1040)
        t.solid(t.track("shape", "Forma"), c, 0, 10.0, centered(x, y, s, s),
                [(0, {"s": 0.0}, "back"), (0.5, {}, "smooth"), (5.0, {"dy": -40}, "smooth"), (10.0, {})], kind=kind,
                radius=20, rotation=keys([(0, 0, "linear"), (10.0, rng.uniform(-120, 120))]), alpha=0.75)
    _video_slot(t, "h-kids-01", Box(160, 300, 720, 405), 0.4, 1, radius=30)
    _video_slot(t, "h-kids-03", Box(1040, 300, 720, 405), 0.6, 2, radius=30)
    label(t, t.track("text", "Título"), "¡Más videos divertidos!", 0.2, 9.8, Box(160, 90, 1600, 150), "Chewy", 110,
          "#5F27CD", weight=400, layers=[shadow("#FFFFFF", 0, 6, 0, 1.0), fill("#5F27CD")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    _subscribe_circle(t, "h-kids-02", 960, 860, 140, 1.0, ring_colour="#FFFFFF", text_colour="#5F27CD")
    song(t, "fun", 2, 0.6)
    return t


def final_gaming():
    t = wide("h-final-gaming", "Pantalla final gaming", "Gaming end screen", "outro", 10.0, order=2204,
             tags=["pantalla final", "gaming", "gamer", "youtube", "stream"], thumb_at=3.0, background="#0E0420")
    photo_bg(t, "h-gaming-03", s1=1.06, label="Fondo", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=12)])
    shade_full(t, 0.6, colour="#0E0420")
    for i, (s, x) in enumerate([("h-gaming-01", 170), ("h-gaming-02", 1030)]):
        t.solid(t.track("shape", "Marco"), "#B026FF", 0.4 + i * 0.2, 9.6 - i * 0.2, Box(x - 30, 280, 780, 445),
                pop(0, 0.45, 0.6), kind="parallelogram", layers=[glow("#B026FF", 26, 0.9), fill("#B026FF"), no_stroke()])
        t.photo(t.track("video", f"Video {i + 1}"), s, 0.5 + i * 0.2, 9.5 - i * 0.2, Box(x, 300, 720, 405),
                pop(0, 0.45, 0.6), label=f"Video sugerido {i + 1}")
    label(t, t.track("text", "Título"), "SIGUE JUGANDO", 0.2, 9.8, Box(160, 90, 1600, 130), "Russo One", 100, "#FFFFFF",
          weight=400, spacing=8, layers=[glow("#B026FF", 20, 0.9), stroke(3, "#B026FF"), fill("#FFFFFF")],
          anim_in=tanim("glitch-in", duration=0.5), name="Título")
    _subscribe_circle(t, "h-man-04", 960, 860, 140, 1.0, ring_colour="#08F7FE")
    song(t, "electro", 1, 0.6)
    return t


def final_minimal():
    t = wide("h-final-minimal", "Pantalla final minimal", "Minimal end screen", "outro", 10.0, order=2205,
             tags=["pantalla final", "minimal", "limpia", "youtube", "elegante"], thumb_at=3.0, background="#FFFFFF")
    bg(t, "#FFFFFF")
    for i, (s, x) in enumerate([("h-interior-01", 160), ("h-interior-05", 1040)]):
        t.photo(t.track("video", f"Video {i + 1}"), s, 0.4 + i * 0.2, 9.6 - i * 0.2, Box(x, 320, 720, 405),
                [(0, {"dy": 40}, "out"), (0.6, {})], label=f"Video sugerido {i + 1}",
                opacity=keys([(0, 0.0), (0.5, 1.0)]))
        line(t, t.track("shape", "Línea"), "#111111", 0.8 + i * 0.2, 9.2 - i * 0.2, Box(x, 750, 720, 2), length=0.7)
    label(t, t.track("text", "Título"), "seguir viendo", 0.2, 9.8, Box(160, 150, 1600, 110), "Raleway", 76, "#111111",
          weight=300, spacing=16, anim_in=tanim("fade", duration=0.6), name="Título")
    label(t, t.track("text", "Canal"), "ESTUDIO NORTE · SUSCRÍBETE", 1.2, 8.8, Box(160, 860, 1600, 60), "Raleway", 34,
          "#6B6B6B", weight=500, spacing=10, anim_in=tanim("fade", duration=0.6), name="Canal")
    song(t, "calm", 0, 0.55)
    return t


def final_podcast():
    t = wide("h-final-podcast", "Cierre de podcast", "Podcast end screen", "outro", 10.0, order=2206,
             tags=["podcast", "próximo episodio", "pantalla final", "plataformas", "audio"], thumb_at=3.0,
             background="#1E1B2E")
    bg_gradient(t, [(0, "#2A1F4A"), (1, "#14121F")], angle=135)
    label(t, t.track("text", "Antetítulo"), "PRÓXIMO EPISODIO", 0.3, 9.7, Box(120, 130, 900, 70), "DM Sans", 42, "#FFB547",
          weight=800, spacing=8, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "Cómo ahorrar sin sufrir", 0.5, 9.5, Box(120, 200, 820, 260), "DM Serif Display",
          100, "#FFFFFF", weight=400, align="left", line=1.0, anim_in=tanim("rise-by-word", duration=0.5, unit="word",
          stagger=0.1), name="Título")
    _video_slot(t, "h-podcast-01", Box(1000, 260, 800, 450), 0.6, 1, colour="#FFB547", border=6)
    label(t, t.track("text", "Plataformas"), "Escúchalo también en tu app de podcasts favorita", 1.2, 8.8,
          Box(120, 520, 820, 140), "DM Sans", 44, "#C9C3E6", weight=500, align="left", line=1.2,
          anim_in=tanim("fade", duration=0.5), name="Plataformas")
    for i, g in enumerate(["🎧", "🎙", "▶"]):
        t.solid(t.track("shape", "Icono"), "#FFB547", 1.5 + i * 0.15, 8.5 - i * 0.15, centered(180 + i * 140, 760, 100, 100),
                pop(0, 0.4), kind="ellipse")
        label(t, t.track("text", "Icono"), g, 1.5 + i * 0.15, 8.5 - i * 0.15, centered(180 + i * 140, 760, 100, 100),
              "Inter", 46, "#1E1B2E", weight=700, editable=False, motion=pop(0, 0.4))
    song(t, "jazz", 2, 0.55)
    return t


def final_cocina():
    t = wide("h-final-cocina", "Cierre de cocina", "Cooking end screen", "outro", 10.0, order=2207,
             tags=["cocina", "receta", "pantalla final", "próxima receta", "comida"], thumb_at=3.0)
    photo_bg(t, "h-food-05", s1=1.05, label="Fondo", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=14)])
    shade_full(t, 0.45, colour="#2B1A0F")
    rrect(t, t.track("shape", "Tarjeta"), "#FFF6E9", 0.3, 9.7, centered(960, 560, 1500, 760), 40, pop(0, 0.45, 0.85),
          layers=[shadow("#000000", 0, 16, 40, 0.45), fill("#FFF6E9"), no_stroke()])
    label(t, t.track("text", "Título"), "Próxima receta", 0.6, 9.4, Box(300, 220, 1320, 130), "Lobster", 100, "#C2410C",
          weight=400, anim_in=tanim("pop", duration=0.4), name="Título")
    _video_slot(t, "h-cooking-04", Box(300, 380, 680, 382), 0.8, 1, colour="#C2410C", border=5)
    _video_slot(t, "h-food-01", Box(1000, 380, 620, 349), 1.0, 2, colour="#C2410C", border=5)
    label(t, t.track("text", "Llamada"), "¡Suscríbete y cocina conmigo!", 1.4, 8.6, Box(300, 820, 1320, 80), "Montserrat",
          46, "#7C2D12", weight=700, anim_in=tanim("fade", duration=0.4), name="Llamada")
    song(t, "jazz", 1, 0.55)
    return t


def final_viajes():
    t = wide("h-final-viajes", "Cierre de viajes", "Travel end screen", "outro", 10.0, order=2208,
             tags=["viajes", "destino", "pantalla final", "mapa", "aventura"], thumb_at=3.4, background="#F3E9D6")
    bg_gradient(t, [(0, "#F6EEDD"), (1, "#E8D8B9")], angle=135)
    for k in range(4):
        outline(t, t.track("shape", "Mapa"), "#C9B38C", 3, 0, 10.0, centered(400 + k * 380, 540 + (k % 2) * 200 - 100,
                520, 340), kind="ellipse", alpha=0.5)
    label(t, t.track("text", "Título"), "Siguiente destino", 0.3, 9.7, Box(160, 90, 1600, 140), "DM Serif Display", 100,
          "#1F2A44", weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15), name="Título")
    framed(t, "h-nature-01", 0.6, 9.4, Box(200, 300, 720, 405), pop(0, 0.45, 0.6), border=16, bottom=80,
           colour="#FFFDF8", rotation=keys([(0, -3)]), label="Video sugerido 1")
    framed(t, "h-beach-04", 0.8, 9.2, Box(1000, 300, 720, 405), pop(0, 0.45, 0.6), border=16, bottom=80,
           colour="#FFFDF8", rotation=keys([(0, 3)]), label="Video sugerido 2")
    for i, (txt, x, r) in enumerate([("Noruega", 560, -3), ("Maldivas", 1360, 3)]):
        label(t, t.track("text", "Lugar"), txt, 1.2 + i * 0.2, 8.6 - i * 0.2, centered(x, 790 + (i * 2 - 1) * 20, 700, 90),
              "Caveat", 70, "#1F2A44", weight=700, anim_in=tanim("typewriter", duration=0.6, unit="character"),
              rotation=keys([(0, r)]), name=f"Lugar {i + 1}")
    label(t, t.track("text", "Avión"), "✈", 0.4, 9.6, centered(960, 940, 100, 100), "Inter", 64, "#D9480F", weight=700,
          editable=False, motion=[(0, {"dx": -900}, "linear"), (9.6, {"dx": 900})])
    song(t, "world", 1, 0.55)
    return t


def final_negocio():
    t = wide("h-final-negocio", "Cierre de negocio", "Business end screen", "outro", 8.0, order=2209,
             tags=["negocio", "contacto", "dirección", "web", "cierre"], thumb_at=4.0, background="#0F172A")
    photo_bg(t, "h-shop-02", s1=1.05, label="Foto del local", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=10)])
    shade_full(t, 0.7, colour="#0F172A")
    t.photo(t.track("video", "Logo"), "logo-07", 0.3, 7.7, centered(480, 470, 380, 380), pop(0, 0.5), label="Tu logo")
    rows = [("🌐", "www.tunegocio.com"), ("📞", "+00 123 456 789"), ("📍", "Calle Principal 123"), ("🕘", "Lun a sáb · 9 a 19 h")]
    for i, (g, txt) in enumerate(rows):
        at = 0.8 + i * 0.3
        y = 290 + i * 140
        t.solid(t.track("shape", "Icono"), "#22C55E", at, 8.0 - at, centered(990, y + 45, 90, 90), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Icono"), g, at, 8.0 - at, centered(990, y + 45, 90, 90), "Inter", 44, "#FFFFFF",
              weight=400, editable=False, motion=pop(0, 0.35))
        label(t, t.track("text", "Dato"), txt, at + 0.1, 7.9 - at, Box(1070, y, 800, 90), "Montserrat", 50, "#FFFFFF",
              weight=600, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.1), name=f"Dato {i + 1}")
    song(t, "upbeat", 3, 0.55)
    return t


def final_curso():
    t = wide("h-final-curso", "Cierre de curso", "Course end screen", "outro", 10.0, order=2210,
             tags=["curso", "lección", "educación", "pantalla final", "tutorial"], thumb_at=3.0, background="#EEF2FF")
    bg(t, "#EEF2FF")
    label(t, t.track("text", "Lección"), "Terminaste la lección 3 de 10", 0.3, 9.7, Box(120, 110, 1000, 80), "Lexend",
          52, "#312E81", weight=700, align="left", anim_in=tanim("fade", duration=0.4), name="Progreso")
    rrect(t, t.track("shape", "Barra"), "#C7D2FE", 0.4, 9.6, Box(120, 210, 820, 26), 13)
    rrect(t, t.track("shape", "Barra"), "#4F46E5", 0.4, 9.6, Box(120, 210, 246, 26), 13, [(0, {"sx": 0.0, "dx": -123}, "out"),
                                                                                          (1.0, {})])
    label(t, t.track("text", "Siguiente"), "SIGUIENTE:", 0.8, 9.2, Box(120, 330, 820, 60), "Lexend", 40, "#4F46E5",
          weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "Lección 4: luces y sombras", 1.0, 9.0, Box(120, 390, 820, 250), "Lexend", 84,
          "#1E1B4B", weight=800, align="left", line=1.05, anim_in=tanim("rise-by-word", duration=0.4, unit="word",
          stagger=0.1), name="Título")
    _video_slot(t, "h-classroom-04", Box(1020, 300, 780, 439), 0.6, 1, colour="#4F46E5", border=6)
    _subscribe_circle(t, "h-portrait-01", 300, 840, 130, 1.4, ring_colour="#4F46E5", text_colour="#312E81")
    song(t, "fun", 3, 0.55)
    return t


def final_familia():
    t = wide("h-final-familia", "Cierre familiar", "Family ending", "outro", 9.0, order=2211,
             tags=["familia", "gracias", "cierre", "recuerdos", "fotos"], thumb_at=5.0, background="#FDF6EC")
    bg(t, "#FDF6EC")
    spots = [("h-family-02", Box(120, 120, 560, 380), -6), ("h-family-05", Box(1240, 100, 560, 380), 5),
             ("h-family-06", Box(160, 600, 520, 350), 4), ("h-mother-02", Box(1260, 600, 520, 350), -4)]
    for i, (s, box, r) in enumerate(spots):
        framed(t, s, 0.3 + i * 0.3, 8.7 - i * 0.3, box, [(0, {"s": 1.3}, "out"), (0.45, {})], border=14,
               colour="#FFFFFF", rotation=keys([(0, r * 2, "out"), (0.45, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Gracias"), "Gracias por ver", 1.5, 7.5, Box(560, 380, 800, 300), "Dancing Script", 130,
          "#9C2C5C", weight=700, line=1.0, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Gracias")
    label(t, t.track("text", "Corazón"), "♥", 2.8, 6.2, centered(960, 700, 120, 120), "Inter", 90, "#E5486F", weight=400,
          editable=False, motion=pop(0, 0.4), anim_loop=tanim("pulse", amount=8, speed=1.2))
    song(t, "romantic", 2, 0.55)
    return t


def final_papel():
    t = wide("h-final-papel", "Cierre de papel", "Paper end screen", "outro", 10.0, order=2212,
             tags=["papel", "manualidades", "pantalla final", "cinta", "creativo"], thumb_at=3.2, background="#E8E1D6")
    bg_gradient(t, [(0, "#EFE9DF"), (1, "#DDD3C3")], angle=90)
    for i, (s, x, r) in enumerate([("h-kids-05", 180, -3), ("h-spring-02", 1020, 2)]):
        framed(t, s, 0.4 + i * 0.2, 9.6 - i * 0.2, Box(x, 300, 720, 405), [(0, {"dy": -900}, "out"), (0.6, {})],
               border=18, colour="#FFFFFF", rotation=keys([(0, r)]), label=f"Video sugerido {i + 1}")
        for side in (-1, 1):
            t.solid(t.track("shape", "Cinta"), "#F7C8A0", 1.0 + i * 0.2, 9.0 - i * 0.2,
                    centered(x + 360 + side * 300, 290, 180, 50), pop(0, 0.3), alpha=0.85,
                    rotation=keys([(0, side * 25 + r)]))
    label(t, t.track("text", "Título"), "¿Hacemos otro?", 0.2, 9.8, Box(160, 80, 1600, 150), "Chewy", 110, "#5A2E1B",
          weight=400, anim_in=tanim("drop", duration=0.5, unit="character", stagger=0.03), name="Título")
    label(t, t.track("text", "Sub"), "suscríbete para más ideas", 1.4, 8.6, Box(460, 860, 1000, 90), "Patrick Hand", 66,
          "#8A4B2F", weight=400, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    song(t, "fun", 3, 0.55)
    return t


def final_retro():
    t = wide("h-final-retro", "Cierre de TV retro", "Retro TV end screen", "outro", 10.0, order=2213,
             tags=["retro", "televisión", "vintage", "pantalla final", "80s"], thumb_at=3.2, background="#3B2A20")
    bg_gradient(t, [(0, "#E9C46A"), (1, "#F4A261")], angle=90)
    for i, (s, x) in enumerate([("h-city-01", 520), ("h-summer-03", 1400)]):
        cx = x
        rrect(t, t.track("shape", "Tele"), "#6B4226", 0.3 + i * 0.2, 9.7 - i * 0.2, centered(cx, 560, 800, 600), 60,
              pop(0, 0.45, 0.6), layers=[shadow("#000000", 0, 16, 30, 0.35), fill("#6B4226"), no_stroke()])
        for side in (-1, 1):
            t.solid(t.track("shape", "Antena"), "#3B2A20", 0.5 + i * 0.2, 9.5 - i * 0.2, centered(cx + side * 90, 210, 8, 220),
                    pop(0, 0.4), rotation=keys([(0, side * 25)]))
        t.photo(t.track("video", f"Video {i + 1}"), s, 0.5 + i * 0.2, 9.5 - i * 0.2, centered(cx - 50, 560, 600, 450),
                pop(0, 0.45, 0.6), label=f"Video sugerido {i + 1}",
                effects=[effect("stylize.vhs", noise=22, chroma=3)])
        for k in range(2):
            t.solid(t.track("shape", "Perilla"), "#E9C46A", 0.6 + i * 0.2, 9.4 - i * 0.2, centered(cx + 320, 470 + k * 130, 60, 60),
                    pop(0, 0.4), kind="ellipse")
    label(t, t.track("text", "Título"), "No cambies de canal", 0.2, 9.8, Box(160, 920, 1600, 130), "Shrikhand", 84,
          "#6B4226", weight=400, anim_in=tanim("pop", duration=0.4), name="Título")
    song(t, "jazz", 2, 0.55)
    return t


def final_noticias():
    t = wide("h-final-noticias", "Cierre informativo", "News end screen", "outro", 10.0, order=2214,
             tags=["noticias", "más noticias", "pantalla final", "informativo", "titulares"], thumb_at=3.4,
             background="#0A1B3D")
    bg_gradient(t, [(0, "#0D2A66"), (1, "#06102A")], angle=90)
    t.solid(t.track("shape", "Franja"), "#E10600", 0.2, 9.8, Box(0, 80, 700, 110), slide_in(dx=-700, length=0.4))
    label(t, t.track("text", "Título"), "MÁS NOTICIAS", 0.4, 9.6, Box(60, 80, 640, 110), "Oswald", 76, "#FFFFFF",
          weight=700, spacing=6, align="left", name="Título")
    heads = [("h-city-05", "La ciudad estrena tranvía"), ("h-nature-02", "Récord de visitantes en el parque"),
             ("h-concert-02", "Festival de música este sábado")]
    for i, (s, h) in enumerate(heads):
        x = 120 + i * 580
        at = 0.6 + i * 0.25
        _video_slot(t, s, Box(x, 300, 520, 293), at, i + 1, border=4, radius=8)
        label(t, t.track("text", "Titular"), h, at + 0.2, 10.0 - at - 0.2, Box(x, 620, 520, 150), "Oswald", 46, "#FFFFFF",
              weight=500, align="left", valign="top", anim_in=tanim("fade", duration=0.4), name=f"Titular {i + 1}")
    song(t, "epic", 5, 0.5)
    return t


# --- Slideshows ---------------------------------------------------------------------------------

def _title_card(t, text, t0, dur, font, size, colour, box=None, sub=None, sub_font="Montserrat", sub_colour=None,
                layers=None, anim="blur-in"):
    box = box or Box(160, 380, 1600, 260)
    label(t, t.track("text", "Título"), text, t0, dur, box, font, size, colour, weight=400 if font in (
          "Great Vibes", "Dancing Script", "Pacifico", "Lobster", "Caveat", "Sacramento", "Kaushan Script",
          "DM Serif Display", "Bebas Neue", "Anton") else 700, layers=layers,
          anim_in=tanim(anim, duration=0.8), anim_out=tanim("fade", duration=0.5), name="Título")
    if sub:
        label(t, t.track("text", "Subtítulo"), sub, t0 + 0.4, dur - 0.4, Box(box.x, box.y + box.h, box.w, 80), sub_font, 46,
              sub_colour or colour, weight=500, spacing=6, anim_in=tanim("fade", duration=0.6),
              anim_out=tanim("fade", duration=0.5), name="Subtítulo")


def presenta_recuerdos():
    t = wide("h-presenta-recuerdos", "Recuerdos", "Memories slideshow", "slideshow", 16.0, order=2215,
             tags=["recuerdos", "presentación", "fotos", "familia", "nostalgia"], thumb_at=1.6)
    samples = ["h-family-04", "h-elderly-02", "h-father-03", "h-mother-03", "h-family-01", "h-elderly-01"]
    slides(t, samples, 0.0, 2.6, transition="crossfade", tdur=0.8, kb_amount=0.09,
           effects_fn=lambda i: [effect("color.basic", fade=0.12, temperature=0.08)])
    shade_full(t, 0.25, 0.0, 3.6)
    _title_card(t, "Recuerdos", 0.4, 3.0, "Dancing Script", 200, "#FFFFFF", sub="de nuestra familia",
                layers=[shadow("#000000", 0, 6, 18, 0.5), fill("#FFFFFF")])
    label(t, t.track("text", "Cierre"), "siempre juntos", 13.6, 2.4, Box(160, 420, 1600, 200), "Dancing Script", 160,
          "#FFFFFF", weight=700, layers=[shadow("#000000", 0, 6, 18, 0.5), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=0.8), name="Frase final")
    grain(t, 0.15)
    vignette(t, 0.45)
    song(t, "romantic", 0, 0.8)
    return t


def presenta_polaroid():
    t = wide("h-presenta-polaroid", "Polaroids sobre madera", "Polaroids on wood", "slideshow", 14.0, order=2216,
             tags=["polaroid", "fotos", "presentación", "madera", "vintage", "álbum"], thumb_at=11.0, background="#5B3A24")
    bg_gradient(t, [(0, "#7A5236"), (0.5, "#5B3A24"), (1, "#6E4A30")], angle=0)
    for k in range(9):
        t.solid(t.track("shape", "Veta"), "#3E2616", 0, 14.0, Box(0, 60 + k * 120, 1920, 3), alpha=0.35)
    rng = random.Random(216)
    samples = ["h-summer-02", "h-beach-02", "h-couple-01", "h-travel-03", "h-birthday-01",
               "h-pet-04", "h-autumn-02"]
    for i, s in enumerate(samples):
        at = 0.3 + i * 1.6
        x, y = rng.uniform(380, 1540), rng.uniform(330, 700)
        r = rng.uniform(-12, 12)
        framed(t, s, at, 14.0 - at, centered(x, y, 440, 420), [(0, {"s": 1.5, "dy": -200}, "out"), (0.5, {})],
               border=20, bottom=100, colour="#FFFDF8", rotation=keys([(0, r * 2, "out"), (0.5, r)]),
               label=f"Foto {i + 1}", shadow_alpha=0.5)
    label(t, t.track("text", "Título"), "nuestro verano", 12.0, 2.0, Box(160, 860, 1600, 160), "Caveat", 130, "#FFFFFF",
          weight=700, layers=[shadow("#000000", 0, 6, 14, 0.6), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Título")
    song(t, "upbeat", 6, 0.8)
    return t


def presenta_tinta():
    t = wide("h-presenta-tinta", "Presentación de tinta", "Ink slideshow", "slideshow", 14.0, order=2217,
             tags=["tinta", "artístico", "presentación", "fotos", "elegante"], thumb_at=6.6, background="#FFFFFF")
    bg(t, "#FFFFFF")
    samples = ["h-spring-03", "h-nature-05", "h-couple-03", "h-autumn-01", "h-winter-03"]
    clips = slides(t, samples, 0.0, 2.8, transition="ink_bleed", tdur=1.0, kb_amount=0.06)
    captions = ["primavera", "montañas", "atardecer", "otoño", "invierno"]
    for i, c in enumerate(captions):
        label(t, t.track("text", "Pie"), c, i * 2.8 + 0.8, 1.8, Box(120, 870, 900, 140), "Sacramento", 110, "#FFFFFF",
              weight=400, align="left", layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
              anim_in=tanim("blur-in", duration=0.6), anim_out=tanim("fade", duration=0.4), name=f"Pie {i + 1}")
    song(t, "calm", 1, 0.75)
    return t


def presenta_glitch():
    t = wide("h-presenta-glitch", "Presentación glitch", "Glitch slideshow", "slideshow", 8.0, order=2218,
             tags=["glitch", "rápida", "ritmo", "fotos", "urbano", "presentación"], thumb_at=4.25, background="#000000")
    samples = ["h-city-04", "h-concert-01", "h-gaming-01", "h-city-06", "h-portrait-03", "h-concert-03", "h-man-04",
               "h-city-02", "h-tech-01", "h-concert-02", "h-portrait-05", "h-city-05", "h-gaming-02", "h-man-03",
               "h-city-03", "h-concert-04"]
    slides(t, samples, 0.0, 0.5, transition=None, kb_amount=0.12,
           effects_fn=lambda i: [effect("color.basic", contrast=0.3, saturation=0.2)])
    t.adjust([effect("rgb_split", animated={"amount": spike([0.5 * k for k in range(1, 16)], 22, 0.15)}),
              effect("digital_glitch", animated={"intensity": spike([0.5 * k for k in range(2, 16, 2)], 0.9, 0.2)},
                     rgbAmount=14)], name="Glitch")
    label(t, t.track("text", "Título"), "NOCHE EN LA CIUDAD", 2.0, 4.0, Box(160, 420, 1600, 200), "Russo One", 140,
          "#FFFFFF", weight=400, spacing=8, layers=[shadow("#FF2E63", 8, 0, 0, 0.9), shadow("#08F7FE", -8, 0, 0, 0.9,
          id="shadow2"), fill("#FFFFFF")], anim_in=tanim("glitch-in", duration=0.4), name="Título")
    song(t, "electro", 0, 0.85)
    return t


def presenta_pelicula():
    t = wide("h-presenta-pelicula", "Tira de película", "Film strip slideshow", "slideshow", 12.0, order=2219,
             tags=["película", "tira", "35 mm", "fotos", "vintage", "cine"], thumb_at=4.0, background="#151515")
    bg(t, "#151515")
    strip = t.track("shape", "Tira")
    move = [(0, {"dx": 1100}, "linear"), (12.0, {"dx": -1500})]
    t.solid(strip, "#0A0A0A", 0, 12.0, Box(-200, 260, 4400, 560), move)
    holes = t.track("shape", "Perforaciones")
    for k in range(40):
        for y in (285, 775):
            t.solid(holes, "#3A3A3A", 0, 12.0, Box(-180 + k * 110, y, 60, 22), move, radius=5, kind="rounded-rectangle")
    samples = ["h-travel-01", "h-travel-04", "h-nature-04", "h-beach-03", "h-city-02", "h-travel-07", "h-nature-06"]
    for i, s in enumerate(samples):
        t.photo(t.track("video", f"Cuadro {i + 1}"), s, 0, 12.0, Box(-150 + i * 620, 330, 580, 420), move,
                label=f"Foto {i + 1}", effects=[effect("color.basic", fade=0.15, temperature=0.12)])
    label(t, t.track("text", "Título"), "Ruta por el sur", 0.3, 11.4, Box(160, 860, 1600, 150), "Special Elite", 90,
          "#E9E2D0", weight=400, anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Título")
    label(t, t.track("text", "Rollo"), "KODA 400  ▸ 12", 0.3, 11.4, Box(160, 120, 800, 80), "Special Elite", 44, "#E0A33A",
          weight=400, align="left", anim_in=tanim("fade", duration=0.6), name="Rótulo")
    grain(t, 0.25)
    song(t, "calm", 3, 0.75)
    return t


def presenta_mosaico():
    t = wide("h-presenta-mosaico", "Mosaico de fotos", "Photo mosaic", "slideshow", 10.0, order=2220,
             tags=["mosaico", "cuadrícula", "collage", "fotos", "grid"], thumb_at=4.0, background="#FFFFFF")
    bg(t, "#FFFFFF")
    samples = ["h-food-01", "h-cafe-03", "h-food-04", "h-cooking-02", "h-food-06", "h-cafe-05", "h-food-02",
               "h-cooking-05", "h-food-03"]
    g = 12
    cw, ch = (1920 - 4 * g) / 3, (1080 - 4 * g) / 3
    order = [4, 0, 8, 2, 6, 1, 7, 3, 5]
    for rank, i in enumerate(order):
        r, c = divmod(i, 3)
        box = Box(g + c * (cw + g), g + r * (ch + g), cw, ch)
        at = 0.2 + rank * 0.3
        t.photo(t.track("video", f"Celda {i + 1}"), samples[i], at, 10.0 - at, box,
                [(0, {"s": 0.0}, "back"), (0.45, {}, "linear"), (6.0 - at, {}), (7.0 - at, {"s": 1.0})],
                label=f"Foto {i + 1}")
    label(t, t.track("text", "Título"), "Sabores de la semana", 4.0, 6.0, Box(360, 400, 1200, 280), "DM Serif Display", 120,
          "#FFFFFF", weight=400, box_bg=("#111111", 0.75), box_pad=34, box_radius=20, anim_in=tanim("pop", duration=0.5),
          name="Título")
    song(t, "jazz", 3, 0.75)
    return t


def presenta_paralaje():
    t = wide("h-presenta-paralaje", "Paralaje", "Parallax slideshow", "slideshow", 15.0, order=2221,
             tags=["paralaje", "3d", "movimiento", "fotos", "viaje", "cinemático"], thumb_at=4.0, background="#000000")
    samples = [("h-nature-01", "LAGO"), ("h-nature-02", "VALLE"), ("h-nature-05", "CUMBRE"), ("h-winter-01", "NIEVE"),
               ("h-beach-05", "MAR")]
    v = t.track("video", "Fotos")
    prev = None
    for i, (s, word) in enumerate(samples):
        at = i * 3.0
        d = 3.0 + (0.6 if i < len(samples) - 1 else 0)
        clip = t.photo(v, s, at, d, Box(-120, -60, 2160, 1200), [(0, {"dx": 100}, "linear"), (d, {"dx": -100})],
                       label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, "slide_left", 0.6)
        prev = clip
        label(t, t.track("text", "Palabra"), word, at + 0.3, 2.6, Box(0, 330, 1920, 420), "Bebas Neue", 420, "#FFFFFF",
              weight=400, spacing=30, layers=[fill("#FFFFFF", 0.85)], motion=[(0, {"dx": 500}, "linear"), (2.6, {"dx": -500})],
              anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.4), name=f"Palabra {i + 1}")
    song(t, "epic", 2, 0.8)
    return t


def presenta_viaje():
    t = wide("h-presenta-viaje", "Diario de viaje", "Travel diary", "slideshow", 15.0, order=2222,
             tags=["viaje", "diario", "sellos", "fotos", "vacaciones", "pasaporte"], thumb_at=4.2, background="#EFE6D2")
    bg_gradient(t, [(0, "#F4ECDB"), (1, "#E3D4B4")], angle=120)
    places = [("h-travel-06", "Día 1 · Montañas", "#B23A48"), ("h-beach-01", "Día 2 · La costa", "#1D3557"),
              ("h-city-03", "Día 3 · La ciudad", "#2A9D8F"), ("h-travel-02", "Día 4 · El camino", "#E76F51"),
              ("h-nature-04", "Día 5 · El lago", "#6D597A")]
    for i, (s, cap, c) in enumerate(places):
        at = i * 3.0
        d = 3.0
        framed(t, s, at, d, Box(260, 120, 900, 680), [(0, {"dx": -1400}, "out"), (0.6, {}, "linear"), (d, {"s": 1.02})],
               border=18, colour="#FFFFFF", rotation=keys([(0, -2 + i % 2 * 3)]), label=f"Foto {i + 1}")
        ring(t, t.track("shape", "Sello"), c, 8, at + 0.6, d - 0.6, centered(1460, 360, 320, 320),
             [(0, {"s": 1.6}, "snap"), (0.25, {})], opacity=keys([(0, 0.0), (0.1, 0.85)]), rotation=keys([(0, 12)]))
        label(t, t.track("text", "Sello"), "VISITADO", at + 0.6, d - 0.6, centered(1460, 360, 320, 100), "Black Ops One",
              54, c, weight=400, editable=False, motion=[(0, {"s": 1.6}, "snap"), (0.25, {})], rotation=keys([(0, 12)]),
              layers=[fill(c, 0.85)])
        label(t, t.track("text", "Pie"), cap, at + 0.5, d - 0.5, Box(1220, 620, 640, 200), "Caveat", 84, "#2B2118",
              weight=700, anim_in=tanim("typewriter", duration=0.6, unit="character"), name=f"Pie {i + 1}")
    grain(t, 0.12)
    song(t, "world", 2, 0.75)
    return t


def presenta_boda():
    t = wide("h-presenta-boda", "Nuestra boda", "Our wedding", "slideshow", 16.0, order=2223,
             tags=["boda", "novios", "presentación", "elegante", "matrimonio", "fotos"], thumb_at=1.8, background="#FBF8F3")
    bg(t, "#FBF8F3")
    samples = ["h-wedding-04", "h-wedding-01", "h-wedding-05", "h-wedding-03", "h-wedding-06"]
    v = t.track("video", "Fotos")
    prev = None
    for i, s in enumerate(samples):
        at = 1.0 + i * 2.8
        d = 2.8 + (0.8 if i < len(samples) - 1 else 0)
        clip = t.photo(v, s, at, min(d, 16.0 - at), Box(360, 120, 1200, 760), kb(d, 1.0, 1.06), label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, "crossfade", 0.8)
        prev = clip
    outline(t, t.track("shape", "Marco"), "#C9A44C", 3, 0.6, 15.4, Box(330, 90, 1260, 820), alpha=0.9)
    label(t, t.track("text", "Nombres"), "Sofía & Daniel", 0.2, 15.8, Box(160, 920, 1600, 140), "Great Vibes", 110,
          "#8C6B2F", weight=400, anim_in=tanim("blur-in", duration=1.0), name="Nombres")
    for side in (-1, 1):
        t.solid(t.track("shape", "Adorno"), "#C9A44C", 0.6, 15.4, centered(960 + side * 450, 990, 220, 2),
                [(0, {"sx": 0.0}, "out"), (0.8, {})])
    dots(t, ["#E8C27A", "#FFFFFF"], 16, 0.5, 15.5, seed=223, size=(8, 14), kinds=("star",), area=Box(360, 120, 1200, 760),
         drift=60)
    song(t, "romantic", 1, 0.8)
    return t


def presenta_bebe():
    t = wide("h-presenta-bebe", "Mi bebé crece", "Baby month by month", "slideshow", 15.0, order=2224,
             tags=["bebé", "mes a mes", "crecimiento", "familia", "primer año"], thumb_at=4.2, background="#FDF0F5")
    bg_gradient(t, [(0, "#FDF0F5"), (1, "#E8F4FD")], angle=90)
    months = ["1 mes", "2 meses", "3 meses", "4 meses", "5 meses", "6 meses"]
    samples = ["h-baby-02", "h-baby-01", "h-baby-03", "h-baby-04", "h-father-04", "h-mother-01"]
    for i, (m, s) in enumerate(zip(months, samples)):
        at = i * 2.5
        circle_photo(t, s, at, 2.5, centered(700, 540, 700, 700), [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"),
                                                                  (2.5, {"s": 1.03})], ring_colour="#FFFFFF",
                     ring_width=16, label=f"Foto {i + 1}")
        label(t, t.track("text", "Mes"), m, at + 0.2, 2.3, Box(1150, 380, 700, 220), "Baloo 2", 150, "#F28AB2", weight=800,
              align="left", layers=[shadow("#FFFFFF", 0, 6, 0, 1.0), fill("#F28AB2")], anim_in=tanim("pop", duration=0.4),
              name=f"Mes {i + 1}")
    label(t, t.track("text", "Nombre"), "Lucas", 0.2, 14.8, Box(1150, 600, 700, 140), "Pacifico", 96, "#7FB3D5",
          weight=400, align="left", anim_in=tanim("fade", duration=0.6), name="Nombre")
    dots(t, ["#F9C6D9", "#BDE0FE", "#FFFFFF"], 20, 0, 15.0, seed=224, size=(16, 40), kinds=("star", "heart", "ellipse"),
         drift=80)
    song(t, "fun", 4, 0.75)
    return t


def presenta_anio():
    t = wide("h-presenta-anio", "Nuestro año", "Our year", "slideshow", 15.0, order=2225,
             tags=["año", "resumen", "12 meses", "recap", "fotos", "año nuevo"], thumb_at=6.6, background="#0E0E10")
    months = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    samples = ["h-winter-02", "h-couple-02", "h-spring-01", "h-easter-03", "h-spring-03", "h-summer-01", "h-beach-02",
               "h-travel-05", "h-school-02", "h-autumn-02", "h-thanksgiving-02", "h-christmas-03"]
    slides(t, samples, 1.5, 1.0, transition=None, kb_amount=0.1)
    nums = t.track("text", "Mes")
    for i, m in enumerate(months):
        label(t, nums, m, 1.5 + i * 1.0, 1.0, Box(80, 860, 600, 160), "Bebas Neue", 140, "#FFFFFF", weight=400,
              layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], anim_in=tanim("slide-up", duration=0.25),
              editable=False)
    t.solid(t.track("shape", "Portada"), "#0E0E10", 0, 1.6)
    label(t, t.track("text", "Año"), "2026", 0.1, 1.5, Box(160, 300, 1600, 480), "Bebas Neue", 460, "#FFD84D", weight=400,
          anim_in=tanim("zoom-out", duration=0.5), name="Año")
    t.solid(t.track("shape", "Barra"), "#FFD84D", 1.5, 12.0, Box(0, 1060, 1920, 20), [(0, {"sx": 0.0, "dx": -960}, "linear"),
                                                                                    (12.0, {})])
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.5 + k for k in range(12)], 0.3, 0.25)})], name="Pulso")
    song(t, "upbeat", 0, 0.85)
    return t


def presenta_graduacion():
    t = wide("h-presenta-graduacion", "Generación", "Graduating class", "slideshow", 14.0, order=2226,
             tags=["graduación", "generación", "promoción", "colegio", "universidad"], thumb_at=11.6, background="#0A1F44")
    bg(t, "#0A1F44")
    samples = ["h-graduation-01", "h-classroom-02", "h-graduation-02", "h-classroom-03", "h-graduation-04"]
    slides(t, samples, 0.0, 2.4, Box(0, 0, 1920, 900), transition="blur_dissolve", tdur=0.6, kb_amount=0.08)
    t.solid(t.track("shape", "Banda"), "#0A1F44", 0, 14.0, Box(0, 880, 1920, 200))
    line(t, t.track("shape", "Filete"), "#D4AF37", 0.3, 13.7, Box(0, 880, 1920, 6), length=1.0)
    label(t, t.track("text", "Generación"), "GENERACIÓN 2026", 0.5, 13.5, Box(120, 900, 1100, 160), "Playfair Display", 96,
          "#D4AF37", weight=700, align="left", spacing=6, anim_in=tanim("fade", duration=0.8), name="Generación")
    label(t, t.track("text", "Escuela"), "Colegio San Martín", 0.9, 13.1, Box(1100, 900, 700, 160), "Montserrat", 46,
          "#FFFFFF", weight=500, align="right", anim_in=tanim("fade", duration=0.8), name="Escuela")
    label(t, t.track("text", "Birrete"), "🎓", 11.0, 3.0, centered(960, 440, 300, 300), "Inter", 220, "#FFFFFF",
          weight=400, editable=False, motion=pop(0, 0.5))
    shade_full(t, 0.45, 12.0 - 1.0, 3.0)
    label(t, t.track("text", "Final"), "¡Lo logramos!", 11.2, 2.8, Box(160, 560, 1600, 200), "Playfair Display", 140,
          "#FFFFFF", weight=800, anim_in=tanim("pop", duration=0.4), name="Frase final")
    confetti(t, ["#D4AF37", "#FFFFFF", "#9FB4D9"], 11.0, 3.0, seed=226, lanes=3, density=0.2)
    song(t, "epic", 4, 0.8)
    return t


def presenta_inmueble():
    t = wide("h-presenta-inmueble", "Recorrido de propiedad", "Property tour", "slideshow", 16.0, order=2227,
             tags=["inmobiliaria", "casa", "venta", "alquiler", "propiedad", "tour"], thumb_at=5.0, background="#F5F1EA")
    samples = ["h-house-02", "h-interior-03", "h-interior-05", "h-interior-01", "h-house-04"]
    slides(t, samples, 0.0, 3.2, transition="crossfade", tdur=0.7, kb_amount=0.07)
    rrect(t, t.track("shape", "Ficha"), "#1F3A5F", 0.5, 15.5, Box(80, 700, 820, 300), 24, slide_in(dx=-900, length=0.5),
          layers=[shadow("#000000", 0, 14, 30, 0.4), fill("#1F3A5F", 0.94), no_stroke()])
    label(t, t.track("text", "Precio"), "$320.000", 0.8, 15.2, Box(120, 720, 760, 110), "Montserrat", 86, "#C9A227",
          weight=800, align="left", anim_in=tanim("fade", duration=0.4), name="Precio")
    label(t, t.track("text", "Datos"), "🛏 3 dormitorios   🛁 2 baños   📐 140 m²", 1.0, 15.0, Box(120, 830, 760, 70),
          "Montserrat", 38, "#FFFFFF", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Datos")
    label(t, t.track("text", "Zona"), "Barrio Los Álamos · Entrega inmediata", 1.2, 14.8, Box(120, 905, 760, 60),
          "Montserrat", 32, "#BFD0E6", weight=400, align="left", anim_in=tanim("fade", duration=0.4), name="Zona")
    pill(t, t.track("shape", "Insignia"), "#C9A227", 0.3, 15.7, Box(80, 80, 330, 80), pop(0, 0.4))
    label(t, t.track("text", "Insignia"), "EN VENTA", 0.3, 15.7, Box(80, 80, 330, 80), "Montserrat", 42, "#1F3A5F",
          weight=800, spacing=6, name="Insignia")
    song(t, "calm", 4, 0.7)
    return t


def presenta_portafolio():
    t = wide("h-presenta-portafolio", "Portafolio", "Portfolio", "slideshow", 15.0, order=2228,
             tags=["portafolio", "trabajos", "diseño", "fotografía", "proyectos", "creativo"], thumb_at=4.0,
             background="#FAFAFA")
    bg(t, "#FAFAFA")
    works = [("h-studio-01", "Retratos de estudio", "2026"), ("h-interior-02", "Casa Aurora", "2025"),
             ("h-product-01", "Bodegón natural", "2025"), ("h-studio-02", "Campaña otoño", "2024"),
             ("h-house-05", "Refugio de piedra", "2024")]
    for i, (s, name, year) in enumerate(works):
        at = i * 3.0
        t.photo(t.track("video", f"Trabajo {i + 1}"), s, at, 3.0, Box(720, 90, 1110, 900),
                [(0, {"dx": 300}, "out"), (0.6, {}, "linear"), (3.0, {"s": 1.02})], label=f"Trabajo {i + 1}",
                opacity=keys([(0, 0.0), (0.4, 1.0)]))
        label(t, t.track("text", "Número"), f"0{i + 1}", at + 0.2, 2.8, Box(100, 300, 560, 160), "Raleway", 130, "#D0D0D0",
              weight=200, align="left", anim_in=tanim("fade", duration=0.4), editable=False)
        label(t, t.track("text", "Proyecto"), name, at + 0.3, 2.7, Box(100, 470, 600, 200), "Raleway", 72, "#111111",
              weight=600, align="left", line=1.05, anim_in=tanim("slide-up", duration=0.4), name=f"Proyecto {i + 1}")
        label(t, t.track("text", "Año"), year, at + 0.4, 2.6, Box(100, 690, 560, 60), "Raleway", 36, "#888888", weight=400,
              align="left", spacing=8, anim_in=tanim("fade", duration=0.4), name=f"Año {i + 1}")
    label(t, t.track("text", "Firma"), "MARINA ESTUDIO", 0.2, 14.8, Box(100, 110, 600, 60), "Raleway", 34, "#111111",
          weight=700, spacing=10, align="left", anim_in=tanim("fade", duration=0.5), name="Firma")
    song(t, "calm", 3, 0.65)
    return t


def presenta_producto():
    t = wide("h-presenta-producto", "Catálogo de productos", "Product catalogue", "slideshow", 14.0, order=2229,
             tags=["catálogo", "productos", "tienda", "precios", "ventas", "colección"], thumb_at=4.0,
             background="#F2EDE7")
    bg(t, "#F2EDE7")
    items = [("h-product-01", "Jarrón Lino", "$35"), ("h-product-03", "Set Arena", "$58"),
             ("h-product-04", "Kit Calma", "$42"), ("h-school-02", "Cuadernos Pastel", "$12")]
    for i, (s, name, price) in enumerate(items):
        at = i * 3.5
        rrect(t, t.track("shape", "Fondo"), "#FFFFFF", at, 3.5, Box(960, 90, 860, 900), 40,
              [(0, {"dy": 60}, "out"), (0.5, {})], opacity=keys([(0, 0.0), (0.4, 1.0)]))
        t.photo(t.track("video", f"Producto {i + 1}"), s, at + 0.1, 3.4, Box(1000, 130, 780, 820),
                [(0, {"s": 0.9}, "out"), (0.5, {}, "linear"), (3.4, {"s": 1.03})], label=f"Producto {i + 1}",
                opacity=keys([(0, 0.0), (0.4, 1.0)]))
        label(t, t.track("text", "Nombre"), name, at + 0.3, 3.2, Box(120, 380, 780, 140), "DM Serif Display", 100,
              "#2D2A26", weight=400, align="left", anim_in=tanim("slide-up", duration=0.4), name=f"Producto {i + 1}")
        label(t, t.track("text", "Precio"), price, at + 0.5, 3.0, Box(120, 540, 500, 120), "Montserrat", 90, "#C65D3B",
              weight=800, align="left", anim_in=tanim("pop", duration=0.35), name=f"Precio {i + 1}")
    label(t, t.track("text", "Tienda"), "NUEVA COLECCIÓN", 0.2, 13.8, Box(120, 140, 780, 60), "Montserrat", 36,
          "#2D2A26", weight=700, spacing=10, align="left", anim_in=tanim("fade", duration=0.5), name="Colección")
    song(t, "jazz", 0, 0.65)
    return t


def presenta_equipo():
    t = wide("h-presenta-equipo", "Nuestro equipo", "Meet the team", "slideshow", 10.0, order=2230,
             tags=["equipo", "personas", "empresa", "nosotros", "staff"], thumb_at=6.0, background="#0F172A")
    bg_gradient(t, [(0, "#1E293B"), (1, "#0F172A")], angle=90)
    label(t, t.track("text", "Título"), "Conoce al equipo", 0.2, 9.8, Box(160, 70, 1600, 140), "Sora", 96, "#FFFFFF",
          weight=800, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.02), name="Título")
    people = [("h-man-01", "Diego", "Dirección"), ("h-portrait-02", "Ana", "Diseño"), ("h-man-05", "Iván", "Ventas"),
              ("h-portrait-05", "Zoe", "Soporte")]
    for i, (s, n, r) in enumerate(people):
        x = 300 + i * 440
        at = 0.8 + i * 0.4
        circle_photo(t, s, at, 10.0 - at, centered(x, 470, 320, 320), pop(0, 0.5), ring_colour="#38BDF8", ring_width=8,
                     label=f"Foto {i + 1}")
        label(t, t.track("text", "Nombre"), n, at + 0.3, 9.7 - at, centered(x, 700, 400, 80), "Sora", 56, "#FFFFFF",
              weight=700, anim_in=tanim("fade", duration=0.3), name=f"Nombre {i + 1}")
        label(t, t.track("text", "Cargo"), r, at + 0.4, 9.6 - at, centered(x, 770, 400, 60), "Sora", 36, "#38BDF8",
              weight=500, anim_in=tanim("fade", duration=0.3), name=f"Cargo {i + 1}")
    song(t, "upbeat", 2, 0.6)
    return t


def presenta_evento():
    t = wide("h-presenta-evento", "Resumen del evento", "Event recap", "slideshow", 10.0, order=2231,
             tags=["evento", "resumen", "aftermovie", "conferencia", "fiesta"], thumb_at=8.6, background="#000000")
    samples = ["h-concert-04", "h-community-01", "h-concert-02", "h-office-01", "h-concert-03", "h-community-02",
               "h-concert-01", "h-office-06", "h-community-04", "h-concert-04", "h-office-03", "h-concert-02",
               "h-community-01", "h-office-05", "h-concert-03", "h-community-02"]
    slides(t, samples, 0.0, 0.5, transition=None, kb_amount=0.12)
    t.solid(t.track("shape", "Cierre"), "#000000", 8.0, 2.0, opacity=keys([(0, 0.0), (0.3, 0.85)]))
    t.photo(t.track("video", "Logo"), "logo-08", 8.2, 1.8, centered(960, 420, 360, 360), pop(0, 0.5), label="Logo del evento")
    label(t, t.track("text", "Evento"), "CUMBRE CREATIVA 2026", 8.4, 1.6, Box(160, 640, 1600, 140), "Montserrat", 84,
          "#FFFFFF", weight=900, spacing=8, anim_in=tanim("rise", duration=0.4, unit="character", stagger=0.02),
          name="Evento")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.5 * k for k in range(1, 16)], 0.35, 0.2)})], name="Pulso")
    flash(t, 8.0, 0.3)
    song(t, "electro", 1, 0.85)
    return t


def presenta_vintage():
    t = wide("h-presenta-vintage", "Álbum antiguo", "Vintage album", "slideshow", 15.0, order=2232,
             tags=["vintage", "antiguo", "sepia", "álbum", "recuerdos", "abuelos"], thumb_at=4.0, background="#2B2118")
    bg_gradient(t, [(0, "#3B2C20"), (1, "#22180F")], angle=90)
    rrect(t, t.track("shape", "Página"), "#EFE3C8", 0, 15.0, centered(960, 540, 1700, 960), 10,
          layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#EFE3C8"), no_stroke()])
    samples = ["h-elderly-03", "h-family-01", "h-elderly-02", "h-father-02", "h-mother-04"]
    caps = ["los abuelos, 1978", "domingo en el campo", "la boda de la tía", "papá y yo", "mamá"]
    for i, (s, cap) in enumerate(zip(samples, caps)):
        at = i * 3.0
        box = Box(420, 160, 1080, 640)
        t.photo(t.track("video", f"Foto {i + 1}"), s, at, 3.0, box, [(0, {"s": 1.04}, "linear"), (3.0, {"s": 1.0})],
                label=f"Foto {i + 1}", effects=[effect("stylize.sepia"), effect("color.basic", fade=0.2, contrast=-0.1)],
                opacity=keys([(0, 0.0), (0.5, 1.0)]))
        for cx, cy, rot in ((box.x, box.y, 45), (box.x + box.w, box.y, 135), (box.x, box.y + box.h, -45),
                            (box.x + box.w, box.y + box.h, -135)):
            t.solid(t.track("shape", "Esquina"), "#3B2C20", at, 3.0, centered(cx, cy, 90, 90), kind="triangle",
                    rotation=keys([(0, rot - 90)]), opacity=keys([(0, 0.0), (0.5, 1.0)]))
        label(t, t.track("text", "Pie"), cap, at + 0.6, 2.4, Box(420, 830, 1080, 110), "Dancing Script", 72, "#3B2C20",
              weight=700, anim_in=tanim("fade", duration=0.6), anim_out=tanim("fade", duration=0.4), name=f"Pie {i + 1}")
    grain(t, 0.3, 2.0)
    vignette(t, 0.7)
    song(t, "classic", 0, 0.75)
    return t


def presenta_revista():
    t = wide("h-presenta-revista", "Revista", "Magazine pages", "slideshow", 12.0, order=2233,
             tags=["revista", "editorial", "moda", "páginas", "presentación"], thumb_at=4.0, background="#FFFFFF")
    pages = [("h-portrait-06", "VERANO", "#E63946"), ("h-portrait-04", "CIUDAD", "#1D3557"),
             ("h-portrait-01", "LUZ", "#F4A261"), ("h-portrait-03", "NOCHE", "#6D597A")]
    v = t.track("video", "Páginas")
    prev = None
    for i, (s, word, c) in enumerate(pages):
        at = i * 3.0
        d = 3.0 + (0.5 if i < len(pages) - 1 else 0)
        clip = t.photo(v, s, at, d, Box(0, 0, 1100, 1080), kb(d, 1.0, 1.05), label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, "push_left", 0.5)
        prev = clip
        t.solid(t.track("shape", "Página"), "#FFFFFF", at, 3.0, Box(1100, 0, 820, 1080), opacity=keys([(0, 1.0)]))
        label(t, t.track("text", "Palabra"), word, at + 0.3, 2.6, Box(1150, 140, 720, 260), "Bodoni Moda", 170, c, weight=700,
              align="left", anim_in=tanim("slide-up", duration=0.4), anim_out=tanim("fade", duration=0.3),
              name=f"Título {i + 1}")
        label(t, t.track("text", "Texto"), "Ideas, lugares y personas que inspiran esta temporada.", at + 0.5, 2.4,
              Box(1150, 440, 640, 260), "Lora", 48, "#333333", weight=400, align="left", line=1.3,
              anim_in=tanim("fade", duration=0.5), anim_out=tanim("fade", duration=0.3), name=f"Texto {i + 1}")
        label(t, t.track("text", "Página"), f"— {12 + i * 2}", at + 0.5, 2.4, Box(1150, 960, 640, 60), "Lora", 30, "#999999",
              weight=400, align="left", editable=False)
    song(t, "jazz", 3, 0.65)
    return t


def presenta_collage_libre():
    t = wide("h-presenta-collage-libre", "Collage libre", "Free collage", "slideshow", 12.0, order=2234,
             tags=["collage", "fotos", "tablero", "amigos", "recuerdos"], thumb_at=10.5, background="#F7E1D7")
    bg_gradient(t, [(0, "#F7E1D7"), (1, "#EDAFB8")], angle=135)
    rng = random.Random(234)
    samples = ["h-summer-02", "h-birthday-03", "h-couple-05", "h-beach-02", "h-concert-04", "h-kids-02", "h-pet-01",
               "h-travel-04", "h-family-03", "h-summer-03"]
    for i, s in enumerate(samples):
        at = 0.2 + i * 1.0
        w = rng.uniform(420, 560)
        h = w * rng.choice([0.75, 1.0, 1.25])
        x, y = rng.uniform(260, 1660), rng.uniform(220, 860)
        r = rng.uniform(-14, 14)
        framed(t, s, at, 12.0 - at, centered(x, y, w, h), [(0, {"s": 1.4}, "out"), (0.4, {})], border=12,
               colour="#FFFFFF", rotation=keys([(0, r * 1.8, "out"), (0.4, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Título"), "best moments ✦", 10.2, 1.8, Box(160, 420, 1600, 220), "Permanent Marker", 150,
          "#FFFFFF", weight=400, layers=[shadow("#B23A48", 6, 6, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          rotation=keys([(0, -4)]), name="Título")
    song(t, "upbeat", 4, 0.8)
    return t


def presenta_split():
    t = wide("h-presenta-split", "Pantalla dividida", "Split screen slideshow", "slideshow", 12.0, order=2235,
             tags=["pantalla dividida", "split", "dos fotos", "comparación", "presentación"], thumb_at=4.0,
             background="#000000")
    pairs = [("h-city-01", "h-nature-03"), ("h-couple-04", "h-beach-04"), ("h-food-04", "h-cafe-01"),
             ("h-sport-03", "h-fitness-01")]
    for i, (a, b) in enumerate(pairs):
        at = i * 3.0
        t.photo(t.track("video", "Izquierda"), a, at, 3.0, Box(0, 0, 955, 1080),
                [(0, {"dy": -1080}, "out"), (0.5, {}, "linear"), (3.0, {"s": 1.04})], label=f"Izquierda {i + 1}")
        t.photo(t.track("video", "Derecha"), b, at + 0.1, 2.9, Box(965, 0, 955, 1080),
                [(0, {"dy": 1080}, "out"), (0.5, {}, "linear"), (2.9, {"s": 1.04})], label=f"Derecha {i + 1}")
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, 12.0, Box(955, 0, 10, 1080))
    label(t, t.track("text", "Título"), "AQUÍ  |  ALLÁ", 0.4, 11.2, Box(160, 900, 1600, 140), "Bebas Neue", 110, "#FFFFFF",
          weight=400, spacing=20, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.5), name="Título")
    song(t, "cine", 3, 0.75)
    return t


def presenta_circulos():
    t = wide("h-presenta-circulos", "Fotos en círculos", "Photos in circles", "slideshow", 10.0, order=2236,
             tags=["círculos", "fotos", "colores", "alegre", "presentación"], thumb_at=6.0, background="#FFB703")
    bg(t, "#FFB703")
    spots = [(420, 360, 460, "#FB8500"), (1000, 640, 520, "#219EBC"), (1520, 330, 420, "#023047"),
             (1560, 820, 300, "#8ECAE6"), (360, 860, 300, "#FFFFFF")]
    samples = ["h-kids-01", "h-summer-01", "h-pet-03", "h-birthday-04", "h-family-05"]
    for i, ((x, y, s, c), smp) in enumerate(zip(spots, samples)):
        at = 0.3 + i * 0.5
        circle_photo(t, smp, at, 10.0 - at, centered(x, y, s, s),
                     [(0, {"s": 0.0}, "back"), (0.5, {}, "smooth"), (4.0, {"dy": -20}, "smooth"), (7.0, {"dy": 15}, "smooth"),
                      (10.0 - at, {})], ring_colour=c, ring_width=14, label=f"Foto {i + 1}")
    label(t, t.track("text", "Título"), "¡Qué buen día!", 3.0, 7.0, Box(560, 60, 800, 140), "Fredoka", 100, "#023047",
          weight=700, anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    song(t, "fun", 3, 0.75)
    return t


def presenta_cinematica():
    t = wide("h-presenta-cinematica", "Presentación cinemática", "Cinematic slideshow", "slideshow", 16.0, order=2237,
             tags=["cinemático", "película", "barras", "viaje", "épico", "presentación"], thumb_at=5.4, background="#000000")
    samples = ["h-nature-05", "h-travel-02", "h-city-02", "h-nature-04", "h-beach-01"]
    slides(t, samples, 0.0, 3.2, transition="blur_dissolve", tdur=1.0, kb_amount=0.1,
           effects_fn=lambda i: [effect("cinematic_grade", strength=0.75, teal=0.7, orange=0.6)])
    letterbox(t)
    for i, (txt, at) in enumerate([("CAPÍTULO I", 0.6), ("EL CAMINO", 4.0), ("LA CIUDAD", 7.2), ("EL REGRESO", 10.4)]):
        label(t, t.track("text", "Rótulo"), txt, at, 2.4, Box(160, 470, 1600, 140), "Cinzel", 96, "#F4EDE4", weight=500,
              spacing=30, anim_in=tanim("blur-in", duration=0.9, blur=16), anim_out=tanim("fade", duration=0.5),
              name=f"Rótulo {i + 1}")
    t.adjust([effect("light_leak", intensity=0.3, hue=0.07, speed=0.5), effect("stylize.film_grain", amount=0.2)],
             name="Película")
    song(t, "epic", 4, 0.8)
    return t


def presenta_mascota():
    t = wide("h-presenta-mascota", "Mi mascota", "My pet", "slideshow", 12.0, order=2238,
             tags=["mascota", "perro", "gato", "huellas", "fotos", "tierno"], thumb_at=4.0, background="#FFF3E2")
    bg(t, "#FFF3E2")
    rng = random.Random(238)
    for k in range(10):  # paw prints walking across
        x, y = 150 + k * 180, 980 - (k % 2) * 60
        at = 0.2 + k * 0.2
        paw = t.track("shape", "Huella")
        t.solid(paw, "#F4A261", at, 12.0 - at, centered(x, y, 60, 52), pop(0, 0.3), kind="ellipse", alpha=0.6)
        for dx, dy in ((-30, -40), (-10, -55), (12, -55), (32, -40)):
            t.solid(paw, "#F4A261", at, 12.0 - at, centered(x + dx, y + dy, 22, 26), pop(0, 0.3), kind="ellipse",
                    alpha=0.6)
    samples = ["h-pet-04", "h-pet-01", "h-pet-02", "h-pet-03"]
    for i, s in enumerate(samples):
        at = i * 3.0
        framed(t, s, at, 3.0, Box(460, 90, 1000, 700), [(0, {"s": 0.85, "dy": 40}, "back"), (0.5, {}, "linear"),
                                                         (3.0, {"s": 1.02})], border=16, radius=30, colour="#FFFFFF",
               label=f"Foto {i + 1}", rotation=keys([(0, (-1) ** i * 2)]))
    label(t, t.track("text", "Nombre"), "Toby, mi mejor amigo", 0.4, 11.4, Box(160, 820, 1600, 120), "Chewy", 96,
          "#E76F51", weight=400, anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Nombre")
    song(t, "fun", 1, 0.75)
    return t


def presenta_amistad():
    t = wide("h-presenta-amistad", "Amigos para siempre", "Friends forever", "slideshow", 12.0, order=2239,
             tags=["amigos", "amistad", "garabatos", "fotos", "diversión"], thumb_at=4.2, background="#000000")
    samples = ["h-summer-03", "h-birthday-02", "h-concert-04", "h-beach-02"]
    slides(t, samples, 0.0, 3.0, transition="slide_left", tdur=0.4, kb_amount=0.08)
    doodles = [("✦", 260, 200, "#FFE600"), ("♥", 1660, 240, "#FF4D6D"), ("☺", 1600, 820, "#FFFFFF"), ("★", 330, 860, "#3EC1FF"),
               ("✿", 980, 140, "#FF9ECF")]
    for i, (g, x, y, c) in enumerate(doodles):
        label(t, t.track("text", "Garabato"), g, 0.3 + i * 0.2, 11.5 - i * 0.2, centered(x, y, 220, 220), "Inter", 150, c,
              weight=400, editable=False, layers=[stroke(4, "#000000"), fill(c)], motion=pop(0, 0.4),
              anim_loop=tanim("swing", angle=8, speed=0.8))
    label(t, t.track("text", "Título"), "amigos para siempre", 0.5, 11.3, Box(160, 420, 1600, 240), "Permanent Marker", 130,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("wipe", duration=0.8, angle=0), rotation=keys([(0, -3)]), name="Título")
    song(t, "upbeat", 5, 0.8)
    return t


def presenta_homenaje():
    t = wide("h-presenta-homenaje", "En memoria", "In loving memory", "slideshow", 18.0, order=2240,
             tags=["homenaje", "en memoria", "despedida", "recuerdo", "velas"], thumb_at=2.4, background="#0B0B0D")
    bg(t, "#0B0B0D")
    photo_bg(t, "h-memorial-01", 0, 4.0, s1=1.06, label="Foto de velas",
             effects=[effect("color.basic", exposure=-0.3, saturation=-0.3)])
    label(t, t.track("text", "Nombre"), "Carmen Ruiz", 0.6, 3.2, Box(160, 360, 1600, 200), "Cormorant Garamond", 150,
          "#F2EDE4", weight=500, anim_in=tanim("blur-in", duration=1.2, blur=20), anim_out=tanim("fade", duration=0.8),
          name="Nombre")
    label(t, t.track("text", "Fechas"), "1941 — 2026", 1.2, 2.6, Box(560, 580, 800, 80), "Cormorant Garamond", 60,
          "#C9BFAE", weight=400, spacing=8, anim_in=tanim("fade", duration=1.0), anim_out=tanim("fade", duration=0.8),
          name="Fechas")
    samples = ["h-elderly-03", "h-elderly-02", "h-family-06", "h-mother-04"]
    v = t.track("video", "Fotos")
    prev = None
    for i, s in enumerate(samples):
        at = 4.0 + i * 3.0
        d = 3.0 + (1.0 if i < len(samples) - 1 else 0)
        clip = t.photo(v, s, at, d, Box(360, 140, 1200, 800), kb(d, 1.0, 1.05), label=f"Foto {i + 1}",
                       effects=[effect("color.basic", saturation=-0.4, fade=0.1)])
        if prev:
            t.transition(v, prev, clip, "crossfade", 1.0)
        prev = clip
    label(t, t.track("text", "Frase"), "Siempre en nuestro corazón", 16.0, 2.0, Box(160, 420, 1600, 200),
          "Cormorant Garamond", 110, "#F2EDE4", weight=500, italic=True, anim_in=tanim("fade", duration=1.0), name="Frase")
    t.solid(t.track("shape", "Fundido"), "#0B0B0D", 15.6, 2.4, opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0)]))
    vignette(t, 0.6)
    song(t, "classic", 2, 0.65)
    return t


def presenta_antes_despues():
    t = wide("h-presenta-antes-despues", "Antes y después", "Before and after", "slideshow", 8.0, order=2241,
             tags=["antes y después", "comparación", "deslizador", "transformación", "remodelación"], thumb_at=3.2,
             background="#000000")
    t.photo(t.track("video", "Después"), "h-interior-04", 0, 8.0, t.full, kb(8.0, 1.0, 1.04), label="Foto de después")
    host = t.track("video", "Antes")
    clip = t.photo(host, "h-interior-02", 0, 8.0, t.full, kb(8.0, 1.0, 1.04), label="Foto de antes",
                   effects=[effect("color.basic", saturation=-0.5, exposure=-0.15)])
    t.mask(host, clip, "rectangle", x=0.5, y=0.5, w=1.0, h=1.0,
           keyframes={"w": keys([(0, 2.0, "hold"), (1.0, 2.0, "inout"), (3.0, 1.0, "inout"), (5.0, 0.4, "inout"), (7.0, 1.0)]),
                      "x": keys([(0, 1.0, "hold"), (1.0, 1.0, "inout"), (3.0, 0.5, "inout"), (5.0, 0.2, "inout"), (7.0, 0.5)])})
    bar = t.track("shape", "Divisor")
    xs = [(0, 1920, "hold"), (1.0, 1920, "inout"), (3.0, 960, "inout"), (5.0, 384, "inout"), (7.0, 960)]
    t.solid(bar, "#FFFFFF", 0, 8.0, Box(955, 0, 10, 1080),
            [(p[0], {"dx": p[1] - 960}) + tuple(p[2:]) for p in xs])
    t.solid(t.track("shape", "Asa"), "#FFFFFF", 0, 8.0, centered(960, 540, 90, 90),
            [(p[0], {"dx": p[1] - 960}) + tuple(p[2:]) for p in xs], kind="ellipse",
            layers=[shadow("#000000", 0, 4, 12, 0.4), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "Flechas"), "◀ ▶", 0, 8.0, centered(960, 540, 90, 90), "Inter", 28, "#111111", weight=700,
          editable=False, motion=[(p[0], {"dx": p[1] - 960}) + tuple(p[2:]) for p in xs])
    for i, (txt, x) in enumerate([("ANTES", 160), ("DESPUÉS", 1560)]):
        pill(t, t.track("shape", "Etiqueta"), "#111111" if i == 0 else "#00C2A8", 0.5, 7.5, Box(x, 70, 260, 70), pop(0, 0.4))
        label(t, t.track("text", "Etiqueta"), txt, 0.5, 7.5, Box(x, 70, 260, 70), "Montserrat", 36, "#FFFFFF", weight=800,
              spacing=4, name=f"Etiqueta {i + 1}")
    song(t, "upbeat", 7, 0.7)
    return t


def presenta_deportes():
    t = wide("h-presenta-deportes", "Temporada deportiva", "Sports season", "slideshow", 13.0, order=2242,
             tags=["deportes", "temporada", "resultados", "equipo", "fútbol"], thumb_at=4.2, background="#0B0B0B")
    games = [("h-soccer-02", "3 – 1", "vs. Halcones"), ("h-soccer-03", "2 – 2", "vs. Toros"),
             ("h-sport-05", "4 – 0", "vs. Pumas"), ("h-soccer-01", "1 – 0", "FINAL")]
    for i, (s, score, rival) in enumerate(games):
        at = i * 3.0
        d = 3.0 if i < 3 else 4.0
        t.photo(t.track("video", f"Partido {i + 1}"), s, at, d, t.full, kb(d, 1.1, 1.0), label=f"Foto {i + 1}",
                effects=[effect("color.basic", contrast=0.25, saturation=-0.2)])
        t.solid(t.track("shape", "Placa"), "#E10600", at + 0.3, d - 0.3, Box(100, 720, 640, 240),
                [(0, {"dx": -800}, "out"), (0.35, {})], kind="parallelogram")
        label(t, t.track("text", "Marcador"), score, at + 0.4, d - 0.4, Box(140, 720, 560, 160), "Anton", 140, "#FFFFFF",
              weight=400, anim_in=tanim("pop", duration=0.3), name=f"Marcador {i + 1}")
        label(t, t.track("text", "Rival"), rival, at + 0.5, d - 0.5, Box(140, 870, 560, 80), "Barlow Condensed", 54,
              "#FFFFFF", weight=700, spacing=6, anim_in=tanim("fade", duration=0.3), name=f"Rival {i + 1}")
    label(t, t.track("text", "Temporada"), "TEMPORADA 2026", 0.2, 12.8, Box(1200, 80, 640, 80), "Anton", 64, "#FFFFFF",
          weight=400, spacing=4, align="right", layers=[shadow("#000000", 0, 4, 12, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Temporada")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([3.0, 6.0, 9.0], 0.5, 0.3)})], name="Golpe")
    song(t, "epic", 1, 0.8)
    return t


def presenta_comida():
    t = wide("h-presenta-comida", "Menú en fotos", "Menu slideshow", "slideshow", 13.0, order=2243,
             tags=["menú", "comida", "restaurante", "platos", "carta"], thumb_at=4.2, background="#1C1410")
    dishes = [("h-food-01", "Desayuno completo", "$12"), ("h-food-03", "Mezze para compartir", "$18"),
              ("h-food-04", "Hamburguesa de la casa", "$15"), ("h-food-06", "Bowl del día", "$11")]
    for i, (s, name, price) in enumerate(dishes):
        at = i * 3.2
        t.photo(t.track("video", f"Plato {i + 1}"), s, at, 3.2, t.full, kb(3.2, 1.0, 1.08), label=f"Plato {i + 1}")
        shade_bottom(t, 460, 0.85, at, 3.2, colour="#1C1410")
        label(t, t.track("text", "Plato"), name, at + 0.3, 2.9, Box(120, 760, 1300, 120), "DM Serif Display", 96, "#FFFFFF",
              weight=400, align="left", anim_in=tanim("slide-up", duration=0.4), name=f"Plato {i + 1}")
        label(t, t.track("text", "Precio"), price, at + 0.5, 2.7, Box(1500, 760, 300, 120), "Montserrat", 90, "#F4A261",
              weight=800, align="right", anim_in=tanim("pop", duration=0.3), name=f"Precio {i + 1}")
    label(t, t.track("text", "Restaurante"), "LA HUERTA · MENÚ", 0.2, 12.8, Box(120, 80, 1000, 60), "Montserrat", 38,
          "#FFFFFF", weight=700, spacing=10, align="left", layers=[shadow("#000000", 0, 3, 10, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Restaurante")
    song(t, "jazz", 2, 0.7)
    return t


def presenta_escuela():
    t = wide("h-presenta-escuela", "Año escolar", "School year", "slideshow", 13.0, order=2244,
             tags=["escuela", "colegio", "año escolar", "cuaderno", "clases", "niños"], thumb_at=4.4, background="#FFFFFF")
    bg(t, "#FFFFFF")
    for k in range(14):
        t.solid(t.track("shape", "Renglón"), "#BFD7EA", 0, 13.0, Box(0, 60 + k * 74, 1920, 3))
    t.solid(t.track("shape", "Margen"), "#F28482", 0, 13.0, Box(200, 0, 4, 1080))
    samples = ["h-classroom-01", "h-kids-04", "h-classroom-02", "h-school-01"]
    caps = ["primer día", "el recreo", "la feria de ciencias", "¡vacaciones!"]
    for i, (s, cap) in enumerate(zip(samples, caps)):
        at = i * 3.2
        r = (-1) ** i * 3
        framed(t, s, at, 3.2, Box(420, 150, 960, 620), [(0, {"s": 1.3}, "out"), (0.45, {})], border=14, colour="#FFFFFF",
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
        for side in (-1, 1):
            t.solid(t.track("shape", "Cinta"), "#FFE066", at + 0.3, 2.9, centered(900 + side * 430, 150, 170, 46), pop(0, 0.3),
                    alpha=0.85, rotation=keys([(0, side * 30 + r)]))
        label(t, t.track("text", "Pie"), cap, at + 0.5, 2.7, Box(420, 820, 960, 140), "Gloria Hallelujah", 80, "#3D405B",
              weight=400, anim_in=tanim("typewriter", duration=0.6, unit="character"), name=f"Pie {i + 1}")
    label(t, t.track("text", "Curso"), "3.º B · 2026", 0.2, 12.8, Box(1520, 70, 360, 80), "Gloria Hallelujah", 56, "#F28482",
          weight=400, rotation=keys([(0, 4)]), anim_in=tanim("fade", duration=0.4), name="Curso")
    song(t, "fun", 4, 0.7)
    return t


# --- Celebrations -------------------------------------------------------------------------------

def _balloons(t, colours, t0, dur, seed, n=7):
    rng = random.Random(seed)
    for k in range(n):
        x = rng.uniform(80, 1840)
        s = rng.uniform(120, 190)
        c = rng.choice(colours)
        at = t0 + rng.uniform(0, 1.5)
        d = t0 + dur - at
        rise = [(0, {"dy": 700}, "out"), (2.0, {}, "smooth"), (d, {"dy": -60, "dx": rng.uniform(-40, 40)})]
        t.solid(t.track("shape", "Cordel"), "#FFFFFF", at, d, Box(x - 1, 300 + s * 0.6, 3, 380), rise, alpha=0.7)
        t.solid(t.track("shape", "Globo"), c, at, d, centered(x, 300, s, s * 1.2), rise, kind="ellipse",
                layers=[gradient([(0, "#FFFFFF", 0.55), (0.35, c), (1, c)], angle=135), no_stroke()])


def cele_cumple():
    t = wide("h-cele-cumple", "Feliz cumpleaños", "Happy birthday", "celebration", 10.0, order=2245,
             tags=["cumpleaños", "fiesta", "globos", "confeti", "felicitación"], thumb_at=4.0, background="#FF6FB5")
    bg_gradient(t, [(0, "#FF6FB5"), (0.6, "#FF9A8B"), (1, "#FFD23F")], angle=120)
    _balloons(t, ["#3BCEAC", "#FFFFFF", "#7B2FF7", "#FFD23F", "#FF5A5F"], 0.0, 10.0, 245)
    framed(t, "h-birthday-01", 0.6, 9.4, Box(1060, 220, 700, 560), [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"),
                                                                   (9.4, {"s": 1.03})], border=18, radius=30,
           colour="#FFFFFF", rotation=keys([(0, 4)]), label="Foto del cumpleañero")
    label(t, t.track("text", "Felicidades"), "¡Feliz\ncumpleaños!", 0.9, 9.1, Box(120, 200, 900, 460), "Pacifico", 150,
          "#FFFFFF", weight=400, line=1.0, layers=[shadow("#B5179E", 0, 8, 0, 0.8), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.5, unit="word", stagger=0.2, ease="back"), name="Felicidades")
    label(t, t.track("text", "Nombre"), "Sofía · 8 años", 1.6, 8.4, Box(120, 700, 900, 120), "Fredoka", 84, "#FFFFFF",
          weight=700, anim_in=tanim("rise", duration=0.4), name="Nombre")
    confetti(t, ["#FFFFFF", "#3BCEAC", "#FFD23F", "#7B2FF7"], 0.5, 9.5, seed=246, lanes=4, density=0.35)
    song(t, "fun", 0, 0.8)
    return t


def cele_aniversario():
    t = wide("h-cele-aniversario", "Feliz aniversario", "Happy anniversary", "celebration", 10.0, order=2246,
             tags=["aniversario", "pareja", "amor", "años juntos", "corazones"], thumb_at=4.5, background="#2B0A1A")
    bg_gradient(t, [(0, "#4A0E2B"), (1, "#1C0611")], angle=90)
    dots(t, ["#FF6B8B", "#FFB3C1", "#FFFFFF"], 26, 0, 10.0, seed=246, size=(24, 60), kinds=("heart",), drift=160,
         alpha=0.7)
    for i, (s, x, r) in enumerate([("h-couple-02", 600, -5), ("h-couple-05", 1320, 5)]):
        framed(t, s, 0.4 + i * 0.4, 9.6 - i * 0.4, centered(x, 470, 560, 560), [(0, {"s": 1.4}, "out"), (0.5, {})],
               border=16, colour="#FFFFFF", rotation=keys([(0, r * 2, "out"), (0.5, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Años"), "10 años juntos", 1.4, 8.6, Box(160, 820, 1600, 160), "Great Vibes", 140, "#FFFFFF",
          weight=400, layers=[glow("#FF6B8B", 18, 0.7), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=1.0),
          name="Años juntos")
    label(t, t.track("text", "Corazón"), "♥", 1.0, 9.0, centered(960, 470, 200, 200), "Inter", 150, "#FF4D6D", weight=400,
          editable=False, motion=pop(0, 0.4), anim_loop=tanim("pulse", amount=10, speed=1.1))
    song(t, "romantic", 3, 0.75)
    return t


def cele_jubilacion():
    t = wide("h-cele-jubilacion", "Feliz jubilación", "Happy retirement", "celebration", 12.0, order=2247,
             tags=["jubilación", "retiro", "carrera", "gracias", "homenaje"], thumb_at=9.8, background="#123C3A")
    samples = ["h-office-03", "h-man-02", "h-office-05", "h-elderly-01"]
    slides(t, samples, 0.0, 2.2, transition="crossfade", tdur=0.6, kb_amount=0.08)
    t.solid(t.track("shape", "Cierre"), "#123C3A", 8.8, 3.2, opacity=keys([(0, 0.0, "smooth"), (0.6, 0.92)]))
    label(t, t.track("text", "Felicidades"), "¡Feliz jubilación!", 9.0, 3.0, Box(160, 300, 1600, 220), "DM Serif Display",
          150, "#F2C14E", weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.2),
          name="Felicidades")
    label(t, t.track("text", "Gracias"), "Gracias por 30 años de trabajo y cariño, Roberto", 9.6, 2.4, Box(260, 560, 1400, 160),
          "Montserrat", 54, "#FFFFFF", weight=500, line=1.2, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    for i, (txt, at) in enumerate([("1996", 0.3), ("2008", 2.5), ("2019", 4.7), ("2026", 6.9)]):
        label(t, t.track("text", "Año"), txt, at, 1.9, Box(120, 860, 600, 160), "DM Serif Display", 120, "#FFFFFF",
              weight=400, align="left", layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
              anim_in=tanim("slide-up", duration=0.3), anim_out=tanim("fade", duration=0.3), name=f"Año {i + 1}")
    confetti(t, ["#F2C14E", "#FFFFFF", "#7FD1B9"], 9.0, 3.0, seed=247, lanes=3, density=0.25)
    song(t, "upbeat", 2, 0.75)
    return t


def cele_compromiso():
    t = wide("h-cele-compromiso", "Nos comprometimos", "We're engaged", "celebration", 9.0, order=2248,
             tags=["compromiso", "propuesta", "anillo", "pareja", "boda"], thumb_at=4.2)
    photo_bg(t, "h-couple-03", s1=1.08, label="Foto de la pareja")
    shade_full(t, 0.35)
    label(t, t.track("text", "Anillo"), "💍", 0.4, 8.6, centered(960, 270, 260, 260), "Inter", 180, "#FFFFFF", weight=400,
          editable=False, motion=pop(0, 0.5), anim_loop=tanim("float", amount=0.08, speed=0.6))
    label(t, t.track("text", "Título"), "¡Dijo que sí!", 1.0, 8.0, Box(160, 420, 1600, 240), "Great Vibes", 200, "#FFFFFF",
          weight=400, layers=[glow("#F2D59B", 20, 0.6), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    label(t, t.track("text", "Fecha"), "LAURA & PABLO · 03.10.2026", 1.8, 7.2, Box(260, 700, 1400, 80), "Cinzel", 50,
          "#F2E6CF", weight=500, spacing=8, anim_in=tanim("fade", duration=0.6), name="Nombres y fecha")
    t.adjust([effect("bling_sparkle", intensity=0.6, threshold=0.75, density=0.35)], name="Destellos")
    song(t, "romantic", 4, 0.75)
    return t


def cele_bautizo():
    t = wide("h-cele-bautizo", "Bautizo", "Christening", "celebration", 9.0, order=2249,
             tags=["bautizo", "bebé", "iglesia", "familia", "celebración"], thumb_at=4.4, background="#EAF4FB")
    bg_gradient(t, [(0, "#F6FBFF"), (1, "#D9ECF9")], angle=90)
    circle_photo(t, "h-baby-02", 0.3, 8.7, centered(560, 540, 640, 640), pop(0, 0.6, 0.6), ring_colour="#FFFFFF",
                 ring_width=18, label="Foto del bebé")
    label(t, t.track("text", "Paloma"), "🕊", 1.0, 8.0, centered(1350, 230, 220, 220), "Inter", 150, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"dx": 300, "dy": -100}, "out"), (1.2, {})],
          anim_loop=tanim("float", amount=0.1, speed=0.5))
    label(t, t.track("text", "Título"), "Mi bautizo", 1.2, 7.8, Box(1000, 380, 860, 200), "Dancing Script", 140, "#3A6EA5",
          weight=700, anim_in=tanim("fade", duration=0.8), name="Título")
    label(t, t.track("text", "Nombre"), "Mateo", 1.6, 7.4, Box(1000, 580, 860, 140), "Playfair Display", 100, "#1F3B5C",
          weight=600, anim_in=tanim("fade", duration=0.8), name="Nombre")
    label(t, t.track("text", "Fecha"), "domingo 8 de noviembre · 11:00", 2.0, 7.0, Box(1000, 740, 860, 70), "Montserrat",
          38, "#5C7FA3", weight=500, anim_in=tanim("fade", duration=0.8), name="Fecha")
    dots(t, ["#FFFFFF", "#BFDDF5"], 18, 0, 9.0, seed=249, size=(12, 30), kinds=("ellipse", "star"), drift=70)
    song(t, "classic", 0, 0.7)
    return t


TEMPLATES = [final_2_videos, final_1_video, final_oscura, final_colorida, final_gaming, final_minimal, final_podcast,
             final_cocina, final_viajes, final_negocio, final_curso, final_familia, final_papel, final_retro,
             final_noticias,
             presenta_recuerdos, presenta_polaroid, presenta_tinta, presenta_glitch, presenta_pelicula,
             presenta_mosaico, presenta_paralaje, presenta_viaje, presenta_boda, presenta_bebe, presenta_anio,
             presenta_graduacion, presenta_inmueble, presenta_portafolio, presenta_producto, presenta_equipo,
             presenta_evento, presenta_vintage, presenta_revista, presenta_collage_libre, presenta_split,
             presenta_circulos, presenta_cinematica, presenta_mascota, presenta_amistad, presenta_homenaje,
             presenta_antes_despues, presenta_deportes, presenta_comida, presenta_escuela,
             cele_cumple, cele_aniversario, cele_jubilacion, cele_compromiso, cele_bautizo]
