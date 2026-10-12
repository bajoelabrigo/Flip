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

## Estado (actualizado 2026-10-12, noche)

**v0.9.3 PUBLICADA.** Release, tag, instalador y portable en GitHub; extras al día.

### Hecho
- `main` = `cfdb0`, tiene todo lo de la 0.9.3 y **0 commits de diferencia con `flip/v0.9.2`**.
  Tag `v0.9.3`. CI y build de Windows en verde; el portable se ejecutó y aplica efectos.
- GitHub Release `v0.9.3` (Latest) con `FlipStudio-Setup-0.9.3-x64.exe` (109 MB, hash
  verificado), `FlipStudio-Portable-0.9.3-x64.zip` y `SHA256SUMS`. El instalador está copiado
  en `Downloads\FlipStudio-0.9.3\`.
- **Índice de extras en vivo con 21 extras** (`getflipstudio.com/addons/index.json`). La 0.9.3 no
  trae paquetes nuevos: los seis de modelos de video entraron en la 0.9.2.
- **El panel de video quedó con las cuatro páginas de CapCut** (Básico, Eliminar fondo, Máscara,
  Retoque) en `src/qml/components/properties/VideoInspector.qml`.
- **Los efectos se pueden recortar** (`independentRange`), **las máscaras se ven con el clip
  seleccionado** (`linkedMaskClips`) y hay **39 transiciones** (10 nuevas, categoría `modern`).
- MSIX de la 0.9.3 generado: `FlipStudio-Store\paquete-0.9.3\FlipStudio-0.9.3.0-x64.msix`.

### Pendiente
1. ~~TXT `version` del DNS a `0.9.3`~~ — **hecho por Jorge el 2026-10-12**. Propagando: Google
   (8.8.8.8) ya devolvía `0.9.3` mientras Cloudflare (1.1.1.1) seguía con `0.9.2` en caché (el
   registro tiene TTL largo, unas 4 h). No es un fallo.
2. **Subir el MSIX 0.9.3 a Partner Center.** Bloqueado por Jorge: la Store no acepta un envío nuevo
   mientras certifica el anterior.
3. **Desplegar el editor web** — pero **Jorge lo está trabajando con Claude en otra sesión**:
   no tocar `flipstudio-app` ni desplegarlo desde aquí.
4. **Verificar a ojo la 0.9.3**: las cuatro páginas del panel de video, que un efecto recortado se
   quede recortado, y las transiciones nuevas. De la 0.9.2 Jorge ya verificó el "Recortar".

---

## Lo que avanzamos el 2026-10-12

Sesión larga. Resumen de lo que se cerró, por si mañana hay que retomar el hilo:

**Se arregló el recorte de sujeto (SAM 2.1).** Era el único motor que armaba sus sesiones de ONNX
Runtime con `defaultSessionOptions` en vez de `buildSessions`, así que nunca reintentaba en el
procesador cuando el proveedor de GPU no podía crear la sesión (su atención necesita 449 MiB
contiguos). Fallaba **en silencio**. Se comprobó por partes: el export ONNX es correcto (el
pipeline completo en ONNX Runtime da máscaras que siguen a la cara, iou 0.95 en la semilla y 0.987
al propagar).

**Los fallos asíncronos ya no se esconden.** `inspect` informa `notice:{message,severity}` con la
línea de estado de la app. Fue justo eso lo que dejó ver el fallo del recorte.

**Los seis paquetes de modelos de IA se publicaron** (recorte de sujeto, quitar fondo de personas,
retoque de rostro, iluminación 3D y profundidad, mejorar la calidad y reducir el ruido), con el
índice en vivo. Se subieron a mano con reintentos porque `gh release upload` falla a la primera con
archivos grandes.

**Los efectos dejaron de ser una propiedad del clip.** `syncLinkedAdjustments()` los re-estiraba a
la duración completa del clip en cada edición, así que recortar un efecto se deshacía solo. Ahora
el ajuste lleva `independentRange`.

**Las máscaras se ven al seleccionar el clip** (`linkedMaskClips`), en vez de obligar a saber
seleccionar su carril de ajuste.

**Diez transiciones nuevas** (39 en total), con la categoría `modern`: deslizar en los cuatro
sentidos, girar, disolución con desenfoque, doblez, deslizamiento con onda, barrido de cristal,
barrido orgánico y papel desgarrado.

**El panel de video se rehizo en las cuatro páginas de CapCut** (`VideoInspector.qml`), reutilizando
los inspectores que ya existían.

**Se publicaron la 0.9.2 y la 0.9.3**, cada una con su release, instalador, portable y MSIX.

**Arnés de pruebas sin ventana** en `tools/e2e/`, con `sam2_full.py` para reproducir el pipeline de
SAM 2.1 fuera de la app y separar "el export está mal" de "la orquestación C++ está mal".

### Lo que quedó mal o a medias (no perderlo de vista)

- **El panel de video salió en inglés** según Jorge. La investigación apunta a que el catálogo sí
  está bien y él esté abriendo una copia anterior al build bueno; ver la sección de arriba.
- **La página Retoque no sigue las capturas**: Jorge espera grupos **Rostro / Cuerpo / Cabello**,
  **Estilos automáticos**, **Piel**, **Funciones** y **Maquillaje**; hoy es una lista plana de 8
  botones.
- **No se verificó a ojo nada de la 0.9.3** (ni el panel, ni el recorte de efectos, ni las
  transiciones): en esta máquina no hay compilador de C++ local, así que todo se validó por CI y
  por el ejecutable corriendo, no viendo la pantalla.
- **Calidad de transiciones viejas**: `radial_zoom_blur` tiene su "strength" fijo en el shader y el
  parámetro no se lee; `liquid_smudge` tiene 3 parámetros muertos y `particle_wind` uno.
- Las diez transiciones nuevas **no tienen `preview_strip.png`** (es opcional).

---

## Mañana (2026-10-13): usuarios, instalaciones y Pexels

Plan acordado con Jorge. **Los tres son backend**: necesitan `api.getflipstudio.com`, que ya está
en la hoja de ruta como requisito de Pexels y de las cuentas.

### 1. Cuentas de usuario — solo con Google

- **Único proveedor: Google.** Nada de correo/contraseña. Eso simplifica: no hay que guardar
  contraseñas ni gestionar recuperación.
- Hace falta **OAuth 2.0 con Google** (ID de cliente, pantalla de consentimiento) y, del lado de
  la app, un flujo de escritorio: **PKCE con redirect a `http://127.0.0.1:<puerto>` y el navegador
  del sistema**, no un WebView embebido (Google lo rechaza).
