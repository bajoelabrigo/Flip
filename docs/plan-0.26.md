# Plan 0.26 — Motion graphics como After Effects (todo en una versión)

Pedido de Jorge (2026-10-28): tras la comparación con After Effects, hacer **las cuatro etapas en una sola
versión** («si lo hacemos en partes se me acaba la suscripción»). Misma metodología de siempre: cada cambio
probado al hacerlo, el trabajo a medias subido a la rama, una compilación de CI al final y **todo probado en
ventana** antes de publicar.
Rama: `flip/v0.26.0`.

Si otro asistente sigue este trabajo: este archivo dice qué está hecho (`[x]`), a medias (`[~]`) y qué falta
(`[ ]`), y dónde vive cada cosa.

## Etapa A — Emparentar capas, Nulo y desenfoque de movimiento
- [x] A1. **Emparentar** (columna «Primario» / látigo de AE): `Clip::parentId` + pose de reposo del padre al
      enlazar (`Clip::parentRest`). La capa hija sigue el movimiento, giro y escala del padre **desde** que se enlaza
      (como AE, que convierte los valores al espacio del padre: aquí se guarda el reposo y la hija conserva sus
      números). Cadenas de padres, sin ciclos. La opacidad no se hereda (como AE).
- [x] A2. **Objeto nulo**: capa de forma que no se dibuja (`Clip::isNull`), solo su marco en la vista previa.
- [x] A3. **Desenfoque de movimiento** por capa (interruptor) + ángulo de obturación y muestras del proyecto.
- Dónde: `Clip::parentId/parentRest/nullObject/motionBlur`, `Project::motionBlurShutterDeg/Samples` (JSON solo si
  no son los de siempre). Matemática en `engine/TransformLayer.cpp` (`clipWorldPose`, `clipParentMatrix`,
  `setClipParentKeepingPlace`, `bakeMatrixIntoClipLayout`: desenlazar o cambiar de padre no mueve la capa). El
  compositor suma el padre en `buildGpuScene` (`applyClipParent`) y salta los nulos; el desenfoque arma muestras en
  `addMotionBlurSamples` (FrameCompositor) y las promedia en `GpuCompositor` (`motionSamples`, suma a 1/N en una
  capa aparte y la pone en su lugar). Interfaz: «+» › Objeto nulo; clic derecho › Primario / Desenfoque de
  movimiento; inspector › Fusión › `MotionLinkSection.qml` (Primario, interruptor, obturación y muestras).
  MCP: `add_null_object`, `set_parent`, `set_motion_blur`.
- Limitaciones: el padre pasa solo 2D (no la inclinación 3D); un clip con pin de esquinas no se desenfoca; el marco
  de la vista previa de una capa hija con anclaje fuera del centro y giro no suma el corrimiento del anclaje.

## Etapa B — Capas de forma como AE
- [x] B1. Pluma: dibujar el trazado en la vista previa; trazado animable (claves de trazado, transformar una forma
      en otra).
- [x] B2. Recortar trazados (inicio, fin, desplazamiento), animables.
- [x] B3. Repetidor (copias, desplazamiento, posición/escala/rotación por copia, opacidad inicio/fin).
- [~] B4. Sacudir trazado hecho (suave, en el tiempo y a lo largo del borde). Redondear esquinas ya existía.
      Desplazar trazado y retorcer: no.
- Dónde: `ShapeStyle` (campos `trim*`, `repeat*`, `wiggle*`, todos en `kKnobs`: así tienen rombo, filas y
  curvas solos; JSON solo si no son los de siempre), pintor `engine/SkiaShapePainter.cpp` (`wiggledPath`,
  `trimmedPath`, `repeaterMatrix`, margen en `makeShapePainter`). Trazado: `core/ShapePathEdit.*` (vértices ↔ SVG,
  `morphSvgPaths`), clave `path` = índice en `ShapeStyle::pathShapes` (`shapePathAt`, `setShapePathAt`,
  `setShapePathAnimated`). Pluma y edición: `preview/PenToolOverlay.qml` (`EditorState.preview.penMode` /
  `pathEditMode`), «+» › Forma con la pluma, inspector de forma › Trazado / Recortar trazados / Repetidor /
  Sacudir trazado. Controlador: `addPenShape`, `shapePathState`, `setShapePathPoints`, `setShapePathAnimated`.

