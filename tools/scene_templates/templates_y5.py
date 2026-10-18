"""YouTuber-style templates (0.15.0, part B of docs/plan-stock.md): Vlog de ciudad, Explicador, Un día en mi vida /
Arréglate conmigo. Category youtuber; order 6300-6399; ids yt-vlog-*, yt-expl-*, yt-dia-*.

Three styles, 18 each:
- Vlog de ciudad: titles over the street, place and time labels, timelapse cuts, a stylised map with the route
  drawn (shapes only, no map tiles), «Día 1 en…» chapter cards, travel stats, metro line, postcard, receipt.
- Explicador: highlighter over text, newspaper clippings, map zooms, facts that appear, numbered points,
  «¿Por qué…?» cards, charts built from shapes (bars, donut, poll), timeline, chalkboard, glossary, magnifier.
- Un día en mi vida / Arréglate conmigo: time on screen, ticking checklists, routine timeline, analog clock,
  makeup and outfit step cards, journal, alarm screen, energy battery, cosy film look.

Helpers live here (city_map, seg/route, pin, gplace, highlight, donut...). Rotations are degrees, clockwise on
screen (y down), about the box centre; groups rotate together through gplace().
"""

from __future__ import annotations

import copy

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, photo_bg,
                 pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides, song,
                 spike, stroke, tall, tanim, text_style, vignette, wide)

O = 6300
CAT = "youtuber"
V = ["youtuber", "vlog de ciudad", "city vlog"]
E = ["youtuber", "explicador", "explainer"]
D = ["youtuber", "un día en mi vida", "day in my life"]
G = ["youtuber", "arréglate conmigo", "get ready with me"]


def T(n: int, id: str, es: str, en: str, tags: list[str], dur: float, w: bool = False, **kw):
    maker = wide if w else tall
    return maker(id, es, en, CAT, dur, order=O + n, tags=tags, **kw)


# --- geometry helpers ------------------------------------------------------------------------------

def gplace(cx: float, cy: float, ang: float, ox: float, oy: float) -> tuple[float, float]:
    """Where a child offset (ox, oy) from a group's centre lands when the group turns `ang` degrees."""
    a = math.radians(ang)
    return cx + ox * math.cos(a) - oy * math.sin(a), cy + ox * math.sin(a) + oy * math.cos(a)


def zmotion(box: Box, zoom, anchor):
    """A whole group zooming about one point: zoom = [(t, s, ease)]."""
    if not zoom:
        return None
    ax, ay = anchor
    return [(z[0], {"s": z[1], "dx": (z[1] - 1) * (box.cx - ax), "dy": (z[1] - 1) * (box.cy - ay)}) + tuple(z[2:])
            for z in zoom]


def zpt(x: float, y: float, s: float, anchor) -> tuple[float, float]:
    return anchor[0] + s * (x - anchor[0]), anchor[1] + s * (y - anchor[1])


def seg(t, colour: str, t0: float, dur: float, a, b, th: float, grow: float = 0.0, ease: str = "linear",
        layers=None, motion=None, name: str = "Trazo", alpha: float = 1.0, **extra):
    """A thick line from a to b (round caps); grow > 0 draws it from a to b in `grow` seconds."""
    (x1, y1), (x2, y2) = a, b
    length = max(1.0, math.hypot(x2 - x1, y2 - y1))
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    box = centered((x1 + x2) / 2, (y1 + y2) / 2, length + th, th)
    if grow and motion is None:
        motion = [(0, {"sx": th / (length + th), "dx": -ux * length / 2, "dy": -uy * length / 2}, ease), (grow, {})]
    return t.solid(t.track("shape", name), colour, t0, dur, box, motion, radius=th / 2, kind="rounded-rectangle",
                   layers=layers, rotation=keys([(0, ang)]), alpha=alpha, **extra)


def route(t, pts, t0: float, speed: float, colour: str, th: float = 14, casing: str | None = "#FFFFFF",
          end: float | None = None) -> list[float]:
    """Draws a polyline segment after segment at `speed` px/s; returns the time it reaches each point."""
    end = t.duration if end is None else end
    times = [t0]
    at = t0
    layers = [stroke(5, casing), fill(colour), ] if casing else None
    for a, b in zip(pts, pts[1:]):
        g = max(0.12, math.hypot(b[0] - a[0], b[1] - a[1]) / speed)
        seg(t, colour, at, end - at, a, b, th, grow=g, layers=layers, name="Ruta")
        at += g
        times.append(at)
    return times


def pin(t, x: float, y: float, at: float, colour: str, size: float = 70, end: float | None = None, dot="#FFFFFF"):
    """A map pin whose tip is at (x, y); it drops in at `at`."""
    end = t.duration if end is None else end
    d = end - at
    drop = [(0, {"dy": -140}, "back"), (0.45, {})]
    op = keys([(0, 0.0), (0.15, 1.0)])
    t.solid(t.track("shape", "Pin"), colour, at, d, centered(x, y - size * 0.42, size * 0.66, size * 0.62), drop,
            kind="triangle", rotation=keys([(0, 180)]), opacity=op)
    t.solid(t.track("shape", "Pin"), colour, at, d, centered(x, y - size * 0.95, size, size), drop, kind="ellipse",
            layers=[shadow("#000000", 0, 6, 14, 0.35), fill(colour), no_stroke()], opacity=op)
    t.solid(t.track("shape", "Pin"), dot, at, d, centered(x, y - size * 0.95, size * 0.38, size * 0.38), drop,
            kind="ellipse", opacity=op)


MAP_LIGHT = dict(land="#F1ECE2", water="#9DD0E3", park="#C5E2B4", road="#FFFFFF", minor="#FBF8F2", text="#8A8170")
MAP_DARK = dict(land="#1C2230", water="#145276", park="#24503A", road="#4A5670", minor="#2A3242", text="#7D889C")
MAP_MINT = dict(land="#EAF4EE", water="#7CC6D6", park="#B9E0A5", road="#FFFFFF", minor="#F7FBF8", text="#6F8A7C")


def city_map(t, pal: dict, t0: float = 0.0, dur: float | None = None, zoom=None, anchor=(0, 0),
             names: bool = True) -> dict:
    """A stylised, made-up city (no real map): a bay, a river with bridges, parks, avenues and side streets.
    Returns the avenue lines {'h': [y...], 'v': [x...]} so routes can follow them."""
    dur = t.duration - t0 if dur is None else dur
    W, H = t.w, t.h
    hs = [0.2 * H, 0.47 * H, 0.72 * H]
    vs = [0.22 * W, 0.5 * W, 0.78 * W]

    def box_shape(colour, box, kind="rectangle", radius=0, alpha=1.0):
        t.solid(t.track("shape", "Mapa"), colour, t0, dur, box, zmotion(box, zoom, anchor), kind=kind, radius=radius,
                alpha=alpha)

    def line_shape(colour, a, b, th, alpha=1.0):
        (x1, y1), (x2, y2) = a, b
        length = math.hypot(x2 - x1, y2 - y1)
        box = centered((x1 + x2) / 2, (y1 + y2) / 2, length + th, th)
        seg(t, colour, t0, dur, a, b, th, motion=zmotion(box, zoom, anchor), name="Mapa", alpha=alpha)

    box_shape(pal["land"], Box(-40, -40, W + 80, H + 80))
    box_shape(pal["water"], centered(W * 1.02, H * 1.04, W * 0.62, H * 0.5), kind="ellipse")
    river = [(-0.05, 0.33), (0.2, 0.36), (0.38, 0.52), (0.6, 0.58), (0.74, 0.8), (0.9, 0.92)]
    for a, b in zip(river, river[1:]):
        line_shape(pal["water"], (a[0] * W, a[1] * H), (b[0] * W, b[1] * H), 0.05 * min(W, H) + 26)
    box_shape(pal["park"], Box(0.05 * W, 0.52 * H, 0.13 * W, 0.15 * H), "rounded-rectangle", 30)
    box_shape(pal["park"], centered(0.64 * W, 0.24 * H, 0.15 * W, 0.15 * W), "ellipse")
    box_shape(pal["park"], Box(0.83 * W, 0.26 * H, 0.12 * W, 0.16 * H), "rounded-rectangle", 30)
    for y in (0.33 * H, 0.6 * H, 0.86 * H):
        line_shape(pal["minor"], (-20, y), (W + 20, y), 9)
    for x in (0.36 * W, 0.64 * W, 0.9 * W, 0.08 * W):
        line_shape(pal["minor"], (x, -20), (x, H + 20), 9)
    for y in hs:
        line_shape(pal["road"], (-20, y), (W + 20, y), 24)
    for x in vs:
        line_shape(pal["road"], (x, -20), (x, H + 20), 24)
    line_shape(pal["road"], (0.02 * W, 0.98 * H), (0.62 * W, 0.02 * H), 20)
    if names:
        nm = t.track("text", "Mapa")
        s = 1.0
        for i, (txt, x, y, ang) in enumerate([("AV. CENTRAL", 0.36 * W, hs[1] - 30, 0), ("RÍO", 0.27 * W, 0.4 * H, 20),
                                              ("PARQUE", 0.115 * W, 0.595 * H, 0)]):
            bx = centered(x, y, 360, 50)
            label(t, t.track("text", "Mapa") if i else nm, txt, t0, dur, bx, "Barlow Condensed", 28 * s, pal["text"],
                  weight=600, spacing=4, editable=False, motion=zmotion(bx, zoom, anchor), rotation=keys([(0, ang)]))
    return {"h": hs, "v": vs}


def highlight(t, colour: str, at: float, box: Box, length: float = 0.45, alpha: float = 0.9, end=None, motion=None,
              **extra):
    """A marker stroke drawn left to right behind a line of text (put it on a track below the text)."""
    end = t.duration if end is None else end
    m = motion or [(0, {"sx": 0.0, "dx": -box.w / 2}, "out"), (length, {})]
    return t.solid(t.track("shape", "Resaltador"), colour, at, end - at, box, m, radius=10, kind="rounded-rectangle",
                   alpha=alpha, **extra)


def hollow_ring(colour: str, width: float, trim: float | None = None) -> list:
    st = {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
          "paint": {"kind": "solid", "color": f"#ff{colour.lstrip('#').lower()}"}, "opacity": 1.0}
    if trim is not None:
        st.update(trimStart=0.0, trimEnd=trim)
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}, st]


def donut(t, colour: str, width: float, at: float, length: float, frac: float, box: Box, end=None):
    end = t.duration if end is None else end
    clip = t.solid(t.track("shape", "Gráfico"), colour, at, end - at, box, layers=hollow_ring(colour, width, 0.0),
                   kind="ellipse", rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": keys([(0, 0.0, "inout"), (length, frac)])}
    return clip


def counting(t, values: list[str], t0: float, step: float, box: Box, style: dict, name: str, end=None, motion=None,
             final_style: dict | None = None):
    """A number that counts with quick clips; the last value is the editable one."""
    end = t.duration if end is None else end
    tr = t.track("text", name)
    for i, v in enumerate(values[:-1]):
        t.text(tr, v, t0 + i * step, step, box, copy.deepcopy(style), motion, editable=False)
    at = t0 + (len(values) - 1) * step
    t.text(tr, values[-1], at, end - at, box, copy.deepcopy(final_style or style), motion, label=name)


def bar_up(t, colour: str, at: float, box: Box, length: float = 0.7, end=None, radius: float = 12, layers=None):
    """A bar that grows up from its bottom edge."""
    end = t.duration if end is None else end
    return t.solid(t.track("shape", "Barra"), colour, at, end - at, box,
                   [(0, {"sy": 0.0, "dy": box.h / 2}, "out"), (length, {})], radius=radius, kind="rounded-rectangle",
                   layers=layers)


def bar_right(t, colour: str, at: float, box: Box, length: float = 0.7, end=None, radius: float = 12, alpha=1.0):
    end = t.duration if end is None else end
    return t.solid(t.track("shape", "Barra"), colour, at, end - at, box,
                   [(0, {"sx": 0.0, "dx": -box.w / 2}, "out"), (length, {})], radius=radius, kind="rounded-rectangle",
                   alpha=alpha)


def emoji(t, ch: str, t0: float, dur: float, box: Box, size: int, motion=None, **extra):
    return label(t, t.track("text", "Icono"), ch, t0, dur, box, "Inter", size, "#FFFFFF", weight=400, editable=False,
                 motion=motion, **extra)


def rounded_photo(t, sample: str, t0: float, dur: float, box: Box, motion=None, radius: float = 0.08, label_=None,
                  reuse=None, **extra):
    """A photo with rounded corners: a freeform mask traced around the corners (radius as a fraction of the
    shorter side)."""
    track = t.track("video", "Foto")
    clip = t.photo(track, sample, t0, dur, box, motion, label=label_, reuse=reuse, **extra)
    rx = radius * min(box.w, box.h) / box.w
    ry = radius * min(box.w, box.h) / box.h
    pts = []
    for cx, cy, a0 in ((1 - rx, ry, -90), (1 - rx, 1 - ry, 0), (rx, 1 - ry, 90), (rx, ry, 180)):
        for k in range(7):
            a = math.radians(a0 + k * 15)
            pts.append([round(cx + rx * math.cos(a), 4), round(cy + ry * math.sin(a), 4)])
    t.mask(track, clip, "freeform", points=pts, smooth=False)
    return clip


# =============================================================================================
# 1. Vlog de ciudad
# =============================================================================================

def vlog_titulo_calle():
    t = T(0, "yt-vlog-titulo-calle", "Título sobre la calle", "Street title", V + ["título", "title", "ciudad"], 8.0,
          thumb_at=3.7)
    slides(t, ["y5-street-07", "y5-street-01", "y5-street-08"], 0, 2.7, transition="zoom_in", tdur=0.35,
           kb_amount=0.06, labels=["Toma 1", "Toma 2", "Toma 3"])
    shade_bottom(t, 1050, 0.85)
    shade_top(t, 320, 0.5)
    t.solid(t.track("shape", "REC"), "#FF3B30", 0, 8, centered(84, 122, 30, 30), kind="ellipse",
            opacity=blink(8, 1.0, 0.15))
    label(t, t.track("text", "REC"), "REC", 0, 8, Box(112, 94, 200, 56), "Barlow Condensed", 48, "#FFFFFF",
          weight=700, align="left", editable=False)
    label(t, t.track("text", "Hora"), "09:41", 0, 8, Box(760, 94, 260, 56), "Barlow Condensed", 48, "#FFFFFF",
          weight=600, align="right", name="Hora")
    label(t, t.track("text", "Episodio"), "VLOG · EPISODIO 03", 0.3, 7.7, Box(60, 1040, 900, 60), "Montserrat", 36,
          "#111111", weight=800, spacing=6, align="left", box_bg=("#FFD23F", 1.0), box_pad=14,
          anim_in=tanim("wipe", duration=0.5, angle=0), name="Episodio")
    label(t, t.track("text", "Ciudad"), "TOKIO", 0.4, 7.6, Box(40, 1110, 1000, 470), "League Gothic", 460, "#FFFFFF",
          weight=400, align="left", line=0.9, layers=[shadow("#000000", 0, 10, 30, 0.45), fill("#FFFFFF")],
          anim_in=tanim("rise", duration=0.6, unit="character", stagger=0.06), name="Ciudad")
    line(t, t.track("shape", "Línea"), "#FFD23F", 1.0, 7.0, Box(60, 1612, 380, 8), grow="x", length=0.5)
    label(t, t.track("text", "Coordenadas"), "35.68° N · 139.69° E", 1.1, 6.9, Box(60, 1640, 900, 70),
          "Barlow Condensed", 52, "#FFFFFF", weight=500, spacing=4, align="left", anim_in=tanim("fade", duration=0.5),
          name="Coordenadas")
    song(t, "upbeat", 0)
    return t


def vlog_ruta_mapa():
    t = T(1, "yt-vlog-ruta-mapa", "Mapa con la ruta del día", "Route map of the day",
          V + ["mapa", "map", "ruta", "route"], 12.0, w=True, thumb_at=9.4, background="#F1ECE2")
    g = city_map(t, MAP_LIGHT)
    h, v = g["h"], g["v"]
    pts = [(150, h[2]), (v[0], h[2]), (v[0], h[1]), (v[1], h[1]), (v[1], h[0]), (v[2], h[0]), (v[2], h[2])]
    times = route(t, pts, 1.0, 420, "#E63946", th=14)
    stops = [(1, "Café del puerto", "y5-street-02", (0, -250)), (3, "Mercado", "coffee-04", (-250, -150)),
             (5, "Mirador", "y5-h-skyline-01", (-260, 170)), (6, "Cena", "y5-night-05", (-260, -40))]
    for k, (i, name, sample, (ox, oy)) in enumerate(stops):
        x, y = pts[i]
        at = times[i]
        circle_photo(t, sample, at + 0.15, t.duration - at - 0.15, centered(x + ox, y + oy, 190, 190), pop(0, 0.45),
                     ring_colour="#FFFFFF", ring_width=8, label=f"Parada {k + 1}")
        pin(t, x, y, at, "#E63946", 64)
        label(t, t.track("text", "Parada"), f"{k + 1} · {name}", at + 0.3, t.duration - at - 0.3,
              centered(x + ox, y + oy + 135, 420, 60), "Montserrat", 32, "#FFFFFF", weight=800,
              box_bg=("#1D3557", 1.0), box_pad=12, box_radius=12, anim_in=tanim("pop", duration=0.35),
              name=f"Parada {k + 1}")
    rrect(t, t.track("shape", "Título"), "#1D3557", 0.2, 11.8, Box(40, 40, 620, 150), 24, slide_in(dx=-700, length=0.6),
          layers=[shadow("#000000", 0, 8, 24, 0.3), fill("#1D3557"), no_stroke()])
    label(t, t.track("text", "Título"), "RUTA DE HOY", 0.5, 11.5, Box(80, 58, 560, 50), "Montserrat", 32, "#FFD166",
          weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.4), name="Etiqueta")
    label(t, t.track("text", "Título"), "Un día a pie por Lisboa", 0.6, 11.4, Box(80, 104, 560, 70), "Montserrat", 46,
          "#FFFFFF", weight=700, align="left", anim_in=tanim("fade", duration=0.4), name="Título")
    label(t, t.track("text", "Distancia"), "🚶 6,4 km · 9 h", times[-1] + 0.4, t.duration - times[-1] - 0.4,
          Box(1480, 960, 400, 80), "Montserrat", 40, "#1D3557", weight=800, box_bg=("#FFD166", 1.0), box_pad=16,
          box_radius=40, anim_in=tanim("pop", duration=0.4), name="Distancia")
    song(t, "upbeat", 1)
    return t


