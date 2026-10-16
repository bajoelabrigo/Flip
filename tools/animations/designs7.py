"""Third set, part five (BRIEF.md › «Tanda de 200»): sports and everyday icons."""

from __future__ import annotations

import math
import random

from designs3 import sparkle4, twinkle
from kit import (FALL, IN, arrow_head, bob, breathe, circle, cyclic, draw_on, heart_path, line, morph, oval, pop, rrect,
                 scale_keys, swing, wave, wobble)
from lottie import (EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, Sticker, anim, ellipse, fill, group, heart, layer_transform,
                    path, polar, rect, star, static, stroke, transform, trim)

C = 256
UP = ({"x": [0.2], "y": [0.6]}, {"x": [0.4], "y": [1]})   # leaving the floor: fast, then slowing at the top


def bounce_keys(frames, floor, height, x=C):
    """A ball's bounce on a loop: up slows to the apex, down speeds into the floor."""
    half = frames // 2
    return anim([(0, [x, floor, 0], UP), (half, [x, floor - height, 0], FALL), (frames, [x, floor, 0])])


def squash(frames, at_floor=True):
    return scale_keys([(0, [112, 88, 100], EASE_OUT), (4, 100), (frames - 4, 100, IN), (frames, [112, 88, 100])])


# --- Deportes ----------------------------------------------------------------------------------


def balon_futbol() -> Sticker:
    s = Sticker("balon-futbol", "Balón de fútbol", "Soccer ball", "deportes", frames=36, order=1201, thumb=0.15,
                tags=["fútbol", "gol", "deporte", "partido"])
    white = s.slot("balon", "#FFFFFF")
    black = s.slot("parches", "#111111")
    s.layer(group(oval(160, 30), fill("#000000", o=30)), ks=layer_transform(p=(C, 452), s=wave(36, lambda u: [60 + 40 * abs(math.cos(math.pi * u)) ** 2] * 2 + [100])))
    patches = [star(5, 42, 34, p=(0, 0))] + [star(5, 26, 21, p=polar(0, 0, 100, -90 + k * 72)) for k in range(5)]
    seams = [line(polar(0, 0, 40, -90 + k * 72), polar(0, 0, 80, -90 + k * 72)) for k in range(5)] + \
            [line(polar(0, 0, 120, -54 + k * 72), polar(0, 0, 150, -54 + k * 72)) for k in range(5)]
    ball = [group(*seams, stroke("#111111", 8, black)), group(*patches, fill("#111111", black)), group(circle(300), stroke("#111111", 8, black)), group(circle(300), fill("#FFFFFF", white))]
    s.layer(group(*ball, tr=transform(r=anim([(0, 0, LINEAR), (36, 144)]))), ks=layer_transform(p=bounce_keys(36, 300, 140), s=squash(36)))
    return s


def baloncesto() -> Sticker:
    s = Sticker("baloncesto", "Baloncesto", "Basketball", "deportes", frames=30, order=1202, thumb=0.15,
                tags=["básquet", "baloncesto", "deporte", "cancha"])
    ball = s.slot("balon", "#FF8A1F")
    seam = s.slot("costuras", "#5A2A00")
    s.layer(group(oval(150, 28), fill("#000000", o=30)), ks=layer_transform(p=(C, 452), s=wave(30, lambda u: [60 + 40 * abs(math.cos(math.pi * u)) ** 2] * 2 + [100])))
    seams = [line((-150, 0), (150, 0)), line((0, -150), (0, 150)), path([(-110, -100), (-60, 0), (-110, 100)], smooth=1.0), path([(110, -100), (60, 0), (110, 100)], smooth=1.0)]
    s.layer(group(group(*seams, stroke("#5A2A00", 10, seam)), group(circle(300), fill("#FF8A1F", ball)), tr=transform(r=anim([(0, 0, LINEAR), (30, -90)]))),
            ks=layer_transform(p=bounce_keys(30, 300, 160), s=squash(30)))
    return s


