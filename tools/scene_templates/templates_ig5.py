"""INSTAGRAM folder video as Stock templates (ig5-*). See docs/plan-instagram.md.

2656838.mp4 (1920×1080 at 29.97 fps), source seconds 70–140: the «150+ Instagram» pack shows its stories three side
by side on light grey, each 486×864 px at x = 117 / 717 / 1317, y = 108; laid out here ×2.2222 on 1080×1920. Every
story copies the reference's layout and moves, studied on 10 fps sheets (sheet index i = reference frame 3·i after
the cut of its trio); photos are slots with our samples, brand words are neutral. Kit de Instagram; ids `ig5-*`,
order 15600-. Study notes in tienda/plantillas/estudio-2656838/NOTAS-ig5.md.

Coordinates below are in the reference's story pixels (486×864); the helpers scale them. Each story plays its
entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, label, tall
from llt_motion import frames_of
from scene import effect, gradient, keys, no_stroke, us
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, poly, ring
from templates_yp4 import art_except

W, H = 1080, 1920
R = W / 486.0
WHITE, BLACK = "#FFFFFF", "#000000"
M, PO, OU, OS, BE, AN = "Montserrat", "Poppins", "Outfit", "Oswald", "Bebas Neue", "Anton"

_FAM = {
    M: ("fonts.basic/fonts/montserrat/Montserrat-", {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold",
                                                     800: "ExtraBold", 900: "Black", 801: "ExtraBoldItalic",
                                                     701: "BoldItalic"}),
    PO: ("fonts.basic/fonts/poppins/Poppins-", {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold",
                                                800: "ExtraBold", 900: "Black"}),
    OU: ("fonts.extra/fonts/outfit/Outfit-", {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold",
                                              800: "ExtraBold", 900: "Black"}),
}
for _fam, (_pre, _ws) in _FAM.items():
    for _w, _n in _ws.items():
        f6._FILES[(_fam, _w)] = f"{_pre}{_n}.ttf"


def font(family, weight, path):
    """Registers one more font file for measuring (path under the add-ons stage)."""
    f6._FILES[(family, weight)] = path


font(OS, 400, "fonts.basic/fonts/oswald/Oswald-Regular.ttf")
font(OS, 500, "fonts.basic/fonts/oswald/Oswald-Medium.ttf")
font(OS, 600, "fonts.basic/fonts/oswald/Oswald-SemiBold.ttf")
font(OS, 700, "fonts.basic/fonts/oswald/Oswald-Bold.ttf")
font(OS, 300, "fonts.basic/fonts/oswald/Oswald-Light.ttf")
font(BE, 400, "fonts.basic/fonts/bebasneue/BebasNeue-Regular.ttf")
font(AN, 400, "fonts.basic/fonts/anton/Anton-Regular.ttf")
BW = [effect("color.basic", saturation=-1.0, contrast=0.12)]


def grad(stops, angle=0):
    return [gradient(stops, angle=angle), no_stroke()]


def argb(colour, alpha=1.0):
    return "#" + format(round(max(0.0, min(1.0, alpha)) * 255), "02x") + colour.lstrip("#").lower()[-6:]


def ease(fr, at, n):
    return k(fr, at, n)


def mix(a, b, p):
    return a + (b - a) * p


class St(S):
    """A story on 1080×1920; geometry in reference px (486×864)."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)

    # --- shapes ---------------------------------------------------------------------------------------------------
    def ob(self, name, layers, g, path=None, kind="rectangle", radius=0.0, base=None):
        """g(fr) = (cx, cy, w, h, rot, op) in reference px."""
        def geom(fr, u):
            cx, cy, w, h, rot, op = g(fr)
            return cx * R, cy * R, max(0.0, w * R), max(0.0, h * R), rot, op
        return self.obj(name, layers, geom, kind=kind, path=path, radius=radius * R,
                        base=(base[0] * R, base[1] * R) if base else None)

    def rr(self, name, layers, r, op=None, rot=None, path=None, kind="rectangle", radius=0.0, base=None):
        """r(fr) = (x0, y0, x1, y1) in reference px."""
        def g(fr):
            x0, y0, x1, y1 = r(fr)
            return ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, rot(fr) if rot else 0.0, op(fr) if op else 1.0)
        return self.ob(name, layers, g, path=path, kind=kind, radius=radius, base=base)

    def bg(self, colour=WHITE, layers=None, name="Fondo"):
        c = self.rect(name, layers or solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))
        c["layoutRole"] = "backdrop"
        return c

    # --- photos ---------------------------------------------------------------------------------------------------
    def pic(self, name, sample, box, win=None, off=None, zoom=None, path=None, kind="rectangle", look=None,
            reuse=None, label="Tu foto", rot=None, radius=0.0, op=None):
        """A photo slot laid out in box (ref px), seen through win(fr) (ref rect; the box when None) by a track
        matte; off(fr) = (dx, dy) moves photo and window; zoom(fr) scales the photo about its centre; rot(fr)
        turns the window (degrees)."""
        x0, y0, x1, y1 = box
        win = win or (lambda fr: box)
        off = off or (lambda fr: (0.0, 0.0))

        def g(fr):
            a, b, c, d = win(fr)
            dx, dy = off(fr)
            return ((a + c) / 2 + dx, (b + d) / 2 + dy, c - a, d - b, rot(fr) if rot else 0.0, 1.0)
        matte = self.ob(f"{name} (forma)", solid(WHITE), g, path=path, kind=kind, radius=radius,
                        base=(x1 - x0, y1 - y0))
        b = Box(x0 * R, y0 * R, (x1 - x0) * R, (y1 - y0) * R)
        motion = []
        for u in frames_of(self.dur):
            fr = self.frame(u)
            dx, dy = off(fr)
            motion.append((u, {"s": zoom(fr) if zoom else 1.0, "dx": dx * R, "dy": dy * R}, "linear"))
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, b, motion, label=label, reuse=reuse)
        clip["name"] = name
        if look:
            clip["effects"] = [dict(e) for e in look]
        clip["matte"] = {"clip": matte["id"], "mode": "alpha"}
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr))), 4), "linear") for u, fr in self.each()])
        return clip

    # --- words ----------------------------------------------------------------------------------------------------
    def say_(self, content, ink, family, weight, colour, name="Título", align="left", rot=0.0, off=None, op=None,
             layers=None, italic=False, reveal=None):
        """A line whose ink spans ink = (x0, cap top, x1, cap bottom) in ref px; off(fr) = (dx, dy) ref px."""
        x0, y0, x1, y1 = ink
        shift = (lambda fr: (off(fr)[0] * R, off(fr)[1] * R)) if off else None
        rv = (lambda fr: tuple(v * R for v in reveal(fr))) if reveal else None
        clip = self.say(content, (x0 * R, y0 * R, x1 * R, y1 * R), family, weight, colour, name, align=align,
                        layers=layers, italic=italic, shift=shift, reveal=rv,
                        op=(lambda fr, u: op(fr)) if op else None,
                        rot=(lambda fr, u: rot(fr)) if callable(rot) else None)
        if rot and not callable(rot):
            clip["rotation"] = keys([(0.0, rot, "hold")])
        return clip

    def para(self, content, box, family, size, colour, weight=400, align="left", line=1.15, bold=(), name="Texto",
             spacing=0.0, valign="top", italic=False):
        """A block of text in box (ref px) at size (ref px)."""
        x0, y0, x1, y1 = box
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur,
                     Box(x0 * R, y0 * R, (x1 - x0) * R, (y1 - y0) * R), family, round(size * R, 1), colour,
                     weight=weight, align=align, valign=valign, line=line, name=name, spacing=spacing * R,
                     italic=italic)
        runs = []
        for word in bold:
            i = content.find(word)
            if i >= 0:
                runs.append({"start": i, "end": i + len(word), "boldEnabled": True, "bold": True})
        if runs:
            clip["textStyle"]["runs"] = runs
        return clip

    def anim(self, clip, at, preset="fade", stagger=0.04, dur=0.3, order="forward", unit="character"):
        self.typed(clip, at, stagger=stagger, duration=dur, preset=preset, order=order, unit=unit)
        return clip

    def tint(self, clip, at, colour, stagger=0.05, dur=0.35, order="forward", domain="character", dy=0.0,
             blur=0.0):
        """Letters come in one after another faded and tinted `colour`, then settle to their own colour."""
        def slot(f):
            props = {"opacity": 0, "fillColor": argb(colour)}
            if dy:
                props["position"] = {"x": 0, "y": dy * R, "unit": "px"}
            if blur:
                props["blur"] = blur
            return {"animators": [{"name": "Aparecer", "selectors": [
                {"driver": "stagger", "domain": domain, "staggerUs": us(stagger * f), "durationUs": us(dur * f),
                 "ease": "easeOut", "order": order, "seed": 7}], "props": props}]}
        clip["textStyle"]["animation"] = {"in": dict(slot(1.0), delayUs=us(at / FPS)),
                                          "out": dict(slot(1.0 / EXIT), delayUs=us(at / FPS / EXIT))}
        return clip

    def logo(self, box, op=None, off=None):
        x0, y0, x1, y1 = box
        b = Box(x0 * R, y0 * R, (x1 - x0) * R, (y1 - y0) * R)
        off = off or (lambda fr: (0.0, 0.0))
        motion = [(u, {"dx": off(fr)[0] * R, "dy": off(fr)[1] * R}, "linear") for u, fr in self.each()]
        clip = self.t.photo(self.t.track("video", "Logo"), "logo-flip", 0.0, self.dur, b, motion, label="Tu logo",
                            brandRole="logo")
        clip["name"] = "Logo"
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr))), 4), "linear") for u, fr in self.each()])
        return clip


def dur_for(entrance, hold=2.0):
    return round(entrance + hold + entrance / EXIT, 1)


def story(id, es, en, order, entrance, tags=(), hold=2.0, colour=WHITE, thumb=None):
    D = dur_for(entrance, hold)
    t = tall(f"ig5-{id}", es, en, "instagram", D, order=order,
             tags=["instagram", "historia", "reels"] + list(tags),
             thumb_at=thumb if thumb is not None else round(entrance + hold * 0.6, 1))
    s = St(t, D)
    if colour:
        s.bg(colour)
    return t, s


def finish(t):
    return art_except(t)


def slab(cx, cy, w, h, ang):
    """(cx, cy, w, h, rot, op) of a box turned `ang` degrees."""
    return cx, cy, w, h, ang, 1.0


# =====================================================================================================================
# Trio 1 (71.4 s)
# =====================================================================================================================

RED1 = "#FF3B3B"


def wake_up():
    """A red block drops from the top, then the photo grows down pushing it to the bottom; a white V band with the
    photo's point between them; three lines rise in."""
    t, s = story("wake-up", "Historia: WAKE UP AND BE AWESOME", "Story: WAKE UP AND BE AWESOME", 15600, 2.9,
                 ["foto", "rojo", "motivación"])
    pb = lambda fr: mix(18, 555, ease(fr, 13, 22))  # noqa: E731  the photo's bottom edge

    def red(fr):
        if fr < 13:
            return (18, 18, 468, mix(20, 620, ease(fr, 0, 13)))
        top = pb(fr) + 23
        return (18, top, 468, min(846, top + 602))
    s.rr("Caja", solid(RED1), red)
    # the white V band (photo point above it) between the photo and the red
    vb = poly([(0, 0), (100, 0), (100, 100 * 23 / 62), (56.2, 100 * 23 / 62), (50, 100), (43.8, 100 * 23 / 62),
               (0, 100 * 23 / 62)])

    def band(fr):
        y = pb(fr)
        return (18, y, 468, y + 62)
    s.rr("Banda", solid(WHITE), band, path=vb, op=lambda fr: ease(fr, 13, 3))
    box = (18, 18, 468, 555)
    first = s.pic("Foto", "beach-02", box, win=lambda fr: (18, 18, 468, max(18.5, pb(fr))),
                  zoom=lambda fr: 1.12 - 0.12 * ease(fr, 13, 40))
    tip = poly([(0, 0), (100, 0), (50, 100)])
    s.pic("Foto (punta)", "beach-02", box, win=lambda fr: (215, pb(fr) - 1, 271, pb(fr) + 34), path=tip, op=lambda fr: ease(fr, 13, 3),
          zoom=lambda fr: 1.12 - 0.12 * ease(fr, 13, 40), reuse=first["placeholderId"])
    for i, (txt, ink, at) in enumerate((("WAKE UP", (96, 648, 393, 690), 66), ("AND BE", (125, 709, 362, 750), 72),
                                        ("AWESOME", (74, 768, 414, 810), 76))):
        c = s.say_(txt, ink, M, 800, WHITE, "Título" if i == 0 else f"Título {i + 1}", align="center")
        s.tint(c, at, "#FFB0B0", stagger=0.02, dur=0.3, dy=14)
    return finish(t)


def flexible_body():
    """A pink-to-orange band slides in from the left, white slabs with blue edges fly away to uncover the B/W photo,
    a white tag slides in under the band; the words come in letter by letter, tinted first."""
    t, s = story("flexible-body", "Historia: FLEXIBLE BODY con banda degradada", "Story: FLEXIBLE BODY gradient band",
                 15601, 2.2, ["foto", "fitness", "degradado", "blanco y negro"])
    ang = -13.3
    s.pic("Foto", "y2b-fit-03", (0, 0, 486, 864), look=BW, zoom=lambda fr: 1.08 - 0.08 * ease(fr, 6, 60))
    # slabs that cover the photo and fly away, alternately left and right
    slabs = [(60, 40, 260), (330, 120, 300), (110, 260, 340), (400, 360, 260), (60, 470, 300), (360, 560, 320),
             (120, 680, 300), (420, 760, 260), (180, 860, 360), (300, 0, 300), (240, 420, 340)]
    for i, (cx, cy, w) in enumerate(slabs):
        sgn = 1 if i % 2 else -1
        at = 9 + (i * 5) % 15

        def g(fr, cx=cx, cy=cy, w=w, sgn=sgn, at=at):
            p = ease(fr, at, 12)
            return cx + sgn * 700 * p, cy, w * 1.9, 140, ang, 1.0
        s.ob(f"Losa {i + 1}", solid(WHITE), g)

        def e(fr, cx=cx, cy=cy, w=w, sgn=sgn, at=at):
            p = ease(fr, at, 12)
            ex = cx - w * 0.95 * math.cos(math.radians(ang))
            ey = cy - w * 0.95 * math.sin(math.radians(ang))
            return ex + sgn * 700 * p, ey, 14, 140, ang, 1.0 if p < 0.98 else 0.0
        s.ob(f"Losa {i + 1} (borde)", solid("#1440F0"), e)
    band = grad([(0.0, "#FF2A5F"), (1.0, "#FFB33A")], angle=0)
    s.ob("Banda", band, lambda fr: (243 - 560 * (1 - ease(fr, 3, 12)), 190, 600, 106, ang, 1.0))
    s.ob("Etiqueta", solid(WHITE), lambda fr: (300 + 420 * (1 - ease(fr, 14, 10)), 336, 290, 62, ang, 1.0))
    a = s.say_("FLEXIBLE BODY", (30, 202, 455, 238), M, 900, WHITE, "Título", align="center", rot=ang)
    s.tint(a, 33, "#FF7A96", stagger=0.05, dur=0.3)
    b = s.say_("#bodyfit", (177, 316, 415, 350), M, 900, "#111111", "Etiqueta", align="center", rot=ang)
    s.tint(b, 36, "#FF2A5F", stagger=0.06, dur=0.45)
    for i, (txt, ink, at) in enumerate((("SHAPE YOUR", (83, 690, 403, 726), 30), ("BODY", (175, 750, 311, 786), 45))):
        c = s.say_(txt, ink, OU, 400, WHITE, "Texto" if i == 0 else "Texto 2", align="center")
        s.tint(c, at, "#C8963E", stagger=0.06, dur=0.6)
    return finish(t)


def modern_office():
    """The photo in a window; a second copy rises over it behind a white band and a black line; a black bar slides
    down to the bottom of the window; the title and the paragraph come in letter by letter."""
    t, s = story("modern-office", "Historia: MODERN OFFICE SPACE", "Story: MODERN OFFICE SPACE", 15602, 2.6,
                 ["foto", "oficina", "empresa", "minimalista"])
    box = (0, 185, 486, 700)
    first = s.pic("Foto", "interior-08", box)
    top = lambda fr: mix(700, 255, ease(fr, 3, 30))  # noqa: E731
    s.pic("Foto (copia)", "interior-08", box, win=lambda fr: (0, top(fr), 486, 700),
          off=lambda fr: (0, 0), zoom=None, reuse=first["placeholderId"])
    s.rr("Franja", solid(WHITE), lambda fr: (0, top(fr) - 27, 486, top(fr)),
         op=lambda fr: ease(fr, 3, 2))
    s.rr("Línea", solid(BLACK), lambda fr: (0, top(fr), 486, top(fr) + 9),
         op=lambda fr: ease(fr, 3, 2) * (1 - ease(fr, 26, 6)))
    s.rr("Barra", solid(BLACK), lambda fr: (0, mix(452, 676, ease(fr, 54, 24)), 486, mix(476, 700, ease(fr, 54, 24))),
         op=lambda fr: ease(fr, 54, 2))
    s.rr("Raya", solid("#1F6FE5"), lambda fr: (100, 58, 106, 58 + 66 * ease(fr, 50, 10)))
    a = s.say_("MODERN", (117, 60, 286, 86), M, 700, "#151515", "Título")
    s.anim(a, 51, stagger=0.04, dur=0.25, order="random")
    b = s.say_("OFFICE SPACE", (117, 98, 386, 124), M, 700, "#151515", "Título 2")
    s.anim(b, 54, stagger=0.03, dur=0.25, order="random")
    p = s.para("Some people dream of success,\nwhile other people get up every morning\nand make it happen",
               (40, 744, 470, 812), M, 15.6, "#151515", weight=500, line=1.05, bold=("success", "make it happen"))
    s.anim(p, 54, stagger=0.012, dur=0.25, order="random")
    return finish(t)


# =====================================================================================================================
# Trio 2 (75.0 s)
# =====================================================================================================================

