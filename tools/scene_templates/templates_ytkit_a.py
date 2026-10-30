"""Kit de YouTube, batch a (2026-10-30): Aperturas (channel openers, order 7100-7149, three vertical) and
Elementos (animated graphic elements to drop over a video, order 8100-8149). Same family as the prototypes in
templates_ytkit.py (palette, fonts, motion). Hand-drawn strokes, rings that draw themselves and the like use the
0.26 shape operators: a `custom` outline (SVG path on a 0..100 box) and Trim Paths keyed on `trimEnd`/`trimStart`.
"""

from __future__ import annotations

import math
import random

from kit import (Box, anim, bg, bg_gradient, centered, dots, effect, fade_kf, fill, framed, glow, gradient, hollow,
                 keys, label, line, no_stroke, outline, photo_bg, pill, pop, rrect, shadow, song, spike, tall,
                 tanim, wide)
from scene import argb

NAVY = "#0B1A2E"
DEEP = "#06101F"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MIST = "#A9B8CC"
LIGHT = "#F4F7FB"
NAVY2 = "#12305A"


def _kit(id, es, en, section, duration, order, tags, vertical=False, **kw):
    if vertical:
        return tall(f"ytk-{id}-vertical", f"{es} vertical", f"{en} (vertical)", "ytkit", duration, order=order,
                    tags=[f"kit:{section}", "youtube", "vertical"] + tags, **kw)
    return wide(f"ytk-{id}", es, en, "ytkit", duration, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


# --- helpers ---------------------------------------------------------------------------------------

def _stroke(colour, width, align="center", alpha=1.0):
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": align,
            "paint": {"kind": "solid", "color": argb(colour, alpha)}, "opacity": 1.0}


def _radial(colour, a0, a1=0.0):
    return {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "gradient", "color": argb(colour, a0),
                      "gradient": {"kind": "radial", "stops": [{"pos": 0, "color": argb(colour, a0)},
                                                               {"pos": 1, "color": argb(colour, a1)}],
                                   "angle": 0, "space": "block"}}}


def _trim(clip, draw=None, erase=None, ease="inout"):
    """Trim Paths: the outline draws itself (draw=(at, length), clip-relative) and/or erases from its start."""
    kf = clip["shapeStyle"].setdefault("keyframes", {})
    if draw:
        at, ln = draw
        kf["trimEnd"] = keys(([(0, 0, "hold")] if at > 0 else []) + [(at, 0, ease), (at + ln, 100)])
    if erase:
        at, ln = erase
        kf["trimStart"] = keys([(0, 0, "hold"), (at, 0, "inout"), (at + ln, 100)])
    return clip


def path(t, track, colour, t0, dur, box, d, width=10, *, filled=False, motion=None, draw=None, erase=None,
         layers=None, ease="inout", **extra):
    """A custom outline: a stroke (default) or a filled shape."""
    if layers is None:
        layers = [fill(colour), no_stroke()] if filled else [hollow(), _stroke(colour, width)]
    c = t.solid(track, colour, t0, dur, box, motion, kind="custom", layers=layers, **extra)
    c["shapeStyle"]["customPath"] = d
    return _trim(c, draw, erase, ease)


def ring_draw(t, track, colour, width, t0, dur, box, draw=None, erase=None, offset=0.0, motion=None, **extra):
    c = t.solid(track, colour, t0, dur, box, motion, kind="ellipse", layers=[hollow(), _stroke(colour, width, "inside")],
                **extra)
    if offset:
        c["shapeStyle"]["trimOffset"] = offset
    return _trim(c, draw, erase)


def _life(dur, length=0.45, out=0.3, grow=1.03, s0=0.0):
    """Pops in, grows a touch while it holds (never still), shrinks away at the end of the clip."""
    return [(0, {"s": s0}, "back"), (length, {}, "linear"), (dur - out, {"s": grow}, "in"), (dur, {"s": 0.0})]


def _spacing(clip, a, b):
    clip["textStyle"]["keyframes"] = {"letterSpacing": keys([(0, a, "linear"),
                                                             (clip["timelineDurationUs"] / 1e6, b)])}


WIPE_R = dict(duration=0.6, angle=0, softness=0.15)      # left -> right
WIPE_UP = dict(duration=0.6, angle=-90, softness=0.15)   # bottom -> top (text above a line)
WIPE_DOWN = dict(duration=0.6, angle=90, softness=0.15)  # top -> bottom (text under a line)

CHECK = "M 0 55 L 35 90 L 100 10"
OUT = lambda d=0.3: tanim("fade", duration=d)  # noqa: E731


# 1 Aperturas -------------------------------------------------------------------------------------

def apertura_anillo(vertical=False):
    t = _kit("apertura-anillo", "Apertura anillo", "Ring opener", "aperturas", 5.5, 7140 if vertical else 7100,
             ["intro", "canal", "logo", "apertura", "anillo"], vertical, thumb_at=2.8, background=DEEP)
    D, cx = t.duration, t.w / 2
    if vertical:
        cy, orb, teal, coral, logo, name_h, name_px, tag_px, line_w = 820, 676, 520, 598, 273, 150, 120, 47, 640
    else:
        cy, orb, teal, coral, logo, name_h, name_px, tag_px, line_w = 370, 600, 480, 550, 270, 150, 136, 46, 760
    bg_gradient(t, [(0, "#10284A"), (1, DEEP)], angle=90)
    dots(t, [TEAL, WHITE, MIST], 20, 0.0, D, seed=11, size=(4, 10), drift=60, alpha=0.5)
    dl = D - 0.9
    orbit = ring_draw(t, t.track("shape", "Órbita"), SUN, 7, 0.6, dl, centered(cx, cy, orb, orb),
                      rotation=keys([(0, 0, "linear"), (dl, 420)]), opacity=fade_kf(dl, 0.4, 0.4))
    orbit["shapeStyle"]["trimEnd"] = 12
    dl = D - 0.2
    ring_draw(t, t.track("shape", "Anillo"), TEAL, 13, 0.2, dl, centered(cx, cy, teal, teal), draw=(0, 1.0),
              erase=(dl - 0.75, 0.55), rotation=keys([(0, 0, "linear"), (dl, 110)]))
    dl = D - 0.35
    ring_draw(t, t.track("shape", "Anillo"), CORAL, 5, 0.35, dl, centered(cx, cy, coral, coral), draw=(0, 1.1),
              erase=(dl - 0.7, 0.5), offset=180, rotation=keys([(0, 0, "linear"), (dl, -80)]))
    dl = D - 0.85
    t.photo(t.track("video", "Logo"), "logo-07", 0.7, dl, centered(cx, cy, logo, logo), _life(dl, 0.5, 0.35, 1.05),
            label="Tu logo")
    # The name sits on the line (born from it, upwards), the tagline hangs under it.
    ly = cy + coral / 2 + 14 + name_h
    dl = D - 1.35
    t.solid(t.track("shape", "Línea"), TEAL, 1.2, dl, centered(cx, ly, line_w, 5),
            [(0, {"sx": 0.0}, "out"), (0.5, {}, "hold"), (dl - 0.45, {}, "in"), (dl, {"sx": 0.0})])
    label(t, t.track("text", "Canal"), "TU CANAL", 1.4, D - 1.8, Box(cx - 800 if not vertical else 60, ly - name_h - 6,
          1600 if not vertical else t.w - 120, name_h), "Sora", name_px, WHITE, weight=800, spacing=6,
          anim_in=tanim("wipe", **WIPE_UP), anim_out=OUT(), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 1.6, D - 2.0,
          Box(cx - 700 if not vertical else 60, ly + 16, 1400 if not vertical else t.w - 120, tag_px * 1.5),
          "Inter", tag_px, MIST, weight=500, spacing=4, anim_in=tanim("wipe", **WIPE_DOWN), anim_out=OUT(),
          name="Lema")
    song(t, "upbeat", 2)
    return t


