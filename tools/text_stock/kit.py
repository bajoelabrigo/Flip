"""Building blocks for Stock's text content: text styles ("Mis estilos") and text animations.

A text style is the object `core/TextStyle.cpp` reads (textStyleFromJson), wrapped the way
`TextPresetStore::importFromFile` expects ({"label", "sampleText", "style"}). A text animation is a
preset recipe as `core/TextAnimationPreset.cpp` reads it (TextAnimationPreset::fromJson).

Every length a design states is a fraction of the font size (em), so a recipe reads the same at
60 px and 160 px; `Style.style_json()` turns them into the project pixels the app stores.
Colours are '#rrggbb' (or '#rrggbbaa' with alpha last, CSS-style); Qt wants '#aarrggbb' and
`argb()` converts.
"""

from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio"
ADDONS = ROOT / "codigo" / "flip-addons" / "build" / "stage"


# --- colours ------------------------------------------------------------------------------------

def argb(color: str, alpha: float | None = None) -> str:
    """'#rrggbb' or '#rrggbbaa' (CSS order) -> Qt's '#aarrggbb'."""
    c = color.lstrip("#").lower()
    if len(c) == 8:
        rgb, a = c[:6], int(c[6:], 16)
    else:
        rgb, a = c[-6:], 255
    if alpha is not None:
        a = max(0, min(255, round(alpha * 255)))
    return f"#{a:02x}{rgb}"


# --- shading layers (em units) ------------------------------------------------------------------
# The stack is back to front: shadows and glows first, then strokes (outer before inner), the fill last.

_EM_FIELDS = ("width", "blur", "offsetX", "offsetY", "spread")


def _layer(kind: str, paint: dict, id: str, **extra) -> dict:
    out = {"id": id, "kind": kind, "enabled": True, "paint": paint, "opacity": 1.0}
    out.update(extra)
    return out


def solid(color: str, alpha: float | None = None) -> dict:
    return {"kind": "solid", "color": argb(color, alpha)}


def grad(stops: list, angle: float = 90.0, kind: str = "linear", space: str = "block", speed: float = 0.0,
         repeat: bool = False, scale: float = 1.0, oklab: bool = True) -> dict:
    """stops: [(pos, colour)]; angle 90 = top -> bottom, 0 = left -> right."""
    out = {"kind": "gradient", "color": argb(stops[0][1]),
           "gradient": {"kind": kind, "stops": [{"pos": p, "color": argb(c)} for p, c in stops], "angle": angle,
                        "space": space, "oklab": oklab, "scale": scale, "repeat": repeat}}
    if speed:
        out["gradient"]["offsetSpeed"] = speed
    return out


def fx(effect: str, tint: str = "#ffffff", **params) -> dict:
    """A shader paint (TextShaderEffect): shine, shimmer, neon-pulse, glitch, chrome, dissolve."""
    p = {}
    for k, v in params.items():
        p[k] = {"type": "color", "value": argb(v)} if isinstance(v, str) else {"type": "scalar", "value": float(v)}
    return {"kind": "effect", "color": argb(tint), "effect": {"id": effect, "params": p}}


def fill(color="#ffffff", id: str = "fill", alpha: float | None = None, **extra) -> dict:
    paint = color if isinstance(color, dict) else solid(color, alpha)
    return _layer("fill", paint, id, **extra)


def hollow_fill(id: str = "fill") -> dict:
    """A see-through fill, for outline-only text (the stroke carries the letters)."""
    return _layer("fill", solid("#ffffff", 0.0), id)


def stroke(width: float, color="#000000", id: str = "stroke", align: str = "outside", **extra) -> dict:
    paint = color if isinstance(color, dict) else solid(color)
    return _layer("stroke", paint, id, width=width, strokeAlign=align, **extra)


def shadow(color: str = "#000000", dx: float = 0.0, dy: float = 0.06, blur: float = 0.12, opacity: float = 0.6,
           id: str = "shadow", **extra) -> dict:
    return _layer("shadow", solid(color), id, offsetX=dx, offsetY=dy, blur=blur, opacity=opacity, **extra)


def hard(color: str = "#000000", dx: float = 0.06, dy: float = 0.06, id: str = "shadow", opacity: float = 1.0) -> dict:
    """A hard drop shadow: no blur."""
    return shadow(color, dx, dy, 0.0, opacity, id=id)


def glow(color: str, radius: float = 0.3, opacity: float = 0.85, id: str = "glow", spread: float = 0.0) -> dict:
    return _layer("glow", solid(color), id, blur=radius, opacity=opacity, spread=spread)


