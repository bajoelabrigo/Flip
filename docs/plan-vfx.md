# Plan VFX (Stock › VFX, segundo intento) — estudio del 2026-11-15

Para retomar los efectos dibujados a mano tipo RTFX (fuego, explosión, humo, electricidad, chispas, energía,
líquidos, líneas, cómic y transiciones de mate) con el motor de formas de la 0.32 (`flip/v0.32`, `docs/plan-0.32.md`
§ 5). Jorge pausó el primer intento el 2026-10-30: «no me convencen»; «el fuego por ejemplo no quedaba bien».
**Líquidos va primero**, si a Jorge le gusta la yp10 rehecha.

Referencias (licenciadas a Jorge, **solo para estudiar**; nunca copiar su contenido): `Videos\aTubeCatcher\RTFX
Generator Plugin….mkv` (páginas «OVERVIEW» por familia de 3:46 a 5:16) y el tutorial «How to use RTFX Generator
Update v.2» (el nombre trae un espacio raro: abrirlo con un comodín, `How*RTFX*`).

## Hojas de estudio (`E:\FlipStudio\tienda\vfx-estudio\`)

| Carpeta | Qué hay |
|---|---|
| `_overview\` | `overview_220_340.png` (todas las familias cada 2 s), `pair1`–`pair5.png` (explosión+líquido, electricidad+energía, chispas+humo, líneas+mate, cómic+mate), `tutorial_cada8s.png` |
| `fuego\` | `rtfx-llama-suelo.png` (cada 2 cuadros), `rtfx-llama-suelo-cuadro-a-cuadro.png` (zoom, cuadro a cuadro), `nuestro-golpe-arriba.png`, `nuestro-v1-antorcha.png`, **`comparacion-rtfx-vs-nuestro.png`** |
| `explosion\` | `rtfx-humo-explosion.png` (destello → nube de humo), `rtfx-destello.png`, `nuestro-explosion-radial.png` |
| `humo\` | `rtfx-nube.png` |
| `liquido\` | `rtfx-goteo.png`, `rtfx-mancha.png` |
| `electricidad\` | `rtfx-rayo-vertical.png` (cuadro a cuadro), `rtfx-espiral.png`, `nuestro-carga.png` |
| `energia\` | `rtfx-energia-carga-tutorial.png` |
| `chispas\` | `rtfx-estrella.png` |

`hoja_cuadros.py VIDEO INICIO DURACIÓN w:h:x:y SALIDA.png [cada] [columnas] [escala]` saca cada cuadro de un
recorte, dice cuántos cuadros dura cada dibujo (2 = «en dos») y los colores más usados, y arma la hoja. Ojo: la
cuadrícula del OVERVIEW se desliza a veces; si una celda «salta», recortar otra vez un poco antes o después.

## Lo que es RTFX (vale para todas las familias)

- **Son capas de formas vectoriales** (el tutorial: «Collapse transform» para agrandarlas sin perder calidad), una
  «capa Control» con color, resplandor y desenfoque. Cada dibujo es un trazado a mano; no hay ruido ni partículas.
- **Dos tonos planos + resplandor.** Fuego: amarillo pálido `#fefe8f` y rojo `#fd1000` (naranja `#ff6a04` solo en
  algunas llamas); humo: blanco `#dcdcdc` y gris `#a8a8a8`; líquido: turquesa `#48a8a8`, lado oscuro `#186060`,
  brillo y punto blanco; electricidad: núcleo `#d8f0f0` dentro de una banda azul `#3048c0`; energía: blanco con
  borde y resplandor azul `#3078f0`; explosión: amarillo → naranja → marrón `#5a3c34` con huecos más oscuros.
- **Contornos de curvas largas que terminan en puntas afiladas.** Curvas lisas y esquinas duras en el mismo dibujo
  (puntas de lengua, muescas). Nunca un borde «grumoso» parejo.
- **Animado en dos** (un dibujo cada 2 cuadros a 24 fps; en el video de 30 fps se ven pares iguales). La
  electricidad va en uno (dibujo nuevo cada cuadro). Sin desenfoque de movimiento.
- **El resplandor va solo hacia afuera** y es del color del tono de afuera (rojo en el fuego, azul en la energía).
  Humo y líquido no llevan resplandor.
- **Nacen** de un punto o una línea, con 1–2 dibujos chicos; **mueren** rompiéndose: huecos que crecen por dentro
  (humo), tiras que se separan y suben (fuego), gotas que se estrangulan y caen (líquido), mordiscos desde el borde
  (chispas). Casi nunca un fundido de opacidad (la excepción es el humo de la explosión).

