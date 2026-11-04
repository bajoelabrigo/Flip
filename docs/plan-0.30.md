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
6. **Clonar y copiar/pegar con Rebote (Jorge, 2026-11-04, noche) — ARREGLADO, FALTA PROBAR EN VENTANA.** Jorge: Motion
   Tools › Clonar y Ctrl+C/Ctrl+V «copian el fotograma pero no la animación». Probado en ventana con la r15: con
   Separar dimensiones X e Y se copian y clonan por separado **como en After Effects** (Jorge lo pidió así: no
   juntarlas). Clonar las claves de Y sí repite la caída. Lo que fallaba es el **Rebote/Elástico**: el motor solo
   rebota donde el valor se queda quieto (`KeyframeTrack::settleOffset`) y con la copia detrás la pelota subía
   despacio hacia ella sin rebotar. Arreglo (`pasteKeyframes`, commit «Clone and paste keys keep Bounce and
   Elastic»): en una propiedad con Rebote/Elástico se pone una clave quieta (el valor del suelo) un fotograma antes de
   la copia. Prueba en `pasteOntoItsOwnKeysCarriesOn`. (Un primer intento que juntaba X con Y y copiaba toda la
   animación con una sola clave se deshizo: commit «Revert …».) En la ventana de Jorge las claves clonadas eran de
   la fila Posición X, que no se mueve: hay que elegir las de Y (clic en el nombre «Posición Y» elige todas).
   Compilación **r16**: run 41798607082 → `pruebas\FlipStudio-0.30-r16`.

## Para seguir (2026-11-05)

1. Bajar la r16 si no se bajó (`gh run download 41798607082 -R bajoelabrigo/Flip -n windows-portable`), abrirla en
   ventana: pelota (elipse arriba, Separar dimensiones, claves de Y en 0 s y 1 s, Rebote), clonar en 3 s y mirar que
   rebote en la primera caída y en la copia; también Ctrl+C/Ctrl+V. Que Jorge lo pruebe.
2. Si queda bien: PR de `flip/subtitulos` a `main` (el PR #52 ya está unido; este es uno nuevo con el arreglo),
   **tag `v0.30.0`** otra vez (se borró: el release se canceló antes de publicarse, no hay release `v0.30.0`),
   esperar `release.yml`, MSIX (`msstore.yml` con `ref=v0.30.0`, `version=0.30.0.0`) a
   `tienda\FlipStudio-Store\paquete-0.30.0`, copia en `versiones\FlipStudio-0.30.0`.
3. Web: `flipstudio-web` commit `80cca` (novedades 0.30 + índice de extras con `voces.ia` y `traduccion.local`) está
   hecho **sin desplegar**: desplegar con `deploy/deploy.sh` después del release. Añadir a las novedades el arreglo
   del rebote si hace falta (las notas de la versión ya cubren el Kit de YouTube).
4. Notas: añadir a `release-notes/0.30.0.md` › Arreglos «Clonar y pegar claves conservan el Rebote y el Elástico».
5. Stock del kit sin fondo y los dos extras **ya están subidos** (no repetir).
