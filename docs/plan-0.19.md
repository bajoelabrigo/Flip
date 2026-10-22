# Plan de la 0.19.0 — máscaras en textos, textos 100 % editables, seguimiento como CapCut

Rama `flip/v0.19.0` (sale de `main` = 0.18.3), en la copia de trabajo `codigo\Flip-v019` (`git worktree`), para no
mezclarla con `flip/stock-tendencias-texto`, que solo tiene herramientas de Stock.

Pedidos de Jorge (2026-10-21):
1. «Las máscaras en los textos quedó pendiente».
2. «Que todo absolutamente de los textos se pueda editar, de manera que los usuarios puedan usar nuestros textos
   para crear los propios».
3. «El seguimiento de rostro o cámara como el que tiene CapCut y Filmora, no sé si está funcionando».

## 1. Máscaras en textos — HECHO (falta probar en ventana)
- Auditoría: el motor ya dibujaba las máscaras de un texto, pero la interfaz lo bloqueaba (sin `maskable` en
  `inspectorCaps`, `linkedMaskClips` solo para video/imagen, `MasksTab.qml` excluía texto y subtítulos).
- «Texto como forma de máscara» ya existía (`MaskShape::Text`): la nota de pendiente era vieja.
- Arreglos (`131a9`):
  - Texto y subtítulo son `maskable`; la lista y el panel de máscaras los aceptan.
  - `FrameCompositor::masksInLayerFrame`: la máscara se coloca sobre la caja del texto (donde la vista previa dibuja
    las asas), no sobre la imagen con margen (bordes, sombras, animación). Sin esto el corte salía corrido y estirado.
  - Prueba `EditorStateTest::textClipTakesMasks`.
- Probado en ventana (2026-10-21): la pestaña Máscaras sale con un texto (con Texto como forma) y un rectángulo
  sobre la mitad izquierda corta «MASCARA» justo en el centro del lienzo. Falta mirarlo con borde grueso y animación.
- Web: no tiene máscaras en textos (`inspectorTabs.ts`, `textLayer.ts`, y el `.flip` las pierde). Pendiente.

## 2. Textos 100 % editables — HECHO en el escritorio (falta probar en ventana)
Auditoría campo por campo de los 590 estilos de Stock contra el inspector. Ya se podía casi todo y «Guardar como mi
estilo» guarda el estilo entero. Huecos cerrados (`38dad`):
- **Forma de la caja** (Fondo › Forma): cambia solo la forma; la galería Burbuja sigue reemplazando el look entero.
- **Interruptores de las animaciones** (cursor de la máquina de escribir): se guardan como 0/1 y el botón buscaba
  `true`; siempre salía apagado y no se podía quitar.
- **Curvas**: faltaban «Suave» (`smooth`) y «Acelerar» (`easeIn`), que usan 644 ranuras de Stock.
- **Tinte de los efectos de relleno** (brillo, neón, cromo): `PaintEditor` solo mostraba color para sólido.
- **Desplazamiento X/Y en todas las capas** (no solo sombra): separación RGB, fantasma, estela.
- **Pasos de la extrusión**.
- **Píldora del acento**: relleno y radio; **desfase** del acento («empezar en la palabra»).
- Rangos: ancho de la caja hasta 200 %, tamaño del acento desde 0,2, altura de «lluvia» negativa.
- **Actualizar un estilo propio** con el texto seleccionado (`TextPresetStore::update`, menú de Mis estilos).
- **Animaciones propias**: «Guardar como mi animación» (`saveTextAnimationAsPreset`, categoría «Míos») y menú con
  Renombrar, Exportar y Borrar en las tarjetas `user:` (el C++ existía, nadie lo llamaba).
- Pruebas: `CoreTest::userTextPresetsRoundTrip` (update), `EditorStateTest::textAnimationSavesAsOwnPreset`.
- Traducciones hechas (`dd7bb`). **Falta:** probar en ventana.
- Menores sin hacer: instalar el mismo estilo de Stock dos veces crea un duplicado; la importación ignora
  `names.en`/`sampleTexts`.
- Web: instala los estilos de Stock simplificados (solo la primera capa de cada tipo, sin efectos ni acento). Pendiente
  decidir: ampliar su modelo o avisar.

## 3. Seguimiento (CapCut / Filmora) — HECHO en el escritorio y probado en ventana
Auditoría previa: no existía en ninguna de las dos apps (solo el escaneo de caras para los efectos `face_*`,
`auto_reframe` por MCP y estabilizar).

