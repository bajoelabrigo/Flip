"""Kit de YouTube, batch o (2026-10-30): what was left of Jorge's «pack youtube 6», almost the same and our own (see
templates_ytkit_i..n): four more channel intros, eight titles (watch next, outlined square, framed boxes, a square
with a vertical label, mixed weights, a numbered pill, «¡SUSCRÍBETE AHORA!», the big «¡GRACIAS POR VER!»), the
video in a circle on coral, and three more ways to show the socials with the platforms' official logos.
Order 8430-8459.
"""

from __future__ import annotations

from brand_logos import COLOURS
from kit import Box, centered, circle_photo, fill, keys, label, no_stroke, outline, photo_bg, pill, rrect, shadow, tanim, wide
from templates_ytkit_a import OUT, _stroke, path
from templates_ytkit_i import _box_line, _text_width as _width_800
from templates_ytkit_j import CORAL, INK, WHITE, _hollow, _life, txt, yt_icon
from templates_ytkit_k import _cycle, _line_text, _wipe_box, logo

FONT = "Montserrat"
SOFT = "#5B6270"
CROSS = "M 0 0 L 100 100 M 100 0 L 0 100"


def _text_width(text, size):
    """Most of these are set in Black (900), a little wider than the ExtraBold the measure uses."""
    return _width_800(text, size) * 1.05


