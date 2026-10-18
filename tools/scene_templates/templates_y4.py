"""YouTuber-style templates (0.15.0, part B of docs/plan-stock.md): Subtítulos palabra por palabra, Reacción,
Entrevista en la calle. Category youtuber; order 6200-6299; ids yt-sub-*, yt-reac-*, yt-calle-*.

1. Subtítulos que saltan (6200-6217): caption chunks over a video slot. Each chunk is one editable text whose
   accent rule is «karaoke»: the engine lights the word under the playhead, spreading the chunk's words over the
   clip's length by their letters (it cannot hear the voice), so the user edits the words and stretches or
   shortens the chunk to their speech. Words also pop in one by one (word unit, staggered over the chunk). Some
   styles give each word its own clip instead (one giant word at a time). Zoom punches sit under the captions.
2. Reacción (6218-6235): the reacted video big and the face cam (second slot) in a corner, side by side, or the
   face big with the video as a floating card; zoom-ins on the reaction moments, emoji bursts, «espera…».
3. Entrevista en la calle (6236-6253): a microphone drawn with shapes (its flag carries the channel name), the
   question on top, quick cuts between people (one slot each) with name and age tags.

Slots take photos or videos (labels say «video»). Visible text in Spanish, for the whole world; no creator names.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels, photo_bg,
                 pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, song, spike,
                 stroke, tall, tanim, text_style, vignette, wide)
from scene import argb

O = 6200
CAT = "youtuber"
B = 0.5  # one beat at 120 BPM

SUB = ["subtítulos", "captions", "palabra por palabra", "word by word"]
REAC = ["reacción", "reaction", "react"]
CALLE = ["entrevista en la calle", "street interview", "entrevista"]


def _t(maker, id, es, en, n, dur, tags, **kw):
    return maker(id, es, en, CAT, dur, order=O + n, tags=tags + ["youtuber"], **kw)


def _v(t, sample, t0, dur, box=None, motion=None, label="Tu video", track=None, name="Video", **kw):
    """A media slot that takes a photo or a video."""
    track = track or t.track("video", name)
    return t.photo(track, sample, t0, dur, box or t.full, motion, label=label, **kw)


def round_mask(t, clip, radius: float, n: int = 8):
    """Rounded corners on a slot (freeform mask, normalised to the clip box)."""
    # The resting size: a pop-in starts at scale 0, so take the largest key.
    box_w = max(k["value"] for k in clip["width"]["keyframes"])
    box_h = max(k["value"] for k in clip["height"]["keyframes"])
    rx, ry = radius / box_w, radius / box_h
    pts = []
    for cx, cy, a0 in ((1 - rx, ry, -90), (1 - rx, 1 - ry, 0), (rx, 1 - ry, 90), (rx, ry, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append([cx + rx * math.cos(a), cy + ry * math.sin(a)])
    track = next(tr for tr in t.tracks if clip in tr.clips)
    t.mask(track, clip, "freeform", points=pts, smooth=False)


def group(motion: list, ox: float, oy: float) -> list:
    """The same motion for a part whose centre is (ox, oy) from the group's centre: scaling about the group."""
    out = []
    for p in motion:
        m = dict(p[1])
        sx = m.get("sx", m.get("s", 1.0))
        sy = m.get("sy", m.get("s", 1.0))
        m["dx"] = m.get("dx", 0.0) + ox * (sx - 1)
        m["dy"] = m.get("dy", 0.0) + oy * (sy - 1)
        out.append((p[0], m) + tuple(p[2:]))
    return out


# --- captions ------------------------------------------------------------------------------------

def plan(chunks: list, start: float = 0.3, wps: float = 0.34, gap: float = 0.0) -> tuple[list, float]:
    """chunks: 'text' or ('text', seconds) -> [(text, t0, dur)], end."""
    out, at = [], start
    for c in chunks:
        text, d = c if isinstance(c, tuple) else (c, max(0.7, wps * len(c.split())))
        out.append((text, at, d))
        at += d + gap
    return out, at


# Loops on the lit word scale it about its centre without re-spacing the line: keep them small.
LOOPS = {"karaoke-pop": {"scale": 105}, "karaoke-bounce": {"lift": 0.06, "scale": 103}}


def late(chunks, k: int) -> float:
    """A thumbnail moment near the end of chunk k: its words are all in."""
    return round(chunks[k][1] + chunks[k][2] * 0.86, 2)


def kara(font, size, colour, accent=None, *, layers=None, scale=1.0, hl=None, hl_pad=6, hl_radius=10,
         case="upper", weight=900, inn="pop", loop=None, line=1.02, spacing=0.0, box=None, box_pad=18,
         box_radius=0, italic=False, align="center", valign="middle", out=None, inn_dur=0.22, ease="back", **inn_kw):
    """A caption style maker: f(stagger) -> textStyle with the karaoke accent and words popping in."""
    def make(stagger: float):
        s = text_style(font, size, layers or [fill(colour)], weight=weight, case=case, line=line, spacing=spacing,
                       italic=italic, align=align, valign=valign, box=box, box_pad=box_pad, box_radius=box_radius,
                       anim_in=tanim(inn, duration=inn_dur, unit="word", stagger=stagger, ease=ease, **inn_kw)
                       if inn else None,
                       anim_out=out, anim_loop=tanim(loop, **LOOPS.get(loop, {})) if loop else None)
        a = {"rule": "karaoke", "colorEnabled": accent is not None, "color": argb(accent or colour),
             "sizeScale": scale}
        if hl:
            a["highlight"] = {"enabled": True, "color": argb(hl), "padding": hl_pad, "radius": hl_radius}
        s["accent"] = a
        return s
    return make


def captions(t, chunks: list, box: Box, make, *, name="Subtítulo", track=None, motion_fn=None, **extra):
    """One editable text per chunk; the words pop in over the first ~85 % of the chunk."""
    track = track or t.track("text", "Subtítulos")
    clips = []
    for i, (text, t0, d) in enumerate(chunks):
        n = max(1, len(text.split()))
        stagger = min(0.32, d * 0.8 / n)
        clips.append(t.text(track, text, t0, d, box, make(stagger), motion_fn(i, d) if motion_fn else None,
                            label=f"{name} {i + 1}", **extra))
    return clips


def emoji(t, e, at, dur, cx, cy, size=170, *, motion=None, loop=None, track=None, fade=True):
    track = track or t.track("text", "Emoji")
    m = motion or [(0, {"s": 0.0}, "back"), (0.3, {})]
    return label(t, track, e, at, dur, centered(cx, cy, size * 1.5, size * 1.5), "Inter", size, "#000000", weight=400,
                 editable=False, motion=m, anim_loop=loop, anim_out=tanim("fade", duration=0.15) if fade else None,
                 name="Emoji")


def burst(t, emojis: list[str], at: float, cx: float, cy: float, spread: float = 260, size: int = 120, seed: int = 1,
          rise: float = 380, dur: float = 1.4):
    """A handful of emoji that pop out of one point and float up."""
    rng = random.Random(seed)
    track = t.track("text", "Emoji")
    for i, e in enumerate(emojis):
        a = -math.pi / 2 + (i - (len(emojis) - 1) / 2) * 0.55 + rng.uniform(-0.15, 0.15)
        dx, dy = math.cos(a) * spread, math.sin(a) * spread * 0.7
        d0 = at + i * 0.06
        if i and i % 3 == 0:
            track = t.track("text", "Emoji")
        label(t, track, e, d0, dur, centered(cx, cy, size * 1.5, size * 1.5), "Inter", size, "#000000", weight=400,
              editable=False, name="Emoji",
              motion=[(0, {"s": 0.2}, "out"), (0.35, {"dx": dx, "dy": dy, "s": 1.0}, "linear"),
                      (dur, {"dx": dx * 1.15, "dy": dy - rise, "s": 0.9})],
              opacity=keys([(0, 1.0, "hold"), (dur - 0.35, 1.0), (dur, 0.0)]))


def punch(t, times: list[float], peak: float = 0.35, fall: float = 0.25, name="Golpe"):
    return t.adjust([effect("zoom_pulse", animated={"punch": spike(times, peak, fall)})], name=name)


def shake(t, times: list[float], amount: float = 0.6, fall: float = 0.35):
    return t.adjust([effect("beat_shake", animated={"amount": spike(times, amount, fall)})], name="Sacudida")


def outlined(colour, width=10, ink="#000000", sh=0.85, dy=8):
    return [shadow(ink, 0, dy, 0, sh), stroke(width, ink), fill(colour)]


# 1 · Subtítulos que saltan ----------------------------------------------------------------------

def sub_amarillo():
    chunks, end = plan(["ESTO NADIE", "TE LO CUENTA", "PERO FUNCIONA", "EN SOLO", "TRES PASOS", "MIRA BIEN 👇"],
                       0.3, 0.42)
    t = _t(tall, "yt-sub-amarillo", "Subtítulos amarillos", "Yellow pop captions", 0, round(end + 0.6, 1),
           SUB + ["amarillo", "yellow"], thumb_at=late(chunks, 2), background="#000000")
    _v(t, "y4-calle-03", 0, t.duration, motion=kb(t.duration, 1.0, 1.1))
    shade_bottom(t, 900, 0.55)
    punch(t, [c[1] for c in chunks[1:]], 0.3, 0.22)
    captions(t, chunks, Box(60, 1150, 960, 330),
             kara("Montserrat", 104, "#FFFFFF", "#FFE600", layers=outlined("#FFFFFF", 9), scale=1.0,
                  loop="karaoke-pop"))
    emoji(t, "🤯", chunks[2][1] + 0.2, chunks[2][2] + 0.2, 820, 1030, 150,
          loop=tanim("swing", angle=10, speed=1.4))
    emoji(t, "🔥", chunks[4][1] + 0.1, chunks[4][2], 260, 1040, 140, loop=tanim("pulse", amount=8, speed=2))
    song(t, "upbeat", 0)
    return t


def sub_una_palabra():
    words = [("NO", 0.45), ("VAS", 0.4), ("A", 0.3), ("CREER", 0.7), ("LO", 0.35), ("QUE", 0.35), ("ME", 0.35),
             ("PASÓ", 0.8), ("HOY", 0.9)]
    chunks, end = plan(words, 0.4)
    t = _t(tall, "yt-sub-una-palabra", "Una palabra a la vez", "One word at a time", 1, round(end + 0.8, 1),
           SUB + ["una palabra", "one word", "cinético"], thumb_at=late(chunks, 3), background="#0A0A0A")
    _v(t, "y4-sorpresa-03", 0, t.duration, motion=kb(t.duration, 1.04, 1.14))
    shade_full(t, 0.25)
    punch(t, [c[1] for c in chunks if c[0] in ("CREER", "PASÓ", "HOY")], 0.45, 0.25)
    track = t.track("text", "Palabras")
    colours = {"CREER": "#FFE600", "PASÓ": "#3CFF8F", "HOY": "#FFE600"}
    for i, (w, t0, d) in enumerate(chunks):
        c = colours.get(w, "#FFFFFF")
        big = w in colours
        label(t, track, w, t0, d, Box(40, 1080, 1000, 420), "Anton", 250 if big else 190, c, weight=400,
              layers=outlined(c, 12, dy=12), anim_in=tanim("stamp", duration=0.18, **{"from": 190}),
              name=f"Palabra {i + 1}")
    emoji(t, "😱", chunks[7][1] + 0.05, end - chunks[7][1] + 0.7, 540, 880, 190,
          loop=tanim("jitter", amount=2, angle=6, speed=14))
    song(t, "electro", 0)
    return t


def sub_caja_verde():
    chunks, end = plan(["Te enseño el truco", "que uso cada día", "para editar", "el doble de rápido",
                        "y sin pagar nada"], 0.3, 0.38)
    t = _t(tall, "yt-sub-caja-verde", "Palabra resaltada en verde", "Green highlight captions", 2,
           round(end + 0.6, 1), SUB + ["resaltado", "highlight"], thumb_at=late(chunks, 3), background="#000000")
    _v(t, "y4-habla-06", 0, t.duration, motion=kb(t.duration, 1.0, 1.08))
    punch(t, [chunks[3][1], chunks[4][1]], 0.22, 0.2)
    captions(t, chunks, Box(70, 1230, 940, 260),
             kara("Inter", 86, "#FFFFFF", "#111111", layers=[shadow("#000000", 0, 4, 14, 0.8), fill("#FFFFFF")],
                  hl="#3CE07A", hl_pad=6, hl_radius=14, scale=1.0, case="none", weight=800, loop="karaoke-bounce",
                  inn="rise", ease="easeOut"))
    emoji(t, "⚡", chunks[3][1], chunks[3][2] + 0.2, 880, 1150, 120, loop=tanim("float", amount=0.3, speed=1.6))
    emoji(t, "💸", chunks[4][1] + 0.1, end - chunks[4][1] + 0.5, 200, 1150, 120,
          loop=tanim("swing", angle=8, speed=1.2))
    song(t, "upbeat", 2)
    return t


def sub_neon():
    chunks, end = plan(["ESTA CIUDAD", "NUNCA DUERME", "Y ESTA NOCHE", "TAMPOCO", "NOSOTROS ✨"], 0.4, 0.42)
    t = _t(tall, "yt-sub-neon", "Subtítulos neón", "Neon captions", 3, round(end + 0.7, 1),
           SUB + ["neón", "neon", "noche"], thumb_at=late(chunks, 1), background="#05010F")
    _v(t, "night-04", 0, t.duration, motion=kb(t.duration, 1.08, 1.0))
    t.adjust([effect("color.basic", exposure=-0.25, saturation=0.2, temperature=-0.2),
              effect("stylize.vignette", amount=0.7, softness=0.9)], name="Noche")
    punch(t, [c[1] for c in chunks[1:]], 0.25, 0.25)
    captions(t, chunks, Box(60, 1120, 960, 320),
             kara("Bebas Neue", 170, "#FFFFFF", "#3DF5FF", weight=400, spacing=4,
                  layers=[glow("#FF2BD6", 30, 0.95), stroke(3, "#FF2BD6"), fill("#FFFFFF")], scale=1.0,
                  loop="flicker", inn="flicker-in", inn_dur=0.25))
    label(t, t.track("text", "Marca"), "● EN VIVO", 0.2, t.duration - 0.2, Box(60, 150, 400, 80), "Bebas Neue", 64,
          "#FF2BD6", weight=400, align="left", layers=[glow("#FF2BD6", 18, 0.9), fill("#FFFFFF")],
          anim_loop=tanim("flicker", intensity=0.4, speed=3), name="Etiqueta")
    song(t, "electro", 2)
    return t


