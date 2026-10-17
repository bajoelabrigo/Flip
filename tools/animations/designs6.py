"""Third set, part four (BRIEF.md › «Tanda de 200»): special dates from around the world, and food."""

from __future__ import annotations

import math
import random

from designs3 import sparkle4, twinkle
from kit import (FALL, IN, bob, breathe, circle, circle_pts, cyclic, draw_on, heart_path, line, morph, oval, pop, rrect,
                 scale_keys, swing, wave, wobble)
from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, heart, layer_transform,
                    path, polar, rect, star, static, stroke, transform, trim)

C = 256


def steam(s, frames, x, y, sid, colour, count=3, spread=40, height=120, width=10, period=None):
    """Curls of steam rising from (x, y), drawn and erased in turn."""
    period = period or frames
    for k in range(count):
        pts = [(0, 0), (14, -height / 4), (0, -height / 2), (-14, -3 * height / 4), (0, -height)]
        d = round(k * frames / count)
        def make(t0, k=k):
            return [group(path(pts, smooth=1.0), stroke(colour, width, sid, o=85),
                          trim(anim([(t0, 0, EASE_OUT), (t0 + frames * 0.5, 100)]), start=anim([(t0 + frames * 0.3, 0, EASE_IN_OUT), (t0 + frames * 0.8, 100)])))], \
                layer_transform(p=anim([(t0, [x + (k - (count - 1) / 2) * spread, y, 0], EASE_OUT), (t0 + frames * 0.8, [x + (k - (count - 1) / 2) * spread, y - 30, 0])]))
        cyclic(s, frames, d, round(frames * 0.8), make)


# --- Fechas especiales (del mundo entero) ------------------------------------------------------


def arbol_navidad() -> Sticker:
    s = Sticker("arbol-navidad", "Árbol de Navidad", "Christmas tree", "fechas", frames=60, order=1001,
                tags=["navidad", "árbol", "diciembre", "fiestas"])
    tree = s.slot("arbol", "#2E9E5B")
    star_c = s.slot("estrella", "#FFD23F")
    balls = [("c1", "#FF4D6D"), ("c2", "#5BC0FF"), ("c3", "#FFD23F")]
    for sid, col in balls:
        s.slot(sid, col)
    tiers = [path([(-170, 150), (170, 150), (0, 10)], closed=True), path([(-140, 60), (140, 60), (0, -80)], closed=True),
             path([(-105, -30), (105, -30), (0, -160)], closed=True)]
    s.layer(group(rrect(60, 70, 8, 0, 180), fill("#8A5A33")), *[group(t, fill("#2E9E5B", tree), stroke("#2E9E5B", 26, tree)) for t in tiers],
            ks=layer_transform(p=(C, C + 20)))
    spots = [(-90, 120), (40, 110), (110, 130), (-30, 40), (70, 30), (-60, -60), (30, -90), (0, 85), (-120, 140)]
    for k, (x, y) in enumerate(spots):
        sid, col = balls[k % 3]
        d = (k * 7) % 60
        s.layer(group(circle(30), fill(col, sid)),
                ks=layer_transform(p=(C + x, C + 20 + y), s=wave(60, lambda u, d=d: [100 + 25 * max(0.0, math.sin(2 * math.pi * (u - d / 60))) ** 3] * 2 + [100], samples=12)))
    s.layer(group(star(5, 46, 20, roundness=6), fill("#FFD23F", star_c)), ks=layer_transform(p=(C, C - 160), r=wobble(60, 8), s=breathe(60, 100, 115)))
    return s


def gorro_santa() -> Sticker:
    s = Sticker("gorro-santa", "Gorro navideño", "Santa hat", "fechas", frames=48, order=1002,
                tags=["navidad", "gorro", "santa", "diciembre"])
    red = s.slot("gorro", "#E63946")
    white = s.slot("borde", "#FFFFFF")
    s.layer(group(rrect(330, 70, 35, 0, 120), fill("#FFFFFF", white)),
            group(path([(-160, 120), (-120, -10), (-30, -110), (70, -120), (150, -60), (175, 20), (120, -10), (60, -40), (100, 120)], closed=True, smooth=0.6),
                  fill("#E63946", red)), ks=layer_transform(p=(C - 20, C + 20), a=(0, 120), r=wobble(48, 3)))
    tip = lambda u: [C + 155 + 6 * math.sin(2 * math.pi * (u - 0.08)), C - 80 + 4 * math.cos(2 * math.pi * (u - 0.08)), 0]
    s.layer(group(circle(80), fill("#FFFFFF", white)), ks=layer_transform(p=wave(48, tip)))
    return s


def esfera_navidad() -> Sticker:
    s = Sticker("esfera-navidad", "Esfera navideña", "Christmas ornament", "fechas", frames=60, order=1003,
                tags=["navidad", "adorno", "decoración", "diciembre"])
    ball = s.slot("esfera", "#E63946")
    band = s.slot("adorno", "#FFD23F")
    zig = [(-130 + k * 26, 18 if k % 2 else -18) for k in range(11)]
    shapes = [group(oval(50, 80, -60, 120), fill("#FFFFFF", o=35)),
              group(path(zig), stroke("#FFD23F", 12, band), tr=transform(p=(0, 220))),
              group(circle(16, -80, 170), circle(16, 80, 170), circle(16, 0, 270), fill("#FFD23F", band)),
              group(circle(280, 0, 210), fill("#E63946", ball)),
              group(rrect(70, 40, 6, 0, 60), fill("#C9A15B")), group(circle(36, 0, 32), stroke("#C9A15B", 8)),
              group(line((0, -60), (0, 18)), stroke("#FFFFFF", 5))]
    s.layer(*shapes, ks=layer_transform(p=(C, 50), a=(0, -60), r=wobble(60, 8)))
    return s


