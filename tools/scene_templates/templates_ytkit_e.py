"""YouTube kit, batch e (see BRIEF-ytkit.md): Transiciones (shape wipes that hide a cut), Pantallas finales (end
screens with clear zones for YouTube's elements) and Redes (social handles). Same palette, fonts and rules as the
prototypes in templates_ytkit.py. Orders: transiciones 7700-7749, pantallas finales 7900-7949, redes 8000-8049.
"""

from __future__ import annotations

import math

from kit import (Box, bg, bg_gradient, centered, dots, fill, keys, label, line, no_stroke, outline, photo_bg, pill,
                 ring, rrect, shade_bottom, shade_full, shadow, song, tall, tanim, wide)

NAVY = "#0B1A2E"
DEEP = "#06101F"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
MIST = "#A9B8CC"
PAPER = "#F4F7FB"


def _kit(id, es, en, section, duration, order, tags, vertical=False, **kw):
    make = tall if vertical else wide
    extra = ["vertical"] if vertical else []
    return make(f"ytk-{id}", es, en, "ytkit", duration, order=order,
                tags=[f"kit:{section}", "youtube"] + extra + tags, **kw)


def pio(d, inlen=0.4, out=0.3, ease="back"):
    """Pop in, hold, shrink out at the end of a clip of length d."""
    return [(0, {"s": 0.0}, ease), (inlen, {}, "hold"), (d - out, {}, "in"), (d, {"s": 0.0})]


def grow_io(box, d, side="left", inlen=0.45, out=0.35):
    """A bar that grows out of one side and goes back into it before the end."""
    k = {"left": {"sx": 0.0, "dx": -box.w / 2}, "right": {"sx": 0.0, "dx": box.w / 2},
         "top": {"sy": 0.0, "dy": -box.h / 2}, "bottom": {"sy": 0.0, "dy": box.h / 2}, "c": {"sx": 0.0}}[side]
    return [(0, k, "out"), (inlen, {}, "hold"), (d - out, {}, "in"), (d, k)]


# =================================================================================================
# 7 Transiciones
# =================================================================================================

def _scenes(t, a, b, cut, zoom=0.08, b_track=None):
    """Scene 1 until the cut, scene 2 after it (both slots). b_track puts scene 2 on its own track."""
    trk = t.track("video", "Escenas")
    t.photo(trk, a, 0.0, cut, None, [(0, {"s": 1.0}, "linear"), (cut, {"s": 1.0 + zoom})], label="Escena 1")
    rest = t.duration - cut
    host = b_track(t) if b_track else trk
    clip = t.photo(host, b, cut, rest, None, [(0, {"s": 1.0 + zoom}, "out"), (rest, {"s": 1.0})], label="Escena 2")
    return host, clip


def _cover(t, items, cut, L=0.4, st=0.05, gap=0.05, ease_in="inout", ease_out="inout", name="Cortinilla"):
    """Shapes that cover the frame by `cut` and uncover it after. Each item: box, colour, rank (stagger units),
    cover / uncover (motion offsets at the ends), optional lag / ulag (seconds), kind, rotation, layers, geometry."""
    maxd = max(it["rank"] * st + it.get("lag", 0.0) for it in items)
    c0 = cut - L - maxd
    for it in items:
        s = c0 + it["rank"] * st + it.get("lag", 0.0)
        u = cut + gap + it["rank"] * st + it.get("ulag", 0.0)
        motion = [(0, it["cover"], ease_in), (L, {}, "hold"), (u - s, {}, ease_out), (u - s + L, it["uncover"])]
        extra = {}
        if "rotation" in it:
            extra["rotation"] = keys([(0, it["rotation"])])
        clip = t.solid(t.track("shape", it.get("name", name)), it["colour"], s, u + L - s, it["box"], motion,
                       kind=it.get("kind", "rectangle"), layers=it.get("layers"), **extra)
        if it.get("geometry"):
            clip["shapeStyle"].update(it["geometry"])
    return c0


def _with_edge(colour, edge, width=5):
    return [fill(colour), {"id": "stroke", "kind": "stroke", "enabled": True, "width": width,
                           "strokeAlign": "inside", "paint": {"kind": "solid", "color": "#ff" + edge.lstrip("#").lower()},
                           "opacity": 1.0}]


def _iris(t, a, b, cut=1.55):
    """Three discs grow from the centre; the cut hides under the last one; scene 2 opens in a circle."""
    W, H = t.w, t.h
    D = math.hypot(W, H) * 1.04
    t.photo(t.track("video", "Escenas"), a, 0.0, cut, None, [(0, {"s": 1.0}, "in"), (cut, {"s": 1.12})],
            label="Escena 1")
    for i, c in enumerate([TEAL, CORAL, NAVY]):
        s = cut - 0.6 - (2 - i) * 0.1
        t.solid(t.track("shape", "Círculo"), c, s, cut + 0.62 - s, centered(W / 2, H / 2, D, D),
                [(0, {"s": 0.0}, "smooth"), (0.6, {})], kind="ellipse")
    rest = t.duration - cut
    trk = t.track("video", "Escena 2")
    clip = t.photo(trk, b, cut, rest, None, [(0, {"s": 1.0}, "hold"), (0.6, {"s": 1.0}, "linear"), (rest, {"s": 1.05})],
                   label="Escena 2")
    reveal = [(0, 0.0, "out"), (0.6, D)]
    t.mask(trk, clip, "ellipse", w=0.0, h=0.0,
           keyframes={"w": keys([(p[0], p[1] / W) + tuple(p[2:]) for p in reveal]),
                      "h": keys([(p[0], p[1] / H) + tuple(p[2:]) for p in reveal])})
    ring(t, t.track("shape", "Aro"), WHITE, 12, cut, 0.62, centered(W / 2, H / 2, D, D),
         [(0, {"s": 0.0}, "out"), (0.6, {})], opacity=keys([(0, 1.0, "hold"), (0.35, 1.0), (0.62, 0.0)]))


def transicion_iris():
    t = _kit("transicion-iris", "Transición iris", "Iris wipe", "transiciones", 3.0, 7700,
             ["transición", "círculo", "iris", "cambio de escena"], thumb_at=1.3)
    _iris(t, "h-city-02", "h-beach-01")
    return t


def transicion_iris_vertical():
    t = _kit("transicion-iris-vertical", "Transición iris vertical", "Iris wipe (vertical)", "transiciones", 3.0,
             7740, ["transición", "círculo", "iris", "cambio de escena"], vertical=True, thumb_at=1.3)
    _iris(t, "city-01", "beach-02")
    return t


def _blinds(t, n):
    W, H = t.w, t.h
    hh = H / n
    items = []
    for j, c in enumerate([TEAL, NAVY]):
        for i in range(n):
            box = Box(-2, i * hh - 1.5, W + 4, hh + 3)
            items.append(dict(box=box, colour=c, rank=i, lag=j * 0.14, ulag=(1 - j) * 0.14,
                              cover={"sy": 0.0, "dy": -(hh + 3) / 2}, uncover={"sy": 0.0, "dy": (hh + 3) / 2},
                              name="Persiana"))
    return items


def transicion_persianas():
    t = _kit("transicion-persianas", "Transición persianas", "Blinds wipe", "transiciones", 3.0, 7701,
             ["transición", "persianas", "franjas", "cambio de escena"], thumb_at=1.15)
    cut = 1.5
    _scenes(t, "h-food-01", "h-cafe-04", cut)
    _cover(t, _blinds(t, 6), cut, L=0.36, st=0.03)
    return t


def transicion_persianas_vertical():
    t = _kit("transicion-persianas-vertical", "Transición persianas vertical", "Blinds wipe (vertical)",
             "transiciones", 3.0, 7741, ["transición", "persianas", "franjas", "cambio de escena"], vertical=True,
             thumb_at=1.15)
    cut = 1.5
    _scenes(t, "travel-05", "nature-02", cut)
    _cover(t, _blinds(t, 8), cut, L=0.36, st=0.025)
    return t


def transicion_franjas():
    t = _kit("transicion-franjas", "Transición de franjas", "Stripe sweep", "transiciones", 3.0, 7702,
             ["transición", "franjas", "barrido", "cambio de escena"], thumb_at=1.2)
    cut = 1.5
    _scenes(t, "h-nature-01", "h-city-05", cut)
    W, H, n = t.w, t.h, 6
    hh = H / n
    colours = [TEAL, NAVY, CORAL, NAVY, SUN, NAVY]
    items = []
    for i in range(n):
        items.append(dict(box=Box(-2, i * hh - 1.5, W + 4, hh + 3), colour=colours[i], rank=i,
                          cover={"dx": -(W + 4)}, uncover={"dx": W + 4}, name="Franja"))
    _cover(t, items, cut, L=0.42, st=0.06)
    return t