def cronometro() -> Sticker:
    s = Sticker("cronometro", "Cronómetro", "Stopwatch", "deportes", frames=60, order=1203,
                tags=["tiempo", "carrera", "récord", "rápido"])
    body = s.slot("cronometro", "#FFFFFF")
    hand = s.slot("aguja", "#FF4D6D")
    ticks = [line(polar(0, 0, 105, a), polar(0, 0, 125, a)) for a in range(0, 360, 30)]
    s.layer(group(*ticks, stroke("#2B2D42", 10)), group(circle(270), fill("#FFFFFF", body)), group(circle(300), fill("#2B2D42")),
            group(rrect(60, 40, 10, 0, -170), rrect(30, 30, 0, 0, -148), fill("#2B2D42")), ks=layer_transform(p=(C, C + 30)))
    s.layer(group(rrect(50, 26, 8, 0, -196), fill("#FF4D6D", hand)),
            ks=layer_transform(p=(C, C + 30), a=(0, -196), s=anim([(0, [100, 100, 100], EASE_IN_OUT), (4, [100, 60, 100], EASE_OUT), (10, [100, 100, 100]), (60, [100, 100, 100])])))
    s.layer(group(rrect(12, 120, 6, 0, -50), fill("#FF4D6D", hand)), group(circle(30), fill("#FF4D6D", hand)),
            ks=layer_transform(p=(C, C + 30), r=anim([(k * 5, k * 30, EASE_BACK) for k in range(12)] + [(60, 360)])))
    return s


def pesas() -> Sticker:
    s = Sticker("pesas", "Pesas", "Dumbbell", "deportes", frames=40, order=1204,
                tags=["gimnasio", "fuerza", "ejercicio", "entrenamiento"])
    plate = s.slot("discos", "#FF4D6D")
    bar = s.slot("barra", "#C0C4CC")
    lift = anim([(0, [C, C + 40, 0], EASE_IN_OUT), (16, [C, C - 50, 0], EASE_IN_OUT), (22, [C, C - 44, 0], EASE_IN_OUT), (36, [C, C + 40, 0]), (40, [C, C + 40, 0])])
    s.layer(group(rrect(70, 200, 20, -150, 0), rrect(70, 200, 20, 150, 0), rrect(40, 140, 14, -200, 0), rrect(40, 140, 14, 200, 0), fill("#FF4D6D", plate)),
            group(rrect(380, 30, 15), fill("#C0C4CC", bar)), ks=layer_transform(p=lift, r=wave(40, lambda u: 3 * math.sin(2 * math.pi * 3 * u), samples=24)))
    for side in (-1, 1):
        for k in range(2):
            s.layer(group(line((0, 0), (side * 30, -20)), stroke("#FFFFFF", 10, o=80)),
                    ks=layer_transform(p=(C + side * (250 - k * 10), C - 120 + k * 40), o=anim([(0, 0), (16, 0, EASE_OUT), (20, 100), (26, 100, IN), (32, 0), (40, 0)])))
    return s


def bandera_meta() -> Sticker:
    s = Sticker("bandera-meta", "Bandera de meta", "Finish flag", "deportes", frames=40, order=1205,
                tags=["meta", "carrera", "ganador", "final"])
    a = s.slot("cuadros", "#111111")
    b = s.slot("fondo", "#FFFFFF")
    sq = 50
    darks = [rect((sq, sq), p=(-125 + sq / 2 + x * sq, -100 + sq / 2 + y * sq)) for x in range(5) for y in range(4) if (x + y) % 2 == 0]
    s.layer(group(rrect(16, 420, 8, -140, 70), fill("#C0C4CC")), ks=layer_transform(p=(C, C)))
    s.layer(group(*darks, fill("#111111", a)), group(rect((250, 200)), fill("#FFFFFF", b)),
            ks=layer_transform(p=(C - 132, C - 40), a=(-125, 0), s=wave(40, lambda u: [92 + 8 * math.sin(2 * math.pi * u), 100, 100]),
                               r=wave(40, lambda u: 6 * math.sin(2 * math.pi * u + 1.2))))
    return s


