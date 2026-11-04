"""Clean lower thirds, third set (2026-10-31): «Lower Thirds Library: Clean Edition» (36403326.mp4, 1920×1080 at
29.97 fps): white and yellow labels in Montserrat. Each one is born from a thin yellow line that grows up from the
label's bottom, widens into a yellow block that uncovers the name, and a white fill sweeps in behind it. Every edge
plays the curve measured at 30 fps (lt_ref/lt3-<name>.json and lt3-<name>-line.json; study in
tienda/plantillas/estudio-36403326/NOTAS.md); the exit is the entrance played backwards, as in the reference. They
sit where the reference has them (bottom left). Order 8574-. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import json
from pathlib import Path

from kit import Box, label, photo_bg, wide
from llt_motion import frames_of, mask_track
from scene import keys

FONT = "Montserrat"
YELLOW = "#FFD80A"
WHITE = "#FFFFFF"
INK = "#151515"
FPS = 30.0
_REF = Path(__file__).with_name("lt_ref")
_FONT_DIR = Path(__file__).resolve().parents[4] / "codigo" / "flip-addons" / "build" / "stage" / "fonts.basic" / \
    "fonts" / "montserrat"
_FACES = {500: "Medium", 600: "SemiBold", 700: "Bold"}


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt3-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "limpio"] + tags,
                **kw)


def fit(text: str, width: float, weight: int = 700) -> float:
    """The Montserrat size at which `text`'s ink is `width` px wide."""
    from PIL import ImageFont
    f = ImageFont.truetype(str(_FONT_DIR / f"Montserrat-{_FACES[weight]}.ttf"), 200)
    bb = f.getbbox(text)
    return round(width / (bb[2] - bb[0]) * 200, 1)


class Measured:
    """One reference measurement (lt_measure.py): per frame, the runs of each colour in each band."""

    def __init__(self, name):
        self.frames = json.loads((_REF / f"{name}.json").read_text(encoding="utf-8"))["frames"]

    def runs(self, f, band, *kinds):
        f = max(0, min(len(self.frames) - 1, int(round(f))))
        out = []
        for k in kinds:
            out += self.frames[f][band].get(k, [])
        return out

    def series(self, band, kinds, pick, lo=None, hi=None):
        """{frame: value} where pick(runs) is not None, frames lo..hi."""
        lo = 0 if lo is None else lo
        hi = len(self.frames) - 1 if hi is None else hi
        out = {}
        for f in range(lo, hi + 1):
            v = pick(self.runs(f, band, *kinds))
            if v is not None:
                out[f] = v
        return out


def held(points: dict, before, after=None):
    """frame -> value from measured {frame: value}: `before` until the first, linear between, the last after."""
    fs = sorted(points)
    after = points[fs[-1]] if after is None else after

    def f(fr):
        if not fs or fr < fs[0]:
            return before
        if fr >= fs[-1]:
            return after
        for a, b in zip(fs, fs[1:]):
            if a <= fr <= b:
                return points[a] + (points[b] - points[a]) * (fr - a) / (b - a)
        return after
    return f


def right_of(skip_to=200):
    """The right end of the runs past the left stripe (x 194-199)."""
    def pick(runs):
        # A run reaching past the stripe (while the block is still joined to the stripe it starts at 194).
        ends = [r[1] + 1 for r in runs if r[1] >= skip_to + 2]
        return max(ends) if ends else None
    return pick


def top_of(runs):
    return min(r[0] for r in runs) if runs else None


