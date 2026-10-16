"""Horizontal batch 1 (2026-10-16): intros, transitions and countdowns for YouTube / Facebook, 1920x1080.
See BRIEF.md, «Las 400 nuevas». Categories intro, transition, countdown; order 2000-2099.
"""

from __future__ import annotations

from kit import *  # noqa: F401,F403
from kit import (Box, appear, bg, bg_gradient, blink, centered, confetti, dots, effect, fill, flash, framed,
                 gradient, grain, glow, keys, kb, label, letterbox, line, no_stroke, outline, panels, photo_bg, pill,
                 pop, random, ring, rrect, shade_bottom, shade_full, shadow, slide_in, slides, song, spike, stroke,
                 tanim, vignette, wide, circle_photo)


# 1 -----------------------------------------------------------------------------------------------

def intro_barras_diagonales():
    t = wide("h-intro-barras-diagonales", "Intro de barras diagonales", "Diagonal bars intro", "intro", 6.0,
             order=2000, tags=["intro", "youtube", "canal", "logo", "barras", "dinámica"], thumb_at=3.2)
    photo_bg(t, "h-portrait-01", s1=1.12, label="Tu foto o video")
    shade_full(t, 0.35)
    colours = ["#FFC93C", "#FF6B35", "#1B1B1B"]
    for i, c in enumerate(colours):
        tr = t.track("shape", "Barra")
        y = 120 + i * 300
        t.solid(tr, c, 0.15 + i * 0.12, 5.6 - i * 0.12, Box(-400, y, 2800, 220),
                [(0, {"dx": -2900}, "out"), (0.7, {}, "linear"), (5.0, {"dx": 120})],
                rotation=keys([(0, -12)]), alpha=0.92 if i < 2 else 0.85)
    logo = t.track("shape", "Logo")
    t.solid(logo, "#FFFFFF", 1.0, 5.0, centered(960, 430, 240, 240), pop(0, 0.55), kind="ellipse",
            layers=[shadow("#000000", 0, 14, 30, 0.4), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "Inicial"), "F", 1.05, 4.95, centered(960, 430, 240, 240), "Poppins", 150, "#1B1B1B",
          weight=900, motion=pop(0, 0.55), name="Inicial del logo")
    label(t, t.track("text", "Canal"), "TU CANAL", 1.5, 4.5, Box(260, 600, 1400, 200), "Poppins", 150, "#FFFFFF",
          weight=900, spacing=6, layers=[shadow("#000000", 0, 8, 20, 0.5), fill("#FFFFFF")],
          anim_in=tanim("slide-up", duration=0.5, unit="character", stagger=0.04, ease="back"), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 2.1, 3.9, Box(460, 800, 1000, 80), "Inter", 46,
          "#FFC93C", weight=600, spacing=3, anim_in=tanim("fade", duration=0.5), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0], 0.5, 0.35)})], name="Golpe")
    song(t, "upbeat", 0)
    return t


# 2 -----------------------------------------------------------------------------------------------

def intro_logo_destello():
    t = wide("h-intro-logo-destello", "Logo con destello", "Logo flare reveal", "intro", 5.0, order=2001,
             tags=["logo", "revelación", "destello", "intro", "elegante", "marca"], thumb_at=2.6, background="#05070D")
    bg_gradient(t, [(0, "#0B1430"), (0.6, "#05070D"), (1, "#000000")], angle=90)
    dots(t, ["#5AA9FF", "#FFFFFF", "#9BD1FF"], 26, 0.0, 5.0, seed=11, size=(4, 12), drift=40)
    halo = t.track("shape", "Halo")
    t.solid(halo, "#5AA9FF", 1.2, 3.8, centered(960, 480, 900, 900),
            [(0, {"s": 0.2}, "out"), (1.2, {"s": 1.0})], kind="ellipse",
            layers=[gradient([(0, "#5AA9FF", 0.45), (1, "#5AA9FF", 0.0)], angle=0), no_stroke()],
            opacity=keys([(0, 0.0), (0.6, 1.0, "smooth"), (3.8, 0.6)]))
    t.photo(t.track("video", "Logo"), "logo-07", 1.0, 4.0, centered(960, 440, 380, 380),
            [(0, {"s": 0.6}, "out"), (1.2, {"s": 1.0}, "linear"), (4.0, {"s": 1.04})], label="Tu logo",
            opacity=keys([(0, 0.0), (0.4, 1.0)]))
    streak = t.track("shape", "Destello")
    t.solid(streak, "#FFFFFF", 1.0, 1.1, centered(960, 480, 1700, 10),
            [(0, {"sx": 0.0}, "out"), (0.4, {"sx": 1.0}, "smooth"), (1.1, {"sx": 0.3})],
            layers=[glow("#9BD1FF", 30, 0.9), fill("#FFFFFF"), no_stroke()], opacity=keys([(0, 1.0), (1.1, 0.0)]))
    label(t, t.track("text", "Marca"), "NOMBRE DE TU MARCA", 1.8, 3.2, Box(260, 700, 1400, 120), "Montserrat", 78,
          "#FFFFFF", weight=300, spacing=18, anim_in=tanim("tracking-drift", duration=1.2), name="Marca")
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.9, blurRadius=14)], name="Brillo")
    song(t, "cine", 3)
    return t


# 3 -----------------------------------------------------------------------------------------------

def intro_cinematica_oscura():
    t = wide("h-intro-cinematica-oscura", "Intro cinematográfica", "Cinematic opener", "intro", 8.0, order=2002,
             tags=["cine", "cinematográfico", "película", "intro", "dramático", "tráiler"], thumb_at=5.2)
    slides(t, ["h-nature-04", "h-city-05", "h-travel-02"], 0.0, 2.7, transition="blur_dissolve", tdur=0.7,
           kb_amount=0.1, effects_fn=lambda i: [effect("cinematic_grade", strength=0.7)])
    letterbox(t)
    label(t, t.track("text", "Presenta"), "UNA HISTORIA DE", 0.6, 3.0, Box(460, 470, 1000, 60), "Montserrat", 34,
          "#E8D9B5", weight=500, spacing=14, anim_in=tanim("fade", duration=0.8), anim_out=tanim("fade", duration=0.6),
          name="Antetítulo")
    label(t, t.track("text", "Título"), "EL VIAJE", 3.6, 4.4, Box(160, 400, 1600, 260), "Cinzel", 190, "#F4EDE4",
          weight=600, spacing=40, layers=[glow("#E8D9B5", 20, 0.35), fill("#F4EDE4")],
          anim_in=tanim("blur-in", duration=1.2, unit="character", stagger=0.08, blur=20), name="Título")
    line(t, t.track("shape", "Línea"), "#E8D9B5", 4.4, 3.6, centered(960, 690, 520, 3), grow="c", length=0.9)
    t.adjust([effect("light_leak", intensity=0.45, hue=0.07, speed=0.6), effect("stylize.film_grain", amount=0.22)],
             name="Fuga de luz")
    song(t, "epic", 0)
    return t


# 4 -----------------------------------------------------------------------------------------------

def intro_tinta():
    t = wide("h-intro-tinta", "Intro de tinta", "Ink reveal intro", "intro", 6.0, order=2003,
             tags=["tinta", "artístico", "intro", "acuarela", "manchas"], thumb_at=1.9, background="#F6F1E7")
    bg(t, "#F6F1E7")
    rng = random.Random(4)
    # Ink blots spread over the paper, then the photo blooms out from under them as they draw back.
    host = t.track("video", "Foto")
    clip = t.photo(host, "h-travel-06", 0, 6.0, t.full, kb(6.0, 1.06, 1.0), label="Tu foto")
    t.mask(host, clip, "ellipse", feather=160,
           keyframes={"w": keys([(0, 0.0, "hold"), (0.9, 0.0, "out"), (2.6, 1.15)]),
                      "h": keys([(0, 0.0, "hold"), (0.9, 0.0, "out"), (2.6, 1.3)])})
    blots = [(520, 480, 760), (1340, 560, 820), (900, 300, 560), (1520, 250, 480), (380, 840, 560), (1140, 880, 600)]
    for i, (x, y, s) in enumerate(blots):
        t.solid(t.track("shape", "Tinta"), "#1F2A44", 0.1 + i * 0.12, 5.9 - i * 0.12, centered(x, y, s, s * 0.85),
                [(0, {"s": 0.0}, "out"), (1.0, {"s": 1.0}, "inout"), (2.4 - i * 0.05, {"s": 0.55}, "linear"),
                 (5.9 - i * 0.12, {"s": 0.45})], kind="cloud" if i % 2 else "ellipse",
                opacity=keys([(0, 0.92, "hold"), (1.2, 0.92, "smooth"), (2.6, 0.35)]))
    sp = t.track("shape", "Salpicaduras")
    for k in range(10):
        x, y = rng.uniform(150, 1770), rng.uniform(120, 960)
        s = rng.uniform(20, 60)
        t.solid(sp, "#1F2A44", 0.4 + k * 0.15, 5.6 - k * 0.15, centered(x, y, s, s), pop(0, 0.3), kind="ellipse",
                alpha=0.85)
    label(t, t.track("text", "Título"), "Arte y viajes", 2.6, 3.4, Box(160, 420, 1600, 240), "Kaushan Script", 170,
          "#FFFFFF", weight=400, layers=[shadow("#1F2A44", 0, 6, 18, 0.6), fill("#FFFFFF")],
          anim_in=tanim("wipe", duration=1.0, angle=0, softness=0.4), name="Título")
    song(t, "calm", 1)
    return t


# 5 -----------------------------------------------------------------------------------------------

