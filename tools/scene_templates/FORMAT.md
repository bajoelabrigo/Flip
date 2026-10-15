# Project JSON format for scene templates (generator reference)

Read from the code on 2026-10-15 (`src/core/Project.cpp`, `Effect.cpp`, `TextStyle.cpp`, `TextShading.cpp`,
`ShapeStyle.cpp`, `ClipAnimation.cpp`, `Mask.h`, `Track.cpp`, `engine/FrameCompositor.cpp`, `models/SceneTemplates.cpp`,
`mcp/*`). Key names are quoted exactly as the reader spells them. Every key not listed as required may be omitted;
the default is what the reader uses then.

## 1. Root

```json
{"version": 14, "projectName": "Photo dump", "width": 1080, "height": 1920, "fps": 30, "sampleRate": 48000,
 "background": {"kind": "color", "color": "#ff000000"},
 "assets": [ ... ], "tracks": [ ... ]}
```

- **`version` (write 14 = `Project::kCurrentVersion`).** Missing means **1**, which switches to the v1 readers
  (`clipFromJsonV1`: `kind`/`start`/`duration` in seconds) and ignores almost everything below. >14 is refused.
  Migrations that run when `version` is lower: `<4` lifts adjustment clips off video tracks and hoists clip effects
  onto lanes; `<5` moves `clip.mask` of media clips onto mask lanes; `<13` rewrites model3d poses. With 14 none of
  them run. Always run (harmless): `ensureTrackIds`, `normalizeTransformLayers`, `normalizeCameraLayers`.
- **`tracks` is required and must be an array** (otherwise "isn't a Flip Studio project"). Empty array = one empty
  video track.
- `width`/`height` int (default 1920x1080), `fps` **int** (default 30), `sampleRate` int (48000).
- `background`: `kind` = `"color"|"blur"|"transparent"`, `color` (`#AARRGGBB` or `#RRGGBB`, default black),
  `blurStrength` (20).
- `assets`: **array**, its order is the bin order (there is no `assetOrder` key in v2+). Optional:
  `binFolders` `[{id,name,parentId}]`, `sequences` `[{id,tracks:[...]}]` (only for composites; templates must not
  contain composites, they are skipped on insert), `bookmarks`, `workAreaInUs`/`workAreaOutUs`, `id`, `author`,
  `description`, `createdAt`, `modifiedAt`.

### Asset

`{"id": "a-photo1", "kind": "image", "name": "photo1.jpg", "path": "media/photo1.jpg", "width": 1080, "height": 1350}`

- `kind`: `"video"|"audio"|"image"|"vector"|"model3d"|"pdf"|"composite"`.
- Other read keys: `durationUs`, `duration` (label), `fps` (double), `hasAudio`, `sampleRate`, `channels`,
  `codecName`, `rotationDegrees`, `trimInUs`, `trimOutUs` (-1), `thumbnailPath`, `filmstripPath`, `folderId`,
  `sourceFrame`, `generator`. For video give `durationUs`, `width`, `height`, `fps`, `hasAudio`; audio `durationUs`,
  `sampleRate`, `channels`.
- **The renderer reads `clip.path`, not the asset.** In a package (`project.json` next to `template.json`)
  asset paths may be relative to the package folder: `insertSceneTemplate` makes them absolute and copies
  `path`/`thumbnailPath`/`filmstripPath` onto every clip whose `assetId` matches. When loading a JSON directly
  through MCP nothing is resolved, so **test renders need absolute `path` on clips**.

## 2. Tracks

```json
{"id": "t-text", "type": "text", "name": "Titles", "clips": [...], "transitions": [...]}
```

- **`tracks[0]` is the top of the stack** (drawn last); higher index = further down.
- `type` (`trackTypeFromString`, default `"video"`): `"video"|"audio"|"text"|"subtitle"|"shape"|"adjustment"`.
- `Track::allowsClipType`:
  - `video`: `video`, `image`, `composite`
  - `shape`: `shape`, `image`, `video`, `vector`, `model3d`, `pdf`, `composite`
  - `text`: `text` only; `subtitle`: `subtitle` only; `audio`: `audio` only; `adjustment`: `adjustment` only