def keep_simple():
    """A round photo of clouds pops up on a lilac-to-cream gradient; the hashtag, three big words and two small lines
    fade up one after another."""
    t, s = story("keep-simple", "Historia: KEEP IT SIMPLE con círculo", "Story: KEEP IT SIMPLE with a circle", 15603,
                 1.7, ["foto", "círculo", "degradado", "frase"], colour=None)
    s.bg(layers=grad([(0.0, "#93A2D4"), (1.0, "#F8E9CE")], angle=90))
    s.pic("Foto", "nature-01", (98, 60, 388, 350), kind="ellipse",
          win=lambda fr: (lambda r: (243 - r, 205 - r, 243 + r, 205 + r))(max(0.5, 145 * ease(fr, 2, 14))),
          zoom=lambda fr: 1.15 - 0.15 * ease(fr, 2, 40))
    h = s.say_("#easymood", (115, 409, 370, 440), PO, 600, WHITE, "Etiqueta", align="center")
    s.anim(h, 39, preset="fade", stagger=0.03, dur=0.3)
    for i, (w, ink, at) in enumerate((("KEEP", (155, 500, 331, 547), 33), ("IT", (213, 563, 273, 610), 39),
                                      ("SIMPLE", (112, 627, 374, 677), 42))):
        c = s.say_(w, ink, M, 800, WHITE, "Título" if i == 0 else f"Título {i + 1}", align="center")
        s.tint(c, at, "#DDE2F3", stagger=0.03, dur=0.4, dy=10)
    for i, (w, ink) in enumerate((("THE MOST IMPORTANT DECISION", (103, 746, 383, 760)),
                                  ("YOU MAKE IS TO BE IN A GOOD MOOD", (78, 772, 408, 786)))):
        c = s.say_(w, ink, M, 500, "#A08FC4", "Texto" if i == 0 else "Texto 2", align="center")
        s.anim(c, 36 + 3 * i, stagger=0.015, dur=0.3)
    return finish(t)


def sale_70():
    """A red block drops from the top with a slanted foot, the photo slides in from the left in a slanted frame,
    a sand block rises at the bottom; SALE, 70 % and the offer lines come in letter by letter."""
    t, s = story("sale-70", "Historia: SALE 70% con bandas inclinadas", "Story: SALE 70% slanted bands", 15604, 2.4,
                 ["foto", "rebajas", "oferta", "compras", "rojo"])
    slant = lambda dy: poly([(0, 0), (100, 0), (100, 100 - dy), (0, 100)])  # noqa: E731
    s.rr("Bloque", solid("#F2262E"), lambda fr: (16, 16, 470, mix(30, 300, ease(fr, 0, 12))),
         path=slant(100 * 95 / 284))
    ph = poly([(0, 100 * 105 / 423), (100, 0), (100, 100 * 318 / 423), (0, 100)])
    s.pic("Foto", "shopping-02", (18, 222, 468, 645), path=ph,
          off=lambda fr: (-520 * (1 - ease(fr, 27, 15)), 0), zoom=lambda fr: 1.1 - 0.1 * ease(fr, 27, 40))
    sand = poly([(0, 100 * 108 / 286), (100, 0), (100, 100), (0, 100)])
    s.rr("Bloque 2", solid("#CEC495"), lambda fr: (18, mix(846, 560, ease(fr, 33, 15)), 468, 846), path=sand,
         op=lambda fr: ease(fr, 33, 1))
    a = s.say_("SALE", (113, 55, 372, 122), M, 900, WHITE, "Título", align="center")
    s.tint(a, 51, "#FF8C8C", stagger=0.06, dur=0.3)
    b = s.say_("70%", (155, 152, 330, 207), PO, 400, WHITE, "Descuento", align="center")
    s.tint(b, 57, "#FF8C8C", stagger=0.05, dur=0.3)
    c = s.say_("#shopping", (98, 688, 390, 722), PO, 500, "#151515", "Etiqueta", align="center")
    s.tint(c, 57, "#8C845C", stagger=0.04, dur=0.3)
    d = s.para("BEST OFFER OF THE YEAR", (40, 750, 446, 780), M, 21.5, "#151515", weight=500, align="center",
               bold=("BEST OFFER",), name="Oferta")
    s.anim(d, 57, stagger=0.02, dur=0.3)
    e = s.para("limited time", (40, 786, 446, 812), PO, 20, "#151515", align="center", name="Texto")
    s.anim(e, 60, stagger=0.03, dur=0.3)
    return finish(t)


def creative_studio():
    """A full photo; a white tag grows from the left edge while the name types in on it; two lines fade in below."""
    t, s = story("creative-studio", "Historia: CREATIVE DESIGN STUDIO", "Story: CREATIVE DESIGN STUDIO", 15605, 1.8,
                 ["foto", "diseño", "estudio", "empresa"])
    s.pic("Foto", "fx-dancer-06", (0, 0, 486, 864), zoom=lambda fr: 1.06 - 0.06 * ease(fr, 0, 50))
    tag = poly([(0, 0), (100 * 327 / 345, 0), (100, 100), (0, 100)])
    s.rr("Etiqueta", solid(WHITE), lambda fr: (0, 370, max(1, 345 * ease(fr, 3, 27)), 492), path=tag)
    a = s.say_("CREATIVE", (28, 402, 192, 425), M, 800, "#111111", "Título")
    s.anim(a, 3, stagger=0.06, dur=0.05, preset="typewriter")
    b = s.say_("DESIGN STUDIO", (28, 440, 296, 463), M, 800, "#111111", "Título 2")
    s.anim(b, 15, stagger=0.045, dur=0.05, preset="typewriter")
    c = s.para("Good design is obvious.\nGreat design is transparent", (40, 742, 470, 822), OU, 30, WHITE,
               line=1.05, name="Texto")
    s.anim(c, 39, stagger=0.02, dur=0.3)
    return finish(t)


# =====================================================================================================================
# Trio 3 (79.1 s)
# =====================================================================================================================

def mindfulness():
    """The B/W photo opens from a small framed window in the middle to the whole story; a warm band tints it on a
    slant; a white tag on top and the hashtag below come in letter by letter."""
    t, s = story("mindfulness", "Historia: #mindfulness en blanco y negro", "Story: B/W #mindfulness", 15606, 2.2,
                 ["foto", "blanco y negro", "frase", "calma"])
    win = lambda fr: (lambda p: (243 - 243 * p, 432 - 432 * p, 243 + 243 * p, 432 + 432 * p))(  # noqa: E731
        max(0.002, ease(fr, 4, 20)))
    s.rr("Marco", solid(WHITE), lambda fr: (lambda r: (r[0] - 6, r[1] - 6, r[2] + 6, r[3] + 6))(win(fr)),
         op=lambda fr: 1 - ease(fr, 20, 4))
    s.pic("Foto", "portrait-08", (0, 0, 486, 864), win=win, look=BW, zoom=lambda fr: 1.25 - 0.25 * ease(fr, 4, 30))
    band = poly([(100 * 110 / 486, 0), (100, 0), (100, 100 * 580 / 864), (100 * 395 / 486, 100), (0, 100),
                 (0, 100 * 340 / 864)])
    c = s.rr("Tono", solid("#D2B48C"), lambda fr: (0, 0, 486, 864), path=band,
             op=lambda fr: 0.55 * ease(fr, 20, 9))
    c["blendMode"] = "multiply"
    s.rr("Etiqueta", solid(WHITE), lambda fr: (243 - 118 * ease(fr, 42, 8), 50, 243 + 118 * ease(fr, 42, 8), 105))
    a = s.say_("#mindfulness", (140, 67, 348, 88), PO, 500, "#151515", "Etiqueta", align="center")
    s.anim(a, 45, stagger=0.03, dur=0.25)
    b = s.say_("#energy", (135, 753, 352, 785), PO, 600, WHITE, "Título", align="center")
    s.anim(b, 45, stagger=0.05, dur=0.3)
    d = s.say_("ATTENTION TO LITTLE THINGS", (50, 808, 438, 820), M, 500, WHITE, "Texto", align="center")
    s.anim(d, 48, stagger=0.02, dur=0.25)
    return finish(t)


def ocean():
    """A white dot, then the photo opens in a circle round it and a second, wider circle opens the whole photo; a
    pale disc stays in the middle with the hashtag and the big word."""
    t, s = story("ocean", "Historia: OCEAN en un círculo", "Story: OCEAN in a circle", 15607, 2.3,
                 ["foto", "círculo", "mar", "surf", "verano"], colour="#E2E1E1")

    def circ(r):
        return lambda fr: (lambda q: (243 - q, 432 - q, 243 + q, 432 + q))(max(0.3, r(fr)))
    first = s.pic("Foto", "y5-h-ocean-02", (0, 0, 486, 864), kind="ellipse",
                  win=circ(lambda fr: mix(205, 640, ease(fr, 27, 18)) * ease(fr, 15, 14)),
                  zoom=lambda fr: 1.2 - 0.2 * ease(fr, 15, 40))
    s.ob("Disco", solid(WHITE), lambda fr: (243, 432, 404 * ease(fr, 15, 14), 404 * ease(fr, 15, 14), 0,
                                           0.22 * ease(fr, 27, 6)), kind="ellipse")
    s.ob("Punto", solid(WHITE), lambda fr: (243, mix(432, 535, ease(fr, 27, 12)), 30 * ease(fr, 2, 6),
                                           30 * ease(fr, 2, 6), 0, 1.0), kind="ellipse")
    a = s.say_("#surfing", (133, 313, 357, 350), PO, 600, WHITE, "Etiqueta", align="center")
    s.anim(a, 57, stagger=0.04, dur=0.3, order="random")
    b = s.say_("OCEAN", (92, 405, 395, 455), M, 900, WHITE, "Título", align="center")
    s.anim(b, 57, stagger=0.05, dur=0.35, order="random")
    return finish(t)


def look_deep():
    """A yellow sheet over the photo narrows to a line and vanishes; the two lines fade in letter by letter and two
    blue tags slide in from the sides."""
    t, s = story("look-deep", "Historia: LOOK DEEP INTO YOURSELF", "Story: LOOK DEEP INTO YOURSELF", 15608, 2.6,
                 ["foto", "frase", "neón", "etiquetas"])
    s.pic("Foto", "fx-woman-02", (0, 0, 486, 864), zoom=lambda fr: 1.1 - 0.1 * ease(fr, 0, 60))
    s.rr("Hoja", solid("#FFD93F"), lambda fr: (mix(0, 288, ease(fr, 2, 24)), 0, mix(486, 292, ease(fr, 2, 24)), 864),
         op=lambda fr: 1 - ease(fr, 30, 9))
    for i, (w, ink, at) in enumerate((("LOOK DEEP", (130, 70, 355, 105), 60), ("INTO YOURSELF", (82, 120, 405, 160), 63))):
        c = s.say_(w, ink, OS, 500, WHITE, "Título" if i == 0 else "Título 2", align="center")
        s.anim(c, at, stagger=0.04, dur=0.3, order="random")
    off1 = lambda fr: (240 * (1 - ease(fr, 57, 9)), 0)  # noqa: E731
    off2 = lambda fr: (-330 * (1 - ease(fr, 57, 9)), 0)  # noqa: E731
    s.rr("Etiqueta", solid("#21A8C6"), lambda fr: (262 + off1(fr)[0], 580, 490 + off1(fr)[0], 645))
    s.rr("Etiqueta 2", solid("#21A8C6"), lambda fr: (-4 + off2(fr)[0], 715, 315 + off2(fr)[0], 782))
    a = s.say_("# LIGHT", (285, 600, 460, 630), OS, 500, WHITE, "Etiqueta", off=off1)
    b = s.say_("# OPENMIND", (22, 735, 297, 765), OS, 500, WHITE, "Etiqueta 2", off=off2)
    return finish(t)



# =====================================================================================================================
# Trio 4 (83.0 s)
# =====================================================================================================================

KS = "Kaushan Script"
font(KS, 400, "fonts.basic/fonts/kaushanscript/KaushanScript-Regular.ttf")


def gentle_soft():
    """Salmon stripes cover the story and squeeze into a line that vanishes over the photo of roses; a white line
    opens into a card and its words come in one after another: tag, framed word, three big words, a rule, a script
    line and a round arrow."""
    t, s = story("gentle-soft", "Historia: GENTLE & SOFT con tarjeta", "Story: GENTLE & SOFT card", 15609, 3.5,
                 ["foto", "flores", "tarjeta", "rosa"])
    s.pic("Foto", "flowers-03", (0, 0, 486, 864), zoom=lambda fr: 1.08 - 0.08 * ease(fr, 6, 60))
    tones = ["#E8A68E", "#F3C9B8", "#D98466", "#FFFFFF", "#E59A7F", "#F6D3C4", "#CF7556", "#EDB39E"]
    sq = lambda fr: ease(fr, 9, 30)  # noqa: E731

    def stripe(i):
        def r(fr):
            y0, y1 = i * 108, (i + 1) * 108
            c = 440
            p = sq(fr)
            return (0, c + (y0 - c) * (1 - p), 486, c + (y1 - c) * (1 - p) + 0.6 * (1 - p))
        return r
    for i, col in enumerate(tones):
        s.rr(f"Franja {i + 1}", solid(col), stripe(i), op=lambda fr: 1 - ease(fr, 38, 4))
    s.rr("Tarjeta", solid(WHITE), lambda fr: (243 - 181 * ease(fr, 60, 12), mix(500, 178, ease(fr, 57, 6)),
                                              243 + 181 * ease(fr, 60, 12) + 4, mix(560, 687, ease(fr, 57, 6))))
    a = s.say_("#flowersforyou", (150, 212, 337, 228), PO, 600, "#151515", "Etiqueta", align="center")
    s.anim(a, 90, stagger=0.02, dur=0.25)
    s.rr("Recuadro", ring(BLACK, 4 * R), lambda fr: (112, 262, 112 + 261 * ease(fr, 84, 9), 337),
         op=lambda fr: ease(fr, 84, 2))
    b = s.say_("MIRACLE", (135, 283, 350, 318), M, 700, "#151515", "Título", align="center")
    s.anim(b, 87, stagger=0.03, dur=0.25)
    for i, (w, ink, at) in enumerate((("GENTLE", (140, 378, 347, 412), 84), ("&", (228, 420, 258, 450), 90),
                                      ("SOFT", (175, 458, 313, 492), 93))):
        c = s.say_(w, ink, M, 800, "#151515", f"Título {i + 2}", align="center")
        s.anim(c, at, stagger=0.04, dur=0.3)
    s.rr("Raya", solid("#151515"), lambda fr: (243 - 130.5 * ease(fr, 96, 8), 531, 243 + 130.5 * ease(fr, 96, 8), 536))
    d = s.say_("Best wishes", (95, 590, 390, 630), KS, 400, "#151515", "Firma", align="center")
    s.anim(d, 93, stagger=0.04, dur=0.3)
    s.ob("Flecha (círculo)", solid("#222222"), lambda fr: (243, 687, 56 * ease(fr, 99, 8), 56 * ease(fr, 99, 8), 0, 1),
         kind="ellipse")
    chev = "M 0 0 L 50 60 L 100 0"
    s.ob("Flecha", ring(WHITE, 3 * R), lambda fr: (243, 685, 24 * ease(fr, 102, 6), 13 * ease(fr, 102, 6), 0, 1),
         path=chev, base=(24, 13))
    return finish(t)


def power():
    """A red sheet over everything slides away to the right; the photo rises under the white top with its slanted
    foot; #POWER and the two lines come in letter by letter."""
    t, s = story("power", "Historia: #POWER con foto", "Story: #POWER with a photo", 15610, 2.2,
                 ["foto", "rojo", "moda", "frase"])
    s.pic("Foto", "y5-outfit-02", (0, 190, 486, 864), off=lambda fr: (0, 260 * (1 - ease(fr, 6, 20))),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 6, 40))
    top = poly([(0, 0), (100, 0), (100, 100 * 205 / 290), (0, 100)])
    s.rr("Fondo arriba", solid(WHITE), lambda fr: (0, 0, 486, 290), path=top)
    s.rr("Hoja", solid("#EA3A1C"), lambda fr: (mix(0, 490, ease(fr, 4, 26)), 0, 490, 864))
    a = s.say_("#POWER", (60, 57, 428, 107), M, 900, "#EA3A1C", "Título")
    s.anim(a, 39, stagger=0.05, dur=0.25)
    for i, (w, ink) in enumerate((("IF YOU WANT DIFFERENT RESULTS,", (57, 136, 432, 150)),
                                  ("MAKE DIFFERENT CHOICES", (57, 160, 338, 175)))):
        c = s.say_(w, ink, M, 700, "#222222", "Texto" if i == 0 else "Texto 2")
        s.anim(c, 42 + 6 * i, stagger=0.015, dur=0.2)
    return finish(t)


