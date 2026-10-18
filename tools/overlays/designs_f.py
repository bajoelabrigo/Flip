"""Sixth batch: YouTuber (subscribe buttons, like/comment/share pops, arrows, highlights, 3-D emoji
reactions, notifications, counters). Icon-only where possible; the few with words come in Spanish and
English, with the language in their id and name. Everything sits in the lower third or the centre and is
drawn with kit.py (crisp vector-ish sprites with gradients, gloss and soft shadows).
"""

from __future__ import annotations

import math

import numpy as np

import fx
from fx import TAU, Canvas
from designs import design
from kit import (Art, Pen, Sprite, back_in, back_out, badge, bezier, blur, burst_lines, damped, ease_in, ease_io,
                 ease_io5, ease_out, elastic_out, grow, hand_details, hexc, icon_bell, icon_check, icon_comment,
                 icon_cross, icon_cursor, icon_eye, icon_hand, icon_heart, icon_person, icon_play, icon_share,
                 icon_thumb, lerp, mix, outlined, partial, pill_button, pop_scale, put, ripple, seg, shift, text_width)

YT = ["youtuber", "youtube", "creador", "creator", "redes sociales", "social media", "streamer", "vlog"]
BOLD = "Montserrat-ExtraBold.ttf"
BLACK = "Montserrat-Black.ttf"

RED_T, RED_B = hexc("#ff4040"), hexc("#d3001b")
GREY_T, GREY_B = hexc("#f4f4f4"), hexc("#cfcfd2")
INK = hexc("#2b2b30")
WHITE = (1.0, 1.0, 1.0)


def yt(id, es, en, seconds, *, loop=False, tags=(), sample="portrait-04.jpg", thumb_at=0.6, crf=34):
    return design(id, es, en, "youtuber", seconds, loop=loop, tags=YT + list(tags), sample=sample,
                  thumb_at=thumb_at, crf=crf)


def spot(w, h, v=0.72, hz=0.74):
    """Where a lower-third element goes: centred, low in a vertical frame, a bit lower in a wide one."""
    return w / 2, (h * v if h > w else h * hz)


def local(x, y, rot, sc, dx, dy):
    """A point (dx, dy) of an element centred at (x, y), rotated (degrees) and scaled with it."""
    th = math.radians(rot)
    return x + sc * (dx * math.cos(th) - dy * math.sin(th)), y + sc * (dx * math.sin(th) + dy * math.cos(th))


def sound_arcs(c: Canvas, x, y, R, age, color=WHITE, width=9.0, op=1.0):
    """Two pairs of arcs on both sides of a ringing bell, pulsing outwards."""
    if age < 0 or op <= 0:
        return
    size = int(2 * R * 1.5 + 4 * width)
    p = Pen(size, size)
    m = size / 2
    for k in range(2):
        ph = (age * 2.2 - k * 0.35) % 1.0
        a = math.sin(math.pi * ph) * op
        r = R * (0.95 + 0.4 * k + 0.12 * ph)
        for side in (0, math.pi):
            pts = [(m + r * math.cos(side + t), m + r * math.sin(side + t)) for t in np.linspace(-0.55, 0.55, 24)]
            p.line(pts, width, int(255 * a))
    c.splat(p.cov(), x, y, color, 1.0)


def confetti_pop(c: Canvas, x, y, age, seed, n=14, speed=520.0, colors=None, size=14.0, dur=1.1):
    """Little discs and bars thrown out of a pop, with gravity."""
    if age < 0 or age > dur:
        return
    rng = np.random.default_rng(seed)
    colors = colors or [hexc(h) for h in ("#ff4d6d", "#ffd23f", "#3ec1ff", "#7bf06a", "#b26bff", "#ffffff")]
    u = age / dur
    for i in range(n):
        a = rng.uniform(0, TAU)
        v = speed * rng.uniform(0.55, 1.0)
        px = x + math.cos(a) * v * age
        py = y + math.sin(a) * v * age + 900 * age * age
        r = size * rng.uniform(0.5, 1.0)
        col = colors[i % len(colors)]
        op = 1 - ease_in(u, 2)
        if i % 2:
            c.splat(fx.disc(max(int(r * 0.6), 1)), px, py, col, op)
        else:
            c.splat(fx.confetti(int(r * 2), 0.4, a + age * 9, math.cos(age * 11 + i)), px, py, col, op)


# ================================================================ subscribe buttons

LABELS = {"es": ("SUSCRÍBETE", "SUSCRITO"), "en": ("SUBSCRIBE", "SUBSCRIBED")}


def _bell_parts(size, disc_top, disc_bot, bell_color, ring=None):
    """A round button and the bell on it as separate sprites (the bell swings on its own pivot)."""
    disc = badge(lambda p: None, size, disc_top, disc_bot, ring=ring)
    art = Art(size * 0.7, size * 0.7)
    p = art.pen(size * 0.5 / 100, size * 0.1, size * 0.08)
    icon_bell(p)
    cov = p.cov()
    art.paint(shift(blur(cov, size * 0.01), 0, size * 0.015), (0, 0, 0), 0.18)
    art.paint(cov, bell_color)
    pivot = (size * 0.1 + 50 * size * 0.005, size * 0.08 + 6 * size * 0.005)
    return disc, art.sprite(), pivot


def _red_dot(size):
    art = Art(size * 1.5, size * 1.5)
    p = art.pen(1, size * 0.25, size * 0.25)
    p.circle(size / 2, size / 2, size / 2)
    cov = p.cov()
    art.shadow(cov, 0, size * 0.05, size * 0.08, 0.3)
    art.paint(grow(cov, size * 0.09), WHITE)
    art.vgrad(cov, hexc("#ff5a5a"), hexc("#e0001e"), size * 0.25, size * 1.25)
    return art.sprite()


def _neon_button(text, height, color, on=True, icon=None):
    th = height * 0.40
    tw = text_width(text, BOLD, th)
    ic = height * 0.5 if icon else 0
    gap = height * 0.2 if icon else 0
    w = tw + ic + gap + height * 1.0
    pad = height * 0.6
    art = Art(w + 2 * pad, height + 2 * pad)
    body = art.pen(1, pad, pad)
    body.rrect((0, 0, w, height), height * 0.5)
    bc = body.cov()
    art.paint(bc, hexc("#0b0b12"), 0.72)
    o = art.pen(1, pad, pad)
    o.rrect_line((0, 0, w, height), height * 0.5, height * 0.06)
    oc = o.cov()
    col = color if on else hexc("#9a9aa6")
    if on:
        art.glow(oc, height * 0.16, col, 0.95, 2.2)
    art.paint(oc, mix(col, WHITE, 0.45 if on else 0.1))
    x = (w - tw - ic - gap) / 2
    if icon:
        ip = art.pen(ic / 100, pad + x, pad + (height - ic) / 2)
        icon(ip)
        art.paint(ip.cov(), WHITE)
        x += ic + gap
    tp = art.pen(1, pad, pad)
    tp.text((x + tw / 2, height * 0.52), text, BOLD, th)
    tc = tp.cov()
    if on:
        art.glow(tc, height * 0.1, col, 0.8, 1.4)
    art.paint(tc, WHITE if on else hexc("#d8d8de"))
    return art.sprite(), w