- Other keys: `muted`, `hidden`, `locked`, `solo`, `volume` (1.0), `pan` (0), plus view-only ones.
- Adjustment tracks: `adjustmentScope` = `"allBelow"` (default) | `"parentTrack"` (lane; needs `parentTrackId`) |
  `"range"` (transform layer, `spanEndTrackId`) | `"camera"`.
- Keep a track's clips sorted by `timelineStartUs` and non-overlapping (overlap only where a transition joins two).

### Adjustment layer over everything below

```json
{"id": "t-fx", "type": "adjustment", "adjustmentScope": "allBelow", "clips": [
  {"id": "c-fx", "type": "adjustment", "adjustmentKind": "videoEffects",
   "timelineStartUs": 0, "timelineDurationUs": 12000000, "srcInUs": 0, "srcOutUs": 12000000,
   "effects": [{"catalogId": "stylize.film_grain", "parameters": {"amount": 0.3}}]}]}
```

It snapshots the composite of every track below it (index greater than its own) for the clip's time span.
`adjustmentKind`: `"videoEffects"` (default) | `"audioEffects"` | `"mask"` | `"transform"` | `"camera"`. Put it
above the tracks it should affect (smaller index).

## 3. Clips

Common keys (all times in **microseconds**, as JSON numbers):

| key | meaning |
|---|---|
| `id` | any unique string; minted if missing (give one: transitions and lanes refer to it) |
| `type` | `"video"|"audio"|"image"|"text"|"subtitle"|"shape"|"adjustment"|"vector"|"model3d"|"pdf"|"composite"` (default `video`) |
| `assetId`, `path` | media clips |
| `timelineStartUs`, `timelineDurationUs` | position on the timeline |
| `srcInUs`, `srcOutUs` | source range. Video: real source µs, `(srcOut-srcIn)/speed = duration`. Image/text/shape/adjustment: `0` and `= timelineDurationUs` |
| `name` | label (text falls back to it if `textContent` is empty) |
| `opacity`, `x`, `y`, `width`, `height`, `rotation` | keyframe objects (below) |
| `blendMode` | `normal|multiply|screen|overlay|add|darken|lighten|soft-light` |
| `speed` (1.0), `reverse`, `flipH`, `flipV`, `volume` (keyframe object **or** plain number), `pan` | |
| `fadeInUs`, `fadeOutUs`, `fadeCurve` (`linear|smooth|equalPower|custom|bezier`, default smooth) | edge fades on opacity/volume |
| `animIn`, `animOut` | section 7 |
| `effects` | section 5 |
| `sourceFrame` | crop `[x,y,w,h]` normalized, default `[0,0,1,1]` |
| `placeholderId`, `placeholderLabel`, `placeholderEmpty` | template slot (media or text) |
| `disabled`, `masksLimitEffects` | written only when true |

**Layout.** `x`,`y` = top-left of the clip's box, `width`,`height` = box size, all in **project pixels**
(origin top-left of the canvas). An empty track at render time means x=0, y=0, w=project width, h=project
height. If the clip has **neither `x` nor `width` as an object**, the reader takes the legacy path
(`posX/posY/scale`) and writes explicit keys for the full canvas, so omitting layout = full canvas. Media is
**stretched** to the box (no aspect fit): to avoid distortion either match the box to the media aspect or crop
with `sourceFrame` (that is what slot filling does, `coverSourceFrame`). `rotation` is degrees about the box
centre (check the sign with one capture). `opacity` is 0..1 (clamped). 3D extras: `rotationX`, `rotationY`, `z`,
`perspective`, `layer3d`.

### Keyframe object (every animatable scalar)

