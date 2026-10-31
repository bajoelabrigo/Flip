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

## Los ~10 proyectos de prueba (pedido de Jorge, 2026-10-31)

Con la build nueva, en ventana, material en `pruebas\proyectos-029\material` (copias). Cada uno usa la app como lo
haría un usuario; lo que falle se arregla y lo que falte se añade. Estado al lado de cada uno.

1. **Reel vertical 9:16**: video de 120 fps, cortes, cámara lenta, texto con animación, música y subtítulos.
2. **Presentación de fotos**: 4 fotos con transiciones, Ken Burns (claves de escala), música al ritmo.
3. **Intro de YouTube**: logo en 3D que se levanta desde su borde (anclaje + inclinación), texto con degradado.
4. **Anuncio de producto**: formas con degradado lineal y radial desde «Opciones de relleno», tiradores, contador.
5. **Tercio inferior**: barra con claves, entrada clonada e **Invertir** para la salida (Motion Tools).
6. **Tutorial de pantalla**: zoom y paneo con claves suaves, flecha (pluma), resaltado con máscara.
7. **Persona recortada**: quitar fondo y texto detrás de la persona.
8. **Mate de seguimiento**: texto que aparece dentro de una forma que se abre (como Charlie).
9. **Vlog 16:9**: varias pistas, velocidad, congelar fotograma, ajustes de color y un LUT.
10. **Exportar**: el mismo proyecto a MP4 1080p, GIF y vertical; guardar, cerrar y abrir de nuevo.

**Cómo se trabaja (Jorge):** si un proyecto se traba por una herramienta que falta o un fallo, se anota aquí abajo todo
lo que hace falta, se deja y se sigue con el siguiente. Al final se arregla todo, se compila una vez y se vuelve a
probar lo que falló en ventana, grabándolo.

### Trabado en… (se llena durante las pruebas)
- (nota técnica) El degradado lineal ahora pasa por `center` (antes siempre por el medio de la caja); con el valor de
  siempre (0,5; 0,5) se ve igual. **El editor web** todavía dibuja el lineal por el medio: un degradado movido con los
  tiradores del escritorio se verá corrido en la web hasta que la web lea `center` también en el lineal.
- (trampa repetida) La primera build con `FillOptionsDialog` no arrancaba: «Cannot override FINAL property» por
  `property int clip` en un `ThemedDialog` (Popup). Renombrado a `editTrack` / `editClip`. Siempre abrir el portable
  y mirar `stderr` antes de seguir.

## Verificación en ventana de la build 41234259093 (portable `pruebas\FlipStudio-0.29-prueba-b`)
- OK: la app arranca sin errores de QML. «Opciones de relleno» se abre con clic en «Relleno» (con la herramienta de
  forma elegida), muestra los 5 tipos, el editor de degradado y los preajustes; Aceptar deja la pintura para la forma
  nueva, y el rectángulo sale con el degradado. Los tiradores aparecen con la herramienta de selección; arrastrar el
  final gira y acorta el degradado, y Ctrl+Z lo devuelve.
- **Fallo:** al elegir un preajuste con «Degradado radial» marcado, el tipo pasa a «Degradado lineal» (el preajuste
  trae su propio `kind`). Debe conservar el tipo elegido en la fila de arriba.
- OK: «Invertir» (2 claves de opacidad 0→100 pasan a 100→0). Campos de anclaje y rombo de Escala visibles. Valores
  escritos ya no dejan claves sueltas en X/Y. El giro 3D pivota en el anclaje (borde de arriba fijo).
- **Fallo (arreglado en código, falta compilar):** el contorno de selección cian giraba desde el centro: 
  `PreviewController::clipPoseMatrix` no recibía el anclaje (ahora `anchorFx/Fy` desde `TransformOverlay`).
- OK: la herramienta Texto deja «Texto» seleccionado (escribir lo reemplaza) y el texto va a su propia pista en el
  cabezal. El primer Guardar pone el nombre del archivo en la píldora («verificacion»).
- **Fallo menor:** el clip de texto sigue llamándose «Texto» en la línea de tiempo después de escribir «HOLA»
  (el nombre sale del texto de ejemplo y no se actualiza si el usuario no lo renombró).
- **Fallo (de la sesión anterior también):** soltar un medio en la vista previa a veces no hace nada si el arrastre
  es corto (pocos movimientos); hay que pasar despacio por encima. Revisar el `DropArea` de la vista previa.
- **Fallo (2 de 3 veces, también en zona vacía):** herramienta Texto con clic **encima de otra capa** (la tarjeta roja): el texto se crea, pero lo que se
  escribe se pierde (queda «Texto»). Sobre una zona vacía sí funciona. Sospecha: el clic llega también a la capa de
  debajo, que toma el foco del editor en línea.
- **Fallo:** en «Opciones de relleno», escribir un color en el campo hex y pulsar Enter acepta la ventana **antes**
  de que el campo guarde el color: la forma sale con el color anterior. `ColorSwatchField` confirma en
  `editingFinished`; el diálogo debe leer el texto del campo al aceptar (o no aceptar con Enter dentro del campo).
