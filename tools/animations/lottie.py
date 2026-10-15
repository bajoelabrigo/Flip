"""A small Lottie (Bodymovin JSON) writer for Flip Studio's own animated stickers.

Shapes only (no text, no images), so every file renders the same in Skottie and in the web
player. Colours that make sense to change are Lottie *slots* ("sid"): Flip's Motion inspector
lists them and lets the user recolour the sticker.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

EASE_OUT = ({"x": [0.16], "y": [1]}, {"x": [0.3], "y": [1]})
EASE_IN_OUT = ({"x": [0.65], "y": [0]}, {"x": [0.35], "y": [1]})
EASE_BACK = ({"x": [0.34], "y": [1.56]}, {"x": [0.64], "y": [1]})
LINEAR = ({"x": [0.0], "y": [0.0]}, {"x": [1.0], "y": [1.0]})


def rgb(hex_colour: str) -> list[float]:
    h = hex_colour.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1]


def static(value) -> dict:
    return {"a": 0, "k": value}


def anim(keys: list[tuple], ease=EASE_OUT) -> dict:
    """keys: [(frame, value[, ease to next])]; value a number or a list."""
    out = []
    for i, key in enumerate(keys):
        frame, value = key[0], key[1]
        s = value if isinstance(value, list) else [value]
        k = {"t": frame, "s": s}
        if i < len(keys) - 1:
            o, inn = key[2] if len(key) > 2 else ease
            k["o"] = {"x": o["x"] * len(s) if len(o["x"]) == 1 else o["x"], "y": o["y"] * len(s) if len(o["y"]) == 1 else o["y"]}
            k["i"] = {"x": inn["x"] * len(s) if len(inn["x"]) == 1 else inn["x"], "y": inn["y"] * len(s) if len(inn["y"]) == 1 else inn["y"]}
        out.append(k)
    return {"a": 1, "k": out}


def transform(p=(0, 0), s=100, r=0, o=100, a=(0, 0)) -> dict:
    """Group transform ("tr"). Values may be static or dicts from anim()."""
    def prop(v, as_list):
        if isinstance(v, dict):
            return v
        return static(list(v) if as_list else v)
    scale = s if isinstance(s, dict) else static([s, s])
    return {"ty": "tr", "p": prop(p, True), "a": prop(a, True), "s": scale, "r": prop(r, False),
            "o": prop(o, False), "sk": static(0), "sa": static(0)}


def layer_transform(p=(256, 256), s=100, r=0, o=100, a=(0, 0)) -> dict:
    def prop(v, n):
        if isinstance(v, dict):
            return v
        return static(list(v) + [0] * (n - len(v)) if isinstance(v, (list, tuple)) else v)
    scale = s if isinstance(s, dict) else static([s, s, 100])
    return {"o": prop(o, 0), "r": prop(r, 0), "p": prop(p, 3), "a": prop(a, 3), "s": scale}


def ellipse(size=(100, 100), p=(0, 0)) -> dict:
    return {"ty": "el", "p": static(list(p)) if not isinstance(p, dict) else p,
            "s": static(list(size)) if not isinstance(size, dict) else size, "d": 1}


def rect(size=(100, 100), p=(0, 0), r=0) -> dict:
    return {"ty": "rc", "p": static(list(p)), "s": static(list(size)) if not isinstance(size, dict) else size,
            "r": static(r) if not isinstance(r, dict) else r, "d": 1}


def star(points=5, outer=50, inner=22, p=(0, 0), roundness=0) -> dict:
    return {"ty": "sr", "sy": 1, "d": 1, "pt": static(points), "p": static(list(p)), "r": static(0),
            "ir": static(inner), "is": static(roundness), "or": static(outer), "os": static(roundness)}


def path(points: list[tuple[float, float]], closed=False, smooth=0.0) -> dict:
    """Polyline through points; smooth>0 rounds it with Catmull-Rom-ish tangents."""
    n = len(points)
    ins, outs = [], []
    for i, (x, y) in enumerate(points):
        if smooth and 0 < i < n - 1 or (smooth and closed):
            px, py = points[(i - 1) % n]
            nx, ny = points[(i + 1) % n]
            # Catmull-Rom to Bezier: a sixth of the neighbour-to-neighbour vector.
            tx, ty = (nx - px) * smooth / 6, (ny - py) * smooth / 6
            ins.append([-tx, -ty])
            outs.append([tx, ty])
        else:
            ins.append([0, 0])
            outs.append([0, 0])
    return {"ty": "sh", "ks": static({"c": closed, "v": [list(p) for p in points], "i": ins, "o": outs})}


def fill(colour: str, slot: str | None = None, o=100) -> dict:
    c = static(rgb(colour))
    if slot:
        c["sid"] = slot
    return {"ty": "fl", "c": c, "o": static(o) if not isinstance(o, dict) else o, "r": 1}


def stroke(colour: str, width=10, slot: str | None = None, o=100, cap=2) -> dict:
    c = static(rgb(colour))
    if slot:
        c["sid"] = slot
    return {"ty": "st", "c": c, "o": static(o) if not isinstance(o, dict) else o,
            "w": static(width) if not isinstance(width, dict) else width, "lc": cap, "lj": 2}


def trim(end: dict, start=None, offset=0) -> dict:
    return {"ty": "tm", "s": start if isinstance(start, dict) else static(start or 0), "e": end,
            "o": static(offset) if not isinstance(offset, dict) else offset, "m": 1}


def heart(colour: str, slot: str | None = None, size: float = 100) -> dict:
    """A heart as two circles over a diamond: the shape reads at any size and needs no curves."""
    k = size / 100
    lobe = 62 * k
    diamond = group(rect((62 * k, 62 * k)), tr=transform(p=(0, 6 * k), r=45))
    return group(ellipse((lobe, lobe), p=(-22 * k, -16 * k)), ellipse((lobe, lobe), p=(22 * k, -16 * k)),
                 diamond, fill(colour, slot), name="corazón")


def group(*items, tr=None, name="g") -> dict:
    return {"ty": "gr", "nm": name, "it": list(items) + [tr or transform()]}


@dataclass
class Sticker:
    id: str
    es: str
    en: str
    category: str
    frames: int = 60
    size: int = 512          # square stickers; `height` set makes it width=size x height
    height: int = 0
    fps: int = 30
    thumb: float = 0.5       # where the card is taken, as a fraction of the length
    tags: list[str] = field(default_factory=list)
    order: int = 0
    loop: bool = True
    layers: list[dict] = field(default_factory=list)
    slot_defaults: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        # A one-shot shows its finished state on the card.
        if not self.loop and self.thumb == 0.5:
            self.thumb = 0.95

    def layer(self, *shapes, ks=None, ip=0, op=None, name="capa") -> dict:
        lay = {"ddd": 0, "ind": len(self.layers) + 1, "ty": 4, "nm": name, "sr": 1,
               "ks": ks or layer_transform((self.size / 2, self.h / 2)), "ao": 0,
               "shapes": list(shapes), "ip": ip, "op": op if op is not None else self.frames, "st": 0, "bm": 0}
        self.layers.append(lay)
        return lay

    def slot(self, sid: str, colour: str) -> str:
        self.slot_defaults.setdefault(sid, colour)
        return sid

    def document(self) -> dict:
        doc = {"v": "5.7.4", "fr": self.fps, "ip": 0, "op": self.frames, "w": self.size, "h": self.h,
               "nm": self.names_es, "ddd": 0, "assets": [],
               # Lottie draws the first layer on top: we add bottom-up, so reverse.
               "layers": [dict(l, ind=i + 1) for i, l in enumerate(reversed(self.layers))]}
        if self.slot_defaults:
            doc["slots"] = {sid: {"p": static(rgb(c))} for sid, c in self.slot_defaults.items()}
        return doc

    @property
    def h(self) -> int:
        return self.height or self.size

    @property
    def names_es(self) -> str:
        return self.es

    def manifest(self) -> dict:
        return {"id": self.id, "names": {"es": self.es, "en": self.en}, "category": self.category,
                "order": self.order, "durationSec": self.frames / self.fps, "width": self.size, "height": self.h,
                "loop": self.loop, "tags": self.tags, "colors": list(self.slot_defaults)}


def polar(cx: float, cy: float, radius: float, degrees: float) -> tuple[float, float]:
    a = math.radians(degrees)
    return (cx + radius * math.cos(a), cy + radius * math.sin(a))
