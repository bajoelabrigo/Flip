# YOUTUBE PACK, second group → Stock (Kit de YouTube), 2026-11-15

Jorge sent five more promo videos: «trabajame estos videos para el stock, tu ya sabes como hacerlo». Same rules as
`docs/plan-youtube-pack.md` (copy, don't invent; transitions too; YouTube play button only where the reference shows
it, the `logo-flip` slot for other logos; nothing uploaded until the whole group is done and Jorge has seen it).

Originals and notes: `E:\FlipStudio\tienda\plantillas\estudio-<video>\` (`<video>.mp4`, `hoja.png`, `NOTAS.md`).

| Video | What it is | Prefix / module | Order | Output (`E:\FlipStudio\tienda\plantillas\…`) |
|---|---|---|---|---|
| 36232731.mp4 (57 s, 29.97 fps) | lower thirds + social media: like buttons, subscribe, social bars (@handle, «subscribe on…»), shape logo openers, «enjoy» | `yp8-*`, `templates_yp8.py` | 17000–17199 | `prototipos-yp8` |
| 27720858.mp4 (48 s) | creator pack: lightning, hearts, «TREND VIDEO» tape title, subscribe stickers, channel card, TikTok-style profile, LIVE / LIVE STREAM, social link bars, glitch blocks | `yp9-*`, `templates_yp9.py` | 17200–17399 | `prototipos-yp9` |
| 52531334.mp4 (36 s) | hand-drawn social titles: Like New Video, Subscribe My Channel, Social Media Title, New Podcast, New Video, @youraccount, Your Logo, Check New Video (Korean lines → Spanish/English words) | `yp10-*`, `templates_yp10.py` | 17400–17599 | `prototipos-yp10` |
| 45549099.mp4 (64 s) | YouTube titles & buttons: High Quality, Like, Follow Me, Play, Watch Now, 2023 Brand New, Looking Perfect, Click, Amazing, Use Any Language, Like my video, Channel Name, Rate Us, Subscribe, Trendy Style, New Video, Comment, Thanks for Watching, Share | `yp11-*`, `templates_yp11.py` | 17600–17799 | `prototipos-yp11` |
| 38494344.mp4 (91 s, 60 fps) | subscribe widgets over footage: avatar + name + subscribed + bell, round avatar with orbiting like/play/bell, like/subscribe/get-notified lists, channel cards | `yp12-*`, `templates_yp12.py` | 17800–17999 | `prototipos-yp12` |
| 35450339.mp4 (87 s, 25 fps) | «Social Media Buttons 70+»: post cards, chat bubbles, ratings and stars, counters (likes, followers), toggles, progress, players, to-do lists, «welcome to my channel» lists, pop-up dialogs | `yp13-*`, `templates_yp13.py` | 18000–18299 | `prototipos-yp13` |
| 34019110.mp4 (97 s, 25 fps) | «YouTube Buttons 80+»: channel cards on coloured photos, comment cards, subscribe/like/dislike/share/bell rows and buttons | `yp14-*`, `templates_yp14.py` | 18300–18599 | `prototipos-yp14` |
| 60440006.mp4 (20 s) | dark glass lower thirds with green subscribe pill, avatars, two-person bars | `yp15-*`, `templates_yp15.py` | 18600–18699 | `prototipos-yp15` |
| 59446629.mp4 (27 s) | frosted glass subscribe bubbles and cards with avatar over footage | `yp16-*`, `templates_yp16.py` | 18700–18799 | `prototipos-yp16` |
| 55227068.mp4 (27 s) | flat outlined channel cards with avatar, subscribe pill and bell over footage | `yp17-*`, `templates_yp17.py` | 18800–18899 | `prototipos-yp17` |

Category `ytkit`, tag `kit:<section>` (most go to `elementos`, `redes`, `tercios`, `tipografia`, `aperturas`).
`publish.py` already gives every `yp\d+-` piece `minAppVersion` 0.31.0.
Exe for renders: `E:/FlipStudio/pruebas/FlipStudio-motor-0109f/Flip Studio/flipstudio.exe`.

## Both formats (Jorge, 2026-11-15: «no olvides que es en los 2 formatos»)

Every piece must work as **Video (16:9) and Short (9:16)**: the app fits the design into the other shape
(`layoutfit.fit_doc`, `layoutRole`). Render the other shape with `short_check.py` and look at it (nothing cut, readable,
well placed); fix roles or layout when it does not fit. **Trap:** `short_check.py` rebuilds each template folder in
`--out` and deletes `preview-wide.mp4` and the thumbnails: give it its own `--out` folder or run it before `build.py`. The comparison video shows both renders under the original.

## Status

- 2026-11-15: modules created and registered; one agent per video studying and building.
- 2026-11-15: five more videos (yp13–yp17) added; both formats required.
- yp12 done: 13 pieces, `prototipos-yp12\comparacion-yp12.mp4` (Video + Short).
