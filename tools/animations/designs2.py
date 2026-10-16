"""The second set of stickers (BRIEF.md): celebration, highlights, arrows, shapes, social, faces,
business, callouts, weather and full-screen shape transitions."""

from __future__ import annotations

import math
import random

from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, heart,
                    layer_transform, path, polar, rect, star, static, stroke, transform, trim)

C = 256
IN = ({"x": [0.7], "y": [0]}, {"x": [0.84], "y": [0]})  # ease-in, for exits


def pop(start=0, length=12, to=100):
    """0 -> 115 % -> 100 %: the entrance most of these share."""
    return anim([(start, [0, 0, 100], EASE_BACK), (start + length, [to, to, 100])])


def swing(frames, amp, cycles, start=0, decay=True):
    """Damped (or steady) rotation around 0, ending at rest."""
    keys = []
    steps = cycles * 2
    for k in range(steps + 1):
        t = start + round(k * frames / steps)
        a = amp * (1 - k / steps if decay else 1) * (1 if k % 2 else -1) if k < steps or not decay else 0
        keys.append((t, a, EASE_IN_OUT))
    return anim(keys)


# --- Celebración --------------------------------------------------------------------------------


def serpentinas() -> Sticker:
    s = Sticker("serpentinas", "Serpentinas", "Streamers", "celebracion", frames=60, order=60,
                tags=["fiesta", "cumpleaños", "celebrar"], thumb=0.6)
    colours = [("c1", "#FF4D6D"), ("c2", "#FFD23F"), ("c3", "#3BCEAC")]
    for k, (sid, colour) in enumerate(colours):
        s.slot(sid, colour)
        side = -1 if k % 2 == 0 else 1
        pts = [(side * 230, -230 + k * 30), (side * 140, -120 + k * 20), (side * 190, -20 + k * 15),
               (side * 90, 70 + k * 10), (side * 140, 170)]
        s.layer(group(path(pts, smooth=1.0), stroke(colour, 14, sid),
                      trim(anim([(k * 4, 0, EASE_OUT), (k * 4 + 24, 100)]))),
                ks=layer_transform(p=(C + side * 20 * k, C),
                                   r=anim([(k * 4 + 24, 0, EASE_IN_OUT), (42, side * 4, EASE_IN_OUT), (60, 0)])))
    return s


def trofeo() -> Sticker:
    s = Sticker("trofeo", "Trofeo", "Trophy", "celebracion", frames=60, order=70,
                tags=["logro", "ganador", "premio", "concurso"], thumb=0.7)
    gold = s.slot("color", "#FFC93C")
    shine = s.slot("brillo", "#FFFFFF")
    cup = path([(-90, -120), (90, -120), (80, -20), (40, 30), (-40, 30), (-80, -20)], closed=True, smooth=0.25)
    handles = [path([(-88, -100), (-140, -95), (-135, -40), (-80, -30)], smooth=1.0),
               path([(88, -100), (140, -95), (135, -40), (80, -30)], smooth=1.0)]
    body = group(cup, fill("#FFC93C", gold))
    s.layer(body, group(*handles, stroke("#FFC93C", 18, gold)),
            group(rect((30, 70), p=(0, 65)), fill("#FFC93C", gold)), group(rect((150, 34), p=(0, 112), r=8), fill("#FFC93C", gold)),
            ks=layer_transform(p=anim([(0, [C, -120, 0], ({"x": [0.5], "y": [0]}, {"x": [0.8], "y": [1]})), (14, [C, C + 20, 0], EASE_OUT),
                                       (20, [C, C, 0], EASE_IN_OUT), (26, [C, C + 20, 0])])))
    # The glint crosses on a loop.
    s.layer(group(rect((14, 150)), fill("#FFFFFF", shine, o=55)),
            ks=layer_transform(p=anim([(30, [C - 80, C - 60, 0], EASE_IN_OUT), (48, [C + 80, C - 60, 0])]), r=static(25)),
            ip=30, op=48)
    return s


def globos() -> Sticker:
    s = Sticker("globos", "Globos", "Balloons", "celebracion", frames=90, order=80,
                tags=["cumpleaños", "fiesta", "baby shower"], thumb=0.5)
    for k, (dx, colour, sid, delay) in enumerate([(-90, "#FF4D6D", "c1", 0), (0, "#FFD23F", "c2", 6), (95, "#3BCEAC", "c3", 12)]):
        s.slot(sid, colour)
        balloon = group(ellipse((120, 145)), fill(colour, sid))
        knot = group(path([(-8, 78), (8, 78), (0, 66)], closed=True), fill(colour, sid))
        string = group(path([(0, 80), (12, 130), (-8, 180), (6, 230)], smooth=1.0), stroke("#FFFFFF", 4))
        s.layer(balloon, knot, string,
                ks=layer_transform(p=anim([(delay, [C + dx, 620, 0], EASE_OUT), (delay + 30, [C + dx, 200 + k * 25, 0], EASE_IN_OUT),
                                           (delay + 60, [C + dx, 190 + k * 25, 0], EASE_IN_OUT), (90, [C + dx, 200 + k * 25, 0])]),
                                   r=anim([(delay, 0, EASE_IN_OUT), (delay + 30, 4 * (1 if k % 2 else -1), EASE_IN_OUT),
                                           (delay + 60, -4 * (1 if k % 2 else -1), EASE_IN_OUT), (90, 0)])))
    return s


# --- Resaltar -----------------------------------------------------------------------------------


def resaltador() -> Sticker:
    s = Sticker("resaltador", "Resaltador", "Highlighter", "resaltar", frames=24, order=160,
                tags=["resaltar", "texto", "estudiar"], loop=False)
    sid = s.slot("color", "#FFE94D")
    s.layer(group(rect((420, 90), r=10), fill("#FFE94D", sid, o=70)),
            ks=layer_transform(p=(C - 210, C), s=anim([(0, [0, 100, 100], EASE_OUT), (12, [100, 100, 100])]), a=(-210, 0)))
    return s