def _kit(id, es, en, section, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _shade(colour=WHITE):
    return [shadow("#000000", 0, 4, 16, 0.45), fill(colour)]


def _sh(colour):
    return [shadow("#000000", 0, 6, 18, 0.3), fill(colour), no_stroke()]


# --- Intros -----------------------------------------------------------------------------------------------------------

def intro_historia():
    """The YouTube icon pops on the left, «GRAN HISTORIA» unrolls beside it and a coral «CANAL» tag drops under."""
    D = 5.0
    t = _kit("intro-historia", "Gran historia", "Big story", "aperturas", D, 8430,
             ["intro", "logo", "canal", "historia"], thumb_at=2.4)
    photo_bg(t, "h-city-03", s1=1.05, label="Tu video")
    end = D - 0.3
    size = 92
    w = _text_width("GRAN HISTORIA", size)
    x0 = 960 - (w + 170) / 2
    yt_icon(t, x0 + 70, 520, 140, 0.3, end - 0.3)
    txt(t, "GRAN HISTORIA", Box(x0 + 170, 460, w + 20, 120), size, 0.7, end - 0.8, align="left", anim="wipe", ad=0.6,
        weight=900, name="Título", layers=_shade())
    _line_text(t, "CANAL", Box(x0 + 174 + 36 * 0.4, 590, 400, 58), 36, 1.2, end - 1.3, anim="wipe", ad=0.3, name="Etiqueta",
               box_bg=(CORAL, 1.0), pad=36 * 0.4, spacing=3)
    return t


def intro_blog():
    """The icon drops in on top; «BLOG DE VIAJES» rises under it, big and centred."""
    D = 5.0
    t = _kit("intro-blog", "Blog de viajes", "Travel blog", "aperturas", D, 8431,
             ["intro", "logo", "blog", "viajes"], thumb_at=2.4)
    photo_bg(t, "h-travel-05", s1=1.05, label="Tu video")
    end = D - 0.3
    yt_icon(t, 960, 420, 130, 0.3, end - 0.3,
            motion=[(0, {"dy": -140, "s": 0.6}, "back"), (0.5, {}, "hold"), (end - 0.65, {}, "in"), (end - 0.3, {"s": 0.0})])
    txt(t, "BLOG DE VIAJES", Box(260, 500, 1400, 140), 104, 0.8, end - 0.9, weight=900, anim="rise", ad=0.5,
        name="Título", layers=_shade())
    return t


def intro_inclinado():
    """A coral band tilted up opens with the channel's name in white; the icon in white pops at its top-left corner."""
    D = 5.0
    t = _kit("intro-inclinado", "Nombre del canal inclinado", "Tilted channel name", "aperturas", D, 8432,
             ["intro", "inclinado", "nombre", "coral"], thumb_at=2.4)
    photo_bg(t, "h-beach-02", s1=1.05, label="Tu video")
    end = D - 0.3
    size = 76
    w = _text_width("NOMBRE DEL CANAL", size) + size * 1.4
    band = centered(960, 560, w, size * 1.9)
    rot = keys([(0, -6.0)])
    t.solid(t.track("shape", "Banda"), CORAL, 0.3, end - 0.3, band,
            [(0, {"sx": 0.0}, "back"), (0.45, {}, "hold"), (end - 0.65, {}, "in"), (end - 0.3, {"sx": 0.0})],
            rotation=rot, layers=_sh(CORAL))
    label(t, t.track("text", "Textos"), "NOMBRE DEL CANAL", 0.55, end - 0.85, band, FONT, size, WHITE, weight=900,
          anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Nombre del canal", rotation=rot)
    yt_icon(t, band.x + 40, band.y - 30, 110, 0.75, end - 0.95, colour=WHITE, play=CORAL)
    return t


def intro_pildora():
    """The icon pops in the middle, a white pill with the name in coral slides out under it, little crosses spark round."""
    D = 5.0
    t = _kit("intro-pildora", "Logo y nombre en píldora", "Logo and name in a pill", "aperturas", D, 8433,
             ["intro", "logo", "píldora", "destellos"], thumb_at=2.4)
    photo_bg(t, "h-man-03", s1=1.05, label="Tu video")
    end = D - 0.3
    yt_icon(t, 960, 450, 150, 0.3, end - 0.3)
    size = 54
    w = _text_width("TuCanal", size) + size * 1.6
    box = centered(960, 580, w, size * 1.8)
    pill(t, t.track("shape", "Píldora"), WHITE, 0.7, end - 0.7, box,
         [(0, {"sy": 0.0, "dy": -40}, "back"), (0.4, {}, "hold"), (end - 1.0, {}, "in"), (end - 0.7, {"sy": 0.0})],
         layers=_sh(WHITE))
    txt(t, "TuCanal", box, size, 0.9, end - 1.0, colour=CORAL, weight=900, name="Nombre del canal")
    for k, (x, y, s) in enumerate([(820, 380, 34), (1110, 400, 26), (790, 600, 24), (1150, 560, 32)]):
        a = 0.6 + k * 0.12
        path(t, t.track("shape", "Destellos"), WHITE, a, 1.0, centered(x, y, s, s), CROSS, 6,
             motion=[(0, {"s": 0.0}, "back"), (0.3, {}, "hold"), (0.7, {}, "in"), (1.0, {"s": 0.0})])
    return t


# --- Titles -----------------------------------------------------------------------------------------------------------

def ver_siguiente():
    """A white box in the lower left: «VER SIGUIENTE» in black with a coral bar, the video's title in grey under it."""
    D = 5.0
    t = _kit("titulo-ver-siguiente", "Ver siguiente", "Watch next", "titulos-estilo", D, 8434,
             ["título", "ver siguiente", "caja", "video"], thumb_at=2.4)
    photo_bg(t, "h-desk-02", s1=1.04, label="Tu video")
    end = D - 0.3
    sub = "Cómo hacer un buen video"
    w = max(_text_width("VER SIGUIENTE", 44), _text_width(sub, 30)) + 2 * 44 * 0.6 + 40
    box = Box(110, 820, w, 150)
    _wipe_box(t, box.x, box.y, box.w, box.h, WHITE, 0.3, end - 0.3)
    t.solid(t.track("shape", "Barra"), CORAL, 0.5, end - 0.6, Box(box.x, box.y, 12, box.h),
            [(0, {"sy": 0.0}, "out"), (0.3, {}, "hold"), (end - 0.6 - 0.25, {}, "in"), (end - 0.6, {"sy": 0.0})])
    txt(t, "VER SIGUIENTE", Box(box.x + 40, box.y + 22, box.w - 50, 60), 44, 0.6, end - 0.8, colour=INK, weight=900,
        align="left", anim="wipe", ad=0.4, name="Título")
    txt(t, sub, Box(box.x + 40, box.y + 86, box.w - 50, 44), 30, 0.85, end - 1.0, colour=SOFT, weight=600, align="left",
        name="Video siguiente")
    return t


def titulo_cuadro_contorno():
    """An outlined square draws itself on the left and the three lines of the title run out of it."""
    D = 5.0
    t = _kit("titulo-cuadro-contorno", "Título sobre un cuadro de contorno", "Title over an outlined square",
             "titulos-estilo", D, 8435, ["título", "contorno", "cuadro", "moderno"], thumb_at=2.4)
    photo_bg(t, "h-beach-03", s1=1.04, label="Tu video")
    end = D - 0.3
    sq = Box(460, 330, 330, 330)
    path(t, t.track("shape", "Cuadro"), WHITE, 0.2, end - 0.2, sq, "M 0 0 L 100 0 L 100 100 L 0 100 Z", 12,
         draw=(0, 0.7), erase=(end - 0.2 - 0.45, 0.35))
    for i, line in enumerate(["TÍTULOS", "MODERNOS PARA", "TU CANAL"]):
        a = 0.5 + i * 0.15
        txt(t, line, Box(sq.x + 70, 365 + i * 92, 1100, 100), 84, a, end - a - 0.1, weight=900, align="left",
            anim="wipe", ad=0.45, name=f"Línea {i + 1}", layers=_shade(), line=1.0)
    return t


def titulo_marco_cajas():
    """Two lines in black boxes — «LA MEJOR SOLUCIÓN / PARA TU TEXTO» — inside an outlined frame that draws itself."""
    D = 5.0
    t = _kit("titulo-marco-cajas", "Título en cajas dentro de un marco", "Boxed title in a frame", "titulos-estilo", D,
             8436, ["título", "cajas", "marco", "negro"], thumb_at=2.4)
    photo_bg(t, "h-nature-06", s1=1.04, label="Tu video")
    end = D - 0.3
    size = 56
    lines = ["LA MEJOR SOLUCIÓN", "PARA TU TEXTO"]
    w = max(_text_width(s, size) for s in lines) + 2 * size * 0.34
    x = 960 - w / 2
    frame = Box(x - 40, 400, w + 80, 2 * size * 1.6 + 70)
    path(t, t.track("shape", "Marco"), WHITE, 0.2, end - 0.2, frame, "M 0 0 L 100 0 L 100 100 L 0 100 Z", 5,
         draw=(0, 0.7), erase=(end - 0.2 - 0.45, 0.35))
    for i, s in enumerate(lines):
        _box_line(t, s, x + size * 0.34, frame.y + 35 + i * size * 1.6, size, WHITE, INK, 0.6 + i * 0.3, end - 0.1,
                  name=f"Línea {i + 1}")
    return t


def titulo_cuadro_vertical():
    """A white square at the right: «¿CÓMO HAGO UN BUEN VIDEO?» in black, «VER SIGUIENTE» standing along its left side
    in coral."""
    D = 5.0
    t = _kit("titulo-cuadro-vertical", "Pregunta en un cuadro blanco", "Question in a white square", "titulos-estilo", D,
             8437, ["título", "cuadro", "pregunta", "vertical"], thumb_at=2.4)
    photo_bg(t, "h-nature-03", s1=1.04, label="Tu video")
    end = D - 0.3
    sq = Box(1380, 560, 400, 400)
    rrect(t, t.track("shape", "Cuadro"), WHITE, 0.3, end - 0.3, sq, radius=0,
          motion=[(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (end - 0.65, {}, "in"), (end - 0.3, {"s": 0.0})],
          layers=_sh(WHITE))
    txt(t, "¿CÓMO HAGO\nUN BUEN\nVIDEO?", Box(sq.x + 40, sq.y + 40, sq.w - 80, sq.h - 80), 56, 0.6, end - 0.8,
        colour=INK, weight=900, align="left", anim="rise", ad=0.4, name="Pregunta", line=1.05)
    label(t, t.track("text", "Textos"), "VER SIGUIENTE", 0.8, end - 1.0, centered(sq.x - 34, sq.cy, sq.h, 50), FONT, 32,
          WHITE, weight=900, spacing=3, anim_in=tanim("fade", duration=0.35), anim_out=OUT(0.2), name="Etiqueta",
          rotation=keys([(0, -90.0)]), box_bg=(CORAL, 1.0), box_pad=12)
    return t


def titulo_mixto():
    """Three lines with mixed weights — «Buen diseño / para tus / títulos de YouTube.» — sliding in, a coral square
    after the last word."""
    D = 5.0
    t = _kit("titulo-mixto", "Título con pesos mezclados", "Mixed-weight title", "titulos-estilo", D, 8438,
             ["título", "tipografía", "mezcla", "elegante"], thumb_at=2.4)
    photo_bg(t, "h-autumn-02", s1=1.04, label="Tu video")
    end = D - 0.3
    rows = [("Buen diseño", 86, 900), ("para tus", 56, 500), ("títulos de YouTube.", 86, 900)]
    y = 250
    for i, (s, size, weight) in enumerate(rows):
        a = 0.3 + i * 0.2
        txt(t, s, Box(120, y, 1300, size * 1.25), size, a, end - a, weight=weight, align="left", anim="slide-left",
            ad=0.45, name=f"Línea {i + 1}", layers=_shade())
        y += size * 1.2
    last = _text_width("títulos de YouTube.", 86)
    t.solid(t.track("shape", "Punto"), CORAL, 1.1, end - 1.1, Box(120 + last + 26, y - 86 * 1.2 + 30, 30, 30),
            _life(end - 1.1))
    return t


def titulo_numero():
    """A coral circle with a number pops, then a white pill with the title slides out of it."""
    D = 5.0
    t = _kit("titulo-numero", "Título con número", "Numbered title", "titulos-estilo", D, 8439,
             ["título", "número", "píldora", "lista"], thumb_at=2.4)
    photo_bg(t, "h-desk-05", s1=1.04, label="Tu video")
    end = D - 0.3
    cx, cy = 1050, 900
    size = 36
    text = "TÍTULOS LIMPIOS Y MODERNOS"
    w = _text_width(text, size) + size * 1.6 + 50
    strip = Box(cx, cy - 38, w, 76)
    t.solid(t.track("shape", "Píldora"), WHITE, 0.5, end - 0.5, strip,
            [(0, {"sx": 0.0, "dx": -w / 2}, "out"), (0.4, {}, "hold"), (end - 0.5 - 0.3, {}, "in"),
             (end - 0.5, {"sx": 0.0, "dx": -w / 2})], radius=38, kind="rounded-rectangle", layers=_sh(WHITE))
    txt(t, text, Box(cx + 60, cy - 38, w - 70, 76), size, 0.7, end - 0.8, colour=INK, weight=900, align="left",
        name="Título")
    t.solid(t.track("shape", "Número"), CORAL, 0.3, end - 0.3, centered(cx, cy, 110, 110), _life(end - 0.3),
            kind="ellipse", layers=_sh(CORAL))
    txt(t, "1", centered(cx, cy, 110, 110), 56, 0.4, end - 0.5, weight=900, name="Número")
    return t


def suscribete_ahora():
    """«¡SUSCRÍBETE AHORA / EN MI CANAL!» typed out big and centred over the video."""
    D = 5.0
    t = _kit("titulo-suscribete-ahora", "¡Suscríbete ahora!", "Subscribe now!", "titulos-estilo", D, 8440,
             ["título", "suscríbete", "grande", "centrado"], thumb_at=2.8)
    photo_bg(t, "h-city-04", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.4, 0.25)]))
    txt(t, "¡SUSCRÍBETE AHORA\nEN MI CANAL!", Box(160, 400, 1600, 260), 100, 0.3, D - 0.6, weight=900,
        anim="typewriter", ad=1.2, name="Título", layers=_shade(), line=1.05)
    return t


