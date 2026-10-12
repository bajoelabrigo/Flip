# Flip Studio — hoja de ruta

Plan completo del proyecto, de la primera versión de escritorio a la suscripción. Se marca cada
casilla al terminarla. Última actualización: 2026-10-11.

**Datos clave**

| | |
|---|---|
| Repositorio | https://github.com/bajoelabrigo/Flip (repo propio desde el 2026-10-10; basado en [Drift](https://github.com/CutWire-Studios/Drift), remoto `upstream`) |
| Código local | `C:\Users\bajoe\Downloads\Flip` |
| Dominio | `getflipstudio.com` (Hostinger, DNS en Hostinger) |
| Servidor | VPS de Hostinger (el mismo de Holy App: nginx + PM2 + certbot) |
| Licencia | GPLv3 (incluye JUCE bajo AGPLv3) — el código de la app es siempre público |
| ID de la app | `io.github.bajoelabrigo.FlipStudio` · ejecutable `flipstudio.exe` |

**Reglas que no cambian**

- Lo de pago vive en **servidores propios** (IA, nube, contenido premium), nunca bloqueado dentro de la app.
- Las claves de API (Pexels, PayPal, ElevenLabs…) van **solo en el servidor**, jamás dentro del `.exe`.
- Los nombres internos de Drift (`drift::`, `DRIFT_*`, módulo QML `Drift`, `.drift`, `.driftfx`) **no se renombran**: así se pueden traer las mejoras de Drift.
- La palabra "Flip" a secas es un verbo en Drift ("Flip horizontally" = Voltear): nunca reemplazarla en bloque.
- Antes de publicar algo, compilarlo y probarlo en Windows.

---

## Qué sigue

Dónde estamos: la app de escritorio va por la **v0.9.2** (en la rama `flip/v0.9.2`, compilada y con las
pruebas en verde, **sin publicar**: espera el visto bueno de Jorge) y el **editor web** está publicado y
anunciado (etapa 6, audio por clip, hecha). La 0.9.1 ya se subió a la Microsoft Store y va después de que
la certifiquen.

### App de escritorio (Windows)
1. ~~v0.8.2 y v0.8.3~~ — publicadas (2026-10-10).
   - Las compilaciones de escritorio se lanzan cuando hay varios cambios juntos, no por cada uno.