## Por qué el primer intento se veía hecho por computadora (fuego)

Ver `fuego\comparacion-rtfx-vs-nuestro.png` (izquierda RTFX; centro nuestro «Golpe hacia arriba» publicado; derecha
la antorcha v1):

1. **Borde de ruido.** Los contornos salían de cortar un campo de ruido (`rtfx_field.py`, OpenCV): todo el borde
   tiene la misma «textura» de bultitos chicos y no hay ni curvas largas ni puntas. RTFX: 6–10 curvas largas por
   llama, cada lengua en S que termina en punta.
2. **Rojo como aro parejo.** El rojo era la misma forma un poco más grande (un nivel más del campo), así que rodea
   el amarillo con un aro del mismo ancho en todos lados. En RTFX el rojo es **otra forma**: casi nada en la base y
   del lado del viento, ancho y con lenguas propias del lado de atrás; el amarillo es más corto que el rojo.
3. **Mucho amarillo y agujeritos.** Nuestro fuego es ~60 % amarillo con puntos rojos sueltos (ruido). En RTFX el
   amarillo es ~35 % y lo rojo de adentro son **1–3 bolsillos grandes**, alargados a lo largo del fuego.
4. **Forma simétrica (hongo/coliflor) y sin dirección.** RTFX siempre se inclina (viento) y es asimétrico.
5. **La muerte.** Nuestro: el borde se come parejo hacia adentro o se deshilacha en pelos radiales. RTFX: primero se
   apaga el amarillo (todo queda rojo), después el rojo se corta en **tiras diagonales** que suben y se achican a
   puntos (cuadros 6–12 de la hoja cuadro a cuadro).
6. **La explosión no tenía humo.** RTFX: destello amarillo → la misma nube cambia de color a naranja y luego marrón
   con huecos oscuros sombreados → se queda y se desvanece; estelas de humo finas salen hacia afuera.

Lo que sí funcionó (Jorge aprobó 17): la electricidad (está cerca; le faltan puntas finas y la línea doble), las
chispas y la energía simples. El ritmo de 12 dibujos por segundo estaba bien.

## Qué ya da el motor de la 0.32

Formas propias con claves de «Trazado» y **transformación suave** entre trazados distintos (`smoothMorph`: gotas que
se separan), **trazos con Taper y punta redonda** (pinceladas), **Trim Paths** (dibujarse solo), **Wiggle Paths**
(también abierto), Offset/Zig Zag/Merge Paths/Pucker, **Repetidor**, varias capas de pintura en una forma (relleno +
trazo + trazo), relleno par-impar (huecos), **Mate de pista** (alfa/luma, invertido), **Brillo exterior**
(`layer_outer_glow`, con color), `liquid.gooey`, colores animables con claves, y en `tools/scene_templates/liquid.py`
los ayudantes `brush`, `rays`, `splash`, `morph_keys` y `smooth_path`. Con eso, cada efecto se hace como plantilla
nativa (editable, nítida a cualquier tamaño) en vez de un Lottie trazado cuadro a cuadro.

## Lo que falta en el motor (por orden de cuántas familias lo necesitan)

- **A. Esquinas en la transformación suave.** `smoothMorph` y `smooth_path` redibujan todo con Catmull-Rom: todo
  sale redondo. Hace falta marcar vértices como **esquina** (puntas de lengua, muescas, puntas de destello) y que la
  mezcla los conserve y los empareje entre claves. *Fuego, energía, chispas, explosión (destello), cómic, mates.*
- **B. Posterizar tiempo por capa** (como «Posterize Time» de AE: la capa se calcula a 12 u 8 fps aunque el
  proyecto vaya a 30). Sin esto, la transformación suave, el Trim y el Wiggle se ven «de computadora» por lo
  fluidos. Hoy solo se puede con claves «hold» cada 2 cuadros (miles de claves y sin aprovechar el morph). *Todas.*
- **C. Sombra interior de borde duro** en una capa de pintura de la forma: el mismo contorno desplazado (dx, dy) y
  restado, pintado en un segundo tono, sin desenfoque (la «panza» gris del humo, el lado oscuro del líquido, las
  medias lunas marrones de la explosión, el borde azul por dentro de la energía). Que siga al trazado animado.
  *Se puede hoy* con dos clips (el tono oscuro con un mate alfa invertido de una copia desplazada), pero duplica
  cada forma y cada clave. *Humo, explosión, líquido, energía.*