def light_easy():
    """Coloured dashes rain over the photo; a white card opens from its middle and the two big words and the line
    under them come in."""
    t, s = story("light-easy", "Historia: LIGHT & EASY con tarjeta", "Story: LIGHT & EASY card", 15611, 2.2,
                 ["foto", "moda", "tarjeta", "azul"])
    s.pic("Foto", "outfit-04", (0, 0, 486, 864), zoom=lambda fr: 1.08 - 0.08 * ease(fr, 0, 60))
    cols = ["#3D7BEA", "#F2E14C", "#7CCB3E", WHITE]
    xs = [70, 150, 225, 300, 380, 440, 110, 260, 340, 190, 410, 40]
    for i, x in enumerate(xs):
        at = (i * 7) % 18
        y = 80 + (i * 137) % 600

        def g(fr, x=x, y=y, at=at):
            p = ease(fr, at, 18)
            return x, y + 160 * p, 7, 34, 0, (1 - p) * ease(fr, at, 2)
        s.ob(f"Raya {i + 1}", solid(cols[i % 4]), g)
    s.rr("Tarjeta", solid(WHITE), lambda fr: (lambda p, q: (243 - 183 * p, 333 - 151 * q, 243 + 183 * p,
                                                            333 + 151 * q))(ease(fr, 36, 9), ease(fr, 36, 9)))
    for i, (w, ink, at) in enumerate((("LIGHT&", (128, 260, 355, 300), 51), ("EASY", (165, 310, 318, 348), 54))):
        c = s.say_(w, ink, M, 800, "#7D8BC4", "Título" if i == 0 else "Título 2", align="center")
        s.tint(c, at, "#E4E8F6", stagger=0.04, dur=0.35)
    for i, (w, ink) in enumerate((("CASUAL AND COMFORTABLE", (107, 374, 376, 388)),
                                  ("STYLE FOR EVERYDAY LOOK", (112, 396, 371, 410)))):
        c = s.say_(w, ink, M, 500, "#222222", "Texto" if i == 0 else "Texto 2", align="center")
        s.anim(c, 51 + 3 * i, stagger=0.015, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 5 (87.5 s)
# =====================================================================================================================

YEL = "#F4EE4A"


def flat_photo(s, name, sample, box, look=None, zoom=None, off=None, label="Tu foto"):
    """A photo slot laid out straight in box (ref px), no matte (so it can turn in 3D)."""
    x0, y0, x1, y1 = box
    b = Box(x0 * R, y0 * R, (x1 - x0) * R, (y1 - y0) * R)
    off = off or (lambda fr: (0.0, 0.0))
    motion = [(u, {"s": zoom(fr) if zoom else 1.0, "dx": off(fr)[0] * R, "dy": off(fr)[1] * R}, "linear")
              for u, fr in s.each()]
    clip = s.t.photo(s.t.track("video", name), sample, 0.0, s.dur, b, motion, label=label)
    clip["name"] = name
    if look:
        clip["effects"] = [dict(e) for e in look]
    return clip


def daring_style():
    """On yellow, the B/W photo swings open in 3D like a door; the two big words type in over its top edge, bars
    and small lines come in round it and a white bar grows down beside the motto."""
    t, s = story("daring-style", "Historia: DARING STYLE sobre amarillo", "Story: DARING STYLE on yellow", 15612, 2.6,
                 ["foto", "amarillo", "moda", "blanco y negro"], colour=YEL)
    c = flat_photo(s, "Foto", "fx-hair-02", (70, 125, 416, 738), look=BW)
    s.d3(c, ry=lambda fr, u: 88 * (1 - ease(fr, 3, 24)), persp=1600)
    for i, (w, ink, at) in enumerate((("DARING", (47, 145, 440, 212), 45), ("STYLE", (47, 230, 343, 297), 57))):
        a = s.say_(w, ink, M, 800, "#111111", "Título" if i == 0 else "Título 2")
        s.anim(a, at, stagger=0.06, dur=0.15)
    s.rr("Raya", solid("#111111"), lambda fr: (70, 107, 70 + 105 * ease(fr, 48, 8), 115))
    b = s.say_("CREATE YOURSELF", (182, 106, 307, 116), M, 700, "#111111", "Texto")
    s.anim(b, 51, stagger=0.02, dur=0.2)
    s.rr("Barra", solid(WHITE), lambda fr: (120, 488, 165, 488 + 197 * ease(fr, 72, 9)))
    for i, (w, ink) in enumerate((("BE WILD", (178, 566, 275, 582)), ("BUT STAY SOFT", (178, 591, 352, 607)))):
        a = s.say_(w, ink, M, 700, WHITE, "Lema" if i == 0 else "Lema 2")
        s.anim(a, 72 + 3 * i, stagger=0.03, dur=0.2)
    s.rr("Raya 2", solid("#111111"), lambda fr: (330 - 105 * ease(fr, 72, 8), 746, 330, 754))
    d = s.say_("YOUR MOVE", (335, 745, 416, 756), M, 700, "#111111", "Texto 2")
    s.anim(d, 75, stagger=0.03, dur=0.2)
    return finish(t)


def dancing():
    """On a lilac gradient a blurred photo of lights opens from a band in the middle; the dancer's photo rises in
    under a diagonal edge; a white tag opens with the hashtag and the line at the foot fades in."""
    t, s = story("dancing", "Historia: #DANCING con foto en diagonal", "Story: #DANCING diagonal photo", 15613, 3.6,
                 ["foto", "baile", "diagonal", "bokeh"], colour=None)
    s.bg(layers=grad([(0.0, "#7C86C4"), (1.0, "#C9A2A9")], angle=90))
    band = lambda fr: (lambda p: (0, mix(300, 0, p), 486, mix(400, 864, p)))(ease(fr, 9, 30))  # noqa: E731
    lights = s.pic("Luces", "xmaslights-02", (0, 0, 486, 864), win=band, label="Fondo",
                   op=lambda fr: ease(fr, 9, 4))
    lights["effects"] = [effect("builtin.effects.gaussian_blur", u_blurRadius=14.0)]
    s.rr("Tono", solid("#E8B0B8"), lambda fr: (0, 0, 486, 864), op=lambda fr: 0.35 * ease(fr, 9, 4))
    diag = poly([(0, 100 * 328 / 704), (100, 0), (100, 100), (0, 100)])
    s.pic("Foto", "y5-street-02", (0, 160, 486, 864), path=diag, off=lambda fr: (0, 720 * (1 - ease(fr, 51, 21))),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 51, 40))
    s.rr("Etiqueta", solid(WHITE), lambda fr: (243 - 147.5 * ease(fr, 99, 12), 70, 243 + 147.5 * ease(fr, 99, 12), 142))
    a = s.say_("#DANCING", (110, 88, 375, 122), M, 800, "#5A4048", "Título", align="center")
    s.anim(a, 102, stagger=0.04, dur=0.25)
    for i, (w, ink) in enumerate((("ONLY YOU ARE CHOOSE", (102, 785, 382, 803)),
                                  ("YOUR LIFE STYLE", (145, 810, 340, 828)))):
        c = s.say_(w, ink, M, 700, "#5A4048", "Texto" if i == 0 else "Texto 2", align="center")
        s.anim(c, 90 + 3 * i, stagger=0.02, dur=0.3)
    return finish(t)


def beach_therapy():
    """Yellow fills the story from the top, a green-blue block follows it down with a blue edge that melts into a
    yellow line, the photo rises in underneath; a yellow tag and the lines come in."""
    t, s = story("beach-therapy", "Historia: beach therapy verde agua", "Story: teal beach therapy", 15614, 2.6,
                 ["foto", "playa", "vacaciones", "verano"])
    s.rr("Amarillo", solid(YEL), lambda fr: (18, 18, 468, mix(20, 846, ease(fr, 3, 21))))
    teal = lambda fr: mix(20, 308, ease(fr, 27, 21))  # noqa: E731
    s.rr("Bloque", solid("#84C3AF"), lambda fr: (18, 18, 468, teal(fr)), op=lambda fr: ease(fr, 27, 1))
    s.rr("Borde", solid("#6474E5"), lambda fr: (18, teal(fr), 468, teal(fr) + 30 * (1 - ease(fr, 48, 9))),
         op=lambda fr: ease(fr, 27, 1))
    s.pic("Foto", "fx-beach-02", (18, 326, 468, 846), win=lambda fr: (18, mix(846, 326, ease(fr, 57, 10)), 468, 846),
          zoom=lambda fr: 1.12 - 0.12 * ease(fr, 57, 40))
    s.rr("Etiqueta", solid(YEL), lambda fr: (243 - 147.5 * ease(fr, 60, 10), 72, 243 + 147.5 * ease(fr, 60, 10), 126))
    a = s.say_("beach therapy", (112, 88, 375, 108), PO, 500, "#222222", "Etiqueta", align="center")
    s.anim(a, 66, stagger=0.04, dur=0.25)
    b = s.say_("#bestvacation", (145, 177, 340, 197), PO, 600, WHITE, "Título", align="center")
    s.anim(b, 69, stagger=0.04, dur=0.25)
    for i, (w, ink) in enumerate((("SKY ABOVE OUR HEADS. SAND BENEATH", (50, 247, 436, 260)),
                                  ("OUR FEET. LIFE IS GOOD", (122, 265, 364, 278)))):
        c = s.say_(w, ink, M, 700, WHITE, "Texto" if i == 0 else "Texto 2", align="center")
        s.anim(c, 72 + 3 * i, stagger=0.015, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 6 (92.6 s)
# =====================================================================================================================

def wave_path(top_amp, bot_amp, phase=0.0, n=24):
    """A band (0..100 box) whose top and bottom edges are gentle waves (amplitudes in % of the box height)."""
    top = [(100 * i / n, top_amp * (1 + math.sin(phase + 2 * math.pi * i / n * 0.9))) for i in range(n + 1)]
    bot = [(100 * i / n, 100 - bot_amp * (1 + math.sin(phase + 1.3 + 2 * math.pi * i / n * 0.8)))
           for i in range(n, -1, -1)]
    return poly(top + bot)


def sensual():
    """Two red blocks slide in from the sides and the two B/W photos open over them, leaving thin red edges that
    shrink away; the vertical word and the red motto type in."""
    t, s = story("sensual", "Historia: SENSUAL con dos fotos", "Story: SENSUAL two photos", 15615, 2.9,
                 ["foto", "blanco y negro", "collage", "moda"])
    s.rr("Rojo", solid("#F02B1E"), lambda fr: (0, 30, mix(0, 388, ease(fr, 6, 10)) - mix(0, 16, ease(fr, 30, 24)), 462))
    s.rr("Rojo 2", solid("#F02B1E"), lambda fr: (mix(486, 98, ease(fr, 9, 10)) + mix(0, 16, ease(fr, 30, 24)), 485,
                                                 486, 833))
    s.pic("Foto", "fx-figure-02", (30, 30, 372, 462), look=BW,
          win=lambda fr: (30, 30, max(30.5, mix(30, 372, ease(fr, 15, 12))), 462), label="Foto 1")
    s.rr("Bloque", solid("#111111"), lambda fr: (393, 428, 456, 485), op=lambda fr: ease(fr, 24, 3))
    s.pic("Foto 2", "pet-03", (114, 485, 456, 833), look=BW,
          win=lambda fr: (min(455.5, mix(456, 114, ease(fr, 18, 12))), 485, 456, 833), label="Foto 2")
    v = s.para("S\nE\nN\nS\nU\nA\nL", (412, 26, 448, 262), M, 20, "#111111", weight=500, align="center", line=1.42,
               name="Palabra")
    s.anim(v, 66, stagger=0.07, dur=0.2)
    for i, (w, ink) in enumerate((("STAY WILD", (30, 745, 250, 762)), ("AND GRACEFUL", (30, 780, 340, 797)))):
        c = s.say_(w, ink, M, 500, "#F02B1E", "Lema" if i == 0 else "Lema 2")
        s.anim(c, 66 + 3 * i, stagger=0.04, dur=0.25, order="random")
    return finish(t)


def denim_style():
    """A slate sheet; the photo slides in over it from the left; the hashtag, a square that draws itself with a
    letter in each corner, the two words in the middle and the line at the foot fade in."""
    t, s = story("denim-style", "Historia: DENIM STYLE con recuadro", "Story: DENIM STYLE framed", 15616, 3.0,
                 ["foto", "moda", "recuadro", "colección"], colour="#41687F")
    s.pic("Foto", "fashion-04", (0, 0, 486, 864), win=lambda fr: (0, 0, max(0.5, mix(0, 486, ease(fr, 12, 18))), 864),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 12, 40))
    a = s.say_("#newcollection", (80, 44, 407, 62), PO, 400, WHITE, "Etiqueta", align="center")
    s.anim(a, 45, stagger=0.03, dur=0.3)
    sq = (75, 264, 412, 600)
    L = 3.0
    p = lambda fr: ease(fr, 60, 24)  # noqa: E731
    s.rr("Recuadro (arriba)", solid(WHITE), lambda fr: (sq[0], sq[1], sq[0] + (sq[2] - sq[0]) * p(fr), sq[1] + L))
    s.rr("Recuadro (derecha)", solid(WHITE), lambda fr: (sq[2] - L, sq[1], sq[2], sq[1] + (sq[3] - sq[1]) * p(fr)))
    s.rr("Recuadro (abajo)", solid(WHITE), lambda fr: (sq[2] - (sq[2] - sq[0]) * p(fr), sq[3] - L, sq[2], sq[3]))
    s.rr("Recuadro (izquierda)", solid(WHITE), lambda fr: (sq[0], sq[3] - (sq[3] - sq[1]) * p(fr), sq[0] + L, sq[3]))
    for i, (w, ink) in enumerate((("IN", (92, 289, 122, 302)), ("S", (376, 289, 388, 302)), ("T", (96, 563, 106, 577)),
                                  ("A", (377, 563, 389, 577)))):
        c = s.say_(w, ink, M, 500, WHITE, f"Letra {i + 1}", align="center")
        s.anim(c, 72 + 3 * i, stagger=0.05, dur=0.3)
    for i, (w, ink) in enumerate((("DENIM", (153, 390, 333, 422)), ("STYLE", (153, 440, 333, 472)))):
        c = s.say_(w, ink, M, 500, WHITE, "Título" if i == 0 else "Título 2", align="center")
        s.anim(c, 63 + 6 * i, stagger=0.05, dur=0.3, order="random")
    for i, (w, ink) in enumerate((("DENIM IS ALWAYS", (70, 766, 418, 783)), ("A GOOD IDEA", (113, 800, 373, 817)))):
        c = s.say_(w, ink, M, 500, WHITE, "Texto" if i == 0 else "Texto 2", align="center")
        s.anim(c, 57 + 6 * i, stagger=0.04, dur=0.3, order="random")
    return finish(t)