def vlog_dia_1():
    t = T(2, "yt-vlog-dia-1", "Día 1 en… (capítulos)", "Day 1 in… (chapters)",
          V + ["capítulos", "chapters", "viaje", "travel"], 12.0, w=True, thumb_at=0.9)
    photos = ["y5-h-street-03", "y5-h-street-05", "y5-h-skyline-04"]
    chap = [("DÍA 1", "Llegada y primer paseo", "#F4A261"), ("DÍA 2", "El barrio antiguo", "#2A9D8F"),
            ("DÍA 3", "Atardecer en el río", "#E76F51")]
    vt = t.track("video", "Fotos")
    for i, s in enumerate(photos):
        t.photo(vt, s, i * 4.0, 4.0, t.full, kb(4.0, 1.0, 1.08), label=f"Día {i + 1}")
    panel, big, sub, city, corner, cornerbg = (t.track("shape", "Capítulo"), t.track("text", "Capítulo"),
                                                t.track("text", "Capítulo"), t.track("text", "Capítulo"),
                                                t.track("text", "Esquina"), None)
    for i, (d, s, c) in enumerate(chap):
        a = i * 4.0
        m = [(0, {"dx": -1920}, "out"), (0.35, {}, "hold"), (1.35, {}, "in"), (1.7, {"dx": 1920})]
        t.solid(panel, c, a, 1.7, t.full, m)
        label(t, big, d, a, 1.7, Box(160, 260, 1600, 340), "Big Shoulders Display", 320, "#FFFFFF", weight=900,
              motion=m, name=f"Capítulo {i + 1}")
        label(t, city, "en Lisboa", a, 1.7, Box(160, 560, 1600, 170), "Yellowtail", 130, "#1B1B1B", weight=400,
              motion=m, name=f"Ciudad {i + 1}")
        label(t, sub, s, a, 1.7, Box(160, 760, 1600, 80), "Montserrat", 48, "#FFFFFF", weight=700, spacing=3,
              motion=m, name=f"Subtítulo {i + 1}")
        label(t, corner, f"{d} · {s}", a + 1.8, 2.2 if i < 2 else 2.2, Box(60, 950, 1200, 70), "Montserrat", 36,
              "#FFFFFF", weight=800, align="left", box_bg=(c, 1.0), box_pad=14, box_radius=8,
              anim_in=tanim("slide-right", duration=0.4, distance=0.2), anim_out=tanim("fade", duration=0.2),
              name=f"Rótulo {i + 1}")
    song(t, "upbeat", 2)
    return t


def vlog_hora_lugar():
    t = T(3, "yt-vlog-hora-lugar", "Hora y lugar", "Time and place", V + ["hora", "time", "lugar", "place"], 10.4,
          thumb_at=3.6)
    items = [("08:12", "Mercado central", "y5-street-02"), ("11:40", "Calle de las flores", "y5-outfit-07"),
             ("16:05", "Mirador del puerto", "city-04"), ("21:30", "Cena en el centro", "y5-night-05")]
    slides(t, [s for _, _, s in items], 0, 2.6, transition="crossfade", tdur=0.4, kb_amount=0.07,
           labels=[f"Toma {i + 1}" for i in range(4)])
    shade_bottom(t, 760, 0.85)
    shade_top(t, 260, 0.45)
    # day progress: a sun that travels along a thin line
    t.solid(t.track("shape", "Día"), "#FFFFFF", 0, 10.4, Box(80, 150, 920, 4), alpha=0.5)
    bar_right(t, "#FFD166", 0, Box(80, 148, 920, 8), length=10.4, radius=4)
    emoji(t, "☀️", 0, 10.4, centered(80, 152, 90, 90), 56, motion=[(0, {}), (10.4, {"dx": 920})])
    tt, pt = t.track("text", "Hora"), t.track("text", "Lugar")
    for i, (h, p, _) in enumerate(items):
        a = i * 2.6
        d = 2.6 if i < 3 else 10.4 - a
        label(t, tt, h, a, d, Box(70, 1430, 900, 230), "Bebas Neue", 220, "#FFFFFF", weight=400, align="left",
              layers=[shadow("#000000", 0, 6, 20, 0.4), fill("#FFFFFF")],
              anim_in=tanim("slide-up", duration=0.35, distance=0.3), name=f"Hora {i + 1}")
        label(t, pt, f"📍 {p}", a + 0.1, d - 0.1, Box(70, 1660, 940, 80), "Montserrat", 50, "#FFD166", weight=700,
              align="left", anim_in=tanim("fade", duration=0.35), name=f"Lugar {i + 1}")
    song(t, "upbeat", 3)
    return t


def vlog_timelapse():
    t = T(4, "yt-vlog-timelapse", "Timelapse de la ciudad", "City timelapse",
          V + ["timelapse", "hyperlapse", "reloj", "clock"], 8.0, thumb_at=4.55)
    vt = t.track("video", "Tomas")
    step = 0.32
    n = int(6.4 / step)
    first = {}
    samples = [("y5-street-08", "Mañana"), ("y5-h-skyline-02", "Tarde"), ("y5-night-05", "Noche")]
    for k in range(n):
        phase = min(2, k * 3 // n)
        s, lab = samples[phase]
        dx = (k % 4) * 14 - 21
        box = centered(540 + dx, 960, 1180, 2098)
        if phase not in first:
            first[phase] = t.photo(vt, s, k * step, step, box, label=f"Foto de la {lab.lower()}")["placeholderId"]
        else:
            t.photo(vt, s, k * step, step, box, reuse=first[phase])
    last = n * step
    t.photo(vt, samples[2][0], last, 8.0 - last, box, kb(8.0 - last, 1.0, 1.06), reuse=first[2])
    shade_top(t, 700, 0.6)
    style = text_style("Teko", 300, [shadow("#000000", 0, 8, 24, 0.5), fill("#FFFFFF")], weight=600)
    hours = [f"{6 + int(17 * k / (n - 1)):02d}:{(k * 37) % 60:02d}" for k in range(n)]
    hours[-1] = "23:00"
    counting(t, hours, 0, step, Box(40, 180, 1000, 320), style, "Hora final")
    label(t, t.track("text", "Título"), "un día en 8 segundos", 0.3, 7.7, Box(40, 470, 1000, 110), "Caveat", 90,
          "#FFD166", weight=700, anim_in=tanim("typewriter", duration=0.8, unit="character"), name="Título")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([k * step * 4 for k in range(1, 5)], 0.25, 0.2)})],
             name="Golpes")
    song(t, "electro", 0)
    return t


def vlog_stats_viaje():
    t = T(5, "yt-vlog-stats-viaje", "El viaje en números", "The trip in numbers",
          V + ["estadísticas", "stats", "números", "resumen"], 9.0, w=True, thumb_at=6.2)
    t.photo(t.track("video", "Foto"), "y5-h-street-06", 0, 9.0, t.full, kb(9.0, 1.05, 1.15), label="Foto de fondo",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=18)])
    shade_full(t, 0.55, colour="#0B1320")
    label(t, t.track("text", "Título"), "Lisboa en números", 0.2, 8.8, Box(160, 120, 1600, 160), "Archivo Black", 110,
          "#FFFFFF", weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.12), name="Título")
    label(t, t.track("text", "Sub"), "4 días · 1 mochila · 0 planes fijos", 0.6, 8.4, Box(160, 280, 1600, 70),
          "Montserrat", 42, "#9AD1D4", weight=600, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    tiles = [("👟", "42", "km caminados"), ("☕", "11", "cafés"), ("📸", "586", "fotos"), ("🚋", "9", "viajes en tranvía")]
    for i, (ic, num, txt) in enumerate(tiles):
        at = 1.2 + i * 0.45
        x = 120 + i * 430
        box = Box(x, 420, 390, 500)
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", at, 9.0 - at, box, 36, pop(0, 0.5, 0.6),
              layers=[fill("#FFFFFF", 0.12), stroke(2, "#FFFFFF", 0.35)])
        emoji(t, ic, at + 0.1, 8.9 - at, centered(box.cx, 520, 160, 140), 96, motion=pop(0, 0.45))
        label(t, t.track("text", "Número"), num, at + 0.2, 8.8 - at, centered(box.cx, 690, 380, 190), "Archivo Black",
              150, "#FFD166", weight=400, anim_in=tanim("stamp", duration=0.3), name=f"Número {i + 1}")
        label(t, t.track("text", "Dato"), txt, at + 0.3, 8.7 - at, centered(box.cx, 840, 360, 110), "Montserrat", 38,
              "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
    song(t, "upbeat", 4)
    return t


def vlog_noche():
    t = T(6, "yt-vlog-noche", "La ciudad de noche", "The city at night",
          V + ["noche", "night", "neón", "neon"], 9.0, thumb_at=4.0, background="#05060A")
    slides(t, ["y5-night-05", "night-04", "y5-night-01"], 0, 3.0, transition="blur_dissolve", tdur=0.6,
           kb_amount=0.08, labels=["Toma 1", "Toma 2", "Toma 3"])
    shade_full(t, 0.3, colour="#0A0420")
    label(t, t.track("text", "Título"), "Tokio\nde noche", 0.4, 8.6, Box(40, 560, 1000, 600), "Yellowtail", 230,
          "#FFE3F6", weight=400, line=0.95,
          layers=[glow("#FF2E93", 40, 0.95), glow("#FF2E93", 12, 0.9, id="glow2"), fill("#FFE3F6")],
          anim_in=tanim("flicker-in", duration=0.8), anim_loop=tanim("flicker", intensity=0.25, speed=3),
          name="Título")
    label(t, t.track("text", "Hora"), "23:47", 0.8, 8.2, Box(60, 1600, 500, 120), "VT323", 120, "#5CF2FF", weight=400,
          align="left", layers=[glow("#5CF2FF", 18, 0.8), fill("#CFFBFF")], anim_in=tanim("typewriter", duration=0.5),
          name="Hora")
    label(t, t.track("text", "Clima"), "18° · lluvia ligera", 1.0, 8.0, Box(60, 1720, 700, 70), "VT323", 60,
          "#FFFFFF", weight=400, align="left", anim_in=tanim("fade", duration=0.4), name="Clima")
    t.adjust([effect("bloom_glow", threshold=0.6, intensity=0.8, blurRadius=12),
              effect("rgb_split", amount=3, angle=0, animated=False)], name="Neón")
    song(t, "electro", 2)
    return t


def vlog_billete():
    t = T(7, "yt-vlog-billete", "Billete de viaje", "Travel ticket", V + ["billete", "ticket", "viaje", "travel"],
          9.0, thumb_at=6.0, background="#DCEBF0")
    bg_gradient(t, [(0, "#DCEBF0"), (1, "#F6E7D2")], angle=90)
    dots(t, ["#FFFFFF"], 14, 0, 9.0, seed=51, size=(10, 24), drift=40, alpha=0.6)
    cx, cy, ang = 540, 560, -3
    m = [(0, {"dy": -900}, "out"), (0.7, {})]
    tk = Box(cx - 450, cy - 300, 900, 600)
    rrect(t, t.track("shape", "Billete"), "#FFFFFF", 0.2, 8.8, tk, 36, m, rotation=keys([(0, ang)]),
          layers=[shadow("#1D3557", 0, 16, 36, 0.25), fill("#FFFFFF"), no_stroke()])
    hx, hy = gplace(cx, cy, ang, 0, -240)
    rrect(t, t.track("shape", "Billete"), "#1D3557", 0.2, 8.8, centered(hx, hy, 900, 120), 36, m,
          rotation=keys([(0, ang)]))
    def put(txt, ox, oy, w, h, font, size, col, name, weight=700, editable=True, align="center", spacing=0):
        x, y = gplace(cx, cy, ang, ox, oy)
        label(t, t.track("text", "Billete"), txt, 0.2, 8.8, centered(x, y, w, h), font, size, col, weight=weight,
              motion=m, rotation=keys([(0, ang)]), editable=editable, name=name, align=align, spacing=spacing)
    put("TARJETA DE EMBARQUE  ✈", 0, -240, 820, 70, "Montserrat", 40, "#FFFFFF", "Cabecera", 800, spacing=4)
    put("MAD", -260, -90, 400, 170, "Archivo Black", 140, "#1D3557", "Origen", 400)
    put("IST", 260, -90, 400, 170, "Archivo Black", 140, "#E63946", "Destino", 400)
    put("✈", 0, -90, 120, 120, "Inter", 80, "#1D3557", "Avión", 400, editable=False)
    put("Madrid", -260, 10, 320, 60, "Montserrat", 36, "#5C677D", "Ciudad de origen", 600)
    put("Estambul", 260, 10, 320, 60, "Montserrat", 36, "#5C677D", "Ciudad de destino", 600)
    put("- - - - - - - - - - - - - - - - - - - - - -", 0, 75, 860, 40, "Montserrat", 30, "#C9CED6", "Corte", 700,
        editable=False)
    for k, (a, b) in enumerate([("VUELO", "FS 2026"), ("PUERTA", "B12"), ("ASIENTO", "14A")]):
        put(a, -280 + k * 280, 140, 260, 40, "Montserrat", 26, "#8D99AE", f"Etiqueta {k + 1}", 700, spacing=4)
        put(b, -280 + k * 280, 200, 260, 70, "Montserrat", 50, "#1D3557", f"Dato {k + 1}", 800)
    framed(t, "y5-outfit-05", 3.0, 6.0, centered(560, 1340, 620, 620), [(0, {"s": 1.4, "dy": 300}, "out"), (0.5, {})],
           border=18, bottom=90, rotation=keys([(0, 4)]), label="Foto del destino")
    label(t, t.track("text", "Polaroid"), "¡llegamos!", 3.3, 5.7, centered(560, 1712, 600, 90), "Caveat", 80,
          "#1D3557", weight=700, rotation=keys([(0, 4)]), anim_in=tanim("typewriter", duration=0.6), name="Nota")
    ring(t, t.track("shape", "Sello"), "#E63946", 10, 5.0, 4.0, centered(860, 1050, 260, 260), [(0, {"s": 2.2}, "snap"),
         (0.25, {})], opacity=keys([(0, 0.0), (0.1, 0.85)]))
    label(t, t.track("text", "Sello"), "ENTRADA\n12 OCT", 5.0, 4.0, centered(860, 1050, 240, 160), "Special Elite", 44,
          "#E63946", weight=400, line=1.0, motion=[(0, {"s": 2.2}, "snap"), (0.25, {})], rotation=keys([(0, -14)]),
          name="Sello")
    label(t, t.track("text", "Título"), "Destino: Estambul", 0.6, 8.4, Box(60, 120, 960, 110), "Montserrat", 72,
          "#1D3557", weight=800, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1), name="Título")
    song(t, "upbeat", 5)
    return t


def vlog_cinematico():
    t = T(8, "yt-vlog-cinematico", "Intro cinematográfica de ciudad", "Cinematic city intro",
          V + ["cinematográfico", "cinematic", "intro"], 10.0, w=True, thumb_at=4.6)
    slides(t, ["y5-h-skyline-05", "y5-h-street-08", "y5-h-street-04"], 0, 3.4, transition="blur_dissolve", tdur=0.8,
           kb_amount=0.06, labels=["Toma 1", "Toma 2", "Toma 3"])
    t.adjust([effect("cinematic_grade", strength=0.7), effect("light_leak", intensity=0.35, speed=0.6)], name="Look")
    letterbox(t, 2.39)
    label(t, t.track("text", "Ciudad"), "R O M A", 1.4, 7.4, Box(160, 400, 1600, 200), "Cinzel", 160, "#F5EBDD",
          weight=600, spacing=30, anim_in=tanim("blur-in", duration=1.4, blur=20), anim_out=tanim("fade", duration=0.8),
          name="Ciudad")
    line(t, t.track("shape", "Línea"), "#F5EBDD", 2.2, 6.4, centered(960, 620, 360, 2), grow="c", length=1.0,
         opacity=keys([(0, 1.0), (5.6, 1.0), (6.4, 0.0)]))
    label(t, t.track("text", "Coordenadas"), "41.90° N  ·  12.49° E", 2.6, 6.0, Box(160, 650, 1600, 70),
          "Cormorant Garamond", 46, "#F5EBDD", weight=500, spacing=10, italic=True,
          anim_in=tanim("fade", duration=1.0), anim_out=tanim("fade", duration=0.8), name="Coordenadas")
    t.adjust([effect("stylize.film_grain", amount=0.15)], name="Grano")
    song(t, "cine", 2)
    return t


def vlog_barrios():
    t = T(9, "yt-vlog-barrios", "Tres barrios en un día", "Three neighbourhoods in a day",
          V + ["barrios", "neighbourhoods", "pantalla dividida", "split screen"], 10.0, w=True, thumb_at=5.3,
          background="#111111")
    names = [("01", "Barrio antiguo"), ("02", "Centro"), ("03", "Junto al río")]
    samples = ["y5-street-04", "y5-street-07", "y5-street-01"]
    for i in range(3):
        x = i * 640
        box = Box(x + 6, 0, 628, 1080)
        dy = 1100 if i % 2 else -1100
        at = 0.2 + i * 0.25
        t.photo(t.track("video", "Barrio"), samples[i], at, 10 - at, box,
                [(0, {"dy": dy}, "out"), (0.7, {}, "linear"), (10 - at, {"s": 1.05})], label=f"Barrio {i + 1}")
        # each panel goes dim while another one is the star
        lit = 3.0 + i * 2.2
        op = keys([(0, 0.0, "hold"), (2.8, 0.0, "smooth"), (3.1, 0.55, "hold"), (lit, 0.55, "smooth"),
                   (lit + 0.3, 0.0, "hold"), (lit + 2.0, 0.0, "smooth"), (lit + 2.3, 0.55)]) if i == 0 else \
            keys([(0, 0.0, "hold"), (2.8, 0.0, "smooth"), (3.1, 0.55, "hold"), (lit, 0.55, "smooth"),
                  (lit + 0.3, 0.0, "hold"), (lit + 2.0, 0.0, "smooth"), (lit + 2.3, 0.55)])
        t.solid(t.track("shape", "Sombra"), "#000000", at, 10 - at, box, opacity=op)
        t.solid(t.track("shape", "Sombra"), "#000000", at, 10 - at, Box(x + 6, 700, 628, 380),
                layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.8)], angle=90), no_stroke()])
        label(t, t.track("text", "Número"), names[i][0], at + 0.6, 9.4 - at, Box(x + 50, 780, 540, 130), "Bebas Neue",
              130, "#FFD166", weight=400, align="left", anim_in=tanim("slide-up", duration=0.4), name=f"Número {i + 1}")
        label(t, t.track("text", "Barrio"), names[i][1], at + 0.7, 9.3 - at, Box(x + 50, 910, 560, 80), "Montserrat", 54,
              "#FFFFFF", weight=800, align="left", anim_in=tanim("slide-up", duration=0.4), name=f"Barrio {i + 1}")
    label(t, t.track("text", "Título"), "3 barrios en un día", 1.0, 9.0, Box(460, 50, 1000, 100), "Montserrat", 50,
          "#111111", weight=800, box_bg=("#FFFFFF", 1.0), box_pad=18, box_radius=40,
          anim_in=tanim("pop", duration=0.4), name="Título")
    song(t, "upbeat", 6)
    return t


