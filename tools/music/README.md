# Stock › Música

Cortes de 15, 30 y 60 s, por ánimo, de música de **dominio público (CC0 1.0)**.

| Paso | Qué hace |
|---|---|
| `py tools/music/fetch.py` | Baja las canciones a `tienda/musica/fuente` y anota de dónde viene cada una (`sources-*.json`: página, archivo, licencia, fecha) |
| `py tools/music/survey.py` | Analiza cada canción (tempo, compases, secciones, volumen) y deja `analisis/survey.tsv` para elegir |
| `py tools/music/build.py` | Corta, nivela (-14 LUFS, picos bajo -1 dBTP) y empaqueta lo de `catalog.py` en `tienda/musica/paquetes/<id>` |
| `py tools/music/review.py` | Hojas de revisión (espectrograma + nivel de cada corte) en `tienda/musica/revision` |
| `py tools/music/publish.py` | Lo deja en `tienda/plantillas/publicar/musica` con `index.json`, `CREDITS.json` y `LICENCIA.txt` |

Después se sube con `flipstudio-api/deploy/plantillas.ps1` (tipo `music`).

**Fuentes (solo estas):**
- **FreePD** (freepd.com, cerró en 2025): «This music is all licensed CC0 1.0 Universal Public Domain Dedication» y
  permite incluirla en software. Comprobado en
  https://web.archive.org/web/20241231185827/https://freepd.com/ y en el README del espejo de donde se bajan
  (https://a.ocv.me/pub/stuff/music/freepd/). Es la misma fuente del extra «musica.libre».
- **HoliznaCC0** en Free Music Archive: `fetch.py` lee la página de cada pista y solo la guarda si su licencia es
  `creativecommons.org/publicdomain/zero/1.0/`.

Nada de Pixabay, YouTube Audio Library, Mixkit, Uppbeat ni Sonniss: no dejan redistribuir su música como catálogo.

**Cómo se corta** (`cuts.py`): empieza en un tiempo fuerte (o al principio de la canción), toca un número par de
compases (mejor 4 u 8), deja sonar el golpe siguiente y se desvanece; o, si cabe, termina con el final propio de
la canción. Nunca pasa de la duración nominal (15 s de una historia caben en una historia).

**Catálogo** (`catalog.py`): una línea por canción, `clave | ánimo | duraciones | etiquetas | opciones`.