def extrude(depth: float, color: str, id: str = "extrude", angle: float = 45.0, steps: int = 12,
            darken: float = 0.3) -> dict:
    return _layer("extrude", solid(color), id, width=depth, extrudeSteps=steps, extrudeAngle=angle,
                  extrudeDarken=darken)


def neon_stack(tube: str, core: str = "#ffffff", wide: float = 0.8, tight: float = 0.28, line: float = 0.035,
               pulse: bool = False) -> list:
    """A white core with a coloured halo, the way a neon tube reads on video."""
    face = fill(fx("neon-pulse", core, speed=1.1, intensity=0.3, flicker=0.25, colorA=tube)) if pulse else fill(core)
    return [glow(tube, wide, 0.55, id="glow2"), glow(tube, tight, 0.95), stroke(line, tube), face]


# --- the style ----------------------------------------------------------------------------------

def tslot(preset: str, duration: float | None = None, ease: str | None = None, unit: str | None = None,
          stagger: float | None = None, order: str | None = None, delay: float = 0.0, **params) -> dict:
    """An In / Out / Loop slot that names a built-in preset with param overrides."""
    p: dict = {}
    if duration is not None:
        p["duration"] = {"type": "scalar", "value": duration}
    if stagger is not None:
        p["stagger"] = {"type": "scalar", "value": stagger}
    for key, val in (("unit", unit), ("order", order), ("ease", ease)):
        if val:
            p[key] = {"type": "text", "value": val}
    for k, v in params.items():
        if isinstance(v, str) and v.startswith("#"):
            p[k] = {"type": "color", "value": argb(v)}
        elif isinstance(v, bool):
            p[k] = {"type": "scalar", "value": 1.0 if v else 0.0}
        elif isinstance(v, str):
            p[k] = {"type": "text", "value": v}
        else:
            p[k] = {"type": "scalar", "value": float(v)}
    out = {"preset": preset}
    if p:
        out["params"] = p
    if delay:
        out["delayUs"] = int(delay * 1_000_000)
    return out


def accent(rule: str, color: str | None = None, *, size: float = 1.0, n: int = 2, phase: int = 0,
           outline: tuple[float, str] | None = None, pill: str | None = None, pad: float = 0.12,
           radius: float = 0.12) -> dict:
    """The per-word look a pack gives the words its rule picks (karaoke, keywords, firstWord…).
    pad / radius / outline width in em."""
    a = {"rule": rule, "n": n, "phase": phase, "colorEnabled": color is not None,
         "color": argb(color or "#ffd640"), "sizeScale": size,
         "outlineEnabled": outline is not None, "outlineWidth": outline[0] if outline else 0.0,
         "outlineColor": argb(outline[1] if outline else "#000000"),
         "highlight": {"enabled": pill is not None, "color": argb(pill or "#e62828"), "padding": pad, "radius": radius}}
    return a


