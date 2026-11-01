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

## Valores arrastrables como After Effects en toda la app (pedido de Jorge, 2026-10-31)
«Ponle manejadores a los controles… que cuando se pone el mouse encima al arrastrar aumente o disminuya la cantidad»,
«en todas las herramientas de la app incluyendo la barra de arriba».
- `components/ScrubArea.qml`: sobre un número el puntero es ↔; arrastrar a los lados cambia el valor en vivo
  (Mayús ×10, Ctrl ×0,1), un clic sin arrastrar deja escribir, la rueda sigue desplazando el panel.
- `ThemedNumberField` (101 usos: Transformar › anclaje, General, Formas, Texto, Preferencias, el grosor del trazo de la
  barra de arriba…): un arrastre = un paso de deshacer (su propia sesión de edición, salvo que un diálogo ya tenga
  una: `EditorState.editSessionOpen()`).
- `PropertyKeyframeRow` (Posición, Escala, Rotación, Opacidad, recortes, máscaras…): el campo y la lectura de los
  deslizadores se arrastran como el deslizador (`beginPreviewDrag` / `previewSetClipKeyframe` / `commitPreviewDrag`:
  clave si la propiedad está animada, si no el valor).
- Ajuste (Exposición, Brillo…): el número sobre el deslizador; el «desde» del contador de Texto pasó a campo numérico.
- La línea de tiempo ya lo tenía (`timeline/ScrubValue.qml`, 0.25): mismo comportamiento y mismo texto de ayuda.
- **Probar en ventana** con la build siguiente: arrastrar Posición X, Escala, Opacidad, anclaje, grosor de la barra de
  arriba, Exposición; Ctrl+Z deshace cada arrastre de una vez.

## Prueba en ventana de la build 9131671 (2026-10-31, grabada: `pruebas\tutorial-llt\manejadores-0.29.mp4`)
- ✓ Valores arrastrables: Posición X (fila con deslizador), anclaje X (campo, 1 px por píxel), grosor del trazo en la
  barra de arriba (6 → 27), Tamaño de la flecha (de 0,1 en 0,1). Ctrl+Z deshace cada arrastre de una vez.
- **Arreglado después:** en las filas con deslizador el paso salía del rango (≈40 px por píxel en Posición); ahora es
  1 unidad por píxel (0,01 en porcentajes), como After Effects (`PropertyKeyframeRow.scrubStep`).
- ✓ Puntas de flecha: Forma › Trazo › Flecha al final › Triángulo y su tamaño, se ven en la vista previa.
- ✓ «Recortar personas» abre «Personas (automático)» y «Recortar un sujeto» abre «Cualquier elemento».
- ✓ «Cambiar nombre del clip»: se escribe directo. ✓ Un 0 en el anclaje se guarda. ✓ Con un texto elegido y el
  Rectángulo, Opciones de relleno es el de la herramienta (la forma sale con el degradado, el texto no cambia).
- **Fallo nuevo, arreglado:** al recuperar el trabajo sin guardar faltaba el «Fotograma congelado»: la limpieza del
  arranque borraba la carpeta del proyecto sin guardar (donde van los congelados) salvo en Android
  (`ProjectFileController`, el id de la recuperación ahora se conserva en todas las plataformas).
- Pendiente de ver con la build siguiente: el paso nuevo del arrastre en las filas y la recuperación con un congelado.

## Pruebas 3, 4, 8 y 10 + verificación (build 4e6b00f, grabada: `pruebas\tutorial-llt\pruebas-3-4-8-10.mp4`)
- ✓ Recuperar con un congelado: el archivo sobrevive al cierre forzado y la app lo encuentra (los dos que faltaban
  los borró una copia 0.28 abierta por error, con la limpieza vieja).
- ✓ Arrastre de Posición X 1 px por píxel (349 → 395).
- **3 (intro con logo 3D):** trabada. Con la Inclinación X animada, escribir 0 a 1 s reescribía la única clave
  (`previewSetClipKeyframe` solo creaba clave con «Fotogramas clave automáticos»). Arreglado: con el cronómetro puesto
  siempre es clave en el cabezal (prueba `typedValueOnAnAnimatedPropertyAddsAKey`). Además: el arrastre de grados iba
  de 0,1 en 0,1 (ahora 1° por píxel; 0,01 solo en rangos de 0 a 2) y la lectura de Escala no se arrastraba (ahora sí,
  y las filas de deslizador de Texto también).
