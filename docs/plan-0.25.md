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
- [x] 1. **Recuadro para elegir claves** en las filas: arrastrar en vacío dibuja un rectángulo y elige todas las
      claves que toca (varias propiedades y clips de la pista). Mayús o Ctrl suman a las ya elegidas.
- [x] 2. **Clic en el nombre de una fila** elige todas sus claves (en la cabecera de la pista).
- [x] 3. **Ctrl+A** con claves elegidas: todas las claves de esa pista.
- [x] 4. **Estirar en el tiempo:** Alt + arrastrar la primera o la última de varias elegidas las acerca o aleja
      en proporción.
- [x] 5. **Mayús+J / Mayús+K** clave anterior / siguiente (J ya es «frenar» del avance tipo Premiere; se
      cambian en Atajos); **U** abre las pistas con claves y deja solo las filas animadas (otra vez: las cierra).
      `AppController::stepToKeyframe`, `toggleRevealKeyframes`, `m_keyframeRowsAnimatedOnly`.
- [x] 6. Recuadro también en el **editor de curvas**, y arrastrar el valor de varias claves a la vez.
- [x] 7. **Gráfico de velocidad** (botón del velocímetro en el editor de curvas: |Δvalor/Δt| de la curva enfocada,
      muestreado de lo que suena/se ve) y **separar X e Y** de Posición (botón de cadena = `positionLinked`).
- [x] 8. **Trazo del movimiento** en la vista previa (`preview/MotionPathOverlay.qml`, dentro de
      `TransformOverlay`): la línea del centro del clip y un rombo por clave de Posición que se arrastra.
- [~] 9. **Igualar texto, video, imagen y forma:** mismas filas fijas (Posición, Rotación, Escala, Opacidad) y
      después las del texto (tamaño, capas, letras) con los mismos gestos. Ya iguales en las filas. **Hecho:**
      la Transformación de las letras elegidas (X, Y, Escala, Rotación) se anima con rombo: las letras llevan
      `TextRun::animId` y las claves son `text.run.<animId>.<campo>` (`TextStyle.cpp`: `parseRunKey`,
      `runKeyframeFields`). Falta: opacidad de las letras con rombo en «Letras seleccionadas».
- [x] 10. **Audio** (Jorge lo aprobó el 2026-10-27, «hazlo tal y como me lo indicas»):
      - filas fijas **Volumen** (en dB) y **Panorama** en las pistas de audio (`audioKeyframeGroups`,
        `fixedKeyframeGroups` en `AppController.cpp`);
      - **panorama animable**: `Clip::panKeys` (JSON `panKeys`), el mezclador lo evalúa en cada punto de control
        (`AudioMixer.cpp`: `panForClip`, ganancias izquierda/derecha interpoladas); prop `pan` en
        `keyframeTrackForProp`, `writeClipPropValue` y `propertyBaseValue`; Audio › Panorama con rombo;
      - **línea de volumen** sobre la onda (`timeline/ClipVolumeLine.qml`): arrastrar el tramo entre dos claves
        (o todo el nivel), Ctrl+clic pone una clave, los puntos se arrastran (Mayús: solo el nivel), doble clic
        los quita. Escala en dB de −40 a +6;
      - **fundidos a claves**: clic derecho › «Fades to volume keyframes» (`convertFadesToVolumeKeys`);
      - **imán al ritmo**: ya lo daba `snapTime` (golpes cuando la cuadrícula de ritmo está visible).

## Cómo se probó / qué falta probar
- CI: Tests y Build de Windows en verde (rama `flip/v0.24.1`).
- **Probado en ventana (2026-10-27, portables `pruebas\FlipStudio-0.25-prueba` y `-b`, capturas en
  `pruebas0241-giro`):** recuadro en las filas (elige Posición y Opacidad que toca, también en curvas), clic en el
  nombre de la fila, U (cierra; otra vez abre solo las filas animadas), gráfico de velocidad, trazo del movimiento
  (arrastrar un rombo mueve la clave), filas Volumen/Panorama del audio (Panorama 0 → 4 s a la derecha marca «R 51»
  a los 2 s), línea de volumen (25 px = −7,5 dB), nombres de los campos de Transformación de letras, y **el giro
  completo de una sola letra**: rombos en Transformación de la «H», claves 0 s y 3 s = 360°, la H gira y «OLA» no.
- Arreglado tras la prueba: `AppController::patchTextRuns` no daba `animId` (no salían los rombos), las pistas de
  audio sin flecha, la línea de volumen se quedaba con el hover del clip, chips del editor de curvas con la clave
  cruda (`text.run.r42….rotation`).
- **Sin probar (los clics simulados no llevan Alt/Ctrl/Mayús ni abren popups):** Alt+arrastrar (estirar), Ctrl+A,
  Mayús+J/K, Ctrl+clic en la línea de volumen, el cuadro para escribir el valor (popup) con 360° o más, oír el
  panorama. Que lo pruebe Jorge.
- Textos nuevos: catálogos regenerados y traducidos al español.

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
