# Plan de la 0.18.0 (pedido de Jorge, 2026-10-18)

Este archivo es para **seguir el trabajo con cualquier asistente** (Claude, DeepSeek u otro). Antes de nada, leer
`CLAUDE.md` (mapa del proyecto, rutina de publicación y trampas). Rama: **`flip/v0.18.0`** (sale de `main` con la
0.17.0 publicada). Regla de Jorge: si CapCut o Filmora ya resolvieron cómo se comporta algo, se copia. Todo lo que
lee Jorge va en español; el código sigue el estilo del archivo (inglés).

Pedido: «Comienza con lo que falta» (el seguimiento de la 0.17) + «en los efectos, plantillas, transiciones y LUT
pon fotos variadas para que no quede todo igual» + «Haz todo lo pendiente».

Leyenda: ✅ hecho en la rama · 🟡 empezado · ⬜ por hacer.

## 1. Contadores de Stock con el contador del motor
- ✅ Motor: `TextStyle.counterSeconds` (cuánto dura el conteo desde el inicio del clip; 0 = el 85 % de la 0.17) y
  relleno con ceros («05:00», «007»): `drift::counterTextAt(text, from, progress, land)`; pruebas en
  `CoreTest::counterTextCountsInTheTextsFormat`. Se guarda en el proyecto solo si es > 0.
- ✅ Plantillas (`tools/scene_templates/templates_c1.py`): `count_fn` hace **un solo texto editable** con
  `counter/counterFrom/counterSeconds` y un pequeño «salto» de tamaño al llegar (`landing_pop`). 15 plantillas
  pasan al motor; **barra de carga y marcador** siguen con cortes (`cuts=True`: su ritmo no es una curva suave), y
  el temporizador y los dos odómetros no cambian. Las barras y el anillo que acompañan al número usan la misma curva
  (cúbica) que el motor.
- ⬜ Renderizar miniaturas y previas de las 15 con un portable de la 0.18 (la 0.17 no conoce `counterSeconds`:
  aterrizaría tarde) — `tools/scene_templates/build.py --only cont-…` — revisar en hoja de contacto y **publicar al
  salir la 0.18** (`publish_delta.py` + `apply_delta.sh`). Una app 0.15/0.16 muestra el número final quieto.

## 2. Fotos variadas en las miniaturas (Jorge, 2026-10-18)
- Hoy: Transiciones de la app = todas el mismo camino con trigo; Plantillas de efectos = todas el loro; los efectos
  de color = todos el mismo lago; LUTs de Filtros = todas la misma mujer. Stock (LUTs y transiciones) ya era variado.
- Fotos: las 16 CC0 de `flip-addons/work/drift-addons/assets/thumbs` (`CREDITS.md`).
- ✅ Reparto en `tools/effects/thumb_bases.json` (efectos por id, plantillas por id, pares para transiciones).
- ✅ `tools/effects/vary_thumbs.py --tools <carpeta>` redibuja con `effectthumbs`, `templatethumbs` y
  `transitionthumbs` (las tres aceptan `--only` y la foto). `package.yml` sube las tres como artefacto
  **`windows-thumb-tools`**: copiarlas dentro de un portable descomprimido (necesitan sus DLL).
- ✅ LUTs: `AppController::lutThumbnail` elige una de 13 fotos por el nombre del LUT (`lutReferencePhoto`, FNV) y
  `lutReference(path)` da esa foto para el «antes» (Filtros y Ajustar › LUT).
- ✅ Corrido con el artefacto de la compilación 39170043199: 33 efectos, 23 plantillas de efectos y 39 transiciones
  redibujadas y revisadas en hoja de contacto (Curvas se quedó con la suya: salía gris; Tormenta de flashes y Chasquido
  pasaron a fotos oscuras). `before_bases.py`: 71 efectos con antes y después.

## 3. Antes y después en Efectos
- ✅ `tools/effects/before_bases.py` escribe `resources/effectbases/<foto>.jpg` (256 px, recorte cuadrado como
  `squareCrop`) y `map.json` (efecto → foto), comprobando que la miniatura se parezca a su foto (si no, la deja
  fuera; `KEEP` = revisadas a ojo). Recurso `:/effectbases` en `CMakeLists.txt`.
- ✅ `effectCatalog()` trae `beforeImage`; `EffectBrowser.qml` usa `BeforeAfterImage` al pasar el mouse.
- Fuera a propósito: `color.lut` (miniatura de otra foto), `face_mesh_3d`, `face_props` (dibujos), película
  granulada (solo grano), intercambio de cara.

