"""Kit de YouTube, batch p (2026-10-30): the last pieces of Jorge's «pack youtube 6», almost the same and our own
(see templates_ytkit_i..o): three more end screens (a white wedge rising from the bottom, a white triangle pointing
at the next video, a darkened video with an arrow to the picture) and two titles (outlined boxes, two weights).
Order 8460-8479.
"""

from __future__ import annotations

from kit import Box, centered, circle_photo, fill, keys, no_stroke, outline, photo_bg, rrect, shadow, wide
from templates_ytkit_a import _stroke, path
from templates_ytkit_i import _text_width as _width_800
from templates_ytkit_j import CORAL, INK, WHITE, _hollow, _life, logo, txt
from templates_ytkit_l import _button, _handles, _video

SOFT = "#5B6270"


def _text_width(text, size):
    return _width_800(text, size) * 1.05


def _kit(id, es, en, section, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _shade(colour=WHITE):
    return [shadow("#000000", 0, 4, 16, 0.45), fill(colour)]


def _avatar(t, sample, cx, cy, d, a, D, ring=WHITE):
    t.solid(t.track("shape", "Aro"), ring, a, D - a - 0.3, centered(cx, cy, d + 16, d + 16), _life(D - a - 0.3),
            kind="ellipse", layers=[shadow("#000000", 0, 8, 22, 0.3), fill(ring), no_stroke()])
    circle_photo(t, sample, a + 0.05, D - a - 0.35, centered(cx, cy, d, d), _life(D - a - 0.35), label="Foto del canal")


def _outlined_video(t, x, y, w, h, sample, name, a, D, frm, colour=CORAL):
    m = [(0, frm, "out"), (0.55, {}, "hold"), (D - a - 0.4, {}, "in"), (D - a, frm)]
    t.photo(t.track("video", name), sample, a, D - a, Box(x, y, w, h), m, label=name)
    rrect(t, t.track("shape", "Marcos"), colour, a, D - a, Box(x - 6, y - 6, w + 12, h + 12), radius=2, motion=m,
          layers=[_hollow(), _stroke(colour, 6, "inside")])


# --- End screens ------------------------------------------------------------------------------------------------------

def final_cuna():
    """«¡GRACIAS POR VER!» over the video; a white wedge rises from the bottom with the picture at its tip, the
    reminder under it and the previous and next videos in coral frames either side."""
    D = 10.0
    t = _kit("final-cuna", "Pantalla final con cuña blanca", "End screen with a white wedge", "pantallas-finales", D,
             8460, ["pantalla final", "cuña", "gracias", "dos videos"], thumb_at=4.5)
    photo_bg(t, "h-nature-06", s1=1.04, label="Tu video")
    path(t, t.track("shape", "Cuña"), WHITE, 0.2, D - 0.2, Box(0, 520, 1920, 560), "M 0 34 L 50 0 L 100 34 L 100 100 L 0 100 Z",
         filled=True, motion=[(0, {"dy": 600}, "out"), (0.7, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dy": 600})],
         layers=[shadow("#000000", 0, -8, 30, 0.3), fill(WHITE), no_stroke()])
    txt(t, "¡GRACIAS POR VER!", Box(360, 130, 1200, 100), 76, 0.8, D - 1.2, weight=900, anim="typewriter", ad=0.6,
        name="Gracias", layers=_shade())
    _avatar(t, "h-portrait-01", 960, 660, 170, 0.9, D, ring=CORAL)
    txt(t, "NO OLVIDES DAR ME GUSTA\nY COMENTAR", Box(700, 770, 520, 90), 28, 1.3, D - 1.7, colour=INK, weight=800,
        line=1.15, name="Llamado")
    for i, (x, lab, sample, name) in enumerate([(170, "VIDEO ANTERIOR", "h-travel-02", "Video anterior"),
                                                (1270, "VIDEO SIGUIENTE", "h-city-05", "Video siguiente")]):
        a = 1.2 + i * 0.2
        txt(t, lab, Box(x, 742, 480, 48), 30, a + 0.3, D - a - 0.6, colour=INK, weight=900, spacing=1,
            name=f"Etiqueta {i + 1}")
        _outlined_video(t, x, 800, 480, 240, sample, name, a, D, {"dy": 400})
    return t


def final_triangulo():
    """A white triangle comes in from the left with the picture and the reminder; a coral arrowhead at its tip points
    at the next video. «¡GRACIAS POR VER!» on top and the handles along the bottom."""
    D = 10.0
    t = _kit("final-triangulo", "Pantalla final con triángulo", "End screen with a triangle", "pantallas-finales", D,
             8461, ["pantalla final", "triángulo", "gracias", "video siguiente"], thumb_at=4.5)
    photo_bg(t, "h-beach-04", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.3)]))
    tri = Box(0, 150, 760, 780)
    m = [(0, {"dx": -800}, "out"), (0.7, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dx": -800})]
    path(t, t.track("shape", "Triángulo"), WHITE, 0.2, D - 0.2, tri, "M 0 0 L 100 50 L 0 100 Z", filled=True, motion=m,
         layers=[shadow("#000000", 10, 0, 30, 0.35), fill(WHITE), no_stroke()])
    path(t, t.track("shape", "Flecha"), CORAL, 0.4, D - 0.6, Box(tri.x + tri.w - 30, 500, 80, 80), "M 0 0 L 100 50 L 0 100 Z",
         filled=True, motion=[(0, {"dx": -900}, "out"), (0.8, {}, "hold"), (D - 0.6 - 0.6, {}, "in"), (D - 0.6, {"dx": -900})])
    _avatar(t, "h-portrait-05", 200, 460, 190, 0.9, D, ring=CORAL)
    txt(t, "NO OLVIDES\nDAR ME GUSTA\nY COMENTAR", Box(60, 590, 300, 130), 28, 1.2, D - 1.6, colour=INK, weight=900,
        line=1.15, name="Llamado")
    txt(t, "¡GRACIAS POR VER!", Box(860, 150, 960, 90), 64, 0.9, D - 1.3, weight=900, anim="typewriter", ad=0.6,
        name="Gracias", layers=_shade())
    _video(t, 900, 300, 880, 495, "h-travel-05", "Video siguiente", 1.1, D, {"dx": 1100})
    txt(t, "VIDEO SIGUIENTE", Box(900, 812, 880, 50), 32, 1.5, D - 1.9, weight=900, spacing=2, name="Etiqueta",
        layers=_shade())
    _handles(t, 960, 2.0, D, (960, 1240, 1520))
    return t


def final_flecha():
    """The video darkened; «¡GRACIAS POR VER!» and the reminder at the top left, the recommended video under them; on
    the right the picture big, a coral «SUSCRÍBETE» and a hand-drawn arrow from the button up to the picture."""
    D = 10.0
    t = _kit("final-flecha", "Pantalla final con flecha", "End screen with an arrow", "pantallas-finales", D, 8462,
             ["pantalla final", "flecha", "suscríbete", "video recomendado"], thumb_at=4.5)
    photo_bg(t, "h-city-03", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.55)]))
    txt(t, "¡GRACIAS POR VER!", Box(150, 120, 900, 90), 68, 0.4, D - 0.8, weight=900, align="left", anim="wipe", ad=0.6,
        name="Gracias", layers=_shade())
    txt(t, "NO OLVIDES DAR ME GUSTA Y COMENTAR", Box(152, 210, 900, 50), 28, 0.8, D - 1.2, colour="#D3D8E0", weight=800,
        align="left", spacing=1, name="Llamado")
    _video(t, 150, 310, 800, 450, "h-travel-02", "Video recomendado", 0.9, D, {"dx": -1000})
    txt(t, "VIDEO RECOMENDADO", Box(150, 780, 800, 50), 30, 1.3, D - 1.7, weight=900, align="left", spacing=2,
        name="Etiqueta", layers=_shade())
    _avatar(t, "h-portrait-03", 1420, 420, 300, 1.0, D)
    _button(t, 1340, 690, "SUSCRÍBETE", 1.4, D, fg=WHITE, bg=CORAL, size=38)
    path(t, t.track("shape", "Flecha"), WHITE, 1.8, D - 2.1, Box(1560, 450, 170, 240),
         "M 0 100 C 85 100 100 50 22 8 M 22 8 L 52 10 M 22 8 L 30 36", 7, draw=(0, 0.6), erase=(D - 2.1 - 0.4, 0.3))
    for i, net in enumerate(("instagram", "facebook", "x")):
        logo(t, net, 1220 + i * 90, 820, 40, 2.0 + i * 0.12, D - 2.4 - i * 0.12)
    txt(t, "@tuusuario", Box(1150, 860, 400, 56), 32, 2.3, D - 2.7, weight=800, name="Usuario", layers=_shade())
    return t