def podio() -> Sticker:
    s = Sticker("podio", "Podio", "Podium", "deportes", frames=40, order=1206, loop=False,
                tags=["ganador", "primer lugar", "competencia", "premio"])
    gold = s.slot("primero", "#FFC93C")
    silver = s.slot("segundo", "#C0C4CC")
    bronze = s.slot("tercero", "#E0A35A")
    for k, (x, h, col, sid, d) in enumerate([(-130, 150, "#C0C4CC", silver, 4), (0, 230, "#FFC93C", gold, 0), (130, 110, "#E0A35A", bronze, 8)]):
        s.layer(group(rrect(124, h, 8, 0, -h / 2), fill(col, sid)),
                ks=layer_transform(p=(C + x, C + 180), s=scale_keys([(d, [100, 0, 100], EASE_OUT), (d + 12, [100, 106, 100], EASE_IN_OUT), (d + 18, 100)])))
    s.layer(group(star(5, 50, 22, roundness=6), fill("#FFC93C", gold)), ks=layer_transform(p=(C, C - 110), s=pop(18, 14), r=anim([(18, -72, EASE_OUT), (32, 0)])))
    return s


def silbato() -> Sticker:
    s = Sticker("silbato", "Silbato", "Whistle", "deportes", frames=36, order=1207,
                tags=["árbitro", "entrenador", "deporte", "falta"])
    body = s.slot("silbato", "#5BC0FF")
    waves = s.slot("sonido", "#FFFFFF")
    s.layer(group(circle(40, -50, 10), fill("#2B6FA0")), group(circle(170, -50, 10), fill("#5BC0FF", body)), group(rrect(170, 70, 16, 40, -50), fill("#5BC0FF", body)),
            group(circle(40, -150, -40), stroke("#FFFFFF", 10, waves)),
            ks=layer_transform(p=(C - 20, C + 30), r=-12, s=scale_keys([(0, 100, EASE_IN_OUT), (4, 95, EASE_OUT), (10, 100), (18, 100, EASE_IN_OUT), (22, 95, EASE_OUT), (28, 100), (36, 100)])))
    for k, a in enumerate((-40, -20, 0)):
        s.layer(group(line(polar(0, 0, 60, a), polar(0, 0, 120, a)), stroke("#FFFFFF", 14, waves),
                      trim(anim([(2, 0, EASE_OUT), (10, 100), (20, 100), (26, 100)]), start=anim([(8, 0, EASE_IN_OUT), (18, 100)]))),
                ks=layer_transform(p=(C + 150, C - 60)), op=20)
        s.layer(group(line(polar(0, 0, 60, a), polar(0, 0, 120, a)), stroke("#FFFFFF", 14, waves),
                      trim(anim([(20, 0, EASE_OUT), (28, 100)]), start=anim([(26, 0, EASE_IN_OUT), (36, 100)]))),
                ks=layer_transform(p=(C + 150, C - 60)), ip=20)
    return s


def pulso() -> Sticker:
    s = Sticker("pulso-cardiaco", "Ritmo cardíaco", "Heartbeat", "deportes", frames=45, order=1208,
                tags=["salud", "corazón", "ejercicio", "cardio"])
    red = s.slot("corazon", "#FF2D55")
    ecg = s.slot("linea", "#22C55E")
    pts = [(-220, 0), (-90, 0), (-60, -40), (-30, 60), (0, -120), (30, 90), (60, 0), (220, 0)]
    s.layer(group(path(pts), stroke("#22C55E", 14, ecg), trim(anim([(0, 0, EASE_IN_OUT), (24, 100), (45, 100)]), start=anim([(12, 0, EASE_IN_OUT), (40, 100)]))),
            ks=layer_transform(p=(C, C + 140)))
    s.layer(heart("#FF2D55", red, 210), ks=layer_transform(p=(C, C - 60), s=scale_keys([(0, 100, EASE_IN_OUT), (8, 118, EASE_IN_OUT), (14, 100, EASE_IN_OUT), (20, 112, EASE_IN_OUT), (28, 100), (45, 100)])))
    return s