def lupa() -> Sticker:
    s = Sticker("lupa", "Lupa", "Magnifier", "resaltar", frames=60, order=170,
                tags=["buscar", "zoom", "detalle", "reseña"], thumb=0.6)
    line = s.slot("color", "#FFFFFF")
    glass = s.slot("cristal", "#9AD7FF")
    s.layer(group(ellipse((170, 170)), stroke("#FFFFFF", 20, line)), group(ellipse((170, 170)), fill("#9AD7FF", glass, o=35)),
            group(path([(62, 62), (140, 140)]), stroke("#FFFFFF", 30, line)),
            ks=layer_transform(p=anim([(0, [-80, 420, 0], EASE_OUT), (16, [C - 20, C - 20, 0], EASE_IN_OUT),
                                       (38, [C - 5, C - 30, 0], EASE_IN_OUT), (60, [C - 20, C - 20, 0])]),
                               r=anim([(0, -30, EASE_OUT), (16, 0, EASE_IN_OUT), (38, 6, EASE_IN_OUT), (60, 0)])))
    return s


# --- Flechas -------------------------------------------------------------------------------------


def flecha_zigzag() -> Sticker:
    s = Sticker("flecha-zigzag", "Flecha en zigzag", "Zigzag arrow", "flechas", frames=30, order=240,
                tags=["flecha", "señalar", "garabato"], loop=False)
    sid = s.slot("color", "#FFFFFF")
    zig = path([(-190, 120), (-110, 20), (-40, 90), (40, -10), (110, 50), (180, -90)])
    s.layer(group(zig, stroke("#FFFFFF", 16, sid), trim(anim([(0, 0, EASE_IN_OUT), (18, 100)]))), ks=layer_transform())
    s.layer(group(path([(120, -95), (180, -90), (170, -30)]), stroke("#FFFFFF", 16, sid)),
            ks=layer_transform(p=(C, C), s=pop(16, 8)))
    return s


def toca_aqui() -> Sticker:
    s = Sticker("toca-aqui", "Toca aquí", "Tap here", "flechas", frames=36, order=250,
                tags=["toca", "clic", "enlace", "botón"])
    ring = s.slot("color", "#FFFFFF")
    s.layer(group(ellipse((70, 70)), fill("#FFFFFF", ring)),
            ks=layer_transform(p=(C, C), s=anim([(0, [100, 100, 100], EASE_IN_OUT), (6, [80, 80, 100], EASE_OUT), (14, [100, 100, 100])])))
    for k in range(2):
        d = 6 + k * 8
        s.layer(group(ellipse((70, 70)), stroke("#FFFFFF", 8, ring)),
                ks=layer_transform(p=(C, C), s=anim([(d, [100, 100, 100], EASE_OUT), (d + 22, [380, 380, 100])]),
                                   o=anim([(d, 100, LINEAR), (d + 22, 0)])), ip=d, op=min(36, d + 22))
    return s


def flecha_circular() -> Sticker:
    s = Sticker("flecha-circular", "Flecha circular", "Circular arrow", "flechas", frames=45, order=260,
                tags=["repetir", "actualizar", "antes y después"])
    sid = s.slot("color", "#FFFFFF")
    arc = [polar(0, 0, 140, a) for a in range(-60, 241, 20)]
    head_at = polar(0, 0, 140, 240)
    s.layer(group(path(arc, smooth=1.0), stroke("#FFFFFF", 22, sid)),
            group(path([(head_at[0] - 40, head_at[1] - 30), head_at, (head_at[0] + 30, head_at[1] - 40)]), stroke("#FFFFFF", 22, sid)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (45, 360)])))
    return s


# --- Formas --------------------------------------------------------------------------------------


def mancha() -> Sticker:
    s = Sticker("mancha", "Mancha orgánica", "Organic blob", "formas", frames=120, order=340,
                tags=["fondo", "forma", "líquido"])
    sid = s.slot("color", "#7B2FF7")
    shapes = []
    for seed in (1, 2, 3):
        rng = random.Random(seed)
        shapes.append([list(polar(0, 0, 170 + rng.uniform(-30, 30), k * 45)) for k in range(8)])

    def blob(points):
        n = len(points)
        ins, outs = [], []
        for i in range(n):
            px, py = points[i - 1]
            nx, ny = points[(i + 1) % n]
            tx, ty = (nx - px) / 6 * 1.2, (ny - py) / 6 * 1.2
            ins.append([-tx, -ty])
            outs.append([tx, ty])
        return {"c": True, "v": points, "i": ins, "o": outs}

    morph = {"a": 1, "k": []}
    frames = [0, 40, 80, 120]
    for t, pts in zip(frames, shapes + [shapes[0]]):
        key = {"t": t, "s": [blob(pts)]}
        if t != frames[-1]:
            key["o"] = {"x": [0.65], "y": [0]}
            key["i"] = {"x": [0.35], "y": [1]}
        morph["k"].append(key)
    s.layer(group({"ty": "sh", "ks": morph}, fill("#7B2FF7", sid)), ks=layer_transform(p=(C, C)))
    return s


def estallido_comic() -> Sticker:
    s = Sticker("estallido-comic", "Estallido cómic", "Comic burst", "formas", frames=40, order=350,
                tags=["pow", "wow", "oferta", "cómic"])
    main = s.slot("color", "#FFD23F")
    edge = s.slot("borde", "#111111")
    burst = star(16, 210, 150)
    s.layer(group(star(16, 210, 150), stroke("#111111", 14, edge)), group(burst, fill("#FFD23F", main)),
            ks=layer_transform(p=(C, C), s=anim([(0, [0, 0, 100], EASE_BACK), (12, [100, 100, 100], EASE_IN_OUT),
                                                 (26, [104, 104, 100], EASE_IN_OUT), (40, [100, 100, 100])]),
                               r=anim([(0, -20, EASE_OUT), (12, 0)])))
    return s


