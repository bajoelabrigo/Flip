# Flip Studio — cambios propios

Flip Studio es un fork de Drift. Esta sección lista lo que Flip Studio cambia respecto a Drift; debajo sigue el
registro heredado de Drift.

## 0.17.0 — IA local, inicio como Filmora y comportamiento de CapCut

- **Transición con IA** (`engine/FrameInterpolator`, RIFE 4.25 MIT en ONNX, extra `transiciones.ia`, tipo
  `interp-model`): `AppController::addAiTransitionAfter` escribe 1 s de fotogramas intermedios con `MatteWriter`
  (modo color) y los inserta entre los dos clips, corriendo el resto.
- **Texto con IA** (`engine/TextEmbedder`, paraphrase-multilingual-MiniLM-L12-v2 int8, extra `texto.ia`, tipo
  `text-embed-model`; tokenizador Unigram propio, igual al de Hugging Face en las pruebas): `addAiText` elige el estilo
  más cercano con descripciones de ambiente (`kStyleHints`).
- **Quitar imperfecciones** (`effects/face_blemish`) y tarjeta en Retoque › Piel.
- **Marca «IA»** (`components/AiBadge.qml`) en la barra lateral, las páginas del panel de Video y la barra de la línea
  de tiempo.
- **Inicio como Filmora** (`StartScreen.qml`) y **tema turquesa** predeterminado (`Theme.qml`, `menuBackground`,
  `home*`); el submenú Color se arma desde `Theme.colorThemes`.
- **La X del editor vuelve al inicio** (`Main.qml onClosing`, `quitApp`; el apagado de Windows sigue cerrando:
  `main.cpp commitDataRequest`). Panel de recursos con la fila de categorías completa (clave nueva `assetsWide`).
- **Vistas previas al pasar el mouse** (`StockThumb.hasMotion`, `SceneTemplateBrowser`) y antes/después en los LUT
  (`BeforeAfterImage.qml`).
- **Contador animado** (`TextStyle.counter`, `counterTextAt`, prueba `counterTextCountsInTheTextsFormat`).
- **Como CapCut:** congelar fotograma en la misma pista corriendo el resto; mover con «Cerrar huecos» cierra la pista
  de video (prueba `moveWithRippleClosesTheTrack`).
- **Traducciones** de lo nuevo de la 0.16 y la 0.17 en 11 idiomas (`tools/i18n/ui_todo.py`).

## 0.16.0 — Menú como en Filmora y CapCut

- **Menú arriba** (`AppMenuBar.qml`, Windows y Linux; macOS sigue con su menú nativo): Archivo, Editar,
  Herramientas, Ver, Avanzado y Ayuda, cada entrada una acción que ya existía, con su atajo
  (`EditorState.shortcutFor`). Junto al menú, Ajustes, Extras y Agente quedan solo con icono y el botón Stock de la
  cabecera se va a la fila de categorías.
- **Categorías sobre el panel de recursos** (`AssetsPanel.qml`): Medios, Stock, Audio, Títulos, Transiciones,
  Efectos, Filtros, Stickers y Plantillas. La barra lateral lista las pestañas de la categoría abierta con su nombre
  y se oculta cuando hay una sola; volver a una categoría abre su última pestaña. En la hoja de Android no cambia.
- **Filtros** (`FiltersTab.qml`): la galería de LUTs en el panel, aplicada al clip seleccionado (`color.lut`), y
  «Efectos de color» (el navegador de efectos en su categoría Color).
- **Plantillas › Mis plantillas y Plantillas de efectos**: `TemplatesTab.showModeChips` apaga los chips en
  escritorio; las favoritas de plantillas de Mi cuenta abren `effectTemplates`.
- **Iniciar sesión para exportar y para Stock** (`SignInRequiredDialog.qml`): todo sigue gratis y el aviso lo dice
  primero; al iniciar sesión se abre Exportar. En Stock, también los efectos de sonido esperan a la sesión.
- **Cerrar huecos al borrar** (`AppController::deleteSelectedClip`): con el modo activado, cada tramo borrado
  corre lo que sigue en sus pistas (con el audio vinculado). Prueba `deleteRipplesFollowers`.
- **Panel de propiedades sin saltos de página con la rueda** (se quitó el «Sigue bajando para ver…»).
- **Actualizaciones**: se buscan en cada arranque y cada 6 horas (`UpdateChecker::scheduleStartup`).
- **Tarjetas de LUT** (Filtros y Ajustar › LUT) con `TapHandler`/`HoverHandler`: el `MouseArea` no recibía el clic
  en la prueba en ventana. Los menús leen `undoAvailable`/`redoAvailable` (`canUndo` no existe).

## 0.15.0 — Stock para creadores: plantillas de estilo youtuber, kits y menú con chips

- **Menú de Stock:** `MarketTab.qml` deja arriba solo Todos, Videos y Fotos (`primaryIds`); los tipos propios van en
  chips bajo Todos, con «Inicio» (los estantes) primero. `StockBrowser.qml` usa `CategoryScrollOn` sobre la vista
  activa (o `StockHome.flickable`) y pasa al siguiente tipo solo sin búsqueda y sin más páginas (`Market.hasMore`).
  Un servidor sin el tipo `all` conserva todas las pestañas.
