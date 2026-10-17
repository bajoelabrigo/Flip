"""Products, celebrations, countdowns and endings (BRIEF.md #20–#23, #25–#32)."""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, anim, beat, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)


def pill(t: Template, track, colour: str, t0: float, dur: float, box: Box, motion=None, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=box.h / 2, kind="rounded-rectangle", **extra)


def pop(at: float = 0.0, length: float = 0.45) -> list:
    return [(at, {"s": 0.0}, "back"), (at + length, {})]


# --- Products ------------------------------------------------------------------------------------


def producto_estrella() -> Template:
    t = Template("producto-estrella", "Producto estrella", "Star product", "product", 8.0,
                 order=600, tags=["producto", "tienda", "emprendimiento", "venta"], thumb_at=7.2)
    t.solid(t.track("shape", "Fondo"), "#FF5A1F",
            layers=[gradient([(0, "#FF7A3D"), (1, "#E8410C")], angle=135), no_stroke()])
    cards = t.track("shape", "Tarjeta")
    photos = t.track("video", "Fotos")
    hero_box = centered(540, 900, 820, 1060)
    hero = [(0, {"s": 0.9}, "out"), (3.0, {"s": 1.06})]
    t.solid(cards, "#FFF4E6", 0, 3.0, centered(540, 900, 860, 1100), hero, radius=40, kind="rounded-rectangle",
            layers=[shadow("#7a2200", 0, 24, 50, 0.45), fill("#FFF4E6"), no_stroke()], rotation=keys([(0, -3)]))
    t.photo(photos, "skincare-03", 0, 3.0, hero_box, hero, label="Producto", rotation=keys([(0, -3)]))
    t.photo(photos, "skincare-02", 3.0, 1.5, FULL, [(0, {"s": 1.15}, "snap"), (0.25, {"s": 1.02}, "linear"), (1.5, {"s": 1.0})],
            label="Detalle 1")
    t.photo(photos, "outfit-04", 4.5, 1.5, FULL, [(0, {"s": 1.15}, "snap"), (0.25, {"s": 1.02}, "linear"), (1.5, {"s": 1.0})],
            label="Detalle 2")
    t.solid(cards, "#FFF4E6", 6.0, 2.0, centered(540, 900, 860, 1100), [(0, {"s": 0.8}, "back"), (0.4, {})], radius=40,
            kind="rounded-rectangle", layers=[shadow("#7a2200", 0, 24, 50, 0.45), fill("#FFF4E6"), no_stroke()],
            rotation=keys([(0, 3)]))
    t.photo(photos, "skincare-03", 6.0, 2.0, hero_box, [(0, {"s": 0.8}, "back"), (0.4, {})], reuse="p1",
            rotation=keys([(0, 3)]))
    badge = t.track("shape", "Insignia")
    t.solid(badge, "#FFD23F", 0.5, 2.5, centered(860, 380, 260, 260), pop(), kind="burst", points=14, innerRatio=0.82,
            layers=[shadow("#000000", 0, 8, 16, 0.3), fill("#FFD23F"), no_stroke()],
            rotation=keys([(0, -40, "out"), (0.6, -12)]))
    price = t.track("shape", "Precio")
    t.solid(price, "#111111", 6.3, 1.7, centered(780, 1450, 420, 170), pop(0, 0.5), radius=24,
            kind="rounded-rectangle", rotation=keys([(0, -6)]))
    cta = t.track("shape", "Botón")
    pill(t, cta, "#FFFFFF", 6.6, 1.4, centered(540, 1720, 560, 120),
         [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.8, {"s": 1.06}, "smooth"), (1.2, {"s": 1.0})])
    words = t.track("text", "Textos")
    t.text(words, "NUEVO", 0.6, 2.4, centered(860, 380, 260, 120),
           text_style("Bebas Neue", 76, [fill("#111111")], weight=400, anim_in=tanim("pop", duration=0.4),
                      ), label="Insignia", rotation=keys([(0, -12)]))
    t.text(words, "Polo oversize", 0.2, 2.8, Box(40, 120, 1000, 200),
           text_style("Bebas Neue", 150, [shadow("#7a2200", 0, 8, 0, 0.6), fill("#FFFFFF")], weight=400,
                      anim_in=tanim("slide-down", duration=0.5, unit="character", stagger=0.03)), label="Producto")
    t.text(words, "$59.90", 6.4, 1.6, centered(780, 1450, 420, 170),
           text_style("Bebas Neue", 120, [fill("#FFD23F")], weight=400, anim_in=tanim("stamp", duration=0.35)),
           label="Precio", rotation=keys([(0, -6)]))
    t.text(words, "Pide por DM", 6.7, 1.3, centered(540, 1720, 560, 120),
           text_style("Poppins", 54, [fill("#E8410C")], weight=800), label="Llamada")
    t.song("advertime", 0.0, 0.85)
    return t


