"""Third set, part three (BRIEF.md › «Tanda de 200»): business, callouts, weather and nature, transitions."""

from __future__ import annotations

import math
import random

from designs3 import sparkle4, twinkle
from kit import (FALL, IN, arrow_head, bob, breathe, circle, circle_pts, cyclic, draw_on, line, morph, oval, pop, rrect,
                 scale_keys, swing, wave, wobble)
from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, layer_transform, path,
                    polar, rect, star, static, stroke, transform, trim)

C = 256


def cloud(colour, sid, k=1.0, x=0, y=0):
    """A flat-bottomed cartoon cloud (four puffs and a base)."""
    def p(px, py):
        return (x + px * k, y + py * k)
    return [group(ellipse((150 * k, 130 * k), p=p(-70, 0)), ellipse((170 * k, 160 * k), p=p(20, -30)), ellipse((140 * k, 120 * k), p=p(100, 15)),
                  rect((300 * k, 80 * k), p=p(15, 35), r=40 * k), fill(colour, sid))]


# --- Negocios ----------------------------------------------------------------------------------


def porcentaje() -> Sticker:
    s = Sticker("porcentaje-oferta", "Descuento", "Percent off", "negocios", frames=60, order=671,
                tags=["descuento", "oferta", "rebaja", "promo"])
    badge = s.slot("insignia", "#FF2D55")
    mark = s.slot("signo", "#FFFFFF")
    s.layer(group(star(18, 200, 172), fill("#FF2D55", badge)), ks=layer_transform(p=(C, C), s=pop(0, 14), r=anim([(0, 0, LINEAR), (60, 20)])))
    s.layer(group(circle(64, -52, -52), circle(64, 52, 52), stroke("#FFFFFF", 22, mark)), group(line((60, -80), (-60, 80)), stroke("#FFFFFF", 24, mark)),
            ks=layer_transform(p=(C, C), s=scale_keys([(6, 0, EASE_OUT), (16, 112, EASE_IN_OUT), (22, 100), (40, 100, EASE_IN_OUT), (46, 110, EASE_IN_OUT), (52, 100), (60, 100)]),
                               r=anim([(6, -30, EASE_OUT), (18, 0)])))
    return s


def moneda() -> Sticker:
    s = Sticker("moneda", "Moneda que gira", "Spinning coin", "negocios", frames=48, order=672, thumb=0.04,
                tags=["dinero", "moneda", "pago", "ahorro"])
    gold = s.slot("moneda", "#FFC93C")
    edge = s.slot("borde", "#E09B1A")
    flip = wave(48, lambda u: [max(6.0, 100 * abs(math.cos(math.pi * u))), 100, 100], samples=16)
    s.layer(group(star(5, 52, 22, roundness=8), fill("#E09B1A", edge)), group(circle(200), stroke("#E09B1A", 12, edge)),
            group(circle(250), fill("#FFC93C", gold)), group(circle(262), fill("#E09B1A", edge)), ks=layer_transform(p=bob(48, C, C, 10), s=flip))
    for x, y, d in [(C + 140, C - 130, 0), (C - 150, C + 110, 24)]:
        twinkle(s, x, y, 50, d, 24, s.slot("brillo", "#FFFFFF"), "#FFFFFF", 48)
    return s


def lluvia_dinero() -> Sticker:
    s = Sticker("lluvia-dinero", "Lluvia de billetes", "Money rain", "negocios", frames=90, order=673,
                tags=["dinero", "ganancias", "rico", "pago"])
    bill = s.slot("billete", "#3DBE7A")
    ink = s.slot("detalle", "#E7F8EE")
    rng = random.Random(41)
    for k in range(10):
        x = 50 + k * 46 + rng.uniform(-15, 15)
        start = (k * 37) % 90
        spin = rng.uniform(-200, 200)
        def make(t0, x=x, spin=spin):
            return [group(circle(36), stroke("#E7F8EE", 6, ink)), group(rrect(126, 66, 8), stroke("#E7F8EE", 5, ink)),
                    group(rrect(140, 80, 10), fill("#3DBE7A", bill))], layer_transform(
                p=anim([(t0, [x, -60, 0], EASE_IN_OUT), (t0 + 30, [x + 40, 200, 0], EASE_IN_OUT), (t0 + 60, [x - 30, 400, 0], EASE_IN_OUT), (t0 + 80, [x, 590, 0])]),
                r=anim([(t0, 0, EASE_IN_OUT), (t0 + 80, spin)]))
        cyclic(s, 90, start, 80, make)
    return s


def grafico_barras() -> Sticker:
    s = Sticker("grafico-barras", "Gráfico de barras", "Bar chart", "negocios", frames=40, order=674, loop=False,
                tags=["crecimiento", "ventas", "resultados", "estadística"])
    bars = s.slot("barras", "#5BC0FF")
    top = s.slot("destacada", "#22C55E")
    axis = s.slot("eje", "#FFFFFF")
    s.layer(group(line((-190, 150), (200, 150)), stroke("#FFFFFF", 10, axis)), ks=layer_transform(p=(C, C), s=scale_keys([(0, [0, 100, 100], EASE_OUT), (10, 100)])))
    for k, h in enumerate((110, 170, 140, 270)):
        col, sid = ("#22C55E", top) if k == 3 else ("#5BC0FF", bars)
        d = 6 + k * 5
        s.layer(group(rrect(70, h, 12, 0, -h / 2), fill(col, sid)),
                ks=layer_transform(p=(C - 135 + k * 90, C + 140), s=scale_keys([(d, [100, 0, 100], EASE_OUT), (d + 10, [100, 110, 100], EASE_IN_OUT), (d + 16, [100, 100, 100])])))
    return s


def grafico_linea() -> Sticker:
    s = Sticker("grafico-linea", "Tendencia al alza", "Trending up", "negocios", frames=40, order=675, loop=False,
                tags=["crecimiento", "éxito", "subida", "estadística"])
    sid = s.slot("color", "#22C55E")
    pts = [(-190, 120), (-90, 30), (-10, 70), (90, -40), (190, -130)]
    s.layer(group(path(pts), stroke("#22C55E", 22, sid), draw_on(0, 22, EASE_IN_OUT)), ks=layer_transform(p=(C, C)))
    for k, (x, y) in enumerate(pts[:-1]):
        s.layer(group(circle(44), fill("#22C55E", sid)), ks=layer_transform(p=(C + x, C + y), s=pop(k * 5 + 2, 10)))
    s.layer(group(arrow_head((200, -140), (150, -96), 70, 40), stroke("#22C55E", 22, sid)), ks=layer_transform(p=(C + 200, C - 140), a=(200, -140), s=pop(20, 12)))
    return s


