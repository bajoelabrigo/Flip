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

## Arreglo aparte (hacer PRIMERO, es corto): Tendencias agrega el texto dos veces

**Lo que ve Jorge:** en Títulos › Tendencias, un texto que no tiene se descarga y se agrega una vez (bien). Cuando
ya está descargado, cada clic lo agrega **dos veces**.

**Causa (encontrada por Claude, 2026-10-26):** en la tarjeta hay **dos `TapHandler` que responden al mismo clic**
y los dos llaman a `useTrend`:
- `StockThumb` tiene su `TapHandler` → `openRequested()` → `onOpenRequested: root.useTrend(...)`;
- encima, el `AssetDragSource` (solo `enabled` cuando ya está instalado) tiene otro `TapHandler` →
  `onTapped: root.useTrend(...)`.

Sin descargar, el `AssetDragSource` está apagado y solo responde uno; ya descargado, responden los dos y como
`installedTrendId` ya existe, cada uno hace `addTextClip`. **El mismo fallo está en Efectos › Tendencias.**

- `src/qml/components/assets/TextAssetsTab.qml` ~línea 594 (`onOpenRequested`) y ~623 (`onTapped` del
  `AssetDragSource`).
- `src/qml/components/EffectBrowser.qml` ~línea 429 y ~458 (mismo par).

**Arreglo:** que la miniatura solo responda cuando todavía **no** está instalado (después el que responde es
`AssetDragSource`, que además permite arrastrar):
```qml
onOpenRequested: if (trendCard.installedId.length === 0) root.useTrend(trendCard.modelData)
```
(En `EffectBrowser.qml` usar la propiedad equivalente de su `trendCard`; mirar cómo decide `enabled` su
`AssetDragSource` y usar la misma condición negada.) No quitar el `TapHandler` de `StockThumb`: lo usan muchas
otras tarjetas.

**Revisar también:** las demás tarjetas que ponen un `AssetDragSource` dentro de un `StockThumb` (buscar
`StockThumb {` en archivos que tengan `AssetDragSource`). En `docs/plan-0.23.md` quedó anotado que un clic en
«Título limpio» puso dos textos: puede ser lo mismo (dos manejadores en la tarjeta).

**Probar en ventana:** clic en un texto de Tendencias sin descargar → 1 texto; clic otra vez → 1 más (total 2, no
3); arrastrarlo a la línea de tiempo sigue funcionando. Lo mismo en Efectos › Tendencias (un efecto por clic).
Contar los clips con `inspect` por MCP o en la línea de tiempo.

## Arreglo aparte 2 (corto): los interruptores del texto quedan cortados a la derecha

**Lo que ve Jorge** (captura `Downloads\Captura de pantalla 2026-10-26 112538.png`): en Texto avanzado › Estilo, los
interruptores de **Fondo, Resplandor y Sombra** (y los botones «Recto · Suave · Salto») salen pegados al borde
derecho y la barra de desplazamiento tapa casi la mitad del interruptor. Falta margen a la derecha.

**Causa:** en `src/qml/components/TextAdvancedDialog.qml` ~línea 627, la columna de la derecha (`sideColumn`,
dentro de `Flickable sideScroll` con `AppScrollBar`) tiene `width: sideScroll.width - Theme.spacingMd` y ningún
margen izquierdo. La barra de desplazamiento se dibuja **encima** del contenido, y `CollapsibleSection` ancla el
interruptor a `parent.right`, así que queda debajo de la barra.

**Arreglo:** dejar el mismo hueco que deja el panel de la derecha (`PropertiesPanel.qml` ~línea 591, `tabColumn`):
```qml
Column {
    id: sideColumn
    x: Theme.pagePadding
    width: sideScroll.width - Theme.pagePadding * 2 - (Theme.spacingLg + 4)
    ...
```
No tocar `CollapsibleSection.qml` (lo usan todos los paneles y en ellos se ve bien). Si en el panel de la derecha
normal también se viera cortado, revisar ahí el `width` de `tabColumn` en `sheetMode`.

