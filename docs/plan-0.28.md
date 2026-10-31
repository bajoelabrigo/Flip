# Plan 0.28 — Formas como After Effects (varias formas dentro de una capa)

Pedido de Jorge (2026-10-30, con capturas de AE): una capa de forma con **Contenido** — varias formas, cada una con su
trazado, relleno, trazo y transformación, que se animan y editan por separado. Solo en **modo Pro**. «Las formas las
trabajamos en la línea de tiempo y en la columna de la derecha: planifica bien para que no se vuelva un enredo y el
usuario entienda fácil cómo funciona.» Análisis técnico: `docs/plan-formas-ae.md`. Rama: `flip/v0.28`.

Si otro asistente sigue: `[x]` hecho, `[~]` a medias, `[ ]` falta.

## Cómo se usa (lo primero: que se entienda)

**Regla de Jorge (dicha dos veces):** tiene que sentirse fácil **para el que es nuevo y para el que viene de After
Effects**. Cada etapa se revisa con los dos en mente antes de mostrarla: el nuevo entiende la columna derecha sin
saber AE (nombres claros, ayudas cortas, nada escondido en menús raros); el de AE encuentra en la línea de tiempo lo
mismo que conoce (orden, nombres, cronómetros, atajos).

### Tres ideas, nada más
1. **Una capa de forma tiene partes.** Cada parte («Rectángulo 1», «Elipse 1»…) es una figura con su relleno, su borde
   y su propia posición/giro/escala. La capa entera tiene además su Transformar de siempre (mueve todas las partes).
2. **Una sola selección para todo.** Elegir una parte en la línea de tiempo, en la columna de la derecha o con doble
   clic en la vista previa es lo mismo: las tres zonas marcan la misma parte. Nunca hay dos selecciones distintas.
3. **Cada zona tiene su trabajo.**
   - **Línea de tiempo = el tiempo**: qué se anima y cuándo (cronómetros, rombos, curvas). Muestra solo lo animable.
   - **Columna derecha = el aspecto**: colores, tamaños, bordes, con controles cómodos (selector de color, deslizadores),
     de la parte elegida. Cada valor tiene su cronómetro también, para animar sin bajar a la línea de tiempo.
   - **Vista previa = la mano**: mover, escalar, girar la parte elegida y dibujar partes nuevas.

### Columna derecha (pestaña Forma, en Pro)
```
┌ Forma ─────────────────────────────────┐
│ Contenido                    [+ Añadir]│   ← lista tipo «capas» de Photoshop
│  👁 ▸ ▭ Rectángulo 2                   │     ojo · flecha para abrir un grupo ·
│  👁 ▾ ◯ Elipse 1                 ●     │     icono del tipo · nombre (doble clic
│  👁     ▭ Rectángulo 1               │     = renombrar) · arrastrar = reordenar
│  ───────────────────────────────────── │
│ ◯ Elipse 1  (la parte elegida)         │
│  ▾ Forma      Tamaño ⏱ 220 × 220  🔗   │   ← secciones con nombres claros;
│               Posición ⏱ 0, 0          │     el nombre de AE en la ayuda (?)
│  ▾ Relleno    Color ⏱ ■  Opacidad ⏱    │
│  ▾ Borde      Color ⏱ ■  Ancho ⏱ 4     │
│               Extremos, guiones, …     │   ← lo avanzado plegado
│  ▾ Posición y giro de la parte         │
│               Posición, Escala, Giro,  │
│               Inclinación, Opacidad ⏱  │
│  ▸ Efectos de trazado (0)  [+]         │   ← recortar, repetidor, ondular…
└────────────────────────────────────────┘
```
- Arriba siempre la lista **Contenido**; abajo, solo la parte elegida. Sin parte elegida (o clic en el nombre de la
  capa), abajo se ve **la capa entera** como hoy: así lo que ya existe sigue en el mismo sitio.
- **«+ Añadir»** con tres grupos y en este orden: **Formas** (Rectángulo, Elipse, Estrella, Polígono, Trazado con la
  pluma), **Pintura** (Relleno, Borde, Relleno degradado, Borde degradado), **Efectos de trazado** (Recortar trazados,
  Repetidor, Redondear esquinas, Ondular, Zigzag, Torcer, Fruncir e inflar, Desplazar, Fusionar trazados,
  Transformación ondulada). Y **Grupo vacío**. Una forma nueva llega ya con Relleno y Borde (como AE).