```json
{"keyframes": [{"timeUs": 0, "value": 1.06}, {"timeUs": 500000, "value": 1.0, "inDx": -166666, "inDy": 0}]}
```

- `timeUs` is **relative to the clip's start** (effect, text, shape and mask keys too; mask keys are relative to
  the carrying adjustment's start).
- Per key: `value` (default 1.0), `inDx`, `inDy`, `outDx`, `outDy` (Bezier handles: dx in µs relative to the key,
  dy in value units; `inDx` is negative, `outDx` positive; 0/0 = straight line), `corner`, `hold` (step to next).
  Missing keys = linear.
- Ease shortcut: track-level `"interpolation": "ease"` (or `"hold"`) is still read and applied to every key
  (flat tangents at a third of each gap = smoothstep). Per key, ease = `outDx = (next-t)/3`, `inDx = -(t-prev)/3`,
  dy 0.
- Track-level `"enabled": false` freezes it at the first key.
- One key = constant.

### Minimal clips

- **image**: `{"id","type":"image","assetId","path","timelineStartUs","timelineDurationUs","srcInUs":0,"srcOutUs":<dur>,"x","y","width","height"}`
  on a `video` or `shape` track.
- **video**: as image plus real `srcInUs`/`srcOutUs`; set `"suppressEmbeddedAudio": true` when music plays (the
  inserter does it for you if the template has an audio track).
- **audio**: `{"type":"audio","assetId","path","timelineStartUs","timelineDurationUs","srcInUs","srcOutUs","volume":1.0,"fadeOutUs":500000}`
  on an `audio` track. `audioFadeInUs`/`audioFadeOutUs` exist too (de-click only).
- **shape**: `{"type":"shape","shapeStyle":{...},` layout `}` on a `shape` track (section 4).
- **text**: `{"type":"text","textContent":"2026","textStyle":{...},` layout `}` on a `text` track.

### Text layout and textStyle

The box is the layout rect: text **wraps at the box width** (`wordWrap`, default true) and is placed in it by
`align` (`left|center|right`) and `valign` (`top|center|bottom`; anything else = middle). `pixelSize` is in
project pixels (default 64), multiplied only by the render scale; it is **not** fitted to the box, so make the
box big enough (wrapping happens, shrinking does not).

textStyle keys read: `fontFamily` ("Inter"), `pixelSize`, `fontWeight` (100..900, default 700), `italic`,
`layers`, `pathBend` (-100..100), `align`, `valign`, `wordWrap`, `lineHeight` (1.2), `letterSpacing` (px),
`textCase` (`none|upper|lower|title`), `boxEnabled`, `boxColor`, `boxPadding` (8), `boxRadius`, `boxStyle`
(`block|line`), `boxShape` (`rect` or a bubble), `boxPaddingX`, `boxPaddingY`, `boxOffsetX`, `boxOffsetY`,
`boxBorderWidth`, `boxBorderColor`, `wordHighlight {enabled,color,padding,radius}`, `underlineEnabled`,
`underlineColor`, `underlineWidth`, `underlineOffset`, `accent` (below), `animation` (below), `keyframes`
(map: `pixelSize`, `letterSpacing`, `lineHeight`, `boxPadding`, `pathBend`, `layer.<id>.<field>` with field
`opacity|offsetX|offsetY|blur|width|spread|color.r|color.g|color.b|color.a`...).

**`layers` must be present** (without it the v6 flat reader runs). `layers[0]` is drawn **first** (back), so
order shadow, glow, stroke, fill. Layer: `id` (lowercase, unique), `kind` `fill|stroke|shadow|glow|extrude`,
`enabled`, `paint {kind: "solid"|"gradient"|"texture"|"effect", color, gradient{kind:"linear"|"radial"|"sweep",
stops:[{pos,color}], angle}}`, `opacity`, `blend`, `offsetX`, `offsetY`, `blur`, `width` (2), `spread`,
`strokeAlign` (`outside|center|inside`), `dash` (`solid|dash|dot|dashdot`), `knockout`, `trimStart`, `trimEnd`.
Colors everywhere are QColor strings: `#AARRGGBB` (8 digits, alpha first) or `#RRGGBB`.

