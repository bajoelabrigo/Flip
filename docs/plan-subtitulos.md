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
- [ ] 1. El karaoke se desincroniza: editar o mover un subtítulo borra el tiempo de cada palabra de todo el clip
  (`SubtitleEditor.qml` `cloneCues`, `SubtitleCueLane.qml`); «quitar muletillas», el diccionario y los emojis
  tampoco actualizan `wordEndsUs` (`finalizeGeneratedSubtitles`).
- [ ] 2. Mensajes en inglés: «Transcribing…», «Detecting language…», «Finishing up…», «Finding speech…», «Timing
  words…» y los nombres de los idiomas (`QLocale::languageToString`).
- [ ] 3. El idioma se detecta solo con los primeros 30 s (`WhisperTranscriber.cpp`).
- [ ] 4. Sin el extra de sincronía, la IA puede inventar texto en los silencios (falta detectar voz).
- [ ] 5. Importar un SRT lo pone en el cabezal: si no está en 0, queda desfasado.
- [ ] 6. El SRT exportado sale desfasado si el clip no empieza en 0 (la opción por defecto es la equivocada).
- [ ] 7. Generar dos veces sobre el mismo tramo encima dos clips de subtítulos.
- [ ] 8. Una sola línea de 42 letras, también en vertical; no permite dos líneas (`packSubtitleCues`).
- [ ] 9. El candado de la pista no protege los subtítulos (`setSubtitleCues`, `importSubtitleFileIntoClip`).
- [ ] 10. Curvas de velocidad y clips en reversa: subtítulos mal sincronizados.
- [ ] 11. Chino, japonés y tailandés: se sincronizan mal (separan palabras por espacios).

## Mejorar (más fácil de usar)
- [ ] Recordar las últimas opciones (idioma, largo, traducción).
- [ ] Unificar los 3 lugares desde donde se crean subtítulos (el del panel de audio no tiene estilos ni limpieza).
- [ ] Cambiar el estilo de subtítulos ya hechos desde la misma galería.
- [ ] Botones ◀ ▶ de un fotograma y atajos «inicio aquí» / «fin aquí» en vez de escribir los tiempos.
- [ ] Vista previa antes de aplicar «Limpiar» y «Emojis».
- [ ] Quitar el aviso de «tiempos repartidos» cuando el extra de sincronía está instalado.
- [ ] Quitar el título repetido «Añadir subtítulos automáticos».
- [ ] Aspecto moderno y minimalista en todo el panel (ver la regla de arriba).

## Agregar
Lo que tienen CapCut, Premiere y Descript:
- [ ] Dividir y unir subtítulos sueltos; «dividir en el cabezal».
- [ ] Estilo y posición por subtítulo (no solo por clip).
- [ ] Traducir a muchos idiomas y subtítulos bilingües.
- [ ] Editar el video borrando texto (como Descript).
- [ ] Revisar los silencios uno por uno antes de quitarlos.
- [ ] Colores y nombres por hablante (el motor ya distingue voces).
- [ ] Reglas de lectura con aviso (letras por segundo, muy cortos, muy largos).
- [ ] Mover todos los subtítulos a la vez (adelantar o atrasar).
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
(se va llenando)
