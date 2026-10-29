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
- [x] D4. Luces 3D (Jorge: «haz lo de las luces de una vez»): capas de luz Puntual, Foco, Paralela y Ambiente
      (`Clip::light`, un clip nulo que no pinta; Motion Tools y el menú de pista nueva). Las capas 3D con «Acepta
      luces» (`Clip::acceptsLights`) se sombrean por píxel en el espacio del mundo (`applyLighting` en
      `GpuCompositor.cpp`: ambiente + difusa + brillo, caída y cono suaves; hasta 8 luces). Ajustes en Vincular y
      movimiento: tipo, color, intensidad, ángulo y difuminado del cono, radio y distancia de caída.

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
- **Probado en ventana (build 381cad8, `pruebas\FlipStudio-0.26-prueba-d`):** los tres arreglos (Marioneta dobla fuera
  del recuadro, RAM en bucle, cambio de capa en el editor de curvas), expresión `time * 90` en Rotación (120,1° a
  1,33 s, la fila muestra «≈»), látigo (↳ Círculo sin salto), zigzag, Ondas de radio y fondo a cuadros.
- **Probado en ventana (build c4d44b2, `pruebas\FlipStudio-0.26-prueba-e`):** las cuatro luces desde Motion Tools
  (Puntual ilumina según dónde se arrastre, Foco con cono de 90° y de 30°, Paralela oscurece la capa girada, Ambiente
  pareja), color/intensidad/cono/atenuación en Fusión, «Acepta luces» apagado devuelve el color original; Mano,
  Punto de anclaje y la ventana de Velocidad del fotograma clave.
- **Arreglado tras esa prueba:** la luz nueva cubre toda la composición desde el 0 (antes empezaba en el cabezal y
  alargaba el proyecto); los Estilos de capa no salen en luces ni nulos; el recuadro (`quad`) de la vista previa suma
  el corrimiento del anclaje (`anchorShift`), así el Punto de anclaje y los pines caen donde se suelta en una capa
  girada con el anclaje fuera del centro.
- **Ronda de Jorge (2026-10-28, noche) y prueba en ventana (build 2f60f77, `pruebas\FlipStudio-0.26-prueba-g`):**
  - Cronómetro encendido = clave donde cambie (`writeKeyframeValue`): arrastrar en la vista previa a 2,5 s dejó claves
    nuevas en X e Y sin tocar las demás.
  - **Separar dimensiones** (menú «…» de Posición, se guarda en `editor/positionLinked`): filas Posición X / Posición Y
    con su cronómetro; un rombo en X no pone clave en Y. Los tiradores del trazado sueltan X/Y solo durante el
    arrastre (`setPositionLinkedForDrag`).
  - Texto sobre un trazado **enlazado** a la capa de forma (`TextStyle::pathShapeId`, `refreshTextPathsFromShapes` en
    `finishEdit`): agrandar el círculo agrandó el anillo de letras; elegir otra forma en la lista la aplica al momento
    (lista no probada con clics simulados). Un contorno que termina donde empieza da vueltas (offset 100 = igual a 0).
    Arreglado en la prueba: el contorno no sumaba el anclaje ni el giro de la forma (`shapeOutlineInTextBox`).
  - **Rebote** como pelota (botes al 0,6 de la velocidad, gravedad de la caída): primer bote 97 px, segundo 35 px.
    **Elástico** a 0,12: pasa el piso 23 px y se calma en ~0,8 s.
  - Motion Tools en ventana: cuadrícula del anclaje, Secuencia (0 / 5 / 10 fotogramas), Unir y Extraer, Convertir en
    forma (texto), Suavizar / Lineal / Mantener sobre claves elegidas y Clonar (al primer clic). Arreglados en la
    prueba: **Centrar** se saltaba sin aviso las capas animadas (ahora mueve toda la animación y cuenta el anclaje);
    **Añadir nulo** empezaba en el cabezal (alargaba el proyecto), quedaba fuera del centro con el anclaje movido y
    dejaba dos pasos de deshacer.
  - El recuadro de selección de claves sube sobre las pistas de abajo mientras se dibuja.
