"""Third set, part two (BRIEF.md › «Tanda de 200»): shapes, social (generic, no brands) and faces."""

from __future__ import annotations

import math
import random

from designs3 import sparkle4, twinkle
from kit import (FALL, IN, arrow_head, at, bez, bob, breathe, circle, circle_pts, cyclic, draw_on, heart_path, line, morph,
                 oval, outline, pop, rrect, scale_keys, solid, swing, wave, wobble)
from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, heart, layer_transform,
                    path, polar, rect, star, static, stroke, transform, trim)

C = 256


def sparkle_curved(size=200) -> dict:
    """Four tips joined by concave curves: the soft Y2K sparkle."""
    r = size / 2
    k = r * 0.62
    v = [[0, -r], [r, 0], [0, r], [-r, 0]]
    # Both handles of every tip point at the centre: the sides curve inwards.
    towards = [[0, k], [-k, 0], [0, -k], [k, 0]]
    return {"ty": "sh", "ks": static({"c": True, "v": v, "i": towards, "o": towards})}


# --- Formas --------------------------------------------------------------------------------------


def brillo_y2k() -> Sticker:
    s = Sticker("brillo-y2k", "Brillo Y2K", "Y2K sparkle", "formas", frames=60, order=371,
                tags=["brillo", "y2k", "estética", "estrella"])
    main = s.slot("color", "#C9B8FF")
    small = s.slot("brillos", "#FFFFFF")
    s.layer(group(sparkle_curved(300), stroke("#FFFFFF", 10, small)), group(sparkle_curved(300), fill("#C9B8FF", main)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0, EASE_IN_OUT), (60, 90)]), s=breathe(60, 100, 108)))
    for x, y, sz, d in [(C + 150, C - 140, 90, 0), (C - 160, C + 130, 70, 30), (C + 140, C + 150, 50, 15)]:
        def make(t0, x=x, y=y, sz=sz):
            return [group(sparkle_curved(sz), fill("#FFFFFF", small))], layer_transform(
                p=(x, y), s=scale_keys([(t0, 0, EASE_OUT), (t0 + 12, 100, EASE_IN_OUT), (t0 + 30, 0)]), r=anim([(t0, -45, EASE_OUT), (t0 + 30, 45)]))
        cyclic(s, 60, d, 30, make)
    return s


def sello_ondulado() -> Sticker:
    s = Sticker("sello-ondulado", "Sello ondulado", "Wavy badge", "formas", frames=120, order=372,
                tags=["insignia", "nuevo", "oferta", "retro"])
    main = s.slot("color", "#FF8A3D")
    ring = s.slot("anillo", "#FFFFFF")
    pts = [polar(0, 0, 200 if k % 2 == 0 else 176, k * 15) for k in range(24)]
    s.layer(group(circle(250), stroke("#FFFFFF", 8, ring)), group(path(pts, closed=True, smooth=1.0), fill("#FF8A3D", main)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (120, 30)]), s=breathe(120, 100, 105)))
    return s


def garabato_infinito() -> Sticker:
    s = Sticker("garabato-infinito", "Infinito", "Infinity loop", "formas", frames=60, order=373,
                tags=["infinito", "bucle", "siempre", "garabato"])
    sid = s.slot("color", "#3BCEAC")
    track = s.slot("pista", "#FFFFFF")
    pts = [(190 * math.cos(t) / (1 + math.sin(t) ** 2), 190 * math.sin(t) * math.cos(t) / (1 + math.sin(t) ** 2))
           for t in [k * 2 * math.pi / 24 for k in range(24)]]
    shape = path(pts, closed=True, smooth=1.0)
    s.layer(group(shape, stroke("#FFFFFF", 18, track, o=18)), ks=layer_transform(p=(C, C)))
    s.layer(group(path(pts, closed=True, smooth=1.0), stroke("#3BCEAC", 22, sid),
                  trim(static(38), start=static(0), offset=anim([(0, 0, LINEAR), (60, 360)]))), ks=layer_transform(p=(C, C)))
    return s


def puntos_onda() -> Sticker:
    s = Sticker("puntos-onda", "Puntos en onda", "Dot ripple", "formas", frames=48, order=374,
                tags=["puntos", "fondo", "onda", "patrón"])
    sid = s.slot("color", "#5BC0FF")
    for gx in range(-3, 4):
        for gy in range(-3, 4):
            d = math.hypot(gx, gy)
            if d > 3.3:
                continue
            s.layer(group(circle(34), fill("#5BC0FF", sid)),
                    ks=layer_transform(p=(C + gx * 62, C + gy * 62), s=wave(48, lambda u, d=d: [60 + 50 * (0.5 + 0.5 * math.cos(2 * math.pi * (u - d / 4)))] * 2 + [100], samples=12)))
    return s


def morph_estrella() -> Sticker:
    s = Sticker("morph-estrella", "Estrella que cambia", "Shape morph", "formas", frames=90, order=375,
                tags=["forma", "estrella", "flor", "transformar"])
    sid = s.slot("color", "#FFD23F")
    starp = [polar(0, 0, 190 if k % 2 == 0 else 80, -90 + k * 18) for k in range(20)]
    flower = [polar(0, 0, 185 if k % 2 == 0 else 130, -90 + k * 18) for k in range(20)]
    roundp = [polar(0, 0, 160, -90 + k * 18) for k in range(20)]
    sh = morph([(0, starp), (25, starp), (30, flower), (55, flower), (60, roundp), (85, roundp), (90, starp)], smooth=0.6)
    s.layer(group(sh, fill("#FFD23F", sid)), ks=layer_transform(p=(C, C), r=anim([(0, 0, EASE_IN_OUT), (90, 72)])))
    return s


def anillos_puntos() -> Sticker:
    s = Sticker("anillos-puntos", "Anillos de puntos", "Dot rings", "formas", frames=120, order=376,
                tags=["círculo", "fondo", "girar", "patrón"])
    a = s.slot("exterior", "#FF4D6D")
    b = s.slot("interior", "#FFD23F")
    for r, n, d, col, sid, turn in [(200, 24, 18, "#FF4D6D", a, 15), (130, 16, 22, "#FFD23F", b, -22.5), (60, 8, 20, "#FF4D6D", a, 45)]:
        dots = [circle(d, *polar(0, 0, r, k * 360 / n)) for k in range(n)]
        s.layer(group(*dots, fill(col, sid)), ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (120, turn)])))
    return s


