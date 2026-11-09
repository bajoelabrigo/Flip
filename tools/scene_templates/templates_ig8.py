"""INSTAGRAM folder video 38567689.mp4 as Stock templates (ig8-*). See docs/plan-instagram.md.

«5 Urban stories» (1920×1080 at 25 fps, 24 s): five blue / mint stories shown side by side (screens of 302×537 at
x 109 / 459 / 809 / 1159 / 1509, y 271) from 6.5 s to 14 s. Each story is laid out flat on 1080×1920 (×3.576 from
the screen) and its moves copied from 10 fps sheets of each screen (sheet index i = 0.1 s, from 6.4 s): the
entrance, the photo swap at ~3 s (the same move again with the next photo) and the words leaving at ~5.5 s, where the
reference starts its second set of words (the same five designs). The tilted-phones cover, the «5 URBAN STORIES»
cards and the «Add Photo / Edit Text / Change Color / Enjoy It!» tutorial are skipped. Photos are slots.
Kit de Instagram; ids `ig8-*`, order 16100-. Study notes in tienda/plantillas/estudio-38567689/NOTAS.md.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from scene import keys
from templates_ig1 import Story, finish
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_f import outline_layers
from templates_tit_h import poly, ring
from kit import tall

W, H = 1080, 1920
WHITE = "#FFFFFF"
BLUE, MINT = "#03477E", "#64E3C6"
POP = "Poppins"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold")):
    f6._FILES[(POP, _w)] = f"fonts.basic/fonts/poppins/Poppins-{_f}.ttf"

TRI = "M 0 0 L 100 50 L 0 100 Z"


def lerp(a, b, t):
    return a + (b - a) * t


def back(p, s=1.6):
    """Ease out with a small overshoot (0 → 1)."""
    p = max(0.0, min(1.0, p))
    q = p - 1
    return 1 + (s + 1) * q ** 3 + s * q ** 2


def lin(fr, at, n):
    return max(0.0, min(1.0, (fr - at) / max(1e-6, n)))


def wave_path(periods=3.0, amp=40.0, steps=60, phase=0.0):
    """A sine line across a 0..100 box (amp in % of the box height around the middle)."""
    pts = [(100 * i / steps, 50 + amp * math.sin(phase + 2 * math.pi * periods * i / steps)) for i in range(steps + 1)]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def wave_fill(periods=2.0, amp=18.0, steps=60):
    """A band whose top edge is a sine wave (0..100 box)."""
    pts = [(100 * i / steps, amp + amp * math.sin(2 * math.pi * periods * i / steps)) for i in range(steps + 1)]
    return poly(pts + [(100, 100), (0, 100)])


def hatch(n=40, slant=8.0, width=1.4):
    """Thin diagonal stripes across a 0..100 box."""
    out = []
    for i in range(-3, n + 3):
        x = 100 * i / n
        out.append(poly([(x, 0), (x + width, 0), (x + width - slant, 100), (x - slant, 100)]))
    return " ".join(out)


class Urban(Story):
    """A story whose frames run straight on (no mirrored exit): the leave is drawn by hand as in the reference."""

    def frame(self, u):
        return u * FPS

    def card(self, name, sample, inner, at, n=21, border=0.0, start_border=30.0, label=None, rot0=-22.0,
             photo_at=None):
        """A white card that spins in from nothing with the photo slot inside (the swap move of these stories):
        inner = the photo's final rect; border = the card's final white edge."""
        x0, y0, x1, y1 = inner
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        pa = at + 3 if photo_at is None else photo_at

        def p(fr):
            return back(lin(fr, at, n), 1.1)

        def rot(fr):
            return rot0 * (1 - k(fr, at, n))

        def bw(fr):
            return lerp(start_border, border, k(fr, at + n * 0.5, n * 0.5))

        self.obj(f"{name} (marco)", solid(WHITE),
                 lambda fr, u: (cx, cy, (w + 2 * bw(fr)) * max(1e-3, p(fr)), (h + 2 * bw(fr)) * max(1e-3, p(fr)),
                                rot(fr), 1.0 if fr >= at else 0.0))
        return self.pic(name, sample, inner, geom=lambda fr, u: (0.0, 0.0, max(1e-3, p(fr) * lerp(0.4, 1.0, k(fr, pa, n * 0.6)))),
                        rot=lambda fr, u: rot(fr), op=lambda fr, u: 1.0 if fr >= pa else 0.0, label=label)

    def slide(self, content, ink, colour, name, enter=None, leave=None, family=POP, weight=800, layers=None,
              extra=None):
        """A word that whips in from (dx, dy, at, n) = enter and out to leave (same form); extra(fr) = (dx, dy)."""
        def g(fr, u):
            dx, dy = extra(fr) if extra else (0.0, 0.0)
            if enter:
                ex, ey, a, n = enter
                q = 1 - back(lin(fr, a, n), 0.8)
                dx, dy = dx + ex * q, dy + ey * q
            if leave:
                lx, ly, a, n = leave
                q = k(fr, a, n)
                dx, dy = dx + lx * q, dy + ly * q
            return dx, dy, 1.0, 0.0, (1.0 if not enter or fr >= enter[2] else 0.0)
        clip = self.say(content, ink, family, weight, colour, name, geom=g, layers=layers)
        clip["textStyle"]["wordWrap"] = False
        return clip

    def waves(self, name, y0, y1, n, colour, width=3.0, periods=2.5, amp=30.0, op=None, x0=-20, x1=W + 20,
              phase_step=0.9, dy=None):
        step = (y1 - y0) / max(1, n - 1)
        for i in range(n):
            y = y0 + i * step
            self.obj(f"{name} {i + 1}", ring(colour, width),
                     lambda fr, u, y=y: ((x0 + x1) / 2, y + (dy(fr) if dy else 0.0), x1 - x0, step * 0.9, 0, op(fr) if op else 1.0),
                     path=wave_path(periods, amp, phase=i * phase_step))


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"ig8-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels", "urbano", "azul"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.45, 1))


def story(id, es, en, order, dur, tags=(), thumb=None):
    t = _p(id, es, en, order, dur, tags, thumb)
    return t, Urban(t, dur)


# ==================================================================================================================
# 1. city vibes: two white cards spin in with the photos (a big one up top, a framed one below), URBAN rises, the
#    words whip in from the left; at 2.9 s two new cards spin in with the next photos; the words leave to the right.
def city_vibes():
    t, s = story("city-vibes", "Historia urbana: city vibes con dos fotos", "Urban story: city vibes with two photos",
                 16100, 5.8, ["ciudad", "fotos"], thumb=2.4)
    s.bg(BLUE)
    s.slide("URBAN", (-10, 1738, W + 10, 1965), MINT, "Palabra de abajo", enter=(0, 320, 6, 21), weight=900)
    big, small = (0, 262, W, 1195), (252, 969, 828, 1619)
    s.card("Foto 1", "y5-h-street-04", big, 3, label="Foto 1")
    s.card("Foto 3", "fx-skater-03", big, 87, label="Foto 3")
    s.card("Foto 2", "portrait-04", small, 5, border=34.0, start_border=34.0, label="Foto 2", rot0=-28.0)
    s.card("Foto 4", "shopping-02", small, 89, border=34.0, start_border=34.0, label="Foto 4", rot0=-28.0)
    for i in range(3):
        x = 4 + i * 88
        s.obj(f"Flecha {i + 1}", solid(WHITE),
              lambda fr, u, x=x, i=i: (x + 36 - 300 * (1 - k(fr, 9 + 2 * i, 9)), 262, 64, 62, 0,
                                       1.0 if fr >= 9 + 2 * i else 0.0), path=TRI)
    s.slide("city", (315, 52, 765, 245), WHITE, "Título", enter=(-900, 0, 30, 9), leave=(1100, 0, 159, 9))
    s.slide("vibes", (222, 300, 858, 486), MINT, "Título 2", enter=(-1000, 0, 33, 9), leave=(1150, 0, 162, 9))
    return finish(t)


# 2. visit page: a blue bar sweeps down over white and leaves the photo behind it, «visit» / «page» whip in from
#    both sides, the address closes its letter spacing, the «Sale is now.» box rises; the bar sweeps again at 2.9 s.
def visit_page():
    t, s = story("visit-page", "Historia urbana: visit page con barra azul", "Urban story: visit page with a blue bar",
                 16101, 6.0, ["web", "rebajas"], thumb=2.4)
    s.bg("#F4F4F4")
    band = 0.35 * H

    def sweep(at, n=18):
        def bottom(fr):
            return lerp(0.0, H + band, k(fr, at, n))
        return bottom

    for i, (smp, at) in enumerate((("portrait-06", 0), ("hike-01", 87))):
        b = sweep(at)
        s.pic(f"Foto {i + 1}", smp, (0, 0, W, H), label=f"Foto {i + 1}",
              matte=lambda fr, u, b=b: (W / 2, max(0.0, b(fr) - band) / 2, W, max(0.5, b(fr) - band), 0,
                                        1.0 if b(fr) > band else 0.0))
        s.bar(f"Barra {i + 1}", BLUE,
              lambda fr, u, b=b: (-10, max(-10.0, b(fr) - band), W + 10, min(H + 10.0, max(0.0, b(fr)))),
              op=lambda fr, u, b=b: 1.0 if 0 < b(fr) < H + band - 1 else 0.0)
    s.slide("visit", (304, 986, 776, 1153), WHITE, "Título", enter=(800, 0, 18, 7), leave=(1000, 0, 165, 9))
    s.slide("page", (262, 1262, 797, 1447), MINT, "Título 2", enter=(-800, 0, 18, 7), leave=(-1000, 0, 165, 9))
    web = s.say("www.website.com", (252, 1488, 833, 1541), POP, 800, WHITE, "Web")
    web["textStyle"]["wordWrap"] = False
    size = web["textStyle"]["pixelSize"]
    web["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
        [(u, round(size * 0.55 * (1 - k(fr, 18, 18)), 3), "linear") for u, fr in s.each()])
    s.typed(web, 18, stagger=0.0, duration=0.3, preset="fade")
    up = (0, 330, 33, 12)
    rise = lambda fr: 330 * (1 - back(lin(fr, 33, 12), 0.8))  # noqa: E731
    s.bar("Caja", BLUE, lambda fr, u: (67, 1640 + rise(fr), 1013, 1835 + rise(fr)))
    s.waves("Caja (onda)", 1655, 1820, 3, MINT, width=2.0, periods=1.6, amp=35,
            op=lambda fr: 0.55, x0=67, x1=1013, dy=rise)
    s.slide("Sale is", (147, 1680, 615, 1800), MINT, "Caja (texto)", enter=up)
    s.slide("now.", (640, 1680, 933, 1782), WHITE, "Caja (texto 2)", enter=up)
    return finish(t)


# 3. mega sale %50: outlined NOW rows drift behind, a white polaroid spins in with the photo, «mega sale» rises
#    (sale a little higher, then settling), the price scrambles through symbols before it lands on %50.
def mega_sale():
    t, s = story("mega-sale", "Historia urbana: mega sale %50 con polaroid", "Urban story: mega sale %50 polaroid",
                 16102, 6.5, ["rebajas", "oferta", "polaroid"], thumb=2.6)
    s.bg(MINT)
    for i, top in enumerate((-250, 200, 650, 1100)):
        d = 1 if i % 2 else -1
        c = s.say("NOW NOW", (-900, top, 1980, top + 400), POP, 900, BLUE, f"Fondo (NOW {i + 1})",
                  layers=outline_layers(BLUE, 3), editable=False,
                  geom=lambda fr, u, d=d: (d * 2.2 * fr - d * 120, 0, 1.0, 0, k(fr, 24, 6)))
        c["textStyle"]["wordWrap"] = False
    inner = (168, 430, 916, 1415)
    s.card("Foto 1", "fx-man-05", inner, 3, n=24, border=57.0, start_border=57.0, label="Foto 1", rot0=-35.0)
    s.card("Foto 2", "shopping-03", inner, 87, n=24, border=57.0, start_border=57.0, label="Foto 2", rot0=-35.0)
    s.slide("mega", (178, 1562, 520, 1680), BLUE, "Texto", enter=(0, 300, 30, 9), leave=(1100, 0, 183, 9))
    # «sale» rides a little higher first and settles on the line
    s.slide("sale", (560, 1562, 895, 1680), BLUE, "Texto 2", enter=(0, 240, 30, 9), leave=(1100, 0, 184, 9),
            extra=lambda fr: (0.0, -55 * (1 - k(fr, 36, 15))))
    junk = ["< 61", "] 38", "{ 72", "~ 05", "! 16", "# 38", "$ 49", "$ 49"]
    ink = (157, 1712, 940, 1995)
    for i, txt in enumerate(junk):
        a = 30 + 3 * i
        s.say(txt, ink, POP, 800, WHITE, f"Precio (cambio {i + 1})", editable=False,
              geom=lambda fr, u, a=a: (0, 260 * (1 - back(lin(fr, 30, 9), 0.8)), 1.0, 0,
                                       1.0 if a <= fr < a + 3 else 0.0))
    s.slide("%50", ink, WHITE, "Precio", enter=(0, 260, 30, 9), leave=(1100, 0, 186, 9))
    price = s.t.tracks[-1].clips[0]
    price["opacity"] = keys([(0.0, 0.0, "hold"), (54 / FPS, 1.0, "hold")])
    return finish(t)


# 4. friends / positive: the photo opens from the middle between two white edges (mint above with blue wave lines,
#    blue below with outlined arrows and mint hatching), «friends» drops, «positive» rises; the next photo opens
#    the same way at 2.9 s; the words leave up and down.
def friends():
    t, s = story("friends", "Historia urbana: friends positive con franja de foto",
                 "Urban story: friends positive with a photo strip", 16103, 6.0, ["amigos", "franja"], thumb=2.4)
    s.bg(BLUE)
    cy, ph, wb = 962.5, 877.0, 62.0

    def half(fr, at):
        return ph / 2 * k(fr, at, 15)

    s.rect("Menta", solid(MINT), lambda fr, u: (-10, -10, W + 10, cy - half(fr, 3) - wb * k(fr, 0, 4)))
    s.waves("Ondas", 40, 430, 7, BLUE, width=3.0, periods=2.2, amp=35)
    for i, x in enumerate((42, 419, 797)):
        s.obj(f"Flecha {i + 1}", ring("#A9C8E6", 4),
              lambda fr, u, x=x: (x + 115, 1490, 230, 190, 90, k(fr, 18, 6)), path=TRI, radius=24)
    s.obj("Rayas", solid(MINT), lambda fr, u: (W / 2, 1850, W + 40, 145, 0, k(fr, 18, 6)), path=hatch())
    for i, (smp, at) in enumerate((("friends-11", 3), ("friends-02", 87))):
        s.pic(f"Foto {i + 1}", smp, (0, cy - ph / 2, W, cy + ph / 2), label=f"Foto {i + 1}",
              matte=lambda fr, u, at=at: (W / 2, cy, W, max(0.5, 2 * half(fr, at)), 0, 1.0 if fr >= at else 0.0))
        for j, sg in enumerate((-1, 1)):
            s.bar(f"Borde {i + 1}.{j + 1}", WHITE,
                  lambda fr, u, at=at, sg=sg: (-10, cy + sg * half(fr, at) - (wb if sg < 0 else 0),
                                               W + 10, cy + sg * half(fr, at) + (wb if sg > 0 else 0)),
                  op=lambda fr, u, at=at, i=i: (1.0 if fr >= at else 0.0) if i == 0 else
                  (1.0 if at <= fr < at + 15 else 0.0))
    s.slide("friends", (178, 168, 902, 335), BLUE, "Título", enter=(0, -420, 18, 9), leave=(0, -600, 168, 9))
    s.slide("positive", (105, 1615, 975, 1782), MINT, "Título 2", enter=(0, 420, 18, 12), leave=(0, 600, 168, 9))
    return finish(t)


# 5. Best Sellers / click now: the two lines drop in, the photo wipes down from under them, «click» and «now» whip in
#    from both sides, the outlined NEW and the waves rise at the bottom; the next photo wipes down at 3.3 s.
def best_sellers():
    t, s = story("best-sellers", "Historia urbana: Best Sellers click now", "Urban story: Best Sellers click now",
                 16104, 5.6, ["tienda", "novedades"], thumb=2.2)
    s.bg(BLUE)
    top, bot = 531.0, 1760.0
    for i, (smp, at) in enumerate((("fx-skater-04", 15), ("selfie-02", 99))):
        s.pic(f"Foto {i + 1}", smp, (0, top, W, bot), label=f"Foto {i + 1}",
              matte=lambda fr, u, at=at: (W / 2, top + (bot - top) * k(fr, at, 12) / 2, W,
                                          max(0.5, (bot - top) * k(fr, at, 12)), 0, 1.0 if fr >= at else 0.0))
    rise = lambda fr: 420 * (1 - back(lin(fr, 21, 9), 0.6))  # noqa: E731
    s.obj("Olas", solid(BLUE), lambda fr, u: (W / 2, 1845 + rise(fr), W + 40, 190, 0, 1.0), path=wave_fill(2.5, 14))
    s.waves("Olas (línea)", 1800, 1880, 3, "#2A73B4", width=6.0, periods=2.5, amp=22, phase_step=1.6, dy=rise)
    s.slide("NEW", (-60, 1545, 1140, 1990), MINT, "Palabra de fondo", enter=(0, 420, 21, 9), weight=800,
            layers=outline_layers(MINT, 4))
    s.slide("Best", (250, 168, 837, 304), MINT, "Título", enter=(0, -400, 12, 8), leave=(1100, 0, 150, 9))
    s.slide("Sellers", (250, 336, 837, 482), MINT, "Título 2", enter=(0, -560, 6, 9), leave=(1100, 0, 144, 9))
    s.slide("click", (323, 902, 753, 1048), WHITE, "Texto", enter=(800, 0, 18, 7), leave=(1100, 0, 156, 9))
    s.slide("now", (344, 1143, 721, 1258), MINT, "Texto 2", enter=(-800, 0, 18, 7), leave=(-1100, 0, 156, 9))
    return finish(t)


TEMPLATES = [city_vibes, visit_page, mega_sale, friends, best_sellers]
