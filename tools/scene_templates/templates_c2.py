"""Social lower thirds (2026-10-17): an editable «@tuusuario» next to the network's mark, for Instagram, TikTok,
YouTube, X, Facebook, Twitch and Threads, plus «all my socials» versions. Category `lowerthird`, tag «redes»;
order 5400-5499; ids `redes-*`.

They go over the user's own video: no background and no photo slot (the composition is transparent). The
render copy alone puts a sample photo under them for the card and the preview. Each one animates in, holds
and animates out. The marks are drawn with the template's own shapes (simplified, to identify the user's own
account), never with logo files. Styles: minimal, glass, neon and bold sticker; vertical and horizontal.
Shapes scale about their group's centre (`group`); texts cannot scale with a box, so they use text animations.
"""

from __future__ import annotations

from kit import Box, centered, fill, glow, gradient, keys, no_stroke, shadow, stroke, tanim, text_style
from scene import Template
from templates_c1 import geo, group, hollow_ring

O = 5400
CAT = "lowerthird"
BASE_TAGS = ["redes", "redes sociales", "usuario", "sígueme", "tercio inferior", "social media", "handle"]


class Overlay(Template):
    """A template whose package holds only its own graphics; `under()` adds a picture to the render copy only."""

    def under(self, sample: str):
        track = self.track("video", "Muestra")
        clip = self._clip("image", 0, self.duration, x={"keyframes": [{"timeUs": 0, "value": 0.0}]},
                          y={"keyframes": [{"timeUs": 0, "value": 0.0}]},
                          width={"keyframes": [{"timeUs": 0, "value": float(self.w)}]},
                          height={"keyframes": [{"timeUs": 0, "value": float(self.h)}]})
        clip["_sample"] = sample
        clip["_render_only"] = True
        track.clips.append(clip)
        return track

    def document(self, *, render, **kw):
        if render:
            return super().document(render=render, **kw)
        saved = self.tracks
        self.tracks = [tr for tr in saved if not any(c.get("_render_only") for c in tr.clips)]
        try:
            return super().document(render=render, **kw)
        finally:
            self.tracks = saved


def _make(vertical: bool, id, es, en, order, tags, sample, duration=5.0, thumb_at=2.4):
    size = (1080, 1920) if vertical else (1920, 1080)
    t = Overlay(id, es, en, CAT, duration, order=O + order, tags=BASE_TAGS + tags + ["vertical" if vertical else "horizontal"],
                thumb_at=thumb_at, size=size, background="#000000")
    t.under(sample)
    return t


# --- marks ------------------------------------------------------------------------------------------

NET = {
    "instagram": dict(name="Instagram", colour="#E1306C", handle="@tuusuario"),
    "tiktok": dict(name="TikTok", colour="#25F4EE", handle="@tuusuario"),
    "youtube": dict(name="YouTube", colour="#FF0033", handle="@tucanal"),
    "x": dict(name="X", colour="#FFFFFF", handle="@tuusuario"),
    "facebook": dict(name="Facebook", colour="#1877F2", handle="@tupagina"),
    "twitch": dict(name="Twitch", colour="#9146FF", handle="tucanal"),
    "threads": dict(name="Threads", colour="#FFFFFF", handle="@tuusuario"),
}
WHITE = "#FFFFFF"


def _solid(colour):
    return [fill(colour), no_stroke()]


