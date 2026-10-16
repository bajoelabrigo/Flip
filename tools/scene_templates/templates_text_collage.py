"""Text, collage and before/after templates (BRIEF.md #11, #12, #14–#19)."""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, anim, beat, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)


def texto_cinetico() -> Template:
    t = Template("texto-cinetico", "Texto cinético", "Kinetic text", "text", 10.0,
                 order=410, tags=["texto", "motivación", "frase", "impacto"], thumb_at=6.2)
    yellow, black = "#FFDD00", "#111111"
    segments = [("NO ES", 0.0, 1.6, black, yellow), ("SUERTE", 1.6, 1.6, yellow, black),
                ("ES", 3.2, 1.6, black, yellow), ("DISCIPLINA", 4.8, 3.2, None, yellow),
                ("@tuusuario", 8.0, 2.0, black, "#F5F5F5")]
    backs = t.track("shape", "Fondos")
    photo = t.track("video", "Foto")
    t.photo(photo, "man-04", 4.8, 3.2, FULL, [(0, {"s": 1.15}, "snap"), (0.2, {"s": 1.05}, "linear"), (3.2, {"s": 1.0})],
            effects=[effect("duotone", strength=0.9, shadowColor="#111111", highlightColor="#ffdd00", contrast=0.6)])
    for word, start, dur, back, _ in segments:
        if back:
            t.solid(backs, back, start, dur)
    words = t.track("text", "Palabras")
    for word, start, dur, _, colour in segments:
        size = 150 if word.startswith("@") else (210 if len(word) > 7 else 300)
        slam = keys([(0, size * 2.4, "snap"), (0.14, size)])
        t.text(words, word, start, dur, Box(30, 560, 1020, 800),
               text_style("Anton", size, [shadow("#000000", 0, 0, 0, 0.0), fill(colour)], weight=400,
                          line=0.9, keyframes={"pixelSize": slam}),
               label="Usuario" if word.startswith("@") else word.title())
    shake = []
    for _, start, _, _, _ in segments:
        shake += [(start, 0.8, "out"), (start + 0.25, 0.0, "hold")]
    t.adjust([effect("beat_shake", animated={"amount": keys(shake)}, rotation=0.3)], name="Golpe")
    t.song("strength-of-the-titans", 0.0, 0.9)
    return t


def pov_texto() -> Template:
    t = Template("pov-texto", "POV con texto", "POV text", "text", 8.0,
                 order=420, tags=["pov", "meme", "tiktok", "texto"], thumb_at=3.4)
    photo = t.track("video", "Video")
    t.photo(photo, "friends-02", 0, 8.0, FULL, [(0, {"s": 1.0}, "linear"), (8.0, {"s": 1.06})], label="Tu video")
    words = t.track("text", "Texto")
    t.text(words, "POV: por fin llegó el viernes", 0.2, 7.8, Box(110, 300, 860, 300),
           text_style("Montserrat", 68, [fill("#000000")], weight=700, line=1.15, box=("#FFFFFF", 1.0),
                      box_pad=22, box_radius=18,
                      anim_in=tanim("typewriter", duration=1.5, unit="character")), label="Texto")
    t.song("funkeriffic", 0.0, 0.85)
    return t