class Piece:
    """One lower third in reference coordinates; its entrance (measured frames) mirrored into the exit."""

    def __init__(self, t, dur, first=0):
        self.t, self.dur, self.first = t, dur, first

    def frame(self, u):
        return self.first + min(u, self.dur - u) * FPS

    def rect(self, name, colour, full, rect, kind="rectangle", radius=0):
        box = Box(full[0], full[1], full[2] - full[0], full[3] - full[1])
        motion = []
        for u in frames_of(self.dur):
            x0, y0, x1, y1 = rect(self.frame(u))
            w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
            motion.append((u, {"sx": w / box.w, "sy": h / box.h, "dx": (x0 + x1) / 2 - box.cx,
                               "dy": (y0 + y1) / 2 - box.cy}, "linear"))
        clip = self.t.solid(self.t.track("shape", name), colour, 0.0, self.dur, box, motion, radius=radius, kind=kind)
        clip["name"] = name
        return clip

    def text(self, content, ink_left, ink_top, ink_bottom, width, weight, colour, name, reveal=None, slide=None,
             editable=True, grow=1.0):
        """Montserrat whose ink is `width` wide from `ink_left`, its letters between ink_top and ink_bottom (caps and
        ascenders); reveal(frame) = (x0, y0, x1, y1) shows only that part; slide(frame) = dy."""
        # The reference's Montserrat is a little bigger and tighter than a plain fit by width (Jorge: «el nombre
        # que sale arriba es más chico que en la muestra»): `grow` raises the size and the letters close up by
        # the same width, so the line keeps its measured width.
        size = round(fit(content, width, weight) * grow, 1)
        spacing = -width * (grow - 1.0) / max(1, len(content) - 1)
        h = size * 1.6
        centre = (ink_top + ink_bottom) / 2 + size * 0.06
        box = Box(ink_left - size * 0.08, centre - h / 2, width + size * 1.5, h)
        motion = [(u, {"dy": slide(self.frame(u))}, "linear") for u in frames_of(self.dur)] if slide else None
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, box, FONT, size, colour,
                     weight=weight, align="left", name=name, line=1.0, motion=motion, editable=editable,
                     spacing=round(spacing, 2))
        if reveal:
            def local(u):
                x0, y0, x1, y1 = reveal(self.frame(u))
                dy = slide(self.frame(u)) if slide else 0.0
                return (x0, y0 - dy, x1, y1 - dy)
            mask_track(self.t, clip, box, local, self.dur)
        return clip


_KIND = {YELLOW: "yellow", WHITE: "white"}
GREY = "#BDBDBD"
_KIND[GREY] = "grey"


def _label(p, m, line_m, top, bottom, white_right, name, name_ink, line_from=0, accent=YELLOW, base=WHITE,
           name_colour=INK, line_colour=None, band="top", base_box=None):
    """The common build: the line grows up from the bottom (x 194-199, stays as the left stripe) with a white glint
    running up inside it, the accent block widens to the right, the base sweeps in behind it; the name shows inside
    both. Colours: any of yellow, white, grey (Nigel turns white then yellow, Jacob grey then white)."""
    line_colour = line_colour or accent
    line_top = held(line_m.series("line", ("yellow", "white", "grey"), top_of, lo=line_from), bottom, top)
    glint = line_m.series("line", ("white",),
                          lambda r: next(((a, b + 1) for a, b in r if a > top + 1 and b < bottom + 1), None),
                          lo=line_from) if line_colour != WHITE else {}
    acc_series = m.series(band, (_KIND[accent],), right_of(200 if accent != WHITE else 201), lo=line_from)
    acc = held(acc_series, 200)
    base_r = held(m.series(band, (_KIND[base],), right_of(201 if base == WHITE else 200), lo=line_from), 202,
                  white_right)
    acc_last = max(acc_series.values())
    p.rect("Línea", line_colour, (194, top, 200, bottom), lambda fr: (194, line_top(fr), 200, bottom))
    if glint:
        p.rect("Brillo", WHITE, (194, top, 200, bottom),
               lambda fr: (194, glint[int(fr)][0], 200, glint[int(fr)][1]) if int(fr) in glint
               else (194, bottom, 200, bottom))
    p.rect("Bloque", accent, (200, top, acc_last, bottom), lambda fr: (200, top, max(200, acc(fr)), bottom))
    # The base may sit inside the block, leaving it as a frame (Jonatan: 7 px of yellow above, below and left).
    bt, bb = base_box or (top, bottom)
    p.rect("Etiqueta", base, (202, bt, white_right, bb), lambda fr: (202, bt, max(202, base_r(fr)), bb))
    shown = lambda fr: (200, top, max(acc(fr), base_r(fr)), bottom)  # noqa: E731
    p.text(name, *name_ink, 700, name_colour, "Nombre", reveal=shown, grow=1.06)
    return acc, base_r