def campanas() -> Sticker:
    s = Sticker("campanas-navidad", "Campanas", "Jingle bells", "fechas", frames=40, order=1004,
                tags=["navidad", "campanas", "fiestas", "boda"])
    gold = s.slot("campanas", "#FFC93C")
    bow = s.slot("lazo", "#E63946")
    bell = path([(-80, 70), (-60, 40), (-60, -30), (-30, -70), (0, -80), (30, -70), (60, -30), (60, 40), (80, 70)], closed=True, smooth=0.6)
    for side, ph in ((-1, 0), (1, 0.5)):
        s.layer(group(circle(36, 0, 80), fill("#C98A12")), group(bell, fill("#FFC93C", gold)),
                ks=layer_transform(p=(C + side * 60, C - 70), a=(0, -110), r=wave(40, lambda u, side=side, ph=ph: side * 10 + 16 * math.sin(2 * math.pi * (u + ph)), samples=16)))
    s.layer(group(oval(80, 50, -40, 0), oval(80, 50, 40, 0), stroke("#E63946", 18, bow)), group(path([(-10, 10), (-50, 80)]), path([(10, 10), (50, 80)]), stroke("#E63946", 16, bow)),
            group(circle(34), fill("#E63946", bow)), ks=layer_transform(p=(C, C - 75)))
    return s


def reloj_medianoche() -> Sticker:
    s = Sticker("reloj-medianoche", "Medianoche", "Midnight countdown", "fechas", frames=54, order=1005, loop=False,
                tags=["año nuevo", "medianoche", "cuenta regresiva", "fiesta"])
    face_c = s.slot("esfera", "#FFFFFF")
    hands = s.slot("agujas", "#111111")
    burst = s.slot("estallido", "#FFD23F")
    ticks = [line(polar(0, 0, 120, a), polar(0, 0, 140 if a % 90 else 150, a)) for a in range(0, 360, 30)]
    s.layer(group(*ticks, stroke("#111111", 10, hands)), group(circle(330), fill("#FFFFFF", face_c)), group(circle(360), fill("#FFD23F", burst)),
            ks=layer_transform(p=(C, C), s=scale_keys([(0, 0, EASE_OUT), (10, 100), (30, 100, EASE_IN_OUT), (34, 110, EASE_IN_OUT), (40, 100)])))
    s.layer(group(rrect(16, 130, 8, 0, -50), fill("#111111", hands)), ks=layer_transform(p=(C, C), r=anim([(6, -120, EASE_IN_OUT), (30, 0)])))
    s.layer(group(rrect(18, 90, 9, 0, -30), fill("#111111", hands)), ks=layer_transform(p=(C, C), r=anim([(6, -30, EASE_IN_OUT), (30, 0)])))
    s.layer(group(circle(26), fill("#111111", hands)), ks=layer_transform(p=(C, C)))
    for k in range(12):
        a = k * 30 + 15
        s.layer(group(line(polar(0, 0, 200, a), polar(0, 0, 250, a)), stroke("#FFD23F", 14, burst),
                      trim(anim([(30, 0, EASE_OUT), (38, 100)]), start=anim([(34, 0, EASE_IN_OUT), (48, 100)]))), ks=layer_transform(p=(C, C)), ip=30)
    return s


def copas_brindis() -> Sticker:
    s = Sticker("copas-brindis", "Brindis", "Cheers", "fechas", frames=48, order=1006,
                tags=["brindis", "año nuevo", "boda", "celebrar"])
    glass = s.slot("copas", "#FFFFFF")
    drink = s.slot("bebida", "#FFD23F")
    def flute(side):
        bowl = path([(-40, -120), (40, -120), (32, 20), (0, 50), (-32, 20)], closed=True, smooth=0.3)
        liquid = path([(-36, -70), (36, -70), (30, 16), (0, 44), (-30, 16)], closed=True, smooth=0.3)
        return [group(liquid, fill("#FFD23F", drink)), group(bowl, stroke("#FFFFFF", 10, glass)), group(bowl, fill("#FFFFFF", glass, o=20)),
                group(line((0, 50), (0, 150)), line((-40, 150), (40, 150)), stroke("#FFFFFF", 12, glass))]
    for side in (-1, 1):
        clink = anim([(0, side * -18, EASE_IN_OUT), (12, side * 8, EASE_OUT), (16, side * 2, EASE_IN_OUT), (26, side * -18), (48, side * -18)])
        s.layer(*flute(side), ks=layer_transform(p=anim([(0, [C + side * 90, C + 40, 0], EASE_IN_OUT), (12, [C + side * 56, C + 30, 0], EASE_OUT),
                                                         (16, [C + side * 62, C + 32, 0], EASE_IN_OUT), (26, [C + side * 90, C + 40, 0]), (48, [C + side * 90, C + 40, 0])]),
                                                 a=(0, 150), r=clink))
    for k, (x, y) in enumerate([(C, C - 150), (C - 60, C - 180), (C + 60, C - 175)]):
        s.layer(group(sparkle4(50 if k == 0 else 34), fill("#FFD23F", drink)), ks=layer_transform(p=(x, y), s=scale_keys([(10 + k * 2, 0, EASE_OUT), (16 + k * 2, 100, EASE_IN_OUT), (28 + k * 2, 0)])),
                ip=10, op=31)
    return s