- **Animación al pasar el mouse** (`scale` 1.02, 0.97 al presionar, `Theme.durationFast`) en `StockThumb`,
  `SceneTemplateBrowser`, `SceneTemplatePickerDialog`, Máscaras, Stickers, Transiciones, Subtítulos, `LutPage`,
  `TextLookPicker`, `VoiceChanger`, `FacePropPicker`, `MaskShapeTiles` y los favoritos de `AccountDialog`.
- **Categorías de plantillas** `counter` («Contadores») y `youtuber` («Estilo youtuber») en
  `SceneTemplateCatalog.cpp`.
- **Contenido:** 300 plantillas de estilo youtuber (`tools/scene_templates/templates_y2`…`y7`), 20 contadores y 24
  tercios de redes (`templates_c1`, `templates_c2`), 43 sonidos, 40 superposiciones ×2 y 24 marcos para la cámara con
  su propio tamaño (`tools/overlays/designs_f.py`, `designs_g.py`), 23 transiciones (`fam_youtuber.py`) y 29 kits
  (`tools/stock_kits/kits.py`, fuente de `colecciones.json`, con nombres en 15 idiomas).
- **Sin Halloween:** fuera de los índices, los generadores, `colecciones.json` y la temporada del servidor; la música
  y los estilos de terror pasan a misterio y suspenso.
- **Herramientas:** `tools/scene_templates/renderlock.py` (un render con la app a la vez entre procesos) y
  `fetch_samples.py --themes` (fotos de muestra por tanda).

## 0.14.0 — Stock completo: tipos nuevos, inicio tipo tienda y uso más rápido

- **Tipos nuevos de Stock con instalación propia:** `MarketClient::isInstalledDelivery` y
  `AppController::installStockFile` instalan `lut` (`importLut` → `AppData/luts`), `effect-preset`
  (`EffectStackStore::importFromFile` → Mis efectos), `text-style` y `text-animation`
  (`TextPresetStore::importFromFile` → Mis estilos), `shape` (biblioteca de formas de usuario, `ShapeStyle`
  y `ShapePath`, también como máscara) y `transition` (`AddonManager::inspectUserPackage` +`installUserPackage`).
  El servidor los sirve con `delivery` por elemento (`PACKS` en `flipstudio-api/src/market.ts`).
- **Inicio tipo tienda:** `GET /v1/market/home` y `StockHome.qml` (estantes «Tendencias de la semana», «Nuevo»,
  «Para esta fecha» —`services/seasons.ts`—, colecciones desde `colecciones.json` y «Más usadas»);
  `MarketClient::home` / `refreshHome`.
- **Búsqueda en todo Stock a la vez** (`type=all`, `delivery: "mixed"`, `services/synonyms.ts`),
  **novedades** (`GET /v1/market/news`, `newsCount` / `newsSummary` y `markNewsSeen`),
  **pedidos** (`/v1/market/requests` con votos, `StockRequestsDialog.qml`) y
  **favoritos en la cuenta** (`GET|PUT /v1/me/favorites`, `fetchFavorites` / `pushFavorites`).
- **Tarjetas con la forma de cada elemento:** `StockBrowser.qml` (`aspectOf` / `tileAspect`) y
  `StockThumb.qml`, que usa `thumb_wide_url` / `preview_wide_url` cuando la tarjeta es apaisada (el servidor los
  sirve desde `thumbWide` / `previewWide` del índice). Vista previa de audio al pasar el mouse y contador de usos
  (`compactCount`).
- **Uso más rápido de las plantillas:** `fetchTemplateSuggestions` («Usar con mis fotos…», por cantidad de fotos y
  orientación), cambio de plantilla conservando el relleno (`SceneTemplates` vuelve a llenar por número de hueco),
  cortes al ritmo de la música (`analyzeBeats`, con 120 BPM fijos si no hay golpes), formulario de textos de la
  plantilla (`TemplateFillPanel.qml`) y **Mi marca** (logo, colores y tipografía, `brandRole` en las plantillas de
  Negocios).
- **Categorías nuevas de plantillas** en `SceneTemplateCatalog.cpp` (`slideshow`, `lowerthird`, `transition`,
  `story15`, `ad6`, `thumbnail`) y filtros de plantillas en el servidor (formato, duración, cuántas fotos pide, con
  o sin música).
- **Contenido:** 883 plantillas, 222 stickers, 200 superposiciones verticales y 200 horizontales, 200 sonidos,
  200 fondos y 200 horizontales, 328 cortes de música, 200 LUTs, 209 looks, 200 estilos y 200 textos animados,
  200 transiciones y 200 formas, con sus nombres en los 15 idiomas de la app (`tools/stock_i18n`).
- **Arreglo:** `publish.py` de las plantillas conserva `colecciones.json` y el `addedAt` de cada plantilla.

## 0.13.0 — Retoque de cuerpo y cabello, plantillas propias y Stock › Animaciones

- **Retoque › Cuerpo y Cabello:** `engine/BodyLandmarker` (MediaPipe Pose sin detector + Selfie Multiclass),
  `engine/PoseTrack` (sidecar en `AppData/posetracks`, `Clip::poseTrackPath`), efecto `body.reshape`
  (`"requires": "pose"`) y `hair.color` en una capa de ajuste con la máscara del pelo (`BodyController`).