def sub_podcast_h():
    chunks, end = plan(["Lo que más me sorprendió", "fue que nadie", "se dio cuenta", "hasta que ya",
                        "era demasiado tarde"], 0.4, 0.4)
    t = _t(wide, "yt-sub-podcast-h", "Subtítulos de podcast 16:9", "Podcast captions 16:9", 4, round(end + 0.8, 1),
           SUB + ["podcast", "16:9"], thumb_at=late(chunks, 2), background="#0F0F14")
    _v(t, "h-podcast-02", 0, t.duration, motion=kb(t.duration, 1.0, 1.06))
    shade_bottom(t, 420, 0.7)
    captions(t, chunks, Box(260, 790, 1400, 200),
             kara("Poppins", 74, "#FFFFFF", "#FFFFFF", layers=[shadow("#000000", 0, 4, 12, 0.7), fill("#FFFFFF")],
                  hl="#7C3AED", hl_pad=6, hl_radius=12, scale=1.0, case="none", weight=800, inn="fade",
                  loop="karaoke-bounce"))
    pill(t, t.track("shape", "Episodio"), "#7C3AED", 0.3, t.duration - 0.3, Box(70, 60, 260, 70), slide_in(dx=-360))
    label(t, t.track("text", "Episodio"), "EP. 24", 0.3, t.duration - 0.3, Box(70, 60, 260, 70), "Poppins", 40,
          "#FFFFFF", weight=800, spacing=3, motion=slide_in(dx=-360), name="Episodio")
    label(t, t.track("text", "Invitado"), "con Laura Méndez", 0.5, t.duration - 0.5, Box(350, 60, 700, 70), "Poppins",
          40, "#FFFFFF", weight=600, align="left", layers=[shadow("#000000", 0, 2, 10, 0.8), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Invitado")
    song(t, "calm", 0, 0.5)
    return t


def sub_marcador():
    chunks, end = plan(["el día que", "lo dejé todo", "para viajar", "con una mochila", "y 200 dólares"], 0.4, 0.42)
    t = _t(tall, "yt-sub-marcador", "Subtítulos a mano", "Hand-drawn captions", 5, round(end + 0.7, 1),
           SUB + ["a mano", "handwritten", "storytime"], thumb_at=late(chunks, 1), background="#F3EBDD")
    _v(t, "travel-04", 0, t.duration, motion=kb(t.duration, 1.0, 1.1))
    shade_bottom(t, 800, 0.4)
    captions(t, chunks, Box(70, 1170, 940, 300),
             kara("Permanent Marker", 112, "#FFFFFF", "#FF5A4E", layers=[shadow("#000000", 6, 8, 0, 0.9),
                                                                          fill("#FFFFFF")],
                  case="lower", weight=400, scale=1.0, inn="pop", loop="karaoke-pop"),
             rotation=keys([(0, -4.0)]))
    t.solid(t.track("shape", "Subrayado"), "#FF5A4E", chunks[1][1] + 0.3, end - chunks[1][1] - 0.3,
            Box(260, 1480, 560, 16), [(0, {"sx": 0.0, "dx": -280}, "out"), (0.45, {})], radius=8,
            kind="rounded-rectangle", rotation=keys([(0, -4.0)]))
    emoji(t, "🎒", chunks[3][1] + 0.1, end - chunks[3][1] + 0.5, 860, 1050, 140,
          loop=tanim("swing", angle=12, speed=1.0))
    song(t, "world", 0)
    return t


def sub_burbuja():
    chunks, end = plan(["¿Sabías que", "puedes ahorrar", "la mitad", "solo cambiando", "este hábito? 🤔"], 0.4, 0.42)
    t = _t(tall, "yt-sub-burbuja", "Subtítulos en burbuja", "Bubble captions", 6, round(end + 0.7, 1),
           SUB + ["burbuja", "bubble", "chat"], thumb_at=late(chunks, 2), background="#1B1033")
    _v(t, "y4-calle-07", 0, t.duration, motion=kb(t.duration, 1.0, 1.08))
    punch(t, [chunks[2][1]], 0.3, 0.25)
    track = t.track("text", "Subtítulos")
    for i, (text, t0, d) in enumerate(chunks):
        left = i % 2 == 0
        box = Box(80 if left else 200, 1180 if left else 1210, 800, 220)
        n = len(text.split())
        st = kara("Poppins", 80, "#1B1033", "#8B5CF6", scale=1.0, case="none", weight=800, inn="fade",
                  box=("#FFFFFF", 1.0), box_pad=30, box_radius=48, loop=None)(min(0.25, d * 0.8 / n))
        t.text(track, text, t0, d, box, st, [(0, {"s": 0.6, "dy": 40}, "back"), (0.3, {})],
               label=f"Subtítulo {i + 1}")
    emoji(t, "💜", chunks[4][1] + 0.3, end - chunks[4][1], 900, 1110, 110, loop=tanim("pulse", amount=8, speed=2))
    song(t, "fun", 2)
    return t


def sub_storytime():
    chunks, end = plan([("nunca pensé que", 1.3), ("una carta olvidada", 1.4), ("cambiaría", 1.0),
                        ("el resto de mi vida", 1.6), ("y esta es la historia", 1.6)], 1.0)
    t = _t(tall, "yt-sub-storytime", "Storytime cinematográfico", "Cinematic storytime", 7, round(end + 0.9, 1),
           SUB + ["storytime", "historia", "cine"], thumb_at=late(chunks, 1), background="#000000")
    _v(t, "reading-02", 0, t.duration, motion=kb(t.duration, 1.12, 1.0))
    t.adjust([effect("cinematic_grade", strength=0.7), effect("stylize.film_grain", amount=0.25)], name="Cine")
    letterbox(t, 1.2)
    label(t, t.track("text", "Título"), "storytime", 0.2, t.duration - 0.2, Box(0, 120, 1080, 120), "DM Serif Display",
          80, "#F4C67A", weight=400, italic=True, anim_in=tanim("blur-in", duration=0.8), name="Título")
    captions(t, chunks, Box(80, 1470, 920, 220),
             kara("DM Serif Display", 82, "#FFFFFF", "#F4C67A", scale=1.0, case="lower", weight=400, italic=True,
                  inn="fade-up-char", ease="easeOut", inn_dur=0.45,
                  layers=[shadow("#000000", 0, 4, 18, 0.8), fill("#FFFFFF")]))
    song(t, "cine", 2, 0.75)
    return t


def sub_gancho():
    chunks, end = plan(["COMPRÉ EL", "PRODUCTO MÁS", "BARATO DE", "INTERNET", "Y PASÓ ESTO"], 1.3, 0.4)
    t = _t(tall, "yt-sub-gancho", "Gancho y subtítulos", "Hook and captions", 8, round(end + 0.8, 1),
           SUB + ["gancho", "hook", "espera"], thumb_at=late(chunks, 3), background="#000000")
    _v(t, "box-02", 0, t.duration, motion=[(0, {"s": 1.25}, "snap"), (0.4, {"s": 1.05}, "linear"),
                                           (t.duration, {"s": 1.12})])
    punch(t, [c[1] for c in chunks], 0.25, 0.2)
    pill(t, t.track("shape", "Gancho"), "#FFFFFF", 0.0, t.duration, Box(130, 170, 820, 130), pop(0, 0.35))
    label(t, t.track("text", "Gancho"), "ESPERA AL FINAL 😳", 0.0, t.duration, Box(130, 170, 820, 130), "Luckiest Guy",
          66, "#111111", weight=400, anim_loop=tanim("pulse", amount=4, speed=1.4), name="Gancho")
    captions(t, chunks, Box(50, 1100, 980, 330),
             kara("Luckiest Guy", 120, "#FFFFFF", "#39FF14", layers=outlined("#FFFFFF", 10), scale=1.0, weight=400,
                  loop="karaoke-pop", inn="bounce", ease="easeOut"))
    rrect(t, t.track("shape", "Barra"), "#FFFFFF", 0, t.duration, Box(0, 1900, 1080, 20), 0, alpha=0.25)
    t.solid(t.track("shape", "Barra"), "#39FF14", 0, t.duration, Box(0, 1900, 1080, 20),
            [(0, {"sx": 0.0, "dx": -540}, "linear"), (t.duration, {})])
    burst(t, ["😳", "🤑", "📦"], chunks[4][1] + 0.2, 540, 1000, seed=8)
    song(t, "upbeat", 3)
    return t


def sub_dividida():
    chunks, end = plan(["Así quedó", "el cuarto", "después de", "una semana", "de trabajo 💪"], 0.4, 0.5)
    t = _t(tall, "yt-sub-pantalla-dividida", "Subtítulos en pantalla dividida", "Split screen captions", 9,
           round(end + 0.6, 1), SUB + ["pantalla dividida", "split screen"], thumb_at=late(chunks, 2),
           background="#111111")
    _v(t, "creator-02", 0, t.duration, Box(0, 0, 1080, 950), kb(t.duration, 1.0, 1.08), label="Tu video (arriba)")
    tr = t.track("video", "Video de apoyo")
    half = t.duration / 2
    a = _v(t, "interior-03", 0, half + 0.3, Box(0, 970, 1080, 950), kb(half + 0.3, 1.0, 1.1),
           label="Video de apoyo 1", track=tr)
    b = _v(t, "interior-06", half, t.duration - half, Box(0, 970, 1080, 950), kb(t.duration - half, 1.1, 1.0),
           label="Video de apoyo 2", track=tr)
    t.transition(tr, a, b, "slide_left", 0.3)
    t.solid(t.track("shape", "Divisor"), "#FFD400", 0, t.duration, Box(0, 950, 1080, 20))
    captions(t, chunks, Box(90, 885, 900, 150),
             kara("Archivo Black", 72, "#111111", "#E11D48", scale=1.0, weight=400, box=("#FFD400", 1.0), box_pad=22,
                  box_radius=14, inn="pop"))
    song(t, "upbeat", 4)
    return t


def sub_rojo():
    chunks, end = plan(["SI QUIERES", "MÁS CLIENTES", "DEJA DE HACER", "ESTO", "Y EMPIEZA", "HOY MISMO"], 0.3, 0.4)
    t = _t(tall, "yt-sub-rojo", "Palabra clave en rojo", "Red keyword captions", 10, round(end + 0.6, 1),
           SUB + ["negocios", "business", "palabra clave"], thumb_at=late(chunks, 3), background="#0B0B0B")
    _v(t, "man-03", 0, t.duration, motion=kb(t.duration, 1.0, 1.1))
    shade_full(t, 0.15)
    # The keyword slams in huge behind the captions.
    label(t, t.track("text", "Palabra clave"), "ESTO", chunks[3][1], chunks[3][2] + 0.3, Box(0, 560, 1080, 520),
          "Anton", 420, "#E11D48", weight=400, editable=True, layers=[shadow("#000000", 0, 14, 30, 0.6), fill("#E11D48")],
          anim_in=tanim("stamp", duration=0.2, **{"from": 260}), anim_out=tanim("fade", duration=0.15),
          name="Palabra clave")
    punch(t, [chunks[1][1], chunks[3][1], chunks[5][1]], 0.4, 0.22)
    shake(t, [chunks[3][1]], 0.5, 0.3)
    captions(t, chunks, Box(60, 1160, 960, 300),
             kara("Archivo Black", 96, "#FFFFFF", "#FFFFFF", layers=outlined("#FFFFFF", 6, dy=6), hl="#E11D48",
                  hl_pad=6, hl_radius=6, scale=1.0, weight=400, inn="drop", ease="easeOut"))
    song(t, "epic", 1)
    return t


def sub_gradiente():
    chunks, end = plan(["3 IDEAS", "PARA TU", "PRÓXIMO", "VIDEO", "QUE SÍ", "FUNCIONAN"], 0.3, 0.42)
    t = _t(tall, "yt-sub-gradiente", "Subtítulos degradados", "Gradient captions", 11, round(end + 0.6, 1),
           SUB + ["degradado", "gradient", "ideas"], thumb_at=late(chunks, 2), background="#14051F")
    _v(t, "y4-habla-05", 0, t.duration, motion=kb(t.duration, 1.0, 1.08))
    shade_bottom(t, 900, 0.5, colour="#14051F")
    punch(t, [chunks[2][1], chunks[4][1]], 0.25, 0.22)
    grad = {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "gradient", "color": argb("#FF8A00"),
                      "gradient": {"kind": "linear", "angle": 0, "space": "block",
                                   "stops": [{"pos": 0, "color": argb("#FFB800")}, {"pos": 0.5, "color": argb("#FF4D6D")},
                                             {"pos": 1, "color": argb("#B14DFF")}]}}}
    captions(t, chunks, Box(60, 1150, 960, 320),
             kara("Kanit", 132, "#FFFFFF", "#FFFFFF", layers=[shadow("#000000", 0, 8, 0, 0.7), grad], scale=1.0,
                  italic=True, weight=900, loop="karaoke-pop", inn="zoom-in"))
    emoji(t, "💡", chunks[0][1] + 0.3, chunks[0][2] + chunks[1][2], 870, 1040, 140,
          loop=tanim("float", amount=0.3, speed=1.5))
    song(t, "upbeat", 5)
    return t


def sub_caja_blanca():
    chunks, end = plan([("POV: por fin aprendes", 1.6), ("a cocinar algo", 1.2), ("que no sea", 0.9),
                        ("arroz con huevo 🍳", 1.6)], 0.4)
    t = _t(tall, "yt-sub-caja-blanca", "Subtítulo en caja blanca", "White box captions", 12, round(end + 0.8, 1),
           SUB + ["caja blanca", "white box", "pov"], thumb_at=late(chunks, 1), background="#FFFFFF")
    _v(t, "cooking-02", 0, t.duration, motion=kb(t.duration, 1.0, 1.08))
    captions(t, chunks, Box(110, 300, 860, 260),
             kara("Montserrat", 66, "#111111", "#E8442E", scale=1.0, case="none", weight=700, inn="fade",
                  box=("#FFFFFF", 1.0), box_pad=22, box_radius=16, line=1.2),
             motion_fn=lambda i, d: [(0, {"s": 0.85}, "back"), (0.25, {})])
    song(t, "fun", 3)
    return t


def sub_pasos():
    steps = [("PASO 1", ["Corta la tela", "en dos partes"]), ("PASO 2", ["Cose los bordes", "por dentro"]),
             ("PASO 3", ["Dale la vuelta", "¡y listo! ✂️"])]
    each = 3.0
    t = _t(tall, "yt-sub-pasos", "Subtítulos por pasos", "Step-by-step captions", 13, 9.4,
           SUB + ["tutorial", "pasos", "steps"], thumb_at=3.9, background="#FFF6E9")
    tr = t.track("video", "Pasos")
    prev = None
    samples = ["handmade-01", "handmade-02", "handmade-03"]
    for i, (s, _) in enumerate(steps):
        at = 0.2 + i * each
        d = each + (0.3 if i < 2 else t.duration - at - each)
        clip = _v(t, samples[i], at, d, motion=kb(d, 1.0, 1.08), label=f"Video del paso {i + 1}", track=tr)
        if prev:
            t.transition(tr, prev, clip, "push_left", 0.3)
        prev = clip
    shade_bottom(t, 700, 0.5)
    for i, (s, chunk) in enumerate(steps):
        at = 0.3 + i * each
        pill(t, t.track("shape", "Paso"), "#FF7A00", at, each - 0.2, Box(60, 160, 330, 110), pop(0, 0.35))
        label(t, t.track("text", "Paso"), s, at, each - 0.2, Box(60, 160, 330, 110), "Fredoka", 62, "#FFFFFF",
              weight=700, motion=pop(0, 0.35), name=f"Paso {i + 1}")
        sub, _ = plan([(chunk[0], 1.3), (chunk[1], each - 1.5)], at + 0.2)
        captions(t, sub, Box(70, 1250, 940, 240),
                 kara("Fredoka", 92, "#FFFFFF", "#FFB21A", layers=outlined("#FFFFFF", 7, "#3A2000", dy=6), scale=1.0,
                      weight=700, case="none", loop="karaoke-bounce"),
                 name=f"Paso {i + 1} · subtítulo")
    punch(t, [0.3 + each, 0.3 + 2 * each], 0.25, 0.2)
    song(t, "fun", 4)
    return t


def sub_tutorial_h():
    chunks, end = plan(["Primero abre", "el menú de ajustes", "busca la opción", "que dice «avanzado»",
                        "y actívala ✅"], 0.4, 0.4)
    t = _t(wide, "yt-sub-tutorial-h", "Subtítulos de tutorial 16:9", "Tutorial captions 16:9", 14, round(end + 0.8, 1),
           SUB + ["tutorial", "16:9"], thumb_at=late(chunks, 3), background="#0B1220")
    _v(t, "h-desk-02", 0, t.duration, motion=kb(t.duration, 1.0, 1.12, dx=-80))
    punch(t, [chunks[2][1], chunks[4][1]], 0.2, 0.2)
    captions(t, chunks, Box(210, 820, 1500, 170),
             kara("Sora", 76, "#FFFFFF", "#FFD60A", scale=1.0, case="none", weight=700, inn="fade",
                  box=("#0B1220", 0.85), box_pad=24, box_radius=18))
    pill(t, t.track("shape", "Tecla"), "#FFD60A", 0.4, t.duration - 0.4, Box(70, 60, 300, 76), slide_in(dy=-160))
    label(t, t.track("text", "Tecla"), "TUTORIAL", 0.4, t.duration - 0.4, Box(70, 60, 300, 76), "Sora", 40, "#0B1220",
          weight=800, spacing=4, motion=slide_in(dy=-160), name="Etiqueta")
    emoji(t, "👉", chunks[2][1] + 0.1, chunks[2][2] + chunks[3][2], 1600, 480, 200,
          loop=tanim("sway", angle=6, speed=1.5))
    song(t, "calm", 4, 0.55)
    return t


def sub_retro():
    chunks, end = plan(["VERANO", "DE 1998", "LA CÁMARA", "DE MI PAPÁ", "Y MUCHO", "RUIDO"], 0.6, 0.5)
    t = _t(tall, "yt-sub-retro", "Subtítulos retro VHS", "Retro VHS captions", 15, round(end + 0.7, 1),
           SUB + ["retro", "vhs", "nostalgia"], thumb_at=late(chunks, 1), background="#000000")
    _v(t, "summer-02", 0, t.duration, motion=kb(t.duration, 1.0, 1.06))
    t.adjust([effect("stylize.vhs", noise=30, chroma=4), effect("color.basic", fade=0.25, saturation=-0.1)], name="VHS")
    label(t, t.track("text", "REC"), "● REC", 0, t.duration, Box(70, 110, 300, 90), "VT323", 84, "#FF3030", weight=400,
          align="left", editable=False, opacity=blink(t.duration, 1.0, 0.0))
    label(t, t.track("text", "Fecha"), "JUL 14 1998", 0, t.duration, Box(560, 1650, 460, 90), "VT323", 76, "#FFFFFF",
          weight=400, align="right", layers=[shadow("#000000", 3, 3, 0, 0.9), fill("#FFFFFF")], name="Fecha")
    captions(t, chunks, Box(60, 1150, 960, 260),
             kara("VT323", 150, "#FFE14D", "#FFFFFF", layers=[shadow("#000000", 5, 5, 0, 1.0), fill("#FFE14D")],
                  scale=1.0, weight=400, inn="typewriter", ease="linear", inn_dur=0.1))
    song(t, "jazz", 1, 0.7)
    return t


def sub_emoji():
    rows = [("me levanté", "😴"), ("hice ejercicio", "🏃‍♀️"), ("comí sano", "🥗"), ("y luego...", "🤔"),
            ("pizza 🍕", "😋")]
    chunks, end = plan([r[0] for r in rows], 0.3, 0.5)
    t = _t(tall, "yt-sub-emoji", "Subtítulos con emoji", "Emoji captions", 16, round(end + 0.7, 1),
           SUB + ["emoji", "divertido", "fun"], thumb_at=late(chunks, 2), background="#FFE3EE")
    _v(t, "selfie-02", 0, t.duration, motion=kb(t.duration, 1.0, 1.08))
    punch(t, [chunks[4][1]], 0.4, 0.25)
    captions(t, chunks, Box(70, 1270, 940, 220),
             kara("Fredoka", 104, "#FFFFFF", "#FF4F9A", layers=outlined("#FFFFFF", 8, "#5A1036", dy=6), scale=1.0,
                  weight=700, case="none", loop="karaoke-bounce", inn="bounce", ease="easeOut"))
    track = t.track("text", "Emoji")
    for i, (text, t0, d) in enumerate(chunks):
        emoji(t, rows[i][1], t0 + 0.1, d - 0.1, 540, 1110, 170, track=track,
              motion=[(0, {"s": 0.0, "dy": 60}, "back"), (0.35, {})], loop=tanim("swing", angle=8, speed=1.3))
    song(t, "fun", 0)
    return t


def sub_comic_h():
    chunks, end = plan(["¡LLEGAMOS", "A LA CIMA!", "TRES HORAS", "SUBIENDO", "Y VALIÓ", "LA PENA"], 0.4, 0.45)
    t = _t(wide, "yt-sub-comic-h", "Subtítulos de cómic 16:9", "Comic captions 16:9", 17, round(end + 0.7, 1),
           SUB + ["cómic", "comic", "vlog", "16:9"], thumb_at=late(chunks, 1), background="#111111")
    _v(t, "h-travel-03", 0, t.duration, motion=kb(t.duration, 1.0, 1.1))
    punch(t, [chunks[0][1], chunks[4][1]], 0.35, 0.25)
    tr = t.track("shape", "Estallido")
    for (at, cx, cy, c) in [(chunks[0][1], 1560, 260, "#FFE600"), (chunks[4][1], 340, 240, "#FF4D4D")]:
        s = t.solid(tr, c, at, 1.3, centered(cx, cy, 380, 300), [(0, {"s": 0.0}, "back"), (0.3, {}, "linear"),
                                                                  (1.3, {"s": 1.05})], kind="burst",
                    layers=[shadow("#000000", 8, 10, 0, 1.0), fill(c), stroke(6, "#000000")])
        s["shapeStyle"].update(points=14, innerRatio=0.72)
    for (at, cx, cy, w) in [(chunks[0][1], 1560, 260, "¡WOW!"), (chunks[4][1], 340, 240, "¡SÍ!")]:
        label(t, t.track("text", "Onomatopeya"), w, at, 1.3, centered(cx, cy, 380, 300), "Bangers", 96, "#111111",
              weight=400, motion=[(0, {"s": 0.0}, "back"), (0.3, {}, "linear"), (1.3, {"s": 1.05})],
              rotation=keys([(0, -8.0)]), name="Onomatopeya")
    captions(t, chunks, Box(260, 800, 1400, 220),
             kara("Bangers", 130, "#FFE600", "#FFFFFF", layers=outlined("#FFE600", 9, dy=9), scale=1.0, weight=400,
                  spacing=3, loop="karaoke-pop"))
    song(t, "epic", 3)
    return t


SUBS = [sub_amarillo, sub_una_palabra, sub_caja_verde, sub_neon, sub_podcast_h, sub_marcador, sub_burbuja,
        sub_storytime, sub_gancho, sub_dividida, sub_rojo, sub_gradiente, sub_caja_blanca, sub_pasos, sub_tutorial_h,
        sub_retro, sub_emoji, sub_comic_h]


# 2 · Reacción --------------------------------------------------------------------------------------

def facecam(t, sample, t0, dur, box: Box, motion=None, *, border="#FFFFFF", width=10, radius=36,
            label="Tu cara (cámara)", shadow_alpha=0.45):
    """The face cam: a rounded frame with a soft shadow and the slot inside, rounded too."""
    fb = Box(box.x - width, box.y - width, box.w + 2 * width, box.h + 2 * width)
    t.solid(t.track("shape", "Marco cámara"), border, t0, dur, fb, motion, radius=radius + width,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 14, 34, shadow_alpha), fill(border), no_stroke()])
    clip = _v(t, sample, t0, dur, box, motion, label=label, name="Cámara")
    round_mask(t, clip, radius)
    return clip