def grafico_torta() -> Sticker:
    s = Sticker("grafico-torta", "Gráfico circular", "Pie chart", "negocios", frames=40, order=676, loop=False,
                tags=["estadística", "porcentaje", "datos", "presentación"])
    cols = [("c1", "#FF4D6D", 0, 45), ("c2", "#FFD23F", 45, 75), ("c3", "#3BCEAC", 75, 100)]
    for k, (sid, col, a, b) in enumerate(cols):
        s.slot(sid, col)
        d = 4 + k * 8
        s.layer(group(circle(190), stroke(col, 190, sid, cap=1), trim(anim([(d, a, EASE_OUT), (d + 12, b)]), start=static(a))),
                ks=layer_transform(p=(C, C), s=scale_keys([(0, 90, EASE_OUT), (12, 100)]) if k == 0 else static([100, 100, 100])))
    return s


def tarjeta_pago() -> Sticker:
    s = Sticker("tarjeta-pago", "Tarjeta de pago", "Payment card", "negocios", frames=60, order=677,
                tags=["pago", "tarjeta", "compra", "tienda"])
    card = s.slot("tarjeta", "#7B2FF7")
    chip = s.slot("chip", "#FFC93C")
    lines = s.slot("detalle", "#FFFFFF")
    front = [group(rrect(60, 46, 8, -100, -20), fill("#FFC93C", chip)),
             group(line((-120, 50), (-40, 50)), line((-20, 50), (60, 50)), stroke("#FFFFFF", 12, lines, o=80)),
             group(circle(44, 110, -60), circle(44, 84, -60), fill("#FFFFFF", lines, o=40)),
             group(rrect(320, 200, 22), fill("#7B2FF7", card))]
    s.layer(*front, ks=layer_transform(p=bob(60, C, C, 12), r=wobble(60, 6),
                                       s=scale_keys([(0, 100, EASE_IN_OUT), (24, 100, EASE_IN_OUT), (30, [100, 92, 100], EASE_IN_OUT), (36, 100), (60, 100)])))
    twinkle(s, C + 150, C - 110, 60, 28, 22, s.slot("brillo", "#FFFFFF"), "#FFFFFF", 60)
    return s


def megafono() -> Sticker:
    s = Sticker("megafono", "Megáfono", "Megaphone", "negocios", frames=36, order=678,
                tags=["anuncio", "noticia", "atención", "promo"])
    body = s.slot("megafono", "#FF4D6D")
    waves = s.slot("ondas", "#FFFFFF")
    horn = path([(-110, -30), (60, -110), (60, 110), (-110, 30)], closed=True)
    s.layer(group(rrect(46, 230, 23, 70, 0), fill("#FFFFFF", waves)), group(horn, fill("#FF4D6D", body), stroke("#FF4D6D", 20, body)),
            group(rrect(60, 70, 14, -130, 0), fill("#FF4D6D", body)), group(rrect(30, 80, 10, -90, 70), fill("#C81E4E")),
            ks=layer_transform(p=(C - 60, C), r=-12, s=scale_keys([(0, 100, EASE_IN_OUT), (4, 94, EASE_OUT), (10, 100), (36, 100)])))
    for k in range(3):
        arcp = path([polar(0, 0, 70 + k * 50, a) for a in range(-35, 36, 10)], smooth=1.0)
        d = 2 + k * 4
        s.layer(group(arcp, stroke("#FFFFFF", 14, waves)), ks=layer_transform(p=(C + 40, C - 22), r=-12,
                                                                             o=anim([(0, 0), (d, 0, EASE_OUT), (d + 6, 100, EASE_IN_OUT), (d + 18, 0), (36, 0)])))
    return s


def tienda() -> Sticker:
    s = Sticker("tienda", "Tienda", "Shop", "negocios", frames=60, order=679,
                tags=["tienda", "negocio", "abierto", "local"])
    a = s.slot("toldo", "#FF4D6D")
    b = s.slot("rayas", "#FFFFFF")
    wall = s.slot("fachada", "#FFE8C2")
    door = s.slot("puerta", "#7B4A2B")
    s.layer(group(rrect(90, 150, 8, -60, 75), fill("#7B4A2B", door)), group(rrect(110, 90, 8, 70, 40), fill("#9AD7FF")),
            group(rect((320, 220), p=(0, 40)), fill("#FFE8C2", wall)), ks=layer_transform(p=(C, C + 70), s=pop(0, 14)))
    def band(k):
        x0 = -180 + k * 60
        return path([(x0, -60), (x0 + 60, -60), (x0 + 60, 30), (x0, 30)], closed=True)
    def scallop(k):
        return circle(60, -150 + k * 60, 30)
    s.layer(group(*[band(k) for k in range(6) if k % 2], *[scallop(k) for k in range(6) if k % 2], fill("#FFFFFF", b)),
            group(*[band(k) for k in range(6) if k % 2 == 0], *[scallop(k) for k in range(6) if k % 2 == 0], fill("#FF4D6D", a)),
            ks=layer_transform(p=(C, C - 90), a=(0, -60), s=scale_keys([(8, [100, 0, 100], EASE_OUT), (18, [100, 115, 100], EASE_IN_OUT), (24, [100, 100, 100])])))
    s.layer(group(line((-30, 0), (0, -40), (30, 0)), stroke("#FFFFFF", 5)), group(rrect(120, 54, 10, 0, 27), fill("#FFFFFF", b)),
            ks=layer_transform(p=(C - 60, C + 40), a=(0, -40), r=swing(36, 14, 3, start=20), s=pop(16, 10)))
    return s