def salpicadura() -> Sticker:
    s = Sticker("salpicadura", "Salpicadura", "Splash", "formas", frames=24, order=360,
                tags=["pintura", "forma", "gota"], loop=False)
    sid = s.slot("color", "#FF4D6D")
    rng = random.Random(12)
    s.layer(group(ellipse((170, 160)), fill("#FF4D6D", sid)), ks=layer_transform(p=(C, C), s=pop(0, 10)))
    for k in range(7):
        a = k * 51 + rng.uniform(-10, 10)
        d = rng.uniform(150, 215)
        size = rng.uniform(26, 56)
        x, y = polar(C, C, d, a)
        s.layer(group(ellipse((size, size)), fill("#FF4D6D", sid)),
                ks=layer_transform(p=anim([(2, [C, C, 0], EASE_OUT), (14, [x, y, 0])]), s=pop(2, 10)))
    return s


def rayos_fondo() -> Sticker:
    s = Sticker("rayos-fondo", "Rayos giratorios", "Spinning rays", "formas", frames=180, order=370,
                tags=["fondo", "oferta", "retro", "producto"])
    a = s.slot("color", "#FFC93C")
    rays = []
    for k in range(12):
        p0 = (0, 0)
        p1 = polar(0, 0, 380, k * 30 - 7)
        p2 = polar(0, 0, 380, k * 30 + 7)
        rays.append(path([p0, p1, p2], closed=True))
    s.layer(group(*rays, fill("#FFC93C", a)), ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (180, 60)])))
    return s


# --- Redes -------------------------------------------------------------------------------------


def comentar() -> Sticker:
    s = Sticker("comentar", "Comentar", "Comment", "redes", frames=40, order=430,
                tags=["comentario", "chat", "redes", "mensaje"], thumb=0.6)
    bubble = s.slot("burbuja", "#FFFFFF")
    dots = s.slot("puntos", "#3B82F6")
    s.layer(group(rect((300, 200), r=60), fill("#FFFFFF", bubble)),
            group(path([(-60, 95), (-20, 95), (-80, 150)], closed=True), fill("#FFFFFF", bubble)),
            ks=layer_transform(p=(C, C - 20), s=pop(0, 12)))
    for k in range(3):
        d = 12 + k * 4
        s.layer(group(ellipse((34, 34)), fill("#3B82F6", dots)),
                ks=layer_transform(p=anim([(d, [C - 70 + k * 70, C - 20, 0], EASE_IN_OUT), (d + 7, [C - 70 + k * 70, C - 42, 0], EASE_IN_OUT),
                                           (d + 14, [C - 70 + k * 70, C - 20, 0])]), s=pop(d - 4, 6)))
    return s


def compartir() -> Sticker:
    s = Sticker("compartir", "Compartir", "Share", "redes", frames=40, order=440,
                tags=["compartir", "enviar", "redes"])
    sid = s.slot("color", "#FFFFFF")
    arrow = path([(-120, 90), (-110, -10), (-30, -70), (60, -80)], smooth=1.0)
    head = path([(20, -140), (110, -80), (20, -20)], closed=True)
    s.layer(group(arrow, stroke("#FFFFFF", 30, sid)), group(head, fill("#FFFFFF", sid)),
            ks=layer_transform(p=anim([(0, [C, C, 0], EASE_IN_OUT), (14, [C + 30, C - 15, 0], EASE_BACK), (24, [C, C, 0]), (40, [C, C, 0])])))
    return s


def boton_seguir() -> Sticker:
    s = Sticker("boton-seguir", "Botón Seguir", "Follow button", "redes", frames=60, order=450,
                tags=["seguir", "suscribirse", "redes", "llamada a la acción"], loop=False, thumb=0.4)
    on = s.slot("boton", "#FF2D55")
    done = s.slot("hecho", "#4B5563")
    check = s.slot("marca", "#FFFFFF")
    btn = (360, 120)
    s.layer(group(rect(btn, r=60), fill("#FF2D55", on)),
            ks=layer_transform(p=(C, C), s=anim([(0, [0, 0, 100], EASE_BACK), (12, [100, 100, 100], EASE_OUT), (28, [100, 100, 100], EASE_IN_OUT),
                                                 (31, [94, 94, 100], EASE_OUT), (36, [100, 100, 100])]),
                               o=anim([(0, 100), (33, 100, EASE_OUT), (38, 0)])), op=40)
    s.layer(group(rect(btn, r=60), fill("#4B5563", done)), ks=layer_transform(p=(C, C)), ip=34)
    s.layer(group(path([(-30, 0), (-8, 22), (32, -20)]), stroke("#FFFFFF", 16, check), trim(anim([(36, 0, EASE_OUT), (46, 100)]))),
            ks=layer_transform(p=(C, C)), ip=36)
    # A cursor comes in and clicks.
    cursor = path([(0, 0), (0, 70), (18, 54), (32, 84), (44, 78), (30, 50), (54, 50)], closed=True)
    s.layer(group(cursor, fill("#FFFFFF"), stroke("#111111", 4)),
            ks=layer_transform(p=anim([(10, [420, 420, 0], EASE_OUT), (26, [C + 40, C + 10, 0], EASE_IN_OUT), (30, [C + 40, C + 16, 0]),
                                       (36, [C + 40, C + 10, 0]), (50, [C + 60, C + 40, 0])]),
                               o=anim([(10, 0), (16, 100), (48, 100), (56, 0)])), ip=10)
    return s


def guardar() -> Sticker:
    s = Sticker("guardar", "Guardar", "Save", "redes", frames=30, order=460,
                tags=["guardar", "marcador", "redes"], loop=False)
    edge = s.slot("borde", "#FFFFFF")
    inner = s.slot("relleno", "#FFD23F")
    mark = path([(-80, -120), (80, -120), (80, 130), (0, 70), (-80, 130)], closed=True)
    s.layer(group(mark, fill("#FFD23F", inner)),
            ks=layer_transform(p=(C, C + 130), a=(0, 130), s=anim([(4, [100, 0, 100], EASE_BACK), (18, [100, 100, 100])])))
    s.layer(group(path([(-80, -120), (80, -120), (80, 130), (0, 70), (-80, 130)], closed=True), stroke("#FFFFFF", 18, edge)),
            ks=layer_transform(p=(C, C), s=anim([(18, [100, 100, 100], EASE_OUT), (22, [112, 112, 100], EASE_IN_OUT), (28, [100, 100, 100])])))
    return s


