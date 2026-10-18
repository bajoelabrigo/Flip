# Plan de la 0.17.0 (pedido de Jorge, 2026-10-18)

Este archivo es para **seguir el trabajo con cualquier asistente** (Claude, DeepSeek u otro). Antes de nada, leer
`CLAUDE.md` (mapa del proyecto, rutina de publicación y trampas). Rama: **`flip/v0.17.0`** (sale de `main` con la
0.16.0 publicada). Regla de Jorge: **si CapCut o Filmora ya resolvieron cómo se comporta algo, se copia**, no se
inventa. Todo lo que lee Jorge va en español; el código sigue el estilo del archivo (inglés).

**Cómo se trabaja aquí:** se prueba cada cambio mientras se hace (qmllint para QML, pruebas en `tests/`), y se compila
**una sola vez al final** en GitHub Actions (`gh workflow run build.yml --ref flip/v0.17.0 -f platforms=windows`, tarda
40–70 min). Después se prueba el portable **en ventana** (ver «Pruebas» en `CLAUDE.md`) y recién entonces se publica
(«Rutina de publicación» en `CLAUDE.md`). Catálogos de traducción: `lupdate` → traducir `i18n/drift_es.ts` →
`lupdate` otra vez para comprobar que no cambia (ver `CLAUDE.md`, «Comprobar los catálogos»).

Leyenda: ✅ hecho en la rama · 🟡 empezado · ⬜ por hacer.

## 1. Arreglos rápidos
- ✅ **Panel izquierdo abre con la fila de categorías completa.** `Main.qml`: `SplitView.preferredWidth` del
  `AssetsPanel` = máx(25 % del ancho, `assetsPanel.categoryRowWidth`, tope 45 %). El ancho guardado se guarda ahora en
  la clave `assetsWide` (la vieja `assets`, angosta, se ignora una vez). Si el usuario lo achica, se recuerda.
- ✅ **La X de la ventana en el editor vuelve al inicio** (como CapCut/Filmora); en el inicio, la X cierra la app.
  `Main.qml` `onClosing` (solo Windows/Linux) llama a `requestCloseProject()`; `quitApp()` + `quitRequested` para
  Archivo › Salir (`AppMenuBar.qml`). `main.cpp`: en `commitDataRequest` (apagar/cerrar sesión de Windows) pone
  `quitRequested = true` en la ventana para no frenar el apagado.
- ✅ **Selector de idioma del primer arranque:** ya preseleccionaba el idioma de Windows desde la 0.12.0 (commit
  `6fd54`, `LanguageChooserDialog.qml` `systemChoice()`). Era una nota vieja; no hubo que tocar nada.

## 2. Comportamiento como CapCut
- ✅ **Congelar fotograma** (`AppController::freezeFrameAtPlayhead`): divide el clip en el cabezal, mete una foto **de
  ese clip** (no de toda la imagen) de **3 s en la misma pista** y corre el resto y su audio vinculado
  (`rippleTracksFrom`). Toma el clip seleccionado si el cabezal está sobre él; si no, el de la pista de video de más
  abajo. **Falta probarlo con la app** (MCP `freeze_frame` en headless o el botón en ventana).
- ✅ **Mover un clip con «Cerrar huecos» activado cierra el hueco** (imán de la pista principal): en `moveClip`, solo
  pistas de video y arrastres de una pista (el audio vinculado acompaña). Ordena por el centro de cada clip y los pone
  seguidos desde donde empezaba el primero. No reordena la lista (solo cambia los inicios). Prueba:
  `EditorStateTest::moveWithRippleClosesTheTrack`.