- ✓ **4 (anuncio):** degradado radial dorado con el tirador del radio, contador $0 → $99.
- ✓ **8 (mate):** Mate alfa con la forma encima; la forma de mate se oculta y el precio solo se ve dentro.
- ✓ **10:** GIF 1280×720 15 fps 8,3 s; vertical MP4 720×1280 30 fps; guardar, cerrar y abrir con todo en su sitio.
  **Fallo, arreglado:** el nombre volvía como «Proyecto sin título» (el documento interno seguía con «Untitled
  Project»; ahora el primer Guardar y Guardar como escriben `projectName` e `id` también en el documento).

### Fallos vistos en esta tanda (por arreglar)
- Congelar un clip con el fondo quitado: el congelado sale con el fondo (la máscara no cubre su tramo).
- Una forma nueva nace en una pista debajo del texto (en AE una capa nueva va arriba de todo).
- El primer clip soltado en la pista principal queda en 0,15 s, no en 0.
- Exportar video después de un GIF hereda sus 15 fps.
- Pasar el proyecto a 9:16 deja el video principal con su tamaño (franja negra); CapCut lo ajusta al cuadro nuevo.
- Las filas de claves de la línea de tiempo no muestran la Inclinación 3D (X/Y).
- Soltar un medio sobre la regla o arriba de las pistas no hace nada.

## Tanda «todo saneado» (pedido de Jorge, 2026-10-31: corregir todos los fallos y probarlos)
Arreglado en el código (causas halladas con tres búsquedas en paralelo):
- **Primer clic perdido** (pestañas del panel, «Abrir Texto avanzado…»): el editor de texto en línea confirmaba dentro
  de la pulsación que le quitaba el foco y el panel se refrescaba a mitad del clic. Ahora confirma después
  (`Qt.callLater`), las pestañas cambian al presionar y el botón de Texto avanzado no toma el foco.
- **Texto avanzado › «Fuente»** volvía a la del texto entero: el campo oculto del inspector cortaba el enlace de la
  selección; ahora solo escribe la selección fuera de la ventana, y `runUnderCursor` se refresca tras cada edición.
- **Soltar en la vista previa** solo funcionaba despacio: el área era solo el lienzo y vivía dentro de la herramienta
  de transformar. Ahora es toda la vista, siempre, y lleva el punto al lienzo.
- **Soltar sobre la regla** no hacía nada; **debajo de las pistas** creaba la pista bajo la principal. Ahora regla
  = pista nueva arriba; debajo = encima de las pistas de video (el sonido, abajo).
- **Primer clip en la pista principal** quedaba en 0,15 s; música soltada cerca del inicio en 0,18 s: el clip ahora
  usa el mismo imán que el contorno, y la pista principal vacía (o un primer clip a menos de 0,5 s) empieza en 0.
- **Capas nuevas** (formas, sólidos, nulos, pluma, luces) nacían bajo el texto: ahora arriba de todo
  (`topFreeTrackForClipType`).
- **Congelar un clip sin fondo** salía con el fondo: la captura conserva sus máscaras enlazadas y es transparente.
- **3D:** dos o más capas 3D opacas a la vez se ordenan por profundidad solas; empates por orden de pista
  (`GL_LEQUAL`).
- **Miniaturas grises** de Stock: reintentos, la vista previa como respaldo y un ícono; transiciones sin tira usan su
  miniatura.
- «Ajustar a la duración del video» en el menú de un clip de audio (`fitClipToVideoLength`, prueba).
- Filas de Inclinación X/Y siempre visibles en capas 3D; pasar a 9:16 ajusta el video que llenaba el cuadro;
  Video y GIF con su propia velocidad; «Recorte cancelado» ya no es un error fijo; editor web: degradado lineal
  por su centro (rama `web/v0221-texto` `b71fd`, sin desplegar).

## Diez proyectos reales con las herramientas de animación (Jorge, 2026-10-31, noche; grabados)
«No es probar herramientas, es crear proyectos reales». Portable `pruebas\FlipStudio-0.29-prueba-f` (build bc31c67).
Grabación: `pruebas\tutorial-llt\raw-p<n>.mkv` + `subs-p<n>.log`, montaje con `montar.py`. Lo que falte o falle se
anota aquí y se corrige todo al final.
1. Squash & Stretch «Your First Animation» (tutorial V2): cuadro naranja que cae y salta sobre la línea hasta el logo.
2. Squash & Stretch «Text Animation Made Easy»: título con las letras que rebotan una a una.
3. Squash & Stretch «Keep the volume» (demo 0650): dos pelotas que caen; una encoge, la otra conserva el volumen.
4. Logo que se dibuja: trazo con Recorte (Motion Tools › Recortar) y Curvas para la suavidad.
5. Morph: tres formas que vuelan y se funden en el logo (Motion Tools › Elementos › Morph).
6. Título con Estela líquida (Elementos › Estela líquida).
7. Chorro líquido que corre por un trazado y descubre un texto (Elementos › Línea líquida).
8. Banda de título que se dobla al entrar (Motion Tools › Doblar).
9. Tercio inferior hecho a mano: Thomas Clarke (llt3-invitado).
10. Tercio inferior inclinado hecho a mano: Laureen Marlene (llt3-inclinada).

