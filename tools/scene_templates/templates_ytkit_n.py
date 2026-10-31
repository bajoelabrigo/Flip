"""Kit de YouTube, batch n (2026-10-30): the subscribe buttons in the lower third of Jorge's «pack youtube 6», almost
the same and our own (see templates_ytkit_i..m): the channel's picture and name with a coral «SUSCRÍBETE» that a
pointer clicks into a grey «SUSCRITO», pills with the like, YouTube and bell icons, a vertical stack, a white card
that ticks its list, a speech bubble. Labels never smaller than 28 px (Jorge: «suscríbete no muy chico»), the
pills sized from the measured text. Order 8400-8429.
"""

from __future__ import annotations

from kit import Box, centered, circle_photo, fill, keys, no_stroke, outline, photo_bg, pill, rrect, shadow, wide
from templates_ytkit_a import BELL, _cursor, _stroke, path
from templates_ytkit_f import THUMB
from templates_ytkit_i import _text_width
from templates_ytkit_j import CORAL, INK, WHITE, _hollow, _life, txt, yt_icon

GREY_BTN = "#E4E7EC"
GREY_INK = "#555D6B"
BUBBLE = "M 8 6 L 92 6 C 97 6 100 9 100 14 L 100 66 C 100 71 97 74 92 74 L 46 74 L 24 96 L 28 74 L 8 74 " \
         "C 3 74 0 71 0 66 L 0 14 C 0 9 3 6 8 6 Z"
CHECK = "M 8 52 L 38 82 L 92 22"


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"ytk-{id}", es, en, "ytkit", dur, order=order, tags=["kit:elementos", "youtube"] + tags, **kw)


def _sh(colour):
    return [shadow("#000000", 0, 6, 18, 0.3), fill(colour), no_stroke()]


def _pop(dur, s0=0.0):
    return _life(dur, fin=0.4, fout=0.3, s0=s0)


