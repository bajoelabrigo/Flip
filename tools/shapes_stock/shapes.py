"""The 200 shapes of Stock › Formas (tools/shapes_stock).

Each entry: id, Spanish and English names, category, tags and a builder. A builder returns a
path (list of subpaths, see geometry.py) or a ``(fills, holes)`` pair: with the nonzero rule the
holes are wound the other way, so a pin keeps its hole without switching to evenodd. Shapes with
``rule="evenodd"`` (frames, rings) XOR their subpaths instead.

    from shapes import SHAPES      # list of dicts, in catalogue order
"""

from __future__ import annotations

import math
import random

from geometry import (arc_point, arc_segments, circle, ellipse, flatten_sub, heart_sub, lerp, poly, radial, rect, regular,
                      reverse_sub, ring_arc, rotate, rounded_poly, scale, smooth, smooth_open_segs, star_points, stroke_polyline,
                      torn_edges, transform, translate, wobble)

SHAPES: list = []
_order = {"n": 0}


def S(sid, es, en, cat, tags, build, rule="nonzero"):
    _order["n"] += 1
    SHAPES.append({"id": sid, "es": es, "en": en, "category": cat, "tags": tags, "build": build,
                   "rule": rule, "order": _order["n"] * 10})


# --------------------------------------------------------------------------------------------
# Small builders shared by several categories

def rrect(x, y, w, h, r):
    return rounded_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], r)


def pill(x, y, w, h):
    r = min(w, h) / 2
    if w >= h:
        sp = [(x + r, y), ("L", (x + w - r, y))]
        sp += arc_segments(x + w - r, y + r, r, r, -90, 90)
        sp.append(("L", (x + r, y + h)))
        sp += arc_segments(x + r, y + r, r, r, 90, 270)
    else:
        sp = [(x + w, y + r), ("L", (x + w, y + h - r))]
        sp += arc_segments(x + r, y + h - r, r, r, 0, 180)
        sp.append(("L", (x, y + r)))
        sp += arc_segments(x + r, y + r, r, r, 180, 360)
    return sp


def bumps(points, k=0.55, closed=False):
    """Segments bulging outward (to the left of travel on screen) between consecutive points."""
    segs = []
    pts = list(points) + ([points[0]] if closed else [])
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L  # outward for clockwise-on-screen travel
        segs.append(("C", (a[0] + nx * L * k, a[1] + ny * L * k), (b[0] + nx * L * k, b[1] + ny * L * k), b))
    return segs


def scallop(n, cx, cy, r, k=0.45, rot=-90):
    pts = regular(n, cx, cy, r, rot)
    return [pts[0]] + bumps(pts, k, closed=True)


def scallop_rect(x, y, w, h, step, k=0.5):
    pts = []
    nx, ny = max(2, round(w / step)), max(2, round(h / step))
    for i in range(nx):
        pts.append((x + w * i / nx, y))
    for i in range(ny):
        pts.append((x + w, y + h * i / ny))
    for i in range(nx):
        pts.append((x + w - w * i / nx, y + h))
    for i in range(ny):
        pts.append((x, y + h - h * i / ny))
    return [pts[0]] + bumps(pts, k, closed=True)


def cloud(x0, y0, w, h, top, k=0.6, flat=False):
    """One outline: bumps along `top` (normalised 0..1 points from bottom-left to bottom-right),
    then a rounded (or flat) bottom back to the start."""
    pts = [(x0 + u * w, y0 + v * h) for u, v in top]
    sp = [pts[0]] + bumps(pts, k)
    a, b = pts[-1], pts[0]
    if flat:
        sp.append(("L", b))
    else:
        sp.append(("C", (a[0] + w * 0.04, a[1] + h * 0.3), (b[0] - w * 0.04, b[1] + h * 0.3), b))
    return sp


CLOUD_TOP = [(0.06, 0.8), (0.12, 0.5), (0.36, 0.3), (0.64, 0.24), (0.86, 0.46), (0.95, 0.8)]


def drop_sub(cx, top, r):
    cy = top + r * 1.8
    return [(cx, top), ("C", (cx + r * 0.3, top + r * 0.5), (cx + r, cy - r * 0.55), (cx + r, cy))] + \
        arc_segments(cx, cy, r, r, 0, 180) + [("C", (cx - r, cy - r * 0.55), (cx - r * 0.3, top + r * 0.5), (cx, top))]


def arrow_pts(length, shaft, head_w, head_len, x=0.0, y=0.0):
    s, hw = shaft / 2, head_w / 2
    return [(x, y - s), (x + length - head_len, y - s), (x + length - head_len, y - hw), (x + length, y),
            (x + length - head_len, y + hw), (x + length - head_len, y + s), (x, y + s)]


def head_at(p, ang, size, width=None):
    width = size * 1.1 if width is None else width
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = (p[0] + ux * size * 0.7, p[1] + uy * size * 0.7)
    b = (p[0] - ux * size * 0.3, p[1] - uy * size * 0.3)
    return poly([tip, (b[0] + nx * width / 2, b[1] + ny * width / 2), (b[0] - nx * width / 2, b[1] - ny * width / 2)])


def sample(f, a, b, n):
    return [f(a + (b - a) * i / (n - 1)) for i in range(n)]


def star(n, ratio, r=50, rot=-90):
    return poly(star_points(n, 50, 50, r, r * ratio, rot))


def sparkle(cx, cy, r, pinch=0.12):
    p = r * pinch
    return [(cx, cy - r), ("Q", (cx + p, cy - p), (cx + r, cy)), ("Q", (cx + p, cy + p), (cx, cy + r)),
            ("Q", (cx - p, cy + p), (cx - r, cy)), ("Q", (cx - p, cy - p), (cx, cy - r))]


def bubble_outline(x, y, w, h, r, tx, tw, tip, tail_r=1.0):
    pts = [(x, y), (x + w, y), (x + w, y + h), (tx + tw, y + h), tip, (tx, y + h), (x, y + h)]
    return rounded_poly(pts, [r, r, r, 1.5, tail_r, 1.5, r])


def circle_intersections(c1, r1, c2, r2):
    d = math.dist(c1, c2)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx = c1[0] + a * (c2[0] - c1[0]) / d
    my = c1[1] + a * (c2[1] - c1[1]) / d
    return ((mx + h * (c2[1] - c1[1]) / d, my - h * (c2[0] - c1[0]) / d),
            (mx - h * (c2[1] - c1[1]) / d, my + h * (c2[0] - c1[0]) / d))


def crescent(c1, r1, c2, r2):
    p, q = circle_intersections(c1, r1, c2, r2)
    ang = lambda c, pt: math.degrees(math.atan2(pt[1] - c[1], pt[0] - c[0]))  # noqa: E731
    a0, a1 = ang(c1, p), ang(c1, q)
    # Outer arc the long way round (away from the bite), inner arc back inside.
    while a1 < a0:
        a1 += 360
    b0, b1 = ang(c2, q), ang(c2, p)
    while b1 > b0:
        b1 -= 360
    outer_len = a1 - a0
    if outer_len < 180:
        a1 -= 360
        b1 += 360
    return [p] + arc_segments(c1[0], c1[1], r1, r1, a0, a1) + arc_segments(c2[0], c2[1], r2, r2, b0, b1)


