"""Shared pieces of the Stock transitions: the design types, the shader assembly and the photo pairs."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from glsl import HEADER

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SAMPLES = ROOT / "plantillas" / "muestras"
OUT = ROOT / "transiciones" / "paquetes"

# Two photos that differ in colour and shape, so every frame of the transition reads (no brands, no faces
# cut in half by a logo). Families take turns.
PAIRS = [
    ("h-nature-03", "h-city-05"),
    ("h-beach-01", "h-portrait-01"),
    ("h-spring-01", "h-nature-05"),
    ("h-couple-02", "h-beach-05"),
    ("h-portrait-02", "h-autumn-02"),
    ("h-food-03", "h-summer-02"),
    ("h-winter-02", "h-city-02"),
    ("h-nature-06", "h-autumn-01"),
]

# Stock › Transiciones categories (the filter), in order.
CATEGORIES = {
    "glitch": {"es": "Glitch", "en": "Glitch"},
    "zoom": {"es": "Zoom y golpe", "en": "Zoom & punch"},
    "movimiento": {"es": "Movimiento", "en": "Motion"},
    "formas": {"es": "Formas", "en": "Shapes"},
    "barridos": {"es": "Barridos", "en": "Wipes"},
    "luz": {"es": "Luz y película", "en": "Light & film"},
    "liquido": {"es": "Tinta y líquido", "en": "Ink & liquid"},
    "3d": {"es": "3D y papel", "en": "3D & paper"},
    "divertidas": {"es": "Divertidas", "en": "Fun"},
    "youtuber": {"es": "Youtuber", "en": "YouTuber"},
}


@dataclass
class Param:
    id: str
    en: str
    lo: float
    hi: float
    default: float


@dataclass
class Variant:
    id: str
    es: str
    en: str
    defines: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)   # default overrides
    tags: list = field(default_factory=list)
    thumb: float = 0.5                             # progress of the card frame
    note: dict = field(default_factory=dict)       # {"es", "en"} line for Stock, e.g. the sound that fits


@dataclass
class Family:
    key: str
    app_category: str      # one of the app's six: basic, geometric, liquid, glitch, cinematic, modern
    category: str          # Stock category (CATEGORIES)
    body: str
    params: list = field(default_factory=list)
    variants: list = field(default_factory=list)
    defines: dict = field(default_factory=dict)  # family defaults, a variant overrides them
    tags: list = field(default_factory=list)
    audio: str = "crossfade"
    duration: float = 1.2  # seconds of the transition in the preview


def define_value(v) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return f"{float(v):.4f}"
    if isinstance(v, tuple):
        return f"vec{len(v)}(" + ", ".join(f"{float(x):.4f}" for x in v) + ")"
    if isinstance(v, str) and v.startswith("#") and len(v) == 7:
        r, g, b = (int(v[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return f"vec3({r:.4f}, {g:.4f}, {b:.4f})"
    return str(v)


def shader(family: Family, variant: Variant) -> str:
    defs = dict(family.defines)
    defs.update(variant.defines)
    lines = [HEADER.rstrip(), "", "// Variant settings"]
    for k, v in defs.items():
        lines.append(f"#define {k} {define_value(v)}")
    if family.params:
        lines.append("")
        for p in family.params:
            lines.append(f"uniform float {p.id};")
    lines.append("")
    lines.append(family.body.strip())
    lines.append("")
    return "\n".join(lines)


def param_defaults(family: Family, variant: Variant) -> dict:
    out = {p.id: p.default for p in family.params}
    out.update(variant.params)
    return out


def package_id(variant: Variant) -> str:
    """The id in transition.json (what a project file stores): stock.<slug with underscores>."""
    return "stock." + re.sub(r"[^a-z0-9]+", "_", variant.id).strip("_")
