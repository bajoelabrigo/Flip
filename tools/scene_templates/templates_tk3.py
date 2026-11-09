"""TIKTOK folder video 3 as Stock templates (tk3-*). See docs/plan-tiktok.md.

40484842.mp4 (1920×1080 at 30 fps, 40 s): fashion stories on pale lavender with soft pastel blobs, serif titles
(Playfair Display, the closest we have), «Lorem ipsum» in Poppins, navy lines, stars and asterisks. The eight stories
are shown three and two side by side (540×960 each, laid out here ×2 on 1080×1920) and end with a «Thanks For
Watching!» card. Each story copies the reference's layout and moves, studied on 10 fps sheets (sheet index i =
reference frame 3·i); the photos are slots. Kit de TikTok; ids `tk3-*`, order 14300-. Study notes in
tienda/plantillas/estudio-40484842/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of, mask_track
from scene import keys, us
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, poly, ring

W, H = 1080, 1920
BG, NAVY, WHITE = "#E4E7EE", "#1A1B39", "#FFFFFF"
PF, PO, DM, BO = "Playfair Display", "Poppins", "DM Serif Display", "Bodoni Moda"
f6._FILES[(DM, 400)] = "fonts.extra/fonts/dmserifdisplay/DMSerifDisplay-Regular.ttf"
for w, f in ((500, "Medium"), (600, "SemiBold")):
    f6._FILES[(BO, w)] = f"fonts.extra/fonts/bodonimoda/BodoniModa-{f}.ttf"
for w, f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
    f6._FILES[(PF, w)] = f"fonts.basic/fonts/playfairdisplay/PlayfairDisplay-{f}.ttf"
    f6._FILES[(PO, w)] = f"fonts.basic/fonts/poppins/Poppins-{f}.ttf"
URL = "www.yourwebsite.com"
LOREM = ["Lorem ipsum dolor sit", "amet, consectetur", "adipiscing elit, sed do", "eiusmod tempor"]
STAR4 = "M 50 0 Q 57 43 100 50 Q 57 57 50 100 Q 43 57 0 50 Q 43 43 50 0 Z"


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"tk3-{id}", es, en, "tiktok", dur, order=order,
                tags=["tiktok", "historia", "reels", "moda", "pastel"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.55, 1))


def dur_for(entrance_frames, hold=1.5):
    e = entrance_frames / FPS
    return round(e + hold + e / EXIT, 1)


def back(x):
    """Ease with a little overshoot (0 → 1)."""
    x = min(1.0, max(0.0, x))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def kout(fr, at, n):
    x = min(1.0, max(0.0, (fr - at) / max(1e-6, n)))
    return 1 - (1 - x) ** 3


def kb(fr, at, n):
    return back((fr - at) / max(1e-6, n))


class T(S):
    """A story on 1080×1920."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)


# --- text animations -------------------------------------------------------------------------------------------

def _stagger(stagger, duration, order="forward", seed=7, ease="easeOut", domain="character"):
    return {"driver": "stagger", "domain": domain, "staggerUs": us(stagger), "durationUs": us(duration),
            "ease": ease, "order": order, "seed": seed}


def _both(clip, at, slot):
    """In at frame `at`; out = the same backwards, EXIT times faster (as S.typed)."""
    clip["textStyle"]["animation"] = {"in": dict(slot(1.0), delayUs=us(at / FPS)),
                                      "out": dict(slot(1.0 / EXIT), delayUs=us(at / FPS / EXIT))}


def blur_in(clip, at, stagger=0.09, dur=0.45, dx=34.0, dy=0.0, blur=18, order="forward", domain="character"):
    """Letters (or words) come in blurred, faded and a little to the right, one after another."""
    _both(clip, at, lambda f: {"animators": [
        {"name": "Aparecer", "selectors": [_stagger(stagger * f, dur * f, order=order, domain=domain)],
         "props": {"opacity": 0, "blur": blur, "position": {"x": dx, "y": dy, "unit": "px"}}}]})