@dataclass
class Style:
    id: str
    es: str
    en: str
    category: str
    sample: tuple[str, str]           # (es, en) sample text shown on the card and in the picker
    font: str
    size: int                         # project px at 1080 x 1920
    weight: int = 700
    layers: list = field(default_factory=lambda: [fill("#ffffff")])
    italic: bool = False
    align: str = "center"
    valign: str = "middle"
    spacing: float = 0.0              # letter spacing, em
    line: float = 1.15
    case: str = "none"
    bend: float = 0.0                 # path bend -100..100
    box: str | None = None            # background colour ('#rrggbbaa' for alpha)
    box_style: str = "block"          # block | line
    box_shape: str = "rect"           # rect | pill | speech | burst | ribbon | tag | ...
    box_pad: tuple[float, float] = (0.35, 0.2)  # em
    box_radius: float = 0.0           # em
    box_offset: tuple[float, float] = (0.0, 0.0)
    box_border: tuple[float, str] | None = None
    word_bg: str | None = None        # pill behind every word
    word_bg_pad: float = 0.1
    word_bg_radius: float = 0.1
    underline: tuple[str, float, float] | None = None  # colour, width em, offset em
    acc: dict | None = None
    anim_in: dict | None = None
    anim_out: dict | None = None
    anim_loop: dict | None = None
    tags: list[str] = field(default_factory=list)
    subtitle: bool = False            # also listed with the caption styles
    card: str = "dark"                # dark | light | warm | cool | night | <#rrggbb>
    card_at: float = 1.6              # second of the 3 s render the card is taken at
    card_size: float = 1.0            # extra shrink for the card only (shapes that reach past the fit)

    def _px(self, v: float) -> float:
        return round(v * self.size, 2)

    def style_json(self) -> dict:
        layers = []
        for layer in self.layers:
            out = copy.deepcopy(layer)
            for k in _EM_FIELDS:
                if k in out:
                    out[k] = self._px(out[k])
            layers.append(out)
        px, py = self.box_pad
        s = {
            "fontFamily": self.font, "pixelSize": self.size, "fontWeight": self.weight, "italic": self.italic,
            "layers": layers, "pathBend": self.bend, "align": self.align, "valign": self.valign, "wordWrap": True,
            "lineHeight": self.line, "letterSpacing": self._px(self.spacing),
            "boxEnabled": self.box is not None, "boxColor": argb(self.box or "#00000080"),
            "boxPadding": self._px(max(px, py)), "boxRadius": self._px(self.box_radius),
            "wordHighlight": {"enabled": self.word_bg is not None, "color": argb(self.word_bg or "#e62828"),
                              "padding": self._px(self.word_bg_pad), "radius": self._px(self.word_bg_radius)},
            "underlineEnabled": self.underline is not None,
            "underlineColor": argb(self.underline[0] if self.underline else "#e62828"),
            "underlineWidth": self._px(self.underline[1]) if self.underline else 6.0,
            "underlineOffset": self._px(self.underline[2]) if self.underline else 4.0,
            "accent": self._accent_json(), "animation": {},
        }
        if self.case != "none":
            s["textCase"] = self.case
        if self.box is not None:
            if self.box_style != "block":
                s["boxStyle"] = self.box_style
            if self.box_shape != "rect":
                s["boxShape"] = self.box_shape
            s["boxPaddingX"] = self._px(px)
            s["boxPaddingY"] = self._px(py)
            if self.box_offset != (0.0, 0.0):
                s["boxOffsetX"] = self._px(self.box_offset[0])
                s["boxOffsetY"] = self._px(self.box_offset[1])
            if self.box_border:
                s["boxBorderWidth"] = self._px(self.box_border[0])
                s["boxBorderColor"] = argb(self.box_border[1])
        for slot, value in (("in", self.anim_in), ("out", self.anim_out), ("loop", self.anim_loop)):
            if value:
                s["animation"][slot] = value
        return s

    def _accent_json(self) -> dict:
        if not self.acc:
            return {"rule": "none"}
        a = copy.deepcopy(self.acc)
        a["outlineWidth"] = self._px(a["outlineWidth"])
        a["highlight"]["padding"] = self._px(a["highlight"]["padding"])
        a["highlight"]["radius"] = self._px(a["highlight"]["radius"])
        return a

    def document(self) -> dict:
        """The file Stock downloads; `AppController::importUserTextPreset(url)` installs it."""
        return {"format": "flip-text-style", "version": 2, "id": self.id, "label": self.es,
                "names": {"es": self.es, "en": self.en}, "sampleText": self.sample[0],
                "sampleTexts": {"es": self.sample[0], "en": self.sample[1]}, "category": self.category,
                "subtitle": self.subtitle, "style": self.style_json()}

    def fonts(self) -> list[tuple[str, int, bool]]:
        return [(self.font, self.weight, self.italic)]


# --- text animation presets ---------------------------------------------------------------------

def P(id: str, label: str, type: str = "scalar", default=0.0, unit: str = "", min: float = 0, max: float = 1,
      step: float = 0.01) -> dict:
    """A typed param the slot controls show. Labels reuse the app's catalogue words so they translate."""
    if type == "color":
        return {"id": id, "type": "color", "label": label, "default": argb(default)}
    if type == "bool":
        return {"id": id, "type": "bool", "label": label, "default": bool(default)}
    return {"id": id, "type": "scalar", "label": label, "unit": unit, "min": min, "max": max, "step": step,
            "default": default}


def ref(param: str, mul: float = 1.0, add: float = 0.0) -> dict:
    out = {"$": param}
    if mul != 1.0:
        out["mul"] = mul
    if add:
        out["add"] = add
    return out


def stagger_sel(duration_mul: float = 1.0, ease="{ease}", unit: str = "{unit}", order: str = "{order}",
                stagger_mul: float = 1.0) -> dict:
    """The reveal selector, spelled out so its duration (or ease) can differ from the common one."""
    return {"driver": "stagger", "domain": unit, "order": order,
            "staggerUs": ref("stagger", 1_000_000 * stagger_mul), "durationUs": ref("duration", 1_000_000 * duration_mul),
            "ease": ease}