# The names and roles share one size across the set (measured on Clarke): a name or role not measured cleanly is
# laid out at that size.
_NAME_SIZE = None
_ROLE_SIZE = None


def name_width(text):
    global _NAME_SIZE
    _NAME_SIZE = _NAME_SIZE or fit("Thomas Clarke", 596, 700)
    return _ink(text, _NAME_SIZE, 700)


def role_width(text, weight=600):
    global _ROLE_SIZE
    _ROLE_SIZE = _ROLE_SIZE or fit("head physician", 376, 600)
    return _ink(text, _ROLE_SIZE, weight)


def _ink(text, size, weight):
    from PIL import ImageFont
    f = ImageFont.truetype(str(_FONT_DIR / f"Montserrat-{_FACES[weight]}.ttf"), 200)
    bb = f.getbbox(text)
    return (bb[2] - bb[0]) * size / 200


def clarke():
    """Thomas Clarke: a tall white label (name and role inside), a yellow «exclusive guest» tag with a slanted end on
    top."""
    D = 6.0
    t = _kit("invitado", "Tercio limpio: etiqueta blanca con «invitado especial»",
             "Clean lower third: white label with a guest tag", D, 8574, ["nombre", "amarillo", "blanco", "invitado"],
             thumb_at=3.0)
    p = Piece(t, D)
    m, line_m = Measured("lt3-clarke"), Measured("lt3-clarke-line")
    acc, base_r = _label(p, m, line_m, 745, 918, 895, "Thomas Clarke", (251, 771, 829, 596))
    # The role comes up from below the label's bottom (hidden till then), overshoots onto the name and settles
    # (frames 46-64).
    slide = held({46: 90, 50: 30, 54: -17, 58: -8, 64: 0}, 90)
    p.text("head physician", 250, 844, 878, 376, 600, INK, "Cargo", slide=slide,
           reveal=lambda fr: (202, 745, max(202, base_r(fr)), 918))
    # The tag grows to the right from the stripe (frames 44-52), its right end slanted.
    tag = held({43: 194, 44: 243, 45: 341, 46: 425, 47: 493, 48: 539, 49: 575, 50: 601, 51: 621, 52: 627}, 194)
    p.rect("Pestaña", YELLOW, (194, 697, 612, 733), lambda fr: (194, 697, max(194, tag(fr) - 15), 733))
    p.rect("Punta", YELLOW, (597, 697, 627, 733), lambda fr: (tag(fr) - 15, 697, tag(fr) + 15, 733) if tag(fr) > 224 else (194, 733, 194, 733),
           kind="right-triangle")
    p.text("exclusive guest", 248, 702, 726, 243, 600, INK, "Etiqueta", grow=1.12, reveal=lambda fr: (194, 690, tag(fr) - 12, 740))
    return t


def bond():
    """Thomas Bond: a short white label with the name, the role in yellow under it (it comes down from behind)."""
    D = 6.0
    t = _kit("cargo-amarillo", "Tercio limpio: etiqueta blanca y cargo amarillo",
             "Clean lower third: white label, yellow role", D, 8575, ["nombre", "amarillo", "blanco"], thumb_at=3.0)
    p = Piece(t, D, first=10)
    m = Measured("lt3-bond")
    acc, base_r = _label(p, m, m, 757, 843, 809, "Thomas Bond", (222, 771, 829, 557), line_from=12)
    # Out from behind the label's bottom (frames 54-66): hidden above y 844 until then.
    slide = held({54: -64, 57: -30, 60: -12, 63: -3, 66: 0}, -64)
    p.text("technology officer", 195, 860, 893, 462, 600, YELLOW, "Cargo", slide=slide,
           reveal=lambda fr: (194, 844, 1000, 930))
    return t