- **Fallo:** en el selector de color (cuadrito de la barra con una forma elegida), el campo hex no toma el foco con
  clic; un `Ctrl+A` va a la línea de tiempo y elige todos los clips. Revisar el foco del `ThemedColorDialog`.
- OK: Jamie grabado con la build nueva (`raw-jamie.mkv`): campos de anclaje, giro 3D desde el borde de arriba
  (cara blanca) y desde el de abajo (cara roja), Texto avanzado mostrando «Antonio» en las letras elegidas.
- **A mejorar:** a mitad del giro las dos caras se pintan superpuestas (sin orden por profundidad). Para el prisma
  hace falta «Ocultar por profundidad» encendido por defecto en capas 3D que se cruzan, o explicarlo en la guía.
- **Fallo:** al elegir otra composición, los campos de anclaje mostraron un rato los valores de la anterior
  (856/713 en la cara roja antes de escribir). Revisar el enlace de `anchorSection` al cambiar de clip.

### Proyecto 1 — reel vertical 9:16 (video de 120 fps, música, cortes, cámara lenta, texto)
- OK: el proyecto toma la forma vertical del primer clip y la ventana pasa sola a la disposición vertical; la tecla S
  divide solo el clip elegido; Velocidad 0,5× ofrece «Cámara lenta suave».
- **Falta:** al poner 0,5× el clip conserva su duración y solo muestra la mitad del material (6,18→11,35 s); en
  CapCut el clip se alarga y se ve entero. Hace falta la opción «Alargar el clip» (o que sea lo normal con el rizo).
- **Fallo menor:** la música soltada al principio de su pista quedó en 0,18 s, no en 0 (el imán no la pegó al inicio).
- **Falta:** recortar la música al final del video con un clic («Ajustar a la duración del video»).
- **Causa del texto perdido (arreglada en código):** Esc en el editor de texto de la vista previa **descartaba** lo
  escrito (`InlineTextEditor` llamaba a `cancel`). Ahora Esc conserva el texto, como AE y CapCut; Ctrl+Z deshace.
  Era lo que pasaba en Jamie («flipstudio» y el nombre se perdían), no la capa de debajo.

### Proyecto 2 — presentación de 4 fotos
- **Fallo:** arrastrar 4 fotos elegidas en Medios a la línea de tiempo deja **solo una** (la del cursor).
- **Fallo:** clic derecho › «Añadir 3 elementos a la línea de tiempo» los pone en una **pista nueva** (llamada
  «Gráfico 1») desde 0, en vez de a continuación del último clip de la pista de video, como CapCut.
- **A revisar:** con una foto como primer clip el proyecto toma su forma (867×1300); en una presentación se espera
  16:9 o preguntar. El aviso «Cambiar» existe; quizá basta con que el primer medio vertical no cambie un 16:9 ya
  elegido.
- OK: transición «Fundido cruzado» soltada en el corte; Exportar 720p da un MP4 de 720×1080 y 15 s correcto.
- **Fallo:** Transiciones › Tendencias muestra las tarjetas sin miniatura (grises); Básico sí las tiene.

### Proyecto 10 — exportar: OK (ver proyecto 2).
### Proyectos 3, 4, 5 y 8: cubiertos por Jamie (3D desde el anclaje), la verificación de degradados, Invertir y
el mate de Charlie.

### Proyecto 9 — vlog 16:9 (congelar, filtro)
- OK: Congelar fotograma (el copo) inserta «Fotograma congelado» y empuja lo demás; un filtro de Filtros se baja y
  queda como capa de ajuste enlazada al clip.
- **Fallo:** al aplicar un filtro de Stock se abre sola la ventana «Descargas» encima de todo; basta el aviso de abajo.
- **Fallo:** varias tarjetas de Filtros (Drama frío, Blanqueado…) salen sin miniatura, igual que Transiciones ›
  Tendencias.
- (descartado) La barra de la línea de tiempo cambia sus botones según lo elegido, igual que CapCut; el clip borrado
  fue un error de puntería al calcular la posición, no de la app.
- No está en el menú del clip «Congelar fotograma» (solo el copo de la barra): añadirlo al menú, como CapCut.

### Proyectos 6 y 7 — no probados en esta tanda (zoom con pluma y máscara; quitar fondo con IA).

## Tanda de arreglos tras los proyectos (para la build siguiente)
- Esc en el editor de texto de la vista previa conserva lo escrito (era la causa del texto perdido en Jamie).
- Opciones de relleno: un preajuste ya no cambia el tipo de degradado; Enter no acepta la ventana (confirma el campo).
- Ctrl+A / Ctrl+C / Ctrl+X / Ctrl+V / Supr van al campo de texto que tiene el teclado, no a la línea de tiempo
  (`Main.qml` `dispatchAction`): el hex del selector de color no se podía cambiar.