def cupido() -> Sticker:
    s = Sticker("corazon-flechado", "Corazón flechado", "Heart and arrow", "fechas", frames=48, order=1007,
                tags=["san valentín", "amor", "cupido", "pareja"])
    red = s.slot("corazon", "#FF2D55")
    shaft = s.slot("flecha", "#FFD23F")
    beat = scale_keys([(0, 100, EASE_IN_OUT), (6, 112, EASE_IN_OUT), (12, 100, EASE_IN_OUT), (18, 110, EASE_IN_OUT), (24, 100), (48, 100)])
    s.layer(group(line((-200, 0), (-60, 0)), stroke("#FFD23F", 14, shaft)),
            group(path([(-200, 0), (-235, -26), (-250, -26), (-222, 0), (-250, 26), (-235, 26)], closed=True), fill("#FFD23F", shaft)),
            ks=layer_transform(p=(C, C), r=-25))
    s.layer(group(heart_path(300), fill("#FF2D55", red)), ks=layer_transform(p=(C, C), s=beat))
    s.layer(group(line((60, 0), (170, 0)), stroke("#FFD23F", 14, shaft)), group(path([(170, -26), (215, 0), (170, 26)], closed=True), fill("#FFD23F", shaft)),
            ks=layer_transform(p=(C, C), r=-25))
    return s


def carta_amor() -> Sticker:
    s = Sticker("carta-amor", "Carta de amor", "Love letter", "fechas", frames=60, order=1008, loop=False,
                tags=["san valentín", "carta", "amor", "mensaje"])
    env = s.slot("sobre", "#FFFFFF")
    flap = s.slot("solapa", "#E5E7EB")
    red = s.slot("corazon", "#FF2D55")
    s.layer(group(rrect(320, 210, 16), fill("#FFFFFF", env)), ks=layer_transform(p=(C, C + 80)))
    s.layer(group(rrect(260, 200, 10), fill("#FFF4E6")), ks=layer_transform(p=anim([(14, [C, C + 80, 0], EASE_OUT), (30, [C, C - 10, 0])])), ip=14)
    s.layer(heart("#FF2D55", red, 150), ks=layer_transform(p=anim([(22, [C, C + 40, 0], EASE_OUT), (36, [C, C - 120, 0], EASE_IN_OUT), (60, [C, C - 130, 0])]),
                                                             s=scale_keys([(22, 0, EASE_OUT), (32, 115, EASE_IN_OUT), (38, 95, EASE_IN_OUT), (42, 100), (48, 108, EASE_IN_OUT), (54, 100)])), ip=22)
    s.layer(group(path([(-160, -105), (0, 30), (160, -105), (160, 105), (-160, 105)], closed=True), fill("#F3F4F6", env)), ks=layer_transform(p=(C, C + 80)))
    s.layer(group(path([(-160, 0), (160, 0), (0, 130)], closed=True), fill("#E5E7EB", flap)),
            ks=layer_transform(p=(C, C - 25), s=anim([(0, [100, 100, 100]), (6, [100, 100, 100], EASE_IN_OUT), (16, [100, -100, 100])])))
    return s


def calabaza() -> Sticker:
    s = Sticker("calabaza", "Calabaza", "Jack-o'-lantern", "fechas", frames=36, order=1009,
                tags=["halloween", "calabaza", "octubre", "miedo"])
    orange = s.slot("calabaza", "#FF8A1F")
    glow = s.slot("luz", "#FFE066")
    flick = anim([(0, 100, LINEAR), (5, 70, LINEAR), (9, 95, LINEAR), (15, 60, LINEAR), (20, 100, LINEAR), (27, 75, LINEAR), (36, 100)])
    face = [path([(-90, -40), (-40, -40), (-65, -90)], closed=True), path([(90, -40), (40, -40), (65, -90)], closed=True),
            path([(-110, 20), (-60, 40), (-35, 20), (0, 45), (35, 20), (60, 40), (110, 20), (70, 80), (-70, 80)], closed=True)]
    s.layer(group(*face, fill("#FFE066", glow, o=flick)), group(*face, fill("#6B2E00")),
            group(oval(150, 230, -70, 0), oval(150, 230, 70, 0), fill("#FF8A1F", orange)), group(oval(170, 250, 0, 0), fill("#F07A0A")),
            group(path([(-10, -110), (0, -170), (30, -160)], smooth=0.6), stroke("#3DBE7A", 22)),
            ks=layer_transform(p=(C, C + 20), s=breathe(36, 100, 103)))
    return s


