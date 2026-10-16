# CLAUDE.md — Flip Studio

Este archivo es el **mapa del proyecto**: dónde vive cada cosa, en qué estado está y las
trampas que ya nos costaron tiempo. Mantenerlo al día al cerrar cada versión.

**Regla de idioma:** todo lo que lee Jorge (respuestas, resúmenes, notas de versión,
descripciones de la Store, textos de la app) va en **español**. El código, los comentarios
y los mensajes de commit siguen el estilo del archivo que se toca — el código de Drift está
en inglés y no se traduce.

---

## Los repos y la carpeta del proyecto

Todo vive en `C:\Users\bajoe\Downloads\FlipStudio` (ordenado el 2026-10-14):

| Carpeta | Qué hay |
|---|---|
| `codigo\` | Los repos: `Flip`, `flip-addons`, `flipstudio-web`, `flipstudio-app`, `flipstudio-api` |
| `secretos\` | Claves privadas (`addon-signing.key`, y los `.env` del servidor). Nunca se commitea nada de aquí |
| `tienda\FlipStudio-Store\` | Paquetes MSIX (`paquete-<versión>`), textos y capturas de la ficha |
| `versiones\` | Copias de cada versión publicada (`FlipStudio-<versión>`) y `FlipStudio-backup-releases` |
| `pruebas\` | Portables para probar en ventana (el ejecutable tiene que estar fuera del repo) |

Los portables de prueba viejos se borraron; las versiones publicadas siguen en los releases de GitHub.

| Repo | Qué es | Dónde se publica |
|---|---|---|
| `Flip` | App de escritorio (Qt/C++, fork de Drift) | GitHub `bajoelabrigo/Flip` — releases + Store |
| `flip-addons` | Recetas y empaquetador de los extras (privado) | Paquetes al release `packages` de `flipstudio-extras` |
| `flipstudio-web` | getflipstudio.com (privado) | VPS `holyvps` con `deploy/deploy.sh` |
| `flipstudio-app` | El editor web de `/editor/` (AGPL) | VPS, con su propio `deploy/deploy.sh` |
| `flipstudio-api` | `api.getflipstudio.com` (privado): cuentas de Google, estadísticas de instalación, stock de Pexels y Pixabay. Express + MongoDB Atlas (clúster propio `cluster0.jsfmxek`, base `flipstudio`; la cadena está en `secretos\api-claves.txt`), sobre el modelo de holyapp (`Downloads\chat-app`) | VPS `holyvps`, PM2 + nginx |

**Claves y secretos:** `Downloads\FlipStudio\secretos\addon-signing.key` (Ed25519, la
privada; la pública está en `Flip/src/engine/AddonSigningKey.h`). Nunca se commitea.

**Reglas que no cambian:**
- Los nombres internos de Drift (`drift::`, `DRIFT_*`, módulo QML `Drift`, `.drift`,
  `.driftfx`) **no se renombran**: así se pueden traer las mejoras de Drift.
- La clave de firma de Drift (`CutWire`) ya no se usa; los extras se firman con la nuestra.
- Lo de pago vive en servidores propios; las claves de API nunca dentro del `.exe`.
- Antes de publicar algo, compilarlo y probarlo en Windows.

---

## Estado (actualizado 2026-10-15)

### 0.13.0 PUBLICADA (2026-10-16): Retoque › Cuerpo y Cabello, plantillas propias, 101 plantillas, Stock › Animaciones
- Rama `flip/plantillas-propias` → PR a `main`, tag `v0.13.0`. Notas en `release-notes/0.13.0.md`; novedades para la
  Store (0.12.0 + 0.13.0, 1014 caracteres) en `docs/store-listing.md`: la 0.12.0 no llegó a subirse (Jorge: «subimos
  la versión 13 de una vez»). Extra `cuerpo.cabello` 1.0.0 publicado (paquete primero, índice después).
- Probado con el ejecutable de la build (run 38844618103): análisis, los cinco retoques y el tinte. **Falta:** mirar
  el panel en ventana (la pantalla estaba bloqueada y las capturas salían en blanco), que Jorge suba el MSIX y el TXT.

### 0.11.0 PUBLICADA (2026-10-15): plantillas editables, plantillas como composición, fotogramas en la pista
- Rama `flip/plantillas-editables` → PR a `main`, tag `v0.11.0`. Notas en `release-notes/0.11.0.md`; novedades para
  la Store (0.10.0 + 0.11.0, 996 caracteres) en `docs/store-listing.md`. **Esta sí va a la Store y al TXT `version`.**
- Release en GitHub, copia en `versiones\FlipStudio-0.11.0`, novedades en la web. **TXT `version` = 0.11.0** (Jorge,
  comprobado en DNS el 2026-10-15). MSIX listo en `tienda\FlipStudio-Store\paquete-0.11.0\FlipStudio-0.11.0.0-x64.msix`
  (run 38702261969). **Falta:** que Jorge lo suba a Partner Center.
- Probada en ventana con Jorge («funciona todo ok»):
  - plantillas de un clip y las 10 de recorte como composición «Plantilla: …» (`buildCompositeFromClipIds`);
  - fotogramas en la pista con el triángulo (`TrackKeyframeRows.qml`), editor de curvas opcional;
  - «+» amarillo en las tarjetas (`applyEffectTemplateToCurrentClip`: selección o clip bajo el cabezal);
  - plantillas de ritmo en videos mudos y fotos: ritmo fijo de 120 BPM, ♪ en la tarjeta (`followsMusic`), aviso y
    nota en Efectos › Plantilla (`EffectTemplateTag::steadyBeat`).
- **Trampa:** `finishEdit(msg)` **ignora** el texto; para que el usuario vea un aviso, `setLastMessage(msg, severidad)`.
- **Trampa:** sin música, el análisis de golpes termina vacío y `analyzeBeats` no repite el mismo tramo: cualquier
  cosa que espere golpes tiene que aceptar también `beatAnalysisCoversClip`.

### 0.12.0 en curso (2026-10-15): rama `flip/v0.12.0` (subida a GitHub)
- Los 7 puntos de abajo están hechos, cada uno en su commit (`a8d9d` tema y tarjetas, `ac720` plantillas en Medios y
  «Quitar plantilla» que devuelve el clip, `bd909` cambiar una transición, `285cb` varias pistas, `067b6` 2K/4K/8K).
- Varias pistas: clic en la cabecera, Mayús (rango), Ctrl (suelta); Suprimir y el menú las borran con sus clips;
  «Agrupar N pistas» = composición (`selectTrackHeader`, `removeSelectedTracks`, `groupSelectedTracks`).
- Exportar: las resoluciones se nombran por el **lado corto** (4K de un 9:16 = 2160×3840; antes «1080p» de un
  vertical daba 608×1080). Por encima del proyecto el compositor dibuja a ese tamaño (`kMaxExportScale` = 8).
  H.264 se niega a pasar de 4096 por lado; el diálogo cambia a H.265 de la misma familia.
- **Falta:** probar en ventana (sobre todo exportar 4K/8K con GPU y con `DRIFT_EXPORT_SWSCALE=1`), versión 0.12.0
  en `CMakeLists.txt`, `release-notes/0.12.0.md`, y el OK de Jorge.

### Etapa 2 de plantillas (en curso, 2026-10-15) — misma rama `flip/v0.12.0`
- Jorge: **al menos 30 plantillas en Stock › Plantillas**, «con calma», buenas miniaturas.
- Hecho en la app: paquete de plantilla de escena (`engine/SceneTemplateCatalog`, carpeta `scene-templates/`, tipo de
  extra `scene-templates`), `AppController::insertSceneTemplate` (composición en el cabezal; proyecto vacío toma 9:16;
  si no, `scaleTemplateLayout`), huecos = clips con `placeholderId` (se rellenan con `fillTemplateSlot*`, recorte
  «cover»; un mismo `placeholderId` repetido se rellena junto), pestaña «Plantilla» del inspector
  (`TemplateFillPanel.qml`) y Plantillas › Escenas/Efectos (`TemplatesTab.qml`, `SceneTemplateBrowser.qml`).
- **Las 32 plantillas** se generan con `tools/scene_templates/` (`scene.py` = bloques, `templates*.py` = diseños,
  `build.py` = paquetes + miniaturas/previas renderizadas por la 0.11.0 portable sin ventana; guarda y restaura el
  registro). Guía de diseño en `BRIEF.md`, formato en `FORMAT.md`. Salida fuera del repo:
  `Downloads\FlipStudio\tienda\plantillas\paquetes\<id>` (32 MB) y `catalogo-32.png`. Fotos de ejemplo (Pexels, con
  `CREDITS.json`) en `tienda\plantillas\muestras`: **solo** para miniaturas; los paquetes van con huecos vacíos.
  Música: cortes de la música libre CC0 de Flip. Tipografías: las de `fonts.basic`/`fonts.extra`.
- **Trampa:** un efecto con picos animados (`rgb_split`, `strobe_flash`, `beat_shake`, `zoom_pulse`) necesita la
  clave de caída en `"hold"`, si no sube en rampa hasta el siguiente pico y lava la imagen.
- **Trampa:** evitar fotos de ejemplo con marcas (Converse, Nike, Adidas…): revisar la cuadrícula.
- **Jorge (2026-10-15):** todas gratis, **todas en Stock** (ninguna incluida en la app), Stock pide iniciar sesión
  y **lo descargado queda en la cuenta** (como «mis materiales» de holyapp).
- **Stock › Plantillas desplegado (2026-10-15):** `flipstudio-api` `main` (tipo `template`, `delivery:
  "scene-template"`, búsqueda sin tildes, filtro «Mis plantillas», `GET /library`, `DELETE /library/:id`, modelo
  `LibraryItem` único por cuenta+elemento, se borra con la cuenta). Paquetes en el VPS en
  `/var/www/flipstudio-templates` servidos en `https://api.getflipstudio.com/plantillas/` (nginx `location ^~`:
  sin `^~` una regla de imágenes se come los `.png`). Subir: `tools/scene_templates/build.py` → `publish.py` →
  `flipstudio-api/deploy/plantillas.ps1` (cambia la carpeta entera).