def wiggle(domain: str = "character", wave: str = "sine", hz="{speed}", phase: float = 34.4, lo: float = -100,
           hi: float = 100, tphase: float = 0.0, seed: int = 0) -> dict:
    out = {"driver": "wiggle", "domain": domain, "wave": wave, "frequencyHz": hz, "spatialPhaseDeg": phase,
           "minAmount": lo, "maxAmount": hi}
    if tphase:
        out["temporalPhaseDeg"] = tphase
    if seed:
        out["seed"] = seed
    return out


def karaoke(domain: str = "word") -> dict:
    return {"driver": "karaoke", "domain": domain}


def sweep(domain: str = "character", width: float = 25.0, shape: str = "smooth", lead: float = -30.0,
          tail: float = 105.0) -> dict:
    """A curves window `width` % wide that travels across the text over the slot's progress."""
    return {"driver": "curves", "domain": domain, "units": "percent", "shape": shape, "start": 0.0, "end": width,
            "offset": curve([(0.0, lead), (1.0, tail)])}


def everything(domain: str = "character") -> dict:
    """Coverage 1 on every fragment of the domain (a per-fragment animator with no selection)."""
    return {"driver": "curves", "domain": domain, "units": "percent", "shape": "square", "start": 0.0,
            "end": 100.0}


def curve(points: list, value: float | None = None) -> dict:
    """A param that changes over the slot's progress: [(progress 0..1, value[, 'hold'])]."""
    keys = []
    for p in points:
        k = {"timeUs": int(round(p[0] * 1_000_000)), "value": p[1]}
        if len(p) > 2 and p[2] == "hold":
            k["hold"] = True
        keys.append(k)
    return {"value": points[0][1] if value is None else value, "curve": {"keyframes": keys}}


def bezier(x1: float, y1: float, x2: float, y2: float) -> dict:
    return {"kind": "bezier", "c1": [x1, y1], "c2": [x2, y2]}


def pos(x=0.0, y=0.0, unit: str = "em", cap: float = 0.0) -> dict:
    out = {"x": x, "y": y, "unit": unit}
    if cap:
        out["maxPx"] = cap
    return out


def A(selectors: list, **props) -> dict:
    """An animator. Props: position=pos(..), scale, scaleX, scaleY, rotation, skew, opacity, blur,
    tracking (+trackingUnit), fillColor, strokeColor, strokeWidth, fillOpacity, strokeOpacity, wipe."""
    collapse = props.pop("collapse", None)
    out = {"selectors": selectors, "props": props}
    if collapse is not None:
        out["collapseHidden"] = collapse
    return out


@dataclass
class Anim:
    id: str
    es: str
    en: str
    category: str                      # Stock category
    chip: str                          # the app's gallery chip: basic, character, word, kinetic, light, colour, hold
    slots: list[str]                   # in / out / loop
    sample: tuple[str, str]
    animators: list
    params: list = field(default_factory=list)
    defaults: dict = field(default_factory=dict)
    flags: dict = field(default_factory=dict)
    caret: dict | None = None
    tags: list[str] = field(default_factory=list)
    order: int = 0
    common: bool | None = None         # None: the app decides (true for in/out)
    look: str = "bold"                 # the card's text look (see build.LOOKS)
    hold: float | None = None          # render: seconds the text rests between in and out

    def document(self) -> dict:
        d = {"format": 1, "id": self.id, "label": self.es, "names": {"es": self.es, "en": self.en},
             "category": self.chip, "stockCategory": self.category, "sampleText": self.sample[0],
             "sampleTexts": {"es": self.sample[0], "en": self.sample[1]}, "slots": self.slots,
             "order": 1000 + self.order}
        if self.common is not None:
            d["commonParams"] = self.common
        if self.defaults:
            d["defaults"] = self.defaults
        if self.flags:
            d["flags"] = self.flags
        if self.params:
            d["params"] = self.params
        d["animators"] = self.animators
        if self.caret:
            d["caret"] = self.caret
        return d

    def param_defaults(self) -> dict:
        common = {"duration": 0.4, "stagger": 0.06, "unit": "block", "order": "forward", "ease": "easeOut"}
        out = {}
        reveal = "in" in self.slots or "out" in self.slots
        if (self.common if self.common is not None else reveal):
            out.update(common)
            out.update(self.defaults)
        for p in self.params:
            out[p["id"]] = p["default"]
        return out


# --- fonts --------------------------------------------------------------------------------------

def available_fonts() -> dict[str, set[tuple[int, bool]]]:
    out: dict[str, set[tuple[int, bool]]] = {}
    for f in ADDONS.glob("fonts.*/fonts/*/family.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[d["family"]] = {(x["weight"], bool(x["italic"])) for x in d["faces"]}
    return out
