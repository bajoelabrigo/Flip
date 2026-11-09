# Motor: lo que falta (pedido de Jorge, 2026-11-08)

## Estado 2026-11-09 (segunda pasada de los packs, con lo que el motor ya tenía)
- **Arreglado en el motor (sin compilar, build 42568155238):** desenfoque gaussiano de verdad (antes 5 muestras: copias
  dobles), medido en px del proyecto (vista previa = exportación) y con margen para no cortarse en la caja; capas 3D que
  se tapan: el color se dibuja entero y solo lo sólido escribe profundidad (texto sobre una cara que gira y el triángulo
  de yp2 desaparecían); Remolino (`stylize.twirl`); contador lineal; `layoutRole` y ajuste parejo de fondos redondos.
  Cuando la build esté: en `templates_yp1.py` poner `BLUR_PX = 3`, quitar las tres capas de desenfoque encadenadas y el
  truco `FLAT` (opacidad 0,998).
- **Arreglado y compilado (build 42584213857, portable `pruebas\FlipStudio-motor-0109b`):** desfase de profundidad por orden de
  dibujo (capas 3D casi en el mismo plano respetan el orden de pistas): se fue el parpadeo de los íconos sobre las
  baldosas (yp5) y de las fotos sobre placas (yp1). Remolino sin bandas negras.
- **Sigue faltando de verdad:**
  0. **Capa que viaja sobre una cara 3D (emparentar en 3D):** hoy el padre solo pasa su movimiento 2D. Con inclinación
     fuerte, una capa encima de otra no queda en el mismo plano y la cara la tapa (yp2: triángulo del botón, fotogramas
     17–21, con Z de −2 a +20; yp1: texto e íconos de los botones que voltean, 2 fotogramas). Hoy: triángulo plano y
     opacidad 0,998 en esos botones; se ven bien.
  1. Un hueco de foto que pida «Quitar fondo» (RVM) al rellenarse, para capas entre el fondo y la persona (yp4).
  2. `liquid.gooey` sobre un grupo de capas: en una capa de ajuste solo desenfoca (el lienzo ya es opaco); hace falta
     componer el grupo sobre transparente antes de sus efectos (yp3; hoy el contorno se calcula en el generador).
  3. Extrusión real por capa (profundidad + color del canto): hoy, copias apiladas (yp1, yp3).
  4. Caja de fondo del texto que mida solo las letras ya escritas por la máquina de escribir, con cursor de bloque
     pegado (yp5, títulos en caja: hoy la caja son claves calculadas para el texto de muestra y no sigue si se edita).
  5. Humo/partículas en estelas (yp3, 91,3–91,9 s); degradado a lo largo del trazo.

Cada sección: qué hace la referencia, en qué segundos, y qué necesitaría el motor.

## yp0 (38664567) — contador de seguidores lineal — HECHO en el motor (sin compilar)
La barra de seguidores cuenta a ritmo fijo (~1500/s, 120240 → 129704); el contador del motor frenaba al final.
Nuevo `TextStyle::counterCurve` = "easeOut" (por defecto) | "linear" (`counterTextAt(..., linear)`), guardado en el
proyecto y en `AppController` (textStyle map). Prueba en `tst_core` (`counterTextCountsInTheTextsFormat`). Falta: control
en el panel de Texto (si Jorge lo quiere) y compilar; la plantilla `yp0-barra-seguidores` puede pasar `counterCurve:
"linear"` cuando el portable lo tenga.

## yp4 (pack youtube 4, historias) — 1 y 3 RESUELTOS sin tocar el motor (2026-11-09)
Texto en círculo con `pathSvg` (cuatro cúbicas: el analizador no tiene arcos); intersección = copia del disco con
máscara de elipse. **Sigue pendiente el 2** (un hueco de foto que pida «Quitar fondo» al rellenarse).
1. **Texto sobre un círculo que gira** (yp4-mi-plan, 9,9–12,4 s): hoy, un clip por palabra girado; falta texto sobre
   un trazado (círculo) con ángulo animable.
2. **Capas entre el fondo y la persona de la foto del usuario** (yp4-mi-plan, yp4-siguiente): falta que un hueco de foto
   pueda pedir «Quitar fondo» al rellenarse, para poner capas detrás de la persona.
3. **Intersección de dos formas en otro color** (yp4-bienvenida, 5,2–5,8 s): falta intersección entre capas o modo
   «diferencia»; hoy, una lente aproximada.

## yp7 (pack youtube 7) — RESUELTO sin tocar el motor (2026-11-09)
Letras con el video: copia del hueco con `matte` (alfa del texto) y brillo; líneas en su franja: `matte` con una franja que escala con el bloque; salto distinto por letra: animador en línea con `stagger` × `wiggle` (ruido, 0 Hz, `intersect`); tramas de puntos: un rectángulo con `halftone_comic` en modo «screen». Detalle en `estudio-pack-youtube-7/NOTAS.md`. Lo de abajo queda como historia.
1. **Letras que dejan ver el video de abajo, aclarado** (yp7-apertura-youtube, 0–4 s): hoy, gris claro; falta un relleno de
   texto que muestre la capa de abajo (modo de mezcla del relleno / «knockout»).
