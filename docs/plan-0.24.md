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

## Estado (2026-10-26, DeepSeek)

**Ojo: el workflow «Build» estaba en verde pero «Tests» NO.** Los runs 40370485680, 40373586041 y
40377649004 fallaban en `SkiaTest::textRunEffectsStayInsideTheirLetters` con «shadowRight r0 g0 b255».
Era un fallo **de la prueba**, no del pintado: `inkOf` leía los canales como ARGB sobre una imagen
RGBA8888, así que el rojo puro salía en el canal azul. Arreglado `inkOf` (convierte a ARGB32), el estilo
base de la prueba lleva relleno blanco y los tramos llevan la **pila completa** (relleno + efecto), que es
lo que manda el inspector. **Comprobar siempre los dos workflows** (`gh run list -b flip/v0.24-tramos`).

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
- [x] **Los dos workflows en verde con el arreglo de pruebas**: `Tests` run 40382869307 y `Build` run
      40385029357, los dos en `9d55c`. Ojo: antes de eso `Tests` fallaba en
      `SkiaTest::textRunEffectsStayInsideTheirLetters` (runs 40370485680, 40373586041, 40377649004) y el
      «Estado» decía que estaba en verde: era falso. Causa: `inkOf` leía los canales como ARGB sobre una
      imagen RGBA8888 (el rojo salía en el azul) y el estilo base de la prueba no pintaba letras, así que
      las comparaciones no significaban nada. Arreglado el lector, con relleno blanco de base, pilas
      completas en el tramo y las regiones de medida lejos de la frontera de la letra 5.
- [x] **La app abre el proyecto en ventana, una sola instancia** (`.drift` con «HOLA MUNDO» hecho por MCP y
      abierto con el ejecutable): texto en la vista previa y en la línea de tiempo, `stderr` sin errores de
      QML. Capturas en `pruebas/v024-capturas` (`01_texto_seleccionado.png`).
- [x] **Los dos workflows en verde con todo lo de esta tanda**: `Tests` 40395917421 y `Build` 40395917729
      (portable nuevo). Incluye: el campo del inspector conserva el sombreado (`persistentSelection`),
      la capa nueva (trazo/fondo/resplandor/sombra) y el preset van al tramo con letras sombreadas
      (`addTextLayer`/`applyTextQuickStyle` con `rangeStart/rangeEnd`), la sección Transformación manda
      `offsetX/offsetY/transformScale/rotation` del tramo y enseña sus valores (`runUnderCursor`), la
      guarda contra el bucle de `expandedLayerIds` y la pestaña de Texto avanzado que vuelve a seguir al
      panel tras «Más estilos».
- [ ] **Recorrido en ventana** de los seis efectos con y sin letras sombreadas (panel normal y Texto avanzado),
      con el portable del CI de esta tanda. Lo hace Claude antes de publicar.
- [ ] Selección hecha sobre la vista previa (`InlineTextEditor`): todavía no manda las letras al inspector. Queda
      fuera a propósito: al terminar de escribir el rango seguiría activo sin aviso. **Hecho después** (ver la
      ampliación de abajo).
- [ ] Teclas de fotograma (rombos) en las capas de unas letras: no hay (`layerProp` sin clave con letras sombreadas).
- [ ] Web: dibujar los efectos por letras (por ahora solo los conserva al abrir y guardar).

## Ampliación pedida por Jorge (2026-10-26, noche): sale todo en la 0.24

Pendientes que quedaban, más las mejoras de texto que propuso Claude («aprovechemos esto para hacer todo»):

- [x] Selección sobre la vista previa: al terminar de escribir con letras elegidas, el «Texto de entrada» del panel
      las sombrea (`AppController::textLettersPicked`); un inspector que pierde las letras las suelta
      (`textStyleRangeChanged`).
- [x] Rombos de fotograma clave en las capas de unas letras: las capas de un tramo llevan ids propios (`<id>~n`,
      `writeTextRangeLayers`) y el mapa de claves del texto también las busca en los tramos (`findStyleLayer` en
      `TextStyle.cpp`). `scaleTextStyle` escala también lo de los tramos (DeepSeek lo había olvidado).
- [ ] Web: dibujar los efectos por letras (agente en `flipstudio-app`, `web/v0221-texto`).
- [ ] Márgenes de Texto avanzado (Arreglo aparte 2): mirarlos en ventana, y el panel derecho también.
- [x] 1. Espacio entre letras e interlineado solo en las letras elegidas (`TextRun::letterSpacing*`, `lineHeight*`;
      la línea toma el mayor interlineado de las letras que lleva).