def murcielago() -> Sticker:
    s = Sticker("murcielago", "Murciélago", "Bat", "fechas", frames=24, order=1010,
                tags=["halloween", "noche", "murciélago", "miedo"])
    bat = s.slot("color", "#5B4B8A")
    eyes = s.slot("ojos", "#FFD23F")
    up = [(0, -10), (60, -70), (120, -110), (190, -60), (150, -30), (110, -20), (70, 10), (20, 20)]
    down = [(0, -10), (60, -20), (130, 10), (180, 70), (130, 60), (100, 70), (70, 60), (20, 20)]
    wing_r = morph([(0, up), (12, down), (24, up)], smooth=0.4)
    wing_l = morph([(0, [(-x, y) for x, y in up]), (12, [(-x, y) for x, y in down]), (24, [(-x, y) for x, y in up])], smooth=0.4)
    s.layer(group(circle(14, -18, -12), circle(14, 18, -12), fill("#FFD23F", eyes)),
            group(path([(-30, -40), (-20, -70), (-6, -44)], closed=True), path([(30, -40), (20, -70), (6, -44)], closed=True), fill("#5B4B8A", bat)),
            group(oval(90, 110, 0, 0), fill("#5B4B8A", bat)), group(wing_r, fill("#5B4B8A", bat)), group(wing_l, fill("#5B4B8A", bat)),
            ks=layer_transform(p=wave(24, lambda u: [C, C + 16 * math.sin(2 * math.pi * u), 0]), s=125))
    return s


def fantasma() -> Sticker:
    s = Sticker("fantasma", "Fantasma", "Ghost", "fechas", frames=60, order=1011,
                tags=["halloween", "fantasma", "boo", "miedo"])
    body = s.slot("fantasma", "#FFFFFF")
    eyes = s.slot("ojos", "#2B2D42")
    def shape(ph):
        top = [polar(0, -40, 130, a) for a in range(180, 361, 30)]
        sides = [(130, 60)]
        bottom = [(130 - k * 260 / 6, 130 + 18 * math.sin(k * math.pi + ph)) for k in range(7)]
        return top + sides + bottom + [(-130, 60)]
    sh = morph([(0, shape(0)), (20, shape(2.1)), (40, shape(4.2)), (60, shape(0))], smooth=0.7)
    blink = anim([(0, [100, 100]), (40, [100, 100], EASE_IN_OUT), (43, [100, 10], EASE_IN_OUT), (47, [100, 100]), (60, [100, 100])])
    s.layer(group(group(oval(30, 46, -45, 0), oval(30, 46, 45, 0), fill("#2B2D42", eyes)), tr=transform(p=(0, -30), s=blink)),
            group(oval(40, 50, 0, 50), fill("#2B2D42", eyes)), group(sh, fill("#FFFFFF", body)),
            ks=layer_transform(p=bob(60, C, C, 18), r=wobble(60, 5)))
    return s


def huevo_pascua() -> Sticker:
    s = Sticker("huevo-pascua", "Huevo de Pascua", "Easter egg", "fechas", frames=48, order=1012,
                tags=["pascua", "primavera", "huevo", "abril"])
    egg = s.slot("huevo", "#9AD7FF")
    a = s.slot("franja1", "#FF8FB1")
    b = s.slot("franja2", "#FFE066")
    egg_pts = [(0, -170), (90, -110), (125, 10), (100, 120), (0, 165), (-100, 120), (-125, 10), (-90, -110)]
    zig = [(-112 + k * 28, -30 + (18 if k % 2 else -18)) for k in range(9)]
    s.layer(group(circle(26, -60, 70), circle(26, 0, 90), circle(26, 60, 70), fill("#FFE066", b)), group(path(zig), stroke("#FF8FB1", 16, a)),
            group(rrect(240, 20, 10, 0, 30), fill("#FFFFFF", o=70)), group(path(egg_pts, closed=True, smooth=1.0), fill("#9AD7FF", egg)),
            ks=layer_transform(p=(C, C + 160), a=(0, 160), r=wave(48, lambda u: 9 * math.sin(2 * math.pi * u) * (1 if u < 0.5 else 0.6))))
    return s


def diya() -> Sticker:
    s = Sticker("diya", "Lámpara diya", "Diya lamp", "fechas", frames=30, order=1013,
                tags=["diwali", "luz", "lámpara", "festival"])
    lamp = s.slot("lampara", "#E07A3F")
    flame = s.slot("llama", "#FFC93C")
    dots = s.slot("detalle", "#FFE066")
    shapes = [[(0, -110), (30, -40), (24, 0), (0, 14), (-24, 0), (-30, -40)], [(10, -120), (32, -40), (22, 0), (0, 14), (-26, 0), (-26, -44)],
              [(-8, -106), (28, -42), (26, 0), (0, 14), (-22, 0), (-32, -38)]]
    fl = morph([(0, shapes[0]), (10, shapes[1]), (20, shapes[2]), (30, shapes[0])], smooth=0.9)
    s.layer(group(fl, fill("#FFC93C", flame)), ks=layer_transform(p=(C, C - 20)))
    s.layer(group(*[circle(16, x, 40) for x in (-90, -45, 0, 45, 90)], fill("#FFE066", dots)),
            group(path([(-170, -10), (170, -10), (110, 80), (-110, 80)], closed=True, smooth=0.5), fill("#E07A3F", lamp)), ks=layer_transform(p=(C, C + 30)))
    return s