def oferta_flash() -> Template:
    t = Template("oferta-flash", "Oferta flash", "Flash sale", "product", 6.0,
                 order=610, tags=["oferta", "descuento", "venta", "promo"], thumb_at=2.2)
    t.solid(t.track("shape", "Fondo"), "#FFD600")
    photos = t.track("video", "Fotos")
    box = centered(540, 980, 860, 980)
    for i in range(12):
        t.photo(photos, ["skincare-02", "skincare-03"][i % 2], i * beat(1), beat(1), box,
                [(0, {"s": 1.08}, "snap"), (0.15, {})], reuse=None if i < 2 else f"p{i % 2 + 1}",
                label=f"Producto {i % 2 + 1}")
    for y, rot, direction in ((170, -6, 1), (1760, 5, -1)):
        band = t.track("shape", "Cinta")
        t.solid(band, "#111111", 0, 6.0, Box(-200, y - 55, 1480, 110), rotation=keys([(0, rot)]))
        tape = t.track("text", "Cinta")
        t.text(tape, "OFERTA ● OFERTA ● OFERTA ● OFERTA ● OFERTA ● OFERTA", 0, 6.0, Box(-600, y - 55, 2600, 110),
               text_style("Anton", 70, [fill("#FFD600")], weight=400, spacing=4, line=1.0),
               [(0, {"dx": -300 * direction}, "linear"), (6.0, {"dx": 300 * direction})], editable=False,
               rotation=keys([(0, rot)]))
    words = t.track("text", "Descuento")
    slam = keys([(0, 900, "snap"), (0.16, 380)])
    t.text(words, "-30%", 0.4, 5.6, Box(0, 640, 1080, 520),
           text_style("Anton", 380, [shadow("#000000", 0, 14, 0, 0.9), stroke(14, "#FFFFFF"), fill("#E10600")],
                      weight=400, keyframes={"pixelSize": slam}), label="Descuento", rotation=keys([(0, -6)]))
    t.text(words, "SOLO HOY", 1.0, 5.0, Box(240, 1160, 600, 120),
           text_style("Anton", 84, [fill("#FFFFFF")], weight=400, spacing=6, box=("#E10600", 1.0), box_pad=18,
                      anim_in=tanim("slide-up", duration=0.35)), label="Cuándo")
    t.text(words, "Escríbenos", 1.4, 4.6, Box(240, 1440, 600, 110),
           text_style("Poppins", 60, [fill("#111111")], weight=800, anim_in=tanim("fade", duration=0.4),
                      anim_loop=tanim("pulse", amount=6, speed=1.5)), label="Llamada")
    bar = t.track("shape", "Tiempo")
    t.solid(bar, "#E10600", 0, 6.0, Box(40, 1640, 1000, 22),
            [(0, {}, "linear"), (6.0, {"sx": 0.0, "dx": -500})])
    t.adjust([effect("beat_shake", animated={"amount": keys([(0.4, 1.0, "out"), (0.8, 0.0)])}, rotation=0.5)])
    t.song("funky-energy-loop", 0.0, 0.9)
    return t


