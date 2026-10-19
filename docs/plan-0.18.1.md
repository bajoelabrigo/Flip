# Plan 0.18.1 — arreglos del control de calidad de la 0.18

Pedido de Jorge (2026-10-18): «sigue con lo tuyo», o sea, el control de calidad de la 0.18 por MCP, con una app de
prueba sin ventana (`pruebas\qa018`: `qa.py` = sesión y registro de fallos; `qa_media.py`, `qa_render.py` y
`qa_misc.py` = las tandas; resultados en `out\`). Rama `flip/v0.18.1`.

## Lo que se probó y pasó
- Importar 15 archivos: H.264, HEVC, MJPEG/AVI, MKV, video mudo, ProRes, vertical de 60 fps, VP9/WebM, GIF animado, y
  audio en MP3, WAV, FLAC, OGG, Opus y M4A. Las capturas de cada clip tienen imagen.
- Cortar, transición, velocidad 0,5, texto, deshacer + rehacer (mismo hash), guardar y reabrir (mismos clips),
  exportar MP4 (dura lo pedido y se reimporta) y GIF.
- Los 78 efectos y las 40 transiciones del catálogo se aplican y se dibujan; comparados píxel a píxel. Los que no
  cambian la imagen lo hacen por diseño: necesitan una cara, golpes de música o un modelo de profundidad.
- 48 animaciones de texto, todos los looks de texto, stickers, formas, golpes, silencios, sonoridad, normalizar,
  volumen, forma de onda y subtítulos (crear, exportar SRT con tildes y reimportar).
- Exportar con cada códec: AV1 (8 y 10 bits), FFV1, H.264 (también NVENC y 10 bits), H.265 (8, 10, 12 bits y NVENC),
  MPEG-4, MPEG-2, VP8, VP9 (también alfa y 10 bits), ProRes, ProRes 4444 y Theora; audio AAC, Opus, MP3, AC3 y FLAC;
  4K con H.264 y 8K con H.265 (H.264 a 8K se niega con su aviso, como debe).
- Congelar fotograma funciona como CapCut: corta en el cabezal, mete una foto de 3 s y empuja el resto.
- Arrastre «tipo tetris»: probado en ventana por Jorge, funciona.

## Arreglos (hechos, falta compilar)
- ✅ **Pintura al óleo no hacía nada** (desde Drift): el shader usaba la variable `flat`, palabra reservada de GLSL;
  no compilaba y el efecto se saltaba sin avisar. Renombrada a `flatColor`. Ningún otro shader tiene el problema.
- ✅ **DNxHR no exportaba nunca** («Could not open the video encoder»): el codificador `dnxhd` de FFmpeg usa por
  defecto el perfil DNxHD clásico. Ahora pide `dnxhr_hq` (o `dnxhr_hqx` en 10 bits); comprobado con ffmpeg en
  `.mov`, `.mxf` y `.mkv`.
- ✅ **Texto › Efectos salía en inglés** (Shadow, Offset, Direction…) y las unidades de grados como «90Â°»:
  - la unidad se leía con `QLatin1String` y el «°» viene en UTF-8; ahora es `QString::fromUtf8` en `TextLook`,
    `TextShading` y `TextAnimationPreset`;
  - los nombres de los looks se extraían al contexto `drift`, pero la app los buscaba en `TextLook`;
  - los nombres de los controles no se extraían nunca.
  Ahora van con `QT_TRANSLATE_NOOP` (el ayudante `tr` de `TextLook.cpp` pasa a `lookText`: con `tr(...)` delante,
  `lupdate` no ve el texto). Son 67 textos traducidos en los 12 idiomas completos; `lupdate` queda estable.
- ✅ MCP `freeze_frame` respondía «0 clips nuevos» porque la foto se hace en segundo plano: ahora espera hasta 30 s a
  que entre, o devuelve el aviso de la app (`freeze_failed`).
- ✅ MCP `import_media` con un archivo que existe pero no se puede leer (0 bytes) respondía «ok» con un elemento sin
  nombre ni tipo. Ahora lo cuenta en `unreadable`, o da `import_failed` si no se pudo leer ninguno.

## Tanda de IA (`qa_ai.py`), 2026-10-18 noche: TODO OK
- Máscara y fotogramas clave; estabilizar (la app avisa «Video estabilizado añadido»); escenas (2 cortes) y dividir
  por escenas; caras (seguimiento en cada fotograma) + ojos grandes; profundidad (121 fotogramas en 100 s);
  reencuadre a 9:16 siguiendo la cara; quitar ruido; Whisper en español (24 s).
- La voz por MCP (`tts_generate`) solo va con ElevenLabs (nube, sin clave aquí): para Whisper se usó
  `media\a_voz.wav`, hecha con la voz de Windows (Helena, español).
- Mejora posible (no arreglada): Whisper añadió «A la gente.» en el silencio del final (alucinación típica). Se
  podría descartar un segmento con alta probabilidad de «sin voz» o que caiga en silencio.
- Los scripts están copiados en `tools/e2e/qa018/`. Registro restaurado (0 diferencias), proyectos de prueba
  borrados y autoguardado devuelto: **el control de calidad terminó**.

## Publicación (Jorge, 2026-10-18: «sí, hazlo»)
- ✅ Versión 0.18.1 en `CMakeLists.txt`, `release-notes/0.18.1.md`, CHANGELOG y notas de la Store combinadas
  0.17 + 0.18 + 0.18.1 en `docs/store-listing.md` (1199/1500; en inglés, 1101): ni la 0.17 ni la 0.18 se subieron.
- ✅ Ensayo `build.yml` en la rama: run 39192341876 en verde (instalador y portable).
- ✅ Probado en ventana con el portable (`pruebas\FlipStudio-0.18.1-prueba`): Texto › Efectos dice «Desplazamiento
  6px», «Dirección 90°», «Desenfoque 6px», «Opacidad 0.60»; Pintura al óleo cambia la imagen (antes 0,0); DNxHR
  exporta (DNXHR HQ y HQX). Registro restaurado con la sesión de Google renovada.
- ✅ PR #26 → `main`, tag `v0.18.1`. ✅ Release (run 39195704624) con instalador, portable y `SHA256SUMS`; ✅ copia en `versiones\FlipStudio-0.18.1` (hashes comprobados). MSIX: run 39199587252 →
  `tienda\FlipStudio-Store\paquete-0.18.1`.
- ✅ Novedades de la web desplegadas (comprobado en vivo).
- ⬜ Jorge: TXT `version` = 0.18.1 y subir el MSIX de la 0.18.1 (no el de la 0.18.0) con las notas combinadas.

## Después de publicar: el botón «Actualizar a …» no actualizaba (Jorge, 2026-10-19)
- Síntoma: baja la actualización, pulsas «Actualizar a (versión)» y el editor vuelve a la pantalla de inicio en vez
  de cerrarse e instalar.
- Causa: `Main.qml` respondía a `Updates.quitRequested` con `window.close()`, y desde la 0.17 eso es la X del
  editor, que vuelve al inicio. Pasa desde la 0.17.0.
- ✅ Arreglo en la rama `flip/v0.18.2`: `onQuitRequested` llama a `window.quitApp()` (como Archivo › Salir).
- Mientras tanto, con la app ya instalada: después de pulsar «Actualizar a …», cerrar con la X **en la pantalla de
  inicio** (o Archivo › Salir). La app sale y el instalador arranca solo (`aboutToQuit` → `launchStagedInstall`).
- El arreglo solo sirve a partir de la versión que lo lleve: quien actualice desde 0.17–0.18.1 todavía necesita el
  paso de arriba. La versión de la Store no usa este actualizador.
