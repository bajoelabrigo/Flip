"""YouTuber-style templates (0.15.0, part B of docs/plan-stock.md): Intros de canal (5 s) y pantallas finales (20 s).
Category intro / outro; order 6500-6599; ids `yt-intro-*` and `yt-final-*`.

Intros (16:9, 5 s): a logo slot («Tu logo», square box: My brand fits the logo whole) revealed on a music hit,
then the channel name and a short line. The music cut is chosen so a strong onset of the track lands on the
reveal (`HITS`, measured on the musica.libre files: the start of the cut is the hit minus the reveal time).

End screens (16:9, 20 s): clear zones for the platform's end-screen elements: one or two 16:9 «Video sugerido»
slots and a round «Foto del canal» where the subscribe element goes, with thanks text and the channel handle,
over a background that moves calmly and comes back to its first state at 20 s (it can loop). Three 9:16 endings
for Shorts («sígueme para más») last 10 s: Shorts have no end-screen elements and a long ending loses viewers.
No platform logos, no platform red as the main colour, no youtuber names.
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, centered, circle_photo, dots, effect, fill, glow, gradient, grain,
                 hollow, keys, label, line, no_stroke, pill, pop, random, rrect, shade_full, shadow, slide_in, spike,
                 stroke, tanim, text_style, vignette, wide, tall)

O = 6500

# Strong onsets (s) in the musica.libre tracks, measured from the decoded audio (a jump of 15-45 dB over the
# half second before). The intro puts its reveal on one of them.
HITS = {
    "beat-one": 9.03, "experimental-test-subject": 21.85, "martini-sunset": 24.92, "llama-in-pajama": 18.76,
    "fresh-focus": 55.19, "groovin": 3.53, "piano-magic-motive": 24.89, "alien-invasion": 9.61,
    "emotional-blockbuster-2": 41.49, "magic-in-the-garden": 36.52, "arpent": 31.97, "hopeful": 7.66,
    "fake-it-til-you-fake-it": 14.58, "funkeriffic": 10.59, "city-sunshine": 57.19,
}


def hit_music(t, music_id: str, at: float, volume: float = 0.9) -> None:
    """The cut starts so the track's hit falls on `at` (template seconds)."""
    t.song(music_id, round(max(0.0, HITS[music_id] - at), 2), volume)


def _a(colour: str, alpha: float = 1.0) -> str:
    return f"#{max(0, min(255, round(alpha * 255))):02x}{colour.lstrip('#').lower()[-6:]}"


def sl(colour: str, width: float, alpha: float = 1.0, align: str = "center", dash: str | None = None,
       sketch: tuple | None = None, id: str = "stroke") -> dict:
    """A stroke layer (shapes and text): optional dash and hand-drawn wobble (length, deviation, seed)."""
    d = {"id": id, "kind": "stroke", "enabled": True, "width": width, "strokeAlign": align,
         "paint": {"kind": "solid", "color": _a(colour, alpha)}, "opacity": 1.0}
    if dash:
        d["dash"] = dash
    if sketch:
        d["sketchLength"], d["sketchDeviation"], d["sketchSeed"] = sketch
    return d


def radial(colour: str, alpha: float, edge: float = 0.0, id: str = "fill") -> dict:
    """A round soft light: `colour` at `alpha` in the middle, fading to `edge` at the rim."""
    return {"id": id, "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "gradient", "color": _a(colour, alpha),
                      "gradient": {"kind": "radial", "stops": [{"pos": 0, "color": _a(colour, alpha)},
                                                               {"pos": 1, "color": _a(colour, edge)}],
                                   "angle": 0, "space": "block"}}}


def tube(colour: str, core: str, width: float = 8) -> list:
    """Neon tube strokes for a hollow shape: a wide soft halo and a bright core (a glow layer would fill it)."""
    halo = sl(colour, width * 4, 0.28, id="halo")
    halo["blur"] = width * 2
    mid = sl(colour, width * 2, 0.6, id="mid")
    mid["blur"] = width
    return [hollow(), halo, mid, sl(core, width)]


def offset_shadow(colour: str, dx: float, dy: float, id: str = "shadow", blur: float = 0, opacity: float = 1.0):
    return shadow(colour, dx, dy, blur, opacity, id=id)


def outline_shape(t, track, colour, width, t0, dur, box, kind="ellipse", *, at: float | None = 0.0,
                  length: float = 0.6, motion=None, radius: float = 0, sketch=None, dash=None, glow_c=None,
                  alpha: float = 1.0, align: str = "center", **extra):
    """A hollow outline; with `at` it draws itself on (stroke trim) from `at` for `length` s (clip seconds)."""
    if glow_c:
        layers = tube(glow_c, colour, width)
        layers[-1].update(sl(colour, width, alpha, align, dash, sketch))
    else:
        layers = [hollow(), sl(colour, width, alpha, align, dash, sketch)]
    clip = t.solid(track, colour, t0, dur, box, motion, radius=radius, kind=kind, layers=layers, **extra)
    if at is not None:
        pts = [(0, 0.0, "hold"), (at, 0.0, "out"), (at + length, 1.0)] if at > 0 else [(0, 0.0, "out"), (length, 1.0)]
        clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": keys(pts)}
    return clip


def logo(t, sample: str, box: Box, t0: float, motion=None, dur: float | None = None, **extra):
    """The logo slot: square box, labelled so My brand puts the user's logo in it whole."""
    dur = t.duration - t0 if dur is None else dur
    return t.photo(t.track("video", "Logo"), sample, t0, dur, box, motion, label="Tu logo", **extra)


def loop(dx: float = 0.0, dy: float = 0.0, s: float = 1.0, period: float = 20.0, phase: float = 0.0) -> list:
    """A calm drift that comes back to where it started at `period` (so a 20 s end screen can loop)."""
    if phase:
        return [(0, {"dx": dx * phase, "dy": dy * phase, "s": 1 + (s - 1) * phase}, "smooth"),
                (period * (0.5 - phase / 2), {"dx": dx, "dy": dy, "s": s}, "smooth"),
                (period * (1 - phase / 2), {}, "smooth"), (period, {"dx": dx * phase, "dy": dy * phase,
                                                                     "s": 1 + (s - 1) * phase})]
    return [(0, {}, "smooth"), (period / 2, {"dx": dx, "dy": dy, "s": s}, "smooth"), (period, {})]


def intro(id, es, en, n, tags, thumb_at=3.0, background="#000000"):
    return wide(id, es, en, "intro", 5.0, order=O + n, tags=["intro", "youtuber", "canal", "logo"] + tags,
                thumb_at=thumb_at, background=background)


# ==== Intros (5 s) ===============================================================================

def intro_gaming():
    """Two neon slashes cross the screen, the logo slams in on the drop with a flash, HUD brackets frame it."""
    t = intro("yt-intro-gaming", "Intro gamer explosiva", "Explosive gamer intro", 0,
              ["gaming", "gamer", "neón", "videojuegos", "stream"], thumb_at=2.6, background="#07060F")
    bg_gradient(t, [(0, "#1E0B45"), (0.55, "#0A0718"), (1, "#05040B")], angle=90)
    rng = random.Random(6500)
    for k in range(12):
        tr = t.track("shape", "Velocidad")
        y = rng.uniform(60, 1020)
        w = rng.uniform(300, 900)
        start = rng.uniform(0, 0.8)
        speed = rng.uniform(0.7, 1.3)
        t.solid(tr, rng.choice(["#00F0FF", "#FF2E88", "#FFFFFF"]), start, 5.0 - start, Box(1920, y, w, rng.choice([3, 5])),
                [(0, {}, "linear"), (5.0 - start, {"dx": -(2600 + w) * speed})], alpha=rng.uniform(0.25, 0.6))
    for i, (c, y, dx, at) in enumerate([("#00F0FF", 330, -2600, 0.1), ("#FF2E88", 470, 2600, 0.3)]):
        t.solid(t.track("shape", "Corte"), c, at, 5.0 - at, centered(960, y, 1700, 230),
                [(0, {"dx": dx}, "snap"), (0.55, {}, "linear"), (5.0 - at, {"dx": -dx * 0.03})], kind="parallelogram",
                layers=[glow(c, 30, 0.8), fill(c, 0.85), no_stroke()])
    # HUD corner brackets around the logo
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = 960 + sx * 250, 400 + sy * 230
            for horiz in (True, False):
                b = centered(cx - sx * 40, cy, 90, 8) if horiz else centered(cx, cy - sy * 40, 8, 90)
                t.solid(t.track("shape", "Visor"), "#FFFFFF", 0.95, 4.05, b,
                        [(0, {"dx": sx * 140, "dy": sy * 120}, "snap"), (0.35, {})],
                        layers=[glow("#00F0FF", 14, 0.9), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Destello"), "#FFFFFF", 1.0, 0.35, t.full, opacity=keys([(0, 0.95, "out"), (0.35, 0.0)]))
    logo(t, "logo-08", centered(960, 400, 360, 360), 1.0,
         [(0, {"s": 2.6}, "snap"), (0.22, {"s": 1.0}, "linear"), (4.0, {"s": 1.06})])
    label(t, t.track("text", "Canal"), "ZONA GAMER", 1.2, 3.8, Box(160, 650, 1600, 190), "Russo One", 150, "#FFFFFF",
          weight=400, spacing=10, layers=[shadow("#000000", 0, 10, 24, 0.6), glow("#FF2E88", 26, 0.8),
                                          stroke(4, "#FF2E88"), fill("#FFFFFF")],
          anim_in=tanim("glitch-in", duration=0.45, offset=0.35, skew=25), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "NUEVOS VIDEOS · TODOS LOS DÍAS", 1.7, 3.3, Box(360, 850, 1200, 70), "Exo 2", 40,
          "#00F0FF", weight=700, spacing=8, anim_in=tanim("wipe", duration=0.5), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0, 3.0], 0.7, 0.35)}),
              effect("beat_shake", animated={"amount": spike([1.0], 0.6, 0.4)}),
              effect("rgb_split", animated={"amount": spike([1.0, 3.0], 22, 0.3)}),
              effect("bloom_glow", threshold=0.6, intensity=0.7, blurRadius=12)], name="Golpe")
    hit_music(t, "beat-one", 1.0)
    return t


def intro_vlog():
    """A strip of warm photo cards drifts across, the logo lands in a white circle, the name in script."""
    t = intro("yt-intro-vlog", "Intro de vlog en tira", "Vlog photo strip intro", 1,
              ["vlog", "viajes", "fotos", "día a día", "aesthetic"], thumb_at=3.0, background="#FFF4E2")
    bg_gradient(t, [(0, "#FFF6E8"), (1, "#F6DEC4")], angle=120)
    t.solid(t.track("shape", "Sol"), "#FFC48C", 0, 5.0, centered(1650, 160, 700, 700),
            [(0, {}, "smooth"), (5.0, {"dx": -60, "dy": 30})], kind="ellipse",
            layers=[radial("#FFB26B", 0.55), no_stroke()])
    samples = ["h-beach-02", "y7-h-vlogger-06", "h-cafe-04", "y7-h-laugh-03", "h-travel-02"]
    for i, s in enumerate(samples):
        st = i * 0.12

        def dx(at):
            return 360 - 150 * at
        x = 200 + i * 380
        motion = [(0, {"dx": dx(st), "dy": 700}, "out"), (0.6, {"dx": dx(st + 0.6)}, "linear"), (5.0 - st, {"dx": dx(5.0)})]
        frame = Box(x - 170 - 12, 240 - 12, 340 + 24, 430 + 24)
        rot = keys([(0, [-4, 3, -2, 4, -3][i])])
        t.solid(t.track("shape", "Marco"), "#FFFFFF", st, 5.0 - st, frame, motion, radius=10, kind="rounded-rectangle",
                layers=[shadow("#5A3A22", 0, 14, 30, 0.3), fill("#FFFDF8"), no_stroke()], rotation=rot)
        t.photo(t.track("video", f"Foto {i + 1}"), s, st, 5.0 - st, Box(x - 170, 240, 340, 430), motion,
                label=f"Foto {i + 1}", rotation=rot)
    t.solid(t.track("shape", "Círculo"), "#FFFFFF", 1.4, 3.6, centered(960, 455, 340, 340), pop(0, 0.5),
            kind="ellipse", layers=[shadow("#5A3A22", 0, 14, 34, 0.35), fill("#FFFFFF"), no_stroke()])
    logo(t, "logo-02", centered(960, 455, 250, 250), 1.45, pop(0, 0.5))
    label(t, t.track("text", "Canal"), "Valeria en ruta", 1.7, 3.3, Box(260, 750, 1400, 190), "Pacifico", 120,
          "#3D2C2E", weight=400, layers=[shadow("#FFFFFF", 0, 0, 18, 0.9), fill("#3D2C2E")],
          anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.15), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "VLOGS · VIAJES · DÍA A DÍA", 2.2, 2.8, Box(360, 950, 1200, 60), "Montserrat", 34,
          "#C8553D", weight=700, spacing=10, anim_in=tanim("fade", duration=0.5), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.4], 0.35, 0.4)})], name="Golpe")
    grain(t, 0.12)
    hit_music(t, "city-sunshine", 1.4)
    return t


