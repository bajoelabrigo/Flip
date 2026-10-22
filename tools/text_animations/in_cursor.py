"""In presets, typing / cursor family (prefix ic-): letters appear one by one while a caret rides
after the last letter shown. Bar, underscore and block cursors, vector glyph carets and a few emoji,
each paired with its own letter motion (pop, drop, slide, flash...) and, for some, particles."""

from tkit import (CARET_PARAMS, SNAP, SOFT, SPRING, A, T, argb, bar_caret, burst, glyph_caret, pos, reveal,
                  stagger_sel, stream, typing)


def typed(id, en, es, cat, caret, motion, *, stagger=0.08, duration=0.2, ease="easeOut", fade=0.2, ease_spec=None,
          extra=(), **kw) -> T:
    """Typing with a short per-letter motion: each letter shows almost at once (fast opacity ramp)
    and settles over `duration` while the caret moves on."""
    return reveal(id, en, es, cat, motion, stagger=stagger, duration=duration, ease=ease, fade=fade,
                  ease_spec=ease_spec, extra=extra, caret=caret, params=list(CARET_PARAMS), **kw)


def flash(color: str) -> dict:
    """The letter arrives tinted and clears to its own fill as it settles."""
    return A([stagger_sel(1.0, ease="easeOut")], fillColor=argb(color))


SPARK = dict(additive=True, glow=0.6)

