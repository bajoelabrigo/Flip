"""In presets, batch "build + stylized" (prefix ibs-): letters that assemble one by one, and styled
entrances (glitch, neon, colour, light, print).

Tricks used here:
* rnd(seed): a frozen noise wiggle (hz 0) intersected with the stagger, so each letter gets its own
  signed amount (random start offsets / tilts that still settle to 0).
* alt(): a frozen sine that is +1, -1, +1… per slot (zipper, lines from both sides); alt01() / alt10()
  are the 1/0 and 0/1 versions for picking even or odd letters.
* prog(points): a curves selector whose amount follows hold-curves over the slot's progress.
"""

from __future__ import annotations

from tkit import (CARET_PARAMS, EXPO, SNAP, SOFT, SPRING, A, T, argb, bar_caret, burst, curve, curves, everything,
                  pos, stagger_sel, sweep, whole, wiggle)


def mode(sel: dict, m: str) -> dict:
    out = dict(sel)
    out["mode"] = m
    return out


def rnd(seed: int, domain: str = "character", lo: float = -100, hi: float = 100) -> dict:
    """A per-fragment random amount, frozen in time, multiplied into the coverage."""
    return mode(wiggle(domain, "noise", hz=0, phase=97, lo=lo, hi=hi, seed=seed), "intersect")


def jitter(hz: float, seed: int, domain: str = "character", lo: float = -100, hi: float = 100) -> dict:
    """A live noise wiggle multiplied into the coverage: shakes while the fragment arrives."""
    return mode(wiggle(domain, "noise", hz=hz, phase=97, lo=lo, hi=hi, seed=seed), "intersect")


def alt(domain: str = "character") -> dict:
    return mode(wiggle(domain, "sine", hz=0, phase=180, tphase=90), "intersect")


def alt01(domain: str = "character") -> dict:
    return mode(wiggle(domain, "sine", hz=0, phase=180, lo=0, hi=100, tphase=90), "intersect")


def alt10(domain: str = "character") -> dict:
    return mode(wiggle(domain, "sine", hz=0, phase=180, lo=0, hi=100, tphase=270), "intersect")


def ramp(domain: str = "character") -> dict:
    """0 on the first fragment rising to 1 on the last."""
    return {"driver": "curves", "domain": domain, "units": "percent", "shape": "rampUp", "start": 0.0, "end": 100.0,
            "mode": "intersect"}


def prog(points: list, domain: str = "character") -> dict:
    s = everything(domain)
    s["amount"] = curve(points)
    return s


def fade(mul: float = 0.45) -> dict:
    return A([stagger_sel(mul, ease="linear")], opacity=0)


def mk(id, en, es, cat, animators, *, unit="character", stagger=0.05, duration=0.5, ease="easeOut",
       order="forward", flags=None, **kw) -> T:
    defaults = {"unit": unit, "stagger": stagger, "duration": duration, "ease": ease, "order": order}
    return T(id, en, es, cat, ["in"], animators, defaults=defaults, flags=dict(flags or {}), **kw)


UNIT = {"unitLocked": True}
UNIT_EASE = {"unitLocked": True, "easeLocked": True}
EASE = {"easeLocked": True}

# --- build: letters assemble one by one -----------------------------------------------------------

