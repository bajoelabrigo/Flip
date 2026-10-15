"""Trend batch 5 (2026-10-15): see BRIEF.md, section «Las 100 de tendencia».

Texto, intros y cierres: the hooks and formats creators reuse every day. Categories text, intro, outro,
countdown; order 1400-1499.
"""

from __future__ import annotations

import random

from scene import (FULL, Box, Template, anim, centered, effect, fill, glow, gradient, keys,
                   no_stroke, shadow, stroke, tanim, text_style)


def _pill(t: Template, track, colour: str, t0: float, dur: float, box: Box, motion=None, **extra):
    return t.solid(track, colour, t0, dur, box, motion, radius=box.h / 2, kind="rounded-rectangle", **extra)


def _pop(at: float = 0.0, length: float = 0.45) -> list:
    return [(at, {"s": 0.0}, "back"), (at + length, {})]


def _hollow() -> dict:
    return {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def _kb(dur: float, s0: float = 1.0, s1: float = 1.08, **end) -> list:
    """Slow Ken Burns push."""
    return [(0, {"s": s0}, "linear"), (dur, {"s": s1, **end})]


def _spike(times: list[float], peak: float, fall: float) -> dict:
    """Peaks that drop to 0 and hold there (BRIEF trap: the decay key must be "hold")."""
    pts = []
    # Off until the first peak: before its first key a channel holds that key's value.
    if times and times[0] > 0:
        pts.append((0.0, 0.0, "hold"))
    for at in times:
        pts += [(at, peak, "out"), (at + fall, 0.0, "hold")]
    return keys(pts)


def _blink(dur: float, period: float, low: float = 0.15) -> dict:
    pts, at = [], 0.0
    while at < dur:
        pts += [(at, 1.0, "hold"), (at + period / 2, low, "hold")]
        at += period
    return keys(pts)


# 1 -----------------------------------------------------------------------------------------------


def gancho_espera_al_final() -> Template:
    """A hook over the video, arrows that blink downwards, a bar that fills, then the payoff slams in."""
    t = Template("gancho-espera-al-final", "Espera al final", "Wait for the end", "text", 7.0,
                 order=1400, tags=["gancho", "espera al final", "suspenso", "tiktok", "viral"], thumb_at=1.6)
    video = t.track("video", "Video")
    t.photo(video, "friends-12", 0, 7.0, FULL, _kb(7.0, 1.0, 1.12), label="Tu video")
    shade = t.track("shape", "Sombra")
    t.solid(shade, "#000000", 0, 7.0, Box(0, 0, 1080, 760),
            layers=[gradient([(0, "#000000", 0.75), (1, "#000000", 0.0)], angle=90), no_stroke()])
    arrows = t.track("text", "Flechas")
    for k in range(3):
        t.text(arrows if k == 0 else t.track("text", "Flechas"), "↓", 0.6 + k * 0.15, 4.9 - k * 0.15,
               centered(540, 1440 + k * 95, 200, 120),
               text_style("Inter", 110, [shadow("#000000", 0, 4, 10, 0.5), fill("#FFE600")], weight=900),
               editable=False, opacity=_blink(4.9 - k * 0.15, 0.6, 0.2))
    track = t.track("shape", "Barra")
    t.solid(track, "#FFFFFF", 0.3, 5.2, Box(80, 1790, 920, 18), radius=9, kind="rounded-rectangle", alpha=0.3)
    bar = t.track("shape", "Progreso")
    t.solid(bar, "#FFE600", 0.3, 5.2, Box(80, 1790, 920, 18), [(0, {"sx": 0.0, "dx": -460}, "linear"), (5.2, {})],
            radius=9, kind="rounded-rectangle")
    words = t.track("text", "Gancho")
    t.text(words, "Espera al final…", 0.1, 5.4, Box(50, 170, 980, 380),
           text_style("Bangers", 170, [shadow("#000000", 0, 10, 0, 0.9), stroke(10, "#111111"), fill("#FFE600")],
                      weight=400, spacing=2, line=0.95,
                      anim_in=tanim("pop", duration=0.45, unit="word", stagger=0.15, ease="back"),
                      anim_loop=tanim("pulse", amount=4, speed=1.4)), label="Gancho")
    flash = t.track("shape", "Destello")
    t.solid(flash, "#FFFFFF", 5.5, 0.35, FULL, opacity=keys([(0, 0.95, "out"), (0.35, 0.0)]))
    pay = t.track("text", "Remate")
    t.text(pay, "¡TE LO DIJE!", 5.5, 1.5, Box(40, 700, 1000, 520),
           text_style("Bangers", 230, [shadow("#000000", 0, 14, 0, 0.9), stroke(12, "#111111"), fill("#FFFFFF")],
                      weight=400, line=0.9, anim_in=tanim("stamp", duration=0.3)), label="Remate",
           rotation=keys([(0, -5)]))
    t.adjust([effect("beat_shake", animated={"amount": _spike([5.5], 0.9, 0.4)}, rotation=0.4)], name="Golpe")
    t.song("beat-one", 0.0, 0.85)
    return t


# 2 -----------------------------------------------------------------------------------------------


def pov_chat() -> Template:
    """POV told as a chat: bubbles pop in one by one, the other side types, then leaves you on read."""
    t = Template("pov-chat-mensajes", "POV en mensajes", "POV chat", "text", 9.0,
                 order=1404, tags=["pov", "chat", "mensajes", "humor", "ex"], thumb_at=6.6)
    video = t.track("video", "Video")
    t.photo(video, "selfie-04", 0, 9.0, FULL, _kb(9.0, 1.05, 1.12), label="Tu video",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=8),
                     effect("color.basic", exposure=-0.35, saturation=-0.15)])
    words = t.track("text", "POV")
    t.text(words, "POV: le escribes a tu ex a las 3 a. m.", 0.2, 8.8, Box(70, 170, 940, 300),
           text_style("DM Sans", 74, [shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")], weight=700, line=1.1,
                      align="left", anim_in=tanim("typewriter", duration=1.2, unit="character")), label="POV")
    messages = [("hola", True, 1.6), ("¿estás despierta?", True, 2.6), ("¿quién es?", False, 4.6),
                ("nada, número equivocado", True, 6.0)]
    y = 640
    for i, (content, mine, at) in enumerate(messages):
        # Every bubble stays to the end, so each one has its own pair of tracks.
        w = min(800, 90 + 27 * len(content))
        box = Box(1010 - w, y, w, 110) if mine else Box(70, y, w, 110)
        dur = t.duration - at
        land = [(0, {"s": 0.6, "dy": 30}, "back"), (0.35, {})]
        colour = "#0A84FF" if mine else "#E9E9EB"
        t.solid(t.track("shape", f"Burbuja {i + 1}"), colour, at, dur, box, land, radius=48, kind="rounded-rectangle",
                layers=[shadow("#000000", 0, 6, 18, 0.25), fill(colour), no_stroke()])
        t.text(t.track("text", f"Mensaje {i + 1}"), content, at + 0.05, dur - 0.05, box,
               text_style("DM Sans", 48, [fill("#FFFFFF" if mine else "#111111")], weight=500,
                          anim_in=tanim("fade", duration=0.2)), [(0, {"s": 0.6, "dy": 30}, "back"), (0.3, {})],
               label=f"Mensaje {i + 1}")
        y += 140
        if i == 1:
            # The other side is typing: three dots that blink in a grey bubble, before the reply lands there.
            typing = t.track("shape", "Escribiendo")
            t.solid(typing, "#E9E9EB", 3.5, 1.05, Box(70, y, 170, 110), _pop(0, 0.3), radius=48,
                    kind="rounded-rectangle")
            for d in range(3):
                dots = t.track("shape", "Punto")
                t.solid(dots, "#8E8E93", 3.5, 1.05, centered(115 + d * 40, y + 55, 22, 22), kind="ellipse",
                        opacity=keys([(0, 0.0, "hold"), (0.3 + d * 0.1, 1.0, "hold"), (0.6 + d * 0.1, 0.3, "hold"),
                                      (0.9 + d * 0.1, 1.0)]))
    seen = t.track("text", "Visto")
    t.text(seen, "Visto 3:07", 7.0, 2.0, Box(470, y + 5, 540, 60),
           text_style("DM Sans", 34, [fill("#FFFFFF", 0.8)], weight=500, align="right",
                      anim_in=tanim("fade", duration=0.4)), label="Visto")
    t.song("llama-in-pajama", 0.0, 0.8)
    return t


# 3 -----------------------------------------------------------------------------------------------


def pov_cine() -> Template:
    """POV as a film still: bars, a warm grade, a serif «POV» and two lines of yellow movie subtitles."""
    t = Template("pov-cinematografico", "POV de película", "Cinematic POV", "text", 8.0,
                 order=1408, tags=["pov", "cine", "protagonista", "aesthetic", "subtítulos"], thumb_at=3.2)
    video = t.track("video", "Video")
    t.photo(video, "portrait-04", 0, 8.0, FULL, [(0, {"s": 1.16, "dx": 30}, "linear"), (8.0, {"s": 1.02})],
            label="Tu video")
    t.adjust([effect("cinematic_grade", strength=0.7, teal=0.55, orange=0.7, contrast=0.4),
              effect("light_leak", animated={"intensity": keys([(0, 0.0, "smooth"), (1.2, 0.45, "smooth"),
                                                                (3.0, 0.0)])}, hue=0.08, speed=0.6),
              effect("stylize.film_grain", amount=0.25, grainSize=1.8), effect("stylize.vignette", amount=0.6)],
             name="Color de cine")
    for y, dy in ((0, -230), (1920 - 230, 230)):
        bars = t.track("shape", "Barras")
        t.solid(bars, "#000000", 0, 8.0, Box(0, y, 1080, 230), [(0, {"dy": dy}, "out"), (0.9, {})])
    words = t.track("text", "POV")
    t.text(words, "POV:", 0.6, 7.4, Box(60, 70, 600, 110),
           text_style("Cormorant Garamond", 84, [fill("#F2D16B")], weight=600, italic=True, align="left",
                      spacing=4, anim_in=tanim("blur-in", duration=1.0, blur=18)), label="POV")
    sub = lambda: text_style("Inter", 54, [shadow("#000000", 0, 3, 8, 0.9), fill("#FFE27A")],  # noqa: E731
                             weight=500, line=1.2, anim_in=tanim("fade-up-char", duration=0.5, unit="character",
                                                                 stagger=0.025),
                             anim_out=tanim("fade", duration=0.3))
    lines = t.track("text", "Subtítulos")
    t.text(lines, "eres la protagonista y todavía no lo sabes", 1.0, 3.4, Box(90, 1450, 900, 200), sub(),
           label="Subtítulo 1")
    t.text(lines, "y hoy empieza tu historia", 4.6, 3.4, Box(90, 1450, 900, 200), sub(), label="Subtítulo 2")
    t.song("infinite-wonder", 0.0, 0.85)
    return t


# 4 -----------------------------------------------------------------------------------------------


def storytime() -> Template:
    """A sticker cover (your face, «storytime», the hook), then the scene with the story in three parts."""
    t = Template("storytime-les-cuento", "Storytime: les cuento", "Storytime", "text", 12.0,
                 order=1412, tags=["storytime", "historia", "anécdota", "les cuento", "tiktok"], thumb_at=4.0,
                 background="#FFF3E0")
    t.solid(t.track("shape", "Fondo"), "#FFF3E0",
            layers=[gradient([(0, "#FFF6E8"), (1, "#FFD9C7")], angle=90), no_stroke()])
    ring = t.track("shape", "Aro")
    t.solid(ring, "#FF7A59", 0.1, 2.5, centered(540, 760, 600, 600), _pop(0, 0.5), kind="ellipse",
            layers=[shadow("#B5432A", 0, 14, 30, 0.35), fill("#FF7A59"), no_stroke()])
    faces = t.track("video", "Tu cara")
    face = t.photo(faces, "creator-03", 0.1, 2.5, centered(540, 760, 560, 560), _pop(0, 0.5), label="Tu cara")
    t.mask(faces, face, "ellipse")
    scene = t.track("video", "Escena")
    t.photo(scene, "friends-10", 2.4, 9.6, FULL, [(0, {"dy": 1920}, "out"), (0.5, {}, "linear"), (9.6, {"s": 1.1})],
            label="Escena")
    sticker = t.track("shape", "Sticker")
    tilt = keys([(0, -4)])
    t.solid(sticker, "#FF7A59", 0.3, 2.3, centered(540, 300, 660, 170), _pop(0, 0.45), radius=85,
            kind="rounded-rectangle", layers=[shadow("#B5432A", 0, 10, 0, 0.9), fill("#FF7A59"), no_stroke()],
            rotation=tilt)
    words = t.track("text", "Títulos")
    t.text(words, "storytime", 0.35, 2.25, centered(540, 300, 660, 170),
           text_style("Fredoka", 110, [fill("#FFFFFF")], weight=700, anim_in=tanim("bounce", duration=0.5,
                                                                                    unit="character", stagger=0.04)),
           label="Título", rotation=tilt)
    t.text(t.track("text", "Gancho"), "Les cuento lo que me pasó…", 0.9, 1.6, Box(80, 1150, 920, 260),
           text_style("Fredoka", 80, [fill("#3D2C2C")], weight=600, line=1.05,
                      anim_in=tanim("typewriter", duration=0.8, unit="character")), label="Gancho")
    parts = ["Fui a una fiesta sin conocer a nadie…", "…y terminé siendo la que más bailó",
             "Moraleja: ve aunque te dé miedo"]
    chips = t.track("shape", "Parte")
    counters = t.track("text", "Contador")
    captions = t.track("text", "Partes")
    for i, part in enumerate(parts):
        start = 2.9 + i * 3.03
        dur = 3.03 if i < 2 else t.duration - start
        _pill(t, chips, "#FF7A59", start, dur, Box(820, 140, 200, 90), _pop(0, 0.35))
        t.text(counters, f"{i + 1}/3", start, dur, Box(820, 140, 200, 90),
               text_style("Fredoka", 54, [fill("#FFFFFF")], weight=700), editable=False)
        t.text(captions, part, start, dur, Box(90, 1440, 900, 300),
               text_style("Fredoka", 62, [fill("#3D2C2C")], weight=600, line=1.1, box=("#FFFFFF", 0.95),
                          box_pad=26, box_radius=28, anim_in=tanim("pop", duration=0.35, unit="word", stagger=0.05),
                          anim_out=tanim("fade", duration=0.2)), label=f"Parte {i + 1}")
    t.song("happy-whistling-ukulele", 0.0, 0.8)
    return t


# 5 -----------------------------------------------------------------------------------------------


def tres_consejos() -> Template:
    """A title, then three numbered tips slide in; the older ones dim when the next arrives."""
    t = Template("tres-consejos", "3 consejos para…", "3 tips for…", "text", 12.0,
                 order=1416, tags=["consejos", "tips", "lista", "estudiar", "educativo"], thumb_at=10.0)
    bg = t.track("video", "Fondo")
    t.photo(bg, "study-03", 0, 12.0, FULL, _kb(12.0, 1.05, 1.15), label="Fondo",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=5),
                     effect("color.basic", exposure=-0.3, saturation=-0.2)])
    t.solid(t.track("shape", "Velo"), "#0F3D3E",
            layers=[gradient([(0, "#0F3D3E", 0.55), (1, "#0F3D3E", 0.92)], angle=90), no_stroke()])
    words = t.track("text", "Título")
    t.text(words, "3 consejos para estudiar mejor", 0.2, 11.8, Box(70, 170, 940, 340),
           text_style("Archivo Black", 96, [shadow("#000000", 0, 6, 0, 0.5), fill("#F2C14E")], weight=400,
                      align="left", line=1.0, anim_in=tanim("rise-by-word", duration=0.45, unit="word",
                                                            stagger=0.12)), label="Título")
    tips = ["Estudia en bloques de 25 minutos", "Explícalo en voz alta como si enseñaras",
            "Duerme bien antes del examen"]
    for i, tip in enumerate(tips):
        at = 2.0 + i * 3.0
        dur = t.duration - at
        y = 700 + i * 330
        slide = [(0, {"dx": -900}, "out"), (0.5, {})]
        dim = keys([(0, 1.0), (3.0 - 0.2, 1.0, "smooth"), (3.0 + 0.2, 0.45)]) if i < 2 else keys([(0, 1.0)])
        circles = t.track("shape", f"Número {i + 1}")
        t.solid(circles, "#F2C14E", at, dur, centered(150, y, 160, 160), slide, kind="ellipse", opacity=dim)
        nums = t.track("text", f"Número {i + 1}")
        t.text(nums, str(i + 1), at, dur, centered(150, y, 160, 160),
               text_style("Archivo Black", 100, [fill("#0F3D3E")], weight=400), slide, editable=False, opacity=dim)
        texts = t.track("text", f"Consejo {i + 1}")
        t.text(texts, tip, at + 0.1, dur - 0.1, Box(270, y - 130, 770, 260),
               text_style("Manrope", 58, [shadow("#000000", 0, 3, 10, 0.4), fill("#FFFFFF")], weight=800,
                          align="left", line=1.08), slide, label=f"Consejo {i + 1}", opacity=dim)
    cta = t.track("text", "Llamada")
    t.text(cta, "Guárdalo para después", 10.3, 1.7, Box(70, 1720, 940, 90),
           text_style("Manrope", 46, [fill("#F2C14E")], weight=700, align="left", spacing=2,
                      anim_in=tanim("slide-up", duration=0.4), anim_loop=tanim("pulse", amount=4, speed=1.2)),
           label="Llamada")
    t.song("from-page-to-practice", 0.0, 0.8)
    return t