def margarita_retro() -> Sticker:
    s = Sticker("margarita-retro", "Margarita retro", "Retro daisy", "formas", frames=90, order=377,
                tags=["flor", "retro", "groovy", "y2k"])
    pet = s.slot("petalos", "#FFFFFF")
    mid = s.slot("centro", "#FFC93C")
    petals = [group(oval(110, 190, 0, -110), fill("#FFFFFF", pet), tr=transform(r=k * 45)) for k in range(8)]
    s.layer(group(circle(130), fill("#FFC93C", mid)), *petals,
            ks=layer_transform(p=(C, C), r=anim([(0, 0, EASE_IN_OUT), (90, 45)]), s=breathe(90, 96, 104)))
    return s


def asterisco() -> Sticker:
    s = Sticker("asterisco", "Asterisco", "Asterisk", "formas", frames=48, order=378,
                tags=["forma", "estrella", "retro", "énfasis"])
    sid = s.slot("color", "#7B2FF7")
    bars = [group(rrect(64, 360, 32), fill("#7B2FF7", sid), tr=transform(r=k * 60)) for k in range(3)]
    s.layer(*bars, ks=layer_transform(p=(C, C), r=anim([(0, 0, EASE_IN_OUT), (24, 60, EASE_IN_OUT), (48, 120)]),
                                      s=scale_keys([(0, 100, EASE_IN_OUT), (12, 88, EASE_IN_OUT), (24, 100, EASE_IN_OUT), (36, 88, EASE_IN_OUT), (48, 100)])))
    return s


def gota() -> Sticker:
    s = Sticker("gota", "Gota", "Drop", "formas", frames=45, order=379, thumb=0.3,
                tags=["agua", "gota", "líquido", "fresco"])
    sid = s.slot("color", "#5BC0FF")
    drop = path([(0, -120), (68, -8), (75, 50), (0, 118), (-75, 50), (-68, -8)], closed=True, smooth=0.9)
    s.layer(group(drop, fill("#5BC0FF", sid)),
            ks=layer_transform(p=anim([(0, [C, 20, 0], FALL), (16, [C, 285, 0])]), s=scale_keys([(0, 0, EASE_OUT), (6, 100), (15, [92, 108, 100], EASE_OUT), (16, 0)])),
            op=17)
    for k in range(2):
        d = 16 + k * 6
        s.layer(group(oval(120, 30), stroke("#5BC0FF", 8, sid)),
                ks=layer_transform(p=(C, 400), s=scale_keys([(d, 30, EASE_OUT), (d + 22, 280)]), o=anim([(d, 100), (d + 22, 0)])), ip=d, op=d + 22)
    for side in (-1, 1):
        s.layer(group(circle(26), fill("#5BC0FF", sid)),
                ks=layer_transform(p=anim([(16, [C, 390, 0], EASE_OUT), (24, [C + side * 50, 330, 0], ({"x": [0.3], "y": [0]}, {"x": [0.7], "y": [1]})),
                                           (32, [C + side * 75, 400, 0])]), s=scale_keys([(16, 0, EASE_OUT), (20, 100), (30, 100, IN), (32, 0)])), ip=16, op=33)
    return s


def formas_memphis() -> Sticker:
    s = Sticker("formas-memphis", "Formas flotantes", "Floating shapes", "formas", frames=90, order=380,
                tags=["geometría", "memphis", "fondo", "retro"])
    a = s.slot("c1", "#FF4D6D")
    b = s.slot("c2", "#FFD23F")
    c = s.slot("c3", "#3BCEAC")
    tri = path([(0, -70), (62, 40), (-62, 40)], closed=True)
    items = [(tri, a, "#FF4D6D", 150, 160, 0), (circle(110), b, "#FFD23F", 360, 150, 22), (rrect(100, 100, 6), c, "#3BCEAC", 160, 370, 45),
             (path([(-60, 0), (-30, -24), (0, 0), (30, -24), (60, 0)]), a, "#FF4D6D", 370, 360, 67)]
    for k, (shape, sid, col, x, y, ph) in enumerate(items):
        paint = stroke(col, 18, sid) if k != 1 else stroke(col, 18, sid)
        s.layer(group(shape, paint), ks=layer_transform(p=bob(90, x, y, 14, ph), r=wobble(90, 12 if k % 2 else -12)))
    return s


def burbujas() -> Sticker:
    s = Sticker("burbujas", "Burbujas", "Bubbles", "formas", frames=90, order=381,
                tags=["burbujas", "agua", "jabón", "fondo"])
    sid = s.slot("color", "#9AD7FF")
    rng = random.Random(8)
    for k in range(9):
        size = rng.choice([50, 70, 90, 120])
        x = rng.uniform(70, 440)
        start = round(k * 10)
        dur = 70
        def make(t0, x=x, size=size):
            return [group(oval(size * 0.22, size * 0.14, -size * 0.2, -size * 0.22), fill("#FFFFFF", o=85)),
                    group(circle(size), stroke("#9AD7FF", 6, sid)), group(circle(size), fill("#9AD7FF", sid, o=18))], layer_transform(
                p=anim([(t0, [x, 560, 0], LINEAR), (t0 + dur, [x + 30, -60, 0])]),
                s=scale_keys([(t0 + dur - 6, 100, EASE_OUT), (t0 + dur - 2, 125), (t0 + dur, 0)]),
                r=0)
        cyclic(s, 90, start, dur, make)
    return s