### Notas durante los proyectos
- **P1, fallo:** en el selector de color (cuadrito del relleno), escribir un hex no se guarda: `ThemedColorDialog.qml:222`
  da «"#" is not a valid color name» con el texto a medio escribir. Hay que aceptar solo un hex completo.
- **P1, fallo:** dibujar un rectángulo empezando justo en el borde del lienzo no crea nada (hay que empezar dentro).
- **P1, falta:** no hay un «Sólido del tamaño del cuadro» rápido desde la barra (hubo que dibujar y ajustar 0,0 y 100 %).
- **P1, fallo grave:** texto nuevo con la herramienta Texto, Esc, herramienta Selección, pestaña General, clic en «Comienza
  en», Ctrl+A y «0»: el **contenido del texto** pasó a ser «0» (el editor en línea seguía con el teclado). Ctrl+Z lo
  devuelve. Sospecha: con el commit diferido (`Qt.callLater`) el proxy oculto conserva el foco tras Esc.
- **P1, falta:** un texto creado con la herramienta empieza en el cabezal; para un título que dura todo el video hay
  que moverlo a mano (en AE la capa nace en el cabezal también: aceptable, pero falta «Comienza en» fácil).
- **P1, falta:** con la herramienta Selección, la barra de arriba no muestra Relleno/Trazo de la forma elegida
  (en AE sí, con cualquier herramienta).
- **P1, falta:** «Salto hacia adelante» tiene una distancia fija (~520 px) sin control; tres saltos encadenados se salen
  del cuadro. Hace falta «Distancia» (o que el salto vaya hasta una clave final, como «Start/End of behavior» del
  tutorial de Squash & Stretch).
- **P1, falta:** borrar las claves de un tramo de tiempo en todas las filas de una capa a la vez (el salto escribe
  posición, ancho, inclinación, estirar…): un recuadro que abarque todas las filas, o «Borrar claves después del
  cabezal».
- **P2, falta:** Squash & Stretch por letras, como «Split into characters» del tutorial (Text Animation Made Easy):
  hoy se aplica a la capa entera o escalonado entre capas. Hace falta «Dividir texto en letras» (una capa por
  letra, como AE) o que el aplastamiento se aplique por carácter dentro del texto.
- **P2, falta:** color de fondo del proyecto (en Propiedades o en Tamaño y formato): hoy hay que dibujar un rectángulo.
- **P2, fallo grave (sigue en bc31c67):** el primer clic se pierde en el panel derecho **cada vez** que cambia la
  selección o la página: pestaña lateral «Texto», páginas Básico/Animación de Texto, tarjetas de Texto › Animación,
  campo de color. El arreglo (`onPressed` en la barra lateral, commit diferido) no basta: hay que reproducirlo con
  un registro (`onCanceled` / `onPressed`) y hallar quién se queda la pulsación. Consecuencia peligrosa: Ctrl+A con
  un campo que no recibió el clic elige **todos los clips**.
- **P2, falta (cuenta):** las animaciones de letras con llama piden iniciar sesión; en el portable de prueba no hay
  sesión. No es un fallo (decisión de Jorge), pero los proyectos de prueba no pueden usar Texto › Animación.
- **P3, falta:** Ctrl+D duplica el clip **a continuación** en la misma pista; en After Effects duplica la capa en el
  mismo momento, en una pista encima. Al menos en Pro debería hacer lo de AE.
- **P3, fallo:** un rectángulo muy fino (arrastre de 2 px) no se crea y no avisa; para una línea hace falta grosor
  mínimo o la herramienta Línea.
- **P3, falta:** herramienta Elipse visible en la barra (hubo que dibujar un rectángulo y cambiarlo a Elipse en Forma).
- **P4, falta:** Motion Tools › Recorte no recuerda «Fotogramas» entre usos (vuelve a 20).
- **P4, duda:** Curvas › «Salida suave» con la capa elegida no dice a qué claves se aplicó (sin aviso ni claves
  resaltadas); conviene un aviso «Curva aplicada a N claves» o usar las claves elegidas.
- **Jorge (2026-10-31), pedido:** en Morph, opción para que **la última forma quede visible** al terminar (hoy
  desaparece): dos modos, «Desaparece al final» y «Queda la última forma».
