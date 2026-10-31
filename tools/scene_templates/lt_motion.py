"""Tools for lower thirds copied frame by frame from a reference (2026-10-30, Jorge: «lo más parecido posible, no
inventes»): edges that follow measured curves (a bar opens behind a white leading block), text that slides out from
behind an edge (a rectangle mask on the text clip, the slide as an inline text animator), and letters typed one at a
time that grow from small and grey. Every curve is sampled once a frame into linear keys, so the motion is exactly
the measured one and the exit is the entrance played backwards.
"""

from __future__ import annotations

import math
from pathlib import Path

from kit import Box, fill, label, no_stroke, tanim
from scene import us

FPS = 30.0
FONT = "Anybody Expanded"
_FONT_DIR = Path(__file__).resolve().parents[4] / "codigo" / "flip-addons" / "build" / "stage" / "fonts.extra" / "fonts" / "anybodyexpanded"
_FACES = {500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}

ORANGE = "#F39405"
MID = "#D9461A"
RED = "#C00026"


def text_width(text: str, size: float, weight: int = 900, spacing: float = 0.0) -> float:
    from PIL import ImageFont
    font = ImageFont.truetype(str(_FONT_DIR / f"AnybodyExpanded-{_FACES[weight]}.ttf"), round(size))
    return font.getlength(text) + spacing * max(0, len(text) - 1)


def fit_size(text: str, width: float, weight: int = 900) -> float:
    """The font size at which `text` is `width` px wide (what the reference measures)."""
    return round(width / text_width(text, 100, weight) * 100, 1)


# --- Curves -----------------------------------------------------------------------------------------------------------

def _ease(kind: str, u: float) -> float:
    u = min(1.0, max(0.0, u))
    if kind == "in":
        return u ** 3
    if kind == "out":
        return 1 - (1 - u) ** 3
    if kind == "inout":
        return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    if kind == "expo":
        return 1.0 if u >= 1 else 1 - 2 ** (-10 * u)
    if kind == "hold":
        return 0.0
    return u


def curve(points):
    """points: [(t, value, ease_to_next), ...] -> f(t)."""
    def f(t):
        if t <= points[0][0]:
            return points[0][1]
        for a, b in zip(points, points[1:]):
            if t <= b[0]:
                k = a[2] if len(a) > 2 else "linear"
                return a[1] + (b[1] - a[1]) * _ease(k, (t - a[0]) / (b[0] - a[0]))
        return points[-1][1]
    return f


def _times(t_in, t_out, dur):
    """Frame times covering the entrance [0, t_in] and the exit [dur - t_out, dur]."""
    n_in = max(1, round(t_in * FPS))
    n_out = max(1, round(t_out * FPS))
    a = [i / FPS for i in range(n_in + 1)]
    b = [dur - t_out + i / FPS for i in range(n_out + 1)]
    return a + b


def span(t, track, box: Box, lo, hi, dur, t_in, t_out=None, axis="x", layers=None, colour="#FFFFFF", t0=0.0, name=None):
    """A rectangle that covers [lo(t), hi(t)] of `box` along `axis` (px from the box's start) during the
    entrance; the exit is the entrance backwards. Zero-size frames have no width, so nothing shows."""
    t_out = t_in if t_out is None else t_out
    full = box.w if axis == "x" else box.h
    motion = []
    for tt in _times(t_in, t_out, dur):
        u = tt if tt <= t_in else (dur - tt) * t_in / t_out if tt >= dur - t_out else t_in
        a, b = lo(u), hi(u)
        a, b = max(0.0, min(full, a)), max(0.0, min(full, b))
        size = max(0.0, b - a)
        centre = (a + b) / 2 - full / 2
        if axis == "x":
            motion.append((tt, {"sx": size / full, "dx": centre}, "linear"))
        else:
            motion.append((tt, {"sy": size / full, "dy": centre}, "linear"))
    clip = t.solid(track, colour, t0, dur, box, motion, layers=layers)
    if name:
        clip["label"] = name
    return clip