# --- Emociones ---------------------------------------------------------------------------------


def face(s: Sticker, colour="#FFC93C"):
    sid = s.slot("cara", colour)
    return group(ellipse((300, 300)), fill(colour, sid), name="cara")


def risa() -> Sticker:
    s = Sticker("cara-risa", "Risa", "Laughing face", "emociones", frames=30, order=500,
                tags=["risa", "jaja", "gracioso", "emoji"])
    line = s.slot("trazo", "#4A2B0F")
    tear = s.slot("lagrima", "#5BC0FF")
    eyes = [group(path([(-75, -40), (-45, -60), (-15, -40)], smooth=1.0), stroke("#4A2B0F", 16, line)),
            group(path([(15, -40), (45, -60), (75, -40)], smooth=1.0), stroke("#4A2B0F", 16, line))]
    mouth = group(path([(-90, 20), (90, 20), (60, 90), (0, 110), (-60, 90)], closed=True, smooth=0.5), fill("#4A2B0F", line))
    s.layer(*eyes, mouth, face(s), ks=layer_transform(p=(C, C), r=anim([(0, -4, EASE_IN_OUT), (5, 4, EASE_IN_OUT), (10, -4, EASE_IN_OUT),
                                                                       (15, 4, EASE_IN_OUT), (20, -4, EASE_IN_OUT), (30, -4)])))
    for side in (-1, 1):
        s.layer(group(path([(0, -20), (16, 8), (0, 22), (-16, 8)], closed=True, smooth=0.8), fill("#5BC0FF", tear)),
                ks=layer_transform(p=anim([(0, [C + side * 120, C - 30, 0], ({"x": [0.5], "y": [0]}, {"x": [0.8], "y": [1]})),
                                           (30, [C + side * 140, C + 120, 0])]),
                                   o=anim([(0, 100), (22, 100), (30, 0)])))
    return s


def enamorada() -> Sticker:
    s = Sticker("cara-enamorada", "Enamorada", "In love", "emociones", frames=48, order=510,
                tags=["amor", "me encanta", "emoji"])
    line = s.slot("trazo", "#4A2B0F")
    red = s.slot("corazones", "#FF2D55")
    s.layer(group(path([(-60, 50), (0, 85), (60, 50)], smooth=1.0), stroke("#4A2B0F", 16, line)), face(s),
            ks=layer_transform(p=(C, C)))
    for side in (-1, 1):
        s.layer(heart("#FF2D55", red, 85), ks=layer_transform(p=(C + side * 60, C - 30),
                s=anim([(0, [100, 100, 100], EASE_IN_OUT), (12, [125, 125, 100], EASE_IN_OUT), (24, [100, 100, 100], EASE_IN_OUT),
                        (36, [125, 125, 100], EASE_IN_OUT), (48, [100, 100, 100])])))
    for k in range(3):
        d = k * 14
        s.layer(heart("#FF2D55", red, 40), ks=layer_transform(
            p=anim([(d, [C + 110 + k * 15, C - 120, 0], EASE_OUT), (d + 30, [C + 140 + k * 15, C - 230, 0])]),
            o=anim([(d, 100), (d + 30, 0)])), ip=d, op=min(48, d + 30))
    return s


def sorpresa() -> Sticker:
    s = Sticker("cara-sorpresa", "Sorpresa", "Surprised face", "emociones", frames=40, order=520,
                tags=["wow", "sorpresa", "omg", "emoji"])
    line = s.slot("trazo", "#4A2B0F")
    s.layer(group(ellipse((38, 52), p=(-55, -40)), fill("#4A2B0F", line)), group(ellipse((38, 52), p=(55, -40)), fill("#4A2B0F", line)),
            group(ellipse((70, 90), p=(0, 70)), fill("#4A2B0F", line)), face(s),
            ks=layer_transform(p=anim([(0, [C, C, 0], EASE_OUT), (6, [C, C - 30, 0], EASE_IN_OUT), (14, [C, C, 0]), (40, [C, C, 0])]),
                               s=anim([(0, [100, 100, 100], EASE_OUT), (6, [94, 108, 100], EASE_IN_OUT), (14, [104, 96, 100], EASE_IN_OUT),
                                       (20, [100, 100, 100])])))
    return s


def pensando() -> Sticker:
    s = Sticker("cara-pensando", "Pensando", "Thinking", "emociones", frames=60, order=530,
                tags=["pensar", "duda", "pregunta", "emoji"])
    line = s.slot("trazo", "#4A2B0F")
    dots = s.slot("puntos", "#FFFFFF")
    s.layer(group(ellipse((32, 40), p=(-55, -30)), fill("#4A2B0F", line)), group(ellipse((32, 40), p=(55, -40)), fill("#4A2B0F", line)),
            group(path([(-40, 70), (50, 55)]), stroke("#4A2B0F", 16, line)), face(s), ks=layer_transform(p=(C + 20, C + 40), s=static([80, 80, 100])))
    for k in range(3):
        d = k * 8
        s.layer(group(ellipse((24 + k * 12, 24 + k * 12)), fill("#FFFFFF", dots)),
                ks=layer_transform(p=(C - 60 + k * 50, 110 - k * 25), s=anim([(d, [0, 0, 100], EASE_BACK), (d + 10, [100, 100, 100]), (50, [100, 100, 100], IN),
                                                                              (58, [0, 0, 100])])))
    return s


