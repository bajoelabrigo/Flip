"""Kit de YouTube, batch k (2026-10-30): the titles, lower thirds and social strips left from Jorge's «pack youtube
6», almost the same and our own (see templates_ytkit_i/j): white or black boxes behind the type, outlined frames,
a tilted label, names with their role, the user's handles with the platforms' official logos. Order 8330-8399.
"""

from __future__ import annotations

from brand_logos import LOGOS
from kit import Box, centered, fill, keys, label, no_stroke, outline, photo_bg, rrect, shadow, tanim, wide
from templates_ytkit_a import OUT, _stroke, path
from templates_ytkit_i import _box_line, _text_width
from templates_ytkit_j import CORAL, INK, WHITE, _hollow, _life, yt_icon

FONT = "Montserrat"


def _kit(id, es, en, section, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _line_text(t, content, box, size, t0, dur, colour=WHITE, weight=800, align="left", anim="rise", ad=0.4, name=None,
               box_bg=None, pad=0.0, shadowed=True, italic=False, spacing=0):
    st_layers = [shadow("#000000", 0, 3, 12, 0.35), fill(colour)] if shadowed and not box_bg else [fill(colour)]
    c = label(t, t.track("text", "Textos"), content, t0, dur, box, FONT, size, colour, weight=weight, align=align,
              anim_in=tanim(anim, duration=ad, **({"angle": 0, "softness": 0.0} if anim == "wipe" else {})),
              anim_out=OUT(0.25), name=name or content, layers=st_layers, box_bg=box_bg, box_pad=pad, italic=italic,
              spacing=spacing)
    if box_bg:
        c["textStyle"]["boxStyle"] = "line"
        c["textStyle"]["boxPaddingX"] = pad
        c["textStyle"]["boxPaddingY"] = size * 0.16
    return c


def _wipe_box(t, x, y, w, h, colour, t0, dur, name="Caja"):
    """A box that opens from its left edge and closes to its right one."""
    t.solid(t.track("shape", name), colour, t0, dur, Box(x, y, w, h),
            [(0, {"sx": 0.0, "dx": -w / 2}, "out"), (0.35, {}, "hold"), (dur - 0.3, {}, "in"),
             (dur, {"sx": 0.0, "dx": w / 2})])


# --- Titles --------------------------------------------------------------------------------------------------------

def mejor_video():
    """A coral line draws across, «MEJOR VIDEO» rises out of it, and «EN YOUTUBE» lands in a coral box under it."""
    D = 5.0
    t = _kit("titulo-mejor-video", "Mejor video en YouTube", "Best video on YouTube", "titulos-estilo", D, 8330,
             ["título", "línea", "caja", "mejor video"], thumb_at=2.5)
    photo_bg(t, "h-travel-02", s1=1.04, label="Tu video")
    end = D - 0.3
    t.solid(t.track("shape", "Línea"), CORAL, 0.2, 0.9, centered(960, 520, 520, 6),
            [(0, {"sx": 0.0}, "out"), (0.5, {}, "hold"), (0.9, {"sx": 0.0})])
    _line_text(t, "MEJOR VIDEO", Box(460, 430, 1000, 90), 76, 0.6, end - 0.6, align="center", anim="rise", ad=0.45,
               name="Línea 1")
    w = _text_width("EN YOUTUBE", 76) + 76 * 0.7
    t.solid(t.track("shape", "Caja"), CORAL, 1.0, end - 1.0, centered(960, 572, w, 104),
            [(0, {"sx": 0.0}, "out"), (0.35, {}, "hold"), (end - 1.3, {}, "in"), (end - 1.0, {"sx": 0.0})])
    _line_text(t, "EN YOUTUBE", centered(960, 572, 1000, 104), 76, 1.15, end - 1.2, align="center", anim="fade", ad=0.3,
               name="Línea 2", shadowed=False)
    return t


def mejor_show_logo():
    """The YouTube icon pops beside two left-aligned lines: «EL MEJOR SHOW / EN YOUTUBE.»"""
    D = 5.0
    t = _kit("titulo-mejor-show", "El mejor show en YouTube", "The best show on YouTube", "titulos-estilo", D, 8331,
             ["título", "logo", "show"], thumb_at=2.4)
    photo_bg(t, "h-sport-01", s1=1.04, label="Tu video")
    end = D - 0.3
    yt_icon(t, 620, 470, 110, 0.3, end - 0.3)
    _line_text(t, "EL MEJOR SHOW", Box(700, 400, 1000, 80), 72, 0.55, end - 0.55, anim="wipe", ad=0.5, name="Línea 1")
    _line_text(t, "EN YOUTUBE.", Box(700, 474, 1000, 80), 72, 0.8, end - 0.8, anim="wipe", ad=0.5, name="Línea 2")
    return t


def barra_nuevo_video():
    """A black bar slides open with «EL NUEVO VIDEO YA SALIÓ» in small caps, then «¡MÍRALO YA!» types in under it,
    underlined."""
    D = 5.0
    t = _kit("titulo-nuevo-video", "El nuevo video ya salió", "The new video is out", "titulos-estilo", D, 8332,
             ["título", "barra", "nuevo video", "estreno"], thumb_at=2.6)
    photo_bg(t, "h-nature-05", s1=1.04, label="Tu video")
    end = D - 0.3
    _wipe_box(t, 520, 400, 880, 64, INK, 0.3, end - 0.3, name="Barra")
    _line_text(t, "EL NUEVO VIDEO YA SALIÓ", Box(520, 400, 880, 64), 34, 0.6, end - 0.7, align="center", anim="fade",
               ad=0.3, name="Barra", shadowed=False, spacing=2)
    _line_text(t, "¡MÍRALO YA!", Box(560, 480, 800, 80), 58, 1.0, end - 1.0, align="center", anim="typewriter", ad=0.5,
               name="Llamado")
    t.solid(t.track("shape", "Subrayado"), WHITE, 1.5, end - 1.5, centered(960, 562, _text_width("¡MÍRALO YA!", 58), 5),
            [(0, {"sx": 0.0}, "out"), (0.35, {}, "hold"), (end - 1.8, {}, "in"), (end - 1.5, {"sx": 0.0})])
    return t


def cuadro_contorno():
    """A white outlined square draws itself; inside it «TÍTULOS / LIMPIOS / PARA TU / CANAL» rise line by line."""
    D = 5.0
    t = _kit("titulo-cuadro", "Título en un cuadro", "Title in a square", "titulos-estilo", D, 8333,
             ["título", "cuadro", "contorno", "minimalista"], thumb_at=2.6)
    photo_bg(t, "h-beach-01", s1=1.04, label="Tu video")
    end = D - 0.3
    sq = centered(560, 540, 380, 380)
    outline(t, t.track("shape", "Cuadro"), WHITE, 8, 0.3, end - 0.3, sq, _life(end - 0.3, s0=0.6))
    for i, word in enumerate(["TÍTULOS", "LIMPIOS", "PARA TU", "CANAL"]):
        a = 0.6 + i * 0.15
        _line_text(t, word, Box(sq.x, sq.y + 60 + i * 66, sq.w, 70), 54, a, end - a, align="center", anim="rise",
                   ad=0.4, name=f"Línea {i + 1}")
    return t


def linea_vertical():
    """A white vertical line grows at the left; «MODERNO / Y / UNIVERSAL.» slides out from behind it."""
    D = 5.0
    t = _kit("titulo-linea-vertical", "Título con línea vertical", "Title with a vertical line", "titulos-estilo", D,
             8334, ["título", "línea", "vertical", "minimalista"], thumb_at=2.4)
    photo_bg(t, "h-studio-01", s1=1.04, label="Tu video")
    end = D - 0.3
    t.solid(t.track("shape", "Línea"), WHITE, 0.3, end - 0.3, Box(200, 690, 6, 200),
            [(0, {"sy": 0.0, "dy": 100}, "out"), (0.4, {}, "hold"), (end - 0.6, {}, "in"), (end - 0.3, {"sy": 0.0, "dy": 100})])
    for i, word in enumerate(["MODERNO", "Y", "UNIVERSAL."]):
        a = 0.6 + i * 0.12
        _line_text(t, word, Box(232, 690 + i * 64, 900, 70), 58, a, end - a, anim="slide-right", ad=0.4,
                   name=f"Línea {i + 1}")
    return t


def promo_grande():
    """«TU PROMO» huge in a black box that opens from the middle, «PACK» under it."""
    D = 5.0
    t = _kit("titulo-promo", "Título grande en caja negra", "Big title in a black box", "titulos-estilo", D, 8335,
             ["título", "caja", "grande", "promo"], thumb_at=2.4)
    photo_bg(t, "h-city-05", s1=1.04, label="Tu video")
    end = D - 0.3
    w = _text_width("TU PROMO", 130) + 130 * 0.8
    t.solid(t.track("shape", "Caja"), INK, 0.3, end - 0.3, centered(960, 490, w, 176),
            [(0, {"sx": 0.0}, "out"), (0.45, {}, "hold"), (end - 0.65, {}, "in"), (end - 0.3, {"sx": 0.0})])
    _line_text(t, "TU PROMO", centered(960, 490, 1600, 160), 130, 0.55, end - 0.6, align="center", anim="fade", ad=0.3,
               name="Título", shadowed=False)
    _line_text(t, "PACK", centered(960, 610, 800, 60), 44, 0.9, end - 0.9, align="center", anim="rise", ad=0.35,
               name="Subtítulo", spacing=6)
    return t


def tres_cajas_negras():
    """Three lines in black boxes, left aligned, each opening with a coral cursor (as the white box titles)."""
    D = 6.0
    t = _kit("titulo-tres-cajas", "Tres líneas en cajas negras", "Three lines in black boxes", "titulos-estilo", D,
             8336, ["título", "cajas", "negro", "pregunta"], thumb_at=2.8)
    photo_bg(t, "h-cooking-02", s1=1.04, label="Tu video")
    lines = ["HEMOS CREADO", "UNA GRAN SOLUCIÓN PARA TI", "¿QUIERES PROBARLA?"]
    for i, text in enumerate(lines):
        _box_line(t, text, 160, 290 + i * 92, 54, WHITE, INK, 0.3 + i * 0.4, D - 0.4 - (2 - i) * 0.1, name=f"Línea {i + 1}")
    return t


def etiqueta_inclinada():
    """A white label tilted up a little with «Motion design» in black, and a small «Por tu nombre» under it."""
    D = 5.0
    t = _kit("titulo-inclinado", "Etiqueta inclinada", "Tilted label", "titulos-estilo", D, 8337,
             ["título", "inclinado", "etiqueta", "firma"], thumb_at=2.4)
    photo_bg(t, "h-sport-02", s1=1.04, label="Tu video")
    end = D - 0.3
    w = _text_width("Motion design", 84) + 84 * 0.8
    box = centered(960, 500, w, 124)
    rot = keys([(0, -6.0)])
    t.solid(t.track("shape", "Etiqueta"), WHITE, 0.3, end - 0.3, box,
            [(0, {"sx": 0.0}, "back"), (0.45, {}, "hold"), (end - 0.65, {}, "in"), (end - 0.3, {"sx": 0.0})], rotation=rot,
            layers=[shadow("#000000", 0, 8, 22, 0.3), fill(WHITE), no_stroke()])
    label(t, t.track("text", "Textos"), "Motion design", 0.5, end - 0.6, box, FONT, 84, INK, weight=800,
          anim_in=tanim("fade", duration=0.3), anim_out=OUT(0.2), name="Título", rotation=rot)
    label(t, t.track("text", "Textos"), "Por tu nombre", 0.9, end - 1.0, Box(1030, 560, 340, 50), FONT, 32, WHITE,
          weight=700, align="right", anim_in=tanim("slide-left", duration=0.35), anim_out=OUT(0.2), name="Firma",
          rotation=rot, layers=[shadow("#000000", 0, 3, 10, 0.5), fill(WHITE)])
    return t


def centrado_cajas():
    """«NO OLVIDES / SUSCRIBIRTE / Y DAR LIKE» centred, each line in a white box, one after another."""
    D = 5.0
    t = _kit("titulo-no-olvides", "No olvides suscribirte y dar like", "Don't forget to subscribe and like",
             "titulos-estilo", D, 8338, ["título", "cajas", "suscríbete", "centrado"], thumb_at=2.6)
    photo_bg(t, "h-portrait-06", s1=1.04, label="Tu video")
    end = D - 0.3
    for i, text in enumerate(["NO OLVIDES", "SUSCRIBIRTE", "Y DAR LIKE"]):
        a = 0.3 + i * 0.3
        _line_text(t, text, centered(960, 420 + i * 96, 1400, 90), 64, a, end - a - (2 - i) * 0.08, colour=INK,
                   align="center", anim="pop", ad=0.35, name=f"Línea {i + 1}", box_bg=(WHITE, 1.0), pad=18)
    return t


def contorno_doble():
    """«DISFRUTA» and «Y USA ESTE PACK» in white outlined boxes (no fill), the frames drawing round the type."""
    D = 5.0
    t = _kit("titulo-contorno", "Título en marcos de contorno", "Title in outlined frames", "titulos-estilo", D, 8339,
             ["título", "contorno", "marco"], thumb_at=2.6)
    photo_bg(t, "h-city-05", s1=1.04, label="Tu video")
    end = D - 0.3
    for i, (text, size) in enumerate([("DISFRUTA", 54), ("Y USA ESTE PACK", 54)]):
        a = 0.3 + i * 0.3
        w = _text_width(text, size) + size * 0.9
        box = centered(960, 460 + i * 98, w, 88)
        outline(t, t.track("shape", "Marcos"), WHITE, 4, a, end - a, box, _life(end - a, s0=0.85))
        _line_text(t, text, box, size, a + 0.15, end - a - 0.2, align="center", anim="fade", ad=0.3, name=f"Línea {i + 1}")
    return t


def gracias_apoyo():
    """«¡GRACIAS POR TU APOYO!» in a white box, and «Nuevo video muy pronto» small under it."""
    D = 5.0
    t = _kit("titulo-gracias-apoyo", "¡Gracias por tu apoyo!", "Thank you for your support!", "frases", D, 8340,
             ["gracias", "apoyo", "caja"], thumb_at=2.4)
    photo_bg(t, "h-nature-01", s1=1.04, label="Tu video")
    end = D - 0.3
    _line_text(t, "¡GRACIAS POR TU APOYO!", centered(960, 500, 1600, 90), 66, 0.3, end - 0.3, colour=INK, align="center",
               anim="wipe", ad=0.6, name="Gracias", box_bg=(WHITE, 1.0), pad=22)
    _line_text(t, "NUEVO VIDEO MUY PRONTO", centered(960, 572, 1200, 50), 28, 0.9, end - 0.9, align="center",
               anim="fade", ad=0.4, name="Subtítulo", spacing=3)
    return t


# --- Lower thirds -----------------------------------------------------------------------------------------------------

def _tercio(t, style, end):
    x, y = 150, 830
    if style == "blanca":
        w = _text_width("NOMBRE APELLIDO", 46) + 46 * 0.8
        _wipe_box(t, x, y, w, 72, WHITE, 0.3, end - 0.3)
        _line_text(t, "NOMBRE APELLIDO", Box(x, y, w, 72), 46, 0.55, end - 0.65, colour=INK, align="center", anim="fade",
                   ad=0.3, name="Nombre", shadowed=False)
    elif style == "coral":
        w = _text_width("NOMBRE APELLIDO", 46) + 46 * 0.8
        _wipe_box(t, x, y, w, 72, CORAL, 0.3, end - 0.3)
        _line_text(t, "NOMBRE APELLIDO", Box(x, y, w, 72), 46, 0.55, end - 0.65, align="center", anim="fade", ad=0.3,
                   name="Nombre", shadowed=False)
    else:
        t.solid(t.track("shape", "Línea"), WHITE, 0.3, end - 0.3, Box(x, y - 4, 6, 120),
                [(0, {"sy": 0.0}, "out"), (0.35, {}, "hold"), (end - 0.6, {}, "in"), (end - 0.3, {"sy": 0.0})])
        _line_text(t, "NOMBRE APELLIDO", Box(x + 26, y, 900, 64), 46, 0.5, end - 0.6, anim="slide-right", ad=0.4,
                   name="Nombre")
    _line_text(t, "TU PROFESIÓN", Box(x + (26 if style == "linea" else 20), y + 80, 700, 40), 26, 0.8, end - 0.9,
               anim="fade", ad=0.35, name="Profesión", spacing=2)


def tercio_blanco():
    D = 6.0
    t = _kit("tercio-caja-blanca", "Nombre en caja blanca", "Name in a white box", "tercios", D, 8341,
             ["tercio", "nombre", "profesión", "caja"], thumb_at=2.0)
    photo_bg(t, "h-man-02", s1=1.04, label="Tu video")
    _tercio(t, "blanca", D - 0.3)
    return t


def tercio_coral():
    D = 6.0
    t = _kit("tercio-caja-coral", "Nombre en caja coral", "Name in a coral box", "tercios", D, 8342,
             ["tercio", "nombre", "profesión", "coral"], thumb_at=2.0)
    photo_bg(t, "h-portrait-05", s1=1.04, label="Tu video")
    _tercio(t, "coral", D - 0.3)
    return t


def tercio_linea():
    D = 6.0
    t = _kit("tercio-linea", "Nombre con línea", "Name with a line", "tercios", D, 8343,
             ["tercio", "nombre", "profesión", "línea"], thumb_at=2.0)
    photo_bg(t, "h-portrait-04", s1=1.04, label="Tu video")
    _tercio(t, "linea", D - 0.3)
    return t


# --- Socials with the official logos ------------------------------------------------------------------------------------

NETS = [("facebook", "/tupagina"), ("instagram", "@tuusuario"), ("x", "@tuusuario"), ("youtube", "@tucanal")]


def _cycle(t, D, draw):
    slot = (D - 0.3) / len(NETS)
    for i, (net, handle) in enumerate(NETS):
        draw(i, net, handle, 0.3 + i * slot, slot - 0.1)


def redes_tarjeta():
    """A white card along the bottom with a coral edge on the left, the platform's logo, the handle and «SÍGUEME»;
    the four platforms one after another."""
    D = 10.0
    t = _kit("redes-tarjeta", "Redes en tarjeta blanca", "Socials on a white card", "redes", D, 8344,
             ["redes", "tarjeta", "sígueme", "logos"], thumb_at=1.6)
    photo_bg(t, "h-city-02", s1=1.04, label="Tu video")

    def draw(i, net, handle, a, dur):
        card = Box(120, 900, 460, 92)
        _wipe_box(t, card.x, card.y, card.w, card.h, WHITE, a, dur, name="Tarjeta")
        t.solid(t.track("shape", "Borde"), CORAL, a, dur, Box(card.x, card.y, 12, card.h),
                [(0, {"sy": 0.0}, "out"), (0.3, {}, "hold"), (dur - 0.25, {}, "in"), (dur, {"sy": 0.0})])
        if net == "youtube":
            yt_icon(t, card.x + 62, card.y + 46, 56, a + 0.2, dur - 0.35)
        else:
            logo(t, net, card.x + 62, card.y + 46, 48, a + 0.2, dur - 0.35, colour=INK)
        _line_text(t, handle, Box(card.x + 104, card.y + 10, 340, 46), 34, a + 0.3, dur - 0.45, colour=INK, anim="fade",
                   ad=0.25, name=f"Usuario {i + 1}", shadowed=False)
        _line_text(t, "SÍGUEME", Box(card.x + 106, card.y + 54, 200, 28), 20, a + 0.4, dur - 0.55, colour=CORAL,
                   anim="fade", ad=0.25, name=f"Sígueme {i + 1}", shadowed=False, spacing=3)
    _cycle(t, D, draw)
    return t


def logo(t, name, cx, cy, size, t0, dur, colour=WHITE, motion=None):
    path(t, t.track("shape", "Logos"), colour, t0, dur, centered(cx, cy, size, size), LOGOS[name], filled=True,
         motion=motion if motion is not None else _life(dur))


def redes_circulo():
    """The logo in a white circle with a coral ring, and the handle in a white pill sliding out of it."""
    D = 10.0
    t = _kit("redes-circulo", "Redes en círculo y píldora", "Socials in a circle and pill", "redes", D, 8345,
             ["redes", "círculo", "píldora", "logos"], thumb_at=1.6)
    photo_bg(t, "h-portrait-03", s1=1.04, label="Tu video")

    def draw(i, net, handle, a, dur):
        cx, cy = 200, 940
        strip = Box(cx, cy - 34, 420, 68)
        t.solid(t.track("shape", "Píldora"), WHITE, a + 0.25, dur - 0.4, strip,
                [(0, {"sx": 0.0, "dx": -210}, "out"), (0.35, {}, "hold"), (dur - 0.7, {}, "in"),
                 (dur - 0.4, {"sx": 0.0, "dx": -210})], radius=34, kind="rounded-rectangle")
        t.solid(t.track("shape", "Círculo"), CORAL, a, dur, centered(cx, cy, 110, 110), _life(dur), kind="ellipse")
        t.solid(t.track("shape", "Círculo"), WHITE, a, dur, centered(cx, cy, 96, 96), _life(dur), kind="ellipse")
        if net == "youtube":
            yt_icon(t, cx, cy, 54, a + 0.1, dur - 0.2)
        else:
            logo(t, net, cx, cy, 46, a + 0.1, dur - 0.2, colour=CORAL)
        _line_text(t, handle, Box(cx + 70, cy - 30, 340, 60), 34, a + 0.5, dur - 0.75, colour=INK, anim="fade",
                   ad=0.25, name=f"Usuario {i + 1}", shadowed=False)
    _cycle(t, D, draw)
    return t


BRUSH = ("M 2 40 C 10 20 30 18 50 22 C 70 26 88 14 98 30 C 100 45 96 60 99 72 C 90 86 70 78 50 82 "
         "C 30 86 12 90 3 76 C 0 62 4 52 2 40 Z")


def redes_pincel():
    """A coral brush stroke sweeps in along the bottom; the white logo and the handle ride on it."""
    D = 10.0
    t = _kit("redes-pincel", "Redes en trazo de pincel", "Socials on a brush stroke", "redes", D, 8346,
             ["redes", "pincel", "trazo", "logos"], thumb_at=1.6)
    photo_bg(t, "h-sport-01", s1=1.04, label="Tu video")

    def draw(i, net, handle, a, dur):
        stroke = Box(100, 890, 560, 110)
        path(t, t.track("shape", "Pincel"), CORAL, a, dur, stroke, BRUSH, filled=True,
             motion=[(0, {"sx": 0.0, "dx": -280}, "out"), (0.4, {}, "hold"), (dur - 0.3, {}, "in"),
                     (dur, {"sx": 0.0, "dx": 280})])
        if net == "youtube":
            yt_icon(t, 175, 945, 54, a + 0.25, dur - 0.4, colour=WHITE, play=CORAL)
        else:
            logo(t, net, 175, 945, 46, a + 0.25, dur - 0.4)
        _line_text(t, handle, Box(220, 915, 420, 60), 38, a + 0.35, dur - 0.55, anim="fade", ad=0.25,
                   name=f"Usuario {i + 1}", shadowed=False)
    _cycle(t, D, draw)
    return t


TEMPLATES = [mejor_video, mejor_show_logo, barra_nuevo_video, cuadro_contorno, linea_vertical, promo_grande,
             tres_cajas_negras, etiqueta_inclinada, centrado_cajas, contorno_doble, gracias_apoyo, tercio_blanco,
             tercio_coral, tercio_linea, redes_tarjeta, redes_circulo, redes_pincel]