- App: «Usar plantilla» baja el zip, lo instala en `AppData/scene-templates/<id>` (`installSceneTemplatePackage`,
  va antes que las incluidas) y la pone en el cabezal; las de la cuenta que faltan en el equipo salen en
  Escenas con insignia de descarga; «Mi cuenta» › Descargas muestra la biblioteca de la cuenta.
- **Falta:** probar en ventana con la build de la rama, aviso si faltan las tipografías, y que la política de
  privacidad diga que la cuenta guarda lo que bajas de Stock.

### 0.12.0 PUBLICADA (2026-10-15) — y Etapa 3 de plantillas en curso (rama `flip/plantillas-propias`)
- 0.12.0: PR #17, tag `v0.12.0`, release con instalador/portable/SHA256SUMS, copia en `versiones\FlipStudio-0.12.0`,
  novedades en la web, política de privacidad con «Tu biblioteca de Stock». MSIX: `msstore.yml` run 38808515108 →
  `tienda\FlipStudio-Store\paquete-0.12.0`. **Falta (Jorge):** TXT `version` = 0.12.0 y subir el MSIX.
- Etapa 3 (Jorge: «hagamos lo que sugeriste»): **MOGRT fuera**; **plantillas propias** (convertir en hueco /
  texto editable, «Guardar como plantilla…», «Mis plantillas», borrar las propias, aviso de tipografías que faltan);
  **Stock › Animaciones**: 65 stickers Lottie hechos por nosotros (`tools/animations`: `designs.py` + `designs2.py`,
  `build.py` renderiza tarjetas con la app, `publish.py` los deja en `publicar/animaciones`), colores como slots
  (`sid`), botón «LottieFiles» que abre su web (su licencia prohíbe servir su catálogo). **Servidor desplegado**
  (tipo `animation`, `delivery: "media"`): la 0.12.0 ya las ve y las importa a Medios.
- **Trampa Lottie:** la primera forma de una capa se dibuja **encima**: los detalles van antes que el fondo (las caras
  salían sin ojos).
- **Trampa curvas:** tangentes Catmull-Rom → Bézier = (siguiente − anterior) / 6, no / 2.

### 101 plantillas de tendencia en Stock (2026-10-15, pedido de Jorge: «surtir la tienda»)
- `tools/scene_templates/templates_t1.py` … `t5.py` (fechas especiales, ediciones de tendencia, negocios, vida y
  personas, texto/intros/cierres); guía en `BRIEF.md` › «Las 100 de tendencia». Categorías nuevas `seasonal`
  («Fechas especiales») y `business` («Negocios»), con nombre en la app (`SceneTemplateCatalog`) y en `publish.py`.
- Renderizadas con el portable de `pruebas\FlipStudio-body`, revisadas en hojas de contacto y **desplegadas**: 133 en
  Stock › Plantillas. Fotos de ejemplo nuevas (24 temas) bajadas con `fetch_samples.py`.
- **Trampa:** un canal animado vale su **primera clave** antes de ella: un pico que empieza en el s 10 deja el efecto
  al máximo los 10 s anteriores. Los ayudantes `spikes()` ponen `(0, 0, "hold")` delante.
- Para elegir el momento de una miniatura: `scan_thumbs.py` (scratch) captura un fotograma por segundo.

### Retoque › Cuerpo y Cabello (rama `flip/plantillas-propias`, 2026-10-15)
- `engine/BodyLandmarker` (MediaPipe Pose sin detector + Selfie Multiclass), `engine/PoseTrack` (sidecar en
  `AppData/posetracks`, `Clip::poseTrackPath`), efecto `body.reshape` (`"requires": "pose"`, uniforms `u_body*`),
  `hair.color` en una capa de ajuste enlazada con la máscara del pelo, `BodyController` (`EditorState.body`), MCP
  `analyze_body` / `color_hair`. Extra `cuerpo.cabello` (tipo `body-model`, app ≥ 0.13.0) preparado en flip-addons,
  **sin publicar**. Probado con el ejecutable real (cuerpo y pelo) — falta mirar el panel en ventana.
- **Arreglo:** `MatteWriter` redondea a pares (una foto de 867 px no abría el codificador; afectaba también a
  «Quitar fondo» con fotos).

### Lista de la 0.12.0 (pedido de Jorge, 2026-10-15) — TODO HECHO y publicado en la 0.12.0
1. **La composición de una plantilla tiene que aparecer en Medios**, y desde ahí poder entrar a editarla o borrarla
   con Suprimir. Hoy el asset `Composite` se crea pero Jorge no lo ve en Medios.
2. **«Quitar plantilla» (Efectos) no deshace la plantilla:** borra la capa de ajuste con la animación pero deja la
   composición «Plantilla: …». Tiene que devolver el clip original a su sitio (desagrupar) o dar las dos opciones.
3. **Tarjetas de plantillas:** la etiqueta «Necesita recorte» es tan ancha que tapa el ♪ y el botón de favorito no
   sale. Achicarla (un icono con tooltip) o moverla.
4. `Theme.scrimColor` / `scrimStrong` transparentes (ver trampas).
5. **Transiciones (Jorge, 2026-10-15, revisar mañana):** una vez colocada una transición entre dos clips no deja
   cambiarla por otra. Reproducirlo primero en ventana (soltar otra encima, elegirla en el panel, el tipo en el
   inspector) antes de tocar código.