- **Plantillas propias:** convertir en hueco / texto editable, «Guardar como plantilla…», «Mis plantillas»
  (borrar las propias) y aviso de tipografías que faltan.
- **Stock › Animaciones:** 65 stickers Lottie propios con colores como slots (`sid`) y botón a LottieFiles.
- Las tarjetas de Retoque se aplican en C++ (`applyRetouchLook`): `addEffect` movía la selección y el panel de
  Video se descargaba a mitad del clic.
- **Arreglo:** `MatteWriter` redondea a pares (una foto de 867 px no abría el codificador; afectaba a «Quitar fondo»).

## 0.12.0 — Varias pistas, 2K/4K/8K, plantillas en Medios y Stock › Plantillas

- **Varias pistas desde su cabecera:** Mayús (rango) y Ctrl (sueltas), borrar y agrupar (`selectTrackHeader`,
  `removeSelectedTracks`, `groupSelectedTracks`).
- **Exportar 2K, 4K y 8K:** presets por el **lado corto**, el compositor dibuja al tamaño final (`kMaxExportScale`)
  y el diálogo cambia a H.265 cuando H.264 no llega.
- **Plantillas de escena:** composición en el cabezal, huecos (`placeholderId`, `fillTemplateSlot*`), panel
  «Plantilla» y Plantillas › Escenas; el asset `Composite` sale en Medios y «Quitar plantilla» devuelve el clip.
- **Stock › Plantillas** servido por `api.getflipstudio.com` (`delivery: "scene-template"`, biblioteca por cuenta).
- Tema y tarjetas: `Theme.scrimColor` y `scrimStrong` con el alfa en su sitio (`#AARRGGBB`).

## 0.11.0 — Plantillas editables, plantillas como composición y fotogramas en la pista

- **Plantillas de efectos editables:** `drift::EffectTemplateTag` en cada efecto de una plantilla (se guarda; copiar o guardar como preajuste lo quita). Efectos › Plantilla: Intensidad, Caída, Ritmo (`setEffectTemplateShape` / `setEffectTemplateRhythm`, que analiza la música si hace falta) y «Quitar plantilla» (`removeEffectTemplate`). `refreshTemplateSpans` rehace los golpes al cortar, recortar, estirar o mover la capa.
- **Plantillas como composición:** `buildCompositeFromClipIds` (lo usa también `makeCompositeFromSelection`). Una plantilla de un clip crea «Plantilla: …» con el clip y su capa de ajuste encima; las 10 de recorte meten el video oculto, la persona, el fondo, los clones y sus carriles de máscara. Dentro de una composición no se anida otra: la capa va en su propia pista. Las que cambian la velocidad siguen en el clip.
- **Fotogramas en la pista, como en After Effects:** `Track::keyframesExpanded` (se guarda; sin deshacer), `trackKeyframeRows`, `animatedPropertyLabel`, `setKeyframeEasingAt` (lineal, suave, entrada o salida suave, mantener) y `addClipKeyframeAt`; `TrackKeyframeRows.qml` y el triángulo en `TrackHeaderColumn`. `previewMoveClipKeyframe` conserva la curva del fotograma.
- **Editor de curvas opcional:** preferencia `ui/curveEditorVisible` (apagada) con botón en la barra; la franja se oculta sin dejar su espacio (también la de subtítulos).
- **Mi cuenta:** `AccountAvatar`, `AccountDialog` con Favoritos por grupo y miniaturas (`assetFavoriteIds`) y el historial de descargas de Stock (`MarketClient`, `market/history`).
- `tools/e2e/mcp_e2e.py`: `drag`, `dblclick` y capturas que incluyen los menús emergentes.

## 0.10.0 — Cuenta de Google, Stock (Pexels y Pixabay) y estadísticas anónimas

- **Servidor propio** `api.getflipstudio.com` (repo privado `flipstudio-api`): cuentas, estadísticas y el contrato de Market (`docs/marketplace/openapi.yaml`) sobre Pexels y Pixabay.
- **`AccountController`:** Google con PKCE y redirección a `127.0.0.1` (el código se canjea en el servidor; sin secretos en el `.exe`), sesión de 15 min con refresco rotado y guardado con DPAPI, cerrar sesión y borrar la cuenta. Si `QDesktopServices` no abre el navegador, se abre el navegador predeterminado directamente (`AssocQueryStringW`) y se ofrece «Copiar el enlace».
- **`AccountWelcomeDialog`** tras el idioma (una vez) y sección **Cuenta** en Ajustes.
- **`InstallStats`:** instalación, actualización y uso diario con un UUID aleatorio; interruptor (encendido por defecto); `FLIP_NO_STATS` lo apaga en pruebas; la instalación se liga a la cuenta al iniciar sesión.
- **Stock:** la pestaña Market heredada usa la cuenta (`MarketClient::setAccount`, sin la firma HMAC ni el id derivado del equipo), botón en la barra, aviso de licencias propio, aviso «Se agregó a Medios» con «Ver», y al cambiar de Fotos a Videos se cancela la búsqueda anterior (`setActiveTypeId`).

