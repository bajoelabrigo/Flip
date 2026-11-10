# TIKTOK folder → Stock (Kit de TikTok), 2026-11-09

Jorge: LOGO, then TIKTOK, then INSTAGRAM, same rules as the YouTube pack; everything ships together with app 0.31.0
(PR #57, draft). Nothing is uploaded until then. He reviews at the end; the lead checks every module in the app window.

Videos in `C:\Users\bajoe\Downloads\EDITAR PARA STOCK\TIKTOK` (all 1920×1080 presentations of **vertical 9:16**
stories/openers, mostly shown inside phone mockups or side by side):

| Video | What it is | Prefix / module | Order | Output (E:\FlipStudio\tienda\plantillas\…) |
|---|---|---|---|---|
| 30653429.mp4 (31 s) | TikTok stories pack: blue/black/red/pink stories with stickers (eyes, smileys, «LIKE!»), «TIK-TOK PROMO», «TRENDY STYLE», «NEW VIDEO», «TIKTOK TRENDS», photo stories | `tk0-*` | 14000– | `prototipos-tk0` |
| 34221988.mp4 (34 s) | «Typography opener»: one word per beat on black/white (BRAND, NEW, MODERN, CREATIVE, FOLLOW, RULES…), photo flashes | `tk1-*` | 14100– | `prototipos-tk1` |
| 35865129.mp4 (28 s) | TikTok intro stories: blue/black/red profile stories, names, «Get new subscribers» | `tk2-*` | 14200– | `prototipos-tk2` |
| 40484842.mp4 (40 s) | fashion stories on pastel gradients: «Fashion Sale 50% OFF», «Keep It Trendy», «Lifestyle», «Giveaway!», «The Next Level Of Fashion», «Fashion Design», «Thanks For Watching!» | `tk3-*` | 14300– | `prototipos-tk3` |
| 4714855.mp4 (175 s) | slideshow/opener pack: stomp openers (one word per beat over photos), typo openers, dynamic openers, 6-in-1 grids | `tk4-*` | 14400– | `prototipos-tk4` |
| 48372050.mp4 (68 s) | «Flow Reels» B/W: photo collage stories with big thin words (ONE, SUNSHINE FILLS SKIES, FIND HIDDEN GEMS, FOLLOW YOUR DREAM…), CTA «JOIN THE JOURNEY» | `tk5-*` | 14500– | `prototipos-tk5` |
| 48513800.mp4 (68 s) | «Flow Reels» teal: FREEDOM, AURA, WIND, STARRY NIGHTS, TIME'S NOW…, CTA «SAVOR LIFE'S GOODNESS» | `tk6-*` | 14600– | `prototipos-tk6` |
| 48513831.mp4 (68 s) | «Flow Reels» colour/flowers: COLORFUL AND CONFIDENCE, EMBRACE, BLOOMS ALL AROUND, SALE SALE SALE, FLOWER PARADISE DELIGHT…, CTA «DISCOVER MORE» | `tk7-*` | 14700– | `prototipos-tk7` |
| 48784008.mp4 (68 s) | «Flow Reels» food/yellow: NEW YORK PIZZA, FOOD LOVERS UNITE, FAST FOOD ADDICTION, FRIED CHICKEN…, CTA «DISCOVER NEW FLAVORS» | `tk8-*` | 14800– | `prototipos-tk8` |
| 57608990.mp4 (37 s) | «Clean opener»: one word per beat on white/black/colour/photo (FRESH, FAST, DARE, BREAK, RULES, PROJECT, MODERN, UNIQUE, SPARK, ENJOY…) | `tk9-*` | 14900– | `prototipos-tk9` |

Category `tiktok` («Kit de TikTok», already in `publish.py`); templates are vertical: `tall(f"tk0-{id}", es, en,
"tiktok", D, order=…, tags=[…], thumb_at=…)` (1080×1920, see `kit.tall`; `templates_yp4.py` is a vertical pack to
learn from). Tags: «tiktok», «historia», «reels» plus what it is.

## Rules

All the rules, tools, traps and engine features of `docs/plan-youtube-pack.md` apply, and the logo rules of
`docs/plan-logo.md` (brand marks → the user's `logo-flip` slot; brand words, «envato», «BRAXXU», «TikTok» used as a
brand name in text → neutral words; the TikTok note glyph may stay only as a small social icon). On top:

- **What to copy is the story on the phone screen**, full 9:16, not the mockup: skip the phone frames, the floating
  phones, the «PREVIEW OF ALL SCENES» grids, «CREATE YOUR OWN STORYLINES / CALL TO ACTION BUTTONS INCLUDED» cards, the
  pack titles and the presenter footage («Perfect for social media», «Use spring bright colors», «Easy to edit»).
  Where the phone is tilted, measure the screen content and lay it out flat.
- **Photos are slots** (`t.photo(..., sample, ..., label="Foto N")`) filled with our samples from `muestras`
  (`fetch_samples.py` if you need new themes; avoid brands). Videos in the reference → photo/video slots too.
- One template per distinct story/opener. An opener that is one long sequence of words is one template (cut it into
  2–3 templates only if the reference clearly shows separate openers).
- Short is native here; the other-shape check is the horizontal one: `short_check.py` renders
  `preview-horizontal.mp4` for tall templates — look at it (backgrounds `cover`/`backdrop`, the story's art fitted).
- Exe: `E:/FlipStudio/pruebas/FlipStudio-motor-0109c/Flip Studio/flipstudio.exe`. Notes:
  `E:\FlipStudio\tienda\plantillas\estudio-<video>\NOTAS.md`. Comparison: `comparacion-tkN.mp4` (reference crop of the
  screen on the left, ours on the right, «N de M» card), in the output folder.