def intro_glitch():
    t = wide("h-intro-glitch", "Intro glitch", "Glitch intro", "intro", 5.0, order=2004,
             tags=["glitch", "digital", "intro", "gaming", "tecnología", "rgb"], thumb_at=3.8, background="#050505")
    bg(t, "#07070A")
    slides(t, ["h-city-04", "h-tech-02", "h-concert-01", "h-gaming-01"], 0.0, 0.5, transition=None,
           effects_fn=lambda i: [effect("color.basic", saturation=-0.3, contrast=0.3)])
    photo_bg(t, "h-tech-01", 2.0, 3.0, s1=1.05, label="Fondo")
    shade_full(t, 0.55, 2.0)
    label(t, t.track("text", "Sombra"), "GLITCH", 2.1, 2.9, Box(160, 330, 1600, 360), "Russo One", 300, "#08F7FE",
          weight=400, spacing=10, editable=False, motion=[(0, {"dx": -14}), (0.1, {"dx": 10}), (0.2, {"dx": -6}), (0.3, {"dx": -8})],
          opacity=keys([(0, 0.8)]))
    label(t, t.track("text", "Sombra"), "GLITCH", 2.1, 2.9, Box(160, 330, 1600, 360), "Russo One", 300, "#FF2E63",
          weight=400, spacing=10, editable=False, motion=[(0, {"dx": 14}), (0.1, {"dx": -10}), (0.2, {"dx": 6}), (0.3, {"dx": 8})],
          opacity=keys([(0, 0.8)]))
    label(t, t.track("text", "Título"), "GLITCH", 2.1, 2.9, Box(160, 330, 1600, 360), "Russo One", 300, "#FFFFFF",
          weight=400, spacing=10, anim_in=tanim("glitch-in", duration=0.5, offset=0.4, skew=30), name="Título")
    label(t, t.track("text", "Sub"), "> nuevo episodio", 2.6, 2.4, Box(560, 700, 800, 70), "VT323", 60, "#08F7FE",
          weight=400, anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Subtítulo")
    t.adjust([effect("digital_glitch", animated={"intensity": spike([0.0, 0.5, 1.0, 1.5, 2.0, 3.4], 0.9, 0.25)},
                     rgbAmount=18, blockAmount=0.6),
              effect("rgb_split", animated={"amount": spike([2.0, 3.4], 26, 0.3)})], name="Glitch")
    song(t, "electro", 0)
    return t


# 6 -----------------------------------------------------------------------------------------------

def intro_vlog_polaroid():
    t = wide("h-intro-vlog-polaroid", "Intro de vlog con polaroids", "Polaroid vlog intro", "intro", 7.0,
             order=2005, tags=["vlog", "polaroid", "intro", "fotos", "aesthetic", "diario"], thumb_at=4.4,
             background="#E9DCC9")
    bg_gradient(t, [(0, "#EFE4D2"), (1, "#DCC8AE")], angle=120)
    spots = [("h-travel-04", centered(520, 520, 520, 520), -9, 0.3), ("h-beach-02", centered(980, 470, 520, 520), 4, 0.9),
             ("h-cafe-04", centered(1430, 540, 520, 520), 10, 1.5)]
    for i, (s, box, ang, at) in enumerate(spots):
        framed(t, s, at, 7.0 - at, box, [(0, {"s": 1.35, "dy": -80}, "out"), (0.45, {}, "linear"), (7.0 - at, {"s": 1.03})],
               border=22, bottom=110, colour="#FFFDF8", rotation=keys([(0, ang * 2.2, "out"), (0.45, ang)]),
               label=f"Foto {i + 1}")
    label(t, t.track("text", "Nombre"), "diario de Sofía", 2.4, 4.6, Box(260, 830, 1400, 170), "Caveat", 140,
          "#2E2A25", weight=700, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Nombre del vlog")
    label(t, t.track("text", "Episodio"), "EP. 12", 3.0, 4.0, Box(1560, 70, 300, 80), "DM Sans", 44, "#2E2A25",
          weight=700, spacing=6, anim_in=tanim("fade", duration=0.5), name="Episodio")
    grain(t, 0.15)
    song(t, "upbeat", 6)
    return t


# 7 -----------------------------------------------------------------------------------------------

def intro_minimal_linea():
    t = wide("h-intro-minimal-linea", "Intro minimalista", "Minimal line intro", "intro", 5.0, order=2006,
             tags=["minimal", "limpio", "intro", "elegante", "blanco"], thumb_at=3.4, background="#FAFAF7")
    bg(t, "#FAFAF7")
    line(t, t.track("shape", "Línea"), "#111111", 0.3, 4.7, centered(960, 540, 700, 4), grow="c", length=0.8)
    label(t, t.track("text", "Nombre"), "ESTUDIO NORTE", 1.0, 4.0, Box(260, 380, 1400, 140), "Raleway", 92,
          "#111111", weight=300, spacing=22, anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.04),
          name="Nombre")
    label(t, t.track("text", "Lema"), "diseño · fotografía · video", 1.6, 3.4, Box(460, 580, 1000, 70), "Raleway",
          40, "#6B6B6B", weight=400, spacing=6, anim_in=tanim("fade", duration=0.7), name="Lema")
    dot = t.track("shape", "Punto")
    t.solid(dot, "#E63946", 2.2, 2.8, centered(1330, 540, 18, 18), pop(0, 0.35), kind="ellipse")
    song(t, "calm", 0)
    return t


# 8 -----------------------------------------------------------------------------------------------

def intro_gaming_neon():
    t = wide("h-intro-gaming-neon", "Intro gaming neón", "Neon gaming intro", "intro", 6.0, order=2007,
             tags=["gaming", "gamer", "neón", "intro", "stream", "videojuegos"], thumb_at=3.4, background="#0A0014")
    photo_bg(t, "h-gaming-01", s1=1.15, label="Tu setup")
    shade_full(t, 0.55, colour="#0A0014")
    grid = t.track("shape", "Rejilla")
    for k in range(9):
        t.solid(grid, "#B026FF", 0.0, 6.0, Box(0, 640 + k * 50, 1920, 3), alpha=0.25 + k * 0.05) if k == 0 else \
            t.solid(t.track("shape", "Rejilla"), "#B026FF", 0.0, 6.0, Box(0, 640 + k * 50, 1920, 3), alpha=0.2 + k * 0.06)
    hexa = t.track("shape", "Emblema")
    t.solid(hexa, "#08F7FE", 0.6, 5.4, centered(960, 380, 260, 260), pop(0, 0.5), kind="hexagon",
            layers=[glow("#08F7FE", 30, 0.9), hollow_fill(), hollow_stroke("#08F7FE", 10)])
    label(t, t.track("text", "Icono"), "▶", 0.8, 5.2, centered(975, 380, 200, 200), "Inter", 110, "#FFFFFF",
          weight=900, editable=False, motion=pop(0, 0.5))
    label(t, t.track("text", "Gamer"), "NOMBRE GAMER", 1.4, 4.6, Box(160, 560, 1600, 180), "Orbitron", 130, "#FFFFFF",
          weight=900, spacing=8, layers=[glow("#FF2EF7", 28, 0.9), stroke(3, "#FF2EF7"), fill("#FFFFFF")],
          anim_in=tanim("flicker-in", duration=0.8), anim_loop=tanim("flicker", intensity=0.15, speed=6),
          name="Nombre gamer")
    label(t, t.track("text", "Sub"), "EN VIVO · TODOS LOS VIERNES", 2.0, 4.0, Box(460, 760, 1000, 70), "Exo 2", 42,
          "#08F7FE", weight=700, spacing=8, anim_in=tanim("fade", duration=0.5), name="Horario")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=1.0, blurRadius=16),
              effect("zoom_pulse", animated={"punch": spike([0.6, 1.4], 0.5, 0.3)})], name="Brillo")
    song(t, "electro", 2)
    return t


def hollow_fill() -> dict:
    return {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def hollow_stroke(colour: str, width: float) -> dict:
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}, "opacity": 1.0}


# 9 -----------------------------------------------------------------------------------------------

def intro_podcast_ondas():
    t = wide("h-intro-podcast-ondas", "Intro de podcast", "Podcast intro", "intro", 7.0, order=2008,
             tags=["podcast", "audio", "entrevista", "intro", "ondas", "programa"], thumb_at=4.0, background="#1E1B2E")
    bg_gradient(t, [(0, "#2A1F4A"), (1, "#14121F")], angle=135)
    bars = 28
    rng = random.Random(9)
    for i in range(bars):
        tr = t.track("shape", "Onda") if i % 7 == 0 else tr
        x = 1060 + i * 26
        h = rng.uniform(60, 260)
        pts = [(0, {"sy": 0.2})]
        at = 0.0
        while at < 6.5:
            at += rng.uniform(0.18, 0.35)
            pts.append((at, {"sy": rng.uniform(0.25, 1.0)}, "smooth"))
        t.solid(tr, "#FFB547" if i % 3 else "#FF6B8A", 0.5, 6.5, centered(x, 540, 14, h), pts, radius=7,
                kind="rounded-rectangle")
    circle_photo(t, "h-podcast-03", 0.3, 6.7, centered(560, 540, 560, 560), pop(0, 0.6, 0.6), ring_colour="#FFB547",
                 ring_width=12, label="Foto de los anfitriones")
    label(t, t.track("text", "Programa"), "La charla", 1.2, 5.8, Box(1040, 230, 800, 160), "DM Serif Display", 130,
          "#FFFFFF", weight=400, anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.15),
          name="Nombre del podcast")
    label(t, t.track("text", "Episodio"), "EPISODIO 24 · CON ANA RUIZ", 1.8, 5.2, Box(1040, 760, 800, 70), "DM Sans", 38,
          "#FFB547", weight=700, spacing=4, align="left", anim_in=tanim("fade", duration=0.5), name="Episodio")
    song(t, "jazz", 0)
    return t


# 10 ----------------------------------------------------------------------------------------------

def intro_noticias():
    t = wide("h-intro-noticias", "Apertura de noticiero", "News opener", "intro", 6.0, order=2009,
             tags=["noticias", "noticiero", "informativo", "intro", "periodismo", "último momento"], thumb_at=3.6,
             background="#0A1B3D")
    bg_gradient(t, [(0, "#0D2A66"), (1, "#06102A")], angle=90)
    for k in range(4):
        ring(t, t.track("shape", "Globo"), "#3D7BFF", 3, 0.0, 6.0, centered(1400, 540, 420 + k * 220, 420 + k * 220),
             [(0, {"s": 0.6}, "out"), (1.2, {"s": 1.0}, "linear"), (6.0, {"s": 1.08})], alpha=0.5 - k * 0.1)
    globe = t.track("shape", "Globo")
    t.solid(globe, "#1E5BFF", 0.2, 5.8, centered(1400, 540, 380, 380), pop(0, 0.6, 0.4), kind="ellipse",
            layers=[glow("#3D7BFF", 40, 0.8), gradient([(0, "#4F8BFF"), (1, "#0F2E8A")], angle=120), no_stroke()])
    # Wireframe: meridians that turn (ellipses that narrow and widen) and three parallels.
    for k in range(4):
        w0 = 380 * (1 - k / 4)
        outline(t, t.track("shape", "Meridiano"), "#BFD4FF", 3, 0.5, 5.5, centered(1400, 540, max(w0, 20), 380),
                [(0, {"s": 0.0}, "out"), (0.6, {}, "linear"), (5.5, {"sx": 0.35 if k == 0 else 1.6 - k * 0.3})],
                kind="ellipse", alpha=0.7)
    for y, w in ((540, 380), (440, 330), (640, 330)):
        t.solid(t.track("shape", "Paralelo"), "#BFD4FF", 0.7, 5.3, centered(1400, y, w, 3), pop(0, 0.4), alpha=0.6)
    for i in range(3):
        sweep = t.track("shape", "Franja")
        t.solid(sweep, ["#E10600", "#FFFFFF", "#1E5BFF"][i], 0.1 + i * 0.1, 0.9, Box(0, 300 + i * 160, 1920, 120),
                [(0, {"dx": -1920}, "inout"), (0.45, {}, "inout"), (0.9, {"dx": 1920})])
    bar = t.track("shape", "Caja")
    t.solid(bar, "#E10600", 1.0, 5.0, Box(140, 420, 900, 150), slide_in(dx=-1000, length=0.5))
    t.solid(t.track("shape", "Caja"), "#FFFFFF", 1.2, 4.8, Box(140, 570, 900, 90), slide_in(dx=-1000, length=0.5))
    label(t, t.track("text", "Programa"), "NOTICIAS 24", 1.3, 4.7, Box(170, 420, 860, 150), "Oswald", 110, "#FFFFFF",
          weight=700, spacing=4, align="left", anim_in=tanim("slide-right", duration=0.4), name="Nombre del noticiero")
    label(t, t.track("text", "Edición"), "EDICIÓN CENTRAL", 1.5, 4.5, Box(170, 570, 860, 90), "Oswald", 54, "#0A1B3D",
          weight=600, spacing=10, align="left", anim_in=tanim("fade", duration=0.4), name="Edición")
    song(t, "epic", 5)
    return t


# 11 ----------------------------------------------------------------------------------------------