# 6 -----------------------------------------------------------------------------------------------


def cita_minimalista() -> Template:
    """Paper white, a terracotta rule that draws itself, a serif quote word by word, a small round portrait."""
    t = Template("cita-minimalista", "Cita minimalista", "Minimal quote", "text", 8.0,
                 order=1420, tags=["cita", "frase", "minimalista", "elegante", "reflexión"], thumb_at=6.6,
                 background="#F7F4EF")
    t.solid(t.track("shape", "Papel"), "#F7F4EF")
    rule = t.track("shape", "Línea")
    t.solid(rule, "#C2410C", 0.2, 7.8, Box(470, 520, 140, 4), [(0, {"sx": 0.0}, "inout"), (0.8, {})])
    marks = t.track("text", "Comillas")
    t.text(marks, "“", 0.5, 7.5, centered(540, 640, 300, 200),
           text_style("Prata", 220, [fill("#C2410C")], weight=400, anim_in=tanim("fade", duration=0.8)),
           editable=False)
    quote = t.track("text", "Cita")
    t.text(quote, "Lo simple, bien hecho, nunca pasa de moda.", 0.9, 7.1, Box(110, 760, 860, 520),
           text_style("Libre Baskerville", 70, [fill("#1E1E1E")], weight=400, italic=True, line=1.35,
                      anim_in=tanim("blur-in", duration=0.6, unit="word", stagger=0.14, blur=10)), label="Cita")
    ring = t.track("shape", "Aro")
    t.solid(ring, "#C2410C", 3.2, 4.8, centered(540, 1430, 196, 196), _pop(0, 0.5), kind="ellipse",
            layers=[stroke(3, "#C2410C"), _hollow()])
    portraits = t.track("video", "Autor")
    face = t.photo(portraits, "portrait-03", 3.2, 4.8, centered(540, 1430, 180, 180), _pop(0, 0.5), label="Autor")
    t.mask(portraits, face, "ellipse")
    author = t.track("text", "Autor")
    t.text(author, "— Tu nombre", 3.6, 4.4, Box(110, 1560, 860, 80),
           text_style("Inter", 38, [fill("#6B6B6B")], weight=500, spacing=8, case="upper",
                      anim_in=tanim("fade", duration=0.8)), label="Autor")
    t.adjust([effect("stylize.film_grain", amount=0.08, grainSize=1.2)], name="Grano")
    t.song("the-celebrated-minuet-for-piano", 0.0, 0.75)
    return t


