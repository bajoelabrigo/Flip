"""In › Particles, batch A: celebration and magic (sparks, fireworks, confetti, glitter, hearts, bubbles…).

Every preset pairs its particles with a letter motion (pop, drop, blur that clears, a fill flash) so
the effect reads as one. Ids start with "ipa-".
"""

from __future__ import annotations

from tkit import (EXPO, SNAP, SOFT, SPRING, A, argb, burst, glyph_caret, pos, reveal, stagger_sel, stream,
                  typing)

CAT = "particles"

GOLD = ("#ffd34d", "#ffb52e", "#fff1b8")
WARM_WHITE = ("#ffffff", "#fff4cf")
RAINBOW = ("#ff4d6d", "#ff9f1c", "#ffe14d", "#3ddc84", "#2ec4ff", "#7b61ff", "#ff5fd2")
PARTY = ("#ff3d7f", "#ffd23f", "#3ec1ff", "#7cf06a", "#b26bff", "#ff8a3d")


def flash(color: str, mul: float = 1.7, ease: str = "easeIn") -> dict:
    """The letters arrive tinted and settle to their own fill a little after landing."""
    return A([stagger_sel(mul, ease=ease)], fillColor=argb(color))


def blur_clear(px: float = 14, mul: float = 0.8) -> dict:
    return A([stagger_sel(mul, ease="easeOut")], blur=px)