def fuego() -> Sticker:
    s = Sticker("fuego", "Fuego", "Fire", "emociones", frames=27, order=540,
                tags=["fuego", "tendencia", "hot", "emoji"])
    outer = s.slot("exterior", "#FF6B1A")
    inner = s.slot("interior", "#FFD23F")
    flames = [[(0, -170), (60, -60), (110, 20), (80, 120), (0, 150), (-80, 120), (-110, 20), (-50, -40)],
              [(10, -180), (70, -70), (105, 25), (85, 115), (0, 150), (-85, 115), (-100, 30), (-60, -50)],
              [(-10, -165), (55, -55), (115, 15), (75, 125), (0, 150), (-75, 125), (-115, 15), (-45, -60)]]

    def shape(points, sc):
        n = len(points)
        ins, outs = [], []
        pts = [[x * sc, y * sc] for x, y in points]
        for i in range(n):
            px, py = pts[i - 1]
            nx, ny = pts[(i + 1) % n]
            tx, ty = (nx - px) / 6, (ny - py) / 6
            ins.append([-tx, -ty])
            outs.append([tx, ty])
        return {"c": True, "v": pts, "i": ins, "o": outs}

    for sc, colour, sid in ((1.0, "#FF6B1A", outer), (0.6, "#FFD23F", inner)):
        morph = {"a": 1, "k": []}
        for t, pts in zip([0, 9, 18, 27], flames + [flames[0]]):
            key = {"t": t, "s": [shape(pts, sc)]}
            if t != 27:
                key["o"] = {"x": [0.5], "y": [0]}
                key["i"] = {"x": [0.5], "y": [1]}
            morph["k"].append(key)
        s.layer(group({"ty": "sh", "ks": morph}, fill(colour, sid)), ks=layer_transform(p=(C, C + (30 if sc < 1 else 0))))
    return s


def cien() -> Sticker:
    s = Sticker("perfecto", "¡Perfecto!", "Perfect", "emociones", frames=30, order=550,
                tags=["perfecto", "100", "aprobado"], loop=False)
    badge = s.slot("insignia", "#FF2D55")
    mark = s.slot("marca", "#FFFFFF")
    s.layer(group(star(12, 150, 128), fill("#FF2D55", badge)), ks=layer_transform(p=(C, C), s=pop(0, 12), r=anim([(0, -30, EASE_OUT), (12, 0)])))
    for k, dx in enumerate((-30, 30)):
        s.layer(group(path([(-45, 0), (-15, 30), (45, -35)]), stroke("#FFFFFF", 20, mark), trim(anim([(10 + k * 5, 0, EASE_OUT), (20 + k * 5, 100)]))),
                ks=layer_transform(p=(C + dx, C + 5)))
    return s


# --- Negocios ----------------------------------------------------------------------------------


def etiqueta_precio() -> Sticker:
    s = Sticker("etiqueta-precio", "Etiqueta de precio", "Price tag", "negocios", frames=50, order=600,
                tags=["precio", "oferta", "venta", "tienda"], thumb=0.9)
    tag = s.slot("etiqueta", "#FFD23F")
    thread = s.slot("hilo", "#FFFFFF")
    # The hole is the origin, so the tag hangs from it; the thread runs up to the pivot.
    shape = path([(20, -60), (170, -60), (240, 0), (170, 60), (20, 60), (-30, 0)], closed=True)
    s.layer(group(ellipse((26, 26)), fill("#1d1f27")), group(path([(0, 0), (0, -190)]), stroke("#FFFFFF", 5, thread)),
            group(shape, fill("#FFD23F", tag), tr=transform(p=(0, 0), r=90, a=(0, 0))),
            ks=layer_transform(p=anim([(0, [C, -260, 0], EASE_OUT), (12, [C, 60, 0])]), a=(0, -190),
                               r=swing(38, 14, 3, start=12)), name="etiqueta")
    return s


def oferta() -> Sticker:
    s = Sticker("sello-oferta", "Sello de oferta", "Sale badge", "negocios", frames=60, order=610,
                tags=["oferta", "descuento", "venta", "promo"])
    a = s.slot("color", "#E10600")
    b = s.slot("anillo", "#FFFFFF")
    s.layer(group(ellipse((240, 240)), stroke("#FFFFFF", 8, b)), group(star(20, 180, 155), fill("#E10600", a)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (60, 16)]),
                               s=anim([(0, [100, 100, 100], EASE_IN_OUT), (30, [106, 106, 100], EASE_IN_OUT), (60, [100, 100, 100])])))
    return s


def bolsa() -> Sticker:
    s = Sticker("bolsa-compras", "Bolsa de compras", "Shopping bag", "negocios", frames=45, order=620,
                tags=["compras", "tienda", "pedido"])
    body = s.slot("bolsa", "#FF4D6D")
    handle = s.slot("asas", "#FFFFFF")
    s.layer(group(rect((230, 220), p=(0, 40), r=24), fill("#FF4D6D", body)),
            ks=layer_transform(p=anim([(0, [C, C, 0], EASE_OUT), (8, [C, C - 30, 0], EASE_IN_OUT), (16, [C, C, 0]), (45, [C, C, 0])])))
    s.layer(group(path([(-60, -60), (-60, -110), (60, -110), (60, -60)], smooth=0.6), stroke("#FFFFFF", 16, handle)),
            ks=layer_transform(p=anim([(2, [C, C, 0], EASE_OUT), (10, [C, C - 30, 0], EASE_IN_OUT), (18, [C, C, 0]), (45, [C, C, 0])]),
                               a=(0, -60), r=swing(24, 10, 2, start=12)))
    return s


def carrito() -> Sticker:
    s = Sticker("carrito", "Carrito", "Cart", "negocios", frames=40, order=630,
                tags=["comprar", "tienda", "carrito"], loop=False)
    sid = s.slot("color", "#FFFFFF")
    cart = path([(-170, -110), (-120, -110), (-80, 50), (110, 50), (140, -60), (-100, -60)])
    s.layer(group(cart, stroke("#FFFFFF", 18, sid)), group(ellipse((44, 44), p=(-60, 100)), fill("#FFFFFF", sid)),
            group(ellipse((44, 44), p=(90, 100)), fill("#FFFFFF", sid)),
            ks=layer_transform(p=anim([(0, [-220, C, 0], EASE_OUT), (18, [C + 15, C, 0], EASE_IN_OUT), (26, [C, C, 0])]),
                               r=anim([(0, 0, EASE_OUT), (18, 6, EASE_IN_OUT), (26, 0)])))
    return s