## 0.9.9 — Capas de ajuste como en Photoshop y Agrupar

- **Máscara de una capa enlazada:** `laneAdjustmentChain` lleva las máscaras de cada capa de un carril junto a sus efectos; `GpuLayer::effectScopes` las aplica a su tramo de la cadena (`buildLayerTarget` mezcla por cobertura con `mixByCoverage`). Antes se descartaban y el ajuste cubría todo el clip. El visor (`maskEditorState`) muestra sus asas sobre el clip.
- **«Aplicar a»** (`AdjustmentTargetSection.qml`): todo lo de abajo o un solo clip de abajo, para capas de efectos y de máscara (`adjustmentTargetState`, `setAdjustmentTarget`: un paso de deshacer y conserva la selección). La pestaña Capa de ajuste sale también en los carriles; intensidad y mezcla, solo en las sueltas.
- **Agrupar / Desagrupar** en el menú de clic derecho con varios clips (`makeCompositeFromSelection` / `ungroupComposite`, que devuelve los clips sin renderizar; `flattenComposite` sigue como «Acoplar composición»).
- Al cambiar «Aplicar a», la máscara de la capa pasa del marco del clip al lienzo (o al revés) sin moverse en pantalla.
- General: tipo de clip traducido para composición («Grupo»), vector, modelo 3D y PDF.

## 0.9.8 — Capas de ajuste profesionales, LUT y máscaras de capa

- **Capas de ajuste:**
  - `Clip::disabled` (interruptor, se salta en `FrameCompositor` y en `laneMasksAt`);
  - pestaña propia `AdjustmentLayerInspector` (nombre, intensidad animable, mezcla, aviso de capa vacía);
  - modo de mezcla `SoftLight` («Luz suave»);
  - se agregan desde el **+** (`NewTrackMenu`, `addAdjustmentClip`) y con clic derecho sobre foto, video o texto (cubre el tiempo del clip).
- **Color:** `color.basic` gana `whites`, `blacks` y `fade`; los números de `AdjustInspector` se escriben; restablecer Luz y Color por separado.
- **LUT:**
  - `core/CubeLut` (parser .cube 3D/1D con `DOMAIN_*`, errores traducidos, `lookup` trilineal, `resolve` por nombre);
  - efecto `color.lut`, con la textura sacada del parámetro de archivo (`GpuEffectTextureSpec::fromParameter`, `GlRuntime::lutTexture`);
  - biblioteca en `AppData/luts`, seis looks de `tools/luts/make_luts.py`, página `LutPage.qml` con miniaturas reales.
- **Máscaras de capa:**
  - `Mask::expand` y `Mask::opacity` (animables), `MaskShape::LinearGradient`;
  - `Clip::extraMasks` y `maskFocus` (la máscara enfocada es la que editan el panel, el visor y los fotogramas clave);
  - `Clip::masksLimitEffects`: `buildLayerTarget` mezcla el resultado de los efectos por cobertura en vez de recortar el clip;
  - `MaskShapeTiles.qml`, compartido por Video › Máscara y Ajustar › Máscara (que en una capa agrega o cambia su máscara).
- **Efectos:** `stylize.film_grain` y viñeta con cantidad, tamaño y suavidad.
- **Crear composición** (`makeCompositeFromSelection`): ocupa el lugar de la pista más baja de la selección (antes un texto solo caía en la primera pista de video libre, bajo una capa de ajuste) y quita las pistas que deja vacías.
- **Paneles:**
  - la rueda recorre las páginas de la pestaña antes de la siguiente;
  - Texto (panel izquierdo) usa `CategoryScrollOn`;
  - tras cada cambio de página o categoría la rueda espera a que pare (`settling`), así un giro rápido no se salta varias.
- **Arnés e2e:** `--window`, `--keep`, `--attach`, capturas por `PrintWindow`, y clics (también derechos) y rueda enviados a la ventana.

## 0.9.7 — Lo que Jorge encontró usando la 0.9.6

- **Imágenes con las páginas de video.**
  - `inspectorCaps` da a `ClipType::Image` `maskable`, `adj:videoEffects` y `videoTools`.
  - `linkedMaskClips` acepta imágenes.
  - `SegmentationController` recorta fotos: lee la imagen una vez (`sourceFrame`), pasa el modelo una sola vez y repite la máscara en cada fotograma.
- **`Track::allowsClipType`:** una pista de video acepta `ClipType::Image`. El compositor y el mezclador ya lo soportaban, porque los importadores ponen imágenes ahí.
- **`moveClipToNewTrack`:** soltar un clip encima de la primera pista o debajo de la última crea una pista de su tipo.
- **`relocateLinkedAdjustments`**, en `normalizeProjectStructure`: los ajustes vinculados (efectos, máscaras) siguen a su clip cuando cambia de pista. Antes se quedaban en un carril de la pista vieja y dejaban de aplicarse.
- **`secondsToUs` redondea** en vez de truncar. Un clip soltado justo al borde de otro se quedaba 1 µs dentro, y la comprobación de solapes lo empujaba detrás.
- **Cabecera de pista:**
  - la rueda ya no cambia la altura en toda la cabecera, solo sobre la línea inferior, que también se arrastra;
  - las pistas de audio tienen un menú `⋯` con Altura (0,6/1,0/1,6) y Tamaño de la forma de onda (`Track::waveformScale`, 0,3/0,6/1,0, solo visual).