def _subscribe(style, lang):
    on_text, off_text = LABELS[lang]

    def make(w, h, T, rng):
        s = min(w, h) / 1080
        bh = (118 if style == "tarjeta" else 138) * s
        if style == "neon":
            on, bw = _neon_button(on_text, bh, hexc("#ff2a4a"), True, icon=lambda p: icon_play(p))
            off, bw2 = _neon_button(off_text, bh, hexc("#ff2a4a"), False, icon=lambda p: icon_check(p, width=15))
            disc, bell, piv = _bell_parts(bh * 1.04, hexc("#1a1a24"), hexc("#0b0b12"), WHITE, ring=hexc("#ff2a4a"))
        elif style == "pildora":
            on, bw = pill_button(on_text, BOLD, bh, hexc("#ffffff"), hexc("#e9e9ee"), INK,
                                 icon=lambda p: icon_play(p), icon_color=hexc("#ff2a2a"))
            off, bw2 = pill_button(off_text, BOLD, bh, hexc("#3a3a42"), hexc("#25252b"), hexc("#e8e8ee"),
                                   icon=lambda p: icon_check(p, width=15))
            disc, bell, piv = _bell_parts(bh * 1.04, hexc("#ffffff"), hexc("#e6e6ec"), INK)
        else:   # clasico / tarjeta
            on, bw = pill_button(on_text, BOLD, bh, RED_T, RED_B, WHITE, icon=lambda p: icon_play(p), radius=0.28)
            off, bw2 = pill_button(off_text, BOLD, bh, GREY_T, GREY_B, INK,
                                   icon=lambda p: icon_check(p, width=15), radius=0.28)
            if style == "tarjeta":
                disc, bell, piv = _bell_parts(bh * 1.04, hexc("#34343c"), hexc("#1d1d22"), WHITE)
            else:
                disc, bell, piv = _bell_parts(bh * 1.04, hexc("#ffffff"), hexc("#e4e4ea"), INK)
        bw = max(bw, bw2)
        dot = _red_dot(30 * s)
        cur, cpad = outlined(icon_cursor, 120 * s)
        cur_tip = (cpad + 10 * 1.2 * s, cpad + 4 * 1.2 * s)
        gap = 50 * s
        bd = bh * 1.04
        avatar = None
        if style == "tarjeta":
            av = 128 * s
            art = Art(av * 1.3, av * 1.3)
            ap = art.pen(av / 100, av * 0.15, av * 0.15)
            ap.circle(50, 50, 50)
            ac = ap.cov()
            art.shadow(ac, 0, 6 * s, 8 * s, 0.35)
            art.lgrad(ac, hexc("#ffb02e"), hexc("#ff2d6f"), (av * 0.15, av * 0.15), (av * 1.15, av * 1.15))
            ip = art.pen(av / 100, av * 0.15, av * 0.15)
            ip.circle(50, 50, 44)
            art.paint(ip.cov(), hexc("#26262c"))
            pp = art.pen(av * 0.62 / 100, av * 0.15 + av * 0.19, av * 0.15 + av * 0.2)
            icon_person(pp)
            art.paint(pp.cov() * ip.cov(), hexc("#e9e9ef"))
            avatar = art.sprite()
            total = av + 26 * s + bw + gap + bd
            cw, chh = total + 2 * 44 * s, av + 2 * 36 * s
            art = Art(cw + 60 * s, chh + 60 * s)
            cp = art.pen(1, 30 * s, 30 * s)
            cp.rrect((0, 0, cw, chh), 40 * s)
            cc = cp.cov()
            art.shadow(cc, 0, 12 * s, 22 * s, 0.45)
            art.vgrad(cc, hexc("#1e1e24"), hexc("#111115"), 30 * s, 30 * s + chh, opacity=0.92)
            bp = art.pen(1, 30 * s, 30 * s)
            bp.rrect_line((0, 0, cw, chh), 40 * s, 2.2 * s)
            art.paint(bp.cov(), WHITE, 0.12)
            card = art.sprite()
        else:
            total = bw + gap + bd
        cx, cy = spot(w, h)
        x0 = cx - total / 2
        if avatar is not None:
            ax = x0 + av / 2
            bx = x0 + av + 26 * s + bw / 2
        else:
            bx = x0 + bw / 2
        lx = bx + bw / 2 + gap + bd / 2
        t_click, t_bell = 1.5, 2.6
        click_pt = (bx + bw * 0.12, cy + bh * 0.18)
        bell_pt = (lx + bd * 0.12, cy + bd * 0.16)
        start = (cx + 0.42 * w, cy + 0.3 * h)
        end = (cx + 0.5 * w, cy + 0.45 * h)
        t_out = T - 0.7

        def cursor_at(t):
            if t < 0.6:
                return None
            if t < 1.4:
                u = ease_io5(seg(t, 0.6, 1.4))
                a, b = start, click_pt
                bend = math.sin(math.pi * u) * 70 * s
            elif t < 1.95:
                return click_pt
            elif t < 2.5:
                u = ease_io5(seg(t, 1.95, 2.5))
                a, b = click_pt, bell_pt
                bend = -math.sin(math.pi * u) * 40 * s
            elif t < 3.0:
                return bell_pt
            else:
                u = ease_in(seg(t, 3.0, 3.7), 2)
                a, b = bell_pt, end
                bend = 0
            x = lerp(a[0], b[0], u)
            y = lerp(a[1], b[1], u) - bend
            return x, y

        def frame(t):
            c = Canvas(w, h)
            k = pop_scale(t, 0.0, t_out, 0.5, 0.35)
            if style == "tarjeta":
                rise = (1 - ease_out(seg(t, 0.0, 0.45))) * 60 * s + ease_in(seg(t, t_out, t_out + 0.35)) * 60 * s
                op = seg(t, 0.0, 0.3) * (1 - seg(t, t_out + 0.1, t_out + 0.4))
                put(c, card, cx, cy + rise, opacity=op)
                put(c, avatar, ax, cy + rise, scale=pop_scale(t, 0.15, t_out, 0.5, 0.3))
            press = 1 - 0.07 * math.sin(math.pi * seg(t, t_click - 0.05, t_click + 0.17))
            sw = seg(t, t_click, t_click + 0.12)
            bump = 1 + 0.06 * math.sin(math.pi * seg(t, t_click + 0.05, t_click + 0.35))
            kb = pop_scale(t, 0.08, t_out, 0.5, 0.35) * press * bump
            if sw < 1:
                put(c, on, bx, cy, scale=kb, opacity=1 - sw)
            if sw > 0:
                put(c, off, bx, cy, scale=kb, opacity=sw)
            ripple(c, click_pt[0], click_pt[1], t - t_click, 90 * s, WHITE if style != "pildora" else INK, 5 * s)
            kd = pop_scale(t, 0.22, t_out + 0.05, 0.5, 0.35)
            kd *= 1 - 0.08 * math.sin(math.pi * seg(t, t_bell - 0.05, t_bell + 0.15))
            put(c, disc, lx, cy, scale=kd)
            swing = 24 * damped(t - t_bell, 2.6, 2.2) + 10 * math.sin(math.pi * seg(t, 0.25, 0.75)) * (t < 0.75)
            bpx, bpy = local(lx, cy, 0, kd, piv[0] - bell.w / 2, piv[1] - bell.h / 2)
            put(c, bell, bpx, bpy, scale=kd, rot=swing, pivot=piv)
            ring = (1 - seg(t, t_bell + 1.1, t_bell + 1.5)) * (t > t_bell)
            arc_col = INK if style in ("clasico", "pildora") else WHITE
            sound_arcs(c, lx, cy, bd * 0.62 * kd, t - t_bell, arc_col, 7 * s, ring)
            dk = pop_scale(t, t_bell + 0.1, t_out + 0.05, 0.45, 0.3)
            dx, dy = local(lx, cy, 0, kd, bd * 0.34, -bd * 0.34)
            put(c, dot, dx, dy, scale=dk)
            p = cursor_at(t)
            if p is not None:
                pr = 1 - 0.14 * math.sin(math.pi * seg(t, t_click - 0.08, t_click + 0.12)) \
                    - 0.14 * math.sin(math.pi * seg(t, t_bell - 0.08, t_bell + 0.12))
                fade = seg(t, 0.6, 0.8) * (1 - seg(t, 3.45, 3.7))
                put(c, cur, p[0], p[1], scale=pr, pivot=cur_tip, opacity=fade)
            return c
        return frame
    return make


SUB_STYLES = {
    "clasico": ("clásico", "classic", "classic", "portrait-04.jpg"),
    "pildora": ("blanco", "white", "white", "man-01.jpg"),
    "neon": ("neón", "neon", "neon", "podcast-01.jpg"),
    "tarjeta": ("con tarjeta", "card", "card", "portrait-02.jpg"),
}
for style, (es_s, en_s, en_id, smp) in SUB_STYLES.items():
    for lang in ("es", "en"):
        if lang == "es":
            oid = f"yt-suscribete-{style}-es"
            es = f"Botón Suscríbete {es_s} (español)"
            en = f"{en_s.capitalize()} subscribe button (Spanish)"
            tags = ["suscribete", "suscribirse", "suscripcion", "campana", "español"]
        else:
            oid = f"yt-subscribe-{en_id}-en"
            es = f"Botón Subscribe {es_s} (inglés)"
            en = f"{en_s.capitalize()} subscribe button (English)"
            tags = ["subscribe", "subscribed", "bell", "notifications", "english", "ingles"]
        yt(oid, es, en, 5.0, tags=tags + ["boton", "button", "clic", "cursor"], sample=smp, thumb_at=0.62)(
            _subscribe(style, lang))


# ================================================================ like / comment / share

BADGES = {
    "like": (icon_thumb, "#5aa9ff", "#1d5fe3"),
    "comment": (lambda p: icon_comment(p), "#43e08f", "#0f9f55"),
    "comment_nodots": (lambda p: icon_comment(p, dots=False), "#43e08f", "#0f9f55"),
    "share": (icon_share, "#b384ff", "#6a2fe6"),
    "bell": (icon_bell, "#ffd84d", "#f19600"),
    "heart": (icon_heart, "#ff6f8c", "#e0173f"),
}


def _badge(kind, size):
    fn, a, b = BADGES[kind]
    return badge(fn, size, hexc(a), hexc(b))


def _icon_sprite(fn, size, color=WHITE):
    art = Art(size * 1.2, size * 1.2)
    p = art.pen(size / 100, size * 0.1, size * 0.1)
    fn(p)
    cov = p.cov()
    art.paint(shift(blur(cov, size * 0.02), 0, size * 0.03), (0, 0, 0), 0.22)
    art.paint(cov, color)
    return art.sprite()


@yt("yt-like-pop", "Me gusta que aparece", "Like pop", 2.6, tags=["like", "me gusta", "pulgar", "thumbs up"],
    sample="man-04.jpg", thumb_at=0.4)
def _like_pop(w, h, T, rng):
    s = min(w, h) / 1080
    size = 300 * s
    disc = badge(lambda p: None, size, hexc("#5aa9ff"), hexc("#1d5fe3"))
    thumb = _icon_sprite(icon_thumb, size * 0.56)
    cx, cy = spot(w, h, 0.66, 0.6)

    def frame(t):
        c = Canvas(w, h)
        k = pop_scale(t, 0.0, T - 0.4, 0.55, 0.32)
        burst_lines(c, cx, cy, t - 0.18, size * 0.6, size * 0.95, hexc("#5aa9ff"), 10, 14 * s, 0.5)
        confetti_pop(c, cx, cy, t - 0.2, 7, 16, 700 * s, size=16 * s)
        put(c, disc, cx, cy, scale=k)
        nod = -28 * (1 - back_out(seg(t, 0.05, 0.6), 2.4)) + 14 * damped(t - 0.9, 2.2, 3.5)
        put(c, thumb, cx - size * 0.02, cy, scale=k * (1 + 0.12 * math.sin(math.pi * seg(t, 0.85, 1.15))), rot=nod)
        return c
    return frame


@yt("yt-comentario-pop", "Comentario que aparece", "Comment pop", 3.0,
    tags=["comentario", "comentar", "comment", "chat", "mensaje"], sample="portrait-07.jpg", thumb_at=0.45)
def _comment_pop(w, h, T, rng):
    s = min(w, h) / 1080
    size = 300 * s
    disc = badge(lambda p: None, size, hexc("#43e08f"), hexc("#0f9f55"))
    bub = _icon_sprite(lambda p: icon_comment(p, dots=False), size * 0.56)
    dot = Sprite.from_canvas(_dot_art(size * 0.043, hexc("#14a75b")))
    cx, cy = spot(w, h, 0.66, 0.6)

    def frame(t):
        c = Canvas(w, h)
        k = pop_scale(t, 0.0, T - 0.4, 0.55, 0.32)
        burst_lines(c, cx, cy, t - 0.18, size * 0.6, size * 0.95, hexc("#43e08f"), 10, 14 * s, 0.5)
        put(c, disc, cx, cy, scale=k)
        wob = 10 * damped(t - 0.1, 1.6, 3.0)
        put(c, bub, cx, cy, scale=k, rot=wob)
        for i in range(3):
            jump = max(0.0, math.sin(TAU * (t * 1.6 - i * 0.18))) ** 2
            dx, dy = local(cx, cy, wob, k, (i - 1) * size * 0.112, -size * 0.05 - jump * size * 0.03)
            put(c, dot, dx, dy, scale=k * pop_scale(t, 0.3 + i * 0.08, None, 0.3))
        return c
    return frame


def _dot_art(r, color):
    art = Art(r * 2 + 4, r * 2 + 4)
    p = art.pen(1, 2, 2)
    p.circle(r, r, r)
    art.paint(p.cov(), color)
    return art


@yt("yt-compartir-pop", "Compartir que aparece", "Share pop", 2.6, tags=["compartir", "share", "enviar", "send"],
    sample="travel-03.jpg", thumb_at=0.45)
def _share_pop(w, h, T, rng):
    s = min(w, h) / 1080
    size = 300 * s
    disc = badge(lambda p: None, size, hexc("#b384ff"), hexc("#6a2fe6"))
    arrow = _icon_sprite(icon_share, size * 0.56)
    cx, cy = spot(w, h, 0.66, 0.6)

    def frame(t):
        c = Canvas(w, h)
        k = pop_scale(t, 0.0, T - 0.4, 0.55, 0.32)
        burst_lines(c, cx, cy, t - 0.18, size * 0.6, size * 0.95, hexc("#b384ff"), 10, 14 * s, 0.5)
        put(c, disc, cx, cy, scale=k)
        u = seg(t, 0.75, 1.25)
        dx = size * 0.16 * math.sin(math.pi * u) * (1 if u < 1 else 0)
        op = 1.0
        put(c, arrow, cx + dx * k, cy - dx * 0.4 * k, scale=k, rot=-8 * math.sin(math.pi * u), opacity=op)
        for j in range(3):
            if 0 < u < 1:
                ly = cy + (j - 1) * size * 0.11
                L = size * 0.18 * math.sin(math.pi * u)
                p = Pen(int(L + 20 * s), int(14 * s))
                p.line([(6 * s, 7 * s), (6 * s + L, 7 * s)], 7 * s)
                c.splat(p.cov(), cx - size * 0.58 - L / 2, ly, WHITE, 0.9 * math.sin(math.pi * u))
        return c
    return frame