6. **Seleccionar varias pistas (capas) desde su cabecera (Jorge, 2026-10-15):** Mayús + clic selecciona un rango
   de pistas seguidas y Ctrl + clic suma o quita pistas sueltas, como en Premiere/After Effects. Con varias
   seleccionadas: **agrupar** (composición con todo su contenido) y **eliminar las pistas completas** con todos sus
   clips (Suprimir y clic derecho). Hoy la selección múltiple es solo de clips.
7. **Exportar en 2K, 4K y 8K (Jorge, 2026-10-15):** hoy `Exporter::scaleOptions` solo ofrece la resolución del
   proyecto o menos («Skip downscale targets that would upscale»): un proyecto 1080p no puede salir en 4K. Hace falta:
   - presets 1440p (2K), 2160p (4K) y 4320p (8K) también por encima del proyecto, renderizando el compositor a ese
     tamaño (no escalar el 1080p ya hecho: textos, formas y vectores se ven nítidos si se dibujan a la resolución final);
   - códec: H.264 llega a 4096×2304 (nivel 5.2) y NVENC H.264 no pasa de 4096 de ancho; **8K exige HEVC o AV1**.
     Elegirlo solo o avisar;
   - tasa de bits sugerida por preset, memoria de GPU y tiempo de exportación (avisar en 8K);
   - el editor web ya exporta hasta 4K60 (ver `flipstudio-app`): mismo criterio de nombres.

### 0.10.0 PUBLICADA EN GITHUB (2026-10-14): cuenta de Google, Stock y estadísticas anónimas
- PR #15, tag `v0.10.0`, release con instalador, portable y `SHA256SUMS` (copia en `FlipStudio\versiones\FlipStudio-0.10.0`).
  Novedades 0.10.0 y política de privacidad nueva publicadas en getflipstudio.com. Google Cloud: app **en producción**.
- **Sin MSIX y sin cambiar el TXT `version` a propósito** (decisión de Jorge): la próxima actualización completa
  (0.10.0 + Etapa 1) es la que va al TXT y a la Store. La 0.9.9 ya está aprobada y en la Store.
- Detalles de la cuenta, el servidor y las trampas en «Pendiente» (punto 5) y en las trampas (navegador y WSA).
- **Rama `flip/plantillas-editables` (2026-10-14, noche), probada en ventana con Jorge:**
  - **Etapa 1a:** las 13 plantillas de un clip marcan sus efectos con `drift::EffectTemplateTag` (Effect.h, se
    guarda en el proyecto; copiar/preajuste la quita). Aplicadas a un video crean una **capa de ajuste propia**
    («Plantilla: …», pista nueva justo encima, misma duración: se mueve, se acorta, se corta con la tijera).
    Efectos › Plantilla: Intensidad, Caída, Ritmo (analiza la música si hace falta) y «Quitar plantilla» (borra la
    capa y su pista si queda vacía). Las que cambian la velocidad (slowmo_drop) siguen en el clip. Golpes de al
    menos 150 ms cuando el ritmo es por golpes. Prueba `effectTemplateStaysEditable`.
  - **Mi cuenta:** foto a la derecha de Exportar (`AccountAvatar`), tarjeta en la pantalla de inicio,
    `AccountDialog` con Favoritos como CapCut (chips + miniaturas de los 15 grupos; `assetFavoriteIds`) y
    Descargas de Stock (historial persistente en `market/history`, últimas 200).
- **Ojo en las pruebas:** el botón «Dividir» de la barra corta **todas** las pistas en el cabezal; para cortar un
  solo clip, la tijera.
- Al cerrar la sesión el repo se mudó a `Downloads\FlipStudio\codigo\Flip`: abrir Claude desde ahí.

### Anterior: cierre de la 0.9.9

**v0.9.6 PUBLICADA.** Ni la 0.9.3, ni la 0.9.4, ni la 0.9.5 llegaron a la Store: Jorge sube
directamente la 0.9.6, y sus notas cubren las cuatro.

