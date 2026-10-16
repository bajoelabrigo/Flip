# Animaciones propias de Stock — guía (investigación del 2026-10-15)

Pedido de Jorge: **al menos 50**, mirando las mejores. Hechas por nosotros (Lottie solo con formas),
así son nuestras sin problemas de licencia. LottieFiles **no** se integra (su licencia prohíbe
recopilar su catálogo); solo un botón que abre su web.

## Categorías (id de categoría)
celebracion · resaltar · flechas · formas · redes · emociones · negocios · llamadas · clima · transiciones

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
