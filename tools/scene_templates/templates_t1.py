"""Trend batch 1 (2026-10-15): see BRIEF.md, section «Las 100 de tendencia».

Fechas especiales (category `seasonal`, order 1000–1099): Día de Muertos, Canción Criolla, Navidad,
Año Nuevo, Black Friday, Cyber Monday, San Valentín / Día de la Amistad, Día del Padre and Fiestas Patrias.
Each one has its own palette, fonts, rhythm and motion.
"""

from __future__ import annotations

import math
import random

from scene import (FULL, Box, Template, argb, beat, centered, effect, fill, glow, gradient, keys, no_stroke,
                   shadow, stroke, tanim, text_style)

# --- Helpers --------------------------------------------------------------------------------------

NO_FILL = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def rot(deg: float) -> dict:
    return keys([(0, deg)])


def ring(color: str, width: float, halo: str | None = None, dash: str | None = None) -> list[dict]:
    """A stroke-only outline (optionally dotted/dashed, with a halo)."""
    line = stroke(width, color)
    if dash:
        line["dash"] = dash
    layers = [glow(halo, 30, 0.8)] if halo else []
    return layers + [line, dict(NO_FILL)]


def spikes(times: list[float], peak: float, decay: float = 0.2) -> dict:
    """Beat spikes for zoom_pulse / beat_shake / strobe_flash / rgb_split: each key falls back to 0 and HOLDS
    there (BRIEF/CLAUDE trap: without the hold it ramps up to the next peak and washes the picture)."""
    times = sorted(times)
    pts: list[tuple] = []
    if times[0] > 0:
        pts.append((0.0, 0.0, "hold"))
    for tt in times:
        pts += [(tt, peak, "out"), (tt + decay, 0.0, "hold")]
    return keys(pts)


def grouped(motion: list[tuple], ox: float, oy: float) -> list[tuple]:
    """The motion of a part placed (ox, oy) from its group's centre, so the group scales about that centre."""
    out = []
    for p in motion:
        m = dict(p[1])
        s = m.get("s", 1.0)
        m["dx"] = m.get("dx", 0.0) + ox * (s - 1)
        m["dy"] = m.get("dy", 0.0) + oy * (s - 1)
        out.append((p[0], m) + tuple(p[2:]))
    return out


def pop(at: float = 0.0, length: float = 0.45) -> list[tuple]:
    # 0.02, not 0: the first key's box sets the photo crop, and a zero box crops nothing.
    return [(at, {"s": 0.02}, "back"), (at + length, {})]


def bobbing(enter: list[tuple], dur: float, period: float = 0.9, amp: float = 14) -> list[tuple]:
    """`enter` then a slow up/down float until `dur`."""
    out = list(enter)
    k = enter[-1][0]
    up = True
    while k + period <= dur:
        k += period
        out.append((k, {"dy": -amp if up else 0.0}, "smooth"))
        up = not up
    return out


def stripes(colors: list, fill_frac: float = 0.8, angle: float = 0.0) -> list[dict]:
    """Hard-stop gradient: n bands (colour or (colour, alpha)), each filling `fill_frac` of its slot, the rest
    transparent. angle 0 = bands side by side, 90 = bands stacked."""
    n = len(colors)
    eps = 1e-4
    stops = []
    for i, c in enumerate(colors):
        col, a = c if isinstance(c, tuple) else (c, 1.0)
        lo, hi = i / n, (i + fill_frac) / n
        stops += [(lo + (eps if i else 0.0), col, a), (min(hi, 1.0), col, a)]
        if fill_frac < 1.0:
            stops += [(hi + eps, col, 0.0), ((i + 1) / n, col, 0.0)]
    return [gradient(stops, angle=angle), no_stroke()]


def shape(t: Template, track, color: str, t0: float, dur: float, box: Box, motion=None, *, geometry: dict,
          **kw) -> dict:
    """A solid whose shapeStyle takes geometry (points, innerRatio...)."""
    clip = t.solid(track, color, t0, dur, box, motion, **kw)
    clip["shapeStyle"].update(geometry)
    return clip


def particles(t: Template, name: str, lanes: int, t0: float, t1: float, rng: random.Random, colors: list[str], *,
              kinds=("ellipse",), size=(20, 40), x=(40, 1040), y: float = -60, dy: float = 2100,
              life=(3.0, 5.0), every=(0.3, 0.7), sway: float = 100, spin: float = 0, alpha: float = 1.0,
              layers_fn=None) -> None:
    """Confetti, snow, petals or embers drifting by `dy` over their life (as feliz_cumple / para_mama do)."""
    for lane in range(lanes):
        tr = t.track("shape", f"{name} {lane + 1}")
        start = t0 + lane * every[0] * 0.7
        while start < t1 - 0.4:
            life_s = rng.uniform(*life)
            d = min(life_s, t1 - start)
            frac = d / life_s
            s = rng.uniform(*size)
            colour = rng.choice(colors)
            extra = {}
            if spin:
                extra["rotation"] = keys([(0, 0), (d, rng.uniform(-spin, spin) * frac)])
            t.solid(tr, colour, start, d, centered(rng.uniform(*x), y, s, s),
                    [(0, {}, "linear"), (d, {"dy": dy * frac, "dx": rng.uniform(-sway, sway) * frac})],
                    kind=rng.choice(kinds), alpha=alpha, radius=3,
                    layers=layers_fn(colour) if layers_fn else None, **extra)
            start += rng.uniform(*every)


# --- Día de Muertos ------------------------------------------------------------------------------

PICADO = ["#E6007E", "#FF8C00", "#FFC300", "#00B3A4", "#7B2CBF", "#43AA8B", "#FF4D8D"]


def dia_de_muertos_ofrenda() -> Template:
    """An altar: papel picado that sways, a marigold-lit frame where the faces we remember cross-fade, candles."""
    t = Template("muertos-ofrenda", "Altar: los recordamos", "Altar: in loving memory", "seasonal", 15.0,
                 order=1010, tags=["día de muertos", "todos los santos", "ofrenda", "recuerdo", "familia"],
                 thumb_at=4.2, background="#1B0B2E")
    t.solid(t.track("shape", "Fondo"), "#1B0B2E",
            layers=[gradient([(0, "#2A0E3F"), (1, "#120720")], angle=90), no_stroke()])
    sway = keys([(0, -1.2, "inout"), (3, 1.2, "inout"), (6, -1.2, "inout"), (9, 1.2, "inout"),
                 (12, -1.2, "inout"), (15, 1.2)])
    t.solid(t.track("shape", "Cordel"), "#F1E3C8", 0, 15.0, Box(-40, 64, 1160, 6), alpha=0.8, rotation=sway)
    t.solid(t.track("shape", "Papel picado"), "#E6007E", 0, 15.0, Box(-40, 70, 1160, 170),
            [(0, {"dy": -260}, "out"), (0.8, {})], layers=stripes(PICADO, 0.86), rotation=sway)
    rng = random.Random(2)
    particles(t, "Pétalos", 2, 1.0, 15.0, rng, ["#FF8C00", "#FFB703", "#FB8500"], size=(14, 26), dy=2100,
              life=(6.0, 8.0), every=(0.5, 1.1), sway=160, spin=200, alpha=0.85)
    t.text(t.track("text", "Encabezado"), "Siempre con nosotros", 0.4, 14.6, Box(40, 262, 1000, 130),
           text_style("Cinzel Decorative", 84, [shadow("#000000", 0, 4, 14, 0.5),
                                                gradient([(0, "#FFD27F"), (1, "#FF8C00")], angle=90)],
                      weight=700, anim_in=tanim("fade", duration=1.0)), label="Encabezado")
    frame = centered(540, 900, 680, 860)
    t.solid(t.track("shape", "Marco"), "#F4A259", 0.8, 14.2, frame, [(0, {"s": 0.92}, "out"), (1.0, {})],
            radius=24, kind="rounded-rectangle", layers=[glow("#FF8C00", 44, 0.7)] + ring("#F4A259", 12))
    photos = t.track("video", "Fotos")
    people = [("portrait-03", "Abuela Rosa", "1938 – 2020"), ("family-01", "Mis abuelitos", "Siempre juntos"),
              ("mother-07", "Mamá Luz", "1961 – 2023")]
    starts = [0.8, 5.5, 10.2]
    clips = []
    names = t.track("text", "Nombres")
    dates = t.track("text", "Fechas")
    for i, ((sample, name, date), start) in enumerate(zip(people, starts)):
        end = starts[i + 1] if i + 1 < len(starts) else t.duration
        clips.append(t.photo(photos, sample, start, end - start, frame,
                             [(0, {"s": 1.0}, "linear"), (end - start, {"s": 1.08})], label=f"Foto {i + 1}",
                             effects=[effect("color.basic", saturation=-0.25, temperature=0.12, fade=0.08)]))
        t.text(names, name, start + 0.4, end - start - 0.4, Box(60, 1372, 960, 120),
               text_style("Dancing Script", 96, [shadow("#000000", 0, 4, 14, 0.6), fill("#FFF4E0")], weight=700,
                          anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.04),
                          anim_out=tanim("fade", duration=0.3)), label=f"Nombre {i + 1}")
        t.text(dates, date, start + 0.8, end - start - 0.8, Box(60, 1490, 960, 60),
               text_style("Cinzel", 42, [fill("#F4A259")], weight=600, spacing=6,
                          anim_in=tanim("fade", duration=0.6), anim_out=tanim("fade", duration=0.3)),
               label=f"Fechas {i + 1}")
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 1.0)
    t.text(t.track("text", "Frase"), "Siempre en nuestro corazón", 1.6, 13.4, Box(60, 1560, 960, 100),
           text_style("Dancing Script", 62, [fill("#FFB703")], weight=600, anim_in=tanim("fade", duration=1.0)),
           label="Frase")
    # Three candles whose flames flicker.
    for k, (x, h) in enumerate([(330, 170), (540, 220), (750, 150)]):
        base = 1880
        t.solid(t.track("shape", f"Vela {k + 1}"), "#F6E7CB", 0.6, 14.4, Box(x - 36, base - h, 72, h),
                [(0, {"dy": 300}, "out"), (0.8, {})], radius=10, kind="rounded-rectangle",
                layers=[gradient([(0, "#FFF6E5"), (1, "#E8D2A6")], angle=0), no_stroke()])
        flicker = keys([(i * 0.25, 1.0 if (i + k) % 2 else 0.75, "smooth") for i in range(55)])
        t.solid(t.track("shape", f"Llama {k + 1}"), "#FFB703", 1.4, 13.6, centered(x, base - h - 36, 40, 64),
                [(0, {"s": 0.02}, "out"), (0.5, {})], kind="ellipse",
                layers=[glow("#FF8C00", 36, 0.9), gradient([(0, "#FFF3B0"), (1, "#FF8C00")], angle=90), no_stroke()],
                opacity=flicker)
    t.adjust([effect("halation", intensity=0.5, threshold=0.6, warmth=0.9, grain=0.1),
              effect("light_leak", intensity=0.25, hue=0.08, speed=0.4, softness=0.6),
              effect("stylize.vignette", amount=0.7)], name="Luz de vela")
    t.song("amazing-grace", 0.0, 0.85)
    return t


