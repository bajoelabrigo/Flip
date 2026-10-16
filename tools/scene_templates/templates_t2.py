"""Trend batch 2 (2026-10-15): see BRIEF.md, section «Las 100 de tendencia».

Ediciones de tendencia: velocity, cortes y transiciones al ritmo, cámara lenta con letra, photo dump,
resúmenes del mes, zoom 3D, VHS, glitch, caleidoscopio, pantallas divididas, duotono, «este o este»,
glow up… 120 BPM (1 golpe = 0,5 s) unless a template says otherwise.
"""

from __future__ import annotations

import math
import random

from scene import (FULL, Box, Template, Track, beat, centered, effect, fill, glow, gradient, keys, no_stroke,
                   shadow, stroke, tanim, text_style)
from templates_reels import letterbox


def tidy(make):
    """Splits any track whose clips overlap in time (texts that share a track, falling shapes) into
    stacked tracks, so every track keeps one clip at a time as FORMAT.md asks."""
    def build() -> Template:
        t = make()
        out: list[Track] = []
        for tr in t.tracks:
            out.append(tr)
            if tr.lanes or tr.transitions or len(tr.clips) < 2:
                continue
            rows: list[list[dict]] = []
            for clip in sorted(tr.clips, key=lambda c: c["timelineStartUs"]):
                row = next((r for r in rows if r[-1]["timelineStartUs"] + r[-1]["timelineDurationUs"]
                            <= clip["timelineStartUs"]), None)
                if row is None:
                    rows.append([clip])
                else:
                    row.append(clip)
            tr.clips = rows[0]
            for j, row in enumerate(rows[1:], start=2):
                extra = Track(type=tr.type, name=f"{tr.name} {j}")
                extra.clips = row
                extra.extra = dict(tr.extra)
                out.append(extra)
        t.tracks = out
        return t
    build.__name__ = make.__name__
    build.__doc__ = make.__doc__
    return build


def spikes(times: list[float], peak: float, length: float = 0.15) -> dict:
    """A keyframed spike at each time that falls back to 0 and holds there (the effect stays off
    between hits instead of ramping to the next peak)."""
    pts: list[tuple] = []
    if times[0] > 0:
        pts.append((0.0, 0.0, "hold"))
    for t in times:
        pts += [(t, peak, "out"), (t + length, 0.0, "hold")]
    return keys(pts)


def punch(dur: float, peak: float = 1.18, settle: float = 0.2, end: float = 1.0) -> list:
    return [(0, {"s": peak}, "snap"), (settle, {"s": 1.0}, "linear"), (dur, {"s": end})]


def rot(deg: float) -> dict:
    return keys([(0, deg)])


# --- 1. Velocity ----------------------------------------------------------------------------------


def velocity_al_ritmo() -> Template:
    """Speed-ramp feel: each shot punches in, eases, then accelerates into the next cut; lime speed
    lines whip across on every cut."""
    t = Template("velocity-al-ritmo", "Velocity al ritmo", "Velocity on the beat", "reels", 8.0,
                 order=1100, tags=["velocity", "velocidad", "ritmo", "moda", "tendencia"], thumb_at=4.1,
                 background="#000000")
    photos = t.track("video", "Tomas")
    samples = ["fashion-02", "portrait-01", "man-06", "fashion-04", "portrait-06", "fashion-03", "portrait-08",
               "man-05"]
    for i, sample in enumerate(samples):
        t.photo(photos, sample, i * 1.0, 1.0, FULL,
                [(0, {"s": 1.34}, "snap"), (0.22, {"s": 1.06}, "linear"), (0.7, {"s": 1.03}, "in"),
                 (1.0, {"s": 1.26})], label=f"Toma {i + 1}",
                effects=[effect("color.basic", contrast=0.22, saturation=0.1)])
    cuts = [float(k) for k in range(8)]
    trail_pts: list[tuple] = [(0.0, 0.0, "hold")]
    for k in range(8):
        trail_pts += [(k + 0.72, 0.0, "in"), (k + 0.98, 0.75, "out"), (k + 1.14, 0.0, "hold")]
    t.adjust([effect("zoom_pulse", animated={"punch": spikes(cuts, 0.6, 0.2)}, blur=0.6),
              effect("motion_trail", animated={"amount": keys(trail_pts)}, angle=0.25, length=0.7),
              effect("stylize.vignette", amount=0.45)], name="Velocidad")
    rng = random.Random(21)
    for lane in range(3):
        lines = t.track("shape", f"Líneas {lane + 1}")
        for k in range(1, 8):
            y = rng.uniform(220, 1700)
            t.solid(lines, "#C6FF00", k - 0.2 + lane * 0.03, 0.3, Box(1100, y, rng.uniform(380, 640), 7),
                    [(0, {}, "in"), (0.3, {"dx": -1900})], layers=[glow("#C6FF00", 14, 0.8), fill("#C6FF00"),
                                                                    no_stroke()])
    words = t.track("text", "Textos")
    t.text(words, "SIN FRENOS", 0.0, 2.0, Box(30, 760, 1020, 400),
           text_style("Staatliches", 210, [shadow("#000000", 0, 12, 0, 0.9), stroke(6, "#000000"), fill("#C6FF00")],
                      weight=400, spacing=4, line=0.9, anim_in=tanim("zoom-out", duration=0.4, ease="easeOut"),
                      anim_out=tanim("fade-scale", duration=0.25)), label="Título")
    t.text(words, "SIN FRENOS", 6.0, 2.0, Box(30, 760, 1020, 400),
           text_style("Staatliches", 210, [shadow("#000000", 0, 12, 0, 0.9), stroke(6, "#000000"), fill("#C6FF00")],
                      weight=400, spacing=4, line=0.9, anim_in=tanim("stamp", duration=0.3)), editable=False)
    t.text(words, "@tuusuario", 0.3, 7.7, Box(60, 1720, 960, 90),
           text_style("Inter", 44, [shadow("#000000", 0, 3, 10, 0.6), fill("#FFFFFF")], weight=700, spacing=3,
                      anim_in=tanim("fade", duration=0.5)), label="Usuario")
    t.song("city-run", 0.0, 0.9)
    return t


# --- 2. Transitions on the beat --------------------------------------------------------------------


def transiciones_al_ritmo() -> Template:
    """Ten shots, one every two beats, each joined by a fast blur/zoom transition centred on the beat."""
    t = Template("transiciones-al-ritmo", "Transiciones al ritmo", "Beat-synced transitions", "reels", 10.0,
                 order=1105, tags=["transiciones", "ritmo", "amigos", "finde", "tendencia"], thumb_at=1.4)
    photos = t.track("video", "Tomas")
    samples = ["friends-03", "friends-08", "friends-09", "friends-11", "friends-12", "friends-05", "friends-04",
               "friends-10", "beach-03", "friends-06"]
    clips = []
    for i, sample in enumerate(samples):
        drift = 40 if i % 2 else -40
        clips.append(t.photo(photos, sample, i * beat(2), beat(2), FULL,
                             [(0, {"s": 1.12, "dx": drift}, "out"), (beat(2), {"s": 1.02, "dx": -drift})],
                             label=f"Foto {i + 1}"))
    kinds = ["radial_zoom_blur", "cross_zoom_swirl", "warp_slide", "spin", "radial_zoom_blur", "rgb_displacement",
             "cross_zoom_swirl", "warp_slide", "spin"]
    for a, b, kind in zip(clips, clips[1:], kinds):
        t.transition(photos, a, b, kind, 0.3)
    t.adjust([effect("color.basic", contrast=0.12, vibrance=0.2, temperature=0.05)], name="Color")
    tag = t.track("shape", "Contador")
    t.solid(tag, "#FF3D2E", 0.0, 10.0, Box(60, 120, 190, 84), radius=42, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 6, 16, 0.35), fill("#FF3D2E"), no_stroke()])
    numbers = t.track("text", "Números")
    for i in range(10):
        t.text(numbers, f"{i + 1:02d}/10", i * beat(2), beat(2), Box(60, 120, 190, 84),
               text_style("Big Shoulders Display", 56, [fill("#FFF4E8")], weight=800, spacing=2,
                          anim_in=tanim("slide-up", duration=0.2, distance=0.5)), editable=False)
    titles = t.track("text", "Título")
    t.text(titles, "el mejor finde", 0.2, 2.6, Box(40, 1380, 1000, 360),
           text_style("Big Shoulders Display", 170, [shadow("#000000", 0, 8, 26, 0.6), fill("#FFF4E8")], weight=900,
                      case="upper", line=0.88, accent={"rule": "lastWord", "colorEnabled": True, "color": "#ffff3d2e"},
                      anim_in=tanim("rise-by-word", duration=0.45, unit="word", stagger=beat(1), rise=0.5, blur=8),
                      anim_out=tanim("fade", duration=0.3)), label="Título")
    t.song("backbeat", 0.0, 0.9)
    return t