def intro_deportes():
    t = wide("h-intro-deportes", "Intro deportiva", "Sports intro", "intro", 6.0, order=2010,
             tags=["deportes", "fútbol", "atletismo", "intro", "energía", "equipo"], thumb_at=4.3, background="#000000")
    shots = ["h-sport-01", "h-soccer-02", "h-sport-04", "h-soccer-03", "h-sport-05", "h-fitness-03"]
    slides(t, shots, 0.0, 0.5, transition=None, kb_amount=0.12,
           effects_fn=lambda i: [effect("color.basic", contrast=0.35, saturation=-0.1)])
    photo_bg(t, "h-sport-02", 3.0, 3.0, s1=1.1, label="Foto principal")
    for i, c in enumerate(["#E10600", "#FFFFFF", "#E10600"]):
        t.solid(t.track("shape", "Franja"), c, 2.6 + i * 0.07, 0.8, Box(-300, -200, 900, 1500),
                [(0, {"dx": -1300}, "inout"), (0.4, {"dx": 1100}, "inout"), (0.8, {"dx": 2600})],
                rotation=keys([(0, 14)]))
    band = t.track("shape", "Banda")
    t.solid(band, "#E10600", 3.2, 2.8, Box(-100, 640, 2200, 230), slide_in(dx=-2300, length=0.4),
            rotation=keys([(0, -4)]))
    label(t, t.track("text", "Título"), "TEMPORADA 2026", 3.3, 2.7, Box(0, 640, 1920, 230), "Anton", 190, "#FFFFFF",
          weight=400, spacing=4, anim_in=tanim("slide-left", duration=0.35, unit="word", stagger=0.1),
          rotation=keys([(0, -4)]), name="Título")
    label(t, t.track("text", "Equipo"), "CLUB DEPORTIVO", 3.6, 2.4, Box(120, 930, 1000, 80), "Barlow Condensed", 64,
          "#FFFFFF", weight=700, spacing=10, align="left", anim_in=tanim("fade", duration=0.4), name="Equipo")
    t.adjust([effect("beat_shake", animated={"amount": spike([0.5 * k for k in range(1, 7)], 0.6, 0.2)}),
              effect("zoom_pulse", animated={"punch": spike([3.0], 0.7, 0.35)})], name="Golpe")
    song(t, "epic", 1)
    return t


# 12 ----------------------------------------------------------------------------------------------

def intro_cocina():
    t = wide("h-intro-cocina", "Intro de canal de cocina", "Cooking channel intro", "intro", 6.0, order=2011,
             tags=["cocina", "recetas", "comida", "intro", "chef", "canal"], thumb_at=3.6)
    photo_bg(t, "h-food-02", s1=1.12, label="Foto del plato")
    shade_full(t, 0.25)
    rng = random.Random(12)
    for k in range(9):  # steam: soft white puffs that rise and spread
        x = rng.uniform(700, 1220)
        s = rng.uniform(80, 160)
        d = min(2.2, 5.7 - k * 0.55)
        t.solid(t.track("shape", "Vapor"), "#FFFFFF", 0.3 + k * 0.55, d, centered(x, 640, s, s),
                [(0, {"s": 0.4}, "linear"), (2.2, {"s": 1.6, "dy": -420})], kind="ellipse",
                layers=[gradient([(0, "#FFFFFF", 0.32), (1, "#FFFFFF", 0.0)], angle=0), no_stroke()])
    tag = t.track("shape", "Etiqueta")
    t.solid(tag, "#FFF4E0", 1.0, 5.0, centered(960, 520, 1100, 300), pop(0, 0.5, 0.3), kind="banner",
            layers=[shadow("#000000", 0, 14, 30, 0.35), fill("#FFF4E0"), no_stroke()])
    label(t, t.track("text", "Canal"), "La cocina de Marta", 1.3, 4.7, centered(960, 505, 1000, 200), "Lobster", 120,
          "#B23A1E", weight=400, anim_in=tanim("pop", duration=0.45, unit="word", stagger=0.12, ease="back"),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "RECETAS FÁCILES PARA CADA DÍA", 1.8, 4.2, centered(960, 790, 1200, 80),
          "Montserrat", 44, "#FFFFFF", weight=700, spacing=8, layers=[shadow("#000000", 0, 3, 10, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.02), name="Lema")
    t.adjust([effect("color.basic", temperature=0.2, saturation=0.15, contrast=0.1)], name="Color")
    song(t, "jazz", 1)
    return t


# 13 ----------------------------------------------------------------------------------------------

def intro_tech():
    t = wide("h-intro-tech", "Intro de tecnología", "Tech intro", "intro", 6.0, order=2012,
             tags=["tecnología", "tech", "digital", "intro", "reseñas", "futuro"], thumb_at=3.8, background="#040B18")
    bg_gradient(t, [(0, "#071A33"), (1, "#020610")], angle=90)
    for k in range(1, 12):
        t.solid(t.track("shape", "Rejilla"), "#1F4E8C", 0, 6.0, Box(k * 160, 0, 2, 1080), alpha=0.35)
    for k in range(1, 7):
        t.solid(t.track("shape", "Rejilla"), "#1F4E8C", 0, 6.0, Box(0, k * 155, 1920, 2), alpha=0.35)
    rng = random.Random(13)
    nodes = [(rng.randint(1, 11) * 160, rng.randint(1, 6) * 155) for _ in range(12)]
    for i, (x, y) in enumerate(nodes):
        t.solid(t.track("shape", "Nodo"), "#29E0FF", 0.2 + i * 0.12, 5.8 - i * 0.12, centered(x, y, 18, 18),
                pop(0, 0.3), kind="ellipse", layers=[glow("#29E0FF", 16, 0.9), fill("#29E0FF"), no_stroke()])
    for i in range(6):
        x, y = nodes[i]
        line(t, t.track("shape", "Enlace"), "#29E0FF", 0.5 + i * 0.15, 5.5 - i * 0.15, Box(x, y - 1, 160 * (1 + i % 3), 3),
             grow="x", length=0.4, alpha=0.8)
    panel = t.track("shape", "Panel")
    rrect(t, panel, "#071A33", 1.4, 4.6, centered(960, 540, 1100, 360), 30, pop(0, 0.5, 0.8),
          layers=[glow("#29E0FF", 30, 0.5), fill("#071A33", 0.85), {"id": "stroke", "kind": "stroke", "enabled": True,
                  "width": 3, "strokeAlign": "inside", "paint": {"kind": "solid", "color": "#ff29e0ff"}, "opacity": 1.0}])
    label(t, t.track("text", "Canal"), "TECH LAB", 1.7, 4.3, centered(960, 500, 1000, 200), "Sora", 150, "#FFFFFF",
          weight=800, spacing=12, anim_in=tanim("snap-together", duration=0.6), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "reseñas · tutoriales · novedades", 2.3, 3.7, centered(960, 640, 1000, 70), "Sora",
          40, "#29E0FF", weight=400, spacing=3, anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Lema")
    song(t, "electro", 3)
    return t


# 14 ----------------------------------------------------------------------------------------------

def intro_viajes_mapa():
    t = wide("h-intro-viajes-mapa", "Intro de viajes", "Travel map intro", "intro", 7.0, order=2013,
             tags=["viajes", "mapa", "ruta", "intro", "aventura", "mochilero"], thumb_at=4.8, background="#F3E9D6")
    bg_gradient(t, [(0, "#F6EEDD"), (1, "#E8D8B9")], angle=135)
    for k in range(5):  # contour lines, like an old map
        outline(t, t.track("shape", "Mapa"), "#C9B38C", 3, 0, 7.0, centered(500 + k * 260, 300 + (k % 2) * 420,
                420 + k * 30, 260 + k * 20), kind="ellipse", alpha=0.5)
    pts = []
    for i in range(26):
        u = i / 25
        pts.append((220 + u * 1300, 820 - math.sin(u * math.pi) * 520 + math.sin(u * 7) * 40))
    route = t.track("shape", "Ruta")
    for i, (x, y) in enumerate(pts):
        if i and i % 8 == 0:
            route = t.track("shape", "Ruta")
        t.solid(route, "#D9480F", 0.4 + i * 0.09, 6.6 - i * 0.09, centered(x, y, 12, 12), pop(0, 0.2), kind="ellipse")
    plane = t.track("text", "Avión")
    motion = [(0.0, {"dx": pts[0][0] - 960, "dy": pts[0][1] - 540})]
    for i in range(1, len(pts)):
        motion.append((i * 0.09, {"dx": pts[i][0] - 960, "dy": pts[i][1] - 540}, "linear"))
    label(t, plane, "✈", 0.4, 6.6, centered(960, 540, 90, 90), "Inter", 64, "#1F2A44", weight=700, editable=False,
          motion=[(0, motion[0][1])] + motion[1:])
    circle_photo(t, "h-travel-08", 2.6, 4.4, centered(1600, 360, 380, 380), pop(0, 0.5), ring_colour="#FFFFFF",
                 ring_width=12, label="Foto del destino")
    pin = t.track("shape", "Pin")
    t.solid(pin, "#D9480F", 2.5, 4.5, centered(1520, 610, 60, 60), pop(0, 0.4), kind="ellipse")
    label(t, t.track("text", "Canal"), "Rumbo al mundo", 1.6, 5.4, Box(120, 70, 1100, 180), "DM Serif Display", 120,
          "#1F2A44", weight=400, align="left", anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.2),
          name="Nombre del canal")
    label(t, t.track("text", "Lugar"), "PRÓXIMA PARADA: ISLANDIA", 3.0, 4.0, Box(1240, 820, 640, 70), "Montserrat",
          36, "#1F2A44", weight=700, spacing=4, anim_in=tanim("fade", duration=0.5), name="Destino")
    grain(t, 0.12)
    song(t, "world", 0)
    return t


# 15 ----------------------------------------------------------------------------------------------

def intro_corporativa():
    t = wide("h-intro-corporativa", "Apertura corporativa", "Corporate opener", "intro", 6.0, order=2014,
             tags=["corporativo", "empresa", "negocio", "presentación", "logo", "profesional"], thumb_at=3.8,
             background="#FFFFFF")
    bg(t, "#FFFFFF")
    for i, (c, y, w) in enumerate([("#0B3D91", 0, 760), ("#1E66F5", 360, 620), ("#7DB4FF", 720, 480)]):
        t.solid(t.track("shape", "Bloque"), c, 0.1 + i * 0.12, 5.9 - i * 0.12, Box(1920 - w, y, w, 360),
                slide_in(dx=w + 40, length=0.6))
    t.photo(t.track("video", "Foto"), "h-office-03", 0.5, 5.5, Box(1920 - 720, 180, 600, 720),
            [(0, {"dx": 700}, "out"), (0.6, {}, "linear"), (5.5, {"s": 1.04})], label="Foto del equipo")
    t.photo(t.track("video", "Logo"), "logo-01", 1.1, 4.9, centered(400, 330, 300, 300), pop(0, 0.5), label="Tu logo")
    label(t, t.track("text", "Empresa"), "Grupo Norte", 1.5, 4.5, Box(120, 520, 900, 140), "Montserrat", 104,
          "#0B3D91", weight=800, align="left", anim_in=tanim("slide-right", duration=0.5, unit="word", stagger=0.12),
          name="Empresa")
    line(t, t.track("shape", "Línea"), "#1E66F5", 1.9, 4.1, Box(124, 680, 160, 8), length=0.5)
    label(t, t.track("text", "Lema"), "Soluciones que crecen contigo", 2.1, 3.9, Box(120, 710, 900, 80), "Montserrat",
          46, "#4A5568", weight=500, align="left", anim_in=tanim("fade", duration=0.6), name="Lema")
    song(t, "upbeat", 3)
    return t


# 16 ----------------------------------------------------------------------------------------------

def intro_retro_80s():
    t = wide("h-intro-retro-80s", "Intro retro 80s", "Retro 80s intro", "intro", 6.0, order=2015,
             tags=["retro", "80s", "synthwave", "neón", "intro", "ochentas"], thumb_at=3.6, background="#12002B")
    bg_gradient(t, [(0, "#12002B"), (0.55, "#5B0E6B"), (0.62, "#1A0033"), (1, "#0A0018")], angle=90)
    sun = t.track("shape", "Sol")
    t.solid(sun, "#FFB000", 0, 6.0, centered(960, 520, 560, 560), [(0, {"dy": 160}, "out"), (2.0, {})], kind="ellipse",
            layers=[glow("#FF4FD8", 60, 0.7), gradient([(0, "#FFE259"), (1, "#FF4FD8")], angle=90), no_stroke()])
    for k in range(6):  # stripes cut across the lower half of the sun
        t.solid(t.track("shape", "Franja"), "#1A0033", 0, 6.0, Box(600, 560 + k * 38, 720, 8 + k * 3),
                [(0, {"dy": 160}, "out"), (2.0, {})])
    horizon = 660
    for k in range(9):
        y = horizon + (k ** 1.7) * 9
        t.solid(t.track("shape", "Suelo"), "#FF2E97", 0, 6.0, Box(0, y, 1920, 3), [(0, {"dy": 0}, "linear"), (6.0, {"dy": 9 * (k ** 0.9)})],
                alpha=0.75, layers=[glow("#FF2E97", 10, 0.8), fill("#FF2E97"), no_stroke()])
    for k in range(-7, 8):
        bottom_x = 960 + k * 260
        cx, cy = (960 + bottom_x) / 2, (horizon + 1080) / 2
        length = math.hypot(bottom_x - 960, 1080 - horizon)
        ang = math.degrees(math.atan2(bottom_x - 960, 1080 - horizon))
        t.solid(t.track("shape", "Suelo"), "#FF2E97", 0, 6.0, centered(cx, cy, 3, length), alpha=0.6,
                rotation=keys([(0, -ang)]), layers=[glow("#FF2E97", 10, 0.8), fill("#FF2E97"), no_stroke()])
    chrome = [glow("#FF4FD8", 26, 0.8), stroke(4, "#2A0B4A"),
              gradient([(0, "#FFFFFF"), (0.45, "#9AD9FF"), (0.5, "#2A3E8C"), (0.75, "#FFB3F0"), (1, "#FFFFFF")], angle=90)]
    label(t, t.track("text", "Título"), "RETRO WAVE", 1.2, 4.8, Box(160, 170, 1600, 260), "Audiowide", 190, "#FFFFFF",
          weight=400, spacing=6, layers=chrome, anim_in=tanim("zoom-out", duration=0.8), name="Título")
    label(t, t.track("text", "Sub"), "Episodio 1", 2.0, 4.0, Box(560, 420, 800, 120), "Pacifico", 90, "#FFE259",
          weight=400, layers=[glow("#FF2E97", 18, 0.9), fill("#FFE259")], anim_in=tanim("wipe", duration=0.7, angle=0),
          rotation=keys([(0, -6)]), name="Subtítulo")
    t.adjust([effect("stylize.vhs", noise=18, chroma=3), effect("bloom_glow", threshold=0.6, intensity=0.8)],
             name="VHS")
    song(t, "electro", 1)
    return t


# 17 ----------------------------------------------------------------------------------------------

def intro_documental():
    t = wide("h-intro-documental", "Apertura de documental", "Documentary opener", "intro", 9.0, order=2016,
             tags=["documental", "historia", "serio", "intro", "cine", "naturaleza"], thumb_at=6.4, background="#000000")
    slides(t, ["h-nature-02", "h-elderly-03", "h-nature-06"], 0.0, 3.0, transition="crossfade", tdur=1.0,
           kb_amount=0.07, effects_fn=lambda i: [effect("color.basic", saturation=-0.55, contrast=0.15, fade=0.12)])
    shade_full(t, 0.25)
    label(t, t.track("text", "Antetítulo"), "UN DOCUMENTAL DE ELENA MORALES", 0.8, 3.6, Box(260, 480, 1400, 70),
          "Cormorant Garamond", 44, "#F2EDE4", weight=500, spacing=10, anim_in=tanim("fade", duration=1.0),
          anim_out=tanim("fade", duration=0.8), name="Autor")
    label(t, t.track("text", "Título"), "Raíces", 4.8, 4.2, Box(260, 380, 1400, 260), "Cormorant Garamond", 230,
          "#FFFFFF", weight=600, italic=True, anim_in=tanim("blur-in", duration=1.6, blur=30), name="Título")
    label(t, t.track("text", "Sub"), "lo que la tierra recuerda", 5.6, 3.4, Box(460, 650, 1000, 80), "Cormorant Garamond",
          60, "#EFE4CF", weight=400, italic=True, anim_in=tanim("fade", duration=1.0), name="Subtítulo")
    grain(t, 0.28, 1.8)
    vignette(t, 0.6)
    song(t, "classic", 2)
    return t


# 18 ----------------------------------------------------------------------------------------------

def intro_boda():
    t = wide("h-intro-boda", "Intro de boda", "Wedding intro", "intro", 9.0, order=2017,
             tags=["boda", "novios", "matrimonio", "intro", "romántico", "elegante"], thumb_at=5.8)
    slides(t, ["h-wedding-03", "h-wedding-04", "h-wedding-05"], 0.0, 3.0, transition="blur_dissolve", tdur=1.0,
           kb_amount=0.06, effects_fn=lambda i: [effect("color.basic", temperature=0.12, fade=0.1)])
    shade_full(t, 0.3)
    dots(t, ["#F2D59B", "#FFFFFF", "#E8C27A"], 30, 0.0, 9.0, seed=18, size=(6, 16), kinds=("star", "ellipse"), drift=80)
    label(t, t.track("text", "Nombres"), "Ana & Leo", 1.0, 8.0, Box(160, 340, 1600, 300), "Great Vibes", 230,
          "#FFFFFF", weight=400, layers=[glow("#E8C27A", 24, 0.55), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=1.4, unit="character", stagger=0.06, blur=16), name="Nombres")
    line(t, t.track("shape", "Línea"), "#E8C27A", 2.0, 7.0, centered(960, 680, 360, 3), grow="c", length=0.9)
    label(t, t.track("text", "Fecha"), "14 · 02 · 2027", 2.4, 6.6, Box(560, 700, 800, 90), "Cinzel", 56, "#F2E6CF",
          weight=500, spacing=10, anim_in=tanim("fade", duration=0.8), name="Fecha")
    t.adjust([effect("light_leak", intensity=0.35, hue=0.08, speed=0.5), effect("bloom_glow", threshold=0.7,
              intensity=0.5)], name="Luz")
    song(t, "romantic", 0)
    return t


# 19 ----------------------------------------------------------------------------------------------

def intro_colorida_formas():
    t = wide("h-intro-colorida-formas", "Intro de formas de colores", "Colourful shapes intro", "intro", 5.0,
             order=2018, tags=["colores", "formas", "divertido", "intro", "alegre", "geométrico"], thumb_at=3.2,
             background="#FFF8EC")
    bg(t, "#FFF8EC")
    shapes = [("ellipse", "#FF5A5F", 300, 260, 220), ("rounded-rectangle", "#FFC43D", 1580, 250, 240),
              ("triangle", "#1B9AAA", 420, 820, 230), ("star", "#7B2FF7", 1520, 820, 250), ("ellipse", "#06D6A0", 1700, 560, 130),
              ("hexagon", "#EF476F", 220, 560, 140), ("diamond", "#118AB2", 960, 150, 120), ("heart", "#FF8C42", 960, 930, 120)]
    for i, (kind, c, x, y, s) in enumerate(shapes):
        t.solid(t.track("shape", "Forma"), c, 0.1 + i * 0.1, 4.9 - i * 0.1, centered(x, y, s, s),
                [(0, {"s": 0.0}, "back"), (0.5, {}, "smooth"), (2.0, {"dy": -20}, "smooth"), (3.5, {"dy": 15}, "smooth"),
                 (4.9 - i * 0.1, {})], kind=kind, radius=40,
                rotation=keys([(0, -40 + i * 13, "out"), (0.5, i * 6 - 20, "smooth"), (4.9 - i * 0.1, i * 6 - 5)]))
    label(t, t.track("text", "Título"), "¡Hola, amigos!", 1.0, 4.0, Box(260, 380, 1400, 240), "Fredoka", 170, "#2B2D42",
          weight=700, anim_in=tanim("bounce", duration=0.6, unit="character", stagger=0.04),
          name="Título")
    label(t, t.track("text", "Sub"), "bienvenidos al canal", 1.7, 3.3, Box(560, 620, 800, 80), "Fredoka", 56,
          "#FF5A5F", weight=600, anim_in=tanim("pop", duration=0.4), name="Subtítulo")
    song(t, "fun", 0)
    return t


# 20 ----------------------------------------------------------------------------------------------

def intro_zoom_fotos():
    t = wide("h-intro-zoom-fotos", "Intro con zoom de fotos", "Photo zoom intro", "intro", 6.0, order=2019,
             tags=["zoom", "fotos", "intro", "dinámico", "collage", "viaje"], thumb_at=4.6, background="#111111")
    samples = ["h-city-04", "h-travel-06", "h-beach-01", "h-nature-05", "h-travel-03"]
    for i, s in enumerate(samples):
        at = i * 0.7
        d = 6.0 - at
        t.photo(t.track("video", f"Foto {i + 1}"), s, at, d, t.full,
                [(0, {"s": 0.18}, "inout"), (0.7, {"s": 1.0}, "linear"), (d, {"s": 1.12})], label=f"Foto {i + 1}")
        if i < len(samples) - 1:
            outline(t, t.track("shape", "Borde"), "#FFFFFF", 12, at, 0.7, t.full,
                    [(0, {"s": 0.18}, "inout"), (0.7, {"s": 1.0})])
    shade_full(t, 0.35, 3.2)
    label(t, t.track("text", "Título"), "MIL LUGARES", 3.4, 2.6, Box(160, 380, 1600, 220), "Bebas Neue", 230, "#FFFFFF",
          weight=400, spacing=12, anim_in=tanim("type-on-blur", duration=0.7, unit="character", stagger=0.04),
          name="Título")
    label(t, t.track("text", "Sub"), "un viaje por el mundo", 3.9, 2.1, Box(560, 610, 800, 70), "Montserrat", 44,
          "#FFFFFF", weight=500, spacing=6, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.7, 1.4, 2.1, 2.8], 0.4, 0.3)})], name="Golpe")
    song(t, "cine", 1)
    return t


