# Text › Animation: the new built-in presets (brief for whoever designs them)

Jorge (owner of Flip Studio) asked for text animations like Filmora's Titles › Animation galleries.
His screenshots (look at them, they are the reference):

- In, page 1 (motion-type, ~108): `C:\Users\bajoe\Downloads\animacion - Entrada 1.png`
- In, page 2 (effects/particles/emoji cursors, ~92): `C:\Users\bajoe\Downloads\animacion - Entrada 2.png`
- Out (~85): `C:\Users\bajoe\Downloads\Animacion - Salida.png`

Make **our own versions** of that kind of catalogue, not copies (no Filmora names, no exact clones).
Quality first: every preset must look good and read clearly on a short word like "ABCD", in the 104×58
gallery tile and on a real 1080×1920 video. Variety matters more than count: two presets that look the
same are one preset.

## Where things go

- Designs: one Python module per batch in this folder (`in_*.py` or `out_*.py`), exporting `PRESETS`, a
  list of `tkit.T`. Ids are kebab-case and **start with the module's prefix** given in your task, so
  batches never clash. `py tools/text_animations/build.py --check <module>` checks one module without
  writing anything. **Do not run build.py without --check** and do not render: the lead runs the full
  build and renders review sheets once the new engine is compiled.
- Each preset has an English label (`en`, what the catalogue shows, translated by i18n) and a Spanish
  name (`es`, Jorge's language: natural Latin American Spanish, short, no Filmora names). Labels must be
  unique within a gallery (In or Out) across all batches: make them specific ("Sparks on landing",
  "Gold dust trail"), never "Animation 3".
- `cat` is the gallery chip: `motion` (Motion & path), `mask` (Mask & reveal / Hide & mask), `fluid`,
  `build` (letter by letter / staggered), `stylized`, `particles`. Mark about one in five of your best as
  `trending=True`.
- Sample text: leave the default "ABCD" unless the motion needs words (then a short English phrase).

## The engine (what a preset can do)

Read `tools/text_animations/tkit.py` (helpers and units), `src/core/TextAnimator.h` (the full model),
the 47 hand-made presets in `presets/text-animations/*.json`, and the 200 Stock animations in
`tools/text_stock/anims_a.py` and `anims_b.py` (the same language through `rv`, `curve_in`, `lp`: very
good examples of what reads well; do not duplicate them one-to-one).

- **Animators**: selectors pick fragments (character / word / line / block) and give a coverage 0..1;
  the props are applied scaled by that coverage. Props: `position` (pos(x, y, unit="em"|"box"|"px")),
  `scale`/`scaleX`/`scaleY` (%), `rotation`, `skew`, **`rotationX` / `rotationY`** (new: turns in depth
  with perspective, per fragment, or the whole block when the selector's domain is block), `opacity`,
  `fillOpacity`, `strokeOpacity`, `fillColor`, `strokeColor` ('#aarrggbb' via argb()), `strokeWidth`,
  `blur` (px), `tracking`, `lineSpacing`, `wipe` ({"enabled": True, "angleDeg": -90, "softness": 0.3}:
  a soft mask that reveals the fragment along that direction).
- **Selectors**: "stagger" (the reveal: each fragment ramps over `duration` after `stagger` seconds
  per slot, in `order` forward / backward / centerOut / random, with `ease`), curves windows
  (`sweep`, `everything`, `curve()` params that change over the slot's progress), `wiggle` (a wave
  over time), `karaoke`.
- **In vs Out**: In coverage 1 = away, 0 = home. The same animator in Out sends fragments away. A preset
  in both slots has its positions mirrored for Out (flags.mirrorForOut false to stop that). Prefer
  presets for **one** slot (`slots=("in",)` or `("out",)`): Filmora's In and Out galleries differ.
- **Glyph caret** (new): `glyph_caret("⚡")` or a vector symbol `glyph_caret("shape:bolt", "#ffd400")`
  rides after the last letter shown while letters appear (use with `typing()` or any staggered reveal)
  and then goes away (`hold` param). Vector symbols: bolt, diamond, heart, star, sparkle, burst, arrow,
  play, chevron, check, plus, hash, slash, asterisk, circle, square, moon, note, flower, drop, snow;
  they take a colour. Emoji keep their own colours but depend on the user's fonts: **prefer vector
  symbols**, use emoji only where nothing else says it (🔥 🎤 👍 👻 💀 🎃 🔔 🚀…), at most ~10 per batch.
  Options: height (em), gap, bob (em), sway (deg), hz, blink. `bar_caret("bar"|"underscore"|"block",
  color=...)` is the classic blinking cursor.
- **Particles** (new): `burst(...)` throws N particles from each fragment once, at `at` of its own
  motion (In: usually 1.0 = when it lands; Out: 0.0..0.3 = as it leaves); `stream(...)` gives them off
  continuously while each fragment moves (all the time in a Loop). Shapes: dot, star, spark (a streak
  along its flight, great for fireworks/explosions), ring (expanding outline: shockwaves, bubbles),
  square, heart, smoke (soft puff; use `behind=True`, big sizes, slow speed, `grow` > 1), confetti
  (tumbling strip), flare (4-point glint), triangle, glyph (any vector symbol or emoji). Options: colours
  (picked per particle), size (em), speed (em/s), life (s), angle (-90 = up) and spread (cone width,
  360 = all round), gravity (em/s², + falls), drag (1/s), origin (center, area = anywhere on the
  letter, top, bottom, left, right, baseline), glow (0..1 halo), additive (light that adds up: fire,
  sparks, energy), grow, spin (deg/s), fade_in, per="block" (one emitter at the block's centre instead
  of one per letter), seed. A preset can carry several specs (a list), or `{"in": [...], "out": [...]}`.
  Keep it tasteful: 6–20 particles per letter per burst, streams 10–40/s per letter, life under ~1.2 s.
  Combine particles with the letters' own motion (a flash of `fillColor`, a blur that clears, a scale
  pop) so the effect reads as one.
- What it **cannot** do: images or textures, real fluid/fire simulation, per-pixel distortion of the
  glyphs, masks other than the wipe, 3D extrusion over time. Fire = additive orange/yellow dots and
  sparks rising with drag and `grow` < 1, plus smoke behind; lightning = spark streaks + a white
  fillColor flash + a bolt glyph; smoke = big soft puffs behind the text while it un-blurs.

## Checklist before you hand in

- `py tools/text_animations/build.py --check <module>` prints 0 problems.
- Every preset reads at 0.4–1.2 s total for "ABCD" (stagger × letters + duration); particles live a
  little after.
- No two presets in your batch look alike; nothing duplicates the 47 hand-made ones.
- Write files with `\n` line endings (open(..., newline="\n") if you generate code with Python).