- **Jorge (2026-10-31), pedido:** Squash & Stretch que anime **letra por letra** un texto (confirma la falta del P2).
- **P7, fallo:** en Opciones de trazo, escribir el color sin «#» (`1E5BFF`) da error; debería aceptar el hex sin «#».
- **P7, falta:** Chorro líquido no **dibuja el trazado**: el trazo se ve entero desde el fotograma 0 y el chorro solo
  pasa por encima. Hace falta la opción «Revelar el trazo» (que el trazo crezca detrás del chorro, como un Recorte).
- **P7, fallo:** el chorro salió turquesa aunque el color elegido era el azul (la muestra azul quedaba marcada).
- **P7, fallo:** el clip «Líquido» dura ~1 s y el trazado 2 s; al crear un texto en 1,6 s el resto queda corto.
  El clip del chorro debería durar lo que dura el trazado.
- **P7, fallo grave:** texto nuevo con la herramienta Texto, escribir «Fluye» y Esc: el texto queda **vacío** (sin
  contenido en el lienzo). Al editarlo de nuevo sí guarda. Mismo origen que el fallo del P1 (commit diferido).
- **P7, falta:** el texto nuevo toma el color del relleno de la barra (aquí el papel claro) y 24 px: sale invisible y
  diminuto. Un texto nuevo debería usar un color legible y un tamaño proporcional al cuadro.
- **P7, falta:** todas las animaciones de Texto › Animación › Entrada que se ven primero llevan la llama (piden
  sesión); sin sesión no hay ninguna gratis a mano. Mostrar primero las libres o un filtro «Sin cuenta».
- **P8, bien:** Doblar › «Enderezar al entrar» dobla la banda 90° y la endereza en 0,6 s, limpio.
- **P8, falta:** el título encima de la banda no se dobla con ella; haría falta «Doblar también las capas hijas» o
  emparentar y que el doblez afecte al grupo (en AE se precompone).
- **P8, fallo:** arrastrar un texto recién creado con la herramienta Selección apenas lo mueve (unos px) en el primer
  arrastre; el segundo sí. Mismo síntoma que el primer clic perdido.
- **Jorge (2026-10-31), P8, fallo:** la banda roja **se corta al doblarse** (la parte doblada se sale del recuadro de
  la capa y se recorta). El dibujo doblado tiene que tener margen (bleed) para toda la curva.
- **P9, fallo:** con un rectángulo recién dibujado, el cuadro de Relleno de la barra **cambia ese rectángulo** (con
  «Vista previa»), no el color de la herramienta para el siguiente. Para dibujar otro de otro color hay que
  deseleccionar antes o recolorear después. En AE el relleno de la barra con la herramienta activa es el del próximo.
- **P9, sorpresa:** un segundo rectángulo dibujado con la capa de forma elegida entra **en la misma capa** (aviso
  «pulsa Esc antes»): es como AE, pero entonces no se puede animar la etiqueta y la línea por separado con las
  herramientas de capa. Bien que avise; falta un botón «Separar en capas» (AE: Create Shapes from… / Split).
- **P9, fallo:** arrastrar un texto en el lienzo con Selección no lo mueve (dos intentos, unos px); hubo que escribir
  la posición en Transformar.
- **P9, falta:** Animación › Entrada del clip no tiene **barrido/revelar** (de izquierda a derecha, con un borde): es la
  entrada típica de un tercio inferior. Tampoco hay a mano la cuadrícula 3×3 del anclaje en Transformar de una forma
  (solo «Anclaje en el centro»), así que la escala X desde la izquierda no se puede armar rápido.
- **P9, bien:** Squash & Stretch › «Entrar por la izquierda» escalonado entre las tres capas: entra en orden y limpio.
- **P9, falta:** un texto nuevo sobre una etiqueta blanca sale blanco (toma el relleno de la barra): invisible.
- **P10, bien:** la pluma hace una etiqueta inclinada y una línea inclinada limpias (clic, clic, cerrar en el primero).
- **P10, falta:** no hay **cursiva** en Texto › Básico (solo B, U, S y el peso); Inter no trae Italic y no hay
  cursiva sintética. Un tercio inclinado la pide.
- **P10, fallo:** Squash & Stretch › «Aparecer de golpe» deja la etiqueta **visible y estirada en el fotograma 0**
  (no nace de cero) y deforma el borde inclinado (la punta queda redondeada en 0,2 s).
- **P10, duda:** con cuatro capas elegidas, «Escalonar» decía 3 copias (no tomó la primera elegida, o el campo no
  sigue la selección).

