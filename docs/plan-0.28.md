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
1. [~] Datos + dibujo + compatibilidad (commit «a shape layer can be made of parts», build de CI en curso).
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
2. [ ] Columna derecha: lista Contenido, «+ Añadir», parte elegida con sus secciones, menú de clic derecho.
3. [ ] Línea de tiempo: filas en árbol, Añadir ▸, ojos y fusión, cronómetros; selección compartida con la columna.
4. [ ] Vista previa: entrar con doble clic, migas de pan, tiradores de la parte, dibujar dentro, combinar/separar.
5. [ ] Borde completo (Taper, Wave, guiones, inglete), degradados, Redondear esquinas, Transformación ondulada,
   estrella con redondez; MCP, expresiones `content("…")`, traducciones, notas.

## Decisiones (Jorge)
- [x] Nombres (Jorge, 2026-10-30: opción A): columna derecha con nombres claros (Forma, Relleno, **Borde**, **Posición y
      giro de la parte**, Efectos de trazado) y el nombre de AE en la ayuda (?); línea de tiempo con los de AE
      (Trazado de elipse, Relleno, Trazo, Transformar: Elipse 1).
- [x] Dibujar con una capa de forma elegida: **se suma a esa capa** (como AE), con el aviso «Añadido a … · Hacer capa
      nueva» (Jorge, 2026-10-30).
