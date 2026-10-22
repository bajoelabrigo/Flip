"""Text › Animation, In: Mask & reveal and Fluid (batch imf-).

Mask: the `wipe` prop in every direction and softness, per letter / word / line / block, combined with
scale, blur, fill and outline so each one reads differently. Fluid: overshooting eases (SPRING, back,
bounce, custom beziers) and two staggered animators with different lengths, so scaleX and scaleY settle
out of phase (a wobble per letter); the curves ones squash on landing.
"""

from __future__ import annotations

from tkit import (A, EXPO, SNAP, SOFT, SPRING, argb, bezier, burst, curve, curves, per_char, pos, reveal,
                  stagger_sel, whole)

MASK = "mask"
FLUID = "fluid"


def wipe(angle: float, softness: float) -> dict:
    return {"enabled": True, "angleDeg": angle, "softness": softness}


WOBBLE = bezier(0.3, 1.9, 0.5, 1.0)      # a second, later overshoot for out-of-phase wobbles
STRETCHY = bezier(0.25, 2.4, 0.4, 1.0)   # rubber band: big overshoot
LIFT = bezier(0.2, 1.4, 0.4, 1.0)        # a gentle overshoot

MASK_PRESETS = [
    # 1. letters unveiled from the top edge while they settle down
    reveal("imf-drop-down-unveil", "Drop-down unveil", "Telón que baja por letra", MASK,
           {"wipe": wipe(90, 0.25), "position": pos(0, -0.22)}, unit="character", stagger=0.05, duration=0.45,
           fade=None, ease_spec=EXPO),
    # 2. a soft left-to-right sweep per word
    reveal("imf-soft-sweep-words", "Soft sweep by word", "Barrido suave por palabra", MASK,
           {"wipe": wipe(0, 0.55), "position": pos(-0.12, 0)}, sample="NEW DROP", unit="word", stagger=0.16,
           duration=0.55, fade=None, ease_spec=SOFT),
    # 3. one crisp edge crossing the whole block from the right
    reveal("imf-razor-wipe", "Razor wipe from the right", "Corte limpio desde la derecha", MASK,
           {"wipe": wipe(180, 0.02)}, unit="block", duration=0.55, ease="easeInOut", fade=None,
           lock={"unitLocked": True, "orderLocked": True}),
    # 4. venetian blinds: each line opens vertically behind a top-down mask
    reveal("imf-venetian-lines", "Venetian blinds", "Persiana veneciana", MASK,
           {"wipe": wipe(90, 0.1), "scaleY": 0}, sample="BIG\nNEWS", unit="line", stagger=0.14, duration=0.45,
           fade=None, ease_spec=SNAP),
    # 5. a thin bright slit that opens into the word
    reveal("imf-slit-opening", "Slit opening", "Rendija que se abre", MASK,
           {"scaleY": 4, "scaleX": 118, "fillColor": argb("#ffffff"), "wipe": wipe(-90, 0.6)}, unit="block",
           duration=0.55, fade=0.2, ease_spec=EXPO, lock={"unitLocked": True, "orderLocked": True},
           trending=True),
    # 6. curtain from the centre: middle letters open first, squeezed horizontally
    reveal("imf-centre-curtain", "Centre curtain", "Cortina desde el centro", MASK,
           {"scaleX": 0, "wipe": wipe(0, 0.6)}, unit="character", order="centerOut", stagger=0.07, duration=0.5,
           fade=None, ease_spec=EXPO, trending=True),
    # 7. a very soft sweep that also brings the block into focus
    reveal("imf-sharpening-sweep", "Sharpening sweep", "Barrido que enfoca", MASK,
           {"wipe": wipe(0, 0.9), "blur": 28, "scale": 106}, unit="block", duration=0.8, fade=None,
           ease_spec=SOFT, lock={"unitLocked": True, "orderLocked": True}),
    # 8. a white outline sweeps in first and the fill catches up
    reveal("imf-outline-sweep-fill", "Outline sweep, then fill", "Contorno que barre y se rellena", MASK,
           {"wipe": wipe(0, 0.04)}, unit="block", duration=0.45, ease="easeOut", fade=None,
           lock={"unitLocked": True, "orderLocked": True},
           extra=[A([stagger_sel(1.9, ease="easeInOut")], fillOpacity=0, strokeColor=argb("#ffffff"), strokeWidth=3)],
           trending=True),
    # 9. letters fade in through a warm colour that settles to the text's own
    reveal("imf-colour-through", "Fade through colour", "Aparece con destello de color", MASK,
           {"fillColor": argb("#ffd84a"), "strokeColor": argb("#ff8a00"), "blur": 6}, unit="character",
           stagger=0.07, duration=0.55, fade=0.3, ease_spec=SOFT),
    # 10. stroke first: a thick light outline draws each letter, then the fill flows in
    reveal("imf-stroke-first", "Stroke-first letters", "Primero el trazo, luego el relleno", MASK,
           {"strokeOpacity": 0, "scale": 92}, unit="character", stagger=0.08, duration=0.6, fade=None,
           ease_spec=EXPO,
           extra=[A([stagger_sel(1.5, ease=SOFT)], fillOpacity=0, strokeWidth=6, strokeColor=argb("#ffffff"))]),
    # 11. camera shutter: random letters snap open top-down with a flash
    reveal("imf-shutter-snap", "Shutter snap", "Obturador", MASK,
           {"scaleY": 0, "wipe": wipe(90, 0.05), "fillColor": argb("#ffffff")}, unit="character", order="random",
           stagger=0.04, duration=0.22, fade=None, ease_spec=SNAP),
    # 12. the block zooms down from big while a soft top-down mask uncovers it
    reveal("imf-zoom-through-wipe", "Zoom-through wipe", "Barrido con zoom", MASK,
           {"scale": 150, "wipe": wipe(90, 0.7), "blur": 8}, unit="block", duration=0.65, fade=0.4,
           ease_spec=EXPO, lock={"unitLocked": True, "orderLocked": True}),
    # 13. erase in: the last letter comes first, each one wiped from the right
    reveal("imf-rewind-erase", "Rewind erase-in", "Borrado al revés", MASK,
           {"wipe": wipe(180, 0.1), "position": pos(0.12, 0)}, unit="character", order="backward", stagger=0.06,
           duration=0.3, ease="linear", fade=None),
    # 14. words drop through a top mask in random order
    reveal("imf-words-through-mask", "Words through a mask", "Palabras tras la máscara", MASK,
           {"wipe": wipe(90, 0.35), "position": pos(0, -0.35)}, sample="MADE FOR YOU", unit="word",
           order="random", stagger=0.12, duration=0.5, fade=None, ease_spec=SNAP),
    # 15. diagonal unveil per letter, straightening a slant
    reveal("imf-diagonal-unveil", "Diagonal letter unveil", "Revelado diagonal por letra", MASK,
           {"wipe": wipe(-45, 0.5), "skew": -18}, unit="character", stagger=0.045, duration=0.45, fade=None,
           ease_spec=EXPO),
    # 16. a hard edge lifts the whole block, stretched tall, settling
    reveal("imf-hard-edge-rise", "Hard-edge rise", "Subida con borde duro", MASK,
           {"wipe": wipe(-90, 0.02), "scaleY": 135}, unit="block", duration=0.5, fade=None, ease_spec=SNAP,
           lock={"unitLocked": True, "orderLocked": True}),
    # 17. ink bleed: very soft edges and a blur that soaks in
    reveal("imf-ink-bleed", "Soft ink bleed", "Tinta que se expande", MASK,
           {"wipe": wipe(0, 1.0), "blur": 10, "strokeWidth": 4}, unit="character", stagger=0.09, duration=0.7,
           fade=None, ease_spec=SOFT),
    # 18. the block slides out from behind a fixed edge (the mask moves against the motion)
    reveal("imf-behind-edge", "Emerge from behind an edge", "Sale detrás de un borde", MASK,
           {"wipe": wipe(0, 0.0), "position": pos(-0.7, 0)}, unit="block", duration=0.6, fade=None,
           ease_spec=EXPO, lock={"unitLocked": True, "orderLocked": True}),
]