def catrina() -> Template:
    """Catrina portraits in a big round window with spinning dotted rings and paper flowers, a pulse per beat."""
    t = Template("catrina-dia-de-muertos", "Maquillaje de calavera", "Skull make-up", "seasonal", 8.0, order=1011,
                 tags=["catrina", "día de muertos", "maquillaje", "méxico", "flores"], thumb_at=2.6,
                 background="#6A0DAD")
    t.solid(t.track("shape", "Fondo"), "#E6007E",
            layers=[gradient([(0, "#FF2E93"), (0.5, "#C2007A"), (1, "#5A0B9E")], angle=120), no_stroke()])
    centre = (540, 860)
    t.solid(t.track("shape", "Aro turquesa"), "#00C2A8", 0.0, 8.0, centered(*centre, 1030, 1030),
            pop(0, 0.6), kind="ellipse", layers=ring("#00C2A8", 10, dash="dash"),
            rotation=keys([(0, 0), (8.0, -60)]))
    t.solid(t.track("shape", "Aro dorado"), "#FFB703", 0.1, 7.9, centered(*centre, 960, 960),
            pop(0, 0.6), kind="ellipse", layers=ring("#FFB703", 22, dash="dot"), rotation=keys([(0, 0), (7.9, 90)]))
    photos = t.track("video", "Fotos")
    samples = ["muertos-02", "muertos-04", "muertos-01", "muertos-03"]
    for i, sample in enumerate(samples):
        clip = t.photo(photos, sample, i * 2.0, 2.0, centered(*centre, 860, 860),
                       [(0, {"s": 1.15}, "snap"), (0.2, {"s": 1.0}, "linear"), (1.0, {"s": 1.06}, "snap"),
                        (1.2, {"s": 1.0}, "linear"), (2.0, {"s": 1.03})], label=f"Catrina {i + 1}")
        t.mask(photos, clip, "ellipse")
    flowers = [(230, 470, "#FF006E"), (860, 420, "#FFBE0B"), (170, 1230, "#FB5607"), (900, 1260, "#00C2A8")]
    for k, (x, y, colour) in enumerate(flowers):
        at = 0.3 + k * 0.15
        spin = keys([(0, 0), (8.0 - at, 120 if k % 2 else -120)])
        shape(t, t.track("shape", f"Flor {k + 1}"), colour, at, 8.0 - at, centered(x, y, 190, 190), pop(0, 0.5),
              kind="star", layers=[shadow("#3A0CA3", 0, 8, 16, 0.4), fill(colour), no_stroke()], rotation=spin,
              geometry={"points": 8, "innerRatio": 0.6})
        t.solid(t.track("shape", f"Centro {k + 1}"), "#3A0CA3", at + 0.1, 7.9 - at, centered(x, y, 62, 62),
                pop(0, 0.4), kind="ellipse")
    t.text(t.track("text", "Título"), "CALAVERA", 0.5, 7.5, Box(0, 1330, 1080, 300),
           text_style("Abril Fatface", 170, [shadow("#3A0CA3", 0, 12, 0, 1.0), fill("#FFF1E6")], weight=400,
                      spacing=6, anim_in=tanim("stamp", duration=0.4)), label="Título")
    t.text(t.track("text", "Subtítulo"), "noche de disfraces", 1.0, 7.0, Box(0, 1600, 1080, 200),
           text_style("Sacramento", 130, [shadow("#3A0CA3", 0, 4, 10, 0.6), fill("#FFB703")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.04)), label="Subtítulo")
    t.adjust([effect("zoom_pulse", animated={"punch": spikes([beat(2 * k) for k in range(8)], 0.35, 0.25)}),
              effect("bling_sparkle", intensity=0.5, density=0.4, threshold=0.75, colorize=0.4)], name="Pulso")
    t.song("magic-in-the-garden", 0.0, 0.9)
    return t


# --- Día de la Canción Criolla (Perú, 31 de octubre) ---------------------------------------------


def cancion_criolla() -> Template:
    """A vintage poster: cream paper, red double border, an oval sepia slideshow and a waltz."""
    t = Template("cancion-criolla", "Noche de música en vivo", "Live music night", "seasonal", 12.0,
                 order=1020, tags=["música en vivo", "concierto", "vals", "noche", "vintage"], thumb_at=7.2,
                 background="#F3E6CC")
    t.solid(t.track("shape", "Papel"), "#F3E6CC",
            layers=[gradient([(0, "#F7ECD6"), (1, "#E6CDA0")], angle=90), no_stroke()])
    t.solid(t.track("shape", "Borde"), "#8C1C13", 0, 12.0, Box(40, 40, 1000, 1840), layers=ring("#8C1C13", 10))
    t.solid(t.track("shape", "Borde fino"), "#8C1C13", 0.2, 11.8, Box(70, 70, 940, 1780), layers=ring("#C9A227", 3))
    for k, (x, y) in enumerate([(70, 70), (1010, 70), (70, 1850), (1010, 1850)]):
        t.solid(t.track("shape", f"Esquina {k + 1}"), "#8C1C13", 0.3 + 0.1 * k, 11.7 - 0.1 * k,
                centered(x, y, 56, 56), pop(0, 0.4), kind="diamond")
    t.text(t.track("text", "Fecha"), "este sábado", 0.3, 11.7, Box(80, 96, 920, 120),
           text_style("Cookie", 92, [fill("#8C1C13")], weight=400, anim_in=tanim("fade", duration=0.8)),
           label="Fecha")
    t.text(t.track("text", "Título"), "Noche de música en vivo", 0.6, 11.4, Box(90, 205, 900, 290),
           text_style("Yeseva One", 104, [shadow("#8C1C13", 3, 3, 0, 0.35), fill("#3E2723")], weight=400, line=1.0,
                      accent={"rule": "lastWord", "colorEnabled": True, "color": argb("#B71C1C")},
                      anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.15)), label="Título")
    oval = centered(540, 970, 700, 880)
    t.solid(t.track("shape", "Marco dorado"), "#C9A227", 0.8, 11.2, centered(540, 970, 744, 924),
            [(0, {"s": 0.9}, "out"), (0.8, {})], kind="ellipse", layers=ring("#C9A227", 4))
    t.solid(t.track("shape", "Marco"), "#8C1C13", 0.8, 11.2, oval, [(0, {"s": 0.9}, "out"), (0.8, {})],
            kind="ellipse", layers=ring("#8C1C13", 12))
    photos = t.track("video", "Fotos")
    samples = ["friends-01", "city-03", "family-01", "portrait-03"]
    clips = []
    for i, sample in enumerate(samples):
        start = 0.8 + i * 2.8
        clips.append(t.photo(photos, sample, start, 2.8, oval, [(0, {"s": 1.0}, "linear"), (2.8, {"s": 1.08})],
                             label=f"Foto {i + 1}",
                             effects=[effect("color.basic", saturation=-0.45, temperature=0.25, fade=0.15,
                                             contrast=0.1)]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.8)
    for clip in clips:
        t.mask(photos, clip, "ellipse")
    t.text(t.track("text", "Frase"), "¡Que viva la música!", 1.6, 10.4, Box(70, 1440, 940, 160),
           text_style("Cookie", 96, [fill("#8C1C13")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.03)), label="Frase")
    t.text(t.track("text", "Géneros"), "Vals · Bolero · Jazz", 2.2, 9.8, Box(70, 1610, 940, 70),
           text_style("Yeseva One", 46, [fill("#3E2723")], weight=400, spacing=6,
                      anim_in=tanim("fade", duration=0.8)), label="Géneros")
    t.text(t.track("text", "Evento"), "Música en vivo esta noche", 2.8, 9.2, Box(70, 1700, 940, 80),
           text_style("Yeseva One", 40, [fill("#F7ECD6")], weight=400, spacing=3, box=("#8C1C13", 1.0),
                      box_pad=14, box_radius=6, anim_in=tanim("pop", duration=0.4)), label="Evento")
    t.adjust([effect("super8_film", intensity=0.45, grain=0.4, scratches=0.25, weave=0.2, flicker=0.15),
              effect("stylize.vignette", amount=0.45)], name="Película")
    t.song("isolation-waltz", 0.0, 0.85)
    return t


# --- Navidad -------------------------------------------------------------------------------------


def navidad_en_familia() -> Template:
    """Warm full-screen family photos under falling snow, a golden script title and the family's name."""
    t = Template("navidad-en-familia", "Navidad en familia", "Christmas with family", "seasonal", 15.0,
                 order=1030, tags=["navidad", "familia", "diciembre", "nochebuena", "fiestas"], thumb_at=2.2)
    photos = t.track("video", "Fotos")
    samples = ["christmas-05", "christmas-04", "christmas-02", "christmas-03", "family-05"]
    clips = []
    for i, sample in enumerate(samples):
        drift = 40 if i % 2 else -40
        clips.append(t.photo(photos, sample, i * 3.0, 3.0, FULL,
                             [(0, {"s": 1.04, "dx": drift}, "linear"), (3.0, {"s": 1.14, "dx": -drift})],
                             label=f"Foto {i + 1}"))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "blur_dissolve", 0.8)
    t.solid(t.track("shape", "Sombra"), "#0B1D13", 0, 15.0, Box(0, 880, 1080, 1040),
            layers=[gradient([(0, "#0B1D13", 0.0), (0.35, "#0B1D13", 0.65), (1, "#0B1D13", 0.95)], angle=90),
                    no_stroke()])
    rng = random.Random(24)
    particles(t, "Nieve", 3, 0.0, 15.0, rng, ["#FFFFFF"], size=(10, 26), dy=2100, life=(6.0, 9.0),
              every=(0.25, 0.6), sway=90, alpha=0.9)
    gold = [shadow("#000000", 0, 6, 22, 0.9), stroke(3, "#2B1A00"),
            gradient([(0, "#FFF4C8"), (0.6, "#F2CF6B"), (1, "#D9A520")], angle=90)]
    t.text(t.track("text", "Título"), "Feliz\nNavidad", 0.5, 14.5, Box(40, 1080, 1000, 440),
           text_style("Great Vibes", 170, gold, weight=400, line=1.0, anim_in=tanim("blur-in", duration=1.2, blur=24),
                      anim_loop=tanim("breathe", amount=0.15, speed=0.4)), label="Título")
    t.text(t.track("text", "Familia"), "Familia Torres · 2026", 1.2, 13.8, Box(40, 1570, 1000, 100),
           text_style("Cormorant Garamond", 64, [shadow("#000000", 0, 3, 10, 0.6), fill("#FFF6E5")], weight=600,
                      italic=True, spacing=3,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.03)), label="Familia")
    t.text(t.track("text", "Mensaje"), "Que la magia de esta noche nos una siempre", 9.0, 6.0,
           Box(90, 130, 900, 200),
           text_style("Cormorant Garamond", 58, [shadow("#000000", 0, 3, 14, 0.7), fill("#FFF6E5")], weight=600,
                      italic=True, anim_in=tanim("fade", duration=1.0)), label="Mensaje")
    t.adjust([effect("color.basic", temperature=0.12, vibrance=0.1),
              effect("halation", intensity=0.45, threshold=0.7, warmth=0.8, grain=0.05),
              effect("stylize.vignette", amount=0.55), effect("stylize.film_grain", amount=0.12)], name="Calidez")
    t.song("icicles-melting", 0.0, 0.85)
    return t


