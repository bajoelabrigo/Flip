# Plan 0.24.0 — efectos de texto solo en las letras seleccionadas (como Filmora)

Rama: `flip/v0.24-tramos` (sale de `main` = 0.23.0). Escrito por Claude el 2026-10-26 para que lo siga otro
asistente (DeepSeek). **Leer entero antes de tocar código, y después `docs/plan-0.23.md` › «Errores de DeepSeek».**

## Lo que pide Jorge

En Filmora, en el panel de Texto de la derecha (en Avanzado **y también fuera de él**), si sombreas una parte del
texto y aplicas **cualquier** cosa — estilo preestablecido, fondo, resplandor, sombra, transformación, trazo — se
aplica **solo a esas letras**. Si no hay nada sombreado, se aplica a todo el texto, como ahora.

## Lo que ya existe (0.23.0) — construir sobre esto, no inventar otro sistema

- `drift::TextRun` (`src/core/TextStyle.h`): tramo `{start, end}` (UTF-16) con color, tamaño, negrita, cursiva,
  subrayado y fuente propios, cada uno con su `*Enabled`. Vive en `TextStyle::runs`.
  Funciones: `normalizedTextRuns`, `shiftTextRunsForEdit`, `patchTextRuns` (suma lo nuevo y conserva lo demás),
  `textRunAt`. Pruebas: `CoreTest::textRunsStyleStretchesOfTheText`, `SkiaTest::textRunsPaintWithTheirOwnColourAndSize`.
- Trazado: `src/engine/TextLayout.cpp` parte el párrafo en trozos por (acento, emoji, tramo); ahí la variable de los
  tramos del estilo se llama `textRuns` (**ya existe otro `runs`**, el de Skia: no confundirlos).
- Pintado: `src/engine/SkiaTextPainter.cpp` pinta la pila `TextStyle::layers` (`TextShadingLayer`, tipos `Fill,
  Stroke, Shadow, Glow, Extrude` en `src/core/TextShading.h`) por trozo (`m_pieces`). **Ya hay un precedente:**
  `TextLayerScope { All, Base, Accent }` y el acento por palabra (`WordAccent`, `piece.accent`, `highlightFor`)
  pintan contorno/resaltado solo en algunas palabras. Copiar ese patrón.
- API QML: `AppController::textRuns`, `setTextRuns`, `patchTextRuns(track, clip, start, end, patch)`;
  `setTextStyle(track, clip, map)` (lo que usa el inspector para todo lo demás), `applyTextPreset`, `applyTextLook`,
  `addTextLayer`.
- Interfaz: `src/qml/components/properties/TextInspector.qml` (panel derecho; con `inAdvanced: true` es el de la
  ventana) y `src/qml/components/TextAdvancedDialog.qml` (tiene `selectionStart/selectionEnd/hasSelection` y ya
  manda la barra a `patchTextRuns`). Sesión de deshacer: `beginEditSession/endEditSession`.

## Diseño (recomendado)

1. **Modelo** — ampliar `TextRun` con overrides opcionales, cada uno con su `Enabled`:
   - `layersEnabled` + `QList<TextShadingLayer> layers`: la pila entera (relleno, trazo, sombra, resplandor,
     extrusión) de esas letras. Cubre **trazo, sombra, resplandor y los estilos preestablecidos/looks** (un preset
     con selección copia su pila — y su color/fuente si los trae — al tramo, no al bloque).
   - `boxEnabled` + color, relleno X/Y, radio, borde (puede reusar `TextHighlight` o los campos `box*`): **fondo**
     detrás de esas letras, uno por línea si el tramo se parte en dos líneas.
   - `transformEnabled` + `offsetX, offsetY, scale, rotation` (px a `pixelSize`, grados): **transformación** de
     esas letras alrededor del centro de su caja. No cambia el trazado del resto (como Filmora).
   - JSON: solo se escribe lo que está `Enabled` (igual que hoy). Proyectos viejos sin esos campos = como antes.
   - `patchTextRuns` tiene que copiar también estos campos (hoy solo conoce color/tamaño/B/I/U/fuente).
   - Los hashes de caché (`TextLayout.cpp` ~línea 75, `qHashMulti` de los runs) tienen que incluir los campos
     nuevos, o la vista previa no se refresca.
2. **Pintado** (`SkiaTextPainter.cpp`): para cada trozo cuyo tramo trae `layersEnabled`, usar `run.layers` en vez
   de `m_style.layers`. Orden: pintar los trozos en orden de texto, cada grupo con su pila completa (la sombra de
   un tramo puede caer sobre la letra de al lado, igual que en Filmora). Fondo del tramo: antes que las letras del
   tramo. Transformación: `canvas->save(); translate/rotate/scale` alrededor de la caja del grupo; `restore()`.
   El color de tramo (`colorEnabled`) sigue mandando sobre el relleno principal de su pila.