def tira_pelicula() -> Template:
    t = Template("tira-pelicula", "Tira de película", "Film strip", "collage", 10.0,
                 order=310, tags=["película", "analógico", "rollo", "retro"], thumb_at=2.4, background="#1C1C1C")
    t.solid(t.track("shape", "Fondo"), "#1C1C1C",
            layers=[gradient([(0, "#2A2420"), (1, "#141210")], angle=90), no_stroke()])
    pitch, frame_w, frame_h = 560, 640, 480
    scroll = -3 * pitch
    strip_motion = [(0, {}, "inout"), (6.0, {"dy": scroll}, "linear")]
    fade_out = keys([(0, 1.0), (6.0, 1.0, "smooth"), (6.6, 0.0)])
    strip = t.track("shape", "Tira")
    t.solid(strip, "#2B1D14", 0, 7.0, Box(160, 960 - pitch / 2 - 120, 760, 6 * pitch + 240), strip_motion,
            layers=[shadow("#000000", 0, 0, 40, 0.6), fill("#2B1D14"), no_stroke()], opacity=fade_out)
    holes = t.track("text", "Perforaciones")
    column = "\n".join(["■"] * 46)
    for x in (170, 862):
        t.text(holes, column, 0, 7.0, Box(x, 960 - pitch / 2 - 120, 48, 6 * pitch + 240),
               text_style("Inter", 34, [fill("#F2E8D8", 0.85)], weight=400, line=2.0, valign="top"),
               strip_motion, editable=False, opacity=fade_out)
    samples = ["friends-06", "beach-03", "couple-03", "friends-09", "travel-07", "family-05"]
    for i, sample in enumerate(samples):
        frames = t.track("video", f"Cuadro {i + 1}")
        box = centered(540, 960 + i * pitch, frame_w, frame_h)
        if i == 3:
            # The fourth frame steps out of the strip and fills the screen.
            motion = strip_motion + [(6.0, {"dy": scroll}, "inout"), (8.0, {"dy": scroll, "s": 4.0})]
            clip = t.photo(frames, sample, 0, 10.0, box, motion)
        else:
            clip = t.photo(frames, sample, 0, 7.0, box, strip_motion, opacity=fade_out)
        clip["effects"] = [effect("color.basic", fade=0.12, saturation=-0.1, temperature=0.08)]
    t.adjust([effect("stylize.sepia"), effect("stylize.film_grain", amount=0.35, grainSize=2.0)], name="Película")
    t.tracks[-1].clips[0]["opacity"] = keys([(0, 0.3)])
    words = t.track("text", "Texto")
    t.text(words, "rollo 01", 0.3, 9.7, Box(60, 90, 960, 110),
           text_style("Special Elite", 72, [fill("#F2E8D8")], weight=400, spacing=6,
                      anim_in=tanim("typewriter", duration=0.8, unit="character")), label="Título")
    t.song("piano-magic-motive", 0.0, 0.8)
    return t


def polaroids() -> Template:
    t = Template("polaroids", "Polaroids sobre la mesa", "Polaroids on the table", "collage", 10.0,
                 order=320, tags=["polaroid", "fotos", "recuerdos", "verano"], thumb_at=8.6, background="#EDE3D1")
    t.solid(t.track("shape", "Mesa"), "#EDE3D1",
            layers=[gradient([(0, "#F3EBDD"), (1, "#E2D3BC")], angle=120), no_stroke()])
    spots = [(330, 560, -7), (760, 700, 6), (360, 1160, 5), (740, 1340, -8), (540, 940, 2)]
    samples = ["beach-02", "friends-11", "city-01", "travel-07", "friends-01"]
    captions = ["verano ☀", "con ellas", "Lima", "2026", "♡"]
    final = 0.9
    for i, ((x, y, tilt), sample, caption) in enumerate(zip(spots, samples, captions)):
        start = 0.4 + i * beat(2)
        dur = t.duration - start
        # Pull back at the end: everything shrinks about the centre of the table.
        ox, oy = (x - 540) * (final - 1), (y - 960) * (final - 1)
        drop = [(0, {"s": 1.35, "dy": -260}, "out"), (0.4, {}, "linear"), (8.4 - start, {}, "smooth"),
                (dur, {"s": final, "dx": ox, "dy": oy})]
        rot = keys([(0, tilt * 2.5, "out"), (0.4, tilt)])
        frames = t.track("shape", f"Polaroid {i + 1}")
        t.solid(frames, "#FFFFFF", start, dur, centered(x, y + 40, 470, 570), drop, radius=4,
                layers=[shadow("#3d2b14", 4, 16, 34, 0.35), fill("#FFFEFB"), no_stroke()], rotation=rot)
        photo_motion = [(p[0], {**p[1], "dy": p[1].get("dy", 0) - 40 * (p[1].get("s", 1.0) - 1)}, *p[2:]) for p in drop]
        photos = t.track("video", f"Foto {i + 1}")
        t.photo(photos, sample, start, dur, centered(x, y, 420, 420), photo_motion, rotation=rot)
        notes = t.track("text", f"Nota {i + 1}")
        note_motion = [(p[0], {**p[1], "dy": p[1].get("dy", 0) + 205 * (p[1].get("s", 1.0) - 1)}, *p[2:]) for p in drop]
        t.text(notes, caption, start + 0.3, dur - 0.3, centered(x, y + 245, 420, 90),
               text_style("Caveat", 62, [fill("#2B2B2B")], weight=600,
                          anim_in=tanim("typewriter", duration=0.6, unit="character")),
               [(max(0.0, p[0] - 0.3), *p[1:]) for p in note_motion], label=f"Nota {i + 1}", rotation=rot)
    t.song("hopeful", 0.0, 0.85)
    return t


