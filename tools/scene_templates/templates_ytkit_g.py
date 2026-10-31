"""Kit de YouTube, batch g (2026-10-30): «Botones de suscripción». Jorge brought a commercial promo with nine
subscribe buttons laid over videos (a channel card, a bar along the bottom with a follower count that keeps going
up, small pills with like and dislike...). These are our own takes on those kinds of pieces: the kit's palette
(no platform logo or red), our own icons, every text and the channel's picture editable, and a cursor that
clicks Subscribe, Like and the bell in turn. Section elementos; order 8200-8249.
"""

from __future__ import annotations

import math

from kit import Box, centered, circle_photo, fill, keys, label, no_stroke, photo_bg, pill, rrect, shadow, tanim, wide
from templates_ytkit_a import BELL, CURSOR, OUT, _stroke, path
from templates_ytkit_f import THUMB, SHARE

NAVY = "#0B1A2E"
TEAL = "#2EE6C8"
CORAL = "#FF5D73"
SUN = "#FFD23F"
WHITE = "#FFFFFF"
INK = "#14202E"
SOFT = "#6B7787"
GREY = "#E3E8EF"


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:elementos", "youtube", "suscríbete", "botón", "clic"] + tags, **kw)


def _hollow():
    return {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def _life(t0, dur, s0=0.0, fin=0.45, fout=0.35):
    """In with a springy pop, out by shrinking: motion keys for a piece shown from t0 for dur seconds."""
    return [(0, {"s": s0}, "back"), (fin, {}, "hold"), (dur - fout, {}, "in"), (dur, {"s": 0.0})]


class Cursor:
    """A pointer that visits points and clicks: stops = [(time, x, y)], every stop a click."""

    def __init__(self, t, t0, t1, start, stops, size=40):
        tip0 = stops[0][1:]
        m = [(0, {"dx": start[0] - tip0[0], "dy": start[1] - tip0[1]}, "out")]
        for i, (at, x, y) in enumerate(stops):
            d = {"dx": x - tip0[0], "dy": y - tip0[1]}
            m.append((at - t0 - 0.15, dict(d), "hold"))
            m.append((at - t0, dict(d, s=0.82), "out"))
            m.append((at - t0 + 0.15, dict(d), "inout"))
        last = stops[-1]
        m.append((t1 - t0, {"dx": last[1] - tip0[0] + 260, "dy": last[2] - tip0[1] + 160}))
        dur = t1 - t0
        path(t, t.track("shape", "Cursor"), WHITE, t0, dur, Box(tip0[0], tip0[1], size, size * 1.45), CURSOR,
             motion=m, layers=[shadow("#000000", 0, 5, 10, 0.45), fill(WHITE), _stroke(NAVY, 3, "inside")],
             opacity=keys([(0, 0.0), (0.2, 1.0, "hold"), (dur - 0.35, 1.0), (dur, 0.0)]))


def _ripple(t, x, y, at, d=60):
    for i, c in enumerate([TEAL, WHITE]):
        t.solid(t.track("shape", "Onda"), c, at + i * 0.08, 0.55, centered(x, y, d, d),
                [(0, {"s": 0.2}, "out"), (0.55, {"s": 2.6})], kind="ellipse",
                layers=[_hollow(), _stroke(c, 4, "inside")], opacity=keys([(0, 1.0), (0.55, 0.0)]))


def _sparks(t, x, y, at, size):
    for i in range(8):
        ang = math.radians(i * 45 + 22.5)
        far = size * 1.4
        c = [TEAL, CORAL, SUN][i % 3]
        t.solid(t.track("shape", "Chispas"), c, at + 0.05, 0.5, centered(x, y, size * 0.2, size * 0.2),
                [(0, {"s": 0.4}, "out"), (0.5, {"dx": math.cos(ang) * far, "dy": math.sin(ang) * far, "s": 0.0})],
                kind="ellipse")


def _subscribe_button(t, box, t0, click, t1, size, life_in=None, radius=None, done_bg=GREY, done_ink=SOFT):
    """«SUSCRIBIRME» in coral; at the click it squeezes and turns into a grey «SUSCRITO» with a check."""
    r = box.h / 2 if radius is None else radius
    first = life_in or [(0, {"s": 0.0}, "back"), (0.45, {}, "hold")]
    rrect(t, t.track("shape", "Botón"), CORAL, t0, click + 0.12 - t0, box, radius=r,
          motion=first + [(click - t0, {}, "out"), (click + 0.12 - t0, {"s": 0.92})])
    label(t, t.track("text", "Botón"), "SUSCRIBIRME", t0 + 0.15, click + 0.1 - t0 - 0.15, box, "Sora", size, WHITE,
          weight=800, spacing=1.5, anim_in=tanim("fade", duration=0.25), name="Botón")
    rest = t1 - click - 0.1
    rrect(t, t.track("shape", "Botón"), done_bg, click + 0.1, rest, box, radius=r,
          motion=[(0, {"s": 0.92}, "back"), (0.3, {}, "hold"), (rest - 0.35, {}, "in"), (rest, {"s": 0.0})])
    label(t, t.track("text", "Botón"), "SUSCRITO", click + 0.15, rest - 0.25, box, "Sora", size, done_ink, weight=800,
          spacing=1.5, anim_in=tanim("fade", duration=0.2), anim_out=OUT(0.2), name="Botón tras el clic")
    _ripple(t, box.x + box.w * 0.6, box.y + box.h * 0.6, click)


def _like(t, cx, cy, s, t0, click, t1, colour=INK, on=TEAL):
    """A thumb in outline; at the click it fills in, pops and sparks."""
    extra = {}
    path(t, t.track("shape", "Me gusta"), colour, t0, click - t0 + 0.05, centered(cx, cy, s, s), THUMB,
         layers=[_hollow(), _stroke(colour, 3.5)], motion=_life(t0, click - t0 + 0.05, fout=0.0)[:2], **extra)
    rest = t1 - click
    path(t, t.track("shape", "Me gusta"), on, click, rest, centered(cx, cy, s, s), THUMB, filled=True,
         motion=[(0, {"s": 0.6}, "out"), (0.12, {"s": 1.35}, "back"), (0.42, {}, "hold"), (rest - 0.35, {}, "in"),
                 (rest, {"s": 0.0})], **extra)
    _sparks(t, cx, cy, click, s)


def _bell(t, cx, cy, s, t0, click, t1, colour=INK, on=NAVY):
    """A bell in outline; at the click it fills, rings and a dot lights up on it."""
    path(t, t.track("shape", "Campana"), colour, t0, click - t0 + 0.05, centered(cx, cy, s, s * 1.08), BELL,
         layers=[_hollow(), _stroke(colour, 3.5)], motion=_life(t0, click - t0 + 0.05, fout=0.0)[:2])
    rest = t1 - click
    wob = [(0, 0, "smooth"), (0.1, 24, "smooth"), (0.2, -20, "smooth"), (0.3, 15, "smooth"), (0.4, -10, "smooth"),
           (0.5, 5, "smooth"), (0.6, 0, "hold"), (1.4, 0, "smooth"), (1.5, 14, "smooth"), (1.6, -10, "smooth"),
           (1.7, 5, "smooth"), (1.8, 0)]
    path(t, t.track("shape", "Campana"), on, click, rest, centered(cx, cy, s, s * 1.08), BELL, filled=True,
         rotation=keys(wob), motion=[(0, {}, "hold"), (rest - 0.35, {}, "in"), (rest, {"s": 0.0})])
    t.solid(t.track("shape", "Aviso"), TEAL, click + 0.15, rest - 0.15,
            centered(cx + s * 0.38, cy - s * 0.38, s * 0.34, s * 0.34),
            [(0, {"s": 0.0}, "back"), (0.3, {}, "hold"), (rest - 0.5, {}, "in"), (rest - 0.15, {"s": 0.0})],
            kind="ellipse", layers=[fill(TEAL), _stroke(WHITE, 2.5, "inside")])


# --- 1. Tarjeta del canal ------------------------------------------------------------------------------------

def tarjeta_canal():
    """A white card at the left: the channel's picture in a teal ring, the name, «SUSCRIBIRME»; once subscribed a
    row of icons (bell, like, share) grows under the button and the cursor rings the bell and likes."""
    D = 6.5
    t = _kit("boton-tarjeta-canal", "Tarjeta del canal con suscribirse", "Channel card with subscribe", D, 8200,
             ["tarjeta", "canal", "campana", "me gusta"], thumb_at=3.6)
    photo_bg(t, "h-man-02", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    card = Box(110, 330, 260, 400)
    cx = card.x + card.w / 2
    life = _life(t0, t1 - t0, s0=0.2)
    rrect(t, t.track("shape", "Tarjeta"), WHITE, t0, t1 - t0, card, radius=26, motion=life,
          layers=[shadow("#000000", 0, 14, 34, 0.35), fill(WHITE), no_stroke()])
    ring = centered(cx, card.y + 104, 150, 150)
    t.solid(t.track("shape", "Aro"), TEAL, t0 + 0.15, t1 - t0 - 0.15, ring,
            [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (t1 - t0 - 0.5, {}, "in"), (t1 - t0 - 0.15, {"s": 0.0})],
            kind="ellipse", layers=[fill(TEAL), no_stroke()])
    circle_photo(t, "h-portrait-03", t0 + 0.2, t1 - t0 - 0.2, centered(cx, card.y + 104, 134, 134),
                 [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (t1 - t0 - 0.55, {}, "in"), (t1 - t0 - 0.2, {"s": 0.0})],
                 label="Foto del canal")
    label(t, t.track("text", "Nombre"), "Tu canal", t0 + 0.35, t1 - t0 - 0.6, Box(card.x + 14, card.y + 192, card.w - 28, 44),
          "Sora", 30, INK, weight=700, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Nombre del canal")
    label(t, t.track("text", "Nombre"), "12,4 mil suscriptores", t0 + 0.45, t1 - t0 - 0.7,
          Box(card.x + 14, card.y + 234, card.w - 28, 30), "Inter", 18, SOFT, weight=500,
          anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Suscriptores")
    c_sub, c_bell, c_like = 1.7, 2.9, 3.8
    btn = centered(cx, card.y + 300, 212, 54)
    _subscribe_button(t, btn, t0 + 0.4, c_sub, t1 - 0.05, 22)
    icons_y = card.y + 362
    xs = [cx - 64, cx, cx + 64]
    _bell(t, xs[0], icons_y, 34, c_sub + 0.3, c_bell, t1 - 0.1)
    _like(t, xs[1], icons_y, 34, c_sub + 0.4, c_like, t1 - 0.1)
    path(t, t.track("shape", "Compartir"), INK, c_sub + 0.5, t1 - 0.1 - c_sub - 0.5, centered(xs[2], icons_y, 32, 32),
         SHARE, layers=[_hollow(), _stroke(INK, 3.5)], motion=_life(0, t1 - 0.1 - c_sub - 0.5))
    Cursor(t, 0.9, t1 - 0.3, (560, 820),
           [(c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_bell, xs[0] + 6, icons_y + 8),
            (c_like, xs[1] + 6, icons_y + 8)])
    return t


# --- 2. Barra del canal ---------------------------------------------------------------------------------------

def barra_canal():
    """A white bar along the bottom: picture, name, the followers counting up, like with its count, the bell and
    «SUSCRIBIRME». The cursor likes (the count goes up), subscribes and rings the bell."""
    D = 7.0
    t = _kit("boton-barra-canal", "Barra del canal con contador", "Channel bar with live counter", D, 8201,
             ["barra", "contador", "seguidores", "campana", "me gusta"], thumb_at=4.6)
    photo_bg(t, "h-food-01", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    bar = Box(0, 930, 1920, 150)
    dur = t1 - t0
    slide = [(0, {"dy": 160}, "out"), (0.5, {}, "hold"), (dur - 0.4, {}, "in"), (dur, {"dy": 160})]
    rrect(t, t.track("shape", "Barra"), WHITE, t0, dur, bar, radius=0, motion=slide,
          layers=[shadow("#000000", 0, -6, 26, 0.3), fill(WHITE), no_stroke()])
    t.solid(t.track("shape", "Barra"), TEAL, t0, dur, Box(0, 930, 1920, 6), slide)
    cy = 1005
    t.solid(t.track("shape", "Aro"), TEAL, t0 + 0.2, dur - 0.2, centered(110, cy, 118, 118),
            [(0, {"dy": 160}, "out"), (0.5, {}, "hold"), (dur - 0.6, {}, "in"), (dur - 0.2, {"dy": 160})],
            kind="ellipse")
    circle_photo(t, "h-portrait-05", t0 + 0.2, dur - 0.2, centered(110, cy, 104, 104),
                 [(0, {"dy": 160}, "out"), (0.5, {}, "hold"), (dur - 0.6, {}, "in"), (dur - 0.2, {"dy": 160})],
                 label="Foto del canal")
    fade_in, fade_out = tanim("fade", duration=0.3), OUT(0.25)
    label(t, t.track("text", "Nombre"), "El nombre de tu canal", t0 + 0.5, dur - 0.8, Box(190, cy - 46, 700, 46),
          "Sora", 32, INK, weight=700, align="left", anim_in=fade_in, anim_out=fade_out, name="Nombre del canal")
    # The followers keep counting while the bar is up (the engine's counter, editable).
    st_track = t.track("text", "Seguidores")
    from kit import text_style
    st = text_style("Inter", 26, [fill(INK)], weight=700, align="left", valign="middle", anim_in=fade_in,
                    anim_out=fade_out)
    st.update(counter=True, counterFrom=120480, counterSeconds=round(dur - 1.0, 3))
    t.text(st_track, "128.960", t0 + 0.6, dur - 0.9, Box(190, cy + 2, 116, 40), st, label="Seguidores")
    label(t, t.track("text", "Seguidores"), "seguidores", t0 + 0.6, dur - 0.9, Box(304, cy + 2, 200, 40), "Inter", 22,
          SOFT, weight=500, align="left", anim_in=fade_in, anim_out=fade_out, name="Seguidores: texto",
          editable=True)
    c_like, c_sub, c_bell = 2.0, 3.0, 4.0
    lx = 1290
    _like(t, lx, cy, 44, t0 + 0.6, c_like, t1 - 0.3)
    label(t, t.track("text", "Me gusta"), "25 mil", t0 + 0.6, c_like + 0.05 - t0 - 0.6, Box(lx + 34, cy - 22, 110, 44),
          "Inter", 26, INK, weight=700, align="left", anim_in=fade_in, anim_out=tanim("fade", duration=0.1),
          name="Me gusta antes")
    label(t, t.track("text", "Me gusta"), "25,1 mil", c_like + 0.05, t1 - 0.3 - c_like - 0.05,
          Box(lx + 34, cy - 22, 120, 44), "Inter", 26, INK, weight=700, align="left",
          anim_in=tanim("slide-up", duration=0.25), anim_out=fade_out, name="Me gusta después")
    bx = 1510
    _bell(t, bx, cy, 44, t0 + 0.6, c_bell, t1 - 0.3)
    btn = Box(1580, cy - 36, 280, 72)
    _subscribe_button(t, btn, t0 + 0.5, c_sub, t1 - 0.25, 26, life_in=[(0, {"dy": 160}, "out"), (0.5, {}, "hold")])
    Cursor(t, 1.2, t1 - 0.3, (1100, 700),
           [(c_like, lx + 8, cy + 10), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_bell, bx + 8, cy + 10)])
    return t


# --- 3. Píldora compacta ----------------------------------------------------------------------------------------

def pildora():
    """A small white pill: picture, like, dislike and «SUSCRIBIRME». It opens from the picture to the side, the
    cursor likes and subscribes, and it folds back into the picture."""
    D = 5.5
    t = _kit("boton-pildora", "Píldora con me gusta y suscribirse", "Pill with like and subscribe", D, 8202,
             ["píldora", "me gusta", "no me gusta", "compacto"], thumb_at=3.2)
    photo_bg(t, "h-city-05", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    pillb = Box(700, 860, 520, 100)
    cy = pillb.y + pillb.h / 2
    ax = pillb.x + 50
    # Opens from the picture: the pill grows to the right from a circle, and closes back.
    grow_dx = -(pillb.w - pillb.h) / 2
    sx0 = pillb.h / pillb.w
    pill(t, t.track("shape", "Píldora"), WHITE, t0 + 0.25, dur - 0.25, pillb,
         [(0, {"sx": sx0, "dx": grow_dx}, "out"), (0.55, {}, "hold"), (dur - 0.25 - 0.75, {}, "inout"),
          (dur - 0.25 - 0.3, {"sx": sx0, "dx": grow_dx})],
         layers=[shadow("#000000", 0, 12, 30, 0.35), fill(WHITE), no_stroke()],
         opacity=keys([(0, 1.0, "hold"), (dur - 0.55, 1.0), (dur - 0.25, 0.0)]))
    circle_photo(t, "h-portrait-01", t0, dur, centered(ax, cy, 78, 78), _life(t0, dur), label="Foto del canal")
    t.solid(t.track("shape", "Insignia"), CORAL, t0 + 0.3, dur - 0.6, centered(ax + 28, cy + 28, 26, 26),
            _life(0, dur - 0.6), kind="ellipse", layers=[fill(CORAL), _stroke(WHITE, 3, "inside")])
    c_like, c_sub = 1.8, 2.8
    inside_t0, inside_t1 = t0 + 0.6, t1 - 0.85
    _like(t, ax + 92, cy, 38, inside_t0, c_like, inside_t1)
    path(t, t.track("shape", "No me gusta"), INK, inside_t0 + 0.05, inside_t1 - inside_t0 - 0.05,
         centered(ax + 152, cy + 4, 38, 38), THUMB, layers=[_hollow(), _stroke(INK, 3.5)],
         rotation=keys([(0, 180.0)]), motion=_life(0, inside_t1 - inside_t0 - 0.05))
    btn = Box(pillb.x + pillb.w - 260, cy - 30, 240, 60)
    _subscribe_button(t, btn, inside_t0, c_sub, inside_t1 + 0.1, 21)
    Cursor(t, 1.0, t1 - 0.6, (1300, 500),
           [(c_like, ax + 98, cy + 8), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6)])
    return t


# --- 4. Tarjeta pequeña --------------------------------------------------------------------------------------

def tarjeta_mini():
    """A small card at the lower right: just the channel's name over «SUSCRIBIRME», for videos with little room."""
    D = 5.0
    t = _kit("boton-tarjeta-mini", "Tarjeta pequeña con suscribirse", "Small subscribe card", D, 8203,
             ["tarjeta", "pequeño", "esquina", "minimalista"], thumb_at=2.6)
    photo_bg(t, "h-cafe-01", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    card = Box(1500, 760, 300, 150)
    cx = card.x + card.w / 2
    rrect(t, t.track("shape", "Tarjeta"), WHITE, t0, dur, card, radius=22, motion=_life(t0, dur, s0=0.3),
          layers=[shadow("#000000", 0, 12, 30, 0.35), fill(WHITE), no_stroke()])
    label(t, t.track("text", "Nombre"), "Tu canal", t0 + 0.25, dur - 0.55, Box(card.x + 12, card.y + 16, card.w - 24, 46),
          "Sora", 30, INK, weight=700, anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Nombre del canal")
    c_sub = 1.9
    btn = centered(cx, card.y + 102, 236, 56)
    _subscribe_button(t, btn, t0 + 0.3, c_sub, t1 - 0.05, 22)
    Cursor(t, 1.0, t1 - 0.6, (1200, 560), [(c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6)])
    return t


# --- 5. Píldora con campana ------------------------------------------------------------------------------------

def pildora_campana():
    """A pill without a picture: like, the bell and «SUSCRIBIRME». The cursor likes, subscribes and rings."""
    D = 6.0
    t = _kit("boton-pildora-campana", "Píldora con campana y suscribirse", "Pill with bell and subscribe", D, 8204,
             ["píldora", "campana", "me gusta", "compacto"], thumb_at=3.9)
    photo_bg(t, "h-studio-01", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    pillb = Box(1240, 860, 560, 100)
    cy = pillb.y + pillb.h / 2
    pill(t, t.track("shape", "Píldora"), WHITE, t0, dur, pillb, _life(t0, dur, s0=0.3),
         layers=[shadow("#000000", 0, 12, 30, 0.35), fill(WHITE), no_stroke()])
    c_like, c_sub, c_bell = 1.7, 2.6, 3.5
    lx, bx = pillb.x + 62, pillb.x + 128
    _like(t, lx, cy, 40, t0 + 0.3, c_like, t1 - 0.1)
    _bell(t, bx, cy, 40, t0 + 0.35, c_bell, t1 - 0.1)
    btn = Box(pillb.x + pillb.w - 290, cy - 32, 270, 64)
    _subscribe_button(t, btn, t0 + 0.3, c_sub, t1 - 0.05, 23)
    Cursor(t, 0.9, t1 - 0.4, (900, 520),
           [(c_like, lx + 8, cy + 10), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_bell, bx + 8, cy + 10)])
    return t


# --- 6. Íconos grandes -------------------------------------------------------------------------------------------

def iconos_grandes():
    """No card: a big like, «SUSCRIBIRME» and a big bell over the video, in white. Each one lights up when the
    cursor clicks it; the bell turns yellow and rings."""
    D = 6.0
    t = _kit("boton-iconos-grandes", "Íconos grandes: me gusta, suscribirse y campana",
             "Big icons: like, subscribe and bell", D, 8205, ["íconos", "grande", "sin fondo", "campana", "me gusta"],
             thumb_at=4.0)
    photo_bg(t, "h-concert-01", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    cy = 900
    c_like, c_sub, c_bell = 1.7, 2.7, 3.7
    lx, bx = 640, 1280
    _like(t, lx, cy, 96, t0, c_like, t1 - 0.1, colour=WHITE)
    _bell(t, bx, cy, 92, t0 + 0.15, c_bell, t1 - 0.1, colour=WHITE, on=SUN)
    btn = centered(960, cy, 340, 92)
    _subscribe_button(t, btn, t0 + 0.08, c_sub, t1 - 0.05, 32, radius=18)
    Cursor(t, 0.9, t1 - 0.4, (1500, 560),
           [(c_like, lx + 14, cy + 22), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_bell, bx + 14, cy + 22)],
           size=52)
    return t


# --- 7. Píldora que se alarga ---------------------------------------------------------------------------------------

def pildora_larga():
    """The channel's picture arrives alone, the pill stretches out of it to the right, and like, «SUSCRIBIRME»
    and the bell come in one after another; at the end it all folds back into the picture."""
    D = 6.5
    t = _kit("boton-pildora-larga", "Píldora que se alarga desde la foto", "Pill that stretches out of the picture",
             D, 8206, ["píldora", "foto", "campana", "me gusta", "se alarga"], thumb_at=4.3)
    photo_bg(t, "h-city-02", s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    pillb = Box(120, 880, 620, 110)
    cy = pillb.y + pillb.h / 2
    ax = pillb.x + 55
    grow_dx = -(pillb.w - pillb.h) / 2
    sx0 = pillb.h / pillb.w
    pill(t, t.track("shape", "Píldora"), WHITE, t0 + 0.4, dur - 0.4, pillb,
         [(0, {"sx": sx0, "dx": grow_dx}, "out"), (0.7, {}, "hold"), (dur - 0.4 - 0.9, {}, "inout"),
          (dur - 0.4 - 0.35, {"sx": sx0, "dx": grow_dx})],
         layers=[shadow("#000000", 0, 12, 30, 0.35), fill(WHITE), no_stroke()],
         opacity=keys([(0, 1.0, "hold"), (dur - 0.7, 1.0), (dur - 0.4, 0.0)]))
    t.solid(t.track("shape", "Aro"), TEAL, t0, dur, centered(ax, cy, 96, 96), _life(t0, dur), kind="ellipse")
    circle_photo(t, "h-portrait-02", t0, dur, centered(ax, cy, 84, 84), _life(t0, dur), label="Foto del canal")
    c_like, c_sub, c_bell = 2.1, 3.0, 3.9
    a, b = t0 + 0.9, t1 - 1.0
    lx = ax + 100
    _like(t, lx, cy, 42, a, c_like, b)
    btn = Box(lx + 50, cy - 33, 270, 66)
    _subscribe_button(t, btn, a + 0.1, c_sub, b + 0.05, 23)
    bx = btn.x + btn.w + 60
    _bell(t, bx, cy, 42, a + 0.2, c_bell, b)
    Cursor(t, 1.4, t1 - 0.9, (900, 600),
           [(c_like, lx + 8, cy + 10), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_bell, bx + 8, cy + 10)])
    return t


# --- 8. Sígueme en mis redes --------------------------------------------------------------------------------------

PLAY = "M 25 10 L 90 50 L 25 90 Z"
BUBBLE = "M 8 12 L 92 12 L 92 70 L 46 70 L 22 92 L 26 70 L 8 70 Z"
HEART = "M 50 90 C 10 62 0 42 8 24 C 18 4 42 6 50 26 C 58 6 82 4 92 24 C 100 42 90 62 50 90 Z"


def redes():
    """Three pills along the bottom, one after another: a round badge with an icon (video, chat, heart; no
    brand logos), the user's handle, and a «SEGUIR» tag that pops under each one."""
    D = 6.0
    t = _kit("boton-redes", "Sígueme en mis redes", "Follow me on my socials", D, 8207,
             ["redes", "sígueme", "seguir", "usuario", "perfil"], thumb_at=3.2)
    photo_bg(t, "h-concert-03", s1=1.03, label="Tu video")
    t1 = D - 0.2
    items = [(PLAY, CORAL, "@tucanal", "Usuario 1"), (BUBBLE, TEAL, "@tuperfil", "Usuario 2"),
             (HEART, SUN, "@tunombre", "Usuario 3")]
    w, h, gap = 470, 84, 50
    x0 = (1920 - (3 * w + 2 * gap)) / 2
    y = 930
    for i, (icon, colour, handle, name) in enumerate(items):
        a = 0.3 + i * 0.25
        dur = t1 - a - (2 - i) * 0.12
        x = x0 + i * (w + gap)
        box = Box(x, y, w, h)
        cy = y + h / 2
        enter = [(0, {"dx": -120, "s": 0.6}, "back"), (0.5, {}, "hold"), (dur - 0.35, {}, "in"), (dur, {"s": 0.0})]
        pill(t, t.track("shape", "Redes"), WHITE, a, dur, box, enter,
             layers=[shadow("#000000", 0, 10, 26, 0.35), fill(WHITE), no_stroke()])
        t.solid(t.track("shape", "Redes"), colour, a + 0.15, dur - 0.15, centered(x + 44, cy, 64, 64),
                _life(0, dur - 0.15), kind="ellipse")
        path(t, t.track("shape", "Íconos"), WHITE, a + 0.25, dur - 0.25, centered(x + 44, cy, 30, 30), icon,
             filled=True, motion=_life(0, dur - 0.25))
        label(t, t.track("text", "Usuarios"), handle, a + 0.35, dur - 0.55, Box(x + 90, y, w - 110, h), "Sora", 30, INK,
              weight=700, align="left", anim_in=tanim("fade", duration=0.35), anim_out=OUT(0.2), name=name)
        tag = Box(x + w - 140, y + h - 16, 120, 34)
        tg0 = 1.6 + i * 0.35
        tdur = t1 - tg0 - (2 - i) * 0.12 - 0.3
        pill(t, t.track("shape", "Seguir"), colour, tg0, tdur, tag,
             [(0, {"s": 0.0}, "back"), (0.35, {}, "hold"), (tdur - 0.3, {}, "in"), (tdur, {"s": 0.0})])
        label(t, t.track("text", "Seguir"), "SEGUIR", tg0 + 0.1, tdur - 0.3, tag, "Sora", 16,
              NAVY if colour == SUN else WHITE, weight=800, spacing=1.5, anim_in=tanim("fade", duration=0.2),
              anim_out=OUT(0.15), name=f"Seguir {i + 1}")
    return t


TEMPLATES = [tarjeta_canal, barra_canal, pildora, tarjeta_mini, pildora_campana, iconos_grandes, pildora_larga, redes]
