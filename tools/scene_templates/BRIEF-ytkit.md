# Kit de YouTube: brief for the batches (2026-10-30)

Jorge approved the 11 prototypes in `templates_ytkit.py` (read it first: it is the reference for style, API and
quality). Now the full pack: ~150 pieces in **Stock › Kit de YouTube**, by section. Quality first: every piece has to
look like a professional motion-graphics kit, not a filler. Our own designs: never copy a commercial kit.

## Look
- One family: palette NAVY `#0B1A2E`, DEEP `#06101F`, TEAL `#2EE6C8`, CORAL `#FF5D73`, SUN `#FFD23F`, WHITE, MIST
  `#A9B8CC`. Variants are welcome (light version: white/`#F4F7FB` background with navy ink; coral-led; sun-led) but
  stay inside this palette.
- Fonts that exist in the app: Sora, Inter, Montserrat, Anton, Bebas Neue, Oswald, Archivo Black, Poppins, DM Sans,
  Outfit, Barlow Condensed, Playfair Display, Cormorant Garamond, Russo One, Orbitron.
- **No platform logos, no platform names in big type, no YouTube red.** Generic glyphs (@, #, ♪, ▶ drawn as a
  `triangle` shape) are fine.
- Motion: clean, eased, staggered (0.05–0.15 s), with an entrance AND (for overlays that sit on a video) a tidy exit
  before the end. Nothing static for more than ~1.5 s in openers / kinetic pieces.

## Rules (Jorge)
- **A text that comes out of a line or bar is born from it and never crosses it**: reveal it with
  `tanim("wipe", duration=0.6, angle=0, softness=0.15)` (left→right; the default −90 reveals bottom→top), or
  `angle=180` for right-aligned text coming out leftwards. Never `slide-right` across a line/shape.
- Every text editable (the default) with a clear Spanish `name=` («Nombre del canal», «Titular»…). Decorative
  glyphs `editable=False`.
- Every picture a slot (`t.photo(..., label="Tu video")`), logos with `label="Tu logo"` and samples `logo-01…08`.
- Overlays (lower thirds, bars, titles, social, elements, transitions) go over a sample photo/video slot or a
  separate background: the background is its own bottom track (`bg`, `bg_gradient`, `photo_bg`) so the user deletes
  it and lays the piece over their own video.
- Texts must fit their box at the given size (check the renders: no clipped or wrapped-by-accident words). Keep key
  content away from the edges (safe margin ~80 px on 1920×1080).
- Avoid photos with brands/logos; prefer the `h-*` samples (16:9) and plain ones for vertical (`portrait`, `city`,
  `travel`, `nature`, `podcast`, `creator`, `y4-*`, `y5-*`…). Look at the sample at full size if in doubt:
  `C:\Users\bajoe\Downloads\FlipStudio\tienda\plantillas\muestras\`.

## API (see `scene.py`, `kit.py`, `templates_ytkit.py`)
- `_kit(...)` lives in `templates_ytkit.py`; in your module define your own helper the same way:
  `wide(f"ytk-{id}", es, en, "ytkit", dur, order=..., tags=[f"kit:{section}", "youtube", ...], thumb_at=..., background=...)`
  and `tall(...)` (1080×1920) for vertical pieces (id ends in `-vertical`, extra tag `vertical`).
- Section keys: aperturas, tipografia, titulos-estilo, titulos-cineticos, tercios, frases, transiciones,
  barras-info, pantallas-finales, redes, elementos.
- Shape kinds: rectangle, rounded-rectangle, ellipse, hexagon, pentagon, diamond, triangle, star, cross, arrow,
  block-arrow, curved-arrow, parallelogram, banner, burst, speech-bubble, heart, lightning-bolt.
- Text presets: the files in `presets/text-animations/*.json` (ids = file names). Good ones: wipe, fade, rise,
  rise-by-word, fade-up-char, typewriter, stamp, pop, blur-in, tracking-drift, slide-up, ibs-digital-decode,
  imf-behind-edge, imf-slit-opening, imf-razor-wipe, imf-venetian-lines, om-soft-lift-wipe (out), pulse (loop).
- Music only on openers/kinetic/end screens: `song(t, mood, pick)` with moods from `kit.MOODS`.
- Traps: a channel's value before its first key is that first key (put `(0, value, "hold")` first); spikes on
  effects need `spike()`; Python on Windows: write files with `newline=""`.

## Workflow (each batch)
1. Write ONLY your module `templates_ytkit_<x>.py` (already registered in `templates.py`; don't touch
   `templates.py`, `kit.py`, `scene.py`, `templates_ytkit.py`). `TEMPLATES = [...]` at the end.
2. Render: `py build.py --only mod:templates_ytkit_<x> --exe "C:/Users/bajoe/Downloads/FlipStudio/pruebas/FlipStudio-0.27-prueba2/app/Flip Studio/flipstudio.exe" --out "C:/Users/bajoe/Downloads/FlipStudio/tienda/plantillas/ytkit-render"`
   (it takes a lock: other batches wait; that's fine). Use `--only ytk-a,ytk-b` to re-render single pieces.
3. Review: for each piece take 4–6 frames of `preview-wide.mp4` (vertical: `preview.mp4`) with ffmpeg
   (`ffmpeg -ss T -i … -frames:v 1 -vf scale=480:-1`), tile them into contact sheets with Pillow (open files by
   relative or Windows paths, not `/c/...`), and LOOK at them: entrances, the middle, the exit. Check also the
   start of each text entrance (0.1–0.3 s after it begins) for anything crossing a line.
4. Fix and re-render until every piece is good. Drop a piece rather than ship a weak one.
5. Report: the list of ids with one line each, and anything you were unsure about.