# --- Titles -----------------------------------------------------------------------------------------------------------

def _outlined_line(t, text, x, y, size, a, until, name):
    w = _text_width(text, size) + size * 0.9
    h = size * 1.55
    outline(t, t.track("shape", "Marcos"), WHITE, 4, a, until - a, Box(x, y, w, h),
            [(0, {"sx": 0.0, "dx": -w / 2}, "out"), (0.35, {}, "hold"), (until - a - 0.3, {}, "in"),
             (until - a, {"sx": 0.0, "dx": w / 2})])
    txt(t, text, Box(x, y, w, h), size, a + 0.2, until - a - 0.35, weight=900, anim="wipe", ad=0.4, name=name,
        layers=_shade())


def titulo_contornos():
    """«ESCRIBE TU TEXTO» and «EN CAJAS DE CONTORNO», each in a white outline that opens from the left."""
    D = 5.0
    t = _kit("titulo-contornos", "Título en cajas de contorno", "Title in outlined boxes", "titulos-estilo", D, 8463,
             ["título", "contorno", "cajas", "blanco"], thumb_at=2.4)
    photo_bg(t, "h-city-06", s1=1.04, label="Tu video")
    _outlined_line(t, "ESCRIBE TU TEXTO", 140, 420, 72, 0.3, D - 0.3, "Línea 1")
    _outlined_line(t, "EN CAJAS DE CONTORNO", 140, 540, 48, 0.6, D - 0.4, "Línea 2")
    return t


def titulo_dos_pesos():
    """«TÍTULOS EN CAJA» in Black and «con cualquier tipografía» in a regular weight under it, centred, sliding up."""
    D = 5.0
    t = _kit("titulo-dos-pesos", "Título en dos pesos", "Two-weight title", "titulos-estilo", D, 8464,
             ["título", "tipografía", "centrado", "simple"], thumb_at=2.4)
    photo_bg(t, "h-beach-02", s1=1.04, label="Tu video")
    txt(t, "TÍTULOS EN CAJA", Box(260, 430, 1400, 110), 88, 0.3, D - 0.6, weight=900, anim="rise", ad=0.5,
        name="Título", layers=_shade())
    txt(t, "con cualquier tipografía", Box(260, 540, 1400, 80), 52, 0.6, D - 0.9, weight=500, anim="rise", ad=0.5,
        name="Subtítulo", layers=_shade())
    return t


TEMPLATES = [final_cuna, final_triangulo, final_flecha, titulo_contornos, titulo_dos_pesos]
