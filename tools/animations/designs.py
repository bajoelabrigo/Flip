"""Flip Studio's own animated stickers (Lottie). 512x512, 30 fps; colours as editable slots."""

from __future__ import annotations

import math
import random

from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, heart,
                    layer_transform, path, polar, rect, star, static, stroke, transform, trim)

C = 256  # centre


# --- Celebración -------------------------------------------------------------------------------


def confeti() -> Sticker:
    s = Sticker("confeti", "Lluvia de confeti", "Confetti burst", "celebracion", frames=60, order=10, thumb=0.38,
                tags=["fiesta", "cumpleaños", "celebrar"])
    rng = random.Random(4)
    palette = [("c1", "#FF4D6D"), ("c2", "#FFD23F"), ("c3", "#3BCEAC"), ("c4", "#7B2FF7")]
    for k in range(28):
        sid, colour = palette[k % 4]
        s.slot(sid, colour)
        angle = rng.uniform(-170, -10)
        dist = rng.uniform(140, 230)
        ex, ey = polar(C, C + 40, dist, angle)
        fall = rng.uniform(80, 160)
        shape = rect((rng.uniform(14, 22), rng.uniform(8, 12)), r=2) if k % 3 else ellipse((14, 14))
        s.layer(group(shape, fill(colour, sid)),
                ks=layer_transform(
                    p=anim([(0, [C, C + 40, 0], EASE_OUT), (22, [ex, ey, 0], EASE_IN_OUT), (60, [ex + rng.uniform(-30, 30), ey + fall, 0])]),
                    r=anim([(0, 0, LINEAR), (60, rng.uniform(-540, 540))]),
                    s=anim([(0, [20, 20, 100], EASE_BACK), (10, [100, 100, 100]), (48, [100, 100, 100]), (60, [0, 0, 100])])),
                name=f"pieza {k}")
    return s


def destellos() -> Sticker:
    s = Sticker("destellos", "Destellos", "Sparkles", "celebracion", frames=60, order=20, thumb=0.22,
                tags=["brillo", "estrellas", "magia"])
    sid = s.slot("color", "#FFFFFF")
    spots = [(C, C, 1.0, 0), (C - 120, C - 90, 0.55, 10), (C + 130, C - 60, 0.45, 20), (C + 90, C + 120, 0.6, 28),
             (C - 110, C + 110, 0.4, 36)]
    for x, y, scale, delay in spots:
        sz = 100 * scale
        # Each spark grows and fades in its own window; staggered, the five keep the loop busy.
        s.layer(group(star(4, 90, 18), fill("#FFFFFF", sid)),
                ks=layer_transform(p=(x, y),
                                   s=anim([(delay, [0, 0, 100], EASE_BACK), (delay + 10, [sz, sz, 100], EASE_IN_OUT),
                                           (delay + 22, [0, 0, 100])]),
                                   r=anim([(delay, 0, LINEAR), (delay + 22, 90)])),
                ip=delay, op=delay + 22)
    return s


def corazones() -> Sticker:
    s = Sticker("corazones", "Corazones que suben", "Floating hearts", "celebracion", frames=72, order=30,
                tags=["amor", "corazón", "pareja", "me gusta"])
    sid = s.slot("color", "#FF4D6D")
    rng = random.Random(9)
    for k in range(7):
        x = rng.uniform(110, 400)
        start = k * 9
        size = rng.uniform(55, 100)
        sway = rng.uniform(25, 45) * (1 if k % 2 else -1)
        s.layer(heart("#FF4D6D", sid),
                ks=layer_transform(
                    p=anim([(start, [x, 480, 0], LINEAR), (start + 30, [x + sway, 300, 0], LINEAR), (start + 60, [x - sway / 2, 90, 0])]),
                    s=anim([(start, [0, 0, 100], EASE_BACK), (start + 10, [size, size, 100])]),
                    o=anim([(start, 100), (start + 45, 100), (start + 60, 0)])), ip=start, op=min(72, start + 60))
    return s