def transicion_ola():
    t = _kit("transicion-ola", "Transición ola de barras", "Bar wave", "transiciones", 3.0, 7703,
             ["transición", "barras", "ola", "cambio de escena"], thumb_at=1.2)
    cut = 1.5
    _scenes(t, "h-travel-02", "h-nature-05", cut)
    W, H, n = t.w, t.h, 8
    bw = W / n
    items = []
    for j, c in enumerate([TEAL, NAVY]):
        for i in range(n):
            rank = i + 1.6 * math.sin(i / (n - 1) * math.pi)  # a wave, not a straight ramp
            items.append(dict(box=Box(i * bw - 1.5, -2, bw + 3, H + 4), colour=c, rank=rank, lag=j * 0.1,
                              ulag=(1 - j) * 0.1, cover={"sy": 0.0, "dy": (H + 4) / 2},
                              uncover={"sy": 0.0, "dy": -(H + 4) / 2}, name="Barra"))
    _cover(t, items, cut, L=0.4, st=0.05, gap=0.0)
    return t


def transicion_hexagonos():
    t = _kit("transicion-hexagonos", "Transición de hexágonos", "Hexagon tiles", "transiciones", 3.0, 7704,
             ["transición", "hexágonos", "panal", "mosaico", "cambio de escena"], thumb_at=1.3)
    cut = 1.55
    _scenes(t, "h-tech-01", "h-studio-01", cut)
    # 14 big tiles (one track each): pointy-top rows cover the band y0 - R/2 .. yN + R/2 edge to edge.
    R = 300.0
    hw = math.sqrt(3) * R
    rows = [120.0, 570.0, 1020.0]
    palette = {(0, 1): NAVY, (0, 3): CORAL, (1, 2): NAVY, (2, 0): CORAL, (2, 3): NAVY}
    items = []
    for r, y in enumerate(rows):
        xs = [k * hw for k in range(5)] if r % 2 == 0 else [hw / 2 + k * hw for k in range(4)]
        for k, x in enumerate(xs):
            c = palette.get((r, k), TEAL)
            rank = (x + y * 0.6) / (t.w + t.h * 0.6) * 7
            # regularPolygonPath inscribes the hexagon in the box's ellipse: a 2R square gives a regular one.
            items.append(dict(box=centered(x, y, 2 * R * 1.02, 2 * R * 1.02), colour=c, rank=rank, kind="hexagon",
                              cover={"s": 0.0}, uncover={"s": 0.0}, layers=_with_edge(c, DEEP, 6),
                              name="Hexágono"))
    _cover(t, items, cut, L=0.4, st=0.06, gap=0.0, ease_in="inout", ease_out="inout")
    return t


def transicion_cortes():
    t = _kit("transicion-cortes", "Transición de cortes diagonales", "Slash wipe", "transiciones", 3.0, 7705,
             ["transición", "diagonal", "cortes", "cambio de escena"], thumb_at=1.25)
    cut = 1.5
    _scenes(t, "h-summer-01", "h-winter-01", cut)
    W, H = t.w, t.h
    angle = -28.0
    a = math.radians(angle)
    n = (-math.sin(a), math.cos(a))  # perpendicular to the bars (screen y down, rotation clockwise)
    colours = [TEAL, CORAL, NAVY, TEAL, SUN, NAVY]
    items = []
    k = len(colours)
    for i, c in enumerate(colours):
        off = (i - (k - 1) / 2) * 380
        cx, cy = W / 2 + n[0] * off, H / 2 + n[1] * off
        items.append(dict(box=centered(cx, cy, 3200, 430), colour=c, rank=[2, 0, 3, 1, 4, 2][i], rotation=angle,
                          cover={"sy": 0.0}, uncover={"sy": 0.0}, name="Corte"))
    _cover(t, items, cut, L=0.42, st=0.06)
    # A white slash leads the way across the frame.
    t.solid(t.track("shape", "Destello"), WHITE, cut - 0.75, 0.6, centered(W / 2, H / 2, 3200, 14),
            [(0, {"sx": 0.0}, "out"), (0.45, {}, "linear"), (0.6, {"sy": 0.0})], rotation=keys([(0, angle)]))
    return t


def transicion_puertas():
    t = _kit("transicion-puertas", "Transición de puertas", "Split doors", "transiciones", 3.0, 7706,
             ["transición", "puertas", "cierre", "cambio de escena"], thumb_at=1.6)
    cut = 1.5
    _scenes(t, "h-house-01", "h-interior-01", cut)
    W, H = t.w, t.h
    items = []
    for j, (c, edge) in enumerate([(TEAL, None), (NAVY, CORAL)]):
        for side in (-1, 1):
            box = Box(0 if side < 0 else W / 2 - 2, 0, W / 2 + 2, H)
            items.append(dict(box=box, colour=c, rank=0, lag=j * 0.1, ulag=(1 - j) * 0.1,
                              cover={"dx": side * (W / 2 + 2)}, uncover={"dx": side * (W / 2 + 2)}, name="Puerta"))
            if edge:
                ex = W / 2 - 10 if side < 0 else W / 2
                items.append(dict(box=Box(ex, 0, 10, H), colour=edge, rank=0, lag=j * 0.1, ulag=(1 - j) * 0.1,
                                  cover={"dx": side * (W / 2 + 12)}, uncover={"dx": side * (W / 2 + 12)},
                                  name="Borde"))
    _cover(t, items, cut, L=0.45, gap=0.12)
    # A ring closes on the seam while the doors are shut.
    ring(t, t.track("shape", "Aro"), WHITE, 10, cut - 0.15, 0.45, centered(W / 2, H / 2, 220, 220),
         [(0, {"s": 0.0}, "back"), (0.25, {}, "in"), (0.45, {"s": 0.0})])
    return t


def transicion_aro_zoom():
    t = _kit("transicion-aro-zoom", "Transición zoom con aros", "Ring zoom", "transiciones", 3.0, 7707,
             ["transición", "zoom", "aros", "cambio de escena"], thumb_at=1.35)
    W, H = t.w, t.h
    cut = 1.5
    D = math.hypot(W, H) * 1.04
    trk = t.track("video", "Escenas")
    t.photo(trk, "h-concert-01", 0.0, cut, None, [(0, {"s": 1.0}, "hold"), (0.5, {"s": 1.0}, "in"), (cut, {"s": 1.4})],
            label="Escena 1")
    rest = t.duration - cut
    t.photo(trk, "h-concert-03", cut, rest, None, [(0, {"s": 1.4}, "out"), (0.9, {"s": 1.0}, "linear"),
                                                   (rest, {"s": 1.03})], label="Escena 2")
    for i, c in enumerate([WHITE, TEAL, CORAL]):
        ring(t, t.track("shape", "Aro"), c, 14, 0.55 + i * 0.1, 0.7, centered(W / 2, H / 2, 200, 200),
             [(0, {"s": 0.3}, "out"), (0.7, {"s": 8.0})], opacity=keys([(0, 1.0, "hold"), (0.4, 1.0), (0.7, 0.0)]))
    t.solid(t.track("shape", "Círculo"), TEAL, cut - 0.5, 1.05, centered(W / 2, H / 2, D, D),
            [(0, {"s": 0.0}, "in"), (0.5, {}, "inout"), (1.05, {"s": 0.0})], kind="ellipse")
    ring(t, t.track("shape", "Aro"), WHITE, 10, cut + 0.5, 0.6, centered(W / 2, H / 2, 160, 160),
         [(0, {"s": 0.2}, "out"), (0.6, {"s": 3.0})], opacity=keys([(0, 1.0), (0.6, 0.0)]))
    return t


def transicion_puntos():
    t = _kit("transicion-puntos", "Transición de puntos", "Dot fill", "transiciones", 3.0, 7708,
             ["transición", "puntos", "círculos", "cambio de escena"], thumb_at=1.25)
    cut = 1.55
    _scenes(t, "h-spring-01", "h-autumn-01", cut)
    # 15 big dots (one track each): a circle of radius >= the half diagonal covers its 384x360 cell.
    cw, chh = t.w / 5, t.h / 3
    d = math.hypot(cw, chh) * 1.04
    items = []
    for r in range(3):
        for c in range(5):
            items.append(dict(box=centered(cw / 2 + c * cw, chh / 2 + r * chh, d, d),
                              colour=CORAL if (c + r) % 3 == 1 else SUN, rank=c + r, kind="ellipse",
                              cover={"s": 0.0}, uncover={"s": 0.0}, name="Punto"))
    _cover(t, items, cut, L=0.34, st=0.07, gap=0.0, ease_in="back", ease_out="inout")
    return t


