# 0.30.0 — lo que va en la próxima versión (lista abierta, 2026-11-03)

Además de lo de `docs/plan-subtitulos.md` y `docs/plan-ejercicio-rebote.md`:

1. **Tooltip de «Editar en línea» en Inicio** — HECHO: `flip/aviso-web` ya está dentro de `flip/subtitulos`.
2. **Stock de la web con las subcategorías como en el escritorio** (Jorge, 2026-11-03). En el editor web
   (`flipstudio-app`, Stock) las subcategorías no están repartidas igual que en la app de escritorio. Es un arreglo, no
   una función nueva (la web está congelada salvo arreglos): comparar el árbol de Stock del escritorio
   (`StockHome.qml`, `StockPanel`) con `flipstudio-app/src/components/StockPanel.tsx` / `src/stock/stock.ts` y
   repartirlas igual. Probar en Chrome y en el celular.
3. **«Lower Thirds» en español — HECHO (2026-11-03).** Jorge eligió unir las dos secciones: el pack `lowerthirds`
   va dentro de «Tercios inferiores» (`sectionOf` en `flipstudio-api/src/services/ytkit.ts`, rama `traduccion`,
   desplegado). Comprobado en la app de escritorio: ya no hay chip «Lower Thirds» y los del pack salen con los demás.
4. **Kit de YouTube sin fondo y a la medida de un Short — HECHO y SUBIDO a Stock (2026-11-04).** Jorge: los tercios
   venían con fondo y en 1920×1080, y en un Short el texto salía chico. Se quitó el fondo «Tu video» de 187
   plantillas del kit (`photo_bg` en `templates_llt_*`, `templates_lt_*` y `templates_ytkit*`; las transiciones
   conservan sus dos escenas y «Suscríbete en la página» su video enmarcado). En una línea de tiempo vacía cualquier
   plantilla del kit (salvo transiciones) pregunta «¿Para qué es el video?» Short/Video; en otra forma se ajusta con
   `fitOverlayLayout` (tercios y `kit:tercios` abajo; lo demás con su tamaño según el lado corto y su lugar, dentro
   de la zona libre de un Short; los fondos a pantalla completa la siguen cubriendo). Probado en ventana con la r15
   (tercio en Short desde vacío, botón y título en un Short armado, barra en horizontal). Render: 273 + 37 sin
   errores; subidas 310 con `publish.py` + `publish_delta.py` + `apply_delta.sh` (hashes comprobados en vivo).
5. **Extras `voces.ia` 1.0.0 (40 voces, retratos aprobados por Jorge el 2026-11-04) y `traduccion.local` 1.0.0:**
   paquetes subidos al release `packages`. **Falta:** copiar `flip-addons/dist/index.json` a la web al publicar la 0.30.