def apertura_paneles(vertical=False):
    t = _kit("apertura-paneles", "Apertura paneles", "Split-panel opener", "aperturas", 5.5,
             7141 if vertical else 7101, ["intro", "canal", "logo", "apertura", "paneles"], vertical, thumb_at=2.8,
             background=DEEP)
    D, W, H = t.duration, t.w, t.h
    if vertical:
        cy, glow_d, logo, name_px, name_y, name_h, tag_px, tag_y = 860, 780, 200, 112, 145, 130, 32, 290
    else:
        cy, glow_d, logo, name_px, name_y, name_h, tag_px, tag_y = 320, 1050, 280, 168, 175, 200, 44, 395
    cx = W / 2
    bg_gradient(t, [(0, NAVY2), (1, DEEP)], angle=90)
    t.solid(t.track("shape", "Brillo"), TEAL, 0.6, D - 0.6, centered(cx, cy + 60, glow_d, glow_d), kind="ellipse",
            layers=[_radial(TEAL, 0.32), no_stroke()], opacity=fade_kf(D - 0.6, 0.6, 0.5))
    dl = D - 1.6
    t.photo(t.track("video", "Logo"), "logo-07", 1.0, dl, centered(cx, cy, logo, logo), _life(dl, 0.5, 0.3, 1.05),
            label="Tu logo")
    tw = W - 160
    label(t, t.track("text", "Canal"), "TU CANAL", 1.25, D - 1.9, Box(80, cy + name_y, tw, name_h), "Montserrat",
          name_px, WHITE, weight=900, spacing=4, anim_in=tanim("imf-slit-opening", duration=0.7), anim_out=OUT(),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.5, D - 2.15,
          Box(80, cy + tag_y, tw, tag_px * 1.7), "Inter", tag_px, TEAL, weight=700, spacing=10 if vertical else 14,
          anim_in=tanim("fade-up-char", duration=0.6), anim_out=OUT(), name="Lema")
    if vertical:
        halves = [(Box(0, 0, W, H / 2), (0, -H / 2), TEAL), (Box(0, H / 2, W, H / 2), (0, H / 2), CORAL)]
        seam = Box(0, H / 2 - 3, W, 6)
    else:
        halves = [(Box(0, 0, W / 2, H), (-W / 2, 0), TEAL), (Box(W / 2, 0, W / 2, H), (W / 2, 0), CORAL)]
        seam = Box(W / 2 - 3, 0, 6, H)
    for box, (ox, oy), colour in halves:
        # The navy panel behind leaves a beat later and comes back first: a two-tone edge.
        for c, opn, cls in ((NAVY2, 0.82, D - 0.68), (colour, 0.7, D - 0.55)):
            m = [(0, {}, "hold"), (opn, {}, "inout"), (opn + 0.6, {"dx": ox, "dy": oy}, "hold"),
                 (cls, {"dx": ox, "dy": oy}, "inout"), (cls + 0.5, {})]
            t.solid(t.track("shape", "Panel"), c, 0.0, D, box, m)
    line(t, t.track("shape", "Costura"), WHITE, 0.1, 0.8, seam, grow="c", length=0.45,
         opacity=keys([(0, 1, "hold"), (0.55, 1, "smooth"), (0.75, 0)]))
    song(t, "electro", 1)
    return t


def apertura_franjas():
    t = _kit("apertura-franjas", "Apertura franjas", "Stripe opener", "aperturas", 5.5, 7102,
             ["intro", "canal", "logo", "apertura", "franjas"], thumb_at=2.8, background=DEEP)
    D = t.duration
    bg(t, DEEP)
    dots(t, [TEAL, MIST], 16, 0.0, D, seed=3, size=(4, 9), drift=50, alpha=0.45)
    dl = D - 0.55
    t.solid(t.track("shape", "Acento"), SUN, 0.6, dl - 0.15, Box(0, 670, 1920, 12),
            [(0, {"sx": 0.0, "dx": -960}, "inout"), (0.8, {}, "hold"), (dl - 0.65, {}, "in"), (dl - 0.15, {"sy": 0.0})])
    t.solid(t.track("shape", "Banda"), WHITE, 0.45, dl, Box(0, 410, 1920, 260),
            [(0, {"sx": 0.0, "dx": -960}, "inout"), (0.8, {}, "hold"), (dl - 0.5, {}, "in"), (dl, {"sy": 0.0})])
    for i, c in enumerate([TEAL, CORAL, SUN, WHITE]):
        t.solid(t.track("shape", "Franja"), c, 0.1 + i * 0.08, 1.1, centered(960, 540, 220, 1500),
                [(0, {"dx": -1500}, "inout"), (1.1, {"dx": 1500})], rotation=keys([(0, 20)]))
    dl = D - 1.6
    t.solid(t.track("shape", "Círculo"), TEAL, 1.1, dl, centered(330, 540, 230, 230), _life(dl, 0.45, 0.3, 1.04),
            kind="ellipse", layers=[shadow("#000000", 0, 10, 26, 0.35), fill(TEAL), no_stroke()])
    t.photo(t.track("video", "Logo"), "logo-07", 1.2, dl - 0.1, centered(330, 540, 150, 150),
            _life(dl - 0.1, 0.45, 0.3, 1.04), label="Tu logo")
    for i in range(3):
        t.solid(t.track("shape", "Barras"), NAVY, 1.6 + i * 0.07, D - 2.35 - i * 0.07,
                Box(1640 + i * 40, 470, 18, 140), [(0, {"dy": -40, "s": 0.6}, "out"), (0.35, {})],
                rotation=keys([(0, 20)]), opacity=fade_kf(D - 2.35 - i * 0.07, 0.2, 0.25))
    label(t, t.track("text", "Canal"), "TU CANAL", 1.3, D - 2.0, Box(500, 425, 1100, 140), "Archivo Black", 104, NAVY,
          weight=400, align="left", spacing=2, anim_in=tanim("wipe", **WIPE_R), anim_out=OUT(),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.55, D - 2.25, Box(504, 568, 1100, 60), "Inter", 30,
          CORAL, weight=800, align="left", spacing=8, anim_in=tanim("wipe", **WIPE_R), anim_out=OUT(), name="Lema")
    song(t, "upbeat", 0)
    return t


def apertura_destello():
    t = _kit("apertura-destello", "Apertura destello de luz", "Light sweep opener", "aperturas", 5.0, 7103,
             ["intro", "canal", "logo", "apertura", "luz", "elegante"], thumb_at=3.6, background=DEEP)
    D = t.duration
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=90)
    t.solid(t.track("shape", "Brillo"), TEAL, 0.0, D, centered(960, 500, 1800, 1050), kind="ellipse",
            layers=[_radial(TEAL, 0.18), no_stroke()], opacity=fade_kf(D, 0.8, 0.4))
    dl = D - 0.6
    t.photo(t.track("video", "Logo"), "logo-07", 0.3, dl, centered(960, 250, 250, 250),
            [(0, {"s": 0.7, "dy": 20}, "out"), (0.8, {}, "linear"), (dl - 0.3, {"s": 1.04}, "in"), (dl, {"s": 0.0})],
            opacity=fade_kf(dl, 0.6, 0.0), label="Tu logo")
    label(t, t.track("text", "Canal"), "TU CANAL", 0.6, D - 1.0, Box(80, 390, 1760, 260), "Montserrat", 210, WHITE,
          weight=900, spacing=6, layers=[shadow("#000000", 0, 8, 24, 0.5), gradient([(0, WHITE), (1, MIST)], angle=90)],
          anim_in=tanim("blur-in", duration=0.9), anim_out=OUT(0.35), name="Nombre del canal")
    for x in (210, 1500):
        line(t, t.track("shape", "Línea"), TEAL, 1.3, D - 2.0, Box(x, 718, 210, 4), grow="c", length=0.5,
             opacity=fade_kf(D - 2.0, 0.05, 0.3))
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.4, D - 2.05, Box(440, 686, 1040, 70), "Inter", 42,
          TEAL, weight=700, spacing=12, anim_in=tanim("fade", duration=0.6), anim_out=OUT(), name="Lema")
    beam = t.track("shape", "Destello")
    for at in (1.0, 3.0):
        t.solid(beam, WHITE, at, 1.2, centered(960, 540, 320, 1700), [(0, {"dx": -1400}, "inout"), (1.2, {"dx": 1400})],
                layers=[gradient([(0, WHITE, 0.0), (0.5, WHITE, 0.5), (1, WHITE, 0.0)], angle=0), no_stroke()],
                rotation=keys([(0, 18)]), blendMode="add")
    song(t, "epic", 0)
    return t