def intro_tech():
    """Circuit traces draw in from the edges to a glowing bezel; a scan line reveals the logo."""
    t = intro("yt-intro-tech", "Intro tecnológica de circuito", "Circuit tech intro", 2,
              ["tecnología", "tech", "reseñas", "gadgets", "circuito"], thumb_at=3.0, background="#050B16")
    bg_gradient(t, [(0, "#0A1A33"), (1, "#03070F")], angle=90)
    for k in range(1, 16):
        t.solid(t.track("shape", "Rejilla"), "#1C3A5E", 0, 5.0, Box(k * 120, 0, 2, 1080), alpha=0.35)
    for k in range(1, 9):
        t.solid(t.track("shape", "Rejilla"), "#1C3A5E", 0, 5.0, Box(0, k * 120, 1920, 2), alpha=0.35)
    # (box, grows from, node at the inner end)
    traces = [(Box(0, 297, 780, 6), "left", (780, 300)), (Box(1140, 297, 780, 6), "right", (1140, 300)),
              (Box(0, 537, 780, 6), "left", (780, 540)), (Box(1140, 537, 780, 6), "right", (1140, 540)),
              (Box(957, 0, 6, 240), "top", (960, 240))]
    for i, (b, side, node) in enumerate(traces):
        motion = {"left": [(0, {"sx": 0.0, "dx": -b.w / 2}, "out"), (0.6, {})],
                  "right": [(0, {"sx": 0.0, "dx": b.w / 2}, "out"), (0.6, {})],
                  "top": [(0, {"sy": 0.0, "dy": -b.h / 2}, "out"), (0.6, {})]}[side]
        t.solid(t.track("shape", "Circuito"), "#39D0FF", 0.1 + i * 0.08, 4.9 - i * 0.08, b, motion,
                layers=[glow("#39D0FF", 16, 0.9), fill("#39D0FF"), no_stroke()])
        t.solid(t.track("shape", "Nodo"), "#FFFFFF", 0.7 + i * 0.08, 4.3 - i * 0.08, centered(node[0], node[1], 26, 26),
                pop(0, 0.3), kind="ellipse", layers=[glow("#39D0FF", 16, 1.0), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Marco"), "#0B1B33", 0.9, 4.1, centered(960, 420, 330, 330), pop(0, 0.4, 0.7), radius=56,
            kind="rounded-rectangle", layers=[glow("#39D0FF", 30, 0.8), fill("#0B1B33"), sl("#39D0FF", 5)])
    logo(t, "logo-07", centered(960, 420, 240, 240), 1.0, [(0, {"s": 0.9}, "out"), (4.0, {"s": 1.03})],
         opacity=keys([(0, 0.0, "hold"), (0.05, 0.0, "smooth"), (0.5, 1.0)]))
    t.solid(t.track("shape", "Escaneo"), "#BFF3FF", 1.0, 0.7, centered(960, 270, 360, 6),
            [(0, {}, "smooth"), (0.7, {"dy": 300})], layers=[glow("#39D0FF", 20, 1.0), fill("#BFF3FF"), no_stroke()],
            opacity=keys([(0, 1.0, "smooth"), (0.6, 1.0, "smooth"), (0.7, 0.0)]))
    label(t, t.track("text", "Canal"), "TECNO CLARO", 1.4, 3.6, Box(160, 650, 1600, 160), "Sora", 118, "#FFFFFF",
          weight=600, spacing=16, anim_in=tanim("rise", duration=0.5, unit="character", stagger=0.035),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "> reseñas · trucos · novedades", 1.9, 3.1, Box(360, 830, 1200, 70),
          "Titillium Web", 42, "#39D0FF", weight=600, spacing=2,
          anim_in=tanim("typewriter", duration=0.8, unit="character", stagger=0.025), name="Lema")
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.8, blurRadius=12),
              effect("zoom_pulse", animated={"punch": spike([1.0], 0.5, 0.3)})], name="Brillo")
    hit_music(t, "experimental-test-subject", 1.0)
    return t


def intro_belleza():
    """Blush gradient, an oval photo with a gold line drawing round it, sparkles and a serif italic name."""
    t = intro("yt-intro-belleza", "Intro de belleza suave", "Soft beauty intro", 3,
              ["belleza", "maquillaje", "skincare", "elegante", "rosa"], thumb_at=3.2, background="#F7E6E1")
    bg_gradient(t, [(0, "#FBEFEA"), (1, "#EFCFCB")], angle=135)
    for c, x, y, s in [("#F4B6B9", 1500, 200, 900), ("#FFFFFF", 300, 950, 800)]:
        t.solid(t.track("shape", "Luz"), c, 0, 5.0, centered(x, y, s, s), [(0, {}, "smooth"), (5.0, {"dx": -80, "dy": 40})],
                kind="ellipse", layers=[radial(c, 0.6), no_stroke()])
    tr = t.track("video", "Foto")
    clip = t.photo(tr, "y7-h-beauty-04", 0.0, 5.0, centered(560, 540, 560, 780),
                   [(0, {"s": 1.08}, "out"), (1.0, {"s": 1.0}, "linear"), (5.0, {"s": 1.03})], label="Tu foto o video",
                   opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0)]))
    t.mask(tr, clip, "ellipse")
    outline_shape(t, t.track("shape", "Línea dorada"), "#C9A15B", 4, 0.3, 4.7, centered(590, 560, 600, 820),
                  at=0.0, length=1.2)
    t.solid(t.track("shape", "Fondo logo"), "#FFFFFF", 1.0, 4.0, centered(1340, 330, 260, 260), pop(0, 0.5),
            kind="ellipse", layers=[shadow("#8A3B4E", 0, 12, 30, 0.2), fill("#FFFFFF"), no_stroke()])
    logo(t, "logo-06", centered(1340, 330, 190, 190), 1.05, pop(0, 0.5))
    label(t, t.track("text", "Canal"), "Belleza con Lu", 1.3, 3.7, Box(900, 500, 900, 170), "Playfair Display", 112,
          "#6B2E3E", weight=500, italic=True, anim_in=tanim("blur-in", duration=0.7, unit="character", stagger=0.03),
          name="Nombre del canal")
    line(t, t.track("shape", "Línea"), "#C9A15B", 1.7, 3.3, centered(1350, 690, 260, 3), grow="c", length=0.6)
    label(t, t.track("text", "Lema"), "MAQUILLAJE · CUIDADO · ESTILO", 1.9, 3.1, Box(900, 720, 900, 60), "Montserrat",
          32, "#B76E79", weight=600, spacing=8, anim_in=tanim("fade", duration=0.6), name="Lema")
    rng = random.Random(6503)
    for k in range(9):
        x, y = rng.uniform(1000, 1720), rng.uniform(160, 860)
        s = rng.uniform(22, 48)
        at = 1.1 + rng.uniform(0, 2.4)
        t.solid(t.track("shape", "Brillo"), rng.choice(["#C9A15B", "#FFFFFF"]), at, 1.2, centered(x, y, s, s),
                [(0, {"s": 0.0}, "back"), (0.4, {"s": 1.0}, "smooth"), (1.2, {"s": 0.0})], kind="star",
                layers=[glow("#FFFFFF", 10, 0.8), fill("#E8C88A"), no_stroke()],
                rotation=keys([(0, 0), (1.2, 90)]))
    hit_music(t, "martini-sunset", 1.0)
    return t


def intro_comedia():
    """A turning sunburst on yellow, the logo squashes in, «JA» bubbles pop round the bouncy name."""
    t = intro("yt-intro-comedia", "Intro de comedia", "Comedy intro", 4,
              ["comedia", "humor", "divertido", "sketch", "risas"], thumb_at=2.8, background="#FFD60A")
    bg(t, "#FFD60A")
    rays = t.solid(t.track("shape", "Rayos"), "#FFE66D", 0, 5.0, centered(960, 540, 2600, 2600), kind="star",
                   layers=[fill("#FFE66D"), no_stroke()], rotation=keys([(0, 0), (5.0, 50)]))
    rays["shapeStyle"].update(points=18, innerRatio=0.12)
    t.solid(t.track("shape", "Círculo"), "#FFFFFF", 0.8, 4.2, centered(960, 380, 330, 330),
            [(0, {"sx": 1.6, "sy": 0.2}, "out"), (0.18, {"sx": 0.8, "sy": 1.25}, "smooth"), (0.36, {"sx": 1.08, "sy": 0.94}, "smooth"),
             (0.5, {})], kind="ellipse", layers=[offset_shadow("#111111", 10, 10), fill("#FFFFFF"), sl("#111111", 9, align="inside")])
    logo(t, "logo-03", centered(960, 380, 240, 240), 0.85, pop(0, 0.45))
    bubbles = [(380, 260, -10, 1.2), (1540, 250, 8, 1.5), (250, 930, 6, 2.2), (1670, 930, -8, 2.5)]
    for i, (x, y, r, at) in enumerate(bubbles):
        b = centered(x, y, 250, 170)
        t.solid(t.track("shape", "Bocadillo"), "#FFFFFF", at, 5.0 - at, b, pop(0, 0.35), kind="speech-bubble",
                layers=[offset_shadow("#111111", 6, 6), fill("#FFFFFF"), sl("#111111", 6, align="inside")],
                rotation=keys([(0, r)]))
        label(t, t.track("text", "Risa"), "¡JA!" if i % 2 == 0 else "JAJA", at, 5.0 - at, centered(x, y - 14, 240, 110),
              "Luckiest Guy", 70 if i % 2 == 0 else 58, "#FF3B6B", weight=400, editable=False, motion=pop(0, 0.35),
              rotation=keys([(0, r)]))
    label(t, t.track("text", "Canal"), "RISAS SIN FILTRO", 1.1, 3.9, Box(160, 600, 1600, 200), "Luckiest Guy", 140,
          "#FFFFFF", weight=400, spacing=4, layers=[offset_shadow("#111111", 10, 10), stroke(8, "#111111"), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.035), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "sketches nuevos cada viernes", 1.8, 3.2, Box(360, 830, 1200, 80), "Baloo 2", 50,
          "#111111", weight=800, anim_in=tanim("pop", duration=0.4), name="Lema")
    t.adjust([effect("beat_shake", animated={"amount": spike([0.8], 0.5, 0.35)}),
              effect("zoom_pulse", animated={"punch": spike([0.8], 0.5, 0.3)})], name="Golpe")
    hit_music(t, "llama-in-pajama", 0.8)
    return t


def intro_educacion():
    """A notebook page draws its lines, a pencil circle goes round the logo, a highlighter marks the name."""
    t = intro("yt-intro-educacion", "Intro de clase en cuaderno", "Notebook class intro", 5,
              ["educación", "clases", "aprender", "cuaderno", "tutorial"], thumb_at=3.2, background="#FBF8EF")
    bg(t, "#FBF8EF")
    for k in range(13):
        line(t, t.track("shape", "Renglón"), "#9EC5F0", k * 0.03, 5.0 - k * 0.03, Box(0, 120 + k * 72, 1920, 3),
             length=0.5)
    line(t, t.track("shape", "Margen"), "#F28B82", 0.2, 4.8, Box(240, 0, 4, 1080), grow="y", length=0.5)
    t.solid(t.track("shape", "Resaltador"), "#FFE45E", 1.3, 3.7, Box(765, 385, 690, 115),
            [(0, {"sx": 0.0, "dx": -345}, "out"), (0.45, {})], alpha=0.75, rotation=keys([(0, -1.5)]))
    logo(t, "logo-01", centered(540, 470, 290, 290), 1.0, pop(0, 0.45))
    outline_shape(t, t.track("shape", "Lápiz"), "#2B59C3", 7, 1.0, 4.0, centered(540, 470, 400, 380), at=0.0,
                  length=0.6, sketch=(18, 4, 7), rotation=keys([(0, -6)]))
    label(t, t.track("text", "Canal"), "Aprende Fácil", 1.2, 3.8, Box(780, 360, 1060, 160), "Fredoka", 128, "#1F2A44",
          weight=600, align="left", anim_in=tanim("wipe", duration=0.5, angle=0), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "ciencia, historia y más en 10 minutos", 1.8, 3.2, Box(780, 540, 1060, 90), "Caveat",
          60, "#2B59C3", weight=700, align="left", anim_in=tanim("typewriter", duration=0.9, unit="character", stagger=0.025),
          name="Lema")
    outline_shape(t, t.track("shape", "Garabato"), "#F28B82", 6, 2.0, 3.0, centered(1660, 220, 120, 120), "star",
                  at=0.0, length=0.5, sketch=(14, 3, 3))
    outline_shape(t, t.track("shape", "Garabato"), "#2B59C3", 6, 2.3, 2.7, Box(780, 700, 220, 120), "curved-arrow",
                  at=0.0, length=0.5, sketch=(14, 3, 5))
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0], 0.35, 0.3)})], name="Golpe")
    hit_music(t, "fresh-focus", 1.0)
    return t


def intro_musica():
    """A record slides in and spins (its sheen turns), the logo on the label, an equaliser under the name."""
    t = intro("yt-intro-musica", "Intro de vinilo", "Vinyl music intro", 6,
              ["música", "vinilo", "covers", "artista", "disco"], thumb_at=3.0, background="#0D0D0F")
    bg_gradient(t, [(0, "#1E1418"), (1, "#0B0B0D")], angle=0)
    t.solid(t.track("shape", "Foco"), "#E63946", 0, 5.0, centered(760, 540, 1300, 1300), kind="ellipse",
            layers=[radial("#E63946", 0.28), no_stroke()])
    rec = centered(760, 540, 780, 780)
    enter = [(0, {"dx": -1200}, "out"), (0.8, {})]
    t.solid(t.track("shape", "Disco"), "#0A0A0A", 0, 5.0, rec, enter, kind="ellipse",
            layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#0A0A0A"), no_stroke()])
    for k, r in enumerate([720, 640, 560, 480, 400]):
        t.solid(t.track("shape", "Surco"), "#2A2A30", 0, 5.0, centered(760, 540, r, r), enter, kind="ellipse",
                layers=[hollow(), sl("#26262C", 3)])
    for ang in (0, 90):
        t.solid(t.track("shape", "Reflejo"), "#FFFFFF", 0, 5.0, centered(760, 540, 760, 70), enter, kind="ellipse",
                layers=[gradient([(0, "#FFFFFF", 0.0), (0.5, "#FFFFFF", 0.12), (1, "#FFFFFF", 0.0)], angle=0), no_stroke()],
                rotation=keys([(0, ang + 30), (5.0, ang + 30 - 540)]))
    t.solid(t.track("shape", "Etiqueta"), "#E63946", 0, 5.0, centered(760, 540, 300, 300), enter, kind="ellipse")
    logo(t, "logo-07", centered(760, 540, 210, 210), 1.0, pop(0, 0.4))
    label(t, t.track("text", "Canal"), "SONIDO NORTE", 1.0, 4.0, Box(1240, 300, 620, 380), "Bebas Neue", 190,
          "#F1FAEE", weight=400, align="left", line=0.9, spacing=4,
          anim_in=tanim("slide-left", duration=0.45, unit="character", stagger=0.04, ease="back"),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "covers · sesiones en vivo", 1.5, 3.5, Box(1240, 690, 620, 60), "Montserrat", 36,
          "#E63946", weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Lema")
    rng = random.Random(6506)
    for i in range(16):
        x = 1250 + i * 38
        pts, at = [(0, {"sy": 0.15})], 0.0
        while at < 3.6:
            at += rng.uniform(0.15, 0.3)
            pts.append((at, {"sy": rng.uniform(0.2, 1.0)}, "smooth"))
        t.solid(t.track("shape", "Ecualizador"), "#F1FAEE" if i % 4 else "#E63946", 1.4, 3.6,
                Box(x, 790, 22, 150), [(p[0], {**p[1], "dy": 75 * (1 - p[1]["sy"])}) + tuple(p[2:]) for p in pts],
                radius=4, kind="rounded-rectangle")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0, 3.0], 0.45, 0.3)})], name="Golpe")
    hit_music(t, "groovin", 1.0)
    return t