### Hecho
- `main` = merge del PR #11 (`flip/v0.9.6`). Tag `v0.9.6`; release Latest con instalador, portable y
  `SHA256SUMS`. Copia en `Downloads\FlipStudio\versiones\FlipStudio-0.9.6\`.
- MSIX: `FlipStudio-Store\paquete-0.9.6\FlipStudio-0.9.6.0-x64.msix`. Notas de la Store en
  `docs/store-listing.md` (1073 caracteres; el límite es 1500).
- **Texto como en CapCut**: `TextInspector.qml` con Básico, Burbuja, Efectos y Animación.
  - Fondo por bloque o por línea, con borde y desplazamiento (`TextStyle::box*`).
  - 32 burbujas y 41 estilos rápidos (`core/TextQuickStyles`).
  - `textCase`.
- **Favoritos** (`EditorState.isAssetFavorite` / `AssetFavoriteButton`) también en Música, Sonidos,
  estilos de texto, subtítulos, burbujas, efectos y animaciones de texto.
- **Arreglo**: los paneles ya no se encogen en cada arranque. Probado: fracciones iguales en tres
  arranques seguidos.
- **Editor web** desplegado:
  - texto con Burbuja y Efectos, Ajuste de color, Música (`/musica/` en el VPS), Formas, fotogramas
    clave, exportar hasta 4K60;
  - favoritos, Mis estilos y Mis efectos, guardados en `localStorage`.
- Web `getflipstudio.com` con la 0.9.6 en `novedades.html`.

### 0.9.7 en curso (2026-10-13)
- Rama `flip/v0.9.7`, PR #12 en borrador; versión 0.9.7 en `CMakeLists.txt`; notas en
  `release-notes/0.9.7.md`.
- Los 14 puntos que encontró Jorge están hechos y probados en ventana con el portable de CI.
- **Falta:**
  - el OK de Jorge;
  - merge, tag y release;
  - el MSIX, después de que la Store apruebe la 0.9.6;
  - las notas de la Store para la 0.9.7.
- **Editor web:** rama `web/jorge-0.9.7` en `flipstudio-app`, probada en Chrome y **sin desplegar**.
  Incluye:
  - menú «⋯» de audio;
  - fotos en la pista de video;
  - pista nueva al arrastrar;
  - máscara de texto;
  - temas de color;
  - paso de sección con la rueda;
  - la escala fija al arrastrar (antes el clip salía disparado).
- **Segunda tanda (2026-10-13, tarde)**, también en la web:
  - fotos y videos en cualquier pista que no sea de audio;
  - candado de pista;
  - en los catálogos, la rueda pasa a la siguiente categoría;
  - Video › Máscara como en CapCut, con la pluma que agrega y borra puntos;
  - Retoque con fotos;
  - iconos en las acciones;
  - menú de la flecha con Seleccionar, Dividir y Seleccionar hacia la izquierda o la derecha;
  - Quitar fondo y Recortar para fotos en la barra.

  Las miniaturas de Retoque las renderiza la propia app (`resources/retouch/README.md`; la foto es CC0).
- **Tercera tanda (2026-10-13, tarde)**, también en la web:
  - fundido automático al montar el borde de un clip sobre otro, como en Sony Vegas
    (`AppController::autoCrossfadeFor`, solo con «Permitir superposición» apagado);
  - capa de ajuste en la barra por defecto; la web estrena las suyas (clip con `adjust: true`,
    `drawAdjustment` en `render/compose.ts`);
  - agrupar en la web (Ctrl+clic y Ctrl+G, por `link`);
  - archivos que faltan como en Premiere: marca «Falta el archivo», «Buscar archivo perdido…» y
    el diálogo al abrir (`MediaBinController::relinkMissing` / `relinkMissingInFolder`,
    `MissingMediaDialog.qml`; en la web, `MissingMediaDialog.tsx`).
  - En escritorio ya había agrupar: «Crear compuesto», «Transformar juntos» (Ctrl+G) y «Vincular».
- Jorge pidió (2026-10-13) probar todo y, si funcionaba, **publicarlo todo**.
- **Jorge tiene el espacio de trabajo fijado en «Horizontal»** (`ui/workspaceLayout`). Por eso un
  video 9:16 no cambiaba de diseño solo; ahora sale el botón «Espacio vertical».

### 0.9.8 PUBLICADA (2026-10-13, noche): capas de ajuste profesionales y LUT
- Rama `flip/v0.9.8` (escritorio) y `web/0.9.8` (editor web). Notas en `release-notes/0.9.8.md`.
- Jorge pidió (con dos documentos) capas de ajuste "profesionales" y un sistema de LUT, **por etapas**,
  **probando cada cambio** y **compilando el escritorio una sola vez al final**.
- Hecho, en las dos:
  - capa de ajuste con interruptor (`Clip::disabled` / `off` en la web), nombre, intensidad animable,
    mezcla y aviso cuando no cambia nada; «Luz suave» en escritorio;
  - Blancos, Negros y Desvanecer en `color.basic` / `adjust_basic`; números que se escriben;
  - LUT: `core/CubeLut` + efecto `effects/color_lut` (la textura sale del parámetro de archivo:
    `GpuEffectTextureSpec::fromParameter`, `lutTexture` en `GlRuntime`); biblioteca en
    `AppData/luts`; búsqueda por nombre (`CubeLut::resolve`); seis looks generados por
    `tools/luts/make_luts.py` (también copiados a `flipstudio-app/public/luts`).
    Web: `effects/cubeLut.ts`, `lutStore.ts` (IndexedDB `flipstudio-luts`, clave por contenido),
    textura 3D en `gl.ts`;
  - grano de película y viñeta ajustable (escritorio); la web ya los tenía;
  - el panel derecho, al bajar, recorre las páginas de la pestaña antes de la siguiente.
- **Máscaras de capa** (tercer documento de Jorge): `Mask::expand`/`opacity` (animables),
  `MaskShape::LinearGradient` ("gradient"), `Clip::extraMasks` + `maskFocus` (la máscara enfocada es
  la que editan el panel, el visor y "mask.<key>"), `Clip::masksLimitEffects` (las máscaras de un clip
  limitan sus efectos: `buildLayerTarget` mezcla por cobertura en vez de recortar). Web: `Clip.masks`
  (pila), `masksLimitEffects`, `MaskHandles.tsx` en el visor.
- Probado en ventana con el portable de CI (run 38464105571) y por píxeles con capturas reales.
- **Publicada** a pedido de Jorge («publica»): PR #13, tag `v0.9.8`, editor web desplegado (`flipstudio-app`
  `main` = `web/0.9.8`), novedades 0.9.8 en la web y la portada con `assets/shot-flip-text.webp` (Jorge no quiere
  su foto en la portada). Notas de la Store en `docs/store-listing.md`. **Falta:** el MSIX, cuando la Store apruebe.
- Segunda tanda del mismo día:
  - capa de ajuste desde el **+** (`NewTrackMenu`) y con clic derecho sobre foto, video o texto;
  - Texto (panel izquierdo) con `CategoryScrollOn`, y la rueda espera a que pare tras cada cambio (`settling`);
  - Ajustar › Máscara con `MaskShapeTiles.qml` (compartido con Video › Máscara).
- **Auditoría de «Crear composición»:** es una secuencia anidada (un solo nivel, instancias compartidas). Antes y
  después, deshacer, rehacer, guardar y reabrir, y exportar con y sin composición dan lo mismo al píxel. Se corrigió
  dónde queda: ocupa el lugar de la pista más baja de la selección y quita las pistas que deja vacías.
- **Para la 0.9.9:** traducir «Tipo: composite» en General (sale en inglés).
- **Límites conocidos:** en la web los parámetros de los efectos no se animan (solo la intensidad de
  la capa); los LUT importados en la web viven en ese navegador (se reconocen al volver a importar el
  mismo archivo).

### 0.9.9 PUBLICADA (2026-10-14): capas de ajuste como en Photoshop
- La 0.9.8 **no** fue a la Store: Jorge sube directamente la 0.9.9. Las notas combinadas (0.9.7 + 0.9.8 + 0.9.9,
  es/en) están en `docs/store-listing.md`. MSIX en `FlipStudio-Store\paquete-0.9.9\`.
- **Jorge (2026-10-14):** cambió el TXT `version` a 0.9.9 y mandó la 0.9.9 a certificación. **Microsoft la aprobó
  el mismo 2026-10-14: la 0.9.9 está en la Store.** El próximo envío lleva solo lo nuevo desde la 0.9.9.
- PR #14, tag `v0.9.9`. Notas en `release-notes/0.9.9.md`.
- **«Aplicar a»** (`AdjustmentTargetSection.qml`, `AppController::adjustmentTargetState` / `setAdjustmentTarget`):
  una capa de ajuste o de máscara va sobre todo lo de abajo (pista suelta, `AllBelow`) o enlazada a un clip (carril
  `ParentTrack` + `linkedClipId`). **Ojo:** la máscara de un carril se mide sobre el marco del clip y la de una pista
  suelta sobre el lienzo; `setAdjustmentTarget` la convierte (`remapMask`) para que no se mueva en pantalla.
- **Arreglo:** la máscara de una capa de ajuste en carril se ignoraba al plegar sus efectos en el clip. Ahora
  `GpuLayer::effectScopes` mezcla cada tramo de efectos por la cobertura de sus máscaras (`laneAdjustmentChain`).
- **Agrupar** (clic derecho con varios clips = `makeCompositeFromSelection`) y **Desagrupar** (`ungroupComposite`:
  devuelve las pistas del grupo sin renderizar; se niega si el grupo tiene movimiento, velocidad, efectos o capas
  propias). **Trampa:** `flattenComposite` **renderiza** el grupo a un video («Acoplar composición»); no es desagrupar.
- **Trampa de pruebas:** matar la app de prueba deja `recovery\autosave.json` y la siguiente apertura pregunta
  «Trabajo no guardado»; borrarlo al terminar. La prueba de estabilizar de Windows a veces falla en CI por OpenGL 3.0
  del runner: relanzar con `gh run rerun <id> --failed`.
- Falta (menor): las máscaras de video/imagen en capas de ajuste en carril no se precargan en `forEachMediaMask`.

### Pendiente
0. **Al final de todo el proyecto (Jorge, 2026-10-15):** el sistema de pagos, la tienda de cada usuario (vender sus
   plantillas) y todo lo que tiene que ver con cobrar. Hasta entonces todo lo de Stock es gratis.
1. **Hecho por Jorge (2026-10-13):** cambió el TXT `version` del DNS y mandó la 0.9.6 a
   certificación en Partner Center. **Falta:** confirmar que la certificación pase. La ficha
   actualizada (descripción, notas y 16 características, en es/es-co/en-us) está en
   `Downloads\FlipStudio\tienda\FlipStudio-Store\textos\listingData-FlipStudio-0.9.6.csv`; las capturas nuevas, en
   `FlipStudio-Store\ficha` (`Guion en Voz.jpg` es una foto suelta, no una captura de la app).
   `docs/store-listing.md` ya tiene la descripción del CSV (2026-10-13).
2. ~~Retoque Cuerpo y Cabello sin modelo~~: hecho en la 0.13.0.
3. Otros idiomas: los nombres de catálogo (contexto `Catalog`) y lo nuevo del texto solo están en
   español.
4. Web: voz con IA (TTS) espera al backend; las opciones del navegador usan espeak-ng (GPL).
5. Backend (`api.getflipstudio.com`): cuenta Google, ventas, Pexels, identificador de instalación
   y política de privacidad (ver el plan de abajo).
   - **2026-10-14:** repo `codigo\flipstudio-api` creado y probado en local (12 pruebas): cuentas de Google,
     instalaciones (anónimas sin sesión, atadas a la cuenta con sesión) y stock de Pexels y Pixabay (solo con
     cuenta). Repo privado `bajoelabrigo/flipstudio-api`. **Desplegado (2026-10-14):** `https://api.getflipstudio.com`
     (PM2 `flipstudio-api` en `127.0.0.1:3100`, `/var/www/flipstudio-api`, nginx + certbot). El `.env` sale de
     `secretos\flipstudio-api.env` (armado con `api-claves.txt` + el JSON `client_secret_*.json` de Google; Pexels
     usa la misma clave que holyapp porque Pexels da una por cuenta). Probado de punta a punta con la cuenta de
     Jorge: PKCE + loopback → login 200, `/v1/me`, Pexels y Pixabay con 30 resultados.
   - **Google Cloud:** proyecto «Flip Studio», cliente «Flip Studio Windows» (App de escritorio), en modo
     **Prueba** (solo usuarios de prueba). Publicarlo antes de la versión con inicio de sesión. Sin logo, a
     propósito (el logo obliga a revisar la marca).
   - **Trampa:** desde aquí no se puede abrir el navegador de Jorge (`start`/`rundll32` no hacen nada o cortan la
     URL en el `&`); para probar, imprimir la URL y que él la abra.
   - **Decisiones de Jorge:** la cuenta de Google se pide al primer arranque pero se puede saltar («Continuar sin
     cuenta»); sin cuenta se envían estadísticas anónimas con interruptor en Ajustes; base en MongoDB Atlas, en un
     clúster aparte del de holyapp (desde el 2026-10-14; la base de prueba que quedó en el de holyapp se borró). La cuenta se usará para su tienda personal (vender plantillas, más adelante; el pago por la web
     con PayPal, como holyapp, para no necesitar cuenta de empresa en Partner Center).
   - **App de escritorio (rama `flip/cuentas`, 2026-10-14):** `AccountController` (Google con PKCE + loopback,
     sesión con DPAPI), `InstallStats` (instalación, actualización y uso diario; interruptor en Ajustes;
     `FLIP_NO_STATS=1` lo apaga, y `mcp_e2e.py` lo pone solo), bienvenida tras el idioma
     (`AccountWelcomeDialog.qml`, una vez), sección «Cuenta» en Ajustes, y la pestaña Market heredada pasa a
     **Stock** con la cuenta (`MarketClient::setAccount`: sin HMAC ni id del equipo). El servidor cumple el
     contrato de `docs/marketplace/openapi.yaml` en `/v1/market`. CI: 17/17 pruebas y build de Windows OK.
     **Falta:** probarlo en ventana (con la pantalla de Jorge bloqueada las capturas salen en blanco, también
     con la 0.9.9: no es la app), el primer inicio de sesión real desde la app, y el OK de Jorge.
   - **Privacidad:** borrador en la rama `privacidad-cuentas` de `flipstudio-web` (**sin desplegar**). nginx ya no
     registra la IP de `/v1/installs/event` y los días de uso se borran a los 13 meses (TTL). Falta la ficha de la
     Store (`docs/store-listing.md` dice «no recoge datos personales» y «sin cuenta»).
