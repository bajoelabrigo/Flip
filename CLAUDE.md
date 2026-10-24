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
- **REGLA (Jorge, 2026-10-22): todo cambio o actualización se comprueba EN VENTANA antes de publicar**, viendo con
  los propios ojos que quedó como queremos: abrir cada panel o función que toca el cambio, comprobar que se vea
  lo que tiene que verse, hacer clic y ver el resultado en la vista previa. Las hojas renderizadas, el MCP sin
  ventana y las pruebas de CI **no** lo reemplazan (la 0.20.0 salió con Texto › Animación vacío por eso).
  Portable en `pruebas\`, `tools/e2e/shot.ps1` y `click.ps1` por pid, errores de QML con
  `-RedirectStandardError`; copia del registro antes y restaurarla después.

---

## Estado (actualizado 2026-10-23, noche)

### 0.22 SIN PUBLICAR: primero el texto completo (2026-10-24) — **estado y orden en `docs/plan-0.22.md`**
- Jorge: la 0.22 no va a la Store hasta tener los arreglos de `docs/auditoria-texto.md`, las funciones básicas y
  avanzadas de texto, el tamaño con decimales, el editor visual de animaciones y todo igual en la web.
- Ramas: `flip/v0.22.1` (worktree `.claude/worktrees/v0221`), `flip/subs-vtt-ass`, `flip/anim-editor`; web
  `web/v0221-texto` (sin desplegar). La copia de prueba tiene la sesión de Google de Jorge: al terminar, restaurar el
  registro **conservando** la clave `account`.

### 0.21.0 PUBLICADA (2026-10-23) — Efectos › Tendencias — **detalle y trampas en `docs/plan-efectos-tendencias.md`**
- PR #37 (`flip/efectos-tendencias` → `main`), tag `v0.21.0`, release (run 40052598335); copia en
  `versiones\FlipStudio-0.21.0` (hashes comprobados); novedades en la web. MSIX: `msstore.yml` run 40057246669 →
  `tienda\FlipStudio-Store\paquete-0.21.0`. Notas de la Store: «Notas para la Store (0.21.0)».
- 364 efectos GPU propios + 9 voces (`tools/effects_trends`), en Efectos › Tendencias y Stock (tipo `effect`).
  Servidor `flipstudio-api` rama `stock-efectos` y contenido (`publicar\efectos` + `i18n`) **desplegados**.
- **Lo que pide cuenta será premium más adelante (Jorge):** Títulos/Efectos › Tendencias se ven con sesión; las
  animaciones de tendencia se ven con una **llamita naranja** y al elegirlas sin sesión piden la cuenta
  (`SignInRequiredDialog` `reason: "trends"`; web `useTrendsGate`).
- **Trampa:** el servidor oculta a una app vieja lo que tiene `minAppVersion` mayor (cabecera `X-Cutwire-App`) en
  Todo, inicio y novedades: así la 0.20 no ve los efectos `.driftfx` que no sabe instalar.
- **Trampa:** `tools/e2e/shot.ps1` y `click.ps1` llevan `-TargetPid` (obligatorio). Con un nombre equivocado
  (`-ProcessId`) lo ignoraban y actuaban sobre la ventana del frente: una vez hicieron clic en otra app de Jorge.
- **Jorge mandó la 0.21.0 a certificación (2026-10-24)**; la 0.20.1 ya estaba aprobada. Falta: cuando la aprueben,
  TXT `version` = 0.21.0.
- **Siguiente (rama `flip/v0.21.1`):** medios ocultos de la web también ocultos en Medios (`webHidden`); build de CI
  run 40062431397, **falta probarlo en ventana** con un `.flip` de la web que tenga un recorte de persona.

### Editor web en el celular como CapCut, etapa 7 (2026-10-23, desplegado, `flipstudio-app` `web/movil-capcut`)
- Capturas de Jorge en `Downloads\capcut movil\1…24.png`; detalle en `docs/plan-movil.md` › Etapa 7. Barras en el
  orden de CapCut, paneles de una fila (`TouchPanels.tsx`), Recortar a pantalla completa (`TouchCrop.tsx`),
  Sustituir, Superposición ⇄ Pista principal, Ritmos, Subtítulos y Seguimiento. Simulación:
  `scripts/check-phone-bar.mjs` y `check-phone-actions.mjs` (con `FLIP_BASE=` contra la web publicada).
- **Trampa:** en `flipstudio-app` los tipos se revisan con `npx tsc -b`; `tsc -p .` no revisa nada.


### 0.20.1 PUBLICADA (2026-10-22, noche) — la galería de Texto › Animación vacía en la 0.20.0
- La 0.20.0 la **aprobó la Store** con Texto › Animación mostrando solo «Ninguno» (`TextAnimPresetTile` era un
  `Column` y la estrella de favorito anclada lo apagaba). PR #35, tag `v0.20.1`, release (run 39852585099), copia en
  `versiones\FlipStudio-0.20.1` (hashes comprobados), novedades en la web. Además: pestañas subrayadas y chips
  desplazables (`AnimSlotTabs`, `ChipScroller`), textos de muestra que caben. Probada en ventana (capturas).
- **MSIX: `msstore.yml` run 39857949348** — si la máquina se apagó antes de bajarlo:
  `gh run download 39857949348 -R bajoelabrigo/Flip` a `tienda\FlipStudio-Store\paquete-0.20.1`.
- **Aprobada en la Store (Jorge, 2026-10-24).** Su lugar lo toma la 0.21.0
  (no 0.20.0).
- **Web (`flipstudio-app` `web/animaciones`, desplegada):** unida con `web/v019` (se había perdido al desplegar),
  galería de los textos con estilo del escritorio (`DeskAnimPage`), «Recuperar archivos» arreglado, en el celular
  «Animaciones» de un texto abre las de letras.

### 0.20.0 PUBLICADA (2026-10-22) — animaciones como Filmora — **detalle y trampas en `docs/plan-animaciones.md`**
- PR #32 (`flip/animaciones` → `main`), tag `v0.20.0`, release (run 39819994016) con instalador, portable y `SHA256SUMS`; copia en `versiones\FlipStudio-0.20.0` (hashes comprobados); MSIX: run 39826305469; novedades en la web. Texto: giro 3D, cursor de glifo, partículas y **302**
  animaciones nuevas (216 Entrada, 86 Salida) en chips como Filmora (`tools/text_animations`). Clip: Video ›
  Animación con **49 Entrada, 55 Salida y 62 Combinado** (`tools/clip_animations/build.py`). Nombres en 12 idiomas.
- Revisadas en hojas renderizadas con la app (`pruebas\animaciones-texto`, `pruebas\animaciones-clip`) y el panel
  probado en ventana. Editor web igual (`flipstudio-app` `web/animaciones`, desplegado). Notas de la Store en
  `docs/store-listing.md` («Notas para la Store (0.20.0)»).
- **Barra de abajo del celular (iPhone instalado):** era `black-translucent`; con `black` queda abajo. Jorge lo
  confirmó tras borrar y volver a agregar el ícono.
- **Falta (Jorge):** cuando aprueben la 0.19.0, mandar la 0.20.0 (MSIX en `tienda\FlipStudio-Store\paquete-0.20.0`)
  y después TXT `version` = 0.20.0.

### 0.19.0 PUBLICADA (2026-10-22) — seguimiento como CapCut, Tendencias, textos 100 % editables — **detalle en `docs/plan-0.19.md`**
- PR #29 (`flip/v0.19.0` → `main`), tag `v0.19.0`, release (run 39723353011) con instalador, portable y `SHA256SUMS`;
  copia en `versiones\FlipStudio-0.19.0` (hashes comprobados). MSIX: `msstore.yml` run 39730527975 →
  `tienda\FlipStudio-Store\paquete-0.19.0`. Novedades en la web (`flipstudio-web` `49b3d`, desplegado). Extra
  `seguimiento.objetos` 1.0.0 publicado (paquete y después índice). Notas de la Store en `docs/store-listing.md`
  («Notas para la Store (0.19.0)»).
- **Jorge (2026-10-22):** la 0.18.3 ya fue aprobada y **mandó la 0.19.0 a certificación**. Falta: cuando la
  aprueben, TXT `version` = 0.19.0.
- **Trampa:** `lupdate` va con `-disable-heuristic sametext -disable-heuristic similartext` (también en `LUPDATE_OPTIONS`
  de CMake): las heurísticas dejaban traducciones adivinadas sin terminar (es_CO mostraba 148 textos mal).

### Editor web en el celular, etapa 6: herramientas como CapCut (2026-10-22, desplegado, `flipstudio-app` `web/v019` `e4ac1`)
- ◇+ / ◇− de fotogramas clave (el rombo del cabezal en rojo), Curvas (17 + propia), Máscara en una fila con anclaje y
  difuminado en la vista previa, Transformar (Reflejar, Girar, Avanzadas con reglas), Animaciones con tarjetas,
  Recortar propio, Audio › Del teléfono. Detalle, arreglos de la simulación y trampas en `docs/plan-movil.md` › Etapa 6.
- Simulación de un celular: `node scripts/check-phone.mjs <carpeta> <puerto> <pasos>` (con `FLIP_BASE=…` contra la web).
- Las curvas son solo de la web por ahora: en el escritorio llegan como asas Bézier (se ven igual, no hay galería).

### 0.18.3 PUBLICADA (2026-10-20) — actualizar sin vueltas, espacio en vivo al mover clips, idiomas, icono de macOS
- PR #28 (`flip/macos` → `main`), tag `v0.18.3`, release (run 39474015359) con instalador, portable y `SHA256SUMS`;
  copia en `versiones\FlipStudio-0.18.3` (hashes comprobados). MSIX: `msstore.yml` run 39481238504 →
  `tienda\FlipStudio-Store\paquete-0.18.3`. Novedades en la web. Notas de la Store en `docs/store-listing.md`
  («Notas para la Store (0.18.3)», 358/1500).
- **Aprobada en la Store (Jorge, 2026-10-22).**
- **Trampa:** Partner Center da «Tienes que corregir todos los errores de validación del paquete» si se sube el
  instalador `.exe` de `versiones\`: la Store solo acepta el `.msix` de `tienda\FlipStudio-Store\paquete-<versión>\`.
- Probado en ventana: el espacio que se abre en vivo al arrastrar (`moveRoomPreview`). «Actualizar» con una
  actualización real se prueba con la versión siguiente (el cambio vive en la 0.18.3).
- **Trampa:** el `.icns` hecho con Pillow no trae `icp4` (16 px) e `iconutil` falla en la prueba de macOS: escribirlo
  a mano con todos los tipos (icp4…ic14) en PNG.
- macOS: el `.dmg` sigue sin probar en un Mac (y sin firma de Apple hasta el anuncio).

### Editor web en celulares y tabletas, como CapCut (2026-10-21, etapa 1 desplegada)
- Pedido de Jorge tras probarlo en su iPad. Plan, estado y trampas en `docs/plan-movil.md` (rama `web/movil` de
  `flipstudio-app`). Diseño táctil = mismo `Editor` con `TouchTimeline` + barra de abajo + hoja con los paneles.
- **Trampa:** en iOS un `:hover` que muestra algo (estrella, «+») se come el primer toque: lo que sale al pasar el
  mouse va siempre visible bajo `@media (hover: none)`.

### Página de inicio con videos (2026-10-21, desplegada, `flipstudio-web` `4a84b`)
- Recorrido: «Plantillas de Stock» = plantilla vertical «Nueva colección» con las dos modelos de traje; «IA en tu
  PC» = antes/después del retoque + parapente de 120 fps a velocidad real y en cámara lenta. Fondos con video detrás
  de «El mismo editor…» (robots), «Herramientas de editor profesional…» (fotógrafa) y «Empieza a editar hoy» (aviones).
- Todo renderizado con la app sin ventana; scripts y fuentes en `pruebas\web-videos` (`plantilla.py` rellena el
  `project.json` del paquete y lo carga con `load_project`; `retoque.py`, `lenta.py`, `enc.sh` para la web).

### Editor web, tarde del 2026-10-20: IA en el navegador y barra derecha igual al escritorio (desplegado)
- Detalle, modelos del VPS y lo que falta en `docs/paridad-web.md` › «Tarde del 2026-10-20». Rama `web/paridad-1`
  `b23bf` (unió `web/ia-rostro`, `ia-cuerpo`, `ia-rife`, `ia-sam`, `ia-mejorar` y `pistas-inspector`).
- **Trampa:** ORT Web con WebGPU calcula mal la capa de 15 canales de RIFE: usar `rife_v4.25_web.onnx`.

### 0.18.2 PUBLICADA (2026-10-19) — actualizar funciona otra vez, rellenar pantalla, «+» en Medios, logo nuevo
- PR #27 → `main`, tag `v0.18.2`, release con instalador, portable y `SHA256SUMS`; copia en
  `versiones\FlipStudio-0.18.2` (hashes comprobados). MSIX (run 39321601743) en
  `tienda\FlipStudio-Store\paquete-0.18.2\FlipStudio-0.18.2.0-x64.msix`. Novedades en la web. Logos de la Store en
  `tienda\FlipStudio-Store\logo-nuevo-2026-10-19`.
- **Jorge (2026-10-20):** la 0.18.2 ya está en la Store y en el TXT `version`; probó el arrastre «tipo tetris», el
  hover, mover con cerrar huecos y quitar imperfecciones, y escuchó la música de `por-escuchar`. Todo eso, cerrado.
- **macOS** en la rama `flip/macos` (sin firma de Apple hasta el anuncio; luego Apple Developer $99). **Primer
  `.dmg` compilado (run 39325198092, arm64)** en `pruebas\mac-0.18.2` (se llama `0.0.0-<commit>` porque no salió de un
  tag); falta probarlo en un Mac. El icono de macOS (`resources/macos/Drift.icon`) sigue con el logo viejo.
- Editor web (rama `web/paridad-1` de `flipstudio-app`, desplegado): seguir `docs/paridad-web.md`.
- **Editor web, tanda del 2026-10-19 (todo desplegado, rama `web/paridad-1`):** plantillas de efectos (siguen la
  música, Intensidad/Caída/Ritmo), «Ajustar los cortes al ritmo», 31 efectos de audio, Escenas, favoritos en la
  cuenta, contadores, antes y después, **todos los tipos de Stock** (looks, transiciones `.driftfx`, formas, estilos
  y animaciones de texto), exportar Video/Audio/GIF, varias pistas, normalizar −14 LUFS, quitar silencios, curvas de
  velocidad, y el `.flip` llevando efectos, transiciones, audio, contadores y plantillas en los dos sentidos (probado
  con la 0.18.2). Qué falta, en `docs/paridad-web.md`.
- **Jorge mandó la 0.18.2 a certificación (2026-10-19).**
- **Editor web, noche del 2026-10-20 (desplegado, rama `web/paridad-1`):** todo lo que no necesita IA (los efectos y
  transiciones del escritorio, cámara, curvas, guías, proxies, estabilizar, multicámara, plantillas propias, menú y
  atajos completos, tema claro, Ajustes) y **los 16 idiomas** (`src/i18n`, `t()`/`N_()`, extractor
  `scripts/i18n-extract.mjs`). Detalle y diferencias en `docs/paridad-web.md` › «Noche del 2026-10-20».
- **Próxima versión del escritorio (en la rama `flip/macos`, sin compilar todavía):**
  - Actualizar sin vueltas (pedido de Jorge, 2026-10-19): al terminar la descarga se abre solo «Actualización
    lista» con «Reiniciar e instalar», aunque esté marcada la casilla de instalar al cerrar
    (`UpdateChecker::finishStage` emite siempre `installReady`). Antes, con la casilla (marcada por defecto), no
    avisaba y había que volver al botón de arriba. **Probarlo en ventana** con una actualización real.
  - Las transiciones de Stock muestran en inglés 22 nombres de parámetros («Cells», «Tiles», «Folds»…): faltan en
    `drift_es.ts`. La web ya los traduce (`flipstudio-app/src/transitions/stockParamLabels.ts`): copiar de ahí.
  - Lo de «Reiniciar» que volvía al inicio ya está arreglado en la 0.18.2 (`window.quitApp()`), pero solo funciona
    **desde** la 0.18.2: quien actualiza desde 0.17–0.18.1 corre el código viejo. Para esos: cerrar con la X de la
    pantalla de inicio (o Archivo › Salir) y el instalador arranca solo.

### 0.18.1 PUBLICADA (2026-10-19) — arreglos del control de calidad de la 0.18 — **detalle en `docs/plan-0.18.1.md`**
- Control de calidad por MCP sin ventana (`tools/e2e/qa018/`, se corre en `pruebas\qa018`): 15 formatos, los 78 efectos
  y 40 transiciones, cada códec, texto, audio, subtítulos e IA. Arreglos: **Pintura al óleo** (shader con `flat`,
  palabra reservada de GLSL: no compilaba desde Drift), **DNxHR** (perfil `dnxhr_hq`/`dnxhr_hqx`), **Texto › Efectos**
  traducido (67 textos × 12 idiomas) y con «°» bien, y MCP `freeze_frame`/`import_media`.
- PR #26 → `main`, tag `v0.18.1`, release (run 39195704624); copia en `versiones\FlipStudio-0.18.1` (hashes
  comprobados); novedades en la web. MSIX: `msstore.yml` run 39199587252 → `tienda\FlipStudio-Store\paquete-0.18.1`.
- **IMPORTANTE — NO SUBIR la 0.18.1 (Jorge, 2026-10-19):** ni MSIX a Partner Center ni TXT `version` = 0.18.1. El
  botón «Actualizar a …» no actualiza desde la 0.17: `Main.qml` respondía a `Updates.quitRequested` con
  `window.close()`, que desde la 0.17 es la X del editor y vuelve al inicio. **Arreglado en la rama `flip/v0.18.2`**
  (`window.quitApp()`, sin compilar). Va en la próxima versión, junto con el editor web. Quien actualice desde
  0.17–0.18.1 tiene que cerrar con la X en la pantalla de inicio (o Archivo › Salir) para que arranque el instalador.
  Detalle en `docs/plan-0.18.1.md` › «Después de publicar».
- **Siguiente (2026-10-19), en la rama `flip/v0.18.2`:** el arreglo de actualizar (ya hecho) + editor web igual al
  escritorio, plan en `docs/paridad-web.md` (empieza por tema, menú, `.flip`, cuenta y Stock).
- **Trampas nuevas:**
  - `QLatin1String` sobre un `const char*` con «°» (UTF-8) da «Â°»: usar `QString::fromUtf8`.
  - `lupdate` no extrae un texto que va dentro de una función llamada `tr(...)` que no es la de Qt, ni uno que llega
    en una variable: marcarlo con `QT_TRANSLATE_NOOP("Contexto", "...")` en el contexto que usa `translate()`.
  - Exportar recuerda los últimos ajustes (códec, audio, escala) entre sesiones, también por MCP: pasar `video`,
    `audio` y `scale` explícitos en las pruebas (FLAC en `.webm`/`.mov` da «Could not write the file header»).
  - Un efecto cuyo shader no compila se salta **sin avisar**: para encontrarlos, comparar píxeles con y sin el efecto
    (`qa_render.py`).

### 2026-10-19: paridad del editor web, etapa 1 (rama `web/paridad-1` de `flipstudio-app`)
Pedido de Jorge: que el editor web quede lo más parecido posible al escritorio; plan en `docs/paridad-web.md`
(y ese archivo dice qué falta por etapa). **Etapa 1 hecha y desplegada** en `getflipstudio.com/editor/`:
- **Tema turquesa por defecto**, con los siete colores del escritorio (antes la web tenía seis y el ámbar fijo), y
  la banda de «Crear proyecto» toma los colores del tema.
- **Menú arriba** (`components/MenuBar.tsx`): Archivo, Editar, Herramientas, Ver, Avanzado y Ayuda, con los atajos
  del escritorio a la derecha; Ver lleva el color de la interfaz y Ayuda abre **Atajos de teclado**.
- **Fila de categorías** sobre el panel de recursos (Medios, Títulos, Audio, Stickers, Efectos, Transiciones), con
  la última pestaña recordada por categoría.
- **`.flip`:** abre `.flip` y `.drift` (documento + tabla de medios + blobs incrustados, que se guardan con el
  proyecto en `SavedMedia.blob`) y guarda `.flip`.
- **Trampa gorda, arreglada:** abrir un proyecto **nunca funcionó** en la web. `sha256` hacía `instanceof
  SharedArrayBuffer` sin comprobar que exista (en una página sin aislamiento entre orígenes lanza `ReferenceError`),
  y el lector de zstd usaba una API que `zstd-codec` no tiene (`ZstdCodec.run`), con un `.d.ts` inventado. Además su
  wasm necesita `SharedArrayBuffer`, así que se pasó a **`fzstd`** (zstd en JavaScript puro; la web solo descomprime).
  Los blobs con `codec: "zstd"` se descomprimen y su digest se comprueba después, como en `ProjectBundle.cpp`.
- Comprobado en el navegador (Playwright) con `Downloads\prueba.flip`, y `tsc`, `vite build`, 99 pruebas y `oxlint`
  igual que antes (30 avisos y el error viejo). Falta de la etapa 1: categorías Stock/Filtros/Plantillas (cuando
  existan en la web), la rueda entre categorías y traducir la web.

### 0.18.0 PUBLICADA (2026-10-18) — cámara lenta suave con IA, fotos variadas, contadores — **detalle en `docs/plan-0.18.md`**
- PR #25 → `main`, tag `v0.18.0`, release (run 39178642565) con instalador, portable y `SHA256SUMS`; copia en
  `versiones\FlipStudio-0.18.0` (hashes comprobados). MSIX (run 39178670318) en
  `tienda\FlipStudio-Store\paquete-0.18.0\FlipStudio-0.18.0.0-x64.msix`. Novedades en la web. Stock: los 15 contadores
  nuevos subidos (delta de 35 MB, comprobado byte a byte). Editor web: pestaña Voz (Kokoro + eSpeak NG) desplegada.
- **Falta (Jorge):** TXT `version` = 0.18.0, subir el MSIX con las notas **combinadas 0.17 + 0.18** de `docs/store-listing.md` (la 0.17 no se subió) y probar
  el arrastre «tipo tetris» (el arrastre simulado no mueve clips).
- **Trampas nuevas:** el contador de la 0.17 no contaba en vista previa ni exportación (se dibuja por
  `FrameCompositor::fillTextLayer`, no por `makeTextPainter(clip, …)`); y `apply_delta.sh` se corta en su resumen final
  (`python3` del heredoc) y deja `flipstudio-templates.old`: borrarla a mano después de comprobar.
- Contadores de Stock con el contador del motor (`counterSeconds`), fotos variadas en las miniaturas de Efectos,
  Plantillas de efectos, Transiciones y LUTs, antes y después en Efectos, cámara lenta suave con RIFE, foto de
  «Imperfecciones» y voz con IA del editor web.

### 0.17.0 PUBLICADA (2026-10-18) — IA en tu computadora, inicio como Filmora, CapCut — **detalle en `docs/plan-0.17.md`**
- Transición con IA (RIFE, extra `transiciones.ia`), texto con IA (MiniLM, extra `texto.ia`), quitar imperfecciones
  (`effects/face_blemish`), marca «IA» con «?», tema turquesa predeterminado e inicio como Filmora, la X vuelve al
  inicio, fila de categorías completa, hover en plantillas/Stock y antes/después de los LUT, contadores animados,
  congelar y mover con cerrar huecos como CapCut, traducciones de 11 idiomas. Notas en `release-notes/0.17.0.md` y
  `docs/store-listing.md`. Probado en ventana (lista en el plan); el hover y mover con cerrar huecos los prueba Jorge.
- Extras subidos primero al release `packages` y después el índice a la web, con las novedades.
- **Publicada:** PR #24 → `main`, tag `v0.17.0`, release (run 39144814597) con instalador, portable y `SHA256SUMS`;
  copia en `versiones\FlipStudio-0.17.0` (hashes comprobados). MSIX (run 39144852574) en
  `tienda\FlipStudio-Store\paquete-0.17.0\FlipStudio-0.17.0.0-x64.msix`.
- **Falta (Jorge):** TXT `version` = 0.17.0, subir el MSIX con las notas de `docs/store-listing.md`, escuchar las pistas
  de `tienda\musica\por-escuchar` y probar el hover, mover con cerrar huecos y quitar imperfecciones.
- **Trampa nueva:** `mcp_e2e.py --attach` se conecta al editor que tenga el puente MCP abierto, que puede ser el de
  Jorge. Con dos editores abiertos, solo clics y capturas por pid.
- Ese archivo dice qué está hecho, qué falta, dónde va cada cosa y cómo seguir, para continuar con cualquier
  asistente (Jorge, 2026-10-18: «anota todo por si se me acaba la suscripción»). **Siempre así:** cada versión
  lleva su `docs/plan-<versión>.md` al día y el trabajo a medias se sube a la rama a menudo.

Las versiones 0.16.0 y 0.15.0 (menú como Filmora/CapCut y Stock para creadores) están contadas enteras en
`docs/historia.md`, con sus trampas; lo de arriba es lo vigente.

### 0.14.0 PUBLICADA (2026-10-17) — Stock completo: tienda, tipos nuevos y uso más rápido
- Rama `flip/v0.14.0` → **PR #20** → `main`; **tag `v0.14.0`**. Notas en `release-notes/0.14.0.md`, CHANGELOG (con
  0.12.0 y 0.13.0 recuperados) y notas de la Store en `docs/store-listing.md` (1.069/1.500 caracteres, es y en).
- **Release `v0.14.0` publicado (2026-10-17 01:38 UTC, run 38986650585)**: instalador, portable y `SHA256SUMS`;
  copia en `versiones\FlipStudio-0.14.0`. **MSIX** en
  `tienda\FlipStudio-Store\paquete-0.14.0\FlipStudio-0.14.0.0-x64.msix` (run 38986680013). Novedades de la web
  desplegadas (`flipstudio-web` commit `2a296`).
- **Jorge (2026-10-16):** TXT `version` = 0.14.0 (comprobado en DNS) y MSIX subido a Partner Center con las notas de
  la Store. Falta que la certifiquen.
- **Probado antes de publicar:** dos ensayos de `build.yml` en verde (runs 38975643991 y 38982166721: compilación +
  16 suites + instalador y portable); la pantalla de inicio de Stock en ventana con estantes, la insignia de
  novedades («99+») y «Pide una plantilla»; y de punta a punta por MCP contra el editor abierto con un elemento de
  cada tipo nuevo (LUT → Ajustar › LUT, look → Mis efectos, estilo y texto animado → Texto, transición →
  Transiciones, forma → Formas, música → Medios, plantilla → Plantillas). Lista en
  `tools/e2e/calls_stock014.jsonl`.
- **Arreglo posterior (PR #21):** el mensaje al instalar un look decía «Mis ajustes predeterminados»; en español
  ahora dice **Mis efectos**, que es el panel real. También entraron `tools/e2e/shot.ps1` y `click.ps1` (capturan y
  clican la ventana por mensajes, sin tocar el mouse).
- **Trampa nueva:** **`--headless` no tiene sesión de cuenta.** `AccountController` carga la sesión guardada en el
  editor con ventana, así que con `--headless` toda llamada `market_*` responde `authenticated:false` y el servidor
  contesta 401. Las pruebas de Stock van con `mcp_e2e.py --window` o `--attach <pid>` a un editor abierto, con
  `mcp/startOnLaunch = true` (y la cuenta rotada se exporta **después** de la prueba, como avisa la trampa de abajo).

### Stock ampliado y DESPLEGADO (2026-10-16/17), contenido y servidor
Lo de Stock que **no necesitaba versión nueva quedó desplegado** antes de la 0.14.0:
- **Contenido en `api.getflipstudio.com/plantillas/`** (4,87 GB, subido con `deploy/plantillas.ps1`, que cambia la
  carpeta entera): **883 plantillas** (533 + **350 de formatos nuevos**: publicaciones 1:1, historias de 15 s,
  anuncios de 6 s, miniaturas de YouTube), **328 cortes de música** (ánimos, 15/30/60 s; 9 pistas FMA en espera de
  oírlas), **200 LUTs**, **209 looks**, **200 estilos de texto**, **200 textos animados**, **200 transiciones**,
  **200 formas**, más lo que ya estaba: 222 stickers, 400 superposiciones (vertical + horizontal), 200 sonidos y
  400 fondos (vertical + horizontal).
- **i18n: segunda pasada completa.** Los 13 idiomas (`tools/stock_i18n/<lang>.json`) cubren **3.642 elementos y 145
  categorías** (`build.py --strict` sin faltantes) y `publicar/i18n/` ya está en el VPS (8,1 MB). Para traducir se
  usaron agentes en paralelo: `collect.py --size 300` → una tanda por agente (`work/todo/<lang>-NN.json` →
  `work/done/<lang>-NN.json`, 91 tandas) → `merge.py` → `check.py` → `build.py --strict`. `work/verify.py` comprueba
  que cada tanda tenga las mismas claves y 3–6 etiquetas.
- **Servidor `flipstudio-api` rama `stock-0.14` DESPLEGADO** (PM2 `flipstudio-api`, health `{"ok":true}`): tipos
  nuevos con su `delivery` (`lut`, `effect-preset`, `text-style`, `text-animation`, `transition`, `shape`),
  `GET /v1/market/search?type=all` con sinónimos, `GET /v1/market/home` (estantes, `services/seasons.ts`,
  `colecciones.json`), `GET /v1/market/news`, `GET|POST /v1/market/requests` con votos y `GET|PUT /v1/me/favorites`.
  Comprobado en vivo: `/v1/market/news` responde 3.642 elementos; `home` y `requests` piden cuenta (401 sin sesión).
- **App (rama `flip/v0.14.0`, unión de `flip/stock-superposiciones` + `stock-plantillas-formatos` +
  `stock-looks-transiciones` + `v0.14.0-stock` + `v0.14.0-plantillas`):** instalación de los tipos nuevos
  (`AppController::installStockFile`), inicio tipo tienda (`StockHome.qml`), tarjetas con la forma de cada elemento
  y **tarjetas anchas** (`StockThumb.qml` usa `thumb_wide_url`/`preview_wide_url`, que el servidor sirve desde
  `thumbWide`/`previewWide`), vista previa de audio al pasar el mouse, contador de usos, novedades, favoritos en la
  cuenta, «Pide una plantilla», «Usar con mis fotos», «Cambiar plantilla», cortes al ritmo, formulario de textos y
  «Mi marca». Versión 0.14.0 en `CMakeLists.txt`, notas en `release-notes/0.14.0.md`, CHANGELOG (con 0.12.0 y
  0.13.0 recuperados) y notas de la Store en `docs/store-listing.md` (1.069/1.500 caracteres).
- **Trampas de esta tanda:**
  - `tools/luts_stock/publish.py` no existía: se escribió (índice como el de sonidos + `delivery: "lut"`).
  - Las **tarjetas de los looks** se renderizan con la app (`tools/looks_stock/build.py` + `appsession.py`, portable
    de `pruebas\FlipStudio-0.13.0-arreglo`): los `.json` y `meta.json` se habían construido, los `thumbnail.png` no.
  - `tools/scene_templates/publish.py` (rama de formatos) **no conservaba** `colecciones.json` ni el `addedAt` de
    cada plantilla: se portó de `flip/v0.14.0-stock` al unir. El índice desplegado de la 0.13.0 no tenía `addedAt`
    (el campo llega con la 0.14.0), así que las 883 quedan con fecha de hoy.
  - Al unir las dos ramas de app, los conflictos fueron **aditivos**: `MarketClient.h` (home/novedades/pedidos/
    favoritos + sugerencias de plantilla) y `SceneTemplates.cpp` (`QPointer` + `QSet`). Se conservan los dos lados.
  - **El fallo del CI de `flip/v0.14.0-stock` era real y ya estaba arreglado en la punta de la rama** (run
    38967194866 probó `d6c24fa`, antes de `3334f`): `McpTest::setMaskRoundTripsFreeformPoints` fallaba porque el
    esquema de `set_mask` aún no conocía `pathData`/`pathEvenOdd` y el validador los marcaba como `ignored`.
### Plan de Stock (Jorge, 2026-10-16)
- Stock es **pieza central** de la app. El plan completo, acordado con Jorge, está en `docs/plan-stock.md`:
  contenido nuevo (textos animados, overlays, marcos, fondos, sonidos, música, LUTs, stickers, tercios inferiores,
  fechas y negocios, formatos 16:9/1:1), inicio de Stock tipo tienda, búsqueda y filtros, uso más rápido y novedades
  semanales. **Para el mundo entero:** nada de fiestas solo peruanas o latinas. Pagos, al final.
- Orden de Jorge (2026-10-16): primero todo lo de Stock que no necesita versión nueva (servidor y contenido); al
  final la 0.14.0 con todo lo que sí, y al terminar: **compilar una vez, probar en ventana y publicar todo**.

### 0.13.0 PUBLICADA (2026-10-16): Retoque › Cuerpo y Cabello, plantillas propias, 101 plantillas, Stock › Animaciones
- Rama `flip/plantillas-propias` → PR a `main`, tag `v0.13.0`. Notas en `release-notes/0.13.0.md`; novedades para la
  Store (0.12.0 + 0.13.0, 1014 caracteres) en `docs/store-listing.md`: la 0.12.0 no llegó a subirse (Jorge: «subimos
  la versión 13 de una vez»). Extra `cuerpo.cabello` 1.0.0 publicado (paquete primero, índice después).
- Probado en ventana con Jorge («funciona todo bien, me gusta»). Arreglo de última hora (PR #19): las tarjetas de
  Retoque se aplican en C++ (`applyRetouchLook`); antes `addEffect` movía la selección, el panel de Video se
  descargaba a mitad del clic y los valores no llegaban. El tag `v0.13.0` se movió a `f6481` (el primero, `7c81c`,
  nunca llegó a release: falló la prueba de estabilizar por el aviso de OpenGL 3.0 del runner, ya tolerada).
- **Publicada (2026-10-16):** release `v0.13.0` (run 38864046035), copia en `versiones\FlipStudio-0.13.0`, MSIX en
  `tienda\FlipStudio-Store\paquete-0.13.0\FlipStudio-0.13.0.0-x64.msix` (run 38864080404; el de
  `descartado-no-subir` es del tag viejo), extra `cuerpo.cabello` en el índice y novedades en la web.
  **Jorge subió el MSIX a Partner Center (2026-10-16)**, con las notas «0.12.0 + 0.13.0». Falta que la certifiquen.

### 0.11.0 PUBLICADA (2026-10-15): plantillas editables, plantillas como composición, fotogramas en la pista
- Rama `flip/plantillas-editables` → PR a `main`, tag `v0.11.0`. Notas en `release-notes/0.11.0.md`; novedades para
  la Store (0.10.0 + 0.11.0, 996 caracteres) en `docs/store-listing.md`. **Esta sí va a la Store y al TXT `version`.**
- Release en GitHub, copia en `versiones\FlipStudio-0.11.0`, novedades en la web. **TXT `version` = 0.11.0** (Jorge,
  comprobado en DNS el 2026-10-15). MSIX listo en `tienda\FlipStudio-Store\paquete-0.11.0\FlipStudio-0.11.0.0-x64.msix`
  (run 38702261969). **Aprobada en la Store (Jorge, 2026-10-16).**
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
.\.qtmingw\6.10.3\mingw_64\bin\lupdate.exe src i18n -no-obsolete -locations none -disable-heuristic sametext -disable-heuristic similartext -ts (gci i18n\drift*.ts).FullName

# 3. Comprobar que quedó estable (dos pasadas iguales) y ver qué traduce de verdad
.\.qtmingw\6.10.3\mingw_64\bin\lrelease.exe i18n\drift_es.ts -qm .qmcheck\drift_es.qm
.\.qtmingw\6.10.3\mingw_64\bin\lconvert.exe -i .qmcheck\drift_es.qm -o .qmcheck\dump.ts
```

