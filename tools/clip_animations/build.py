"""Writes presets/clip-animations/*.json: Video › Animation's In, Out and Combo galleries.

    py tools/clip_animations/build.py

A preset is curves over its slot's progress (core/ClipAnimationPreset.h): In runs from away (0)
to in place (1), Out from in place (0) to away (1), Combo is one motion over the whole clip that
both brings it in and takes it out. Each Out is the matching In played backwards and sent the
other way, so "Slide up" comes in from below and leaves through the top. Combos are built from an
entrance, an exit and an optional motion while the clip is on screen.

Units: x / y are fractions of the clip's box (+ right / + down), scale percent, rotations degrees,
opacity percent, blur pixels of a 1080 frame. Effects name a catalog effect (effects/<dir>/
effect.json "id") and curve its parameters in the effect's own units.

The Spanish names go to i18n with the rest of the catalog (tools/i18n/catalog_strings.py picks the
English labels up; `ES` below is what drift_es.ts gets).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "presets" / "clip-animations"
ES_OUT = Path(__file__).resolve().parent / "es.json"

ES: dict[str, str] = {}


def k(t, v, e="easeInOut"):
    return [round(t, 4), v, e]


class P:
    def __init__(self, id, en, es, cat, keys, effects=(), duration=0.6, trending=False):
        self.id, self.en, self.es, self.cat = id, en, es, cat
        self.keys = {name: list(track) for name, track in keys.items()}
        self.effects = [dict(e) for e in effects]
        self.duration = duration
        self.trending = trending


def fx(id, **params):
    return {"id": id, "params": params}


# --- In ----------------------------------------------------------------------------------------
# Opacity that is fully up by `t`.
def appear(t=0.45):
    return [k(0, 0, "linear"), k(t, 100)]


IN: list[P] = [
    # basic: what Flip had before the presets, same look
    P("slide-up", "Slide up", "Deslizar hacia arriba", "basic", {"y": [k(0, 0.35, "easeOut"), k(1, 0)], "opacity": appear(0.6)}),
    P("slide-down", "Slide down", "Deslizar hacia abajo", "basic", {"y": [k(0, -0.35, "easeOut"), k(1, 0)], "opacity": appear(0.6)}),
    P("slide-left", "Slide left", "Deslizar a la izquierda", "basic", {"x": [k(0, 0.35, "easeOut"), k(1, 0)], "opacity": appear(0.6)}),
    P("slide-right", "Slide right", "Deslizar a la derecha", "basic", {"x": [k(0, -0.35, "easeOut"), k(1, 0)], "opacity": appear(0.6)}),
    P("zoom-in", "Zoom in", "Acercar", "basic", {"scale": [k(0, 60, "easeOut"), k(1, 100)], "opacity": appear()}),
    P("zoom-out", "Zoom out", "Alejar", "basic", {"scale": [k(0, 140, "easeOut"), k(1, 100)], "opacity": appear()}),
    P("pop", "Pop", "Pop", "basic", {"scale": [k(0, 55, "back"), k(1, 100)], "opacity": appear(0.3)}, duration=0.45),
    P("spin-cw", "Spin clockwise", "Girar a la derecha", "basic", {"rotation": [k(0, -90, "easeOut"), k(1, 0)], "opacity": appear()}),
    P("spin-ccw", "Spin anticlockwise", "Girar a la izquierda", "basic", {"rotation": [k(0, 90, "easeOut"), k(1, 0)], "opacity": appear()}),
    P("bounce", "Bounce", "Rebote", "basic", {"y": [k(0, 0.35, "bounce"), k(1, 0)], "opacity": appear(0.25)}, duration=0.8),

    # slide
    P("push-left", "Push from right", "Empujar desde la derecha", "slide", {"x": [k(0, 1, "easeOut"), k(1, 0)]}, trending=True),
    P("push-right", "Push from left", "Empujar desde la izquierda", "slide", {"x": [k(0, -1, "easeOut"), k(1, 0)]}),
    P("push-up", "Push from below", "Empujar desde abajo", "slide", {"y": [k(0, 1, "easeOut"), k(1, 0)]}),
    P("push-down", "Push from above", "Empujar desde arriba", "slide", {"y": [k(0, -1, "easeOut"), k(1, 0)]}),
    P("diagonal", "Diagonal", "Diagonal", "slide", {"x": [k(0, -0.7, "easeOut"), k(1, 0)], "y": [k(0, 0.7, "easeOut"), k(1, 0)], "opacity": appear(0.4)}),
    P("swift-left", "Swift slide", "Deslizamiento veloz", "slide",
      {"x": [k(0, 0.8, "easeOut"), k(1, 0)], "blur": [k(0, 40, "easeOut"), k(0.7, 0)]},
      [fx("motion_trail", amount=[k(0, 0.8, "easeOut"), k(0.8, 0)], angle=0.0, length=0.7)], duration=0.5, trending=True),
    P("swing-in", "Swing in", "Entrar balanceando", "slide",
      {"x": [k(0, -0.6, "easeOut"), k(1, 0)], "rotation": [k(0, -25, "back"), k(1, 0)], "opacity": appear(0.3)}, duration=0.7),
    P("glide-up", "Glide up", "Planear hacia arriba", "slide",
      {"y": [k(0, 0.12, "easeOut"), k(1, 0)], "scale": [k(0, 108, "easeOut"), k(1, 100)], "opacity": appear(0.7)}, duration=0.9),

    # zoom
    P("zoom-blur", "Zoom blur", "Zoom desenfocado", "zoom",
      {"scale": [k(0, 170, "easeOut"), k(1, 100)], "opacity": appear(0.25)},
      [fx("zoom_pulse", punch=[k(0, 1, "easeOut"), k(0.9, 0)], blur=0.7)], trending=True),
    P("zoom-far", "From far away", "Desde lejos", "zoom", {"scale": [k(0, 15, "easeOut"), k(1, 100)], "opacity": appear(0.3)}, duration=0.8),
    P("zoom-spin", "Zoom spin", "Zoom con giro", "zoom",
      {"scale": [k(0, 25, "easeOut"), k(1, 100)], "rotation": [k(0, -180, "easeOut"), k(1, 0)], "opacity": appear(0.3)}, duration=0.8, trending=True),
    P("punch-in", "Punch in", "Golpe de zoom", "zoom", {"scale": [k(0, 135, "elastic"), k(1, 100)]}, duration=0.7),
    P("zoom-rgb", "Zoom split", "Zoom con color separado", "zoom",
      {"scale": [k(0, 130, "easeOut"), k(1, 100)], "opacity": appear(0.3)},
      [fx("rgb_split", amount=[k(0, 30, "easeOut"), k(1, 0)], angle=0.0)]),

    # spin
    P("spin-blur", "Spin blur", "Giro desenfocado", "spin",
      {"rotation": [k(0, 360, "easeOut"), k(1, 0)], "scale": [k(0, 50, "easeOut"), k(1, 100)], "opacity": appear(0.3)},
      [fx("spin_blur", amount=[k(0, 0.9, "easeOut"), k(0.9, 0)])], duration=0.8, trending=True),
    P("roll-in", "Roll in", "Rodar", "spin", {"x": [k(0, -1, "easeOut"), k(1, 0)], "rotation": [k(0, -360, "easeOut"), k(1, 0)]}, duration=0.8),
    P("twist", "Twist", "Torcer", "spin", {"rotation": [k(0, 45, "back"), k(1, 0)], "scale": [k(0, 70, "back"), k(1, 100)], "opacity": appear(0.3)}),
    P("whirl", "Whirlwind", "Remolino", "spin",
      {"rotation": [k(0, -720, "easeOut"), k(1, 0)], "scale": [k(0, 0, "easeOut"), k(1, 100)]}, duration=1.0),

    # 3d
    P("flip-x", "Flip down", "Voltear hacia abajo", "3d", {"rotationX": [k(0, 90, "easeOut"), k(1, 0)], "opacity": appear(0.2)}),
    P("flip-y", "Flip over", "Voltear", "3d", {"rotationY": [k(0, -90, "easeOut"), k(1, 0)], "opacity": appear(0.2)}, trending=True),
    P("door", "Door", "Puerta", "3d", {"rotationY": [k(0, 85, "easeOut"), k(1, 0)], "x": [k(0, 0.25, "easeOut"), k(1, 0)], "opacity": appear(0.3)}, duration=0.8),
    P("tilt-up", "Tilt up", "Inclinar hacia arriba", "3d", {"rotationX": [k(0, -60, "easeOut"), k(1, 0)], "y": [k(0, 0.25, "easeOut"), k(1, 0)], "opacity": appear(0.5)}),
    P("cube-in", "Cube turn", "Giro de cubo", "3d", {"rotationY": [k(0, 90, "easeInOut"), k(1, 0)], "x": [k(0, 0.5, "easeInOut"), k(1, 0)], "scale": [k(0, 85), k(0.5, 85), k(1, 100)]}, duration=0.8),
    P("page-in", "Page turn", "Pasar página", "3d", {"rotationY": [k(0, -120, "easeOut"), k(1, 0)], "opacity": appear(0.3)}, duration=0.9),
    P("swing-3d", "Hinge", "Bisagra", "3d", {"rotationX": [k(0, 95, "elastic"), k(1, 0)]}, duration=1.1),

    # blur
    P("focus-in", "Focus in", "Enfocar", "blur", {"blur": [k(0, 60, "easeOut"), k(1, 0)], "opacity": appear(0.4)}, duration=0.8, trending=True),
    P("dream-in", "Dreamy", "Soñador", "blur", {"blur": [k(0, 40, "easeOut"), k(1, 0)], "scale": [k(0, 112, "easeOut"), k(1, 100)], "opacity": appear(0.6)}, duration=1.0),
    P("ripple-in", "Ripple", "Onda", "blur", {"opacity": appear(0.4)}, [fx("ripple_water", amplitude=[k(0, 40, "easeOut"), k(1, 0)], frequency=14.0)], duration=0.9),
    P("wave-in", "Wave warp", "Ondular", "blur", {"opacity": appear(0.4)}, [fx("wave_warp", amount=[k(0, 0.9, "easeOut"), k(1, 0)], frequency=8.0)], duration=0.8),

    # glitch
    P("glitch-in", "Glitch", "Glitch", "glitch",
      {"opacity": [k(0, 0, "hold"), k(0.1, 100, "hold"), k(0.18, 30, "hold"), k(0.26, 100)]},
      [fx("digital_glitch", intensity=[k(0, 1, "easeOut"), k(1, 0)], rgbAmount=24.0, blockAmount=0.7)], duration=0.6, trending=True),
    P("pixel-in", "Pixelate", "Pixelar", "glitch", {"opacity": appear(0.3)},
      [fx("stylize.pixelate", width=[k(0, 56, "easeOut"), k(1, 2)], height=[k(0, 56, "easeOut"), k(1, 2)])], duration=0.7),
    P("flash-in", "Flash", "Destello", "glitch", {"opacity": appear(0.15)}, [fx("strobe_flash", flash=[k(0, 1, "easeOut"), k(1, 0)])], duration=0.5),
    P("shake-in", "Shake", "Sacudir", "glitch", {"scale": [k(0, 112, "easeOut"), k(1, 100)]}, [fx("beat_shake", amount=[k(0, 1, "easeOut"), k(1, 0)], rotation=0.5)], duration=0.6),
    P("rgb-in", "Colour split", "Color separado", "glitch", {"opacity": appear(0.3)}, [fx("rgb_split", amount=[k(0, 45, "easeOut"), k(1, 0)], angle=90.0)], duration=0.5),
    P("vhs-in", "Bad signal", "Mala señal", "glitch", {"opacity": appear(0.3)},
      [fx("scanline_glitch", jitter=[k(0, 1, "easeOut"), k(1, 0)], colorShift=[k(0, 18, "easeOut"), k(1, 0)])], duration=0.7),

    # bounce
    P("drop-bounce", "Drop", "Caer", "bounce", {"y": [k(0, -1, "bounce"), k(1, 0)]}, duration=0.9, trending=True),
    P("jelly", "Jelly", "Gelatina", "bounce",
      {"scaleX": [k(0, 40), k(0.35, 120), k(0.55, 92), k(0.75, 104), k(1, 100)],
       "scaleY": [k(0, 40), k(0.35, 85), k(0.55, 108), k(0.75, 97), k(1, 100)], "opacity": appear(0.2)}, duration=0.8),
    P("spring-up", "Spring", "Resorte", "bounce", {"y": [k(0, 0.5, "elastic"), k(1, 0)], "opacity": appear(0.2)}, duration=1.0),
    P("rubber", "Rubber band", "Liga", "bounce", {"scaleX": [k(0, 160, "elastic"), k(1, 100)], "scaleY": [k(0, 55, "elastic"), k(1, 100)]}, duration=0.9),
    P("hop", "Hop", "Saltito", "bounce",
      {"y": [k(0, 0.3, "easeOut"), k(0.5, -0.06, "easeIn"), k(0.75, 0, "easeOut"), k(0.88, -0.02, "easeIn"), k(1, 0)], "opacity": appear(0.25)}, duration=0.7),
]

# --- Out: each In backwards, sent the other way ------------------------------------------------
REVERSED_EASE = {"easeIn": "easeOut", "easeOut": "easeIn", "back": "backIn", "backIn": "back", "elastic": "easeIn",
                 "bounce": "easeIn", "easeInOut": "easeInOut", "linear": "linear", "hold": "hold"}
MIRRORED = {"x", "y", "rotation", "rotationX", "rotationY"}


def reverse_track(track, mirror):
    keys = [[1 - t, (-v if mirror else v), e] for t, v, e in track]
    keys.reverse()
    # A segment's ease lives on its first key: shift them one along, mirrored.
    eases = [e for _, _, e in track][:-1]
    eases.reverse()
    out = []
    for i, (t, v, _) in enumerate(keys):
        e = REVERSED_EASE.get(eases[i], "easeInOut") if i < len(eases) else "easeInOut"
        out.append([round(t, 4), v, e])
    return out


def as_out(p: P) -> P:
    keys = {name: reverse_track(track, name in MIRRORED) for name, track in p.keys.items()}
    effects = []
    for e in p.effects:
        params = {}
        for name, val in e["params"].items():
            params[name] = reverse_track(val, False) if isinstance(val, list) else val
        effects.append({"id": e["id"], "params": params})
    return P(p.id, p.en, p.es, p.cat, keys, effects, p.duration, p.trending)


OUT_ONLY: list[P] = [
    P("shrink-away", "Shrink away", "Encoger", "zoom", {"scale": [k(0, 100, "backIn"), k(1, 0)]}, duration=0.5, trending=True),
    P("fall-away", "Fall", "Caída", "slide",
      {"y": [k(0, 0, "easeIn"), k(1, 1.1)], "rotation": [k(0, 0, "easeIn"), k(1, 25)]}, duration=0.8),
    P("blow-away", "Blow away", "Volar", "slide",
      {"x": [k(0, 0, "easeIn"), k(1, 1.2)], "y": [k(0, 0, "easeIn"), k(1, -0.4)], "rotation": [k(0, 0, "easeIn"), k(1, 30)],
       "scale": [k(0, 100, "easeIn"), k(1, 60)]}, duration=0.8),
    P("tv-off", "TV off", "Apagar la tele", "glitch",
      {"scaleY": [k(0, 100, "easeIn"), k(0.6, 1.5, "easeIn"), k(1, 1.5)], "scaleX": [k(0, 100, "hold"), k(0.6, 100, "easeIn"), k(1, 0)]},
      [fx("strobe_flash", flash=[k(0, 0, "easeIn"), k(0.6, 1)])], duration=0.6, trending=True),
    P("dissolve-blur", "Fade into blur", "Fundir en desenfoque", "blur",
      {"blur": [k(0, 0, "easeIn"), k(1, 60)], "opacity": [k(0, 100, "easeIn"), k(1, 0)]}, duration=0.8),
    P("suck-in", "Black hole", "Agujero negro", "spin",
      {"scale": [k(0, 100, "easeIn"), k(1, 0)], "rotation": [k(0, 0, "easeIn"), k(1, 540)]},
      [fx("spin_blur", amount=[k(0, 0, "easeIn"), k(1, 0.9)])], duration=0.8),
]

OUTS: list[P] = [as_out(p) for p in IN] + OUT_ONLY


# --- Combo -------------------------------------------------------------------------------------
def squeeze(track, t0, t1):
    return [[round(t0 + (t1 - t0) * t, 4), v, e] for t, v, e in track]


def combo(id, en, es, cat, enter: P | None, leave: P | None, middle=None, *, a=0.18, b=0.18, effects=(), trending=False):
    """An entrance over [0, a], the exit over [1 - b, 1], and `middle` keys (full 0..1 times) between."""
    keys: dict[str, list] = {}
    rest = {"x": 0, "y": 0, "scale": 100, "scaleX": 100, "scaleY": 100, "rotation": 0, "rotationX": 0,
            "rotationY": 0, "opacity": 100, "blur": 0}

    def add(name, pts):
        keys.setdefault(name, []).extend(pts)

    if enter:
        for name, track in enter.keys.items():
            add(name, squeeze(track, 0, a))
    if leave:
        for name, track in as_out(leave).keys.items():
            add(name, squeeze(track, 1 - b, 1))
    for name, pts in (middle or {}).items():
        add(name, pts)
    names = set(keys)
    for name in names:
        pts = sorted(keys[name], key=lambda p: p[0])
        # Hold the rest pose between the entrance and the exit when the middle says nothing.
        if not (middle and name in middle):
            if enter and name in enter.keys and not any(abs(p[0] - a) < 1e-6 for p in pts):
                pts.append([a, rest[name], "linear"])
            if leave and name in leave.keys and not any(abs(p[0] - (1 - b)) < 1e-6 for p in pts):
                pts.append([round(1 - b, 4), rest[name], "linear"])
            if enter and name not in enter.keys:
                pts.append([0, rest[name], "linear"])
            if leave and name not in leave.keys:
                pts.append([1, rest[name], "linear"])
        pts.sort(key=lambda p: p[0])
        dedup = []
        for p in pts:
            if dedup and abs(dedup[-1][0] - p[0]) < 1e-6:
                dedup[-1] = p
            else:
                dedup.append(p)
        keys[name] = dedup
    fx_all = []
    if enter:
        for e in enter.effects:
            fx_all.append({"id": e["id"], "params": {n: (squeeze(v, 0, a) + [[a, v[-1][1], "linear"]] if isinstance(v, list) else v)
                                                       for n, v in e["params"].items()}})
    if leave:
        for e in as_out(leave).effects:
            fx_all.append({"id": e["id"], "params": {n: ([[round(1 - b, 4), v[0][1], "linear"]] + squeeze(v, 1 - b, 1) if isinstance(v, list) else v)
                                                       for n, v in e["params"].items()}})
    fx_all.extend(dict(e) for e in effects)
    return P(id, en, es, cat, keys, fx_all, duration=0, trending=trending)


def wave(name, amp, cycles, phase=0.0, base=0.0, t0=0.0, t1=1.0, n=None):
    """Smooth back-and-forth keys: peaks at ±amp, `cycles` full swings between t0 and t1."""
    n = n or int(cycles * 2)
    pts = [[t0, base, "easeInOut"]]
    for i in range(1, n + 1):
        t = t0 + (t1 - t0) * i / (n + 1)
        sign = 1 if (i + int(phase)) % 2 else -1
        pts.append([round(t, 4), base + sign * amp, "easeInOut"])
    pts.append([t1, base, "easeInOut"])
    return {name: pts}


I = {p.id: p for p in IN}
O = {p.id: p for p in OUTS}

COMBO: list[P] = [
    # dynamic: motion that lasts the whole clip
    combo("ken-burns-in", "Ken Burns in", "Ken Burns acercando", "dynamic", None, None,
          {"scale": [k(0, 100, "linear"), k(1, 118)], "x": [k(0, 0, "linear"), k(1, -0.03)]}, trending=True),
    combo("ken-burns-out", "Ken Burns out", "Ken Burns alejando", "dynamic", None, None,
          {"scale": [k(0, 118, "linear"), k(1, 100)], "y": [k(0, -0.03, "linear"), k(1, 0)]}),
    combo("pan-left", "Pan left", "Paneo a la izquierda", "dynamic", None, None,
          {"scale": [k(0, 115, "linear"), k(1, 115)], "x": [k(0, 0.06, "linear"), k(1, -0.06)]}),
    combo("pan-right", "Pan right", "Paneo a la derecha", "dynamic", None, None,
          {"scale": [k(0, 115, "linear"), k(1, 115)], "x": [k(0, -0.06, "linear"), k(1, 0.06)]}),
    combo("rise-drift", "Rise", "Ascender", "dynamic", None, None,
          {"scale": [k(0, 112, "linear"), k(1, 112)], "y": [k(0, 0.05, "linear"), k(1, -0.05)]}),
    combo("breathe", "Breathe", "Respirar", "dynamic", None, None, {**wave("scale", 5, 3, base=105)}),
    combo("heartbeat", "Heartbeat", "Latido", "dynamic", None, None,
          {"scale": [k(0, 100), k(0.08, 112, "easeOut"), k(0.16, 100), k(0.24, 108, "easeOut"), k(0.4, 100),
                     k(0.58, 112, "easeOut"), k(0.66, 100), k(0.74, 108, "easeOut"), k(0.9, 100), k(1, 100)]}, trending=True),
    combo("rock", "Rock", "Mecer", "dynamic", None, None, {**wave("rotation", 6, 3), "scale": [k(0, 112, "linear"), k(1, 112)]}),
    combo("float", "Float", "Flotar", "dynamic", None, None, {**wave("y", 0.03, 3), "scale": [k(0, 108, "linear"), k(1, 108)]}),
    combo("sway-3d", "Sway 3D", "Vaivén 3D", "dynamic", None, None, {**wave("rotationY", 14, 2), **wave("rotationX", 8, 3, phase=1), "scale": [k(0, 108, "linear"), k(1, 108)]}, trending=True),
    combo("orbit", "Orbit", "Órbita", "dynamic", None, None,
          {"rotation": [k(0, 0, "linear"), k(1, 360)], "scale": [k(0, 60, "easeOut"), k(0.15, 75), k(0.85, 75, "easeIn"), k(1, 0)]}),
    combo("earthquake", "Earthquake", "Terremoto", "dynamic", None, None, {"scale": [k(0, 110, "linear"), k(1, 110)]},
          effects=[fx("beat_shake", amount=[k(0, 0.6, "linear"), k(1, 0.6)], rotation=0.4)]),
    combo("pendulum", "Pendulum", "Péndulo", "dynamic", None, None, {**wave("rotation", 18, 2, t0=0.05, t1=0.95), "scale": [k(0, 90, "linear"), k(1, 90)]}),

    # entrance + exit
    combo("zoom-roll", "Zoom roll", "Zoom y giro", "zoom", I["zoom-spin"], I["roll-in"], {"scale": [k(0.18, 100, "linear"), k(0.82, 106)]}, trending=True),
    combo("zoom-punch", "Zoom punch", "Golpe de zoom doble", "zoom", I["punch-in"], O["shrink-away"]),
    combo("zoom-blur-combo", "Zoom rush", "Zoom veloz", "zoom", I["zoom-blur"], I["zoom-blur"], {"scale": [k(0.18, 100, "linear"), k(0.82, 108)]}),
    combo("zoom-far-near", "Far and near", "Lejos y cerca", "zoom", I["zoom-far"], I["zoom-out"]),
    combo("zoom-split", "Split zoom", "Zoom separado", "zoom", I["zoom-rgb"], I["zoom-rgb"]),
    combo("zoom-dolly", "Dolly", "Travelling", "zoom", I["zoom-in"], I["zoom-in"], {"scale": [k(0.18, 100, "linear"), k(0.82, 125)]}),

    combo("spin-around", "Spin around", "Dar la vuelta", "spin", I["spin-blur"], I["spin-blur"], trending=True),
    combo("whirl-combo", "Whirlwind", "Remolino", "spin", I["whirl"], O["suck-in"]),
    combo("twist-combo", "Twist", "Torcer", "spin", I["twist"], I["twist"]),
    combo("roll-combo", "Rolling", "Rodando", "spin", I["roll-in"], I["roll-in"]),
    combo("rotate-vanish", "Rotate and vanish", "Rotar y desaparecer", "spin", I["spin-cw"], O["suck-in"]),

    combo("flip-show", "Flip show", "Volteo", "3d", I["flip-y"], I["flip-y"], {"rotationY": [k(0.18, 0), k(0.82, 0)]}, trending=True),
    combo("cube", "Cube", "Cubo", "3d", I["cube-in"], I["cube-in"]),
    combo("door-combo", "Doors", "Puertas", "3d", I["door"], I["door"]),
    combo("page-flip", "Page flip", "Voltear página", "3d", I["page-in"], I["page-in"]),
    combo("tilt-combo", "Tilt", "Inclinación", "3d", I["tilt-up"], I["flip-x"]),
    combo("hinge-combo", "Hinge", "Bisagra", "3d", I["swing-3d"], I["flip-x"]),
    combo("card-flip", "Card flip", "Carta que gira", "3d", I["flip-x"], I["flip-y"], {**wave("rotationY", 10, 1, t0=0.18, t1=0.82)}),

    combo("bounce-in-out", "Bounce", "Rebote", "bounce", I["drop-bounce"], O["fall-away"], trending=True),
    combo("jelly-combo", "Jelly", "Gelatina", "bounce", I["jelly"], I["jelly"]),
    combo("spring-combo", "Spring", "Resorte", "bounce", I["spring-up"], I["spring-up"]),
    combo("rubber-combo", "Rubber band", "Liga", "bounce", I["rubber"], I["rubber"]),
    combo("hop-combo", "Hops", "Saltitos", "bounce", I["hop"], I["hop"], {"y": [k(0.18, 0), k(0.35, -0.03, "easeIn"), k(0.45, 0, "easeOut"), k(0.6, -0.02, "easeIn"), k(0.7, 0), k(0.82, 0)]}),
    combo("roller-coaster", "Roller coaster", "Montaña rusa", "bounce", I["push-left"], I["push-left"],
          {"y": [k(0.18, 0), k(0.35, -0.06), k(0.5, 0.05), k(0.65, -0.06), k(0.82, 0)],
           "rotation": [k(0.18, 0), k(0.35, -6), k(0.5, 5), k(0.65, -6), k(0.82, 0)]}),

    combo("slide-through", "Slide through", "Atravesar", "slide", I["push-left"], I["push-left"], trending=True),
    combo("slide-swift", "Swift", "Veloz", "slide", I["swift-left"], I["swift-left"]),
    combo("rise-fall", "Rise and fall", "Subir y caer", "slide", I["push-up"], O["fall-away"]),
    combo("swing-combo", "Swing", "Balanceo", "slide", I["swing-in"], I["swing-in"], {**wave("rotation", 4, 1, t0=0.18, t1=0.82)}),
    combo("diagonal-combo", "Diagonal", "Diagonal", "slide", I["diagonal"], I["diagonal"]),
    combo("blow-combo", "Gust", "Ráfaga", "slide", I["glide-up"], O["blow-away"]),
    combo("slide-wave", "Wave slide", "Tobogán de olas", "slide", I["push-right"], I["push-right"], {**wave("y", 0.035, 2, t0=0.18, t1=0.82)}),

    combo("focus-combo", "Focus", "Enfoque", "blur", I["focus-in"], I["focus-in"], trending=True),
    combo("dream-combo", "Dream", "Sueño", "blur", I["dream-in"], O["dissolve-blur"]),
    combo("ripple-combo", "Ripples", "Ondas", "blur", I["ripple-in"], I["ripple-in"]),
    combo("wave-combo", "Waves", "Oleaje", "blur", I["wave-in"], I["wave-in"]),

    combo("glitch-combo", "Glitch", "Glitch", "glitch", I["glitch-in"], I["glitch-in"], trending=True),
    combo("pixel-combo", "Pixels", "Píxeles", "glitch", I["pixel-in"], I["pixel-in"]),
    combo("flash-combo", "Double flash", "Flash doble", "glitch", I["flash-in"], I["flash-in"]),
    combo("tv-combo", "Old TV", "Tele antigua", "glitch", I["vhs-in"], O["tv-off"]),
    combo("shake-combo", "Shake", "Sacudir", "glitch", I["shake-in"], I["shake-in"]),
    combo("rgb-combo", "Colour split", "Color separado", "glitch", I["rgb-in"], I["rgb-in"]),
    combo("glitch-pulse", "Glitch pulse", "Pulso glitch", "glitch", I["rgb-in"], I["glitch-in"],
          effects=[fx("digital_glitch", intensity=[k(0, 0, "hold"), k(0.3, 0.9, "hold"), k(0.34, 0, "hold"), k(0.55, 0.9, "hold"),
                                                   k(0.59, 0, "hold"), k(1, 0, "hold")], rgbAmount=20.0)]),
    combo("echo-slide", "Echo slide", "Eco deslizante", "glitch", I["push-left"], I["push-left"],
          effects=[fx("time_echo", frames=6.0, decay=[k(0, 0.85, "linear"), k(0.18, 0), k(0.82, 0, "linear"), k(1, 0.85)])]),

    combo("zoom-beats", "Zoom beats", "Pulsos de zoom", "zoom", I["zoom-in"], O["shrink-away"],
          effects=[fx("zoom_pulse", blur=0.5, punch=[k(0, 0, "hold"), k(0.3, 0.7, "easeOut"), k(0.38, 0, "hold"), k(0.5, 0.7, "easeOut"),
                                                     k(0.58, 0, "hold"), k(0.7, 0.7, "easeOut"), k(0.78, 0, "hold"), k(1, 0, "hold")])], trending=True),
    combo("shockwave-combo", "Shockwave", "Onda expansiva", "zoom", I["punch-in"], O["shrink-away"],
          effects=[fx("shockwave_pulse", width=0.12,
                      radius=[k(0, 0, "linear"), k(0.2, 1, "hold"), k(0.8, 0, "linear"), k(1, 1, "hold")],
                      # Up from nothing: a ring of radius 0 at full strength is a smudge in the middle.
                      strength=[k(0, 0, "linear"), k(0.04, 0.5, "linear"), k(0.2, 0, "hold"), k(0.8, 0, "linear"),
                                k(0.84, 0.5, "linear"), k(1, 0, "hold")])]),
    combo("spiral-combo", "Spiral", "Espiral", "spin", I["zoom-spin"], O["suck-in"],
          effects=[fx("droste_zoom", turns=1.5, zoom=1.2,
                      strength=[k(0, 0.85, "easeOut"), k(0.2, 0), k(0.8, 0, "easeIn"), k(1, 0.85)])]),
    combo("drop-spin", "Drop and spin", "Caer y girar", "spin", I["drop-bounce"], I["spin-blur"]),

    combo("tumble-3d", "Tumble", "Voltereta", "3d", I["flip-x"], I["cube-in"], {**wave("rotationX", 6, 2, t0=0.18, t1=0.82)}),

    combo("light-combo", "Light leak", "Fuga de luz", "blur", I["glide-up"], O["dissolve-blur"],
          effects=[fx("light_leak", hue=0.06, speed=1.0, softness=0.4, flicker=0.1,
                      intensity=[k(0, 0.9, "easeOut"), k(0.25, 0), k(0.75, 0, "easeIn"), k(1, 0.9)])], trending=True),
]


def write(p: P, slot: str, order: int):
    keys = {name: track for name, track in p.keys.items() if track}
    doc = {"format": 1, "id": f"{slot}-{p.id}", "label": p.en, "category": p.cat, "slots": [slot], "order": order,
           "duration": p.duration, "keys": keys}
    if p.trending:
        doc["trending"] = True
    if p.effects:
        doc["effects"] = p.effects
    (OUT / f"{slot}-{p.id}.json").write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n",
                                             encoding="utf-8", newline="\n")
    if ES.get(p.en, p.es) != p.es:
        raise SystemExit(f"{p.en!r} is {ES[p.en]!r} and {p.es!r} in Spanish: one English name, one translation")
    ES[p.en] = p.es


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for i, p in enumerate(IN):
        write(p, "in", i)
    for i, p in enumerate(OUTS):
        write(p, "out", i)
    for i, p in enumerate(COMBO):
        write(p, "combo", i)
    ES_OUT.write_text(json.dumps(ES, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(IN)} in, {len(OUTS)} out, {len(COMBO)} combo -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