- **D. Contornos que nacen y mueren en su propio centro.** En el morph, un contorno sin pareja nace del punto más
  cercano del otro; para un **hueco** que se abre dentro del humo, una **gota** que se suelta o una **tira** que se
  apaga hace falta que nazca/muera como un punto en su propio centro (o en un punto dado). *Humo, fuego,
  explosión, chispas, líquido.*
- **E. Wiggle y Zig Zag «a saltos».** Hoy el Wiggle se mueve suave (`wiggleSpeed`); el temblor de un dibujo animado
  es un **sorteo nuevo en cada dibujo** (en uno o en dos) y, en la electricidad, con quiebres en punta (zig zag
  irregular, no parejo). Un modo «a saltos» para Wiggle Paths y Zig Zag (semilla nueva cada N cuadros, tamaño de
  cada punta al azar). *Electricidad (imprescindible), y el «hervor» leve de humo, cómic y líneas.*
- **F. Flecos en el borde** (la «pelusa» de los estallidos de energía y del destello): puntas radiales cortas e
  irregulares. Se puede aproximar con `rays` (trazos con Taper) o con E. *Energía.*
- **G. Entrega de las transiciones de mate.** Una plantilla de formas que se use como **mate entre dos clips**
  (el clip B aparece donde la forma cubre). El mate de pista existe; falta que Stock lo inserte así (hoy las
  transiciones de Stock son shaders `.driftfx`). *Mates.*
- **H. Comprobar** (no necesariamente falta): que Merge Paths reste entre partes de un grupo y no solo entre
  contornos de un trazado; que el Brillo exterior de una capa no se dibuje por dentro de la forma.

También hay que decidir la **entrega**: las 17 de octubre eran stickers Lottie (tipo `vfx`, entrega «media»). Las
nuevas deberían ir como plantilla nativa (`scene-template`, encima del video, con `minAppVersion` 0.32 o la versión
que traiga A–E), para que el color y el tamaño se cambien desde el panel Plantilla (sección Colores de la 0.32).

## Por familia