# --- Iconos ------------------------------------------------------------------------------------


def reloj() -> Sticker:
    s = Sticker("reloj", "Reloj", "Clock", "iconos", frames=90, order=1301,
                tags=["hora", "tiempo", "horario", "puntual"])
    face = s.slot("esfera", "#FFFFFF")
    rim = s.slot("borde", "#5BC0FF")
    hands = s.slot("agujas", "#2B2D42")
    ticks = [line(polar(0, 0, 118, a), polar(0, 0, 136, a)) for a in range(0, 360, 30)]
    s.layer(group(*ticks, stroke("#2B2D42", 10, hands)), group(circle(300), fill("#FFFFFF", face)), group(circle(340), fill("#5BC0FF", rim)), ks=layer_transform(p=(C, C)))
    s.layer(group(rrect(18, 90, 9, 0, -35), fill("#2B2D42", hands)), ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (90, 30)])))
    s.layer(group(rrect(12, 130, 6, 0, -55), fill("#2B2D42", hands)), ks=layer_transform(p=(C, C), r=anim([(0, 0, LINEAR), (90, 360)])))
    s.layer(group(circle(28), fill("#FF4D6D")), ks=layer_transform(p=(C, C)))
    return s


def calendario() -> Sticker:
    s = Sticker("calendario", "Calendario", "Calendar", "iconos", frames=48, order=1302,
                tags=["fecha", "evento", "agenda", "recordatorio"])
    head = s.slot("cabecera", "#FF4D6D")
    page = s.slot("hoja", "#FFFFFF")
    mark = s.slot("marca", "#FF4D6D")
    grid = [rrect(36, 30, 6, -90 + (k % 4) * 60, 10 + (k // 4) * 50) for k in range(12)]
    s.layer(group(*grid, fill("#D1D5DB")), group(rrect(300, 260, 24, 0, 40), fill("#FFFFFF", page)), group(rrect(300, 90, 24, 0, -90), rect((300, 40), p=(0, -65)), fill("#FF4D6D", head)),
            group(rrect(22, 60, 11, -80, -140), rrect(22, 60, 11, 80, -140), fill("#2B2D42")), ks=layer_transform(p=(C, C + 10)))
    s.layer(group(circle(56), stroke("#FF4D6D", 10, mark), draw_on(0, 14)), ks=layer_transform(p=(C + 30, C + 70)), op=40)
    s.layer(group(path([(-16, 0), (-4, 12), (18, -12)]), stroke("#FF4D6D", 8, mark), draw_on(10, 8, EASE_OUT)), ks=layer_transform(p=(C + 30, C + 70)), op=40)
    return s


def correo() -> Sticker:
    s = Sticker("correo", "Correo nuevo", "New mail", "iconos", frames=48, order=1303,
                tags=["correo", "mensaje", "email", "contacto"])
    env = s.slot("sobre", "#FFFFFF")
    edge = s.slot("pliegues", "#C7CBD4")
    badge = s.slot("insignia", "#FF2D55")
    s.layer(group(path([(-150, -100), (0, 20), (150, -100)]), path([(-150, 100), (-40, 0)]), path([(150, 100), (40, 0)]), stroke("#C7CBD4", 10, edge)),
            group(rrect(300, 200, 18), fill("#FFFFFF", env)),
            ks=layer_transform(p=wave(48, lambda u: [C, C + 20 + 8 * math.sin(2 * math.pi * u), 0]), r=wave(48, lambda u: 4 * math.sin(2 * math.pi * u + 0.6))))
    s.layer(group(circle(80), fill("#FF2D55", badge)),
            ks=layer_transform(p=(C + 140, C - 80), s=scale_keys([(0, 100, EASE_IN_OUT), (6, 120, EASE_IN_OUT), (12, 100), (48, 100)])))
    return s


def descargar() -> Sticker:
    s = Sticker("descargar", "Descargar", "Download", "iconos", frames=45, order=1304,
                tags=["descargar", "guardar", "bajar", "archivo"])
    sid = s.slot("color", "#FFFFFF")
    done = s.slot("progreso", "#22C55E")
    s.layer(group(path([(-130, 40), (-130, 120), (130, 120), (130, 40)]), stroke("#FFFFFF", 24, sid)), ks=layer_transform(p=(C, C + 40)))
    s.layer(group(line((0, -150), (0, 40)), arrow_head((0, 50), (0, 0), 70, 42), stroke("#FFFFFF", 24, sid)),
            ks=layer_transform(p=anim([(0, [C, C - 10, 0], EASE_IN_OUT), (14, [C, C + 20, 0], EASE_IN_OUT), (24, [C, C - 10, 0]), (45, [C, C - 10, 0])]),
                               o=anim([(0, 100), (24, 100)])))
    s.layer(group(line((-110, 0), (110, 0)), stroke("#22C55E", 16, done), trim(anim([(10, 0, EASE_IN_OUT), (34, 100), (40, 100)]))), ks=layer_transform(p=(C, C + 210)),
            op=42)
    return s


def engranajes() -> Sticker:
    s = Sticker("engranajes", "Engranajes", "Gears", "iconos", frames=90, order=1305,
                tags=["ajustes", "proceso", "trabajo", "configuración"])
    a = s.slot("grande", "#9CA3AF")
    b = s.slot("pequeno", "#FFD23F")
    def gear(r, teeth, w, sid, col):
        teeth_g = [group(rrect(w, r * 0.5, 6, 0, -r), fill(col, sid), tr=transform(r=k * 360 / teeth)) for k in range(teeth)]
        return [group(circle(r * 0.75), stroke(col, r * 0.5, sid))] + teeth_g
    s.layer(*gear(140, 10, 50, a, "#9CA3AF"), ks=layer_transform(p=(C - 50, C + 40), r=anim([(0, 0, LINEAR), (90, 36)])))
    # 10 teeth against 8: the small one turns one tooth (45°) while the big one turns one (36°).
    s.layer(*gear(80, 8, 36, b, "#FFD23F"), ks=layer_transform(p=(C + 150, C - 120), r=anim([(0, 22.5, LINEAR), (90, 22.5 - 45)])))
    return s


def candado() -> Sticker:
    s = Sticker("candado", "Candado", "Padlock", "iconos", frames=48, order=1306, loop=False,
                tags=["seguro", "privado", "desbloquear", "contraseña"])
    body = s.slot("candado", "#FFC93C")
    shackle = s.slot("arco", "#C0C4CC")
    s.layer(group(path([(-70, 0), (-70, -70), (-40, -110), (40, -110), (70, -70), (70, 0)], smooth=0.9), stroke("#C0C4CC", 34, shackle)),
            ks=layer_transform(p=anim([(0, [C, C - 10, 0]), (18, [C, C - 10, 0], EASE_OUT), (26, [C, C - 60, 0])]), a=(-70, 0),
                               r=anim([(0, 0), (26, 0, EASE_OUT), (36, -30, EASE_IN_OUT), (42, -24)])))
    s.layer(group(circle(46, 0, 30), rrect(20, 60, 10, 0, 60), fill("#8A5A00")), group(rrect(260, 220, 30, 0, 50), fill("#FFC93C", body)),
            ks=layer_transform(p=(C, C + 20), s=pop(0, 14), r=anim([(14, 0), (16, 0, EASE_IN_OUT), (18, -5, EASE_IN_OUT), (21, 5, EASE_IN_OUT), (24, 0)])))
    return s


def reloj_arena() -> Sticker:
    s = Sticker("reloj-arena", "Reloj de arena", "Hourglass", "iconos", frames=90, order=1307,
                tags=["espera", "tiempo", "cargando", "paciencia"])
    frame = s.slot("marco", "#E0A35A")
    sand = s.slot("arena", "#FFD23F")
    glass = s.slot("vidrio", "#FFFFFF")
    s.layer(group(path([(-110, -170), (110, -170), (20, 0), (110, 170), (-110, 170), (-20, 0)], closed=True), stroke("#FFFFFF", 12, glass)),
            group(rrect(280, 30, 10, 0, -180), rrect(280, 30, 10, 0, 180), fill("#E0A35A", frame)),
            ks=layer_transform(p=(C, C), r=anim([(0, 0), (70, 0, EASE_IN_OUT), (90, 180)])))
    s.layer(group(path([(-90, 0), (90, 0), (0, 140)], closed=True), fill("#FFD23F", sand)),
            ks=layer_transform(p=(C, C - 155), a=(0, 140), s=scale_keys([(0, 100, LINEAR), (66, 0)]), r=anim([(0, 0), (70, 0, EASE_IN_OUT), (90, 180)])), op=70)
    s.layer(group(path([(-95, 0), (95, 0), (0, -130)], closed=True), fill("#FFD23F", sand)),
            ks=layer_transform(p=anim([(0, [C, C + 160, 0]), (70, [C, C + 160, 0], EASE_IN_OUT), (90, [C, C - 160, 0])]), s=scale_keys([(0, 0, LINEAR), (66, 100)]),
                               r=anim([(0, 0), (70, 0, EASE_IN_OUT), (90, 180)])))
    s.layer(group(line((0, 0), (0, 150)), stroke("#FFD23F", 8, sand)), ks=layer_transform(p=(C, C)), op=66)
    return s


def advertencia() -> Sticker:
    s = Sticker("advertencia", "Advertencia", "Warning", "iconos", frames=40, order=1308,
                tags=["cuidado", "alerta", "atención", "aviso"])
    tri = s.slot("triangulo", "#FFC93C")
    mark = s.slot("signo", "#2B2D42")
    s.layer(group(circle(36, 0, 90), rrect(34, 120, 17, 0, -10), fill("#2B2D42", mark)),
            group(path([(0, -170), (190, 150), (-190, 150)], closed=True), fill("#FFC93C", tri), stroke("#FFC93C", 40, tri)),
            ks=layer_transform(p=(C, C + 10), s=scale_keys([(0, 100, EASE_IN_OUT), (6, 108, EASE_IN_OUT), (12, 100, EASE_IN_OUT), (18, 108, EASE_IN_OUT), (24, 100), (40, 100)]),
                               r=anim([(0, 0, EASE_IN_OUT), (6, -4, EASE_IN_OUT), (12, 4, EASE_IN_OUT), (18, -3, EASE_IN_OUT), (24, 0), (40, 0)])))
    return s


def bateria() -> Sticker:
    s = Sticker("bateria-carga", "Batería cargando", "Charging battery", "iconos", frames=60, order=1309,
                tags=["batería", "energía", "carga", "recargar"])
    shell = s.slot("bateria", "#FFFFFF")
    cells = s.slot("carga", "#22C55E")
    bolt = s.slot("rayo", "#FFD23F")
    s.layer(group(rrect(340, 180, 30), stroke("#FFFFFF", 18, shell)), group(rrect(30, 70, 10, 190, 0), fill("#FFFFFF", shell)), ks=layer_transform(p=(C - 10, C)))
    for k in range(4):
        on = 6 + k * 10
        s.layer(group(rrect(66, 130, 10), fill("#22C55E", cells)), ks=layer_transform(p=(C - 130 + k * 80, C),
                                                                                  o=anim([(0, 0), (on, 0, EASE_OUT), (on + 4, 100), (50, 100, IN), (56, 0), (60, 0)])))
    s.layer(group(path([(10, -60), (-30, 10), (0, 10), (-10, 60), (30, -10), (0, -10)], closed=True), fill("#FFD23F", bolt), stroke("#2B2D42", 8)),
            ks=layer_transform(p=(C - 10, C), s=breathe(60, 100, 112)))
    return s


def wifi() -> Sticker:
    s = Sticker("wifi", "Señal wifi", "Wi-Fi signal", "iconos", frames=48, order=1310,
                tags=["internet", "conexión", "señal", "online"])
    sid = s.slot("color", "#FFFFFF")
    s.layer(group(circle(46), fill("#FFFFFF", sid)), ks=layer_transform(p=(C, C + 120)))
    for k in range(3):
        r = 90 + k * 70
        on = 6 + k * 8
        s.layer(group(path([polar(0, 0, r, a) for a in range(-135, -44, 15)], smooth=1.0), stroke("#FFFFFF", 30, sid)),
                ks=layer_transform(p=(C, C + 120), o=anim([(0, 20), (on, 20, EASE_OUT), (on + 6, 100), (40, 100, IN), (46, 20), (48, 20)])))
    return s


def cuenta_regresiva() -> Sticker:
    s = Sticker("cuenta-regresiva", "Cuenta regresiva", "Countdown", "iconos", frames=90, order=1311,
                tags=["cuenta regresiva", "3 2 1", "empieza", "espera"])
    ring = s.slot("anillo", "#FF4D6D")
    dots = s.slot("puntos", "#FFFFFF")
    track = s.slot("pista", "#FFFFFF")
    s.layer(group(circle(320), stroke("#FFFFFF", 22, track, o=20)), ks=layer_transform(p=(C, C)))
    s.layer(group(circle(320), stroke("#FF4D6D", 22, ring), trim(anim([(0, 100, EASE_IN_OUT), (28, 0), (30, 100, EASE_IN_OUT), (58, 0),
                                                                       (60, 100, EASE_IN_OUT), (88, 0), (90, 100)]))),
            ks=layer_transform(p=(C, C)))
    # Three dots, then two, then one: the count without numbers. They all grow back for the next loop.
    for x, gone in ((-70, 28), (70, 58), (0, 84)):
        s.layer(group(circle(50), fill("#FFFFFF", dots)), ks=layer_transform(p=(C + x, C), s=scale_keys(
            [(0, 100), (gone - 4, 100, EASE_IN_OUT), (gone, 125, IN), (gone + 2, 0), (86, 0, EASE_OUT), (90, 100)])))
    return s


def notas_musicales() -> Sticker:
    s = Sticker("notas-musicales", "Notas musicales", "Music notes", "iconos", frames=48, order=1312,
                tags=["música", "canción", "audio", "baile"])
    a = s.slot("nota1", "#FF4D6D")
    b = s.slot("nota2", "#5BC0FF")
    single = [group(oval(70, 54, 0, 0), fill("#FF4D6D", a), tr=transform(r=-20)), group(line((30, -10), (30, -150), (80, -110)), stroke("#FF4D6D", 16, a))]
    double = [group(oval(64, 50, -60, 20), oval(64, 50, 60, 0), fill("#5BC0FF", b), tr=transform(r=-20)),
              group(line((-30, 10), (-30, -130), (88, -150), (88, -10)), stroke("#5BC0FF", 16, b))]
    s.layer(*single, ks=layer_transform(p=bob(48, C - 110, C + 60, 22), r=wobble(48, 10)))
    s.layer(*double, ks=layer_transform(p=bob(48, C + 80, C + 20, 22, 24), r=wobble(48, -10)))
    return s


STICKERS = [balon_futbol, baloncesto, cronometro, pesas, bandera_meta, podio, silbato, pulso,
            reloj, calendario, correo, descargar, engranajes, candado, reloj_arena, advertencia, bateria, wifi, cuenta_regresiva,
            notas_musicales]