def feliz_navidad_luces() -> Template:
    """A string of twinkling bulbs over blurred tree lights, a round portrait in gold and a bright Lobster title."""
    t = Template("feliz-navidad-luces", "Feliz Navidad con luces", "Merry Christmas lights", "seasonal", 8.0,
                 order=1031, tags=["navidad", "luces", "saludo", "tarjeta", "diciembre"], thumb_at=5.0,
                 background="#06281A")
    t.photo(t.track("video", "Fondo"), "xmaslights-01", 0, 8.0, centered(540, 960, 1240, 2200),
            [(0, {"s": 1.0}, "linear"), (8.0, {"s": 1.1})], label="Fondo de luces",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=14)])
    t.solid(t.track("shape", "Velo"), "#06281A", alpha=0.5)
    # The wire is the lower arc of a wide ellipse: it sags between (0, 230) and (1080, 230).
    t.solid(t.track("shape", "Cable"), "#173A28", 0, 8.0, Box(-300, -300, 1680, 600), kind="ellipse",
            layers=ring("#0E2418", 5))
    colours = ["#FF3B3B", "#FFC93C", "#3BE37A", "#4CC9F0"]
    for i in range(8):
        x = 80 + i * 131.4
        y = 300 * math.sqrt(1 - ((x - 540) / 840) ** 2) + 36
        colour = colours[i % 4]
        twinkle = keys([(k * 0.5, 1.0 if (k + i) % 2 else 0.45, "smooth") for k in range(17)])
        t.solid(t.track("shape", f"Foco {i + 1}"), colour, 0.1 * i, 8.0 - 0.1 * i, centered(x, y, 44, 62),
                pop(0, 0.35), kind="ellipse", layers=[glow(colour, 34, 0.95), fill(colour), no_stroke()],
                opacity=twinkle)
    t.solid(t.track("shape", "Aro"), "#E9C46A", 0.6, 7.4, centered(540, 980, 660, 660), pop(0, 0.5),
            kind="ellipse", layers=[glow("#FFE8A3", 40, 0.8), fill("#E9C46A"), no_stroke()])
    portrait = t.track("video", "Foto")
    face = t.photo(portrait, "christmas-02", 0.6, 7.4, centered(540, 980, 620, 620),
                   pop(0, 0.5) + [(7.4, {"s": 1.04})], label="Tu foto")
    t.mask(portrait, face, "ellipse")
    t.text(t.track("text", "Saludo"), "Feliz", 0.3, 7.7, Box(40, 360, 1000, 270),
           text_style("Lobster", 190, [shadow("#000000", 0, 6, 14, 0.5), stroke(8, "#FFFFFF"), fill("#E63946")],
                      weight=400,
                      anim_in=tanim("pop", duration=0.5, unit="character", stagger=0.06, ease="back")),
           label="Saludo")
    t.text(t.track("text", "Título"), "Navidad", 1.0, 7.0, Box(40, 1290, 1000, 300),
           text_style("Lobster", 220, [glow("#FFFFFF", 30, 0.6), stroke(8, "#FFFFFF"), fill("#E63946")], weight=400,
                      anim_in=tanim("pop", duration=0.5, unit="character", stagger=0.06, ease="back"),
                      anim_loop=tanim("pulse", amount=4, speed=1.0)), label="Título")
    t.text(t.track("text", "Firma"), "Les desea: Familia Ríos", 1.8, 6.2, Box(40, 1610, 1000, 90),
           text_style("Quicksand", 54, [shadow("#000000", 0, 3, 10, 0.6), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("fade", duration=0.6)), label="Firma")
    t.adjust([effect("star_filter", intensity=0.7, threshold=0.8, spikeLength=0.35, points=4, rainbow=0.2),
              effect("bling_sparkle", intensity=0.4, density=0.35, threshold=0.8)], name="Destellos")
    t.song("dance-of-the-tuba-plum-fairy", 0.0, 0.85)
    return t


def regalo_sorpresa() -> Template:
    """A red gift box bounces in and shakes; the lid flies off and the present pops out, then the reaction."""
    t = Template("navidad-regalo-sorpresa", "Regalo sorpresa", "Surprise gift", "seasonal", 8.0, order=1032,
                 tags=["regalo", "sorpresa", "navidad", "unboxing", "cumpleaños"], thumb_at=3.9,
                 background="#9D0208")
    t.solid(t.track("shape", "Fondo"), "#C1121F",
            layers=[gradient([(0, "#E63946"), (1, "#8D0801")], angle=90), no_stroke()])
    shape(t, t.track("shape", "Rayos"), "#FFFFFF", 2.7, 5.3, centered(540, 1000, 1700, 1700),
          [(0, {"s": 0.3}, "out"), (0.6, {})], kind="burst", alpha=0.12, rotation=keys([(0, 0), (5.3, 40)]),
          geometry={"points": 24, "innerRatio": 0.82})
    # The box: body parts and lid parts share an entrance and a shake; at 2.6 the lid flies off, the body drops.
    cx, cy = 540, 1180
    shake = [(0, {"s": 0.02, "dy": 300}, "back"), (0.6, {}, "linear"), (1.2, {}, "linear")]
    k = 1.2
    side = 1
    while k < 2.5:
        k += 0.1
        shake.append((k, {"dx": 18 * side}, "linear"))
        side = -side
    shake.append((2.6, {}, "linear"))
    body_motion = shake + [(3.2, {"dy": 900})]
    lid_motion = shake + [(3.2, {"dy": -1400})]
    gold = "#FFC300"
    body = [(0, 0, 560, 440, "#C1121F", "rectangle"), (0, 0, 90, 440, gold, "rectangle")]
    lid = [(0, -215, 620, 130, "#D62828", "rectangle"), (0, -215, 90, 130, gold, "rectangle"),
           (-75, -315, 150, 100, gold, "ellipse"), (75, -315, 150, 100, gold, "ellipse"),
           (0, -300, 64, 64, "#E8A700", "ellipse")]
    for j, (ox, oy, w, h, colour, kind) in enumerate(body):
        t.solid(t.track("shape", f"Caja {j + 1}"), colour, 0.0, 3.3, centered(cx + ox, cy + oy, w, h),
                grouped(body_motion, ox, oy), kind=kind,
                layers=[shadow("#3D0000", 0, 16, 30, 0.45), fill(colour), no_stroke()])
    for j, (ox, oy, w, h, colour, kind) in enumerate(lid):
        t.solid(t.track("shape", f"Tapa {j + 1}"), colour, 0.0, 3.3, centered(cx + ox, cy + oy, w, h),
                grouped(lid_motion, ox, oy), kind=kind,
                layers=[shadow("#3D0000", 0, 10, 20, 0.35), fill(colour), no_stroke()],
                rotation=keys([(0, 0), (2.6, 0, "in"), (3.2, 35)]))
    t.text(t.track("text", "Pregunta"), "¿Qué habrá adentro?", 0.4, 2.3, Box(60, 330, 960, 240),
           text_style("Fredoka", 88, [shadow("#5C0000", 0, 6, 0, 0.8), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("typewriter", duration=0.9, unit="character"),
                      anim_out=tanim("fade", duration=0.2)), label="Pregunta")
    t.solid(t.track("shape", "Destello"), "#FFFFFF", 2.6, 0.4, FULL, opacity=keys([(0, 0.9, "out"), (0.4, 0.0)]))
    cards = t.track("shape", "Tarjeta")
    photos = t.track("video", "Fotos")
    card_box, photo_box = centered(540, 1000, 780, 1000), centered(540, 1000, 720, 940)
    gift = [(0, {"s": 0.15, "dy": 180}, "back"), (0.55, {}, "linear"), (2.7, {"s": 1.04})]
    t.solid(cards, "#FFFFFF", 2.7, 2.7, card_box, gift, radius=30, kind="rounded-rectangle",
            layers=[shadow("#3D0000", 0, 20, 40, 0.45), fill("#FFFFFF"), no_stroke()], rotation=rot(-3))
    t.photo(photos, "box-02", 2.7, 2.7, photo_box, gift, label="Tu regalo", rotation=rot(-3))
    react = [(0, {"dx": 1100}, "out"), (0.45, {}, "linear"), (2.6, {"s": 1.04})]
    t.solid(cards, "#FFFFFF", 5.4, 2.6, card_box, react, radius=30, kind="rounded-rectangle",
            layers=[shadow("#3D0000", 0, 20, 40, 0.45), fill("#FFFFFF"), no_stroke()], rotation=rot(3))
    t.photo(photos, "shopping-03", 5.4, 2.6, photo_box, react, label="Tu reacción", rotation=rot(3))
    rng = random.Random(9)
    for lane in range(2):
        confetti = t.track("shape", f"Confeti {lane + 1}")
        for n in range(10):
            x = rng.uniform(60, 1020)
            start = 2.7 + rng.uniform(0, 0.3)
            t.solid(confetti, rng.choice([gold, "#FFFFFF", "#3BE37A", "#4CC9F0"]), start, 8.0 - start,
                    centered(540, 1100, 36, 36),
                    [(0, {"s": 0.3}, "out"), (0.7, {"dx": x - 540, "dy": rng.uniform(-950, -200), "s": 1.0}, "linear"),
                     (8.0 - start, {"dx": x - 540 + rng.uniform(-80, 80), "dy": rng.uniform(500, 900)})],
                    kind=rng.choice(["star", "rectangle", "ellipse"]),
                    rotation=keys([(0, 0), (8.0 - start, rng.uniform(-300, 300))]))
    t.text(t.track("text", "Grito"), "¡SORPRESA!", 2.8, 2.6, Box(0, 200, 1080, 260),
           text_style("Titan One", 150, [shadow("#5C0000", 0, 10, 0, 1.0), stroke(10, "#9D0208"), fill(gold)],
                      weight=400, anim_in=tanim("stamp", duration=0.35)), label="Grito")
    t.text(t.track("text", "Mensaje"), "¡Me encantó, gracias!", 5.6, 2.4, Box(60, 1560, 960, 200),
           text_style("Fredoka", 84, [shadow("#5C0000", 0, 6, 0, 0.8), fill("#FFFFFF")], weight=700,
                      anim_in=tanim("rise", duration=0.5)), label="Mensaje")
    t.adjust([effect("beat_shake", animated={"amount": spikes([2.7], 0.8, 0.4)}, rotation=0.4)], name="Golpe")
    t.song("happy-whistling-ukulele", 0.0, 0.85)
    return t


def menu_navideno() -> Template:
    """A cream menu card on deep green: three courses with round photos, then each dish fills the screen."""
    t = Template("menu-navideno", "Menú navideño", "Christmas menu", "seasonal", 12.0, order=1033,
                 tags=["navidad", "menú", "cena", "restaurante", "nochebuena"], thumb_at=4.6, background="#0F2E1E")
    t.solid(t.track("shape", "Fondo"), "#0F2E1E",
            layers=[gradient([(0, "#1E5631"), (1, "#0F2E1E")], angle=90), no_stroke()])
    enter = [(0, {"dy": 1900}, "out"), (0.7, {})]
    t.solid(t.track("shape", "Carta"), "#FFF8F0", 0, 12.0, Box(60, 120, 960, 1680), enter, radius=44,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 24, 50, 0.45), fill("#FFF8F0"), no_stroke()])
    t.solid(t.track("shape", "Filete"), "#A4161A", 0, 12.0, Box(86, 146, 908, 1628), enter, radius=30,
            kind="rounded-rectangle", layers=ring("#A4161A", 3))
    # Holly in the two top corners.
    for side, x in (("izq", 170), ("der", 910)):
        flip = -1 if side == "der" else 1
        for j, (ox, oy, w, h, colour, kind, deg) in enumerate([(-28, 0, 90, 44, "#2D6A4F", "ellipse", -30),
                                                                (28, 0, 90, 44, "#40916C", "ellipse", 30),
                                                                (0, -14, 34, 34, "#D00000", "ellipse", 0)]):
            t.solid(t.track("shape", f"Acebo {side} {j + 1}"), colour, 0.9, 11.1,
                    centered(x + ox * flip, 230 + oy, w, h), pop(0, 0.4), kind=kind, rotation=rot(deg * flip))
    t.text(t.track("text", "Título"), "Menú de Nochebuena", 0.8, 11.2, Box(100, 200, 880, 180),
           text_style("Pinyon Script", 112, [fill("#A4161A")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.03)), label="Título")
    t.text(t.track("text", "Fecha"), "24 · 12 · 2026", 1.0, 11.0, Box(100, 382, 880, 60),
           text_style("Playfair Display", 40, [fill("#1E5631")], weight=600, spacing=8,
                      anim_in=tanim("fade", duration=0.6)), label="Fecha")
    t.solid(t.track("shape", "Divisor"), "#B08D57", 1.1, 10.9, Box(440, 462, 200, 4), [(0, {"sx": 0.02}, "out"),
                                                                                      (0.6, {})])
    courses = [("ENTRADA", "Ensalada de la casa", "food-01"), ("FONDO", "Pasta rellena con albahaca", "restaurant-01"),
               ("POSTRE", "Chocolate caliente y bombones", "coffee-01")]
    for i, (course, dish, sample) in enumerate(courses):
        y0 = 520 + i * 380
        at = 1.2 + i * 0.7
        slide = [(0, {"dx": -160}, "out"), (0.5, {})]
        t.solid(t.track("shape", f"Aro {i + 1}"), "#B08D57", at, 12.0 - at, centered(260, y0 + 150, 316, 316),
                pop(0, 0.45), kind="ellipse", layers=ring("#B08D57", 6))
        plates = t.track("video", f"Plato {i + 1}")
        clip = t.photo(plates, sample, at, 12.0 - at, centered(260, y0 + 150, 300, 300), pop(0, 0.45),
                       label=course.title())
        t.mask(plates, clip, "ellipse")
        t.text(t.track("text", f"Tiempo {i + 1}"), course, at + 0.1, 11.9 - at, Box(440, y0 + 50, 540, 50),
               text_style("Playfair Display", 34, [fill("#B08D57")], weight=700, spacing=6, align="left"),
               slide, editable=False)
        t.text(t.track("text", f"Plato {i + 1}"), dish, at + 0.2, 11.8 - at, Box(440, y0 + 100, 540, 150),
               text_style("Playfair Display", 54, [fill("#1E2B22")], weight=700, italic=True, align="left",
                          valign="top", line=1.05), slide, label=f"Plato {i + 1}")
    t.text(t.track("text", "Cierre"), "¡Buen provecho!", 3.6, 8.4, Box(100, 1650, 880, 120),
           text_style("Pinyon Script", 84, [fill("#A4161A")], weight=400, anim_in=tanim("fade", duration=0.8)),
           label="Cierre")
    # Then each dish fills the screen (the same slots, shown again).
    heroes = t.track("video", "Platos en grande")
    hero_clips = []
    for i, (course, _, _) in enumerate(courses):
        start = 6.2 + i * 1.95
        dur = 12.0 - start if i == 2 else 1.95
        hero_clips.append(t.photo(heroes, "", start, dur, FULL, [(0, {"s": 1.12}, "linear"), (dur, {"s": 1.0})],
                                  reuse=f"p{i + 1}"))
    hero_clips[0]["animIn"] = {"kind": "fade", "durationUs": 400000, "curve": "smooth"}
    for a, b in zip(hero_clips, hero_clips[1:]):
        t.transition(heroes, a, b, "crossfade", 0.4)
    tags = t.track("text", "Etiqueta")
    for i, (course, _, _) in enumerate(courses):
        start = 6.4 + i * 1.95
        t.text(tags, course, start, (12.0 if i == 2 else start + 1.75) - start, Box(340, 1640, 400, 100),
               text_style("Playfair Display", 46, [fill("#FFF8F0")], weight=700, spacing=8, box=("#A4161A", 0.95),
                          box_pad=18, box_radius=50, anim_in=tanim("pop", duration=0.35)), editable=False)
    t.adjust([effect("color.basic", temperature=0.08, vibrance=0.1)], name="Color")
    t.song("the-celebrated-minuet-for-piano", 0.0, 0.8)
    return t