def olas() -> Sticker:
    s = Sticker("olas", "Olas", "Waves", "formas", frames=60, order=382,
                tags=["mar", "playa", "agua", "verano"])
    front = s.slot("ola", "#3B82F6")
    back = s.slot("fondo", "#9AD7FF")
    def wave_pts(phase, amp, base):
        pts = [(x, base + amp * math.sin(2 * math.pi * (x / 256) + phase)) for x in range(-20, 533, 46)]
        return pts + [(532, 520), (-20, 520)]
    for col, sid, amp, base, sign in [("#9AD7FF", back, 22, 270, -1), ("#3B82F6", front, 28, 320, 1)]:
        keys = [(round(60 * j / 6), wave_pts(sign * 2 * math.pi * j / 6, amp, base)) for j in range(7)]
        n = len(keys[0][1])
        sh = {"ty": "sh", "ks": {"a": 1, "k": []}}
        for idx, (t, pts) in enumerate(keys):
            b = path(pts[:-2], smooth=1.0)["ks"]["k"]
            v = b["v"] + [list(pts[-2]), list(pts[-1])]
            ins = b["i"] + [[0, 0], [0, 0]]
            outs = b["o"] + [[0, 0], [0, 0]]
            key = {"t": t, "s": [{"c": True, "v": v, "i": ins, "o": outs}]}
            if idx < len(keys) - 1:
                key["o"] = {"x": [0], "y": [0]}
                key["i"] = {"x": [1], "y": [1]}
            sh["ks"]["k"].append(key)
        s.layer(group(sh, fill(col, sid)), ks=layer_transform(p=(0, 0)))
    return s


# --- Redes (genéricas, sin marcas) ---------------------------------------------------------------


def en_vivo() -> Sticker:
    s = Sticker("en-vivo", "En vivo", "Live", "redes", frames=40, order=461,
                tags=["en vivo", "directo", "transmisión", "live"])
    red = s.slot("color", "#FF2D55")
    white = s.slot("ondas", "#FFFFFF")
    s.layer(group(circle(80), fill("#FF2D55", red)), ks=layer_transform(p=(C, C), s=breathe(40, 92, 108)))
    for k in range(2):
        for side in (-1, 1):
            r = 90 + k * 50
            a0 = 180 - 40 if side < 0 else -40
            arcpath = path([polar(0, 0, r, a0 + j * 10) for j in range(9)], smooth=1.0)
            d = k * 6
            s.layer(group(arcpath, stroke("#FFFFFF", 18, white)),
                    ks=layer_transform(p=(C, C), o=anim([(d, 25, EASE_IN_OUT), (d + 10, 100, EASE_IN_OUT), (d + 24, 25), (40, 25)])))
    return s


def nueva_notificacion() -> Sticker:
    s = Sticker("nueva-notificacion", "Nueva notificación", "New notification", "redes", frames=50, order=462,
                tags=["notificación", "aviso", "mensaje", "app"])
    app = s.slot("app", "#7B2FF7")
    badge = s.slot("insignia", "#FF2D55")
    glyph = s.slot("icono", "#FFFFFF")
    bubble = [group(path([(-30, 40), (-50, 72), (0, 46)], closed=True), fill("#FFFFFF", glyph)), group(rrect(150, 100, 40, 0, 0), fill("#FFFFFF", glyph))]
    s.layer(*bubble, group(rrect(260, 260, 64), fill("#7B2FF7", app)),
            ks=layer_transform(p=(C - 10, C + 15), s=scale_keys([(0, 100), (14, 100, EASE_IN_OUT), (18, 94, EASE_OUT), (26, 100)])))
    s.layer(group(circle(96), stroke("#FFFFFF", 10, glyph), fill("#FF2D55", badge)),
            ks=layer_transform(p=(C + 105, C - 90), s=scale_keys([(0, 0), (14, 0, EASE_OUT), (22, 125, EASE_IN_OUT), (28, 92, EASE_IN_OUT), (33, 100), (50, 100)]),
                               r=anim([(0, 0), (28, 0, EASE_IN_OUT), (32, -14, EASE_IN_OUT), (36, 10, EASE_IN_OUT), (40, -4, EASE_IN_OUT), (44, 0)])))
    return s


def republicar() -> Sticker:
    s = Sticker("republicar", "Republicar", "Repost", "redes", frames=48, order=463, thumb=0.1,
                tags=["compartir", "republicar", "repetir", "redes"])
    sid = s.slot("color", "#22C55E")
    top = path([(-120, 40), (-120, -60), (100, -60)])
    bottom = path([(120, -40), (120, 60), (-100, 60)])
    s.layer(group(top, arrow_head((130, -60), (60, -60), 46, 40), stroke("#22C55E", 26, sid)),
            group(bottom, arrow_head((-130, 60), (-60, 60), 46, 40), stroke("#22C55E", 26, sid)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0), (12, 0, EASE_IN_OUT), (30, 180), (48, 180)]),
                               s=scale_keys([(0, 100), (12, 100, EASE_IN_OUT), (21, 86, EASE_IN_OUT), (30, 100)])))
    return s


def seguir_persona() -> Sticker:
    s = Sticker("seguir-persona", "Nuevo seguidor", "New follower", "redes", frames=50, order=464, loop=False,
                tags=["seguir", "seguidor", "agregar", "amigo"])
    person = s.slot("persona", "#FFFFFF")
    badge = s.slot("insignia", "#3B82F6")
    mark = s.slot("marca", "#FFFFFF")
    s.layer(group(circle(130, 0, -80), fill("#FFFFFF", person)), group(path([(-120, 150), (-120, 90), (-80, 30), (80, 30), (120, 90), (120, 150)],
                                                                         closed=True, smooth=0.5), fill("#FFFFFF", person)),
            ks=layer_transform(p=(C - 30, C + 10), s=pop(0, 14)))
    s.layer(group(circle(116), fill("#3B82F6", badge)), ks=layer_transform(p=(C + 120, C + 100), s=pop(10, 12)))
    plus = [line((-26, 0), (26, 0)), line((0, -26), (0, 26))]
    s.layer(group(*plus, stroke("#FFFFFF", 14, mark)), ks=layer_transform(p=(C + 120, C + 100), s=scale_keys([(14, 0, EASE_OUT), (22, 100), (28, 100, IN), (32, 0)]),
                                                                       r=anim([(28, 0, IN), (32, 90)])), op=33)
    s.layer(group(path([(-28, 2), (-8, 22), (30, -18)]), stroke("#FFFFFF", 14, mark), draw_on(32, 10, EASE_OUT)), ks=layer_transform(p=(C + 120, C + 100)), ip=32)
    return s