# --- 3. Slow motion with lyrics --------------------------------------------------------------------


def camara_lenta_con_letra() -> Template:
    """Four long, slow shots melting into each other, scope bars and a lyric line under each one."""
    t = Template("camara-lenta-con-letra", "Cámara lenta con letra", "Slow motion with lyrics", "reels", 12.0,
                 order=1110, tags=["cámara lenta", "letra", "canción", "pareja", "cinemático"], thumb_at=7.6)
    photos = t.track("video", "Tomas")
    samples = ["couple-07", "beach-06", "couple-04", "nature-04"]
    clips = []
    for i, sample in enumerate(samples):
        start = i * 3.0 - (0.5 if i else 0.0)
        dur = 3.5 if i < 3 else t.duration - start
        clips.append(t.photo(photos, sample, start, dur, FULL,
                             [(0, {"s": 1.04, "dy": 20}, "linear"), (dur, {"s": 1.14, "dy": -20})],
                             label=f"Toma {i + 1}"))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "blur_dissolve", 0.5)
    t.adjust([effect("cinematic_grade", strength=0.55, teal=0.75, orange=0.45, contrast=0.35),
              effect("halation", intensity=0.6, threshold=0.6, warmth=0.85, grain=0.2),
              effect("stylize.vignette", amount=0.5)], name="Color de cine")
    letterbox(t, 250)
    lyrics = t.track("text", "Letra")
    lines = ["y si el tiempo se detiene", "que sea aquí", "contigo, otra vez", "una vez más"]
    for i, line in enumerate(lines):
        start = 0.6 + i * 2.85
        t.text(lyrics, line, start, 2.6, Box(60, 1440, 960, 200),
               text_style("Cormorant Garamond", 76, [shadow("#000000", 0, 4, 18, 0.7), fill("#F7EDE2")], weight=600,
                          italic=True, line=1.0,
                          anim_in=tanim("rise-by-word", duration=0.7, unit="word", stagger=0.18, rise=0.3, blur=10),
                          anim_out=tanim("fade", duration=0.4)), label=f"Verso {i + 1}")
    song = t.track("text", "Canción")
    t.text(song, "♪  nuestra canción", 0.8, 11.2, Box(60, 1720, 960, 80),
           text_style("Inter", 32, [fill("#F7EDE2", 0.8)], weight=500, spacing=8, case="upper",
                      anim_in=tanim("fade", duration=1.0)), label="Canción")
    t.song("i-guess-what-i-m-trying-to-say", 0.0, 0.9)
    return t


# --- 4. Cinematic photo dump ---------------------------------------------------------------------


def photo_dump_cinematico() -> Template:
    """A 4:5 print floating on black, a new one every three beats, Super 8 texture, frame counter."""
    t = Template("photo-dump-cinematico", "Photo dump cinemático", "Cinematic photo dump", "reels", 12.0,
                 order=1115, tags=["photo dump", "cine", "fotos", "aesthetic", "recuerdos"], thumb_at=6.2,
                 background="#0B0B0B")
    t.solid(t.track("shape", "Fondo"), "#0B0B0B")
    photos = t.track("video", "Fotos")
    samples = ["friends-03", "travel-07", "beach-05", "city-04", "friends-06", "cusco-01", "couple-08", "nature-01"]
    box = centered(540, 900, 900, 1125)
    each = beat(3)
    for i, sample in enumerate(samples):
        start = 0.0 if i == 0 else 0.0 + i * each
        dur = each if i < len(samples) - 1 else t.duration - start
        t.photo(photos, sample, start, dur, box, [(0, {"s": 1.05}, "out"), (0.5, {"s": 1.0}, "linear"),
                                                  (dur, {"s": 0.985})], label=f"Foto {i + 1}")
    t.adjust([effect("super8_film", intensity=0.5, grain=0.5, scratches=0.25, weave=0.3, flicker=0.15),
              effect("color.basic", fade=0.1, temperature=0.06)], name="Super 8")
    stamps = t.track("text", "Contador")
    for i in range(len(samples)):
        start = i * each
        dur = each if i < len(samples) - 1 else t.duration - start
        t.text(stamps, f"{i + 1:02d}", start, dur, Box(90, 1490, 300, 80),
               text_style("VT323", 64, [fill("#F2E8D8", 0.85)], weight=400, align="left"), editable=False)
    date = t.track("text", "Fecha")
    t.text(date, "10  15  '26", 0.0, 12.0, Box(600, 1370, 400, 70),
           text_style("VT323", 58, [glow("#FF7A1A", 10, 0.8), fill("#FF9A3C")], weight=400, align="right"),
           label="Fecha")
    titles = t.track("text", "Título")
    t.text(titles, "photo dump", 0.3, 11.7, Box(60, 110, 960, 140),
           text_style("Bodoni Moda", 104, [fill("#F2E8D8")], weight=400, italic=True,
                      anim_in=tanim("blur-in", duration=1.2, blur=24)), label="Título")
    t.text(titles, "vol. 03 — octubre", 0.8, 11.2, Box(60, 1580, 960, 70),
           text_style("Inter", 34, [fill("#F2E8D8", 0.7)], weight=500, spacing=10, case="upper",
                      anim_in=tanim("fade", duration=0.8)), label="Subtítulo")
    t.song("and-just-like-that", 0.0, 0.85)
    return t


# --- 5. «Octubre en fotos» ----------------------------------------------------------------------