def intro_minimal():
    """A dot breathes, opens into a black circle that fills the frame, and the logo and name settle in."""
    t = intro("yt-intro-minimal", "Intro minimal de punto", "Minimal dot intro", 7,
              ["minimal", "limpio", "elegante", "marca", "blanco y negro"], thumb_at=3.4, background="#F4F1EA")
    bg(t, "#F4F1EA")
    t.solid(t.track("shape", "Punto"), "#111111", 0.2, 4.8, centered(960, 540, 40, 40),
            [(0, {"s": 0.0}, "back"), (0.35, {"s": 1.0}, "smooth"), (0.6, {"s": 0.8}, "smooth"), (0.8, {"s": 1.0}, "in"),
             (1.25, {"s": 72.0})], kind="ellipse")
    logo(t, "logo-07", centered(960, 430, 250, 250), 1.3, [(0, {"s": 0.85}, "out"), (1.0, {"s": 1.0}, "linear"),
                                                            (3.7, {"s": 1.03})],
         opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0)]))
    label(t, t.track("text", "Canal"), "ESTUDIO NORTE", 1.8, 3.2, Box(260, 610, 1400, 120), "Inter", 76, "#FFFFFF",
          weight=300, spacing=26, anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.03),
          name="Nombre del canal")
    line(t, t.track("shape", "Línea"), "#FFFFFF", 2.3, 2.7, centered(960, 760, 360, 2), grow="c", length=0.7)
    label(t, t.track("text", "Lema"), "diseño y fotografía", 2.6, 2.4, Box(560, 790, 800, 60), "Inter", 32, "#A8A8A8",
          weight=400, spacing=8, anim_in=tanim("fade", duration=0.6), name="Lema")
    t.solid(t.track("shape", "Acento"), "#E63946", 2.8, 2.2, centered(1162, 760, 14, 14), pop(0, 0.3), kind="ellipse")
    hit_music(t, "piano-magic-motive", 1.0, 0.85)
    return t


def intro_glitch():
    """Colour bars and «SIN SEÑAL» break up, cut to black: the logo tears in with RGB split and VHS noise."""
    t = intro("yt-intro-glitch", "Intro de señal perdida", "Lost signal glitch intro", 8,
              ["glitch", "vhs", "señal", "digital", "retro"], thumb_at=2.6, background="#000000")
    bg(t, "#000000")
    bars = ["#C0C0C0", "#C0C000", "#00C0C0", "#00C000", "#C000C0", "#C00000", "#0000C0"]
    for i, c in enumerate(bars):
        t.solid(t.track("shape", "Barras"), c, 0, 1.2, Box(i * 1920 / 7, 0, 1920 / 7 + 1, 820))
    for i, c in enumerate(["#0000C0", "#111111", "#C000C0", "#111111", "#00C0C0", "#111111", "#C0C0C0"]):
        t.solid(t.track("shape", "Barras"), c, 0, 1.2, Box(i * 1920 / 7, 820, 1920 / 7 + 1, 260))
    label(t, t.track("text", "Aviso"), "SIN SEÑAL", 0.15, 1.05, centered(960, 410, 900, 150), "VT323", 130, "#FFFFFF",
          weight=400, spacing=10, box_bg=("#000000", 0.85), box_pad=24, editable=False)
    rng = random.Random(6508)
    for k in range(14):
        at = rng.choice([rng.uniform(0.3, 1.2), rng.uniform(1.2, 2.0), rng.uniform(3.4, 3.9)])
        w, h = rng.uniform(200, 900), rng.uniform(20, 90)
        t.solid(t.track("shape", "Bloque"), rng.choice(["#00F0FF", "#FF2E88", "#FFFFFF"]), at, rng.uniform(0.05, 0.12),
                Box(rng.uniform(0, 1920 - w), rng.uniform(0, 1080 - h), w, h), alpha=0.85)
    logo(t, "logo-08", centered(960, 400, 340, 340), 1.2, [(0, {"s": 1.25}, "snap"), (0.2, {"s": 1.0}, "linear"),
                                                            (3.8, {"s": 1.05})])
    label(t, t.track("text", "Grabando"), "● REC", 1.2, 3.8, Box(90, 60, 300, 70), "VT323", 60, "#FF3B3B", weight=400,
          align="left", editable=False, anim_loop=tanim("flicker", intensity=0.5, speed=2))
    label(t, t.track("text", "Contador"), "SP  0:00:05", 1.2, 3.8, Box(1430, 60, 400, 70), "VT323", 60, "#FFFFFF",
          weight=400, align="right", editable=False)
    for b in [Box(80, 140, 120, 5), Box(80, 140, 5, 100), Box(1720, 140, 120, 5), Box(1835, 140, 5, 100),
              Box(80, 935, 120, 5), Box(80, 840, 5, 100), Box(1720, 935, 120, 5), Box(1835, 840, 5, 100)]:
        t.solid(t.track("shape", "Visor"), "#FFFFFF", 1.2, 3.8, b, alpha=0.8)
    label(t, t.track("text", "Canal"), "PIXEL ROTO", 1.4, 3.6, Box(160, 640, 1600, 180), "Audiowide", 140, "#FFFFFF",
          weight=400, spacing=8,
          layers=[offset_shadow("#00F0FF", -8, 0, opacity=0.9), offset_shadow("#FF2E88", 8, 0, id="shadow2", opacity=0.9),
                  fill("#FFFFFF")],
          anim_in=tanim("glitch-in", duration=0.5, offset=0.4, skew=30), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "▶ REC  ·  NUEVO EPISODIO", 1.7, 3.3, Box(460, 840, 1000, 70), "VT323", 60,
          "#00F0FF", weight=400, spacing=4, anim_in=tanim("typewriter", duration=0.7, unit="character", stagger=0.025), name="Lema")
    t.adjust([effect("digital_glitch", animated={"intensity": spike([0.35, 0.8, 1.2, 1.6, 3.6], 0.95, 0.22)},
                     rgbAmount=20, blockAmount=0.6),
              effect("rgb_split", animated={"amount": spike([1.2, 1.6, 3.6], 28, 0.3)}),
              effect("stylize.vhs", noise=18, chroma=3, saturation=1.0)], name="Glitch")
    hit_music(t, "alien-invasion", 1.2)
    return t


def intro_3d():
    """A perspective floor, the logo card swings round in 3D and the name rises out of the floor, extruded."""
    t = intro("yt-intro-3d", "Intro 3D de tarjeta", "3D card intro", 9,
              ["3d", "profundidad", "épico", "cinemático", "brillante"], thumb_at=3.2, background="#0A0E1F")
    bg_gradient(t, [(0, "#1A2560"), (0.55, "#0A0E1F"), (1, "#05060D")], angle=90)
    vx, vy = 960, 640
    for k in range(-8, 9):
        bx, by = 960 + k * 260, 1080
        length = ((bx - vx) ** 2 + (by - vy) ** 2) ** 0.5
        ang = __import__("math").degrees(__import__("math").atan2(by - vy, bx - vx))
        t.solid(t.track("shape", "Suelo"), "#4C6FFF", 0, 5.0, centered((vx + bx) / 2, (vy + by) / 2, length, 3),
                alpha=0.35, rotation=keys([(0, ang)]))
    for k in range(6):
        y0 = 650 + (k ** 1.8) * 18
        y1 = 650 + ((k + 1) ** 1.8) * 18
        t.solid(t.track("shape", "Suelo"), "#4C6FFF", 0, 5.0, Box(0, y0, 1920, 3),
                [(0, {}, "linear"), (5.0, {"dy": y1 - y0})], alpha=0.3)
    t.solid(t.track("shape", "Horizonte"), "#7FA0FF", 0, 5.0, centered(960, 640, 1920, 260), kind="ellipse",
            layers=[radial("#7FA0FF", 0.35), no_stroke()])
    swing = keys([(0, -100, "out"), (0.9, 0, "smooth"), (4.0, -14)])
    t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", 1.0, 4.0, centered(960, 360, 380, 380), radius=60,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 30, 50, 0.6),
                                              gradient([(0, "#FFFFFF"), (1, "#C9D6FF")], angle=135), no_stroke()],
            rotationY=swing)
    logo(t, "logo-01", centered(960, 360, 290, 290), 1.0, rotationY=swing)
    style = text_style("Archivo Black", 150, [shadow("#000000", 0, 30, 40, 0.5),
                                              {"id": "extrude", "kind": "extrude", "enabled": True,
                                               "paint": {"kind": "solid", "color": "#ff2c3e91"}, "width": 22,
                                               "extrudeSteps": 14, "extrudeAngle": 90, "extrudeDarken": 0.35,
                                               "opacity": 1.0},
                                              gradient([(0, "#FFFFFF"), (1, "#AFC4FF")], angle=90)],
                       weight=400, spacing=6, anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.04,
                                                             ease="back"))
    t.text(t.track("text", "Canal"), "NIVEL ÉPICO", 1.5, 3.5, Box(160, 620, 1600, 200), style, label="Nombre del canal",
           rotationX=keys([(0, 50, "out"), (0.8, 0)]))
    label(t, t.track("text", "Lema"), "historias que se sienten de cerca", 2.2, 2.8, Box(360, 860, 1200, 60), "Manrope",
          38, "#9FB4FF", weight=600, spacing=4, anim_in=tanim("fade", duration=0.6), name="Lema")
    t.adjust([effect("bloom_glow", threshold=0.7, intensity=0.6, blurRadius=14),
              effect("zoom_pulse", animated={"punch": spike([1.0], 0.5, 0.35)})], name="Brillo")
    hit_music(t, "emotional-blockbuster-2", 1.0)
    return t


def intro_a_mano():
    """Doodles draw themselves in marker on paper: two wobbly circles round the logo, stars, an arrow, a scribble."""
    t = intro("yt-intro-a-mano", "Intro dibujada a mano", "Hand-drawn intro", 10,
              ["dibujado", "a mano", "manualidades", "creativo", "doodle"], thumb_at=3.2, background="#FFFDF6")
    bg(t, "#FFFDF6")
    t.solid(t.track("shape", "Mancha"), "#FFD93D", 0.4, 4.6, centered(560, 470, 420, 400), pop(0, 0.5, 0.4),
            kind="cloud", alpha=0.55, rotation=keys([(0, 8)]))
    outline_shape(t, t.track("shape", "Trazo"), "#222222", 7, 0.0, 5.0, centered(560, 470, 420, 400), at=0.1,
                  length=0.7, sketch=(22, 5, 11))
    outline_shape(t, t.track("shape", "Trazo"), "#222222", 4, 0.0, 5.0, centered(570, 460, 440, 410), at=0.4,
                  length=0.6, sketch=(22, 6, 29), rotation=keys([(0, 12)]))
    logo(t, "logo-03", centered(560, 470, 280, 280), 0.9,
         [(0, {"s": 0.0}, "back"), (0.4, {"s": 1.0}, "smooth"), (2.0, {"s": 1.0}, "smooth"), (4.1, {"s": 1.03})],
         rotation=keys([(0, -8, "out"), (0.4, 0)]))
    label(t, t.track("text", "Canal"), "Hecho en Casa", 1.1, 3.9, Box(860, 330, 980, 170), "Permanent Marker", 120,
          "#222222", weight=400, align="left", anim_in=tanim("typewriter", duration=0.8, unit="character", stagger=0.04),
          name="Nombre del canal")
    t.solid(t.track("shape", "Subrayado"), "#FF6B6B", 1.8, 3.2, Box(860, 500, 760, 16),
            [(0, {"sx": 0.0, "dx": -380}, "out"), (0.4, {})], radius=8, kind="rounded-rectangle",
            rotation=keys([(0, -1.5)]))
    label(t, t.track("text", "Lema"), "manualidades · ideas · hazlo tú", 2.0, 3.0, Box(860, 540, 980, 90), "Caveat", 64,
          "#4D96FF", weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Lema")
    for (kind, box, c, at, seed) in [("star", centered(1650, 200, 110, 110), "#FFB703", 1.4, 3),
                                     ("star", centered(260, 170, 80, 80), "#6BCB77", 1.6, 4),
                                     ("heart", centered(300, 860, 110, 100), "#FF6B6B", 1.9, 5),
                                     ("curved-arrow", Box(880, 700, 240, 140), "#4D96FF", 2.1, 6),
                                     ("lightning-bolt", centered(1700, 820, 90, 140), "#FFB703", 2.3, 7)]:
        outline_shape(t, t.track("shape", "Garabato"), c, 6, at, 5.0 - at, box, kind, at=0.0, length=0.45,
                      sketch=(16, 4, seed))
    hit_music(t, "magic-in-the-garden", 0.9)
    return t


def intro_neon():
    """A neon tube frame flickers on in a dark room, the logo and the name light up, the sign hums."""
    t = intro("yt-intro-neon", "Intro de letrero neón", "Neon sign intro", 11,
              ["neón", "letrero", "noche", "stream", "música"], thumb_at=3.2, background="#0B0710")
    bg_gradient(t, [(0, "#1A0F22"), (1, "#07050A")], angle=90)
    t.solid(t.track("shape", "Halo"), "#FF2EF7", 0.9, 4.1, centered(960, 520, 1500, 900), kind="ellipse",
            layers=[radial("#FF2EF7", 0.22), no_stroke()],
            opacity=keys([(0, 0.0, "hold"), (0.1, 1.0, "hold"), (0.18, 0.2, "hold"), (0.3, 1.0)]))
    flick = keys([(0, 0.0, "hold"), (0.1, 1.0, "hold"), (0.16, 0.1, "hold"), (0.24, 1.0, "hold"), (0.3, 0.3, "hold"),
                  (0.38, 1.0, "hold"), (2.6, 0.55, "hold"), (2.66, 1.0)])
    t.solid(t.track("shape", "Tubo"), "#FF2EF7", 0.9, 4.1, Box(330, 230, 1260, 560), radius=60,
            kind="rounded-rectangle", layers=tube("#FF2EF7", "#FFD6FB", 9), opacity=flick)
    logo(t, "logo-08", centered(600, 510, 280, 280), 1.05, pop(0, 0.4, 0.8),
         opacity=keys([(0, 0.0, "hold"), (0.12, 1.0, "hold"), (0.2, 0.3, "hold"), (0.28, 1.0)]))
    label(t, t.track("text", "Canal"), "NOCHE NEÓN", 1.2, 3.8, Box(800, 380, 740, 260), "Monoton", 100, "#FFE6FB",
          weight=400, line=1.15, layers=[glow("#FF2EF7", 30, 1.0), glow("#FF2EF7", 8, 1.0, id="glow2"), fill("#FFE6FB")],
          anim_in=tanim("flicker-in", duration=0.7), anim_loop=tanim("flicker", intensity=0.08, speed=5),
          name="Nombre del canal")
    t.solid(t.track("shape", "Línea"), "#00F0FF", 1.6, 3.4, Box(820, 670, 600, 8), [(0, {"sx": 0.0, "dx": -300}, "out"),
                                                                               (0.4, {})], radius=4,
            kind="rounded-rectangle", layers=[glow("#00F0FF", 18, 1.0), fill("#C8FCFF"), no_stroke()])
    label(t, t.track("text", "Lema"), "streams · música · charlas", 1.9, 3.1, Box(360, 860, 1200, 80), "Righteous", 46,
          "#C8FCFF", weight=400, spacing=4, layers=[glow("#00F0FF", 18, 0.9), fill("#C8FCFF")],
          anim_in=tanim("flicker-in", duration=0.5), name="Lema")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.9, blurRadius=14),
              effect("zoom_pulse", animated={"punch": spike([1.0], 0.35, 0.3)})], name="Brillo")
    vignette(t, 0.6)
    hit_music(t, "arpent", 1.0)
    return t


