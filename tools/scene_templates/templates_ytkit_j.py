"""Kit de YouTube, batch j (2026-10-30): the rest of Jorge's «pack youtube 6», almost the same and our own (see
templates_ytkit_i). With the platforms' official logos (brand_logos.py, Jorge: «sí pon los logos oficiales»):
the YouTube icon in its own red where the pack shows it, the social glyphs in white beside the handles. The
pack's red backgrounds are our coral. Every text and picture editable. Order 8310-8399.
"""

from __future__ import annotations

import math
import random

from brand_logos import LOGOS
from kit import Box, centered, circle_photo, fill, gradient, keys, label, no_stroke, photo_bg, pill, rrect, shadow, tanim, wide
from templates_ytkit_a import BELL, OUT, _stroke, path
from templates_ytkit_f import THUMB

CORAL = "#FF4F64"
CORAL_DARK = "#D93A50"
CORAL_DEEP = "#B82A40"
WHITE = "#FFFFFF"
INK = "#121212"
YT_RED = "#FF0000"  # the YouTube icon's own colour (its brand guidelines)
FONT = "Montserrat"
D_INTRO = 5.0

YT_PLAY = "M 39.77 64.87 L 39.77 35.13 L 65.91 50 Z"


def _kit(id, es, en, section, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + tags, **kw)


def _life(dur, fin=0.45, fout=0.35, s0=0.0):
    return [(0, {"s": s0}, "back"), (fin, {}, "hold"), (dur - fout, {}, "in"), (dur, {"s": 0.0})]


