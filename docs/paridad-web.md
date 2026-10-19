# Paridad del editor web con la app de escritorio

Pedido de Jorge (2026-10-18): que el editor web (`flipstudio-app`, getflipstudio.com/editor) quede **igual o lo más
parecido posible** a la app de escritorio. **Empezamos a armarlo mañana, 2026-10-19**, después de publicar la
0.18.1. Este documento es la lista de trabajo: una fila por función, y se actualiza en cada versión.

## Reglas
- **Copiar, no inventar:** nombres, iconos (lucide, los mismos ids que `src/qml/Theme.qml`), colores, orden de
  pestañas y atajos salen del escritorio. Si CapCut o Filmora ya resolvieron cómo se comporta algo, se copia.
- **Nada de código de Drift en la web:** los shaders y el código de Drift son GPL y `flipstudio-app` es privado. Los
  efectos y transiciones de la web se escriben desde cero. Lo que escribimos nosotros (por ejemplo `face_blemish`,
  las plantillas, los generadores de Stock) es nuestro y sí se puede reusar.
- **Un solo formato, el `.flip`:** el escritorio guarda como `.flip` y sigue abriendo los `.drift` de antes (es el
  mismo paquete, solo cambia la extensión: `EditorHeader.qml`, «Flip Studio project (*.flip *.drift)»). La web hoy
  solo conoce `.drift` (`Home.tsx`: `accept=".drift"`, «Importar .drift»; `App.tsx` descarga `.drift`): tiene que
  abrir `.flip` y `.drift` y guardar `.flip`, igual que el escritorio. Todo lo nuevo tiene que sobrevivir el viaje
  escritorio → web → escritorio (`project/driftBundle.ts`).
- **Mismo servidor:** la cuenta de Google y Stock usan `api.getflipstudio.com`, igual que el escritorio.
- Cada versión nueva del escritorio dice en su `docs/plan-<versión>.md` qué parte pasa a la web.

## Estado (revisado en el código el 2026-10-18; ❓ = comprobar mañana en el navegador)

Leyenda: ✅ igual · 🟡 parcial · ⬜ falta · ❓ por comprobar

### Aspecto y navegación
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Tema oscuro turquesa como Filmora (paneles `#181c1f`, menús `#202427`, acento `#55e5c5`) | 0.17 | ✅ | `teal` es el tema por defecto y los siete son los del escritorio (`layout/theme.ts`, `index.css`) |
| Pantalla de inicio como Filmora | 0.17 | ✅ | `Home.tsx` tenía la estructura (banda + formatos + atajos + tus proyectos): la banda ya toma los colores del tema |
| Cerrar el editor vuelve al inicio | 0.17 | ✅ | `Root.tsx` (`onHome`): «Inicio» en la cabecera y Archivo › Inicio |
| Menú arriba (Archivo, Editar, Herramientas, Ver, Avanzado, Ayuda) con atajos | 0.16 | ✅ | `components/MenuBar.tsx`, con los mismos nombres y atajos y Ayuda › Atajos de teclado |
| Fila de categorías sobre el panel de recursos | 0.16 | ✅ | Igual que `AssetsPanel.qml`: sin columna de iconos, las 9 categorías con el icono sobre el nombre y la lista lateral de 152 px con las pestañas de la abierta (oculta si tiene una sola), con los nombres del escritorio. El panel abre tan ancho como la fila (`panelSizes.ts`, clave `v2`) |
| Pestañas Escenas (Medios) y Efectos de audio (Audio) | sí | ⬜ | Están en la lista con una página que dice qué hacen y «Descargar app» (`NotYetPanel`) |
| Filtros › LUTs y Efectos de color, Stickers › Máscaras | 0.16 | ✅ | `LibraryExtraPanels.tsx`: la galería de `LutPage` y las formas de máscara, sobre el clip seleccionado; Efectos de color = `EffectsPanel only="color"` |
| Panel izquierdo con barra de iconos e inspector derecho con su barra | 0.9.x | ✅ | |
| Idiomas de la app (13) | sí | ⬜ | La web está solo en español: no tiene capa de traducción |
| Proyectos `.flip` (abrir `.flip` y `.drift`, guardar `.flip`) | sí | ✅ | Abre los dos (documento + tabla de medios + blobs incrustados, que se guardan con el proyecto) y guarda `.flip` |

