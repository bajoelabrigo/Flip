"""Kit de YouTube, batch h (2026-10-30): more subscribe buttons. Jorge's second commercial promo («20 elements»,
light and dark) brought ideas the first one lacked: cards with a video's thumbnail on top, a field that types
its own messages (subscribe, the bell, like) with a button the cursor presses, a card whose round picture
sticks out of it, and dark versions. Our own takes, with the kit's palette (no platform logo or red) and the
helpers of batch g. Section elementos; order 8210-8229.
"""

from __future__ import annotations

from kit import Box, centered, circle_photo, fill, keys, label, no_stroke, photo_bg, rrect, shadow, tanim
from templates_ytkit_a import BELL, OUT, _stroke, path
from templates_ytkit_f import THUMB
from templates_ytkit_g import (CORAL, GREY, INK, NAVY, SOFT, TEAL, WHITE, Cursor, _bell, _hollow, _kit, _like,
                               _ripple, _subscribe_button)

LIGHT = dict(card=WHITE, ink=INK, soft=SOFT, done_bg=GREY, done_ink=SOFT, field="#F1F4F8")
DARK = dict(card="#1B2130", ink="#F2F5FA", soft="#9AA6B8", done_bg="#2C3445", done_ink="#B7C1D1", field="#262D3D")


def _slide(dur, dy=60):
    """Every piece of a card rises in and sinks out together (same offsets, so the card holds together)."""
    return [(0, {"dy": dy}, "out"), (0.45, {}, "hold"), (dur - 0.35, {}, "in"), (dur, {"dy": dy})]


def _fade(dur):
    return keys([(0, 0.0, "out"), (0.3, 1.0, "hold"), (dur - 0.3, 1.0), (dur, 0.0)])


def _card(t, th, box, t0, dur, radius=20):
    rrect(t, t.track("shape", "Tarjeta"), th["card"], t0, dur, box, radius=radius, motion=_slide(dur),
          layers=[shadow("#000000", 0, 14, 34, 0.4), fill(th["card"]), no_stroke()], opacity=_fade(dur))


def _text(t, th, content, box, t0, dur, size, colour=None, weight=700, align="left", name=None, font="Sora"):
    label(t, t.track("text", "Textos"), content, t0, dur, box, font, size, colour or th["ink"], weight=weight,
          align=align, motion=_slide(dur), opacity=_fade(dur), name=name or content)


def _avatar(t, sample, cx, cy, d, t0, dur, ring=TEAL):
    t.solid(t.track("shape", "Aro"), ring, t0, dur, centered(cx, cy, d + 8, d + 8), _slide(dur), kind="ellipse",
            opacity=_fade(dur))
    circle_photo(t, sample, t0, dur, centered(cx, cy, d, d), _slide(dur), label="Foto del canal")


# --- 1/2. Tarjeta con video -----------------------------------------------------------------------------------