## Correcciones y herramientas tras los 20 proyectos (Jorge, 2026-10-31: «no dejes nada pendiente»)
Después: una build, 10 proyectos de prueba en ventana y **5 animaciones de Squash & Stretch hechas a mano con
fotogramas clave** (desde cero, con las herramientas de la app). Estado: [ ] pendiente, [x] hecho, [p] probado.

Fallos
- [ ] F1 Primer clic perdido en el panel derecho (pestañas, tarjetas, campos, Aplicar).
- [ ] F2 Arrastrar un texto en el lienzo casi no lo mueve.
- [ ] F3 Tras Esc el editor de texto en línea sigue con el teclado (el título pasó a «0»).
- [x] F4 Doblar recorta la forma doblada (sin margen).
- [x] F5 Chorro líquido: revelar el trazo, respetar el color elegido, durar lo que dura el trazado.
- [x] F6 (no era fallo: la etiqueta no estaba elegida; el Ctrl+clic se perdió = F1) Squash › Aparecer de golpe: visible y estirada en el fotograma 0; punta redondeada en formas inclinadas.
- [x] F7 (= F1: un Ctrl+clic perdido) «Escalonar» no cuenta bien las capas elegidas.
- [x] F8 Texto nuevo legible (color con contraste y tamaño proporcional al cuadro).
- [x] F9 Rectángulo que empieza en el borde del lienzo o muy fino: se crea (o avisa).
- [x] F10 Recorte recuerda «Fotogramas».
- [x] F11 Color hex sin «#» (ColorSwatchField).
- [x] F12 Curvas dice a cuántas claves se aplicó.
- [x] F13 Con Selección, la barra muestra Relleno/Trazo de la forma elegida.

Herramientas
- [x] T1 Entrada/salida «Barrido» (revelar desde un lado, borde recto o inclinado).
- [x] T2 Cuadrícula 3×3 del anclaje en Transformar de cualquier capa.
- [x] T3 Dividir texto en letras (una capa por letra, en su sitio).
- [x] T4 Morph: «Queda la última forma».
- [x] T5 (ya existía: clic derecho › Separar en capas; el aviso ahora lo dice) Separar las partes de una capa de forma en capas.
- [x] T6 Herramientas Elipse y Línea en la barra.
- [x] T7 Ctrl+D en Pro: duplicado en el mismo momento, en una pista encima.
- [x] T8 Cursiva sintética si la fuente no la trae.
- [x] T9 Borrar claves de todas las filas: después del cabezal / en un tramo.
- [x] T10 («Oomph» pasa a «Recorrido», hasta 400 %) Distancia en «Salto hacia adelante».
- [x] T11 Doblar también las capas hijas.
- [x] T12 Color de fondo del proyecto.
- [x] T13 Sólido del tamaño del cuadro en un clic.
- [x] T14 (sin cambio: por decisión de Jorge todas las animaciones incluidas llevan llama y piden cuenta) Animaciones: filtro «Sin cuenta» / las libres primero.
- [x] T15 Squash & Stretch letra por letra (con T3 + escalonar).

F1–F3 esperan la build: se añadió `FLIP_TRACE_CLICKS=1` (main.cpp) que escribe en stderr cada pulsación con la pila
de elementos bajo el puntero, el foco y quién se queda la pulsación; con eso se busca la causa en ventana.