def intro_papel():
    """Paper hills rise in layers with soft shadows, a sun comes up, the logo drops in on a paper tag."""
    t = intro("yt-intro-papel", "Intro de papel en capas", "Layered paper intro", 12,
              ["papel", "manualidades", "infantil", "familia", "colores"], thumb_at=3.0, background="#BDE0FE")
    bg_gradient(t, [(0, "#A9D6FF"), (1, "#E7F4FF")], angle=90)
    t.solid(t.track("shape", "Sol"), "#FFC75F", 0, 5.0, centered(1500, 300, 260, 260),
            [(0, {"dy": 700}, "out"), (1.0, {}, "linear"), (5.0, {"dy": -20})], kind="ellipse",
            layers=[shadow("#E09F3E", 0, 8, 0, 0.6), fill("#FFC75F"), no_stroke()])
    for i, (x, dur) in enumerate([(300, 5.0), (1300, 5.0)]):
        t.solid(t.track("shape", "Nube"), "#FFFFFF", 0.2 + i * 0.2, 4.8 - i * 0.2, centered(x, 180 + i * 70, 300, 150),
                [(0, {"dx": -200 if i == 0 else 200}, "out"), (0.8, {}, "linear"), (4.8, {"dx": 60})], kind="cloud",
                layers=[shadow("#6C8EAD", 0, 8, 12, 0.3), fill("#FFFFFF"), no_stroke()])
    hills = [("#8AC926", 400, 760, 1700, 700), ("#52A447", 1500, 800, 1800, 700), ("#1B7F5C", 700, 900, 2000, 600),
             ("#0F5C4A", 1400, 1010, 2400, 600)]
    for i, (c, x, y, w, h) in enumerate(hills):
        sway = 30 * (1 if i % 2 else -1)
        t.solid(t.track("shape", "Colina"), c, 0.05 + i * 0.12, 4.95 - i * 0.12, centered(x, y + h / 2, w, h),
                [(0, {"dy": 700}, "out"), (0.7, {}, "smooth"), (4.95 - i * 0.12, {"dx": sway})], kind="ellipse",
                layers=[shadow("#0B3B2E", 0, -10, 24, 0.35), fill(c), no_stroke()])
    tag = centered(960, 330, 300, 300)
    drop = [(0, {"dy": -700}, "back"), (0.55, {})]
    t.solid(t.track("shape", "Etiqueta"), "#FFFFFF", 1.0, 4.0, tag, drop, radius=34, kind="rounded-rectangle",
            layers=[shadow("#1D3557", 0, 14, 22, 0.35), fill("#FFFFFF"), no_stroke()], rotation=keys([(0, -4)]))
    logo(t, "logo-03", centered(960, 330, 240, 240), 1.0, drop, rotation=keys([(0, -4)]))
    label(t, t.track("text", "Canal"), "Pequeños Exploradores", 1.3, 3.7, Box(160, 520, 1600, 150), "Baloo 2", 110,
          "#1D3557", weight=800, layers=[stroke(12, "#FFFFFF"), fill("#1D3557")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.12), name="Nombre del canal")
    pill(t, t.track("shape", "Cinta"), "#FFFFFF", 1.8, 3.2, centered(960, 735, 760, 84), pop(0, 0.4, 0.6))
    label(t, t.track("text", "Lema"), "aventuras para toda la familia", 1.85, 3.15, centered(960, 735, 740, 84), "Baloo 2",
          42, "#1B7F5C", weight=700, motion=pop(0, 0.4, 0.6), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0], 0.3, 0.3)})], name="Golpe")
    hit_music(t, "hopeful", 1.0)
    return t


def intro_liquido():
    """Bright gradient blobs flow and merge behind a blur; a drop lands, ripples, and holds the logo."""
    t = intro("yt-intro-liquido", "Intro de formas líquidas", "Liquid shapes intro", 13,
              ["líquido", "formas", "degradado", "creativo", "moderno"], thumb_at=3.0, background="#120A2A")
    bg(t, "#120A2A")
    rng = random.Random(6513)
    blobs = [("#7B2FF7", "#F72585"), ("#F72585", "#FF9E00"), ("#00BBF9", "#7B2FF7"), ("#FF9E00", "#F72585"),
             ("#4CC9F0", "#00F5D4")]
    for i, (a, b) in enumerate(blobs):
        x, y = rng.uniform(250, 1670), rng.uniform(150, 930)
        s = rng.uniform(520, 820)
        pts = [(0, {"sx": 1.0, "sy": 1.0}, "smooth")]
        for k in range(1, 4):
            pts.append((k * 1.25, {"sx": rng.uniform(0.8, 1.25), "sy": rng.uniform(0.8, 1.25),
                                   "dx": rng.uniform(-260, 260), "dy": rng.uniform(-160, 160)}, "smooth"))
        pts.append((5.0, {"dx": rng.uniform(-200, 200), "dy": rng.uniform(-120, 120)}))
        t.solid(t.track("shape", "Mancha"), a, 0, 5.0, centered(x, y, s * 1.4, s * 1.4), pts, kind="ellipse",
                layers=[radial(a, 0.95), no_stroke()])
    shade_full(t, 0.25, colour="#120A2A")
    t.solid(t.track("shape", "Gota"), "#FFFFFF", 0.6, 4.4, centered(960, 430, 380, 380),
            [(0, {"s": 0.0, "dy": -500}, "in"), (0.4, {"sx": 1.15, "sy": 0.8}, "smooth"), (0.6, {"sx": 0.95, "sy": 1.05},
                                                                                         "smooth"), (0.8, {})],
            kind="ellipse", layers=[shadow("#000000", 0, 20, 40, 0.35),
                                    gradient([(0, "#FF5DA2"), (1, "#FF9E00")], angle=135), no_stroke()])
    for k in range(3):
        at = 1.0 + k * 0.25
        t.solid(t.track("shape", "Onda"), "#FFFFFF", at, 1.2, centered(960, 430, 380, 380),
                [(0, {"s": 1.0}, "out"), (1.2, {"s": 2.6})], kind="ellipse", layers=[hollow(), sl("#FFFFFF", 4)],
                opacity=keys([(0, 0.8, "smooth"), (1.2, 0.0)]))
    logo(t, "logo-07", centered(960, 430, 260, 260), 1.05, pop(0, 0.45))
    label(t, t.track("text", "Canal"), "Mente Fluida", 1.4, 3.6, Box(160, 680, 1600, 160), "Outfit", 124, "#FFFFFF",
          weight=700, layers=[shadow("#3A0D5C", 0, 8, 26, 0.6), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=0.7, unit="character", stagger=0.03), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "creatividad · diseño · calma", 1.9, 3.1, Box(360, 850, 1200, 60), "Outfit", 38,
          "#FFD1E8", weight=500, spacing=6, anim_in=tanim("fade", duration=0.6), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0], 0.4, 0.35)})], name="Golpe")
    hit_music(t, "fake-it-til-you-fake-it", 1.0)
    return t


def intro_retro():
    """70s rainbow arcs rise from the bottom, a cream badge holds the logo, a chunky name with stacked shadows."""
    t = intro("yt-intro-retro", "Intro retro setentera", "70s retro intro", 14,
              ["retro", "70s", "vintage", "arcoíris", "buena onda"], thumb_at=3.0, background="#F6E7C8")
    bg(t, "#F6E7C8")
    arcs = [("#D1495B", 2000), ("#E76F2B", 1700), ("#F2A93B", 1400), ("#2A9D8F", 1100), ("#F6E7C8", 800)]
    for i, (c, d) in enumerate(arcs):
        t.solid(t.track("shape", "Arco"), c, 0.0, 5.0, centered(960, 1180, d, d),
                [(0, {"dy": 1100}, "out"), (0.8 + i * 0.07, {}, "linear"), (5.0, {"dy": -30})], kind="ellipse")
    t.solid(t.track("shape", "Insignia"), "#FFF3DC", 1.0, 4.0, centered(960, 300, 320, 320),
            [(0, {"s": 0.0}, "back"), (0.5, {})], kind="ellipse",
            layers=[offset_shadow("#8C4A2F", 8, 8), fill("#FFF3DC"), sl("#8C4A2F", 8, align="inside")],
            rotation=keys([(0, -90, "out"), (0.5, 0)]))
    logo(t, "logo-05", centered(960, 300, 240, 240), 1.05, pop(0, 0.5))
    label(t, t.track("text", "Canal"), "Buena Onda", 1.2, 3.8, Box(160, 480, 1600, 220), "Shrikhand", 160, "#FFF3DC",
          weight=400, layers=[offset_shadow("#8C4A2F", 14, 14), offset_shadow("#E76F2B", 7, 7, id="shadow2"),
                              fill("#FFF3DC")],
          anim_in=tanim("bounce", duration=0.55, unit="character", stagger=0.04), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "música, discos y buena vibra", 1.8, 3.2, centered(960, 770, 900, 80), "Righteous",
          42, "#FFF3DC", weight=400, box_bg=("#8C4A2F", 1.0), box_pad=16, box_radius=40,
          anim_in=tanim("pop", duration=0.4), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0], 0.4, 0.3)}),
              effect("stylize.film_grain", amount=0.22, grainSize=1.8)], name="Golpe")
    hit_music(t, "funkeriffic", 1.0)
    return t


INTROS = [intro_gaming, intro_vlog, intro_tech, intro_belleza, intro_comedia, intro_educacion, intro_musica,
          intro_minimal, intro_glitch, intro_3d, intro_a_mano, intro_neon, intro_papel, intro_liquido, intro_retro]

# ==== End screens (20 s, 16:9) ===================================================================

FT = ["pantalla final", "youtuber", "end screen", "suscríbete", "siguiente video"]


def final(id, es, en, n, tags, background, thumb_at=5.0):
    return wide(id, es, en, "outro", 20.0, order=O + 50 + n, tags=FT + tags, thumb_at=thumb_at, background=background)


def vid(t, sample: str, box: Box, n: int, t0: float, motion=None, **extra):
    """A «Video sugerido» zone: where the platform's video element goes (a screenshot can fill it)."""
    return t.photo(t.track("video", f"Video {n}"), sample, t0, t.duration - t0, box, motion,
                   label=f"Video sugerido {n}", **extra)


def avatar(t, sample: str, cx: float, cy: float, d: float, t0: float, ring: str | None = "#FFFFFF",
           ring_w: float = 8, motion=None):
    """The round zone where the subscribe element goes, with the channel photo in it."""
    return circle_photo(t, sample, t0, t.duration - t0, centered(cx, cy, d, d), motion or pop(0, 0.5),
                        ring_colour=ring, ring_width=ring_w, label="Foto del canal")


def frame(t, colour: str, box: Box, t0: float, border: float = 8, radius: float = 16, motion=None, layers=None,
          name: str = "Marco", **extra):
    b = Box(box.x - border, box.y - border, box.w + 2 * border, box.h + 2 * border)
    return t.solid(t.track("shape", name), colour, t0, t.duration - t0, b, motion, radius=radius + border,
                   kind="rounded-rectangle", layers=layers or [shadow("#000000", 0, 14, 30, 0.4), fill(colour),
                                                               no_stroke()], **extra)


