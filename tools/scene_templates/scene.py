"""Building blocks for scene templates: a small Python layer over Flip's project document (see
FORMAT.md). A template is built bottom-up (background first), with clip times in seconds and boxes in
1080x1920 project pixels, and written twice: the package (`project.json`, slots empty) and a render
copy with the sample photos in the slots, which the app renders into the thumbnail and the preview.
"""

from __future__ import annotations

import copy
import itertools
import math
from dataclasses import dataclass, field
from pathlib import Path

W, H = 1080, 1920
US = 1_000_000

# Cubic-bezier easings (x1, y1, x2, y2), as CSS writes them.
EASES: dict[str, tuple[float, float, float, float] | None] = {
    "linear": None,
    "smooth": (0.33, 0.0, 0.67, 1.0),
    "out": (0.16, 1.0, 0.3, 1.0),       # fast start, long settle (easeOutExpo-ish)
    "in": (0.7, 0.0, 0.84, 0.0),
    "inout": (0.65, 0.0, 0.35, 1.0),
    "back": (0.34, 1.56, 0.64, 1.0),    # overshoots and settles
    "snap": (0.05, 0.9, 0.1, 1.0),      # a punch: there almost at once
}

_ids = itertools.count(1)


def new_id(prefix: str) -> str:
    return f"{prefix}{next(_ids)}"


def us(seconds: float) -> int:
    return int(round(seconds * US))


def argb(color: str, alpha: float = 1.0) -> str:
    """'#rrggbb' -> Qt's '#aarrggbb'."""
    return f"#{max(0, min(255, round(alpha * 255))):02x}{color.lstrip('#').lower()[-6:]}"


def keys(points: list[tuple]) -> dict:
    """[(t, value[, ease to the next key])] -> a keyframe object; t is clip-relative seconds."""
    out = [{"timeUs": us(p[0]), "value": float(p[1])} for p in points]
    for i in range(len(points) - 1):
        ease = points[i][2] if len(points[i]) > 2 else "linear"
        if ease == "hold":
            out[i]["hold"] = True
            continue
        curve = EASES[ease]
        if not curve:
            continue
        dt = us(points[i + 1][0]) - us(points[i][0])
        dv = float(points[i + 1][1]) - float(points[i][1])
        x1, y1, x2, y2 = curve
        out[i].update(outDx=x1 * dt, outDy=y1 * dv)
        out[i].setdefault("inDx", 0.0)
        out[i].setdefault("inDy", 0.0)
        out[i + 1].update(inDx=-(1 - x2) * dt, inDy=-(1 - y2) * dv, outDx=0.0, outDy=0.0)
    return {"keyframes": out}


def const(value: float) -> dict:
    return {"keyframes": [{"timeUs": 0, "value": float(value)}]}


# --- Paint layers (text and shapes share the model) --------------------------------------------


def fill(color: str, alpha: float = 1.0, id: str = "fill") -> dict:
    return {"id": id, "kind": "fill", "enabled": True, "paint": {"kind": "solid", "color": argb(color, alpha)}, "opacity": 1.0}


def gradient(stops: list[tuple], angle: float = 90.0, id: str = "fill") -> dict:
    """stops: (pos, '#rrggbb'[, alpha])."""
    colours = [argb(st[1], st[2] if len(st) > 2 else 1.0) for st in stops]
    return {"id": id, "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "gradient", "color": colours[0],
                      "gradient": {"kind": "linear", "stops": [{"pos": st[0], "color": c} for st, c in zip(stops, colours)],
                                   "angle": angle, "space": "block"}}}


def stroke(width: float, color: str = "#000000", alpha: float = 1.0, id: str = "stroke") -> dict:
    return {"id": id, "kind": "stroke", "enabled": True, "paint": {"kind": "solid", "color": argb(color, alpha)},
            "width": width, "opacity": 1.0, "strokeAlign": "outside"}


def shadow(color: str = "#000000", dx: float = 0, dy: float = 6, blur: float = 14, opacity: float = 0.5, id: str = "shadow") -> dict:
    return {"id": id, "kind": "shadow", "enabled": True, "paint": {"kind": "solid", "color": argb(color)},
            "offsetX": dx, "offsetY": dy, "blur": blur, "opacity": opacity}


def glow(color: str, radius: float = 24, opacity: float = 0.8, id: str = "glow") -> dict:
    return {"id": id, "kind": "glow", "enabled": True, "paint": {"kind": "solid", "color": argb(color)},
            "blur": radius, "opacity": opacity}


def no_stroke() -> dict:
    return {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0, "strokeAlign": "inside",
            "paint": {"kind": "solid", "color": "#ffffffff"}}


# --- Text animation slots -----------------------------------------------------------------------


