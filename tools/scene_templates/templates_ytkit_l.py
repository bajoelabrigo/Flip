"""Kit de YouTube, batch l (2026-10-30): the last end screens of Jorge's «pack youtube 6», almost the same and our
own (see templates_ytkit_i/j/k): a narrow coral card, a coral circle coming in from the side, and a grey panel with
a curve. Official logos beside the handles. Order 8350-8369.
"""

from __future__ import annotations

from kit import Box, centered, circle_photo, fill, keys, label, no_stroke, photo_bg, pill, rrect, shadow, tanim, wide
from templates_ytkit_a import OUT, _stroke
from templates_ytkit_i import _text_width
from templates_ytkit_j import CORAL, INK, WHITE, _hollow, _life, logo, txt

FONT = "Montserrat"
GREY = "#2B2F36"


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=["kit:pantallas-finales", "youtube"] + tags, **kw)


def _video(t, x, y, w, h, sample, name, a, D, frm):
    m = [(0, frm, "out"), (0.55, {}, "hold"), (D - a - 0.4, {}, "in"), (D - a, frm)]
    rrect(t, t.track("shape", "Marcos"), WHITE, a, D - a, Box(x - 8, y - 8, w + 16, h + 16), radius=4, motion=m,
          layers=[shadow("#000000", 0, 12, 30, 0.3), fill(WHITE), no_stroke()])
    t.photo(t.track("video", name), sample, a, D - a, Box(x, y, w, h), m, label=name)


def _avatar(t, sample, cx, cy, d, a, D):
    t.solid(t.track("shape", "Aro"), WHITE, a, D - a - 0.3, centered(cx, cy, d + 16, d + 16), _life(D - a - 0.3), kind="ellipse")
    circle_photo(t, sample, a + 0.05, D - a - 0.35, centered(cx, cy, d, d), _life(D - a - 0.35), label="Foto del canal")


def _button(t, cx, cy, text, a, D, fg=CORAL, bg=WHITE, size=34):
    w = _text_width(text, size) + size * 1.6
    btn = centered(cx, cy, w, size * 2.0)
    pill(t, t.track("shape", "Botón"), bg, a, D - a - 0.3, btn, _life(D - a - 0.3),
         layers=[shadow("#000000", 0, 8, 20, 0.25), fill(bg), no_stroke()])
    txt(t, text, btn, size, a + 0.1, D - a - 0.5, colour=fg, weight=900, spacing=1, name="Botón")


def _handles(t, y, a, D, xs, colour=WHITE, size=30):
    for i, (net, x) in enumerate(zip(("instagram", "facebook", "x"), xs)):
        b = a + i * 0.15
        logo(t, net, x, y, size, b, D - b - 0.3, colour=colour)
        txt(t, "@tuusuario", Box(x + size * 0.8, y - 26, 300, 52), 28, b + 0.1, D - b - 0.5, colour=colour, weight=700,
            align="left", anim="slide-left", ad=0.3, name=f"Red {i + 1}")