def apertura_mosaico():
    t = _kit("apertura-mosaico", "Apertura mosaico", "Mosaic tiles opener", "aperturas", 5.5, 7104,
             ["intro", "canal", "logo", "apertura", "mosaico", "colores"], thumb_at=2.9, background=DEEP)
    D = t.duration
    bg_gradient(t, [(0, NAVY2), (1, DEEP)], angle=90)
    dl = D - 2.5
    t.photo(t.track("video", "Logo"), "logo-07", 1.6, dl, centered(960, 330, 290, 290), _life(dl, 0.5, 0.25, 1.05),
            label="Tu logo")
    label(t, t.track("text", "Canal"), "TU CANAL", 1.8, D - 2.7, Box(80, 500, 1760, 180), "Sora", 144, WHITE,
          weight=800, spacing=6, anim_in=tanim("rise-by-word", duration=0.6), anim_out=OUT(0.25),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 2.1, D - 3.0, Box(260, 690, 1400, 76), "Inter", 50,
          MIST, weight=500, spacing=4, anim_in=tanim("fade", duration=0.5), anim_out=OUT(0.25), name="Lema")
    for (x, y), c in zip([(250, 200), (1670, 200), (250, 880), (1670, 880)], [TEAL, CORAL, SUN, WHITE]):
        dl = D - 3.0
        t.solid(t.track("shape", "Adorno"), c, 2.0, dl, centered(x, y, 70, 70), _life(dl, 0.4, 0.25, 1.0),
                kind="rounded-rectangle", radius=12, rotation=keys([(0, 0, "linear"), (dl, 120)]))
    rng = random.Random(5)
    colours = [NAVY2, NAVY2, "#1B4A80", TEAL, TEAL, CORAL, SUN, WHITE]
    cols, rows, cw, ch = 6, 4, 320, 270
    tracks = [t.track("shape", "Mosaico") for _ in range(cols)]
    for c in range(cols):
        for r in range(rows):
            d = c + r
            colour = rng.choice(colours)
            box = centered(c * cw + cw / 2, r * ch + ch / 2, cw - 16, ch - 16)
            a, b = 0.05 + d * 0.04, 1.3 + d * 0.045
            t.solid(tracks[c], colour, a, b + 0.35 - a, box,
                    [(0, {"s": 0.0}, "back"), (0.35, {}, "hold"), (b - a, {}, "in"), (b - a + 0.35, {"s": 0.0})],
                    kind="rounded-rectangle", radius=20,
                    rotation=keys([(0, 0, "hold"), (b - a, 0, "in"), (b - a + 0.35, 90)]))
            back = D - 0.85 + d * 0.045
            t.solid(tracks[c], rng.choice(colours), back, D - back, box, [(0, {"s": 0.0}, "back"), (0.35, {})],
                    kind="rounded-rectangle", radius=20, rotation=keys([(0, -90, "out"), (0.35, 0)]))
    song(t, "upbeat", 3)
    return t


BRACKETS = "M 0 25 L 0 0 L 25 0 M 75 0 L 100 0 L 100 25 M 100 75 L 100 100 L 75 100 M 25 100 L 0 100 L 0 75"


def apertura_decodificar():
    t = _kit("apertura-decodificar", "Apertura digital", "Digital decode opener", "aperturas", 5.0, 7105,
             ["intro", "canal", "logo", "apertura", "glitch", "tecnología", "gaming"], thumb_at=3.0, background=DEEP)
    D = t.duration
    bg(t, DEEP)
    scan = t.solid(t.track("shape", "Líneas"), WHITE, 0.0, D, Box(0, 4, 1920, 2), alpha=0.05)
    scan["shapeStyle"].update(repeatCopies=60, repeatY=18)
    t.solid(t.track("shape", "Barrido"), TEAL, 0.0, D, Box(0, -200, 1920, 200), [(0, {}, "linear"), (D, {"dy": 1480})],
            layers=[gradient([(0, TEAL, 0.0), (1, TEAL, 0.1)], angle=90), no_stroke()])
    dl = D - 0.6
    path(t, t.track("shape", "Marco"), TEAL, 0.3, dl, centered(960, 320, 400, 400), BRACKETS, 10,
         motion=[(0, {"s": 1.5}, "out"), (0.6, {}, "linear"), (dl - 0.3, {"s": 1.04}, "in"), (dl, {"s": 1.6})],
         opacity=fade_kf(dl, 0.3, 0.3))
    for x, dx in ((520, -80), (1240, 80)):
        t.solid(t.track("shape", "Datos"), CORAL, 0.7, D - 1.3, Box(x, 314, 160, 12),
                [(0, {"sx": 0.0, "dx": dx}, "out"), (0.4, {})], opacity=fade_kf(D - 1.3, 0.05, 0.25))
    dl = D - 1.0
    t.photo(t.track("video", "Logo"), "logo-07", 0.6, dl, centered(960, 320, 260, 260), label="Tu logo",
            opacity=keys([(0, 0, "hold"), (0.06, 1, "hold"), (0.12, 0.2, "hold"), (0.2, 1, "hold"), (0.28, 0.4, "hold"),
                          (0.34, 1, "hold"), (dl - 0.3, 1, "hold"), (dl - 0.24, 0.2, "hold"), (dl - 0.18, 1, "hold"),
                          (dl - 0.1, 0, "hold"), (dl, 0)]))
    label(t, t.track("text", "Canal"), "TU CANAL", 0.9, D - 1.3, Box(80, 570, 1760, 190), "Orbitron", 140, TEAL,
          weight=800, spacing=10, layers=[glow(TEAL, 22, 0.55), fill(TEAL)],
          anim_in=tanim("ibs-digital-decode", duration=1.2), anim_out=tanim("om-glitch-slice", duration=0.4),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.8, D - 2.2, Box(160, 790, 1600, 70), "Orbitron", 40,
          MIST, weight=500, spacing=8, anim_in=tanim("typewriter", duration=1.0), anim_out=OUT(0.25), name="Lema")
    t.adjust([effect("digital_glitch", animated={"intensity": spike([0.9, 1.05, 2.6, 4.45, 4.6], 0.9, 0.18)},
                     rgbAmount=18)], name="Glitch")
    song(t, "electro", 2)
    return t


def apertura_tipografica():
    t = _kit("apertura-tipografica", "Apertura tipográfica", "Type block opener", "aperturas", 5.0, 7106,
             ["intro", "canal", "logo", "apertura", "tipografía", "coral"], thumb_at=2.8, background=CORAL)
    D = t.duration
    bg(t, CORAL)
    for (x, y, s, a) in ((180, 960, 900, 0.14), (1760, 110, 700, 0.12)):
        outline(t, t.track("shape", "Aro"), NAVY, 4, 0.0, D, centered(x, y, s, s), [(0, {}, "linear"), (D, {"s": 1.1})],
                kind="ellipse", alpha=a)
    dl = D - 0.3
    t.solid(t.track("shape", "Bloque"), NAVY, 0.15, dl, Box(250, 330, 1420, 360),
            [(0, {"sx": 0.0, "dx": -710}, "inout"), (0.5, {}, "linear"), (dl - 0.45, {"s": 1.015}, "in"),
             (dl, {"sx": 0.0, "dx": 710})])
    for i in range(3):
        t.solid(t.track("shape", "Barras"), SUN, 1.0 + i * 0.07, D - 1.6 - i * 0.07, Box(1560 + i * 42, 235, 20, 110),
                [(0, {"dy": -50}, "out"), (0.35, {})], rotation=keys([(0, 20)]),
                opacity=fade_kf(D - 1.6 - i * 0.07, 0.2, 0.25))
    dl = D - 1.3
    t.solid(t.track("shape", "Círculo"), WHITE, 0.9, dl, centered(960, 175, 150, 150), _life(dl, 0.45, 0.3, 1.05),
            kind="ellipse", layers=[shadow("#000000", 0, 8, 20, 0.25), fill(WHITE), no_stroke()])
    t.photo(t.track("video", "Logo"), "logo-01", 0.95, dl - 0.05, centered(960, 175, 104, 104),
            _life(dl - 0.05, 0.45, 0.3, 1.05), label="Tu logo")
    name = label(t, t.track("text", "Canal"), "TU CANAL", 0.6, D - 1.05, Box(250, 330, 1420, 360), "Anton", 260, WHITE,
                 weight=400, spacing=4, anim_in=tanim("imf-venetian-lines", duration=0.8),
                 anim_out=OUT(0.35), name="Nombre del canal")
    _spacing(name, 4, 16)
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.2, D - 1.8, Box(360, 704, 1200, 56), "Inter", 34,
          NAVY, weight=800, spacing=14, anim_in=tanim("wipe", **WIPE_DOWN), anim_out=OUT(), name="Lema")
    song(t, "upbeat", 6)
    return t