def valoracion() -> Sticker:
    s = Sticker("estrellas-valoracion", "Valoración de 5 estrellas", "5-star rating", "negocios", frames=40, order=640,
                tags=["reseña", "valoración", "cliente", "estrellas"], loop=False)
    on = s.slot("llena", "#FFC93C")
    off = s.slot("vacia", "#4B5563")
    for k in range(5):
        x = C - 192 + k * 96
        s.layer(group(star(5, 44, 20, roundness=6), fill("#4B5563", off)), ks=layer_transform(p=(x, C)))
        s.layer(group(star(5, 44, 20, roundness=6), fill("#FFC93C", on)),
                ks=layer_transform(p=(x, C), s=anim([(4 + k * 4, [0, 0, 100], EASE_BACK), (14 + k * 4, [100, 100, 100])])))
    return s


def pin() -> Sticker:
    s = Sticker("ubicacion", "Ubicación", "Location pin", "negocios", frames=50, order=650,
                tags=["ubicación", "mapa", "dirección", "visítanos"])
    sid = s.slot("color", "#FF2D55")
    hole = s.slot("centro", "#FFFFFF")
    s.layer(group(ellipse((120, 34)), fill("#000000", o=35)), ks=layer_transform(p=(C, C + 170), s=anim([(0, [0, 0, 100], EASE_OUT), (16, [100, 100, 100])])))
    pin_shape = path([(0, 150), (-95, 10), (-100, -70), (-60, -125), (0, -145), (60, -125), (100, -70), (95, 10)], closed=True, smooth=0.75)
    s.layer(group(ellipse((80, 80), p=(0, -55)), fill("#FFFFFF", hole)), group(pin_shape, fill("#FF2D55", sid)),
            ks=layer_transform(p=anim([(0, [C, -180, 0], ({"x": [0.5], "y": [0]}, {"x": [0.8], "y": [1]})), (12, [C, C, 0], EASE_OUT),
                                       (18, [C, C - 40, 0], ({"x": [0.5], "y": [0]}, {"x": [0.8], "y": [1]})), (24, [C, C, 0], EASE_OUT),
                                       (28, [C, C - 12, 0], EASE_IN_OUT), (32, [C, C, 0])])))
    s.layer(group(ellipse((120, 34)), stroke("#FF2D55", 6, sid)),
            ks=layer_transform(p=(C, C + 170), s=anim([(32, [100, 100, 100], EASE_OUT), (50, [260, 260, 100])]), o=anim([(32, 100), (50, 0)])), ip=32)
    return s


def telefono() -> Sticker:
    s = Sticker("telefono", "Llamada", "Phone call", "negocios", frames=45, order=660,
                tags=["llamar", "contacto", "escríbenos", "pedidos"])
    sid = s.slot("color", "#22C55E")
    handset = path([(-80, -110), (-40, -120), (-20, -60), (-50, -35), (0, 40), (40, 70), (65, 40), (120, 70), (110, 115),
                    (60, 125), (-40, 60), (-110, -50)], closed=True, smooth=0.5)
    s.layer(group(handset, fill("#22C55E", sid)),
            ks=layer_transform(p=(C - 30, C + 20), r=anim([(0, 0, EASE_IN_OUT), (3, 10, EASE_IN_OUT), (6, -10, EASE_IN_OUT), (9, 10, EASE_IN_OUT),
                                                           (12, -10, EASE_IN_OUT), (15, 0), (45, 0)])))
    for k in range(2):
        arc = [polar(0, 0, 70 + k * 45, a) for a in range(-80, 1, 20)]
        s.layer(group(path(arc, smooth=1.0), stroke("#22C55E", 14, sid)),
                ks=layer_transform(p=(C + 20, C - 60), o=anim([(k * 6, 0, EASE_OUT), (k * 6 + 8, 100), (30, 100), (40, 0)])))
    return s


def envio() -> Sticker:
    s = Sticker("caja-envio", "Envío", "Delivery box", "negocios", frames=40, order=670,
                tags=["envío", "delivery", "pedido", "paquete"], loop=False)
    box = s.slot("caja", "#C8894A")
    tape = s.slot("cinta", "#F3D5A6")
    s.layer(group(rect((40, 170), p=(0, 40)), fill("#F3D5A6", tape)), group(rect((240, 170), p=(0, 40), r=10), fill("#C8894A", box)),
            ks=layer_transform(p=anim([(0, [C, C, 0]), (16, [C, C, 0], IN), (30, [C + 60, C, 0], EASE_OUT), (40, [C + 40, C, 0])])))
    for side in (-1, 1):
        s.layer(group(rect((120, 50)), fill("#C8894A", box)),
                ks=layer_transform(p=anim([(0, [C + side * 60, C - 70, 0]), (16, [C + side * 60, C - 70, 0], IN), (30, [C + 60 + side * 60, C - 70, 0], EASE_OUT),
                                           (40, [C + 40 + side * 60, C - 70, 0])]),
                                   a=(-side * 60, 25), r=anim([(0, side * -60, EASE_OUT), (12, 0)])))
    for k in range(3):
        s.layer(group(path([(-60, 0), (60, 0)]), stroke("#FFFFFF", 8)),
                ks=layer_transform(p=(C - 200, C - 30 + k * 50), o=anim([(18, 0), (24, 100), (34, 0)])), ip=18, op=40)
    return s


# --- Llamadas ----------------------------------------------------------------------------------


def tercio_inferior() -> Sticker:
    s = Sticker("tercio-inferior", "Barra de nombre", "Lower third", "llamadas", frames=40, order=700, size=1024, height=256,
                tags=["nombre", "título", "entrevista", "presentación"], loop=False)
    accent = s.slot("acento", "#FFD23F")
    main = s.slot("barra", "#111111")
    s.layer(group(rect((780, 130), r=8), fill("#111111", main, o=90)),
            ks=layer_transform(p=(452, 128), a=(-390, 0), s=anim([(6, [0, 100, 100], EASE_OUT), (20, [100, 100, 100])])))
    s.layer(group(rect((24, 150)), fill("#FFD23F", accent)),
            ks=layer_transform(p=(62, 128), s=anim([(0, [100, 0, 100], EASE_OUT), (9, [100, 100, 100])])))
    return s


