# Animaciones propias de Stock — guía (investigación del 2026-10-15)

Pedido de Jorge: **al menos 50**, mirando las mejores. Hechas por nosotros (Lottie solo con formas),
así son nuestras sin problemas de licencia. LottieFiles **no** se integra (su licencia prohíbe
recopilar su catálogo); solo un botón que abre su web.

## Categorías (id de categoría)
celebracion · resaltar · flechas · formas · redes · emociones · negocios · llamadas · clima · transiciones ·
fechas · comida · deportes · iconos

Referencias: etiquetas en tendencia de LottieFiles (loading, success, confetti, arrow, check, money),
packs de Envato/MotionArray (llamadas, bocadillos, precios, suscribirse, desliza/toca, garabatos,
formas), categorías de CapCut (tendencias, emojis, corazones, temporadas).

## Reglas de calidad
1. Nunca lineal (salvo giros continuos): entrar con ease-out, salir con ease-in.
2. Rebote 108–125 % en los «pop» y que se asiente en 1–2 oscilaciones.
3. Entradas de 0,4–0,8 s; trazos dibujados 0,5–0,6 s; celebraciones hasta 1,6 s.
4. Escalonar: 20–50 ms entre piezas, 80–150 ms entre elementos que se leen en orden; lo que cuelga
   (cuerdas, asas) sigue con 2–4 fotogramas de retraso.
5. Ciclos sin costura (primer fotograma = último); las entradas terminan en un fotograma limpio.
6. Trazo uniforme (~14–22 px en 512), remates redondos.
7. Legible a 64–96 px: siluetas claras, 1–2 colores principales.
8. Solo capas de forma, colores como ranuras (`sid`) para que Flip los cambie.

Sin logos de plataformas (el botón de reproducir es redondo y blanco, no rojo rectangular).

## Tanda de 200 (2026-10-16)

Pedido de Jorge: **al menos 200**, calidad antes que velocidad. Se suman 157 a los 65 (222 en total), en
`designs3.py` … `designs7.py`, con los ayudantes de movimiento en `kit.py`.

Tendencias que se miraron (catálogos de CapCut, Motion Array, Envato Elements, LottieFiles, Picsart): garabatos a
mano (subrayados, recuadros, flechas con bucle, espirales), brillos Y2K de cuatro puntas, formas retro (margarita,
asterisco, sello ondulado), iconos de redes **genéricos** (en vivo, republicar, nuevo seguidor, verificado),
emojis propios (guiño, lentes, derritiéndose, diablillo…), precios y ofertas, gráficos, cargando/descargar,
cuenta regresiva **sin números** (puntos que se van), bocadillos y tarjetas, clima y naturaleza, comida y
fiestas **de todo el mundo** (Navidad, Año Nuevo, San Valentín, Halloween, Pascua, Diwali, Año Nuevo Lunar,
Ramadán, graduación, bodas), nada solo peruano ni latino.

Categorías nuevas: `fechas` (Fechas especiales), `comida` (Comida y bebida), `deportes`, `iconos`
(nombres es/en en `publish.py`).

| Categoría | Nuevas |
|---|---|
| celebracion | cañón de confeti, pastel con velas, regalo sorpresa, gorro de fiesta, bola de disco, medalla, corona, banderines, varita mágica, bengala, guirnalda de luces, estrella fugaz |
| resaltar | subrayado ondulado, recuadro a mano, tachado, estrella a mano, ¡atención!, corchetes, foco de luz, corazón a mano, mira de enfoque, ojo que mira, chincheta, espiral |
| flechas | flecha con bucle, doble, gruesa, flechas al centro, en U, desliza hacia abajo, clic, punteada, ondulada, círculo con flecha, mano que señala |
| formas | brillo Y2K, sello ondulado, infinito, puntos en onda, estrella que cambia, anillos de puntos, margarita retro, asterisco, gota, formas flotantes, burbujas, olas |
| redes | en vivo, nueva notificación, republicar, nuevo seguidor, reacciones en vivo, avión de papel, cámara, micrófono, mensaje con amor, enlace, numeral, verificado |
| emociones | guiño, lentes de sol, llorando, enojado, beso, dormido, deslumbrado, cara de fiesta, nervioso, derritiéndose, angelito, diablillo, corazón roto |
| negocios | descuento (%), moneda, lluvia de billetes, gráfico de barras, tendencia al alza, gráfico circular, tarjeta de pago, megáfono, tienda, alcancía, cohete, ¡idea!, diana |
| llamadas | nota adhesiva, cinta adhesiva, bocadillo de grito, conversación, tarjeta de aviso, marco circular, bandera, pergamino, globo informativo |
| clima | tormenta, sol entre nubes, arcoíris, copo de nieve, viento, luna y estrellas, paraguas, mucho calor, flor que crece, pétalos de cerezo |
| transiciones | círculos, franjas diagonales, cuadros, corte dividido, onda líquida, estrella giratoria |
| fechas | árbol de Navidad, gorro navideño, esfera, campanas, medianoche, brindis, corazón flechado, carta de amor, calabaza, murciélago, fantasma, huevo de Pascua, diya, farol rojo, luna y farol, graduación, anillos de boda |
| comida | café humeante, pizza, hamburguesa, helado, dona, bebida con pajita, palomitas, sandía, tazón de fideos, cupcake |
| deportes | balón de fútbol, baloncesto, cronómetro, pesas, bandera de meta, podio, silbato, ritmo cardíaco |
| iconos | reloj, calendario, correo, descargar, engranajes, candado, reloj de arena, advertencia, batería, wifi, cuenta regresiva, notas musicales |

### Reglas que se añadieron
9. **Los detalles van antes que el fondo** dentro de una capa (la primera forma se dibuja encima); entre capas,
   la que se añade después queda arriba.
10. **Nada de «recortes» pintados con el color de la tarjeta** (`#1d1f27`): sobre un video se ven. Un agujero
    de verdad se hace con trazos gruesos (la dona) o con formas que no lo tapan.
11. Lo que aparece y desaparece en bucle va con `kit.cyclic` (si se pasa del final, una copia empieza antes del
    principio): así el bucle no tiene huecos.
12. Movimientos periódicos (flotar, mecerse, latir) con `kit.wave`/`bob`/`wobble`: el primer fotograma es igual al
    último.
13. Cuando una pieza escala o gira «desde su punta», el ancla (`a`) es esa punta y la posición (`p`) es donde
    queda la punta en pantalla (`p = origen de la capa + a`), si no salta al centro.

### Revisar sin la app
`py tools/animations/preview.py --module designs3 --sheet hoja.png [--strip 8]` dibuja una hoja de contacto con
QPainter (tarjetas o una tira de fotogramas por sticker). Coincide con lo que dibuja la app en lo que usamos; la
referencia sigue siendo la tarjeta que renderiza la app (`build.py`).

14. **Nada de trazos discontinuos (`d`)**: la app los dibujó como línea continua. Una línea punteada se hace con
    trazos sueltos (`kit.sample_curve` reparte puntos a igual distancia sobre la curva).
15. Los halos de luz con poca opacidad se ven barrosos sobre fondo oscuro: mejor rayos o nada.