def apertura_collage(vertical=False):
    t = _kit("apertura-collage", "Apertura collage de fotos", "Photo collage opener", "aperturas", 6.0,
             7142 if vertical else 7107, ["intro", "canal", "logo", "apertura", "fotos", "collage"], vertical,
             thumb_at=3.2, background=DEEP)
    D, W, H = t.duration, t.w, t.h
    cx, cy = W / 2, H / 2
    bg_gradient(t, [(0, NAVY2), (1, DEEP)], angle=120)
    if vertical:
        cards = [(300, 620, -7, "h-nature-03"), (775, 580, 6, "h-beach-01"), (305, 1340, 5, "h-city-03"),
                 (780, 1380, -6, "h-food-02")]
        cw, chh = 400, 520
    else:
        cards = [(330, 520, -8, "h-nature-03"), (640, 560, 5, "h-beach-01"), (960, 500, -3, "h-city-03"),
                 (1280, 560, 6, "h-food-02"), (1590, 520, -6, "h-cafe-01")]
        cw, chh = 300, 400
    for i, (x, y, rot, sample) in enumerate(cards):
        a = 0.1 + i * 0.1
        dl = D - a
        m = [(0, {"dy": H * 0.9}, "out"), (0.7, {}, "linear"), (dl - 0.75 + i * 0.04, {"dy": -24}, "inout"),
             (dl - 0.15 + i * 0.03, {"dy": -H * 1.05})]
        framed(t, sample, a, dl, centered(x, y, cw, chh), m, border=12, radius=8, rotation=keys([(0, rot)]),
               label=f"Tu foto {i + 1}")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 2.0, D - 2.0, alpha=0.45, opacity=fade_kf(D - 2.0, 0.4, 0.4))
    pw = 900 if vertical else 980
    dl = D - 2.4
    rrect(t, t.track("shape", "Placa"), NAVY, 2.1, dl, centered(cx, cy, pw, 380), radius=28,
          layers=[shadow("#000000", 0, 18, 44, 0.5), fill(NAVY), no_stroke()], motion=_life(dl, 0.5, 0.3, 1.02))
    lx = cx - pw / 2 + 170
    dl = D - 2.6
    t.photo(t.track("video", "Logo"), "logo-07", 2.3, dl, centered(lx, cy, 200, 200), _life(dl, 0.45, 0.3, 1.04),
            label="Tu logo")
    bx = lx + 140
    t.solid(t.track("shape", "Barra"), TEAL, 2.5, D - 3.0, Box(bx, cy - 80, 8, 160),
            [(0, {"sy": 0.0, "dy": -80}, "out"), (0.35, {}, "hold"), (D - 3.35, {}, "in"), (D - 3.0, {"sy": 0.0})])
    label(t, t.track("text", "Canal"), "TU CANAL", 2.6, D - 3.2, Box(bx + 30, cy - 92, pw - 360, 110), "Sora",
          78 if vertical else 84, WHITE, weight=800, align="left", spacing=3, anim_in=tanim("wipe", **WIPE_R),
          anim_out=OUT(), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 2.85, D - 3.45, Box(bx + 34, cy + 24, pw - 360, 56),
          "Inter", 32, MIST, weight=500, align="left", spacing=2, anim_in=tanim("fade", duration=0.5),
          anim_out=OUT(), name="Lema")
    song(t, "upbeat", 4)
    return t


def apertura_linea():
    t = _kit("apertura-linea", "Apertura minimalista", "Minimal line opener", "aperturas", 5.5, 7108,
             ["intro", "canal", "logo", "apertura", "minimalista", "elegante"], thumb_at=3.0, background=DEEP)
    D = t.duration
    bg(t, DEEP)
    dl = D - 0.3
    t.solid(t.track("shape", "Línea"), WHITE, 0.2, dl, Box(260, 598, 1400, 4),
            [(0, {"sx": 0.0, "dx": -700}, "inout"), (0.9, {}, "hold"), (dl - 0.6, {}, "inout"),
             (dl, {"sx": 0.0, "dx": 700})])
    t.solid(t.track("shape", "Punto"), TEAL, 0.2, dl, centered(260, 600, 24, 24),
            [(0, {}, "inout"), (0.9, {"dx": 1400}, "hold"), (dl - 0.6, {"dx": 1400}, "inout"),
             (dl, {"dx": 1400, "s": 0.0})],
            kind="ellipse")
    halo = t.track("shape", "Pulso")
    for at in (1.3, 2.5, 3.7):
        ring_draw(t, halo, TEAL, 4, at, 1.0, centered(1660, 600, 30, 30), motion=[(0, {}, "out"), (1.0, {"s": 3.5})],
                  opacity=keys([(0, 0.9), (1.0, 0.0)]))
    dl = D - 1.6
    t.photo(t.track("video", "Logo"), "logo-07", 0.9, dl, centered(960, 285, 250, 250),
            [(0, {"s": 0.9}, "out"), (0.8, {}, "linear"), (dl, {"s": 1.05})], opacity=fade_kf(dl, 0.6, 0.35),
            label="Tu logo")
    name = label(t, t.track("text", "Canal"), "TU CANAL", 1.0, D - 1.65, Box(80, 430, 1760, 160), "Outfit", 128, WHITE,
                 weight=600, spacing=30, anim_in=tanim("wipe", duration=0.7, angle=-90, softness=0.15),
                 anim_out=tanim("wipe", duration=0.4, angle=-90, softness=0.15), name="Nombre del canal")
    _spacing(name, 30, 38)
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 1.2, D - 1.85, Box(160, 620, 1600, 70), "Inter", 44,
          MIST, weight=400, spacing=10, anim_in=tanim("wipe", **WIPE_DOWN),
          anim_out=tanim("wipe", duration=0.4, angle=90, softness=0.15), name="Lema")
    song(t, "calm", 4)
    return t


def apertura_clara():
    t = _kit("apertura-clara", "Apertura clara", "Light opener", "aperturas", 5.5, 7109,
             ["intro", "canal", "logo", "apertura", "claro", "blanco"], thumb_at=2.8, background=LIGHT)
    D = t.duration
    bg(t, LIGHT)
    for i, c in enumerate([TEAL, SUN, CORAL, LIGHT]):
        a = 0.05 + i * 0.14
        t.solid(t.track("shape", "Onda"), c, a, 1.45 - a, centered(960, 540, 100, 100),
                [(0, {"s": 0.0}, "out"), (0.9, {"s": 24})], kind="ellipse")
    dots(t, [TEAL, CORAL, SUN], 14, 1.2, D - 1.9, seed=4, size=(8, 18), drift=50, alpha=0.8)
    for (x, y, s, c) in ((250, 230, 110, TEAL), (1690, 860, 140, CORAL), (1650, 200, 70, SUN)):
        outline(t, t.track("shape", "Aro"), c, 5, 1.3, D - 2.0, centered(x, y, s, s), _life(D - 2.0, 0.5, 0.25, 1.15),
                kind="ellipse")
    dl = D - 1.7
    t.photo(t.track("video", "Logo"), "logo-01", 1.0, dl, centered(960, 315, 300, 300), _life(dl, 0.5, 0.3, 1.04),
            label="Tu logo")
    label(t, t.track("text", "Canal"), "TU CANAL", 1.2, D - 1.9, Box(80, 485, 1760, 180), "Sora", 150, NAVY,
          weight=800, spacing=4, anim_in=tanim("rise", duration=0.6), anim_out=OUT(0.25), name="Nombre del canal")
    dl = D - 2.2
    pill(t, t.track("shape", "Etiqueta"), TEAL, 1.5, dl, centered(960, 750, 780, 100), _life(dl, 0.4, 0.25, 1.0))
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 1.6, dl - 0.15, centered(960, 750, 780, 100), "Inter",
          46, NAVY, weight=700, spacing=2, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Lema")
    for i, c in enumerate([TEAL, NAVY]):
        a = D - 0.75 + i * 0.12
        t.solid(t.track("shape", "Cierre"), c, a, D - a, centered(960, 540, 100, 100),
                [(0, {"s": 0.0}, "inout"), (0.55, {"s": 24})], kind="ellipse")
    song(t, "fun", 1)
    return t