def draw_mark(t, network: str, cx, cy, s, t0, dur, motion=None, shadow_alpha=0.3, outline=None):
    """A network mark of side s centred at (cx, cy); every part moves with `motion` as one group. `outline`
    (colour) draws a ring around the tile, for marks on a background of their own colour."""

    def part(colour, ox, oy, w, h, kind="rectangle", radius=0.0, layers=None, rotation=None, **g):
        box = centered(cx + ox * s, cy + oy * s, w * s, h * s)
        mo = group(motion, ox * s, oy * s) if motion else None
        extra = {"rotation": keys([(0, rotation)])} if rotation is not None else {}
        clip = t.solid(t.track("shape", "Logo"), colour, t0, dur, box, mo, radius=radius * s, kind=kind,
                       layers=layers or _solid(colour), **extra)
        if g:
            geo(clip, **g)
        return clip

    def drop():
        return [shadow("#000000", 0, s * 0.05, s * 0.14, shadow_alpha)] if shadow_alpha else []

    def tile(layers, radius=0.26, kind="rounded-rectangle", w=1.0, h=1.0):
        ring = [stroke(max(2, s * 0.03), outline)] if outline else [no_stroke()]
        return part("#000000", 0, 0, w, h, kind, radius, layers=drop() + layers + ring)

    if network == "instagram":
        tile([gradient([(0, "#FEDA75"), (0.28, "#FA7E1E"), (0.55, "#D62976"), (0.8, "#962FBF"), (1, "#4F5BD5")],
                       angle=-45)])
        part(WHITE, 0, 0, 0.62, 0.62, "rounded-rectangle", 0.19, layers=hollow_ring(WHITE, 0.075 * s))
        part(WHITE, 0, 0, 0.3, 0.3, "ellipse", layers=hollow_ring(WHITE, 0.075 * s))
        part(WHITE, 0.165, -0.165, 0.08, 0.08, "ellipse")
    elif network == "tiktok":
        tile([fill("#000000")])
        for colour, d in (("#25F4EE", -0.025), ("#FE2C55", 0.025), (WHITE, 0.0)):
            part(colour, 0.075 + d, -0.06 + d, 0.1, 0.5)
            part(colour, -0.07 + d, 0.15 + d, 0.3, 0.3, "ellipse", layers=hollow_ring(colour, 0.09 * s))
            part(colour, 0.18 + d, -0.2 + d, 0.2, 0.1, "rounded-rectangle", 0.04, rotation=35)
    elif network == "youtube":
        part("#FF0033", 0, 0, 1.0, 0.7, "rounded-rectangle", 0.2,
             layers=drop() + [fill("#FF0033")] + ([stroke(max(2, s * 0.03), outline)] if outline else [no_stroke()]))
        part(WHITE, 0.03, 0, 0.3, 0.3, "triangle", rotation=90)
    elif network == "x":
        tile([fill("#000000")])
        part(WHITE, 0, 0, 0.14, 0.74, rotation=-36)
        part(WHITE, 0, 0, 0.05, 0.74, rotation=36)
        part("#000000", 0, 0, 0.05, 0.72, rotation=-36)
    elif network == "facebook":
        tile([fill("#1877F2")], kind="ellipse")
        # The "f": a stem that runs off the bottom of the circle, a cross bar and the curved top.
        # The top hook is the upper-left quarter of a ring; blue covers hide the rest of it.
        part(WHITE, 0.2, -0.12, 0.4, 0.4, "ellipse", layers=hollow_ring(WHITE, 0.15 * s))
        part("#1877F2", 0.43, -0.12, 0.14, 0.46)
        part("#1877F2", 0.255, -0.01, 0.21, 0.22)
        part(WHITE, 0.075, 0.175, 0.15, 0.59)
        part(WHITE, 0.13, 0.04, 0.46, 0.12)
    elif network == "twitch":
        tile([fill("#9146FF")])
        part(WHITE, 0.0, 0.03, 0.56, 0.6, "speech-bubble-rect", tailX=0.15, tailSize=0.25)
        part("#9146FF", -0.07, -0.08, 0.07, 0.2)
        part("#9146FF", 0.09, -0.08, 0.07, 0.2)
    elif network == "threads":
        tile([fill("#000000")])
        part(WHITE, 0, 0.02, 0.62, 0.62, "ellipse", layers=hollow_ring(WHITE, 0.09 * s))
        part(WHITE, 0.03, 0.02, 0.24, 0.26, "ellipse", layers=hollow_ring(WHITE, 0.08 * s))
        part("#000000", 0.25, 0.12, 0.2, 0.14)
        part(WHITE, 0.17, 0.0, 0.08, 0.3)


# --- motion ------------------------------------------------------------------------------------------