def _hollow():
    return {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def yt_icon(t, cx, cy, w, t0, dur, motion=None, colour=YT_RED, play=WHITE):
    """The YouTube icon as its guidelines draw it: the red shape with the white play triangle. The triangle is
    the official outline's own hole, with a square of its colour hidden behind: drawn as a separate small shape
    it wobbled against the red one as it grew (Jorge, 2026-10-30: «solo tiembla el logo de YouTube»)."""
    box = centered(cx, cy, w, w)
    m = motion if motion is not None else _life(dur)
    t.solid(t.track("shape", "Logo de YouTube"), play, t0, dur, centered(cx, cy, w * 0.44, w * 0.44), m)
    path(t, t.track("shape", "Logo de YouTube"), colour, t0, dur, box, LOGOS["youtube"], filled=True, motion=m)


def logo(t, name, cx, cy, size, t0, dur, colour=WHITE, motion=None):
    path(t, t.track("shape", "Logos"), colour, t0, dur, centered(cx, cy, size, size), LOGOS[name], filled=True,
         motion=motion if motion is not None else _life(dur))


def txt(t, content, box, size, t0, dur, colour=WHITE, weight=800, align="center", anim="fade", ad=0.35,
        name=None, motion=None, spacing=0, line=1.05, layers=None, box_bg=None, box_pad=12):
    return label(t, t.track("text", "Textos"), content, t0, dur, box, FONT, size, colour, weight=weight, align=align,
                 anim_in=tanim(anim, duration=ad, **({"angle": 0, "softness": 0.1} if anim == "wipe" else {})),
                 anim_out=OUT(0.25), name=name or content, motion=motion,
                 spacing=spacing, line=line, layers=layers, box_bg=box_bg, box_pad=box_pad)


def shade(colour=WHITE):
    return [shadow("#000000", 0, 4, 16, 0.4), fill(colour)]


# --- Intros over the video -------------------------------------------------------------------------------------------

def canal_nombre():
    """The YouTube icon pops in the middle, slides left and the channel's name unrolls beside it; a small coral
    «SUSCRÍBETE» tag under the name."""
    t = _kit("intro-canal-nombre", "Logo y nombre del canal", "Logo and channel name", "aperturas", D_INTRO, 8310,
             ["intro", "logo", "nombre", "canal"], thumb_at=2.4)
    photo_bg(t, "h-nature-01", s1=1.05, label="Tu video")
    end = D_INTRO - 0.3
    slide = [(0, {"s": 0.0, "dx": 190}, "back"), (0.45, {"dx": 190}, "inout"), (0.95, {}, "hold"),
             (end - 0.3 - 0.35, {}, "in"), (end - 0.3, {"s": 0.0})]
    yt_icon(t, 700, 520, 150, 0.3, end - 0.3, motion=slide)
    txt(t, "TuCanal", Box(800, 450, 700, 120), 96, 1.2, end - 1.2, align="left", anim="wipe", ad=0.6,
        name="Nombre del canal", layers=shade())
    tag = Box(808, 580, 290, 54)
    t.solid(t.track("shape", "Etiqueta"), CORAL, 1.6, end - 1.6, tag, _life(end - 1.6, fin=0.3), radius=8,
            kind="rounded-rectangle")
    txt(t, "SUSCRÍBETE", tag, 30, 1.7, end - 1.8, weight=800, spacing=1, name="Etiqueta")
    return t


def canal_tu_youtube():
    """The icon drops in on top; under it «TU CANAL» in a coral box and «DE YOUTUBE» below, line by line."""
    t = _kit("intro-tu-canal", "Tu canal de YouTube", "Your YouTube channel", "aperturas", D_INTRO, 8311,
             ["intro", "logo", "canal", "caja"], thumb_at=2.4)
    photo_bg(t, "h-beach-01", s1=1.05, label="Tu video")
    end = D_INTRO - 0.3
    yt_icon(t, 960, 400, 150, 0.3, end - 0.3,
            motion=[(0, {"dy": -120, "s": 0.6}, "back"), (0.5, {}, "hold"), (end - 0.65, {}, "in"), (end - 0.3, {"s": 0.0})])
    box = centered(960, 535, 620, 92)
    t.solid(t.track("shape", "Caja"), CORAL, 0.8, end - 0.8, box,
            [(0, {"sx": 0.0}, "out"), (0.35, {}, "hold"), (end - 1.15, {}, "in"), (end - 0.8, {"sx": 0.0})])
    txt(t, "TU CANAL", box, 66, 1.0, end - 1.1, weight=900, spacing=2, name="Línea 1")
    txt(t, "DE YOUTUBE", Box(560, 590, 800, 80), 54, 1.3, end - 1.4, weight=800, spacing=3, anim="rise", ad=0.4,
        name="Línea 2", layers=shade())
    return t


def canal_apilado():
    """Three stacked lines «TU / CANAL DE / YOUTUBE» bounce in word by word, with speech bubbles popping round."""
    t = _kit("intro-apilado", "Tu canal de YouTube apilado", "Stacked YouTube channel", "aperturas", D_INTRO, 8312,
             ["intro", "apilado", "burbujas", "canal"], thumb_at=2.6)
    photo_bg(t, "h-city-02", s1=1.05, label="Tu video")
    end = D_INTRO - 0.3
    for i, (word, size, name) in enumerate([("TU", 110, "Línea 1"), ("CANAL DE", 110, "Línea 2"), ("YOUTUBE", 120, "Línea 3")]):
        a = 0.3 + i * 0.22
        txt(t, word, Box(460, 300 + i * 125, 1000, 140), size, a, end - a, weight=900, anim="pop", ad=0.35, name=name,
            layers=shade(), line=0.95)
    for k, (bx, by, w) in enumerate([(520, 330, 120), (1400, 330, 110), (1450, 690, 120), (470, 700, 100)]):
        a = 0.9 + k * 0.15
        rrect(t, t.track("shape", "Burbujas"), WHITE, a, end - a, centered(bx, by, w, w * 0.55), radius=w * 0.27,
              motion=_life(end - a), layers=[shadow("#000000", 0, 6, 14, 0.3), fill(WHITE), no_stroke()])
        for j in range(3):
            t.solid(t.track("shape", "Burbujas"), CORAL, a + 0.1, end - a - 0.1,
                    centered(bx - w * 0.22 + j * w * 0.22, by, w * 0.12, w * 0.12), _life(end - a - 0.1), kind="ellipse")
    return t


# --- White profile with perforated strips -----------------------------------------------------------------------------

def perfil_blanco():
    """White frame with two strips of little squares (top and bottom) that slide sideways; the channel's picture in a
    coral ring pops, then the YouTube icon and the name in coral, and the subscribers under it."""
    D = 5.5
    t = _kit("perfil-blanco", "Perfil del canal en blanco", "White channel profile", "aperturas", D, 8313,
             ["perfil", "foto", "blanco", "suscriptores"], thumb_at=2.8)
    t.solid(t.track("shape", "Fondo"), WHITE)
    rnd = random.Random(6)
    for row, y in enumerate([40, 92, 958, 1010]):
        # Little squares along a 2100 px strip, in the path's 0..100 box.
        off = 26 if row % 2 else 0
        d = " ".join(f"M {(c * 52 + off) / 21:.3f} 0 L {(c * 52 + off + 34) / 21:.3f} 0 L {(c * 52 + off + 34) / 21:.3f} 100 "
                     f"L {(c * 52 + off) / 21:.3f} 100 Z" for c in range(40))
        alpha = [0.55, 0.3, 0.3, 0.55][row]
        c = rnd.choice(["#E9A9B2", "#C9C9C9", "#F0C3C9"])
        path(t, t.track("shape", "Franjas"), c, 0.0, D, Box(-60, y, 2100, 34), d, filled=True,
             motion=[(0, {"dx": -50 if row % 2 else 50}, "linear"), (D, {"dx": 50 if row % 2 else -50})],
             opacity=keys([(0, alpha)]))
    end = D - 0.3
    t.solid(t.track("shape", "Aro"), CORAL, 0.3, end - 0.3, centered(960, 430, 250, 250), _life(end - 0.3), kind="ellipse")
    t.solid(t.track("shape", "Aro"), WHITE, 0.3, end - 0.3, centered(960, 430, 234, 234), _life(end - 0.3), kind="ellipse")
    circle_photo(t, "h-portrait-01", 0.35, end - 0.35, centered(960, 430, 218, 218), _life(end - 0.35), label="Foto del canal")
    # Icon and name as one line under the picture (wide enough for a long name on one line).
    yt_icon(t, 640, 650, 92, 0.9, end - 0.9)
    txt(t, "NombreDelCanal", Box(700, 600, 900, 100), 78, 1.05, end - 1.05, colour=CORAL, weight=800, align="left",
        anim="wipe", ad=0.5, name="Nombre del canal")
    txt(t, "50 mil suscriptores", Box(700, 700, 640, 44), 28, 1.4, end - 1.4, colour=CORAL_DARK, weight=600,
        align="right", name="Suscriptores")
    return t


# --- Coral backgrounds ---------------------------------------------------------------------------------------------------

def _coral_bg(t, D):
    t.solid(t.track("shape", "Fondo"), CORAL, 0.0, D, None,
            layers=[gradient([(0, CORAL, 1.0), (1, CORAL_DARK, 1.0)], angle=120), no_stroke()])


def _name_card(t, D, name, subs, dark_boxes=True, icon_y=420, name_y=520):
    end = D - 0.3
    yt_icon(t, 960, icon_y, 120, 0.5, end - 0.5, colour=WHITE, play=CORAL)
    if dark_boxes:
        b = centered(960, name_y, 640, 78)
        t.solid(t.track("shape", "Cajas"), INK, 0.8, end - 0.8, b,
                [(0, {"sx": 0.0}, "out"), (0.35, {}, "hold"), (end - 1.15, {}, "in"), (end - 0.8, {"sx": 0.0})])
        txt(t, name, b, 50, 0.95, end - 1.0, weight=900, spacing=1, name="Nombre del canal")
        s = centered(960, name_y + 66, 380, 44)
        t.solid(t.track("shape", "Cajas"), INK, 1.1, end - 1.1, s,
                [(0, {"sx": 0.0}, "out"), (0.3, {}, "hold"), (end - 1.4, {}, "in"), (end - 1.1, {"sx": 0.0})])
        txt(t, subs, s, 24, 1.25, end - 1.3, weight=800, spacing=2, name="Suscriptores")
    else:
        txt(t, name, Box(360, name_y - 60, 1200, 120), 104, 0.9, end - 0.9, weight=900, anim="pop", ad=0.4,
            name="Nombre del canal")
        txt(t, subs, Box(960, name_y + 50, 420, 40), 24, 1.3, end - 1.3, weight=800, spacing=2, align="left",
            name="Suscriptores")


def fondo_triangulos():
    D = 5.0
    t = _kit("fondo-coral-triangulos", "Nombre del canal con triángulos", "Channel name with triangles", "aperturas", D,
             8314, ["fondo", "coral", "triángulos", "nombre"], thumb_at=2.6)
    _coral_bg(t, D)
    rnd = random.Random(14)
    for k in range(14):
        cx, cy = rnd.uniform(0, 1920), rnd.uniform(0, 1080)
        if abs(cx - 960) < 380 and abs(cy - 520) < 200:
            continue
        s = rnd.uniform(70, 170)
        rot = rnd.uniform(0, 360)
        path(t, t.track("shape", "Triángulos"), CORAL_DEEP, 0.1 + k * 0.03, D - 0.1 - k * 0.03, centered(cx, cy, s, s),
             "M 50 5 L 95 90 L 5 90 Z", filled=True, rotation=keys([(0, rot), (D, rot + rnd.choice([-40, 40]))]),
             motion=[(0, {"s": 0.0}, "back"), (0.5, {}, "linear"), (D - 0.4 - 0.1 - k * 0.03, {"dy": -40}, "in"),
                     (D - 0.1 - k * 0.03, {"dy": -40, "s": 0.0})], opacity=keys([(0, 0.6)]))
    _name_card(t, D, "TUCANALDEYOUTUBE", "100 MIL SUSCRIPTORES")
    return t


def fondo_manchas():
    D = 5.0
    t = _kit("fondo-coral-manchas", "Nombre del canal con manchas", "Channel name with blobs", "aperturas", D, 8315,
             ["fondo", "coral", "manchas", "nombre"], thumb_at=2.6)
    _coral_bg(t, D)
    rnd = random.Random(15)
    for k in range(16):
        cx, cy = rnd.uniform(0, 1920), rnd.uniform(0, 1080)
        if abs(cx - 960) < 460 and abs(cy - 520) < 200:
            continue
        s = rnd.uniform(24, 70)
        t.solid(t.track("shape", "Manchas"), "#2A0A10", 0.15 + k * 0.04, D - 0.15 - k * 0.04,
                centered(cx, cy, s, s * rnd.uniform(0.7, 1.2)),
                [(0, {"s": 0.0}, "back"), (0.4, {}, "linear"), (D - 0.5 - k * 0.04, {"dx": rnd.uniform(-60, 60),
                                                                                   "dy": rnd.uniform(-60, 60)}, "in"),
                 (D - 0.15 - k * 0.04, {"s": 0.0})], kind="ellipse", rotation=keys([(0, rnd.uniform(0, 90))]))
    _name_card(t, D, "TUCANAL", "200 MIL SUSCRIPTORES", dark_boxes=False)
    return t


def fondo_circulos():
    """Big soft circles drifting; the white icon, a divider and «NombreDelCanal», a little «SUSCRÍBETE» pill."""
    D = 5.0
    t = _kit("fondo-coral-circulos", "Nombre del canal con círculos", "Channel name with circles", "aperturas", D, 8316,
             ["fondo", "coral", "círculos", "nombre"], thumb_at=2.6)
    _coral_bg(t, D)
    for k, (cx, cy, d) in enumerate([(240, 180, 520), (1650, 860, 640), (1500, 120, 260), (420, 960, 300)]):
        t.solid(t.track("shape", "Círculos"), WHITE, 0.0, D, centered(cx, cy, d, d),
                [(0, {"s": 0.7}, "out"), (1.0, {}, "linear"), (D, {"dx": 40 * (-1) ** k, "dy": 30 * (-1) ** (k + 1)})],
                kind="ellipse", layers=[gradient([(0, WHITE, 0.16), (1, WHITE, 0.0)], angle=135), no_stroke()])
    end = D - 0.3
    yt_icon(t, 700, 540, 130, 0.4, end - 0.4, colour=WHITE, play=CORAL)
    t.solid(t.track("shape", "Divisor"), WHITE, 0.7, end - 0.7, Box(790, 480, 4, 120),
            [(0, {"sy": 0.0}, "out"), (0.35, {}, "hold"), (end - 1.05, {}, "in"), (end - 0.7, {"sy": 0.0})])
    txt(t, "NombreDelCanal", Box(820, 470, 800, 110), 80, 0.9, end - 0.9, weight=800, align="left", anim="wipe", ad=0.6,
        name="Nombre del canal")
    p = Box(825, 596, 320, 64)
    pill(t, t.track("shape", "Botón"), INK, 1.4, end - 1.4, p, _life(end - 1.4, fin=0.3))
    txt(t, "SUSCRÍBETE", p, 32, 1.5, end - 1.5, weight=800, spacing=1, name="Botón")
    return t


def fondo_cruces():
    """A grid of little crosses that twinkle; the icon, «TuCanal» and the subscribers in a dark pill."""
    D = 5.0
    t = _kit("fondo-coral-cruces", "Nombre del canal con cruces", "Channel name with crosses", "aperturas", D, 8317,
             ["fondo", "coral", "cruces", "nombre"], thumb_at=2.6)
    _coral_bg(t, D)
    crosses = []
    for row in range(10):
        for col in range(18):
            cx = (col * 110 + 55) / 1920 * 100
            cy = (row * 110 + 40) / 1080 * 100
            a, b = 9 / 1920 * 100, 9 / 1080 * 100
            w, h = 2.2 / 1920 * 100, 2.2 / 1080 * 100
            crosses.append(f"M {cx - a:.3f} {cy - h:.3f} L {cx + a:.3f} {cy - h:.3f} L {cx + a:.3f} {cy + h:.3f} "
                           f"L {cx - a:.3f} {cy + h:.3f} Z M {cx - w:.3f} {cy - b:.3f} L {cx + w:.3f} {cy - b:.3f} "
                           f"L {cx + w:.3f} {cy + b:.3f} L {cx - w:.3f} {cy + b:.3f} Z")
    path(t, t.track("shape", "Cruces"), WHITE, 0.0, D, Box(0, 0, 1920, 1080), " ".join(crosses), filled=True,
         opacity=keys([(0, 0.0), (0.6, 0.35, "smooth"), (1.6, 0.18, "smooth"), (2.6, 0.35, "smooth"), (3.6, 0.18, "smooth"),
                       (D, 0.3)]))
    end = D - 0.3
    yt_icon(t, 960, 430, 120, 0.4, end - 0.4, colour=WHITE, play=CORAL)
    txt(t, "TuCanal", Box(460, 470, 1000, 130), 104, 0.8, end - 0.8, weight=800, anim="pop", ad=0.4, name="Nombre del canal")
    p = centered(960, 625, 300, 44)
    pill(t, t.track("shape", "Píldora"), INK, 1.2, end - 1.2, p, _life(end - 1.2, fin=0.3))
    txt(t, "500 mil suscriptores", p, 22, 1.3, end - 1.3, weight=700, name="Suscriptores")
    return t


# --- Text over the video ------------------------------------------------------------------------------------------------

def suscribete_ahora():
    """«¡SUSCRÍBETE AHORA / A MI CANAL!»: two big lines whose letters bounce in one after another."""
    D = 5.0
    t = _kit("suscribete-ahora", "¡Suscríbete ahora a mi canal!", "Subscribe now on my channel!", "frases", D, 8318,
             ["suscríbete", "frase", "letras"], thumb_at=2.4)
    photo_bg(t, "h-city-05", s1=1.05, label="Tu video")
    end = D - 0.3
    txt(t, "¡SUSCRÍBETE AHORA", Box(260, 420, 1400, 120), 96, 0.3, end - 0.3, weight=900,
        anim="fade-up-char", ad=0.9, name="Línea 1", layers=shade())
    txt(t, "A MI CANAL!", Box(260, 530, 1400, 120), 96, 0.7, end - 0.7, weight=900, anim="fade-up-char", ad=0.7,
        name="Línea 2", layers=shade())
    return t


def botones_fila():
    """Three small buttons along the bottom, one after another: «Me gusta» with the thumb, «Suscríbete» with the
    YouTube icon, «Activa la campana» with the bell; each gets its tap."""
    D = 6.0
    t = _kit("botones-fila", "Me gusta, suscríbete y campana", "Like, subscribe and bell", "elementos", D, 8319,
             ["botones", "me gusta", "suscríbete", "campana"], thumb_at=3.6)
    photo_bg(t, "h-concert-01", s1=1.04, label="Tu video")
    end = D - 0.3
    items = [("ME GUSTA", "like"), ("SUSCRÍBETE", "yt"), ("ACTIVA LA CAMPANA", "bell")]
    x = 300
    for i, (text, kind) in enumerate(items):
        a = 0.4 + i * 0.5
        w = 120 + len(text) * 19
        box = Box(x, 900, w, 70)
        rrect(t, t.track("shape", "Botones"), WHITE, a, end - a, box, radius=35, motion=_life(end - a),
              layers=[shadow("#000000", 0, 8, 20, 0.35), fill(WHITE), no_stroke()])
        cx, cy = x + 44, 935
        if kind == "yt":
            yt_icon(t, cx, cy, 46, a + 0.1, end - a - 0.1)
        else:
            d = THUMB if kind == "like" else BELL
            path(t, t.track("shape", "Iconos"), CORAL, a + 0.1, end - a - 0.1, centered(cx, cy, 34, 34), d, filled=True,
                 motion=_life(end - a - 0.1))
        txt(t, text, Box(x + 74, 900, w - 86, 70), 26, a + 0.2, end - a - 0.3, colour=INK, weight=800, align="left",
            name=f"Botón {i + 1}")
        # The tap: the button squeezes and the icon pops.
        tap = a + 1.4
        t.solid(t.track("shape", "Toques"), CORAL, tap, 0.5, centered(cx, cy, 60, 60),
                [(0, {"s": 0.3}, "out"), (0.5, {"s": 2.0})], kind="ellipse",
                layers=[_hollow(), _stroke(CORAL, 4, "inside")], opacity=keys([(0, 1.0), (0.5, 0.0)]))
        x += w + 40
    return t


def redes_logos():
    """The user's handles on the platforms, lower left, one after another: the official glyph in a coral badge and
    «@usuario» in a white strip; each slides out and back."""
    D = 9.0
    t = _kit("redes-logos", "Tus redes con logos", "Your socials with logos", "redes", D, 8320,
             ["redes", "instagram", "facebook", "tiktok", "x", "usuario"], thumb_at=1.6)
    photo_bg(t, "h-portrait-05", s1=1.04, label="Tu video")
    nets = [("instagram", "@tuusuario"), ("facebook", "/tupagina"), ("tiktok", "@tuusuario"), ("x", "@tuusuario")]
    slot = (D - 0.3) / len(nets)
    for i, (net, handle) in enumerate(nets):
        a = 0.3 + i * slot
        dur = slot - 0.1
        badge = Box(120, 900, 90, 90)
        rrect(t, t.track("shape", "Insignias"), CORAL, a, dur, badge, radius=14, motion=_life(dur, fin=0.4, fout=0.3))
        logo(t, net, badge.x + 45, badge.y + 45, 50, a + 0.08, dur - 0.16, motion=_life(dur - 0.16, fin=0.4, fout=0.3))
        strip = Box(222, 912, 470, 66)
        t.solid(t.track("shape", "Franjas"), WHITE, a + 0.25, dur - 0.4, strip,
                [(0, {"sx": 0.0, "dx": -235}, "out"), (0.35, {}, "hold"), (dur - 0.4 - 0.3, {}, "in"),
                 (dur - 0.4, {"sx": 0.0, "dx": -235})])
        txt(t, handle, Box(246, 912, 440, 66), 36, a + 0.45, dur - 0.75, colour=INK, weight=800, align="left",
            anim="typewriter", ad=0.4, name=f"Usuario {i + 1}")
    return t


# --- End screens ------------------------------------------------------------------------------------------------------------

def _yt_pattern(t, D):
    """The faint pattern of little play icons on the coral end screens."""
    icons = []
    for row in range(7):
        for col in range(12):
            cx = (col * 170 + (85 if row % 2 else 0) + 40) / 1920 * 100
            cy = (row * 165 + 50) / 1080 * 100
            w, h = 34 / 1920 * 100, 24 / 1080 * 100
            icons.append(f"M {cx - w:.3f} {cy - h:.3f} L {cx + w:.3f} {cy - h:.3f} L {cx + w:.3f} {cy + h:.3f} "
                         f"L {cx - w:.3f} {cy + h:.3f} Z")
    path(t, t.track("shape", "Patrón"), CORAL_DARK, 0.0, D, Box(0, 0, 1920, 1080), " ".join(icons), filled=True,
         motion=[(0, {}, "linear"), (D, {"dx": -85})], opacity=keys([(0, 0.0), (0.6, 0.55)]))


def _socials_row(t, y, a, D, names=("instagram", "facebook", "x"), xs=(520, 960, 1400), colour=WHITE, size=40):
    for i, (net, x) in enumerate(zip(names, xs)):
        b = a + i * 0.15
        logo(t, net, x - 130, y, size, b, D - b - 0.3, colour=colour)
        txt(t, "@tuusuario", Box(x - 100, y - 30, 330, 60), 32, b + 0.1, D - b - 0.5, colour=colour, weight=700,
            align="left", anim="slide-left", ad=0.3, name=f"Red {i + 1}")


def final_mas_videos():
    """Coral with a pattern of play icons: the three handles along the top, the channel's picture, «¡GRACIAS POR
    VER!», «MÁS VIDEOS:» and two video slots side by side."""
    D = 10.0
    t = _kit("final-mas-videos", "Pantalla final: más videos", "End screen: more videos", "pantallas-finales", D, 8321,
             ["pantalla final", "gracias", "más videos", "redes"], thumb_at=4.5)
    _coral_bg(t, D)
    _yt_pattern(t, D)
    _socials_row(t, 70, 0.4, D)
    av = (960, 290)
    t.solid(t.track("shape", "Aro"), WHITE, 0.6, D - 0.9, centered(*av, 196, 196), _life(D - 0.9), kind="ellipse")
    circle_photo(t, "h-portrait-03", 0.65, D - 0.95, centered(*av, 180, 180), _life(D - 0.95), label="Foto del canal")
    txt(t, "¡GRACIAS POR VER!", Box(260, 410, 1400, 110), 84, 1.0, D - 1.3, weight=900, anim="typewriter", ad=0.7,
        name="Gracias")
    txt(t, "MÁS VIDEOS:", Box(560, 515, 800, 60), 40, 1.5, D - 1.8, weight=800, name="Más videos")
    for i, (x, sample, name) in enumerate([(445, "h-travel-02", "Video 1"), (985, "h-city-02", "Video 2")]):
        a = 1.7 + i * 0.2
        frame = Box(x - 8, 592, 506, 290)
        m = [(0, {"dy": 500}, "out"), (0.55, {}, "hold"), (D - a - 0.4, {}, "in"), (D - a, {"dy": 500})]
        rrect(t, t.track("shape", "Marcos"), WHITE, a, D - a, frame, radius=4, motion=m,
              layers=[shadow("#000000", 0, 12, 30, 0.3), fill(WHITE), no_stroke()])
        t.photo(t.track("video", name), sample, a, D - a, Box(x, 600, 490, 274), m, label=name)
    return t


def final_curva():
    """The user's video on top; a coral circle rises from the bottom like a big curve. On it: «GRACIAS POR VER»,
    the picture, two video slots either side, and «NO OLVIDES DAR ME GUSTA Y COMENTAR» in an outlined box."""
    D = 10.0
    t = _kit("final-curva", "Pantalla final con curva", "End screen with a curve", "pantallas-finales", D, 8322,
             ["pantalla final", "curva", "gracias", "dos videos"], thumb_at=4.5)
    photo_bg(t, "h-nature-05", s1=1.04, label="Tu video")
    # A bowl coming down from the top: its curved edge low in the middle, the video showing in the corners below.
    circle = centered(960, -300, 2700, 2700)
    t.solid(t.track("shape", "Curva"), CORAL, 0.2, D - 0.2, circle,
            [(0, {"dy": -1300}, "out"), (0.8, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dy": -1300})],
            kind="ellipse", layers=[shadow("#000000", 0, -8, 30, 0.35), fill(CORAL), no_stroke()])
    txt(t, "¡GRACIAS POR VER!", Box(460, 110, 1000, 90), 64, 0.9, D - 1.2, weight=900, anim="typewriter", ad=0.6,
        name="Gracias")
    av = (960, 470)
    t.solid(t.track("shape", "Aro"), WHITE, 1.1, D - 1.4, centered(*av, 196, 196), _life(D - 1.4), kind="ellipse")
    circle_photo(t, "h-portrait-04", 1.15, D - 1.45, centered(*av, 180, 180), _life(D - 1.45), label="Foto del canal")
    for i, (x, lab, sample, name) in enumerate([(230, "VIDEO ANTERIOR", "h-travel-02", "Video anterior"),
                                                (1210, "VIDEO SIGUIENTE", "h-city-02", "Video siguiente")]):
        a = 1.3 + i * 0.2
        m = [(0, {"dx": -700 if i == 0 else 700}, "out"), (0.55, {}, "hold"), (D - a - 0.4, {}, "in"),
             (D - a, {"dx": -700 if i == 0 else 700})]
        rrect(t, t.track("shape", "Marcos"), WHITE, a, D - a, Box(x - 8, 342, 496, 282), radius=4, motion=m,
              layers=[shadow("#000000", 0, 10, 26, 0.3), fill(WHITE), no_stroke()])
        t.photo(t.track("video", name), sample, a, D - a, Box(x, 350, 480, 266), m, label=name)
        txt(t, lab, Box(x, 636, 480, 50), 28, a + 0.4, D - a - 0.7, weight=800, spacing=1, name=f"Etiqueta {i + 1}")
    cta = centered(960, 780, 820, 70)
    rrect(t, t.track("shape", "Llamado"), WHITE, 1.9, D - 2.2, cta, radius=4, motion=_life(D - 2.2),
          layers=[_hollow(), _stroke(WHITE, 4, "inside")])
    txt(t, "NO OLVIDES DAR ME GUSTA Y COMENTAR", cta, 32, 2.0, D - 2.3, weight=800, spacing=1, name="Llamado")
    _socials_row(t, 905, 2.2, D, xs=(560, 960, 1360), size=36)
    return t


def final_diagonal():
    """Split by a diagonal: the user's video darkened on the left with «VIDEO SIGUIENTE» in a frame, coral on the
    right with «¡GRACIAS POR VER!», the picture, «SUSCRÍBETE PARA MÁS VIDEOS» and a white button; handles below."""
    D = 10.0
    t = _kit("final-diagonal", "Pantalla final en diagonal", "Diagonal end screen", "pantallas-finales", D, 8323,
             ["pantalla final", "diagonal", "gracias", "suscríbete"], thumb_at=4.5)
    photo_bg(t, "h-cafe-01", s1=1.04, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.5, 0.45)]))
    path(t, t.track("shape", "Diagonal"), CORAL, 0.2, D - 0.2, Box(880, 0, 1040, 1080), "M 30 0 L 100 0 L 100 100 L 0 100 Z",
         filled=True, motion=[(0, {"dx": 1100}, "out"), (0.7, {}, "hold"), (D - 0.2 - 0.6, {}, "in"), (D - 0.2, {"dx": 1100})],
         layers=[shadow("#000000", -10, 0, 30, 0.35), fill(CORAL), no_stroke()])
    txt(t, "VIDEO SIGUIENTE", Box(150, 230, 760, 60), 40, 0.9, D - 1.2, weight=800, spacing=1, name="Etiqueta")
    m = [(0, {"dx": -900}, "out"), (0.6, {}, "hold"), (D - 1.0 - 0.4, {}, "in"), (D - 1.0, {"dx": -900})]
    rrect(t, t.track("shape", "Marcos"), WHITE, 0.8, D - 1.0, Box(162, 302, 696, 396), radius=4, motion=m,
          layers=[shadow("#000000", 0, 12, 30, 0.35), fill(WHITE), no_stroke()])
    t.photo(t.track("video", "Video siguiente"), "h-travel-02", 0.8, D - 1.0, Box(170, 310, 680, 380), m,
            label="Video siguiente")
    txt(t, "¡GRACIAS\nPOR VER!", Box(1230, 150, 620, 200), 76, 1.0, D - 1.3, weight=900, line=1.0, anim="typewriter",
        ad=0.7, name="Gracias")
    av = (1540, 480)
    t.solid(t.track("shape", "Aro"), WHITE, 1.2, D - 1.5, centered(*av, 196, 196), _life(D - 1.5), kind="ellipse")
    circle_photo(t, "h-portrait-06", 1.25, D - 1.55, centered(*av, 180, 180), _life(D - 1.55), label="Foto del canal")
    txt(t, "SUSCRÍBETE\nPARA MÁS VIDEOS", Box(1290, 600, 500, 110), 36, 1.6, D - 1.9, weight=800, line=1.1,
        name="Llamado")
    btn = centered(1540, 760, 300, 66)
    pill(t, t.track("shape", "Botón"), WHITE, 1.9, D - 2.2, btn, _life(D - 2.2),
         layers=[shadow("#000000", 0, 8, 20, 0.25), fill(WHITE), no_stroke()])
    txt(t, "SUSCRÍBETE", btn, 34, 2.0, D - 2.3, colour=CORAL, weight=900, spacing=1, name="Botón")
    # Along the bottom of the video side, clear of the coral diagonal.
    _socials_row(t, 900, 2.1, D, xs=(240, 490, 740), size=30)
    return t


TEMPLATES = [canal_nombre, canal_tu_youtube, canal_apilado, perfil_blanco, fondo_triangulos, fondo_manchas,
             fondo_circulos, fondo_cruces, suscribete_ahora, botones_fila, redes_logos, final_mas_videos, final_curva,
             final_diagonal]