def chip(t, text, t0, dur, box: Box, colour, ink, font="Montserrat", size=44, *, motion=None, name="Etiqueta",
         weight=800, spacing=2, loop=None, editable=True):
    pill(t, t.track("shape", name), colour, t0, dur, box, motion)
    return label(t, t.track("text", name), text, t0, dur, box, font, size, ink, weight=weight, spacing=spacing,
                 motion=motion, anim_loop=loop, name=name, editable=editable)


def reac_esquina_h():
    t = _t(wide, "yt-reac-esquina-h", "Reacción con cámara en la esquina", "Corner face cam reaction", 18, 10.0,
           REAC + ["cámara en la esquina", "face cam", "16:9"], thumb_at=4.6, background="#000000")
    _v(t, "y4b-h-dance-05", 0, 10.0, motion=[(0, {"s": 1.0}, "linear"), (4.0, {"s": 1.04}, "snap"),
                                            (4.3, {"s": 1.25}, "linear"), (6.0, {"s": 1.28}, "inout"),
                                            (6.6, {"s": 1.05}, "linear"), (10.0, {"s": 1.08})],
       label="Video que comentas")
    fm = [(0, {"s": 0.0}, "back"), (0.5, {}, "hold"), (4.0, {}, "snap"), (4.3, {"s": 1.35, "dx": -95, "dy": -70},
                                                                         "hold"),
          (6.0, {"s": 1.35, "dx": -95, "dy": -70}, "inout"), (6.6, {})]
    facecam(t, "y4-sorpresa-h-02", 0.3, 9.7, Box(1360, 650, 480, 340), fm, border="#FFD400")
    chip(t, "● REACCIONANDO", 0.3, 9.7, Box(60, 50, 430, 72), "#E11D48", "#FFFFFF", size=36,
         motion=slide_in(dx=-500), loop=None)
    burst(t, ["😱", "🔥", "😂", "🤯"], 4.1, 1600, 650, spread=300, size=110, seed=18)
    label(t, t.track("text", "Texto"), "¡NO PUEDE SER!", 4.0, 2.2, Box(360, 420, 1200, 240), "Anton", 150, "#FFFFFF",
          weight=400, layers=outlined("#FFFFFF", 10), anim_in=tanim("stamp", duration=0.2),
          anim_out=tanim("fade", duration=0.2), name="Reacción")
    song(t, "upbeat", 1, 0.7)
    return t


def reac_arriba_abajo():
    t = _t(tall, "yt-reac-arriba-abajo", "Reacción arriba y abajo", "Top and bottom reaction", 19, 10.0,
           REAC + ["pantalla dividida", "split screen"], thumb_at=3.9, background="#000000")
    _v(t, "y4-viral-03", 0, 10.0, Box(0, 0, 1080, 1060), kb(10.0, 1.0, 1.08), label="Video que comentas")
    _v(t, "y4-sorpresa-06", 0, 10.0, Box(0, 1060, 1080, 860),
       [(0, {}, "hold"), (3.5, {}, "snap"), (3.7, {"s": 1.3}, "linear"), (5.0, {"s": 1.32}, "inout"),
        (5.4, {}, "hold"), (7.5, {}, "snap"), (7.7, {"s": 1.3}, "linear"), (10.0, {"s": 1.35})],
       label="Tu cara (cámara)", name="Cámara")
    t.solid(t.track("shape", "Banda"), "#111111", 0, 10.0, Box(0, 1010, 1080, 100))
    label(t, t.track("text", "Banda"), "😂 ESPERA A VER SU CARA", 0.2, 9.8, Box(0, 1010, 1080, 100), "Archivo Black",
          52, "#FFFFFF", weight=400, anim_in=tanim("wipe", duration=0.5), name="Texto")
    burst(t, ["😂", "😂", "💀"], 3.55, 960, 1760, seed=19, size=130)
    burst(t, ["🔥", "😱", "🔥"], 7.55, 130, 1760, seed=20, size=130)
    song(t, "fun", 1)
    return t


def reac_espera():
    t = _t(tall, "yt-reac-espera", "Espera… reacción", "Wait for it reaction", 20, 10.0,
           REAC + ["espera", "wait for it", "cuenta regresiva"], thumb_at=4.0, background="#000000")
    _v(t, "y4-viral-05", 0, 10.0, motion=[(0, {"s": 1.0}, "linear"), (3.2, {"s": 1.04}, "snap"),
                                          (3.45, {"s": 1.35}, "linear"), (10.0, {"s": 1.42})],
       label="Video que comentas")
    shade_top(t, 520, 0.6, 0, 3.2)
    facecam(t, "y4-sorpresa-02", 0.3, 9.7, Box(640, 170, 360, 360),
            [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (3.2, {}, "snap"),
             (3.45, {"s": 1.6, "dx": -120, "dy": 160}, "linear"), (9.7, {"s": 1.65, "dx": -120, "dy": 160})],
            border="#FFFFFF", radius=40)
    label(t, t.track("text", "Espera"), "ESPERA…", 0.2, 3.0, Box(60, 700, 960, 220), "Luckiest Guy", 150, "#FFFFFF",
          weight=400, layers=outlined("#FFFFFF", 10), anim_in=tanim("pop", duration=0.3),
          anim_loop=tanim("pulse", amount=6, speed=1.5), name="Espera")
    track = t.track("text", "Cuenta")
    for i, n in enumerate("321"):
        label(t, track, n, 0.9 + i * 0.75, 0.7, Box(340, 940, 400, 400), "Luckiest Guy", 320, "#FFE600", weight=400,
              editable=False, layers=outlined("#FFE600", 12, dy=12), anim_in=tanim("stamp", duration=0.18))
    flash(t, 3.2, 0.35)
    shake(t, [3.25, 4.2], 0.55, 0.35)
    label(t, t.track("text", "Reacción"), "¡¿QUÉ?!", 3.3, 6.7, Box(40, 1300, 1000, 300), "Luckiest Guy", 210,
          "#FFE600", weight=400, layers=outlined("#FFE600", 12, dy=12), anim_in=tanim("stamp", duration=0.2),
          rotation=keys([(0, -6.0)]), name="Reacción")
    burst(t, ["😱", "🤯", "😱", "🔥", "😳"], 3.3, 540, 1300, spread=380, size=130, seed=21)
    song(t, "suspense", 0)
    return t


def reac_dividida_h():
    t = _t(wide, "yt-reac-dividida-h", "Reacción lado a lado", "Side by side reaction", 21, 9.0,
           REAC + ["lado a lado", "side by side", "16:9"], thumb_at=3.9, background="#0D0D0D")
    _v(t, "y4b-h-parkour-02", 0, 9.0, Box(0, 0, 950, 1080), kb(9.0, 1.0, 1.1), label="Video que comentas")
    _v(t, "y4-sorpresa-h-02", 0, 9.0, Box(970, 0, 950, 1080),
       [(0, {}, "hold"), (3.5, {}, "snap"), (3.7, {"s": 1.18}, "linear"), (6.0, {"s": 1.2}, "inout"),
        (6.5, {}, "linear"), (9.0, {"s": 1.04})], label="Tu cara (cámara)", name="Cámara")
    t.solid(t.track("shape", "Divisor"), "#FFD400", 0, 9.0, Box(950, 0, 20, 1080),
            [(0, {"sy": 0.0}, "out"), (0.5, {})])
    chip(t, "EL VIDEO", 0.4, 8.6, Box(60, 960, 300, 70), "#FFFFFF", "#111111", size=36, motion=slide_in(dy=150))
    chip(t, "YO", 0.5, 8.5, Box(1030, 960, 160, 70), "#FFD400", "#111111", size=36, motion=slide_in(dy=150))
    burst(t, ["😳", "😂", "😂"], 3.6, 1450, 600, seed=22)
    label(t, t.track("text", "Texto"), "¿EN SERIO? 😂", 3.6, 2.6, Box(1000, 120, 900, 180), "Archivo Black", 96,
          "#FFFFFF", weight=400, layers=outlined("#FFFFFF", 7, dy=7), anim_in=tanim("pop", duration=0.25),
          anim_out=tanim("fade", duration=0.2), name="Reacción")
    song(t, "fun", 2)
    return t


def reac_tarjeta():
    t = _t(tall, "yt-reac-tarjeta", "Reacción con el video flotando", "Floating card reaction", 22, 10.0,
           REAC + ["comentario", "commentary"], thumb_at=5.4, background="#101828")
    bg_gradient(t, [(0, "#2B1055"), (1, "#7597DE")], angle=90)
    _v(t, "y4-calle-04", 0, 10.0, Box(0, 820, 1080, 1100), kb(10.0, 1.0, 1.05), label="Tu cara (cámara)",
       name="Cámara")
    shade_top(t, 1100, 0.0)
    card = Box(110, 200, 860, 600)
    cm = [(0, {"s": 0.5, "dy": -300}, "back"), (0.6, {}, "hold"), (5.0, {}, "snap"),
          (5.3, {"s": 1.12, "dy": 40}, "linear"), (10.0, {"s": 1.14, "dy": 40})]
    t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", 0.2, 9.8, Box(card.x - 14, card.y - 14, card.w + 28, card.h + 28),
            cm, radius=34, kind="rounded-rectangle", layers=[shadow("#000000", 0, 24, 50, 0.55), fill("#FFFFFF"),
                                                            no_stroke()], rotation=keys([(0, -3.0)]))
    c = _v(t, "y4-viral-06", 0.2, 9.8, card, cm, label="Video que comentas", name="Tarjeta",
           rotation=keys([(0, -3.0)]))
    round_mask(t, c, 24)
    chip(t, "¿VISTE ESTO? 👀", 0.6, 9.4, Box(250, 860, 580, 96), "#FFE600", "#111111", "Archivo Black", 46,
         motion=pop(0, 0.4))
    burst(t, ["🤯", "👏", "🔥"], 5.1, 540, 760, seed=23)
    song(t, "upbeat", 3)
    return t