def vlog_postal():
    t = T(10, "yt-vlog-postal", "Saludos desde… (postal)", "Greetings from… (postcard)",
          V + ["postal", "postcard", "retro", "viaje"], 9.0, thumb_at=5.0, background="#264653")
    bg(t, "#264653")
    dots(t, ["#2A9D8F", "#E9C46A"], 16, 0, 9.0, seed=61, size=(14, 30), kinds=("star",), drift=60, alpha=0.6)
    cx, cy, ang = 540, 900, -4
    m = [(0, {"s": 0.6, "dy": 400}, "back"), (0.7, {})]
    card = centered(cx, cy, 960, 1320)
    rrect(t, t.track("shape", "Postal"), "#FFF6E5", 0.2, 8.8, card, 18, m, rotation=keys([(0, ang)]),
          layers=[shadow("#000000", 0, 18, 40, 0.4), fill("#FFF6E5"), no_stroke()])
    px, py = gplace(cx, cy, ang, 0, -160)
    t.photo(t.track("video", "Foto"), "city-01", 0.2, 8.8, centered(px, py, 880, 900), m, rotation=keys([(0, ang)]),
            label="Foto de la ciudad")
    def put(txt, ox, oy, w, h, font, size, col, name, layers=None, editable=True, rot=0.0, anim=None, **kw):
        x, y = gplace(cx, cy, ang, ox, oy)
        label(t, t.track("text", "Postal"), txt, 0.2, 8.8, centered(x, y, w, h), font, size, col, weight=400,
              motion=m, rotation=keys([(0, ang + rot)]), editable=editable, name=name, layers=layers, anim_in=anim,
              **kw)
    put("Saludos desde", -40, -470, 820, 140, "Pacifico", 96, "#FFFFFF", "Saludo",
        layers=[shadow("#000000", 0, 6, 16, 0.6), fill("#FFFFFF")], anim=tanim("fade", duration=0.4, delay=0.6))
    put("ROMA", 0, -60, 940, 320, "Alfa Slab One", 230, "#E9C46A", "Ciudad",
        layers=[shadow("#264653", 14, 14, 0, 1.0), stroke(10, "#264653"), fill("#E9C46A")],
        anim=tanim("pop", duration=0.5, unit="character", stagger=0.08, delay=0.7))
    put("Querida mamá: aquí todo es\nhermoso. ¡Te extraño!", -150, 470, 560, 160, "Caveat", 52, "#264653", "Mensaje",
        anim=tanim("typewriter", duration=1.6, delay=1.5), line=1.0)
    # stamp + postmark
    sx, sy = gplace(cx, cy, ang, 340, 470)
    rrect(t, t.track("shape", "Sello"), "#E76F51", 0.2, 8.8, centered(sx, sy, 160, 190), 6, m,
          rotation=keys([(0, ang + 6)]), layers=[stroke(6, "#FFFFFF"), fill("#E76F51")])
    label(t, t.track("text", "Sello"), "✈\n2026", 0.2, 8.8, centered(sx, sy, 150, 170), "Montserrat", 40, "#FFFFFF",
          weight=800, line=1.0, motion=m, rotation=keys([(0, ang + 6)]), editable=False)
    ring(t, t.track("shape", "Matasellos"), "#264653", 5, 2.8, 6.2, centered(sx - 110, sy - 20, 210, 210),
         [(0, {"s": 1.8}, "snap"), (0.2, {})], opacity=keys([(0, 0.0), (0.1, 0.7)]))
    label(t, t.track("text", "Matasellos"), "〰〰〰〰", 2.8, 6.2, centered(sx - 170, sy - 20, 320, 60), "Inter", 46,
          "#264653", weight=400, editable=False, opacity=keys([(0, 0.0), (0.1, 0.7)]))
    t.adjust([effect("stylize.film_grain", amount=0.12)], name="Grano")
    song(t, "jazz", 0)
    return t


def vlog_mapa_zoom():
    t = T(11, "yt-vlog-mapa-zoom", "Zoom al mapa: estás aquí", "Map zoom: you are here",
          V + ["mapa", "map", "zoom", "ubicación"], 9.0, thumb_at=3.8, background="#1C2230")
    P = (0.64 * 1080, 0.47 * 1920)
    zoom = [(0, 1.0, "hold"), (0.6, 1.0, "inout"), (2.8, 1.5, "linear"), (4.6, 1.58)]
    city_map(t, MAP_DARK, 0, 4.6, zoom=zoom, anchor=P)
    x, y = P
    ring(t, t.track("shape", "Pulso"), "#4CC9F0", 6, 2.9, 1.7, centered(x, y, 160, 160),
         [(0, {"s": 0.3}, "out"), (0.9, {"s": 2.2})], opacity=keys([(0, 0.9), (0.9, 0.0)]))
    pin(t, x, y, 2.8, "#4CC9F0", 150, end=4.6)
    label(t, t.track("text", "Aquí"), "Estás aquí", 3.1, 1.5, centered(x - 40, y + 110, 700, 110), "Montserrat", 70,
          "#0B1320", weight=800, box_bg=("#4CC9F0", 1.0), box_pad=18, box_radius=50,
          anim_in=tanim("pop", duration=0.35), name="Etiqueta del mapa")
    label(t, t.track("text", "Título"), "Barrio Alto", 0.3, 4.3, Box(60, 140, 960, 160), "Montserrat", 110, "#FFFFFF",
          weight=900, anim_in=tanim("rise", duration=0.5), name="Lugar")
    label(t, t.track("text", "Título"), "PRIMERA PARADA", 0.5, 4.1, Box(60, 290, 960, 60), "Montserrat", 38,
          "#4CC9F0", weight=700, spacing=8, anim_in=tanim("fade", duration=0.5), name="Etiqueta")
    t.photo(t.track("video", "Foto"), "y5-street-08", 4.6, 4.4, t.full, kb(4.4, 1.12, 1.0), label="Foto del lugar")
    shade_bottom(t, 600, 0.75, 4.6, 4.4)
    flash(t, 4.55, 0.35, peak=0.9)
    label(t, t.track("text", "Rótulo"), "📍 Barrio Alto · 10:24", 4.9, 4.1, Box(60, 1660, 960, 90), "Montserrat", 52,
          "#FFFFFF", weight=800, align="left", anim_in=tanim("slide-right", duration=0.4, distance=0.2),
          name="Rótulo")
    song(t, "upbeat", 7)
    return t


def vlog_gastos():
    t = T(12, "yt-vlog-gastos", "¿Cuánto gasté en un día?", "How much I spent in a day",
          V + ["gastos", "budget", "presupuesto", "precios"], 10.0, w=True, thumb_at=7.6, background="#F2E8DA")
    bg(t, "#F2E8DA")
    t.photo(t.track("video", "Foto"), "y5-outfit-01", 0, 10, Box(0, 0, 900, 1080), kb(10, 1.0, 1.08),
            label="Tu foto")
    label(t, t.track("text", "Título"), "¿Cuánto gasté\nen un día?", 0.3, 9.7, Box(40, 720, 840, 300), "Archivo Black",
          96, "#FFFFFF", weight=400, align="left", line=1.0,
          layers=[shadow("#000000", 0, 6, 24, 0.6), fill("#FFFFFF")],
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1), name="Título")
    rc = Box(1060, 60, 720, 960)
    m = [(0, {"dy": -1100}, "out"), (0.9, {})]
    t.solid(t.track("shape", "Ticket"), "#FFFFFF", 0.2, 9.8, rc, m, rotation=keys([(0, 2)]),
            layers=[shadow("#5A4632", 0, 14, 30, 0.25), fill("#FFFFFF"), no_stroke()])
    tx = t.track("text", "Ticket")
    label(t, tx, "— TICKET DEL DÍA —", 0.2, 9.8, Box(1100, 100, 640, 60), "VT323", 54, "#222222", weight=400,
          motion=m, rotation=keys([(0, 2)]), name="Cabecera")
    rows = [("Desayuno", "6,50"), ("Tranvía (día)", "7,00"), ("Museo", "15,00"), ("Almuerzo", "12,00"),
            ("Helado", "3,50")]
    for i, (a, b) in enumerate(rows):
        at = 1.4 + i * 0.7
        y = 210 + i * 100
        cx, cy = gplace(rc.cx, rc.cy, 2, 0, y + 35 - rc.cy)
        label(t, t.track("text", "Fila"), f"{a}", at, 10 - at, centered(cx - 60, cy, 520, 70), "VT323", 58, "#222222",
              weight=400, align="left", rotation=keys([(0, 2)]), anim_in=tanim("typewriter", duration=0.4),
              name=f"Concepto {i + 1}")
        label(t, t.track("text", "Fila"), f"$ {b}", at + 0.2, 9.8 - at, centered(cx + 190, cy, 260, 70), "VT323", 58,
              "#222222", weight=400, align="right", rotation=keys([(0, 2)]), anim_in=tanim("fade", duration=0.2),
              name=f"Precio {i + 1}")
    cx, cy = gplace(rc.cx, rc.cy, 2, 0, 740 - rc.cy)
    label(t, t.track("text", "Corte"), "--------------------------", 5.0, 5.0, centered(cx, cy, 640, 50), "VT323", 54,
          "#888888", weight=400, rotation=keys([(0, 2)]), editable=False)
    cx, cy = gplace(rc.cx, rc.cy, 2, 0, 830 - rc.cy)
    highlight(t, "#FFD23F", 5.6, centered(cx, cy, 620, 96), rotation=keys([(0, 2)]))
    label(t, t.track("text", "Total"), "TOTAL      $ 44,00", 5.4, 4.6, centered(cx, cy, 640, 90), "VT323", 84,
          "#111111", weight=400, rotation=keys([(0, 2)]), anim_in=tanim("stamp", duration=0.3), name="Total")
    song(t, "jazz", 1)
    return t


def vlog_llegando():
    t = T(13, "yt-vlog-llegando", "Llegando a la ciudad", "Arriving in the city",
          V + ["llegada", "arrival", "gps", "distancia"], 8.0, thumb_at=6.4)
    photo_bg(t, "y5-street-07", s1=1.12, label="Foto de llegada")
    shade_full(t, 0.35, colour="#0B132B")
    shade_bottom(t, 900, 0.7, colour="#0B132B")
    label(t, t.track("text", "Llegando"), "Llegando a", 0.2, 7.8, Box(60, 180, 960, 100), "Montserrat", 64, "#FFFFFF",
          weight=600, anim_in=tanim("fade", duration=0.4), name="Llegando a")
    label(t, t.track("text", "Ciudad"), "SEÚL", 0.4, 7.6, Box(40, 270, 1000, 330), "Bebas Neue", 320, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 8, 30, 0.5), fill("#FFFFFF")],
          anim_in=tanim("zoom-out", duration=0.6), name="Ciudad")
    for k in range(3):
        ring(t, t.track("shape", "Pulso"), "#5BC0BE", 6, 0.6 + k * 0.6, 7.4 - k * 0.6, centered(540, 1300, 220, 220),
             [(0, {"s": 0.4}, "out"), (1.8, {"s": 2.6})],
             opacity=keys([(0, 0.0, "hold"), (0.01, 0.9), (1.8, 0.0)]))
    t.solid(t.track("shape", "Punto"), "#5BC0BE", 0.4, 7.6, centered(540, 1300, 70, 70), pop(0, 0.4), kind="ellipse",
            layers=[glow("#5BC0BE", 30, 0.9), fill("#5BC0BE"), stroke(6, "#FFFFFF")])
    vals = [f"{v:.1f} km".replace(".", ",") for v in [12.4 * (1 - k / 24) ** 2 for k in range(24)]] + ["0 km"]
    counting(t, vals, 0.8, 0.18, Box(40, 1480, 1000, 160),
             text_style("Barlow Condensed", 140, [fill("#FFFFFF")], weight=700), "Distancia", end=5.5)
    label(t, t.track("text", "Llegamos"), "¡LLEGAMOS!", 5.5, 2.5, Box(40, 1470, 1000, 180), "Bebas Neue", 190,
          "#0B132B", weight=400, box_bg=("#5BC0BE", 1.0), box_pad=24, box_radius=20,
          anim_in=tanim("stamp", duration=0.3), name="Llegamos")
    t.adjust([effect("beat_shake", animated={"amount": spike([5.5], 0.8, 0.35)}, rotation=0.3)], name="Golpe")
    song(t, "epic", 3)
    return t


def vlog_top3():
    t = T(14, "yt-vlog-top3", "3 lugares imperdibles", "3 must-see places",
          V + ["top 3", "lugares", "places", "guía"], 12.0, thumb_at=9.6, background="#FFF8E7")
    bg(t, "#FFF8E7")
    highlight(t, "#FFB703", 0.9, centered(540, 1130, 560, 80), end=2.1)
    label(t, t.track("text", "Intro"), "3 lugares\nque no te\npuedes\nperder", 0.1, 2.0, Box(40, 560, 1000, 600),
          "Archivo Black", 124, "#1B1B1B", weight=400, line=1.0, anim_in=tanim("rise-by-word", duration=0.4,
          unit="word", stagger=0.08), anim_out=tanim("fade", duration=0.2), name="Título")
    places = [("1", "La plaza vieja", "Ve temprano: sin filas", "y5-street-07"),
              ("2", "El mercado", "Prueba el pan de la esquina", "y5-outfit-05"),
              ("3", "El mirador", "Sube al atardecer", "city-04")]
    vt = t.track("video", "Lugares")
    for i, (n, name, tip, s) in enumerate(places):
        a = 2.0 + i * 3.33
        d = 3.33 if i < 2 else 12 - a
        t.photo(vt, s, a, d, t.full, kb(d, 1.1, 1.0), label=f"Lugar {n}")
        label(t, t.track("text", "Número"), n, a, d, Box(40, 120, 500, 520), "Archivo Black", 460, "#FFB703",
              weight=400, align="left", layers=[shadow("#000000", 0, 12, 0, 0.9), stroke(12, "#1B1B1B"),
                                                fill("#FFB703")],
              anim_in=tanim("stamp", duration=0.3), editable=False)
        label(t, t.track("text", "Nombre"), name, a + 0.2, d - 0.2, Box(60, 1500, 960, 110), "Archivo Black", 84,
              "#1B1B1B", weight=400, align="left", box_bg=("#FFFFFF", 1.0), box_pad=20, box_radius=10,
              anim_in=tanim("slide-right", duration=0.35, distance=0.2), name=f"Lugar {n}")
        label(t, t.track("text", "Consejo"), tip, a + 0.4, d - 0.4, Box(60, 1650, 960, 80), "Montserrat", 46,
              "#1B1B1B", weight=700, align="left", box_bg=("#FFB703", 1.0), box_pad=14, box_radius=10,
              anim_in=tanim("fade", duration=0.3), name=f"Consejo {n}")
    song(t, "upbeat", 5, 0.8)
    return t


def vlog_metro():
    t = T(15, "yt-vlog-metro", "Ruta en metro", "Metro ride", V + ["metro", "subway", "transporte", "estaciones"],
          12.0, w=True, thumb_at=7.3, background="#FFFFFF")
    st = [("Puerto", "y5-h-street-08"), ("Plaza Mayor", "y5-h-street-03"), ("Catedral", "y5-h-street-04"),
          ("Mirador", "y5-h-skyline-04")]
    xs = [260, 740, 1220, 1700]
    arrive = [0.0, 3.0, 6.0, 9.0]
    vt = t.track("video", "Estaciones")
    for i, (name, s) in enumerate(st):
        d = 3.0 if i < 3 else 3.0
        t.photo(vt, s, arrive[i], d, Box(0, 0, 1920, 760), kb(d, 1.0, 1.06), label=f"Estación {i + 1}")
    shade_bottom(t, 300, 0.6, colour="#000000")
    t.solid(t.track("shape", "Banda"), "#FFFFFF", 0, 12, Box(0, 760, 1920, 320))
    t.solid(t.track("shape", "Línea"), "#2B9348", 0, 12, Box(xs[0], 856, xs[-1] - xs[0], 16), radius=8,
            kind="rounded-rectangle")
    for i, x in enumerate(xs):
        t.solid(t.track("shape", "Estación"), "#FFFFFF", 0, 12, centered(x, 864, 52, 52), kind="ellipse",
                layers=[fill("#FFFFFF"), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 9,
                                          "strokeAlign": "inside", "paint": {"kind": "solid", "color": "#ff2b9348"},
                                          "opacity": 1.0}])
        op = keys([(0, 0.45, "hold"), (arrive[i], 0.45, "smooth"), (arrive[i] + 0.3, 1.0)]) if i else const_one()
        label(t, t.track("text", "Estación"), st[i][0], 0, 12, centered(x, 950, 440, 70), "Montserrat", 40, "#1B1B1B",
              weight=800, opacity=op, name=f"Estación {i + 1}")
    # the train: holds at each station, then moves on
    pts = []
    for i, x in enumerate(xs):
        dx = x - xs[0]
        pts.append((arrive[i], {"dx": dx}, "hold" if i == len(xs) - 1 else "hold"))
        if i < len(xs) - 1:
            pts.append((arrive[i + 1] - 1.0, {"dx": dx}, "inout"))
    pts = sorted(pts, key=lambda p: p[0])
    t.solid(t.track("shape", "Tren"), "#FFD60A", 0, 12, centered(xs[0], 864, 90, 44), pts, radius=22,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 4, 10, 0.3), fill("#FFD60A"), stroke(4, "#1B1B1B")])
    t.solid(t.track("shape", "Badge"), "#2B9348", 0, 12, centered(110, 864, 110, 110), kind="ellipse")
    label(t, t.track("text", "Badge"), "L2", 0, 12, centered(110, 864, 110, 110), "Montserrat", 50, "#FFFFFF",
          weight=900, name="Línea")
    tt = t.track("text", "Próxima")
    for i, (name, _) in enumerate(st):
        label(t, tt, f"ESTACIÓN · {name.upper()}", arrive[i] + 0.2, 2.8, Box(60, 640, 1400, 90), "Montserrat", 44,
              "#FFFFFF", weight=800, align="left", spacing=4, anim_in=tanim("slide-right", duration=0.35,
              distance=0.15), name=f"Rótulo {i + 1}")
    song(t, "upbeat", 2)
    return t


def const_one():
    return keys([(0, 1.0)])


def vlog_clima():
    t = T(16, "yt-vlog-clima", "Clima y hora del día", "Weather and time",
          V + ["clima", "weather", "hora", "widget"], 9.0, thumb_at=4.2)
    slides(t, ["y5-street-01", "y5-outfit-06", "y5-street-08"], 0, 3.0, transition="crossfade", tdur=0.6,
           kb_amount=0.07, labels=["Toma 1", "Toma 2", "Toma 3"])
    shade_top(t, 900, 0.5)
    card = Box(70, 140, 940, 460)
    rrect(t, t.track("shape", "Widget"), "#FFFFFF", 0.3, 8.7, card, 56, pop(0, 0.5, 0.7),
          layers=[shadow("#000000", 0, 16, 40, 0.25), fill("#FFFFFF", 0.22), stroke(2, "#FFFFFF", 0.5)])
    label(t, t.track("text", "Ciudad"), "Buenos Aires", 0.6, 8.4, Box(130, 180, 620, 80), "Outfit", 58, "#FFFFFF",
          weight=700, align="left", anim_in=tanim("fade", duration=0.4), name="Ciudad")
    label(t, t.track("text", "Día"), "Día 2 · 11:30", 0.7, 8.3, Box(130, 260, 620, 60), "Outfit", 40, "#FFFFFF",
          weight=500, align="left", anim_in=tanim("fade", duration=0.4), name="Día y hora")
    label(t, t.track("text", "Temp"), "24°", 0.8, 8.2, Box(120, 320, 520, 250), "Outfit", 230, "#FFFFFF", weight=300,
          align="left", anim_in=tanim("rise", duration=0.5), name="Temperatura")
    emoji(t, "☀️", 0.9, 8.1, centered(830, 330, 220, 220), 170, motion=pop(0, 0.5),
          anim_loop=tanim("sway", angle=4, speed=0.4))
    label(t, t.track("text", "Estado"), "Soleado\nmáx 26° · mín 15°", 1.0, 8.0, Box(640, 450, 340, 120), "Outfit", 36,
          "#FFFFFF", weight=600, line=1.2, anim_in=tanim("fade", duration=0.4), name="Estado")
    label(t, t.track("text", "Nota"), "un paseo sin prisa", 1.6, 7.4, Box(60, 1620, 960, 140), "Caveat", 110,
          "#FFFFFF", weight=700, layers=[shadow("#000000", 0, 4, 16, 0.5), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.9), name="Nota")
    song(t, "calm", 1)
    return t