def beauty_pro():
    """A purple sheet is swept up by a red wave that uncovers the B/W photo; a red-to-purple tint stays on its lower
    part; BEAUTY, the hashtag and the line fade in."""
    t, s = story("beauty-pro", "Historia: BEAUTY con ola morada", "Story: BEAUTY purple wave", 15617, 2.6,
                 ["foto", "belleza", "morado", "blanco y negro"])
    s.pic("Foto", "fx-face-03", (0, 0, 486, 864), look=BW, zoom=lambda fr: 1.1 - 0.1 * ease(fr, 12, 50))
    tint = s.rr("Tono", grad([(0.0, "#E8204C"), (1.0, "#8A1A9F")], angle=0), lambda fr: (0, 535, 486, 864),
                path=wave_path(4, 0, 0.6), op=lambda fr: 0.88 * ease(fr, 27, 9))
    tint["blendMode"] = "normal"
    d = lambda fr: mix(864, -140, ease(fr, 12, 33))  # noqa: E731
    s.rr("Hoja", solid("#7B1570"), lambda fr: (0, -20, 486, d(fr) + 20))
    s.rr("Ola", solid("#F42A2E"), lambda fr: (0, d(fr), 486, d(fr) + 110), path=wave_path(12, 12, 0.3))
    a = s.say_("BEAUTY", (70, 535, 415, 592), M, 800, WHITE, "Título", align="center")
    s.anim(a, 57, stagger=0.04, dur=0.3)
    b = s.say_("# professional", (70, 620, 418, 640), PO, 400, WHITE, "Etiqueta", align="center")
    s.anim(b, 63, stagger=0.04, dur=0.3)
    for i, (w, ink) in enumerate((("BEAUTY IS ABOUT TO BEING COMFORTABLE", (68, 738, 415, 750)),
                                  ("IN YOUR OWN SKIN", (167, 756, 318, 768)))):
        c = s.say_(w, ink, M, 700, WHITE, "Texto" if i == 0 else "Texto 2", align="center")
        s.anim(c, 69 + 3 * i, stagger=0.015, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 7 (96.7 s)
# =====================================================================================================================

SEPIA = [effect("color.basic", saturation=-0.85, contrast=0.1)]


def dot_grid(x0, y0, x1, y1, cols, rows, d=1.0):
    """One path (0..100 box) with a small octagon dot of `d` % at every grid point."""
    out = []
    for r in range(rows):
        for c in range(cols):
            cx = 100 * c / max(1, cols - 1)
            cy = 100 * r / max(1, rows - 1)
            pts = [(cx + d * math.cos(math.radians(45 * i)), cy + d * (x1 - x0) / (y1 - y0) * math.sin(math.radians(45 * i)))
                   for i in range(8)]
            out.append(poly(pts))
    return " ".join(out)


def awesome():
    """On dark, the sepia photo uncovers from the top in a staircase with red steps at its edge; AWESOME runs down
    in red letter by letter, the spaced lines and the framed hashtag follow."""
    t, s = story("awesome", "Historia: AWESOME en vertical", "Story: vertical AWESOME", 15618, 3.0,
                 ["foto", "rojo", "vertical", "retrato"], colour="#18171A")
    cols = 6
    for i in range(cols):
        x0, x1 = 486 * i / cols, 486 * (i + 1) / cols
        at = 15 + (cols - 1 - i) * 4
        edge = lambda fr, at=at: mix(0, 864, ease(fr, at, 30))  # noqa: E731
        kw = {} if i == 0 else {"reuse": first["placeholderId"]}
        c = s.pic("Foto" if i == 0 else f"Foto ({i + 1})", "fx-man-04", (0, 0, 486, 864), look=SEPIA,
                  win=lambda fr, x0=x0, x1=x1, edge=edge: (x0, 0, x1 + 0.5, max(0.5, edge(fr))), **kw)
        if i == 0:
            first = c
        s.rr(f"Escalón {i + 1}", solid("#F0241E"),
             lambda fr, x0=x0, x1=x1, edge=edge: (x0 + 20, edge(fr), x1, edge(fr) + 24),
             op=lambda fr, at=at: ease(fr, at, 2) * (1 - ease(fr, at + 28, 4)))
    tone = s.rr("Tono", solid("#E2D2B0"), lambda fr: (0, 0, 486, 864), op=lambda fr: 0.55 * ease(fr, 40, 6))
    tone["blendMode"] = "multiply"
    v = s.para("A\nW\nE\nS\nO\nM\nE", (100, 128, 170, 680), M, 50, "#F0241E", weight=600, align="center", line=1.37,
               name="Título")
    s.anim(v, 66, stagger=0.07, dur=0.2)
    body = s.para("BE BOLD ENOUGH\nTO USE YOUR VOICE,\nAND STRONG\nTO LIVE THE LIFE\nYOU'VE ALWAYS\nIMAGINED",
                  (186, 664, 486, 784), M, 11.5, "#F0241E", weight=600, line=1.55, spacing=5.4, name="Texto")
    s.anim(body, 75, stagger=0.01, dur=0.25, order="random")
    s.rr("Recuadro", ring("#F0241E", 2 * R), lambda fr: (183, 810, 183 + 119 * ease(fr, 81, 8), 838),
         op=lambda fr: ease(fr, 81, 2))
    h = s.say_("#followme", (196, 818, 290, 830), PO, 500, "#F0241E", "Etiqueta")
    s.anim(h, 84, stagger=0.03, dur=0.2)
    return finish(t)


def focus_breathe():
    """On black the photo drops open from the top, a white band slides down under it and fills the foot; the three
    condensed words, the numbers and the spaced line fade in."""
    t, s = story("focus-breathe", "Historia: FOCUS ON THE BREATHE", "Story: FOCUS ON THE BREATHE", 15619, 2.6,
                 ["foto", "frase", "tipografía", "naranja"], colour="#111111")
    s.pic("Foto", "fx-man-03", (0, 0, 486, 548), win=lambda fr: (0, 0, 486, max(0.5, mix(0, 548, ease(fr, 12, 30)))),
          zoom=lambda fr: 1.12 - 0.12 * ease(fr, 12, 40))
    tone = s.rr("Tono", solid("#C6622C"), lambda fr: (0, 0, 486, 548), op=lambda fr: 0.85 * ease(fr, 12, 4))
    tone["blendMode"] = "multiply"
    s.rr("Panel", solid(WHITE), lambda fr: (0, mix(520, 548, ease(fr, 39, 12)), 486,
                                            mix(540, 864, ease(fr, 45, 12))), op=lambda fr: ease(fr, 39, 2))
    for i, (w, ink, at) in enumerate((("FOCUS", (36, 580, 255, 655), 54), ("ON THE", (36, 668, 265, 745), 60),
                                      ("BREATHE", (36, 755, 342, 832), 63))):
        c = s.say_(w, ink, OS, 600, "#1E1E1E", "Título" if i == 0 else f"Título {i + 1}")
        s.tint(c, at, "#BBBBBB", stagger=0.03, dur=0.3)
    a = s.say_("ACHIEVING PERFECTION", (40, 507, 450, 528), OS, 500, WHITE, "Texto", align="center")
    s.anim(a, 72, stagger=0.02, dur=0.25)
    for i, (w, ink) in enumerate((("48", (37, 35, 74, 55)), ("712", (405, 35, 457, 55)))):
        c = s.say_(w, ink, OS, 500, WHITE, f"Número {i + 1}", align="left" if i == 0 else "right")
        s.anim(c, 75, stagger=0.05, dur=0.25)
    return finish(t)


def your_choice():
    """A red sheet covers the B/W portrait and goes; a field of yellow dots and a tall yellow frame draw in with a
    short text inside, a line up the side and a hashtag at the foot."""
    t, s = story("your-choice", "Historia: retrato con puntos amarillos", "Story: portrait with yellow dots", 15620,
                 3.2, ["foto", "amarillo", "puntos", "blanco y negro"])
    s.pic("Foto", "fx-man-06", (0, 0, 486, 864), look=BW, zoom=lambda fr: 1.08 - 0.08 * ease(fr, 50, 40))
    s.rr("Hoja", solid("#E5242A"), lambda fr: (0, mix(0, 864, ease(fr, 50, 18)), 486, 864))
    holes = s.rr("Puntos (hoja)", solid("#141414"), lambda fr: (8, mix(10, 874, ease(fr, 50, 18)), 478,
                                                                 mix(854, 1718, ease(fr, 50, 18))),
                 path=dot_grid(0, 0, 470, 844, 14, 25, 2.2 + 0.0))
    holes["opacity"] = keys([(u, round(min(1.0, ease(fr, 3, 30)), 4), "linear") for u, fr in s.each()])
    s.rr("Puntos", solid("#F2E62E"), lambda fr: (22, 145, 470, 385), path=dot_grid(22, 145, 470, 385, 13, 8, 0.8),
         op=lambda fr: ease(fr, 69, 9))
    s.rr("Marco", ring("#F2E62E", 4 * R), lambda fr: (180, 128, 306, 128 + 442 * ease(fr, 72, 18)),
         op=lambda fr: ease(fr, 72, 2))
    p = s.para("TALENT IS\nA GIFT, BUT\nCHARACTER\nIS A CHOICE", (196, 474, 306, 556), M, 13.5, "#F2E62E", weight=500,
               line=1.3, name="Texto")
    s.anim(p, 84, stagger=0.02, dur=0.25)
    side = s.say_("YOU ARE THE ARTIST OF YOUR LIFE", (342, 593, 580, 606), M, 500, "#F2E62E", "Texto 2",
                  align="center", rot=-90.0)
    s.anim(side, 87, stagger=0.015, dur=0.25)
    h = s.say_("#yourchoice", (193, 817, 290, 832), PO, 500, "#F2E62E", "Etiqueta")
    s.anim(h, 90, stagger=0.03, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 8 (101.3 s)
# =====================================================================================================================

TEAL = "#22908A"


def best_look():
    """The photo, tinted green, fills the story; the same photo in colour opens from a line in the middle into a
    tall frame, yellow bars slide in above and below it and the words fade in."""
    t, s = story("best-look", "Historia: YOUR BEST LOOK con marco", "Story: YOUR BEST LOOK framed", 15621, 2.4,
                 ["foto", "verde", "moda", "amarillo"], colour="#2E7D66")
    back = s.pic("Fondo foto", "fx-fashion-03", (0, 0, 486, 864), look=BW, zoom=lambda fr: 1.15, label="Tu foto")
    back["opacity"] = keys([(0.0, 0.45, "hold")])
    back["blendMode"] = "multiply"
    s.pic("Foto", "fx-fashion-03", (48, 126, 438, 738), reuse=back["placeholderId"],
          win=lambda fr: (lambda p: (243 - 195 * p, 126, 243 + 195 * p + 0.5, 738))(ease(fr, 21, 12)),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 21, 40))
    s.rr("Barra", solid("#F6E92A"), lambda fr: (138 + 360 * (1 - ease(fr, 36, 9)), 88, 438 + 360 * (1 - ease(fr, 36, 9)),
                                                 126))
    s.rr("Barra 2", solid("#F6E92A"), lambda fr: (48 - 360 * (1 - ease(fr, 36, 9)), 738,
                                                  347 - 360 * (1 - ease(fr, 36, 9)), 776))
    for i, (w, ink) in enumerate((("YOUR BEST", (77, 163, 294, 190)), ("LOOK", (77, 199, 183, 226)))):
        c = s.say_(w, ink, M, 800, WHITE, "Título" if i == 0 else "Título 2")
        s.anim(c, 42 + 3 * i, stagger=0.05, dur=0.3, order="random")
    b = s.say_("YOUR KNOW WHAT YOU WANT", (52, 808, 434, 828), M, 500, WHITE, "Texto", align="center")
    s.anim(b, 42, stagger=0.03, dur=0.3, order="random")
    return finish(t)


def style_y():
    """The portrait slides in from the right, a teal half follows it, a thin white frame draws round the story; a
    big see-through Y, STYLE and the small words fade in."""
    t, s = story("style-y", "Historia: STYLE con Y grande", "Story: STYLE with a big Y", 15622, 2.8,
                 ["foto", "moda", "verde azulado", "marco"])
    s.pic("Foto", "fx-face-02", (0, 0, 486, 864), off=lambda fr: (486 * (1 - ease(fr, 9, 12)), 0))
    s.rr("Panel", solid(TEAL), lambda fr: (243 + 250 * (1 - ease(fr, 18, 12)), 0, 490 + 250 * (1 - ease(fr, 18, 12)),
                                            864))
    fr0, L, b = 30, 3.0, (30, 30, 458, 836)
    p = lambda fr: ease(fr, fr0, 30)  # noqa: E731
    s.rr("Marco (arriba)", solid(WHITE), lambda fr: (b[2] - (b[2] - b[0]) * p(fr), b[1], b[2], b[1] + L))
    s.rr("Marco (izquierda)", solid(WHITE), lambda fr: (b[0], b[1], b[0] + L, b[1] + (b[3] - b[1]) * p(fr)))
    s.rr("Marco (abajo)", solid(WHITE), lambda fr: (b[0], b[3] - L, b[0] + (b[2] - b[0]) * p(fr), b[3]))
    s.rr("Marco (derecha)", solid(WHITE), lambda fr: (b[2] - L, b[3] - (b[3] - b[1]) * p(fr), b[2], b[3]))
    y = s.say_("Y", (95, 237, 395, 557), M, 600, WHITE, "Letra", align="center")
    y["opacity"] = keys([(0.0, 0.5, "hold")])
    s.anim(y, 66, preset="fade", stagger=0.0, dur=0.4)
    a = s.say_("STYLE", (143, 632, 343, 677), M, 700, WHITE, "Título", align="center")
    s.anim(a, 60, stagger=0.05, dur=0.3)
    side = s.say_("LIMITED EDITION", (-30, 140, 148, 152), M, 500, WHITE, "Texto", align="center", rot=90.0)
    s.anim(side, 66, stagger=0.03, dur=0.25)
    tags = s.para("#insta\n#fashion", (300, 770, 434, 822), PO, 17.5, WHITE, weight=500, align="right", line=1.05,
                  spacing=2.0, name="Etiquetas")
    s.anim(tags, 69, stagger=0.03, dur=0.25)
    return finish(t)


def design_passion():
    """The photo opens through horizontal slats with dark rules between them that close up; the title, a rule, two
    lines and a vertical line on the photo type in."""
    t, s = story("design-passion", "Historia: DESIGN IS MY PASSION", "Story: DESIGN IS MY PASSION", 15623, 3.0,
                 ["foto", "interior", "diseño", "persianas"])
    n, y0, y1 = 12, 290, 815
    h = (y1 - y0) / n
    first = None
    order = [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0, 11]
    for j, i in enumerate(order):
        at = 6 + j * 3
        a, b = y0 + i * h, y0 + (i + 1) * h
        win = lambda fr, a=a, b=b, at=at: (48, a, 438, a + max(0.5, (b - a + 0.6) * ease(fr, at, 18)))  # noqa: E731
        kw = {} if first is None else {"reuse": first["placeholderId"]}
        c = s.pic("Foto" if first is None else f"Foto ({j + 1})", "interior-02", (48, y0, 438, y1), win=win, **kw)
        first = first or c
        s.rr(f"Lama {j + 1}", solid("#111111"),
             lambda fr, a=a, b=b, at=at: (48, a + (b - a) * ease(fr, at, 18), 438, a + (b - a) * ease(fr, at, 18) + 10),
             op=lambda fr, at=at: ease(fr, at, 2) * (1 - ease(fr, at + 16, 6)))
    d = s.say_("DESIGN", (48, 58, 345, 108), M, 800, "#111111", "Título")
    s.anim(d, 72, stagger=0.05, dur=0.2)
    i2 = s.say_("IS", (368, 58, 438, 108), M, 400, "#111111", "Título 2")
    s.anim(i2, 84, stagger=0.05, dur=0.2)
    m = s.say_("MY PASSION", (48, 124, 438, 166), M, 400, "#111111", "Título 3")
    s.anim(m, 78, stagger=0.05, dur=0.2)
    s.rr("Raya", solid("#111111"), lambda fr: (48, 193, 48 + 388 * ease(fr, 60, 10), 199))
    for i, (w, ink) in enumerate((("THE DETAILS ARE NOT THE DETAILS,", (48, 225, 436, 240)),
                                  ("THEY MAKE THE DESIGN", (48, 251, 310, 266)))):
        c = s.say_(w, ink, M, 500, "#111111", "Texto" if i == 0 else "Texto 2")
        s.anim(c, 81 + 3 * i, stagger=0.02, dur=0.15)
    side = s.say_("LIGHT SPACE FOR CREATIVE IDEAS", (200, 577, 580, 593), M, 500, WHITE, "Texto 3", align="center",
                  rot=-90.0)
    s.anim(side, 84, stagger=0.02, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 9 (105.7 s)
# =====================================================================================================================

def enjoy_movement():
    """A dark sheet lifts away, a black band rises at the foot, the black photo panel grows out of the middle; a
    cyan tag with «enjoy» and the lines under it fade in on the white card."""
    t, s = story("enjoy-movement", "Historia: enjoy the movement", "Story: enjoy the movement", 15624, 2.2,
                 ["foto", "baile", "negro", "cian"])
    s.rr("Banda", solid("#000000"), lambda fr: (0, mix(864, 600, ease(fr, 12, 18)), 486, 864))
    s.rr("Tarjeta", solid(WHITE), lambda fr: (38, 600, 448, 826), op=lambda fr: ease(fr, 27, 3))
    sc = lambda fr: 0.35 + 0.65 * ease(fr, 27, 15)  # noqa: E731
    panel = lambda fr: (lambda q: (243 - 205 * q, 319 - 281 * q, 243 + 205 * q, 319 + 281 * q))(sc(fr))  # noqa: E731
    s.rr("Panel", solid("#000000"), panel, op=lambda fr: ease(fr, 27, 2))
    s.pic("Foto", "dance-02", (38, 38, 448, 600), win=panel, op=lambda fr: ease(fr, 27, 2))
    s.rr("Hoja", solid("#2A2A2D"), lambda fr: (0, 0, 486, mix(864, 0, ease(fr, 6, 24))))
    s.rr("Etiqueta", solid("#12B5EA"), lambda fr: (243 - 103.5 * ease(fr, 39, 8), 570, 243 + 103.5 * ease(fr, 39, 8),
                                                   635))
    a = s.say_("enjoy", (168, 585, 318, 615), PO, 700, "#111111", "Título", align="center")
    s.anim(a, 42, stagger=0.05, dur=0.25)
    b = s.say_("the movement", (145, 670, 343, 690), PO, 700, "#111111", "Texto", align="center", italic=True)
    s.anim(b, 45, stagger=0.03, dur=0.25)
    for i, (w, ink) in enumerate((("DANCE IS AN ART, PAINT", (145, 738, 341, 752)),
                                  ("YOUR DREAM AND FOLLOW IT", (120, 755, 366, 769)))):
        c = s.say_(w, ink, M, 500, "#111111", "Texto 2" if i == 0 else "Texto 3", align="center")
        s.anim(c, 51 + 3 * i, stagger=0.015, dur=0.25)
    return finish(t)


def happiness_love():
    """On gold, white lines draw the grid of a collage; four photos slide into its cells, the vertical word and LOVE
    fade in."""
    t, s = story("happiness-love", "Historia: collage HAPPINESS y LOVE", "Story: HAPPINESS and LOVE collage", 15625,
                 3.0, ["foto", "collage", "boda", "dorado"], colour="#B58E5E")
    cells = [("Foto 1", "wedding-04", (0, 0, 370, 582), (0, -600), 54),
             ("Foto 2", "flowers-02", (386, 0, 486, 312), (0, -330), 60),
             ("Foto 3", "flowers-01", (0, 598, 128, 864), (-140, 0), 66),
             ("Foto 4", "wedding-05", (144, 328, 486, 864), (0, 560), 72)]
    for name, sample, box, frm, at in cells:
        s.pic(name, sample, box, off=lambda fr, frm=frm, at=at: (frm[0] * (1 - ease(fr, at, 15)),
                                                                 frm[1] * (1 - ease(fr, at, 15))),
              win=lambda fr, box=box: box, label=name)
    # the white gaps draw themselves first (they stay as the collage's borders)
    lines = [((370, 0, 386, 582), "y", 12), ((386, 312, 486, 328), "x", 24), ((0, 582, 370, 598), "x", 30),
             ((128, 598, 144, 864), "y", 36), ((144, 328, 486, 344), "x", 42), ((370, 328, 386, 598), "y", 42)]
    for i, (r, way, at) in enumerate(lines):
        def g(fr, r=r, way=way, at=at):
            p = ease(fr, at, 15)
            if way == "y":
                return (r[0], r[1], r[2], r[1] + (r[3] - r[1]) * p)
            return (r[0], r[1], r[0] + (r[2] - r[0]) * p, r[3])
        s.rr(f"Línea {i + 1}", solid(WHITE), g)
    h = s.say_("HAPPINESS", (-38, 122, 132, 149), M, 800, WHITE, "Título", align="center", rot=-90.0)
    s.anim(h, 84, stagger=0.04, dur=0.25)
    lv = s.say_("LOVE", (330, 795, 450, 825), M, 800, WHITE, "Título 2", align="center")
    s.anim(lv, 84, stagger=0.06, dur=0.25)
    return finish(t)


def happy_weekends():
    """A white sheet peels off from the top-left corner and uncovers the dark photo; four white lines frame it, the
    yellow script and the white lines of text fade in."""
    t, s = story("happy-weekends", "Historia: Happy weekends", "Story: Happy weekends", 15626, 2.6,
                 ["foto", "flores", "fin de semana", "amarillo"])
    s.pic("Foto", "tk7-flora-11", (0, 0, 486, 864), zoom=lambda fr: 1.1 - 0.1 * ease(fr, 0, 60))
    shade = s.rr("Sombra", solid(BLACK), lambda fr: (0, 0, 486, 864), op=lambda fr: 0.25)
    shade["name"] = "Oscurecer"
    d = lambda fr: mix(-60, 1420, ease(fr, 3, 27))  # noqa: E731  the fold line x + y = d

    def sheet2(fr):
        # the sheet: everything with x + y > d, a square turned 45° whose near edge sits on the fold line
        c = d(fr)
        h = 1500.0
        off = (c + h * math.sqrt(2)) / 2
        return off, off, 2 * h, 2 * h, 45, 1.0
    s.ob("Hoja", solid(WHITE), sheet2)

    def fold(fr):
        c = d(fr)
        w = 70 * (1 - ease(fr, 22, 8))
        off = (c - w * math.sqrt(2) / 2) / 2
        return off, off, w, 3000, 45, 1.0
    s.ob("Pliegue", grad([(0.0, "#BFBFB8"), (1.0, "#F2F2EE")], angle=0), fold)
    for i, (r, way, at) in enumerate((((105, 60, 382, 64), "x", 60), ((105, 800, 382, 804), "x", 60),
                                      ((48, 100, 52, 760), "y", 63), ((434, 100, 438, 760), "y", 63))):
        def g(fr, r=r, way=way, at=at):
            p = ease(fr, at, 12)
            if way == "x":
                c = (r[0] + r[2]) / 2
                return (c - (c - r[0]) * p, r[1], c + (r[2] - c) * p, r[3])
            c = (r[1] + r[3]) / 2
            return (r[0], c - (c - r[1]) * p, r[2], c + (r[3] - c) * p)
        s.rr(f"Línea {i + 1}", solid(WHITE), g)
    for i, (w, ink, at) in enumerate((("Happy", (130, 100, 378, 150), 45), ("weekends", (125, 180, 358, 230), 51))):
        c = s.say_(w, ink, KS, 400, "#F5C518", "Título" if i == 0 else "Título 2", align="center")
        s.anim(c, at, stagger=0.06, dur=0.3)
    b = s.para("THE HAPPIEST PEOPLE\nARE NOT THOSE GETTING MORE,\nBUT THOSE GIVING MORE", (60, 274, 426, 352), M, 18.5,
               WHITE, weight=800, align="center", line=1.08, name="Texto")
    s.anim(b, 51, stagger=0.015, dur=0.25, order="random")
    c = s.para("YOUR SMILE\nMAKES ME HAPPY", (80, 700, 406, 766), M, 24, WHITE, weight=800, align="center", line=1.15,
               name="Texto 2")
    s.anim(c, 54, stagger=0.02, dur=0.25, order="random")
    return finish(t)


# =====================================================================================================================
# Trio 10 (109.7 s)
# =====================================================================================================================

def striped_circle(n=9, gap=0.45):
    """A disc (0..100 box) cut into diagonal stripes, as one path."""
    r, out, w = 50.0, [], 100.0 / n
    for i in range(n):
        a, b = -r + i * w, -r + i * w + w * (1 - gap)
        if abs(a) >= r and abs(b) >= r:
            continue
        ha, hb = math.sqrt(max(0.0, r * r - a * a)), math.sqrt(max(0.0, r * r - b * b))
        pts = []
        for u, v in ((a, -ha), (b, -hb), (b, hb), (a, ha)):
            x, y = (u - v) / math.sqrt(2), (u + v) / math.sqrt(2)
            pts.append((50 + x, 50 + y))
        out.append(poly(pts))
    return " ".join(out)


def striped_triangle(n=7, th=2.6):
    """A triangle (0..100 box, apex up) drawn as nested chevrons."""
    out = []
    for i in range(n):
        k_ = i / n
        top = 100 * k_
        lx, rx = 50 * k_, 100 - 50 * k_
        pts = [(50, top), (rx, 100 - 0), (rx - th, 100), (50, top + th * 2), (lx + th, 100), (lx, 100)]
        out.append(poly(pts))
    return " ".join(out)


def pleasure():
    """Colour blocks slide into a two-column grid on dark, the photos settle into their cells; a striped disc, a
    hash sign, a striped triangle and the words fade in."""
    t, s = story("pleasure", "Historia: collage PLEASURE en bloques", "Story: PLEASURE block collage", 15627, 2.0,
                 ["foto", "collage", "terracota", "bloques"], colour="#1E1C1C")
    BR, CR, TN = "#A0604F", "#EEDDAA", "#D08C60"
    blocks = [((243, 0, 486, 216), BR, (0, -300), 0), ((243, 216, 486, 432), CR, (300, 0), 3),
              ((0, 432, 243, 648), CR, (-300, 0), 6), ((0, 648, 243, 864), BR, (0, 300), 9),
              ((243, 648, 486, 864), TN, (300, 0), 12), ((0, 0, 243, 432), TN, (0, -450), 4),
              ((243, 432, 486, 648), BR, (0, 300), 8)]
    for i, (r, col, frm, at) in enumerate(blocks):
        s.rr(f"Bloque {i + 1}", solid(col), lambda fr, r=r, frm=frm, at=at: (
            r[0] + frm[0] * (1 - ease(fr, at, 15)), r[1] + frm[1] * (1 - ease(fr, at, 15)),
            r[2] + frm[0] * (1 - ease(fr, at, 15)), r[3] + frm[1] * (1 - ease(fr, at, 15))))
    s.pic("Foto 1", "outfit-01", (0, 0, 243, 432), off=lambda fr: (0, 432 * (1 - ease(fr, 27, 15))),
          win=lambda fr: (0, 0, 243, 432), label="Foto 1", op=lambda fr: ease(fr, 27, 2))
    s.pic("Foto 2", "spa-03", (243, 432, 486, 648), off=lambda fr: (243 * (1 - ease(fr, 30, 15)), 0),
          win=lambda fr: (243, 432, 486, 648), label="Foto 2", op=lambda fr: ease(fr, 30, 2))
    s.rr("Círculo", solid(TN), lambda fr: (lambda q: (364.5 - 80 * q, 108 - 80 * q, 364.5 + 80 * q, 108 + 80 * q))(
        ease(fr, 33, 12)), path=striped_circle())
    s.rr("Triángulo", solid(TN), lambda fr: (40, mix(830, 682, ease(fr, 36, 12)), 206, 830),
         path=striped_triangle(), op=lambda fr: ease(fr, 36, 3))
    a = s.say_("#", (318, 287, 412, 367), M, 800, TN, "Signo", align="center")
    s.anim(a, 36, preset="pop", stagger=0.0, dur=0.35)
    b = s.say_("PLEASURE", (35, 528, 207, 553), M, 800, TN, "Título", align="center")
    s.anim(b, 39, stagger=0.04, dur=0.25)
    c = s.say_("YOUR ONLY", (72, 560, 170, 572), M, 500, TN, "Texto", align="center")
    s.anim(c, 45, stagger=0.03, dur=0.25)
    for i, (w, ink) in enumerate((("IT'S THE LITTLE", (278, 738, 452, 756)), ("THINGS IN LIFE", (278, 762, 452, 780)))):
        d = s.say_(w, ink, M, 800, "#F1DBA8", "Texto 2" if i == 0 else "Texto 3", align="center")
        s.anim(d, 42 + 3 * i, stagger=0.03, dur=0.25)
    return finish(t)


def inspiration():
    """A red sheet; the dark B/W photo panel builds up from strips sliding in from both sides, white cuts open in
    the red round it; the hashtag, two lines and «inspiration» fade in."""
    t, s = story("inspiration", "Historia: #pleasure inspiration", "Story: #pleasure inspiration", 15628, 2.4,
                 ["foto", "rojo", "blanco y negro", "frase"], colour="#F43020")
    for i, (r, at) in enumerate((((0, 0, 40, 160), 33), ((447, 170, 486, 864), 36), ((200, 815, 486, 864), 39))):
        s.rr(f"Corte {i + 1}", solid(WHITE), lambda fr, r=r, at=at: (r[0], r[1], r[2],
                                                                    r[1] + (r[3] - r[1]) * ease(fr, at, 12)))
    n, first = 6, None
    for i in range(n):
        a, b = 815 * i / n, 815 * (i + 1) / n
        sgn = -1 if i % 2 else 1
        at = 3 + i * 3
        kw = {} if first is None else {"reuse": first["placeholderId"]}
        c = s.pic("Foto" if first is None else f"Foto ({i + 1})", "tk7-flora-07", (40, 0, 447, 815), look=BW,
                  win=lambda fr, a=a, b=b, sgn=sgn, at=at: (40 + sgn * 460 * (1 - ease(fr, at, 15)), a,
                                                            447 + sgn * 460 * (1 - ease(fr, at, 15)), b + 0.6), **kw)
        first = first or c
    a = s.say_("#pleasure", (182, 38, 304, 56), PO, 600, WHITE, "Etiqueta", align="center")
    s.anim(a, 42, stagger=0.04, dur=0.25)
    b = s.para("Slow down and enjoy the simple\npleasures in life", (60, 88, 426, 136), PO, 16.5, WHITE, weight=600,
               align="center", line=1.2, name="Texto")
    s.anim(b, 45, stagger=0.015, dur=0.25)
    c = s.say_("inspiration", (198, 742, 397, 768), PO, 700, WHITE, "Título", align="center")
    s.anim(c, 36, stagger=0.05, dur=0.25)
    return finish(t)


def choose_glam():
    """White slabs with red edges fly off up and to the right over the photo; a pale slanted band stays on it; the
    line on top and «48 choose the glam» fade in."""
    t, s = story("choose-glam", "Historia: 48 choose the glam", "Story: 48 choose the glam", 15629, 2.6,
                 ["foto", "belleza", "glamour", "frase"])
    s.pic("Foto", "makeup-02", (0, 0, 486, 864), zoom=lambda fr: 1.08 - 0.08 * ease(fr, 0, 60))
    band = poly([(100 * 320 / 486, 0), (100, 0), (100, 100), (100 * 170 / 486, 100)])
    s.rr("Banda", solid(WHITE), lambda fr: (0, 0, 486, 864), path=band, op=lambda fr: 0.16 * ease(fr, 24, 9))
    slabs = [(140, 300, 0), (330, 620, 4), (420, 140, 7), (80, 760, 10)]
    for i, (cx, cy, at) in enumerate(slabs):
        go = lambda fr, at=at: ease(fr, at, 18)  # noqa: E731
        s.ob(f"Losa {i + 1} (borde)", solid("#E4373A"),
             lambda fr, cx=cx, cy=cy, go=go: (cx + 700 * go(fr) - 30, cy - 1200 * go(fr) + 60, 260, 1100, 28, 1.0))
        s.ob(f"Losa {i + 1}", solid(WHITE),
             lambda fr, cx=cx, cy=cy, go=go: (cx + 700 * go(fr), cy - 1200 * go(fr), 260, 1100, 28, 1.0))
    a = s.para("glamour never takes\na day off", (22, 36, 300, 100), PO, 20, WHITE, weight=600, line=1.35,
               name="Texto")
    s.anim(a, 30, stagger=0.02, dur=0.25)
    for i, (w, ink, at) in enumerate((("48", (318, 540, 448, 610), 57), ("choose", (216, 638, 448, 680), 60),
                                      ("the", (348, 690, 448, 733), 63), ("glam", (292, 745, 448, 790), 66))):
        c = s.say_(w, ink, M, 700, WHITE, "Número" if i == 0 else f"Título {i}", align="right")
        s.anim(c, at, stagger=0.05, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 11 (113.5 s)
# =====================================================================================================================

YT_ = "Yellowtail"
font(YT_, 400, "fonts.extra/fonts/yellowtail/Yellowtail-Regular.ttf")


def interior_dream():
    """A catalogue page: olive blocks drop in, the photos open from their corners, a mustard band rises at the foot;
    the title, prices and text fade in."""
    t, s = story("interior-dream", "Historia: catálogo INTERIOR OF YOUR DREAM", "Story: INTERIOR OF YOUR DREAM catalogue",
                 15630, 2.0, ["foto", "catálogo", "interior", "precio", "tienda"])
    OL = "#6E6C58"
    s.rr("Banda", solid("#C0843A"), lambda fr: (0, mix(864, 636, ease(fr, 6, 12)), 486, 864))
    s.pic("Foto 1", "interior-03", (206, 45, 486, 443),
          win=lambda fr: (lambda p: (486 - 280 * p, 45, 486, 45 + 398 * p + 0.5))(ease(fr, 12, 18)), label="Foto 1")
    s.pic("Foto 2", "y5-cozy-06", (0, 494, 436, 846),
          win=lambda fr: (lambda p: (0, 846 - 352 * p - 0.5, 436 * p + 0.5, 846))(ease(fr, 18, 18)), label="Foto 2")
    s.rr("Barra", solid(OL), lambda fr: (0, 0, 486, 45 * ease(fr, 3, 10)))
    s.rr("Bloque", solid(OL), lambda fr: (0, 45, 206, 45 + 201 * ease(fr, 9, 12)))
    for i, (w, ink, wt) in enumerate((("INTERIOR", (32, 72, 190, 98), 400), ("OF YOUR", (32, 107, 186, 131), 400),
                                      ("DREAM", (32, 143, 188, 172), 800))):
        c = s.say_(w, ink, M, wt, WHITE, "Título" if i == 0 else f"Título {i + 1}")
        s.anim(c, 33 + 3 * i, stagger=0.04, dur=0.25)
    a = s.say_("01. bedroom table", (234, 129, 420, 145), PO, 600, WHITE, "Producto")
    s.anim(a, 42, stagger=0.02, dur=0.2)
    b = s.say_("49.-", (234, 158, 336, 192), M, 800, WHITE, "Precio")
    s.anim(b, 45, stagger=0.05, dur=0.25)
    p = s.para("Some people look\nfor a beautiful place,\nothers make a place\nbeautiful. Some people\nlook for a beautiful\n"
               "place, others make\na place beautiful. Some\npeople look for a\nbeautiful place, others\n"
               "make a place beautiful", (30, 258, 205, 452), PO, 13.4, "#111111", line=1.24, name="Texto")
    s.anim(p, 45, stagger=0.006, dur=0.2)
    c = s.say_("02. bedroom table", (32, 532, 222, 548), PO, 600, "#111111", "Producto 2")
    s.anim(c, 48, stagger=0.02, dur=0.2)
    d = s.say_("59.-", (32, 561, 132, 594), M, 800, "#111111", "Precio 2")
    s.anim(d, 51, stagger=0.05, dur=0.25)
    return finish(t)


def your_style():
    """Three framed photos pop in one after another on white; a vertical line and the script «Your style» with two
    hashtags write in."""
    t, s = story("your-style", "Historia: collage Your style", "Story: Your style collage", 15631, 3.2,
                 ["foto", "collage", "interior", "blanco"])
    shots = [("Foto 1", "interior-04", (93, 95, 372, 338), 15, 0), ("Foto 2", "interior-07", (242, 253, 453, 585), 30, 8),
             ("Foto 3", "y5-yoga-02", (32, 392, 288, 788), 27, 8)]
    for name, sample, box, at, border in shots:
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        sc = lambda fr, at=at: 0.6 + 0.4 * ease(fr, at, 12)  # noqa: E731
        if border:
            s.rr(f"{name} (marco)", solid(WHITE), lambda fr, box=box, cx=cx, cy=cy, sc=sc: (
                cx + (box[0] - border - cx) * sc(fr), cy + (box[1] - border - cy) * sc(fr),
                cx + (box[2] + border - cx) * sc(fr), cy + (box[3] + border - cy) * sc(fr)),
                op=lambda fr, at=at: ease(fr, at, 4))
        s.pic(name, sample, box, label=name, op=lambda fr, at=at: ease(fr, at, 4),
              win=lambda fr, box=box, cx=cx, cy=cy, sc=sc: (cx + (box[0] - cx) * sc(fr), cy + (box[1] - cy) * sc(fr),
                                                            cx + (box[2] - cx) * sc(fr), cy + (box[3] - cy) * sc(fr)))
    v = s.say_("lightness & freedom", (-57, 210, 187, 223), PO, 400, "#111111", "Texto", align="center", rot=-90.0)
    s.anim(v, 93, stagger=0.03, dur=0.25)
    a = s.say_("Your style", (268, 605, 452, 645), YT_, 400, "#111111", "Título", align="center")
    s.anim(a, 90, stagger=0.06, dur=0.3)
    b = s.para("#insta\n#design", (312, 664, 440, 716), PO, 19, "#111111", line=1.1, name="Etiquetas")
    s.anim(b, 96, stagger=0.03, dur=0.25)
    return finish(t)


def glam():
    """A phone camera: the B/W photo slides in over black with a shutter button below, a flash, then the shot
    shrinks into a frame on pink and GLAM rises in letter by letter."""
    t, s = story("glam", "Historia: GLAM con cámara", "Story: GLAM camera shot", 15632, 4.4,
                 ["foto", "rosa", "cámara", "blanco y negro"], colour="#000000")
    PK = "#E5A9A0"
    s.rr("Fondo rosa", solid(PK), lambda fr: (0, 0, 486, 864), op=lambda fr: ease(fr, 105, 6))
    shrink = lambda fr: ease(fr, 105, 12)  # noqa: E731

    def win(fr):
        p = shrink(fr)
        top = mix(864, 0, ease(fr, 9, 21))
        return (mix(0, 112, p), mix(top, 112, p), mix(486, 375, p), mix(740, 580, p))
    s.pic("Foto", "portrait-04", (0, 0, 486, 740), look=BW, win=win,
          zoom=lambda fr: 1.15 - 0.15 * ease(fr, 9, 60))
    s.ob("Botón", ring(WHITE, 3 * R), lambda fr: (243, 802, 40 * ease(fr, 36, 6), 40 * ease(fr, 36, 6), 0,
                                                 1 - ease(fr, 102, 4)), kind="ellipse", base=(40, 40))
    s.ob("Botón (centro)", solid(WHITE), lambda fr: (243, 802, 28 * ease(fr, 39, 6) * (1 - 0.3 * ease(fr, 72, 3) +
                                                                                       0.3 * ease(fr, 78, 3)),
                                                    28 * ease(fr, 39, 6) * (1 - 0.3 * ease(fr, 72, 3) +
                                                                            0.3 * ease(fr, 78, 3)), 0,
                                                    1 - ease(fr, 102, 4)), kind="ellipse")
    s.rr("Destello", solid(WHITE), lambda fr: (0, 0, 486, 740),
         op=lambda fr: 0.7 * ease(fr, 74, 2) * (1 - ease(fr, 77, 12)))
    g = s.say_("GLAM", (112, 600, 375, 706), OS, 600, WHITE, "Título", align="center")
    s.tint(g, 117, PK, stagger=0.06, dur=0.3, dy=20)
    h = s.say_("#INSTA", (307, 733, 375, 752), OS, 600, "#111111", "Etiqueta", align="right")
    s.anim(h, 126, stagger=0.04, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 12 (118.5 s)
# =====================================================================================================================

def cold_water():
    """A mustard block grows in from the right under the white top, two short white lines and a white band slide
    in; the photo comes in from the right inside a white frame; the title, the vertical line and the hashtag fade
    in."""
    t, s = story("cold-water", "Historia: COLD DEEP WATER", "Story: COLD DEEP WATER", 15633, 3.4,
                 ["foto", "mar", "amarillo", "verano"])
    MU = "#F2B92B"
    s.rr("Bloque", solid(MU), lambda fr: (mix(486, 0, ease(fr, 3, 12)), 150, 486, 864))
    s.rr("Banda", solid(WHITE), lambda fr: (0, 722, 486 * ease(fr, 9, 12), 792))
    s.rr("Línea", solid(WHITE), lambda fr: (0, 678, 185 * ease(fr, 12, 9), 688))
    s.rr("Línea 2", solid(WHITE), lambda fr: (200, 678, 200 + 70 * ease(fr, 15, 6), 688))
    s.pic("Foto", "y5-h-ocean-01", (126, 150, 486, 645), off=lambda fr: (380 * (1 - ease(fr, 45, 10)), 0),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 45, 40))
    p = lambda fr: ease(fr, 51, 12)  # noqa: E731
    L = 7
    s.rr("Marco (arriba)", solid(WHITE), lambda fr: (486 - 411 * p(fr), 225, 486, 225 + L))
    s.rr("Marco (izquierda)", solid(WHITE), lambda fr: (75, 225, 75 + L, 225 + 370 * p(fr)))
    s.rr("Marco (abajo)", solid(WHITE), lambda fr: (75, 595 - L, 75 + 411 * p(fr), 595))
    for i, (w, ink) in enumerate((("COLD DEEP", (57, 48, 368, 85)), ("WATER", (57, 95, 245, 132)))):
        c = s.say_(w, ink, M, 800, "#111111", "Título" if i == 0 else "Título 2")
        s.anim(c, 90 + 3 * i, stagger=0.04, dur=0.25, order="random")
    v = s.say_("HAPPINESS COMES IN WAVES", (-98, 349, 168, 362), M, 700, WHITE, "Texto", align="center", rot=-90.0)
    s.anim(v, 96, stagger=0.02, dur=0.25)
    h = s.say_("#OCEAN", (57, 742, 265, 773), PO, 400, "#111111", "Etiqueta")
    s.anim(h, 93, stagger=0.05, dur=0.25, order="random")
    return finish(t)


def dont_waste():
    """On a teal gradient a tall pointed column of the photo grows, then opens to the whole story; teal and light
    blue bars slide in and the condensed words fade in."""
    t, s = story("dont-waste", "Historia: DON'T WASTE YOUR TIME", "Story: DON'T WASTE YOUR TIME", 15634, 3.0,
                 ["foto", "frase", "verde azulado", "motivación"], colour=None)
    s.bg(layers=grad([(0.0, "#259AA6"), (1.0, "#96CBEE")], angle=90))
    hexa = poly([(50, 0), (100, 7), (100, 93), (50, 100), (0, 93), (0, 7)])

    def win(fr):
        h = 290 * ease(fr, 3, 27)
        w = mix(64, 1100, ease(fr, 51, 18))
        hh = mix(h, 1500, ease(fr, 51, 18))
        return (220 - w / 2, 330 - hh / 2, 220 + w / 2, 330 + hh / 2 + 0.5)
    s.pic("Foto", "portrait-06", (0, 0, 486, 864), win=win, path=hexa,
          zoom=lambda fr: 1.15 - 0.15 * ease(fr, 3, 70))
    bars = [((57, 0, 155, 365), "#2AA7B4", (0, -380), 60), ((348, 112, 388, 252), "#9BCBEF", (0, 160), 66),
            ((0, 537, 155, 575), "#9BCBEF", (-170, 0), 63), ((155, 830, 356, 864), "#9BCBEF", (0, 40), 69)]
    for i, (r, col, frm, at) in enumerate(bars):
        s.rr(f"Barra {i + 1}", solid(col), lambda fr, r=r, frm=frm, at=at: (
            r[0] + frm[0] * (1 - ease(fr, at, 10)), r[1] + frm[1] * (1 - ease(fr, at, 10)),
            r[2] + frm[0] * (1 - ease(fr, at, 10)), r[3] + frm[1] * (1 - ease(fr, at, 10))),
             op=lambda fr, at=at: ease(fr, at, 2))
    a = s.para("DON'T\nWASTE\nYOUR\nTIME", (55, 374, 200, 534), OS, 37, WHITE, weight=600, line=0.93, name="Título")
    s.anim(a, 75, stagger=0.06, dur=0.3, unit="word")
    b = s.para("YOUR TIME IS LIMITED\nSO DON'T WASTE IT\nLIVING SOMEONE ELSE LIFE\nBELIEVE IN YOURSELF",
               (200, 748, 413, 826), OS, 14.5, WHITE, weight=500, align="right", line=1.15, name="Texto")
    s.anim(b, 81, stagger=0.01, dur=0.25)
    return finish(t)


def relax_home():
    """Two white square outlines grow and turn into a diamond on beige; a white panel drops in with the green
    script and two lines, the photo rises under it and the diamond, now green, frames HOME."""
    t, s = story("relax-home", "Historia: Relax SWEET HOME", "Story: Relax SWEET HOME", 15635, 2.8,
                 ["foto", "hogar", "interior", "verde"], colour="#C2AE98")
    s.pic("Foto", "interior-06", (0, 432, 486, 864), win=lambda fr: (0, mix(864, 432, ease(fr, 63, 12)), 486, 864),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 63, 40))
    s.rr("Panel", solid(WHITE), lambda fr: (0, -432 * (1 - ease(fr, 42, 12)), 486, 432 - 432 * (1 - ease(fr, 42, 12))))
    for j, (dr, tilt) in enumerate(((0, 0), (12, 8))):
        def g(fr, dr=dr, tilt=tilt):
            size = mix(30, 165, ease(fr, 3, 30))
            cy = mix(432, 648, ease(fr, 42, 12))
            rot = mix(-15 + tilt, 45 + tilt * 0.4, ease(fr, 3, 40))
            return 243, cy, size, size, rot, 1.0
        s.ob(f"Rombo {j + 1}", ring(WHITE, 2 * R), lambda fr, g=g: g(fr)[:5] + (1 - ease(fr, 66, 6),), base=(165, 165))
        s.ob(f"Rombo {j + 1} (verde)", ring("#7DC242", 2.2 * R), lambda fr, g=g: g(fr)[:5] + (ease(fr, 66, 6),),
             base=(165, 165))
    a = s.say_("Relax", (100, 128, 385, 222), YT_, 400, "#77B830", "Título", align="center")
    s.anim(a, 48, stagger=0.06, dur=0.3)
    b = s.say_("SWEET HOME", (128, 263, 357, 290), M, 800, "#111111", "Título 2", align="center")
    s.anim(b, 54, stagger=0.04, dur=0.25, order="random")
    c = s.say_("warm & cozy atmosphere", (128, 315, 358, 330), PO, 500, "#111111", "Texto", align="center")
    s.anim(c, 57, stagger=0.02, dur=0.25, order="random")
    h = s.say_("HOME", (198, 638, 287, 658), M, 700, WHITE, "Etiqueta", align="center")
    s.anim(h, 72, stagger=0.05, dur=0.25)
    return finish(t)


# =====================================================================================================================
# Trio 13 (122.8 s)
# =====================================================================================================================

MUS = "#F2BB2E"


def summer_pause():
    """The photo drops in on white, mustard blocks close in above and below, a white frame draws itself on the lower
    block; the hashtag, SUMMER and «take a pause» fade in."""
    t, s = story("summer-pause", "Historia: SUMMER take a pause", "Story: SUMMER take a pause", 15636, 2.8,
                 ["foto", "verano", "vacaciones", "amarillo"])
    s.rr("Bloque", solid(MUS), lambda fr: (0, mix(864, 472, ease(fr, 12, 15)), 486, 864))
    s.rr("Bloque 2", solid(MUS), lambda fr: (0, 0, 486, 153 * ease(fr, 27, 6)))
    s.pic("Foto", "summer-01", (37, 73, 449, 441), off=lambda fr: (0, -470 * (1 - ease(fr, 3, 12))),
          zoom=lambda fr: 1.1 - 0.1 * ease(fr, 3, 40))
    p = lambda fr: ease(fr, 27, 18)  # noqa: E731
    b, L = (37, 505, 449, 835), 7
    s.rr("Marco (arriba)", solid(WHITE), lambda fr: (b[0], b[1], b[0] + (b[2] - b[0]) * p(fr), b[1] + L))
    s.rr("Marco (derecha)", solid(WHITE), lambda fr: (b[2] - L, b[1], b[2], b[1] + (b[3] - b[1]) * p(fr)))
    s.rr("Marco (abajo)", solid(WHITE), lambda fr: (b[2] - (b[2] - b[0]) * p(fr), b[3] - L, b[2], b[3]))
    s.rr("Marco (izquierda)", solid(WHITE), lambda fr: (b[0], b[3] - (b[3] - b[1]) * p(fr), b[0] + L, b[3]))
    import random as _r
    rng = _r.Random(5)
    dots = []
    for _ in range(60):
        x, y, d = rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0.25, 0.7)
        dots.append(poly([(x + d * math.cos(math.radians(a)), y + d * 0.8 * math.sin(math.radians(a)))
                          for a in range(0, 360, 60)]))
    s.rr("Motas", solid(WHITE), lambda fr: (50, 518, 436, 822), path=" ".join(dots), op=lambda fr: 0.8 * ease(fr, 60, 9))
    h = s.say_("#vacation", (150, 26, 338, 46), PO, 600, WHITE, "Etiqueta", align="center")
    s.anim(h, 69, stagger=0.04, dur=0.25)
    a = s.say_("SUMMER", (92, 625, 393, 668), M, 800, WHITE, "Título", align="center")
    s.anim(a, 66, stagger=0.05, dur=0.3)
    c = s.say_("take a pause", (190, 691, 392, 709), PO, 500, WHITE, "Texto", align="right")
    s.anim(c, 75, stagger=0.04, dur=0.25)
    return finish(t)


def amazing_now():
    """The B/W portrait comes into focus; a red block grows in from the right edge, coloured squares pop at the
    foot; the framed word, the lines and NOW fade in."""
    t, s = story("amazing-now", "Historia: AMAZING NOW", "Story: AMAZING NOW", 15637, 2.6,
                 ["foto", "blanco y negro", "rojo", "frase"], colour="#16161E")
    ph = s.pic("Foto", "fx-face-04", (0, 0, 486, 864), look=BW, zoom=lambda fr: 1.06 - 0.06 * ease(fr, 0, 50))
    s.fx(ph, "builtin.effects.gaussian_blur", animated={"u_blurRadius": lambda fr, u: 24 * (1 - ease(fr, 6, 39))})
    s.rr("Bloque", solid("#F4352D"), lambda fr: (mix(486, 253, ease(fr, 12, 39)), 466, 486, 568))
    for i, (x, col, at) in enumerate(((358, "#FFA200", 12), (128, "#6E9A26", 45), (64, "#000000", 54),
                                      (0, "#0E2463", 57))):
        s.ob(f"Cuadro {i + 1}", solid(col), lambda fr, x=x, at=at: (x + 32, 731, 64 * ease(fr, at, 6), 62 * ease(fr, at, 6),
                                                                    0, 1.0))
    s.rr("Recuadro", ring(WHITE, 3 * R), lambda fr: (242 - 107 * ease(fr, 54, 12), 68, 242 + 107 * ease(fr, 54, 12), 139),
         op=lambda fr: ease(fr, 54, 2))
    a = s.say_("AMAZING", (155, 90, 330, 117), M, 800, WHITE, "Título", align="center")
    s.anim(a, 57, stagger=0.05, dur=0.25)
    b = s.para("FELL THE FULLNESS\nOF LIFE.\nENJOY EVERY\nMOMENT", (22, 466, 240, 562), M, 18, WHITE, weight=700,
               line=1.16, name="Texto")
    s.anim(b, 60, stagger=0.015, dur=0.2)
    n = s.say_("NOW", (272, 489, 470, 545), M, 800, WHITE, "Título 2", align="center")
    s.anim(n, 57, stagger=0.06, dur=0.25)
    return finish(t)


def sunny_day():
    """On mustard a dark dot grows into a round window of the photo, which then opens into a tall frame; white and
    yellow slanted stripes slide in, an orange disc fades in with SUNNY DAY."""
    t, s = story("sunny-day", "Historia: SUNNY DAY con círculo", "Story: SUNNY DAY with a circle", 15638, 2.6,
                 ["foto", "verano", "piscina", "amarillo"], colour=MUS)
    box = (45, 45, 437, 819)
    r = lambda fr: max(0.3, 225 * ease(fr, 6, 21))  # noqa: E731
    first = s.pic("Foto", "fx-beach-03", box, kind="ellipse",
                  win=lambda fr: (243 - r(fr), 430 - r(fr), 243 + r(fr), 430 + r(fr)),
                  op=lambda fr: 1 - ease(fr, 33, 2))
    s.pic("Foto (marco)", "fx-beach-03", box, reuse=first["placeholderId"], op=lambda fr: ease(fr, 27, 3),
          win=lambda fr: (lambda p: (mix(18, 45, p), mix(205, 45, p), mix(468, 437, p), mix(655, 819, p)))(
              ease(fr, 27, 15)))
    s.ob("Punto", solid("#1F2A30"), lambda fr: (243, 430, 18 * ease(fr, 3, 4), 18 * ease(fr, 3, 4), 0,
                                               1 - ease(fr, 8, 4)), kind="ellipse")
    stripes = [(180, 125, 360, 14, WHITE, 30), (140, 200, 230, 12, MUS, 33), (243, 690, 520, 16, WHITE, 36),
               (320, 760, 300, 22, MUS, 39)]
    for i, (cx, cy, ln, th, col, at) in enumerate(stripes):
        ang = -32.0
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        g = lambda fr, cx=cx, cy=cy, ln=ln, th=th, at=at, dx=dx, dy=dy: (
            cx - dx * 600 * (1 - ease(fr, at, 12)), cy - dy * 600 * (1 - ease(fr, at, 12)), ln, th, ang, 1.0)
        s.ob(f"Raya {i + 1}", solid(col), g)
    s.ob("Disco", solid("#F2A31E"), lambda fr: (243, 430, 320 * ease(fr, 60, 12), 320 * ease(fr, 60, 12), 0, 0.78),
         kind="ellipse")
    for i, (w, ink) in enumerate((("SUNNY", (155, 405, 330, 440)), ("DAY", (195, 450, 292, 485)))):
        c = s.say_(w, ink, M, 800, WHITE, "Título" if i == 0 else "Título 2", align="center")
        s.anim(c, 69 + 3 * i, stagger=0.06, dur=0.3, order="random")
    return finish(t)


# =====================================================================================================================
# 126.8 s: B STRONG (one story alone) and 137.5 s: the first three backgrounds of «update version 02»
# =====================================================================================================================

def be_strong():
    """A pale card tumbles in over the B/W portrait and a red bar drops from the top; the photo shows through a big
    B cut in the bar; STRONG, the quote and the hashtag come in."""
    t, s = story("be-strong", "Historia: B STRONG", "Story: B STRONG", 15639, 3.0,
                 ["foto", "rojo", "frase", "motivación", "blanco y negro"], colour="#0D0D0D")
    first = s.pic("Foto", "fx-hair-05", (0, 0, 486, 864), look=BW, zoom=lambda fr: 1.08 - 0.08 * ease(fr, 0, 70))
    s.ob("Tarjeta", solid("#E6E6E6"), lambda fr: (mix(300, 210, ease(fr, 15, 12)), mix(-80, 230, ease(fr, 15, 12)),
                                                  130, 80, mix(-10, -22, ease(fr, 15, 12)),
                                                  ease(fr, 15, 2) * (1 - ease(fr, 27, 3))))
    s.rr("Barra", solid("#E1402A"), lambda fr: (119, 0, 367, 474 * ease(fr, 21, 12)))
    hole = flat_photo(s, "Foto (en la letra)", "fx-hair-05", (0, 0, 486, 864), look=BW,
                      zoom=lambda fr: 1.08 - 0.08 * ease(fr, 0, 70))
    hole["placeholderId"], hole["placeholderLabel"] = first["placeholderId"], first["placeholderLabel"]
    s.t.slots.pop()
    b = s.say_("B", (174, 51, 311, 319), AN, 400, WHITE, "Letra", align="center")
    b["opacity"] = keys([(u, round(ease(fr, 27, 4), 4), "linear") for u, fr in s.each()])
    hole["matte"] = {"clip": b["id"], "mode": "alpha"}
    a = s.say_("STRONG", (177, 380, 308, 414), OS, 600, WHITE, "Título", align="center")
    s.anim(a, 42, stagger=0.1, dur=0.15)
    p = s.para("YOU NEVER KNOW HOW\nSTRONG YOU REALLY ARE\nUNTIL BEING STRONG IS\nTHE ONLY CHOICE YOU HAVE",
               (100, 503, 386, 620), OS, 19, WHITE, weight=600, align="center", line=1.08, spacing=0.6, name="Texto")
    s.tint(p, 33, "#9A9A9A", stagger=0.004, dur=0.3, dy=10)
    h = s.say_("#CHALLENGE", (182, 789, 305, 810), OS, 600, WHITE, "Etiqueta", align="center")
    s.anim(h, 57, stagger=0.1, dur=0.12)
    return finish(t)


def background(id, es, en, order, colour, tags):
    D = 8.0
    t = tall(f"ig5-{id}", es, en, "instagram", D, order=order, tags=["instagram", "historia", "reels", "fondo"] + tags,
             thumb_at=4.0)
    s = St(t, D)
    s.frame = lambda u: u * FPS  # backgrounds keep drifting; they do not play back out
    if colour:
        s.bg(colour)
    return t, s


def cover_all(t):
    for track in t.tracks:
        for clip in track.clips:
            if clip.get("type") not in ("audio", "adjustment"):
                clip["layoutRole"] = "cover"
    return t


def ribbon(n=32, thick=26.0):
    """A wavy band rising from bottom left to top right (0..100 box)."""
    def mid(x):
        return 78 - 0.55 * x + 9 * math.sin(2 * math.pi * x / 100 + 0.6)
    top = [(100 * i / n, mid(100 * i / n) - thick / 2) for i in range(n + 1)]
    bot = [(100 * i / n, mid(100 * i / n) + thick / 2) for i in range(n, -1, -1)]
    return poly(top + bot)


def bg_waves():
    """Three wavy orange ribbons fading to purple at one end drift slowly down across a deep purple ground."""
    t, s = background("fondo-olas", "Fondo: olas naranja y morado", "Background: orange and purple waves", 15640,
                      "#3A0E5A", ["degradado", "naranja", "morado", "abstracto"])
    for i in range(4):
        y0 = -330 + i * 300

        def g(fr, y0=y0):
            u = fr / FPS
            return 243 + 10 * u, y0 + 300 + 14 * u, 760, 520, 0, 1.0
        s.ob(f"Ola {i + 1}", grad([(0.0, "#5A1060"), (0.45, "#FF3A1E"), (1.0, "#FF2E1A")], angle=0), g, path=ribbon())
    return cover_all(t)


def bg_silver():
    """Silvery ribbons, each shading from white to grey, cross the story on a slant and slide slowly along."""
    t, s = background("fondo-plata", "Fondo: rayas plateadas", "Background: silver stripes", 15641, "#9C9C9C",
                      ["plata", "gris", "rayas", "abstracto"])
    arcband = poly([(100 * i / 24, 10 + 30 * (1 - math.sin(math.pi * i / 24))) for i in range(25)] +
                   [(100 * i / 24, 70 + 30 * (1 - math.sin(math.pi * i / 24))) for i in range(24, -1, -1)])
    for i in range(12):
        cy = -120 + i * 95
        shade = [(0.0, "#8E8E8E"), (0.5, "#FAFAFA" if i % 2 else "#DADADA"), (1.0, "#8E8E8E")]

        def g(fr, cy=cy, i=i):
            u = fr / FPS
            return 243 + (6 if i % 2 else -6) * u, cy + 4 * u, 900, 70, -26.0, 1.0
        s.ob(f"Raya {i + 1}", grad(shade, angle=0), g, path=arcband)
    return cover_all(t)


def bg_red_shapes():
    """A dark red gradient; big rounded diamonds in bright red slide in from the edges with soft shadows and keep
    drifting."""
    t, s = background("fondo-rojo", "Fondo: formas rojas redondeadas", "Background: rounded red shapes", 15642,
                      None, ["rojo", "formas", "abstracto", "degradado"])
    s.bg(layers=grad([(0.0, "#B3172C"), (1.0, "#4E0A30")], angle=120))
    from templates_tit_h import shadow as tshadow
    shapes = [(470, 60, 300, (260, -120), 0), (120, 200, 330, (-360, -60), 6), (420, 480, 330, (380, 60), 12),
              (40, 700, 300, (-360, 120), 18), (460, 860, 280, (300, 220), 24)]
    for i, (cx, cy, size, frm, at) in enumerate(shapes):
        layers = [tshadow("#2A0010", -8, 10, 30, 0.55)] + grad([(0.0, "#FF2433"), (1.0, "#B3122A")], angle=135)

        def g(fr, cx=cx, cy=cy, size=size, frm=frm, at=at):
            p = ease(fr, at, 24)
            u = fr / FPS
            return cx + frm[0] * (1 - p) + 4 * u, cy + frm[1] * (1 - p) + 3 * u, size, size, 45, 1.0
        s.ob(f"Forma {i + 1}", layers, g, kind="rounded-rectangle", radius=60, base=(size, size))
    return cover_all(t)


# =====================================================================================================================
# «update version 02», 140.1–147.6 s: the other six backgrounds (three trios of three, slow drift)
# =====================================================================================================================

def radial_fill(stops, cx=0.5, cy=0.5):
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": argb(stops[0][1]),
                       "gradient": {"kind": "radial", "space": "block", "angle": 0,
                                    "stops": [{"pos": p, "color": argb(c)} for p, c in stops]}}},
            {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0,
             "paint": {"kind": "solid", "color": "#00000000"}}]