def album_scrapbook() -> Template:
    t = Template("album-scrapbook", "Álbum scrapbook", "Scrapbook album", "collage", 12.0,
                 order=330, tags=["álbum", "scrapbook", "recuerdos", "pareja"], thumb_at=4.0, background="#F6E7D8")
    t.solid(t.track("shape", "Papel"), "#F6E7D8",
            layers=[gradient([(0, "#F8EDE1"), (1, "#EFDCC8")], angle=60), no_stroke()])
    pages = [
        {"photos": [("couple-01", 330, 640, 520, 640, -4), ("couple-04", 760, 1080, 460, 560, 5),
                    ("couple-06", 340, 1440, 480, 380, -2)],
         "texts": [("nuestro álbum", Box(60, 150, 960, 200), 128, "Título")]},
        {"photos": [("beach-03", 740, 560, 500, 620, 4), ("friends-06", 320, 980, 480, 560, -5),
                    ("couple-07", 720, 1440, 520, 420, 3)],
         "texts": [("el mejor día", Box(40, 1660, 600, 140), 96, "Frase"),
                   ("para siempre", Box(440, 150, 600, 160), 104, "Cierre")]},
    ]
    for p, page in enumerate(pages):
        start, end = (0.0, 6.2) if p == 0 else (5.8, 12.0)
        enter = 1300 if p else 0
        leave = -1300 if p == 0 else 0
        for i, (sample, x, y, w, h, tilt) in enumerate(page["photos"]):
            t0 = start + 0.3 + i * 0.5
            local_leave = end - 0.6 - t0
            motion = [(0, {"dx": enter, "s": 0.85}, "out"), (0.6, {"s": 1.0}, "linear")]
            if leave:
                motion += [(local_leave, {}, "inout"), (local_leave + 0.6, {"dx": leave})]
            rot = keys([(0, tilt)])
            frames = t.track("shape", f"Papel foto {p}-{i}")
            t.solid(frames, "#FFFFFF", t0, end - t0, centered(x, y, w + 36, h + 36), motion,
                    layers=[shadow("#6b4f2a", 3, 10, 22, 0.3), fill("#FFFCF6"), no_stroke()], rotation=rot)
            photos = t.track("video", f"Foto {p}-{i}")
            t.photo(photos, sample, t0, end - t0, centered(x, y, w, h), motion, rotation=rot)
            tape = t.track("shape", f"Cinta {p}-{i}")
            tape_rot = keys([(0, tilt + (-38 if i % 2 else 34))])
            t.solid(tape, "#D4A373", t0 + 0.4, end - t0 - 0.4, centered(x - w / 2 + 30, y - h / 2 + 20, 170, 46),
                    [(m[0] - 0.4 if m[0] else 0, *m[1:]) for m in motion], alpha=0.75, rotation=tape_rot)
        words = t.track("text", f"Textos {p}")
        for content, box, size, label in page["texts"]:
            motion = [(0, {"dx": enter}, "out"), (0.6, {})]
            if leave:
                motion += [(end - start - 1.2, {}, "inout"), (end - start - 0.6, {"dx": leave})]
            t.text(words, content, start + 0.6, end - start - 0.6, box,
                   text_style("Dancing Script", size, [fill("#6B705C")], weight=700,
                              anim_in=tanim("typewriter", duration=0.9, unit="character")),
                   motion, label=label)
    t.song("landra-s-dream", 0.0, 0.8)
    return t