def transicion_destello():
    t = _kit("transicion-destello", "Transición destello de color", "Colour flash", "transiciones", 2.5, 7709,
             ["transición", "destello", "flash", "luz", "cambio de escena"], thumb_at=1.08)
    W, H = t.w, t.h
    cut = 1.2
    trk = t.track("video", "Escenas")
    t.photo(trk, "h-beach-03", 0.0, cut, None, [(0, {"s": 1.0}, "hold"), (0.5, {"s": 1.0}, "in"), (cut, {"s": 1.25})],
            label="Escena 1")
    rest = t.duration - cut
    t.photo(trk, "h-summer-03", cut, rest, None, [(0, {"s": 1.25}, "out"), (0.8, {"s": 1.0}, "linear"),
                                                  (rest, {"s": 1.03})], label="Escena 2")
    # Light streaks sweep across, then the frame burns to sun and white and settles on the new scene.
    for i, (c, w) in enumerate([(SUN, 260), (WHITE, 90), (CORAL, 140)]):
        t.solid(t.track("shape", "Luz"), c, 0.55 + i * 0.07, 0.55, centered(W / 2, H / 2, w, H * 2.2),
                [(0, {"dx": -W}, "inout"), (0.55, {"dx": W})], rotation=keys([(0, 18)]),
                opacity=keys([(0, 0.85)]))
    t.solid(t.track("shape", "Destello"), SUN, cut - 0.3, 0.75,
            opacity=keys([(0, 0.0, "in"), (0.3, 1.0, "out"), (0.75, 0.0)]))
    t.solid(t.track("shape", "Destello"), WHITE, cut - 0.12, 0.5,
            opacity=keys([(0, 0.0, "in"), (0.12, 1.0, "hold"), (0.16, 1.0, "out"), (0.5, 0.0)]))
    return t


def transicion_esquinas():
    t = _kit("transicion-esquinas", "Transición de esquinas", "Corner wipe", "transiciones", 3.0, 7710,
             ["transición", "diagonal", "esquinas", "triángulos", "cambio de escena"], thumb_at=1.3)
    cut = 1.5
    _scenes(t, "h-office-01", "h-desk-02", cut)
    W, H = t.w, t.h
    items = []
    for j, c in enumerate([CORAL, NAVY]):
        box = Box(-3, -3, W + 6, H + 6)
        # Lower-left half comes from the bottom-left corner, the upper-right half (turned 180°) from the other one.
        items.append(dict(box=box, colour=c, rank=0, lag=j * 0.1, ulag=(1 - j) * 0.1, kind="right-triangle",
                          cover={"dx": -W, "dy": H}, uncover={"dx": -W, "dy": H}, name="Esquina"))
        items.append(dict(box=Box(-3, -3, W + 6, H + 6), colour=c if j else TEAL, rank=0, lag=j * 0.1,
                          ulag=(1 - j) * 0.1, kind="right-triangle", rotation=180.0,
                          cover={"dx": W, "dy": -H}, uncover={"dx": W, "dy": -H}, name="Esquina"))
    _cover(t, items, cut, L=0.48)
    # A white seam flashes along the diagonal where the halves meet.
    ang = math.degrees(math.atan2(H, W))
    t.solid(t.track("shape", "Destello"), WHITE, cut - 0.1, 0.3, centered(W / 2, H / 2, math.hypot(W, H) + 40, 10),
            [(0, {"sx": 0.0}, "out"), (0.18, {}, "in"), (0.3, {"sy": 0.0})], rotation=keys([(0, ang)]))
    return t


def transicion_chevrones():
    t = _kit("transicion-chevrones", "Transición de chevrones", "Chevron sweep", "transiciones", 3.0, 7711,
             ["transición", "flechas", "chevrón", "barrido", "cambio de escena"], thumb_at=1.25)
    cut = 1.5
    _scenes(t, "h-travel-07", "h-city-06", cut)
    W, H = t.w, t.h
    bw, bh = 3200.0, 1300.0
    box = Box(-600, (H - bh) / 2, bw, bh)
    items = []
    for j, c in enumerate([TEAL, CORAL, NAVY]):
        items.append(dict(box=box, colour=c, rank=0, lag=j * 0.12, ulag=(2 - j) * 0.12, kind="chevron",
                          geometry={"headSize": 0.18}, cover={"dx": -2600}, uncover={"dx": W + 640},
                          name="Chevrón"))
    _cover(t, items, cut, L=0.5, gap=0.0)
    return t


# =================================================================================================
# 9 Pantallas finales
# =================================================================================================

def _frame(t, sample, box, t0, end, border=TEAL, label_="Video 1", delay=0.0, dx=-80, radius=16, pad=8):
    dur = end - t0
    m = [(0, {"dx": dx, "s": 0.96}, "out"), (0.55, {})]
    rrect(t, t.track("shape", "Marco"), border, t0, dur, Box(box.x - pad, box.y - pad, box.w + 2 * pad, box.h + 2 * pad),
          radius=radius, motion=m, layers=[shadow("#000000", 0, 14, 36, 0.35), fill(border), no_stroke()])
    t.photo(t.track("video", "Video"), sample, t0, dur, box, m, label=label_)


def _hollow_frame(t, box, t0, end, colour=WHITE, glyph=MIST):
    """An empty zone for YouTube's video element: thin frame and a play mark."""
    dur = end - t0
    outline(t, t.track("shape", "Marco"), colour, 4, t0, dur, box, [(0, {"s": 0.94}, "out"), (0.5, {})], alpha=0.9,
            opacity=keys([(0, 0.0), (0.4, 1.0)]))
    t.solid(t.track("shape", "Zona"), WHITE, t0, dur, Box(box.x + 4, box.y + 4, box.w - 8, box.h - 8), alpha=0.04)
    t.solid(t.track("shape", "Play"), glyph, t0 + 0.3, dur - 0.3, centered(box.cx + 6, box.cy, 70, 60),
            [(0, {"s": 0.0}, "back"), (0.4, {})], kind="triangle", rotation=keys([(0, 90)]), alpha=0.8)


def _caption(t, text, box, t0, end, back, ink, name, size=26, delay=0.0):
    dur = end - t0
    pill(t, t.track("shape", "Rótulo"), back, t0, dur, box, [(0, {"sx": 0.0, "dx": -box.w / 2}, "out"), (0.4, {})])
    label(t, t.track("text", "Rótulo"), text, t0 + 0.15, dur - 0.15, box, "Inter", size, ink, weight=800, spacing=3,
          anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15), name=name)


def _subscribe(t, cx, cy, d, t0, end, ring_c=TEAL, logo="logo-07", waves=True):
    """The circle where YouTube's subscribe element goes: a ring with the logo and soft waves around it."""
    dur = end - t0
    ring(t, t.track("shape", "Aro"), ring_c, 10, t0, dur, centered(cx, cy, d, d), [(0, {"s": 0.0}, "back"), (0.5, {})])
    t.photo(t.track("video", "Logo"), logo, t0 + 0.1, dur - 0.1, centered(cx, cy, d * 0.6, d * 0.6),
            [(0, {"s": 0.0}, "back"), (0.5, {})], label="Tu logo")
    if waves:
        trk = t.track("shape", "Onda")
        at = t0 + 1.0
        while at + 1.4 <= end:
            ring(t, trk, ring_c, 4, at, 1.4, centered(cx, cy, d, d), [(0, {"s": 1.0}, "out"), (1.4, {"s": 1.35})],
                 opacity=keys([(0, 0.7), (1.4, 0.0)]))
            at += 2.2


def _button(t, text, box, t0, end, back=CORAL, ink=WHITE, size=34, pulse=True):
    dur = end - t0
    pill(t, t.track("shape", "Botón"), back, t0, dur, box, [(0, {"s": 0.0}, "back"), (0.4, {})],
         layers=[shadow("#000000", 0, 8, 20, 0.3), fill(back), no_stroke()])
    label(t, t.track("text", "Botón"), text, t0 + 0.1, dur - 0.1, box, "Sora", size, ink, weight=800, spacing=4,
          anim_loop=tanim("pulse") if pulse else None, name="Botón")


def _title_from_bar(t, text, x, y, w, h, t0, end, font="Sora", size=64, colour=WHITE, bar=TEAL, name="Título",
                    spacing=3, weight=800):
    dur = end - t0
    line(t, t.track("shape", "Barra"), bar, t0, dur, Box(x, y + 6, 10, h - 12), grow="y", length=0.35)
    label(t, t.track("text", "Título"), text, t0 + 0.2, dur - 0.2, Box(x + 34, y, w, h), font, size, colour,
          weight=weight, align="left", spacing=spacing, anim_in=tanim("wipe", duration=0.6, angle=0, softness=0.15),
          name=name)


def pantalla_un_video():
    T = 15.0
    t = _kit("pantalla-final-un-video", "Pantalla final con un video", "One-video end screen", "pantallas-finales",
             T, 7900, ["pantalla final", "suscríbete", "cierre", "siguiente video"], thumb_at=3.0, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=110)
    dots(t, [TEAL, MIST], 16, 0.0, T, seed=31, size=(4, 10), drift=90, alpha=0.5)
    _title_from_bar(t, "MIRA ESTE VIDEO", 160, 130, 900, 90, 0.3, T, name="Título")
    _frame(t, "h-travel-05", Box(160, 290, 960, 540), 0.5, T, border=TEAL, label_="Video")
    _subscribe(t, 1490, 470, 330, 0.9, T)
    _button(t, "SUSCRÍBETE", Box(1305, 690, 370, 78), 1.3, T)
    label(t, t.track("text", "Lema"), "videos nuevos cada semana", 1.6, T - 1.6, Box(1240, 790, 500, 50), "Inter", 28,
          MIST, weight=500, spacing=1, anim_in=tanim("fade", duration=0.5), name="Lema")
    song(t, "upbeat", 0)
    return t