def receta_rapida() -> Template:
    t = Template("receta-rapida", "Receta en 15 segundos", "15-second recipe", "product", 15.0,
                 order=620, tags=["receta", "cocina", "comida", "ensalada"], thumb_at=1.4, background="#FFF8EE")
    t.solid(t.track("shape", "Fondo"), "#FFF8EE")
    cards = t.track("shape", "Tarjeta")
    photos = t.track("video", "Fotos")
    t.photo(photos, "food-01", 0, 2.0, FULL, [(0, {"s": 1.1}, "out"), (2.0, {"s": 1.0})], label="Plato final")
    steps = [("cooking-01", "Ingredientes"), ("cooking-02", "Paso 1"), ("cooking-04", "Paso 2"), ("cooking-05", "Paso 3")]
    box = centered(540, 1010, 940, 1240)
    for i, (sample, label) in enumerate(steps):
        start = 2.0 + i * 2.5
        t.solid(cards, "#FFFFFF", start, 2.5, centered(540, 1010, 970, 1270),
                [(0, {"dx": 1100}, "out"), (0.4, {})], radius=36, kind="rounded-rectangle",
                layers=[shadow("#2F6B3B", 0, 14, 36, 0.25), fill("#FFFFFF"), no_stroke()])
        t.photo(photos, sample, start, 2.5, box, [(0, {"dx": 1100}, "out"), (0.4, {}, "linear"), (2.5, {"s": 1.05})],
                label=label)
    t.photo(photos, "food-01", 12.0, 3.0, FULL, [(0, {"s": 1.0}, "linear"), (3.0, {"s": 1.1})], reuse="p1")
    badges = t.track("shape", "Número")
    words = t.track("text", "Textos")
    titles = ["Ingredientes", "Paso 1: corta las verduras", "Paso 2: el aliño", "Paso 3: sirve"]
    for i, title in enumerate(titles):
        start = 2.0 + i * 2.5
        t.solid(badges, "#2F6B3B", start + 0.3, 2.2, centered(150, 280, 130, 130), pop(), kind="ellipse")
        t.text(words, str(i) if i else "✓", start + 0.35, 2.15, centered(150, 280, 130, 130),
               text_style("DM Serif Display", 80, [fill("#FFFFFF")], weight=400), editable=False)
        t.text(words if i % 2 == 0 else t.track("text", "Títulos"), title, start + 0.4, 2.1, Box(240, 220, 800, 130),
               text_style("DM Serif Display", 66, [fill("#2F6B3B")], weight=400, align="left",
                          anim_in=tanim("rise", duration=0.4)), label=title.split(":")[0])
    hook = t.track("text", "Gancho")
    t.text(hook, "Ensalada fácil", 0.1, 1.9, Box(40, 1300, 1000, 400),
           text_style("DM Serif Display", 170, [shadow("#000000", 0, 8, 30, 0.6), fill("#FFFFFF")], weight=400,
                      line=0.95, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15)),
           label="Título")
    t.text(hook, "¡Buen provecho!", 12.3, 2.7, Box(40, 1400, 1000, 260),
           text_style("DM Serif Display", 140, [shadow("#000000", 0, 8, 30, 0.6), fill("#F2A541")], weight=400,
                      anim_in=tanim("pop", duration=0.5, unit="word", stagger=0.12)), label="Cierre")
    t.song("cumbish", 0.0, 0.85)
    return t


def tour_inmobiliario() -> Template:
    t = Template("tour-inmobiliario", "Tour inmobiliario", "Property tour", "product", 15.0,
                 order=630, tags=["inmobiliaria", "casa", "venta", "departamento"], thumb_at=3.6)
    photos = t.track("video", "Ambientes")
    samples = ["interior-01", "interior-03", "interior-06", "interior-08", "interior-02", "interior-05"]
    clips = []
    for i, sample in enumerate(samples):
        drift = 60 if i % 2 else -60
        clips.append(t.photo(photos, sample, i * 2.5, 2.5, FULL,
                             [(0, {"s": 1.12, "dx": drift}, "linear"), (2.5, {"s": 1.02, "dx": -drift})]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.4)
    t.adjust([effect("color.basic", exposure=0.05, contrast=0.1, vibrance=0.15)], name="Color")
    bar = t.track("shape", "Barra")
    t.solid(bar, "#1F3A5F", 0.4, 14.6, Box(0, 1560, 1080, 260), [(0, {"dy": 300}, "out"), (0.6, {})], alpha=0.94)
    tag = t.track("shape", "Etiqueta")
    t.solid(tag, "#C9A227", 0.2, 14.8, Box(0, 150, 420, 110), [(0, {"dx": -420}, "out"), (0.5, {})],
            layers=[shadow("#000000", 0, 6, 16, 0.4), fill("#C9A227"), no_stroke()])
    words = t.track("text", "Datos")
    t.text(words, "EN VENTA", 0.5, 14.5, Box(30, 150, 380, 110),
           text_style("Montserrat", 58, [fill("#1F3A5F")], weight=800, spacing=4), label="Etiqueta")
    t.text(words, "Barrio Centro", 0.8, 14.2, Box(60, 1580, 960, 110),
           text_style("Playfair Display", 72, [fill("#FFFFFF")], weight=700, align="left",
                      anim_in=tanim("slide-up", duration=0.5)), label="Lugar")
    details = t.track("text", "Detalles")
    t.text(details, "3 dorm · 2 baños · 120 m²", 1.1, 13.9, Box(60, 1690, 960, 90),
           text_style("Montserrat", 46, [fill("#C9A227")], weight=600, align="left",
                      anim_in=tanim("fade", duration=0.5)), label="Detalles")
    cta = t.track("shape", "Botón")
    pill(t, cta, "#C9A227", 12.5, 2.5, centered(540, 1360, 620, 120), pop())
    t.text(t.track("text", "Llamada"), "Agenda tu visita", 12.6, 2.4, centered(540, 1360, 620, 120),
           text_style("Montserrat", 54, [fill("#1F3A5F")], weight=800), label="Llamada")
    t.song("energizing", 0.0, 0.8)
    return t


# --- Celebrations --------------------------------------------------------------------------------


def framed_slideshow(t: Template, samples: list[str], start: float, each: float, box: Box, frame_layers,
                     radius: float = 0, kind: str = "rectangle", transition: str = "crossfade",
                     frame_pad: float = 30, kenburns: float = 1.08, frame_motion=None) -> None:
    frames = t.track("shape", "Marco")
    t.solid(frames, "#FFFFFF", start, each * len(samples), centered(box.cx, box.cy, box.w + frame_pad * 2,
            box.h + frame_pad * 2), frame_motion, radius=radius, kind=kind, layers=frame_layers)
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(samples):
        zoom = [(0, {"s": 1.0}, "linear"), (each, {"s": kenburns})]
        clips.append(t.photo(photos, sample, start + i * each, each, box, zoom))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, transition, min(0.6, each / 3))