@yt("yt-iconos-fila", "Me gusta, comentar y compartir", "Like, comment and share", 4.0,
    tags=["like", "comentar", "compartir", "share", "comment", "campana", "iconos", "icons", "llamada a la accion"],
    sample="cooking-02.jpg", thumb_at=0.55)
def _icon_row(w, h, T, rng):
    s = min(w, h) / 1080
    size = 190 * s
    kinds = ["like", "comment", "share", "bell"]
    sprites = [_badge(k_, size) for k_ in kinds]
    cx, cy = spot(w, h, 0.74, 0.78)
    gap = size * 1.22
    xs = [cx + (i - 1.5) * gap for i in range(4)]

    def frame(t):
        c = Canvas(w, h)
        for i, spr in enumerate(sprites):
            t0 = 0.1 + i * 0.16
            k = pop_scale(t, t0, T - 0.6 + i * 0.06, 0.5, 0.3)
            tap = 0.55 + i * 0.45 + 0.4
            k *= 1 + 0.16 * math.sin(math.pi * seg(t, tap, tap + 0.28))
            bob = 6 * s * math.sin(TAU * (t * 0.8 - i * 0.2))
            rot = 12 * damped(t - tap, 2.4, 4.0) if i != 3 else 22 * damped(t - tap, 3.0, 3.0)
            put(c, spr, xs[i], cy + bob, scale=k, rot=rot)
            burst_lines(c, xs[i], cy + bob, t - tap, size * 0.62, size * 0.85, WHITE, 8, 8 * s, 0.4)
        return c
    return frame


def _flat_disc(size, color, op):
    art = Art(size * 1.2, size * 1.2)
    p = art.pen(size / 100, size * 0.1, size * 0.1)
    p.circle(50, 50, 50)
    art.paint(p.cov(), color, op)
    return art.sprite()


def _label(text, size, color=WHITE, font=BOLD):
    tw = text_width(text, font, size)
    art = Art(tw + size, size * 1.8)
    p = art.pen(1, size / 2, size * 0.4)
    p.text((tw / 2, size * 0.5), text, font, size)
    cov = p.cov()
    art.paint(shift(blur(cov, size * 0.08), 0, size * 0.06), (0, 0, 0), 0.5)
    art.paint(cov, color)
    return art.sprite()


@yt("yt-iconos-lateral", "Botones laterales de video corto", "Short video side buttons", 4.5,
    tags=["shorts", "reels", "lateral", "like", "comentar", "compartir", "botones", "contador"],
    sample="fashion-04.jpg", thumb_at=0.62)
def _side_stack(w, h, T, rng):
    s = min(w, h) / 1080
    size = 132 * s
    disc = _flat_disc(size, (0.05, 0.05, 0.07), 0.45)
    icons = [_icon_sprite(icon_thumb, size * 0.56), _icon_sprite(lambda p: icon_comment(p), size * 0.56),
             _icon_sprite(icon_share, size * 0.56)]
    liked = _icon_sprite(icon_thumb, size * 0.56, hexc("#4aa3ff"))
    labels = [_label("12K", 40 * s), _label("845", 40 * s), _label("3K", 40 * s)]
    label2 = _label("13K", 40 * s)
    x = w - (110 * s if h > w else 120 * s)
    y0 = h * (0.55 if h > w else 0.36)
    step = 228 * s
    t_tap = 1.7

    def frame(t):
        c = Canvas(w, h)
        for i in range(3):
            t0 = 0.1 + i * 0.14
            u = ease_out(seg(t, t0, t0 + 0.45))
            o = 1 - ease_in(seg(t, T - 0.55 + i * 0.05, T - 0.25 + i * 0.05))
            dx = (1 - u + (1 - o)) * 200 * s
            y = y0 + i * step
            k = 1.0
            if i == 0:
                k = 1 + 0.2 * math.sin(math.pi * seg(t, t_tap, t_tap + 0.3))
            put(c, disc, x + dx, y, scale=k, opacity=u * o)
            spr = icons[i]
            if i == 0 and t >= t_tap + 0.08:
                spr = liked
            put(c, spr, x + dx, y, scale=k, rot=(-18 * damped(t - t_tap, 2.0, 4.0) if i == 0 else 0), opacity=u * o)
            lab = labels[i] if not (i == 0 and t >= t_tap + 0.25) else label2
            put(c, lab, x + dx, y + size * 0.78, opacity=u * o)
        burst_lines(c, x, y0, t - t_tap, size * 0.55, size * 0.85, hexc("#4aa3ff"), 8, 8 * s, 0.4)
        ripple(c, x, y0, t - t_tap, size * 0.9, WHITE, 5 * s)
        return c
    return frame


# ================================================================ cursors, bell, play

@yt("yt-cursor-clic", "Cursor que hace clic", "Clicking cursor", 3.0, loop=True,
    tags=["cursor", "clic", "click", "raton", "mouse", "pantalla", "tutorial"], sample="office-02.jpg", thumb_at=0.4)
def _cursor_loop(w, h, T, rng):
    s = min(w, h) / 1080
    cur, pad = outlined(icon_cursor, 150 * s)
    tip = (pad + 10 * 1.5 * s, pad + 4 * 1.5 * s)
    cx, cy = w / 2, h / 2
    rest = (cx + 260 * s, cy + 300 * s)

    def frame(t):
        c = Canvas(w, h)
        if t < 0.9:
            u = ease_io5(seg(t, 0.1, 0.9))
            x, y = lerp(rest[0], cx, u), lerp(rest[1], cy, u) - math.sin(math.pi * u) * 80 * s
        elif t < 1.6:
            x, y = cx, cy
        else:
            u = ease_io5(seg(t, 1.6, 2.7))
            x, y = lerp(cx, rest[0], u), lerp(cy, rest[1], u) + math.sin(math.pi * u) * 60 * s
        pr = 1 - 0.16 * math.sin(math.pi * seg(t, 0.98, 1.2))
        for k in range(2):
            ripple(c, cx, cy, t - 1.05 - k * 0.14, 130 * s, WHITE, 7 * s, 0.55)
        burst_lines(c, cx, cy, t - 1.05, 40 * s, 95 * s, hexc("#ffd23f"), 8, 9 * s, 0.38, rot=0.39)
        put(c, cur, x, y, scale=pr, pivot=tip)
        return c
    return frame


@yt("yt-mano-clic", "Mano que toca", "Tapping hand", 2.0, loop=True,
    tags=["mano", "hand", "tocar", "tap", "clic", "señalar", "aqui", "tutorial"], sample="shopping-02.jpg",
    thumb_at=0.3)
def _hand_loop(w, h, T, rng):
    s = min(w, h) / 1080
    hand, pad = outlined(icon_hand, 190 * s, details=hand_details)
    tip = (pad + 32 * 1.9 * s, pad + 4 * 1.9 * s)
    cx, cy = spot(w, h, 0.64, 0.58)

    def frame(t):
        c = Canvas(w, h)
        u = t / T
        press = math.sin(math.pi * seg(u, 0.25, 0.45))
        lift = (1 - press) * (0.5 + 0.5 * math.cos(TAU * u)) * 40 * s
        for k in range(2):
            ripple(c, cx, cy, t - 0.6 - k * 0.15, 120 * s, WHITE, 7 * s, 0.6)
        put(c, hand, cx + 6 * s, cy + 8 * s + lift, scale=1 - 0.1 * press, rot=-8 + 4 * press, pivot=tip)
        return c
    return frame


@yt("yt-campana", "Campana de notificaciones", "Notification bell", 3.0, loop=True,
    tags=["campana", "bell", "notificaciones", "notifications", "activa", "avisos"], sample="portrait-06.jpg",
    thumb_at=0.12)
def _bell_loop(w, h, T, rng):
    s = min(w, h) / 1080
    size = 280 * s
    disc, bell, piv = _bell_parts(size, hexc("#ffd84d"), hexc("#f19600"), WHITE)
    dot = _red_dot(64 * s)
    cx, cy = spot(w, h, 0.66, 0.6)

    def frame(t):
        c = Canvas(w, h)
        sw = 26 * damped(t - 0.15, 3.0, 3.6) + 26 * damped(t - 1.65, 3.0, 3.6)
        k = 1 + 0.05 * math.sin(math.pi * seg(t, 0.12, 0.32)) + 0.05 * math.sin(math.pi * seg(t, 1.62, 1.82))
        put(c, disc, cx, cy, scale=k)
        bx, by = local(cx, cy, 0, k, piv[0] - bell.w / 2, piv[1] - bell.h / 2)
        put(c, bell, bx, by, scale=k, rot=sw, pivot=piv)
        ring = max(math.exp(-2.5 * max(t - 0.15, 0)) * (t > 0.15), math.exp(-2.5 * max(t - 1.65, 0)) * (t > 1.65))
        sound_arcs(c, cx, cy, size * 0.66, t, WHITE, 10 * s, min(ring * 1.5, 1))
        dk = 1 + 0.12 * math.sin(TAU * 2 * t / T)
        put(c, dot, cx + size * 0.34, cy - size * 0.34, scale=dk)
        return c
    return frame


@yt("yt-boton-play", "Botón de reproducir", "Play button", 2.0, loop=True,
    tags=["play", "reproducir", "boton", "video", "ver", "watch"], sample="travel-05.jpg",
    thumb_at=0.3)
def _play_loop(w, h, T, rng):
    s = min(w, h) / 1080
    bw, bh = 300 * s, 212 * s
    pad = 60 * s
    art = Art(bw + 2 * pad, bh + 2 * pad)
    p = art.pen(1, pad, pad)
    p.rrect((0, 0, bw, bh), bh * 0.3)
    cov = p.cov()
    art.shadow(cov, 0, 12 * s, 18 * s, 0.4)
    art.vgrad(cov, RED_T, RED_B, pad, pad + bh)
    g = art.pen(1, pad, pad)
    g.rrect((10 * s, 8 * s, bw - 10 * s, bh * 0.5), bh * 0.26)
    art.gloss(g.cov() * cov, pad, pad + bh * 0.55, 0.25)
    tri = art.pen(bh / 100, pad + (bw - bh) / 2 + 6 * s, pad)
    icon_play(tri, cx=50, cy=50, r=24)
    tc = tri.cov()
    art.paint(shift(blur(tc, 3 * s), 0, 4 * s), (0, 0, 0), 0.2)
    art.paint(tc, WHITE)
    btn = art.sprite()
    shine_mask = cov
    cx, cy = w / 2, h / 2

    def frame(t):
        c = Canvas(w, h)
        u = t / T
        k = 1 + 0.045 * math.sin(TAU * u)
        for j in range(2):
            age = (t - j * T / 2) % T
            ripple(c, cx, cy, age, 300 * s, hexc("#ff3b3b"), 10 * s, 1.0)
        put(c, btn, cx, cy, scale=k)
        sh = seg(u, 0.1, 0.45)
        if 0 < sh < 1:
            yy, xx = np.mgrid[0:shine_mask.shape[0], 0:shine_mask.shape[1]].astype(np.float32)
            band = np.exp(-(((xx - yy * 0.5) - (-0.3 + 1.6 * sh) * shine_mask.shape[1]) / (22 * s)) ** 2)
            spr = band * shine_mask
            c.splat(spr.astype(np.float32), cx, cy, WHITE, 0.35 * math.sin(math.pi * sh))
        return c
    return frame


# ================================================================ notifications and stickers