def farol_chino() -> Sticker:
    s = Sticker("farol-rojo", "Farol rojo", "Red lantern", "fechas", frames=60, order=1014,
                tags=["año nuevo lunar", "farol", "festival", "asia"])
    red = s.slot("farol", "#E63946")
    gold = s.slot("dorado", "#FFC93C")
    ribs = [path([(x, -110), (x * 1.3, 0), (x, 110)], smooth=1.0) for x in (-60, 0, 60)]
    shapes = [group(*ribs, stroke("#B71C2B", 8)), group(oval(260, 230, 0, 0), fill("#E63946", red)),
              group(rrect(120, 30, 8, 0, -120), rrect(120, 30, 8, 0, 120), fill("#FFC93C", gold)),
              group(line((0, 135), (0, 210)), line((-14, 150), (-18, 210)), line((14, 150), (18, 210)), stroke("#FFC93C", 8, gold)),
              group(line((0, -135), (0, -230)), stroke("#FFC93C", 6, gold))]
    s.layer(*shapes, ks=layer_transform(p=(C, 30), a=(0, -230), r=wobble(60, 7)))
    return s


def luna_farol() -> Sticker:
    s = Sticker("luna-farol", "Luna y farol", "Crescent and lantern", "fechas", frames=72, order=1015,
                tags=["ramadán", "eid", "luna", "farol"])
    moon = s.slot("luna", "#FFD23F")
    lantern = s.slot("farol", "#3BCEAC")
    light = s.slot("luz", "#FFF4C2")
    R = 120
    outer = [polar(0, 0, R, a) for a in range(60, 301, 15)]
    (x1, y1), (x2, y2) = outer[0], outer[-1]
    cx = R * 0.55
    r2 = math.hypot(x1 - cx, y1)
    st = math.degrees(math.atan2(y2, x2 - cx))
    en = math.degrees(math.atan2(y1, x1 - cx)) - 360
    inner = [polar(cx, 0, r2, st + (en - st) * j / 12) for j in range(1, 12)]
    s.layer(group(path(outer + inner, closed=True, smooth=0.9), fill("#FFD23F", moon)), ks=layer_transform(p=(C - 90, C - 70), r=-20, s=breathe(72, 100, 104)))
    body = [group(oval(46, 70, 0, 110), fill("#FFF4C2", light)),
            group(path([(-50, 60), (50, 60), (36, 170), (-36, 170)], closed=True), stroke("#3BCEAC", 10, lantern)),
            group(path([(-50, 60), (50, 60), (36, 170), (-36, 170)], closed=True), fill("#3BCEAC", lantern, o=40)),
            group(path([(-60, 60), (0, 10), (60, 60)], closed=True), rrect(90, 20, 6, 0, 178), fill("#3BCEAC", lantern)),
            group(line((0, 10), (0, -80)), stroke("#FFD23F", 5, moon)), group(circle(20, 0, -6), stroke("#3BCEAC", 6, lantern))]
    s.layer(*body, ks=layer_transform(p=(C + 110, 30), a=(0, -80), r=wobble(72, 6)))
    for x, y, d in [(C + 10, C - 170, 0), (C - 170, C + 90, 24), (C + 170, C + 150, 48)]:
        twinkle(s, x, y, 40, d, 24, light, "#FFF4C2", 72)
    return s


def birrete() -> Sticker:
    s = Sticker("birrete", "Graduación", "Graduation cap", "fechas", frames=60, order=1016,
                tags=["graduación", "egresado", "logro", "estudios"])
    cap = s.slot("birrete", "#2B2D42")
    tassel = s.slot("borla", "#FFD23F")
    toss = anim([(0, [C, C + 60, 0], EASE_OUT), (20, [C, C - 90, 0], IN), (40, [C, C + 60, 0], EASE_OUT), (44, [C, C + 50, 0], EASE_IN_OUT), (48, [C, C + 60, 0]), (60, [C, C + 60, 0])])
    s.layer(group(line((0, 0), (130, 10), (130, 90)), stroke("#FFD23F", 8, tassel)), group(rrect(26, 50, 8, 130, 100), fill("#FFD23F", tassel)),
            group(circle(24), fill("#FFD23F", tassel)),
            group(path([(0, -90), (210, 0), (0, 90), (-210, 0)], closed=True), fill("#2B2D42", cap), stroke("#6B7090", 8)),
            group(path([(-110, 30), (110, 30), (110, 110), (0, 130), (-110, 110)], closed=True, smooth=0.3), fill("#1A1B29")),
            ks=layer_transform(p=toss, r=anim([(0, 0, EASE_OUT), (20, -12, IN), (40, 0), (60, 0)]), s=scale_keys([(0, 100), (38, 100, EASE_OUT), (40, [108, 92, 100], EASE_IN_OUT), (46, 100)])))
    for x, y, d in [(C - 160, C - 150, 14), (C + 170, C - 120, 18), (C + 150, C + 160, 44)]:
        twinkle(s, x, y, 46, d, 18, tassel, "#FFD23F", 60)
    return s


