"""The scene templates. Each function builds one; see BRIEF.md for the design of each and scene.py for
the building blocks. Times in seconds, boxes in 1080x1920 project pixels; tracks are added bottom-up.
"""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, anim, beat, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)


def photo_dump_ritmo() -> Template:
    """A pile of prints on cream: a new one lands on every second beat, the older ones stay under it."""
    t = Template("photo-dump-ritmo", "Photo dump al ritmo", "Photo dump on the beat", "reels", 12.0,
                 order=10, tags=["fotos", "ritmo", "dump", "amigos"], thumb_at=9.3, background="#F5F0E8")
    rng = random.Random(7)
    t.solid(t.track("shape", "Fondo"), "#F5F0E8")
    samples = ["friends-03", "y4c-friends-05", "beach-01", "travel-05", "friends-08", "cafe-02",
               "travel-10", "friends-01", "friends-11", "friends-12"]
    starts = [0.0] + [1.0 + i * beat(2) for i in range(9)]
    # The print and its white border share a centre, so they turn and punch together.
    print_box = centered(540, 900, 800, 1000)
    frame_box = centered(540, 900, 860, 1060)
    for i, (start, sample) in enumerate(zip(starts, samples)):
        angle = (rng.uniform(5, 11) * (1 if i % 2 else -1)) if i < len(samples) - 1 else 0.0
        shift = (rng.uniform(-70, 70), rng.uniform(-50, 50)) if i < len(samples) - 1 else (0, 0)
        hold = t.duration - start
        land = [(0, {"s": 1.12, "dx": shift[0], "dy": shift[1]}, "snap"),
                (0.22, {"s": 1.0, "dx": shift[0], "dy": shift[1]})]
        if i == len(samples) - 1:
            land = [(0, {"s": 1.12}, "snap"), (0.22, {"s": 1.0}, "smooth"), (hold, {"s": 1.08})]
        rotation = keys([(0, angle * 1.8, "out"), (0.22, angle)])
        frames = t.track("shape", f"Marco {i + 1}")
        t.solid(frames, "#FFFFFF", start, hold, frame_box, land, radius=6,
                layers=[shadow("#000000", 0, 10, 30, 0.28), {"id": "fill", "kind": "fill", "enabled": True,
                        "paint": {"kind": "solid", "color": "#fffdfaf3"}, "opacity": 1.0}, no_stroke()],
                rotation=rotation)
        photos = t.track("video", f"Foto {i + 1}")
        t.photo(photos, sample, start, hold, print_box, land, rotation=rotation)
    # A white flash on every fourth beat.
    flashes = t.track("shape", "Destellos")
    for k in range(1, 6):
        t.solid(flashes, "#FFFFFF", 1.0 + k * beat(4) - 0.02, 0.18, FULL,
                opacity=keys([(0, 0.55, "out"), (0.18, 0.0)]))
    titles = t.track("text", "Título")
    t.text(titles, "mis días ✦", 0.15, t.duration - 0.15, Box(90, 1580, 900, 200),
           text_style("Caveat", 132, [fill("#1A1A1A")], weight=700,
                      anim_in=tanim("typewriter", duration=0.9, unit="character")),
           label="Título")
    t.adjust([effect("stylize.film_grain", amount=0.18, grainSize=1.6)], name="Grano")
    t.song("city-sunshine", 6.0, 0.85)
    return t