def pop_motion(dur: float, at: float = 0.0, length: float = 0.45, out: float = 0.35) -> list:
    pts = [(0, {"s": 0.0}, "back")] if at <= 0 else [(0, {"s": 0.0}, "hold"), (at, {"s": 0.0}, "back")]
    return pts + [(at + length, {}, "hold"), (dur - out, {}, "in"), (dur, {"s": 0.0})]


def slide_motion(dur: float, dx: float = 0, dy: float = 0, at: float = 0.0, length: float = 0.5,
                 out: float = 0.4, ease: str = "out") -> list:
    pts = [(0, {"dx": dx, "dy": dy}, ease)] if at <= 0 else [(0, {"dx": dx, "dy": dy}, "hold"),
                                                            (at, {"dx": dx, "dy": dy}, ease)]
    return pts + [(at + length, {}, "hold"), (dur - out, {}, "in"), (dur, {"dx": dx, "dy": dy})]


def wipe_motion(dur: float, w: float, at: float = 0.0, length: float = 0.5, out: float = 0.4) -> list:
    """A card that opens from its left edge and closes back into it."""
    closed = {"sx": 0.0, "dx": -w / 2}
    pts = [(0, closed, "out")] if at <= 0 else [(0, closed, "hold"), (at, closed, "out")]
    return pts + [(at + length, {}, "hold"), (dur - out, {}, "in"), (dur, closed)]


def fade_kf(dur: float, fin: float = 0.35, fout: float = 0.35, peak: float = 1.0) -> dict:
    return keys([(0, 0.0, "smooth"), (fin, peak, "hold"), (dur - fout, peak, "smooth"), (dur, 0.0)])


def text(t, track_name, content, t0, end, box, font, size, colour, *, layers=None, weight=700, align="left",
         anim_in=None, anim_out=None, name=None, editable=True, spacing=0.0, case="none", **extra):
    style = text_style(font, size, layers or [fill(colour)], weight=weight, align=align, spacing=spacing, case=case,
                       anim_in=anim_in, anim_out=anim_out)
    style["wordWrap"] = False
    return t.text(t.track("text", track_name), content, t0, end - t0, box, style, label=name or content,
                  editable=editable, **extra)


# --- the four styles -------------------------------------------------------------------------------------
# Each draws one network row: a mark at (x + m/2, cy) and the texts to its right, between t0 and end.

def row_minimal(t, net, x, cy, m, hs, t0, end, *, caption=True, font="Poppins", accent=None, delay=0.0):
    n = NET[net]
    d = end - t0
    draw_mark(t, net, x + m / 2, cy, m, t0 + delay, d - delay, pop_motion(d - delay), shadow_alpha=0.35)
    xt = x + m + m * 0.28
    soft = [shadow("#000000", 0, 3, 14, 0.6)]
    if caption:
        cs = round(hs * 0.52)
        text(t, "Texto", f"sígueme en {n['name']}", t0 + delay + 0.25, end, Box(xt, cy - m / 2 - cs * 0.1, 1100, cs * 1.3),
             "Poppins", cs, WHITE, layers=soft + [fill(WHITE, 0.85)], weight=500,
             anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.25), name="Texto")
        hy = cy - m / 2 + cs * 1.05
    else:
        hy = cy - hs * 0.7
    text(t, "Usuario", n["handle"], t0 + delay + 0.15, end, Box(xt, hy, 1200, hs * 1.4), font, hs, WHITE,
         layers=soft + [fill(WHITE)], weight=700, anim_in=tanim("rise", duration=0.45, distance=0.4),
         anim_out=tanim("fade", duration=0.25), name=f"Usuario de {n['name']}")
    bar_y = hy + hs * 1.32
    t.solid(t.track("shape", "Línea"), accent or n["colour"], t0 + delay + 0.3, d - delay - 0.3,
            Box(xt + 2, bar_y, hs * 3.2, max(4, hs * 0.07)), wipe_motion(d - delay - 0.3, hs * 3.2, length=0.5, out=0.3))