def vlog_resumen():
    t = T(17, "yt-vlog-resumen", "Resumen del viaje", "Trip recap", V + ["resumen", "recap", "collage", "fotos"],
          12.0, w=True, thumb_at=8.6, background="#F7F3EC")
    bg(t, "#F7F3EC")
    samples = ["y5-h-street-03", "y5-h-skyline-04", "y5-h-street-08", "y5-h-street-05", "y5-h-street-06",
               "y5-h-skyline-01"]
    rng = random.Random(171)
    for i, s in enumerate(samples):
        col, row = i % 3, i // 3
        cx, cy = 340 + col * 620, 290 + row * 460
        at = 0.3 + i * 0.6
        framed(t, s, at, 12 - at, centered(cx, cy, 540, 360), [(0, {"s": 1.35}, "out"), (0.4, {})], border=14,
               rotation=keys([(0, rng.uniform(-4, 4))]), label=f"Foto {i + 1}")
    at = 4.4
    rrect(t, t.track("shape", "Tarjeta"), "#1B1B1B", at, 12 - at, centered(960, 520, 900, 330), 30, pop(0, 0.5, 0.5),
          layers=[shadow("#000000", 0, 20, 40, 0.4), fill("#1B1B1B"), no_stroke()])
    label(t, t.track("text", "Título"), "Lisboa en 3 días", at + 0.2, 7.4, centered(960, 480, 860, 150),
          "DM Serif Display", 110, "#FFFFFF", weight=400, anim_in=tanim("blur-in", duration=0.6), name="Título")
    label(t, t.track("text", "Datos"), "47 km · 9 barrios · 1 tranvía amarillo", at + 0.5, 7.1,
          centered(960, 600, 860, 70), "Montserrat", 38, "#FFD166", weight=700, anim_in=tanim("fade", duration=0.5),
          name="Datos")
    label(t, t.track("text", "Cierre"), "¿a dónde vamos ahora?", 7.0, 5.0, Box(560, 960, 800, 90), "Caveat", 70,
          "#1B1B1B", weight=700, anim_in=tanim("typewriter", duration=0.8), name="Cierre")
    song(t, "upbeat", 3)
    return t


# =============================================================================================
# 2. Explicador
# =============================================================================================

PAPER = "#F4EFE4"
INK = "#1B1B1B"
HL = "#FFE14D"


def expl_por_que():
    t = T(18, "yt-expl-por-que", "¿Por qué…? (título)", "Why…? (title card)", E + ["pregunta", "question", "título"],
          7.0, w=True, thumb_at=3.6, background=PAPER)
    bg(t, PAPER)
    t.photo(t.track("video", "Foto"), "h-nature-03", 0.2, 6.8, Box(1080, 90, 760, 900),
            [(0, {"dx": 900}, "out"), (0.7, {}, "linear"), (6.8, {"s": 1.04})], label="Foto del tema")
    label(t, t.track("text", "Etiqueta"), "EXPLICADO EN 5 MINUTOS", 0.3, 6.7, Box(100, 170, 800, 60), "Montserrat", 32,
          "#FFFFFF", weight=800, spacing=4, align="left", box_bg=("#D62828", 1.0), box_pad=14, box_radius=6,
          anim_in=tanim("wipe", duration=0.4, angle=0), name="Etiqueta")
    highlight(t, HL, 1.6, Box(90, 525, 450, 130), length=0.5)
    label(t, t.track("text", "Línea 1"), "¿Por qué el cielo", 0.5, 6.5, Box(100, 320, 940, 170), "DM Serif Display", 104,
          INK, weight=400, align="left", anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1),
          name="Pregunta, línea 1")
    label(t, t.track("text", "Línea 2"), "es azul?", 0.9, 6.1, Box(100, 500, 940, 170), "DM Serif Display", 104, INK,
          weight=400, align="left", anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1),
          name="Pregunta, línea 2")
    t.solid(t.track("shape", "Flecha"), INK, 2.4, 4.6, centered(860, 820, 220, 140), pop(0, 0.4), kind="curved-arrow",
            rotation=keys([(0, -20)]))
    label(t, t.track("text", "Nota"), "(no es por el mar)", 2.6, 4.4, Box(100, 760, 700, 90), "Caveat", 70, "#D62828",
          weight=700, align="left", anim_in=tanim("typewriter", duration=0.6), name="Nota")
    grain(t, 0.1)
    song(t, "fun", 0)
    return t