- La app guarda el **token de refresco** y lo usa contra el backend propio; el backend valida el
  `id_token` de Google y emite su propia sesión.
- **Decisión pendiente de Jorge:** qué se gana con la cuenta. Hoy la app es libre y sin cuenta, así
  que hay que definir qué desbloquea (¿sincronizar proyectos?, ¿los extras de pago?) y qué pasa si
  alguien no quiere cuenta.

### 2. Saber quién instala la app

- Es lo que Jorge pidió: **control de quién instala**.
- **OJO, esto choca con lo que la ficha de la Store declara hoy.** En
  `docs/store-listing.md` está escrito: *"no recoge datos personales, no contiene publicidad, no
  tiene compras dentro de la aplicación"*. Un identificador de instalación que se envíe al servidor
  ya es telemetría, y si se ata a la cuenta de Google pasa a ser dato personal.
- **Antes de programarlo hay que decidir:**
  - ¿Se cuenta la instalación **de forma anónima** (un identificador aleatorio que no se puede
    atar a una persona), o **atada a la cuenta**?
  - ¿Se avisa en la app y se actualiza la **política de privacidad** y la declaración de la Store?
    Si se recoge algo, la declaración **tiene** que cambiar: una ficha que dice que no se recoge
    nada y una app que sí lo hace es un problema con Microsoft, no un detalle.
- Lo primero, entonces, es un identificador anónimo de instalación y actualizar la declaración;
  atarlo a la cuenta es una decisión de producto, no un detalle técnico.

### 3. Pexels (stock de video y fotos)

- Ya estaba en la hoja de ruta: **requiere el backend** porque **la clave de API nunca va dentro
  del `.exe`** (es una regla que no cambia). La app le pide al backend, el backend firma con la
  clave y devuelve los resultados.
- Hay que decidir dónde se guarda lo descargado y si cuenta contra la cuota de Pexels por usuario
  o global.
- **Ojo con la licencia de Pexels**: permite uso gratis, pero no revender ni redistribuir el
  material como stock; conviene leerlo antes de exponerlo como herramienta.

### Orden sugerido

1. **Levantar `api.getflipstudio.com`** con HTTPS y una base mínima: es el bloqueante de los tres.
2. **El identificador anónimo de instalación** (lo más pequeño, y obliga a resolver la parte
   legal de la ficha).
3. **Pexels**, que solo necesita la clave en el servidor.
4. **Las cuentas de Google**, que son las que más piezas tienen (OAuth, PKCE, sesión, refresco).


---

## El panel de video salió en inglés: qué se sabe (2026-10-12)

> **RESUELTO (2026-10-12, tarde): la causa era la carga, no el catálogo.** El instalador real
> de la 0.9.3 (mismo hash que el portable del release) muestra el fallo. En un sistema es-PE,
> `QTranslator::load(locale, "drift", ...)` cargaba **`drift_es_CO.qm`**, que tiene la pestaña
> Video sin terminar: por eso salían en español justo "Quitar fondo", "Máscara" e "Imagen o video
> como máscara…" (las únicas con texto en `es_CO`). Arreglo en
> `PreferencesController::installUiTranslators()`: el catálogo base del idioma (`drift_es`) se
> instala siempre, y uno regional solo encima si coincide el territorio o la escritura exactos.
> Lo de abajo es la investigación previa, que daba por bueno el catálogo y no miraba qué archivo
> se cargaba.