- **`PropertiesPanel`:** seguir girando la rueda al final de una pestaña (360 de `angleDelta`) abre la siguiente, y al principio, la anterior.
- **Máscaras:**
  - `Mask::smooth` (Pluma: Catmull-Rom cerrada sobre los puntos de la forma libre);
  - `MaskShape::Text` con `Mask::text` (`QPainterPath::addText` ajustado al rectángulo);
  - las dos entran en la clave de caché de la máscara;
  - los controles muestran el valor real de la máscara y no el predeterminado.
- **Favoritos** (`AssetFavoriteButton`) en las fichas de Retoque (`retouch`, con sección Favoritos) y del Modificador de voz.
- **Botón Actualizar siempre visible** en `EditorHeader`. En la copia de la Store abre `ms-windows-store://pdp/?productid=9NZZJ9MRGT0B`.
- **Temas de color:** `PreferencesController::colorTheme` (`ui/colorTheme`) y `Theme.colorThemes`, con seis acentos y el tinte de las superficies oscuras.
- **`PreviewTransportBar`:** botón para volver al espacio de trabajo que corresponde al lienzo cuando hay uno fijado que no coincide.
- **Barra de recursos** ordenada por temas: audio junto, con Voz, y Plantillas debajo de Efectos de audio.
- **«Formatos compatibles»:** cada tipo va con sus formatos debajo, a todo el ancho.
- **Instalador:** el arranque tras una actualización silenciosa lleva `runasoriginaluser`. Elevado, Windows bloqueaba arrastrar archivos desde el Explorador.
- **`drift_es_CO.ts`:** las 123 entradas sin terminar que `lupdate` rellenaba con conjeturas toman el texto de `drift_es` y quedan terminadas. `lrelease` incluye las sin terminar, así que pisaban la traducción buena.

## 0.9.6 — El texto como en CapCut

- `TextInspector.qml` pasa a las páginas de CapCut: Básico, Burbuja, Efectos y Animación.
  - Básico agrupa:
    - fuente, tamaño, B/U/I, mayúsculas/minúsculas, color, espaciado y alineación;
    - Estilo preestablecido;
    - las secciones con interruptor Trazo, Fondo, Brillo, Sombra y Curva, que editan la capa de ese tipo;
    - Transformación y Mezcla;
    - lo que antes era la página Estilo, plegado en Avanzado.
- `TextStyle` suma `textCase`, que se aplica al maquetar sin cambiar el texto y carácter a carácter para no mover los índices.
- El fondo suma:
  - `boxStyle` (bloque o línea) y `boxShape`;
  - `boxPaddingX/Y`, que si no se tocan caen en `boxPadding`;
  - `boxOffsetX/Y` y `boxBorderColor/Width`.
  - Solo se escriben si se usan, así que los proyectos viejos no cambian.
- `SkiaTextPainter::drawBackground` dibuja el fondo por bloque o por línea, con desplazamiento, borde y las formas de burbuja de `bubblePath()`.
- `core/TextQuickStyles` reúne dos catálogos:
  - 41 estilos rápidos, que mantienen la fuente;
  - 32 burbujas.
  - Sus miniaturas salen de `image://textlook/quick:<id>` y `bubble:<id>`.
- Favoritos (`EditorState.isAssetFavorite` y `AssetFavoriteButton`) en:
  - Música y Efectos de sonido;
  - los paquetes de estilos de texto y las plantillas de subtítulos;
  - las páginas Burbuja, Efectos y Animación del texto, con su filtro Favoritos.
- "Guardar como mi estilo…" también al final de Básico.
- `Main.qml` ya no aplica las fracciones guardadas de los paneles antes de que la ventana llegue a su estado final (maximizada). Antes se convertían en píxeles contra la ventana sin maximizar, y cada arranque guardaba fracciones más chicas.
- El estado vacío de Medios no se sale por encima del panel.

## 0.9.5 — Ajuste de color, música libre y los catálogos en español

La 0.9.4 no se publicó por separado: sale dentro de esta.

- Pestaña **Ajuste** (`AdjustInspector.qml`) con Básico, HSL, Curvas, Círculo cromático y
  Máscara, sobre los efectos nuevos `color.basic`, `color.hsl`, `color.curves` y `color.wheels`.
- Pestaña **Música** (`SoundEffectsTab` con `music: true`) para el extra `musica.libre`.
- Los nombres de los catálogos en JSON (efectos, transiciones, efectos de audio, plantillas,
  animaciones de texto y sus parámetros) pasan por `drift::catalogText()` al cargarse.
  `tools/i18n/catalog_strings.py` los lista en `src/engine/CatalogStrings.cpp` para lupdate,
  bajo el contexto `Catalog`; hay que volver a correrlo al añadir o renombrar una entrada.
- Se incluyen `face_eyeliner`, `face_eyeshadow`, `face_brow_tint`, `face_eye_color` y
  `face_teeth_whiten` (de los extras de Drift, GPL): Retoque los usaba y no venían con la app.
- `addSoundEffect` espera a que el análisis del archivo dé la duración antes de colocar el clip;
  antes una canción recién importada entraba con los 5 s del marcador provisional.