# --- Año Nuevo -----------------------------------------------------------------------------------


def cuenta_regresiva_anio_nuevo() -> Template:
    """10 → 1 on the beat over a dark firework sky with a draining bar, then flash, «2027» and fireworks."""
    t = Template("anio-nuevo-cuenta-regresiva", "Cuenta regresiva de Año Nuevo", "New Year countdown", "seasonal",
                 12.0, order=1040, tags=["año nuevo", "cuenta regresiva", "2027", "fuegos artificiales", "fiesta"],
                 thumb_at=7.3, background="#05060F")
    photos = t.track("video", "Fotos")
    t.photo(photos, "newyear-04", 0, 6.4, FULL, [(0, {"s": 1.0}, "linear"), (6.4, {"s": 1.15})], label="Fondo",
            effects=[effect("color.basic", exposure=-0.35, saturation=-0.1)])
    after = [("newyear-03", "Foto 1"), ("newyear-02", "Foto 2"), ("newyear-01", "Foto 3")]
    for i, (sample, label) in enumerate(after):
        start = 6.4 + i * 1.9
        dur = 12.0 - start if i == 2 else 1.9
        t.photo(photos, sample, start, dur, FULL,
                [(0, {"s": 1.2}, "snap"), (0.2, {"s": 1.03}, "linear"), (dur, {"s": 1.0})], label=label)
    t.solid(t.track("shape", "Barra"), "#E9C46A", 0.4, 6.0, Box(140, 1700, 800, 12),
            [(0, {}, "linear"), (6.0, {"sx": 0.02, "dx": -400})], layers=[glow("#FFE8A3", 16, 0.8), fill("#E9C46A"),
                                                                        no_stroke()])
    rings = t.track("shape", "Anillo")
    numbers = t.track("text", "Números")
    for i in range(10):
        start = 0.4 + i * 0.6
        t.solid(rings, "#E9C46A", start, 0.6, centered(540, 960, 620, 620),
                [(0, {"s": 1.25}, "snap"), (0.2, {}, "linear"), (0.6, {"s": 0.9})], kind="ellipse",
                layers=ring("#E9C46A", 10, halo="#FFE8A3"), opacity=keys([(0, 1.0), (0.4, 1.0, "smooth"), (0.6, 0.0)]))
        t.text(numbers, str(10 - i), start, 0.6, centered(540, 960, 900, 700),
               text_style("Big Shoulders Display", 520, [glow("#E9C46A", 30, 0.8), fill("#FFFFFF")], weight=900,
                          keyframes={"pixelSize": keys([(0, 900, "snap"), (0.15, 520)])}), editable=False)
    t.text(t.track("text", "Antes"), "¡Despidamos el 2026!", 0.2, 6.2, Box(40, 180, 1000, 140),
           text_style("Big Shoulders Display", 92, [shadow("#000000", 0, 4, 14, 0.6), fill("#E9C46A")], weight=800,
                      spacing=4, case="upper", anim_in=tanim("slide-down", duration=0.5)), label="Antes")
    rng = random.Random(27)
    for lane in range(2):
        bursts = t.track("shape", f"Fuegos {lane + 1}")
        start = 6.5 + lane * 0.45
        while start < 11.2:
            colour = rng.choice(["#FFD166", "#FF5D8F", "#4CC9F0", "#FFFFFF"])
            size = rng.uniform(220, 380)
            shape(t, bursts, colour, start, 0.85, centered(rng.uniform(140, 940), rng.uniform(300, 700), size, size),
                  [(0, {"s": 0.1}, "out"), (0.85, {"s": 1.3})], kind="burst",
                  layers=[glow(colour, 30, 0.9), fill(colour), no_stroke()],
                  opacity=keys([(0, 1.0), (0.4, 1.0, "smooth"), (0.85, 0.0)]),
                  geometry={"points": 14, "innerRatio": 0.25})
            start += 0.9
    t.text(t.track("text", "Año"), "2027", 6.4, 5.6, Box(0, 720, 1080, 420),
           text_style("Monoton", 300, [glow("#FFD166", 40, 0.9), gradient([(0, "#FFF3B0"), (1, "#E9C46A")], angle=90)],
                      weight=400, keyframes={"pixelSize": keys([(0, 700, "snap"), (0.2, 300)])},
                      anim_loop=tanim("pulse", amount=4, speed=1.0)), label="Año")
    t.text(t.track("text", "Saludo"), "¡Feliz Año Nuevo!", 6.7, 5.3, Box(40, 1150, 1000, 160),
           text_style("Big Shoulders Display", 112, [shadow("#000000", 0, 6, 16, 0.7), fill("#FFFFFF")], weight=900,
                      case="upper", anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.12)), label="Saludo")
    beats = [0.4 + 0.6 * i for i in range(10)] + [6.4 + 0.5 * k for k in range(11)]
    t.adjust([effect("zoom_pulse", animated={"punch": spikes(beats, 0.25, 0.2)}),
              effect("strobe_flash", animated={"flash": spikes([6.4, 7.4, 8.4, 9.4, 10.4], 0.7, 0.25)}, tint=0.15),
              effect("bloom_glow", threshold=0.6, intensity=0.8, blurRadius=10)], name="Golpes")
    t.song("beat-one", 0.0, 0.9)
    return t