def apertura_explosion():
    t = _kit("apertura-explosion", "Apertura explosión", "Burst opener", "aperturas", 5.0, 7110,
             ["intro", "canal", "logo", "apertura", "energía", "rayos"], thumb_at=2.6, background=DEEP)
    D = t.duration
    cx, cy = 960, 345
    bg_gradient(t, [(0, NAVY2), (1, DEEP)], angle=90)
    dl = D - 0.7
    burst = t.solid(t.track("shape", "Estallido"), SUN, 0.4, dl, centered(cx, cy, 580, 580),
                    [(0, {"s": 0.0}, "back"), (0.5, {}, "linear"), (dl - 0.4, {"s": 1.05}, "in"), (dl, {"s": 0.0})],
                    kind="burst", rotation=keys([(0, 0, "linear"), (dl, 70)]))
    burst["shapeStyle"].update(points=18, innerRatio=0.82)
    for wave, (at, r0, r1, n, w) in enumerate(((0.5, 300, 700, 14, 14), (2.8, 300, 600, 14, 8))):
        rays = [t.track("shape", "Rayos") for _ in range(2)]
        for i in range(n):
            ang = 2 * math.pi * (i + wave * 0.5) / n
            ca, sa = math.cos(ang), math.sin(ang)
            c = [TEAL, CORAL, WHITE][i % 3]
            t.solid(rays[i % 2], c, at + (i % 2) * 0.05, 0.7, centered(cx, cy, w, 120),
                    [(0, {"dx": ca * r0, "dy": sa * r0}, "out"), (0.7, {"dx": ca * r1, "dy": sa * r1})],
                    kind="rounded-rectangle", radius=w / 2, rotation=keys([(0, math.degrees(ang) + 90)]),
                    opacity=keys([(0, 1, "hold"), (0.35, 1, "smooth"), (0.7, 0)]))
    dl = D - 0.9
    t.solid(t.track("shape", "Círculo"), NAVY, 0.5, dl, centered(cx, cy, 420, 420), _life(dl, 0.5, 0.35, 1.04),
            kind="ellipse", layers=[shadow("#000000", 0, 10, 30, 0.45), fill(NAVY), no_stroke()])
    dl = D - 1.0
    t.photo(t.track("video", "Logo"), "logo-07", 0.6, dl, centered(cx, cy, 290, 290), _life(dl, 0.5, 0.35, 1.04),
            label="Tu logo")
    label(t, t.track("text", "Canal"), "TU CANAL", 1.0, D - 1.4, Box(80, 650, 1760, 210), "Anton", 172, WHITE,
          weight=400, spacing=6, anim_in=tanim("pop", duration=0.4), anim_out=OUT(), name="Nombre del canal")
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.4, D - 1.8, Box(160, 868, 1600, 70), "Inter", 42,
          TEAL, weight=700, spacing=10, anim_in=tanim("fade", duration=0.5), anim_out=OUT(), name="Lema")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.5, 1.05, 2.8], 0.5, 0.3)})], name="Golpe")
    song(t, "epic", 1)
    return t


CORNERS = {"tl": ("M 0 100 L 0 0 L 100 0", -1, -1), "tr": ("M 0 0 L 100 0 L 100 100", 1, -1),
           "br": ("M 100 0 L 100 100 L 0 100", 1, 1), "bl": ("M 100 100 L 0 100 L 0 0", -1, 1)}


def _corners(t, frame: Box, colour, width, t0, dur, size=140, start=400, end=600, draw=(0, 0.7), breathe=12,
             name="Esquina", alpha_fade=False):
    for key, (d, sx, sy) in CORNERS.items():
        x = frame.x if sx < 0 else frame.x + frame.w - size
        y = frame.y if sy < 0 else frame.y + frame.h - size
        m = [(0, {"dx": sx * start, "dy": sy * start}, "out"), (0.7, {}, "smooth"),
             (2.0, {"dx": sx * breathe, "dy": sy * breathe}, "smooth"), (3.3 if dur > 3.6 else 2.4, {}, "hold"),
             (dur - 0.5, {}, "in"), (dur, {"dx": sx * end, "dy": sy * end})]
        if dur <= 2.6:
            m = [(0, {"dx": sx * start, "dy": sy * start}, "out"), (0.6, {}, "hold"), (dur - 0.4, {}, "in"),
                 (dur, {"dx": sx * end, "dy": sy * end})]
        extra = {"opacity": fade_kf(dur, 0.3, 0.4)} if alpha_fade else {}
        path(t, t.track("shape", name), colour, t0, dur, Box(x, y, size, size), d, width, motion=m, draw=draw, **extra)


def apertura_esquinas():
    t = _kit("apertura-esquinas", "Apertura esquinas", "Corner frame opener", "aperturas", 5.5, 7111,
             ["intro", "canal", "logo", "apertura", "marco", "amarillo"], thumb_at=2.8, background=SUN)
    D = t.duration
    bg(t, SUN)
    for (x, y, s) in ((200, 960, 900), (1750, 120, 700)):
        outline(t, t.track("shape", "Aro"), NAVY, 3, 0.0, D, centered(x, y, s, s), [(0, {}, "linear"), (D, {"s": 1.08})],
                kind="ellipse", alpha=0.14)
    for i, (x, y) in enumerate(((960, 110), (960, 970), (180, 540), (1740, 540))):
        dl = D - 1.5 - i * 0.05
        t.solid(t.track("shape", "Cruz"), NAVY, 0.9 + i * 0.05, dl, centered(x, y, 44, 44), _life(dl, 0.4, 0.3, 1.0),
                kind="cross", rotation=keys([(0, 0, "linear"), (dl, 90)]))[
            "shapeStyle"].update(thickness=0.22)
    _corners(t, centered(960, 540, 1560, 860), NAVY, 18, 0.2, D - 0.2, size=190)
    dl = D - 1.5
    t.photo(t.track("video", "Logo"), "logo-01", 0.8, dl, centered(960, 320, 260, 260), _life(dl, 0.45, 0.3, 1.05),
            label="Tu logo")
    label(t, t.track("text", "Canal"), "TU CANAL", 1.0, D - 1.7, Box(200, 465, 1520, 200), "Archivo Black", 160, NAVY,
          weight=400, spacing=2, anim_in=tanim("rise", duration=0.5), anim_out=OUT(), name="Nombre del canal")
    dl = D - 2.0
    t.solid(t.track("shape", "Línea"), NAVY, 1.2, dl, centered(960, 700, 340, 6),
            [(0, {"sx": 0.0}, "out"), (0.45, {}, "hold"), (dl - 0.35, {}, "in"), (dl, {"sx": 0.0})])
    label(t, t.track("text", "Lema"), "VIDEOS NUEVOS CADA SEMANA", 1.35, D - 2.2, Box(200, 722, 1520, 70), "Inter", 44,
          NAVY, weight=700, spacing=8, anim_in=tanim("wipe", **WIPE_DOWN), anim_out=OUT(), name="Lema")
    song(t, "upbeat", 1)
    return t


# 11 Elementos ------------------------------------------------------------------------------------

def elemento_flecha():
    t = _kit("elemento-flecha", "Flecha dibujada", "Hand-drawn arrow", "elementos", 4.0, 8100,
             ["elementos", "flecha", "señalar", "mira esto"], thumb_at=1.9)
    photo_bg(t, "h-portrait-02", s1=1.03, label="Tu video")
    label(t, t.track("text", "Texto"), "¡MIRA ESTO!", 0.2, 3.5, Box(130, 250, 680, 130), "Poppins", 86, SUN,
          weight=800, italic=True, layers=[shadow("#000000", 0, 6, 16, 0.55), fill(SUN)],
          anim_in=tanim("pop", duration=0.4), anim_out=tanim("shrink", duration=0.3), name="Texto")
    path(t, t.track("shape", "Marcas"), WHITE, 0.2, 3.4, Box(92, 196, 80, 80),
         "M 70 80 L 30 40 M 88 62 L 82 8 M 52 94 L 4 86", 7, draw=(0.3, 0.3), erase=(3.0, 0.3))
    nudge = [(0, {"dx": -50}, "smooth"), (1.7, {"dx": -50}, "smooth"), (2.0, {"dx": -40, "dy": 7}, "smooth"),
             (2.3, {"dx": -50}, "smooth"), (2.6, {"dx": -40, "dy": 7}, "smooth"), (2.9, {"dx": -50})]
    path(t, t.track("shape", "Flecha"), CORAL, 0.4, 3.5, Box(690, 340, 420, 200), "M 0 80 C 25 0 70 0 98 50", 12,
         motion=nudge, draw=(0.15, 0.6), erase=(2.95, 0.4))
    path(t, t.track("shape", "Punta"), CORAL, 0.4, 3.5, Box(1040, 380, 80, 80), "M 62.5 20 L 76.25 75 L 20 70", 12,
         motion=nudge, draw=(0.72, 0.22), erase=(2.9, 0.2))
    return t


LOOP = ("M 78 14 C 60 2 22 4 8 30 C -4 54 14 88 50 94 C 84 99 102 70 96 42 C 92 22 74 8 48 8 C 34 8 24 12 18 16")
LOOP2 = "M 74 10 C 50 -2 14 8 6 38 C -2 66 24 94 56 92 C 88 90 100 62 94 36 C 90 18 70 4 40 6"


def elemento_circulo():
    t = _kit("elemento-circulo", "Círculo a mano", "Hand-drawn circle", "elementos", 3.5, 8101,
             ["elementos", "círculo", "resaltar", "señalar"], thumb_at=1.8)
    photo_bg(t, "h-food-02", s1=1.0, label="Tu video")
    path(t, t.track("shape", "Círculo"), CORAL, 0.3, 3.1, centered(860, 330, 380, 280), LOOP, 11, draw=(0, 0.9),
         erase=(2.5, 0.45))
    path(t, t.track("shape", "Círculo"), WHITE, 0.55, 2.85, centered(860, 330, 400, 296), LOOP2, 4, draw=(0, 0.8),
         erase=(2.2, 0.45))
    dl = 2.3
    m = [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (0.9, {"dy": -6}, "smooth"), (1.4, {}, "smooth"),
         (dl - 0.25, {"dy": -6}, "inout"), (dl, {"s": 0.0})]
    pill(t, t.track("shape", "Etiqueta"), SUN, 1.0, dl, Box(1040, 140, 280, 86), m, rotation=keys([(0, -6)]),
         layers=[shadow("#000000", 0, 6, 16, 0.35), fill(SUN), no_stroke()])
    label(t, t.track("text", "Etiqueta"), "¡ESTE!", 1.0, dl - 0.05, Box(1040, 140, 280, 86), "Sora", 44, NAVY, weight=800,
          motion=[(0, {}, "smooth"), (0.9, {"dy": -6}, "smooth"), (1.4, {}, "smooth"), (dl, {"dy": -6})],
          anim_in=tanim("pop", duration=0.4), anim_out=OUT(0.2), rotation=keys([(0, -6)]), name="Etiqueta")
    return t