def feliz_cumple() -> Template:
    """Confetti colours, a big script title, then the photos bounce in turn in white rounded frames."""
    t = Template("feliz-cumple", "Feliz cumpleaños", "Happy birthday", "celebration", 12.0,
                 order=200, tags=["cumpleaños", "fiesta", "familia"], thumb_at=5.0)
    bg = t.track("shape", "Fondo")
    t.solid(bg, "#FF6FB5", layers=[gradient([(0, "#FF6FB5"), (0.55, "#FF9A8B"), (1, "#FFD23F")], angle=120),
                                   no_stroke()])
    # Confetti: dots and stars that drift down, spread over four tracks.
    rng = random.Random(3)
    colours = ["#FFFFFF", "#3BCEAC", "#FFD23F", "#7B2FF7", "#FFFFFF"]
    for lane in range(4):
        confetti = t.track("shape", f"Confeti {lane + 1}")
        start = lane * 0.4
        while start < t.duration - 0.5:
            size = rng.uniform(26, 54)
            x = rng.uniform(40, 1000)
            dur = rng.uniform(2.6, 4.2)
            kind = rng.choice(["ellipse", "star", "rectangle"])
            t.solid(confetti, rng.choice(colours), start, min(dur, t.duration - start), centered(x, -60, size, size),
                    [(0, {}, "linear"), (dur, {"dy": 2100, "dx": rng.uniform(-120, 120)})], kind=kind,
                    radius=4, rotation=keys([(0, 0), (dur, rng.uniform(-360, 360))]))
            start += rng.uniform(0.25, 0.6)
    frames = t.track("shape", "Marcos")
    photos = t.track("video", "Fotos")
    samples = ["birthday-01", "family-02", "birthday-02", "friends-09", "family-04", "birthday-07"]
    slot_len = 8.0 / len(samples)
    for i, sample in enumerate(samples):
        start = 2.0 + i * slot_len
        tilt = (-4 if i % 2 else 4)
        land = [(0, {"s": 0.6, "dy": 260}, "back"), (0.45, {}, "linear"), (slot_len, {"s": 1.03})]
        rot = keys([(0, tilt * 3, "back"), (0.45, tilt)])
        t.solid(frames, "#FFFFFF", start, slot_len, centered(540, 1000, 820, 1060), land, radius=48,
                kind="rounded-rectangle", layers=[shadow("#7a1f4f", 0, 18, 40, 0.35), fill("#FFFFFF"), no_stroke()],
                rotation=rot)
        t.photo(photos, sample, start, slot_len, centered(540, 1000, 760, 1000), land, rotation=rot)
    titles = t.track("text", "Títulos")
    big = text_style("Pacifico", 150, [shadow("#8a1d55", 0, 10, 0, 0.9), stroke(10, "#FFFFFF"), fill("#E8277A")],
                     weight=400, line=1.0, anim_in=tanim("pop", duration=0.6, unit="word", stagger=0.12, ease="back"),
                     anim_out=tanim("fade-scale", duration=0.3))
    t.text(titles, "¡Feliz cumpleaños!", 0.2, 1.8, Box(60, 640, 960, 640), big, label="Título")
    small = text_style("Pacifico", 96, [shadow("#8a1d55", 0, 6, 0, 0.9), stroke(8, "#FFFFFF"), fill("#E8277A")],
                       weight=400, anim_in=tanim("drop", duration=0.5))
    t.text(titles, "¡Feliz cumpleaños!", 2.0, 8.0, Box(40, 150, 1000, 260), small, editable=False)
    name = text_style("Pacifico", 190, [glow("#FFFFFF", 40, 0.9), stroke(10, "#FFFFFF"), fill("#E8277A")],
                      weight=400, anim_in=tanim("stamp", duration=0.5), anim_loop=tanim("pulse", amount=4, speed=1.2))
    t.text(titles, "Ana", 10.0, 2.0, Box(40, 700, 1000, 420), name, label="Nombre")
    sub = text_style("Poppins", 64, [shadow("#8a1d55", 0, 4, 10, 0.5), fill("#FFFFFF")], weight=700,
                     anim_in=tanim("rise", duration=0.5, delay=0.3))
    t.text(titles, "Te queremos ♥", 10.0, 2.0, Box(40, 1120, 1000, 140), sub, label="Mensaje")
    t.adjust([effect("bling_sparkle", intensity=0.5, density=0.35, threshold=0.8)], 10.0, 2.0, name="Brillos")
    t.song("funshine", 0.0, 0.85)
    return t