def pantalla_clara():
    T = 12.0
    t = _kit("pantalla-final-clara", "Pantalla final clara", "Light end screen", "pantallas-finales", T, 7901,
             ["pantalla final", "suscríbete", "cierre", "claro", "blanco"], thumb_at=3.0, background=PAPER)
    bg(t, PAPER)
    dots(t, [TEAL, CORAL, SUN], 14, 0.0, T, seed=5, size=(6, 12), drift=70, alpha=0.6)
    label(t, t.track("text", "Gracias"), "¡GRACIAS POR VER!", 0.3, T - 0.3, Box(260, 70, 1400, 100), "Sora", 70, NAVY,
          weight=800, spacing=4, anim_in=tanim("rise-by-word", duration=0.7), name="Gracias")
    _subscribe(t, 960, 330, 230, 0.7, T, ring_c=NAVY, logo="logo-01")
    for i, (x, sample, cap, c) in enumerate([(200, "h-food-03", "VIDEO SIGUIENTE", TEAL),
                                             (1080, "h-cooking-01", "TE PUEDE GUSTAR", CORAL)]):
        _caption(t, cap, Box(x, 500, 330, 52), 1.0 + i * 0.2, T, NAVY, WHITE, f"Rótulo {i + 1}")
        _frame(t, sample, Box(x, 580, 640, 360), 0.8 + i * 0.2, T, border=c, label_=f"Video {i + 1}",
               dx=-80 if i == 0 else 80)
    song(t, "fun", 1)
    return t


def pantalla_lista():
    T = 15.0
    t = _kit("pantalla-final-lista", "Pantalla final con lista", "Playlist end screen", "pantallas-finales", T, 7902,
             ["pantalla final", "lista de reproducción", "playlist", "cierre"], thumb_at=3.2, background=DEEP)
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=150)
    dots(t, [TEAL, WHITE], 14, 0.0, T, seed=44, size=(4, 9), drift=70, alpha=0.45)
    # The playlist: two cards fanned behind the frame.
    fx, fy, fw, fh = 180, 300, 880, 495
    for i, (c, off) in enumerate([(CORAL, 52), (SUN, 26)]):
        rrect(t, t.track("shape", "Lista"), c, 0.5 + i * 0.12, T - 0.5 - i * 0.12,
              Box(fx + off - 8, fy - off - 8, fw + 16, fh + 16), radius=16,
              motion=[(0, {"dx": -off, "dy": off}, "out"), (0.6, {})], alpha=0.9 if i else 0.75)
    _frame(t, "h-nature-04", Box(fx, fy, fw, fh), 0.4, T, border=TEAL, label_="Lista", dx=0)
    # «Playlist» tag: three lines and a play mark.
    tag = Box(180, 150, 520, 70)
    pill(t, t.track("shape", "Etiqueta"), TEAL, 0.9, T - 0.9, tag, [(0, {"sx": 0.0, "dx": -tag.w / 2}, "out"), (0.45, {})])
    for k in range(3):
        t.solid(t.track("shape", "Icono"), NAVY, 1.1 + k * 0.05, T - 1.1 - k * 0.05, Box(214, 168 + k * 13, 34 - k * 0, 6),
                [(0, {"sx": 0.0, "dx": -17}, "out"), (0.3, {})])
    t.solid(t.track("shape", "Icono"), NAVY, 1.25, T - 1.25, centered(262, 194, 16, 14), [(0, {"s": 0.0}, "back"), (0.3, {})],
            kind="triangle", rotation=keys([(0, 90)]))
    label(t, t.track("text", "Etiqueta"), "LISTA DE REPRODUCCIÓN", 1.2, T - 1.2, Box(290, 150, 400, 70), "Inter", 26,
          NAVY, weight=800, align="left", spacing=3, anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          name="Etiqueta")
    _subscribe(t, 1500, 460, 320, 1.0, T)
    _button(t, "SUSCRÍBETE", Box(1315, 680, 370, 78), 1.4, T)
    label(t, t.track("text", "Lema"), "maratón de videos aquí", 1.7, T - 1.7, Box(1250, 780, 500, 50), "Inter", 28, MIST,
          weight=500, anim_in=tanim("fade", duration=0.5), name="Lema")
    song(t, "upbeat", 2)
    return t


def pantalla_foto():
    T = 15.0
    t = _kit("pantalla-final-foto", "Pantalla final con foto de fondo", "Photo end screen", "pantallas-finales", T,
             7903, ["pantalla final", "foto", "suscríbete", "cierre"], thumb_at=3.2)
    photo_bg(t, "h-travel-02", s1=1.12, label="Tu foto o video")
    shade_full(t, 0.55)
    t.solid(t.track("shape", "Sombra"), "#000000", 0.0, T, Box(0, 0, 1100, 1080),
            layers=[{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                     "paint": {"kind": "gradient", "color": "#cc06101f", "gradient": {
                         "kind": "linear", "angle": 0.0, "space": "block",
                         "stops": [{"pos": 0, "color": "#cc06101f"}, {"pos": 1, "color": "#0006101f"}]}}}, no_stroke()])
    label(t, t.track("text", "Antetítulo"), "¿QUIERES MÁS?", 0.3, T - 0.3, Box(160, 140, 800, 60), "Inter", 34, TEAL,
          weight=800, align="left", spacing=10, anim_in=tanim("tracking-drift", duration=1.0), name="Antetítulo")
    label(t, t.track("text", "Título"), "SIGUE\nVIENDO", 0.5, T - 0.5, Box(160, 240, 800, 320), "Anton", 140, WHITE,
          weight=400, align="left", line=0.95, spacing=4, anim_in=tanim("rise-by-word", duration=0.8), name="Título")
    _subscribe(t, 330, 740, 280, 1.0, T)
    _button(t, "SUSCRÍBETE", Box(520, 702, 360, 76), 1.4, T)
    for i, (y, sample) in enumerate([(130, "h-summer-02"), (560, "h-nature-02")]):
        _frame(t, sample, Box(1120, y, 640, 360), 0.7 + i * 0.2, T, border=WHITE, label_=f"Video {i + 1}", dx=80,
               radius=12, pad=6)
    song(t, "cine", 1)
    return t