def gracias_grande():
    """The pack's last frame: «¡GRACIAS POR VER!» big over the video, each letter popping, a coral line drawn under."""
    D = 5.0
    t = _kit("gracias-grande", "¡Gracias por ver! grande", "Big thanks for watching", "frases", D, 8441,
             ["gracias", "final", "grande", "despedida"], thumb_at=2.6)
    photo_bg(t, "h-sport-02", s1=1.04, label="Tu video")
    size = 120
    w = _text_width("¡GRACIAS POR VER!", size)
    txt(t, "¡GRACIAS POR VER!", Box(960 - w / 2 - 40, 440, w + 80, 170), size, 0.3, D - 0.6, weight=900, anim="pop",
        ad=0.6, name="Título", layers=_shade())
    path(t, t.track("shape", "Línea"), CORAL, 0.8, D - 1.1, Box(960 - w * 0.3, 625, w * 0.6, 20), "M 0 50 L 100 50", 14,
         draw=(0, 0.5), erase=(D - 1.1 - 0.4, 0.3), ease="out")
    return t


# --- The video in a circle --------------------------------------------------------------------------------------------

def video_circulo():
    """A coral screen; the video comes in inside a big circle with a white ring, which grows a little and then shrinks
    away (the pack's circle between two clips)."""
    D = 4.5
    t = _kit("video-circulo", "Video en un círculo", "Video in a circle", "transiciones", D, 8442,
             ["círculo", "coral", "transición", "video"], thumb_at=2.0)
    t.solid(t.track("shape", "Fondo"), CORAL, 0.0, D, None)
    d = 860
    m = [(0, {"s": 0.0}, "back"), (0.6, {}, "inout"), (D - 0.9, {"s": 1.06}, "in"), (D - 0.3, {"s": 0.0})]
    circle_photo(t, "h-travel-05", 0.2, D - 0.2, centered(960, 540, d, d), m, ring_colour=WHITE, ring_width=22,
                 label="Tu video")
    return t


