"""Building blocks for the built-in text animations of Text › Animation (presets/text-animations).

A preset is the JSON core/TextAnimationPreset.cpp reads: typed params, animators (After Effects
style: selectors that pick fragments + property deltas at full coverage), an optional caret and
optional particles. `T.document()` writes it. Labels are English (the catalog translates them,
see tools/i18n/catalog_strings.py); the Spanish name rides along for drift_es.ts.

Reading the motion
------------------
* In: coverage 1 = fully away, 0 = in place. A reveal animator says where a fragment starts
  ("position 0, 0.6 em below, opacity 0") and the stagger selector brings each one home in turn.
* Out: the same animator, mirrored in time: coverage rises from 0 to 1 as the fragment leaves.
  When a preset is in both slots, positions are negated for Out unless flags.mirrorForOut is false.
* Curves presets (no stagger) read their props over the slot's progress (0 → 1), with the length
  in the "duration" param.

Units: positions in em (+y down) unless the unit says box / px; scale in %; rotations in degrees
(rotationX tips the top edge away, rotationY swings the right edge away); blur and stroke in
project px; times in seconds (params) or microseconds (raw selector fields).

Chips (category): motion, mask, fluid, build, stylized, particles. trending=True also lists it
under Trending.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import importlib.util  # noqa: E402

# Stock's text kit (tools/text_stock/kit.py) holds the animator spellings; loaded under its own name.
_spec = importlib.util.spec_from_file_location("stock_kit", Path(__file__).resolve().parents[1] / "text_stock" / "kit.py")
_stock = importlib.util.module_from_spec(_spec)
sys.modules["stock_kit"] = _stock
_spec.loader.exec_module(_stock)
A, P, argb, bezier, curve, everything = _stock.A, _stock.P, _stock.argb, _stock.bezier, _stock.curve, _stock.everything
karaoke, pos, ref, stagger_sel, sweep, wiggle = _stock.karaoke, _stock.pos, _stock.ref, _stock.stagger_sel, _stock.sweep, _stock.wiggle

CHIPS = ("motion", "mask", "fluid", "build", "stylized", "particles")

SNAP = bezier(0.05, 0.9, 0.1, 1.0)       # lands hard
SPRING = bezier(0.2, 2.1, 0.45, 1.0)     # overshoots once
SOFT = bezier(0.25, 0.1, 0.25, 1.0)
EXPO = bezier(0.16, 1.0, 0.3, 1.0)

ABCD = "ABCD"


@dataclass
class T:
    id: str
    en: str
    es: str
    cat: str
    slots: list
    animators: list
    sample: str = ABCD
    defaults: dict = field(default_factory=dict)
    params: list = field(default_factory=list)
    flags: dict = field(default_factory=dict)
    caret: dict | None = None
    particles: list | dict | None = None
    trending: bool = False
    common: bool | None = None
    order: int = 0

    def document(self) -> dict:
        d = {"format": 1, "id": self.id, "label": self.en, "category": self.cat, "sampleText": self.sample,
             "slots": list(self.slots), "order": 2000 + self.order}
        if self.trending:
            d["trending"] = True
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
        if self.particles:
            # One spec on its own is a list of one: an object reads as {"in": [...], "out": [...]}.
            single = isinstance(self.particles, dict) and "shape" in self.particles
            d["particles"] = [self.particles] if single else self.particles
        return d

    def param_defaults(self) -> dict:
        out = {}
        if self.common if self.common is not None else True:
            out.update({"duration": 0.4, "stagger": 0.06, "unit": "block", "order": "forward", "ease": "easeOut"})
            out.update(self.defaults)
        for p in self.params:
            out[p["id"]] = p["default"]
        return out


def reveal(id, en, es, cat, motion: dict, *, slots=("in",), unit="character", stagger=0.05, duration=0.5,
           ease="easeOut", order="forward", fade: float | None = 0.45, ease_spec=None, extra=(), lock=None,
           **kw) -> T:
    """The everyday reveal: `motion` (the away pose) on the standard stagger selector, plus a faster
    opacity ramp (`fade` × duration, linear) so a letter shows while it still moves. fade=None: no
    fade; fade>=1: opacity is part of the motion. `extra`: more animators. `lock`: flags such as
    {"unitLocked": True} for presets that only make sense one way."""
    motion = dict(motion)
    sel = stagger_sel(ease=ease_spec) if ease_spec else "stagger"
    animators = []
    if fade is None:
        animators.append(A([sel], **motion))
    elif fade >= 1.0:
        motion["opacity"] = 0
        animators.append(A([sel], **motion))
    else:
        animators.append(A([sel], **motion))
        animators.append(A([stagger_sel(fade, ease="linear")], opacity=0))
    animators.extend(extra)
    flags = dict(lock or {})
    if ease_spec:
        flags["easeLocked"] = True
    defaults = {"unit": unit, "stagger": stagger, "duration": duration, "ease": ease, "order": order}
    return T(id, en, es, cat, list(slots), animators, defaults=defaults, flags=flags, **kw)


def curves(id, en, es, cat, animators, *, slots=("in",), duration=0.7, **kw) -> T:
    """A one-piece motion whose props follow curves over the slot's progress (no stagger)."""
    flags = {"unitLocked": True, "orderLocked": True, "easeLocked": True}
    flags.update(kw.pop("flags", {}))
    return T(id, en, es, cat, list(slots), animators, defaults={"duration": duration, "unit": "block", "ease": "linear"},
             flags=flags, **kw)


