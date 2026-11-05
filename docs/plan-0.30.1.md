# 0.30.1 — arreglos (PUBLICADA el 2026-11-05: PR #55, tag v0.30.1, release run 41992980133, MSIX run 41993039969)

Pedidos de Jorge después de publicar la 0.30.0. Jorge (2026-11-05): «esto debe entrar como versión 0.30.1 porque es
una corrección, no son novedades». Rama `flip/v0.30.1` (salida de `flip/subtitulos`, que ya está en `main`).
Versión 0.30.1 en `CMakeLists.txt`, notas en `release-notes/0.30.1.md`.

## Arreglos

1. **Stock: la rueda saltaba al tipo siguiente** (Jorge: «no pasa de chip a chip»). HECHO en código (sin probar en ventana).
   - Causa: `CategoryScrollOn` de `StockBrowser.qml` recorría los tipos (Plantillas → Música…), no las categorías del tipo
     abierto (el tercer nivel del árbol, `categoryChips`).
   - Ahora la lista de pasos es: las categorías del tipo abierto, una por una (`chip:<id>`), y después los demás tipos
     (`kind:<id>`).
   - Probar: Stock › Plantillas › Intros, bajar con la rueda hasta el final y seguir: tiene que pasar a la categoría
     siguiente del árbol, y tras la última al tipo siguiente.

2. **Squash & Stretch: marcar sus claves cerraba el ajuste**. Reproducido en la 0.30 (ventana) y HECHO en código.
   - Causa: Squash crea una capa de ajuste «Squash & Stretch» enlazada al texto. Con ella elegida, el recuadro marcaba
     claves del texto y `KeyframeKeyTools.selectPickedClips` cambiaba la selección al texto: el panel «Capa de ajuste»
     se cerraba y las filas pasaban al gráfico.
   - Ahora, si la capa de ajuste elegida está enlazada al clip de esas claves, la selección no cambia
     (`heldByAdjustment`, `selectKeyOwner`, también al hacer clic en una clave). Supr borra las claves elegidas primero.
   - Probar: aplicar Squash a un texto, elegir la barra «Squash & Stretch», marcar claves con un recuadro, soltar, Supr.

3. **Gráfico de velocidad como el de After Effects** (Jorge, con capturas de AE: tiradores muy grandes; al mover uno
   cambiaban las otras claves). Comprobado en la 0.30: con una clave elegida cambia solo esa; con varias elegidas el
   tirador se copiaba en todas (`otherPicked` en `speedDrag`). HECHO en código:
   - el tirador cambia solo su clave en el gráfico de velocidad (en el de valores sigue igual);
   - tiradores: punto amarillo de 6 px y línea amarilla de 1 px (`handleYellow`), solo en las claves elegidas;
   - claves como cuadraditos de 7 px (amarillas al elegirlas) en los dos gráficos; las filas conservan sus rombos;
   - la curva de velocidad en gris claro y fina, solo entre la primera y la última clave; fuera, línea punteada en 0;
     en la última clave baja recta a 0 (como AE);
   - eje con números redondos y margen arriba (`speedStep`, `speedAxisTop`) y unidades px/s, °/s, %/s (`speedUnit`).

## Para seguir
- Compilación de Windows de la rama: run 41981190349. Bajarla a `E:\FlipStudio\pruebas\FlipStudio-0.30.1-r1`
  y probar los tres puntos en ventana (copia del registro en `E:\FlipStudio\pruebas\v031\registro-antes.reg`).
- Si todo está bien: PR a `main`, tag `v0.30.1`, release, MSIX (`version=0.30.1.0`), novedades en la web, notas de la
  Store (0.30.1).