def octubre_en_fotos() -> Template:
    """Monthly recap: a warm title over a blurred cover, then ten tilted prints, one per two beats,
    with falling autumn dots and a date chip that counts up."""
    t = Template("octubre-en-fotos", "Octubre en fotos", "October in photos", "reels", 13.0,
                 order=1120, tags=["octubre", "resumen", "mes", "otoño", "recap"], thumb_at=7.3,
                 background="#E8642C")
    t.solid(t.track("shape", "Fondo"), "#E8642C",
            layers=[gradient([(0, "#F08A3C"), (1, "#C9471F")], angle=120), no_stroke()])
    cover = t.track("video", "Portada")
    t.photo(cover, "friends-07", 0.0, 2.6, FULL, [(0, {"s": 1.0}, "linear"), (2.6, {"s": 1.1})], label="Portada",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=8), effect("color.basic", exposure=-0.15)])
    t.solid(t.track("shape", "Velo"), "#E8642C", 0.0, 2.6, alpha=0.5)
    rng = random.Random(10)
    for lane in range(2):
        leaves = t.track("shape", f"Hojas {lane + 1}")
        start = lane * 0.5
        while start < t.duration - 0.6:
            size = rng.uniform(22, 44)
            dur = min(rng.uniform(3.0, 4.5), t.duration - start)
            t.solid(leaves, rng.choice(["#F6D7A7", "#FFB04A", "#8C2F12"]), start, dur,
                    centered(rng.uniform(40, 1040), -50, size, size * 1.6),
                    [(0, {}, "linear"), (dur, {"dy": 2050, "dx": rng.uniform(-160, 160)})], kind="ellipse",
                    rotation=keys([(0, 0), (dur, rng.uniform(-300, 300))]))
            start += rng.uniform(0.35, 0.8)
    frames = t.track("shape", "Marcos")
    photos = t.track("video", "Fotos")
    samples = ["cusco-04", "friends-09", "beach-03", "portrait-04", "friends-12", "travel-09", "couple-06",
               "selfie-02", "friends-02", "man-01"]
    for i, sample in enumerate(samples):
        start = 2.5 + i * beat(2)
        dur = beat(2) if i < len(samples) - 1 else t.duration - start
        tilt = -4 if i % 2 else 4
        land = [(0, {"s": 1.15}, "snap"), (0.25, {}, "linear"), (dur, {"s": 1.03})]
        t.solid(frames, "#FFF6EA", start, dur, centered(540, 900, 860, 1100), land, radius=10,
                layers=[shadow("#5a1d08", 0, 18, 40, 0.4), fill("#FFF6EA"), no_stroke()], rotation=rot(tilt))
        t.photo(photos, sample, start, dur, centered(540, 880, 800, 1000), land, rotation=rot(tilt),
                label=f"Foto {i + 1}")
    chips = t.track("shape", "Fecha")
    t.solid(chips, "#2B1A12", 2.5, 10.5, centered(540, 1640, 340, 100), [(0, {"dy": 300}, "out"), (0.4, {})],
            radius=50, kind="rounded-rectangle")
    days = t.track("text", "Días")
    for i in range(len(samples)):
        start = 2.5 + i * beat(2)
        dur = beat(2) if i < len(samples) - 1 else t.duration - start
        t.text(days, f"{3 * i + 1:02d} OCT", start, dur, centered(540, 1640, 340, 100),
               text_style("Archivo Black", 54, [fill("#F6D7A7")], weight=400, spacing=3,
                          anim_in=tanim("slide-up", duration=0.2, distance=0.4)), editable=False)
    titles = t.track("text", "Título")
    t.text(titles, "Octubre", 0.15, 2.35, Box(0, 640, 1080, 320),
           text_style("Shrikhand", 200, [shadow("#5a1d08", 0, 12, 0, 0.9), fill("#FFF6EA")], weight=400,
                      anim_in=tanim("drop", duration=0.6), anim_out=tanim("fade-scale", duration=0.25)), label="Mes")
    t.text(titles, "en fotos", 0.6, 1.9, Box(0, 950, 1080, 200),
           text_style("Caveat", 140, [shadow("#5a1d08", 0, 6, 12, 0.6), fill("#2B1A12")], weight=700,
                      anim_in=tanim("typewriter", duration=0.7, unit="character"),
                      anim_out=tanim("fade", duration=0.25)), label="Subtítulo")
    t.song("happy-whistling-ukulele", 0.0, 0.85)
    return t


# --- 6. «Mis mejores fotos» carousel ------------------------------------------------------------


def mis_mejores_fotos() -> Template:
    """A carousel: the centre card is big, its neighbours peek at the sides; it slides one card every
    two seconds."""
    t = Template("mis-mejores-fotos", "Mis mejores fotos", "My best photos", "reels", 12.0,
                 order=1125, tags=["slideshow", "mejores fotos", "carrusel", "recuerdos", "pastel"], thumb_at=4.3,
                 background="#FDE2E4")
    t.solid(t.track("shape", "Fondo"), "#FDE2E4",
            layers=[gradient([(0, "#FDE2E4"), (0.5, "#F6EAF5"), (1, "#DCEBF7")], angle=150), no_stroke()])
    samples = ["portrait-04", "friends-11", "selfie-02", "beach-03", "portrait-05", "friends-08"]
    steps = [1.5 + 2.0 * k for k in range(len(samples) - 1)]
    pitch = 800

    def state(i: int, k: int) -> dict:
        off = i - k
        return {"dx": off * pitch, "s": 1.0 if off == 0 else 0.76}

    for i, sample in enumerate(samples):
        motion = [(0, state(i, 0), "inout")]
        for k, ts in enumerate(steps):
            motion += [(ts, state(i, k), "inout"), (ts + 0.6, state(i, k + 1), "inout")]
        motion[-1] = motion[-1][:2]
        frames = t.track("shape", f"Tarjeta {i + 1}")
        t.solid(frames, "#FFFFFF", 0, t.duration, centered(540, 960, 780, 1040), motion, radius=44,
                kind="rounded-rectangle", layers=[shadow("#7a5a8a", 0, 22, 50, 0.3), fill("#FFFFFF"), no_stroke()])
        photos = t.track("video", f"Foto {i + 1}")
        t.photo(photos, sample, 0, t.duration, centered(540, 960, 720, 980), motion, label=f"Foto {i + 1}")
    words = t.track("text", "Textos")
    t.text(words, "mis mejores fotos", 0.2, 11.8, Box(40, 150, 1000, 140),
           text_style("Outfit", 86, [fill("#3A3A5A")], weight=800,
                      anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.12, ease="back")), label="Título")
    t.text(words, "2026 ♡", 0.6, 11.4, Box(40, 1580, 1000, 110),
           text_style("Outfit", 60, [fill("#E26D8C")], weight=600, spacing=6,
                      anim_in=tanim("fade", duration=0.6), anim_loop=tanim("pulse", amount=4, speed=1.0)),
           label="Año")
    t.song("magic-in-the-garden", 0.0, 0.85)
    return t


# --- 7. 3D zoom / parallax ----------------------------------------------------------------------


def zoom_3d() -> Template:
    """Parallax: a blurred copy of each photo pushes in behind while the sharp card drifts the other
    way, as if the picture had depth."""
    t = Template("zoom-3d-parallax", "Zoom 3D", "3D zoom", "reels", 9.0,
                 order=1130, tags=["zoom 3d", "parallax", "viaje", "ken burns", "tendencia"], thumb_at=4.5,
                 background="#0C1424")
    back = t.track("video", "Fondo")
    cards = t.track("shape", "Sombra")
    front = t.track("video", "Primer plano")
    samples = [("city-04", "Lima"), ("cusco-01", "Cusco"), ("travel-09", "Puno")]
    backs, fronts = [], []
    card = centered(540, 900, 860, 1320)
    for i, (sample, _) in enumerate(samples):
        start = i * 3.0
        b = t.photo(back, sample, start, 3.0, FULL, [(0, {"s": 1.0}, "linear"), (3.0, {"s": 1.3})],
                    label=f"Foto {i + 1}",
                    effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=22),
                             effect("color.basic", exposure=-0.3, saturation=-0.1)])
        backs.append(b)
        move = [(0, {"s": 1.08, "dy": 40}, "linear"), (3.0, {"s": 0.94, "dy": -40})]
        t.solid(cards, "#000000", start, 3.0, card, move, radius=8,
                layers=[shadow("#000000", 0, 30, 60, 0.6), fill("#0C1424"), no_stroke()])
        fronts.append(t.photo(front, sample, start, 3.0, card, move, reuse=b["placeholderId"]))
    for track, clips in ((back, backs), (front, fronts)):
        for a, b in zip(clips, clips[1:]):
            t.transition(track, a, b, "zoom_in", 0.4)
    t.adjust([effect("stylize.vignette", amount=0.5), effect("color.basic", contrast=0.1, vibrance=0.15)],
             name="Color")
    words = t.track("text", "Lugares")
    for i, (_, place) in enumerate(samples):
        t.text(words, place, i * 3.0 + 0.3, 2.5, Box(40, 1610, 1000, 180),
               text_style("Marcellus", 130, [shadow("#000000", 0, 6, 24, 0.7), fill("#FFFFFF")], weight=400,
                          spacing=10, case="upper",
                          anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.04),
                          anim_out=tanim("fade", duration=0.3)), label=f"Lugar {i + 1}")
    t.song("infinite-wonder", 0.0, 0.85)
    return t