def gradient_fill(angle=0.0):
    from scene import gradient
    return [gradient([(0.0, ORANGE), (0.5, MID), (1.0, RED)], angle=angle), no_stroke()]


# --- Text animations --------------------------------------------------------------------------------------------------

def _sel(stagger, duration, order="forward", ease="easeOut", domain="chars"):
    return {"driver": "stagger", "domain": domain, "staggerUs": us(stagger), "durationUs": us(duration),
            "order": order, "ease": ease}


def typing(stagger=0.07, grow=0.14, scale=35, grey="#FF8C8C8C", order="forward", delay=0.0):
    """Each letter pops in small and grey, then grows to full size and its own colour (the reference's typing)."""
    slot = {"animators": [
        {"selectors": [_sel(stagger, 0.0, order, "linear")], "props": {"opacity": 0}},
        {"selectors": [_sel(stagger, grow, order, "easeOut")], "props": {"scaleX": scale, "scaleY": scale, "fillColor": grey}},
    ]}
    if delay:
        slot["delayUs"] = us(delay)
    return slot


def slide(dx=0.0, dy=0.0, duration=0.5, ease="easeOut", delay=0.0, domain="all", stagger=0.0):
    """The whole text (or each word) moves in from (dx, dy) px; a mask on the clip hides what is past the edge."""
    slot = {"animators": [{"selectors": [_sel(stagger, duration, "forward", ease, domain)],
                           "props": {"position": {"x": dx, "y": dy, "unit": "px"}}}]}
    if delay:
        slot["delayUs"] = us(delay)
    return slot


def out_of(slot, delay=0.0):
    """The exit slot: the same animators, letters in the opposite order — the entrance backwards, as in the
    reference."""
    import copy
    s = copy.deepcopy(slot)
    s.pop("delayUs", None)
    if delay:
        s["delayUs"] = us(delay)
    for a in s["animators"]:
        for sel in a["selectors"]:
            # Rendered: with the same order the first letter left first; the reference takes the last one first.
            if sel.get("domain") != "all":
                sel["order"] = "backward" if sel.get("order", "forward") == "forward" else "forward"
            if sel.get("ease") == "easeOut":
                sel["ease"] = "easeIn"
    return s


def text(t, content, box, size, colour="#FFFFFF", weight=900, align="left", t0=0.0, dur=5.0, anim_in=None,
         anim_out=None, name=None, spacing=0.0, layers=None, mask: Box | None = None, line=1.0):
    clip = label(t, t.track("text", name or "Texto"), content, t0, dur, box, FONT, size, colour, weight=weight,
                 align=align, anim_in=anim_in, anim_out=anim_out, name=name or content, spacing=spacing, line=line,
                 layers=layers)
    if mask is not None:
        track = next(tr for tr in t.tracks if clip in tr.clips)
        t.mask(track, clip, "rectangle", x=(mask.cx - box.x) / box.w, y=(mask.cy - box.y) / box.h,
               w=mask.w / box.w, h=mask.h / box.h)
    return clip


def slid_text(t, content, box, size, offset, dur, t_in, t_out=None, mask: Box | None = None, colour="#FFFFFF",
              weight=900, align="left", name=None, spacing=0.0, layers=None, anim_in=None, anim_out=None, line=1.0):
    """A text that slides into place from `offset(u)` = (dx, dy) px, u the time since the start of the entrance (the
    exit is the entrance backwards), hidden past the edges of `mask` (screen px). The clip itself moves and its
    rectangle mask moves the other way, so the mask stays put on screen."""
    from scene import keys
    t_out = t_in if t_out is None else t_out
    motion, mx, my = [], [], []
    for tt in _times(t_in, t_out, dur):
        u = tt if tt <= t_in else (dur - tt) * t_in / t_out if tt >= dur - t_out else t_in
        dx, dy = offset(u)
        motion.append((tt, {"dx": dx, "dy": dy}, "linear"))
        if mask is not None:
            mx.append((tt, (mask.cx - box.x - dx) / box.w, "linear"))
            my.append((tt, (mask.cy - box.y - dy) / box.h, "linear"))
    clip = label(t, t.track("text", name or "Texto"), content, 0.0, dur, box, FONT, size, colour, weight=weight,
                 align=align, anim_in=anim_in, anim_out=anim_out, name=name or content, spacing=spacing, line=line,
                 layers=layers, motion=motion)
    if mask is not None:
        track = next(tr for tr in t.tracks if clip in tr.clips)
        t.mask(track, clip, "rectangle", x=mx[0][1], y=my[0][1], w=mask.w / box.w, h=mask.h / box.h,
               keyframes={"x": keys(mx), "y": keys(my)})
    return clip