### Cuenta y Stock
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Iniciar sesión con Google | 0.10 | ✅ | `src/account/account.ts` + `AccountButton`: PKCE, vuelta a `/editor/`, canje en el servidor y token con refresco. El servidor usa el cliente web de Google (`GOOGLE_WEB_CLIENT_ID`) |
| Stock (plantillas, música, sonidos, LUT, looks, estilos y animaciones de texto, transiciones, formas, stickers, superposiciones, fondos, contadores, kits) | 0.12–0.18 | 🟡 | Armado como `MarketTab.qml` desde `/v1/market/catalog`: pestañas Todo/Videos/Fotos, tipos propios como chips bajo Todo, filtros del catálogo. «Usar» funciona con todo lo de `delivery: media` y `lut` (música, sonidos, stickers, superposiciones, fondos, filtros, fotos y videos). Plantillas, looks, estilos de texto, transiciones y formas salen marcados «app» |
| Inicio de Stock tipo tienda, búsqueda, favoritos y «Pide una plantilla» | 0.14 | 🟡 | Inicio con los estantes de `/v1/market/home`, tarjetas con la forma del elemento, vista previa de audio y video al pasar el mouse, «Usado N veces» y «Pide una plantilla» con votos (`StockRequestsDialog.tsx`). Falta: los favoritos de la web siguen en el navegador, no en la cuenta (`/v1/me/favorites` usa los grupos del escritorio) |
| Biblioteca de la cuenta («Mis descargas») | 0.12 | ✅ | «Mi cuenta» (`AccountDialog.tsx`, se abre con la foto como en el escritorio): foto, plan, Favoritos por grupo y Descargas de Stock con «Usar» |
| Pexels y Pixabay | 0.10 | ✅ | Pestañas Videos y Fotos, con la fuente como chip y la orientación como filtro; los archivos se bajan directo de sus CDN (CORS `*`, permitidos en la CSP) |

### Plantillas
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Plantillas de escena con huecos «Tu foto aquí» | 0.12 | ⬜ | Leer el mismo paquete (`FORMAT.md` en `tools/scene_templates`) |
| Plantillas de efectos (Intensidad, Caída, Ritmo) | 0.11 | ⬜ | No hay: el «plantilla» de la web es texto y biblioteca |
| Guardar como plantilla / Mis plantillas | 0.13 | ⬜ | |

### Edición en la línea de tiempo
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Pistas libres, ojo, silencio y candado por pista | 0.9.7 | ✅ | |
| Cortar, duplicar, invertir, marcadores | sí | ✅ | |
| Congelar fotograma como CapCut | 0.17 | ✅ | `freezeFrame` corta en el cabezal, mete 3 s congelados y empuja el resto, igual que el escritorio |
| Mover con cerrar huecos y borrar con cerrar huecos | 0.16–0.17 | ✅ | `removeClipRippled` y los recortes con `ripple`, con el interruptor de la barra |
| Arrastre «tipo tetris» | 0.18 | ❓ | |
| Seleccionar varias pistas, agrupar y desagrupar | 0.9.9 / 0.12 | 🟡 | Hay composiciones; falta la selección de pistas |
| Capas de ajuste con «Aplicar a» | 0.9.9 | 🟡 | Hay `AdjustmentLayerSection.tsx` |
| Curvas de velocidad | sí | ⬜ | Solo se conservan al abrir un `.drift` |
| Estabilizar | sí | ⬜ | Solo se conserva al abrir un `.drift` |

### Efectos, transiciones, color
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Efectos | 78 | 🟡 ~25 | Escribirlos desde cero, por categoría, con las mismas tarjetas |
| Transiciones | 40 | 🟡 10 | Ídem |
| Antes y después al pasar el mouse | 0.17–0.18 | ⬜ | |
| Filtros (LUT) y Efectos de color | 0.16 | 🟡 | Hay `LutPage.tsx` y `cubeLut.ts`; faltan las 200 LUT de Stock |
| Máscaras | sí | 🟡 | Hay `MaskPage.tsx`; falta texto como máscara (tampoco está en el escritorio) |
| Modos de fusión | sí | ✅ | |

### Texto
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Básico, Burbuja, Efectos y Animación como CapCut | 0.9.6 | ✅ | |
| Contadores animados | 0.17–0.18 | ⬜ | `counterTextAt` y `counterSeconds` en el escritorio |
| Texto con IA (describir la idea) | 0.17 | ⬜ | MiniLM puede correr en el navegador |

