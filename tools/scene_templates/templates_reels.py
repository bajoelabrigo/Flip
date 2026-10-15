"""Reels and intros (BRIEF.md #2–#9)."""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, anim, beat, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)

MONTHS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def letterbox(t: Template, height: float = 250, start: float = 0.0, dur: float | None = None,
              slide: bool = True) -> None:
    bars = t.track("shape", "Barras")
    top = t.track("shape", "Barras")
    dur = t.duration - start if dur is None else dur
    motion_top = [(0, {"dy": -height}, "out"), (0.8, {})] if slide else None
    motion_bottom = [(0, {"dy": height}, "out"), (0.8, {})] if slide else None
    t.solid(bars, "#000000", start, dur, Box(0, 0, 1080, height), motion_top)
    t.solid(top, "#000000", start, dur, Box(0, 1920 - height, 1080, height), motion_bottom)


def recap_del_anio() -> Template:
    t = Template("recap-del-anio", "Mi año en 12 meses", "My year in 12 months", "reels", 15.0,
                 order=20, tags=["recap", "año", "resumen", "meses", "2026"], thumb_at=1.4, background="#0E0E10")
    photos = t.track("video", "Fotos")
    t.photo(photos, "friends-07", 0, 2.0, FULL, [(0, {"s": 1.0}, "smooth"), (2.0, {"s": 1.12})], label="Portada",
            effects=[effect("color.basic", exposure=-0.25, saturation=-0.1)])
    samples = ["beach-01", "friends-04", "travel-03", "cafe-03", "birthday-03", "beach-04", "travel-08",
               "friends-05", "graduation-02", "nature-03", "couple-02", "family-01"]
    for i, (month, sample) in enumerate(zip(MONTHS, samples)):
        start = 2.0 + i
        t.photo(photos, sample, start, 1.0, FULL, [(0, {"s": 1.08}, "snap"), (0.25, {"s": 1.0}, "linear"),
                                                     (1.0, {"s": 1.03})], label=month.title())
    t.photo(photos, "friends-12", 14.0, 1.0, FULL, [(0, {"s": 1.0}, "smooth"), (1.0, {"s": 1.06})],
            label="Cierre", effects=[effect("color.basic", exposure=-0.3)])
    pills = t.track("shape", "Píldora")
    t.solid(pills, "#FFD84D", 2.0, 12.0, Box(60, 1680, 230, 104), [(0, {"dx": -320}, "out"), (0.4, {})],
            radius=52, kind="rounded-rectangle", layers=[shadow("#000000", 0, 8, 20, 0.4), fill("#FFD84D"), no_stroke()])
    months = t.track("text", "Meses")
    for i, month in enumerate(MONTHS):
        t.text(months, month, 2.0 + i, 1.0, Box(60, 1680, 230, 104),
               text_style("Bebas Neue", 84, [fill("#0E0E10")], weight=400, spacing=4,
                          anim_in=tanim("slide-up", duration=0.25, distance=0.6)), editable=False)
    year = t.track("text", "Año")
    t.text(year, "2026", 0.1, 1.9, Box(0, 560, 1080, 520),
           text_style("Bebas Neue", 430, [shadow("#000000", 0, 16, 40, 0.6), fill("#FFD84D")], weight=400,
                      spacing=6, anim_in=tanim("zoom-out", duration=0.7, ease="easeOut"),
                      anim_out=tanim("fade-scale", duration=0.25)), label="Año")
    t.text(year, "¡Gracias, 2026!", 14.0, 1.0, Box(60, 760, 960, 400),
           text_style("Bebas Neue", 180, [shadow("#000000", 0, 10, 30, 0.6), fill("#FFFFFF")], weight=400,
                      line=0.95, accent={"rule": "lastWord", "colorEnabled": True, "color": "#ffffd84d"},
                      anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.12)), label="Cierre")
    t.adjust([effect("stylize.film_grain", amount=0.15), effect("stylize.vignette", amount=0.5)])
    t.song("inspiration", 4.0, 0.85)
    return t