Hecho (`398f3`):
- **`engine/RegionTracker`**: sigue un rectángulo de fotograma a fotograma (correlación normalizada sobre una copia
  gris pequeña, de grueso a fino con los 8 mejores candidatos, pico sub-píxel, escala ±4 % opcional, plantilla que se
  adapta despacio, penaliza los picos lejanos para no saltar a la repetición de un patrón, y «perdido» por debajo de
  0,35 que mantiene la última posición). Probado con un programa aparte (`pruebas\tracker-test`, MinGW 13.1 de
  `pruebas\qt-tools`): error < 1 px en movimiento lento y rápido, escala ±4 %. Prueba `EngineTest::regionTrackerFollowsAMovingPatch`.
- **`models/MotionTrackController`** (`EditorState.motionTrack`): el elemento seleccionado (texto, imagen/sticker,
  forma, vector, composición) sigue al video que tiene **debajo** (pistas de índice mayor). Modo **Objeto**: lo que
  el elemento tapa en el cabezal; modo **Rostro**: la cara escaneada (si no hay escaneo, lo lanza y sigue al
  terminar). Hacia adelante y hacia atrás desde el cabezal, en el tramo donde se solapan. Se hornea en fotogramas
  clave de posición (y tamaño) cada 2 fotogramas, suavizado, en un paso de deshacer. «Quitar seguimiento» deja una
  posición fija. Los **textos** siguen solo la posición (cambiar el tamaño de su caja no agranda las letras).
  Prueba `EditorStateTest::motionTrackingKeysTheElementOverItsVideo` (con una foto, sin decodificador).
- **Interfaz:** sección «Seguimiento» al final de Transformar (`MotionTrackSection.qml`), con Objeto/Rostro,
  «Seguir también el tamaño», barra de progreso y Cancelar.

**Probado en ventana (2026-10-21, build run 39691308647, portable en `pruebas\FlipStudio-0.19-prueba`, archivos en
`pruebas\track-test`):**
- **Objeto:** un texto sobre el piloto de `parapente120.mp4` lo sigue en todo el clip (capturas en 2,1–6,8 s).
- **Rostro:** sin escaneo previo, «Iniciar seguimiento» escanea las caras (~50 s para 20 s de video) y sigue solo
  hasta «Seguimiento listo»; 63 claves de X/Y cada 0,08 s y «YO» queda sobre la cabeza de `retrato.mp4`.
- Ojo al probar: si el texto ya tiene claves de ancho/alto (fotogramas automáticos al colocarlo), siguen ahí, porque
  en un texto el seguimiento solo toca la posición.
- Traducciones de los 15 idiomas hechas (`e8f3a`).

**Falta:**
- Difuminar/pixelar una cara o un objeto siguiéndolo (CapCut «Mosaico»): reutilizar el seguidor para mover una
  máscara de una capa de ajuste con desenfoque.
- Web: no tiene seguimiento.

## 4. Títulos › Tendencias como CapCut (pedido de Jorge, 2026-10-21)
Jorge buscaba los 391 estilos «Tendencias» en el panel Títulos (sus capturas eran de CapCut, Títulos › Tendencias);
solo estaban en Stock › Estilos de texto. Y al bajar uno desde Stock el aviso decía «se agregó a Medios» y «Ver»
llevaba a Medios: el estilo se instalaba en Texto › Mis estilos.
Hecho (`ef885`, traducciones `a53a6`):
- **Títulos › Texto › Tendencias** (primera sección, la de entrada): todos los estilos de texto de Stock (los de
  tendencia primero, como los ordena el servidor), página a página (`MarketClient::fetchTextTrends`, `textTrends`).
  Tarjeta cuadrada con la vista previa animada al pasar el mouse (`StockThumb`) y el icono de descarga si falta;
  un clic la baja y la pone en el cabezal; ya bajada, clic o arrastre como cualquier estilo. Pide cuenta (aviso
  con «Iniciar sesión»).
- **Un estilo de Stock recuerda su id** (`TextPreset::stockId`, `TextPresetStore::idForStockId`): bajarlo otra vez lo
  actualiza en vez de duplicarlo, sale en Tendencias y no en Mis estilos. Prueba en `CoreTest::userTextPresetsRoundTrip`.
  Los que Jorge bajó antes de esto no tienen el id: siguen en Mis estilos.
- **Aviso al instalar** (LUT, look, estilo, animación, transición, forma): `downloadInstalled(itemId, name, where)`
  dice dónde quedó («En Títulos › Tendencias») y «Ver» abre Títulos › Tendencias.
- **Stock:** las categorías de nuestros catálogos salen como botones (Todo, Tendencias, Subtítulos…), no solo detrás
  de Filtros, y Estilos de texto entra en **Tendencias**.