def reac_zoom_cara():
    t = _t(tall, "yt-reac-zoom-cara", "Zoom a mi cara", "Face zoom reaction", 23, 9.0,
           REAC + ["zoom", "cara", "face"], thumb_at=4.6, background="#000000")
    _v(t, "y4-viral-03", 0, 9.0, motion=kb(9.0, 1.0, 1.1), label="Video que comentas")
    fm = [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (4.0, {}, "snap"),
          (4.25, {"s": 2.9, "dx": 380, "dy": -500}, "linear"), (6.0, {"s": 3.0, "dx": 380, "dy": -500}, "inout"),
          (6.5, {})]
    circle_photo(t, "y4-sorpresa-07", 0.3, 8.7, centered(200, 1520, 340, 340), fm, ring_colour="#FFFFFF",
                 ring_width=10, label="Tu cara (cámara)")
    label(t, t.track("text", "Texto"), "mi cara cuando 👇", 0.4, 3.5, Box(60, 1220, 960, 120), "Poppins", 70,
          "#FFFFFF", weight=800, layers=[shadow("#000000", 0, 4, 16, 0.85), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Texto")
    t.adjust([effect("strobe_flash", animated={"flash": spike([4.0], 0.8, 0.3)}, tint=0.1)], name="Destello")
    shake(t, [4.05], 0.7, 0.5)
    emoji(t, "😱", 4.2, 1.9, 540, 1500, 260, loop=tanim("jitter", amount=2, angle=8, speed=14))
    song(t, "suspense", 3)
    return t


def reac_comentarios():
    comments = [("@marta.viaja", "¿Eso es real? 😳", "#F97316"), ("@leo_92", "Haz la parte 2 por favor", "#22C55E"),
                ("@sofi.art", "Me reí demasiado 😂", "#8B5CF6")]
    t = _t(tall, "yt-reac-comentarios", "Respondo sus comentarios", "Reacting to comments", 24, 10.0,
           REAC + ["comentarios", "comments"], thumb_at=4.6, background="#000000")
    _v(t, "y4-habla-06", 0, 10.0, motion=kb(10.0, 1.0, 1.08), label="Tu video")
    shade_top(t, 700, 0.55)
    chip(t, "RESPONDIENDO A…", 0.2, 9.8, Box(60, 150, 520, 80), "#FFFFFF", "#111111", size=38,
         motion=slide_in(dx=-600))
    for i, (user, text, c) in enumerate(comments):
        at = 0.6 + i * 3.1
        d = 3.0 if i < 2 else 10.0 - at
        cm = [(0, {"s": 0.6, "dy": -60}, "back"), (0.35, {})]
        card = Box(60, 270, 960, 230)
        group_c = (card.cx, card.cy)
        rrect(t, t.track("shape", "Comentario"), "#FFFFFF", at, d, card, 34, cm,
              layers=[shadow("#000000", 0, 14, 30, 0.4), fill("#FFFFFF"), no_stroke()])
        av = centered(150, 385, 120, 120)
        t.solid(t.track("shape", "Avatar"), c, at, d, av, group(cm, av.cx - group_c[0], av.cy - group_c[1]),
                kind="ellipse")
        ub = Box(240, 300, 740, 70)
        label(t, t.track("text", "Usuario"), user, at, d, ub, "Montserrat", 38, "#6B7280", weight=700, align="left",
              motion=group(cm, ub.cx - group_c[0], ub.cy - group_c[1]), name=f"Usuario {i + 1}")
        cb = Box(240, 365, 760, 110)
        label(t, t.track("text", "Comentario"), text, at, d, cb, "Montserrat", 54, "#111111", weight=800, align="left",
              motion=group(cm, cb.cx - group_c[0], cb.cy - group_c[1]), name=f"Comentario {i + 1}")
        emoji(t, ["😅", "✌️", "🥹"][i], at + 0.9, d - 0.9, 900, 1250, 170, loop=tanim("swing", angle=10, speed=1.2))
    song(t, "upbeat", 6)
    return t


def reac_ventana_h():
    t = _t(wide, "yt-reac-ventana-h", "Reacción en ventana", "Window reaction 16:9", 25, 10.0,
           REAC + ["ventana", "window", "16:9"], thumb_at=4.4, background="#0E1116")
    bg_gradient(t, [(0, "#0E1116"), (1, "#1D2433")], angle=135)
    win = Box(60, 170, 1220, 760)
    wm = [(0, {"dx": -1400}, "out"), (0.6, {})]
    rrect(t, t.track("shape", "Ventana"), "#2A3142", 0, 10.0, Box(win.x, win.y - 56, win.w, win.h + 56), 22, wm,
          layers=[shadow("#000000", 0, 20, 44, 0.5), fill("#2A3142"), no_stroke()])
    dots_tr = t.track("shape", "Ventana")
    for k, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        t.solid(dots_tr if k == 0 else t.track("shape", "Ventana"), c, 0, 10.0, centered(win.x + 34 + k * 36,
                                                                                        win.y - 28, 20, 20),
                wm, kind="ellipse")
    _v(t, "y4b-h-flip-01", 0, 10.0, win, [(0, {"dx": -1400}, "out"), (0.6, {}, "linear"), (10.0, {"s": 1.04})],
       label="Video que comentas")
    facecam(t, "y4-sorpresa-h-03", 0.4, 9.6, Box(1320, 170, 540, 760),
            [(0, {"dx": 700}, "out"), (0.6, {}, "hold"), (4.0, {}, "snap"), (4.2, {"s": 1.06}, "linear"),
             (5.5, {"s": 1.06}, "inout"), (6.0, {})], border="#3B82F6", width=8, radius=22)
    label(t, t.track("text", "Título"), "REACCIONANDO A: el truco más difícil del año", 0.6, 9.4,
          Box(60, 30, 1800, 80), "Montserrat", 46, "#FFFFFF", weight=800, align="left",
          anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Título")
    t.solid(t.track("shape", "Barra"), "#3B82F6", 0, 10.0, Box(0, 980, 1920, 100), slide_in(dy=120))
    label(t, t.track("text", "Barra"), "Cuéntame en los comentarios qué opinas 👇", 0.5, 9.5, Box(60, 980, 1800, 100),
          "Montserrat", 44, "#FFFFFF", weight=700, align="left", motion=slide_in(dy=120), name="Llamada")
    burst(t, ["😮", "🔥", "👏"], 4.0, 1590, 500, seed=25)
    song(t, "cine", 0, 0.7)
    return t


def reac_musica():
    t = _t(tall, "yt-reac-musica", "Primera vez escuchando", "First time listening reaction", 26, 10.0,
           REAC + ["música", "music", "canción"], thumb_at=8.2, background="#0B0B12")
    _v(t, "concert-02", 0, 10.0, Box(0, 0, 1080, 960), kb(10.0, 1.0, 1.1), label="Video musical")
    _v(t, "y4-sorpresa-04", 0, 10.0, Box(0, 1040, 1080, 880),
       [(0, {}, "hold"), (4.5, {}, "snap"), (4.7, {"s": 1.2}, "linear"), (10.0, {"s": 1.25})],
       label="Tu cara (cámara)", name="Cámara")
    t.solid(t.track("shape", "Banda"), "#0B0B12", 0, 10.0, Box(0, 940, 1080, 120))
    rng = random.Random(26)
    tr = t.track("shape", "Ecualizador")
    for k in range(24):
        x = 40 + k * 42
        h = 90
        pts = [(0, {"sy": 0.2}, "smooth")]
        at = 0.0
        while at < 10.0:
            at += rng.uniform(0.18, 0.35)
            pts.append((min(at, 10.0), {"sy": rng.uniform(0.15, 1.0)}, "smooth"))
        t.solid(tr, "#FF2E88" if k % 2 else "#FFB800", 0, 10.0, Box(x, 955, 26, h), pts, radius=8,
                kind="rounded-rectangle")
    chip(t, "PRIMERA VEZ ESCUCHANDO", 0.3, 9.7, Box(140, 150, 800, 90), "#FFFFFF", "#0B0B12", "Archivo Black", 44,
         motion=pop(0, 0.4))
    rrect(t, t.track("shape", "Nota"), "#FF2E88", 7.4, 2.6, Box(290, 1430, 500, 240), 40, pop(0, 0.4),
          layers=[shadow("#000000", 0, 12, 30, 0.5), fill("#FF2E88"), no_stroke()])
    label(t, t.track("text", "Nota"), "10/10 🔥", 7.4, 2.6, Box(290, 1430, 500, 240), "Archivo Black", 110, "#FFFFFF",
          weight=400, motion=pop(0, 0.4), name="Nota")
    burst(t, ["🎶", "😍", "🔥"], 4.6, 540, 1500, seed=26)
    song(t, "electro", 1)
    return t


def reac_nota_h():
    t = _t(wide, "yt-reac-nota-h", "Reacción con nota final", "Reaction with a score", 27, 9.0,
           REAC + ["nota", "score", "16:9"], thumb_at=7.6, background="#000000")
    _v(t, "h-food-03", 0, 9.0, motion=[(0, {"s": 1.0}, "linear"), (5.4, {"s": 1.06, "dx": 0}, "out"),
                                       (6.0, {"s": 1.06, "dx": -300}, "linear"), (9.0, {"s": 1.08, "dx": -300})],
       label="Video que comentas")
    circle_photo(t, "y4-sorpresa-h-05", 0.3, 8.7, centered(220, 850, 300, 300), pop(0, 0.4), ring_colour="#22C55E",
                 ring_width=10, label="Tu cara (cámara)")
    panel = Box(1240, 0, 680, 1080)
    pm = [(0, {"dx": 700}, "out"), (0.5, {})]
    t.solid(t.track("shape", "Panel"), "#0F172A", 5.5, 3.5, panel, pm, alpha=0.92)
    label(t, t.track("text", "Panel"), "MI NOTA", 5.6, 3.4, Box(1300, 220, 560, 110), "Montserrat", 64, "#94A3B8",
          weight=800, spacing=6, motion=pm, name="Título de la nota")
    label(t, t.track("text", "Nota"), "8/10", 5.8, 3.2, Box(1300, 330, 560, 300), "Archivo Black", 210, "#22C55E",
          weight=400, anim_in=tanim("stamp", duration=0.25), name="Nota")
    rrect(t, t.track("shape", "Barra"), "#1E293B", 5.8, 3.2, Box(1330, 680, 500, 40), 20)
    rrect(t, t.track("shape", "Barra"), "#22C55E", 6.0, 3.0, Box(1330, 680, 500, 40), 20,
          [(0, {"sx": 0.0, "dx": -250}, "out"), (1.2, {"sx": 0.8, "dx": -50})])
    label(t, t.track("text", "Veredicto"), "¡Lo volvería a comer!", 6.4, 2.6, Box(1300, 760, 560, 120), "Montserrat",
          46, "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.4), name="Veredicto")
    burst(t, ["😋", "🤤"], 2.5, 220, 800, seed=27)
    song(t, "jazz", 0)
    return t


def reac_comida():
    t = _t(tall, "yt-reac-comida", "¿Lo probarías?", "Would you try it?", 28, 9.0,
           REAC + ["comida", "food", "encuesta"], thumb_at=5.2, background="#FF8A00")
    _v(t, "y4-sorpresa-05", 0, 9.0, motion=[(0, {}, "hold"), (4.5, {}, "snap"), (4.7, {"s": 1.15}, "linear"),
                                            (9.0, {"s": 1.2})], label="Tu cara (cámara)", name="Cámara")
    circle_photo(t, "restaurant-02", 0.3, 8.7, centered(290, 1270, 440, 440),
                 [(0, {"s": 0.0}, "back"), (0.5, {}, "linear"), (8.7, {"s": 1.04})], ring_colour="#FFFFFF",
                 ring_width=14, label="Video de la comida")
    label(t, t.track("text", "Pregunta"), "¿LO PROBARÍAS?", 0.5, 8.5, Box(40, 110, 1000, 150), "Luckiest Guy", 110,
          "#FFFFFF", weight=400, layers=outlined("#FFFFFF", 9), anim_in=tanim("bounce", duration=0.5),
          name="Pregunta")
    chip(t, "SÍ 😋", 2.0, 7.0, Box(120, 1640, 380, 130), "#22C55E", "#FFFFFF", "Luckiest Guy", 70,
         motion=pop(0, 0.4))
    chip(t, "NO 🤢", 2.2, 6.8, Box(580, 1640, 380, 130), "#EF4444", "#FFFFFF", "Luckiest Guy", 70,
         motion=pop(0, 0.4))
    burst(t, ["🤤", "😍", "🤤"], 4.55, 300, 1050, seed=28, size=140)
    shake(t, [4.5], 0.5, 0.3)
    song(t, "fun", 4)
    return t


def reac_pareja_h():
    t = _t(wide, "yt-reac-pareja-h", "Reacción en pareja", "Duo reaction 16:9", 29, 10.0,
           REAC + ["pareja", "duo", "16:9"], thumb_at=6.3, background="#140C24")
    bg_gradient(t, [(0, "#140C24"), (1, "#3B0F4A")], angle=0)
    c = _v(t, "y4b-h-dog-01", 0, 10.0, centered(960, 470, 1120, 630),
           [(0, {"s": 0.8}, "back"), (0.5, {}, "linear"), (10.0, {"s": 1.03})], label="Video que comentas")
    round_mask(t, c, 28)
    for i, (s, name, x, at, col) in enumerate([("y4-sorpresa-h-01", "ANA", 200, 3.0, "#FF4F9A"),
                                               ("y4-sorpresa-h-04", "LEO", 1720, 6.0, "#22D3EE")]):
        fm = [(0, {"s": 0.0}, "back"), (0.5, {}, "hold"), (at - 0.3, {}, "snap"), (at - 0.1, {"s": 1.18}, "linear"),
              (at + 1.2, {"s": 1.18}, "inout"), (at + 1.6, {})]
        circle_photo(t, s, 0.3 + i * 0.15, 9.7 - i * 0.15, centered(x, 640, 300, 300), fm, ring_colour=col,
                     ring_width=10, label=f"Cámara de {name.title()}")
        chip(t, name, 0.6 + i * 0.15, 9.4 - i * 0.15, centered(x, 860, 200, 70), col, "#FFFFFF", size=40,
             motion=slide_in(dy=60), name=f"Nombre {i + 1}")
        burst(t, ["😂", "😂", "😳"] if i == 0 else ["😱", "🔥", "😱"], at - 0.2, x, 560, seed=29 + i)
    label(t, t.track("text", "Título"), "REACCIONAMOS JUNTOS", 0.3, 9.7, Box(360, 940, 1200, 100), "Archivo Black", 64,
          "#FFFFFF", weight=400, spacing=4, anim_in=tanim("rise-by-word", duration=0.4, unit="word"), name="Título")
    song(t, "fun", 2)
    return t


def reac_esquinas():
    t = _t(tall, "yt-reac-esquinas", "Cámara que salta de esquina", "Jumping corner cam", 30, 10.0,
           REAC + ["esquina", "corner", "dinámico"], thumb_at=3.2, background="#000000")
    _v(t, "y4-viral-06", 0, 10.0, motion=kb(10.0, 1.0, 1.1), label="Video que comentas")
    box = Box(80, 180, 380, 380)
    spots = [(0, 0), (540, 0), (540, 1180), (0, 1180)]
    fm = [(0, {"s": 0.0}, "back")]
    for k, (dx, dy) in enumerate(spots):
        at = 0.45 + k * 2.4
        fm.append((at, {"dx": dx, "dy": dy}, "hold"))
        fm.append((at + 2.1, {"dx": dx, "dy": dy}, "snap"))
    fm = fm[:-1]
    fm.append((10.0, {"dx": spots[-1][0], "dy": spots[-1][1]}))
    facecam(t, "y4-sorpresa-08", 0.3, 9.7, box, fm, border="#FFE600", radius=190, width=10)
    punch(t, [2.55, 4.95, 7.35], 0.25, 0.2)
    label(t, t.track("text", "Texto"), "¿Quién más lo vio venir?", 0.5, 9.5, Box(60, 820, 960, 200), "Poppins", 78,
          "#FFFFFF", weight=800, layers=[shadow("#000000", 0, 4, 18, 0.9), fill("#FFFFFF")],
          anim_in=tanim("rise-by-word", duration=0.4, unit="word"), name="Texto")
    emoji(t, "😏", 1.2, 8.6, 540, 1160, 150, loop=tanim("swing", angle=8, speed=1.0))
    song(t, "upbeat", 7)
    return t


def reac_dueto():
    t = _t(tall, "yt-reac-dueto", "Dueto de reacción", "Reaction duet", 31, 9.0,
           REAC + ["dueto", "duet"], thumb_at=4.2, background="#000000")
    _v(t, "y4-viral-06", 0, 9.0, motion=kb(9.0, 1.2, 1.3), label="Video que comentas",
       effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=40), effect("color.basic", exposure=-0.5)])
    a = _v(t, "y4-viral-06", 0, 9.0, Box(0, 480, 540, 960), kb(9.0, 1.0, 1.06), reuse="p1", name="Video")
    b = _v(t, "y4-calle-03", 0, 9.0, Box(540, 480, 540, 960),
           [(0, {}, "hold"), (4.0, {}, "snap"), (4.2, {"sx": 1.0, "sy": 1.0}, "linear"), (9.0, {"s": 1.06})],
           label="Tu cara (cámara)", name="Cámara")
    outline(t, t.track("shape", "Marco"), "#FFFFFF", 6, 0, 9.0, Box(0, 480, 1080, 960))
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, 9.0, Box(537, 480, 6, 960))
    chip(t, "DUETO", 0.2, 8.8, Box(390, 330, 300, 90), "#FFFFFF", "#111111", "Archivo Black", 48, motion=pop(0, 0.4),
         editable=False)
    label(t, t.track("text", "Texto"), "no me esperaba ese final 😂", 0.6, 8.4, Box(60, 1480, 960, 200), "Poppins", 72,
          "#FFFFFF", weight=800, anim_in=tanim("typewriter", duration=1.0, unit="character"), name="Texto")
    burst(t, ["😂", "😂", "💀"], 4.0, 810, 900, seed=31)
    song(t, "fun", 0)
    return t


def reac_cine_h():
    t = _t(wide, "yt-reac-cine-h", "Función de reacción", "Watch party reaction 16:9", 32, 10.0,
           REAC + ["cine", "watch party", "16:9"], thumb_at=4.6, background="#0A0505")
    bg_gradient(t, [(0, "#1A0909"), (1, "#050202")], angle=90)
    scr = Box(330, 110, 1260, 700)
    t.solid(t.track("shape", "Pantalla"), "#FFFFFF", 0, 10.0, Box(scr.x - 6, scr.y - 6, scr.w + 12, scr.h + 12),
            layers=[glow("#FFE7B3", 60, 0.55), fill("#FFFFFF"), no_stroke()])
    _v(t, "h-concert-03", 0, 10.0, scr, kb(10.0, 1.0, 1.08), label="Video que comentas")
    for side in (-1, 1):
        x = 0 if side < 0 else 1920 - 420
        t.solid(t.track("shape", "Telón"), "#8B0E1A", 0, 10.0, Box(x, 0, 420, 1080),
                [(0, {"sx": 2.3, "dx": -side * 0}, "inout"), (1.2, {})],
                layers=[gradient([(0, "#5E0610"), (0.5, "#B3172A"), (1, "#5E0610")], angle=0), no_stroke()])
    circle_photo(t, "y4-sorpresa-h-03", 1.2, 8.8, centered(250, 860, 300, 300),
                 [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (4.0, {}, "snap"), (4.2, {"s": 1.2}, "linear"),
                  (5.6, {"s": 1.2}, "inout"), (6.0, {})], ring_colour="#FFC94D", ring_width=10,
                 label="Tu cara (cámara)")
    emoji(t, "🍿", 1.4, 8.6, 440, 950, 130, loop=tanim("swing", angle=8, speed=0.8))
    label(t, t.track("text", "Título"), "FUNCIÓN DE HOY", 1.2, 8.8, Box(560, 860, 800, 110), "Cinzel", 64, "#FFC94D",
          weight=700, spacing=10, layers=[glow("#FFC94D", 18, 0.5), fill("#FFC94D")],
          anim_in=tanim("blur-in", duration=0.6), name="Título")
    label(t, t.track("text", "Subtítulo"), "con palomitas y sin spoilers", 1.6, 8.4, Box(560, 960, 800, 70), "Montserrat",
          38, "#FFFFFF", weight=600, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    burst(t, ["😱", "😂", "👏"], 4.1, 250, 760, seed=32)
    song(t, "cine", 1, 0.75)
    return t


def reac_repeticion():
    t = _t(tall, "yt-reac-repeticion", "Repetición en cámara lenta", "Slow-mo replay reaction", 33, 10.0,
           REAC + ["repetición", "replay", "cámara lenta"], thumb_at=6.4, background="#000000")
    tr = t.track("video", "Video")
    a = _v(t, "y4-viral-03", 0, 4.6, motion=kb(4.6, 1.0, 1.08), label="Video que comentas", track=tr)
    b = t.photo(tr, "y4-viral-03", 4.6, 5.4, t.full, [(0, {"s": 1.5}, "linear"), (5.4, {"s": 1.75})], reuse="p1",
                effects=[effect("color.basic", saturation=-0.4, contrast=0.2)])
    t.transition(tr, a, b, "dip_white", 0.4)
    letterbox(t, 0.8, 4.6, 5.4)
    facecam(t, "y4-sorpresa-01", 0.3, 9.7, Box(660, 160, 340, 340),
            [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (4.6, {}, "snap"), (4.85, {"s": 1.35, "dx": -40, "dy": 60},
                                                                               "linear"),
             (9.7, {"s": 1.4, "dx": -40, "dy": 60})], border="#FFFFFF", radius=30)
    chip(t, "⏪ REPETICIÓN", 4.7, 5.3, Box(60, 1580, 520, 100), "#FFFFFF", "#111111", "Archivo Black", 46,
         motion=slide_in(dx=-600), loop=tanim("flicker", intensity=0.3, speed=2))
    chip(t, "x0.5", 4.8, 5.2, Box(820, 1580, 200, 100), "#E11D48", "#FFFFFF", "Archivo Black", 48,
         motion=slide_in(dx=400), editable=False)
    label(t, t.track("text", "Texto"), "otra vez, más lento 👀", 0.4, 4.0, Box(60, 1300, 960, 160), "Poppins", 76,
          "#FFFFFF", weight=800, layers=[shadow("#000000", 0, 4, 16, 0.85), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.3, unit="word", stagger=0.1), anim_out=tanim("fade", duration=0.2),
          name="Texto")
    song(t, "epic", 2)
    return t


def reac_real_falso_h():
    t = _t(wide, "yt-reac-real-falso-h", "¿Real o falso?", "Real or fake?", 34, 10.0,
           REAC + ["real o falso", "real or fake", "16:9"], thumb_at=7.4, background="#0B0B0B")
    bg(t, "#0B0B0B")
    _v(t, "y4b-h-dog-06", 0, 10.0, Box(60, 180, 1180, 760), kb(10.0, 1.0, 1.06), label="Video que comentas")
    facecam(t, "y4-sorpresa-h-01", 0.3, 9.7, Box(1290, 180, 570, 520), slide_in(dx=700), border="#FFFFFF", width=6,
            radius=20)
    label(t, t.track("text", "Título"), "¿REAL O FALSO?", 0.2, 9.8, Box(60, 40, 1800, 120), "Anton", 100, "#FFFFFF",
          weight=400, align="left", anim_in=tanim("slide-right", duration=0.4), name="Título")
    chip(t, "REAL", 0.8, 9.2, Box(1290, 760, 270, 140), "#22C55E", "#FFFFFF", "Anton", 72, motion=pop(0, 0.4),
         weight=400, name="Opción 1")
    rrect(t, t.track("shape", "Elegido"), "#EF4444", 0.9, 9.1, Box(1590, 760, 270, 140), 70,
          [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (6.0, {}, "back"), (6.3, {"s": 1.15}, "inout"),
           (6.6, {"s": 1.05})])
    label(t, t.track("text", "Elegido"), "FALSO", 0.9, 9.1, Box(1590, 760, 270, 140), "Anton", 72, "#FFFFFF",
          weight=400, motion=[(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (6.0, {}, "back"), (6.3, {"s": 1.15},
                                                                                              "inout"),
                              (6.6, {"s": 1.05})], name="Opción 2")
    label(t, t.track("text", "Veredicto"), "¡FALSO!", 6.0, 4.0, Box(160, 380, 980, 360), "Anton", 250, "#EF4444",
          weight=400, layers=[shadow("#000000", 0, 10, 0, 0.9), stroke(12, "#FFFFFF"), fill("#EF4444")],
          anim_in=tanim("stamp", duration=0.25), rotation=keys([(0, -10.0)]), name="Veredicto")
    shake(t, [6.05], 0.5, 0.3)
    song(t, "suspense", 1)
    return t


def reac_sus_videos():
    t = _t(tall, "yt-reac-sus-videos", "Reacciono a sus videos", "Reacting to your videos", 35, 10.5,
           REAC + ["seguidores", "followers", "videos"], thumb_at=4.6, background="#111827")
    bg_gradient(t, [(0, "#111827"), (1, "#312E81")], angle=90)
    phone = Box(250, 150, 580, 1030)
    rrect(t, t.track("shape", "Teléfono"), "#000000", 0, 10.5, Box(phone.x - 18, phone.y - 18, phone.w + 36,
                                                                   phone.h + 36), 56,
          [(0, {"dy": -1300}, "out"), (0.5, {})], layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#000000"),
                                                          no_stroke()])
    tr = t.track("video", "Sus videos")
    prev = None
    for i, s in enumerate(["y4-viral-05", "puppy-01", "dance-02"]):
        at = 0.3 + i * 3.4
        d = 3.4 + (0.3 if i < 2 else 10.5 - at - 3.4)
        c = _v(t, s, at, d, phone, kb(d, 1.0, 1.08) if i else [(0, {"dy": -1300}, "out"), (0.5, {}, "linear"),
                                                                 (d, {"s": 1.08})],
               label=f"Video de seguidor {i + 1}", track=tr)
        if prev:
            t.transition(tr, prev, c, "slide_up", 0.3)
        prev = c
        round_mask(t, c, 40)
        chip(t, f"{i + 1}/3", at + 0.2, 3.1 if i < 2 else d - 0.2, Box(phone.x + 20, phone.y + 24, 140, 64),
             "#FFFFFF", "#111111", size=34, motion=pop(0, 0.3), editable=False, name="Contador")
    circle_photo(t, "y4-calle-07", 0.6, 9.9, centered(540, 1480, 420, 420),
                 [(0, {"s": 0.0}, "back"), (0.5, {}, "hold"), (3.6, {}, "snap"), (3.8, {"s": 1.12}, "inout"),
                  (4.3, {}, "hold"), (7.0, {}, "snap"), (7.2, {"s": 1.12}, "inout"), (7.7, {})],
                 ring_colour="#A78BFA", ring_width=12, label="Tu cara (cámara)")
    label(t, t.track("text", "Título"), "REACCIONO A SUS VIDEOS", 0.4, 10.1, Box(40, 1730, 1000, 110), "Archivo Black",
          62, "#FFFFFF", weight=400, anim_in=tanim("rise-by-word", duration=0.4, unit="word"), name="Título")
    burst(t, ["😍", "🐶", "😂"], 3.7, 540, 1300, seed=35)
    burst(t, ["🔥", "💃", "👏"], 7.1, 540, 1300, seed=36)
    song(t, "upbeat", 2)
    return t


REACS = [reac_esquina_h, reac_arriba_abajo, reac_espera, reac_dividida_h, reac_tarjeta, reac_zoom_cara,
         reac_comentarios, reac_ventana_h, reac_musica, reac_nota_h, reac_comida, reac_pareja_h, reac_esquinas,
         reac_dueto, reac_cine_h, reac_repeticion, reac_real_falso_h, reac_sus_videos]


# 3 · Entrevista en la calle ----------------------------------------------------------------------

def mic(t, cx: float, top: float, s: float = 1.0, *, flag="#E11D48", flag_ink="#FFFFFF", flag_text="TU CANAL",
        t0: float = 0.0, dur: float | None = None, motion=None, font="Archivo Black"):
    """A handheld microphone drawn with shapes: silver grille, collar, the channel cube (editable name), handle.
    `motion` moves the whole microphone (scale about its middle)."""
    dur = t.duration - t0 if dur is None else dur
    gc = (cx, top + 260 * s)  # the group's centre

    def m(box: Box):
        return group(motion, box.cx - gc[0], box.cy - gc[1]) if motion else None

    handle = Box(cx - 30 * s, top + 150 * s, 60 * s, 330 * s)
    t.solid(t.track("shape", "Micrófono"), "#1A1A1A", t0, dur, handle, m(handle), radius=30 * s,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 10, 24, 0.45),
                                              gradient([(0, "#4A4A4A"), (0.45, "#151515"), (1, "#2E2E2E")], angle=0),
                                              no_stroke()])
    cube = Box(cx - 92 * s, top + 178 * s, 184 * s, 138 * s)
    t.solid(t.track("shape", "Micrófono"), flag, t0, dur, cube, m(cube), radius=14 * s, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 8, 18, 0.35), fill(flag), no_stroke()])
    label(t, t.track("text", "Micrófono"), flag_text, t0, dur, cube, font, int(34 * s), flag_ink, weight=400,
          line=0.95, motion=m(cube), name="Nombre del canal")
    collar = Box(cx - 52 * s, top + 140 * s, 104 * s, 34 * s)
    t.solid(t.track("shape", "Micrófono"), "#2A2A2A", t0, dur, collar, m(collar), radius=10 * s,
            kind="rounded-rectangle", layers=[gradient([(0, "#6B6B6B"), (0.5, "#2A2A2A"), (1, "#5A5A5A")], angle=0),
                                              no_stroke()])
    head = centered(cx, top + 78 * s, 160 * s, 160 * s)
    t.solid(t.track("shape", "Micrófono"), "#BDBDBD", t0, dur, head, m(head), kind="ellipse",
            layers=[shadow("#000000", 0, 8, 20, 0.35),
                    gradient([(0, "#F2F2F2"), (0.55, "#A8A8A8"), (1, "#5E5E5E")], angle=90), no_stroke()])
    tr = t.track("shape", "Rejilla")
    r = 80 * s
    for dy in (-44, -16, 12, 40):
        w = 2 * math.sqrt(max(0.0, r * r - (dy * s) ** 2)) * 0.86
        bar = Box(cx - w / 2, top + 78 * s + dy * s - 2.5 * s, w, 5 * s)
        t.solid(tr, "#4A4A4A", t0, dur, bar, m(bar), alpha=0.55)


