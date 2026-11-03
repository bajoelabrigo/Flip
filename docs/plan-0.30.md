# 0.30.0 — lo que va en la próxima versión (lista abierta, 2026-11-03)

Además de lo de `docs/plan-subtitulos.md` y `docs/plan-ejercicio-rebote.md`:

1. **Tooltip de «Editar en línea» en Inicio** (rama `flip/aviso-web`, sin compilar): unirla.
2. **Stock de la web con las subcategorías como en el escritorio** (Jorge, 2026-11-03). En el editor web
   (`flipstudio-app`, Stock) las subcategorías no están repartidas igual que en la app de escritorio. Es un arreglo, no
   una función nueva (la web está congelada salvo arreglos): comparar el árbol de Stock del escritorio
   (`StockHome.qml`, `StockPanel`) con `flipstudio-app/src/components/StockPanel.tsx` / `src/stock/stock.ts` y
   repartirlas igual. Probar en Chrome y en el celular.
3. **«Lower Thirds» en español — HECHO (2026-11-03).** Jorge eligió unir las dos secciones: el pack `lowerthirds`
   va dentro de «Tercios inferiores» (`sectionOf` en `flipstudio-api/src/services/ytkit.ts`, rama `traduccion`,
   desplegado). Comprobado en la app de escritorio: ya no hay chip «Lower Thirds» y los del pack salen con los demás.