### Audio
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Música y efectos de sonido incluidos | sí | ✅ | `/musica/` en el VPS |
| Mezclador y efectos de audio | sí | 🟡 | Hay `AudioMixer.tsx`; comparar con la pestaña de audio |
| Golpes de música, cortes al ritmo | sí | ⬜ | |
| Silencios, sonoridad, normalizar | sí | ⬜ | Solo hay volumen por clip |

### IA
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Subtítulos con Whisper | sí | ✅ | Whisper base en el navegador |
| Voz con IA | sí (extra `tts-model`, local) | ✅ | La web usa Kokoro en el navegador; comprobar que las voces e idiomas coincidan |
| Quitar fondo | sí (IA) | 🟡 | La web usa croma (color), no IA |
| Transición con IA y cámara lenta suave (RIFE) | 0.17–0.18 | ⬜ | ONNX Runtime Web con WebGPU, como Whisper |
| Retoque, quitar imperfecciones, cuerpo y cabello | 0.13–0.17 | ⬜ | Necesita caras en el navegador (MediaPipe web) |
| Profundidad, quitar ruido | sí | ⬜ | Al final, o nunca: muy pesados para el navegador |

### Exportar
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Hasta 4K | sí | ✅ | La web llega a 4K60 |
| 8K, H.265/AV1 | 0.12 | 🟡 | WebCodecs da H.264, VP9 y AV1 (no H.265); 8K depende del navegador |
| GIF | sí | ⬜ | La web exporta MP4 (y WebM) |

## Etapa 1 hecha (2026-10-19), en la rama `web/paridad-1`
Lo que hoy se ve y se usa igual que en el escritorio:
- **Tema turquesa por defecto**, con los siete colores del escritorio (`teal`, `amber`, `midnight`, `graphite`,
  `violet`, `rose`, `forest`); en la web el «teal» es `:root` y los demás son overrides. La banda de «Crear
  proyecto» toma los colores del tema en vez del ámbar fijo.
- **Menú arriba** (`components/MenuBar.tsx`): Archivo, Editar, Herramientas, Ver, Avanzado y Ayuda, con los
  atajos del escritorio a la derecha; solo entradas que ya hacían algo en la web. Ver incluye el color de la
  interfaz y Ayuda abre **Atajos de teclado** (`ShortcutsDialog.tsx`), con la misma lista que respeta el teclado.
- **Fila de categorías** sobre el panel de recursos, con la última pestaña recordada por categoría.
- **`.flip`:** «Abrir proyecto…» acepta `.flip` y `.drift`; el documento se convierte con la tabla de medios del
  proyecto, y los medios incrustados se guardan con el proyecto (`SavedMedia.blob`), así que al reabrir siguen
  ahí. «Guardar copia .flip» (y Archivo › Guardar copia) descarga `.flip`.
- Comprobado en el navegador: inicio, editor, los seis menús, el diálogo de atajos, las categorías y los temas
  (capturas en `%TEMP%\web-*.png`). `tsc`, `vite build` y las 99 pruebas en verde; `oxlint` igual que antes
  (30 avisos y el error viejo de `rules-of-hooks`).

### Arreglado al probarlo: abrir un proyecto no funcionaba desde que se escribió
Al probar «Abrir proyecto…» con un `.flip` de verdad salieron tres fallos encadenados en
`project/driftBundle.ts`; ninguno se había visto porque la función no se había usado:
1. **`sha256` tocaba `SharedArrayBuffer` sin comprobar si existe.** En una página sin aislamiento entre
   orígenes (la nuestra) ese global no existe y el `instanceof` lanza `ReferenceError`. Ahora se copia el búfer y se
   firma la copia.
2. **El lector de zstd usaba una API que el paquete no tiene** (`new ZstdCodec()` + `init()`): el módulo exporta
   `ZstdCodec.run(callback)`, así que fallaba con «ZstdCodec is not a constructor». El `.d.ts` propio declaraba una
   API inventada.
3. **El wasm de `zstd-codec` necesita `SharedArrayBuffer`**, que la web no tiene ni puede tener sin COOP/COEP (eso
   rompería las fuentes y las imágenes de Stock). Se cambió a **`fzstd`**, zstd en JavaScript puro, que basta porque
   la web solo descomprime (escribe los proyectos sin comprimir).
