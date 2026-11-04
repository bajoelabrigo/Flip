# Cursos de After Effects: nulos y formas/pluma (2026-11-04)

Pedido de Jorge: comprobar que todo lo que muestran los dos videos (`Downloads\trabajar con nulos.txt`,
`Downloads\curso de formas.txt` y los `.mkv` de `Videos\aTubeCatcher`) se pueda hacer en Flip, añadir lo que falte
y probarlo **en ventana sin el mouse**. Igual que `docs/tutorial-keyframes-ae.md`. Archivos de prueba en
`E:\FlipStudio\pruebas\cursos-nf` (`logo-prueba.ai`, `formas.svg`, `wheeldrag.py` = arrastrar girando la rueda).
También: abrir archivos de Illustrator (`.ai`).

Leyenda: ✅ visto en ventana · 🔁 arreglado tras la primera ronda, falta volver a verlo · ≈ se hace de otra forma.

Rondas: **r1** = build 41853361934 (portable `pruebas\FlipStudio-0.30-nf1`); **r2** = build 41863501207.

## Illustrator

| Del curso | En Flip |
|---|---|
| Importar un `.ai` | ✅ r1: entra como PDF (extra Visor de PDF) con su miniatura. `AssetLibrary::isPdfPath` |

## Nulos y conectar propiedades

| Del curso | En Flip |
|---|---|
| Nuevo › Objeto nulo; mover/girar varias capas con él | ✅ r1 (nulo + Emparentar; giran alrededor del nulo) |
| El nulo se ve como un cuadrado con contorno | ✅ r1 (`TransformOverlay`) |
| Látigo a otra capa; la opacidad no se hereda | ✅ ya existía |
| Meteoro con `time*180` | ✅ r1: escrita a mano en el diálogo, 90° en 0,5 s |
| Columna «Primario» | ≈ menú Emparentar de la cabecera y el látigo |
| Controles de expresión (Deslizador, Punto, Ángulo, Color, Casilla) | ✅ r1, en Efectos › Controles de expresión, nombres en español |
| Tecla E: todos los parámetros de los efectos | ✅ r1; 🔁 los valores salían en 0 y el color como número (ahora valor por defecto y muestra de color) |
| Ver los controles al desplegar la capa, sin claves | 🔁 (antes solo con E o con claves) |
| Látigo de una propiedad a un efecto | ✅ r1: escribe `thisComp.layer("Nulo 1").effect("Control deslizante")("Deslizador")` |
| Escala enlazada a un deslizador en % | 🔁 la expresión daba píxeles (50 → 9,6 %); ahora lee y da % |
| Renombrar un efecto | ✅ r1 (panel y franja); 🔁 la fila y las expresiones que lo usan |
| «Habilitar expresión» | ✅ r1 («Expresión activa»: apagada vuelve al valor propio) |
| Alt+clic en el cronómetro: crear/quitar | ✅ r1 crear; 🔁 quitar una apagada (abría el diálogo) |
| Nombre en rojo con expresión | ✅ r1 |
| Buscar propiedades («color») | ✅ r1 filtra; 🔁 el Control de color no salía por no tener claves |

## Formas y pluma

| Del curso | En Flip |
|---|---|
| Alt+clic en la herramienta: la forma siguiente | ✅ r1 (rect → redondeado → elipse → polígono → estrella); 🔁 ícono propio del redondeado |
| Doble clic en la herramienta: forma del tamaño del cuadro | 🔁 llegaban dos clics sueltos y abría el menú; ahora se mide el tiempo entre clics |
| Polígono/estrella: rueda = puntos, gira con el puntero | ✅ r1 (8 lados); 🔁 se dibujaba un cuadrado al arrastrar, ahora el polígono; el desplegable decía «Hexágono» |
| Alt+clic en Relleno/Trazo | ✅ r1 (sólido → lineal → radial → ninguno, sobre la forma elegida) |
| Modo máscara de la herramienta | ✅ r1 crea la máscara; 🔁 quedaba con el tamaño por defecto |
| Máscara en una capa emparentada a un nulo que gira | 🔁 el recuadro de la máscara no seguía al padre; en formas con trazo la máscara se medía sobre el borde ampliado |
| Guion/Espacio en px, varios pares | ✅ r1 (Guion 1, Espacio 1, Guion 2… con + y −) |
| Recortar trazados, transformar grupo, Ctrl+G, alinear | ✅ ya existían |
| Pluma sobre una capa de formas elegida: añade un trazado | ✅ r1 («Trazado 1», «Trazado 2» en Contenido) |
| Menú del trazado: Fijar primer vértice, RotoBezier, Cerrado, Ctrl+T | 🔁 en «Editar puntos» el clic derecho abría el menú de la vista previa |
| Crear formas desde texto | ✅ r1 (H, o, l, a); 🔁 las letras salían más finas y chicas: ahora vienen del mismo motor que dibuja el texto |
| Crear formas desde capa vectorial (SVG) | ✅ r1 (4 trazados con sus colores, igual a la vista) |
| Combinar trazados (Sumar…) | ✅ r1 (6 partes → «Trazado 2 combinado») |
| Espacio + arrastrar | ≈ Espacio reproduce; la vista se mueve con el botón del medio |
| Trazo fuera del grupo al escalar | ≈ cambiar Tamaño en vez de Escala |
| Afinar con suavizados separados | ≈ Afinar con un solo suavizado |
| Quitar una parada de degradado arrastrándola | ≈ clic derecho en la parada |