def _new(id, es, en, order, tags):
    t = _kit(id, es, en, 6.0, order, ["nombre"] + tags, thumb_at=3.0)
    return t


def _role_inside(p, text, top_ink, base_r, x=250, width=None, weight=600, colour=INK, rise=(46, 64)):
    """A role under the name inside a tall label: it comes up from below the label's bottom, overshoots a little
    onto the name and settles, as Clarke's does (scaled to the frames `rise`)."""
    a, b = rise
    k = (b - a) / 18.0
    slide = held({a: 90, a + 4 * k: 30, a + 8 * k: -17, a + 12 * k: -8, b: 0}, 90)
    p.text(text, x, top_ink, top_ink + 34, width or role_width(text, weight), weight, colour, "Cargo", slide=slide,
           reveal=lambda fr: (202, 745, max(202, base_r(fr)), 918))


def nigel():
    """Nigel Harper: a white line grows up, white sweeps right and yellow follows behind it: the label ends yellow,
    the name and role dark, a white stripe on the left."""
    t = _new("amarillo", "Tercio limpio: etiqueta amarilla", "Clean lower third: yellow label", 8576, ["amarillo"])
    p = Piece(t, 6.0, first=10)
    m = Measured("lt3-nigel")
    acc, base_r = _label(p, m, Measured("lt3-nigel-line"), 745, 918, 800, "Nigel Harper",
                         (249, 771, 829, name_width("Nigel Harper")), line_from=12, accent=WHITE, base=YELLOW)
    _role_inside(p, "policeman", 846, base_r, rise=(36, 54))
    return t


def cornelius():
    """Cornelius Rose: a short white label, and under it a yellow bar with a slanted end that runs out to the right
    with the role."""
    t = _new("barra-inclinada", "Tercio limpio: cargo en barra amarilla inclinada",
             "Clean lower third: role on a slanted yellow bar", 8577, ["amarillo", "blanco"])
    p = Piece(t, 6.0)
    m = Measured("lt3-cornelius")
    acc, base_r = _label(p, m, Measured("lt3-cornelius-line"), 757, 843, 840, "Cornelius Rose", (220, 771, 829, 594))
    bar = Measured("lt3-cornelius-bar")
    low = held(bar.series("barlow", ("yellow",), right_of(), lo=30), 194)
    tip = held({42: 0, 43: 23, 44: 38, 45: 50, 46: 58, 47: 61}, 0)
    p.rect("Barra", YELLOW, (194, 846, 614, 912), lambda fr: (194, 846, max(194, low(fr)), 912))
    # The slanted end: wider at the top (61 px over the bar's height), drawn after the bar reaches its length.
    motion = [(u, {"sx": max(0.001, tip(p.frame(u)) / 61.0), "dx": (tip(p.frame(u)) - 61) / 2.0}, "linear")
              for u in frames_of(6.0)]
    point = t.solid(t.track("shape", "Punta"), YELLOW, 0.0, 6.0, Box(614, 846, 61, 66), motion, kind="custom")
    point["shapeStyle"].update(customPath="M 0 0 L 100 0 L 0 100 Z", customEvenOdd=False)
    point["name"] = "Punta"
    p.text("produser", 220, 860, 893, role_width("produser"), 600, INK, "Cargo",
           reveal=lambda fr: (194, 846, max(194, low(fr) - 4), 912))
    return t


def jonatan():
    """Jonatan Miller: a tall label, yellow then white, the role coming up under the name."""
    t = _new("alta", "Tercio limpio: etiqueta alta con cargo", "Clean lower third: tall label with role", 8578,
             ["amarillo", "blanco"])
    p = Piece(t, 6.0)
    m = Measured("lt3-jonatan")
    acc, base_r = _label(p, m, Measured("lt3-jonatan-line"), 745, 918, 872, "Jonatan Miller", (251, 771, 829, 570),
                         band="role", base_box=(752, 911))
    _role_inside(p, "psychologist", 844, base_r, width=314, rise=(52, 70))
    return t