def drift(fr):
    return fr / FPS


def bg_lines_glow():
    """Pink to navy; thin cyan-green chevron lines rise in from the bottom corner, one behind the other."""
    t, s = background("fondo-lineas", "Fondo: degradado con líneas de neón", "Background: gradient with neon lines",
                      15643, None, ["degradado", "rosa", "líneas", "neón"])
    s.bg(layers=grad([(0.0, "#FF1F5A"), (0.55, "#7A1590"), (1.0, "#1A0A8C")], angle=100))
    strokes = []
    for i in range(16):
        y = 100 - i * 5.0
        strokes.append(poly([(0, y), (55, y - 18), (100, y - 2), (100, y - 3.6), (55, y - 19.6), (0, y - 1.6)]))
    s.obj("Líneas", grad([(0.0, "#24E0C0"), (1.0, "#C83CF0")], angle=0),
          lambda fr, u: (540, mix(2300, 1600, ease(fr, 9, 40)) - 6 * drift(fr), 1200, 640, 0, ease(fr, 9, 6)),
         path=" ".join(strokes))
    return cover_all(t)


def bg_grey_bubbles():
    """Black, with soft grey discs of every size floating slowly up; fainter ones behind."""
    t, s = background("fondo-burbujas-grises", "Fondo: burbujas grises sobre negro", "Background: grey bubbles on black",
                      15644, "#000000", ["negro", "gris", "círculos", "burbujas"])
    import random as _r
    rng = _r.Random(11)
    for i in range(22):
        faint = i < 8
        d = rng.uniform(140, 300) if faint else rng.uniform(60, 220)
        x, y = rng.uniform(60, 1020), rng.uniform(60, 1900)
        sp = rng.uniform(10, 26)
        layers = radial_fill([(0.0, "#3A3A3A" if faint else "#E4E4E4"), (1.0, "#262626" if faint else "#9C9C9C")])
        s.obj(f"Burbuja {i + 1}", layers, lambda fr, u, x=x, y=y, d=d, sp=sp: (x, y - sp * u, d, d, 0, 1.0),
              kind="ellipse")
    return cover_all(t)