def pantalla_coral():
    T = 12.0
    t = _kit("pantalla-final-coral", "Pantalla final coral", "Coral end screen", "pantallas-finales", T, 7904,
             ["pantalla final", "coral", "suscríbete", "cierre"], thumb_at=3.0, background=CORAL)
    bg_gradient(t, [(0, "#FF6F83"), (1, "#E8455C")], angle=120)
    # Slow diagonal stripes in the back keep it alive.
    for i in range(4):
        t.solid(t.track("shape", "Franja"), WHITE, 0.0, T, centered(300 + i * 480, 540, 120, 2200),
                [(0, {"dx": -120}, "linear"), (T, {"dx": 240})], rotation=keys([(0, 24)]), alpha=0.06)
    label(t, t.track("text", "Título"), "SIGUE VIENDO", 0.3, T - 0.3, Box(260, 90, 1400, 140), "Anton", 120, WHITE,
          weight=400, spacing=8, anim_in=tanim("stamp", duration=0.4), name="Título")
    for i, (x, sample) in enumerate([(200, "h-city-04"), (1080, "h-travel-03")]):
        _frame(t, sample, Box(x, 290, 640, 360), 0.6 + i * 0.2, T, border=NAVY, label_=f"Video {i + 1}",
               dx=-80 if i == 0 else 80)
    _subscribe(t, 960, 850, 210, 1.0, T, ring_c=WHITE)
    _button(t, "SUSCRÍBETE", Box(420, 812, 360, 76), 1.4, T, back=NAVY)
    label(t, t.track("text", "Lema"), "y activa la campanita", 1.6, T - 1.6, Box(1140, 812, 500, 76), "Sora", 34,
          WHITE, weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Lema")
    song(t, "fun", 0)
    return t


def pantalla_centro():
    T = 12.0
    t = _kit("pantalla-final-centro", "Pantalla final centrada", "Centred end screen", "pantallas-finales", T, 7905,
             ["pantalla final", "suscríbete", "cierre", "simétrica"], thumb_at=3.0, background=NAVY)
    bg_gradient(t, [(0, "#0F2547"), (1, DEEP)], angle=90)
    dots(t, [TEAL, SUN, MIST], 18, 0.0, T, seed=12, size=(4, 10), drift=80, alpha=0.5)
    label(t, t.track("text", "Antetítulo"), "NOS VEMOS EN EL PRÓXIMO", 0.3, T - 0.3, Box(460, 60, 1000, 60), "Inter", 30,
          MIST, weight=700, spacing=12, anim_in=tanim("tracking-drift", duration=1.0), name="Antetítulo")
    _subscribe(t, 960, 320, 300, 0.6, T)
    for i, (x, sample, c) in enumerate([(120, "h-sport-01", TEAL), (1160, "h-beach-04", CORAL)]):
        _frame(t, sample, Box(x, 580, 640, 360), 0.8 + i * 0.15, T, border=c, label_=f"Video {i + 1}",
               dx=-80 if i == 0 else 80)
    label(t, t.track("text", "Gracias"), "¡Gracias\npor ver!", 1.2, T - 1.2, Box(780, 610, 360, 200), "Sora", 54, WHITE,
          weight=800, line=1.1, anim_in=tanim("rise-by-word", duration=0.7), name="Gracias")
    _button(t, "SUSCRÍBETE", Box(790, 840, 340, 70), 1.6, T, size=30)
    song(t, "upbeat", 4)
    return t


def pantalla_minimal():
    T = 15.0
    t = _kit("pantalla-final-minimal", "Pantalla final minimalista", "Minimal end screen", "pantallas-finales", T,
             7906, ["pantalla final", "minimalista", "líneas", "cierre"], thumb_at=3.0, background=DEEP)
    bg(t, DEEP)
    line(t, t.track("shape", "Línea"), WHITE, 0.2, T - 0.2, Box(160, 150, 1600, 2), grow="c", length=0.8, alpha=0.4)
    line(t, t.track("shape", "Línea"), WHITE, 0.3, T - 0.3, Box(160, 930, 1600, 2), grow="c", length=0.8, alpha=0.4)
    label(t, t.track("text", "Título"), "GRACIAS POR VER", 0.6, T - 0.6, Box(160, 70, 900, 70), "Sora", 40, WHITE,
          weight=700, align="left", spacing=14, anim_in=tanim("wipe", duration=0.7, angle=0, softness=0.15),
          name="Título")
    label(t, t.track("text", "Canal"), "@tucanal", 0.8, T - 0.8, Box(1060, 70, 700, 70), "Sora", 34, TEAL, weight=600,
          align="right", anim_in=tanim("wipe", duration=0.7, angle=180, softness=0.15), name="Canal")
    for i, (x, cap) in enumerate([(160, "SIGUIENTE"), (840, "RECOMENDADO")]):
        label(t, t.track("text", "Rótulo"), cap, 0.9 + i * 0.15, T - 0.9 - i * 0.15, Box(x, 345, 600, 44), "Inter", 24,
              MIST, weight=700, align="left", spacing=8, anim_in=tanim("fade", duration=0.5), name=f"Rótulo {i + 1}")
        _hollow_frame(t, Box(x, 400, 640, 360), 0.8 + i * 0.15, T)
    cx, cy = 1645, 580
    ring(t, t.track("shape", "Aro"), WHITE, 4, 1.1, T - 1.1, centered(cx, cy, 210, 210), [(0, {"s": 0.0}, "back"), (0.5, {})])
    plus = t.solid(t.track("shape", "Cruz"), TEAL, 1.3, T - 1.3, centered(cx, cy, 64, 64),
                   [(0, {"s": 0.0}, "back"), (0.4, {})], kind="cross")
    plus["shapeStyle"]["thickness"] = 0.22
    label(t, t.track("text", "Suscríbete"), "suscríbete", 1.5, T - 1.5, Box(cx - 160, cy + 130, 320, 50), "Inter", 28,
          WHITE, weight=600, spacing=6, anim_in=tanim("fade", duration=0.5), name="Suscríbete")
    song(t, "calm", 2)
    return t


def pantalla_sol():
    T = 15.0
    t = _kit("pantalla-final-sol", "Pantalla final amarilla", "Sun end screen", "pantallas-finales", T, 7907,
             ["pantalla final", "amarillo", "like", "suscríbete", "cierre"], thumb_at=3.2, background=SUN)
    bg(t, SUN)
    # A big soft circle drifting behind the title.
    t.solid(t.track("shape", "Círculo"), WHITE, 0.0, T, centered(1500, 360, 900, 900),
            [(0, {"s": 0.95}, "smooth"), (T, {"s": 1.08, "dx": -60})], kind="ellipse", alpha=0.25)
    for i, (y, sample) in enumerate([(130, "h-food-05"), (570, "h-cafe-01")]):
        _frame(t, sample, Box(160, y, 640, 360), 0.5 + i * 0.2, T, border=NAVY, label_=f"Video {i + 1}", radius=12)
    label(t, t.track("text", "Título"), "¿TE GUSTÓ?", 0.3, T - 0.3, Box(960, 160, 860, 170), "Anton", 150, NAVY, weight=400,
          align="left", spacing=4, anim_in=tanim("rise", duration=0.5), name="Título")
    line(t, t.track("shape", "Barra"), CORAL, 0.7, T - 0.7, Box(966, 345, 10, 60), grow="y", length=0.3)
    label(t, t.track("text", "Lema"), "dale like y suscríbete", 0.9, T - 0.9, Box(1000, 345, 820, 60), "Sora", 40, NAVY,
          weight=700, align="left", anim_in=tanim("wipe", duration=0.6, angle=0, softness=0.15), name="Lema")
    _subscribe(t, 1130, 640, 260, 1.1, T, ring_c=NAVY, logo="logo-01")
    _button(t, "SUSCRÍBETE", Box(1310, 602, 360, 76), 1.5, T, back=NAVY)
    song(t, "fun", 3)
    return t


def pantalla_tarjetas():
    T = 15.0
    t = _kit("pantalla-final-tarjetas", "Pantalla final con tres tarjetas", "Three-card end screen",
             "pantallas-finales", T, 7908, ["pantalla final", "tarjetas", "suscríbete", "cierre"], thumb_at=3.0,
             background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=100)
    dots(t, [TEAL, CORAL, MIST], 12, 0.0, T, seed=8, size=(4, 9), drift=80, alpha=0.5)
    label(t, t.track("text", "Gracias"), "¡GRACIAS POR VER!", 0.3, T - 0.3, Box(260, 110, 1400, 110), "Sora", 76, WHITE,
          weight=800, spacing=4, anim_in=tanim("rise-by-word", duration=0.7), name="Gracias")
    cards = [(120, TEAL, "ÚLTIMO VIDEO", "h-office-02"), (700, CORAL, "EL MÁS VISTO", "h-nature-06"),
             (1280, SUN, "SUSCRÍBETE", None)]
    for i, (x, c, cap, sample) in enumerate(cards):
        at = 0.6 + i * 0.15
        card = Box(x, 330, 520, 470)
        rrect(t, t.track("shape", "Tarjeta"), "#14294A", at, T - at, card, radius=22,
              motion=[(0, {"dy": 80, "s": 0.95}, "out"), (0.55, {})],
              layers=[shadow("#000000", 0, 16, 40, 0.4), fill("#14294A"), no_stroke()])
        t.solid(t.track("shape", "Tarjeta"), c, at, T - at, Box(x, 330, 520, 10),
                [(0, {"dy": 80, "sx": 0.0}, "out"), (0.55, {})])
        label(t, t.track("text", "Rótulo"), cap, at + 0.3, T - at - 0.3, Box(x + 30, 360, 460, 50), "Inter", 28, c,
              weight=800, align="left", spacing=4, anim_in=tanim("fade", duration=0.4), name=f"Rótulo {i + 1}")
        if sample:
            t.photo(t.track("video", "Video"), sample, at + 0.1, T - at - 0.1, Box(x + 30, 430, 460, 259),
                    [(0, {"dy": 80, "s": 0.95}, "out"), (0.55, {})], label=f"Video {i + 1}")
            label(t, t.track("text", "Detalle"), "mira este video", at + 0.5, T - at - 0.5, Box(x + 30, 715, 460, 50),
                  "Inter", 26, MIST, weight=500, align="left", anim_in=tanim("fade", duration=0.4),
                  name=f"Detalle {i + 1}")
    _subscribe(t, 1540, 575, 240, 1.1, T, ring_c=SUN)
    label(t, t.track("text", "Detalle"), "contenido nuevo cada semana", 1.5, T - 1.5, Box(1310, 715, 460, 50), "Inter",
          26, MIST, weight=500, anim_in=tanim("fade", duration=0.4), name="Detalle 3")
    song(t, "upbeat", 5)
    return t


def pantalla_gracias():
    T = 20.0
    t = _kit("pantalla-final-gracias", "Pantalla final ¡Gracias!", "Thank-you end screen", "pantallas-finales", T,
             7909, ["pantalla final", "gracias", "redes", "suscríbete", "cierre"], thumb_at=4.0, background=DEEP)
    bg_gradient(t, [(0, "#0E2242"), (1, DEEP)], angle=135)
    dots(t, [TEAL, CORAL, SUN], 20, 0.0, T, seed=77, size=(4, 10), drift=90, alpha=0.5)
    # Opening beat: a big «GRACIAS» on a turquoise wipe, then the layout.
    t.solid(t.track("shape", "Cortinilla"), TEAL, 0.0, 2.2, None,
            [(0, {"dx": -1920}, "out"), (0.4, {}, "hold"), (1.8, {}, "in"), (2.2, {"dx": 1920})])
    label(t, t.track("text", "Gracias grande"), "¡GRACIAS!", 0.3, 1.6, Box(160, 330, 1600, 420), "Anton", 300, NAVY,
          weight=400, spacing=6, anim_in=tanim("stamp", duration=0.35), anim_out=tanim("fade", duration=0.25),
          name="Gracias grande")
    _title_from_bar(t, "GRACIAS POR VER", 160, 110, 1000, 90, 2.1, T, size=60, bar=CORAL, name="Título")
    _frame(t, "h-portrait-02", Box(160, 270, 880, 495), 2.3, T, border=TEAL, label_="Video")
    _subscribe(t, 1450, 430, 300, 2.6, T)
    _button(t, "SUSCRÍBETE", Box(1265, 630, 370, 78), 2.9, T)
    # Handle line with an @ icon.
    t.solid(t.track("shape", "Icono"), CORAL, 3.2, T - 3.2, centered(1290, 830, 72, 72), [(0, {"s": 0.0}, "back"), (0.4, {})],
            kind="ellipse")
    label(t, t.track("text", "Icono"), "@", 3.25, T - 3.25, centered(1290, 830, 72, 72), "Inter", 40, WHITE, weight=900,
          anim_in=tanim("pop", duration=0.35), editable=False, name="Icono")
    label(t, t.track("text", "Usuario"), "@tuusuario", 3.4, T - 3.4, Box(1345, 800, 450, 60), "Sora", 40, WHITE,
          weight=700, align="left", anim_in=tanim("wipe", duration=0.6, angle=0, softness=0.15), name="Usuario")
    song(t, "upbeat", 6)
    return t


# =================================================================================================
# 10 Redes sociales
# =================================================================================================

def _icon(t, glyph, cx, cy, d, colour, ink, t0, dur, out=0.3, name="Icono", rot=0.0):
    """A round icon with a generic glyph: text (@, #, ♪) or a drawn shape (play, heart, star)."""
    t.solid(t.track("shape", name), colour, t0, dur, centered(cx, cy, d, d), pio(dur, 0.4, out), kind="ellipse")
    g0, gd = t0 + 0.08, dur - 0.08
    if glyph == "play":
        t.solid(t.track("shape", name), ink, g0, gd, centered(cx + d * 0.04, cy, d * 0.40, d * 0.36),
                pio(gd, 0.4, out), kind="triangle", rotation=keys([(0, 90 + rot)]))
    elif glyph in ("heart", "star"):
        t.solid(t.track("shape", name), ink, g0, gd, centered(cx, cy + (d * 0.02 if glyph == "heart" else 0),
                                                              d * 0.46, d * 0.42), pio(gd, 0.4, out), kind=glyph,
                rotation=keys([(0, rot)]))
    else:
        label(t, t.track("text", name), glyph, g0, gd - out * 0.5, centered(cx, cy, d, d), "Inter", int(d * 0.55), ink,
              weight=900, anim_in=tanim("pop", duration=0.35), anim_out=tanim("fade", duration=0.2), editable=False,
              name=name, rotation=keys([(0, rot)]))


def _handle(t, text, box, t0, dur, size=52, colour=WHITE, name="Usuario", align="left", font="Sora", weight=700):
    angle = 0 if align == "left" else 180
    label(t, t.track("text", "Usuario"), text, t0, dur, box, font, size, colour, weight=weight, align=align,
          anim_in=tanim("wipe", duration=0.5, angle=angle, softness=0.15), anim_out=tanim("fade", duration=0.25),
          name=name)


def redes_pildoras():
    T = 6.0
    t = _kit("redes-pildoras", "Redes en píldoras", "Social pills", "redes", T, 8000,
             ["redes", "sígueme", "usuario", "píldoras"], thumb_at=2.6)
    photo_bg(t, "h-city-05", s1=1.06, label="Tu video")
    shade_full(t, 0.45)
    label(t, t.track("text", "Título"), "SÍGUEME EN REDES", 0.2, T - 0.6, Box(360, 330, 1200, 100), "Anton", 84, WHITE,
          weight=400, spacing=10, anim_in=tanim("rise", duration=0.5), anim_out=tanim("fade", duration=0.3),
          name="Título")
    rows = [(TEAL, "@", "@tuusuario"), (CORAL, "♪", "@tuusuario"), (SUN, "play", "/tucanal")]
    pw, gap = 500, 40
    x0 = (1920 - (3 * pw + 2 * gap)) / 2
    for i, (c, g, h) in enumerate(rows):
        at = 0.5 + i * 0.12
        dur = T - 0.3 - at - (2 - i) * 0.06
        box = Box(x0 + i * (pw + gap), 490, pw, 100)
        pill(t, t.track("shape", "Píldora"), NAVY, at, dur, box, pio(dur, 0.45, 0.3),
             layers=[shadow("#000000", 0, 10, 24, 0.35), fill(NAVY), no_stroke()])
        _icon(t, g, box.x + 50, box.cy, 76, c, NAVY, at + 0.1, dur - 0.1)
        _handle(t, h, Box(box.x + 104, box.y, pw - 120, 100), at + 0.3, dur - 0.45, size=40,
                name=f"Usuario {i + 1}")
    return t


def _big_handle(t, T, cx, cy, vertical=False):
    W = t.w
    if vertical:
        _icon(t, "@", W / 2, cy - 260, 300, TEAL, NAVY, 0.3, T - 0.6, name="Icono")
        label(t, t.track("text", "Antetítulo"), "SÍGUEME", 0.6, T - 1.0, Box(140, cy - 60, W - 280, 70), "Inter", 40, MIST,
              weight=800, spacing=16, anim_in=tanim("tracking-drift", duration=1.0), anim_out=tanim("fade", duration=0.3),
              name="Antetítulo")
        line(t, t.track("shape", "Línea"), CORAL, 0.8, T - 1.1, Box(W / 2 - 160, cy + 30, 320, 8), grow="c", length=0.4)
        label(t, t.track("text", "Usuario"), "@tuusuario", 1.0, T - 1.3, Box(80, cy + 60, W - 160, 140), "Sora", 104,
              WHITE, weight=800, anim_in=tanim("wipe", duration=0.6, angle=90, softness=0.15),
              anim_out=tanim("fade", duration=0.3), name="Usuario")
        label(t, t.track("text", "Lema"), "contenido nuevo cada semana", 1.4, T - 1.7, Box(80, cy + 210, W - 160, 60),
              "Inter", 38, MIST, weight=500, anim_in=tanim("fade", duration=0.5), anim_out=tanim("fade", duration=0.3),
              name="Lema")
        return
    # One lockup, ~1.5x: icon, coral bar, «SÍGUEME» and a handle about 40 % of the width. All leave together.
    E = T - 0.3
    d = 380
    x0 = 300
    _icon(t, "@", x0 + d / 2, cy, d, TEAL, NAVY, 0.3, E - 0.3, name="Icono")
    bx = x0 + d + 60
    bar = Box(bx, cy - 150, 12, 300)
    t.solid(t.track("shape", "Barra"), CORAL, 0.6, E - 0.6, bar, grow_io(bar, E - 0.6, "top", 0.35, 0.3))
    tx = bx + 50
    label(t, t.track("text", "Antetítulo"), "SÍGUEME", 0.8, E - 0.85, Box(tx, cy - 150, 1840 - tx, 70), "Inter", 48, MIST,
          weight=800, align="left", spacing=18, anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          anim_out=tanim("fade", duration=0.25), name="Antetítulo")
    _handle(t, "@tuusuario", Box(tx, cy - 75, 1840 - tx, 190), 0.9, E - 0.95, size=136, weight=800)


def redes_grande():
    T = 5.0
    t = _kit("redes-grande", "Usuario en grande", "Big handle", "redes", T, 8001,
             ["redes", "sígueme", "usuario", "grande"], thumb_at=2.4, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=120)
    dots(t, [TEAL, MIST], 14, 0.0, T, seed=3, size=(4, 10), drift=60, alpha=0.5)
    _big_handle(t, T, 960, 540)
    return t


def redes_grande_vertical():
    T = 5.0
    t = _kit("redes-grande-vertical", "Usuario en grande vertical", "Big handle (vertical)", "redes", T, 8041,
             ["redes", "sígueme", "usuario", "grande"], vertical=True, thumb_at=2.4, background=NAVY)
    bg_gradient(t, [(0, "#123158"), (1, DEEP)], angle=120)
    dots(t, [TEAL, MIST], 18, 0.0, T, seed=3, size=(5, 12), drift=80, alpha=0.5)
    _big_handle(t, T, 540, 960, vertical=True)
    return t


def redes_cuadricula():
    T = 6.0
    t = _kit("redes-cuadricula", "Redes en cuadrícula", "Social grid", "redes", T, 8002,
             ["redes", "sígueme", "usuario", "cuadrícula"], thumb_at=2.8, background=DEEP)
    bg(t, DEEP)
    dots(t, [TEAL, CORAL, SUN], 6, 0.0, T, seed=19, size=(4, 9), drift=60, alpha=0.5)
    label(t, t.track("text", "Título"), "ENCUÉNTRAME EN", 0.2, T - 0.45, Box(260, 120, 1400, 130), "Anton", 104, WHITE,
          weight=400, spacing=12, anim_in=tanim("rise", duration=0.5), anim_out=tanim("fade", duration=0.3),
          name="Título")
    cells = [(TEAL, "@", "@tuusuario", "fotos y día a día"), (CORAL, "♪", "@tuusuario", "videos cortos"),
             (SUN, "#", "#tuhashtag", "comunidad"), (WHITE, "play", "/tucanal", "videos largos")]
    cw, ch, gx, gy = 840, 280, 40, 40
    x0, y0 = (1920 - (2 * cw + gx)) / 2, 300
    for i, (c, g, h, sub) in enumerate(cells):
        at = 0.5 + i * 0.1
        dur = T - 0.3 - at
        box = Box(x0 + (i % 2) * (cw + gx), y0 + (i // 2) * (ch + gy), cw, ch)
        rrect(t, t.track("shape", "Tarjeta"), "#11233F", at, dur, box, radius=30, motion=pio(dur, 0.45, 0.3, "out"),
              layers=[fill("#11233F"), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 3,
                                        "strokeAlign": "inside", "paint": {"kind": "solid", "color": "#ff1f3a60"},
                                        "opacity": 1.0}])
        _icon(t, g, box.x + 140, box.cy, 170, c, NAVY, at + 0.1, dur - 0.1)
        _handle(t, h, Box(box.x + 260, box.y + 55, cw - 290, 100), at + 0.3, dur - 0.45, size=70,
                name=f"Usuario {i + 1}")
        label(t, t.track("text", "Detalle"), sub, at + 0.4, dur - 0.55, Box(box.x + 262, box.y + 158, cw - 290, 60),
              "Inter", 40, MIST, weight=500, align="left", anim_in=tanim("fade", duration=0.4),
              anim_out=tanim("fade", duration=0.25), name=f"Detalle {i + 1}")
    return t


def redes_tercio():
    T = 5.0
    t = _kit("redes-tercio", "Usuario en tercio inferior", "Lower-third handle", "redes", T, 8003,
             ["redes", "usuario", "tercio inferior", "rótulo"], thumb_at=2.2)
    photo_bg(t, "h-podcast-03", s1=1.05, label="Tu video")
    shade_bottom(t, 380, 0.55)
    sq = Box(120, 790, 130, 130)
    rrect(t, t.track("shape", "Icono"), CORAL, 0.2, T - 0.4, sq, radius=18, motion=pio(T - 0.4, 0.4, 0.3))
    label(t, t.track("text", "Icono"), "@", 0.28, T - 0.6, sq, "Inter", 80, WHITE, weight=900,
          anim_in=tanim("pop", duration=0.35), anim_out=tanim("fade", duration=0.2), editable=False, name="Icono")
    plate = Box(250, 790, 620, 82)
    t.solid(t.track("shape", "Placa"), WHITE, 0.45, T - 0.85, plate, grow_io(plate, T - 0.85, "left", 0.45, 0.35))
    _handle(t, "@tuusuario", Box(280, 790, 580, 82), 0.75, T - 1.3, size=50, colour=NAVY, weight=800)
    sub = Box(250, 872, 420, 48)
    t.solid(t.track("shape", "Placa"), NAVY, 0.6, T - 1.0, sub, grow_io(sub, T - 1.0, "left", 0.45, 0.3))
    label(t, t.track("text", "Lema"), "sígueme para más", 0.9, T - 1.45, Box(280, 872, 390, 48), "Inter", 28, TEAL,
          weight=700, align="left", spacing=2, anim_in=tanim("wipe", duration=0.5, angle=0, softness=0.15),
          anim_out=tanim("fade", duration=0.25), name="Lema")
    return t


def redes_circulos():
    T = 6.0
    t = _kit("redes-circulos", "Iconos en círculos", "Circle icons", "redes", T, 8004,
             ["redes", "iconos", "círculos", "usuario"], thumb_at=2.6, background=DEEP)
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=90)
    dots(t, [TEAL, MIST], 14, 0.0, T, seed=23, size=(4, 9), drift=60, alpha=0.5)
    icons = [(TEAL, "@"), (CORAL, "♪"), (SUN, "#"), (WHITE, "play"), (TEAL, "heart")]
    d, gap = 250, 70
    x0 = (1920 - (len(icons) * d + (len(icons) - 1) * gap)) / 2 + d / 2
    E = T - 0.3
    for i, (c, g) in enumerate(icons):
        at = 0.3 + i * 0.1
        _icon(t, g, x0 + i * (d + gap), 330, d, c, NAVY, at, E - at - (len(icons) - 1 - i) * 0.04)
    line(t, t.track("shape", "Línea"), MIST, 0.9, E - 0.9, Box(660, 535, 600, 4), grow="c", length=0.4,
         opacity=keys([(0, 1.0, "hold"), (E - 1.2, 1.0), (E - 0.9, 0.0)]))
    label(t, t.track("text", "Usuario"), "@tuusuario", 1.0, E - 1.05, Box(160, 560, 1600, 200), "Sora", 150, WHITE,
          weight=800, anim_in=tanim("wipe", duration=0.6, angle=90, softness=0.15), anim_out=tanim("fade", duration=0.3),
          name="Usuario")
    label(t, t.track("text", "Lema"), "en todas mis redes", 1.4, E - 1.45, Box(360, 770, 1200, 80), "Inter", 50, MIST,
          weight=500, spacing=5, anim_in=tanim("fade", duration=0.5), anim_out=tanim("fade", duration=0.3), name="Lema")
    return t


def redes_tarjetas():
    T = 6.0
    t = _kit("redes-tarjetas", "Tarjetas sígueme", "Follow cards", "redes", T, 8005,
             ["redes", "sígueme", "tarjetas", "usuario"], thumb_at=2.8, background=TEAL)
    bg_gradient(t, [(0, "#3FF0D2"), (1, "#16B8A0")], angle=120)
    cards = [(-6, CORAL, "♪", "@tuusuario", "videos cortos"), (0, NAVY, "@", "@tuusuario", "fotos"),
             (6, SUN, "play", "/tucanal", "videos largos")]
    k = 1.17
    cw, ch = 420 * k, 520 * k
    for i, (rot, c, g, h, sub) in enumerate(cards):
        cx = 960 + (i - 1) * 560
        cy = 540 + (14 if i != 1 else -10)
        at = 0.3 + i * 0.12
        dur = T - 0.3 - at
        leave = dur - 0.3  # the card starts to drop; its content fades out as it goes
        a = math.radians(rot)

        def at_card(ox, oy):  # a point of the card, turned with it (clockwise, screen y down)
            ox, oy = ox * k, oy * k
            return cx + ox * math.cos(a) - oy * math.sin(a), cy + ox * math.sin(a) + oy * math.cos(a)

        m = [(0, {"dy": 800}, "out"), (0.6, {}, "hold"), (leave, {}, "in"), (dur, {"dy": 800})]
        rrect(t, t.track("shape", "Tarjeta"), WHITE, at, dur, centered(cx, cy, cw, ch), radius=32, motion=m,
              layers=[shadow("#000000", 0, 20, 40, 0.3), fill(WHITE), no_stroke()],
              rotation=keys([(0, rot * 3, "out"), (0.6, rot)]))
        rk = keys([(0, rot)])
        x, y = at_card(0, -120)
        _icon(t, g, x, y, 150 * k, c, WHITE if c == NAVY else NAVY, at + 0.55, leave - 0.4, out=0.25, rot=rot)
        x, y = at_card(0, 45)
        label(t, t.track("text", "Usuario"), h, at + 0.65, leave - 0.5, centered(x, y, 360 * k, 80), "Sora", 52, NAVY,
              weight=800, anim_in=tanim("fade-up-char", duration=0.5), anim_out=tanim("fade", duration=0.2),
              name=f"Usuario {i + 1}", rotation=rk)
        x, y = at_card(0, 105)
        label(t, t.track("text", "Detalle"), sub, at + 0.75, leave - 0.6, centered(x, y, 360 * k, 56), "Inter", 33,
              "#5A6B82", weight=500, anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.2),
              name=f"Detalle {i + 1}", rotation=rk)
        x, y = at_card(0, 185)
        btn = centered(x, y, 240 * k, 64 * k)
        bd = leave - 0.65
        pill(t, t.track("shape", "Botón"), c if c != SUN else CORAL, at + 0.8, bd, btn, pio(bd, 0.4, 0.2), rotation=rk)
        label(t, t.track("text", "Botón"), "SÍGUEME", at + 0.9, bd - 0.15, btn, "Inter", 30, WHITE, weight=800,
              spacing=4, anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.15),
              name=f"Botón {i + 1}", rotation=rk)
    return t


