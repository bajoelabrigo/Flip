# Editor web en celulares y tabletas, como CapCut (pedido de Jorge, 2026-10-21)

Jorge probó el editor web en su iPad y no podía elegir bien los efectos con el dedo. Pidió adaptarlo a
celulares y tabletas con el formato de la app de CapCut (capturas en `Downloads\WhatsApp Image
2026-10-21 at 11.15.26 … 11.18.42 AM.jpeg`): plantillas en cuadrícula con barra abajo, inicio de sesión,
y el editor con la vista previa arriba, la línea de tiempo con el cabezal fijo al centro y la barra de
herramientas abajo que cambia cuando tocas un clip.

Repo: `flipstudio-app`, rama **`web/movil`** (sale de `web/paridad-1`). Se despliega igual que siempre
(`deploy/deploy.sh`); el diseño táctil solo se activa en pantallas táctiles, así que en la computadora
no cambia nada.

## Cómo está hecho

- **No es otro editor:** el mismo `Editor` (`App.tsx`) reacomoda sus piezas cuando `useTouchLayout()`
  (`src/layout/touch.ts`) dice que sí. Todo lo que ya funciona (paneles de la biblioteca, secciones del
  inspector, exportar, deshacer) se reutiliza tal cual dentro de una **hoja inferior**.
- Cuándo se activa: Ajustes › «Diseño» = Automático (pantalla táctil sin mouse, o ventana angosta),
  Escritorio o Táctil. También en Ver › «Diseño táctil».
- **Línea de tiempo táctil** (`components/TouchTimeline.tsx`), como la de CapCut: cabezal fijo al centro,
  deslizar el dedo mueve el tiempo, pellizcar hace zoom, tocar un clip lo elige, mantenerlo presionado
  lo mueve, tiradores anchos para recortar, «+» al final para añadir medios, filas «+ Agregar audio» y
  «+ Agregar texto». Usa las mismas funciones de `timeline/tracks.ts` que la de escritorio.
- **Barra de abajo:** sin nada elegido, las categorías (Editar, Audio, Texto, Stickers, Efectos,
  Filtros, Transiciones, Plantillas, Stock, Subtítulos, Formato…); con un clip elegido, sus acciones
  (Dividir, Volumen, Velocidad, Animaciones, Efectos, Ajustar, Máscara, Recortar, Quitar fondo,
  Retoque, Duplicar, Eliminar…) con «‹» para volver.

## Etapas

1. **Editor táctil** — barra de arriba (cerrar, tamaño, Exportar), vista previa, fila de reproducción
   (pantalla completa, reproducir, deshacer/rehacer, tiempo), línea de tiempo táctil, barra de abajo y
   hoja inferior con los paneles. **Hecha y desplegada (2026-10-21, `flipstudio-app` `8ddf0`).**
2. **Al tacto en todo** — tarjetas que se aplican al primer toque (los efectos con antes/después al pasar
   el mouse necesitaban dos toques en el iPad), botones de 44 px, hoja que se arrastra, zona segura del
   iPhone, sin zoom de la página al tocar dos veces.
3. **Inicio como CapCut** — barra abajo (Editar, Plantillas, IA, Yo), plantillas de Stock en dos
   columnas con chips, y «Yo» con el inicio de sesión de Google.
4. **Pruebas** — Chrome con emulación de iPhone y iPad (toque), y Jorge en su iPad.

## Etapa 5: las 16 ideas (Jorge, 2026-10-21: «vamos a hacerlas todas… no dejes ni una pendiente»)

Orden de trabajo (de lo más rápido y útil a lo más grande). Cada una se marca al desplegarla.