4. De paso: los blobs con `codec: "zstd"` ahora se descomprimen, y su digest se comprueba **después** de
   descomprimir, como hace el escritorio (`ProjectBundle.cpp`: «digest … over the uncompressed bytes»).

Comprobado contra `getflipstudio.com/editor/`: `prueba.flip` se abre, sale en la lista de medios su archivo (que era
de referencia, así que la app pide buscarlo, como debe) y el proyecto queda con el nombre del archivo.

### Segunda tanda (2026-10-19): cuenta en la web y cabecera ordenada
- **Cabecera**: Inicio, Guardar, Video y Descargar app pasan a la derecha, junto a Exportar (Jorge: «para que no se
  confundan con los otros»); a la izquierda quedan el menú y el nombre del proyecto.
- **Cuenta**: botón «Iniciar sesión» con Google (PKCE, vuelta a `https://getflipstudio.com/editor/`), avatar con
  menú y «Cerrar sesión». La vuelta del `code` se canjea en `Root` y la dirección se limpia siempre, aunque falle.
  El servidor tiene ahora **dos clientes** de Google (escritorio y web, cada uno con su par id/secreto) y una
  **lista cerrada** de direcciones de vuelta (`isWebRedirect`), con prueba propia. El cliente web lo creó Jorge en
  Google Cloud y hay que tener registrada la dirección con barra final: lo comprobé contra Google con
  `scripts/check-google-redirect.mjs` (con él se ve `redirect_uri_mismatch` o, si está bien, la pantalla de cuentas).
- Falta de la etapa 2: **el panel de Stock** (catálogo, búsqueda, categorías y «Usar» para los tipos que la web
  sabe aplicar: LUTs, música, sonidos, stickers, superposiciones y fondos).

### Tercera tanda (2026-10-19): Stock en la web
- **Pestaña y categoría propias** (`components/StockPanel.tsx` + `stock/stock.ts`), con la fila de chips por tipo, el
  cuadro de búsqueda y tarjetas con miniatura, duración y «Usar».
- **Qué se puede usar ya:** música, sonidos, stickers (Lottie), superposiciones, fondos y filtros. Los dos primeros
  van a Medios con su dirección guardada (`importFromUrl`), así que al reabrir se descargan solos; los filtros entran
  en Filtros (`importLutFile`). Plantillas de escena, looks, estilos de texto, transiciones y formas se listan con la
  etiqueta **app**: ese contenido se aplica en el escritorio, no aquí.
- Sin sesión, el panel invita a entrar con Google; el catálogo lo pide el servidor con el token de la cuenta.
- Comprobado con datos simulados (`scripts/check-stock-ui.mjs`): 4 tarjetas, títulos, duraciones y «Usar», y la
  plantilla filtrada en «Todo» porque la web no la aplica. Falta la prueba con la cuenta de Jorge.

### Cuarta tanda (2026-10-19, Claude): entrar con Google ya funciona en la web
- **«Failed to fetch» al volver de Google:** la CSP del editor (`deploy/nginx-editor.conf`) tenía `connect-src
  'self'` y el navegador cortaba el canje en `api.getflipstudio.com`. Ahora permite `api.getflipstudio.com` en
  `connect-src`, `img-src` y `media-src`, y `*.googleusercontent.com` en `img-src` (la foto de la cuenta). El
  snippet se copió al VPS (`/etc/nginx/snippets/flipstudio-editor.conf`, copia en `/root/*.bak-*`).
- **«Usar» de Stock:** los archivos de `api.getflipstudio.com/plantillas/` no traían `Access-Control-Allow-Origin` y
  el `fetch` de `StockPanel` habría fallado igual. Añadido en `flipstudio-api/deploy/nginx-api.conf` y en el sitio
  del VPS (parcheado en su sitio: lo editó certbot).
- **La vuelta de Google abre el mismo proyecto** (antes caía en el inicio): `Root` guarda el proyecto abierto en
  `sessionStorage` (`rememberReturnView`) y lo reabre si la página trae `?code` (`returnViewAfterSignIn`).
- **El botón de la cuenta es como el del escritorio** (`EditorHeader.qml` › `accountButton`): solo el círculo de
  32 px con la foto de 28, borde turquesa al pasar el mouse, sin el nombre al lado; sin sesión, el icono de persona.
- Jorge entró con su cuenta y funciona.

