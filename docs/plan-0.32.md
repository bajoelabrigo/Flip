# Plan 0.32 (rama `flip/v0.32`, worktree `codigo\Flip-032`)

Pedidos de Jorge del 2026-11-15. La versión sigue en 0.31.0 en `CMakeLists.txt` (la decide quien coordina).

## 1. Colores en el panel Plantilla — HECHO (código), falta probar en ventana

- `TemplateFillPanel.qml`: sección **Colores** (antes de Música): los colores de la plantilla, los más usados
  primero (hasta 10). Clic en una muestra → el selector de color de siempre (`ColorSwatchField`) → cambia ese color
  en toda la plantilla en **un solo paso de deshacer**, conservando la transparencia de cada capa.
- C++: `drift::templateColours` / `drift::replaceTemplateColour` en `src/core/SceneTemplateTools.*` (rellenos,
  trazos, sombras, brillos y paradas de degradado de formas —también las partes de un grupo— y textos; cajas,
  resaltados, subrayados, acentos y tramos de texto; colores de efectos `#rrggbb`/`#rrggbbaa`; y los valores de las
  claves `layer.<id>.color.r/g/b` y `<param>.r/g/b`). Une colores casi iguales (distancia RGB < 14). Fotos y videos
  no cuentan. Funciona con las plantillas ya publicadas (no usa datos nuevos).
- `AppController::templateColours(assetId)` y `replaceTemplateColour(assetId, from, to)` en
  `src/models/SceneTemplates.cpp`: recorren la composición de la plantilla y las composiciones de dentro.
- Prueba: `CoreTest::sceneTemplateColoursAreListedAndReplaced` (`tests/tst_core.cpp`).

## 2. «Instalar todo» de los extras — HECHO (código), falta probar en ventana

(Jorge corrigió: no eran los efectos de Stock sino los **extras**. La descarga de todos los efectos de Stock no se hizo.)

- `AddonManager` (C++): `installAllPlan`, `installAll`, `cancelInstallAll`, propiedad `bulk`, señal `bulkFinished`.
  Cola de dos en dos, de la más chica a la más grande; los fallos se cuentan sin parar el resto. Usa el mismo
  `install()` de siempre (descarga, firma, instalación).
- Antes de empezar: `AddonInstallAllDialog.qml` dice cuántos y cuánto pesa. Botón «Instalar todo (X MB)» en
  Extras (`AddonManagerDialog.qml`) y «Instalar todos los extras (X MB)» en el diálogo de paquetes básicos
  (`AddonStartupDialog.qml`).
- Mientras corre: tarjeta abajo a la izquierda (`AddonBulkStrip.qml`, en `Main.qml`): «Instalando extras: 3 de 12»,
  el extra actual, MB, barra y «Cancelar»; un clic abre Extras. Al terminar, aviso «Listo: se instalaron N extras» o
  «Se instalaron N, M no se pudieron instalar: … · Reintentar», y la barra de tareas parpadea si la ventana está
  de fondo (`window.alert`).
- Cerrar la app con la cola andando: después de las preguntas de guardar de siempre, la ventana se esconde
  (`Addons.continueInBackground()`), queda un ícono en la bandeja con el avance y el menú «Abrir Flip Studio» /
  «Cancelar y salir»; al terminar, notificación de Windows y la app se cierra sola.
- Otra instancia: candado `install-all.lock` en la caché de descargas (`QLockFile`); la segunda no instala lo mismo,
  avisa «Flip Studio todavía está terminando de instalar los extras en segundo plano» y no borra la caché.
  (La app no tiene instancia única: no se trae la ventana escondida al frente.)
- Si se mata el proceso: la cola queda en `QSettings` `addons/installAllPending`; al arrancar, a los 5 s, un aviso
  ofrece «Instalarlos».

## 3. Iniciar sesión en Stock más visible — HECHO (código), falta probar en ventana

- `SignInRequiredDialog.qml`: motivo nuevo `"stock"` («Inicia sesión para usar Stock», todo es gratis).
- `MarketTab.qml`: sin sesión, al abrir Stock sale ese diálogo **una vez por sesión de la app**
  (`SessionFlags.qml`, singleton nuevo); el aviso del panel pasa arriba (antes centrado y en una laptop no se veía).
- `StockPanelCards.qml`: el «Iniciar sesión» de Tendencias abre el mismo diálogo.

## 4. Máscaras de las capas de ajuste al pasar Short ⇄ Video — HECHO (código)

- `src/core/SceneTemplateLayout.cpp` (`mapCanvasMask`, dentro de `mapLayout`): una capa de ajuste suelta (sobre
  todo lo de abajo, no un carril de un clip) mide sus máscaras en el lienzo; al adaptar la plantilla a la otra
  forma, sus máscaras (`mask` y `extraMasks`: centro, tamaño, puntos libres, `pathKeys`, claves x/y/w/h, desenfoque
  del borde y `expand`) se mueven igual que el diseño. Caso: tercios de vidrio (`templates_yp15.py`/`yp16`,
  `GLASS_BLUR`), el desenfoque bajo el vidrio quedaba fuera de lugar.
- Igual en `tools/scene_templates/layoutfit.py` (`fit_doc` → `_map_loose_adjustment_masks`). La copia del checkout
  principal la porta quien coordina.
- Prueba: `EditorStateTest::sceneTemplateLayoutMovesLooseAdjustmentMasks`.

## Compilación y pruebas

- `pwsh tools/precheck.ps1`: OK (traducciones al español hechas en `drift_es.ts`).
- **Ojo:** `lupdate.exe` que vive dentro de un repo (`codigo\Flip\.qtmingw`) no puede escribir archivos (la misma
  trampa que `.e2e-app`). Para este worktree se copió el `bin` de Qt a `E:\FlipStudio\pruebas\qttools-6.10.3\bin`
  y `Flip-032\.qtmingw\6.10.3\mingw_64\bin` es una unión a esa carpeta.
- CI: (ver abajo).
- En ventana: pendiente.