`accent`: `{rule: none|firstWord|lastWord|everyOther|everyNth|longestWord|randomStable|karaoke|keywords, n, phase,
colorEnabled, color, sizeScale, outlineEnabled, outlineWidth, outlineColor, highlight{...}}`. Words wrapped in
`*asterisks*` in `textContent` are accented whatever the rule.

**Text animation** (`textStyle.animation`): `{"in": slot, "out": slot, "loop": slot}`; slot =
`{"preset": "<id>", "params": {"<name>": {"type": "scalar"|"color"|"text", "value": ...}}, "delayUs", "durationUs",
"periodUs"}`. Every in/out preset also takes the common params `duration` (s, 0.4), `stagger` (s, 0.06),
`unit` (text: `block|character|word|line`), `order` (text: `forward|backward|centerOut|random`), `ease`
(text: `linear|easeIn|easeOut|easeInOut|back|bounce|smooth`). Missing params use the preset defaults.
Presets (`presets/text-animations/`, slot kinds, own params = default):

- in+out: `blur-in` blur=24; `blur-in-words` blur=20; `bounce` distance=0.35; `converge` spread=1, blur=8;
  `fade`; `fade-up-char` rise=0.35; `flip`; `glitch-in` offset=0.3, skew=25; `pop` from=60 (%);
  `rain` height=3, blur=6; `rise` distance=0.35; `rise-by-word` rise=0.6, blur=8; `skew-slide` distance=0.3,
  skew=-20; `slide-up|slide-down|slide-left|slide-right` distance=0.35; `spin-in` angle=-90, from=50;
  `type-on-blur` blur=12, scale=115; `typewriter` caret=false, lead=0.2, blink=2, hold=0.5, collapse=false;
  `wipe` angle=-90, softness=0.3; `zoom-in` from=50; `zoom-out` from=160, blur=12
- in only: `color-wave` arrive=#ffc52896, decay=0.35, rise=0.3; `drop` height=1.2; `flicker-in`;
  `snap-together` spread=0.06, blur=6; `squash` stretch=260; `stamp` from=250, tilt=-8
- out only: `fade-scale` to=130, blur=10; `fade-shift` rise=0.5, blur=0; `fall` height=4, spin=25;
  `remove-by-word` drop=0.4, blur=6; `shrink`
- loop: `breathe` amount=0.3, speed=0.4; `colour-pulse` colorA, colorB, speed=0.5; `flicker` intensity=0.5,
  speed=8; `float` amount=0.15, speed=0.5; `jitter` amount=1.5, angle=2, speed=12; `karaoke-bounce` lift=0.1,
  scale=110; `karaoke-pop` scale=112; `pulse` amount=5, speed=1; `slow-zoom` to=108; `sway` angle=2, lift=0.02,
  speed=0.6; `swing` angle=3, speed=0.6; `tracking-drift` from=2, to=21, zoom=100; `wave` amount=0.12,
  frequency=1.1, phase=34.4

Fonts: `fontFamily` must be a family the app can see: system-installed, a user font in
`%APPDATA%\Flip Studio\Flip Studio\fonts\user`, or a font package (`family.json` + faces) under a `fonts` data
root / `DRIFT_FONTS_DIR`. The repo bundles none.

## 4. shapeStyle

```json
{"kind": "rounded-rectangle", "cornerRadius": 24,
 "layers": [{"id": "fill", "kind": "fill", "paint": {"kind": "solid", "color": "#ffffd84d"}},
            {"id": "stroke", "kind": "stroke", "enabled": false, "width": 0, "strokeAlign": "inside",
             "paint": {"kind": "solid", "color": "#ffffffff"}}]}
```