# 21 ----------------------------------------------------------------------------------------------

def intro_texto_gigante():
    t = wide("h-intro-texto-gigante", "Intro de texto gigante", "Giant text intro", "intro", 5.0, order=2020,
             tags=["texto", "tipografía", "intro", "impacto", "foto en letras", "bold"], thumb_at=2.2,
             background="#0E0E0E")
    bg(t, "#0E0E0E")
    host = t.track("video", "Foto")
    clip = t.photo(host, "h-concert-02", 0.0, 3.2, t.full, [(0, {"s": 1.25}, "out"), (3.2, {"s": 1.0})],
                   label="Foto dentro del texto")
    t.mask(host, clip, "text", text="CREA", feather=0)
    photo_bg(t, "h-concert-02", 3.0, 2.0, s1=1.06, label="Foto", reuse="p1")
    shade_full(t, 0.45, 3.0)
    flash(t, 3.0, 0.3)
    label(t, t.track("text", "Título"), "crea sin miedo", 3.2, 1.8, Box(160, 420, 1600, 200), "Montserrat", 120,
          "#FFFFFF", weight=900, spacing=2, anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1),
          name="Frase")
    song(t, "electro", 0)
    return t


# 22 ----------------------------------------------------------------------------------------------

def intro_split():
    t = wide("h-intro-split", "Intro de pantalla dividida", "Split screen intro", "intro", 6.0, order=2021,
             tags=["pantalla dividida", "split", "fotos", "intro", "moderno", "franjas"], thumb_at=3.8, background="#000000")
    samples = ["h-portrait-03", "h-city-03", "h-man-04", "h-concert-04"]
    for i, s in enumerate(samples):
        x = i * 480
        dy = -1100 if i % 2 else 1100
        t.photo(t.track("video", f"Franja {i + 1}"), s, 0.1 + i * 0.12, 5.9 - i * 0.12, Box(x, 0, 480, 1080),
                [(0, {"dy": dy}, "out"), (0.6, {}, "linear"), (5.9 - i * 0.12, {"s": 1.06})], label=f"Foto {i + 1}")
    for i in range(1, 4):
        t.solid(t.track("shape", "Separador"), "#FFFFFF", 0.6, 5.4, Box(i * 480 - 4, 0, 8, 1080),
                [(0, {"sy": 0.0}, "out"), (0.5, {})])
    band = t.track("shape", "Banda")
    t.solid(band, "#FFFFFF", 1.6, 4.4, Box(0, 430, 1920, 220), [(0, {"sy": 0.0}, "out"), (0.4, {})])
    label(t, t.track("text", "Título"), "CUATRO HISTORIAS", 1.8, 4.2, Box(0, 430, 1920, 220), "Oswald", 150,
          "#111111", weight=700, spacing=14, anim_in=tanim("rise", duration=0.5, unit="character", stagger=0.03),
          name="Título")
    song(t, "cine", 2)
    return t