def anillos_boda() -> Sticker:
    s = Sticker("anillos-boda", "Anillos de boda", "Wedding rings", "fechas", frames=60, order=1017,
                tags=["boda", "matrimonio", "compromiso", "aniversario"])
    gold = s.slot("anillos", "#FFC93C")
    gem = s.slot("diamante", "#BFE6FF")
    s.layer(group(circle(190), stroke("#FFC93C", 26, gold)), ks=layer_transform(p=bob(60, C - 60, C + 40, 8)))
    s.layer(group(path([(-30, -10), (0, -40), (30, -10), (0, 25)], closed=True), fill("#BFE6FF", gem)), group(rrect(40, 22, 4, 0, 30), fill("#FFC93C", gold)),
            group(circle(190, 0, 150), stroke("#FFC93C", 26, gold)), ks=layer_transform(p=bob(60, C + 60, C - 110, 8, 10), r=wobble(60, 5)))
    for x, y, d in [(C + 60, C - 230, 10), (C + 170, C - 60, 40), (C - 180, C - 30, 25)]:
        twinkle(s, x, y, 50, d, 22, s.slot("brillo", "#FFFFFF"), "#FFFFFF", 60)
    return s


# --- Comida ------------------------------------------------------------------------------------


def cafe() -> Sticker:
    s = Sticker("cafe-humeante", "Café humeante", "Hot coffee", "comida", frames=60, order=1101,
                tags=["café", "mañana", "desayuno", "bebida"])
    cup = s.slot("taza", "#FFFFFF")
    coffee = s.slot("cafe", "#7B4A2B")
    st = s.slot("vapor", "#FFFFFF")
    s.layer(group(oval(320, 50, 0, 120), fill("#E5E7EB")), group(oval(200, 34, 0, -60), fill("#7B4A2B", coffee)),
            group(path([(-110, -60), (110, -60), (90, 90), (-90, 90)], closed=True, smooth=0.25), fill("#FFFFFF", cup)),
            group(path([(100, -20), (160, -10), (150, 50), (90, 50)], smooth=1.0), stroke("#FFFFFF", 22, cup)), ks=layer_transform(p=(C - 10, C + 60)))
    steam(s, 60, C - 10, C - 30, st, "#FFFFFF", count=3, spread=50, height=130, width=12)
    return s


def pizza() -> Sticker:
    s = Sticker("pizza", "Pizza", "Pizza slice", "comida", frames=48, order=1102,
                tags=["pizza", "comida", "noche de pizza", "delivery"])
    cheese = s.slot("queso", "#FFD23F")
    crust = s.slot("borde", "#E0A35A")
    pep = s.slot("pepperoni", "#E63946")
    tri = path([(-150, -140), (150, -140), (0, 190)], closed=True)
    drip = morph([(0, [(-30, 60), (-14, 60), (-14, 100), (-22, 112), (-30, 100)]), (24, [(-30, 60), (-14, 60), (-14, 140), (-22, 152), (-30, 140)]),
                  (48, [(-30, 60), (-14, 60), (-14, 100), (-22, 112), (-30, 100)])], closed=True, smooth=0.6)
    s.layer(group(circle(50, -50, -70), circle(46, 50, -60), circle(40, 5, 20), circle(30, -20, 100), fill("#E63946", pep)),
            group(drip, fill("#FFD23F", cheese)), group(tri, fill("#FFD23F", cheese)), group(rrect(330, 56, 28, 0, -150), fill("#E0A35A", crust)),
            ks=layer_transform(p=(C, C - 20), r=wobble(48, 5), s=breathe(48, 100, 104)))
    return s


def hamburguesa() -> Sticker:
    s = Sticker("hamburguesa", "Hamburguesa", "Burger", "comida", frames=40, order=1103, loop=False,
                tags=["hamburguesa", "comida rápida", "almuerzo", "delivery"])
    bun = s.slot("pan", "#E8A24A")
    meat = s.slot("carne", "#6B3A1E")
    lettuce = s.slot("lechuga", "#5CC56A")
    cheese = s.slot("queso", "#FFD23F")
    layers = [  # (shapes, y), from the bottom up
        ([group(rrect(280, 50, 22), fill("#E8A24A", bun))], 120),
        ([group(rrect(290, 54, 27), fill("#6B3A1E", meat))], 75),
        ([group(path([(-150, -12), (150, -12), (150, 0), (90, 34), (70, 4), (-40, 30), (-60, 4), (-150, 6)], closed=True), fill("#FFD23F", cheese))], 44),
        ([group(path([(-155, 0)] + [(-155 + k * 31, 14 if k % 2 else -4) for k in range(11)] + [(155, -16), (-155, -16)], closed=True, smooth=0.5), fill("#5CC56A", lettuce))], 26),
        ([group(*[oval(14, 8, x, y) for x, y in ((-60, -60), (-10, -78), (40, -64), (80, -40), (-90, -30))], fill("#FFF4E0")),
          group(path([(-150, 0), (-140, -70), (-60, -112), (60, -112), (140, -70), (150, 0)], closed=True, smooth=0.5), fill("#E8A24A", bun))], 10),
    ]
    for k, (shapes, y) in enumerate(layers):
        d = k * 5
        s.layer(*shapes, ks=layer_transform(p=anim([(d, [C, -150, 0], FALL), (d + 10, [C, C + y, 0])]),
                                            s=scale_keys([(d + 10, [108, 90, 100], EASE_OUT), (d + 15, [97, 104, 100], EASE_IN_OUT), (d + 19, 100)])), ip=d)
    return s