### Quinta tanda (2026-10-19, Claude): Stock completo y «Mi cuenta»
- `StockPanel.tsx` reescrito como el escritorio: buscador, pestañas subrayadas **Todo / Videos / Fotos**, bajo Todo
  los chips **Inicio** + los tipos del catálogo (los que la web no aplica, con la etiqueta «app»), Pexels/Pixabay como
  chips en Videos y Fotos, y los filtros de cada fuente (categoría, formato, fotos, duración, música, orientación)
  como listas. **Inicio** = los estantes de `/v1/market/home` con tarjetas de la forma del elemento.
- `applyStockItem` (`stock/stock.ts`) decide qué hace «Usar»: Medios (`delivery: media`) o Filtros (`lut`); lo usan
  Stock y «Mi cuenta». Los errores del servidor llegan con su texto (`errorOf` en `account.ts`).
- **«Pide una plantilla»** (`StockRequestsDialog.tsx`): idea + tipo, Más votadas / Nuevas y votar.
- **«Mi cuenta»** (`AccountDialog.tsx`): la foto de la cabecera lo abre (ya no hay menú), como en el escritorio.
- CSP: Pexels (`images.`/`videos.pexels.com`) y Pixabay (`pixabay.com`, `cdn.pixabay.com`) en `img-src`,
  `media-src` y `connect-src`.
- De paso: quedaban 13 colores **amarillos del tema viejo** fijos en `index.css` (segmentados, máscaras…) y en
  `timeline/look.ts`; ahora salen de `--accent`.
- Probado en el navegador con datos simulados (inicio, plantillas con filtro, videos, pedidos, cuenta y descargas),
  `tsc` y las 99 pruebas en verde, desplegado. **Falta que Jorge lo pruebe con su cuenta** (datos reales).

### Sexta tanda (2026-10-19, Claude): el panel izquierdo, igual que el escritorio
Jorge: «Replica la app de escritorio». La web tenía una columna de iconos a la izquierda (no existe en el escritorio)
y una fila de chips de texto. Ahora es `AssetsPanel.qml` tal cual:
- **Fila de categorías** de 54 px, icono arriba y nombre abajo, en turquesa la abierta: Medios, Stock, Audio,
  Títulos, Transiciones, Efectos, Filtros, Stickers, Plantillas.
- **Lista lateral** (152 px, botones de 32 px con icono y nombre) con las pestañas de la categoría: Medios (Medios,
  Escenas), Audio (Música, Efectos de sonido, Voz, Efectos de audio), Títulos (Texto, Subtítulos), Filtros (LUTs,
  Efectos de color), Stickers (Pegatinas, Formas, Máscaras), Plantillas (Mis plantillas, Plantillas de efectos).
- Lo que la web no tiene todavía (Escenas, Efectos de audio, Mis plantillas, Plantillas de efectos) abre una página
  que lo explica, con «Descargar app» (y en Mis plantillas, «Ver plantillas en Stock»).
- Iconos nuevos en `Icon.tsx`: `blend`, `listVideo`, `micVocal` (los de `Theme.icons`).
- **Trampa:** `npx tsc --noEmit -p .` en `flipstudio-app` **no revisa nada** (`tsconfig.json` solo tiene
  `references`). Usar `npx tsc -b`, que es lo que corre `npm run build`.

### Lo siguiente de la etapa 1 que queda
- Las categorías **Stock**, **Filtros** (LUT y efectos de color en una sola) y **Plantillas**, cuando existan en
  la web (etapa 2).
- La rueda que pasa de una categoría a la siguiente (`CategoryScrollOn.tsx` ya existe para las bibliotecas).
- Traducir la web a los 13 idiomas: hoy son textos en español a pelo.

### Séptima tanda (2026-10-19, Claude): el cromo de las pestañas, como AssetSearchBar y AssetCategoryChips
Regla de Jorge: replicar el escritorio y comparar cada pestaña con su `.qml` antes de darla por hecha. Lo primero que
no cuadraba era el cromo, en todas las pestañas de catálogo a la vez:
- **Sin cabecera con título** donde el escritorio la oculta (`assetsHeader.searchBarTab`): Texto, Formas, Stickers y
  Efectos ya no llevan «Texto / Formas / Stickers / Efectos» encima. Siguen con cabecera Medios, Música, Efectos de
  sonido, Voz, Subtítulos, Máscaras y Stock, como en `AssetsPanel.qml`.
