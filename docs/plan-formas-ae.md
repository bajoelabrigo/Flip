# Formas como After Effects: varias formas dentro de una capa (análisis, 2026-10-30)

Pedido de Jorge (con capturas de AE): en After Effects una capa de forma tiene **Contenido** con varias formas
(«Rectangle 1», «Rectangle 2»…), cada una con su trazado, relleno, trazo y transformación, que se animan y editan
por separado. Copiarlo tal cual en Flip, **solo en modo Pro**.

## Lo que hay hoy (0.27)
- Un clip de forma = **una** figura (`ShapeStyle`: `kind` + geometría, o `customPath` con varios contornos desde la
  pluma de la 0.26) y **una** pila de capas de pintura (`TextShadingLayer`: rellenos, trazos, sombras, brillos), con
  sus operadores (recortar, repetidor, ondular, fusionar, desplazar, zigzag, torcer, fruncir) sobre **toda** la figura.
- La transformación es la del clip (anclaje, posición, escala, rotación, opacidad) y las filas de la pista son las fijas
  de la 0.25 (`fixedKeyframeGroups`). Las propiedades de la forma se animan con claves `layer.<id>.<campo>`, pero no
  salen como filas en la línea de tiempo: se editan en el inspector (`ShapeInspector.qml`).
- Render: `SkiaShapePainter` arma un solo `SkPath`, le aplica los operadores y pinta la pila.
- Lo que no hay: grupos, una transformación por forma, inclinación y su eje, y un orden de AE en el que un relleno o un
  trazo pinta los trazados de **su** grupo. Al trazo le faltan Taper (adelgazar los extremos), Wave (onda), lista de
  guiones y límite de inglete. La regla de relleno vale para toda la forma. No hay árbol «Contenido» con «Añadir ▸».

## Cómo quedaría (igual a AE)
**Modelo** (`core/ShapeContents.h`, nuevo): `ShapeStyle` gana `contents`, una lista ordenada de elementos como en AE:
- **Grupo**: nombre, visible, modo de fusión, sus propios elementos (anidables) y **Transformar: Grupo** (anclaje,
  posición, escala, inclinación, eje de inclinación, rotación, opacidad).
- **Trazados**: Rectángulo (tamaño, posición, redondez), Elipse (tamaño, posición), Polígono/Estrella (puntos, radios y
  redondez interior/exterior, rotación) y Trazado libre (el de la pluma, animable como ya lo es en la 0.26).
- **Pinturas**: Relleno (color, opacidad, regla de relleno, composición) y Trazo (color, opacidad, ancho, extremo,
  unión, límite de inglete, guiones, **Taper**, **Wave**), y sus versiones con degradado. Reusan `TextShadingLayer`.
- **Operadores**: los de la 0.26, más «Redondear esquinas» y «Transformación ondulada», cada uno **dentro** del grupo
  donde se pone.
- **Regla de AE para el orden**: un relleno o trazo pinta todos los trazados que tiene encima en su grupo; un
  operador cambia los trazados que tiene encima. «Composición: debajo del anterior en el mismo grupo».
- **Compatibilidad**: un proyecto viejo (sin `contents`) se lee como un solo grupo con su figura y su pila, y se ve
  igual. Versión de proyecto 16; una app vieja que abra uno nuevo verá la forma «aplanada» (se guarda también
  `customPath` con el resultado, como respaldo).
- **Claves**: `contents.<idElemento>.<campo>` (p. ej. `contents.r2.size.w`, `contents.g1.transform.rotation`), con el
  mismo cronómetro, curvas, expresiones y comportamientos de la 0.25/0.26.

**Render**: `SkiaShapePainter` recorre el árbol como AE (de abajo arriba en cada grupo, acumulando las matrices de
grupo), aplicando operadores y pinturas en su sitio. La caché de render ya usa un hash del estilo; se extiende al árbol.

**Línea de tiempo (Pro)**: bajo la pista de forma, filas en árbol como en las capturas: «Contenido» con «Añadir ▸» a
la derecha, cada grupo con su ojo, su modo de fusión y sus hijos (Trazado de rectángulo › Tamaño / Posición /
Redondez, Trazo › …, Relleno › …, Transformar: Rectángulo › …), después «Transformar» de la capa. Cronómetro y
valores azules arrastrables en cada fila (`ScrubValue`), renombrar con doble clic, arrastrar para reordenar,
Ctrl+D duplica, Suprimir borra, Ctrl+G agrupa los elementos elegidos.

**Vista previa (Pro)**: clic elige la capa; doble clic entra en un grupo y muestra **su** recuadro, con tiradores
para moverlo, escalarlo y girarlo (su Transformar). En un rectángulo o elipse, tiradores de tamaño y redondez. Las
herramientas de forma y pluma de la barra dibujan **dentro** de la capa elegida (como AE: con la capa elegida, un
rectángulo nuevo se suma como «Rectángulo 2»).

**Inspector**: la pestaña de forma muestra el elemento elegido en el árbol (si no, la capa entera, como hoy).

**Extras**: «Combinar en una capa de forma» (varios clips de forma elegidos → una capa con un grupo por clip) y
«Separar en capas» (lo contrario); herramientas MCP (`add_shape_item`, `set_shape_item`, `group_shape_items`); en
expresiones, `content("Rectángulo 1")`. En Simple no se ve nada de esto: la forma sigue siendo una figura.

## Etapas
1. Modelo, JSON, lectura de proyectos viejos y render del árbol, con pruebas (`tst_core`: orden de pintura de AE,
   grupos anidados, claves por elemento, proyecto viejo idéntico píxel a píxel).
2. Filas «Contenido» en la línea de tiempo con «Añadir ▸», ojos, fusión, cronómetros y valores.
3. Vista previa: entrar en grupos, tiradores por grupo y por rectángulo/elipse, dibujar dentro de la capa elegida.
4. Trazo completo (Taper, Wave, guiones, inglete), rellenos y trazos degradados, Redondear esquinas, Transformación
   ondulada, Polígono/Estrella con redondez.
5. Combinar/Separar capas, MCP, expresiones, traducciones; prueba en ventana de cada punto.

Riesgo principal: es el cambio más grande en las formas desde Drift; hay que cuidar que los proyectos y plantillas
existentes (Stock, el Kit de YouTube) se vean igual, por eso la etapa 1 compara píxeles antes y después.