def mi_anio_en_fotos() -> Template:
    """A 3×3 grid that fills a cell per beat, then the centre photo grows to full screen under an outlined «2026»."""
    t = Template("mi-2026-en-fotos", "Mi 2026 en fotos", "My 2026 in photos", "seasonal", 14.0, order=1041,
                 tags=["año nuevo", "resumen", "2026", "recuerdos", "fotos"], thumb_at=4.9, background="#0F0F0F")
    t.solid(t.track("shape", "Fondo"), "#0F0F0F")
    champagne = "#F7E7CE"
    t.text(t.track("text", "Título"), "Mi 2026 en fotos", 0.2, 6.6, Box(40, 70, 1000, 140),
           text_style("Prata", 84, [fill(champagne)], weight=400, anim_in=tanim("fade-up-char", duration=0.5,
                                                                                unit="character", stagger=0.03),
                      anim_out=tanim("fade", duration=0.3)), label="Título")
    samples = ["friends-01", "travel-07", "beach-01", "birthday-01", "couple-07", "graduation-03", "family-05",
               "concert-02", "selfie-02"]
    cell_w, cell_h, gap = 320, 500, 20
    for i, sample in enumerate(samples):
        col, row = i % 3, i // 3
        box = Box(40 + col * (cell_w + gap), 240 + row * (cell_h + gap), cell_w, cell_h)
        start = 0.5 + i * beat(1)
        cells = t.track("video", f"Celda {i + 1}")
        if i == 4:
            # The centre one grows to cover the screen and stays.
            grow = 1920 / cell_h
            motion = [(0, {"s": 0.02}, "back"), (0.4, {}, "linear"), (6.5 - start, {}, "inout"),
                      (7.5 - start, {"s": grow, "dy": 960 - box.cy}, "linear"),
                      (14.0 - start, {"s": grow * 1.06, "dy": 960 - box.cy})]
            t.photo(cells, sample, start, 14.0 - start, box, motion, label="Foto principal")
        else:
            motion = [(0, {"s": 0.02}, "back"), (0.4, {}, "linear"), (6.5 - start, {}, "smooth"),
                      (7.2 - start, {"s": 0.85})]
            t.photo(cells, sample, start, 7.3 - start, box, motion, label=f"Foto {i + 1}",
                    opacity=keys([(0, 1.0), (6.5 - start, 1.0, "smooth"), (7.2 - start, 0.0)]))
    t.solid(t.track("shape", "Velo"), "#000000", 7.5, 6.5, FULL, alpha=0.35, opacity=keys([(0, 0.0), (0.6, 1.0)]))
    t.text(t.track("text", "Año"), "2026", 7.7, 6.3, Box(0, 640, 1080, 460),
           text_style("Josefin Sans", 380, [glow(champagne, 30, 0.6), stroke(6, champagne), dict(NO_FILL)],
                      weight=700, anim_in=tanim("blur-in", duration=1.0, blur=24),
                      anim_loop=tanim("tracking-drift", **{"from": 0, "to": 16})), label="Año")
    t.text(t.track("text", "Frase"), "gracias por tanto", 8.4, 5.6, Box(40, 1140, 1000, 130),
           text_style("Prata", 76, [shadow("#000000", 0, 4, 14, 0.6), fill(champagne)], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.04)), label="Frase")
    t.adjust([effect("light_leak", animated={"intensity": keys([(0, 0.0), (6.6, 0.0, "smooth"), (7.3, 0.6, "smooth"),
                                                                (8.4, 0.0)])}, hue=0.08, speed=0.7),
              effect("stylize.film_grain", amount=0.15)], name="Luz")
    t.song("and-just-like-that", 0.0, 0.85)
    return t


def propositos_anio_nuevo() -> Template:
    """A ruled notebook page: the title in marker, four resolutions ticked one by one and two taped photos."""
    t = Template("propositos-2027", "Mis propósitos 2027", "My 2027 resolutions", "seasonal", 10.0, order=1042,
                 tags=["año nuevo", "propósitos", "metas", "2027", "cuaderno"], thumb_at=7.6, background="#FDFBF4")
    t.solid(t.track("shape", "Papel"), "#FDFBF4")
    t.solid(t.track("shape", "Renglones"), "#A8C5E6", 0, 10.0, Box(0, 440, 1080, 1480),
            layers=stripes([("#A8C5E6", 0.8)] * 18, 0.04, angle=90))
    t.solid(t.track("shape", "Margen"), "#E76F51", 0, 10.0, Box(150, 0, 4, 1920), alpha=0.7)
    ink = "#1D3557"
    t.solid(t.track("shape", "Resaltador"), "#FFE066", 1.0, 9.0, Box(175, 382, 700, 30),
            [(0, {"sx": 0.02, "dx": -343}, "out"), (0.6, {})], alpha=0.8)
    t.text(t.track("text", "Título"), "Mis propósitos 2027", 0.2, 9.8, Box(180, 110, 860, 290),
           text_style("Kalam", 104, [fill(ink)], weight=700, align="left", line=1.0, valign="bottom",
                      anim_in=tanim("typewriter", duration=0.8, unit="character")), label="Título")
    t.solid(t.track("shape", "Estrella"), "#FFC300", 0.9, 9.1, centered(985, 150, 90, 90), pop(0, 0.4), kind="star",
            rotation=keys([(0, 0), (9.1, 40)]))
    items = ["Viajar a otro país", "Ahorrar cada mes", "Ir al gym", "Leer 12 libros"]
    for i, item in enumerate(items):
        y = 480 + i * 150
        at = 1.3 + i * 1.0
        t.solid(t.track("shape", f"Casilla {i + 1}"), ink, at, 10.0 - at, centered(222, y + 50, 64, 64),
                pop(0, 0.3), radius=10, kind="rounded-rectangle", layers=ring(ink, 5))
        t.text(t.track("text", f"Propósito {i + 1}"), item, at, 10.0 - at, Box(290, y, 760, 100),
               text_style("Patrick Hand", 78, [fill(ink)], weight=400, align="left",
                          anim_in=tanim("typewriter", duration=0.6, unit="character")), label=f"Propósito {i + 1}")
        t.text(t.track("text", f"Visto {i + 1}"), "✓", at + 0.7, 9.3 - at, centered(226, y + 40, 120, 120),
               text_style("Kalam", 110, [fill("#2A9D8F")], weight=700, anim_in=tanim("stamp", duration=0.3)),
               editable=False)
    polaroids = [("travel-07", 330, 1420, -6, 5.4), ("selfie-03", 760, 1450, 5, 6.0)]
    for i, (sample, x, y, tilt, at) in enumerate(polaroids):
        drop = [(0, {"s": 1.3, "dy": -200}, "out"), (0.4, {})]
        t.solid(t.track("shape", f"Polaroid {i + 1}"), "#FFFFFF", at, 10.0 - at, centered(x, y + 40, 420, 500),
                grouped(drop, 0, 40), layers=[shadow("#3d2b14", 4, 14, 26, 0.3), fill("#FFFFFF"), no_stroke()],
                rotation=rot(tilt))
        t.photo(t.track("video", f"Foto {i + 1}"), sample, at, 10.0 - at, centered(x, y, 370, 370), drop,
                label=f"Foto {i + 1}", rotation=rot(tilt))
        t.solid(t.track("shape", f"Cinta {i + 1}"), "#F4A261", at + 0.4, 9.6 - at, centered(x, y - 205, 170, 46),
                alpha=0.75, rotation=rot(tilt + (8 if i else -8)))
    t.text(t.track("text", "Frase"), "¡Este año sí!", 7.0, 3.0, Box(60, 1735, 960, 150),
           text_style("Kalam", 96, [fill("#E76F51")], weight=700, anim_in=tanim("pop", duration=0.4, ease="back")),
           label="Frase", rotation=rot(-3))
    t.song("from-page-to-practice", 0.0, 0.85)
    return t


# --- Black Friday y Cyber Monday -----------------------------------------------------------------