Jorge reportó que en la 0.9.3 las páginas del panel de video salen en inglés y solo "Máscara" en
español. **La investigación no encontró un fallo en el catálogo**, y esto es lo comprobado:

- `i18n/drift_es.ts` tiene las cuatro **traducidas**: Basic→Básico, Remove background→Eliminar
  fondo, Mask→Máscara, Retouch→Retoque, y también todos los títulos de sección (Skin retouch→
  Retoque de piel, Bigger eyes→Ojos más grandes…).
- `lrelease` sobre ese `.ts` da **4296 traducidas y 0 sin terminar**, y el `.qm` resultante se
  vuelve a volcar con `lconvert` y contiene las cuatro.
- El log del build que publicó la 0.9.3 (`38215230650`) dice:
  `drift_es.qm … Generated 4296 translation(s) (4296 finished and 0 unfinished)`.

O sea: **el `.qm` que se publicó sí lleva las traducciones**. La causa más probable es que Jorge
esté abriendo una copia anterior a ese build (el portable de prueba que le pasé antes de la
0.9.3), o que su app no esté cargando el catálogo español. Su sistema es es-PE y no tiene idioma
forzado en el registro (`HKCU\Software\Flip Studio\Flip Studio` no tiene `ui/language`), así que
debería cargar `drift_es.qm` desde `:/i18n`.

**Para la próxima actualización:**
1. **Confirmar con el instalador 0.9.3 real** (el `.exe` del release, no un portable viejo) antes
   de tocar nada. Si ahí sigue en inglés, entonces el problema está en la carga, no en el catálogo.
2. **Alinear la página Retoque con las capturas de Jorge**: él espera grupos **Rostro / Cuerpo /
   Cabello**, **Estilos automáticos**, **Piel**, **Funciones** y **Maquillaje**. Hoy la página es
   una lista plana de 8 botones con otros nombres (Skin retouch, Body reshape…). Traducirlos está
   bien, pero los **nombres y la agrupación** no son los de CapCut.
3. "Body reshape" debería ser **"Cuerpo"** para coincidir con la captura (hoy dice "Reformar el
   cuerpo").
4. La página **Básico** no incluye **Flujo óptico** (gap ya conocido: es render, no un modelo).

### Comprobar los catálogos sin depender de CI

En Windows no hay `lupdate`, así que el ciclo es: bajar un Qt desechable y correrlo a mano.

```powershell
# 1. lupdate/lrelease (una vez; .qttools/ y .qtmingw/ están en .gitignore)
py -m pip install aqtinstall
py -m aqt install-qt windows desktop 6.10.3 win64_mingw --archives MinGW qttools qtbase qtdeclarative -O .qtmingw

# 2. Regenerar los catálogos tras añadir qsTr (y NO editar un .ts a mano: lupdate tiene que
#    reproducirlo byte a byte o el test Translations falla en los 17 idiomas)
.\.qtmingw\6.10.3\mingw_64\bin\lupdate.exe src i18n -no-obsolete -locations none -ts (gci i18n\drift*.ts).FullName

# 3. Comprobar que quedó estable (dos pasadas iguales) y ver qué traduce de verdad
.\.qtmingw\6.10.3\mingw_64\bin\lrelease.exe i18n\drift_es.ts -qm .qmcheck\drift_es.qm
.\.qtmingw\6.10.3\mingw_64\bin\lconvert.exe -i .qmcheck\drift_es.qm -o .qmcheck\dump.ts
```

**Trampa que costó dos ciclos de CI:** editar un `.ts` a mano (o con un script de reemplazo) puede
dejar el archivo en una forma que `lupdate` no reproduce, y entonces el test Translations falla
aunque el contenido se vea correcto. El orden es: `lupdate` primero, después rellenar
traducciones, después `lupdate` otra vez para confirmar que no cambia nada.

### Dónde vive cada cosa en la interfaz (verificado en el código)

Cuesta encontrarlas porque **se crean en un panel y se editan en el otro**:

| Función | Se crea en | Se edita en |
|---|---|---|
| **Las cuatro páginas de video** | Pestaña **Video** del panel de la derecha (sale con un clip de video seleccionado) | Ahí mismo: Básico, Eliminar fondo, Máscara y Retoque |
| **Máscaras** (formas) | Pestaña **Video → Máscara**, o el panel de recursos → "Máscaras"; también se arrastran sobre el clip | Pestaña **Máscaras** del panel de la derecha |
| **Eliminar fondo** | Pestaña **Video → Eliminar fondo** | La máscara resultante queda como carril de ajuste propio |
| **Retoque facial** | Pestaña **Video → Retoque** | Ahí, más el escaneo de caras en Efectos |
| **Imagen o video como máscara** | **"Máscaras" → "Imagen o video como máscara…"** | Pestaña "Máscaras" |

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