def alcancia() -> Sticker:
    s = Sticker("alcancia", "Alcancía", "Piggy bank", "negocios", frames=48, order=680,
                tags=["ahorro", "dinero", "finanzas", "meta"])
    pig = s.slot("cerdito", "#FF8FB1")
    coin = s.slot("moneda", "#FFC93C")
    s.layer(group(rrect(60, 12, 6, -10, -88), fill("#B3476A")), group(circle(24, 80, -30), oval(12, 20, 132, 0), oval(12, 20, 150, 0), fill("#5A1E33")),
            group(oval(70, 60, 140, 0), fill("#FF8FB1", pig)), group(path([(-60, -70), (-30, -130), (0, -78)], closed=True), fill("#FF8FB1", pig)),
            group(rrect(34, 50, 10, -80, 85), rrect(34, 50, 10, 60, 85), fill("#FF8FB1", pig)), group(oval(300, 210), fill("#FF8FB1", pig)),
            ks=layer_transform(p=(C - 10, C + 50), s=scale_keys([(0, 100), (22, 100, EASE_OUT), (26, [104, 94, 100], EASE_IN_OUT), (32, 100), (48, 100)])))
    s.layer(group(circle(46), stroke("#E09B1A", 6)), group(circle(70), fill("#FFC93C", coin)),
            ks=layer_transform(p=anim([(0, [C - 20, 20, 0], FALL), (22, [C - 20, C - 38, 0])]), s=scale_keys([(0, 100), (20, 100, EASE_IN_OUT), (22, [100, 30, 100])]),
                               o=anim([(0, 0), (4, 100)])), op=23)
    return s


def cohete() -> Sticker:
    s = Sticker("cohete", "Cohete", "Rocket", "negocios", frames=30, order=681,
                tags=["lanzamiento", "despegue", "startup", "rápido"])
    body = s.slot("cohete", "#FFFFFF")
    accent = s.slot("aletas", "#FF4D6D")
    fire = s.slot("fuego", "#FFC93C")
    window = s.slot("ventana", "#5BC0FF")
    shake = wave(30, lambda u: [C + 3 * math.sin(2 * math.pi * 5 * u), C - 30 + 4 * math.sin(2 * math.pi * 2 * u), 0], samples=30)
    flame = morph([(0, [(0, 60), (30, 90), (0, 190), (-30, 90)]), (5, [(0, 60), (34, 95), (0, 160), (-34, 95)]), (10, [(0, 60), (30, 90), (0, 200), (-30, 90)]),
                   (15, [(0, 60), (34, 95), (0, 165), (-34, 95)]), (20, [(0, 60), (30, 90), (0, 195), (-30, 90)]), (25, [(0, 60), (34, 95), (0, 162), (-34, 95)]),
                   (30, [(0, 60), (30, 90), (0, 190), (-30, 90)])], smooth=1.0)
    s.layer(group(circle(50, 0, -40), fill("#5BC0FF", window)), group(circle(70, 0, -40), fill("#2B2D42")),
            group(path([(0, -170), (60, -80), (60, 70), (-60, 70), (-60, -80)], closed=True, smooth=0.5), fill("#FFFFFF", body)),
            group(path([(-60, 0), (-110, 80), (-60, 70)], closed=True), path([(60, 0), (110, 80), (60, 70)], closed=True), rrect(70, 26, 8, 0, 80), fill("#FF4D6D", accent)),
            group(flame, fill("#FFC93C", fire)), ks=layer_transform(p=shake, r=20))
    rng = random.Random(6)
    for k in range(6):
        x = rng.uniform(100, 420)
        def make(t0, x=x):
            return [group(line((0, 0), (0, 80)), stroke("#FFFFFF", 8, body, o=60))], layer_transform(
                p=anim([(t0, [x, -100, 0], LINEAR), (t0 + 12, [x - 140, 600, 0])]), r=20)
        cyclic(s, 30, k * 5, 12, make)
    return s


def bombilla() -> Sticker:
    s = Sticker("bombilla-idea", "¡Idea!", "Light bulb idea", "negocios", frames=48, order=682,
                tags=["idea", "creatividad", "consejo", "tip"])
    bulb = s.slot("bombilla", "#FFD23F")
    base = s.slot("base", "#9CA3AF")
    rays = s.slot("rayos", "#FFD23F")
    s.layer(group(circle(330), fill("#FFD23F", bulb, o=14)), ks=layer_transform(p=(C, C - 30), s=breathe(48, 90, 110)))
    s.layer(group(path([(-30, 40), (-14, 0), (0, 30), (14, 0), (30, 40)]), stroke("#E09B1A", 9)),
            group(path([(-60, 50), (-100, -10), (-100, -80), (-60, -130), (0, -150), (60, -130), (100, -80), (100, -10), (60, 50)], closed=True, smooth=0.8),
                  fill("#FFD23F", bulb)),
            group(rrect(110, 26, 10, 0, 76), rrect(96, 26, 10, 0, 104), rrect(60, 20, 10, 0, 128), fill("#9CA3AF", base)), ks=layer_transform(p=(C, C)))
    for k in range(7):
        a = -180 + k * 30
        x1, y1 = polar(0, -30, 150, a)
        x2, y2 = polar(0, -30, 200, a)
        s.layer(group(line((x1, y1), (x2, y2)), stroke("#FFD23F", 16, rays),
                      trim(anim([(0, 0, EASE_OUT), (10, 100), (30, 100)]), start=anim([(16, 0, EASE_IN_OUT), (30, 100)]))), ks=layer_transform(p=(C, C)), op=31)
    return s


def diana() -> Sticker:
    s = Sticker("diana", "Diana", "Bullseye", "negocios", frames=40, order=683, loop=False,
                tags=["objetivo", "meta", "acierto", "estrategia"])
    red = s.slot("rojo", "#EF4444")
    white = s.slot("blanco", "#FFFFFF")
    dart = s.slot("dardo", "#3B82F6")
    rings = [group(circle(d), fill(col, sid)) for d, col, sid in [(60, "#EF4444", red), (130, "#FFFFFF", white), (200, "#EF4444", red), (270, "#FFFFFF", white),
                                                                   (340, "#EF4444", red)]]
    s.layer(*rings, ks=layer_transform(p=(C - 20, C + 20), s=pop(0, 12), r=anim([(14, 0), (16, 0, EASE_OUT), (18, -3, EASE_IN_OUT), (22, 2, EASE_IN_OUT), (26, 0)])))
    s.layer(group(path([(150, -20), (190, -50), (180, 0)], closed=True), path([(150, 20), (190, 50), (180, 0)], closed=True), fill("#3B82F6", dart)),
            group(line((0, 0), (170, 0)), stroke("#2B2D42", 14)), group(path([(0, 0), (30, -10), (30, 10)], closed=True), fill("#9CA3AF")),
            ks=layer_transform(p=anim([(4, [C + 340, C - 300, 0], EASE_IN_OUT), (16, [C - 20, C + 20, 0], EASE_OUT)]), r=anim([(16, -40, EASE_IN_OUT), (19, -34, EASE_IN_OUT),
                                                                                                                         (22, -42, EASE_IN_OUT), (26, -40)])),
            ip=4)
    return s


