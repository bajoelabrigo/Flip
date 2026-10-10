# Flip Studio — hoja de ruta

Plan completo del proyecto, de la primera versión de escritorio a la suscripción. Se marca cada
casilla al terminarla. Última actualización: 2026-10-10.

**Datos clave**

| | |
|---|---|
| Repositorio | https://github.com/bajoelabrigo/Flip (fork de [Drift](https://github.com/CutWire-Studios/Drift), remoto `upstream`) |
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

### Pendiente
- [ ] **Separar el repo de la red de forks de Drift**: pedirlo en https://support.github.com ("detach fork" para `bajoelabrigo/Flip`). Conserva URL, Releases, issues y estrellas; el remoto `upstream` local sigue sirviendo para traer cambios de Drift. No recrear el repo (se perderían los Releases que usa el actualizador).
- [x] Probar el instalador nuevo en Windows (ícono, tema oscuro, panel de Medios, importar y **exportar** un video). — validado 2026-10-09 con el portable.
- [ ] Revisar el resto de la interfaz buscando "Drift" o fallos de diseño en español.
  - [x] Traducción al español completa (`es` y `es_CO`, 0 textos pendientes): menús, actualizador, cámara 3D, mejora con IA, los 33 estilos de texto y "Proyecto sin título" (2026-10-10).
  - [x] "Media bin" ya no es "papelera de medios" sino "biblioteca de medios"; "video" en lugar de "vídeo".
  - [x] Botones Recto / Suave / Salto de los fotogramas clave ya no se cortan ("R…", "Su…").
  - [ ] Revisarlo dentro de la app con la compilación de la v0.8.2.
- [x] Fusionar el PR #1 en `main`.
- [x] Publicar **v0.8.0** en GitHub Releases (`FlipStudio-Setup-0.8.0-x64.exe` + portable + `SHA256SUMS`) — 2026-10-09.
- [x] Actualizador probado de punta a punta: 0.8.0 → 0.8.1 desde la app (2026-10-10).
- [x] v0.8.1 preparada (rama `flip/v0.8.1`): claves cifradas, límites del MCP, acciones fijadas.
- [ ] v0.8.2 (rama `flip/v0.8.2`): interfaz en español completa, enlaces de soporte propios en la ventana de diagnóstico, nota de Flip Studio en `docs/`, carpeta de sesión MCP propia.
  - [x] Código listo; versión `0.8.2` en `CMakeLists.txt`, `CHANGELOG.md` y `release-notes/0.8.2.md`.
  - [ ] Compilar con **Actions → Build → windows** y probar el instalador (en curso).
  - [ ] Fusionar en `main`, etiqueta `v0.8.2` y TXT `version` → `0.8.2`.
  - [ ] Nuevo envío a la Microsoft Store con el MSIX `0.8.2.0`.
- [x] `release.yml` adaptado: publica solo en tus Releases (Windows), sin Homebrew ni Discord de CutWire. Notas en `release-notes/<versión>.md`.
- [ ] Ajustar `nightly.yml` o dejarlo desactivado (aún usa `drift-version.cutwire.org` y los IDs `org.cutwire.*.Nightly`).

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
- [ ] Alojarlos en **Cloudflare R2** (sin coste por descarga; el modelo de subtítulos pesa unos 470 MB).
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

## Fase 5 — Versión web (React)

- [ ] Proyecto Vite + React + TypeScript (`app.getflipstudio.com`).
- [ ] Reproducción y decodificación con **WebCodecs**; composición con **WebGL/WebGPU**.
- [ ] Reutilizar de Drift: shaders de `effects/` y `transitions/`, audio en WebAssembly (`wasm/`), presets JSON.
- [ ] Etapas: importar y reproducir → timeline con cortes → texto → exportar MP4 → efectos y transiciones → audio.
- [ ] Mismo formato de proyecto que la versión de escritorio.
- [ ] Enlace visible al código fuente (obligatorio por AGPL al reutilizar código de Drift).
- [ ] Probar en Chrome, Edge, Safari y Firefox (WebCodecs varía entre navegadores).

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
| Alta | Separar el repo de la red de forks de Drift | GitHub Support |
| Alta | Publicar v0.8.2 | `flip/v0.8.2` |
| Media | Firma de add-ons con clave propia (hoy solo acepta las de CutWire) | `src/engine/AddonPackage.*` |
| Media | Textos de servicios de CutWire todavía visibles ("Flip Studio Assets", librería de sonidos) | `src/models/DriftAssetStore.*`, `SfxLibrary.*` |
| Media | `nightly.yml` y `playstore-aab.yml` usan dominios e IDs de CutWire (`release.yml` y `msstore.yml` ya adaptados) | `.github/workflows/` |
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