def pulses(t, colour: str, cx: float, cy: float, d: float, t0: float, period: float = 2.5, grow: float = 1.45,
           width: float = 4):
    """A ring that leaves the avatar and fades, again and again (one track, clips in turn)."""
    tr = t.track("shape", "Pulso")
    at = t0
    while at + period <= t.duration + 1e-6:
        t.solid(tr, colour, at, period, centered(cx, cy, d, d), [(0, {}, "out"), (period, {"s": grow})], kind="ellipse",
                layers=[hollow(), sl(colour, width)], opacity=keys([(0, 0.8, "smooth"), (period, 0.0)]))
        at += period


def wave_keys(rng, period: float, n: int, lo: float, hi: float) -> list:
    """Smooth random values that come back to the first one at `period` (calm, loopable)."""
    first = rng.uniform(lo, hi)
    pts = [(0, first, "smooth")]
    for k in range(1, n):
        pts.append((period * k / n, rng.uniform(lo, hi), "smooth"))
    pts.append((period, first))
    return pts


def blobs(t, colours: list[str], seed: int, alpha: float = 0.95, size=(700, 1100), wander: float = 220):
    """Soft round lights drifting and changing shape; they are back in place at the end (loop)."""
    rng = random.Random(seed)
    d = t.duration
    for a in colours:
        x, y = rng.uniform(200, t.w - 200), rng.uniform(150, t.h - 150)
        s = rng.uniform(*size)
        pts = [(0, {}, "smooth")]
        for k in range(1, 4):
            pts.append((d * k / 4, {"dx": rng.uniform(-wander, wander), "dy": rng.uniform(-wander, wander) * 0.6,
                                    "sx": rng.uniform(0.85, 1.2), "sy": rng.uniform(0.85, 1.2)}, "smooth"))
        pts.append((d, {}))
        t.solid(t.track("shape", "Mancha"), a, 0, d, centered(x, y, s, s), pts, kind="ellipse",
                layers=[radial(a, alpha), no_stroke()])


def soft_light(t, colour: str, x: float, y: float, s: float, dx: float, dy: float, alpha: float = 0.5):
    t.solid(t.track("shape", "Luz"), colour, 0, t.duration, centered(x, y, s, s), loop(dx, dy), kind="ellipse",
            layers=[radial(colour, alpha), no_stroke()])


def fin_columnas():
    """Channel on the left (photo, «SUSCRÍBETE», thanks, handle), two videos stacked on the right; dashed rings turn."""
    t = final("yt-final-columnas", "Pantalla final en columnas", "Two-column end screen", 0,
              ["dos videos", "elegante", "oscura", "gracias por ver"], "#120D33")
    bg_gradient(t, [(0, "#2A1B66"), (1, "#0B0820")], angle=135)
    soft_light(t, "#FFB703", 300, 300, 1000, 120, 80, 0.22)
    soft_light(t, "#7B5CFF", 1500, 900, 1200, -140, -60, 0.35)
    outline_shape(t, t.track("shape", "Anillo"), "#FFB703", 3, 0, 20.0, centered(420, 470, 760, 760), at=0.2,
                  length=1.5, dash="dash", alpha=0.35, rotation=keys([(0, 0), (20.0, 360)]))
    outline_shape(t, t.track("shape", "Anillo"), "#FFFFFF", 3, 0, 20.0, centered(420, 470, 960, 960), at=0.4,
                  length=1.5, dash="dot", alpha=0.2, rotation=keys([(0, 0), (20.0, -360)]))
    avatar(t, "h-portrait-02", 420, 400, 300, 0.4, ring="#FFB703", ring_w=8)
    label(t, t.track("text", "Suscríbete"), "SUSCRÍBETE", 0.8, 19.2, Box(120, 590, 600, 70), "Montserrat", 46,
          "#FFFFFF", weight=800, spacing=8, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.03),
          name="Suscríbete")
    label(t, t.track("text", "Gracias"), "¡Gracias por ver!", 1.1, 18.9, Box(80, 670, 680, 120), "Pacifico", 66,
          "#FFFFFF", weight=400, anim_in=tanim("pop", duration=0.45), name="Gracias")
    label(t, t.track("text", "Canal"), "@tucanal", 1.4, 18.6, Box(120, 800, 600, 60), "Montserrat", 38, "#FFB703",
          weight=600, spacing=2, anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    label(t, t.track("text", "Título"), "SIGUE VIENDO", 0.3, 19.7, Box(1000, 70, 720, 60), "Montserrat", 38, "#FFB703",
          weight=900, spacing=10, align="left", anim_in=tanim("slide-right", duration=0.45), name="Título")
    for i, (s, y) in enumerate([("h-travel-02", 150), ("h-cooking-01", 600)]):
        box = Box(1000, y, 720, 405)
        m = [(0, {"dx": 260}, "out"), (0.6, {})]
        frame(t, "#FFFFFF", box, 0.5 + i * 0.2, 6, 14, m,
              layers=[shadow("#000000", 0, 16, 34, 0.5), fill("#FFFFFF"), no_stroke()])
        vid(t, s, box, i + 1, 0.5 + i * 0.2, m)
    t.song("i-guess-what-i-m-trying-to-say", 4.0, 0.55)
    return t


def fin_hud():
    """A gamer HUD: corner brackets on two videos, a scan line, a dashed ring turning round the channel photo."""
    t = final("yt-final-hud", "Pantalla final HUD gamer", "Gamer HUD end screen", 1,
              ["gaming", "gamer", "hud", "stream", "dos videos"], "#05070A")
    bg_gradient(t, [(0, "#0D1B2A"), (1, "#03050A")], angle=90)
    dots(t, ["#00F0FF", "#FF3864", "#FFFFFF"], 30, 0, 20.0, seed=6551, size=(3, 8), drift=90, alpha=0.6)
    scan = t.track("shape", "Escaneo")
    for k in range(5):
        t.solid(scan, "#00F0FF", k * 4.0, 4.0, Box(0, 0, 1920, 3), [(0, {}, "linear"), (4.0, {"dy": 1080})], alpha=0.25)
    label(t, t.track("text", "Título"), "SIGUIENTE MISIÓN", 0.2, 19.8, Box(160, 60, 1600, 100), "Russo One", 70,
          "#FFFFFF", weight=400, spacing=10, layers=[glow("#00F0FF", 22, 0.8), fill("#FFFFFF")],
          anim_in=tanim("glitch-in", duration=0.5), name="Título")
    for i, (s, x, c, cap) in enumerate([("h-gaming-01", 160, "#00F0FF", "ÚLTIMO VIDEO"),
                                        ("h-gaming-03", 1000, "#FF3864", "MEJOR PARTIDA")]):
        box = Box(x, 240, 760, 428)
        t0 = 0.5 + i * 0.25
        t.solid(t.track("shape", "Fondo video"), "#0B1622", t0, 20.0 - t0, box, pop(0, 0.4, 0.8),
                layers=[shadow(c, 0, 0, 40, 0.6), fill("#0B1622"), no_stroke()])
        vid(t, s, box, i + 1, t0, pop(0, 0.4, 0.8))
        for sx in (0, 1):
            for sy in (0, 1):
                cx = box.x - 18 + sx * (box.w + 36)
                cy = box.y - 18 + sy * (box.h + 36)
                for horiz in (True, False):
                    b = (Box(cx - (70 if sx else 0), cy - (6 if sy else 0), 70, 6) if horiz else
                         Box(cx - (6 if sx else 0), cy - (70 if sy else 0), 6, 70))
                    t.solid(t.track("shape", "Visor"), c, t0 + 0.2, 19.8 - t0, b,
                            [(0, {"dx": (1 if sx else -1) * 60, "dy": (1 if sy else -1) * 60}, "snap"), (0.35, {})],
                            layers=[glow(c, 14, 0.9), fill(c), no_stroke()])
        label(t, t.track("text", "Etiqueta"), cap, t0 + 0.3, 19.7 - t0, Box(x, 170, 760, 46), "Exo 2", 32, c,
              weight=700, spacing=6, align="left",
              anim_in=tanim("typewriter", duration=0.6, unit="character", stagger=0.03),
              name=f"Etiqueta del video {i + 1}")
    outline_shape(t, t.track("shape", "Anillo"), "#BFFBFF", 4, 0.9, 19.1, centered(960, 860, 250, 250), at=0.0,
                  length=0.8, dash="dash", glow_c="#00F0FF", rotation=keys([(0, 0), (19.1, 360)]))
    avatar(t, "h-man-04", 960, 860, 190, 0.8, ring="#FFFFFF", ring_w=6)
    label(t, t.track("text", "Suscríbete"), "SUSCRÍBETE", 1.1, 18.9, Box(1120, 805, 640, 70), "Russo One", 54, "#FFFFFF",
          weight=400, spacing=6, align="left", anim_in=tanim("slide-right", duration=0.4), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@zonagamer", 1.3, 18.7, Box(1120, 875, 640, 50), "Exo 2", 36, "#00F0FF",
          weight=700, spacing=2, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    label(t, t.track("text", "Gracias"), "GG · ¡GRACIAS POR JUGAR!", 1.2, 18.8, Box(160, 820, 640, 80), "Russo One", 40,
          "#FF3864", weight=400, spacing=3, align="right", anim_in=tanim("slide-left", duration=0.4), name="Gracias")
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.6, blurRadius=12)], name="Brillo")
    t.song("beat-one", 41.0, 0.5)
    return t


def fin_postal():
    """Vlog: the next video as a postcard on cream paper, the channel photo on a postage stamp, a dashed route."""
    t = final("yt-final-postal", "Pantalla final de postal", "Postcard end screen", 2,
              ["vlog", "viajes", "postal", "un video", "cálida"], "#F3EBDD")
    bg_gradient(t, [(0, "#F7F0E3"), (1, "#EADBC4")], angle=120)
    for i, (x, y, s, dx) in enumerate([(300, 110, 260, 140), (420, 1010, 320, 160), (1150, 70, 200, -90)]):
        t.solid(t.track("shape", "Nube"), "#FFFFFF", 0, 20.0, centered(x, y, s, s * 0.5), loop(dx, 0), kind="cloud",
                alpha=0.8)
    outline_shape(t, t.track("shape", "Ruta"), "#C0392B", 4, 0.0, 20.0, Box(1240, 70, 560, 170), "curved-arrow", at=0.8,
                  length=1.6, dash="dash", alpha=0.55)
    m = [(0, {"dy": 90}, "out"), (0.7, {})]
    fade = keys([(0, 0.0, "smooth"), (0.5, 1.0)])
    t.solid(t.track("shape", "Postal"), "#FFFDF8", 0.3, 19.7, Box(120, 150, 1000, 630), m, radius=6,
            kind="rounded-rectangle", layers=[shadow("#5A3A22", 0, 16, 36, 0.3), fill("#FFFDF8"), no_stroke()],
            opacity=fade)
    vid(t, "h-beach-04", Box(140, 170, 960, 540), 1, 0.3, m, opacity=fade)
    label(t, t.track("text", "Pie"), "el próximo destino →", 0.9, 19.1, Box(150, 714, 940, 60), "Caveat", 54, "#3A2E2A",
          weight=700, align="right", anim_in=tanim("typewriter", duration=0.8, unit="character", stagger=0.03),
          name="Pie de la postal")
    stamp = t.solid(t.track("shape", "Sello"), "#FFFFFF", 0.6, 19.4, centered(1500, 390, 340, 340),
                    [(0, {"s": 0.0}, "back"), (0.5, {})], kind="star",
                    layers=[shadow("#5A3A22", 0, 10, 24, 0.3), fill("#FFFFFF"), no_stroke()],
                    rotation=keys([(0, 6, "smooth"), (9.7, 2, "smooth"), (19.4, 6)]))
    stamp["shapeStyle"].update(points=30, innerRatio=0.93)
    avatar(t, "h-portrait-04", 1500, 390, 250, 0.7, ring="#C0392B", ring_w=4)
    style = text_style("Special Elite", 48, [fill("#C0392B")], weight=400, spacing=4, box=("#C0392B", 0.0), box_pad=14,
                       anim_in=tanim("stamp", duration=0.4))
    style.update(boxBorderWidth=4, boxBorderColor=_a("#C0392B"))
    t.text(t.track("text", "Suscríbete"), "SUSCRÍBETE", 1.2, 18.8, centered(1500, 640, 440, 80), style,
           label="Suscríbete", rotation=keys([(0, -6)]))
    label(t, t.track("text", "Gracias"), "¡Gracias por acompañarme!", 1.5, 18.5, Box(1220, 720, 580, 170), "Caveat", 74,
          "#3A2E2A", weight=700, anim_in=tanim("fade", duration=0.6), name="Gracias")
    label(t, t.track("text", "Canal"), "@valeriaenruta", 1.8, 18.2, Box(1220, 900, 580, 50), "Montserrat", 34, "#C0392B",
          weight=700, spacing=2, anim_in=tanim("fade", duration=0.6), name="Usuario del canal")
    grain(t, 0.1)
    t.song("happy-whistling-ukulele", 2.0, 0.55)
    return t


