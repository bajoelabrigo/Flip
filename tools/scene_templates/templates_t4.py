"""Trend batch 4 (2026-10-15): see BRIEF.md, section «Las 100 de tendencia».

Vida y personas: weddings, babies, couples, friends, trips, routines, pets and parties (order 1300–1399).
Each one has its own palette, typeface and motion; times in seconds, boxes in 1080x1920 project pixels.
"""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, Track, beat, centered, effect, fill, glow, gradient, keys, no_stroke,
                   shadow, stroke, tanim, text_style)


# --- Helpers -------------------------------------------------------------------------------------


def pop(at: float = 0.0, length: float = 0.45) -> list:
    return [(at, {"s": 0.0}, "back"), (at + length, {})]


def grow_left(box: Box, length: float, ease: str = "linear") -> list:
    """Motion of a bar that fills from its left edge in `length` seconds."""
    return [(0, {"sx": 0.0, "dx": -box.w / 2}, ease), (length, {})]


def spikes(times: list[float], peak: float, fall: float = 0.25) -> dict:
    """Keys for a spike effect: up at each time, back to 0 and held there until the next one."""
    points: list[tuple] = []
    if times[0] > 0:
        points.append((0.0, 0.0, "hold"))
    for at in times:
        points.append((at, peak, "out"))
        points.append((at + fall, 0.0, "hold"))
    return keys(points)


def outline(width: float, colour: str, alpha: float = 1.0) -> list:
    return [stroke(width, colour, alpha), {"id": "fill", "kind": "fill", "enabled": False,
                                           "paint": {"kind": "solid", "color": "#00000000"}}]


def pill(t: Template, track, colour: str, t0: float, dur: float, box: Box, motion=None, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=box.h / 2, kind="rounded-rectangle", **extra)


def confetti(t: Template, seed: int, colours: list[str], start: float, end: float, lanes: int = 3,
             kinds=("rectangle", "ellipse", "star")) -> None:
    """Bits that fall from the top between `start` and `end`."""
    rng = random.Random(seed)
    for lane in range(lanes):
        track = t.track("shape", f"Confeti {lane + 1}")
        at = start + lane * 0.15
        while at < end - 0.4:
            size = rng.uniform(22, 48)
            fall = rng.uniform(2.2, 3.6)
            dur = min(fall, end - at)
            t.solid(track, rng.choice(colours), at, dur, centered(rng.uniform(30, 1050), -50, size, size * 0.7),
                    [(0, {}, "linear"), (fall, {"dy": 2100, "dx": rng.uniform(-140, 140)})],
                    kind=rng.choice(kinds), radius=3, rotation=keys([(0, 0), (fall, rng.uniform(-400, 400))]))
            at += rng.uniform(0.18, 0.4)


def tidy(t: Template) -> Template:
    """Clips that overlap in time on one track go to extra tracks right above it (first fit), so every
    track holds its clips in turn. Tracks with transitions or mask lanes are left alone."""
    out = []
    for track in t.tracks:
        if track.transitions or track.lanes or len(track.clips) < 2:
            out.append(track)
            continue
        rows: list[list[dict]] = []
        for clip in sorted(track.clips, key=lambda c: c["timelineStartUs"]):
            for row in rows:
                last = row[-1]
                if last["timelineStartUs"] + last["timelineDurationUs"] <= clip["timelineStartUs"]:
                    row.append(clip)
                    break
            else:
                rows.append([clip])
        track.clips = rows[0]
        out.append(track)
        for row in rows[1:]:
            extra = Track(type=track.type, name=track.name, clips=row)
            extra.extra = dict(track.extra)
            out.append(extra)
    t.tracks = out
    return t


def _tidied(make):
    def build() -> Template:
        return tidy(make())
    build.__name__ = make.__name__
    return build


# --- Weddings ------------------------------------------------------------------------------------


def boda_save_the_date() -> Template:
    """Ivory card, sage double frame, three photos dissolving, names and date written in like print."""
    t = Template("boda-save-the-date", "Save the date: boda", "Wedding save the date", "celebration", 10.0,
                 order=1300, tags=["boda", "save the date", "invitación", "matrimonio", "novios"], thumb_at=7.6,
                 background="#F7F3EC")
    t.solid(t.track("shape", "Papel"), "#F7F3EC",
            layers=[gradient([(0, "#FBF8F2"), (1, "#EEE7DA")], angle=90), no_stroke()])
    box = centered(540, 820, 760, 1000)
    frames = t.track("shape", "Marco")
    t.solid(frames, "#FFFFFF", 0.0, 10.0, centered(540, 820, 820, 1060), [(0, {"s": 0.94}, "out"), (1.2, {})],
            layers=[shadow("#6b6450", 0, 14, 40, 0.22), fill("#FFFFFF"), no_stroke()])
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(["wedding-04", "wedding-02", "wedding-05"]):
        start = i * 10 / 3
        motion = [(0, {"s": 0.94 if i == 0 else 1.0}, "out" if i == 0 else "linear"),
                  (1.2 if i == 0 else 10 / 3, {"s": 1.0 if i == 0 else 1.04})]
        clips.append(t.photo(photos, sample, start, 10 / 3, box, motion, label=f"Foto {i + 1}"))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.8)
    inner = t.track("shape", "Filete")
    t.solid(inner, "#8A9A7B", 0.6, 9.4, centered(540, 820, 720, 960), layers=outline(3, "#F7F3EC", 0.9),
            opacity=keys([(0, 0.0, "smooth"), (0.8, 1.0)]))
    rules = t.track("shape", "Líneas")
    rules2 = t.track("shape", "Líneas")
    for track, x, sign in ((rules, 115, 1), (rules2, 815, -1)):
        line = Box(x, 1563, 150, 3)
        t.solid(track, "#8A9A7B", 2.4, 7.6, line, [(0, {"sx": 0.0, "dx": -75 * sign}, "out"), (0.8, {})])
    words = t.track("text", "Textos")
    t.text(words, "Save the date", 0.3, 9.7, Box(40, 70, 1000, 230),
           text_style("Pinyon Script", 150, [fill("#7C8C6C")], weight=400,
                      anim_in=tanim("blur-in", duration=1.2, blur=18)), label="Título")
    t.text(words, "Lucía & Diego", 1.4, 8.6, Box(40, 1380, 1000, 130),
           text_style("Cinzel", 84, [fill("#3E4A3A")], weight=600, spacing=6,
                      anim_in=tanim("fade-up-char", duration=0.7, unit="character", stagger=0.04)), label="Nombres")
    t.text(words, "14 · 02 · 2027", 2.2, 7.8, Box(270, 1520, 540, 90),
           text_style("Cinzel", 56, [fill("#7C8C6C")], weight=500, spacing=8,
                      anim_in=tanim("wipe", duration=0.9)), label="Fecha")
    t.text(words, "Hacienda Los Olivos · Lima", 3.0, 7.0, Box(40, 1630, 1000, 80),
           text_style("Cormorant Garamond", 50, [fill("#5B6650")], weight=600,
                      anim_in=tanim("fade", duration=0.8)), label="Lugar")
    t.text(words, "invitación formal a continuación", 3.6, 6.4, Box(40, 1720, 1000, 70),
           text_style("Cormorant Garamond", 38, [fill("#8A9A7B")], weight=400, spacing=3, case="upper",
                      anim_in=tanim("fade", duration=0.8)), label="Nota")
    t.adjust([effect("light_leak", intensity=0.22, hue=0.08, speed=0.4, softness=0.7),
              effect("stylize.film_grain", amount=0.12, grainSize=1.4)], name="Luz")
    t.song("the-celebrated-minuet-for-piano", 0.0, 0.8)
    return t


def letterbox(t: Template, height: float, start: float = 0.0) -> None:
    for y, dy in ((0, -height), (1920 - height, height)):
        t.solid(t.track("shape", "Barras"), "#000000", start, t.duration - start, Box(0, y, 1080, height),
                [(0, {"dy": dy}, "out"), (0.9, {})])


def resumen_de_boda() -> Template:
    """Cinematic wedding recap: scope bars, slow pushes, blurred dissolves, chapter titles in the bars."""
    t = Template("resumen-de-boda", "Resumen de boda", "Wedding recap", "celebration", 15.0,
                 order=1301, tags=["boda", "matrimonio", "resumen", "cinemático", "novios"], thumb_at=2.2,
                 background="#0B0B0B")
    photos = t.track("video", "Fotos")
    samples = ["wedding-01", "wedding-03", "travel-03", "wedding-06", "wedding-04"]
    labels = ["Apertura", "La iglesia", "El sí", "La cena", "Final"]
    clips = []
    for i, (sample, label) in enumerate(zip(samples, labels)):
        drift = 50 if i % 2 else -50
        clips.append(t.photo(photos, sample, i * 3.0, 3.0, FULL,
                             [(0, {"s": 1.14, "dx": drift}, "linear"), (3.0, {"s": 1.03, "dx": -drift})],
                             label=label))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "blur_dissolve", 0.8)
    t.adjust([effect("cinematic_grade", strength=0.45, teal=0.3, orange=0.6, contrast=0.35),
              effect("light_leak", intensity=0.25, hue=0.07, speed=0.6, softness=0.6),
              effect("stylize.vignette", amount=0.5, softness=0.9),
              effect("stylize.film_grain", amount=0.2, grainSize=1.6)], name="Cine")
    letterbox(t, 230)
    words = t.track("text", "Títulos")
    shade = shadow("#000000", 0, 4, 24, 0.7)
    t.text(words, "Ana & Luis", 0.4, 2.8, Box(40, 760, 1000, 220),
           text_style("Playfair Display", 130, [shade, fill("#FFF8EE")], weight=500, italic=True,
                      anim_in=tanim("blur-in", duration=1.2, blur=22), anim_out=tanim("fade", duration=0.4)),
           label="Nombres")
    t.text(words, "12 · 10 · 2026", 0.9, 2.3, Box(40, 980, 1000, 80),
           text_style("Montserrat", 40, [shade, fill("#F1E3C8")], weight=500, spacing=14,
                      anim_in=tanim("fade", duration=0.8), anim_out=tanim("fade", duration=0.4)), label="Fecha")
    chapters = t.track("text", "Capítulos")
    for i, (name, start) in enumerate((("la ceremonia", 3.2), ("el sí, acepto", 6.2), ("la fiesta", 9.2))):
        t.text(chapters, name, start, 2.6, Box(40, 1730, 1000, 90),
               text_style("Montserrat", 40, [fill("#F1E3C8")], weight=500, spacing=12, case="upper",
                          anim_in=tanim("tracking-drift", duration=0.9), anim_out=tanim("fade", duration=0.3)),
               label=f"Capítulo {i + 1}")
    t.text(words, "para siempre", 12.3, 2.7, Box(40, 780, 1000, 260),
           text_style("Playfair Display", 140, [shade, fill("#FFF8EE")], weight=500, italic=True,
                      anim_in=tanim("blur-in", duration=1.2, blur=22)), label="Cierre")
    t.song("amazing-grace", 0.0, 0.85)
    return t


