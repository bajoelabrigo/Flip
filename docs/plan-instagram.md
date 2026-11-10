# INSTAGRAM folder → Stock (Kit de Instagram), 2026-11-09

Jorge: LOGO, then TIKTOK, then INSTAGRAM, same rules; everything ships together with app 0.31.0 (PR #57, draft).
Nothing is uploaded until then. The lead checks samples of every module in the app window.

Videos in `C:\Users\bajoe\Downloads\EDITAR PARA STOCK\INSTAGRAM` (`instagram.mp4` is the same file as `60629101.mp4`:
skip it). Most are presentations of **vertical 9:16** stories (or 4:5 / 1:1 posts) inside mockups or side by side.

| Video | What it is | Prefix / module | Order | Output (E:\…\plantillas\…) |
|---|---|---|---|---|
| 12241495.mp4 (17 s) | urban «dynamic intro» story: URBAN, STREETS, CLEAN, RHYTHM, THANKS, logo | `ig0-*` | 15000– | `prototipos-ig0` |
| 21692676.mp4 (50 s) | big stories pack: DO YOUR BEST, NEON CITY, WE MUST BELIEVE, Conquer from within, Love is friendship, STYLISH DESIGN, Alison Stanley, happy thoughts, 30% Spring Sale, ELEGANT DESIGN, 40% Sale, Nature, SEEK THE SEEKER, WORK HARD DREAM BIG, LIVE WHAT YOU LOVE, Anna Fletcher… | `ig1-*` | 15100– | `prototipos-ig1` |
| 22025898.mp4 (40 s) | colourful stories pack: Fashion, Cooking, Your life, Modern interior design, %, DARK, R, GREAT SUMMER, HAPPY, Stories… | `ig2-*` | 15200– | `prototipos-ig2` |
| 23012546.mp4 (70 s) | «Instagram pack»: 20 stories (Stories, Full, art 01, PRO, ADT, LEV, TECH, FRIEND, Promo, PORTFOLIO, JOHN… → ordinary name, Food, MODELS, MUSIC, CITY LIFE, CS…), 5 profile designs, 1 dynamic opener (INSTAGRAM, Kinetic…) | `ig3-*` | 15300– | `prototipos-ig3` |
| 2656838.mp4 (210 s) | «150+ Instagram» stories/posts in 3 formats, plus updates: 12 backgrounds and titles, neon titles, Christmas stories, swipe-up elements, 6 new stories. **Skip the Halloween stories** (Stock is for the whole world) | `ig4-*` (0–70 s), `ig5-*` (70–140 s), `ig6-*` (140–210 s) | 15400–, 15600–, 15800– | `prototipos-ig4`, `-ig5`, `-ig6` |
| 28897023.mp4 (68 s) | «Typo Instagram stories» 10 colourful typography stories | `ig7-*` | 16000– | `prototipos-ig7` |
| 38567689.mp4 (24 s) | «5 Urban stories» (city vibes, visit page, mega sale, friends, best sellers…) | `ig8-*` | 16100– | `prototipos-ig8` |
| 57447063.mp4 (30 s) | 5 typographic stories in grey/black/red (TYPO, AGR, GR, INSTAGRAM) | `ig9-*` | 16200– | `prototipos-ig9` |
| 59320997.mp4 (27 s) | 5 «Instagram models» stories with arch-shaped photos | `ig10-*` | 16300– | `prototipos-ig10` |
| 59444568.mp4 (73 s) | Instagram call-to-action **elements over footage** (16:9 overlays): profile card, «Give double tap!», «Click our bio link», «Comment below», «Tap to see story», tag, «Add your story», «Watch our latest reels», «Find your inspiration», «Share post to story», likes, follow buttons… | `ig11-*` | 16400– | `prototipos-ig11` |
| 60629101.mp4 (27 s) | 5 orange/black stories («Insta», «photo», «awesome»…) | `ig12-*` | 16500– | `prototipos-ig12` |
| 63756849.mp4 (38 s) + `instagram 2.mp4` (22 s) | 10 yellow «Typo Instagram story» stories + the feed slideshow / logo intro of `instagram 2` | `ig13-*` | 16600– | `prototipos-ig13` |
| instagram sliders.mp4 (287 s) | «IGTV pack»: 8 slideshows (dynamic, fashion, rhythmic, clean, epic, stomp, minimal, energy) in story size; skip the presenter, footage and info cards | `ig14-*` | 16700– | `prototipos-ig14` |

The 2656838 pack is split in three agents by source time: `ig4` 0–70 s, `ig5` 70–140 s, `ig6` 140–210 s.

Category `instagram` («Kit de Instagram», in `publish.py`); vertical templates with `tall(...)` (1080×1920; a 4:5 or
1:1 post only if the reference shows that format as its own design, with `size=(1080, 1350)` / `(1080, 1080)`);
ig11 elements are wide overlays (`wide`, no background of their own, like the yp0 widgets). Tags: «instagram»,
«historia», «reels» plus what it is.

## Rules

All the rules of `docs/plan-youtube-pack.md`, the logo rules of `docs/plan-logo.md` and the «what to copy» rules of
`docs/plan-tiktok.md` apply: copy the story/post flat (no mockups, no info cards, no pack covers), photos and videos →
photo slots with our samples (check for brands; `kit.BLOCKED`), brand marks → the user's `logo-flip` slot, brand words
(envato, Instagram used as the brand name in big type, «IGTV», author names) → neutral words («YOUR BRAND», «STORIES»…);
the Instagram camera glyph may stay only as a small social icon. Famous names → ordinary names. One template per
distinct story; a long pack is many templates: be faithful rather than fast. Halloween: skip.
Exe: `E:/FlipStudio/pruebas/FlipStudio-motor-0109c/Flip Studio/flipstudio.exe` (or the newest `FlipStudio-motor-*`).