WAVE = ("M 0 50 C 8 0 17 0 25 50 C 33 100 42 100 50 50 C 58 0 67 0 75 50 C 83 100 92 100 100 50")


def elemento_subrayados():
    t = _kit("elemento-subrayados", "Subrayados y marcador", "Underlines and marker", "elementos", 4.0, 8102,
             ["elementos", "subrayado", "marcador", "resaltar", "texto"], thumb_at=2.4, background=NAVY)
    bg(t, NAVY)
    t.solid(t.track("shape", "Marcador"), SUN, 0.2, 3.3, Box(620, 252, 680, 104),
            [(0, {"sx": 0.0, "dx": -340}, "inout"), (0.45, {}, "hold"), (3.0, {}, "inout"), (3.3, {"sx": 0.0, "dx": 340})],
            rotation=keys([(0, -1.5)]))
    label(t, t.track("text", "Palabra"), "MARCADOR", 0.3, 3.15, Box(560, 244, 800, 120), "Montserrat", 92, NAVY,
          weight=900, anim_in=tanim("wipe", duration=0.4, angle=0, softness=0.15), anim_out=OUT(0.2), name="Palabra 1")
    label(t, t.track("text", "Palabra"), "ONDULADO", 0.8, 2.9, Box(560, 470, 800, 120), "Montserrat", 92, WHITE,
          weight=900, anim_in=tanim("fade-up-char", duration=0.5), anim_out=OUT(), name="Palabra 2")
    path(t, t.track("shape", "Onda"), TEAL, 1.1, 2.5, Box(650, 588, 620, 32), WAVE, 8, draw=(0, 0.6), erase=(2.0, 0.4))
    label(t, t.track("text", "Palabra"), "SUBRAYADO", 1.4, 2.3, Box(560, 710, 800, 120), "Montserrat", 92, WHITE,
          weight=900, anim_in=tanim("fade-up-char", duration=0.5), anim_out=OUT(), name="Palabra 3")
    path(t, t.track("shape", "Trazo"), CORAL, 1.7, 2.0, Box(630, 822, 660, 44),
         "M 0 35 C 30 20 70 30 100 15 M 6 85 C 40 70 70 80 98 62", 8, draw=(0, 0.5), erase=(1.5, 0.4))
    return t