def mis_xv() -> Template:
    t = Template("mis-xv", "Mis 15 años", "My 15th birthday", "celebration", 15.0,
                 order=210, tags=["xv", "quinceañera", "15 años", "fiesta"], thumb_at=4.0)
    t.solid(t.track("shape", "Fondo"), "#0B6E4F",
            layers=[gradient([(0, "#0E8A63"), (1, "#053D2B")], angle=90), no_stroke()])
    gold = [glow("#D4AF37", 30, 0.6), stroke(10, "#D4AF37"), {"id": "fill", "kind": "fill", "enabled": False,
                                                               "paint": {"kind": "solid", "color": "#00000000"}}]
    box = centered(540, 1000, 760, 1060)
    framed_slideshow(t, ["quince-04", "quince-01", "quince-06", "quince-03", "quince-05", "quince-08", "quince-02"],
                     0.5, 2.0, box, gold, kind="ellipse", frame_pad=22,
                     frame_motion=[(0, {"s": 0.9}, "out"), (1.0, {})])
    photos = t.tracks[-1]
    for clip in list(photos.clips):
        t.mask(photos, clip, "ellipse", feather=6)
    words = t.track("text", "Títulos")
    goldtext = [shadow("#02251a", 0, 6, 10, 0.6), gradient([(0, "#F7E39C"), (0.5, "#D4AF37"), (1, "#A8841F")], angle=90)]
    t.text(words, "Mis 15", 0.3, 14.7, Box(40, 110, 1000, 300),
           text_style("Great Vibes", 230, goldtext, weight=400, anim_in=tanim("blur-in", duration=1.2, blur=20),
                      anim_loop=tanim("breathe", amount=0.15, speed=0.4)), label="Título")
    t.text(words, "Valentina", 1.0, 14.0, Box(40, 1590, 1000, 140),
           text_style("Cormorant Garamond", 110, [fill("#FFF8F0")], weight=600, italic=True,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.05)), label="Nombre")
    t.text(words, "12 · 12 · 2026", 1.6, 13.4, Box(40, 1730, 1000, 80),
           text_style("Cormorant Garamond", 52, [fill("#D4AF37")], weight=600, spacing=8,
                      anim_in=tanim("fade", duration=0.8)), label="Fecha")
    t.adjust([effect("bling_sparkle", intensity=0.6, density=0.4, threshold=0.7, colorize=0.5)], name="Brillos")
    t.song("isolation-waltz", 0.0, 0.85)
    return t


