# Historia de Flip Studio

Bloques que salieron de `CLAUDE.md` por espacio (2026-10-17). Se conservan tal cual: sirven
para entender por qué el código está como está, no como instrucciones del día a día.

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
- **Pedido de Jorge (2026-10-13), para hacerlo junto con el login y Pexels:** contar **descargas,
  máquinas instaladas y actualizaciones instaladas**.
  - **Descargas:** ya se pueden leer.
    - GitHub da `download_count` por archivo del release (`gh api repos/bajoelabrigo/Flip/releases`).
      Al 2026-10-13 eran de 0 a 3 por versión, casi todas nuestras pruebas.
    - La Store tiene sus análisis en Partner Center.
    - Los registros de nginx del VPS cuentan los clics en «Descargar» de la web.
    - GitHub no separa instalación nueva de actualización: las dos bajan el mismo archivo.
  - **Máquinas y actualizaciones:** la app tiene que avisar a `api.getflipstudio.com` con un
    identificador **aleatorio y anónimo** (nada de la persona ni del equipo):
    - al instalarse (versión, Windows);
    - al actualizarse (de qué versión a cuál);
    - y como mucho una vez al día «sigo en uso», para contar las activas por día y por mes.
  - Con eso, un panel con instalaciones, activas, versiones en uso y actualizaciones aplicadas.
  - **Pendiente de Jorge:** confirmar «anónimo» y un interruptor «Enviar estadísticas anónimas» en
    Ajustes, activado por defecto. Hay que actualizar la política de privacidad y la declaración de
    la Store **antes** de publicarlo.

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


---

### 0.9.7 en curso (2026-10-13)
- Rama `flip/v0.9.7`, PR #12 en borrador; versión 0.9.7 en `CMakeLists.txt`; notas en
  `release-notes/0.9.7.md`.
- Los 14 puntos que encontró Jorge están hechos y probados en ventana con el portable de CI.
- **Falta:**
  - el OK de Jorge;
  - merge, tag y release;
  - el MSIX, después de que la Store apruebe la 0.9.6;
  - las notas de la Store para la 0.9.7.
- **Editor web:** rama `web/jorge-0.9.7` en `flipstudio-app`, probada en Chrome y **sin desplegar**.
  Incluye:
  - menú «⋯» de audio;
  - fotos en la pista de video;
  - pista nueva al arrastrar;
  - máscara de texto;
  - temas de color;
  - paso de sección con la rueda;
  - la escala fija al arrastrar (antes el clip salía disparado).
- **Segunda tanda (2026-10-13, tarde)**, también en la web:
  - fotos y videos en cualquier pista que no sea de audio;
  - candado de pista;
  - en los catálogos, la rueda pasa a la siguiente categoría;
  - Video › Máscara como en CapCut, con la pluma que agrega y borra puntos;
  - Retoque con fotos;
  - iconos en las acciones;
  - menú de la flecha con Seleccionar, Dividir y Seleccionar hacia la izquierda o la derecha;
  - Quitar fondo y Recortar para fotos en la barra.

  Las miniaturas de Retoque las renderiza la propia app (`resources/retouch/README.md`; la foto es CC0).
- **Tercera tanda (2026-10-13, tarde)**, también en la web:
  - fundido automático al montar el borde de un clip sobre otro, como en Sony Vegas
    (`AppController::autoCrossfadeFor`, solo con «Permitir superposición» apagado);
  - capa de ajuste en la barra por defecto; la web estrena las suyas (clip con `adjust: true`,
    `drawAdjustment` en `render/compose.ts`);
  - agrupar en la web (Ctrl+clic y Ctrl+G, por `link`);
  - archivos que faltan como en Premiere: marca «Falta el archivo», «Buscar archivo perdido…» y
    el diálogo al abrir (`MediaBinController::relinkMissing` / `relinkMissingInFolder`,
    `MissingMediaDialog.qml`; en la web, `MissingMediaDialog.tsx`).
  - En escritorio ya había agrupar: «Crear compuesto», «Transformar juntos» (Ctrl+G) y «Vincular».