def scatter(clip, at, stagger=0.06, dur=0.45, amp=26.0, blur=10, seed=7, order="random"):
    """Letters in random order, each blurred at a height of its own, settling onto the line (the web address)."""
    noise = {"driver": "wiggle", "domain": "character", "mode": "intersect", "wave": "noise", "frequencyHz": 0,
             "spatialPhaseDeg": 0, "temporalPhaseDeg": 0, "minAmount": -100, "maxAmount": 100, "seed": seed}
    _both(clip, at, lambda f: {"animators": [
        {"name": "Aparecer", "selectors": [_stagger(stagger * f, dur * f, order=order, seed=seed)],
         "props": {"opacity": 0, "blur": blur}},
        {"name": "Altura", "selectors": [_stagger(stagger * f, dur * 1.3 * f, order=order, seed=seed,
                                                   ease="easeInOut"), noise],
         "props": {"position": {"x": 0, "y": amp, "unit": "px"}}}]})


# --- pieces ----------------------------------------------------------------------------------------------------

def bg(s, colour=BG):
    c = s.rect("Fondo", solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))
    c["layoutRole"] = "backdrop"
    return c


def radial(colour, alpha=0.9, mid=0.55):
    a = lambda v: "#" + format(round(max(0.0, min(1.0, v)) * 255), "02x") + colour.lstrip("#").lower()  # noqa: E731
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": a(alpha),
                       "gradient": {"kind": "radial", "space": "block", "angle": 0,
                                    "stops": [{"pos": 0.0, "color": a(alpha)}, {"pos": 0.5, "color": a(alpha * mid)},
                                              {"pos": 1.0, "color": a(0.0)}]}}},
            {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0,
             "paint": {"kind": "solid", "color": "#00000000"}}]


def blob(s, name, colour, cx, cy, r, at=6, drift=(60, 40), period=7.0, phase=0.0, alpha=0.9, sq=1.0):
    """A soft colour stain (radial gradient) that drifts slowly and breathes a little."""
    def g(fr, u):
        a = 2 * math.pi * (u / period) + phase
        d = 2 * r * (1 + 0.06 * math.sin(a * 1.3))
        return (cx + drift[0] * math.sin(a), cy + drift[1] * math.cos(a * 0.8), d, d * sq, 0, k(fr, at, 24))
    c = s.obj(name, radial(colour, alpha), g, kind="ellipse", base=(2 * r * 1.06, 2 * r * 1.06 * sq))
    c["layoutRole"] = "backdrop"  # in a horizontal video the stains grow with the background, round
    return c


def grad(c0, c1, angle=0):
    from scene import gradient, no_stroke
    return [gradient([(0.0, c0), (1.0, c1)], angle=angle), no_stroke()]


def photo(s, sample, box, origin, at=3, n=40, zoom=1.45, label="Foto", name="Foto"):
    """A photo slot in box = (x0, y0, x1, y1): a window that opens from the point `origin` while the picture inside
    settles from `zoom` to 1 (as the reference)."""
    t = s.t
    x0, y0, x1, y1 = box
    b = Box(x0, y0, x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sc = lambda fr: zoom + (1 - zoom) * kout(fr, at, n)  # noqa: E731
    motion = [(u, {"s": sc(s.frame(u))}, "linear") for u in frames_of(s.dur)]
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, b, motion, label=label)
    clip["name"] = name
    ox, oy = origin

    def rect(u):
        fr = s.frame(u)
        p = kout(fr, at, n)
        r = (ox + (x0 - ox) * p, oy + (y0 - oy) * p, ox + (x1 - ox) * p, oy + (y1 - oy) * p)
        if p <= 0:
            return (-4000.0, -4000.0, -3999.0, -3999.0)
        z = sc(fr)  # the mask lives in the clip's own (scaled) frame
        return (cx + (r[0] - cx) / z, cy + (r[1] - cy) / z, cx + (r[2] - cx) / z, cy + (r[3] - cy) / z)
    mask_track(t, clip, b, rect, s.dur)
    return clip