FLUID_PRESETS = [
    # 1. letters spring up from flat and wide
    reveal("imf-springy-letters", "Springy letters", "Letras de resorte", FLUID,
           {"scaleY": 0, "scaleX": 140}, unit="character", stagger=0.05, duration=0.55, fade=0.3,
           ease_spec=SPRING),
    # 2. jelly: scaleY and scaleX overshoot out of phase, so each letter wobbles
    reveal("imf-jelly-wobble", "Jelly wobble", "Gelatina por letra", FLUID,
           {"scaleY": 20}, unit="character", stagger=0.06, duration=0.6, fade=0.3, ease_spec=SPRING,
           extra=[A([stagger_sel(1.35, ease=WOBBLE)], scaleX=170)], trending=True),
    # 3. drip: drops fall stretched, splat flat and spring back
    curves("imf-drip-splat", "Drip and splat", "Gota que se aplasta", FLUID,
           [per_char(position=pos(0, curve([(0, -1.5), (0.45, 0), (1, 0)]), "em"),
                     scaleY=curve([(0, 150), (0.42, 135), (0.5, 62), (0.64, 112), (0.8, 96), (1, 100)]),
                     scaleX=curve([(0, 60), (0.42, 75), (0.5, 135), (0.64, 92), (0.8, 103), (1, 100)]),
                     opacity=curve([(0, 0), (0.15, 100), (1, 100)]))], duration=0.8, trending=True),
    # 4. liquid rise: letters rise stretched and blurred, then settle
    reveal("imf-liquid-rise", "Liquid rise", "Subida líquida", FLUID,
           {"position": pos(0, 0.8), "scaleY": 180, "scaleX": 80, "blur": 6}, unit="character", stagger=0.04,
           duration=0.6, fade=0.4, ease_spec=LIFT),
    # 5. rubber band: the block snaps in from very wide with a big elastic overshoot
    reveal("imf-rubber-band", "Rubber band snap", "Liga elástica", FLUID,
           {"scaleX": 260}, unit="block", duration=0.7, fade=0.25, ease_spec=STRETCHY,
           extra=[A([stagger_sel(0.8, ease="back")], scaleY=50)], lock={"unitLocked": True, "orderLocked": True},
           trending=True),
    # 6. feather float: slow, gentle, slightly tilted
    reveal("imf-feather-float", "Feather float", "Pluma que flota", FLUID,
           {"position": pos(0, 0.5), "rotation": -8}, unit="character", stagger=0.08, duration=0.9, fade=0.6,
           ease_spec=SOFT),
    # 7. wavy arrival: letters rise and their tilt overshoots later, like a ripple
    reveal("imf-wavy-arrival", "Wavy arrival", "Llegada ondulante", FLUID,
           {"position": pos(0, 0.6)}, unit="character", stagger=0.05, duration=0.5, ease="back", fade=0.35,
           extra=[A([stagger_sel(1.4, ease=SPRING)], rotation=22)]),
    # 8. bubble pop: random letters inflate past full size with a little ring
    reveal("imf-bubble-pop", "Bubble pop", "Burbuja que revienta", FLUID,
           {"scale": 0}, unit="character", order="random", stagger=0.06, duration=0.4, ease="back", fade=0.25,
           particles=[burst("ring", count=2, colors=("#bfefff", "#ffffff"), size=(0.35, 0.55), speed=(0.05, 0.15),
                            life=(0.3, 0.45), grow=1.8, at=0.6)], trending=True),
    # 9. bounce drop from the middle out, stretched on the way down
    reveal("imf-centre-bounce-drop", "Centre-out bounce drop", "Rebote desde el centro", FLUID,
           {"position": pos(0, -1.1), "scaleY": 125, "scaleX": 88}, unit="character", order="centerOut",
           stagger=0.06, duration=0.65, ease="bounce", fade=0.2, lock={"easeLocked": True}),
    # 10. melt in: flattened, blurred letters condense into shape
    reveal("imf-melt-in", "Melt into shape", "Se derrite al revés", FLUID,
           {"scaleY": 40, "scaleX": 125, "blur": 18, "position": pos(0, 0.25)}, unit="character", stagger=0.07,
           duration=0.8, fade=0.5, ease_spec=SOFT),
    # 11. gooey merge: wide tracking pulls together with a springy overshoot
    reveal("imf-gooey-merge", "Gooey merge", "Fusión viscosa", FLUID,
           {"tracking": 0.9, "trackingUnit": "em", "blur": 12, "scaleY": 130}, unit="block", duration=0.75,
           fade=0.35, ease_spec=SPRING, lock={"unitLocked": True, "orderLocked": True}),
    # 12. squishy hop: flat letters pop up from the right end
    reveal("imf-squishy-hop", "Squishy hop", "Salto blandito", FLUID,
           {"scaleY": 30, "scaleX": 160, "position": pos(0, 0.3)}, unit="character", order="backward",
           stagger=0.06, duration=0.5, ease="back", fade=0.3),
    # 13. dangling letters: they swing in from above and settle like pendulums
    reveal("imf-dangling-letters", "Dangling letters", "Letras colgantes", FLUID,
           {"rotation": 65, "position": pos(0, -0.4)}, unit="character", stagger=0.07, duration=0.7, fade=0.3,
           ease_spec=SPRING),
    # 14. springboard words: words shoot up stretched and overshoot
    reveal("imf-springboard-words", "Springboard words", "Palabras de trampolín", FLUID,
           {"position": pos(0, 0.9), "scaleY": 145, "scaleX": 85}, sample="HELLO THERE", unit="word",
           stagger=0.13, duration=0.6, fade=0.3, ease_spec=SPRING),
    # 15. jello skew: the block shakes its slant out
    curves("imf-jello-skew", "Jello skew shake", "Temblor de gelatina", FLUID,
           [whole(skew=curve([(0, 32), (0.22, -20), (0.42, 12), (0.6, -6), (0.78, 2.5), (1, 0)]),
                  scaleX=curve([(0, 70), (0.22, 112), (0.42, 95), (0.6, 102), (1, 100)]),
                  opacity=curve([(0, 0), (0.12, 100), (1, 100)]))], duration=0.85),
    # 16. blob bloom: narrow, tall, blurry blobs swell into letters from the centre
    reveal("imf-blob-bloom", "Blob bloom", "Mancha que florece", FLUID,
           {"scaleX": 0, "scaleY": 160, "blur": 22}, unit="character", order="centerOut", stagger=0.05,
           duration=0.55, ease="back", fade=0.3),
    # 17. stretchy slide: letters arrive from the right leaning and stretched, then spring back
    reveal("imf-stretchy-slide", "Stretchy slide", "Deslizamiento elástico", FLUID,
           {"position": pos(1.4, 0), "skew": -28, "scaleX": 150}, unit="character", stagger=0.04, duration=0.6,
           fade=0.3, ease_spec=WOBBLE),
    # 18. water ripple: letters rise while tipping in depth, with a late springy settle
    reveal("imf-water-ripple", "Water ripple in", "Onda de agua", FLUID,
           {"position": pos(0, 0.35), "scaleY": 70}, unit="character", order="random", stagger=0.05, duration=0.5,
           fade=0.4, ease_spec=SOFT, extra=[A([stagger_sel(1.5, ease=SPRING)], rotationX=70)]),
]

PRESETS = MASK_PRESETS + FLUID_PRESETS
