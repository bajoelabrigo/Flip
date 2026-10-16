"""Reel batch 6 (2026-10-16): 50 trend edits, 1080x1920. See BRIEF.md, «Las 400 nuevas».
Category reels (and collage, beforeafter, text where it fits); order 3000-3099.

120 BPM unless said otherwise: one beat = 0.5 s. Every design here is new next to the 133 already in Stock
(velocity, slow motion, dumps and memes are done again with other mechanics, not copies of those).
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels,
                 photo_bg, pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides,
                 song, spike, stroke, tall, tanim, vignette)

B = 0.5  # one beat


def _beats(start: float, n: int, every: float = B) -> list[float]:
    return [start + k * every for k in range(n)]


def _ramp(d: float) -> list:
    """A speed-ramp feel on a still: slow drift, a fast punch in on the beat, slow again."""
    return [(0, {"s": 1.0}, "linear"), (d * 0.45, {"s": 1.04}, "in"), (d * 0.6, {"s": 1.22}, "out"), (d, {"s": 1.26})]


# 1 -----------------------------------------------------------------------------------------------

def velocity_suave():
    t = tall("r-velocity-suave", "Velocity suave", "Smooth velocity", "reels", 9.0, order=3000,
             tags=["velocity", "rampa de velocidad", "suave", "tendencia", "capcut"], thumb_at=4.4)
    samples = ["fashion-02", "outfit-03", "outfit-04", "portrait-07", "fashion-04", "selfie-02"]
    slides(t, samples, 0.0, 1.5, transition=None, motion_fn=lambda i, d: _ramp(d),
           effects_fn=lambda i: [effect("color.basic", contrast=0.15, saturation=0.1, fade=0.06)])
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.7 + 1.5 * k for k in range(6)], 0.45, 0.35)}, blur=0.7),
              effect("strobe_flash", animated={"flash": spike([1.5 * k for k in range(1, 6)], 0.4, 0.15)}, tint=0.0)],
             name="Rampa")
    label(t, t.track("text", "Texto"), "vibes ✧", 0.2, 8.8, Box(90, 1620, 900, 160), "Sacramento", 140, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 4, 14, 0.5), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.8),
          name="Texto")
    song(t, "electro", 2, 0.85)
    return t


# 2 -----------------------------------------------------------------------------------------------

def velocity_duro():
    t = tall("r-velocity-duro", "Velocity duro", "Hard velocity", "reels", 8.0, order=3001,
             tags=["velocity", "rampa", "duro", "temblor", "edit", "tendencia"], thumb_at=3.6, background="#000000")
    samples = ["night-01", "skate-01", "night-03", "city-04", "skate-03", "night-04", "concert-03", "night-02"]
    slides(t, samples, 0.0, 1.0, transition=None, motion_fn=lambda i, d: _ramp(d),
           effects_fn=lambda i: [effect("color.basic", contrast=0.4, saturation=-0.25)])
    hits = [0.5 + k for k in range(8)]
    t.adjust([effect("zoom_pulse", animated={"punch": spike(hits, 0.75, 0.3)}, blur=0.9),
              effect("beat_shake", animated={"amount": spike(hits, 0.7, 0.25)}, rotation=0.5),
              effect("rgb_split", animated={"amount": spike(hits, 18, 0.2)})], name="Golpes")
    bars = t.track("shape", "Barras")
    for k, at in enumerate(hits):
        t.solid(bars, "#000000", at - 0.04, 0.12, Box(0, 0, 1080, 1920), opacity=keys([(0, 1.0)]))
    song(t, "electro", 0, 0.9)
    return t


# 3 -----------------------------------------------------------------------------------------------

def slowmo_destello():
    t = tall("r-slowmo-destello", "Cámara lenta con destello", "Slow motion flare", "reels", 10.0, order=3002,
             tags=["cámara lenta", "slow motion", "destello", "sol", "cinemático"], thumb_at=5.2)
    slides(t, ["sunset-01", "summer-04", "beach-05"], 0.0, 3.3, transition="blur_dissolve", tdur=0.8, kb_amount=0.07,
           effects_fn=lambda i: [effect("color.basic", temperature=0.25, highlights=-0.2, fade=0.08)])
    for k, at in enumerate((1.4, 4.6, 7.8)):
        t.solid(t.track("shape", "Destello"), "#FFE8C2", at, 1.6, centered(540, 700, 2400, 26),
                [(0, {"dx": -1400}, "inout"), (1.6, {"dx": 1400})], rotation=keys([(0, -18)]),
                layers=[glow("#FFB347", 40, 0.9), fill("#FFF6E5", 0.9), no_stroke()], opacity=keys([(0, 0.0), (0.4, 1.0, "smooth"),
                                                                                                   (1.2, 1.0), (1.6, 0.0)]))
    label(t, t.track("text", "Letra"), "y el tiempo se detuvo", 1.0, 8.6, Box(90, 1400, 900, 260), "Cormorant Garamond", 96,
          "#FFFFFF", weight=500, italic=True, layers=[shadow("#000000", 0, 4, 16, 0.5), fill("#FFFFFF")],
          anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.25, blur=10), name="Frase")
    t.adjust([effect("bloom_glow", threshold=0.65, intensity=0.8, blurRadius=14),
              effect("light_leak", intensity=0.4, hue=0.08, speed=0.6)], name="Luz")
    song(t, "cine", 2, 0.85)
    return t


# 4 -----------------------------------------------------------------------------------------------

def pareja_ritmo():
    t = tall("r-pareja-ritmo", "Montaje de pareja al ritmo", "Couple montage on the beat", "reels", 10.0, order=3003,
             tags=["pareja", "novios", "montaje", "ritmo", "amor", "tendencia"], thumb_at=6.3, background="#FFE3EA")
    bg(t, "#FFE3EA")
    samples = ["couple-01", "couple-03", "couple-05", "couple-02", "couple-07", "couple-04", "couple-06", "couple-08"]
    photos = t.track("video", "Fotos")
    for i, s in enumerate(samples):
        at = 0.5 + i * 1.0
        d = 10.0 - at if i == len(samples) - 1 else 1.0
        t.photo(photos, s, at, d, centered(540, 900, 860, 1240), [(0, {"s": 1.15}, "snap"), (0.3, {}, "linear"),
                                                                  (d, {"s": 1.04})], label=f"Foto {i + 1}")
    host = t.tracks[-1]
    for clip in host.clips:
        t.mask(host, clip, "heart")
    hearts = t.track("shape", "Corazones")
    rng = random.Random(3003)
    for k in range(16):
        at = 0.5 + k * 0.5
        s = rng.uniform(50, 110)
        t.solid(hearts, "#FF4D6D", at, 0.5, centered(rng.uniform(80, 1000), rng.uniform(300, 1650), s, s),
                [(0, {"s": 0.0}, "back"), (0.25, {}, "linear"), (0.5, {"dy": -60})], kind="heart",
                opacity=keys([(0, 1.0), (0.5, 0.0)]))
    label(t, t.track("text", "Nombres"), "tú y yo", 0.2, 9.8, Box(90, 1600, 900, 180), "Pacifico", 130, "#C9184A",
          weight=400, anim_in=tanim("pop", duration=0.4), name="Texto")
    song(t, "upbeat", 1, 0.85)
    return t


# 5 -----------------------------------------------------------------------------------------------

def pareja_lento():
    t = tall("r-pareja-lento", "Montaje de pareja lento", "Slow couple montage", "reels", 12.0, order=3004,
             tags=["pareja", "romántico", "lento", "película", "amor", "recuerdos"], thumb_at=7.0, background="#000000")
    slides(t, ["couple-02", "couple-06", "couple-08", "couple-04"], 0.0, 3.0, transition="crossfade", tdur=1.0,
           kb_amount=0.06, effects_fn=lambda i: [effect("color.basic", fade=0.15, temperature=0.1, saturation=-0.1)])
    letterbox(t, 1.0)
    label(t, t.track("text", "Texto"), "contigo todo es más bonito", 1.5, 10.2, Box(90, 1500, 900, 200), "Special Elite",
          60, "#F5EDE0", weight=400, anim_in=tanim("typewriter", duration=2.0, unit="character"), name="Texto")
    label(t, t.track("text", "Fecha"), "VERANO · 2026", 0.6, 11.0, Box(90, 300, 900, 70), "Special Elite", 40, "#F5EDE0",
          weight=400, spacing=8, anim_in=tanim("fade", duration=0.8), name="Fecha")
    grain(t, 0.3, 1.8)
    vignette(t, 0.5)
    song(t, "romantic", 0, 0.85)
    return t


# 6 -----------------------------------------------------------------------------------------------

def flash_camara():
    t = tall("r-flash-camara", "Flashes de paparazzi", "Paparazzi flashes", "reels", 8.0, order=3005,
             tags=["flash", "paparazzi", "famosa", "alfombra roja", "moda", "tendencia"], thumb_at=3.9, background="#000000")
    samples = ["fashion-01", "portrait-08", "portrait-02", "fashion-03", "outfit-01", "portrait-06"]
    slides(t, samples, 0.0, 1.0, transition=None, kb_amount=0.06, motion_fn=lambda i, d: [(0, {"s": 1.08}, "out"),
                                                                                        (0.3, {"s": 1.0}, "linear"),
                                                                                        (d, {"s": 1.03})])
    photo_bg(t, "fashion-01", 6.0, 2.0, s1=1.05, label="Foto final", reuse="p1")
    rng = random.Random(3005)
    fl = t.track("shape", "Flashes")
    times = sorted(rng.uniform(0.1, 7.6) for _ in range(22))
    for at in times:
        t.solid(fl, "#FFFFFF", at, 0.12, Box(0, 0, 1080, 1920), opacity=keys([(0, rng.uniform(0.5, 0.9), "out"), (0.12, 0.0)]))
    bursts = t.track("shape", "Destellos")
    for at in times[::2]:
        s = rng.uniform(160, 300)
        t.solid(bursts, "#FFFFFF", at, 0.18, centered(rng.uniform(100, 980), rng.uniform(200, 1700), s, s), kind="star",
                points=4, innerRatio=0.15, layers=[glow("#FFFFFF", 30, 1.0), fill("#FFFFFF"), no_stroke()],
                opacity=keys([(0, 1.0), (0.18, 0.0)]))
    label(t, t.track("text", "Texto"), "main character energy", 6.1, 1.9, Box(60, 1520, 960, 200), "Bodoni Moda", 84,
          "#FFFFFF", weight=700, italic=True, layers=[shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=0.5), name="Texto")
    song(t, "electro", 1, 0.85)
    return t


# 7 -----------------------------------------------------------------------------------------------

def modo_bestia():
    t = tall("r-modo-bestia", "Modo bestia", "Beast mode", "reels", 8.0, order=3006,
             tags=["gym", "modo bestia", "entrenamiento", "motivación", "fitness"], thumb_at=4.25, background="#000000")
    samples = ["gym-01", "dance-02", "gym-05", "gym-02", "gym-06", "gym-04", "sport-04", "gym-01"]
    slides(t, samples[:7], 0.0, 1.0, transition=None, kb_amount=0.12,
           effects_fn=lambda i: [effect("color.basic", saturation=-1.0, contrast=0.45)])
    photo_bg(t, "gym-01", 7.0, 1.0, s1=1.1, label="Foto final", reuse="p1",
             effects=[effect("color.basic", saturation=-1.0, contrast=0.45)])
    t.solid(t.track("shape", "Rojo"), "#E10600", 0, 8.0, opacity=keys([(0, 0.0, "hold"), (4.0, 0.35, "hold")]))
    label(t, t.track("text", "Título"), "MODO\nBESTIA", 4.0, 4.0, Box(40, 620, 1000, 680), "Anton", 300, "#FFFFFF",
          weight=400, line=0.9, layers=[shadow("#E10600", 12, 12, 0, 1.0), fill("#FFFFFF")],
          anim_in=tanim("stamp", duration=0.3), name="Título")
    hits = [k * B for k in range(16)]
    t.adjust([effect("beat_shake", animated={"amount": spike(hits, 0.6, 0.2)}),
              effect("strobe_flash", animated={"flash": spike([4.0, 6.0], 0.9, 0.2)})], name="Golpes")
    song(t, "epic", 1, 0.9)
    return t


# 8 -----------------------------------------------------------------------------------------------

def recuerdo_verano():
    t = tall("r-recuerdo-verano", "Recuerdo de verano", "Summer memory", "reels", 10.0, order=3007,
             tags=["verano", "playa", "recuerdos", "vacaciones", "polaroid", "sol"], thumb_at=6.0, background="#FFE8C7")
    bg_gradient(t, [(0, "#FFD7A8"), (1, "#FFF3E0")], angle=90)
    samples = ["summer-01", "beach-02", "summer-03", "beach-04", "summer-02"]
    for i, s in enumerate(samples):
        at = 0.2 + i * 1.8
        r = (-1) ** i * (4 + i)
        framed(t, s, at, 10.0 - at, centered(540, 860 + (i % 2) * 40, 780, 860),
               [(0, {"dx": 900 * (-1) ** i, "dy": -200}, "out"), (0.6, {})], border=26, bottom=180, colour="#FFFDF8",
               rotation=keys([(0, r * 2.5, "out"), (0.6, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Texto"), "verano 2026 ☼", 1.2, 8.8, Box(90, 1480, 900, 180), "Caveat", 130, "#3B2C20",
          weight=700, anim_in=tanim("typewriter", duration=1.0, unit="character"), rotation=keys([(0, -3)]), name="Texto")
    t.adjust([effect("light_leak", intensity=0.45, hue=0.08, speed=0.7), effect("stylize.film_grain", amount=0.15)],
             name="Luz")
    song(t, "upbeat", 0, 0.85)
    return t


# 9 -----------------------------------------------------------------------------------------------

def core_memory():
    t = tall("r-core-memory", "Recuerdos que brillan", "Core memories", "reels", 10.0, order=3008,
             tags=["recuerdos", "core memory", "brillo", "nostalgia", "esferas", "tendencia"], thumb_at=6.5,
             background="#0B0A1F")
    bg_gradient(t, [(0, "#1A1240"), (1, "#05040F")], angle=90)
    dots(t, ["#FFFFFF", "#B9A6FF"], 40, 0, 10.0, seed=3008, size=(4, 10), drift=30)
    orbs = [(300, 560, 360, "#FFD166"), (780, 820, 400, "#7BDFF2"), (360, 1180, 380, "#F7AEF8"), (760, 1480, 340, "#B2F7EF")]
    samples = ["friends-04", "family-03", "mother-05", "friends-10"]
    for i, ((x, y, s, c), smp) in enumerate(zip(orbs, samples)):
        at = 0.4 + i * 1.3
        mo = [(0, {"s": 0.0}, "back"), (0.7, {}, "smooth"), (4.0, {"dy": -30}, "smooth"), (10.0 - at, {"dy": 20})]
        t.solid(t.track("shape", "Halo"), c, at, 10.0 - at, centered(x, y, s * 1.35, s * 1.35), mo, kind="ellipse",
                layers=[gradient([(0, c, 0.65), (1, c, 0.0)], angle=0), no_stroke()])
        circle_photo(t, smp, at, 10.0 - at, centered(x, y, s, s), mo, ring_colour=c, ring_width=8, label=f"Recuerdo {i + 1}")
    label(t, t.track("text", "Texto"), "recuerdos que brillan", 0.4, 9.6, Box(60, 150, 960, 200), "Quicksand", 84, "#FFFFFF",
          weight=700, layers=[glow("#B9A6FF", 20, 0.8), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.8),
          name="Texto")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.9, blurRadius=16)], name="Brillo")
    song(t, "fantasy", 0, 0.8)
    return t


# 10 ----------------------------------------------------------------------------------------------

def dump_fecha():
    t = tall("r-dump-fecha", "Dump con fecha de cámara", "Dated photo dump", "reels", 9.0, order=3009,
             tags=["photo dump", "fecha", "cámara digital", "2000s", "recuerdos"], thumb_at=3.4, background="#000000")
    samples = ["friends-05", "cafe-03", "friends-07", "beach-06", "night-02", "friends-11", "selfie-03", "concert-02"]
    dates = ["10 03 '26", "22 04 '26", "05 06 '26", "18 07 '26", "02 08 '26", "14 09 '26", "30 09 '26", "16 10 '26"]
    slides(t, samples, 0.0, 1.0, transition=None, kb_amount=0.04,
           effects_fn=lambda i: [effect("color.basic", contrast=0.2, saturation=0.15), effect("bloom_glow", threshold=0.8,
                                                                                             intensity=0.4)])
    stamp = t.track("text", "Fecha")
    for i, d in enumerate(dates):
        label(t, stamp, d, i * 1.0, 1.0, Box(560, 1720, 470, 90), "VT323", 84, "#FF9F1C", weight=400, align="right",
              layers=[glow("#FF6A00", 10, 0.8), fill("#FFB347")], editable=False)
    flash(t, 0.0, 0.2, peak=0.8)
    t.adjust([effect("stylize.film_grain", amount=0.2), effect("strobe_flash", animated={"flash": spike(_beats(1.0, 7, 1.0),
                                                                                                     0.35, 0.12)})],
             name="Cámara")
    song(t, "upbeat", 4, 0.85)
    return t


# 11 ----------------------------------------------------------------------------------------------

def dump_finde():
    t = tall("r-dump-finde", "Dump de fin de semana", "Weekend dump", "collage", 8.0, order=3010,
             tags=["fin de semana", "photo dump", "cuadrícula", "amigos", "domingo"], thumb_at=6.5, background="#F4EFE6")
    bg(t, "#F4EFE6")
    g = 16
    cw, ch = (1080 - 3 * g) / 2, (1500 - 4 * g) / 3
    samples = ["friends-06", "coffee-02", "beach-01", "friends-09", "food-02", "sunset-02"]
    for i, s in enumerate(samples):
        r, c = divmod(i, 2)
        box = Box(g + c * (cw + g), 300 + g + r * (ch + g), cw, ch)
        at = 0.3 + i * B
        t.photo(t.track("video", f"Celda {i + 1}"), s, at, 8.0 - at, box,
                [(0, {"s": 1.25}, "snap"), (0.25, {}, "linear"), (8.0 - at, {"s": 1.03})], label=f"Foto {i + 1}",
                opacity=keys([(0, 0.0), (0.08, 1.0)]))
    label(t, t.track("text", "Título"), "fin de semana ☀", 0.2, 7.8, Box(60, 90, 960, 180), "Caveat", 140, "#2B2B2B",
          weight=700, anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Título")
    label(t, t.track("text", "Pie"), "sáb + dom", 3.5, 4.5, Box(60, 1840 - 70, 960, 70), "DM Sans", 40, "#8A8172",
          weight=600, spacing=6, anim_in=tanim("fade", duration=0.4), name="Pie")
    song(t, "upbeat", 2, 0.85)
    return t


# 12 ----------------------------------------------------------------------------------------------

def dump_viaje_mapa():
    t = tall("r-dump-viaje-mapa", "Dump de viaje con mapa", "Travel dump with map", "reels", 11.0, order=3011,
             tags=["viaje", "mapa", "ruta", "photo dump", "vacaciones"], thumb_at=5.5, background="#F3E9D6")
    bg_gradient(t, [(0, "#F6EEDD"), (1, "#E8D8B9")], angle=135)
    for k in range(5):
        outline(t, t.track("shape", "Mapa"), "#C9B38C", 3, 0, 3.0, centered(300 + (k % 2) * 480, 380 + k * 300, 520, 300),
                kind="ellipse", alpha=0.5)
    pts = [(220 + math.sin(u / 7 * 4) * 280 + u * 60, 1500 - u * 170) for u in range(8)]
    route = t.track("shape", "Ruta")
    for i, (x, y) in enumerate(pts):
        t.solid(route, "#D9480F", 0.2 + i * 0.25, 2.8 - i * 0.25, centered(x, y, 16, 16), pop(0, 0.2), kind="ellipse")
    for i, (x, y) in enumerate(pts[::2]):
        t.solid(t.track("shape", "Pin"), "#1F2A44", 0.4 + i * 0.5, 2.6 - i * 0.5, centered(x, y - 30, 50, 50), pop(0, 0.3),
                kind="ellipse")
    label(t, t.track("text", "Título"), "14 días · 4 ciudades", 0.3, 2.7, Box(60, 120, 960, 220), "DM Serif Display", 100,
          "#1F2A44", weight=400, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1), name="Título")
    slides(t, ["travel-01", "travel-04", "hike-01", "travel-08", "city-02", "travel-06",
               "beach-03", "travel-09"], 3.0, 1.0, transition="slide_up", tdur=0.25, kb_amount=0.06)
    labels = ["Montaña", "Pueblo", "Sendero", "Mirador", "Ciudad", "Mercado", "Costa", "Regreso"]
    tags_ = t.track("text", "Lugar")
    for i, l in enumerate(labels):
        label(t, tags_, "📍 " + l, 3.1 + i * 1.0, 0.9, Box(60, 1660, 960, 110), "Montserrat", 58, "#FFFFFF", weight=800,
              layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], anim_in=tanim("slide-up", duration=0.25),
              name=f"Lugar {i + 1}")
    song(t, "world", 0, 0.85)
    return t


# 13 ----------------------------------------------------------------------------------------------

def dia_perfecto():
    t = tall("r-dia-perfecto", "Mi día perfecto", "My perfect day", "reels", 10.0, order=3012,
             tags=["día perfecto", "rutina", "horas", "vlog", "día en mi vida"], thumb_at=5.4)
    samples = ["coffee-01", "reading-02", "garden-03", "food-03", "sunset-03"]
    times = ["08:00", "11:30", "15:00", "19:00", "21:30"]
    slides(t, samples, 0.0, 2.0, transition="crossfade", tdur=0.4, kb_amount=0.07)
    for i, (h, txt) in enumerate(zip(times, ["café lento", "un buen libro", "jardín", "cena rica", "atardecer"])):
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", i * 2.0 + 0.2, 1.7, Box(80, 1460, 620, 230), 30,
              pop(0, 0.4, 0.7), layers=[shadow("#000000", 0, 10, 24, 0.3), fill("#FFFFFF", 0.95), no_stroke()])
        label(t, t.track("text", "Hora"), h, i * 2.0 + 0.3, 1.6, Box(120, 1480, 560, 110), "DM Sans", 92, "#111111",
              weight=800, align="left", anim_in=tanim("fade", duration=0.3), name=f"Hora {i + 1}")
        label(t, t.track("text", "Actividad"), txt, i * 2.0 + 0.4, 1.5, Box(124, 1590, 560, 80), "DM Sans", 48, "#6B6B6B",
              weight=500, align="left", anim_in=tanim("fade", duration=0.3), name=f"Actividad {i + 1}")
    label(t, t.track("text", "Título"), "mi día perfecto", 0.2, 9.8, Box(60, 140, 960, 160), "Caveat", 120, "#FFFFFF",
          weight=700, layers=[shadow("#000000", 0, 4, 14, 0.5), fill("#FFFFFF")], anim_in=tanim("fade", duration=0.5),
          name="Título")
    song(t, "calm", 4, 0.85)
    return t


# 14 ----------------------------------------------------------------------------------------------

def zoom_golpe():
    t = tall("r-zoom-golpe", "Zoom de golpe", "Punch zoom", "reels", 8.0, order=3013,
             tags=["zoom", "golpe", "ritmo", "minimal", "edit"], thumb_at=3.1, background="#FFFFFF")
    bg(t, "#FFFFFF")
    samples = ["portrait-01", "man-02", "selfie-01", "portrait-04", "man-06", "selfie-04", "portrait-06", "friends-02"]
    for i, s in enumerate(samples):
        at = i * 1.0
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 1.0, Box(90, 260, 900, 1300),
                [(0, {"s": 1.0}, "hold"), (0.5, {"s": 1.0}, "snap"), (0.62, {"s": 1.18}, "out"), (1.0, {"s": 1.12})],
                label=f"Foto {i + 1}")
        if i == 0:
            ph = t.tracks[-1]
    label(t, t.track("text", "Texto"), "NO PARES", 0.2, 7.8, Box(60, 1620, 960, 160), "Archivo Black", 120, "#111111",
          weight=400, spacing=6, anim_in=tanim("pop", duration=0.3), name="Texto")
    t.adjust([effect("zoom_pulse", animated={"punch": spike(_beats(0.5, 8, 1.0), 0.5, 0.25)})], name="Golpe")
    song(t, "electro", 3, 0.85)
    return t


# 15 ----------------------------------------------------------------------------------------------

def sacudida_3d():
    t = tall("r-sacudida-3d", "Giro 3D al ritmo", "3D swing on the beat", "reels", 8.0, order=3014,
             tags=["3d", "giro", "ritmo", "tarjeta", "tendencia"], thumb_at=2.75, background="#1B1B2F")
    bg_gradient(t, [(0, "#2E2E5C"), (1, "#121226")], angle=90)
    samples = ["outfit-02", "fashion-03", "outfit-04", "portrait-06"]
    for i, s in enumerate(samples):
        at = i * 2.0
        box = centered(540, 900, 820, 1180)
        swing = keys([(0, -35 * (-1) ** i, "out"), (0.45, 0, "hold"), (1.0, 0, "out"), (1.25, 12 * (-1) ** i, "smooth"),
                      (1.6, 0)])
        rrect(t, t.track("shape", "Marco"), "#FFFFFF", at, 2.0, Box(box.x - 14, box.y - 14, box.w + 28, box.h + 28), 40,
              layers=[shadow("#000000", 0, 30, 60, 0.5), fill("#FFFFFF"), no_stroke()], rotationY=swing)
        t.photo(t.track("video", f"Foto {i + 1}"), s, at, 2.0, box, label=f"Foto {i + 1}", rotationY=swing)
    label(t, t.track("text", "Texto"), "fit check", 0.2, 7.8, Box(60, 1660, 960, 160), "Righteous", 110, "#FFFFFF",
          weight=400, anim_in=tanim("pop", duration=0.3), name="Texto")
    song(t, "electro", 1, 0.85)
    return t


# 16 ----------------------------------------------------------------------------------------------

def giro_camara():
    t = tall("r-giro-camara", "Giro de cámara", "Camera spin", "reels", 8.0, order=3015,
             tags=["giro", "transición", "spin", "viaje", "energía"], thumb_at=2.05, background="#000000")
    v = t.track("video", "Fotos")
    samples = ["travel-02", "city-04", "travel-07", "nature-03", "travel-10"]
    prev = None
    for i, s in enumerate(samples):
        at = i * 1.6
        d = 1.6 + (0.4 if i < len(samples) - 1 else 0)
        clip = t.photo(v, s, at, min(d, 8.0 - at), t.full, kb(d, 1.12, 1.0), label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, "spin", 0.4)
        prev = clip
    label(t, t.track("text", "Texto"), "a dar vueltas por el mundo", 0.3, 7.5, Box(60, 1500, 960, 260), "Montserrat", 80,
          "#FFFFFF", weight=900, layers=[shadow("#000000", 0, 6, 18, 0.6), fill("#FFFFFF")],
          anim_in=tanim("spin-in", duration=0.5, unit="word", stagger=0.1), name="Texto")
    song(t, "upbeat", 5, 0.85)
    return t


# 17 ----------------------------------------------------------------------------------------------

def cambio_ropa():
    t = tall("r-cambio-ropa", "Cambio de outfit al golpe", "Outfit change on the beat", "reels", 7.0, order=3016,
             tags=["outfit", "cambio de ropa", "moda", "transición", "ootd"], thumb_at=3.75, background="#EDE7E3")
    samples = ["outfit-01", "outfit-02", "outfit-03", "outfit-04", "fashion-01", "fashion-02"]
    slides(t, samples, 0.5, 1.0, transition=None, kb_amount=0.0)
    t.photo(t.track("video", "Inicio"), "outfit-01", 0, 0.5, t.full, label="Foto 1", reuse="p1")
    count = t.track("text", "Contador")
    for i in range(6):
        label(t, count, f"{i + 1}/6", 0.5 + i, 1.0, Box(760, 120, 260, 110), "DM Sans", 72, "#FFFFFF", weight=800,
              align="right", layers=[shadow("#000000", 0, 3, 12, 0.6), fill("#FFFFFF")], editable=False,
              anim_in=tanim("pop", duration=0.2))
    flash(t, 0.5, 0.15, peak=1.0)
    for k in range(1, 6):
        flash(t, 0.5 + k, 0.15, peak=1.0)
    label(t, t.track("text", "Texto"), "¿cuál eliges?", 0.2, 6.8, Box(60, 1650, 960, 150), "DM Sans", 92, "#FFFFFF",
          weight=800, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], anim_in=tanim("fade", duration=0.3),
          name="Pregunta")
    song(t, "electro", 0, 0.85)
    return t


# 18 ----------------------------------------------------------------------------------------------

def outfit_check():
    t = tall("r-outfit-check", "Outfit check con flechas", "Outfit check with arrows", "reels", 8.0, order=3017,
             tags=["outfit", "moda", "flechas", "detalles", "estilo"], thumb_at=5.5, background="#F5F0EB")
    photo_bg(t, "outfit-03", s1=1.05, label="Foto del outfit")
    # Each note: a dot on the garment, a line out to a pill label on the left or right edge.
    notes = [("camisa · segunda mano", 640, 700, 1.0, -1), ("jean recto", 440, 1150, 2.0, 1),
             ("botas de lluvia", 640, 1600, 3.0, -1)]
    for i, (txt, x, y, at, side) in enumerate(notes):
        lx = 60 if side < 0 else 560
        x0, x1 = (lx + 460, x) if side < 0 else (x, lx)
        line(t, t.track("shape", "Flecha"), "#FFFFFF", at, 8.0 - at, Box(x0, y - 3, x1 - x0, 6), grow="x", length=0.3,
             layers=[shadow("#000000", 0, 2, 6, 0.5), fill("#FFFFFF"), no_stroke()])
        t.solid(t.track("shape", "Punto"), "#FFFFFF", at, 8.0 - at, centered(x, y, 26, 26), pop(0, 0.3), kind="ellipse",
                layers=[shadow("#000000", 0, 2, 6, 0.5), fill("#FFFFFF"), no_stroke()])
        pill(t, t.track("shape", "Etiqueta"), "#FFFFFF", at + 0.2, 7.8 - at, Box(lx, y - 48, 460, 96), pop(0, 0.35),
             layers=[shadow("#000000", 0, 6, 16, 0.35), fill("#FFFFFF"), no_stroke()])
        label(t, t.track("text", "Etiqueta"), txt, at + 0.2, 7.8 - at, Box(lx, y - 48, 460, 96), "DM Sans", 40, "#111111",
              weight=700, name=f"Prenda {i + 1}")
    label(t, t.track("text", "Título"), "OUTFIT CHECK", 0.2, 7.8, Box(60, 140, 960, 140), "Archivo Black", 110, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 4, 14, 0.5), fill("#FFFFFF")], anim_in=tanim("slide-down", duration=0.3),
          name="Título")
    song(t, "jazz", 2, 0.8)
    return t


# 19 ----------------------------------------------------------------------------------------------

def ojo_pez():
    t = tall("r-ojo-pez", "Ojo de pez noventas", "90s fisheye", "reels", 8.0, order=3018,
             tags=["ojo de pez", "90s", "skate", "retro", "cámara"], thumb_at=3.4, background="#000000")
    bg(t, "#000000")
    host = t.track("video", "Fotos")
    samples = ["skate-01", "skate-03", "friends-08", "friends-04", "night-01", "friends-12"]
    for i, s in enumerate(samples):
        at = i * (8.0 / 6)
        d = 8.0 / 6
        clip = t.photo(host, s, at, d, centered(540, 960, 1080, 1080), [(0, {"s": 1.25}, "out"), (0.3, {"s": 1.08}, "linear"),
                                                                       (d, {"s": 1.0})], label=f"Foto {i + 1}",
                       effects=[effect("color.basic", contrast=0.35, saturation=0.3)])
        t.mask(host, clip, "ellipse", feather=40)
    label(t, t.track("text", "REC"), "● REC", 0.0, 8.0, Box(80, 300, 400, 80), "VT323", 72, "#FF2B2B", weight=400,
          align="left", anim_loop=tanim("flicker", intensity=0.6, speed=1.5), editable=False)
    label(t, t.track("text", "Tiempo"), "SP 0:00:12", 0.0, 8.0, Box(560, 300, 440, 80), "VT323", 72, "#FFFFFF", weight=400,
          align="right", editable=False)
    label(t, t.track("text", "Texto"), "los de siempre", 0.3, 7.6, Box(60, 1560, 960, 160), "Permanent Marker", 110,
          "#FFFFFF", weight=400, anim_in=tanim("stamp", duration=0.3), rotation=keys([(0, -4)]), name="Texto")
    t.adjust([effect("stylize.vhs", noise=24, chroma=4)], name="VHS")
    song(t, "jazz", 1, 0.85)
    return t


# 20 ----------------------------------------------------------------------------------------------

def grano_analogico():
    t = tall("r-grano-analogico", "Grano analógico", "Analog film", "reels", 10.0, order=3019,
             tags=["analógico", "película", "35 mm", "grano", "vintage", "aesthetic"], thumb_at=4.6, background="#111111")
    bg(t, "#111111")
    samples = ["city-01", "coffee-03", "portrait-05", "nature-06", "friends-03"]
    for i, s in enumerate(samples):
        at = i * 2.0
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 2.0, Box(60, 260, 960, 1280),
                [(0, {"s": 1.02}, "linear"), (2.0, {"s": 1.0})], label=f"Foto {i + 1}",
                effects=[effect("color.basic", fade=0.2, temperature=0.15, contrast=-0.05)])
        if i == 0:
            ph = t.tracks[-1]
    outline(t, t.track("shape", "Borde"), "#111111", 16, 0, 10.0, Box(60, 260, 960, 1280), radius=8)
    label(t, t.track("text", "Película"), "PORTRA 400  ·  36", 0, 10.0, Box(60, 1570, 960, 70), "Special Elite", 44,
          "#E0A33A", weight=400, align="left", editable=False)
    frame = t.track("text", "Número")
    for i in range(5):
        label(t, frame, f"{12 + i}A ▸", i * 2.0, 2.0, Box(60, 180, 960, 70), "Special Elite", 44, "#E0A33A", weight=400,
              align="right", editable=False)
    label(t, t.track("text", "Texto"), "días lentos", 0.4, 9.4, Box(60, 1660, 960, 160), "Cormorant Garamond", 110,
          "#F2EDE4", weight=500, italic=True, anim_in=tanim("fade", duration=0.8), name="Texto")
    t.adjust([effect("super8_film", intensity=0.5, grain=0.6, scratches=0.2, weave=0.15, flicker=0.15),
              effect("light_leak", intensity=0.3, hue=0.06, speed=0.5)], name="Película")
    song(t, "calm", 2, 0.8)
    return t


# 21 ----------------------------------------------------------------------------------------------

def camara_desechable():
    t = tall("r-camara-desechable", "Cámara desechable", "Disposable camera", "reels", 9.0, order=3020,
             tags=["cámara desechable", "flash", "fiesta", "boda", "rollo", "retro"], thumb_at=5.2, background="#1E1E1E")
    bg(t, "#1E1E1E")
    rrect(t, t.track("shape", "Cámara"), "#2B2B2B", 0, 9.0, Box(40, 180, 1000, 1360), 60,
          layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#2B2B2B"), no_stroke()])
    samples = ["wedding-02", "friends-01", "birthday-06", "wedding-05", "friends-10", "newyear-01"]
    for i, s in enumerate(samples):
        at = i * 1.5
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 1.5, Box(110, 250, 860, 1140),
                label=f"Foto {i + 1}", effects=[effect("color.basic", exposure=0.15, contrast=0.2, saturation=0.15)])
        if i == 0:
            ph = t.tracks[-1]
        flash(t, at, 0.25, peak=0.95)
    counter = t.track("text", "Contador")
    for i in range(6):
        label(t, counter, str(27 - i), i * 1.5, 1.5, centered(880, 1460, 160, 90), "VT323", 80, "#FFB347", weight=400,
              editable=False)
    label(t, t.track("text", "Texto"), "la boda de Ana", 0.3, 8.6, Box(60, 1620, 960, 160), "Caveat", 120, "#FFFFFF",
          weight=700, anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Texto")
    grain(t, 0.25)
    song(t, "upbeat", 6, 0.85)
    return t


# 22 ----------------------------------------------------------------------------------------------

def cuadros_4_3():
    t = tall("r-cuadros-4-3", "Cuadros 4:3", "4:3 frames", "reels", 10.0, order=3021,
             tags=["4:3", "cine", "cuadro", "minimal", "fotografía", "aesthetic"], thumb_at=4.6, background="#0D0D0D")
    bg(t, "#0D0D0D")
    samples = ["nature-02", "city-03", "coffee-04", "travel-05", "sunset-02"]
    caps = ["madrugada", "la ciudad despierta", "un café", "el camino", "y volver"]
    for i, (s, c) in enumerate(zip(samples, caps)):
        at = i * 2.0
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 2.0, centered(540, 860, 960, 720),
                [(0, {"s": 1.0}, "linear"), (2.0, {"s": 1.03})], label=f"Foto {i + 1}",
                effects=[effect("cinematic_grade", strength=0.55)])
        if i == 0:
            ph = t.tracks[-1]
        label(t, t.track("text", "Pie"), c, at + 0.2, 1.7, Box(60, 1260, 960, 90), "Cormorant Garamond", 64, "#E8E2D6",
              weight=500, italic=True, anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.3),
              name=f"Pie {i + 1}")
    label(t, t.track("text", "Número"), "N.º 07", 0.2, 9.8, Box(60, 380, 960, 60), "Montserrat", 32, "#8C8C8C", weight=600,
          spacing=12, anim_in=tanim("fade", duration=0.5), name="Número")
    song(t, "cine", 2, 0.8)
    return t


# 23 ----------------------------------------------------------------------------------------------

def contador_fotos():
    t = tall("r-contador-fotos", "Foto a foto con contador", "Photo counter", "reels", 6.0, order=3022,
             tags=["contador", "fotos", "ritmo", "rápido", "photo dump"], thumb_at=2.8, background="#111111")
    samples = ["friends-01", "beach-01", "food-01", "pet-01", "city-02", "concert-01", "friends-04", "nature-01",
               "selfie-02", "travel-03", "cafe-01", "sunset-04"]
    slides(t, samples, 0.0, B, transition=None, kb_amount=0.06)
    c = t.track("text", "Contador")
    for i in range(12):
        label(t, c, f"{i + 1:02d}", i * B, B, Box(60, 1640, 960, 200), "Bebas Neue", 200, "#FFFFFF", weight=400,
              align="left", layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], editable=False)
    label(t, t.track("text", "Total"), "/12", 0, 6.0, Box(260, 1690, 400, 150), "Bebas Neue", 120, "#FFFFFF", weight=400,
          align="left", layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF", 0.7)], editable=False)
    label(t, t.track("text", "Título"), "mis 12 favoritas", 0.0, 6.0, Box(60, 130, 960, 140), "DM Sans", 80, "#FFFFFF",
          weight=800, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], name="Título")
    song(t, "electro", 1, 0.85)
    return t


# 24 ----------------------------------------------------------------------------------------------

def en_otra_vida():
    t = tall("r-en-otra-vida", "En otra vida", "In another life", "reels", 10.0, order=3023,
             tags=["en otra vida", "soñador", "tendencia", "frase", "aesthetic"], thumb_at=5.8)
    slides(t, ["nature-05", "flowers-03", "spring-01", "hike-03"], 0.0, 2.5, transition="blur_dissolve", tdur=0.8,
           kb_amount=0.08, effects_fn=lambda i: [effect("color.basic", fade=0.12, saturation=-0.1, temperature=0.05),
                                                 effect("builtin.effects.gaussian_blur", u_blurRadius=1.5)])
    lines = ["en otra vida", "fui flor", "fui montaña", "y siempre fui feliz"]
    for i, l in enumerate(lines):
        label(t, t.track("text", "Verso"), l, 0.4 + i * 2.5, 2.2, Box(60, 820, 960, 280), "Cormorant Garamond", 120,
              "#FFFFFF", weight=500, italic=True, layers=[glow("#FFFFFF", 16, 0.4), fill("#FFFFFF")],
              anim_in=tanim("blur-in", duration=0.8, blur=18), anim_out=tanim("fade", duration=0.5), name=f"Verso {i + 1}")
    dots(t, ["#FFFFFF", "#FFE9F5"], 26, 0, 10.0, seed=3023, size=(6, 14), drift=120, alpha=0.8)
    song(t, "fantasy", 1, 0.8)
    return t


# 25 ----------------------------------------------------------------------------------------------

def yo_vs_yo():
    t = tall("r-yo-vs-yo", "Yo de niño vs. yo hoy", "Me then vs me now", "beforeafter", 8.0, order=3024,
             tags=["yo vs yo", "antes y ahora", "infancia", "crecer", "comparación"], thumb_at=4.0, background="#111111")
    for i, (s, txt, y, c) in enumerate([("kids-03", "yo a los 6", 0, "#FFD166"), ("portrait-03", "yo hoy", 960, "#06D6A0")]):
        at = 0.2 + i * 1.2
        extra = {"effects": [effect("color.basic", saturation=-0.6, fade=0.15)]} if i == 0 else {}
        t.photo(t.track("video", f"Foto {i + 1}"), s, at, 8.0 - at, Box(0, y, 1080, 955),
                [(0, {"dx": -1080 if i == 0 else 1080}, "out"), (0.5, {}, "linear"), (8.0 - at, {"s": 1.04})],
                label=f"Foto {i + 1}", **extra)
        pill(t, t.track("shape", "Etiqueta"), c, at + 0.4, 7.6 - at, Box(60, y + 800, 440, 100), pop(0, 0.35))
        label(t, t.track("text", "Etiqueta"), txt, at + 0.4, 7.6 - at, Box(60, y + 800, 440, 100), "DM Sans", 54, "#111111",
              weight=800, name=f"Etiqueta {i + 1}")
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0.2, 7.8, Box(0, 955, 1080, 10), [(0, {"sx": 0.0}, "out"), (0.5, {})])
    t.solid(t.track("shape", "VS"), "#FFFFFF", 1.6, 6.4, centered(540, 960, 180, 180), pop(0, 0.4), kind="ellipse")
    label(t, t.track("text", "VS"), "vs", 1.6, 6.4, centered(540, 960, 180, 180), "Archivo Black", 76, "#111111",
          weight=400, motion=pop(0, 0.4), editable=False)
    song(t, "fun", 3, 0.85)
    return t


# 26 ----------------------------------------------------------------------------------------------

def esta_soy_yo():
    t = tall("r-esta-soy-yo", "Esta soy yo", "This is me", "text", 10.0, order=3025,
             tags=["esta soy yo", "presentación", "sobre mí", "datos", "conóceme"], thumb_at=6.6, background="#FDF0E6")
    bg(t, "#FDF0E6")
    circle_photo(t, "selfie-01", 0.2, 9.8, centered(540, 470, 520, 520), pop(0, 0.5), ring_colour="#FF8C42", ring_width=12,
                 label="Tu foto")
    label(t, t.track("text", "Título"), "esta soy yo:", 0.5, 9.5, Box(60, 790, 960, 150), "Caveat", 130, "#2B2D42",
          weight=700, anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Título")
    facts = ["☕ fan del café", "📚 leo antes de dormir", "🌱 cuido 12 plantas", "✈ sueño con Japón", "🎧 música todo el día"]
    for i, f in enumerate(facts):
        at = 1.6 + i * 0.9
        label(t, t.track("text", "Dato"), f, at, 10.0 - at, Box(120, 980 + i * 150, 900, 110), "DM Sans", 62, "#2B2D42",
              weight=700, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.15), name=f"Dato {i + 1}")
    song(t, "fun", 2, 0.8)
    return t


# 27 ----------------------------------------------------------------------------------------------

def split_ritmo():
    t = tall("r-split-ritmo", "Pantalla dividida al ritmo", "Beat split screen", "collage", 8.0, order=3026,
             tags=["pantalla dividida", "ritmo", "dos fotos", "edit", "dinámico"], thumb_at=3.25, background="#000000")
    top = ["night-01", "concert-03", "city-04", "night-04"]
    bottom = ["dance-02", "friends-08", "dance-03", "friends-12"]
    for i in range(4):
        at = i * 2.0
        t.photo(t.track("video", "Arriba"), top[i], at, 2.0, Box(0, 0, 1080, 955),
                [(0, {"dx": 1080 * (-1) ** i}, "snap"), (0.3, {}, "linear"), (2.0, {"s": 1.05})], label=f"Arriba {i + 1}")
        t.photo(t.track("video", "Abajo"), bottom[i], at + B, 2.0 - B, Box(0, 965, 1080, 955),
                [(0, {"dx": -1080 * (-1) ** i}, "snap"), (0.3, {}, "linear"), (2.0 - B, {"s": 1.05})], label=f"Abajo {i + 1}")
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, 8.0, Box(0, 955, 1080, 10))
    t.adjust([effect("zoom_pulse", animated={"punch": spike(_beats(0.0, 16), 0.25, 0.2)})], name="Pulso")
    song(t, "electro", 2, 0.85)
    return t


# 28 ----------------------------------------------------------------------------------------------

def collage_respira():
    t = tall("r-collage-respira", "Collage que respira", "Breathing collage", "collage", 9.0, order=3027,
             tags=["collage", "fotos", "respira", "suave", "aesthetic"], thumb_at=6.0, background="#EFE9E1")
    bg(t, "#EFE9E1")
    cells = [Box(40, 160, 640, 760), Box(700, 160, 340, 360), Box(700, 540, 340, 380), Box(40, 940, 340, 420),
             Box(400, 940, 640, 420), Box(40, 1380, 1000, 380)]
    samples = ["flowers-02", "coffee-02", "reading-01", "garden-02", "spring-02", "sunset-02"]
    for i, (box, s) in enumerate(zip(cells, samples)):
        at = 0.2 + i * 0.25
        breathe = [(0, {"s": 0.0}, "out"), (0.5, {}, "smooth")]
        tt = 0.5
        while tt < 9.0 - at:
            tt += 1.5
            breathe.append((min(tt, 9.0 - at), {"s": 1.0 + 0.04 * ((len(breathe) + i) % 2)}, "smooth"))
        t.photo(t.track("video", f"Celda {i + 1}"), s, at, 9.0 - at, box, breathe, label=f"Foto {i + 1}")
    label(t, t.track("text", "Texto"), "slow living", 1.6, 7.4, Box(40, 1790, 1000, 110), "Cormorant Garamond", 84,
          "#5A4E44", weight=600, italic=True, anim_in=tanim("fade", duration=0.8), name="Texto")
    song(t, "calm", 1, 0.8)
    return t


# 29 ----------------------------------------------------------------------------------------------

def reflejo():
    t = tall("r-reflejo", "Reflejo en el agua", "Water reflection", "reels", 9.0, order=3028,
             tags=["reflejo", "espejo", "agua", "simetría", "aesthetic"], thumb_at=4.6, background="#0E1A24")
    bg(t, "#0E1A24")
    samples = ["sunset-01", "city-03", "nature-04"]
    for i, s in enumerate(samples):
        at = i * 3.0
        t.photo(t.track("video", "Arriba"), s, at, 3.0, Box(0, 0, 1080, 960), kb(3.0, 1.0, 1.06), label=f"Foto {i + 1}")
        t.photo(t.track("video", "Reflejo"), s, at, 3.0, Box(0, 960, 1080, 960), kb(3.0, 1.0, 1.06), label=f"Foto {i + 1}",
                reuse=f"p{i + 1}", flipV=True, opacity=keys([(0, 0.55)]),
                effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=3), effect("color.basic", exposure=-0.25,
                                                                                        saturation=-0.2)])
    t.solid(t.track("shape", "Agua"), "#0E1A24", 0, 9.0, Box(0, 960, 1080, 960),
            layers=[gradient([(0, "#0E1A24", 0.0), (1, "#0E1A24", 0.9)], angle=90), no_stroke()])
    label(t, t.track("text", "Texto"), "calma", 0.4, 8.4, Box(60, 1540, 960, 200), "Cormorant Garamond", 160, "#FFFFFF",
          weight=500, italic=True, spacing=10, anim_in=tanim("blur-in", duration=1.0), name="Texto")
    song(t, "calm", 0, 0.8)
    return t


# 30 ----------------------------------------------------------------------------------------------

def foto_rompe():
    t = tall("r-foto-rompe", "Foto que se rompe", "Shattering photos", "reels", 8.0, order=3029,
             tags=["romper", "cristal", "transición", "impacto", "edit"], thumb_at=2.05, background="#000000")
    v = t.track("video", "Fotos")
    samples = ["concert-04", "night-02", "night-03", "concert-01"]
    prev = None
    for i, s in enumerate(samples):
        at = i * 2.0
        d = 2.0 + (0.5 if i < len(samples) - 1 else 0)
        clip = t.photo(v, s, at, min(d, 8.0 - at), t.full, kb(d, 1.0, 1.08), label=f"Foto {i + 1}")
        if prev:
            t.transition(v, prev, clip, "voronoi_shatter", 0.5)
        prev = clip
    for at in (2.0, 4.0, 6.0):
        flash(t, at - 0.05, 0.15, peak=0.7)
    t.adjust([effect("beat_shake", animated={"amount": spike([2.0, 4.0, 6.0], 0.8, 0.3)})], name="Golpe")
    label(t, t.track("text", "Texto"), "rompe la rutina", 0.3, 7.5, Box(60, 1580, 960, 180), "Russo One", 104, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], anim_in=tanim("glitch-in", duration=0.4),
          name="Texto")
    song(t, "epic", 5, 0.85)
    return t


# 31 ----------------------------------------------------------------------------------------------

def luces_fiesta():
    t = tall("r-luces-fiesta", "Luces de fiesta", "Party lights", "reels", 8.0, order=3030,
             tags=["fiesta", "luces", "noche", "disco", "amigos", "baile"], thumb_at=3.6, background="#0A0014")
    samples = ["concert-02", "friends-10", "newyear-03", "dance-01", "concert-04", "friends-07", "newyear-05", "friends-12"]
    slides(t, samples, 0.0, 1.0, transition=None, kb_amount=0.06)
    rng = random.Random(3030)
    for k in range(16):
        c = ["#FF2EF7", "#08F7FE", "#FFE600", "#7CFF00"][k % 4]
        at = k * B
        t.solid(t.track("shape", "Luz"), c, at, B, centered(rng.uniform(100, 980), rng.uniform(200, 1700), 1200, 1200),
                kind="ellipse", blendMode="screen", layers=[gradient([(0, c, 0.55), (1, c, 0.0)], angle=0), no_stroke()],
                opacity=keys([(0, 1.0, "out"), (B, 0.2)]))
    label(t, t.track("text", "Texto"), "NOCHE DE FIESTA", 0.2, 7.8, Box(60, 1640, 960, 150), "Monoton", 92, "#FFFFFF",
          weight=400, layers=[glow("#FF2EF7", 24, 0.9), fill("#FFFFFF")], anim_loop=tanim("flicker", intensity=0.2, speed=4),
          name="Texto")
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.8)], name="Brillo")
    song(t, "electro", 0, 0.9)
    return t


# 32 ----------------------------------------------------------------------------------------------

def letra_sube():
    t = tall("r-letra-sube", "Letra que sube", "Scrolling lyrics", "text", 12.0, order=3031,
             tags=["letra", "canción", "karaoke", "lyrics", "música"], thumb_at=6.2, background="#2B1B3D")
    photo_bg(t, "music-03", s1=1.08, label="Foto de fondo", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=18),
                                                                       effect("color.basic", exposure=-0.4)])
    lines = ["y cuando todo calla", "te escucho en la radio", "bailando en la cocina", "como si fuera ayer",
             "no quiero despertar"]
    for i, l in enumerate(lines):
        at = i * 2.4
        d = min(4.8, 12.0 - at)
        label(t, t.track("text", "Verso"), l, at, d, Box(80, 1100, 920, 260), "Plus Jakarta Sans", 96, "#FFFFFF",
              weight=800, align="left", line=1.05,
              motion=[(0, {"dy": 0}, "inout"), (2.4, {"dy": -380}, "inout"), (d, {"dy": -760})],
              opacity=keys([(0, 1.0, "smooth"), (2.4, 0.35, "smooth"), (d, 0.0)]),
              anim_in=tanim("fade-up-char", duration=0.5, unit="word", stagger=0.12), name=f"Verso {i + 1}")
    rrect(t, t.track("shape", "Reproductor"), "#FFFFFF", 0, 12.0, Box(80, 1700, 920, 10), 5, alpha=0.3)
    rrect(t, t.track("shape", "Reproductor"), "#FFFFFF", 0, 12.0, Box(80, 1700, 920, 10), 5,
          [(0, {"sx": 0.0, "dx": -460}, "linear"), (12.0, {})])
    song(t, "romantic", 3, 0.85)
    return t


# 33 ----------------------------------------------------------------------------------------------

def si_te_ries():
    t = tall("r-si-te-ries", "Si te ríes pierdes", "Try not to laugh", "text", 10.0, order=3032,
             tags=["meme", "si te ríes pierdes", "humor", "reto", "divertido"], thumb_at=3.0, background="#FFE600")
    bg(t, "#FFE600")
    label(t, t.track("text", "Título"), "SI TE RÍES\nPIERDES", 0.1, 9.9, Box(40, 100, 1000, 380), "Luckiest Guy", 150,
          "#111111", weight=400, line=0.95, layers=[shadow("#FFFFFF", 0, 8, 0, 1.0), fill("#111111")],
          anim_in=tanim("stamp", duration=0.3), name="Título")
    rrect(t, t.track("shape", "Marco"), "#111111", 0.3, 9.7, Box(50, 520, 980, 1100), 40)
    t.photo(t.track("video", "Video"), "puppy-01", 0.4, 9.6, Box(70, 540, 940, 1060), kb(9.6, 1.0, 1.06), label="Tu video gracioso")
    rrect(t, t.track("shape", "Barra"), "#111111", 0.4, 9.6, Box(90, 1700, 900, 40), 20, alpha=0.2)
    rrect(t, t.track("shape", "Barra"), "#E10600", 0.4, 9.6, Box(90, 1700, 900, 40), 20,
          [(0, {}, "linear"), (9.6, {"sx": 0.0, "dx": -450})])
    label(t, t.track("text", "Emoji"), "😂", 0.6, 9.4, centered(900, 520, 220, 220), "Inter", 160, "#000000", weight=400,
          editable=False, motion=pop(0, 0.4), anim_loop=tanim("swing", angle=10, speed=1.2))
    song(t, "fun", 0, 0.85)
    return t


# 34 ----------------------------------------------------------------------------------------------

def nadie_yo():
    t = tall("r-nadie-yo", "«Nadie: / Yo:»", "Nobody: / Me:", "text", 7.0, order=3033,
             tags=["meme", "nadie yo", "humor", "relatable", "tendencia"], thumb_at=3.6, background="#FFFFFF")
    bg(t, "#FFFFFF")
    label(t, t.track("text", "Nadie"), "Nadie:", 0.2, 6.8, Box(70, 120, 940, 120), "Roboto", 80, "#111111", weight=700,
          align="left", anim_in=tanim("fade", duration=0.2), name="Línea 1")
    label(t, t.track("text", "Yo"), "Yo a las 2 a. m.: haciendo pan casero", 1.2, 5.8, Box(70, 250, 940, 260), "Roboto",
          80, "#111111", weight=700, align="left", line=1.15, anim_in=tanim("typewriter", duration=1.0, unit="character"),
          name="Línea 2")
    t.photo(t.track("video", "Video"), "bakery-02", 2.0, 5.0, Box(0, 560, 1080, 1360), kb(5.0, 1.0, 1.08),
            label="Tu video", opacity=keys([(0, 0.0), (0.2, 1.0)]))
    song(t, "fun", 1, 0.85)
    return t


# 35 ----------------------------------------------------------------------------------------------

def expectativa_realidad():
    t = tall("r-expectativa-realidad", "Expectativa vs. realidad", "Expectation vs reality", "beforeafter", 8.0,
             order=3034, tags=["expectativa", "realidad", "meme", "humor", "comparación"], thumb_at=5.0, background="#111111")
    for i, (s, txt, y, c) in enumerate([("cake-03", "EXPECTATIVA", 0, "#06D6A0"), ("cake-02", "REALIDAD", 965, "#EF476F")]):
        at = 0.2 if i == 0 else 2.5
        t.photo(t.track("video", f"Foto {i + 1}"), s, at, 8.0 - at, Box(0, y, 1080, 955), kb(8.0 - at, 1.0, 1.05),
                label=f"Foto {i + 1}")
        t.solid(t.track("shape", "Etiqueta"), c, at + 0.2, 7.8 - at, Box(0, y + 820, 1080, 120), slide_in(dx=-1080, length=0.3))
        label(t, t.track("text", "Etiqueta"), txt, at + 0.3, 7.7 - at, Box(0, y + 820, 1080, 120), "Archivo Black", 80,
              "#FFFFFF", weight=400, spacing=8, name=f"Etiqueta {i + 1}")
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, 8.0, Box(0, 955, 1080, 10))
    t.adjust([effect("beat_shake", animated={"amount": spike([2.5], 0.7, 0.3)})], name="Golpe")
    song(t, "fun", 3, 0.85)
    return t


# 36 ----------------------------------------------------------------------------------------------

def reaccion_esquina():
    t = tall("r-reaccion-esquina", "Reacción en la esquina", "Corner reaction", "reels", 10.0, order=3035,
             tags=["reacción", "pip", "react", "esquina", "comentario"], thumb_at=4.0, background="#000000")
    photo_bg(t, "concert-03", s1=1.06, label="Video principal")
    circle_photo(t, "selfie-03", 0.4, 9.6, centered(800, 1500, 380, 380), pop(0, 0.5), ring_colour="#FFFFFF", ring_width=10,
                 label="Tu reacción")
    for i, (e, at) in enumerate([("😮", 1.5), ("🔥", 3.5), ("😂", 5.5), ("❤️", 7.5)]):
        label(t, t.track("text", "Emoji"), e, at, 1.6, centered(640 + i * 40, 1260, 160, 160), "Inter", 110, "#000000",
              weight=400, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.3, {}, "linear"), (1.6, {"dy": -300})],
              opacity=keys([(0, 1.0, "hold"), (1.1, 1.0), (1.6, 0.0)]))
    label(t, t.track("text", "Texto"), "no puede ser 😳", 0.3, 9.4, Box(60, 180, 960, 140), "DM Sans", 84, "#FFFFFF",
          weight=800, box_bg=("#000000", 0.6), box_pad=20, box_radius=20, anim_in=tanim("pop", duration=0.3), name="Texto")
    song(t, "upbeat", 1, 0.8)
    return t


# 37 ----------------------------------------------------------------------------------------------

def antes_ahora():
    t = tall("r-antes-ahora", "Antes y ahora", "Then and now", "beforeafter", 8.0, order=3036,
             tags=["antes y ahora", "cambio", "comparación", "lugar", "tiempo"], thumb_at=3.0, background="#000000")
    t.photo(t.track("video", "Ahora"), "home-03", 0, 8.0, t.full, kb(8.0, 1.0, 1.05), label="Foto de ahora")
    host = t.track("video", "Antes")
    clip = t.photo(host, "home-01", 0, 8.0, t.full, kb(8.0, 1.0, 1.05), label="Foto de antes",
                   effects=[effect("stylize.sepia"), effect("color.basic", fade=0.2)])
    t.mask(host, clip, "rectangle", keyframes={"h": keys([(0, 1.0, "hold"), (2.0, 1.0, "inout"), (4.0, 0.0)]),
                                               "y": keys([(0, 0.5, "hold"), (2.0, 0.5, "inout"), (4.0, 0.0)])})
    xs = [(0, 1920, "hold"), (2.0, 1920, "inout"), (4.0, 0)]
    t.solid(t.track("shape", "Línea"), "#FFFFFF", 0, 8.0, Box(0, 0, 1080, 8),
            [(p[0], {"dy": p[1] - 4}) + tuple(p[2:]) for p in xs])
    label(t, t.track("text", "Antes"), "ANTES · 2015", 0.2, 3.8, Box(60, 150, 960, 120), "Montserrat", 70, "#FFFFFF",
          weight=900, spacing=6, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.3), name="Antes")
    label(t, t.track("text", "Ahora"), "AHORA · 2026", 4.0, 4.0, Box(60, 150, 960, 120), "Montserrat", 70, "#FFFFFF",
          weight=900, spacing=6, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.3), name="Ahora")
    song(t, "cine", 1, 0.8)
    return t


# 38 ----------------------------------------------------------------------------------------------

def ciudad_neon():
    t = tall("r-ciudad-neon", "Ciudad neón", "Neon city", "reels", 9.0, order=3037,
             tags=["ciudad", "noche", "neón", "cyberpunk", "urbano", "luces"], thumb_at=4.6, background="#0A0014")
    slides(t, ["night-04", "night-01", "city-01", "night-03"], 0.0, 2.25, transition="rgb_displacement", tdur=0.4,
           kb_amount=0.08, effects_fn=lambda i: [effect("duotone", strength=0.45, shadowColor="#120035",
                                                        highlightColor="#FF3CAC", contrast=0.6)])
    label(t, t.track("text", "Título"), "NOCHES\nDE CIUDAD", 0.4, 8.4, Box(60, 700, 960, 520), "Orbitron", 140, "#FFFFFF",
          weight=900, line=1.0, layers=[glow("#08F7FE", 30, 1.0), stroke(3, "#08F7FE"), fill("#FFFFFF")],
          anim_in=tanim("flicker-in", duration=0.8), anim_loop=tanim("flicker", intensity=0.15, speed=5), name="Título")
    t.adjust([effect("bloom_glow", threshold=0.5, intensity=1.0, blurRadius=16), effect("stylize.film_grain", amount=0.12)],
             name="Brillo")
    song(t, "electro", 3, 0.85)
    return t


# 39 ----------------------------------------------------------------------------------------------

def atardecer_cine():
    t = tall("r-atardecer-cine", "Atardecer cinemático", "Cinematic sunset", "reels", 10.0, order=3038,
             tags=["atardecer", "sunset", "cinemático", "frase", "dorado"], thumb_at=6.0, background="#000000")
    slides(t, ["sunset-03", "sunset-02", "sunset-04"], 0.0, 3.4, transition="crossfade", tdur=1.0, kb_amount=0.08,
           effects_fn=lambda i: [effect("cinematic_grade", strength=0.7, teal=0.6, orange=0.8)])
    letterbox(t, 1.2)
    label(t, t.track("text", "Frase"), "algunos días terminan\nmejor de lo que empezaron", 1.5, 8.0, Box(60, 1350, 960, 260),
          "Cormorant Garamond", 70, "#FFE8C7", weight=500, italic=True, line=1.15,
          anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.18), name="Frase")
    t.adjust([effect("light_leak", intensity=0.35, hue=0.06, speed=0.5)], name="Luz")
    song(t, "cine", 3, 0.85)
    return t


# 40 ----------------------------------------------------------------------------------------------

def lugar_feliz():
    t = tall("r-lugar-feliz", "Mi lugar feliz", "My happy place", "reels", 9.0, order=3039,
             tags=["lugar feliz", "naturaleza", "paz", "viaje", "aesthetic"], thumb_at=5.0, background="#E9F1E7")
    bg(t, "#E9F1E7")
    for i, s in enumerate(["hike-02", "garden-01", "nature-01"]):
        at = i * 3.0
        rrect(t, t.track("shape", "Marco"), "#FFFFFF", at, 3.0, Box(80, 220, 920, 1280), 60,
              layers=[shadow("#3A5A40", 0, 16, 40, 0.25), fill("#FFFFFF"), no_stroke()], opacity=keys([(0, 1.0)]))
        clip = t.photo(t.track("video", "Foto"), s, at, 3.0, Box(100, 240, 880, 1240), kb(3.0, 1.0, 1.06),
                       label=f"Foto {i + 1}", opacity=keys([(0, 0.0), (0.5, 1.0)]))
    label(t, t.track("text", "Título"), "mi lugar feliz", 0.3, 8.7, Box(60, 1560, 960, 180), "Courgette", 110, "#3A5A40",
          weight=400, anim_in=tanim("fade", duration=0.8), name="Título")
    label(t, t.track("text", "Lugar"), "📍 Valle Verde", 1.0, 8.0, Box(60, 1740, 960, 80), "DM Sans", 46, "#588157",
          weight=700, anim_in=tanim("fade", duration=0.6), name="Lugar")
    song(t, "calm", 3, 0.8)
    return t


# 41 ----------------------------------------------------------------------------------------------

def recorrido_ubicacion():
    t = tall("r-recorrido-ubicacion", "Recorrido con ubicaciones", "Places tour", "reels", 10.0, order=3040,
             tags=["recorrido", "ubicación", "ciudad", "guía", "lugares", "turismo"], thumb_at=4.6)
    places = [("city-02", "Mirador del puerto", "1"), ("restaurant-02", "Mercado central", "2"), ("coffee-04", "Café de la esquina", "3"),
              ("night-01", "Calle de los murales", "4"), ("sunset-01", "Playa al atardecer", "5")]
    for i, (s, name, n) in enumerate(places):
        at = i * 2.0
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 2.0, t.full, kb(2.0, 1.08, 1.0), label=f"Lugar {i + 1}")
        if i == 0:
            ph = t.tracks[-1]
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", at + 0.15, 1.8, Box(60, 1500, 960, 200), 36,
              [(0, {"dy": 300}, "out"), (0.35, {})], layers=[shadow("#000000", 0, 10, 26, 0.35), fill("#FFFFFF"), no_stroke()])
        t.solid(t.track("shape", "Número"), "#FF4D4D", at + 0.25, 1.7, centered(160, 1600, 120, 120), pop(0, 0.3),
                kind="ellipse")
        label(t, t.track("text", "Número"), n, at + 0.25, 1.7, centered(160, 1600, 120, 120), "DM Sans", 64, "#FFFFFF",
              weight=800, editable=False, motion=pop(0, 0.3))
        label(t, t.track("text", "Lugar"), name, at + 0.3, 1.65, Box(250, 1500, 760, 200), "DM Sans", 58, "#111111",
              weight=800, align="left", anim_in=tanim("fade", duration=0.25), name=f"Nombre {i + 1}")
    label(t, t.track("text", "Título"), "5 lugares que no te puedes perder", 0.2, 9.8, Box(60, 140, 960, 260), "DM Sans", 84,
          "#FFFFFF", weight=900, layers=[shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Título")
    song(t, "upbeat", 3, 0.85)
    return t


# 42 ----------------------------------------------------------------------------------------------

def detras_camaras():
    t = tall("r-detras-camaras", "Detrás de cámaras", "Behind the scenes", "reels", 9.0, order=3041,
             tags=["detrás de cámaras", "bts", "grabación", "proceso", "creador"], thumb_at=4.5, background="#111111")
    slides(t, ["creator-02", "podcast-01", "creator-04", "office-02"], 0.0, 2.25, transition=None, kb_amount=0.06,
           effects_fn=lambda i: [effect("color.basic", saturation=-0.2, contrast=0.1)])
    m = 60
    frame = t.track("shape", "Visor")
    for (x, y, dx, dy) in ((m, 220, 1, 1), (1080 - m, 220, -1, 1), (m, 1700, 1, -1), (1080 - m, 1700, -1, -1)):
        t.solid(frame, "#FFFFFF", 0, 9.0, Box(x if dx > 0 else x - 110, y if dy > 0 else y - 8, 110, 8))
        t.solid(t.track("shape", "Visor"), "#FFFFFF", 0, 9.0, Box(x if dx > 0 else x - 8, y if dy > 0 else y - 110, 8, 110))
    pill(t, t.track("shape", "BTS"), "#FF2B2B", 0.2, 8.8, Box(80, 250, 230, 80), pop(0, 0.3))
    label(t, t.track("text", "BTS"), "BTS", 0.2, 8.8, Box(80, 250, 230, 80), "Archivo Black", 48, "#FFFFFF", weight=400,
          spacing=4, editable=False)
    notes = ["toma 1: luz perfecta", "toma 4: risas", "toma 9: ¡esta sí!", "y así quedó ✨"]
    for i, n in enumerate(notes):
        label(t, t.track("text", "Nota"), n, i * 2.25 + 0.2, 2.0, Box(80, 1500, 920, 150), "Permanent Marker", 76, "#FFFFFF",
              weight=400, layers=[shadow("#000000", 0, 4, 12, 0.6), fill("#FFFFFF")],
              anim_in=tanim("typewriter", duration=0.5, unit="character"), name=f"Nota {i + 1}")
    song(t, "jazz", 3, 0.8)
    return t


# 43 ----------------------------------------------------------------------------------------------

def lo_que_no_se_vio():
    t = tall("r-lo-que-no-se-vio", "Lo que no se vio", "Bloopers", "reels", 8.0, order=3042,
             tags=["bloopers", "errores", "tomas falsas", "humor", "detrás de cámaras"], thumb_at=0.9, background="#111111")
    bg(t, "#111111")
    t.solid(t.track("shape", "Claqueta"), "#1A1A1A", 0.1, 1.6, centered(540, 900, 820, 520), pop(0, 0.4))
    for k in range(6):
        t.solid(t.track("shape", "Claqueta"), "#FFFFFF" if k % 2 else "#1A1A1A", 0.1, 1.6,
                Box(130 + k * 137, 560, 137, 90), pop(0, 0.4))
    label(t, t.track("text", "Toma"), "TOMA 27", 0.2, 1.5, centered(540, 960, 760, 200), "Special Elite", 140, "#FFFFFF",
          weight=400, editable=False, anim_in=tanim("fade", duration=0.2))
    samples = ["friends-06", "selfie-04", "pet-03", "friends-11", "cooking-04", "family-04"]
    slides(t, samples, 1.6, (8.0 - 1.6) / 6, transition=None, kb_amount=0.1,
           effects_fn=lambda i: [effect("color.basic", contrast=0.15)])
    label(t, t.track("text", "Título"), "lo que no se vio 🙈", 1.7, 6.3, Box(60, 160, 960, 160), "DM Sans", 84, "#FFFFFF",
          weight=900, box_bg=("#000000", 0.55), box_pad=20, box_radius=18, anim_in=tanim("pop", duration=0.3), name="Título")
    t.adjust([effect("beat_shake", animated={"amount": spike([1.6 + k * 1.0667 for k in range(6)], 0.5, 0.2)})],
             name="Golpe")
    song(t, "fun", 2, 0.85)
    return t


# 44 ----------------------------------------------------------------------------------------------

def tierno_stickers():
    t = tall("r-tierno-stickers", "Tierno con stickers", "Cute with stickers", "reels", 8.0, order=3043,
             tags=["tierno", "stickers", "cute", "kawaii", "mascota", "bebé"], thumb_at=4.0, background="#FFE4EC")
    bg(t, "#FFE4EC")
    framed(t, "puppy-03", 0.2, 7.8, Box(120, 330, 840, 1060), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (7.8, {"s": 1.03})],
           border=20, radius=50, colour="#FFFFFF", label="Tu foto")
    stickers = [("⭐", 140, 300, -15), ("💖", 940, 360, 12), ("🌸", 170, 1380, 10), ("🐾", 920, 1360, -10), ("✨", 540, 250, 0),
                ("🍓", 980, 860, 8), ("🎀", 100, 860, -8)]
    for i, (g, x, y, r) in enumerate(stickers):
        label(t, t.track("text", "Sticker"), g, 0.6 + i * 0.2, 7.4 - i * 0.2, centered(x, y, 200, 200), "Inter", 130,
              "#000000", weight=400, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.4, {})], rotation=keys([(0, r)]),
              anim_loop=tanim("swing", angle=8, speed=0.7))
    label(t, t.track("text", "Texto"), "la cosita más bonita", 1.0, 7.0, Box(60, 1500, 960, 160), "Sniglet", 96, "#E5486F",
          weight=800, layers=[stroke(8, "#FFFFFF"), fill("#E5486F")], anim_in=tanim("bounce", duration=0.5, unit="character",
          stagger=0.03), name="Texto")
    song(t, "fun", 4, 0.8)
    return t


# 45 ----------------------------------------------------------------------------------------------

def cumple_ritmo():
    t = tall("r-cumple-ritmo", "Cumple al ritmo", "Birthday on the beat", "celebration", 8.0, order=3044,
             tags=["cumpleaños", "ritmo", "fiesta", "letras", "happy birthday"], thumb_at=5.75, background="#1B1B1B")
    samples = ["birthday-02", "cake-01", "birthday-04", "friends-01", "birthday-08", "cake-03", "birthday-05", "birthday-07"]
    slides(t, samples, 0.0, 1.0, transition=None, kb_amount=0.08)
    word = "FELIZ CUMPLE"
    colours = ["#FF5A5F", "#FFD23F", "#3EC1FF", "#7BF06A", "#FF8C42", "#B26BFF"]
    for i, ch in enumerate(word):
        if ch == " ":
            continue
        at = 4.0 + i * 0.25
        row = 0 if i < 5 else 1
        col = i if i < 5 else i - 6
        label(t, t.track("text", "Letra"), ch, at, 8.0 - at, centered(170 + col * 150 + (0 if row == 0 else -70), 1420 + row * 230, 180, 240),
              "Luckiest Guy", 200, colours[i % len(colours)], weight=400, editable=False,
              layers=[shadow("#000000", 0, 8, 0, 1.0), stroke(6, "#FFFFFF"), fill(colours[i % len(colours)])],
              anim_in=tanim("pop", duration=0.25), rotation=keys([(0, (-1) ** i * 6)]))
    label(t, t.track("text", "Nombre"), "¡Sofi!", 0.2, 7.8, Box(60, 160, 960, 200), "Luckiest Guy", 150, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 8, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          name="Nombre")
    confetti(t, ["#FF5A5F", "#FFD23F", "#3EC1FF", "#FFFFFF"], 4.0, 4.0, seed=3044, lanes=3, density=0.25)
    t.adjust([effect("zoom_pulse", animated={"punch": spike(_beats(1.0, 7, 1.0), 0.35, 0.2)})], name="Pulso")
    song(t, "fun", 0, 0.85)
    return t


# 46 ----------------------------------------------------------------------------------------------

def main_characters():
    t = tall("r-main-characters", "Protagonistas", "Main characters", "reels", 10.0, order=3045,
             tags=["amigas", "protagonistas", "película", "créditos", "main character"], thumb_at=8.8, background="#000000")
    people = [("friends-03", "SOFÍA"), ("portrait-07", "VALE"), ("selfie-02", "CAMI"), ("portrait-02", "LU")]
    for i, (s, n) in enumerate(people):
        at = i * 1.8
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 1.8, t.full, kb(1.8, 1.06, 1.0), label=f"Foto {i + 1}",
                effects=[effect("cinematic_grade", strength=0.6)])
        if i == 0:
            ph = t.tracks[-1]
        label(t, t.track("text", "Nombre"), n, at + 0.2, 1.5, Box(60, 1500, 960, 140), "Cinzel", 100, "#FFFFFF",
              weight=700, spacing=24, anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.3),
              name=f"Nombre {i + 1}")
        label(t, t.track("text", "Papel"), "como ella misma", at + 0.4, 1.3, Box(60, 1640, 960, 70), "Cormorant Garamond", 50,
              "#D9D0BF", weight=500, italic=True, anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.3),
              editable=False)
    photo_bg(t, "friends-09", 7.2, 2.8, s1=1.05, label="Foto del grupo", effects=[effect("cinematic_grade", strength=0.6)])
    letterbox(t, 1.0)
    label(t, t.track("text", "Título"), "PROTAGONISTAS", 7.4, 2.6, Box(60, 820, 960, 160), "Cinzel", 100, "#F4EDE4",
          weight=700, spacing=12, anim_in=tanim("blur-in", duration=0.8), name="Título")
    label(t, t.track("text", "Sub"), "una película de nosotras", 7.8, 2.2, Box(60, 990, 960, 80), "Cormorant Garamond", 56,
          "#D9D0BF", weight=500, italic=True, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    grain(t, 0.18)
    song(t, "cine", 1, 0.85)
    return t


# 47 ----------------------------------------------------------------------------------------------

def papa_hijo():
    t = tall("r-papa-hijo", "Papá y yo", "Dad and me", "reels", 10.0, order=3046,
             tags=["papá", "padre", "hijo", "hija", "familia", "héroe"], thumb_at=6.4)
    slides(t, ["father-02", "father-03", "father-01", "father-04"], 0.0, 2.5, transition="crossfade", tdur=0.6, kb_amount=0.08,
           effects_fn=lambda i: [effect("color.basic", temperature=0.15, fade=0.08)])
    shade_bottom(t, 700, 0.75)
    label(t, t.track("text", "Título"), "mi primer héroe", 1.0, 8.8, Box(60, 1380, 960, 200), "DM Serif Display", 120,
          "#FFFFFF", weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.2), name="Título")
    label(t, t.track("text", "Sub"), "y mi mejor amigo", 2.4, 7.4, Box(60, 1580, 960, 100), "DM Sans", 60, "#FFE0B2",
          weight=600, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    song(t, "epic", 4, 0.8)
    return t


# 48 ----------------------------------------------------------------------------------------------

def abuelos():
    t = tall("r-abuelos", "Gracias, abuelos", "Thank you, grandparents", "reels", 12.0, order=3047,
             tags=["abuelos", "abuela", "abuelo", "familia", "gracias", "recuerdos"], thumb_at=8.0, background="#2B2118")
    samples = ["elderly-01", "elderly-02", "elderly-04", "elderly-03"]
    v = t.track("video", "Fotos")
    prev = None
    for i, s in enumerate(samples):
        at = i * 3.0
        d = 3.0 + (0.8 if i < 3 else 0)
        sep = [effect("stylize.sepia"), effect("color.basic", fade=0.15)]
        clip = t.photo(v, s, at, min(d, 12.0 - at), t.full, kb(d, 1.0, 1.06), label=f"Foto {i + 1}",
                       effects=sep if i < 2 else [effect("color.basic", temperature=0.1)])
        if prev:
            t.transition(v, prev, clip, "luma_fade", 0.8)
        prev = clip
    shade_bottom(t, 700, 0.75, colour="#2B2118")
    label(t, t.track("text", "Texto"), "gracias por cada historia,\ncada abrazo y cada sopa", 1.0, 10.6,
          Box(60, 1420, 960, 300), "Cormorant Garamond", 74, "#FFF4E0", weight=600, italic=True, line=1.15,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15), name="Texto")
    label(t, t.track("text", "Firma"), "— tus nietos", 4.0, 7.6, Box(60, 1730, 960, 80), "Dancing Script", 70, "#F2C14E",
          weight=700, anim_in=tanim("fade", duration=0.6), name="Firma")
    grain(t, 0.2)
    song(t, "classic", 0, 0.8)
    return t


# 49 ----------------------------------------------------------------------------------------------

def gracias_por_tanto():
    t = tall("r-gracias-por-tanto", "Gracias por tanto", "Thank you for everything", "reels", 10.0, order=3048,
             tags=["gracias", "agradecimiento", "mamá", "amistad", "mensaje"], thumb_at=6.5, background="#FFF8F0")
    bg(t, "#FFF8F0")
    spots = [("mother-04", Box(90, 140, 560, 700), -5), ("friends-02", Box(450, 560, 540, 680), 6),
             ("family-05", Box(110, 1040, 560, 640), -3)]
    for i, (s, box, r) in enumerate(spots):
        framed(t, s, 0.3 + i * 0.8, 9.7 - i * 0.8, box, [(0, {"s": 1.3}, "out"), (0.45, {})], border=14,
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Texto"), "gracias por tanto", 2.8, 7.2, Box(560, 1340, 500, 360), "Caveat", 120, "#9C2C5C",
          weight=700, line=0.95, anim_in=tanim("typewriter", duration=1.2, unit="character"), rotation=keys([(0, -4)]),
          name="Texto")
    label(t, t.track("text", "Corazón"), "♥", 4.0, 6.0, centered(860, 1760, 140, 140), "Inter", 100, "#E5486F", weight=400,
          editable=False, motion=pop(0, 0.4), anim_loop=tanim("pulse", amount=10, speed=1.2))
    song(t, "romantic", 2, 0.8)
    return t


# 50 ----------------------------------------------------------------------------------------------

def recuerdo_proyector():
    t = tall("r-recuerdo-proyector", "Recuerdo en proyector", "Projector memory", "reels", 12.0, order=3049,
             tags=["proyector", "recuerdos", "vintage", "película", "familia", "nostalgia"], thumb_at=7.0, background="#0B0906")
    bg(t, "#0B0906")
    beam = t.track("shape", "Haz")
    t.solid(beam, "#FFF4D6", 0, 12.0, centered(540, 960, 1300, 1900), kind="ellipse",
            layers=[gradient([(0, "#FFF4D6", 0.18), (1, "#FFF4D6", 0.0)], angle=0), no_stroke()],
            opacity=blink(12.0, 0.12, 0.85))
    samples = ["family-01", "baby-01", "family-05", "mother-03"]
    for i, s in enumerate(samples):
        at = i * 3.0
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 3.0, Box(80, 420, 920, 1080),
                [(0, {"s": 1.03}, "linear"), (3.0, {"s": 1.0})], label=f"Foto {i + 1}",
                effects=[effect("color.basic", saturation=-1.0, contrast=0.2, fade=0.15)],
                opacity=keys([(0, 0.0), (0.4, 1.0, "hold"), (2.6, 1.0), (3.0, 0.0)]))
        if i == 0:
            ph = t.tracks[-1]
    label(t, t.track("text", "Texto"), "como si fuera ayer", 0.6, 11.0, Box(60, 1580, 960, 160), "Special Elite", 80,
          "#E9E2D0", weight=400, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Texto")
    t.adjust([effect("super8_film", intensity=0.8, grain=0.7, scratches=0.5, weave=0.35, flicker=0.4)], name="Película")
    vignette(t, 0.8)
    song(t, "classic", 1, 0.8)
    return t


TEMPLATES = [velocity_suave, velocity_duro, slowmo_destello, pareja_ritmo, pareja_lento, flash_camara, modo_bestia,
             recuerdo_verano, core_memory, dump_fecha, dump_finde, dump_viaje_mapa, dia_perfecto, zoom_golpe,
             sacudida_3d, giro_camara, cambio_ropa, outfit_check, ojo_pez, grano_analogico, camara_desechable,
             cuadros_4_3, contador_fotos, en_otra_vida, yo_vs_yo, esta_soy_yo, split_ritmo, collage_respira, reflejo,
             foto_rompe, luces_fiesta, letra_sube, si_te_ries, nadie_yo, expectativa_realidad, reaccion_esquina,
             antes_ahora, ciudad_neon, atardecer_cine, lugar_feliz, recorrido_ubicacion, detras_camaras,
             lo_que_no_se_vio, tierno_stickers, cumple_ritmo, main_characters, papa_hijo, abuelos, gracias_por_tanto,
             recuerdo_proyector]