# --- Babies --------------------------------------------------------------------------------------


def anuncio_embarazo() -> Template:
    """«1 + 1 =» then a «3» pops over a beating heart, and the bump photos arrive in an oval."""
    t = Template("anuncio-embarazo", "Anuncio de embarazo", "Pregnancy announcement", "celebration", 10.0,
                 order=1302, tags=["embarazo", "bebé", "anuncio", "familia", "seremos tres"], thumb_at=8.2,
                 background="#EFE6DA")
    t.solid(t.track("shape", "Fondo"), "#EFE6DA",
            layers=[gradient([(0, "#F6EFE6"), (1, "#E8D9C6")], angle=90), no_stroke()])
    rng = random.Random(31)
    for k in range(2):
        dots = t.track("shape", "Puntos")
        at = k * 0.7
        while at < 9.0:
            size = rng.uniform(18, 40)
            dur = rng.uniform(3.0, 4.5)
            t.solid(dots, rng.choice(["#D9A58E", "#C9D6C2", "#FFFFFF"]), at, min(dur, 10 - at),
                    centered(rng.uniform(40, 1040), 1980, size, size),
                    [(0, {}, "linear"), (dur, {"dy": -2100})], kind="ellipse", alpha=0.8)
            at += rng.uniform(0.8, 1.4)
    heart = t.track("shape", "Corazón")
    t.solid(heart, "#E7B9A6", 1.7, 1.7, centered(540, 1180, 420, 380),
            [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.7, {"s": 1.08}, "smooth"), (1.0, {}, "smooth"),
             (1.3, {"s": 1.08}, "in"), (1.7, {"s": 0.0})], kind="heart")
    sums = t.track("text", "Cuenta")
    t.text(sums, "1 + 1 =", 0.2, 3.1, Box(40, 560, 1000, 300),
           text_style("Quicksand", 200, [fill("#B5654A")], weight=700,
                      anim_in=tanim("typewriter", duration=1.0, unit="character"), anim_out=tanim("fade", duration=0.3)),
           editable=False)
    t.text(sums, "3", 1.8, 1.5, centered(540, 1170, 400, 400),
           text_style("Quicksand", 260, [fill("#FFFFFF")], weight=700, anim_in=tanim("pop", duration=0.4, ease="back"),
                      anim_out=tanim("fade", duration=0.3)), label="Número")
    oval_box = centered(540, 820, 760, 1000)
    ring = t.track("shape", "Aro")
    t.solid(ring, "#FFFFFF", 3.3, 6.7, centered(540, 820, 800, 1040), [(0, {"s": 0.7}, "out"), (0.7, {})],
            kind="ellipse", layers=[shadow("#8a5a44", 0, 14, 40, 0.25), fill("#FFFFFF"), no_stroke()])
    photos = t.track("video", "Fotos")
    first = t.photo(photos, "pregnant-03", 3.3, 3.4, oval_box,
                    [(0, {"s": 0.7}, "out"), (0.7, {}, "linear"), (3.4, {"s": 1.04})], label="Pancita")
    second = t.photo(photos, "pregnant-01", 6.7, 3.3, oval_box, [(0, {"s": 1.0}, "linear"), (3.3, {"s": 1.06})],
                     label="Foto 2")
    t.transition(photos, first, second, "crossfade", 0.8)
    for clip in (first, second):
        t.mask(photos, clip, "ellipse", feather=4)
    words = t.track("text", "Textos")
    t.text(words, "Pronto seremos 3", 3.6, 6.4, Box(40, 1360, 1000, 220),
           text_style("Sacramento", 150, [fill("#B5654A")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.8, unit="character", stagger=0.04)), label="Título")
    t.text(words, "llega en mayo 2027", 4.4, 5.6, Box(40, 1590, 1000, 90),
           text_style("Quicksand", 54, [fill("#6B5B4B")], weight=600, spacing=6, case="upper",
                      anim_in=tanim("fade", duration=0.8)), label="Fecha")
    t.song("happy-whistling-ukulele", 0.0, 0.8)
    return t


def revelacion_de_genero() -> Template:
    """Pink and blue halves, a 3-2-1 and the pink (or blue) side sweeps the screen with confetti."""
    t = Template("revelacion-de-genero", "Revelación: ¿niño o niña?", "Gender reveal", "celebration", 9.0,
                 order=1303, tags=["revelación", "niño o niña", "bebé", "embarazo", "baby"], thumb_at=7.4)
    t.solid(t.track("shape", "Azul"), "#9AD0F5", box=Box(540, 0, 540, 1920))
    pink = t.track("shape", "Rosa")
    t.solid(pink, "#FFB3C7", 0.0, 9.0, Box(0, 0, 540, 1920),
            [(0, {}, "linear"), (5.5, {}, "out"), (6.1, {"sx": 2.0, "dx": 270})])
    ring = t.track("shape", "Aro")
    photos = t.track("video", "Fotos")
    circle = centered(540, 900, 640, 640)
    t.solid(ring, "#FFFFFF", 0.2, 3.8, centered(540, 900, 690, 690), pop(), kind="ellipse",
            layers=[shadow("#3A3A5A", 0, 12, 30, 0.25), fill("#FFFFFF"), no_stroke()])
    t.solid(ring, "#FFFFFF", 5.6, 3.4, centered(540, 900, 690, 690), pop(0.1, 0.5), kind="ellipse",
            layers=[glow("#FFFFFF", 40, 0.8), fill("#FFFFFF"), no_stroke()])
    a = t.photo(photos, "couple-07", 0.2, 3.8, circle, pop(), label="Los papás")
    b = t.photo(photos, "pregnant-03", 5.6, 3.4, circle, pop(0.1, 0.5), label="Foto final")
    for clip in (a, b):
        t.mask(photos, clip, "ellipse")
    veil = t.track("shape", "Velo")
    t.solid(veil, "#3A3A5A", 4.0, 1.5, FULL, alpha=0.55)
    words = t.track("text", "Textos")
    ink = [shadow("#3A3A5A", 0, 8, 0, 0.9), stroke(10, "#3A3A5A"), fill("#FFFFFF")]
    t.text(words, "¿Niño o niña?", 0.3, 3.7, Box(40, 180, 1000, 260),
           text_style("Fredoka", 130, ink, weight=700, anim_in=tanim("bounce", duration=0.6, unit="word", stagger=0.12)),
           label="Pregunta")
    t.text(words, "niña", 0.8, 3.2, Box(40, 1300, 460, 140),
           text_style("Fredoka", 100, [fill("#E2557F")], weight=700, anim_in=tanim("pop", duration=0.4)),
           editable=False)
    t.text(words, "niño", 1.0, 3.0, Box(580, 1300, 460, 140),
           text_style("Fredoka", 100, [fill("#2E7DB8")], weight=700, anim_in=tanim("pop", duration=0.4)),
           editable=False)
    counts = t.track("text", "Cuenta")
    for i, n in enumerate("321"):
        t.text(counts, n, 4.0 + i * 0.5, 0.5, centered(540, 960, 800, 800),
               text_style("Fredoka", 420, [shadow("#000000", 0, 10, 0, 0.4), fill("#FFFFFF")], weight=700,
                          keyframes={"pixelSize": keys([(0, 800, "snap"), (0.16, 420)])}), editable=False)
    t.text(words, "¡Es niña!", 5.6, 3.4, Box(40, 1300, 1000, 300),
           text_style("Fredoka", 190, [shadow("#B8325E", 0, 10, 0, 0.9), stroke(12, "#FFFFFF"), fill("#FF4F8B")],
                      weight=700, anim_in=tanim("stamp", duration=0.45), anim_loop=tanim("pulse", amount=4, speed=1.2)),
           label="Resultado")
    t.text(words, "llega en abril", 6.2, 2.8, Box(40, 1620, 1000, 100),
           text_style("Fredoka", 60, [fill("#FFFFFF")], weight=600, anim_in=tanim("rise", duration=0.5)), label="Fecha")
    confetti(t, 12, ["#FF4F8B", "#FFFFFF", "#FFD23F", "#FF8FB1"], 5.5, 9.0, lanes=3)
    flash = t.track("shape", "Destello")
    t.solid(flash, "#FFFFFF", 5.5, 0.4, FULL, opacity=keys([(0, 0.95, "out"), (0.4, 0.0)]))
    t.adjust([effect("beat_shake", animated={"amount": spikes([5.5], 1.0, 0.5)}, rotation=0.4)], name="Golpe")
    t.song("my-giant-bunny-friend", 0.0, 0.85)
    return t