def expl_resaltador():
    t = T(19, "yt-expl-resaltador", "Resaltador sobre el texto", "Highlighter over text",
          E + ["resaltador", "highlighter", "texto", "estudio"], 10.0, thumb_at=6.2, background="#FBF8F1")
    P = (540, 1150)
    def zm(box, t0=0.0):
        return zmotion(box, [(0, 1.0, "hold"), (6.6 - t0, 1.0, "inout"), (7.6 - t0, 1.55)], P)
    bx = Box(-40, -40, 1160, 2000)
    t.solid(t.track("shape", "Papel"), "#FBF8F1", 0, 10, bx, zm(bx))
    pb = centered(540, 380, 620, 440)
    t.solid(t.track("shape", "Marco"), "#FFFFFF", 0.2, 9.8, centered(540, 380, 660, 480), zm(centered(540, 380, 660, 480), 0.2),
            rotation=keys([(0, -3)]), layers=[shadow("#000000", 0, 10, 24, 0.25), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Foto"), "y5-bee-02", 0.2, 9.8, pb, zm(pb, 0.2), rotation=keys([(0, -3)]), label="Foto del tema")
    tb = centered(540, 160, 200, 50)
    t.solid(t.track("shape", "Cinta"), "#F4A261", 0.2, 9.8, tb, zm(tb, 0.2), rotation=keys([(0, 4)]), alpha=0.75)
    lines = ["Las abejas visitan", "hasta 5.000 flores al día", "y se comunican", "con un baile en zigzag",
             "que indica dónde está", "el néctar."]
    marks = {1: (1.6, round(0.46 * 76 * len(lines[1])) + 30), 3: (3.2, round(0.46 * 76 * len(lines[3])) + 30)}
    y0 = 760
    for i, txt in enumerate(lines):
        y = y0 + i * 130
        if i in marks:
            at, w = marks[i]
            hb = Box(70, y + 18, w, 100)
            highlight(t, HL, at, hb, motion=[(0, {"sx": 0.0, "dx": -w / 2}, "out"), (0.5, {}, "hold"),
                                              (6.6 - at, {}, "inout"),
                                              (7.6 - at, {"s": 1.55, "dx": 0.55 * (hb.cx - P[0]),
                                                          "dy": 0.55 * (hb.cy - P[1])})])
        b = Box(80, y, 940, 130)
        label(t, t.track("text", f"Línea {i + 1}"), txt, 0.4 + i * 0.12, 9.6 - i * 0.12, b, "Lora", 76, INK,
              weight=500, align="left", motion=zm(b, 0.4 + i * 0.12), anim_in=tanim("fade", duration=0.3), name=f"Línea {i + 1}")
    ub = Box(80, y0 + 5 * 130 + 110, 330, 12)
    line(t, t.track("shape", "Subrayado"), "#D62828", 4.6, 2.0, ub, grow="x", length=0.4,
         opacity=keys([(0, 1.0, "hold"), (1.8, 1.0, "smooth"), (2.0, 0.0)]))
    nb = Box(640, y0 + 6 * 130 - 10, 400, 110)
    label(t, t.track("text", "Nota"), "¡esto!", 5.0, 1.6, nb, "Caveat", 90, "#D62828", weight=700,
          rotation=keys([(0, -8)]), anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Nota")
    label(t, t.track("text", "Título"), "DATO DEL DÍA", 0.2, 9.8, Box(60, 640, 960, 70), "Montserrat", 40, "#D62828",
          weight=800, spacing=8, align="left", motion=zm(Box(60, 640, 960, 70), 0.2), name="Etiqueta")
    song(t, "calm", 2)
    return t


def _clipping(t, cx, cy, ang, w, h, at, sample, head, date, slot_label, drop=True, end=None):
    end = t.duration if end is None else end
    d = end - at
    m = [(0, {"s": 1.3, "dy": -160}, "out"), (0.45, {})] if drop else None
    op = keys([(0, 0.0), (0.12, 1.0)])
    t.solid(t.track("shape", "Recorte"), "#F3EBDA", at, d, centered(cx, cy, w, h), m, rotation=keys([(0, ang)]),
            layers=[shadow("#000000", 4, 14, 26, 0.45), fill("#F3EBDA"), no_stroke()], opacity=op)
    def put_box(ox, oy, bw, bh):
        x, y = gplace(cx, cy, ang, ox, oy)
        return centered(x, y, bw, bh)
    label(t, t.track("text", "Recorte"), date, at, d, put_box(0, -h / 2 + 34, w - 60, 40), "Libre Baskerville", 22,
          "#6B5E4A", weight=400, motion=m, rotation=keys([(0, ang)]), opacity=op, name="Fecha", editable=False)
    t.solid(t.track("shape", "Recorte"), "#3A332A", at, d, put_box(0, -h / 2 + 58, w - 60, 3), m,
            rotation=keys([(0, ang)]), opacity=op)
    label(t, t.track("text", "Titular"), head, at, d, put_box(0, -h / 2 + 150, w - 60, 170), "Playfair Display", 52,
          "#1B1B1B", weight=900, line=1.0, motion=m, rotation=keys([(0, ang)]), opacity=op, name="Titular")
    ph = h - 300 - 90
    t.photo(t.track("video", "Recorte"), sample, at, d, put_box(0, -h / 2 + 250 + ph / 2, w - 60, ph), m,
            rotation=keys([(0, ang)]), label=slot_label, opacity=op,
            effects=[effect("color.basic", saturation=-0.75, contrast=0.2)])
    for k in range(2):
        t.solid(t.track("shape", "Recorte"), "#9C9078", at, d, put_box(-20 * k, h / 2 - 60 + k * 26, w - 60 - 40 * k, 8),
                m, rotation=keys([(0, ang)]), opacity=op)


def expl_recortes():
    t = T(20, "yt-expl-recortes", "Recortes de periódico", "Newspaper clippings",
          E + ["periódico", "newspaper", "noticias", "documental"], 10.0, w=True, thumb_at=7.6, background="#2E2622")
    bg(t, "#2E2622")
    t.adjust([effect("stylize.vignette", amount=0.6)], name="Viñeta")
    _clipping(t, 420, 560, -6, 600, 820, 0.4, "y5-h-ocean-02", "La ciudad que se hunde\n2 cm cada año",
              "MARTES 12 DE MARZO", "Foto del recorte 1")
    _clipping(t, 980, 520, 3, 600, 820, 1.6, "y5-h-lab-02", "Los científicos\nexplican por qué",
              "JUEVES 21 DE MARZO", "Foto del recorte 2")
    _clipping(t, 1520, 580, -2, 600, 820, 2.8, "y5-h-forest-01", "¿Qué podemos hacer\nahora?",
              "LUNES 8 DE ABRIL", "Foto del recorte 3")
    x, y = gplace(980, 520, 3, 0, -410 + 150)
    t.solid(t.track("shape", "Círculo"), "#D62828", 4.6, 5.4, centered(x, y, 620, 230),
            [(0, {"s": 1.4}, "snap"), (0.3, {})], kind="ellipse", layers=hollow_ring("#D62828", 9),
            rotation=keys([(0, -4)]), opacity=keys([(0, 0.0), (0.1, 1.0)]))
    label(t, t.track("text", "Nota"), "¿y nadie lo vio venir?", 5.2, 4.8, Box(560, 8, 800, 90), "Permanent Marker", 50,
          "#FFE14D", weight=400, rotation=keys([(0, -3)]), anim_in=tanim("typewriter", duration=0.7), name="Nota")
    label(t, t.track("text", "Título"), "LO QUE DIJERON LOS PERIÓDICOS", 0.2, 9.8, Box(60, 990, 1200, 60), "Montserrat",
          34, "#FFFFFF", weight=800, spacing=6, align="left", box_bg=("#D62828", 1.0), box_pad=12, name="Etiqueta")
    song(t, "suspense", 0, 0.7)
    return t


def expl_mapa_zoom():
    t = T(21, "yt-expl-mapa-zoom", "Mapa con zoom: ¿dónde queda?", "Map zoom: where is it?",
          E + ["mapa", "map", "zoom", "geografía"], 9.0, w=True, thumb_at=5.6, background="#123A5A")
    P = (1240, 430)
    zoom = [(0, 1.0, "hold"), (0.7, 1.0, "inout"), (2.6, 1.7, "linear"), (9.0, 1.8)]
    def zb(box, colour, kind="cloud", alpha=1.0, layers=None):
        t.solid(t.track("shape", "Mapa"), colour, 0, 9, box, zmotion(box, zoom, P), kind=kind, alpha=alpha,
                layers=layers)
    zb(Box(-60, -60, 2040, 1200), "#123A5A", "rectangle")
    for k in range(1, 6):  # latitude / longitude lines
        zb(Box(-60, k * 180, 2040, 2), "#FFFFFF", "rectangle", alpha=0.12)
    for k in range(1, 10):
        zb(Box(k * 192, -60, 2, 1200), "#FFFFFF", "rectangle", alpha=0.12)
    land, coast = "#E9D8A6", "#F7EBCB"
    # made-up continents: clusters of ellipses, a pale coast ring drawn first
    masses = [[(330, 300, 420, 260), (250, 420, 260, 220), (430, 420, 220, 200), (470, 230, 200, 150)],
              [(520, 640, 200, 260), (560, 790, 160, 220), (500, 880, 110, 140)],
              [(1120, 300, 520, 240), (1000, 380, 240, 200), (1300, 240, 260, 180), (1220, 450, 260, 200)],
              [(1200, 650, 240, 300), (1260, 800, 160, 200)],
              [(1620, 430, 300, 220), (1720, 520, 200, 160)],
              [(1680, 820, 220, 130)]]
    for pad, colour in ((26, coast), (0, land)):
        for mass in masses:
            for (x, y, w, h) in mass:
                zb(centered(x, y, w + pad, h + pad), colour, "ellipse")
    pin(t, P[0], P[1], 2.7, "#D62828", 110)
    ring(t, t.track("shape", "Pulso"), "#D62828", 6, 3.0, 2.0, centered(P[0], P[1], 160, 160),
         [(0, {"s": 0.4}, "out"), (1.0, {"s": 2.0})], opacity=keys([(0, 0.9), (1.0, 0.0)]))
    label(t, t.track("text", "Aquí"), "Aquí empieza todo", 3.0, 6.0, centered(P[0], P[1] + 100, 560, 80), "Montserrat",
          44, "#FFFFFF", weight=800, box_bg=("#D62828", 1.0), box_pad=14, box_radius=8,
          anim_in=tanim("pop", duration=0.35), name="Etiqueta del mapa")
    pb = Box(100, 300, 640, 500)
    rrect(t, t.track("shape", "Ventana"), "#FFFFFF", 4.0, 5.0, Box(84, 284, 672, 600), 16,
          [(0, {"dx": -900}, "out"), (0.6, {})], layers=[shadow("#000000", 0, 16, 30, 0.4), fill("#FFFFFF"),
                                                          no_stroke()])
    t.photo(t.track("video", "Foto"), "y5-h-volcano-03", 4.0, 5.0, pb, [(0, {"dx": -900}, "out"), (0.6, {})],
            label="Foto del lugar")
    label(t, t.track("text", "Pie"), "Un volcán activo en medio del océano", 4.2, 4.8, Box(100, 806, 640, 70),
          "Montserrat", 28, INK, weight=700, motion=[(0, {"dx": -900}, "out"), (0.6, {})], name="Pie de foto")
    label(t, t.track("text", "Título"), "¿Dónde queda?", 0.2, 8.8, Box(60, 40, 900, 120), "Archivo Black", 80, "#FFFFFF",
          weight=400, align="left", layers=[shadow("#000000", 0, 6, 0, 0.6), fill("#FFFFFF")],
          anim_in=tanim("rise", duration=0.4), name="Título")
    song(t, "suspense", 1, 0.7)
    return t


def expl_datos():
    t = T(22, "yt-expl-datos", "Datos que aparecen", "Facts that appear", E + ["datos", "facts", "números", "ciencia"],
          10.0, w=True, thumb_at=1.9)
    photo_bg(t, "y5-h-ocean-02", s1=1.1, label="Foto del tema")
    t.solid(t.track("shape", "Sombra"), "#000000", 0, 10, Box(0, 0, 1300, 1080),
            layers=[gradient([(0, "#06121F", 0.92), (0.7, "#06121F", 0.6), (1, "#06121F", 0.0)], angle=0),
                    no_stroke()])
    facts = [("71 %", "de la superficie de la Tierra\nestá cubierta de agua"), ("97 %", "de toda esa agua\nes salada"),
             ("1 %", "es agua dulce que\npodemos usar")]
    nt, st, kt = t.track("text", "Número"), t.track("text", "Dato"), t.track("text", "Paso")
    for i, (num, txt) in enumerate(facts):
        a = 0.3 + i * 3.25
        d = 3.25 if i < 2 else 10 - a
        label(t, nt, num, a, d, Box(110, 220, 1100, 360), "Anton", 320, "#7FDBFF", weight=400, align="left",
              layers=[glow("#7FDBFF", 24, 0.5), fill("#E6FAFF")], anim_in=tanim("stamp", duration=0.3),
              anim_out=tanim("fade", duration=0.2) if i < 2 else None, name=f"Número {i + 1}")
        label(t, st, txt, a + 0.25, d - 0.25, Box(120, 600, 1100, 200), "Montserrat", 60, "#FFFFFF", weight=700,
              align="left", line=1.1, anim_in=tanim("fade-up-char", duration=0.5, unit="word", stagger=0.05),
              anim_out=tanim("fade", duration=0.2) if i < 2 else None, name=f"Dato {i + 1}")
        label(t, kt, f"DATO {i + 1} / 3", a, d, Box(120, 140, 600, 60), "Montserrat", 34, "#7FDBFF", weight=800,
              spacing=6, align="left", editable=False)
    label(t, t.track("text", "Fuente"), "Cifras aproximadas", 0.3, 9.7, Box(120, 960, 800, 50), "Montserrat", 28,
          "#9FB3C8", weight=500, align="left", name="Fuente")
    song(t, "calm", 3)
    return t


def expl_puntos():
    t = T(23, "yt-expl-puntos", "Puntos numerados", "Numbered points",
          E + ["lista", "list", "puntos", "consejos"], 12.0, thumb_at=9.0, background="#111827")
    bg(t, "#111827")
    t.photo(t.track("video", "Foto"), "y5-sci-01", 0, 12, Box(0, 0, 1080, 760), kb(12, 1.0, 1.08), label="Foto del tema")
    t.solid(t.track("shape", "Fundido"), "#111827", 0, 12, Box(0, 400, 1080, 360),
            layers=[gradient([(0, "#111827", 0.0), (1, "#111827", 1.0)], angle=90), no_stroke()])
    label(t, t.track("text", "Título"), "3 cosas que debes saber", 0.3, 11.7, Box(60, 660, 960, 120), "Sora", 66,
          "#FFFFFF", weight=800, align="left", anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1),
          name="Título")
    pts = [("Mezclar no siempre es seguro", "Algunos productos reaccionan entre sí.", "#F72585"),
           ("La temperatura importa", "El calor acelera casi todas las reacciones.", "#4CC9F0"),
           ("Lee siempre la etiqueta", "Ahí está todo lo que necesitas saber.", "#FFD60A")]
    for i, (h, s, c) in enumerate(pts):
        at = 1.6 + i * 2.6
        y = 830 + i * 330
        m = [(0, {"dx": 1100}, "out"), (0.5, {})]
        op = keys([(0, 1.0, "hold"), (2.6, 1.0, "smooth"), (2.9, 0.55)]) if i < 2 else const_one()
        rrect(t, t.track("shape", "Tarjeta"), "#1F2937", at, 12 - at, Box(60, y, 960, 290), 28, m,
              layers=[fill("#1F2937"), stroke(3, c, 0.8)], opacity=op)
        t.solid(t.track("shape", "Número"), c, at, 12 - at, centered(170, y + 145, 150, 150), m, kind="ellipse",
                opacity=op)
        label(t, t.track("text", "Número"), str(i + 1), at, 12 - at, centered(170, y + 145, 150, 150), "Sora", 96,
              "#111827", weight=800, motion=m, editable=False, opacity=op)
        label(t, t.track("text", "Punto"), h, at + 0.1, 11.9 - at, Box(280, y + 40, 710, 110), "Sora", 50, "#FFFFFF",
              weight=700, align="left", motion=m, opacity=op, name=f"Punto {i + 1}")
        label(t, t.track("text", "Detalle"), s, at + 0.1, 11.9 - at, Box(280, y + 150, 710, 110), "Sora", 36,
              "#CBD5E1", weight=400, align="left", motion=m, opacity=op, name=f"Detalle {i + 1}")
    song(t, "electro", 1, 0.7)
    return t


def expl_barras():
    t = T(24, "yt-expl-barras", "Gráfico de barras", "Bar chart", E + ["gráfico", "chart", "barras", "datos"], 10.0,
          w=True, thumb_at=6.8, background="#FFFFFF")
    bg(t, "#FFFFFF")
    label(t, t.track("text", "Título"), "¿Cuántas horas necesitamos dormir?", 0.2, 9.8, Box(100, 60, 1400, 110),
          "Sora", 64, INK, weight=800, align="left", anim_in=tanim("fade", duration=0.4), name="Título")
    label(t, t.track("text", "Sub"), "Horas recomendadas por noche, según la edad", 0.4, 9.6, Box(100, 160, 1400, 60),
          "Sora", 34, "#6B7280", weight=400, align="left", name="Subtítulo")
    base = 900
    t.solid(t.track("shape", "Eje"), INK, 0.4, 9.6, Box(100, base, 1350, 4))
    data = [("Bebés", 14), ("Niños", 11), ("Adolescentes", 9), ("Adultos", 8), ("Mayores", 7)]
    for k in range(1, 4):
        t.solid(t.track("shape", "Guía"), "#E5E7EB", 0.4, 9.6, Box(100, base - k * 160, 1350, 2))
    for i, (name, h) in enumerate(data):
        x = 160 + i * 260
        hh = h * 40
        at = 1.0 + i * 0.35
        c = "#3B82F6" if i != 2 else "#F97316"
        bar_up(t, c, at, Box(x, base - hh, 180, hh))
        label(t, t.track("text", "Valor"), f"{h} h", at + 0.6, 9.4 - at, centered(x + 90, base - hh - 50, 240, 70),
              "Sora", 48, INK, weight=800, anim_in=tanim("pop", duration=0.3), name=f"Valor {i + 1}")
        label(t, t.track("text", "Grupo"), name, at, 10 - at, centered(x + 90, base + 50, 260, 60), "Sora", 32,
              "#374151", weight=600, name=f"Grupo {i + 1}")
    t.solid(t.track("shape", "Marca"), "#F97316", 4.2, 5.8, centered(160 + 2 * 260 + 90, base - 9 * 40 - 50, 300, 130),
            [(0, {"s": 1.4}, "snap"), (0.3, {})], kind="ellipse", layers=hollow_ring("#F97316", 6),
            opacity=keys([(0, 0.0), (0.1, 1.0)]))
    label(t, t.track("text", "Nota"), "¡y casi nadie llega!", 4.6, 5.4, Box(560, 300, 600, 90), "Caveat", 72,
          "#F97316", weight=700, rotation=keys([(0, -5)]), anim_in=tanim("typewriter", duration=0.6), name="Nota")
    circle_photo(t, "h-portrait-02", 0.6, 9.4, centered(1690, 620, 300, 300), pop(0, 0.5), ring_colour="#3B82F6",
                 ring_width=10, label="Tu cara")
    song(t, "fun", 2, 0.7)
    return t


def expl_dona():
    t = T(25, "yt-expl-dona", "Gráfico de porcentaje", "Percentage donut", E + ["porcentaje", "percent", "gráfico",
          "dato"], 9.0, thumb_at=5.0, background="#0F172A")
    bg(t, "#0F172A")
    t.photo(t.track("video", "Foto"), "selfie-04", 0, 9, Box(0, 0, 1080, 700), kb(9, 1.0, 1.06), label="Foto del tema")
    t.solid(t.track("shape", "Fundido"), "#0F172A", 0, 9, Box(0, 300, 1080, 400),
            layers=[gradient([(0, "#0F172A", 0.0), (1, "#0F172A", 1.0)], angle=90), no_stroke()])
    box = centered(540, 1090, 560, 560)
    t.solid(t.track("shape", "Fondo del gráfico"), "#1E293B", 0.4, 8.6, box, kind="ellipse",
            layers=hollow_ring("#1E293B", 56))
    donut(t, "#22D3EE", 56, 0.6, 2.2, 0.68, box)
    vals = [f"{round(68 * (1 - (1 - k / 14) ** 2))} %" for k in range(14)] + ["68 %"]
    counting(t, vals, 0.6, 0.15, centered(540, 1090, 460, 200),
             text_style("Sora", 150, [fill("#FFFFFF")], weight=800), "Porcentaje")
    label(t, t.track("text", "Dato"), "de las personas mira el celular\nantes de levantarse", 2.6, 6.4,
          Box(60, 1450, 960, 180), "Sora", 54, "#FFFFFF", weight=600, line=1.15,
          anim_in=tanim("fade-up-char", duration=0.5, unit="word", stagger=0.05), name="Dato")
    label(t, t.track("text", "Pregunta"), "¿Tú también?", 3.8, 5.2, Box(60, 1680, 960, 110), "Caveat", 96, "#22D3EE",
          weight=700, anim_in=tanim("pop", duration=0.4), name="Pregunta")
    song(t, "electro", 3, 0.7)
    return t


def expl_linea_tiempo():
    t = T(26, "yt-expl-linea-tiempo", "Línea de tiempo histórica", "History timeline",
          E + ["historia", "history", "línea de tiempo", "timeline"], 12.0, w=True, thumb_at=8.3)
    eras = [("3000 a. C.", "Primeras ciudades", "y5-h-ruins-02"), ("500 a. C.", "Templos de piedra", "y5-h-ruins-01"),
            ("1200", "Grandes catedrales", "y5-h-street-06"), ("HOY", "Ciudades de vidrio", "y5-h-skyline-04")]
    vt = t.track("video", "Épocas")
    for i, (_, _, s) in enumerate(eras):
        t.photo(vt, s, i * 3.0, 3.0, t.full, kb(3.0, 1.0, 1.07), label=f"Época {i + 1}",
                effects=[effect("color.basic", saturation=-0.2)] if i < 3 else None)
    t.adjust([effect("stylize.sepia")], 0, 6.0, name="Sepia")
    shade_bottom(t, 560, 0.85)
    label(t, t.track("text", "Título"), "La historia en 60 segundos", 0.2, 11.8, Box(60, 50, 1400, 100),
          "Cinzel", 60, "#FFFFFF", weight=700, align="left", layers=[shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")],
          name="Título")
    xs = [260, 730, 1200, 1670]
    line(t, t.track("shape", "Línea"), "#FFFFFF", 0.2, 11.8, Box(160, 820, 1600, 6), grow="x", length=1.2)
    for i, (year, txt, _) in enumerate(eras):
        a = i * 3.0 + 0.2
        t.solid(t.track("shape", "Hito"), "#FFFFFF", a, 12 - a, centered(xs[i], 823, 40, 40), pop(0, 0.4), kind="ellipse",
                layers=[fill("#F4A261"), stroke(6, "#FFFFFF")])
        label(t, t.track("text", "Año"), year, a, 12 - a, centered(xs[i], 750, 440, 100), "Cinzel", 64, "#F4A261",
              weight=800, anim_in=tanim("rise", duration=0.4), name=f"Año {i + 1}")
        label(t, t.track("text", "Hito"), txt, a + 0.15, 11.85 - a, centered(xs[i], 900, 440, 70), "Montserrat", 36,
              "#FFFFFF", weight=600, anim_in=tanim("fade", duration=0.4), name=f"Hito {i + 1}")
    t.solid(t.track("shape", "Ahora"), "#F4A261", 0, 12, centered(xs[0], 823, 90, 90),
            [(0, {}, "hold"), (2.8, {}, "inout"), (3.2, {"dx": xs[1] - xs[0]}, "hold"), (5.8, {"dx": xs[1] - xs[0]},
             "inout"), (6.2, {"dx": xs[2] - xs[0]}, "hold"), (8.8, {"dx": xs[2] - xs[0]}, "inout"),
             (9.2, {"dx": xs[3] - xs[0]})], kind="ellipse", layers=hollow_ring("#F4A261", 6))
    song(t, "epic", 4, 0.7)
    return t


def expl_pizarra():
    t = T(27, "yt-expl-pizarra", "Pizarra con tiza", "Chalkboard", E + ["pizarra", "chalkboard", "clase", "fórmula"],
          10.0, w=True, thumb_at=7.4, background="#5B3A1E")
    bg(t, "#5B3A1E")
    rrect(t, t.track("shape", "Pizarra"), "#2F4F3E", 0, 10, Box(50, 50, 1820, 980), 10,
          layers=[shadow("#000000", 0, 0, 30, 0.6), gradient([(0, "#36594A"), (1, "#26443A")], angle=120), no_stroke()])
    chalk = "#F2F2EC"
    label(t, t.track("text", "Título"), "La regla del 1 %", 0.3, 9.7, Box(130, 110, 1100, 140), "Gloria Hallelujah",
          90, chalk, weight=400, align="left", anim_in=tanim("typewriter", duration=1.0), name="Título")
    line(t, t.track("shape", "Subrayado"), chalk, 1.3, 8.7, Box(130, 250, 720, 6), grow="x", length=0.6,
         alpha=0.85)
    label(t, t.track("text", "Fórmula 1"), "1,01  ³⁶⁵  =  37,8", 2.0, 8.0, Box(160, 380, 1100, 150), "Kalam", 110,
          chalk, weight=700, align="left", anim_in=tanim("typewriter", duration=1.0), name="Fórmula 1")
    label(t, t.track("text", "Fórmula 2"), "0,99  ³⁶⁵  =  0,03", 3.6, 6.4, Box(160, 580, 1100, 150), "Kalam", 110,
          chalk, weight=700, align="left", anim_in=tanim("typewriter", duration=1.0), name="Fórmula 2")
    t.solid(t.track("shape", "Círculo"), chalk, 5.2, 4.8, centered(940, 455, 330, 170),
            [(0, {"s": 1.3}, "snap"), (0.3, {})], kind="ellipse", layers=hollow_ring("#FFE066", 7),
            rotation=keys([(0, -6)]), opacity=keys([(0, 0.0), (0.1, 1.0)]))
    t.solid(t.track("shape", "Flecha"), "#FFE066", 5.6, 4.4, centered(1220, 600, 200, 110), pop(0, 0.35),
            kind="curved-arrow", rotation=keys([(0, 160)]))
    label(t, t.track("text", "Nota"), "¡mejorar un poco\ncada día suma!", 5.8, 4.2, Box(160, 790, 1100, 180),
          "Gloria Hallelujah", 60, "#FFE066", weight=400, align="left", line=1.1,
          anim_in=tanim("typewriter", duration=1.0), name="Nota")
    t.solid(t.track("shape", "Foto"), "#FFFFFF", 0.6, 9.4, centered(1560, 470, 430, 500), pop(0, 0.4, 0.6),
            rotation=keys([(0, 5)]), layers=[shadow("#000000", 0, 10, 20, 0.4), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Foto"), "h-portrait-01", 0.6, 9.4, centered(1560, 440, 380, 390), pop(0, 0.4, 0.6),
            rotation=keys([(0, 5)]), label="Tu foto")
    t.solid(t.track("shape", "Cinta"), "#E9C46A", 0.6, 9.4, centered(1560, 225, 180, 50), pop(0, 0.4, 0.6),
            rotation=keys([(0, -4)]), alpha=0.8)
    t.adjust([effect("stylize.film_grain", amount=0.25, grainSize=2.0)], name="Tiza")
    song(t, "fun", 3, 0.7)
    return t


def expl_mito():
    t = T(28, "yt-expl-mito", "Mito o realidad", "Myth or fact", E + ["mito", "myth", "verdad", "fact"], 10.0,
          thumb_at=7.0, background="#FFFFFF")
    t.solid(t.track("shape", "Mito"), "#FFE5E5", 0, 10, Box(0, 0, 1080, 960))
    t.solid(t.track("shape", "Realidad"), "#E3F9E5", 0, 10, Box(0, 960, 1080, 960))
    label(t, t.track("text", "Mito"), "MITO", 0.2, 9.8, Box(60, 120, 960, 140), "Archivo Black", 120, "#D62828",
          weight=400, anim_in=tanim("stamp", duration=0.3), name="Etiqueta mito")
    label(t, t.track("text", "Afirmación"), "«Solo usamos el 10 %\nde nuestro cerebro»", 0.6, 9.4, Box(60, 280, 960, 260),
          "Lora", 70, INK, weight=700, italic=True, line=1.15, anim_in=tanim("fade", duration=0.5), name="Mito")
    label(t, t.track("text", "Cruz"), "✕", 2.2, 7.8, centered(940, 190, 200, 200), "Inter", 170, "#D62828",
          weight=900, anim_in=tanim("stamp", duration=0.25), editable=False)
    t.solid(t.track("shape", "Tachado"), "#D62828", 2.4, 7.6, Box(90, 400, 900, 12), [(0, {"sx": 0.0, "dx": -450},
            "out"), (0.4, {})], radius=6, kind="rounded-rectangle", rotation=keys([(0, -4)]))
    circle_photo(t, "study-02", 0.3, 9.7, centered(540, 960, 400, 400), pop(0, 0.5), ring_colour="#FFFFFF",
                 ring_width=14, label="Foto del tema")
    label(t, t.track("text", "Realidad"), "REALIDAD", 3.4, 6.6, Box(60, 1220, 960, 140), "Archivo Black", 120,
          "#2B9348", weight=400, anim_in=tanim("stamp", duration=0.3), name="Etiqueta realidad")
    label(t, t.track("text", "Explicación"), "Usamos casi todo el cerebro,\nsolo que no todo a la vez.", 3.8, 6.2,
          Box(60, 1380, 960, 220), "Lora", 64, INK, weight=600, line=1.15,
          anim_in=tanim("fade-up-char", duration=0.5, unit="word", stagger=0.05), name="Realidad")
    label(t, t.track("text", "Visto"), "✓", 4.6, 5.4, centered(985, 1290, 160, 200), "Inter", 170, "#2B9348",
          weight=900, anim_in=tanim("stamp", duration=0.25), editable=False)
    song(t, "fun", 4, 0.7)
    return t


def expl_comparar():
    t = T(29, "yt-expl-comparar", "Comparación A vs B", "A vs B comparison",
          E + ["comparación", "comparison", "versus", "tabla"], 10.0, w=True, thumb_at=7.0, background="#F8FAFC")
    bg(t, "#F8FAFC")
    for i, (s, name, c) in enumerate([("coffee-03", "Café", "#7F5539"), ("y5-cozy-03", "Té", "#2B9348")]):
        x = 120 + i * 1000
        rounded_photo(t, s, 0.2 + i * 0.3, 9.8 - i * 0.3, Box(x, 60, 680, 420), slide_in(dy=-600, length=0.6),
                      radius=0.1, label_=f"Foto {name}")
        label(t, t.track("text", "Nombre"), name, 0.4 + i * 0.3, 9.6 - i * 0.3, Box(x, 380, 680, 90), "Sora", 64,
              "#FFFFFF", weight=800, layers=[shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")],
              name=f"Opción {i + 1}")
    t.solid(t.track("shape", "VS"), "#111827", 0.9, 9.1, centered(960, 270, 170, 170), pop(0, 0.4), kind="ellipse")
    label(t, t.track("text", "VS"), "VS", 0.9, 9.1, centered(960, 270, 170, 170), "Sora", 64, "#FFFFFF", weight=800,
          motion=pop(0, 0.4), editable=False)
    rows = [("Cafeína por taza", "95 mg", "47 mg", 0), ("Antioxidantes", "Altos", "Muy altos", 1),
            ("Despierta en", "15 min", "30 min", 0), ("Calorías (solo)", "2", "2", -1)]
    for i, (k, a, b, win) in enumerate(rows):
        at = 1.6 + i * 0.9
        y = 540 + i * 120
        t.solid(t.track("shape", "Fila"), "#FFFFFF" if i % 2 else "#EEF2F7", at, 10 - at, Box(120, y, 1680, 104),
                [(0, {"sx": 0.0}, "out"), (0.35, {})], radius=16, kind="rounded-rectangle")
        label(t, t.track("text", "Fila"), k, at + 0.1, 9.9 - at, centered(960, y + 52, 560, 80), "Sora", 38, "#475569",
              weight=600, name=f"Criterio {i + 1}")
        for j, v in enumerate((a, b)):
            x = 460 + j * 1000
            col = "#2B9348" if win == j else INK
            label(t, t.track("text", "Valor"), (v + "  ✓") if win == j else v, at + 0.2, 9.8 - at,
                  centered(x, y + 52, 560, 80), "Sora", 46, col, weight=800, anim_in=tanim("pop", duration=0.3),
                  name=f"Valor {i + 1}{'AB'[j]}")
    song(t, "fun", 0, 0.7)
    return t


def expl_fuente():
    t = T(30, "yt-expl-fuente", "Lo que dice la ciencia", "What science says",
          E + ["ciencia", "science", "estudio", "fuente"], 9.0, thumb_at=5.2)
    photo_bg(t, "y5-sci-02", s1=1.1, label="Foto del tema")
    shade_full(t, 0.62, colour="#0B1D2A")
    label(t, t.track("text", "Etiqueta"), "LO QUE DICE LA CIENCIA", 0.2, 8.8, Box(60, 250, 960, 70), "Montserrat", 40,
          "#7FDBFF", weight=800, spacing=6, anim_in=tanim("fade", duration=0.4), name="Etiqueta")
    label(t, t.track("text", "Comillas"), "“", 0.4, 8.6, centered(540, 520, 300, 300), "Playfair Display", 400,
          "#7FDBFF", weight=900, editable=False, anim_in=tanim("pop", duration=0.4))
    label(t, t.track("text", "Cita"), "Caminar 20 minutos al día mejora el ánimo tanto como otros hábitos que cuestan mucho más.",
          0.8, 8.2, Box(80, 640, 920, 560), "Playfair Display", 70, "#FFFFFF", weight=600, line=1.2,
          anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.06), name="Cita")
    line(t, t.track("shape", "Subrayado"), "#7FDBFF", 3.6, 5.4, centered(540, 1235, 520, 8), grow="c", length=0.6)
    label(t, t.track("text", "Fuente"), "Fuente: estudio publicado en 2024", 4.0, 5.0, Box(80, 1280, 920, 80),
          "Montserrat", 40, "#0B1D2A", weight=700, box_bg=("#7FDBFF", 1.0), box_pad=16, box_radius=40,
          anim_in=tanim("pop", duration=0.35), name="Fuente")
    label(t, t.track("text", "Aviso"), "Resumen simplificado: lee el estudio completo", 4.4, 4.6,
          Box(80, 1400, 920, 60), "Montserrat", 30, "#B7C9D6", weight=500, name="Aviso")
    song(t, "calm", 0, 0.7)
    return t


def expl_glosario():
    t = T(31, "yt-expl-glosario", "Palabra del día (glosario)", "Word of the day (glossary)",
          E + ["definición", "definition", "glosario", "palabra"], 9.0, w=True, thumb_at=5.8, background="#FFFDF7")
    bg(t, "#FFFDF7")
    t.solid(t.track("shape", "Margen"), "#E76F51", 0, 9, Box(0, 0, 24, 1080))
    label(t, t.track("text", "Etiqueta"), "PALABRA DEL DÍA", 0.2, 8.8, Box(110, 90, 800, 60), "Montserrat", 34,
          "#FFFFFF", weight=800, spacing=6, align="left", box_bg=("#E76F51", 1.0), box_pad=12, box_radius=6,
          name="Etiqueta")
    label(t, t.track("text", "Palabra"), "algoritmo", 0.5, 8.5, Box(110, 180, 1000, 220), "Libre Baskerville", 150, INK,
          weight=700, align="left", anim_in=tanim("blur-in", duration=0.6), name="Palabra")
    label(t, t.track("text", "Fonética"), "/al·go·rit·mo/  ·  sustantivo", 1.0, 8.0, Box(110, 400, 1000, 70),
          "Libre Baskerville", 44, "#6B7280", weight=400, italic=True, align="left",
          anim_in=tanim("fade", duration=0.4), name="Fonética")
    highlight(t, HL, 3.2, Box(196, 552, 610, 62), length=0.6)
    label(t, t.track("text", "Definición"), "1.  Una lista de pasos ordenados para\n     resolver un problema o tomar una decisión.",
          1.6, 7.4, Box(110, 520, 1100, 200), "Libre Baskerville", 46, INK, weight=400, align="left", line=1.55,
          anim_in=tanim("typewriter", duration=1.6), name="Definición")
    label(t, t.track("text", "Ejemplo"), "Ej.: una receta de cocina es un algoritmo.", 4.4, 4.6, Box(110, 780, 1100, 70),
          "Caveat", 64, "#E76F51", weight=700, align="left", anim_in=tanim("typewriter", duration=0.8), name="Ejemplo")
    framed(t, "y5-h-lab-01", 0.8, 8.2, Box(1300, 230, 500, 600), [(0, {"dx": 700}, "out"), (0.6, {})], border=16,
           rotation=keys([(0, 3)]), label="Foto")
    song(t, "calm", 4, 0.7)
    return t


def expl_proceso():
    t = T(32, "yt-expl-proceso", "Paso a paso: cómo funciona", "Step by step: how it works",
          E + ["proceso", "process", "diagrama", "diagram"], 12.0, thumb_at=9.6, background="#EAF6FB")
    t.photo(t.track("video", "Foto"), "y5-h-forest-02", 0, 12, t.full, kb(12, 1.0, 1.06), label="Foto de fondo",
            opacity=keys([(0, 0.35)]))
    t.solid(t.track("shape", "Velo"), "#EAF6FB", 0, 12, alpha=0.7)
    label(t, t.track("text", "Título"), "¿Cómo funciona\nla lluvia?", 0.2, 11.8, Box(60, 120, 960, 280), "Fredoka", 104,
          "#0B4F6C", weight=700, line=1.0, anim_in=tanim("bounce", duration=0.6, unit="word", stagger=0.1),
          name="Título")
    steps = [("☀️", "El sol calienta el agua", "#FFB703"), ("💧", "El agua sube como vapor", "#4CC9F0"),
             ("☁️", "El vapor forma nubes", "#A0AEC0"), ("🌧️", "Las nubes sueltan la lluvia", "#219EBC")]
    for i, (ic, txt, c) in enumerate(steps):
        at = 1.2 + i * 2.2
        y = 470 + i * 360
        rrect(t, t.track("shape", "Paso"), "#FFFFFF", at, 12 - at, Box(90, y, 900, 240), 40, pop(0, 0.45, 0.6),
              layers=[shadow("#0B4F6C", 0, 10, 24, 0.18), fill("#FFFFFF"), stroke(4, c)])
        t.solid(t.track("shape", "Icono"), c, at, 12 - at, centered(220, y + 120, 170, 170), pop(0, 0.45), kind="ellipse",
                alpha=0.25)
        emoji(t, ic, at, 12 - at, centered(220, y + 120, 170, 170), 100, motion=pop(0, 0.45))
        label(t, t.track("text", "Paso"), txt, at + 0.15, 11.85 - at, Box(330, y + 30, 630, 180), "Fredoka", 56,
              "#0B4F6C", weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Paso {i + 1}")
        if i < 3:
            t.solid(t.track("shape", "Flecha"), "#0B4F6C", at + 1.2, 10.8 - at, centered(540, y + 300, 90, 110),
                    pop(0, 0.35), kind="arrow", rotation=keys([(0, 90)]))
    song(t, "calm", 2, 0.7)
    return t


def expl_lupa():
    t = T(33, "yt-expl-lupa", "Lupa sobre el detalle", "Magnifier on the detail",
          E + ["lupa", "magnifier", "detalle", "zoom"], 9.0, w=True, thumb_at=5.0)
    vt = t.track("video", "Foto")
    t.photo(vt, "y5-h-ruins-02", 0, 9, t.full, label="Foto")
    shade_full(t, 0.25, 1.4, 7.6)
    cx, cy, r, k = 1240, 470, 250, 2.4
    big = Box(cx - k * cx, cy - k * cy, k * 1920, k * 1080)
    t.solid(t.track("shape", "Lupa"), "#FFFFFF", 1.4, 7.6, centered(cx, cy, 2 * r + 30, 2 * r + 30), pop(0, 0.5),
            kind="ellipse", layers=[shadow("#000000", 0, 16, 40, 0.5), fill("#FFFFFF"), no_stroke()])
    lt = t.track("video", "Aumento")
    host = t.photo(lt, "y5-h-ruins-02", 1.4, 7.6, big, reuse="p1")
    t.mask(lt, host, "ellipse", x=(cx - big.x) / big.w, y=(cy - big.y) / big.h, w=2 * r / big.w, h=2 * r / big.h)
    t.solid(t.track("shape", "Lupa"), "#1B1B1B", 1.4, 7.6, centered(cx, cy, 2 * r + 30, 2 * r + 30), pop(0, 0.5),
            kind="ellipse", layers=hollow_ring("#1B1B1B", 18))
    hx, hy = cx + (r + 120) * math.cos(math.radians(45)), cy + (r + 120) * math.sin(math.radians(45))
    t.solid(t.track("shape", "Mango"), "#1B1B1B", 1.4, 7.6, centered(hx, hy, 220, 56), pop(0, 0.5), radius=28,
            kind="rounded-rectangle", rotation=keys([(0, 45)]))
    label(t, t.track("text", "Nota"), "Mira este detalle", 2.2, 6.8, Box(120, 120, 900, 120), "Permanent Marker", 84,
          "#FFE14D", weight=400, align="left", layers=[shadow("#000000", 0, 6, 0, 0.8), fill("#FFE14D")],
          rotation=keys([(0, -4)]), anim_in=tanim("typewriter", duration=0.7), name="Nota")
    t.solid(t.track("shape", "Flecha"), "#FFE14D", 2.8, 6.2, centered(860, 340, 300, 140), pop(0, 0.35),
            kind="curved-arrow", rotation=keys([(0, 20)]))
    shade_bottom(t, 320, 0.8)
    label(t, t.track("text", "Pie"), "Las piedras guardan marcas de más de 800 años", 3.0, 6.0, Box(120, 930, 1600, 90),
          "Montserrat", 50, "#FFFFFF", weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Pie")
    song(t, "suspense", 2, 0.7)
    return t


def expl_capitulos():
    t = T(34, "yt-expl-capitulos", "En este video (capítulos)", "In this video (chapters)",
          E + ["capítulos", "chapters", "índice", "contenido"], 10.0, w=True, thumb_at=5.3, background="#0F172A")
    bg(t, "#0F172A")
    rounded_photo(t, "h-portrait-04", 0.3, 9.7, Box(1180, 120, 640, 840), slide_in(dx=800, length=0.6), radius=0.06,
                  label_="Tu foto")
    label(t, t.track("text", "Título"), "En este video", 0.2, 9.8, Box(100, 90, 1000, 130), "Sora", 92, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("rise", duration=0.4), name="Título")
    chapters = [("00:00", "Introducción"), ("01:24", "El problema"), ("03:10", "Lo que nadie te cuenta"),
                ("06:45", "La solución"), ("09:30", "Conclusión")]
    y0, step = 290, 140
    pts = [(0, {}, "hold")]
    for i in range(1, 5):
        a = 1.6 + i * 1.5
        pts += [(a - 0.35, {"dy": (i - 1) * step}, "inout"), (a, {"dy": i * step}, "hold")]
    rrect(t, t.track("shape", "Actual"), "#38BDF8", 0, 10.0, Box(80, y0, 1000, 116), 24, pts, alpha=0.22,
          opacity=appear(1.0))
    for i, (ts, name) in enumerate(chapters):
        at = 0.5 + i * 0.2
        y = y0 + i * step
        label(t, t.track("text", "Tiempo"), ts, at, 10 - at, Box(120, y + 18, 240, 80), "VT323", 72, "#38BDF8",
              weight=400, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.1),
              name=f"Tiempo {i + 1}")
        label(t, t.track("text", "Capítulo"), name, at, 10 - at, Box(330, y + 20, 740, 80), "Sora", 50, "#FFFFFF",
              weight=600, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.1),
              name=f"Capítulo {i + 1}")
    song(t, "electro", 2, 0.65)
    return t


def expl_opina():
    t = T(35, "yt-expl-opina", "¿Y tú qué opinas? (encuesta)", "What do you think? (poll)",
          E + ["encuesta", "poll", "comentarios", "cierre"], 8.0, thumb_at=5.6)
    t.photo(t.track("video", "Foto"), "y5-h-lab-03", 0, 8, t.full, kb(8, 1.05, 1.12), label="Foto de fondo",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=24)])
    shade_full(t, 0.5, colour="#1E1B4B")
    label(t, t.track("text", "Pregunta"), "¿Y tú qué\nopinas?", 0.2, 7.8, Box(60, 260, 960, 440), "Archivo Black", 150,
          "#FFFFFF", weight=400, line=1.0, anim_in=tanim("bounce", duration=0.5, unit="word", stagger=0.12),
          name="Pregunta")
    opts = [("A", "Vale la pena", 62, "#A78BFA"), ("B", "No lo haría", 38, "#F472B6")]
    for i, (k, txt, pct, c) in enumerate(opts):
        y = 860 + i * 230
        at = 1.4 + i * 0.3
        rrect(t, t.track("shape", "Opción"), "#FFFFFF", at, 8 - at, Box(80, y, 920, 180), 90, pop(0, 0.4, 0.8),
              alpha=0.15)
        bar_right(t, c, at + 0.6, Box(80, y, 920 * pct / 100, 180), length=1.2, radius=90, alpha=0.9)
        label(t, t.track("text", "Opción"), f"{k}.  {txt}", at + 0.1, 7.9 - at, Box(130, y + 45, 640, 90), "Sora", 54,
              "#FFFFFF", weight=700, align="left", name=f"Opción {k}")
        label(t, t.track("text", "Porcentaje"), f"{pct} %", at + 1.6, 6.4 - at, Box(760, y + 40, 200, 100), "Sora", 64,
              "#FFFFFF", weight=800, align="right", anim_in=tanim("pop", duration=0.3), name=f"Porcentaje {k}")
    label(t, t.track("text", "CTA"), "Déjalo en los comentarios 👇", 3.6, 4.4, Box(60, 1440, 960, 100), "Sora", 54,
          "#1E1B4B", weight=800, box_bg=("#FFE14D", 1.0), box_pad=20, box_radius=50,
          anim_in=tanim("pop", duration=0.4), name="Llamada")
    song(t, "fun", 1, 0.7)
    return t


# =============================================================================================
# 3. Un día en mi vida / Arréglate conmigo
# =============================================================================================

CREAM = "#F6EFE6"
COCOA = "#4A3B32"
SAGE = "#8FA382"
BLUSH = "#E8B4B8"


def dia_0630():
    t = T(36, "yt-dia-0630", "La hora en pantalla", "Time on screen", D + ["hora", "time", "rutina", "routine"], 12.0,
          thumb_at=1.6)
    items = [("06:30", "me levanto sin prisa", "y5-morning-03"), ("07:15", "café y diario", "y5-morning-07"),
             ("12:40", "trabajo desde casa", "y5-journal-03"), ("21:00", "té y a leer", "y5-cozy-05")]
    slides(t, [s for _, _, s in items], 0, 3.0, transition="crossfade", tdur=0.5, kb_amount=0.06,
           labels=[f"Momento {i + 1}" for i in range(4)])
    shade_top(t, 900, 0.45)
    for i in range(4):
        x = 70 + i * 240
        t.solid(t.track("shape", "Progreso"), "#FFFFFF", 0, 12, Box(x, 80, 220, 8), radius=4, kind="rounded-rectangle",
                alpha=0.35)
        bar_right(t, "#FFFFFF", i * 3.0, Box(x, 80, 220, 8), length=3.0, radius=4, end=12)
    label(t, t.track("text", "Etiqueta"), "un día en mi vida", 0.2, 11.8, Box(60, 130, 960, 70), "Quicksand", 44,
          "#FFFFFF", weight=700, spacing=3, name="Etiqueta")
    ht, ct = t.track("text", "Hora"), t.track("text", "Qué hago")
    for i, (h, c, _) in enumerate(items):
        a = i * 3.0
        label(t, ht, h, a, 3.0, Box(40, 220, 1000, 300), "Bebas Neue", 300, "#FFFFFF", weight=400,
              layers=[shadow("#000000", 0, 6, 30, 0.35), fill("#FFFFFF")],
              anim_in=tanim("blur-in", duration=0.4, blur=12), name=f"Hora {i + 1}")
        label(t, ct, c, a + 0.15, 2.85, Box(40, 510, 1000, 120), "Caveat", 90, "#FFFFFF", weight=700,
              layers=[shadow("#000000", 0, 4, 16, 0.4), fill("#FFFFFF")], anim_in=tanim("typewriter", duration=0.6),
              name=f"Qué hago {i + 1}")
    song(t, "calm", 0)
    return t


def dia_checklist():
    t = T(37, "yt-dia-checklist", "Rutina de mañana con checklist", "Morning routine checklist",
          D + ["checklist", "rutina", "routine", "mañana"], 11.0, thumb_at=8.6, background=CREAM)
    bg(t, CREAM)
    vt = t.track("video", "Fotos")
    a = t.photo(vt, "y5-yoga-01", 0, 5.8, Box(0, 0, 1080, 820), kb(5.8, 1.0, 1.06), label="Foto 1")
    b = t.photo(vt, "y5-morning-02", 5.3, 5.7, Box(0, 0, 1080, 820), kb(5.7, 1.06, 1.0), label="Foto 2")
    t.transition(vt, a, b, "crossfade", 0.5)
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.2, 10.8, Box(50, 700, 980, 1140), 48, slide_in(dy=900, length=0.6),
          layers=[shadow(COCOA, 0, -6, 30, 0.15), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "Título"), "Rutina de mañana", 0.5, 10.5, Box(120, 760, 840, 130), "Playfair Display", 84,
          COCOA, weight=700, italic=True, align="left", anim_in=tanim("fade", duration=0.4), name="Título")
    items = ["Tender la cama", "Agua con limón", "10 minutos de yoga", "Ducha tibia", "Desayuno sin pantallas"]
    for i, it in enumerate(items):
        y = 940 + i * 165
        shown = 0.8 + i * 0.15
        tick = 2.0 + i * 1.5
        ring(t, t.track("shape", "Casilla"), SAGE, 6, shown, 11 - shown, centered(175, y + 50, 80, 80), pop(0, 0.3))
        t.solid(t.track("shape", "Marca"), SAGE, tick, 11 - tick, centered(175, y + 50, 80, 80),
                [(0, {"s": 0.0}, "back"), (0.3, {})], kind="ellipse")
        label(t, t.track("text", "Visto"), "✓", tick, 11 - tick, centered(175, y + 50, 80, 80), "Inter", 52, "#FFFFFF",
              weight=800, editable=False, motion=[(0, {"s": 0.0}, "back"), (0.3, {})])
        label(t, t.track("text", "Paso"), it, shown, 11 - shown, Box(250, y + 5, 740, 90), "Quicksand", 56, COCOA,
              weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Paso {i + 1}",
              opacity=keys([(0, 1.0, "hold"), (tick - shown, 1.0, "smooth"), (tick - shown + 0.3, 0.45)]))
    song(t, "calm", 1)
    return t


def dia_linea_rutina():
    t = T(38, "yt-dia-linea-rutina", "Línea de tiempo de mi rutina", "My routine timeline",
          D + ["línea de tiempo", "timeline", "rutina", "routine"], 12.0, thumb_at=7.0, background="#FBF6EF")
    bg(t, "#FBF6EF")
    label(t, t.track("text", "Título"), "mi martes", 0.2, 11.8, Box(60, 90, 960, 160), "Sacramento", 150, COCOA,
          weight=400, anim_in=tanim("fade", duration=0.6), name="Título")
    steps = [("07:00", "despertar", "y5-morning-01"), ("08:30", "estudiar", "y5-journal-04"),
             ("13:00", "almuerzo", "coffee-01"), ("18:00", "yoga", "y5-yoga-02"), ("22:00", "leer", "reading-01")]
    x0, y0, step = 130, 360, 300
    t.solid(t.track("shape", "Línea"), "#D8C8B8", 0.2, 11.8, Box(x0 - 3, y0, 6, step * 4))
    t.solid(t.track("shape", "Progreso"), BLUSH, 0, 12, Box(x0 - 4, y0, 8, step * 4),
            [(0, {"sy": 0.0, "dy": -step * 2}, "linear"), (0.8, {"sy": 0.0, "dy": -step * 2}, "linear"),
             (9.6, {})])
    vt = t.track("video", "Fotos")
    prev = None
    for i, (h, act, s) in enumerate(steps):
        at = 0.8 + i * 2.2
        y = y0 + i * step
        t.solid(t.track("shape", "Hito"), BLUSH, at, 12 - at, centered(x0, y, 44, 44), pop(0, 0.35), kind="ellipse",
                layers=[fill(BLUSH), stroke(6, "#FBF6EF")])
        op = keys([(0, 1.0, "hold"), (2.2, 1.0, "smooth"), (2.5, 0.5)]) if i < 4 else const_one()
        label(t, t.track("text", "Hora"), h, at, 12 - at, Box(x0 + 50, y - 60, 300, 70), "Quicksand", 54, COCOA,
              weight=700, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.1),
              name=f"Hora {i + 1}", opacity=op)
        label(t, t.track("text", "Actividad"), act, at, 12 - at, Box(x0 + 50, y + 5, 300, 70), "Caveat", 60, "#9C6B5E",
              weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Actividad {i + 1}", opacity=op)
        d = 2.2 if i < 4 else 12 - at
        clip = t.photo(vt, s, at, d + (0.4 if i < 4 else 0), Box(500, 420, 520, 1180),
                       [(0, {"s": 1.04}), (d, {})], label=f"Foto {i + 1}")
        if prev:
            t.transition(vt, prev, clip, "crossfade", 0.4)
        prev = clip
    song(t, "calm", 3)
    return t


def dia_grwm_pasos():
    t = T(39, "yt-dia-grwm-pasos", "Arréglate conmigo: pasos", "Get ready with me: steps",
          G + ["maquillaje", "makeup", "pasos", "steps"], 12.0, thumb_at=5.0, background="#2B1B1F")
    steps = [("Base ligera", "con esponja húmeda", "y5-grwm-01"), ("Corrector", "solo donde hace falta", "y5-grwm-03"),
             ("Rubor", "en las mejillas, hacia arriba", "y5-grwm-05"), ("Labios", "un tono que te guste", "y5-grwm-06")]
    vt = t.track("video", "Pasos")
    intro = t.photo(vt, "y5-grwm-08", 0, 1.8, t.full, kb(1.8, 1.08, 1.0), label="Foto de portada")
    prev = intro
    for i, (_, _, s) in enumerate(steps):
        a = 1.6 + i * 2.6
        d = 2.8 if i < 3 else 12 - a
        c = t.photo(vt, s, a, d, t.full, kb(d, 1.0, 1.07), label=f"Paso {i + 1}")
        t.transition(vt, prev, c, "crossfade" if i else "dip_white", 0.25)
        prev = c
    label(t, t.track("text", "Intro"), "arréglate\nconmigo", 0.1, 1.6, Box(40, 640, 1000, 520), "Dancing Script", 170,
          "#FFFFFF", weight=700, line=0.9, layers=[shadow("#000000", 0, 6, 24, 0.5), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=0.5), name="Título")
    ct, st, tt = t.track("shape", "Tarjeta"), t.track("text", "Paso"), t.track("text", "Consejo")
    nt = t.track("text", "Número")
    for i, (name, tip, _) in enumerate(steps):
        a = 1.8 + i * 2.6
        d = 2.6 if i < 3 else 12 - a
        m = [(0, {"dy": 500}, "out"), (0.45, {})]
        rrect(t, ct, "#FFFFFF", a, d, Box(60, 1460, 960, 330), 44, m,
              layers=[shadow("#000000", 0, 10, 30, 0.3), fill("#FFF4F5"), no_stroke()])
        label(t, nt, f"PASO {i + 1}", a, d, Box(120, 1500, 600, 60), "Montserrat", 36, "#C9184A", weight=800, spacing=6,
              align="left", motion=m, name=f"Número {i + 1}", editable=False)
        label(t, st, name, a, d, Box(120, 1560, 860, 120), "Playfair Display", 92, "#2B1B1F", weight=700, align="left",
              motion=m, name=f"Paso {i + 1}")
        label(t, tt, tip, a, d, Box(120, 1690, 860, 70), "Montserrat", 40, "#8A6A70", weight=500, align="left",
              motion=m, name=f"Consejo {i + 1}")
        for k in range(4):
            t.solid(t.track("shape", "Punto"), "#FFFFFF", a, d, centered(810 + k * 50, 1530, 22, 22), m,
                    kind="ellipse", layers=[fill("#C9184A", 1.0 if k <= i else 0.2), no_stroke()])
    song(t, "romantic", 1)
    return t


def dia_outfit():
    t = T(40, "yt-dia-outfit", "Outfit del día", "Outfit of the day", G + ["outfit", "ropa", "fashion", "look"], 9.0,
          thumb_at=6.4)
    photo_bg(t, "y5-outfit-04", s1=1.05, label="Foto del outfit")
    shade_top(t, 420, 0.5)
    label(t, t.track("text", "Título"), "Outfit del día", 0.2, 8.8, Box(60, 110, 960, 150), "Playfair Display", 110,
          "#FFFFFF", weight=700, italic=True, layers=[shadow("#000000", 0, 4, 20, 0.5), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=0.6), name="Título")
    label(t, t.track("text", "Fecha"), "lunes · 8 °C · oficina", 0.5, 8.5, Box(60, 260, 960, 70), "Montserrat", 40,
          "#FFFFFF", weight=600, spacing=3, name="Detalle")
    tags = [((560, 780), (820, 640), "chaqueta oversize"), ((520, 1250), (820, 1150), "pantalón de pinzas"),
            ((470, 1700), (230, 1560), "zapatillas blancas")]
    for i, ((px, py), (lx, ly), txt) in enumerate(tags):
        at = 1.4 + i * 1.3
        t.solid(t.track("shape", "Punto"), "#FFFFFF", at, 9 - at, centered(px, py, 34, 34), pop(0, 0.3), kind="ellipse",
                layers=[shadow("#000000", 0, 2, 8, 0.5), fill("#FFFFFF"), no_stroke()])
        ring(t, t.track("shape", "Pulso"), "#FFFFFF", 4, at, 9 - at, centered(px, py, 34, 34),
             [(0, {"s": 1.0}, "out"), (1.2, {"s": 2.6})], opacity=keys([(0, 0.8), (1.2, 0.0)]))
        seg(t, "#FFFFFF", at + 0.2, 8.8 - at, (px, py), (lx, ly), 4, grow=0.3, name="Guía")
        label(t, t.track("text", "Prenda"), txt, at + 0.45, 8.55 - at, centered(lx, ly - 46, 440, 70), "Montserrat", 38,
              "#1B1B1B", weight=700, box_bg=("#FFFFFF", 1.0), box_pad=14, box_radius=36,
              anim_in=tanim("pop", duration=0.3), name=f"Prenda {i + 1}")
    song(t, "jazz", 2)
    return t


def dia_cozy():
    t = T(41, "yt-dia-cozy", "Domingo lento (cozy)", "Slow Sunday (cosy)", D + ["cozy", "acogedor", "domingo",
          "aesthetic"], 10.0, thumb_at=3.6, background="#2A1F19")
    slides(t, ["y5-cozy-05", "y5-cozy-04", "y5-morning-04", "y5-cozy-03"], 0, 2.5, transition="blur_dissolve",
           tdur=0.7, kb_amount=0.05, labels=[f"Momento {i + 1}" for i in range(4)])
    t.adjust([effect("color.basic", temperature=0.22, fade=0.12, contrast=-0.05, exposure=0.15, shadows=0.2),
              effect("stylize.film_grain", amount=0.25, grainSize=1.8), effect("stylize.vignette", amount=0.3)],
             name="Look cálido")
    outline(t, t.track("shape", "Marco"), "#F6E7D7", 3, 0, 10, Box(40, 40, 1000, 1840), alpha=0.8)
    label(t, t.track("text", "Título"), "un domingo lento", 0.6, 9.4, Box(60, 1420, 960, 180), "Caveat", 130, "#F6E7D7",
          weight=700, layers=[shadow("#000000", 0, 4, 20, 0.5), fill("#F6E7D7")],
          anim_in=tanim("typewriter", duration=1.2), name="Título")
    label(t, t.track("text", "Hora"), "16:20", 1.0, 9.0, Box(60, 1600, 960, 90), "Cormorant Garamond", 70, "#F6E7D7",
          weight=500, italic=True, anim_in=tanim("fade", duration=0.8), name="Hora")
    label(t, t.track("text", "Lista"), "té · libro · lluvia", 1.4, 8.6, Box(60, 1690, 960, 70), "Cormorant Garamond", 48,
          "#E8C9A8", weight=500, spacing=6, anim_in=tanim("fade", duration=0.8), name="Detalle")
    t.adjust([effect("light_leak", intensity=0.3, hue=0.06, speed=0.4)], name="Luz")
    song(t, "jazz", 0, 0.75)
    return t


def dia_diario():
    t = T(42, "yt-dia-diario", "Diario de mi día", "My day journal", D + ["diario", "journal", "notas", "bullet"],
          11.0, thumb_at=8.0, background="#FBF7F0")
    bg(t, "#FBF7F0")
    entries = [("7:00", "café en la ventana"), ("9:30", "clase de inglés"), ("13:00", "almuerzo con Ana"),
               ("17:00", "caminata al parque"), ("21:30", "película y a dormir")]
    for k in range(6):
        t.solid(t.track("shape", "Renglón"), "#DCE6F0", 0, 11, Box(0, 1140 + k * 140, 1080, 3))
    t.solid(t.track("shape", "Margen"), "#F4A6A6", 0, 11, Box(110, 0, 4, 1920))
    label(t, t.track("text", "Fecha"), "martes 14 de octubre", 0.2, 10.8, Box(150, 110, 880, 120), "Kalam", 84, COCOA,
          weight=700, align="left", anim_in=tanim("typewriter", duration=0.8), name="Fecha")
    label(t, t.track("text", "Ánimo"), "ánimo: ☀️ tranquilo", 0.6, 10.4, Box(150, 230, 880, 70), "Kalam", 50, "#9C6B5E",
          weight=400, align="left", anim_in=tanim("fade", duration=0.5), name="Ánimo")
    for i, (h, txt) in enumerate(entries):
        at = 1.4 + i * 1.3
        y = 1140 + i * 140 - 112
        label(t, t.track("text", "Entrada"), f"{h}  —  {txt}", at, 11 - at, Box(150, y, 900, 110), "Patrick Hand", 70,
              "#2F3E46", weight=400, align="left", anim_in=tanim("typewriter", duration=0.6), name=f"Entrada {i + 1}")
    for i, (s, cx, cy, r) in enumerate([("y5-morning-05", 340, 640, -6), ("y5-journal-02", 760, 670, 5)]):
        at = 0.8 + i * 0.4
        framed(t, s, at, 11 - at, centered(cx, cy, 380, 420), [(0, {"s": 1.3}, "out"), (0.4, {})], border=16, bottom=56,
               rotation=keys([(0, r)]), label=f"Foto {i + 1}")
        t.solid(t.track("shape", "Cinta"), ["#B8E0D2", "#F7C59F"][i], at + 0.2, 10.8 - at,
                centered(cx, cy - 235, 180, 48), pop(0, 0.3), rotation=keys([(0, -r * 1.5)]), alpha=0.85)
    emoji(t, "♡", 8.2, 2.8, centered(930, 1850, 110, 110), 80, motion=pop(0, 0.4))
    song(t, "calm", 4, 0.75)
    return t


def dia_reloj():
    t = T(43, "yt-dia-reloj", "Reloj de mi día", "Clock of my day", D + ["reloj", "clock", "hora", "rutina"], 12.0,
          thumb_at=6.6, background="#EDE6DA")
    bg(t, "#EDE6DA")
    cx, cy, R = 540, 560, 330
    t.solid(t.track("shape", "Reloj"), "#FFFFFF", 0, 12, centered(cx, cy, 2 * R, 2 * R), kind="ellipse",
            layers=[shadow(COCOA, 0, 14, 30, 0.2), fill("#FFFFFF"), stroke(14, COCOA)])
    for k, n in enumerate(["12", "3", "6", "9"]):
        a = math.radians(-90 + k * 90)
        label(t, t.track("text", "Número"), n, 0, 12, centered(cx + 0.78 * R * math.cos(a), cy + 0.78 * R * math.sin(a),
              120, 90), "DM Serif Display", 64, COCOA, weight=400, editable=False)
    steps = [(7, 0, "despierto"), (9, 30, "en la oficina"), (13, 0, "almuerzo"), (18, 30, "gimnasio"),
             (22, 0, "a descansar")]
    # minute hand spins to each new time, hour hand follows
    hk, mk = [], []
    for i, (h, m, _) in enumerate(steps):
        at = i * 2.4
        tot = h * 60 + m
        if i:
            hk.append((at - 0.9, (steps[i - 1][0] * 60 + steps[i - 1][1]) * 0.5, "inout"))
            mk.append((at - 0.9, (steps[i - 1][0] * 60 + steps[i - 1][1]) * 6.0, "inout"))
        hk.append((at, tot * 0.5, "hold"))
        mk.append((at, tot * 6.0, "hold"))
    def hand(length, th, colour, ks):
        t.solid(t.track("shape", "Aguja"), colour, 0, 12, centered(cx, cy, th, 2 * length), radius=th / 2,
                kind="rounded-rectangle",
                layers=[gradient([(0, colour), (0.5, colour), (0.501, colour, 0.0), (1, colour, 0.0)], angle=90),
                        no_stroke()], rotation=keys(ks))
    hand(R * 0.55, 22, COCOA, hk)
    hand(R * 0.82, 12, "#C0846A", mk)
    t.solid(t.track("shape", "Centro"), COCOA, 0, 12, centered(cx, cy, 40, 40), kind="ellipse")
    vt = t.track("video", "Fotos")
    prev = None
    samples = ["y5-morning-06", "study-01", "coffee-03", "y5-yoga-03", "reading-02"]
    tt, at_ = t.track("text", "Hora"), t.track("text", "Actividad")
    for i, (h, m, act) in enumerate(steps):
        at = i * 2.4
        d = 2.4 if i < 4 else 12 - at
        c = t.photo(vt, samples[i], at, d + (0.3 if i < 4 else 0), Box(90, 1180, 900, 640), kb(d, 1.0, 1.06),
                    label=f"Foto {i + 1}")
        if prev:
            t.transition(vt, prev, c, "crossfade", 0.3)
        prev = c
        label(t, tt, f"{h:02d}:{m:02d}", at, d, Box(90, 950, 420, 120), "DM Serif Display", 100, COCOA, weight=400,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Hora {i + 1}")
        label(t, at_, act, at, d, Box(480, 975, 520, 90), "Caveat", 76, "#C0846A", weight=700, align="right",
              anim_in=tanim("fade", duration=0.3), name=f"Actividad {i + 1}")
    song(t, "jazz", 1, 0.75)
    return t


def dia_grwm_espejo():
    t = T(44, "yt-dia-grwm-espejo", "Arréglate conmigo: espejo", "Get ready with me: mirror",
          G + ["espejo", "mirror", "maquillaje", "cita"], 10.0, thumb_at=6.0, background="#F7D6E0")
    bg_gradient(t, [(0, "#F7D6E0"), (1, "#F2B5D4")], angle=90)
    cx, cy, w, h = 540, 980, 700, 940
    t.solid(t.track("shape", "Espejo"), "#FFFFFF", 0, 10, centered(cx, cy, w + 70, h + 70), kind="ellipse",
            layers=[shadow("#9D4E6A", 0, 16, 40, 0.3), fill("#FFF7FA"), no_stroke()])
    vt = t.track("video", "Espejo")
    prev = None
    for i, s in enumerate(["y5-grwm-02", "y5-grwm-04", "y5-grwm-07"]):
        a = i * 3.3
        d = 3.3 if i < 2 else 10 - a
        c = t.photo(vt, s, a, d, centered(cx, cy, w, h), kb(d, 1.0, 1.05), label=f"Foto {i + 1}")
        t.mask(vt, c, "ellipse")
        prev = c
    for k in range(10):
        ang = math.radians(-90 + k * 36)
        bx, by = cx + (w / 2 + 75) * math.cos(ang), cy + (h / 2 + 75) * math.sin(ang)
        t.solid(t.track("shape", "Bombilla"), "#FFF6D5", 0.1 * k, 10 - 0.1 * k, centered(bx, by, 54, 54), pop(0, 0.3),
                kind="ellipse", layers=[glow("#FFE8A3", 26, 0.9), fill("#FFF6D5"), no_stroke()])
    label(t, t.track("text", "Título"), "GRWM: cita de noche", 0.3, 9.7, Box(40, 90, 1000, 140), "Playfair Display", 84,
          "#7A2E4B", weight=700, italic=True, anim_in=tanim("fade", duration=0.5), name="Título")
    st = t.track("text", "Paso")
    for i, txt in enumerate(["paso 1 · piel", "paso 2 · ojos", "paso 3 · labios"]):
        a = i * 3.3
        d = 3.3 if i < 2 else 10 - a
        label(t, st, txt, a + 0.2, d - 0.2, Box(40, 1600, 1000, 100), "Montserrat", 60, "#FFFFFF", weight=700,
              box_bg=("#7A2E4B", 1.0), box_pad=18, box_radius=45, anim_in=tanim("pop", duration=0.3),
              name=f"Paso {i + 1}")
    dots(t, ["#FFFFFF"], 12, 0, 10, seed=441, size=(10, 24), kinds=("star",), drift=40)
    song(t, "romantic", 2)
    return t


def dia_estudio():
    t = T(45, "yt-dia-estudio", "Un día de estudio conmigo", "Study with me day",
          D + ["estudio", "study", "agenda", "productividad"], 12.0, w=True, thumb_at=8.6, background="#F5F3EE")
    bg(t, "#F5F3EE")
    label(t, t.track("text", "Título"), "Un día de estudio conmigo", 0.2, 11.8, Box(80, 50, 960, 100), "Outfit", 62,
          "#1F2933", weight=800, align="left", anim_in=tanim("fade", duration=0.4), name="Título")
    top, hrs = 190, ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    for i, h in enumerate(hrs):
        y = top + i * 130
        label(t, t.track("text", "Hora"), h, 0.2, 11.8, Box(80, y - 22, 160, 44), "Outfit", 32, "#7B8794", weight=500,
              align="left", editable=False)
        t.solid(t.track("shape", "Guía"), "#E1DCD2", 0.2, 11.8, Box(230, y, 760, 2))
    blocks = [(0, 3, "Clase de química", "#A3C4F3"), (3.5, 2, "Biblioteca", "#B9FBC0"),
              (6.5, 2, "Gimnasio", "#FFCFD2"), (10.5, 1.5, "Cena con amigos", "#FDE4CF")]
    vt = t.track("video", "Fotos")
    prev = None
    samples = ["y5-h-lab-02", "y5-h-cozy-03", "y5-yoga-02", "h-cafe-03"]
    for i, (start, length, name, c) in enumerate(blocks):
        at = 0.8 + i * 2.7
        y = top + start * 65 + 4
        hgt = length * 65 - 8
        rrect(t, t.track("shape", "Bloque"), c, at, 12 - at, Box(250, y, 720, hgt), 18,
              [(0, {"sx": 0.0, "dx": -360}, "out"), (0.5, {})])
        label(t, t.track("text", "Bloque"), name, at + 0.3, 11.7 - at, Box(280, y + 10, 680, 70), "Outfit", 40,
              "#1F2933", weight=700, align="left", anim_in=tanim("fade", duration=0.3), name=f"Bloque {i + 1}")
        d = 2.7 if i < 3 else 12 - at
        clip = t.photo(vt, samples[i], at, d + (0.4 if i < 3 else 0), Box(1060, 120, 800, 860), kb(d, 1.0, 1.05),
                       label=f"Foto {i + 1}")
        if prev:
            t.transition(vt, prev, clip, "slide_left", 0.4)
        prev = clip
    label(t, t.track("text", "Nota"), "horas de estudio: 5 ✓", 9.8, 2.2, Box(1080, 900, 760, 70), "Caveat", 60,
          "#1F2933", weight=700, box_bg=("#FFFFFF", 1.0), box_pad=12, box_radius=10,
          anim_in=tanim("pop", duration=0.3), name="Nota")
    song(t, "electro", 3, 0.65)
    return t


def dia_antes_despues():
    t = T(46, "yt-dia-antes-despues", "Arréglate conmigo: antes y después", "Get ready with me: before and after",
          G + ["antes y después", "before after", "transformación"], 8.0, thumb_at=5.2)
    t.photo(t.track("video", "Antes"), "y5-grwm-03", 0, 8, t.full, kb(8, 1.0, 1.05), label="Foto de antes",
            effects=[effect("color.basic", saturation=-0.85, exposure=-0.15, contrast=-0.2)])
    after_track = t.track("video", "Después")
    after = t.photo(after_track, "y5-grwm-03", 0, 8, t.full, kb(8, 1.0, 1.05), label="Foto de después")
    # the after photo opens from the right edge with a moving divider
    lane_x = keys([(0, 1.5, "hold"), (1.8, 1.5, "inout"), (3.6, 1.0)])
    t.mask(after_track, after, "rectangle", x=1.5, y=0.5, w=1.0, h=1.0, keyframes={"x": lane_x})
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0, 8, centered(1080, 960, 10, 1920),
            [(0, {"dx": 0}, "hold"), (1.8, {"dx": 0}, "inout"), (3.6, {"dx": -540})], layers=[shadow("#000000", 0, 0, 16, 0.5), fill("#FFFFFF"), no_stroke()])
    label(t, t.track("text", "Antes"), "7:40 · recién levantada", 0.3, 7.7, Box(40, 220, 700, 90), "Montserrat", 40,
          "#FFFFFF", weight=700, align="left", box_bg=("#000000", 0.55), box_pad=14, box_radius=10,
          anim_in=tanim("fade", duration=0.3), name="Antes")
    label(t, t.track("text", "Después"), "8:10 · ¡lista!", 3.8, 4.2, Box(560, 1600, 480, 90), "Montserrat", 44,
          "#3D0F1E", weight=800, align="right", box_bg=("#FFC8DD", 1.0), box_pad=16, box_radius=10,
          anim_in=tanim("pop", duration=0.3), name="Después")
    label(t, t.track("text", "Título"), "30 minutos", 0.4, 7.6, Box(40, 90, 1000, 120), "Archivo Black", 96, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 6, 20, 0.6), fill("#FFFFFF")], anim_in=tanim("rise", duration=0.4),
          name="Título")
    song(t, "upbeat", 4)
    return t