## Etapa C — Comportamientos (expresiones) y mates de seguimiento
- [x] C1. Comportamientos por propiedad: Repetir (`loopOut` ciclo / ida y vuelta / sumando / continuar), Velocidad
      constante (`time * n`) y Temblor (`wiggle`), que se suman en ese orden. Viven en la pista de claves misma
      (`TrackBehavior` en `core/Keyframe.h`, `KeyframeTrack::evaluateAt`; `evaluateKeys` = solo las claves), así sirven
      para **todas** las propiedades animables (transformación, opacidad, formas, efectos, texto, audio). JSON
      `behavior` en `keyframesToJson`. Interfaz: menú «…» de la fila › Comportamiento… (`PropertyBehaviorDialog.qml`),
      la fila muestra «≈». Controlador: `propertyBehavior` / `setPropertyBehavior` (sin claves pone una en el 0).
      **Falta:** enlazar una propiedad a otra (el látigo de expresiones de AE).
- [x] C2. Mate de seguimiento: alfa / alfa invertido / luminancia / luminancia invertida, de cualquier clip
      (`Clip::matteMode/matteClipId`, JSON `matte`). La capa mate no se dibuja sola (como AE). Compositor: el clip se
      dibuja aparte, se recorta con el mate (`kTrackMatteFragShader`, `applyTrackMatte`) y se pone en su lugar; comparte
      ese camino con el desenfoque de movimiento. Interfaz: inspector › Fusión › Mate de seguimiento (modo y capa;
      sin capa elegida toma la más cercana de arriba). MCP `set_track_matte`.

## Etapa D — Curvas, tiempo, vista previa y 3D
- [x] D1. Velocidad del fotograma clave (AE): velocidad e influencia % de entrada y salida, «Continua»
      (`KeyframeVelocityDialog.qml` desde el menú de la clave; `keyVelocity` / `setKeyVelocity`). Auto-orientar al
      trazado (`Clip::autoOrient`, `autoOrientDegrees`, sumado al giro en compositor, padres y vista previa; clic
      derecho › Orientar según el trazado).
- [x] D2. Reasignación de tiempo (`Clip::timeRemap`, segundos del material desde srcIn; manda sobre velocidad, curvas y
      reversa en `timelineToSourceUs`; el audio la sigue en `AudioMixer`). Clic derecho › Reasignación de tiempo pone
      una clave en cada punta con lo que ya se ve; la fila «Reasignación de tiempo» sale con las demás.
- [x] D3. Vista previa: ½ y ¼ y el fondo a cuadros ya existían; nuevas las **zonas seguras** (opciones de la vista
      previa; `EditorState.preview.safeZones`).
- [ ] D4. Luces 3D: **no entra en la 0.26** (necesita un tipo de capa nuevo y sombreado por capa; se deja para
      después).

## Etapa E — Barra de herramientas y Preferencias (Jorge, 2026-10-28)
- [x] E1. **Barra de herramientas sobre la vista previa** (como el panel Herramientas de AE,
      `preview/PreviewToolbar.qml`): Selección (V), Mano (H), Zoom (Z; Alt+clic aleja), Punto de anclaje (Y: se arrastra y
      la capa no se mueve, `setAnchorKeepingPlace`), Formas (Mayús+Q: rectángulo, elipse, estrella, polígono; Mayús =
      cuadrado, Alt = desde el centro; `addDrawnShape`), Pluma (P), Texto (Ctrl+T: clic y escribir, `addTextAtPoint`),
      Roto (abre Video › Eliminar fondo, `openInspectorPage`) y Cámara 3D (Mayús+C). A la derecha, Relleno / Trazo /
      grosor para formas y pluma (clic derecho = ninguno). Estado en `EditorState.preview.tool` (`PreviewController`);
      la capa de dibujo es `preview/PreviewToolOverlay.qml`; Mano y Zoom en `PreviewPanel.qml`. Esc vuelve a Selección.
      G, Q y C ya eran guías, borrar y cuchilla: por eso P, Mayús+Q y Mayús+C (todo se puede cambiar en Atajos).
- [x] E2. **Preferencias como AE** (Edición › Preferencias…, `SettingsDialog.qml`): lista de páginas a la izquierda
      (General, Apariencia e idioma, Capas nuevas, Línea de tiempo y claves, Herramientas de la vista previa, Vista
      previa y rendimiento, Audio, Guardado y deshacer, Atajos de teclado, Cuenta y privacidad, IA en la nube). En el
      celular sigue la lista larga de siempre. Nuevas preferencias reales (`PreferencesController::editorDefaults`,
      claves `defaults/*` en el registro): niveles de deshacer, copia de recuperación cada N s, duración de fotos /
      formas / sólidos y de textos al ponerlos (`drift::defaultStillDurationUs`, `defaultTextDurationUs`),
      interpolación de las claves nuevas (`newKeyInterpolationRef`, en `writeKeyframeValue`), mostrar la barra,
      zonas seguras al iniciar y los colores de la barra (se recuerdan). Color y modo del tema también aquí; los atajos
      se editan dentro de la página (`ShortcutsTab`). «Restablecer los valores de edición».