def fin_tech():
    """A circuit grid slides slowly, two videos in device bezels, a pulse leaves the channel photo."""
    t = final("yt-final-tech", "Pantalla final tecnológica", "Tech end screen", 3,
              ["tecnología", "reseñas", "gadgets", "dos videos", "oscura"], "#04101C")
    bg_gradient(t, [(0, "#071C33"), (1, "#020810")], angle=90)
    for k in range(18):
        t.solid(t.track("shape", "Rejilla"), "#1C3A5E", 0, 20.0, Box(k * 120, 0, 2, 1080),
                [(0, {}, "linear"), (20.0, {"dx": -120})], alpha=0.4)
    for k in range(1, 9):
        t.solid(t.track("shape", "Rejilla"), "#1C3A5E", 0, 20.0, Box(0, k * 120, 1920, 2), alpha=0.4)
    label(t, t.track("text", "Título"), "PRÓXIMA RESEÑA", 0.2, 19.8, Box(140, 70, 1200, 80), "Sora", 54, "#FFFFFF",
          weight=600, spacing=12, align="left", anim_in=tanim("rise", duration=0.4, unit="character", stagger=0.03),
          name="Título")
    line(t, t.track("shape", "Línea"), "#39D0FF", 0.5, 19.5, Box(140, 158, 220, 5), length=0.6)
    for i, (s, x, cap) in enumerate([("h-tech-02", 140, "Lo nuevo"), ("h-desk-02", 980, "Comparativa")]):
        box = Box(x, 210, 800, 450)
        t0 = 0.5 + i * 0.2
        m = [(0, {"dy": 60}, "out"), (0.6, {})]
        frame(t, "#0E2238", box, t0, 16, 14, m,
              layers=[shadow("#39D0FF", 0, 0, 40, 0.35), fill("#0E2238"), sl("#39D0FF", 3, 0.6, align="inside")])
        vid(t, s, box, i + 1, t0, m)
        label(t, t.track("text", "Etiqueta"), cap, t0 + 0.4, 19.6 - t0, Box(x, 690, 800, 50), "Sora", 32, "#39D0FF",
              weight=600, spacing=4, align="left", anim_in=tanim("fade", duration=0.5), name=f"Etiqueta del video {i + 1}")
    pulses(t, "#39D0FF", 960, 880, 180, 1.0)
    avatar(t, "h-man-01", 960, 880, 180, 0.8, ring="#39D0FF", ring_w=5)
    label(t, t.track("text", "Suscríbete"), "SUSCRÍBETE", 1.1, 18.9, Box(1090, 835, 600, 56), "Sora", 42, "#FFFFFF",
          weight=700, spacing=6, align="left", anim_in=tanim("slide-right", duration=0.4), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@tecnoclaro", 1.3, 18.7, Box(1090, 892, 600, 46), "Sora", 32, "#39D0FF",
          weight=500, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    label(t, t.track("text", "Gracias"), "Gracias por ver", 1.2, 18.8, Box(180, 845, 600, 70), "Sora", 46, "#FFFFFF",
          weight=300, spacing=3, align="right", anim_in=tanim("slide-left", duration=0.4), name="Gracias")
    t.adjust([effect("bloom_glow", threshold=0.65, intensity=0.5, blurRadius=10)], name="Brillo")
    t.song("arpent", 40.0, 0.5)
    return t


def fin_belleza():
    """Blush and gold: a script thank-you, two videos with offset gold lines, sparkles that twinkle in turn."""
    t = final("yt-final-belleza", "Pantalla final rosa y dorado", "Blush and gold end screen", 4,
              ["belleza", "maquillaje", "elegante", "rosa", "dos videos"], "#F6E3E0")
    bg_gradient(t, [(0, "#FBEFEA"), (1, "#EFCFCB")], angle=135)
    soft_light(t, "#F4B6B9", 1600, 200, 1100, -180, 60, 0.6)
    soft_light(t, "#FFFFFF", 260, 900, 1000, 160, -60, 0.7)
    rng = random.Random(6554)
    for k in range(10):
        tr = t.track("shape", "Brillo")
        at = rng.uniform(0, 3)
        while at + 1.4 <= 20.0:
            x, y = rng.choice([(rng.uniform(60, 130), rng.uniform(100, 1000)), (rng.uniform(1790, 1870), rng.uniform(100, 1000)),
                               (rng.uniform(200, 1700), rng.uniform(1010, 1050))])
            s = rng.uniform(20, 40)
            t.solid(tr, "#E8C88A", at, 1.4, centered(x, y, s, s), [(0, {"s": 0.0}, "back"), (0.5, {}, "smooth"),
                                                                  (1.4, {"s": 0.0})],
                    kind="star", layers=[glow("#FFFFFF", 10, 0.8), fill("#E8C88A"), no_stroke()],
                    rotation=keys([(0, 0), (1.4, 90)]))
            at += rng.uniform(2.5, 4.5)
    label(t, t.track("text", "Gracias"), "gracias por estar aquí", 0.2, 19.8, Box(160, 50, 1600, 180), "Great Vibes", 120,
          "#8A3B4E", weight=400, anim_in=tanim("blur-in", duration=0.8, unit="character", stagger=0.025), name="Gracias")
    for i, (s, x, cap) in enumerate([("y7-h-beauty-01", 160, "TUTORIAL COMPLETO"), ("y7-h-beauty-05", 1000, "RUTINA DE NOCHE")]):
        box = Box(x, 270, 760, 428)
        t0 = 0.5 + i * 0.2
        outline_shape(t, t.track("shape", "Línea dorada"), "#C9A15B", 3, t0, 20.0 - t0,
                      Box(box.x + 22, box.y + 22, box.w, box.h), "rectangle", at=0.3, length=0.9)
        vid(t, s, box, i + 1, t0, [(0, {"dy": 40}, "out"), (0.7, {})], opacity=keys([(0, 0.0, "smooth"), (0.5, 1.0)]))
        label(t, t.track("text", "Etiqueta"), cap, t0 + 0.5, 19.5 - t0, Box(x, 735, 760, 44), "Montserrat", 26, "#B76E79",
              weight=600, spacing=8, align="left", anim_in=tanim("fade", duration=0.6), name=f"Etiqueta del video {i + 1}")
    avatar(t, "makeup-02", 960, 880, 170, 0.9, ring="#C9A15B", ring_w=5)
    label(t, t.track("text", "Suscríbete"), "SUSCRÍBETE", 1.2, 18.8, Box(1080, 832, 600, 50), "Montserrat", 34, "#8A3B4E",
          weight=600, spacing=12, align="left", anim_in=tanim("fade", duration=0.6), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@bellezaconlu", 1.4, 18.6, Box(1080, 880, 600, 56), "Playfair Display", 38,
          "#6B2E3E", weight=500, italic=True, align="left", anim_in=tanim("fade", duration=0.6), name="Usuario del canal")
    label(t, t.track("text", "Frecuencia"), "nuevo video cada martes", 1.3, 18.7, Box(240, 852, 600, 56), "Montserrat",
          32, "#8A3B4E", weight=500, spacing=2, align="right", anim_in=tanim("fade", duration=0.6), name="Frecuencia")
    t.song("landra-s-dream", 4.0, 0.5)
    return t


def fin_comic():
    """Comic panels on sliding stripes: tilted video panels with caption boxes, the channel photo on a burst."""
    t = final("yt-final-comic", "Pantalla final de cómic", "Comic end screen", 5,
              ["comedia", "cómic", "divertido", "humor", "dos videos"], "#FFE45C")
    bg(t, "#FFE45C")
    for k in range(16):
        t.solid(t.track("shape", "Franja"), "#FFF0A0", 0, 20.0, centered(-700 + k * 220, 540, 90, 2600),
                [(0, {}, "linear"), (20.0, {"dx": 220})], rotation=keys([(0, 30)]))
    label(t, t.track("text", "Título"), "¿TODAVÍA AQUÍ?", 0.2, 19.8, Box(160, 30, 1600, 160), "Bangers", 130, "#FFFFFF",
          weight=400, spacing=4, layers=[offset_shadow("#111111", 10, 10), stroke(8, "#111111"), fill("#FFFFFF")],
          anim_in=tanim("bounce", duration=0.5, unit="character", stagger=0.04), name="Título")
    for i, (s, x, y, r, cap, cbox, cr) in enumerate([
            ("y7-h-laugh-05", 160, 240, -2, "¡NO TE LO PIERDAS!", Box(130, 205, 440, 66), -4),
            ("y7-h-laugh-01", 1000, 270, 2, "¡EL MEJOR!", Box(1420, 235, 340, 66), 4)]):
        box = Box(x, y, 760, 428)
        t0 = 0.5 + i * 0.25
        rot = keys([(0, r)])
        m = pop(0, 0.45, 0.6)
        frame(t, "#FFFFFF", box, t0, 12, 0, m, layers=[offset_shadow("#111111", 16, 16), fill("#FFFFFF"),
                                                       sl("#111111", 6, align="inside")], rotation=rot)
        vid(t, s, box, i + 1, t0, m, rotation=rot)
        style = text_style("Bangers", 44, [fill("#111111")], weight=400, spacing=2, box=("#FFFFFF", 1.0), box_pad=12,
                           anim_in=tanim("pop", duration=0.35))
        style.update(boxBorderWidth=5, boxBorderColor=_a("#111111"))
        t.text(t.track("text", "Cartela"), cap, t0 + 0.4, 19.6 - t0, cbox, style, label=f"Cartela del video {i + 1}",
               rotation=keys([(0, cr)]))
    burst = t.solid(t.track("shape", "Estallido"), "#FF3B3B", 0.8, 19.2, centered(960, 860, 340, 340),
                    [(0, {"s": 0.0}, "back"), (0.5, {})], kind="star",
                    layers=[offset_shadow("#111111", 8, 8), fill("#FF3B3B"), sl("#111111", 5, align="inside")],
                    rotation=keys([(0, 0, "smooth"), (9.6, 12, "smooth"), (19.2, 0)]))
    burst["shapeStyle"].update(points=14, innerRatio=0.74)
    avatar(t, "h-portrait-05", 960, 860, 190, 1.0, ring="#111111", ring_w=6)
    label(t, t.track("text", "Suscríbete"), "¡SUSCRÍBETE!", 1.3, 18.7, Box(1150, 790, 640, 90), "Bangers", 76, "#111111",
          weight=400, spacing=3, align="left", anim_in=tanim("bounce", duration=0.5), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@risassinfiltro", 1.5, 18.5, Box(1150, 880, 640, 56), "Baloo 2", 38, "#111111",
          weight=800, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    t.solid(t.track("shape", "Bocadillo"), "#FFFFFF", 1.2, 18.8, Box(230, 770, 580, 170), pop(0, 0.4), kind="speech-bubble",
            layers=[offset_shadow("#111111", 8, 8), fill("#FFFFFF"), sl("#111111", 6, align="inside")])
    label(t, t.track("text", "Gracias"), "¡Gracias por ver!", 1.3, 18.7, Box(240, 780, 560, 120), "Bangers", 60,
          "#111111", weight=400, spacing=2, motion=pop(0, 0.4), name="Gracias")
    t.song("frogs-legs-rag", 40.0, 0.5)
    return t


def fin_pizarra():
    """A chalkboard in a wood frame: chalk lines draw round the two videos and the channel photo."""
    t = final("yt-final-pizarra", "Pantalla final de pizarra", "Chalkboard end screen", 6,
              ["educación", "clases", "pizarra", "tiza", "dos videos"], "#1F3B2D")
    bg_gradient(t, [(0, "#2C4D3B"), (1, "#18301F")], angle=135)
    for x, y, s in [(400, 300, 800), (1500, 800, 900), (1100, 200, 600)]:
        t.solid(t.track("shape", "Polvo"), "#FFFFFF", 0, 20.0, centered(x, y, s, s * 0.6), loop(40, 20), kind="ellipse",
                layers=[radial("#FFFFFF", 0.07), no_stroke()])
    for b in [Box(0, 0, 1920, 26), Box(0, 1054, 1920, 26), Box(0, 0, 26, 1080), Box(1894, 0, 26, 1080)]:
        t.solid(t.track("shape", "Marco"), "#8B5A2B", 0, 20.0, b, layers=[gradient([(0, "#A0703F"), (1, "#6E4420")]),
                                                                       no_stroke()])
    label(t, t.track("text", "Título"), "Tarea para hoy:", 0.2, 19.8, Box(160, 55, 1600, 110), "Kalam", 80, "#F4F4EC",
          weight=700, anim_in=tanim("typewriter", duration=0.9, unit="character", stagger=0.04), name="Título")
    for i, (s, x, cap) in enumerate([("y7-h-study-03", 170, "Siguiente lección"), ("y7-h-study-05", 1010, "Repaso rápido")]):
        box = Box(x, 250, 740, 416)
        t0 = 0.6 + i * 0.3
        vid(t, s, box, i + 1, t0, opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0)]))
        outline_shape(t, t.track("shape", "Tiza"), "#F4F4EC", 5, t0, 20.0 - t0,
                      Box(box.x - 16, box.y - 16, box.w + 32, box.h + 32), "rectangle", at=0.0, length=0.8,
                      sketch=(26, 4, 11 + i))
        label(t, t.track("text", "Etiqueta"), cap, t0 + 0.4, 19.6 - t0, Box(x - 10, 172, 740, 60), "Kalam", 42, "#FFE680",
              weight=700, align="left", anim_in=tanim("typewriter", duration=0.6, unit="character", stagger=0.03),
              name=f"Etiqueta del video {i + 1}")
    avatar(t, "h-portrait-01", 960, 860, 180, 1.0, ring=None)
    outline_shape(t, t.track("shape", "Tiza"), "#F4F4EC", 5, 1.0, 19.0, centered(960, 860, 220, 215), at=0.2, length=0.7,
                  sketch=(20, 4, 21))
    label(t, t.track("text", "Suscríbete"), "¡Suscríbete y aprende más!", 1.4, 18.6, Box(1090, 805, 760, 64), "Kalam",
          46, "#F4F4EC", weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@aprendefacil", 1.6, 18.4, Box(1090, 872, 760, 50), "Kalam", 36, "#FFE680",
          weight=400, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    label(t, t.track("text", "Gracias"), "Gracias por estudiar conmigo", 1.5, 18.5, Box(120, 825, 700, 64), "Kalam", 42,
          "#F4F4EC", weight=400, align="right", anim_in=tanim("fade", duration=0.5), name="Gracias")
    for txt, b, r in [("E = mc²", Box(1500, 70, 340, 80), -6), ("a² + b² = c²", Box(70, 960, 420, 70), 4)]:
        label(t, t.track("text", "Apunte"), txt, 2.0, 18.0, b, "Kalam", 44, "#F4F4EC", weight=400, editable=False,
              rotation=keys([(0, r)]), opacity=keys([(0, 0.0, "smooth"), (0.8, 0.35)]))
    grain(t, 0.16)
    t.song("from-page-to-practice", 4.0, 0.5)
    return t


def fin_vinilo():
    """Music: one big video, a slowly turning record with the channel photo as its label, a calm equaliser."""
    t = final("yt-final-vinilo", "Pantalla final musical", "Music end screen", 7,
              ["música", "vinilo", "artista", "un video", "ecualizador"], "#111013")
    bg_gradient(t, [(0, "#1E1418"), (1, "#0B0B0D")], angle=0)
    soft_light(t, "#E63946", 1500, 420, 1200, -60, 40, 0.28)
    label(t, t.track("text", "Título"), "SIGUIENTE CANCIÓN", 0.2, 19.8, Box(110, 70, 1000, 90), "Bebas Neue", 84,
          "#F1FAEE", weight=400, spacing=6, align="left", anim_in=tanim("slide-right", duration=0.45, unit="character",
                                                                             stagger=0.03), name="Título")
    box = Box(110, 170, 1000, 563)
    frame(t, "#E63946", box, 0.4, 5, 10, [(0, {"dx": -120}, "out"), (0.6, {})],
          layers=[shadow("#E63946", 0, 0, 40, 0.45), fill("#E63946"), no_stroke()])
    vid(t, "y7-h-guitar-05", box, 1, 0.4, [(0, {"dx": -120}, "out"), (0.6, {})])
    label(t, t.track("text", "Pie"), "Escucha la sesión completa", 0.9, 19.1, Box(110, 760, 1000, 56), "Montserrat", 36,
          "#E63946", weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Pie del video")
    rec = centered(1500, 420, 560, 560)
    enter = [(0, {"dx": 700}, "out"), (0.8, {})]
    t.solid(t.track("shape", "Disco"), "#0A0A0A", 0.3, 19.7, rec, enter, kind="ellipse",
            layers=[shadow("#000000", 0, 20, 40, 0.6), fill("#0A0A0A"), no_stroke()])
    for r in (520, 460, 400, 340):
        t.solid(t.track("shape", "Surco"), "#26262C", 0.3, 19.7, centered(1500, 420, r, r), enter, kind="ellipse",
                layers=[hollow(), sl("#26262C", 3)])
    for ang in (0, 90):
        t.solid(t.track("shape", "Reflejo"), "#FFFFFF", 0.3, 19.7, centered(1500, 420, 540, 54), enter, kind="ellipse",
                layers=[gradient([(0, "#FFFFFF", 0.0), (0.5, "#FFFFFF", 0.12), (1, "#FFFFFF", 0.0)], angle=0), no_stroke()],
                rotation=keys([(0, ang + 30), (19.7, ang + 30 - 720)]))
    avatar(t, "y7-h-guitar-02", 1500, 420, 230, 1.0, ring="#E63946", ring_w=10)
    label(t, t.track("text", "Suscríbete"), "SUSCRÍBETE", 1.2, 18.8, Box(1240, 730, 520, 90), "Bebas Neue", 84,
          "#F1FAEE", weight=400, spacing=8, anim_in=tanim("rise", duration=0.4, unit="character", stagger=0.03),
          name="Suscríbete")
    label(t, t.track("text", "Canal"), "@sonidonorte", 1.4, 18.6, Box(1240, 820, 520, 50), "Montserrat", 34, "#E63946",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    rng = random.Random(6557)
    for i in range(40):
        pts = wave_keys(rng, 20.0, 8, 0.15, 1.0)
        t.solid(t.track("shape", "Ecualizador"), "#F1FAEE" if i % 5 else "#E63946", 0, 20.0, Box(30 + i * 47, 920, 26, 130),
                [(p[0], {"sy": p[1], "dy": 65 * (1 - p[1])}) + tuple(p[2:]) for p in pts], radius=5,
                kind="rounded-rectangle", alpha=0.45)
    t.song("groovin", 30.0, 0.5)
    return t


def fin_minimal():
    """White, one large video, the channel column to its right; a soft grey light drifts behind."""
    t = final("yt-final-minimal-uno", "Pantalla final minimal: 1 video", "Minimal end screen: 1 video", 8,
              ["minimal", "limpia", "blanco", "un video", "elegante"], "#FFFFFF")
    bg(t, "#FFFFFF")
    soft_light(t, "#E2DED5", 1500, 300, 1300, -300, 200, 1.0)
    label(t, t.track("text", "Título"), "a continuación", 0.2, 19.8, Box(120, 85, 900, 70), "Inter", 42, "#111111",
          weight=300, spacing=8, align="left", anim_in=tanim("fade", duration=0.7), name="Título")
    vid(t, "h-nature-04", Box(120, 180, 1100, 619), 1, 0.4, opacity=keys([(0, 0.0, "smooth"), (0.8, 1.0)]))
    line(t, t.track("shape", "Línea"), "#111111", 0.8, 19.2, Box(120, 830, 1100, 2), length=1.0)
    avatar(t, "h-portrait-06", 1560, 370, 240, 0.8, ring=None)
    label(t, t.track("text", "Suscríbete"), "Suscríbete", 1.1, 18.9, Box(1320, 530, 480, 70), "Inter", 50, "#111111",
          weight=600, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.03), name="Suscríbete")
    t.solid(t.track("shape", "Acento"), "#E63946", 1.4, 18.6, centered(1560, 615, 80, 4),
            [(0, {"sx": 0.0}, "out"), (0.6, {}, "smooth"), (5.0, {"sx": 1.6}, "smooth"), (10.0, {}, "smooth"),
             (15.0, {"sx": 1.6}, "smooth"), (18.6, {})])
    label(t, t.track("text", "Gracias"), "Gracias por ver hasta el final.", 1.5, 18.5, Box(1320, 645, 480, 110), "Inter",
          34, "#555555", weight=300, anim_in=tanim("fade", duration=0.7), name="Gracias")
    label(t, t.track("text", "Canal"), "@estudionorte", 1.8, 18.2, Box(1320, 775, 480, 50), "Inter", 30, "#E63946",
          weight=500, spacing=2, anim_in=tanim("fade", duration=0.7), name="Usuario del canal")
    t.song("infinite-peace", 0.0, 0.5)
    return t


def fin_neon():
    """Neon tubes round two videos breathe and flicker now and then; stars blink in the corners."""
    t = final("yt-final-neon", "Pantalla final de neón", "Neon end screen", 9,
              ["neón", "noche", "stream", "música", "dos videos"], "#0B0710")
    bg_gradient(t, [(0, "#1A0F22"), (1, "#07050A")], angle=90)
    soft_light(t, "#FF2EF7", 500, 500, 1200, 80, 40, 0.16)
    soft_light(t, "#00F0FF", 1450, 500, 1200, -80, -40, 0.12)
    label(t, t.track("text", "Título"), "SIGUE LA NOCHE", 0.2, 19.8, Box(160, 55, 1600, 150), "Monoton", 84, "#FFE6FB",
          weight=400, layers=[glow("#FF2EF7", 28, 1.0), glow("#FF2EF7", 8, 1.0, id="glow2"), fill("#FFE6FB")],
          anim_in=tanim("flicker-in", duration=0.8), anim_loop=tanim("flicker", intensity=0.06, speed=4),
          name="Título")
    for i, (s, x, c, core) in enumerate([("h-concert-02", 170, "#FF2EF7", "#FFD6FB"), ("h-gaming-01", 1010, "#00F0FF",
                                                                                          "#C8FCFF")]):
        box = Box(x, 260, 740, 416)
        t0 = 0.6 + i * 0.3
        vid(t, s, box, i + 1, t0, opacity=keys([(0, 0.0, "smooth"), (0.5, 1.0)]))
        breathe = [(0, 0.0, "hold"), (0.1, 1.0, "hold"), (0.16, 0.2, "hold"), (0.26, 1.0, "smooth")]
        at = 0.26
        while at + 4.0 <= 20.0 - t0:
            breathe += [(at + 2.0, 0.75, "smooth"), (at + 4.0, 1.0, "smooth")]
            at += 4.0
        t.solid(t.track("shape", "Tubo"), c, t0, 20.0 - t0, Box(box.x - 18, box.y - 18, box.w + 36, box.h + 36),
                radius=28, kind="rounded-rectangle", layers=tube(c, core, 7), opacity=keys(breathe))
    rng = random.Random(6559)
    for (x, y) in [(90, 120), (1830, 120), (90, 960), (1830, 960)]:
        tr = t.track("shape", "Estrella")
        at = rng.uniform(1.0, 2.0)
        t.solid(tr, "#FFE66D", at, 20.0 - at, centered(x, y, 80, 80), kind="star", layers=tube("#FFE66D", "#FFF6C2", 4),
                opacity=keys([(0, 1.0, "hold"), (rng.uniform(3, 6), 0.3, "hold"), (rng.uniform(6.1, 6.4), 1.0, "hold"),
                              (rng.uniform(11, 13), 0.3, "hold"), (13.2, 1.0)]))
    outline_shape(t, t.track("shape", "Aro"), "#C8FCFF", 6, 1.0, 19.0, centered(960, 870, 210, 210), at=0.0, length=0.6,
                  glow_c="#00F0FF")
    avatar(t, "h-portrait-03", 960, 870, 180, 1.0, ring=None)
    label(t, t.track("text", "Suscríbete"), "SUSCRÍBETE", 1.3, 18.7, Box(1100, 815, 640, 70), "Righteous", 54, "#C8FCFF",
          weight=400, spacing=6, align="left", layers=[glow("#00F0FF", 20, 0.9), fill("#C8FCFF")],
          anim_in=tanim("flicker-in", duration=0.5), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@nocheneon", 1.5, 18.5, Box(1100, 888, 640, 50), "Righteous", 36, "#FFD6FB",
          weight=400, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    label(t, t.track("text", "Gracias"), "¡gracias por la compañía!", 1.4, 18.6, Box(160, 835, 660, 70), "Righteous", 42,
          "#FFD6FB", weight=400, align="right", layers=[glow("#FF2EF7", 18, 0.8), fill("#FFD6FB")],
          anim_in=tanim("flicker-in", duration=0.5), name="Gracias")
    t.adjust([effect("bloom_glow", threshold=0.55, intensity=0.8, blurRadius=14)], name="Brillo")
    vignette(t, 0.5)
    t.song("blippy-trance", 20.0, 0.45)
    return t


def fin_setentas():
    """70s: a slow sunburst, rainbow arcs in the corners, two videos in chunky rounded frames."""
    t = final("yt-final-setentas", "Pantalla final setentera", "70s end screen", 10,
              ["retro", "70s", "vintage", "buena onda", "dos videos"], "#F6E7C8")
    bg(t, "#F6E7C8")
    sun = t.solid(t.track("shape", "Rayos"), "#F2D49B", 0, 20.0, centered(960, 620, 2800, 2800), kind="star",
                  layers=[fill("#F2D49B", 0.7), no_stroke()],
                  rotation=keys([(0, 0, "smooth"), (10.0, 18, "smooth"), (20.0, 0)]))
    sun["shapeStyle"].update(points=20, innerRatio=0.12)
    for cx in (0, 1920):
        for i, (c, d) in enumerate([("#D1495B", 1000), ("#E76F2B", 840), ("#F2A93B", 680), ("#2A9D8F", 520),
                                    ("#F6E7C8", 360)]):
            t.solid(t.track("shape", "Arco"), c, 0, 20.0, centered(cx, 1080, d, d),
                    [(0, {"s": 0.0}, "out"), (0.6 + i * 0.08, {}, "smooth"), (10.0, {"s": 1.04}, "smooth"), (20.0, {})],
                    kind="ellipse")
    label(t, t.track("text", "Gracias"), "¡Gracias por la buena onda!", 0.2, 19.8, Box(160, 35, 1600, 130), "Shrikhand",
          84, "#D1495B", weight=400, layers=[offset_shadow("#8C4A2F", 6, 6), fill("#D1495B")],
          anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.1), name="Gracias")
    for i, (s, x, c) in enumerate([("h-concert-04", 160, "#E76F2B"), ("h-travel-02", 1000, "#2A9D8F")]):
        box = Box(x, 195, 760, 428)
        t0 = 0.5 + i * 0.25
        m = pop(0, 0.5, 0.7)
        frame(t, c, box, t0, 16, 26, m, layers=[offset_shadow("#8C4A2F", 12, 12), fill(c), no_stroke()])
        vid(t, s, box, i + 1, t0, m)
    t.solid(t.track("shape", "Insignia"), "#FFF3DC", 0.9, 19.1, centered(760, 830, 250, 250), pop(0, 0.5),
            kind="ellipse", layers=[offset_shadow("#8C4A2F", 8, 8), fill("#FFF3DC"), sl("#8C4A2F", 6, align="inside")])
    avatar(t, "h-portrait-01", 760, 830, 200, 1.0, ring=None)
    label(t, t.track("text", "Suscríbete"), "¡Suscríbete!", 1.3, 18.7, Box(910, 760, 700, 100), "Shrikhand", 70,
          "#D1495B", weight=400, align="left", layers=[offset_shadow("#FFF3DC", 4, 4), fill("#D1495B")],
          anim_in=tanim("pop", duration=0.4), name="Suscríbete")
    label(t, t.track("text", "Canal"), "@buenaonda", 1.5, 18.5, Box(915, 862, 700, 56), "Righteous", 40, "#8C4A2F",
          weight=400, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    grain(t, 0.18)
    t.song("funkeriffic", 26.0, 0.5)
    return t


def fin_liquido():
    """Liquid gradient lights flowing, glass cards holding two videos, a glass pill with the channel."""
    t = final("yt-final-liquido", "Pantalla final de cristal líquido", "Liquid glass end screen", 11,
              ["líquido", "cristal", "degradado", "moderno", "dos videos"], "#120A2A")
    bg(t, "#120A2A")
    blobs(t, ["#7B2FF7", "#F72585", "#00BBF9", "#FF9E00", "#4CC9F0", "#B5179E"], seed=6561, size=(900, 1300),
          wander=260)
    shade_full(t, 0.25, colour="#120A2A")
    label(t, t.track("text", "Título"), "¿Seguimos?", 0.2, 19.8, Box(160, 55, 1600, 150), "Outfit", 100, "#FFFFFF",
          weight=300, spacing=4, anim_in=tanim("blur-in", duration=0.8, unit="character", stagger=0.04), name="Título")
    glass = [fill("#FFFFFF", 0.14), sl("#FFFFFF", 2, 0.45, align="inside")]
    for i, (s, x) in enumerate([("h-nature-02", 170), ("h-city-04", 1010)]):
        box = Box(x, 260, 740, 416)
        t0 = 0.5 + i * 0.25
        m = [(0, {"dy": 70}, "out"), (0.7, {})]
        frame(t, "#FFFFFF", box, t0, 22, 12, m, layers=[shadow("#000000", 0, 20, 40, 0.3)] + glass,
              opacity=keys([(0, 0.0, "smooth"), (0.5, 1.0)]))
        vid(t, s, box, i + 1, t0, m, opacity=keys([(0, 0.0, "smooth"), (0.5, 1.0)]))
    pill(t, t.track("shape", "Cristal"), "#FFFFFF", 0.9, 19.1, Box(520, 795, 880, 170), pop(0, 0.5, 0.8),
         layers=glass)
    avatar(t, "h-portrait-04", 610, 880, 130, 1.0, ring="#FFFFFF", ring_w=4)
    label(t, t.track("text", "Suscríbete"), "Suscríbete", 1.2, 18.8, Box(705, 815, 660, 66), "Outfit", 52, "#FFFFFF",
          weight=600, align="left", anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.03),
          name="Suscríbete")
    label(t, t.track("text", "Canal"), "@mentefluida", 1.4, 18.6, Box(705, 882, 660, 50), "Outfit", 36, "#FFD1E8",
          weight=500, align="left", anim_in=tanim("fade", duration=0.5), name="Usuario del canal")
    t.song("infinite-wonder", 10.0, 0.5)
    return t


# ==== Shorts endings (10 s, 9:16) ================================================================

def short(id, es, en, n, tags, background, thumb_at=4.0):
    return tall(id, es, en, "outro", 10.0, order=O + 50 + n,
                tags=["sígueme", "youtuber", "shorts", "vertical", "cierre"] + tags,
                thumb_at=thumb_at, background=background)


def follow_button(t, cx: float, cy: float, w: float, h: float, at: float, press: float, colours, texts, font="Poppins"):
    """A «Seguir» pill that is pressed and turns into «Siguiendo»."""
    (c1, tc1), (c2, tc2) = colours
    t.solid(t.track("shape", "Botón"), c1, at, press - at, centered(cx, cy, w, h),
            [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (press - at - 0.15, {}, "smooth"),
             (press - at, {"s": 0.9})], radius=h / 2, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 10, 24, 0.3), fill(c1), no_stroke()])
    label(t, t.track("text", "Botón"), texts[0], at, press - at, centered(cx, cy, w, h), font, int(h * 0.42), tc1,
          weight=800, motion=[(0, {"s": 0.0}, "back"), (0.45, {})], name="Botón")
    t.solid(t.track("shape", "Botón"), c2, press, t.duration - press, centered(cx, cy, w, h),
            [(0, {"s": 0.9}, "back"), (0.3, {})], radius=h / 2, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 10, 24, 0.3), fill(c2), sl(tc2, 4, 0.6, align="inside")])
    label(t, t.track("text", "Botón"), texts[1], press, t.duration - press, centered(cx, cy, w, h), font, int(h * 0.38),
          tc2, weight=800, anim_in=tanim("pop", duration=0.3), name="Botón pulsado")
    t.solid(t.track("shape", "Toque"), "#FFFFFF", press - 0.1, 0.6, centered(cx + w * 0.25, cy + h * 0.1, 60, 60),
            [(0, {"s": 0.3}, "out"), (0.6, {"s": 2.4})], kind="ellipse",
            opacity=keys([(0, 0.8, "smooth"), (0.6, 0.0)]))