def dia_noche():
    t = T(47, "yt-dia-noche", "Rutina de noche", "Night routine", D + ["noche", "night", "rutina", "skincare"], 11.0,
          thumb_at=7.0, background="#0D1B3E")
    bg_gradient(t, [(0, "#0D1B3E"), (1, "#2D1E4F")], angle=90)
    dots(t, ["#FFFFFF", "#FFE9A8"], 24, 0, 11, seed=471, size=(6, 16), kinds=("star", "ellipse"), drift=20,
         area=Box(0, 0, 1080, 700))
    t.solid(t.track("shape", "Luna"), "#FFE9A8", 0.2, 10.8, centered(860, 260, 200, 200), pop(0, 0.6), kind="ellipse",
            layers=[glow("#FFE9A8", 40, 0.6), fill("#FFE9A8"), no_stroke()])
    t.solid(t.track("shape", "Luna"), "#12204A", 0.2, 10.8, centered(910, 220, 170, 170), pop(0, 0.6), kind="ellipse")
    label(t, t.track("text", "Título"), "rutina de noche", 0.4, 10.6, Box(60, 180, 800, 200), "Sacramento", 140,
          "#FFFFFF", weight=400, align="left", anim_in=tanim("blur-in", duration=0.8), name="Título")
    steps = [("22:00", "limpiar y crema", "y5-grwm-05"), ("22:30", "un capítulo", "reading-03"),
             ("23:00", "a dormir", "y5-h-cozy-01")]
    for i, (h, txt, s) in enumerate(steps):
        at = 1.4 + i * 2.4
        y = 520 + i * 440
        x = 90 if i % 2 == 0 else 560
        m = [(0, {"dy": 120}, "out"), (0.5, {})]
        rounded_photo(t, s, at, 11 - at, Box(x, y, 430, 400), m, radius=0.12, label_=f"Foto {i + 1}",
                      opacity=keys([(0, 0.0), (0.3, 1.0)]))
        tx = 560 if i % 2 == 0 else 90
        label(t, t.track("text", "Hora"), h, at + 0.2, 10.8 - at, Box(tx, y + 90, 430, 130), "Cormorant Garamond", 110,
              "#FFE9A8", weight=600, align="left", anim_in=tanim("fade", duration=0.4), name=f"Hora {i + 1}")
        label(t, t.track("text", "Paso"), txt, at + 0.35, 10.65 - at, Box(tx, y + 220, 430, 80), "Montserrat", 44,
              "#FFFFFF", weight=500, align="left", anim_in=tanim("fade", duration=0.4), name=f"Paso {i + 1}")
    song(t, "romantic", 3, 0.7)
    return t


