# Plan 0.25 — Fotogramas clave como After Effects (texto, video, imagen y audio)

Pedido de Jorge (2026-10-27): «aún no me convence; no puedo con el mouse dibujar y marcar varios keyframes al
mismo tiempo». Hacer **todo** lo de la comparación con After Effects e igualar texto, videos, imágenes y audio.
Rama: `flip/v0.24.1` (empezó con el arreglo del Ángulo; se publicará como 0.25.0).

## Dónde vive cada cosa
- Filas bajo cada pista: `src/qml/components/timeline/TrackKeyframeRows.qml` (las arma
  `AppController::trackKeyframeRows`, en `AppController.cpp`, con `keyframeGroups()`).
- Claves elegidas, menú, atajos (F9…): `src/qml/components/timeline/KeyframeKeyTools.qml` (una por línea de
  tiempo, `keyTools` en `TimelinePanel.qml`, compartida con el editor de curvas).
- Editor de curvas: `src/qml/components/KeyframeGraph.qml`.
- Fila del inspector (deslizador + valor + rombo): `src/qml/components/PropertyKeyframeRow.qml`.
- Atajos de Editar (Suprimir, Copiar, Pegar, Seleccionar todo): `Main.qml` › `dispatchAction`.

## Lista (en el orden en que se hace)
- [x] 0. **Ángulo de más de 180°** (Jorge): `PropertyKeyframeRow` recortaba lo escrito al rango del deslizador.
      Ahora `inputFrom`/`inputTo`; el Ángulo acepta ±3600° (10 vueltas). Falta verlo en ventana.
- [ ] 1. **Recuadro para elegir claves** en las filas: arrastrar en vacío dibuja un rectángulo y elige todas las
      claves que toca (varias propiedades y clips de la pista). Mayús o Ctrl suman a las ya elegidas.
- [ ] 2. **Clic en el nombre de una fila** elige todas sus claves (en la cabecera de la pista).
- [ ] 3. **Ctrl+A** con claves elegidas: todas las claves de esa pista.
- [ ] 4. **Estirar en el tiempo:** Alt + arrastrar la primera o la última de varias elegidas las acerca o aleja
      en proporción.
- [ ] 5. **J / K** clave anterior / siguiente del clip; **U** muestra solo las filas con claves.
- [ ] 6. Recuadro también en el **editor de curvas**, y arrastrar el valor de varias claves a la vez.
- [ ] 7. **Gráfico de velocidad** en el editor de curvas (además del de valores) y **separar X e Y** de Posición.
- [ ] 8. **Trazo del movimiento** en la vista previa: la línea del recorrido de Posición con un punto por clave
      que se arrastra.
- [ ] 9. **Igualar texto, video, imagen y forma:** mismas filas fijas (Posición, Rotación, Escala, Opacidad) y
      después las del texto (tamaño, capas, letras) con los mismos gestos.
- [ ] 10. **Audio** (ver abajo).

## Audio (propuesta, a confirmar con Jorge)
After Effects casi no tiene audio (solo «Niveles de audio» en dB, con claves). La referencia buena es Premiere,
que viene de la misma casa:
- Pistas de audio con filas fijas: **Volumen (dB)** y **Panorama**, más los parámetros de los efectos de audio
  animados. Mismos gestos que en video: rombo, recuadro, estirar, Ctrl+A, curvas.
- **La línea de volumen sobre la onda del clip** («banda elástica»): arrastrarla sube o baja todo, Ctrl+clic pone
  un punto, y los puntos se arrastran como claves (son las mismas claves de `volume`).
- **Panorama animable:** hoy `Clip::pan` es un número fijo; hace falta pista de claves en el motor y el mezclador.
- Fundidos (ya hay asas en las esquinas) que se vean como claves y se puedan pasar a claves.
- Claves pegadas al **ritmo** (ya hay análisis de golpes): imán a los golpes al arrastrar claves.