**Trampa (2026-10-21): las «adivinanzas» de lupdate pisaban el español en Colombia.** Para un texto
nuevo, lupdate copiaba la traducción de otro texto parecido y la dejaba «sin terminar»; lrelease la
incluye igual, y como el catálogo regional `drift_es_CO` va encima de `drift_es` (el idioma de Jorge es
`es_CO`), salían cosas como «Desenfoque» en vez de «Desenfocar». Se vaciaron las 148 de `es_CO` y
lupdate corre con `-disable-heuristic sametext -disable-heuristic similartext` (también en CMake).

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
- **Máscara**: el texto como forma de máscara ya existía (`MaskShape::Text`); las máscaras **sobre** un clip de
  texto llegan en la 0.19.0 (`docs/plan-0.19.md`).
- **Retoque**: falta **quitar imperfecciones** (manchas y arrugas).
- De nube de CapCut y no replicable: quitar objetos con IA, ampliar a 4K con IA, remix,
  contacto visual, sincronización labial.
- Ideas sin modelo todavía: separar audio (voz/música) y traductor de video.

---

## Historia (movida a `docs/historia.md`)

Lo cerrado de las 0.9.x, el plan de cuentas/instalaciones/Pexels del 2026-10-13 y la investigación del panel
en inglés están en `docs/historia.md`; aquí quedan solo el estado, las trampas vigentes y la rutina.

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