def blob(seed, n=9, base=40, var=10, ry=1.0):
    rnd = random.Random(seed)
    rs = [base + rnd.uniform(-var, var) for _ in range(n)]
    pts = [(50 + rs[i] * math.cos(2 * math.pi * i / n), 50 + ry * rs[i] * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return smooth(pts)


def wave_band(w, amp, periods, thick, phase=0.0, n=None, bottom_wave=True):
    n = n or int(periods * 8) + 1
    top = [(w * i / (n - 1), amp * math.sin(2 * math.pi * periods * i / (n - 1) + phase)) for i in range(n)]
    sp = [top[0]] + smooth_open_segs(top)
    if bottom_wave:
        bot = [(x, y + thick) for x, y in reversed(top)]
        sp += [("L", bot[0])] + smooth_open_segs(bot)
    else:
        sp += [("L", (w, thick)), ("L", (0, thick))]
    return sp


def wavy(w, amp, periods, y=0.0, phase=0.0):
    n = int(periods * 8) + 1
    return [(w * i / (n - 1), y + amp * math.sin(2 * math.pi * periods * i / (n - 1) + phase)) for i in range(n)]


def concave_edges(x, y, w, h, notch_r, n_top, n_side):
    """Rectangle whose edges are a row of concave half-circle bites (postage stamp)."""
    sp = [(x, y)]

    def edge(a, b, n, inward_ang):
        out = []
        for i in range(n):
            s = lerp(a, b, (i + 0.5 - 0.35) / n)
            e = lerp(a, b, (i + 0.5 + 0.35) / n)
            c = lerp(s, e, 0.5)
            out.append(("L", s))
            rr = math.dist(s, e) / 2
            ang = math.degrees(math.atan2(s[1] - c[1], s[0] - c[0]))
            out += arc_segments(c[0], c[1], rr, rr, ang, ang - 180)
        out.append(("L", b))
        return out

    sp += edge((x, y), (x + w, y), n_top, 90)
    sp += edge((x + w, y), (x + w, y + h), n_side, 180)
    sp += edge((x + w, y + h), (x, y + h), n_top, 270)
    sp += edge((x, y + h), (x, y), n_side, 0)
    return sp


def ticket_sub(x, y, w, h, r_notch, corner=4):
    """Rectangle with a concave half-circle notch in the middle of each short side."""
    cy = y + h / 2
    sp = [(x + corner, y), ("L", (x + w - corner, y)), ("Q", (x + w, y), (x + w, y + corner)),
          ("L", (x + w, cy - r_notch))]
    sp += arc_segments(x + w, cy, r_notch, r_notch, -90, -270)
    sp += [("L", (x + w, y + h - corner)), ("Q", (x + w, y + h), (x + w - corner, y + h)), ("L", (x + corner, y + h)),
           ("Q", (x, y + h), (x, y + h - corner)), ("L", (x, cy + r_notch))]
    sp += arc_segments(x, cy, r_notch, r_notch, 90, -90)
    sp += [("L", (x, y + corner)), ("Q", (x, y), (x + corner, y))]
    return sp


def _shout():
    rnd = random.Random(11)
    pts = []
    n = 24
    for i in range(n):
        a = math.radians(-90 + 360 * i / n)
        r = (50 if i % 2 == 0 else 36) * rnd.uniform(0.9, 1.06)
        pts.append((50 + r * math.cos(a) * 1.25, 46 + r * math.sin(a)))
        if i == 15:  # the long spike that points at the speaker
            pts.append((18, 100))
    return pts


# --------------------------------------------------------------------------------------------
# Hearts (12)

S("heart-classic", "Corazón clásico", "Classic heart", "hearts", ["amor", "love", "corazón", "heart"],
  lambda: [heart_sub(50, 45, 100, 90)])
S("heart-round", "Corazón redondo", "Round heart", "hearts", ["amor", "love", "tierno", "cute"],
  lambda: [heart_sub(50, 45, 100, 84, fat=1.28)])
S("heart-tilted", "Corazón inclinado", "Tilted heart", "hearts", ["amor", "love", "san valentín", "valentine"],
  lambda: rotate([heart_sub(50, 45, 100, 90)], -16, 50, 45))
S("heart-double", "Corazones dobles", "Double hearts", "hearts", ["pareja", "couple", "amor", "love"],
  lambda: [heart_sub(40, 45, 80, 72)] + rotate([heart_sub(78, 62, 52, 47)], 14, 78, 62))
S("heart-cracked", "Corazón roto", "Broken heart", "hearts", ["desamor", "heartbreak", "triste", "sad"],
  lambda: ([heart_sub(50, 45, 100, 90)],
           [poly([(49, 27), (55, 38), (45, 49), (55, 61), (47, 72), (50, 81), (48, 81), (43, 72), (51, 61),
                  (41, 49), (51, 38), (46, 27)])]))
S("heart-ring", "Corazón de contorno", "Heart outline", "hearts", ["marco", "frame", "amor", "love"],
  lambda: [heart_sub(50, 45, 100, 90), heart_sub(50, 47.5, 76, 66)], "evenodd")
S("heart-hand-drawn", "Corazón a mano", "Hand-drawn heart", "hearts", ["dibujo", "doodle", "amor", "love"],
  lambda: [smooth(wobble(flatten_sub(heart_sub(50, 45, 100, 90), 5)[:-1:2], 1.4, 7))])
S("heart-pixel", "Corazón pixelado", "Pixel heart", "hearts", ["juego", "game", "retro", "8 bits"],
  lambda: [rect(c * 10, r * 10, 10.02, 10.02) for r, row in enumerate(
      ["0110110", "1111111", "1111111", "1111111", "0111110", "0011100", "0001000"]) for c, v in enumerate(row) if v == "1"])
S("hearts-trio", "Tres corazones", "Three hearts", "hearts", ["amor", "love", "flotando", "floating"],
  lambda: [heart_sub(36, 58, 64, 58)] + rotate([heart_sub(84, 26, 32, 29)], 16, 84, 26)
  + rotate([heart_sub(84, 74, 22, 20)], -12, 84, 74))
S("heart-arrow", "Corazón flechado", "Heart with arrow", "hearts", ["cupido", "cupid", "amor", "love"],
  lambda: [heart_sub(50, 50, 80, 72)] + rotate(
      [rect(-6, 47.5, 102, 5), poly([(96, 41), (110, 50), (96, 59)]), poly([(-6, 47.5), (-14, 40), (-2, 40), (6, 47.5)]),
       poly([(-6, 52.5), (-14, 60), (-2, 60), (6, 52.5)])], -28, 50, 50))
S("heart-keyhole", "Corazón con cerradura", "Heart with keyhole", "hearts", ["candado", "lock", "amor", "love"],
  lambda: ([heart_sub(50, 45, 100, 90)],
           [[arc_point(50, 38, 9, 9, 115)] + arc_segments(50, 38, 9, 9, 115, 425) + [("L", (55, 64)), ("L", (45, 64))]]))
S("heart-star-hole", "Corazón con estrella", "Heart with star", "hearts", ["estrella", "star", "amor", "love"],
  lambda: ([heart_sub(50, 45, 100, 90)], [poly(star_points(5, 50, 48, 20, 8.5))]))

# --------------------------------------------------------------------------------------------
# Stars (14)

for n, ratio, es_name, en_name in [(4, 0.38, "Estrella de 4 puntas", "4-point star"), (5, 0.42, "Estrella", "Star"),
                                   (6, 0.55, "Estrella de 6 puntas", "6-point star"),
                                   (8, 0.55, "Estrella de 8 puntas", "8-point star"),
                                   (10, 0.62, "Estrella de 10 puntas", "10-point star"),
                                   (12, 0.68, "Estrella de 12 puntas", "12-point star")]:
    S(f"star-{n}", es_name, en_name, "stars", ["estrella", "star", "brillo", "shine"],
      (lambda n=n, ratio=ratio: [star(n, ratio)]))
S("star-5-rounded", "Estrella redondeada", "Rounded star", "stars", ["estrella", "star", "suave", "soft"],
  lambda: [rounded_poly(star_points(5, 50, 50, 50, 23), [7, 2.5] * 5)])
S("star-6-rounded", "Estrella de 6 redondeada", "Rounded 6-point star", "stars", ["estrella", "star"],
  lambda: [rounded_poly(star_points(6, 50, 50, 50, 28), [6, 2.5] * 6)])
S("sparkle", "Destello", "Sparkle", "stars", ["brillo", "sparkle", "magia", "magic"], lambda: [sparkle(50, 50, 50)])
S("sparkle-trio", "Tres destellos", "Sparkle trio", "stars", ["brillo", "sparkle", "nuevo", "new"],
  lambda: [sparkle(40, 58, 40), sparkle(84, 20, 16), sparkle(86, 84, 11)])
S("star-shooting", "Estrella fugaz", "Shooting star", "stars", ["deseo", "wish", "noche", "night"],
  lambda: [rounded_poly(star_points(5, 72, 30, 28, 12.5, -80), [4, 1.5] * 5)]
  + [stroke_polyline(sample(lambda t: (8 + t * 50, 92 - t * 46 + d), 0, 1, 12), [w * t for t in [i / 11 for i in range(12)]], "round")
     for d, w in [(-14, 7), (0, 9), (14, 7)]])
S("star-ring", "Estrella de contorno", "Star outline", "stars", ["marco", "frame", "estrella", "star"],
  lambda: [rounded_poly(star_points(5, 50, 50, 50, 23), [4, 2] * 5),
           rounded_poly(star_points(5, 50, 51.5, 33, 15), [3, 1.5] * 5)], "evenodd")
S("star-chubby", "Estrella gordita", "Chubby star", "stars", ["tierno", "cute", "estrella", "star"],
  lambda: [rounded_poly(star_points(5, 50, 50, 50, 32), [12, 6] * 5)])
S("star-thin", "Estrella fina", "Thin star", "stars", ["elegante", "elegant", "estrella", "star"],
  lambda: [star(5, 0.22)])

# --------------------------------------------------------------------------------------------
# Speech bubbles (14)

S("bubble-round", "Bocadillo redondo", "Round speech bubble", "bubbles", ["diálogo", "speech", "hablar", "talk"],
  lambda: [ellipse(50, 40, 50, 36), smooth([(20, 62), (38, 72), (8, 96)], 0.0)])
S("bubble-oval-left", "Bocadillo ovalado", "Oval speech bubble", "bubbles", ["diálogo", "speech", "cómic", "comic"],
  lambda: [ellipse(56, 40, 54, 34), [(30, 60), ("Q", (26, 82), (4, 96)), ("Q", (34, 88), (48, 70))]])
S("bubble-square", "Bocadillo cuadrado", "Square speech bubble", "bubbles", ["diálogo", "speech", "chat"],
  lambda: [bubble_outline(0, 0, 100, 74, 3, 18, 18, (14, 100), 1)])
S("bubble-rounded", "Bocadillo redondeado", "Rounded speech bubble", "bubbles", ["mensaje", "message", "chat"],
  lambda: [bubble_outline(0, 0, 120, 74, 18, 82, 16, (104, 100), 2)])
S("bubble-shout", "Bocadillo de grito", "Shout bubble", "bubbles", ["grito", "shout", "cómic", "comic", "boom"],
  lambda: [poly(_shout())])
S("bubble-thought", "Bocadillo de pensamiento", "Thought bubble", "bubbles", ["pensar", "think", "idea", "sueño"],
  lambda: [cloud(0, 0, 110, 72, [(0.06, 0.75), (0.08, 0.38), (0.3, 0.12), (0.56, 0.06), (0.82, 0.18), (0.97, 0.48),
                                 (0.9, 0.82), (0.64, 0.95), (0.36, 0.95), (0.12, 0.9)], 0.5, flat=True),
           circle(26, 88, 6.5), circle(12, 100, 4)])
S("bubble-double", "Dos bocadillos", "Chat bubbles", "bubbles", ["chat", "conversación", "conversation"],
  lambda: [bubble_outline(0, 0, 80, 52, 16, 14, 14, (8, 70), 2),
           bubble_outline(44, 42, 76, 48, 16, 96, 12, (112, 106), 2)])
S("bubble-typing", "Escribiendo…", "Typing bubble", "bubbles", ["chat", "escribiendo", "typing", "mensaje"],
  lambda: ([bubble_outline(0, 0, 120, 70, 35, 18, 18, (6, 96), 2)],
           [circle(34, 35, 9), circle(60, 35, 9), circle(86, 35, 9)]))
S("bubble-callout", "Globo de nota", "Callout box", "bubbles", ["nota", "note", "aviso", "callout"],
  lambda: [bubble_outline(0, 0, 130, 70, 8, 56, 18, (65, 100), 1)])
S("bubble-pill", "Bocadillo píldora", "Pill speech bubble", "bubbles", ["mensaje", "message", "chat"],
  lambda: [pill(0, 0, 150, 56), poly([(34, 46), (54, 50), (24, 76)])])
S("bubble-outline", "Bocadillo de contorno", "Speech bubble outline", "bubbles", ["marco", "frame", "diálogo", "speech"],
  lambda: [bubble_outline(0, 0, 120, 74, 20, 22, 18, (12, 102), 2), rrect(9, 9, 102, 56, 13)], "evenodd")
S("bubble-whisper", "Bocadillo suave", "Soft bubble", "bubbles", ["susurro", "whisper", "suave", "soft"],
  lambda: [smooth(wobble(regular(14, 50, 40, 52, ry=36), 2.2, 5)), poly([(64, 64), (80, 66), (90, 94)])])
S("bubble-comic", "Bocadillo de cómic", "Comic bubble", "bubbles", ["cómic", "comic", "historieta"],
  lambda: [ellipse(54, 40, 54, 38), [(64, 70), ("C", (64, 86), (78, 96), (96, 98)), ("C", (84, 90), (78, 80), (82, 70))]])
S("bubble-circle", "Bocadillo circular", "Circle speech bubble", "bubbles", ["diálogo", "speech", "círculo"],
  lambda: [circle(46, 46, 46), poly([(70, 76), (100, 100), (82, 64)])])

# --------------------------------------------------------------------------------------------
# Clouds (9)

S("cloud-classic", "Nube", "Cloud", "clouds", ["cielo", "sky", "clima", "weather"], lambda: [cloud(0, 0, 140, 90, CLOUD_TOP)])
S("cloud-puffy", "Nube esponjosa", "Puffy cloud", "clouds", ["cielo", "sky", "suave", "soft"],
  lambda: [cloud(0, 0, 180, 90, [(0.04, 0.82), (0.06, 0.55), (0.2, 0.36), (0.38, 0.2), (0.58, 0.16), (0.76, 0.3),
                                 (0.9, 0.5), (0.96, 0.82)], 0.62)])
S("cloud-long", "Nube alargada", "Long cloud", "clouds", ["cielo", "sky", "horizonte"],
  lambda: [cloud(0, 0, 240, 70, [(0.02, 0.86), (0.08, 0.5), (0.2, 0.34), (0.33, 0.3), (0.46, 0.22), (0.6, 0.28),
                                 (0.73, 0.3), (0.86, 0.42), (0.97, 0.86)], 0.55, flat=True)])
S("cloud-rain", "Nube con lluvia", "Rain cloud", "clouds", ["lluvia", "rain", "clima", "weather"],
  lambda: [cloud(0, 0, 140, 78, CLOUD_TOP, flat=True)] + [rotate([drop_sub(x, 84, 6)], 15, x, 96)[0] for x in (34, 70, 106)])
S("cloud-storm", "Nube con rayo", "Storm cloud", "clouds", ["tormenta", "storm", "rayo", "lightning"],
  lambda: [cloud(0, 0, 140, 78, CLOUD_TOP, flat=True),
           poly([(74, 62), (94, 62), (82, 86), (98, 86), (60, 132), (70, 98), (56, 98)])])
S("cloud-ring", "Nube de contorno", "Cloud outline", "clouds", ["marco", "frame", "cielo", "sky"],
  lambda: [cloud(0, 0, 140, 90, CLOUD_TOP), scale([cloud(0, 0, 140, 90, CLOUD_TOP)], 0.78, 0.7, 70, 52)[0]], "evenodd")
S("cloud-sun", "Sol y nube", "Sun and cloud", "clouds", ["sol", "sun", "clima", "weather", "verano"],
  lambda: [circle(92, 34, 26)] + [rotate([rrect(89, -14, 6, 14, 3)], a, 92, 34)[0] for a in range(0, 360, 45)]
  + [cloud(0, 22, 130, 84, CLOUD_TOP)])
S("cloud-bumpy", "Nube de algodón", "Cotton cloud", "clouds", ["cielo", "sky", "tierno", "cute"],
  lambda: [cloud(0, 0, 150, 90, [(0.04, 0.8), (0.04, 0.6), (0.12, 0.44), (0.24, 0.32), (0.36, 0.22), (0.5, 0.18),
                                 (0.63, 0.22), (0.75, 0.3), (0.86, 0.42), (0.95, 0.58), (0.96, 0.8)], 0.7)])
S("cloud-flat", "Nube de base plana", "Flat-bottom cloud", "clouds", ["cielo", "sky", "minimalista"],
  lambda: [cloud(0, 0, 150, 80, [(0.0, 1.0), (0.1, 0.6), (0.34, 0.34), (0.64, 0.3), (0.88, 0.56), (1.0, 1.0)], 0.55, flat=True)])

# --------------------------------------------------------------------------------------------
# Torn paper (10)

S("paper-strip", "Tira de papel rasgado", "Torn paper strip", "paper", ["papel", "paper", "collage", "rasgado"],
  lambda: [poly(torn_edges([(0, 0), (300, 0), (300, 64), (0, 64)], 7, 3.2, 1, edges={0, 2}))])
S("paper-strip-vertical", "Tira vertical rasgada", "Vertical torn strip", "paper", ["papel", "paper", "collage"],
  lambda: [poly(torn_edges([(0, 0), (64, 0), (64, 260), (0, 260)], 7, 3.2, 2, edges={1, 3}))])
S("paper-torn", "Papel rasgado", "Torn paper", "paper", ["papel", "paper", "nota", "note"],
  lambda: [poly(torn_edges([(0, 0), (160, 0), (160, 120), (0, 120)], 6, 2.4, 3))])
S("paper-note-torn-top", "Hoja arrancada", "Torn-off note", "paper", ["nota", "note", "cuaderno", "notebook"],
  lambda: [poly(torn_edges([(0, 0), (120, 0), (120, 150), (0, 150)], 6, 3, 4, edges={0}))])
S("paper-tape", "Cinta adhesiva", "Tape strip", "paper", ["cinta", "tape", "scrapbook", "collage"],
  lambda: [poly([(0, 0), (240, 0)] + [(240 + (6 if i % 2 else 0), 60 * i / 10) for i in range(1, 11)]
                + [(0, 60)] + [((6 if i % 2 else 0), 60 - 60 * i / 10) for i in range(1, 10)])])
S("paper-hole", "Papel con agujero rasgado", "Paper with torn hole", "paper", ["papel", "paper", "revelar", "reveal"],
  lambda: [rect(0, 0, 160, 120),
           poly(radial(48, 80, 60, lambda a, r=random.Random(5): 38 * (0.92 + 0.16 * random.Random(int(a * 7)).random())))],
  "evenodd")
S("paper-torn-circle", "Círculo de papel rasgado", "Torn paper circle", "paper", ["papel", "paper", "círculo"],
  lambda: [poly(radial(70, 50, 50, lambda a: 50 * (0.95 + 0.06 * random.Random(int(a * 13)).random())))])
S("paper-sticky", "Nota adhesiva", "Sticky note", "paper", ["nota", "note", "post-it", "recordatorio"],
  lambda: [[(0, 0), ("L", (100, 0)), ("L", (100, 76)), ("Q", (94, 96), (76, 100)), ("L", (0, 100))],
           [(80, 99), ("Q", (84, 84), (99, 80)), ("Q", (98, 92), (80, 99))]])
S("paper-notebook", "Hoja de cuaderno", "Notebook page", "paper", ["cuaderno", "notebook", "escuela", "school"],
  lambda: [rrect(0, 0, 110, 140, 4)] + [circle(14, 18 + i * 21, 5) for i in range(6)], "evenodd")
S("paper-torn-corner", "Esquina rasgada", "Torn corner", "paper", ["papel", "paper", "esquina", "corner"],
  lambda: [poly(torn_edges([(0, 0), (120, 0), (0, 120)], 6, 3, 9, edges={1}))])

def _hand_arrow():
    curve = sample(lambda t: (t * 150, 60 - 46 * math.sin(t * math.pi * 0.85) + 6 * math.sin(t * 9)), 0, 1, 36)
    end, before = curve[-1], curve[-4]
    ang = math.atan2(end[1] - before[1], end[0] - before[0])
    wing = lambda d: (end[0] - 34 * math.cos(ang + d), end[1] - 34 * math.sin(ang + d))  # noqa: E731
    return [stroke_polyline(curve, [6 + 4 * t for t in [i / 35 for i in range(36)]]),
            stroke_polyline([wing(0.6), end, wing(-0.6)], 10)]


# --------------------------------------------------------------------------------------------
# Arrows (16)

S("arrow-right", "Flecha", "Arrow", "arrows", ["flecha", "arrow", "señalar", "point"],
  lambda: [poly(arrow_pts(160, 30, 80, 60, 0, 40))])
S("arrow-block", "Flecha gruesa", "Block arrow", "arrows", ["flecha", "arrow", "dirección"],
  lambda: [rounded_poly(arrow_pts(140, 56, 100, 54, 0, 50), 3)])
S("arrow-double", "Flecha doble", "Double arrow", "arrows", ["flecha", "arrow", "ambos", "both"],
  lambda: [poly([(0, 40), (50, 0), (50, 26), (150, 26), (150, 0), (200, 40), (150, 80), (150, 54), (50, 54), (50, 80)])])
S("arrow-curved", "Flecha curva", "Curved arrow", "arrows", ["flecha", "arrow", "curva", "curve"],
  lambda: [ring_arc(70, 90, 78, 56, 200, 318)] + [head_at(arc_point(70, 90, 67, 67, 318), 48, 44)])
S("arrow-u-turn", "Flecha de vuelta", "U-turn arrow", "arrows", ["volver", "back", "u", "regresar"],
  lambda: [stroke_polyline([(20, 130), (20, 50)] + sample(lambda t: (50 - 30 * math.cos(t), 50 - 30 * math.sin(t)), 0, math.pi, 24)
                           + [(80, 50), (80, 104)], 18, "butt"), head_at((80, 112), 90, 44)])
S("arrow-circular", "Flecha circular", "Circular arrow", "arrows", ["repetir", "repeat", "ciclo", "loop"],
  lambda: [ring_arc(50, 50, 50, 34, -40, 250)] + [head_at(arc_point(50, 50, 42, 42, -40), -40 - 90, 34)])
S("arrow-hand-drawn", "Flecha a mano", "Hand-drawn arrow", "arrows", ["dibujo", "doodle", "flecha", "arrow"],
  lambda: _hand_arrow())
S("chevron", "Cheurón", "Chevron", "arrows", ["flecha", "arrow", "siguiente", "next"],
  lambda: [poly([(0, 0), (40, 0), (80, 50), (40, 100), (0, 100), (40, 50)])])
S("chevron-double", "Cheurón doble", "Double chevron", "arrows", ["avanzar", "forward", "rápido", "fast"],
  lambda: [poly([(x, 0), (x + 34, 0), (x + 70, 50), (x + 34, 100), (x, 100), (x + 36, 50)]) for x in (0, 48)])
S("chevron-triple", "Cheurón triple", "Triple chevron", "arrows", ["avanzar", "forward", "deslizar", "swipe"],
  lambda: [poly([(x, 0), (x + 26, 0), (x + 58, 50), (x + 26, 100), (x, 100), (x + 32, 50)]) for x in (0, 40, 80)])
S("arrow-diagonal", "Flecha diagonal", "Diagonal arrow", "arrows", ["subir", "up", "crecer", "growth"],
  lambda: rotate([poly(arrow_pts(150, 28, 76, 56, 0, 50))], -45, 75, 50))
S("arrow-zigzag", "Flecha en zigzag", "Zigzag arrow", "arrows", ["crecimiento", "growth", "gráfico", "chart"],
  lambda: [stroke_polyline([(0, 100), (40, 56), (70, 78), (118, 26)], 14, "round"), head_at((122, 22), -46, 50)])
S("arrow-circle", "Flecha en círculo", "Arrow in circle", "arrows", ["botón", "button", "siguiente", "next"],
  lambda: [circle(50, 50, 50), poly(arrow_pts(56, 14, 38, 26, 22, 50))], "evenodd")
S("arrow-refresh", "Flechas de actualizar", "Refresh arrows", "arrows", ["actualizar", "refresh", "ciclo", "sync"],
  lambda: [ring_arc(50, 50, 50, 36, 200, 330), head_at(arc_point(50, 50, 43, 43, 330), 60, 32),
           ring_arc(50, 50, 50, 36, 20, 150), head_at(arc_point(50, 50, 43, 43, 150), 240, 32)])
S("arrow-notched", "Flecha con cola", "Notched arrow", "arrows", ["flecha", "arrow", "dirección"],
  lambda: [poly([(0, 18), (110, 18), (110, 0), (160, 40), (110, 80), (110, 62), (0, 62), (22, 40)])])
S("arrow-cursor", "Cursor", "Cursor", "arrows", ["clic", "click", "ratón", "mouse", "puntero"],
  lambda: [rounded_poly([(0, 0), (70, 64), (40, 66), (58, 104), (42, 112), (24, 74), (0, 96)], 2)])

# --------------------------------------------------------------------------------------------
# Badges (10)

S("badge-scallop-12", "Insignia festoneada", "Scalloped badge", "badges", ["insignia", "badge", "sello"],
  lambda: [scallop(12, 50, 50, 45, 0.5)])
S("badge-scallop-16", "Insignia de 16 ondas", "16-scallop badge", "badges", ["insignia", "badge", "oferta", "sale"],
  lambda: [scallop(16, 50, 50, 46, 0.5)])
S("badge-rosette", "Escarapela", "Rosette", "badges", ["premio", "award", "ganador", "winner"],
  lambda: [poly([(30, 70), (48, 72), (36, 128), (26, 112), (14, 118)]), poly([(70, 70), (52, 72), (64, 128), (74, 112), (86, 118)]),
           scallop(14, 50, 46, 42, 0.5)])
S("badge-hexagon", "Insignia hexagonal", "Hexagon badge", "badges", ["insignia", "badge", "logro", "achievement"],
  lambda: [rounded_poly(regular(6, 50, 50, 50), 9)])
S("badge-medal", "Medalla", "Medal", "badges", ["medalla", "medal", "premio", "award", "primer lugar"],
  lambda: [poly([(18, 0), (40, 0), (60, 52), (44, 58)]), poly([(82, 0), (60, 0), (40, 52), (56, 58)]), circle(50, 82, 34)])
S("badge-sticker-ring", "Sticker con anillo", "Ringed sticker", "badges", ["sticker", "etiqueta", "label"],
  lambda: [circle(50, 50, 50), circle(50, 50, 42), circle(50, 50, 38)], "evenodd")
S("badge-burst", "Explosión de oferta", "Starburst", "badges", ["oferta", "sale", "nuevo", "new", "promo"],
  lambda: [star(20, 0.84)])
S("badge-flower", "Insignia de flor", "Flower badge", "badges", ["flor", "flower", "insignia", "badge"],
  lambda: [scallop(8, 50, 50, 40, 0.7)])
S("badge-octagon", "Insignia octogonal", "Octagon badge", "badges", ["insignia", "badge", "etiqueta"],
  lambda: [rounded_poly(regular(8, 50, 50, 50, -67.5), 6)])
S("badge-banner", "Insignia con cinta", "Badge with ribbon", "badges", ["premio", "award", "calidad", "quality"],
  lambda: [scallop(18, 80, 46, 46, 0.28), poly([(0, 58), (160, 58), (146, 75), (160, 92), (0, 92), (14, 75)])])

# --------------------------------------------------------------------------------------------
# Seals and stamps (9)

S("seal-zigzag", "Sello dentado", "Zigzag seal", "seals", ["sello", "seal", "garantía", "guarantee"], lambda: [star(24, 0.88)])
S("seal-wavy", "Sello ondulado", "Wavy seal", "seals", ["sello", "seal", "certificado"],
  lambda: [poly(radial(240, 50, 50, lambda a: 46 + 4 * math.cos(math.radians(a) * 14)))])
S("seal-wavy-soft", "Sello de ondas suaves", "Soft wavy seal", "seals", ["sello", "seal", "flor", "suave"],
  lambda: [poly(radial(240, 50, 50, lambda a: 42 + 8 * math.cos(math.radians(a) * 8)))])
S("seal-postage", "Estampilla", "Postage stamp", "seals", ["estampilla", "stamp", "correo", "mail"],
  lambda: [concave_edges(0, 0, 100, 124, 4, 8, 10)])
S("seal-stamp-round", "Sello redondo", "Round stamp", "seals", ["sello", "stamp", "aprobado", "approved"],
  lambda: [star(28, 0.9), circle(50, 50, 38), circle(50, 50, 33)], "evenodd")
S("seal-notched", "Sello con muescas", "Notched seal", "seals", ["sello", "seal", "insignia"],
  lambda: [rounded_poly(star_points(16, 50, 50, 50, 43), 1.5)])
S("seal-wax", "Sello de lacre", "Wax seal", "seals", ["lacre", "wax", "carta", "letter", "boda"],
  lambda: [smooth(radial(16, 50, 50, lambda a: 47 + 3 * math.sin(a * 0.7) + 2 * math.cos(a * 1.3))),
           circle(50, 50, 33), circle(50, 50, 29)], "evenodd")
S("seal-gear", "Engranaje", "Gear", "seals", ["engranaje", "gear", "ajustes", "settings"],
  lambda: [rounded_poly([pt for i in range(12) for pt in (
      arc_point(50, 50, 50, 50, i * 30 - 9), arc_point(50, 50, 50, 50, i * 30 + 9),
      arc_point(50, 50, 39, 39, i * 30 + 13), arc_point(50, 50, 39, 39, i * 30 + 17))], 1.5), circle(50, 50, 16)], "evenodd")
S("seal-certificate", "Sello de certificado", "Certificate seal", "seals", ["certificado", "certificate", "premio", "award"],
  lambda: ([poly([(30, 80), (46, 82), (36, 130), (28, 118), (16, 124)]), poly([(70, 80), (54, 82), (64, 130), (72, 118), (84, 124)]),
            star(22, 0.86)], [circle(50, 50, 27)]))

# --------------------------------------------------------------------------------------------
# Frames (12)

S("frame-rect", "Marco rectangular", "Rectangle frame", "frames", ["marco", "frame", "borde", "border"],
  lambda: [rect(0, 0, 160, 120), rect(10, 10, 140, 100)], "evenodd")
S("frame-rounded", "Marco redondeado", "Rounded frame", "frames", ["marco", "frame", "borde", "border"],
  lambda: [rrect(0, 0, 160, 120, 22), rrect(10, 10, 140, 100, 14)], "evenodd")
S("frame-circle", "Aro", "Circle frame", "frames", ["marco", "frame", "círculo", "circle", "perfil"],
  lambda: [circle(50, 50, 50), circle(50, 50, 43)], "evenodd")
S("frame-double-ring", "Marco de doble aro", "Double ring frame", "frames", ["marco", "frame", "elegante"],
  lambda: [circle(50, 50, 50), circle(50, 50, 46), circle(50, 50, 42), circle(50, 50, 36)], "evenodd")
S("frame-ornate", "Marco clásico", "Classic frame", "frames", ["marco", "frame", "vintage", "elegante"],
  lambda: [[(14, 0), ("L", (146, 0)), ("Q", (146, 14), (160, 14)), ("L", (160, 106)), ("Q", (146, 106), (146, 120)),
            ("L", (14, 120)), ("Q", (14, 106), (0, 106)), ("L", (0, 14)), ("Q", (14, 14), (14, 0))],
           rrect(14, 14, 132, 92, 6)], "evenodd")
S("frame-scalloped", "Marco festoneado", "Scalloped frame", "frames", ["marco", "frame", "tierno", "cute"],
  lambda: [scallop_rect(4, 4, 152, 112, 15, 0.45), rrect(14, 14, 132, 92, 4)], "evenodd")
S("frame-hexagon", "Marco hexagonal", "Hexagon frame", "frames", ["marco", "frame", "hexágono"],
  lambda: [rounded_poly(regular(6, 50, 50, 50), 4), rounded_poly(regular(6, 50, 50, 42), 3)], "evenodd")
S("frame-heart", "Marco de corazón", "Heart frame", "frames", ["marco", "frame", "amor", "love"],
  lambda: [heart_sub(50, 45, 100, 90), heart_sub(50, 46.5, 84, 74)], "evenodd")
S("frame-arch", "Marco de arco", "Arch frame", "frames", ["marco", "frame", "arco", "arch", "boho"],
  lambda: [[(0, 140), ("L", (0, 50))] + arc_segments(50, 50, 50, 50, 180, 360) + [("L", (100, 140))],
           [(9, 131), ("L", (9, 50))] + arc_segments(50, 50, 41, 41, 180, 360) + [("L", (91, 131))]], "evenodd")
S("frame-polaroid", "Marco de foto instantánea", "Instant photo frame", "frames", ["foto", "photo", "polaroid", "recuerdo"],
  lambda: [rect(0, 0, 100, 120), rect(7, 7, 86, 86)], "evenodd")
S("frame-film", "Marco de película", "Film frame", "frames", ["cine", "film", "película", "movie"],
  lambda: [rect(0, 0, 160, 120), rect(10, 24, 140, 72)] + [rrect(6 + i * 16, 6, 9, 11, 2) for i in range(10)]
  + [rrect(6 + i * 16, 103, 9, 11, 2) for i in range(10)], "evenodd")
S("frame-brackets", "Esquinas de enfoque", "Corner brackets", "frames", ["enfoque", "focus", "esquinas", "corners", "cámara"],
  lambda: [poly([(0, 0), (40, 0), (40, 9), (9, 9), (9, 40), (0, 40)]),
           poly([(160, 0), (160, 40), (151, 40), (151, 9), (120, 9), (120, 0)]),
           poly([(160, 120), (120, 120), (120, 111), (151, 111), (151, 80), (160, 80)]),
           poly([(0, 120), (0, 80), (9, 80), (9, 111), (40, 111), (40, 120)])])

# --------------------------------------------------------------------------------------------
# Nature (16)

S("drop", "Gota", "Drop", "nature", ["agua", "water", "gota", "drop"], lambda: [drop_sub(50, 0, 36)])
S("drops-duo", "Dos gotas", "Two drops", "nature", ["agua", "water", "lluvia", "rain"],
  lambda: [drop_sub(40, 10, 34), drop_sub(94, 0, 16)])
S("leaf", "Hoja", "Leaf", "nature", ["hoja", "leaf", "planta", "plant", "eco"],
  lambda: rotate([[(0, 50), ("C", (25, 4), (75, 4), (100, 50)), ("C", (75, 96), (25, 96), (0, 50))],
                  rrect(-24, 47, 30, 6, 3)], -35, 50, 50))
S("leaf-vein", "Hoja con nervio", "Leaf with vein", "nature", ["hoja", "leaf", "otoño", "autumn"],
  lambda: rotate([[(0, 50), ("C", (25, 4), (75, 4), (100, 50)), ("C", (75, 96), (25, 96), (0, 50))],
                  [(10, 49), ("Q", (50, 46), (88, 50)), ("Q", (50, 54), (10, 51))]], -35, 50, 50), "evenodd")
S("leaf-round", "Hoja redonda", "Round leaf", "nature", ["hoja", "leaf", "planta", "plant"],
  lambda: rotate([[(10, 50), ("C", (20, -4), (90, -4), (100, 50)), ("C", (90, 104), (20, 104), (10, 50))],
                  rrect(-18, 47, 32, 6, 3)], -45, 50, 50))
S("leaf-slits", "Hoja tropical", "Tropical leaf", "nature", ["tropical", "monstera", "hoja", "leaf", "verano"],
  lambda: [heart_sub(50, 50, 100, 100, fat=1.2)]
  + [rotate([ellipse(x, y, 13, 3.2)], ang, x, y)[0] for x, y, ang in [(20, 36, 30), (80, 36, -30), (22, 58, 10), (78, 58, -10), (34, 76, -20), (66, 76, 20)]],
  "evenodd")
S("leaf-maple", "Hoja de arce", "Maple leaf", "nature", ["otoño", "autumn", "arce", "maple"],
  lambda: [poly([(50, 0), (60, 20), (72, 14), (68, 40), (88, 26), (86, 36), (100, 40), (88, 52), (94, 58), (66, 64), (68, 74),
                 (52, 68), (53, 100), (47, 100), (48, 68), (32, 74), (34, 64), (6, 58), (12, 52), (0, 40), (14, 36), (12, 26),
                 (32, 40), (28, 14), (40, 20)])])
S("flower-5", "Flor", "Flower", "nature", ["flor", "flower", "primavera", "spring"],
  lambda: [rotate([ellipse(50, 24, 17, 26)], a, 50, 50)[0] for a in range(0, 360, 72)] + [circle(50, 50, 14)])
S("flower-round", "Flor de pétalos redondos", "Round-petal flower", "nature", ["flor", "flower", "tierno", "cute"],
  lambda: [circle(*arc_point(50, 50, 30, 30, a), 20) for a in range(-90, 270, 60)] + [circle(50, 50, 22)])
S("flower-daisy", "Margarita", "Daisy", "nature", ["margarita", "daisy", "flor", "flower"],
  lambda: [rotate([ellipse(50, 20, 7, 20)], a, 50, 50)[0] for a in range(0, 360, 30)] + [circle(50, 50, 14)])
S("tulip", "Tulipán", "Tulip", "nature", ["tulipán", "tulip", "flor", "flower"],
  lambda: [[(20, 10), ("L", (34, 22)), ("L", (50, 4)), ("L", (66, 22)), ("L", (80, 10)), ("C", (84, 44), (74, 62), (50, 62)),
            ("C", (26, 62), (16, 44), (20, 10))], rect(47, 58, 6, 52),
           [(50, 100), ("C", (40, 80), (26, 74), (16, 76)), ("C", (22, 92), (36, 100), (50, 102))]])
S("sprout", "Brote", "Sprout", "nature", ["brote", "sprout", "crecer", "grow", "eco"],
  lambda: [rrect(46, 40, 8, 64, 3), [(50, 46), ("C", (40, 20), (16, 16), (0, 22)), ("C", (8, 44), (30, 54), (50, 48))],
           [(50, 40), ("C", (58, 12), (82, 4), (100, 8)), ("C", (94, 32), (72, 44), (50, 42))]])
S("tree-pine", "Pino", "Pine tree", "nature", ["pino", "pine", "árbol", "tree", "navidad"],
  lambda: [rounded_poly([(50, 0), (78, 34), (22, 34)], 3), rounded_poly([(50, 18), (86, 62), (14, 62)], 3),
           rounded_poly([(50, 40), (96, 92), (4, 92)], 3), rect(43, 88, 14, 22)])
S("cactus", "Cactus", "Cactus", "nature", ["cactus", "desierto", "desert", "planta"],
  lambda: [pill(36, 0, 28, 120), stroke_polyline([(40, 70), (14, 70), (14, 34)], 18, "round"),
           stroke_polyline([(60, 56), (86, 56), (86, 24)], 18, "round")])
S("mushroom", "Hongo", "Mushroom", "nature", ["hongo", "mushroom", "bosque", "forest"],
  lambda: [[(0, 52)] + arc_segments(50, 52, 50, 46, 180, 360) + [("Q", (100, 62), (90, 62)), ("L", (10, 62)), ("Q", (0, 62), (0, 52))],
           [(34, 60), ("L", (66, 60)), ("Q", (70, 100), (62, 104)), ("L", (38, 104)), ("Q", (30, 100), (34, 60))]])
S("snowflake", "Copo de nieve", "Snowflake", "nature", ["nieve", "snow", "invierno", "winter", "navidad"],
  lambda: [p for a in range(0, 360, 60) for p in rotate(
      [rrect(46, 0, 8, 50, 4), rotate([rrect(46, 8, 7, 22, 3.5)], 40, 50, 22)[0], rotate([rrect(47, 8, 7, 22, 3.5)], -40, 50, 22)[0]],
      a, 50, 50)])

# --------------------------------------------------------------------------------------------
# Waves (11)

S("wave-strip", "Onda", "Wave", "waves", ["onda", "wave", "agua", "water"], lambda: [wave_band(300, 14, 2, 34)])
S("wave-banner", "Cinta ondulada", "Wavy banner", "waves", ["cinta", "banner", "ondulada", "wavy"],
  lambda: [wave_band(260, 10, 1, 80)])
S("wave-divider", "Separador de ola", "Wave divider", "waves", ["separador", "divider", "fondo", "background"],
  lambda: [[wavy(300, 12, 1.5, 16)[0]] + smooth_open_segs(wavy(300, 12, 1.5, 16)) + [("L", (300, 90)), ("L", (0, 90))]])
S("wave-layers", "Olas en capas", "Layered waves", "waves", ["mar", "sea", "olas", "waves"],
  lambda: [wave_band(300, 10, 2, 22, 0), translate([wave_band(300, 10, 2, 22, 1.4)], 0, 40)[0],
           translate([wave_band(300, 10, 2, 22, 2.8)], 0, 80)[0]])
S("zigzag-strip", "Zigzag", "Zigzag", "waves", ["zigzag", "dinámico", "energy"],
  lambda: [poly([(i * 20, 0 if i % 2 else 24) for i in range(16)] + [(i * 20, (0 if i % 2 else 24) + 22) for i in range(15, -1, -1)])])
S("squiggle", "Garabato ondulado", "Squiggle", "waves", ["garabato", "squiggle", "línea", "line"],
  lambda: [stroke_polyline(sample(lambda t: (t * 260, 20 * math.sin(t * 2 * math.pi * 2.5)), 0, 1, 80), 14)])
S("wave-curl", "Ola rompiente", "Breaking wave", "waves", ["ola", "wave", "surf", "playa", "beach"],
  lambda: [smooth([(0, 100), (10, 70), (30, 40), (56, 16), (84, 8), (104, 20), (108, 42), (92, 54), (80, 44), (88, 32),
                   (74, 30), (60, 46), (56, 72), (72, 96), (100, 100)], 1.0)])
S("wave-flag", "Bandera ondulante", "Waving flag", "waves", ["bandera", "flag", "meta", "goal"],
  lambda: [wave_band(200, 10, 1.2, 100)])
S("wave-scallop", "Cenefa festoneada", "Scalloped edge", "waves", ["cenefa", "edge", "toldo", "awning"],
  lambda: [[(0, 0), ("L", (240, 0)), ("L", (240, 30))] + [s for i in range(8, 0, -1) for s in arc_segments(15 + (i - 1) * 30, 30, 15, 15, 0, 180)]])
S("wave-ripples", "Ondas concéntricas", "Ripples", "waves", ["ondas", "ripples", "agua", "señal", "signal"],
  lambda: [circle(50, 50, r) for r in (50, 44, 36, 30, 22, 16, 8)], "evenodd")
S("wave-sound", "Onda de sonido", "Sound wave", "waves", ["sonido", "sound", "audio", "música", "podcast"],
  lambda: [pill(i * 14, 50 - h / 2, 9, h) for i, h in enumerate([20, 40, 64, 90, 56, 100, 70, 44, 80, 50, 28, 14])])

# --------------------------------------------------------------------------------------------
# Splashes and blobs (10)

for i, seed in enumerate([3, 8, 21], 1):
    S(f"blob-{i}", f"Mancha orgánica {i}", f"Organic blob {i}", "splash", ["mancha", "blob", "orgánico", "organic", "fondo"],
      (lambda seed=seed: [blob(seed)]))
S("blob-wide", "Mancha ancha", "Wide blob", "splash", ["mancha", "blob", "fondo", "background"],
  lambda: scale([blob(31, 10, 42, 8)], 1.9, 1.0, 50, 50))
S("splash-splat", "Salpicadura", "Splat", "splash", ["salpicadura", "splat", "pintura", "paint"],
  lambda: [smooth(radial(26, 50, 50, lambda a: (44 if int(a / (360 / 26) + 0.5) % 2 == 0 else 26) * random.Random(int(a)).uniform(0.8, 1.15)), 0.9)]
  + [circle(*arc_point(50, 50, 56, 56, a), r) for a, r in [(20, 5), (130, 4), (250, 6), (300, 3)]])
S("splash-paint", "Mancha de pintura", "Paint splash", "splash", ["pintura", "paint", "arte", "art"],
  lambda: [smooth(radial(36, 50, 50, lambda a: 30 + (24 if int(a / 10) % 4 == 0 else 0) * random.Random(int(a) + 3).uniform(0.6, 1.0)), 0.7)])
S("splash-ink", "Gota de tinta", "Ink drop", "splash", ["tinta", "ink", "mancha", "stain"],
  lambda: [blob(44, 11, 36, 7)] + [circle(*arc_point(50, 50, 50, 50, a), r) for a, r in [(-40, 6), (200, 4.5), (100, 3.5)]])
S("splash-crown", "Corona de agua", "Water crown", "splash", ["agua", "water", "salpicadura", "splash"],
  lambda: [[(0, 100), ("C", (6, 76), (14, 60), (14, 36)), ("L", (24, 64)), ("L", (36, 24)), ("L", (46, 60)), ("L", (54, 10)),
            ("L", (62, 60)), ("L", (74, 28)), ("L", (80, 64)), ("L", (90, 40)), ("C", (90, 66), (96, 80), (100, 100))]]
  + [circle(14, 24, 6), circle(36, 12, 5), circle(54, 0, 6), circle(76, 16, 5), circle(92, 30, 4)])
S("splash-spray", "Rociado", "Spray dots", "splash", ["puntos", "dots", "rociado", "spray", "confeti"],
  lambda: [circle(random.Random(i).uniform(10, 90), random.Random(i + 99).uniform(10, 90), random.Random(i + 7).uniform(2.5, 8))
           for i in range(26) if math.dist((random.Random(i).uniform(10, 90), random.Random(i + 99).uniform(10, 90)), (50, 50)) < 42])
S("brush-stroke", "Pincelada", "Brush stroke", "splash", ["pincel", "brush", "trazo", "stroke", "pintura"],
  lambda: [poly([(x, y + random.Random(int(x * 3)).uniform(-1.5, 1.5)) for x, y in
                 (flatten_sub(stroke_polyline(
                     sample(lambda t: (t * 220, 8 * math.sin(t * 5)), 0, 1, 40),
                     [60 * (0.12 + 0.88 * math.sin(math.pi * t) ** 0.45) for t in [i / 39 for i in range(40)]], "butt"), 4))])])

# --------------------------------------------------------------------------------------------
# Shields (8)

SHIELD = lambda: [(0, 0), ("L", (100, 0)), ("L", (100, 46)), ("C", (100, 80), (62, 95), (50, 100)),  # noqa: E731
                  ("C", (38, 95), (0, 80), (0, 46))]
S("shield-classic", "Escudo", "Shield", "shields", ["escudo", "shield", "seguridad", "security"], lambda: [SHIELD()])
S("shield-rounded", "Escudo redondeado", "Rounded shield", "shields", ["escudo", "shield", "protección"],
  lambda: [[(14, 0), ("L", (86, 0)), ("Q", (100, 0), (100, 14)), ("L", (100, 46)), ("C", (100, 80), (62, 95), (50, 100)),
            ("C", (38, 95), (0, 80), (0, 46)), ("L", (0, 14)), ("Q", (0, 0), (14, 0))]])
S("shield-peak", "Escudo de pico", "Peaked shield", "shields", ["escudo", "shield", "insignia", "badge"],
  lambda: [[(0, 10), ("Q", (30, 10), (50, 0)), ("Q", (70, 10), (100, 10)), ("L", (100, 50)), ("C", (100, 82), (62, 95), (50, 100)),
            ("C", (38, 95), (0, 82), (0, 50))]])
S("shield-star", "Escudo con estrella", "Shield with star", "shields", ["escudo", "shield", "héroe", "hero"],
  lambda: ([SHIELD()], [poly(star_points(5, 50, 44, 26, 11))]))
S("shield-crest", "Blasón", "Crest", "shields", ["blasón", "crest", "real", "royal", "equipo"],
  lambda: [[(0, 0), ("L", (20, 0)), ("Q", (35, 10), (50, 0)), ("Q", (65, 10), (80, 0)), ("L", (100, 0)), ("L", (100, 46)),
            ("C", (100, 80), (62, 95), (50, 100)), ("C", (38, 95), (0, 80), (0, 46))]])
S("shield-outline", "Escudo de contorno", "Shield outline", "shields", ["escudo", "shield", "marco", "frame"],
  lambda: [SHIELD(), scale([SHIELD()], 0.8, 0.8, 50, 44)[0]], "evenodd")
S("shield-chevron", "Escudo con galón", "Chevron shield", "shields", ["escudo", "shield", "rango", "rank"],
  lambda: ([SHIELD()], [poly([(24, 40), (50, 56), (76, 40), (76, 54), (50, 70), (24, 54)])]))
S("shield-split", "Escudo partido", "Split shield", "shields", ["escudo", "shield", "equipo", "team"],
  lambda: [[(0, 0), ("L", (47, 0)), ("L", (47, 98.5)), ("C", (36, 93), (0, 80), (0, 46))],
           [(53, 0), ("L", (100, 0)), ("L", (100, 46)), ("C", (100, 80), (64, 93), (53, 98.5))]])

# --------------------------------------------------------------------------------------------
# Tags, tickets and ribbons (17)

S("tag-price", "Etiqueta de precio", "Price tag", "labels", ["precio", "price", "oferta", "sale", "tienda", "shop"],
  lambda: [rounded_poly([(0, 40), (34, 0), (150, 0), (150, 80), (34, 80)], [3, 4, 8, 8, 4]), circle(30, 40, 8)], "evenodd")
S("tag-vertical", "Etiqueta colgante", "Hang tag", "labels", ["etiqueta", "tag", "regalo", "gift", "precio"],
  lambda: [rounded_poly([(30, 0), (60, 26), (60, 130), (0, 130), (0, 26)], [3, 3, 7, 7, 3]), circle(30, 24, 7)], "evenodd")
S("ticket", "Boleto", "Ticket", "labels", ["boleto", "ticket", "evento", "event", "cine"],
  lambda: [ticket_sub(0, 0, 180, 80, 12, 6)] + [circle(124, 10 + i * 10, 2.2) for i in range(7)], "evenodd")
S("ticket-stub", "Entrada", "Admission ticket", "labels", ["entrada", "admission", "concierto", "concert"],
  lambda: [[(14, 0), ("L", (146, 0))] + arc_segments(160, 0, 14, 14, 180, 90) + [("L", (160, 66))]
           + arc_segments(160, 80, 14, 14, 270, 180) + [("L", (14, 80))] + arc_segments(0, 80, 14, 14, 0, -90)
           + [("L", (0, 14))] + arc_segments(0, 0, 14, 14, 90, 0)])
S("ribbon-banner", "Cinta de título", "Ribbon banner", "labels", ["cinta", "ribbon", "título", "title"],
  lambda: [poly([(0, 30), (44, 30), (44, 74), (0, 74), (16, 52)]), poly([(220, 30), (176, 30), (176, 74), (220, 74), (204, 52)]),
           rect(24, 14, 172, 48)])
S("ribbon-curved", "Cinta curva", "Curved ribbon", "labels", ["cinta", "ribbon", "logo", "insignia"],
  lambda: [poly([arc_point(110, 230, 210, 210, a) for a in [250 + i * 2 for i in range(21)]]
                + [arc_point(110, 230, 205, 205, 291), arc_point(110, 230, 170, 170, 290)]
                + [arc_point(110, 230, 170, 170, a) for a in [290 - i * 2 for i in range(21)]]
                + [arc_point(110, 230, 175, 175, 249)])])
S("ribbon-folded", "Cinta plegada", "Folded ribbon", "labels", ["cinta", "ribbon", "rótulo", "label"],
  lambda: [rect(20, 0, 160, 44), poly([(0, 18), (34, 18), (34, 62), (0, 62), (12, 40)]),
           poly([(200, 18), (166, 18), (166, 62), (200, 62), (188, 40)])])
S("label-notched", "Etiqueta con muescas", "Notched label", "labels", ["etiqueta", "label", "título", "title"],
  lambda: [poly([(0, 0), (200, 0), (186, 30), (200, 60), (0, 60), (14, 30)])])
S("bookmark", "Marcapáginas", "Bookmark", "labels", ["marcador", "bookmark", "guardar", "save"],
  lambda: [poly([(0, 0), (60, 0), (60, 110), (30, 86), (0, 110)])])
S("label-scalloped", "Etiqueta festoneada", "Scalloped label", "labels", ["etiqueta", "label", "vintage"],
  lambda: [scallop_rect(0, 0, 180, 80, 14, 0.4)])
S("label-tab", "Pestaña", "Tab label", "labels", ["pestaña", "tab", "carpeta", "folder"],
  lambda: [rounded_poly([(0, 30), (14, 0), (70, 0), (84, 30), (160, 30), (160, 110), (0, 110)], [3, 5, 5, 3, 6, 6, 6])])
S("label-signpost", "Letrero de flecha", "Signpost label", "labels", ["letrero", "sign", "dirección", "direction"],
  lambda: [rounded_poly([(0, 0), (150, 0), (190, 35), (150, 70), (0, 70)], [8, 3, 3, 3, 8])])
S("tag-round", "Etiqueta redonda", "Round tag", "labels", ["etiqueta", "tag", "precio", "price"],
  lambda: [circle(50, 50, 50), circle(50, 15, 6)], "evenodd")
S("coupon", "Cupón", "Coupon", "labels", ["cupón", "coupon", "descuento", "discount", "oferta"],
  lambda: [ticket_sub(0, 0, 200, 90, 14, 8)] + [rrect(140, 8 + i * 13, 3, 7, 1.5) for i in range(6)], "evenodd")
S("pennant", "Banderín", "Pennant", "labels", ["banderín", "pennant", "equipo", "team", "fiesta"],
  lambda: [poly([(0, 0), (180, 32), (0, 64)])])
S("bunting", "Guirnalda de banderines", "Bunting", "labels", ["guirnalda", "bunting", "fiesta", "party", "cumpleaños"],
  lambda: [stroke_polyline(sample(lambda t: (t * 280, 18 * math.sin(t * math.pi)), 0, 1, 40), 3, "round")]
  + [rounded_poly([(x - 18, 18 * math.sin(x / 280 * math.pi) - 1), (x + 18, 18 * math.sin(x / 280 * math.pi) - 1),
                   (x, 18 * math.sin(x / 280 * math.pi) + 48)], 2) for x in (30, 82, 140, 198, 250)])
S("banner-wavy", "Banderola", "Wavy banner", "labels", ["banderola", "banner", "anuncio"],
  lambda: [[(0, 0)] + smooth_open_segs(wavy(300, 10, 1)) + [("L", (282, 40))] + [("L", (300, 80))]
           + smooth_open_segs(wavy(300, 10, 1, 80)[::-1]) + [("L", (18, 40))]])

# --------------------------------------------------------------------------------------------
# Symbols (16)

S("pin", "Ubicación", "Location pin", "symbols", ["ubicación", "location", "mapa", "map", "dirección"],
  lambda: ([[(50, 140)] + [("C", (36, 112), (0, 84), (0, 50))] + arc_segments(50, 50, 50, 50, 180, 360)
            + [("C", (100, 84), (64, 112), (50, 140))]], [circle(50, 50, 20)]))
S("check", "Visto bueno", "Check mark", "symbols", ["listo", "done", "correcto", "check", "ok"],
  lambda: [rounded_poly([(0, 56), (16, 40), (40, 64), (98, 6), (114, 22), (40, 96)], 4)])
S("x-mark", "Equis", "X mark", "symbols", ["no", "cerrar", "close", "error", "x"],
  lambda: rotate([rrect(40, -6, 20, 112, 6), rrect(-6, 40, 112, 20, 6)], 45, 50, 50))
S("bolt", "Rayo", "Lightning bolt", "symbols", ["rayo", "bolt", "energía", "energy", "rápido"],
  lambda: [poly([(58, 0), (12, 64), (44, 64), (32, 120), (86, 46), (52, 46), (68, 0)])])
S("crown", "Corona", "Crown", "symbols", ["corona", "crown", "rey", "king", "reina", "queen"],
  lambda: [rounded_poly([(0, 20), (28, 50), (50, 8), (72, 50), (100, 20), (90, 80), (10, 80)], [2, 3, 2, 3, 2, 3, 3]),
           circle(0, 16, 7), circle(50, 4, 7), circle(100, 16, 7), rrect(10, 86, 80, 12, 4)])
S("music-note", "Nota musical", "Music note", "symbols", ["música", "music", "nota", "note", "canción"],
  lambda: [rotate([ellipse(26, 96, 22, 15)], -20, 26, 96)[0], rect(39, 8, 9, 88),
           [(39, 4), ("C", (50, 30), (82, 30), (78, 62)), ("C", (72, 42), (58, 38), (48, 40)), ("L", (48, 4))]])
S("music-notes", "Notas musicales", "Music notes", "symbols", ["música", "music", "notas", "notes"],
  lambda: [rotate([ellipse(22, 100, 20, 14)], -20, 22, 100)[0], rotate([ellipse(92, 88, 20, 14)], -20, 92, 88)[0],
           rect(34, 22, 8, 76), rect(104, 10, 8, 76), poly([(34, 14), (112, 0), (112, 18), (34, 32)])])
S("play-circle", "Botón de reproducir", "Play button", "symbols", ["reproducir", "play", "video", "botón"],
  lambda: ([circle(50, 50, 50)], [rounded_poly([(38, 28), (74, 50), (38, 72)], 4)]))
S("play", "Reproducir", "Play", "symbols", ["reproducir", "play", "video"],
  lambda: [rounded_poly([(0, 0), (90, 52), (0, 104)], 12)])
S("pause", "Pausa", "Pause", "symbols", ["pausa", "pause", "video"],
  lambda: [rrect(0, 0, 32, 100, 8), rrect(56, 0, 32, 100, 8)])
S("moon", "Luna", "Moon", "symbols", ["luna", "moon", "noche", "night", "dormir"],
  lambda: [crescent((50, 50), 50, (78, 34), 42)])
S("sun", "Sol", "Sun", "symbols", ["sol", "sun", "verano", "summer", "día"],
  lambda: [circle(50, 50, 28)] + [rotate([rrect(46, -2, 8, 20, 4)], a, 50, 50)[0] for a in range(0, 360, 30)])
S("house", "Casa", "House", "symbols", ["casa", "house", "hogar", "home", "inmobiliaria"],
  lambda: [rounded_poly([(50, 0), (100, 44), (88, 44), (88, 100), (60, 100), (60, 64), (40, 64), (40, 100), (12, 100), (12, 44), (0, 44)],
                        [3, 3, 1, 3, 1, 2, 2, 1, 3, 1, 3])])
S("bell", "Campana", "Bell", "symbols", ["campana", "bell", "notificación", "notification", "aviso"],
  lambda: [[(50, 0), ("C", (76, 0), (82, 24), (82, 46)), ("C", (82, 66), (90, 74), (100, 82)), ("L", (0, 82)),
            ("C", (10, 74), (18, 66), (18, 46)), ("C", (18, 24), (24, 0), (50, 0))], circle(50, 92, 10)])
S("flame", "Llama", "Flame", "symbols", ["fuego", "fire", "tendencia", "trending", "hot"],
  lambda: [[(40, 0), ("C", (44, 22), (80, 34), (80, 76)), ("C", (80, 98), (64, 112), (44, 112)), ("C", (20, 112), (0, 96), (0, 72)),
            ("C", (0, 50), (14, 40), (20, 26)), ("C", (24, 40), (28, 46), (34, 48)), ("C", (40, 30), (44, 16), (40, 0))]])
S("magnifier", "Lupa", "Magnifier", "symbols", ["buscar", "search", "lupa", "zoom"],
  lambda: ([circle(40, 40, 40), rotate([rrect(70, 33, 50, 14, 7)], 45, 40, 40)[0]], [circle(40, 40, 28)]))

# --------------------------------------------------------------------------------------------
# Geometric (16)

S("plus", "Más", "Plus", "geometric", ["más", "plus", "sumar", "add", "cruz"],
  lambda: [rounded_poly([(34, 0), (66, 0), (66, 34), (100, 34), (100, 66), (66, 66), (66, 100), (34, 100), (34, 66), (0, 66),
                         (0, 34), (34, 34)], [5, 5, 1, 5, 5, 1, 5, 5, 1, 5, 5, 1])])
S("triangle-rounded", "Triángulo redondeado", "Rounded triangle", "geometric", ["triángulo", "triangle"],
  lambda: [rounded_poly(regular(3, 50, 50, 50), 10)])
S("square-rounded", "Cuadrado redondeado", "Rounded square", "geometric", ["cuadrado", "square"], lambda: [rrect(0, 0, 100, 100, 22)])
S("pentagon-rounded", "Pentágono redondeado", "Rounded pentagon", "geometric", ["pentágono", "pentagon"],
  lambda: [rounded_poly(regular(5, 50, 50, 50), 8)])
S("hexagon-rounded", "Hexágono redondeado", "Rounded hexagon", "geometric", ["hexágono", "hexagon", "panal"],
  lambda: [rounded_poly(regular(6, 50, 50, 50, 0), 8)])
S("octagon", "Octágono", "Octagon", "geometric", ["octágono", "octagon", "pare", "stop"],
  lambda: [poly(regular(8, 50, 50, 50, -67.5))])
S("ring", "Anillo", "Ring", "geometric", ["anillo", "ring", "dona", "donut"], lambda: [circle(50, 50, 50), circle(50, 50, 30)], "evenodd")
S("ring-thin", "Anillo fino", "Thin ring", "geometric", ["anillo", "ring", "círculo", "circle"],
  lambda: [circle(50, 50, 50), circle(50, 50, 45)], "evenodd")
S("arch", "Arco", "Arch", "geometric", ["arco", "arch", "arcoíris", "rainbow"],
  lambda: [[(0, 50)] + arc_segments(50, 50, 50, 50, 180, 360) + [("L", (74, 50))] + arc_segments(50, 50, 24, 24, 0, -180)])
S("semicircle", "Semicírculo", "Semicircle", "geometric", ["semicírculo", "half circle", "medio"],
  lambda: [[(0, 50)] + arc_segments(50, 50, 50, 50, 180, 360)])
S("quarter-circle", "Cuarto de círculo", "Quarter circle", "geometric", ["cuarto", "quarter", "esquina", "corner"],
  lambda: [[(0, 100), ("L", (0, 0))] + arc_segments(0, 100, 100, 100, -90, 0)])
S("pill", "Píldora", "Pill", "geometric", ["píldora", "pill", "botón", "button"], lambda: [pill(0, 0, 200, 70)])
S("capsule-vertical", "Cápsula vertical", "Vertical capsule", "geometric", ["cápsula", "capsule"], lambda: [pill(0, 0, 60, 150)])
S("parallelogram-rounded", "Paralelogramo", "Parallelogram", "geometric", ["paralelogramo", "parallelogram", "dinámico"],
  lambda: [rounded_poly([(40, 0), (200, 0), (160, 80), (0, 80)], 6)])
S("rhombus-rounded", "Rombo redondeado", "Rounded rhombus", "geometric", ["rombo", "rhombus", "diamante", "diamond"],
  lambda: [rounded_poly([(50, 0), (100, 60), (50, 120), (0, 60)], 8)])
S("ring-segment", "Arco de anillo", "Ring segment", "geometric", ["progreso", "progress", "anillo", "ring", "gráfico"],
  lambda: [ring_arc(50, 50, 50, 32, -90, 180, round_caps=True)])
