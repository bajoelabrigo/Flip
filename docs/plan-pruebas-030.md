# Pruebas de la 0.30: 5 proyectos de After Effects y 3 de subtítulos

Pedido de Jorge (2026-11-03): preparar 5 proyectos para la línea de tiempo tipo After Effects y 3 para los subtítulos,
usando todas las herramientas instaladas, en escenarios distintos. Se hacen en ventana, se anotan los errores en la
lista de abajo (sin arreglar nada a mitad de camino), al final se corrige todo, se compila una vez y se repite hasta
que quede al 100 %.

- Proyectos de partida y material: `E:\FlipStudio\pruebas\proyectos-030\` (`ae1…ae5`, `sub1…sub3`), armados con
  `tools/e2e/mcp_e2e.py` y los `make-*.jsonl` de esa carpeta (solo el material y las capas; la animación se hace a mano
  en la prueba, como un usuario).
- Antes de cada sesión: copia del registro desde PowerShell; al final, restaurarla (y la clave `account` exportada
  después, si se usó la cuenta). Variables para los extras sin publicar: `DRIFT_TRANSLATE_MODEL_DIR`,
  `DRIFT_DIARIZE_MODEL_DIR`, `DRIFT_TEXT_STYLES_DIR` (rutas en `docs/plan-subtitulos.md`).
- Sin el mouse de Jorge: `tools/e2e/shot.ps1` / `click.ps1` / `drag.ps1` / `type.ps1` con `-TargetPid`, y MCP para
  leer el estado. Con el mouse de Jorge (cuando él está): computer use.

## After Effects

### AE1 — Pelota que rebota y sale de cuadro (formas, Posición unida)
Material: fondo sólido 1920×1080, círculo (capa de forma) y una línea de suelo.
1. Activar Posición con el cronómetro; claves de caída, golpe, dos rebotes y salida por la derecha.
2. Ver que Posición se unió sola (menú de la clave: «Separar dimensiones»).
3. Curvar el trayecto con los tiradores de la vista previa: el ritmo no debe cambiar.
4. F9 en las claves altas; gráfico de velocidad («Pos»): caída que acelera, subida que frena.
5. «Itinerante» en las claves del medio; «Trayecto recto» en el golpe (esquina).
6. Escala: Squash al golpe (claves copiadas y pegadas en cada golpe), anclaje abajo.
7. Separar dimensiones y volver a unir; deshacer y rehacer.
Resultado esperado: rebote creíble, sin saltos; el trayecto no se deforma al cambiar el ritmo.

### AE2 — Título cinético con nulo (varias capas a la vez)
Material: tres textos («FLIP», «STUDIO», «0.30») y un objeto nulo.
1. Emparentar los tres textos al nulo; animar Escala y Rotación del nulo.
2. Entradas escalonadas: claves de Opacidad y Posición en cada texto.
3. Elegir claves de las tres capas con Ctrl+clic y con un recuadro que cruce las tres pistas; F9, arrastrar, estirar
   con Alt, invertir; un solo deshacer para cada cosa.
4. Juego de atajos «After Effects»: P/S/R/T/A, U y UU, J/K, B/N (zona de trabajo), [ ] y Alt+[ ].
5. Zona de trabajo: arrastrarla y reproducir (se detiene al final).
Resultado esperado: todo actúa en las tres capas; los atajos hacen lo de AE.

### AE3 — Producto con trayecto curvo y Auto-Orient (vista previa y gráfico)
Material: video del robot (1280×720) de fondo y una imagen/forma de «producto» encima.
1. Trayecto en S con cuatro claves; tiradores en la vista previa (Ctrl rompe la simetría).
2. Auto-Orient: el producto mira hacia donde va.
3. Velocidad numérica (diálogo) en varias claves a la vez, en px/s del trayecto.
4. Cuentas en los valores: «+50», «*2», «(1920-200)/2».
5. Gráfico sobre toda la línea de tiempo: rueda, Ctrl+rueda, Alt+rueda, «Ver toda la curva», «Acercar a las elegidas»,
   recuadro de transformación (estirar en tiempo, escalar valores).
Resultado esperado: curva suave, ritmo parejo, cuentas bien, el gráfico no se pierde.

### AE4 — Infografía con expresiones y Motion Tools
Material: cinco barras (formas) y un texto contador.
1. Expresiones: `wiggle`, `loopOut`, `index * 10`, `thisLayer.index`, `linear(time, 0, 2, 0, 100)`,
   `valueAtTime(time - 0.2)`, `velocity`.
2. Motion Tools: Elastic y Bounce sobre la Escala de las barras; Curvas (presets y propia) en las claves elegidas.
3. Panel Curvas con claves de varias capas elegidas: aplicar en todas.
4. Copiar claves de una barra y pegarlas con las cinco elegidas.
Resultado esperado: expresiones sin error, cada barra según su índice, los paneles tocan todas las capas elegidas.

### AE5 — Video vertical para redes con zooms al ritmo (curvas de varias capas)
Material: video vertical 1080×1920 a 120 fps y dos textos encima.
1. Zooms rápidos (Escala) y sacudida (Posición) en el video; los mismos en los textos.
2. Gráfico con las tres capas elegidas: tocar las claves de las otras capas (clic = editar esa capa, Ctrl = sumar),
   arrastrarlas en el tiempo juntas, recuadro sobre varias capas.
3. Velocidad del fotograma clave para muchas claves; Curvas «Rebote» en todas.
4. Exportar un tramo con la zona de trabajo.
Resultado esperado: se editan las curvas de las tres capas sin cambiar de capa a cada rato.

## Subtítulos

### SUB1 — Entrevista horizontal con dos voces
Material: `entrevista.mp4` (dos personas).
1. Crear subtítulos con «Distinguir a los hablantes» y «Resaltar palabras clave».
2. Traducir al inglés con DeepL (con sesión): ver que no se encime con el original y que diga «English».
3. «Editar con el texto»: tachar dos frases y cortar; los dos clips de subtítulos siguen sincronizados.
4. Exportar MP4 con la pista de subtítulos y el `.srt`/`.vtt` al lado (ffprobe).

### SUB2 — Vertical estilo TikTok
Material: `charla-vertical.mp4`.
1. Estilos virales (los 12), subtítulos animados (emoji), estilo y lugar por subtítulo.
2. Quitar silencios: las otras pistas (música, texto) se corren en el mismo deshacer.
3. Groserías con pitido; aviso «Pitido en 1 palabra».
4. Máximo de dos líneas; palabras clave en color.

### SUB3 — Sin sesión y sin internet
Material: video de B-roll con voz (`voz.wav` sobre el video de la gente).
1. Sin sesión: transcribir en el equipo.
2. Traducir con el modelo del equipo (extra «Traducción sin internet», con `DRIFT_TRANSLATE_MODEL_DIR`): el aviso de
   «Traduciendo los subtítulos en tu computadora…», el clip traducido y su tiempo por línea.
3. Importar un `.srt`, mover tiempos, karaoke (palabra resaltada), exportar quemado.

## Lista de errores (se llena durante las pruebas; no se arregla nada hasta el final)

| # | Proyecto | Qué pasó | Estado |
|---|---|---|---|