def question(t, text, t0, dur, *, box=Box(60, 140, 960, 250), colour="#FFFFFF", ink="#111111", tag="PREGUNTA",
             tag_colour="#FFD400", tag_ink="#111111", font="Montserrat", size=62, motion=None, radius=30, name="Pregunta"):
    """The question on top: a card with a little label hanging off its top edge."""
    m = motion or [(0, {"s": 0.7, "dy": -40}, "back"), (0.4, {})]
    rrect(t, t.track("shape", "Pregunta"), colour, t0, dur, box, radius, m,
          layers=[shadow("#000000", 0, 12, 30, 0.35), fill(colour), no_stroke()])
    label(t, t.track("text", "Pregunta"), text, t0, dur, Box(box.x + 30, box.y + 20, box.w - 60, box.h - 30), font,
          size, ink, weight=800, line=1.08, motion=group(m, 0, 5), name=name)
    if tag:
        tb = Box(box.x + 40, box.y - 34, 300, 64)
        pill(t, t.track("shape", "Pregunta"), tag_colour, t0, dur, tb, group(m, tb.cx - box.cx, tb.cy - box.cy))
        label(t, t.track("text", "Pregunta"), tag, t0, dur, tb, font, 32, tag_ink, weight=900, spacing=3,
              motion=group(m, tb.cx - box.cx, tb.cy - box.cy), name="Etiqueta de la pregunta")