def para_mama() -> Template:
    t = Template("para-mama", "Para mamá", "For mom", "celebration", 15.0,
                 order=220, tags=["mamá", "día de la madre", "familia", "amor"], thumb_at=9.0)
    t.solid(t.track("shape", "Fondo"), "#F8C8DC",
            layers=[gradient([(0, "#FFF5F7"), (1, "#F8C8DC")], angle=90), no_stroke()])
    rng = random.Random(21)
    for k in range(2):
        hearts = t.track("shape", "Corazones")
        start = k * 0.9
        while start < 14.0:
            size = rng.uniform(40, 80)
            x = rng.uniform(60, 1020)
            dur = rng.uniform(4.0, 6.0)
            t.solid(hearts, "#E88AAE", start, min(dur, 15 - start), centered(x, 2000, size, size),
                    [(0, {}, "linear"), (dur, {"dy": -2200, "dx": rng.uniform(-80, 80)})], kind="heart", alpha=0.55)
            start += rng.uniform(1.0, 1.8)
    frame = [shadow("#9C2C5C", 0, 16, 40, 0.25), fill("#FFFFFF"), no_stroke()]
    framed_slideshow(t, ["mother-01", "mother-04", "mother-02", "mother-06", "mother-03", "mother-08"], 0.0, 2.5,
                     centered(540, 1010, 820, 1080), frame, radius=24, kind="rounded-rectangle", frame_pad=26)
    t.adjust([effect("light_leak", intensity=0.35, hue=0.95, speed=0.5, softness=0.6)], name="Luz")
    words = t.track("text", "Textos")
    rose = lambda size: text_style("Dancing Script", size, [shadow("#FFFFFF", 0, 0, 12, 0.9), fill("#9C2C5C")],  # noqa: E731
                                   weight=700, anim_in=tanim("fade-up-char", duration=0.7, unit="character", stagger=0.04))
    t.text(words, "Para la mejor mamá", 0.4, 7.4, Box(40, 140, 1000, 220), rose(118), label="Título")
    t.text(words, "Gracias por todo", 8.0, 4.4, Box(40, 140, 1000, 220), rose(118), label="Mensaje")
    t.text(words, "Te amo, mamá", 12.6, 2.4, Box(40, 1660, 1000, 200), rose(140), label="Cierre")
    t.song("piano-magic-motive", 0.0, 0.85)
    return t


def me_gradue() -> Template:
    t = Template("me-gradue", "¡Me gradué!", "I graduated!", "celebration", 10.0,
                 order=230, tags=["graduación", "promoción", "logro", "universidad"], thumb_at=5.0)
    t.solid(t.track("shape", "Fondo"), "#0A1F44",
            layers=[gradient([(0, "#12306B"), (1, "#06142E")], angle=90), no_stroke()])
    gold = [glow("#D4AF37", 20, 0.5), fill("#D4AF37"), no_stroke()]
    framed_slideshow(t, ["graduation-02", "graduation-05", "graduation-01", "graduation-06", "graduation-03"],
                     1.0, beat(3), centered(540, 990, 800, 1100), gold, frame_pad=14, transition="glass_wipe")
    rng = random.Random(8)
    for k in range(3):
        confetti = t.track("shape", "Confeti")
        for n in range(8):
            x = rng.uniform(80, 1000)
            start = 8.4 + rng.uniform(0, 0.4)
            t.solid(confetti, rng.choice(["#D4AF37", "#F7E39C", "#FFFFFF"]), start, 10 - start,
                    centered(540, 1000, 40, 40),
                    [(0, {"s": 0.3}, "out"), (0.8, {"dx": x - 540, "dy": rng.uniform(-900, 600), "s": 1.0}, "linear"),
                     (10 - start, {"dx": x - 540, "dy": rng.uniform(300, 900)})], kind="star")
    words = t.track("text", "Textos")
    goldtext = [shadow("#000000", 0, 6, 16, 0.5), gradient([(0, "#F7E39C"), (1, "#C39A2A")], angle=90)]
    t.text(words, "Promoción 2026", 0.3, 9.7, Box(40, 120, 1000, 200),
           text_style("Playfair Display", 110, goldtext, weight=800, anim_in=tanim("drop", duration=0.6)),
           label="Promoción")
    t.text(words, "Lic. María Torres", 8.4, 1.6, Box(40, 1620, 1000, 140),
           text_style("Playfair Display", 92, goldtext, weight=700, italic=True, anim_in=tanim("pop", duration=0.5)),
           label="Nombre")
    t.text(words, "¡Lo logramos!", 1.0, 7.4, Box(40, 1650, 1000, 120),
           text_style("Montserrat", 70, [fill("#FFFFFF")], weight=800, spacing=2,
                      anim_in=tanim("slide-up", duration=0.5)), label="Frase")
    t.song("honor-bound", 0.0, 0.85)
    return t


