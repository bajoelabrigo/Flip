# Historia de Flip Studio

Bloques que salieron de `CLAUDE.md` por espacio (2026-10-17). Se conservan tal cual: sirven
para entender por qué el código está como está, no como instrucciones del día a día.

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


---

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


---

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


---

### 0.16.0 PUBLICADA (2026-10-18) — Menú como en Filmora y CapCut
- Rama `flip/v0.16.0` → **PR #23** → `main`; **tag `v0.16.0`**. Release (run 39108213510) con instalador, portable y
  `SHA256SUMS`; copia en `versiones\FlipStudio-0.16.0` (hashes comprobados). Novedades de la web desplegadas
  (`flipstudio-web` `15d44`). MSIX: `msstore.yml` run 39111195833 → `tienda\FlipStudio-Store\paquete-0.16.0`.
- **Menú arriba** (`AppMenuBar.qml`, Windows/Linux; macOS sigue con su menú nativo en `Main.qml`): Archivo, Editar,
  Herramientas, Ver, Avanzado, Ayuda; cada entrada es una acción que ya existía, con su atajo
  (`EditorState.shortcutFor`). Junto al menú, Ajustes/Extras/Agente solo con icono; el botón Stock de la cabecera se
  oculta (Stock está en la fila de categorías).
- **Fila de categorías** sobre el panel de recursos (`AssetsPanel.qml`: `categories`, `showCategory`,
  `lastTabInCategory`): Medios (Medios, Escenas), Stock, Audio (Música, Efectos de sonido, Voz, Efectos de audio),
  Títulos (Títulos, Subtítulos), Transiciones, Efectos, **Filtros** (LUTs = `FiltersTab.qml`, Efectos de color =
  `EffectBrowser` en la categoría `color`), Stickers (Pegatinas, Formas, Máscaras) y Plantillas (**Mis plantillas** =
  escenas de Stock y propias, **Plantillas de efectos**; `TemplatesTab.showModeChips`). La barra lateral lista las
  pestañas de la categoría con nombre y se oculta si hay una sola. En la hoja de Android no cambia.
- **Iniciar sesión para exportar y para Stock** (`SignInRequiredDialog.qml`, desde `EditorHeader.exportVideo`; en
  Stock también los efectos de sonido). Todo sigue gratis y el aviso lo dice primero. Una build sin cuentas exporta
  como antes. **Notas para la certificación cambiadas** en `docs/store-listing.md`.
- **Arreglos:** cerrar huecos al **borrar** (`deleteSelectedClip`, prueba `deleteRipplesFollowers`; reproducido en la
  0.15.0); el panel de propiedades ya no salta de página con la rueda (Jorge: confunde; el panel izquierdo sí sigue
  pasando de categoría); actualizaciones en cada arranque y cada 6 h (`UpdateChecker::scheduleStartup`).
- **Probado en ventana** con el portable (menús, categorías, Filtros, Plantillas, cerrar huecos, rueda, Exportar con
  sesión). En la prueba salieron y se arreglaron: **las tarjetas de LUT no recibían el clic** (Filtros y también
  Ajustar › LUT, o sea desde antes): ahora usan `TapHandler`/`HoverHandler` como `AssetDragSource`; los menús leían
  `EditorState.canUndo`, que **no existe** (es `undoAvailable`/`redoAvailable`; el menú de macOS tenía lo mismo).
- **Falta (Jorge):** TXT `version` = 0.16.0; subir el MSIX con las notas (712/1500) y las **notas de certificación
  nuevas**; si la 0.15.0 sigue en certificación, esperar o reemplazarla (entonces juntar las novedades de las dos);
  probar el aviso de inicio de sesión (cerrar sesión → Exportar → iniciar sesión → se abre Exportar).
- **Siguiente (0.17), pedido por Jorge:** marca «IA» + «?» en lo de IA que ya tenemos (local, sin internet);
  transiciones con IA (RIFE); texto con IA simple; panel izquierdo que abra con la fila de categorías completa;
  congelar fotograma y mover clip con cerrar huecos **como CapCut**; modo oscuro y pantalla de inicio **como
  Filmora** (colores medidos en sus capturas: paneles `#181c1f`, menús `#202427`, inicio `#0a0d0f`, acento turquesa
  `#55e5c5`; preguntar si el acento pasa a turquesa o queda el amarillo); **cerrar el editor vuelve al inicio**; y
  **todos los pendientes viejos** (traducir lo nuevo de la 0.16 a los otros idiomas y «Same as project» en Exportar,
  selector de idioma del primer arranque, contadores animados, las 9 pistas FMA, texto como máscara, quitar
  imperfecciones, voz con IA del editor web). Exportar 4K/8K: **probado por Jorge, funciona**. Regla de Jorge: si
  CapCut/Filmora ya resolvieron cómo se comporta algo, se copia.
- **Trampas nuevas:**
  - Con el editor de Jorge abierto, **no usar llamadas MCP** contra una app de prueba con ventana (`--mcp-stdio` se
    adjunta a «un editor abierto» y podría ser el suyo): armar el proyecto con `--headless` (`save_project`), abrir
    la prueba con ese archivo y manejarla solo con clics y capturas.
  - Restaurar el registro **sin la clave `account`**: importar la copia quitándole esa sección y borrar los valores
    nuevos (`recentMeta`), para no devolver un token de Google ya rotado.


