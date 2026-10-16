"""Reel batch 7 (2026-10-16): collages, before/after, celebrations and intros, 1080x1920.
See BRIEF.md, «Las 400 nuevas». Categories collage, beforeafter, celebration, intro; order 3100-3199.

Collages: 3 vertical, 2+1, 3x3, magazine cut-outs, camera frame, cork board, stacked cards, circles, photo
booth strip, sticker album, phone screen, taped diary, thick-border grid, carousel, picture in picture.
Before/after: vertical curtain, day 1 / day 100, make-up, house, garden, hair, pet, kitchen, car, drawing.
Celebrations: kids' party, elegant adult birthday, mum's birthday, cake and candles, wedding anniversary,
first date, proposal, bachelorette, vows, first dance, christening, first communion, kindergarten and
university graduation, retirement, welcome home, new job, new house, sports win, end-of-year party.
Intros: «hi, I'm…», new chapter, series opener, «part 1», blog cover.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels,
                 photo_bg, pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides,
                 song, spike, stroke, tall, tanim, vignette)

B = 0.5


def _cells(t, cells, samples, t0=0.2, step=0.35, motion="pop", radius=0, name="Celda"):
    for i, (box, s) in enumerate(zip(cells, samples)):
        at = t0 + i * step
        d = t.duration - at
        m = {"pop": [(0, {"s": 0.0}, "back"), (0.45, {}, "linear"), (d, {"s": 1.03})],
             "snap": [(0, {"s": 1.25}, "snap"), (0.25, {}, "linear"), (d, {"s": 1.03})],
             "drop": [(0, {"dy": -1400}, "out"), (0.5, {}, "linear"), (d, {"s": 1.02})]}[motion]
        clip = t.photo(t.track("video", f"{name} {i + 1}"), s, at, d, box, m, label=f"Foto {i + 1}")
        if radius:
            pts = _round_rect_points(radius / box.w, radius / box.h)
            t.mask(t.tracks[-1], clip, "freeform", points=pts, smooth=False)


def _round_rect_points(rx: float, ry: float, n: int = 8) -> list:
    """A rounded rectangle as a freeform mask (normalised to the clip box)."""
    pts = []
    for cx, cy, a0 in ((1 - rx, ry, -90), (1 - rx, 1 - ry, 0), (rx, 1 - ry, 90), (rx, ry, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append([cx + rx * math.cos(a), cy + ry * math.sin(a)])
    return pts


# --- Collages -----------------------------------------------------------------------------------

def collage_3_vertical():
    t = tall("r-collage-3-vertical", "Collage de 3 franjas", "Three-strip collage", "collage", 8.0, order=3100,
             tags=["collage", "tres fotos", "franjas", "vertical", "minimal"], thumb_at=4.0, background="#FFFFFF")
    bg(t, "#FFFFFF")
    g = 14
    h = (1920 - 4 * g) / 3
    _cells(t, [Box(g, g + i * (h + g), 1080 - 2 * g, h) for i in range(3)], ["beach-05", "coffee-03", "sunset-03"],
           motion="drop", step=0.4)
    label(t, t.track("text", "Texto"), "sol · café · mar", 1.6, 6.4, Box(60, 880, 960, 160), "DM Serif Display", 100,
          "#FFFFFF", weight=400, box_bg=("#111111", 0.7), box_pad=24, box_radius=20, anim_in=tanim("pop", duration=0.3),
          name="Texto")
    song(t, "calm", 2, 0.8)
    return t


def collage_2_mas_1():
    t = tall("r-collage-2-mas-1", "Collage 2 + 1", "Two plus one collage", "collage", 8.0, order=3101,
             tags=["collage", "fotos", "cuadrícula", "moderno", "aesthetic"], thumb_at=4.0, background="#F2EBE3")
    bg(t, "#F2EBE3")
    _cells(t, [Box(40, 160, 490, 700), Box(550, 160, 490, 700), Box(40, 880, 1000, 900)],
           ["fashion-02", "fashion-04", "portrait-08"], motion="snap", radius=36)
    label(t, t.track("text", "Texto"), "nueva temporada", 1.4, 6.6, Box(60, 40, 960, 110), "Bodoni Moda", 80, "#2B2118",
          weight=700, italic=True, anim_in=tanim("fade", duration=0.5), name="Texto")
    song(t, "jazz", 1, 0.8)
    return t


def mosaico_3x3():
    t = tall("r-mosaico-3x3", "Mosaico 3×3", "3x3 mosaic", "collage", 9.0, order=3102,
             tags=["mosaico", "nueve fotos", "cuadrícula", "grid", "instagram"], thumb_at=5.0, background="#111111")
    bg(t, "#111111")
    g = 10
    cw = (1080 - 4 * g) / 3
    ch = cw * 1.25
    y0 = (1920 - 3 * ch - 2 * g) / 2
    cells = [Box(g + c * (cw + g), y0 + r * (ch + g), cw, ch) for r in range(3) for c in range(3)]
    samples = ["friends-01", "food-03", "beach-02", "pet-02", "selfie-01", "city-03", "concert-02", "coffee-01", "nature-02"]
    order = [4, 0, 8, 2, 6, 1, 7, 3, 5]
    _cells(t, [cells[i] for i in order], [samples[i] for i in order], step=B, motion="snap")
    song(t, "upbeat", 3, 0.85)
    return t


def recortes_revista():
    t = tall("r-recortes-revista", "Recortes de revista", "Magazine cut-outs", "collage", 9.0, order=3103,
             tags=["revista", "recortes", "collage", "editorial", "letras recortadas"], thumb_at=5.6, background="#EDE6DA")
    bg(t, "#EDE6DA")
    rng = random.Random(3103)
    spots = [("portrait-08", centered(380, 600, 560, 720), -6), ("outfit-04", centered(760, 1050, 520, 680), 5),
             ("outfit-02", centered(360, 1440, 520, 560), -3)]
    for i, (s, box, r) in enumerate(spots):
        framed(t, s, 0.3 + i * 0.6, 8.7 - i * 0.6, box, [(0, {"s": 1.3}, "out"), (0.4, {})], border=10, radius=2,
               colour="#FFFFFF", rotation=keys([(0, r)]), label=f"Foto {i + 1}")
    word = ["Y", "O", " ", "S", "O", "Y"]
    bgs = ["#111111", "#E63946", "", "#FFD166", "#FFFFFF", "#1D3557"]
    fgs = ["#FFFFFF", "#FFFFFF", "", "#111111", "#111111", "#FFFFFF"]
    fonts = ["Bodoni Moda", "Anton", "", "Abril Fatface", "Bebas Neue", "Playfair Display"]
    x = 120
    for i, ch in enumerate(word):
        if ch == " ":
            x += 60
            continue
        at = 2.4 + i * 0.2
        box = Box(x, 200 + rng.uniform(-20, 20), 150, 190)
        r = rng.uniform(-10, 10)
        t.solid(t.track("shape", "Recorte"), bgs[i], at, 9.0 - at, box, [(0, {"s": 1.6}, "snap"), (0.2, {})],
                rotation=keys([(0, r)]), layers=[shadow("#000000", 3, 5, 6, 0.3), fill(bgs[i]), no_stroke()])
        label(t, t.track("text", "Letra"), ch, at, 9.0 - at, box, fonts[i], 150, fgs[i], weight=700, editable=False,
              motion=[(0, {"s": 1.6}, "snap"), (0.2, {})], rotation=keys([(0, r)]))
        x += 165
    label(t, t.track("text", "Texto"), "y me encanta", 3.8, 5.2, Box(560, 1500, 480, 200), "Permanent Marker", 84, "#E63946",
          weight=400, anim_in=tanim("wipe", duration=0.5, angle=0), rotation=keys([(0, -6)]), name="Texto")
    song(t, "upbeat", 7, 0.8)
    return t


def marco_camara():
    t = tall("r-marco-camara", "Marco de cámara", "Camera frame", "collage", 8.0, order=3104,
             tags=["cámara", "marco", "foto", "visor", "fotografía"], thumb_at=4.0, background="#1E1E1E")
    bg(t, "#1E1E1E")
    rrect(t, t.track("shape", "Cuerpo"), "#2E2E2E", 0, 8.0, Box(40, 340, 1000, 1240), 60,
          layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#2E2E2E"), no_stroke()])
    samples = ["nature-01", "city-02", "pet-05", "friends-04"]
    for i, s in enumerate(samples):
        at = i * 2.0
        t.photo(t.track("video", "Fotos") if i == 0 else ph, s, at, 2.0, Box(100, 400, 880, 1000), label=f"Foto {i + 1}")
        if i == 0:
            ph = t.tracks[-1]
        flash(t, at, 0.2, peak=0.8)
    for (x, y) in ((140, 440), (940, 440), (140, 1360), (940, 1360)):
        t.solid(t.track("shape", "Esquina"), "#FFFFFF", 0, 8.0, centered(x, y, 60, 6))
        t.solid(t.track("shape", "Esquina"), "#FFFFFF", 0, 8.0, centered(x + (-27 if x > 540 else 27), y + (27 if y < 900 else -27), 6, 60))
    t.solid(t.track("shape", "Botón"), "#E63946", 0, 8.0, centered(540, 1500, 120, 120), kind="ellipse",
            layers=[shadow("#000000", 0, 6, 12, 0.5), fill("#E63946"), stroke(8, "#FFFFFF")])
    label(t, t.track("text", "Texto"), "click, click", 0.2, 7.8, Box(60, 120, 960, 160), "Caveat", 120, "#FFFFFF",
          weight=700, anim_in=tanim("typewriter", duration=0.6, unit="character"), name="Texto")
    song(t, "fun", 1, 0.8)
    return t


def tablero_corcho():
    t = tall("r-tablero-corcho", "Tablero de corcho", "Cork board", "collage", 10.0, order=3105,
             tags=["corcho", "tablero", "fotos", "chinchetas", "recuerdos"], thumb_at=7.0, background="#B98A5B")
    bg_gradient(t, [(0, "#C59A6D"), (1, "#A9784A")], angle=135)
    rng = random.Random(3105)
    for k in range(120):
        t.solid(t.track("shape", "Grano") if k % 40 == 0 else gr, "#8C5E34", 0, 10.0,
                centered(rng.uniform(0, 1080), rng.uniform(0, 1920), 6, 6), kind="ellipse", alpha=0.5)
        if k % 40 == 0:
            gr = t.tracks[-1]
    spots = [("friends-02", centered(330, 450, 460, 560), -7), ("travel-03", centered(770, 560, 440, 520), 6),
             ("concert-01", centered(340, 1080, 440, 520), 4), ("family-02", centered(760, 1180, 460, 560), -5),
             ("pet-04", centered(540, 1650, 480, 420), 2)]
    for i, (s, box, r) in enumerate(spots):
        at = 0.3 + i * 0.7
        framed(t, s, at, 10.0 - at, box, [(0, {"s": 1.25}, "out"), (0.35, {})], border=14, colour="#FFFFFF",
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
        t.solid(t.track("shape", "Chincheta"), ["#E63946", "#FFD166", "#06D6A0", "#118AB2", "#EF476F"][i], at + 0.3,
                9.7 - at, centered(box.cx, box.y - 4, 40, 40), pop(0, 0.25), kind="ellipse",
                layers=[shadow("#000000", 2, 6, 6, 0.4), fill(["#E63946", "#FFD166", "#06D6A0", "#118AB2", "#EF476F"][i]),
                        no_stroke()])
    label(t, t.track("text", "Nota"), "2026 ✓", 3.6, 6.4, Box(700, 1560, 340, 150), "Permanent Marker", 84, "#2B2118",
          weight=400, box_bg=("#FFF59D", 1.0), box_pad=16, anim_in=tanim("pop", duration=0.3), rotation=keys([(0, 6)]),
          name="Nota")
    song(t, "upbeat", 6, 0.8)
    return t


def tarjetas_apiladas():
    t = tall("r-tarjetas-apiladas", "Tarjetas apiladas", "Stacked cards", "collage", 9.0, order=3106,
             tags=["tarjetas", "pila", "deslizar", "fotos", "swipe"], thumb_at=3.2, background="#14213D")
    bg_gradient(t, [(0, "#1F2F57"), (1, "#0B132B")], angle=90)
    samples = ["portrait-01", "portrait-03", "portrait-05", "portrait-07", "portrait-02"]
    n = len(samples)
    for i, s in enumerate(samples):
        depth = n - 1 - i
        box = centered(540, 900 + depth * 40, 820 - depth * 50, 1180 - depth * 60)
        leave = 1.5 + depth * 1.5 if depth else None
        mo = [(0, {"dy": 900}, "out"), (0.5 + i * 0.1, {})]
        if depth:
            mo += [(leave - 0.4, {}, "in"), (leave, {"dx": 1300 if depth % 2 else -1300, "dy": -200})]
        dur = leave if depth else 9.0
        rot = keys([(0, (-1) ** i * 3, "hold"), ((leave or 9.0) - 0.4, (-1) ** i * 3), ((leave or 9.0), (-1) ** i * 25)]) \
            if depth else keys([(0, 0)])
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0, dur, Box(box.x - 12, box.y - 12, box.w + 24, box.h + 24), 44, mo,
              layers=[shadow("#000000", 0, 20, 40, 0.45), fill("#FFFFFF"), no_stroke()], rotation=rot)
        t.photo(t.track("video", f"Foto {i + 1}"), s, 0, dur, box, mo, label=f"Foto {i + 1}", rotation=rot)
    label(t, t.track("text", "Texto"), "desliza →", 0.6, 8.4, Box(60, 1680, 960, 120), "DM Sans", 72, "#FFFFFF", weight=800,
          anim_loop=tanim("float", amount=0.2, speed=0.8), name="Texto")
    song(t, "electro", 3, 0.8)
    return t


def collage_circulos():
    t = tall("r-collage-circulos", "Collage de círculos", "Circle collage", "collage", 9.0, order=3107,
             tags=["círculos", "collage", "redondo", "colores", "fotos"], thumb_at=5.0, background="#FFF1E6")
    bg(t, "#FFF1E6")
    spots = [(330, 420, 520, "#F28482"), (790, 820, 440, "#84A59D"), (300, 1150, 420, "#F6BD60"), (760, 1520, 520, "#F5CAC3")]
    samples = ["kids-02", "family-03", "baby-02", "mother-06"]
    for i, ((x, y, s, c), smp) in enumerate(zip(spots, samples)):
        at = 0.3 + i * 0.6
        t.solid(t.track("shape", "Fondo"), c, at, 9.0 - at, centered(x + 30, y + 30, s, s), pop(0, 0.5), kind="ellipse")
        circle_photo(t, smp, at + 0.1, 8.9 - at, centered(x, y, s, s), pop(0, 0.5), label=f"Foto {i + 1}")
    label(t, t.track("text", "Texto"), "mi gente", 2.4, 6.6, Box(500, 200, 540, 160), "Pacifico", 110, "#84A59D",
          weight=400, anim_in=tanim("pop", duration=0.4), rotation=keys([(0, -6)]), name="Texto")
    song(t, "fun", 2, 0.8)
    return t


def fotomaton():
    t = tall("r-fotomaton", "Tira de fotomatón", "Photo booth strip", "collage", 8.0, order=3108,
             tags=["fotomatón", "tira", "photobooth", "amigos", "pareja"], thumb_at=5.0, background="#E63946")
    bg(t, "#E63946")
    for k in range(10):
        t.solid(t.track("shape", "Cortina"), "#C1121F", 0, 8.0, Box(k * 108, 0, 54, 1920))
    rrect(t, t.track("shape", "Tira"), "#FFFFFF", 0.2, 7.8, Box(270, 120, 540, 1680), 8, slide_in(dy=-1900, length=0.6),
          layers=[shadow("#000000", 0, 20, 40, 0.5), fill("#FFFFFF"), no_stroke()], rotation=keys([(0, -3)]))
    samples = ["couple-07", "friends-05", "couple-03", "friends-08"]
    for i, s in enumerate(samples):
        at = 0.9 + i * 0.9
        t.photo(t.track("video", f"Cuadro {i + 1}"), s, at, 8.0 - at, Box(310, 160 + i * 400, 460, 370), label=f"Foto {i + 1}",
                rotation=keys([(0, -3)]), opacity=keys([(0, 0.0), (0.1, 1.0)]),
                effects=[effect("color.basic", saturation=-1.0, contrast=0.2)])
        flash(t, at, 0.2, peak=0.9)
    label(t, t.track("text", "Pie"), "sonríe ✦", 4.2, 3.8, Box(300, 1760, 480, 80), "Caveat", 64, "#E63946", weight=700,
          rotation=keys([(0, -3)]), anim_in=tanim("fade", duration=0.4), name="Pie")
    song(t, "fun", 3, 0.8)
    return t


def album_stickers():
    t = tall("r-album-stickers", "Álbum con stickers", "Sticker album", "collage", 9.0, order=3109,
             tags=["álbum", "stickers", "scrapbook", "lindo", "diario"], thumb_at=6.0, background="#FCEFF9")
    bg(t, "#FCEFF9")
    for k in range(16):
        t.solid(t.track("shape", "Puntos") if k == 0 else dotsk, "#F3C4E5", 0, 9.0, Box(0, 120 * k, 1080, 4), alpha=0.6)
        if k == 0:
            dotsk = t.tracks[-1]
    spots = [("selfie-02", Box(110, 260, 520, 620), -4), ("icecream-02", Box(560, 640, 440, 520), 5),
             ("friends-06", Box(130, 1160, 600, 520), 3)]
    for i, (s, box, r) in enumerate(spots):
        framed(t, s, 0.3 + i * 0.7, 8.7 - i * 0.7, box, [(0, {"s": 1.3}, "out"), (0.4, {})], border=16, radius=24,
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
    stickers = [("🌈", 880, 330), ("🦋", 140, 980), ("🍦", 900, 1300), ("💫", 640, 220), ("🌷", 860, 1700), ("😎", 450, 1720)]
    for i, (g, x, y) in enumerate(stickers):
        label(t, t.track("text", "Sticker"), g, 2.4 + i * 0.25, 6.6 - i * 0.25, centered(x, y, 200, 200), "Inter", 140,
              "#000000", weight=400, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.35, {})],
              rotation=keys([(0, (-1) ** i * 10)]))
    label(t, t.track("text", "Texto"), "días bonitos", 1.0, 8.0, Box(60, 80, 960, 160), "Sniglet", 100, "#C2185B", weight=800,
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Texto")
    song(t, "fun", 4, 0.8)
    return t


def pantalla_celular():
    t = tall("r-pantalla-celular", "Pantalla de celular", "Phone screen", "collage", 9.0, order=3110,
             tags=["celular", "teléfono", "galería", "pantalla", "fotos"], thumb_at=5.0, background="#DCE6F2")
    bg_gradient(t, [(0, "#E3ECF7"), (1, "#C9D6E8")], angle=90)
    rrect(t, t.track("shape", "Teléfono"), "#111111", 0.2, 8.8, centered(540, 980, 760, 1560), 110, pop(0, 0.5, 0.8),
          layers=[shadow("#000000", 0, 30, 60, 0.4), fill("#111111"), no_stroke()])
    samples = ["beach-03", "food-02", "friends-07", "sunset-01"]
    for i, s in enumerate(samples):
        at = 0.6 + i * 2.0
        t.photo(t.track("video", "Pantalla") if i == 0 else sc, s, at, min(2.0, 9.0 - at) if i < 3 else 9.0 - at,
                centered(540, 980, 700, 1500), [(0, {"dx": 700}, "out"), (0.4, {})], label=f"Foto {i + 1}")
        if i == 0:
            sc = t.tracks[-1]
    t.solid(t.track("shape", "Isla"), "#111111", 0.6, 8.4, centered(540, 285, 220, 56), radius=28, kind="rounded-rectangle")
    for k in range(4):
        t.solid(t.track("shape", "Puntos"), "#FFFFFF", 0.6 + k * 2.0, min(2.0, 8.4 - k * 2.0) if k < 3 else 8.4 - k * 2.0,
                centered(486 + k * 36, 1680, 14, 14), kind="ellipse")
    label(t, t.track("text", "Texto"), "mi galería este mes", 0.8, 8.0, Box(60, 60, 960, 130), "DM Sans", 72, "#1D3557",
          weight=800, anim_in=tanim("fade", duration=0.4), name="Texto")
    song(t, "upbeat", 5, 0.8)
    return t


def diario_cinta():
    t = tall("r-diario-cinta", "Diario con cinta", "Taped diary", "collage", 10.0, order=3111,
             tags=["diario", "cinta", "journal", "notas", "scrapbook"], thumb_at=6.5, background="#FBF6EC")
    bg(t, "#FBF6EC")
    for k in range(22):
        t.solid(t.track("shape", "Renglón") if k == 0 else rl, "#D9E3EA", 0, 10.0, Box(0, 120 + k * 82, 1080, 3))
        if k == 0:
            rl = t.tracks[-1]
    spots = [("coffee-02", Box(90, 220, 480, 560), -3), ("reading-03", Box(520, 760, 470, 560), 4)]
    for i, (s, box, r) in enumerate(spots):
        framed(t, s, 0.3 + i * 1.0, 9.7 - i * 1.0, box, [(0, {"s": 1.2}, "out"), (0.4, {})], border=12, colour="#FFFFFF",
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
        t.solid(t.track("shape", "Cinta"), ["#F7C8A0", "#BDE0FE"][i], 0.7 + i * 1.0, 9.3 - i * 1.0,
                centered(box.cx, box.y - 6, 220, 60), pop(0, 0.3), alpha=0.8, rotation=keys([(0, r - 8)]))
    notes = [("hoy:", 600, 300), ("café con calma", 600, 380), ("terminé mi libro", 90, 900), ("y respiré ✿", 90, 990)]
    for i, (txt, x, y) in enumerate(notes):
        label(t, t.track("text", "Nota"), txt, 1.0 + i * 0.9, 9.0 - i * 0.9, Box(x, y, 460, 90), "Gloria Hallelujah", 56,
              "#3D405B", weight=400, align="left", anim_in=tanim("typewriter", duration=0.6, unit="character"),
              name=f"Nota {i + 1}")
    label(t, t.track("text", "Fecha"), "lunes 12", 0.2, 9.8, Box(560, 1500, 460, 140), "Caveat", 110, "#E07A5F", weight=700,
          rotation=keys([(0, -4)]), anim_in=tanim("fade", duration=0.4), name="Fecha")
    song(t, "calm", 1, 0.8)
    return t


def rejilla_bordes():
    t = tall("r-rejilla-bordes", "Rejilla de bordes gruesos", "Bold border grid", "collage", 8.0, order=3112,
             tags=["rejilla", "bordes", "brutalista", "colores", "collage"], thumb_at=4.6, background="#111111")
    bg(t, "#FFE600")
    g = 28
    cells = [Box(g, g, 1080 - 2 * g, 720), Box(g, 720 + 2 * g, (1080 - 3 * g) / 2, 560),
             Box(g * 2 + (1080 - 3 * g) / 2, 720 + 2 * g, (1080 - 3 * g) / 2, 560), Box(g, 1280 + 3 * g, 1080 - 2 * g, 1920 - 1280 - 4 * g)]
    _cells(t, cells, ["skate-03", "night-02", "friends-12", "city-04"], motion="snap", step=B)
    for c in cells:
        outline(t, t.track("shape", "Borde"), "#111111", 12, 0, 8.0, c)
    label(t, t.track("text", "Texto"), "CALLE", 2.0, 6.0, Box(g, 1280 + 3 * g, 1080 - 2 * g, 1920 - 1280 - 4 * g), "Anton",
          220, "#FFE600", weight=400, spacing=20, layers=[stroke(10, "#111111"), fill("#FFE600")],
          anim_in=tanim("stamp", duration=0.3), name="Texto")
    song(t, "electro", 1, 0.85)
    return t


def carrusel():
    t = tall("r-carrusel", "Carrusel que pasa", "Sliding carousel", "collage", 10.0, order=3113,
             tags=["carrusel", "deslizar", "fotos", "galería", "instagram"], thumb_at=3.0, background="#F5F5F5")
    bg(t, "#F5F5F5")
    samples = ["skincare-02", "skincare-03", "box-02", "handmade-01", "shopping-02"]
    strip = []
    for i in range(len(samples)):
        x = 140 + i * 860
        steps = [(0, {"dx": 0}, "hold")]
        for k in range(1, len(samples)):
            steps += [(k * 2.0 - 0.4, {"dx": -(k - 1) * 860}, "inout"), (k * 2.0, {"dx": -k * 860}, "hold")]
        strip.append((Box(x, 380, 800, 1000), steps))
    for i, (s, (box, steps)) in enumerate(zip(samples, strip)):
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0, 10.0, Box(box.x - 10, box.y - 10, box.w + 20, box.h + 20), 40, steps,
              layers=[shadow("#000000", 0, 16, 30, 0.18), fill("#FFFFFF"), no_stroke()])
        clip = t.photo(t.track("video", f"Foto {i + 1}"), s, 0, 10.0, box, steps, label=f"Foto {i + 1}")
        t.mask(t.tracks[-1], clip, "freeform", points=_round_rect_points(30 / 800, 30 / 1000), smooth=False)
    for k in range(len(samples)):
        t.solid(t.track("shape", "Indicador"), "#BBBBBB", 0, 10.0, centered(468 + k * 36, 1460, 16, 16), kind="ellipse")
        t.solid(t.track("shape", "Indicador"), "#111111", k * 2.0, 2.0, centered(468 + k * 36, 1460, 16, 16), kind="ellipse")
    label(t, t.track("text", "Texto"), "nueva colección", 0.2, 9.8, Box(60, 180, 960, 120), "DM Sans", 80, "#111111",
          weight=800, anim_in=tanim("fade", duration=0.4), name="Texto")
    label(t, t.track("text", "Sub"), "desliza para ver todo", 0.4, 9.6, Box(60, 1540, 960, 80), "DM Sans", 44, "#777777",
          weight=500, anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    song(t, "jazz", 0, 0.75)
    return t


def foto_en_foto():
    t = tall("r-foto-en-foto", "Foto dentro de foto", "Picture in picture", "collage", 8.0, order=3114,
             tags=["foto en foto", "pip", "detalle", "zoom", "collage"], thumb_at=4.0)
    photo_bg(t, "restaurant-03", s1=1.08, label="Foto grande", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=14)])
    shade_full(t, 0.25)
    framed(t, "restaurant-03", 0.4, 7.6, Box(140, 380, 800, 1000), [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"),
                                                                   (7.6, {"s": 1.04})], border=14, radius=30,
           label="Foto", reuse="p1")
    framed(t, "restaurant-05", 1.6, 6.4, Box(560, 1150, 400, 480), [(0, {"s": 0.0}, "back"), (0.45, {})], border=10, radius=24,
           rotation=keys([(0, 6)]), label="Detalle")
    label(t, t.track("text", "Texto"), "el detalle lo es todo", 2.4, 5.6, Box(60, 160, 960, 160), "DM Serif Display", 90,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.5), name="Texto")
    song(t, "jazz", 2, 0.75)
    return t


# --- Before and after ---------------------------------------------------------------------------

def _before_after(t, before, after, labels=("ANTES", "DESPUÉS"), at=2.5, colours=("#111111", "#00C2A8"),
                  before_fx=None, wipe="vertical"):
    """Before fills the frame, then a wipe uncovers after (vertical: left to right; horizontal: top down)."""
    t.photo(t.track("video", "Después"), after, 0, t.duration, t.full, kb(t.duration, 1.0, 1.05), label="Foto de después")
    host = t.track("video", "Antes")
    extra = {"effects": before_fx} if before_fx else {}
    clip = t.photo(host, before, 0, t.duration, t.full, kb(t.duration, 1.0, 1.05), label="Foto de antes", **extra)
    if wipe == "vertical":
        t.mask(host, clip, "rectangle", keyframes={"w": keys([(0, 1.0, "hold"), (at, 1.0, "inout"), (at + 1.2, 0.0)]),
                                                   "x": keys([(0, 0.5, "hold"), (at, 0.5, "inout"), (at + 1.2, 1.0)])})
        t.solid(t.track("shape", "Línea"), "#FFFFFF", 0, t.duration, Box(0, 0, 10, 1920),
                [(0, {"dx": -10}, "hold"), (at, {"dx": 0}, "inout"), (at + 1.2, {"dx": 1080})])
    else:
        t.mask(host, clip, "rectangle", keyframes={"h": keys([(0, 1.0, "hold"), (at, 1.0, "inout"), (at + 1.2, 0.0)]),
                                                   "y": keys([(0, 0.5, "hold"), (at, 0.5, "inout"), (at + 1.2, 1.0)])})
        t.solid(t.track("shape", "Línea"), "#FFFFFF", 0, t.duration, Box(0, 0, 1080, 10),
                [(0, {"dy": -10}, "hold"), (at, {"dy": 0}, "inout"), (at + 1.2, {"dy": 1920})])
    for i, (txt, c) in enumerate(zip(labels, colours)):
        t0 = 0.2 if i == 0 else at + 1.2
        d = at + 0.9 - t0 if i == 0 else t.duration - t0
        pill(t, t.track("shape", "Etiqueta"), c, t0, d, Box(60, 140, 440, 110), pop(0, 0.3))
        label(t, t.track("text", "Etiqueta"), txt, t0, d, Box(60, 140, 440, 110), "Montserrat", 54, "#FFFFFF", weight=800,
              spacing=4, name=f"Etiqueta {i + 1}")


def ba_cortina():
    t = tall("r-ba-cortina", "Antes y después: cortina", "Before/after curtain", "beforeafter", 7.0, order=3115,
             tags=["antes y después", "cortina", "transformación", "cambio"], thumb_at=3.1, background="#000000")
    _before_after(t, "interior-02", "interior-06", before_fx=[effect("color.basic", saturation=-0.5, exposure=-0.1)])
    song(t, "upbeat", 7, 0.8)
    return t


def ba_dia_1_100():
    t = tall("r-ba-dia-1-100", "Día 1 / Día 100", "Day 1 / Day 100", "beforeafter", 8.0, order=3116,
             tags=["día 1", "día 100", "progreso", "reto", "transformación"], thumb_at=4.6, background="#000000")
    _before_after(t, "gym-04", "gym-02", labels=("DÍA 1", "DÍA 100"), at=3.0, colours=("#555555", "#E10600"),
                  before_fx=[effect("color.basic", saturation=-1.0)], wipe="horizontal")
    label(t, t.track("text", "Texto"), "no te rindas", 4.4, 3.6, Box(60, 1640, 960, 160), "Anton", 130, "#FFFFFF", weight=400,
          spacing=4, layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          name="Texto")
    song(t, "epic", 6, 0.85)
    return t


def ba_maquillaje():
    t = tall("r-ba-maquillaje", "Antes y después: maquillaje", "Make-up before/after", "beforeafter", 7.0, order=3117,
             tags=["maquillaje", "antes y después", "belleza", "look", "makeup"], thumb_at=3.3, background="#000000")
    _before_after(t, "portrait-04", "makeup-02", labels=("SIN MAQUILLAJE", "LOOK FINAL"), colours=("#9E9E9E", "#E5486F"))
    t.adjust([effect("bling_sparkle", animated={"intensity": keys([(0, 0.0, "hold"), (3.7, 0.0, "smooth"), (4.2, 0.6)])},
                     threshold=0.7, density=0.35)], name="Destellos")
    song(t, "upbeat", 1, 0.8)
    return t


def ba_casa():
    t = tall("r-ba-casa", "Antes y después: mi casa", "Home makeover", "beforeafter", 8.0, order=3118,
             tags=["casa", "remodelación", "antes y después", "decoración", "hogar"], thumb_at=3.6, background="#000000")
    _before_after(t, "kitchen-old-01", "interior-07", at=2.8, before_fx=[effect("color.basic", saturation=-0.4,
                                                                                 exposure=-0.15)])
    label(t, t.track("text", "Texto"), "3 semanas de trabajo", 4.2, 3.8, Box(60, 1660, 960, 140), "Montserrat", 72, "#FFFFFF",
          weight=800, box_bg=("#000000", 0.55), box_pad=20, box_radius=18, anim_in=tanim("fade", duration=0.4), name="Texto")
    song(t, "upbeat", 2, 0.8)
    return t


def ba_jardin():
    t = tall("r-ba-jardin", "Antes y después: jardín", "Garden before/after", "beforeafter", 7.0, order=3119,
             tags=["jardín", "plantas", "antes y después", "huerto", "verde"], thumb_at=3.2, background="#000000")
    _before_after(t, "garden-03", "garden-01", colours=("#8D6E63", "#43A047"), wipe="horizontal",
                  before_fx=[effect("color.basic", saturation=-0.6, temperature=0.2)])
    song(t, "calm", 3, 0.8)
    return t


def ba_peinado():
    t = tall("r-ba-peinado", "Antes y después: peinado", "Hair before/after", "beforeafter", 7.0, order=3120,
             tags=["peinado", "pelo", "salón", "antes y después", "corte"], thumb_at=3.2, background="#000000")
    _before_after(t, "salon-03", "salon-01", labels=("ANTES", "¡NUEVO LOOK!"), colours=("#6D597A", "#F28482"))
    song(t, "upbeat", 4, 0.8)
    return t


def ba_mascota():
    t = tall("r-ba-mascota", "De cachorro a grande", "Puppy to grown-up", "beforeafter", 8.0, order=3121,
             tags=["mascota", "cachorro", "perro", "crecer", "antes y después"], thumb_at=3.8, background="#000000")
    _before_after(t, "puppy-02", "pet-05", labels=("2 MESES", "2 AÑOS"), at=2.6, colours=("#F4A261", "#2A9D8F"))
    label(t, t.track("text", "Texto"), "creció tan rápido 🥹", 4.0, 4.0, Box(60, 1660, 960, 140), "Fredoka", 80, "#FFFFFF",
          weight=700, layers=[shadow("#000000", 0, 4, 14, 0.6), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.3),
          name="Texto")
    song(t, "fun", 1, 0.8)
    return t


def ba_cocina():
    t = tall("r-ba-cocina", "Antes y después: receta", "Recipe before/after", "beforeafter", 7.0, order=3122,
             tags=["receta", "cocina", "ingredientes", "plato", "antes y después"], thumb_at=3.3, background="#000000")
    _before_after(t, "cooking-02", "restaurant-01", labels=("INGREDIENTES", "RESULTADO"), colours=("#7C2D12", "#F59E0B"),
                  wipe="horizontal")
    song(t, "jazz", 1, 0.8)
    return t


def ba_auto():
    t = tall("r-ba-auto", "Antes y después: auto", "Car before/after", "beforeafter", 7.0, order=3123,
             tags=["auto", "carro", "lavado", "taller", "antes y después"], thumb_at=3.3, background="#000000")
    _before_after(t, "mechanic-03", "mechanic-02", labels=("ANTES", "COMO NUEVO"), colours=("#424242", "#1E88E5"),
                  before_fx=[effect("color.basic", saturation=-0.7, contrast=-0.1)])
    song(t, "epic", 2, 0.8)
    return t


def ba_dibujo():
    t = tall("r-ba-dibujo", "Del boceto al color", "Sketch to colour", "beforeafter", 7.0, order=3124,
             tags=["dibujo", "arte", "boceto", "pintura", "proceso"], thumb_at=3.2, background="#000000")
    _before_after(t, "handmade-02", "handmade-01", labels=("BOCETO", "TERMINADO"), colours=("#757575", "#8E24AA"),
                  before_fx=[effect("color.basic", saturation=-1.0, contrast=0.3, exposure=0.15)])
    song(t, "calm", 4, 0.8)
    return t


# --- Celebrations -------------------------------------------------------------------------------

def _party_title(t, text, t0, box, font, size, colour, shadow_c="#000000", **kw):
    label(t, t.track("text", "Título"), text, t0, t.duration - t0, box, font, size, colour, weight=kw.pop("weight", 400),
          layers=[shadow(shadow_c, 0, 8, 0, 0.9), fill(colour)], anim_in=tanim(kw.pop("anim", "pop"), duration=0.5),
          name="Título", **kw)


def cumple_infantil():
    t = tall("r-cumple-infantil", "Cumpleaños infantil", "Kids' birthday", "celebration", 10.0, order=3125,
             tags=["cumpleaños", "niños", "infantil", "fiesta", "globos"], thumb_at=5.0, background="#8ECAE6")
    bg_gradient(t, [(0, "#A8DADC"), (1, "#FFE5EC")], angle=90)
    rng = random.Random(3125)
    for k in range(9):
        x, s = rng.uniform(80, 1000), rng.uniform(130, 190)
        c = rng.choice(["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93"])
        at = rng.uniform(0, 1.5)
        mo = [(0, {"dy": 1400}, "out"), (2.4, {}, "smooth"), (10.0 - at, {"dy": -80})]
        t.solid(t.track("shape", "Cordel"), "#FFFFFF", at, 10.0 - at, Box(x - 1, 300 + s * 0.6, 3, 300), mo, alpha=0.8)
        t.solid(t.track("shape", "Globo"), c, at, 10.0 - at, centered(x, 300, s, s * 1.2), mo, kind="ellipse",
                layers=[gradient([(0, "#FFFFFF", 0.55), (0.35, c), (1, c)], angle=135), no_stroke()])
    framed(t, "kids-01", 0.8, 9.2, centered(540, 1050, 760, 860), [(0, {"s": 0.6}, "back"), (0.5, {}, "linear"),
                                                                    (9.2, {"s": 1.03})], border=20, radius=40,
           rotation=keys([(0, -3)]), label="Foto del cumpleañero")
    _party_title(t, "¡Tomás cumple 5!", 1.2, Box(40, 1520, 1000, 220), "Chewy", 130, "#FF595E", shadow_c="#FFFFFF")
    confetti(t, ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4"], 1.2, 8.8, seed=3125, lanes=4, density=0.3)
    song(t, "fun", 0, 0.85)
    return t


def cumple_adulto():
    t = tall("r-cumple-adulto", "Cumpleaños elegante", "Elegant birthday", "celebration", 10.0, order=3126,
             tags=["cumpleaños", "elegante", "dorado", "40", "50", "fiesta"], thumb_at=5.6, background="#0B0B0B")
    bg_gradient(t, [(0, "#1A1A1A"), (1, "#050505")], angle=90)
    dots(t, ["#E8C27A", "#FFFFFF"], 30, 0, 10.0, seed=3126, size=(6, 14), kinds=("star", "ellipse"), drift=60)
    t.photo(t.track("video", "Foto"), "man-03", 0.3, 9.7, Box(140, 300, 800, 1000), kb(9.7, 1.0, 1.05), label="Foto",
            effects=[effect("color.basic", contrast=0.15)])
    outline(t, t.track("shape", "Marco"), "#E8C27A", 4, 0.6, 9.4, Box(110, 270, 860, 1060), alpha=0.9)
    label(t, t.track("text", "Edad"), "40", 1.2, 8.8, Box(60, 1280, 960, 340), "Playfair Display", 300, "#E8C27A", weight=800,
          layers=[glow("#E8C27A", 20, 0.5), gradient([(0, "#FFF4D6"), (0.5, "#E8C27A"), (1, "#B8892E")], angle=90)],
          anim_in=tanim("zoom-out", duration=0.6), name="Edad")
    label(t, t.track("text", "Nombre"), "Feliz cumpleaños, Andrés", 1.8, 8.2, Box(60, 1620, 960, 120), "Cormorant Garamond",
          70, "#FFFFFF", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Nombre")
    t.adjust([effect("bling_sparkle", intensity=0.6, threshold=0.65, density=0.35)], name="Destellos")
    song(t, "jazz", 0, 0.8)
    return t


def cumple_mama():
    t = tall("r-cumple-mama", "Cumpleaños de mamá", "Mum's birthday", "celebration", 10.0, order=3127,
             tags=["cumpleaños", "mamá", "madre", "flores", "familia"], thumb_at=6.0, background="#FFF0F3")
    bg(t, "#FFF0F3")
    slides(t, ["mother-01", "mother-03", "mother-07", "mother-05"], 0.0, 2.5, Box(90, 240, 900, 1100), transition="crossfade",
           tdur=0.5, kb_amount=0.06)
    outline(t, t.track("shape", "Marco"), "#E5989B", 6, 0, 10.0, Box(70, 220, 940, 1140), radius=40)
    for i, (x, y) in enumerate([(120, 250), (960, 1330), (980, 260), (110, 1320)]):
        label(t, t.track("text", "Flor"), "🌸", 0.3 + i * 0.2, 9.7 - i * 0.2, centered(x, y, 180, 180), "Inter", 130, "#000000",
              weight=400, editable=False, motion=pop(0, 0.4))
    label(t, t.track("text", "Título"), "Feliz cumple, mamá", 1.0, 9.0, Box(60, 1420, 960, 200), "Dancing Script", 120,
          "#B5525F", weight=700, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Título")
    label(t, t.track("text", "Mensaje"), "eres mi lugar favorito", 2.4, 7.6, Box(60, 1630, 960, 90), "Cormorant Garamond", 64,
          "#6D2E46", weight=600, italic=True, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "romantic", 3, 0.8)
    return t


def pastel_velas():
    t = tall("r-pastel-velas", "Pastel y velas", "Cake and candles", "celebration", 8.0, order=3128,
             tags=["pastel", "velas", "cumpleaños", "deseo", "soplar"], thumb_at=4.6, background="#120A06")
    photo_bg(t, "cake-02", s1=1.06, label="Foto del pastel")
    shade_full(t, 0.25, colour="#120A06")
    t.solid(t.track("shape", "Calidez"), "#FFB347", 0, 8.0, centered(540, 1000, 1200, 1200), kind="ellipse",
            layers=[gradient([(0, "#FFB347", 0.35), (1, "#FFB347", 0.0)], angle=0), no_stroke()],
            opacity=blink(8.0, 0.3, 0.75))
    label(t, t.track("text", "Deseo"), "pide un deseo…", 0.5, 3.5, Box(60, 260, 960, 180), "Dancing Script", 120, "#FFF4D6",
          weight=700, layers=[glow("#FFB347", 18, 0.7), fill("#FFF4D6")], anim_in=tanim("blur-in", duration=0.8),
          anim_out=tanim("fade", duration=0.4), name="Primera frase")
    t.solid(t.track("shape", "Soplido"), "#000000", 4.0, 0.6, opacity=keys([(0, 0.0, "smooth"), (0.3, 0.75, "smooth"), (0.6, 0.3)]))
    label(t, t.track("text", "Felicidades"), "¡Feliz cumpleaños!", 4.3, 3.7, Box(60, 820, 960, 260), "Pacifico", 120, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 6, 18, 0.6), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.5),
          name="Felicidades")
    confetti(t, ["#FFD166", "#FFFFFF", "#EF476F", "#06D6A0"], 4.3, 3.7, seed=3128, lanes=4, density=0.25)
    song(t, "fun", 4, 0.8)
    return t


def aniversario_bodas():
    t = tall("r-aniversario-bodas", "Aniversario de bodas", "Wedding anniversary", "celebration", 10.0, order=3129,
             tags=["aniversario", "bodas", "pareja", "años", "matrimonio"], thumb_at=6.0, background="#F7F1E8")
    bg(t, "#F7F1E8")
    framed(t, "wedding-03", 0.3, 9.7, Box(120, 200, 520, 680), [(0, {"s": 1.2}, "out"), (0.5, {})], border=16,
           rotation=keys([(0, -4)]), label="Foto de la boda", reuse=None)
    framed(t, "couple-08", 1.4, 8.6, Box(440, 760, 540, 700), [(0, {"s": 1.2}, "out"), (0.5, {})], border=16,
           rotation=keys([(0, 4)]), label="Foto de hoy")
    label(t, t.track("text", "Antes"), "2001", 0.8, 9.2, Box(660, 380, 380, 140), "Playfair Display", 110, "#B89B5E",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Año de la boda")
    label(t, t.track("text", "Ahora"), "2026", 1.9, 8.1, Box(60, 1060, 380, 140), "Playfair Display", 110, "#B89B5E",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Año de hoy")
    label(t, t.track("text", "Título"), "25 años juntos", 2.8, 7.2, Box(60, 1540, 960, 180), "Great Vibes", 140, "#6B4F2E",
          weight=400, anim_in=tanim("blur-in", duration=1.0), name="Título")
    song(t, "romantic", 4, 0.8)
    return t


def primera_cita():
    t = tall("r-primera-cita", "Nuestra primera cita", "Our first date", "celebration", 9.0, order=3130,
             tags=["primera cita", "pareja", "amor", "recuerdo", "aniversario"], thumb_at=5.4, background="#2D0A1E")
    slides(t, ["restaurant-04", "couple-05", "night-02"], 0.0, 3.0, transition="blur_dissolve", tdur=0.6, kb_amount=0.07,
           effects_fn=lambda i: [effect("color.basic", temperature=0.15, fade=0.1)])
    shade_full(t, 0.3, colour="#2D0A1E")
    label(t, t.track("text", "Fecha"), "14 · 02 · 2024", 0.4, 8.6, Box(60, 260, 960, 90), "Special Elite", 64, "#FFE3EA",
          weight=400, spacing=6, anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Fecha")
    label(t, t.track("text", "Título"), "el día que\ntodo empezó", 1.4, 7.6, Box(60, 1300, 960, 360), "DM Serif Display",
          120, "#FFFFFF", weight=400, line=1.0, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15),
          name="Título")
    dots(t, ["#FF8FA3", "#FFFFFF"], 16, 1.0, 8.0, seed=3130, size=(28, 54), kinds=("heart",), drift=180, alpha=0.8)
    song(t, "romantic", 2, 0.8)
    return t


def propuesta():
    t = tall("r-propuesta", "¡Dijo que sí!", "She said yes!", "celebration", 8.0, order=3131,
             tags=["propuesta", "compromiso", "anillo", "dijo que sí", "pareja"], thumb_at=4.6, background="#000000")
    slides(t, ["proposal-02", "proposal-03"], 0.0, 3.0, transition="crossfade", tdur=0.5, kb_amount=0.08)
    photo_bg(t, "proposal-01", 6.0, 2.0, s1=1.05, label="Foto del anillo")
    flash(t, 3.0, 0.4, peak=0.9)
    label(t, t.track("text", "Anillo"), "💍", 3.0, 5.0, centered(540, 700, 300, 300), "Inter", 220, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"s": 0.0}, "back"), (0.5, {})], anim_loop=tanim("float", amount=0.06, speed=0.6))
    label(t, t.track("text", "Título"), "¡DIJO QUE SÍ!", 3.2, 4.8, Box(60, 900, 960, 260), "Anton", 170, "#FFFFFF", weight=400,
          spacing=6, layers=[shadow("#E5486F", 0, 10, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          name="Título")
    confetti(t, ["#FFFFFF", "#F2D59B", "#FFB3C1"], 3.0, 5.0, seed=3131, lanes=4, density=0.25)
    t.adjust([effect("bling_sparkle", intensity=0.6, threshold=0.7, density=0.35)], name="Destellos")
    song(t, "epic", 3, 0.85)
    return t


def despedida_soltera():
    t = tall("r-despedida-soltera", "Despedida de soltera", "Bachelorette party", "celebration", 9.0, order=3132,
             tags=["despedida de soltera", "amigas", "fiesta", "novia", "bride"], thumb_at=5.0, background="#FFB3C6")
    bg_gradient(t, [(0, "#FFC8DD"), (1, "#FFAFCC")], angle=135)
    samples = ["friends-03", "friends-09", "friends-05", "newyear-04"]
    for i, s in enumerate(samples):
        at = 0.2 + i * 1.6
        r = (-1) ** i * 6
        framed(t, s, at, 9.0 - at, centered(540 + (-1) ** i * 120, 520 + i * 300, 640, 640),
               [(0, {"s": 1.4}, "out"), (0.4, {})], border=16, radius=20, rotation=keys([(0, r)]), label=f"Foto {i + 1}")
    label(t, t.track("text", "Título"), "BRIDE\nSQUAD", 1.0, 8.0, Box(60, 1460, 960, 400), "Shrikhand", 150, "#FFFFFF",
          weight=400, line=0.95, layers=[shadow("#C9184A", 0, 10, 0, 1.0), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.2), name="Título")
    dots(t, ["#FFFFFF", "#F2D59B"], 22, 0.5, 8.5, seed=3132, size=(12, 26), kinds=("star", "heart"), drift=90)
    song(t, "electro", 2, 0.85)
    return t


def boda_votos():
    t = tall("r-boda-votos", "Boda: los votos", "Wedding vows", "celebration", 12.0, order=3133,
             tags=["boda", "votos", "promesas", "novios", "ceremonia"], thumb_at=6.0, background="#FBF8F3")
    slides(t, ["wedding-01", "wedding-04", "wedding-06"], 0.0, 4.0, transition="crossfade", tdur=1.0, kb_amount=0.05,
           effects_fn=lambda i: [effect("color.basic", fade=0.12, temperature=0.06)])
    shade_bottom(t, 900, 0.7, colour="#2B2118")
    vows = ["prometo elegirte", "cada mañana", "incluso los lunes"]
    for i, v in enumerate(vows):
        label(t, t.track("text", "Voto"), v, 1.0 + i * 3.4, 3.2, Box(60, 1350, 960, 200), "Cormorant Garamond", 100, "#FFFFFF",
              weight=500, italic=True, anim_in=tanim("blur-in", duration=0.8, blur=12), anim_out=tanim("fade", duration=0.5),
              name=f"Voto {i + 1}")
    label(t, t.track("text", "Nombres"), "Ana & Leo", 0.4, 11.6, Box(60, 1650, 960, 140), "Great Vibes", 100, "#E8C27A",
          weight=400, anim_in=tanim("fade", duration=0.8), name="Nombres")
    song(t, "romantic", 1, 0.8)
    return t


def boda_primer_baile():
    t = tall("r-boda-primer-baile", "Boda: primer baile", "First dance", "celebration", 10.0, order=3134,
             tags=["boda", "primer baile", "vals", "novios", "fiesta"], thumb_at=5.4, background="#0B0B12")
    slides(t, ["wedding-05", "dance-01", "wedding-02"], 0.0, 3.3, transition="blur_dissolve", tdur=0.8, kb_amount=0.07)
    t.solid(t.track("shape", "Foco"), "#FFFFFF", 0, 10.0, centered(540, 900, 1400, 1400), kind="ellipse",
            layers=[gradient([(0, "#FFFFFF", 0.0), (0.55, "#000000", 0.0), (1, "#000000", 0.75)], angle=0), no_stroke()])
    dots(t, ["#FFE8A0", "#FFFFFF"], 34, 0, 10.0, seed=3134, size=(8, 20), drift=50, alpha=0.8)
    label(t, t.track("text", "Título"), "nuestro primer baile", 1.0, 9.0, Box(60, 1500, 960, 220), "Great Vibes", 120,
          "#FFFFFF", weight=400, layers=[glow("#FFE8A0", 16, 0.6), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=1.0),
          name="Título")
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.7)], name="Brillo")
    song(t, "romantic", 2, 0.85)
    return t


def bautizo_vertical():
    t = tall("r-bautizo", "Bautizo", "Christening", "celebration", 9.0, order=3135,
             tags=["bautizo", "bebé", "iglesia", "familia", "fe"], thumb_at=5.0, background="#F2F8FC")
    bg_gradient(t, [(0, "#F8FCFF"), (1, "#DCEBF7")], angle=90)
    circle_photo(t, "baby-03", 0.3, 8.7, centered(540, 760, 760, 760), pop(0, 0.6, 0.6), ring_colour="#FFFFFF",
                 ring_width=20, label="Foto del bebé")
    label(t, t.track("text", "Paloma"), "🕊", 1.0, 8.0, centered(880, 320, 220, 220), "Inter", 150, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"dx": 400, "dy": -200}, "out"), (1.2, {})], anim_loop=tanim("float", amount=0.08,
                                                                                                    speed=0.5))
    label(t, t.track("text", "Título"), "Mi bautizo", 1.2, 7.8, Box(60, 1220, 960, 200), "Dancing Script", 150, "#3A6EA5",
          weight=700, anim_in=tanim("fade", duration=0.8), name="Título")
    label(t, t.track("text", "Nombre"), "Valentina", 1.6, 7.4, Box(60, 1420, 960, 150), "Playfair Display", 110, "#1F3B5C",
          weight=600, anim_in=tanim("fade", duration=0.8), name="Nombre")
    label(t, t.track("text", "Fecha"), "8 de noviembre · 11:00", 2.0, 7.0, Box(60, 1590, 960, 80), "Montserrat", 46,
          "#5C7FA3", weight=500, anim_in=tanim("fade", duration=0.8), name="Fecha")
    song(t, "classic", 2, 0.75)
    return t


def primera_comunion():
    t = tall("r-primera-comunion", "Primera comunión", "First communion", "celebration", 9.0, order=3136,
             tags=["primera comunión", "fe", "familia", "niños", "celebración"], thumb_at=5.0, background="#FFFDF7")
    bg(t, "#FFFDF7")
    photo_bg(t, "church-01", 0, 9.0, s1=1.04, label="Foto de fondo", effects=[effect("color.basic", exposure=0.25, fade=0.3)])
    shade_full(t, 0.55, colour="#FFFDF7")
    framed(t, "kids-03", 0.4, 8.6, Box(190, 380, 700, 860), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (8.6, {"s": 1.03})],
           border=14, radius=20, colour="#E8C27A", label="Foto")
    label(t, t.track("text", "Título"), "Mi primera comunión", 1.0, 8.0, Box(60, 1300, 960, 200), "Dancing Script", 120,
          "#8C6B2F", weight=700, anim_in=tanim("fade", duration=0.8), name="Título")
    label(t, t.track("text", "Nombre"), "Santiago · mayo 2026", 1.6, 7.4, Box(60, 1510, 960, 90), "Cinzel", 52, "#5C4B2E",
          weight=600, spacing=4, anim_in=tanim("fade", duration=0.8), name="Nombre y fecha")
    dots(t, ["#E8C27A", "#FFFFFF"], 18, 0.5, 8.5, seed=3136, size=(8, 16), kinds=("star",), drift=60)
    song(t, "classic", 0, 0.75)
    return t


def graduacion_kinder():
    t = tall("r-graduacion-kinder", "Graduación de kínder", "Kindergarten graduation", "celebration", 9.0, order=3137,
             tags=["graduación", "kínder", "preescolar", "niños", "orgullo"], thumb_at=5.0, background="#FFF3B0")
    bg_gradient(t, [(0, "#FFF3B0"), (1, "#E0FBFC")], angle=90)
    for k in range(10):  # crayon border
        c = ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93"][k % 5]
        t.solid(t.track("shape", "Crayón"), c, 0, 9.0, Box(k * 108, 0, 108, 40))
        t.solid(t.track("shape", "Crayón"), c, 0, 9.0, Box(k * 108, 1880, 108, 40))
    framed(t, "school-01", 0.4, 8.6, Box(140, 260, 800, 960), [(0, {"s": 0.7}, "back"), (0.5, {}, "linear"), (8.6, {"s": 1.03})],
           border=18, radius=40, label="Foto del graduado")
    label(t, t.track("text", "Birrete"), "🎓", 1.0, 8.0, centered(860, 260, 240, 240), "Inter", 170, "#000000", weight=400,
          editable=False, motion=[(0, {"dy": -400}, "back"), (0.6, {})], rotation=keys([(0, 15)]))
    label(t, t.track("text", "Título"), "¡Me gradué\ndel kínder!", 1.2, 7.8, Box(60, 1300, 960, 360), "Baloo 2", 120, "#1982C4",
          weight=800, line=0.95, layers=[stroke(8, "#FFFFFF"), fill("#1982C4")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.03), name="Título")
    label(t, t.track("text", "Nombre"), "Mía · Promoción 2026", 2.0, 7.0, Box(60, 1680, 960, 90), "Baloo 2", 56, "#FF595E",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Nombre")
    song(t, "fun", 3, 0.8)
    return t


def graduacion_universidad():
    t = tall("r-graduacion-universidad", "Graduación universitaria", "University graduation", "celebration", 10.0,
             order=3138, tags=["graduación", "universidad", "título", "logro", "carrera"], thumb_at=7.4, background="#0A1F44")
    slides(t, ["graduation-03", "graduation-05", "graduation-01", "graduation-06"], 0.0, 1.8, transition=None, kb_amount=0.1)
    photo_bg(t, "graduation-02", 7.2, 2.8, s1=1.06, label="Foto principal")
    shade_bottom(t, 900, 0.8, 7.2, 2.8, colour="#0A1F44")
    label(t, t.track("text", "Título"), "LIC. EN\nARQUITECTURA", 7.4, 2.6, Box(60, 1250, 960, 360), "Playfair Display", 110,
          "#F5D98B", weight=800, line=1.0, layers=[glow("#F5D98B", 14, 0.5), fill("#F5D98B")],
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12), name="Título")
    label(t, t.track("text", "Nombre"), "Daniela Ríos · 2026", 7.8, 2.2, Box(60, 1640, 960, 90), "Montserrat", 52, "#FFFFFF",
          weight=600, anim_in=tanim("fade", duration=0.5), name="Nombre")
    flash(t, 7.2, 0.3, peak=0.8)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.8, 3.6, 5.4], 0.4, 0.3)})], name="Golpe")
    confetti(t, ["#F5D98B", "#FFFFFF"], 7.2, 2.8, seed=3138, lanes=3, density=0.25)
    song(t, "epic", 1, 0.85)
    return t


def jubilacion_vertical():
    t = tall("r-jubilacion", "¡Me jubilé!", "I retired!", "celebration", 9.0, order=3139,
             tags=["jubilación", "retiro", "trabajo", "nueva etapa", "celebración"], thumb_at=5.6, background="#E9F5DB")
    bg_gradient(t, [(0, "#E9F5DB"), (1, "#CFE1B9")], angle=90)
    framed(t, "office-03", 0.2, 3.6, Box(140, 300, 800, 700), [(0, {"s": 1.2}, "out"), (0.4, {})], border=14,
           rotation=keys([(0, -3)]), label="Foto del trabajo")
    framed(t, "hike-02", 3.4, 5.6, Box(140, 300, 800, 700), [(0, {"dx": 1100}, "out"), (0.5, {})], border=14,
           rotation=keys([(0, 3)]), label="Foto de la nueva etapa")
    label(t, t.track("text", "Antes"), "30 años de oficina…", 0.6, 2.8, Box(60, 1100, 960, 150), "Caveat", 100, "#3A5A40",
          weight=700, anim_in=tanim("typewriter", duration=0.8, unit="character"), anim_out=tanim("fade", duration=0.3),
          name="Antes")
    label(t, t.track("text", "Título"), "¡ahora a\nvivir la vida!", 3.8, 5.2, Box(60, 1100, 960, 360), "Lilita One", 140,
          "#3A5A40", weight=400, line=0.95, anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.15), name="Título")
    confetti(t, ["#F2C14E", "#FFFFFF", "#A7C957"], 3.6, 5.4, seed=3139, lanes=3, density=0.3)
    song(t, "upbeat", 4, 0.8)
    return t


def bienvenida_casa():
    t = tall("r-bienvenida-casa", "Bienvenido a casa", "Welcome home", "celebration", 9.0, order=3140,
             tags=["bienvenida", "regreso", "casa", "familia", "sorpresa"], thumb_at=5.0, background="#FFF4E0")
    bg(t, "#FFF4E0")
    t.solid(t.track("shape", "Banderín"), "#E76F51", 0, 9.0, Box(0, 120, 1080, 6))
    for k in range(9):
        c = ["#E76F51", "#F4A261", "#2A9D8F", "#E9C46A"][k % 4]
        t.solid(t.track("shape", "Banderín"), c, 0.1 + k * 0.08, 8.9 - k * 0.08, centered(60 + k * 120, 190, 100, 130),
                pop(0, 0.3), kind="triangle", rotation=keys([(0, 180)]))
    framed(t, "family-04", 0.5, 8.5, Box(110, 360, 860, 1000), [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (8.5, {"s": 1.03})],
           border=18, radius=30, label="Foto del reencuentro")
    label(t, t.track("text", "Título"), "¡Bienvenido\na casa, papá!", 1.0, 8.0, Box(60, 1420, 960, 360), "Lilita One", 120,
          "#E76F51", weight=400, line=0.95, anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.15), name="Título")
    song(t, "upbeat", 6, 0.8)
    return t


def nuevo_empleo():
    t = tall("r-nuevo-empleo", "Nuevo empleo", "New job", "celebration", 8.0, order=3141,
             tags=["nuevo trabajo", "empleo", "logro", "primer día", "carrera"], thumb_at=4.6, background="#1D3557")
    bg_gradient(t, [(0, "#264B7A"), (1, "#14263F")], angle=90)
    circle_photo(t, "office-04", 0.3, 7.7, centered(540, 720, 640, 640), pop(0, 0.5), ring_colour="#A8DADC", ring_width=14,
                 label="Tu foto")
    label(t, t.track("text", "Antetítulo"), "PRIMER DÍA EN", 1.0, 7.0, Box(60, 1120, 960, 80), "Montserrat", 50, "#A8DADC",
          weight=800, spacing=10, anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    label(t, t.track("text", "Empresa"), "Estudio Norte", 1.3, 6.7, Box(60, 1200, 960, 180), "DM Serif Display", 140, "#FFFFFF",
          weight=400, anim_in=tanim("rise", duration=0.5), name="Empresa")
    label(t, t.track("text", "Cargo"), "diseñadora junior ✨", 1.8, 6.2, Box(60, 1390, 960, 90), "Montserrat", 56, "#F1FAEE",
          weight=600, anim_in=tanim("fade", duration=0.4), name="Cargo")
    confetti(t, ["#A8DADC", "#FFFFFF", "#E63946"], 1.0, 7.0, seed=3141, lanes=3, density=0.35)
    song(t, "upbeat", 3, 0.8)
    return t


def casa_nueva():
    t = tall("r-casa-nueva", "Casa nueva", "New home", "celebration", 8.0, order=3142,
             tags=["casa nueva", "mudanza", "hogar", "llaves", "logro"], thumb_at=4.6, background="#F5EFE6")
    photo_bg(t, "home-02", s1=1.06, label="Foto de la casa")
    shade_bottom(t, 900, 0.75, colour="#2B2118")
    label(t, t.track("text", "Llaves"), "🔑", 0.5, 7.5, centered(540, 700, 260, 260), "Inter", 200, "#FFFFFF", weight=400,
          editable=False, motion=[(0, {"s": 0.0}, "back"), (0.5, {})], rotation=keys([(0, -20, "smooth"), (0.6, 10, "smooth"),
                                                                                   (1.2, 0)]))
    label(t, t.track("text", "Título"), "¡Tenemos\ncasa nueva!", 1.0, 7.0, Box(60, 1180, 960, 380), "DM Serif Display", 140,
          "#FFFFFF", weight=400, line=0.95, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15),
          name="Título")
    label(t, t.track("text", "Sub"), "nuevo comienzo · familia Paz", 1.8, 6.2, Box(60, 1600, 960, 90), "Montserrat", 50,
          "#F2E6CF", weight=600, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    song(t, "upbeat", 2, 0.8)
    return t


def logro_deportivo():
    t = tall("r-logro-deportivo", "¡Campeones!", "Champions!", "celebration", 8.0, order=3143,
             tags=["campeones", "deporte", "trofeo", "victoria", "equipo"], thumb_at=4.6, background="#000000")
    slides(t, ["sport-03", "sport-04", "gym-06", "hike-03"], 0.0, 1.0, transition=None, kb_amount=0.12,
           effects_fn=lambda i: [effect("color.basic", contrast=0.3)])
    photo_bg(t, "sport-03", 4.0, 4.0, s1=1.05, label="Foto final", reuse="p1")
    shade_full(t, 0.4, 4.0, 4.0)
    label(t, t.track("text", "Trofeo"), "🏆", 4.0, 4.0, centered(540, 620, 360, 360), "Inter", 260, "#FFD23F", weight=400,
          editable=False, motion=[(0, {"s": 0.0, "dy": 300}, "back"), (0.6, {})])
    label(t, t.track("text", "Título"), "¡CAMPEONES!", 4.2, 3.8, Box(40, 900, 1000, 260), "Anton", 190, "#FFFFFF",
          weight=400, layers=[shadow("#E10600", 0, 12, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("stamp", duration=0.3),
          name="Título")
    label(t, t.track("text", "Torneo"), "Liga juvenil 2026", 4.6, 3.4, Box(60, 1180, 960, 100), "Barlow Condensed", 70,
          "#FFD23F", weight=800, spacing=6, anim_in=tanim("fade", duration=0.4), name="Torneo")
    flash(t, 4.0, 0.35)
    confetti(t, ["#FFD23F", "#FFFFFF", "#E10600"], 4.0, 4.0, seed=3143, lanes=4, density=0.22)
    t.adjust([effect("beat_shake", animated={"amount": spike([1.0, 2.0, 3.0, 4.0], 0.6, 0.25)})], name="Golpe")
    song(t, "epic", 1, 0.9)
    return t


def fiesta_fin_anio():
    t = tall("r-fiesta-fin-anio", "Fiesta de fin de año", "Year-end party", "celebration", 9.0, order=3144,
             tags=["fin de año", "fiesta", "empresa", "amigos", "brindis"], thumb_at=6.0, background="#0B0B1E")
    slides(t, ["newyear-01", "newyear-03", "friends-10", "newyear-05"], 0.0, 1.5, transition="crossfade", tdur=0.3,
           kb_amount=0.08)
    photo_bg(t, "newyear-02", 6.0, 3.0, s1=1.05, label="Foto final")
    shade_full(t, 0.4, 6.0, 3.0, colour="#0B0B1E")
    label(t, t.track("text", "Brindis"), "🥂", 6.0, 3.0, centered(540, 650, 300, 300), "Inter", 220, "#FFFFFF", weight=400,
          editable=False, motion=pop(0, 0.5))
    label(t, t.track("text", "Título"), "¡Salud por\nun gran año!", 6.2, 2.8, Box(60, 900, 960, 380), "Playfair Display", 130,
          "#F5D98B", weight=800, line=0.95, layers=[glow("#F5D98B", 18, 0.6), fill("#F5D98B")],
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.12), name="Título")
    confetti(t, ["#F5D98B", "#FFFFFF", "#C0C0C0"], 6.0, 3.0, seed=3144, lanes=4, density=0.22)
    t.adjust([effect("bling_sparkle", intensity=0.5, threshold=0.7, density=0.3)], name="Destellos")
    song(t, "upbeat", 5, 0.85)
    return t


# --- Intros ---------------------------------------------------------------------------------------

def hola_soy():
    t = tall("r-hola-soy", "Hola, soy…", "Hi, I'm…", "intro", 7.0, order=3145,
             tags=["presentación", "hola soy", "creador", "intro", "nuevo seguidor"], thumb_at=4.0, background="#FFE066")
    bg(t, "#FFE066")
    t.photo(t.track("video", "Video"), "creator-03", 0.0, 7.0, Box(0, 520, 1080, 1400), kb(7.0, 1.0, 1.06), label="Tu video")
    label(t, t.track("text", "Hola"), "hola, soy", 0.2, 6.8, Box(60, 120, 960, 140), "DM Sans", 92, "#111111", weight=700,
          anim_in=tanim("fade", duration=0.3), name="Saludo")
    label(t, t.track("text", "Nombre"), "Camila ✌", 0.6, 6.4, Box(60, 250, 960, 230), "Archivo Black", 180, "#111111",
          weight=400, anim_in=tanim("stamp", duration=0.3), name="Nombre")
    tags_ = ["recetas", "viajes", "humor"]
    for i, tg in enumerate(tags_):
        pill(t, t.track("shape", "Tema"), "#111111", 1.4 + i * 0.3, 5.6 - i * 0.3, Box(80 + i * 320, 1700, 290, 100),
             pop(0, 0.35))
        label(t, t.track("text", "Tema"), tg, 1.4 + i * 0.3, 5.6 - i * 0.3, Box(80 + i * 320, 1700, 290, 100), "DM Sans", 48,
              "#FFE066", weight=800, name=f"Tema {i + 1}")
    song(t, "fun", 1, 0.8)
    return t


def nuevo_capitulo():
    t = tall("r-nuevo-capitulo", "Nuevo capítulo", "New chapter", "intro", 6.0, order=3146,
             tags=["nuevo capítulo", "comienzo", "cambio", "intro", "historia"], thumb_at=3.6, background="#0F0F0F")
    photo_bg(t, "hike-01", s1=1.1, label="Foto")
    shade_full(t, 0.45)
    label(t, t.track("text", "Capítulo"), "CAPÍTULO 2", 0.4, 5.6, Box(60, 700, 960, 100), "Cinzel", 64, "#F2E6CF", weight=600,
          spacing=20, anim_in=tanim("fade", duration=0.8), name="Capítulo")
    label(t, t.track("text", "Título"), "empezar de nuevo", 1.0, 5.0, Box(60, 820, 960, 300), "Cormorant Garamond", 140,
          "#FFFFFF", weight=500, italic=True, line=1.0, anim_in=tanim("blur-in", duration=1.0, unit="word", stagger=0.2),
          name="Título")
    line(t, t.track("shape", "Línea"), "#F2E6CF", 1.6, 4.4, centered(540, 1160, 240, 3), grow="c", length=0.8)
    song(t, "cine", 3, 0.8)
    return t


def intro_serie():
    t = tall("r-intro-serie", "Intro de serie", "Series opener", "intro", 7.0, order=3147,
             tags=["serie", "temporada", "episodio", "intro", "netflix style"], thumb_at=5.2, background="#000000")
    slides(t, ["night-04", "portrait-08", "city-01"], 0.0, 1.4, transition=None, kb_amount=0.1,
           effects_fn=lambda i: [effect("color.basic", saturation=-0.4, contrast=0.3)])
    t.solid(t.track("shape", "Negro"), "#000000", 4.2, 2.8)
    label(t, t.track("text", "Título"), "MI VIDA", 4.4, 2.6, Box(60, 760, 960, 260), "Bebas Neue", 280, "#E50914", weight=400,
          spacing=20, layers=[glow("#E50914", 18, 0.6), fill("#E50914")], anim_in=tanim("zoom-out", duration=0.8, blur=10),
          name="Título")
    label(t, t.track("text", "Temporada"), "TEMPORADA 26 · EPISODIO 1", 4.9, 2.1, Box(60, 1030, 960, 70), "Montserrat", 40,
          "#FFFFFF", weight=600, spacing=8, anim_in=tanim("fade", duration=0.5), name="Temporada")
    song(t, "suspense", 0, 0.85)
    return t


def parte_1():
    t = tall("r-parte-1", "Parte 1", "Part 1", "intro", 5.0, order=3148,
             tags=["parte 1", "serie", "historia", "storytime", "continuará"], thumb_at=1.4, background="#111111")
    photo_bg(t, "selfie-04", s1=1.08, label="Tu video")
    pill(t, t.track("shape", "Etiqueta"), "#FFFFFF", 0.2, 4.8, Box(60, 160, 360, 120), pop(0, 0.35))
    label(t, t.track("text", "Parte"), "PARTE 1", 0.2, 4.8, Box(60, 160, 360, 120), "Archivo Black", 64, "#111111", weight=400,
          name="Parte")
    label(t, t.track("text", "Gancho"), "cómo renuncié a mi trabajo y me fui a vivir a una isla", 0.5, 4.5,
          Box(60, 320, 960, 400), "DM Sans", 80, "#FFFFFF", weight=800, align="left", line=1.1,
          layers=[shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")], anim_in=tanim("typewriter", duration=1.4, unit="character"),
          name="Gancho")
    song(t, "suspense", 1, 0.8)
    return t


def portada_blog():
    t = tall("r-portada-blog", "Portada de blog", "Blog cover", "intro", 6.0, order=3149,
             tags=["blog", "portada", "artículo", "lectura", "nuevo post"], thumb_at=3.6, background="#F7F3EE")
    bg(t, "#F7F3EE")
    t.photo(t.track("video", "Foto"), "reading-02", 0.2, 5.8, Box(80, 760, 920, 1040), [(0, {"dy": 200}, "out"), (0.6, {}, "linear"),
                                                                                       (5.8, {"s": 1.03})], label="Foto")
    label(t, t.track("text", "Sección"), "NUEVO EN EL BLOG", 0.3, 5.7, Box(80, 150, 920, 70), "Montserrat", 38, "#C65D3B",
          weight=800, spacing=12, align="left", anim_in=tanim("fade", duration=0.4), name="Sección")
    label(t, t.track("text", "Título"), "10 libros para leer este otoño", 0.6, 5.4, Box(80, 230, 920, 420), "Playfair Display",
          104, "#2D2A26", weight=800, align="left", line=1.02, anim_in=tanim("rise-by-word", duration=0.4, unit="word",
          stagger=0.08), name="Título")
    label(t, t.track("text", "Link"), "link en mi perfil ↗", 1.6, 4.4, Box(80, 660, 920, 70), "Montserrat", 40, "#777777",
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), name="Llamada")
    song(t, "calm", 4, 0.75)
    return t


TEMPLATES = [collage_3_vertical, collage_2_mas_1, mosaico_3x3, recortes_revista, marco_camara, tablero_corcho,
             tarjetas_apiladas, collage_circulos, fotomaton, album_stickers, pantalla_celular, diario_cinta,
             rejilla_bordes, carrusel, foto_en_foto,
             ba_cortina, ba_dia_1_100, ba_maquillaje, ba_casa, ba_jardin, ba_peinado, ba_mascota, ba_cocina, ba_auto,
             ba_dibujo,
             cumple_infantil, cumple_adulto, cumple_mama, pastel_velas, aniversario_bodas, primera_cita, propuesta,
             despedida_soltera, boda_votos, boda_primer_baile, bautizo_vertical, primera_comunion, graduacion_kinder,
             graduacion_universidad, jubilacion_vertical, bienvenida_casa, nuevo_empleo, casa_nueva, logro_deportivo,
             fiesta_fin_anio,
             hola_soy, nuevo_capitulo, intro_serie, parte_1, portada_blog]
