# Próxima versión (0.23)

## 1. ~~Efectos y LUTs directamente sobre un texto~~ — HECHO en la 0.22.0 (escritorio y web)
Jorge: «¿se pueden aplicar máscaras, efectos, luts a textos?» → «ok, para la próxima sería».

- Hoy: las **máscaras** sí van sobre el texto (pestaña Máscaras, desde la 0.19.0). **Efectos y LUTs no:** un clip de
  texto no tiene la capacidad `adj:videoEffects` (`AppController.cpp`, `case ClipType::Text` en la lista de `caps`),
  así que no salen las pestañas Efectos ni Ajustar. Solo con una capa de ajuste encima («Aplicar a» → enlazada al clip).
- Qué hacer (como CapCut): soltar un efecto, un LUT o un filtro sobre un texto (y elegirlo con el texto seleccionado)
  crea solo la capa de ajuste enlazada a ese texto (`ParentTrack` + `linkedClipId`), y el texto muestra las pestañas
  Efectos y Ajustar que editan esa capa. Lo mismo para subtítulos si tiene sentido.
- Igual en la web. Probar en ventana: efecto, LUT y Ajustar sobre un texto, con animación y máscara a la vez.

## 2. Colorear letras sueltas dentro de un texto (Jorge, 2026-10-24)
Jorge: «¿en un solo texto es posible poner letras de diferentes colores?» → «sí, anótalo».

- Hoy hay: «Resaltar palabra» (reglas, o la palabra entre asteriscos `*así*`), degradado del relleno por bloque,
  línea, palabra o letra (`TextGradientSpace`), o dos textos encima. **No** se puede elegir unas letras con el ratón
  y darles su propio color.
- Qué hacer (como CapCut): en el cuadro de texto del inspector (y al editar sobre la vista previa) seleccionar parte
  del texto y cambiarle **color, tamaño, negrita/cursiva, contorno y fondo** solo a esa parte.
- Cómo, con lo que ya existe: tramos con estilo propio sobre el texto (`TextStyle` gana una lista de
  `{inicio, fin, cambios}` guardada en el proyecto); `TextLayout` ya parte el texto en palabras/letras con su
  estilo (`StyledWord`, el acento usa algo parecido): extenderlo a tramos por caracteres. Las capas (relleno,
  contorno, sombra) aplican el color del tramo; las animaciones por letra siguen funcionando.
- Que sobreviva a: editar el texto (los tramos se mueven con lo escrito), cortar el clip, aplicar un estilo (decidir
  si los conserva: sí, como las animaciones), copiar/pegar atributos, plantillas, `.flip` y la web.
- Igual en el editor web. Probar en ventana: seleccionar «O» de «HOLA», ponerla roja y más grande, exportar.

**Jorge (2026-10-25): el punto 2 se hace en «Texto avanzado», como Filmora** (ver el punto 3).

**0.26/10 (ronda 3):** el «Aplicar a todos los textos» ya está en la ventana (applyTextBrushToAllTexts,
una sola entrada de deshacer), y la **web** de los tramos se está haciendo en web/v0221-texto.

### Punto 3, tercera pieza (2026-10-26): la ventana, hecha
- **`components/TextAdvancedDialog.qml`** (`ThemedDialog`, 980 px): el texto del clip en grande y **seleccionable**
  (de solo lectura: el texto se escribe en el inspector), una barra con **Negrita**, **Cursiva**, seis colores y
  «Más colores…» (`ThemedColorDialog`), **tamaño** (50 %…300 %) y **«Aplicar a lo seleccionado»**, que crea el tramo
  con lo elegido (encima de los que hubiera: donde se pisen gana el nuevo). Debajo, la lista de tramos con su color,
  su trozo de texto y su porcentaje, y «Quitar todos».
- **Aplicar** manda los tramos con `EditorState.setTextRuns` (**una sola entrada de deshacer**); **Cancelar** no toca
  el proyecto; si la selección cambia de clip, la ventana se cierra sola.
- Se abre desde **Texto › Avanzado › «Abrir Texto avanzado…»** (`TextInspector.qml`).
- **CI en verde** (run 40263840885: 16/16 suites y el paquete de Windows).
- **Trampa gorda de esta pieza:** el test **Traducciones** compara `i18n/*.ts` con lo que extrae el **build** (su
  propio `lupdate` vía `qt_add_translations`, que escanea las fuentes del target, no `lupdate src i18n` a mano). Mis
  catálogos regenerados a mano **no** coincidían y el test fallaba aunque el contenido fuera correcto: se revirtieron
  los `.ts` a como estaban y los textos de la ventana van en **literales en español** hasta que el build los regenere.
  Para traducirlos: volver a poner `qsTr`, correr `cmake --build build --target update_translations` y rellenar.