def nuestra_historia() -> Template:
    t = Template("nuestra-historia", "Nuestra historia", "Our story", "celebration", 12.0,
                 order=240, tags=["pareja", "aniversario", "amor", "san valentín"], thumb_at=6.0)
    t.solid(t.track("shape", "Fondo"), "#FCE8E6",
            layers=[gradient([(0, "#FFF1EF"), (1, "#F6CFCB")], angle=90), no_stroke()])
    behind = t.track("shape", "Corazón")
    t.solid(behind, "#B23A48", 0.3, 11.7, centered(540, 980, 960, 900),
            [(0, {"s": 0.0}, "back"), (0.6, {}, "smooth"), (6.0, {"s": 1.02})] , kind="heart", alpha=0.18)
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(["couple-01", "couple-03", "couple-05", "couple-02", "couple-06", "couple-08"]):
        clips.append(t.photo(photos, sample, 0.6 + i * 1.9, 1.9, centered(540, 960, 880, 820),
                             [(0, {"s": 1.0}, "linear"), (1.9, {"s": 1.06})]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.5)
    for clip in clips:
        t.mask(photos, clip, "heart")
    words = t.track("text", "Textos")
    t.text(words, "Desde 2021", 0.8, 11.2, Box(40, 230, 1000, 140),
           text_style("Caveat", 96, [fill("#B23A48")], weight=700, anim_in=tanim("typewriter", duration=0.8,
                                                                                    unit="character")),
           label="Fecha")
    t.text(words, "Tú y yo", 1.4, 9.0, Box(40, 1450, 1000, 200),
           text_style("DM Serif Display", 150, [fill("#2D2D2D")], weight=400, italic=True,
                      anim_in=tanim("blur-in", duration=0.8)), label="Título")
    t.text(words, "Feliz aniversario", 10.4, 1.6, Box(40, 1450, 1000, 200),
           text_style("DM Serif Display", 120, [fill("#B23A48")], weight=400, italic=True,
                      anim_in=tanim("pop", duration=0.5), anim_loop=tanim("pulse", amount=5, speed=1.0)),
           label="Cierre")
    t.song("night-in-venice", 0.0, 0.85)
    return t


# --- Countdowns ----------------------------------------------------------------------------------


def cuenta_321() -> Template:
    t = Template("cuenta-3-2-1", "Cuenta regresiva 3-2-1", "3-2-1 countdown", "countdown", 5.0,
                 order=700, tags=["cuenta regresiva", "lanzamiento", "sorpresa"], thumb_at=0.55, background="#111111")
    photos = t.track("video", "Fotos")
    for i, sample in enumerate(["friends-04", "beach-01", "friends-07"]):
        t.photo(photos, sample, i * 1.0, 1.0, FULL, [(0, {"s": 1.15}, "snap"), (0.2, {"s": 1.03})],
                effects=[effect("color.basic", exposure=-0.45, saturation=-0.3)])
    t.photo(photos, "friends-07", 3.0, 2.0, FULL, [(0, {"s": 1.2}, "snap"), (0.2, {"s": 1.0})], reuse="p3")
    rings = t.track("shape", "Anillo")
    ring = [stroke(16, "#FF2D55"), {"id": "fill", "kind": "fill", "enabled": False,
                                    "paint": {"kind": "solid", "color": "#00000000"}}]
    for i in range(3):
        t.solid(rings, "#FF2D55", i * 1.0, 1.0, centered(540, 960, 640, 640),
                [(0, {"s": 1.25}, "snap"), (0.25, {}, "linear"), (1.0, {"s": 0.92})], kind="ellipse", layers=ring,
                opacity=keys([(0, 1.0), (0.7, 1.0, "smooth"), (1.0, 0.0)]))
    words = t.track("text", "Números")
    for i, n in enumerate(["3", "2", "1"]):
        t.text(words, n, i * 1.0, 1.0, centered(540, 960, 640, 640),
               text_style("Bebas Neue", 460, [fill("#FFFFFF")], weight=400,
                          keyframes={"pixelSize": keys([(0, 900, "snap"), (0.18, 460)])}), editable=False)
    t.text(words, "¡YA!", 3.0, 2.0, Box(0, 560, 1080, 800),
           text_style("Bebas Neue", 420, [shadow("#000000", 0, 12, 0, 0.8), fill("#FF2D55")], weight=400,
                      keyframes={"pixelSize": keys([(0, 1000, "snap"), (0.18, 420)])}), label="Final")
    flash = t.track("shape", "Destello")
    t.solid(flash, "#FFFFFF", 3.0, 0.3, FULL, opacity=keys([(0, 0.9, "out"), (0.3, 0.0)]))
    t.adjust([effect("beat_shake", animated={"amount": keys([(3.0, 1.0, "out"), (3.6, 0.0)])}, rotation=0.5)])
    t.song("backbeat", 0.0, 0.9)
    return t


def faltan_dias() -> Template:
    t = Template("faltan-dias", "Faltan X días", "X days to go", "countdown", 8.0,
                 order=710, tags=["cuenta regresiva", "faltan", "evento", "lanzamiento"], thumb_at=3.0)
    photos = t.track("video", "Fotos")
    clips = [t.photo(photos, s, i * 8 / 3, 8 / 3, FULL, [(0, {"s": 1.0}, "linear"), (8 / 3, {"s": 1.08})])
             for i, s in enumerate(["city-02", "friends-05", "cafe-04"])]
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.6)
    t.solid(t.track("shape", "Velo"), "#1D3557", alpha=0.62)
    cards = t.track("shape", "Tarjeta")
    card = centered(540, 900, 520, 640)
    t.solid(cards, "#F1FAEE", 0.5, 1.0, card, [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"), (0.8, {}, "in"),
                                               (1.0, {"sy": 0.0})], radius=36, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 20, 40, 0.4), fill("#F1FAEE"), no_stroke()])
    t.solid(cards, "#F1FAEE", 1.5, 6.5, card, [(0, {"sy": 0.0}, "out"), (0.3, {})], radius=36, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 20, 40, 0.4), fill("#F1FAEE"), no_stroke()])
    seam = t.track("shape", "Línea")
    t.solid(seam, "#1D3557", 0.5, 7.5, Box(card.x, card.cy - 3, card.w, 6), alpha=0.25)
    numbers = t.track("text", "Número")
    t.text(numbers, "8", 0.6, 0.9, card, text_style("Space Grotesk", 420, [fill("#E63946")], weight=700,
                                                     anim_in=tanim("fade", duration=0.2)), editable=False,
           height=keys([(0, card.h, "linear"), (0.7, card.h, "in"), (0.9, 0.0)]),
           y=keys([(0, card.y, "linear"), (0.7, card.y, "in"), (0.9, card.cy)]))
    t.text(numbers, "7", 1.5, 6.5, card, text_style("Space Grotesk", 420, [fill("#E63946")], weight=700),
           label="Número", height=keys([(0, 0.0, "out"), (0.3, card.h)]), y=keys([(0, card.cy, "out"), (0.3, card.y)]))
    words = t.track("text", "Textos")
    t.text(words, "Faltan", 0.3, 7.7, Box(40, 360, 1000, 160),
           text_style("Space Grotesk", 110, [fill("#F1FAEE")], weight=700, anim_in=tanim("slide-down", duration=0.5)),
           label="Antes")
    t.text(words, "días para el gran lanzamiento", 1.8, 6.2, Box(90, 1280, 900, 260),
           text_style("Space Grotesk", 76, [fill("#F1FAEE")], weight=600, line=1.05,
                      anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1)), label="Después")
    t.song("hidden-truth", 0.0, 0.85)
    return t


