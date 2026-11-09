"""Layout roles and the app's overlay fit, for templates that must work in a Short and in a normal video
(2026-11-08, Jorge: «todo lo que hemos creado tiene que poderse adaptar a horizontal y short»).

`assign_roles(doc)` marks every visual clip of a project document with `layoutRole`: "backdrop" for what goes on
covering the frame (a background, a transition shape that sweeps across it, a giant word behind), "art" for the
design. The app (`SceneTemplateLayout.cpp`, `fitOverlayLayout`) stretches backdrops with the frame and scales and
places the art; `fit_doc` does the same here, so the Short version of a template can be rendered and looked at
before the app is built.
"""

from __future__ import annotations

import copy
import math


def _keys(clip, name, implicit):
    track = clip.get(name)
    if not track or not track.get("keyframes"):
        return None, implicit
    return track["keyframes"], implicit


def _value_at(clip, name, t, implicit):
    track = clip.get(name)
    if not track or not track.get("keyframes"):
        return implicit
    keys = track["keyframes"]
    if t <= keys[0]["timeUs"]:
        return keys[0]["value"]
    for a, b in zip(keys, keys[1:]):
        if a["timeUs"] <= t <= b["timeUs"]:
            span = b["timeUs"] - a["timeUs"]
            return a["value"] if span <= 0 else a["value"] + (b["value"] - a["value"]) * (t - a["timeUs"]) / span
    return keys[-1]["value"]


def _times(clip):
    out = {0}
    for name in ("x", "y", "width", "height"):
        track = clip.get(name)
        if track and track.get("keyframes"):
            out.update(k["timeUs"] for k in track["keyframes"])
    return sorted(out)


def _visual(clip):
    return clip.get("type") not in ("audio", "adjustment", "composite")


def _boxes(clip, W, H):
    for t in _times(clip):
        x = _value_at(clip, "x", t, 0.0)
        y = _value_at(clip, "y", t, 0.0)
        w = _value_at(clip, "width", t, W)
        h = _value_at(clip, "height", t, H)
        rot = math.radians(_value_at(clip, "rotation", t, 0.0))
        yield t, x, y, w, h, rot


def _spans(x, y, w, h, rot, W, H):
    cx, cy = x + w / 2, y + h / 2
    ex = abs(w / 2 * math.cos(rot)) + abs(h / 2 * math.sin(rot))
    ey = abs(w / 2 * math.sin(rot)) + abs(h / 2 * math.cos(rot))
    across = cx - ex <= 2 and cx + ex >= W - 2
    down = cy - ey <= 2 and cy + ey >= H - 2
    turned = abs(math.sin(rot)) > 0.05
    spans = (across and down) or (across and (turned or ey * 2 >= H * 0.3)) or (down and (turned or ex * 2 >= W * 0.3))
    outside = cx + ex <= 0 or cx - ex >= W or cy + ey <= 0 or cy - ey >= H or w <= 0.5 or h <= 0.5
    return spans, outside, ex, ey


def guess_role(clip, W, H):
    """What a clip is to the layout, judged where the title holds (the middle of the clip). "backdrop": a shape or
    picture that there covers the frame or crosses it (as a turned sweep or a panel at least 30 % deep), or that
    crossed it during the transition and is out of the frame by then; a word wider or taller than the frame by 15 %
    (a giant word behind, a wall of words). "art": the rest (a full-width bar of a lower third, a square that opens
    from the whole frame and settles in the middle)."""
    if clip.get("name", "").startswith("Fondo"):
        return "backdrop"
    text = clip.get("type") in ("text", "subtitle")
    boxes = list(_boxes(clip, W, H))
    if text:
        # A text clip's box is wider than its ink, so its size says little: a word behind is named so by the
        # slide helpers («Fondo (texto)», «Trama …», «Fila …») or set in letters as tall as most of the frame.
        name = clip.get("name", "")
        size = clip.get("textStyle", {}).get("pixelSize", 0)
        if name.startswith(("Trama", "Fila")) or size >= 0.6 * min(W, H):
            return "backdrop"
        return "art"
    spans_ever = any(_spans(x, y, w, h, rot, W, H)[0] for _, x, y, w, h, rot in boxes)
    big_ever = any(w >= W * 0.3 or h >= H * 0.3 for _, _, _, w, h, _ in boxes)
    mid = clip.get("timelineDurationUs", 0) / 2
    x = _value_at(clip, "x", mid, 0.0)
    y = _value_at(clip, "y", mid, 0.0)
    w = _value_at(clip, "width", mid, W)
    h = _value_at(clip, "height", mid, H)
    rot = math.radians(_value_at(clip, "rotation", mid, 0.0))
    spans, outside, _, _ = _spans(x, y, w, h, rot, W, H)
    faded = _value_at(clip, "opacity", mid, 1.0) < 0.02
    if spans or (outside and (spans_ever or big_ever)) or (faded and spans_ever):
        return "backdrop"
    return "art"


def assign_roles(doc):
    W, H = doc["width"], doc["height"]
    for track in doc["tracks"]:
        for clip in track.get("clips", []):
            if _visual(clip) and "layoutRole" not in clip:
                clip["layoutRole"] = guess_role(clip, W, H)
    return doc


# --- the app's fitOverlayLayout, in Python ---------------------------------------------------------------------

def _map_track(clip, name, scale, offset, implicit):
    track = clip.get(name)
    if not track or not track.get("keyframes"):
        clip[name] = {"keyframes": [{"timeUs": 0, "value": implicit * scale + offset}]}
        return
    for k in track["keyframes"]:
        k["value"] = k["value"] * scale + offset
        for d in ("inDy", "outDy"):
            if d in k:
                k[d] *= scale