# --- 8. VHS -----------------------------------------------------------------------------------------


def vhs_de_los_2000() -> Template:
    """A home video: VHS noise and scanlines, PLAY in the corner, a tracking glitch on every cut."""
    t = Template("vhs-de-los-2000", "VHS de los 2000", "2000s VHS", "reels", 10.0,
                 order=1135, tags=["vhs", "retro", "2000", "nostalgia", "cámara"], thumb_at=1.3)
    photos = t.track("video", "Tomas")
    samples = ["friends-10", "friends-05", "friends-01", "man-01", "couple-02"]
    for i, sample in enumerate(samples):
        t.photo(photos, sample, i * 2.0, 2.0, FULL, [(0, {"s": 1.06, "dx": -20}, "linear"), (2.0, {"s": 1.0, "dx": 20})],
                label=f"Toma {i + 1}")
    cuts = [2.0 * k for k in range(1, 5)]
    t.adjust([effect("stylize.vhs", noise=30, chroma=4, saturation=0.8),
              effect("vhs_crt", scanlines=0.4, noise=0.25, colorBleed=4, distortion=0.25, vignette=0.35,
                     desaturation=0.1),
              effect("scanline_glitch", animated={"jitter": spikes([c - 0.05 for c in cuts], 0.9, 0.25)},
                     lineStrength=0.5, colorShift=8, speed=3)], name="VHS")
    osd = lambda size, align="left": text_style("VT323", size, [shadow("#000000", 2, 2, 0, 0.8), fill("#F2F2F2")],  # noqa: E731
                                                weight=400, align=align, spacing=2)
    hud = t.track("text", "Pantalla")
    t.text(hud, "PLAY ▶", 0.0, 10.0, Box(70, 110, 500, 100), {**osd(88), "animation": {
        "loop": tanim("flicker", intensity=0.3, speed=2)}}, label="Esquina")
    t.text(hud, "SP", 0.0, 10.0, Box(70, 1700, 300, 90), osd(76), editable=False)
    t.text(hud, "OCT. 15 2006", 0.0, 10.0, Box(500, 1700, 510, 90), osd(76, "right"), label="Fecha")
    clock = t.track("text", "Reloj")
    for k in range(10):
        t.text(clock, f"0:00:{k:02d}", float(k), 1.0, Box(570, 110, 440, 100), osd(76, "right"), editable=False)
    title = t.track("text", "Título")
    t.text(title, "mis 2000s", 0.2, 2.6, Box(40, 820, 1000, 260),
           {**osd(190, "center"), "animation": {"in": tanim("typewriter", duration=0.8, unit="character"),
                                                 "out": tanim("fade", duration=0.2)}}, label="Título")
    t.song("groovin", 0.0, 0.85)
    return t


# --- 9. Neon glitch ---------------------------------------------------------------------------------


def glitch_neon() -> Template:
    """Night colours: a purple/aqua duotone, block glitches on every beat and a flickering neon word."""
    t = Template("glitch-neon", "Glitch neón", "Neon glitch", "reels", 8.0,
                 order=1140, tags=["glitch", "neón", "fiesta", "noche", "concierto"], thumb_at=2.6,
                 background="#120024")
    photos = t.track("video", "Fotos")
    samples = ["concert-01", "portrait-01", "concert-03", "fashion-04"]
    for i, sample in enumerate(samples):
        t.photo(photos, sample, i * 2.0, 2.0, FULL, punch(2.0, 1.15, 0.2, 1.06), label=f"Foto {i + 1}")
    hits = [beat(k) for k in range(16)]
    t.adjust([effect("duotone", strength=0.6, shadowColor="#1a0033", highlightColor="#00ffc6", contrast=0.6),
              effect("block_glitch", animated={"intensity": spikes(hits, 0.8, 0.12)}, blockSize=48,
                     shiftAmount=40, frequency=0.5),
              effect("rgb_split", animated={"amount": spikes(hits, 22.0, 0.14)}, angle=90),
              effect("bloom_glow", threshold=0.7, intensity=0.6)], name="Glitch")
    words = t.track("text", "Neón")
    t.text(words, "NEÓN", 0.4, 7.6, Box(20, 700, 1040, 330),
           text_style("Monoton", 230, [glow("#FF2BD6", 40, 1.0), fill("#FFB3F2")], weight=400,
                      anim_in=tanim("glitch-in", duration=0.4), anim_loop=tanim("flicker", intensity=0.4, speed=5)),
           label="Título")
    t.text(words, "noche de fiesta", 0.9, 7.1, Box(40, 1040, 1000, 110),
           text_style("Audiowide", 62, [glow("#00FFC6", 20, 0.9), fill("#E9FFFA")], weight=400, spacing=4,
                      anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.03)),
           label="Subtítulo")
    t.song("blippy-trance", 0.0, 0.9)
    return t


# --- 10. Mirror / kaleidoscope ----------------------------------------------------------------------


def espejo_caleidoscopio() -> Template:
    """The picture folds into a mirror, then 4, 6 and 8 slices, turning slowly; one bar per photo."""
    t = Template("espejo-caleidoscopio", "Espejo caleidoscopio", "Mirror kaleidoscope", "reels", 8.0,
                 order=1145, tags=["espejo", "caleidoscopio", "efecto", "psicodélico", "tendencia"], thumb_at=6.6)
    photos = t.track("video", "Fotos")
    samples = ["concert-02", "nature-05", "travel-02", "makeup-03"]
    for i, sample in enumerate(samples):
        t.photo(photos, sample, i * 2.0, 2.0, FULL, [(0, {"s": 1.12}, "snap"), (0.25, {"s": 1.0}, "linear"),
                                                    (2.0, {"s": 1.1})], label=f"Foto {i + 1}")
    segments = keys([(0, 2, "hold"), (2.0, 4, "hold"), (4.0, 6, "hold"), (6.0, 8)])
    t.adjust([effect("kaleidoscope", animated={"segments": segments,
                                               "rotation": keys([(0, 0.0), (8.0, 0.5)]),
                                               "zoom": keys([(0, 1.0, "smooth"), (8.0, 1.35)])}),
              effect("bloom_glow", threshold=0.7, intensity=0.5),
              effect("zoom_pulse", animated={"punch": spikes([2.0, 4.0, 6.0], 0.7, 0.25)})], name="Caleidoscopio")
    words = t.track("text", "Texto")
    t.text(words, "modo espejo", 0.3, 7.7, Box(40, 820, 1000, 280),
           text_style("Righteous", 140, [shadow("#3b0a6b", 0, 8, 0, 0.9), glow("#FFFFFF", 30, 0.6), fill("#FFFFFF")],
                      weight=400, line=0.95, anim_in=tanim("pop", duration=0.5, unit="character", stagger=0.04),
                      anim_loop=tanim("pulse", amount=4, speed=2)), label="Título")
    t.song("aquarium", 0.0, 0.85)
    return t