# --- Endings -------------------------------------------------------------------------------------


def cierre_siguenos() -> Template:
    t = Template("cierre-siguenos", "Cierre: síguenos", "Ending: follow us", "outro", 5.0,
                 order=800, tags=["cierre", "seguir", "redes", "suscríbete"], thumb_at=3.6, background="#FFFFFF")
    t.solid(t.track("shape", "Fondo"), "#FFFFFF",
            layers=[gradient([(0, "#FFFFFF"), (1, "#FFE3EA")], angle=90), no_stroke()])
    ring = t.track("shape", "Aro")
    t.solid(ring, "#FF4D6D", 0.2, 4.8, centered(540, 720, 460, 460), pop(), kind="ellipse",
            layers=[gradient([(0, "#FF4D6D"), (1, "#FFB347")], angle=45), no_stroke()])
    avatar = t.track("video", "Foto")
    face = t.photo(avatar, "creator-02", 0.2, 4.8, centered(540, 720, 420, 420), pop(), label="Tu foto")
    t.mask(avatar, face, "ellipse")
    button = t.track("shape", "Botón")
    pill(t, button, "#FF4D6D", 1.6, 1.4, centered(540, 1390, 440, 120),
         [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"), (1.1, {}, "in"), (1.25, {"s": 0.9}, "out"), (1.4, {})])
    pill(t, button, "#E9E9EE", 3.0, 2.0, centered(540, 1390, 440, 120), [(0, {"s": 0.9}, "back"), (0.25, {})])
    words = t.track("text", "Textos")
    t.text(words, "¡Gracias por ver!", 0.6, 4.4, Box(40, 1000, 1000, 140),
           text_style("Poppins", 84, [fill("#111111")], weight=800, anim_in=tanim("rise", duration=0.5)),
           label="Título")
    t.text(words, "@tuusuario", 1.0, 4.0, Box(40, 1130, 1000, 90),
           text_style("Poppins", 54, [fill("#FF4D6D")], weight=600,
                      anim_in=tanim("typewriter", duration=0.6, unit="character")), label="Usuario")
    label = t.track("text", "Botón")
    t.text(label, "Seguir", 1.7, 1.3, centered(540, 1390, 440, 120),
           text_style("Poppins", 54, [fill("#FFFFFF")], weight=700), editable=False)
    t.text(label, "Siguiendo ✓", 3.0, 2.0, centered(540, 1390, 440, 120),
           text_style("Poppins", 54, [fill("#111111")], weight=700), editable=False)
    t.text(words, "Síguenos para más", 1.2, 3.8, Box(40, 1520, 1000, 80),
           text_style("Poppins", 42, [fill("#555555")], weight=500, anim_in=tanim("fade", duration=0.5)),
           label="Llamada")
    rng = random.Random(4)
    hearts = t.track("shape", "Corazones")
    start = 3.1
    while start < 4.8:
        x = rng.uniform(640, 980)
        t.solid(hearts, "#FF4D6D", start, 5.0 - start, centered(x, 1400, 70, 70),
                [(0, {"s": 0.3}, "out"), (5.0 - start, {"dy": -700, "dx": rng.uniform(-80, 80), "s": 1.0})], kind="heart",
                opacity=keys([(0, 1.0), (5.0 - start, 0.0)]))
        start += 0.22
    t.song("hopeful", 0.0, 0.8)
    return t


def cierre_negocio() -> Template:
    t = Template("cierre-negocio", "Cierre de negocio", "Business ending", "outro", 6.0,
                 order=810, tags=["negocio", "contacto", "emprendimiento", "delivery"], thumb_at=4.0)
    shop = t.track("video", "Local")
    t.photo(shop, "cafe-01", 0, 6.0, FULL, [(0, {"s": 1.1}, "linear"), (6.0, {"s": 1.0})], label="Tu local",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=12)])
    t.solid(t.track("shape", "Velo"), "#0F172A", alpha=0.72)
    ring = t.track("shape", "Aro")
    t.solid(ring, "#22C55E", 0.2, 5.8, centered(540, 600, 400, 400), pop(), kind="ellipse")
    logo = t.track("video", "Logo")
    mark = t.photo(logo, "cafe-03", 0.2, 5.8, centered(540, 600, 370, 370), pop(), label="Logo")
    t.mask(logo, mark, "ellipse")
    words = t.track("text", "Textos")
    t.text(words, "Tu Negocio", 0.7, 5.3, Box(40, 860, 1000, 170),
           text_style("Montserrat", 112, [fill("#FFFFFF")], weight=900, anim_in=tanim("rise", duration=0.5)),
           label="Nombre")
    rows = [("Delivery a domicilio", "Servicio"), ("000 123 456", "Teléfono"), ("@tunegocio", "Redes")]
    dots = t.track("shape", "Puntos")
    for i, (content, label) in enumerate(rows):
        y = 1160 + i * 150
        start = 1.2 + i * 0.2
        slide = [(0, {"dx": -700}, "out"), (0.5, {})]
        t.solid(dots, "#22C55E", start, 6.0 - start, centered(250, y + 45, 34, 34), slide, kind="ellipse")
        t.text(words if i % 2 == 0 else t.track("text", "Contacto"), content, start, 6.0 - start, Box(300, y, 740, 90),
               text_style("Montserrat", 56, [fill("#FFFFFF")], weight=600, align="left"), slide, label=label)
    t.song("groovin", 0.0, 0.8)
    return t


TEMPLATES = [producto_estrella, oferta_flash, receta_rapida, tour_inmobiliario, mis_xv, para_mama, me_gradue,
             nuestra_historia, cuenta_321, faltan_dias, cierre_siguenos, cierre_negocio]