# --- Socials ----------------------------------------------------------------------------------------------------------

def _logo_on(t, net, cx, cy, size, a, dur, colour):
    if net == "youtube":
        yt_icon(t, cx, cy, size * 1.15, a, dur, colour=colour, play=COLOURS["youtube"] if colour == WHITE else WHITE)
    else:
        logo(t, net, cx, cy, size, a, dur, colour=colour)


def redes_insignia():
    """A square badge in the platform's own colour with its logo in white, the handle in a white pill beside it and a
    tilted coral «SÍGUEME» under."""
    D = 10.0
    t = _kit("redes-insignia", "Redes con insignia de color", "Socials with a colour badge", "redes", D, 8443,
             ["redes", "insignia", "sígueme", "logos"], thumb_at=1.6)
    photo_bg(t, "h-portrait-06", s1=1.04, label="Tu video")

    def draw(i, net, handle, a, dur):
        cx, cy = 190, 930
        rrect(t, t.track("shape", "Insignia"), COLOURS[net], a, dur, centered(cx, cy, 100, 100), radius=18,
              motion=_life(dur), layers=_sh(COLOURS[net]))
        _logo_on(t, net, cx, cy, 52, a + 0.1, dur - 0.2, WHITE)
        w = _text_width(handle, 34) + 34 * 1.2
        strip = Box(cx + 64, cy - 34, w, 68)
        t.solid(t.track("shape", "Píldora"), WHITE, a + 0.2, dur - 0.35, strip,
                [(0, {"sx": 0.0, "dx": -w / 2}, "out"), (0.35, {}, "hold"), (dur - 0.65, {}, "in"),
                 (dur - 0.35, {"sx": 0.0, "dx": -w / 2})], layers=_sh(WHITE))
        txt(t, handle, strip, 34, a + 0.35, dur - 0.5, colour=INK, weight=800, name=f"Usuario {i + 1}")
        tag = centered(cx + 64 + w - 70, cy + 58, 170, 44)
        rot = keys([(0, -5.0)])
        t.solid(t.track("shape", "Sígueme"), CORAL, a + 0.4, dur - 0.55, tag, _life(dur - 0.55), rotation=rot)
        label(t, t.track("text", "Textos"), "SÍGUEME", a + 0.45, dur - 0.6, tag, FONT, 26, WHITE, weight=900, spacing=2,
              anim_in=tanim("fade", duration=0.2), anim_out=OUT(0.2), name=f"Sígueme {i + 1}", rotation=rot)
    _cycle(t, D, draw)
    return t