def row_glass(t, net, x, cy, m, hs, t0, end, *, w, caption=True, delay=0.0, tint="#0B0B14", text_colour=WHITE,
              dy_in=90):
    n = NET[net]
    d = end - t0 - delay
    pad = m * 0.24
    h = m + pad * 2
    card = Box(x, cy - h / 2, w, h)
    mo = slide_motion(d, dy=dy_in, length=0.55)
    t.solid(t.track("shape", "Cristal"), tint, t0 + delay, d, card, mo, radius=h * 0.3, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 14, 40, 0.28), fill(tint, 0.42), stroke(2, WHITE, 0.5)],
            opacity=fade_kf(d))
    # A soft highlight on the upper half: the glass catching light.
    t.solid(t.track("shape", "Brillo"), WHITE, t0 + delay, d, Box(x + 3, cy - h / 2 + 3, w - 6, h * 0.45),
            group(mo, 0, -h * 0.27), radius=h * 0.28, kind="rounded-rectangle",
            layers=[gradient([(0, WHITE, 0.18), (1, WHITE, 0.0)], angle=90), no_stroke()], opacity=fade_kf(d))
    draw_mark(t, net, x + pad + m / 2, cy, m, t0 + delay + 0.1, d - 0.1, group(pop_motion(d - 0.1, length=0.5),
                                                                             0, 0), shadow_alpha=0.2)
    xt = x + pad + m + pad * 0.9
    tw = w - (xt - x) - pad
    if caption:
        cs = round(hs * 0.52)
        text(t, "Texto", f"sígueme en {n['name']}", t0 + delay + 0.3, end, Box(xt, cy - m / 2 - cs * 0.05, tw, cs * 1.3),
             "Inter", cs, text_colour, layers=[fill(text_colour, 0.8)], weight=500,
             anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.25), name="Texto")
        hy = cy - m / 2 + cs * 1.1
    else:
        hy = cy - hs * 0.7
    text(t, "Usuario", n["handle"], t0 + delay + 0.25, end, Box(xt, hy, tw, hs * 1.4), "Inter", hs, text_colour,
         layers=[fill(text_colour)], weight=700, anim_in=tanim("rise", duration=0.45, distance=0.3),
         anim_out=tanim("fade", duration=0.25), name=f"Usuario de {n['name']}")


def row_neon(t, net, x, cy, m, hs, t0, end, *, w, caption=False, delay=0.0, font="Righteous"):
    n = NET[net]
    c = n["colour"] if net not in ("x", "threads") else "#B8B8FF"
    d = end - t0 - delay
    pad = m * 0.22
    h = m + pad * 2
    card = Box(x, cy - h / 2, w, h)
    t.solid(t.track("shape", "Neón"), c, t0 + delay, d, card, wipe_motion(d, w, length=0.55), radius=h / 2,
            kind="rounded-rectangle", layers=[fill("#07070D", 0.78), stroke(4, c)])
    t.solid(t.track("shape", "Halo"), c, t0 + delay, d, card, wipe_motion(d, w, length=0.55), radius=h / 2,
            kind="rounded-rectangle", layers=hollow_ring(c, 14, 0.25),
            opacity=keys([(0, 1.0), (0.7, 0.6, "smooth"), (1.0, 1.0, "smooth"), (1.4, 0.65, "smooth"), (1.8, 1.0)]))
    draw_mark(t, net, x + pad + m / 2, cy, m, t0 + delay + 0.3, d - 0.3, pop_motion(d - 0.3, length=0.4),
              shadow_alpha=0, outline=c if net in ("x", "threads", "tiktok") else None)
    xt = x + pad + m + pad
    tw = w - (xt - x) - pad
    lay = [glow(c, 18, 0.9), fill(WHITE)]
    if caption:
        cs = round(hs * 0.52)
        text(t, "Texto", f"sígueme en {n['name']}", t0 + delay + 0.45, end, Box(xt, cy - m / 2 - cs * 0.05, tw, cs * 1.3),
             font, cs, c, layers=[glow(c, 10, 0.6), fill(c)], weight=400, anim_in=tanim("flicker-in", duration=0.5),
             anim_out=tanim("fade", duration=0.25), name="Texto")
        hy = cy - m / 2 + cs * 1.1
    else:
        hy = cy - hs * 0.68
    text(t, "Usuario", n["handle"], t0 + delay + 0.4, end, Box(xt, hy, tw, hs * 1.4), font, hs, WHITE, layers=lay,
         weight=400, anim_in=tanim("flicker-in", duration=0.6), anim_out=tanim("fade", duration=0.25),
         name=f"Usuario de {n['name']}")


