# Animaciones como Filmora (pedido de Jorge, 2026-10-22)

Jorge mandó las capturas de Filmora (en `Downloads`): **Títulos › Animación › Entrada**
(`animacion - Entrada 1.png` y `animacion - Entrada 2.png`, unas 200), **Salida**
(`Animacion - Salida.png`, unas 85) y **Video › Animación › Combinado** (`animacion - Combinado.png`,
unas 60). Quiere esas animaciones en Flip. Versiones propias, no copias (ver memoria «Stock: trends»).

Rama: **`flip/animaciones`** (sale de `main` con la 0.19.0). El editor web va detrás, en
`flipstudio-app` (rama `web/animaciones`), igual al escritorio.

## Lo que ya había

- Texto: motor de animadores tipo After Effects (`core/TextAnimator.*`, presets JSON en
  `presets/text-animations/`, 47 incluidos) y 200 en Stock › Textos animados
  (`tools/text_stock/anims_*.py`). El panel Texto › Animación tiene Entrada/Salida/Bucle con chips y
  tarjetas que se reproducen al pasar el mouse (`TextAnimPresetTile`).
- Clips: `core/ClipAnimation.*`, un `enum` de 11 tipos (deslizar, zoom, girar, rebote), solo Entrada y
  Salida, elegidos en una lista (`AnimationInspector.qml`).

## Qué se hace

### 1. Motor de texto (escritorio)
- **Giro 3D por letra**: `rotationX` / `rotationY` en los animadores (puerta, voltear, rodar en 3D).
- **Emoji o símbolo que acompaña al texto** (cursor de glifo): «ABC⚡», «ABC💎», «ABC★»… El cursor de
  la máquina de escribir puede ser un glifo, con tamaño, giro y rebote.
- **Partículas**: chispas, estrellas, polvo, humo, confeti, anillos y glifos que salen de cada letra
  al aparecer o al irse (explosión, polvo de hadas, humo, chispas, fuegos artificiales…).
- Todo en el preset (`"particles"`, `"caret"` con `"shape": "glyph"`), así que Stock puede traer más.

### 2. Animaciones de texto nuevas (incluidas en la app)
- Chips de Entrada como Filmora: **Tendencias, Movimiento y trayectoria, Máscara y revelado, Fluido,
  Construcción, Estilizado, Partículas**. Salida: **Tendencias, Ocultar y enmascarar, Escalonado,
  Estilizado, Partículas**. Las 47 de antes se reparten en estos chips.
- Meta: ≥ 200 en Entrada y ≥ 85 en Salida (además de las de antes).

### 3. Animaciones de clip con presets (Video › Animación)
- `ClipAnimation` gana `preset` (JSON en `presets/clip-animations/`): curvas de posición, escala,
  giro, giro 3D, opacidad y desenfoque, más efectos del catálogo con parámetros animados
  (desenfoque de zoom, separación RGB, giro, etc.).
- Tercera pestaña **Combinado** (entra y sale en una sola animación, dura todo el clip o lo que se elija).
- Panel con tarjetas y vista previa animada al pasar el mouse, como Filmora.
- Meta: ≥ 60 Combinado, y más Entrada/Salida de clip.

### 4. Editor web
- Mismo formato de presets (se copian del repo de escritorio) y el mismo panel.

### 5. Publicar
- Compilar una vez (`build.yml`), probar en ventana, 0.20.0.

## Estado

- [x] Barra de abajo del celular pegada al final (web, `flipstudio-app` `web/movil`, desplegado
  2026-10-22): `.ph` y `.app.is-touch` usan `position: fixed; inset: 0` en vez de `100dvh`, que en
  el iPhone instalado como app medía menos que la pantalla.
- [x] 1. Motor de texto (commit `01cd8`: giro 3D, cursor de glifo, partículas)
- [x] Lo de arriba no bastaba: la barra seguía alta en el iPhone instalado. La causa era
  `apple-mobile-web-app-status-bar-style` = `black-translucent`; con `black` queda abajo (como la app de
  gastos). Hay que borrar el ícono y volver a agregarlo. Jorge lo confirmó (2026-10-22).
- [x] 2. Animaciones de texto: **302 nuevas** (216 Entrada, 86 Salida) en `tools/text_animations/`, nombres en
  12 idiomas. Revisadas en hojas (`build.py --sheet`, `pruebasnimaciones-texto`).
- [x] 3. Animaciones de clip: 49 Entrada / 55 Salida / 62 Combinado, revisadas en hojas (script de la
  sesión: proyecto con un texto «FLIP», `set_animation` por MCP y `DRIFT_CLIP_ANIMATIONS` apuntando a
  `presets/clip-animations` para no depender de lo compilado).
- [x] 4. Web (`flipstudio-app` `web/animaciones`): galería de texto con chips y tarjetas (`TextAnimSection`),
  galería de clip (`ClipAnimGallery`), el lienzo dibuja partículas, cursor de glifo, giro 3D y barrido;
  `scripts/sync-desktop-anims.mjs` copia los presets; los 16 idiomas.
- [ ] 5. Publicar 0.20.0 (notas en `release-notes/0.20.0.md`, CHANGELOG y `docs/store-listing.md`).

## Trampas de esta versión

- **El commit del motor (`01cd8`) nunca había compilado:** `SkPath::transform` y `SkMatrix::mapXY` no
  existen en nuestro Skia (giro a mano con seno y coseno), y las pruebas inicializaban `ClipAnimation`
  con llaves (ganó un campo `presetId`).
- **Una partícula suelta (objeto, no lista) no se dibujaba:** el motor lo leía como `{in, out}` por momento.
  36 animaciones no mostraban ninguna partícula. `tkit.T.document()` escribe siempre una lista, y el
  escritorio y la web aceptan también un objeto con `shape`.
- **Opacidad en las curvas va de 0 a 100**, no de 0 a 1 (tres salidas se veían casi invisibles).
- **Combinado con una salida que ya es de salida** (`O[...]`): `combo()` la invertía otra vez y el clip se
  iba a mitad y volvía al final. Ahora solo invierte las de entrada.
- **«elastic» hace casi todo el movimiento en el primer 10 %:** en la hoja parece quieto. Mejor claves con
  un rebote visible.
- **`digital_glitch` y `scanline_glitch` devolvían alfa 1:** sobre un texto o sticker pintaban un recuadro
  negro. Las capas usan alfa sin premultiplicar: no recortar el color por el alfa.
- **Los textos de muestra con salto de línea no llegaban a lupdate:** `catalog_strings.py` escapa los saltos de línea (`\n`).
- Las hojas se revisaron con agentes en paralelo (tres para texto, dos para clip): su lista sirve de
  punto de partida, pero hay que mirar la hoja antes de cambiar nada (algunos avisos eran del muestreo).