def redes_clara():
    T = 6.0
    t = _kit("redes-clara", "Tus redes, versión clara", "Social handles (light)", "redes", T, 8006,
             ["redes", "sígueme", "usuario", "claro", "blanco"], thumb_at=2.8, background=PAPER)
    bg(t, PAPER)
    # Your photo in a ring on the right.
    cx, cy, d = 1450, 540, 580
    ring(t, t.track("shape", "Aro"), TEAL, 16, 0.2, T - 0.5, centered(cx, cy, d + 64, d + 64), pio(T - 0.5, 0.5, 0.3))
    from kit import circle_photo
    circle_photo(t, "h-portrait-01", 0.3, T - 0.6, centered(cx, cy, d, d), pio(T - 0.6, 0.5, 0.3), label="Tu foto")
    t.solid(t.track("shape", "Adorno"), CORAL, 0.6, T - 0.9, centered(cx + 235, cy - 235, 80, 80),
            pio(T - 0.9, 0.4, 0.25), kind="ellipse")
    _title_from_bar(t, "SÍGUEME", 130, 170, 900, 150, 0.2, T - 0.4, font="Anton", size=136, colour=NAVY, bar=CORAL,
                    spacing=12, weight=400)
    rows = [(TEAL, "@", "@tuusuario"), (CORAL, "♪", "@tuusuario"), (SUN, "#", "#tuhashtag")]
    for i, (c, g, h) in enumerate(rows):
        at, y = 0.6 + i * 0.15, 380 + i * 180
        dur = T - 0.4 - at
        _icon(t, g, 210, y + 65, 134, c, NAVY, at, dur)
        _handle(t, h, Box(310, y + 15, 780, 100), at + 0.2, dur - 0.3, size=76, colour=NAVY,
                name=f"Usuario {i + 1}")
    return t


