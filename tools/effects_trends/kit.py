"""Shared pieces of the Stock trend effects (Efectos › Tendencias): design types, shader assembly, photos.

Each effect is a GPU package of the app (effect.json + main.frag), shipped in Stock as a .driftfx. A family
is one shader body; a variant sets its #defines and default parameters, its names and its card photo.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from glsl import HEADER

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SAMPLES = ROOT / "plantillas" / "muestras"
OUT = ROOT / "efectos" / "paquetes"

# Stock › Efectos categories (the filter) and the chips of Efectos › Tendencias, in order.
CATEGORIES = {
    "particulas": {"es": "Partículas y brillos", "en": "Particles & sparkle"},
    "amor": {"es": "Amor", "en": "Love"},
    "luz": {"es": "Luz y destellos", "en": "Light & flares"},
    "glitch": {"es": "Glitch", "en": "Glitch"},
    "camara": {"es": "Movimiento de cámara", "en": "Camera motion"},
    "desenfoque": {"es": "Desenfoque", "en": "Blur"},
    "retro": {"es": "Retro y película", "en": "Retro & film"},
    "marcos": {"es": "Marcos y bordes", "en": "Frames & borders"},
    "estilo": {"es": "Estilizar", "en": "Stylize"},
    "energia": {"es": "Energía y elementos", "en": "Energy & elements"},
    "dividir": {"es": "Dividir y copias", "en": "Split & clones"},
    "abrir": {"es": "Abrir y cerrar", "en": "Open & close"},
    "ia": {"es": "IA", "en": "AI"},
    "audio": {"es": "Voz", "en": "Voice"},
}

# Parameter labels the app already translates (src/engine/CatalogStrings.cpp, context Catalog): a package's
# displayName goes through drift::catalogText, so only these read in the person's language.
PARAM_LABELS = {"Intensity", "Speed", "Colour", "Amount", "Size", "Density", "Angle", "Blur", "Glow", "Brightness",
                "Center X", "Center Y", "Grain", "Frequency", "Zoom", "Rotation", "Distance", "Direction",
                "Softness", "Saturation", "Contrast", "Flicker", "Width", "Height", "Opacity", "Spread",
                "Colour A", "Colour B", "Mix", "Strength", "Scale", "Detail", "Edge Width", "Feather", "Hue"}

# Photo themes of tienda/plantillas/muestras (fx-* were fetched for these cards: fetch_samples.py).
PHOTOS = {
    "woman": ["fx-woman-02", "fx-woman-03", "fx-woman-04", "fx-woman-05", "fx-woman-06", "fx-woman-07", "fx-woman-08"],
    "skater": ["fx-skater-01", "fx-skater-02", "fx-skater-04", "fx-skater-06"],
    "man": ["fx-man-01", "fx-man-02", "fx-man-04", "fx-man-05"],
    "car": ["fx-car-02", "fx-car-03", "fx-car-05"],
    "lighthouse": ["fx-lighthouse-02", "fx-lighthouse-03", "fx-lighthouse-04"],
    "dancer": ["fx-dancer-02", "fx-dancer-03", "fx-dancer-06"],
    "fashion": ["fx-fashion-01", "fx-fashion-02", "fx-fashion-04", "fx-fashion-05", "fx-fashion-06"],
    "citynight": ["fx-citynight-01", "fx-citynight-02", "fx-citynight-03", "fx-citynight-04", "fx-citynight-06"],
    "couple": ["fx-couple-01", "fx-couple-02", "fx-couple-03"],
    "hair": ["fx-hair-01", "fx-hair-02", "fx-hair-03", "fx-hair-05"],
    "concert": ["fx-concert-01", "fx-concert-02", "fx-concert-04"],
    "beach": ["fx-beach-01", "fx-beach-02", "fx-beach-03"],
    "walk": ["fx-walk-01", "fx-walk-02", "fx-walk-03"],
    "face": ["fx-face-01", "fx-face-02", "fx-face-04", "fx-face-06"],
    "figure": ["fx-figure-01", "fx-figure-03", "fx-figure-04", "fx-figure-05", "fx-figure-06"],
    "nature": ["fx-nature-01", "fx-nature-03", "fx-nature-04"],
    "cyber": ["fx-cyber-01", "fx-cyber-02", "fx-cyber-03", "fx-cyber-05", "fx-cyber-06"],
    "dark": ["fx-citynight-02", "fx-concert-01", "fx-cyber-03"],
}


@dataclass
class Param:
    id: str
    en: str            # one of PARAM_LABELS
    lo: float = 0.0
    hi: float = 1.0
    default: float | str = 1.0   # a "#rrggbb" string makes a colour parameter (vec3 in the shader)

    @property
    def is_color(self) -> bool:
        return isinstance(self.default, str)


@dataclass
class Variant:
    id: str                                        # slug, unique across every module
    es: str
    en: str
    defines: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)     # default overrides
    tags: list = field(default_factory=list)
    photo: str = ""                                # a sample name, or a PHOTOS theme (picked by id)
    thumb: float = 1.0                             # second of the card frame
    note: dict = field(default_factory=dict)       # {"es", "en"} line for Stock
    hide: list = field(default_factory=list)       # parameters kept out of the effect panel (fixedParams)


@dataclass
class Family:
    key: str
    category: str          # CATEGORIES
    body: str
    params: list = field(default_factory=list)
    variants: list = field(default_factory=list)
    defines: dict = field(default_factory=dict)  # family defaults, a variant overrides them
    tags: list = field(default_factory=list)
    photo: str = "woman"   # default PHOTOS theme
    requires: str = ""     # "", "face" or "depth" (the clip needs that analysis; AI effects)
    preview: float = 3.0   # seconds of the hover video


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
            lines.append(f"uniform {'vec3' if p.is_color else 'float'} {p.id};")
    lines.append("")
    lines.append(family.body.strip())
    lines.append("")
    return "\n".join(lines)


def param_defaults(family: Family, variant: Variant) -> dict:
    out = {p.id: p.default for p in family.params}
    out.update(variant.params)
    return out


def package_id(variant: Variant) -> str:
    """The id in effect.json (what a project file stores): stockfx_<slug with underscores>."""
    return "stockfx_" + re.sub(r"[^a-z0-9]+", "_", variant.id).strip("_")


def photo_for(family: Family, variant: Variant) -> str:
    name = variant.photo or family.photo
    if name in PHOTOS:
        pool = PHOTOS[name]
        h = 2166136261
        for c in variant.id:
            h = ((h ^ ord(c)) * 16777619) & 0xFFFFFFFF
        name = pool[h % len(pool)]
    return name