- `LottieHoverSprite` esperaba `AnimatedSprite.status`, que no existe; la hoja pasa antes por un
  `Image` oculto.
- Las tiras de páginas de Video y Ajuste pasan a dos líneas en vez de cortar el texto, y las
  categorías largas se recortan dentro del panel.

## 0.9.4 — Retoque como en CapCut y el español completo

- `PreferencesController::installUiTranslators()` instala siempre el catálogo base del idioma
  (`drift_es.qm`) y uno regional solo encima, cuando coincide territorio o escritura. Antes
  con "Español (Colombia)" elegido (la única opción latinoamericana del selector) la app cargaba
  solo `drift_es_CO.qm`, que tenía la pestaña Video sin terminar, y la mostraba medio en inglés.
- La página Retoque de `VideoInspector.qml` pasa a Rostro / Cuerpo / Cabello con Estilos
  automáticos, Piel, Funciones y Maquillaje. Casi todo son ajustes de `face_retouch` que
  reutilizan el que ya lleva el clip.
- `AssetCategoryChips` reparte las categorías en filas (como Texto) y las pliega con un chevron;
  los grupos de emojis la usan también.
- `HoverPop` anima stickers y emojis bajo el ratón; `image://lottie`
  (`LottiePreviewImageProvider`) reproduce los stickers animados en su tarjeta.
- Transiciones: `fold` dibujaba el entrante siempre encima y `glass_wipe` mezclaba al revés.
  Las once nuevas tienen `preview_strip.png`, generadas con `tools/transitions/make_strips.py`.

## 0.9.3 — el panel de video como el de CapCut

- El panel de video se ordena en las cuatro pestañas de CapCut (**Básico**, **Eliminar fondo**,
  **Máscara**, **Retoque**) dentro de una sola pestaña "Video" (`VideoInspector.qml`). Cada página
  reutiliza los inspectores que ya existían en vez de duplicarlos: Básico compone
  TransformInspector, BlendingInspector, StabilizeInspector y EffectsInspector; Eliminar fondo
  ofrece la segmentación automática y la personalizada; Máscara las formas y `MasksInspector`;
  Retoque los efectos de rostro con sus parámetros.
  - Los clips de video declaran `videoTools` y `adj:videoEffects`, que es lo que hace aparecer la
    pestaña y permite aplicar un efecto al clip aunque viva en su carril de ajuste.
  - `VideoInspector.qml` tiene que estar en la lista `QML_FILES` de CMakeLists: sin eso no se
    compila y lupdate no ve sus cadenas, y el test de traducciones falla en los 17 idiomas con el
    contexto vacío.
- **Los efectos se pueden recortar.** `syncLinkedAdjustments()` re-estiraba cada ajuste fijado a
  la duración completa de su clip en cada edición, así que recortar un efecto se deshacía solo.
  Ahora el ajuste lleva `independentRange`, que se activa al recortarlo o moverlo por primera vez
  y desde entonces lo deja en paz.
- **Máscaras a la derecha**: la pestaña Máscaras sale también con el clip de video seleccionado y
  lista las máscaras que lleva (`linkedMaskClips()`), porque las máscaras viven en ajustes y antes
  había que saber seleccionar ese carril.
- **Diez transiciones nuevas** (39 en total), con la categoría `modern`: deslizar en los cuatro
  sentidos, girar, disolución con desenfoque, doblez, deslizamiento con onda, barrido de cristal,
  barrido orgánico y papel desgarrado. Se generan con `tools/transitions/make_transitions.py`.

## 0.9.2 — sincronización con Drift, voz con IA y PDF

- Primera sincronización con Drift (69 cambios): texto con SkParagraph (emojis de color, árabe y
  hebreo, edición sobre la vista previa), enlazar clips, clips PDF, recorte de imagen y video, fuentes
  del sistema en el selector y voz con Chatterbox.
- Windows: Skia usa DirectWrite; elegía el gestor de fuentes de Android, que no encuentra ninguna, y el
  texto sin el paquete de fuentes no se dibujaba.
- Se conservan el resaltado `*palabra*`, el selector de fuentes propio (ahora con las del sistema), las
  herramientas de subtítulos, la barra tipo CapCut y la pestaña de efectos de sonido.
- Pestaña Audio como la de CapCut: Básico (fundidos solo del sonido con `setClipAudioFade`,
  normalizar a −14 LUFS según ITU-R BS.1770 con `normalizeClipLoudness`, mejorar voz, completar canal
  con el procesador nuevo `channelfill`) y Modificador de voz (`VoiceChanger.qml`, `setVoiceFilter`):
  las voces son los efectos `voz.*` del extra "Modificador de voz" (flip-addons/voces.py, 116 voces
  hechas con los pedales del motor).
- Extras propios nuevos: "Voz con IA" (`voz.chatterbox`, decodificador exportado con
  flip-addons/tts_export.py) y "Visor de PDF" (`pdfium`, PDFium chromium/8066).