PRESETS = [
    # 1. Letters drop and skid: sparks fly sideways along the baseline.
    reveal("ipa-landing-sparks", "Sparks on landing", "Chispas al aterrizar", CAT,
           {"position": pos(0, -0.7)}, stagger=0.08, duration=0.32, ease_spec=SNAP,
           extra=[flash("#ffe27a", 1.4)],
           particles=[burst("spark", 7, ("#ffd34d", "#ffffff", "#ff9a2e"), (0.04, 0.07), (1.6, 3.0), (0.2, 0.45),
                            angle=0, spread=40, gravity=4, origin="baseline", additive=True, glow=0.4),
                      burst("spark", 7, ("#ffd34d", "#ffffff", "#ff9a2e"), (0.04, 0.07), (1.6, 3.0), (0.2, 0.45),
                            angle=180, spread=40, gravity=4, origin="baseline", additive=True, glow=0.4, seed=2)]),

    # 2. Each word pops and throws its own little firework.
    reveal("ipa-firework-words", "Firework words", "Fuegos por palabra", CAT,
           {"scale": 20}, unit="word", stagger=0.3, duration=0.35, ease_spec=SPRING, sample="BIG NEWS",
           particles=[burst("spark", 6, ("#ff4d6d", "#2ec4ff", "#ffe14d", "#ff5fd2"), (0.04, 0.08), (2.0, 3.4),
                            (0.45, 0.8), spread=360, drag=2.2, gravity=1.6, additive=True, glow=0.6),
                      burst("dot", 5, ("#ffffff", "#fff1b8"), (0.03, 0.05), (0.6, 1.4), (0.6, 1.0),
                            spread=360, drag=1.5, gravity=1.2, additive=True, glow=0.5, seed=3)]),

    # 3. The whole word zooms out of a blur and a multicolour firework opens behind it.
    reveal("ipa-fireworks-finale", "Fireworks finale", "Gran final de fuegos", CAT,
           {"scale": 0, "blur": 18}, unit="block", duration=0.55, ease_spec=EXPO, trending=True,
           lock={"unitLocked": True},
           particles=[burst("spark", 46, RAINBOW, (0.05, 0.09), (2.6, 4.2), (0.55, 1.0), at=0.7, spread=360,
                            drag=2.0, gravity=1.4, additive=True, glow=0.6, per="block"),
                      burst("dot", 30, ("#fff1b8", "#ffd34d"), (0.03, 0.05), (0.8, 1.8), (0.8, 1.2), at=0.7,
                            spread=360, drag=1.4, gravity=2.2, additive=True, glow=0.5, per="block", seed=4)]),

    # 4. Letters bounce down while confetti rains from above the block.
    reveal("ipa-confetti-drop", "Confetti drop", "Lluvia de confeti", CAT,
           {"position": pos(0, -0.9)}, stagger=0.07, duration=0.45, ease_spec=SPRING, trending=True,
           particles=[burst("confetti", 44, PARTY, (0.08, 0.14), (0.6, 1.6), (0.9, 1.2), at=0.0, angle=90,
                            spread=70, gravity=1.8, drag=0.6, origin="top", spin=420, per="block")]),

    # 5. Glitter dust glints all over each letter while it clears from a blur.
    reveal("ipa-glitter-dust", "Glitter dust reveal", "Polvo de brillantina", CAT,
           {"blur": 16, "scale": 112}, stagger=0.09, duration=0.5, fade=0.6,
           particles=[stream("flare", 30, ("#ffffff", "#e8e8ff", "#ffe9a8"), (0.06, 0.12), (0.05, 0.25),
                             (0.25, 0.55), spread=360, origin="area", additive=True, glow=0.7)]),

    # 6. Letters glide in from the left leaving a trail of tiny stars.
    reveal("ipa-fairy-trail", "Fairy dust trail", "Estela de hada", CAT,
           {"position": pos(-1.4, 0)}, stagger=0.1, duration=0.5, ease_spec=EXPO,
           particles=[stream("star", 28, ("#d9b8ff", "#ffc2e8", "#ffffff"), (0.05, 0.1), (0.15, 0.45),
                             (0.45, 0.85), angle=180, spread=50, gravity=0.6, origin="left", glow=0.5, spin=90)]),

    # 7. A springy pop with yellow stars bursting round each letter.
    reveal("ipa-star-pop", "Star burst pop", "Estallido de estrellas", CAT,
           {"scale": 0}, stagger=0.07, duration=0.4, ease_spec=SPRING, fade=0.3,
           particles=[burst("star", 8, ("#ffe14d", "#ffc400", "#ffffff"), (0.08, 0.14), (1.0, 2.2), (0.35, 0.7),
                            at=0.55, spread=360, drag=3.0, spin=200)]),

    # 8. Pink flash and hearts that float up as each letter pops.
    reveal("ipa-heart-burst", "Heart burst", "Explosión de corazones", CAT,
           {"scale": 30, "position": pos(0, 0.2)}, stagger=0.08, duration=0.4, ease_spec=SPRING, trending=True,
           extra=[flash("#ff5c9a", 1.8)],
           particles=[burst("heart", 6, ("#ff4d7d", "#ff8fb8", "#ff2d55"), (0.1, 0.18), (0.8, 1.6), (0.6, 1.0),
                            angle=-90, spread=150, gravity=-0.6, drag=1.6)]),

    # 9. Letters rise out of the water; bubbles drift up from below them.
    reveal("ipa-rising-bubbles", "Rising bubbles", "Burbujas que suben", CAT,
           {"position": pos(0, 0.6), "blur": 6}, stagger=0.1, duration=0.6, ease="easeOut", fade=0.7,
           particles=[stream("ring", 12, ("#bdf3ff", "#7fdcff", "#ffffff"), (0.1, 0.26), (0.5, 1.1), (0.6, 1.0),
                             angle=-90, spread=35, drag=0.8, origin="bottom", grow=1.3, fade_in=0.2)]),

    # 10. Snowflakes fall over the word as it un-blurs from an icy tint.
    reveal("ipa-snow-flurry", "Snow flurry", "Ráfaga de nieve", CAT,
           {"position": pos(0, -0.25), "blur": 12}, stagger=0.08, duration=0.6, ease="easeOut", fade=0.7,
           extra=[flash("#a8dcff", 1.6, "easeOut")],
           particles=[burst("glyph", 22, ("#ffffff", "#dff3ff"), (0.1, 0.2), (0.3, 0.7), (1.0, 1.2), at=0.0,
                            angle=90, spread=60, gravity=0.6, origin="top", spin=60, glyph="shape:snow",
                            per="block", fade_in=0.15)]),

    # 11. Letters swing in while flower petals drift down and to the side.
    reveal("ipa-falling-petals", "Falling petals", "Pétalos al viento", CAT,
           {"rotation": -25, "position": pos(0, -0.3)}, stagger=0.09, duration=0.55, ease_spec=SOFT,
           particles=[burst("glyph", 4, ("#ffb3c7", "#ffd6e0", "#ff8fab"), (0.12, 0.2), (0.4, 0.8), (0.8, 1.2),
                            at=0.4, angle=40, spread=60, gravity=0.8, origin="top", spin=140, glyph="shape:flower",
                            fade_in=0.15)]),

    # 12. Gold flash; coins fountain up and fall back with glints.
    reveal("ipa-gold-coins", "Gold coin sparkle", "Destello de monedas", CAT,
           {"position": pos(0, 0.5), "scale": 70}, stagger=0.07, duration=0.4, ease_spec=SPRING,
           extra=[flash("#ffc93c", 1.8)],
           particles=[burst("dot", 10, GOLD, (0.06, 0.1), (1.6, 2.6), (0.5, 0.9), angle=-90, spread=80, gravity=5,
                            glow=0.3),
                      burst("flare", 3, WARM_WHITE, (0.16, 0.26), (0.05, 0.2), (0.3, 0.5), origin="area",
                            additive=True, glow=0.8, seed=5)]),

    # 13. A soft wipe reveals each letter with sparkles at the wand's tip.
    reveal("ipa-magic-wand", "Magic wand reveal", "Varita mágica", CAT,
           {"wipe": {"enabled": True, "angleDeg": 0, "softness": 0.35}}, stagger=0.1, duration=0.35, ease="linear",
           fade=None, trending=True,
           particles=[stream("flare", 34, ("#ffffff", "#ffe9a8", "#c9a8ff"), (0.06, 0.13), (0.2, 0.6),
                             (0.3, 0.7), angle=-60, spread=120, gravity=0.8, origin="right", additive=True, glow=0.7),
                      stream("star", 10, ("#d7b8ff", "#ffd6f5"), (0.05, 0.09), (0.1, 0.4), (0.5, 0.9),
                             angle=90, spread=60, gravity=0.5, origin="right", spin=120, seed=6)]),

    # 14. A party popper fires confetti up from below as letters spring up.
    reveal("ipa-party-popper", "Party popper", "Lanzaconfeti", CAT,
           {"position": pos(0, 0.8), "scale": 60}, stagger=0.05, duration=0.42, ease_spec=SPRING, trending=True,
           particles=[burst("confetti", 54, PARTY, (0.08, 0.15), (3.0, 5.0), (0.9, 1.2), at=0.0, angle=-90,
                            spread=70, gravity=5.0, drag=1.2, origin="bottom", spin=520, per="block"),
                      burst("ring", 1, ("#ffffff",), (0.4, 0.4), (0.0, 0.0), (0.3, 0.3), at=0.0, origin="bottom",
                            grow=4.0, per="block", seed=7)]),

    # 15. The word slams down from big; gold sparks, a shockwave and smoke.
    reveal("ipa-golden-explosion", "Golden explosion", "Explosión dorada", CAT,
           {"scale": 260, "blur": 10}, unit="block", duration=0.3, ease_spec=SNAP, fade=0.4, trending=True,
           lock={"unitLocked": True}, extra=[flash("#ffffff", 2.2, "easeOut")],
           particles=[burst("spark", 50, ("#ffd34d", "#ff9a2e", "#fff1b8"), (0.05, 0.1), (3.0, 5.0), (0.4, 0.8),
                            spread=360, drag=2.6, gravity=1.0, additive=True, glow=0.6, per="block"),
                      burst("ring", 2, ("#ffe08a",), (0.6, 0.9), (0.0, 0.1), (0.35, 0.5), grow=4.5, glow=0.4,
                            additive=True, per="block", seed=8),
                      burst("smoke", 10, ("#8a6a3a", "#5a4630"), (0.6, 1.0), (0.3, 0.8), (0.8, 1.2), spread=360,
                            drag=1.5, behind=True, grow=1.8, per="block", seed=9)]),

    # 16. Letters fade in out of order; a big four-point glint flashes on each.
    reveal("ipa-shimmer-glints", "Shimmering arrival", "Llegada brillante", CAT,
           {"blur": 8}, stagger=0.1, duration=0.45, order="random", ease="easeOut", fade=0.8,
           particles=[burst("flare", 2, ("#ffffff", "#fff4cf"), (0.22, 0.38), (0.0, 0.08), (0.4, 0.65), at=0.7,
                            origin="area", additive=True, glow=0.9, spin=30)]),

    # 17. Letters bob up and music notes float away from each one.
    reveal("ipa-rising-notes", "Rising notes", "Notas que suben", CAT,
           {"position": pos(0, 0.45)}, stagger=0.09, duration=0.45, ease_spec=SPRING,
           particles=[burst("glyph", 3, ("#b78bff", "#4ad9ff", "#ff7ac6"), (0.18, 0.26), (0.6, 1.0), (0.8, 1.2),
                            angle=-80, spread=60, drag=0.6, spin=40, glyph="shape:note", fade_in=0.15)]),

    # 18. Letters spin in and throw an even ring of gold stars.
    reveal("ipa-star-ring", "Star ring burst", "Anillo de estrellas", CAT,
           {"rotation": 360, "scale": 0}, stagger=0.09, duration=0.5, ease_spec=EXPO, fade=0.3,
           particles=[burst("star", 10, ("#ffd34d", "#fff1b8"), (0.07, 0.1), (1.5, 1.6), (0.45, 0.6), spread=360,
                            drag=2.4, glow=0.5, spin=160)]),

    # 19. Letters turn in depth; ice-blue diamonds fall off them.
    reveal("ipa-diamond-shower", "Diamond shower", "Lluvia de diamantes", CAT,
           {"rotationY": 90}, stagger=0.08, duration=0.45, ease_spec=EXPO,
           particles=[burst("glyph", 5, ("#9feaff", "#ffffff", "#5cc8ff"), (0.1, 0.17), (0.8, 1.6), (0.6, 0.9),
                            angle=-90, spread=110, gravity=3.5, spin=220, glow=0.4, glyph="shape:diamond")]),

    # 20. Letters drop in while golden sparkles rain from their tops.
    reveal("ipa-sparkle-rain", "Sparkle rain", "Lluvia de destellos", CAT,
           {"position": pos(0, -0.5)}, stagger=0.08, duration=0.5, ease="easeOut", fade=0.6,
           particles=[stream("flare", 22, GOLD, (0.05, 0.1), (0.5, 1.0), (0.4, 0.8), angle=90, spread=25,
                             gravity=2.0, origin="top", additive=True, glow=0.6),
                      stream("dot", 14, ("#fff1b8",), (0.02, 0.04), (0.6, 1.2), (0.4, 0.8), angle=90, spread=20,
                             gravity=2.0, origin="top", additive=True, seed=10)]),

    # 21. Letters inflate red like balloons and pop: a ring and a puff of confetti.
    reveal("ipa-balloon-pop", "Balloon pop", "Globo que revienta", CAT,
           {"scale": 25}, stagger=0.1, duration=0.45, ease_spec=SOFT, fade=0.3,
           extra=[flash("#ff3b4e", 1.1, "linear")],
           particles=[burst("ring", 1, ("#ffffff",), (0.5, 0.5), (0.0, 0.0), (0.22, 0.22), grow=3.2),
                      burst("confetti", 10, PARTY, (0.06, 0.1), (1.4, 2.4), (0.5, 0.9), spread=360, drag=2.5,
                            gravity=2.5, spin=480, seed=11)]),

    # 22. Warm letters fade up; glowing lanterns drift slowly out of them.
    reveal("ipa-lantern-glow", "Lantern glow rise", "Faroles que suben", CAT,
           {"position": pos(0, 0.3), "blur": 10}, stagger=0.12, duration=0.6, ease_spec=SOFT, fade=0.7,
           extra=[flash("#ffb347", 1.8, "easeOut")],
           particles=[stream("dot", 8, ("#ffb347", "#ff8c42", "#ffd27a"), (0.08, 0.14), (0.2, 0.45), (0.8, 1.2),
                             angle=-90, spread=40, gravity=-0.4, origin="bottom", additive=True, glow=0.9,
                             grow=0.7, fade_in=0.25)]),

    # 23. Typed by a sparkler: a sparkle rides the last letter and sparks fly off each one.
    typing("ipa-sparkler", "Sparkler writing", "Bengala que escribe", CAT,
           glyph_caret("shape:sparkle", "#fff1b8", height=0.6, sway=25, hz=6), stagger=0.1, trending=True,
           particles=[burst("spark", 12, ("#fff4cf", "#ffd34d", "#ffffff"), (0.03, 0.05), (1.2, 2.4), (0.15, 0.35),
                            at=0.0, spread=360, gravity=3.0, origin="right", additive=True, glow=0.5)]),

    # 24. Letters flip down in depth with mirror-ball glints.
    reveal("ipa-disco-sparkle", "Disco sparkle", "Brillo disco", CAT,
           {"rotationX": -90}, stagger=0.08, duration=0.45, ease_spec=EXPO,
           extra=[flash("#c8f4ff", 1.5)],
           particles=[burst("square", 10, ("#ffffff", "#c8f4ff", "#ffc8f0"), (0.04, 0.07), (0.6, 1.4), (0.4, 0.8),
                            at=0.8, spread=360, drag=1.8, additive=True, glow=0.6, spin=320)]),

    # 25. Golden flash and a fizz of tiny bubbles shooting up from the baseline.
    reveal("ipa-champagne-fizz", "Champagne fizz", "Burbujas de champán", CAT,
           {"scaleY": 40, "position": pos(0, 0.25)}, stagger=0.06, duration=0.4, ease_spec=SPRING, fade=0.4,
           extra=[flash("#ffe39a", 1.8)],
           particles=[stream("dot", 36, ("#fff1c4", "#ffe39a", "#ffffff"), (0.025, 0.05), (1.0, 2.0), (0.3, 0.6),
                             angle=-90, spread=22, origin="baseline", glow=0.3, fade_in=0.1),
                      burst("ring", 4, ("#fff1c4",), (0.06, 0.1), (0.8, 1.6), (0.4, 0.7), angle=-90, spread=40,
                            grow=1.4, seed=12)]),

    # 26. Letters swing down; a piñata spill of candy shapes falls from the block.
    reveal("ipa-pinata-candy", "Piñata candy burst", "Piñata de dulces", CAT,
           {"rotation": 35, "position": pos(0, -0.6)}, stagger=0.07, duration=0.5, ease_spec=SPRING,
           particles=[burst("triangle", 14, PARTY, (0.08, 0.13), (1.6, 3.0), (0.7, 1.1), spread=360, gravity=4.5,
                            spin=260, per="block"),
                      burst("square", 14, PARTY, (0.06, 0.1), (1.6, 3.0), (0.7, 1.1), spread=360, gravity=4.5,
                            spin=260, per="block", seed=13),
                      burst("dot", 14, PARTY, (0.06, 0.1), (1.6, 3.0), (0.7, 1.1), spread=360, gravity=4.5,
                            per="block", seed=14)]),

    # 27. Letters streak in diagonally like shooting stars, trails behind them.
    reveal("ipa-shooting-stars", "Shooting star letters", "Letras fugaces", CAT,
           {"position": pos(1.2, -1.2)}, stagger=0.1, duration=0.4, ease_spec=EXPO,
           particles=[stream("spark", 34, ("#ffffff", "#bfe3ff", "#8fd0ff"), (0.04, 0.07), (0.6, 1.2),
                             (0.15, 0.35), angle=-45, spread=18, origin="center", additive=True, glow=0.6),
                      burst("flare", 1, ("#ffffff",), (0.4, 0.5), (0.0, 0.0), (0.3, 0.4), additive=True, glow=0.8,
                            seed=15)]),

    # 28. Letters grow out of a blur; a glowing halo ripples out of each.
    reveal("ipa-halo-ripple", "Halo ripple", "Onda de halo", CAT,
           {"scale": 70, "blur": 12}, stagger=0.1, duration=0.45, ease="easeOut", fade=0.6,
           particles=[burst("ring", 2, ("#fff1b8", "#ffffff"), (0.5, 0.7), (0.0, 0.05), (0.45, 0.6), at=0.75,
                            grow=3.0, glow=0.6, additive=True)]),

    # 29. Each word pops round and throws rainbow dots in every direction.
    reveal("ipa-rainbow-burst", "Rainbow burst", "Estallido arcoíris", CAT,
           {"scale": 0, "rotation": -90}, unit="word", stagger=0.25, duration=0.45, ease_spec=SPRING,
           sample="YAY PARTY",
           particles=[burst("dot", 14, RAINBOW, (0.06, 0.11), (1.4, 2.8), (0.45, 0.8), at=0.6, spread=360,
                            drag=2.6, glow=0.3)]),

    # 30. Letters fade up softly while little hearts float up from their tops.
    reveal("ipa-floating-hearts", "Floating hearts", "Corazones flotantes", CAT,
           {"position": pos(0, 0.25), "scale": 90}, stagger=0.12, duration=0.6, ease_spec=SOFT, fade=0.7,
           particles=[stream("heart", 8, ("#ff8fb8", "#ffc2d9", "#ffffff"), (0.08, 0.14), (0.3, 0.6), (0.8, 1.2),
                             angle=-90, spread=50, gravity=-0.3, origin="top", spin=120, fade_in=0.2)]),

    # 31. A magician's poof: purple smoke behind each letter and stars popping out.
    reveal("ipa-magic-poof", "Magic poof", "Puf de magia", CAT,
           {"scale": 0}, stagger=0.1, duration=0.3, ease_spec=SPRING, fade=0.2,
           particles=[burst("smoke", 5, ("#8b5cf6", "#c4a5ff"), (0.5, 0.8), (0.3, 0.7), (0.6, 1.0), at=0.0,
                            spread=360, drag=2.0, behind=True, grow=1.7),
                      burst("star", 6, ("#ffe14d", "#ffffff", "#e0c3ff"), (0.06, 0.1), (1.2, 2.0), (0.3, 0.6),
                            at=0.3, spread=360, drag=2.5, spin=240, glow=0.4, seed=16)]),

    # 32. The word flies in from the right with a fiery comet tail.
    reveal("ipa-comet-arrival", "Comet arrival", "Llegada de cometa", CAT,
           {"position": pos(1.2, 0, "box")}, unit="block", duration=0.6, ease_spec=EXPO, fade=0.3,
           lock={"unitLocked": True},
           particles=[stream("spark", 70, ("#ffffff", "#ffd34d", "#ff8a3d"), (0.05, 0.1), (1.0, 2.2), (0.2, 0.5),
                             angle=0, spread=20, origin="right", additive=True, glow=0.6, per="block"),
                      stream("smoke", 16, ("#ff8a3d",), (0.3, 0.5), (0.4, 0.8), (0.4, 0.7), angle=0, spread=30,
                             origin="right", additive=True, behind=True, grow=1.5, per="block", seed=17)]),

    # 33. A glitter bomb goes off at the centre and the letters clear out of the blur.
    reveal("ipa-glitter-bomb", "Glitter bomb", "Bomba de brillantina", CAT,
           {"blur": 20, "scale": 85}, stagger=0.05, duration=0.55, order="centerOut", ease="easeOut", fade=0.6,
           particles=[burst("dot", 90, ("#ff7ad9", "#ffd34d", "#e6e6f0", "#5ce1ff"), (0.025, 0.05), (2.0, 5.0),
                            (0.6, 1.1), at=0.0, spread=360, drag=3.0, gravity=1.2, additive=True, glow=0.4,
                            per="block"),
                      burst("flare", 16, ("#ffffff",), (0.08, 0.14), (1.5, 3.5), (0.4, 0.8), at=0.0, spread=360,
                            drag=3.0, additive=True, glow=0.7, per="block", seed=18)]),

    # 34. Letters wave in on a curve; long paper streamers tumble out.
    reveal("ipa-streamers", "Streamers", "Serpentinas", CAT,
           {"position": pos(0, 0.5), "rotation": 20, "scale": 60}, stagger=0.08, duration=0.5, ease_spec=SPRING,
           particles=[burst("confetti", 4, ("#ff3d7f", "#3ec1ff", "#ffd23f", "#7cf06a"), (0.2, 0.3), (0.7, 1.4),
                            (0.8, 1.2), angle=-90, spread=200, gravity=1.6, drag=0.8, spin=200)]),

    # 35. Letters rise like birthday candles, each with a flickering little flame.
    reveal("ipa-birthday-candles", "Birthday candles", "Velas de cumpleaños", CAT,
           {"position": pos(0, 0.5), "scaleY": 50}, stagger=0.1, duration=0.45, ease_spec=EXPO,
           particles=[stream("dot", 22, ("#ffd34d", "#ff9a2e", "#fff4cf"), (0.06, 0.1), (0.25, 0.5), (0.3, 0.5),
                             angle=-90, spread=20, origin="top", additive=True, glow=0.8, grow=0.4),
                      burst("flare", 1, ("#fff4cf",), (0.3, 0.3), (0.0, 0.0), (0.35, 0.35), origin="top",
                            additive=True, glow=0.9, seed=19)]),

    # 36. Letters stamp down from big and a fountain of sparks arcs up and falls.
    reveal("ipa-spark-fountain", "Spark fountain", "Fuente de chispas", CAT,
           {"scale": 160}, stagger=0.09, duration=0.3, ease_spec=SNAP, fade=0.5,
           extra=[flash("#ffcf5a", 1.6)],
           particles=[burst("spark", 14, ("#ffd34d", "#ff8a3d", "#ffffff"), (0.035, 0.06), (2.6, 4.0), (0.5, 0.9),
                            angle=-90, spread=30, gravity=7.0, origin="top", additive=True, glow=0.5)]),
]