def black_friday_ofertas() -> Template:
    """Black and red hype: products cut on the beat in a tilting white frame, a «-50%» price tag that slams in."""
    t = Template("black-friday-ofertas", "Black Friday: ofertas", "Black Friday deals", "seasonal", 8.0,
                 order=1050, tags=["black friday", "ofertas", "descuento", "tienda", "noviembre"], thumb_at=3.2,
                 background="#000000")
    t.solid(t.track("shape", "Fondo"), "#000000")
    t.text(t.track("text", "Letras de fondo"), "BLACK FRIDAY\n" * 7, 0, 8.0, Box(-100, -200, 1280, 2700),
           text_style("League Gothic", 330, [stroke(3, "#FFFFFF", 0.22), dict(NO_FILL)], weight=400, line=0.95),
           [(0, {}, "linear"), (8.0, {"dy": -600})], editable=False)
    red = "#FF1E1E"
    frames = t.track("shape", "Marco")
    photos = t.track("video", "Productos")
    samples = ["shopping-03", "shopping-02", "outfit-04", "shopping-04"]
    frame_box, photo_box = centered(540, 980, 840, 1080), centered(540, 980, 800, 1040)
    for i in range(14):
        start = 0.5 + i * beat(1)
        tilt = 3 if i % 2 else -3
        motion = [(0, {"s": 1.12}, "snap"), (0.15, {})]
        t.solid(frames, "#FFFFFF", start, beat(1), frame_box, motion, rotation=rot(tilt))
        t.photo(photos, samples[i % 4], start, beat(1), photo_box, motion, rotation=rot(tilt),
                reuse=None if i < 4 else f"p{i % 4 + 1}", label=f"Producto {i % 4 + 1}")
    t.solid(t.track("shape", "Banda"), red, 0.0, 8.0, Box(0, 60, 1080, 250), [(0, {"dx": -1100}, "out"), (0.4, {})])
    t.text(t.track("text", "Título"), "BLACK FRIDAY", 0.1, 7.9, Box(0, 60, 1080, 250),
           text_style("League Gothic", 230, [fill("#000000")], weight=400, spacing=6,
                      anim_in=tanim("slide-left", duration=0.35)), label="Título")
    tag = centered(780, 1500, 440, 260)
    t.solid(t.track("shape", "Etiqueta"), red, 2.0, 6.0, tag, [(0, {"s": 2.2}, "snap"), (0.18, {})], radius=28,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 14, 30, 0.7), fill(red), no_stroke()],
            rotation=rot(-8))
    t.solid(t.track("shape", "Ojal"), "#000000", 2.0, 6.0, centered(600, 1475, 36, 36),
            grouped([(0, {"s": 2.2}, "snap"), (0.18, {})], -180, -25), kind="ellipse")
    t.text(t.track("text", "Descuento"), "-50%", 2.0, 6.0, tag,
           text_style("League Gothic", 230, [fill("#FFFFFF")], weight=400,
                      keyframes={"pixelSize": keys([(0, 500, "snap"), (0.18, 230)])}), label="Descuento",
           rotation=rot(-8))
    t.text(t.track("text", "Alcance"), "EN TODA LA TIENDA", 2.4, 5.6, Box(60, 1665, 640, 100),
           text_style("Barlow Condensed", 70, [fill("#FFFFFF")], weight=800, spacing=3, align="left",
                      box=("#000000", 0.85), box_pad=12, anim_in=tanim("slide-up", duration=0.35)), label="Alcance")
    t.text(t.track("text", "Fechas"), "28 y 29 de noviembre", 2.7, 5.3, Box(60, 1775, 700, 70),
           text_style("Barlow Condensed", 52, [fill(red)], weight=700, spacing=2, align="left",
                      anim_in=tanim("fade", duration=0.4)), label="Fechas")
    beats = [0.5 + k * beat(1) for k in range(14)]
    t.adjust([effect("rgb_split", animated={"amount": spikes(beats, 22, 0.15)}),
              effect("beat_shake", animated={"amount": spikes([2.0], 0.9, 0.4)}, rotation=0.5),
              effect("scanline_glitch", jitter=0.1, lineStrength=0.2, colorShift=2, speed=2)], name="Golpes")
    t.song("bar-brawl", 0.0, 0.9)
    return t


def black_friday_ultimas_horas() -> Template:
    """Black and gold luxury: slow cross-fading looks, Bodoni titles and a timer that ticks down every second."""
    t = Template("black-friday-ultimas-horas", "Black Friday: últimas horas", "Black Friday: last hours",
                 "seasonal", 10.0, order=1051, tags=["black friday", "últimas horas", "oferta", "moda", "lujo"],
                 thumb_at=5.2, background="#0A0A0A")
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(["shopping-01", "shopping-02", "outfit-04"]):
        start = i * 3.4
        dur = 10.0 - start if i == 2 else 3.4
        clips.append(t.photo(photos, sample, start, dur, FULL, [(0, {"s": 1.02}, "linear"), (dur, {"s": 1.12})],
                             label=f"Foto {i + 1}",
                             effects=[effect("color.basic", contrast=0.15, saturation=-0.2, exposure=-0.1)]))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "crossfade", 0.7)
    t.solid(t.track("shape", "Sombra"), "#000000",
            layers=[gradient([(0, "#000000", 0.8), (0.3, "#000000", 0.0), (0.55, "#000000", 0.0),
                              (1, "#000000", 0.92)], angle=90), no_stroke()])
    gold = "#C9A227"
    t.solid(t.track("shape", "Marco"), gold, 0.2, 9.8, Box(40, 40, 1000, 1840), layers=ring(gold, 3),
            opacity=keys([(0, 0.0), (0.8, 1.0)]))
    goldtext = [shadow("#000000", 0, 4, 14, 0.6), gradient([(0, "#F7E39C"), (0.5, "#D4AF37"), (1, "#A8841F")], angle=90)]
    t.text(t.track("text", "Título"), "BLACK FRIDAY", 0.3, 9.7, Box(60, 150, 960, 130),
           text_style("Bodoni Moda", 80, goldtext, weight=700, spacing=6, anim_in=tanim("blur-in", duration=0.9)),
           label="Título")
    t.text(t.track("text", "Subtítulo"), "Últimas horas", 0.8, 9.2, Box(60, 300, 960, 140),
           text_style("Bodoni Moda", 96, [shadow("#000000", 0, 4, 14, 0.6), fill("#F5E6C8")], weight=400, italic=True,
                      anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.04)), label="Subtítulo")
    t.solid(t.track("shape", "Reloj"), "#000000", 1.4, 8.6, Box(190, 1290, 700, 190), pop(0, 0.4), radius=95,
            kind="rounded-rectangle", alpha=0.8, layers=[glow(gold, 24, 0.5), stroke(3, gold),
                                                          fill("#000000", 0.8)])
    t.text(t.track("text", "Antes del reloj"), "TERMINA EN", 1.5, 8.5, Box(190, 1215, 700, 60),
           text_style("Montserrat", 34, [fill(gold)], weight=600, spacing=10, anim_in=tanim("fade", duration=0.4)),
           label="Antes del reloj")
    timer = t.track("text", "Segundos")
    for k in range(9):
        start = 1.5 + k
        t.text(timer, f"05:59:{59 - k:02d}", start, min(1.0, 10.0 - start), Box(190, 1290, 700, 190),
               text_style("Montserrat", 120, [fill("#FFFFFF")], weight=800, spacing=4), editable=False)
    t.text(t.track("text", "Descuento"), "Hasta 70% de descuento", 2.0, 8.0, Box(60, 1515, 960, 100),
           text_style("Montserrat", 64, [shadow("#000000", 0, 4, 12, 0.6), fill("#FFFFFF")], weight=800,
                      anim_in=tanim("rise", duration=0.5)), label="Descuento")
    t.solid(t.track("shape", "Botón"), gold, 3.0, 7.0, centered(540, 1715, 640, 110),
            [(0, {"s": 0.02}, "back"), (0.4, {}, "smooth"), (1.0, {"s": 1.05}, "smooth"), (1.6, {}, "smooth"),
             (2.2, {"s": 1.05}, "smooth"), (2.8, {}, "smooth"), (3.4, {"s": 1.05}, "smooth"), (4.0, {})],
            radius=55, kind="rounded-rectangle", layers=[gradient([(0, "#F7E39C"), (1, "#C39A2A")], angle=0),
                                                         no_stroke()])
    t.text(t.track("text", "Llamada"), "Compra en el link de la bio", 3.2, 6.8, centered(540, 1715, 640, 110),
           text_style("Montserrat", 38, [fill("#111111")], weight=700), label="Llamada")
    t.adjust([effect("light_leak", intensity=0.3, hue=0.1, speed=0.5), effect("stylize.film_grain", amount=0.12),
              effect("stylize.vignette", amount=0.5)], name="Acabado")
    t.song("fake-it-til-you-fake-it", 0.0, 0.85)
    return t