def fuegos() -> Sticker:
    s = Sticker("fuegos-artificiales", "Fuegos artificiales", "Fireworks", "celebracion", frames=54, order=40,
                tags=["año nuevo", "fiesta", "celebrar"])
    for b, (cx, cy, colour, delay) in enumerate([(C, 220, "#FFD23F", 0), (150, 330, "#FF4D6D", 14), (370, 320, "#3BCEAC", 24)]):
        sid = s.slot(f"color{b + 1}", colour)
        rays = []
        for k in range(12):
            a = k * 30
            x1, y1 = polar(0, 0, 18, a)
            x2, y2 = polar(0, 0, 95, a)
            rays.append(path([(x1, y1), (x2, y2)]))
        s.layer(group(*rays, stroke(colour, 7, sid),
                      trim(anim([(delay, 0, EASE_OUT), (delay + 14, 100)]), start=anim([(delay + 8, 0, EASE_IN_OUT), (delay + 26, 100)]))),
                ks=layer_transform(p=(cx, cy)), ip=delay, op=min(54, delay + 30))
    return s


def estrellas() -> Sticker:
    s = Sticker("estrellas-pop", "Estrellas pop", "Popping stars", "celebracion", frames=40, order=50,
                tags=["estrella", "logro", "premio"])
    sid = s.slot("color", "#FFD23F")
    for k, (x, y, size, delay) in enumerate([(C, C, 260, 0), (130, 140, 90, 8), (395, 160, 70, 12), (380, 390, 80, 16)]):
        s.layer(group(star(5, 100, 45, roundness=10), fill("#FFD23F", sid)),
                ks=layer_transform(p=(x, y),
                                   s=anim([(delay, [0, 0, 100], EASE_BACK), (delay + 12, [size / 2, size / 2, 100])]),
                                   r=anim([(delay, -60, EASE_OUT), (delay + 14, 0)])))
    return s


# --- Resaltar -----------------------------------------------------------------------------------


def circulo_marcador() -> Sticker:
    s = Sticker("circulo-marcador", "Círculo a mano", "Hand-drawn circle", "resaltar", frames=36, order=100,
                tags=["resaltar", "marcar", "señalar"], loop=False)
    sid = s.slot("color", "#FF3B30")
    pts = [polar(0, 0, 190 + 4 * math.sin(k * 0.9), k * 22 - 100) for k in range(19)]
    s.layer(group(path(pts, smooth=1.0), stroke("#FF3B30", 14, sid), trim(anim([(0, 0, EASE_IN_OUT), (22, 100)]))),
            ks=layer_transform(p=(C, C), s=static([100, 72, 100]), r=static(-8)))
    return s


def subrayado() -> Sticker:
    s = Sticker("subrayado", "Subrayado a mano", "Hand-drawn underline", "resaltar", frames=30, order=110,
                tags=["subrayar", "resaltar", "texto"], loop=False)
    sid = s.slot("color", "#FFD23F")
    pts = [(-200, 14), (-100, 2), (0, 6), (100, -2), (205, -12)]
    s.layer(group(path(pts, smooth=0.9), stroke("#FFD23F", 18, sid), trim(anim([(0, 0, EASE_IN_OUT), (16, 100)]))),
            ks=layer_transform(p=(C, 300)))
    pts2 = [(-120, 44), (0, 36), (130, 30)]
    s.layer(group(path(pts2, smooth=0.9), stroke("#FFD23F", 12, sid), trim(anim([(8, 0, EASE_IN_OUT), (22, 100)]))),
            ks=layer_transform(p=(C, 300)))
    return s


def palomita() -> Sticker:
    s = Sticker("palomita", "Visto bueno", "Check mark", "resaltar", frames=36, order=120,
                tags=["listo", "correcto", "hecho", "check"], loop=False)
    green = s.slot("fondo", "#22C55E")
    white = s.slot("marca", "#FFFFFF")
    s.layer(group(ellipse((300, 300)), fill("#22C55E", green)),
            ks=layer_transform(p=(C, C), s=anim([(0, [0, 0, 100], EASE_BACK), (14, [100, 100, 100])])))
    s.layer(group(path([(-70, 0), (-20, 50), (80, -55)]), stroke("#FFFFFF", 30, white),
                  trim(anim([(10, 0, EASE_OUT), (26, 100)]))), ks=layer_transform(p=(C, C + 8)))
    return s