- Lo que se añade va **dentro de la parte elegida** si es un grupo, o **encima** de ella si no: siempre se ve dónde cayó
  (queda elegido y resaltado).
- Clic derecho en la lista: Duplicar (Ctrl+D), Agrupar (Ctrl+G), Desagrupar, Renombrar, Eliminar (Supr), Mostrar/ocultar.

### Línea de tiempo (en Pro)
```
▾ Gráfico 1  ★ Capa de forma 1
   ▾ Contenido                                    Añadir ▸
      ▸ 👁 Rectángulo 2                       Normal ▾
      ▾ 👁 Elipse 1                           Normal ▾
           ▸ Trazado de elipse 1
           ▸ Relleno 1
           ▸ Trazo 1
           ▸ Transformar: Elipse 1
      ▸ 👁 Rectángulo 1                       Normal ▾
   ▸ Transformar                                  (las filas de la 0.25)
```
- Igual a AE en orden y nombres (Contenido, Trazado de rectángulo, Relleno, Trazo, Transformar: …), porque quien usa
  Pro viene de AE. Cada propiedad con cronómetro, ◀◆▶ y valor azul arrastrable, como las filas de la 0.25.
- **Plegado por defecto.** Al elegir una parte en la columna derecha o en la vista previa, la línea de tiempo abre y
  muestra esa parte (y no más).
- **U** muestra solo lo animado de todas las partes (como ya hace con la capa). Mayús+clic en un cronómetro, como hoy.
- Arrastrar una parte arriba/abajo en estas filas reordena igual que en la lista de la derecha (es la misma lista).

### Vista previa
- Clic: elige la capa (como hoy). **Doble clic sobre una parte: entra y la elige** (recuadro con tiradores de esa parte:
  mover, escalar, girar = su Transformar). Otro doble clic entra en un grupo dentro de otro. **Esc** sale un nivel.
- Arriba de la vista previa, una **migas de pan** mientras se está dentro: «Capa de forma 1 › Elipse 1». Clic en
  «Capa de forma 1» vuelve a la capa.
- Rectángulo/elipse elegidos: además de los tiradores de la parte, un punto para la **redondez** (como hoy).
- **Dibujar dentro:** con una capa de forma elegida, la herramienta de rectángulo/elipse/estrella/pluma añade una parte
  nueva a esa capa (como AE) y avisa: «Añadido a Capa de forma 1 · Hacer capa nueva». Sin capa elegida, capa nueva.
- **Combinar en una capa** (clic derecho con varias formas elegidas en la línea de tiempo) y **Separar en capas**.

### Modo Simple
- Nada de esto se ve: una forma es una figura, con el inspector de hoy. Si la forma tiene varias partes, la columna dice
  «Esta forma tiene varias partes · Ver en Pro» y lo que se cambie en Simple (color, por ejemplo) va a todas.

## Qué pasa con lo que ya existe
- Una forma de antes se lee como **una capa con una parte** que tiene todo lo de antes (figura, rellenos, bordes,
  sombras, efectos de trazado) y **se ve idéntica** (prueba de píxeles con plantillas de Stock y del Kit de YouTube).
- «Formas en esta capa» (0.26: contornos dentro de un trazado + Fusionar) se reemplaza por la lista Contenido; las formas
  hechas así siguen como un trazado con varios contornos.
- Sombras, brillo y extrusión de la forma: quedan en la parte (como hoy); los estilos de capa de la 0.26 siguen en la capa.

## Datos y dibujo (resumen; detalle en `docs/plan-formas-ae.md`)
- `core/ShapeContents.h`: árbol de elementos (grupo, trazado rectángulo/elipse/estrella/libre, relleno, borde,
  operadores) en `ShapeStyle::contents`; vacío = forma de antes. Ids estables por elemento; claves
  `contents.<id>.<campo>`. Proyecto versión 16; se guarda además el contorno aplanado para apps viejas.