- **Falta:** el «aplicar a todos los textos», la selección arrastrando sobre la vista previa (hoy se selecciona en el
  cuadro), el **punto 2 en la web** (tramos + ventana) y la **prueba en ventana**.

### Punto 3, segunda pieza (2026-10-26): ya se ven, y hay API para la ventana
- **El trazado parte por tramo** (`TextLayout.cpp`): el párrafo se compone en trozos por (acento, emoji, tramo) con
  el **tamaño** (`pixelSize × sizeScale`) y el **peso/cursiva** del tramo, y cada trozo (`StyledWord`) sabe si su
  tramo trae color. La palabra se parte donde empieza o acaba un tramo, aunque sea en medio.
- **El relleno usa ese color** (`SkiaTextPainter.cpp`): el color del tramo va por delante del acento y por detrás del
  que ponga un animador. (Contorno, sombra y degradado siguen como estaban: el color de tramo solo cambia el relleno.)
- **API para QML** (`AppController::textRuns` / `setTextRuns`): leer los tramos de un clip y reemplazarlos de una vez,
  con una sola entrada de deshacer; al escribir se normalizan (orden, recorte, sin solapes).
- Pruebas: la del modelo (JSON, orden, solapes) y `SkiaTest::textRunsPaintWithTheirOwnColourAndSize` (el trozo lleva
  su color, la palabra se parte y la tinta del tramo grande crece). **CI en verde** (run 40258486574: 125 + 191
  pruebas y el paquete de Windows).
- **Trampas de esta pieza:** en `TextLayout.cpp` ya existe un `runs` (los tramos de Skia) — los del estilo se llaman
  `textRuns`; y el test de **Traducciones** falla si se añade un `tr(...)` nuevo sin pasar `lupdate`, así que la API
  reusa los textos que ya existían.
- **Falta:** la **ventana** de Texto avanzado (selección de letras con `TextEdit.selectionStart/selectionEnd` y
  `select()`, barra B/I/U + color + tamaño sobre lo seleccionado, pestañas reusadas del inspector, Aplicar/Cancelar
  con un solo paso de deshacer), el «aplicar a todos los textos», la web, y la prueba en ventana.

### Estado del punto 3 (2026-10-26): el modelo, hecho; falta pintarlo y la ventana
- **`TextRun`** en `core/TextStyle.h`: tramos `{start, end}` con **color**, **tamaño** (relativo al `pixelSize`) y
  **negrita/cursiva** propios, en `TextStyle::runs`. Se guardan en el proyecto (`"runs"`, solo si hay) y
  `normalizedTextRuns()` los deja ordenados, recortados al texto y **sin solapes** (donde dos se pisan gana el último
  de la lista); `textRunAt()` dice qué tramo cubre un desplazamiento.
- Prueba `CoreTest::textRunsStyleStretchesOfTheText` (ida y vuelta por JSON, recorte, orden, solapes, fuera del
  texto). **CI `build.yml` en verde** (run 40250429888): 191 + 124 pruebas y el paquete de Windows.
- **Falta para que se vea:** `TextLayout.cpp` (partir el texto también por tramo, y `styleFor()` con el tamaño y el
  peso del tramo) y `SkiaTextPainter.cpp` (color de relleno por pieza). Después, la **ventana** de Texto avanzado
  con selección de letras (el `TextArea` de QML no da desplazamientos de selección: hay que llevar la selección a
  mano, con los `caretStops` que ya existen), el «Aplicar a todos», y la web.
- El punto 2 del plan (letras de colores) va dentro de esto: es el mismo `TextRun`.

### Punto 4 en la web (2026-10-26): hecho, rama `web/v0221-texto` `ba09b` (sin desplegar)
- `components/LibraryTree.tsx` + `components/subcategories.ts`: la barra lateral es un árbol (flechita, nombre que
  abre la pestaña, subcategorías con sangría, la elegida con fondo, mayúsculas del título, `localStorage`). Los chips
  se esconden (`panelDriven` en `CategoryChips`) y **en celular/tableta siguen**.
- Comprobado: `npx tsc -b` limpio, `npm run build` OK, `npx vitest run --no-file-parallelism` **996/996**, oxlint
  igual que antes, y Playwright en 6 pestañas (0 chips, filas de subcategoría 6/6, título 6/6, tarjetas filtradas
  6/6). Los 4 fallos de vitest en paralelo ya estaban en HEAD (carga).
- Pendiente ahí: Stock sin subcategorías en el árbol (su tanda), los paneles que nunca tuvieron chips (Medios,
  Voz, Subtítulos, Máscaras) van sin flecha, y la fila del *paquete* en Pegatinas sigue.

## 3. Editor de «Texto avanzado» como Filmora (Jorge, 2026-10-25) — incluye el punto 2
Captura de referencia: `docs/capturas/filmora-texto-avanzado.png` (Filmora › botón **AVANZADO** abajo a la derecha
del inspector de Títulos → ventana «Texto avanzado Editar»).