def tachar() -> Sticker:
    s = Sticker("equis", "Equis", "Cross mark", "resaltar", frames=34, order=130,
                tags=["error", "no", "incorrecto"], loop=False)
    red = s.slot("fondo", "#EF4444")
    white = s.slot("marca", "#FFFFFF")
    s.layer(group(ellipse((300, 300)), fill("#EF4444", red)),
            ks=layer_transform(p=(C, C), s=anim([(0, [0, 0, 100], EASE_BACK), (14, [100, 100, 100])])))
    s.layer(group(path([(-60, -60), (60, 60)]), stroke("#FFFFFF", 30, white), trim(anim([(10, 0, EASE_OUT), (20, 100)]))),
            ks=layer_transform(p=(C, C)))
    s.layer(group(path([(60, -60), (-60, 60)]), stroke("#FFFFFF", 30, white), trim(anim([(16, 0, EASE_OUT), (26, 100)]))),
            ks=layer_transform(p=(C, C)))
    return s


def enfasis() -> Sticker:
    s = Sticker("enfasis", "Rayitas de énfasis", "Emphasis lines", "resaltar", frames=30, order=140, thumb=0.35,
                tags=["sorpresa", "wow", "atención"])
    sid = s.slot("color", "#FFD23F")
    for k, a in enumerate([-150, -120, -90, -60, -30]):
        x1, y1 = polar(C, C + 80, 120, a)
        x2, y2 = polar(C, C + 80, 210, a)
        s.layer(group(path([(x1, y1), (x2, y2)]), stroke("#FFD23F", 16, sid),
                      trim(anim([(0, 0, EASE_OUT), (8, 100), (22, 100, EASE_IN_OUT), (30, 100)]),
                           start=anim([(0, 0), (10, 0, EASE_IN_OUT), (22, 100)]))))
    return s


def marco_esquinas() -> Sticker:
    s = Sticker("marco-esquinas", "Esquinas de enfoque", "Focus corners", "resaltar", frames=40, order=150,
                tags=["marco", "enfoque", "cámara"])
    sid = s.slot("color", "#FFFFFF")
    for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        corner = path([(sx * 200, sy * 120), (sx * 200, sy * 200), (sx * 120, sy * 200)])
        s.layer(group(corner, stroke("#FFFFFF", 14, sid)),
                ks=layer_transform(p=(C, C), s=anim([(0, [130, 130, 100], EASE_OUT), (14, [100, 100, 100], EASE_IN_OUT),
                                                     (27, [92, 92, 100], EASE_IN_OUT), (40, [100, 100, 100])])))
    return s


# --- Flechas -------------------------------------------------------------------------------------


def flecha_abajo() -> Sticker:
    s = Sticker("flecha-abajo", "Flecha que salta", "Bouncing arrow", "flechas", frames=30, order=200,
                tags=["flecha", "abajo", "mira aquí", "enlace"])
    sid = s.slot("color", "#FFFFFF")
    arrow = path([(0, -150), (0, 110)])
    head = path([(-80, 40), (0, 120), (80, 40)])
    s.layer(group(arrow, head, stroke("#FFFFFF", 30, sid)),
            ks=layer_transform(p=anim([(0, [C, 230, 0], EASE_IN_OUT), (15, [C, 290, 0], EASE_IN_OUT), (30, [C, 230, 0])])))
    return s


def flecha_curva() -> Sticker:
    s = Sticker("flecha-curva", "Flecha a mano", "Hand-drawn arrow", "flechas", frames=34, order=210,
                tags=["flecha", "señalar", "mira"], loop=False)
    sid = s.slot("color", "#FFFFFF")
    curve = path([(-190, 150), (-120, -20), (0, -110), (150, -120)], smooth=1.0)
    s.layer(group(curve, stroke("#FFFFFF", 16, sid), trim(anim([(0, 0, EASE_IN_OUT), (20, 100)]))), ks=layer_transform())
    s.layer(group(path([(110, -170), (160, -120), (100, -75)]), stroke("#FFFFFF", 16, sid),
                  trim(anim([(18, 0, EASE_OUT), (28, 100)]))), ks=layer_transform())
    return s


