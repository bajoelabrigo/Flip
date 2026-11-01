"""Tools for the logo lower thirds (2026-10-31), copied frame by frame from the second reference video Jorge sent
(15488414.mp4, 960×540 at 25 fps, measured scaled to 1080p by lt_measure.py fps=25): red bars and white edges whose
every frame is the measured one, texts that stay put and show only where the reference shows them (a rectangle mask
that follows a measured edge), and a logo slot where the reference has its logo.

Type (compared letter by letter with the reference's): Oswald ExtraLight, a little tighter, for the thin words and
Antonio Bold for the heavy ones — one text per line, the bold words as a run, so the user edits the whole name at
once.
"""

from __future__ import annotations

from pathlib import Path

from kit import Box, fill, label, no_stroke
from lt_motion import Ref, frame_at, last_frame
from scene import keys

FPS = 30.0  # the rate the keys are written at (the measurements are 25 fps; the curves join them)
FONT = "Oswald"        # ExtraLight: the reference's thin words (fonts.basic 1.1.0)
BOLD_FONT = "Antonio"  # Bold: its heavy words, as narrow as the reference's (fonts.extra 1.2.0)
RED = "#FB3B3A"
GREEN = "#70AC1B"
WHITE = "#FFFFFF"
_FONTS = Path(__file__).resolve().parents[4] / "codigo" / "flip-addons" / "build" / "stage"
_FILES = {("Oswald", 200): "fonts.basic/fonts/oswald/Oswald-ExtraLight.ttf",
          ("Oswald", 300): "fonts.basic/fonts/oswald/Oswald-Light.ttf",
          ("Oswald", 400): "fonts.basic/fonts/oswald/Oswald-Regular.ttf",
          ("Antonio", 700): "fonts.extra/fonts/antonio/Antonio-Bold.ttf"}
CAP = {"Oswald": 810 / 1000, "Antonio": 1760 / 2048}  # cap heights, em
BOLD_SCALE = round(CAP["Oswald"] / CAP["Antonio"], 4)  # the bold run's size: its capitals as tall as Oswald's
# Rendered (llt-francois) with Oswald: the capitals' height with their soft edges, how far below the box centre
# they sit (valign middle), and how far inside the box's left edge the line starts — all in em.
CAP_RENDER = 0.83
CAPS_DROP = 0.047
INSET = 0.04


def size_for_caps(px: float) -> float:
    """The font size whose capitals render `px` tall."""
    return round(px / CAP_RENDER, 1)


def _font(family: str, weight: int, size: float):
    from PIL import ImageFont
    return ImageFont.truetype(str(_FONTS / _FILES[(family, weight)]), max(1, round(size)))


def ink_extent(text: str, size: float, weight: int = 200, bold_from: str | None = None, spacing: float = 0.0,
               bold_spacing: float = 0.0):
    """(left, right) of the ink from the start of the line as the app lays it out: each run shaped whole (with its
    kerning), its own letter spacing after every letter; the bold words in Antonio Bold at BOLD_SCALE."""
    cut = text.rindex(bold_from) if bold_from else len(text)
    x, lo, hi = 0.0, None, 0.0
    for seg, f, sp in ((text[:cut], _font(FONT, weight, size), spacing),
                       (text[cut:], _font(BOLD_FONT, 700, size * BOLD_SCALE), bold_spacing)):
        if not seg:
            continue
        bb = f.getbbox(seg)
        lo = x + bb[0] if lo is None else lo
        hi = x + f.getlength(seg[:-1]) + sp * (len(seg) - 1) + f.getbbox(seg[-1])[2]
        x += f.getlength(seg) + sp * len(seg)
    return lo or 0.0, hi


def caps_box(ink_x: float, caps_top: float, caps_bottom: float, text: str, weight: int = 200, width: float = 1400.0,
             align: str = "left", spacing: float = 0.0, bold_from: str | None = None, bold_spacing: float = 0.0):
    """(box, size) for a text whose capitals span [caps_top, caps_bottom] and whose ink starts at `ink_x` (left), ends
    there (right) or is centred on it."""
    size = size_for_caps(caps_bottom - caps_top + 1)
    lo, hi = ink_extent(text, size, weight, bold_from, spacing, bold_spacing)
    centre = (caps_top + caps_bottom) / 2 - CAPS_DROP * size
    h = size * 1.5
    inset = INSET * size
    if align == "left":
        x = ink_x - lo - inset
    elif align == "right":
        x = ink_x - width + inset
    else:
        x = ink_x - width / 2
    return Box(x, centre - h / 2, width, h), size


def frames_of(dur):
    n = int(round(dur * FPS))
    return [i / FPS for i in range(n + 1)]


def duration(ref: Ref) -> float:
    import math
    return math.ceil((last_frame(ref) - ref.first + 2) / ref.fps * 100) / 100