def _video_card(th, id, es, en, order, sample, video, avatar, likes, at_left):
    D = 6.5
    tags = ["tarjeta", "video", "miniatura", "campana"] + (["oscuro"] if th is DARK else ["claro"])
    t = _kit(id, es, en, D, order, tags, thumb_at=4.2)
    photo_bg(t, sample, s1=1.03, label="Tu video")
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    card = Box(110 if at_left else 1920 - 110 - 560, 560, 560, 420)
    _card(t, th, card, t0, dur)
    thumb = Box(card.x + 16, card.y + 16, card.w - 32, 282)
    t.photo(t.track("video", "Video recomendado"), video, t0, dur, thumb, _slide(dur), label="Video recomendado",
            opacity=_fade(dur))
    t.solid(t.track("shape", "Duración"), "#000000", t0 + 0.4, dur - 0.6, Box(thumb.x + thumb.w - 82, thumb.y + thumb.h - 40, 70, 30),
            _slide(dur - 0.6), radius=6, kind="rounded-rectangle", opacity=keys([(0, 0.0), (0.3, 0.75, "hold"),
                                                                                 (dur - 0.9, 0.75), (dur - 0.6, 0.0)]))
    _text(t, th, "8:24", Box(thumb.x + thumb.w - 82, thumb.y + thumb.h - 40, 70, 30), t0 + 0.4, dur - 0.6, 18,
          WHITE, weight=700, align="center", name="Duración")
    cy = card.y + 360
    _avatar(t, avatar, card.x + 50, cy, 56, t0 + 0.1, dur - 0.1)
    _text(t, th, "Tu canal", Box(card.x + 92, cy - 30, 220, 32), t0 + 0.2, dur - 0.3, 22, name="Nombre del canal")
    _text(t, th, "77 mil suscriptores", Box(card.x + 92, cy + 2, 220, 26), t0 + 0.25, dur - 0.35, 15, th["soft"],
          weight=500, font="Inter", name="Suscriptores")
    if likes:
        btn = Box(card.x + card.w - 186, cy - 4, 166, 40)
    else:
        btn = Box(card.x + card.w - 206, cy - 22, 140, 44)
    c_a, c_b = 1.9, 2.9
    a, b = t0 + 0.6, t1 - 0.35
    if likes:
        # Likes with their count over the button, a dislike beside them; the cursor likes, then subscribes.
        ly = cy - 26
        _like(t, btn.x + 14, ly, 24, a, c_a, b, colour=th["ink"])
        _text(t, th, "50 mil", Box(btn.x + 32, ly - 14, 90, 28), a, c_a + 0.05 - a, 16, weight=700, font="Inter",
              name="Me gusta antes")
        label(t, t.track("text", "Me gusta"), "50,1 mil", c_a + 0.05, b - c_a - 0.05, Box(btn.x + 32, ly - 14, 90, 28),
              "Inter", 16, th["ink"], weight=700, align="left", anim_in=tanim("slide-up", duration=0.25),
              anim_out=OUT(0.2), name="Me gusta después")
        path(t, t.track("shape", "No me gusta"), th["ink"], a, b - a, centered(btn.x + btn.w - 14, ly + 2, 22, 22),
             THUMB, layers=[_hollow(), _stroke(th["ink"], 3)], rotation=keys([(0, 180.0)]),
             opacity=_fade(b - a))
        _subscribe_button(t, btn, a, c_b, b + 0.05, 15, done_bg=th["done_bg"], done_ink=th["done_ink"])
        stops = [(c_a, btn.x + 20, ly + 6), (c_b, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6)]
    else:
        _subscribe_button(t, btn, a, c_a, b + 0.05, 16, done_bg=th["done_bg"], done_ink=th["done_ink"])
        bx = card.x + card.w - 36
        _bell(t, bx, cy, 30, a + 0.1, c_b, b, colour=th["ink"], on=TEAL if th is DARK else NAVY)
        stops = [(c_a, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_b, bx + 6, cy + 8)]
    Cursor(t, 1.0, t1 - 0.5, (card.x + card.w + 260, card.y - 120), stops)
    return t


def tarjeta_video():
    return _video_card(LIGHT, "boton-tarjeta-video", "Tarjeta de video con suscribirse",
                       "Video card with subscribe", 8210, "h-tech-01", "h-travel-02", "h-portrait-04", False, True)


def tarjeta_video_oscura():
    return _video_card(DARK, "boton-tarjeta-video-oscura", "Tarjeta de video oscura con me gusta",
                       "Dark video card with likes", 8211, "h-studio-01", "h-food-01", "h-portrait-06", True, False)


# --- 3. Tarjeta de video vertical -----------------------------------------------------------------------------------

def tarjeta_video_vertical():
    """A narrow card at the right: the thumbnail, a wide «SUSCRIBIRME», and like and the bell under it."""
    D = 6.0
    t = _kit("boton-tarjeta-video-vertical", "Tarjeta de video angosta", "Narrow video card", D, 8212,
             ["tarjeta", "video", "miniatura", "angosta", "campana"], thumb_at=4.0)
    photo_bg(t, "h-cafe-04", s1=1.03, label="Tu video")
    th = LIGHT
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    card = Box(1500, 520, 300, 330)
    _card(t, th, card, t0, dur)
    t.photo(t.track("video", "Video recomendado"), "h-nature-05", t0, dur, Box(card.x + 16, card.y + 16, 268, 151),
            _slide(dur), label="Video recomendado", opacity=_fade(dur))
    _text(t, th, "Tu canal", Box(card.x + 16, card.y + 172, 268, 34), t0 + 0.2, dur - 0.3, 22, align="center",
          name="Nombre del canal")
    a, b = t0 + 0.6, t1 - 0.35
    c_sub, c_like, c_bell = 1.8, 2.8, 3.6
    btn = Box(card.x + 24, card.y + 214, 252, 52)
    _subscribe_button(t, btn, a, c_sub, b + 0.05, 20, done_bg=th["done_bg"], done_ink=th["done_ink"])
    iy = card.y + 296
    lx, bx = card.x + 110, card.x + 190
    _like(t, lx, iy, 30, a + 0.1, c_like, b)
    _bell(t, bx, iy, 30, a + 0.15, c_bell, b)
    Cursor(t, 1.0, t1 - 0.5, (1200, 420),
           [(c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_like, lx + 6, iy + 8), (c_bell, bx + 6, iy + 8)])
    return t