# --- 11. Triple split screen --------------------------------------------------------------------------


def pantalla_triple() -> Template:
    """Three strips slide in from alternating sides one beat apart; halfway three new shots push them out."""
    t = Template("pantalla-triple", "Pantalla triple", "Triple split screen", "collage", 9.0,
                 order=1150, tags=["pantalla dividida", "tres", "ciudad", "collage", "calle"], thumb_at=7.0,
                 background="#000000")
    t.solid(t.track("shape", "Fondo"), "#000000")
    gap = 12
    h = (1920 - 2 * gap) / 3
    rounds = [["skate-01", "city-02", "fashion-03"], ["man-05", "cusco-04", "skate-02"]]
    for r, samples in enumerate(rounds):
        for i, sample in enumerate(samples):
            side = -1 if (i + r) % 2 == 0 else 1
            start = (0.0 if r == 0 else 4.5) + i * beat(1)
            box = Box(0, i * (h + gap), 1080, h)
            # A first-round strip stays until the second-round one has covered it.
            dur = (4.5 + i * beat(1) + 0.5 if r == 0 else t.duration) - start
            t.photo(t.track("video", f"Tira {i + 1}" + (" (2.ª parte)" if r else "")), sample, start, dur, box,
                    [(0, {"dx": side * 1080}, "out"), (0.5, {"s": 1.0}, "linear"), (dur, {"s": 1.08})],
                    label=f"Tira {i + 1}" + (" (2.ª parte)" if r else ""))
    t.adjust([effect("color.basic", contrast=0.15, saturation=-0.15), effect("stylize.film_grain", amount=0.15)],
             name="Color")
    words = t.track("text", "Textos")
    t.text(words, "un día en la ciudad", 1.6, 2.9, centered(540, 960, 1000, 140),
           text_style("Barlow Condensed", 92, [fill("#111111")], weight=800, case="upper", spacing=2,
                      box=("#FFE600", 1.0), box_pad=18, anim_in=tanim("wipe", duration=0.4, angle=0),
                      anim_out=tanim("fade", duration=0.2)), label="Título")
    t.text(words, "@tuusuario", 6.0, 3.0, centered(540, 960, 1000, 120),
           text_style("Barlow Condensed", 80, [fill("#111111")], weight=700, spacing=2,
                      box=("#FFE600", 1.0), box_pad=16, anim_in=tanim("wipe", duration=0.4, angle=0)),
           label="Usuario")
    t.song("one-step-closer", 0.0, 0.85)
    return t


# --- 12. Strobe and shake ---------------------------------------------------------------------------


def estrobo_y_temblor() -> Template:
    """A cut on every beat, black-and-white and colour in turn, a strobe and a shake on each hit."""
    t = Template("estrobo-y-temblor", "Estrobo y temblor", "Strobe and shake", "reels", 8.0,
                 order=1155, tags=["estrobo", "temblor", "ritmo", "fiesta", "energía"], thumb_at=3.3,
                 background="#000000")
    photos = t.track("video", "Fotos")
    samples = ["concert-04", "friends-04", "man-03", "gym-02"]
    for k in range(16):
        mono = k % 2 == 1
        fx = [effect("color.basic", saturation=-1.0, contrast=0.35)] if mono else [effect("color.basic", contrast=0.2, saturation=0.25)]
        t.photo(photos, samples[k % 4], beat(k), beat(1), FULL, punch(beat(1), 1.2, 0.12, 1.04),
                label=f"Foto {k % 4 + 1}", reuse=None if k < 4 else f"p{k % 4 + 1}", effects=fx)
    hits = [beat(k) for k in range(16)]
    t.adjust([effect("strobe_flash", animated={"flash": spikes(hits, 0.7, 0.1)}, tint=0.2),
              effect("beat_shake", animated={"amount": spikes(hits, 0.6, 0.25)}, rotation=0.5)], name="Golpe")
    bar = t.track("shape", "Franja")
    t.solid(bar, "#FF1E1E", 0.0, 8.0, Box(0, 1460, 1080, 210), [(0, {"sx": 0.0}, "out"), (0.4, {})])
    words = t.track("text", "Texto")
    t.text(words, "SUBE EL VOLUMEN", 0.2, 7.8, Box(30, 1460, 1020, 210),
           text_style("Bungee", 96, [shadow("#000000", 6, 6, 0, 1.0), fill("#FFFFFF")], weight=400, line=1.0,
                      anim_in=tanim("pop", duration=0.25, unit="word", stagger=beat(2))), label="Texto")
    t.song("new-hero-in-town", 0.0, 0.9)
    return t


# --- 13. Aesthetic moodboard -------------------------------------------------------------------------


def moodboard_aesthetic() -> Template:
    """A masonry board on linen: six tiles pop in a beat apart, a palette of swatches, a serif title."""
    t = Template("moodboard-aesthetic", "Moodboard aesthetic", "Aesthetic moodboard", "collage", 10.0,
                 order=1160, tags=["moodboard", "aesthetic", "otoño", "inspiración", "collage"], thumb_at=6.0,
                 background="#EFE7DC")
    t.solid(t.track("shape", "Fondo"), "#EFE7DC")
    tiles = [(60, 330, 460, 560), (60, 910, 460, 380), (60, 1310, 460, 500),
             (560, 330, 460, 380), (560, 730, 460, 560), (560, 1310, 460, 500)]
    samples = ["travel-05", "coffee-03", "cusco-01", "portrait-02", "beach-05", "nature-01"]
    order = [0, 3, 4, 1, 2, 5]
    photos = t.track("video", "Fotos")
    clips = []
    for n, i in enumerate(order):
        x, y, w, hh = tiles[i]
        start = 0.3 + n * beat(1)
        dur = t.duration - start
        clips.append((start, t.photo(t.track("video", f"Foto {i + 1}") if n else photos, samples[i], start, dur,
                                     Box(x, y, w, hh), [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"),
                                                        (dur, {"s": 1.04, "dy": -30})], label=f"Foto {i + 1}")))
    swatches = t.track("shape", "Paleta")
    for k, colour in enumerate(["#C8A27A", "#8C5E3C", "#E9D8C4", "#6F7D5C", "#2F2A26"]):
        t.solid(swatches if k == 0 else t.track("shape", f"Color {k + 1}"), colour, 3.4 + k * 0.12,
                t.duration - 3.4 - k * 0.12, centered(390 + k * 75, 262, 56, 56),
                [(0, {"s": 0.0}, "back"), (0.35, {})], kind="ellipse",
                layers=[shadow("#5B4636", 0, 4, 8, 0.25), fill(colour), no_stroke()])
    words = t.track("text", "Textos")
    t.text(words, "mood: otoño", 0.2, 9.8, Box(40, 70, 1000, 150),
           text_style("Cormorant Garamond", 108, [fill("#5B4636")], weight=600, italic=True,
                      anim_in=tanim("blur-in", duration=0.9, blur=20)), label="Título")
    t.adjust([effect("stylize.film_grain", amount=0.12), effect("color.basic", fade=0.08, temperature=0.06)],
             name="Textura")
    t.song("icicles-melting", 0.0, 0.85)
    return t


# --- 14. Duotone pop -----------------------------------------------------------------------------------