# --- Llamadas y marcos -------------------------------------------------------------------------


def nota_adhesiva() -> Sticker:
    s = Sticker("nota-adhesiva", "Nota adhesiva", "Sticky note", "llamadas", frames=30, order=751, loop=False,
                tags=["nota", "recordatorio", "apunte", "tarea"])
    note = s.slot("nota", "#FFE066")
    fold = s.slot("doblez", "#E8C23C")
    s.layer(group(path([(160, 100), (100, 160), (100, 100)], closed=True), fill("#E8C23C", fold)),
            group(path([(-160, -160), (160, -160), (160, 100), (100, 160), (-160, 160)], closed=True), fill("#FFE066", note)),
            group(path([(-150, -150), (170, -150), (170, 110), (110, 172), (-150, 172)], closed=True), fill("#000000", o=25)),
            ks=layer_transform(p=anim([(0, [C + 60, C - 60, 0], EASE_OUT), (10, [C, C, 0])]), s=scale_keys([(0, 140, EASE_OUT), (10, 96, EASE_IN_OUT), (15, 102, EASE_IN_OUT), (20, 100)]),
                               r=anim([(0, -16, EASE_OUT), (10, -5, EASE_IN_OUT), (15, -3)]), o=anim([(0, 0), (4, 100)])))
    return s


def cinta_adhesiva() -> Sticker:
    s = Sticker("cinta-adhesiva", "Cinta adhesiva", "Washi tape", "llamadas", frames=24, order=752, loop=False,
                tags=["marco", "foto", "scrapbook", "collage"])
    sid = s.slot("cinta", "#FF8FB1")
    dots = s.slot("lunares", "#FFFFFF")
    def tape(cx, cy, r, d):
        pts = [(-110, -30)] + [(-90 + k * 36, -34 + (4 if k % 2 else -2)) for k in range(6)] + [(110, -30), (114, 30)] + \
              [(90 - k * 36, 34 + (-4 if k % 2 else 2)) for k in range(6)] + [(-114, 30)]
        s.layer(group(*[circle(12, -80 + k * 40, 0) for k in range(5)], fill("#FFFFFF", dots, o=70)), group(path(pts, closed=True), fill("#FF8FB1", sid, o=88)),
                ks=layer_transform(p=(cx, cy), r=r, s=scale_keys([(d, [0, 100, 100], EASE_OUT), (d + 8, [100, 100, 100])])))
    tape(150, 130, -35, 0)
    tape(362, 382, -35, 6)
    return s


def bocadillo_grito() -> Sticker:
    s = Sticker("bocadillo-grito", "Bocadillo de grito", "Shout bubble", "llamadas", frames=36, order=753,
                tags=["grito", "wow", "cómic", "exclamación"])
    main = s.slot("relleno", "#FFFFFF")
    edge = s.slot("borde", "#111111")
    rng = random.Random(4)
    pts = [polar(0, 0, (200 if k % 2 == 0 else 150) * (1 + rng.uniform(-0.06, 0.06)), k * 360 / 26) for k in range(26)]
    pts = [(x, y * 0.72) for x, y in pts]
    s.layer(group(path(pts, closed=True), stroke("#111111", 12, edge)), group(path(pts, closed=True), fill("#FFFFFF", main)),
            ks=layer_transform(p=(C, C), s=scale_keys([(0, 0, EASE_OUT), (8, 112, EASE_IN_OUT), (12, 96, EASE_IN_OUT), (16, 100), (36, 100)]),
                               r=wave(36, lambda u: 3 * math.sin(2 * math.pi * 6 * u), samples=36)))
    return s


def conversacion() -> Sticker:
    s = Sticker("conversacion", "Conversación", "Chat", "llamadas", frames=72, order=754,
                tags=["chat", "diálogo", "mensajes", "conversación"])
    a = s.slot("burbuja1", "#FFFFFF")
    b = s.slot("burbuja2", "#3B82F6")
    lines_a = s.slot("lineas", "#C7CBD4")
    def bubble(x, y, w, col, sid, side, lines_col, lsid, t_in):
        tail = path([(side * (w / 2 - 30), 40), (side * (w / 2 + 6), 62), (side * (w / 2 - 70), 40)], closed=True)
        bars = [line((-w / 2 + 34, -12), (w / 2 - 50, -12)), line((-w / 2 + 34, 16), (w / 2 - 110, 16))]
        s.layer(group(*bars, stroke(lines_col, 14, lsid)), group(tail, fill(col, sid)), group(rrect(w, 100, 40), fill(col, sid)),
                ks=layer_transform(p=(x, y), a=(side * w / 2, 50), s=scale_keys([(0, 0), (t_in, 0, EASE_OUT), (t_in + 8, 108, EASE_IN_OUT), (t_in + 13, 100), (62, 100, IN), (68, 0), (72, 0)])))
    bubble(C - 220 + 150, 190 + 50, 300, "#FFFFFF", a, -1, "#C7CBD4", lines_a, 2)
    bubble(C + 220 - 140, 330 + 50, 280, "#3B82F6", b, 1, "#FFFFFF", None, 22)
    return s


def tarjeta_aviso() -> Sticker:
    s = Sticker("tarjeta-aviso", "Tarjeta de aviso", "Notification card", "llamadas", frames=40, order=755, loop=False, size=1024, height=320,
                tags=["aviso", "notificación", "mensaje", "banner"])
    card = s.slot("tarjeta", "#FFFFFF")
    avatar = s.slot("avatar", "#7B2FF7")
    lines = s.slot("lineas", "#C7CBD4")
    s.layer(group(line((-150, -24), (180, -24)), stroke("#2B2D42", 22)), group(line((-150, 26), (280, 26)), stroke("#C7CBD4", 18, lines)),
            group(circle(110, -290, 0), fill("#7B2FF7", avatar)), group(rrect(800, 200, 50), fill("#FFFFFF", card)),
            ks=layer_transform(p=anim([(0, [512, -160, 0], EASE_OUT), (14, [512, 170, 0], EASE_IN_OUT), (20, [512, 155, 0], EASE_IN_OUT), (26, [512, 160, 0])])))
    return s