- [x] 9. Textos «haz clic» / «panel de la derecha» → «toca» / «abajo» en pantallas táctiles.
- [x] 3. Vibración al pegarse a un borde o al cabezal, al levantar un clip y al llegar a 0 en un deslizador.
- [x] 10. Almacenamiento persistente (`navigator.storage.persist`) y aviso «guarda una copia .flip».
- [x] 14. Aviso antes de exportar un video largo o pesado en tableta/celular, con tiempo estimado.
- [x] 16. Guía rápida la primera vez (tres burbujas: tocar, mantener, pellizcar).
- [x] 11. Instalar como app (manifiesto, iconos, `apple-mobile-web-app`, service worker de red primero).
- [x] 12. Compartir al terminar de exportar (`navigator.share` con el archivo: Fotos, TikTok, WhatsApp).
- [x] 5. Importar desde Fotos en iPhone/iPad (selector solo de imagen y video) y videos HEVC del iPhone.
- [x] 4. Tocar con tres dedos = deshacer, con dos = rehacer.
- [x] 1. Vista previa con dos dedos: pellizcar = escala, girar = rotación, un dedo = mover (clips y textos).
- [x] 2. Guías magnéticas en la vista previa (centro y bordes) al mover con el dedo.
- [x] 7. Hoja de abajo que se arrastra (más alta o más baja).
- [x] 8. Vista previa a pantalla completa en el celular (doble toque o botón), también en iPhone.
- [x] 13. Vista previa liviana automática en tabletas (calidad automática y proxies para 4K).
- [x] 6. Inicio como CapCut en el celular (barra abajo: Editar, Plantillas, IA, Yo).
- [x] 15. Teclado externo y Apple Pencil en el iPad (atajos y lápiz como mouse).

Tanda 1 desplegada (2026-10-21): 9, 3, 10, 14, 12 y 16, con pruebas (`touchWords.test.ts`, `haptics.test.ts`,
`persist.test.ts`, `estimate.test.ts`) y probadas en Chrome emulando un iPad con Safari (sin `showSaveFilePicker`,
`navigator.share` simulado). Traducciones: **hechas** (2026-10-21, 85 textos × 15 idiomas, `--check` en 2845/2845). La herramienta
«Ajustar» usa en los otros idiomas la palabra de «Ajuste» (los catálogos traducen «Ajustar» como «encajar»), y la
línea de los términos es una sola frase con los enlaces entre corchetes.

Tanda 2 desplegada (2026-10-21): 11 (manifiesto, iconos, `sw.js` de red primero; nginx sirve el manifiesto como
`application/manifest+json`, snippet actualizado en el VPS), 5 (selectores solo de medios en iPhone/iPad,
`media/accept.ts`) y 4 (dos dedos = deshacer, tres = rehacer, como Procreate; `layout/gestures.ts`). Probado:
instalación con los pasos de Safari (agente de usuario de iPad), recarga sin internet desde el service worker,
deshacer/rehacer con toques simulados. **Trampa:** Chrome emulado reporta `maxTouchPoints` 1; un iPad real, 5.

Tanda 3 desplegada (2026-10-21): 1 (`preview/pinch.ts`, en `PreviewTransform.tsx` y los textos de `Preview.tsx`),
2 (los textos se pegan a bordes, centro y guías; la caja de los videos ya lo hacía; vibración al pegarse),
7 (`layout/sheetDrag.ts`, manija en `TouchSheet`) y 8 (pantalla completa propia donde no hay API: iPhone;
doble toque). **Trampa:** con punteros simulados `setPointerCapture` lanza `NotFoundError`; todo
`setPointerCapture` nuevo va en `try`, si no el gesto se corta en las pruebas.

Tanda 4 desplegada (2026-10-21): 13 (calidad «Automática» por defecto en pantallas táctiles y copia liviana de
videos de más de 1080p, `media/lightCopy.ts`), 6 (`PhoneHome.tsx`: Editar, Plantillas, IA, Yo) y 15 (Cmd + / =
atajos, ⌘/⌥ en teclados de Apple; el Apple Pencil arrastra como mouse y, quieto, abre el menú). Además, pedido de
Jorge: **«Instalar app» como en holyapp** (`Downloads\chat-app\holy_app\frontend\src\lib\installPrompt.js`): siempre
visible hasta instalarla, un clic donde el navegador puede y, si no, los pasos de Android, iPhone/iPad y computadora.
**Trampa:** las reglas de `touchWords.ts` del celular cambian «arriba a la derecha» por «el menú ⋯»: un texto que
hable de otra cosa (el menú de Chrome) no debe usar esa frase.