- **Falta antes de publicar:** lo de etapas anteriores sin ventana (editar puntos, reasignación de tiempo,
  Mayús+A/P/R/T/S, invertir/estirar claves: Mayús no llega con mensajes simulados, lo prueba Jorge).
- **Trampa:** `/tmp/chk.sh` no tenía g++ en el PATH y no comprobaba nada (salida vacía = «bien»): ahora exporta
  `.qtmingw/Tools/mingw1310_64/bin` y define `QT_NO_FOREACH`. Un efecto GPU sin `"pipeline"` se salta al cargar
  («pipeline has no passes»), sin aviso en la interfaz.
- **Trampa (2026-10-29):** el build `a3d01` no arrancaba: `472fe` dejó `onEntered` en las tarjetas de Medios (no son
  `DropArea`). Ni el CI ni `qmllint` lo ven; quitado en `927ab`. Abrir cada build en ventana primero.

- **Forma como máscara de cualquier clip (Jorge, 2026-10-29: «que tenga las 2 opciones, que quede pegada o que la
  siga… quiero animar textos que aparecen de la nada»), commit `3b7a7`, sin probar en ventana:** clic derecho en una
  forma, texto o foto › «Usar como máscara fija de ▸» / «Usar como máscara pegada a ▸» (lista de clips, primero los
  que se solapan). Por dentro es el mate alfa (`AppController::useAsMatteFor`, `matteTargetOptions`): **fija** = la
  forma queda en la pantalla y el clip pasa a través; **pegada** = la forma se emparenta al clip
  (`setClipParentKeepingPlace`). Si la forma termina antes, se alarga (si su pista tiene lugar); si empieza después,
  avisa. En Fusión › Mate de seguimiento, el interruptor «La máscara se mueve con esta capa» cambia entre las dos.
  Prueba `EditorStateTest::shapeAsFixedOrStuckMask`. **Probar en ventana:** texto que entra deslizándose por debajo
  de un rectángulo fijo (aparece de la nada) y el mismo con la máscara pegada.

- **Ronda de Jorge (2026-10-29), commit `a3d01`, sin probar en ventana todavía (build 40844216565):**
  - **Mover un texto animado «lo hacía desaparecer»:** reproducido en ventana (`pruebas\mate-texto\texto-forma.flip`,
    cabezal en 15f). El tirador recto de la clave del 0 se dibuja a un tercio del trazado, justo bajo el texto, y se
    llevaba el clic: el texto no se movía y la curva sí (con un arrastre largo el texto salía de la pantalla). Ahora
    un tirador recto o el rombo de otra clave que caen sobre la capa dejan pasar el clic (`MotionPathOverlay.overLayer`).
  - **Reglas como AE** (Ver › Reglas, Ctrl+R; `PreviewRulers.qml`, `PreviewController::rulersVisible`): marcas en px
    del proyecto que siguen el zoom, marca del puntero, guías que se arrastran desde la regla (conjunto propio
    «Guías de las reglas», `AppController::rulerGuideSet`), se mueven arrastrándolas y se quitan soltándolas sobre
    la regla o fuera del cuadro; Mayús redondea a 10 px.
  - **Pista vacía se borra** al borrar su último clip (`deleteSelectedClip`), con sus carriles; queda siempre una
    pista de video. Y si se borra la forma que hacía de mate, el clip vuelve a verse entero.