**Python en Windows escribe CRLF.** `open(p, "w")` traduce `\n` a `\r\n`: un script que reescribe un `.qml` o `.py`
lo deja entero como cambiado. Usar `newline=""` (o `sed -i`), y pedirlo a los agentes. (Este `CLAUDE.md`, en cambio,
está en CRLF en la copia de trabajo: respetar el fin de línea del archivo.)

**Varias tandas de plantillas en paralelo:** el render usa una sola app y el registro compartido; `build.py` toma
`renderlock.exclusive()` (un candado entre procesos) y `fetch_samples.py --themes <json>` baja fotos por tanda con el
mismo candado. Registrar los módulos de cada tanda antes de lanzar a los agentes (si no, todos editan
`templates.py`), y no tocar `kit.py` mientras rendericen.

**El aviso de actualización espera 24 h y no reintenta.** `UpdateChecker::scheduleStartup()` mira
`updates/lastCheck`: si la última comprobación fue hace menos de un día **no pregunta** (solo vuelve a anunciar lo
que ya sabía), y `lastCheck` se guarda aunque el TXT todavía devolviera la versión vieja por la caché de DNS. Síntoma:
Jorge cambia el TXT `version` a la versión nueva, abre la app y no le sale nada; y así seguirá hasta el día siguiente.
Lo que funciona: **Ajustes › Actualizaciones › «Buscar ahora»** (`Updates.checkNow()`, que se salta la espera). Si
acaba de cambiar el TXT, antes `ipconfig /flushdns` (Windows cachea el TXT con su TTL). El aviso de la barra admite
una comprobación manual y, si falla, deja el motivo en `Updates.status`.