def collage_2x2() -> Template:
    """Four cells pop in one per beat, the grid breathes in, the title lands, then it all flies apart."""
    t = Template("collage-2x2", "Collage 2×2", "2×2 collage", "collage", 8.0,
                 order=300, tags=["collage", "cuadrícula", "fin de semana"], thumb_at=3.6, background="#F2E9E4")
    t.solid(t.track("shape", "Fondo"), "#F2E9E4")
    cell_w, cell_h, gap = 486, 760, 28
    x0 = (1080 - 2 * cell_w - gap) / 2
    y0 = (1920 - 2 * cell_h - gap) / 2
    samples = ["friends-01", "beach-01", "friends-10", "cafe-01"]
    exits = [(-1300, -200), (1300, -200), (-1300, 200), (1300, 200)]
    for i, sample in enumerate(samples):
        col, row = i % 2, i // 2
        box = Box(x0 + col * (cell_w + gap), y0 + row * (cell_h + gap), cell_w, cell_h)
        start = i * beat(1)
        # Scale about the canvas centre for the "breathe": move the cell out with it.
        grow = 1.08
        ox, oy = (box.cx - 540) * (grow - 1), (box.cy - 960) * (grow - 1)
        local = lambda s: s - start  # noqa: E731
        motion = [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"), (local(4.0), {}, "smooth"),
                  (local(5.6), {"s": grow, "dx": ox, "dy": oy}, "in"),
                  (local(6.6), {"s": grow, "dx": ox + exits[i][0], "dy": oy + exits[i][1]})]
        cells = t.track("video", f"Celda {i + 1}")
        t.photo(cells, sample, start, t.duration - start, box, motion)
    pills = t.track("shape", "Píldora")
    pill = [(0, {"s": 0.0}, "back"), (0.45, {}, "linear"), (2.6, {}, "in"), (3.2, {"s": 0.0})]
    t.solid(pills, "#FFFFFF", 2.4, 3.4, centered(540, 960, 560, 130), pill, radius=65, kind="rounded-rectangle",
            layers=[shadow("#22223B", 0, 10, 30, 0.3), fill("#FFFFFF"), no_stroke()])
    titles = t.track("text", "Título")
    t.text(titles, "nuestro finde", 2.5, 3.1, centered(540, 960, 560, 130),
           text_style("Poppins", 58, [fill("#22223B")], weight=600,
                      anim_in=tanim("pop", duration=0.4, unit="character", stagger=0.03),
                      anim_out=tanim("shrink", duration=0.3)),
           label="Título")
    t.song("fresh-focus", 0.0, 0.85)
    return t


def frase_del_dia() -> Template:
    """A blurred, slowly panning photo behind a serif quote that arrives a word per beat."""
    t = Template("frase-del-dia", "Frase del día", "Quote of the day", "text", 8.0,
                 order=400, tags=["frase", "motivación", "cita"], thumb_at=6.8)
    bg = t.track("video", "Fondo")
    t.photo(bg, "beach-01", 0, 8.0, centered(540, 960, 1300, 2310),
            [(0, {"dx": 90}, "linear"), (8.0, {"dx": -90})],
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=10),
                     effect("color.basic", exposure=-0.05, saturation=-0.1)])
    t.solid(t.track("shape", "Velo"), "#1d140c", alpha=0.32)
    marks = t.track("text", "Comillas")
    t.text(marks, "“", 0.0, 8.0, Box(90, 430, 300, 300),
           text_style("DM Serif Display", 300, [fill("#B08D57")], weight=400, align="left",
                      anim_in=tanim("fade", duration=0.8)), editable=False)
    quote = t.track("text", "Frase")
    t.text(quote, "Lo que haces hoy decide tu mañana.", 0.4, 7.6, Box(110, 640, 860, 640),
           text_style("DM Serif Display", 108, [shadow("#000000", 0, 4, 16, 0.45), fill("#F4EFE6")],
                      weight=400, align="left", line=0.92,
                      anim_in=tanim("rise-by-word", duration=0.45, unit="word", stagger=beat(1), rise=0.4, blur=8)),
           label="Frase")
    rule = t.track("shape", "Línea")
    t.solid(rule, "#B08D57", 3.6, 4.4, Box(114, 1330, 180, 6),
            [(0, {"sx": 0.0, "dx": -90}, "out"), (0.6, {})])
    handle = t.track("text", "Usuario")
    t.text(handle, "@tuusuario", 4.0, 4.0, Box(110, 1370, 860, 90),
           text_style("Inter", 46, [fill("#F4EFE6", 0.85)], weight=500, align="left", spacing=2,
                      anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.03)),
           label="Usuario")
    t.song("infinite-peace", 0.0, 0.8)
    return t