- **Ronda de Jorge (2026-10-29, mañana), sobre el portable `prueba-h`:**
  - [x] El imán del cabezal era débil: arrastrando la cabeza solo se pegaba a claves (8 px), y en la regla el imán
        general tenía como objetivo la posición del propio cabezal (se quedaba pegado donde estaba). Ahora
        `snapPlayheadToKeys` suma bordes de clips, marcadores y el área de trabajo (con el imán encendido), a 14 px.
  - [x] El tirador del final temblaba bajo la bolita de la transición: la zona del mouse estaba atada al ancho del
        tirador, que se adelgaza al pasar el mouse (entraba/salía en bucle). Zona fija en los dos tiradores.
  - [x] Elegir una animación (Entrada/Salida/Combinada) devolvía el inspector a Video › Básico, y al volver se
        abría en Entrada: `onSelectionChanged` volvía a correr `syncAdjustmentTab` con el mismo clip. Solo corre si
        cambia el clip; la pestaña Entrada/Salida/Combinada se recuerda (`inspectorUi.clipAnimTab`). La Salida en
        la segunda mitad de una foto cortada **sí** se aplica (probado por MCP y con clics); el salto de panel es lo
        que parecía «no funciona».
  - [x] Claves que no se crean al arrastrar la foto, y «claves pegadas» (Jorge quiere: animar 0→1 s, quieta, y
        otra animación de 3 a 4 s). Reproducido en `prueba-h`: con una clave «quieta» puesta con ◆ en 2,0 s, arrastrar
        la foto en 2,4 s **movía la clave de 2,0 s** (X 289 en 2,0 y ninguna en 2,4). El punto de esa clave cae bajo la
        capa; al apretar, el punto se llevaba el clic y además llevaba el cabezal a su clave
        (`MotionPathOverlay` › `dotMouse.onPressed`). Es lo que `a3d01` ya arregla (un punto de otra clave bajo la
        capa deja pasar el clic). **Probar en ventana con el build nuevo:** ◆ en 2,0 s, arrastrar en 2,4 s → clave
        nueva en 2,4 y quieta entre 1,5 y 2,0.
  - [x] El trazado del movimiento quedaba congelado mientras se arrastraba la capa (sin la clave nueva) y se rehacía
        al soltar: ahora se rehace en vivo con `clipPropertiesPreviewed` (una vez por fotograma).
  - [x] Imán en la vista previa entre capas (Jorge): además del lienzo y las guías, los bordes y centros de las otras
        capas que se ven en el cabezal (`PreviewController::appendLayerSnapTargets`, en mover y en cambiar de tamaño;
        sin las giradas, los nulos, los grupos ni con cámara). Ctrl lo apaga, como antes.
- **Probado en ventana (build 548e6, `pruebas\FlipStudio-0.26-prueba-j`, 2026-10-29):** arrancar sin errores; foto
  con clave en 0 y arrastrar desde encima de su rombo en el fotograma 20 → clave nueva en 0,667 (antes movía la
  clave del 0); ◆ en 1,5 s y arrastrar en 2,0 s → claves 0 / 0,667 / 1,5 (quieta) / 2,0, y en 1,1 s la foto queda
  quieta; elegir Fundido en Salida → se aplica y el panel sigue en Animación › Salida; imán entre capas → el borde
  izquierdo de la foto se pegó al del texto (X 837 = 836,6). **Falta en ventana:** reglas (Ctrl+R) y guías,
  máscara fija/pegada, pista vacía que se borra, tirador que ya no tiembla (el hover no se simula bien) y el trazado
  en vivo (se vio en pie durante el arrastre).
- **Trampa (otra vez):** restaurar el registro después de que un portable usó la cuenta cerró la sesión de Google de
  Jorge (el token renovado se perdió y el viejo ya estaba gastado). Antes de restaurar: exportar
  `HKCU\Software\Flip Studio\Flip Studio\account`, restaurar y volver a importar esa clave.