def bg_blue_ribbon():
    """Red to violet with a broad blue ribbon curving down from the top left, swaying slowly."""
    t, s = background("fondo-cinta-azul", "Fondo: cinta azul sobre rojo", "Background: blue ribbon on red", 15645, None,
                      ["degradado", "azul", "rojo", "abstracto"])
    s.bg(layers=grad([(0.0, "#E8174F"), (1.0, "#6B1AB8")], angle=120))
    n = 16
    left = [(0 + 62 * math.sin(math.pi / 2 * i / n), 100 * (1 - math.cos(math.pi / 2 * i / n))) for i in range(n + 1)]
    right = [(34 + 66 * math.sin(math.pi / 2 * i / n), 100 * (1 - math.cos(math.pi / 2 * i / n)) * 0.85)
             for i in range(n, -1, -1)]
    band = poly(left + right)
    for j, (cols, dx) in enumerate(((("#2E6BF0", "#5A2BE0"), 0), (("#25B4F5", "#3A5BEA"), 60))):
        s.obj(f"Cinta {j + 1}", grad([(0.0, cols[0]), (1.0, cols[1])], angle=60),
              lambda fr, u, dx=dx: (640 + dx + 18 * math.sin(drift(fr) * 0.8), 960, 860, 2000,
                                3 * math.sin(drift(fr) * 0.6), 0.9 if dx else 1.0), path=band)
    return cover_all(t)