def reacciones_vivo() -> Sticker:
    s = Sticker("reacciones-vivo", "Reacciones en vivo", "Live reactions", "redes", frames=90, order=465,
                tags=["reacciones", "en vivo", "me gusta", "corazones"])
    h = s.slot("corazon", "#FF2D55")
    st = s.slot("estrella", "#FFD23F")
    fc = s.slot("cara", "#FFC93C")
    def smile():
        return [group(path([(-22, 6), (0, 20), (22, 6)], smooth=1.0), stroke("#4A2B0F", 7)),
                group(circle(12, -15, -10), circle(12, 15, -10), fill("#4A2B0F")), group(circle(76), fill("#FFC93C", fc))]
    kinds = [lambda: [heart("#FF2D55", h, 74)], lambda: [group(star(5, 40, 18, roundness=8), fill("#FFD23F", st))], smile]
    rng = random.Random(14)
    for k in range(9):
        kind = kinds[k % 3]
        sway = rng.uniform(25, 45) * (1 if k % 2 else -1)
        x0 = 330 + rng.uniform(-50, 50)
        size = rng.choice([130, 150, 170])
        def make(t0, kind=kind, sway=sway, x0=x0, size=size):
            return kind(), layer_transform(p=anim([(t0, [x0, 470, 0], EASE_IN_OUT), (t0 + 20, [x0 + sway, 360, 0], EASE_IN_OUT),
                                                   (t0 + 40, [x0 - sway * 1.5, 230, 0], EASE_IN_OUT), (t0 + 60, [x0 + sway * 0.5 - 60, 80, 0])]),
                                           s=scale_keys([(t0, 0, EASE_OUT), (t0 + 10, size)]), o=anim([(t0, 100), (t0 + 45, 100), (t0 + 60, 0)]))
        cyclic(s, 90, k * 10, 60, make)
    return s


def avion_papel() -> Sticker:
    s = Sticker("avion-papel", "Avión de papel", "Paper plane", "redes", frames=60, order=466,
                tags=["enviar", "mensaje", "compartir", "viaje"])
    plane = s.slot("avion", "#FFFFFF")
    fold = s.slot("pliegue", "#C7D2FE")
    trail = s.slot("estela", "#FFFFFF")
    pts = [(60, 400), (160, 330), (230, 380), (300, 300), (430, 150)]
    s.layer(group(path(pts, smooth=1.0), stroke("#FFFFFF", 8, trail, o=60),
                  trim(anim([(0, 0, EASE_IN_OUT), (40, 100)]), start=anim([(12, 0, EASE_IN_OUT), (52, 100)]))), ks=layer_transform(p=(0, 0)))
    body = [group(path([(0, 0), (-110, 48), (-64, 16)], closed=True), fill("#C7D2FE", fold)),
            group(path([(64, 0), (-128, -80), (-80, 0), (-128, 80)], closed=True), fill("#FFFFFF", plane))]
    # Position and heading sampled along the same curve the trail follows.
    curve = path(pts, smooth=1.0)["ks"]["k"]
    def point(u):
        n = len(curve["v"]) - 1
        seg = min(int(u * n), n - 1)
        tt = u * n - seg
        p0 = curve["v"][seg]; p3 = curve["v"][seg + 1]
        p1 = [p0[0] + curve["o"][seg][0], p0[1] + curve["o"][seg][1]]
        p2 = [p3[0] + curve["i"][seg + 1][0], p3[1] + curve["i"][seg + 1][1]]
        x = (1 - tt) ** 3 * p0[0] + 3 * (1 - tt) ** 2 * tt * p1[0] + 3 * (1 - tt) * tt ** 2 * p2[0] + tt ** 3 * p3[0]
        y = (1 - tt) ** 3 * p0[1] + 3 * (1 - tt) ** 2 * tt * p1[1] + 3 * (1 - tt) * tt ** 2 * p2[1] + tt ** 3 * p3[1]
        return x, y
    pk, rk = [], []
    for j in range(21):
        u = j / 20
        ease = 0.5 - 0.5 * math.cos(math.pi * u)
        x, y = point(min(ease, 0.999))
        x2, y2 = point(min(ease + 0.01, 1.0))
        pk.append((round(j * 40 / 20, 2), [x, y, 0], LINEAR))
        rk.append((round(j * 40 / 20, 2), math.degrees(math.atan2(y2 - y, x2 - x)), LINEAR))
    s.layer(*body, ks=layer_transform(p=anim(pk), r=anim(rk), o=anim([(0, 0), (4, 100), (38, 100), (44, 0)]),
                                      s=scale_keys([(0, 140), (40, 100)])), op=45)
    return s


def camara_foto() -> Sticker:
    s = Sticker("camara-foto", "Cámara de fotos", "Photo camera", "redes", frames=40, order=467, thumb=0.8,
                tags=["foto", "cámara", "selfie", "recuerdo"])
    body = s.slot("camara", "#2B2D42")
    lens = s.slot("lente", "#5BC0FF")
    flash = s.slot("flash", "#FFFFFF")
    s.layer(group(circle(40, -60, -60), fill("#FFFFFF", o=70)),
            group(circle(70, -24, -24), fill("#FFFFFF", o=35)), group(circle(140), fill("#5BC0FF", lens)), group(circle(176), fill("#FFFFFF")),
            group(rrect(30, 22, 6, 110, -62), fill("#FFD23F")), group(rrect(90, 40, 12, -60, -122), fill("#2B2D42", body)),
            group(rrect(330, 230, 40, 0, 0), fill("#2B2D42", body)),
            ks=layer_transform(p=(C, C + 20), s=scale_keys([(0, 100), (10, 100, EASE_IN_OUT), (13, 94, EASE_OUT), (20, 100)])))
    s.layer(group(circle(520), fill("#FFFFFF", flash)), ks=layer_transform(p=(C, C), o=anim([(0, 0), (12, 0, EASE_OUT), (14, 85, IN), (22, 0)])), ip=12, op=23)
    return s