**Probar en ventana:** abrir Texto avanzado, pestañas Estilo, Personalizar, Animación y Burbuja, con la barra de
desplazamiento visible (que la lista sea más larga que la ventana): cada interruptor se ve entero con aire a la
derecha, y la ventana maximizada también.

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

## Estado (2026-10-26, DeepSeek; CI del run 40370485636 EN VERDE)

- [x] Modelo (`TextRun` ampliado: `layersEnabled`+`layers`, `boxEnabled`+color/relleno/radio/borde,
      `transformEnabled`+offsetX/offsetY/transformScale/rotation; JSON solo si se usaron; `patchTextRuns` los suma;
      el hash de `layoutKey` los cuenta) + `CoreTest::textRunsCarryEffectsBackgroundAndTransform`.
- [x] Pintado: `SkiaTextPainter.cpp` usa la pila del tramo cuando la trae (`drawStack` por grupo), pinta su fondo
      (`drawRunBackgrounds`, una caja por trozo) y aplica su transformación alrededor del centro de su caja
      (`drawPiece`); los trozos sin tramo siguen con la pila del bloque. `SkiaTest::textRunEffectsStayInsideTheirLetters`
      compara píxeles: sombra roja, trazo, fondo y transformación solo en «MUNDO», con «HOLA» intacta.
- [x] Inspector: **una sola puerta** `applyStyle(patch)`
      (`src/qml/components/properties/TextInspector.qml`): con letras sombreadas en «Texto de entrada» llama a
      `patchTextRuns` con `runPatchFor(patch)`; sin selección, `setTextStyle`. Los cinco llamadores directos de
      `setTextStyle` pasan por ella, y el acento por palabra se queda en el bloque (no es por tramo).
      Aviso «Se aplica a las letras seleccionadas». La ventana de Texto avanzado le pasa su selección
      (`runSelectionStart/End`).
- [x] API de tramos con los campos nuevos en los dos sentidos (`textRuns`, `setTextRuns`, `patchTextRuns`), o la
      ventana de Texto avanzado los borraría al guardar.
- [x] Los dos arreglos cortos («Arreglo aparte» 1 y 2): Tendencias ya no agrega dos veces (Títulos y Efectos) y la
      columna de la derecha de Texto avanzado deja el hueco de la barra de desplazamiento.
- [x] Catálogos: el run que falló en Traducciones subió `i18n-regenerated`; copiado a `i18n/`, «Se aplica a las letras
      seleccionadas» en `drift_es.ts`, y el CI siguiente en verde.
- [ ] **Prueba en ventana** (pendiente, es lo único que falta para decir «hecho»): portable del run 40370485636
      descargado y descomprimido en `pruebas\portable-0.24\app`, registro copiado y restaurado. El ejecutable sale
      enseguida con `--mcp-stdio` («MCP is off») aunque `mcp/startOnLaunch` esté en el registro: hay que abrirlo con
      el arnés (`py tools/e2e/mcp_e2e.py --window …`) y no con el flag suelto, y después `shot.ps1`/`click.ps1`
      con `-TargetPid` y `drag.ps1` para sombrear letras. Probar los seis (preset, fondo, resplandor, sombra,
      transformación, trazo) con y sin selección, en el panel normal **y** en Texto avanzado.
- [ ] Valores del tramo bajo el cursor en los controles (hoy muestran los del bloque).
- [ ] Transformar (mover/girar/escalar) desde la sección Transformar del inspector cuando hay selección: hoy el
      modelo y el pintado lo admiten, pero esa sección no pasa por `applyStyle`.
- [ ] Web (o al menos conservar los campos nuevos al abrir y guardar).
- [ ] Publicar 0.24.0 (sin tags ni publicación sin el OK de Jorge).