Prueba final (Jorge, 2026-10-31): **15 proyectos** en ventana (no 10) + las 5 animaciones de Squash a mano con
fotogramas clave; cada proyecto guardado en `pruebas\proyectos-029c\`. El inicio de sesión de las animaciones con
llama se queda como está (Jorge: «es un pequeño esfuerzo que el usuario va a hacer una sola vez»).

### Los 15 proyectos de la prueba final (con el mouse, como un usuario; portable `pruebas\FlipStudio-0.29-prueba-g`)
1. Banda roja que se dobla al entrar con su título doblándose junto (Doblar juntas, sin recorte) — F4, T11.
2. Tercio inferior con Barrido desde la izquierda, línea con la herramienta Línea, sólido de fondo y color de fondo — T1, T6, T12, T13.
3. Título que salta letra por letra (Dividir en letras + Squash «Aplicar letra por letra») — T3, T15.
4. Tres formas que se funden en un logo visible desde el principio (Morph) — T4.
5. Chorro líquido que dibuja una firma — F5.
6. Logo que se dibuja con Recorte (Fotogramas recordados) y Curvas con aviso — F10, F12.
7. Pelota que salta lejos (Recorrido 250 %) y se borran las claves sobrantes con «Después del cabezal» — T9, T10.
8. Cita en cursiva sobre fondo claro (texto nuevo legible, cursiva sintética) — F8, T8.
9. Composición con Elipse, Línea, barra fina y un rectángulo empezado fuera del cuadro; relleno desde la barra con Selección — T6, F9, F13.
10. Logo de dos piezas separado en capas y animado por partes — T5.
11. Tercio inclinado (Laureen) con Barrido inclinado — T1.
12. Duplicados en Pro (Ctrl+D encima) para un eco de texto — T7.
13. Anclaje en la esquina con la cuadrícula 3×3 y una barra que crece desde la izquierda — T2.
14. Intro con fondo sólido, título con animación de llama (con la sesión de Jorge) y Barrido de salida.
15. Arrastrar capas, textos y máscaras con el mouse por el lienzo, en varios proyectos — F2.

### Las 5 animaciones de Squash & Stretch hechas a mano (fotogramas clave, desde cero)
A1 Caer (cae, se aplasta al tocar el suelo, rebota y se asienta). A2 Entrar rebotando. A3 Salto hacia adelante.
A4 Aparecer de golpe. A5 Latido. Cada una se compara a ojo con la del panel de Squash & Stretch.

### Prueba final, primera tanda (portable prueba-g, build f368180; FLIP_TRACE_CLICKS + QT_LOGGING_RULES=default.info=true)
- [p] P1 banda + título doblándose juntos (T11), sólido de fondo (T13), color de fondo sin «#» (T12, F11), arrastre de
  texto con el mouse (F2), texto nuevo grande (F8), barra con Selección (F13). **Jorge vio la punta cortada** a ~35°:
  el margen de Doblar subía con el ángulo y se quedaba corto → ahora reserva el largo entero (`percentFactor` 5).
- [p] P2 tercio con Barrido (T1) y herramienta Línea (T6). Fallos nuevos: **el botón de Rectángulo se quedaba en Línea**
  tras pulsar Línea (arreglado: vuelve a Rectángulo); **texto nuevo blanco sobre etiqueta blanca** (capturaba la capa
  transparente: ahora la ventana entera); las tarjetas de Barrido no muestran el barrido en su miniatura (pendiente
  menor); el campo de color del texto con triple clic deja «##» (pendiente menor).
- [p] P3 «SALTA» letra por letra (T3, T15): bien; la ventana tarda ~2 s en refrescar tras dividir.
- [p] P4 Morph con destino visible (T4). **Jorge: el círculo reacciona antes de que lleguen** (la clave del golpe valía
  desde el principio) → ahora espera quieto; y **pidió controlar la reacción**: «Momento de la reacción» (−15…+15 fot.)
  e «Intensidad de la reacción» (0–300 %).
- [p] P5 firma con Chorro líquido (F5): dibuja la línea detrás del chorro y respeta el color.
- **F1, causa encontrada:** el fondo oscuro de los diálogos (`ThemedDialog` `Overlay.modal`) tenía un MouseArea que
  aceptaba todo; la animación de salida se trababa segundos y ese fondo invisible quedaba encima comiéndose clics,
  incluso los del diálogo siguiente. Arreglo: sin animación de salida (`exit: null`, también en NewTrackMenu y
  RecentProjectsPopup) y el MouseArea solo con el diálogo abierto. Además el selector de color no aplicaba el hex
  escrito (`validHex` iba un paso atrás).
- Pendiente de ver con la build nueva: el clic perdido en la pestaña Texto justo tras escribir un texto (registro
  `[tab]` con la pila).

### Herramientas para tercios inferiores (Jorge, 2026-11-01: «dale a los 7»)
- [ ] L1 Etiqueta que se ajusta al texto (forma vinculada a un texto + margen; crece al cambiar el nombre).
- [ ] L2 «Mostrar solo dentro de la capa de abajo» en un clic (mate de la etiqueta).
- [ ] L3 Escalonar las animaciones de entrada/salida entre las capas elegidas.
- [ ] L4 Barrido de dos colores (acento delante, etiqueta detrás).
- [ ] L5 Rectángulo con inclinación.
- [ ] L6 Alinear y distribuir.
- [ ] L7 Generador «Tercio inferior» (estilo + nombre + cargo → capas animadas y editables).
Además (de la prueba): Escala X/Y en % [x]; valores de los deslizadores escribibles; «##» en el campo de color;
miniaturas de Barrido; el diálogo de relleno que cambia de tamaño; rectángulo empezado fuera del cuadro;
clic en la pestaña Texto tras escribir.

### Segunda tanda (portable prueba-i, build a9d78d9), con el mouse
- [p] F1: el primer clic después de un diálogo ya no se pierde (dibujar justo tras «Aceptar» funciona).
- [p] Diálogo de relleno: «Ninguno» deja la fila de color en gris, el tamaño no cambia.
- [p] Morph con destino visible + salpicadura: la reacción y las gotas llegan en el impacto (`p04b-morph`).
- [p] L1 etiqueta ajustada al texto, crece con un nombre más largo; L2 nombre solo dentro de la etiqueta; L4 barrido de
  dos colores (`lt02-manual`); L5 inclinación; L3 escalonar + barrido inclinado en las dos capas (`lt03-inclinado`);
  L6 alinear y repartir (`lt04-alinear`).
- Fallos encontrados y arreglados (para la build siguiente):
  - **Generador de tercios:** las entradas iban al slot «in» (es «animIn»): nada se animaba; el cargo quedaba fuera de
    la etiqueta → ahora es la segunda línea del nombre (más chica, en su color) y la etiqueta envuelve las dos.
  - **Guías:** con Texto/Forma/Pluma, un clic sobre una guía la agarraba y no dibujaba nada → solo con Selección.
  - **Barrido inclinado:** el borde se inclinaba al revés que la etiqueta (−14° → 14°).
  - **Rombo de clave:** sin claves, la fila tomaba el valor por defecto (0) y la clave salía en 0 (la pelota saltaba
    arriba); y la clave suelta en el inicio no encendía el cronómetro, así que lo escrito después no hacía claves.
  - La ventana tarda en redibujarse con clics simulados (el clic llega; el panel se ve tarde). Con el mouse real no
    pasa; se deja anotado.
- [p] A1 «Caer» a mano con claves de Y y Escala X/Y en % (`a1-caer`).

### Tercera tanda (portable prueba-j, build d035002), con el mouse
- [p] L1 la etiqueta crece con «Ana María Gómez» y se encoge con «Bo»; L2 + L4 animado como el ejemplo (`lt05-demo`).
- [p] Fondo del proyecto transparente (alfa): textos traducidos a los 15 idiomas (`6f748`).
- [p] A2 «Entrar rebotando» (`a2-rebote`): X −150 → 900 → 800 → 855 → 835 y Escala X/Y estirada en el viaje
  (125/80, 130/78) y aplastada al frenar (75/125 → 110/92 → 96/104 → 100).
- [p] A3 «Salto hacia adelante» (`a3-salto`): anticipación, arco con la Y en «Suave», aterrizaje aplastado.
- Fallos encontrados:
  - **Filas que parecían animadas sin estarlo** (arreglado, `d6e4b`): toda capa guarda su posición/tamaño como una
    clave suelta en el inicio; la fila la mostraba como animada (rombo azul, flechas), pero lo escrito en otro
    momento solo cambiaba el valor, y pulsar el rombo en el inicio **borraba** esa clave. Ahora esa clave se marca
    `static` y la fila se ve sin claves: el rombo empieza la animación, como en After Effects.
  - **Escala X/Y de una forma nueva salía en 11 % / 19 %** (la medía contra el lienzo, porque el interruptor de
    escala separada se recuerda entre capas). Arreglado (`b667f`): sin referencia, el 100 % es su propio tamaño.
  - Clic en la regla justo sobre el cabezal no lo mueve (agarra el cabezal): en las pruebas, usar la tecla Inicio.
- **Barrido de colores con hasta 3 colores** (Jorge, 2026-11-01): «Segundo color» y «Tercer color» opcionales en
  Forma › Barrido de dos colores; entran en cascada (el primero más al fondo) y la etiqueta llega al final encima.
  Prueba `colourWipeTakesUpToThreeAccents`.
- **Tercios con entrada y salida** (Jorge, 2026-11-01: «igual que la herramienta de barrido»): el generador pone a
  cada pieza su entrada (`in-…`) y la misma salida de vuelta (`out-…`); el barrido de colores sale al final de la capa
  en orden inverso (la etiqueta primero, el primer acento al final), con «Salida también» (activado por defecto).
- **Escala X/Y desde el anclaje** (`setClipScaledSize`): antes encogía hacia la esquina de arriba a la izquierda.
- MCP para probar sin mouse: `create_lower_third`, `make_text_label`, `show_inside_below`, `colour_wipe`,
  `stagger_clips`, `scale_about_anchor`.
- Extras publicados (2026-11-01): `fonts.basic` 1.1.0 y `fonts.extra` 1.2.0 (paquetes primero, después el índice).

### Prueba final sin mouse (Jorge, 2026-11-01: «ya no necesitas usar el mouse»), build 01f98d0, por MCP
Programa `pruebas\mcp029\run029.py`: una sesión sin ventana por proyecto, guardado en `proyectos-029c` con su hoja.
- [p] lt06–lt10: el generador en sus 5 estilos (Limpio, Con línea, Inclinado, Dos colores, Cargo en barra), con entrada
  y salida (comprobadas de 3,6 a 5 s en lt07, lt09 y lt11).
- [p] lt11: texto + etiqueta ajustada + solo dentro + barrido de **tres colores** (entra amarillo, azul, blanco; sale al
  revés). lt12: la etiqueta crece de 164 a 1116 px al cambiar «Bo» por un nombre largo. lt13: fondo transparente.
  lt14: dos tercios seguidos. lt15: etiqueta a mano con barrido inclinado.
- [p] A4 «Aparecer de golpe» y A5 «Latido» con `scale_about_anchor`: crecen y se aplastan desde el centro.
- [p] P11 Laureen (la inclinación por MCP faltaba: `set_shape_style` no conocía `skew`; arreglado en `24d6d`) y P14
  intro con barrido de entrada y salida. A2/A3 se hicieron con el mouse (`a2-rebote`, `a3-salto`).
- Stock publicado (2026-11-01): 37 tercios (`llt-*`, `llt2-*`, `llt3-*`) con `minAppVersion` 0.29.0, en 13 idiomas;
  1531 plantillas en vivo, zips comprobados por hash.

### Últimas pruebas en ventana (build 24d6d0f, con el mouse, 2026-11-01)
- [p] Generador de tercios (Dos colores) con entrada y salida en la vista previa (`lt16-ventana`).
- [p] Forma › Barrido: «Segundo color», «Tercer color» y «Salida también»; barrido de tres colores aplicado desde la
  ventana sobre una etiqueta hecha con «Hacer una etiqueta para este texto» (`p15-arrastrar`).
- [p] F3: texto con la herramienta Texto, Esc, Selección, «Comienza en» = 0,5: el texto sigue intacto.
- [p] F2: un texto recién creado se arrastra entero al primer intento.
- [p] P15: arrastrar textos, un rectángulo y una máscara de círculo sobre una foto (`p15-arrastrar`).
- [p] Guías: con la herramienta Texto, un clic sobre una guía crea el texto (no agarra la guía).
- [p] Dividir en letras + Motion Tools › Secuencia (solo en Pro; en Simple está Animación › Escalonar). Jorge: «funciona».
- Arreglado tras esta tanda (`8e401`, `b5b94`): arrastrar una capa **sin elegirla antes** (la de arriba bajo el
  puntero, como CapCut y After Effects; antes solo se elegía); un clic junto al cabezal lo mueve ahí; el sólido toma el
  color de fondo de arriba; los cuadritos de color tienen borde gris (el del Texto no se veía en el diálogo de tercios);
  cuadrícula del anclaje de 54 px.
- **Entrada y salida a elegir en el generador de tercios** (Jorge, 2026-11-01): Automática (la de cada estilo),
  Barrido, Deslizar, Aparecer, Zoom, Desvanecer o Ninguna, para la entrada y para la salida (`entrance` / `exit`).
  Trampa evitada: en un diálogo no se puede llamar `exit` a una propiedad (es la transición del Popup).
- **Dos acentos más, opcionales, en el generador de tercios** (Jorge, 2026-11-01): «Segundo acento» y «Tercer acento»;
  con ellos la etiqueta de cualquier estilo entra con el barrido de colores en cascada (`accent2Color`, `accent3Color`).
- **Jorge (2026-11-01), fallo:** al achicar el nombre la barra amarilla («Con línea») se quedaba con el alto viejo.
  Ahora la barra está atada al texto como la etiqueta (`Clip::fitBarWidth`, guardado en `fitText.bar`).
- **Alineación en el generador** (Jorge): Izquierda, Centro, Derecha: las líneas del texto y el tercio entero en el
  cuadro; a la derecha la barra va al lado derecho de la etiqueta (`fitBarWidth` negativo).
- Prueba en ventana (build 8173b9f): diálogo de tercios con Segundo acento, Entrada, Salida y Alineación; el cuadrito
  del Texto ya se ve; Derecha pone el tercio y la barra a la derecha; el sólido toma el color de fondo; el clic al lado
  del cabezal lo mueve (si hay una clave cerca, el imán lo lleva a ella); cuadrícula del anclaje más grande.
- **Fallo encontrado:** un toque en el lienzo lo recibían todas las cajas bajo el puntero y ganaba el sólido del fondo
  (un tercio sobre un sólido no se podía elegir ni editar con doble clic). Ahora solo responde la capa de arriba, y el
  arrastre también mueve la capa de arriba bajo el puntero aunque haya otra elegida (`8a1b3`, `70c66`, `5496f`).