def whole(**props) -> dict:
    """An animator on the whole block that follows curves over progress (use with curves())."""
    return A([everything("block")], **props)


def per_char(**props) -> dict:
    return A([everything("character")], **props)


# --- particles ------------------------------------------------------------------------------------

def burst(shape="dot", count=8, colors=("#ffffff",), size=(0.04, 0.1), speed=(0.6, 1.8), life=(0.35, 0.8), *,
          at=1.0, angle=-90.0, spread=360.0, gravity=0.0, drag=0.0, origin="center", glow=0.0, additive=False,
          behind=False, grow=1.0, spin=0.0, fade_in=0.0, glyph=None, per="fragment", seed=1) -> dict:
    """Particles thrown once per fragment as it lands (In, at=1 = the end of its motion) or leaves
    (Out, at=0 = as it starts to go). Sizes in em, speed em/s, gravity em/s², life seconds.
    shape: dot, star, spark, ring, square, heart, smoke, confetti, flare, triangle, glyph."""
    d = {"shape": shape, "count": count, "colors": [argb(c) for c in colors], "size": list(size),
         "speed": list(speed), "life": list(life), "at": at, "angle": angle, "spread": spread}
    return _finish(d, gravity, drag, origin, glow, additive, behind, grow, spin, fade_in, glyph, per, seed)


def stream(shape="dot", rate=24.0, colors=("#ffffff",), size=(0.03, 0.08), speed=(0.2, 0.8), life=(0.3, 0.7), *,
           angle=-90.0, spread=120.0, gravity=0.0, drag=0.0, origin="area", glow=0.0, additive=False, behind=False,
           grow=1.0, spin=0.0, fade_in=0.15, glyph=None, per="fragment", seed=1) -> dict:
    """Particles given off continuously while each fragment moves (and all the time in a loop)."""
    d = {"shape": shape, "trigger": "during", "rate": rate, "colors": [argb(c) for c in colors], "size": list(size),
         "speed": list(speed), "life": list(life), "angle": angle, "spread": spread}
    return _finish(d, gravity, drag, origin, glow, additive, behind, grow, spin, fade_in, glyph, per, seed)


def _finish(d, gravity, drag, origin, glow, additive, behind, grow, spin, fade_in, glyph, per, seed):
    for key, val, default in (("gravity", gravity, 0.0), ("drag", drag, 0.0), ("glow", glow, 0.0),
                              ("grow", grow, 1.0), ("spin", spin, 0.0), ("fadeIn", fade_in, 0.0)):
        if val != default:
            d[key] = val
    if origin != "center":
        d["origin"] = origin
    if additive:
        d["additive"] = True
    if behind:
        d["behind"] = True
    if glyph:
        d["glyph"] = glyph
    if per != "fragment":
        d["per"] = per
    if seed != 1:
        d["seed"] = seed
    return d


# --- carets ---------------------------------------------------------------------------------------

CARET_PARAMS = [P("caret", "Caret", type="bool", default=True),
                P("lead", "Caret lead", default=0.3, unit="s", min=0, max=2, step=0.05),
                P("hold", "Hold after", default=0.6, unit="s", min=0, max=5, step=0.1)]


def bar_caret(shape="bar", width=0.08, height=1.0, color="") -> dict:
    """The typewriter cursor: bar, underscore or block, blinking."""
    return {"enabled": "{caret}", "leadUs": ref("lead", 1_000_000), "blinkOnUs": 220000, "blinkOffUs": 280000,
            "holdAfterUs": ref("hold", 1_000_000), "widthEm": width, "heightEm": height, "shape": shape,
            "color": argb(color) if color else ""}


def glyph_caret(glyph: str, color="", height=0.85, gap=0.1, bob=0.0, sway=0.0, hz=2.0, blink=False) -> dict:
    """An emoji or symbol that rides after the last letter shown ("ABC⚡"). glyph: an emoji, a
    symbol, or a vector one: shape:bolt, diamond, heart, star, sparkle, burst, arrow, play, chevron,
    check, plus, hash, slash, asterisk, circle, square, moon, note, flower, drop, snow. The vector
    ones take `color` (the text's fill when empty); emoji keep their own colours."""
    d = {"enabled": "{caret}", "leadUs": ref("lead", 1_000_000), "holdAfterUs": ref("hold", 1_000_000),
         "shape": "glyph", "glyph": glyph, "heightEm": height, "gapEm": gap, "blinkOnUs": 220000,
         "blinkOffUs": 280000 if blink else 0, "color": argb(color) if color else ""}
    if bob:
        d["bobEm"] = bob
    if sway:
        d["swayDeg"] = sway
    if hz != 2.0:
        d["swayHz"] = hz
    return d


def typing(id, en, es, cat, caret: dict, *, stagger=0.07, unit="character", slots=("in",), extra=(), **kw) -> T:
    """Letters appear one by one (a hard step) with a caret riding after the last one."""
    t = reveal(id, en, es, cat, {}, slots=slots, unit=unit, stagger=stagger, duration=0.0, ease="linear", fade=1.0,
               extra=extra, lock={"durationLocked": True}, caret=caret, params=list(CARET_PARAMS) + kw.pop("params", []),
               **kw)
    return t


__all__ = ["A", "P", "T", "ABCD", "CHIPS", "SNAP", "SPRING", "SOFT", "EXPO", "argb", "bezier", "curve", "everything",
           "karaoke", "pos", "ref", "stagger_sel", "sweep", "wiggle", "reveal", "curves", "whole", "per_char",
           "burst", "stream", "bar_caret", "glyph_caret", "typing", "CARET_PARAMS"]