## 3. Modo oscuro y pantalla de inicio como Filmora
Jorge eligió **idéntico a Filmora, con acento turquesa**. Capturas de referencia en `C:\Users\bajoe\Downloads`:
`Filmora.png`, `Ayuda.png`, `Ver.png`, `Herramientas.png`, `Editar.png`, `Archivo.png` (editor) y
`Captura de pantalla 2026-10-18 030324.png` (inicio).
- 🟡 **Colores** (`Theme.qml`): tema nuevo **`teal`** («Turquesa»), ahora el predeterminado (también en
  `PreferencesController.cpp`). Medidos en las capturas: paneles `#181c1f`, fondo `#111416`, menús `#202427` (token
  nuevo `menuBackground`, usado por `ThemedContextMenu`), fila seleccionada `#31363b`, bordes `#272b2e`, texto
  `#c3cad0`/`#e8eaeb`, acento `#2EE6C5`, degradado `#25ecd5 → #2cb0f0 → #3b6cf6`. Tokens nuevos para el inicio:
  `homeBackground #0a0d0f`, `homeCard #131517`, `homeActive #25292d`. El submenú Ajustes › Color se arma desde
  `Theme.colorThemes` (antes tenía posiciones fijas). **Falta:** revisar en ventana que todo se lea bien; el amarillo
  queda como uno de los colores a elegir.
  - Trampa: los colores con alfa en QML son `#AARRGGBB` (alfa primero).
- ⬜ **Pantalla de inicio como la de Filmora** (`components/StartScreen.qml`): barra lateral con logo, Crear proyecto
  (activo), Extras, Ajustes… y la tarjeta de usuario abajo («Haz clic para iniciar sesión» sin sesión); arriba el
  selector de formato (16:9…) a la izquierda y «Abrir proyecto» a la derecha; botón ancho «+ Crear proyecto» con el
  degradado; a su derecha un carrusel (novedades y kits de Stock: `Market.newsSummary`, `/v1/market/home`); fila de
  herramientas rápidas (subtítulos automáticos, quitar fondo, texto a voz, mejorar video, stickers, «Más»);
  «Proyectos locales» con buscar, recargar y lista/cuadrícula, y un dibujo vacío «Proyecto reciente». Fondo
  `Theme.homeBackground`.

## 4. Marca «IA» y botón «?»
- ⬜ Componente nuevo (p. ej. `components/AiBadge.qml`): texto «IA» (estilo del «AI» de Filmora, en turquesa) y un «?»
  con `ThemedToolTip` que explique la función. Texto base: *«Funciona con IA en tu computadora, sin internet: tu video
  no sale de tu equipo.»* más una línea propia de cada función.
- Dónde (todo lo que ya tenemos con IA, local): barra lateral de `AssetsPanel.qml` (Subtítulos, Voz, Escenas), páginas
  del panel de Video (Eliminar fondo, Retoque › Rostro/Cuerpo/Cabello), botones de la barra de la línea de tiempo
  (`TimelineToolbar.qml`: transcribe, cutSilences, removeBg, enhanceAudio, enhanceVideo) y Mejorar video / Reducir
  ruido. Motores: Whisper (subtítulos, silencios), Chatterbox Multilingual (voz), RVM y SAM 2 (fondo), MediaPipe
  (rostro, cuerpo, cabello), modelos de restauración y de ruido, detección de objetos, profundidad, separar hablantes.

## 5. Funciones nuevas de IA (solo lo factible y gratis)
Investigado y probado en la PC de Jorge (RTX 5060) el 2026-10-18; ver también la memoria del proyecto.
- ⬜ **Transiciones con IA y cámara lenta suave: RIFE 4.25** (código y pesos MIT). ONNX listo del proyecto vs-mlrt,
  release `external-models`: `https://github.com/AmusementClub/vs-mlrt/releases/download/external-models/rife_v4.25.7z`.
  Usar el grafo de la carpeta **`rife_v2/`**: entrada `input` fp32 `[1,7,H,W]` = fotograma A en RGB, fotograma B en RGB
  y un plano con el instante t (p. ej. 0,5), valores 0–1 en planos; salida `output` `[1,3,H,W]` RGB; ~22,7 MB; ~70 ms
  por fotograma 1080p en GPU (DirectML), ~1,9 s en CPU. Hacer un extra en `flip-addons` (tipo nuevo, p. ej.
  `interp-model`), sesiones con `drift::ort::buildSessions` (trampa en `CLAUDE.md`), y comprobar cortes de escena
  antes (RIFE deja «fantasmas» en cortes duros). Versión rápida: 4.25 lite.