**Líquidos** (`liquido\`). Turquesa con lado oscuro (C), brillo arriba a la izquierda y un punto blanco; contorno
oscuro fino en algunos. Gotas que se estiran, se estrangulan y caen (morph + D); salpicaduras con huecos. Ya casi
todo está (`splash`, `morph_keys`, `liquid.gooey`). **Falta:** C (o el mate), D, B. → primera familia.

**Humo** (`humo\rtfx-nube.png`). Blanco + gris abajo de cada bulto, sin contorno ni resplandor. Nace de un bulto en
el piso que crece en 4–5 dibujos; muere con **huecos redondos que se abren y crecen** hasta dejar medias lunas.
**Falta:** C, D, B. Es la familia más simple después de líquidos y prueba C y D para todo lo demás.

**Explosión** (`explosion\rtfx-humo-explosion.png`). Chispa → destello amarillo con resplandor (2–3 dibujos) → la
**misma silueta** pasa a naranja con medias lunas marrones que crecen (brasas que se apagan) → nube marrón de dos
tonos que se queda y se desvanece; estelas de humo finas y curvas (trazos con Taper y Trim). **Falta:** C, D, B, A
(el destello). Colores con claves: ya existen.

**Fuego** (`fuego\`). Ver la receta abajo. **Falta:** A, B, D (y C opcional para un tercer tono).

**Electricidad** (`electricidad\`). Polilínea quebrada en punta con **dos trazos en el mismo camino** (núcleo claro
fino + banda azul ancha) y resplandor azul fuerte; a veces doble línea y ramas; puntas que se afinan (Taper);
**dibujo nuevo cada cuadro**. Nuestro intento ya estaba cerca. **Falta:** E (imprescindible), Taper en los extremos
(existe), B en 1.

**Energía** (`energia\`, `_overview\pair2.png`). Formas blancas sólidas (medias lunas, cuchillas, gotas, anillos)
con borde azul por dentro y gran resplandor azul; estallidos con borde de flecos. **Falta:** A, C, F, B.

**Chispas** (`chispas\`, `_overview\pair3.png`). Lentes (forma con dos puntas) amarillas con borde rojo y
resplandor, estrellas de 4 puntas, anillos de puntos (Repetidor). Mueren a mordiscos desde el borde o achicándose.
**Falta:** A, D, B. `rays` sirve para los chorros.

**Líneas** (`_overview\pair4.png`). Medias lunas y espirales de trazo con Taper que se dibujan y se borran (Trim),
a veces con una copia desplazada de otro color. **Ya se puede** (`brush`); solo B y E leve.

**Cómic** (`_overview\pair5.png`). Mezcla de texto con forma (SPLASH, BOOM, FHSSS), gotas de sudor, lágrimas en
chorro con espuma blanca, nubecitas, llama de enojo en tres tonos. Se arma con lo de las otras familias + texto.
**Falta:** A, B, E (hervor).

**Mates** (transiciones; `_overview\s_matte.png`, `pair4.png`). Blanco y negro a pantalla completa: ola líquida con
gotas, manchas de tinta, salpicaduras. Las formas ya se pueden; **falta:** G (y B, D).

## Cómo hacer el fuego esta vez

1. **Nada de campos de ruido ni OpenCV.** Cada dibujo es un trazado de 12–25 puntos con puntas marcadas (A).
2. **Esqueleto:** una espina en S inclinada por el viento y 2–4 lenguas que salen de ella; el ancho a lo largo de
   cada espina decrece hasta la punta (como un trazo con Taper, pero se guarda como contorno cerrado para poder
   rellenarlo). Asimétrico siempre.
3. **Capa roja (cuerpo):** ese contorno. **Capa amarilla (corazón):** otro contorno, más corto que el rojo, corrido
   hacia la base y el lado del viento (el rojo casi no asoma ahí: 2–4 px; del lado de atrás, ancho y con lenguas
   propias), con **1–3 bolsillos** rojos alargados a lo largo del fuego (huecos, par-impar). Nunca el rojo como
   aro parejo. Amarillo ~35 % del área.
4. **Resplandor exterior** rojo-anaranjado en la capa roja (tamaño ~15–25 px a 1080), que late un poco; nada de
   halo por dentro.
5. **Tiempos (a 12 dibujos/s, B):** nace de un punto o una línea en el piso en 3–5 dibujos; ciclo de 6–8 dibujos
   que se repite (las lenguas suben y la punta se suelta como una gota que sube y se achica, D); muere en 4–6
   dibujos: el amarillo se encoge y desaparece primero (queda todo rojo) y el rojo se corta en tiras diagonales
   que suben y terminan en puntos.
6. **Claves cada 2–4 dibujos** con la transformación suave que conserva puntas (A) y la capa posterizada a 12 fps
   (B). Sin A y B: generar una clave «hold» por dibujo, como antes, pero con los contornos de los puntos 1–5.
7. Antes de hacer muchos: **un prototipo al lado de `fuego\rtfx-llama-suelo-cuadro-a-cuadro.png`** (cuadro a
   cuadro, misma escala) y que Jorge lo vea. Recién con su sí, la tanda (antorcha, suelo, lanzallamas, explosión de
   fuego, alas, anillo).

## Orden propuesto

1. **Líquidos** (con la yp10 aprobada). Hacer B y C (o probar el mate) aquí, que sirven a todo.
2. **Humo** (prueba C y D en limpio).
3. **Explosión** (humo + destello + cambio de color).
4. **Fuego** (necesita A; es el que Jorge criticó: prototipo primero).
5. **Chispas y Líneas** (trazos, `rays`, `brush`).
6. **Energía** (A, C, F).
7. **Electricidad** (E).
8. **Cómic** (une lo anterior con texto).
9. **Mates** (G: entrega como transición).

Motor en una sola tanda si se puede (A, B, C, D, E juntos en la versión siguiente a la 0.32), con sus pruebas, y
cada familia **vista en ventana** antes de subir nada a Stock.

## Estado (2026-11-16)

- **Motor A–E y H: HECHO** en la 0.32 (`flip/v0.32`, detalle en `docs/plan-0.32.md` § 7): esquinas en la
  transformación suave, posterizar tiempo por clip, tono interior, romperse / contornos que nacen en su centro, wiggle y
  zig zag a saltos, y Combinar trazados en vivo dentro de un grupo. Jorge vio las muestras («están bien»). Unido con el
  Goteo y las claves por cuadro (compilación 43786419000, pruebas 43786410473, en verde; portable en
  `pruebas\FlipStudio-0.32-todo`).
- **Líquidos, primera tanda de prototipos (nada en Stock).** Jorge: «hazlo lo más parecido al original… no inventes
  nada», como los tercios. Única fuente: la página OVERVIEW › LIQUID del video (241,4–251 s), una cuadrícula de celdas
  que a ratos se reacomoda. Seis elementos con su vida entera visible en una celda: **columna** (sube, se tuerce y se
  parte en gotas), **goteo** en T (labio, chorro, cuello, gotas que caen), **salpicadura** doble, **racimo** de tres
  gotas que se separan, **anillo** de arcos que se rompe en puntos y **gota** que sube y se parte.
  - Cómo: `tools/scene_templates/vfx_measure.py` mide cada cuadro (piezas, contorno grueso de pocos puntos, huecos,
    tamaño y dónde está); `vfx_liquid_rtfx.py` redibuja cada dibujo con nuestras formas (trazado suave por pieza, gotas
    redondas como elipses, relleno turquesa, lado oscuro con tono interior, borde claro, brillo blanco propio) con
    claves en los mismos cuadros (sostenidas entre medio: el mismo ritmo), mismo tamaño relativo, dirección y
    duración. No se usa ningún píxel del video.
  - Salida en `E:\FlipStudio\tienda\vfx-estudio\liquido\prototipos\`: `<nombre>.mp4` (solo, sobre negro) y
    `comparacion-<nombre>.mp4` («Referencia RTFX» | «Nuestro (Flip)», sincronizados, tres vueltas). Medidas y hojas de
    estudio en `liquido\estudio\`.
  - Lo que todavía difiere: los dibujos de dentro (bolsillos oscuros y brillos con forma) son nuestros y más simples
    (un tono interior y un brillo por pieza); los bordes salen algo más lisos; los restos muy tenues del final no se
    dibujan; en **racimo** y **anillo** la celda de referencia se reacomoda a mitad (la página cambia), así que la
    referencia salta y la nuestra también.
  - Falta en el motor para hacerlo sin medir: un **tono interior por pieza** (hoy el desplazamiento es uno para todo
    el trazado), **varios colores dentro de una forma** (bolsillos oscuros y brillos dibujados como contornos propios)
    y que la **posterización** pueda seguir un ritmo irregular (hoy: claves sostenidas).
  - Entrega pensada: plantilla nativa (`scene-template`, encima del video), no Lottie; decidir con Jorge.
- **Segunda vuelta (2026-11-16, Jorge: «se parece bastante, pero si lo puedes mejorar mucho mejor»).**
  - Motor (0.32): **grupo de recorte** (`ShapePart::clipChildren`, JSON `"clip": true`: las partes de arriba solo se
    ven dentro de la de abajo, cada una con su color y sus claves; inspector del grupo: «Mostrar las partes solo dentro
    de la de abajo») y **tono interior por pieza** (`tonePerContour`: desplazamiento en % del tamaño de cada contorno,
    escala y giro sobre su propio centro). Pruebas `SkiaTest::shapeClippingGroupAndToneByPiece`. CI 43795102160 y
    43795102915 en verde; portable `pruebas\FlipStudio-0.32-todo2`.
  - `vfx_liquid_rtfx2.py`: cada dibujo es un grupo de recorte con tres partes (cuerpo con borde claro, **bolsillos
    oscuros** y **brillos** medidos por color dentro de cada pieza, cada uno con su contorno y sus claves); contornos
    más finos (un punto cada ~0,5 % del borde, quiebres conservados; las piezas chicas, más suaves); los **restos
    tenues** del final (umbral más bajo; el blanco solo cuenta junto al turquesa, así no entran las chispas de las
    celdas vecinas); **racimo** sigue el desplazamiento de la página (la página baja ~870 px entre los cuadros 135 y
    151, medido con correlación de fase), así que el nuestro queda quieto y no copia el salto.
  - Salida: `<nombre>-v2.mp4`, `comparacion-<nombre>-v2.mp4` y `hoja-<nombre>-v2.png` en `liquido\prototipos\`.
  - Sigue distinto: el borde de la referencia es borroso (video comprimido y ampliado) y el nuestro nítido; en **gota**
    no sale la astilla fina del primer cuadro; algún cuello muy fino del goteo se pierde en uno o dos cuadros; los
    últimos puntitos del anillo, apenas visibles en la referencia, salen menos.
- **Jorge aprobó la segunda vuelta de los líquidos (2026-11-16): «me convenció».** Nada en Stock todavía.
  - **Siguiente:** la próxima familia según «Orden propuesto» (humo, después fuego…), con el mismo método:
    medir cuadro a cuadro la referencia, redibujar con nuestras formas y grupos de recorte, comparar lado a lado.
  - Antes de subir cualquier VFX a Stock: decidir con Jorge la licencia (las siluetas siguen muy de cerca el arte de
    RTFX, que él tiene solo para estudiar) y la entrega (plantilla nativa encima del video).