# --- 4. Mensajes que se escriben -----------------------------------------------------------------------------------

PLAY = "M 25 10 L 90 50 L 25 90 Z"


def mensajes():
    """The channel's picture and name, and under them a field that types three messages one after another
    («Suscríbete al canal», «Activa la campana», «Dale me gusta»); each has its button at the right end, the
    cursor presses it, it lights up, and the next message comes."""
    D = 9.0
    t = _kit("boton-mensajes", "Mensajes que se escriben solos", "Self-typing messages", D, 8213,
             ["mensajes", "escribir", "máquina de escribir", "campana", "me gusta"], thumb_at=5.0)
    photo_bg(t, "h-podcast-02", s1=1.03, label="Tu video")
    th = LIGHT
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    x, y = 1360, 760
    _avatar(t, "h-portrait-03", x + 38, y + 38, 70, t0, dur)
    label(t, t.track("text", "Textos"), "Tu canal", t0 + 0.15, dur - 0.3, Box(x + 90, y + 14, 400, 48), "Sora", 32,
          WHITE, weight=700, align="left", motion=_slide(dur - 0.3), opacity=_fade(dur - 0.3), name="Nombre del canal",
          layers=[shadow("#000000", 0, 3, 10, 0.6), fill(WHITE)])
    field = Box(x, y + 100, 440, 66)
    rrect(t, t.track("shape", "Campo"), th["card"], t0 + 0.3, dur - 0.3, field, radius=14, motion=_slide(dur - 0.3),
          layers=[shadow("#000000", 0, 10, 26, 0.35), fill(th["card"]), no_stroke()], opacity=_fade(dur - 0.3))
    msgs = [("Suscríbete al canal", PLAY, CORAL, "Mensaje 1"), ("Activa la campana", BELL, NAVY, "Mensaje 2"),
            ("Dale me gusta", THUMB, TEAL, "Mensaje 3")]
    slot = 2.1
    first = 1.0
    stops = []
    bx, by = field.x + field.w - 40, field.y + field.h / 2
    for i, (text, icon, colour, name) in enumerate(msgs):
        s0 = first + i * slot
        s1 = s0 + slot - 0.1 if i < 2 else t1 - 0.4
        type_len = 0.05 * len(text)
        click = s0 + type_len + 0.55
        label(t, t.track("text", "Mensajes"), text, s0, s1 - s0, Box(field.x + 24, field.y, field.w - 100, field.h),
              "Inter", 26, th["ink"], weight=500, align="left",
              anim_in=tanim("typewriter", duration=type_len), anim_out=OUT(0.2), name=name)
        # The button waits in outline while the line types.
        path(t, t.track("shape", "Botones"), th["ink"], s0 + 0.1, click - s0 - 0.1, centered(bx, by, 30, 30), icon,
             layers=[_hollow(), _stroke(th["ink"], 3.5)],
             motion=[(0, {"s": 0.0}, "back"), (0.35, {})])
        rest = s1 - click
        # Keys in order also on a short life (under 0.65 s the hold landed after the shrink and the icon
        # vanished in one frame instead of shrinking away).
        hold = min(0.4, max(0.14, rest - 0.3))
        shrink = max(hold + 0.02, rest - 0.25)
        path(t, t.track("shape", "Botones"), colour, click, rest, centered(bx, by, 30, 30), icon, filled=True,
             motion=[(0, {"s": 0.6}, "out"), (0.12, {"s": 1.35}, "back"), (hold, {}, "hold"), (shrink, {}, "in"),
                     (rest, {"s": 0.0})])
        _ripple(t, bx, by, click, 40)
        stops.append((click, bx + 6, by + 8))
    Cursor(t, 1.2, t1 - 0.5, (1100, 640), stops)
    return t