- ⬜ **Texto con IA, versión simple:** la persona escribe una idea («título de terror») y se elige y ajusta uno de
  nuestros ~200 estilos de texto. Modelo **paraphrase-multilingual-MiniLM-L12-v2** (Apache-2.0), ONNX int8 de 118 MB
  (Hugging Face `Xenova/paraphrase-multilingual-MiniLM-L12-v2`, carpeta `onnx/`). Tokenizador XLM-R SentencePiece
  (biblioteca `sentencepiece`, Apache-2.0; ids `<s>`=0, `</s>`=2, desplazamiento +1 de fairseq). Entradas
  `input_ids`, `attention_mask`, `token_type_ids` (int64); salida `[1,T,384]` → promedio con la máscara + normalizar.
  Las incrustaciones de los 200 estilos se calculan fuera de la app y se guardan con el catálogo. Acertó 12 de 13 ideas
  en 6 idiomas, ~3 ms en CPU. **No usar** EmbeddingGemma (licencia Gemma) ni MusicGen (no comercial).
- No ahora (pesado, necesita tarjeta gráfica o un servicio de pago): música con IA (ACE-Step), efectos de sonido
  (Stable Audio Open), stickers (FLUX.1 schnell). ElevenLabs ya está en el código (MCP `sfx_generate`) pero es de pago.

## 6. Vistas previas al pasar el mouse
- ⬜ Las tarjetas de **plantillas y de Stock** se animan al entrar a la pestaña, pero **no al poner el mouse encima**:
  al pasar el mouse tienen que reproducir su vista previa animada (`StockThumb.qml`, `SceneTemplateBrowser.qml`).
- ⬜ **Efectos y Filtros (LUT):** al pasar el mouse, un **antes y después** animado sobre la foto de muestra
  (`EffectBrowser.qml`, `components/assets/FiltersTab.qml`, `components/properties/LutPage.qml`).

## 7. Pendientes viejos (todos entran)
- ⬜ **Traducciones:** lo nuevo de la 0.16 y la 0.17 (menús, categorías, Filtros, avisos de inicio de sesión) solo está
  en español; los otros idiomas lo ven en inglés. Traducir con `lupdate` + los `.ts` de cada idioma (se puede repartir
  entre agentes por idioma, como en `tools/stock_i18n`). También «Same as project» en Exportar sale en inglés.
- ⬜ **Contadores animados** en el motor (hoy las plantillas de contador van con cortes).
- ⬜ **Las 9 pistas de música FMA** en espera: preparar una lista para que Jorge las escuche y decida.
- ⬜ **Texto como forma de máscara** (Video › Máscara).
- ⬜ **Quitar imperfecciones** (manchas y arrugas) en Retoque.
- ⬜ **Voz con IA en el editor web** (`flipstudio-app`), que espera al servidor.
- Hecho y fuera de la lista: exportar en 4K y 8K (**probado por Jorge, funciona**).
- Siempre al final del proyecto: pagos y tienda de cada usuario. Hasta entonces, todo gratis.

## Al cerrar la versión
Versión 0.17.0 en `CMakeLists.txt`, `release-notes/0.17.0.md`, CHANGELOG, notas de la Store en
`docs/store-listing.md` (máx. 1.500 caracteres), compilación en GitHub, prueba en ventana, PR, tag, release, MSIX,
copia en `versiones`, novedades en la web y `CLAUDE.md`. Lo de Jorge: TXT `version` y Partner Center.