def before_after(t: Template, before: str, after: str, start: float, dur: float, sweep_at: float,
                 sweep: float, back: float | None = None, line_color: str = "#FFFFFF") -> None:
    """A divider that sweeps across, uncovering `after` over `before` (left to right)."""
    under = t.track("video", "Antes")
    t.photo(under, before, start, dur, FULL, [(0, {"s": 1.0}, "linear"), (dur, {"s": 1.05})], label="Antes")
    over = t.track("video", "Después")
    top = t.photo(over, after, start, dur, FULL, [(0, {"s": 1.0}, "linear"), (dur, {"s": 1.05})], label="Después")
    a, b = sweep_at - start, sweep_at - start + sweep
    pts = [(0, 0.0, "linear"), (a, 0.0, "inout"), (b, 1.0, "linear")]
    if back is not None:
        pts += [(back - start, 1.0, "inout"), (back - start + 0.8, 0.5, "linear")]
    w = keys(pts)
    x = keys([(p[0], p[1] / 2, *p[2:]) for p in pts])
    t.mask(over, top, "rectangle", w=0.0, x=0.0, keyframes={"w": w, "x": x})
    line = t.track("shape", "Divisor")
    lx = keys([(p[0], p[1] * 1080 - 4, *p[2:]) for p in pts])
    t.solid(line, line_color, start, dur, Box(0, 0, 8, 1920),
            layers=[glow(line_color, 26, 0.9), fill(line_color), no_stroke()], x=lx)


def antes_despues_deslizador() -> Template:
    t = Template("antes-despues-deslizador", "Antes y después", "Before and after", "beforeafter", 6.0,
                 order=500, tags=["antes", "después", "comparar", "cambio"], thumb_at=2.5)
    before_after(t, "kitchen-old-01", "interior-02", 0.0, 6.0, 1.5, 2.0, back=5.0, line_color="#FFFFFF")
    labels = t.track("text", "Etiquetas")
    pill = lambda: text_style("Montserrat", 44, [fill("#FFFFFF")], weight=800, spacing=3,  # noqa: E731
                              box=("#111111", 0.75), box_pad=16, box_radius=30,
                              anim_in=tanim("pop", duration=0.4))
    t.text(labels, "ANTES", 0.2, 5.8, Box(50, 120, 300, 90), pill(), label="Antes")
    t.text(labels, "DESPUÉS", 1.6, 4.4, Box(690, 120, 340, 90),
           {**pill(), "boxColor": "#ff00c2a8"}, label="Después")
    t.song("hopeful", 0.0, 0.8)
    return t