- `kind`: `rectangle, rounded-rectangle, square, ellipse, triangle, right-triangle, diamond, pentagon, hexagon,
  octagon, parallelogram, trapezoid, arrow, double-arrow, block-arrow, curved-arrow, chevron, speech-bubble,
  speech-bubble-rect, thought-bubble, callout, star, lightning-bolt, cloud, heart, cross, burst, banner`; `circle`
  is accepted (= ellipse). No line kind: use a thin rectangle.
- Geometry: `cornerRadius` (project px, clamped to half the short side), `points` (5, star/burst), `innerRatio`
  (0.5), `headSize` (0.4), `thickness` (0.4), `tailX` (0.25), `tailSize` (0.2). The shape fills the clip box.
- `layers`: same layer model as text, `layers[0]` back-most. Omitting `layers` runs the legacy flat reader
  (`fill`, `fillKind`, `stroke`, `strokeWidth`), not what you want. Always give both layers explicitly:
  the default stack is a blue fill plus a 4 px white stroke.
- `keyframes`: `cornerRadius`, `layer.<id>.<field>` (as text).

## 5. Effects

`[{"catalogId": "<meta id>", "parameters": {...}, "paramKeyframes": {"<param>": <keyframe object>}, "enabled": true, "name": ""}]`

- **`catalogId` is the `id` field inside `effects/<folder>/effect.json`, not the folder name** (an unknown id
  renders nothing). Parameters you omit take the catalog default. An animated parameter (`paramKeyframes`) wins
  over `parameters`; key times are clip-relative. Colors are `"#rrggbb"` strings; bools true/false.
- Effects may sit on an adjustment clip (section 2) or directly on a media/text clip (rendered as is; the editor
  moves them onto a linked lane on the next edit, same timing).

| catalogId | parameters (default [min..max]) |
|---|---|
| `builtin.effects.gaussian_blur` | `u_blurRadius` 10 [0..100] |
| `stylize.film_grain` | `amount` 0.35 [0..1], `grainSize` 1.5 [1..4], `colourGrain` bool false |
| `stylize.vignette` | `amount` 0.55 [0..1.5], `size` 0 [0..1], `softness` 1 [0..1] |
| `light_leak` | `intensity` 0.55, `hue` 0.06, `angle` 0, `speed` 1 [0..4], `softness` 0.3 [0.02..1], `flicker` 0.2 (others [0..1]) |
| `rgb_split` | `amount` 8 [0..50], `angle` 0 [0..360], `animated` bool false, `speed` 1 [0..10] |
| `zoom_pulse` | `punch` **0** [0..1], `centerX` 0.5, `centerY` 0.5, `blur` 0.45 |
| `beat_shake` | `amount` **0** [0..1], `rotation` 0.35, `seed` 0.5 |
| `bloom_glow` | `threshold` 0.75 [0..1], `intensity` 0.6 [0..2], `blurRadius` 8 [1..30] |
| `stylize.sepia` | none |
| `cinematic_grade` | `strength` 0.65, `teal` 0.7, `orange` 0.55, `contrast` 0.45 [all 0..1] |
| `digital_glitch` | `intensity` 0.5, `frequency` 0.35, `rgbAmount` 8 [0..40], `blockAmount` 0.4, `flashAmount` 0.15, `seed` 1 [0..999999] |
| `strobe_flash` | `flash` **0** [0..1], `tint` 0.15 |
| `bling_sparkle` | `intensity` 0.6, `threshold` 0.7, `density` 0.5, `size` 0.5, `twinkleSpeed` 1 [0..4], `points` 4 [4..8], `colorize` 0.3 |
| `duotone` | `strength` 0.8, `shadowColor` "#0a1628", `highlightColor` "#ff6b35", `contrast` 0.5 |
| `stylize.vhs` | `noise` 28 [0..80], `chroma` 3 [0..12], `saturation` 0.85 [0.2..1.2] |
| `super8_film` | `intensity` 0.7, `grain` 0.55, `scratches` 0.35, `weave` 0.25, `flicker` 0.2 [all 0..1] |
| `color.basic` | `exposure, brightness, contrast, highlights, shadows, whites, blacks, saturation, vibrance, temperature, tint` 0 [-1..1]; `fade` 0 [0..1] |