# 7 -----------------------------------------------------------------------------------------------


def encuesta_cual_prefieres() -> Template:
    """Two halves slide in, the question sits between them, then the votes fill each half."""
    t = Template("encuesta-cual-prefieres", "¿Cuál prefieres?", "Which one do you prefer?", "text", 8.0,
                 order=1424, tags=["encuesta", "cuál prefieres", "esto o aquello", "comenta", "interacción"],
                 thumb_at=5.4, background="#1B1033")
    halves = [("beach-06", "A · Playa", "38%", 0.38, 0, -1100), ("nature-05", "B · Montaña", "62%", 0.62, 960, 1100)]
    for i, (sample, label, pct, share, y, dx) in enumerate(halves):
        photos = t.track("video", f"Opción {'AB'[i]}")
        t.photo(photos, sample, 0.1 * i, 8.0 - 0.1 * i, Box(0, y, 1080, 960),
                [(0, {"dx": dx}, "out"), (0.6, {}, "linear"), (8.0 - 0.1 * i, {"s": 1.06})],
                label=f"Opción {'AB'[i]}")
        names = t.track("text", f"Nombre {'AB'[i]}")
        t.text(names, label, 0.8, 7.2, Box(60, y + 120 if i else y + 110, 960, 130),
               text_style("Lilita One", 96, [shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], weight=400,
                          align="left", anim_in=tanim("slide-left", duration=0.4)), label=f"Nombre {'AB'[i]}")
        bar_y = y + 960 - 190 if i == 0 else y + 960 - 170
        backs = t.track("shape", f"Barra {'AB'[i]}")
        t.solid(backs, "#000000", 4.0, 4.0, Box(60, bar_y, 960, 110), _pop(0, 0.3), radius=55,
                kind="rounded-rectangle", alpha=0.45)
        fills = t.track("shape", f"Votos {'AB'[i]}")
        w = 960 * share
        t.solid(fills, "#F59E0B" if i else "#7C3AED", 4.3, 3.7, Box(60, bar_y, w, 110),
                [(0, {"sx": 0.0, "dx": -w / 2}, "out"), (1.0, {})], radius=55, kind="rounded-rectangle")
        pcts = t.track("text", f"Porcentaje {'AB'[i]}")
        t.text(pcts, pct, 4.9, 3.1, Box(80, bar_y, 920, 110),
               text_style("Lilita One", 72, [fill("#FFFFFF")], weight=400, align="right",
                          anim_in=tanim("pop", duration=0.35)), label=f"Porcentaje {'AB'[i]}")
    middle = t.track("shape", "Pregunta")
    _pill(t, middle, "#7C3AED", 0.6, 5.8, centered(540, 960, 700, 150), _pop(0, 0.5),
          layers=[shadow("#000000", 0, 10, 30, 0.5), fill("#7C3AED"), stroke(6, "#FFFFFF")])
    _pill(t, middle, "#F59E0B", 6.4, 1.6, centered(540, 960, 700, 150), _pop(0, 0.4),
          layers=[shadow("#000000", 0, 10, 30, 0.5), fill("#F59E0B"), stroke(6, "#FFFFFF")])
    ask = t.track("text", "Pregunta")
    t.text(ask, "¿Cuál prefieres?", 0.7, 5.7, centered(540, 960, 700, 150),
           text_style("Lilita One", 80, [fill("#FFFFFF")], weight=400), label="Pregunta")
    t.text(ask, "¡Comenta A o B!", 6.5, 1.5, centered(540, 960, 700, 150),
           text_style("Lilita One", 80, [fill("#1B1033")], weight=400, anim_in=tanim("pop", duration=0.3),
                      anim_loop=tanim("pulse", amount=5, speed=1.4)), label="Llamada")
    t.song("and-just-like-that", 0.0, 0.8)
    return t


# 8 -----------------------------------------------------------------------------------------------


def ultimo_momento() -> Template:
    """Breaking-news dress: EN VIVO tag, a red strap, a white headline bar and a ticker that runs."""
    t = Template("ultimo-momento-noticia", "Último momento", "Breaking news", "text", 8.0,
                 order=1428, tags=["noticia", "último momento", "anuncio", "en vivo", "novedad"], thumb_at=3.0)
    video = t.track("video", "Video")
    t.photo(video, "city-02", 0, 8.0, FULL, [(0, {"s": 1.08, "dx": 30}, "linear"), (8.0, {"s": 1.18, "dx": -30})],
            label="Tu video", effects=[effect("color.basic", contrast=0.15, saturation=-0.1)])
    live = t.track("shape", "En vivo")
    t.solid(live, "#D90429", 0.2, 7.8, Box(50, 120, 260, 84), [(0, {"dx": -360}, "out"), (0.4, {})], radius=8,
            kind="rounded-rectangle")
    dot = t.track("shape", "Punto")
    t.solid(dot, "#FFFFFF", 0.6, 7.4, centered(92, 162, 26, 26), kind="ellipse", opacity=_blink(7.4, 1.0))
    clock = t.track("text", "Hora")
    t.text(clock, "EN VIVO", 0.6, 7.4, Box(118, 120, 192, 84),
           text_style("Oswald", 46, [fill("#FFFFFF")], weight=700, spacing=3, align="left"), editable=False)
    t.text(t.track("text", "Hora"), "20:45", 0.6, 7.4, Box(760, 120, 270, 84),
           text_style("Oswald", 52, [shadow("#000000", 0, 3, 10, 0.6), fill("#FFFFFF")], weight=600, align="right",
                      anim_in=tanim("fade", duration=0.4)), label="Hora")
    strap = t.track("shape", "Franja roja")
    t.solid(strap, "#D90429", 0.5, 7.5, Box(0, 1310, 760, 110), [(0, {"dx": -760}, "out"), (0.45, {})])
    band = t.track("shape", "Franja blanca")
    t.solid(band, "#FFFFFF", 0.7, 7.3, Box(0, 1420, 1080, 250), [(0, {"dx": 1080}, "out"), (0.45, {})],
            layers=[shadow("#000000", 0, 10, 30, 0.4), fill("#FFFFFF"), no_stroke()])
    words = t.track("text", "Titulares")
    t.text(words, "ÚLTIMO MOMENTO", 0.8, 7.2, Box(50, 1310, 700, 110),
           text_style("Oswald", 70, [fill("#FFFFFF")], weight=700, spacing=4, align="left",
                      anim_in=tanim("wipe", duration=0.4, angle=0)), label="Rótulo")
    t.text(t.track("text", "Titular"), "Hoy lancé algo que lo cambia todo", 1.1, 6.9, Box(50, 1430, 980, 230),
           text_style("Roboto", 70, [fill("#0B0B0B")], weight=900, align="left", line=1.05,
                      anim_in=tanim("slide-up", duration=0.4, unit="line", stagger=0.1)), label="Titular")
    ticker = t.track("shape", "Cinta")
    t.solid(ticker, "#0B0B0B", 0.9, 7.1, Box(0, 1670, 1080, 96), [(0, {"dy": 120}, "out"), (0.4, {})])
    crawl = t.track("text", "Cinta")
    t.text(crawl, "Más detalles en mi perfil  •  Comparte con quien lo necesita  •  Síguenos para no perderte nada",
           1.0, 7.0, Box(200, 1670, 3200, 96),
           text_style("Roboto", 44, [fill("#FFFFFF")], weight=500, align="left", line=1.0),
           [(0, {"dx": 700}, "linear"), (7.0, {"dx": -1900})], label="Cinta")
    tag = t.track("shape", "Etiqueta")
    t.solid(tag, "#FFD60A", 0.9, 7.1, Box(0, 1670, 190, 96), [(0, {"dy": 120}, "out"), (0.4, {})])
    t.text(t.track("text", "Etiqueta"), "HOY", 1.0, 7.0, Box(0, 1670, 190, 96),
           text_style("Oswald", 52, [fill("#0B0B0B")], weight=700, spacing=3), label="Etiqueta")
    t.adjust([effect("strobe_flash", animated={"flash": _spike([0.0, 0.5], 0.6, 0.18)}, tint=0.1),
              effect("rgb_split", animated={"amount": _spike([0.0, 0.5], 18.0, 0.2)})], name="Golpe")
    t.song("one-step-closer", 0.0, 0.85)
    return t