PRESETS = [
    # --- classic cursors ------------------------------------------------------------------------
    typing("ic-red-bar", "Red cursor typing", "Escritura con cursor rojo", "build",
           bar_caret("bar", 0.08, 1.0, "#ff3b3b"), stagger=0.08),

    typed("ic-yellow-pop", "Thick yellow cursor pop", "Cursor amarillo con rebote", "build",
          bar_caret("bar", 0.16, 1.05, "#ffd400"), {"scale": 140}, stagger=0.08, duration=0.22,
          ease_spec=SPRING, trending=True),

    typed("ic-cyan-drop", "Cyan cursor with falling letters", "Cursor cian con letras que caen", "build",
          bar_caret("bar", 0.1, 1.0, "#00e5ff"), {"position": pos(0, -0.4)}, stagger=0.08, duration=0.24,
          ease_spec=SNAP),

    typed("ic-green-terminal", "Green terminal block", "Bloque verde de terminal", "build",
          bar_caret("block", 0.55, 1.0, "#33ff66"), {}, stagger=0.07, duration=0.3, fade=0.02,
          extra=[flash("#33ff66")]),

    typed("ic-underscore-blur", "Underscore typing with focus", "Guion bajo que enfoca", "build",
          bar_caret("underscore", 0.6, 0.1, "#ffffff"), {"blur": 14}, stagger=0.09, duration=0.25),

    typing("ic-fast-bar", "Rapid magenta typing", "Escritura rápida magenta", "build",
           bar_caret("bar", 0.07, 1.0, "#ff2bd6"), stagger=0.035),

    typed("ic-slow-bar", "Slow thoughtful typing", "Escritura pausada", "build",
          bar_caret("bar", 0.06, 1.0, "#e8e8e8"), {"position": pos(0, 0.08)}, stagger=0.17, duration=0.35,
          fade=0.6, ease_spec=SOFT),

    typed("ic-word-orange", "Word by word typing", "Escritura palabra por palabra", "build",
          bar_caret("bar", 0.1, 1.0, "#ff8a00"), {"position": pos(0, 0.25), "scale": 115}, unit="word",
          stagger=0.22, duration=0.25, ease_spec=SNAP, sample="TYPE IT OUT"),

    typed("ic-center-out", "Typing from the centre", "Escritura desde el centro", "build",
          bar_caret("underscore", 0.6, 0.1, "#ffd400"), {"scaleX": 20}, order="centerOut", stagger=0.1,
          duration=0.22, ease_spec=SNAP),

    typed("ic-amber-block", "Amber terminal block", "Bloque ámbar de terminal", "build",
          bar_caret("block", 0.55, 1.0, "#ffb000"), {"scaleY": 0}, stagger=0.07, duration=0.18, fade=0.1,
          extra=[flash("#ffb000")]),

    # --- vector glyph carets ----------------------------------------------------------------------
    typed("ic-bolt", "Typing with lightning", "Escritura con rayo", "particles",
          glyph_caret("shape:bolt", "#ffd400", bob=0.04, hz=4.0), {"scale": 120}, stagger=0.08, duration=0.2,
          fade=0.05, ease_spec=SNAP, extra=[flash("#fff6a0")], trending=True,
          particles=[burst("spark", 6, ("#ffffff", "#ffd400"), (0.03, 0.07), (1.6, 3.0), (0.15, 0.35),
                           drag=3.0, **SPARK)]),

    typed("ic-gold-star", "Typing with a gold star", "Escritura con estrella dorada", "particles",
          glyph_caret("shape:star", "#ffc83d", sway=14), {"scale": 140}, stagger=0.09, duration=0.25,
          ease_spec=SPRING,
          particles=[burst("star", 5, ("#ffc83d", "#fff1b3"), (0.05, 0.09), (0.5, 1.2), (0.4, 0.7),
                           angle=-90, spread=160, gravity=1.2, spin=180)]),

    typed("ic-sparkle", "Sparkle typing", "Escritura con destello", "particles",
          glyph_caret("shape:sparkle", "#bfe9ff", bob=0.05, sway=10), {"blur": 8, "scale": 90}, stagger=0.08,
          duration=0.25, extra=[flash("#bfe9ff")], trending=True,
          particles=[burst("flare", 4, ("#ffffff", "#bfe9ff"), (0.08, 0.14), (0.2, 0.6), (0.3, 0.55),
                           origin="area", **SPARK)]),

    typed("ic-heart", "Typing with hearts", "Escritura con corazones", "particles",
          glyph_caret("shape:heart", "#ff4d8d", bob=0.06, hz=2.5), {"position": pos(0, -0.3), "scale": 80},
          stagger=0.09, duration=0.3, ease_spec=SPRING, trending=True,
          particles=[burst("heart", 4, ("#ff4d8d", "#ff9ec0"), (0.06, 0.1), (0.4, 0.9), (0.5, 0.9),
                           angle=-90, spread=70, gravity=-0.4, origin="top")]),

    typed("ic-arrow", "Arrow cursor slide", "Cursor de flecha que desliza", "build",
          glyph_caret("shape:arrow", "#00e5ff"), {"position": pos(-0.35, 0)}, stagger=0.07, duration=0.2,
          ease_spec=SNAP),

    typed("ic-play", "Play button cursor", "Cursor de reproducir", "build",
          glyph_caret("shape:play", "#ff2d55", height=0.7), {"scaleX": 0}, stagger=0.08, duration=0.18,
          ease_spec=SNAP),

    typed("ic-chevron", "Green chevron cursor", "Cursor en ángulo verde", "build",
          glyph_caret("shape:chevron", "#7cff4f", sway=8, hz=3.0), {"skew": -25, "position": pos(-0.15, 0)},
          stagger=0.07, duration=0.2, ease_spec=SNAP),

    typed("ic-slash", "Slash cursor tilt", "Cursor de barra inclinada", "build",
          glyph_caret("shape:slash", "#ff7a1a"), {"rotation": -30, "position": pos(0, 0.15)}, stagger=0.08,
          duration=0.22, ease_spec=SPRING),

    typed("ic-asterisk", "Spinning asterisk cursor", "Cursor de asterisco que gira", "build",
          glyph_caret("shape:asterisk", "#ff3b3b", sway=40, hz=3.0), {"scale": 0, "rotation": 120}, stagger=0.08,
          duration=0.22, ease_spec=SNAP),

    typed("ic-hashtag", "Hashtag cursor", "Cursor de hashtag", "stylized",
          glyph_caret("shape:hash", "#39ff14", blink=True), {"position": pos(0, 0.2)}, stagger=0.07, duration=0.25,
          fade=0.05, ease_spec=SNAP, extra=[flash("#39ff14")]),

    typed("ic-plus-flip", "Plus cursor with flips", "Cursor de más con giro", "stylized",
          glyph_caret("shape:plus", "#00d1ff", sway=45, hz=1.5), {"rotationY": 90}, stagger=0.08, duration=0.3,
          ease_spec=SNAP),

    typed("ic-check", "Check mark typing", "Escritura con visto", "particles",
          glyph_caret("shape:check", "#2ee66b", bob=0.04), {"position": pos(0, -0.25)}, stagger=0.09, duration=0.25,
          ease_spec=SPRING,
          particles=[burst("ring", 1, ("#2ee66b",), (0.35, 0.45), (0.0, 0.0), (0.3, 0.4), grow=2.2,
                           origin="center")]),

    typed("ic-diamond", "Diamond cursor shards", "Cursor de diamante con esquirlas", "particles",
          glyph_caret("shape:diamond", "#6ee7ff", sway=12), {"scale": 30, "rotation": 90}, stagger=0.08,
          duration=0.25, ease_spec=SNAP,
          particles=[burst("triangle", 6, ("#6ee7ff", "#ffffff"), (0.03, 0.06), (0.8, 1.8), (0.3, 0.55),
                           gravity=2.5, spin=360, glow=0.3)]),

    typed("ic-moon", "Moonlit typing", "Escritura a la luz de la luna", "stylized",
          glyph_caret("shape:moon", "#ffe9a8", bob=0.05, hz=1.0), {"blur": 10, "position": pos(0, -0.1)},
          stagger=0.13, duration=0.4, fade=0.7, ease_spec=SOFT,
          particles=[burst("star", 3, ("#fff6d6",), (0.03, 0.05), (0.1, 0.3), (0.6, 1.0), origin="area",
                           glow=0.5, fade_in=0.2)]),

    typed("ic-note", "Musical note typing", "Escritura musical", "particles",
          glyph_caret("shape:note", "#b86bff", bob=0.07, sway=15, hz=2.5), {"position": pos(0, 0.3)}, stagger=0.09,
          duration=0.28, ease_spec=SPRING,
          particles=[burst("glyph", 2, ("#b86bff", "#ff7ad9"), (0.12, 0.18), (0.4, 0.8), (0.6, 1.0),
                           angle=-90, spread=60, origin="top", glyph="shape:note", spin=30)]),

    typed("ic-flower", "Blooming typing", "Escritura que florece", "stylized",
          glyph_caret("shape:flower", "#ff8fc7", sway=20, hz=1.5), {"scale": 0, "rotation": -90}, stagger=0.09,
          duration=0.3, ease_spec=SPRING,
          particles=[burst("dot", 5, ("#ff8fc7", "#ffd1e6"), (0.03, 0.06), (0.4, 0.9), (0.4, 0.7),
                           gravity=0.8)]),

    typed("ic-drop", "Water drop typing", "Escritura con gota", "particles",
          glyph_caret("shape:drop", "#3aa0ff", bob=0.06, hz=1.5), {"position": pos(0, -0.6)}, stagger=0.09,
          duration=0.22, ease="easeIn", fade=0.1,
          particles=[burst("dot", 6, ("#3aa0ff", "#a8d8ff"), (0.03, 0.05), (0.8, 1.5), (0.3, 0.5),
                           angle=-90, spread=120, gravity=5.0, origin="bottom"),
                     burst("ring", 1, ("#a8d8ff",), (0.25, 0.3), (0.0, 0.0), (0.3, 0.4), grow=2.0,
                           origin="bottom")]),

    typed("ic-snowflake", "Snowflake typing", "Escritura con copo de nieve", "particles",
          glyph_caret("shape:snow", "#dff4ff", sway=25, hz=1.0), {"blur": 12, "scale": 110}, stagger=0.1,
          duration=0.35, fade=0.5, ease_spec=SOFT, extra=[flash("#bfe6ff")],
          particles=[burst("dot", 6, ("#ffffff", "#dff4ff"), (0.02, 0.05), (0.1, 0.35), (0.7, 1.1),
                           origin="top", spread=180, angle=90, gravity=0.6, glow=0.3)]),

    typed("ic-burst", "Burst cursor pops", "Cursor de estallido", "particles",
          glyph_caret("shape:burst", "#ffcf33", sway=20, hz=3.0), {"scale": 165}, stagger=0.08, duration=0.2,
          fade=0.05, ease_spec=SNAP, extra=[flash("#ffcf33")], trending=True,
          particles=[burst("spark", 8, ("#ffcf33", "#ff7a1a", "#ffffff"), (0.03, 0.06), (1.2, 2.4), (0.2, 0.4),
                           drag=2.5, **SPARK)]),

    typed("ic-dot-bounce", "Bouncing dot cursor", "Cursor de pelotita", "build",
          glyph_caret("shape:circle", "#ff5a36", height=0.35, bob=0.12, hz=3.0), {"position": pos(0, 0.35)},
          stagger=0.09, duration=0.3, ease_spec=SPRING),

    typed("ic-square-tumble", "Tumbling square cursor", "Cursor de cuadrito que gira", "build",
          glyph_caret("shape:square", "#8a5cff", height=0.5, sway=45, hz=2.0), {"scale": 0, "rotation": 45},
          stagger=0.08, duration=0.22, ease_spec=SNAP),

    typed("ic-neon-trail", "Neon trail typing", "Escritura con estela neón", "particles",
          bar_caret("bar", 0.08, 1.0, "#00f0ff"), {"position": pos(-0.5, 0), "blur": 6}, stagger=0.08,
          duration=0.3, fade=0.15, ease_spec=SNAP, extra=[flash("#00f0ff")], trending=True,
          particles=[stream("dot", 36, ("#00f0ff", "#7af9ff"), (0.03, 0.06), (0.05, 0.2), (0.2, 0.4),
                            angle=180, spread=30, origin="left", additive=True, glow=0.8, grow=0.4)]),

    # --- emoji carets -----------------------------------------------------------------------------
    typed("ic-pencil", "Pencil writing", "Escrito a lápiz", "build",
          glyph_caret("✏️", bob=0.03, sway=10, hz=4.0), {"wipe": {"enabled": True, "angleDeg": 0, "softness": 0.2}},
          stagger=0.12, duration=0.25, fade=None, ease="linear"),

    typed("ic-mic", "Microphone typing", "Escritura con micrófono", "particles",
          glyph_caret("🎤", sway=12, hz=2.5), {"scale": 125}, stagger=0.1, duration=0.25, ease_spec=SPRING,
          particles=[burst("ring", 2, ("#ffffff", "#ffd400"), (0.3, 0.4), (0.0, 0.1), (0.35, 0.5), grow=2.5)]),

    typed("ic-fire", "Fire cursor typing", "Escritura con fuego", "particles",
          glyph_caret("🔥", bob=0.04, hz=3.0), {"position": pos(0, 0.12)}, stagger=0.09, duration=0.35, fade=0.1,
          extra=[flash("#ff7a1a")], trending=True,
          particles=[burst("dot", 8, ("#ffcf33", "#ff7a1a", "#ff3b1a"), (0.04, 0.08), (0.6, 1.3), (0.35, 0.7),
                           angle=-90, spread=50, drag=1.5, grow=0.3, origin="top", **SPARK)]),

    typed("ic-rocket", "Rocket typing", "Escritura con cohete", "particles",
          glyph_caret("🚀", bob=0.03, hz=5.0), {"position": pos(-0.6, 0.1), "blur": 10}, stagger=0.07,
          duration=0.25, fade=0.15, ease_spec=SNAP,
          particles=[burst("smoke", 2, ("#cfd4dc", "#9aa3b0"), (0.25, 0.4), (0.1, 0.3), (0.5, 0.9), angle=180,
                           spread=50, origin="left", behind=True, grow=1.8, drag=1.0),
                     burst("spark", 4, ("#ffcf33", "#ff7a1a"), (0.03, 0.05), (1.0, 2.0), (0.15, 0.3), angle=180,
                           spread=40, origin="left", drag=3.0, **SPARK)]),
]