def helado() -> Sticker:
    s = Sticker("helado", "Helado", "Ice cream", "comida", frames=60, order=1104,
                tags=["helado", "verano", "postre", "dulce"])
    cone = s.slot("cono", "#E0A35A")
    a = s.slot("bola1", "#FF8FB1")
    b = s.slot("bola2", "#9AD7FF")
    cherry = s.slot("cereza", "#E63946")
    grid = [line((-80 + k * 40, 0), (k * 10, 200)) for k in range(5)]
    s.layer(group(*grid, stroke("#B9793A", 6)), group(path([(-90, 0), (90, 0), (0, 210)], closed=True), fill("#E0A35A", cone)), ks=layer_transform(p=(C, C + 40)))
    s.layer(group(path([(-40, 30), (-30, 70), (-20, 30)], closed=True, smooth=0.6), fill("#9AD7FF", b)), group(circle(190, 0, 0), fill("#9AD7FF", b)),
            ks=layer_transform(p=(C, C + 10), r=wobble(60, 3)))
    s.layer(group(circle(170, 0, 0), fill("#FF8FB1", a)), ks=layer_transform(p=(C, C - 110), r=wobble(60, 4)))
    s.layer(group(path([(0, -10), (10, -50), (30, -70)], smooth=1.0), stroke("#3DBE7A", 6)), group(circle(54), fill("#E63946", cherry)),
            ks=layer_transform(p=wave(60, lambda u: [C + 6 * math.sin(2 * math.pi * u), C - 205 + 4 * math.cos(2 * math.pi * u), 0])))
    return s


def dona() -> Sticker:
    s = Sticker("dona", "Dona", "Donut", "comida", frames=90, order=1105,
                tags=["dona", "postre", "dulce", "desayuno"])
    dough = s.slot("masa", "#E8A24A")
    icing = s.slot("glaseado", "#FF8FB1")
    sprinkles = [("c1", "#FFFFFF"), ("c2", "#5BC0FF"), ("c3", "#FFD23F")]
    for sid, col in sprinkles:
        s.slot(sid, col)
    rng = random.Random(7)
    bits = []
    for sid, col in sprinkles:
        group_bits = []
        for _ in range(7):
            r = rng.uniform(125, 180)
            a = rng.uniform(0, 360)
            x, y = polar(0, 0, r, a)
            group_bits.append(group(rrect(26, 9, 4), tr=transform(p=(x, y), r=rng.uniform(0, 180))))
        bits.append(group(*group_bits, fill(col, sid)))
    # Real rings (thick strokes), so the hole stays see-through over any video.
    icing_pts = [polar(0, 0, 155 + (10 if k % 2 else -6), k * 20) for k in range(18)]
    s.layer(group(circle(330), stroke("#E8A24A", 110, dough)), ks=layer_transform(p=(C, C)))
    s.layer(*bits, group(path(icing_pts, closed=True, smooth=1.0), stroke("#FF8FB1", 84, icing)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (90, 360)])))
    return s


def refresco() -> Sticker:
    s = Sticker("refresco", "Bebida con pajita", "Soda cup", "comida", frames=60, order=1106,
                tags=["bebida", "refresco", "verano", "fiesta"])
    cup = s.slot("vaso", "#FF4D6D")
    straw = s.slot("pajita", "#FFFFFF")
    lid = s.slot("tapa", "#FFFFFF")
    s.layer(group(path([(10, -150), (60, -260), (110, -260)]), stroke("#FFFFFF", 22, straw)), ks=layer_transform(p=(C, C + 40)))
    s.layer(group(rrect(140, 30, 6, 0, 40), fill("#FFFFFF", lid, o=85)), group(rrect(260, 40, 20, 0, -150), fill("#FFFFFF", lid)),
            group(path([(-110, -130), (110, -130), (85, 170), (-85, 170)], closed=True), fill("#FF4D6D", cup)),
            ks=layer_transform(p=(C, C + 40), r=wobble(60, 3)))
    for k in range(4):
        x = C - 50 + k * 34
        def make(t0, x=x):
            return [group(circle(20), stroke("#FFFFFF", 5, lid))], layer_transform(p=anim([(t0, [x, C + 190, 0], LINEAR), (t0 + 30, [x + 6, C - 60, 0])]),
                                                                              o=anim([(t0, 0), (t0 + 4, 80), (t0 + 24, 80), (t0 + 30, 0)]))
        cyclic(s, 60, k * 15, 30, make)
    return s


def palomitas() -> Sticker:
    s = Sticker("palomitas", "Palomitas", "Popcorn", "comida", frames=48, order=1107,
                tags=["cine", "película", "palomitas", "maratón"])
    box = s.slot("caja", "#E63946")
    stripe = s.slot("rayas", "#FFFFFF")
    corn = s.slot("maiz", "#FFF4D6")
    def kernel():
        return [group(circle(56, 0, 0), circle(44, -26, 14), circle(44, 26, 12), fill("#FFF4D6", corn))]
    for k, (x, y) in enumerate([(-80, -110), (-20, -140), (50, -120), (100, -100), (10, -95), (-110, -90)]):
        s.layer(*kernel(), ks=layer_transform(p=(C + x, C + y - 20)))
    stripes = [path([(-100 + k * 60, -80), (-70 + k * 60, -80), (-62 + k * 52, 170), (-86 + k * 52, 170)], closed=True) for k in range(4)]
    s.layer(group(*stripes, fill("#FFFFFF", stripe)), group(path([(-150, -80), (150, -80), (110, 170), (-110, 170)], closed=True), fill("#E63946", box)),
            ks=layer_transform(p=(C, C + 70)))
    for k in range(4):
        def make(t0, k=k):
            x = [-60, 70, 0, -120][k]
            return kernel(), layer_transform(p=anim([(t0, [C + x * 0.5, C - 80, 0], EASE_OUT), (t0 + 10, [C + x, C - 220, 0], IN), (t0 + 20, [C + x * 1.3, C - 120, 0])]),
                                             s=scale_keys([(t0, 30, EASE_OUT), (t0 + 6, 100)]), r=anim([(t0, 0, LINEAR), (t0 + 20, 200)]),
                                             o=anim([(t0, 100), (t0 + 16, 100), (t0 + 20, 0)]))
        cyclic(s, 48, k * 12, 20, make)
    return s