def marco_circular() -> Sticker:
    s = Sticker("marco-circular", "Marco circular", "Circle frame", "llamadas", frames=90, order=756,
                tags=["perfil", "foto", "marco", "avatar"])
    ring = s.slot("anillo", "#FF4D6D")
    dots = s.slot("puntos", "#FFD23F")
    s.layer(group(circle(340), stroke("#FF4D6D", 18, ring)), ks=layer_transform(p=(C, C), s=breathe(90, 100, 103)))
    orbit = [circle(18 if k % 3 else 28, *polar(0, 0, 210, k * 20)) for k in range(18)]
    s.layer(group(*orbit, fill("#FFD23F", dots)), ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (90, 60)])))
    return s


def bandera() -> Sticker:
    s = Sticker("bandera", "Bandera ondeando", "Waving flag", "llamadas", frames=40, order=757,
                tags=["bandera", "meta", "logro", "inicio"])
    flag = s.slot("bandera", "#FF4D6D")
    pole = s.slot("asta", "#E5E7EB")
    s.layer(group(circle(30, -150, -200), fill("#FFD23F")), group(rrect(16, 420, 8, -150, 20), fill("#E5E7EB", pole)), ks=layer_transform(p=(C, C)))
    def shape(ph):
        top = [(-142 + k * 40, -190 + 18 * math.sin(k * 0.9 + ph) * (k / 7)) for k in range(8)]
        bottom = [(x, y + 170) for x, y in reversed(top)]
        return top + bottom
    sh = morph([(round(j * 40 / 8, 2), shape(-2 * math.pi * j / 8)) for j in range(9)], smooth=0.9, ease=({"x": [0], "y": [0]}, {"x": [1], "y": [1]}))
    s.layer(group(sh, fill("#FF4D6D", flag)), ks=layer_transform(p=(C, C)))
    return s


def pergamino() -> Sticker:
    s = Sticker("pergamino", "Pergamino", "Scroll banner", "llamadas", frames=30, order=758, loop=False, size=1024, height=320,
                tags=["título", "banner", "medieval", "aviso"])
    paper = s.slot("papel", "#F3D9A4")
    roll = s.slot("rollos", "#C9A15B")
    s.layer(group(rect((720, 180)), fill("#F3D9A4", paper)), ks=layer_transform(p=(512, 160), s=scale_keys([(4, [0, 100, 100], EASE_IN_OUT), (22, [100, 100, 100])])))
    for side in (-1, 1):
        s.layer(group(oval(26, 190, 0, 0), fill("#8A6A33")), group(rrect(54, 220, 26), fill("#C9A15B", roll)),
                ks=layer_transform(p=anim([(4, [512 + side * 20, 160, 0], EASE_IN_OUT), (22, [512 + side * 372, 160, 0])]), s=pop(0, 8)))
    return s


def tooltip() -> Sticker:
    s = Sticker("globo-info", "Globo informativo", "Tooltip", "llamadas", frames=40, order=759, loop=False,
                tags=["información", "detalle", "precio", "etiqueta"])
    bub = s.slot("globo", "#111111")
    dot = s.slot("punto", "#FFD23F")
    s.layer(group(circle(26), fill("#FFD23F", dot)), ks=layer_transform(p=(C, C + 150), s=pop(0, 8)))
    s.layer(group(circle(26), stroke("#FFD23F", 6, dot)), ks=layer_transform(p=(C, C + 150), s=scale_keys([(8, 100, EASE_OUT), (30, 320)]), o=anim([(8, 100), (30, 0)])), ip=8, op=31)
    s.layer(group(line((-110, -14), (80, -14)), line((-110, 22), (20, 22)), stroke("#FFFFFF", 14, o=85)),
            group(path([(-24, 60), (24, 60), (0, 86)], closed=True), rrect(300, 130, 30), fill("#111111", bub)),
            ks=layer_transform(p=(C, C + 30), a=(0, 86), s=scale_keys([(6, 0, EASE_OUT), (14, 110, EASE_IN_OUT), (19, 97, EASE_IN_OUT), (24, 100)])))
    return s


# --- Clima y naturaleza ------------------------------------------------------------------------


def tormenta() -> Sticker:
    s = Sticker("tormenta", "Tormenta", "Thunderstorm", "clima", frames=48, order=821,
                tags=["tormenta", "rayo", "lluvia", "clima"])
    cl = s.slot("nube", "#6B7280")
    bolt = s.slot("rayo", "#FFD23F")
    drop = s.slot("gotas", "#5BC0FF")
    for k in range(4):
        x = C - 90 + k * 60
        def make(t0, x=x):
            return [group(line((0, 0), (-8, 28)), stroke("#5BC0FF", 9, drop))], layer_transform(
                p=anim([(t0, [x, 280, 0], LINEAR), (t0 + 16, [x - 18, 450, 0])]), o=anim([(t0, 100), (t0 + 12, 100), (t0 + 16, 0)]))
        cyclic(s, 48, k * 12 + 3, 16, make)
    s.layer(group(path([(10, -10), (-40, 70), (0, 70), (-30, 150), (50, 40), (10, 40), (40, -10)], closed=True), fill("#FFD23F", bolt)),
            ks=layer_transform(p=(C + 10, 290), o=anim([(0, 0), (20, 0), (21, 100), (25, 100), (26, 0), (28, 0), (29, 100), (34, 100, EASE_IN_OUT), (40, 0), (48, 0)], LINEAR)))
    s.layer(*cloud("#6B7280", cl, 1.15), ks=layer_transform(p=(C - 10, 200), s=scale_keys([(0, 100), (20, 100, EASE_OUT), (23, 104, EASE_IN_OUT), (30, 100)])))
    return s