- `SkiaShapePainter` recorre el árbol con el orden de AE (una pintura pinta los trazados de arriba en su grupo; un
  operador cambia los de arriba; las matrices de grupo se acumulan).
- `AppController`: elegir elemento (`selectedShapeItem`), añadir/borrar/duplicar/agrupar/reordenar/renombrar,
  valores y claves por elemento, filas de la línea de tiempo en árbol. Todo con un paso de deshacer por acción.
- MCP: `list_shape_items`, `add_shape_item`, `set_shape_item`, `group_shape_items`.

## Etapas (cada una se prueba en ventana antes de seguir)
1. [x] Datos + dibujo + compatibilidad (build 41122983222: tst_skia 135 pasan, 0 fallan; las 3 pruebas nuevas en verde;
   con la app real sin ventana, un proyecto con rectángulo, elipse y un grupo girado/inclinado al 60 % en Trama se
   dibuja en el orden y lugar correctos).
   **Decisión de diseño:** cada parte es una **figura completa** (su contorno, sus rellenos y bordes, sus efectos de
   trazado y sus claves: la misma `ShapeStyle` de siempre) con su Transformar de grupo; los grupos contienen partes.
   No hay rellenos o trazos «sueltos» que pinten varias figuras como en AE: eso se hace con una parte de varios
   contornos (la pluma) o con Fusionar trazados. Así cada parte se dibuja con el pintor de siempre (idéntica) y la lista
   es fácil de entender; la línea de tiempo igual la muestra como AE (Trazado, Relleno, Trazo, Transformar).
   `ShapeStyle::parts` (arriba la primera), `partsRefWidth/Height` (la caja de referencia que estira la capa),
   `ShapePart` (id, nombre, visible, fusión, grupo/hijos, tamaño, `shape`, `transform`, claves propias),
   `shapeWithParts()` (forma de antes → capa de una parte, mismos píxeles), `ContentsPainter` en `SkiaShapePainter`.
   Pruebas en `tst_skia`: una parte = mismos píxeles (5 variantes), orden/posición/opacidad/grupo girado/oculta,
   JSON y claves por parte. Versión de proyecto 16.
   Original de la etapa: Pruebas: orden de pintura de AE, grupos anidados, claves por elemento, proyecto
   viejo idéntico píxel a píxel, ida y vuelta del JSON.
2. [x] Columna derecha: lista Contenido, «+ Añadir», parte elegida con sus secciones, menú de clic derecho.
   **Probado en ventana (build 41130586723):** lista con grupo abierto, elegir una parte, mover solo esa parte, deshacer,
   «+ Añadir» (menú bajo el botón, numeración «Estrella 2»), cambiar las puntas solo en esa estrella, ojo, clic derecho y
   Agrupar, convertir una forma sencilla (no se mueve) y Simple con «Ver en Pro». Pendiente menor: en Simple, poder
   cambiar el color de todas las partes; «Trazo» de la pila de capas sigue llamándose así (la opción A pide «Borde» en
   la columna derecha: cambiarlo con cuidado porque la misma fila sirve al texto).
   Hecho: `ShapeContentsList.qml` (capa arriba, partes con ojo, color, nombre; grupos que se
   pliegan; doble clic renombra; clic derecho: Cambiar nombre, Duplicar Ctrl+D, Agrupar Ctrl+G, Desagrupar Ctrl+Mayús+G,
   Mostrar/Ocultar, Eliminar Supr; arrastrar reordena, con línea antes/después o recuadro «dentro» de un grupo).
   `ShapeInspector`: la lista solo en Pro; con una parte elegida, las secciones de siempre editan **esa parte** (el
   clip redirige `shape.<clave>`, la pila de rellenos/bordes y `setShapeStyle` a la parte: `shapeStyleOf()` en
   AppController); «Posición y giro de la parte/del grupo» con Ancho/Alto, Posición, Escala, Rotación, Opacidad, Modo
   de fusión e «Inclinación y punto de anclaje», todo con cronómetro (`part.<id>.<campo>`). Capa de partes sin parte
   elegida: un aviso que lleva a elegir una parte o a Transformar. En Simple: «Esta forma tiene varias partes · Ver en
   Pro». La sección Trazado (pluma) se esconde en capas de partes hasta la etapa 4. La primera parte añadida convierte
   la forma (lo que dibujaba pasa a «<forma> 1» sin moverse). No se puede borrar la última forma de la capa.
