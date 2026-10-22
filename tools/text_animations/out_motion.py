"""Out presets, motion batch: fragments that fall, fly, fold, melt or get masked away.

Reading an Out preset: coverage rises from 0 (in place) to 1 (gone) as each fragment leaves, so the
props say where it ends up. The engine mirrors the ease in time for Out (coverage = 1 - ease(1 - t)):
"easeOut" gives an exit that accelerates away, "easeIn" one that starts fast and settles, "back"
winds up the other way before it goes, "bounce" hops before it leaves. In Out the order reads as
written: forward = the first letter leaves first, backward = the last one, centerOut = the centre.
"""

from __future__ import annotations

from tkit import (A, SPRING, argb, bar_caret, burst, curve, curves, glyph_caret, pos, reveal, stagger_sel, stream,
                  typing, whole, wiggle)

OUT = ("out",)
CHAR_LOCK = {"unitLocked": True}
WORDS = "SEE YOU SOON"
LINES = "SEE YOU\nNEXT TIME"


def _gate(sel: dict) -> dict:
    """A selector that multiplies the reveal's coverage instead of adding to it."""
    return {**sel, "mode": "intersect"}


def _fixed(hz: float = 0.0, phase: float = 137.5, lo: float = -100, hi: float = 100, tphase: float = 0.0,
           domain: str = "character", wave: str = "sine") -> dict:
    """A per-fragment factor (-1..1 by default) from a wave frozen in time (hz 0): each letter gets its
    own direction, the same on every frame."""
    return _gate(wiggle(domain, wave, hz=hz, phase=phase, lo=lo, hi=hi, tphase=tphase))


def _half(start: float, end: float) -> dict:
    """Coverage 1 on the characters inside [start, end] % of the text, hard edges."""
    return _gate({"driver": "curves", "domain": "character", "units": "percent", "shape": "square",
                  "start": start, "end": end, "smoothness": 0})


def _wipe(angle: float, softness: float) -> dict:
    return {"enabled": True, "angleDeg": angle, "softness": softness}