## Etapa H — Expresiones guardadas y Squash & Stretch (Jorge, 2026-10-29)
- [x] H1. **Expresiones como AE:** el diálogo Comportamiento… tiene «Aplicar a» (Posición, Posición X/Y, Escala,
      Ancho, Alto, Rotación, Opacidad, Punto de anclaje; Volumen y Panorama en audio; y las demás filas de la pista),
      y **Mis expresiones** (guardar con nombre, cargar, borrar; `Settings` de QtCore, categoría `expressions`, para
      todos los proyectos). `PropertyBehaviorDialog.qml` + `TrackHeaderColumn.qml` (`expressionTargets`).
- [x] H2. **Squash & Stretch** (pestaña de Animación al lado de Combinado; Jorge compró Squash & Stretch Pro y pidió
      replicarlo). Sus 169 animaciones y 641 sonidos tienen licencia para él, no para repartirlos: **las nuestras son
      propias** (`tools/squash_animations/build.py` → `presets/squash-animations/`, 59 en 8 categorías: Entrada,
      Salida, Movimientos, Saltos, Destacados, Rotaciones, Temblores, Glitch). Cómo funciona el original (para
      entenderlo, sin copiar): posición + Bezier Warp de AE animados, intensidad de deformación 0–150 %, escala
      0–200 %, anclado al inicio o al final, sonidos opcionales.
      - Motor: efecto `squash.deform` (`effects/squash_deform`: zoom, estirar con volumen, suelo, inclinar, abombar;
        mapa inverso en el shader). Margen nuevo `"padding": {"percentParams": [...]}` (en % del lado mayor de la capa,
        `applyEffectPadding`).
      - `core/SquashAnimation` (catálogo, curvas con el formato de `ClipAnimTrack`, `clipAnimTrackFromJson`),
        `AppController::squashAnimations`, `squashAnimationPose`, `applySquashAnimation` (escribe claves en x, y,
        rotation, opacity y `fx.N.zoom/stretch/bend/bulge`; Entrada al inicio, Salida al final, el resto en el cabezal;
        borra lo que había en ese tramo; back/elastic/bounce se escriben una clave por fotograma; un paso de deshacer
        con `beginEditSession`).
      - Interfaz: `SquashStretchPanel.qml` (categorías, Intensidad/Escala/Velocidad, cuadrícula) y `SquashAnimTile.qml`
        (un bloque con ojos que se deforma con el mismo mapa que el shader, al pasar el mouse).
      - Prueba `EditorStateTest::squashAnimationWritesKeysAndDeformer`.
      - **Falta:** probar en ventana (que el deformador no se corte al estirar, sobre todo en un video con carril de
        ajuste), miniatura propia del efecto (hoy es la de la Marioneta), sonidos propios (Stock › Sonidos) más adelante.
- [x] H3. **Motion Tools con pestañas** (Jorge: los scripts Trim-Pack, Bend Layers y ButtCapper, `.jsxbin` compilados:
      se replicó lo que hacen, no su código). Pestañas Herramientas / Recorte / Doblar / Extremos (`MotionToolsPanel.qml`).
      - **Recorte** (`TrimPackPanel.qml`, `AppController::applyTrimPack`): Entrada, Salida, Entrada y salida, Desde y
        Hacia el centro, Invertir, Copias (N copias en pistas encima, escalonadas), Rastro entrada/salida/E-S (una copia
        con una línea corta que va por delante), Convertir, Quitar. Ajustes como Trim-Pack: fotogramas, rango de
        desplazamiento, copias; sus teclas Alt/Mayús son dos interruptores (invertir dirección, girar el desplazamiento).
        Formas (`shape.trimStart/End/Offset`, 0–100) y trazos de textos (`text.layer.<id>.trimStart/End`, 0–1).
      - **Doblar** (`BendLayersPanel.qml`, `applyBend`, efecto `ae.bend`: arco de hasta 360°, a lo ancho o a lo alto,
        punto fijo): Arco, Sonrisa, Medio anillo, Anillo, Doblar, Enderezar al entrar, Doblar al salir, Quitar. Margen
        `"percentFactor"` nuevo en `padding`.
      - **Extremos** (`StrokeCapsPanel.qml`, `setStrokeCaps`, `strokeCapsState`): extremo plano/redondo/cuadrado y unión
        en punta/redonda/biselada (`TextShadingLayer::cap/join`, JSON `cap`/`join` solo si no son redondos; los dos
        pintores de Skia).
      - Prueba `EditorStateTest::motionToolsTrimBendAndCaps`.