# 23 ----------------------------------------------------------------------------------------------

def intro_tiza():
    t = wide("h-intro-tiza", "Intro de pizarra", "Chalkboard intro", "intro", 6.0, order=2022,
             tags=["educación", "pizarra", "clases", "tiza", "profesor", "intro"], thumb_at=4.4, background="#1F3B2D")
    bg_gradient(t, [(0, "#2A4A39"), (1, "#16291F")], angle=120)
    outline(t, t.track("shape", "Marco"), "#8B5A2B", 30, 0, 6.0, t.full)
    chalk = "#F2F2EA"
    label(t, t.track("text", "Título"), "Aprende conmigo", 0.4, 5.6, Box(200, 280, 1520, 220), "Gloria Hallelujah", 140,
          chalk, weight=400, layers=[fill(chalk, 0.92)], anim_in=tanim("typewriter", duration=1.6, unit="character"),
          name="Título")
    line(t, t.track("shape", "Subrayado"), chalk, 2.0, 4.0, Box(420, 520, 1080, 8), length=0.7, alpha=0.85)
    label(t, t.track("text", "Materia"), "matemáticas · ciencias · idiomas", 2.6, 3.4, Box(300, 580, 1320, 90),
          "Patrick Hand", 66, "#FFE08A", weight=400, anim_in=tanim("fade", duration=0.6), name="Materias")
    for i, (glyph, x, y, r) in enumerate([("π", 240, 820, -10), ("★", 1680, 200, 12), ("A+", 1620, 830, -6),
                                         ("2+2=4", 330, 160, 4), ("→", 1460, 470, 0)]):
        label(t, t.track("text", "Garabato"), glyph, 1.2 + i * 0.3, 4.8 - i * 0.3, centered(x, y, 360, 140),
              "Gloria Hallelujah", 84, chalk, weight=400, editable=False, layers=[fill(chalk, 0.7)],
              anim_in=tanim("wipe", duration=0.5, angle=0), rotation=keys([(0, r)]))
    grain(t, 0.25, 2.0)
    song(t, "fun", 3)
    return t


# 24 ----------------------------------------------------------------------------------------------

def intro_elegante_oro():
    t = wide("h-intro-elegante-oro", "Intro elegante dorada", "Elegant gold intro", "intro", 6.0, order=2023,
             tags=["elegante", "dorado", "lujo", "intro", "marca", "premium"], thumb_at=4.0, background="#070707")
    bg_gradient(t, [(0, "#141210"), (1, "#050505")], angle=90)
    gold = [gradient([(0, "#8C6B2F"), (0.35, "#F5D98B"), (0.6, "#B8892E"), (1, "#F1D18A")], angle=60)]
    outline(t, t.track("shape", "Marco"), "#C9A44C", 3, 0.2, 5.8, centered(960, 540, 1500, 760),
            [(0, {"s": 0.85}, "out"), (1.0, {})], alpha=0.9, opacity=keys([(0, 0.0), (0.8, 1.0)]))
    outline(t, t.track("shape", "Marco"), "#C9A44C", 1.5, 0.4, 5.6, centered(960, 540, 1460, 720),
            [(0, {"s": 0.85}, "out"), (1.0, {})], alpha=0.6, opacity=keys([(0, 0.0), (0.8, 1.0)]))
    diamond = t.track("shape", "Monograma")
    t.solid(diamond, "#C9A44C", 0.9, 5.1, centered(960, 330, 150, 150), pop(0, 0.5), kind="diamond",
            layers=[glow("#F5D98B", 20, 0.6)] + gold + [no_stroke()])
    label(t, t.track("text", "Inicial"), "M", 1.0, 5.0, centered(960, 335, 150, 150), "Cinzel", 80, "#141210",
          weight=700, motion=pop(0, 0.5), name="Inicial")
    label(t, t.track("text", "Marca"), "MAISON LUNA", 1.5, 4.5, Box(260, 460, 1400, 180), "Cinzel", 130, "#F5D98B",
          weight=500, spacing=28, layers=[glow("#F5D98B", 16, 0.4)] + gold,
          anim_in=tanim("blur-in", duration=1.0, unit="character", stagger=0.05, blur=12), name="Marca")
    label(t, t.track("text", "Lema"), "ALTA JOYERÍA DESDE 1987", 2.3, 3.7, Box(460, 660, 1000, 70), "Marcellus", 40,
          "#BFA36A", weight=400, spacing=12, anim_in=tanim("fade", duration=0.8), name="Lema")
    t.adjust([effect("bling_sparkle", intensity=0.7, threshold=0.6, density=0.4, size=0.6)], name="Destellos")
    song(t, "classic", 0)
    return t


# 25 ----------------------------------------------------------------------------------------------

def intro_pop_comic():
    t = wide("h-intro-pop-comic", "Intro estilo cómic", "Comic pop intro", "intro", 5.0, order=2024,
             tags=["cómic", "pop art", "divertido", "intro", "historieta", "colores"], thumb_at=3.0, background="#FFE600")
    bg(t, "#FFE600")
    left = t.track("video", "Viñeta 1")
    t.photo(left, "h-portrait-05", 0.1, 4.9, Box(60, 60, 900, 960), slide_in(dx=-1000, length=0.4), label="Foto 1",
            effects=[effect("halftone_comic")])
    t.photo(t.track("video", "Viñeta 2"), "h-man-05", 0.3, 4.7, Box(980, 60, 880, 960), slide_in(dx=1000, length=0.4),
            label="Foto 2", effects=[effect("halftone_comic")])
    for b in (Box(60, 60, 900, 960), Box(980, 60, 880, 960)):
        outline(t, t.track("shape", "Borde"), "#111111", 14, 0.4, 4.6, b)
    burst = t.track("shape", "Estallido")
    t.solid(burst, "#FF2E63", 1.0, 4.0, centered(960, 540, 820, 600), pop(0, 0.4), kind="burst", points=14,
            innerRatio=0.72, layers=[shadow("#111111", 12, 12, 0, 1.0), fill("#FF2E63"), stroke(8, "#111111")],
            rotation=keys([(0, -6)]))
    label(t, t.track("text", "Grito"), "¡POW!", 1.1, 3.9, centered(960, 520, 760, 360), "Bangers", 260, "#FFE600",
          weight=400, layers=[shadow("#111111", 10, 10, 0, 1.0), stroke(10, "#111111"), fill("#FFE600")],
          anim_in=tanim("stamp", duration=0.3), rotation=keys([(0, -6)]), name="Grito")
    label(t, t.track("text", "Sub"), "EPISODIO NUEVO", 1.8, 3.2, Box(560, 800, 800, 110), "Bangers", 84, "#FFFFFF",
          weight=400, layers=[stroke(8, "#111111"), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.3),
          name="Subtítulo")
    t.adjust([effect("beat_shake", animated={"amount": spike([1.1], 0.8, 0.35)})], name="Golpe")
    song(t, "fun", 1)
    return t


# 26 ----------------------------------------------------------------------------------------------

def intro_papel():
    t = wide("h-intro-papel", "Intro de papel recortado", "Paper cut intro", "intro", 6.0, order=2025,
             tags=["papel", "recortes", "manualidades", "intro", "infantil", "capas"], thumb_at=3.5, background="#FDE2C8")
    layers = [("#F28C6B", 2600, 1500), ("#F6B08C", 2200, 1250), ("#FAD0B0", 1800, 1000), ("#FFE9D6", 1400, 760)]
    for i, (c, w, h) in enumerate(layers):
        t.solid(t.track("shape", "Papel"), c, 0, 6.0, centered(960, 540, w, h),
                [(0, {"s": 0.0}, "out"), (0.6 + i * 0.25, {"s": 1.0}, "linear"), (6.0, {"s": 1.03 + i * 0.01})],
                kind="cloud", layers=[shadow("#8A4B2F", 0, 14, 26, 0.35), fill(c), no_stroke()])
    for i, (x, y, c) in enumerate([(360, 240, "#7FB069"), (1580, 300, "#E6AA68"), (300, 860, "#CA3C25"),
                                   (1640, 820, "#1D3557")]):
        t.solid(t.track("shape", "Recorte"), c, 1.4 + i * 0.15, 4.6 - i * 0.15, centered(x, y, 150, 150), pop(0, 0.4),
                kind=["heart", "star", "ellipse", "diamond"][i], layers=[shadow("#000000", 0, 8, 12, 0.3), fill(c), no_stroke()])
    label(t, t.track("text", "Título"), "Hecho a mano", 1.6, 4.4, Box(360, 400, 1200, 200), "Chewy", 150, "#5A2E1B",
          weight=400, layers=[shadow("#FFFFFF", 0, 6, 0, 0.9), fill("#5A2E1B")],
          anim_in=tanim("drop", duration=0.6, unit="character", stagger=0.04), name="Título")
    label(t, t.track("text", "Sub"), "ideas para crear en casa", 2.3, 3.7, Box(460, 600, 1000, 80), "Patrick Hand", 60,
          "#8A4B2F", weight=400, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    song(t, "fun", 2)
    return t


# 27 ----------------------------------------------------------------------------------------------

def intro_suscriptores():
    t = wide("h-intro-suscriptores", "Intro con contador", "Subscriber counter intro", "intro", 6.0, order=2026,
             tags=["suscriptores", "contador", "celebración", "intro", "youtube", "hito"], thumb_at=4.6,
             background="#0F0F0F")
    bg_gradient(t, [(0, "#1C1C1C"), (1, "#0A0A0A")], angle=90)
    confetti(t, ["#FF8C42", "#FFFFFF", "#FFD23F", "#3EC1FF"], 3.4, 2.6, seed=27, lanes=3, density=0.25)
    circle_photo(t, "h-portrait-04", 0.2, 5.8, centered(960, 300, 300, 300), pop(0, 0.5), ring_colour="#FF8C42",
                 ring_width=10, label="Tu foto de perfil")
    values = ["0", "1.204", "8.930", "24.511", "51.876", "78.032", "93.448", "99.999"]
    nums = t.track("text", "Contador")
    for i, v in enumerate(values):
        label(t, nums, v, 0.8 + i * 0.32, 0.32, Box(260, 480, 1400, 220), "Montserrat", 190, "#FFFFFF", weight=900,
              editable=False)
    label(t, nums, "100.000", 0.8 + len(values) * 0.32, 6.0 - (0.8 + len(values) * 0.32), Box(260, 480, 1400, 220),
          "Montserrat", 190, "#FFFFFF", weight=900, anim_in=tanim("pop", duration=0.4),
          anim_loop=tanim("pulse", amount=3, speed=1.2), name="Número final")
    label(t, t.track("text", "Sub"), "¡GRACIAS POR SER PARTE!", 3.6, 2.4, Box(460, 720, 1000, 80), "Montserrat", 50,
          "#FF8C42", weight=800, spacing=6, anim_in=tanim("rise", duration=0.4), name="Mensaje")
    label(t, t.track("text", "Campana"), "🔔", 3.4, 2.6, centered(1390, 330, 160, 160), "Inter", 110, "#FFD23F",
          weight=400, editable=False, rotation=keys([(0, -20, "smooth"), (0.15, 20, "smooth"), (0.3, -15, "smooth"),
                                                     (0.45, 10, "smooth"), (0.6, 0)]), motion=pop(0, 0.4))
    flash(t, 3.36, 0.3, peak=0.6)
    song(t, "upbeat", 1)
    return t


# 28 ----------------------------------------------------------------------------------------------

def intro_musica():
    t = wide("h-intro-musica", "Intro de canal de música", "Music channel intro", "intro", 6.0, order=2027,
             tags=["música", "artista", "sencillo", "intro", "ecualizador", "banda"], thumb_at=3.8, background="#0B0B12")
    bg(t, "#0B0B12")
    t.photo(t.track("video", "Artista"), "h-concert-03", 0, 6.0, Box(960, 0, 960, 1080), kb(6.0, 1.08, 1.0),
            label="Foto del artista", effects=[effect("duotone", shadowColor="#120A2A", highlightColor="#FF3CAC",
                                                      contrast=0.6)])
    t.solid(t.track("shape", "Fundido"), "#0B0B12", 0, 6.0, Box(940, 0, 400, 1080),
            layers=[gradient([(0, "#0B0B12", 1.0), (1, "#0B0B12", 0.0)], angle=0), no_stroke()])
    rng = random.Random(28)
    for i in range(36):
        tr = t.track("shape", "Ecualizador") if i % 9 == 0 else tr
        x = 40 + i * 52
        pts = [(0, {"sy": 0.1})]
        at = 0.0
        while at < 5.8:
            at += rng.uniform(0.12, 0.3)
            pts.append((at, {"sy": rng.uniform(0.15, 1.0)}, "smooth"))
        h = 240
        t.solid(tr, "#FF3CAC", 0.2, 5.8, Box(x, 1080 - h, 36, h), [(p[0], {**p[1], "dy": h / 2 * (1 - p[1]["sy"])}) +
                tuple(p[2:]) for p in pts],
                layers=[gradient([(0, "#784BA0"), (1, "#FF3CAC")], angle=90), no_stroke()], alpha=0.9)
    label(t, t.track("text", "Antetítulo"), "NUEVO SENCILLO", 0.8, 5.2, Box(120, 250, 900, 70), "Montserrat", 40,
          "#FF3CAC", weight=800, spacing=12, align="left", anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Artista"), "Luna Vega", 1.1, 4.9, Box(110, 320, 1000, 200), "Bebas Neue", 210,
          "#FFFFFF", weight=400, align="left", spacing=4, anim_in=tanim("slide-up", duration=0.5, unit="character",
          stagger=0.04), name="Artista")
    label(t, t.track("text", "Canción"), "«Ciudad de cristal»", 1.6, 4.4, Box(120, 520, 900, 90), "Montserrat", 56,
          "#D9D3FF", weight=500, italic=True, align="left", anim_in=tanim("fade", duration=0.5), name="Canción")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.5 * k for k in range(2, 12, 2)], 0.25, 0.25)})],
             name="Pulso")
    song(t, "electro", 1)
    return t