def slowmo_cinematico() -> Template:
    t = Template("slowmo-cinematico", "Cámara lenta cinemática", "Cinematic slow motion", "reels", 10.0,
                 order=30, tags=["cine", "cinemático", "lento", "atardecer"], thumb_at=2.6)
    photos = t.track("video", "Tomas")
    a = t.photo(photos, "beach-06", 0, 4.0, FULL, [(0, {"s": 1.0}, "linear"), (4.0, {"s": 1.1, "dx": -30})])
    b = t.photo(photos, "couple-05", 4.0, 3.0, FULL, [(0, {"s": 1.12}, "out"), (3.0, {"s": 1.02})])
    c = t.photo(photos, "nature-01", 7.0, 3.0, FULL, [(0, {"s": 1.0}, "linear"), (3.0, {"s": 1.12, "dy": 40})])
    t.transition(photos, a, b, "blur_dissolve", 0.8)
    t.transition(photos, b, c, "crossfade", 0.8)
    t.adjust([effect("cinematic_grade", strength=0.75, teal=0.65, orange=0.6, contrast=0.4),
              effect("light_leak", animated={"intensity": keys([(0, 0.0, "smooth"), (4.0, 0.0, "smooth"),
                                                                (4.6, 0.7, "smooth"), (5.6, 0.0)])},
                     hue=0.07, speed=0.6),
              effect("stylize.film_grain", amount=0.22, grainSize=1.8)], name="Color de cine")
    letterbox(t, 240)
    words = t.track("text", "Texto")
    t.text(words, "momentos", 1.0, 8.4, Box(60, 1500, 960, 160),
           text_style("Cormorant Garamond", 104, [shadow("#000000", 0, 4, 18, 0.5), fill("#F4EDE4")],
                      weight=500, italic=True, spacing=14,
                      anim_in=tanim("blur-in", duration=1.4, blur=30),
                      anim_loop=tanim("tracking-drift", **{"from": 10, "to": 22})),
           label="Título")
    t.text(words, "que no se repiten", 2.0, 7.4, Box(60, 1640, 960, 70),
           text_style("Inter", 32, [fill("#F4EDE4", 0.8)], weight=400, spacing=10, case="upper",
                      anim_in=tanim("fade", duration=1.2)), label="Subtítulo")
    t.song("dreams-of-vain", 0.0, 0.9)
    return t


def hype_glitch() -> Template:
    t = Template("hype-glitch", "Hype con glitch", "Glitch hype", "reels", 8.0,
                 order=40, tags=["hype", "glitch", "energía", "gym", "fiesta"], thumb_at=6.75)
    photos = t.track("video", "Fotos")
    samples = ["fashion-03", "gym-02", "man-03", "fashion-04", "friends-04", "man-02", "gym-01", "man-01"]
    for i, sample in enumerate(samples):
        t.photo(photos, sample, i * 1.0, 1.0, FULL,
                [(0, {"s": 1.22}, "snap"), (0.18, {"s": 1.04}, "linear"), (0.5, {"s": 1.16}, "snap"),
                 (0.68, {"s": 1.02}, "linear"), (1.0, {"s": 1.0})],
                effects=[effect("color.basic", contrast=0.25, saturation=0.15)])
    # Every beat: a split and a punch; every bar: a shake.
    split_keys = []
    for k in range(16):
        split_keys += [(beat(k), 34.0, "out"), (beat(k) + 0.16, 0.0, "hold")]
    flash_keys = []
    for k in range(0, 16, 2):
        flash_keys += [(beat(k), 0.6, "out"), (beat(k) + 0.12, 0.0, "hold")]
    shake_keys = []
    for k in range(0, 16, 4):
        shake_keys += [(beat(k), 0.7, "out"), (beat(k) + 0.3, 0.0, "hold")]
    t.adjust([effect("rgb_split", animated={"amount": keys(split_keys)}, angle=0),
              effect("strobe_flash", animated={"flash": keys(flash_keys)}, tint=0.1),
              effect("beat_shake", animated={"amount": keys(shake_keys)}, rotation=0.4),
              effect("digital_glitch", intensity=0.25, frequency=0.25, rgbAmount=6, blockAmount=0.2,
                     flashAmount=0.0)], name="Glitch")
    words = t.track("text", "Texto")
    hype = lambda size: text_style("Anton", size, [  # noqa: E731
        shadow("#FF2E63", -10, 0, 0, 1.0, id="magenta"), shadow("#08F7FE", 10, 0, 0, 1.0, id="cyan"),
        stroke(6, "#000000"), fill("#FFFFFF")], weight=400, case="upper", line=0.9)
    t.text(words, "¡VAMOS!", 0.0, 1.0, Box(40, 720, 1000, 480),
           {**hype(250), "animation": {"in": tanim("stamp", duration=0.3)}}, label="Grito")
    t.text(words, "¡VAMOS!", 6.0, 2.0, Box(40, 720, 1000, 480),
           {**hype(270), "animation": {"in": tanim("glitch-in", duration=0.35),
                                        "loop": tanim("flicker", intensity=0.35, speed=6)}}, editable=False)
    t.song("action-strike", 0.0, 0.9)
    return t