6. **Plantillas (plan del 2026-10-14, después del servidor):** las de efectos dejan rombos en cada golpe y no
   guardan sus parámetros → sección «Plantilla» con Intensidad/Caída/Ritmo que regenera los puntos y «Quitar
   plantilla»; las de escena entran como composición con capas con nombre, huecos «Tu foto aquí» y panel
   «Rellenar plantilla»; reactivar la importación de MOGRT; LottieFiles; catálogo propio; más adelante, plantillas
   hechas y vendidas por los usuarios.
   - **Publicación por tandas (Jorge, 2026-10-14):** la 0.10.0 se publica en GitHub (tag, release y novedades
     en la web), pero **sin MSIX ni cambio del TXT `version`**. La próxima actualización completa (0.10.0 +
     Etapa 1, quizá 0.11.0) es la que va al TXT y a la Store: cada envío tarda días en certificarse.
   - **Decisión de Jorge (2026-10-14):** las plantillas también salen en **Stock › Plantillas**, como escaparate en
     línea servido por `api.getflipstudio.com` (catálogo propio, de pago y, más adelante, las tiendas de los
     usuarios), con un botón **«Usar»** que la descarga, la guarda en la pestaña Plantillas y la pone en la línea
     de tiempo como composición. La pestaña Plantillas sigue siendo «lo que ya tienes». Llega con la Etapa 2;
     `MarketClient::applyCatalog` hoy solo acepta tipos `delivery: "media"`, así que hace falta otro tipo de entrega.
7. ~~Candado para bloquear una pista~~: hecho en la 0.9.7 (escritorio y web).
8. El selector de idioma del primer arranque marca "American English" por defecto aunque el
   sistema esté en español.

---

## Lo que avanzamos el 2026-10-12

Sesión larga. Resumen de lo que se cerró, por si mañana hay que retomar el hilo:

**Se arregló el recorte de sujeto (SAM 2.1).** Era el único motor que armaba sus sesiones de ONNX
Runtime con `defaultSessionOptions` en vez de `buildSessions`, así que nunca reintentaba en el
procesador cuando el proveedor de GPU no podía crear la sesión (su atención necesita 449 MiB
contiguos). Fallaba **en silencio**. Se comprobó por partes: el export ONNX es correcto (el
pipeline completo en ONNX Runtime da máscaras que siguen a la cara, iou 0.95 en la semilla y 0.987
al propagar).

**Los fallos asíncronos ya no se esconden.** `inspect` informa `notice:{message,severity}` con la
línea de estado de la app. Fue justo eso lo que dejó ver el fallo del recorte.

**Los seis paquetes de modelos de IA se publicaron** (recorte de sujeto, quitar fondo de personas,
retoque de rostro, iluminación 3D y profundidad, mejorar la calidad y reducir el ruido), con el
índice en vivo. Se subieron a mano con reintentos porque `gh release upload` falla a la primera con
archivos grandes.

**Los efectos dejaron de ser una propiedad del clip.** `syncLinkedAdjustments()` los re-estiraba a
la duración completa del clip en cada edición, así que recortar un efecto se deshacía solo. Ahora
el ajuste lleva `independentRange`.

**Las máscaras se ven al seleccionar el clip** (`linkedMaskClips`), en vez de obligar a saber
seleccionar su carril de ajuste.

**Diez transiciones nuevas** (39 en total), con la categoría `modern`: deslizar en los cuatro
sentidos, girar, disolución con desenfoque, doblez, deslizamiento con onda, barrido de cristal,
barrido orgánico y papel desgarrado.

**El panel de video se rehizo en las cuatro páginas de CapCut** (`VideoInspector.qml`), reutilizando
los inspectores que ya existían.

**Se publicaron la 0.9.2 y la 0.9.3**, cada una con su release, instalador, portable y MSIX.

**Arnés de pruebas sin ventana** en `tools/e2e/`, con `sam2_full.py` para reproducir el pipeline de
SAM 2.1 fuera de la app y separar "el export está mal" de "la orquestación C++ está mal".

### Lo que quedó mal o a medias (no perderlo de vista)

- **El panel de video salió en inglés** según Jorge. La investigación apunta a que el catálogo sí
  está bien y él esté abriendo una copia anterior al build bueno; ver la sección de arriba.
