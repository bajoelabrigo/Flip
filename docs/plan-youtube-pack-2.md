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

Category `ytkit`, tag `kit:<section>` (most go to `elementos`, `redes`, `tercios`, `tipografia`, `aperturas`).
`publish.py` already gives every `yp\d+-` piece `minAppVersion` 0.31.0.
Exe for renders: `E:/FlipStudio/pruebas/FlipStudio-motor-0109f/Flip Studio/flipstudio.exe`.

## Status

- 2026-11-15: modules created and registered; one agent per video studying and building.