Arreglos tras probar Jorge en el iPad (2026-10-21, desplegados): con efecto o LUT, un video 4K o una foto del
iPhone se veía a un cuarto (los efectos corren en un lienzo de 2048 px como máximo y se recortaba con las medidas
del original: `compose.ts › effectPicture`; afectaba también a la exportación); el cabezal ya pasa del último clip;
con proyecto vertical el separador horizontal ya no cruza la vista previa. **Trampa:** probar siempre con material
de más de 2048 px (4K, fotos de 12 MP): con videos chicos el fallo de los efectos no se ve.

Audio en iPhone/iPad (2026-10-21, desplegado): no sonaba lo insertado porque Safari solo deja sonar un elemento de
medios que se reprodujo dentro de un toque, y el editor los arranca silenciados y los activa desde su reloj. Al tocar
Reproducir se crean y desbloquean todos (`useSequencer.ts › unlockAudio`), se reanuda el AudioContext y
`navigator.audioSession.type = "playback"`. Avisos al agregar música/sonidos («Agregando…» y «… está en la línea de
tiempo, en 0:05»). **Confirmado por Jorge en su iPhone y iPad (2026-10-21).**

Sonido robótico en iPhone/iPad (2026-10-21, desplegado): el reproductor cambiaba la velocidad de cada elemento en
cada cuadro (±10 %) para seguir el reloj; Safari da currentTime a saltos y re-estira el audio en cada cambio (ignora
`preservesPitch`, usa `webkitPreservesPitch`). Ahora velocidad exacta dentro de 0,12 s de desfase, ±3 % como mucho
fuera (`steeredRate`, con pruebas). **Trampa:** no tocar `playbackRate` de un elemento que suena en cada cuadro.
Android revisado en emulación (diseño, instalar, audio, avisos); su selector de archivos también pide solo medios.

Pasar de categoría con el dedo (2026-10-21, desplegado, `flipstudio-app` `f3535`): en el iPad, al bajar hasta el final de una lista (Efectos, Transiciones, Títulos, Stickers…) no se abría la categoría siguiente porque `useCategoryScrollOn` solo escuchaba la rueda del mouse. Ahora, seguir arrastrando ~110 px pasado el final llena la píldora «Sigue bajando para ver …» y al soltar abre la siguiente; desde arriba, tirar hacia abajo vuelve a la anterior. Probado con toques simulados en Chrome (iPad emulado).

## Estado

- 2026-10-21: **etapa 1 desplegada** en getflipstudio.com/editor (rama `web/movil`, commit `8ddf0`). Probado en
  Chrome con emulación de iPhone (390×844) y de iPad horizontal (1180×820): añadir con «+» (van uno tras otro),
  deslizar = mover el tiempo, tocar = elegir, pulsación larga = mover (con desplazamiento al borde), recortar con
  los tiradores (la pista principal cierra huecos), pellizcar = zoom, efecto aplicado al **primer toque**, y todas
  las hojas (Medios, Audio › Música, Texto, Stickers, Plantillas › Escenas, Filtros, Efectos). En la computadora
  el editor no cambia. 366 pruebas, `tsc` y `vite build` bien.
- **Causa del problema del iPad:** en las tarjetas, la estrella de favoritos y el antes/después salían solo con
  `:hover`; en iOS el primer toque solo «pasa el mouse» y hacía falta otro. Con `@media (hover: none)` se ven
  siempre (vale también para el diseño de escritorio en una tableta).
- **Safari no puede volver a abrir un archivo elegido** tras recargar (no hay `showOpenFilePicker`): ahí los
  bytes se guardan con el proyecto (`useProject.ts › canReopenFiles`), igual que lo que entra con el «+».
- **Ajustar como CapCut** (capturas `Downloads\ajustes*.jpeg`, desplegado): una hoja con Predefinidos (efectos de
  color), Filtros (LUTs), Ajustar (botones redondos + un deslizador, `AdjustSection.tsx › TouchAdjustPage`) y
  Calidad del video (Mejorar video, Estabilización, Reducir ruido del audio).