def final_tarjeta_vertical():
    """A narrow coral card rises over the darkened video: «¡GRACIAS POR VER!», the picture, «SUSCRÍBETE», a line
    and the three handles one under another."""
    D = 10.0
    t = _kit("final-tarjeta-vertical", "Pantalla final: tarjeta vertical", "End screen: tall card", D, 8350,
             ["pantalla final", "tarjeta", "gracias", "suscríbete"], thumb_at=4.5)
    photo_bg(t, "h-city-02", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.4)]))
    card = Box(700, 90, 520, 900)
    rrect(t, t.track("shape", "Tarjeta"), CORAL, 0.2, D - 0.2, card, radius=18,
          motion=[(0, {"dy": 1000}, "out"), (0.7, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dy": 1000})],
          layers=[shadow("#000000", 0, 16, 40, 0.4), fill(CORAL), no_stroke()])
    txt(t, "¡GRACIAS\nPOR VER!", Box(card.x + 40, card.y + 60, card.w - 80, 200), 72, 0.9, D - 1.3, weight=900, line=1.0,
        anim="typewriter", ad=0.7, name="Gracias")
    _avatar(t, "h-portrait-04", 960, 470, 200, 1.1, D)
    _button(t, 960, 660, "SUSCRÍBETE", 1.5, D)
    txt(t, "NO OLVIDES DAR ME GUSTA\nY COMENTAR", Box(card.x + 30, 720, card.w - 60, 90), 26, 1.8, D - 2.2, weight=700,
        line=1.15, name="Llamado")
    xs = (770, 960, 1150)
    for i, net in enumerate(("instagram", "facebook", "x")):
        b = 2.0 + i * 0.15
        logo(t, net, xs[i], 870, 40, b, D - b - 0.3)
    txt(t, "@tuusuario", Box(card.x, 900, card.w, 50), 28, 2.3, D - 2.7, weight=700, name="Usuario")
    return t


def final_circulo():
    """A big coral circle comes in from the left over the video, «¡GRACIAS POR VER!» and «SUSCRÍBETE» on it; on the
    right «VIDEO SIGUIENTE» and «VIDEO RECOMENDADO», two slots; the handles along the bottom."""
    D = 10.0
    t = _kit("final-circulo", "Pantalla final con círculo", "End screen with a circle", D, 8351,
             ["pantalla final", "círculo", "gracias", "dos videos"], thumb_at=4.5)
    photo_bg(t, "h-nature-01", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.35)]))
    t.solid(t.track("shape", "Círculo"), CORAL, 0.2, D - 0.2, centered(330, 540, 1180, 1180),
            [(0, {"dx": -1300}, "out"), (0.8, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dx": -1300})],
            kind="ellipse", layers=[shadow("#000000", 10, 0, 40, 0.35), fill(CORAL), no_stroke()])
    txt(t, "¡GRACIAS\nPOR VER!", Box(140, 300, 680, 220), 90, 0.9, D - 1.3, weight=900, line=1.0, anim="typewriter",
        ad=0.7, name="Gracias")
    _button(t, 400, 600, "SUSCRÍBETE", 1.4, D)
    for i, (lab, sample, name) in enumerate([("VIDEO SIGUIENTE", "h-travel-02", "Video siguiente"),
                                             ("VIDEO RECOMENDADO", "h-cafe-04", "Video recomendado")]):
        a = 1.1 + i * 0.25
        y = 170 + i * 380
        txt(t, lab, Box(1150, y - 60, 620, 50), 32, a + 0.4, D - a - 0.8, weight=800, spacing=1, name=f"Etiqueta {i + 1}")
        _video(t, 1150, y, 600, 300, sample, name, a, D, {"dx": 900})
    _handles(t, 990, 2.0, D, (1150, 1400, 1650))
    return t


def final_panel_curvo():
    """A grey panel on the left with a coral curved edge: the picture, «¡GRACIAS POR VER!», «SUSCRÍBETE PARA MÁS
    VIDEOS» and the button; on the video side «VIDEO SIGUIENTE» in a frame."""
    D = 10.0
    t = _kit("final-panel-curvo", "Pantalla final con panel curvo", "End screen with a curved panel", D, 8352,
             ["pantalla final", "panel", "curva", "gracias"], thumb_at=4.5)
    photo_bg(t, "h-sport-01", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Borde"), CORAL, 0.2, D - 0.2, centered(-60, 540, 1500, 1500),
            [(0, {"dx": -1200}, "out"), (0.8, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dx": -1200})],
            kind="ellipse")
    t.solid(t.track("shape", "Panel"), GREY, 0.25, D - 0.25, centered(-90, 540, 1440, 1440),
            [(0, {"dx": -1200}, "out"), (0.8, {}, "hold"), (D - 0.25 - 0.6, {}, "in"), (D - 0.25, {"dx": -1200})],
            kind="ellipse", layers=[shadow("#000000", 10, 0, 40, 0.4), fill(GREY), no_stroke()])
    _avatar(t, "h-portrait-01", 320, 280, 190, 1.0, D)
    txt(t, "¡GRACIAS POR VER!", Box(40, 405, 560, 70), 42, 1.2, D - 1.6, weight=900, anim="typewriter", ad=0.6,
        name="Gracias")
    txt(t, "SUSCRÍBETE PARA MÁS VIDEOS", Box(60, 480, 520, 50), 26, 1.5, D - 1.9, weight=700, spacing=1,
        colour="#C9CFD8", name="Llamado")
    _button(t, 320, 590, "SUSCRÍBETE", 1.7, D, fg=WHITE, bg=CORAL, size=32)
    # The handles one under another (the panel is narrow).
    for i, net in enumerate(("instagram", "facebook", "x")):
        b = 2.0 + i * 0.15
        logo(t, net, 200, 700 + i * 56, 30, b, D - b - 0.3)
        txt(t, "@tuusuario", Box(232, 674 + i * 56, 300, 52), 28, b + 0.1, D - b - 0.5, weight=700, align="left",
            anim="slide-left", ad=0.3, name=f"Red {i + 1}")
    txt(t, "VIDEO SIGUIENTE", Box(900, 240, 820, 60), 40, 1.1, D - 1.5, weight=800, spacing=1, name="Etiqueta")
    _video(t, 940, 310, 740, 416, "h-city-05", "Video siguiente", 1.0, D, {"dx": 1100})
    return t


TEMPLATES = [final_tarjeta_vertical, final_circulo, final_panel_curvo]