## Etapa F — Motion Tools y atajos de AE (Jorge, 2026-10-28, tarde)
- [x] F1. **Invertir fotogramas clave** (Time-Reverse de AE) y **Estirar…** por porcentaje, en el menú de la clave
      (`reverseKeyframes`, `stretchKeyframes`). Estirar a mano ya existía desde la 0.25: Alt + arrastrar la primera o
      la última clave elegida, como en AE.
- [x] F2. **Mayús+A / P / R / T / S**: abren solo Punto de anclaje / Posición / Rotación / Opacidad / Escala en las
      pistas elegidas (otra vez: cierran). `showOnlyKeyframeGroup`, filtro `m_keyframeRowsOnlyGroup` en
      `trackKeyframeRows`. Seleccionar a la izquierda pasó a Alt+A y la orientación del gizmo a Alt+T.
- [x] F3. **Panel Motion Tools** (pestaña de la barra derecha del inspector, `properties/MotionToolsPanel.qml`):
      suavizar entrada/salida con influencia, Lineal, Mantener (sobre las claves elegidas, que la línea de tiempo
      publica en `EditorState.pickedKeyframes`); cuadrícula 3×3 del anclaje (la del «…» de la fila se quitó, Jorge);
      Elástico y Rebote (`TrackBehavior::settle`, en `Keyframe.h`); Clonar (las claves al cabezal); Secuencia con
      desfase y paso, de arriba abajo o al revés; Extraer (desagrupar), Unir (agrupar), Añadir nulo (en el centro de
      la selección, que pasa a seguirlo); Convertir en forma (letras de un texto o una forma en trazado editable);
      Centrar (en vez de «Remove artboard», que es de Illustrator).

## Etapa G — Lo que faltaba frente a AE (Jorge, 2026-10-28, noche: «todo esto debe salir en esta versión»)
Orden de trabajo (de más usado a más pesado). Cada punto dice qué versión práctica se hace.
- [x] G1. Fondo a cuadros a pedido (opciones de la vista previa › «Transparency grid»): la vista previa sin el fondo
      del proyecto (`PlaybackEngine::transparencyGrid` → `RenderOptions::transparentBackground`).
- [x] G2. Látigo: en el clip elegido de la línea de tiempo, un espiral que se arrastra a otro clip = Primario; el clip
      muestra «↳ nombre del primario» (`TimelineClipItem.qml`, icono `pick-whip.svg`).
- [x] G3. Estilos de capa en cualquier capa (categoría «Layer Styles»; botones en Fusión): Sombra paralela,
      Resplandor exterior, Trazo, Bisel y relieve, Superposición de color (`effects/layer_*`). Margen para que no se
      corten: `"padding"` en el `effect.json` (`applyEffectPadding` en `FrameCompositor.cpp`, la textura crece en
      `GpuCompositor.cpp`).
- [x] G4. Formas: unir trazados, desplazar trazado, zigzag, retorcer (`ShapeStyle` + `SkiaShapePainter`), trazo con
      degradado (ya existía) y «Formas en esta capa» (`AppController::addShapeToLayer`). Claves en el esquema de MCP.
- [x] G5. Efectos con nombre de AE: Fractal Noise, Particle World, Shatter, Turbulent Displace, Gradient Ramp,
      Radio Waves (`effects/ae_*`, categoría «Generate & Simulate»).
- [x] G6. Expresiones en JavaScript (`src/engine/ExpressionEngine.*`, un QJSEngine por hilo): value, time, wiggle(),
      Math, layer("Nombre") / thisComp.layer("Nombre").transform…; `loopOut("cycle")` solo se convierte en el bucle
      del comportamiento. Editor con error en vivo en el diálogo de Comportamiento.
- [x] G7. Bosquejo de movimiento: herramienta de la barra de la vista previa (`applyMotionSketch`).
- [x] G8. Texto sobre un trazado: Texto › «Text on a path» con 6 trazados listos o el contorno de una capa de forma
      (`useShapeAsTextPath`), y «Path offset» animable (`TextStyle::pathSvg/pathOffset`, `Bend::contour` en
      `SkiaTextPainter.cpp`). Una sola línea, como la curva. Los animadores 3D por letra ya existían («3D turn X/Y»).