- Paquetes nuevos de modelos de IA (flip-addons/modelos.py): "Recorte de sujeto" (SAM 2.1 tiny),
  "Quitar fondo (personas)" (RVM MobileNetV3), "Retoque de rostro" (MediaPipe Face Mesh + YuNet),
  "Iluminación 3D y profundidad" (Video Depth Anything Small), "Mejorar la calidad" (4 modelos de
  Philip Hofmann) y "Reducir el ruido" (DeepFilterNet3). Todos redistribuibles (Apache-2.0, MIT,
  GPL-3.0 o CC BY 4.0) y verificados por hash contra las recetas de Drift.
- Arreglo del recorte de sujeto con SAM 2.1: era el único motor que armaba sus sesiones de ONNX
  Runtime sin pasar por `buildSessions`, así que nunca reintentaba en el procesador cuando el
  proveedor elegido solo no podía crear una sesión. La atención de SAM2 necesita una matriz de
  449 MiB en el mismo espacio de memoria, y con el proveedor de GPU la sesión no se creaba: el
  recorte fallaba en silencio (la operación respondía `ok` y el clip quedaba igual). Igual que los
  demás modelos, ahora cae a procesador y funciona.
- `inspect` informa `notice:{message,severity}` con la línea de estado de la app. Los trabajos
  largos son asíncronos y solo dejan su resultado ahí: sin esto un fallo como "Failed to load SAM2
  model" no se podía ver desde fuera, porque la operación responde `ok` y nada cambia.
- El menú del selector de fuentes se queda dentro de la ventana; los estilos "Simple" y "Negrita"
  aparecen en español.

## 0.9.1 — inicio nuevo, quitar silencios y efectos de sonido

- Pantalla de inicio al estilo CapCut (StartScreen): crear con formato, herramientas rápidas y tarjetas de
  proyecto con miniatura, duración y tamaño; botón de inicio en el encabezado del editor.
- Quitar silencios y muletillas (`cutSilencesAndFillers`, operación MCP `cut_silences`): transcribe si hace
  falta y deja solo los tramos hablados con `keepRanges`; sin modelo de voz abre Extras.
- Efectos de sonido: tipo de extra nuevo `sound-effects` (SoundEffectCatalog), pestaña en el panel de
  recursos; paquete propio de 37 sonidos sintetizados (Licencia de contenido Flip Studio).
- Extras: 21 plantillas y 13 stickers animados nuevos; los paquetes se descargan de
  bajoelabrigo/flipstudio-extras; un paquete que da 404 refresca el índice y reintenta.
- Panel de propiedades más ancho y con margen para la barra de desplazamiento; los menús contextuales se
  ajustan al texto más largo.

## 0.9.0 — extras propios

- Extras vuelve a descargar: índice en getflipstudio.com/addons/index.json y paquetes en los GitHub Releases
  de bajoelabrigo/flip-addons, firmados con la clave de Flip Studio (la app ya no confía en la de CutWire).
- Paquetes: subtítulos automáticos (Whisper small), motor de IA (ONNX Runtime 1.27.0 para procesador),
  32 fuentes de Google Fonts, 150 stickers de emojis 3D y dos packs de stickers animados (48 emojis con
  movimiento; 19 de redes sociales, flechas y efectos).
- Stickers animados: un sticker Lottie entra como animación que se repite y dura lo que un sticker; en la
  cuadrícula se ve su miniatura con una insignia ▶. Las imágenes dentro de una animación se escalan sin
  mipmaps: en algunas tarjetas gráficas se veían como un cuadro negro.
- Fuentes: selector nuevo con buscador, favoritas, recientes y categorías con nombre (limpias, impacto,
  elegantes, manuscritas, divertidas, retro); botón para importar fuentes propias (.ttf/.otf, "Mis fuentes").
  Paquete "Más fuentes" con 72 familias, todas con tildes, ñ, ¿ y ¡.
- Texto: tipo de extra nuevo, plantillas de texto ("text-styles"), listadas por categoría en el panel Texto;
  paquete con 44 plantillas animadas (fe y versículos, redes, subtítulos virales, títulos, rótulos, precios,
  frases) y 8 combinadas (título con subtítulo, rótulo de dos líneas, versículo con cita, evento…), que se
  agregan como varios textos ya ubicados y sincronizados. Las tarjetas de estilo se animan al pasar el mouse.
- Subtítulos automáticos: se elige el estilo antes de generarlos; las frases se cortan en el punto, la
  pregunta o la coma; muletillas (eh, mmm) fuera y mayúscula al inicio; diccionario propio y Buscar y
  reemplazar; emojis según las palabras (opcional); traducción al inglés encima de los originales; en videos
  verticales quedan por encima de los botones de TikTok y Reels. Seleccionar un bloque de subtítulos abre el
  editor de frases.
- Resaltar palabras: una palabra entre asteriscos (*fe*) se pinta con el color de acento en cualquier estilo;
  regla nueva "Palabras clave". Los nombres de las reglas de acento están traducidos.
- Sincronización por palabra: con el extra "Sincronización por palabra (español)" (wav2vec2) cada subtítulo
  empieza y termina justo con la voz. Whisper medium como extra (más preciso; si está instalado se usa en
  lugar del small) y aceleración con tarjeta gráfica (WebGPU, experimental), que ahora también usa Whisper.
