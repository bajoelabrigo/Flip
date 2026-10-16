"""Third set of stickers (BRIEF.md › «Tanda de 200»): celebration, highlights and arrows."""

from __future__ import annotations

import math
import random

from kit import (FALL, IN, arrow_head, sample_curve, at, bob, breathe, circle, circle_pts, cyclic, draw_on, heart_path, line, morph,
                 oval, outline, pop, rrect, scale_keys, solid, swing, wave, wobble)
from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, layer_transform, path,
                    polar, rect, star, static, stroke, transform, trim)

C = 256


def sparkle4(size=60):
    """A four-point sparkle with concave sides (the Y2K / «brillo» shape)."""
    r, k = size / 2, size * 0.06
    pts = [(0, -r), (k, -k), (r, 0), (k, k), (0, r), (-k, k), (-r, 0), (-k, -k)]
    return path(pts, closed=True)


def twinkle(s, x, y, size, start, length, sid, colour, frames):
    """A sparkle that grows, turns and vanishes; wraps around the loop."""
    def make(t0):
        return [group(sparkle4(size), fill(colour, sid))], layer_transform(
            p=(x, y), s=scale_keys([(t0, 0, EASE_OUT), (t0 + length * 0.45, 100, EASE_IN_OUT), (t0 + length, 0)]),
            r=anim([(t0, 0, LINEAR), (t0 + length, 90)]))
    cyclic(s, frames, start, length, make)


# --- Celebración --------------------------------------------------------------------------------


def cono_fiesta() -> Sticker:
    s = Sticker("cono-fiesta", "Cañón de confeti", "Party popper", "celebracion", frames=60, order=81, thumb=0.33,
                tags=["fiesta", "cumpleaños", "sorpresa", "celebrar"])
    a = s.slot("cono", "#7B2FF7")
    b = s.slot("rayas", "#FFD23F")
    rng = random.Random(21)
    confetti = [("c1", "#FF4D6D"), ("c2", "#FFD23F"), ("c3", "#3BCEAC"), ("c4", "#5BC0FF")]
    for sid, col in confetti:
        s.slot(sid, col)
    # Cone: tip down-left, mouth up-right. Bands are drawn before the cone so they sit on top.
    def half(y):
        return 78 * (120 - y) / 210
    bands = []
    for y1, y2 in ((-60, -25), (10, 45), (80, 110)):
        bands.append(path([(-half(y1), y1), (half(y1), y1), (half(y2), y2), (-half(y2), y2)], closed=True))
    cone_shapes = [group(oval(156, 40, 0, -90), fill("#2A0E5C")), group(*bands, fill("#FFD23F", b)),
                   group(path([(-78, -90), (78, -90), (0, 120)], closed=True), fill("#7B2FF7", a))]
    s.layer(*cone_shapes, ks=layer_transform(p=(196, 336), r=35,
                                             s=scale_keys([(0, 100, EASE_IN_OUT), (6, 92, EASE_OUT), (10, 108, EASE_IN_OUT),
                                                           (18, 98, EASE_IN_OUT), (24, 100)])))
    mx, my = 196 + 90 * math.sin(math.radians(35)), 336 - 90 * math.cos(math.radians(35))
    for k in range(22):
        sid, col = confetti[k % 4]
        ang = rng.uniform(-105, -15)
        dist = rng.uniform(150, 300)
        ex, ey = polar(mx, my, dist, ang)
        d = 8 + rng.randint(0, 4)
        shape = rect((rng.uniform(14, 22), rng.uniform(8, 11)), r=2) if k % 3 else ellipse((14, 14))
        s.layer(group(shape, fill(col, sid)), ks=layer_transform(
            p=anim([(d, [mx, my, 0], EASE_OUT), (d + 16, [ex, ey, 0], EASE_IN_OUT), (56, [ex + rng.uniform(-25, 25), ey + rng.uniform(70, 130), 0])]),
            r=anim([(d, 0, LINEAR), (56, rng.uniform(-500, 500))]),
            s=scale_keys([(d, 30, EASE_OUT), (d + 6, 100), (46, 100, IN), (56, 0)])), ip=d, op=57)
    for k, (sid, col) in enumerate(confetti[:2]):
        curl = [(0, 0), (40, -50), (20, -95), (70, -120), (110, -100), (140, -150)]
        rot = -20 + k * 45
        s.layer(group(path(curl, smooth=1.0), stroke(col, 9, sid),
                      trim(anim([(9, 0, EASE_OUT), (24, 100)]), start=anim([(30, 0, EASE_IN_OUT), (50, 100)]))),
                ks=layer_transform(p=(mx, my), r=rot), ip=9, op=52)
    return s


def pastel_velas() -> Sticker:
    s = Sticker("pastel-velas", "Pastel con velas", "Birthday cake", "celebracion", frames=60, order=82,
                tags=["cumpleaños", "pastel", "torta", "fiesta"])
    cake = s.slot("pastel", "#FF8FB1")
    icing = s.slot("crema", "#FFFFFF")
    candle = s.slot("velas", "#5BC0FF")
    flame = s.slot("llama", "#FFC93C")
    s.layer(group(oval(340, 50, 0, 0), fill("#FFFFFF", o=25)), ks=layer_transform(p=(C, 410)))
    # Bottom tier then its icing drips (drips first in the list = on top).
    drips = [circle(36, x, -42) for x in range(-110, 111, 44)]
    s.layer(group(*drips, rrect(270, 26, 13, 0, -52), fill("#FFFFFF", icing)),
            group(rrect(270, 120, 20, 0, 0), fill("#FF8FB1", cake)), ks=layer_transform(p=(C, 345)))
    drips2 = [circle(30, x, -38) for x in range(-75, 76, 37)]
    s.layer(group(*drips2, rrect(196, 24, 12, 0, -48), fill("#FFFFFF", icing)),
            group(rrect(196, 100, 18, 0, 0), fill("#FF8FB1", cake, o=100)), ks=layer_transform(p=(C, 236)))
    for k, x in enumerate((-60, 0, 60)):
        s.layer(group(rrect(10, 60, 0, 6, 0), fill("#FFFFFF", o=45)), group(rrect(22, 64, 6), fill("#5BC0FF", candle)),
                ks=layer_transform(p=(C + x, 160)))
        shapes = [[(0, -38), (12, -12), (13, 4), (0, 14), (-13, 4), (-12, -12)],
                  [(6, -40), (14, -12), (12, 4), (0, 14), (-13, 4), (-10, -14)],
                  [(-5, -36), (11, -12), (13, 4), (0, 14), (-12, 4), (-13, -10)]]
        seq = [shapes[(k + j) % 3] for j in range(3)] + [shapes[k % 3]]
        flick = morph([(round(j * 20 / 3) + 20 * c, seq[j % 3 if j < 3 else 0]) for c in range(3) for j in range(3)] + [(60, seq[0])])
        s.layer(group(circle(54), fill("#FFC93C", flame, o=22)), group(flick, fill("#FFC93C", flame)),
                ks=layer_transform(p=(C + x, 112)))
    return s