# 9 -----------------------------------------------------------------------------------------------


def podcast_subtitulos() -> Template:
    """A podcast clip: episode chip, a moving waveform and big captions that change every phrase."""
    t = Template("clip-de-podcast", "Clip de podcast", "Podcast clip", "text", 10.0,
                 order=1432, tags=["podcast", "subtítulos", "entrevista", "clip", "conversación"], thumb_at=4.9)
    video = t.track("video", "Video")
    t.photo(video, "podcast-02", 0, 10.0, FULL, [(0, {"s": 1.18, "dy": 80}, "linear"), (10.0, {"s": 1.08, "dy": 80})],
            label="Tu video")
    shade = t.track("shape", "Sombra")
    t.solid(shade, "#000000", 0, 10.0, Box(0, 960, 1080, 960),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.85)], angle=90), no_stroke()])
    chip = t.track("shape", "Episodio")
    _pill(t, chip, "#0B0F19", 0.2, 9.8, Box(60, 110, 660, 96), [(0, {"dy": -200}, "out"), (0.5, {})], alpha=0.85)
    mic = t.track("shape", "Grabando")
    t.solid(mic, "#22D3EE", 0.5, 9.5, centered(114, 158, 30, 30), kind="ellipse", opacity=_blink(9.5, 1.2, 0.35))
    head = t.track("text", "Episodio")
    t.text(head, "EP. 24 · Nombre del podcast", 0.5, 9.5, Box(150, 110, 560, 96),
           text_style("Inter", 38, [fill("#FFFFFF")], weight=700, align="left",
                      anim_in=tanim("fade", duration=0.4)), label="Episodio")
    rng = random.Random(24)
    for k in range(15):
        bars = t.track("shape", "Onda")
        pts, at = [], 0.0
        while at < 10.0:
            pts.append((at, rng.uniform(0.25, 1.0), "smooth"))
            at += rng.uniform(0.18, 0.32)
        heights = keys([(p[0], 30 + 90 * p[1], "smooth") for p in pts])
        ys = keys([(p[0], 1230 - (30 + 90 * p[1]) / 2, "smooth") for p in pts])
        t.solid(bars, "#22D3EE", 0.3, 9.7, Box(330 + k * 30, 1200, 16, 60), radius=8, kind="rounded-rectangle",
                alpha=0.9, height=heights, y=ys)
    chunks = ["LO QUE NADIE", "TE DICE SOBRE", "*EMPEZAR*", "ES QUE NUNCA", "TE VAS A SENTIR", "*LISTO*"]
    captions = t.track("text", "Subtítulos")
    accent = {"rule": "none", "colorEnabled": True, "color": "#ffFACC15"}
    for i, chunk in enumerate(chunks):
        at = 0.6 + i * 1.5
        dur = 1.5 if i < len(chunks) - 1 else t.duration - at
        t.text(captions, chunk, at, dur, Box(50, 1330, 980, 300),
               text_style("Montserrat", 108, [shadow("#000000", 0, 8, 0, 0.9), stroke(10, "#000000"), fill("#FFFFFF")],
                          weight=900, line=0.95, accent=accent,
                          anim_in=tanim("pop", duration=0.25, unit="word", stagger=0.12, ease="back")),
               label=f"Subtítulo {i + 1}")
    guest = t.track("text", "Invitado")
    t.text(guest, "con Ana Ruiz", 0.8, 9.2, Box(60, 1700, 960, 80),
           text_style("Inter", 44, [fill("#22D3EE")], weight=700, spacing=2,
                      anim_in=tanim("fade", duration=0.5)), label="Invitado")
    t.song("i-guess-what-i-m-trying-to-say", 0.0, 0.45)
    return t


# 10 ----------------------------------------------------------------------------------------------


def entrevista_rotulo() -> Template:
    """An interview shot with a TV lower third that builds in steps: bar, name panel, role panel."""
    t = Template("entrevista-con-rotulo", "Entrevista con rótulo", "Interview lower third", "text", 7.0,
                 order=1436, tags=["entrevista", "rótulo", "nombre", "testimonio", "noticias"], thumb_at=3.0)
    video = t.track("video", "Video")
    t.photo(video, "man-04", 0, 7.0, FULL, [(0, {"s": 1.12, "dx": -40}, "linear"), (7.0, {"s": 1.02, "dx": 20})],
            label="Tu video", effects=[effect("color.basic", contrast=0.1, vibrance=0.1)])
    tag = t.track("shape", "Etiqueta")
    t.solid(tag, "#1D4ED8", 0.3, 6.7, Box(720, 120, 310, 70), [(0, {"dx": 400}, "out"), (0.45, {})])
    words = t.track("text", "Etiqueta")
    t.text(words, "ENTREVISTA", 0.4, 6.6, Box(720, 120, 310, 70),
           text_style("Barlow", 36, [fill("#FFFFFF")], weight=800, spacing=6), label="Etiqueta")
    accent = t.track("shape", "Acento")
    t.solid(accent, "#1D4ED8", 0.6, 6.0, Box(60, 1440, 16, 220), [(0, {"sy": 0.0}, "out"), (0.35, {})])
    panel = t.track("shape", "Panel")
    t.solid(panel, "#FFFFFF", 0.8, 5.8, Box(76, 1440, 800, 130), [(0, {"sx": 0.0, "dx": -400}, "out"), (0.45, {})],
            layers=[shadow("#000000", 0, 8, 24, 0.35), fill("#FFFFFF"), no_stroke()])
    role = t.track("shape", "Cargo")
    t.solid(role, "#1D4ED8", 1.1, 5.5, Box(76, 1570, 620, 90), [(0, {"sx": 0.0, "dx": -310}, "out"), (0.45, {})])
    names = t.track("text", "Nombre")
    t.text(names, "Carlos Mendoza", 1.1, 5.5, Box(110, 1440, 760, 130),
           text_style("Barlow", 76, [fill("#0F172A")], weight=700, align="left",
                      anim_in=tanim("slide-up", duration=0.35, unit="character", stagger=0.02)), label="Nombre")
    roles = t.track("text", "Cargo")
    t.text(roles, "Chef y fundador de Sazón", 1.4, 5.2, Box(110, 1570, 580, 90),
           text_style("Barlow", 42, [fill("#FFFFFF")], weight=500, align="left",
                      anim_in=tanim("fade", duration=0.4)), label="Cargo")
    for track in (accent, panel, role, names, roles):
        track.clips[0]["animOut"] = anim("fade", 0.35)
    t.song("bebop-for-joey", 0.0, 0.7)
    return t


# 11 ----------------------------------------------------------------------------------------------


def intro_vlog() -> Template:
    """Four snapshots land on a cream table in turn, then the vlog title is written over them."""
    t = Template("intro-de-vlog", "Intro de vlog", "Vlog intro", "intro", 7.0,
                 order=1440, tags=["vlog", "intro", "día conmigo", "rutina", "aesthetic"], thumb_at=5.6,
                 background="#FEFAE0")
    t.solid(t.track("shape", "Fondo"), "#FEFAE0",
            layers=[gradient([(0, "#FEFAE0"), (1, "#E9EDC9")], angle=90), no_stroke()])
    spots = [(360, 640, -8), (720, 760, 7), (380, 1180, 5), (700, 1300, -6)]
    samples = ["selfie-02", "coffee-03", "friends-11", "nature-02"]
    for i, ((x, y, tilt), sample) in enumerate(zip(spots, samples)):
        at = 0.3 + i * 1.0
        dur = t.duration - at
        land = [(0, {"s": 1.4, "dy": -120}, "out"), (0.35, {})]
        rot = keys([(0, tilt * 2.2, "out"), (0.35, tilt)])
        frames = t.track("shape", f"Marco {i + 1}")
        t.solid(frames, "#FFFFFF", at, dur, centered(x, y, 500, 640), land, radius=10, kind="rounded-rectangle",
                layers=[shadow("#3A5A40", 0, 14, 30, 0.3), fill("#FFFFFF"), no_stroke()], rotation=rot)
        photos = t.track("video", f"Foto {i + 1}")
        t.photo(photos, sample, at, dur, centered(x, y, 460, 600), land, rotation=rot, label=f"Toma {i + 1}")
    sticker = t.track("shape", "Sticker")
    _pill(t, sticker, "#A3B18A", 4.3, 2.7, centered(540, 300, 380, 110), _pop(0, 0.4),
          layers=[shadow("#3A5A40", 0, 6, 0, 0.8), fill("#A3B18A"), no_stroke()], rotation=keys([(0, -5)]))
    words = t.track("text", "Textos")
    t.text(words, "VLOG #12", 4.35, 2.65, centered(540, 300, 380, 110),
           text_style("Outfit", 62, [fill("#FFFFFF")], weight=800, spacing=4), label="Número",
           rotation=keys([(0, -5)]))
    t.text(t.track("text", "Título"), "un día conmigo", 4.5, 2.5, Box(40, 1560, 1000, 200),
           text_style("Gloria Hallelujah", 120, [shadow("#FFFFFF", 0, 0, 14, 0.9), stroke(8, "#FEFAE0"),
                                                 fill("#3A5A40")], weight=400,
                      anim_in=tanim("typewriter", duration=0.9, unit="character")), label="Título")
    t.text(t.track("text", "Fecha"), "15 · 10 · 2026", 0.3, 6.7, Box(40, 1770, 1000, 80),
           text_style("Kalam", 50, [fill("#3A5A40", 0.8)], weight=400, spacing=4,
                      anim_in=tanim("fade", duration=0.6)), label="Fecha")
    t.song("magic-in-the-garden", 0.0, 0.85)
    return t