import templates_reels  # noqa: E402
import templates_text_collage  # noqa: E402
import templates_rest  # noqa: E402
import templates_t1  # noqa: E402
import templates_t2  # noqa: E402
import templates_t3  # noqa: E402
import templates_t4  # noqa: E402
import templates_t5  # noqa: E402
import templates_h1  # noqa: E402
import templates_h2  # noqa: E402
import templates_h3  # noqa: E402
import templates_h4  # noqa: E402
import templates_r6  # noqa: E402
import templates_r7  # noqa: E402
import templates_r8  # noqa: E402
import templates_r9  # noqa: E402
import templates_s1  # noqa: E402
import templates_s2  # noqa: E402
import templates_s3  # noqa: E402
import templates_s4  # noqa: E402
import templates_f1  # noqa: E402
import templates_f2  # noqa: E402
import templates_y1  # noqa: E402
import templates_c1  # noqa: E402
import templates_c2  # noqa: E402
import templates_y2  # noqa: E402
import templates_y3  # noqa: E402
import templates_y4  # noqa: E402
import templates_y5  # noqa: E402
import templates_y6  # noqa: E402
import templates_y7  # noqa: E402
import templates_ytkit  # noqa: E402
import templates_ytkit_a  # noqa: E402
import templates_ytkit_b  # noqa: E402
import templates_ytkit_c  # noqa: E402
import templates_ytkit_d  # noqa: E402
import templates_ytkit_e  # noqa: E402
import templates_ytkit_f  # noqa: E402
import templates_ytkit_g  # noqa: E402
import templates_ytkit_h  # noqa: E402
import templates_ytkit_i  # noqa: E402
import templates_ytkit_j  # noqa: E402
import templates_ytkit_k  # noqa: E402
import templates_ytkit_l  # noqa: E402
import templates_ytkit_m  # noqa: E402
import templates_ytkit_n  # noqa: E402
import templates_ytkit_o  # noqa: E402
import templates_ytkit_p  # noqa: E402
import templates_lt_a  # noqa: E402
import templates_lt_b  # noqa: E402
import templates_llt_a  # noqa: E402
import templates_llt_b  # noqa: E402
import templates_llt_c  # noqa: E402
import templates_igkit  # noqa: E402

TEMPLATES = ([photo_dump_ritmo, feliz_cumple, collage_2x2, frase_del_dia] + templates_reels.TEMPLATES
             + templates_text_collage.TEMPLATES + templates_rest.TEMPLATES
             + templates_t1.TEMPLATES + templates_t2.TEMPLATES + templates_t3.TEMPLATES
             + templates_t4.TEMPLATES + templates_t5.TEMPLATES
             + templates_h1.TEMPLATES + templates_h2.TEMPLATES + templates_h3.TEMPLATES
             + templates_h4.TEMPLATES
             + templates_r6.TEMPLATES + templates_r7.TEMPLATES
             + templates_r8.TEMPLATES + templates_r9.TEMPLATES
             + templates_s1.TEMPLATES + templates_s2.TEMPLATES
             + templates_s3.TEMPLATES + templates_s4.TEMPLATES
             + templates_f1.TEMPLATES + templates_f2.TEMPLATES + templates_y1.TEMPLATES
             + templates_c1.TEMPLATES + templates_c2.TEMPLATES
             + templates_y2.TEMPLATES + templates_y3.TEMPLATES + templates_y4.TEMPLATES + templates_y5.TEMPLATES + templates_y6.TEMPLATES + templates_y7.TEMPLATES
             + templates_ytkit.TEMPLATES
             + templates_ytkit_a.TEMPLATES + templates_ytkit_b.TEMPLATES + templates_ytkit_c.TEMPLATES + templates_ytkit_d.TEMPLATES + templates_ytkit_e.TEMPLATES + templates_ytkit_f.TEMPLATES + templates_ytkit_g.TEMPLATES + templates_ytkit_h.TEMPLATES + templates_ytkit_i.TEMPLATES + templates_ytkit_j.TEMPLATES + templates_ytkit_k.TEMPLATES + templates_ytkit_l.TEMPLATES + templates_ytkit_m.TEMPLATES + templates_ytkit_n.TEMPLATES + templates_ytkit_o.TEMPLATES + templates_ytkit_p.TEMPLATES + templates_lt_a.TEMPLATES + templates_lt_b.TEMPLATES + templates_llt_a.TEMPLATES + templates_llt_b.TEMPLATES + templates_llt_c.TEMPLATES + templates_igkit.TEMPLATES)