- **La página Retoque no sigue las capturas**: Jorge espera grupos **Rostro / Cuerpo / Cabello**,
  **Estilos automáticos**, **Piel**, **Funciones** y **Maquillaje**; hoy es una lista plana de 8
  botones.
- **No se verificó a ojo nada de la 0.9.3** (ni el panel, ni el recorte de efectos, ni las
  transiciones): en esta máquina no hay compilador de C++ local, así que todo se validó por CI y
  por el ejecutable corriendo, no viendo la pantalla.
- **Calidad de transiciones viejas**: `radial_zoom_blur` tiene su "strength" fijo en el shader y el
  parámetro no se lee; `liquid_smudge` tiene 3 parámetros muertos y `particle_wind` uno.
- Las diez transiciones nuevas **no tienen `preview_strip.png`** (es opcional).

---

## Mañana (2026-10-13): usuarios, instalaciones y Pexels

Plan acordado con Jorge. **Los tres son backend**: necesitan `api.getflipstudio.com`, que ya está
en la hoja de ruta como requisito de Pexels y de las cuentas.

### 1. Cuentas de usuario — solo con Google

- **Único proveedor: Google.** Nada de correo/contraseña. Eso simplifica: no hay que guardar
  contraseñas ni gestionar recuperación.
- Hace falta **OAuth 2.0 con Google** (ID de cliente, pantalla de consentimiento) y, del lado de
  la app, un flujo de escritorio: **PKCE con redirect a `http://127.0.0.1:<puerto>` y el navegador
  del sistema**, no un WebView embebido (Google lo rechaza).
- La app guarda el **token de refresco** y lo usa contra el backend propio; el backend valida el
  `id_token` de Google y emite su propia sesión.
- **Decisión pendiente de Jorge:** qué se gana con la cuenta. Hoy la app es libre y sin cuenta, así
  que hay que definir qué desbloquea (¿sincronizar proyectos?, ¿los extras de pago?) y qué pasa si
  alguien no quiere cuenta.

### 2. Saber quién instala la app

- Es lo que Jorge pidió: **control de quién instala**.
- **OJO, esto choca con lo que la ficha de la Store declara hoy.** En
  `docs/store-listing.md` está escrito: *"no recoge datos personales, no contiene publicidad, no
  tiene compras dentro de la aplicación"*. Un identificador de instalación que se envíe al servidor
  ya es telemetría, y si se ata a la cuenta de Google pasa a ser dato personal.
- **Antes de programarlo hay que decidir:**
  - ¿Se cuenta la instalación **de forma anónima** (un identificador aleatorio que no se puede
    atar a una persona), o **atada a la cuenta**?
  - ¿Se avisa en la app y se actualiza la **política de privacidad** y la declaración de la Store?
    Si se recoge algo, la declaración **tiene** que cambiar: una ficha que dice que no se recoge
    nada y una app que sí lo hace es un problema con Microsoft, no un detalle.
- Lo primero, entonces, es un identificador anónimo de instalación y actualizar la declaración;
  atarlo a la cuenta es una decisión de producto, no un detalle técnico.
- **Pedido de Jorge (2026-10-13), para hacerlo junto con el login y Pexels:** contar **descargas,
  máquinas instaladas y actualizaciones instaladas**.
  - **Descargas:** ya se pueden leer.
    - GitHub da `download_count` por archivo del release (`gh api repos/bajoelabrigo/Flip/releases`).
      Al 2026-10-13 eran de 0 a 3 por versión, casi todas nuestras pruebas.
    - La Store tiene sus análisis en Partner Center.
    - Los registros de nginx del VPS cuentan los clics en «Descargar» de la web.
    - GitHub no separa instalación nueva de actualización: las dos bajan el mismo archivo.
  - **Máquinas y actualizaciones:** la app tiene que avisar a `api.getflipstudio.com` con un
    identificador **aleatorio y anónimo** (nada de la persona ni del equipo):
    - al instalarse (versión, Windows);
    - al actualizarse (de qué versión a cuál);
    - y como mucho una vez al día «sigo en uso», para contar las activas por día y por mes.
  - Con eso, un panel con instalaciones, activas, versiones en uso y actualizaciones aplicadas.
  - **Pendiente de Jorge:** confirmar «anónimo» y un interruptor «Enviar estadísticas anónimas» en
    Ajustes, activado por defecto. Hay que actualizar la política de privacidad y la declaración de
    la Store **antes** de publicarlo.

### 3. Pexels (stock de video y fotos)

- Ya estaba en la hoja de ruta: **requiere el backend** porque **la clave de API nunca va dentro
  del `.exe`** (es una regla que no cambia). La app le pide al backend, el backend firma con la
  clave y devuelve los resultados.
- Hay que decidir dónde se guarda lo descargado y si cuenta contra la cuota de Pexels por usuario
  o global.
- **Ojo con la licencia de Pexels**: permite uso gratis, pero no revender ni redistribuir el
  material como stock; conviene leerlo antes de exponerlo como herramienta.

### Orden sugerido

1. **Levantar `api.getflipstudio.com`** con HTTPS y una base mínima: es el bloqueante de los tres.
2. **El identificador anónimo de instalación** (lo más pequeño, y obliga a resolver la parte
   legal de la ficha).
3. **Pexels**, que solo necesita la clave en el servidor.
4. **Las cuentas de Google**, que son las que más piezas tienen (OAuth, PKCE, sesión, refresco).


---

## El panel de video salió en inglés: qué se sabe (2026-10-12)

> **RESUELTO (2026-10-12, tarde): la causa era la carga, no el catálogo.** El instalador real
> de la 0.9.3 (mismo hash que el portable del release) muestra el fallo. Jorge tiene guardado
> `language = es_CO` (Español (Colombia), elegido en el selector de idioma, `languageChosen =
> true`, en `HKCU\Software\Flip Studio`), así que la app cargaba solo **`drift_es_CO.qm`**, que
> tiene la pestaña Video sin terminar: por eso salían en español justo "Quitar fondo", "Máscara" e
> "Imagen o video como máscara…" (las únicas con texto en `es_CO`). Reproducido con PySide6 sobre
> los `.qm` reales; un es-PE sin idioma elegido sí carga `drift_es.qm`. Antes se creyó que el
> sistema es-PE caía en `es_CO`: era falso. Arreglo en
> `PreferencesController::installUiTranslators()`: el catálogo base del idioma (`drift_es`) se
> instala siempre, y uno regional solo encima si coincide el territorio o la escritura exactos.
> Lo de abajo es la investigación previa, que daba por bueno el catálogo y no miraba qué archivo
> se cargaba.

Jorge reportó que en la 0.9.3 las páginas del panel de video salen en inglés y solo "Máscara" en
español. **La investigación no encontró un fallo en el catálogo**, y esto es lo comprobado:

- `i18n/drift_es.ts` tiene las cuatro **traducidas**: Basic→Básico, Remove background→Eliminar
  fondo, Mask→Máscara, Retouch→Retoque, y también todos los títulos de sección (Skin retouch→
  Retoque de piel, Bigger eyes→Ojos más grandes…).
- `lrelease` sobre ese `.ts` da **4296 traducidas y 0 sin terminar**, y el `.qm` resultante se
  vuelve a volcar con `lconvert` y contiene las cuatro.
- El log del build que publicó la 0.9.3 (`38215230650`) dice:
  `drift_es.qm … Generated 4296 translation(s) (4296 finished and 0 unfinished)`.