def row_sticker(t, net, x, cy, m, hs, t0, end, *, w, caption=False, delay=0.0, colour=WHITE, ink="#111111",
                tilt=-3.0, font="Lilita One"):
    n = NET[net]
    d = end - t0 - delay
    pad = m * 0.22
    h = m + pad * 2
    card = Box(x, cy - h / 2, w, h)
    ccx, ccy = card.cx, card.cy
    mo = pop_motion(d, length=0.5)
    rot = keys([(0, tilt)])
    t.solid(t.track("shape", "Sticker"), colour, t0 + delay, d, card, mo, radius=h * 0.32, kind="rounded-rectangle",
            layers=[shadow(ink, 9, 11, 0, 1.0), fill(colour), stroke(7, ink)], rotation=rot)
    mx = x + pad + m / 2
    draw_mark(t, net, mx, cy, m, t0 + delay + 0.1, d - 0.1, group(pop_motion(d - 0.1, length=0.5), mx - ccx, 0),
              shadow_alpha=0, outline=ink)
    xt = x + pad + m + pad * 0.9
    tw = w - (xt - x) - pad
    if caption:
        cs = round(hs * 0.52)
        text(t, "Texto", f"sígueme en {n['name']}", t0 + delay + 0.3, end, Box(xt, cy - m / 2 - cs * 0.05, tw, cs * 1.3),
             "Poppins", cs, ink, weight=700, anim_in=tanim("pop", duration=0.3), anim_out=tanim("shrink", duration=0.2),
             rotation=rot, name="Texto")
        hy = cy - m / 2 + cs * 1.05
    else:
        hy = cy - hs * 0.66
    text(t, "Usuario", n["handle"], t0 + delay + 0.25, end, Box(xt, hy, tw, hs * 1.4), font, hs, ink, weight=400,
         anim_in=tanim("pop", duration=0.35), anim_out=tanim("shrink", duration=0.2), rotation=rot,
         name=f"Usuario de {n['name']}")


# --- single-network lower thirds --------------------------------------------------------------------------

IN = 0.4


def _single(vertical, style, net, order, es_style, en_style, sample, extra_tags, **kw):
    n = NET[net]
    t = _make(vertical, f"redes-{'v' if vertical else 'h'}-{net}-{style}", f"{n['name']} {es_style}",
              f"{n['name']} {en_style} handle", order, [net, n["name"].lower(), es_style.lower()] + extra_tags, sample)
    end = t.duration - 0.4
    if vertical:
        x, cy, m, hs, w = 80, 1420, 130, 74, 820
    else:
        x, cy, m, hs, w = 110, 860, 124, 68, 800
    if style == "minimal":
        row_minimal(t, net, x, cy, m, hs, IN, end, **kw)
    elif style == "cristal":
        row_glass(t, net, x, cy, m, hs, IN, end, w=w, **kw)
    elif style == "neon":
        row_neon(t, net, x, cy, m, hs, IN, end, w=w - (60 if vertical else 40), **kw)
    else:
        row_sticker(t, net, x, cy, m, hs, IN, end, w=w - (40 if vertical else 30), **kw)
    return t


STYLES = {"minimal": ("minimal", "minimal", ["minimal", "limpio"]),
          "cristal": ("cristal", "glass", ["cristal", "transparente", "glass"]),
          "neon": ("neón", "neon", ["neón", "brillo", "gamer"]),
          "sticker": ("sticker", "sticker", ["sticker", "llamativo", "divertido"])}