def vlog_de_viaje() -> Template:
    t = Template("vlog-de-viaje", "Mini vlog de viaje", "Mini travel vlog", "reels", 15.0,
                 order=50, tags=["viaje", "vlog", "turismo", "perú"], thumb_at=1.2)
    photos = t.track("video", "Tomas")
    samples = ["cusco-02", "travel-05", "cusco-03", "travel-09", "travel-06", "cusco-04", "travel-10", "travel-02"]
    clips = []
    starts = [0.0, 2.0, 3.6, 5.2, 6.8, 8.4, 10.0, 11.6]
    ends = starts[1:] + [15.0]
    for i, (sample, a, b) in enumerate(zip(samples, starts, ends)):
        drift = 50 if i % 2 else -50
        clips.append(t.photo(photos, sample, a, b - a, FULL,
                             [(0, {"s": 1.1, "dx": drift}, "linear"), (b - a, {"s": 1.02, "dx": -drift})]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "warp_slide", 0.4)
    t.adjust([effect("color.basic", vibrance=0.25, temperature=0.08, contrast=0.1)], name="Color")
    labels = t.track("shape", "Ubicación")
    t.solid(labels, "#D96C3F", 0.3, 2.6, Box(96, 1338, 30, 30), [(0, {"s": 0.0}, "back"), (0.4, {})],
            kind="ellipse")
    words = t.track("text", "Textos")
    t.text(words, "Cusco, Perú", 0.2, 2.8, Box(80, 1360, 940, 180),
           text_style("DM Serif Display", 128, [shadow("#000000", 0, 6, 24, 0.55), fill("#FFFFFF")], weight=400,
                      align="left", anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.04),
                      anim_out=tanim("fade", duration=0.3)), label="Lugar")
    t.text(words, "Día 1", 0.6, 2.4, Box(130, 1310, 400, 60),
           text_style("Inter", 40, [shadow("#000000", 0, 3, 10, 0.5), fill("#F7E7CE")], weight=600, align="left",
                      spacing=6, case="upper", anim_in=tanim("fade", duration=0.5)), label="Día")
    t.text(words, "volvería mil veces", 12.6, 2.4, Box(60, 1420, 960, 220),
           text_style("Caveat", 132, [shadow("#000000", 0, 4, 18, 0.55), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("typewriter", duration=1.0, unit="character")), label="Cierre")
    stamp = t.track("text", "Fecha")
    t.text(stamp, "15 10 '26", 0.0, 15.0, Box(640, 1760, 380, 80),
           text_style("VT323", 64, [glow("#FF7A1A", 10, 0.7), fill("#FF9A3C")], weight=400, align="right"),
           label="Fecha")
    t.song("adventure", 0.0, 0.85)
    return t


def y2k_brillitos() -> Template:
    t = Template("y2k-brillitos", "Y2K brillitos", "Y2K sparkles", "reels", 10.0,
                 order=60, tags=["y2k", "brillos", "rosa", "aesthetic"], thumb_at=4.2)
    t.solid(t.track("shape", "Fondo"), "#FF8DC7",
            layers=[gradient([(0, "#FF8DC7"), (0.5, "#C9B6FF"), (1, "#B5E8FF")], angle=160), no_stroke()])
    frames = t.track("shape", "Marcos")
    photos = t.track("video", "Fotos")
    samples = ["portrait-02", "portrait-08", "portrait-05", "friends-08", "portrait-07", "fashion-02"]
    for i, sample in enumerate(samples):
        start = 0.5 + i * 1.5
        dur = 1.5 if i < len(samples) - 1 else t.duration - start
        tilt = -5 if i % 2 else 5
        land = [(0, {"s": 0.55, "dy": 160}, "back"), (0.45, {}, "linear"), (dur, {"s": 1.04})]
        rot = keys([(0, tilt * 4, "back"), (0.45, tilt)])
        t.solid(frames, "#FFFFFF", start, dur, centered(540, 980, 800, 1060), land, radius=70,
                kind="rounded-rectangle", layers=[glow("#FFFFFF", 50, 0.9), fill("#FFFFFF"), no_stroke()],
                rotation=rot)
        t.photo(photos, sample, start, dur, centered(540, 980, 740, 1000), land, rotation=rot)
    rng = random.Random(11)
    for k in range(3):
        twinkle = t.track("shape", f"Destello {k + 1}")
        for n in range(4):
            x, y = rng.choice([(rng.uniform(60, 200), rng.uniform(300, 1700)), (rng.uniform(880, 1020), rng.uniform(300, 1700))])
            size = rng.uniform(50, 110)
            start = n * 2.5 + k * 0.7
            t.solid(twinkle, "#FFFFFF", start, 2.0, centered(x, y, size, size),
                    [(0, {"s": 0.0}, "back"), (0.4, {"s": 1.0}, "smooth"), (1.6, {"s": 1.0}, "in"), (2.0, {"s": 0.0})],
                    kind="star", layers=[glow("#FFFFFF", 20, 0.9), fill("#FFFFFF"), no_stroke()],
                    rotation=keys([(0, 0), (2.0, 45)]))
    words = t.track("text", "Textos")
    chrome = [stroke(8, "#FF5FB0"), gradient([(0, "#FFFFFF"), (0.5, "#E9D8FF"), (1, "#FFC1E3")], angle=90)]
    t.text(words, "it girl era", 0.0, 10.0, Box(40, 110, 1000, 260),
           text_style("Pacifico", 140, [glow("#FFFFFF", 30, 0.8)] + chrome, weight=400,
                      anim_in=tanim("bounce", duration=0.6, unit="character", stagger=0.05),
                      anim_loop=tanim("float", amount=0.1, speed=0.5)), label="Título")
    t.text(words, "2026 ★", 0.4, 9.6, Box(40, 1690, 1000, 120),
           text_style("Orbitron", 64, [stroke(4, "#FF5FB0"), fill("#FFFFFF")], weight=700, spacing=8,
                      anim_in=tanim("fade", duration=0.6)), label="Año")
    t.adjust([effect("bling_sparkle", intensity=0.55, density=0.45, threshold=0.75, colorize=0.4)], name="Brillos")
    t.song("bit-bit-loop", 0.0, 0.85)
    return t


def intro_de_canal() -> Template:
    t = Template("intro-de-canal", "Intro de canal", "Channel intro", "intro", 5.0,
                 order=100, tags=["intro", "canal", "youtube", "logo"], thumb_at=3.6, background="#1B1B1B")
    t.solid(t.track("shape", "Fondo"), "#1B1B1B")
    bars = t.track("shape", "Barra amarilla")
    t.solid(bars, "#FFC93C", 0.0, 4.4, Box(-300, 360, 1700, 260), [(0, {"dx": -1800}, "out"), (0.7, {})],
            rotation=const_rot(-16))
    bars2 = t.track("shape", "Barra blanca")
    t.solid(bars2, "#FFFFFF", 0.15, 4.25, Box(-300, 1340, 1700, 120), [(0, {"dx": 1800}, "out"), (0.7, {})],
            rotation=const_rot(-16))
    ring = t.track("shape", "Aro")
    pop = [(0, {"s": 0.0}, "back"), (0.5, {})]
    t.solid(ring, "#FFC93C", 0.9, 3.5, centered(540, 820, 470, 470), pop, kind="ellipse",
            layers=[shadow("#000000", 0, 14, 40, 0.5), fill("#FFC93C"), no_stroke()])
    avatar = t.track("video", "Logo")
    face = t.photo(avatar, "creator-01", 0.9, 3.5, centered(540, 820, 430, 430), pop, label="Logo o cara")
    t.mask(avatar, face, "ellipse")
    words = t.track("text", "Textos")
    t.text(words, "Tu Nombre", 1.6, 2.8, Box(40, 1080, 1000, 170),
           text_style("Poppins", 120, [fill("#FFFFFF")], weight=900,
                      anim_in=tanim("wipe", duration=0.5, angle=0)), label="Nombre")
    t.text(words, "Recetas · Viajes · Vida", 2.1, 2.3, Box(40, 1250, 1000, 90),
           text_style("Poppins", 50, [fill("#FFC93C")], weight=600, spacing=2,
                      anim_in=tanim("typewriter", duration=0.8, unit="character")), label="Temas")
    for clip in (c for tr in t.tracks for c in tr.clips if tr.type != "shape" or c is not t.tracks[0].clips[0]):
        clip["animOut"] = anim("zoomIn", 0.35)
    t.song("funky-energy-loop", 0.0, 0.9)
    return t


def const_rot(deg: float) -> dict:
    return keys([(0, deg)])


def portada_revista() -> Template:
    t = Template("portada-revista", "Portada de revista", "Magazine cover", "intro", 6.0,
                 order=110, tags=["revista", "portada", "moda", "glam"], thumb_at=4.6)
    photo = t.track("video", "Foto")
    t.photo(photo, "portrait-06", 0, 6.0, FULL, [(0, {"s": 1.0}, "linear"), (6.0, {"s": 1.08})], label="Portada")
    fade = t.track("shape", "Sombra")
    t.solid(fade, "#000000", 0, 6.0, Box(0, 1100, 1080, 820),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.9)], angle=90), no_stroke()], alpha=1.0,
            opacity=keys([(0, 0.0), (0.8, 0.7)]))
    words = t.track("text", "Cabecera")
    t.text(words, "VIDA", 0.3, 5.7, Box(0, 40, 1080, 360),
           text_style("Playfair Display", 330, [shadow("#000000", 0, 6, 20, 0.3), fill("#C8102E")], weight=900,
                      spacing=-6, anim_in=tanim("drop", duration=0.6)), label="Cabecera")
    lines = t.track("text", "Titulares")
    t.text(lines, "EDICIÓN 2026", 0.9, 5.1, Box(60, 400, 960, 60),
           text_style("Montserrat", 36, [fill("#FFFFFF")], weight=700, spacing=10, align="left",
                      anim_in=tanim("fade", duration=0.4)), label="Edición")
    t.text(lines, "La mujer del año", 1.4, 4.6, Box(60, 1380, 960, 200),
           text_style("Playfair Display", 104, [shadow("#000000", 0, 4, 14, 0.5), fill("#FFFFFF")], weight=800,
                      italic=True, align="left", line=0.95, anim_in=tanim("slide-left", duration=0.5)),
           label="Titular")
    t.text(lines, "+ 5 secretos de su éxito", 1.8, 4.2, Box(60, 1600, 960, 90),
           text_style("Montserrat", 50, [shadow("#000000", 0, 3, 10, 0.5), fill("#FFD23F")], weight=800,
                      align="left", anim_in=tanim("slide-left", duration=0.5)), label="Subtitular")
    code = t.track("shape", "Código")
    t.solid(code, "#FFFFFF", 4.6, 1.4, Box(860, 1720, 160, 120), [(0, {"s": 0.0}, "back"), (0.3, {})], radius=6)
    bars = t.track("shape", "Barras")
    rng = random.Random(5)
    x = 872
    k = 0
    while x < 1006:
        w = rng.choice([3, 3, 5, 8])
        t.solid(bars if k % 2 == 0 else code, "#000000", 4.7, 1.3, Box(x, 1732, w, 80))
        x += w + rng.choice([3, 4, 6])
        k += 1
    t.song("martini-sunset", 0.0, 0.8)
    return t