def baby_shower() -> Template:
    """Mint sky with drifting clouds, three round photos that pop in turn, an invitation card."""
    t = Template("baby-shower", "Baby shower", "Baby shower", "celebration", 10.0,
                 order=1304, tags=["baby shower", "bebé", "invitación", "fiesta", "embarazo"], thumb_at=6.4)
    t.solid(t.track("shape", "Cielo"), "#CFEDE3",
            layers=[gradient([(0, "#CFEDE3"), (1, "#FFF6E9")], angle=90), no_stroke()])
    rng = random.Random(5)
    for k, (y, size, speed) in enumerate(((330, 300, 70), (1180, 380, 50), (1760, 260, 90))):
        clouds = t.track("shape", f"Nubes {k + 1}")
        x0 = rng.uniform(-100, 600)
        t.solid(clouds, "#FFFFFF", 0.0, 10.0, centered(x0, y, size, size * 0.6),
                [(0, {}, "linear"), (10.0, {"dx": speed * 10})], kind="cloud", alpha=0.9)
    spots = [("baby-02", 540, 860, 640, "Bebé", 0.4), ("pregnant-03", 850, 470, 300, "Pancita", 1.2),
             ("family-02", 230, 1250, 320, "Familia", 1.8)]
    for i, (sample, x, y, d, label, at) in enumerate(spots):
        rings = t.track("shape", f"Aro {i + 1}")
        t.solid(rings, "#FFFFFF", at, 10 - at, centered(x, y, d + 34, d + 34), pop(0, 0.5), kind="ellipse",
                layers=[shadow("#4F7C6F", 0, 10, 26, 0.25), fill("#FFFFFF"), no_stroke()])
        photos = t.track("video", f"Foto {i + 1}")
        clip = t.photo(photos, sample, at, 10 - at, centered(x, y, d, d),
                       pop(0, 0.5) + [(10 - at, {"s": 1.04})], label=label)
        t.mask(photos, clip, "ellipse")
    card = t.track("shape", "Tarjeta")
    t.solid(card, "#FFFFFF", 2.4, 7.6, centered(540, 1560, 900, 300), [(0, {"dy": 500}, "out"), (0.6, {})],
            radius=48, kind="rounded-rectangle", layers=[shadow("#4F7C6F", 0, 12, 30, 0.22), fill("#FFFFFF"), no_stroke()])
    words = t.track("text", "Textos")
    t.text(words, "Baby shower", 0.2, 9.8, Box(40, 90, 1000, 220),
           text_style("Cookie", 170, [shadow("#FFFFFF", 0, 0, 14, 0.9), fill("#E58FA0")], weight=400,
                      anim_in=tanim("blur-in", duration=0.9, blur=16)), label="Título")
    t.text(words, "para Mateo", 0.8, 9.2, Box(560, 1080, 500, 120),
           text_style("Baloo 2", 72, [fill("#4F7C6F")], weight=700, anim_in=tanim("pop", duration=0.4, unit="word",
                                                                                   stagger=0.1)), label="Nombre")
    info = t.track("text", "Datos")
    t.text(info, "Sábado 20 de marzo · 4 p. m.", 2.8, 7.2, Box(120, 1440, 840, 100),
           text_style("Baloo 2", 54, [fill("#4F7C6F")], weight=700, anim_in=tanim("fade", duration=0.5)), label="Fecha")
    t.text(info, "Casa de los abuelos, Arequipa", 3.1, 6.9, Box(120, 1550, 840, 90),
           text_style("Baloo 2", 44, [fill("#E58FA0")], weight=600, anim_in=tanim("fade", duration=0.5)), label="Lugar")
    t.text(info, "¡te esperamos!", 3.4, 6.6, Box(120, 1640, 840, 80),
           text_style("Baloo 2", 40, [fill("#8AA79E")], weight=500, anim_in=tanim("fade", duration=0.5)), label="Nota")
    t.adjust([effect("bling_sparkle", intensity=0.4, density=0.3, threshold=0.82, colorize=0.4)], name="Brillos")
    t.song("llama-in-pajama", 0.0, 0.8)
    return t


def primer_anio_bebe() -> Template:
    """Month by month: twelve quick cards with a numbered badge, then the first birthday photo."""
    t = Template("primer-anio-bebe", "Mi primer añito: mes a mes", "Baby's first year, month by month",
                 "celebration", 14.0, order=1305, tags=["bebé", "primer año", "mes a mes", "cumpleaños", "familia"],
                 thumb_at=13.0, background="#FFE8A3")
    t.solid(t.track("shape", "Fondo"), "#FFE8A3",
            layers=[gradient([(0, "#FFF1C4"), (1, "#FFD97A")], angle=90), no_stroke()])
    samples = ["baby-01", "baby-02", "baby-03", "family-02"]
    each = 0.85
    frames = t.track("shape", "Tarjeta")
    photos = t.track("video", "Meses")
    for m in range(12):
        start = 1.5 + m * each
        tilt = 3 if m % 2 else -3
        land = [(0, {"s": 1.12, "dy": 40}, "snap"), (0.2, {}, "linear"), (each, {"s": 1.02})]
        t.solid(frames, "#FFFFFF", start, each, centered(540, 880, 860, 1080), land, radius=40,
                kind="rounded-rectangle", layers=[shadow("#9a7a1a", 0, 14, 30, 0.3), fill("#FFFFFF"), no_stroke()],
                rotation=keys([(0, tilt)]))
        t.photo(photos, samples[m % 4], start, each, centered(540, 860, 800, 980), land, label=f"Mes {m + 1}",
                rotation=keys([(0, tilt)]))
    badge = t.track("shape", "Insignia")
    numbers = t.track("text", "Mes")
    for m in range(12):
        start = 1.5 + m * each
        t.solid(badge, "#2E5E8C", start, each, centered(540, 1570, 250, 250),
                [(0, {"s": 0.6}, "back"), (0.25, {})], kind="ellipse",
                layers=[shadow("#1d3a57", 0, 8, 0, 0.6), fill("#2E5E8C"), no_stroke()])
        t.text(numbers, f"{m + 1}\nmes{'es' if m else ''}", start, each, centered(540, 1570, 250, 250),
               text_style("Sniglet", 100, [fill("#FFFFFF")], weight=800, line=0.8,
                          accent={"rule": "none"}), editable=False)
    t.solid(t.track("shape", "Marco final"), "#FFFFFF", 11.7, 2.3, centered(540, 880, 900, 1140),
            [(0, {"s": 0.5}, "back"), (0.5, {})], radius=48, kind="rounded-rectangle",
            layers=[shadow("#9a7a1a", 0, 16, 40, 0.35), fill("#FFFFFF"), no_stroke()])
    final = t.track("video", "Cumple")
    t.photo(final, "baby-02", 11.7, 2.3, centered(540, 860, 840, 1040),
            [(0, {"s": 0.5}, "back"), (0.5, {}, "linear"), (2.3, {"s": 1.04})], label="Foto del cumple")
    words = t.track("text", "Títulos")
    title = [shadow("#2E5E8C", 0, 8, 0, 0.9), stroke(10, "#FFFFFF"), fill("#2E5E8C")]
    t.text(words, "Mi primer año", 0.15, 1.35, Box(40, 680, 1000, 420),
           text_style("Sniglet", 170, title, weight=800, line=0.95,
                      anim_in=tanim("bounce", duration=0.6, unit="word", stagger=0.15),
                      anim_out=tanim("shrink", duration=0.25)), label="Título")
    t.text(words, "¡Feliz primer añito!", 11.9, 2.1, Box(40, 1450, 1000, 300),
           text_style("Sniglet", 120, title, weight=800, line=0.95, anim_in=tanim("pop", duration=0.5, unit="word",
                                                                                 stagger=0.12)), label="Cierre")
    t.text(words, "Mateo", 12.2, 1.8, Box(40, 140, 1000, 180),
           text_style("Sniglet", 140, [shadow("#9a7a1a", 0, 6, 0, 0.5), fill("#FFFFFF")], weight=800,
                      anim_in=tanim("drop", duration=0.5)), label="Nombre")
    confetti(t, 44, ["#2E5E8C", "#FFFFFF", "#F28C8C", "#7CC6A4"], 11.7, 14.0, lanes=2)
    t.song("dance-of-the-tuba-plum-fairy", 0.0, 0.85)
    return t


# --- Couples and friends -------------------------------------------------------------------------


def aniversario_pareja() -> Template:
    """A strip of polaroids glides past on wine red while the years count shows below in gold."""
    t = Template("aniversario-pareja", "Aniversario de pareja", "Couple anniversary", "celebration", 12.0,
                 order=1306, tags=["aniversario", "pareja", "amor", "novios", "años juntos"], thumb_at=9.4,
                 background="#2B0F1A")
    t.solid(t.track("shape", "Fondo"), "#2B0F1A",
            layers=[gradient([(0, "#4A1426"), (1, "#1E0A12")], angle=90), no_stroke()])
    samples = ["couple-01", "couple-03", "couple-04", "couple-07", "couple-08"]
    pitch, travel = 620, -3120
    for k in range(7):
        x = 540 + k * pitch
        tilt = 3 if k % 2 else -3
        motion = [(0, {}, "linear"), (12.0, {"dx": travel})]
        rot = keys([(0, tilt)])
        frames = t.track("shape", f"Polaroid {k + 1}")
        t.solid(frames, "#FFFFFF", 0, 12.0, centered(x, 730, 560, 760), motion, radius=4,
                layers=[shadow("#000000", 0, 16, 34, 0.45), fill("#FFF9F2"), no_stroke()], rotation=rot)
        photos = t.track("video", f"Foto {k + 1}")
        if k < len(samples):
            t.photo(photos, samples[k], 0, 12.0, centered(x, 690, 520, 640), motion, rotation=rot)
        else:
            reuse = f"p{k - len(samples) + 1}"
            t.photo(photos, samples[k - len(samples)], 0, 12.0, centered(x, 690, 520, 640), motion, reuse=reuse,
                    rotation=rot)
    rng = random.Random(9)
    hearts = t.track("shape", "Corazones")
    at = 0.5
    while at < 11.0:
        size = rng.uniform(30, 56)
        dur = rng.uniform(2.5, 3.5)
        t.solid(hearts, "#D9B26F", at, min(dur, 12 - at), centered(rng.uniform(80, 1000), 1960, size, size),
                [(0, {}, "linear"), (dur, {"dy": -900})], kind="heart",
                opacity=keys([(0, 0.8), (dur, 0.0)]))
        at += rng.uniform(0.6, 1.1)
    gold = [shadow("#000000", 0, 6, 14, 0.5), gradient([(0, "#F7E3B0"), (0.5, "#D9B26F"), (1, "#A9802F")], angle=90)]
    words = t.track("text", "Textos")
    t.text(words, "Feliz aniversario", 0.3, 11.7, Box(40, 1150, 1000, 200),
           text_style("Allura", 140, [fill("#F3D9A4")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.8, unit="character", stagger=0.04)), label="Título")
    t.text(words, "5 años", 1.4, 10.6, Box(40, 1340, 1000, 260),
           text_style("Bodoni Moda", 210, gold, weight=700, anim_in=tanim("zoom-out", duration=0.8)), label="Años")
    t.text(words, "1826 días juntos y contando", 2.4, 9.6, Box(40, 1610, 1000, 90),
           text_style("Bodoni Moda", 48, [fill("#F3D9A4")], weight=500, spacing=4, case="upper",
                      anim_in=tanim("typewriter", duration=1.2, unit="character")), label="Días")
    t.adjust([effect("stylize.vignette", amount=0.6, softness=1.0),
              effect("stylize.film_grain", amount=0.15, grainSize=1.5)], name="Ambiente")
    t.song("alls-fair-in-love", 0.0, 0.8)
    return t