def bocadillo() -> Sticker:
    s = Sticker("bocadillo", "Bocadillo", "Speech bubble", "llamadas", frames=24, order=710,
                tags=["diálogo", "habla", "texto", "cómic"], loop=False)
    fill_c = s.slot("relleno", "#FFFFFF")
    edge = s.slot("borde", "#111111")
    shape = path([(-180, -110), (180, -110), (180, 80), (-30, 80), (-110, 160), (-90, 80), (-180, 80)], closed=True)
    s.layer(group(path([(-180, -110), (180, -110), (180, 80), (-30, 80), (-110, 160), (-90, 80), (-180, 80)], closed=True),
                  stroke("#111111", 12, edge)), group(shape, fill("#FFFFFF", fill_c)),
            ks=layer_transform(p=(C - 100, C + 130), a=(-100, 150), s=anim([(0, [0, 0, 100], EASE_BACK), (13, [100, 100, 100])])))
    return s


def nube_pensamiento() -> Sticker:
    s = Sticker("nube-pensamiento", "Nube de pensamiento", "Thought bubble", "llamadas", frames=60, order=720,
                tags=["pensar", "idea", "texto"], thumb=0.6)
    sid = s.slot("relleno", "#FFFFFF")
    for k, (x, y, size) in enumerate([(C - 150, C + 170, 34), (C - 110, C + 120, 50)]):
        s.layer(group(ellipse((size, size)), fill("#FFFFFF", sid)), ks=layer_transform(p=(x, y), s=pop(k * 4, 8)))
    cloud = [group(ellipse((170, 150), p=(-80, 0)), fill("#FFFFFF", sid)), group(ellipse((190, 170), p=(30, -30)), fill("#FFFFFF", sid)),
             group(ellipse((160, 140), p=(110, 20)), fill("#FFFFFF", sid)), group(ellipse((260, 130), p=(10, 50)), fill("#FFFFFF", sid))]
    s.layer(*cloud, ks=layer_transform(p=anim([(10, [C + 30, C - 40, 0], EASE_IN_OUT), (35, [C + 30, C - 50, 0], EASE_IN_OUT), (60, [C + 30, C - 40, 0])]),
                                       s=pop(8, 12)))
    return s


def cinta() -> Sticker:
    s = Sticker("cinta", "Cinta", "Ribbon banner", "llamadas", frames=24, order=730, size=1024, height=320,
                tags=["título", "banner", "nuevo"], loop=False)
    main = s.slot("cinta", "#E63946")
    fold = s.slot("pliegue", "#9B1D27")
    for side in (-1, 1):
        s.layer(group(path([(0, -60), (side * 150, -60), (side * 110, 0), (side * 150, 60), (0, 60)], closed=True), fill("#9B1D27", fold)),
                ks=layer_transform(p=(512 + side * 330, 190), s=anim([(8, [0, 100, 100], EASE_OUT), (16, [100, 100, 100])]), a=(0, 0)))
    s.layer(group(rect((680, 130)), fill("#E63946", main)),
            ks=layer_transform(p=(512, 160), s=anim([(0, [0, 100, 100], EASE_OUT), (12, [100, 100, 100])])))
    return s


def llamada_linea() -> Sticker:
    s = Sticker("llamada-linea", "Llamada con línea", "Line callout", "llamadas", frames=30, order=740,
                tags=["señalar", "detalle", "producto", "etiqueta"], loop=False)
    sid = s.slot("color", "#FFFFFF")
    s.layer(group(ellipse((30, 30)), fill("#FFFFFF", sid)), ks=layer_transform(p=(110, 380), s=pop(0, 6)))
    s.layer(group(path([(110, 380), (240, 230), (430, 230)]), stroke("#FFFFFF", 8, sid), trim(anim([(4, 0, EASE_IN_OUT), (18, 100)]))),
            ks=layer_transform(p=(0, 0)))
    s.layer(group(rect((10, 70)), fill("#FFFFFF", sid)), ks=layer_transform(p=(430, 230), s=anim([(16, [100, 0, 100], EASE_OUT), (24, [100, 100, 100])])))
    return s


def polaroid() -> Sticker:
    s = Sticker("marco-polaroid", "Marco instantáneo", "Instant photo frame", "llamadas", frames=24, order=750, size=512,
                tags=["foto", "marco", "recuerdo"], loop=False)
    frame_c = s.slot("marco", "#FFFFFF")
    s.layer(group(rect((290, 290), p=(0, -35)), fill("#3a3f4f")), group(rect((330, 400), r=6), fill("#FFFFFF", frame_c)),
            ks=layer_transform(p=anim([(0, [C - 60, C + 120, 0], EASE_OUT), (14, [C, C, 0])]),
                               r=anim([(0, -14, EASE_OUT), (14, -3)]), o=anim([(0, 0), (6, 100)])))
    return s


# --- Clima -------------------------------------------------------------------------------------


def lluvia() -> Sticker:
    s = Sticker("nube-lluvia", "Nube con lluvia", "Rain cloud", "clima", frames=36, order=800,
                tags=["lluvia", "clima", "invierno"])
    cloud_c = s.slot("nube", "#E5E7EB")
    drop = s.slot("gotas", "#5BC0FF")
    cloud = [group(ellipse((150, 130), p=(-70, 0)), fill("#E5E7EB", cloud_c)), group(ellipse((170, 160), p=(20, -30)), fill("#E5E7EB", cloud_c)),
             group(ellipse((140, 120), p=(100, 15)), fill("#E5E7EB", cloud_c)), group(rect((300, 80), p=(15, 35), r=40), fill("#E5E7EB", cloud_c))]
    s.layer(*cloud, ks=layer_transform(p=anim([(0, [C, 200, 0], EASE_IN_OUT), (18, [C, 194, 0], EASE_IN_OUT), (36, [C, 200, 0])])))
    for k in range(5):
        x = C - 110 + k * 55
        d = (k * 7) % 36
        s.layer(group(path([(0, 0), (-10, 30)]), stroke("#5BC0FF", 10, drop)),
                ks=layer_transform(p=anim([(d, [x, 280, 0], LINEAR), (d + 18, [x - 20, 440, 0])]), o=anim([(d, 100), (d + 14, 100), (d + 18, 0)])),
                ip=d, op=d + 18)
    return s


