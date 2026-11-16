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

## 5. Motor para animación líquida / de dibujo animado — HECHO (código), falta probar en ventana

Pedido de Jorge (2026-11-15, yp10): «la animación líquida está fea; si tienes que corregir tu motor hazlo para que nos
quede para próximas animaciones que van a ser así». Lo que había ya servía a medias (Trim Paths, Taper, Wiggle Paths,
claves de trazado, `liquid.gooey`); la yp10 no lo usaba: dibujaba cada cuadro como un polígono (gordo, con bordes
quebrados y salpicaduras en anillos de puntos). Lo nuevo:

- **Transformación suave entre trazados distintos** (`ShapeStyle::smoothMorph`, JSON `smoothMorph`, 0/1): dos claves
  de «Trazado» con distinto número de puntos o de contornos se mezclan igual: cada contorno se remuestrea por su
  largo, se elige el inicio y el sentido más cercanos y se dibuja de vuelta con curvas suaves (Catmull-Rom). Un
  contorno sin pareja nace del punto más cercano del otro (una gota que se separa de una mancha).
  `drift::morphSvgPathsResampled` (`src/core/ShapePathEdit.*`); `shapePathAt` lo usa solo con el interruptor encendido
  y solo cuando la mezcla punto a punto no sirve (los proyectos de antes no cambian). Interruptor en el inspector de
  la forma, bajo «Animar el trazado»: «Transformación suave entre trazados distintos».
- **Puntas redondas en un trazo con Taper** (`SkiaShapePainter.cpp` `profiledStroke`): con remate redondo (el de
  siempre) cada punta de un trazo abierto se cierra con media circunferencia de su ancho: la cabeza redonda de una
  pincelada. Antes terminaba plano. Además el relleno del trazo es «non-zero» con los lados de un anillo en sentidos
  opuestos: un trazo grueso en una curva cerrada se doblaba sobre sí mismo y el par-impar le abría un hueco.
- **Wiggle Paths en un trazado abierto** se une por los puntos medios (antes una polilínea quebrada).
- **Short ⇄ Video:** el ajuste de la plantilla escala también el ancho de los trazos, desplazamientos y desenfoques de
  las capas de pintura de una forma y los px de los operadores (Wiggle, Offset, Zig Zag, Repetidor), con sus claves
  (`scaleShapeStyle` en `SceneTemplateLayout.cpp`; igual en `tools/scene_templates/layoutfit.py` `_scale_shape`).
  Antes un trazo quedaba con su ancho completo en un Short mientras el dibujo se achicaba.
- Pruebas: `CoreTest::shapePathSmoothMorph`, `SkiaTest::taperedStrokeRoundCaps`, y
  `EditorStateTest::sceneTemplateLayoutScalesAndCovers` (trazo, clave de ancho y wiggle a la mitad).
- Plantillas: `tools/scene_templates/liquid.py` (checkout principal): `brush` (trazo que se dibuja solo: Trim +
  Taper + punta redonda + Wiggle), `rays`, `splash` (gotas que salen estiradas por su velocidad) y `morph_keys`
  (manchas con claves cada dos cuadros y transformación suave). Las yp10 piden la 0.32 (`publish.py`).
- **Goteo** (2026-11-15, segunda vuelta; Jorge: «viene como chorreando líquido, el nuestro en algunos logos no lo
  hace»): operador nuevo de forma (`dripLength`, `dripCount`, `dripWidth`, `dripFall`, `dripSeed`, todos con claves).
  De la parte de abajo de cada contorno cuelgan chorros de líquido espeso con una gota redonda en la punta; «Caída de
  gotas» suelta las gotas y las deja caer. Se une al cuerpo (unión de trazados) y con el efecto Líquido (`liquid.gooey`)
  los cuellos se funden. `drippedPath` en `SkiaShapePainter.cpp` (después de Zig Zag y antes de Wiggle); sección
  «Goteo» en el inspector; el ajuste Short/Video escala sus px. Prueba `SkiaTest::dripHangsBelowTheShape`.
  **Trampa:** un óvalo hecho con `QPainterPath` no queda marcado como cerrado al medirlo: el goteo mide todo contorno
  como cerrado.
- Queda para otra vez: animar la curvatura del camino de un texto (`pathSvg`) y la escala X/Y separada de un texto.

## 6. Arreglos de CI

- `AddonManager.cpp` usaba `QApplication`/`QSystemTrayIcon` y las pruebas no enlazan QtWidgets: la bandeja se compila
  solo en la app (`FLIP_ADDON_TRAY`, definido en `CMakeLists.txt` para `drift`).
- La prueba de Colores comparaba un canal de `QColor` (float) con un double exacto: ahora con tolerancia.
- **Trampa nueva:** vcpkg se clonaba sin fijar y su actualización de zlib 1.4 (2026-11-13) dejó a Skia enlazando un
  `zs.lib` que no existe (todo Windows en rojo al enlazar). `package.yml` y `msstore.yml` fijan vcpkg en
  `fe8e78fac7` (el commit anterior). Para actualizar vcpkg, cambiar ese commit a propósito.
- Compilación con todo lo de arriba: run 43738406085 (Windows) en verde; Tests (Linux) run 43733676879 en verde.
  Portable en `E:\FlipStudio\pruebas\FlipStudio-0.32-liquido` (con ella se renderizó la yp10 nueva).

## Compilación y pruebas

- `pwsh tools/precheck.ps1`: OK (traducciones al español hechas en `drift_es.ts`).
- **Ojo:** `lupdate.exe` que vive dentro de un repo (`codigo\Flip\.qtmingw`) no puede escribir archivos (la misma
  trampa que `.e2e-app`). Para este worktree se copió el `bin` de Qt a `E:\FlipStudio\pruebas\qttools-6.10.3\bin`
  y `Flip-032\.qtmingw\6.10.3\mingw_64\bin` es una unión a esa carpeta.