- **Buscador que nombra la pestaña** (`AssetSearchBar.qml` → `components/AssetSearchBar.tsx`): «Buscar efectos» (con
  la capa de ajuste como icono a la derecha, donde el escritorio pone las acciones), «Buscar transiciones», «Buscar
  stickers», «Buscar formas» y «Buscar sonidos». El buscador filtra de verdad y, mientras se escribe, los chips se
  esconden (`searching` en el escritorio).
- **Chips de categoría del escritorio** (`AssetCategoryChips.qml` → `components/CategoryChips.tsx`): estrella de
  favoritos, divisor fino y las categorías; **fuera el chip «Todos»**, que el escritorio no tiene (siempre hay una
  categoría abierta y la rueda sigue a la siguiente).
- **Fuera los párrafos explicativos** que la web ponía encima de la lista de música y sonidos: el escritorio los
  tiene solo en el estado vacío.
- Comprobado en el navegador pestaña por pestaña (`scripts/check-tabs.mjs`, contra la web desplegada): Efectos,
  Transiciones, Stickers y Sonidos con buscador y chips; Texto y Formas sin título; Medios, Música, Voz y Subtítulos
  conservan su cabecera. `tsc` limpio y las 99 pruebas en verde.

**Lo que aún no cuadra dentro de las pestañas** (siguiente en la lista, por orden del escritorio):
1. **Medios**: hecha la fila «Buscar medios» con vista de cuadrícula/lista y el orden (octava tanda); **faltan las
   carpetas** («Nueva carpeta», ruta, mover/renombrar) y por eso también la vista de árbol, y el «Importar» partido.
2. **Filtros › LUTs**: el escritorio lleva «Buscar filtros», chips y «Importar LUT…» en el cromo; la web solo tiene
   la galería y el botón de Stock.
3. **Formas**: el escritorio tiene categorías (`builtinShapeCategories`) y favoritos; la web es una lista plana.
4. **Máscaras** y **Voz**: comparar su contenido pieza por pieza con `MasksTab.qml` y `SpeechTab.qml`.

### Octava tanda (2026-10-19, Claude): Medios, con la fila de `MediaAssetsTab.qml`
- **Fila de controles** bajo la cabecera, como el escritorio: «Buscar medios» (filtra por nombre) y los tres botones
  a su derecha —vista de **cuadrícula**, vista de **lista** y **ordenar por nombre / por tipo**—, recordados entre
  visitas (`flip.mediaView` y `flip.mediaSort` en `localStorage`, como `EditorState.mediaViewMode`).
- **Vista de lista** nueva: fila con miniatura de 56×32 (o el icono del tipo), nombre, `tipo · duración` y los botones
  «+» y «⋯», como el `listDelegate` del escritorio. Se sigue pudiendo arrastrar a la línea de tiempo.
- **Sin resultados**: «Ningún medio coincide con «…»» en vez de una lista vacía.
- Comprobado en el navegador con dos archivos reales (un MP4 y un WAV) contra la web desplegada: buscador, las dos
  vistas, el orden por tipo (video antes que audio), la búsqueda que deja un solo resultado y el aviso sin resultados.
  `tsc` limpio y las 99 pruebas en verde.

**Lo que falta de Medios** (lo siguiente, en este orden):
1. **Carpetas**: «Nueva carpeta» en la cabecera, la ruta sobre la cuadrícula (`BinBreadcrumb.qml`), mover medios y
   carpetas, renombrar y borrar. Es lo que da sentido a la vista de **árbol**, que por eso aún no está.
2. **Importar partido**: el botón del escritorio tiene dos mitades (archivos / carpeta entera).
3. **Mover a carpeta** desde el «⋯» de cada medio.

## PARA SEGUIR (traspaso del 2026-10-19, de Claude a DeepSeek): leer esto primero

### Regla número uno (Jorge, dicha dos veces)
**«Replica la app de escritorio».** La web tiene que verse y comportarse **exactamente** como el escritorio:
misma estructura, mismos iconos, mismos nombres, y cada botón abre lo mismo. Antes de dar por terminada una
pantalla, abrir el `.qml` del escritorio que le corresponde y compararlo **pieza por pieza** (orden, textos,
medidas, qué pasa al hacer clic). Los nombres en español salen de `Flip/i18n/drift_es.ts` (buscar el
`<context>` del archivo QML; ojo con los que tienen `<comment>`, por ejemplo «Stickers» en la fila de categorías
y «Pegatinas» en la pestaña). Si CapCut o Filmora ya resolvieron algo, se copia.