- **iPad = diseño de escritorio (Jorge, 2026-10-21, captura `Downloads\43067.jpg`):** CapCut en el iPad es su editor de
  escritorio. El diseño táctil queda solo para celulares (`touch.ts`: menos de 700 px de ancho, o dedo y menos de
  500 px de alto). En la tableta, la línea de tiempo de escritorio acepta el dedo (`Timeline.tsx`: toque = elegir,
  deslizar = desplazar, mantener = mover, pellizcar = zoom, toque en el fondo = cabezal) y en vertical todo entra
  en una pantalla (vista previa arriba, biblioteca y propiedades al medio, línea de tiempo abajo). Desplegado.
- **Jorge en su iPad (2026-10-21), arreglado y desplegado:** mover el tiempo con el dedo lo sacaba del editor
  (Safari tomaba el deslizamiento como «atrás»: la regla y los tiradores lo retienen, sin rebote de página y con
  un paso de historial propio en pantallas táctiles); mantener presionado = clic derecho (`layout/longPress.ts`,
  clips y Medios); y «Borrar» del menú «…» de un proyecto no hacía nada (el menú se cerraba con `pointerleave`,
  que el dedo dispara al levantarse, antes del toque: ahora solo con mouse).
- **Trampa:** en iOS, `onPointerLeave` de un menú se dispara al levantar el dedo, antes del `click`: no cerrar
  menús así salvo con `e.pointerType === "mouse"`.
- Falta (etapa 2): textos de ayuda que dicen «haz clic» o «panel de la derecha», arrastrar la hoja para
  agrandarla, mover textos y stickers con dos dedos en la vista previa, el teclado de iOS al escribir un texto,
  y probarlo en el iPad de Jorge. Etapa 3 (inicio con barra abajo) sin empezar.

## Etapa 6: herramientas como CapCut (Jorge, 2026-10-22, capturas `Downloads\WhatsApp Image 2026-10-22 at 12.14.25 … 1.04.13 AM.jpeg`)

Desplegado el 2026-10-22 (`flipstudio-app` rama `web/v019`, commit `e4ac1`). Pedido: «botón de keyframe + / −, curvas,
restaurar; las máscaras en una fila que no tape el video ni la línea de tiempo; después simula que editas y corrige».

- **◇+ / ◇−** en la fila de reproducción (`timeline/quickKeys.ts`): con un video, foto, texto o audio elegido, un toque
  pone un fotograma clave de todo lo animable en el cabezal (lugar, tamaño, giro, opacidad; en audio, el volumen) y
  cerca de un rombo lo quita. **El rombo bajo el cabezal se pinta rojo y más grande** (pedido de Jorge), los demás blancos.
- **Curvas** (`TouchCurves.tsx`): 17 curvas para el tramo entre los dos fotogramas del cabezal; tocar de nuevo la
  elegida = «Editar», una curva propia con dos puntos. Se guardan como `Keyframe.curve` (cubic-bezier) y al `.flip`
  van como las asas del escritorio (`desktopTransform.ts › track`). «Restaurar» de CapCut = deshacer, que ya estaba.
- **Máscara** en una fila (`MaskPage.tsx › TouchMaskBar`) con Invertir · Máscara · ajustes · ✓; en la vista previa el
  **anclaje amarillo al centro** y el **manejador de difuminado** (⇣) que Jorge pidió, de tamaño para el dedo.
  Mientras está abierta solo se ven los manejadores de la máscara. Textos con Máscara y Seguimiento.
- **Transformar** (`TouchTransform.tsx`): Reflejar, Girar (cuarto de vuelta) y Avanzadas con Posición / Zoom / Girar en
  reglas que se arrastran, Restablecer y ✓. Respeta los fotogramas clave.
- **Animaciones** con Entrada / Salida y tarjetas que muestran la animación (`TouchAnim.tsx`); **Recortar** abre el
  recorte (antes abría Básico); **Audio › Del teléfono** para una canción propia.