- CI: (ver abajo).
- En ventana: pendiente.

## 7. Motor VFX (A–E) — rama `flip/v0.32-vfx` (worktree `codigo\Flip-032-vfx`), para unir a `flip/v0.32`

Lo que pedía `docs/plan-vfx.md` (checkout principal) para los efectos dibujados a mano tipo RTFX. Todo es opcional en
el JSON: si falta, se dibuja como antes.

- **A. Esquinas en la transformación suave** (`ShapeStyle::morphCorners`, grados; 0 = todo redondo como antes). Con
  la transformación suave encendida, los vértices donde el trazado gira más que ese ángulo (una cúspide: punta de
  llama, chispa) quedan en punta; si las dos claves tienen el mismo número de esquinas, se emparejan en orden y cada
  tramo entre esquinas se remuestrea por separado (la punta viaja a su pareja). `drift::pathContourCorners`,
  `SmoothMorphOptions` en `src/core/ShapePathEdit.*`. Inspector › Trazado: «Conservar las esquinas en punta» (40°).
- **B. Posterizar tiempo** (`Clip::posterizeFps`, JSON `posterizeFps`; 0 = apagado). Todo el clip (transformación,
  claves, trazado, temblor, efectos, el cuadro del video, el padre que sigue y el desenfoque de movimiento) se calcula
  a esos cuadros por segundo y se mantiene entre medio, como «Posterize Time» de AE. `Clip::posterizedTimelineUs`,
  aplicado en `buildGpuLayer`, `clipGeometryAt` y el padre (`FrameCompositor.cpp`). Inspector › Movimiento (donde
  está «Desenfoque de movimiento»): «Posterizar tiempo» + fps (12 por defecto). `setClipPosterizeFps`.
- **C. Tono interior** (capa de relleno con `innerTone`, `toneScale` %, `toneRotation` °, `toneInvert`). Pinta, con
  borde duro y solo dentro de la forma, donde no llega una copia del contorno movida por su desplazamiento (o donde sí
  llega, invertido): la panza gris del humo, el lado oscuro del líquido. Sigue al trazado animado. «Añadir capa ›
  Tono interior» (desplazamiento Y −12, color más oscuro). `drawInnerTone` en `SkiaShapePainter.cpp`.
- **D. Nacer y morir por dentro.** (1) `morphFromCentre`: en la transformación suave, un contorno que solo tiene una
  clave (un hueco, una gota) nace/muere en su propio centro. Inspector › Trazado: «Los contornos nuevos crecen desde
  su centro». (2) Operador **Romperse** (`erodeAmount` 0–100 %, `erodeSize` px, `erodeSeed`, `erodeAngle`,
  `erodeStretch`): huecos en una cuadrícula con azar que se abren desde su centro, cada uno a su momento, hasta que no
  queda nada (100 % = vacío); con Estirar > 1 son tiras a lo largo del ángulo (el fuego que se corta en tiras).
  Sección nueva «Romperse» en el inspector. `erodedPath`.
- **E. A saltos.** `wiggleStepRate` (dibujos por segundo; 0 = el temblor suave de siempre): un sorteo nuevo cada
  dibujo, quieto entre medio. Zig Zag: `zigzagJitter` % (cada punta con su tamaño y corrida a lo largo), `zigzagSeed`,
  `zigzagStepRate` (redibujo por segundo): la electricidad. En las secciones de Wiggle y Zig Zag.
- **H. Comprobado.** Merge Paths solo combinaba los contornos de un mismo trazado, y «Combinar» de la 0.30 hornea las
  partes en un trazado fijo. Ahora un **grupo** tiene `ShapePart::mergeMode` (JSON `merge`): sus partes se combinan
  en vivo (la de abajo es la base y pinta el resultado; las de arriba se suman, restan…), siguen animadas.
  `mergeGroupNode` en `SkiaShapePainter.cpp`; inspector de un grupo: «Combinar las partes del grupo». El Brillo
  exterior (`layer.outer_glow`) se compone **debajo** de la capa (`composite.frag`): con la forma opaca no se ve por
  dentro; sí asoma si la capa es semitransparente (como en AE). No se tocó.
- **Short ⇄ Video:** `erodeSize` se escala con el diseño (`scaleShapeStyle`).
- **Plantillas:** `tools/scene_templates/vfx.py` (en esta rama; el `liquid.py` del checkout principal no se tocó):
  `smooth_path` con esquinas (índices o `corner_angle`), `smooth_morph`, `posterize`, `inner_tone`, `break_apart`,
  `stepped_wiggle`, `jagged_zigzag`, `MERGE`. `tools/scene_templates/vfx_demo.py` arma y renderiza los videos de
  prueba en `E:\FlipStudio\tienda\vfx-estudio\motor\`. Lo que use esto pide la versión que traiga el motor.
- **Pruebas:** `CoreTest::shapePathSmoothMorphKeepsCornersAndGrowsFromCentre`, `CoreTest::cartoonVfxFieldsRoundTrip`
  (todos los campos, posterizar, guardar/abrir), `SkiaTest::shapeCartoonVfxOperators` (tono, romperse, saltos) y
  `SkiaTest::shapeGroupMergePaths`.
- **Falta:** verlo en ventana (paneles nuevos) y que Jorge vea los videos; el MCP (`set_shape`) no lista los campos
  nuevos (presupuesto del catálogo), se pueden poner por JSON de proyecto.
