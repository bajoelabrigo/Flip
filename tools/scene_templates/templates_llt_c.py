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


def _label(p, m, line_m, top, bottom, white_right, name, name_ink, line_from=0, accent=YELLOW, base=WHITE,
           name_colour=INK):
    """The common build: the line grows up from the bottom (x 194-199, stays as the left stripe) with a white glint
    running up inside it, the accent block widens to the right, the base sweeps in behind it; the name shows inside
    both."""
    line_top = held(line_m.series("line", ("yellow", "white"), top_of, lo=line_from), bottom, top)
    glint = line_m.series("line", ("white",),
                          lambda r: next(((a, b + 1) for a, b in r if a > top + 1 and b < bottom + 1), None),
                          lo=line_from)
    acc = held(m.series("top", ("yellow",) if accent == YELLOW else ("grey",), right_of()), 200)
    base_r = held(m.series("top", ("white",) if base == WHITE else ("yellow",), right_of(201)), 202, white_right)
    acc_last = max(m.series("top", ("yellow",) if accent == YELLOW else ("grey",), right_of()).values())
    p.rect("Línea", accent, (194, top, 200, bottom), lambda fr: (194, line_top(fr), 200, bottom))
    p.rect("Brillo", WHITE, (194, top, 200, bottom),
           lambda fr: (194, glint[int(fr)][0], 200, glint[int(fr)][1]) if int(fr) in glint else (194, bottom, 200, bottom))
    p.rect("Bloque", accent, (200, top, acc_last, bottom), lambda fr: (200, top, max(200, acc(fr)), bottom))
    p.rect("Etiqueta", base, (202, top, white_right, bottom), lambda fr: (202, top, max(202, base_r(fr)), bottom))
    shown = lambda fr: (200, top, max(acc(fr), base_r(fr)), bottom)  # noqa: E731
    p.text(name, *name_ink, 700, name_colour, "Nombre", reveal=shown, grow=1.06)
    return acc, base_r


def clarke():
    """Thomas Clarke: a tall white label (name and role inside), a yellow «exclusive guest» tag with a slanted end on
    top."""
    D = 6.0
    t = _kit("invitado", "Tercio limpio: etiqueta blanca con «invitado especial»",
             "Clean lower third: white label with a guest tag", D, 8574, ["nombre", "amarillo", "blanco", "invitado"],
             thumb_at=3.0)
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
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
    photo_bg(t, "h-city-01", s1=1.03, label="Tu video")
    p = Piece(t, D, first=10)
    m = Measured("lt3-bond")
    acc, base_r = _label(p, m, m, 757, 843, 809, "Thomas Bond", (222, 771, 829, 557), line_from=12)
    # Out from behind the label's bottom (frames 54-66): hidden above y 844 until then.
    slide = held({54: -64, 57: -30, 60: -12, 63: -3, 66: 0}, -64)
    p.text("technology officer", 195, 860, 893, 462, 600, YELLOW, "Cargo", slide=slide,
           reveal=lambda fr: (194, 844, 1000, 930))
    return t


TEMPLATES = [clarke, bond]