def duotono_pop() -> Template:
    """Four photos, each in its own two-colour pair, with a giant stamped word and a halftone texture."""
    t = Template("duotono-pop", "Duotono pop", "Pop duotone", "reels", 8.0,
                 order=1165, tags=["duotono", "pop art", "color", "retrato", "tendencia"], thumb_at=2.4)
    photos = t.track("video", "Fotos")
    pairs = [("#1b1464", "#ff4fa3"), ("#3a0ca3", "#ffd60a"), ("#0b3d3a", "#ff7a3d"), ("#7a0010", "#7cf5c4")]
    samples = ["portrait-07", "man-06", "selfie-03", "portrait-02"]
    for i, (sample, (dark, light)) in enumerate(zip(samples, pairs)):
        t.photo(photos, sample, i * 2.0, 2.0, FULL, punch(2.0, 1.14, 0.18, 1.05), label=f"Foto {i + 1}",
                effects=[effect("duotone", strength=0.95, shadowColor=dark, highlightColor=light, contrast=0.6)])
    t.adjust([effect("halftone_comic", strength=0.25, dotSize=5, levels=5, angle=0.15),
              effect("zoom_pulse", animated={"punch": spikes([2.0, 4.0, 6.0], 0.6, 0.2)})], name="Trama")
    words = t.track("text", "Palabras")
    for i, word in enumerate(["POP", "COLOR", "ARTE", "TÚ"]):
        size = 300 if len(word) <= 4 else 230
        t.text(words, word, i * 2.0 + 0.1, 1.9, Box(20, 1260, 1040, 420),
               text_style("Archivo Black", size, [shadow("#000000", 14, 14, 0, 1.0), stroke(8, "#000000"),
                                                  fill("#FFFFFF")], weight=400, line=0.9,
                          anim_in=tanim("stamp", duration=0.3)), label=f"Palabra {i + 1}", rotation=rot(-4))
    t.song("beat-one", 0.0, 0.9)
    return t


# --- 15. This or that ------------------------------------------------------------------------------------


def este_o_este() -> Template:
    """Two options stacked; the question sits in the seam, then the pick lights up and the other dims.
    Two rounds."""
    t = Template("este-o-este", "¿Este o este?", "This or that", "collage", 10.0,
                 order=1170, tags=["este o este", "elige", "encuesta", "pareja", "divertido"], thumb_at=3.6,
                 background="#1C1C28")
    t.solid(t.track("shape", "Fondo"), "#1C1C28")
    top_box, bottom_box = Box(0, 0, 1080, 930), Box(0, 990, 1080, 930)
    rounds = [(("beach-05", "Playa"), ("nature-05", "Montaña"), 0), (("city-04", "Ciudad"), ("cusco-01", "Pueblo"), 1)]
    tops = t.track("video", "Opción de arriba")
    bottoms = t.track("video", "Opción de abajo")
    dims = t.track("shape", "Sombra")
    for r, (a, b, pick) in enumerate(rounds):
        start = r * 5.0
        for (sample, name), box, side, lag, track in ((a, top_box, -1, 0.0, tops), (b, bottom_box, 1, 0.25, bottoms)):
            t.photo(track, sample, start + lag, 5.0 - lag, box,
                    [(0, {"dx": side * 1080}, "out"), (0.45, {}, "linear"), (5.0 - lag, {"s": 1.04})],
                    label=f"{name} ({'arriba' if box is top_box else 'abajo'})")
        loser = bottom_box if pick == 0 else top_box
        t.solid(dims, "#000000", start + 2.5, 2.5, loser, alpha=0.65, opacity=keys([(0, 0.0, "out"), (0.3, 1.0)]))
    seam = t.track("shape", "Costura")
    t.solid(seam, "#FF4FA3", 0.0, 10.0, Box(0, 930, 1080, 60), [(0, {"sx": 0.0}, "out"), (0.5, {})],
            layers=[gradient([(0, "#FF4FA3"), (1, "#3EC5FF")], angle=0), no_stroke()])
    pill = t.track("shape", "Píldora")
    t.solid(pill, "#FFFFFF", 0.3, 9.7, centered(540, 960, 560, 130), [(0, {"s": 0.0}, "back"), (0.45, {})],
            radius=65, kind="rounded-rectangle", layers=[shadow("#000000", 0, 10, 30, 0.45), fill("#FFFFFF"),
                                                         no_stroke()])
    ticks = t.track("shape", "Elegido")
    names = t.track("text", "Nombres")
    for r, (a, b, pick) in enumerate(rounds):
        start = r * 5.0
        for (sample, name), y in ((a, 790), (b, 1780)):
            t.text(names, name, start + 0.5, 4.5, Box(60, y - 70, 700, 120),
                   text_style("Lilita One", 96, [shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], weight=400,
                              align="left", anim_in=tanim("slide-up", duration=0.35)), label=f"Opción {name}")
        cy = 790 if pick == 0 else 1780
        t.solid(ticks, "#3EC5FF" if pick else "#FF4FA3", start + 2.5, 2.5, centered(960, cy - 10, 130, 130),
                [(0, {"s": 0.0}, "back"), (0.4, {})], kind="ellipse",
                layers=[glow("#FFFFFF", 24, 0.6), fill("#3EC5FF" if pick else "#FF4FA3"), no_stroke()])
    marks = t.track("text", "Visto")
    for r, (_, _, pick) in enumerate(rounds):
        cy = 790 if pick == 0 else 1780
        t.text(marks, "✓", r * 5.0 + 2.55, 2.45, centered(960, cy - 10, 130, 130),
               text_style("Lilita One", 90, [fill("#FFFFFF")], weight=400, anim_in=tanim("pop", duration=0.3)),
               editable=False)
    question = t.track("text", "Pregunta")
    t.text(question, "¿Este o este?", 0.4, 9.6, centered(540, 960, 560, 130),
           text_style("Lilita One", 72, [fill("#1C1C28")], weight=400,
                      anim_in=tanim("pop", duration=0.4, unit="character", stagger=0.03)), label="Pregunta")
    t.song("my-giant-bunny-friend", 0.0, 0.85)
    return t


# --- 16. Lyrics on the beat -------------------------------------------------------------------------------


def letra_al_ritmo() -> Template:
    """A line per photo, its words landing one per beat in tall condensed capitals."""
    t = Template("letra-al-ritmo", "Letra al ritmo", "Lyrics on the beat", "reels", 10.0,
                 order=1175, tags=["letra", "canción", "ritmo", "fiesta", "palabras"], thumb_at=3.6)
    photos = t.track("video", "Fotos")
    samples = ["concert-01", "friends-10", "concert-03", "friends-04", "beach-06"]
    for i, sample in enumerate(samples):
        t.photo(photos, sample, i * 2.0, 2.0, FULL, [(0, {"s": 1.1}, "snap"), (0.2, {"s": 1.02}, "linear"),
                                                    (2.0, {"s": 1.08})], label=f"Foto {i + 1}",
                effects=[effect("color.basic", exposure=-0.2, contrast=0.15)])
    t.adjust([effect("zoom_pulse", animated={"punch": spikes([beat(k) for k in range(20)], 0.3, 0.15)}),
              effect("stylize.vignette", amount=0.6)], name="Pulso")
    lines = ["esta noche no", "se duerme nadie", "sube la música", "que suene más", "hasta el amanecer"]
    words = t.track("text", "Letra")
    for i, line in enumerate(lines):
        t.text(words, line, i * 2.0, 2.0, Box(40, 560, 1000, 800),
               text_style("League Gothic", 250, [shadow("#000000", 0, 10, 24, 0.7), fill("#FFFFFF")], weight=400,
                          case="upper", line=0.86,
                          accent={"rule": "lastWord", "colorEnabled": True, "color": "#ffffe14d"},
                          anim_in=tanim("pop", duration=0.2, unit="word", stagger=beat(1), ease="back")),
               label=f"Verso {i + 1}")
    t.song("downtown-boogie", 0.0, 0.9)
    return t