- **Qué es:** una ventana grande (diálogo modal, ~1200×700) que se abre desde un botón **«Avanzado»** al pie del
  inspector de Texto (`src/qml/components/properties/TextInspector.qml`; hoy «Avanzado» es solo una sección
  plegable, `advancedOpen`, línea ~1858, y el botón «Edit in Advanced» ~1183 la abre: que abran la ventana).
- **Arriba, barra de herramientas:** añadir texto (T), añadir cuadro, imagen, borrar · fuente · tamaño · alinear
  vertical · **B / I / U** · mayúsculas · las 4 alineaciones · interlineado · espaciado entre letras.
  **B/I/U, color, tamaño y fuente se aplican a lo seleccionado** dentro del texto (si no hay selección, a todo):
  aquí entra el punto 2 (tramos con estilo propio; en la captura «YO» va en rojo y el resto en blanco).
- **Centro:** vista previa grande del texto sobre negro con el cuadro de selección (asas en las esquinas y el
  tirador de giro), donde se puede **escribir y seleccionar letras directamente** (como un TextEdit sobre la vista).
  Debajo, controles de reproducción (atrás, reproducir, parar, barra, tiempo `00:00:00:00 / 00:00:05:00`, zoom) y
  una **mini línea de tiempo** propia con una fila por capa de texto (ojo y candado), para varios textos en el
  mismo título.
- **Derecha, pestañas:** **Estilo** (estilos rápidos, los de `core/TextQuickStyles`), **Personalizar**, **Animación**,
  **Burbuja**. Personalizar, en secciones plegables con casilla: «Texto de entrada» (cuadro con contador `16/1500`),
  «Texto en perspectiva» (Eje X/Y/Z, Intensidad de perspectiva, Desenfoque — ya existe el giro 3D de la 0.20),
  «Relleno» (Tipo: Color de relleno/degradado/imagen, + / − colores, Efecto, Opacidad, Desenfoque), «Contorno» (con
  «+» para varios contornos), «Sombra», «Fondo», «Brillo»… Reusar los controles que ya están en `TextInspector.qml`
  (no duplicar lógica: extraerlos a componentes y usarlos en los dos sitios).
- **Abajo:** «Guardar como personalizado» (va a Mis estilos), «Aplicar cambios» (con flecha: aplicar a este / a
  todos los textos), casilla «Utilizar fuente predeterminada para texto nuevo», **Aplicar** y **Cancelar** (Cancelar
  deshace todo lo hecho en la ventana: una sola entrada de deshacer al Aplicar).
- **Modelo (punto 2):** `TextStyle` gana una lista de tramos `{inicio, fin, cambios}` (color, tamaño, negrita,
  cursiva, subrayado, fuente, contorno, fondo) guardada en el proyecto y en el `.flip`; `TextLayout` (ya parte en
  `StyledWord`) los aplica por carácter; las animaciones por letra siguen funcionando. Los tramos se mueven al editar
  el texto. Pruebas en `tst_*` para guardar/abrir y para editar el texto con tramos.
- **Web** (`flipstudio-app`): la misma ventana después del escritorio.
- **Probar en ventana:** abrir Avanzado, seleccionar «YO» de «YOUR TITLE HERE», ponerlo rojo y en negrita, Aplicar,
  ver la vista previa y exportar; Cancelar no deja cambios; deshacer/rehacer.

### Hecho (2026-10-25, rama `flip/v0.22.1`): el árbol, en el escritorio
- `AssetsPanel.qml`: la barra lateral ya no es una lista de pestañas, es un **árbol**. Cada pestaña lleva una
  **flechita** (› cerrada, ⌄ abierta) y, al abrirse, **sus subcategorías una por línea con sangría**; la elegida va
  con fondo. La fila de la pestaña abre la pestaña; la flechita solo abre y cierra. La pestaña que se abre se
  despliega sola (`expandGroup`), y arriba del árbol va el **nombre de la subcategoría en mayúsculas**.
- **Los chips desaparecen** de los navegadores: `AssetCategoryChips` gana `panelDriven` y se oculta cuando el panel
  lleva la categoría. Cada navegador (Efectos, Títulos, Transiciones, Stickers, Formas, Filtros, Audio, Plantillas
  de efectos, Escenas, Pegatinas del emoji…) gana `property bool panelDriven: false` y lo recibe del panel
  (`panelDriven: !root.sheetMode`), así que **en el celular/Android (modo hoja) los chips siguen**, como está hoy.
- El panel conoce cada navegador por su `Loader` (los 19 tienen id) y le pasa la categoría elegida; la pestaña
  recuerda búsqueda y categoría como siempre (`tabState`).