2. ~~**v0.9.0 — extras propios, texto y subtítulos**~~ (2026-10-10):
   - Clave de firma propia (Ed25519; la privada en `Downloads\FlipStudio-secretos`, con copia de seguridad).
     Repo privado `bajoelabrigo/flip-addons` con el empaquetador y las recetas; los paquetes se descargan del
     release `packages` del repo público [`bajoelabrigo/flipstudio-extras`](https://github.com/bajoelabrigo/flipstudio-extras);
     índice en `getflipstudio.com/addons/index.json`.
   - 11 extras: subtítulos (Whisper small y medium), sincronización por palabra (wav2vec2 español), motor de IA,
     aceleración WebGPU (experimental), 104 fuentes, 52 plantillas de texto, 150 emojis 3D y 67 stickers animados.
   - Texto y subtítulos: selector de fuentes, importar fuentes, plantillas combinadas, estilo antes de generar,
     cortes naturales, limpieza, diccionario, buscar y reemplazar, emojis, traducción al inglés, `*resaltar*`.
   - Línea de tiempo y vista previa al estilo CapCut (dividir, borrar izquierda/derecha, herramientas según el
     clip, zoom y relación de aspecto).
   - Pruebas de punta a punta sin ventana (`flipstudio.exe --headless --mcp-stdio`): el arnés vive ahora en
     `tools/e2e/` (`mcp_e2e.py` corre una lista de llamadas JSONL y guarda cada respuesta; `sam2_full.py`
     reproduce el pipeline de SAM2 entero en ONNX Runtime sin la app). La aceleración WebGPU apenas ayuda con
     Whisper int8 (63 s contra 69 s en 45 s de video); Whisper medium int8 en procesador es tan rápido como
     small fp16 y más preciso.
3. ~~**v0.9.1**~~ (2026-10-11): inicio como CapCut, quitar silencios y muletillas a partir de la transcripción,
   efectos de sonido propios (sintetizados), más stickers y plantillas. Falta subir el MSIX a la Store cuando
   certifiquen la 0.9.0.
4. **v0.9.2 — sincronización con Drift, voz con IA y PDF** (rama `flip/v0.9.2`, sin publicar):
   - Primera sincronización con Drift (69 cambios): texto con SkParagraph, enlazar clips, clips PDF, recorte,
     fuentes del sistema y voz con Chatterbox.
   - Pestaña Audio como la de CapCut (Básico y Modificador de voz con 116 voces) y los extras "Voz con IA",
     "Visor de PDF" y "Modificador de voz".
   - **Herramientas de video al estilo CapCut**: Básico (`adjust_*`: brillo, contraste, saturación,
     temperatura, tono, gamma), Eliminar fondo (recorte de sujeto SAM 2.1 o RVM sobre `set_background`),
     Máscara (formas y máscaras de imagen en la pestaña Máscaras) y Retoque (`face_retouch` con suavizar,
     afinar, ojos, labial, rubor; más `face_fat_slim`, `face_big_eyes` y props). Los desenfoques
     (`gaussian_blur`, `stylize_blur`, `depth_of_field`) y la iluminación 3D (`depth_relight`, `depth_fog`)
     cubren el resto del panel de CapCut.
   - **Seis paquetes nuevos de modelos** (flip-addons/modelos.py), todos redistribuibles: Recorte de sujeto
     (SAM 2.1 tiny), Quitar fondo de personas (RVM MobileNetV3), Retoque de rostro (MediaPipe Face Mesh +
     YuNet), Iluminación 3D y profundidad (Video Depth Anything Small), Mejorar la calidad (GaterV3, NomosUni
     2x/4x, Nomos8k 4x) y Reducir el ruido (DeepFilterNet3).
   - **Arreglo del recorte de sujeto**: SAM2 era el único motor que no pasaba por `buildSessions`, así que no
     reintentaba en el procesador cuando el proveedor de GPU no podía crear su sesión (su atención necesita
     449 MiB contiguos). Fallaba en silencio; ahora `inspect` además informa `notice` con la línea de estado
     de la app, que es donde los trabajos asíncronos dejan su error.
   - Para publicar: fusionar la rama en `main`, etiqueta `v0.9.2`, release de GitHub e instalador; subir los
     seis paquetes nuevos al release `packages` de `flipstudio-extras` y copiar `dist/index.json` al índice
     en vivo; Jorge cambia el TXT `version` y sube el MSIX más nuevo a la Store.
5. **Stock de Pexels (3.2)**: requiere el backend `api.getflipstudio.com`, que también servirá para las cuentas (Fase 6).
6. **Firma de código** del instalador cuando haya presupuesto (quita el aviso de SmartScreen en la descarga directa).
7. Más adelante: Linux, Android y macOS (Fase 4).
8. **Ideas de tu flujo de edición** (`Videos\Videos_Claude`, Remotion): ~~cortar silencios automáticamente,
   quitar muletillas a partir de la transcripción~~ (0.9.1), reencuadre 16:9 → 9:16 siguiendo la cara,
   subtítulos con palabras resaltadas y normalizar el audio a -14 LUFS. Revisar cuáles ya trae Drift
   antes de construirlas.
9. **Ideas pendientes del panel de CapCut** (2026-10-11): separar audio (voz y música) y traductor de videos;
   las dos necesitan modelos que todavía no tenemos.

### Editor web (getflipstudio.com/editor)
1. ~~**Etapa 5a — transiciones**~~: las 28 de Drift con WebGL2, en vista previa y exportación (publicada el 2026-10-10).
2. **Rediseño igual al escritorio** (decidido el 2026-10-10, va antes de los efectos):
   - ~~**R1 — distribución**~~ (publicada el 2026-10-10; faltan la forma de onda y el botón "Video"): barra de íconos a la izquierda con la biblioteca, vista previa, inspector con
     su propia barra de íconos a la derecha, encabezado y barra de la línea de tiempo como en escritorio,
     y la vista previa a la derecha para videos verticales. Mismos íconos, colores y nombres.
   - ~~**R2 — pistas libres**~~ (publicada el 2026-10-10): Video 1, Video 2, Gráfico 1, Texto 1, Audio 1… con los clips donde los
     sueltes, ojo y silencio por pista, forma de onda, imán y "+" para añadir pistas. Las transiciones
     van entre clips seguidos de una misma pista. Los proyectos guardados se convierten solos.
   - ~~**R3 — inspector**~~ (2026-10-10): General, Transformar y Animación, como en escritorio.
   - ~~**Barra como CapCut**~~ (2026-10-10): Dividir, Borrar izquierda/derecha (Q/W), más espacio; en la vista
     previa, zoom (Completa a 400 %) y Relación (16:9, 9:16, 1:1, 4:5, 4:3, 21:9).
3. ~~**Etapa 5b — efectos**~~ (2026-10-10): pestaña Efectos con 10 filtros tipo CapCut y brillo, contraste,
   saturación y desenfoque (filtro de canvas, igual en vista previa y exportación). Pendiente: más efectos de
   Drift (glitch, viñeta, etc.) con shaders.
   - ~~**Textos**~~ (2026-10-10): 29 fuentes propias con selector por categoría y 15 plantillas nuevas (Fe, Redes,
     Subtítulos virales, Ventas, Frases).
4. ~~**Etapa 6 — audio**~~: volumen y fundidos por clip, pista de música, silenciar el audio de un video.
5. **Probar en Edge, Firefox y Safari** (y en el celular) antes de anunciarlo.
6. ~~**Anunciarlo**~~: botón "Editar en línea" en la web y sin `noindex`.
7. **Igual al escritorio** (siguiente): velocidad, recorte, congelar, invertir, stickers y efectos de sonido, escritos desde cero.
8. Después: abrir y guardar proyectos en el formato de la app de escritorio.

---

## Fase 0 — Auditoría y fork ✅

- [x] Auditoría de seguridad del código de Drift (sin malware ni telemetría).
- [x] Revisión de licencia: se puede modificar, vender y publicar como GPL.
- [x] Fork `bajoelabrigo/Flip` con `upstream` hacia Drift.
- [x] GitHub Actions activado en el fork; desactivados los workflows que usan cuentas de CutWire.

## Fase 1 — Flip Studio para Windows

### Hecho
- [x] Nombre **Flip Studio**, ID propio, `flipstudio.exe`, carpeta de datos `%APPDATA%\Flip Studio`.
- [x] Textos visibles y 16 traducciones con el nuevo nombre.
- [x] Instalador de Windows con AppId propio (no choca con Drift instalado).
- [x] "Acerca de" con crédito a Drift / CutWire Studios y enlace al código fuente (GPL).
- [x] Servicios de CutWire desconectados (add-ons, marketplace, versión).
- [x] Arreglo: ZIP truncado colgaba la app + límite contra "bombas ZIP" + test.
- [x] Dominio `getflipstudio.com` y registro DNS `TXT version → 0.8.0`.
- [x] Actualizador apuntando a `version.getflipstudio.com` + GitHub Releases.
- [x] Ícono propio (Windows, Store, Linux, Android). Logo fuente en `resources/branding/`.
- [x] Tema oscuro por defecto.
- [x] Pantalla de inicio con "Flip Studio".
- [x] Panel de Medios: botones que se montaban en paneles angostos.
- [x] Tests en CI: 15/15 en Linux y macOS.
- [x] Versión portable para probar sin instalar; caché de compilación (ccache) en el CI de Windows.

### Hecho después (2026-10-10)
- [x] **Repo separado de la red de forks de Drift** (2026-10-10, *Settings → Leave fork network*). Se conservaron el código, las etiquetas, los Releases y Actions; se perdieron las páginas de los PR #1–#3 (sus commits siguen en `main`). Copia de los Releases en `C:\Users\bajoe\Downloads\FlipStudio-backup-releases`. El remoto `upstream` local sigue sirviendo para traer cambios de Drift; `gh repo set-default bajoelabrigo/Flip` hecho en la copia local.
- [x] Probar el instalador nuevo en Windows (ícono, tema oscuro, panel de Medios, importar y **exportar** un video). — validado 2026-10-09 con el portable.
- [x] Revisar el resto de la interfaz buscando "Drift" o fallos de diseño en español.
  - [x] Traducción al español completa (`es` y `es_CO`, 0 textos pendientes): menús, actualizador, cámara 3D, mejora con IA, los 33 estilos de texto y "Proyecto sin título" (2026-10-10).
  - [x] "Media bin" ya no es "papelera de medios" sino "biblioteca de medios"; "video" en lugar de "vídeo".
  - [x] Botones Recto / Suave / Salto de los fotogramas clave ya no se cortan ("R…", "Su…").
  - [x] Revisado dentro de la app con el portable de la v0.8.2: todo en español.
- [x] Fusionar el PR #1 en `main`.
- [x] Publicar **v0.8.0** en GitHub Releases (`FlipStudio-Setup-0.8.0-x64.exe` + portable + `SHA256SUMS`) — 2026-10-09.
- [x] Actualizador probado de punta a punta: 0.8.0 → 0.8.1 desde la app (2026-10-10).
- [x] v0.8.1 preparada (rama `flip/v0.8.1`): claves cifradas, límites del MCP, acciones fijadas.
- [x] **v0.8.2** publicada el 2026-10-10 (PR #3): interfaz en español completa, enlaces de soporte propios en la ventana de diagnóstico, nota de Flip Studio en `docs/`, carpeta de sesión MCP propia.
  - [x] Código listo; versión `0.8.2` en `CMakeLists.txt`, `CHANGELOG.md` y `release-notes/0.8.2.md`.
  - [x] Compilada con **Actions → Build → windows** y probada con el portable.
  - [x] Fusionada en `main`, etiqueta `v0.8.2`, GitHub Release y TXT `version` → `0.8.2`.
  - [x] Microsoft Store: MSIX `0.8.2.0` certificado y publicado el 2026-10-10 (paquete en `C:\Users\bajoe\Downloads\FlipStudio-Store\paquete`).
- [x] `release.yml` adaptado: publica solo en tus Releases (Windows), sin Homebrew ni Discord de CutWire. Notas en `release-notes/<versión>.md`.
- [x] `nightly.yml` sin uso: GitHub lo dejó desactivado (`disabled_fork`) y no se puede ejecutar salvo que alguien lo active; aun así se salta las ejecuciones programadas fuera del repo de CutWire. Se deja sin tocar para no complicar los merges con Drift.

## Fase 2 — Distribución en Windows

- [x] **Microsoft Store** — publicada el 2026-10-10 (v0.8.1.0): https://apps.microsoft.com/detail/9NZZJ9MRGT0B
  - [x] Nombre "Flip Studio" reservado (Store ID `9NZZJ9MRGT0B`, identidad `yitoweb.FlipStudio`).
  - [x] `AppxManifest.xml` y `msstore.yml` con la identidad de la cuenta; MSIX generado con **Actions → Microsoft Store MSIX** (`ref` = etiqueta de la versión).
  - [x] Ficha en español, español (Colombia) e inglés; 3 capturas; clasificación IARC 3+ / ESRB E.
  - [x] Botón "Obtener en Microsoft Store" en la web (opción principal) y en el README.
  - [ ] Repetir el cuestionario IARC cuando se activen stock, cuentas o suscripción.
  - Cada versión nueva: subir el número MSIX (`A.B.C.0`), generar el paquete y crear un envío nuevo en Partner Center.
- [ ] **Firma de código** del instalador `.exe` para quitar el aviso de SmartScreen (certificado OV/EV o Azure Trusted Signing). La Store firma su propio paquete, así que esto solo hace falta para la descarga directa.
- [x] Web de `getflipstudio.com` hecha (`C:\Users\bajoe\Downloads\flipstudio-web`, repo privado https://github.com/bajoelabrigo/flipstudio-web): inicio, descarga automática de la última versión, preguntas, privacidad y términos. Se publica con `deploy/deploy.sh`.
- [x] Captura real de la app en la web; textos legales bajo ley peruana (Ley 29733).
- [x] DNS `A @ → 145.223.27.84`, publicada en el VPS y con HTTPS: https://getflipstudio.com (2026-10-09). Rediseño con recorrido interactivo y hoja de ruta.
- [x] Correo de soporte `soporte@getflipstudio.com`.
- [x] Sección "El editor" con 4 capturas reales y tarjetas al estilo CapCut: cambian la imagen al pasar el mouse y rotan solas (2026-10-10).

## Fase 3 — Infraestructura propia básica

### 3.1 Add-ons: fuentes, stickers y modelos de subtítulos
- [ ] Crear tu propia **clave de firma Ed25519** y sustituir la clave pública de CutWire en `src/engine/AddonPackage.*` (hoy los add-ons solo validan firmas de CutWire).
- [ ] Usar el empaquetador del repo público `CutWire-Studios/Drift-Addons` (GPL) para generar los `.driftpkg`.
- [ ] Revisar la licencia de cada contenido (fuentes OFL, Whisper MIT, stickers) antes de redistribuirlo.
- [ ] Alojarlos como archivos de un **GitHub Release** (por ejemplo, en un repo `flipstudio-addons`): gratis, hasta 2 GB por archivo, y ya se usa para los instaladores; el modelo de subtítulos pesa unos 470 MB. **Cloudflare R2** (sin coste por descarga, 10 GB gratis) solo si hace falta limitar quién descarga, como contenido Pro. No hace falta cuenta de Cloudflare hasta entonces (decidido el 2026-10-10).
- [ ] Publicar el índice y configurar `DRIFT_ADDON_INDEX_URL` / `DRIFT_ADDON_CLIENT_TOKEN` en `CMakeLists.txt`.
- [ ] Cambiar los textos "Flip Studio team" de la firma cuando la clave sea tuya.

### 3.2 Marketplace de stock (Pexels / Pixabay)
- [ ] Backend `flipstudio-api` en el VPS: proceso PM2 aparte, subdominio `api.getflipstudio.com`, nginx + certbot (con las cabeceras `Upgrade` y `X-Forwarded-For` que ya aprendimos en Holy App).
- [ ] Implementar el contrato de `docs/marketplace/openapi.yaml` usando la clave de Pexels **en el servidor**.
- [ ] Configurar `DRIFT_MARKET_API_URL` / `DRIFT_MARKET_CLIENT_KEY`.
- [ ] Decidir si se mantienen "Drift Assets" y la librería de efectos de sonido (servicios de CutWire) o se reemplazan por contenido propio.

### 3.3 Mantenimiento con Drift
- [ ] Rutina mensual: `git fetch upstream && git merge upstream/main`, resolver conflictos, regenerar traducciones, compilar y probar.
- Regenerar traducciones sin compilar la app: instalar `lupdate` de Qt 6.10.3 (`pip install aqtinstall`, luego `aqt install-qt windows desktop 6.10.3 win64_msvc2022_64 --archives qtbase qttools qtdeclarative`) y ejecutar `lupdate -no-obsolete -locations none -extensions cpp,h,qml,js,mm src -ts i18n/drift.ts i18n/drift_*.ts`. Da el mismo resultado que el test `Translations` del CI.

## Fase 4 — Otras plataformas

- [ ] **Linux**: AppImage desde Releases; Flatpak con ID propio (renombrar `flatpak/org.cutwire.Drift.*` y sus íconos).
- [ ] **Android**:
  - [ ] ID de paquete propio (hoy `org.cutwire.drift` en los workflows y `build-android.sh`).
  - [ ] Rehabilitar `android.yml` con tus secretos de firma.
  - [ ] Google Play: cuenta de desarrollador, ficha, política de privacidad.
  - [ ] Splash screen con el logo (`scripts/gen-android-icons.sh` apunta a un archivo que no existe).
- [ ] **macOS**: ícono propio (`resources/macos/Drift.icon` y `Drift.icns`), firma y notarización de Apple (cuenta de desarrollador, 99 USD/año), Homebrew tap propio.

## Modelo de licencias (decidido el 2026-10-11)

Modelo mixto: la app de escritorio sigue siendo software libre (GPL-3.0, como Drift, del que deriva);
lo que es 100 % de Flip Studio es propio:

- **Editor web**: código cerrado desde el 2026-10-11 (repo privado). Ya no contiene código de Drift:
  transiciones, animaciones y estilos de texto propios. Las versiones anteriores siguen bajo AGPL-3.0.
- **Extras propios** (efectos de sonido, plantillas de texto, stickers): *Licencia de contenido Flip
  Studio* desde esa fecha (uso libre en videos, también comerciales; prohibido redistribuirlos). Los
  paquetes publicados antes como CC0 siguen CC0.
- **Herramientas de los extras** (`flip-addons`): privadas.
- Pendiente del dueño: registrar la marca "Flip Studio" y el logo en INDECOPI.

## Fase 5 — Versión web (React)

- [x] Proyecto Vite + React + TypeScript, repo `bajoelabrigo/flipstudio-app` (`C:\Users\bajoe\Downloads\flipstudio-app`) — 2026-10-10; privado y de código cerrado desde el 2026-10-11.
- [x] Publicado en https://getflipstudio.com/editor/ (sin anunciar: `noindex` y sin enlace desde la web) con `deploy/deploy.sh` del repo del editor; nginx lo sirve desde `/var/www/flipstudio-app/editor` con su propio snippet (2026-10-10).
- [x] Anunciado (2026-10-11): botón "Editar en línea" en la web, sin `noindex` y en el mapa del sitio.
- [ ] Reproducción y decodificación con **WebCodecs**; composición con **WebGL/WebGPU**.
  - [x] Etapa 1: importar (botón y arrastrar), análisis de MP4/MOV con mp4box.js + WebCodecs, miniaturas desde los fotogramas clave, vista previa en lienzo con audio y avance por fotograma, línea de tiempo con cabezal. WebM y MKV usan el reproductor del navegador.
  - [x] Etapa 2: pista principal magnética con varios clips (añadir con +, doble clic o arrastrando), dividir, recortar los bordes, reordenar, deshacer/rehacer, zoom; la vista previa reproduce la secuencia preparando el siguiente clip. 10 pruebas con Vitest en el CI.
  - [x] Guardado automático del proyecto en el navegador (IndexedDB); en Chrome/Edge se recuerda el acceso a los archivos y "Recuperar archivos" los vuelve a abrir; si falta uno, se enlaza al importarlo de nuevo.
  - [x] Etapa 3: pista de texto con carriles; 11 estilos de escritorio (tipografías, contornos, sombras, brillos, degradados, caja, palabra destacada) con animaciones por texto, palabra o letra; edición en el panel y arrastre sobre la vista previa. Tipografías de Google Fonts (OFL) alojadas en el propio servidor.
  - [x] Etapa 4: exportar a MP4 en el navegador (H.264 + AAC con WebCodecs, vía Mediabunny MPL-2.0): resolución original o 720p, calidad alta o normal, progreso y cancelar; en Chrome/Edge se escribe directo al disco. Corrige además la orientación de los videos de celular (rotación del MP4). Verificado con ffprobe: imagen, textos y audio de cada clip en su sitio.
  - [ ] Etapa 5a: transiciones. Motor de composición en **WebGL2** compartido por la vista previa y la exportación; las 28 transiciones de `transitions/` (GLSL 330 → GLSL ES 3.00, solo cambia la cabecera); en cada corte, un botón para elegir transición y duración.
  - [ ] Etapa 5b: efectos. Pestaña "Efectos" para aplicarlos al clip seleccionado (se pueden apilar) y sus parámetros en el panel derecho. Entran unos 45 de los 64 de `effects/`; quedan fuera los que necesitan IA (caras, profundidad), el ritmo del audio (`beat_shake`) o fotogramas anteriores (`motion_trail`, `time_echo`).
  - [ ] Etapa 6: audio (volumen y fundidos por clip, pista de música, silenciar el audio de un video; más adelante, el motor de audio de Drift en WebAssembly).
- [ ] Reutilizar de Drift: shaders de `effects/` y `transitions/`, audio en WebAssembly (`wasm/`), presets JSON.
- [ ] Mismo formato de proyecto que la versión de escritorio.
- [x] Enlace visible al código fuente (obligatorio por AGPL al reutilizar código de Drift): botón "Código fuente" y pie de página.
- [ ] Probar en Chrome, Edge, Safari y Firefox (WebCodecs varía entre navegadores). Hasta ahora solo se ha probado en Chrome.
- [ ] Pendientes conocidos: la pista de texto se ve bien hasta 3 carriles; un corte a otro punto del mismo video puede tener una pausa mínima en la vista previa; solo un proyecto a la vez.

## Fase 6 — Cuentas y nube (todavía gratis)

- [ ] Base de datos **propia** en MongoDB Atlas (no mezclar con `chatapp` de Holy App).
- [ ] Login con Google + JWT (reutilizar el patrón de Holy App).
- [ ] Login desde el escritorio: la app abre el navegador y recibe el token.
- [ ] Proyectos en la nube: originales en Cloudflare R2; miniaturas y vistas previas en Cloudinary.
- [ ] Sincronización escritorio ↔ web.
- [ ] Métricas de uso **respetuosas** (opt-in) para saber qué funciones valen la pena cobrar.
- [ ] Límites gratuitos para controlar costes (minutos de IA y GB por usuario).

## Fase 7 — Suscripción (Flip Studio Pro)

- [ ] Plan Pro en PayPal (reutilizar `paypalService` de Holy App: `/v1/billing/subscriptions` + webhooks).
- [ ] Funciones Pro en el servidor: subtítulos e IA en la nube, voces, quitar fondo, exportación en servidor, almacenamiento extra, plantillas y música premium.
- [ ] La IA pesada va por APIs externas (OpenAI Whisper, ElevenLabs, Replicate): el VPS no tiene GPU.
- [ ] **Reglas de las tiendas**:
  - Microsoft Store: permite cobrar con tu propio sistema de pagos en apps que no son juegos.
  - Google Play: por regla general las suscripciones digitales deben usar **Google Play Billing** (comisión del 15 % en suscripciones). Algunos países permiten pagos alternativos; revisar la política vigente antes de lanzar. Por defecto, no usar PayPal dentro de la app Android.
  - Web y descarga directa: PayPal sin restricciones.
- [ ] Facturación e impuestos según tu país.
- [ ] Mantener un plan gratuito generoso.

---

## Correcciones conocidas (por prioridad)

| Prioridad | Qué | Dónde |
|---|---|---|
| Media | Firma de add-ons con clave propia (hoy solo acepta las de CutWire) | `src/engine/AddonPackage.*` |
| Media | Textos de servicios de CutWire todavía visibles ("Flip Studio Assets", librería de sonidos) | `src/models/DriftAssetStore.*`, `SfxLibrary.*` |
| Media | `playstore-aab.yml` usa el paquete de Android de CutWire (`release.yml` y `msstore.yml` ya adaptados; `nightly.yml` desactivado) | `.github/workflows/` |
| Media | Firma de código del `.exe` (aviso de SmartScreen) | Instalador |
| Baja | Ícono de macOS | `resources/macos/` |
| Baja | IDs de Flatpak y Android | `flatpak/`, workflows |
| Baja | Capturas de pantalla del README | `docs/screenshots/` |

## Cómo publicar una versión nueva

1. Subir la versión en `CMakeLists.txt` (`project(Drift VERSION x.y.z ...)`) y anotar los cambios en `CHANGELOG.md`.
2. Compilar con **Actions → Build → windows** y probar el instalador.
3. Escribir `release-notes/X.Y.Z.md`, fusionar en `main` y crear la etiqueta: `git tag vX.Y.Z && git push origin vX.Y.Z`. El workflow **Release** compila y publica el instalador, el portable y `SHA256SUMS`.
4. En Hostinger → DNS de `getflipstudio.com`, cambiar el TXT `version` a `X.Y.Z`.
5. Las apps instaladas ofrecerán la actualización en menos de un día.
6. Microsoft Store: **Actions → Microsoft Store MSIX** con `ref` = `vX.Y.Z` (genera `FlipStudio-X.Y.Z.0-x64.msix`). En Partner Center → Flip Studio → **Iniciar actualización** → Paquetes: subir el nuevo y quitar el anterior → (opcional) "Novedades de esta versión" en cada idioma → **Enviar a la Store**.