def nametag(t, name, info, at, dur, x, y, *, colour="#FFD400", ink="#111111", colour2="#111111", ink2="#FFFFFF",
            font="Archivo Black", font2="Montserrat", w=520, h=92, size=54, size2=36, from_left=True, i=0):
    """Name (and age) on a block, the second line on a darker one; both slide in."""
    sx = -(w + x + 40) if from_left else (t.w - x + 40)
    m1 = [(0, {"dx": sx}, "out"), (0.35, {})]
    m2 = [(0, {"dx": sx}, "hold"), (0.1, {"dx": sx}, "out"), (0.45, {})]
    t.solid(t.track("shape", "Nombre"), colour, at, dur, Box(x, y, w, h), m1)
    label(t, t.track("text", "Nombre"), name, at, dur, Box(x + 24, y, w - 48, h), font, size, ink, weight=400,
          align="left", motion=m1, name=f"Nombre {i + 1}")
    if info:
        w2 = w * 0.78
        t.solid(t.track("shape", "Dato"), colour2, at, dur, Box(x, y + h, w2, h * 0.72), m2)
        label(t, t.track("text", "Dato"), info, at, dur, Box(x + 24, y + h, w2 - 48, h * 0.72), font2, size2, ink2,
              weight=700, align="left", motion=m2, name=f"Dato {i + 1}")


def cuts(t, samples, start, each, *, box=None, labels=None, transition=None, tdur=0.25, zoom=1.06, name="Personas",
         punch_in=True):
    """People one after another on one track (quick cuts); each starts slightly zoomed in and settles."""
    tr = t.track("video", name)
    clips, prev = [], None
    eachs = each if isinstance(each, list) else [each] * len(samples)
    at = start
    for i, s in enumerate(samples):
        d = eachs[i] + (tdur if transition and i < len(samples) - 1 else 0)
        d = min(d, t.duration - at)
        mo = [(0, {"s": 1.12}, "snap"), (0.25, {"s": 1.0}, "linear"), (d, {"s": zoom})] if punch_in else \
            kb(d, 1.0, zoom)
        c = _v(t, s, at, d, box, mo, label=(labels[i] if labels else f"Persona {i + 1}"), track=tr)
        if prev and transition:
            t.transition(tr, prev, c, transition, tdur)
        clips.append(c)
        prev = c
        at += eachs[i]
    return clips


def answers(t, items, box, make, name="Respuesta"):
    """One caption (karaoke) per person: items = [(text, t0, dur)]."""
    return captions(t, items, box, make, name=name)


def calle_que_opinas():
    people = ["y4-calle-03", "man-02", "y4-calle-07", "portrait-03"]
    each = 2.4
    t = _t(tall, "yt-calle-que-opinas", "¿Qué opinas de…?", "What do you think of…?", 36, 0.2 + each * 4 + 0.2,
           CALLE + ["opinión", "opinion", "street interview"], thumb_at=0.2 + each + 1.7, background="#111111")
    cuts(t, people, 0.2, each)
    for k in range(1, 4):
        flash(t, 0.2 + k * each, 0.18, peak=0.6)
    shade_bottom(t, 760, 0.55)
    mic(t, 860, 1080, 0.9, flag="#E11D48", t0=0.3, motion=[(0, {"dy": 900}, "out"), (0.5, {}, "smooth"),
                                                          (t.duration - 0.3, {"dy": 12})])
    question(t, "¿Qué opinas de trabajar desde casa?", 0.0, t.duration)
    tags = [("Carla, 24", "estudiante"), ("Marcos, 35", "diseñador"), ("Elena, 29", "enfermera"),
            ("Jorge, 41", "cocinero")]
    said = ["«¡Me encanta, cero tráfico!»", "«Extraño a mis compañeros»", "«Depende del día, la verdad»",
            "«Yo no podría, me distraigo»"]
    for i, (n, info) in enumerate(tags):
        nametag(t, n, info, 0.35 + i * each, each - 0.25, 60, 1300, i=i, colour="#FFD400")
    items = [(said[i], 0.5 + i * each, each - 0.4) for i in range(4)]
    answers(t, items, Box(60, 1520, 960, 220),
            kara("Montserrat", 64, "#FFFFFF", "#FFD400", layers=[shadow("#000000", 0, 4, 14, 0.85), fill("#FFFFFF")],
                 case="none", weight=800, inn="fade", loop=None))
    song(t, "upbeat", 1, 0.6)
    return t


def calle_a_que_te_dedicas():
    people = ["man-01", "y4-calle-04", "man-05", "portrait-06", "y4-calle-01"]
    jobs = [("Andrés, 31", "💻 Programador"), ("Sofía, 26", "🎨 Tatuadora"), ("Luis, 44", "🚕 Taxista"),
            ("Paula, 33", "🩺 Doctora"), ("Diego, 22", "🎸 Músico")]
    each = 1.8
    t = _t(tall, "yt-calle-a-que-te-dedicas", "¿A qué te dedicas?", "What do you do for a living?", 37,
           0.3 + each * 5 + 0.3, CALLE + ["trabajo", "jobs", "profesiones"], thumb_at=0.3 + each * 1 + 1.3,
           background="#0F766E")
    cuts(t, people, 0.3, each, transition="push_left", tdur=0.2)
    shade_top(t, 520, 0.55)
    label(t, t.track("text", "Pregunta"), "¿A QUÉ TE DEDICAS?", 0.1, t.duration - 0.1, Box(40, 150, 1000, 150),
          "Anton", 120, "#FFFFFF", weight=400, layers=outlined("#FFFFFF", 8), anim_in=tanim("stamp", duration=0.25),
          name="Pregunta")
    for i, (n, job) in enumerate(jobs):
        at = 0.45 + i * each
        d = each - 0.3
        pill(t, t.track("shape", "Oficio"), "#14B8A6", at, d, centered(540, 1450, 760, 150), pop(0, 0.35))
        label(t, t.track("text", "Oficio"), job, at, d, centered(540, 1450, 760, 150), "Poppins", 74, "#FFFFFF",
              weight=800, motion=pop(0, 0.35), name=f"Oficio {i + 1}")
        label(t, t.track("text", "Nombre"), n, at + 0.1, d - 0.1, centered(540, 1580, 760, 80), "Poppins", 50, "#FFFFFF",
              weight=700, layers=[shadow("#000000", 0, 3, 12, 0.9), fill("#FFFFFF")], anim_in=tanim("fade", duration=0.2),
              name=f"Nombre {i + 1}")
    mic(t, 180, 1640, 0.62, flag="#14B8A6", t0=0.3)
    punch(t, [0.3 + k * each for k in range(1, 5)], 0.25, 0.2)
    song(t, "upbeat", 4, 0.7)
    return t


def calle_verdadero_falso():
    people = ["portrait-02", "man-04", "y4-calle-07"]
    verdicts = [("VERDADERO", "#22C55E"), ("FALSO", "#EF4444"), ("VERDADERO", "#22C55E")]
    each = 2.4
    t = _t(tall, "yt-calle-verdadero-falso", "¿Verdadero o falso?", "True or false?", 38, 0.3 + each * 3 + 2.4,
           CALLE + ["verdadero o falso", "true or false", "trivia"], thumb_at=0.3 + each + 1.9, background="#1E1B4B")
    bg_gradient(t, [(0, "#1E1B4B"), (1, "#4C1D95")], angle=90)
    cuts(t, people, 0.3, each, box=Box(60, 520, 960, 1140), transition="dip_white", tdur=0.2)
    question(t, "Los pulpos tienen tres corazones", 0.0, t.duration, box=Box(60, 170, 960, 230),
             tag="¿VERDADERO O FALSO?", tag_colour="#A78BFA", tag_ink="#FFFFFF", size=60)
    for i, (v, c) in enumerate(verdicts):
        at = 0.3 + i * each + 1.0
        label(t, t.track("text", "Respuesta"), v, at, each - 1.1, Box(60, 1380, 960, 200), "Anton", 150, c, weight=400,
              layers=[shadow("#000000", 0, 10, 0, 0.8), stroke(10, "#FFFFFF"), fill(c)],
              anim_in=tanim("stamp", duration=0.2), rotation=keys([(0, -5.0)]), name=f"Respuesta {i + 1}")
    end = 0.3 + each * 3
    t.solid(t.track("shape", "Final"), "#22C55E", end, t.duration - end, t.full, slide_in(dy=1920, length=0.4))
    label(t, t.track("text", "Final"), "¡ES VERDADERO! 🐙", end + 0.2, t.duration - end - 0.2, Box(40, 700, 1000, 520),
          "Anton", 150, "#FFFFFF", weight=400, layers=outlined("#FFFFFF", 8), anim_in=tanim("pop", duration=0.35),
          name="Resultado")
    label(t, t.track("text", "Final"), "2 de 3 acertaron", end + 0.6, t.duration - end - 0.6, Box(40, 1220, 1000, 120),
          "Montserrat", 64, "#FFFFFF", weight=800, anim_in=tanim("fade", duration=0.3), name="Aciertos")
    song(t, "fun", 1, 0.75)
    return t


def calle_trivia():
    qs = [("¿Capital de Australia?", "«¿Sídney?»", False), ("¿Cuántos lados tiene un hexágono?", "«¡Seis!»", True),
          ("¿Qué planeta es el más grande?", "«Júpiter»", True)]
    people = ["y4-calle-06", "portrait-05", "man-06"]
    each = 3.0
    t = _t(tall, "yt-calle-trivia", "Preguntas en la calle", "Street trivia", 39, 0.3 + each * 3 + 0.3,
           CALLE + ["trivia", "cultura general", "quiz"], thumb_at=0.3 + each + 2.4, background="#0B132B")
    cuts(t, people, 0.3, each, transition="slide_left", tdur=0.25)
    shade_bottom(t, 760, 0.6, colour="#0B132B")
    shade_top(t, 560, 0.6, colour="#0B132B")
    score = 0
    for i, (q, a, ok) in enumerate(qs):
        at = 0.3 + i * each
        d = each - 0.1
        chip(t, f"PREGUNTA {i + 1}", at + 0.1, d - 0.1, Box(60, 150, 330, 70), "#5BC0EB", "#0B132B", size=34,
             motion=pop(0, 0.3), editable=False, name="Número")
        label(t, t.track("text", "Pregunta"), q, at + 0.15, d - 0.15, Box(60, 240, 960, 220), "Montserrat", 72,
              "#FFFFFF", weight=900, align="left", anim_in=tanim("rise-by-word", duration=0.35, unit="word",
                                                                  stagger=0.05),
              name=f"Pregunta {i + 1}")
        rrect(t, t.track("shape", "Respuesta"), "#FFFFFF", at + 1.0, d - 1.0, Box(110, 1380, 700, 150), 75, pop(0, 0.35))
        label(t, t.track("text", "Respuesta"), a, at + 1.0, d - 1.0, Box(110, 1380, 700, 150), "Montserrat", 66,
              "#0B132B", weight=800, motion=pop(0, 0.35), name=f"Respuesta {i + 1}")
        c = "#22C55E" if ok else "#EF4444"
        t.solid(t.track("shape", "Correcta"), c, at + 1.8, d - 1.8, centered(900, 1455, 150, 150),
                [(0, {"s": 0.0}, "back"), (0.3, {})], kind="ellipse")
        label(t, t.track("text", "Correcta"), "✓" if ok else "✗", at + 1.8, d - 1.8, centered(900, 1455, 150, 150),
              "Inter", 100, "#FFFFFF", weight=900, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.3, {})])
        score += ok
        chip(t, f"ACIERTOS: {score}", at + 1.9, d - 1.9 if i < 2 else t.duration - at - 1.9,
             Box(700, 150, 320, 70), "#FFD400", "#0B132B", size=34, motion=pop(0, 0.3), editable=False,
             name="Aciertos")
    mic(t, 960, 1640, 0.5, flag="#5BC0EB", flag_ink="#0B132B", t0=0.3)
    song(t, "fun", 3, 0.7)
    return t


def calle_consejo():
    people = ["elderly-01", "elderly-03", "elderly-02"]
    quotes = ["«Viaja más y preocúpate menos.»", "«Ahorra un poco cada mes, aunque sea poco.»",
              "«Llama a tu mamá más seguido.»"]
    names = ["Rosa, 71", "Ernesto, 68", "Carmen, 75"]
    each = 3.6
    t = _t(tall, "yt-calle-consejo", "Consejo a tu yo de 20 años", "Advice to your 20-year-old self", 40,
           0.6 + each * 3 + 0.3, CALLE + ["consejos", "advice", "abuelos"], thumb_at=0.6 + each + 2.6,
           background="#1C1917")
    cuts(t, people, 0.6, each, transition="crossfade", tdur=0.6, punch_in=False, zoom=1.08)
    t.adjust([effect("color.basic", fade=0.12, temperature=0.15, saturation=-0.1),
              effect("stylize.film_grain", amount=0.18)], name="Cálido")
    shade_bottom(t, 900, 0.75, colour="#1C1917")
    label(t, t.track("text", "Pregunta"), "¿Qué consejo le darías\na tu yo de 20 años?", 0.0, t.duration,
          Box(60, 150, 960, 260), "DM Serif Display", 80, "#FFFFFF", weight=400, line=1.05,
          layers=[shadow("#000000", 0, 4, 22, 0.8), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.8),
          name="Pregunta")
    for i in range(3):
        at = 0.6 + i * each + 0.5
        d = each - 0.7
        label(t, t.track("text", "Consejo"), quotes[i], at, d, Box(80, 1280, 920, 300), "DM Serif Display", 76,
              "#FFFFFF", weight=400, italic=True, line=1.1,
              anim_in=tanim("fade-up-char", duration=0.5, unit="word", stagger=0.08), anim_out=tanim("fade", duration=0.3),
              name=f"Consejo {i + 1}")
        line(t, t.track("shape", "Línea"), "#E9C46A", at + 0.3, d - 0.3, Box(80, 1620, 120, 5))
        label(t, t.track("text", "Nombre"), names[i], at + 0.3, d - 0.3, Box(80, 1640, 600, 80), "Montserrat", 44,
              "#E9C46A", weight=700, align="left", anim_in=tanim("fade", duration=0.4), name=f"Nombre {i + 1}")
    song(t, "romantic", 0, 0.7)
    return t