O sea: **el `.qm` que se publicó sí lleva las traducciones**. La causa más probable es que Jorge
esté abriendo una copia anterior a ese build (el portable de prueba que le pasé antes de la
0.9.3), o que su app no esté cargando el catálogo español. Su sistema es es-PE y no tiene idioma
forzado en el registro (**falso**: sí lo tiene, `language = es_CO`; ver el RESUELTO de arriba), así que
debería cargar `drift_es.qm` desde `:/i18n`.

**Para la próxima actualización:**
1. **Confirmar con el instalador 0.9.3 real** (el `.exe` del release, no un portable viejo) antes
   de tocar nada. Si ahí sigue en inglés, entonces el problema está en la carga, no en el catálogo.
2. **Alinear la página Retoque con las capturas de Jorge**: él espera grupos **Rostro / Cuerpo /
   Cabello**, **Estilos automáticos**, **Piel**, **Funciones** y **Maquillaje**. Hoy la página es
   una lista plana de 8 botones con otros nombres (Skin retouch, Body reshape…). Traducirlos está
   bien, pero los **nombres y la agrupación** no son los de CapCut.
3. "Body reshape" debería ser **"Cuerpo"** para coincidir con la captura (hoy dice "Reformar el
   cuerpo").
4. La página **Básico** no incluye **Flujo óptico** (gap ya conocido: es render, no un modelo).

### Comprobar los catálogos sin depender de CI

En Windows no hay `lupdate`, así que el ciclo es: bajar un Qt desechable y correrlo a mano.

```powershell
# 1. lupdate/lrelease (una vez; .qttools/ y .qtmingw/ están en .gitignore)
py -m pip install aqtinstall
py -m aqt install-qt windows desktop 6.10.3 win64_mingw --archives MinGW qttools qtbase qtdeclarative -O .qtmingw

# 2. Regenerar los catálogos tras añadir qsTr (y NO editar un .ts a mano: lupdate tiene que
#    reproducirlo byte a byte o el test Translations falla en los 17 idiomas)
.\.qtmingw\6.10.3\mingw_64\bin\lupdate.exe src i18n -no-obsolete -locations none -ts (gci i18n\drift*.ts).FullName

# 3. Comprobar que quedó estable (dos pasadas iguales) y ver qué traduce de verdad
.\.qtmingw\6.10.3\mingw_64\bin\lrelease.exe i18n\drift_es.ts -qm .qmcheck\drift_es.qm
.\.qtmingw\6.10.3\mingw_64\bin\lconvert.exe -i .qmcheck\drift_es.qm -o .qmcheck\dump.ts
```

**Trampa que costó dos ciclos de CI:** editar un `.ts` a mano (o con un script de reemplazo) puede
dejar el archivo en una forma que `lupdate` no reproduce, y entonces el test Translations falla
aunque el contenido se vea correcto. El orden es: `lupdate` primero, después rellenar
traducciones, después `lupdate` otra vez para confirmar que no cambia nada.

### Dónde vive cada cosa en la interfaz (verificado en el código)

Cuesta encontrarlas porque **se crean en un panel y se editan en el otro**:

| Función | Se crea en | Se edita en |
|---|---|---|
| **Las cuatro páginas de video** | Pestaña **Video** del panel de la derecha (sale con un clip de video seleccionado) | Ahí mismo: Básico, Eliminar fondo, Máscara y Retoque |
| **Máscaras** (formas) | Pestaña **Video → Máscara**, o el panel de recursos → "Máscaras"; también se arrastran sobre el clip | Pestaña **Máscaras** del panel de la derecha |
| **Eliminar fondo** | Pestaña **Video → Eliminar fondo** | La máscara resultante queda como carril de ajuste propio |
| **Retoque facial** | Pestaña **Video → Retoque** | Ahí, más el escaneo de caras en Efectos |
| **Imagen o video como máscara** | **"Máscaras" → "Imagen o video como máscara…"** | Pestaña "Máscaras" |

Las máscaras también se pueden soltar **directamente sobre la línea de tiempo**
(`TimelinePanel.qml` llama a `addMaskToClip` / `addMaskLaneClip`).

### Gaps conocidos de las cuatro secciones de video (auditado contra CapCut)
- **Básico**: falta **flujo óptico** (interpolar fotogramas). Es render, no un modelo.
- **Máscara**: falta **texto como forma de máscara**.
- **Retoque**: falta **quitar imperfecciones** (manchas y arrugas).
- De nube de CapCut y no replicable: quitar objetos con IA, ampliar a 4K con IA, remix,
  contacto visual, sincronización labial.
- Ideas sin modelo todavía: separar audio (voz/música) y traductor de video.

---

## Rutina de publicación (lo que funcionó en la 0.9.2)

1. **Compilar y probar antes de etiquetar.** `gh workflow run build.yml --ref <rama> -f
   platforms=windows` para un ensayo; el tag es público en cuanto termina `release.yml`.
2. **Extras, en este orden y no en otro:** subir los `.driftpkg` al release `packages`
   **primero**, y solo después copiar `flip-addons/dist/index.json` a
   `flipstudio-web/addons/index.json` y desplegar. El índice apunta a las URLs de los
   paquetes: publicarlo antes deja 404 para todos.
3. **PR a `main`** (patrón de la casa: rama `flip/vX.Y.Z` → PR → merge).
4. **Tag `vX.Y.Z`** y push: `release.yml` se dispara solo, verifica que el tag coincida con
   `project(... VERSION ...)` de `CMakeLists.txt` y que exista `release-notes/<version>.md`,
   compila y publica el release.
5. **MSIX:** `gh workflow run msstore.yml --ref main -f ref=vX.Y.Z -f version=X.Y.Z.0`, y
   bajar el artefacto a `FlipStudio-Store\paquete-<version>\`.
6. **Jorge:** cambiar el TXT `version` en el DNS (Hostinger) y subir el MSIX a Partner
   Center. Recordar que el campo "Novedades de esta versión" tiene **límite de 1500
   caracteres**.

Los textos de la ficha de la Store están en `Flip/docs/store-listing.md` (hay que
actualizarlos en cada versión: la sección de notas todavía decía 0.8.1 al cerrar la 0.9.2).

---

## Pruebas

**Arnés sin ventana** (`Flip/tools/e2e/`, ver su README): `mcp_e2e.py` corre una lista de
llamadas JSONL contra `flipstudio.exe --headless --mcp-stdio` y guarda cada respuesta.
`calls_four.jsonl` es la comprobación de humo de las cuatro secciones de video.

- **Correrlo sin sandbox de archivos.** Los sidecars (mattes del recorte, `facetracks`)
  van a `%APPDATA%\Flip Studio\Flip Studio`, y bajo un sandbox de archivos `avio_open`
  falla con `Permission denied (error -13)`. Eso **no** significa que la función esté rota.
- **Mover `APPDATA` no sirve:** Windows resuelve esa carpeta por la API del shell, no por
  la variable de entorno.
- Los modelos no van dentro del ejecutable: `--stage` apunta a
  `flip-addons\build\stage` y exporta los `DRIFT_*_MODEL_DIR`.
- `sam2_full.py` reproduce el pipeline de SAM 2.1 entero en ONNX Runtime, sin la app: sirve
  para separar "el export está mal" de "la orquestación C++ está mal".

---

## Trampas que ya nos costaron tiempo

**Colores de 8 dígitos en QML son `#AARRGGBB`, no `#RRGGBBAA`.** `Theme.scrimColor`, `scrimStrong` y `waveformColor` venían de Drift al revés (transparentes o amarillos); corregidos en la 0.12.0 (`a8d9d`). Al escribir un color con alfa, el alfa va primero.

**Restaurar el registro tras una prueba puede cerrar la sesión de Google de Jorge.** El servidor rota el token de
refresco en cada uso y, si llega uno ya usado, cierra toda la familia (2026-10-14 22:34 UTC pasó). Si la app de
prueba usó la cuenta (Stock, Mi cuenta), exportar `HKCU\Software\Flip Studio\Flip Studio\account` **después** de la
prueba, restaurar la copia y volver a importar esa clave. Comprobar en Mongo (`sessions`, `revokedAt`) si hay dudas.

**La app escribe en el registro de Jorge aunque se lance para pruebas, incluso sin ventana:** anota el proyecto
de prueba en `recentProjects`/`lastSessionPath` y guarda preferencias. Quitar solo `mcp/startOnLaunch` no basta:
con la app cerrada, `reg delete "HKCU\Software\Flip Studio" /f` y `reg import` de la copia, y comparar el
`reg export` con la copia. Borrar también la carpeta del proyecto de prueba en `%APPDATA%\Flip Studio\Flip Studio\projects`.
`mcp_e2e.py` acepta además `--keep` (deja la ventana abierta), `--attach <pid>` (sigue en esa ventana) y
`click` con `"button": "right"`.

**Probar la interfaz en ventana sin tocar el mouse de Jorge:** `mcp_e2e.py --window` abre el editor con
el proyecto, se conecta a él (`--mcp-stdio` sin `--headless` se *adjunta* a un editor abierto) y acepta
las pseudo-llamadas `screenshot` (PrintWindow: solo la ventana, nunca el escritorio), `click` y
`wheel` (mensajes enviados a la ventana, coordenadas de la captura). Necesita **Acceso de agente**
encendido (`mcp/startOnLaunch = true` en el registro): encenderlo solo con copia del registro y
restaurarlo al terminar. Nunca usar capturas de pantalla completa: una vez salió el navegador de Jorge.
- Para preparar proyectos de prueba: `load` acepta un `.json` con el documento (Project::toJson); el
  `.drift` es "DRIFTPRJ" + cabecera de 52 bytes + manifiesto zstd con `document`.
- Las pruebas de GPU de `tst_engine` se **saltan en CI** (Linux sin GPU): lo de GPU se verifica con
  capturas `capture full:true` del ejecutable real en Windows.

**«No se pudo abrir el navegador» al iniciar sesión con Google (2026-10-14).** En el equipo de Jorge ninguna
app abría `accounts.google.com` (Flip, Antigravity, el plugin de YouTube de OBS): `ShellExecute` daba error 2
solo para dominios de Google. Causa: un **Subsistema de Windows para Android** roto (registrado, sin archivos)
reclamaba 64 dominios como «app para sitios web»
(`HKCU\Software\Classes\Local Settings\…\SystemAppData\<paquete>\AppUriHandlers`). Se desinstaló con
`Remove-AppxPackage` y volvió a funcionar. Para otros usuarios, `AccountController::openBrowser` abre el
navegador predeterminado directamente (`AssocQueryStringW`) si `QDesktopServices` falla, y ofrece «Copiar el
enlace». Pistas para diagnosticar: las capas implícitas de Vulkan (OBS, TikTok LIVE Studio) se inyectan en toda
app que usa la GPU, pero **no** eran la causa.

**Nada que se lance desde `Flip\.e2e-app` puede escribir archivos.** Le pasa incluso a la 0.9.6
copiada ahí, y aunque se lance sin sandbox o desde una tarea programada. No es la app: el
ejecutable tiene que estar fuera del repo, por ejemplo en `Downloads\FlipStudio\pruebas\FlipStudio-0.9.7-prueba`.
- Síntomas: el escaneo de caras da `Could not write …facetracks…`, `capture full:true` da
  `Could not write PNG` y `save_project` no deja archivo.

**Los nombres de los catálogos en JSON se traducen aparte.** Efectos, transiciones, efectos de
audio, plantillas y animaciones de texto (y sus parámetros) vienen de `effect.json` & cía., que
`lupdate` no lee. `tools/i18n/catalog_strings.py` los copia a `src/engine/CatalogStrings.cpp`
(contexto `Catalog`) y los cargadores los pasan por `drift::catalogText()`. **Al añadir o renombrar
un efecto o una transición: correr ese script, después `lupdate`, y traducir en `drift_es.ts`.**
Si no, el nombre nuevo sale en inglés.

**Un botón de la interfaz puede apuntar a un efecto que no existe y no avisar.** Retoque llamaba a
`face_eyeliner` y otros cuatro que no venían con la app: cinco botones mudos durante dos versiones.
Para comprobarlo, `list_effects` por MCP en el ejecutable real.

**Todo motor de ONNX Runtime tiene que armar sus sesiones con `drift::ort::buildSessions`,
nunca con `defaultSessionOptions` a mano.** `buildSessions` es lo que reintenta en el
procesador cuando el proveedor elegido no puede crear la sesión. SAM2 era el único que no
pasaba por ahí y su atención necesita 449 MiB contiguos, así que fallaba **en silencio** en
equipos donde todos los demás modelos funcionaban.

**Un trabajo asíncrono que falla no tiene dónde decirlo.** La operación responde `ok`, la
línea de tiempo no cambia y no hay campo de progreso que consultar. Por eso `inspect`
informa siempre `notice:{message,severity}` con la línea de estado de la app. Si una
operación asíncrona parece no haber hecho nada, **leer `notice` antes que nada**.

**`inspect` sin `clips:true` no emite `items`.** Un `tracks:[{clips:1}]` sin `items` es
normal, no un clip perdido. (Este error nos costó un diagnóstico equivocado.)

**Algo en el VPS revierte `index.json` si se reemplaza el archivo suelto.** Pasó con
`flipstudio-web/addons/index.json`: el `cp`/`install` se aplicaba y a la sesión siguiente
volvía el contenido viejo (mismo hash, misma fecha), mientras que otros archivos nuevos en
esa carpeta sí persistían. Lo que funciona es el **swap de directorio completo** que hace
`deploy/deploy.sh` (descomprimir al lado y `mv`). No se investigó la causa.

**`git add -A` en el repo de la app mete el portable extraído.** Hay `.e2e-app/` y
`FlipStudio-Portable-*.zip` en el `.gitignore`, pero conviene mirar `git status` antes de
commitear: una vez entraron 1854 archivos y hubo que reescribir el commit.

**`gh release upload` de paquetes grandes falla a la primera.** Reintentar
(`tools/e2e/upload_extras.ps1` lo hace hasta 4 veces).

**La subida por SSH:** `git push` falla si el credential helper de msys no puede crear sus
named pipes. Se resuelve con `gh auth token` en un `http.extraheader`, o usando `gh` para
las operaciones de GitHub.

**El nginx del VPS (1.18) no conoce `.mjs` ni `.wasm`** y los manda como `octet-stream`; con
`nosniff`, el navegador se niega a ejecutar un módulo así (`Failed to fetch dynamically imported
module`). El editor declara los tipos para `/editor/ort/` en `deploy/nginx-editor.conf`. Tras
arreglarlo hay que recargar sin caché: el navegador recuerda la respuesta mala.

**Subtítulos del editor web:** Whisper base con transformers.js **4.3.0** (la 4.2.0 no carga el
decodificador de 8 bits y en WebGPU fp16 transcribe basura). El modelo vive en el VPS en
`/var/www/flipstudio-models/modelos/whisper-base/` (servido en `/modelos/`), fuera del editor
para que `deploy.sh` no lo vuelva a subir. Para probar en local: servir una copia y arrancar con
`FLIP_MODELS=http://127.0.0.1:8766 npx vite`.

**En Windows no hay WSL.** El `deploy.sh` de los sitios usa `tar | ssh`; desde PowerShell se
arma el tar con `tar.exe` y se sube con `scp`, y la mitad remota va en un `.sh` aparte
(`tools/e2e/deploy_remote.sh`).