- **Falta:** probar en ventana con la cuenta (compilación run 39701007841).

## 5. Seguimiento profesional (pedido de Jorge, 2026-10-21) — PLAN
Jorge pasó un pliego hecho con ChatGPT (pensado para C#/.NET) y una captura de CapCut (Texto › pestaña
«Seguimiento»: casilla, Ninguno / Seguimiento de cuerpo, Dirección «Ambos», Escala y Distancia). Pidió adaptarlo a lo
nuestro. Lo que sigue es ese pliego traducido a la app real.

### Lo que ya hay (auditoría)
- Qt 6.10 + C++20 + QML; motor de Drift. Vista previa y exportación usan el **mismo compositor**
  (`FrameCompositor`/`GpuLayer`, con camino de CPU): todo lo que se hornea en fotogramas clave sale igual al
  exportar, sin código aparte.
- Fotogramas clave: `KeyframeTrack<double>` en posición/tamaño/giro del clip, en `mask.x|y|w|h|rotation|feather` y
  en los parámetros de efectos; relativos al inicio del clip; se guardan en el proyecto.
- Decodificación: `ClipReaderPool::readVideoFrame` (FFmpeg) al tamaño pedido; nunca el video entero en memoria.
- IA local con ONNX Runtime (`drift::ort::buildSessions`: DirectML/CUDA con vuelta a CPU). Rostros: MediaPipe
  (Apache 2.0, ya distribuido) en `FaceTrackingController` → `FaceTrack` (archivo aparte por clip, una ranura por
  cara; detecta y luego sigue por ROI, y vuelve a detectar al perderla: el sistema híbrido que pide el pliego).
  SAM 2.1 ya está (Quitar fondo) y sigue un objeto en todo el video con su contorno.
- Objetos: `RegionTracker` (correlación normalizada, CPU, con pruebas) de la 0.19.
- `MotionTrackController`: hilo aparte, progreso, cancelar, hornea posición (y tamaño) cada 2 fotogramas,
  suavizado, un solo paso de deshacer.
- Efectos para tapar: `stylize_pixelate`, `gaussian_blur`; capas de ajuste enlazadas a un clip (carril
  `ParentTrack`), con máscaras medidas sobre el marco del clip.

### Lo que falta frente al pliego
- Elegir **qué cara** (hoy siempre la ranura 0) y verla en el visor.
- Ver en el visor el objetivo seguido y su estado (seguido / perdido / recuperado).
- Objeto perdido: hoy se queda quieto; falta **volver a encontrarlo** sin saltar a otro parecido.
- Dirección (adelante / atrás / ambos), **Distancia** (mantener la separación o centrarse encima) y recalcular
  desde un fotograma.
- **Guardar los datos del seguimiento** (hoy solo quedan las claves): sin ellos no se puede cambiar Escala o
  Distancia sin volver a analizar, ni marcar los tramos perdidos, ni reacomodar si se mueve o recorta el video.
- **Aplicarlo a otras cosas**: difuminar/pixelar una cara (Mosaico de CapCut) y que una máscara siga al objetivo.
- Pestaña propia «Seguimiento» como CapCut (hoy es una sección al final de Transformar).

### Decisiones
- Nada de .NET ni OpenCV (sería una dependencia enorme para lo que ya hacen `RegionTracker` y MediaPipe).
- **Detector de categorías (personas, autos, animales):** necesita un modelo nuevo. YOLOv8/11 de Ultralytics es AGPL
  (fuera). Candidatos Apache 2.0: YOLOX o RT-DETR en ONNX (~20–40 MB) como extra. Queda para el final y se le pregunta
  a Jorge antes; mientras, el objeto se marca con el propio elemento (como CapCut) o con un recuadro.
- Los datos se guardan en **tiempo del video de origen** y coordenadas **normalizadas del fotograma de origen**
  (0..1): si el video se mueve, se recorta o cambia de velocidad, se vuelve a hornear sin analizar
  (`Clip::sourceUsToClipLocalUs`). Las claves siguen siendo el resultado: vista previa y exportación no cambian.

### Fases
1. **Datos y motor.** `drift::MotionTrack` en el clip que sigue (modo, id del video, ranura de cara, dirección,
   escala, distancia, referencia, muestras {tiempo de origen, rectángulo, confianza, estado}), en el JSON del
   proyecto con versión (los proyectos viejos no cambian). Horneado aparte (`bakeMotionTrack`), que sirve para
   rehacer las claves al cambiar Escala/Distancia o al mover el video. Cara elegida (por defecto la más cercana al
   elemento) con control de identidad para no cambiar de persona. Objeto: búsqueda amplia al perderlo, aceptada
   solo con un pico claro (no otro objeto parecido). Pruebas con datos sintéticos: quieto, lateral, escala,
   oclusión, sale y vuelve, objetos parecidos, cancelar.