def calle_mic_grande():
    people = ["portrait-07", "y4-calle-01", "man-03"]
    said = ["¡OBVIO QUE SÍ!", "MMM… NO SÉ 🤔", "¡JAMÁS! 😂"]
    each = 2.6
    t = _t(tall, "yt-calle-mic-grande", "Micrófono en primer plano", "Big microphone interview", 41,
           0.2 + each * 3 + 0.2, CALLE + ["micrófono", "microphone", "pov"], thumb_at=0.2 + 2 * 1.0 + 1.4,
           background="#111111")
    cuts(t, people, 0.2, each, transition="zoom_in", tdur=0.25)
    for k in range(1, 3):
        flash(t, 0.2 + k * each, 0.15, peak=0.5)
    mic(t, 690, 1120, 1.75, flag="#FFD400", flag_ink="#111111", flag_text="EN LA\nCALLE",
        motion=[(0, {"dy": 900, "s": 1.0}, "out"), (0.5, {}, "smooth"), (1.6, {"dy": -10}, "smooth"),
                (2.8, {"dy": 6}, "smooth"), (t.duration, {"dy": -8})])
    label(t, t.track("text", "Pregunta"), "¿PIÑA EN LA PIZZA?", 0.1, t.duration - 0.1, Box(40, 150, 1000, 200),
          "Luckiest Guy", 120, "#FFD400", weight=400, layers=outlined("#FFD400", 9), anim_in=tanim("bounce", duration=0.4),
          anim_loop=tanim("sway", angle=2, speed=0.8), name="Pregunta")
    for i in range(3):
        at = 0.2 + i * each + 0.7
        label(t, t.track("text", "Respuesta"), said[i], at, each - 0.8, Box(40, 360, 1000, 180), "Luckiest Guy", 96,
              "#FFFFFF", weight=400, layers=outlined("#FFFFFF", 8), anim_in=tanim("pop", duration=0.25),
              rotation=keys([(0, [-4.0, 3.0, -2.0][i])]), name=f"Respuesta {i + 1}")
    song(t, "fun", 4, 0.75)
    return t


def calle_noticiero_h():
    people = ["y4-calle-h-01", "y4-calle-h-03", "h-man-02"]
    each = 3.2
    t = _t(wide, "yt-calle-noticiero-h", "Entrevista estilo noticiero", "News-style street interview", 42,
           0.2 + each * 3 + 0.2, CALLE + ["noticias", "news", "16:9"], thumb_at=0.2 + each + 2.0, background="#0A1A33")
    cuts(t, people, 0.2, each, transition="crossfade", tdur=0.3, punch_in=False, zoom=1.06)
    t.solid(t.track("shape", "Cinta"), "#0A1A33", 0, t.duration, Box(0, 990, 1920, 90), slide_in(dy=100))
    t.solid(t.track("shape", "Cinta"), "#E11D48", 0, t.duration, Box(0, 990, 300, 90), slide_in(dx=-300))
    label(t, t.track("text", "Cinta"), "EN LA CALLE", 0.2, t.duration - 0.2, Box(0, 990, 300, 90), "Oswald", 46,
          "#FFFFFF", weight=700, spacing=3, name="Sección")
    label(t, t.track("text", "Cinta"), "HOY PREGUNTAMOS: ¿cuál es tu mayor miedo?   •   ¿y el tuyo?   •   "
          "escríbelo en los comentarios", 0.3, t.duration - 0.3, Box(330, 990, 3600, 90), "Oswald", 44, "#FFFFFF",
          weight=500, align="left", motion=[(0, {}, "linear"), (t.duration - 0.3, {"dx": -1500})], name="Cinta")
    chip(t, "● EN VIVO", 0.3, t.duration - 0.3, Box(60, 50, 250, 64), "#E11D48", "#FFFFFF", "Oswald", 36,
         loop=tanim("flicker", intensity=0.3, speed=1.5), editable=False)
    tags = [("Valeria Ruiz, 27", "fotógrafa"), ("Tomás Lee, 34", "profesor"), ("Mateo Silva, 52", "panadero")]
    for i, (n, info) in enumerate(tags):
        nametag(t, n, info, 0.5 + i * each, each - 0.5, 80, 760, i=i, colour="#FFFFFF", ink="#0A1A33",
                colour2="#E11D48", font="Oswald", size=52, w=620)
    song(t, "cine", 3, 0.5)
    return t


def calle_vs():
    t = _t(tall, "yt-calle-vs", "¿Esto o aquello? en la calle", "This or that street poll", 43, 9.0,
           CALLE + ["esto o aquello", "this or that", "versus"], thumb_at=3.2, background="#111111")
    rounds = [("¿PLAYA O MONTAÑA?", ["y4-calle-03", "man-04"], ["PLAYA 🏖️", "MONTAÑA 🏔️"]),
              ("¿PERRO O GATO?", ["portrait-08", "y4-calle-06"], ["GATO 🐱", "PERRO 🐶"])]
    for r, (q, ss, picks) in enumerate(rounds):
        at = 0.2 + r * 4.4
        d = 4.4 if r == 0 else t.duration - at
        for k in range(2):
            y = 0 if k == 0 else 970
            _v(t, ss[k], at + k * 0.2, d - k * 0.2, Box(0, y, 1080, 950),
               [(0, {"dx": -1080 if k == 0 else 1080}, "out"), (0.4, {}, "linear"), (d, {"s": 1.06})],
               label=f"Persona {r * 2 + k + 1}", name="Personas")
            pick_box = Box(60, y + (700 if k == 0 else 90), 620, 130)
            rrect(t, t.track("shape", "Elección"), "#FFFFFF" if k == 0 else "#FFD400", at + 1.4 + k * 0.4,
                  d - 1.4 - k * 0.4, pick_box, 65, pop(0, 0.35))
            label(t, t.track("text", "Elección"), picks[k], at + 1.4 + k * 0.4, d - 1.4 - k * 0.4, pick_box, "Archivo Black",
                  62, "#111111", weight=400, motion=pop(0, 0.35), name=f"Elección {r * 2 + k + 1}")
        t.solid(t.track("shape", "Centro"), "#111111", at, d, Box(0, 940, 1080, 40))
        label(t, t.track("text", "Pregunta"), q, at + 0.2, d - 0.2, centered(540, 960, 1000, 150), "Archivo Black", 76,
              "#FFFFFF", weight=400, box_bg=("#E11D48", 1.0), box_pad=24, box_radius=20,
              anim_in=tanim("pop", duration=0.3), name=f"Pregunta {r + 1}")
    song(t, "upbeat", 5, 0.7)
    return t


def calle_ranking():
    people = ["portrait-01", "man-06", "y4-calle-03", "portrait-04"]
    each = 1.6
    t = _t(tall, "yt-calle-ranking", "Encuesta en la calle con resultados", "Street poll with results", 44, 11.0,
           CALLE + ["encuesta", "poll", "resultados"], thumb_at=9.6, background="#FFF7ED")
    cuts(t, people, 0.2, each)
    q = "¿Cuál es tu comida favorita?"
    question(t, q, 0.0, 0.2 + each * 4, box=Box(60, 150, 960, 200), tag="ENCUESTA", tag_colour="#F97316",
             tag_ink="#FFFFFF", size=60)
    said = ["«¡Pizza, siempre!»", "«Tacos»", "«Sushi, sin duda»", "«Pizza 🍕»"]
    items = [(said[i], 0.45 + i * each, each - 0.35) for i in range(4)]
    answers(t, items, Box(60, 1450, 960, 200),
            kara("Poppins", 78, "#FFFFFF", "#FDBA74", layers=outlined("#FFFFFF", 6, "#7C2D12", dy=5), case="none",
                 weight=800, inn="pop", loop=None))
    end = 0.2 + each * 4
    t.solid(t.track("shape", "Resultados"), "#FFF7ED", end, t.duration - end, t.full, slide_in(dy=1920, length=0.45))
    label(t, t.track("text", "Resultados"), "RESULTADOS", end + 0.3, t.duration - end - 0.3, Box(60, 300, 960, 130),
          "Archivo Black", 96, "#7C2D12", weight=400, anim_in=tanim("rise", duration=0.4), name="Título")
    rows = [("Pizza 🍕", 0.5, "#F97316"), ("Tacos 🌮", 0.3, "#FB923C"), ("Sushi 🍣", 0.2, "#FDBA74")]
    for i, (n, v, c) in enumerate(rows):
        y = 560 + i * 300
        at = end + 0.6 + i * 0.25
        label(t, t.track("text", "Opción"), n, at, t.duration - at, Box(80, y, 920, 90), "Poppins", 64, "#7C2D12",
              weight=800, align="left", anim_in=tanim("fade", duration=0.3), name=f"Opción {i + 1}")
        bw = 880 * v / 0.5
        rrect(t, t.track("shape", "Barra"), c, at + 0.1, t.duration - at - 0.1, Box(80, y + 100, bw, 110), 30,
              [(0, {"sx": 0.0, "dx": -bw / 2}, "out"), (0.8, {})])
        label(t, t.track("text", "Porcentaje"), f"{round(v * 100)} %", at + 0.6, t.duration - at - 0.6,
              Box(80, y + 100, max(bw, 260) - 30, 110), "Archivo Black", 60, "#FFFFFF" if v > 0.25 else "#7C2D12",
              weight=400, align="right", anim_in=tanim("fade", duration=0.3), name=f"Porcentaje {i + 1}")
    song(t, "fun", 3, 0.7)
    return t


def calle_adivina_edad():
    t = _t(tall, "yt-calle-adivina-edad", "¿Cuántos años tengo?", "Guess my age", 45, 10.0,
           CALLE + ["adivina la edad", "guess my age", "reto"], thumb_at=8.6, background="#111111")
    tr = t.track("video", "Personas")
    plan_ = [("portrait-06", 0.2, 2.2, "Tú"), ("man-01", 2.4, 1.6, "Persona 1"), ("y4-calle-04", 4.0, 1.6, "Persona 2"),
             ("y4-calle-01", 5.6, 1.6, "Persona 3"), ("portrait-06", 7.2, 2.8, None)]
    prev = None
    for i, (s, at, d, lab) in enumerate(plan_):
        mo = [(0, {"s": 1.1}, "snap"), (0.25, {}, "linear"), (d, {"s": 1.05})]
        if lab is None:
            c = t.photo(tr, s, at, d, t.full, mo, reuse="p1")
        else:
            c = _v(t, s, at, d, motion=mo, label="Tu video" if lab == "Tú" else lab, track=tr)
        prev = c
    shade_top(t, 520, 0.6)
    label(t, t.track("text", "Pregunta"), "¿CUÁNTOS AÑOS\nCREES QUE TENGO?", 0.2, 2.2, Box(40, 1300, 1000, 300), "Anton",
          110, "#FFFFFF", weight=400, line=1.0, layers=outlined("#FFFFFF", 8), anim_in=tanim("stamp", duration=0.25),
          name="Pregunta")
    for i, g in enumerate(["¿25?", "¿31?", "¿22?"]):
        at = 2.4 + i * 1.6 + 0.2
        t.solid(t.track("shape", "Adivina"), "#FFFFFF", at, 1.3, centered(540, 1450, 460, 230),
                [(0, {"s": 0.0}, "back"), (0.3, {})], kind="speech-bubble",
                layers=[shadow("#000000", 0, 10, 24, 0.4), fill("#FFFFFF"), no_stroke()])
        label(t, t.track("text", "Adivina"), g, at, 1.3, centered(540, 1430, 460, 180), "Anton", 120, "#111111",
              weight=400, motion=[(0, {"s": 0.0}, "back"), (0.3, {})], name=f"Respuesta {i + 1}")
    label(t, t.track("text", "Edad"), "TENGO 38", 7.4, 2.6, Box(40, 1280, 1000, 300), "Anton", 210, "#FFD400",
          weight=400, layers=outlined("#FFD400", 12, dy=12), anim_in=tanim("stamp", duration=0.25), name="Edad real")
    label(t, t.track("text", "Marca"), "ADIVINA LA EDAD", 0.0, t.duration, Box(60, 150, 960, 100), "Archivo Black", 56,
          "#FFFFFF", weight=400, spacing=6, name="Título")
    burst(t, ["😱", "😳", "🤯"], 7.45, 540, 1250, seed=45)
    shake(t, [7.4], 0.5, 0.3)
    song(t, "suspense", 4, 0.7)
    return t


def calle_primera_cita():
    people = ["portrait-08", "man-02", "y4-calle-07", "man-05"]
    said = ["«El que invita, paga.»", "«Mitad y mitad, siempre.»", "«¡Yo pago, sin problema!»", "«Depende de la cita…»"]
    tags = ["Lucía, 25", "Pablo, 30", "Ana, 28", "Iván, 33"]
    each = 2.3
    t = _t(tall, "yt-calle-primera-cita", "¿Quién paga en la primera cita?", "Who pays on a first date?", 46,
           0.4 + each * 4 + 0.3, CALLE + ["citas", "dating", "amor"], thumb_at=0.4 + each * 2 + 1.7,
           background="#FFE4EC")
    bg(t, "#FFE4EC")
    cuts(t, people, 0.4, each, box=Box(80, 430, 920, 1140), transition="slide_up", tdur=0.2)
    outline(t, t.track("shape", "Marco"), "#FF3D7F", 14, 0.4, t.duration - 0.4, Box(80, 430, 920, 1140))
    label(t, t.track("text", "Pregunta"), "¿Quién paga en la\nprimera cita? 💸", 0.0, t.duration, Box(40, 130, 1000, 260),
          "Lilita One", 92, "#C2185B", weight=400, line=1.0, anim_in=tanim("bounce", duration=0.5), name="Pregunta")
    for i in range(4):
        at = 0.6 + i * each
        d = each - 0.3
        rrect(t, t.track("shape", "Respuesta"), "#FFFFFF", at, d, Box(120, 1450, 840, 170), 40, pop(0, 0.35),
              layers=[shadow("#C2185B", 0, 10, 0, 1.0), fill("#FFFFFF"), no_stroke()])
        label(t, t.track("text", "Respuesta"), said[i], at, d, Box(140, 1450, 800, 170), "Poppins", 60, "#C2185B",
              weight=800, motion=pop(0, 0.35), name=f"Respuesta {i + 1}")
        pill(t, t.track("shape", "Nombre"), "#FF3D7F", at + 0.1, d - 0.1, Box(120, 1380, 300, 64), slide_in(dx=-420))
        label(t, t.track("text", "Nombre"), tags[i], at + 0.1, d - 0.1, Box(120, 1380, 300, 64), "Poppins", 36,
              "#FFFFFF", weight=800, motion=slide_in(dx=-420), name=f"Nombre {i + 1}")
    dots(t, ["#FF3D7F", "#FF8FB1"], 10, 0.4, t.duration - 0.4, seed=46, size=(30, 60), kinds=("heart",), drift=120,
         area=Box(0, 1600, 1080, 300))
    song(t, "romantic", 2, 0.7)
    return t


def calle_rapido():
    people = ["y4-calle-03", "man-01", "portrait-02", "y4-calle-06", "elderly-04", "portrait-05"]
    words = [("FELIZ", "#FFE600"), ("CURIOSO", "#3CFF8F"), ("INTENSA", "#FF4D6D"), ("TRANQUILO", "#5BC0EB"),
             ("SABIA", "#FFB800"), ("LOCA 😂", "#C084FC")]
    each = 1.0
    t = _t(tall, "yt-calle-rapido", "Descríbete en una palabra", "Describe yourself in one word", 47,
           0.6 + each * 6 + 0.4, CALLE + ["una palabra", "one word", "ronda rápida"], thumb_at=0.6 + each * 2 + 0.7,
           background="#000000")
    label(t, t.track("text", "Intro"), "DESCRÍBETE EN\nUNA PALABRA", 0.0, 0.7, Box(40, 700, 1000, 420), "Anton", 140,
          "#FFFFFF", weight=400, line=0.95, anim_in=tanim("stamp", duration=0.2), name="Pregunta")
    cuts(t, people, 0.6, each)
    for i, (w, c) in enumerate(words):
        at = 0.6 + i * each + 0.15
        label(t, t.track("text", "Palabra"), w, at, each - 0.15 if i < 5 else t.duration - at, Box(40, 1250, 1000, 260),
              "Anton", 190, c, weight=400, layers=outlined(c, 12, dy=12), anim_in=tanim("stamp", duration=0.15),
              name=f"Palabra {i + 1}")
    label(t, t.track("text", "Pregunta fija"), "DESCRÍBETE EN UNA PALABRA", 0.6, t.duration - 0.6,
          Box(40, 160, 1000, 110), "Anton", 72, "#FFFFFF", weight=400, layers=outlined("#FFFFFF", 6, dy=6),
          editable=False)
    punch(t, [0.6 + k * each for k in range(6)], 0.3, 0.18)
    song(t, "electro", 1, 0.8)
    return t