def flechas_derecha() -> Sticker:
    s = Sticker("flechas-derecha", "Flechas en fila", "Chevron row", "flechas", frames=36, order=220,
                tags=["siguiente", "desliza", "derecha"])
    sid = s.slot("color", "#FFD23F")
    for k in range(3):
        x = C - 110 + k * 110
        chevron = path([(-40, -70), (30, 0), (-40, 70)])
        s.layer(group(chevron, stroke("#FFD23F", 28, sid)),
                ks=layer_transform(p=(x, C), o=anim([(k * 6, 20, EASE_IN_OUT), (k * 6 + 10, 100, EASE_IN_OUT), (k * 6 + 22, 20), (36, 20)])))
    return s


def deslizar_arriba() -> Sticker:
    s = Sticker("desliza-arriba", "Desliza hacia arriba", "Swipe up", "flechas", frames=40, order=230,
                tags=["desliza", "arriba", "historias", "enlace"])
    sid = s.slot("color", "#FFFFFF")
    for k in range(2):
        chevron = path([(-90, 40), (0, -45), (90, 40)])
        s.layer(group(chevron, stroke("#FFFFFF", 26, sid)),
                ks=layer_transform(p=anim([(k * 8, [C, 340 - k * 70, 0], EASE_IN_OUT), (k * 8 + 20, [C, 280 - k * 70, 0], EASE_IN_OUT),
                                           (min(40, k * 8 + 34), [C, 340 - k * 70, 0])]),
                                   o=anim([(k * 8, 40), (k * 8 + 20, 100), (min(40, k * 8 + 34), 40)])))
    return s


# --- Formas -------------------------------------------------------------------------------------


def ondas() -> Sticker:
    s = Sticker("ondas", "Ondas", "Pulse rings", "formas", frames=60, order=300,
                tags=["pulso", "radar", "ubicación", "en vivo"])
    sid = s.slot("color", "#3BCEAC")
    s.layer(group(ellipse((90, 90)), fill("#3BCEAC", sid)), ks=layer_transform(p=(C, C)))
    for k in range(3):
        d = k * 20
        s.layer(group(ellipse((90, 90)), stroke("#3BCEAC", 6, sid)),
                ks=layer_transform(p=(C, C), s=anim([(d, [100, 100, 100], LINEAR), (d + 40, [480, 480, 100])]),
                                   o=anim([(d, 100, LINEAR), (d + 40, 0)])), ip=d, op=min(60, d + 40))
        if d + 40 > 60:
            pass
    return s


def cargando() -> Sticker:
    s = Sticker("cargando", "Cargando", "Loading", "formas", frames=45, order=310,
                tags=["espera", "cargando", "pronto"])
    sid = s.slot("color", "#FFFFFF")
    s.layer(group(ellipse((300, 300)), stroke("#FFFFFF", 26, sid),
                  trim(anim([(0, 5, EASE_IN_OUT), (22, 75, EASE_IN_OUT), (45, 5)]), start=static(0),
                       offset=anim([(0, 0, LINEAR), (45, 360)]))),
            ks=layer_transform(p=(C, C)))
    return s


def puntos() -> Sticker:
    s = Sticker("escribiendo", "Escribiendo…", "Typing dots", "formas", frames=36, order=320,
                tags=["chat", "mensaje", "espera"])
    bubble = s.slot("burbuja", "#FFFFFF")
    dot = s.slot("puntos", "#9CA3AF")
    s.layer(group(rect((320, 150), r=75), fill("#FFFFFF", bubble)), ks=layer_transform(p=(C, C)))
    for k in range(3):
        d = k * 6
        s.layer(group(ellipse((44, 44)), fill("#9CA3AF", dot)),
                ks=layer_transform(p=anim([(d, [C - 80 + k * 80, C, 0], EASE_IN_OUT), (d + 8, [C - 80 + k * 80, C - 26, 0], EASE_IN_OUT),
                                           (d + 16, [C - 80 + k * 80, C, 0]), (36, [C - 80 + k * 80, C, 0])])))
    return s