def redes_esquina():
    T = 5.0
    t = _kit("redes-esquina", "Usuario en la esquina", "Corner handle", "redes", T, 8007,
             ["redes", "usuario", "esquina", "notificación"], thumb_at=2.0)
    photo_bg(t, "h-beach-05", s1=1.05, label="Tu video")
    cx, cy, d = 1740, 140, 116
    plate = Box(cx - 560, cy - 50, 560, 100)
    pill(t, t.track("shape", "Placa"), NAVY, 0.5, T - 0.9, plate, grow_io(plate, T - 0.9, "right", 0.45, 0.35),
         layers=[shadow("#000000", 0, 10, 24, 0.35), fill(NAVY), no_stroke()])
    _icon(t, "@", cx, cy, d, TEAL, NAVY, 0.2, T - 0.55)
    _handle(t, "@tuusuario", Box(cx - 520, cy - 50, 440, 100), 0.8, T - 1.25, size=44, align="right")
    tag = Box(cx - 330, cy + 66, 270, 52)
    pill(t, t.track("shape", "Etiqueta"), CORAL, 1.0, T - 1.6, tag, grow_io(tag, T - 1.6, "right", 0.4, 0.3))
    label(t, t.track("text", "Etiqueta"), "SÍGUEME", 1.2, T - 1.95, tag, "Inter", 27, WHITE, weight=800, spacing=4,
          anim_in=tanim("fade", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Etiqueta")
    return t


def redes_barra():
    T = 6.0
    t = _kit("redes-barra", "Barra de redes", "Social bar", "redes", T, 8008,
             ["redes", "barra", "usuario", "rótulo"], thumb_at=2.6)
    photo_bg(t, "h-cafe-01", s1=1.05, label="Tu video")
    shade_bottom(t, 360, 0.55)
    E = T - 0.4
    bar = Box(0, 850, 1920, 150)
    t.solid(t.track("shape", "Barra"), NAVY, 0.2, E - 0.2, bar, [(0, {"dy": 240}, "out"), (0.45, {}, "hold"),
                                                                 (E - 0.55, {}, "in"), (E - 0.2, {"dy": 240})],
            alpha=0.94)
    line(t, t.track("shape", "Acento"), TEAL, 0.5, E - 0.85, Box(0, 845, 1920, 5), grow="x", length=0.6,
         opacity=keys([(0, 1.0, "hold"), (E - 1.15, 1.0), (E - 0.85, 0.0)]))
    items = [(TEAL, "@", "@tuusuario"), (CORAL, "♪", "@tuusuario"), (SUN, "play", "/tucanal")]
    seg = 1920 / 3
    for i, (c, g, h) in enumerate(items):
        at = 0.6 + i * 0.12
        dur = E - 0.15 - at
        x = i * seg
        _icon(t, g, x + 150, 925, 100, c, NAVY, at, dur, out=0.25)
        _handle(t, h, Box(x + 222, 875, seg - 250, 100), at + 0.2, dur - 0.22, size=56, name=f"Usuario {i + 1}")
        if i:
            div = Box(x, 885, 3, 80)
            t.solid(t.track("shape", "Divisor"), MIST, at, dur, div, grow_io(div, dur, "top", 0.3, 0.2), alpha=0.5)
    return t


def redes_coral():
    T = 5.0
    t = _kit("redes-coral", "Sígueme en coral", "Coral follow", "redes", T, 8009,
             ["redes", "sígueme", "cinético", "usuario"], thumb_at=2.6, background=CORAL)
    bg_gradient(t, [(0, "#FF6F83"), (1, "#E8455C")], angle=120)
    E = T - 0.3
    label(t, t.track("text", "Título"), "SÍGUEME", 0.2, E - 0.2, Box(160, 200, 1600, 330), "Anton", 280, WHITE,
          weight=400, spacing=10, anim_in=tanim("stamp", duration=0.35), anim_out=tanim("fade", duration=0.3),
          name="Título")
    box = centered(960, 650, 760, 130)
    pill(t, t.track("shape", "Píldora"), NAVY, 0.7, E - 0.7, box, pio(E - 0.7, 0.45, 0.3),
         layers=[shadow("#000000", 0, 12, 28, 0.3), fill(NAVY), no_stroke()])
    _icon(t, "@", box.x + 66, box.cy, 100, SUN, NAVY, 0.8, E - 0.8)
    _handle(t, "@tuusuario", Box(box.x + 136, box.y, box.w - 170, box.h), 1.0, E - 1.15, size=66, weight=800)
    for i, (g, x, y, c) in enumerate([("♪", 330, 790, NAVY), ("#", 1590, 790, SUN), ("heart", 1650, 220, NAVY),
                                       ("play", 270, 220, SUN)]):
        at = 1.0 + i * 0.1
        _icon(t, g, x, y, 120, c, CORAL if c == NAVY else NAVY, at, E - at)
    return t


def redes_lista_vertical():
    T = 6.0
    t = _kit("redes-lista-vertical", "Tus redes vertical", "Social handles (vertical)", "redes", T, 8040,
             ["redes", "sígueme", "usuario", "lista"], vertical=True, thumb_at=2.8, background=DEEP)
    bg_gradient(t, [(0, NAVY), (1, DEEP)], angle=90)
    dots(t, [TEAL, CORAL, MIST], 12, 0.0, T, seed=41, size=(5, 12), drift=80, alpha=0.5)
    label(t, t.track("text", "Título"), "SÍGUEME", 0.2, T - 0.6, Box(90, 460, 900, 150), "Anton", 140, WHITE,
          weight=400, spacing=14, anim_in=tanim("rise", duration=0.5), anim_out=tanim("fade", duration=0.3),
          name="Título")
    rows = [(TEAL, "@", "@tuusuario"), (CORAL, "♪", "@tuusuario"), (SUN, "#", "#tuhashtag"), (WHITE, "play", "/tucanal")]
    for i, (c, g, h) in enumerate(rows):
        at, y = 0.5 + i * 0.15, 700 + i * 170
        dur = T - 0.3 - at - (3 - i) * 0.05
        pill(t, t.track("shape", "Píldora"), "#11233F", at, dur, Box(110, y, 860, 130), pio(dur, 0.45, 0.3, "out"))
        _icon(t, g, 185, y + 65, 100, c, NAVY, at + 0.1, dur - 0.1)
        _handle(t, h, Box(265, y, 680, 130), at + 0.3, dur - 0.45, size=58, name=f"Usuario {i + 1}")
    return t


TEMPLATES = [transicion_iris, transicion_persianas, transicion_franjas, transicion_ola, transicion_hexagonos,
             transicion_cortes, transicion_puertas, transicion_aro_zoom, transicion_puntos, transicion_destello,
             transicion_esquinas, transicion_chevrones, transicion_iris_vertical, transicion_persianas_vertical,
             pantalla_un_video, pantalla_clara, pantalla_lista, pantalla_foto, pantalla_coral, pantalla_centro,
             pantalla_minimal, pantalla_sol, pantalla_tarjetas, pantalla_gracias,
             redes_pildoras, redes_grande, redes_cuadricula, redes_tercio, redes_circulos, redes_tarjetas, redes_clara,
             redes_esquina, redes_barra, redes_coral, redes_lista_vertical, redes_grande_vertical]