2. **Interfaz como CapCut.** Pestaña «Seguimiento» para texto, sticker, imagen y forma: casilla, tarjetas
   Ninguno / Objeto / Rostro, Dirección, Escala, Distancia, restablecer, progreso y cancelar. En el visor: los
   rostros detectados para elegir con un clic, y el recuadro seguido con su estado; «Recalcular desde aquí».
3. **Aplicarlo a otras cosas.** «Difuminar rostro» (pixelado o desenfoque) en la pestaña Video: capa de ajuste
   enlazada al clip con una máscara elíptica que sigue la cara. «La máscara sigue» en Máscaras.
4. **Guardar y exportar.** Probar guardar y volver a abrir, exportar y comparar posiciones fotograma a fotograma; aviso
   y «Reacomodar» si el video se movió o recortó después del seguimiento.
5. **Rendimiento y cierre.** Memoria en videos largos, archivo dañado, modelo de caras ausente, error de
   inferencia; documentación y traducciones.

Cada fase: compilar en CI, pruebas, ventana. Las pruebas con video real usan `pruebas\web-videos\medios`
(`parapente120.mp4`, `retrato.mp4`, `modelos.mp4`).

### Estado (2026-10-21, noche)
- **Fase 1 HECHA** (`271d6`, CI: compila; EngineTest y EditorStateTest del seguimiento en verde):
  `core/MotionTrack` (datos + JSON versionado + `bakeMotionTrack` + `followFaceSlot`), `RegionTracker` con
  recuperación (plantilla original, búsqueda en todo el cuadro, se niega a saltar a un parecido presente desde el
  primer cuadro), `MotionTrackController::trackWith/setOption/realign/info/faceTargets/targetAt`. Texto con Escala:
  también se anima su tamaño de letra (`textStyle.keyframes["pixelSize"]`). Un re-horneado reemplaza toda la
  animación de posición (y tamaño).
- **Detector de objetos:** YOLOX-Tiny (Apache 2.0, 19,3 MB, ~27 ms/cuadro en CPU) — `engine/ObjectDetector` ya venía de
  Drift (detección de escenas), ahora con un candado entre hilos. Extra `seguimiento.objetos` (kind `object-model`,
  raíz `models/yolox-tiny`) preparado en `flip-addons` rama `extra/seguimiento-objetos` (`4bf23`), **sin publicar**.
  Probado aparte en `pruebas\object-detector` (README con el pre/posprocesado). Para probar la app sin el extra:
  `DRIFT_OBJECT_MODEL_DIR=pruebas\object-detector\stage-model`. «Detectar objetos» elige una caja; al perder el
  objeto se vuelve a detectar uno de la misma clase cerca y de tamaño parecido (cada 5 cuadros perdidos).
- **Fase 2 HECHA (sin compilar todavía):** pestaña «Seguimiento» (`TrackingInspector.qml`, cap `trackable`) con
  Ninguno/Objeto/Rostro, Dirección, Escala, Distancia, «Seguir de nuevo desde aquí», «Reacomodar», estado; visor
  (`preview/TrackingOverlay.qml`): recuadro seguido con color por estado, rostros y objetos para elegir con un clic y
  recuadro dibujado a mano (`MotionTrackController::chooser/pick/regionFromCanvas`). Se quitó la sección de
  Transformar (`MotionTrackSection.qml`).
- **Fase 3, parte hecha:** «Ocultar un rostro» (Pixelar / Desenfocar) en la pestaña Seguimiento de un video o foto:
  pista de ajuste encima con el efecto y una elipse que sigue la cara (`blurFace`). Falta: «la máscara sigue» a un
  objeto y ocultar un objeto (no solo caras).
- Además: cuadro de texto ajustado a las palabras (rama `flip/texto-ajustado`, `32bc0`, unida) y listas que ya no
  vuelven arriba al cargar la página siguiente (Stock y Tendencias).
- **Falta probar en ventana** todo lo de la fase 2 y 3 con la compilación nueva, y las fases 4–5.

## Estado de la compilación
- Ensayo `build.yml` (Windows) run 39685634394 sobre `38dad` (solo falló la prueba de traducciones, ya arreglada).
- Run 39691308647 sobre `e8f3a`: compila bien; `tests.yml` 17/17 en verde.