def redes_corchetes():
    """A white card with thick ends in the platform's colour, like brackets; the logo and the handle inside."""
    D = 10.0
    t = _kit("redes-corchetes", "Redes entre corchetes", "Socials between brackets", "redes", D, 8444,
             ["redes", "tarjeta", "corchetes", "logos"], thumb_at=1.6)
    photo_bg(t, "h-sport-03", s1=1.04, label="Tu video")

    def draw(i, net, handle, a, dur):
        w = _text_width(handle, 34) + 140
        card = Box(150, 890, w, 84)
        _wipe_box(t, card.x, card.y, card.w, card.h, WHITE, a, dur, name="Tarjeta")
        for side in (0, 1):
            x = card.x - 6 if side == 0 else card.x + card.w - 10
            t.solid(t.track("shape", "Corchetes"), COLOURS[net], a + 0.15, dur - 0.3, Box(x, card.y - 10, 16, card.h + 20),
                    [(0, {"sy": 0.0}, "out"), (0.3, {}, "hold"), (dur - 0.55, {}, "in"), (dur - 0.3, {"sy": 0.0})])
        _logo_on(t, net, card.x + 56, card.y + 42, 44, a + 0.25, dur - 0.4, COLOURS[net])
        txt(t, handle, Box(card.x + 96, card.y, w - 100, card.h), 34, a + 0.3, dur - 0.45, colour=INK, weight=800,
            align="left", name=f"Usuario {i + 1}")
    _cycle(t, D, draw)
    return t