- Arreglos de la simulación (`scripts/check-phone.mjs`, iPhone 13 emulado; `FLIP_BASE=https://getflipstudio.com/editor/`
  para correrlo contra la web publicada): la vista previa no se achicaba al abrir una fila más alta (una regla de
  pantallas angostas le daba 320 px de alto mínimo y el video quedaba cortado bajo la línea de tiempo); los avisos
  tapaban la barra de abajo (ahora salen sobre la imagen); **una foto superpuesta al inicio cambiaba el formato del
  proyecto** a su forma (`render/frame.ts › projectFormat`: manda la pista principal); el nombre y la duración del
  clip elegido se encimaban; el icono de Reflejar era el de voltear vertical (Lucide 1 cambió los nombres).
- **Trampa:** en Lucide 1, `FlipHorizontal2` es el icono de arriba/abajo; el de izquierda/derecha es
  `TrianglesCenterlineDashedVertical`.
- **Trampa:** los catálogos de la web van ordenados con `localeCompare(…, "es")`; un `sort()` simple los reordena enteros.
- **Máscaras con fotogramas clave (Jorge, 2026-10-22: «no los reconoce»):** con Máscara abierta, ◇+ / ◇− anima la
  máscara elegida (lugar, tamaño, giro, difuminado; en forma libre, el contorno) y no el clip; los rombos de la línea
  de tiempo son los de la máscara, y Curvas abierta desde Máscara les da forma y con ✓ vuelve a Máscara. Mover la
  máscara con un fotograma ya puesto pone otro en el cabezal. El Degradado también muestra el manejador de difuminado.
- Falta: probarlo Jorge en su celular; arrastrar el recorte en la vista previa (hoy son deslizadores).

- **Trampa (2026-10-22):** `apple-mobile-web-app-status-bar-style` va en `black`, no en `black-translucent`: con translúcida, la app instalada en el iPhone mide la pantalla más corta (la barra de estado) y la barra de abajo queda alta aunque todo vaya con `position: fixed; inset: 0`. Así lo tiene la app de gastos (`mern-expenses-tracker`). El iPhone lo lee al instalar: hay que borrar el ícono y volver a agregarlo (`flipstudio-app` `web/movil`).

## Etapa 7: menús y paneles de CapCut, uno por uno (Jorge, 2026-10-23, capturas `Downloads\capcut movil\1…23.png`)

Pedido: «adaptes estas fotos a lo que tenemos y lo que no tenemos o capcut no tiene lo adaptas a lo nuestro»; será
también el formato del `.apk`. Simulación nueva: `node scripts/check-phone-bar.mjs <carpeta> 5199` recorre las dos
barras y abre cada herramienta (capturas por paso). Hoy casi todo existe, pero se abre en hojas altas tipo inspector
que tapan la línea de tiempo; CapCut usa filas compactas con ✓ y sub-filas con «‹».

**Barra sin clip (1–2):** Ediciones · Audio · Texto · Efectos · Superposición · Subtítulos · Filtros · Ajustar ·
Stickers | Transiciones · Plantillas · Stock (lo nuestro) | Texto a voz (IA) · Relación de aspecto · Fondo.
- «Editar» → «Ediciones»; «Formato» → «Relación de aspecto»; «Ajustar» sin clip agrega una capa de ajuste con Ajustar
  abierto (como CapCut). «Genera archivos multimedia» y «Avatar de IA» no los tenemos: en su lugar Texto a voz.
- Separadores entre grupos (`TouchTool.sep`).

**Barra con video (3–7):** Dividir · Volumen · Animaciones · Efectos · Eliminar · Velocidad · Ritmos · Recortar ·
Duplicar | Sustituir · Superposición/Pista principal · Ajustar · Filtros | Retoque · Calidad del video · Eliminar
fondo | Opacidad | Transformación · Estabilización · Seguimiento | Extraer audio · Reducir ruido | Efectos de audio |
Congelar · Revertir · Máscara · Desvincular (si tiene audio enlazado).
- Sin equivalente (IA en la nube de CapCut): Ampliación/Remix/Contacto visual/Sincronización labial/Traductor/Aislar voz.