`zoom_pulse.punch`, `beat_shake.amount` and `strobe_flash.flash` default to 0 = invisible: they are meant to be
driven by `paramKeyframes`, e.g. a beat pulse
`{"punch": {"keyframes": [{"timeUs": 0, "value": 0.8}, {"timeUs": 250000, "value": 0}]}}`.

## 6. Transitions (on the track, next to `clips`)

`{"id": "x1", "kind": "crossfade", "fromClipId": "c1", "toClipId": "c2", "durationUs": 500000, "parameters": {}, "easingCurve": "smooth"}`

- `kind` = package id (folder in `transitions/`): `crossfade, dip, dip_white, blur_dissolve, luma_fade,
  slide_up|down|left|right, push_left, wipe_up|down|left|right, zoom_in, spin, fold, glass_wipe, organic_wipe,
  torn_paper, warp_slide, radial_zoom_blur, cross_zoom_swirl, rgb_displacement, pixelate_matrix, ...` (39).
  `parameters` override the package defaults. `easingCurve` optional (`linear` default).
- Both clips on **the same track**; `toClip` starts at or after `fromClip`'s start and no more than 1 ms after
  its end. If they physically overlap, the overlap is the window (`durationUs` ignored); if they abut, the window
  is `durationUs` centred on the cut, clamped to the two clips.

## 7. animIn / animOut (whole-clip intro/outro)

`{"kind": "pop", "durationUs": 400000, "curve": "smooth"}`

- `kind`: `none|fade|slideUp|slideDown|slideLeft|slideRight|zoomIn|zoomOut|pop|spinCW|spinCCW|bounce`.
- `curve`: `linear|smooth|equalPower|custom|bezier` (custom/bezier need `shape`); legacy `ease`
  (`linear|easeOut|easeInOut|back`) is used only when `curve` is missing. `duration` in seconds is accepted
  if `durationUs` is missing. Slides travel 0.35 of the box size. `fade` drives opacity through the fade path.

## 8. Masks

`clip.mask` is honoured **only on a Mask-kind adjustment clip**; on a media clip it is ignored (v14 runs no
migration). A photo is masked by a lane: an adjustment track with `adjustmentScope: "parentTrack"` and
`parentTrackId` = the photo's track id, placed right after it in `tracks`, holding an adjustment clip linked to
the photo:

```json
{"id": "t-p1", "type": "video", "clips": [{"id": "c-p1", "type": "image", "path": "...", "x": 290, "y": 560,
  "width": 500, "height": 500, "timelineStartUs": 0, "timelineDurationUs": 3000000, "srcInUs": 0, "srcOutUs": 3000000}]},
{"id": "t-p1-mask", "type": "adjustment", "adjustmentScope": "parentTrack", "parentTrackId": "t-p1", "clips": [
  {"id": "m-p1", "type": "adjustment", "adjustmentKind": "mask", "linkedClipId": "c-p1",
   "timelineStartUs": 0, "timelineDurationUs": 3000000, "srcInUs": 0, "srcOutUs": 3000000,
   "mask": {"shape": "ellipse", "x": 0.5, "y": 0.5, "w": 1.0, "h": 1.0, "feather": 0}}]}
```