# 29 ----------------------------------------------------------------------------------------------

def intro_fitness():
    t = wide("h-intro-fitness", "Intro fitness", "Fitness intro", "intro", 5.0, order=2028,
             tags=["fitness", "gym", "entrenamiento", "intro", "motivación", "deporte"], thumb_at=3.6, background="#000000")
    slides(t, ["h-fitness-03", "h-fitness-01", "h-fitness-02", "h-fitness-05"], 0.0, 0.5, transition=None,
           kb_amount=0.15, effects_fn=lambda i: [effect("color.basic", saturation=-0.8, contrast=0.4)])
    photo_bg(t, "h-fitness-03", 2.0, 3.0, s1=1.08, label="Foto principal", reuse="p1",
             effects=[effect("color.basic", saturation=-0.6, contrast=0.4)])
    t.solid(t.track("shape", "Franja"), "#E10600", 2.0, 3.0, Box(-200, 0, 900, 1080),
            [(0, {"dx": -1100}, "out"), (0.35, {})], rotation=keys([(0, 10)]), alpha=0.92)
    label(t, t.track("text", "Título"), "ENTRENA DURO", 2.1, 2.9, Box(60, 260, 900, 440), "Anton", 190, "#FFFFFF",
          weight=400, line=0.95, align="left", anim_in=tanim("slide-right", duration=0.3, unit="word", stagger=0.12),
          name="Título")
    label(t, t.track("text", "Sub"), "DÍA 1 DE 30", 2.6, 2.4, Box(70, 740, 700, 90), "Barlow Condensed", 70, "#111111",
          weight=800, spacing=6, align="left", box_bg=("#FFFFFF", 1.0), box_pad=14, anim_in=tanim("pop", duration=0.3),
          name="Reto")
    t.adjust([effect("beat_shake", animated={"amount": spike([0.0, 0.5, 1.0, 1.5, 2.0], 0.7, 0.18)}),
              effect("strobe_flash", animated={"flash": spike([2.0], 0.8, 0.2)})], name="Golpe")
    song(t, "epic", 6)
    return t


# 30 ----------------------------------------------------------------------------------------------

def intro_ninos():
    t = wide("h-intro-ninos", "Intro infantil", "Kids intro", "intro", 6.0, order=2029,
             tags=["niños", "infantil", "colores", "intro", "educativo", "juegos"], thumb_at=3.8, background="#BDE6FF")
    bg_gradient(t, [(0, "#A7DCFF"), (1, "#E6F6FF")], angle=90)
    for i, (x, y, s) in enumerate([(300, 200, 360), (1500, 160, 420), (1000, 320, 260), (1750, 520, 280)]):
        t.solid(t.track("shape", "Nube"), "#FFFFFF", 0, 6.0, centered(x, y, s, s * 0.6),
                [(0, {"dx": -40}, "linear"), (6.0, {"dx": 60})], kind="cloud",
                layers=[shadow("#7FB3D5", 0, 8, 16, 0.3), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Colina"), "#7ED957", 0, 6.0, centered(500, 1180, 1600, 600), kind="ellipse")
    t.solid(t.track("shape", "Colina"), "#5CC93C", 0, 6.0, centered(1500, 1220, 1700, 640), kind="ellipse")
    rng = random.Random(30)
    for k in range(12):
        x = rng.uniform(100, 1820)
        s = rng.uniform(40, 90)
        ring(t, t.track("shape", "Burbuja"), "#FFFFFF", 4, 0.3 + k * 0.35, min(3.5, 5.7 - k * 0.35),
             centered(x, 1000, s, s), [(0, {}, "linear"), (3.5, {"dy": -900, "dx": rng.uniform(-80, 80)})], alpha=0.85)
    colours = ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93"]
    label(t, t.track("text", "Título"), "¡Aprendamos jugando!", 0.8, 5.2, Box(160, 360, 1600, 260), "Baloo 2", 150,
          "#FF595E", weight=800, layers=[shadow("#1982C4", 0, 8, 0, 0.9), stroke(8, "#FFFFFF"), fill("#FF595E")],
          anim_in=tanim("bounce", duration=0.6, unit="character", stagger=0.04),
          anim_loop=tanim("wave", amount=0.08, frequency=1.0), name="Título")
    label(t, t.track("text", "Sub"), "canciones · cuentos · colores", 1.8, 4.2, Box(460, 640, 1000, 80), "Baloo 2", 56,
          "#1982C4", weight=700, anim_in=tanim("pop", duration=0.4), name="Subtítulo")
    song(t, "fun", 4)
    return t


# --- Transitions: two slots (the shot before and after), the move hides the cut ------------------

def _ab(t, a: str, b: str, cut: float, la="Toma anterior", lb="Toma siguiente", s1=1.06):
    v = t.track("video", "Tomas")
    ca = t.photo(v, a, 0, cut, t.full, kb(cut, 1.0, s1), label=la)
    cb = t.photo(v, b, cut, t.duration - cut, t.full, kb(t.duration - cut, s1, 1.0), label=lb)
    return v, ca, cb


def trans_barrido_color():
    t = wide("h-trans-barrido-color", "Barrido de color", "Colour sweep", "transition", 3.0, order=2030,
             tags=["transición", "barrido", "colores", "cortinilla", "dinámica"], thumb_at=1.0)
    _ab(t, "h-city-02", "h-beach-05", 1.5)
    panels(t, ["#FF5A5F", "#FFC43D", "#1B9AAA"], 0.9, "left", length=0.45, hold=0.1, stagger=0.09, angle=0)
    song(t, "upbeat", 2)
    return t


def trans_circulo():
    t = wide("h-trans-circulo", "Separador de círculo", "Circle separator", "transition", 4.0, order=2031,
             tags=["transición", "círculo", "capítulo", "separador", "título"], thumb_at=1.25)
    _ab(t, "h-cafe-01", "h-cafe-05", 2.0)
    c = t.track("shape", "Círculo")
    t.solid(c, "#2B2D42", 1.0, 2.0, centered(960, 540, 2300, 2300),
            [(0, {"s": 0.0}, "inout"), (0.55, {"s": 1.0}, "hold"), (1.45, {"s": 1.0}, "inout"), (2.0, {"s": 0.0})],
            kind="ellipse")
    label(t, t.track("text", "Título"), "Parte 2", 1.5, 1.0, Box(360, 420, 1200, 240), "DM Serif Display", 170,
          "#FFFFFF", weight=400, anim_in=tanim("rise", duration=0.3), anim_out=tanim("fade", duration=0.2),
          name="Título")
    song(t, "calm", 2)
    return t


def trans_persiana():
    t = wide("h-trans-persiana", "Persiana", "Blinds", "transition", 3.0, order=2032,
             tags=["transición", "persiana", "franjas", "cortinilla", "elegante"], thumb_at=1.02)
    _ab(t, "h-interior-03", "h-interior-04", 1.5)
    for i in range(8):
        t.solid(t.track("shape", "Lámina"), "#F4F1EA", 0.9 + i * 0.04, 1.2, Box(i * 240, 0, 240, 1080),
                [(0, {"sx": 0.0}, "inout"), (0.45, {}, "hold"), (0.65, {}, "inout"), (1.1, {"sx": 0.0})])
    song(t, "calm", 3)
    return t


def trans_glitch_corto():
    t = wide("h-trans-glitch-corto", "Golpe glitch", "Glitch hit", "transition", 2.0, order=2033,
             tags=["transición", "glitch", "rápida", "gaming", "digital"], thumb_at=1.0)
    _ab(t, "h-gaming-02", "h-gaming-05", 1.0)
    for i, (y, h) in enumerate([(180, 60), (420, 120), (700, 40), (860, 90)]):
        t.solid(t.track("shape", "Bloque"), ["#08F7FE", "#FF2E63", "#FFFFFF", "#08F7FE"][i], 0.85 + i * 0.03, 0.18,
                Box(0, y, 1920, h), [(0, {"dx": -300}), (0.09, {"dx": 260}), (0.18, {"dx": -80})], alpha=0.7)
    t.adjust([effect("digital_glitch", animated={"intensity": spike([0.8, 1.0], 1.0, 0.2)}, rgbAmount=24,
                     blockAmount=0.7),
              effect("rgb_split", animated={"amount": spike([0.9], 30, 0.35)})], name="Glitch")
    flash(t, 0.98, 0.12, peak=0.7)
    song(t, "electro", 0)
    return t


def trans_tinta():
    t = wide("h-trans-tinta", "Cortinilla de tinta", "Ink wipe", "transition", 3.0, order=2034,
             tags=["transición", "tinta", "artística", "manchas", "suave"], thumb_at=1.5)
    v, a, b = _ab(t, "h-spring-01", "h-spring-03", 1.5)
    t.transition(v, a, b, "ink_bleed", 1.2)
    for i, (x, y, s) in enumerate([(200, 150, 500), (1750, 950, 600), (1700, 120, 380), (180, 960, 420)]):
        t.solid(t.track("shape", "Tinta"), "#111827", 0.9 + i * 0.05, 1.2, centered(x, y, s, s),
                [(0, {"s": 0.0}, "out"), (0.6, {"s": 1.0}, "in"), (1.2, {"s": 0.0})], kind="cloud", alpha=0.9)
    song(t, "calm", 4)
    return t


def trans_capitulo_numero():
    t = wide("h-trans-capitulo-numero", "Número de capítulo", "Chapter number", "transition", 4.0, order=2035,
             tags=["capítulo", "transición", "número", "separador", "documental"], thumb_at=2.0)
    _ab(t, "h-desk-02", "h-desk-03", 2.0)
    p = t.track("shape", "Panel")
    t.solid(p, "#111111", 0.8, 2.4, t.full, [(0, {"dx": -1920}, "inout"), (0.5, {}, "hold"), (1.9, {}, "inout"),
                                              (2.4, {"dx": 1920})])
    label(t, t.track("text", "Número"), "02", 1.2, 1.6, Box(160, 220, 700, 640), "Bebas Neue", 560, "#FFD23F",
          weight=400, align="left", anim_in=tanim("slide-up", duration=0.4), anim_out=tanim("fade", duration=0.2),
          name="Número")
    label(t, t.track("text", "Título"), "El comienzo", 1.4, 1.4, Box(860, 420, 960, 200), "DM Serif Display", 130,
          "#FFFFFF", weight=400, align="left", anim_in=tanim("fade-up-char", duration=0.4, unit="character",
          stagger=0.02), anim_out=tanim("fade", duration=0.2), name="Título del capítulo")
    song(t, "cine", 3)
    return t


def trans_diagonal():
    t = wide("h-trans-diagonal", "Cortinilla diagonal", "Diagonal wipe", "transition", 3.0, order=2036,
             tags=["transición", "diagonal", "cortinilla", "moderna", "paneles"], thumb_at=1.12)
    _ab(t, "h-travel-01", "h-travel-07", 1.5)
    for i, (sx, c) in enumerate([(-1, "#0F172A"), (1, "#F97316")]):
        box = centered(960 + sx * 700, 540, 2000, 2400)
        t.solid(t.track("shape", "Panel"), c, 0.95, 1.1, box,
                [(0, {"dx": sx * 1700}, "inout"), (0.45, {}, "hold"), (0.65, {}, "inout"), (1.1, {"dx": sx * 1700})],
                rotation=keys([(0, 25)]))
    song(t, "upbeat", 5)
    return t


def trans_zoom_golpe():
    t = wide("h-trans-zoom-golpe", "Zoom con golpe", "Zoom punch", "transition", 2.0, order=2037,
             tags=["transición", "zoom", "golpe", "rápida", "energía"], thumb_at=0.92)
    v, a, b = _ab(t, "h-city-05", "h-city-06", 1.0)
    t.transition(v, a, b, "zoom_in", 0.4)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.85], 1.0, 0.4)}, blur=0.8)], name="Golpe")
    flash(t, 0.95, 0.15, peak=0.5)
    song(t, "electro", 1)
    return t


