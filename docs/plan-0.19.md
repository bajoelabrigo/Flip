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

## Estado de la compilación
- Ensayo `build.yml` (Windows) run 39685634394 sobre `38dad` (solo falló la prueba de traducciones, ya arreglada).
- Run 39691308647 sobre `e8f3a`: compila bien; `tests.yml` 17/17 en verde.
