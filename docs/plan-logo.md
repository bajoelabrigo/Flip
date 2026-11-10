# LOGO folder → Stock (Kit de YouTube), 2026-11-09

Jorge: «hazlo en ese orden» (LOGO, then TIKTOK, then INSTAGRAM), same rules as the YouTube pack; when everything is
done it ships together with app 0.31.0 (PR #57, draft). Nothing is uploaded until then.

Videos in `C:\Users\bajoe\Downloads\EDITAR PARA STOCK\LOGO`:

| Video | What it shows | Prefix / module | Order | Output (E:\FlipStudio\tienda\plantillas\…) |
|---|---|---|---|---|
| 19724440.mp4 (960×540, 25 fps, 25 s) | four flat logo reveals on colour (blue, white, coral with a word, yellow), ten social icons, «FOLLOW ME / USERNAME» over a photo | `lg0-*`, `templates_lg0.py` | 13600– | `prototipos-lg0` |
| 34063055.mp4 (960×540, 10 s) | one logo built by light streaks and flares on a bright haze, «WWW.YOURWEBSITE.COM» under it | `lg1-*`, `templates_lg1.py` | 13700– | `prototipos-lg1` |
| 47586149.mp4 (1920×1080, 45 s) | «simple and flat corporate logo pack»: spin, dots that merge, word logos, glitch, «FOLLOW ME ON / SUBSCRIBE ME» social logos, line reveals, in green and blue | `lg2-*`, `templates_lg2.py` | 13800– | `prototipos-lg2` |
| 48635588.mp4 (1920×1080, 25 s) | five logo reveals shown «ORIGINAL / CUSTOM»: ring of dashes, pie that fills, striped sphere, striped square, coloured waves | `lg3-*`, `templates_lg3.py` | 13900– | `prototipos-lg3` |

Sections (first tag `kit:<section>`): logo reveals → `aperturas`; follow / subscribe / social icons → `redes`.

## Rules

All the rules, tools, traps and engine features of `docs/plan-youtube-pack.md` apply. On top of them:

- **The logo is always the user's**: wherever the reference shows its brand mark (Envato leaf, Twitter bird used as a
  brand, any «LOGO»), put the `logo-flip` slot (`t.photo(t.track("video", "Logo"), "logo-flip", start, D, box, motion,
  label="Tu logo", brandRole="logo")`, see `templates_llt_d.py`). The reveal (shapes, rings, pieces, light) is ours and
  copied; the mark inside it is the slot. Where the logo is cut into pieces or drawn by lines in the reference, reveal
  the slot with masks/mattes in the same rhythm (a track matte on the slot is the cleanest).
- Brand words («envato», «envato market», «twitter») → «YOUR LOGO» / «YOUR BRAND»; taglines stay generic
  («#yourtagline», «www.yourwebsite.com», «@username»). Social icons: our own glyph shapes in their colours.
- Skip the After Effects interface shots and the pack covers («SIMPLE AND FLAT CORPORATE LOGO PACK», «INCLUDING 10
  SOCIAL MEDIA ICONS…»); when a reveal is shown twice in two colours, make one template per colour only if the motion
  differs, otherwise one template (colours are editable).
- Engine now has 3D parenting (`stick_to` in `templates_yp2.py`: a child keeps riding a 3D face) and the `cover`
  layout role (a whole-background template grows evenly in a Short). Exe for renders:
  `E:/FlipStudio/pruebas/FlipStudio-motor-0109c/Flip Studio/flipstudio.exe`.
- Notes in `E:\FlipStudio\tienda\plantillas\estudio-<video>\NOTAS.md`; comparison video `comparacion-lgN.mp4` in the
  output folder; Short check with `short_check.py --only "mod:templates_lgN" --out E:/FlipStudio/tienda/plantillas/trabajo-short/out --work E:/FlipStudio/tienda/plantillas/trabajo-short`.