# 12 ----------------------------------------------------------------------------------------------


def intro_podcast() -> Template:
    """Dark studio look: the host in a circle with orange sound rings, an equalizer and the show title."""
    t = Template("intro-de-podcast", "Intro de podcast", "Podcast intro", "intro", 6.0,
                 order=1444, tags=["podcast", "intro", "episodio", "audio", "programa"], thumb_at=3.8,
                 background="#111827")
    t.solid(t.track("shape", "Fondo"), "#111827",
            layers=[gradient([(0, "#1F2937"), (1, "#0B0F19")], angle=90), no_stroke()])
    for k in range(3):
        rings = t.track("shape", f"Onda {k + 1}")
        at = 0.6 + k * 0.6
        while at < 6.0:
            dur = min(1.8, 6.0 - at)
            t.solid(rings, "#F97316", at, dur, centered(540, 760, 500, 500),
                    [(0, {"s": 1.0}, "out"), (dur, {"s": 1.55})], kind="ellipse",
                    layers=[stroke(6, "#F97316"), _hollow()], opacity=keys([(0, 0.9), (dur, 0.0)]))
            at += 1.8
    ring = t.track("shape", "Aro")
    t.solid(ring, "#F97316", 0.3, 5.7, centered(540, 760, 500, 500), _pop(0, 0.5), kind="ellipse",
            layers=[glow("#F97316", 40, 0.6), fill("#F97316"), no_stroke()])
    hosts = t.track("video", "Foto")
    face = t.photo(hosts, "creator-02", 0.3, 5.7, centered(540, 760, 470, 470), _pop(0, 0.5), label="Tu foto")
    t.mask(hosts, face, "ellipse")
    rng = random.Random(12)
    for k in range(12):
        eq = t.track("shape", "Ecualizador")
        pts, at = [], 0.0
        while at < 4.8:
            pts.append(at)
            at += rng.uniform(0.15, 0.3)
        hs = [rng.uniform(20, 110) for _ in pts]
        t.solid(eq, "#F97316", 1.2, 4.8, Box(330 + k * 36, 1600, 20, 60), radius=10, kind="rounded-rectangle",
                height=keys([(a, h, "smooth") for a, h in zip(pts, hs)]),
                y=keys([(a, 1680 - h, "smooth") for a, h in zip(pts, hs)]))
    words = t.track("text", "Título")
    t.text(words, "Nombre del Podcast", 1.0, 5.0, Box(40, 1080, 1000, 300),
           text_style("Big Shoulders Display", 150, [shadow("#000000", 0, 8, 20, 0.6), fill("#FFFFFF")], weight=900,
                      case="upper", line=0.92, anim_in=tanim("rise", duration=0.5, unit="word", stagger=0.12)),
           label="Nombre")
    t.text(t.track("text", "Episodio"), "EPISODIO 07 · INVITADA ESPECIAL", 1.6, 4.4, Box(40, 1390, 1000, 70),
           text_style("Inter", 38, [fill("#F97316")], weight=700, spacing=6,
                      anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.015)), label="Episodio")
    t.song("downtown-boogie", 0.0, 0.85)
    return t


# 13 ----------------------------------------------------------------------------------------------