- [x] 2. Opacidad de las letras elegidas (`TextRun::opacity*`, `opacityOf()` en el pintor).
- [x] 3. Superíndice y subíndice (`TextRun::baseline`: 1/−1, tamaño ×0,62, sube 0,36 em o baja 0,16 em).
- [x] 4. «Quitar estilo» de las letras elegidas en el panel (`AppController::clearTextRunsIn`), en la sección nueva
      «Letras seleccionadas» del inspector (tamaño, espacio, interlineado, opacidad, x²/x₂, copiar/pegar/quitar).
- [x] 5. Copiar el estilo de unas letras y pegarlo en otras (`copyRunStyle`/`pasteRunStyle` del inspector).
- [x] 6. Texto que se encoge para caber en su caja (`TextStyle::shrinkToFit`, búsqueda en `fragmentsFor`; al
      encenderlo la caja deja de seguir al texto, `textAutoFit` = false).
- [ ] 7. Buscar y reemplazar en todos los textos y subtítulos del proyecto (agente en la rama `flip/v0.24-buscar`).
- [x] 8. Ligaduras y versalitas (`TextStyle::ligatures`/`smallCaps` → `liga`/`clig`/`smcp` en `styleFor`).

- [x] Editor de curvas (pedido de Jorge, 2026-10-27), escritorio y web:
      - **se queda abierto** al mover el cabezal o soltar la selección, hasta cerrarlo con su **×** (sigue a la
        selección solo hacia un clip con animación; `KeyframeGraph.pinnedClipId` + `AppController::clipLocation`;
        web `curvePin` en `App.tsx`);
      - **se abre debajo de la pista de su clip**, no sobre la línea de tiempo: `trackRowHeight` suma su alto con
        `metrics.curveTrack/curveEditor` y `curveOverlay` (TimelinePanel) lo dibuja en ese hueco; web
        `.curve-under-track` en `Timeline.tsx`;
      - en la web medía más que el del escritorio: ahora 88/180 px y solo las propiedades animadas.

## Revisión de Claude (2026-10-26, noche): errores de DeepSeek y arreglos

1. **El fondo de las letras se escalaba dos veces** (`drawRunBackgrounds` multiplicaba por `m_scale` un `cellRect`
   que ya está en píxeles de salida): en la vista previa (media escala) caía a un cuarto y fuera de las letras. La
   prueba solo miraba escala 1. Arreglado y con caso a media escala en `SkiaTest`.
2. **Transformación:** el desplazamiento salía girado y escalado (se aplicaba dentro del giro), el fondo no se movía
   con las letras, y dos tramos vecinos (p. ej. «MU» con color y «NDO» sin él) giraban cada uno sobre su centro.
   Ahora `applyRunTransform` (mismo para letras y fondo) y una caja por tramos vecinos con la misma transformación.
3. **El color de las letras con pila propia** comparaba con el relleno del bloque (`isPrimaryFill`); ahora con el de
   su pila (`stackOf`). Las letras a medio desvanecer perdían su fondo; la sombra/resplandor de las letras no
   contaba su propio trazo.
4. **El margen de pintado (`bleedFor`) no contaba lo de los tramos:** una sombra, un fondo o un giro de unas letras
   se recortaba en el borde. La prueba de píxeles se cambió para comparar sobre un lienzo común.
5. **Lo más grave: las capas no llegaban a las letras.** Con letras sombreadas, `addTextLayer` creaba la capa en el
   tramo, pero todos los controles (color, grosor, desenfoque, quitar, duplicar, mover, las filas de capas, el
   editor de pintura y de degradado) seguían leyendo y escribiendo la pila **del bloque** por id: después del
   primer clic nada tocaba las letras. Además mutaba el proyecto **después** de `pushProjectEdit` (el deshacer
   guardaba otra cosa). Ahora `AppController::setTextStyleRange` (lo manda el inspector al cambiar la selección) y
   las llamadas de capas, looks, plantillas y estilos rápidos editan la pila de esas letras con un paso de deshacer
   cada una; `root.layers` del inspector muestra esa pila. Prueba `EditorStateTest::shadedLettersTakeLayersLooksAndBoxAlone`.
6. **`patchTextRuns` copiaba el fondo y la transformación enteros:** mover el relleno ponía el color en negro,
   cambiar X ponía Y a 0, y apagar el fondo lo **encendía** (`boxEnabled` se forzaba a `true`). Ahora clave por clave.
7. Con letras sombreadas, un control sin equivalente en las letras (alineación, interlineado…) no hacía nada y
   dejaba un paso de deshacer vacío: ahora va al bloque. La B (`fontWeight`) y los dos rellenos del fondo se traducen.
8. **Textos fijos en español** en la interfaz («Escala», «Giro»): ahora `qsTranslate` de contextos ya traducidos.
   El campo de escala no admitía decimales (`decimals: 0`).
9. **Web:** el `.flip` perdía el subrayado y la fuente de las letras (el tipo los tenía, el lector y el escritor no)
   y perdería los efectos 0.24: ahora se conservan (`flipstudio-app` `web/v0221-texto`, prueba en `runs.test.ts`).