- La barra lateral se ve **siempre** (antes se ocultaba en las categorías de una sola pestaña: Efectos,
  Transiciones, Stock), con 168 px.
- `qmllint` limpio en los 20 archivos tocados (sin errores de sintaxis ni propiedades que no existan).

**Lo que falta de este punto:**
1. **La web** (`flipstudio-app`): el mismo árbol en el panel izquierdo (hoy son chips bajo el buscador).
2. **Stock**: el árbol solo tiene lo que expone cada navegador; la sección «Todo» de Stock con sus tipos por línea
   (plantillas, música, LUTs, looks, stickers…) queda para su tanda; Videos y Fotos se dejan como están.
3. **Las subcategorías de una pestaña que no está abierta** no se pueden dibujar (los navegadores se instancian al
   abrir su pestaña): el grupo enseña la flechita al abrirlo. Se puede resolver guardando la lista en `tabState`.
4. Puntos rojos de novedades en las subcategorías, y el teclado ↑/↓ recorriendo el árbol (ya recorre las filas).
5. **Probar en ventana** (regla de Jorge) en cuanto haya build de CI: recorrer cada categoría, abrir y cerrar grupos,
   elegir subcategorías y ver que las miniaturas llenan el alto que ganan.
## 4. Panel izquierdo como Filmora: subcategorías en la barra lateral (Jorge, 2026-10-25)
Captura de referencia: `docs/capturas/filmora-panel-izquierdo.png` (Filmora › Filtros).

- **Problema:** cada pestaña (Efectos, Títulos, Stock…) muestra sus subcategorías como **chips debajo del buscador**
  (`ChipScroller`, `activeCategory` de cada navegador). Como crecieron, ocupan tanto alto que no dejan ver las
  miniaturas.
- **Cómo queda (Filmora):** se quitan los chips de debajo del buscador. La barra lateral izquierda (la que ya lista las
  pestañas de la categoría: `tabRail` en `src/qml/AssetsPanel.qml`, ~línea 1036; categorías en `categories`, ~752)
  pasa a ser un **árbol**: cada pestaña con una **flechita** (› cerrada / ⌄ abierta) y, al abrirla, **sus
  subcategorías debajo, una por línea, con sangría** (en la captura: «› Mío», «⌄ Filtros» → Básico, Premium, Blanco y
  negro…). La elegida va resaltada con fondo; un punto rojo para las que tienen novedades. Clic en una subcategoría =
  lo que hoy hace el chip (`activeCategory`). Recordar qué grupos quedaron abiertos y la última elegida
  (`lastTabInCategory` y el guardado de búsqueda/categoría, ~línea 811, ya existen).
- Arriba del contenido queda solo: buscador y «…», y el **título de la subcategoría elegida** en mayúsculas
  («BÁSICO»), como Filmora. Las entradas especiales («Favoritos» `__favorites__`, «Míos» `__mine__`, «Tendencias»)
  también van en el árbol.
- Aunque la categoría tenga una sola pestaña (Efectos, Transiciones), ahora **sí** se muestra la barra lateral con
  sus subcategorías (hoy se oculta, `showSideList`).
- **Stock, con un cambio:** la sección **«Todo»** de Stock (la que abre todo el submenú de tipos: plantillas,
  música, LUTs, looks, stickers…) va en el árbol de la izquierda como **«Stock»** con sus pestañas debajo (cada tipo
  de Stock = una línea). **«Videos» y «Fotos» (Pexels y Pixabay) se dejan tal y como están hoy**, con su selector de
  proveedor por defecto (`StockBrowser.qml`, ~línea 325) — no se tocan.
- Cuidar: el ancho del panel (`sideListWidth`, que no se coma las miniaturas: lateral ~150 px como Filmora), el
  teclado (↑/↓ en el árbol, `tabRail.step`), el modo hoja del celular/Android (`sheetMode`: ahí siguen los chips),
  y que nada se quede sin poder elegir.
- **Web:** igual en `flipstudio-app` (mismo árbol en el panel izquierdo).
- **Probar en ventana:** recorrer cada categoría de la fila de arriba, abrir y cerrar grupos, elegir subcategorías,
  ver que las miniaturas llenan el alto; en Stock, «Stock» con sus tipos en el árbol y Videos/Fotos como siempre.

## Orden sugerido
1. Punto 4 (panel izquierdo): es solo QML y se nota en toda la app.
2. Punto 3 (Texto avanzado + letras de colores): modelo `TextStyle`/`TextLayout` con pruebas, después la ventana.
3. Compilar una vez (`gh workflow run build.yml --ref <rama> -f platforms=windows`), **probar en ventana** (regla de
   Jorge) y publicar como 0.23.0 (rutina en `CLAUDE.md`). La 0.22.0 aún espera subir el MSIX tras aprobarse la 0.21.0.
