"""In presets, Motion & path batch: slides and pushes from every side, arcs and thrown paths, wind,
rolls, hinges, zooms from far and from big, spirals, converging halves and 3D turns (rotationX /
rotationY) per letter, per word and on the whole block. Prefix "im-"."""

from __future__ import annotations

import math

from tkit import (A, EXPO, SNAP, SOFT, SPRING, T, bezier, curve, pos, reveal, curves, stagger_sel, whole)

LOCK_BLOCK = {"unitLocked": True}
WORDS = "GO BIG NOW"
LINES = "NEW\nDROP"


def half(start: float, end: float) -> dict:
    """Coverage 1 on the characters between start and end percent (left or right half)."""
    return {"driver": "curves", "domain": "character", "units": "percent", "shape": "square",
            "start": start, "end": end}


def gated(ease="{ease}") -> dict:
    """The reveal selector, multiplied into the selector before it (only that half moves)."""
    s = stagger_sel(ease=ease)
    s["mode"] = "intersect"
    return s


def spiral_points(turns=1.25, radius=0.45, steps=10):
    """x / y keys (box units) of a path that winds into the centre."""
    xs, ys = [], []
    for i in range(steps + 1):
        p = i / steps
        r = radius * (1 - p) ** 1.4
        a = math.pi * 0.5 + turns * 2 * math.pi * p
        xs.append((round(p, 3), round(r * math.cos(a), 4)))
        ys.append((round(p, 3), round(-r * math.sin(a) * 0.6, 4)))
    return xs, ys


_SX, _SY = spiral_points()