def jacob():
    """Jacob Stewart: grey then white, a yellow bar along the bottom of the label holding the role."""
    t = _new("barra-dentro", "Tercio limpio: cargo en barra amarilla dentro", "Clean lower third: role bar inside",
             8579, ["amarillo", "blanco", "gris"])
    p = Piece(t, 6.0)
    m = Measured("lt3-jacob")
    acc, base_r = _label(p, m, Measured("lt3-jacob-line"), 745, 918, 855, "Jacob Stewart", (253, 771, 829, 578),
                         accent=GREY, line_colour=GREY)
    bar = Measured("lt3-jacob-bar")
    r = held(bar.series("bar", ("yellow",), right_of(), lo=28), 194)
    p.rect("Barra", YELLOW, (194, 838, 848, 897), lambda fr: (194, 838, max(194, r(fr)), 897))
    p.text("produser", 252, 846, 879, 223, 600, INK, "Cargo", reveal=lambda fr: (194, 838, max(194, r(fr)), 897))
    return t


def alice():
    """Alice Moore: a short white label, a grey bar under it, the role showing in it at the end."""
    t = _new("barra-gris", "Tercio limpio: cargo en barra gris", "Clean lower third: role on a grey bar", 8580,
             ["blanco", "gris"])
    p = Piece(t, 6.0)
    m = Measured("lt3-alice")
    acc, base_r = _label(p, m, Measured("lt3-alice-line"), 757, 843, 721, "Alice Moore", (221, 771, 829, 477))
    g = held(m.series("role", ("grey",), right_of(196), lo=30), 194)
    p.rect("Barra", GREY, (194, 862, 507, 912), lambda fr: (194, 862, max(194, g(fr)), 912))
    clip = p.text("spa owner", 220, 871, 897, 262, 600, WHITE, "Cargo")
    clip["opacity"] = keys([(u, min(1.0, max(0.0, (p.frame(u) - 54) / 8.0)), "linear") for u in frames_of(6.0)])
    return t


SLOPE = 0.25  # the slanted labels lean right by a quarter of their height (14 degrees)


def _slanted_shape(t, p, name, colour, top, bottom, left_top, right_top, reveal_at, y_ref):
    """A parallelogram from left_top/right_top at `top` leaning SLOPE, uncovered from the left by an edge of the same
    slant whose position at y_ref is reveal_at(frame) (a rotated rectangle mask)."""
    import math
    h = bottom - top
    lb, rb = left_top - SLOPE * h, right_top - SLOPE * h
    x0, x1 = lb, right_top
    box = Box(x0, top, x1 - x0, h)

    def P(x, y):
        return f"{(x - x0) / box.w * 100:.3f} {(y - top) / h * 100:.3f}"
    path = f"M {P(left_top, top)} L {P(right_top, top)} L {P(rb, bottom)} L {P(lb, bottom)} Z"
    clip = t.solid(t.track("shape", name), colour, 0.0, p.dur, box, kind="custom")
    clip["shapeStyle"].update(customPath=path, customEvenOdd=False)
    clip["name"] = name
    track = next(tr for tr in t.tracks if clip in tr.clips)
    theta = math.degrees(math.atan(SLOPE))
    W = 4000.0
    nx, ny = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    xs, ys = [], []
    for u in frames_of(p.dur):
        ex, ey = reveal_at(p.frame(u)) - x0, y_ref - top
        cx, cy = ex - nx * W / 2, ey - ny * W / 2
        xs.append((u, cx / box.w, "linear"))
        ys.append((u, cy / h, "linear"))
    t.mask(track, clip, "rectangle", x=xs[0][1], y=ys[0][1], w=W / box.w, h=W / h, rotation=theta,
           keyframes={"x": keys(xs), "y": keys(ys)})
    return clip