def bg_crossing_lines():
    """Magenta to violet; thin pink and cyan lines draw in and keep turning slowly across each other."""
    t, s = background("fondo-lineas-cruzadas", "Fondo: líneas cruzadas sobre magenta", "Background: crossing lines",
                      15646, None, ["degradado", "magenta", "líneas"])
    s.bg(layers=grad([(0.0, "#E8174F"), (1.0, "#5A16C8")], angle=120))
    lines = [("#FF8AD8", 300, 300, -28, 0), ("#FF8AD8", 600, 900, 62, 3), ("#4FD8F0", 450, 1300, -22, 6),
             ("#4FD8F0", 700, 1500, 70, 9)]
    for i, (col, cx, cy, ang, at) in enumerate(lines):
        s.obj(f"Línea {i + 1}", solid(col),
              lambda fr, u, cx=cx, cy=cy, ang=ang, at=at: (cx + 10 * u, cy - 6 * u, 2600 * ease(fr, at, 15), 5,
                                                           ang + 2.5 * u * (1 if i % 2 else -1), 1.0))
    return cover_all(t)


def bg_geometric():
    """Light grey with small flat bits: orange squares turned on a corner, dark slabs and triangles, dot grids and
    line hatches, popping in one after another and drifting."""
    t, s = background("fondo-geometrico", "Fondo: formas geométricas sobre gris", "Background: geometric bits on grey",
                      15647, "#DEDEDE", ["gris", "geométrico", "naranja", "minimalista"])
    OR, DK = "#FF5A3A", "#3A3A3A"
    dots = " ".join(poly([(x + 1.6 * math.cos(math.radians(a)), y + 1.6 * math.sin(math.radians(a)))
                          for a in range(0, 360, 60)]) for x in range(5, 100, 15) for y in range(5, 100, 15))
    hatch = " ".join(poly([(0, y), (100, y - 30), (100, y - 26), (0, y + 4)]) for y in range(30, 130, 12))
    bits = [("Cuadro 1", OR, 170, 400, 90, 90, 45, None, 3), ("Cuadro 2", OR, 850, 220, 80, 80, 0, None, 6),
            ("Cuadro 3", OR, 830, 1350, 100, 100, 45, None, 9), ("Losa", DK, 230, 190, 110, 40, -20, None, 4),
            ("Triángulo", DK, 960, 300, 110, 110, 0, poly([(0, 0), (100, 0), (100, 100)]), 7),
            ("Triángulo 2", DK, 270, 1700, 140, 220, 0, poly([(100, 0), (100, 100), (0, 100), (0, 40)]), 10),
            ("Puntos", DK, 360, 260, 160, 130, 0, dots, 5), ("Puntos 2", DK, 900, 820, 200, 260, 45, dots, 8),
            ("Puntos 3", DK, 880, 1650, 170, 140, 0, dots, 11), ("Rayas", DK, 260, 1430, 170, 220, 0, hatch, 12),
            ("Rayas 2", DK, 870, 90, 140, 80, 0, poly([(0, 0), (100, 0), (100, 6), (0, 6)]) + " " +
             " ".join(poly([(0, y), (100, y), (100, y + 6), (0, y + 6)]) for y in range(16, 100, 16)), 6)]
    for name, col, cx, cy, w, h, rot, path, at in bits:
        s.obj(name, solid(col), lambda fr, u, cx=cx, cy=cy, w=w, h=h, rot=rot, at=at: (
            cx + 5 * u, cy - 8 * u, w * ease(fr, at, 8), h * ease(fr, at, 8), rot, 1.0), path=path)
    return cover_all(t)


def bg_chevrons():
    """Red chevrons pointing down drop in from the top one after another, each over the last with a soft shadow."""
    t, s = background("fondo-chevrones", "Fondo: chevrones rojos", "Background: red chevrons", 15648, None,
                      ["rojo", "chevrones", "abstracto"])
    s.bg(layers=grad([(0.0, "#8E0F25"), (1.0, "#D81A2C")], angle=0))
    from templates_tit_h import shadow as tshadow
    chev = poly([(0, 0), (50, 45), (100, 0), (100, 55), (50, 100), (0, 55)])
    for i in range(9):
        y = -200 + i * 270
        layers = [tshadow("#3A0010", 0, 18, 30, 0.5)] + grad([(0.0, "#FF2A3A"), (1.0, "#D8162C")], angle=0)
        s.obj(f"Chevrón {i + 1}", layers, lambda fr, u, y=y, i=i: (540, mix(y - 900, y, ease(fr, i * 2, 14)) + 8 * u,
                                                                   1300, 560, 0, 1.0), path=chev)
    return cover_all(t)


def bg_pills():
    """Pastel pink to plum; rounded pills shading from white to pink slide in on a slant and keep drifting."""
    t, s = background("fondo-pildoras", "Fondo: píldoras rosas en diagonal", "Background: pink pills", 15649, None,
                      ["rosa", "pastel", "formas", "abstracto"])
    s.bg(layers=grad([(0.0, "#FDE3F2"), (1.0, "#9E1E66")], angle=90))
    import random as _r
    rng = _r.Random(4)
    for i in range(14):
        cx, cy = rng.uniform(-50, 1130), rng.uniform(-50, 1970)
        ln, th = rng.uniform(260, 520), rng.uniform(90, 140)
        warm = i % 3 == 0
        cols = ("#FFFFFF", "#FF3C6E") if warm else ("#FFFFFF", "#F2A6C8")
        at = rng.uniform(4, 14)
        s.obj(f"Píldora {i + 1}", grad([(0.0, cols[0]), (1.0, cols[1])], angle=45),
              lambda fr, u, cx=cx, cy=cy, ln=ln, th=th, at=at: (
                  cx + 700 * (1 - ease(fr, at, 12)) - 10 * u, cy - 700 * (1 - ease(fr, at, 12)) + 10 * u, ln, th,
                  45, 1.0), kind="rounded-rectangle", radius=th / 2, base=(ln, th))
    return cover_all(t)


def bg_blue_bubbles():
    """Pink to lilac; glossy blue spheres and thin white rings rise from the bottom and float."""
    t, s = background("fondo-burbujas-azules", "Fondo: burbujas azules sobre rosa", "Background: blue bubbles on pink",
                      15650, None, ["rosa", "azul", "burbujas", "abstracto"])
    s.bg(layers=grad([(0.0, "#FF5E8A"), (1.0, "#D9CBFF")], angle=90))
    balls = [(130, 1650, 300), (820, 1780, 360), (400, 1500, 140), (760, 620, 200), (900, 540, 120), (300, 900, 110),
             (560, 1220, 90), (950, 1100, 70), (200, 380, 60), (640, 300, 70)]
    for i, (cx, cy, d) in enumerate(balls):
        at = 4 + (i % 5) * 2
        s.obj(f"Burbuja {i + 1}", radial_fill([(0.0, "#2EC4FF"), (1.0, "#1240E0")], 0.35, 0.3),
              lambda fr, u, cx=cx, cy=cy, d=d, at=at: (cx + 8 * math.sin(u + cx), cy + 900 * (1 - ease(fr, at, 15))
                                                        - 14 * u, d, d, 0, 1.0), kind="ellipse")
    for i, (cx, cy, d) in enumerate(((560, 1450, 420), (900, 720, 300))):
        s.obj(f"Aro {i + 1}", ring(WHITE, 4), lambda fr, u, cx=cx, cy=cy, d=d: (
            cx, cy + 900 * (1 - ease(fr, 8, 15)) - 10 * u, d, d * 0.8, -20, 0.9), kind="ellipse", base=(d, d * 0.8))
    return cover_all(t)


def bg_amber_circles():
    """Amber light in a corner fading to dark brown; big overlapping discs edged in shade slide in from the
    sides."""
    t, s = background("fondo-ambar", "Fondo: círculos ámbar", "Background: amber circles", 15651, None,
                      ["naranja", "marrón", "círculos", "abstracto"])
    s.bg(layers=radial_fill([(0.0, "#FFB000"), (0.55, "#B55A00"), (1.0, "#3E1200")]))
    from templates_tit_h import shadow as tshadow
    discs = [(-120, 420, 900, (-600, 0), 4), (1150, 1300, 1000, (700, 0), 6), (-200, 1750, 800, (-600, 200), 8)]
    for i, (cx, cy, d, frm, at) in enumerate(discs):
        layers = [tshadow("#2A0A00", 14, 10, 50, 0.6)] + radial_fill([(0.0, "#F0A000"), (1.0, "#7A3400")])
        s.obj(f"Círculo {i + 1}", layers, lambda fr, u, cx=cx, cy=cy, d=d, frm=frm, at=at: (
            cx + frm[0] * (1 - ease(fr, at, 15)) + 4 * u, cy + frm[1] * (1 - ease(fr, at, 15)) - 3 * u, d, d, 0, 1.0),
            kind="ellipse")
    return cover_all(t)


# =====================================================================================================================
# «update version 02», 147.6–154.5 s: twelve titles on black (two trios of six), here as titles over the user's
# video (no background of their own), the element in the middle of the story, ×1.9 of the reference cell.
# =====================================================================================================================

from scene import fill as sfill, text_style  # noqa: E402

PM = "Permanent Marker"
LO = "Lora"
font(PM, 400, "fonts.basic/fonts/permanentmarker/PermanentMarker-Regular.ttf")
font(LO, 400, "fonts.basic/fonts/lora/Lora-Regular.ttf")
font(LO, 700, "fonts.basic/fonts/lora/Lora-Bold.ttf")
CX, CY = 540, 960


def title(id, es, en, order, entrance, tags=()):
    D = dur_for(entrance, 2.2)
    t = tall(f"ig5-{id}", es, en, "instagram", D, order=order,
             tags=["instagram", "historia", "reels", "título", "texto"] + list(tags),
             thumb_at=round(entrance + 1.2, 1))
    return t, St(t, D)


def brush(n=18, seed=3, rough=7.0):
    """A dry-brush stroke (0..100 box): ragged ends and a few streaks."""
    import random as _r
    rng = _r.Random(seed)
    top = [(100 * i / n, rng.uniform(0, rough)) for i in range(n + 1)]
    right = [(100 - rng.uniform(0, 9), 100 * j / 8) for j in range(1, 8)]
    bot = [(100 * i / n, 100 - rng.uniform(0, rough)) for i in range(n, -1, -1)]
    left = [(rng.uniform(0, 9), 100 - 100 * j / 8) for j in range(1, 8)]
    out = [poly(top + right + bot + left)]
    for _ in range(4):
        y = rng.uniform(8, 92)
        x0 = rng.uniform(-8, 0)
        out.append(poly([(x0 - 6, y), (8, y - 1.5), (8, y + 1.5)]))
    return " ".join(out)


def big_sale():
    """A pink dry-brush stroke sweeps in, a white cart pops on it and BIG SALE types in (the reference's BLACK
    FRIDAY, made neutral)."""
    t, s = title("titulo-big-sale", "Título: BIG SALE con brocha y carrito", "Title: BIG SALE brush and cart", 15652,
                 1.0, ["rebajas", "brocha", "compras"])
    s.rect("Brocha", solid("#FF2D55"), lambda fr, u: (90, 840, 90 + 900 * ease(fr, 0, 9), 1080), path=brush())
    cart = ("M 0 8 L 14 8 L 22 62 L 86 62 L 96 22 L 22 22 L 20 16 L 92 16 L 100 16 L 88 70 L 18 70 L 8 14 L 0 14 Z "
            "M 26 34 L 90 34 L 90 37 L 26 37 Z M 28 48 L 86 48 L 86 51 L 28 51 Z "
            "M 30 78 L 42 78 L 42 92 L 30 92 Z M 70 78 L 82 78 L 82 92 L 70 92 Z")
    s.obj("Carrito", solid(WHITE), lambda fr, u: (310, 958, 150 * ease(fr, 9, 6), 130 * ease(fr, 9, 6), 0, 1.0),
          path=cart)
    for i, (w, ink) in enumerate((("BIG", (420, 885, 640, 945)), ("SALE", (420, 970, 690, 1030)))):
        c = s.say(w, ink, M, 900, "#111111", "Título" if i == 0 else "Título 2", align="left")
        s.anim(c, 9 + 3 * i, stagger=0.05, dur=0.15)
    return finish(t)