def hearts(t, colours, t0: float, seed: int, n: int = 18, area: Box | None = None):
    rng = random.Random(seed)
    area = area or Box(80, 1350, 920, 500)
    for k in range(n):
        tr = t.track("shape", "Corazón")
        at = t0 + rng.uniform(0, t.duration - t0 - 2.6)
        d = rng.uniform(2.0, 2.6)
        s = rng.uniform(40, 90)
        x = rng.uniform(area.x, area.x + area.w)
        t.solid(tr, rng.choice(colours), at, d, centered(x, area.y + area.h, s, s * 0.9),
                [(0, {"s": 0.0}, "back"), (0.35, {}, "linear"), (d, {"dy": -rng.uniform(380, 640),
                                                                     "dx": rng.uniform(-80, 80)})],
                kind="heart", opacity=keys([(0, 1.0, "smooth"), (d * 0.6, 1.0, "smooth"), (d, 0.0)]))


def short_sigueme():
    """Big channel photo with pulses, the handle, a «Seguir» button that gets pressed, hearts floating up."""
    t = short("yt-final-short-sigueme", "Sígueme para más (Shorts)", "Follow for more (Shorts)", 12,
              ["sígueme para más", "seguir", "corazones", "pantalla final"], "#5B2EFF")
    bg_gradient(t, [(0, "#5B2EFF"), (1, "#FF4FA3")], angle=135)
    blobs(t, ["#FFFFFF", "#FFB3D9", "#8A6BFF"], seed=6562, alpha=0.22, size=(800, 1200), wander=150)
    label(t, t.track("text", "Título"), "¡Sígueme\npara más!", 0.2, 9.8, Box(60, 170, 960, 330), "Poppins", 130, "#FFFFFF",
          weight=900, line=1.0, layers=[shadow("#2A0E6B", 0, 12, 30, 0.45), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.45, unit="word", stagger=0.12), name="Título")
    pulses(t, "#FFFFFF", 540, 800, 440, 1.0, period=2.25, grow=1.3)
    avatar(t, "portrait-04", 540, 800, 440, 0.4, ring="#FFFFFF", ring_w=12)
    label(t, t.track("text", "Canal"), "@tucanal", 0.9, 9.1, Box(80, 1060, 920, 100), "Poppins", 70, "#FFFFFF",
          weight=700, anim_in=tanim("fade-up-char", duration=0.4, unit="character", stagger=0.03), name="Usuario del canal")
    follow_button(t, 540, 1260, 540, 136, 1.3, 2.8, [("#FFFFFF", "#FF2D7A"), ("#1A1033", "#FFFFFF")],
                  ["Seguir", "Siguiendo"])
    label(t, t.track("text", "Lema"), "nuevo video todos los días", 1.8, 8.2, Box(80, 1420, 920, 80), "Poppins", 46,
          "#FFFFFF", weight=500, anim_in=tanim("fade", duration=0.5), name="Lema")
    hearts(t, ["#FFFFFF", "#FFD1E8", "#FF2D7A"], 2.8, 6562, area=Box(120, 1500, 840, 380))
    t.song("inspiration", 2.0, 0.6)
    return t