def trans_papel():
    t = wide("h-trans-papel", "Papel que se rasga", "Torn paper", "transition", 3.0, order=2038,
             tags=["transición", "papel", "rasgado", "collage", "creativa"], thumb_at=1.5)
    v, a, b = _ab(t, "h-kids-04", "h-kids-02", 1.5)
    t.transition(v, a, b, "torn_paper", 1.0)
    song(t, "fun", 1)
    return t


def trans_formas():
    t = wide("h-trans-formas", "Formas que llenan", "Shape fill", "transition", 3.0, order=2039,
             tags=["transición", "formas", "círculos", "colores", "divertida"], thumb_at=0.98)
    _ab(t, "h-birthday-02", "h-birthday-05", 1.5)
    for i, c in enumerate(["#FF5A5F", "#FFC43D", "#06D6A0", "#118AB2"]):
        t.solid(t.track("shape", "Forma"), c, 0.8 + i * 0.08, 1.4 - i * 0.08, centered(960, 540, 2300, 2300),
                [(0, {"s": 0.0}, "out"), (0.5, {"s": 1.0}, "hold"), (0.75 - i * 0.04, {"s": 1.0}, "in"),
                 (1.4 - i * 0.08, {"s": 0.0})], kind="ellipse")
    song(t, "fun", 2)
    return t


def trans_pelicula():
    t = wide("h-trans-pelicula", "Quemado de película", "Film burn", "transition", 3.0, order=2040,
             tags=["transición", "película", "quemado", "vintage", "cálida"], thumb_at=1.15)
    v, a, b = _ab(t, "h-autumn-01", "h-autumn-03", 1.5)
    t.transition(v, a, b, "dip_white", 0.8)
    burn = t.track("shape", "Quemado")
    t.solid(burn, "#FF7A1A", 0.7, 1.6, centered(1500, 300, 2200, 1800),
            [(0, {"s": 0.2}, "out"), (0.8, {"s": 1.0}, "in"), (1.6, {"s": 1.3})], kind="ellipse",
            layers=[gradient([(0, "#FFF2C0", 0.95), (0.4, "#FF7A1A", 0.8), (1, "#C41E00", 0.0)], angle=0), no_stroke()],
            opacity=keys([(0, 0.0), (0.6, 1.0, "smooth"), (1.6, 0.0)]))
    t.adjust([effect("stylize.film_grain", amount=0.3), effect("light_leak", intensity=0.6, hue=0.05, speed=2)],
             name="Película")
    song(t, "calm", 2)
    return t


def trans_mientras_tanto():
    t = wide("h-trans-mientras-tanto", "«Mientras tanto…»", "Meanwhile…", "transition", 4.0, order=2041,
             tags=["mientras tanto", "humor", "cómic", "transición", "meme"], thumb_at=2.0, background="#FFE600")
    _ab(t, "h-office-02", "h-pet-02", 1.0)
    card = t.track("shape", "Cartel")
    t.solid(card, "#FFE600", 1.0, 2.0, t.full)
    t.solid(t.track("shape", "Estallido"), "#FFFFFF", 1.0, 2.0, centered(960, 540, 2200, 1500), pop(0, 0.3),
            kind="burst", points=24, innerRatio=0.6, alpha=0.6)
    label(t, t.track("text", "Texto"), "Mientras tanto…", 1.05, 1.95, Box(160, 380, 1600, 300), "Bangers", 220,
          "#111111", weight=400, layers=[shadow("#FF2E63", 10, 10, 0, 1.0), fill("#111111")],
          anim_in=tanim("stamp", duration=0.3), name="Texto")
    song(t, "fun", 0)
    return t


# --- Countdowns ---------------------------------------------------------------------------------

def _count(t, track, values, t0, each, box, font, size, colour, layers=None, anim="pop", last_label="Número"):
    for i, v in enumerate(values):
        label(t, track, v, t0 + i * each, each, box, font, size, colour, weight=700 if font != "Bebas Neue" else 400,
              layers=layers, anim_in=tanim(anim, duration=min(0.35, each * 0.6)), editable=False)


def cuenta_10_neon():
    t = wide("h-cuenta-10-neon", "Cuenta de 10 neón", "Neon 10 countdown", "countdown", 11.5, order=2042,
             tags=["cuenta regresiva", "neón", "10 segundos", "inicio", "evento"], thumb_at=4.8, background="#06000F")
    bg_gradient(t, [(0, "#14002E"), (1, "#06000F")], angle=90)
    rings = t.track("shape", "Anillo")
    for i in range(10):  # a neon ring that shrinks and dims every second
        t.solid(rings, "#FF2EF7", 0.5 + i, 1.0, centered(960, 520, 560, 560),
                [(0, {"s": 1.15}, "out"), (1.0, {"s": 0.85})], kind="ellipse",
                layers=[hollow_fill(), dict(hollow_stroke("#FF2EF7", 26), id="halo", blur=18, opacity=0.8),
                        hollow_stroke("#FF2EF7", 10)],
                opacity=keys([(0, 1.0), (1.0, 0.2)]))
    nums = t.track("text", "Números")
    _count(t, nums, [str(10 - i) for i in range(10)], 0.5, 1.0, centered(960, 520, 560, 400), "Orbitron", 260,
           "#FFFFFF", layers=[glow("#08F7FE", 30, 0.9), stroke(4, "#08F7FE"), fill("#FFFFFF")])
    label(t, nums, "¡YA!", 10.5, 1.0, centered(960, 520, 1200, 400), "Orbitron", 280, "#FFFFFF", weight=900,
          layers=[glow("#FF2EF7", 30, 0.9), fill("#FFFFFF")], anim_in=tanim("zoom-in", duration=0.3), name="Final")
    label(t, t.track("text", "Arriba"), "EMPEZAMOS EN", 0.2, 10.3, Box(460, 120, 1000, 90), "Orbitron", 52, "#08F7FE",
          weight=700, spacing=10, anim_in=tanim("fade", duration=0.5), name="Texto de arriba")
    flash(t, 10.5, 0.4, "#FF2EF7", 0.6)
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.9)], name="Brillo")
    song(t, "electro", 0)
    return t


def cuenta_5_cine():
    t = wide("h-cuenta-5-cine", "Cuenta de cine antiguo", "Old film countdown", "countdown", 6.0, order=2043,
             tags=["cuenta regresiva", "cine", "película", "vintage", "líder"], thumb_at=2.3, background="#6E6A63")
    bg_gradient(t, [(0, "#8A857C"), (1, "#4D4A45")], angle=0)
    t.solid(t.track("shape", "Cruz"), "#2B2926", 0, 6.0, Box(0, 538, 1920, 4))
    t.solid(t.track("shape", "Cruz"), "#2B2926", 0, 6.0, Box(958, 0, 4, 1080))
    for r in (760, 640):
        ring(t, t.track("shape", "Círculo"), "#EDE8DD", 8, 0, 6.0, centered(960, 540, r, r))
    for i in range(5):
        t.solid(t.track("shape", "Barrido"), "#2B2926", 0.5 + i, 1.0, centered(960, 540, 6, 760),
                rotation=keys([(0, 0, "linear"), (1.0, 360)]), alpha=0.8)
    nums = t.track("text", "Números")
    _count(t, nums, ["5", "4", "3", "2", "1"], 0.5, 1.0, centered(960, 540, 600, 600), "Bebas Neue", 480, "#141311",
           anim="fade")
    t.adjust([effect("super8_film", intensity=0.8, grain=0.6, scratches=0.5, weave=0.3, flicker=0.4)], name="Película")
    flash(t, 5.5, 0.5, "#FFFFFF", 0.9)
    song(t, "classic", 1)
    return t


def cuenta_directo():
    t = wide("h-cuenta-directo", "Empezamos pronto", "Starting soon", "countdown", 12.0, order=2044,
             tags=["directo", "en vivo", "stream", "empezamos pronto", "cuenta regresiva"], thumb_at=5.4,
             background="#0E1020")
    bg(t, "#0E1020")
    for i, (c, x, y, s) in enumerate([("#6C63FF", 300, 260, 900), ("#FF6584", 1600, 800, 1000), ("#00D2FF", 1500, 180, 700)]):
        t.solid(t.track("shape", "Luz"), c, 0, 12.0, centered(x, y, s, s),
                [(0, {}, "smooth"), (6.0, {"dx": 140 * (-1) ** i, "dy": 80}, "smooth"), (12.0, {})], kind="ellipse",
                layers=[gradient([(0, c, 0.55), (1, c, 0.0)], angle=0), no_stroke()])
    rrect(t, t.track("shape", "Panel"), "#FFFFFF", 0.2, 11.8, centered(960, 540, 1100, 560), 40, pop(0, 0.5, 0.9),
          layers=[fill("#FFFFFF", 0.08), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 2,
                  "strokeAlign": "inside", "paint": {"kind": "solid", "color": "#40ffffff"}, "opacity": 1.0}])
    label(t, t.track("text", "Arriba"), "EL DIRECTO EMPIEZA EN", 0.4, 11.6, Box(460, 330, 1000, 80), "Outfit", 52,
          "#FFFFFF", weight=600, spacing=8, anim_in=tanim("fade", duration=0.6), name="Texto")
    nums = t.track("text", "Reloj")
    _count(t, nums, [f"00:{10 - i:02d}" for i in range(10)], 1.0, 1.0, centered(960, 560, 1000, 260), "Outfit", 220,
           "#FFFFFF", anim="fade")
    label(t, nums, "¡EN VIVO!", 11.0, 1.0, centered(960, 560, 1000, 260), "Outfit", 180, "#FF6584", weight=800,
          anim_in=tanim("pop", duration=0.3), name="Final")
    pill(t, t.track("shape", "Insignia"), "#FF2D55", 0.6, 11.4, centered(960, 760, 220, 60))
    label(t, t.track("text", "Insignia"), "● LIVE", 0.6, 11.4, centered(960, 760, 220, 60), "Outfit", 34, "#FFFFFF",
          weight=700, anim_loop=tanim("flicker", intensity=0.3, speed=2), editable=False)
    song(t, "electro", 2)
    return t