3. [x] Línea de tiempo: filas en árbol, Añadir ▸, ojos y fusión, cronómetros; selección compartida con la columna.
   **Probado en ventana (build 41142087360):** Contenido se abre y muestra Rectángulo 1 / Grupo 1 (carpeta, «Trama») /
   Elipse 1 con ojo y fusión; elegir una parte la resalta y la abre (Trazado, Trazo 1, Relleno 1, Transformar); Relleno
   con la fila Color (cuadrito) y Opacidad; el ojo oculta la parte en la vista previa y se deshace; el cronómetro de
   Ancho pone la primera clave; «Añadir ▸» abre su menú. **Trampa de compilación:** MSVC 19.4x se cerraba (0xC0000005,
   sin mensaje) con la primera versión, una lambda recursiva en `std::function` que llamaba a cinco lambdas locales:
   ahora es la estructura `ShapeContentRowsBuilder` con métodos normales. Pendiente menor: Opacidad del relleno se ve
   «1.00» y no «100 %»; la flecha de la pista no se abrió con clics simulados (las filas sí): que Jorge la pruebe.
   Hecho: `AppController::shapeContentRows` (solo en Pro y en capas de partes, para el clip
   que miran las filas): «Contenido» con «Añadir ▸», cada parte con su ojo, su modo de fusión ▾ y menú de clic derecho;
   dentro, «Trazado: <forma>» (Ancho, Alto, Redondez o Puntas/Radio interior), «Relleno N»/«Trazo N» (con ojo;
   Opacidad, Ancho del trazo) y «Transformar: <parte>» (anclaje, posición, escala, inclinación y su eje, rotación,
   opacidad); los grupos con sus partes. Después, «Transformar» de la capa con sus filas de siempre. Todo plegado;
   elegir una parte (columna, línea de tiempo o vista previa) abre Contenido y esa parte. U deja solo lo animado.
   Los encabezados se dibujan encima de la fila de valor en `TrackHeaderColumn` (capa `headingLine`). Las claves
   `part.*` ya no salen repetidas entre «otras propiedades animadas». «Color» de cada relleno/trazo: una fila que une
   sus cuatro canales (como Posición une X e Y), con un cuadrito que abre el selector y escribe los cuatro en un paso.
4. [x] Vista previa: entrar con doble clic, migas de pan, tiradores de la parte, dibujar dentro, combinar/separar.
   **Probado en ventana (build 41149757033):** doble clic entra (migas «Capa de forma › Grupo 1»), dibujar con la capa
   elegida añade «Rectángulo 2» con su aviso, esquina escala desde el anclaje, el redondo gira, Separar (2 capas iguales)
   y Combinar (una capa, se ve igual), proyecto nuevo sin «Video 1». Arreglado después (siguiente build): la capa crece
   para abarcar lo dibujado fuera de su caja (si no, un clic ahí la soltaba), Separar ajusta la caja de cada capa a su
   parte, la zona para arrastrar sigue a la parte, las migas siguen a la selección; y en el motor, formas y fotos ya no
   tiemblan al crecer (caja exacta; fotos decodificadas en pasos de 256 px).
   Hecho: `ShapePartOverlay.qml` dentro de la caja de la capa elegida (Pro, 2D):
   contorno de la parte elegida, sus tiradores (arrastrar dentro = mover; esquinas = escalar por sus ejes, Mayús igual en
   los dos; el redondo = girar, Mayús de 15 en 15°) y la parte bajo el puntero punteada. Doble clic entra (la capa →
   sus partes; un grupo → las suyas), clic al lado elige la vecina o vuelve a la capa, **Esc** sube un nivel (y en la
   capa la suelta). Migas «Capa › Grupo › Parte» arriba a la izquierda de la vista previa. `AppController::
   shapePartFrames` (esquinas de cada parte en fracciones de la caja, su anclaje y el mapa del padre) y
   `shapePartCrumbs`. **Dibujar dentro:** en Pro, con una capa de forma elegida y a la vista, la herramienta de formas
   añade una parte donde se dibujó (`addDrawnShapeToLayer`) y avisa «se añadió a … · pulsa Esc antes»; Esc con la
   herramienta suelta la capa. **Combinar en una capa de forma** (clic derecho con varias formas, Pro;
   `combineSelectedShapes`: cada una queda donde estaba, una capa de partes del tamaño de todas; solo formas quietas sin
   máscaras ni efectos) y **Separar en capas** (`separateShapeParts`: cada parte en su capa encima, se ve igual).
   Prueba `shapeLayerCombineSeparateAndFrames`. En el paso: un proyecto nuevo ya no deja «Video 1» vacío bajo la
   primera forma (`ensureFreeTrackForClipType`, prueba `firstShapeTakesTheEmptyStartingTrack`), y la opacidad del
   relleno se lee «100 %». **Pluma dentro:** en Pro, con una capa de forma elegida, el trazo de la pluma se dibuja
   como siempre y al terminarlo pasa a esa capa como «Trazado N» donde se dibujó (`m_penTargetLayerId`,
   `moveShapeClipIntoLayer`, en el mismo paso de deshacer); el primer Esc con la pluma suelta la capa, el segundo deja
   la pluma. Una capa de partes ya no se trata como trazado libre (`shapePathState`).