def _skeleton(art, x, y, w_, h_, color, op):
    p = art.pen(1)
    p.rrect((x, y, x + w_, y + h_), h_ / 2)
    art.paint(p.cov(), color, op)


def _notification(dark):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        bw = (w - 2 * 60 * s) if h > w else 860 * s
        bh = 190 * s
        pad = 50 * s
        art = Art(bw + 2 * pad, bh + 2 * pad)
        p = art.pen(1, pad, pad)
        p.rrect((0, 0, bw, bh), 46 * s)
        cov = p.cov()
        art.shadow(cov, 0, 14 * s, 26 * s, 0.4)
        if dark:
            art.vgrad(cov, hexc("#2a2a31"), hexc("#1b1b20"), pad, pad + bh, opacity=0.96)
            fg, sub = hexc("#f2f2f5"), hexc("#8d8d99")
        else:
            art.vgrad(cov, hexc("#ffffff"), hexc("#f1f1f5"), pad, pad + bh, opacity=0.97)
            fg, sub = hexc("#2a2a30"), hexc("#b4b4bf")
        av = 112 * s
        ax, ay = pad + 38 * s, pad + (bh - av) / 2
        ap = art.pen(1)
        ap.rrect((ax, ay, ax + av, ay + av), 30 * s)
        ac = ap.cov()
        art.vgrad(ac, RED_T, RED_B, ay, ay + av)
        tp = art.pen(av / 100, ax, ay)
        icon_play(tp, cx=52, cy=50, r=22)
        art.paint(tp.cov(), WHITE)
        tx = ax + av + 34 * s
        thw = 220 * s
        tw = bw - (tx - pad) - thw - 60 * s
        _skeleton(art, tx, pad + 52 * s, tw * 0.92, 26 * s, fg, 0.9)
        _skeleton(art, tx, pad + 98 * s, tw * 0.62, 20 * s, sub, 0.9)
        _skeleton(art, tx + tw * 0.66, pad + 98 * s, tw * 0.18, 20 * s, sub, 0.6)
        thx = pad + bw - thw - 34 * s
        thh = thw * 9 / 16
        thy = pad + (bh - thh) / 2
        th = art.pen(1)
        th.rrect((thx, thy, thx + thw, thy + thh), 16 * s)
        thc = th.cov()
        art.lgrad(thc, hexc("#ff9a3d"), hexc("#7a3dff"), (thx, thy), (thx + thw, thy + thh))
        sun = art.pen(1)
        sun.circle(thx + thw * 0.72, thy + thh * 0.32, thh * 0.16)
        art.paint(sun.cov() * thc, hexc("#ffe08a"), 0.95)
        hill = art.pen(1)
        hill.poly([(thx, thy + thh), (thx + thw * 0.35, thy + thh * 0.45), (thx + thw * 0.6, thy + thh * 0.75),
                   (thx + thw * 0.8, thy + thh * 0.55), (thx + thw, thy + thh * 0.8), (thx + thw, thy + thh)])
        art.paint(hill.cov() * thc, hexc("#2b1a5e"), 0.8)
        pp = art.pen(thh * 0.5 / 100, thx + thw / 2 - thh * 0.25, thy + thh * 0.25)
        icon_play(pp, r=26)
        art.paint(pp.cov() * thc, WHITE, 0.9)
        card = art.sprite()
        bell = _icon_sprite(icon_bell, 64 * s, hexc("#ffb800"))
        dot = _red_dot(26 * s)
        cx = w / 2 if h > w else w - 60 * s - bw / 2
        cy = (190 * s if h > w else 170 * s) + bh / 2

        def frame(t):
            c = Canvas(w, h)
            u_in = back_out(seg(t, 0.0, 0.55), 1.3)
            u_out = ease_in(seg(t, T - 0.55, T - 0.1), 2.5)
            y = cy - (1 - u_in) * (cy + bh) - u_out * (cy + bh)
            put(c, card, cx, y)
            bx, by = cx - bw / 2 + 38 * s + av, y - bh / 2 + 22 * s
            rot = 26 * damped(t - 0.55, 3.0, 3.0)
            put(c, bell, bx, by, rot=rot, pivot=(bell.w / 2, bell.h * 0.12), scale=pop_scale(t, 0.35, None, 0.4))
            put(c, dot, bx + 26 * s, by - 6 * s, scale=pop_scale(t, 0.6, None, 0.35))
            return c
        return frame
    return make


yt("yt-notificacion", "Notificación de video nuevo", "New video notification", 4.0,
   tags=["notificacion", "notification", "aviso", "banner", "video nuevo", "campana"], sample="portrait-01.jpg",
   thumb_at=0.4)(_notification(False))
yt("yt-notificacion-oscura", "Notificación oscura", "Dark notification", 4.0,
   tags=["notificacion", "notification", "oscuro", "dark", "banner", "video nuevo"], sample="man-05.jpg",
   thumb_at=0.4)(_notification(True))


def _starburst(R, points=16, inner=0.84):
    pts = []
    for i in range(points * 2):
        r = R if i % 2 == 0 else R * inner
        a = i / (points * 2) * TAU - math.pi / 2
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def _new_video(line1, line2):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        R = 250 * s
        pad = 60 * s
        W = 2 * R + 2 * pad
        art = Art(W, W)
        p = art.pen(1, W / 2, W / 2)
        p.poly(_starburst(R))
        cov = p.cov()
        art.shadow(cov, 0, 14 * s, 18 * s, 0.4)
        art.paint(cov, WHITE)
        p2 = art.pen(1, W / 2, W / 2)
        p2.poly(_starburst(R * 0.93))
        c2 = p2.cov()
        art.rgrad(c2, W / 2 - R * 0.25, W / 2 - R * 0.35, R * 1.2,
                  [(0, hexc("#ff5148")), (0.7, hexc("#e8102a")), (1, hexc("#b8001c"))])
        ring = art.pen(1, W / 2, W / 2)
        ring.ring((-R * 0.68, -R * 0.68, R * 0.68, R * 0.68), 5 * s)
        art.paint(ring.cov(), WHITE, 0.35)
        size1 = 84 * s * min(1.0, 5.6 / max(len(line1), 1))
        size2 = 92 * s * min(1.0, 6.0 / max(len(line2), 1))
        tp = art.pen(1, W / 2, W / 2)
        tp.text((0, -R * 0.2), line1, BLACK, size1)
        tp.text((0, R * 0.2), line2, BLACK, size2)
        tc = tp.cov()
        art.paint(shift(tc, 0, 7 * s), hexc("#7a0010"), 0.9)
        art.vgrad(tc, hexc("#ffffff"), hexc("#ffe7a8"), W / 2 - R * 0.4, W / 2 + R * 0.4)
        gl = art.pen(1, W / 2, W / 2)
        gl.ellipse((-R * 0.8, -R * 0.95, R * 0.8, -R * 0.05))
        art.gloss(gl.cov() * c2, W / 2 - R, W / 2 - R * 0.1, 0.18)
        sticker = art.sprite()
        cx, cy = spot(w, h, 0.68, 0.62)
        if h <= w:
            cx = w * 0.74

        def frame(t):
            c = Canvas(w, h)
            k = pop_scale(t, 0.0, T - 0.4, 0.55, 0.32)
            rot = -16 * (1 - back_out(seg(t, 0.0, 0.6), 2.0)) + 5 * math.sin(TAU * t / 1.6)
            k *= 1 + 0.03 * math.sin(TAU * t / 0.8)
            burst_lines(c, cx, cy, t - 0.2, R * 1.05, R * 1.4, hexc("#ffd23f"), 12, 12 * s, 0.5)
            put(c, sticker, cx, cy, scale=k, rot=rot)
            return c
        return frame
    return make


yt("yt-nuevo-video-es", "¡Nuevo video! (español)", "New video sticker (Spanish)", 3.5,
   tags=["nuevo video", "nuevo", "estreno", "sticker", "español"], sample="podcast-03.jpg", thumb_at=0.5)(
    _new_video("¡NUEVO", "VIDEO!"))
yt("yt-new-video-en", "New video (inglés)", "New video sticker (English)", 3.5,
   tags=["new video", "new", "premiere", "sticker", "english", "ingles"], sample="man-02.jpg", thumb_at=0.5)(
    _new_video("NEW", "VIDEO!"))


# ================================================================ arrows and highlights

def _block_arrow(L, Wd, head_l, head_w):
    """An arrow pointing right, tail at x = 0, tip at x = L (centred on y = 0)."""
    return [(0, -Wd / 2), (L - head_l, -Wd / 2), (L - head_l, -head_w / 2), (L, 0),
            (L - head_l, head_w / 2), (L - head_l, Wd / 2), (0, Wd / 2)]


def _arrow_sprite(L, Wd, top, bot, outline=WHITE, ol=12.0, depth=10.0, s=1.0):
    pad = 50 * s
    hl, hw = L * 0.38, Wd * 2.3
    art = Art(L + 2 * pad, hw + 2 * pad)
    p = art.pen(1, pad, pad + hw / 2)
    pts = _block_arrow(L, Wd, hl, hw)
    p.poly(pts)
    p.line(pts + [pts[0]], Wd * 0.18)
    cov = p.cov()
    o = grow(cov, ol * s)
    art.shadow(o, 0, 10 * s, 14 * s, 0.4)
    if outline is not None:
        art.paint(blur(o, 0.7), outline)
    art.paint(shift(cov, 0, depth * s), mix(bot, (0, 0, 0), 0.45))
    art.vgrad(cov, top, bot, pad, pad + hw)
    hi = art.pen(1, pad, pad + hw / 2)
    hi.line([(Wd * 0.3, -Wd * 0.22), (L - hl - Wd * 0.1, -Wd * 0.22)], Wd * 0.12)
    art.paint(hi.cov() * cov, WHITE, 0.35)
    return art.sprite(), pad


@yt("yt-flecha-roja", "Flecha roja que señala", "Red pointing arrow", 2.0, loop=True,
    tags=["flecha", "arrow", "roja", "red", "señalar", "mira aqui", "look", "miniatura"], sample="cake-01.jpg",
    thumb_at=0.25)
def _red_arrow(w, h, T, rng):
    s = min(w, h) / 1080
    L = 360 * s
    spr, pad = _arrow_sprite(L, 78 * s, hexc("#ff4a3d"), hexc("#d10018"), s=s)
    tip = (pad + L, spr.h / 2)
    tx, ty = w * 0.5, h * 0.5
    ang = 135.0      # pointing down-left at the target from the upper right
    th = math.radians(ang)
    ux, uy = math.cos(th), math.sin(th)

    def frame(t):
        c = Canvas(w, h)
        b = abs(math.sin(math.pi * 2 * t / T)) ** 0.8
        d = 30 * s + 60 * s * b
        sq = 1 + 0.06 * (1 - b)
        put(c, spr, tx - ux * d, ty - uy * d, rot=ang, pivot=tip, sx=sq, sy=1 / sq)
        return c
    return frame


@yt("yt-flechas-amarillas", "Flechas amarillas a los lados", "Yellow side arrows", 2.0, loop=True,
    tags=["flechas", "arrows", "amarillo", "yellow", "señalar", "centro", "mira", "atencion"], sample="food-02.jpg",
    thumb_at=0.25)