def cyber_monday() -> Template:
    """Neon cyber grid, a glowing phone whose screen swipes through products, a «-40%» burst and a cart tap."""
    t = Template("cyber-monday", "Cyber Monday", "Cyber Monday", "seasonal", 8.0, order=1052,
                 tags=["cyber monday", "ofertas", "tienda online", "descuento", "envío gratis"], thumb_at=3.3,
                 background="#070A1F")
    t.solid(t.track("shape", "Fondo"), "#070A1F",
            layers=[gradient([(0, "#070A1F"), (1, "#1B1464")], angle=90), no_stroke()])
    cyan, magenta = "#00E5FF", "#FF2BD6"
    t.solid(t.track("shape", "Rejilla vertical"), cyan, 0, 8.0, Box(0, 0, 1080, 1920),
            layers=stripes([(cyan, 0.16)] * 12, 0.03, angle=0))
    t.solid(t.track("shape", "Rejilla horizontal"), cyan, 0, 8.0, Box(0, -480, 1080, 2400),
            [(0, {}, "linear"), (8.0, {"dy": 480})], layers=stripes([(cyan, 0.16)] * 25, 0.03, angle=90))
    t.text(t.track("text", "Título"), "CYBER MONDAY", 0.1, 7.9, Box(0, 70, 1080, 400),
           text_style("Audiowide", 170, [shadow(magenta, 8, 0, 0, 1.0, id="magenta"), glow(cyan, 20, 0.6),
                                         fill(cyan)], weight=400, line=0.95,
                      accent={"rule": "lastWord", "colorEnabled": True, "color": argb(magenta)},
                      anim_in=tanim("glitch-in", duration=0.4)), label="Título")
    phone = [(0, {"dy": 1400}, "out"), (0.6, {})]
    t.solid(t.track("shape", "Teléfono"), "#0A0A14", 0.2, 7.8, centered(540, 1060, 600, 1120), phone, radius=70,
            kind="rounded-rectangle", layers=[glow(cyan, 40, 0.8), stroke(6, cyan), fill("#0A0A14")])
    screen = t.track("video", "Pantalla")
    clips = []
    for i, (sample, start, end) in enumerate([("shopping-01", 0.2, 2.6), ("outfit-04", 2.6, 4.6),
                                              ("shopping-03", 4.6, 8.0)]):
        motion = phone if i == 0 else None
        clips.append(t.photo(screen, sample, start, end - start, centered(540, 1060, 556, 1076), motion,
                             label=f"Producto {i + 1}"))
    for a, b in zip(clips, clips[1:]):
        t.transition(screen, a, b, "push_left", 0.4)
    t.solid(t.track("shape", "Cámara"), "#0A0A14", 0.2, 7.8, centered(540, 536, 160, 30), phone, radius=15,
            kind="rounded-rectangle")
    shape(t, t.track("shape", "Estallido"), magenta, 2.8, 5.2, centered(850, 600, 380, 380),
          [(0, {"s": 2.0}, "snap"), (0.2, {})], kind="burst",
          layers=[glow(magenta, 30, 0.8), fill(magenta), no_stroke()], rotation=keys([(0, -10), (5.2, 30)]),
          geometry={"points": 16, "innerRatio": 0.78})
    t.text(t.track("text", "Descuento"), "-40%", 2.8, 5.2, centered(850, 600, 380, 380),
           text_style("Exo 2", 130, [fill("#FFFFFF")], weight=900,
                      keyframes={"pixelSize": keys([(0, 300, "snap"), (0.2, 130)])}), label="Descuento",
           rotation=rot(-10))
    button = centered(540, 1740, 700, 120)
    t.solid(t.track("shape", "Botón"), magenta, 4.6, 3.4, button,
            [(0, {"s": 0.02}, "back"), (0.4, {}, "linear"), (0.95, {}, "in"), (1.05, {"s": 0.92}, "out"), (1.25, {})],
            radius=60, kind="rounded-rectangle",
            layers=[glow(magenta, 24, 0.7), gradient([(0, magenta), (1, "#7B2FF7")], angle=0), no_stroke()])
    t.text(t.track("text", "Botón"), "Agregar al carrito", 4.7, 0.95, button,
           text_style("Exo 2", 54, [fill("#FFFFFF")], weight=800), label="Botón")
    t.text(t.track("text", "Botón confirmado"), "✓ ¡Agregado!", 5.65, 2.35, button,
           text_style("Exo 2", 56, [fill("#FFFFFF")], weight=800, anim_in=tanim("pop", duration=0.3)),
           label="Botón confirmado")
    t.solid(t.track("shape", "Cursor"), "#FFFFFF", 4.9, 1.6, centered(640, 1790, 54, 74),
            [(0, {"dx": 380, "dy": 260}, "out"), (0.6, {}, "linear"), (0.7, {"s": 0.85}, "out"), (0.9, {})],
            kind="triangle", layers=[stroke(4, "#000000"), fill("#FFFFFF")], rotation=rot(-28))
    t.text(t.track("text", "Detalle"), "Envío gratis · Solo hoy", 1.0, 7.0, Box(40, 1830, 1000, 70),
           text_style("Exo 2", 42, [fill(cyan)], weight=600, spacing=4, case="upper",
                      anim_in=tanim("fade", duration=0.5)), label="Detalle")
    t.adjust([effect("rgb_split", animated={"amount": spikes([0.1, 2.6, 2.8, 4.6], 26, 0.16)}),
              effect("scanline_glitch", jitter=0.08, lineStrength=0.25, colorShift=3, speed=3),
              effect("bloom_glow", threshold=0.7, intensity=0.6, blurRadius=10)], name="Neón")
    t.song("arpent", 0.0, 0.9)
    return t


# --- San Valentín / Día de la Amistad ------------------------------------------------------------


def san_valentin_carta() -> Template:
    """A love letter: the envelope slides up, its sealed flap opens and the photo card rises out of it."""
    t = Template("san-valentin-carta", "Carta de amor", "Love letter", "seasonal", 10.0, order=1060,
                 tags=["san valentín", "amor", "pareja", "14 de febrero", "carta"], thumb_at=4.6,
                 background="#C9184A")
    t.solid(t.track("shape", "Fondo"), "#C9184A",
            layers=[gradient([(0, "#FF4D6D"), (1, "#A4133C")], angle=90), no_stroke()])
    rng = random.Random(14)
    particles(t, "Corazones", 2, 0.0, 10.0, rng, ["#FFB3C1", "#FFFFFF", "#FF758F"], kinds=("heart",),
              size=(30, 70), y=1990, dy=-2200, life=(4.0, 6.0), every=(0.6, 1.2), sway=80, alpha=0.45)
    env = Box(120, 1180, 840, 540)
    enter = [(0, {"dy": 900}, "out"), (0.6, {})]
    t.solid(t.track("shape", "Sobre fondo"), "#E8C7B0", 0, 10.0, env, enter,
            layers=[shadow("#590D22", 0, 20, 40, 0.45), fill("#E8C7B0"), no_stroke()])
    # The open flap (pointing up) grows from the envelope's top edge once the closed one has folded away.
    t.solid(t.track("shape", "Solapa abierta"), "#F2D5C0", 1.5, 8.5, Box(120, 880, 840, 300),
            [(0, {"sy": 0.02, "dy": 150}, "out"), (0.35, {})], kind="triangle")
    card_motion = [(0, {"dy": 690, "s": 0.85}, "out"), (1.0, {})]
    t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", 2.0, 8.0, centered(540, 760, 640, 760), card_motion, radius=14,
            kind="rounded-rectangle", layers=[shadow("#590D22", 0, 14, 30, 0.35), fill("#FFFFFF"), no_stroke()])
    photos = t.track("video", "Fotos")
    first = t.photo(photos, "couple-01", 2.0, 4.0, centered(540, 705, 580, 590), grouped(card_motion, 0, -55),
                    label="Foto 1")
    second = t.photo(photos, "couple-08", 6.0, 4.0, centered(540, 705, 580, 590),
                     None, label="Foto 2")
    t.transition(photos, first, second, "crossfade", 0.6)
    t.solid(t.track("shape", "Sobre frente"), "#F5DCC8", 0, 10.0, Box(120, 1330, 840, 390), enter,
            layers=[shadow("#8A4B3A", 0, -4, 12, 0.25), fill("#F5DCC8"), no_stroke()])
    # The closed flap points down; it folds up towards the top edge between 1.1 s and 1.5 s.
    t.solid(t.track("shape", "Solapa cerrada"), "#F2D5C0", 0, 1.5, Box(120, 1180, 840, 320),
            enter + [(1.1, {}, "in"), (1.5, {"sy": 0.02, "dy": -157})], kind="triangle",
            layers=[shadow("#8A4B3A", 0, 6, 12, 0.3), fill("#F2D5C0"), no_stroke()], rotation=rot(180))
    t.solid(t.track("shape", "Sello"), "#C9184A", 0, 1.3, centered(540, 1420, 120, 110),
            enter + [(0.9, {}, "in"), (1.2, {"s": 0.02})], kind="heart",
            layers=[shadow("#590D22", 0, 4, 8, 0.4), fill("#C9184A"), no_stroke()])
    t.text(t.track("text", "Dedicatoria"), "Para ti, mi amor", 0.3, 9.7, Box(40, 150, 1000, 210),
           text_style("Parisienne", 130, [shadow("#590D22", 0, 6, 16, 0.5), fill("#FFFFFF")], weight=400,
                      anim_in=tanim("fade-up-char", duration=0.6, unit="character", stagger=0.04)),
           label="Dedicatoria")
    t.text(t.track("text", "Mensaje"), "Feliz San Valentín", 2.6, 7.4, Box(140, 1440, 800, 140),
           text_style("Lora", 70, [fill("#C9184A")], weight=700, italic=True, anim_in=tanim("fade", duration=0.6)),
           label="Mensaje")
    t.text(t.track("text", "Fecha"), "14 · 02 · 2027", 3.0, 7.0, Box(40, 1760, 1000, 70),
           text_style("Lora", 46, [fill("#FFFFFF")], weight=600, spacing=8, anim_in=tanim("fade", duration=0.6)),
           label="Fecha")
    t.adjust([effect("light_leak", intensity=0.3, hue=0.95, speed=0.5, softness=0.6),
              effect("stylize.vignette", amount=0.35)], name="Luz")
    t.song("alls-fair-in-love", 0.0, 0.85)
    return t


def dia_de_la_amistad() -> Template:
    """A photo-booth strip on candy stripes: each shot flashes in like a camera, then the stickers land."""
    t = Template("dia-de-la-amistad", "Día de la amistad", "Friendship day", "seasonal", 9.0, order=1061,
                 tags=["amistad", "san valentín", "amigas", "14 de febrero", "fotomatón"], thumb_at=6.0,
                 background="#FFB3C6")
    t.solid(t.track("shape", "Fondo"), "#FFB3C6",
            layers=stripes(["#FFC8D6", "#FFB3C6"] * 8, 1.0, angle=45))
    pink = "#FF4D6D"
    strip = centered(540, 1060, 560, 1640)
    enter = [(0, {"dy": 1900}, "out"), (0.6, {})]
    t.solid(t.track("shape", "Tira"), "#FFFFFF", 0, 9.0, strip, enter, radius=16, kind="rounded-rectangle",
            layers=[shadow("#A4133C", 0, 18, 40, 0.35), fill("#FFFFFF"), no_stroke()])
    flashes = t.track("shape", "Flash")
    for i, sample in enumerate(["friends-09", "friends-11", "friends-03", "friends-12"]):
        cell = centered(540, strip.y + 30 + 170 + i * 360, 500, 340)
        at = 0.9 + i * 1.0
        t.photo(t.track("video", f"Foto {i + 1}"), sample, at, 9.0 - at, cell,
                [(0, {"s": 1.06}, "out"), (0.4, {}, "linear"), (9.0 - at, {"s": 1.03})], label=f"Foto {i + 1}")
        t.solid(flashes, "#FFFFFF", at, 0.35, cell, opacity=keys([(0, 1.0, "out"), (0.35, 0.0)]))
    t.text(t.track("text", "Pie"), "amigas x siempre", 4.9, 4.1, Box(260, strip.y + 1480 + 10, 560, 130),
           text_style("Bubblegum Sans", 70, [fill(pink)], weight=400,
                      anim_in=tanim("typewriter", duration=0.7, unit="character")), label="Pie")
    t.text(t.track("text", "Título"), "Feliz día de la amistad", 0.3, 8.7, Box(30, 40, 1020, 190),
           text_style("Chewy", 84, [shadow("#A4133C", 0, 6, 0, 0.9), stroke(8, pink), fill("#FFFFFF")], weight=400,
                      anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.1)), label="Título")
    stickers = [("Corazón", "heart", pink, centered(930, 560, 210, 190), 12, 5.0, "BFF", 70),
                ("Círculo", "ellipse", "#FFD166", centered(140, 1430, 200, 200), -10, 5.4, "14 FEB", 50)]
    for name, kind, colour, box, tilt, at, word, size in stickers:
        t.solid(t.track("shape", name), colour, at, 9.0 - at, box, pop(0, 0.4), kind=kind,
                layers=[shadow("#A4133C", 0, 8, 14, 0.35), stroke(6, "#FFFFFF"), fill(colour)], rotation=rot(tilt))
        t.text(t.track("text", f"Sticker {word}"), word, at + 0.1, 8.9 - at, box,
               text_style("Chewy", size, [fill("#FFFFFF" if kind == "heart" else pink)], weight=400,
                          anim_in=tanim("pop", duration=0.3)), label=f"Sticker {name.lower()}", rotation=rot(tilt))
    t.solid(t.track("shape", "Estrella"), "#FFFFFF", 5.8, 3.2, centered(940, 1700, 130, 130), pop(0, 0.4),
            kind="star", layers=[glow("#FFFFFF", 20, 0.8), fill("#FFFFFF"), no_stroke()],
            rotation=keys([(0, 0), (3.2, 60)]))
    t.adjust([effect("bling_sparkle", intensity=0.3, density=0.3, threshold=0.85)], name="Brillos")
    t.song("my-giant-bunny-friend", 0.0, 0.85)
    return t