## 4. Cámara lenta suave con IA (RIFE)
- ✅ `AppController::canSmoothSlowMotion` / `smoothSlowMotion`: cada fotograma del clip lento (velocidad < 1 o
  curva) se dibuja al fps del proyecto desde los dos fotogramas de origen que lo rodean (RIFE en medio; si cae
  casi en uno, se usa ese), se escribe con `MatteWriter` en modo color y el clip pasa a leer ese render a 1×
  (mismo lugar, duración, efectos). El audio incrustado se separa antes (`separateAudioFromSelection`) para que
  conserve su tiempo. Máximo 3 minutos. Botón «Cámara lenta suave» + marca IA en Velocidad
  (`SpeedFadeInspector.qml`). Usa el extra `transiciones.ia`.
- ⬜ Probar en ventana con un clip a 0,25×.

## 5. Foto de la tarjeta «Imperfecciones»
- ⬜ `resources/retouch/skin-blemish.jpg` es copia de skin-smooth: rehacerla con la app (ver
  `resources/retouch/README.md`) con el efecto `face_blemish`.

## 6. Voz con IA en el editor web (`flipstudio-app`) — ✅ DESPLEGADA (2026-10-18)
- Pestaña **Voz** (`src/components/VoicePanel.tsx`): texto, idioma (español, inglés, portugués, francés, italiano),
  voz, velocidad → «Crear voz» → WAV en Medios y en la línea de tiempo en el cursor.
- `src/voice/worker.ts`: Kokoro-82M q8 (`StyleTextToSpeech2Model` de transformers.js 4.3, como kokoro-js) +
  fonemas de **eSpeak NG de Echogarden** (`@echogarden/espeak-ng-emscripten` 0.3.5, GPL-3: la librería `phonemizer`
  de kokoro-js solo trae inglés). `src/voice/kokoro.ts`: cortes por frase, fonemas (para idiomas que no son inglés,
  el mapa E2M de misaki: tʃ→ʧ, eɪ→A…; **no** cambiar r→ɹ ni x→k), estilo por longitud y WAV.
- Archivos en el VPS: `/var/www/flipstudio-models/modelos/kokoro-82m/` (config, tokenizer, `onnx/model_quantized.onnx`,
  9 voces en `voices/`) y `/modelos/espeak-ng/espeak-ng.data` (24 MB). Copia local en `tienda\modelos-web`.
- Comprobado: `scripts/voice-check.ts` en Node + Whisper small transcribe igual (es, en, pt); en Chrome local y en
  **getflipstudio.com/editor** (3,5 s de voz en la línea de tiempo).
- **Trampa:** esa build de eSpeak **ignora `locateFile`** para su `.data` y la pide junto al script (en el sitio,
  una página HTML de 1,5 KB → fonemas vacíos → audio de 0,3 s). El worker redirige ese `fetch` a `/modelos/espeak-ng/`.
- **Trampa:** un worker cuya carga falló a medias no vuelve a cargar: ante un error el panel lo descarta.

## 7. Arrastre «tipo tetris» en la línea de tiempo (Jorge, 2026-10-18)
- Pedido: al arrastrar un clip hacia adelante o atrás no debe subir ni bajar; solo cambia de pista cuando se lleva
  claramente arriba o abajo, como en CapCut y Filmora.
- ✅ `TimelineTrackItem::applyDrag`: el clip encaja en filas enteras (`TimelineViewState.rowSpans`, que arma
  `TimelinePanel.rowSpans()`); cambia de fila solo cuando su centro entra en otra. Por encima de la primera o debajo
  de la última sigue libre (pista nueva). Las capas de ajuste siguen libres (sus carriles van dentro de una fila).
- ⬜ Probarlo en ventana.

## 8. Arreglo: el contador no contaba en la vista previa ni al exportar
- Encontrado al renderizar las plantillas: la 0.17 solo aplicaba el contador en `makeTextPainter(clip, …)`, pero la
  vista previa y la exportación dibujan por `FrameCompositor::fillTextLayer`. ✅ Ahora lo aplica ahí (el texto que se
  está editando queda como se escribió). Las 15 plantillas de contador hay que **volver a renderizarlas** con la
  compilación que trae este arreglo.

## Traducciones
- ✅ Las 12 frases nuevas (cámara lenta suave) en es y los 11 idiomas completos; `lupdate` estable.

## Al cerrar la versión
Versión 0.18.0 en `CMakeLists.txt`, `release-notes/0.18.0.md`, CHANGELOG, notas de la Store en
`docs/store-listing.md`, compilación, prueba en ventana, PR, tag, release, MSIX, copia en `versiones`, novedades en
la web, contadores a Stock y `CLAUDE.md`. Lo de Jorge: TXT `version` y Partner Center.
