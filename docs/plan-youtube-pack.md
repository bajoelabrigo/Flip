# YOUTUBE PACK → Stock (Kit de YouTube), 2026-11-08

Jorge: «ahora vas a hacer las de la carpeta pack de YouTube, sigue las mismas reglas, haces todos los videos y al final
lo reviso; si alguna animación no la tienes creas el motor, no inventes sino busca la manera de hacerlo».

Videos in `C:\Users\bajoe\Downloads\EDITAR PARA STOCK\YOUTUBE PACK` (`*-hecho.mp4` are already done; `pack youtube 6`
is the same file as `pack youtube 5`):

| Video | Prefix / module | Order range | Output folder (E:\FlipStudio\tienda\plantillas\…) |
|---|---|---|---|
| 38664567.mp4 (subscribe widgets over footage, 1920×1080) | `yp0-*`, `templates_yp0.py` | 12000–12099 | `prototipos-yp0` |
| pack youtube 1.mp4 (960×540, red/black pack) | `yp1-*`, `templates_yp1.py` | 12100–12299 | `prototipos-yp1` |
| pack youtube 2.mp4 | `yp2-*`, `templates_yp2.py` | 12300–12499 | `prototipos-yp2` |
| pack youtube 3.mp4 (subscribe buttons, end screens) | `yp3-*`, `templates_yp3.py` | 12500–12699 | `prototipos-yp3` |
| pack youtube 4.mp4 (vertical stories, 9:16) | `yp4-*`, `templates_yp4.py` | 12700–12899 | `prototipos-yp4` |
| pack youtube 5.mp4 (140 elements) | `yp5-*`, `templates_yp5.py` | 12900–13299 | `prototipos-yp5` |
| pack youtube 7.mp4 (mograph pack) | `yp7-*`, `templates_yp7.py` | 13300–13599 | `prototipos-yp7` |

The modules already exist (empty `TEMPLATES = []`) and are registered in `templates.py`: only edit your own module.

## Rules (Jorge, all of them still apply)

- **Copy, don't invent.** Each element as close as possible to the reference *including its transitions and moves*:
  study it frame by frame before writing it. Same layout, colours, fonts (closest we have), timing order.
- **What counts as an element:** every distinct title, lower third, button, end screen, social bar, transition,
  background, call-out, counter… that the video shows clearly enough to copy (full screen or in a 2×2 / 3×3 grid).
  Skip: the product-box/mockup shots, the After Effects interface shots, «148 items» counters about the pack itself,
  illegible thumbnails.
- **Logos:** where the reference shows the YouTube play button/logo, draw a YouTube play button (`S.yt` in
  `templates_tit_h`); where it shows another logo or a channel avatar, use the `logo-flip` slot
  (`t.photo(..., "logo-flip", ..., label="Tu logo", brandRole="logo")`) or a photo slot for avatars.
  Other brands (Envato, Videohive, After Effects, Mograph…) → neutral words («YOUR CHANNEL», «TITLES TEMPLATE»…).
  Famous people's names → ordinary names. Social networks' icons: draw simple glyph shapes in their colours.
- **Nothing is uploaded to Stock.** Do not run publish scripts. Do not commit (the lead commits).
- Everything Jorge reads is in Spanish (`es` names, notes); code/comments in English like the other modules.

## Tools

- Template: `wide(f"yp1-{id}", es, en, "ytkit", D, order=…, tags=["kit:<section>", "youtube", …], thumb_at=…)`
  (vertical: `tall(...)` from `kit`, frame 1080×1920). Sections: aperturas, barras-info, elementos, frases,
  pantallas-finales, redes, tercios, tipografia, titulos-estilo, transiciones, lowerthirds.
- Motion helpers: `templates_tit_h.S` (the slide class; read the file):
  - `s.obj(name, layers, geom(fr,u)->(cx,cy,w,h,rot,op), kind=, path=, radius=, base=)` any shape per frame;
  - `s.rect(name, layers, r(fr,u)->(x0,y0,x1,y1), op=, rot=, path=)`;
  - `s.say(text, ink(x0,y0,x1,y1), family, weight, colour, name, geom=(fr,u)->(dx,dy,scale,rot,op) | shift=fr->(dx,dy) with reveal=fr->rect, op=, rot=, layers=, align=)`;
  - `s.typed(clip, at_frame, stagger, duration, preset="typewriter|fade|rise|drop|pop|...", order="forward|random|backward", unit=)`;
  - `s.outline(name, points, width, colour, at, n, closed)` a stroke that draws itself; `s.fade(clip, fn)`;
  - `s.yt(name, geom->(cx,cy,scale,rot,op), w, h, red, tri, tri_at)` a YouTube play button;
  - `ring(colour,w)`, `solid(colour,a)`, `grad(c0,c1,angle)`, `fill`, `shadow`, `poly`, `regular(n)`, `sectors`, `arc`, `rot_pt`, `lin`.
  - `templates_tit_i`: `bg(s, colour)`, `cam(ink, sc, px, py, extra)` (camera pull-back), `with_op`, `masked_photo(s, sample, "WORD", rect_fn)` (photo inside a word).
  - `templates_tit_j`: `photo(s, sample, rect_fn)` (photo slot clipped to a moving rect), `dots(...)`.
  - Exit = entrance backwards at 2.5× (`S.frame`); `dur_for(entrance, hold)`.
  - Frames: 29.97 fps; `k(fr, at, n)` eases 0→1 from frame `at` over `n` frames.