def _yellow_arrows(w, h, T, rng):
    s = min(w, h) / 1080
    L = 260 * s
    spr, pad = _arrow_sprite(L, 70 * s, hexc("#ffe14a"), hexc("#ffad00"), outline=hexc("#16161a"), ol=10, s=s)
    tip = (pad + L, spr.h / 2)
    cx, cy = w / 2, h / 2
    gapx = (190 if h > w else 380) * s

    def frame(t):
        c = Canvas(w, h)
        for side in (-1, 1):
            b = abs(math.sin(math.pi * 2 * t / T + (0 if side < 0 else 0.0))) ** 0.8
            d = gapx - 70 * s * b
            put(c, spr, cx + side * d, cy, rot=0 if side < 0 else 180, pivot=tip)
        return c
    return frame


@yt("yt-flecha-neon", "Flecha de neón", "Neon arrow", 3.0, loop=True,
    tags=["flecha", "arrow", "neon", "brillo", "gamer", "señalar", "noche"], sample="concert-02.jpg", thumb_at=0.4)
def _neon_arrow(w, h, T, rng):
    s = min(w, h) / 1080
    L, Wd = 380 * s, 70 * s
    hl, hw = L * 0.38, Wd * 2.3
    pad = 90 * s
    art = Art(L + 2 * pad, hw + 2 * pad)
    p = art.pen(1, pad, pad + hw / 2)
    pts = _block_arrow(L, Wd, hl, hw)
    p.line(pts + [pts[0], pts[1]], 11 * s)
    cov = p.cov()
    col = hexc("#2bfff0")
    art.glow(cov, 26 * s, col, 0.9, 2.4)
    art.glow(cov, 8 * s, col, 1.0, 1.8)
    art.paint(cov, mix(col, WHITE, 0.7))
    spr = art.sprite()
    tip = (pad + L, spr.h / 2)
    tx, ty = w * 0.5, h * 0.52
    ang = 160.0
    th = math.radians(ang)
    ux, uy = math.cos(th), math.sin(th)
    frames = int(T * 30)
    r = np.random.default_rng(3)
    flick = [1.0 if r.random() > 0.08 else 0.35 for _ in range(frames)]

    def frame(t):
        c = Canvas(w, h)
        b = 0.5 - 0.5 * math.cos(TAU * 2 * t / T)
        d = 40 * s + 50 * s * b
        k = flick[int(round(t * 30)) % frames] * (0.85 + 0.15 * math.sin(TAU * 3 * t / T))
        put(c, spr, tx - ux * d, ty - uy * d, rot=ang, pivot=tip, opacity=k, add=True)
        return c
    return frame


def _marker_path(cx, cy, rx, ry, turns=1.12, n=160, jitter=0.0, rng=None, start=-2.2):
    pts = []
    for i in range(n + 1):
        u = i / n
        a = start + TAU * turns * u
        k = 1 + 0.06 * u + (jitter * math.sin(a * 3 + 1.3) if jitter else 0)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


@yt("yt-circulo-flecha", "Círculo y flecha rojos", "Red circle and arrow", 3.0,
    tags=["circulo", "flecha", "rojo", "marcar", "señalar", "miniatura", "thumbnail", "mira esto"],
    sample="pet-03.jpg", thumb_at=0.85)
def _circle_arrow(w, h, T, rng):
    s = min(w, h) / 1080
    cx, cy = w / 2, h * 0.47
    rx, ry = 270 * s, 200 * s
    circ = _marker_path(cx, cy, rx, ry, jitter=0.02)
    a0 = (cx + rx * 1.45, cy + ry * 2.0)
    a1 = (cx + rx * 0.82, cy + ry * 1.02)
    shaft = bezier(a0, (cx + rx * 1.6, cy + ry * 1.25), a1, 40)
    ang = math.atan2(a1[1] - shaft[-4][1], a1[0] - shaft[-4][0])
    head = [(a1[0] + 70 * s * math.cos(ang + math.pi + d), a1[1] + 70 * s * math.sin(ang + math.pi + d))
            for d in (-0.55, 0.55)]
    red = hexc("#ff1f2d")
    wd = 22 * s

    def frame(t):
        c = Canvas(w, h)
        u1 = ease_io(seg(t, 0.05, 0.85))
        u2 = ease_io(seg(t, 0.8, 1.25))
        u3 = ease_out(seg(t, 1.2, 1.4))
        fade = 1 - seg(t, T - 0.35, T - 0.05)
        covs = []
        for width in (wd + 14 * s, wd):
            p = Pen(w, h, ss=2)
            if u1 > 0:
                p.line(partial(circ, u1), width)
            if u2 > 0:
                p.line(partial(shaft, u2), width)
            if u3 > 0:
                for hp in head:
                    p.line([a1, (lerp(a1[0], hp[0], u3), lerp(a1[1], hp[1], u3))], width)
            covs.append(p.cov())
        out, cov = covs
        c.fill((0, 0, 0), shift(blur(out, 6 * s), 0, 6 * s) * 0.35 * fade)
        c.fill(WHITE, out * fade)
        c.fill(red, cov * fade)
        return c
    return frame


@yt("yt-resaltador", "Resaltador amarillo", "Yellow highlighter", 2.5,
    tags=["resaltador", "highlighter", "subrayar", "marcar", "texto", "amarillo", "destacar"],
    sample="study-02.jpg", thumb_at=0.7)
def _highlighter(w, h, T, rng):
    s = min(w, h) / 1080
    cx, cy = spot(w, h, 0.7, 0.72)
    L = (w * 0.78) if h > w else w * 0.5
    Hh = 110 * s
    tex = fx.tile_noise(256, 11, falloff=1.2)
    x0 = cx - L / 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    grain = fx.sample_tile(tex, w, h, 0, 0, 0.6)
    edge = fx.sample_tile(fx.tile_noise(256, 12, falloff=1.6), w, 1, 0, 0, 0.2)[0]

    def frame(t):
        c = Canvas(w, h)
        u = ease_io(seg(t, 0.05, 0.75))
        fade = 1 - seg(t, T - 0.35, T - 0.05)
        if u <= 0:
            return c
        xe = x0 + L * u
        top = cy - Hh / 2 + (edge - 0.5) * 10 * s - (xx[0] - x0) * 0.02
        bot = cy + Hh / 2 + (edge[::-1] - 0.5) * 10 * s - (xx[0] - x0) * 0.02
        a = np.clip(yy - top[None, :] + 0.5, 0, 1) * np.clip(bot[None, :] - yy + 0.5, 0, 1)
        a *= np.clip(xe - xx + 0.5, 0, 1) * np.clip(xx - x0 + 0.5, 0, 1)
        a *= 0.5 + 0.12 * grain
        c.fill(hexc("#ffe83a"), a * fade)
        return c
    return frame


@yt("yt-circulo-neon", "Círculo de neón", "Neon circle", 3.0,
    tags=["circulo", "neon", "marcar", "resaltar", "highlight", "mira esto", "gamer"], sample="concert-04.jpg",
    thumb_at=0.7)
def _neon_circle(w, h, T, rng):
    s = min(w, h) / 1080
    cx, cy = w / 2, h * 0.47
    R = 280 * s
    col = hexc("#ff3df2")
    path = _marker_path(cx, cy, R, R, turns=1.0, n=200, start=-math.pi / 2)

    def frame(t):
        c = Canvas(w, h)
        u = ease_io(seg(t, 0.05, 0.8))
        fade = 1 - seg(t, T - 0.35, T - 0.05)
        pulse = 0.85 + 0.15 * math.sin(TAU * 2 * t)
        p = Pen(w, h, ss=2)
        if u > 0:
            p.line(partial(path, u), 10 * s)
        cov = p.cov()
        g1 = blur(cov, 26 * s)
        g2 = blur(cov, 8 * s)
        c.fill(col, np.clip(g1 * 2.4, 0, 1) * 0.85 * pulse * fade)
        c.fill(col, np.clip(g2 * 1.8, 0, 1) * fade)
        c.fill(mix(col, WHITE, 0.75), cov * fade)
        if 0 < u < 1:
            hx, hy = partial(path, u)[-1]
            c.splat(fx.glow(int(50 * s)), hx, hy, WHITE, 0.9 * fade, add=True)
        return c
    return frame


def _mark_badge(kind):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        size = 300 * s
        if kind == "check":
            disc = badge(lambda p: None, size, hexc("#4be38a"), hexc("#11a050"))
            pts = [(22, 52), (42, 72), (80, 30)]
        else:
            disc = badge(lambda p: None, size, hexc("#ff5a5a"), hexc("#d6001c"))
            pts = None
        cx, cy = spot(w, h, 0.66, 0.6)
        u_ = size * 0.56 / 100

        def frame(t):
            c = Canvas(w, h)
            k = pop_scale(t, 0.0, T - 0.4, 0.5, 0.3)
            shake = 0.0 if kind == "check" else 16 * damped(t - 0.75, 4.0, 4.0)
            burst_lines(c, cx, cy, t - 0.65, size * 0.62, size * 0.95, WHITE, 10, 12 * s, 0.45)
            put(c, disc, cx, cy, scale=k, rot=shake)
            box = int(size * 0.9)
            p = Pen(box, box, u=u_ * k, ox=box / 2 - 50 * u_ * k, oy=box / 2 - 50 * u_ * k)
            if kind == "check":
                v = ease_out(seg(t, 0.3, 0.7))
                if v > 0:
                    p.line(partial(pts, v), 14)
            else:
                v1, v2 = ease_out(seg(t, 0.3, 0.5)), ease_out(seg(t, 0.5, 0.7))
                if v1 > 0:
                    p.line(partial([(28, 28), (72, 72)], v1), 14)
                if v2 > 0:
                    p.line(partial([(72, 28), (28, 72)], v2), 14)
            cov = p.cov()
            if shake:
                from PIL import Image as _I
                cov = np.asarray(_I.fromarray((cov * 255).astype(np.uint8)).rotate(-shake, _I.BICUBIC),
                                 np.float32) / 255
            c.splat(shift(cov, 0, 4 * s), cx, cy, (0, 0, 0), 0.2)
            c.splat(cov, cx, cy, WHITE, 1.0)
            return c
        return frame
    return make


yt("yt-check-verde", "Visto bueno verde", "Green check mark", 2.2,
   tags=["check", "visto bueno", "correcto", "si", "ok", "aprobado", "verde"], sample="office-03.jpg",
   thumb_at=0.6)(_mark_badge("check"))
yt("yt-x-roja", "Equis roja", "Red cross mark", 2.2,
   tags=["x", "equis", "incorrecto", "no", "error", "mal", "rojo"], sample="man-03.jpg", thumb_at=0.6)(
    _mark_badge("cross"))


# ================================================================ 3-D emoji reactions

FACE_STOPS = [(0, hexc("#fff38a")), (0.5, hexc("#ffd23a")), (0.82, hexc("#ffb11a")), (1.0, hexc("#f58a00"))]
BROWN_T, BROWN_B = hexc("#7a4210"), hexc("#4a2205")