def outline_layers(width=3.0, colour="#FFFFFF"):
    from scene import stroke
    s = stroke(width, colour)
    s["strokeAlign"] = "inside"
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}, s]


# --- Measured curves (lt_measure.py) ----------------------------------------------------------------------------------

class Ref:
    """One lower third measured on the reference: u = seconds since its first visible frame."""

    def __init__(self, name: str, first: int | None = None):
        import json
        data = json.loads((Path(__file__).with_name("lt_ref") / f"{name}.json").read_text(encoding="utf-8"))
        self.frames = data["frames"]
        if first is None:
            first = next(i for i, f in enumerate(self.frames)
                         if any(b["warm"] or b["white"] for b in f.values()))
        self.first = first

    def series(self, fn, frames=None):
        out = []
        lo, hi = frames if frames else (self.first, len(self.frames) - 1)
        for i in range(max(self.first, lo), min(len(self.frames) - 1, hi) + 1):
            v = fn(self.frames[i])
            if v is not None:
                out.append(((i - self.first) / FPS, float(v)))
        return out

    def curve(self, fn, before=None, after=None, offset=0.0, frames=None):
        pts = self.series(fn, frames)
        if not pts:
            return lambda u: (before if before is not None else 0.0) + offset
        first_u, first_v = pts[0]
        def f(u):
            if u < first_u:
                if before == "extrapolate" and len(pts) > 1:
                    (a, va), (b, vb) = pts[0], pts[1]
                    return va + (vb - va) * (u - a) / (b - a) + offset
                return (before if before is not None and before != "extrapolate" else first_v) + offset
            for (a, va), (b, vb) in zip(pts, pts[1:]):
                if u <= b:
                    return va + (vb - va) * (u - a) / (b - a) + offset
            if after == "extrapolate" and len(pts) > 1:
                (a, va), (b, vb) = pts[-2], pts[-1]
                return vb + (vb - va) * (u - b) / (b - a) + offset
            return (pts[-1][1] if after is None else after) + offset
        return f

    @staticmethod
    def edge(band, kind="warm", side="max", below=None):
        """fn(frame) -> the band's outermost run edge of `kind` (or None); `below` = only runs ending before that."""
        def fn(frame):
            rs = frame[band][kind]
            if below is not None:
                lim = below(frame)
                if lim is not None:
                    rs = [r for r in rs if r[1] < lim]
            if not rs:
                return None
            return max(r[1] for r in rs) if side == "max" else min(r[0] for r in rs)
        return fn


def caps_box(x, caps_centre, size, width=1600.0, align="left"):
    """A text box whose capitals are centred on `caps_centre` (rendered: the caps sit 0.1 em above the box centre)."""
    h = size * 1.3
    left = x if align == "left" else x - width
    return Box(left, caps_centre + 0.1 * size - h / 2, width, h)


# --- Whole-timeline playback of the measurements -----------------------------------------------------------------------

def frames_of(dur):
    n = int(round(dur * FPS))
    return [i / FPS for i in range(n + 1)]