def sol() -> Sticker:
    s = Sticker("sol", "Sol que gira", "Spinning sun", "formas", frames=90, order=330,
                tags=["verano", "sol", "playa"])
    sid = s.slot("color", "#FFC93C")
    rays = [path([polar(0, 0, 120, k * 30), polar(0, 0, 175, k * 30)]) for k in range(12)]
    s.layer(group(*rays, stroke("#FFC93C", 20, sid)), ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (90, 90)])))
    s.layer(group(ellipse((180, 180)), fill("#FFC93C", sid)),
            ks=layer_transform(p=(C, C), s=anim([(0, [100, 100, 100], EASE_IN_OUT), (45, [108, 108, 100], EASE_IN_OUT), (90, [100, 100, 100])])))
    return s


# --- Redes -------------------------------------------------------------------------------------


def corazon_like() -> Sticker:
    s = Sticker("me-gusta", "Me gusta", "Like", "redes", frames=36, order=400,
                tags=["me gusta", "like", "corazón", "redes"], loop=False)
    sid = s.slot("color", "#FF2D55")
    s.layer(heart("#FF2D55", sid, 160),
            ks=layer_transform(p=(C, C + 10), s=anim([(0, [0, 0, 100], EASE_BACK), (12, [190, 190, 100], EASE_IN_OUT), (20, [160, 160, 100])])))
    for k in range(8):
        a = k * 45
        x1, y1 = polar(0, 0, 150, a)
        x2, y2 = polar(0, 0, 200, a)
        s.layer(group(path([(x1, y1), (x2, y2)]), stroke("#FF2D55", 10, sid),
                      trim(anim([(8, 0, EASE_OUT), (16, 100)]), start=anim([(12, 0, EASE_IN_OUT), (24, 100)]))),
                ks=layer_transform(p=(C, C)))
    return s


def campana() -> Sticker:
    s = Sticker("campana", "Campana de notificaciones", "Notification bell", "redes", frames=40, order=410,
                tags=["suscríbete", "notificación", "campana", "youtube"])
    sid = s.slot("color", "#FFD23F")
    bell = path([(-90, 60), (-70, 30), (-70, -40), (-40, -85), (0, -100), (40, -85), (70, -40), (70, 30), (90, 60)],
                closed=True, smooth=0.6)
    s.layer(group(bell, fill("#FFD23F", sid)), group(ellipse((44, 44), p=(0, 82)), fill("#FFD23F", sid)),
            ks=layer_transform(p=(C, 230), a=(0, -100),
                               r=anim([(0, 0, EASE_IN_OUT), (5, 18, EASE_IN_OUT), (10, -16, EASE_IN_OUT), (15, 12, EASE_IN_OUT),
                                       (20, -8, EASE_IN_OUT), (25, 0), (40, 0)])))
    return s


def play() -> Sticker:
    s = Sticker("boton-play", "Botón de reproducir", "Play button", "redes", frames=40, order=420,
                tags=["video", "play", "mira"])
    bg = s.slot("fondo", "#FFFFFF")
    tri = s.slot("triangulo", "#111111")
    # Round and white: a red rounded rectangle would read as one platform's logo.
    s.layer(group(ellipse((300, 300)), fill("#FFFFFF", bg)),
            ks=layer_transform(p=(C, C), s=anim([(0, [100, 100, 100], EASE_IN_OUT), (20, [108, 108, 100], EASE_IN_OUT), (40, [100, 100, 100])])))
    s.layer(group(path([(-40, -60), (70, 0), (-40, 60)], closed=True), fill("#111111", tri)), ks=layer_transform(p=(C + 10, C)))
    return s


import designs2  # noqa: E402

STICKERS_1 = [confeti, destellos, corazones, fuegos, estrellas, circulo_marcador, subrayado, palomita, tachar, enfasis,
            marco_esquinas, flecha_abajo, flecha_curva, flechas_derecha, deslizar_arriba, ondas, cargando, puntos, sol,
            corazon_like, campana, play]
STICKERS = STICKERS_1 + designs2.STICKERS