class Face:
    """A shaded emoji face on its own Art; features are drawn in a 100-unit box over the face."""

    def __init__(self, D, pad=0.45, stops=FACE_STOPS, rim="#e06d00", shape=None):
        self.D, self.pad = D, D * pad
        W = D + 2 * self.pad
        self.art = Art(W, W)
        self.u = D / 100
        p = self.pen()
        if shape:
            shape(p)
        else:
            p.circle(50, 50, 50)
        self.cov = p.cov()
        a = self.art
        a.shadow(self.cov, 0, D * 0.035, D * 0.045, 0.35)
        a.rgrad(self.cov, self.X(42), self.Y(32), D * 0.74, stops)
        d = np.sqrt((a.xx - self.X(50)) ** 2 + (a.yy - self.Y(50)) ** 2) / (D / 2)
        a.paint(self.cov * fx.smooth(0.72, 1.02, d) * fx.smooth(0.25, 0.7, (a.yy - self.Y(0)) / D),
                hexc(rim), 0.45)

    def X(self, x):
        return self.pad + x * self.u

    def Y(self, y):
        return self.pad + y * self.u

    def pen(self):
        return self.art.pen(self.u, self.pad, self.pad)

    def feature(self, draw, top=BROWN_T, bot=BROWN_B, y0=0, y1=100, clip=True):
        p = self.pen()
        draw(p)
        cov = p.cov()
        if clip:
            cov = cov * self.cov
        self.art.vgrad(cov, top, bot, self.Y(y0), self.Y(y1))
        return cov

    def gloss(self, box=(20, 4, 80, 40), op=0.55):
        g = self.pen()
        g.ellipse(box)
        self.art.gloss(g.cov() * self.cov, self.Y(box[1]), self.Y(box[3]) + self.D * 0.02, op)

    def grin(self, top_y, bot_y, hw, curve=5.0, teeth=0.26, tongue=True):
        top = [(50 + x, top_y - curve * (x / hw) ** 2) for x in np.linspace(-hw, hw, 30)]
        bot = [(50 + hw * math.cos(a), top_y + (bot_y - top_y) * math.sin(a)) for a in np.linspace(0, math.pi, 40)]
        shape = top + bot

        def m(p):
            p.poly(shape)
        mouth = self.feature(m, hexc("#5a1a08"), hexc("#2a0902"), top_y, bot_y)
        H = bot_y - top_y
        if teeth:
            tp = self.pen()
            tp.rect((50 - hw - 2, top_y - curve - 2, 50 + hw + 2, top_y + teeth * H))
            self.art.vgrad(tp.cov() * mouth, WHITE, hexc("#e2e2ea"), self.Y(top_y), self.Y(top_y + teeth * H))
        if tongue:
            gp = self.pen()
            gp.ellipse((50 - hw * 0.55, bot_y - H * 0.42, 50 + hw * 0.55, bot_y + H * 0.2))
            self.art.vgrad(gp.cov() * mouth, hexc("#ff6b7a"), hexc("#d92a48"), self.Y(bot_y - H * 0.4), self.Y(bot_y))
        return mouth

    def sprite(self):
        return self.art.sprite()


def _drop_pts(x, y, r, rot=0.0):
    pts = []
    th = math.radians(rot)
    for t in np.linspace(0, TAU, 60):
        px = r * math.sin(t) * abs(math.sin(t / 2)) ** 0.9
        py = -r * math.cos(t) * 1.25
        pts.append((x + px * math.cos(th) - py * math.sin(th), y + px * math.sin(th) + py * math.cos(th)))
    return pts


def _paint_drop(f: Face, x, y, r, rot=0.0, clip=False):
    pts = _drop_pts(x, y, r, rot)
    p = f.pen()
    p.poly(pts)
    cov = p.cov()
    if clip:
        cov *= f.cov
    f.art.vgrad(cov, hexc("#b5ecff"), hexc("#2f86ff"), f.Y(y - r * 1.2), f.Y(y + r))
    hp = f.pen()
    hp.ellipse((x - r * 0.45, y - r * 0.05, x - r * 0.1, y + r * 0.5))
    f.art.paint(hp.cov() * cov, WHITE, 0.7)


def _arc_pts(cx, cy, rx, ry, a0, a1, n=30):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(a0, a1, n)]


def _heart_sprite(size, top="#ff5a78", bot="#d8002c"):
    art = Art(size * 1.3, size * 1.3)
    p = art.pen(size / 100, size * 0.15, size * 0.15)
    icon_heart(p)
    cov = p.cov()
    art.shadow(cov, 0, size * 0.03, size * 0.04, 0.3)
    art.vgrad(cov, hexc(top), hexc(bot), size * 0.15, size * 1.15)
    g = art.pen(size / 100, size * 0.15, size * 0.15)
    g.ellipse((14, 14, 46, 40))
    art.paint(blur(g.cov(), size * 0.03) * cov, WHITE, 0.55)
    return art.sprite()


def _emoji(build, idle, extras=None, per_frame=False, D=440):
    """Pop in with a twist, an idle loop of its own, pop out."""
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        size = D * s
        state = build(size, s)
        state["size"] = size
        cx, cy = spot(w, h, 0.62, 0.56)

        def frame(t):
            c = Canvas(w, h)
            k = pop_scale(t, 0.0, T - 0.38, 0.55, 0.32)
            rot = -24 * (1 - back_out(seg(t, 0.0, 0.6), 2.2))
            dx, dy, drot, dk = idle(t, s)
            x, y = cx + dx, cy + dy
            burst_lines(c, x, y, t - 0.15, size * 0.62, size * 0.85, hexc("#ffd23f"), 10, 11 * s, 0.45)
            spr = state["face"] if not per_frame else state["face"](t)
            put(c, spr, x, y, scale=k * dk, rot=rot + drot)
            if extras:
                extras(c, state, t, x, y, rot + drot, k * dk, s)
            return c
        return frame
    return make


def _laugh(size, s):
    f = Face(size)
    f.gloss()

    def eyes(p):
        for ex in (32, 68):
            p.line(_arc_pts(ex, 44, 11, 10, math.pi, TAU), 6.5)
    f.feature(eyes, y0=30, y1=46)
    f.grin(55, 88, 33, 7)
    _paint_drop(f, 12, 46, 12, -50)
    _paint_drop(f, 88, 46, 12, 50)
    return {"face": f.sprite()}


def _shock(size, s):
    f = Face(size)
    f.gloss()

    def brows(p):
        for ex in (33, 67):
            p.line(_arc_pts(ex, 24, 12, 7, math.pi + 0.3, TAU - 0.3), 4.5)
    f.feature(brows, y0=14, y1=24)
    ep = f.pen()
    for ex in (34, 66):
        ep.ellipse((ex - 10, 28, ex + 10, 56))
    ec = ep.cov()
    f.art.vgrad(ec, WHITE, hexc("#dfe3ea"), f.Y(28), f.Y(56))
    rp = f.pen()
    for ex in (34, 66):
        rp.ellipse((ex - 10, 28, ex + 10, 56))
        rp.ellipse((ex - 8.6, 29.4, ex + 8.6, 54.6), 0)
    f.art.paint(rp.cov(), BROWN_B, 0.9)

    def pupils(p):
        for ex in (34, 66):
            p.circle(ex, 43, 5.2)
    f.feature(pupils, hexc("#3a1d06"), hexc("#1a0a02"))
    hp = f.pen()
    for ex in (34, 66):
        hp.circle(ex - 1.8, 41, 1.6)
    f.art.paint(hp.cov(), WHITE, 0.9)

    def mouth(p):
        p.ellipse((39, 63, 61, 92))
    mc = f.feature(mouth, hexc("#5a1a08"), hexc("#2a0902"), 63, 92)
    tp = f.pen()
    tp.ellipse((42, 80, 58, 96))
    f.art.vgrad(tp.cov() * mc, hexc("#ff6b7a"), hexc("#d92a48"), f.Y(80), f.Y(92))
    return {"face": f.sprite()}


def _love(size, s):
    f = Face(size)
    f.gloss()
    f.grin(60, 86, 27, 6, teeth=0.3, tongue=False)
    return {"face": f.sprite(), "heart": _heart_sprite(size * 0.36), "mini": _heart_sprite(size * 0.16)}


def _love_extras(c, st, t, x, y, rot, k, s):
    size = st["size"]
    beat = 1 + 0.2 * max(0.0, math.sin(TAU * 1.6 * t)) ** 3
    for ex in (-0.17, 0.17):
        px, py = local(x, y, rot, k, ex * size, -0.07 * size)
        put(c, st["heart"], px, py, scale=k * beat * pop_scale(t, 0.25, None, 0.45), rot=rot + ex * 40)
    for i in range(4):
        age = (t - 0.5 - i * 0.45)
        if 0 < age < 1.6:
            u = age / 1.6
            hx = x + (0.45 if i % 2 else -0.45) * size + 20 * s * math.sin(age * 5 + i)
            hy = y - 0.3 * size - u * 260 * s
            put(c, st["mini"], hx, hy, scale=0.7 + 0.3 * math.sin(math.pi * u), opacity=math.sin(math.pi * u) * k,
                rot=(i - 1.5) * 12)


def _cry(size, s):
    f = Face(size)
    f.gloss()

    def eyes(p):
        p.line([(22, 43), (30, 47), (41, 45)], 5.5)
        p.line([(78, 43), (70, 47), (59, 45)], 5.5)
        p.line([(22, 30), (38, 24)], 4.5)
        p.line([(78, 30), (62, 24)], 4.5)
    f.feature(eyes, y0=22, y1=48)
    top = [(x, 64 + 2 * ((x - 50) / 18) ** 2) for x in np.linspace(32, 68, 20)]
    bot = [(50 + 19 * math.cos(a), 64 + 26 * math.sin(a)) for a in np.linspace(0, math.pi, 40)]

    def mouth(p):
        p.poly(top + bot)
    mc = f.feature(mouth, hexc("#5a1a08"), hexc("#2a0902"), 62, 90)
    tp = f.pen()
    tp.ellipse((38, 78, 62, 96))
    f.art.vgrad(tp.cov() * mc, hexc("#ff6b7a"), hexc("#d92a48"), f.Y(78), f.Y(92))
    sp = f.pen()
    for ex in (31, 69):
        pts = [(ex + (2 if ex < 50 else -2) * math.sin(v * 3), 47 + v * 58) for v in np.linspace(0, 1, 30)]
        sp.line(pts, 9)
    sc = sp.cov()
    f.art.lgrad(sc, hexc("#9fe2ff"), hexc("#3a8dff"), (0, f.Y(47)), (0, f.Y(105)))
    hp = f.pen()
    for ex in (29.5, 67.5):
        hp.line([(ex, 50), (ex, 100)], 2.2)
    f.art.paint(hp.cov() * sc, WHITE, 0.55)
    drop = Art(40 * s, 50 * s)
    dp = drop.pen(1, 20 * s, 26 * s)
    dp.poly(_drop_pts(0, 0, 12 * s))
    drop.vgrad(dp.cov(), hexc("#d4f4ff"), hexc("#4a9cff"))
    return {"face": f.sprite(), "drop": drop.sprite()}


def _cry_extras(c, st, t, x, y, rot, k, s):
    size = st["size"]
    for i in range(6):
        age = (t * 1.4 + i / 3) % 1.0
        ex = -0.19 if i % 2 == 0 else 0.19
        dx, dy = local(x, y, rot, k, ex * size, (-0.03 + age * 0.62) * size)
        put(c, st["drop"], dx, dy, scale=k * 0.8, opacity=math.sin(math.pi * age) * 0.9 * (t > 0.3))


def _skull_shape(p):
    p.circle(50, 42, 42)
    p.rrect((26, 56, 74, 96), 16)


