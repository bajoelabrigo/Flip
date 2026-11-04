# Cursos de After Effects: nulos y formas/pluma (2026-11-04)

Pedido de Jorge: comprobar que todo lo que muestran los dos videos (`Downloads\trabajar con nulos.txt`,
`Downloads\curso de formas.txt` y los `.mkv` de `Videos\aTubeCatcher`) se pueda hacer en Flip, añadir lo que falte
y probarlo **en ventana sin el mouse**. Igual que `docs/tutorial-keyframes-ae.md`. Archivos de prueba en
`E:\FlipStudio\pruebas\cursos-nf`. También: abrir archivos de Illustrator (`.ai`).

Leyenda: ✅ hecho y visto en ventana · 🔧 añadido, falta verlo en ventana · ≈ se hace de otra forma en Flip.

## Illustrator

| Del curso | En Flip |
|---|---|
| Importar un `.ai` | 🔧 `.ai` con PDF dentro (todo `.ai` desde CS) entra como PDF (extra Visor de PDF). `AssetLibrary::isPdfPath` |

## Nulos y conectar propiedades

| Del curso | En Flip |
|---|---|
| Capa › Nuevo › Objeto nulo; mover/escalar/girar varias capas con él | ✅ ya existía (nulo + Emparentar) |
| El nulo se ve como un cuadrado con contorno | 🔧 `TransformOverlay` dibuja el cuadrado de los nulos |
| Látigo (pick whip) a otra capa; la opacidad no se hereda | ✅ ya existía |
| Nulos encadenados (meteoro que gira con `time*180` alrededor de un planeta) | ✅ ya existía (emparentar en cadena + expresión) |
| Columna «Primario» | ≈ menú Emparentar de la cabecera y el látigo |
| Controles de expresión: Deslizador, Punto, Ángulo, Color, Casilla | 🔧 efectos `ae.*_control` (Efectos › Controles de expresión) |
| Látigo de una propiedad a un efecto (`effect("Slider Control")("Slider")`) | 🔧 `effectExpressionPath`, `ExpressionEngine` (`effect()` en el preludio) |
| Renombrar un efecto y que la expresión lo encuentre por ese nombre | 🔧 Efectos › clic derecho › Renombrar… (`Effect::label`) |
| Interruptor «Habilitar expresión» (=/≠) | 🔧 «Expresión activa» en el diálogo (`TrackBehavior::expressionEnabled`) |
| Alt+clic en el cronómetro: crear/quitar expresión | 🔧 `TrackHeaderColumn` |
| Nombre de la propiedad en rojo con expresión | 🔧 |
| Buscar propiedades («color») en la línea de tiempo | 🔧 campo «Buscar propiedades» (`keyframeRowsSearch`) |
| Tecla E: los efectos con todos sus parámetros | 🔧 la fila de efectos lista también los no animados |

## Formas y pluma

| Del curso | En Flip |
|---|---|
| Rectángulo, rectángulo redondeado, elipse, polígono, estrella | 🔧 «Rectángulo redondeado» nuevo; polígono con número de lados (`polygonFromPoints`) |
| Alt+clic en la herramienta: la forma siguiente | 🔧 `PreviewToolbar` `cycleKind` |
| Doble clic en la herramienta: una forma del tamaño del cuadro | 🔧 |
| Polígono/estrella: rueda mientras se arrastra = puntos; girar con el puntero; Mayús = derecho | 🔧 `PreviewToolOverlay` (`polystarTool`) |
| Ctrl al dibujar: desde el centro | ✅ ya existía |
| Alt+clic en Relleno/Trazo: ninguno → sólido → lineal → radial | 🔧 `FillOptionsDialog.cycle` |
| Modo máscara de la herramienta (con una capa elegida) | 🔧 botón junto a la herramienta (`shapeToolMask`) |
| Trazo discontinuo con Guion/Espacio en px y varios pares | 🔧 «Guion y espacio (px)» con + y − (`dashPattern`) |
| Recortar trazados, transformar grupo (con sesgo), Ctrl+G, alinear | ✅ ya existían |
| Pluma: menú del trazado: Fijar primer vértice, RotoBezier, Cerrado | 🔧 clic derecho en el trazado (`PenToolOverlay`) |
| Ctrl+T: transformar puntos libremente | 🔧 diálogo con escala X/Y y ángulo |
| Crear formas desde texto (una por letra) | 🔧 clic derecho en el texto y Motion Tools |
| Crear formas desde capa vectorial (SVG/AI) | 🔧 clic derecho en la capa SVG |
| Combinar trazados (sumar, restar, intersecar, excluir: la luna) | 🔧 Contenido › Añadir › Combinar trazados |
| Espacio + arrastrar para mover la vista | ≈ Espacio reproduce en Flip; la vista se mueve con el botón del medio |
| Trazo fuera del grupo al escalar | ≈ cambiar Tamaño en vez de Escala |
| Afinar (taper) con suavizados separados | ≈ Afinar con un solo suavizado |
| Quitar una parada de degradado arrastrándola hacia abajo | ≈ clic derecho en la parada |

## Prueba en ventana

(se completa con la compilación que lleva todo)