### Dónde está todo
- Repo de la web: `Downloads\FlipStudio\codigo\flipstudio-app`, rama **`web/paridad-1`** (todo subido; último
  commit `c6ede`). No hay PR a `main` todavía: la rama está desplegada tal cual.
- Repo del servidor: `codigo\flipstudio-api`, rama **`stock-0.15`** (desplegada; último commit `df65e`).
- Este plan: `Flip/docs/paridad-web.md`, rama `flip/v0.18.2`. **Actualizarlo en cada tanda** y subirlo.
- Escritorio de referencia, en `Flip/src/qml/`: panel izquierdo `AssetsPanel.qml`; Stock en `components/assets/`
  (`MarketTab`, `StockHome`, `StockBrowser`, `StockThumb`, `StockRequestsDialog`); cuenta en
  `components/AccountDialog.qml`; cabecera `EditorHeader.qml`; inicio `components/StartScreen.qml`; panel derecho
  `PropertiesPanel.qml`; colores e iconos `Theme.qml`.

### Cómo probar y publicar la web
1. `cd flipstudio-app`, luego `npx tsc -b` (**no** `npx tsc --noEmit -p .`: ese no revisa nada), `npx vitest run`
   (99 pruebas) y `npx oxlint` (hay avisos viejos; que no salgan errores nuevos).
2. En el navegador: `npx vite --port 5183` y un script de Playwright dentro de `scripts/` (usa `playwright-core`,
   ya instalado; el script tiene que estar dentro del repo para encontrarlo). Para no tocar la cuenta de Jorge,
   simular el servidor con `page.route("https://api.getflipstudio.com/v1/**", ...)` y poner una sesión falsa en
   `localStorage["flip.account"]` = `{accessToken:"a.eyJleHAiOjk5OTk5OTk5OTl9.b", refreshToken:"r", user:{...}}`.
   Ejemplo: `scripts/check-stock-ui.mjs`. Para crear un proyecto: clic en `.home-create-btn`.
3. Publicar: `bash deploy/deploy.sh` (compila con `npm run build` y cambia la carpeta entera en el VPS).
4. Si se toca la CSP (`deploy/nginx-editor.conf`): copiarla al VPS en `/etc/nginx/snippets/flipstudio-editor.conf`,
   guardar antes una copia (`/root/...bak-<fecha>`), correr `nginx -t` y `systemctl reload nginx`. Todo dominio
   nuevo del que la web cargue imágenes o audio, o al que haga `fetch`, tiene que ir en
   `img-src`/`media-src`/`connect-src`, o el navegador lo corta con «Failed to fetch» (eso era lo que rompía el
   inicio de sesión).
5. Pedirle a Jorge que recargue con **Ctrl+F5**.

### Hecho hoy (2026-10-19) y desplegado
- Entrar con Google: CSP arreglada, vuelve al mismo proyecto y la foto se ve como en el escritorio. **Jorge lo probó: funciona.**
- Stock completo como el escritorio, más Pexels/Pixabay, «Pide una plantilla» y «Mi cuenta» (Favoritos y Descargas).
  Probado solo con datos simulados: **falta que Jorge lo pruebe con su cuenta**.
- Panel izquierdo igual que el escritorio: fila de 9 categorías con icono, lista lateral, y LUTs, Efectos de color
  y Máscaras. El detalle de cada cosa está en las tandas de arriba.

### Lo que sigue, en este orden
1. **Comparar por dentro cada pestaña del panel izquierdo** con el escritorio (es lo que Jorge espera ahora), una
   por una, y corregir lo que no coincida: Medios (`MediaBin.tsx` contra la pestaña media de `AssetsPanel.qml`:
   cabecera con importar, vista en cuadrícula o lista, filtros por tipo), Música y Efectos de sonido
   (`LibraryPanels.tsx`), Voz (`VoicePanel.tsx`), Texto (`TextPanel.tsx`), Subtítulos (`SubtitlesPanel.tsx`),
   Transiciones (`TransitionsPanel.tsx`), Efectos (`EffectsPanel.tsx` contra `EffectBrowser`: el escritorio tiene
   el buscador arriba y chips con las categorías de su catálogo), Pegatinas y Formas. En el escritorio las pestañas
   de catálogo **no tienen cabecera con título** (`assetsHeader` se oculta y el buscador ocupa ese lugar); en la web
   casi todas tienen un `panel-head` con el nombre: quitarlo donde el escritorio no lo tiene.