def regalo_sorpresa() -> Sticker:
    s = Sticker("regalo-sorpresa", "Regalo sorpresa", "Surprise gift", "celebracion", frames=54, order=83, loop=False,
                tags=["regalo", "sorpresa", "cumpleaños", "navidad"])
    box = s.slot("caja", "#FF4D6D")
    ribbon = s.slot("cinta", "#FFD23F")
    star_c = s.slot("estrellas", "#FFFFFF")
    shake = anim([(0, 0, EASE_IN_OUT), (14, 0, EASE_IN_OUT), (17, -7, EASE_IN_OUT), (20, 7, EASE_IN_OUT), (23, -6, EASE_IN_OUT),
                  (26, 4, EASE_IN_OUT), (29, 0)])
    s.layer(group(rect((40, 170), p=(0, 0)), fill("#FFD23F", ribbon)), group(rrect(220, 170, 12), fill("#FF4D6D", box)),
            ks=layer_transform(p=(C, 430), a=(0, 85), s=pop(0, 14), r=shake))
    for k in range(7):
        ang = -90 + (k - 3) * 26
        x, y = polar(C, 250, 175 + (k % 2) * 30, ang)
        sz = 70 if k % 2 else 50
        s.layer(group(star(5, sz / 2, sz / 4.4, roundness=8), fill("#FFFFFF", star_c)),
                ks=layer_transform(p=anim([(30, [C, 260, 0], EASE_OUT), (44, [x, y, 0])]), s=pop(30, 14),
                                   r=anim([(30, -90, EASE_OUT), (44, 0)])), ip=30)
    lid = [group(oval(70, 50, -38, -42), oval(70, 50, 38, -42), stroke("#FFD23F", 16, ribbon)),
           group(rect((44, 56)), fill("#FFD23F", ribbon)), group(rrect(244, 56, 12), fill("#FF4D6D", box))]
    s.layer(*lid, ks=layer_transform(
        p=anim([(0, [C, 232, 0]), (29, [C, 232, 0], EASE_OUT), (40, [C - 30, 110, 0], EASE_IN_OUT), (54, [C - 34, 122, 0])]),
        a=(0, 0), s=pop(4, 14), r=anim([(0, 0), (14, 0, EASE_IN_OUT), (17, -5, EASE_IN_OUT), (20, 5, EASE_IN_OUT), (23, -4, EASE_IN_OUT),
                                         (26, 3, EASE_IN_OUT), (29, 0, EASE_OUT), (40, -24, EASE_IN_OUT), (54, -18)])))
    return s