def sol_nube() -> Sticker:
    s = Sticker("sol-nube", "Sol entre nubes", "Sun and cloud", "clima", frames=90, order=822,
                tags=["sol", "nublado", "clima", "buen día"])
    sun = s.slot("sol", "#FFC93C")
    cl = s.slot("nube", "#FFFFFF")
    rays = [line(polar(0, 0, 100, k * 30), polar(0, 0, 140, k * 30)) for k in range(12)]
    s.layer(group(*rays, stroke("#FFC93C", 16, sun), tr=transform(r=anim([(0, 0, LINEAR), (90, 30)]))), group(circle(160), fill("#FFC93C", sun)),
            ks=layer_transform(p=wave(90, lambda u: [C + 60, C - 50 - 20 * (0.5 - 0.5 * math.cos(2 * math.pi * u)), 0])))
    s.layer(*cloud("#FFFFFF", cl, 1.0), ks=layer_transform(p=wave(90, lambda u: [C - 40 + 20 * math.sin(2 * math.pi * u), C + 60, 0])))
    return s


def arcoiris() -> Sticker:
    s = Sticker("arcoiris", "Arcoíris", "Rainbow", "clima", frames=40, order=823, loop=False,
                tags=["arcoíris", "lluvia", "esperanza", "colores"])
    cols = [("c1", "#FF4D6D"), ("c2", "#FF9F1C"), ("c3", "#FFD23F"), ("c4", "#3BCEAC"), ("c5", "#5BC0FF")]
    cl = s.slot("nubes", "#FFFFFF")
    for k, (sid, col) in enumerate(cols):
        s.slot(sid, col)
        r = 190 - k * 26
        pts = [polar(0, 0, r, 180 + j * 15) for j in range(13)]
        s.layer(group(path(pts, smooth=1.0), stroke(col, 26, sid, cap=1), draw_on(k * 3, 18, EASE_OUT)), ks=layer_transform(p=(C, C + 70)))
    for side, d in ((-1, 0), (1, 18)):
        s.layer(*cloud("#FFFFFF", cl, 0.5), ks=layer_transform(p=(C + side * 140 - 8, C + 70), s=pop(d, 12)))
    return s


def copo_nieve() -> Sticker:
    s = Sticker("copo-nieve", "Copo de nieve", "Snowflake", "clima", frames=120, order=824,
                tags=["nieve", "invierno", "frío", "navidad"])
    sid = s.slot("color", "#BFE6FF")
    arms = []
    for k in range(6):
        a = k * 60 - 90
        arms.append(line((0, 0), polar(0, 0, 190, a)))
        for r, l in ((90, 50), (140, 36)):
            base = polar(0, 0, r, a)
            arms.append(line(base, polar(base[0], base[1], l, a - 45)))
            arms.append(line(base, polar(base[0], base[1], l, a + 45)))
    s.layer(group(*arms, stroke("#BFE6FF", 18, sid)), group(circle(56), fill("#BFE6FF", sid)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (120, 60)]), s=breathe(120, 96, 104)))
    for x, y, d in [(C + 170, C - 160, 0), (C - 180, C + 150, 60), (C - 170, C - 150, 30)]:
        twinkle(s, x, y, 46, d, 30, s.slot("brillo", "#FFFFFF"), "#FFFFFF", 120)
    return s


def viento() -> Sticker:
    s = Sticker("viento", "Viento", "Wind", "clima", frames=48, order=825,
                tags=["viento", "brisa", "aire", "frío"])
    sid = s.slot("color", "#FFFFFF")
    for k, (y, length, d) in enumerate([(-90, 300, 0), (0, 380, 10), (90, 260, 22)]):
        pts = [(-200 + j * length / 8, y + 6 * math.sin(j)) for j in range(9)]
        curl = [polar(pts[-1][0], y - 36, 36, a) for a in range(90, -181, -45)]
        s.layer(group(path(pts + curl, smooth=1.0), stroke("#FFFFFF", 16, sid),
                      trim(anim([(d, 0, EASE_IN_OUT), (d + 20, 100)]), start=anim([(d + 10, 0, EASE_IN_OUT), (d + 26, 100)]))),
                ks=layer_transform(p=(C - 20, C)), ip=d, op=d + 27)
    return s


def luna_estrellas() -> Sticker:
    s = Sticker("luna-estrellas", "Luna y estrellas", "Moon and stars", "clima", frames=90, order=826,
                tags=["noche", "dormir", "luna", "buenas noches"])
    moon = s.slot("luna", "#FFE066")
    stars_c = s.slot("estrellas", "#FFFFFF")
    R = 150
    outer = [polar(0, 0, R, a) for a in range(60, 301, 15)]
    # Inner arc: a circle through both horns, bulging left, walked from the top horn back to the bottom one.
    (x1, y1), (x2, y2) = outer[0], outer[-1]
    cx = R * 0.5
    r2 = math.hypot(x1 - cx, y1)
    start = math.degrees(math.atan2(y2, x2 - cx))
    end = math.degrees(math.atan2(y1, x1 - cx)) - 360
    steps = 12
    inner = [polar(cx, 0, r2, start + (end - start) * j / steps) for j in range(1, steps)]
    s.layer(group(path(outer + inner, closed=True, smooth=0.9), fill("#FFE066", moon)), ks=layer_transform(p=(C - 30, C + 10), r=wobble(90, 6)))
    for x, y, sz, d in [(C + 120, C - 120, 70, 0), (C + 170, C + 40, 44, 30), (C - 150, C - 160, 40, 55), (C + 60, C + 160, 34, 70)]:
        s.layer(group(star(5, sz / 2, sz / 4.5, roundness=8), fill("#FFFFFF", stars_c)),
                ks=layer_transform(p=(x, y), s=scale_keys([(0, 100, EASE_IN_OUT), (d, 100, EASE_IN_OUT), (d + 10, 55, EASE_IN_OUT), (d + 20, 100), (90, 100)]) if d + 20 <= 90 else static([100, 100, 100])))
    return s