def track_span(t, track, box: Box, lo, hi, dur, axis="x", layers=None, colour="#FFFFFF", name=None):
    """A rectangle covering [lo(u), hi(u)] px of `box` along `axis`, u = seconds since the clip start, every frame."""
    full = box.w if axis == "x" else box.h
    motion = []
    for u in frames_of(dur):
        a, b = max(0.0, min(full, lo(u))), max(0.0, min(full, hi(u)))
        size = max(0.0, b - a)
        centre = (a + b) / 2 - full / 2
        key = {"sx": size / full, "dx": centre} if axis == "x" else {"sy": size / full, "dy": centre}
        motion.append((u, key, "linear"))
    clip = t.solid(track, colour, 0.0, dur, box, motion, layers=layers)
    if name:
        clip["label"] = name
    return clip


def track_text(t, content, box, size, offset, dur, mask=None, colour="#FFFFFF", weight=900, align="left", name=None,
               spacing=0.0, layers=None, anim_in=None, anim_out=None, line=1.0):
    """A text moved by `offset(u)` = (dx, dy) px every frame; `mask(u)` = the screen Box it shows through (or None)."""
    from scene import keys
    motion, mk = [], {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(dur):
        dx, dy = offset(u)
        motion.append((u, {"dx": dx, "dy": dy}, "linear"))
        if mask is not None:
            m = mask(u)
            mk["x"].append((u, (m.cx - box.x - dx) / box.w, "linear"))
            mk["y"].append((u, (m.cy - box.y - dy) / box.h, "linear"))
            mk["w"].append((u, max(0.0, m.w) / box.w, "linear"))
            mk["h"].append((u, max(0.0, m.h) / box.h, "linear"))
    clip = label(t, t.track("text", name or "Texto"), content, 0.0, dur, box, FONT, size, colour, weight=weight,
                 align=align, anim_in=anim_in, anim_out=anim_out, name=name or content, spacing=spacing, line=line,
                 layers=layers, motion=motion)
    if mask is not None:
        track = next(tr for tr in t.tracks if clip in tr.clips)
        m0 = mask(0.0)
        t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
               keyframes={k: keys(v) for k, v in mk.items()})
    return clip


def run_where(band, kind="white", lo=None, hi=None, side="max", pick="last"):
    """fn(frame): the run of `kind` in `band` lying within [lo, hi] (px), its `side` edge — the text's own run."""
    def fn(frame):
        rs = [r for r in frame[band][kind] if (lo is None or r[0] >= lo) and (hi is None or r[1] <= hi)]
        if not rs:
            return None
        r = rs[-1] if pick == "last" else rs[0]
        return r[1] if side == "max" else r[0]
    return fn


def frame_at(ref: "Ref", u: float) -> dict | None:
    """The measured frame shown u seconds after the clip start (None past the measurement)."""
    i = ref.first + int(round(u * FPS))
    return ref.frames[i] if 0 <= i < len(ref.frames) else None


def last_frame(ref: "Ref") -> int:
    return max(i for i, f in enumerate(ref.frames) if any(b["warm"] or b["white"] for b in f.values()))


def measured_bar(t, ref, band, box, axis="x", white_on=True, name="Barra", clip_runs=None):
    """The reference's bar as two layers: the white edge (every white run of the band, from the first to the last)
    under the gradient (every warm run, first to last). Whatever white shows past the gradient is the leading block
    or a thin line, exactly where the reference has it."""
    origin = box.x if axis == "x" else box.y
    dur = (last_frame(ref) - ref.first + 2) / FPS

    def extent(kind):
        def lo(u):
            f = frame_at(ref, u)
            rs = [r for r in (f[band][kind] if f else []) if clip_runs is None or clip_runs(kind, r)]
            return min(r[0] for r in rs) - origin if rs else 0.0
        def hi(u):
            f = frame_at(ref, u)
            rs = [r for r in (f[band][kind] if f else []) if clip_runs is None or clip_runs(kind, r)]
            return max(r[1] for r in rs) + 1 - origin if rs else 0.0
        return lo, hi
    if white_on:
        lo, hi = extent("white")
        track_span(t, t.track("shape", "Borde"), box, lo, hi, dur, axis=axis, colour="#FFFFFF", name="Borde")
    lo, hi = extent("warm")
    track_span(t, t.track("shape", name), box, lo, hi, dur, axis=axis, layers=gradient_fill(), name=name)
    return dur