PRESETS = [
    # --- slides and pushes -------------------------------------------------------------------------
    reveal("im-push-left-words", "Word push from the left", "Empuje de palabras", "motion",
           {"position": pos(-1.6, 0), "blur": 10}, unit="word", stagger=0.09, duration=0.45, fade=0.3,
           ease_spec=SNAP, sample=WORDS),
    reveal("im-motion-blur-slide", "Motion-blur sweep", "Barrido con estela", "motion",
           {"position": pos(0.55, 0, "box"), "blur": 36, "scaleX": 135}, unit="block", duration=0.45, fade=0.35,
           ease_spec=EXPO, lock=LOCK_BLOCK, trending=True),
    reveal("im-lean-sprint", "Leaning sprint from the right", "Llegan inclinadas", "motion",
           {"position": pos(3.0, 0), "skew": -32, "blur": 6}, stagger=0.035, duration=0.4, fade=0.3, ease_spec=SNAP),
    reveal("im-diag-top-left", "Diagonal dive from the top left", "Diagonal desde arriba", "motion",
           {"position": pos(-1.3, -1.3), "rotation": -22}, stagger=0.05, duration=0.5, fade=0.35, ease_spec=EXPO),
    reveal("im-corner-spring", "Spring out of the corner", "Resorte desde la esquina", "motion",
           {"position": pos(0.35, 0.35, "box"), "scale": 55}, unit="block", duration=0.6, fade=0.3,
           ease_spec=SPRING, lock=LOCK_BLOCK),
    reveal("im-bounce-drop", "Letters drop and bounce", "Caída con rebote", "motion",
           {"position": pos(0, -2.6), "scaleY": 130}, stagger=0.07, duration=0.7, ease="bounce", fade=0.2),
    reveal("im-stretch-rise-lines", "Stretched rise by line", "Subida estirada", "motion",
           {"position": pos(0, 1.3), "scaleY": 150, "blur": 8}, unit="line", stagger=0.12, duration=0.5, fade=0.4,
           ease_spec=SOFT, sample=LINES),
    reveal("im-tilt-drop-words", "Words drop with a tilt", "Palabras caen inclinadas", "motion",
           {"position": pos(0, -1.3), "rotation": -14}, unit="word", stagger=0.1, duration=0.5, order="backward",
           fade=0.3, ease_spec=SPRING, sample=WORDS),

    # --- arcs and curved paths (x and y on different eases) ---------------------------------------
    reveal("im-arc-left", "Arc in from the left", "Arco desde la izquierda", "motion",
           {"position": pos(-2.6, 0)}, stagger=0.06, duration=0.6, fade=0.3, ease_spec=EXPO,
           extra=[A([stagger_sel(ease="easeIn")], position=pos(0, -1.5))]),
    reveal("im-arc-below", "Arc up from below", "Arco desde abajo", "motion",
           {"position": pos(0, 1.8)}, stagger=0.06, duration=0.6, order="backward", fade=0.3, ease_spec=EXPO,
           extra=[A([stagger_sel(ease="easeIn")], position=pos(2.2, 0))]),
    curves("im-thrown-arc", "Thrown in a parabola", "Lanzado en parábola", "motion",
           [whole(position=pos(curve([(0, -0.55), (0.6, 0.03), (0.82, -0.008), (1, 0)]),
                               curve([(0, 0.35), (0.3, -0.16), (0.6, -0.02), (0.8, 0.012), (1, 0)]), "box"),
                  rotation=curve([(0, -40), (0.6, 6), (0.82, -2), (1, 0)]),
                  opacity=curve([(0, 0), (0.15, 100), (1, 100)]))], duration=0.8, trending=True),
    reveal("im-orbit-letters", "Orbit in by letter", "Órbita por letra", "motion",
           {"position": pos(1.5, 0), "rotation": -180, "scale": 40}, stagger=0.06, duration=0.6, order="backward",
           fade=0.3, ease_spec=EXPO, extra=[A([stagger_sel(ease="easeIn")], position=pos(0, -1.5))]),
    curves("im-boomerang", "Boomerang return", "Bumerán", "motion",
           [whole(position=pos(curve([(0, -0.6), (0.45, 0.12), (0.72, -0.025), (0.88, 0.006), (1, 0)]),
                               curve([(0, -0.08), (0.45, 0.05), (1, 0)]), "box"),
                  rotation=curve([(0, -25), (0.45, 12), (0.72, -3), (1, 0)]),
                  scale=curve([(0, 70), (0.45, 104), (1, 100)]),
                  opacity=curve([(0, 0), (0.12, 100), (1, 100)]))], duration=0.85),
    curves("im-skid-stop", "Skid to a stop", "Frenazo", "motion",
           [whole(position=pos(curve([(0, 0.6), (0.4, -0.035), (0.62, 0.012), (0.8, -0.003), (1, 0)]), 0, "box"),
                  skew=curve([(0, -28), (0.4, 22), (0.62, -8), (0.8, 2), (1, 0)]),
                  blur=curve([(0, 24), (0.35, 0), (1, 0)]),
                  opacity=curve([(0, 0), (0.1, 100), (1, 100)]))], duration=0.7),
    curves("im-spiral-in", "Spiral into place", "Espiral hacia el centro", "motion",
           [whole(position=pos(curve(_SX), curve(_SY), "box"),
                  rotation=curve([(0, -300), (0.7, -20), (1, 0)]),
                  scale=curve([(0, 10), (0.7, 92), (1, 100)]),
                  blur=curve([(0, 10), (0.6, 0), (1, 0)]),
                  opacity=curve([(0, 0), (0.15, 100), (1, 100)]))], duration=1.0, trending=True),

    # --- wind, rolls and swings --------------------------------------------------------------------
    reveal("im-wind-blown", "Blown in by the wind", "Traídas por el viento", "fluid",
           {"position": pos(-2.6, -0.7), "skew": -38, "rotation": -30, "blur": 6}, stagger=0.06, duration=0.7,
           fade=0.4, ease_spec=SOFT, trending=True),
    reveal("im-roll-in", "Roll in from the left", "Rodando desde la izquierda", "motion",
           {"position": pos(-3.2, 0), "rotation": -360}, stagger=0.05, duration=0.65, fade=0.25, ease_spec=EXPO),
    reveal("im-hanging-letters", "Hanging letters swing in", "Letras colgantes", "motion",
           {"position": pos(0.35, -0.35), "rotation": 70}, stagger=0.06, duration=0.7, fade=0.25,
           ease_spec=bezier(0.25, 1.8, 0.4, 1.0)),
    curves("im-hinge-swing", "Swing on a hinge", "Balanceo de bisagra", "motion",
           [whole(rotation=curve([(0, -55), (0.35, 20), (0.58, -9), (0.78, 4), (0.9, -1.5), (1, 0)]),
                  position=pos(curve([(0, -0.25), (0.35, 0.09), (0.58, -0.04), (0.78, 0.015), (1, 0)]),
                               curve([(0, -0.12), (0.35, -0.015), (0.58, -0.006), (1, 0)]), "box"),
                  opacity=curve([(0, 0), (0.15, 100), (1, 100)]))], duration=1.0),
    curves("im-falling-leaf", "Falling leaf", "Hoja que cae", "fluid",
           [whole(position=pos(curve([(0, -0.22), (0.25, 0.16), (0.5, -0.09), (0.75, 0.035), (1, 0)]),
                               curve([(0, -0.5), (0.25, -0.33), (0.5, -0.16), (0.75, -0.05), (1, 0)]), "box"),
                  rotation=curve([(0, -18), (0.25, 14), (0.5, -8), (0.75, 3), (1, 0)]),
                  opacity=curve([(0, 0), (0.12, 100), (1, 100)]))], duration=1.2),
    curves("im-jump-squash", "Jump up and squash", "Salta y aplasta", "motion",
           [whole(position=pos(0, curve([(0, 0.5), (0.45, -0.06), (0.65, 0), (1, 0)]), "box"),
                  scaleY=curve([(0, 150), (0.45, 108), (0.65, 80), (0.82, 105), (1, 100)]),
                  scaleX=curve([(0, 72), (0.45, 95), (0.65, 118), (0.82, 97), (1, 100)]),
                  opacity=curve([(0, 0), (0.12, 100), (1, 100)]))], duration=0.75),

    # --- zooms -------------------------------------------------------------------------------------
    reveal("im-words-from-back", "Words from far away", "Palabras desde el fondo", "motion",
           {"scale": 12, "blur": 10}, unit="word", stagger=0.1, duration=0.6, order="random", fade=0.4,
           ease_spec=EXPO, sample=WORDS),
    reveal("im-crash-from-big", "Crash down from giant", "Cae desde gigante", "motion",
           {"scale": 420, "blur": 22}, unit="block", duration=0.4, fade=0.5, ease_spec=SNAP, lock=LOCK_BLOCK),
    reveal("im-drift-focus", "Drift into focus", "Flotan hasta enfocar", "fluid",
           {"position": pos(0, 0.6), "scale": 135, "blur": 16}, stagger=0.07, duration=0.9, order="random",
           fade=0.6, ease_spec=SOFT),
    reveal("im-unfold-centre", "Unfold from the centre", "Se abren desde el centro", "motion",
           {"tracking": -0.55, "trackingUnit": "em", "scale": 30}, stagger=0.03, duration=0.55,
           order="centerOut", ease="back", fade=0.3),

    # --- letters converging from both sides --------------------------------------------------------
    T("im-close-in-sides", "Close in from both sides", "Se juntan desde los lados", "motion", ["in"],
      [A([half(0, 50), gated(SNAP)], position=pos(-2.4, 0), rotationY=-70),
       A([half(50, 100), gated(SNAP)], position=pos(2.4, 0), rotationY=70),
       A([stagger_sel(0.4, ease="linear")], opacity=0)],
      defaults={"unit": "character", "stagger": 0.05, "duration": 0.55, "ease": "easeOut", "order": "centerOut"},
      flags={"unitLocked": True, "easeLocked": True}),

    # --- 3D turns per letter and per word ----------------------------------------------------------
    reveal("im-flip-down", "Flip down into place", "Volteo hacia abajo", "motion",
           {"rotationX": 90, "position": pos(0, -0.3)}, stagger=0.06, duration=0.5, ease="back", fade=0.3),
    reveal("im-flip-over", "Full letter flip", "Volteo completo", "motion",
           {"rotationX": -180}, stagger=0.07, duration=0.6, fade=0.5, ease_spec=EXPO),
    reveal("im-door-words", "Doors open by word", "Puertas por palabra", "motion",
           {"rotationY": -95}, unit="word", stagger=0.12, duration=0.6, fade=0.3, ease_spec=SOFT, sample=WORDS),
    reveal("im-card-turn", "Card turn", "Vuelta de carta", "motion",
           {"rotationY": 180, "scale": 85}, stagger=0.08, duration=0.55, ease="smooth", fade=0.55),
    reveal("im-tumble", "Tumbling letters", "Letras que caen girando", "motion",
           {"rotationX": 120, "rotationY": 60, "rotation": 45, "position": pos(0, -1.6)}, stagger=0.05,
           duration=0.7, order="random", fade=0.3, ease_spec=SOFT, trending=True),
    reveal("im-words-flip-up", "Words flip up", "Palabras que se levantan", "motion",
           {"rotationX": -90, "position": pos(0, 0.6)}, unit="word", stagger=0.1, duration=0.45, fade=0.3,
           ease_spec=SNAP, sample=WORDS),
    reveal("im-line-blinds", "Lines turn like blinds", "Persianas por línea", "motion",
           {"rotationX": 90, "scaleY": 120}, unit="line", stagger=0.15, duration=0.55, ease="back", fade=0.35,
           sample=LINES),
    reveal("im-side-turn-words", "Turn in from the side", "Entran de perfil", "motion",
           {"rotationY": 65, "position": pos(1.6, 0), "blur": 6}, unit="word", stagger=0.09, duration=0.55,
           fade=0.35, ease_spec=EXPO, sample=WORDS),

    # --- whole block in depth ----------------------------------------------------------------------
    reveal("im-block-swing-3d", "3D swing open", "Giro 3D del bloque", "motion",
           {"rotationY": 80}, unit="block", duration=0.7, fade=0.3, ease_spec=SPRING, lock=LOCK_BLOCK,
           trending=True),
    reveal("im-depth-approach", "Approach from depth", "Acercamiento en profundidad", "motion",
           {"rotationX": 70, "scale": 40, "blur": 16, "position": pos(0, 0.15, "box")}, unit="block",
           duration=0.75, fade=0.45, ease_spec=EXPO, lock=LOCK_BLOCK, trending=True),
]