**Paneles (8–23), compactos, sobre la línea de tiempo:**
- 8 Volumen: un deslizador 0–1000 % y «Reducir el ruido» (el de la web).
- 9 Animaciones: ya es así (TouchAnim); revisar chips «En tendencia» primero.
- 10 Efectos: sub-fila Efectos de video · Plantillas de efectos · Efectos de color · Efectos con IA (Retoque/Cuerpo).
- 11–13 Velocidad: sub-fila Normal · Curva. Normal = regla 0.1×–100× con duración antes → después y «Cambiar tono del
  audio»; Curva = fila de tarjetas (Ninguna, Personalizada, Montaje, Héroe, Bala, Salto, Destellos).
- 14 Recortar: pantalla completa con la imagen y el marco, regla de girar (−45°…45°) y relaciones (A medida, 9:16, 16:9,
  1:1, 4:3, 2:1, 2.35:1), Restablecer.
- 15 Sustituir: el selector del teléfono (solo medios); el clip se queda con su lugar, duración y todo lo aplicado.
- 16–17 Ajustar y 18 Filtros: ya están (TouchAdjustPage); revisar que la hoja sea baja.
- 19 Calidad del video: botones redondos (Mejorar video IA, Estabilización, Reducir ruido de imagen si lo hay, Cámara lenta fluida).
- 20–22 Eliminar fondo: sub-fila Eliminación automática · Eliminación personalizada · Chroma key. Chroma = selector de
  color en la vista previa + Intensidad, Sombra (reflejo), Borde difuminado.
- 23 Seguimiento: Rostro · Cuerpo · Personalizado + «Seguir».

- 24 Subtítulos automáticos: Generar desde · Idioma de origen · Plantillas (fila) · Opciones avanzadas (plegadas:
  palabras por línea y todos los estilos) · Generar abajo (`SubtitlesPanel.tsx`, con `TouchUiContext`).

**Hecho (2026-10-23, `flipstudio-app` rama `web/movil-capcut`):**
- Barras en el orden y con los nombres de CapCut, con separadores entre grupos (`TouchTool.sep`) y lo nuestro al final.
- `components/TouchPanels.tsx`: Volumen, Velocidad › Normal (regla logarítmica 0.25×–4×, duración antes → después,
  Cámara lenta fluida) y › Curva (tarjetas con el dibujo de la curva), Chroma key (selector de color tocando la vista
  previa + Intensidad/Sombra/Borde difuminado), Calidad del video (botones redondos).
- Sub-filas: Velocidad (Normal · Curva), Efectos (de video · Plantillas · de color · IA · Aplicados), Eliminar fondo
  (automática · personalizada · Chroma key).
- Acciones nuevas: Sustituir (el selector del teléfono; el clip conserva lugar y efectos, se fija el formato y se quita
  el recorte viejo), Superposición ⇄ Pista principal, Ritmos (marcas amarillas en la regla con los golpes de la música;
  otro toque las quita), Reducir el ruido, Desvincular, Ajustar sin clip (capa de ajuste con Ajustar abierto).
- `components/TouchCrop.tsx`: Recortar a pantalla completa (marco con esquinas y lados, tercios, Rotar en regla,
  relaciones de aspecto, Restablecer, ✕/✓).
- Seguimiento: «Selecciona el objeto…», Rostro / Personalizado y «Seguir» ancho. Se llama «Seguimiento» y no «de
  cámara»: el nuestro hace que un elemento siga algo del video; el de CapCut mueve el encuadre (no lo tenemos).
- Pruebas: `scripts/check-phone-bar.mjs` (barras, herramientas y sub-filas) y `scripts/check-phone-actions.mjs`
  (Superposición ⇄ Pista principal, Recortar, Sustituir, Chroma, Ritmos, Subtítulos), iPhone 13 emulado.
- **Trampa:** en este repo los tipos se revisan con `npx tsc -b` (el `tsconfig.json` solo tiene referencias); `tsc -p .`
  no revisa nada y sale limpio.
- Falta: probarlo Jorge en su celular; Animaciones con «En tendencia» primero; Ajustar/Filtros como hoja baja.