def mejores_amigas() -> Template:
    """«Ella / yo»: two photos slap in from opposite sides every two seconds, then the best one fills the screen."""
    t = Template("mejores-amigas", "Mejores amigas", "Best friends", "reels", 10.0,
                 order=1307, tags=["amigas", "mejores amigas", "besties", "amistad", "bff"], thumb_at=4.6,
                 background="#C7B8FF")
    t.solid(t.track("shape", "Fondo"), "#C7B8FF",
            layers=[gradient([(0, "#D8CCFF"), (1, "#B4A0FF")], angle=135), no_stroke()])
    pairs = [("friends-09", "friends-03"), ("friends-08", "friends-01"), ("friends-12", "friends-10")]
    top, bottom = Box(70, 230, 940, 700), Box(70, 990, 940, 700)
    frames = t.track("shape", "Bordes")
    frames2 = t.track("shape", "Bordes")
    tops = t.track("video", "Ella")
    bottoms = t.track("video", "Yo")
    for i, (a, b) in enumerate(pairs):
        start = i * 2.0
        tilt = -2 if i % 2 else 2
        from_left = [(0, {"dx": -1200}, "snap"), (0.25, {}, "linear"), (2.0, {"s": 1.03})]
        from_right = [(0.15, {"dx": 1200}, "snap"), (0.4, {}, "linear"), (2.0, {"s": 1.03})]
        from_right = [(0, {"dx": 1200}, "linear")] + from_right
        for track, box, motion, angle in ((frames, top, from_left, tilt), (frames2, bottom, from_right, -tilt)):
            t.solid(track, "#FFFFFF", start, 2.0, centered(box.cx, box.cy, box.w + 30, box.h + 30), motion, radius=22,
                    kind="rounded-rectangle", layers=[shadow("#3b2a7a", 0, 12, 0, 0.6), fill("#FFFFFF"), no_stroke()],
                    rotation=keys([(0, angle)]))
        t.photo(tops, a, start, 2.0, top, from_left, label=f"Ella {i + 1}", rotation=keys([(0, tilt)]))
        t.photo(bottoms, b, start, 2.0, bottom, from_right, label=f"Yo {i + 1}", rotation=keys([(0, -tilt)]))
    final = t.track("video", "Final")
    t.photo(final, "friends-11", 6.0, 4.0, FULL, [(0, {"s": 1.25}, "snap"), (0.3, {"s": 1.05}, "linear"),
                                                   (4.0, {"s": 1.0})], label="Juntas")
    stickers = t.track("shape", "Stickers")
    stickers2 = t.track("shape", "Stickers")
    tags = t.track("text", "Etiquetas")
    tags2 = t.track("text", "Etiquetas")
    for i in range(3):
        start = i * 2.0
        pill(t, stickers, "#FF7A00", start + 0.25, 1.75, centered(250, 280, 300, 110), pop(0, 0.3),
             rotation=keys([(0, -8)]))
        pill(t, stickers2, "#FF7A00", start + 0.4, 1.6, centered(830, 1640, 240, 110), pop(0, 0.3),
             rotation=keys([(0, 7)]))
        marker = text_style("Permanent Marker", 64, [fill("#FFFFFF")], weight=400)
        t.text(tags, "ella", start + 0.3, 1.7, centered(250, 280, 300, 110), marker, editable=i == 0,
               label="Etiqueta 1", rotation=keys([(0, -8)]))
        t.text(tags2, "yo", start + 0.45, 1.55, centered(830, 1640, 240, 110), marker, editable=i == 0,
               label="Etiqueta 2", rotation=keys([(0, 7)]))
    words = t.track("text", "Títulos")
    t.text(words, "mi persona favorita", 6.3, 3.7, Box(60, 1300, 960, 400),
           text_style("Permanent Marker", 130, [shadow("#3b2a7a", 0, 10, 0, 0.8), stroke(10, "#FF7A00"),
                                                 fill("#FFFFFF")], weight=400, line=0.95,
                      anim_in=tanim("stamp", duration=0.45, unit="word", stagger=0.15)), label="Título",
           rotation=keys([(0, -4)]))
    t.text(words, "@tuamiga", 7.2, 2.8, Box(60, 1720, 960, 90),
           text_style("Permanent Marker", 56, [shadow("#000000", 0, 4, 10, 0.6), fill("#FFFFFF")], weight=400,
                      anim_in=tanim("typewriter", duration=0.6, unit="character")), label="Usuario")
    t.solid(t.track("shape", "Destello"), "#FFFFFF", 6.0, 0.3, FULL, opacity=keys([(0, 0.8, "out"), (0.3, 0.0)]))
    t.song("and-just-like-that", 0.0, 0.85)
    return t


# --- Trips ---------------------------------------------------------------------------------------