def tanim(preset: str, duration: float | None = None, unit: str | None = None, stagger: float | None = None,
          ease: str | None = None, delay: float = 0.0, **params) -> dict:
    p: dict = {}
    if duration is not None:
        p["duration"] = {"type": "scalar", "value": duration}
    if stagger is not None:
        p["stagger"] = {"type": "scalar", "value": stagger}
    if unit:
        p["unit"] = {"type": "text", "value": unit}
    if ease:
        p["ease"] = {"type": "text", "value": ease}
    for k, v in params.items():
        if isinstance(v, str) and v.startswith("#"):
            p[k] = {"type": "color", "value": v}
        elif isinstance(v, str) or isinstance(v, bool):
            p[k] = {"type": "text", "value": str(v).lower() if isinstance(v, bool) else v}
        else:
            p[k] = {"type": "scalar", "value": v}
    slot = {"preset": preset, "params": p}
    if delay:
        slot["delayUs"] = us(delay)
    return slot


def text_style(font: str, size: int, layers: list[dict], *, weight: int = 700, italic: bool = False,
               align: str = "center", valign: str = "middle", spacing: float = 0.0, line: float = 1.12,
               case: str = "none", box: tuple[str, float] | None = None, box_pad: float = 18, box_radius: float = 0,
               anim_in: dict | None = None, anim_out: dict | None = None, anim_loop: dict | None = None,
               accent: dict | None = None, keyframes: dict | None = None) -> dict:
    style = {
        "fontFamily": font, "pixelSize": size, "fontWeight": weight, "italic": italic, "layers": layers,
        "align": align, "valign": valign, "wordWrap": True, "lineHeight": line, "letterSpacing": spacing,
        "textCase": case, "boxEnabled": box is not None,
        "boxColor": argb(box[0], box[1]) if box else argb("#000000", 0.5),
        "boxPadding": box_pad, "boxRadius": box_radius,
        "accent": accent or {"rule": "none"}, "animation": {},
    }
    if anim_in:
        style["animation"]["in"] = anim_in
    if anim_out:
        style["animation"]["out"] = anim_out
    if anim_loop:
        style["animation"]["loop"] = anim_loop
    if keyframes:
        style["keyframes"] = keyframes  # e.g. {"pixelSize": keys([...])}
    return style


def shape_style(kind: str, layers: list[dict], radius: float = 0, **geometry) -> dict:
    style = {"kind": kind, "cornerRadius": radius, "layers": layers}
    style.update(geometry)
    return style


def effect(catalog_id: str, animated: dict | None = None, **params) -> dict:
    e = {"catalogId": catalog_id, "parameters": params, "enabled": True}
    if animated:
        e["paramKeyframes"] = animated
    return e


# --- Motion -------------------------------------------------------------------------------------


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


FULL = Box(0, 0, W, H)
# Horizontal templates (16:9, YouTube / Facebook): Template(..., size=WIDE).
WIDE = (1920, 1080)
FULL_H = Box(0, 0, 1920, 1080)
# Square posts (Facebook / Instagram feed): Template(..., size=SQUARE).
SQUARE = (1080, 1080)
FULL_S = Box(0, 0, 1080, 1080)


def centered(cx: float, cy: float, w: float, h: float) -> Box:
    return Box(cx - w / 2, cy - h / 2, w, h)


def layout(box: Box, motion: list[tuple] | None) -> dict:
    """x/y/width/height for a box that moves: motion = [(t, {"s": scale, "dx": .., "dy": ..}, ease)].
    Scale is about the box centre; dx/dy in pixels."""
    if not motion:
        return {"x": const(box.x), "y": const(box.y), "width": const(box.w), "height": const(box.h)}
    xs, ys, ws, hs = [], [], [], []
    for point in motion:
        t, m = point[0], point[1]
        ease = point[2] if len(point) > 2 else "linear"
        s = m.get("s", 1.0)
        sx = m.get("sx", s)
        sy = m.get("sy", s)
        w, h = box.w * sx, box.h * sy
        cx, cy = box.cx + m.get("dx", 0.0), box.cy + m.get("dy", 0.0)
        xs.append((t, cx - w / 2, ease))
        ys.append((t, cy - h / 2, ease))
        ws.append((t, w, ease))
        hs.append((t, h, ease))
    return {"x": keys(xs), "y": keys(ys), "width": keys(ws), "height": keys(hs)}


def anim(kind: str, duration: float = 0.4, curve: str = "smooth") -> dict:
    return {"kind": kind, "durationUs": us(duration), "curve": curve}


# --- Clips and tracks ---------------------------------------------------------------------------


@dataclass
class Slot:
    """A photo slot; `sample` names the sample photo the render copy shows in it."""
    id: str
    label: str
    sample: str