- [x] G9. Editor de curvas: con varios clips elegidos, las curvas de los otros salen punteadas y un clic en su nombre
      los pasa a editar (`KeyframeGraph.qml` › `otherLayers`). Separar dimensiones de la escala: ya existía.
- [x] G10. Vista previa en RAM (Vista › «RAM Preview», tecla 0 del teclado numérico): el área de trabajo (o todo) a
      memoria, hasta 3 GB, y se reproduce sola; barra verde en la regla; cualquier edición la vacía
      (`PlaybackEngine::buildRamPreview`). Región de interés: herramienta de la barra; las capas simples que quedan
      fuera no se decodifican (`RenderOptions::regionOfInterest`) y fuera del recuadro se tapa.
- [x] G11. Pines de marioneta: efecto `ae.puppet` (hasta 8 pines, rigidez) y herramienta de la barra: clic pone un pin,
      arrastrarlo lo mueve con clave en el cabezal (`addPuppetPin`, `movePuppetPin`).
- [x] G12. Gráficos esenciales: dentro de una composición, Fusión › «Add to Essential Graphics» (texto, color,
      tamaño, posición, giro, opacidad); fuera, la composición muestra esos controles (`Clip::essentialProps`,
      `essentialControls`, `setEssentialValue`; una propiedad con claves se desplaza entera).
- **Probado en ventana (build d2c0493, 2026-10-28, `pruebas\FlipStudio-0.26-prueba-c`):** RAM preview (0 numérico,
  barra verde, arranca sola), región de interés, texto sobre trazado (Onda, Seguir la forma con el Círculo,
  desplazamiento con clave), curvas de otra capa punteadas, estilos de capa (sombra, resplandor y trazo salen del
  recuadro), bosquejo de movimiento, Gráficos esenciales (texto cambiado desde fuera de la composición).
- **Arreglado tras esa prueba (build siguiente):** la Marioneta no cargaba (`effect.json` sin `pipeline`) y la imagen
  doblada se cortaba en el recuadro (margen + `u_padX/u_padY`); la vista previa en RAM ahora se repite en su tramo
  hasta pausar; el nombre de otra capa en el editor de curvas la elige y abre sus filas (antes el gráfico se perdía).
- **Falta:** volver a mirar en ventana esos tres arreglos, el látigo, expresiones, fondo a cuadros y operadores de
  forma; luego publicar.
- **Trampa:** `/tmp/chk.sh` no tenía g++ en el PATH y no comprobaba nada (salida vacía = «bien»): ahora exporta
  `.qtmingw/Tools/mingw1310_64/bin` y define `QT_NO_FOREACH`. Un efecto GPU sin `"pipeline"` se salta al cargar
  («pipeline has no passes»), sin aviso en la interfaz.

## Dónde vive cada cosa
- Matriz de los padres: `src/engine/TransformLayer.*` (`transformParentsAt` = capas de transformación por pista;
  ahora también el padre de cada clip). El compositor la aplica en `buildGpuScene` (`applyParent`) y la vista
  previa dibuja los controles a través de ella (`PreviewController::clipsAtPlayhead`).

## Cómo se probó / qué falta probar
- Cada archivo de C++ tocado pasa `g++ -fsyntax-only` en local con las cabeceras reales (Qt 6.10.3 de `.qtmingw`,
  FFmpeg n7.1, ONNX Runtime 1.27.0 y Skia 148 de vcpkg, bajadas al scratchpad); las QML pasan `qmlformat`.
  `ShapePathEdit` y `TrackBehavior` se probaron de verdad con programas pequeños enlazados al Qt local.
- Pruebas nuevas: `tst_engine` (emparentar, ciclos, desenlazar sin salto, nulo, desenfoque, mate, guardado),
  `tst_skia` (recortar, repetidor, sacudir), `tst_core` (trazado ↔ SVG, transformar, claves de trazado,
  comportamientos, reasignación de tiempo y auto-orientar). Las de GPU se saltan en CI: se miran en ventana.
- Traducciones: catálogos regenerados (119 textos nuevos) y español completo (7135/7135), `lupdate` estable.
- **Falta:** CI en verde, y **probar todo en ventana** (portable en `pruebas\FlipStudio-0.26-prueba`).