def dia_de_playa() -> Template:
    """Full-screen beach shots wiping upward, a sun behind the title and rolling waves at the bottom."""
    t = Template("dia-de-playa", "Modo playa", "Beach mode", "reels", 10.0,
                 order=1308, tags=["playa", "verano", "vacaciones", "mar", "atardecer"], thumb_at=2.6)
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(["beach-04", "beach-06", "beach-03", "beach-05", "beach-02"]):
        clips.append(t.photo(photos, sample, i * 2.0, 2.0, FULL, [(0, {"s": 1.1}, "linear"), (2.0, {"s": 1.0})]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "wipe_up", 0.4)
    t.adjust([effect("color.basic", temperature=0.15, vibrance=0.2, contrast=0.05)], name="Sol")
    sun = t.track("shape", "Sol")
    t.solid(sun, "#FFD166", 0.2, 9.8, centered(760, 420, 300, 300),
            [(0, {"s": 0.0}, "back"), (0.6, {}, "smooth"), (5.0, {"s": 1.08}, "smooth"), (9.8, {})], kind="ellipse",
            layers=[glow("#FFB703", 60, 0.9), fill("#FFD166"), no_stroke()])
    for k, (colour, alpha, y, amp, period) in enumerate((("#90E0EF", 0.85, 1700, 140, 2.5),
                                                         ("#00B4D8", 0.9, 1770, 180, 3.2),
                                                         ("#0077B6", 1.0, 1850, 120, 2.0))):
        waves = t.track("shape", f"Ola {k + 1}")
        swing = [(i * period / 2, {"dx": amp if i % 2 else -amp}, "inout") for i in range(int(10 / (period / 2)) + 2)]
        t.solid(waves, colour, 0, 10.0, centered(540, y + 200, 2600, 520), swing, kind="ellipse", alpha=alpha)
    words = t.track("text", "Títulos")
    t.text(words, "modo playa", 0.3, 9.7, Box(40, 300, 1000, 260),
           text_style("Righteous", 170, [shadow("#0077B6", 0, 10, 0, 0.9), fill("#FFFFFF")], weight=400, line=0.9,
                      anim_in=tanim("bounce", duration=0.6, unit="character", stagger=0.05),
                      anim_loop=tanim("float", amount=0.1, speed=0.5)), label="Título")
    t.text(words, "Máncora, Piura", 0.9, 9.1, Box(40, 1790, 1000, 90),
           text_style("Righteous", 60, [fill("#FFFFFF")], weight=400, spacing=3,
                      anim_in=tanim("slide-up", duration=0.5)), label="Lugar")
    t.text(words, "verano 2027", 1.3, 8.7, Box(40, 540, 1000, 90),
           text_style("Righteous", 56, [shadow("#0077B6", 0, 4, 0, 0.9), fill("#FFD166")], weight=400, spacing=6,
                      anim_in=tanim("fade", duration=0.6)), label="Fecha")
    t.song("adding-the-sun", 0.0, 0.85)
    return t


def mochilero_por_peru() -> Template:
    """Backpacking route: a day per stop, the route bar fills and the pin hops from dot to dot."""
    t = Template("mochilero-por-peru", "Mochilero por Perú", "Backpacking Peru", "reels", 15.0,
                 order=1309, tags=["viaje", "mochilero", "perú", "cusco", "ruta", "aventura"], thumb_at=4.0)
    stops = [("travel-07", "Cusco"), ("travel-01", "Salkantay"), ("travel-02", "Vinicunca"),
             ("travel-06", "Valle Sagrado"), ("travel-09", "Titicaca"), ("travel-10", "Pisac")]
    each = 2.5
    photos = t.track("video", "Paradas")
    clips = []
    for i, (sample, place) in enumerate(stops):
        drift = 70 if i % 2 else -70
        clips.append(t.photo(photos, sample, i * each, each, FULL,
                             [(0, {"s": 1.12, "dx": drift}, "linear"), (each, {"s": 1.02})], label=place))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "push_left", 0.4)
    t.adjust([effect("color.basic", vibrance=0.2, contrast=0.08),
              effect("stylize.film_grain", amount=0.14, grainSize=1.6)], name="Color")
    shade = t.track("shape", "Sombra")
    t.solid(shade, "#000000", 0, 15.0, Box(0, 1500, 1080, 420),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.6)], angle=90), no_stroke()])
    t.solid(t.track("shape", "Sombra"), "#000000", 0, 15.0, Box(0, 0, 1080, 520),
            layers=[gradient([(0, "#000000", 0.55), (1, "#000000", 0.0)], angle=90), no_stroke()])
    route = Box(110, 1757, 860, 6)
    t.solid(t.track("shape", "Ruta"), "#FFFFFF", 0, 15.0, route, alpha=0.4)
    t.solid(t.track("shape", "Avance"), "#F2C14E", 0, 15.0, route, grow_left(route, 15.0))
    dots = [route.x + route.w * i / (len(stops) - 1) for i in range(len(stops))]
    for i, x in enumerate(dots):
        t.solid(t.track("shape", f"Punto {i + 1}"), "#F2C14E", i * each, 15.0 - i * each,
                centered(x, route.cy, 30, 30), pop(0, 0.35), kind="ellipse",
                layers=[stroke(4, "#2D2A26"), fill("#F2C14E")])
    hop = []
    for i, x in enumerate(dots):
        if i:
            hop.append((i * each - 0.35, {"dx": dots[i - 1] - dots[0]}, "back"))
        hop.append((i * each, {"dx": x - dots[0]}, "linear"))
    t.solid(t.track("shape", "Pin"), "#E4572E", 0, 15.0, centered(dots[0], route.cy - 52, 56, 56), hop,
            kind="ellipse", layers=[shadow("#000000", 0, 4, 10, 0.5), stroke(8, "#FFFFFF"), fill("#E4572E")])
    days = t.track("text", "Días")
    places = t.track("text", "Lugares")
    for i, (_, place) in enumerate(stops):
        start = i * each + 0.15
        t.text(days, f"DÍA {i + 1}", start, each - 0.15, Box(70, 150, 940, 200),
               text_style("Big Shoulders Display", 170, [shadow("#000000", 0, 6, 20, 0.5), fill("#F2C14E")],
                          weight=900, align="left", spacing=2, anim_in=tanim("slide-up", duration=0.35)),
               editable=False)
        t.text(places, place, start + 0.1, each - 0.25, Box(70, 340, 940, 120),
               text_style("Big Shoulders Display", 90, [shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")],
                          weight=700, align="left", case="upper", spacing=4,
                          anim_in=tanim("wipe", duration=0.45, angle=0)), label=f"Lugar {i + 1}")
    t.text(t.track("text", "Título"), "mochileando por Perú", 0.2, 14.8, Box(110, 1600, 860, 110),
           text_style("Kalam", 64, [shadow("#000000", 0, 3, 10, 0.6), fill("#FFFFFF")], weight=700, align="left",
                      anim_in=tanim("typewriter", duration=1.0, unit="character")), label="Título")
    t.song("one-step-closer", 0.0, 0.85)
    return t


# --- Style and routines --------------------------------------------------------------------------


def ootd_outfit() -> Template:
    """OOTD slams in lime, then four looks cut on the beat inside a lime frame, each with a pointed label."""
    t = Template("ootd-outfit", "OOTD: outfit del día", "OOTD: outfit of the day", "reels", 8.0,
                 order=1310, tags=["outfit", "ootd", "moda", "look", "estilo"], thumb_at=5.0, background="#0F0F0F")
    t.solid(t.track("shape", "Fondo"), "#0F0F0F")
    frame_box = Box(60, 170, 960, 1420)
    photo_box = Box(76, 186, 928, 1388)
    t.solid(t.track("shape", "Marco"), "#D7FF3A", 1.0, 7.0, frame_box, [(0, {"s": 1.06}, "snap"), (0.2, {})])
    photos = t.track("video", "Looks")
    looks = [("outfit-04", "chaqueta de jean", (720, 640), "left"), ("outfit-01", "top floral", (420, 760), "right"),
             ("fashion-02", "gorra y casaca", (560, 520), "left"), ("fashion-04", "lentes de sol", (520, 560), "right")]
    each = 1.75
    for i, (sample, _, _, _) in enumerate(looks):
        t.photo(photos, sample, 1.0 + i * each, each, photo_box,
                [(0, {"s": 1.1}, "snap"), (0.18, {}, "linear"), (each, {"s": 1.03})], label=f"Look {i + 1}")
    dots = t.track("shape", "Punto")
    lines = t.track("shape", "Línea")
    callouts = t.track("text", "Prendas")
    counter = t.track("text", "Contador")
    for i, (_, garment, (x, y), side) in enumerate(looks):
        start = 1.0 + i * each + 0.25
        dur = each - 0.25
        t.solid(dots, "#D7FF3A", start, dur, centered(x, y, 34, 34), pop(0, 0.3), kind="ellipse",
                layers=[stroke(5, "#0F0F0F"), fill("#D7FF3A")])
        length = 260
        line = Box(x - length if side == "left" else x, y - 2, length, 4)
        sign = 1 if side == "left" else -1
        t.solid(lines, "#D7FF3A", start + 0.1, dur - 0.1, line,
                [(0, {"sx": 0.0, "dx": sign * length / 2}, "out"), (0.3, {})])
        label_box = Box(x - length - 400, y - 50, 400, 100) if side == "left" else Box(x + length, y - 50, 400, 100)
        label_box = Box(max(80, min(label_box.x, 1040 - label_box.w)), label_box.y, label_box.w, label_box.h)
        t.text(callouts, garment, start + 0.25, dur - 0.25, label_box,
               text_style("DM Sans", 44, [fill("#0F0F0F")], weight=700, box=("#D7FF3A", 1.0), box_pad=14,
                          anim_in=tanim("slide-left" if side == "right" else "slide-right", duration=0.3)),
               label=f"Prenda {i + 1}")
        t.text(counter, f"LOOK {i + 1}/4", 1.0 + i * each, each, Box(60, 1620, 500, 110),
               text_style("Archivo Black", 70, [fill("#FFFFFF")], weight=400, align="left"), editable=False)
    words = t.track("text", "Títulos")
    t.text(words, "OOTD", 0.0, 1.0, Box(0, 700, 1080, 520),
           text_style("Archivo Black", 330, [fill("#D7FF3A")], weight=400,
                      keyframes={"pixelSize": keys([(0, 800, "snap"), (0.2, 330)])}), label="Título")
    t.text(words, "look casual · lunes", 1.2, 6.8, Box(520, 1630, 500, 90),
           text_style("DM Sans", 44, [fill("#D7FF3A")], weight=500, align="right",
                      anim_in=tanim("fade", duration=0.4)), label="Ocasión")
    cuts = [1.0 + i * each for i in range(4)]
    t.adjust([effect("strobe_flash", animated={"flash": spikes(cuts, 0.7, 0.2)}, tint=0.1),
              effect("beat_shake", animated={"amount": spikes(cuts, 0.6, 0.25)}, rotation=0.3)], name="Golpes")
    t.song("fake-it-til-you-fake-it", 0.0, 0.85)
    return t


def grwm_arreglate() -> Template:
    """Get ready with me: a photo window on pink and a checklist that ticks off step by step."""
    t = Template("grwm-arreglate-conmigo", "GRWM: arréglate conmigo", "GRWM: get ready with me", "reels", 12.0,
                 order=1311, tags=["grwm", "maquillaje", "arréglate conmigo", "belleza", "rutina"], thumb_at=10.6,
                 background="#FFD1DC")
    t.solid(t.track("shape", "Fondo"), "#FFD1DC",
            layers=[gradient([(0, "#FFE3EA"), (1, "#FFC2D1")], angle=90), no_stroke()])
    t.solid(t.track("shape", "Marco"), "#FFFFFF", 0, 12.0, Box(50, 110, 980, 1200), radius=44,
            kind="rounded-rectangle", layers=[shadow("#8E2C48", 0, 14, 36, 0.22), fill("#FFFFFF"), no_stroke()])
    photos = t.track("video", "Pasos")
    window = Box(70, 130, 940, 1160)
    clips = []
    for i, (sample, label) in enumerate((("makeup-01", "Skincare"), ("makeup-03", "Base"), ("makeup-02", "Labial"),
                                         ("selfie-02", "Lista"))):
        clips.append(t.photo(photos, sample, i * 3.0, 3.0, window, [(0, {"s": 1.0}, "linear"), (3.0, {"s": 1.05})],
                             label=label))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.4)
    t.solid(t.track("shape", "Lista"), "#FFFFFF", 0.2, 11.8, Box(50, 1350, 980, 480),
            [(0, {"dy": 600}, "out"), (0.6, {})], radius=44, kind="rounded-rectangle",
            layers=[shadow("#8E2C48", 0, 14, 36, 0.22), fill("#FFFFFF"), no_stroke()])
    pill(t, t.track("shape", "Sello"), "#8E2C48", 0.3, 11.7, Box(100, 170, 300, 90), pop(0, 0.4))
    steps = ["Skincare", "Base y rubor", "Labial rojo", "¡Lista!"]
    boxes = t.track("shape", "Casillas")
    ticks = t.track("shape", "Marcas")
    rows = t.track("text", "Pasos")
    marks = t.track("text", "Visto")
    for i, step in enumerate(steps):
        y = 1400 + i * 105
        slide = [(0, {"dy": 600}, "out"), (0.6, {})]
        t.solid(boxes, "#8E2C48", 0.2, 11.8, Box(120, y + 15, 62, 62), slide, radius=14,
                kind="rounded-rectangle", layers=outline(5, "#8E2C48"))
        done = 2.6 + i * 3.0 if i < 3 else 11.0
        t.solid(ticks, "#8E2C48", done, 12.0 - done, Box(120, y + 15, 62, 62), pop(0, 0.35), radius=14,
                kind="rounded-rectangle")
        t.text(marks, "✓", done, 12.0 - done, Box(120, y + 15, 62, 62),
               text_style("Poppins", 46, [fill("#FFFFFF")], weight=800, anim_in=tanim("pop", duration=0.3)),
               editable=False)
        t.text(rows, step, 0.5 + i * 0.12, 11.5 - i * 0.12, Box(215, y, 780, 92),
               text_style("Josefin Sans", 56, [fill("#8E2C48")], weight=700, align="left",
                          anim_in=tanim("fade", duration=0.4)), label=f"Paso {i + 1}")
    words = t.track("text", "Títulos")
    t.text(words, "GRWM", 0.35, 11.65, Box(100, 170, 300, 90),
           text_style("Josefin Sans", 56, [fill("#FFFFFF")], weight=700, spacing=6), editable=False)
    t.text(words, "para la boda de mi prima", 0.6, 11.4, Box(80, 1110, 920, 170),
           text_style("Satisfy", 86, [shadow("#000000", 0, 4, 18, 0.6), fill("#FFFFFF")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.8, unit="character", stagger=0.03)), label="Ocasión")
    t.song("magic-in-the-garden", 0.0, 0.8)
    return t


