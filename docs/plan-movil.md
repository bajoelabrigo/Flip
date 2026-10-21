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
- **Ajustar como CapCut** (capturas `Downloadsjustes*.jpeg`, desplegado): una hoja con Predefinidos (efectos de
  color), Filtros (LUTs), Ajustar (botones redondos + un deslizador, `AdjustSection.tsx › TouchAdjustPage`) y
  Calidad del video (Mejorar video, Estabilización, Reducir ruido del audio).
- Falta (etapa 2): textos de ayuda que dicen «haz clic» o «panel de la derecha», arrastrar la hoja para
  agrandarla, mover textos y stickers con dos dedos en la vista previa, el teclado de iOS al escribir un texto,
  y probarlo en el iPad de Jorge. Etapa 3 (inicio con barra abajo) sin empezar.