# --- 17. Black and white to colour -------------------------------------------------------------------------


def blanco_y_negro_a_color() -> Template:
    """Each photo starts in black and white; a circle of colour opens from the middle on the drop."""
    t = Template("blanco-y-negro-a-color", "Del blanco y negro al color", "Black and white to colour", "reels", 8.0,
                 order=1180, tags=["blanco y negro", "color", "pareja", "revelación", "amor"], thumb_at=1.55)
    grey = t.track("video", "En gris")
    colour = t.track("video", "En color")
    samples = ["couple-08", "couple-07"]
    for i, sample in enumerate(samples):
        start = i * 4.0
        drift = [(0, {"s": 1.0}, "linear"), (4.0, {"s": 1.1})]
        g = t.photo(grey, sample, start, 4.0, FULL, drift, label=f"Foto {i + 1}",
                    effects=[effect("color.basic", saturation=-1.0, contrast=0.2)])
        c = t.photo(colour, sample, start, 4.0, FULL, drift, reuse=g["placeholderId"],
                    effects=[effect("color.basic", vibrance=0.3, saturation=0.1)])
        grow = [(0, 0.0, "hold"), (1.0, 0.0, "inout"), (2.0, 2.1)]
        t.mask(colour, c, "ellipse", w=0.0, h=0.0, feather=40,
               keyframes={"w": keys(grow), "h": keys([(p[0], p[1] * 1080 / 1920, *p[2:]) for p in grow])})
    flash = t.track("shape", "Destello")
    for i in range(2):
        t.solid(flash, "#FFFFFF", i * 4.0 + 1.0, 0.3, FULL, opacity=keys([(0, 0.6, "out"), (0.3, 0.0)]))
    words = t.track("text", "Textos")
    serif = lambda size, colour_: text_style("Playfair Display", size, [shadow("#000000", 0, 4, 20, 0.6),  # noqa: E731
                                                                         fill(colour_)], weight=700, italic=True)
    t.text(words, "todo era gris…", 0.2, 1.6, Box(40, 1440, 1000, 200),
           {**serif(100, "#FFFFFF"), "animation": {"in": tanim("fade", duration=0.5),
                                                   "out": tanim("fade", duration=0.2)}}, label="Antes")
    t.text(words, "y llegaste tú", 2.0, 2.0, Box(40, 1440, 1000, 200),
           {**serif(110, "#FF7A59"), "animation": {"in": tanim("rise-by-word", duration=0.5, unit="word",
                                                                 stagger=0.15)}}, label="Después")
    t.text(words, "a todo color", 5.0, 3.0, Box(40, 1440, 1000, 200),
           {**serif(120, "#FF7A59"), "animation": {"in": tanim("blur-in", duration=0.8, blur=20)}}, label="Cierre")
    t.song("alls-fair-in-love", 0.0, 0.85)
    return t


# --- 18. Sports highlights ---------------------------------------------------------------------------------