def _slanted(p, t, m, top, bottom, stripe_left, stripe_w, right_top, accent, base, y_ref, line_frames):
    """A slanted label: the stripe grows up from the bottom, the accent block and the base sweep across."""
    edge = stripe_left + stripe_w
    a = held(m.series("a", (_KIND[accent],), right_of(edge)), edge)
    b = held(m.series("a", (_KIND[base],), right_of(edge)), edge)
    f0, f1 = line_frames

    def grow(fr):
        return min(1.0, max(0.0, (fr - f0) / max(1, f1 - f0)))
    stripe = _slanted_shape(t, p, "Línea", YELLOW, top, bottom, stripe_left, edge, lambda fr: 99999, y_ref)
    # The stripe grows up from the bottom: a second, upright mask over the slanted one.
    track = next(tr for tr in t.tracks if stripe in tr.clips)
    t.mask(track, stripe, "rectangle", x=0.5, y=1.0, w=1.2, h=0.0,
           keyframes={"y": keys([(u, 1 - grow(p.frame(u)) / 2, "linear") for u in frames_of(p.dur)]),
                      "h": keys([(u, grow(p.frame(u)), "linear") for u in frames_of(p.dur)])})
    _slanted_shape(t, p, "Bloque", accent, top, bottom, edge, right_top, a, y_ref)
    _slanted_shape(t, p, "Etiqueta", base, top, bottom, edge, right_top, b, y_ref)
    return a, b


def laureen():
    """Laureen Marlene: everything leaning right: a slanted yellow line, a yellow block, a white label."""
    t = _new("inclinada", "Tercio limpio: etiqueta inclinada", "Clean lower third: slanted label", 8581,
             ["amarillo", "blanco", "inclinado"])
    p = Piece(t, 6.0)
    m = Measured("lt3-laureen-slope")
    # At y 745 the stripe starts at 215 (211 at y 761), 10 px wide; the label's right top at 987.
    a, b = _slanted(p, t, m, 745, 918, 215, 10, 987, YELLOW, WHITE, 761, (2, 12))

    def shown(fr):
        return (205, 745, max(a(fr), b(fr)) - 4, 918)
    p.text("Laureen Marlene", 251, 771, 829, 671, 700, INK, "Nombre", reveal=shown, grow=1.06)
    p.text("school teacher", 249, 845, 879, 369, 600, INK, "Cargo", reveal=shown)
    return t


def leona():
    """Leona Goodwin: a slanted grey label with the name in white and a yellow stripe on the left; the role in white
    under it."""
    t = _new("inclinada-gris", "Tercio limpio: etiqueta gris inclinada", "Clean lower third: slanted grey label",
             8582, ["gris", "inclinado"])
    p = Piece(t, 6.0)
    m = Measured("lt3-leona-slope")
    a, b = _slanted(p, t, m, 757, 843, 220, 7, 897, YELLOW, GREY, 763, (3, 13))

    def shown(fr):
        return (205, 757, max(a(fr), b(fr)) - 4, 843)
    p.text("Leona Goodwin", 238, 771, 829, 621, 700, WHITE, "Nombre", reveal=shown, grow=1.06)
    # Dark where the yellow block runs ahead of the grey, as the reference reads.
    p.text("Leona Goodwin", 238, 771, 829, 621, 700, INK, "Nombre sobre amarillo", editable=False, grow=1.06,
           reveal=lambda fr: (max(205, b(fr)), 757, max(205, a(fr)) - 4, 843))
    # The role comes down from behind the label (frames 20-32).
    slide = held({16: -90, 20: -48, 24: -22, 28: -8, 32: 0}, -90)
    p.text("Managing Director", 200, 859, 893, role_width("Managing Director", 500), 500, WHITE, "Cargo",
           slide=slide, reveal=lambda fr: (150, 846, 1000, 930))
    return t


TEMPLATES = [clarke, bond, nigel, cornelius, jonatan, laureen, leona, alice, jacob]