def dia_fin_semana():
    t = T(48, "yt-dia-fin-semana", "Sábado conmigo (scrapbook)", "Saturday with me (scrapbook)",
          D + ["fin de semana", "weekend", "scrapbook", "polaroids"], 11.0, w=True, thumb_at=8.0, background="#E8D5B5")
    bg(t, "#E8D5B5")
    dots(t, ["#D9BF94"], 18, 0, 11, seed=481, size=(20, 50), drift=10)
    label(t, t.track("text", "Título"), "Sábado conmigo", 0.2, 10.8, Box(560, 40, 800, 170), "Dancing Script", 130,
          COCOA, weight=700, anim_in=tanim("blur-in", duration=0.6), name="Título")
    spots = [("y5-morning-08", 250, 430, -6, "09:00 brunch"), ("y5-h-street-03", 640, 690, 4, "11:30 mercado"),
             ("y5-yoga-04", 1060, 430, -3, "15:00 siesta"), ("y5-outfit-03", 1460, 690, 5, "19:00 salir"),
             ("y5-night-04", 1730, 370, -4, "23:00 casa")]
    for i, (s, cx, cy, r, note) in enumerate(spots):
        at = 0.6 + i * 1.6
        framed(t, s, at, 11 - at, centered(cx, cy, 320, 320), [(0, {"s": 1.4, "dy": -80}, "out"), (0.45, {})],
               border=14, bottom=70, rotation=keys([(0, r)]), label=f"Foto {i + 1}")
        nx, ny = gplace(cx, cy + 35, r, 0, 180)
        label(t, t.track("text", "Nota"), note, at + 0.4, 10.6 - at, centered(nx, ny, 320, 60), "Permanent Marker", 34,
              COCOA, weight=400, rotation=keys([(0, r)]), anim_in=tanim("typewriter", duration=0.5),
              name=f"Nota {i + 1}")
        tx, ty = gplace(cx, cy, r, 0, -185)
        t.solid(t.track("shape", "Cinta"), ["#F7C59F", "#B8E0D2", "#E4C1F9", "#FCF6BD", "#A9DEF9"][i], at + 0.3,
                10.7 - at, centered(tx, ty, 140, 40), pop(0, 0.3), rotation=keys([(0, r - 8)]), alpha=0.85)
    song(t, "upbeat", 6, 0.75)
    return t