def short_perfil():
    """A profile preview: photo, handle and three more shorts as cards, then «Seguir» turns to «Siguiendo»."""
    t = short("yt-final-short-perfil", "Más videos en mi perfil", "More videos on my profile", 13,
              ["perfil", "más videos", "shorts", "pantalla final"], "#0F0F14")
    bg_gradient(t, [(0, "#17171F"), (1, "#0A0A0E")], angle=90)
    soft_light(t, "#00E5A0", 900, 300, 1000, -120, 60, 0.2)
    label(t, t.track("text", "Título"), "Mira más en mi perfil", 0.2, 9.8, Box(60, 170, 960, 260), "Montserrat", 104,
          "#FFFFFF", weight=900, line=1.0, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1),
          name="Título")
    avatar(t, "portrait-06", 220, 560, 200, 0.5, ring="#00E5A0", ring_w=8)
    label(t, t.track("text", "Canal"), "@tucanal", 0.8, 9.2, Box(360, 500, 680, 76), "Montserrat", 58, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("fade", duration=0.4), name="Usuario del canal")
    label(t, t.track("text", "Datos"), "120 videos · uno nuevo cada día", 1.0, 9.0, Box(360, 578, 680, 50), "Montserrat",
          34, "#9A9AA8", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Datos del canal")
    for i, (s, x, views) in enumerate([("friends-03", 60, "1,2 M"), ("cooking-02", 390, "860 K"), ("travel-05", 720, "2,4 M")]):
        box = Box(x, 700, 300, 533)
        t0 = 1.0 + i * 0.2
        m = [(0, {"dy": 120}, "out"), (0.6, {}, "smooth"), (4.0 - i * 0.3, {"dy": -12}, "smooth"), (9.0 - t0, {})]
        rrect(t, t.track("shape", "Tarjeta"), "#22222C", t0, 10.0 - t0, Box(box.x - 6, box.y - 6, 312, 545), 22, m,
              layers=[shadow("#000000", 0, 14, 30, 0.5), fill("#22222C"), no_stroke()])
        t.photo(t.track("video", f"Video {i + 1}"), s, t0, 10.0 - t0, box, m, label=f"Video sugerido {i + 1}")
        t.solid(t.track("shape", "Sombra"), "#000000", t0, 10.0 - t0, Box(box.x, box.y + 400, 300, 133), m,
                layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.7)], angle=90), no_stroke()])
        t.solid(t.track("shape", "Play"), "#FFFFFF", t0, 10.0 - t0, Box(box.x + 18, box.y + 478, 34, 34), m,
                kind="triangle", rotation=keys([(0, 90)]))
        label(t, t.track("text", "Vistas"), views, t0, 10.0 - t0, Box(box.x + 60, box.y + 470, 230, 50), "Montserrat", 32,
              "#FFFFFF", weight=700, align="left", motion=m, name=f"Vistas del video {i + 1}")
    follow_button(t, 540, 1400, 600, 130, 1.8, 3.2, [("#00E5A0", "#0A0A0E"), ("#22222C", "#FFFFFF")],
                  ["Seguir", "Siguiendo"], font="Montserrat")
    label(t, t.track("text", "Gracias"), "¡Gracias por ver!", 2.2, 7.8, Box(80, 1550, 920, 90), "Montserrat", 54,
          "#FFFFFF", weight=600, anim_in=tanim("fade", duration=0.5), name="Gracias")
    t.song("advertime", 2.0, 0.6)
    return t


def short_acciones():
    """Over the user's last clip (blurred): the channel photo with a «+», and a side rail where like, comment,
    save and share pop in turn, each with its line."""
    t = short("yt-final-short-acciones", "¿Te gustó? Dale like y guárdalo", "Liked it? Like and save", 14,
              ["like", "guardar", "compartir", "comentar", "pantalla final"], "#111111", thumb_at=5.0)
    t.photo(t.track("video", "Fondo"), "creator-02", 0, 10.0, t.full, [(0, {"s": 1.1}, "linear"), (10.0, {"s": 1.2})],
            label="Tu último clip", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=28)])
    shade_full(t, 0.55, colour="#0B0B12")
    avatar(t, "selfie-02", 540, 240, 200, 0.3, ring="#FFFFFF", ring_w=6)
    t.solid(t.track("shape", "Más"), "#FF3B6B", 0.7, 9.3, centered(540, 345, 66, 66), pop(0, 0.4), kind="ellipse")
    label(t, t.track("text", "Más"), "+", 0.7, 9.3, centered(540, 341, 66, 66), "Poppins", 54, "#FFFFFF", weight=800,
          editable=False, motion=pop(0, 0.4))
    label(t, t.track("text", "Canal"), "@tucanal", 0.8, 9.2, Box(80, 395, 920, 70), "Poppins", 48, "#FFFFFF", weight=700,
          anim_in=tanim("fade", duration=0.4), name="Usuario del canal")
    label(t, t.track("text", "Título"), "¿Te gustó?", 0.5, 9.5, Box(70, 560, 760, 160), "Poppins", 120, "#FFFFFF",
          weight=900, align="left", anim_in=tanim("pop", duration=0.45), name="Título")
    label(t, t.track("text", "Sub"), "Ayúdame con estos 4 toques", 0.9, 9.1, Box(70, 730, 820, 80), "Poppins", 50,
          "#FFE14D", weight=700, align="left", line=1.1, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    actions = [("heart", "#FF3B6B", "Dale like"), ("speech-bubble", "#FFFFFF", "Comenta"),
               ("pentagon", "#FFE14D", "Guárdalo"), ("curved-arrow", "#FFFFFF", "Comparte")]
    for i, (kind, c, text) in enumerate(actions):
        y = 960 + i * 200
        at = 1.4 + i * 0.6
        t.solid(t.track("shape", "Botón"), "#FFFFFF", at, 10.0 - at, centered(910, y, 160, 160), pop(0, 0.4),
                kind="ellipse", alpha=0.16)
        icon = centered(910, y, 82, 82) if kind != "pentagon" else centered(910, y, 70, 86)
        motion = [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.55, {"s": 1.25}, "smooth"), (0.75, {})]
        t.solid(t.track("shape", "Icono"), c, at, 10.0 - at, icon, motion, kind=kind,
                rotation=keys([(0, 180 if kind == "pentagon" else 0)]))
        t.solid(t.track("shape", "Toque"), "#FFFFFF", at + 0.4, 0.6, centered(910, y, 160, 160),
                [(0, {"s": 1.0}, "out"), (0.6, {"s": 1.5})], kind="ellipse", layers=[hollow(), sl("#FFFFFF", 4)],
                opacity=keys([(0, 0.8, "smooth"), (0.6, 0.0)]))
        label(t, t.track("text", "Acción"), text, at + 0.15, 9.85 - at, Box(260, y - 45, 540, 90), "Poppins", 60, "#FFFFFF",
              weight=800, align="right", anim_in=tanim("slide-left", duration=0.35), name=f"Acción {i + 1}")
    label(t, t.track("text", "Cierre"), "¡Sígueme para más!", 4.2, 5.8, Box(60, 1740, 960, 110), "Poppins", 82,
          "#FFE14D", weight=900, anim_in=tanim("bounce", duration=0.45, unit="word", stagger=0.1), name="Cierre")
    t.song("funshine", 2.0, 0.6)
    return t


FINALS = [fin_columnas, fin_hud, fin_postal, fin_tech, fin_belleza, fin_comic, fin_pizarra, fin_vinilo, fin_minimal,
          fin_neon, fin_setentas, fin_liquido, short_sigueme, short_perfil, short_acciones]

TEMPLATES = INTROS + FINALS
