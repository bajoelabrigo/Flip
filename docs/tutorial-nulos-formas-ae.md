# Cursos de After Effects: nulos y formas/pluma (2026-11-04)

Pedido de Jorge: comprobar que todo lo que muestran los dos videos (`Downloads\trabajar con nulos.txt`,
`Downloads\curso de formas.txt` y los `.mkv` de `Videos\aTubeCatcher`) se pueda hacer en Flip, añadir lo que falte
y probarlo **en ventana sin el mouse**. Igual que `docs/tutorial-keyframes-ae.md`. Archivos de prueba en
`E:\FlipStudio\pruebas\cursos-nf` (`logo-prueba.ai`, `formas.svg`, `wheeldrag.py` = arrastrar girando la rueda).
También: abrir archivos de Illustrator (`.ai`).

Leyenda: ✅ visto en ventana · 🔁 arreglado tras la primera ronda, falta volver a verlo · ≈ se hace de otra forma.

Rondas: **r1** = build 41853361934 (`pruebas\FlipStudio-0.30-nf1`); **r2** = build 41868656800 (`pruebas\FlipStudio-0.30-nf2`);
**r3** = build 41874630576 (cifra de la fila con expresión y rótulos de Ctrl+T).

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
| Tecla E: todos los parámetros de los efectos | ✅ r2: valor por defecto y muestra de color |
| Ver los controles al desplegar la capa, sin claves | ✅ r2 |
| Látigo de una propiedad a un efecto | ✅ r1: escribe `thisComp.layer("Nulo 1").effect("Control deslizante")("Deslizador")` |
| Escala enlazada a un deslizador en % | ✅ r2 en la vista (50 % → 150 %); ✅ r3: la cifra de la fila también (150 % en 2 s, 100 % en 1 s) |
| Renombrar un efecto | ✅ r2: la fila y la expresión siguen al nombre nuevo («Escalador») |
| «Habilitar expresión» | ✅ r1 («Expresión activa»: apagada vuelve al valor propio) |
| Alt+clic en el cronómetro: crear/quitar | ✅ r2: también quita una apagada |
| Nombre en rojo con expresión | ✅ r1 |
| Buscar propiedades («color») | ✅ r2: sale «Control de color · Color» |

## Formas y pluma

| Del curso | En Flip |
|---|---|
| Alt+clic en la herramienta: la forma siguiente | ✅ r2 (con ícono propio del redondeado) |
| Doble clic en la herramienta: forma del tamaño del cuadro | ✅ r2: rectángulo del tamaño del cuadro |
| Polígono/estrella: rueda = puntos, gira con el puntero | ✅ r2: se ve el polígono al arrastrar y el desplegable dice «Polígono (8 lados)» |
| Alt+clic en Relleno/Trazo | ✅ r1 (sólido → lineal → radial → ninguno, sobre la forma elegida) |
| Modo máscara de la herramienta | ✅ r2: la máscara toma el rectángulo arrastrado, en el espacio de la capa (como AE) |
| Máscara en una capa emparentada a un nulo que gira | ✅ r2: los tiradores calzan con la parte visible |
| Guion/Espacio en px, varios pares | ✅ r1 (Guion 1, Espacio 1, Guion 2… con + y −) |
| Recortar trazados, transformar grupo, Ctrl+G, alinear | ✅ ya existían |
| Pluma sobre una capa de formas elegida: añade un trazado | ✅ r1 («Trazado 1», «Trazado 2» en Contenido) |
| Menú del trazado: Fijar primer vértice, RotoBezier, Cerrado, Ctrl+T | ✅ r2: menú en «Editar puntos»; RotoBezier y Ctrl+T (Escala X 50 %) probados; ✅ r3 con rótulos (Escala X %, Escala Y %, Rotación °) |
| Crear formas desde texto | ✅ r2: mismas letras, tamaño y lugar que el texto |
| Crear formas desde capa vectorial (SVG) | ✅ r1 (4 trazados con sus colores, igual a la vista) |
| Combinar trazados (Sumar…) | ✅ r1 (6 partes → «Trazado 2 combinado») |
| Espacio + arrastrar | ≈ Espacio reproduce; la vista se mueve con el botón del medio |
| Trazo fuera del grupo al escalar | ≈ cambiar Tamaño en vez de Escala |
| Afinar con suavizados separados | ≈ Afinar con un solo suavizado |
| Quitar una parada de degradado arrastrándola | ≈ clic derecho en la parada |

## Cierre (2026-11-04)

Todo lo de los dos cursos quedó visto en ventana en r1–r3 sin usar el mouse; registro restaurado (0 diferencias).
Detalles que quedan como en After Effects o para más adelante:
- La pluma sobre una capa de formas añade un trazado nuevo; para editar los puntos de una parte se usa «Editar puntos».
- Un clip de texto convertido en formas se queda en su pista de texto (After Effects crea una capa nueva y apaga el texto).
- Una máscara dibujada sobre una capa girada sale en el espacio de la capa (como AE): un arrastre en diagonal da un rectángulo angosto.
- Las notas de la Store (1356/1500) no tienen lugar para los cursos: van en `release-notes/0.30.0.md` y en la web.
- Prueba inestable en CI: `EditorStateTest::packagedProjectCarriesDerivedArtifacts` falló una vez porque el servidor no tenía la fuente Inter; pasó al relanzar.