def gorro_fiesta() -> Sticker:
    s = Sticker("gorro-fiesta", "Gorro de fiesta", "Party hat", "celebracion", frames=48, order=84,
                tags=["fiesta", "cumpleaños", "celebrar"])
    hat = s.slot("gorro", "#3BCEAC")
    dots = s.slot("lunares", "#FFFFFF")
    pom = s.slot("pompon", "#FFD23F")
    def inside(x, y):
        return y > -140 and abs(x) < 115 * (y + 150) / 260 - 18
    spots = [circle(24, x + (23 if ((y + 90) // 46) % 2 else 0), y) for y in range(-90, 100, 46) for x in range(-100, 101, 46)
             if inside(x + (23 if ((y + 90) // 46) % 2 else 0), y)]
    fringe = [circle(36, x, 112) for x in range(-104, 105, 26)]
    body = [group(*fringe, fill("#FFD23F", pom)), group(*spots, fill("#FFFFFF", dots)),
            group(path([(-118, 110), (118, 110), (0, -150)], closed=True), fill("#3BCEAC", hat))]
    s.layer(*body, ks=layer_transform(p=(C, 400), a=(0, 110), r=wobble(48, 5)))
    # The pompom rides the tip with a short lag.
    tip = lambda u: [C + 260 * math.sin(math.radians(5 * math.sin(2 * math.pi * (u - 0.06)))), 400 - 260 * math.cos(math.radians(5 * math.sin(2 * math.pi * (u - 0.06)))) - 14, 0]
    s.layer(group(circle(70), fill("#FFD23F", pom)), ks=layer_transform(
        p=wave(48, tip), s=wave(48, lambda u: [100 + 8 * math.sin(4 * math.pi * u), 100 - 8 * math.sin(4 * math.pi * u), 100])))
    return s


def bola_disco() -> Sticker:
    s = Sticker("bola-disco", "Bola de disco", "Disco ball", "celebracion", frames=90, order=85,
                tags=["fiesta", "baile", "noche", "disco"])
    base = s.slot("bola", "#4B5563")
    tile = s.slot("espejos", "#D9DEE8")
    light = s.slot("brillo", "#FFFFFF")
    R, cy = 125, 290
    s.layer(group(line((C, 0), (C, cy - R)), stroke("#D9DEE8", 6)), ks=layer_transform(p=(0, 0)))
    s.layer(group(circle(2 * R + 8), fill("#4B5563", base)), ks=layer_transform(p=(C, cy)))
    lat_step, lon_step = 22.5, 22.5
    tiles = []
    for row in range(-3, 4):
        lat = row * lat_step
        rr = R * math.cos(math.radians(lat))
        y = cy + R * math.sin(math.radians(lat))
        th = 26 * math.cos(math.radians(lat)) + 2
        shade = 100 - abs(row) * 12
        for k in range(-5, 5):
            lon0 = k * lon_step
            def pos(u, lon0=lon0):
                lon = math.radians(lon0 + lon_step * u)
                return [C + rr * math.sin(lon), y]
            def size(u, lon0=lon0):
                lon = math.radians(lon0 + lon_step * u)
                return [max(0.0, 100 * math.cos(lon)), 100]
            if lon0 + lon_step < -90 or lon0 > 90:
                continue
            keys_p, keys_s = [], []
            for j in range(9):
                u = j / 8
                keys_p.append((round(90 * u, 2), pos(u), LINEAR))
                keys_s.append((round(90 * u, 2), size(u), LINEAR))
            tr = {"ty": "tr", "p": anim(keys_p), "a": static([0, 0]), "s": anim(keys_s), "r": static(0), "o": static(shade),
                  "sk": static(0), "sa": static(0)}
            tiles.append(group(rrect(rr * math.radians(lon_step) - 3, th, 3), fill("#D9DEE8", tile), tr=tr))
    s.layer(*tiles, ks=layer_transform(p=(0, 0)))
    for k, (x, y, sz, d) in enumerate([(C - 60, cy - 70, 70, 0), (C + 70, cy + 30, 50, 30), (C - 20, cy + 80, 40, 60),
                                       (C + 150, cy - 120, 46, 15), (C - 160, cy + 10, 40, 48)]):
        twinkle(s, x, y, sz, d, 26, light, "#FFFFFF", 90)
    return s


def medalla() -> Sticker:
    s = Sticker("medalla", "Medalla", "Medal", "celebracion", frames=60, order=86, thumb=0.8,
                tags=["ganador", "premio", "logro", "primer lugar"])
    gold = s.slot("medalla", "#FFC93C")
    rib_a = s.slot("cinta", "#3B82F6")
    rib_b = s.slot("cinta2", "#E63946")
    shine = s.slot("brillo", "#FFFFFF")
    # Pivot at the top of the ribbon, so it swings like it hangs from a neck.
    shapes = [group(star(5, 46, 21, roundness=8, p=(0, 250)), fill("#FFFFFF", shine, o=85)),
              group(circle(124, 0, 250), stroke("#B7811C", 8)),
              group(circle(160, 0, 250), fill("#FFC93C", gold)),
              group(path([(-70, 0), (-20, 0), (40, 190), (-10, 190)], closed=True), fill("#3B82F6", rib_a)),
              group(path([(70, 0), (20, 0), (-40, 190), (10, 190)], closed=True), fill("#E63946", rib_b))]
    s.layer(*shapes, ks=layer_transform(p=anim([(0, [C, -340, 0], FALL), (14, [C, 50, 0])]), r=swing(40, 12, 3, start=14)))
    twinkle(s, C + 70, 240, 56, 40, 18, shine, "#FFFFFF", 60)
    return s


def corona() -> Sticker:
    s = Sticker("corona", "Corona", "Crown", "celebracion", frames=60, order=87,
                tags=["rey", "reina", "ganador", "premium"])
    gold = s.slot("corona", "#FFC93C")
    gem = s.slot("gemas", "#FF4D6D")
    light = s.slot("brillo", "#FFFFFF")
    shapes = [group(circle(30, -120, -58), circle(30, 120, -58), circle(36, 0, -98), fill("#FFC93C", gold)),
              group(circle(30, -70, 62), circle(36, 0, 62), circle(30, 70, 62), fill("#FF4D6D", gem)),
              group(rrect(250, 50, 10, 0, 62), fill("#E8A92A")),
              group(path([(-125, 80), (-125, -45), (-62, 5), (0, -85), (62, 5), (125, -45), (125, 80)], closed=True), fill("#FFC93C", gold))]
    s.layer(*shapes, ks=layer_transform(p=bob(60, C, C + 20, 10), r=wobble(60, 3)))
    for x, y, sz, d in [(C - 150, C - 120, 50, 0), (C + 160, C - 90, 60, 20), (C + 120, C + 110, 40, 40)]:
        twinkle(s, x, y, sz, d, 24, light, "#FFFFFF", 60)
    return s


def banderines() -> Sticker:
    s = Sticker("banderines", "Banderines", "Bunting flags", "celebracion", frames=60, order=88,
                tags=["fiesta", "decoración", "cumpleaños", "inauguración"])
    cols = [("c1", "#FF4D6D"), ("c2", "#FFD23F"), ("c3", "#3BCEAC"), ("c4", "#5BC0FF")]
    for sid, col in cols:
        s.slot(sid, col)
    x0, x1, top, sag = 24, 488, 150, 70
    def y_at(x):
        u = (x - x0) / (x1 - x0)
        return top + sag * 4 * u * (1 - u)
    pts = [(x, y_at(x)) for x in range(x0, x1 + 1, 29)]
    s.layer(group(path(pts, smooth=1.0), stroke("#FFFFFF", 5)), ks=layer_transform(p=(0, 0)))
    for k in range(7):
        x = x0 + (k + 0.5) * (x1 - x0) / 7
        y = y_at(x)
        slope = math.degrees(math.atan(sag * 4 * (1 - 2 * (x - x0) / (x1 - x0)) / (x1 - x0)))
        sid, col = cols[k % 4]
        s.layer(group(path([(-30, 0), (30, 0), (0, 72)], closed=True), fill(col, sid)),
                ks=layer_transform(p=(x, y), r=wave(60, lambda u, k=k, sl=slope: sl + 7 * math.sin(2 * math.pi * (u - k * 0.09)))))
    return s


def varita_magica() -> Sticker:
    s = Sticker("varita-magica", "Varita mágica", "Magic wand", "celebracion", frames=60, order=89,
                tags=["magia", "deseo", "sorpresa", "brillo"])
    wand = s.slot("varita", "#9D4EDD")
    tip = s.slot("estrella", "#FFD23F")
    spark = s.slot("chispas", "#FFFFFF")
    hx, hy, length = 150, 420, 300
    angle = lambda u: -40 + 28 * math.sin(2 * math.pi * u)
    def tip_pos(u):
        # The wand points straight up at rotation 0; rotation is clockwise.
        a = math.radians(angle(u) + 50)
        return hx + length * math.sin(a), hy - length * math.cos(a)
    for k in range(8):
        u0 = k / 8
        x, y = tip_pos(u0)
        def make(t0, x=x, y=y, k=k):
            return [group(sparkle4(34 + (k % 3) * 12), fill("#FFFFFF", spark))], layer_transform(
                p=anim([(t0, [x, y, 0], EASE_OUT), (t0 + 20, [x - 10, y + 30, 0])]),
                s=scale_keys([(t0, 0, EASE_OUT), (t0 + 6, 100, EASE_IN_OUT), (t0 + 20, 0)]))
        cyclic(s, 60, round(u0 * 60), 20, make)
    shapes = [group(star(5, 66, 28, roundness=10, p=(0, -length)), fill("#FFD23F", tip)),
              group(rrect(30, 60, 6, 0, -length + 66), fill("#FFFFFF")),
              group(rrect(30, length, 12, 0, -length / 2), fill("#9D4EDD", wand))]
    s.layer(*shapes, ks=layer_transform(p=(hx, hy), r=wave(60, lambda u: angle(u) + 50)))
    return s


def bengala() -> Sticker:
    s = Sticker("bengala", "Bengala", "Sparkler", "celebracion", frames=30, order=90,
                tags=["año nuevo", "fiesta", "boda", "chispas"])
    stick = s.slot("varilla", "#9CA3AF")
    spark = s.slot("chispas", "#FFD23F")
    core = s.slot("centro", "#FFFFFF")
    hx, hy = 210, 230
    s.layer(group(line((hx, hy), (380, 450)), stroke("#9CA3AF", 10, stick)), ks=layer_transform(p=(0, 0)))
    s.layer(group(circle(150), fill("#FFD23F", spark, o=18)), ks=layer_transform(p=(hx, hy), s=wave(30, lambda u: [100 + 10 * math.sin(6 * math.pi * u)] * 2 + [100])))
    rng = random.Random(3)
    for g in range(3):
        rays = []
        for k in range(14):
            a = k * 360 / 14 + g * 9 + rng.uniform(-5, 5)
            r0, r1 = 22, rng.uniform(70, 120)
            rays.append(line(polar(0, 0, r0, a), polar(0, 0, r1, a)))
        on = [0, 0, 0]
        on[g] = 100
        keys = []
        for f in range(0, 31, 2):
            keys.append((f, 100 if (f // 2) % 3 == g else 15, LINEAR))
        s.layer(group(*rays, stroke("#FFD23F", 5, spark)), ks=layer_transform(p=(hx, hy), o=anim(keys)))
    s.layer(group(circle(40), fill("#FFFFFF", core)), ks=layer_transform(p=(hx, hy), s=wave(30, lambda u: [100 + 15 * math.sin(4 * math.pi * u)] * 2 + [100])))
    for k in range(6):
        a = rng.uniform(0, 360)
        ex, ey = polar(hx, hy, rng.uniform(130, 180), a)
        def make(t0, ex=ex, ey=ey):
            return [group(star(4, 9, 3), fill("#FFFFFF", core))], layer_transform(
                p=anim([(t0, [hx, hy, 0], EASE_OUT), (t0 + 12, [ex, ey + 20, 0])]), o=anim([(t0, 100), (t0 + 8, 100), (t0 + 12, 0)]))
        cyclic(s, 30, k * 5, 12, make)
    return s


def guirnalda_luces() -> Sticker:
    s = Sticker("guirnalda-luces", "Guirnalda de luces", "String lights", "celebracion", frames=40, order=91,
                tags=["luces", "navidad", "fiesta", "decoración"])
    cols = [("c1", "#FFD23F"), ("c2", "#FF4D6D"), ("c3", "#3BCEAC"), ("c4", "#5BC0FF")]
    for sid, col in cols:
        s.slot(sid, col)
    wire = s.slot("cable", "#2E7D32")
    def y_at(x):
        return 210 + 60 * math.sin(math.pi * (x - 20) / 236) ** 2
    pts = [(x, y_at(x)) for x in range(20, 493, 24)]
    s.layer(group(path(pts, smooth=1.0), stroke("#2E7D32", 6, wire)), ks=layer_transform(p=(0, 0)))
    for k in range(8):
        x = 46 + k * 60
        y = y_at(x)
        sid, col = cols[k % 4]
        phase = (k % 4) * 10
        keys = []
        for f in range(0, 41, 5):
            on = ((f - phase) % 40) < 20
            keys.append((f, 32 if on else 0, EASE_IN_OUT))
        bulb_keys = [(f, 100 if ((f - phase) % 40) < 20 else 55, EASE_IN_OUT) for f in range(0, 41, 5)]
        s.layer(group(circle(80, 0, 42), fill(col, sid)), ks=layer_transform(p=(x, y), o=anim(keys)))
        s.layer(group(rrect(18, 18, 4, 0, 8), fill("#2E7D32", wire)), group(oval(36, 52, 0, 40), fill(col, sid)),
                ks=layer_transform(p=(x, y), o=anim(bulb_keys)))
    return s


def estrella_fugaz() -> Sticker:
    s = Sticker("estrella-fugaz", "Estrella fugaz", "Shooting star", "celebracion", frames=45, order=92, thumb=0.45,
                tags=["deseo", "magia", "noche", "estrella"])
    st = s.slot("estrella", "#FFD23F")
    tail = s.slot("estela", "#FFF4C2")
    # Travelling to the lower right; the tail points back up-left.
    trail = path([(0, -30), (-260, -140), (-270, -116), (0, 30)], closed=True, smooth=0)
    s.layer(group(star(5, 72, 32, roundness=10), fill("#FFD23F", st), tr=transform(r=anim([(0, 0, LINEAR), (45, 144)]))),
            group(trail, fill("#FFF4C2", tail, o=45)),
            group(path([(0, -14), (-190, -98), (-196, -84), (0, 14)], closed=True), fill("#FFF4C2", tail, o=85)),
            ks=layer_transform(p=anim([(0, [-80, 120, 0], LINEAR), (45, [600, 420, 0])])))
    for k in range(5):
        u = (k + 1) / 6
        x, y = -80 + 680 * u, 120 + 300 * u
        twinkle(s, x - 40, y + (20 if k % 2 else -30), 30, round(45 * u) + 2, 16, tail, "#FFFFFF", 45)
    return s


# --- Resaltar -----------------------------------------------------------------------------------


def subrayado_ondulado() -> Sticker:
    s = Sticker("subrayado-ondulado", "Subrayado ondulado", "Wavy underline", "resaltar", frames=24, order=171, loop=False,
                tags=["subrayar", "resaltar", "texto", "garabato"])
    sid = s.slot("color", "#FF4D6D")
    pts = [(-200 + k * 25, 18 * math.sin(k * math.pi / 2)) for k in range(17)]
    s.layer(group(path(pts, smooth=1.0), stroke("#FF4D6D", 16, sid), draw_on(0, 16)), ks=layer_transform(p=(C, 300)))
    return s


def recuadro_a_mano() -> Sticker:
    s = Sticker("recuadro-a-mano", "Recuadro a mano", "Hand-drawn box", "resaltar", frames=30, order=172, loop=False,
                tags=["resaltar", "marco", "garabato", "señalar"])
    sid = s.slot("color", "#FFD23F")
    pts = [(-205, -100), (-60, -112), (90, -106), (200, -114), (196, -10), (204, 108), (60, 102), (-80, 110), (-196, 104),
           (-200, 0), (-192, -118)]
    s.layer(group(path(pts, smooth=0.35), stroke("#FFD23F", 14, sid), draw_on(0, 22)), ks=layer_transform(p=(C, C), r=-2))
    return s


def tachado_garabato() -> Sticker:
    s = Sticker("tachado-garabato", "Tachado a mano", "Scribble out", "resaltar", frames=24, order=173, loop=False,
                tags=["tachar", "error", "no", "garabato"])
    sid = s.slot("color", "#EF4444")
    pts = []
    for k in range(13):
        x = -190 + k * 31
        pts.append((x, -46 if k % 2 else 46))
    s.layer(group(path(pts, smooth=0.25), stroke("#EF4444", 14, sid), draw_on(0, 16, EASE_OUT)), ks=layer_transform(p=(C, C), r=-6))
    return s


def estrella_a_mano() -> Sticker:
    s = Sticker("estrella-a-mano", "Estrella a mano", "Hand-drawn star", "resaltar", frames=36, order=174, loop=False,
                tags=["estrella", "favorito", "importante", "garabato"])
    sid = s.slot("color", "#FFD23F")
    pts = [polar(0, 10, 165 if k % 2 == 0 else 68, -90 + k * 36) for k in range(11)]
    pts[-1] = (pts[-1][0] + 14, pts[-1][1] + 10)
    s.layer(group(path(pts, smooth=0.1), stroke("#FFD23F", 14, sid), draw_on(0, 22)), ks=layer_transform(p=(C, C)))
    for x, y, sz, d in [(C + 175, C - 150, 44, 20), (C - 185, C - 120, 32, 24), (C + 160, C + 150, 30, 28)]:
        s.layer(group(sparkle4(sz), fill("#FFD23F", sid)), ks=layer_transform(p=(x, y), s=pop(d, 10)))
    return s


def exclamaciones() -> Sticker:
    s = Sticker("exclamaciones", "¡Atención!", "Exclamation marks", "resaltar", frames=40, order=175,
                tags=["atención", "importante", "alerta", "ojo"])
    sid = s.slot("color", "#FF4D6D")
    for k, (x, r, d) in enumerate([(C - 70, -12, 0), (C + 70, 10, 4)]):
        mark = [group(circle(46, 0, 105), rrect(46, 150, 23, 0, -30), fill("#FF4D6D", sid))]
        s.layer(*mark, ks=layer_transform(p=(x, C + 118), a=(0, 128), r=anim([(d, r, EASE_IN_OUT), (d + 6, r - 8, EASE_IN_OUT), (d + 12, r + 6, EASE_IN_OUT),
                                                                         (d + 18, r, EASE_IN_OUT), (40, r)]),
                                          s=scale_keys([(d, 100, EASE_OUT), (d + 6, 112, EASE_IN_OUT), (d + 16, 98, EASE_IN_OUT), (d + 22, 100), (40, 100)])))
    return s


def corchetes() -> Sticker:
    s = Sticker("corchetes", "Corchetes de enfoque", "Focus brackets", "resaltar", frames=24, order=176, loop=False,
                tags=["resaltar", "enfoque", "marco", "texto"])
    sid = s.slot("color", "#FFFFFF")
    for side in (-1, 1):
        br = path([(side * -40, -130), (0, -130), (0, 130), (side * -40, 130)])
        s.layer(group(br, stroke("#FFFFFF", 18, sid)), ks=layer_transform(
            p=anim([(0, [C + side * 30, C, 0], EASE_OUT), (12, [C + side * 184, C, 0], EASE_IN_OUT), (18, [C + side * 166, C, 0], EASE_IN_OUT),
                    (24, [C + side * 170, C, 0])]),
            o=anim([(0, 0), (4, 100)])))
    return s


def foco_luz() -> Sticker:
    s = Sticker("foco-luz", "Foco de luz", "Spotlight", "resaltar", frames=72, order=177,
                tags=["foco", "escenario", "protagonista", "presentación"])
    beam = s.slot("luz", "#FFF4C2")
    lamp = s.slot("lampara", "#2B2D42")
    shapes = [group(rrect(80, 60, 14, 0, 0), fill("#2B2D42", lamp)),
              group(path([(-26, 20), (26, 20), (150, 400), (-150, 400)], closed=True), fill("#FFF4C2", beam, o=28)),
              group(oval(320, 70, 0, 400), fill("#FFF4C2", beam, o=45))]
    s.layer(*shapes, ks=layer_transform(p=(C, 40), r=wobble(72, 14)))
    return s


def corazon_a_mano() -> Sticker:
    s = Sticker("corazon-a-mano", "Corazón a mano", "Hand-drawn heart", "resaltar", frames=36, order=178, loop=False,
                tags=["amor", "favorito", "garabato", "resaltar"])
    sid = s.slot("color", "#FF2D55")
    s.layer(group(heart_path(330, 0, 0), stroke("#FF2D55", 14, sid), draw_on(0, 22)),
            ks=layer_transform(p=(C, C), s=scale_keys([(22, 100, EASE_OUT), (27, 108, EASE_IN_OUT), (32, 98, EASE_IN_OUT), (36, 100)]), r=-6))
    return s


def mira_enfoque() -> Sticker:
    s = Sticker("mira-enfoque", "Mira de enfoque", "Target reticle", "resaltar", frames=30, order=179, loop=False,
                tags=["enfoque", "objetivo", "detalle", "zoom"])
    sid = s.slot("color", "#FF3B30")
    ticks = [line(polar(0, 0, 120, a), polar(0, 0, 170, a)) for a in (0, 90, 180, 270)]
    s.layer(group(circle(240), *ticks, stroke("#FF3B30", 12, sid)), group(circle(22), fill("#FF3B30", sid)),
            ks=layer_transform(p=(C, C), s=scale_keys([(0, 220, EASE_OUT), (14, 92, EASE_IN_OUT), (20, 104, EASE_IN_OUT), (26, 100)]),
                               r=anim([(0, -90, EASE_OUT), (16, 0)]), o=anim([(0, 0), (6, 100)])))
    return s


def ojo_mira() -> Sticker:
    s = Sticker("ojo-mira", "Ojo que mira", "Looking eye", "resaltar", frames=72, order=180,
                tags=["mira", "ojo", "atención", "detalle"])
    white = s.slot("ojo", "#FFFFFF")
    iris = s.slot("iris", "#3B82F6")
    almond = path([(-170, 0), (0, -110), (170, 0), (0, 110)], closed=True, smooth=1.15)
    look = anim([(0, [0, 0], EASE_IN_OUT), (10, [-55, 0], EASE_IN_OUT), (28, [-55, 0], EASE_IN_OUT), (38, [55, 0], EASE_IN_OUT),
                 (56, [55, 0], EASE_IN_OUT), (66, [0, 0]), (72, [0, 0])])
    pupil = group(group(circle(30, -22, -22), fill("#FFFFFF")), group(circle(60), fill("#111111")), group(circle(130), fill("#3B82F6", iris)),
                  tr=transform(p=look))
    blink = anim([(0, [100, 100, 100]), (44, [100, 100, 100], EASE_IN_OUT), (47, [100, 6, 100], EASE_IN_OUT), (51, [100, 100, 100]), (72, [100, 100, 100])])
    s.layer(pupil, group(almond, fill("#FFFFFF", white)), group(path([(-170, 0), (0, -110), (170, 0), (0, 110)], closed=True, smooth=1.15),
                                                                   stroke("#111111", 12)),
            ks=layer_transform(p=(C, C), s=blink))
    return s


def chincheta() -> Sticker:
    s = Sticker("chincheta", "Chincheta", "Push pin", "resaltar", frames=30, order=181, loop=False,
                tags=["fijar", "importante", "nota", "recordatorio"])
    head = s.slot("chincheta", "#FF3B30")
    s.layer(group(oval(90, 22), fill("#000000", o=30)), ks=layer_transform(p=(C + 30, C + 150), s=scale_keys([(0, 0, EASE_OUT), (12, 100)])))
    shapes = [group(group(circle(30, -22, -150), fill("#FFFFFF", o=55)),
                    group(circle(120, 0, -130), fill("#FF3B30", head)),
                    group(rrect(70, 40, 10, 0, -70), fill("#C81E1E")),
                    group(line((0, -50), (0, 20)), stroke("#C0C4CC", 10)), tr=transform(s=140))]
    s.layer(*shapes, ks=layer_transform(
        p=anim([(0, [C + 120, -160, 0], FALL), (12, [C + 30, C + 124, 0])]), r=anim([(0, 30, EASE_OUT), (12, 22, EASE_IN_OUT), (18, 14, EASE_IN_OUT), (24, 18)]),
        s=scale_keys([(12, [104, 92, 100], EASE_OUT), (18, [98, 103, 100], EASE_IN_OUT), (24, 100)])))
    return s


def espiral_garabato() -> Sticker:
    s = Sticker("espiral-garabato", "Espiral a mano", "Hand-drawn spiral", "resaltar", frames=30, order=182, loop=False,
                tags=["garabato", "mareo", "hipnosis", "doodle"])
    sid = s.slot("color", "#7B2FF7")
    pts = [polar(0, 0, 8 + 6.2 * k, k * 30) for k in range(33)]
    s.layer(group(path(pts, smooth=1.0), stroke("#7B2FF7", 14, sid), draw_on(0, 24)), ks=layer_transform(p=(C, C)))
    return s


# --- Flechas -------------------------------------------------------------------------------------


def flecha_bucle() -> Sticker:
    s = Sticker("flecha-bucle", "Flecha con bucle", "Loop arrow", "flechas", frames=36, order=261, loop=False,
                tags=["flecha", "señalar", "garabato", "mira"])
    sid = s.slot("color", "#FFFFFF")
    pts = [(-200, 150), (-130, 70), (-40, 30), (20, -40), (-10, -120), (-80, -100), (-60, -30), (30, -10), (120, -50), (190, -120)]
    s.layer(group(path(pts, smooth=1.0), stroke("#FFFFFF", 15, sid), draw_on(0, 24)), ks=layer_transform())
    s.layer(group(arrow_head((190, -120), (150, -80), 50, 34), stroke("#FFFFFF", 15, sid)),
            ks=layer_transform(p=(C + 190, C - 120), a=(190, -120), s=pop(22, 10)))
    return s


def flecha_doble() -> Sticker:
    s = Sticker("flecha-doble", "Flecha doble", "Double arrow", "flechas", frames=40, order=262,
                tags=["flecha", "medida", "comparar", "ancho"])
    sid = s.slot("color", "#FFD23F")
    for side in (-1, 1):
        s.layer(group(arrow_head((side * 30, 0), (side * -10, 0), 60, 40), line((side * 30, 0), (side * -200, 0)), stroke("#FFD23F", 26, sid)),
                ks=layer_transform(p=anim([(0, [C + side * 150, C, 0], EASE_IN_OUT), (20, [C + side * 190, C, 0], EASE_IN_OUT), (40, [C + side * 150, C, 0])])))
    return s


def flecha_gruesa() -> Sticker:
    s = Sticker("flecha-gruesa", "Flecha gruesa", "Bold arrow", "flechas", frames=40, order=263,
                tags=["flecha", "siguiente", "ir", "derecha"])
    sid = s.slot("color", "#FF4D6D")
    lines = s.slot("lineas", "#FFFFFF")
    shape = path([(-150, -45), (20, -45), (20, -110), (150, 0), (20, 110), (20, 45), (-150, 45)], closed=True)
    push = anim([(0, [C - 30, C, 0], EASE_IN_OUT), (8, [C - 50, C, 0], EASE_OUT), (14, [C + 10, C, 0], EASE_IN_OUT), (24, [C - 30, C, 0]), (40, [C - 30, C, 0])])
    s.layer(group(shape, fill("#FF4D6D", sid), stroke("#FF4D6D", 24, sid)), ks=layer_transform(p=push))
    for k, y in enumerate((-60, 0, 60)):
        s.layer(group(line((-50, 0), (50, 0)), stroke("#FFFFFF", 10, lines),
                      trim(anim([(10 + k, 0, EASE_OUT), (16 + k, 100)]), start=anim([(14 + k, 0, EASE_IN_OUT), (22 + k, 100)]))),
                ks=layer_transform(p=(C - 230, C + y)), ip=10, op=24)
    return s


def flechas_centro() -> Sticker:
    s = Sticker("flechas-centro", "Flechas al centro", "Arrows to centre", "flechas", frames=36, order=264,
                tags=["enfoque", "centro", "mira aquí", "atención"])
    sid = s.slot("color", "#FFFFFF")
    for a in (45, 135, 225, 315):
        far = polar(0, 0, 210, a)
        near = polar(0, 0, 120, a)
        s.layer(group(line((far[0], far[1]), (near[0], near[1])), arrow_head(near, far, 46, 38), stroke("#FFFFFF", 18, sid)),
                ks=layer_transform(p=anim([(0, [C, C, 0], EASE_IN_OUT), (18, [C - 26 * math.cos(math.radians(a)), C - 26 * math.sin(math.radians(a)), 0], EASE_IN_OUT),
                                           (36, [C, C, 0])])))
    return s


def flecha_u() -> Sticker:
    s = Sticker("flecha-u", "Flecha en U", "U-turn arrow", "flechas", frames=32, order=265, loop=False,
                tags=["volver", "regresar", "girar", "flecha"])
    sid = s.slot("color", "#3BCEAC")
    pts = [(-120, 160), (-120, 20)] + [polar(0, 20, 120, a) for a in range(180, 361, 30)][1:] + [(120, 110)]
    s.layer(group(path(pts, smooth=0.9), stroke("#3BCEAC", 26, sid), draw_on(0, 20)), ks=layer_transform(p=(C, C - 10)))
    s.layer(group(arrow_head((120, 150), (120, 100), 60, 40), stroke("#3BCEAC", 26, sid)), ks=layer_transform(p=(C + 120, C + 140), a=(120, 150),
                                                                                                    s=pop(18, 12)))
    return s


def scroll_abajo() -> Sticker:
    s = Sticker("scroll-abajo", "Desliza hacia abajo", "Scroll down", "flechas", frames=40, order=266,
                tags=["desliza", "abajo", "scroll", "más"])
    sid = s.slot("color", "#FFFFFF")
    s.layer(group(rrect(130, 200, 65), stroke("#FFFFFF", 14, sid)), ks=layer_transform(p=(C, C - 50)))
    s.layer(group(rrect(18, 36, 9), fill("#FFFFFF", sid)),
            ks=layer_transform(p=anim([(0, [C, C - 110, 0], EASE_IN_OUT), (20, [C, C - 60, 0]), (21, [C, C - 110, 0]), (40, [C, C - 110, 0])]),
                               o=anim([(0, 100), (14, 100, EASE_OUT), (20, 0), (24, 0, EASE_OUT), (32, 100)])))
    for k in range(2):
        d = 6 + k * 6
        s.layer(group(path([(-34, -14), (0, 18), (34, -14)]), stroke("#FFFFFF", 12, sid)),
                ks=layer_transform(p=(C, C + 90 + k * 40), o=anim([(0, 25), (d, 25, EASE_OUT), (d + 8, 100, EASE_IN_OUT), (d + 20, 25), (40, 25)])))
    return s


def cursor_clic() -> Sticker:
    s = Sticker("cursor-clic", "Clic", "Click", "flechas", frames=40, order=267, thumb=0.22,
                tags=["clic", "toca", "botón", "enlace"])
    ring = s.slot("onda", "#FFD23F")
    body = s.slot("cursor", "#FFFFFF")
    tip = (C - 30, C - 40)
    for k in range(2):
        d = 6 + k * 4
        s.layer(group(circle(60), stroke("#FFD23F", 8, ring)),
                ks=layer_transform(p=tip, s=scale_keys([(d, 40, EASE_OUT), (d + 20, 300)]), o=anim([(d, 100), (d + 10, 100, IN), (d + 20, 0)])), ip=d, op=d + 20)
    for a in (-150, -110, -70):
        s.layer(group(line(polar(0, 0, 46, a), polar(0, 0, 80, a)), stroke("#FFD23F", 10, ring),
                      trim(anim([(6, 0, EASE_OUT), (12, 100)]), start=anim([(10, 0, EASE_IN_OUT), (18, 100)]))),
                ks=layer_transform(p=tip), ip=6, op=19)
    cursor = path([(0, 0), (0, 150), (38, 116), (66, 176), (92, 164), (64, 106), (112, 106)], closed=True)
    s.layer(group(cursor, stroke("#111111", 12)), group(cursor, fill("#FFFFFF", body)),
            ks=layer_transform(p=tip, s=scale_keys([(0, 100, EASE_IN_OUT), (4, 86, EASE_OUT), (9, 100), (40, 100)])))
    return s


def flecha_punteada() -> Sticker:
    s = Sticker("flecha-punteada", "Flecha punteada", "Dotted arrow", "flechas", frames=36, order=268, loop=False,
                tags=["camino", "ruta", "señalar", "flecha"])
    sid = s.slot("color", "#FFFFFF")
    pts = [(-200, 150), (-100, -40), (60, -110), (190, -60)]
    # Separate dashes (not a dashed stroke: the app's renderer drew it solid), each popping in turn.
    along = sample_curve(pts, 26)
    n = 13
    for k in range(n):
        a, b = along[2 * k], along[2 * k + 1]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        d = round(k * 20 / n)
        s.layer(group(line((a[0] - mx, a[1] - my), (b[0] - mx, b[1] - my)), stroke("#FFFFFF", 14, sid)),
                ks=layer_transform(p=(C + mx, C + my), s=scale_keys([(d, 0, EASE_OUT), (d + 5, 100)])))
    s.layer(group(arrow_head((200, -55), (150, -85), 50, 36), stroke("#FFFFFF", 14, sid)), ks=layer_transform(p=(C + 200, C - 55), a=(200, -55),
                                                                                               s=pop(20, 12)))
    return s


def flecha_ondulada() -> Sticker:
    s = Sticker("flecha-ondulada", "Flecha ondulada", "Wavy arrow", "flechas", frames=32, order=269, loop=False,
                tags=["abajo", "mira", "flecha", "garabato"])
    sid = s.slot("color", "#FFD23F")
    pts = [(40 * math.sin(k * math.pi / 2), -190 + k * 32) for k in range(11)]
    s.layer(group(path(pts, smooth=1.0), stroke("#FFD23F", 16, sid), draw_on(0, 20)), ks=layer_transform(p=(C, C - 20)))
    end = pts[-1]
    s.layer(group(arrow_head((end[0], end[1] + 10), (end[0], end[1] - 30), 55, 38), stroke("#FFD23F", 16, sid)),
            ks=layer_transform(p=(C + end[0], C - 20 + end[1] + 10), a=(end[0], end[1] + 10), s=pop(18, 12)))
    return s


def circulo_flecha() -> Sticker:
    s = Sticker("circulo-flecha", "Círculo con flecha", "Circle and arrow", "flechas", frames=40, order=270, loop=False,
                tags=["resaltar", "señalar", "aquí", "garabato"])
    sid = s.slot("color", "#FF3B30")
    ring = [polar(-40, -40, 120 + 5 * math.sin(k), -60 + k * 24) for k in range(17)]
    s.layer(group(path(ring, smooth=1.0), stroke("#FF3B30", 13, sid), draw_on(0, 18)), ks=layer_transform(p=(C, C), s=static([100, 85, 100])))
    tail = [(90, 70), (150, 140), (200, 170)]
    s.layer(group(path(tail, smooth=1.0), stroke("#FF3B30", 13, sid), draw_on(14, 12)), ks=layer_transform(p=(C, C)))
    s.layer(group(arrow_head((80, 60), (130, 120), 46, 36), stroke("#FF3B30", 13, sid)), ks=layer_transform(p=(C + 80, C + 60), a=(80, 60), s=pop(24, 10)))
    return s


def mano_senala() -> Sticker:
    s = Sticker("mano-senala", "Mano que señala", "Pointing hand", "flechas", frames=36, order=271,
                tags=["señalar", "aquí", "mira", "mano"])
    skin = s.slot("mano", "#FFFFFF")
    edge = s.slot("borde", "#111111")
    cuff = s.slot("puño", "#5BC0FF")
    parts = [rrect(130, 140, 40, -20, 10), rrect(200, 50, 25, 70, -36), rrect(84, 40, 20, 26, 6), rrect(84, 40, 20, 20, 44),
             rrect(76, 38, 19, 6, 80), rrect(70, 42, 21, -64, -54)]
    folds = [line((8, 26), (46, 26)), line((0, 64), (40, 64))]
    hand = [group(*folds, stroke("#111111", 8, edge)), group(*parts, fill("#FFFFFF", skin)), group(*parts, stroke("#111111", 22, edge)),
            group(rrect(56, 150, 12, -108, 14), fill("#5BC0FF", cuff), stroke("#111111", 11, edge))]
    s.layer(*hand, ks=layer_transform(p=anim([(0, [C - 70, C, 0], EASE_IN_OUT), (9, [C - 20, C, 0], EASE_IN_OUT), (18, [C - 70, C, 0], EASE_IN_OUT),
                                              (27, [C - 20, C, 0], EASE_IN_OUT), (36, [C - 70, C, 0])]), s=122))
    return s


STICKERS = [cono_fiesta, pastel_velas, regalo_sorpresa, gorro_fiesta, bola_disco, medalla, corona, banderines, varita_magica,
            bengala, guirnalda_luces, estrella_fugaz,
            subrayado_ondulado, recuadro_a_mano, tachado_garabato, estrella_a_mano, exclamaciones, corchetes, foco_luz,
            corazon_a_mano, mira_enfoque, ojo_mira, chincheta, espiral_garabato,
            flecha_bucle, flecha_doble, flecha_gruesa, flechas_centro, flecha_u, scroll_abajo, cursor_clic, flecha_punteada,
            flecha_ondulada, circulo_flecha, mano_senala]