def microfono() -> Sticker:
    s = Sticker("microfono", "Micrófono", "Microphone", "redes", frames=36, order=468,
                tags=["podcast", "grabar", "voz", "canción"])
    mic = s.slot("microfono", "#FFFFFF")
    bars = s.slot("nivel", "#FF4D6D")
    s.layer(group(rrect(110, 180, 55, 0, -50), fill("#FFFFFF", mic)),
            group(path([(-80, -10), (-80, 30), (-40, 80), (40, 80), (80, 30), (80, -10)], smooth=0.9), line((0, 90), (0, 140)), line((-50, 140), (50, 140)),
                  stroke("#FFFFFF", 16, mic)), ks=layer_transform(p=(C, C - 10)))
    for side in (-1, 1):
        for k in range(3):
            x = C + side * (130 + k * 36)
            ph = k * 0.22
            s.layer(group(rrect(18, 100, 9), fill("#FF4D6D", bars)),
                    ks=layer_transform(p=(x, C - 40), s=wave(36, lambda u, ph=ph, k=k: [100, 30 + (70 - k * 15) * abs(math.sin(math.pi * 2 * (u + ph))), 100], samples=12)))
    return s


def chat_corazon() -> Sticker:
    s = Sticker("chat-corazon", "Mensaje con amor", "Love message", "redes", frames=40, order=469,
                tags=["mensaje", "amor", "chat", "dm"])
    bub = s.slot("burbuja", "#FFFFFF")
    h = s.slot("corazon", "#FF2D55")
    s.layer(group(path([(-90, 90), (-120, 150), (-30, 100)], closed=True), fill("#FFFFFF", bub)), group(rrect(320, 240, 90), fill("#FFFFFF", bub)),
            ks=layer_transform(p=(C, C - 10), s=pop(0, 14)))
    s.layer(heart("#FF2D55", h, 140), ks=layer_transform(p=(C, C - 6), s=scale_keys([(6, 0, EASE_OUT), (16, 100, EASE_IN_OUT), (22, 100, EASE_IN_OUT), (26, 116, EASE_IN_OUT),
                                                                                      (30, 100, EASE_IN_OUT), (34, 112, EASE_IN_OUT), (40, 100)])))
    return s


def enlace() -> Sticker:
    s = Sticker("enlace", "Enlace", "Link", "redes", frames=40, order=470, loop=False,
                tags=["enlace", "link", "biografía", "web"])
    sid = s.slot("color", "#FFFFFF")
    for side in (-1, 1):
        s.layer(group(rrect(200, 100, 50), stroke("#FFFFFF", 26, sid)),
                ks=layer_transform(p=anim([(0, [C + side * 220, C + side * 220 * 0.0, 0], EASE_OUT), (16, [C + side * 64, C, 0], EASE_IN_OUT), (22, [C + side * 74, C, 0], EASE_IN_OUT),
                                           (28, [C + side * 70, C, 0])]), r=-40, o=anim([(0, 0), (6, 100)])))
    return s


def hashtag() -> Sticker:
    s = Sticker("hashtag", "Numeral", "Hashtag", "redes", frames=40, order=471, loop=False,
                tags=["hashtag", "tendencia", "etiqueta", "redes"])
    sid = s.slot("color", "#3BCEAC")
    strokes = [((-40, -130), (-70, 130)), ((50, -130), (20, 130)), ((-120, -45), (120, -45)), ((-130, 45), (110, 45))]
    for k, (a, b) in enumerate(strokes):
        s.layer(group(line(a, b), stroke("#3BCEAC", 34, sid), draw_on(k * 4, 10, EASE_OUT)), ks=layer_transform(p=(C, C)))
    return s


def verificado() -> Sticker:
    s = Sticker("verificado", "Verificado", "Verified", "redes", frames=36, order=472, loop=False,
                tags=["verificado", "oficial", "aprobado", "insignia"])
    badge = s.slot("insignia", "#3B82F6")
    mark = s.slot("marca", "#FFFFFF")
    pts = [polar(0, 0, 160 if k % 2 == 0 else 136, k * 15) for k in range(24)]
    s.layer(group(path(pts, closed=True, smooth=0.9), fill("#3B82F6", badge)), ks=layer_transform(p=(C, C), s=pop(0, 14), r=anim([(0, -45, EASE_OUT), (14, 0)])))
    s.layer(group(path([(-60, 0), (-18, 42), (64, -44)]), stroke("#FFFFFF", 30, mark), draw_on(12, 12, EASE_OUT)), ks=layer_transform(p=(C, C + 6)))
    return s


# --- Emociones ---------------------------------------------------------------------------------


def face(s: Sticker, colour="#FFC93C"):
    sid = s.slot("cara", colour)
    return group(circle(300), fill(colour, sid), name="cara")


def ink(s: Sticker):
    return s.slot("trazo", "#4A2B0F")


def guino() -> Sticker:
    s = Sticker("cara-guino", "Guiño", "Winking face", "emociones", frames=48, order=551,
                tags=["guiño", "coqueto", "broma", "emoji"])
    line_c = ink(s)
    tongue = s.slot("lengua", "#FF6B8B")
    wink = anim([(0, [100, 100]), (14, [100, 100], EASE_IN_OUT), (18, [100, 10], EASE_IN_OUT), (30, [100, 10], EASE_IN_OUT), (34, [100, 100]), (48, [100, 100])])
    s.layer(group(oval(40, 54, -55, -40), fill("#4A2B0F", line_c), tr=transform(p=(0, 0), s=static([100, 100]))),
            group(group(oval(40, 54), fill("#4A2B0F", line_c)), tr=transform(p=(55, -40), s=wink)),
            group(oval(60, 50, 20, 82), fill("#FF6B8B", tongue)),
            group(path([(-80, 40), (0, 80), (80, 40)], smooth=1.0), stroke("#4A2B0F", 16, line_c)), face(s),
            ks=layer_transform(p=(C, C), r=anim([(0, 0), (14, 0, EASE_IN_OUT), (20, 8, EASE_IN_OUT), (30, 8, EASE_IN_OUT), (36, 0), (48, 0)])))
    return s