def abstract_shapes():
    """A coral blob pops up with a yellow edge and a violet one behind it, a few dots spark round it; the three
    words come in letter by letter."""
    t, s = title("titulo-formas-abstractas", "Título: ABSTRACT SHAPES DESIGN", "Title: ABSTRACT SHAPES DESIGN", 15653,
                 1.0, ["formas", "coral", "diseño"])
    blob = ("M 6 22 C 6 4 30 2 50 3 C 74 2 96 4 96 24 C 98 46 98 62 95 80 C 92 97 70 98 50 97 C 28 98 6 98 4 78 "
            "C 2 60 4 40 6 22 Z")
    for name, col, dx, dy, at in (("Forma (violeta)", "#5A5CFF", 22, -14, 3), ("Forma (amarilla)", "#FFD23F", -14, 14, 2),
                                   ("Forma", "#FF5F55", 0, 0, 0)):
        s.obj(name, solid(col), lambda fr, u, dx=dx, dy=dy, at=at: (
            CX + dx * ease(fr, at + 3, 6), CY + dy * ease(fr, at + 3, 6), 520 * ease(fr, at, 7), 330 * ease(fr, at, 7),
            0, 1.0), path=blob, base=(520, 330))
    for i, (x, y, d, col) in enumerate(((250, 790, 12, "#FF5FB0"), (275, 810, 8, "#5A5CFF"), (815, 1140, 10, "#FF5FB0"),
                                        (835, 1118, 7, "#FFD23F"))):
        s.obj(f"Punto {i + 1}", solid(col), lambda fr, u, x=x, y=y, d=d: (x, y, d * ease(fr, 12, 5), d * ease(fr, 12, 5),
                                                                          0, 1.0), kind="ellipse")
    for i, (w, ink, wt) in enumerate((("ABSTRACT", (420, 880, 660, 910), 400), ("SHAPES", (400, 935, 680, 975), 800),
                                      ("DESIGN", (420, 998, 660, 1036), 400))):
        c = s.say(w, ink, M, wt, WHITE, f"Título {i + 1}" if i else "Título", align="center")
        s.anim(c, 6 + 3 * i, stagger=0.04, dur=0.2, order="random")
    return finish(t)


def bold_fashion():
    """Three stacked words on a slant slide in along it, the middle one in blue; violet and blue strokes shoot in
    above and below."""
    t, s = title("titulo-bold-fashion", "Título: BOLD FASHION STYLE inclinado", "Title: slanted BOLD FASHION STYLE",
                 15654, 1.0, ["moda", "inclinado", "azul"])
    ang = -30.0
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -dy, dx
    rows = [("BOLD", "#D8D8D8", -120, -240, 3), ("FASHION", "#23C5F0", 0, 0, 6), ("STYLE", "#D8D8D8", 120, 240, 9)]
    for i, (w, col, off, slide, at) in enumerate(rows):
        cx, cy = CX + nx * off * 0.0 + dx * 0, CY + off
        c = s.say(w, (cx - 230, cy - 45, cx + 230, cy + 45), M, 801 if w == "FASHION" else 900, col,
                  "Título" if i == 0 else f"Título {i + 1}", align="center",
                  geom=lambda fr, u, slide=slide, at=at: (dx * slide * (1 - ease(fr, at, 9)),
                                                          dy * slide * (1 - ease(fr, at, 9)), 1, ang, ease(fr, at, 4)))
    for i, (ox, oy, ln, col, at) in enumerate(((-70, -170, 300, "#7B5CFF", 0), (130, 170, 380, "#4A6BFF", 2),
                                               (200, 210, 160, "#23C5F0", 4))):
        s.obj(f"Trazo {i + 1}", grad([(0.0, col), (1.0, "#C04CFF")], angle=0),
              lambda fr, u, ox=ox, oy=oy, ln=ln, at=at: (CX + ox - dx * 500 * (1 - ease(fr, at, 9)),
                                                         CY + oy - dy * 500 * (1 - ease(fr, at, 9)), ln, 16, ang, 1.0),
              kind="rounded-rectangle", radius=8, base=(ln, 16))
    return finish(t)


def neon_style():
    """A pink neon frame flickers on, NEON lights up in orange and a cyan script word swings in under it."""
    t, s = title("titulo-neon", "Título: NEON con brillo", "Title: glowing NEON", 15655, 1.4, ["neón", "brillo", "rosa"])
    from scene import glow
    flick = lambda fr, at: (0.0 if fr < at else 1.0 if fr > at + 10 else (0.25, 1.0, 0.1, 0.8, 0.3, 1.0, 0.6, 1.0, 0.9,
                                                                            1.0, 1.0)[int(fr - at)])  # noqa: E731
    s.obj("Marco", [glow("#FF2BD6", 26, 0.9), {"id": "fill", "kind": "fill", "enabled": False,
                                                "paint": {"kind": "solid", "color": "#00000000"}},
                    {"id": "stroke", "kind": "stroke", "enabled": True, "width": 12, "strokeAlign": "center",
                     "opacity": 1.0, "paint": {"kind": "solid", "color": "#ffff4fe0"}}],
          lambda fr, u: (CX, CY, 620, 270, 0, flick(fr, 2)), kind="rounded-rectangle", radius=40, base=(620, 270))
    n = s.say("NEON", (310, 890, 770, 1010), M, 800, "#FFC24A", "Título", align="center",
              layers=[glow("#FF7A1A", 24, 0.95), {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                                   "paint": {"kind": "solid", "color": "#ffffc860"}}],
              op=lambda fr, u: flick(fr, 12))
    st = s.say("Style", (450, 1010, 640, 1080), KS, 400, "#2BF0E0", "Texto", align="center",
               layers=[glow("#18D8E0", 18, 0.9), {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                                   "paint": {"kind": "solid", "color": "#ff7ff8f0"}}],
               rot=lambda fr, u: -12.0)
    s.anim(st, 30, preset="typewriter", stagger=0.08, dur=0.05)
    return finish(t)


def art_design_forum():
    """Colour blocks wipe across and leave three stacked words: ART& in yellow and pink, DESIGN in white and FORUM
    white on a blue band."""
    t, s = title("titulo-art-design", "Título: ART & DESIGN FORUM", "Title: ART & DESIGN FORUM", 15656, 1.1,
                 ["arte", "diseño", "amarillo", "azul"])
    s.rect("Banda", solid("#1A3CFF"), lambda fr, u: (300, 1035, 300 + 480 * ease(fr, 12, 9), 1110))
    wipe = lambda fr, at: (300 + 480 * ease(fr, at, 6), 300 + 480 * ease(fr, at + 6, 6))  # noqa: E731
    for i, (y0, y1, col, at) in enumerate(((810, 890, "#FF2BB0", 3), (900, 975, WHITE, 6), (1035, 1110, WHITE, 12))):
        s.rect(f"Barrido {i + 1}", solid(col), lambda fr, u, y0=y0, y1=y1, at=at: (wipe(fr, at)[1], y0, wipe(fr, at)[0],
                                                                                   y1))
    a = s.say("ART&", (300, 815, 600, 885), M, 900, "#FFD200", "Título", align="left",
              reveal=lambda fr: (300, 780, 300 + 480 * ease(fr, 3, 6), 900))
    b = s.say("DESIGN", (300, 905, 780, 970), M, 900, WHITE, "Título 2", align="left",
              reveal=lambda fr: (300, 895, 300 + 480 * ease(fr, 6, 6), 985))
    c = s.say("FORUM", (300, 1040, 780, 1105), M, 900, WHITE, "Título 3", align="left",
              reveal=lambda fr: (300, 1030, 300 + 480 * ease(fr, 15, 6), 1115))
    return finish(t)


def retro_style():
    """A neon pink triangle outline, chrome RETROSTYLE and a cyan script word over a purple floor grid that fades
    in."""
    t, s = title("titulo-retro", "Título: RETROSTYLE años 80", "Title: 80s RETROSTYLE", 15657, 1.2,
                 ["retro", "80", "neón", "cromado"])
    from scene import glow
    tri = "M 0 0 L 100 0 L 50 100 Z M 8 5 L 50 90 L 92 5 Z"
    s.obj("Triángulo", [glow("#FF2B8A", 18, 0.8), {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                                     "paint": {"kind": "solid", "color": "#ffff2b8a"}}],
          lambda fr, u: (CX, 960, 360 * ease(fr, 6, 9), 300 * ease(fr, 6, 9), 0, 1.0), path=tri, base=(360, 300))
    grid = " ".join(poly([(50 + (x - 50) * 0.4, 0), (50 + (x - 50) * 0.4 + 0.6, 0), (x + 0.8, 100), (x, 100)])
                    for x in range(0, 101, 10))
    grid += " " + " ".join(poly([(0, y), (100, y), (100, y + 1.5), (0, y + 1.5)]) for y in (20, 42, 66, 92))
    s.obj("Suelo", solid("#9A3CFF"), lambda fr, u: (CX, 1050, 640, 120, 0, 0.7 * ease(fr, 0, 12)), path=grid)
    chrome = [gradient([(0.0, "#FFFFFF"), (0.45, "#F2B8FF"), (0.52, "#7A2B9A"), (0.75, "#FF6AD8"), (1.0, "#FFFFFF")],
                       angle=90), no_stroke()]
    r = s.say("RETROSTYLE", (290, 905, 790, 985), OS, 700, WHITE, "Título", align="center", layers=chrome)
    s.anim(r, 3, preset="fade", stagger=0.0, dur=0.3)
    d = s.say("Design", (520, 990, 690, 1045), KS, 400, "#2BF0E0", "Texto", align="center",
              layers=[glow("#18D8E0", 14, 0.9), {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                                                  "paint": {"kind": "solid", "color": "#ff7ff8f0"}}],
              rot=lambda fr, u: -10.0)
    s.anim(d, 21, preset="typewriter", stagger=0.07, dur=0.05)
    return finish(t)


def sale_ticket():
    """A pale strip peels off a red ticket with zigzag ends and leaves SALE in yellow."""
    t, s = title("titulo-sale", "Título: SALE en etiqueta", "Title: SALE ticket", 15658, 1.0, ["rebajas", "rojo",
                                                                                                  "amarillo"])
    zig = poly([(0, 0), (100, 0)] + [(100 - (4 if j % 2 else 0), 100 * j / 10) for j in range(1, 10)] +
               [(100, 100), (0, 100)] + [((4 if j % 2 else 0), 100 - 100 * j / 10) for j in range(1, 10)])
    s.rect("Etiqueta", solid("#E8162A"), lambda fr, u: (310, 890, 770, 1030), path=zig)
    c = s.say("SALE", (345, 912, 735, 1008), M, 900, "#FFD21E", "Título", align="center")
    c["opacity"] = keys([(0.0, 1.0, "hold")])
    edge = lambda fr: mix(310, 790, ease(fr, 2, 24))  # noqa: E731
    s.rect("Tira", solid("#EDEDED"), lambda fr, u: (edge(fr), 880, 790, 1040), op=lambda fr, u: 1 - ease(fr, 25, 2))
    s.obj("Tira (pliegue)", grad([(0.0, "#BDBDBD"), (1.0, "#FFFFFF")], angle=0),
          lambda fr, u: (edge(fr) + 22, 945, 48, 190 * (1 - ease(fr, 22, 5)), -8, 1 - ease(fr, 25, 2)))
    return finish(t)


def bubblegum():
    """Pink condensed words with a yellow edge pop up tilted, and little yellow and pink dashes burst round them."""
    t, s = title("titulo-chicle", "Título: BUBBLEGUM STYLE", "Title: BUBBLEGUM STYLE", 15659, 1.0,
                 ["rosa", "amarillo", "divertido"])
    edge = [{"id": "shadow", "kind": "shadow", "enabled": True, "paint": {"kind": "solid", "color": "#ffffd23f"},
             "offsetX": 5, "offsetY": 5, "blur": 0, "opacity": 1.0},
            {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "solid", "color": "#ffff4fb8"}}]
    for i, (w, ink, at) in enumerate((("BUBBLEGUM", (330, 870, 750, 950), 0), ("STYLE", (440, 965, 640, 1045), 3))):
        c = s.say(w, ink, OS, 500, "#FF4FB8", "Título" if i == 0 else "Título 2", align="center", layers=edge,
                  rot=lambda fr, u: -9.0)
        s.anim(c, at, preset="pop", stagger=0.03, dur=0.25)
    for i in range(12):
        a = math.radians(i * 30 + 10)
        rx, ry = 300, 170
        col = "#FFD23F" if i % 2 else "#FF4FB8"
        s.obj(f"Chispa {i + 1}", solid(col), lambda fr, u, a=a, col=col: (
            CX + math.cos(a) * rx * mix(0.7, 1.0, ease(fr, 9, 9)), CY + math.sin(a) * ry * mix(0.7, 1.0, ease(fr, 9, 9)),
            34, 6, math.degrees(a), ease(fr, 9, 3)))
    return finish(t)


def quote_card():
    """A three-line quote in serif types in between two large quotation marks, a small tag with the author's name
    slides in under it."""
    t, s = title("titulo-cita", "Título: cita con autor", "Title: quote with author", 15660, 1.6,
                 ["cita", "frase", "elegante"])
    q = s.t.text(s.t.track("text", "Cita"), "There are only two ways to live your life.\nOne is as though nothing is a "
                 "miracle.\nThe other is as though everything is a miracle.", 0.0, s.dur, Box(110, 850, 860, 190),
                 text_style(LO, 33, [sfill(WHITE)], weight=400, align="left", line=1.25),
                 label="Cita")
    s.anim(q, 3, stagger=0.012, dur=0.25, order="random")
    for i, (txt, x, y, at) in enumerate((("“", 70, 820, 0), ("”", 960, 1040, 6))):
        c = s.say(txt, (x, y, x + 40, y + 40), LO, 700, "#E07A3C", f"Comilla {i + 1}", align="center")
        s.anim(c, at, preset="pop", stagger=0.0, dur=0.3)
    s.rect("Etiqueta", solid("#C8875A"), lambda fr, u: (950 - 240 * ease(fr, 30, 9), 1050, 950, 1096))
    n = s.say("Alex Morgan", (730, 1062, 930, 1084), LO, 700, WHITE, "Autor", align="center")
    s.anim(n, 36, stagger=0.03, dur=0.2)
    return finish(t)


def glitch_style():
    """Two white words jolt in with colour split and jumping letters, then settle."""
    t, s = title("titulo-glitch", "Título: GLITCH STYLE", "Title: GLITCH STYLE", 15661, 1.2, ["glitch", "blanco",
                                                                                                "digital"])
    for i, (w, ink, at) in enumerate((("GLITCH", (330, 880, 750, 955), 0), ("STYLE", (360, 970, 720, 1045), 3))):
        c = s.say(w, ink, M, 900, WHITE, "Título" if i == 0 else "Título 2", align="center",
                  geom=lambda fr, u, at=at: ((18 * math.sin(fr * 2.7 + at) if fr < at + 30 else 0.0), 0, 1, 0,
                                             ease(fr, at, 2)))
        s.fx(c, "rgb_split", animated={"amount": lambda fr, u, at=at: 22 * (1 - ease(fr, at, 30)) *
                                       abs(math.sin(fr * 1.3))})
        s.anim(c, at, preset="fade", stagger=0.04, dur=0.08, order="random")
    return finish(t)


def never_give_up():
    """A red brush stroke slashes across on a slant and two hand-written lines write on it."""
    t, s = title("titulo-never-give-up", "Título: NEVER GIVE UP con brocha", "Title: NEVER GIVE UP brush", 15662, 1.0,
                 ["motivación", "brocha", "rojo"])
    s.obj("Brocha", solid("#F0202A"), lambda fr, u: (CX - 230 * (1 - ease(fr, 0, 7)), CY, 600 * ease(fr, 0, 7), 210,
                                                     -16, 1.0), path=brush(seed=8), base=(600, 210))
    for i, (w, ink, at) in enumerate((("NEVER", (330, 880, 600, 950), 6), ("GIVE UP", (420, 960, 760, 1040), 12))):
        c = s.say(w, ink, PM, 400, WHITE, "Título" if i == 0 else "Título 2", align="center", rot=lambda fr, u: -16.0)
        s.anim(c, at, preset="typewriter", stagger=0.06, dur=0.05)
    return finish(t)


def do_what():
    """DO WHAT types in in amber; a violet-to-pink band sweeps in under it with YOU WANT."""
    t, s = title("titulo-do-what", "Título: DO WHAT YOU WANT", "Title: DO WHAT YOU WANT", 15663, 1.0,
                 ["motivación", "violeta", "amarillo"])
    a = s.say("DO WHAT", (300, 880, 780, 950), M, 900, "#FFB000", "Título", align="center")
    s.anim(a, 6, preset="fade", stagger=0.05, dur=0.1)
    s.rect("Banda", grad([(0.0, "#7B2BFF"), (1.0, "#FF2B9A")], angle=0),
           lambda fr, u: (300, 965, 300 + 480 * ease(fr, 9, 8), 1045))
    b = s.say("YOU WANT", (325, 975, 755, 1035), M, 900, WHITE, "Título 2", align="center")
    s.anim(b, 12, preset="fade", stagger=0.05, dur=0.1)
    return finish(t)

TEMPLATES = [wake_up, flexible_body, modern_office, keep_simple, sale_70, creative_studio, mindfulness, ocean,
             look_deep, gentle_soft, power, light_easy, daring_style, dancing, beach_therapy, sensual, denim_style,
             beauty_pro, awesome, focus_breathe, your_choice, best_look, style_y, design_passion, enjoy_movement,
             happiness_love, happy_weekends, pleasure, inspiration, choose_glam, interior_dream, your_style, glam,
             cold_water, dont_waste, relax_home, summer_pause, amazing_now, sunny_day, be_strong, bg_waves,
             bg_silver, bg_red_shapes, bg_lines_glow, bg_grey_bubbles, bg_blue_ribbon, bg_crossing_lines,
             bg_geometric, bg_chevrons, bg_pills, bg_blue_bubbles, bg_amber_circles, big_sale, abstract_shapes,
             bold_fashion, neon_style, art_design_forum, retro_style, sale_ticket, bubblegum, quote_card,
             glitch_style, never_give_up, do_what]
