# CLAUDE.md — Flip Studio

Este archivo es el **mapa del proyecto**: dónde vive cada cosa, en qué estado está y las
trampas que ya nos costaron tiempo. Mantenerlo al día al cerrar cada versión.

**Regla de idioma:** todo lo que lee Jorge (respuestas, resúmenes, notas de versión,
descripciones de la Store, textos de la app) va en **español**. El código, los comentarios
y los mensajes de commit siguen el estilo del archivo que se toca — el código de Drift está
en inglés y no se traduce.

---

## Los cuatro repos

Todos en `C:\Users\bajoe\Downloads`.

| Repo | Qué es | Dónde se publica |
|---|---|---|
| `Flip` | App de escritorio (Qt/C++, fork de Drift) | GitHub `bajoelabrigo/Flip` — releases + Store |
| `flip-addons` | Recetas y empaquetador de los extras (privado) | Paquetes al release `packages` de `flipstudio-extras` |
| `flipstudio-web` | getflipstudio.com (privado) | VPS `holyvps` con `deploy/deploy.sh` |
| `flipstudio-app` | El editor web de `/editor/` (AGPL) | VPS, con su propio `deploy/deploy.sh` |

**Claves y secretos:** `Downloads\FlipStudio-secretos\addon-signing.key` (Ed25519, la
privada; la pública está en `Flip/src/engine/AddonSigningKey.h`). Nunca se commitea.

**Reglas que no cambian:**
- Los nombres internos de Drift (`drift::`, `DRIFT_*`, módulo QML `Drift`, `.drift`,
  `.driftfx`) **no se renombran**: así se pueden traer las mejoras de Drift.
- La clave de firma de Drift (`CutWire`) ya no se usa; los extras se firman con la nuestra.
- Lo de pago vive en servidores propios; las claves de API nunca dentro del `.exe`.
- Antes de publicar algo, compilarlo y probarlo en Windows.

---

## Estado (actualizado 2026-10-12)

**v0.9.2 PUBLICADA.** Release, tag, instalador y portable en GitHub; extras en vivo.

### Hecho
- `main` = `7e987` e incluye `flip/v0.9.2` (`b7014`) completo, tag `v0.9.2`, CI en verde.
- GitHub Release `v0.9.2` (Latest) con `FlipStudio-Setup-0.9.2-x64.exe`,
  `FlipStudio-Portable-0.9.2-x64.zip` y `SHA256SUMS`.
- **Índice de extras en vivo con 21 extras** (`getflipstudio.com/addons/index.json`).
  Los seis paquetes nuevos de modelos de video están subidos y verificados por hash.
- TXT `version.getflipstudio.com` = **0.9.2** (Jorge, 2026-10-12). El aviso de
  actualización dentro de la app ya funciona.
- MSIX de la 0.9.2 generado: `FlipStudio-Store\paquete-0.9.2\FlipStudio-0.9.2.0-x64.msix`.

### Pendiente
1. **Subir el MSIX a Partner Center.** Bloqueado por Jorge: la Store no acepta un envío
   nuevo mientras certifica el anterior. Es lo único que impide cerrar la versión.
2. **Desplegar el editor web.** `flipstudio-app` tiene el commit `28ccc` (velocidad,
   invertir, congelar fotograma, recortar, stickers y efectos de sonido) **commiteado y
   pusheado pero nunca compilado ni desplegado**: lo que sirve `/editor/` es el bundle
   viejo (mismo hash `index-RhO7mBu-.js`, build del 11/10 01:54). Hay que compilar y
   correr `flipstudio-app/deploy/deploy.sh`.
3. **Verificar a ojo, con la 0.9.2 instalada.** ✅ **"Recortar" verificado por Jorge el
   2026-10-12** (falta confirmar el retoque facial). Es la última milla que el arnés sin
   ventana no cubre (ver trampas).

### Dónde vive cada cosa en la interfaz (verificado en el código)

Cuesta encontrarlas porque **se crean en un panel y se editan en el otro**:

| Función | Se crea en | Se edita en |
|---|---|---|
| **Máscaras** (formas) | Panel de recursos, pestaña **"Máscaras"** (izquierda, ícono de máscara) — se aplican con clic a la selección o se arrastran sobre un clip | Panel de propiedades, pestaña **"Máscaras"** (derecha, grupo 2) |
| **Eliminar fondo** | Igual: **"Máscaras" → "Recortar sujeto…"** (SAM 2.1) o el recorte de personas (RVM, ~20 MB) | La máscara resultante queda como carril de ajuste propio |
| **Imagen o video como máscara** | **"Máscaras" → "Imagen o video como máscara…"** | Pestaña "Máscaras" |
| **Retoque facial** | Panel de recursos → **Efectos** (`face_retouch`, etc.), o el inspector del clip | Panel de propiedades → **Efectos** (ahí vive el escaneo de caras) |

Las máscaras también se pueden soltar **directamente sobre la línea de tiempo**
(`TimelinePanel.qml` llama a `addMaskToClip` / `addMaskLaneClip`).

### Gaps conocidos de las cuatro secciones de video (auditado contra CapCut)
- **Básico**: falta **flujo óptico** (interpolar fotogramas). Es render, no un modelo.
- **Máscara**: falta **texto como forma de máscara**.
- **Retoque**: falta **quitar imperfecciones** (manchas y arrugas).
- De nube de CapCut y no replicable: quitar objetos con IA, ampliar a 4K con IA, remix,
  contacto visual, sincronización labial.