def jugadas_destacadas() -> Template:
    """Highlights with a TV feel: a score bug, a REPETICIÓN tag on the slow replay, and a goal that shakes."""
    t = Template("jugadas-destacadas", "Jugadas destacadas", "Sports highlights", "reels", 10.0,
                 order=1185, tags=["deporte", "fútbol", "highlights", "gol", "partido"], thumb_at=6.6,
                 background="#0B1F3A")
    photos = t.track("video", "Jugadas")
    samples = ["beach-01", "man-03", "gym-06", "beach-06", "gym-02"]
    plan = [(0.0, 2.0), (2.0, 1.5), (3.5, 2.5), (6.0, 2.0), (8.0, 2.0)]
    clips = []
    for i, (sample, (start, dur)) in enumerate(zip(samples, plan)):
        if i == 2:  # the replay: a slow push in
            motion = [(0, {"s": 1.0}, "linear"), (dur, {"s": 1.3})]
        else:
            motion = punch(dur, 1.16, 0.2, 1.05)
        clips.append(t.photo(photos, sample, start, dur, FULL, motion, label=f"Jugada {i + 1}",
                             effects=[effect("color.basic", contrast=0.2, vibrance=0.25)]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "push_left", 0.25)
    t.adjust([effect("strobe_flash", animated={"flash": spikes([6.0, 6.5], 0.8, 0.12)}, tint=0.1),
              effect("beat_shake", animated={"amount": spikes([6.0], 1.0, 0.6)}, rotation=0.4)], name="Gol")
    bug = t.track("shape", "Marcador")
    t.solid(bug, "#0B1F3A", 0.2, 9.8, Box(60, 110, 760, 110), [(0, {"dy": -260}, "out"), (0.5, {})], radius=18,
            kind="rounded-rectangle", alpha=0.92, layers=[shadow("#000000", 0, 6, 20, 0.4), fill("#0B1F3A", 0.92),
                                                          no_stroke()])
    t.solid(t.track("shape", "Minuto"), "#00E676", 0.2, 9.8, Box(820, 110, 200, 110),
            [(0, {"dy": -260}, "out"), (0.5, {})], radius=18, kind="rounded-rectangle")
    tag = t.track("shape", "Repetición")
    t.solid(tag, "#E53935", 3.6, 2.4, Box(60, 1600, 440, 100), [(0, {"dx": -500}, "out"), (0.35, {})])
    words = t.track("text", "Marcador")
    teko = lambda size, colour, align="center": text_style("Teko", size, [fill(colour)], weight=600,  # noqa: E731
                                                           align=align, spacing=2)
    t.text(words, "LOCAL  2 - 1  VISITA", 0.3, 9.7, Box(60, 110, 760, 110), teko(76, "#FFFFFF"), label="Marcador")
    t.text(words, "89'", 0.3, 9.7, Box(820, 110, 200, 110), teko(76, "#0B1F3A"), label="Minuto")
    rep = t.track("text", "Repetición")
    t.text(rep, "● REPETICIÓN", 3.7, 2.3, Box(60, 1600, 440, 100),
           {**teko(66, "#FFFFFF"), "animation": {"loop": tanim("flicker", intensity=0.3, speed=2)}},
           label="Etiqueta")
    goal = t.track("text", "Gol")
    t.text(goal, "¡GOOOL!", 6.0, 2.0, Box(20, 760, 1040, 380),
           text_style("Teko", 300, [shadow("#000000", 0, 14, 0, 0.9), stroke(8, "#0B1F3A"), fill("#00E676")],
                      weight=700, anim_in=tanim("stamp", duration=0.3)), label="Grito")
    t.text(goal, "MVP · #10 Tu Nombre", 8.2, 1.8, Box(40, 1560, 1000, 140),
           text_style("Teko", 96, [fill("#0B1F3A")], weight=600, box=("#00E676", 1.0), box_pad=14,
                      anim_in=tanim("slide-up", duration=0.35)), label="Jugador")
    t.song("honor-bound", 0.0, 0.9)
    return t


# --- 19. Street edit ----------------------------------------------------------------------------------------


def edicion_callejera() -> Template:
    """Concrete and orange: fast pushes between street shots, marker scribbles and tape strips."""
    t = Template("edicion-callejera", "Edición callejera", "Street edit", "reels", 9.0,
                 order=1190, tags=["skate", "calle", "urbano", "crew", "ciudad"], thumb_at=3.3)
    photos = t.track("video", "Tomas")
    samples = ["skate-01", "man-05", "city-02", "skate-02", "fashion-03", "cusco-04"]
    clips = []
    for i, sample in enumerate(samples):
        side = 60 if i % 2 else -60
        clips.append(t.photo(photos, sample, i * beat(3), beat(3), FULL,
                             [(0, {"s": 1.12, "dx": side}, "linear"), (beat(3), {"s": 1.02, "dx": -side})],
                             label=f"Toma {i + 1}"))
    kinds = ["push_left", "slide_up", "push_left", "slide_down", "push_left"]
    for a, b, kind in zip(clips, clips[1:], kinds):
        t.transition(photos, a, b, kind, 0.25)
    t.adjust([effect("color.basic", contrast=0.3, saturation=-0.35, blacks=-0.1),
              effect("stylize.film_grain", amount=0.3, grainSize=2.0)], name="Calle")
    tape = t.track("shape", "Cinta")
    t.solid(tape, "#FF6B00", 0.2, 8.8, Box(-40, 150, 760, 150), [(0, {"dx": -800}, "out"), (0.4, {})],
            rotation=rot(-5), layers=[shadow("#000000", 0, 6, 12, 0.4), fill("#FF6B00"), no_stroke()])
    tape2 = t.track("shape", "Cinta 2")
    t.solid(tape2, "#F2F2F2", 0.6, 8.4, Box(520, 1650, 620, 110), [(0, {"dx": 800}, "out"), (0.4, {})],
            rotation=rot(4), layers=[shadow("#000000", 0, 6, 12, 0.4), fill("#F2F2F2"), no_stroke()])
    words = t.track("text", "Textos")
    t.text(words, "la calle", 0.3, 8.7, Box(-20, 150, 760, 150),
           text_style("Permanent Marker", 110, [fill("#111111")], weight=400,
                      anim_in=tanim("typewriter", duration=0.5, unit="character")), label="Título", rotation=rot(-5))
    t.text(words, "skate · ciudad · crew", 0.7, 8.3, Box(520, 1650, 620, 110),
           text_style("Permanent Marker", 54, [fill("#111111")], weight=400,
                      anim_in=tanim("fade", duration=0.4)), label="Subtítulo", rotation=rot(4))
    marks = t.track("text", "Garabatos")
    for k, (x, y, s) in enumerate([(820, 420, "✕"), (90, 1300, "↗"), (880, 1240, "★")]):
        t.text(marks, s, 1.0 + k * beat(3), 8.0 - k * beat(3), centered(x, y, 200, 200),
               text_style("Permanent Marker", 140, [fill("#FF6B00")], weight=400,
                          anim_in=tanim("pop", duration=0.3), anim_loop=tanim("float", amount=0.1, speed=0.6)),
               editable=False)
    t.song("fake-it-til-you-fake-it", 0.0, 0.9)
    return t


# --- 20. Glow up ---------------------------------------------------------------------------------------------


def mi_glow_up() -> Template:
    """The «before» card, flat and grey; a burst of stars on the drop; the glowing «after» card."""
    t = Template("mi-glow-up", "Mi glow up", "My glow up", "beforeafter", 9.0,
                 order=1195, tags=["glow up", "antes y después", "maquillaje", "cambio", "belleza"], thumb_at=6.0,
                 background="#C9A7FF")
    t.solid(t.track("shape", "Fondo"), "#C9A7FF",
            layers=[gradient([(0, "#E9D7FF"), (0.6, "#C9A7FF"), (1, "#F7C6E0")], angle=160), no_stroke()])
    frames = t.track("shape", "Marcos")
    photos = t.track("video", "Fotos")
    before = [(0, {"s": 0.8, "dy": 200}, "back"), (0.5, {}, "linear"), (3.4, {"s": 1.03})]
    t.solid(frames, "#FFFFFF", 0.2, 3.3, centered(540, 900, 720, 960), before, radius=8, rotation=rot(-5),
            layers=[shadow("#5b3a8a", 0, 16, 30, 0.3), fill("#F4F0F7"), no_stroke()])
    t.photo(photos, "makeup-01", 0.2, 3.3, centered(540, 870, 660, 840), before, label="Antes", rotation=rot(-5),
            effects=[effect("color.basic", saturation=-0.85, exposure=-0.1, contrast=-0.1)])
    after = [(0, {"s": 1.25}, "snap"), (0.3, {}, "linear"), (5.5, {"s": 1.06})]
    t.solid(frames, "#FFFFFF", 3.5, 5.5, centered(540, 900, 880, 1160), after, radius=36, kind="rounded-rectangle",
            layers=[glow("#FFE7A3", 50, 0.9), fill("#FFFFFF"), no_stroke()])
    t.photo(photos, "makeup-02", 3.5, 5.5, centered(540, 900, 820, 1100), after, label="Después")
    stars = t.track("shape", "Estrellas")
    rng = random.Random(4)
    for k in range(8):
        lane = stars if k == 0 else t.track("shape", f"Estrella {k + 1}")
        angle = k * 45 + rng.uniform(-10, 10)
        dx, dy = math.cos(math.radians(angle)) * 520, math.sin(math.radians(angle)) * 700
        size = rng.uniform(70, 120)
        t.solid(lane, "#FFE7A3", 3.4, 1.0, centered(540, 900, size, size),
                [(0, {"s": 0.2}, "out"), (0.8, {"dx": dx, "dy": dy, "s": 1.0}, "in"), (1.0, {"dx": dx * 1.1, "dy": dy * 1.1, "s": 0.0})],
                kind="star", layers=[glow("#FFFFFF", 20, 0.9), fill("#FFE7A3"), no_stroke()],
                rotation=keys([(0, 0), (1.0, 120)]))
    t.solid(t.track("shape", "Destello"), "#FFFFFF", 3.45, 0.35, FULL, opacity=keys([(0, 0.85, "out"), (0.35, 0.0)]))
    t.adjust([effect("bloom_glow", threshold=0.7, intensity=0.7, blurRadius=12),
              effect("bling_sparkle", intensity=0.6, density=0.4, threshold=0.75, colorize=0.3)], 3.5, 5.5,
             name="Brillo")
    words = t.track("text", "Textos")
    t.text(words, "antes", 0.5, 3.0, Box(40, 1460, 1000, 160),
           text_style("Caveat", 110, [fill("#4A3366")], weight=700,
                      anim_in=tanim("typewriter", duration=0.5, unit="character")), label="Antes")
    t.text(words, "glow up ✨", 3.7, 5.3, Box(20, 120, 1040, 220),
           text_style("Yellowtail", 150, [glow("#FFE7A3", 30, 0.9), stroke(6, "#FFFFFF"), fill("#B04A9E")],
                      weight=400, anim_in=tanim("pop", duration=0.5, unit="character", stagger=0.04, ease="back"),
                      anim_loop=tanim("float", amount=0.1, speed=0.5)), label="Título")
    t.text(words, "después", 4.0, 5.0, Box(40, 1530, 1000, 140),
           text_style("Caveat", 100, [fill("#4A3366")], weight=700,
                      anim_in=tanim("fade", duration=0.5)), label="Después")
    t.song("adding-the-sun", 0.0, 0.85)
    return t


TEMPLATES = [tidy(make) for make in (velocity_al_ritmo, transiciones_al_ritmo, camara_lenta_con_letra, photo_dump_cinematico,
             octubre_en_fotos, mis_mejores_fotos, zoom_3d, vhs_de_los_2000, glitch_neon, espejo_caleidoscopio,
             pantalla_triple, estrobo_y_temblor, moodboard_aesthetic, duotono_pop, este_o_este, letra_al_ritmo,
             blanco_y_negro_a_color, jugadas_destacadas, edicion_callejera, mi_glow_up)]