def calle_documental_h():
    people = ["h-elderly-02", "y4-calle-h-02", "h-portrait-04"]
    each = 3.6
    t = _t(wide, "yt-calle-documental-h", "Entrevista documental", "Documentary street interview", 48,
           1.8 + each * 3 + 0.4, CALLE + ["documental", "documentary", "16:9"], thumb_at=1.8 + each + 2.3,
           background="#000000")
    label(t, t.track("text", "Título"), "¿Qué te hace feliz?", 0.2, 1.6, Box(160, 380, 1600, 320), "Cormorant Garamond",
          120, "#F5EBDD", weight=500, italic=True, anim_in=tanim("blur-in", duration=0.7),
          anim_out=tanim("fade", duration=0.3), name="Pregunta")
    cuts(t, people, 1.8, each, transition="crossfade", tdur=0.7, punch_in=False, zoom=1.05)
    t.adjust([effect("cinematic_grade", strength=0.55), effect("stylize.film_grain", amount=0.2)], 1.8, name="Cine")
    letterbox(t, 2.39, 1.8)
    names = [("Elena Paz", "maestra jubilada"), ("Sara Okafor", "arquitecta"), ("Daniel Ríos", "ciclista")]
    said = ["«Un café por la mañana, sin prisa.»", "«Cuando un proyecto por fin sale bien.»",
            "«Salir a rodar con mis amigos.»"]
    for i, (n, info) in enumerate(names):
        at = 1.8 + i * each + 0.6
        d = each - 0.9
        line(t, t.track("shape", "Línea"), "#F5EBDD", at, d, Box(120, 690, 4, 120), grow="y")
        label(t, t.track("text", "Nombre"), n, at + 0.1, d - 0.1, Box(150, 680, 900, 80), "Cormorant Garamond", 64,
              "#F5EBDD", weight=600, align="left", anim_in=tanim("fade", duration=0.5), name=f"Nombre {i + 1}")
        label(t, t.track("text", "Dato"), info, at + 0.3, d - 0.3, Box(150, 755, 900, 60), "Montserrat", 34, "#D9C7A8",
              weight=500, align="left", spacing=4, case="upper", anim_in=tanim("fade", duration=0.5),
              name=f"Dato {i + 1}")
        label(t, t.track("text", "Respuesta"), said[i], at + 0.5, d - 0.5, Box(260, 860, 1400, 80), "Cormorant Garamond",
              54, "#FFFFFF", weight=500, italic=True, anim_in=tanim("fade", duration=0.6), name=f"Respuesta {i + 1}")
    song(t, "calm", 1, 0.65)
    return t


def calle_termina_cancion():
    people = ["y4-calle-04", "man-03", "portrait-07"]
    each = 3.0
    t = _t(tall, "yt-calle-termina-cancion", "Termina la canción", "Finish the lyric", 49, 0.3 + each * 3 + 0.3,
           CALLE + ["canción", "song", "karaoke"], thumb_at=0.3 + each * 2 + 2.3, background="#2E1065")
    bg_gradient(t, [(0, "#2E1065"), (1, "#DB2777")], angle=135)
    cuts(t, people, 0.3, each, box=Box(90, 560, 900, 1000), transition="spin", tdur=0.3)
    outline(t, t.track("shape", "Marco"), "#FFFFFF", 10, 0.3, t.duration - 0.3, Box(90, 560, 900, 1000))
    label(t, t.track("text", "Título"), "TERMINA LA CANCIÓN 🎤", 0.0, t.duration, Box(40, 140, 1000, 120), "Lilita One",
          84, "#FFFFFF", weight=400, anim_in=tanim("bounce", duration=0.5), name="Título")
    label(t, t.track("text", "Letra"), "«y bajo la luna yo te ____»", 0.2, t.duration - 0.2, Box(40, 300, 1000, 200),
          "Poppins", 68, "#FDE68A", weight=800, anim_in=tanim("typewriter", duration=1.0, unit="character"),
          name="Letra")
    picks = [("«…te canté»", False), ("«…te esperé»", False), ("«…te encontré»", True)]
    for i, (a, ok) in enumerate(picks):
        at = 0.3 + i * each + 1.0
        d = each - 1.1 if i < 2 else t.duration - at
        c = "#22C55E" if ok else "#EF4444"
        rrect(t, t.track("shape", "Respuesta"), c, at, d, Box(140, 1600, 800, 140), 70, pop(0, 0.35))
        label(t, t.track("text", "Respuesta"), a + (" ✓" if ok else " ✗"), at, d, Box(140, 1600, 800, 140), "Poppins",
              62, "#FFFFFF", weight=800, motion=pop(0, 0.35), name=f"Respuesta {i + 1}")
    confetti(t, ["#FDE68A", "#FFFFFF", "#22C55E"], 0.3 + 2 * each + 1.0, each - 0.6, seed=49, lanes=3, density=0.25)
    song(t, "upbeat", 6, 0.7)
    return t


def calle_precio():
    t = _t(tall, "yt-calle-precio", "¿Cuánto cuesta esto?", "Guess the price", 50, 10.0,
           CALLE + ["precio", "price", "adivina"], thumb_at=9.0, background="#052E16")
    bg_gradient(t, [(0, "#052E16"), (1, "#14532D")], angle=90)
    card = Box(240, 130, 600, 600)
    rrect(t, t.track("shape", "Producto"), "#FFFFFF", 0.2, 9.8, Box(card.x - 14, card.y - 14, card.w + 28, card.h + 28),
          40, pop(0, 0.45), layers=[shadow("#000000", 0, 16, 36, 0.5), fill("#FFFFFF"), no_stroke()])
    c = _v(t, "coffee-01", 0.2, 9.8, card, pop(0, 0.45), label="Foto del producto", name="Producto")
    round_mask(t, c, 28)
    label(t, t.track("text", "Pregunta"), "¿CUÁNTO CUESTA ESTO?", 0.4, 9.6, Box(40, 760, 1000, 130), "Anton", 100,
          "#FFFFFF", weight=400, anim_in=tanim("stamp", duration=0.25), name="Pregunta")
    people = ["portrait-03", "man-04", "y4-calle-04"]
    guesses = ["$ 3", "$ 12", "$ 6"]
    cuts(t, people, 1.0, [2.2, 2.2, 5.6], box=Box(0, 930, 1080, 990), name="Personas")
    for i, g in enumerate(guesses):
        at = 1.3 + i * 2.2
        d = 1.8 if i < 2 else 2.1
        pill(t, t.track("shape", "Precio"), "#FFFFFF", at, d, Box(620, 1720, 400, 130), pop(0, 0.3))
        label(t, t.track("text", "Precio"), g, at, d, Box(620, 1720, 400, 130), "Anton", 92, "#14532D", weight=400,
              motion=pop(0, 0.3), name=f"Respuesta {i + 1}")
    label(t, t.track("text", "Precio real"), "PRECIO REAL: $ 4,50", 7.8, 2.2, Box(40, 1280, 1000, 220), "Anton", 120,
          "#FDE047", weight=400, layers=outlined("#FDE047", 10), anim_in=tanim("stamp", duration=0.25),
          rotation=keys([(0, -4.0)]), name="Precio real")
    flash(t, 7.8, 0.3, peak=0.7)
    mic(t, 150, 1580, 0.6, flag="#22C55E", t0=1.0)
    song(t, "jazz", 2, 0.7)
    return t


def calle_parejas_h():
    t = _t(wide, "yt-calle-parejas-h", "Preguntas a parejas en la calle", "Couples street questions 16:9", 51, 10.0,
           CALLE + ["parejas", "couples", "16:9"], thumb_at=4.0, background="#1F0A1A")
    qs = [("¿Quién cocina mejor?", "👉 ÉL", "👈 ELLA"), ("¿Quién llega tarde siempre?", "👈 ELLA", "👈 ELLA")]
    tr = t.track("video", "Parejas")
    a = _v(t, "h-couple-01", 0, 5.2, motion=kb(5.2, 1.0, 1.08), label="Pareja 1", track=tr)
    b = _v(t, "h-couple-03", 5.0, 5.0, motion=kb(5.0, 1.08, 1.0), label="Pareja 2", track=tr)
    t.transition(tr, a, b, "glass_wipe", 0.4)
    shade_top(t, 380, 0.6)
    for i, (q, x1, x2) in enumerate(qs):
        at = 0.3 + i * 5.0
        d = 4.6 if i == 0 else t.duration - at
        label(t, t.track("text", "Pregunta"), q, at, d, Box(60, 50, 1800, 140), "Lilita One", 100, "#FFFFFF", weight=400,
              layers=outlined("#FFFFFF", 7, dy=7), anim_in=tanim("pop", duration=0.3), name=f"Pregunta {i + 1}")
        for k, (x, txt, c) in enumerate([(380, x1, "#FF4F9A"), (1540, x2, "#22D3EE")]):
            pill(t, t.track("shape", "Respuesta"), c, at + 1.3 + k * 0.5, d - 1.3 - k * 0.5, centered(x, 900, 420, 130),
                 pop(0, 0.35))
            label(t, t.track("text", "Respuesta"), txt, at + 1.3 + k * 0.5, d - 1.3 - k * 0.5, centered(x, 900, 420, 130),
                  "Lilita One", 72, "#FFFFFF", weight=400, motion=pop(0, 0.35), name=f"Respuesta {i * 2 + k + 1}")
    burst(t, ["😂", "❤️", "😂"], 7.6, 960, 700, seed=51)
    song(t, "romantic", 1, 0.7)
    return t


def calle_tv_retro_h():
    people = ["y4-calle-h-04", "h-man-03", "y4-calle-h-05"]
    each = 3.0
    t = _t(wide, "yt-calle-tv-retro-h", "La voz del barrio (TV retro)", "Retro TV street interview", 52,
           0.4 + each * 3 + 0.3, CALLE + ["retro", "tv", "16:9"], thumb_at=0.4 + each + 2.0, background="#E9D8A6")
    bg(t, "#E9D8A6")
    tv = Box(240, 80, 1180, 920)
    rrect(t, t.track("shape", "Televisor"), "#7F4F24", 0, t.duration, tv, 60,
          layers=[shadow("#000000", 0, 20, 40, 0.45), gradient([(0, "#9C6644"), (1, "#5E3A1C")], angle=90),
                  no_stroke()])
    scr = Box(300, 140, 860, 650)
    rrect(t, t.track("shape", "Televisor"), "#111111", 0, t.duration, Box(scr.x - 16, scr.y - 16, scr.w + 32,
                                                                          scr.h + 32), 70)
    clips = cuts(t, people, 0.4, each, box=scr, transition="dip", tdur=0.3, punch_in=False)
    for c in clips:
        round_mask(t, c, 50)
    t.adjust([effect("stylize.vhs", noise=24, chroma=3, saturation=0.9)], name="VHS")
    for k, y in enumerate([260, 460]):
        t.solid(t.track("shape", "Perilla"), "#2B1A0E", 0, t.duration, centered(1290, y, 120, 120), kind="ellipse",
                layers=[gradient([(0, "#D4A373"), (1, "#3B2414")], angle=90), no_stroke()])
    t.solid(t.track("shape", "Parlante"), "#3B2414", 0, t.duration, Box(1220, 600, 140, 180), radius=16,
            kind="rounded-rectangle", alpha=0.85)
    for k in range(5):
        t.solid(t.track("shape", "Parlante"), "#1A0F07", 0, t.duration, Box(1235, 620 + k * 32, 110, 10), radius=5,
                kind="rounded-rectangle")
    label(t, t.track("text", "Título"), "LA VOZ DEL BARRIO", 0.0, t.duration, Box(300, 850, 860, 110), "Righteous", 64,
          "#FFE8B0", weight=400, spacing=6, anim_in=tanim("flicker-in", duration=0.6), name="Título")
    mic(t, 1640, 380, 1.3, flag="#E76F51", flag_text="VOZ\nTV", motion=[(0, {"dx": 500}, "out"), (0.6, {})])
    names = ["Don Raúl, 66", "Inés, 31", "Beto, 45"]
    for i, n in enumerate(names):
        at = 0.6 + i * each
        rrect(t, t.track("shape", "Nombre"), "#E76F51", at, each - 0.4, Box(330, 690, 440, 76), 8, slide_in(dx=-500))
        label(t, t.track("text", "Nombre"), n, at, each - 0.4, Box(330, 690, 440, 76), "Righteous", 44, "#FFFFFF",
              weight=400, motion=slide_in(dx=-500), name=f"Nombre {i + 1}")
    song(t, "jazz", 3, 0.7)
    return t


def calle_pregunta_del_dia():
    people = ["man-02", "y4-calle-07", "portrait-01"]
    said = ["«Aprender a cocinar de verdad.»", "«Viajar sola por primera vez.»", "«Dormir ocho horas, ja ja.»"]
    each = 2.6
    t = _t(tall, "yt-calle-pregunta-del-dia", "La pregunta del día", "Question of the day", 53, 0.3 + each * 3 + 2.4,
           CALLE + ["pregunta del día", "question of the day", "serie"], thumb_at=0.3 + each + 1.9,
           background="#FFD400")
    cuts(t, people, 0.3, each, transition="wipe_left", tdur=0.25)
    shade_bottom(t, 700, 0.6)
    t.solid(t.track("shape", "Cabecera"), "#FFD400", 0, 0.3 + each * 3, Box(0, 0, 1080, 420), slide_in(dy=-420))
    label(t, t.track("text", "Cabecera"), "PREGUNTA DEL DÍA #12", 0.1, 0.2 + each * 3, Box(60, 120, 960, 90),
          "Archivo Black", 58, "#111111", weight=400, align="left", name="Serie")
    label(t, t.track("text", "Pregunta"), "¿Qué meta tienes este año?", 0.2, 0.1 + each * 3, Box(60, 210, 960, 180),
          "Montserrat", 70, "#111111", weight=900, align="left", line=1.05,
          anim_in=tanim("rise-by-word", duration=0.35, unit="word"), name="Pregunta")
    items = [(said[i], 0.6 + i * each, each - 0.5) for i in range(3)]
    answers(t, items, Box(60, 1380, 960, 240),
            kara("Montserrat", 74, "#FFFFFF", "#FFD400", layers=outlined("#FFFFFF", 6, dy=5), case="none",
                 weight=900, inn="pop", loop=None))
    end = 0.3 + each * 3
    t.solid(t.track("shape", "Cierre"), "#FFD400", end, t.duration - end, t.full, slide_in(dy=-1920, length=0.4))
    mic(t, 540, 520, 1.6, flag="#111111", flag_text="TU CANAL", t0=end + 0.2,
        motion=[(0, {"dy": 1400}, "out"), (0.5, {})])
    label(t, t.track("text", "Cierre"), "¿Y tú qué dirías?\nComenta 👇", end + 0.4, t.duration - end - 0.4,
          Box(40, 1300, 1000, 320), "Archivo Black", 96, "#111111", weight=400, line=1.05,
          anim_in=tanim("rise-by-word", duration=0.35, unit="word"), name="Cierre")
    song(t, "upbeat", 7, 0.7)
    return t


CALLES = [calle_que_opinas, calle_a_que_te_dedicas, calle_verdadero_falso, calle_trivia, calle_consejo,
          calle_mic_grande, calle_noticiero_h, calle_vs, calle_ranking, calle_adivina_edad, calle_primera_cita,
          calle_rapido, calle_documental_h, calle_termina_cancion, calle_precio, calle_parejas_h, calle_tv_retro_h,
          calle_pregunta_del_dia]

TEMPLATES = SUBS + REACS + CALLES