2. **El panel derecho** (propiedades) contra `PropertiesPanel.qml`: pestañas, iconos y orden según el tipo de clip
   (video, imagen, audio, texto, capa de ajuste).
3. **La cabecera** contra `EditorHeader.qml` (Jorge ya pidió Inicio, Guardar, Video y Descargar app a la derecha,
   junto a Exportar; mirar qué más tiene el escritorio) y **el inicio** contra `StartScreen.qml` (el escritorio
   tiene una tarjeta de la cuenta en el inicio; la web no).
4. **Etapa 3: plantillas de escena** en la web, con el mismo paquete que el escritorio
   (`Flip/tools/scene_templates/FORMAT.md`; el zip se baja con `/v1/market/downloads`, `delivery: "scene-template"`).
   Hace falta: abrir el zip, crear la composición en el cabezal y los huecos «Tu foto aquí» (`placeholderId`), que
   se rellenan con medios. Cuando esté, **Mis plantillas** deja de ser `NotYetPanel` y en Stock las plantillas dejan
   de decir «app» (`canUseInWeb` en `src/stock/stock.ts`).
5. **Plantillas de efectos** (Intensidad, Caída, Ritmo; `EffectTemplateTag` en el escritorio): llenan la pestaña
   Plantillas de efectos.
6. **Efectos de audio** (Web Audio: eco, reverberación, ecualizador…) y **Escenas** (detectar dónde empieza cada
   toma), para que esas dos pestañas dejen de ser `NotYetPanel`.
7. **Favoritos en la cuenta:** hoy la web los guarda en el navegador (`src/layout/favorites.ts`, clave
   `flip.favorites`). El servidor tiene `GET/PUT /v1/me/favorites` con los grupos del escritorio: hay que traducir
   los nombres de grupo de la web a los del escritorio y sincronizar.
8. Lo demás de la tabla de arriba (efectos y transiciones que faltan, antes y después, contadores, IA en el
   navegador, 13 idiomas), en el orden aprobado de abajo.

### Trampas que ya costaron tiempo hoy
- `npx tsc --noEmit -p .` no revisa nada en `flipstudio-app`: usar `npx tsc -b`.
- Desde Git Bash, un `python - <<'EOF'` largo y con comillas puede romperse («unexpected EOF»): escribir el script
  en un archivo y correrlo con `python -I archivo.py`.
- Python en Windows escribe CRLF: abrir con `newline=""` para no cambiar los fines de línea. Este
  `paridad-web.md` y `CLAUDE.md` están en CRLF.
- La CSP del editor corta en silencio todo dominio que no esté en la lista (sale «Failed to fetch»).
- Los archivos de `api.getflipstudio.com/plantillas/` necesitan `Access-Control-Allow-Origin` para el `fetch` de
  la web. Ya está puesto en el nginx del servidor (y en `flipstudio-api/deploy/nginx-api.conf`); si alguien vuelve
  a generar ese sitio con certbot, comprobar que siga.
- El servidor manda los errores en `{detail}` (Stock) o en `{error}` (cuentas); `apiGet`/`apiPost` ya los muestran.
- No usar la cuenta real de Jorge en las pruebas automáticas: simular el servidor (punto 2 de «Cómo probar»).

## Orden aprobado por Jorge (2026-10-19)
1. **Que se vea igual:** tema turquesa, inicio, menú arriba con atajos y fila de categorías completa; y proyectos
   `.flip` (abrir `.flip`/`.drift`, guardar `.flip`).
2. **Cuenta y Stock:** Google + todo Stock desde `api.getflipstudio.com`.
3. **Plantillas de escena** con el mismo paquete que el escritorio.
4. **Completar efectos y transiciones** escritos desde cero, con antes y después.
5. **Comportamiento de CapCut** que falte: congelar, cerrar huecos, tetris, selección de pistas, curvas de velocidad.
6. **IA en el navegador:** RIFE, texto con IA y caras/retoque. Profundidad y quitar ruido al final.

## Primer paso (hecho el 2026-10-19)
- ❓ resueltos leyendo el código de la web y comprobando en el navegador (ver la tabla).
- Etapa 1 en la rama `web/paridad-1` de `flipstudio-app`, desplegada con `deploy/deploy.sh`.
- El escritorio lleva el arreglo de «Actualizar a …» en la rama `flip/v0.18.2` (commit `28ed5`), sin compilar.