def un_dia_en_mi_vida() -> Template:
    """Day in my life as stories: progress bars on top, a time pill and a caption for every moment."""
    t = Template("un-dia-en-mi-vida", "Un día en mi vida", "A day in my life", "reels", 15.0,
                 order=1312, tags=["un día en mi vida", "rutina", "vlog", "day in my life", "historias"],
                 thumb_at=7.8)
    moments = [("coffee-03", "07:00", "café y a empezar"), ("study-03", "09:00", "clases toda la mañana"),
               ("food-01", "13:00", "almuerzo con mamá"), ("cafe-01", "16:00", "turno en la cafetería"),
               ("friends-10", "20:00", "salida con los amigos"), ("selfie-04", "23:00", "y a dormir")]
    each = 2.5
    photos = t.track("video", "Momentos")
    for i, (sample, hour, _) in enumerate(moments):
        t.photo(photos, sample, i * each, each, FULL, [(0, {"s": 1.08, "dy": 30}, "linear"), (each, {"s": 1.0})],
                label=f"Momento {i + 1}")
    t.solid(t.track("shape", "Sombra"), "#000000", 0, 15.0, Box(0, 0, 1080, 380),
            layers=[gradient([(0, "#000000", 0.5), (1, "#000000", 0.0)], angle=90), no_stroke()])
    gap, n = 10, len(moments)
    width = (1080 - 2 * 40 - gap * (n - 1)) / n
    for i in range(n):
        bar = Box(40 + i * (width + gap), 60, width, 8)
        t.solid(t.track("shape", f"Barra {i + 1}"), "#FFFFFF", 0, 15.0, bar, radius=4, kind="rounded-rectangle",
                alpha=0.35)
        t.solid(t.track("shape", f"Avance {i + 1}"), "#FFFFFF", i * each, 15.0 - i * each, bar,
                grow_left(bar, each), radius=4, kind="rounded-rectangle")
    pills = t.track("shape", "Hora")
    hours = t.track("text", "Horas")
    captions = t.track("text", "Textos")
    for i, (_, hour, caption) in enumerate(moments):
        start = i * each + 0.15
        pill(t, pills, "#FFFFFF", start, each - 0.15, Box(60, 130, 250, 96), [(0, {"dx": -320}, "out"), (0.35, {})])
        t.text(hours, hour, start, each - 0.15, Box(60, 130, 250, 96),
               text_style("Outfit", 60, [fill("#111111")], weight=800), [(0, {"dx": -320}, "out"), (0.35, {})],
               label=f"Hora {i + 1}")
        t.text(captions, caption, start + 0.2, each - 0.35, Box(60, 1560, 960, 200),
               text_style("Outfit", 64, [fill("#111111")], weight=700, align="left", valign="bottom",
                          box=("#FFFFFF", 1.0), box_pad=16, box_radius=12,
                          anim_in=tanim("typewriter", duration=0.5, unit="character")), label=f"Texto {i + 1}")
    t.text(t.track("text", "Título"), "un día en mi vida", 0.2, 2.2, Box(60, 760, 960, 300),
           text_style("Outfit", 120, [shadow("#000000", 0, 6, 24, 0.6), fill("#FFFFFF")], weight=800, line=0.95,
                      anim_in=tanim("rise-by-word", duration=0.45, unit="word", stagger=0.12),
                      anim_out=tanim("fade", duration=0.3)), label="Título")
    t.song("from-page-to-practice", 0.0, 0.85)
    return t