- Línea de tiempo al estilo CapCut: Dividir, Borrar izquierda/derecha, Eliminar y Marcador en la barra,
  más espacio entre botones, micrófono para voz en off, y herramientas que aparecen según el clip
  seleccionado (recortar, congelar, invertir/espejo/rotar, transcripción, quitar fondo, extraer audio,
  mejorar audio con reducir ruido y mejorar voz, mejorar video).
- Vista previa: menú de zoom (Completa a 400 %) y de relación de aspecto (16:9, 9:16, 1:1, 4:5, 4:3, 21:9).
- Subtítulos: entre segmentos de Whisper ya no se pegan las palabras ("noches,que"), y la limpieza solo
  pone mayúscula donde empieza una oración.

## 0.8.3 — sin funciones rotas a la vista

- La pestaña Market (recursos, efectos de sonido y stock de Pexels) se oculta mientras Flip Studio no tenga
  servicio propio; antes mostraba "Mercado no disponible".
- Extras: sin tienda de descargas, el administrador dice "Descargas próximamente" en lugar de "No se puede
  acceder a la tienda de descargas" con un botón Reintentar que no podía funcionar. Afecta a todos los botones
  que llevan a Extras (subtítulos automáticos, fuentes, stickers, máscaras, efectos).
- Las barras de íconos de los paneles de recursos y de propiedades son más anchas (50 px): la barra de
  desplazamiento ya no tapa los íconos cuando no caben todos.

## 0.8.2 — en español y con soporte propio

- Ventana de información de depuración: los enlaces de documentación y Discord de CutWire ahora llevan a las preguntas
  frecuentes de getflipstudio.com y a soporte@getflipstudio.com.
- La sesión del servidor MCP usa su propia carpeta temporal (`flip-studio`); antes compartía `drift` con una
  instalación de Drift y podían pisarse.
- La descripción del marketplace para agentes ya no nombra a CutWire.
- Paquete de Microsoft Store con la identidad de Flip Studio (`yitoweb.FlipStudio`).
- Interfaz en español completa (es y es_CO): unos 300 textos que seguían en inglés, los 33 estilos de texto
  y el nombre "Proyecto sin título". "Media bin" ya no se traduce como "papelera" sino como "biblioteca de
  medios", y se usa "video" en lugar de "vídeo".
- Los botones de interpolación de fotogramas clave (Recto, Suave, Salto) se ajustan a su texto; antes se
  cortaban en "R…" y "Su…".

## 0.8.1 — seguridad

- Claves de API y token MCP cifrados con DPAPI en Windows (migración automática).
- Servidor MCP: límites de tamaño y rechazo de `Content-Length` inválido.
- Acciones de GitHub de terceros fijadas a un commit exacto.
- Mensajes que aún decían "Flip" en lugar de "Flip Studio".
- Botón "Acerca de Flip Studio" en Ajustes para Windows, Linux y Android (Drift solo lo tenía en macOS).

## Etapa 1 — identidad propia (2026-10-09)

- Nuevo nombre e identidad: Flip Studio (`io.github.bajoelabrigo.FlipStudio`, `flipstudio.exe`, instalador con AppId propio).
- Ajustes y datos en su propia carpeta, separados de una instalación de Drift.
- Desactivados los servicios de CutWire (add-ons, marketplace y comprobación de versión) hasta que Flip Studio tenga los suyos.
- "Acerca de" acredita a Drift / CutWire Studios y enlaza al código fuente (requisito de la GPL).
- Ícono propio de Flip Studio en Windows, instalador, Microsoft Store, Linux y Android.
- Tema oscuro por defecto (antes seguía al de Windows); el usuario puede cambiarlo en Ajustes.
- La pantalla de inicio dice "Flip Studio" (quedaba "Drift").
- Corregido: en un panel de Medios angosto, "Nueva carpeta" e "Importar" se montaban sobre el título;
  ahora pasan a solo ícono. Los botones del panel vacío se apilan cuando no caben.
- Corregido: un archivo ZIP truncado (.mogrt, .lottie, accesorios faciales) colgaba la app; ahora falla con un error y hay un límite contra "bombas ZIP".

---

# Unreleased changes

Tracks work done on `main` **since the last public release**. Use this to see what is already fixed or added before filing an issue. Cleared when a new release ships.

**Last released version:** `0.7.5`

---

## ✅ Fixed

- **macOS: AVI, MKV and WebM play in the trim and preview window.** It could only play what Apple's own player supports, so these files showed a first frame and then would not play, even though they played on the timeline.
- **The media bin's hover hint no longer covers the right-click menu.**

## ✨ Added

- **Audio effects made of pedals.** An audio effect can now be a whole pedalboard: filters, a ladder filter, drive, reverb, convolution reverb, delay, pan and gain, alongside the original effects, run in series or side by side in parallel and frequency-band splits. Build them in Drift Forge and import the `.driftfx`.
- **Modulation for audio effects.** LFOs, envelope followers and step sequencers can move any pedal's knobs over time, in step with the clip, so a wobble lands in the same place after you seek.
- **Convolution reverb.** Put a sound in a real space using an impulse response shipped with the effect: Forge has a room, a plate, a hall and a spring tank, or record your own.
- **Keyframe audio effect parameters.** The sliders of an audio effect now take keyframes on the timeline, like a video effect's.

## 🎨 Improved