# --- Día del Padre y Fiestas Patrias --------------------------------------------------------------


def dia_del_padre() -> Template:
    """Three tall panels slide in under a slab title, then one word per photo («MI HÉROE»…) and a closing shot."""
    t = Template("dia-del-padre", "Feliz Día del Papá", "Happy Father's Day", "seasonal", 12.0, order=1070,
                 tags=["día del padre", "papá", "familia", "junio", "héroe"], thumb_at=2.4, background="#14213D")
    t.solid(t.track("shape", "Fondo"), "#14213D")
    mustard, navy = "#FCA311", "#14213D"
    samples = ["christmas-05", "family-04", "wedding-05"]
    for i, (sample, cx) in enumerate(zip(samples, (200, 540, 880))):
        at = 0.3 + 0.2 * i
        side = -1 if i % 2 == 0 else 1
        motion = [(0, {"dy": 1400 * side}, "out"), (0.6, {}, "linear"), (3.8 - at, {}, "in"),
                  (4.2 - at, {"dy": -1400 * side})]
        t.solid(t.track("shape", f"Bloque {i + 1}"), mustard, at, 4.2 - at, centered(cx + 14, 1074, 320, 1100),
                motion)
        t.photo(t.track("video", f"Panel {i + 1}"), sample, at, 4.2 - at, centered(cx, 1060, 320, 1100), motion,
                label=f"Foto {i + 1}")
    t.text(t.track("text", "Título"), "Feliz Día del Papá", 0.2, 4.0, Box(40, 120, 1000, 340),
           text_style("Alfa Slab One", 120, [shadow("#000000", 0, 8, 0, 0.5), fill(mustard)], weight=400, line=1.0,
                      anim_in=tanim("drop", duration=0.5, unit="word", stagger=0.1),
                      anim_out=tanim("fade", duration=0.2)), label="Título")
    t.text(t.track("text", "Mensaje"), "Gracias por todo, papá", 1.2, 2.8, Box(40, 1660, 1000, 90),
           text_style("Work Sans", 54, [fill("#FFFFFF")], weight=600, anim_in=tanim("fade", duration=0.5),
                      anim_out=tanim("fade", duration=0.2)), label="Mensaje")
    full = t.track("video", "En grande")
    for i in range(3):
        start = 4.2 + i * 2.0
        t.photo(full, "", start, 2.0, FULL, [(0, {"s": 1.2}, "snap"), (0.2, {"s": 1.04}, "linear"), (2.0, {"s": 1.0})],
                reuse=f"p{i + 1}")
    t.photo(full, "man-04", 10.2, 1.8, FULL, [(0, {"s": 1.0}, "linear"), (1.8, {"s": 1.08})], label="Foto final")
    t.solid(t.track("shape", "Sombra"), "#000000", 4.2, 7.8, Box(0, 1100, 1080, 820),
            layers=[gradient([(0, navy, 0.0), (1, navy, 0.9)], angle=90), no_stroke()])
    words = t.track("text", "Palabras")
    for i, word in enumerate(["MI HÉROE", "MI GUÍA", "MI EJEMPLO"]):
        t.text(words, word, 4.2 + i * 2.0, 2.0, Box(40, 1320, 1000, 420),
               text_style("Alfa Slab One", 170, [shadow(mustard, 10, 10, 0, 1.0), fill("#FFFFFF")], weight=400,
                          line=0.95, keyframes={"pixelSize": keys([(0, 380, "snap"), (0.16, 170)])}),
               label=f"Palabra {i + 1}")
    t.text(t.track("text", "Cierre"), "Te quiero, papá", 10.3, 1.7, Box(40, 1340, 1000, 260),
           text_style("Alfa Slab One", 120, [shadow("#000000", 0, 8, 0, 0.6), fill(mustard)], weight=400,
                      anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1)), label="Cierre")
    t.text(t.track("text", "Firma"), "Con amor, Mateo", 10.6, 1.4, Box(40, 1640, 1000, 80),
           text_style("Work Sans", 50, [fill("#FFFFFF")], weight=600, anim_in=tanim("fade", duration=0.4)),
           label="Firma")
    t.adjust([effect("beat_shake", animated={"amount": spikes([4.2, 6.2, 8.2, 10.2], 0.7, 0.35)}, rotation=0.35),
              effect("stylize.vignette", amount=0.45)], name="Golpes")
    t.song("new-hero-in-town", 0.0, 0.85)
    return t


def fiestas_patrias() -> Template:
    """The red bands of the Peruvian flag slide in around a framed slideshow; «¡Viva el Perú!» and confetti."""
    t = Template("fiestas-patrias-peru", "Día de la patria", "National Day", "seasonal", 10.0,
                 order=1080, tags=["fiestas patrias", "día nacional", "independencia", "bandera", "orgullo"], thumb_at=6.2,
                 background="#FFFFFF")
    red, dark = "#D91023", "#9B0A16"
    t.solid(t.track("shape", "Fondo"), "#FFFFFF")
    t.solid(t.track("shape", "Banda izquierda"), red, 0, 10.0, Box(0, 0, 360, 1920), [(0, {"dy": -1920}, "out"),
                                                                                       (0.7, {})])
    t.solid(t.track("shape", "Banda derecha"), red, 0, 10.0, Box(720, 0, 360, 1920), [(0, {"dy": 1920}, "out"),
                                                                                       (0.7, {})])
    frame = centered(540, 1000, 660, 900)
    t.solid(t.track("shape", "Marco"), "#FFFFFF", 0.8, 9.2, frame, pop(0, 0.5), radius=18, kind="rounded-rectangle",
            layers=[shadow("#3D0006", 0, 18, 40, 0.4), stroke(6, dark), fill("#FFFFFF")])
    photos = t.track("video", "Fotos")
    clips = []
    for i, sample in enumerate(["city-03", "city-01", "friends-01", "family-04"]):
        start = 0.8 + i * 2.3
        motion = (pop(0, 0.5) + [(2.3, {"s": 1.05})]) if i == 0 else [(0, {"s": 1.0}, "linear"), (2.3, {"s": 1.06})]
        clips.append(t.photo(photos, sample, start, 2.3, centered(540, 1000, 620, 860), motion, label=f"Foto {i + 1}"))
    for a, b in zip(clips, clips[1:]):
        t.transition(photos, a, b, "glass_wipe", 0.5)
    t.solid(t.track("shape", "Cinta"), dark, 0.5, 9.5, Box(60, 180, 960, 230), pop(0, 0.45), radius=20,
            kind="rounded-rectangle", layers=[shadow("#3D0006", 0, 12, 24, 0.4), fill(dark), no_stroke()])
    t.text(t.track("text", "Título"), "¡Feliz día de la patria!", 0.7, 9.3, Box(80, 180, 920, 230),
           text_style("Cinzel", 70, [fill("#FFFFFF")], weight=900, line=1.05, anim_in=tanim("rise", duration=0.5)),
           label="Título")
    rng = random.Random(28)
    particles(t, "Confeti", 2, 1.2, 10.0, rng, [red, "#FFFFFF", "#FFD166"], kinds=("rectangle", "ellipse"),
              size=(16, 30), dy=2100, life=(3.5, 5.0), every=(0.3, 0.6), sway=120, spin=360)
    t.text(t.track("text", "Frase"), "¡Viva mi país!", 1.4, 8.6, Box(40, 1465, 1000, 230),
           text_style("Kaushan Script", 150, [shadow("#3D0006", 0, 8, 14, 0.5), stroke(10, "#FFFFFF"), fill(red)],
                      weight=400, anim_in=tanim("pop", duration=0.5, unit="word", stagger=0.15, ease="back"),
                      anim_loop=tanim("pulse", amount=4, speed=1.0)), label="Frase")
    t.text(t.track("text", "Fecha"), "DÍA NACIONAL", 2.0, 8.0, Box(290, 1720, 500, 90),
           text_style("Cinzel", 52, [fill("#FFFFFF")], weight=700, spacing=6, box=(dark, 1.0), box_pad=14,
                      box_radius=10, anim_in=tanim("fade", duration=0.5)), label="Fecha")
    t.adjust([effect("light_leak", intensity=0.25, hue=0.03, speed=0.5), effect("color.basic", vibrance=0.15)],
             name="Luz")
    t.song("go-on-without-me", 0.0, 0.85)
    return t


TEMPLATES = [dia_de_muertos_ofrenda,
             catrina, cancion_criolla, navidad_en_familia, feliz_navidad_luces, regalo_sorpresa, menu_navideno,
             cuenta_regresiva_anio_nuevo, mi_anio_en_fotos, propositos_anio_nuevo, black_friday_ofertas,
             black_friday_ultimas_horas, cyber_monday, san_valentin_carta, dia_de_la_amistad, dia_del_padre,
             fiestas_patrias]