def mi_mascota() -> Template:
    """Yellow and blue, a round photo that bounces to a new pet pose every beat-pair, paw prints walking past."""
    t = Template("mi-mascota", "Mi mascota", "My pet", "reels", 10.0,
                 order=1313, tags=["mascota", "perro", "perrito", "gato", "mi mejor amigo"], thumb_at=6.6,
                 background="#FFC93C")
    t.solid(t.track("shape", "Fondo"), "#FFC93C")
    # Paw prints walk up the left side, two visible at a time.
    for side in range(2):
        parts = [t.track("shape", f"Huella {side + 1}") for _ in range(5)]
        k = side
        while k * 0.6 < 9.4:
            at = k * 0.6
            x = 150 + (40 if k % 2 else -40) + (760 if (k // 6) % 2 else 0)
            y = 1800 - (k % 6) * 300
            for j, (dx, dy, w, h) in enumerate(((0, 30, 90, 76), (-50, -40, 32, 40), (-16, -62, 32, 40),
                                                (20, -62, 32, 40), (54, -40, 32, 40))):
                t.solid(parts[j], "#2B59C3", at, min(1.2, 10 - at), centered(x + dx, y + dy, w, h),
                        kind="ellipse", alpha=0.35, opacity=keys([(0, 1.0), (0.8, 1.0, "smooth"), (1.2, 0.0)]))
            k += 2
    circle = centered(540, 900, 820, 820)
    t.solid(t.track("shape", "Aro"), "#2B59C3", 0.2, 9.8, centered(540, 900, 880, 880), pop(0, 0.5), kind="ellipse",
            layers=[shadow("#1a3a8a", 0, 16, 0, 0.6), fill("#2B59C3"), no_stroke()])
    photos = t.track("video", "Fotos")
    samples = ["pet-02", "pet-04", "pet-05", "pet-03", "pet-01"]
    each = 9.8 / len(samples)
    for i, sample in enumerate(samples):
        start = 0.2 + i * each
        motion = pop(0, 0.5) if i == 0 else [(0, {"s": 0.85}, "back"), (0.3, {})]
        clip = t.photo(photos, sample, start, each, circle, motion + [(each, {"s": 1.04})], label=f"Foto {i + 1}")
        t.mask(photos, clip, "ellipse")
    words = t.track("text", "Textos")
    t.text(words, "Toby", 0.5, 9.5, Box(40, 110, 1000, 300),
           text_style("Luckiest Guy", 230, [shadow("#1a3a8a", 0, 12, 0, 1.0), stroke(12, "#FFFFFF"), fill("#2B59C3")],
                      weight=400, anim_in=tanim("drop", duration=0.6), anim_loop=tanim("float", amount=0.12, speed=0.6)),
           label="Nombre")
    t.text(words, "el mejor perrito del mundo", 1.2, 8.8, Box(60, 1380, 960, 220),
           text_style("Luckiest Guy", 80, [stroke(8, "#FFFFFF"), fill("#2B59C3")], weight=400, line=1.0,
                      anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1)), label="Frase")
    pill(t, t.track("shape", "Edad"), "#FFFFFF", 2.0, 8.0, centered(540, 1690, 440, 110), pop(0, 0.4))
    t.text(t.track("text", "Edad"), "3 años de amor", 2.1, 7.9, centered(540, 1690, 440, 110),
           text_style("Luckiest Guy", 56, [fill("#2B59C3")], weight=400), label="Edad")
    t.song("frogs-legs-rag", 0.0, 0.85)
    return t


def diario_de_comida() -> Template:
    """A notebook page: four meal photos taped in one after another with handwritten notes, then a stamp."""
    t = Template("diario-de-comida", "Lo que comí hoy", "What I ate today", "collage", 10.0,
                 order=1314, tags=["comida", "lo que comí hoy", "diario", "food", "recetas"], thumb_at=9.0,
                 background="#FFFDF6")
    t.solid(t.track("shape", "Papel"), "#FFFDF6")
    t.solid(t.track("shape", "Margen"), "#F28B82", 0, 10.0, Box(96, 0, 4, 1920), alpha=0.8)
    meals = [("coffee-03", "desayuno", "8:00 · capuchino"), ("food-01", "almuerzo", "1:00 · ceviche"),
             ("coffee-01", "lonche", "5:00 · cafecito"), ("food-03", "cena", "8:30 · tiradito")]
    for i, (sample, meal, note) in enumerate(meals):
        start = 0.6 + i * 1.8
        y = 470 + i * 360
        left = i % 2 == 0
        x = 400 if left else 690
        tilt = -3 if left else 3
        drop = [(0, {"s": 1.3, "dy": -120}, "out"), (0.35, {})]
        rot = keys([(0, tilt * 2.5, "out"), (0.35, tilt)])
        t.solid(t.track("shape", f"Foto papel {i + 1}"), "#FFFFFF", start, 10 - start, centered(x, y, 560, 340), drop,
                layers=[shadow("#5a4a2a", 3, 10, 22, 0.3), fill("#FFFFFF"), no_stroke()], rotation=rot)
        t.photo(t.track("video", f"Foto {i + 1}"), sample, start, 10 - start, centered(x, y, 520, 300), drop,
                label=meal.capitalize(), rotation=rot)
        t.solid(t.track("shape", f"Cinta {i + 1}"), "#FFE08A", start + 0.35, 9.65 - start,
                centered(x, y - 170, 160, 44), alpha=0.8, rotation=keys([(0, tilt * 3)]))
        tx = 690 if left else 120
        words = t.track("text", f"Nota {i + 1}")
        t.text(words, meal, start + 0.4, 9.6 - start, Box(tx, y - 110, 300, 100),
               text_style("Kalam", 68, [fill("#2E2E2E")], weight=700, align="left",
                          anim_in=tanim("typewriter", duration=0.5, unit="character")), label=f"Comida {i + 1}",
               rotation=keys([(0, -tilt)]))
        t.text(t.track("text", f"Detalle {i + 1}"), note, start + 0.7, 9.3 - start, Box(tx, y - 10, 300, 120),
               text_style("Kalam", 40, [fill("#6B6B6B")], weight=400, align="left", line=1.0,
                          anim_in=tanim("fade", duration=0.4)), label=f"Detalle {i + 1}", rotation=keys([(0, -tilt)]))
    head = t.track("text", "Título")
    t.text(head, "lo que comí hoy", 0.1, 9.9, Box(130, 70, 900, 140),
           text_style("Kalam", 104, [fill("#2E2E2E")], weight=700, align="left",
                      anim_in=tanim("typewriter", duration=0.7, unit="character")), label="Título")
    t.text(head, "martes", 0.1, 9.9, Box(700, 210, 330, 80),
           text_style("Kalam", 50, [fill("#F28B82")], weight=700, align="right", anim_in=tanim("fade", duration=0.6)),
           label="Día")
    stamp = t.track("shape", "Sello")
    t.solid(stamp, "#F28B82", 8.0, 2.0, centered(800, 1560, 330, 330), [(0, {"s": 2.0}, "snap"), (0.2, {})],
            kind="ellipse", layers=outline(8, "#E5534B"), rotation=keys([(0, -12)]))
    t.text(t.track("text", "Sello"), "¡ñam!\n10/10", 8.0, 2.0, centered(800, 1560, 330, 330),
           text_style("Kalam", 80, [fill("#E5534B")], weight=700, line=0.95,
                      keyframes={"pixelSize": keys([(0, 160, "snap"), (0.2, 80)])}),
           label="Sello", rotation=keys([(0, -12)]))
    t.song("bebop-for-joey", 0.0, 0.85)
    return t


def progreso_gym() -> Template:
    """Training week: a slammed week number, then five days with a big orange day tag and filling day boxes."""
    t = Template("progreso-gym", "Semana de entreno", "Training week", "reels", 10.0,
                 order=1315, tags=["gym", "entreno", "fitness", "progreso", "rutina"], thumb_at=6.1,
                 background="#0D0D0D")
    days = [("LUN", "pecho y tríceps", "gym-01"), ("MAR", "piernas", "gym-02"), ("MIÉ", "espalda", "gym-04"),
            ("JUE", "cardio", "gym-05"), ("VIE", "brazos", "gym-01")]
    each = 1.6
    photos = t.track("video", "Días")
    for i, (_, _, sample) in enumerate(days):
        start = 1.0 + i * each
        t.photo(photos, sample, start, each, FULL, [(0, {"s": 1.18}, "snap"), (0.2, {"s": 1.04}, "linear"),
                                                     (each, {"s": 1.0})],
                label=f"Día {i + 1}", reuse="p1" if i == 4 else None,
                effects=[effect("color.basic", contrast=0.2, saturation=-0.25)])
    t.solid(t.track("shape", "Sombra"), "#000000", 1.0, 9.0, Box(0, 1300, 1080, 620),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.8)], angle=90), no_stroke()])
    tags = t.track("text", "Día")
    names = t.track("text", "Rutina")
    for i, (day, name, _) in enumerate(days):
        start = 1.0 + i * each
        t.text(tags, day, start, each, Box(50, 110, 700, 300),
               text_style("Teko", 300, [shadow("#000000", 0, 8, 20, 0.5), fill("#FF4D00")], weight=700, align="left",
                          line=0.85, keyframes={"pixelSize": keys([(0, 520, "snap"), (0.18, 300)])}), editable=False)
        t.text(names, name, start + 0.1, each - 0.1, Box(60, 1480, 960, 140),
               text_style("Teko", 110, [fill("#FFFFFF")], weight=600, align="left", case="upper",
                          anim_in=tanim("slide-up", duration=0.3)), label=f"Rutina {i + 1}")
    size, gap = 150, 30
    x0 = (1080 - 5 * size - 4 * gap) / 2
    for i in range(5):
        box = Box(x0 + i * (size + gap), 1660, size, 90)
        t.solid(t.track("shape", f"Casilla {i + 1}"), "#FFFFFF", 1.0, 9.0, box, radius=12, kind="rounded-rectangle",
                layers=outline(4, "#FFFFFF", 0.6))
        done = 1.0 + (i + 1) * each - 0.4
        t.solid(t.track("shape", f"Hecho {i + 1}"), "#FF4D00", done, 10.0 - done, box, pop(0, 0.3), radius=12,
                kind="rounded-rectangle")
    words = t.track("text", "Títulos")
    t.text(words, "SEMANA 12", 0.0, 1.0, Box(0, 640, 1080, 640),
           text_style("Teko", 300, [fill("#FF4D00")], weight=700, line=0.85,
                      keyframes={"pixelSize": keys([(0, 700, "snap"), (0.2, 300)])}), label="Semana")
    t.text(words, "5/5 cumplido", 9.0, 1.0, Box(0, 1440, 1080, 200),
           text_style("Teko", 150, [shadow("#000000", 0, 6, 0, 0.8), fill("#FF4D00")], weight=700, case="upper",
                      anim_in=tanim("stamp", duration=0.35)), label="Cierre")
    cuts = [1.0 + i * each for i in range(5)] + [9.0]
    t.adjust([effect("zoom_pulse", animated={"punch": spikes(cuts, 0.7, 0.3)}, blur=0.4),
              effect("beat_shake", animated={"amount": spikes(cuts, 0.8, 0.3)}, rotation=0.4)], name="Golpes")
    t.song("new-hero-in-town", 0.0, 0.9)
    return t


def estudia_conmigo() -> Template:
    """Lo-fi study session: sage card, a soft photo window and a pomodoro clock that ticks every second."""
    t = Template("estudia-conmigo", "Estudia conmigo", "Study with me", "reels", 12.0,
                 order=1316, tags=["estudia conmigo", "estudiar", "pomodoro", "universidad", "productividad"],
                 thumb_at=6.0, background="#E9EDE0")
    t.solid(t.track("shape", "Fondo"), "#E9EDE0")
    window = Box(70, 330, 940, 960)
    t.solid(t.track("shape", "Marco"), "#FFFFFF", 0, 12.0, Box(54, 314, 972, 992), radius=40,
            kind="rounded-rectangle", layers=[shadow("#3A5A40", 0, 12, 30, 0.2), fill("#FFFFFF"), no_stroke()])
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(["study-02", "study-03", "coffee-01"]):
        drift = 40 if i % 2 else -40
        clips.append(t.photo(photos, sample, i * 4.0, 4.0, window, [(0, {"s": 1.06, "dx": drift}, "linear"),
                                                                     (4.0, {"s": 1.0})], label=f"Foto {i + 1}"))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.8)
    t.adjust([effect("color.basic", fade=0.12, saturation=-0.15, temperature=0.06),
              effect("stylize.film_grain", amount=0.16, grainSize=1.8)], name="Lo-fi")
    words = t.track("text", "Títulos")
    t.text(words, "estudia conmigo", 0.2, 11.8, Box(70, 110, 940, 120),
           text_style("Lexend", 86, [fill("#3A5A40")], weight=700, align="left",
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.03)), label="Título")
    t.text(words, "sesión 1 de 4 · pomodoro", 0.6, 11.4, Box(70, 225, 940, 70),
           text_style("Lexend", 42, [fill("#6B8F71")], weight=500, align="left", anim_in=tanim("fade", duration=0.6)),
           label="Sesión")
    clock = t.track("text", "Reloj")
    for s in range(12):
        t.text(clock, f"24:{59 - s:02d}" if s else "25:00", s * 1.0, 1.0, Box(70, 1330, 940, 300),
               text_style("Lexend", 240, [fill("#3A5A40")], weight=600, spacing=-4), editable=False)
    bar = Box(70, 1650, 940, 18)
    t.solid(t.track("shape", "Barra"), "#3A5A40", 0, 12.0, bar, radius=9, kind="rounded-rectangle", alpha=0.18)
    t.solid(t.track("shape", "Avance"), "#3A5A40", 0, 12.0, bar, grow_left(bar, 12.0), radius=9,
            kind="rounded-rectangle")
    t.text(words, "celular en otra habitación", 1.0, 11.0, Box(70, 1710, 940, 80),
           text_style("Lexend", 40, [fill("#6B8F71")], weight=500, anim_in=tanim("fade", duration=0.6)),
           label="Regla")
    t.song("icicles-melting", 0.0, 0.75)
    return t