def lentes_sol() -> Sticker:
    s = Sticker("cara-lentes", "Con lentes de sol", "Cool face", "emociones", frames=40, order=552, loop=False,
                tags=["cool", "genial", "lentes", "emoji"])
    line_c = ink(s)
    glass = s.slot("lentes", "#111111")
    s.layer(group(path([(-60, 60), (10, 80), (70, 45)], smooth=1.0), stroke("#4A2B0F", 16, line_c)), face(s), ks=layer_transform(p=(C, C), s=pop(0, 12)))
    lenses = [group(path([(-110, -15), (110, -15)]), stroke("#111111", 14, glass)),
              group(path([(-40, -50), (30, -36)]), stroke("#FFFFFF", 8, o=70)),
              group(path([(-120, -55), (-10, -55), (-20, 10), (-100, 10)], closed=True, smooth=0.4), path([(10, -55), (120, -55), (100, 10), (20, 10)], closed=True, smooth=0.4),
                    fill("#111111", glass))]
    s.layer(*lenses, ks=layer_transform(p=anim([(10, [C, -60, 0], FALL), (22, [C, C - 20, 0], EASE_OUT), (26, [C, C - 28, 0], EASE_IN_OUT), (30, [C, C - 20, 0])])), ip=10)
    return s


def llorando() -> Sticker:
    s = Sticker("cara-llorando", "Llorando", "Crying face", "emociones", frames=40, order=553,
                tags=["triste", "llorar", "pena", "emoji"])
    line_c = ink(s)
    tear = s.slot("lagrimas", "#5BC0FF")
    s.layer(group(path([(-80, -50), (-50, -30), (-20, -50)], smooth=1.0), path([(20, -50), (50, -30), (80, -50)], smooth=1.0), stroke("#4A2B0F", 14, line_c)),
            group(path([(-55, 80), (0, 50), (55, 80)], smooth=1.0), stroke("#4A2B0F", 16, line_c)), face(s),
            ks=layer_transform(p=(C, C), s=wave(40, lambda u: [100 + 2 * math.sin(4 * math.pi * u), 100 - 2 * math.sin(4 * math.pi * u), 100])))
    for side in (-1, 1):
        for k in range(2):
            def make(t0, side=side):
                return [group(path([(0, -30), (21, 10), (0, 30), (-21, 10)], closed=True, smooth=0.8), fill("#5BC0FF", tear))], layer_transform(
                    p=anim([(t0, [C + side * 50, C - 20, 0], FALL), (t0 + 20, [C + side * 80, C + 170, 0])]), o=anim([(t0, 0), (t0 + 3, 100), (t0 + 16, 100), (t0 + 20, 0)]))
            cyclic(s, 40, k * 20 + (5 if side > 0 else 0), 20, make)
    return s


def enojado() -> Sticker:
    s = Sticker("cara-enojada", "Enojado", "Angry face", "emociones", frames=36, order=554,
                tags=["enojo", "furia", "molesto", "emoji"])
    line_c = ink(s)
    steam = s.slot("vapor", "#FFFFFF")
    shake = wave(36, lambda u: [C + 6 * math.sin(2 * math.pi * 6 * u), C, 0], samples=24)
    s.layer(group(path([(-90, -70), (-25, -40)]), path([(90, -70), (25, -40)]), stroke("#4A2B0F", 16, line_c)),
            group(oval(34, 34, -55, -18), oval(34, 34, 55, -18), fill("#4A2B0F", line_c)),
            group(path([(-55, 80), (0, 58), (55, 80)], smooth=1.0), stroke("#4A2B0F", 16, line_c)), face(s, "#FF6B4A"), ks=layer_transform(p=shake))
    for side in (-1, 1):
        for k in range(2):
            def make(t0, side=side):
                return [group(circle(46), circle(34, side * 20, -16), fill("#FFFFFF", steam))], layer_transform(
                    p=anim([(t0, [C + side * 130, C - 110, 0], EASE_OUT), (t0 + 18, [C + side * 190, C - 190, 0])]),
                    s=scale_keys([(t0, 30, EASE_OUT), (t0 + 18, 120)]), o=anim([(t0, 100), (t0 + 12, 100), (t0 + 18, 0)]))
            cyclic(s, 36, k * 18 + (9 if side > 0 else 0), 18, make)
    return s


def beso() -> Sticker:
    s = Sticker("cara-beso", "Beso", "Kiss", "emociones", frames=48, order=555,
                tags=["beso", "amor", "muak", "emoji"])
    line_c = ink(s)
    red = s.slot("corazon", "#FF2D55")
    s.layer(group(path([(-80, -40), (-55, -25), (-30, -40)], smooth=1.0), path([(30, -50), (55, -35), (80, -50)], smooth=1.0), stroke("#4A2B0F", 14, line_c)),
            group(path([(10, 40), (36, 56), (14, 70), (36, 86), (10, 100)], smooth=0.8), stroke("#4A2B0F", 14, line_c)), face(s),
            ks=layer_transform(p=(C - 20, C + 20), s=static([90, 90, 100]), r=-8))
    def make(t0):
        return [heart("#FF2D55", red, 90)], layer_transform(
            p=anim([(t0, [C + 30, C + 90, 0], EASE_OUT), (t0 + 30, [C + 160, C - 140, 0])]), s=scale_keys([(t0, 0, EASE_OUT), (t0 + 10, 100, EASE_IN_OUT), (t0 + 30, 130)]),
            o=anim([(t0, 100), (t0 + 22, 100), (t0 + 30, 0)]), r=anim([(t0, -20, EASE_IN_OUT), (t0 + 30, 15)]))
    cyclic(s, 48, 6, 30, make)
    return s