def rect_track(t, track, box: Box, rect, dur, colour=WHITE, name=None, layers=None):
    """A solid inside `box` covering rect(u) = (x0, y0, x1, y1) screen px (x1/y1 one past), every frame."""
    motion = []
    for u in frames_of(dur):
        x0, y0, x1, y1 = rect(u)
        x0, x1 = max(box.x, min(box.x + box.w, x0)), max(box.x, min(box.x + box.w, x1))
        y0, y1 = max(box.y, min(box.y + box.h, y0)), max(box.y, min(box.y + box.h, y1))
        w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
        motion.append((u, {"sx": w / box.w, "sy": h / box.h, "dx": (x0 + x1) / 2 - box.cx,
                           "dy": (y0 + y1) / 2 - box.cy}, "linear"))
    clip = t.solid(track, colour, 0.0, dur, box, motion, layers=layers or [fill(colour), no_stroke()])
    if name:
        clip["name"] = name
    return clip


def mask_track(t, clip, box: Box, rect, dur, invert=False):
    """A rectangle mask on `clip` (laid out in `box`, not moving) that follows rect(u) = (x0, y0, x1, y1) screen px."""
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(dur):
        x0, y0, x1, y1 = rect(u)
        w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
        mk["x"].append((u, ((x0 + x1) / 2 - box.x) / box.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - box.y) / box.h, "linear"))
        mk["w"].append((u, w / box.w, "linear"))
        mk["h"].append((u, h / box.h, "linear"))
    t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           invert=invert, keyframes={k: keys(v) for k, v in mk.items()})


def name_text(t, content, box, size, dur, bold_from=None, weight=200, colour=WHITE, align="left", name="Nombre",
              motion=None, anim_in=None, anim_out=None, spacing=0.0, bold_spacing=0.0, word_spacing=0.0):
    """One line of Oswald ExtraLight; the words from `bold_from` (its last match) to the end in Antonio Bold, as a
    run, so the whole name is one text the user edits at once."""
    clip = label(t, t.track("text", name), content, 0.0, dur, box, FONT, size, colour, weight=weight, align=align,
                 name=name, line=1.0, motion=motion, anim_in=anim_in, anim_out=anim_out, spacing=spacing)
    if word_spacing:
        clip["textStyle"]["wordSpacing"] = word_spacing
    if bold_from:
        start = content.rindex(bold_from)
        clip["textStyle"]["runs"] = [{"start": start, "end": len(content), "boldEnabled": True, "bold": True,
                                      "fontEnabled": True, "fontFamily": BOLD_FONT, "sizeEnabled": True,
                                      "sizeScale": BOLD_SCALE, "letterSpacingEnabled": True,
                                      "letterSpacing": bold_spacing}]
    return clip


def edge(ref: Ref, band: str, kind: str, side: str, before, after=None):
    """u -> the band's outermost `kind` edge (side "min" = first pixel, "max" = one past the last), screen px."""
    fn = Ref.edge(band, kind, side)
    off = 1 if side == "max" else 0
    return ref.curve(fn, before=before - off if before is not None else None,
                     after=(after - off) if after is not None else None, offset=off)


def runs_at(ref: Ref, u: float, band: str, kind: str):
    f = frame_at(ref, u)
    return f[band][kind] if f else []


def effect_track(t, clip, box: Box, rect, dur, effects, name="Calado"):
    """An adjustment lane linked to `clip` (laid out in `box`, not moving) whose effects land only inside rect(u) =
    (x0, y0, x1, y1) screen px: the adjustment's own mask scopes them (FrameCompositor laneAdjustmentChain)."""
    from scene import Track, new_id
    track = next(tr for tr in t.tracks if clip in tr.clips)
    lane = Track(type="adjustment", name=name)
    lane.extra.update(adjustmentScope="parentTrack", parentTrackId=track.id)
    track.lanes.append(lane)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(dur):
        x0, y0, x1, y1 = rect(u)
        mk["x"].append((u, ((x0 + x1) / 2 - box.x) / box.w, "linear"))
        mk["y"].append((u, ((y0 + y1) / 2 - box.y) / box.h, "linear"))
        mk["w"].append((u, max(0.0, x1 - x0) / box.w, "linear"))
        mk["h"].append((u, max(0.0, y1 - y0) / box.h, "linear"))
    m = {"shape": "rectangle", "x": mk["x"][0][1], "y": mk["y"][0][1], "w": mk["w"][0][1], "h": mk["h"][0][1],
         "feather": 0, "enabled": True, "keyframes": {k: keys(v) for k, v in mk.items()}}
    lane.clips.append({"id": new_id("fx"), "type": "adjustment", "adjustmentKind": "videoEffects",
                       "linkedClipId": clip["id"], "timelineStartUs": clip["timelineStartUs"],
                       "timelineDurationUs": clip["timelineDurationUs"], "srcInUs": 0,
                       "srcOutUs": clip["timelineDurationUs"], "effects": effects, "mask": m, "name": name})