def domingo_en_familia() -> Template:
    """Warm sunday: a spinning sun, three tall panels sliding in from top and bottom, then one wide photo."""
    t = Template("domingo-en-familia", "Domingo en familia", "Family Sunday", "collage", 12.0,
                 order=1317, tags=["familia", "domingo", "abuelos", "hogar", "recuerdos"], thumb_at=3.6,
                 background="#FFF3E0")
    t.solid(t.track("shape", "Fondo"), "#FFF3E0",
            layers=[gradient([(0, "#FFF6E8"), (1, "#FFE2BF")], angle=90), no_stroke()])
    t.solid(t.track("shape", "Rayos"), "#F4A259", 0, 12.0, centered(900, 230, 420, 420), kind="burst", points=16,
            innerRatio=0.7, alpha=0.45, rotation=keys([(0, 0), (12.0, 90)]))
    t.solid(t.track("shape", "Sol"), "#F4A259", 0, 12.0, centered(900, 230, 230, 230), pop(0, 0.6), kind="ellipse")
    panel_w, gap = 312, 18
    x0 = (1080 - 3 * panel_w - 2 * gap) / 2
    for i, sample in enumerate(["family-04", "family-05", "family-02"]):
        box = Box(x0 + i * (panel_w + gap), 430, panel_w, 1100)
        start = 0.3 + i * 0.35
        enter = -1500 if i % 2 == 0 else 1500
        motion = [(0, {"dy": enter}, "out"), (0.7, {}, "linear"), (5.5 - start, {}, "in"),
                  (6.1 - start, {"dy": -enter})]
        t.photo(t.track("video", f"Panel {i + 1}"), sample, start, 6.1 - start, box, motion, label=f"Foto {i + 1}")
    wide = Box(60, 430, 960, 1100)
    t.solid(t.track("shape", "Marco"), "#FFFFFF", 5.6, 6.4, centered(540, 980, 1000, 1140),
            [(0, {"s": 0.8}, "out"), (0.6, {})], radius=28, kind="rounded-rectangle",
            layers=[shadow("#8a5a2a", 0, 14, 34, 0.3), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Foto grande"), "family-01", 5.6, 6.4, wide,
            [(0, {"s": 0.8}, "out"), (0.6, {}, "linear"), (6.4, {"s": 1.05})], label="Foto de todos")
    words = t.track("text", "Textos")
    t.text(words, "Domingo en familia", 0.2, 11.8, Box(60, 160, 760, 240),
           text_style("Courgette", 100, [fill("#5B8E7D")], weight=400, align="left", line=1.0,
                      anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15)), label="Título")
    t.text(words, "lo más bonito de la semana", 0.9, 11.1, Box(60, 1580, 960, 90),
           text_style("Nunito", 52, [fill("#8A5A2A")], weight=700, anim_in=tanim("fade", duration=0.6)),
           label="Frase")
    t.text(words, "los Quispe Mamani", 6.4, 5.6, Box(60, 1680, 960, 140),
           text_style("Courgette", 90, [fill("#F4A259")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.7, unit="character", stagger=0.04)), label="Familia")
    t.adjust([effect("light_leak", intensity=0.25, hue=0.08, speed=0.5, softness=0.6)], name="Luz")
    t.song("i-guess-what-i-m-trying-to-say", 0.0, 0.8)
    return t


def concierto_festival() -> Template:
    """Festival night: a cut on every beat, neon title that flickers, a VIP wristband, RGB hits and strobes."""
    t = Template("concierto-festival", "Noche de concierto", "Concert night", "reels", 8.0,
                 order=1318, tags=["concierto", "festival", "música", "fiesta", "en vivo"], thumb_at=4.7,
                 background="#000000")
    photos = t.track("video", "Cortes")
    samples = ["concert-01", "concert-03", "friends-10", "concert-02", "concert-04"]
    n = 16
    for i in range(n):
        slot = i % len(samples)
        tilt = 2 if i % 2 else -2
        t.photo(photos, samples[slot], i * beat(1), beat(1), FULL, [(0, {"s": 1.18}, "snap"), (0.16, {"s": 1.04})],
                label=f"Foto {slot + 1}", reuse=None if i < len(samples) else f"p{slot + 1}",
                rotation=keys([(0, tilt)]))
    t.adjust([effect("color.basic", contrast=0.15, vibrance=0.25),
              effect("light_leak", intensity=0.35, hue=0.78, speed=1.5, flicker=0.4),
              effect("rgb_split", animated={"amount": spikes([beat(2 * k) for k in range(8)], 18, 0.2)}),
              effect("strobe_flash", animated={"flash": spikes([beat(4 * k) for k in range(4)], 0.6, 0.15)}, tint=0.3)],
             name="Luces")
    words = t.track("text", "Títulos")
    t.text(words, "noche de festival", 0.2, 7.8, Box(40, 620, 1000, 520),
           text_style("Bungee", 140, [glow("#00F5D4", 30, 0.9), stroke(6, "#7B2FF7"), fill("#FFFFFF")], weight=400,
                      line=0.95, case="upper", anim_in=tanim("glitch-in", duration=0.5),
                      anim_loop=tanim("flicker", intensity=0.4, speed=6)), label="Título")
    band = t.track("shape", "Pulsera")
    pill(t, band, "#7B2FF7", 1.0, 7.0, centered(540, 1560, 640, 130), [(0, {"dx": 1200}, "out"), (0.5, {})],
         rotation=keys([(0, -6)]), layers=[glow("#00F5D4", 24, 0.6), fill("#7B2FF7"), no_stroke()])
    t.text(t.track("text", "Pulsera"), "VIP · 2027", 1.0, 7.0, centered(540, 1560, 640, 130),
           text_style("Bungee", 66, [fill("#00F5D4")], weight=400, spacing=6),
           [(0, {"dx": 1200}, "out"), (0.5, {})], label="Pulsera", rotation=keys([(0, -6)]))
    t.text(words, "Lima · sábado", 1.4, 6.6, Box(40, 1720, 1000, 90),
           text_style("Bungee", 54, [glow("#7B2FF7", 20, 0.9), fill("#FFFFFF")], weight=400, spacing=4,
                      anim_in=tanim("fade", duration=0.4)), label="Lugar")
    t.song("beat-one", 0.0, 0.9)
    return t


def cumple_sorpresa() -> Template:
    """Dark room and a candle («shhh…»), a flash and «¡SORPRESA!», then the party photos with streamers."""
    t = Template("cumple-sorpresa", "Cumpleaños sorpresa", "Surprise party", "celebration", 10.0,
                 order=1319, tags=["sorpresa", "cumpleaños", "fiesta", "amigos", "celebración"], thumb_at=6.2,
                 background="#120E1F")
    t.solid(t.track("shape", "Fondo"), "#120E1F")
    party = t.track("shape", "Fiesta")
    t.solid(party, "#FF3D7F", 2.4, 7.6, FULL, layers=[gradient([(0, "#FF3D7F"), (1, "#7B2FF7")], angle=135),
                                                     no_stroke()])
    t.solid(t.track("shape", "Vela"), "#FFB347", 0.0, 2.4, centered(540, 1150, 360, 360), kind="ellipse",
            layers=[glow("#FFB347", 90, 0.9), fill("#FFB347", 0.5), no_stroke()],
            opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0, "smooth"), (1.2, 0.75, "smooth"), (1.8, 1.0)]))
    t.solid(t.track("shape", "Estallido"), "#FFD23F", 2.4, 2.2, centered(540, 960, 1300, 1300),
            [(0, {"s": 0.0}, "snap"), (0.3, {}, "linear"), (2.2, {"s": 1.1})], kind="burst", points=18,
            innerRatio=0.6, rotation=keys([(0, 0), (2.2, 40)]))
    spots = [("birthday-01", 4.4, -5), ("birthday-07", 6.25, 4), ("friends-02", 8.1, -3)]
    frames = t.track("shape", "Marcos")
    photos = t.track("video", "Fotos")
    for i, (sample, start, tilt) in enumerate(spots):
        dur = 1.9 if i < 2 else 10 - start
        land = [(0, {"s": 0.5, "dy": 300}, "back"), (0.4, {}, "linear"), (dur, {"s": 1.04})]
        rot = keys([(0, tilt * 3, "back"), (0.4, tilt)])
        t.solid(frames, "#FFFFFF", start, dur, centered(540, 900, 860, 1100), land, radius=20,
                kind="rounded-rectangle", layers=[shadow("#3a0a2a", 0, 18, 0, 0.5), fill("#FFFFFF"), no_stroke()],
                rotation=rot)
        t.photo(photos, sample, start, dur, centered(540, 900, 800, 1040), land, label=f"Foto {i + 1}", rotation=rot)
    confetti(t, 77, ["#FFD23F", "#FFFFFF", "#00D1B2", "#FF8FB1"], 2.4, 10.0, lanes=3, kinds=("rectangle",))
    words = t.track("text", "Textos")
    t.text(words, "shhh…", 0.2, 2.2, Box(40, 560, 1000, 260),
           text_style("Lilita One", 170, [fill("#FFE3B3")], weight=400,
                      anim_in=tanim("typewriter", duration=0.8, unit="character")), label="Silencio")
    t.text(words, "ya viene…", 1.1, 1.3, Box(40, 1450, 1000, 120),
           text_style("Lilita One", 76, [fill("#FFE3B3", 0.8)], weight=400, anim_in=tanim("fade", duration=0.4)),
           label="Espera")
    t.text(words, "¡SORPRESA!", 2.4, 2.0, Box(0, 760, 1080, 400),
           text_style("Lilita One", 190, [shadow("#3a0a2a", 0, 12, 0, 0.9), stroke(12, "#FFFFFF"), fill("#FF3D7F")],
                      weight=400, keyframes={"pixelSize": keys([(0, 420, "snap"), (0.22, 190)])},
                      anim_out=tanim("fade-scale", duration=0.3)), label="Grito")
    t.text(words, "¡Feliz cumple, Sofi!", 4.6, 5.4, Box(40, 1520, 1000, 260),
           text_style("Lilita One", 110, [shadow("#3a0a2a", 0, 8, 0, 0.9), stroke(8, "#FFFFFF"), fill("#FF3D7F")],
                      weight=400, line=0.95, anim_in=tanim("pop", duration=0.45, unit="word", stagger=0.12)),
           label="Saludo")
    t.solid(t.track("shape", "Destello"), "#FFFFFF", 2.4, 0.35, FULL, opacity=keys([(0, 1.0, "out"), (0.35, 0.0)]))
    t.adjust([effect("beat_shake", animated={"amount": spikes([2.4], 1.0, 0.6)}, rotation=0.5)], name="Golpe")
    t.song("bar-brawl", 0.0, 0.9)
    return t


TEMPLATES = [boda_save_the_date, resumen_de_boda, anuncio_embarazo, revelacion_de_genero, baby_shower,
             primer_anio_bebe, aniversario_pareja, mejores_amigas, dia_de_playa, mochilero_por_peru, ootd_outfit,
             grwm_arreglate, un_dia_en_mi_vida, mi_mascota, diario_de_comida, progreso_gym, estudia_conmigo,
             domingo_en_familia, concierto_festival, cumple_sorpresa]
TEMPLATES = [_tidied(make) for make in TEMPLATES]