def _skull(size, s):
    stops = [(0, hexc("#ffffff")), (0.55, hexc("#eef0f4")), (0.85, hexc("#c9cdd6")), (1.0, hexc("#9ea4b2"))]
    f = Face(size, stops=stops, rim="#8a90a0", shape=_skull_shape)
    f.gloss((22, 4, 78, 36), 0.6)

    def sockets(p):
        p.ellipse((22, 36, 46, 62))
        p.ellipse((54, 36, 78, 62))
        p.poly([(50, 60), (43.5, 74), (56.5, 74)])
        p.line([(43.5, 74), (56.5, 74)], 3)
    f.feature(sockets, hexc("#3b3b48"), hexc("#14141a"), 36, 74)

    def teeth(p):
        p.line([(33, 82), (67, 82)], 2.4)
        for tx in (40, 47, 54, 61):
            p.line([(tx, 78), (tx, 92)], 2.2)
    f.feature(teeth, hexc("#9aa0ae"), hexc("#7a8090"), 78, 92)
    return {"face": f.sprite()}


def _hundred(size, s):
    th = size * 0.55
    font = "Montserrat-ExtraBoldItalic.ttf"
    tw = text_width("100", font, th)
    W, H = tw + size * 0.6, size * 1.2
    art = Art(W, H)
    p = art.pen(1)
    p.text((W / 2, H * 0.42), "100", font, th)
    ul = [(W / 2 - tw * 0.48, H * 0.73), (W / 2 + tw * 0.5, H * 0.69)]
    ul2 = [(W / 2 - tw * 0.4, H * 0.86), (W / 2 + tw * 0.42, H * 0.82)]
    p.line(ul, size * 0.07)
    p.line(ul2, size * 0.07)
    cov = p.cov()
    ext = np.zeros_like(cov)
    for i in range(1, 9):
        ext = np.maximum(ext, shift(cov, i * 0.6 * s, i * 1.0 * s))
    out = grow(np.maximum(cov, ext), 7 * s)
    art.shadow(out, 0, 10 * s, 14 * s, 0.35)
    art.paint(blur(out, 0.8), WHITE)
    art.paint(ext, hexc("#7d0014"))
    art.vgrad(cov, hexc("#ff4a3a"), hexc("#d8001e"), H * 0.15, H * 0.9)
    hi = art.pen(1)
    hi.rect((0, 0, W, H * 0.36))
    art.paint(hi.cov() * cov, WHITE, 0.16)
    return {"face": art.sprite()}


def _flame_poly(cx, cy, R, H, t, ph, amp, n=48):
    left, right = [], []
    for i in range(n + 1):
        y = cy + R - (R + H) * i / n
        if y >= cy:
            hw = math.sqrt(max(R * R - (y - cy) ** 2, 0))
            v = 0.0
        else:
            v = min((cy - y) / H, 1.0)
            hw = R * (1 - v) ** 1.35 * (1 + 0.22 * math.sin(math.pi * v))
        hw *= 1 + 0.07 * math.sin(TAU * 3.1 * t + 9 * v + ph)
        xo = amp * v ** 1.5 * math.sin(TAU * 2.3 * t + 3.5 * v + ph) + amp * 0.3 * v * math.sin(TAU * 4.7 * t + ph)
        left.append((cx + xo - hw, y))
        right.append((cx + xo + hw, y))
    return left + right[::-1]


def _fire(size, s):
    W, H = size * 1.3, size * 1.5

    def face(t):
        art = Art(W, H)
        cx, cy = W / 2, H * 0.68
        R = size * 0.36
        layers = [
            (1.0, 1.55, "#ff3a1c", "#ff8a00"),
            (0.72, 1.15, "#ff9200", "#ffcc1a"),
            (0.44, 0.75, "#ffe46a", "#fff8d6"),
        ]
        for k, (rk, hk, top, bot) in enumerate(layers):
            p = art.pen(1)
            r = R * rk
            ccy = cy + R * (1 - rk) * 0.9
            p.poly(_flame_poly(cx, ccy, r, R * hk * 1.6, t, k * 1.7, R * 0.22))
            if k == 0:
                for side, ph in ((-1, 2.1), (1, 4.2)):
                    p.poly(_flame_poly(cx + side * R * 0.62, ccy + R * 0.18, r * 0.42, R * 1.15, t, ph, R * 0.18))
            cov = p.cov()
            if k == 0:
                art.shadow(cov, 0, size * 0.03, size * 0.04, 0.3)
                art.glow(cov, size * 0.06, hexc("#ff6a00"), 0.35, 1.2)
            art.vgrad(cov, hexc(top), hexc(bot), cy - R * hk * 1.6, cy + R)
        return art.sprite()
    return {"face": face}


def _fire_extras(c, st, t, x, y, rot, k, s):
    for i in range(7):
        age = (t * 0.9 + i / 7) % 1.0
        px = x + (i - 3) * 22 * s + 16 * s * math.sin(age * 9 + i)
        py = y - 120 * s - age * 300 * s
        c.splat(fx.glow(int(12 * s)), px, py, hexc("#ffb02e"), math.sin(math.pi * age) * k * 0.9, add=True)
        c.splat(fx.disc(max(int(3 * s), 1)), px, py, hexc("#fff2b0"), math.sin(math.pi * age) * k)


def _idle_laugh(t, s):
    return 0.0, -abs(math.sin(TAU * 1.6 * t)) * 18 * s, 9 * math.sin(TAU * 3.2 * t) * seg(t, 0.3, 0.6), 1.0


def _idle_shock(t, s):
    j = 1 + 0.14 * math.sin(math.pi * seg(t, 0.55, 0.85))
    return 5 * s * math.sin(TAU * 17 * t) * seg(t, 0.6, 0.9), -30 * s * math.sin(math.pi * seg(t, 0.55, 0.85)), 0.0, j


def _idle_sway(t, s):
    return 0.0, 8 * s * math.sin(TAU * 0.9 * t), 6 * math.sin(TAU * 1.1 * t), 1.0


def _idle_sob(t, s):
    return 0.0, 6 * s * abs(math.sin(TAU * 2.2 * t)), 3 * math.sin(TAU * 1.1 * t), 1 + 0.02 * math.sin(TAU * 4.4 * t)


def _idle_wobble(t, s):
    return 0.0, 0.0, 12 * damped(t - 0.35, 1.8, 2.2), 1.0


def _idle_skull(t, s):
    return 0.0, -abs(math.sin(TAU * 1.4 * t)) * 16 * s, 10 * math.sin(TAU * 1.4 * t), 1.0


EMO = ["emoji", "reaccion", "reaction", "3d"]
yt("yt-emoji-risa", "Emoji muerto de risa 3D", "3D tears of joy emoji", 3.0,
   tags=EMO + ["risa", "jaja", "lol", "gracioso", "funny", "laugh"], sample="friends-04.jpg", thumb_at=0.45)(
    _emoji(_laugh, _idle_laugh))
yt("yt-emoji-sorpresa", "Emoji sorprendido 3D", "3D shocked emoji", 3.0,
   tags=EMO + ["sorpresa", "wow", "shock", "asombro", "omg", "surprised"], sample="man-03.jpg", thumb_at=0.45)(
    _emoji(_shock, _idle_shock))
yt("yt-emoji-enamorado", "Emoji enamorado 3D", "3D heart eyes emoji", 3.0,
   tags=EMO + ["enamorado", "amor", "love", "corazones", "me encanta", "heart eyes"], sample="food-01.jpg",
   thumb_at=0.5)(_emoji(_love, _idle_sway, _love_extras))
yt("yt-emoji-llorando", "Emoji llorando 3D", "3D crying emoji", 3.0,
   tags=EMO + ["llorar", "triste", "sad", "crying", "lagrimas", "drama"], sample="pet-02.jpg", thumb_at=0.5)(
    _emoji(_cry, _idle_sob, _cry_extras))
yt("yt-emoji-calavera", "Emoji calavera 3D", "3D skull emoji", 3.0,
   tags=EMO + ["calavera", "skull", "muerto de risa", "dead", "jaja", "gracioso"], sample="friends-02.jpg",
   thumb_at=0.5)(_emoji(_skull, _idle_skull))
yt("yt-emoji-fuego", "Emoji de fuego 3D", "3D fire emoji", 3.0,
   tags=EMO + ["fuego", "fire", "hot", "lit", "increible", "tendencia"], sample="food-03.jpg", thumb_at=0.5)(
    _emoji(_fire, _idle_sway, _fire_extras, per_frame=True))
yt("yt-emoji-100", "Emoji 100 3D", "3D 100 emoji", 3.0,
   tags=EMO + ["100", "cien", "perfecto", "perfect", "exito", "top"], sample="gym-02.jpg", thumb_at=0.5)(
    _emoji(_hundred, _idle_wobble))


# ================================================================ counters, goal, player

def _group(n):
    return f"{n:,}".replace(",", " ")


def _bubble(width, height, top, bot, s):
    """A pill with a little tail under it. Returns (sprite, padding, tail length)."""
    pad = 40 * s
    tail = 26 * s
    art = Art(width + 2 * pad, height + tail + 2 * pad)
    p = art.pen(1, pad, pad)
    p.rrect((0, 0, width, height), height / 2)
    p.poly([(width / 2 - tail, height - 2), (width / 2, height + tail), (width / 2 + tail, height - 2)])
    cov = p.cov()
    art.shadow(cov, 0, 10 * s, 16 * s, 0.4)
    art.vgrad(cov, top, bot, pad, pad + height)
    g = art.pen(1, pad, pad)
    g.rrect((height * 0.12, height * 0.06, width - height * 0.12, height * 0.5), height * 0.4)
    art.gloss(g.cov() * cov, pad, pad + height * 0.55, 0.2)
    return art.sprite(), pad, tail


def _number_sprite(text, size, font=BLACK):
    tw = text_width(text, font, size)
    art = Art(tw + size * 0.5, size * 1.6)
    p = art.pen(1)
    p.text((art.w / 2, art.h / 2), text, font, size)
    cov = p.cov()
    art.paint(shift(blur(cov, size * 0.04), 0, size * 0.05), (0, 0, 0), 0.25)
    art.paint(cov, WHITE)
    return art.sprite()


def _counter(icon_fn, top, bot, end, floater=None):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        bh = 150 * s
        ns = 84 * s
        maxw = text_width(_group(end), BLACK, ns)
        ic = bh * 0.6
        lead = bh * 0.3
        bw = lead + ic + 28 * s + maxw + bh * 0.42
        bub, pad, tail = _bubble(bw, bh, hexc(top), hexc(bot), s)
        icon = _icon_sprite(icon_fn, ic)
        flo = None if floater is False else _icon_sprite(floater or icon_fn, 70 * s, hexc(top))
        cx, cy = spot(w, h, 0.66, 0.62)
        t_end = 2.6
        cache = {}
        tip = (bub.w / 2, pad + bh + tail)        # the tail tip stays put while the bubble pops

        def num(n):
            key = _group(n)
            if key not in cache:
                cache[key] = _number_sprite(key, ns)
            return cache[key]

        def frame(t):
            c = Canvas(w, h)
            k = pop_scale(t, 0.0, T - 0.4, 0.5, 0.3)
            k *= 1 + 0.08 * math.sin(math.pi * seg(t, t_end, t_end + 0.3))
            n = int(round(end * ease_out(seg(t, 0.45, t_end), 3)))
            ty = cy + bh / 2 + tail
            put(c, bub, cx, ty, scale=k, pivot=tip)
            pill_y = ty - (bh / 2 + tail) * k
            left = cx - bw / 2 * k
            ib = 1 + 0.15 * math.sin(math.pi * seg(t, t_end, t_end + 0.3))
            put(c, icon, left + (lead + ic / 2) * k, pill_y, scale=k * ib)
            spr = num(n)
            nx = left + (lead + ic + 28 * s) * k + (spr.w / 2 - ns * 0.25) * k
            put(c, spr, nx, pill_y, scale=k)
            confetti_pop(c, cx, pill_y, t - t_end, 5, 18, 650 * s, size=15 * s)
            if flo is not None:
                for i in range(6):
                    age = t - 0.5 - i * 0.32
                    if 0 < age < 1.3:
                        u = age / 1.3
                        fxp = cx + (i % 3 - 1) * 90 * s + 24 * s * math.sin(age * 6 + i)
                        fyp = pill_y - bh * 0.5 - u * 300 * s
                        put(c, flo, fxp, fyp, scale=0.6 + 0.4 * math.sin(math.pi * u),
                            opacity=math.sin(math.pi * u) * k)
            return c
        return frame
    return make