def dia_alarma():
    t = T(49, "yt-dia-alarma", "Suena la alarma", "The alarm rings", D + ["alarma", "alarm", "mañana", "despertar"],
          9.0, thumb_at=1.7, background="#101827")
    bg_gradient(t, [(0, "#1E293B"), (1, "#0B1120")], angle=90)
    label(t, t.track("text", "Hora"), "06:30", 0.1, 3.0, Box(40, 420, 1000, 330), "Inter", 280, "#FFFFFF", weight=300,
          anim_in=tanim("fade", duration=0.3), name="Hora de la alarma")
    label(t, t.track("text", "Etiqueta"), "Alarma · hoy es el día", 0.3, 2.8, Box(40, 760, 1000, 80), "Inter", 52,
          "#CBD5E1", weight=500, name="Etiqueta de la alarma")
    emoji(t, "⏰", 0.1, 2.9, centered(540, 300, 200, 200), 150, anim_loop=tanim("jitter", amount=3, angle=8, speed=14))
    pill(t, t.track("shape", "Botón"), "#334155", 0.4, 2.6, centered(540, 1200, 440, 120))
    label(t, t.track("text", "Botón"), "Posponer", 0.4, 2.6, centered(540, 1200, 440, 120), "Inter", 48, "#FFFFFF",
          weight=600, name="Botón")
    pill(t, t.track("shape", "Deslizar"), "#FFFFFF", 0.4, 2.6, centered(540, 1560, 820, 150), alpha=0.15)
    label(t, t.track("text", "Deslizar"), "desliza para detener  →", 0.4, 2.6, centered(600, 1560, 700, 150), "Inter",
          40, "#E2E8F0", weight=500, name="Deslizar")
    t.solid(t.track("shape", "Perilla"), "#FFFFFF", 0.4, 2.6, centered(205, 1560, 130, 130),
            [(0, {}, "hold"), (1.4, {}, "inout"), (2.4, {"dx": 660})], kind="ellipse")
    t.adjust([effect("beat_shake", animated={"amount": spike([0.3, 0.8, 1.3], 0.5, 0.3)}, rotation=0.6)], 0, 2.9,
             name="Vibración")
    vt = t.track("video", "Día")
    items = [("06:45", "y5-morning-02"), ("07:20", "y5-yoga-02"), ("08:00", "y5-outfit-06")]
    prev = None
    for i, (h, s) in enumerate(items):
        a = 3.0 + i * 2.0
        d = 2.0 if i < 2 else 9 - a
        c = t.photo(vt, s, a, d, t.full, kb(d, 1.1, 1.0), label=f"Momento {i + 1}")
        prev = c
        label(t, t.track("text", "Momento"), h, a, d, Box(60, 1580, 600, 140), "Inter", 110, "#FFFFFF", weight=800, align="left",
              layers=[shadow("#000000", 0, 4, 20, 0.5), fill("#FFFFFF")], anim_in=tanim("slide-up", duration=0.3),
              name=f"Hora {i + 1}")
    flash(t, 2.95, 0.4, peak=1.0)
    label(t, t.track("text", "Cierre"), "y así empezó todo", 7.2, 1.8, Box(60, 1740, 960, 100), "Caveat", 80,
          "#FFFFFF", weight=700, layers=[shadow("#000000", 0, 4, 16, 0.5), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.6), name="Cierre")
    song(t, "upbeat", 7)
    return t


def dia_energia():
    t = T(50, "yt-dia-energia", "Mi energía durante el día", "My energy through the day",
          D + ["energía", "energy", "batería", "humor"], 12.0, thumb_at=4.0)
    steps = [("07:00", 35, "😴", "recién despierta", "y5-morning-01"), ("09:00", 90, "☕", "después del café", "coffee-03"),
             ("15:00", 55, "😐", "bajón de la tarde", "study-03"), ("21:00", 12, "🛌", "modo ahorro", "y5-h-cozy-04")]
    slides(t, [s[4] for s in steps], 0, 3.0, transition="crossfade", tdur=0.4, kb_amount=0.06,
           labels=[f"Momento {i + 1}" for i in range(4)])
    shade_bottom(t, 900, 0.75)
    card = Box(80, 1260, 920, 520)
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.2, 11.8, card, 48, pop(0, 0.4, 0.8),
          layers=[fill("#FFFFFF", 0.16), stroke(2, "#FFFFFF", 0.4)])
    bat = Box(140, 1520, 560, 200)
    rrect(t, t.track("shape", "Batería"), "#FFFFFF", 0.2, 11.8, bat, 30, layers=hollow_ring("#FFFFFF", 10))
    rrect(t, t.track("shape", "Batería"), "#FFFFFF", 0.2, 11.8, Box(706, 1580, 30, 80), 10)
    colours = {35: "#FFD60A", 90: "#38B000", 55: "#FFD60A", 12: "#EF233C"}
    lv = t.track("shape", "Nivel")
    for i, (h, pct, ic, txt, _) in enumerate(steps):
        a = i * 3.0
        d = 3.0 if i < 3 else 12 - a
        prev = steps[i - 1][1] if i else 0
        wfull = 520
        box = Box(160, 1540, wfull * pct / 100, 160)
        sx0 = max(0.02, prev / pct) if pct else 1
        t.solid(lv, colours[pct], a, d, box, [(0, {"sx": sx0, "dx": -box.w * (1 - sx0) / 2}, "out"), (0.8, {})],
                radius=18, kind="rounded-rectangle")
        label(t, t.track("text", "Hora"), h, a, d, Box(140, 1300, 400, 120), "Montserrat", 100, "#FFFFFF", weight=800,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Hora {i + 1}")
        label(t, t.track("text", "Estado"), txt, a, d, Box(140, 1420, 820, 70), "Montserrat", 44, "#FFFFFF", weight=500,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Estado {i + 1}")
        label(t, t.track("text", "Porcentaje"), f"{pct} %", a, d, Box(760, 1300, 220, 120), "Montserrat", 64,
              "#FFFFFF", weight=800, align="right", anim_in=tanim("pop", duration=0.3), name=f"Porcentaje {i + 1}")
        emoji(t, ic, a, d, centered(860, 1620, 170, 170), 120, motion=pop(0, 0.4))
    label(t, t.track("text", "Título"), "mi batería social", 0.3, 11.7, Box(60, 120, 960, 130), "Caveat", 110,
          "#FFFFFF", weight=700, layers=[shadow("#000000", 0, 4, 20, 0.5), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.8), name="Título")
    song(t, "fun", 2, 0.75)
    return t


def dia_grwm_lista():
    t = T(51, "yt-dia-grwm-lista", "Lo que uso hoy (lista)", "What I'm using today (list)",
          G + ["lista", "list", "maquillaje", "skincare"], 10.0, thumb_at=7.8, background="#EFE7FA")
    bg_gradient(t, [(0, "#EFE7FA"), (1, "#FBE7EF")], angle=90)
    circle_photo(t, "y5-grwm-06", 0.2, 9.8, centered(540, 480, 560, 560), pop(0, 0.6, 0.6), ring_colour="#FFFFFF",
                 ring_width=16, label="Tu foto")
    label(t, t.track("text", "Título"), "lo que uso hoy", 0.6, 9.4, Box(60, 790, 960, 150), "Pacifico", 104, "#6D4C9F",
          weight=400, anim_in=tanim("pop", duration=0.5), name="Título")
    items = ["Protector solar", "Base en barra", "Máscara de pestañas", "Bálsamo con color", "Perfume suave"]
    cols = ["#B79CED", "#F2A7C3", "#9AD0EC", "#F7C59F", "#A7E3B5"]
    for i, it in enumerate(items):
        at = 1.4 + i * 1.1
        y = 980 + i * 165
        t.solid(t.track("shape", "Número"), cols[i], at, 10 - at, centered(170, y + 60, 100, 100), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Número"), str(i + 1), at, 10 - at, centered(170, y + 60, 100, 100), "Fredoka", 56,
              "#FFFFFF", weight=700, editable=False, motion=pop(0, 0.35))
        rrect(t, t.track("shape", "Fila"), "#FFFFFF", at + 0.1, 9.9 - at, Box(250, y, 770, 120), 60,
              [(0, {"sx": 0.0, "dx": -385}, "out"), (0.4, {})], alpha=0.85)
        label(t, t.track("text", "Producto"), it, at + 0.3, 9.7 - at, Box(300, y + 15, 700, 90), "Fredoka", 58,
              "#4B3869", weight=600, align="left", anim_in=tanim("fade", duration=0.3), name=f"Producto {i + 1}")
    dots(t, ["#FFFFFF", "#F2A7C3"], 10, 0, 10, seed=511, size=(14, 28), kinds=("heart", "star"), drift=50,
         area=Box(0, 100, 1080, 700))
    song(t, "fun", 4, 0.7)
    return t


def dia_numeros():
    t = T(52, "yt-dia-numeros", "Mi día en números", "My day in numbers",
          D + ["números", "numbers", "estadísticas", "resumen"], 10.0, thumb_at=7.2, background="#F3ECE2")
    bg(t, "#F3ECE2")
    rounded_photo(t, "y5-morning-07", 0, 10, Box(60, 80, 960, 700), kb(10, 1.0, 1.06), radius=0.08, label_="Tu foto")
    label(t, t.track("text", "Título"), "mi día en números", 0.4, 9.6, Box(60, 820, 960, 130), "DM Serif Display", 96,
          COCOA, weight=400, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1), name="Título")
    tiles = [("☕", "2", "cafés"), ("👟", "9.432", "pasos"), ("📖", "30", "páginas"), ("💧", "2 L", "de agua")]
    for i, (ic, n, txt) in enumerate(tiles):
        col, row = i % 2, i // 2
        box = Box(60 + col * 500, 990 + row * 440, 460, 400)
        at = 1.2 + i * 0.6
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", at, 10 - at, box, 40, pop(0, 0.45, 0.6),
              layers=[shadow(COCOA, 0, 8, 20, 0.12), fill(["#DDE5D3", "#F3D9C9", "#E6DDF1", "#D6E8F0"][i]),
                      no_stroke()])
        emoji(t, ic, at + 0.1, 9.9 - at, centered(box.cx, box.y + 90, 140, 120), 80, motion=pop(0, 0.4))
        label(t, t.track("text", "Número"), n, at + 0.2, 9.8 - at, centered(box.cx, box.y + 225, 440, 140), "DM Serif Display",
              120, COCOA, weight=400, anim_in=tanim("stamp", duration=0.3), name=f"Número {i + 1}")
        label(t, t.track("text", "Dato"), txt, at + 0.3, 9.7 - at, centered(box.cx, box.y + 335, 440, 70), "Quicksand",
              46, COCOA, weight=600, name=f"Dato {i + 1}")
    song(t, "calm", 4, 0.75)
    return t


def dia_rutina_split():
    t = T(53, "yt-dia-rutina-split", "Rutina minimalista (pantalla dividida)", "Minimal routine (split screen)",
          D + ["minimalista", "minimal", "rutina", "routine"], 12.0, w=True, thumb_at=4.0, background="#F4F1EA")
    bg(t, "#F4F1EA")
    steps = [("06:30", "despertar", "y5-h-cozy-02"), ("07:00", "moverme un poco", "y5-yoga-01"),
             ("07:45", "desayunar", "h-food-03"), ("08:30", "a trabajar", "y5-h-lab-03")]
    vt = t.track("video", "Fotos")
    prev = None
    for i, (_, _, s) in enumerate(steps):
        a = i * 3.0
        d = 3.0 if i < 3 else 12 - a
        c = t.photo(vt, s, a, d + (0.5 if i < 3 else 0), Box(960, 0, 960, 1080), kb(d, 1.0, 1.06),
                    label=f"Foto {i + 1}")
        if prev:
            t.transition(vt, prev, c, "wipe_up", 0.5)
        prev = c
    ht, at_ = t.track("text", "Hora"), t.track("text", "Paso")
    for i, (h, txt, _) in enumerate(steps):
        a = i * 3.0
        d = 3.0 if i < 3 else 12 - a
        label(t, ht, h, a + 0.1, d - 0.1, Box(120, 330, 760, 260), "Playfair Display", 220, "#1B1B1B", weight=500,
              align="left", anim_in=tanim("rise", duration=0.5), anim_out=tanim("fade", duration=0.2) if i < 3 else None,
              name=f"Hora {i + 1}")
        label(t, at_, txt, a + 0.25, d - 0.25, Box(130, 600, 760, 90), "Montserrat", 50, "#6B6358", weight=500,
              align="left", spacing=4, anim_in=tanim("fade", duration=0.4),
              anim_out=tanim("fade", duration=0.2) if i < 3 else None, name=f"Paso {i + 1}")
        t.solid(t.track("shape", "Paso"), "#1B1B1B", 0, 12, Box(130 + i * 60, 800, 40, 6),
                opacity=keys([(0, 0.2, "hold"), (a, 0.2, "smooth"), (a + 0.3, 1.0)]) if i else const_one())
    label(t, t.track("text", "Título"), "MI MAÑANA", 0.2, 11.8, Box(130, 180, 700, 60), "Montserrat", 36, "#1B1B1B",
          weight=700, spacing=12, align="left", name="Etiqueta")
    song(t, "calm", 2, 0.7)
    return t


TEMPLATES = [vlog_titulo_calle, vlog_ruta_mapa, vlog_dia_1, vlog_hora_lugar, vlog_timelapse, vlog_stats_viaje,
             vlog_noche, vlog_billete, vlog_cinematico, vlog_barrios, vlog_postal, vlog_mapa_zoom, vlog_gastos,
             vlog_llegando, vlog_top3, vlog_metro, vlog_clima, vlog_resumen,
             expl_por_que, expl_resaltador, expl_recortes, expl_mapa_zoom, expl_datos, expl_puntos, expl_barras,
             expl_dona, expl_linea_tiempo, expl_pizarra, expl_mito, expl_comparar, expl_fuente, expl_glosario,
             expl_proceso, expl_lupa, expl_capitulos, expl_opina,
             dia_0630, dia_checklist, dia_linea_rutina, dia_grwm_pasos, dia_outfit, dia_cozy, dia_diario, dia_reloj,
             dia_grwm_espejo, dia_estudio, dia_antes_despues, dia_noche, dia_fin_semana, dia_alarma, dia_energia,
             dia_grwm_lista, dia_numeros, dia_rutina_split]