def hojas() -> Sticker:
    s = Sticker("hojas", "Hojas que caen", "Falling leaves", "clima", frames=120, order=810,
                tags=["otoño", "naturaleza", "hojas"], thumb=0.4)
    colours = [("c1", "#E07A3F"), ("c2", "#F2A541"), ("c3", "#B23A48")]
    leaf = path([(0, -60), (38, -15), (30, 30), (0, 60), (-30, 30), (-38, -15)], closed=True, smooth=0.9)
    for k in range(6):
        sid, colour = colours[k % 3]
        s.slot(sid, colour)
        x = 90 + k * 70
        d = k * 15
        s.layer(group(leaf, fill(colour, sid)),
                ks=layer_transform(p=anim([(d, [x, -40, 0], EASE_IN_OUT), (d + 30, [x + 60, 150, 0], EASE_IN_OUT), (d + 60, [x - 20, 330, 0], EASE_IN_OUT),
                                           (d + 90, [x + 50, 560, 0])]),
                                   r=anim([(d, 0, EASE_IN_OUT), (d + 30, 60, EASE_IN_OUT), (d + 60, -20, EASE_IN_OUT), (d + 90, 80)])),
                ip=d, op=min(120, d + 90))
    return s


def nieve() -> Sticker:
    s = Sticker("nieve", "Nieve", "Snow", "clima", frames=150, order=820,
                tags=["navidad", "nieve", "invierno", "frío"], thumb=0.5)
    sid = s.slot("color", "#FFFFFF")
    rng = random.Random(5)
    for k in range(40):
        size = rng.choice([16, 22, 30])
        speed = {16: 150, 22: 110, 30: 80}[size]
        x = rng.uniform(20, 492)
        d = rng.randint(0, 149)
        # Starts already falling, wraps at the bottom: a seamless loop.
        y0 = -20 + (d / speed) * 552 % 552
        s.layer(group(ellipse((size, size)), fill("#FFFFFF", sid)),
                ks=layer_transform(p=anim([(0, [x, y0, 0], LINEAR), (150, [x + rng.uniform(-30, 30), y0 + 552 * 150 / speed, 0])])))
    return s


# --- Transiciones (pantalla vertical completa) -------------------------------------------------


def barrido() -> Sticker:
    s = Sticker("barrido-diagonal", "Barrido diagonal", "Diagonal wipe", "transiciones", frames=24, order=900, size=1080, height=1920,
                tags=["transición", "barrido", "cambio de escena"], loop=False, thumb=0.3)
    for k, (sid, colour) in enumerate([("c1", "#FFD23F"), ("c2", "#FF4D6D"), ("c3", "#111111")]):
        s.slot(sid, colour)
        d = k * 2
        s.layer(group(rect((1400, 2600)), fill(colour, sid)),
                ks=layer_transform(p=anim([(d, [-1400, 960, 0], EASE_IN_OUT), (d + 10, [540, 960, 0], EASE_IN_OUT), (d + 14, [540, 960, 0], EASE_IN_OUT),
                                           (d + 24, [2480, 960, 0])]), r=static(20)))
    return s


def iris() -> Sticker:
    s = Sticker("iris", "Iris", "Iris", "transiciones", frames=24, order=910, size=1080, height=1920,
                tags=["transición", "círculo", "cambio de escena"], loop=False, thumb=0.3)
    sid = s.slot("color", "#111111")
    s.layer(group(ellipse((100, 100)), fill("#111111", sid)),
            ks=layer_transform(p=(540, 960), s=anim([(0, [0, 0, 100], EASE_IN_OUT), (11, [4400, 4400, 100]), (13, [4400, 4400, 100], EASE_IN_OUT),
                                                     (24, [0, 0, 100])])))
    return s


def persiana() -> Sticker:
    s = Sticker("persiana", "Persiana", "Blinds", "transiciones", frames=24, order=920, size=1080, height=1920,
                tags=["transición", "barras", "cambio de escena"], loop=False, thumb=0.3)
    sid = s.slot("color", "#FFFFFF")
    for k in range(6):
        d = k * 1
        s.layer(group(rect((1080, 322)), fill("#FFFFFF", sid)),
                ks=layer_transform(p=(540, 160 + k * 320), s=anim([(d, [100, 0, 100], EASE_IN_OUT), (d + 9, [100, 100, 100]), (d + 12, [100, 100, 100], EASE_IN_OUT),
                                                                   (d + 20, [100, 0, 100])])))
    return s


def mancha_liquida() -> Sticker:
    s = Sticker("mancha-liquida", "Mancha líquida", "Liquid blob wipe", "transiciones", frames=28, order=930, size=1080, height=1920,
                tags=["transición", "líquido", "cambio de escena"], loop=False, thumb=0.3)
    a = s.slot("color", "#7B2FF7")
    b = s.slot("borde", "#3BCEAC")
    rng = random.Random(7)
    pts = [polar(0, 0, 100 + rng.uniform(-18, 18), k * 30) for k in range(12)]
    for k, (colour, sid, delay) in enumerate([("#3BCEAC", b, 0), ("#7B2FF7", a, 3)]):
        s.layer(group(path(pts, closed=True, smooth=1.0), fill(colour, sid)),
                ks=layer_transform(p=(540, 960), s=anim([(delay, [0, 0, 100], EASE_IN_OUT), (delay + 12, [1500, 1500, 100]), (delay + 14, [1500, 1500, 100], EASE_IN_OUT),
                                                         (min(28, delay + 25), [0, 0, 100])]),
                                   r=anim([(0, 0, LINEAR), (28, 40)])))
    return s


STICKERS = [serpentinas, trofeo, globos, resaltador, lupa, flecha_zigzag, toca_aqui, flecha_circular, mancha,
            estallido_comic, salpicadura, rayos_fondo, comentar, compartir, boton_seguir, guardar, risa, enamorada,
            sorpresa, pensando, fuego, cien, etiqueta_precio, oferta, bolsa, carrito, valoracion, pin, telefono, envio,
            tercio_inferior, bocadillo, nube_pensamiento, cinta, llamada_linea, polaroid, lluvia, hojas, nieve,
            barrido, iris, persiana, mancha_liquida]