yt("yt-contador-seguidores", "Contador de seguidores", "Follower counter", 4.0,
   tags=["contador", "seguidores", "followers", "suscriptores", "subscribers", "numero", "crecer"],
   sample="portrait-08.jpg", thumb_at=0.7)(
    _counter(icon_person, "#ff4d4d", "#d6001c", 10000, floater=icon_heart))
yt("yt-contador-likes", "Contador de me gusta", "Like counter", 4.0,
   tags=["contador", "likes", "me gusta", "numero", "viral", "pulgar"], sample="beach-04.jpg", thumb_at=0.7)(
    _counter(icon_thumb, "#5aa9ff", "#1d5fe3", 25000))
yt("yt-contador-vistas", "Contador de vistas", "View counter", 4.0,
   tags=["contador", "vistas", "views", "reproducciones", "numero", "viral", "ojo"], sample="travel-07.jpg",
   thumb_at=0.7)(_counter(icon_eye, "#45454f", "#1e1e24", 1000000, floater=False))


def put_layer(c: Canvas, sub: Canvas, x0, y0, opacity=1.0):
    """Composites a premultiplied sub-canvas at an integer offset."""
    x0, y0 = int(round(x0)), int(round(y0))
    X0, Y0 = max(x0, 0), max(y0, 0)
    X1, Y1 = min(x0 + sub.w, c.w), min(y0 + sub.h, c.h)
    if X0 >= X1 or Y0 >= Y1:
        return
    a = sub.a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * opacity
    rgb = sub.rgb[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * opacity
    c.rgb[Y0:Y1, X0:X1] = c.rgb[Y0:Y1, X0:X1] * (1 - a)[..., None] + rgb
    c.a[Y0:Y1, X0:X1] = c.a[Y0:Y1, X0:X1] * (1 - a) + a


@yt("yt-meta-suscriptores", "Barra de meta alcanzada", "Goal reached bar", 4.5,
    tags=["meta", "goal", "progreso", "progress", "barra", "suscriptores", "logro", "100%"], sample="man-06.jpg",
    thumb_at=0.78)
def _goal(w, h, T, rng):
    s = min(w, h) / 1080
    L = (w * 0.74) if h > w else w * 0.46
    bh = 64 * s
    cx, cy = spot(w, h, 0.72, 0.78)
    x0 = cx - L / 2
    pad = 40 * s
    art = Art(L + 2 * pad, bh + 2 * pad)
    p = art.pen(1, pad, pad)
    p.rrect((0, 0, L, bh), bh / 2)
    tc = p.cov()
    art.shadow(tc, 0, 8 * s, 14 * s, 0.4)
    art.paint(tc, hexc("#121216"), 0.72)
    o = art.pen(1, pad, pad)
    o.rrect_line((0, 0, L, bh), bh / 2, 2.5 * s)
    art.paint(o.cov(), WHITE, 0.25)
    track = art.sprite()
    av = badge(icon_person, 150 * s, hexc("#ff4d4d"), hexc("#d6001c"))
    check = badge(lambda q: icon_check(q, width=15), 130 * s, hexc("#4be38a"), hexc("#11a050"))
    Li, Bi = int(math.ceil(L)), int(math.ceil(bh))
    yy, xx = np.mgrid[0:Bi, 0:Li].astype(np.float32)
    inner = Pen(Li, Bi)
    inner.rrect((5 * s, 5 * s, L - 5 * s, bh - 5 * s), (bh - 10 * s) / 2)
    inner_c = inner.cov()
    base = np.stack([np.ones_like(xx), 0.3 - 0.16 * xx / L, 0.3 - 0.08 * xx / L], -1)
    cache = {}
    t_full = 3.0

    def frame(t):
        c = Canvas(w, h)
        u_in = ease_out(seg(t, 0.0, 0.4))
        o_ = 1 - ease_in(seg(t, T - 0.45, T - 0.1))
        op = u_in * o_
        put(c, track, cx, cy, opacity=op, sx=0.6 + 0.4 * u_in)
        prog = ease_io(seg(t, 0.5, t_full))
        fill_x = 5 * s + bh * 0.6 + (L - 10 * s - bh * 0.6) * prog
        m = inner_c * np.clip(fill_x - xx + 0.5, 0, 1)
        stripes = np.clip(np.sin((xx + yy - t * 160 * s) / (14 * s)) * 3, -1, 1) * 0.5 + 0.5
        col = base * (0.86 + 0.14 * stripes[..., None])
        flash = math.sin(math.pi * seg(t, t_full, t_full + 0.35))
        col = col * (1 - flash) + flash
        sub = Canvas(Li, Bi)
        sub.layer(col.astype(np.float32), m.astype(np.float32))
        put_layer(c, sub, x0, cy - bh / 2, op)
        pct = f"{int(round(prog * 100))}%"
        if pct not in cache:
            cache[pct] = _number_sprite(pct, 40 * s)
        put(c, cache[pct], cx, cy - bh * 1.15, opacity=op)
        put(c, av, x0, cy, scale=pop_scale(t, 0.1, T - 0.45, 0.5, 0.3))
        put(c, check, x0 + L, cy, scale=pop_scale(t, t_full + 0.05, T - 0.45, 0.5, 0.3))
        confetti_pop(c, x0 + L, cy, t - t_full - 0.05, 9, 22, 750 * s, size=16 * s)
        return c
    return frame


def _gear(p, cx, cy, r):
    pts = []
    for i in range(48):
        a = i / 48 * TAU
        tooth = 1.0 if (i // 3) % 2 == 0 else 0.78
        pts.append((cx + r * tooth * math.cos(a), cy + r * tooth * math.sin(a)))
    p.poly(pts)
    p.circle(cx, cy, r * 0.36, 0)


@yt("yt-barra-reproduccion", "Barra de reproducción", "Video player bar", 6.0,
    tags=["reproductor", "player", "barra", "progreso", "video", "controles", "pausa"], sample="travel-01.jpg",
    thumb_at=0.5)
def _player(w, h, T, rng):
    s = min(w, h) / 1080
    vert = h > w
    m = 48 * s
    bar_y = h - (300 if vert else 130) * s
    icons_y = bar_y + 70 * s
    shade = Canvas(w, h)
    yy = np.arange(h, dtype=np.float32)[:, None]
    top = bar_y - 240 * s
    grad = np.clip((yy - top) / (h - top), 0, 1) ** 1.3 * np.ones((1, w), np.float32)
    shade.fill((0, 0, 0), grad * 0.7)
    L = w - 2 * m
    ic = 58 * s
    art = Art(w, 120 * s)
    p = art.pen(1, 0, 60 * s)
    x = m + ic / 2
    p.rrect((x - ic * 0.32, -ic * 0.4, x - ic * 0.1, ic * 0.4), 3 * s)
    p.rrect((x + ic * 0.1, -ic * 0.4, x + ic * 0.32, ic * 0.4), 3 * s)
    x += ic * 1.6
    p.poly([(x - ic * 0.35, -ic * 0.38), (x + ic * 0.2, 0), (x - ic * 0.35, ic * 0.38)])
    p.rrect((x + ic * 0.22, -ic * 0.38, x + ic * 0.36, ic * 0.38), 2 * s)
    x += ic * 1.5
    p.poly([(x - ic * 0.4, -ic * 0.16), (x - ic * 0.2, -ic * 0.16), (x + ic * 0.05, -ic * 0.4),
            (x + ic * 0.05, ic * 0.4), (x - ic * 0.2, ic * 0.16), (x - ic * 0.4, ic * 0.16)])
    for r in (ic * 0.25, ic * 0.45):
        p.line(_arc_pts(x + ic * 0.1, 0, r, r, -0.8, 0.8, 16), 4.5 * s / 1)
    time_x = x + ic * 0.9
    xr = w - m - ic / 2
    for sx_, sy_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        cx_, cy_ = xr + sx_ * ic * 0.36, sy_ * ic * 0.32
        p.line([(cx_, cy_ - sy_ * ic * 0.2), (cx_, cy_), (cx_ - sx_ * ic * 0.24, cy_)], 5 * s)
    _gear(p, xr - ic * 1.5, 0, ic * 0.42)
    cov = p.cov()
    art.paint(shift(blur(cov, 2 * s), 0, 2 * s), (0, 0, 0), 0.3)
    art.paint(cov, WHITE)
    icons = art.sprite()
    kn = Art(60 * s, 60 * s)
    kp = kn.pen(1, 30 * s, 30 * s)
    kp.circle(0, 0, 16 * s)
    kn.shadow(kp.cov(), 0, 2 * s, 4 * s, 0.4)
    kn.paint(kp.cov(), hexc("#ff2a2a"))
    knob = kn.sprite()
    total = 225
    cache = {}
    bh = 8 * s

    def bar(x0, x1):
        q = Pen(w, 3 * bh)
        q.rrect((x0, bh, x1, 2 * bh), bh / 2)
        return q.cov()

    track = bar(m, m + L)

    def frame(t):
        c = Canvas(w, h)
        op = ease_out(seg(t, 0.0, 0.35)) * (1 - ease_in(seg(t, T - 0.4, T - 0.05)))
        c.merge(shade, op)
        sec = 12 + int(t)
        prog = (12 + t) / total
        y0 = bar_y - 1.5 * bh
        c.splat(track, w / 2, y0 + track.shape[0] / 2, WHITE, 0.3 * op)
        buf = bar(m, m + L * min(prog + 0.2, 1))
        c.splat(buf, w / 2, y0 + buf.shape[0] / 2, WHITE, 0.35 * op)
        pl = bar(m, m + L * prog)
        c.splat(pl, w / 2, y0 + pl.shape[0] / 2, hexc("#ff2a2a"), op)
        put(c, knob, m + L * prog, bar_y, scale=1 + 0.1 * math.sin(TAU * t), opacity=op)
        put(c, icons, w / 2, icons_y, opacity=op)
        label = f"{sec // 60}:{sec % 60:02d} / {total // 60}:{total % 60:02d}"
        if label not in cache:
            cache[label] = _number_sprite(label, 40 * s, "Montserrat-SemiBold.ttf")
        spr = cache[label]
        put(c, spr, time_x + spr.w / 2 - 20 * s, icons_y, opacity=op)
        return c
    return frame