def redes_circulo_marca():
    """The logo in its own colour on a white circle; the handle in big white type beside it and «SÍGUEME» in coral."""
    D = 10.0
    t = _kit("redes-circulo-marca", "Redes con logo en círculo", "Socials with a logo in a circle", "redes", D, 8445,
             ["redes", "círculo", "sígueme", "logos"], thumb_at=1.6)
    photo_bg(t, "h-nature-02", s1=1.04, label="Tu video")

    def draw(i, net, handle, a, dur):
        cx, cy = 190, 930
        t.solid(t.track("shape", "Círculo"), WHITE, a, dur, centered(cx, cy, 104, 104), _life(dur), kind="ellipse",
                layers=_sh(WHITE))
        _logo_on(t, net, cx, cy, 52, a + 0.1, dur - 0.2, COLOURS[net])
        txt(t, handle, Box(cx + 76, cy - 52, 700, 64), 46, a + 0.25, dur - 0.4, weight=900, align="left",
            anim="slide-left", ad=0.35, name=f"Usuario {i + 1}", layers=_shade())
        txt(t, "SÍGUEME", Box(cx + 78, cy + 12, 400, 44), 28, a + 0.4, dur - 0.55, colour=CORAL, weight=900, spacing=3,
            align="left", name=f"Sígueme {i + 1}", layers=_shade(CORAL))
    _cycle(t, D, draw)
    return t


TEMPLATES = [intro_historia, intro_blog, intro_inclinado, intro_pildora, ver_siguiente, titulo_cuadro_contorno,
             titulo_marco_cajas, titulo_cuadro_vertical, titulo_mixto, titulo_numero, suscribete_ahora, gracias_grande,
             video_circulo, redes_insignia, redes_corchetes, redes_circulo_marca]
