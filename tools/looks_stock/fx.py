"""Builds one-click «Ajustar» looks out of the app's own colour effects.

A look is a stack of effects in a fixed order (LUT, grade, basic, HSL, curves, wheels, stylise, glow,
texture, vignette), saved as the effect-stack payload of src/core/EffectStackStore.cpp: the file the
app imports with AppController::importUserEffectPreset (it lands in AppData/effect-presets.json, under
«Mis efectos»). Every parameter is written out, defaults included, so a look reads the same in any build.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EFFECTS = REPO / "effects"

# catalogId -> package folder
FOLDERS = {
    "color.basic": "color_basic", "color.curves": "color_curves", "color.hsl": "color_hsl",
    "color.wheels": "color_wheels", "color.lut": "color_lut", "stylize.vignette": "stylize_vignette",
    "stylize.film_grain": "stylize_film_grain", "bloom_glow": "bloom_glow", "halation": "halation",
    "stylize.bloom": "stylize_bloom", "cinematic_grade": "cinematic_grade", "duotone": "duotone",
    "stylize.vhs": "stylize_vhs", "super8_film": "super8_film", "vhs_crt": "vhs_crt", "light_leak": "light_leak",
    "bokeh_dream": "bokeh_dream", "star_filter": "star_filter", "stylize.sharpen": "stylize_sharpen",
    "halftone_comic": "halftone_comic", "film_burn": "film_burn",
}
FACTORY_LUTS = {"black_white", "cinematic", "cold", "teal_orange", "vintage", "warm"}


def _defaults() -> dict[str, dict]:
    out = {}
    for cid, folder in FOLDERS.items():
        spec = json.loads((EFFECTS / folder / "effect.json").read_text(encoding="utf-8"))
        assert spec["id"] == cid, (cid, spec["id"])
        out[cid] = {p["identifier"]: p.get("defaultValue") for p in spec.get("parameters", [])}
        out[cid]["_ranges"] = {p["identifier"]: (p.get("minValue"), p.get("maxValue")) for p in spec.get("parameters", [])}
    return out


DEFAULTS = _defaults()


def effect(cid: str, **params) -> dict:
    base = {k: v for k, v in DEFAULTS[cid].items() if k != "_ranges"}
    ranges = DEFAULTS[cid]["_ranges"]
    for k, v in params.items():
        assert k in base, f"{cid} has no parameter {k}"
        lo, hi = ranges[k]
        if isinstance(v, (int, float)) and not isinstance(v, bool) and lo is not None:
            assert lo - 1e-9 <= v <= hi + 1e-9, f"{cid}.{k}={v} outside [{lo}, {hi}]"
            v = round(float(v), 4)
        base[k] = v
    return {"name": "gpu", "catalogId": cid, "parameters": base}


# Curve points at 0, .25, .5, .75, 1.
LINEAR = (0.0, 0.25, 0.5, 0.75, 1.0)


def s_curve(k: float, lift: float = 0.0, crush: float = 1.0) -> tuple:
    """Contrast S of strength k; lift raises the black point (matte), crush < 1 lowers the white point."""
    return (lift, 0.25 - 0.06 * k + lift * 0.5, 0.5, 0.75 + 0.06 * k, crush)


@dataclass
class Look:
    id: str
    es: str
    en: str
    category: str
    theme: str                      # sample photo theme for the card
    tags: list = field(default_factory=list)
    lut: tuple | None = None        # (factory name, intensity)
    grade: dict | None = None       # cinematic_grade
    basic: dict | None = None
    hsl: dict | None = None
    curve: tuple | None = None      # luminance curve
    rgb: tuple | None = None        # (r points, g points, b points)
    wheels: dict | None = None      # shadows/midtones/highlights/offset: (r, g, b)
    duo: dict | None = None
    glow: dict | None = None        # bloom_glow
    bloom: dict | None = None       # stylize.bloom
    halation: dict | None = None
    dream: dict | None = None       # bokeh_dream
    star: dict | None = None
    leak: dict | None = None
    burn: dict | None = None
    vhs: dict | None = None
    crt: dict | None = None
    super8: dict | None = None
    comic: dict | None = None
    sharpen: float | None = None
    grain: tuple | float | None = None     # amount or (amount, size, colour)
    vignette: tuple | float | None = None  # amount or (amount, size, softness)

    def effects(self) -> list[dict]:
        out = []
        if self.lut:
            name, k = self.lut
            assert name in FACTORY_LUTS, name
            out.append(effect("color.lut", lut=f"{name}.cube", intensity=k))
        if self.grade:
            out.append(effect("cinematic_grade", **self.grade))
        if self.basic:
            out.append(effect("color.basic", **self.basic))
        if self.hsl:
            out.append(effect("color.hsl", **self.hsl))
        if self.curve or self.rgb:
            pts = {}
            for ch, vals in zip("l", [self.curve or LINEAR]):
                pts.update({f"{ch}{i}": v for i, v in enumerate(vals)})
            r, g, b = self.rgb or (LINEAR, LINEAR, LINEAR)
            for ch, vals in (("r", r), ("g", g), ("b", b)):
                pts.update({f"{ch}{i}": v for i, v in enumerate(vals)})
            out.append(effect("color.curves", **pts))
        if self.wheels:
            w = {}
            for zone, rgb in self.wheels.items():
                for c, v in zip("RGB", rgb):
                    w[f"{zone}{c}"] = v
            out.append(effect("color.wheels", **w))
        if self.duo:
            out.append(effect("duotone", **self.duo))
        if self.comic:
            out.append(effect("halftone_comic", **self.comic))
        if self.dream:
            out.append(effect("bokeh_dream", **self.dream))
        if self.glow:
            # Designed against bright test photos; three quarters keeps highlights from clipping on most footage.
            g = dict(self.glow)
            g["intensity"] = round(g.get("intensity", 0.6) * 0.75, 3)
            out.append(effect("bloom_glow", **g))
        if self.bloom:
            out.append(effect("stylize.bloom", **self.bloom))
        if self.halation:
            out.append(effect("halation", **self.halation))
        if self.star:
            out.append(effect("star_filter", **self.star))
        if self.leak:
            out.append(effect("light_leak", **self.leak))
        if self.burn:
            out.append(effect("film_burn", **self.burn))
        if self.sharpen:
            out.append(effect("stylize.sharpen", luma_amount=self.sharpen))
        if self.vhs:
            out.append(effect("stylize.vhs", **self.vhs))
        if self.crt:
            out.append(effect("vhs_crt", **self.crt))
        if self.super8:
            out.append(effect("super8_film", **self.super8))
        if self.grain is not None:
            g = self.grain if isinstance(self.grain, tuple) else (self.grain, 1.5, False)
            out.append(effect("stylize.film_grain", amount=g[0], grainSize=g[1], colourGrain=bool(g[2])))
        if self.vignette is not None:
            v = self.vignette if isinstance(self.vignette, tuple) else (self.vignette, 0.0, 1.0)
            out.append(effect("stylize.vignette", amount=v[0], size=v[1], softness=v[2]))
        assert out, self.id
        return out

    def preset(self) -> dict:
        return {"drift": "effectStack", "version": 1, "label": self.es, "labels": {"es": self.es, "en": self.en},
                "sourceDurationUs": 0, "effects": self.effects(), "audioEffects": []}
