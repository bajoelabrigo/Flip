# Plan 0.29 — arreglos y herramientas que salieron al usar la app de verdad

Rama `flip/v0.29-tutorial` (sale de `flip/stock-logo-lt`). Origen: grabar a mano el tutorial de los tercios con logo
(Francois, Charlie, Jamie) moviendo el ratón de Jorge (2026-10-31). Después, pedido de Jorge: hacer ~10 proyectos de
situaciones distintas con la build nueva, arreglar lo que falle y añadir las herramientas que falten.

## Hecho (commit 8095b, build de Windows run 41227885368)

- **Giro 3D alrededor del punto de anclaje** (como After Effects). Antes la inclinación X/Y giraba siempre en el
  centro del rectángulo: una tarjeta con el anclaje en su borde no podía «levantarse» desde ese borde.
  `ClipPose3d::pivot` (anclaje respecto al centro, ya girado en el plano) y `clipPivot()` en `ClipTransform3d.h`;
  lo usan `placeCentre`, `clipQuadToWorld` y `clipLocalToWorld`; lo rellenan `FrameCompositor` (capa),
  `TransformLayer` y `PreviewController::previewBoxPose`. El giro en el plano sigue con `Clip::anchorShift`.
  - Falta: el gizmo 3D (`ClipGizmo::originOf`) sigue dibujando sus ejes en el centro, no en el anclaje.
- **Escribir un valor ya no crea una clave sin querer.** `PropertyKeyframeRow` escribía con `setClipKeyframe`
  (fuerza clave y cronómetro) al teclear un número. Ahora `typeValue()` sigue la regla del deslizador
  (`previewSetClipKeyframe`): clave solo si la propiedad está animada o con «Fotogramas clave automáticos». El rombo
  sigue creando la clave siempre. Síntoma que lo destapó: un valor fijado con el cabezal en 1,17 s dejaba una clave
  ahí y, al animar después, el nombre empezaba arriba y el «hueco» de un mate empezaba abierto.
- **Texto nuevo en el cabezal, en su propia pista.** `addTextClip` con `atSeconds < 0` (herramienta Texto, Títulos,
  Stock) busca una pista de texto libre en ese momento o crea una arriba de todo; antes iba a la primera pista de
  texto y, si estaba ocupada, al final del trabajo.
- **La herramienta Texto deja «Texto» seleccionado**: escribir lo reemplaza (antes quedaba «TextoFRANCOIS BERG»).
  Señal `textEditRequested(track, clip, selectAll)` en `PreviewToolOverlay` / `TransformOverlay` / `PreviewPanel`.
- **Motion Tools › Invertir** (Time-Reverse Keyframes de AE): `AppController::reversePickedKeyframes`, prueba
  `motionToolsReverseMirrorsPickedKeys`. Sirve para hacer la salida clonando la entrada e invirtiéndola.
- **Rombo en la Escala unida** (cadena) de Transformar: clave de posición y tamaño a la vez (crece desde el centro).
- Catálogos: 5 textos nuevos traducidos a los 16 idiomas (`lupdate` estable).
- **Relleno y Trazo como After Effects (pedido de Jorge).** En la barra de arriba, la palabra «Relleno» / «Trazo»
  abre `FillOptionsDialog.qml` (Ninguno, Sólido, Degradado lineal, radial y en barrido; modo de fusión, opacidad,
  grosor del trazo, Vista previa, Aceptar/Cancelar en una sesión de edición). Con una forma o texto elegido edita su
  capa de Relleno/Trazo (la misma del panel Forma) y los cuadritos muestran y cambian esa pintura; sin nada elegido
  fija la pintura de las formas nuevas (`PreviewController::toolFillOptions` / `toolStrokeOptions`, recordadas en
  Preferencias, aplicadas en `AppController::applyToolPaintOptions`). El editor del degradado es el mismo de Forma
  (`GradientStopEditor`, con `standalone` para la pintura por defecto).
- **Tiradores del degradado en el video** (`GradientHandlesOverlay.qml`): con la herramienta de selección, una forma o
  texto con degradado muestra sus dos puntos (inicio y fin; o centro y radio). Arrastrarlos reescribe ángulo, escala,
  desplazamiento y centro (`drift::gradientHandlePoints` / `setGradientFromHandles`, `AppController::gradientHandles`
  / `previewGradientHandles`), en un solo paso de deshacer. Pruebas `gradientHandlesRoundTrip` y
  `gradientHandlesAndToolPaintOptions`.

- **Arreglos sueltos (sin compilar todavía, para la siguiente build):** el primer «Guardar» de un proyecto sin
  título le pone el nombre del archivo (`ProjectFileController::saveProject`); Texto avanzado y el panel muestran la
  fuente y la negrita de las letras elegidas (`shownFontFamily` / `shownFontWeight`); campos de **Punto de anclaje
  (px)** en Transformar con botón de centrar; el gizmo 3D pone sus ejes en el anclaje (`ClipGizmo::originOf`);
  iconos de Invertir y de centrar con archivos que existen. Lo de «la forma nace con claves» era el valor escrito.

## Pendiente (visto en la grabación, sin arreglar todavía)

- **El primer clic se pierde** a veces: pestañas laterales del inspector (Texto, Transformar…) tras editar un texto en
  la vista previa o elegir otro clip, y «Abrir Texto avanzado…» (abrió al 2.º–3.er clic). Sospecha: el inspector se
  rehace entre pulsar y soltar. Hay que reproducirlo en ventana y depurarlo, no adivinar.
- Texto avanzado › Letras seleccionadas: el desplegable «Fuente» sigue diciendo la fuente del texto entero después de
  poner otra a las letras elegidas.
- Tras «Guardar como» `francois.flip`, la píldora de arriba sigue diciendo «Proyecto sin título».
- La forma dibujada con el rectángulo nace con claves (cronómetro) en X/Y/W/H a 0 s. Con el arreglo del valor
  escrito ya no estorba, pero conviene que nazca sin cronómetro, como en AE.
- El anclaje solo se puede escribir en la fila de la línea de tiempo; Transformar no tiene campos de anclaje.

## Tutorial (en `Downloads\FlipStudio\pruebas\tutorial-llt`)

- Tomas en bruto `raw-<toma>.mkv` (ffmpeg gdigrab del 2.º monitor), subtítulos `subs-<toma>.log` (hora y texto),
  montaje `montar.py <toma>` → `tutorial-<toma>.mp4` (recorta el borde, banda de subtítulos, cortes, ratos quietos
  acelerados con mpdecimate). Francois y Charlie grabadas; Jamie se repite con la build nueva (la primera toma no
  servía por el giro 3D en el centro).
