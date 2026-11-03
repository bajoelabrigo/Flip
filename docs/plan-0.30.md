# 0.30.0 — lo que va en la próxima versión (lista abierta, 2026-11-03)

Además de lo de `docs/plan-subtitulos.md` y `docs/plan-ejercicio-rebote.md`:

1. **Tooltip de «Editar en línea» en Inicio** (rama `flip/aviso-web`, sin compilar): unirla.
2. **Stock de la web con las subcategorías como en el escritorio** (Jorge, 2026-11-03). En el editor web
   (`flipstudio-app`, Stock) las subcategorías no están repartidas igual que en la app de escritorio. Es un arreglo, no
   una función nueva (la web está congelada salvo arreglos): comparar el árbol de Stock del escritorio
   (`StockHome.qml`, `StockPanel`) con `flipstudio-app/src/components/StockPanel.tsx` / `src/stock/stock.ts` y
   repartirlas igual. Probar en Chrome y en el celular.
3. **«Lower Thirds» en español** (Jorge, 2026-11-03): en Stock › Kit de YouTube la sección `lowerthirds` se llama
   «Lower Thirds» en todos los idiomas (`flipstudio-api/src/services/ytkit.ts`, decisión del 2026-10-30 de dejar el
   nombre del pack). Jorge quiere «Tercios inferiores». Ojo: ya existe la sección `tercios` con ese nombre; ver con
   Jorge cómo quedan las dos. Se arregla en el servidor (no necesita versión nueva) y se despliega.