PRESETS = [
    # --- motion ---------------------------------------------------------------------------------
    reveal("om-drop-spin", "Spinning drop", "Caída con giro", "motion",
           {"position": pos(0.4, 2.6), "rotation": 220}, slots=OUT, stagger=0.05, duration=0.6,
           ease="easeOut", fade=0.4),
    reveal("om-jump-drop", "Jump and drop", "Salto y caída", "motion",
           {"position": pos(0, 2.4)}, slots=OUT, stagger=0.05, duration=0.6, ease="easeOut",
           ease_spec=SPRING, fade=0.35, trending=True),
    reveal("om-spin-off-top", "Spin off the top", "Salen girando hacia arriba", "motion",
           {"position": pos(1.2, -1.6), "rotation": -480, "scale": 40}, slots=OUT, stagger=0.05, duration=0.6,
           ease="easeOut", order="backward", fade=0.45),
    reveal("om-scatter", "Scatter in all directions", "Se dispersan", "motion",
           {"scale": 60, "blur": 6}, slots=OUT, stagger=0.02, duration=0.55, ease="easeOut", order="random",
           fade=0.5, lock=CHAR_LOCK, trending=True,
           extra=[A([stagger_sel(), _fixed(phase=137.5)], position=pos(1.8, 0)),
                  A([stagger_sel(), _fixed(phase=137.5, tphase=90)], position=pos(0, 1.4))]),
    reveal("om-push-right", "Push out right", "Empujadas a la derecha", "motion",
           {"position": pos(3.0, 0), "scaleX": 120, "blur": 5}, slots=OUT, stagger=0.035, duration=0.45,
           ease="easeOut", order="backward", fade=0.4),
    reveal("om-lines-slide-down", "Lines slide down", "Líneas que bajan", "motion",
           {"position": pos(0, 1.4), "scaleY": 120, "blur": 12}, slots=OUT, unit="line", stagger=0.14,
           duration=0.45, ease="easeOut", fade=0.5, sample=LINES),
    reveal("om-tornado", "Tornado lift", "Tornado", "motion",
           {"position": pos(0, -2.2), "rotation": 540, "rotationY": 180, "scale": 20}, slots=OUT, stagger=0.04,
           duration=0.7, ease="easeOut", order="centerOut", fade=0.4, lock=CHAR_LOCK, trending=True,
           extra=[A([stagger_sel(), _fixed(hz=2.5, phase=60)], position=pos(0.7, 0))]),
    reveal("om-roll-left", "Roll away left", "Se van rodando", "motion",
           {"position": pos(-2.4, 0), "rotation": -360}, slots=OUT, stagger=0.05, duration=0.6, ease="easeOut",
           fade=0.35),
    reveal("om-words-fly-up", "Words fly up", "Palabras al cielo", "motion",
           {"position": pos(0, -2.5), "scale": 70, "blur": 4}, slots=OUT, unit="word", stagger=0.1,
           duration=0.5, ease="easeOut", fade=0.5, sample=WORDS),
    reveal("om-tumble", "Tumble down", "Tropiezo", "motion",
           {"position": pos(0.2, 1.9), "rotation": 140, "rotationX": 180}, slots=OUT, stagger=0.05,
           duration=0.65, ease="easeOut", order="random", fade=0.4),
    reveal("om-word-drop", "Word by word drop", "Palabra por palabra al suelo", "motion",
           {"position": pos(0, 2.8), "rotation": 18}, slots=OUT, unit="word", stagger=0.14, duration=0.5,
           ease="back", fade=0.35, sample="BYE FOR NOW"),
    reveal("om-squeeze-centre", "Squeeze to the centre", "Se juntan al centro", "motion",
           {"tracking": -0.55, "trackingUnit": "em", "scale": 40, "blur": 4}, slots=OUT, stagger=0.0,
           duration=0.5, ease="easeOut", fade=0.6, lock={"unitLocked": True, "orderLocked": True}),

    # --- hide & mask ----------------------------------------------------------------------------
    reveal("om-letter-shutters", "Letter shutters", "Persianas por letra", "mask",
           {"wipe": _wipe(0, 0.04)}, slots=OUT, stagger=0.07, duration=0.22, ease="easeInOut", fade=None),
    reveal("om-diagonal-word-wipe", "Diagonal word wipe", "Barrido diagonal por palabra", "mask",
           {"wipe": _wipe(-45, 0.4), "position": pos(0.15, -0.15)}, slots=OUT, unit="word", stagger=0.12,
           duration=0.45, ease="smooth", fade=None, sample=WORDS),
    reveal("om-doors-close", "Doors close by word", "Puertas que se cierran", "mask",
           {"rotationY": 90, "position": pos(-0.15, 0), "fillColor": argb("#5a5a5a")}, slots=OUT, unit="word",
           stagger=0.12, duration=0.45, ease="easeOut", fade=0.3, sample=WORDS),
    reveal("om-split-apart", "Split apart", "Se parten en dos", "mask",
           {"blur": 6, "scaleX": 115}, slots=OUT, stagger=0.06, duration=0.5, ease="easeOut", order="centerOut",
           fade=0.5, lock={"unitLocked": True, "orderLocked": True}, trending=True,
           extra=[A([stagger_sel(), _half(0, 50)], position=pos(-2.4, 0)),
                  A([stagger_sel(), _half(50, 100)], position=pos(2.4, 0))]),
    reveal("om-lines-slip-left", "Lines slip behind the left edge", "Líneas que se esconden a la izquierda",
           "mask", {"position": pos(-0.6, 0), "wipe": _wipe(180, 0.08)}, slots=OUT, unit="line", stagger=0.15,
           duration=0.45, ease="easeOut", fade=None, sample=LINES),
    reveal("om-sink-floor", "Sink through the floor", "Se hunden en el piso", "mask",
           {"position": pos(0, 0.9), "wipe": _wipe(90, 0.05)}, slots=OUT, stagger=0.05, duration=0.4,
           ease="easeOut", order="centerOut", fade=None),
    reveal("om-into-ceiling", "Rise into the ceiling", "Suben y se esconden", "mask",
           {"position": pos(0, -0.8), "wipe": _wipe(-90, 0.05)}, slots=OUT, unit="word", stagger=0.1,
           duration=0.4, ease="easeOut", order="backward", fade=None, sample=WORDS),
    reveal("om-soft-lift-wipe", "Soft lift wipe", "Se borran hacia arriba", "mask",
           {"position": pos(0, -0.2), "wipe": _wipe(-90, 0.35)}, slots=OUT, stagger=0.04, duration=0.4,
           ease="smooth", order="centerOut", fade=None),

    # --- staggered ------------------------------------------------------------------------------
    typing("om-backspace", "Backspace erase", "Borrado con cursor", "build", bar_caret("bar"), slots=OUT,
           stagger=0.07, order="backward", trending=True),
    typing("om-sparkle-delete", "Sparkle delete", "Borrado con destello", "build",
           glyph_caret("shape:sparkle", "#ffd400", bob=0.04, sway=10), slots=OUT, stagger=0.08,
           order="backward"),
    reveal("om-random-vanish", "Random pop-off", "Desaparecen al azar", "build",
           {"scale": 150, "blur": 6}, slots=OUT, stagger=0.09, duration=0.15, ease="linear", order="random",
           fade=1.0),
    reveal("om-domino", "Domino fall", "Efecto dominó", "build",
           {"rotation": 90, "position": pos(0.3, 0.3)}, slots=OUT, stagger=0.07, duration=0.35, ease="easeOut",
           fade=0.3),
    reveal("om-squash-pop", "Squash and pop", "Aplastar y reventar", "build",
           {"scaleY": 45, "scaleX": 130, "position": pos(0, 0.12)}, slots=OUT, stagger=0.08, duration=0.4,
           ease="smooth", fade=None,
           extra=[A([stagger_sel(0.25, ease="easeOut")], scale=190, opacity=0)],
           particles=[burst("ring", 1, ("#ffffff",), size=(0.5, 0.6), speed=(0, 0), life=(0.25, 0.3), at=0.8),
                      burst("dot", 8, ("#ffffff", "#ffd400"), size=(0.04, 0.08), speed=(1.0, 2.0),
                            life=(0.25, 0.45), at=0.8, drag=2.0)]),
    reveal("om-flip-back-3d", "3D flip backwards", "Volteo 3D hacia atrás", "build",
           {"rotationX": 95, "position": pos(0, -0.15)}, slots=OUT, stagger=0.06, duration=0.4, ease="easeOut",
           fade=0.5),
    reveal("om-card-turn", "Cards turn away", "Cartas que se voltean", "build",
           {"rotationY": -100, "position": pos(0.2, 0)}, slots=OUT, stagger=0.05, duration=0.35,
           ease="easeOut", order="backward", fade=0.5),
    reveal("om-zipper", "Zipper open", "Cremallera", "build",
           {"blur": 4}, slots=OUT, stagger=0.04, duration=0.45, ease="easeOut", fade=0.45, lock=CHAR_LOCK,
           extra=[A([stagger_sel(), _fixed(phase=180, tphase=90)], position=pos(0, -1.2))]),

    # --- fluid ----------------------------------------------------------------------------------
    reveal("om-blur-drift", "Blur and drift", "Desenfoque a la deriva", "fluid",
           {"blur": 20, "position": pos(0.4, -0.25), "scale": 120}, slots=OUT, stagger=0.05, duration=0.6,
           ease="smooth", order="random", fade=0.8),
    reveal("om-evaporate", "Evaporate", "Evaporarse", "fluid",
           {"position": pos(0, -1.0), "blur": 14, "scaleY": 140, "scaleX": 80}, slots=OUT, stagger=0.05,
           duration=0.8, ease="easeIn", order="random", fade=0.9, trending=True,
           particles=[stream("smoke", 10, ("#ffffff55",), size=(0.25, 0.45), speed=(0.2, 0.5), life=(0.5, 0.9),
                             spread=50, behind=True, grow=1.8, fade_in=0.2)]),
    reveal("om-melt", "Melt down", "Se derriten", "fluid",
           {"position": pos(0, 0.8), "scaleY": 190, "scaleX": 80, "blur": 9, "wipe": _wipe(-90, 0.5)},
           slots=OUT, stagger=0.05, duration=0.75, ease="easeOut", order="random", fade=None),
    reveal("om-wave-goodbye", "Wave goodbye", "Ola de despedida", "fluid",
           {"position": pos(0, -1.3), "rotation": -12}, slots=OUT, stagger=0.07, duration=0.5, ease="smooth",
           fade=0.5, lock=CHAR_LOCK,
           extra=[A([stagger_sel(), _fixed(phase=90)], position=pos(0.5, 0))]),
    reveal("om-swirl", "Swirl out", "Remolino", "fluid",
           {"rotation": -360, "scale": 0}, slots=OUT, stagger=0.04, duration=0.6, ease="smooth", fade=0.3,
           lock=CHAR_LOCK,
           extra=[A([stagger_sel(), _fixed(phase=90)], position=pos(0.6, 0)),
                  A([stagger_sel(), _fixed(phase=90, tphase=90)], position=pos(0, 0.6))]),
    reveal("om-wind-blown", "Blown by the wind", "Se las lleva el viento", "fluid",
           {"position": pos(2.8, -0.7), "rotation": 50, "skew": 15, "blur": 8}, slots=OUT, stagger=0.04,
           duration=0.7, ease="easeOut", order="backward", fade=0.5, trending=True),
    reveal("om-stretch-up", "Stretch up and thin out", "Se estiran hacia arriba", "fluid",
           {"scaleY": 280, "scaleX": 35, "position": pos(0, -0.9), "blur": 6}, slots=OUT, stagger=0.05,
           duration=0.5, ease="smooth", order="centerOut", fade=0.6),
    reveal("om-bouncy-shrink", "Bouncy shrink", "Rebote que se encoge", "fluid",
           {"scale": 0}, slots=OUT, stagger=0.05, duration=0.6, ease="bounce", fade=0.2),

    # --- stylized -------------------------------------------------------------------------------
    reveal("om-glitch-slice", "Glitch slice out", "Corte glitch", "stylized",
           {"scaleX": 140, "scaleY": 40}, slots=OUT, stagger=0.03, duration=0.35, ease="easeOut", order="random",
           fade=0.4, lock=CHAR_LOCK, trending=True,
           extra=[A([stagger_sel(), _fixed(hz=18, phase=77, wave="noise")], position=pos(0.45, 0), skew=30),
                  A([stagger_sel(0.6, ease="linear")], fillColor=argb("#00f0ff"))]),
    curves("om-flicker-off", "Flicker off", "Parpadeo que se apaga", "stylized",
           [whole(opacity=curve([(0, 1.0, "hold"), (0.15, 0.15, "hold"), (0.22, 1.0, "hold"), (0.4, 0.1, "hold"),
                                 (0.47, 0.9, "hold"), (0.62, 0.0, "hold"), (0.69, 0.7, "hold"), (0.8, 0.0, "hold"),
                                 (1.0, 0.0)]))],
           slots=OUT, duration=0.8),
    reveal("om-short-out", "Letters short out", "Letras en cortocircuito", "stylized",
           {}, slots=OUT, stagger=0.08, duration=0.45, ease="linear", order="random", fade=None, lock=CHAR_LOCK,
           extra=[A([stagger_sel(), _fixed(hz=14, phase=63, lo=0, wave="noise")], opacity=0),
                  A([stagger_sel(0.6, ease="linear")], fillColor=argb("#ffe066")),
                  A([stagger_sel(0.0)], opacity=0)]),
    curves("om-zoom-crush", "Zoom crush", "Golpe de zoom", "stylized",
           [whole(scale=curve([(0, 100), (0.3, 88), (1.0, 340)]), opacity=curve([(0, 1), (0.55, 1), (1.0, 0)]),
                  blur=curve([(0, 0), (0.45, 0), (1.0, 18)]))],
           slots=OUT, duration=0.5, trending=True),
    reveal("om-stretch-away", "Stretch away", "Se estiran y se van", "stylized",
           {"scaleX": 300, "scaleY": 25, "position": pos(1.6, 0), "blur": 10}, slots=OUT, stagger=0.03,
           duration=0.4, ease="easeOut", order="backward", fade=0.5),
    reveal("om-lean-fold", "Lean and fold", "Se inclinan y se pliegan", "stylized",
           {"skew": 60, "scaleX": 20}, slots=OUT, stagger=0.05, duration=0.35, ease="easeOut", fade=0.4),
    curves("om-vanishing-point", "Vanishing point", "Punto de fuga", "stylized",
           [whole(rotationX=curve([(0, 0), (1.0, 70)]), scale=curve([(0, 100), (0.5, 70), (1.0, 0)]),
                  position=pos(0, curve([(0, 0), (1.0, -0.6)])), opacity=curve([(0, 1), (0.8, 1), (1.0, 0)]))],
           slots=OUT, duration=0.7),
    reveal("om-neon-cut", "Neon cut out", "Corte de neón", "stylized",
           {"wipe": _wipe(0, 0.03)}, slots=OUT, stagger=0.06, duration=0.3, ease="easeInOut", fade=None,
           extra=[A([stagger_sel(0.6, ease="linear")], fillColor=argb("#00e5ff"))],
           particles=[burst("spark", 8, ("#00e5ff", "#ffffff"), size=(0.03, 0.06), speed=(1.2, 2.4),
                            life=(0.2, 0.45), at=0.5, angle=0, spread=70, origin="right", glow=0.6,
                            additive=True)]),
    reveal("om-camera-pull", "Pull back into depth", "Se alejan al fondo", "motion",
           {"scale": 20, "rotationY": -35, "blur": 6}, slots=OUT, stagger=0.04, duration=0.5, ease="easeOut",
           order="centerOut", fade=0.6),
    reveal("om-drop-the-mic", "Drop the mic", "Soltar el micrófono", "motion",
           {"position": pos(0, 3.2), "rotation": 40}, slots=OUT, unit="block", stagger=0.0, duration=0.55,
           ease="back", fade=0.85, trending=True),
]