def cuenta_anio_nuevo():
    t = wide("h-cuenta-anio-nuevo", "Cuenta de Año Nuevo", "New Year countdown", "countdown", 12.5, order=2045,
             tags=["año nuevo", "cuenta regresiva", "fuegos artificiales", "fiesta", "medianoche"], thumb_at=11.3,
             background="#050814")
    photo_bg(t, "h-newyear-03", s1=1.08, label="Foto de fondo")
    shade_full(t, 0.5, colour="#050814")
    nums = t.track("text", "Números")
    _count(t, nums, [str(10 - i) for i in range(10)], 0.3, 1.0, centered(960, 520, 700, 500), "Playfair Display", 380,
           "#F5D98B", layers=[glow("#F5D98B", 24, 0.6), fill("#FFF4D6")], anim="zoom-out")
    rng = random.Random(45)
    for b in range(5):
        cx, cy = rng.uniform(300, 1620), rng.uniform(200, 520)
        c = rng.choice(["#FFD23F", "#FF5A5F", "#3EC1FF", "#FFFFFF", "#B26BFF"])
        tr = t.track("shape", "Fuego")
        for k in range(14):
            a = k / 14 * math.tau
            t.solid(tr, c, 10.3 + b * 0.25, 1.6, centered(cx, cy, 16, 16),
                    [(0, {}, "out"), (1.0, {"dx": math.cos(a) * 260, "dy": math.sin(a) * 260 + 60}, "linear"),
                     (1.6, {"dx": math.cos(a) * 290, "dy": math.sin(a) * 290 + 160})], kind="ellipse",
                    layers=[glow(c, 14, 0.9), fill(c), no_stroke()], opacity=keys([(0, 1.0), (1.6, 0.0)]))
    label(t, t.track("text", "Saludo"), "¡Feliz Año Nuevo!", 10.3, 2.2, Box(160, 300, 1600, 220), "Great Vibes", 200,
          "#FFFFFF", weight=400, layers=[glow("#F5D98B", 20, 0.7), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.6),
          name="Saludo")
    label(t, t.track("text", "Año"), "2027", 10.6, 1.9, Box(560, 540, 800, 260), "Playfair Display", 230, "#F5D98B",
          weight=800, layers=[glow("#F5D98B", 24, 0.7), fill("#F5D98B")], anim_in=tanim("pop", duration=0.4), name="Año")
    flash(t, 10.3, 0.5, peak=0.8)
    confetti(t, ["#F5D98B", "#FFFFFF", "#E8C27A"], 10.4, 2.1, seed=46, lanes=3, density=0.2)
    song(t, "epic", 3)
    return t


def cuenta_lanzamiento():
    t = wide("h-cuenta-lanzamiento", "Cuenta para lanzamiento", "Launch countdown", "countdown", 6.0, order=2046,
             tags=["lanzamiento", "producto", "3 2 1", "cuenta regresiva", "ya disponible"], thumb_at=4.6,
             background="#0A0A0A")
    bg(t, "#0A0A0A")
    nums = t.track("text", "Números")
    _count(t, nums, ["3", "2", "1"], 0.2, 0.8, centered(960, 540, 600, 600), "Montserrat", 460, "#FFFFFF", anim="zoom-out")
    spot = t.track("shape", "Foco")
    t.solid(spot, "#FFFFFF", 2.6, 3.4, centered(960, 520, 1300, 1300), pop(0, 0.6, 0.3), kind="ellipse",
            layers=[gradient([(0, "#FFFFFF", 0.35), (1, "#FFFFFF", 0.0)], angle=0), no_stroke()])
    t.photo(t.track("video", "Producto"), "h-product-04", 2.6, 3.4, centered(960, 470, 820, 520),
            [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"), (3.4, {"s": 1.05})], label="Foto del producto")
    label(t, t.track("text", "Texto"), "YA DISPONIBLE", 3.0, 3.0, Box(260, 780, 1400, 150), "Montserrat", 110,
          "#FFFFFF", weight=900, spacing=10, anim_in=tanim("rise", duration=0.4, unit="character", stagger=0.03),
          name="Texto")
    flash(t, 2.6, 0.35, peak=0.9)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.2, 1.0, 1.8], 0.5, 0.3)})], name="Golpe")
    song(t, "epic", 2)
    return t


def cuenta_dias_evento():
    t = wide("h-cuenta-dias-evento", "Faltan X días", "Days to go", "countdown", 6.0, order=2047,
             tags=["faltan días", "evento", "cuenta regresiva", "boda", "viaje", "calendario"], thumb_at=3.8)
    photo_bg(t, "h-travel-05", s1=1.08, label="Foto de fondo")
    shade_full(t, 0.4)
    for i, (txt, w) in enumerate([("FALTAN", 520), ("07", 380), ("DÍAS", 440)]):
        x = [340, 960, 1540][i]
        box = centered(x, 520, w, 300)
        t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", 0.4 + i * 0.3, 5.6 - i * 0.3, box,
                [(0, {"dy": -700}, "back"), (0.55, {})], radius=24, kind="rounded-rectangle",
                layers=[shadow("#000000", 0, 16, 30, 0.45), fill("#FFFFFF"), no_stroke()])
        t.solid(t.track("shape", "Pliegue"), "#E5E5E5", 0.4 + i * 0.3, 5.6 - i * 0.3, Box(box.x, 517, box.w, 6),
                [(0, {"dy": -700}, "back"), (0.55, {})])
        label(t, t.track("text", "Tarjeta"), txt, 0.4 + i * 0.3, 5.6 - i * 0.3, box, "Bebas Neue",
              200 if i == 1 else 120, "#E63946" if i == 1 else "#1D3557", weight=400,
              motion=[(0, {"dy": -700}, "back"), (0.55, {})], name=["Antes", "Número de días", "Después"][i])
    label(t, t.track("text", "Evento"), "para nuestro gran viaje", 1.6, 4.4, Box(360, 760, 1200, 100), "Kaushan Script",
          84, "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 4, 12, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.6), name="Evento")
    song(t, "upbeat", 7)
    return t


def cuenta_minimal():
    t = wide("h-cuenta-minimal", "Cuenta minimalista", "Minimal countdown", "countdown", 6.0, order=2048,
             tags=["cuenta regresiva", "minimal", "limpio", "presentación", "inicio"], thumb_at=2.2, background="#F7F7F5")
    bg(t, "#F7F7F5")
    nums = t.track("text", "Números")
    _count(t, nums, ["5", "4", "3", "2", "1"], 0.3, 1.0, centered(960, 500, 600, 600), "Raleway", 420, "#111111",
           anim="blur-in")
    for i in range(5):
        line(t, t.track("shape", "Progreso"), "#111111", 0.3 + i, 1.0, Box(660, 840, 600, 4), length=1.0, ease="linear")
    t.solid(t.track("shape", "Base"), "#D9D9D6", 0, 6.0, Box(660, 840, 600, 4))
    label(t, t.track("text", "Final"), "comenzamos", 5.3, 0.7, Box(460, 440, 1000, 160), "Raleway", 110, "#111111",
          weight=300, spacing=10, anim_in=tanim("fade", duration=0.3), name="Final")
    song(t, "calm", 4)
    return t


def cuenta_deportes():
    t = wide("h-cuenta-deportes", "Cuenta de partido", "Match countdown", "countdown", 12.0, order=2049,
             tags=["partido", "fútbol", "cuenta regresiva", "deportes", "marcador"], thumb_at=5.4)
    photo_bg(t, "h-soccer-01", s1=1.06, label="Foto del estadio")
    shade_full(t, 0.5, colour="#06140A")
    board = t.track("shape", "Marcador")
    rrect(t, board, "#0B0B0B", 0.2, 11.8, centered(960, 320, 1300, 200), 20, pop(0, 0.4, 0.8),
          layers=[shadow("#000000", 0, 10, 24, 0.5), fill("#0B0B0B", 0.92), no_stroke()])
    t.solid(t.track("shape", "Equipo"), "#E10600", 0.3, 11.7, Box(330, 240, 420, 160), slide_in(dx=-200, length=0.4))
    t.solid(t.track("shape", "Equipo"), "#1E5BFF", 0.3, 11.7, Box(1170, 240, 420, 160), slide_in(dx=200, length=0.4))
    label(t, t.track("text", "Local"), "LOCAL", 0.5, 11.5, Box(330, 240, 420, 160), "Oswald", 80, "#FFFFFF",
          weight=700, spacing=4, anim_in=tanim("fade", duration=0.3), name="Equipo local")
    label(t, t.track("text", "Visita"), "VISITA", 0.5, 11.5, Box(1170, 240, 420, 160), "Oswald", 80, "#FFFFFF",
          weight=700, spacing=4, anim_in=tanim("fade", duration=0.3), name="Equipo visitante")
    label(t, t.track("text", "VS"), "VS", 0.5, 11.5, Box(750, 240, 420, 160), "Oswald", 90, "#FFD23F", weight=700,
          anim_in=tanim("pop", duration=0.3), name="VS", editable=False)
    label(t, t.track("text", "Texto"), "EL PARTIDO EMPIEZA EN", 0.8, 11.2, Box(460, 520, 1000, 80), "Oswald", 54,
          "#FFFFFF", weight=500, spacing=10, anim_in=tanim("fade", duration=0.4), name="Texto")
    nums = t.track("text", "Segundos")
    _count(t, nums, [f"{10 - i}" for i in range(10)], 1.0, 1.0, centered(960, 750, 600, 300), "Oswald", 260,
           "#FFD23F", anim="pop")
    label(t, nums, "¡VAMOS!", 11.0, 1.0, centered(960, 750, 1000, 300), "Oswald", 200, "#FFFFFF", weight=700,
          anim_in=tanim("zoom-in", duration=0.3), name="Final")
    song(t, "epic", 4)
    return t


TEMPLATES = [intro_barras_diagonales, intro_logo_destello, intro_cinematica_oscura, intro_tinta, intro_glitch,
             intro_vlog_polaroid, intro_minimal_linea, intro_gaming_neon, intro_podcast_ondas, intro_noticias,
             intro_deportes, intro_cocina, intro_tech, intro_viajes_mapa, intro_corporativa, intro_retro_80s,
             intro_documental, intro_boda, intro_colorida_formas, intro_zoom_fotos, intro_texto_gigante, intro_split,
             intro_tiza, intro_elegante_oro, intro_pop_comic, intro_papel, intro_suscriptores, intro_musica,
             intro_fitness, intro_ninos,
             trans_barrido_color, trans_circulo, trans_persiana, trans_glitch_corto, trans_tinta,
             trans_capitulo_numero, trans_diagonal, trans_zoom_golpe, trans_papel, trans_formas, trans_pelicula,
             trans_mientras_tanto,
             cuenta_10_neon, cuenta_5_cine, cuenta_directo, cuenta_anio_nuevo, cuenta_lanzamiento, cuenta_dias_evento,
             cuenta_minimal, cuenta_deportes]