- Mask geometry is **normalized to the host clip's box** (not the canvas): `x`,`y` = centre, `w`,`h` = size;
  so a circle needs a square box. Other keys: `rotation`, `feather` (px), `invert`, `expand` (fraction of the
  shorter side), `opacity`, `op` (`add|subtract|intersect`), `enabled`, `points` `[[x,y],...]` + `smooth` for
  freeform, `text` for text, `keyframes` (`x,y,w,h,rotation,feather,expand,opacity`, relative to the
  adjustment's start), `pathKeys`.
- Shapes: `rectangle, ellipse, star, heart, bars, freeform, text, gradient, media`. **There is no rounded
  rectangle**: use `freeform` with points traced around the rounded corners (about 8 per corner), or put the photo
  above a `rounded-rectangle` shape and accept square corners on the photo.
- A linked adjustment without `"independentRange": true` is re-synced to its host's span by the editor.
- Unlinked mask (`linkedClipId` empty) masks whatever that track shows during its span.

## 9. Audio

Asset `{"id": "a-music", "kind": "audio", "path": "media/music.m4a", "durationUs": 15000000, "sampleRate": 48000,
"channels": 2, "hasAudio": true}`, a track `{"type": "audio", "clips": [...]}` with an `audio` clip whose
`srcInUs`/`srcOutUs` are source µs (`srcOut - srcIn = timelineDurationUs` at speed 1). `volume` may be a plain
number or a keyframe object; `fadeInUs`/`fadeOutUs` (`fadeCurve`) shape the volume.

## 10. Template package notes (`engine/SceneTemplateCatalog.h`)

Folder = `template.json` (`{id, displayName, names{locale:name}, category, order, width, height, durationSec,
slots, texts, premium, tags[]}`) + `project.json` (this format) + `thumbnail.png` (+ `preview.mp4`) + `media/`.
On insert every id is re-minted (transitions, `linkedClipId`, `parentTrackId`, `spanEndTrackId` follow), times
are shifted to the playhead, the layout is scaled if the open project has another size, and every **non-text clip
with `placeholderId`** becomes an `image` clip showing a generated "Your photo here" card (its box is kept, so
give slots their final box; its asset may be any image, it is replaced). Text clips with `placeholderId` are the
editable texts in the Fill template panel.

## 11. MCP (headless)

`flipstudio.exe --headless --mcp-stdio` speaks JSON-RPC `tools/call`; the payload is JSON text in
`result.content[0].text`. With `tools/e2e/mcp_e2e.py --exe <exe> --calls <file.jsonl> --out <dir>`, each line is
`{"tool": ..., "args": {...}, "sleep": s, "wait": s, "save": "name.json"}`. Toolbox ops can be called directly by
name (they go through `applyOne`).

- (a) Load: `{"tool": "load_project", "args": {"path": "C:\\abs\\project.json"}}`. Accepts `.drift` or a JSON
  document; JSON is an import (inspect.path stays empty). Blocks until loaded; errors `load_failed` with the
  message. `new_project {width, height, fps}` starts blank.
- (b) Still: `{"tool": "capture", "args": {"at": 2.5, "full": true}}` (`at` in timeline **seconds**). `full:true`
  writes a full-resolution PNG to a path the app chooses (`newFreezeFramePath`, under AppData) and returns it as
  `path`; copy it from there. Without `full` it returns an inline JPEG (long edge 1280). Contact sheet:
  `frames {at:[...]}` or `{start,end,n,sample:"uniform"}`.
- (c) Export: `{"tool": "export_video", "args": {"path": "C:\\abs\\out.mp4", "in": 0, "out": 3, "video": "h264",
  "audio": "aac", "rate": "crf", "crf": 18, "fps": 30, "height": 0}}`. Waits by default (`wait` true, optional
  `timeout` s); use the path echoed in the reply. `list_export_options` lists codecs; `export_status`,
  `cancel_export`.
- (d) Inspect: `{"tool": "inspect", "args": {"clips": true, "detail": true}}` (`clip: <id>` for one clip,
  `track: n` for one track). Read `notice` when something silently did nothing.

Traps (CLAUDE.md): the executable must live outside the repo (`Downloads\FlipStudio\pruebas\...`) or it cannot
write files; run unsandboxed; a test run writes `recentProjects`/preferences to `HKCU\Software\Flip Studio`
(export it before, restore after) and may leave `recovery\autosave.json`.