- Ideas sin modelo todavía: separar audio (voz/música) y traductor de video.

---

## Rutina de publicación (lo que funcionó en la 0.9.2)

1. **Compilar y probar antes de etiquetar.** `gh workflow run build.yml --ref <rama> -f
   platforms=windows` para un ensayo; el tag es público en cuanto termina `release.yml`.
2. **Extras, en este orden y no en otro:** subir los `.driftpkg` al release `packages`
   **primero**, y solo después copiar `flip-addons/dist/index.json` a
   `flipstudio-web/addons/index.json` y desplegar. El índice apunta a las URLs de los
   paquetes: publicarlo antes deja 404 para todos.
3. **PR a `main`** (patrón de la casa: rama `flip/vX.Y.Z` → PR → merge).
4. **Tag `vX.Y.Z`** y push: `release.yml` se dispara solo, verifica que el tag coincida con
   `project(... VERSION ...)` de `CMakeLists.txt` y que exista `release-notes/<version>.md`,
   compila y publica el release.
5. **MSIX:** `gh workflow run msstore.yml --ref main -f ref=vX.Y.Z -f version=X.Y.Z.0`, y
   bajar el artefacto a `FlipStudio-Store\paquete-<version>\`.
6. **Jorge:** cambiar el TXT `version` en el DNS (Hostinger) y subir el MSIX a Partner
   Center. Recordar que el campo "Novedades de esta versión" tiene **límite de 1500
   caracteres**.

Los textos de la ficha de la Store están en `Flip/docs/store-listing.md` (hay que
actualizarlos en cada versión: la sección de notas todavía decía 0.8.1 al cerrar la 0.9.2).

---

## Pruebas

**Arnés sin ventana** (`Flip/tools/e2e/`, ver su README): `mcp_e2e.py` corre una lista de
llamadas JSONL contra `flipstudio.exe --headless --mcp-stdio` y guarda cada respuesta.
`calls_four.jsonl` es la comprobación de humo de las cuatro secciones de video.

- **Correrlo sin sandbox de archivos.** Los sidecars (mattes del recorte, `facetracks`)
  van a `%APPDATA%\Flip Studio\Flip Studio`, y bajo un sandbox de archivos `avio_open`
  falla con `Permission denied (error -13)`. Eso **no** significa que la función esté rota.
- **Mover `APPDATA` no sirve:** Windows resuelve esa carpeta por la API del shell, no por
  la variable de entorno.
- Los modelos no van dentro del ejecutable: `--stage` apunta a
  `flip-addons\build\stage` y exporta los `DRIFT_*_MODEL_DIR`.
- `sam2_full.py` reproduce el pipeline de SAM 2.1 entero en ONNX Runtime, sin la app: sirve
  para separar "el export está mal" de "la orquestación C++ está mal".

---

## Trampas que ya nos costaron tiempo

**Todo motor de ONNX Runtime tiene que armar sus sesiones con `drift::ort::buildSessions`,
nunca con `defaultSessionOptions` a mano.** `buildSessions` es lo que reintenta en el
procesador cuando el proveedor elegido no puede crear la sesión. SAM2 era el único que no
pasaba por ahí y su atención necesita 449 MiB contiguos, así que fallaba **en silencio** en
equipos donde todos los demás modelos funcionaban.

**Un trabajo asíncrono que falla no tiene dónde decirlo.** La operación responde `ok`, la
línea de tiempo no cambia y no hay campo de progreso que consultar. Por eso `inspect`
informa siempre `notice:{message,severity}` con la línea de estado de la app. Si una
operación asíncrona parece no haber hecho nada, **leer `notice` antes que nada**.

**`inspect` sin `clips:true` no emite `items`.** Un `tracks:[{clips:1}]` sin `items` es
normal, no un clip perdido. (Este error nos costó un diagnóstico equivocado.)

**Algo en el VPS revierte `index.json` si se reemplaza el archivo suelto.** Pasó con
`flipstudio-web/addons/index.json`: el `cp`/`install` se aplicaba y a la sesión siguiente
volvía el contenido viejo (mismo hash, misma fecha), mientras que otros archivos nuevos en
esa carpeta sí persistían. Lo que funciona es el **swap de directorio completo** que hace
`deploy/deploy.sh` (descomprimir al lado y `mv`). No se investigó la causa.

**`git add -A` en el repo de la app mete el portable extraído.** Hay `.e2e-app/` y
`FlipStudio-Portable-*.zip` en el `.gitignore`, pero conviene mirar `git status` antes de
commitear: una vez entraron 1854 archivos y hubo que reescribir el commit.

**`gh release upload` de paquetes grandes falla a la primera.** Reintentar
(`tools/e2e/upload_extras.ps1` lo hace hasta 4 veces).

**La subida por SSH:** `git push` falla si el credential helper de msys no puede crear sus
named pipes. Se resuelve con `gh auth token` en un `http.extraheader`, o usando `gh` para
las operaciones de GitHub.

**En Windows no hay WSL.** El `deploy.sh` de los sitios usa `tar | ssh`; desde PowerShell se
arma el tar con `tar.exe` y se sube con `scp`, y la mitad remota va en un `.sh` aparte
(`tools/e2e/deploy_remote.sh`).