def transformacion_gym() -> Template:
    t = Template("transformacion-gym", "Transformación gym", "Gym transformation", "beforeafter", 8.0,
                 order=510, tags=["gym", "fitness", "transformación", "antes y después"], thumb_at=4.3)
    photos = t.track("video", "Fotos")
    t.photo(photos, "gym-01", 0, 3.0, FULL, [(0, {"s": 1.0}, "linear"), (3.0, {"s": 1.1})], label="Antes",
            effects=[effect("color.basic", saturation=-1.0, contrast=0.1, exposure=-0.1)])
    after = ["gym-04", "gym-06"]
    for i in range(10):
        # Two "after" slots, cut on the beat in turn: the repeats show the same pictures.
        t.photo(photos, after[i % 2], 3.0 + i * 0.5, 0.5, FULL, [(0, {"s": 1.14}, "snap"), (0.2, {"s": 1.02})],
                label=f"Después {i % 2 + 1}", reuse=None if i < 2 else f"p{i % 2 + 2}",
                effects=[effect("color.basic", saturation=0.25, contrast=0.2)])
    flash = t.track("shape", "Destello")
    t.solid(flash, "#FFFFFF", 3.0, 0.3, FULL, opacity=keys([(0, 0.9, "out"), (0.3, 0.0)]))
    words = t.track("text", "Días")
    style = lambda colour: text_style("Anton", 190, [shadow("#000000", 0, 8, 24, 0.6), fill(colour)],  # noqa: E731
                                      weight=400, case="upper")
    t.text(words, "Día 1", 0.2, 2.8, Box(40, 1380, 1000, 260),
           {**style("#FFFFFF"), "animation": {"in": tanim("slide-up", duration=0.4)}}, label="Antes")
    for k, day in enumerate(["Día 15", "Día 30", "Día 45", "Día 60", "Día 75"]):
        t.text(words, day, 3.0 + k * 0.12, 0.12, Box(40, 1380, 1000, 260), style("#FF3B30"), editable=False)
    t.text(words, "Día 90", 3.6, 4.4, Box(40, 1380, 1000, 260),
           {**style("#FF3B30"), "animation": {"in": tanim("stamp", duration=0.3)}}, label="Después")
    t.text(words, "@tuusuario", 5.0, 3.0, Box(40, 1660, 1000, 100),
           text_style("Inter", 48, [fill("#FFFFFF")], weight=700, anim_in=tanim("fade", duration=0.4)),
           label="Usuario")
    shake = [(3.0, 1.0, "out"), (3.5, 0.0)]
    t.adjust([effect("beat_shake", animated={"amount": keys(shake)}, rotation=0.4),
              effect("stylize.vignette", amount=0.6)], name="Golpe")
    t.song("behind-enemy-lines", 0.0, 0.9)
    return t


def remodelacion() -> Template:
    t = Template("remodelacion", "Antes y después del espacio", "Room makeover", "beforeafter", 10.0,
                 order=520, tags=["remodelación", "casa", "inmobiliaria", "decoración"], thumb_at=2.0)
    before_after(t, "kitchen-old-02", "interior-05", 0.0, 5.2, 1.2, 1.6, line_color="#F5F1EA")
    before_after(t, "interior-07", "interior-04", 5.0, 5.0, 6.4, 1.6, line_color="#F5F1EA")
    # The second pair fades in over the first.
    for track in t.tracks[-3:]:
        for clip in track.clips:
            clip["animIn"] = anim("fade", 0.4)
    labels = t.track("text", "Etiquetas")
    tag = lambda: text_style("Playfair Display", 54, [fill("#F5F1EA")], weight=700, italic=True,  # noqa: E731
                             box=("#3D405B", 0.85), box_pad=16, box_radius=6, anim_in=tanim("fade", duration=0.4))
    t.text(labels, "Antes", 0.2, 9.8, Box(50, 110, 260, 90), tag(), label="Antes")
    t.text(labels, "Después", 1.4, 8.6, Box(770, 110, 260, 90), {**tag(), "boxColor": "#ffe07a5f"}, label="Después")
    bar = t.track("shape", "Barra")
    t.solid(bar, "#3D405B", 0.6, 9.4, Box(0, 1650, 1080, 150), [(0, {"dx": -1080}, "out"), (0.6, {})], alpha=0.92)
    credit = t.track("text", "Crédito")
    t.text(credit, "Remodelación por @tuempresa", 1.0, 9.0, Box(60, 1650, 960, 150),
           text_style("Montserrat", 46, [fill("#F5F1EA")], weight=600, anim_in=tanim("fade", duration=0.5)),
           label="Crédito")
    t.song("energizing", 0.0, 0.8)
    return t


TEMPLATES = [texto_cinetico, pov_texto, tira_pelicula, polaroids, album_scrapbook, antes_despues_deslizador,
             transformacion_gym, remodelacion]