- [x] H5. **Elementos** (Motion Tools, Jorge: como los scripts Super Morphings y Super Liquids, `.jsxbin` con todo
      compilado dentro): 34 elementos propios (22 morphings: formas que se transforman unas en otras y transiciones de
      círculo/cuadrado/estrella/corazón; 12 líquidos: mancha, gota y salpicadura, salpicadura, goteo, goteos, burbuja,
      fusión viscosa, charco, estallido, transición líquida, ola). Generados con `tools/shape_elements/build.py` →
      `presets/shape-elements/` (contornos de 48 puntos, 12 por segundo, todos con los mismos puntos para que el
      morph sea limpio). `core/ShapeElement` (catálogo, `outlinesAt`), `AppController::shapeElements`,
      `shapeElementFrame`, `insertShapeElement` (una capa de forma por capa, en pistas propias, con `pathShapes` y
      claves `path` lineales; centrado = tamaño × lado corto; transición = cuadrado del tamaño de la diagonal).
      `ShapeElementsPanel.qml`: Morphings / Líquidos, 8 paletas de 3 colores, tarjetas que se animan al pasar el mouse.
- **Probado en ventana (build 15d365b, `pruebas\FlipStudio-0.26-prueba-k`, 2026-10-29):** pestaña Squash & Stretch
  (categorías, controles, tarjetas en español); «Entrar rebotando» en una foto: claves de altura 0/0,48/0,75/0,99/1,14/
  1,26 y en 0,5 s la foto aterriza aplastada y abombada sin cortarse; Motion Tools con sus 5 pestañas; Elementos ›
  Líquidos › «Gota y salpicadura»: dos capas, charco y gotitas animados; Doblar › Medio anillo: la foto se curva;
  deshacer quita cada cosa en un paso. **Arreglado tras la prueba:** Squash & Stretch y Doblar dejaban elegida la capa
  de ajuste nueva (el panel se cerraba): `m_addEffectKeepsSelection`; las tarjetas de Elementos dibujaban las formas
  al 160 % (llenaban la tarjeta). **Falta en ventana:** Recorte y Extremos (probados por la prueba de CI), y el diálogo
  de expresiones («Aplicar a», «Mis expresiones»): el menú «…» de la fila no se abre con clics simulados, lo prueba
  Jorge.
- **Probado en ventana (build final de la tanda, `pruebas\FlipStudio-0.26-prueba-l`):** tras aplicar «Entrar rebotando» la
  foto sigue elegida y el panel en Squash & Stretch; las tarjetas de Elementos muestran cada forma entera.
- [ ] H4. **RTFX → Stock › «Animaciones Extremas»** (Jorge, 2026-10-29). Es un paquete de contenido (1035 videos de elementos: fuego, humo, electricidad, chispas,
      líquidos, cómic; transiciones; 48 títulos y tercios inferiores de AE; fondos; 201 sonidos), con licencia para él.
      Plan: nuestro propio paquete para Stock con las mismas categorías, renderizado con nuestros efectos y partículas.
      Pendiente de empezar.
- Dónde están los efectos de AE (pregunta de Jorge): Efectos › categorías «Generar y simular» (Ruido fractal, Mundo de
  partículas, Se hace añicos, Desplazamiento turbulento, Rampa de degradado, Ondas de radio) y «Estilos de capa»
  (también como botones en Fusión); la Marioneta está en «Glitch» y en la barra de la vista previa.
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