def dormido() -> Sticker:
    s = Sticker("cara-dormida", "Dormido", "Sleeping face", "emociones", frames=60, order=556,
                tags=["sueño", "dormir", "cansado", "zzz"])
    line_c = ink(s)
    zc = s.slot("zetas", "#FFFFFF")
    s.layer(group(path([(-80, -30), (-55, -18), (-30, -30)], smooth=1.0), path([(30, -30), (55, -18), (80, -30)], smooth=1.0), stroke("#4A2B0F", 14, line_c)),
            group(oval(40, 30, 0, 70), fill("#4A2B0F", line_c)), face(s),
            ks=layer_transform(p=(C - 30, C + 40), s=wave(60, lambda u: [86 + 3 * math.sin(2 * math.pi * u), 86 + 3 * math.sin(2 * math.pi * u), 100]), r=-6))
    for k in range(3):
        def make(t0, k=k):
            return [group(path([(-20, -20), (20, -20), (-20, 20), (20, 20)]), stroke("#FFFFFF", 9, zc))], layer_transform(
                p=anim([(t0, [C + 110, C - 60, 0], EASE_OUT), (t0 + 40, [C + 190, C - 210, 0])]), s=scale_keys([(t0, 30, EASE_OUT), (t0 + 40, 140)]),
                o=anim([(t0, 0), (t0 + 6, 100), (t0 + 30, 100), (t0 + 40, 0)]), r=anim([(t0, -10, EASE_IN_OUT), (t0 + 40, 10)]))
        cyclic(s, 60, k * 20, 40, make)
    return s


def estrellado() -> Sticker:
    s = Sticker("cara-estrellas", "Deslumbrado", "Star-struck", "emociones", frames=40, order=557,
                tags=["wow", "increíble", "fan", "emoji"])
    line_c = ink(s)
    st = s.slot("estrellas", "#FF4D6D")
    s.layer(group(path([(-90, 30), (90, 30), (60, 95), (0, 115), (-60, 95)], closed=True, smooth=0.5), fill("#4A2B0F", line_c)), face(s),
            ks=layer_transform(p=(C, C)))
    for side in (-1, 1):
        s.layer(group(star(5, 50, 22, roundness=8), fill("#FF4D6D", st)),
                ks=layer_transform(p=(C + side * 58, C - 40), r=anim([(0, 0, EASE_IN_OUT), (40, 72 * side)]),
                                   s=scale_keys([(0, 100, EASE_IN_OUT), (10, 120, EASE_IN_OUT), (20, 100, EASE_IN_OUT), (30, 120, EASE_IN_OUT), (40, 100)])))
    return s


def cara_fiesta() -> Sticker:
    s = Sticker("cara-fiesta", "Cara de fiesta", "Party face", "emociones", frames=48, order=558,
                tags=["fiesta", "cumpleaños", "celebrar", "emoji"])
    line_c = ink(s)
    hat = s.slot("gorro", "#7B2FF7")
    conf = s.slot("confeti", "#3BCEAC")
    s.layer(group(path([(-80, -40), (-55, -55), (-30, -40)], smooth=1.0), path([(30, -40), (55, -55), (80, -40)], smooth=1.0), stroke("#4A2B0F", 14, line_c)),
            group(path([(-70, 40), (0, 90), (70, 40)], smooth=1.0), stroke("#4A2B0F", 16, line_c)), face(s),
            ks=layer_transform(p=(C, C + 30), s=static([90, 90, 100])))
    s.layer(group(circle(40, 0, -150), fill("#FFD23F")), group(path([(-70, 0), (70, 0), (0, -140)], closed=True), fill("#7B2FF7", hat)),
            ks=layer_transform(p=(C + 70, C - 80), r=wave(48, lambda u: 25 + 6 * math.sin(2 * math.pi * u))))
    rng = random.Random(30)
    for k in range(8):
        x, y = polar(C, C, rng.uniform(180, 230), rng.uniform(150, 390))
        def make(t0, x=x, y=y, k=k):
            return [group(rect((18, 10), r=2) if k % 2 else circle(14), fill("#3BCEAC" if k % 3 else "#FF4D6D", conf if k % 3 else None))], layer_transform(
                p=anim([(t0, [x, y - 40, 0], EASE_OUT), (t0 + 24, [x + 10, y + 40, 0])]), r=anim([(t0, 0, LINEAR), (t0 + 24, 300)]),
                o=anim([(t0, 0), (t0 + 4, 100), (t0 + 18, 100), (t0 + 24, 0)]))
        cyclic(s, 48, k * 6, 24, make)
    return s


def nervioso() -> Sticker:
    s = Sticker("cara-nerviosa", "Nervioso", "Nervous face", "emociones", frames=40, order=559,
                tags=["nervios", "ups", "incómodo", "emoji"])
    line_c = ink(s)
    sweat = s.slot("sudor", "#5BC0FF")
    mouth = path([(-70, 70), (-45, 55), (-20, 70), (5, 55), (30, 70), (55, 55), (75, 68)], smooth=0.7)
    s.layer(group(oval(42, 58, -55, -30), oval(42, 58, 55, -30), fill("#4A2B0F", line_c)), group(mouth, stroke("#4A2B0F", 12, line_c)), face(s),
            ks=layer_transform(p=wave(40, lambda u: [C + 3 * math.sin(2 * math.pi * 5 * u), C, 0], samples=20)))
    s.layer(group(oval(14, 18, -6, -2), fill("#FFFFFF", o=80)), group(path([(0, -40), (22, 4), (0, 24), (-22, 4)], closed=True, smooth=0.8), fill("#5BC0FF", sweat)),
            ks=layer_transform(p=anim([(0, [C + 105, C - 110, 0], EASE_IN_OUT), (30, [C + 115, C - 40, 0], IN), (34, [C + 115, C - 30, 0])]),
                               o=anim([(0, 0), (4, 100), (28, 100), (34, 0)]), s=pop(0, 8)))
    return s