def cierre_parte_2() -> Template:
    """The video drains to grey, «PARTE 2» slams in neon and arrows point at your profile picture."""
    t = Template("cierre-parte-2", "Parte 2 en mi perfil", "Part 2 on my profile", "outro", 5.0,
                 order=1448, tags=["parte 2", "continuará", "cierre", "perfil", "seguir"], thumb_at=2.6,
                 background="#120B1F")
    video = t.track("video", "Video")
    t.photo(video, "friends-09", 0, 5.0, FULL, [(0, {"s": 1.0}, "linear"), (0.5, {"s": 1.04}, "linear"),
                                                (5.0, {"s": 1.12})], label="Tu video")
    t.adjust([effect("color.basic", animated={"saturation": keys([(0, 0.0), (0.3, 0.0, "smooth"), (0.7, -1.0)]),
                                              "exposure": keys([(0, 0.0), (0.3, 0.0, "smooth"), (0.7, -0.45)])})],
             name="Pausa")
    words = t.track("text", "Parte 2")
    t.text(words, "PARTE 2", 0.5, 4.5, Box(30, 520, 1020, 340),
           text_style("Bungee", 210, [shadow("#F15BB5", 10, 10, 0, 1.0), fill("#00F5D4")], weight=400,
                      keyframes={"pixelSize": keys([(0, 520, "snap"), (0.18, 210)])},
                      anim_loop=tanim("flicker", intensity=0.2, speed=4)), label="Título",
           rotation=keys([(0, -4)]))
    t.text(t.track("text", "Dónde"), "en mi perfil", 1.0, 4.0, Box(40, 860, 1000, 140),
           text_style("Outfit", 96, [shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], weight=800,
                      anim_in=tanim("typewriter", duration=0.6, unit="character")), label="Dónde")
    for k in range(3):
        arrows = t.track("text", "Flechas")
        t.text(arrows, "↓", 1.6 + k * 0.12, 3.4 - k * 0.12, centered(540, 1130 + k * 90, 200, 110),
               text_style("Inter", 110, [shadow("#000000", 0, 4, 10, 0.5), fill("#F15BB5")], weight=900),
               editable=False, opacity=_blink(3.4 - k * 0.12, 0.5, 0.15))
    ring = t.track("shape", "Aro")
    t.solid(ring, "#00F5D4", 2.0, 3.0, centered(540, 1560, 300, 300), _pop(0, 0.45), kind="ellipse",
            layers=[glow("#00F5D4", 30, 0.8), fill("#00F5D4"), no_stroke()])
    avatar = t.track("video", "Perfil")
    face = t.photo(avatar, "portrait-02", 2.0, 3.0, centered(540, 1560, 270, 270), _pop(0, 0.45),
                   label="Tu foto de perfil")
    t.mask(avatar, face, "ellipse")
    t.text(t.track("text", "Usuario"), "@tuusuario", 2.3, 2.7, Box(40, 1720, 1000, 90),
           text_style("Outfit", 54, [shadow("#000000", 0, 4, 12, 0.6), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("fade", duration=0.4)), label="Usuario")
    t.adjust([effect("beat_shake", animated={"amount": _spike([0.5], 0.9, 0.35)}, rotation=0.4),
              effect("rgb_split", animated={"amount": _spike([0.5], 24.0, 0.25)})], name="Golpe")
    t.song("new-hero-in-town", 0.0, 0.85)
    return t


# 14 ----------------------------------------------------------------------------------------------


def pantalla_final_videos() -> Template:
    """An end screen: two recommended videos as cards with play buttons, your face and a subscribe pill."""
    t = Template("pantalla-final-2-videos", "Pantalla final: 2 videos", "End screen: 2 videos", "outro", 8.0,
                 order=1452, tags=["pantalla final", "videos recomendados", "cierre", "suscríbete", "youtube shorts"],
                 thumb_at=4.0, background="#0B1020")
    t.solid(t.track("shape", "Fondo"), "#0B1020",
            layers=[gradient([(0, "#1A2240"), (1, "#0B1020")], angle=120), no_stroke()])
    title = t.track("text", "Título")
    t.text(title, "¿Quieres más?", 0.2, 7.8, Box(40, 150, 1000, 160),
           text_style("Outfit", 104, [fill("#FFFFFF")], weight=800, anim_in=tanim("rise", duration=0.5)),
           label="Título")
    cards = [("travel-07", "Mi viaje a Cusco", 420), ("food-03", "Ceviche en 5 minutos", 960)]
    for i, (sample, caption, y) in enumerate(cards):
        at = 0.6 + i * 0.35
        dur = t.duration - at
        land = [(0, {"s": 0.7, "dy": 120}, "back"), (0.5, {})]
        frames = t.track("shape", f"Tarjeta {i + 1}")
        t.solid(frames, "#FACC15", at, dur, Box(80, y, 920, 518), land, radius=30, kind="rounded-rectangle",
                layers=[shadow("#000000", 0, 16, 40, 0.5), fill("#FACC15"), no_stroke()])
        photos = t.track("video", f"Video {i + 1}")
        t.photo(photos, sample, at, dur, Box(92, y + 12, 896, 494), land, label=f"Video {i + 1}")
        strips = t.track("shape", f"Pie {i + 1}")
        t.solid(strips, "#000000", at, dur, Box(92, y + 386, 896, 120), land, alpha=0.6)
        plays = t.track("shape", f"Reproducir {i + 1}")
        beat_in = [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (1.0, {"s": 1.1}, "smooth"), (1.6, {}, "smooth"),
                   (2.2, {"s": 1.1}, "smooth"), (2.8, {})]
        t.solid(plays, "#FFFFFF", at + 0.4, dur - 0.4, centered(540, y + 200, 150, 150), beat_in, kind="ellipse",
                alpha=0.92)
        icons = t.track("shape", f"Icono {i + 1}")
        t.solid(icons, "#0B1020", at + 0.4, dur - 0.4, centered(548, y + 200, 62, 62), beat_in, kind="triangle",
                rotation=keys([(0, 90)]))
        caps = t.track("text", f"Pie {i + 1}")
        t.text(caps, caption, at + 0.3, dur - 0.3, Box(120, y + 386, 840, 120),
               text_style("Outfit", 54, [fill("#FFFFFF")], weight=700, align="left",
                      anim_in=tanim("fade", duration=0.4)), label=f"Título video {i + 1}")
    ring = t.track("shape", "Aro")
    t.solid(ring, "#FACC15", 1.6, 6.4, centered(200, 1680, 190, 190), _pop(0, 0.4), kind="ellipse")
    avatar = t.track("video", "Tu foto")
    face = t.photo(avatar, "portrait-07", 1.6, 6.4, centered(200, 1680, 170, 170), _pop(0, 0.4), label="Tu foto")
    t.mask(avatar, face, "ellipse")
    button = t.track("shape", "Botón")
    _pill(t, button, "#FACC15", 1.9, 6.1, Box(340, 1620, 640, 120),
          [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (1.4, {"s": 1.05}, "smooth"), (2.4, {})])
    t.text(t.track("text", "Botón"), "Suscríbete", 2.0, 6.0, Box(340, 1620, 640, 120),
           text_style("Outfit", 62, [fill("#0B1020")], weight=800), label="Botón")
    t.song("aquarium", 0.0, 0.8)
    return t


# 15 ----------------------------------------------------------------------------------------------


def cuenta_regresiva_10() -> Template:
    """A neon digital timer from 00:10 to 00:01 over a dim crowd, a draining bar, then the drop."""
    t = Template("cuenta-regresiva-10", "Cuenta regresiva de 10 s", "10-second countdown", "countdown", 12.0,
                 order=1456, tags=["cuenta regresiva", "10 segundos", "lanzamiento", "estreno", "fiesta"],
                 thumb_at=3.5, background="#0D0221")
    crowd = t.track("video", "Fotos")
    t.photo(crowd, "concert-01", 0, 10.0, FULL, _kb(10.0, 1.05, 1.25), label="Espera",
            effects=[effect("duotone", strength=0.85, shadowColor="#0d0221", highlightColor="#ff00a0", contrast=0.6),
                     effect("color.basic", exposure=-0.35)])
    t.photo(crowd, "concert-02", 10.0, 2.0, FULL, [(0, {"s": 1.25}, "snap"), (0.25, {"s": 1.04}, "linear"),
                                                   (2.0, {"s": 1.0})], label="Final",
            effects=[effect("color.basic", contrast=0.2, saturation=0.25)])
    head = t.track("text", "Antes")
    t.text(head, "EMPIEZA EN", 0.2, 9.8, Box(40, 560, 1000, 100),
           text_style("Orbitron", 60, [glow("#FF00A0", 24, 0.9), fill("#FF7AD0")], weight=700, spacing=12,
                      anim_in=tanim("fade", duration=0.5), anim_loop=tanim("flicker", intensity=0.25, speed=3)),
           label="Antes")
    digits = t.track("text", "Números")
    neon = lambda: text_style("Orbitron", 230, [glow("#00F0FF", 40, 0.9), stroke(4, "#B5FBFF"),  # noqa: E731
                                                fill("#E8FEFF")], weight=900,
                              keyframes={"pixelSize": keys([(0, 260, "snap"), (0.15, 230)])})
    for k in range(10):
        t.text(digits, f"00:{10 - k:02d}", float(k), 1.0, Box(0, 700, 1080, 360), neon(), editable=False)
    track = t.track("shape", "Barra")
    t.solid(track, "#FFFFFF", 0, 10.0, Box(140, 1160, 800, 20), radius=10, kind="rounded-rectangle", alpha=0.18)
    bar = t.track("shape", "Tiempo")
    t.solid(bar, "#00F0FF", 0, 10.0, Box(140, 1160, 800, 20), [(0, {}, "linear"), (10.0, {"sx": 0.0, "dx": -400})],
            radius=10, kind="rounded-rectangle", layers=[glow("#00F0FF", 20, 0.9), fill("#00F0FF"), no_stroke()])
    final = t.track("text", "Final")
    t.text(final, "¡AHORA!", 10.0, 2.0, Box(0, 640, 1080, 520),
           text_style("Orbitron", 200, [glow("#FF00A0", 50, 1.0), stroke(6, "#FFFFFF"), fill("#FF00A0")], weight=900,
                      keyframes={"pixelSize": keys([(0, 480, "snap"), (0.2, 200)])}), label="Final")
    flash = t.track("shape", "Destello")
    t.solid(flash, "#FFFFFF", 10.0, 0.35, FULL, opacity=keys([(0, 0.95, "out"), (0.35, 0.0)]))
    t.adjust([effect("zoom_pulse", animated={"punch": _spike([float(k) for k in range(10)], 0.25, 0.25)}),
              effect("rgb_split", animated={"amount": _spike([10.0], 30.0, 0.4)}),
              effect("beat_shake", animated={"amount": _spike([10.0], 1.0, 0.5)}, rotation=0.5)], name="Golpes")
    t.song("blippy-trance", 0.0, 0.9)
    return t


# 16 ----------------------------------------------------------------------------------------------


def checklist_marcado() -> Template:
    """A notebook page: each item gets its tick and a red strike, a polaroid of the trip, then «¡Listo!»."""
    t = Template("checklist-que-se-marca", "Checklist que se marca", "Ticking checklist", "text", 10.0,
                 order=1460, tags=["checklist", "lista", "pendientes", "viaje", "organización"], thumb_at=7.4,
                 background="#FFFDF5")
    t.solid(t.track("shape", "Papel"), "#FFFDF5")
    margin = t.track("shape", "Margen")
    t.solid(margin, "#E57373", 0, 10.0, Box(96, 0, 4, 1920), alpha=0.7)
    items = ["Pasaporte", "Cargador del celular", "Bloqueador", "Reservas impresas"]
    ys = [600, 790, 980, 1170]
    for y in ys + [420]:
        lines = t.track("shape", "Renglón")
        t.solid(lines, "#A7C7E7", 0, 10.0, Box(0, y + 70, 1080, 3), alpha=0.8)
    polaroid = t.track("shape", "Polaroid")
    drop = [(0, {"s": 1.3, "dy": -200}, "out"), (0.45, {})]
    rot = keys([(0, 14, "out"), (0.45, 6)])
    t.solid(polaroid, "#FFFFFF", 0.6, 9.4, centered(800, 1560, 400, 470), drop, radius=4,
            layers=[shadow("#1F2A44", 4, 14, 28, 0.3), fill("#FFFFFF"), no_stroke()], rotation=rot)
    photo = t.track("video", "Foto")
    t.photo(photo, "travel-07", 0.6, 9.4, centered(800, 1530, 350, 350),
            [(0, {"s": 1.3, "dy": -200 - 30 * 0.3}, "out"), (0.45, {})], rotation=rot, label="Tu foto")
    words = t.track("text", "Título")
    t.text(words, "Antes de viajar:", 0.2, 9.8, Box(130, 320, 900, 150),
           text_style("Patrick Hand", 110, [fill("#1F2A44")], weight=400, align="left",
                      anim_in=tanim("typewriter", duration=0.7, unit="character")), label="Título")
    for i, (item, y) in enumerate(zip(items, ys)):
        shown = 0.6 + i * 0.25
        ticked = 2.2 + i * 1.5
        boxes = t.track("shape", f"Casilla {i + 1}")
        t.solid(boxes, "#1F2A44", shown, 10.0 - shown, centered(175, y + 20, 74, 74), _pop(0, 0.35), radius=10,
                kind="rounded-rectangle", layers=[stroke(5, "#1F2A44"), _hollow()])
        texts = t.track("text", f"Tarea {i + 1}")
        t.text(texts, item, shown, 10.0 - shown, Box(250, y - 40, 780, 120),
               text_style("Patrick Hand", 80, [fill("#1F2A44")], weight=400, align="left",
                          anim_in=tanim("fade", duration=0.3)), label=f"Tarea {i + 1}",
               opacity=keys([(0, 1.0), (ticked - shown + 0.2, 1.0, "smooth"), (ticked - shown + 0.5, 0.55)]))
        ticks = t.track("text", f"Visto {i + 1}")
        t.text(ticks, "✓", ticked, 10.0 - ticked, centered(185, y + 5, 140, 140),
               text_style("DM Sans", 130, [fill("#2A9D8F")], weight=700, anim_in=tanim("stamp", duration=0.25)),
               editable=False)
        width = min(760, 40 + 38 * len(item))
        strikes = t.track("shape", f"Tachado {i + 1}")
        t.solid(strikes, "#E57373", ticked + 0.15, 10.0 - ticked - 0.15, Box(245, y + 20, width, 7),
                [(0, {"sx": 0.0, "dx": -width / 2}, "out"), (0.35, {})], radius=3, kind="rounded-rectangle")
    done = t.track("text", "Listo")
    t.text(done, "¡Listo!", 8.4, 1.6, Box(80, 1420, 560, 200),
           text_style("Patrick Hand", 150, [fill("#2A9D8F")], weight=400, anim_in=tanim("stamp", duration=0.35)),
           label="Cierre", rotation=keys([(0, -6)]))
    t.song("stunted-adventure", 0.0, 0.8)
    return t


# 17 ----------------------------------------------------------------------------------------------


def cosas_que_no_sabias() -> Template:
    """A loud title card, then three «Dato» cards slide in from the right, each in its own colour."""
    t = Template("cosas-que-no-sabias", "Cosas que no sabías", "Things you didn't know", "text", 12.0,
                 order=1464, tags=["datos curiosos", "sabías que", "curiosidades", "educativo", "trivia"],
                 thumb_at=1.4, background="#FFBE0B")
    t.solid(t.track("shape", "Fondo"), "#FFBE0B")
    burst = t.track("shape", "Estallido")
    t.solid(burst, "#FFFFFF", 0.1, 2.1, centered(540, 960, 900, 900), _pop(0, 0.5), kind="burst", points=16,
            innerRatio=0.8, rotation=keys([(0, 0), (2.1, 25)]))
    marks = t.track("text", "Pregunta")
    t.text(marks, "?", 0.3, 1.9, centered(820, 520, 260, 300),
           text_style("Luckiest Guy", 260, [shadow("#111111", 0, 10, 0, 1.0), fill("#FF006E")], weight=400,
                      anim_in=tanim("bounce", duration=0.5)), editable=False, rotation=keys([(0, 14)]))
    title = t.track("text", "Título")
    t.text(title, "Cosas que no sabías", 0.2, 2.0, Box(60, 640, 960, 640),
           text_style("Luckiest Guy", 150, [shadow("#111111", 0, 12, 0, 1.0), stroke(10, "#111111"), fill("#FFFFFF")],
                      weight=400, line=1.0, anim_in=tanim("drop", duration=0.5, unit="word", stagger=0.12)),
           label="Título")
    facts = [("pet-05", "#FF006E", "Los perros pueden entender más de 150 palabras."),
             ("coffee-03", "#3A86FF", "El café es la semilla de una fruta roja."),
             ("food-03", "#8338EC", "El ceviche es Patrimonio Cultural de la Nación del Perú.")]
    for i, (sample, colour, fact) in enumerate(facts):
        at = 2.1 + i * 3.3
        dur = 3.3 if i < 2 else t.duration - at
        slide = [(0, {"dx": 1100}, "out"), (0.45, {})]
        backs = t.track("shape", f"Dato {i + 1}")
        t.solid(backs, colour, at, dur, FULL, slide)
        frames = t.track("shape", f"Marco {i + 1}")
        t.solid(frames, "#FFFFFF", at, dur, Box(80, 260, 920, 860), slide, radius=36, kind="rounded-rectangle",
                layers=[shadow("#111111", 0, 12, 0, 1.0), fill("#FFFFFF"), no_stroke()])
        photos = t.track("video", f"Foto {i + 1}")
        t.photo(photos, sample, at, dur, Box(100, 280, 880, 820),
                [(0, {"dx": 1100}, "out"), (0.45, {}, "linear"), (dur, {"s": 1.05})], label=f"Foto {i + 1}")
        pills = t.track("shape", f"Píldora {i + 1}")
        _pill(t, pills, "#111111", at + 0.4, dur - 0.4, Box(80, 1170, 330, 100), _pop(0, 0.35))
        tags = t.track("text", f"Número {i + 1}")
        t.text(tags, f"DATO #{i + 1}", at + 0.45, dur - 0.45, Box(80, 1170, 330, 100),
               text_style("Luckiest Guy", 60, [fill("#FFBE0B")], weight=400), editable=False)
        texts = t.track("text", f"Dato {i + 1}")
        t.text(texts, fact, at + 0.5, dur - 0.5, Box(80, 1310, 920, 440),
               text_style("Lexend", 70, [fill("#FFFFFF")], weight=700, align="left", line=1.12,
                          anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.06)),
               label=f"Dato {i + 1}")
    t.song("my-giant-bunny-friend", 0.0, 0.8)
    return t