BUILD = [
    mk("ibs-scatter-gather", "Scatter and gather", "Dispersas que se juntan", "build", [
        A([stagger_sel(ease=EXPO), rnd(3)], position=pos(1.8, 0)),
        A([stagger_sel(ease=EXPO), rnd(9)], position=pos(0, 1.4)),
        A([stagger_sel(ease=EXPO), rnd(21)], rotation=70),
        A([stagger_sel(ease=EXPO)], blur=4, scale=70),
        fade(0.4)],
       stagger=0.05, duration=0.6, order="random", flags=UNIT_EASE, trending=True),

    mk("ibs-downpour", "Letter downpour", "Aguacero de letras", "build", [
        A([stagger_sel(ease=SNAP)], position=pos(0, -3.0), scaleY=230, scaleX=70, blur=5),
        fade(0.3)],
       stagger=0.05, duration=0.45, order="random", flags=EASE,
       particles=[burst("dot", 8, ("#bfe9ff", "#ffffff"), size=(0.02, 0.045), speed=(0.8, 1.6), life=(0.25, 0.45),
                        spread=150, gravity=7.0, origin="bottom")]),

    mk("ibs-pinwheel", "Pinwheel letters", "Molinete de letras", "build", [
        A([stagger_sel(ease=EXPO)], rotation=-540, scale=15),
        fade(0.4)],
       stagger=0.08, duration=0.65, order="centerOut", flags=EASE),

    mk("ibs-card-turn", "Card turn per letter", "Cartas que giran", "build", [
        A([stagger_sel(ease=SPRING)], rotationY=-100, position=pos(0.15, 0)),
        fade(0.3)],
       stagger=0.07, duration=0.55, flags=EASE, trending=True),

    mk("ibs-centre-bloom", "Bloom from the centre", "Brote desde el centro", "build", [
        A([stagger_sel(ease=SPRING)], scale=0, blur=3),
        fade(0.35)],
       stagger=0.06, duration=0.4, order="centerOut", flags=EASE),

    mk("ibs-word-stamp", "Word by word stamp", "Sello palabra a palabra", "build", [
        A([stagger_sel(ease=SNAP)], scale=260, blur=6),
        A([stagger_sel(ease=SNAP), rnd(5, "word")], rotation=10),
        fade(0.3)],
       unit="word", stagger=0.2, duration=0.28, flags=UNIT_EASE, sample="BIG BOLD NEWS", trending=True,
       particles=[burst("ring", 1, ("#ffffff",), size=(0.5, 0.5), speed=(0.0, 0.0), life=(0.3, 0.35), grow=2.2,
                        per="fragment")]),

    mk("ibs-lines-both-sides", "Lines from both sides", "Líneas de lado a lado", "build", [
        A([stagger_sel(ease=EXPO), alt("line")], position=pos(1.4, 0)),
        A([stagger_sel(ease=EXPO)], blur=8),
        fade(0.4)],
       unit="line", stagger=0.18, duration=0.55, flags=UNIT_EASE, sample="LINE ONE\nLINE TWO"),

    mk("ibs-drop-from-end", "Drop from the end", "Caen desde el final", "build", [
        A(["stagger"], position=pos(0, -1.4), rotation=15),
        fade(0.3)],
       stagger=0.07, duration=0.55, ease="bounce", order="backward"),

    mk("ibs-staircase", "Staircase rise", "Escalera de letras", "build", [
        A([stagger_sel(ease=SNAP)], position=pos(0, 0.3)),
        A([stagger_sel(ease=SNAP), ramp()], position=pos(0, 1.5)),
        fade(0.4)],
       stagger=0.07, duration=0.45, flags=UNIT_EASE),

    mk("ibs-dice-tumble", "Tumbling dice", "Dados que ruedan", "build", [
        A(["stagger"], position=pos(0, -1.1), rotationX=260),
        A([stagger_sel(), rnd(11)], rotation=140),
        fade(0.3)],
       stagger=0.07, duration=0.6, ease="bounce", order="random", flags=UNIT),

    mk("ibs-pancake-pop", "Pancake pop", "Pop aplastado", "build", [
        A(["stagger"], scaleY=0, scaleX=180),
        fade(0.25)],
       stagger=0.05, duration=0.35, ease="back", order="random",
       particles=[burst("ring", 1, ("#ffffffb0",), size=(0.35, 0.35), speed=(0.0, 0.0), life=(0.25, 0.3), grow=2.0,
                        at=0.6)]),

    mk("ibs-soft-type", "Soft-fade typing", "Tecleo con fundido", "build", [
        A([stagger_sel(ease="linear")], position=pos(-0.12, 0), opacity=0)],
       stagger=0.08, duration=0.22, ease="linear", flags=EASE, caret=bar_caret("bar"), params=list(CARET_PARAMS)),

    mk("ibs-skew-side-swap", "Skewed side swap", "Entrada lateral sesgada", "build", [
        A([stagger_sel(ease=EXPO)], position=pos(1.3, 0), skew=-35, scaleX=150),
        fade(0.35)],
       stagger=0.05, duration=0.45, flags=EASE),

    mk("ibs-zipper", "Zipper", "Cremallera", "build", [
        A([stagger_sel(ease=SNAP), alt()], position=pos(0, 1.1)),
        fade(0.35)],
       stagger=0.045, duration=0.45, flags=UNIT_EASE),

    mk("ibs-domino", "Domino stand-up", "Dominó que se levanta", "build", [
        A([stagger_sel(ease=SNAP)], rotation=-85, position=pos(-0.45, 0.32)),
        fade(0.3)],
       stagger=0.09, duration=0.4, flags=EASE),

    mk("ibs-deck-spread", "Deck spread", "Baraja que se abre", "build", [
        A([stagger_sel(ease=EXPO)], tracking=-0.6, trackingUnit="em", rotationY=70),
        fade(0.35)],
       stagger=0.05, duration=0.55, flags=EASE),

    mk("ibs-roll-up-floor", "Roll up from the floor", "Se levantan del piso", "build", [
        A([stagger_sel(ease=EXPO)], rotationX=90, position=pos(0, 0.25)),
        fade(0.4)],
       stagger=0.06, duration=0.5, flags=EASE),

    mk("ibs-slam-from-lens", "Slam from the lens", "Desde la lente", "build", [
        A(["stagger"], scale=420, blur=12),
        fade(0.6)],
       stagger=0.06, duration=0.38, ease="easeOut", order="random"),
]