def paraguas() -> Sticker:
    s = Sticker("paraguas", "Paraguas", "Umbrella", "clima", frames=48, order=827,
                tags=["lluvia", "otoño", "protección", "clima"])
    top = s.slot("paraguas", "#FF4D6D")
    drop = s.slot("gotas", "#5BC0FF")
    canopy = [polar(0, 0, 180, a) for a in range(180, 361, 15)]
    ribs = [path([(0, -180), (x, 0)]) for x in (-60, 60)]
    bumps = [ellipse((120, 40), p=(x, 0)) for x in (-120, 0, 120)]
    s.layer(group(*ribs, stroke("#000000", 8, o=18)),
            group(path([(0, 0), (0, 170), (-10, 200), (-40, 205), (-55, 185)], smooth=0.6), stroke("#E5E7EB", 14)),
            group(path(canopy, closed=True, smooth=1.0), *bumps, fill("#FF4D6D", top)),
            ks=layer_transform(p=(C, C + 10), r=wobble(48, 5)))
    for k in range(6):
        x = C - 200 + k * 80
        def make(t0, x=x, k=k):
            land = 170 if abs(x - C) < 170 else 520
            return [group(line((0, 0), (-4, 24)), stroke("#5BC0FF", 9, drop))], layer_transform(
                p=anim([(t0, [x, -30, 0], LINEAR), (t0 + 14, [x - 6, land if land < 500 else 540, 0])]), o=anim([(t0, 100), (t0 + 12, 100), (t0 + 14, 0)]))
        if abs(x - C) >= 170:
            cyclic(s, 48, k * 8, 14, make)
    for side in (-1, 1):
        def make(t0, side=side):
            return [group(circle(14), fill("#5BC0FF", drop))], layer_transform(
                p=anim([(t0, [C + side * 120, C - 120, 0], EASE_OUT), (t0 + 16, [C + side * 220, C + 30, 0])]), o=anim([(t0, 100), (t0 + 16, 0)]))
        cyclic(s, 48, 10 if side < 0 else 34, 16, make)
    return s


def termometro() -> Sticker:
    s = Sticker("termometro-calor", "Mucho calor", "Heat", "clima", frames=60, order=828,
                tags=["calor", "verano", "temperatura", "sol"])
    glass = s.slot("tubo", "#FFFFFF")
    red = s.slot("mercurio", "#EF4444")
    heat = s.slot("ondas", "#FFB020")
    s.layer(group(circle(90, 0, 120)), group(circle(80, 0, 120), fill("#EF4444", red)), group(circle(120, 0, 120), rrect(70, 300, 35, 0, -20), fill("#FFFFFF", glass)),
            ks=layer_transform(p=(C - 40, C)))
    s.layer(group(rrect(34, 250, 17, 0, -125), fill("#EF4444", red)),
            ks=layer_transform(p=(C - 40, C + 110), s=scale_keys([(0, [100, 25, 100], EASE_IN_OUT), (30, [100, 100, 100], EASE_IN_OUT), (60, [100, 25, 100])])))
    for k in range(3):
        pts = [(0, 0), (14, -30), (0, -60), (-14, -90), (0, -120)]
        def make(t0, k=k):
            return [group(path(pts, smooth=1.0), stroke("#FFB020", 12, heat))], layer_transform(
                p=anim([(t0, [C + 80 + k * 50, C + 100, 0], EASE_OUT), (t0 + 30, [C + 80 + k * 50, C - 20, 0])]), o=anim([(t0, 0), (t0 + 8, 100), (t0 + 22, 100), (t0 + 30, 0)]))
        cyclic(s, 60, k * 20, 30, make)
    return s


def flor_crece() -> Sticker:
    s = Sticker("flor-crece", "Flor que crece", "Growing flower", "clima", frames=50, order=829, loop=False,
                tags=["primavera", "naturaleza", "flor", "crecer"])
    stem = s.slot("tallo", "#3DBE7A")
    pet = s.slot("petalos", "#FF8FB1")
    mid = s.slot("centro", "#FFD23F")
    s.layer(group(path([(0, 200), (10, 100), (-10, 0), (0, -80)], smooth=1.0), stroke("#3DBE7A", 16, stem), draw_on(0, 18, EASE_OUT)), ks=layer_transform(p=(C, C + 30)))
    for side, y, d in ((-1, 110, 12), (1, 50, 16)):
        leaf = path([(0, 0), (side * 50, -30), (side * 100, 0), (side * 50, 22)], closed=True, smooth=0.9)
        s.layer(group(leaf, fill("#3DBE7A", stem)), ks=layer_transform(p=(C + 4, C + 30 + y), s=pop(d, 12)))
    petals = [group(oval(70, 110, 0, -60), fill("#FF8FB1", pet), tr=transform(r=k * 60)) for k in range(6)]
    s.layer(group(circle(70), fill("#FFD23F", mid)), *petals, ks=layer_transform(p=(C, C - 50), s=pop(20, 16), r=anim([(20, -60, EASE_OUT), (38, 0)])))
    return s


def petalos() -> Sticker:
    s = Sticker("petalos-cerezo", "Pétalos de cerezo", "Cherry blossom petals", "clima", frames=120, order=830, thumb=0.4,
                tags=["primavera", "sakura", "flores", "romántico"])
    sid = s.slot("petalo", "#FFB7D0")
    rng = random.Random(11)
    petal = path([(0, -30), (16, -12), (12, 18), (0, 30), (-12, 18), (-16, -12)], closed=True, smooth=0.9)
    notch = path([(-6, -30), (0, -20), (6, -30)])
    for k in range(10):
        x = rng.uniform(-40, 420)
        start = (k * 12) % 120
        spin = rng.uniform(180, 420) * (1 if k % 2 else -1)
        def make(t0, x=x, spin=spin):
            return [group(petal, fill("#FFB7D0", sid))], layer_transform(
                p=anim([(t0, [x, -40, 0], EASE_IN_OUT), (t0 + 30, [x + 70, 140, 0], EASE_IN_OUT), (t0 + 60, [x + 30, 330, 0], EASE_IN_OUT), (t0 + 90, [x + 120, 560, 0])]),
                r=anim([(t0, 0, EASE_IN_OUT), (t0 + 90, spin)]), s=140)
        cyclic(s, 120, start, 90, make)
    return s


# --- Transiciones (pantalla vertical completa) -------------------------------------------------


W, H = 1080, 1920


def burbujas_barrido() -> Sticker:
    s = Sticker("circulos-barrido", "Barrido de círculos", "Circle wipe", "transiciones", frames=30, order=931, size=W, height=H,
                tags=["transición", "círculos", "cambio de escena"], loop=False, thumb=0.4)
    cols = [("c1", "#FF4D6D"), ("c2", "#FFD23F"), ("c3", "#7B2FF7")]
    for sid, col in cols:
        s.slot(sid, col)
    rng = random.Random(2)
    for k in range(14):
        sid, col = cols[k % 3]
        x, y = rng.uniform(0, W), H - k * 130 + rng.uniform(-60, 60)
        d = round(k * 0.7)
        s.layer(group(circle(1000), fill(col, sid)), ks=layer_transform(p=(x, y), s=scale_keys([(d, 0, EASE_OUT), (d + 10, 100), (d + 13, 100, IN), (d + 17, 0)])))
    return s