# 18 ----------------------------------------------------------------------------------------------


def meme_clasico() -> Template:
    """The classic: white outlined caps above, the punchline below lands with a zoom and a shake."""
    t = Template("meme-texto-arriba-abajo", "Meme clásico", "Classic meme", "text", 6.0,
                 order=1468, tags=["meme", "humor", "texto arriba y abajo", "chistoso", "relatable"], thumb_at=4.0,
                 background="#000000")
    video = t.track("video", "Video")
    t.photo(video, "man-03", 0, 6.0, FULL, [(0, {"s": 1.0}, "linear"), (2.6, {"s": 1.06}, "snap"),
                                            (2.8, {"s": 1.22}, "linear"), (6.0, {"s": 1.26})], label="Tu video")
    meme = lambda: text_style("Anton", 120, [stroke(12, "#000000"), fill("#FFFFFF")], weight=400,  # noqa: E731
                              case="upper", line=1.0)
    top = t.track("text", "Arriba")
    t.text(top, "Cuando dices «solo un capítulo más»", 0.0, 6.0, Box(40, 90, 1000, 420),
           {**meme(), "valign": "top", "animation": {"in": tanim("pop", duration=0.3, unit="word", stagger=0.08)}},
           label="Texto de arriba")
    bottom = t.track("text", "Abajo")
    t.text(bottom, "y ya son las 4 a. m.", 2.6, 3.4, Box(40, 1400, 1000, 420),
           {**meme(), "valign": "bottom", "animation": {"in": tanim("stamp", duration=0.25)}},
           label="Texto de abajo")
    t.adjust([effect("zoom_pulse", animated={"punch": _spike([2.6], 0.7, 0.3)}),
              effect("beat_shake", animated={"amount": _spike([2.6], 0.8, 0.45)}, rotation=0.4)], name="Golpe")
    t.song("fake-it-til-you-fake-it", 0.0, 0.85)
    return t


# 19 ----------------------------------------------------------------------------------------------


def opinion_impopular() -> Template:
    """A red-tinted face, a stamped label, the take typed out in heavy caps, then «Sí / No»."""
    t = Template("opinion-impopular", "Opinión impopular", "Unpopular opinion", "text", 8.0,
                 order=1472, tags=["opinión impopular", "debate", "polémica", "comenta", "hot take"], thumb_at=5.0,
                 background="#111111")
    t.solid(t.track("shape", "Fondo"), "#111111")
    face = t.track("video", "Foto")
    t.photo(face, "portrait-02", 0, 8.0, Box(0, 0, 1080, 1000), _kb(8.0, 1.0, 1.08), label="Tu foto",
            effects=[effect("duotone", strength=0.95, shadowColor="#111111", highlightColor="#ff3b3b", contrast=0.6)])
    edge = t.track("shape", "Borde")
    t.solid(edge, "#111111", 0, 8.0, Box(0, 760, 1080, 240),
            layers=[gradient([(0, "#111111", 0.0), (1, "#111111", 1.0)], angle=90), no_stroke()])
    label_box = centered(540, 930, 820, 130)
    stamp = t.track("shape", "Sello")
    t.solid(stamp, "#FF3B3B", 0.3, 7.7, label_box, [(0, {"s": 2.0}, "snap"), (0.2, {})],
            rotation=keys([(0, -4)]), layers=[shadow("#000000", 0, 10, 0, 0.8), fill("#FF3B3B"), no_stroke()])
    words = t.track("text", "Sello")
    t.text(words, "OPINIÓN IMPOPULAR", 0.35, 7.65, label_box,
           text_style("Archivo Black", 66, [fill("#FFFFFF")], weight=400, spacing=2,
                      anim_in=tanim("glitch-in", duration=0.3)), label="Sello", rotation=keys([(0, -4)]))
    take = t.track("text", "Opinión")
    t.text(take, "La pizza con piña está buenísima", 1.0, 7.0, Box(70, 1060, 940, 420),
           text_style("Archivo Black", 96, [fill("#F5F5F5")], weight=400, align="left", line=1.02, case="upper",
                      anim_in=tanim("typewriter", duration=1.4, unit="character")), label="Opinión")
    ask = t.track("text", "Pregunta")
    t.text(ask, "¿Estás de acuerdo?", 4.4, 3.6, Box(70, 1520, 940, 80),
           text_style("Inter", 48, [fill("#AAAAAA")], weight=600, align="left",
                      anim_in=tanim("fade", duration=0.4)), label="Pregunta")
    pills = t.track("shape", "Botones")
    _pill(t, pills, "#F5F5F5", 4.8, 3.2, Box(70, 1640, 420, 130), _pop(0, 0.35))
    more = t.track("shape", "Botones")
    _pill(t, more, "#FF3B3B", 5.0, 3.0, Box(530, 1640, 420, 130), _pop(0, 0.35))
    yes = t.track("text", "Sí")
    t.text(yes, "SÍ", 4.9, 3.1, Box(70, 1640, 420, 130),
           text_style("Archivo Black", 66, [fill("#111111")], weight=400), label="Opción 1")
    t.text(t.track("text", "No"), "NO", 5.1, 2.9, Box(530, 1640, 420, 130),
           text_style("Archivo Black", 66, [fill("#FFFFFF")], weight=400), label="Opción 2")
    t.adjust([effect("rgb_split", animated={"amount": _spike([0.3], 26.0, 0.3)}),
              effect("stylize.film_grain", amount=0.2)], name="Golpe")
    t.song("experimental-test-subject", 0.0, 0.8)
    return t