- Photo samples: `E:\FlipStudio\tienda\plantillas\muestras` (names without extension; `kit.BLOCKED` ones are banned).
- Build & render (renders are serialised by a lock, so parallel runs are fine):
  `cd tools/scene_templates; py build.py --only "mod:templates_yp1" --out E:/FlipStudio/tienda/plantillas/prototipos-yp1 --work E:/FlipStudio/tienda/plantillas/trabajo-yp1 --exe "E:/FlipStudio/pruebas/FlipStudio-0.30.2-stock/Flip Studio/flipstudio.exe" </dev/null`
  (`--only "yp1-a,yp1-b"` for single pieces; each folder gets `preview-wide.mp4`, thumbnails).
- Study: 10 fps sheets with frame numbers, e.g.
  `ffmpeg -nostdin -v error -y -ss START -t DUR -i VIDEO -vf "fps=10,scale=320:-2,drawtext=fontfile=C\\:/Windows/Fonts/arial.ttf:text='%{n}':fontcolor=red:fontsize=18:x=4:y=4,tile=6x8" -frames:v 1 SHEET.png`
  A 320 px tile maps to 1920 px by ×6. Grid pieces (2×2) map by ×12 inside their quarter.
- Comparison video (original on top, Flip below, «N de M» card, padded by clone, never grey): see `cmp2.sh` in the
  lead's scratchpad pattern — write your own copy in **your own scratchpad with a unique name**.

## Traps (learned on tit5–tit7)

- Text that slides out from behind something: pass `shift=` together with `reveal=`; moving x/y keys (geom) drags the mask.
- A mask/reveal on rotated text rotates with it.
- Track creation order is z order (first = bottom). Transition shapes that cover the slide are created last.
- `typed` stagger/duration are seconds. `ffmpeg` in loops needs `-nostdin`. Python writes CRLF unless `newline=""`.
- Scratch files: unique names per agent (several agents share the scratchpad).

## Engine gaps

If a move cannot be done with the current engine (3D flips/cubes, path morphing, per-letter colours, blur…), do the
closest honest version and write the gap in your video's `NOTAS.md` under «## Motor pendiente»: which element, what
the reference does, the source seconds, and what the engine would need (the lead gathers them into
`docs/motor-pendiente.md`; do not edit that file, several agents run at once). Do not edit C++; the lead implements the engine features afterwards.

## Notes per video

`E:\FlipStudio\tienda\plantillas\estudio-<video>\NOTAS.md`: element list with source times, what was made, what was
skipped and why. Keep it updated as you go so the work can be resumed.

## Engine features that already exist (use them; found after the first pass)

Many «Motor pendiente» notes of the first pass are things the engine already does. Use, in `templates_tit_h.S`:
- **3D flips in perspective:** `s.d3(clip, rx=fn, ry=fn, z=fn, persp=1400, occlude=False)` (the engine's 3D layer:
  `layer3d`, `rotationX`, `rotationY`, `positionZ`, `perspective`, `depthOcclude`). Thickness: `layer.bevel` effect or
  a darker copy at `z` behind.
- **Effects on any clip:** `s.fx(clip, "<effect id>", animated={param: fn(fr,u)}, **params)`. Useful ids:
  `builtin.effects.gaussian_blur` (u_blurRadius), `liquid.gooey` (goo, threshold, shine: metaballs / liquid merging),
  `halftone_comic` (dot screens), `spin_blur`, `wave_warp`, `motion_trail`, `layer.bevel`, `ae.linear_wipe`
  (completion, angle, feather), `ae.fractal_noise`, `squash.deform`, `stylize.twirl` (NEW: angle, radius, centerX,
  centerY — needs the next build), `layer.drop_shadow`, `layer.outer_glow`, `layer.stroke`, `rgb_split`…
  (`effects/*/effect.json` lists every id and parameter).
- **Motion blur:** `s.mblur(clip)`.
- **Blend modes:** `clip["blendMode"] = "multiply" | "screen" | "difference" | …` (difference = the colour of an overlap).
- **Text on a path / circle:** `textStyle["pathSvg"]` (SVG on 0..100 of the text box) or `pathCircle` (percent of the
  circle), `pathOffset` keyframable (letters slide along); turn the clip to spin it.
- **Morph between shapes:** `pathShapes` + the `path` key; animatable `cornerRadius`, `wiggleSize`, `trimEnd`.
- **Masks on any clip** (shapes too): `t.mask(track, clip, "rectangle"|"ellipse"|"path"|"text", invert=…, keyframes=…)`
  or `llt_motion.mask_track`; inverted masks make holes.
- **Text:** `runs` (colour per letter), `letterSpacing` keyframes, presets `blur-in`, `converge`,
  `ibs-scatter-gather`, `im-crash-from-big`; per-letter `random` order.
- **Counter:** `counter`, `counterFrom`, `counterSeconds`, `counterCurve: "linear"` (NEW, next build).
- **Short / Video:** slides mark `layoutRole` themselves; check the other shape with `short_check.py`.