2. **Cada línea sube dentro de su franja recortada mientras el bloque se achica** (tipografía, 140–155 s): falta una
   animación de texto por línea con recorte propio, o máscaras que no sigan la escala del clip.
3. **Salto vertical distinto por letra** (yp7-greatness, yp7-awesomeness): falta desplazamiento aleatorio por letra en
   las animaciones («rise» con amplitud aleatoria).
4. **Tramas de puntos y líneas de barrido**: hoy, trazados con cientos de cuadritos; falta un relleno con patrón para formas.
- Trampa: una forma escalada a cientos de miles de px (trazados con hueco par-impar) colgó el render con 5 GB; usar un
  sólido de cuadro completo con máscara invertida.

## yp3 (pack youtube 3)
1. Giro 3D en Y con perspectiva y grosor (ícono play, caja roja, caja like→campana, tarjeta blanca): hoy, ancho que se
   aplasta + copia oscura de canto.
2. Mosaicos que se dan vuelta en 3D (pantalla rosa «next video»): hoy, rectángulos que se deslizan.
3. Claves de espaciado entre letras («Weekly videos», «Thanks for watching» se abren).
4. Animación de texto «desenfoque por letra» (todas las pantallas finales): hoy, fundido.
5. Formas líquidas que se funden (metaballs): píldora burbuja, estiramiento de color, manchas rojas.
6. Partículas de salpicadura irregulares: hoy, elipses.
7. Garabatos curvos que se dibujan y se recogen: hoy, barras rectas.
8. Esquinas redondeadas en trazados propios (hexágono).
9. Trazos con degradado (marco del hexágono, banda azul, aro del avatar).
10. Estelas en espiral de entrada: hoy, arco/espiral que se dibuja.

## yp2 (pack youtube 2) — rehecho 2026-11-09 (3D real, transiciones calcadas por fotograma, íconos en bucle)
**Fallo del motor encontrado:** dos capas 3D casi en el mismo plano con perspectiva corta (persp 500): la de arriba (el
triángulo del botón) desaparece mientras la caja se inclina mucho (yp2-apertura, fotogramas ~17–22). Hoy el triángulo va
en 2D. Revisar el orden/recorte de capas 3D coplanares.
1. Giro 3D en Y del botón con perspectiva (apertura 0–1,5 s, aro-canal 26,8–28,3 s): hoy, giro en el plano.
2. Barras de la transición diagonal que cambian de ancho y abren líneas (29,3–30,6 s): pediría morph de trazados
   (`pathShapes` existe en el motor; el generador no lo usa todavía).
3. Franjas que se deforman al girar (44,4–45,6 s): hoy, rectas.
4. Íconos en bucle infinito: hoy, 3,2 s cada uno.

## yp5 (pack youtube 5)
1. Huecos en formas (máscara invertida en formas, trazados con agujero y esquinas redondeadas): botón de YouTube con
   triángulo transparente (13,9 s), ventana del iris (183,6 s).
2. Relleno con patrón (rayas, puntos) dentro de una elipse (discos de la transición, 22,1 s).
3. Giro 3D real del botón (opener-flip, mosaicos de redes): hoy, ancho que se achica.
4. Marco en perspectiva (modern-titles, 32,5 s).
5. Ancho de caja atado al texto tecleado visible (títulos en caja, 107–124 s) y cursor de bloque rojo delante (113 s).
6. Máscara rectangular animada sobre formas (barrido de pincel, social-pincel 144,4 s).
7. Huecos de video en pantallas finales (hoy, huecos de foto).

## yp1 (pack youtube 1)
1. Objetos 3D con grosor que giran en perspectiva (pulgar, campana, insignia, logos que vuelan): hoy, ancho × cos + canto oscuro.
2. Voltear botones y textos sobre el eje X con perspectiva: hoy, el alto se achica.
3. Desenfoque gaussiano de formas y efecto remolino (twirl) para fondos de seda/líquido y la espiral.
4. Desenfoque de movimiento por forma (bordes de transiciones, zooms desde letras gigantes).
5. Dos rellenos en un mismo trazado (campana gris con badajo amarillo).
- Ya existe y conviene usar: `pathShapes` + clave `path` (morph), `cornerRadius`/`wiggleSize`/`trimEnd` animables,
  máscaras `path`, trazos con `dashPattern`, `runs` con color por letra, `letterSpacing` animado, presets
  `ibs-scatter-gather`, `im-crash-from-big`, `converge`, `blur-in`.