- Jorge pidió (2026-10-13) probar todo y, si funcionaba, **publicarlo todo**.
- **Jorge tiene el espacio de trabajo fijado en «Horizontal»** (`ui/workspaceLayout`). Por eso un
  video 9:16 no cambiaba de diseño solo; ahora sale el botón «Espacio vertical».


---

### 0.9.8 PUBLICADA (2026-10-13, noche): capas de ajuste profesionales y LUT
- Rama `flip/v0.9.8` (escritorio) y `web/0.9.8` (editor web). Notas en `release-notes/0.9.8.md`.
- Jorge pidió (con dos documentos) capas de ajuste "profesionales" y un sistema de LUT, **por etapas**,
  **probando cada cambio** y **compilando el escritorio una sola vez al final**.
- Hecho, en las dos:
  - capa de ajuste con interruptor (`Clip::disabled` / `off` en la web), nombre, intensidad animable,
    mezcla y aviso cuando no cambia nada; «Luz suave» en escritorio;
  - Blancos, Negros y Desvanecer en `color.basic` / `adjust_basic`; números que se escriben;
  - LUT: `core/CubeLut` + efecto `effects/color_lut` (la textura sale del parámetro de archivo:
    `GpuEffectTextureSpec::fromParameter`, `lutTexture` en `GlRuntime`); biblioteca en
    `AppData/luts`; búsqueda por nombre (`CubeLut::resolve`); seis looks generados por
    `tools/luts/make_luts.py` (también copiados a `flipstudio-app/public/luts`).
    Web: `effects/cubeLut.ts`, `lutStore.ts` (IndexedDB `flipstudio-luts`, clave por contenido),
    textura 3D en `gl.ts`;
  - grano de película y viñeta ajustable (escritorio); la web ya los tenía;
  - el panel derecho, al bajar, recorre las páginas de la pestaña antes de la siguiente.
- **Máscaras de capa** (tercer documento de Jorge): `Mask::expand`/`opacity` (animables),
  `MaskShape::LinearGradient` ("gradient"), `Clip::extraMasks` + `maskFocus` (la máscara enfocada es
  la que editan el panel, el visor y "mask.<key>"), `Clip::masksLimitEffects` (las máscaras de un clip
  limitan sus efectos: `buildLayerTarget` mezcla por cobertura en vez de recortar). Web: `Clip.masks`
  (pila), `masksLimitEffects`, `MaskHandles.tsx` en el visor.
- Probado en ventana con el portable de CI (run 38464105571) y por píxeles con capturas reales.
- **Publicada** a pedido de Jorge («publica»): PR #13, tag `v0.9.8`, editor web desplegado (`flipstudio-app`
  `main` = `web/0.9.8`), novedades 0.9.8 en la web y la portada con `assets/shot-flip-text.webp` (Jorge no quiere
  su foto en la portada). Notas de la Store en `docs/store-listing.md`. **Falta:** el MSIX, cuando la Store apruebe.
- Segunda tanda del mismo día:
  - capa de ajuste desde el **+** (`NewTrackMenu`) y con clic derecho sobre foto, video o texto;
  - Texto (panel izquierdo) con `CategoryScrollOn`, y la rueda espera a que pare tras cada cambio (`settling`);
  - Ajustar › Máscara con `MaskShapeTiles.qml` (compartido con Video › Máscara).
- **Auditoría de «Crear composición»:** es una secuencia anidada (un solo nivel, instancias compartidas). Antes y
  después, deshacer, rehacer, guardar y reabrir, y exportar con y sin composición dan lo mismo al píxel. Se corrigió
  dónde queda: ocupa el lugar de la pista más baja de la selección y quita las pistas que deja vacías.
- **Para la 0.9.9:** traducir «Tipo: composite» en General (sale en inglés).
- **Límites conocidos:** en la web los parámetros de los efectos no se animan (solo la intensidad de
  la capa); los LUT importados en la web viven en ese navegador (se reconocen al volver a importar el
  mismo archivo).

