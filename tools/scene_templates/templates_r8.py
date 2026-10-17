"""Reel batch 8 (2026-10-16): international dates and businesses, 1080x1920.
See BRIEF.md, «Las 400 nuevas». Categories seasonal, business; order 3200-3299.

Dates: Easter, Lunar New Year, Ramadan, Eid al-Fitr, Diwali, Holi, Thanksgiving, Women's Day, Earth Day,
Teachers' Day, Children's Day, Grandparents' Day, back to school, end of the school year, summer, cosy
autumn, winter, spring, Hanukkah, minimal Christmas, Christmas Eve at home, elegant New Year, fun
Valentine's, floral Mother's Day, sporty Father's Day.
Businesses: dish of the day, latte art café, bakery, ice-cream shop, corner shop, supermarket deals,
hardware store, pharmacy tip, vet, pet grooming, spa, mechanic, laundry, florist, photographer, house for
sale, removals, language school, music school, community meeting, community thought of the day, charity
drive, handmade shop, online shop free shipping, book an appointment.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels,
                 photo_bg, pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides,
                 song, spike, stroke, tall, tanim, vignette)


def _fall(t, colours, kinds, t0, dur, seed, size=(30, 70), lanes=3, gap=(0.3, 0.7), spin=True, alpha=1.0):
    rng = random.Random(seed)
    for lane in range(lanes):
        tr = t.track("shape", "Caída")
        at = t0 + lane * 0.3
        while at < t0 + dur - 0.6:
            s = rng.uniform(*size)
            fall = rng.uniform(3.5, 6.0)
            d = min(fall, t0 + dur - at)
            extra = {"rotation": keys([(0, rng.uniform(0, 90)), (fall, rng.uniform(-300, 300))])} if spin else {}
            t.solid(tr, rng.choice(colours), at, d, centered(rng.uniform(0, 1080), -80, s, s * 0.8),
                    [(0, {}, "linear"), (fall, {"dy": 2100, "dx": rng.uniform(-180, 180)})], kind=rng.choice(kinds),
                    alpha=alpha, **extra)
            at += rng.uniform(*gap)


def _rows(t, rows, x, y0, step, t0, font, size, colour, chip, chip_text, width=820, gap=0.3):
    for i, (icon, txt) in enumerate(rows):
        at = t0 + i * gap
        y = y0 + i * step
        t.solid(t.track("shape", "Icono"), chip, at, t.duration - at, centered(x + 45, y + 45, 90, 90), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Icono"), icon, at, t.duration - at, centered(x + 45, y + 45, 90, 90), "Inter", 44,
              chip_text, weight=700, editable=False, motion=pop(0, 0.35))
        label(t, t.track("text", "Dato"), txt, at + 0.1, t.duration - at - 0.1, Box(x + 120, y, width, 90), font, size,
              colour, weight=700, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.1),
              name=f"Dato {i + 1}")


# --- International dates ------------------------------------------------------------------------

def pascua():
    t = tall("r-pascua", "Felices Pascuas", "Happy Easter", "seasonal", 9.0, order=3200,
             tags=["pascua", "easter", "huevos", "conejo", "primavera"], thumb_at=5.0, background="#F4FBEF")
    bg_gradient(t, [(0, "#F4FBEF"), (1, "#FFF1DC")], angle=90)
    framed(t, "easter-02", 0.3, 8.7, Box(110, 300, 860, 1000), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (8.7, {"s": 1.03})],
           border=18, radius=40, label="Foto familiar")
    eggs = ["#F9C6D9", "#BDE0FE", "#FFF1B5", "#CDEAC0", "#E2C2FF"]
    for i, c in enumerate(eggs):
        x = 140 + i * 200
        t.solid(t.track("shape", "Huevo"), c, 0.6 + i * 0.15, 8.4 - i * 0.15, centered(x, 1430, 150, 190),
                [(0, {"dy": 500}, "back"), (0.5, {})], kind="ellipse", rotation=keys([(0, (-1) ** i * 10)]),
                layers=[shadow("#000000", 0, 8, 14, 0.15), fill(c), no_stroke()])
        t.solid(t.track("shape", "Franja"), "#FFFFFF", 0.6 + i * 0.15, 8.4 - i * 0.15, centered(x, 1430, 150, 18),
                [(0, {"dy": 500}, "back"), (0.5, {})], alpha=0.85, rotation=keys([(0, (-1) ** i * 10)]))
    label(t, t.track("text", "Título"), "¡Felices Pascuas!", 1.2, 7.8, Box(60, 1580, 960, 200), "Fredoka", 120, "#6A994E",
          weight=700, anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    song(t, "fun", 4, 0.8)
    return t


def anio_nuevo_lunar():
    t = tall("r-anio-nuevo-lunar", "Año Nuevo Lunar", "Lunar New Year", "seasonal", 9.0, order=3201,
             tags=["año nuevo lunar", "año nuevo chino", "faroles", "rojo", "prosperidad"], thumb_at=5.0,
             background="#7A0A0A")
    photo_bg(t, "lunar-02", s1=1.06, label="Foto de fondo")
    shade_full(t, 0.35, colour="#4A0505")
    for i, x in enumerate((180, 900)):
        t.solid(t.track("shape", "Cordón"), "#D4AF37", 0, 9.0, Box(x - 2, 0, 4, 260))
        t.solid(t.track("shape", "Farol"), "#E10600", 0, 9.0, centered(x, 380, 240, 260),
                [(0, {}, "smooth"), (2.0, {"dx": 12}, "smooth"), (4.0, {"dx": -12}, "smooth"), (9.0, {})], kind="ellipse",
                layers=[glow("#FF6A3D", 40, 0.9), gradient([(0, "#FF4D2E"), (1, "#B00000")], angle=90), no_stroke()])
    rrect(t, t.track("shape", "Placa"), "#B00000", 0.4, 8.6, centered(540, 1100, 900, 560), 40, pop(0, 0.5, 0.8),
          layers=[shadow("#000000", 0, 14, 30, 0.45), fill("#B00000", 0.92), stroke(6, "#D4AF37")])
    label(t, t.track("text", "Título"), "Feliz\nAño Nuevo\nLunar", 0.8, 8.2, centered(540, 1060, 860, 460), "Playfair Display",
          112, "#F5D98B", weight=800, line=0.98, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15),
          name="Título")
    label(t, t.track("text", "Deseo"), "salud, suerte y prosperidad", 1.6, 7.4, centered(540, 1320, 860, 80), "Montserrat",
          44, "#FFFFFF", weight=600, anim_in=tanim("fade", duration=0.6), name="Deseo")
    song(t, "world", 3, 0.75)
    return t


def ramadan():
    t = tall("r-ramadan", "Ramadán Kareem", "Ramadan Kareem", "seasonal", 9.0, order=3202,
             tags=["ramadán", "iftar", "familia", "media luna", "faroles"], thumb_at=5.0, background="#0B1530")
    photo_bg(t, "ramadan-02", s1=1.06, label="Foto del iftar")
    shade_top(t, 1100, 0.92, colour="#0B1530")
    t.solid(t.track("shape", "Luna"), "#F5D98B", 0.3, 8.7, centered(540, 360, 300, 300), pop(0, 0.6), kind="ellipse",
            layers=[glow("#F5D98B", 40, 0.7), fill("#F5D98B"), no_stroke()])
    t.solid(t.track("shape", "Luna"), "#0B1530", 0.3, 8.7, centered(620, 320, 280, 280), pop(0, 0.6), kind="ellipse")
    dots(t, ["#FFFFFF", "#F5D98B"], 30, 0, 9.0, seed=3202, size=(4, 10), kinds=("star",), area=Box(0, 0, 1080, 900), drift=10)
    label(t, t.track("text", "Título"), "Ramadán\nKareem", 0.9, 8.1, Box(60, 560, 960, 380), "Marcellus", 150, "#F5D98B",
          weight=400, line=0.95, layers=[glow("#F5D98B", 18, 0.5), fill("#F5D98B")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    label(t, t.track("text", "Deseo"), "paz en tu mesa y en tu corazón", 1.8, 7.2, Box(60, 950, 960, 90), "Montserrat", 46,
          "#DDE3F5", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    song(t, "world", 2, 0.7)
    return t


def eid():
    t = tall("r-eid", "Eid Mubarak", "Eid Mubarak", "seasonal", 8.0, order=3203,
             tags=["eid", "eid mubarak", "fiesta", "familia", "bendiciones"], thumb_at=4.4, background="#0E3B36")
    bg_gradient(t, [(0, "#14544C"), (1, "#072320")], angle=90)
    for i, x in enumerate((140, 360, 720, 940)):
        h = 300 + (i % 2) * 160
        t.solid(t.track("shape", "Cordón"), "#D4AF37", 0, 8.0, Box(x - 2, 0, 4, h - 60))
        t.solid(t.track("shape", "Estrella"), "#F5D98B", 0.2 + i * 0.15, 7.8 - i * 0.15, centered(x, h, 100, 100),
                [(0, {"dy": -400}, "back"), (0.6, {}, "smooth"), (4.0, {"dy": 10}, "smooth"), (7.8 - i * 0.15, {})],
                kind="star", layers=[glow("#F5D98B", 18, 0.8), fill("#F5D98B"), no_stroke()])
    circle_photo(t, "ramadan-01", 0.6, 7.4, centered(540, 1000, 600, 600), pop(0, 0.5), ring_colour="#D4AF37", ring_width=12,
                 label="Foto familiar")
    label(t, t.track("text", "Título"), "Eid Mubarak", 1.0, 7.0, Box(60, 1360, 960, 200), "Cinzel Decorative", 120, "#F5D98B",
          weight=700, layers=[glow("#F5D98B", 18, 0.6), fill("#F5D98B")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    label(t, t.track("text", "Deseo"), "felicidad para ti y los tuyos", 1.8, 6.2, Box(60, 1570, 960, 90), "Montserrat", 46,
          "#E6F2EF", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    song(t, "world", 0, 0.7)
    return t


def diwali():
    t = tall("r-diwali", "Feliz Diwali", "Happy Diwali", "seasonal", 8.0, order=3204,
             tags=["diwali", "luces", "diya", "festival", "celebración"], thumb_at=4.4, background="#1A0B05")
    photo_bg(t, "diwali-02", s1=1.06, label="Foto")
    shade_bottom(t, 900, 0.85, colour="#1A0B05")
    dots(t, ["#FFB703", "#FB8500", "#FFE8A0"], 40, 0, 8.0, seed=3204, size=(6, 16), kinds=("ellipse", "star"), drift=140)
    label(t, t.track("text", "Título"), "Feliz Diwali", 0.6, 7.4, Box(60, 1320, 960, 220), "Yeseva One", 140, "#FFD166",
          weight=400, layers=[glow("#FB8500", 26, 0.8), fill("#FFD166")], anim_in=tanim("blur-in", duration=1.0), name="Título")
    label(t, t.track("text", "Deseo"), "que la luz siempre gane", 1.4, 6.6, Box(60, 1550, 960, 90), "Montserrat", 48, "#FFF1D6",
          weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.9, blurRadius=16)], name="Brillo")
    song(t, "world", 1, 0.75)
    return t


def holi():
    t = tall("r-holi", "Feliz Holi", "Happy Holi", "seasonal", 8.0, order=3205,
             tags=["holi", "colores", "festival", "polvo de colores", "primavera"], thumb_at=3.6, background="#FFFFFF")
    slides(t, ["holi-01", "holi-02", "holi-03"], 0.0, 2.7, transition="ink_bleed", tdur=0.6, kb_amount=0.1)
    rng = random.Random(3205)
    for k in range(12):
        c = rng.choice(["#FF006E", "#FFBE0B", "#3A86FF", "#8338EC", "#06D6A0", "#FB5607"])
        s = rng.uniform(300, 600)
        at = rng.uniform(0, 6)
        t.solid(t.track("shape", "Polvo"), c, at, 2.0, centered(rng.uniform(0, 1080), rng.uniform(200, 1700), s, s),
                [(0, {"s": 0.2}, "out"), (2.0, {"s": 1.4})], kind="cloud",
                layers=[gradient([(0, c, 0.6), (1, c, 0.0)], angle=0), no_stroke()], opacity=keys([(0, 0.9), (2.0, 0.0)]))
    label(t, t.track("text", "Título"), "¡Feliz Holi!", 0.4, 7.6, Box(60, 760, 960, 300), "Luckiest Guy", 190, "#FFFFFF",
          weight=400, layers=[shadow("#8338EC", 0, 12, 0, 1.0), stroke(10, "#FF006E"), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.04), name="Título")
    song(t, "world", 1, 0.85)
    return t


def accion_gracias():
    t = tall("r-accion-gracias", "Acción de Gracias", "Thanksgiving", "seasonal", 9.0, order=3206,
             tags=["acción de gracias", "thanksgiving", "familia", "mesa", "gratitud"], thumb_at=5.0, background="#3A1F0F")
    slides(t, ["thanksgiving-01", "thanksgiving-02", "thanksgiving-03"], 0.0, 3.0, transition="crossfade", tdur=0.6,
           kb_amount=0.07, effects_fn=lambda i: [effect("color.basic", temperature=0.2)])
    shade_bottom(t, 900, 0.85, colour="#2B1408")
    _fall(t, ["#D9480F", "#F08C00", "#A61E4D", "#C2A000"], ["diamond"], 0, 9.0, 3206, size=(44, 80))
    label(t, t.track("text", "Título"), "Gracias", 0.6, 8.4, Box(60, 1300, 960, 260), "Lobster", 200, "#FFD8A8", weight=400,
          anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.05), name="Título")
    label(t, t.track("text", "Mensaje"), "por esta mesa llena de gente que quiero", 1.6, 7.4, Box(60, 1570, 960, 160),
          "Montserrat", 50, "#FFFFFF", weight=600, line=1.2, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "calm", 3, 0.75)
    return t


def dia_mujer():
    t = tall("r-dia-mujer", "Día de la Mujer", "Women's Day", "seasonal", 9.0, order=3207,
             tags=["día de la mujer", "8 de marzo", "mujeres", "fuerza", "inspiración"], thumb_at=6.0, background="#5B2A86")
    bg_gradient(t, [(0, "#7B2CBF"), (1, "#3C096C")], angle=135)
    samples = ["portrait-03", "elderly-04", "portrait-06", "makeup-01"]
    g = 16
    cw, ch = (1080 - 3 * g) / 2, 640
    for i, s in enumerate(samples):
        r, c = divmod(i, 2)
        box = Box(g + c * (cw + g), 200 + r * (ch + g), cw, ch)
        t.photo(t.track("video", f"Foto {i + 1}"), s, 0.3 + i * 0.4, 8.7 - i * 0.4, box,
                [(0, {"s": 0.0}, "back"), (0.45, {}, "linear"), (8.7 - i * 0.4, {"s": 1.03})], label=f"Foto {i + 1}")
    label(t, t.track("text", "Fecha"), "8M", 2.0, 7.0, Box(60, 1530, 300, 200), "Anton", 180, "#E0AAFF", weight=400,
          align="left", anim_in=tanim("stamp", duration=0.3), name="Fecha")
    label(t, t.track("text", "Frase"), "fuertes, libres\ny juntas", 2.4, 6.6, Box(380, 1530, 660, 260), "Playfair Display", 84,
          "#FFFFFF", weight=800, line=1.0, align="left", anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Frase")
    song(t, "epic", 2, 0.75)
    return t


def dia_tierra():
    t = tall("r-dia-tierra", "Día de la Tierra", "Earth Day", "seasonal", 8.0, order=3208,
             tags=["día de la tierra", "planeta", "ecología", "verde", "naturaleza"], thumb_at=4.6, background="#0B2E1D")
    photo_bg(t, "garden-02", s1=1.06, label="Foto")
    shade_top(t, 1000, 0.85, colour="#0B2E1D")
    label(t, t.track("text", "Planeta"), "🌍", 0.3, 7.7, centered(540, 330, 300, 300), "Inter", 220, "#FFFFFF", weight=400,
          editable=False, motion=pop(0, 0.5), rotation=keys([(0, -10, "linear"), (7.7, 10)]))
    label(t, t.track("text", "Título"), "Día de\nla Tierra", 0.7, 7.3, Box(60, 520, 960, 380), "Lexend", 140, "#FFFFFF",
          weight=800, line=0.95, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15), name="Título")
    tips = ["♻ separa tu basura", "💧 cuida el agua", "🌱 planta algo hoy"]
    for i, tip in enumerate(tips):
        at = 1.8 + i * 0.6
        pill(t, t.track("shape", "Consejo"), "#FFFFFF", at, 8.0 - at, Box(140, 1250 + i * 150, 800, 110), slide_in(dx=-900, length=0.4),
             layers=[fill("#FFFFFF", 0.9), no_stroke()])
        label(t, t.track("text", "Consejo"), tip, at + 0.1, 7.9 - at, Box(140, 1250 + i * 150, 800, 110), "Lexend", 48,
              "#0B2E1D", weight=700, name=f"Consejo {i + 1}")
    song(t, "calm", 4, 0.7)
    return t


def dia_maestro():
    t = tall("r-dia-maestro", "Día del Maestro", "Teachers' Day", "seasonal", 8.0, order=3209,
             tags=["día del maestro", "profesora", "escuela", "gracias", "docente"], thumb_at=5.0, background="#1F3B2D")
    bg_gradient(t, [(0, "#2A4A39"), (1, "#16291F")], angle=120)
    outline(t, t.track("shape", "Marco"), "#8B5A2B", 30, 0, 8.0, t.full)
    circle_photo(t, "school-03", 0.3, 7.7, centered(540, 600, 560, 560), pop(0, 0.5), ring_colour="#F2F2EA", ring_width=10,
                 label="Foto con la maestra")
    label(t, t.track("text", "Título"), "¡Gracias,\nprofe!", 0.8, 7.2, Box(80, 960, 920, 380), "Gloria Hallelujah", 140,
          "#F2F2EA", weight=400, line=1.0, layers=[fill("#F2F2EA", 0.92)],
          anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Título")
    label(t, t.track("text", "Mensaje"), "por enseñarnos a soñar", 2.0, 6.0, Box(80, 1380, 920, 100), "Patrick Hand", 70,
          "#FFE08A", weight=400, anim_in=tanim("fade", duration=0.5), name="Mensaje")
    label(t, t.track("text", "Manzana"), "🍎", 2.4, 5.6, centered(540, 1640, 220, 220), "Inter", 160, "#E63946", weight=400,
          editable=False, motion=pop(0, 0.5))
    grain(t, 0.25, 2.0)
    song(t, "calm", 4, 0.7)
    return t


def dia_nino():
    t = tall("r-dia-nino", "Día del Niño", "Children's Day", "seasonal", 8.0, order=3210,
             tags=["día del niño", "niños", "infancia", "juegos", "alegría"], thumb_at=4.4, background="#FFE066")
    bg(t, "#FFE066")
    rng = random.Random(3210)
    for k in range(14):
        kind = rng.choice(["star", "ellipse", "heart", "triangle"])
        c = rng.choice(["#FF595E", "#8AC926", "#1982C4", "#6A4C93", "#FFFFFF"])
        s = rng.uniform(60, 130)
        t.solid(t.track("shape", "Forma"), c, rng.uniform(0, 1), 7.0, centered(rng.uniform(40, 1040), rng.uniform(40, 1880), s, s),
                [(0, {"s": 0.0}, "back"), (0.5, {}, "smooth"), (3.5, {"dy": -30}, "smooth"), (7.0, {})], kind=kind,
                rotation=keys([(0, 0, "linear"), (7.0, rng.uniform(-90, 90))]), alpha=0.8)
    framed(t, "kids-02", 0.4, 7.6, Box(120, 380, 840, 960), [(0, {"s": 0.7}, "back"), (0.5, {}, "linear"), (7.6, {"s": 1.03})],
           border=20, radius=50, rotation=keys([(0, -3)]), label="Foto")
    label(t, t.track("text", "Título"), "¡Feliz Día\ndel Niño!", 0.9, 7.1, Box(60, 1420, 960, 360), "Chewy", 140, "#FF595E",
          weight=400, line=0.95, layers=[shadow("#FFFFFF", 0, 8, 0, 1.0), fill("#FF595E")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    song(t, "fun", 0, 0.85)
    return t


def dia_abuelos():
    t = tall("r-dia-abuelos", "Día de los Abuelos", "Grandparents' Day", "seasonal", 9.0, order=3211,
             tags=["día de los abuelos", "abuela", "abuelo", "familia", "cariño"], thumb_at=5.4, background="#FDF6EC")
    bg(t, "#FDF6EC")
    framed(t, "elderly-02", 0.3, 8.7, Box(110, 220, 860, 1000), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (8.7, {"s": 1.03})],
           border=18, radius=24, rotation=keys([(0, 2)]), label="Foto con los abuelos")
    label(t, t.track("text", "Título"), "Feliz día,\nabuelos", 0.9, 8.1, Box(60, 1300, 960, 360), "Dancing Script", 150,
          "#9C2C5C", weight=700, line=0.95, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Título")
    label(t, t.track("text", "Mensaje"), "las mejores historias empiezan con ustedes", 2.2, 6.8, Box(60, 1680, 960, 140),
          "Cormorant Garamond", 56, "#5C2340", weight=600, italic=True, line=1.15, anim_in=tanim("fade", duration=0.6),
          name="Mensaje")
    song(t, "romantic", 3, 0.75)
    return t


def regreso_clases():
    t = tall("r-regreso-clases", "Regreso a clases", "Back to school", "seasonal", 8.0, order=3212,
             tags=["regreso a clases", "escuela", "mochila", "útiles", "primer día"], thumb_at=4.6, background="#FFF8E6")
    bg(t, "#FFF8E6")
    for k in range(8):
        t.solid(t.track("shape", "Cuadrícula"), "#D6E4F0", 0, 8.0, Box(k * 140, 0, 2, 1920))
    for k in range(14):
        t.solid(t.track("shape", "Cuadrícula"), "#D6E4F0", 0, 8.0, Box(0, k * 140, 1080, 2))
    framed(t, "school-02", 0.3, 7.7, Box(140, 360, 800, 1000), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (7.7, {"s": 1.03})],
           border=16, colour="#FFFFFF", rotation=keys([(0, -3)]), label="Foto del primer día")
    for i, (g, x, y) in enumerate([("✏️", 150, 260), ("📚", 930, 330), ("🎒", 930, 1340), ("📐", 130, 1320)]):
        label(t, t.track("text", "Útil"), g, 0.6 + i * 0.2, 7.4 - i * 0.2, centered(x, y, 220, 220), "Inter", 150, "#000000",
              weight=400, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.4, {})], rotation=keys([(0, (-1) ** i * 12)]))
    label(t, t.track("text", "Título"), "¡De vuelta\na clases!", 1.0, 7.0, Box(60, 1460, 960, 360), "Luckiest Guy", 130,
          "#F94144", weight=400, line=0.95, layers=[shadow("#277DA1", 0, 10, 0, 1.0), fill("#F94144")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    song(t, "fun", 2, 0.8)
    return t


def fin_curso():
    t = tall("r-fin-curso", "Fin de curso", "End of the school year", "seasonal", 9.0, order=3213,
             tags=["fin de curso", "vacaciones", "escuela", "último día", "verano"], thumb_at=6.6, background="#00B4D8")
    slides(t, ["school-03", "kids-01", "school-01", "kids-04"], 0.0, 1.5, transition=None, kb_amount=0.1)
    photo_bg(t, "summer-02", 6.0, 3.0, s1=1.05, label="Foto de vacaciones")
    flash(t, 6.0, 0.3)
    label(t, t.track("text", "Título"), "¡ADIÓS, ESCUELA!", 0.2, 5.8, Box(60, 160, 960, 200), "Luckiest Guy", 110, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 8, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          anim_out=tanim("fade", duration=0.2), name="Primera frase")
    label(t, t.track("text", "Final"), "¡HOLA,\nVACACIONES!", 6.2, 2.8, Box(60, 700, 960, 400), "Luckiest Guy", 150, "#FFE600",
          weight=400, line=0.95, layers=[shadow("#0077B6", 0, 10, 0, 1.0), stroke(8, "#0077B6"), fill("#FFE600")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.15), name="Frase final")
    confetti(t, ["#FFE600", "#FFFFFF", "#FF595E", "#00B4D8"], 6.0, 3.0, seed=3213, lanes=4, density=0.25)
    song(t, "fun", 1, 0.85)
    return t


def verano():
    t = tall("r-verano", "Hola verano", "Hello summer", "seasonal", 8.0, order=3214,
             tags=["verano", "playa", "piscina", "sol", "vacaciones"], thumb_at=4.0)
    slides(t, ["summer-03", "summer-04", "icecream-01", "beach-06"], 0.0, 2.0, transition="slide_up", tdur=0.3, kb_amount=0.08,
           effects_fn=lambda i: [effect("color.basic", saturation=0.25, temperature=0.1)])
    t.solid(t.track("shape", "Sol"), "#FFD60A", 0.2, 7.8, centered(880, 260, 260, 260), pop(0, 0.6), kind="ellipse",
            layers=[glow("#FFB703", 50, 0.8), fill("#FFD60A"), no_stroke()])
    label(t, t.track("text", "Título"), "HOLA\nVERANO", 0.4, 7.6, Box(60, 1300, 960, 440), "Luckiest Guy", 200, "#FFFFFF",
          weight=400, line=0.9, layers=[shadow("#0077B6", 0, 12, 0, 1.0), stroke(8, "#0077B6"), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.2), rotation=keys([(0, -4)]), name="Título")
    song(t, "upbeat", 0, 0.85)
    return t


def otono_acogedor():
    t = tall("r-otono-acogedor", "Otoño acogedor", "Cosy autumn", "seasonal", 9.0, order=3215,
             tags=["otoño", "acogedor", "café", "hojas", "cozy"], thumb_at=5.0, background="#5A3418")
    slides(t, ["autumn-01", "autumn-03", "autumn-04", "reading-03"], 0.0, 2.25, transition="crossfade", tdur=0.5,
           kb_amount=0.07, effects_fn=lambda i: [effect("color.basic", temperature=0.2, fade=0.08)])
    _fall(t, ["#D9480F", "#F08C00", "#A61E4D", "#C2A000"], ["diamond"], 0, 9.0, 3215, size=(40, 76), lanes=2, gap=(0.5, 0.9))
    label(t, t.track("text", "Título"), "cozy season", 0.5, 8.5, Box(60, 1400, 960, 220), "Amatic SC", 200, "#FFF1E0",
          weight=700, layers=[shadow("#3A1F0F", 0, 6, 16, 0.7), fill("#FFF1E0")],
          anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.05), name="Título")
    label(t, t.track("text", "Sub"), "manta · café · un buen libro", 1.6, 7.4, Box(60, 1620, 960, 90), "Amatic SC", 72,
          "#FFD8A8", weight=700, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    grain(t, 0.15)
    song(t, "calm", 1, 0.75)
    return t


def invierno():
    t = tall("r-invierno", "Invierno", "Winter", "seasonal", 9.0, order=3216,
             tags=["invierno", "nieve", "frío", "amigos", "estación"], thumb_at=5.0, background="#DDE7F0")
    slides(t, ["winter-01", "winter-03", "winter-04"], 0.0, 3.0, transition="blur_dissolve", tdur=0.6, kb_amount=0.07,
           effects_fn=lambda i: [effect("color.basic", temperature=-0.15)])
    _fall(t, ["#FFFFFF"], ["ellipse"], 0, 9.0, 3216, size=(8, 24), lanes=4, gap=(0.12, 0.3), spin=False)
    label(t, t.track("text", "Título"), "invierno", 0.5, 8.5, Box(60, 1350, 960, 260), "Cormorant Garamond", 200, "#FFFFFF",
          weight=600, spacing=12, layers=[shadow("#3D5A80", 0, 6, 20, 0.6), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=1.0, blur=16), name="Título")
    song(t, "classic", 2, 0.7)
    return t


def primavera():
    t = tall("r-primavera", "Primavera", "Spring", "seasonal", 8.0, order=3217,
             tags=["primavera", "flores", "colores", "estación", "naturaleza"], thumb_at=4.4, background="#FDF2F8")
    slides(t, ["spring-01", "spring-02", "flowers-02"], 0.0, 2.7, transition="ink_bleed", tdur=0.6, kb_amount=0.08)
    _fall(t, ["#FFB3C6", "#FFFFFF", "#FFD6E0"], ["heart", "ellipse"], 0, 8.0, 3217, size=(22, 44), lanes=3, alpha=0.9)
    label(t, t.track("text", "Título"), "¡Llegó la\nprimavera!", 0.6, 7.4, Box(60, 1360, 960, 380), "Courgette", 130, "#FFFFFF",
          weight=400, line=1.0, layers=[shadow("#B5179E", 0, 6, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.18), name="Título")
    song(t, "upbeat", 7, 0.8)
    return t


def hanukkah():
    t = tall("r-hanukkah", "Feliz Janucá", "Happy Hanukkah", "seasonal", 9.0, order=3218,
             tags=["janucá", "hanukkah", "velas", "luces", "familia"], thumb_at=5.6, background="#0B1D3A")
    bg_gradient(t, [(0, "#14305E"), (1, "#081428")], angle=90)
    dots(t, ["#FFFFFF", "#9EC5FF"], 40, 0, 9.0, seed=3218, size=(4, 10), kinds=("star",), drift=10)
    t.solid(t.track("shape", "Base"), "#C9A44C", 0, 9.0, Box(140, 1060, 800, 26), radius=13, kind="rounded-rectangle")
    t.solid(t.track("shape", "Base"), "#C9A44C", 0, 9.0, Box(520, 1060, 40, 260))
    t.solid(t.track("shape", "Base"), "#C9A44C", 0, 9.0, Box(380, 1300, 320, 30), radius=15, kind="rounded-rectangle")
    xs = [180, 270, 360, 450, 540, 630, 720, 810, 900]
    for i, x in enumerate(xs):
        h = 300 if i == 4 else 230
        t.solid(t.track("shape", "Vela"), "#E8F0FF", 0, 9.0, Box(x - 16, 1060 - h, 32, h), radius=6, kind="rounded-rectangle")
        at = 0.6 + (0 if i == 4 else (abs(i - 4) * 0.7))
        t.solid(t.track("shape", "Llama"), "#FFC94D", at, 9.0 - at, centered(x, 1060 - h - 40, 40, 70), pop(0, 0.4),
                kind="ellipse", layers=[glow("#FFB347", 26, 0.9), fill("#FFE29A"), no_stroke()],
                opacity=blink(9.0 - at, 0.18 + (i % 3) * 0.05, 0.75))
    label(t, t.track("text", "Título"), "Feliz Janucá", 1.0, 8.0, Box(60, 280, 960, 220), "Playfair Display", 130, "#F5D98B",
          weight=700, layers=[glow("#F5D98B", 16, 0.5), fill("#F5D98B")], anim_in=tanim("blur-in", duration=1.0), name="Título")
    label(t, t.track("text", "Deseo"), "ocho noches de luz y alegría", 1.8, 7.2, Box(60, 1440, 960, 90), "Montserrat", 48,
          "#DDE6F5", weight=500, anim_in=tanim("fade", duration=0.6), name="Deseo")
    song(t, "classic", 1, 0.7)
    return t


def navidad_minimal():
    t = tall("r-navidad-minimal", "Navidad minimalista", "Minimal Christmas", "seasonal", 8.0, order=3219,
             tags=["navidad", "minimal", "árbol", "elegante", "diciembre"], thumb_at=4.6, background="#F4F1EA")
    bg(t, "#F4F1EA")
    layers_ = [(560, 360, 240), (760, 500, 360), (960, 640, 480), (1160, 780, 600)]
    for i, (y, w, _) in enumerate(layers_):
        t.solid(t.track("shape", "Árbol"), "#2F5D50", 0.3 + i * 0.25, 7.7 - i * 0.25, centered(540, y, w, 320),
                [(0, {"sy": 0.0, "dy": 160}, "back"), (0.5, {})], kind="triangle")
    t.solid(t.track("shape", "Tronco"), "#7A5230", 1.4, 6.6, Box(500, 1330, 80, 110), pop(0, 0.3))
    t.solid(t.track("shape", "Estrella"), "#D4AF37", 1.6, 6.4, centered(540, 380, 120, 120), pop(0, 0.4), kind="star",
            layers=[glow("#F5D98B", 20, 0.8), fill("#D4AF37"), no_stroke()])
    rng = random.Random(3219)
    for k in range(12):
        y = rng.uniform(560, 1260)
        half = (y - 400) / 900 * 330
        t.solid(t.track("shape", "Esfera"), rng.choice(["#C1121F", "#D4AF37", "#FFFFFF"]), 1.8 + k * 0.1, 6.2 - k * 0.1,
                centered(540 + rng.uniform(-half, half), y, 34, 34), pop(0, 0.3), kind="ellipse")
    label(t, t.track("text", "Título"), "Feliz Navidad", 2.0, 6.0, Box(60, 1520, 960, 180), "Cormorant Garamond", 130,
          "#2F5D50", weight=600, italic=True, anim_in=tanim("fade", duration=0.8), name="Título")
    label(t, t.track("text", "Firma"), "con cariño, familia Ruiz", 2.6, 5.4, Box(60, 1700, 960, 80), "Montserrat", 40,
          "#7A5230", weight=500, spacing=4, anim_in=tanim("fade", duration=0.6), name="Firma")
    song(t, "classic", 2, 0.7)
    return t


def nochebuena():
    t = tall("r-nochebuena", "Nochebuena en casa", "Christmas Eve at home", "seasonal", 9.0, order=3220,
             tags=["nochebuena", "navidad", "cena", "familia", "hogar"], thumb_at=5.4, background="#1B0F0A")
    slides(t, ["christmas-01", "christmas-05", "xmaslights-02", "christmas-03"], 0.0, 2.25, transition="crossfade", tdur=0.5,
           kb_amount=0.07, effects_fn=lambda i: [effect("color.basic", temperature=0.2)])
    for k in range(10):
        c = ["#FF4D4D", "#FFD23F", "#4CC9F0", "#7BF06A"][k % 4]
        if k % 5 == 0:
            lights = t.track("shape", "Luces")
        t.solid(lights, c, 0, 9.0, centered(60 + k * 107, 90 + math.sin(k / 9 * math.pi) * 50, 26, 34), kind="ellipse",
                layers=[glow(c, 18, 0.9), fill(c), no_stroke()], opacity=blink(9.0, 0.7 + (k % 3) * 0.2, 0.4))
    shade_bottom(t, 800, 0.8, colour="#1B0F0A")
    label(t, t.track("text", "Título"), "Nochebuena\nen casa", 0.6, 8.4, Box(60, 1320, 960, 380), "Great Vibes", 160, "#FFFFFF",
          weight=400, line=0.95, layers=[glow("#FFD23F", 16, 0.5), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    song(t, "classic", 0, 0.75)
    return t


def anio_nuevo_elegante():
    t = tall("r-anio-nuevo-elegante", "Año Nuevo elegante", "Elegant New Year", "seasonal", 8.0, order=3221,
             tags=["año nuevo", "elegante", "dorado", "brindis", "fiesta"], thumb_at=4.4, background="#050505")
    bg_gradient(t, [(0, "#141210"), (1, "#050505")], angle=90)
    dots(t, ["#F5D98B", "#FFFFFF", "#E8C27A"], 50, 0, 8.0, seed=3221, size=(4, 12), kinds=("star", "ellipse"), drift=80)
    outline(t, t.track("shape", "Marco"), "#C9A44C", 3, 0.2, 7.8, Box(60, 60, 960, 1800), alpha=0.9,
            opacity=keys([(0, 0.0), (0.8, 1.0)]))
    label(t, t.track("text", "Antetítulo"), "FELIZ", 0.6, 7.4, Box(60, 520, 960, 120), "Cinzel", 96, "#F5D98B", weight=500,
          spacing=40, anim_in=tanim("tracking-drift", duration=1.0), name="Antetítulo")
    label(t, t.track("text", "Año"), "2027", 1.0, 7.0, Box(60, 660, 960, 420), "Playfair Display", 340, "#F5D98B",
          weight=800, layers=[glow("#F5D98B", 26, 0.6), gradient([(0, "#FFF4D6"), (0.5, "#E8C27A"), (1, "#B8892E")], angle=90)],
          anim_in=tanim("blur-in", duration=1.0), name="Año")
    label(t, t.track("text", "Deseo"), "que sea tu mejor año", 1.8, 6.2, Box(60, 1120, 960, 90), "Cormorant Garamond", 64,
          "#E8DCC0", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Deseo")
    t.adjust([effect("bling_sparkle", intensity=0.6, threshold=0.6, density=0.4)], name="Destellos")
    song(t, "jazz", 0, 0.8)
    return t


def san_valentin_divertido():
    t = tall("r-san-valentin-divertido", "San Valentín divertido", "Fun Valentine's", "seasonal", 8.0, order=3222,
             tags=["san valentín", "amor", "humor", "pareja", "corazones"], thumb_at=4.6, background="#FF4D6D")
    bg(t, "#FF4D6D")
    _fall(t, ["#FFFFFF", "#FFB3C1", "#C9184A"], ["heart"], 0, 8.0, 3222, size=(40, 90), lanes=3, spin=False, alpha=0.9)
    framed(t, "couple-07", 0.3, 7.7, Box(140, 300, 800, 960), [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"), (7.7, {"s": 1.03})],
           border=20, radius=40, rotation=keys([(0, 3)]), label="Foto de la pareja")
    label(t, t.track("text", "Título"), "eres mi\npersona favorita", 0.9, 7.1, Box(60, 1320, 960, 360), "Sniglet", 110, "#FFFFFF",
          weight=800, line=1.0, layers=[stroke(8, "#C9184A"), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.15), name="Título")
    label(t, t.track("text", "Chiste"), "(después de la pizza 🍕)", 2.4, 5.6, Box(60, 1700, 960, 90), "Sniglet", 52, "#FFE3EA",
          weight=800, anim_in=tanim("pop", duration=0.3), name="Remate")
    song(t, "fun", 3, 0.85)
    return t


def dia_madre_floral():
    t = tall("r-dia-madre-floral", "Día de la Madre floral", "Floral Mother's Day", "seasonal", 9.0, order=3223,
             tags=["día de la madre", "mamá", "flores", "amor", "gracias"], thumb_at=5.0, background="#FFF5F7")
    bg(t, "#FFF5F7")
    for i, (x, y, s, c) in enumerate([(150, 200, 300, "#F8C8DC"), (930, 260, 260, "#F4A7B9"), (150, 1560, 280, "#FADADD"),
                                      (930, 1640, 320, "#E8B4C8")]):
        for p in range(6):
            a = p / 6 * math.tau
            t.solid(t.track("shape", "Flor"), c, 0.2 + i * 0.2, 8.8 - i * 0.2,
                    centered(x + math.cos(a) * s * 0.28, y + math.sin(a) * s * 0.28, s * 0.42, s * 0.42), pop(0, 0.5),
                    kind="ellipse", alpha=0.9)
        t.solid(t.track("shape", "Flor"), "#FFD166", 0.3 + i * 0.2, 8.7 - i * 0.2, centered(x, y, s * 0.3, s * 0.3),
                pop(0, 0.5), kind="ellipse")
    circle_photo(t, "mother-08", 0.6, 8.4, centered(540, 820, 700, 700), pop(0, 0.5), ring_colour="#F4A7B9", ring_width=14,
                 label="Foto con mamá")
    label(t, t.track("text", "Título"), "Feliz día, mamá", 1.2, 7.8, Box(60, 1220, 960, 200), "Dancing Script", 130, "#9C2C5C",
          weight=700, anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Título")
    label(t, t.track("text", "Mensaje"), "todo lo bonito lo aprendí de ti", 2.4, 6.6, Box(60, 1420, 960, 90),
          "Cormorant Garamond", 60, "#5C2340", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "romantic", 3, 0.75)
    return t


def dia_padre_deportivo():
    t = tall("r-dia-padre-deportivo", "Día del Padre deportivo", "Sporty Father's Day", "seasonal", 8.0, order=3224,
             tags=["día del padre", "papá", "deporte", "fútbol", "campeón"], thumb_at=4.6, background="#0B2545")
    photo_bg(t, "father-02", s1=1.06, label="Foto con papá")
    shade_bottom(t, 1000, 0.85, colour="#0B2545")
    t.solid(t.track("shape", "Dorsal"), "#E63946", 0.5, 7.5, Box(60, 1120, 300, 300), pop(0, 0.4), kind="pentagon")
    label(t, t.track("text", "Número"), "1", 0.6, 7.4, Box(60, 1140, 300, 280), "Anton", 220, "#FFFFFF", weight=400,
          anim_in=tanim("stamp", duration=0.3), name="Número")
    label(t, t.track("text", "Título"), "EL MEJOR\nPAPÁ DEL\nEQUIPO", 0.8, 7.2, Box(390, 1100, 640, 420), "Anton", 110, "#FFFFFF",
          weight=400, line=0.95, align="left", anim_in=tanim("slide-right", duration=0.4, unit="word", stagger=0.1),
          name="Título")
    label(t, t.track("text", "Fecha"), "feliz Día del Padre ⚽", 1.6, 6.4, Box(60, 1580, 960, 100), "Barlow Condensed", 66,
          "#FFD166", weight=800, spacing=4, anim_in=tanim("fade", duration=0.5), name="Saludo")
    song(t, "epic", 2, 0.8)
    return t


# --- Businesses ---------------------------------------------------------------------------------

def plato_del_dia():
    t = tall("r-plato-del-dia", "Plato del día", "Dish of the day", "business", 8.0, order=3225,
             tags=["restaurante", "plato del día", "menú", "almuerzo", "comida"], thumb_at=4.6, background="#1C1410")
    photo_bg(t, "restaurant-01", s1=1.08, label="Foto del plato")
    shade_bottom(t, 900, 0.9, colour="#1C1410")
    pill(t, t.track("shape", "Etiqueta"), "#F4A261", 0.3, 7.7, Box(60, 160, 420, 90), pop(0, 0.35))
    label(t, t.track("text", "Etiqueta"), "PLATO DEL DÍA", 0.3, 7.7, Box(60, 160, 420, 90), "Montserrat", 38, "#1C1410",
          weight=800, spacing=4, name="Etiqueta")
    label(t, t.track("text", "Plato"), "Risotto de hongos", 0.7, 7.3, Box(60, 1300, 960, 220), "Playfair Display", 110, "#FFFFFF",
          weight=700, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12), name="Plato")
    label(t, t.track("text", "Incluye"), "con ensalada y bebida", 1.3, 6.7, Box(60, 1520, 960, 80), "Montserrat", 46, "#D6C7B8",
          weight=500, anim_in=tanim("fade", duration=0.4), name="Incluye")
    label(t, t.track("text", "Precio"), "$9,90", 1.6, 6.4, Box(60, 1620, 960, 170), "Montserrat", 140, "#F4A261", weight=900,
          anim_in=tanim("pop", duration=0.4), anim_loop=tanim("pulse", amount=3, speed=1.2), name="Precio")
    song(t, "jazz", 1, 0.7)
    return t


def cafeteria_latte():
    t = tall("r-cafeteria-latte", "Cafetería: latte art", "Latte art café", "business", 8.0, order=3226,
             tags=["cafetería", "café", "latte", "barista", "desayuno"], thumb_at=4.4, background="#F3E9DC")
    bg(t, "#F3E9DC")
    circle_photo(t, "coffee-01", 0.3, 7.7, centered(540, 760, 820, 820), pop(0, 0.6, 0.6), ring_colour="#6F4E37", ring_width=16,
                 label="Foto del café")
    t.photo(t.track("video", "Logo"), "logo-05", 0.5, 7.5, centered(540, 230, 280, 280), pop(0, 0.5), label="Tu logo")
    label(t, t.track("text", "Título"), "hecho con amor ☕", 1.0, 7.0, Box(60, 1240, 960, 160), "DM Serif Display", 100,
          "#3E2723", weight=400, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12), name="Título")
    label(t, t.track("text", "Horario"), "abierto todos los días · 7 a 20 h", 1.6, 6.4, Box(60, 1420, 960, 80), "Montserrat",
          42, "#6F4E37", weight=600, anim_in=tanim("fade", duration=0.4), name="Horario")
    pill(t, t.track("shape", "Botón"), "#6F4E37", 2.0, 6.0, Box(240, 1560, 600, 120), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "¡te esperamos!", 2.05, 5.95, Box(240, 1560, 600, 120), "Montserrat", 56, "#FFFFFF",
          weight=800, name="Llamada")
    song(t, "jazz", 0, 0.7)
    return t


def panaderia():
    t = tall("r-panaderia", "Panadería: recién horneado", "Bakery", "business", 8.0, order=3227,
             tags=["panadería", "pan", "recién horneado", "pastelería", "desayuno"], thumb_at=4.6, background="#F6E7D0")
    slides(t, ["bakery-02", "bakery-03", "cake-03"], 0.0, 2.7, transition="crossfade", tdur=0.4, kb_amount=0.08,
           effects_fn=lambda i: [effect("color.basic", temperature=0.15)])
    shade_bottom(t, 900, 0.85, colour="#3B2414")
    label(t, t.track("text", "Título"), "recién\nhorneado", 0.5, 7.5, Box(60, 1220, 960, 380), "Lobster", 150, "#FFE8C7",
          weight=400, line=0.95, anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.03), name="Título")
    label(t, t.track("text", "Hora"), "pan caliente desde las 6:30", 1.4, 6.6, Box(60, 1620, 960, 80), "Montserrat", 46,
          "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.4), name="Horario")
    label(t, t.track("text", "Nombre"), "PANADERÍA LA ESPIGA", 1.8, 6.2, Box(60, 1720, 960, 70), "Montserrat", 38, "#F4A261",
          weight=800, spacing=8, anim_in=tanim("fade", duration=0.4), name="Negocio")
    song(t, "jazz", 2, 0.7)
    return t


def heladeria():
    t = tall("r-heladeria", "Heladería", "Ice-cream shop", "business", 8.0, order=3228,
             tags=["helados", "heladería", "verano", "sabores", "postre"], thumb_at=4.0, background="#FFD6E8")
    bg_gradient(t, [(0, "#FFD6E8"), (1, "#C8F2FF")], angle=90)
    for i, s in enumerate(["icecream-01", "icecream-02", "icecream-03"]):
        at = i * 2.6
        t.photo(t.track("video", "Helados") if i == 0 else hl, s, at, 2.6 if i < 2 else 8.0 - at, Box(140, 260, 800, 1100),
                [(0, {"s": 0.0}, "back"), (0.5, {}, "linear"), (2.6, {"s": 1.03})], label=f"Foto {i + 1}")
        if i == 0:
            hl = t.tracks[-1]
    for i, (flav, c) in enumerate([("frutilla", "#FF6B9A"), ("pistacho", "#8BC34A"), ("chocolate", "#6D4C41")]):
        at = i * 2.6 + 0.4
        pill(t, t.track("shape", "Sabor"), c, at, 2.2, Box(240, 1420, 600, 120), pop(0, 0.35))
        label(t, t.track("text", "Sabor"), flav, at, 2.2, Box(240, 1420, 600, 120), "Sniglet", 64, "#FFFFFF", weight=800,
              name=f"Sabor {i + 1}")
    label(t, t.track("text", "Título"), "¿cuál es tu favorito?", 0.2, 7.8, Box(60, 80, 960, 150), "Sniglet", 84, "#C2185B",
          weight=800, anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.02), name="Título")
    label(t, t.track("text", "Precio"), "2 bolas por $3", 0.6, 7.4, Box(60, 1600, 960, 120), "Sniglet", 80, "#0277BD",
          weight=800, anim_in=tanim("pop", duration=0.35), name="Precio")
    song(t, "fun", 4, 0.8)
    return t


def tienda_barrio_v():
    t = tall("r-tienda-barrio", "Tienda de barrio", "Corner shop", "business", 8.0, order=3229,
             tags=["tienda", "barrio", "ofertas", "vecinos", "abarrotes"], thumb_at=4.6, background="#FFD23F")
    bg(t, "#FFD23F")
    t.solid(t.track("shape", "Toldo"), "#E63946", 0, 8.0, Box(0, 0, 1080, 160))
    for k in range(6):
        t.solid(t.track("shape", "Toldo"), "#FFFFFF", 0, 8.0, Box(k * 180 + 90, 0, 90, 160))
    framed(t, "shopping-01", 0.3, 7.7, Box(140, 260, 800, 700), pop(0, 0.5, 0.6), border=14, radius=24, rotation=keys([(0, -2)]),
           label="Foto de la tienda")
    label(t, t.track("text", "Nombre"), "Tienda Doña Rosa", 0.6, 7.4, Box(60, 1000, 960, 140), "Lilita One", 100, "#1D3557",
          weight=400, anim_in=tanim("pop", duration=0.4), name="Tienda")
    offers = [("Leche 1 L", "$1,10"), ("Pan x6", "$1,50"), ("Café 250 g", "$3,90")]
    for i, (p, pr) in enumerate(offers):
        at = 1.2 + i * 0.4
        y = 1180 + i * 170
        rrect(t, t.track("shape", "Fila"), "#FFFFFF", at, 8.0 - at, Box(80, y, 920, 140), 30, slide_in(dx=-1000, length=0.4))
        label(t, t.track("text", "Producto"), p, at + 0.1, 7.9 - at, Box(120, y, 520, 140), "Lilita One", 60, "#1D3557",
              weight=400, align="left", name=f"Producto {i + 1}")
        label(t, t.track("text", "Precio"), pr, at + 0.1, 7.9 - at, Box(640, y, 320, 140), "Lilita One", 72, "#E63946",
              weight=400, align="right", name=f"Precio {i + 1}")
    song(t, "fun", 3, 0.75)
    return t


def super_ofertas():
    t = tall("r-super-ofertas", "Supermercado: ofertas", "Supermarket deals", "business", 8.0, order=3230,
             tags=["supermercado", "ofertas", "precios", "descuentos", "frutas"], thumb_at=5.2, background="#0B8A3E")
    bg(t, "#0B8A3E")
    label(t, t.track("text", "Título"), "OFERTAS\nDE LA SEMANA", 0.2, 7.8, Box(60, 100, 960, 360), "Anton", 140, "#FFFFFF",
          weight=400, line=0.95, anim_in=tanim("slide-down", duration=0.4), name="Título")
    items = [("food-01", "Frutas frescas", "-30%"), ("food-02", "Platos listos", "2x1"),
             ("coffee-03", "Café molido", "$4,99")]
    for i, (s, name, deal) in enumerate(items):
        at = 0.8 + i * 1.8
        d = 8.0 - at
        y = 520 + i * 440
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", at, d, Box(60, y, 960, 400), 30, slide_in(dx=1100, length=0.4),
              layers=[shadow("#000000", 0, 10, 20, 0.3), fill("#FFFFFF"), no_stroke()])
        t.photo(t.track("video", f"Producto {i + 1}"), s, at + 0.1, d - 0.1, Box(90, y + 30, 440, 340),
                slide_in(dx=1100, length=0.4), label=f"Producto {i + 1}")
        label(t, t.track("text", "Producto"), name, at + 0.2, d - 0.2, Box(560, y + 40, 440, 140), "Montserrat", 50, "#111111",
              weight=800, align="left", name=f"Nombre {i + 1}")
        label(t, t.track("text", "Oferta"), deal, at + 0.3, d - 0.3, Box(560, y + 190, 440, 170), "Anton", 130, "#D00000",
              weight=400, align="left", anim_in=tanim("stamp", duration=0.3), name=f"Oferta {i + 1}")
    song(t, "upbeat", 5, 0.75)
    return t


def ferreteria_v():
    t = tall("r-ferreteria", "Ferretería", "Hardware store", "business", 8.0, order=3231,
             tags=["ferretería", "herramientas", "construcción", "hogar", "oferta"], thumb_at=4.4, background="#1B1B1B")
    photo_bg(t, "h-tools-03", s1=1.06, label="Foto de la ferretería")
    shade_full(t, 0.55)
    for k in range(10):
        t.solid(t.track("shape", "Rayas"), "#FFC300" if k % 2 == 0 else "#111111", 0, 8.0, Box(-120 + k * 130, 1760, 130, 160))
    label(t, t.track("text", "Nombre"), "FERRETERÍA\nEL MARTILLO", 0.4, 7.6, Box(60, 160, 960, 320), "Black Ops One", 110,
          "#FFC300", weight=400, line=1.0, anim_in=tanim("slide-right", duration=0.4), name="Ferretería")
    t.solid(t.track("shape", "Descuento"), "#E10600", 0.9, 7.1, centered(540, 900, 640, 640), [(0, {"s": 0.0}, "back"),
                                                                                             (0.5, {})],
            kind="burst", points=20, innerRatio=0.85, rotation=keys([(0, 0, "linear"), (7.1, 30)]))
    label(t, t.track("text", "Descuento"), "-25%", 1.0, 7.0, centered(540, 900, 600, 300), "Anton", 240, "#FFFFFF", weight=400,
          anim_in=tanim("stamp", duration=0.3), name="Descuento")
    label(t, t.track("text", "Oferta"), "en pinturas y brochas", 1.4, 6.6, Box(60, 1300, 960, 160), "Oswald", 80, "#FFFFFF",
          weight=700, anim_in=tanim("rise", duration=0.4), name="Oferta")
    song(t, "epic", 6, 0.7)
    return t


def farmacia_consejo():
    t = tall("r-farmacia-consejo", "Farmacia: consejo de salud", "Pharmacy tip", "business", 9.0, order=3232,
             tags=["farmacia", "salud", "consejo", "bienestar", "prevención"], thumb_at=5.6, background="#E8F7F1")
    bg(t, "#E8F7F1")
    t.solid(t.track("shape", "Cruz"), "#16A34A", 0.2, 8.8, centered(540, 300, 220, 70), pop(0, 0.4), radius=12,
            kind="rounded-rectangle")
    t.solid(t.track("shape", "Cruz"), "#16A34A", 0.2, 8.8, centered(540, 300, 70, 220), pop(0, 0.4), radius=12,
            kind="rounded-rectangle")
    label(t, t.track("text", "Antetítulo"), "CONSEJO DE SALUD", 0.6, 8.4, Box(60, 460, 960, 80), "Lexend", 46, "#16A34A",
          weight=800, spacing=8, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "¿Tomas suficiente agua?", 0.9, 8.1, Box(60, 560, 960, 300), "Lexend", 100, "#064E3B",
          weight=800, line=1.05, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1), name="Título")
    tips = ["💧 8 vasos al día", "🍋 agrega limón o frutas", "⏰ ponte recordatorios"]
    for i, tip in enumerate(tips):
        at = 2.0 + i * 0.7
        rrect(t, t.track("shape", "Consejo"), "#FFFFFF", at, 9.0 - at, Box(80, 940 + i * 170, 920, 140), 30,
              slide_in(dx=-1000, length=0.4), layers=[shadow("#064E3B", 0, 8, 16, 0.12), fill("#FFFFFF"), no_stroke()])
        label(t, t.track("text", "Consejo"), tip, at + 0.1, 8.9 - at, Box(120, 940 + i * 170, 860, 140), "Lexend", 54, "#064E3B",
              weight=600, align="left", name=f"Consejo {i + 1}")
    label(t, t.track("text", "Farmacia"), "Farmacia Central · cuidamos de ti", 3.6, 5.4, Box(60, 1530, 960, 80), "Lexend", 40,
          "#16A34A", weight=700, anim_in=tanim("fade", duration=0.4), name="Farmacia")
    song(t, "calm", 4, 0.65)
    return t


def veterinaria():
    t = tall("r-veterinaria", "Veterinaria", "Vet clinic", "business", 8.0, order=3233,
             tags=["veterinaria", "mascotas", "perros", "gatos", "salud animal"], thumb_at=4.6, background="#E0F2FE")
    bg_gradient(t, [(0, "#E0F2FE"), (1, "#F0FDF4")], angle=90)
    circle_photo(t, "vet-02", 0.3, 7.7, centered(540, 700, 720, 720), pop(0, 0.5, 0.6), ring_colour="#0EA5E9", ring_width=14,
                 label="Foto de la clínica")
    label(t, t.track("text", "Título"), "Cuidamos a\ntu mejor amigo", 0.8, 7.2, Box(60, 1120, 960, 320), "Fredoka", 110,
          "#075985", weight=700, line=1.0, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Título")
    _rows(t, [("🩺", "consultas y vacunas"), ("🏠", "atención a domicilio"), ("📞", "000 123 456")], 120, 1480, 120, 1.6,
          "Fredoka", 50, "#075985", "#0EA5E9", "#FFFFFF")
    song(t, "fun", 2, 0.7)
    return t


def peluqueria_mascotas():
    t = tall("r-peluqueria-mascotas", "Peluquería de mascotas", "Pet grooming", "business", 8.0, order=3234,
             tags=["peluquería canina", "baño", "mascotas", "grooming", "perros"], thumb_at=4.0, background="#FCE7F3")
    bg(t, "#FCE7F3")
    t.photo(t.track("video", "Antes"), "puppy-03", 0.2, 3.4, Box(100, 260, 880, 960), [(0, {"s": 1.1}, "out"), (0.4, {})],
            label="Foto de antes")
    t.photo(t.track("video", "Después"), "pet-02", 3.6, 4.4, Box(100, 260, 880, 960), [(0, {"s": 1.2}, "snap"), (0.3, {})],
            label="Foto de después")
    flash(t, 3.6, 0.3)
    bubbles = t.track("shape", "Burbujas")
    rng = random.Random(3234)
    for k in range(16):
        s = rng.uniform(40, 110)
        ring(t, bubbles if k else bubbles, "#FFFFFF", 5, 3.6 + rng.uniform(0, 1), 2.0, centered(rng.uniform(100, 980), 1200, s, s),
             [(0, {}, "linear"), (2.0, {"dy": -900, "dx": rng.uniform(-80, 80)})], alpha=0.9)
    label(t, t.track("text", "Antes"), "antes 😅", 0.4, 3.0, Box(60, 1300, 960, 140), "Sniglet", 90, "#9D174D", weight=800,
          anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Antes")
    label(t, t.track("text", "Después"), "después ✨", 3.8, 4.2, Box(60, 1300, 960, 140), "Sniglet", 90, "#9D174D", weight=800,
          anim_in=tanim("pop", duration=0.3), name="Después")
    label(t, t.track("text", "Negocio"), "Baño y corte · reserva tu turno", 1.0, 7.0, Box(60, 1520, 960, 90), "Sniglet", 52,
          "#BE185D", weight=800, anim_in=tanim("fade", duration=0.4), name="Servicio")
    song(t, "fun", 1, 0.75)
    return t


def spa():
    t = tall("r-spa", "Spa y relajación", "Spa", "business", 9.0, order=3235,
             tags=["spa", "masajes", "relajación", "bienestar", "belleza"], thumb_at=5.0, background="#EFEAE2")
    slides(t, ["spa-01", "spa-02", "spa-03"], 0.0, 3.0, transition="crossfade", tdur=0.8, kb_amount=0.05,
           effects_fn=lambda i: [effect("color.basic", fade=0.1, saturation=-0.1)])
    shade_bottom(t, 900, 0.75, colour="#3D3229")
    label(t, t.track("text", "Título"), "un momento\npara ti", 0.6, 8.4, Box(60, 1260, 960, 360), "Cormorant Garamond", 140,
          "#FFFFFF", weight=500, italic=True, line=1.0, anim_in=tanim("blur-in", duration=1.0), name="Título")
    label(t, t.track("text", "Oferta"), "masaje de 60 min · 20% de descuento", 1.8, 7.2, Box(60, 1640, 960, 80), "Montserrat",
          42, "#F2E6CF", weight=600, anim_in=tanim("fade", duration=0.6), name="Oferta")
    song(t, "calm", 0, 0.7)
    return t


def taller_mecanico():
    t = tall("r-taller-mecanico", "Taller mecánico", "Mechanic", "business", 8.0, order=3236,
             tags=["taller", "mecánico", "autos", "revisión", "servicio"], thumb_at=4.4, background="#111111")
    photo_bg(t, "mechanic-02", s1=1.06, label="Foto del taller")
    shade_bottom(t, 1100, 0.9)
    label(t, t.track("text", "Título"), "REVISIÓN\nCOMPLETA", 0.4, 7.6, Box(60, 1000, 960, 340), "Russo One", 130, "#FFFFFF",
          weight=400, line=0.95, anim_in=tanim("slide-right", duration=0.4, unit="word", stagger=0.1), name="Título")
    _rows(t, [("🔧", "frenos y suspensión"), ("🛢", "cambio de aceite"), ("⚙", "diagnóstico gratis")], 80, 1380, 120, 1.0,
          "Russo One", 46, "#FFFFFF", "#F59E0B", "#111111")
    label(t, t.track("text", "Precio"), "desde $39", 2.4, 5.6, Box(60, 1760, 960, 110), "Russo One", 80, "#F59E0B", weight=400,
          anim_in=tanim("pop", duration=0.3), name="Precio")
    song(t, "epic", 5, 0.7)
    return t


def lavanderia():
    t = tall("r-lavanderia", "Lavandería", "Laundry", "business", 8.0, order=3237,
             tags=["lavandería", "ropa", "limpieza", "servicio", "delivery"], thumb_at=4.4, background="#E0F7FA")
    bg_gradient(t, [(0, "#E0F7FA"), (1, "#FFFFFF")], angle=90)
    circle_photo(t, "laundry-02", 0.3, 7.7, centered(540, 700, 720, 720),
                 [(0, {"s": 0.0}, "back"), (0.6, {}, "linear"), (7.7, {"s": 1.03})], ring_colour="#00ACC1", ring_width=20,
                 label="Foto")
    ring(t, t.track("shape", "Tambor"), "#00ACC1", 10, 0.3, 7.7, centered(540, 700, 820, 820), pop(0, 0.6), alpha=0.4)
    rng = random.Random(3237)
    for k in range(14):
        s = rng.uniform(30, 80)
        ring(t, t.track("shape", "Burbuja"), "#00ACC1", 4, rng.uniform(0, 5), 3.0, centered(rng.uniform(60, 1020), 1900, s, s),
             [(0, {}, "linear"), (3.0, {"dy": -1600})], alpha=0.6)
    label(t, t.track("text", "Título"), "ropa limpia\nsin esfuerzo", 0.8, 7.2, Box(60, 1120, 960, 320), "Quicksand", 110,
          "#006064", weight=700, line=1.0, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Título")
    label(t, t.track("text", "Servicio"), "lavado + secado + doblado · listo en 24 h", 1.6, 6.4, Box(60, 1480, 960, 140),
          "Quicksand", 48, "#00838F", weight=700, line=1.2, anim_in=tanim("fade", duration=0.4), name="Servicio")
    song(t, "upbeat", 2, 0.7)
    return t


def floristeria():
    t = tall("r-floristeria", "Floristería", "Florist", "business", 8.0, order=3238,
             tags=["flores", "floristería", "ramos", "regalos", "arreglos"], thumb_at=4.4, background="#FDF2F8")
    slides(t, ["flowers-01", "flowers-02", "flowers-03"], 0.0, 2.7, transition="blur_dissolve", tdur=0.5, kb_amount=0.07)
    shade_bottom(t, 900, 0.75, colour="#3A0D22")
    label(t, t.track("text", "Título"), "flores para\ncada momento", 0.5, 7.5, Box(60, 1280, 960, 360), "Parisienne", 130,
          "#FFFFFF", weight=400, line=1.0, anim_in=tanim("blur-in", duration=0.8), name="Título")
    label(t, t.track("text", "Servicio"), "ramos · bodas · entregas el mismo día", 1.4, 6.6, Box(60, 1660, 960, 80),
          "Montserrat", 40, "#FFD6E5", weight=600, anim_in=tanim("fade", duration=0.4), name="Servicio")
    song(t, "romantic", 1, 0.7)
    return t


def fotografo():
    t = tall("r-fotografo", "Fotógrafo", "Photographer", "business", 9.0, order=3239,
             tags=["fotógrafo", "sesión de fotos", "retratos", "estudio", "reservas"], thumb_at=5.0, background="#0F0F0F")
    bg(t, "#0F0F0F")
    samples = ["portrait-02", "wedding-03", "family-01", "portrait-05"]
    for i, s in enumerate(samples):
        at = i * 1.8
        t.photo(t.track("video", "Portafolio") if i == 0 else pf, s, at, 1.8 if i < 3 else 9.0 - at, Box(80, 200, 920, 1150),
                [(0, {"s": 1.05}, "out"), (0.3, {}, "linear"), (1.8, {"s": 1.0})], label=f"Foto {i + 1}")
        if i == 0:
            pf = t.tracks[-1]
        flash(t, at, 0.15, peak=0.6)
    for (x, y) in ((110, 230), (970, 230), (110, 1320), (970, 1320)):
        t.solid(t.track("shape", "Esquina"), "#FFFFFF", 0, 9.0, centered(x, y, 60, 4))
    label(t, t.track("text", "Nombre"), "Lucía Paz · Fotografía", 0.4, 8.6, Box(60, 1420, 960, 120), "Raleway", 70, "#FFFFFF",
          weight=600, spacing=4, anim_in=tanim("fade", duration=0.6), name="Fotógrafa")
    label(t, t.track("text", "Servicio"), "retratos · bodas · familia", 0.8, 8.2, Box(60, 1550, 960, 80), "Raleway", 44,
          "#BBBBBB", weight=400, spacing=6, anim_in=tanim("fade", duration=0.6), name="Servicios")
    pill(t, t.track("shape", "Botón"), "#FFFFFF", 1.4, 7.6, Box(240, 1700, 600, 110), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "reserva tu sesión", 1.45, 7.55, Box(240, 1700, 600, 110), "Raleway", 48, "#0F0F0F",
          weight=800, name="Llamada")
    song(t, "jazz", 3, 0.7)
    return t


def casa_venta():
    t = tall("r-casa-venta", "Se vende casa", "House for sale", "business", 10.0, order=3240,
             tags=["inmobiliaria", "se vende", "casa", "propiedad", "tour"], thumb_at=5.6, background="#F5F1EA")
    slides(t, ["home-02", "interior-05", "interior-03", "interior-08"], 0.0, 2.5, transition="crossfade", tdur=0.5,
           kb_amount=0.07)
    rrect(t, t.track("shape", "Ficha"), "#1F3A5F", 0.5, 9.5, Box(60, 1300, 960, 520), 36, slide_in(dy=600, length=0.5),
          layers=[shadow("#000000", 0, 14, 30, 0.4), fill("#1F3A5F", 0.95), no_stroke()])
    pill(t, t.track("shape", "Insignia"), "#C9A227", 0.3, 9.7, Box(60, 140, 380, 96), pop(0, 0.4))
    label(t, t.track("text", "Insignia"), "SE VENDE", 0.3, 9.7, Box(60, 140, 380, 96), "Montserrat", 50, "#1F3A5F", weight=800,
          spacing=6, name="Insignia")
    label(t, t.track("text", "Precio"), "$185.000", 0.8, 9.2, Box(100, 1330, 880, 140), "Montserrat", 110, "#C9A227",
          weight=900, align="left", anim_in=tanim("pop", duration=0.4), name="Precio")
    label(t, t.track("text", "Datos"), "🛏 3   🛁 2   🚗 1   📐 120 m²", 1.2, 8.8, Box(100, 1480, 880, 90), "Montserrat", 50,
          "#FFFFFF", weight=600, align="left", anim_in=tanim("fade", duration=0.4), name="Datos")
    label(t, t.track("text", "Contacto"), "Laura · 000 123 456", 1.6, 8.4, Box(100, 1620, 880, 90), "Montserrat", 50, "#BFD0E6",
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), name="Contacto")
    song(t, "calm", 2, 0.7)
    return t


def mudanzas_v():
    t = tall("r-mudanzas", "Mudanzas", "Removals", "business", 8.0, order=3241,
             tags=["mudanzas", "transporte", "cajas", "fletes", "servicio"], thumb_at=4.6, background="#FF7B00")
    bg(t, "#FF7B00")
    t.photo(t.track("video", "Foto"), "box-02", 0.2, 7.8, Box(100, 220, 880, 900), [(0, {"dx": 1100}, "out"), (0.6, {})],
            label="Foto del servicio")
    label(t, t.track("text", "Camión"), "🚚", 0.6, 7.4, centered(240, 1240, 300, 240), "Inter", 200, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"dx": -700}, "out"), (1.0, {})], anim_loop=tanim("jitter", amount=1, angle=1, speed=10))
    label(t, t.track("text", "Título"), "MUDANZAS\nSIN ESTRÉS", 0.8, 7.2, Box(60, 1360, 960, 320), "Anton", 140, "#FFFFFF",
          weight=400, line=0.95, anim_in=tanim("slide-right", duration=0.4, unit="word", stagger=0.1), name="Título")
    label(t, t.track("text", "Teléfono"), "☎ 000 123 456", 1.6, 6.4, Box(60, 1700, 960, 120), "Anton", 96, "#1B1B1B",
          weight=400, anim_in=tanim("pop", duration=0.35), name="Teléfono")
    song(t, "upbeat", 4, 0.75)
    return t


def academia_idiomas():
    t = tall("r-academia-idiomas", "Academia de idiomas", "Language school", "business", 9.0, order=3242,
             tags=["idiomas", "inglés", "clases", "academia", "cursos"], thumb_at=5.0, background="#1E3A8A")
    bg_gradient(t, [(0, "#2547A8"), (1, "#152A63")], angle=135)
    words = [("Hello!", 200, 260, "#FFD166"), ("Bonjour!", 760, 420, "#EF476F"), ("Ciao!", 220, 620, "#06D6A0"),
             ("Hallo!", 780, 780, "#FFFFFF"), ("Olá!", 300, 940, "#FFD166")]
    for i, (w, x, y, c) in enumerate(words):
        label(t, t.track("text", "Saludo"), w, 0.3 + i * 0.3, 8.7 - i * 0.3, centered(x, y, 520, 150), "Fredoka", 100, c,
              weight=700, editable=False, motion=pop(0, 0.4), rotation=keys([(0, (-1) ** i * 6)]),
              anim_loop=tanim("float", amount=0.1, speed=0.5))
    label(t, t.track("text", "Título"), "Aprende un idioma\nen 6 meses", 1.8, 7.2, Box(60, 1120, 960, 320), "Fredoka", 100,
          "#FFFFFF", weight=700, line=1.05, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.1),
          name="Título")
    _rows(t, [("🗣", "clases de conversación"), ("💻", "presencial o en línea"), ("🎓", "certificado")], 100, 1480, 120, 2.4,
          "Fredoka", 50, "#FFFFFF", "#FFD166", "#1E3A8A")
    song(t, "upbeat", 5, 0.7)
    return t


def escuela_musica():
    t = tall("r-escuela-musica", "Escuela de música", "Music school", "business", 9.0, order=3243,
             tags=["música", "clases", "guitarra", "piano", "escuela"], thumb_at=5.0, background="#0B0B12")
    photo_bg(t, "music-02", s1=1.06, label="Foto")
    shade_bottom(t, 1000, 0.9, colour="#0B0B12")
    rng = random.Random(3243)
    for k in range(10):
        label(t, t.track("text", "Nota"), rng.choice(["♪", "♫", "♬"]), rng.uniform(0, 5), 3.0,
              centered(rng.uniform(100, 980), 1300, 120, 120), "Inter", rng.choice([70, 90, 110]), "#FFD166", weight=700,
              editable=False, motion=[(0, {}, "linear"), (3.0, {"dy": -900, "dx": rng.uniform(-100, 100)})],
              opacity=keys([(0, 0.0), (0.4, 1.0, "hold"), (2.4, 1.0), (3.0, 0.0)]))
    label(t, t.track("text", "Título"), "Tu música\nempieza aquí", 0.6, 8.4, Box(60, 1080, 960, 320), "DM Serif Display", 120,
          "#FFFFFF", weight=400, line=1.0, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Título")
    label(t, t.track("text", "Clases"), "guitarra · piano · canto · batería", 1.4, 7.6, Box(60, 1440, 960, 80), "Montserrat",
          44, "#FFD166", weight=700, anim_in=tanim("fade", duration=0.4), name="Clases")
    pill(t, t.track("shape", "Botón"), "#FFD166", 2.0, 7.0, Box(190, 1620, 700, 120), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "primera clase gratis", 2.05, 6.95, Box(190, 1620, 700, 120), "Montserrat", 50,
          "#0B0B12", weight=800, name="Llamada")
    song(t, "jazz", 2, 0.75)
    return t


def comunidad_reunion():
    t = tall("r-comunidad-reunion", "Comunidad: reunión semanal", "Community meeting", "business", 8.0, order=3244,
             tags=["comunidad", "reunión", "iglesia", "grupo", "invitación"], thumb_at=4.6, background="#2F3E46")
    photo_bg(t, "community-03", s1=1.06, label="Foto de la comunidad")
    shade_bottom(t, 1100, 0.9, colour="#1B262C")
    label(t, t.track("text", "Antetítulo"), "TE ESPERAMOS", 0.4, 7.6, Box(60, 900, 960, 80), "Montserrat", 50, "#F6BD60",
          weight=800, spacing=14, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Título"), "Reunión de\nla comunidad", 0.7, 7.3, Box(60, 990, 960, 340), "DM Serif Display", 130,
          "#FFFFFF", weight=400, line=0.95, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Título")
    _rows(t, [("📅", "todos los jueves"), ("🕖", "19:30 h"), ("📍", "salón principal")], 100, 1380, 120, 1.5, "Montserrat", 50,
          "#FFFFFF", "#F6BD60", "#1B262C")
    song(t, "calm", 3, 0.7)
    return t


def frase_comunidad():
    t = tall("r-frase-comunidad", "Frase del día de la comunidad", "Community thought of the day", "business", 8.0,
             order=3245, tags=["frase del día", "comunidad", "reflexión", "fe", "esperanza"], thumb_at=5.0, background="#F7F1E3")
    photo_bg(t, "church-02", s1=1.05, label="Fondo", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=4)])
    shade_full(t, 0.4)
    label(t, t.track("text", "Antetítulo"), "FRASE DEL DÍA", 0.3, 7.7, Box(60, 420, 960, 80), "Montserrat", 46, "#F6BD60",
          weight=800, spacing=12, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Frase"), "«Haz el bien sin mirar a quién.»", 0.6, 7.4, Box(80, 560, 920, 600),
          "Cormorant Garamond", 120, "#FFFFFF", weight=600, italic=True, line=1.05,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.2, blur=8), name="Frase")
    label(t, t.track("text", "Firma"), "Comunidad San Pablo", 2.6, 5.4, Box(60, 1300, 960, 80), "Montserrat", 44, "#F2E6CF",
          weight=600, spacing=4, anim_in=tanim("fade", duration=0.6), name="Comunidad")
    song(t, "calm", 0, 0.65)
    return t


def ong_donaciones():
    t = tall("r-ong-donaciones", "Campaña de donaciones", "Charity drive", "business", 9.0, order=3246,
             tags=["donaciones", "ong", "ayuda", "solidaridad", "voluntarios"], thumb_at=5.4, background="#FFF7ED")
    bg(t, "#FFF7ED")
    framed(t, "community-02", 0.3, 8.7, Box(110, 200, 860, 880), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (8.7, {"s": 1.03})],
           border=14, radius=30, label="Foto de la campaña")
    label(t, t.track("text", "Título"), "Juntos llegamos\nmás lejos", 0.8, 8.2, Box(60, 1140, 960, 300), "Lexend", 100,
          "#9A3412", weight=800, line=1.0, anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12),
          name="Título")
    label(t, t.track("text", "Meta"), "meta: 500 kits escolares", 1.6, 7.4, Box(60, 1460, 960, 80), "Lexend", 48, "#C2410C",
          weight=700, anim_in=tanim("fade", duration=0.4), name="Meta")
    rrect(t, t.track("shape", "Barra"), "#FED7AA", 1.8, 7.2, Box(120, 1580, 840, 50), 25)
    rrect(t, t.track("shape", "Barra"), "#EA580C", 1.8, 7.2, Box(120, 1580, 588, 50), 25, [(0, {"sx": 0.0, "dx": -294}, "out"),
                                                                                         (1.5, {})])
    label(t, t.track("text", "Avance"), "70% · ¡ayúdanos a completar!", 2.6, 6.4, Box(60, 1660, 960, 80), "Lexend", 44,
          "#9A3412", weight=700, anim_in=tanim("fade", duration=0.4), name="Avance")
    song(t, "upbeat", 1, 0.7)
    return t


def hecho_a_mano():
    t = tall("r-hecho-a-mano", "Emprendimiento hecho a mano", "Handmade shop", "business", 9.0, order=3247,
             tags=["hecho a mano", "artesanía", "emprendimiento", "tienda", "regalos"], thumb_at=5.0, background="#F3EDE4")
    slides(t, ["handmade-03", "handmade-01", "handmade-02"], 0.0, 3.0, transition="crossfade", tdur=0.6, kb_amount=0.07)
    shade_bottom(t, 900, 0.75, colour="#3B2A20")
    label(t, t.track("text", "Título"), "hecho a mano,\nhecho con calma", 0.6, 8.4, Box(60, 1280, 960, 340), "Caveat", 130,
          "#FFF4E0", weight=700, line=1.0, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Título")
    label(t, t.track("text", "Pedidos"), "pedidos por mensaje directo · envíos a todo el país", 1.8, 7.2, Box(60, 1640, 960, 140),
          "Montserrat", 40, "#F2E6CF", weight=600, line=1.2, anim_in=tanim("fade", duration=0.4), name="Pedidos")
    grain(t, 0.15)
    song(t, "calm", 2, 0.7)
    return t


def envio_gratis():
    t = tall("r-envio-gratis", "Tienda en línea: envío gratis", "Free shipping", "business", 7.0, order=3248,
             tags=["envío gratis", "tienda en línea", "compras", "oferta", "delivery"], thumb_at=3.6, background="#4F46E5")
    bg_gradient(t, [(0, "#6366F1"), (1, "#3730A3")], angle=135)
    t.photo(t.track("video", "Producto"), "box-02", 0.2, 6.8, Box(140, 260, 800, 800), [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"),
                                                                                      (6.8, {"s": 1.04})], label="Foto del pedido")
    label(t, t.track("text", "Camión"), "🚚💨", 1.0, 6.0, centered(540, 1160, 600, 220), "Inter", 160, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"dx": -1100}, "out"), (0.6, {})])
    label(t, t.track("text", "Título"), "ENVÍO GRATIS", 1.2, 5.8, Box(60, 1300, 960, 200), "Anton", 170, "#FFE600", weight=400,
          spacing=4, anim_in=tanim("stamp", duration=0.3), anim_loop=tanim("pulse", amount=3, speed=1.3), name="Título")
    label(t, t.track("text", "Condición"), "en compras desde $30 · solo esta semana", 1.8, 5.2, Box(60, 1520, 960, 140),
          "Montserrat", 46, "#FFFFFF", weight=700, line=1.2, anim_in=tanim("fade", duration=0.4), name="Condición")
    song(t, "electro", 1, 0.8)
    return t


def agenda_citas():
    t = tall("r-agenda-citas", "Agenda tu cita", "Book an appointment", "business", 8.0, order=3249,
             tags=["citas", "reservas", "agenda", "turnos", "salón"], thumb_at=5.0, background="#FFF1F2")
    bg(t, "#FFF1F2")
    circle_photo(t, "salon-02", 0.3, 7.7, centered(540, 560, 600, 600), pop(0, 0.5), ring_colour="#FB7185", ring_width=12,
                 label="Foto del salón")
    label(t, t.track("text", "Título"), "Agenda tu cita", 0.7, 7.3, Box(60, 920, 960, 160), "DM Serif Display", 120,
          "#881337", weight=400, anim_in=tanim("rise", duration=0.4), name="Título")
    days = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB"]
    for i, d in enumerate(days):
        x = 120 + i * 168
        at = 1.4 + i * 0.12
        free = i in (1, 3, 5)
        rrect(t, t.track("shape", "Día"), "#FB7185" if free else "#FFFFFF", at, 8.0 - at, Box(x - 70, 1140, 140, 170), 24,
              pop(0, 0.3), layers=[shadow("#881337", 0, 6, 12, 0.12), fill("#FB7185" if free else "#FFFFFF"), no_stroke()])
        label(t, t.track("text", "Día"), d, at, 8.0 - at, Box(x - 70, 1150, 140, 70), "Montserrat", 36,
              "#FFFFFF" if free else "#881337", weight=800, editable=False, motion=pop(0, 0.3))
        label(t, t.track("text", "Día"), "✓" if free else "—", at, 8.0 - at, Box(x - 70, 1220, 140, 80), "Montserrat", 50,
              "#FFFFFF" if free else "#CCCCCC", weight=800, editable=False, motion=pop(0, 0.3))
    label(t, t.track("text", "Info"), "quedan pocos turnos esta semana", 2.4, 5.6, Box(60, 1360, 960, 80), "Montserrat", 44,
          "#9F1239", weight=700, anim_in=tanim("fade", duration=0.4), name="Aviso")
    pill(t, t.track("shape", "Botón"), "#881337", 2.8, 5.2, Box(190, 1520, 700, 120), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "reserva por mensaje", 2.85, 5.15, Box(190, 1520, 700, 120), "Montserrat", 50, "#FFFFFF",
          weight=800, anim_loop=tanim("pulse", amount=3, speed=1.2), name="Llamada")
    song(t, "upbeat", 7, 0.7)
    return t


TEMPLATES = [pascua, anio_nuevo_lunar, ramadan, eid, diwali, holi, accion_gracias, dia_mujer, dia_tierra, dia_maestro,
             dia_nino, dia_abuelos, regreso_clases, fin_curso, verano, otono_acogedor, invierno, primavera, hanukkah,
             navidad_minimal, nochebuena, anio_nuevo_elegante, san_valentin_divertido, dia_madre_floral,
             dia_padre_deportivo,
             plato_del_dia, cafeteria_latte, panaderia, heladeria, tienda_barrio_v, super_ofertas, ferreteria_v,
             farmacia_consejo, veterinaria, peluqueria_mascotas, spa, taller_mecanico, lavanderia, floristeria, fotografo,
             casa_venta, mudanzas_v, academia_idiomas, escuela_musica, comunidad_reunion, frase_comunidad,
             ong_donaciones, hecho_a_mano, envio_gratis, agenda_citas]