@dataclass
class Track:
    type: str
    clips: list[dict] = field(default_factory=list)
    transitions: list[dict] = field(default_factory=list)
    name: str = ""
    id: str = field(default_factory=lambda: new_id("t"))
    lanes: list["Track"] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        out = {"id": self.id, "type": self.type, "name": self.name, "clips": self.clips, "transitions": self.transitions}
        out.update(self.extra)
        return out


class Template:
    def __init__(self, id: str, es: str, en: str, category: str, duration: float, *, order: int = 0,
                 tags: list[str] | None = None, thumb_at: float | None = None, premium: bool = False,
                 background: str = "#000000", size: tuple[int, int] = (W, H)):
        self.id = id
        self.w, self.h = size
        self.full = Box(0, 0, self.w, self.h)
        self.names = {"es": es, "en": en}
        self.category = category
        self.duration = duration
        self.order = order
        self.tags = tags or []
        self.thumb_at = thumb_at if thumb_at is not None else duration * 0.55
        self.premium = premium
        self.background = background
        self.tracks: list[Track] = []  # bottom first
        self.slots: list[Slot] = []
        self.texts = 0
        self.music: tuple[str, float, float] | None = None  # (music id, start s, volume)
        self.assets: list[dict] = []

    # Tracks are added bottom-up: each new one draws over the ones before it.
    def track(self, type: str, name: str = "") -> Track:
        t = Track(type=type, name=name)
        self.tracks.append(t)
        return t

    def _clip(self, type: str, t0: float, dur: float, **extra) -> dict:
        clip = {"id": new_id("c"), "type": type, "timelineStartUs": us(t0), "timelineDurationUs": us(dur),
                "srcInUs": 0, "srcOutUs": us(dur)}
        clip.update(extra)
        return clip

    def solid(self, track: Track, color: str, t0: float = 0.0, dur: float | None = None, box: Box | None = None,
              motion=None, radius: float = 0, kind: str = "rectangle", alpha: float = 1.0, layers=None, **extra) -> dict:
        dur = self.duration - t0 if dur is None else dur
        box = self.full if box is None else box
        style = shape_style(kind, layers or [fill(color, alpha), no_stroke()], radius)
        clip = self._clip("shape", t0, dur, shapeStyle=style, **layout(box, motion))
        clip.update(extra)
        track.clips.append(clip)
        return clip

    def photo(self, track: Track, sample: str, t0: float, dur: float, box: Box | None = None, motion=None, *,
              label: str | None = None, slot: bool = True, reuse: str | None = None, **extra) -> dict:
        """A photo slot (or, slot=False, a fixed picture from the package's media). reuse="p2" shows slot
        p2's picture again: one fill fills every clip of that slot."""
        box = self.full if box is None else box
        clip = self._clip("image", t0, dur, **layout(box, motion))
        if reuse:
            first = next(s for s in self.slots if s.id == reuse)
            clip["placeholderId"] = first.id
            clip["placeholderLabel"] = first.label
            clip["_sample"] = first.sample
        elif slot:
            number = len(self.slots) + 1
            clip["placeholderId"] = f"p{number}"
            clip["placeholderLabel"] = label or f"Foto {number}"
            self.slots.append(Slot(clip["placeholderId"], clip["placeholderLabel"], sample))
            clip["_sample"] = sample
        else:
            clip["_media"] = sample
        clip.update(extra)
        track.clips.append(clip)
        return clip

    def text(self, track: Track, content: str, t0: float, dur: float, box: Box, style: dict, motion=None, *,
             label: str | None = None, editable: bool = True, **extra) -> dict:
        clip = self._clip("text", t0, dur, textContent=content, textStyle=style, **layout(box, motion))
        if editable:
            self.texts += 1
            clip["placeholderId"] = f"t{self.texts}"
            clip["placeholderLabel"] = label or content
        clip.update(extra)
        track.clips.append(clip)
        return clip

    def adjust(self, effects: list[dict], t0: float = 0.0, dur: float | None = None, name: str = "Ajuste") -> dict:
        dur = self.duration - t0 if dur is None else dur
        t = self.track("adjustment", name)
        t.extra["adjustmentScope"] = "allBelow"
        clip = self._clip("adjustment", t0, dur, adjustmentKind="videoEffects", effects=effects)
        t.clips.append(clip)
        return clip

    def mask(self, track: Track, host: dict, shape: str = "ellipse", feather: float = 0, **geometry) -> None:
        """Clips `host` (on `track`) to a shape, normalised to its box."""
        # Masks of clips in turn share one lane; one that would overlap gets a lane of its own.
        lane = next((l for l in track.lanes
                     if all(c["timelineStartUs"] + c["timelineDurationUs"] <= host["timelineStartUs"] for c in l.clips)),
                    None)
        if lane is None:
            lane = Track(type="adjustment", name="Máscara")
            lane.extra.update(adjustmentScope="parentTrack", parentTrackId=track.id)
            track.lanes.append(lane)
        m = {"shape": shape, "x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0, "feather": feather, "enabled": True}
        m.update(geometry)
        lane.clips.append({"id": new_id("m"), "type": "adjustment", "adjustmentKind": "mask",
                           "linkedClipId": host["id"], "timelineStartUs": host["timelineStartUs"],
                           "timelineDurationUs": host["timelineDurationUs"], "srcInUs": 0,
                           "srcOutUs": host["timelineDurationUs"], "mask": m})

    def transition(self, track: Track, a: dict, b: dict, kind: str = "crossfade", duration: float = 0.5, **params) -> None:
        track.transitions.append({"id": new_id("x"), "kind": kind, "fromClipId": a["id"], "toClipId": b["id"],
                                  "durationUs": us(duration), "parameters": params, "easingCurve": "smooth"})

    def song(self, music_id: str, start: float = 0.0, volume: float = 0.9) -> None:
        self.music = (music_id, start, volume)

    # --- Output ---------------------------------------------------------------------------------

    def _tracks_top_first(self) -> list[Track]:
        out: list[Track] = []
        for t in reversed(self.tracks):
            out.append(t)
            out.extend(t.lanes)  # a lane sits right after its parent in the list
        return out

    def document(self, *, render: bool, photo_size, sample_path, media_root: Path | None) -> dict:
        """The project document. render=True puts the sample photos in the slots, with absolute paths."""
        assets: list[dict] = []
        tracks = []
        for t in self._tracks_top_first():
            data = copy.deepcopy(t.to_json())
            for clip in data["clips"]:
                sample = clip.pop("_sample", None)
                media = clip.pop("_media", None)
                path = None
                if sample and render:
                    path = str(sample_path(sample))
                elif media:
                    path = str((media_root / media).resolve()) if (render and media_root) else f"media/{media}"
                if path:
                    pw, ph = photo_size(sample or media)
                    asset_id = new_id("a")
                    assets.append({"id": asset_id, "kind": "image", "name": Path(path).name, "path": path,
                                   "width": pw, "height": ph})
                    clip["assetId"] = asset_id
                    clip["path"] = path
                    box_w = clip["width"]["keyframes"][0]["value"]
                    box_h = clip["height"]["keyframes"][0]["value"]
                    clip["sourceFrame"] = cover(pw, ph, box_w, box_h)
                    if sample:
                        clip["placeholderEmpty"] = False
            tracks.append(data)
        if self.music:
            music_id, start, volume = self.music
            path = str((media_root / "music.m4a").resolve()) if (render and media_root) else "media/music.m4a"
            asset_id = new_id("a")
            assets.append({"id": asset_id, "kind": "audio", "name": "music.m4a", "path": path,
                           "durationUs": us(self.duration), "sampleRate": 48000, "channels": 2, "hasAudio": True})
            tracks.append({"id": new_id("t"), "type": "audio", "name": "Música", "transitions": [], "clips": [{
                "id": new_id("c"), "type": "audio", "assetId": asset_id, "path": path,
                "timelineStartUs": 0, "timelineDurationUs": us(self.duration), "srcInUs": 0,
                "srcOutUs": us(self.duration), "volume": volume, "fadeOutUs": us(min(1.0, self.duration / 4))}]})
        return {"version": 14, "projectName": self.names["es"], "width": self.w, "height": self.h, "fps": 30,
                "sampleRate": 48000, "background": {"kind": "color", "color": argb(self.background)},
                "assets": assets, "tracks": tracks}

    def manifest(self) -> dict:
        return {"id": self.id, "displayName": self.names["en"], "names": self.names, "category": self.category,
                "order": self.order, "width": self.w, "height": self.h, "durationSec": self.duration,
                "slots": len(self.slots), "texts": self.texts, "premium": self.premium, "tags": self.tags,
                "music": self.music[0] if self.music else None}


def cover(pw: float, ph: float, bw: float, bh: float) -> list[float]:
    """Normalised source rect that fills a bw x bh box from a pw x ph picture without stretching."""
    if pw <= 0 or ph <= 0 or bw <= 0 or bh <= 0:
        return [0, 0, 1, 1]
    media, box = pw / ph, bw / bh
    if media > box:
        w = box / media
        return [(1 - w) / 2, 0, w, 1]
    h = media / box
    # Portraits keep the upper part: faces sit there.
    return [0, max(0.0, (1 - h) * 0.35), 1, h]


def beat(n: float, bpm: float = 120.0) -> float:
    """Seconds of n beats."""
    return n * 60.0 / bpm