def franjas() -> Sticker:
    s = Sticker("franjas-diagonales", "Franjas diagonales", "Diagonal stripes", "transiciones", frames=26, order=932, size=W, height=H,
                tags=["transición", "franjas", "cambio de escena"], loop=False, thumb=0.4)
    a = s.slot("c1", "#111111")
    b = s.slot("c2", "#FFD23F")
    for k in range(8):
        sid, col = (a, "#111111") if k % 2 == 0 else (b, "#FFD23F")
        cy = -300 + k * 360
        d = k
        s.layer(group(rect((3000, 380)), fill(col, sid)),
                ks=layer_transform(p=anim([(d, [-1800, cy, 0], EASE_OUT), (d + 9, [540, cy, 0]), (d + 12, [540, cy, 0], IN), (d + 18, [2900, cy, 0])]), r=-30))
    return s


def cuadros_zoom() -> Sticker:
    s = Sticker("cuadros-zoom", "Cuadros", "Square grid", "transiciones", frames=30, order=933, size=W, height=H,
                tags=["transición", "cuadros", "píxeles", "cambio de escena"], loop=False, thumb=0.42)
    sid = s.slot("color", "#3BCEAC")
    n = 180
    for gx in range(6):
        for gy in range(11):
            cx, cy = 90 + gx * n, 60 + gy * n
            d = round(math.hypot(gx - 2.5, gy - 5) * 1.3)
            s.layer(group(rrect(n + 2, n + 2, 0), fill("#3BCEAC", sid)),
                    ks=layer_transform(p=(cx, cy), s=scale_keys([(d, 0, EASE_OUT), (d + 7, 100), (d + 11, 100, IN), (d + 17, 0)]), r=anim([(d, 45, EASE_OUT), (d + 7, 0)])))
    return s


def corte_dividido() -> Sticker:
    s = Sticker("corte-dividido", "Corte dividido", "Split slide", "transiciones", frames=24, order=934, size=W, height=H,
                tags=["transición", "deslizar", "cambio de escena"], loop=False, thumb=0.4)
    a = s.slot("c1", "#FF4D6D")
    b = s.slot("c2", "#111111")
    for side, cy, sid, col in ((-1, 480, a, "#FF4D6D"), (1, 1440, b, "#111111")):
        s.layer(group(rect((W + 40, 980)), fill(col, sid)),
                ks=layer_transform(p=anim([(0, [540 + side * 1200, cy, 0], EASE_IN_OUT), (10, [540, cy, 0]), (13, [540, cy, 0], EASE_IN_OUT), (23, [540 - side * 1200, cy, 0])])))
    return s


def onda_liquida() -> Sticker:
    s = Sticker("onda-liquida", "Onda líquida", "Liquid wave", "transiciones", frames=30, order=935, size=W, height=H,
                tags=["transición", "líquido", "ola", "cambio de escena"], loop=False, thumb=0.45)
    a = s.slot("c1", "#5BC0FF")
    b = s.slot("c2", "#3B82F6")
    def wave_rect(top, ph, amp=70):
        pts = [(x, top + amp * math.sin(x / 1080 * 2 * math.pi * 1.5 + ph)) for x in range(-60, 1141, 120)]
        return pts + [(1140, top + 2400), (-60, top + 2400)]
    for col, sid, d in (("#5BC0FF", a, 0), ("#3B82F6", b, 3)):
        frames = [(d, wave_rect(H + 120, 0)), (d + 12, wave_rect(-200, 3)), (d + 15, wave_rect(-200, 4)), (d + 27, wave_rect(-2700, 7))]
        keys = {"a": 1, "k": []}
        for i, (t, pts) in enumerate(frames):
            bz = path(pts[:-2], smooth=1.0)["ks"]["k"]
            key = {"t": t, "s": [{"c": True, "v": bz["v"] + [list(pts[-2]), list(pts[-1])], "i": bz["i"] + [[0, 0], [0, 0]], "o": bz["o"] + [[0, 0], [0, 0]]}]}
            if i < len(frames) - 1:
                e = EASE_IN_OUT
                key["o"], key["i"] = {"x": e[0]["x"], "y": e[0]["y"]}, {"x": e[1]["x"], "y": e[1]["y"]}
            keys["k"].append(key)
        s.layer(group({"ty": "sh", "ks": keys}, fill(col, sid)), ks=layer_transform(p=(0, 0)))
    return s


def estrella_giro() -> Sticker:
    s = Sticker("estrella-giro", "Estrella giratoria", "Spinning star", "transiciones", frames=26, order=936, size=W, height=H,
                tags=["transición", "estrella", "cambio de escena"], loop=False, thumb=0.45)
    a = s.slot("c1", "#FFD23F")
    b = s.slot("c2", "#FF4D6D")
    for k, (sid, col, d) in enumerate(((b, "#FF4D6D", 0), (a, "#FFD23F", 2))):
        s.layer(group(star(5, 100, 46, roundness=6), fill(col, sid)),
                ks=layer_transform(p=(540, 960), s=scale_keys([(d, 0, EASE_IN_OUT), (d + 11, 2600), (d + 13, 2600, EASE_IN_OUT), (min(26, d + 24), 0)]),
                                   r=anim([(d, -90, EASE_IN_OUT), (min(26, d + 24), 120)])))
    return s


STICKERS = [porcentaje, moneda, lluvia_dinero, grafico_barras, grafico_linea, grafico_torta, tarjeta_pago, megafono, tienda, alcancia,
            cohete, bombilla, diana,
            nota_adhesiva, cinta_adhesiva, bocadillo_grito, conversacion, tarjeta_aviso, marco_circular, bandera, pergamino, tooltip,
            tormenta, sol_nube, arcoiris, copo_nieve, viento, luna_estrellas, paraguas, termometro, flor_crece, petalos,
            burbujas_barrido, franjas, cuadros_zoom, corte_dividido, onda_liquida, estrella_giro]
