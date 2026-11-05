# 0.31.0 — lista abierta (desde el 2026-11-05)

Pedidos de Jorge después de publicar la 0.30.0. Nada empezado todavía: Jorge dijo «eso lo vamos a hacer en la
próxima, solo para que anotes».

## Arreglos

1. **Panel de la izquierda: bajar por las tarjetas salta a la subcategoría siguiente** (Jorge, 2026-11-05).
   En el árbol de recursos (Efectos, Títulos, Stock…), al ir bajando por las tarjetas de una subcategoría, la lista
   no sigue a la tarjeta siguiente de ese mismo submenú: cambia de una vez a la subcategoría siguiente. No va «de
   chip en chip» sino que salta de subcategoría.
   - Reproducir primero en ventana con la rueda del mouse y con el teclado (flechas), en varias pestañas.
   - Sospechas: la rueda al final de la lista que cambia de categoría (`AssetsPanel.qml` `treeRows`, la rueda entre
     categorías), o el seguimiento de la subcategoría visible que mueve la selección al hacer scroll.
   - Lo esperado: bajar recorre todas las tarjetas de la subcategoría elegida; para pasar a otra, se elige en el árbol.

2. **Squash & Stretch: al marcar claves con el mouse se cierra el ajuste** (Jorge, 2026-11-05).
   Tras crear una animación con Squash & Stretch, quiso editar su ajuste (por ejemplo borrar claves): al marcarlas
   (arrastrar para elegir) y soltar el mouse, el panel del ajuste se cerraba y no dejaba eliminarlas.
   - Archivo: `src/qml/components/properties/SquashStretchPanel.qml` (y el panel que lo contiene).
   - Probable: soltar el arrastre de selección cambia la selección o rehace el inspector (`notifyTracksChanged`
     dentro del arrastre; ver la trampa de `emitPreviewEdit` en `CLAUDE.md`), o el clic llega a la capa de abajo.
   - Lo esperado: marcar varias claves, soltar, y que sigan elegidas con el panel abierto para borrarlas con Supr
     o moverlas.

## Para seguir
- Rama nueva desde `main` (la 0.30.0 ya está en `main`, tag `v0.30.0`).
- Probar cada arreglo en ventana antes de compilar la versión (regla de `CLAUDE.md`).