def sandia() -> Sticker:
    s = Sticker("sandia", "Sandía", "Watermelon", "comida", frames=48, order=1108,
                tags=["sandía", "fruta", "verano", "fresco"])
    rind = s.slot("cascara", "#3DBE7A")
    flesh = s.slot("pulpa", "#FF4D6D")
    seeds = [oval(14, 22, x, y) for x, y in ((-70, -40), (0, -50), (70, -40), (-35, 10), (35, 10), (0, 60))]
    wedge = [polar(0, -150, 220, a) for a in range(20, 161, 20)]
    wedge_in = [polar(0, -150, 190, a) for a in range(20, 161, 20)]
    s.layer(group(*seeds, fill("#2B2D42")), group(path([(0, -150)] + wedge_in, closed=True, smooth=0), fill("#FF4D6D", flesh)),
            group(path([(0, -150)] + wedge, closed=True), fill("#F2FFF2")), group(path([(0, -160)] + [polar(0, -160, 245, a) for a in range(20, 161, 20)], closed=True), fill("#3DBE7A", rind)),
            ks=layer_transform(p=(C, C - 20), r=wobble(48, 6), s=breathe(48, 100, 104)))
    return s


def fideos() -> Sticker:
    s = Sticker("tazon-fideos", "Tazón de fideos", "Noodle bowl", "comida", frames=60, order=1109,
                tags=["fideos", "ramen", "sopa", "cena"])
    bowl = s.slot("tazon", "#FF4D6D")
    noodle = s.slot("fideos", "#FFE29A")
    sticks = s.slot("palillos", "#C98A4A")
    st = s.slot("vapor", "#FFFFFF")
    s.layer(group(line((40, -40), (180, -240)), line((70, -30), (220, -220)), stroke("#C98A4A", 14, sticks)), ks=layer_transform(p=(C, C + 40)))
    s.layer(group(path([(-120, -10), (-80, -40), (-40, -10), (0, -40), (40, -10), (80, -40), (120, -10)], smooth=1.0), stroke("#FFE29A", 14, noodle)),
            group(oval(300, 60, 0, -10), fill("#FFE29A", noodle)),
            group(path([(-170, -10), (170, -10), (120, 120), (-120, 120)], closed=True, smooth=0.5), fill("#FF4D6D", bowl)),
            group(rrect(120, 24, 8, 0, 128), fill("#C81E4E")), ks=layer_transform(p=(C, C + 70)))
    steam(s, 60, C - 30, C - 10, st, "#FFFFFF", count=3, spread=55, height=130, width=12)
    return s


def cupcake() -> Sticker:
    s = Sticker("cupcake", "Cupcake", "Cupcake", "comida", frames=48, order=1110,
                tags=["cupcake", "postre", "cumpleaños", "dulce"])
    cup = s.slot("capacillo", "#5BC0FF")
    cream = s.slot("crema", "#FF8FB1")
    cherry = s.slot("cereza", "#E63946")
    pleats = [line((-90 + k * 36, 0), (-72 + k * 29, 140)) for k in range(6)]
    s.layer(group(*pleats, stroke("#3B8FD0", 7)), group(path([(-110, 0), (110, 0), (80, 150), (-80, 150)], closed=True), fill("#5BC0FF", cup)), ks=layer_transform(p=(C, C + 40)))
    s.layer(group(oval(240, 70, 0, 0), oval(190, 70, 0, -50), oval(130, 66, 0, -95), oval(60, 50, 0, -128), fill("#FF8FB1", cream)),
            ks=layer_transform(p=(C, C + 30), a=(0, 20), s=scale_keys([(0, 100, EASE_IN_OUT), (12, [104, 96, 100], EASE_IN_OUT), (24, 100, EASE_IN_OUT), (36, [97, 103, 100], EASE_IN_OUT), (48, 100)])))
    s.layer(group(path([(0, -10), (6, -40), (26, -56)], smooth=1.0), stroke("#3DBE7A", 6)), group(circle(50), fill("#E63946", cherry)),
            ks=layer_transform(p=bob(48, C, C - 140, 6)))
    return s


STICKERS = [arbol_navidad, gorro_santa, esfera_navidad, campanas, reloj_medianoche, copas_brindis, cupido, carta_amor, calabaza, murcielago,
            fantasma, huevo_pascua, diya, farol_chino, luna_farol, birrete, anillos_boda,
            cafe, pizza, hamburguesa, helado, dona, refresco, palomitas, sandia, fideos, cupcake]