# 20 ----------------------------------------------------------------------------------------------


def _flag(t: Template, colour: str, at: float, dur: float, cx: float, cy: float) -> None:
    """A waving flag: a pole and a cloth that sways about its own centre."""
    poles = t.track("shape", "Asta")
    land = [(0, {"s": 0.0}, "back"), (0.35, {})]
    t.solid(poles, "#FFFFFF", at, dur, Box(cx - 90, cy - 120, 14, 260), land, radius=7, kind="rounded-rectangle")
    cloths = t.track("shape", "Bandera")
    sway = []
    k = 0.0
    while k < dur:
        sway += [(k, -6, "smooth"), (k + 0.35, 6, "smooth")]
        k += 0.7
    t.solid(cloths, colour, at, dur, Box(cx - 76, cy - 120, 170, 120), land,
            layers=[stroke(5, "#FFFFFF"), fill(colour)], kind="banner", rotation=keys(sway))


def red_green_flags() -> Template:
    """Red and green alternate: each item takes the whole screen with its waving flag; your reaction stays."""
    t = Template("red-flags-green-flags", "Red flags y green flags", "Red flags, green flags", "text", 10.0,
                 order=1476, tags=["red flags", "green flags", "relaciones", "citas", "humor"], thumb_at=2.6,
                 background="#1A1A1A")
    t.solid(t.track("shape", "Fondo"), "#1A1A1A")
    items = [("red", "No contesta en tres días"), ("green", "Recuerda lo que le contaste"),
             ("red", "Revisa tu celular"), ("green", "Te presenta a sus amigos")]
    colours = {"red": "#E63946", "green": "#2A9D8F"}
    backs = t.track("shape", "Color")
    for i, (kind, _) in enumerate(items):
        at = 1.6 + i * 2.1
        dur = 2.1 if i < 3 else t.duration - at
        t.solid(backs, colours[kind], at, dur, FULL, [(0, {"sy": 0.0, "dy": 960 if i % 2 else -960}, "out"),
                                                      (0.3, {})])
    title = t.track("text", "Título")
    t.text(title, "Red flags", 0.1, 1.5, Box(40, 560, 1000, 220),
           text_style("Paytone One", 170, [shadow("#000000", 0, 10, 0, 0.8), fill("#E63946")], weight=400,
                      anim_in=tanim("slide-left", duration=0.35)), label="Título 1")
    t.text(t.track("text", "Título"), "vs green flags", 0.4, 1.2, Box(40, 790, 1000, 220),
           text_style("Paytone One", 130, [shadow("#000000", 0, 10, 0, 0.8), fill("#2A9D8F")], weight=400,
                      anim_in=tanim("slide-left", duration=0.35)), label="Título 2")
    for i, (kind, text) in enumerate(items):
        at = 1.6 + i * 2.1
        dur = 2.1 if i < 3 else t.duration - at
        _flag(t, "#B5121F" if kind == "red" else "#1B6F64", at + 0.15, dur - 0.15, 540, 470)
        tags = t.track("text", f"Tipo {i + 1}")
        t.text(tags, "RED FLAG" if kind == "red" else "GREEN FLAG", at + 0.2, dur - 0.2, Box(40, 650, 1000, 110),
               text_style("Paytone One", 76, [fill("#FFFFFF", 0.85)], weight=400, spacing=6,
                          anim_in=tanim("fade", duration=0.3)), editable=False)
        texts = t.track("text", f"Frase {i + 1}")
        t.text(texts, text, at + 0.25, dur - 0.25, Box(60, 790, 960, 420),
               text_style("Paytone One", 104, [shadow("#000000", 0, 8, 0, 0.35), fill("#FFFFFF")], weight=400,
                          line=1.02, anim_in=tanim("pop", duration=0.3, unit="word", stagger=0.07, ease="back")),
               label=f"{'Red' if kind == 'red' else 'Green'} flag {i // 2 + 1}")
    ring = t.track("shape", "Aro")
    t.solid(ring, "#FFFFFF", 1.6, 8.4, centered(540, 1560, 360, 360), _pop(0, 0.45), kind="ellipse")
    react = t.track("video", "Reacción")
    face = t.photo(react, "selfie-04", 1.6, 8.4, centered(540, 1560, 330, 330),
                   _pop(0, 0.45) + [(8.4, {"s": 1.04})], label="Tu reacción")
    t.mask(react, face, "ellipse")
    t.adjust([effect("beat_shake", animated={"amount": _spike([1.6 + i * 2.1 for i in range(4)], 0.6, 0.3)},
                     rotation=0.3)], name="Golpe")
    t.song("breaking-bollywood", 0.0, 0.85)
    return t


# 21 ----------------------------------------------------------------------------------------------


def portada_tutorial() -> Template:
    """A tutorial cover: a slanted pink block with the title, a «5 min» burst and level chips."""
    t = Template("portada-de-tutorial", "Portada de tutorial", "Tutorial cover", "intro", 6.0,
                 order=1480, tags=["tutorial", "paso a paso", "cómo hacer", "portada", "aprende"], thumb_at=3.8)
    video = t.track("video", "Video")
    t.photo(video, "creator-04", 0, 6.0, FULL, _kb(6.0, 1.04, 1.14, dy=-40), label="Tu video")
    block = t.track("shape", "Bloque")
    t.solid(block, "#FF5C8A", 0.3, 5.7, Box(-120, 1180, 1320, 560), [(0, {"dx": -1400}, "out"), (0.5, {})],
            rotation=keys([(0, -6)]), layers=[shadow("#5A0F2A", 0, 12, 0, 0.9), fill("#FF5C8A"), no_stroke()])
    kicker = t.track("text", "Antetítulo")
    t.text(kicker, "TUTORIAL", 0.6, 5.4, Box(60, 1150, 600, 120),
           text_style("Staatliches", 100, [fill("#FFE3EC")], weight=400, spacing=10, align="left",
                      anim_in=tanim("wipe", duration=0.4, angle=0)), label="Antetítulo", rotation=keys([(0, -6)]))
    title = t.track("text", "Título")
    t.text(title, "Maquillaje natural en 5 minutos", 0.8, 5.2, Box(60, 1280, 960, 340),
           text_style("Staatliches", 140, [shadow("#5A0F2A", 0, 6, 0, 0.9), fill("#FFFFFF")], weight=400,
                      align="left", line=0.92, anim_in=tanim("slide-up", duration=0.4, unit="word", stagger=0.08)),
           label="Título", rotation=keys([(0, -6)]))
    badge = t.track("shape", "Insignia")
    t.solid(badge, "#FFE14D", 1.3, 4.7, centered(850, 360, 300, 300), _pop(0, 0.5), kind="burst", points=12,
            innerRatio=0.84, layers=[shadow("#000000", 0, 8, 16, 0.35), fill("#FFE14D"), no_stroke()],
            rotation=keys([(0, -30, "out"), (0.6, 10), (4.7, 25)]))
    t.text(t.track("text", "Insignia"), "5 MIN", 1.4, 4.6, centered(850, 360, 300, 300),
           text_style("Staatliches", 92, [fill("#1A1A1A")], weight=400, anim_in=tanim("pop", duration=0.35)),
           label="Insignia", rotation=keys([(0, 10)]))
    chips = [("Nivel: fácil", 60, 1.6), ("Paso a paso", 400, 1.8)]
    for k, (content, x, at) in enumerate(chips):
        pill_track = t.track("shape", f"Chip {k + 1}")
        _pill(t, pill_track, "#1A1A1A", at, 6.0 - at, Box(x, 1700, 320, 90), _pop(0, 0.35), alpha=0.9)
        t.text(t.track("text", f"Chip {k + 1}"), content, at + 0.05, 5.95 - at, Box(x, 1700, 320, 90),
               text_style("Plus Jakarta Sans", 42, [fill("#FFFFFF")], weight=700), label=f"Chip {k + 1}")
    t.song("adding-the-sun", 0.0, 0.85)
    return t


TEMPLATES = [gancho_espera_al_final, pov_chat, pov_cine, storytime, tres_consejos, cita_minimalista,
             encuesta_cual_prefieres, ultimo_momento, podcast_subtitulos, entrevista_rotulo, intro_vlog,
             intro_podcast, cierre_parte_2, pantalla_final_videos, cuenta_regresiva_10, checklist_marcado,
             cosas_que_no_sabias, meme_clasico, opinion_impopular, red_green_flags, portada_tutorial]
