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
| Fila de categorías sobre el panel de recursos | 0.16 | 🟡 | La fila está (Medios, Títulos, Audio, Stickers, Efectos, Transiciones) y recuerda la última pestaña de cada una; faltan las categorías Stock, Filtros y Plantillas, que aún no existen en la web |
| Panel izquierdo con barra de iconos e inspector derecho con su barra | 0.9.x | ✅ | |
| Idiomas de la app (13) | sí | ⬜ | La web está solo en español: no tiene capa de traducción |
| Proyectos `.flip` (abrir `.flip` y `.drift`, guardar `.flip`) | sí | ✅ | Abre los dos (documento + tabla de medios + blobs incrustados, que se guardan con el proyecto) y guarda `.flip` |

### Cuenta y Stock
| Función | Escritorio | Web | Notas |
|---|---|---|---|
| Iniciar sesión con Google | 0.10 | ✅ | `src/account/account.ts` + `AccountButton`: PKCE, vuelta a `/editor/`, canje en el servidor y token con refresco. El servidor usa el cliente web de Google (`GOOGLE_WEB_CLIENT_ID`) |
| Stock (plantillas, música, sonidos, LUT, looks, estilos y animaciones de texto, transiciones, formas, stickers, superposiciones, fondos, contadores, kits) | 0.12–0.18 | 🟡 | Panel propio con búsqueda y chips por tipo; «Usar» ya funciona con **música, sonidos, stickers, superposiciones, fondos y filtros**. Plantillas, looks, estilos de texto, transiciones y formas se ven marcados «app»: solo en el escritorio |
| Inicio de Stock tipo tienda, búsqueda, favoritos y «Pide una plantilla» | 0.14 | ⬜ | |
| Biblioteca de la cuenta («Mis descargas») | 0.12 | ⬜ | |
| Pexels y Pixabay | 0.10 | ⬜ | Ya están detrás del servidor |

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

### Lo siguiente de la etapa 1 que queda
- Las categorías **Stock**, **Filtros** (LUT y efectos de color en una sola) y **Plantillas**, cuando existan en
  la web (etapa 2).
- La rueda que pasa de una categoría a la siguiente (`CategoryScrollOn.tsx` ya existe para las bibliotecas).
- Traducir la web a los 13 idiomas: hoy son textos en español a pelo.

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