def _until(dur, at, s1=0.92):
    """In with a pop, then out squeezed at `at` (clip-relative) where the next state takes over."""
    return [(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (at - 0.12, {}, "out"), (at, {"s": s1})]


def _from(dur, s0=0.92):
    return [(0, {"s": s0}, "back"), (0.25, {}, "hold"), (dur - 0.3, {}, "in"), (dur, {"s": 0.0})]


def _ring_keys(at):
    return keys([(0, 0, "hold"), (at, 0), (at + 0.1, 18), (at + 0.2, -16), (at + 0.3, 12), (at + 0.4, -8), (at + 0.5, 0)])


def _icon(t, kind, cx, cy, s, colour, t0, dur, motion=None, back=CORAL, ring_at=None):
    m = motion if motion is not None else _pop(dur)
    if kind == "yt":
        yt_icon(t, cx, cy, s, t0, dur, motion=m, colour=colour, play=back)
        return
    extra = {"rotation": _ring_keys(ring_at)} if ring_at is not None else {}
    d = {"thumb": THUMB, "bell": BELL, "check": None}[kind]
    if kind == "check":
        path(t, t.track("shape", "Iconos"), colour, t0, dur, centered(cx, cy, s, s), CHECK, s * 0.14, motion=m,
             draw=(0.15, 0.3))
        return
    path(t, t.track("shape", "Iconos"), colour, t0, dur, centered(cx, cy, s, s), d, filled=True, motion=m, **extra)


def _btn(t, x, cy, text, size, t0, dur, fg=WHITE, bg=CORAL, icon=None, icon_colour=None, motion=None, ad=0.3,
         name=None, ring_at=None, h=None):
    """A pill sized from its text, left edge at x, centred on cy; optional icon on its left. Returns the box."""
    h = h or size * 2.0
    tw = _text_width(text, size)
    isz = size * 1.2 if icon else 0
    gap = size * 0.45 if icon else 0
    padx = size * 0.85
    box = Box(x, cy - h / 2, tw + 2 * padx + isz + gap, h)
    m = motion if motion is not None else _pop(dur)
    pill(t, t.track("shape", "Botones"), bg, t0, dur, box, m, layers=_sh(bg))
    if icon:
        _icon(t, icon, x + padx + isz / 2, cy, isz, icon_colour or fg, t0 + 0.05, dur - 0.05, motion=m, back=bg,
              ring_at=ring_at)
    txt(t, text, Box(x + padx + isz + gap, cy - h / 2, tw + 6, h), size, t0 + 0.08, dur - 0.1, colour=fg, weight=800,
        align="left", anim="fade", ad=ad, name=name or text)
    return box


def _ripple(t, cx, cy, at, d=70, colour=WHITE):
    t.solid(t.track("shape", "Onda"), colour, at, 0.6, centered(cx, cy, d, d),
            [(0, {"s": 0.3}, "out"), (0.6, {"s": 2.4})], kind="ellipse",
            layers=[_hollow(), _stroke(colour, 5, "inside")], opacity=keys([(0, 1.0), (0.6, 0.0)]))


def _subscribe_swap(t, x, cy, size, t0, click, t1, icon="yt"):
    """Coral «SUSCRÍBETE» until the click, then grey «SUSCRITO». Returns the later box (for what goes after it)."""
    _btn(t, x, cy, "SUSCRÍBETE", size, t0, click - t0, icon=icon, motion=_until(click - t0, click - t0), name="Botón")
    return _btn(t, x, cy, "SUSCRITO", size, click, t1 - click, fg=GREY_INK, bg=GREY_BTN, icon=icon,
                icon_colour=GREY_INK, motion=_from(t1 - click), ad=0.12, name="Botón suscrito")


def _avatar(t, sample, cx, cy, d, t0, dur):
    t.solid(t.track("shape", "Aro"), WHITE, t0, dur, centered(cx, cy, d + 12, d + 12), _pop(dur), kind="ellipse",
            layers=_sh(WHITE))
    circle_photo(t, sample, t0 + 0.05, dur - 0.05, centered(cx, cy, d, d), _pop(dur - 0.05), label="Foto del canal")


# --- The pieces -------------------------------------------------------------------------------------------------------

def boton_canal():
    """The channel's picture, its name in a white pill and a coral «SUSCRÍBETE» that the pointer clicks into a grey
    «SUSCRITO»; the bell beside it rings."""
    D = 5.0
    t = _kit("boton-canal", "Canal con botón suscríbete", "Channel with a subscribe button", D, 8400,
             ["suscríbete", "canal", "foto", "campana"], thumb_at=2.6)
    photo_bg(t, "h-man-02", s1=1.03, label="Tu video")
    cy = 940
    _avatar(t, "h-portrait-04", 150, cy, 104, 0.2, D - 0.4)
    name = _btn(t, 220, cy, "NOMBRE DEL CANAL", 36, 0.35, D - 0.65, fg=INK, bg=WHITE, name="Nombre del canal")
    x = name.x + name.w + 16
    _subscribe_swap(t, x, cy, 36, 0.5, 2.0, D - 0.4)
    _ripple(t, x + 120, cy, 2.0)
    bell_x = x + _btn_width("SUSCRITO", 36, True) + 56
    t.solid(t.track("shape", "Campana"), WHITE, 0.65, D - 1.05, centered(bell_x, cy, 72, 72), _pop(D - 1.05),
            kind="ellipse", layers=_sh(WHITE))
    _icon(t, "bell", bell_x, cy, 40, CORAL, 0.7, D - 1.1, ring_at=1.8)
    _cursor(t, x + 120, cy, 0.9, 2.0, 1.1, 1.6, frm=(380, 160))
    return t


def _btn_width(text, size, icon):
    return _text_width(text, size) + 2 * size * 0.85 + (size * 1.65 if icon else 0)


def pildora_iconos():
    """One white pill with three parts — like, YouTube and bell — each turning coral in turn with a ripple."""
    D = 5.0
    t = _kit("pildora-iconos", "Píldora con tres iconos", "Pill with three icons", D, 8401,
             ["suscríbete", "me gusta", "campana", "píldora"], thumb_at=2.9)
    photo_bg(t, "h-sport-01", s1=1.03, label="Tu video")
    cy, size = 940, 36
    parts = [("thumb", "ME GUSTA"), ("yt", "SUSCRÍBETE"), ("bell", "CAMPANA")]
    widths = [_text_width(s, size) + size * 1.2 + size * 0.45 for _, s in parts]
    gap = 56
    total = sum(widths) + gap * 2 + 2 * size * 0.9
    box = centered(960, cy, total, size * 2.2)
    pill(t, t.track("shape", "Píldora"), WHITE, 0.2, D - 0.4, box, _pop(D - 0.4), layers=_sh(WHITE))
    x = box.x + size * 0.9
    for i, ((kind, word), w) in enumerate(zip(parts, widths)):
        at = 1.3 + i * 0.5
        icx = x + size * 0.6
        _icon(t, kind, icx, cy, size * 1.2, INK, 0.35, at - 0.35, motion=_until(at - 0.35, at - 0.35), back=WHITE)
        _icon(t, kind, icx, cy, size * 1.2, CORAL, at, D - 0.5 - at, motion=_from(D - 0.5 - at, 0.6), back=WHITE,
              ring_at=0.2 if kind == "bell" else None)
        _ripple(t, icx, cy, at, 50, CORAL)
        txt(t, word, Box(icx + size * 0.6 + size * 0.45, cy - 30, w, 60), size, 0.45, D - 0.95, colour=INK,
            align="left", name=word)
        x += w + gap
    return t


def yt_suscrito():
    """The YouTube icon pops, a coral «SUSCRÍBETE» slides out of it and is clicked into «SUSCRITO»; the bell rings."""
    D = 5.0
    t = _kit("yt-suscrito", "Logo de YouTube y suscríbete", "YouTube logo and subscribe", D, 8402,
             ["suscríbete", "logo", "youtube", "campana"], thumb_at=2.6)
    photo_bg(t, "h-nature-03", s1=1.03, label="Tu video")
    cy = 940
    yt_icon(t, 160, cy, 120, 0.2, D - 0.4, motion=_pop(D - 0.4))
    x = 235
    _subscribe_swap(t, x, cy, 38, 0.5, 2.1, D - 0.4, icon=None)
    _ripple(t, x + 110, cy, 2.1)
    bell_x = x + _btn_width("SUSCRITO", 38, False) + 52
    _icon(t, "bell", bell_x, cy, 54, WHITE, 0.7, D - 1.1, ring_at=1.9)
    _cursor(t, x + 110, cy, 0.9, 2.1, 1.2, 1.6, frm=(360, 160))
    return t


def pila_vertical():
    """Three coral pills stacked on the left — like, subscribe, bell — slide in one after another."""
    D = 5.0
    t = _kit("pila-vertical", "Botones en columna", "Stacked buttons", D, 8403,
             ["suscríbete", "me gusta", "campana", "columna"], thumb_at=2.4)
    photo_bg(t, "h-man-04", s1=1.03, label="Tu video")
    for i, (kind, word) in enumerate([("thumb", "ME GUSTA"), ("yt", "SUSCRÍBETE"), ("bell", "ACTIVA LA CAMPANA")]):
        a = 0.3 + i * 0.25
        dur = D - 0.3 - a
        _btn(t, 80, 720 + i * 104, word, 38, a, dur, icon=kind, name=word, ring_at=1.6 - a if kind == "bell" else None,
             motion=[(0, {"dx": -700}, "out"), (0.45, {}, "hold"), (dur - 0.4, {}, "in"), (dur, {"dx": -700})])
    return t


def me_gusta():
    """«DALE ME GUSTA» in a white pill with a coral circle holding the thumb; the pointer clicks it, the thumb jumps."""
    D = 4.5
    t = _kit("me-gusta", "Dale me gusta", "Like the video", D, 8404,
             ["me gusta", "like", "pulgar", "clic"], thumb_at=2.3)
    photo_bg(t, "h-cafe-01", s1=1.03, label="Tu video")
    cy = 940
    box = _btn(t, 120, cy, "DALE ME GUSTA", 38, 0.2, D - 0.4, fg=INK, bg=WHITE, name="Me gusta")
    cx = box.x + box.w + 60
    t.solid(t.track("shape", "Círculo"), CORAL, 0.35, D - 0.65, centered(cx, cy, 96, 96), _pop(D - 0.65),
            kind="ellipse", layers=_sh(CORAL))
    _icon(t, "thumb", cx, cy - 2, 48, WHITE, 0.4, D - 0.7,
          motion=[(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (1.3, {}, "out"), (1.45, {"s": 1.45}, "back"),
                  (1.8, {}, "hold"), (D - 0.7 - 0.3, {}, "in"), (D - 0.7, {"s": 0.0})])
    _ripple(t, cx, cy, 1.7)
    _cursor(t, cx, cy, 0.7, 2.0, 1.0, 1.6, frm=(300, 150))
    return t


def tarjeta_lista():
    """A white card: the channel's picture and name, then three lines — like, subscribe, bell — each ticked in coral."""
    D = 5.5
    t = _kit("tarjeta-lista", "Tarjeta con lista", "Card with a checklist", D, 8405,
             ["suscríbete", "lista", "tarjeta", "me gusta"], thumb_at=3.2)
    photo_bg(t, "h-office-03", s1=1.03, label="Tu video")
    card = Box(80, 560, 560, 440)
    rrect(t, t.track("shape", "Tarjeta"), WHITE, 0.2, D - 0.4, card, radius=24,
          motion=[(0, {"dy": 500}, "out"), (0.5, {}, "hold"), (D - 0.4 - 0.4, {}, "in"), (D - 0.4, {"dy": 500})],
          layers=_sh(WHITE))
    _avatar(t, "h-portrait-01", card.x + 80, card.y + 80, 88, 0.6, D - 1.0)
    txt(t, "NOMBRE DEL CANAL", Box(card.x + 150, card.y + 50, 380, 60), 30, 0.7, D - 1.1, colour=INK, align="left",
        name="Nombre del canal")
    for i, (kind, word) in enumerate([("thumb", "DALE ME GUSTA"), ("yt", "SUSCRÍBETE"), ("bell", "ACTIVA LA CAMPANA")]):
        cy = card.y + 190 + i * 80
        a = 0.8 + i * 0.12
        _icon(t, kind, card.x + 64, cy, 40, CORAL, a, D - 0.5 - a, back=WHITE)
        txt(t, word, Box(card.x + 110, cy - 28, 360, 56), 30, a + 0.05, D - 0.55 - a, colour=INK, align="left",
            name=word)
        at = 1.6 + i * 0.45
        t.solid(t.track("shape", "Marcas"), CORAL, at, D - 0.5 - at, centered(card.x + card.w - 60, cy, 46, 46),
                _pop(D - 0.5 - at), kind="ellipse")
        _icon(t, "check", card.x + card.w - 60, cy, 26, WHITE, at + 0.05, D - 0.55 - at)
    return t


def suscribete_contorno():
    """The YouTube icon drops in the middle, under it «SUSCRÍBETE» in an outlined white box that opens sideways."""
    D = 4.5
    t = _kit("suscribete-contorno", "Suscríbete en marco", "Subscribe in a frame", D, 8406,
             ["suscríbete", "marco", "contorno", "logo"], thumb_at=2.2)
    photo_bg(t, "h-travel-03", s1=1.03, label="Tu video")
    yt_icon(t, 960, 790, 120, 0.2, D - 0.4,
            motion=[(0, {"dy": -80, "s": 0.5}, "back"), (0.45, {}, "hold"), (D - 0.4 - 0.3, {}, "in"), (D - 0.4, {"s": 0.0})])
    size = 40
    w = _text_width("SUSCRÍBETE", size) + size * 2.0
    box = centered(960, 920, w, size * 2.0)
    outline(t, t.track("shape", "Marco"), WHITE, 5, 0.5, D - 0.8, box,
            [(0, {"sx": 0.0}, "out"), (0.35, {}, "hold"), (D - 0.8 - 0.3, {}, "in"), (D - 0.8, {"sx": 0.0})], radius=12)
    txt(t, "SUSCRÍBETE", box, size, 0.7, D - 1.0, weight=900, spacing=2, name="Botón",
        layers=[shadow("#000000", 0, 3, 12, 0.4), fill(WHITE)])
    return t


def suscribete_texto():
    """Just «SUSCRÍBETE» in big white type with the YouTube icon beside it; the pointer clicks the icon."""
    D = 4.5
    t = _kit("suscribete-texto", "Suscríbete con el logo", "Subscribe with the logo", D, 8407,
             ["suscríbete", "texto", "logo", "clic"], thumb_at=2.2)
    photo_bg(t, "h-portrait-05", s1=1.03, label="Tu video")
    size = 54
    w = _text_width("SUSCRÍBETE", size)
    x = 1820 - w * 1.05 - 160
    txt(t, "SUSCRÍBETE", Box(x, 900, w * 1.05 + 10, 80), size, 0.3, D - 0.6, weight=900, align="left", anim="wipe", ad=0.5,
        name="Texto", layers=[shadow("#000000", 0, 4, 16, 0.45), fill(WHITE)])
    icx = 1820 - 50
    yt_icon(t, icx, 940, 100, 0.2, D - 0.4,
            motion=[(0, {"s": 0.0}, "back"), (0.4, {}, "hold"), (1.5, {}, "out"), (1.62, {"s": 0.85}, "back"),
                    (1.9, {}, "hold"), (D - 0.4 - 0.3, {}, "in"), (D - 0.4, {"s": 0.0})])
    _ripple(t, icx, 940, 1.8)
    _cursor(t, icx, 950, 0.6, 2.4, 1.2, 1.8, frm=(-260, -200))
    return t


def campana_texto():
    """«ACTIVA LA CAMPANA» in white beside a coral circle with the bell, which rings twice."""
    D = 4.5
    t = _kit("campana-texto", "Activa la campana", "Turn on the bell", D, 8408,
             ["campana", "notificaciones", "texto", "coral"], thumb_at=2.2)
    photo_bg(t, "h-food-02", s1=1.03, label="Tu video")
    t.solid(t.track("shape", "Oscurecer"), "#000000", 0.0, D, None, opacity=keys([(0, 0.0), (0.4, 0.25)]))
    cx, cy = 170, 935
    t.solid(t.track("shape", "Círculo"), CORAL, 0.2, D - 0.4, centered(cx, cy, 100, 100), _pop(D - 0.4), kind="ellipse",
            layers=_sh(CORAL))
    path(t, t.track("shape", "Iconos"), WHITE, 0.3, D - 0.6, centered(cx, cy, 52, 52), BELL, filled=True,
         motion=_pop(D - 0.6),
         rotation=keys([(0, 0, "hold"), (0.6, 0), (0.7, 18), (0.8, -16), (0.9, 12), (1.0, -8), (1.1, 0, "hold"),
                        (1.8, 0), (1.9, 18), (2.0, -16), (2.1, 12), (2.2, -8), (2.3, 0)]))
    txt(t, "ACTIVA LA CAMPANA", Box(250, 895, 900, 80), 46, 0.5, D - 0.9, weight=900, align="left", anim="wipe", ad=0.5,
        name="Texto", layers=[shadow("#000000", 0, 4, 16, 0.45), fill(WHITE)])
    return t


def burbuja():
    """A coral speech bubble pops with the YouTube icon in white inside, «SUSCRÍBETE» unrolls beside it."""
    D = 4.5
    t = _kit("burbuja-suscribete", "Burbuja con suscríbete", "Speech bubble with subscribe", D, 8409,
             ["suscríbete", "burbuja", "logo", "coral"], thumb_at=2.2)
    photo_bg(t, "h-nature-05", s1=1.03, label="Tu video")
    bx, by = 170, 905
    path(t, t.track("shape", "Burbuja"), CORAL, 0.2, D - 0.4, centered(bx, by, 140, 120), BUBBLE, filled=True,
         motion=_pop(D - 0.4), layers=_sh(CORAL))
    yt_icon(t, bx, by - 14, 70, 0.3, D - 0.6, colour=WHITE, play=CORAL, motion=_pop(D - 0.6))
    txt(t, "SUSCRÍBETE", Box(265, 860, 700, 80), 48, 0.55, D - 0.95, weight=900, align="left", anim="wipe", ad=0.5,
        name="Texto", layers=[shadow("#000000", 0, 4, 16, 0.45), fill(WHITE)])
    return t


def nombre_botones():
    """The channel's name in big white type and, under it, a row of three small coral pills."""
    D = 5.0
    t = _kit("nombre-botones", "Nombre y tres botones", "Name and three buttons", D, 8410,
             ["suscríbete", "nombre", "botones", "canal"], thumb_at=2.6)
    photo_bg(t, "h-man-01", s1=1.03, label="Tu video")
    txt(t, "NOMBRE DEL CANAL", Box(90, 790, 1100, 90), 62, 0.2, D - 0.5, weight=900, align="left", anim="wipe", ad=0.5,
        name="Nombre del canal", layers=[shadow("#000000", 0, 4, 16, 0.45), fill(WHITE)])
    x = 90
    for i, (kind, word) in enumerate([("thumb", "ME GUSTA"), ("yt", "SUSCRÍBETE"), ("bell", "CAMPANA")]):
        a = 0.6 + i * 0.18
        box = _btn(t, x, 935, word, 34, a, D - 0.3 - a, icon=kind, name=word,
                   ring_at=1.8 - a if kind == "bell" else None)
        x = box.x + box.w + 18
    return t


def fila_tres():
    """A centred row of three pills; «ME GUSTA» and the bell are white and turn coral when pressed, «SUSCRÍBETE» turns
    grey «SUSCRITO» between them."""
    D = 5.5
    t = _kit("fila-tres", "Fila de tres botones", "Row of three buttons", D, 8411,
             ["suscríbete", "me gusta", "campana", "fila"], thumb_at=3.6)
    photo_bg(t, "h-sport-03", s1=1.03, label="Tu video")
    size, cy, gap = 38, 945, 28
    w1 = _btn_width("ME GUSTA", size, True)
    w2 = _btn_width("SUSCRÍBETE", size, True)
    w3 = _btn_width("CAMPANA", size, True)
    x = 960 - (w1 + w2 + w3 + 2 * gap) / 2
    end = D - 0.4
    # Like: white, then coral at 1.4.
    _btn(t, x, cy, "ME GUSTA", size, 0.2, 1.2, fg=INK, bg=WHITE, icon="thumb", motion=_until(1.2, 1.2), name="Me gusta")
    _btn(t, x, cy, "ME GUSTA", size, 1.4, end - 1.4, icon="thumb", motion=_from(end - 1.4), ad=0.12, name="Me gusta activo")
    _ripple(t, x + w1 / 2, cy, 1.4)
    x2 = x + w1 + gap
    _subscribe_swap(t, x2, cy, size, 0.35, 2.1, end)
    _ripple(t, x2 + w2 / 2, cy, 2.1)
    x3 = x2 + w2 + gap
    _btn(t, x3, cy, "CAMPANA", size, 0.5, 2.3, fg=INK, bg=WHITE, icon="bell", motion=_until(2.3, 2.3), name="Campana")
    _btn(t, x3, cy, "CAMPANA", size, 2.8, end - 2.8, icon="bell", motion=_from(end - 2.8), ad=0.12, ring_at=0.2,
         name="Campana activa")
    _ripple(t, x3 + w3 / 2, cy, 2.8)
    return t


TEMPLATES = [boton_canal, pildora_iconos, yt_suscrito, pila_vertical, me_gusta, tarjeta_lista, suscribete_contorno,
             suscribete_texto, campana_texto, burbuja, nombre_botones, fila_tres]