# --- stylized -------------------------------------------------------------------------------------

STYLE = [
    mk("ibs-glitch-burst", "Glitch burst in", "Glitch de entrada", "stylized", [
        A([stagger_sel(0.0)], opacity=0),
        A([stagger_sel(), jitter(16, 7)], position=pos(0.4, 0.06), skew=24),
        A([stagger_sel(), jitter(12, 3, lo=0, hi=100)], fillColor=argb("#00f0ff")),
        A([stagger_sel(), mode(prog([(0, 0, "hold"), (0.2, 100, "hold"), (0.28, 0, "hold"), (0.55, 100, "hold"),
                                     (0.6, 0, "hold"), (1, 0, "hold")]), "intersect")], fillColor=argb("#ff2bd6"))],
       stagger=0.04, duration=0.45, ease="linear", order="random", flags=UNIT, trending=True),

    mk("ibs-neon-strike", "Neon tube strike", "Tubo de neón", "stylized", [
        A(["stagger"], fillColor=argb("#40404c"), strokeColor=argb("#40404c"), blur=1.5),
        A([stagger_sel(), jitter(22, 4, lo=0, hi=100)], opacity=10)],
       stagger=0.09, duration=0.5, ease="linear", flags=UNIT),

    mk("ibs-colour-sweep", "Colour sweep in", "Barrido de color", "stylized", [
        A(["stagger"], position=pos(0, 0.25)),
        fade(0.5),
        A([sweep("character", 35, "smooth", -35, 120)], fillColor=argb("#ff3fa4")),
        A([sweep("character", 30, "smooth", -80, 110)], fillColor=argb("#ffd23f"))],
       stagger=0.06, duration=0.4, ease="easeOut", flags=UNIT),

    mk("ibs-chromatic-pop", "Chromatic pop", "Pop cromático", "stylized", [
        A(["stagger"], scale=160),
        A([stagger_sel(1.8, ease="easeOut")], fillColor=argb("#22e4ff")),
        A([stagger_sel(0.9, ease="easeOut")], fillColor=argb("#ff2bd6")),
        fade(0.3)],
       stagger=0.06, duration=0.35, ease="back", order="centerOut"),

    curves("ibs-alternating-strobe", "Alternating strobe", "Estrobo alterno", "stylized", [
        A([prog([(0, 100, "hold"), (0.1, 0, "hold"), (0.2, 100, "hold"), (0.3, 0, "hold"), (0.4, 100, "hold"),
                 (0.5, 0, "hold"), (1, 0, "hold")]), alt01()], opacity=0),
        A([prog([(0, 100, "hold"), (0.05, 0, "hold"), (0.15, 100, "hold"), (0.25, 0, "hold"), (0.35, 100, "hold"),
                 (0.45, 0, "hold"), (0.55, 100, "hold"), (0.6, 0, "hold"), (1, 0, "hold")]), alt10()], opacity=0),
        whole(scale=curve([(0, 118, "hold"), (0.2, 110, "hold"), (0.4, 104, "hold"), (0.6, 100, "hold"),
                           (1, 100, "hold")]))],
           duration=0.7),

    mk("ibs-glow-bloom", "Glow bloom", "Brillo que florece", "stylized", [
        A(["stagger"], blur=16, scale=125),
        fade(0.6),
        A([stagger_sel(1.3, ease="easeOut")], fillColor=argb("#ffe08a"), strokeColor=argb("#ffd27a"), strokeWidth=6)],
       stagger=0.05, duration=0.7, ease="easeOut", order="centerOut"),

    mk("ibs-shimmer-reveal", "Golden shimmer reveal", "Revelado dorado", "stylized", [
        A(["stagger"], wipe={"enabled": True, "angleDeg": 0, "softness": 0.5}, position=pos(-0.08, 0)),
        A([sweep("character", 18, "smooth", -20, 118)], fillColor=argb("#ffd86b"))],
       stagger=0.06, duration=0.4, ease="smooth", trending=True,
       particles=[burst("flare", 2, ("#ffffff", "#fff2c0"), size=(0.06, 0.12), speed=(0.0, 0.1), life=(0.3, 0.5),
                        origin="top", glow=0.8, additive=True)]),

    mk("ibs-outline-then-fill", "Outline then fill", "Contorno y relleno", "stylized", [
        fade(0.5),
        A(["stagger"], strokeWidth=7, strokeColor=argb("#ffffff")),
        A([stagger_sel(2.2, ease="easeIn")], fillOpacity=0)],
       stagger=0.1, duration=0.35, ease="easeOut"),

    mk("ibs-skew-snap", "Skew snap", "Golpe sesgado", "stylized", [
        A([stagger_sel(ease=SPRING)], skew=-55, scaleY=30, position=pos(-0.3, 0)),
        fade(0.3)],
       unit="word", stagger=0.14, duration=0.45, flags=EASE, sample="SNAP TO IT"),

    mk("ibs-digital-decode", "Digital decode", "Decodificación digital", "stylized", [
        A([stagger_sel(0.0)], opacity=0),
        A([stagger_sel(), jitter(18, 13, lo=0, hi=100)], opacity=0),
        A([stagger_sel(), jitter(10, 17)], scaleY=150),
        A([stagger_sel(1.3, ease="easeIn")], fillColor=argb("#36ff8f"))],
       stagger=0.06, duration=0.5, ease="linear", order="random", flags=UNIT),

    curves("ibs-vhs-tracking", "VHS tracking", "Señal VHS", "stylized", [
        whole(position=pos(curve([(0, 0.5, "hold"), (0.1, -0.3, "hold"), (0.2, 0.2, "hold"), (0.32, -0.1, "hold"),
                                  (0.45, 0.06, "hold"), (0.6, 0, "hold"), (1, 0, "hold")]), 0),
              skew=curve([(0, 18, "hold"), (0.15, -12, "hold"), (0.3, 8, "hold"), (0.5, 0, "hold"), (1, 0, "hold")]),
              blur=curve([(0, 8), (0.6, 0), (1, 0)]),
              opacity=curve([(0, 0, "hold"), (0.05, 70, "hold"), (0.12, 30, "hold"), (0.2, 90, "hold"), (0.6, 100),
                             (1, 100)])),
        A([prog([(0, 100, "hold"), (0.1, 0, "hold"), (0.2, 100, "hold"), (0.3, 0, "hold"), (1, 0, "hold")], "block")],
          fillColor=argb("#ff3b6b")),
        A([prog([(0, 0, "hold"), (0.1, 100, "hold"), (0.2, 0, "hold"), (0.3, 100, "hold"), (0.42, 0, "hold"),
                 (1, 0, "hold")], "block")], fillColor=argb("#3be8ff"))],
           duration=0.8),

    mk("ibs-heat-haze", "Heat haze clearing", "Calor que se aclara", "stylized", [
        A([stagger_sel(), mode(wiggle("character", "sine", hz=7, phase=70), "intersect")], position=pos(0, 0.12),
          skew=10),
        A(["stagger"], blur=9, scaleY=112),
        A([stagger_sel(1.2)], fillColor=argb("#ff9a3c")),
        fade(0.5)],
       stagger=0.05, duration=0.7, ease="smooth", flags=UNIT),

    mk("ibs-comic-pop", "Comic pop with tilt", "Pop de cómic", "stylized", [
        A([stagger_sel(ease=SPRING)], scale=0),
        A([stagger_sel(ease=SPRING), rnd(8, "word")], rotation=22),
        A([stagger_sel(1.6, ease="easeIn")], fillColor=argb("#ffd400"), strokeColor=argb("#e62828"), strokeWidth=6),
        fade(0.2)],
       unit="word", stagger=0.16, duration=0.4, flags=UNIT_EASE, sample="BAM! POW!", trending=True,
       particles=[burst("triangle", 8, ("#ffd400", "#ff3b3b", "#ffffff"), size=(0.05, 0.1), speed=(1.2, 2.4),
                        life=(0.25, 0.45), drag=4.0, spin=300.0)]),

    mk("ibs-rainbow-settle", "Rainbow letters settling", "Letras arcoíris", "stylized", [
        A(["stagger"], position=pos(0, -0.5), scale=70),
        fade(0.4),
        A([stagger_sel(2.2, ease="easeIn")], fillColor=argb("#ff3b5c"))] + [
        A([wiggle("character", "noise", hz=0, phase=97, lo=-300, hi=300, seed=s), mode(prog([(0, 0), (1, 0)]), "max"),
           mode(stagger_sel(2.2, ease="easeIn"), "intersect")], fillColor=argb(c))
        for s, c in ((5, "#ffd400"), (9, "#2bd9ff"), (14, "#7cff4f"), (21, "#b45cff"))],
       stagger=0.05, duration=0.45, ease="back", flags=UNIT),

    mk("ibs-ink-blot", "Ink blot settle", "Mancha de tinta", "stylized", [
        A(["stagger"], blur=10, strokeWidth=14, strokeColor=argb("#101014"), scale=115),
        A([stagger_sel(1.0)], fillColor=argb("#1a1a22")),
        fade(0.5)],
       stagger=0.07, duration=0.6, ease="smooth"),

    mk("ibs-scanline-print", "Scanline print", "Impresión por escaneo", "stylized", [
        A(["stagger"], wipe={"enabled": True, "angleDeg": 90, "softness": 0.15}),
        A([stagger_sel(2.0, ease="easeOut")], fillColor=argb("#5ef2ff")),
        A([stagger_sel(), jitter(20, 2)], position=pos(4, 0, "px"))],
       stagger=0.08, duration=0.35, ease="linear", flags=UNIT),

    curves("ibs-hologram-boot", "Hologram boot", "Holograma que arranca", "stylized", [
        whole(scaleY=curve([(0, 3), (0.3, 100), (1, 100)]), scaleX=curve([(0, 160), (0.3, 100), (1, 100)]),
              opacity=curve([(0, 0, "hold"), (0.04, 100, "hold"), (0.4, 40, "hold"), (0.46, 100, "hold"),
                             (0.58, 55, "hold"), (0.64, 100, "hold"), (1, 100, "hold")]),
              blur=curve([(0, 6), (0.35, 0), (1, 0)])),
        A([prog([(0, 100), (0.7, 100), (1, 0)], "block")], fillColor=argb("#6ff7ff"), strokeColor=argb("#1aa8c8"))],
           duration=0.8, trending=True),

    mk("ibs-two-tone-settle", "Two-tone settle", "Dos tonos que se asientan", "stylized", [
        A([stagger_sel(ease=SOFT)], position=pos(0, 0.35), rotation=-8),
        fade(0.4),
        A([stagger_sel(1.8, ease="easeOut"), alt01()], fillColor=argb("#ff7a2f")),
        A([stagger_sel(1.8, ease="easeOut"), alt10()], fillColor=argb("#8a5cff"))],
       stagger=0.05, duration=0.45, flags=UNIT_EASE),
]

PRESETS = BUILD + STYLE