def title(s, content, ink, at, name="Título", weight=500, align="left", stagger=0.11, dur=0.6):
    c = s.say(content, ink, PF, weight, NAVY, name, align=align)
    blur_in(c, at, stagger=stagger, dur=dur)
    return c


def lorem(s, lines, x, top, at, pitch=50, cap=27, align="left", gap=12, name="Texto", colour=NAVY):
    """Body lines in Poppins, each coming in word by word (blurred) after the one above."""
    out = []
    for i, ln in enumerate(lines):
        y = top + i * pitch
        ink = (x, y, x + 1400, y + cap) if align == "left" else (x - 700, y, x + 700, y + cap)
        c = s.say(ln, ink, PO, 400, colour, name if i == 0 else f"{name} {i + 1}", align=align)
        blur_in(c, at + i * gap, stagger=0.16, dur=0.5, dx=10, blur=10, domain="word")
        out.append(c)
    return out


def web(s, ink, at, colour=NAVY, align="left", seed=7):
    c = s.say(URL, ink, PF, 400, colour, "Web", align=align)
    scatter(c, at, seed=seed)
    return c


def spokes(angles, half=1.2):
    """Lines through the middle of a 100 box (an asterisk / a cross), each `2·half` thick."""
    out = []
    for a in angles:
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        nx, ny = -dy, dx
        out.append(poly([(50 + 50 * dx + half * nx, 50 + 50 * dy + half * ny),
                         (50 + 50 * dx - half * nx, 50 + 50 * dy - half * ny),
                         (50 - 50 * dx - half * nx, 50 - 50 * dy - half * ny),
                         (50 - 50 * dx + half * nx, 50 - 50 * dy + half * ny)]))
    return " ".join(out)


def pop(s, name, layers, cx, cy, w, h, at, n=9, path=None, kind="rectangle", rot=None, op=None, spin=0.0):
    """A shape that grows from nothing with a little overshoot (turning `spin` degrees as it grows)."""
    def g(fr, u):
        p = kb(fr, at, n)
        r = (rot(fr, u) if rot else 0.0) - spin * (1 - k(fr, at, n))
        return cx, cy, w * max(0.0, p), h * max(0.0, p), r, (op(fr, u) if op else 1.0) if fr > at else 0.0
    return s.obj(name, layers, g, kind=kind, path=path, base=(w * 1.12, h * 1.12))


def twinkle(period, offset=0.0):
    """Rotation of a cross that now and then turns 45° and back (the crosses of the reference)."""
    def r(fr, u):
        ph = ((u + offset) % period) / period
        return 45.0 * k(ph * 60, 0, 6) * (1 - k(ph * 60, 24, 6))
    return r


def line_x(s, name, x0, x1, y, w, at, n, side="right", colour=NAVY):
    """A thin horizontal line that slides in from a side of the frame."""
    off = (W + 10 - x0) if side == "right" else -(x1 + 10)
    return s.rect(name, solid(colour), lambda fr, u: (x0 + off * (1 - k(fr, at, n)), y - w / 2,
                                                       x1 + off * (1 - k(fr, at, n)), y + w / 2))


def line_y(s, name, x, y0, y1, w, at, n, grow="down", colour=NAVY):
    """A thin vertical line that draws itself from its top (down) or its bottom (up)."""
    if grow == "down":
        return s.rect(name, solid(colour), lambda fr, u: (x - w / 2, y0, x + w / 2, y0 + (y1 - y0) * k(fr, at, n)))
    return s.rect(name, solid(colour), lambda fr, u: (x - w / 2, y1 - (y1 - y0) * k(fr, at, n), x + w / 2, y1))


def sparkles_row(s, name, x0, step, y, size, count, at, gap=2, vertical=False):
    for i in range(count):
        x, yy = (x0, y + i * step) if vertical else (x0 + i * step, y)
        pop(s, f"{name} {i + 1}", ring(NAVY, 2.2), x, yy, size, size, at + i * gap, n=8, path=STAR4)