- Campos de anclaje con `Binding` (no se quedan con los valores del clip anterior).
- «Añadir N elementos a la línea de tiempo» pone fotos y videos en la pista principal de video, uno detrás de otro.
- Arrastrar varios medios elegidos: el primero cae donde se suelta y los demás lo siguen en su pista
  (`application/x-drift-assets`, `addClipsFromAssets(ids, track, seconds)`).
- Descargas ya no se abre sola al bajar algo de Stock.
- «Congelar fotograma en la posición actual» también en el menú del clip.
- Velocidad: se conserva siempre el material; a 0,5× el clip dura el doble y los clips de detrás se corren
  (`retimeKeepingSource`). Pruebas `slowingAClipKeepsItsMaterial` y `addClipsFromAssetsPutsPhotosOnTheVideoTrack`.
- Contorno de selección 3D girando en el anclaje (`clipPoseMatrix`).

## Reprueba en ventana de la build c523066 (2026-10-31, grabada: `pruebas\tutorial-llt\reprueba-0.29.mp4`)
Portable `pruebas\FlipStudio-0.29-prueba-c`, arranca sin errores de QML.
- ✓ Esc en el editor de texto conserva lo escrito y el clip toma ese nombre (texto en su propia pista).
- ✓ Ctrl+A dentro de un campo selecciona su texto (no los clips).
- ✓ Opciones de relleno: un preajuste deja el tipo (Radial).
- ✓ Campos del anclaje cambian con el clip elegido (225, 345 → 192, 52).
- ✓ Arrastrar dos medios elegidos: caen seguidos en la pista de video (5,00 s + 68,22 s + el otro).
- ✓ Velocidad 0,5×: 136,45 s, recorte 0–68,22 intacto, el clip siguiente se corre.
- ✓ «Congelar fotograma en la posición actual» en el menú del clip.
- ✓ Capa 3D con anclaje X 0: inclina sobre el borde izquierdo y el contorno de selección sigue a la forma.
- Sin probar: que Descargas no se abra sola (pide bajar algo de Stock con la cuenta).

Fallos nuevos, ya corregidos en el código (para la próxima build):
- Con la herramienta Rectángulo/Pluma y un **texto** elegido, Opciones de relleno pintaba el texto y la forma nueva salía
  con el color de siempre. Ahora, como After Effects, con herramienta de dibujo y un texto elegido el relleno es el de la
  herramienta (`PreviewToolbar.pickedStyled`, `FillOptionsDialog.openFor(which, toolOnly)`).
- «Cambiar nombre del clip»: el campo no tomaba el teclado al abrir (ThemedDialog lo da al botón Aceptar en su
  `onOpened`); `NameDialog` lo toma después con `Qt.callLater` y selecciona el nombre.
- **Escribir 0 en un campo con `Binding on value { when: !activeFocus }` no se guardaba**: al tomar el foco el Binding
  devolvía el valor al de por defecto (0), y 0 contaba como «sin cambio». Lo mismo al presionar un deslizador
  (`when: !pressed`). `restoreMode: Binding.RestoreNone` en los 38 casos (19 archivos).
  **Trampa:** todo `Binding` con `when` sobre un campo o deslizador lleva `restoreMode: Binding.RestoreNone`.
- Menor, sin arreglar: el triple clic no selecciona el número en un campo numérico (clic + Ctrl+A sí).

## Proyectos 6 y 7 en ventana (2026-10-31, grabados: `pruebas\tutorial-llt\proyectos-6-7.mp4`)
- **6 — zoom, flecha y resaltado:** Escala 100 % → 141 % en 4 s ✓; línea con la pluma sin relleno y trazo blanco ✓;
  capa de ajuste «Aplicar a» solo el video (queda como carril, la flecha no se oscurece) + Exposición abajo + máscara
  círculo invertida con desvanecimiento ✓, y la máscara crece con el zoom ✓.
  **Faltaba: puntas de flecha.** Hecho: capa Trazo › «Flecha al inicio / al final» (Ninguna, Triángulo, Abierta,
  Punto) y «Tamaño de la flecha» (en anchos de trazo), solo en trazados abiertos y siguiendo Recortar final
  (`TextShadingLayer::arrowStart/arrowEnd/arrowSize`, `drawArrowHeads` en `SkiaShapePainter.cpp`, margen en
  `shapeBleedFor`, MCP, prueba `strokeArrowheadsRoundTrip`). **Probar en ventana** con la build siguiente.
- **7 — quitar el fondo con IA:** con «Personas (automático)» tarda ~1 min (695 fotogramas) y el recorte queda limpio ✓.
  **Fallo:** «Recortar personas…» abría la ventana en «Cualquier elemento» (SAM, ~40 min). Arreglado: cada botón abre
  su modo (`openSegmentation(..., "rvm" | "sam2")`, `SegmentationWindow.openFor(..., backend)`). **Probar.**
- Visto de paso: soltar un medio debajo de las pistas crea la pista **debajo** de todo (detrás del video principal);
  arrastrar la cabecera para subirla funciona. Al borrar clips de la pista principal queda el hueco (en CapCut se
  cierra solo): anotado, sin tocar.