# --- 5. Foto en el centro ---------------------------------------------------------------------------------------------

def foto_central():
    """A wide card with the name at the left, a big round picture in the middle that sticks out of it, and like,
    the bell and «SUSCRIBIRME» at the right."""
    D = 6.0
    t = _kit("boton-foto-central", "Tarjeta con la foto en el centro", "Card with the picture in the middle", D,
             8214, ["tarjeta", "foto", "centro", "campana", "me gusta"], thumb_at=4.0)
    photo_bg(t, "h-city-05", s1=1.03, label="Tu video")
    th = LIGHT
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    card = Box(560, 880, 800, 120)
    cy = card.y + card.h / 2
    _card(t, th, card, t0, dur, radius=18)
    _avatar(t, "h-portrait-01", 960, cy, 150, t0 + 0.15, dur - 0.15)
    _text(t, th, "Tu canal", Box(card.x + 34, card.y + 20, 300, 44), t0 + 0.25, dur - 0.4, 30, name="Nombre del canal")
    _text(t, th, "77 mil suscriptores", Box(card.x + 34, card.y + 64, 300, 32), t0 + 0.3, dur - 0.45, 18, th["soft"],
          weight=500, font="Inter", name="Suscriptores")
    a, b = t0 + 0.6, t1 - 0.35
    c_like, c_bell, c_sub = 1.8, 2.6, 3.4
    lx, bx = 1150, 1250
    iy = card.y + 34
    _like(t, lx, iy, 30, a, c_like, b)
    _bell(t, bx, iy, 30, a + 0.05, c_bell, b)
    btn = Box(1100, card.y + 62, 210, 44)
    _subscribe_button(t, btn, a + 0.1, c_sub, b + 0.05, 17)
    Cursor(t, 1.0, t1 - 0.5, (1600, 640),
           [(c_like, lx + 6, iy + 8), (c_bell, bx + 6, iy + 8), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6)])
    return t


# --- 6. Barra oscura ---------------------------------------------------------------------------------------------------

def barra_oscura():
    """A dark card at the top: picture, name and a line about the channel, like, «SUSCRIBIRME» and the bell."""
    D = 6.0
    t = _kit("boton-barra-oscura", "Barra oscura con suscribirse", "Dark subscribe bar", D, 8215,
             ["barra", "oscuro", "campana", "me gusta"], thumb_at=4.0)
    photo_bg(t, "h-concert-01", s1=1.03, label="Tu video")
    th = DARK
    t0, t1 = 0.3, D - 0.2
    dur = t1 - t0
    card = Box(560, 90, 800, 120)
    cy = card.y + card.h / 2
    _card(t, th, card, t0, dur)
    _avatar(t, "h-portrait-05", card.x + 70, cy, 76, t0 + 0.1, dur - 0.1)
    _text(t, th, "Tu canal", Box(card.x + 128, cy - 34, 320, 40), t0 + 0.2, dur - 0.35, 28, name="Nombre del canal")
    _text(t, th, "Música en vivo cada semana", Box(card.x + 128, cy + 6, 320, 30), t0 + 0.25, dur - 0.4, 17, th["soft"],
          weight=500, font="Inter", name="Sobre el canal")
    a, b = t0 + 0.6, t1 - 0.35
    c_like, c_sub, c_bell = 1.8, 2.7, 3.6
    lx = card.x + 480
    _like(t, lx, cy, 34, a, c_like, b, colour=th["ink"])
    btn = Box(card.x + 520, cy - 25, 200, 50)
    _subscribe_button(t, btn, a + 0.05, c_sub, b + 0.05, 18, done_bg=th["done_bg"], done_ink=th["done_ink"])
    bx = card.x + card.w - 42
    _bell(t, bx, cy, 34, a + 0.1, c_bell, b, colour=th["ink"], on=TEAL)
    Cursor(t, 1.0, t1 - 0.5, (1700, 420),
           [(c_like, lx + 6, cy + 8), (c_sub, btn.x + btn.w * 0.6, btn.y + btn.h * 0.6), (c_bell, bx + 6, cy + 8)])
    return t


TEMPLATES = [tarjeta_video, tarjeta_video_oscura, tarjeta_video_vertical, mensajes, foto_central, barra_oscura]