def apertura_pelicula() -> Template:
    t = Template("apertura-pelicula", "Apertura de película", "Movie opening", "intro", 7.0,
                 order=120, tags=["película", "cine", "familia", "título"], thumb_at=6.1)
    photos = t.track("video", "Tomas")
    a = t.photo(photos, "family-03", 1.0, 3.0, FULL, [(0, {"s": 1.04}, "linear"), (3.0, {"s": 1.12})])
    b = t.photo(photos, "family-05", 4.0, 3.0, FULL, [(0, {"s": 1.1}, "linear"), (3.0, {"s": 1.0})])
    t.transition(photos, a, b, "crossfade", 0.8)
    a["animIn"] = anim("fade", 0.8)
    t.adjust([effect("cinematic_grade", strength=0.6, teal=0.5, orange=0.6, contrast=0.5),
              effect("light_leak", animated={"intensity": keys([(0, 0.0, "smooth"), (1.4, 0.65, "smooth"), (2.8, 0.0)])},
                     hue=0.05, speed=0.7),
              effect("stylize.film_grain", amount=0.25), effect("stylize.vignette", amount=0.7)])
    letterbox(t, 300, slide=False)
    words = t.track("text", "Títulos")
    t.text(words, "Una historia de", 4.3, 2.7, Box(60, 820, 960, 80),
           text_style("Cormorant Garamond", 52, [fill("#E8D9B5")], weight=500, spacing=12, case="upper",
                      anim_in=tanim("fade", duration=0.8)), label="Antetítulo")
    t.text(words, "Tu familia", 4.8, 2.2, Box(40, 900, 1000, 220),
           text_style("Cormorant Garamond", 170, [shadow("#000000", 0, 4, 24, 0.6), fill("#F3E9D2")], weight=600,
                      italic=True, anim_in=tanim("blur-in", duration=1.2, blur=24),
                      anim_loop=tanim("tracking-drift", **{"from": 0, "to": 14})), label="Título")
    t.song("emotional-blockbuster-2", 0.0, 0.85)
    return t


TEMPLATES = [recap_del_anio, slowmo_cinematico, hype_glitch, vlog_de_viaje, y2k_brillitos,
             intro_de_canal, portada_revista, apertura_pelicula]
