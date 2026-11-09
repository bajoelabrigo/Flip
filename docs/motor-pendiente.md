# Motor: lo que falta (pedido de Jorge, 2026-11-08)

Cada sección: qué hace la referencia, en qué segundos, y qué necesitaría el motor.

## yp0 (38664567) — contador de seguidores lineal — HECHO en el motor (sin compilar)
La barra de seguidores cuenta a ritmo fijo (~1500/s, 120240 → 129704); el contador del motor frenaba al final.
Nuevo `TextStyle::counterCurve` = "easeOut" (por defecto) | "linear" (`counterTextAt(..., linear)`), guardado en el
proyecto y en `AppController` (textStyle map). Prueba en `tst_core` (`counterTextCountsInTheTextsFormat`). Falta: control
en el panel de Texto (si Jorge lo quiere) y compilar; la plantilla `yp0-barra-seguidores` puede pasar `counterCurve:
"linear"` cuando el portable lo tenga.

## yp4 (pack youtube 4, historias)
1. **Texto sobre un círculo que gira** (yp4-mi-plan, 9,9–12,4 s): hoy, un clip por palabra girado; falta texto sobre
   un trazado (círculo) con ángulo animable.
2. **Capas entre el fondo y la persona de la foto del usuario** (yp4-mi-plan, yp4-siguiente): falta que un hueco de foto
   pueda pedir «Quitar fondo» al rellenarse, para poner capas detrás de la persona.
3. **Intersección de dos formas en otro color** (yp4-bienvenida, 5,2–5,8 s): falta intersección entre capas o modo
   «diferencia»; hoy, una lente aproximada.

## yp7 (pack youtube 7)
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