def S(vertical, style, net, order, sample, **kw):
    es, en, tags = STYLES[style]

    def make():
        return _single(vertical, style, net, order, es, en, sample, tags, **kw)
    make.__name__ = f"redes_{'v' if vertical else 'h'}_{net}_{style}"
    make.__module__ = __name__
    return make


# --- all my socials -------------------------------------------------------------------------------------

ALL = ["instagram", "tiktok", "youtube", "x", "facebook"]


def todas_lista_cristal():
    """Vertical: five glass rows, one per network, that rise in turn."""
    t = _make(True, "redes-v-todas-cristal", "Todas mis redes en cristal", "All my socials, glass", 20,
              ["todas mis redes", "lista", "cristal", "instagram", "tiktok", "youtube"], "creator-02", duration=6.0,
              thumb_at=3.0)
    end = 5.6
    for i, net in enumerate(ALL):
        row_glass(t, net, 150, 1060 + i * 150, 96, 56, IN, end, w=780, caption=False, delay=i * 0.12, dy_in=60)
    text(t, "Título", "SÍGUEME EN REDES", IN, end, Box(150, 900, 780, 80), "Inter", 46, WHITE,
         layers=[shadow("#000000", 0, 3, 12, 0.6), fill(WHITE)], weight=800, spacing=8,
         anim_in=tanim("fade", duration=0.5), anim_out=tanim("fade", duration=0.3), name="Título")
    return t


def todas_lista_neon():
    """Horizontal: a column of neon pills on the left."""
    t = _make(False, "redes-h-todas-neon", "Todas mis redes neón", "All my socials, neon", 21,
              ["todas mis redes", "lista", "neón", "gamer", "twitch", "streaming"], "h-gaming-03", duration=6.0,
              thumb_at=3.0)
    end = 5.6
    for i, net in enumerate(["twitch", "youtube", "tiktok", "instagram", "x"]):
        row_neon(t, net, 90, 330 + i * 140, 90, 50, IN, end, w=600, delay=i * 0.12)
    return t


def todas_fila():
    """Horizontal: the marks in a row over one handle — the same name everywhere."""
    t = _make(False, "redes-h-todas-fila", "Búscame en todas", "Find me everywhere", 22,
              ["todas mis redes", "fila", "mismo usuario", "minimal"], "h-portrait-04", duration=6.0, thumb_at=3.0)
    end = 5.6
    nets = ["instagram", "tiktok", "youtube", "facebook", "x", "threads"]
    m, gap = 100, 22
    x0 = 150
    cy = 780
    d = end - IN
    panel = Box(110, 700, 800, 340)
    t.solid(t.track("shape", "Panel"), "#0B0B14", IN, d, panel, wipe_motion(d, panel.w, length=0.5), radius=40,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 14, 40, 0.3), fill("#0B0B14", 0.55), no_stroke()])
    for i, net in enumerate(nets):
        cx = x0 + m / 2 + i * (m + gap)
        draw_mark(t, net, cx, cy, m, IN + i * 0.08, end - IN - i * 0.08,
                  pop_motion(end - IN - i * 0.08, length=0.45), shadow_alpha=0.4, outline="#FFFFFF" if net in ("x", "threads", "tiktok") else None)
    soft = [shadow("#000000", 0, 3, 14, 0.6)]
    text(t, "Texto", "búscame como", IN + 0.5, end, Box(x0, 860, 700, 60), "Poppins", 42, WHITE,
         layers=soft + [fill(WHITE, 0.85)], weight=500, anim_in=tanim("fade", duration=0.4),
         anim_out=tanim("fade", duration=0.25), name="Texto")
    text(t, "Usuario", "@tuusuario", IN + 0.6, end, Box(x0, 905, 700, 110), "Poppins", 80, WHITE,
         layers=soft + [fill(WHITE)], weight=800, anim_in=tanim("rise", duration=0.45, distance=0.4),
         anim_out=tanim("fade", duration=0.25), name="Usuario")
    return t


