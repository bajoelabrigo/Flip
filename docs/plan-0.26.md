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
- [ ] C1. Comportamientos por propiedad: Temblor (`wiggle`), Repetir (`loopOut` ciclo / ida y vuelta / continuar),
      Velocidad constante (`time * n`), Enlazar a otra propiedad (con multiplicador y desfase).
- [ ] C2. Mate de seguimiento: la capa de arriba como mate alfa / alfa invertido / luminancia / luminancia invertida.

## Etapa D — Curvas, tiempo, vista previa y 3D
- [ ] D1. Editor de curvas: velocidad de las claves escrita a mano (influencia %), auto-orientar al trazado.
- [ ] D2. Reasignación de tiempo con claves.
- [ ] D3. Vista previa: resolución ½/¼, fondo a cuadros, zonas seguras (lo que falte).
- [ ] D4. 3D: luces (si cabe).

## Dónde vive cada cosa
- Matriz de los padres: `src/engine/TransformLayer.*` (`transformParentsAt` = capas de transformación por pista;
  ahora también el padre de cada clip). El compositor la aplica en `buildGpuScene` (`applyParent`) y la vista
  previa dibuja los controles a través de ella (`PreviewController::clipsAtPlayhead`).

## Cómo se probó / qué falta probar
- (se va llenando)
