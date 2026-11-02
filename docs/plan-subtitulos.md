# Subtítulos: plan (Jorge, 2026-11-01)

Lista acordada con Jorge tras revisar el área de subtítulos de la app de escritorio. Rama `flip/subtitulos`
(sale de `flip/aviso-web`, que ya lleva el aviso de «Editar en línea»). Va en la próxima versión del escritorio.

**Regla para todo lo de esta lista (Jorge):** que sea **fácil de usar** y que el aspecto sea **moderno y
minimalista**: pocas opciones a la vista, lo avanzado plegado, textos cortos, nada repetido, una sola forma clara
de hacer cada cosa.

Cómo seguir: marcar cada punto al terminarlo con el commit; probar en ventana antes de publicar (regla de siempre).

## Lo que ya tiene (referencia)
- Crear subtítulos con IA en la computadora (Whisper); con el extra de sincronía, tiempo exacto por palabra
  (`engine/LocalTranscription.cpp`, `WhisperTranscriber.cpp`, `AppController::generateSubtitlesForSources`).
- Opciones: largo, 10 estilos + los de Stock, quitar muletillas, emojis, traducción al inglés (`SubtitlesTab.qml`).
- Editar: `SubtitleEditor.qml` (líneas, buscar y reemplazar, diccionario), `SubtitleCueLane.qml` (arrastrar).
- Archivos: SRT, VTT, ASS (`core/SrtIO.*`). Voz en off desde los subtítulos; quitar silencios.

## Corregir
- [x] 1. El karaoke se desincroniza: editar o mover un subtítulo borra el tiempo de cada palabra de todo el clip
  (`SubtitleEditor.qml` `cloneCues`, `SubtitleCueLane.qml`); «quitar muletillas», el diccionario y los emojis
  tampoco actualizan `wordEndsUs` (`finalizeGeneratedSubtitles`).
- [x] 2. Mensajes en inglés: «Transcribing…», «Detecting language…», «Finishing up…», «Finding speech…», «Timing
  words…» y los nombres de los idiomas (`QLocale::languageToString`).
- [ ] 3. El idioma se detecta solo con los primeros 30 s (`WhisperTranscriber.cpp`).
- [ ] 4. Sin el extra de sincronía, la IA puede inventar texto en los silencios (falta detectar voz).
- [x] 5. Importar un SRT lo pone en el cabezal: si no está en 0, queda desfasado.
- [x] 6. El SRT exportado sale desfasado si el clip no empieza en 0 (la opción por defecto es la equivocada).
- [x] 7. Generar dos veces sobre el mismo tramo encima dos clips de subtítulos.
- [~] 8. Una sola línea de 42 letras, también en vertical; no permite dos líneas (`packSubtitleCues`).
- [x] 9. El candado de la pista no protege los subtítulos (`setSubtitleCues`, `importSubtitleFileIntoClip`).
- [ ] 10. Curvas de velocidad y clips en reversa: subtítulos mal sincronizados.
- [ ] 11. Chino, japonés y tailandés: se sincronizan mal (separan palabras por espacios).

## Mejorar (más fácil de usar)
- [x] Recordar las últimas opciones (idioma, largo, traducción).
- [ ] Unificar los 3 lugares desde donde se crean subtítulos (el del panel de audio no tiene estilos ni limpieza).
- [ ] Cambiar el estilo de subtítulos ya hechos desde la misma galería.
- [x] Botones ◀ ▶ de un fotograma y atajos «inicio aquí» / «fin aquí» en vez de escribir los tiempos.
- [ ] Vista previa antes de aplicar «Limpiar» y «Emojis».
- [x] Quitar el aviso de «tiempos repartidos» cuando el extra de sincronía está instalado.
- [x] Quitar el título repetido «Añadir subtítulos automáticos».
- [ ] Aspecto moderno y minimalista en todo el panel (ver la regla de arriba).

## Agregar
Lo que tienen CapCut, Premiere y Descript:
- [x] Dividir y unir subtítulos sueltos; «dividir en el cabezal».
- [ ] Estilo y posición por subtítulo (no solo por clip).
- [ ] Traducir a muchos idiomas y subtítulos bilingües.
- [ ] Editar el video borrando texto (como Descript).
- [ ] Revisar los silencios uno por uno antes de quitarlos.
- [ ] Colores y nombres por hablante (el motor ya distingue voces).
- [ ] Reglas de lectura con aviso (letras por segundo, muy cortos, muy largos).
- [x] Mover todos los subtítulos a la vez (adelantar o atrasar).
- [ ] Subtítulos dentro del MP4 (activables) y un `.srt` al lado del video al exportar.
- [ ] ASS con el estilo real del proyecto.
- [ ] Palabras difíciles antes de transcribir (nombres, marcas, términos).

Para redes (estilo CapCut):
- [ ] Palabras clave resaltadas por la IA (color o tamaño) y emojis animados de Stock.
- [ ] Más plantillas de subtítulos virales en Stock (palabra por palabra, rebote, caja que sigue la palabra).
- [ ] Filtro de groserías (*** o pitido).
- [ ] Revisión de ortografía.
- [ ] Elegir la transcripción en la nube (ElevenLabs) desde el panel de subtítulos.

## Hecho
- 2026-11-01, rama `flip/subtitulos` (sin compilar ni probar en ventana todavía; se prueba todo junto con la build):
  - `7ff3e` karaoke: los tiempos por palabra viajan con cada subtítulo (editor y carril), un subtítulo movido
    entero corre los suyos; limpiar, diccionario y buscar/reemplazar los reacomodan (`realignWordEnds`, con pruebas
    en `tst_core` y probado aparte compilando `SubtitleCue.cpp`).
  - `48045` mensajes de progreso traducidos (15 idiomas) y cada idioma con su propio nombre («Español», «Deutsch»).
  - `7e3f0` un SRT importado empieza en 0:00 en una pista libre; exportar usa por defecto los tiempos del video.
  - candado: no deja cambiar ni importar subtítulos en una pista bloqueada; generar otra vez va a otra pista.
  - panel: recuerda idioma y largo, sin el título repetido, sin el aviso cuando está «Sincronía de palabras».
- Segunda ronda (rama `flip/subtitulos`, sin compilar todavía):
  - largo de cada subtítulo según la forma del video (vertical 26 letras, cuadrado 32, horizontal 42): en vertical
    salían 3 o 4 líneas. La caja ya parte en líneas sola; falta ver en ventana si conviene un máximo de 2 líneas.
  - editor: inicio y fin en su propia fila con ◀ ▶ de un fotograma y «al cabezal»; Dividir en el cabezal (con los
    tiempos por palabra), Unir con el siguiente, Eliminar en una fila; «Mover todos» ±0,1 s. Atajos de teclado: pendiente.