def todas_sticker_v():
    """Vertical: a stack of stickers, each tilted its own way."""
    t = _make(True, "redes-v-todas-sticker", "Mis redes en stickers", "My socials as stickers", 23,
              ["todas mis redes", "sticker", "divertido", "colores"], "portrait-06", duration=6.0, thumb_at=3.0)
    end = 5.6
    colours = ["#FFE14D", "#7DF9FF", "#FF9ECF", "#B9FF66"]
    for i, net in enumerate(["instagram", "tiktok", "youtube", "facebook"]):
        row_sticker(t, net, 110 + (i % 2) * 70, 1080 + i * 175, 100, 58, IN, end, w=760, delay=i * 0.15,
                    colour=colours[i], tilt=-3 if i % 2 == 0 else 2.5)
    return t


def todas_iconos_v():
    """Vertical: a row of marks and one handle in a dark pill."""
    t = _make(True, "redes-v-todas-iconos", "Mismo usuario en todas", "Same handle everywhere", 24,
              ["todas mis redes", "iconos", "mismo usuario", "píldora"], "portrait-07", duration=6.0, thumb_at=3.0)
    end = 5.6
    d = end - IN
    pill = Box(110, 1440, 860, 150)
    t.solid(t.track("shape", "Píldora"), "#111111", IN + 0.3, d - 0.3, pill, wipe_motion(d - 0.3, pill.w, length=0.5),
            radius=75, kind="rounded-rectangle", layers=[shadow("#000000", 0, 12, 30, 0.4), fill("#111111", 0.88),
                                                         no_stroke()])
    nets = ["instagram", "tiktok", "youtube", "facebook", "x"]
    m, gap = 112, 34
    x0 = 540 - (len(nets) * m + (len(nets) - 1) * gap) / 2
    for i, net in enumerate(nets):
        draw_mark(t, net, x0 + m / 2 + i * (m + gap), 1320, m, IN + i * 0.08, d - i * 0.08,
                  pop_motion(d - i * 0.08, length=0.45), shadow_alpha=0.4,
                  outline="#FFFFFF" if net in ("x", "tiktok") else None)
    text(t, "Usuario", "@tuusuario", IN + 0.6, end, Box(110, 1440, 860, 150), "Poppins", 76, WHITE, weight=800,
         align="center", anim_in=tanim("typewriter", duration=0.6, unit="character"),
         anim_out=tanim("fade", duration=0.25), name="Usuario")
    return t


TEMPLATES = [
    # Horizontal 16:9
    S(False, "minimal", "instagram", 0, "h-portrait-03"),
    S(False, "neon", "tiktok", 1, "h-gaming-02", caption=True),
    S(False, "sticker", "youtube", 2, "h-man-05", caption=True),
    S(False, "cristal", "x", 3, "h-portrait-01"),
    S(False, "cristal", "facebook", 4, "h-man-01"),
    S(False, "neon", "twitch", 5, "h-gaming-05", caption=True),
    S(False, "minimal", "threads", 6, "h-portrait-02"),
    S(False, "sticker", "instagram", 7, "h-portrait-06", caption=True),
    S(False, "minimal", "youtube", 8, "h-podcast-02"),
    S(False, "sticker", "tiktok", 9, "h-man-03", colour="#7DF9FF"),
    # Vertical 9:16
    S(True, "cristal", "instagram", 10, "creator-03"),
    S(True, "sticker", "tiktok", 11, "selfie-02", caption=True),
    S(True, "minimal", "youtube", 12, "creator-04"),
    S(True, "sticker", "x", 13, "portrait-02", caption=True, colour="#FFE14D"),
    S(True, "minimal", "facebook", 14, "selfie-04"),
    S(True, "neon", "twitch", 15, "portrait-04", caption=True),
    S(True, "cristal", "threads", 16, "selfie-03"),
    S(True, "neon", "instagram", 17, "portrait-08", caption=True),
    S(True, "minimal", "tiktok", 18, "creator-02"),
    todas_lista_cristal, todas_lista_neon, todas_fila, todas_sticker_v, todas_iconos_v,
]