def derretida() -> Sticker:
    s = Sticker("cara-derretida", "Derritiéndose", "Melting face", "emociones", frames=80, order=560,
                tags=["calor", "vergüenza", "derretir", "emoji"])
    line_c = ink(s)
    col = "#FFC93C"
    sid = s.slot("cara", col)
    rnd = circle_pts(150, 16)
    melted = []
    for k, (x, y) in enumerate(rnd):
        if y > 20:
            y = min(150 + (40 if k in (7, 10) else 0), y + 110 + (50 if k in (7, 10) else 0))
            x *= 1.25
        melted.append((x, y))
    sh = morph([(0, rnd), (14, rnd), (40, melted), (60, melted), (76, rnd), (80, rnd)], smooth=1.0)
    puddle = group(oval(360, 60, 0, 150), fill(col, sid))
    eyes = group(oval(34, 46, -55, -50), oval(34, 46, 55, -50), fill("#4A2B0F", line_c))
    smile = group(path([(-60, 10), (0, 40), (60, 10)], smooth=1.0), stroke("#4A2B0F", 14, line_c))
    s.layer(group(sh, fill(col, sid)), ks=layer_transform(p=(C, C)))
    s.layer(eyes, smile, ks=layer_transform(p=anim([(0, [C, C, 0]), (14, [C, C, 0], EASE_IN_OUT), (40, [C, C + 40, 0]), (60, [C, C + 40, 0], EASE_IN_OUT), (76, [C, C, 0])])))
    s.layer(puddle, ks=layer_transform(p=(C, C), s=anim([(0, [0, 100, 100]), (14, [0, 100, 100], EASE_IN_OUT), (40, [100, 100, 100]), (60, [100, 100, 100], EASE_IN_OUT),
                                                         (76, [0, 100, 100])])))
    return s


def angel() -> Sticker:
    s = Sticker("cara-angel", "Angelito", "Angel face", "emociones", frames=60, order=561,
                tags=["ángel", "inocente", "bueno", "emoji"])
    line_c = ink(s)
    halo = s.slot("aureola", "#FFE066")
    s.layer(group(path([(-80, -30), (-55, -45), (-30, -30)], smooth=1.0), path([(30, -30), (55, -45), (80, -30)], smooth=1.0), stroke("#4A2B0F", 14, line_c)),
            group(path([(-60, 50), (0, 85), (60, 50)], smooth=1.0), stroke("#4A2B0F", 16, line_c)), face(s), ks=layer_transform(p=(C, C + 40), s=static([92, 92, 100])))
    s.layer(group(oval(220, 56), stroke("#FFE066", 18, halo)), ks=layer_transform(p=bob(60, C, C - 140, 10)))
    for x, y, d in [(C - 170, C - 110, 0), (C + 170, C - 60, 30)]:
        twinkle(s, x, y, 46, d, 30, halo, "#FFE066", 60)
    return s


def diablillo() -> Sticker:
    s = Sticker("cara-diablillo", "Diablillo", "Devil face", "emociones", frames=40, order=562,
                tags=["travieso", "malvado", "broma", "emoji"])
    line_c = s.slot("trazo", "#2A0E3F")
    sid = s.slot("cara", "#9D4EDD")
    horns = [path([(-110, -90), (-150, -190), (-60, -130)], closed=True, smooth=0.3), path([(110, -90), (150, -190), (60, -130)], closed=True, smooth=0.3)]
    s.layer(group(path([(-90, -60), (-30, -35)]), path([(90, -60), (30, -35)]), stroke("#2A0E3F", 14, line_c)),
            group(oval(30, 30, -55, -14), oval(30, 30, 55, -14), fill("#2A0E3F", line_c)),
            group(path([(-80, 40), (-30, 70), (30, 70), (80, 40), (40, 100), (-40, 100)], closed=True, smooth=0.6), fill("#2A0E3F", line_c)),
            group(circle(300), fill("#9D4EDD", sid)), group(*horns, fill("#9D4EDD", sid)),
            ks=layer_transform(p=(C, C + 30), s=static([90, 90, 100]), r=wave(40, lambda u: 5 * math.sin(2 * math.pi * u))))
    return s


def corazon_roto() -> Sticker:
    s = Sticker("corazon-roto", "Corazón roto", "Broken heart", "emociones", frames=40, order=563, loop=False,
                tags=["desamor", "triste", "ruptura", "corazón"])
    sid = s.slot("color", "#FF2D55")
    k = 1.6
    z = (0, 0)
    crack = [(-18, -10), (14, 20), (-10, 50)]
    # Each half keeps the heart's own curves on the outside and the zigzag crack on the inside.
    right_pts = [((0, -48), z, (10, -25)), ((52, -92), (-28, 0), (28, 0)), ((100, -35), (0, -35), (0, 40)), ((0, 95), (45, -40), z)] + \
                [(p, z, z) for p in reversed(crack)]
    left_pts = [((0, -48), (-10, -25), z)] + [(p, z, z) for p in crack] + \
               [((0, 95), z, (-45, -40)), ((-100, -35), (0, 40), (0, -35)), ((-52, -92), (28, 0), (-28, 0))]

    def shape(pts):
        return {"ty": "sh", "ks": static({"c": True, "v": [[x * k, y * k] for (x, y), _, _ in pts],
                                          "i": [[x * k, y * k] for _, (x, y), _ in pts], "o": [[x * k, y * k] for _, _, (x, y) in pts]})}
    for half, side in ((shape(left_pts), -1), (shape(right_pts), 1)):
        s.layer(group(half, fill("#FF2D55", sid)),
                ks=layer_transform(p=anim([(0, [C, C, 0]), (14, [C, C, 0], EASE_OUT), (24, [C + side * 30, C + 10, 0], EASE_IN_OUT), (40, [C + side * 36, C + 30, 0])]),
                                   r=anim([(0, 0), (14, 0, EASE_OUT), (24, side * 14, EASE_IN_OUT), (40, side * 18)]), s=pop(0, 12)))
    return s


STICKERS = [brillo_y2k, sello_ondulado, garabato_infinito, puntos_onda, morph_estrella, anillos_puntos, margarita_retro, asterisco,
            gota, formas_memphis, burbujas, olas,
            en_vivo, nueva_notificacion, republicar, seguir_persona, reacciones_vivo, avion_papel, camara_foto, microfono,
            chat_corazon, enlace, hashtag, verificado,
            guino, lentes_sol, llorando, enojado, beso, dormido, estrellado, cara_fiesta, nervioso, derretida, angel, diablillo,
            corazon_roto]