---

### 0.15.0 PUBLICADA (2026-10-18) — Stock para creadores: 300 plantillas youtuber, contadores y kits
- Rama `flip/v0.15.0` → **PR #22** → `main`; **tag `v0.15.0`**. Release publicado (run 39094220184) con instalador,
  portable y `SHA256SUMS`; copia en `versiones\FlipStudio-0.15.0`. **MSIX** en
  `tienda\FlipStudio-Store\paquete-0.15.0\FlipStudio-0.15.0.0-x64.msix` (run 39094247870). Novedades de la web
  desplegadas (`flipstudio-web` commit `248aa`).
- **CI:** dos ensayos en verde sobre la rama (39082599750 y 39093137986: compilación + 16 suites + instalador y
  portable). **Ojo:** el run del tag tardó más de una hora en el paso `Build` (caché de dependencias fría); no es un
  fallo, pero no asustarse.
- A: menú de Stock con chips bajo «Todos» (`MarketTab.qml`, `CategoryScrollOn` en `StockBrowser.qml`), hover en
  todas las tarjetas, **Halloween fuera** (índices, generadores, kit, temporada del servidor; lo borrado está en
  `tienda\plantillas\quitado-halloween`; Día de Muertos se queda). Categorías nuevas `youtuber` y `counter` con su
  nombre en `SceneTemplateCatalog.cpp` y su traducción.
- B: **300 plantillas de estilo youtuber** (categoría `youtuber`; miniaturas en `thumbnail`, intros y finales en
  `intro`/`outro`). C: 43 sonidos, 40 superposiciones ×2 y 24 marcos para la cámara, 23 transiciones, 20 contadores
  y 24 tercios de redes. D: 29 kits en `tools/stock_kits/kits.py` (los 390 elementos existen en el índice final).
- **Auditoría de marcas de las fotos de muestra: TERMINADA.** 781 fotos revisadas una por una entre 19 tandas de
  agentes, **46 fotos más bloqueadas** en `kit.BLOCKED` (Costa, Toyota, Apple, Dell, Disney/Mickey, Adidas, Schwinn,
  SHUA, Ibanez, Gretsch, Shure, Puma, THRASHER, Ruffino, matrículas…) y **177 cambios de foto** en los módulos con
  `fix_blocked_samples.py`; tarjetas rehechas (`stale_renders.py` da 0 desactualizadas) y `check_blocked.py` prueba
  que ninguna plantilla usa una foto bloqueada. `merge_audit.py --apply` vuelca los informes en `kit.py`.
  - **Un solo `BLOCKED`:** `templates_y2.py` tenía su propia lista y se desincronizaba; ahora es `kit.BLOCKED`.
  - **12 muestras eran PNG con extensión `.jpg`** (`friends-03` y `y6-h-hands-06` con alfa): las dos renombradas a
    `.png` (`sample_file()` prueba `.png` antes de `.jpg`) y diez reencodadas a JPEG. `read_image` se negaba a
    abrirlas y los agentes las saltaban.
  - Decisión de Jorge: kits de fecha **solo con calendario del hemisferio norte**; contadores **con cortes** (animar
    los números en el motor queda para otra versión).
- **i18n:** los 13 idiomas cubren 4.140 elementos y 151 categorías (`build.py --strict` sin faltantes), con la
  categoría `youtuber` y las 300 plantillas nuevas.
- **Contenido desplegado en el VPS** (`api.getflipstudio.com/plantillas/`, 5,5 GB): solo se subieron **1,6 GB
  (2.837 archivos cambiados)** con `tools/scene_templates/publish_delta.py` + `apply_delta.sh` (clon por enlaces
  duros, `tar --unlink-first` y swap de la carpeta entera). Comprobado en vivo con `verify_published.py`: 1.221
  plantillas (300 `yt-*`), zips y miniaturas idénticos byte a byte, packs al día, 29 kits, i18n 4.140 y cero
  elementos de Halloween.
- **Servidor `stock-0.15` DESPLEGADO** (PM2, health `{"ok":true}`): sin Halloween (temporada y sinónimo).
- **Trampa nueva:** `scp` a un **nombre que ya existe** en `/tmp` se queda escribiendo sin que el tamaño avance (el
  archivo viejo conserva tamaño y fecha). Subir con un nombre nuevo.
- **Jorge (2026-10-18):** TXT `version` = 0.15.0 (comprobado en DNS) y **MSIX 0.15.0 enviado a certificación**
  (la 0.14.0 ya estaba lista). `flipstudio-web` (`248aa`) y `flipstudio-api` `stock-0.15` → `main` (`a4a75`) en GitHub.
- **Aviso:** la sesión de Google de la app se cayó durante las pruebas (el servidor revoca la familia cuando llega un
  `refresh_token` ya usado, y las pruebas de ventana restauran el registro). Hay que **volver a iniciar sesión** con
  Google la primera vez que se abra la 0.15.0; no afecta a nada más.