3. **Interfaz — lo importante:** una sola función en `TextInspector.qml`, p. ej.
   `applyStyle(map)`: si hay letras sombreadas → `EditorState.patchTextRuns(...)` con el patch traducido; si no →
   `EditorState.setTextStyle(...)` como hoy. **Todos** los controles de Estilo/Personalizar/Burbuja (presets, looks,
   fondo, resplandor, sombra, trazo, transformación) pasan por ahí. Tiene que funcionar:
   - en el panel derecho normal (seleccionar letras en el cuadro «Texto de entrada» del inspector — hoy esa
     selección solo existe en la ventana: exponerla en el inspector),
   - en la ventana de Texto avanzado (ya tiene la selección),
   - y con la selección hecha sobre la vista previa (doble clic → `InlineTextEdit`).
   - Al mover el cursor dentro de un tramo, los controles muestran **los valores del tramo** (si los tiene), no los
     del bloque. Sin selección muestran los del bloque.
   - Un aviso pequeño sobre los controles: «Se aplica a las letras seleccionadas» cuando hay selección.
   - Botón «Quitar estilo de las letras» (ya existe uno que vacía los tramos en la ventana: reusarlo).
4. **«Aplicar cambios a todos los textos»** sigue copiando el estilo del bloque; los tramos de cada texto se quedan.
5. **Web** (`flipstudio-app`): mismo modelo en el `.flip` (que los campos nuevos viajen en los dos sentidos). Si no
   da tiempo, que la web **conserve** los campos que no entiende al abrir y guardar (no borrarlos).

## Pruebas obligatorias

- `CoreTest`: JSON de ida y vuelta de cada campo nuevo; `patchTextRuns` con trazo sobre un tramo que ya tenía color
  conserva el color; `shiftTextRunsForEdit` mueve también los efectos.
- `SkiaTest`: un texto «HOLA MUNDO» con sombra roja solo en «MUNDO»: los píxeles bajo «HOLA» no cambian respecto a
  sin sombra, los de «MUNDO» sí. Lo mismo con trazo, resplandor, fondo y transformación.
- **En ventana (regla de Jorge, CLAUDE.md):** portable en `pruebas\`, `tools/e2e/shot.ps1 -TargetPid`,
  `click.ps1 -TargetPid`, `drag.ps1` para sombrear letras, y `-RedirectStandardError` para ver errores de QML.
  Probar los seis (preset, fondo, resplandor, sombra, transformación, trazo) con y sin selección, en el panel normal
  **y** en Texto avanzado, y que Aplicar = un deshacer y Cancelar lo devuelve. La vista previa sale negra en
  `shot.ps1` (PrintWindow): para ver los píxeles, exportar un fotograma o `capture full:true` por MCP.

## Errores que ya cometió DeepSeek (no repetir)

1. **Todo archivo QML nuevo va en `CMakeLists.txt`** (`qt_add_qml_module`). Si no, la app no lo encuentra y falla
   la prueba Traducciones.
2. **`qsTr` nuevos rompen la prueba Traducciones** si no se regeneran los `.ts`. Lo que funciona: el run de Windows
   que falla sube el artefacto `i18n-regenerated`; copiarlo a `i18n/`, rellenar las traducciones y subir. No
   resolverlo poniendo textos fijos en español. Nunca editar un `.ts` a mano sin pasar `lupdate` después.
3. **`qFuzzyCompare` no existe en QML/JS** (ReferenceError silencioso). Mirar siempre el stderr.
4. Usar propiedades sin declararlas (`panelDriven`) falla en silencio. Declarar todo.
5. Python en Windows escribe CRLF: `open(p, "w", newline="")`.
6. No decir «hecho» sin haberlo **visto en la ventana**: la 0.20.0 salió con una galería vacía por eso.

## Cómo cerrar

Una sola compilación de CI al final (`gh workflow run build.yml --ref flip/v0.24-tramos -f platforms=windows`),
probar el portable en ventana, versión 0.24.0 en `CMakeLists.txt`, `release-notes/0.24.0.md`, notas de la Store en
`docs/store-listing.md`, y la rutina de publicación de `CLAUDE.md`. Mantener **este archivo** al día con lo hecho y lo
que falta, y subir a la rama a menudo.

## Estado

- [ ] Modelo (`TextRun` ampliado, JSON, `patchTextRuns`, hashes) + pruebas Core
- [ ] Pintado (pila, fondo, transformación por tramo) + pruebas Skia
- [ ] Inspector: `applyStyle` único, selección en el panel normal, valores del tramo bajo el cursor
- [ ] Texto avanzado y vista previa
- [ ] Web (o al menos conservar los campos)
- [ ] Prueba en ventana de los seis efectos, con y sin selección
- [ ] Publicar 0.24.0