def _scale_text(style, f):
    style["pixelSize"] = max(1.0, style.get("pixelSize", 48) * f)
    for key in ("letterSpacing", "wordSpacing", "boxPadding", "boxRadius", "underlineWidth", "underlineOffset"):
        if key in style:
            style[key] *= f
    for layer in style.get("layers", []) or []:
        for key in ("offsetX", "offsetY", "width", "blur"):
            if key in layer:
                layer[key] *= f
    kf = style.get("keyframes", {}).get("pixelSize")
    if kf and kf.get("keyframes"):
        for k in kf["keyframes"]:
            k["value"] *= f


def fit_doc(doc, toW, toH, fit="keep"):
    """A copy of doc fitted into toW×toH as the app fits a kit overlay (fit "keep" or "lowerthird")."""
    doc = copy.deepcopy(doc)
    W, H = doc["width"], doc["height"]
    art = None
    backdrops = []
    for track in doc["tracks"]:
        for clip in track.get("clips", []):
            if not _visual(clip):
                continue
            role = clip.get("layoutRole", "")
            text = clip.get("type") in ("text", "subtitle")
            covers = all(w >= W * 0.98 and h >= H * 0.98 for _, _, _, w, h, _ in _boxes(clip, W, H))
            if role == "backdrop" or (not role and not text and covers):
                backdrops.append(clip)
                continue
            for _, x, y, w, h, _ in _boxes(clip, W, H):
                x0, y0, x1, y1 = max(0, min(x, x + w)), max(0, min(y, y + h)), min(W, max(x, x + w)), min(H, max(y, y + h))
                if x1 <= x0 or y1 <= y0 or (x1 - x0 >= W * 0.98 and y1 - y0 >= H * 0.98):
                    continue
                art = (x0, y0, x1, y1) if art is None else (min(art[0], x0), min(art[1], y0), max(art[2], x1),
                                                            max(art[3], y1))
    if art is None:
        s = min(toW / W, toH / H)
        scale, ox, oy = s, (toW - W * s) / 2, (toH - H * s) / 2
    else:
        aw, ah = art[2] - art[0], art[3] - art[1]
        tall = toH > toW
        if fit == "lowerthird":
            scale = min(2.0, min(toW * 0.92 / aw, toH * 0.34 / ah))
            ox = (toW - aw * scale) / 2 - art[0] * scale
            bottom = toH * 0.74 if tall else toH * 0.88
            oy = bottom - art[3] * scale
        else:
            safe = (toW * 0.04, toH * 0.06, toW * 0.92, toH * 0.74) if tall else (toW * 0.04, toH * 0.05, toW * 0.92,
                                                                                    toH * 0.90)
            short = min(toW, toH) / max(1, min(W, H))
            scale = min(min(2.0, short), min(safe[2] / aw, safe[3] / ah))
            w, h = aw * scale, ah * scale
            x = (art[0] + aw / 2) / W * toW - w / 2
            y = (art[1] + ah / 2) / H * toH - h / 2
            x = min(max(safe[0], x), safe[0] + safe[2] - w)
            y = min(max(safe[1], y), safe[1] + safe[3] - h)
            ox, oy = x - art[0] * scale, y - art[1] * scale
    sx, sy = toW / W, toH / H
    leave = set()
    for clip in backdrops:
        leave.add(id(clip))
        if clip.get("type") in ("text", "subtitle"):
            w0 = _value_at(clip, "width", 0, W)
            h0 = _value_at(clip, "height", 0, H)
            _map_track(clip, "x", 1.0, (sx - 1) * (_value_at(clip, "x", 0, 0.0) + w0 / 2), 0.0)
            _map_track(clip, "y", 1.0, (sy - 1) * (_value_at(clip, "y", 0, 0.0) + h0 / 2), 0.0)
            continue
        _map_track(clip, "x", sx, 0, 0.0)
        _map_track(clip, "y", sy, 0, 0.0)
        _map_track(clip, "width", sx, 0, W)
        _map_track(clip, "height", sy, 0, H)
    ids = {c.get("id") for c in backdrops}
    for track in doc["tracks"]:
        for clip in track.get("clips", []):
            if clip.get("type") == "adjustment" and clip.get("adjustmentKind") == "mask" and clip.get("linkedClipId") in ids:
                m = clip["mask"]
                for key, horiz, size in (("x", True, False), ("y", False, False), ("w", True, True), ("h", False, True)):
                    frm, to, off = (W, toW, ox) if horiz else (H, toH, oy)
                    if key in m:
                        m[key] = m[key] * frm * scale / to + (0 if size else off / to)
                    kf = m.get("keyframes", {}).get(key)
                    if kf and kf.get("keyframes"):
                        for k in kf["keyframes"]:
                            k["value"] = k["value"] * frm * scale / to + (0 if size else off / to)
    for track in doc["tracks"]:
        for clip in track.get("clips", []):
            if not _visual(clip) or id(clip) in leave:
                continue
            _map_track(clip, "x", scale, ox, 0.0)
            _map_track(clip, "y", scale, oy, 0.0)
            _map_track(clip, "width", scale, 0, W)
            _map_track(clip, "height", scale, 0, H)
            if clip.get("type") in ("text", "subtitle") and "textStyle" in clip:
                _scale_text(clip["textStyle"], scale)
            elif clip.get("type") == "shape" and "shapeStyle" in clip:
                clip["shapeStyle"]["cornerRadius"] = clip["shapeStyle"].get("cornerRadius", 0) * scale
    doc["width"], doc["height"] = toW, toH
    return doc