def dots(s, x, ys, size, at, gap=5, blink=2.4, small=()):
    """A column of dots that come one by one and then blink in turn."""
    for i, y in enumerate(ys):
        d = size * (0.45 if i in small else 1.0)

        def op(fr, u, i=i):
            ph = ((u - i * 0.35) % blink) / blink
            return 0.25 + 0.75 * (1 - k(ph * 60, 40, 6) * (1 - k(ph * 60, 52, 6)))
        pop(s, f"Punto {i + 1}", solid(NAVY), x, y, d, d, at + i * gap, n=6, kind="ellipse", op=op)


# --- 1. Fashion Sale 50% OFF -----------------------------------------------------------------------------------
def fashion_sale():
    D = dur_for(150)
    t = _p("rebajas", "Historia: rebajas de moda con caja 50% OFF", "Story: fashion sale with a 50% OFF box", 14300, D,
           ["rebajas", "descuento"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha lila", "#D5B0F8", 820, 300, 330, drift=(70, 40))
    blob(s, "Mancha rosa", "#F2B6EC", 1000, 520, 220, drift=(40, 60), phase=1.5, alpha=0.7)
    blob(s, "Mancha lila (abajo)", "#C9A0F6", 140, 1660, 330, drift=(50, 50), phase=3.0)
    blob(s, "Mancha rosa (abajo)", "#F0B4E6", 330, 1840, 220, drift=(60, 30), phase=0.7, alpha=0.6)
    s.obj("Aro de arriba", ring(NAVY, 28), lambda fr, u: (84 - 200 * (1 - k(fr, 15, 12)), 4 - 200 * (1 - k(fr, 15, 12)),
                                                          140, 140, 0, 1), kind="ellipse")
    s.obj("Aro de abajo", ring(NAVY, 36), lambda fr, u: (932, 1916 + 260 * (1 - k(fr, 18, 12)), 212, 212, 0, 1),
          kind="ellipse")
    s.outline("Triángulo", [(130, 556), (130, 780), (356, 780)], 3, NAVY, at=75, n=15)
    photo(s, "fx-figure-03", (196, 596, 996, 1496), (596, 1046), at=3, n=40)
    pop(s, "Estrella", solid(NAVY), 996, 1196, 190, 230, 81, n=9, path=STAR4)
    s.rect("Caja", solid(NAVY), lambda fr, u: (262, 1402, 262 + 656 * max(0.012, k(fr, 45, 18)), 1556),
           op=lambda fr, u: 1.0 if fr > 45 else 0.0)
    c = s.say("50% OFF", (348, 1432, 840, 1520), DM, 400, WHITE, "Descuento")
    scatter(c, 66, stagger=0.1, dur=0.35, amp=30, blur=8, order="forward", seed=3)
    title(s, "Fashion", (256, 274, 866, 400), 9)
    title(s, "Sale", (400, 424, 720, 556), 33, name="Título 2")
    lorem(s, LOREM[:2], 594, 1604, 75, align="center", gap=24)
    return t


# --- 2. Keep It Trendy 50% -------------------------------------------------------------------------------------
def keep_trendy():
    D = dur_for(180)
    t = _p("tendencia", "Historia: Keep It Trendy con 50%", "Story: Keep It Trendy with 50%", 14301, D,
           ["tendencia", "descuento"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha naranja", "#F2C08E", 820, 860, 300, drift=(40, 50), phase=2.0)
    blob(s, "Mancha rosa", "#EE7FA6", 860, 560, 330, drift=(50, 40))
    blob(s, "Mancha lila", "#B98AF0", 640, 380, 230, drift=(40, 30), phase=1.0, alpha=0.75)
    blob(s, "Mancha rosa (abajo)", "#EE86B8", 150, 1760, 300, drift=(50, 40), phase=3.5)
    blob(s, "Mancha lila (abajo)", "#C29AF2", 420, 1900, 240, drift=(40, 30), phase=0.5, alpha=0.7)
    s.rect("Barra", grad("#9266D9", "#D68597"), lambda fr, u: (600 + 500 * (1 - k(fr, 36, 30)), 0,
                                                              1080 + 500 * (1 - k(fr, 36, 30)), 86))
    line_x(s, "Raya", 586, 1080, 1634, 4, 21, 9)
    s.obj("Rombo", ring(NAVY, 2.5), lambda fr, u: (540, 1920, 30, 30, 45, k(fr, 30, 9)))
    pop(s, "Asterisco", solid(NAVY), 216, 470, 192, 192, 9, n=12, path=spokes([-80, -35, 12, 55], 1.3), spin=60)
    photo(s, "fx-woman-04", (0, 640, 630, 1446), (420, 1000), at=3, n=40)
    pop(s, "Estrella", solid(NAVY), 176, 1452, 190, 190, 93, n=9, path=STAR4)
    title(s, "Keep It", (442, 376, 944, 484), 6)
    title(s, "Trendy", (436, 524, 944, 644), 30, name="Título 2")
    lorem(s, LOREM, 480, 720, 75)
    c = s.say("50%", (546, 1200, 954, 1346), BO, 600, NAVY, "Descuento")
    blur_in(c, 105, stagger=0.3, dur=0.5, dx=40, blur=22, order="backward")
    c = s.say("OFF", (792, 1376, 954, 1436), BO, 500, NAVY, "Descuento 2")
    blur_in(c, 129, stagger=0.08, dur=0.4, dx=0, dy=16, blur=12)
    web(s, (464, 1510, 1040, 1556), 132)
    return t


# --- 3. Lifestyle ----------------------------------------------------------------------------------------------
def lifestyle():
    D = dur_for(180)
    t = _p("estilo-de-vida", "Historia: Lifestyle con triángulo que gira", "Story: Lifestyle with a turning triangle",
           14302, D, ["estilo de vida"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha naranja", "#F3A88B", 330, 1820, 300, drift=(50, 30), phase=1.0)
    blob(s, "Mancha rosa", "#F27BC8", 120, 1620, 360, drift=(60, 50))
    blob(s, "Mancha celeste", "#BFE6F0", 1000, 1520, 200, drift=(30, 30), phase=2.0, alpha=0.6)
    for i, x in enumerate((340, 470, 600, 736)):
        s.obj(f"Aro {i + 1}", ring(NAVY, 2.5), lambda fr, u, x=x: (x, -6 - 300 * (1 - k(fr, 15 + 2 * i, 15)), 252,
                                                                     252, 0, 1), kind="ellipse")
    photo(s, "portrait-08", (330, 604, 1080, 1504), (1080, 1054), at=3, n=40)
    ast = spokes([0, 90, 50, 130], 0.8)
    pop(s, "Asterisco", solid(NAVY), 330, 916, 314, 314, 81, n=24, path=ast, spin=40)
    pop(s, "Asterisco 2", solid(NAVY), 330, 1264, 314, 314, 108, n=18, path=ast, spin=40)
    title(s, "Lifestyle", (180, 330, 784, 460), 6, stagger=0.13)
    pop(s, "Destello", solid(NAVY), 808, 346, 40, 48, 87, n=8, path=STAR4)
    pop(s, "Destello 2", solid(NAVY), 838, 308, 22, 26, 90, n=8, path=STAR4)
    tri = poly([(50, 0), (100, 86), (0, 86)])
    pop(s, "Triángulo", grad("#F27BEC", "#F3A88B", 90), 944, 394, 160, 140, 78, n=18, path=tri,
        rot=lambda fr, u: 180 + 0.5 * (fr - 78))
    lorem(s, LOREM, 176, 540, 75)
    web(s, (204, 1620, 840, 1666), 132)
    return t


# --- 4. Giveaway! ----------------------------------------------------------------------------------------------
def giveaway():
    D = dur_for(150)
    t = _p("sorteo", "Historia: Giveaway! (sorteo)", "Story: Giveaway!", 14303, D, ["sorteo", "concurso"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha celeste", "#BFDFEB", 420, 1820, 300, drift=(50, 30), phase=2.0)
    blob(s, "Mancha lila", "#BC91E4", 160, 1650, 400, drift=(50, 40))
    blob(s, "Mancha rosa", "#F0A8E8", 90, 1450, 240, drift=(40, 40), phase=1.0, alpha=0.7)
    line_x(s, "Raya", 0, 646, 176, 4, 9, 18, side="left")
    s.obj("Raya (círculo)", ring(NAVY, 4), lambda fr, u: (666 - 690 * (1 - k(fr, 9, 18)), 176, 40, 40, 0, 1),
          kind="ellipse")
    photo(s, "fx-fashion-01", (190, 512, 890, 1410), (540, 961), at=3, n=40)
    pop(s, "Estrella", solid(NAVY), 890, 646, 150, 190, 78, n=9, path=STAR4)
    pop(s, "Triángulo", grad("#BE67F6", "#644FCE", 135), 188, 1290, 216, 186, 81, n=9,
        path=poly([(0, 0), (100, 0), (50, 100)]))
    pop(s, "Asterisco", solid(NAVY), 274, 1564, 188, 188, 87, n=18, path=spokes([-90, -45, 0, 45], 1.4), spin=50)
    title(s, "Giveaway!", (180, 344, 910, 460), 9)
    lorem(s, LOREM, 436, 1470, 90)
    return t


# --- 5. Fashion Sale (50% over the photo) ----------------------------------------------------------------------
def fashion_sale_2():
    D = dur_for(174)
    t = _p("rebajas-2", "Historia: Fashion Sale con 50% sobre la foto", "Story: Fashion Sale with 50% over the photo",
           14304, D, ["rebajas", "descuento"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha amarilla", "#F3E2A6", 300, 1060, 300, drift=(40, 40), phase=2.0)
    blob(s, "Mancha rosa", "#F0A2D8", 230, 720, 360, drift=(50, 40))
    blob(s, "Mancha lila", "#D9B6F4", 540, 300, 220, drift=(40, 30), phase=1.0, alpha=0.5)
    for i, x in enumerate((344, 472, 602, 734)):
        s.obj(f"Aro {i + 1}", ring(NAVY, 2.5), lambda fr, u, x=x, i=i: (x, 1918 + 320 * (1 - k(fr, 6 + 6 * i, 36)),
                                                                          260, 260, 0, 1), kind="ellipse")
    photo(s, "fx-figure-05", (380, 530, 1080, 1430), (1080, 980), at=3, n=40)
    for i, y in enumerate((30, 150, 270, 396)):
        pop(s, f"Cruz {i + 1}", solid(NAVY), 950, y, 90, 90, 9 + 3 * i, n=9, path=spokes([0, 90], 1.6),
            rot=twinkle(2.2 + 0.4 * i, 0.5 * i))
    sparkles_row(s, "Estrellita", 224, 63, 266, 36, 6, 12)
    title(s, "Fashion Sale", (200, 360, 890, 456), 12, stagger=0.1)
    lorem(s, LOREM, 192, 856, 72)
    c = s.say("50%", (220, 610, 636, 766), BO, 600, NAVY, "Descuento")
    blur_in(c, 108, stagger=0.28, dur=0.5, dx=40, blur=22, order="backward")
    c = s.say("OFF", (526, 784, 636, 820), BO, 600, NAVY, "Descuento 2")
    blur_in(c, 132, stagger=0.08, dur=0.4, dx=0, dy=12, blur=10)
    web(s, (210, 1504, 860, 1552), 132)
    return t


# --- 6. The Next Level Of Fashion (vertical 50% OFF) -----------------------------------------------------------
def next_level():
    D = dur_for(180)
    t = _p("siguiente-nivel", "Historia: The Next Level Of Fashion con 50% OFF vertical",
           "Story: The Next Level Of Fashion with a vertical 50% OFF", 14305, D, ["descuento"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha celeste", "#A6DAF4", 620, 140, 380, drift=(60, 40))
    blob(s, "Mancha lila", "#D2B6F4", 900, 300, 290, drift=(50, 40), phase=1.6, alpha=0.8)
    blob(s, "Mancha clara", "#C9D6E5", 380, 380, 220, drift=(40, 30), phase=3.0, alpha=0.6)
    s.rect("Barra", grad("#8E64E6", "#D97F99"), lambda fr, u: (500 + 600 * (1 - k(fr, 21, 39)), 1844,
                                                              1080 + 600 * (1 - k(fr, 21, 39)), 1920))
    pop(s, "Cruz", solid(NAVY), 72, 1846, 92, 92, 9, n=9, path=spokes([0, 90], 1.6), rot=twinkle(2.6))
    sparkles_row(s, "Estrellita", 150, 89, 80, 52, 6, 15, vertical=True)
    photo(s, "fx-fashion-06", (0, 640, 700, 1540), (0, 1090), at=3, n=40)
    title(s, "The Next", (324, 280, 900, 384), 9)
    title(s, "Level Of", (324, 430, 850, 534), 27, name="Título 2")
    title(s, "Fashion", (324, 576, 816, 684), 39, name="Título 3")
    c = s.say("50% OFF", (802 - 245, 1104 - 48, 802 + 245, 1104 + 48), BO, 600, NAVY, "Descuento",
              rot=lambda fr, u: 90)
    blur_in(c, 90, stagger=0.13, dur=0.5, dx=30, blur=18, order="backward")
    web(s, (316, 1590, 940, 1638), 138)
    return t


# --- 7. Fashion Design -----------------------------------------------------------------------------------------
def fashion_design():
    D = dur_for(180)
    t = _p("diseno", "Historia: Fashion Design con líneas finas", "Story: Fashion Design with thin lines", 14306, D,
           ["diseño", "descuento"], )
    s = T(t, D)
    bg(s)
    blob(s, "Mancha amarilla", "#F6EFC8", 780, 1540, 280, drift=(40, 30), phase=2.0)
    blob(s, "Mancha morada", "#A384EC", 620, 820, 470, drift=(60, 50))
    blob(s, "Mancha rosa", "#E8A2F2", 330, 1140, 320, drift=(40, 40), phase=1.0, alpha=0.8)
    blob(s, "Mancha rosa (abajo)", "#EFB2EE", 880, 1300, 240, drift=(30, 30), phase=3.0, alpha=0.6)
    line_y(s, "Raya vertical", 356, 0, 1020, 3, 36, 24)
    line_x(s, "Raya", 356, 1080, 1020, 3, 18, 9)
    dots(s, 240, (250, 340, 430, 520, 610), 11, 6, gap=6, small=(4,))
    pop(s, "Cruz", solid(NAVY), 972, 94, 92, 92, 9, n=9, path=spokes([-5, 85], 1.5), rot=twinkle(3.0))
    sparkles_row(s, "Estrellita", 616, 63, 1444, 36, 6, 18)
    s.obj("Triángulo", grad("#F9F0C1", "#F4B8F3", 90),
          lambda fr, u: (806, 1760 - 200 * k(fr, 78, 30) / 2, 228, 200 * k(fr, 78, 30), 0, 1.0 if fr > 78 else 0.0),
          path=poly([(50, 0), (100, 100), (0, 100)]), base=(228, 200))
    photo(s, "man-05", (0, 800, 620, 1920), (0, 1920), at=15, n=45, zoom=1.3)
    title(s, "Fashion", (494, 316, 984, 420), 27)
    title(s, "Design", (494, 470, 920, 570), 45, name="Título 2")
    lorem(s, ["Lorem ipsum dolor sit", "amet, consectetur", "adipiscing elit"], 458, 632, 75)
    c = s.say("Get 50% OFF", (516, 1214, 950, 1266), DM, 400, NAVY, "Descuento")
    scatter(c, 126, stagger=0.07, dur=0.4, amp=0, blur=16, seed=5)
    web(s, (580, 1350, 940, 1386), 156)
    return t


# --- 8. The Next Level Of Fashion (green photo, Get 50% OFF) ---------------------------------------------------
def next_level_2():
    D = dur_for(168)
    t = _p("siguiente-nivel-2", "Historia: The Next Level Of Fashion con Get 50% OFF",
           "Story: The Next Level Of Fashion with Get 50% OFF", 14307, D, ["descuento"])
    s = T(t, D)
    bg(s)
    blob(s, "Mancha rosa", "#D383E9", 980, 320, 320, drift=(50, 40))
    blob(s, "Mancha lila (abajo)", "#C98BD0", 220, 1800, 320, drift=(50, 30), phase=1.0)
    blob(s, "Mancha naranja", "#E9B0A0", 60, 1640, 230, drift=(30, 40), phase=2.5, alpha=0.7)
    line_x(s, "Raya", 356, 1080, 240, 3, 9, 15)
    line_y(s, "Raya vertical", 690, 1524, 1920, 3, 6, 24, grow="up")
    photo(s, "fx-figure-04", (380, 494, 1080, 1394), (1080, 944), at=3, n=40)
    title(s, "The Next", (206, 304, 780, 404), 9)
    title(s, "Level Of", (206, 454, 734, 554), 27, name="Título 2")
    title(s, "Fashion", (206, 602, 700, 704), 39, name="Título 3")
    dots(s, 172, (836, 972, 1108, 1242, 1376), 22, 36, gap=6, small=(0,))
    pop(s, "Estrella", solid(NAVY), 870, 1572, 124, 124, 66, n=9, path=STAR4)
    lorem(s, LOREM[:2], 106, 1570, 78, gap=24)
    c = s.say("Get 50% OFF", (152, 1474, 600, 1530), DM, 400, NAVY, "Descuento")
    scatter(c, 111, stagger=0.07, dur=0.4, amp=0, blur=16, seed=5)
    return t


# --- 9. Thanks For Watching! -----------------------------------------------------------------------------------
def thanks():
    D = 5.6
    t = _p("gracias", "Cierre: Thanks For Watching!", "End card: Thanks For Watching!", 14308, D, ["cierre", "gracias"],
           thumb=2.5)
    s = T(t, D)
    s.frame = lambda u: u * FPS  # the words leave on their own, the card holds
    bg(s, "#7471C4")
    c = s.say("Thanks For Watching!", (90, 926, 990, 994), PF, 500, WHITE, "Título", align="center")
    fly = lambda f: {"animators": [  # noqa: E731
        {"name": "Aparecer", "selectors": [_stagger(0.055 * f, 0.55 * f, order="forward")],
         "props": {"opacity": 0, "blur": 24, "position": {"x": 30, "y": 24, "unit": "px"}, "rotation": 8}}]}
    c["textStyle"]["animation"] = {"in": dict(fly(1.0), delayUs=us(0.45)), "out": dict(fly(0.9), delayUs=0)}
    return t


def art(make):
    """In a normal (horizontal) video the story keeps its shape: every clip is design ("art", fitted together as one
    column) except the background and its stains (as yp4's art_except)."""
    def wrapped():
        t = make()
        for track in t.tracks:
            for clip in track.clips:
                if clip.get("type") in ("audio", "adjustment", "composite") or "layoutRole" in clip:
                    continue
                clip["layoutRole"] = "art"
        return t
    wrapped.__name__ = make.__name__
    wrapped.__module__ = make.__module__
    return wrapped


TEMPLATES = [art(f) for f in (fashion_sale, keep_trendy, lifestyle, giveaway, fashion_sale_2, next_level, fashion_design,
             next_level_2, thanks)]