**Fotos de Pexels con marcas:** casi todas las de gimnasio, deporte y aparatos traen logos (Nike, Puma, Under Armour,
Apple, Samsung…). Revisarlas a tamaño completo, no en la hoja de contacto.

**Colores de 8 dígitos en QML son `#AARRGGBB`, no `#RRGGBBAA`.** `Theme.scrimColor`, `scrimStrong` y `waveformColor` venían de Drift al revés (transparentes o amarillos); corregidos en la 0.12.0 (`a8d9d`). Al escribir un color con alfa, el alfa va primero.

**Restaurar el registro tras una prueba puede cerrar la sesión de Google de Jorge.** El servidor rota el token de
refresco en cada uso y, si llega uno ya usado, cierra toda la familia (2026-10-14 22:34 UTC pasó). Si la app de
prueba usó la cuenta (Stock, Mi cuenta), exportar `HKCU\Software\Flip Studio\Flip Studio\account` **después** de la
prueba, restaurar la copia y volver a importar esa clave. Comprobar en Mongo (`sessions`, `revokedAt`) si hay dudas.

**`reg export … /y` desde el Bash (Git Bash) falla** con «sintaxis incorrecta»: msys convierte `/y` en una ruta y no
queda copia. Hacer la copia del registro **desde PowerShell** y comprobar que el archivo existe antes de lanzar la app.
Y `flipstudio.exe --headless --mcp-stdio <proyecto>` arranca con la línea de tiempo vacía: abrir el proyecto con la
llamada `load_project`.

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

**Antes de desplegar el editor web, la rama tiene que llevar lo último publicado.** `deploy/deploy.sh` sube
lo que hay en la carpeta, no lo que está en una rama. El 2026-10-22 se desplegó `web/animaciones` (salida de
`web/movil`) y desaparecieron de la web 17 cambios de `web/v019` (Seguimiento, Títulos › Tendencias, estilos de
texto, máscaras en textos, herramientas del celular). Antes de desplegar: `git fetch` y `git log origin/<rama
desplegada antes> ^HEAD` tiene que salir vacío; si no, unirla primero. Desde entonces la rama viva es
`web/animaciones` (ya une `web/v019`).

**En Windows no hay WSL.** El `deploy.sh` de los sitios usa `tar | ssh`; desde PowerShell se
arma el tar con `tar.exe` y se sube con `scp`, y la mitad remota va en un `.sh` aparte
(`tools/e2e/deploy_remote.sh`).