5. [~] Borde completo (Taper, Wave, guiones, inglete), degradados, Redondear esquinas, Transformación ondulada,
   estrella con redondez; MCP, expresiones `content("…")`, traducciones, notas.
   Hecho (falta compilar y probar en ventana): **Afinar y ondular** en el borde de las formas (`TextShadingLayer`:
   taperStart/EndLength, taperStart/EndWidth, taperEase, waveAmount/Length/Phase, todos animables; se dibuja como
   contorno de ancho variable, `profiledStroke` en `SkiaShapePainter`), **límite de inglete**, y en el inspector
   (`ShadingLayerRow`, solo formas) «Afinar y ondular» con **Extremos** (planos/redondeados/cuadrados) y **Esquinas** (en
   punta/redondeadas/biseladas), que no tenían control. **Redondez exterior/interior** en estrellas y polígonos
   regulares (`radialPath`: a 100 % un polígono es un círculo; animables; filas en Contenido). **Transformación
   ondulada** de una parte (posición, rotación, escala, temblores por segundo, semilla; ruido suave determinista, así la
   exportación es igual a la vista previa). **MCP** `list_shape_parts`, `add_shape_part`, `set_shape_part`,
   `group_shape_part` (docs/MCP.md, prueba `shapePartsThroughMcp`). Prueba `strokeTaperWaveAndRoundness`. Guiones,
   degradados y redondear esquinas ya existían. Además, en el motor: el «barrido» de un texto con caja barría solo las
   letras y dejaba sin margen derecho la caja (ahora barre la caja entera). **Expresiones:** `layer("Capa").content("Grupo 1").content("Elipse 1").transform.rotation` (y `.size`), prueba en `expressionsRunOnProperties`. **Trampa:** cambiar la firma de una función declarada en un `.h` solo en el `.cpp` compila pero falla al enlazar (`regularPolygonPath`, las máscaras la usan): buscar en los encabezados.

## Decisiones (Jorge)
- [x] Nombres (Jorge, 2026-10-30: opción A): columna derecha con nombres claros (Forma, Relleno, **Borde**, **Posición y
      giro de la parte**, Efectos de trazado) y el nombre de AE en la ayuda (?); línea de tiempo con los de AE
      (Trazado de elipse, Relleno, Trazo, Transformar: Elipse 1).
- [x] Dibujar con una capa de forma elegida: **se suma a esa capa** (como AE), con el aviso «Añadido a … · Hacer capa
      nueva» (Jorge, 2026-10-30).

## Publicación (Jorge, 2026-10-30)
La 0.27.0 **no se subió** a la Store: no hay 0.27.1. El arreglo del espacio de trabajo «Vertical» (`WorkspaceView.qml`,
`captured` se borra al cambiar de árbol) va en la 0.28, y las notas de la Store de la 0.28 son **combinadas 0.27 + 0.28**.

**Espacio de trabajo (probado, build 41142087360):** Video › 1080×1920 (9:16) cambia al espacio vertical al momento,
sin reiniciar.
