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
| 1 | AE1 | La herramienta `add_shape` (MCP) pone la forma en la esquina de arriba a la izquierda, no centrada como dice su descripción | pendiente |
| 2 | AE1 | Tras pasar a Pro, el primer clic sobre un clip no lo eligió (el segundo sí) | revisar |
| 3 | AE1 | Con Posición unida la línea de tiempo sigue mostrando dos filas (Posición X / Posición Y); en AE es una fila «Posición» con los dos valores | pendiente |
| 4 | AE1 | La rueda sobre las filas no las desplaza cuando el panel de la línea de tiempo es bajo (Escala quedaba fuera); hubo que agrandar el panel | pendiente |
| 5 | AE1 | Escala: al escribir 130 en el ancho con el cronómetro recién puesto, la pelota se ensancha pero la fila sigue diciendo 100,0 / 100,0 % (el primer tamaño con clave pasa a ser el 100 %) | pendiente |
| 6 | AE1 | Escala: Tab desde el ancho no pasa al alto (el 75 no se aplicó) | pendiente |
| 7 | AE1 | Al escalar cambian los números de Punto de anclaje (259 → 337) y de Posición X; en AE el anclaje no cambia con la escala | pendiente |
| 8 | AE1 | Separar dimensiones y volver a unir pierde las esquinas («Trayecto recto») de los golpes: todo vuelve a Bezier automático | pendiente |
| — | AE1 | Bien: Posición se une sola, trayecto con tiradores propios, doblarlo no cambia el ritmo, F9 frena sin mover el camino, gráfico de velocidad «Pos» con velocidad pareja por tramo, influencia, Trayecto recto (esquinas), Itinerante, deshacer/rehacer | ok |
| 9 | AE2 | Con un clip elegido, el clic sobre otro clip no cambia la elección (seguía el nulo); hace falta Esc antes. Pasa sobre todo tras usar sus filas o emparentar (mismo que el 2) | pendiente |
| 10 | AE2 | Un texto recién creado dice «Escala 10 %» en Transformar | pendiente |
| 11 | AE2 | Emparentar solo está en clic derecho › Avanzado › «Seguir a (primario)»: en AE es una columna visible (con el látigo) en la línea de tiempo | pendiente |
| 12 | AE2 | Juego «After Effects»: Alt+Mayús+T (y P/S/R) no ponen clave de esa propiedad como en AE | pendiente |
| 13 | AE2 | [ , ] , Alt+[ , Alt+] no hicieron nada (teclado español: «[» va con AltGr; revisar qué tecla llega y aceptar la de la distribución) | revisar |
| 14 | AE2 | UU muestra Posición y Escala 100/100 del nulo como modificadas aunque no se tocaron | pendiente |
| — | AE2 | Bien: emparentar al nulo y girar con él, T muestra solo Opacidad (de las capas elegidas), Inicio, K/J entre claves, B/N zona de trabajo y la reproducción se para al final, copiar y pegar claves en dos capas («×2»), recuadro sobre dos pistas + F9 en las dos, arrastrar claves de dos pistas juntas, deshacer/rehacer | ok |
| 15 | AE3 | Velocidad del fotograma clave: con el cursor aún en el último campo, el primer clic en «Aplicar» solo confirma el campo; hace falta un segundo clic | pendiente |
| 16 | AE3 | Gráfico: Ctrl+rueda y Alt+rueda no acercaron valores ni tiempo (la rueda sola sí movió el tiempo). Revisar con el mouse de Jorge: puede ser que la herramienta de pruebas no mande el modificador con la rueda | revisar |
| — | AE3 | Sin probar: Ctrl sobre un tirador del trayecto (la herramienta no deja mantener Ctrl durante el arrastre) | — |
| — | AE3 | Bien: cuentas en los valores (resultado 860 de «(1920-200)/2»), trayecto en S de 4 claves, Auto-Orient, velocidad de varias claves en px/s del trayecto (el camino no cambia), gráfico a pantalla completa, «Ver toda la curva», recuadro de transformación que estira en el tiempo, deshacer | ok |
| 17 | AE4 | Comportamiento › Expresión: la ayuda solo nombra value, time, wiggle, Math y thisComp.layer; faltan index, thisLayer, linear, ease, easeIn/Out, clamp, valueAtTime, velocity, speed | pendiente |
| 18 | AE4 | El menú de la fila de Posición muestra «✓ Separar dimensiones» marcado aun antes de animar (y al animar se une sola): el estado que muestra confunde | pendiente |
| 19 | AE4 | El gráfico dibuja solo las claves: no muestra el resultado del comportamiento (Rebote, expresión, bucle); AE dibuja el valor final | mejora |
| — | AE4 | Bien: expresión con index y linear (la barra baja index×100 y 300 más en 2 s), punto verde de expresión válida, marca «≈» en la fila, «+800» relativo en un valor animado, Motion Tools › Rebote aplicado | ok |
| — | AE4 | Sin probar todavía: Curvas con claves de varias capas, Elástico, pegar en las cinco barras | — |
| 20 | AE5 | Escala de un texto: al escribir 150 la fila queda en «30,2 / 14,3 %» (ancho y alto distintos aunque unidos) y el texto no se ve más grande; la escala de los textos está rota (ver 10) | pendiente |
| 21 | AE5 | «Ver toda la curva» ajusta al largo del clip (17 s) y no a donde están las claves (en el primer segundo) | pendiente |
| 22 | AE5 | El gráfico bajo la pista del video sale muy bajo (unos 50 px): sin pantalla completa no se puede trabajar | pendiente |
| — | AE5 | Bien: S muestra solo Escala (también con dos capas), curvas de dos capas (la otra punteada con su etiqueta), clic en la clave de la otra capa pasa a editarla, Ctrl+clic suma claves de las dos capas y F9 las suaviza a la vez | ok |
| 23 | SUB1 | El progreso de los hablantes dice «Telling speakers apart…» en inglés (sin traducir) | pendiente |
| 24 | SUB1 | Justo después de traducir, la vista previa no mostraba ningún subtítulo en 0:02 hasta mover el cabezal | revisar |
| 25 | SUB1 | «Editar con el texto» vuelve a transcribir aunque el clip ya tiene subtítulos; debería usar esa transcripción y abrir al instante | pendiente |
| 26 | SUB1 | (Jorge) «Editar con el texto» tarda ~30 s sin aviso visible de carga (solo un aviso chico abajo que se va); el usuario puede pensar que no sirve: abrir la ventana al tiro con «Escuchando… %» y Cancelar | pendiente |
| — | SUB1 | Bien: Hablante 1/2 con colores, palabras clave marcadas, Traducir dice «English», el inglés arriba sin encimarse con el español, Editar con el texto tacha y corta 0,7 s y los dos clips de subtítulos se acortan con el video | ok |
| — | SUB1 | Sin probar: exportar MP4 con la pista de subtítulos y el .srt/.vtt (ffprobe) | — |
| 27 | SUB2 | En la franja de subtítulos de la línea de tiempo el texto de un bloque se sale de su caja («a editar videos de» queda afuera) | pendiente |
| 28 | SUB2 | Las miniaturas de los estilos «Subtítulo» y «Leyenda» casi no se ven (texto diminuto) | pendiente |
| 29 | SUB2 | Elegir un estilo (Fondo de frase) con el clip de subtítulos elegido no cambia los subtítulos que ya están: la vista previa sigue con el estilo anterior | pendiente |
| 30 | SUB3 | **Sin sesión el panel Traducir dice «Inicia sesión con Google…» y deja el botón apagado: la traducción en la computadora no se puede usar desde la pantalla.** Encender el botón si está el extra «Traducción sin internet» (y decir que traduce en el equipo) | pendiente |
| — | SUB2 | Bien: Dos líneas, emojis (🎬 en dos frases), ocultar groserías, una sola voz sin etiquetas de hablante, la galería de 33 estilos | ok |
| — | SUB3 | Bien: subtítulos creados en el equipo sin sesión (5), «Continuar sin cuenta» | ok |
| — | SUB2/3 | Sin probar: pitido, quitar silencios con otras pistas, estilo por subtítulo, importar .srt, karaoke, exportar con subtítulos (siguen en la próxima ronda, con la compilación nueva) | — |
| — | — | (E31 quitado: la bienvenida «Esperando al navegador» fue Jorge iniciando sesión) | — |

## Estado (2026-11-03, tarde) — para seguir
- Ronda 1 hecha (lista de arriba). Arreglos en `f1f6b` y `8fb52` (rama `flip/subtitulos`): 1, 3, 4, 5, 7, 8, 9/2 (ScrubValue
  que re-elegía su clip al perder el foco; si vuelve: revisar herramienta de la línea de tiempo activa o el 1.er clic tras Pro),
  10, 12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 26, 27, 29, 30. Pendientes para la ronda 2: 6 (Tab ancho→alto), 11 (látigo de
  emparentar ya existe pero solo con el clip elegido: hacerlo visible), 13 ([ ] con teclado español), 19 (gráfico con el
  resultado de comportamientos), 24, 25 (Editar con el texto reusando los subtítulos), 28 (miniaturas de estilos).
- Compilación con todo junto (voz nueva + arreglos): run 41685086924. Al salir: bajar `windows-portable` a
  `E:\FlipStudio\pruebas\FlipStudio-0.30-r2`, rehacer los proyectos con `proyectos-030\make-*.jsonl` (mcp_e2e.py), copia del
  registro, AE con el mouse de Jorge (avisarle), subtítulos sin mouse (`proyectos-030\cs.ps1 -P <pid> -Steps "c:x,y; w:ms"`),
  SUB3 sin sesión: exportar `account` antes, borrarla, «Continuar sin cuenta», restaurar al final con la exportada.
- Probar también la voz (docs/plan-voz.md): tomas, frases, [pausa 1s], velocidad/tono, diálogo, editar guion, leer título,
  diseño nuevo, menú cruzado Subtítulos/Voz.

## Ronda 2 (2026-11-03, compilación 41690321814, portable `pruebas\FlipStudio-0.30-r2`)
Compilación: la primera (41685086924) falló porque las pruebas compilan `TtsController.cpp` sin SoundTouch (`4e888`), la
segunda por dos `onClosing` en `TextEditWindow.qml` (qmlcachegen; ahora se revisan todos los QML cambiados en local con
`qmlcachegen --only-bytecode --resource-path /x/<archivo>`). La tercera (41690321814) salió bien.

| # | Proyecto | Qué pasó | Estado |
|---|---|---|---|
| — | AE1 | Bien: 1 (formas centradas), 3 (una fila «Posición X Y» al animar), 4 (rueda sobre las filas), 5 (el ancho dice 130), 14 (UU), 15 (Aplicar al primer clic), 18 (menú sin «✓ Separar»), separar/unir | ok |
| 2 | AE1 | Sigue: el primer clic tras pasar a Pro no elige el clip | revisar |
| 6 | AE1 | Sigue: Tab desde el ancho iba a la cadena (sin campo), el foco se perdía y lo tecleado iba a la app (Ctrl+A eligió todo) | arreglado (salta la cadena) |
| 7 | AE1 | Sigue: con el cronómetro y 130 escrito en el mismo instante queda una sola clave y la forma crecía desde su esquina (X 960 → 1038). Ahora el tamaño guarda su punto de partida al poner el cronómetro (`Clip::sizePivotW/H`) y crece alrededor del anclaje; prueba `keyedSizeGrowsAroundAnchorFromItsPivot` | arreglado |
| 11 | AE1 | El látigo de emparentar ahora está en todas las capas en Pro (tenue hasta pasar el puntero) | arreglado |
| 13 | AE1 | Sigue: «[» con teclado español llega como Ctrl+Alt+[ (AltGr). Filtro `AltGrShortcutFilter` en `main.cpp` (fuera de campos de texto) | arreglado |
| 16 | AE1 | La herramienta de pruebas no mantiene Ctrl/Alt con la rueda (tampoco hace zoom en la línea de tiempo): **lo prueba Jorge con su mouse** | Jorge |
| 19 | AE1 | Elástico se aplica (≈ en la fila) pero el gráfico sigue sin dibujar el resultado del comportamiento | mejora |
| 10 | AE2 | Sigue en el inspector Transformar («Escala 10 %» de un texto nuevo): ahora cuenta desde el tamaño propio | arreglado |
| — | AE2 | Bien: 12 (Alt+Mayús+P con el juego After Effects pone claves de Posición y muestra solo esa fila) | ok |
| 32 | Voz | La primera frase se cortaba en la coma («Hola a todos, bienvenidos al canal.» → «Hola a todos», Jorge lo oyó). Reintenta con otra redacción y otras lecturas si la frase sale muy corta (< 22 letras por segundo) | arreglado |
| 33 | Voz | ↻ (rehacer frase) y «Generar de nuevo» daban el mismo audio (la voz elige siempre lo más probable): ahora cada vez es otra lectura (`variant`) | arreglado |
| 34 | Voz | Los subtítulos de una voz se sacaban escuchándola («¡Toy vamos…») en vez del guion: ahora salen del guion con los tiempos de cada frase | arreglado |
| 35 | Voz | Reemplazar la voz dejaba sus subtítulos viejos (dos pistas de subtítulos): ahora se cambian | arreglado |
| 36 | Voz | El clip y el medio se llamaban «tts-chatterbox-…flac»: ahora «Voz: Hola a todos, bienvenidos…» | arreglado |
| 37 | Voz | Opciones: los tres deslizadores no decían qué eran (Velocidad, Tono, Expresividad) ni su valor | arreglado |
| — | Voz | Bien: Voz y Subtítulos juntos en Audio, diseño nuevo, «Cargando el modelo…», progreso por frase con Cancelar, [pausa 1s] (1,18 s de silencio), velocidad 1,25×, Editar guion desde Audio (aviso de reemplazo), Reemplazar, diálogo Ana/Luis (una voz por persona, sin decir los nombres) | ok |
| 38 | Voz | Solo hay una voz («Predeterminada»): un diálogo suena igual para todos. Es el punto 1 de `docs/plan-voz.md` (paquete de voces) | pendiente |
| — | — | Sin probar todavía: Curvas con varias capas, pegar en las cinco barras, exportar la zona de trabajo, Ctrl en un tirador del trayecto; subtítulos: pitido, quitar silencios, estilo por subtítulo, .srt, karaoke, exportar con subtítulos, SUB3 sin sesión con la traducción en el equipo; voz: leer un título, importar guion, guardar la voz, bajar la música | — |

### Ronda 2b (compilación 41706768086, portable `pruebas\FlipStudio-0.30-r3`, con el mouse de Jorge)
- 7 bien: con el cronómetro y 130 la elipse crece alrededor de su centro. 11: el látigo está en todas las capas pero
  casi no se veía (ahora más opaco y más grande).
- 6 seguía: la fila se reconstruye dos veces al confirmar y la primera, destruida al instante, se llevaba la edición
  pendiente («root is not defined», «format is not a function»). Ahora se da por hecha solo cuando una fila viva abrió el campo.
- 13: el teclado de Jorge es Español (Latinoamérica): «[» va con Mayús, no con AltGr. El filtro ahora mira el carácter
  escrito (Mayús y AltGr no cuentan; Alt sí, para Alt+[).
- 2 explicado: el primer paso a Pro abre «¿Usar los atajos de After Effects?», que se cierra con el clic de afuera; las
  pruebas restauran el registro y la pregunta vuelve cada vez. No es un fallo.