def elemento_destellos():
    t = _kit("elemento-destellos", "Destellos", "Sparkles", "elementos", 3.5, 8103,
             ["elementos", "brillo", "estrellas", "magia", "nuevo"], thumb_at=1.5, background=DEEP)
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=90)
    ring_draw(t, t.track("shape", "Onda"), WHITE, 4, 0.25, 0.8, centered(960, 540, 260, 260),
              motion=[(0, {"s": 0.3}, "out"), (0.8, {"s": 3.4})], opacity=keys([(0, 1.0), (0.8, 0.0)]))
    dots(t, [SUN, WHITE], 16, 0.3, 2.9, seed=9, size=(6, 14), drift=40, area=Box(420, 120, 1080, 840))
    stars = [(960, 540, 340, SUN, 0.2), (700, 330, 150, WHITE, 0.35), (1250, 340, 120, TEAL, 0.45),
             (1220, 780, 170, WHITE, 0.4), (680, 790, 110, SUN, 0.55), (500, 560, 80, TEAL, 0.6),
             (1440, 560, 95, SUN, 0.5), (860, 190, 70, WHITE, 0.65)]
    for i, (x, y, s, c, at) in enumerate(stars):
        dl = 2.9 + at * 0.6 - at
        m = [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth")]
        k, tt = 0, 0.4 + (i % 3) * 0.12
        while tt + 0.35 < dl - 0.35:
            tt += 0.35
            k += 1
            m.append((tt, {"s": 0.78} if k % 2 else {}, "smooth"))
        m += [(dl - 0.3, {}, "in"), (dl, {"s": 0.0})]
        st = t.solid(t.track("shape", "Destello"), c, at, dl, centered(x, y, s, s), m, kind="star",
                     layers=[glow(c, 26, 0.7), fill(c), no_stroke()],
                     rotation=keys([(0, -60, "out"), (0.5, 0, "linear"), (dl, 25)]))
        st["shapeStyle"].update(points=4, innerRatio=0.22)
    return t


CURSOR = "M 0 0 L 0 82 L 22 64 L 36 98 L 52 92 L 38 59 L 66 59 Z"


def _cursor(t, tip_x, tip_y, t0, dur, click, leave, frm=(520, 300)):
    m = [(0, {"dx": frm[0], "dy": frm[1]}, "out"), (click - 0.15, {}, "hold"), (click, {"s": 0.82}, "out"),
         (click + 0.15, {}, "hold"), (leave, {}, "inout"), (dur, {"dx": frm[0] + 60, "dy": frm[1] + 60})]
    path(t, t.track("shape", "Cursor"), WHITE, t0, dur, Box(tip_x, tip_y, 64, 92), CURSOR, motion=m,
         layers=[shadow("#000000", 0, 6, 12, 0.45), fill(WHITE), _stroke(NAVY, 5, "inside")])


def elemento_clic():
    t = _kit("elemento-clic", "Botón con clic", "Click button", "elementos", 3.5, 8104,
             ["elementos", "clic", "cursor", "botón", "puntero"], thumb_at=1.7)
    photo_bg(t, "h-cafe-01", s1=1.03, label="Tu video")
    box = centered(960, 540, 560, 130)
    pill(t, t.track("shape", "Botón"), WHITE, 0.2, 1.15, box,
         [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (0.95, {}, "out"), (1.1, {"s": 0.93})],
         layers=[shadow("#000000", 0, 10, 26, 0.4), fill(WHITE), no_stroke()])
    pill(t, t.track("shape", "Botón"), TEAL, 1.35, 1.95, box,
         [(0, {"s": 0.93}, "back"), (0.3, {}, "linear"), (1.7, {"s": 1.02}, "inout"), (1.95, {"s": 0.0})],
         layers=[shadow("#000000", 0, 10, 26, 0.4), fill(TEAL), no_stroke()])
    label(t, t.track("text", "Botón"), "CLIC AQUÍ", 0.3, 2.95, box, "Sora", 52, NAVY, weight=800, spacing=4,
          anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Botón")
    for i, c in enumerate([TEAL, WHITE]):
        ring_draw(t, t.track("shape", "Onda"), c, 5 - i, 1.3 + i * 0.1, 0.7, centered(1030, 575, 120, 120),
                  motion=[(0, {"s": 0.2}, "out"), (0.7, {"s": 2.6})], opacity=keys([(0, 1.0), (0.7, 0.0)]))
    _cursor(t, 1030, 575, 0.4, 2.6, 0.85, 2.0)
    return t


BELL = ("M 50 4 C 30 4 18 20 18 42 L 18 62 L 6 78 L 94 78 L 82 62 L 82 42 C 82 20 70 4 50 4 Z "
        "M 38 84 C 38 98 62 98 62 84 Z")


def elemento_suscribete():
    t = _kit("elemento-suscribete", "Botón suscríbete con campana", "Subscribe button with bell", "elementos", 4.0,
             8105, ["elementos", "suscríbete", "campana", "botón", "clic"], thumb_at=1.2)
    photo_bg(t, "h-man-02", s1=1.03, label="Tu video")
    cy = 880
    box = centered(960, cy, 600, 124)
    sh = shadow("#000000", 0, 10, 28, 0.4)
    pill(t, t.track("shape", "Botón"), CORAL, 0.2, 1.35, box,
         [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (1.1, {}, "out"), (1.25, {"s": 0.94})],
         layers=[sh, fill(CORAL), no_stroke()])
    pill(t, t.track("shape", "Botón"), NAVY, 1.55, 2.35, box,
         [(0, {"s": 0.94}, "back"), (0.3, {}, "linear"), (2.0, {"s": 1.02}, "in"), (2.35, {"s": 0.0})],
         layers=[sh, fill(NAVY), _stroke(TEAL, 4, "inside")])
    cx = 960 - 300 + 76
    t.solid(t.track("shape", "Círculo"), WHITE, 0.35, 3.55, centered(cx, cy, 92, 92),
            [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (3.2, {}, "in"), (3.55, {"s": 0.0})], kind="ellipse")
    bell_box = centered(cx, cy - 2, 52, 56)
    path(t, t.track("shape", "Campana"), CORAL, 0.45, 1.1, bell_box, BELL, filled=True, motion=pop(0, 0.4))
    wob = [(0, 0, "hold"), (0.15, 0, "smooth"), (0.25, 20, "smooth"), (0.35, -18, "smooth"), (0.45, 14, "smooth"),
           (0.55, -10, "smooth"), (0.65, 6, "smooth"), (0.75, 0, "hold"), (1.3, 0, "smooth"), (1.4, 12, "smooth"),
           (1.5, -10, "smooth"), (1.6, 6, "smooth"), (1.7, 0)]
    path(t, t.track("shape", "Campana"), NAVY, 1.55, 2.35, bell_box, BELL, filled=True,
         motion=[(0, {}, "hold"), (2.0, {}, "in"), (2.35, {"s": 0.0})], rotation=keys(wob))
    t.solid(t.track("shape", "Aviso"), SUN, 1.75, 2.1, centered(cx + 32, cy - 32, 28, 28),
            [(0, {"s": 0.0}, "back"), (0.35, {}, "hold"), (1.8, {}, "in"), (2.1, {"s": 0.0})], kind="ellipse",
            layers=[fill(SUN), _stroke(NAVY, 4, "inside")])
    tb = Box(cx + 52, cy - 62, 600 - 76 - 52 - 30, 124)
    label(t, t.track("text", "Botón"), "SUSCRÍBETE", 0.4, 1.15, tb, "Sora", 46, WHITE, weight=800, spacing=3,
          anim_in=tanim("fade", duration=0.3), name="Botón")
    label(t, t.track("text", "Botón"), "SUSCRITO", 1.55, 2.1, tb, "Sora", 46, WHITE, weight=800, spacing=3,
          anim_in=tanim("fade", duration=0.2), anim_out=OUT(0.25), name="Botón tras el clic")
    _cursor(t, 1100, 905, 0.6, 2.3, 0.8, 1.7)
    return t


def elemento_visor():
    t = _kit("elemento-visor", "Visor de cámara", "Camera viewfinder", "elementos", 3.5, 8106,
             ["elementos", "cámara", "grabando", "rec", "enfoque", "marco"], thumb_at=1.6)
    photo_bg(t, "h-portrait-05", s1=1.03, label="Tu video")
    for box, grow in ((Box(640, 0, 2, 1080), "c"), (Box(1280, 0, 2, 1080), "c"), (Box(0, 360, 1920, 2), "c"),
                      (Box(0, 720, 1920, 2), "c")):
        m = [(0, {"sy" if box.w < 10 else "sx": 0.0}, "out"), (0.6, {})]
        t.solid(t.track("shape", "Cuadrícula"), WHITE, 0.1, 3.3, box, m, alpha=0.3, opacity=fade_kf(3.3, 0.05, 0.3))
    for key, (d, sx, sy) in CORNERS.items():
        x = 80 if sx < 0 else 1920 - 80 - 70
        y = 80 if sy < 0 else 1080 - 80 - 70
        path(t, t.track("shape", "Borde"), WHITE, 0.1, 3.3, Box(x, y, 70, 70), d, 5, draw=(0, 0.4),
             opacity=fade_kf(3.3, 0.05, 0.3))
    _corners(t, centered(905, 420, 460, 460), WHITE, 8, 0.25, 3.0, size=90, start=120, end=80, draw=None,
             name="Enfoque", alpha_fade=True)
    t.solid(t.track("shape", "Punto"), CORAL, 0.3, 3.0, centered(140, 160, 26, 26), pop(0, 0.3), kind="ellipse",
            opacity=keys([(0, 1, "hold"), (0.5, 0.15, "hold"), (1.0, 1, "hold"), (1.5, 0.15, "hold"), (2.0, 1, "hold"),
                          (2.5, 0.15, "hold"), (2.7, 1, "smooth"), (3.0, 0)]))
    label(t, t.track("text", "Rec"), "REC", 0.3, 3.0, Box(166, 136, 160, 48), "Inter", 36, WHITE, weight=800,
          align="left", spacing=3, anim_in=tanim("fade", duration=0.3), anim_out=OUT(), name="Grabando")
    label(t, t.track("text", "Tiempo"), "00:12:48", 0.3, 3.0, Box(1440, 136, 340, 48), "Inter", 34, WHITE, weight=600,
          align="right", spacing=3, anim_in=tanim("fade", duration=0.3), anim_out=OUT(), name="Tiempo")
    return t


def elemento_cargando():
    t = _kit("elemento-cargando", "Barra de carga", "Loading bar", "elementos", 3.5, 8107,
             ["elementos", "cargando", "progreso", "barra", "listo"], thumb_at=1.6, background=NAVY)
    bg(t, NAVY)
    bar = Box(375, 520, 1170, 34)
    pill(t, t.track("shape", "Pista"), WHITE, 0.1, 3.3, bar,
         [(0, {"sx": 0.0}, "out"), (0.4, {}, "hold"), (2.9, {}, "in"), (3.3, {"sx": 0.0})], alpha=0.15)
    prog = [(0, 0.02), (0.6, 0.35), (1.0, 0.42), (1.7, 0.85), (2.1, 1.0)]
    m = [(tt, {"sx": p, "dx": -(1 - p) * bar.w / 2}, "smooth") for tt, p in prog]
    m += [(2.5, {}, "in"), (2.9, {"sx": 0.0})]
    pill(t, t.track("shape", "Progreso"), TEAL, 0.4, 2.9, bar, m,
         layers=[glow(TEAL, 20, 0.6), fill(TEAL), no_stroke()])
    label(t, t.track("text", "Texto"), "CARGANDO", 0.2, 2.45, Box(360, 400, 1200, 84), "Sora", 54, WHITE, weight=700,
          spacing=16, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Texto")
    for i in range(3):
        t.solid(t.track("shape", "Puntos"), TEAL, 0.3, 2.3, centered(1195 + i * 34, 448, 16, 16), kind="ellipse",
                opacity=_dots_blink(i, 2.3))
    label(t, t.track("text", "Listo"), "¡LISTO!", 2.65, 0.8, Box(360, 384, 1200, 110), "Sora", 80, TEAL, weight=800,
          spacing=6, anim_in=tanim("pop", duration=0.3), anim_out=OUT(0.2), name="Texto al terminar")
    t.solid(t.track("shape", "Visto"), TEAL, 2.5, 0.95, centered(1545, 537, 96, 96),
            [(0, {"s": 0.0}, "back"), (0.35, {}, "hold"), (0.65, {}, "in"), (0.95, {"s": 0.0})], kind="ellipse")
    path(t, t.track("shape", "Visto"), NAVY, 2.5, 0.95, centered(1545, 539, 46, 40), CHECK, 9, draw=(0.2, 0.25),
         motion=[(0, {}, "hold"), (0.65, {}, "in"), (0.95, {"s": 0.0})])
    return t


def _dots_blink(i, dur):
    pts, k = [(0, 0.2, "hold")], 0
    while True:
        a = 0.15 + k * 0.6 + i * 0.15
        if a + 0.3 > dur:
            break
        pts += [(a, 1.0, "hold"), (a + 0.3, 0.2, "hold")]
        k += 1
    return keys(pts)


def elemento_barras():
    t = _kit("elemento-barras", "Grupos de barras diagonales", "Slash groups", "elementos", 3.5, 8108,
             ["elementos", "barras", "diagonales", "adornos", "marco"], thumb_at=1.6)
    photo_bg(t, "h-city-05", s1=1.04, label="Tu video")
    cols = [TEAL, TEAL, CORAL, SUN]
    for g, (x0, y0, step, dy) in enumerate(((160, 110, 66, -340), (1724, 700, -66, 340))):
        for i, c in enumerate(cols):
            a = 0.15 + i * 0.07
            dl = 3.3 - a - (3 - i) * 0.05
            m = [(0, {"dy": dy}, "out"), (0.45, {}, "smooth"), (1.4, {"dy": -dy * 0.05}, "smooth"), (2.2, {}, "hold"),
                 (dl - 0.35, {}, "in"), (dl, {"dy": -dy})]
            t.solid(t.track("shape", "Barras"), c, a, dl, Box(x0 + i * step, y0, 36, 260), m,
                    rotation=keys([(0, 22)]), opacity=fade_kf(dl, 0.2, 0.3))
    line(t, t.track("shape", "Línea"), WHITE, 0.5, 2.8, Box(130, 410, 480, 5), grow="x", length=0.5,
         opacity=fade_kf(2.8, 0.05, 0.3))
    t.solid(t.track("shape", "Línea"), WHITE, 0.5, 2.8, Box(1310, 665, 480, 5),
            [(0, {"sx": 0.0, "dx": 240}, "out"), (0.5, {})], opacity=fade_kf(2.8, 0.05, 0.3))
    for (x, y, c) in ((620, 260, SUN), (1300, 820, TEAL)):
        ring_draw(t, t.track("shape", "Aro"), c, 5, 0.7, 2.5, centered(x, y, 56, 56), draw=(0, 0.4),
                  erase=(2.1, 0.35))
    return t


def elemento_globos():
    t = _kit("elemento-globos", "Globos de diálogo", "Speech bubbles", "elementos", 4.0, 8109,
             ["elementos", "globo", "diálogo", "conversación", "texto"], thumb_at=2.0)
    photo_bg(t, "h-podcast-02", s1=1.03, label="Tu video")
    for (x, y, c, tail, at, end, text, nm) in ((200, 120, WHITE, 0.78, 0.2, 3.55, "¿Sabías que…?", "Globo 1"),
                                               (1160, 150, TEAL, 0.22, 1.0, 3.75, "¡Te lo cuento!", "Globo 2")):
        dl = end - at
        m = [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"), (dl - 0.25, {"s": 1.03}, "inout"), (dl, {"s": 0.0})]
        b = t.solid(t.track("shape", "Globo"), c, at, dl, Box(x, y, 560, 250), m, kind="speech-bubble",
                    layers=[shadow("#000000", 0, 10, 26, 0.35), fill(c), no_stroke()])
        b["shapeStyle"].update(tailX=tail, tailSize=0.22)
        label(t, t.track("text", "Globo"), text, at + 0.15, dl - 0.2, Box(x + 20, y, 520, 195), "Sora", 48, NAVY,
              weight=800, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name=nm)
    return t


CROSS_A, CROSS_B = "M 0 0 L 100 100", "M 100 0 L 0 100"


def elemento_check_cruz():
    t = _kit("elemento-check-cruz", "Sí y no", "Check and cross", "elementos", 3.5, 8110,
             ["elementos", "check", "cruz", "correcto", "incorrecto", "comparar"], thumb_at=1.8, background=NAVY)
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=90)
    for (x, c, at, ink, kind, nm, text) in ((640, CORAL, 0.2, WHITE, "x", "Etiqueta 1", "ASÍ NO"),
                                            (1280, TEAL, 0.9, NAVY, "v", "Etiqueta 2", "ASÍ SÍ")):
        dl = 3.3 - at
        if kind == "x":
            hit = [(0.75, {"dx": -16}, "smooth"), (0.85, {"dx": 14}, "smooth"), (0.95, {"dx": -9}, "smooth"),
                   (1.05, {"dx": 5}, "smooth"), (1.15, {}, "hold")]
        else:
            hit = [(0.7, {"dy": -22}, "out"), (0.85, {}, "smooth"), (0.95, {"dy": -6}, "smooth"), (1.05, {}, "hold")]
        m = [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (0.6, {}, "smooth")] + hit + \
            [(dl - 0.3, {}, "in"), (dl, {"s": 0.0})]
        t.solid(t.track("shape", "Insignia"), c, at, dl, centered(x, 460, 280, 280), m, kind="ellipse",
                layers=[shadow("#000000", 0, 12, 30, 0.4), fill(c), no_stroke()])
        if kind == "x":
            path(t, t.track("shape", "Marca"), ink, at, dl, centered(x, 460, 110, 110), CROSS_A, 20, motion=m,
                 draw=(0.4, 0.18))
            path(t, t.track("shape", "Marca"), ink, at, dl, centered(x, 460, 110, 110), CROSS_B, 20, motion=m,
                 draw=(0.55, 0.18))
        else:
            path(t, t.track("shape", "Marca"), ink, at, dl, centered(x, 466, 130, 110), CHECK, 20, motion=m,
                 draw=(0.35, 0.32))
        ring_draw(t, t.track("shape", "Onda"), c, 6, at + 0.7, 0.7, centered(x, 460, 280, 280),
                  motion=[(0, {}, "out"), (0.7, {"s": 1.6})], opacity=keys([(0, 0.9), (0.7, 0.0)]))
        label(t, t.track("text", "Etiqueta"), text, at + 0.3, dl - 0.35, Box(x - 250, 640, 500, 84), "Sora", 60, WHITE,
              weight=800, spacing=4, anim_in=tanim("rise", duration=0.4), anim_out=OUT(0.25), name=nm)
    return t


def elemento_pasos():
    t = _kit("elemento-pasos", "Pasos con progreso", "Progress steps", "elementos", 4.0, 8111,
             ["elementos", "pasos", "progreso", "tutorial", "lista"], thumb_at=2.3, background=DEEP)
    bg(t, DEEP)
    xs, y, arrive = [330, 750, 1170, 1590], 460, [0.5, 1.2, 1.9, 2.6]
    end = 3.75
    t.solid(t.track("shape", "Pista"), WHITE, 0.1, end - 0.1, Box(330, y - 6, 1260, 12),
            [(0, {"sx": 0.0, "dx": -630}, "out"), (0.45, {}, "hold"), (end - 0.45, {}, "in"), (end - 0.1, {"sx": 0.0})],
            alpha=0.2)
    m, rel = [], lambda a: a - arrive[0]
    for k in range(4):
        p = k / 3
        st = {"sx": max(p, 0.001), "dx": -(1 - p) * 630}
        m.append((rel(arrive[k]), st, "hold"))
        if k < 3:
            m.append((rel(arrive[k]) + 0.12, st, "inout"))
    dl = end - arrive[0] - 0.05
    m += [(dl - 0.35, {}, "in"), (dl, {"sx": 0.0, "dx": 630})]
    t.solid(t.track("shape", "Progreso"), TEAL, arrive[0], dl, Box(330, y - 6, 1260, 12), m)
    for i, x in enumerate(xs):
        a = 0.15 + i * 0.08
        dl = end - a
        life = [(0, {"s": 0.0}, "back"), (0.35, {}, "hold"), (dl - 0.3, {}, "in"), (dl, {"s": 0.0})]
        t.solid(t.track("shape", "Paso"), DEEP, a, dl, centered(x, y, 160, 160), life, kind="ellipse",
                layers=[fill(DEEP), _stroke(MIST, 4, "inside", 0.6)])
        label(t, t.track("text", "Número"), str(i + 1), a, dl, centered(x, y, 160, 160), "Sora", 62, MIST, weight=700,
              anim_in=tanim("pop", duration=0.35), anim_out=OUT(0.2), editable=False, name=f"Número {i + 1}")
        b = arrive[i] - 0.05
        dl2 = end - b
        life2 = [(0, {"s": 0.0}, "back"), (0.35, {}, "hold"), (dl2 - 0.3, {}, "in"), (dl2, {"s": 0.0})]
        t.solid(t.track("shape", "Hecho"), TEAL, b, dl2, centered(x, y, 160, 160), life2, kind="ellipse",
                layers=[glow(TEAL, 18, 0.5), fill(TEAL), no_stroke()])
        path(t, t.track("shape", "Visto"), NAVY, b, dl2, centered(x, y + 4, 72, 60), CHECK, 13, motion=life2,
             draw=(0.15, 0.25))
        label(t, t.track("text", "Paso"), ["Idea", "Guion", "Grabar", "Publicar"][i], 0.3 + i * 0.08,
              end - 0.3 - i * 0.08 - 0.1, Box(x - 200, 575, 400, 76), "Inter", 54, WHITE, weight=600,
              anim_in=tanim("fade-up-char", duration=0.4), anim_out=OUT(0.25), name=f"Paso {i + 1}")
    return t


def apertura_anillo_vertical():
    return apertura_anillo(True)


def apertura_paneles_vertical():
    return apertura_paneles(True)


def apertura_collage_vertical():
    return apertura_collage(True)


TEMPLATES = [apertura_anillo, apertura_paneles, apertura_franjas, apertura_destello, apertura_mosaico,
             apertura_decodificar, apertura_tipografica, apertura_collage, apertura_linea, apertura_clara,
             apertura_explosion, apertura_esquinas,
             apertura_anillo_vertical, apertura_paneles_vertical, apertura_collage_vertical,
             elemento_flecha, elemento_circulo, elemento_subrayados, elemento_destellos, elemento_clic,
             elemento_suscribete, elemento_visor, elemento_cargando, elemento_barras, elemento_globos,
             elemento_check_cruz, elemento_pasos]
