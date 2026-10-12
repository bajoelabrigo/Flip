# Flip Studio — cambios propios

Flip Studio es un fork de Drift. Esta sección lista lo que Flip Studio cambia respecto a Drift; debajo sigue el
registro heredado de Drift.

## 0.9.4 — Retoque como en CapCut y el español completo

- `PreferencesController::installUiTranslators()` instala siempre el catálogo base del idioma
  (`drift_es.qm`) y uno regional solo encima, cuando coincide territorio o escritura. Antes
  con "Español (Colombia)" elegido (la única opción latinoamericana del selector) la app cargaba
  solo `drift_es_CO.qm`, que tenía la pestaña Video sin terminar, y la mostraba medio en inglés.
- La página Retoque de `VideoInspector.qml` pasa a Rostro / Cuerpo / Cabello con Estilos
  automáticos, Piel, Funciones y Maquillaje. Casi todo son ajustes de `face_retouch` que
  reutilizan el que ya lleva el clip.
- `AssetCategoryChips` reparte las categorías en filas (como Texto) y las pliega con un chevron;
  los grupos de emojis la usan también.
- `HoverPop` anima stickers y emojis bajo el ratón; `image://lottie`
  (`LottiePreviewImageProvider`) reproduce los stickers animados en su tarjeta.
- Transiciones: `fold` dibujaba el entrante siempre encima y `glass_wipe` mezclaba al revés.
  Las once nuevas tienen `preview_strip.png`, generadas con `tools/transitions/make_strips.py`.

## 0.9.3 — el panel de video como el de CapCut

- El panel de video se ordena en las cuatro pestañas de CapCut (**Básico**, **Eliminar fondo**,
  **Máscara**, **Retoque**) dentro de una sola pestaña "Video" (`VideoInspector.qml`). Cada página
  reutiliza los inspectores que ya existían en vez de duplicarlos: Básico compone
  TransformInspector, BlendingInspector, StabilizeInspector y EffectsInspector; Eliminar fondo
  ofrece la segmentación automática y la personalizada; Máscara las formas y `MasksInspector`;
  Retoque los efectos de rostro con sus parámetros.
  - Los clips de video declaran `videoTools` y `adj:videoEffects`, que es lo que hace aparecer la
    pestaña y permite aplicar un efecto al clip aunque viva en su carril de ajuste.
  - `VideoInspector.qml` tiene que estar en la lista `QML_FILES` de CMakeLists: sin eso no se
    compila y lupdate no ve sus cadenas, y el test de traducciones falla en los 17 idiomas con el
    contexto vacío.
- **Los efectos se pueden recortar.** `syncLinkedAdjustments()` re-estiraba cada ajuste fijado a
  la duración completa de su clip en cada edición, así que recortar un efecto se deshacía solo.
  Ahora el ajuste lleva `independentRange`, que se activa al recortarlo o moverlo por primera vez
  y desde entonces lo deja en paz.
- **Máscaras a la derecha**: la pestaña Máscaras sale también con el clip de video seleccionado y
  lista las máscaras que lleva (`linkedMaskClips()`), porque las máscaras viven en ajustes y antes
  había que saber seleccionar ese carril.
- **Diez transiciones nuevas** (39 en total), con la categoría `modern`: deslizar en los cuatro
  sentidos, girar, disolución con desenfoque, doblez, deslizamiento con onda, barrido de cristal,
  barrido orgánico y papel desgarrado. Se generan con `tools/transitions/make_transitions.py`.

## 0.9.2 — sincronización con Drift, voz con IA y PDF

- Primera sincronización con Drift (69 cambios): texto con SkParagraph (emojis de color, árabe y
  hebreo, edición sobre la vista previa), enlazar clips, clips PDF, recorte de imagen y video, fuentes
  del sistema en el selector y voz con Chatterbox.
- Windows: Skia usa DirectWrite; elegía el gestor de fuentes de Android, que no encuentra ninguna, y el
  texto sin el paquete de fuentes no se dibujaba.
- Se conservan el resaltado `*palabra*`, el selector de fuentes propio (ahora con las del sistema), las
  herramientas de subtítulos, la barra tipo CapCut y la pestaña de efectos de sonido.
- Pestaña Audio como la de CapCut: Básico (fundidos solo del sonido con `setClipAudioFade`,
  normalizar a −14 LUFS según ITU-R BS.1770 con `normalizeClipLoudness`, mejorar voz, completar canal
  con el procesador nuevo `channelfill`) y Modificador de voz (`VoiceChanger.qml`, `setVoiceFilter`):
  las voces son los efectos `voz.*` del extra "Modificador de voz" (flip-addons/voces.py, 116 voces
  hechas con los pedales del motor).
- Extras propios nuevos: "Voz con IA" (`voz.chatterbox`, decodificador exportado con
  flip-addons/tts_export.py) y "Visor de PDF" (`pdfium`, PDFium chromium/8066).
- Paquetes nuevos de modelos de IA (flip-addons/modelos.py): "Recorte de sujeto" (SAM 2.1 tiny),
  "Quitar fondo (personas)" (RVM MobileNetV3), "Retoque de rostro" (MediaPipe Face Mesh + YuNet),
  "Iluminación 3D y profundidad" (Video Depth Anything Small), "Mejorar la calidad" (4 modelos de
  Philip Hofmann) y "Reducir el ruido" (DeepFilterNet3). Todos redistribuibles (Apache-2.0, MIT,
  GPL-3.0 o CC BY 4.0) y verificados por hash contra las recetas de Drift.
- Arreglo del recorte de sujeto con SAM 2.1: era el único motor que armaba sus sesiones de ONNX
  Runtime sin pasar por `buildSessions`, así que nunca reintentaba en el procesador cuando el
  proveedor elegido solo no podía crear una sesión. La atención de SAM2 necesita una matriz de
  449 MiB en el mismo espacio de memoria, y con el proveedor de GPU la sesión no se creaba: el
  recorte fallaba en silencio (la operación respondía `ok` y el clip quedaba igual). Igual que los
  demás modelos, ahora cae a procesador y funciona.
- `inspect` informa `notice:{message,severity}` con la línea de estado de la app. Los trabajos
  largos son asíncronos y solo dejan su resultado ahí: sin esto un fallo como "Failed to load SAM2
  model" no se podía ver desde fuera, porque la operación responde `ok` y nada cambia.
- El menú del selector de fuentes se queda dentro de la ventana; los estilos "Simple" y "Negrita"
  aparecen en español.

## 0.9.1 — inicio nuevo, quitar silencios y efectos de sonido

- Pantalla de inicio al estilo CapCut (StartScreen): crear con formato, herramientas rápidas y tarjetas de
  proyecto con miniatura, duración y tamaño; botón de inicio en el encabezado del editor.
- Quitar silencios y muletillas (`cutSilencesAndFillers`, operación MCP `cut_silences`): transcribe si hace
  falta y deja solo los tramos hablados con `keepRanges`; sin modelo de voz abre Extras.
- Efectos de sonido: tipo de extra nuevo `sound-effects` (SoundEffectCatalog), pestaña en el panel de
  recursos; paquete propio de 37 sonidos sintetizados (Licencia de contenido Flip Studio).
- Extras: 21 plantillas y 13 stickers animados nuevos; los paquetes se descargan de
  bajoelabrigo/flipstudio-extras; un paquete que da 404 refresca el índice y reintenta.
- Panel de propiedades más ancho y con margen para la barra de desplazamiento; los menús contextuales se
  ajustan al texto más largo.

## 0.9.0 — extras propios

- Extras vuelve a descargar: índice en getflipstudio.com/addons/index.json y paquetes en los GitHub Releases
  de bajoelabrigo/flip-addons, firmados con la clave de Flip Studio (la app ya no confía en la de CutWire).
- Paquetes: subtítulos automáticos (Whisper small), motor de IA (ONNX Runtime 1.27.0 para procesador),
  32 fuentes de Google Fonts, 150 stickers de emojis 3D y dos packs de stickers animados (48 emojis con
  movimiento; 19 de redes sociales, flechas y efectos).
- Stickers animados: un sticker Lottie entra como animación que se repite y dura lo que un sticker; en la
  cuadrícula se ve su miniatura con una insignia ▶. Las imágenes dentro de una animación se escalan sin
  mipmaps: en algunas tarjetas gráficas se veían como un cuadro negro.
- Fuentes: selector nuevo con buscador, favoritas, recientes y categorías con nombre (limpias, impacto,
  elegantes, manuscritas, divertidas, retro); botón para importar fuentes propias (.ttf/.otf, "Mis fuentes").
  Paquete "Más fuentes" con 72 familias, todas con tildes, ñ, ¿ y ¡.
- Texto: tipo de extra nuevo, plantillas de texto ("text-styles"), listadas por categoría en el panel Texto;
  paquete con 44 plantillas animadas (fe y versículos, redes, subtítulos virales, títulos, rótulos, precios,
  frases) y 8 combinadas (título con subtítulo, rótulo de dos líneas, versículo con cita, evento…), que se
  agregan como varios textos ya ubicados y sincronizados. Las tarjetas de estilo se animan al pasar el mouse.
- Subtítulos automáticos: se elige el estilo antes de generarlos; las frases se cortan en el punto, la
  pregunta o la coma; muletillas (eh, mmm) fuera y mayúscula al inicio; diccionario propio y Buscar y
  reemplazar; emojis según las palabras (opcional); traducción al inglés encima de los originales; en videos
  verticales quedan por encima de los botones de TikTok y Reels. Seleccionar un bloque de subtítulos abre el
  editor de frases.
- Resaltar palabras: una palabra entre asteriscos (*fe*) se pinta con el color de acento en cualquier estilo;
  regla nueva "Palabras clave". Los nombres de las reglas de acento están traducidos.
- Sincronización por palabra: con el extra "Sincronización por palabra (español)" (wav2vec2) cada subtítulo
  empieza y termina justo con la voz. Whisper medium como extra (más preciso; si está instalado se usa en
  lugar del small) y aceleración con tarjeta gráfica (WebGPU, experimental), que ahora también usa Whisper.
- Línea de tiempo al estilo CapCut: Dividir, Borrar izquierda/derecha, Eliminar y Marcador en la barra,
  más espacio entre botones, micrófono para voz en off, y herramientas que aparecen según el clip
  seleccionado (recortar, congelar, invertir/espejo/rotar, transcripción, quitar fondo, extraer audio,
  mejorar audio con reducir ruido y mejorar voz, mejorar video).
- Vista previa: menú de zoom (Completa a 400 %) y de relación de aspecto (16:9, 9:16, 1:1, 4:5, 4:3, 21:9).
- Subtítulos: entre segmentos de Whisper ya no se pegan las palabras ("noches,que"), y la limpieza solo
  pone mayúscula donde empieza una oración.

## 0.8.3 — sin funciones rotas a la vista

- La pestaña Market (recursos, efectos de sonido y stock de Pexels) se oculta mientras Flip Studio no tenga
  servicio propio; antes mostraba "Mercado no disponible".
- Extras: sin tienda de descargas, el administrador dice "Descargas próximamente" en lugar de "No se puede
  acceder a la tienda de descargas" con un botón Reintentar que no podía funcionar. Afecta a todos los botones
  que llevan a Extras (subtítulos automáticos, fuentes, stickers, máscaras, efectos).
- Las barras de íconos de los paneles de recursos y de propiedades son más anchas (50 px): la barra de
  desplazamiento ya no tapa los íconos cuando no caben todos.

## 0.8.2 — en español y con soporte propio

- Ventana de información de depuración: los enlaces de documentación y Discord de CutWire ahora llevan a las preguntas
  frecuentes de getflipstudio.com y a soporte@getflipstudio.com.
- La sesión del servidor MCP usa su propia carpeta temporal (`flip-studio`); antes compartía `drift` con una
  instalación de Drift y podían pisarse.
- La descripción del marketplace para agentes ya no nombra a CutWire.
- Paquete de Microsoft Store con la identidad de Flip Studio (`yitoweb.FlipStudio`).
- Interfaz en español completa (es y es_CO): unos 300 textos que seguían en inglés, los 33 estilos de texto
  y el nombre "Proyecto sin título". "Media bin" ya no se traduce como "papelera" sino como "biblioteca de
  medios", y se usa "video" en lugar de "vídeo".
- Los botones de interpolación de fotogramas clave (Recto, Suave, Salto) se ajustan a su texto; antes se
  cortaban en "R…" y "Su…".

## 0.8.1 — seguridad

- Claves de API y token MCP cifrados con DPAPI en Windows (migración automática).
- Servidor MCP: límites de tamaño y rechazo de `Content-Length` inválido.
- Acciones de GitHub de terceros fijadas a un commit exacto.
- Mensajes que aún decían "Flip" en lugar de "Flip Studio".
- Botón "Acerca de Flip Studio" en Ajustes para Windows, Linux y Android (Drift solo lo tenía en macOS).

## Etapa 1 — identidad propia (2026-10-09)

- Nuevo nombre e identidad: Flip Studio (`io.github.bajoelabrigo.FlipStudio`, `flipstudio.exe`, instalador con AppId propio).
- Ajustes y datos en su propia carpeta, separados de una instalación de Drift.
- Desactivados los servicios de CutWire (add-ons, marketplace y comprobación de versión) hasta que Flip Studio tenga los suyos.
- "Acerca de" acredita a Drift / CutWire Studios y enlaza al código fuente (requisito de la GPL).
- Ícono propio de Flip Studio en Windows, instalador, Microsoft Store, Linux y Android.
- Tema oscuro por defecto (antes seguía al de Windows); el usuario puede cambiarlo en Ajustes.
- La pantalla de inicio dice "Flip Studio" (quedaba "Drift").
- Corregido: en un panel de Medios angosto, "Nueva carpeta" e "Importar" se montaban sobre el título;
  ahora pasan a solo ícono. Los botones del panel vacío se apilan cuando no caben.
- Corregido: un archivo ZIP truncado (.mogrt, .lottie, accesorios faciales) colgaba la app; ahora falla con un error y hay un límite contra "bombas ZIP".

---

# Unreleased changes

Tracks work done on `main` **since the last public release**. Use this to see what is already fixed or added before filing an issue. Cleared when a new release ships.

**Last released version:** `0.7.5`

---

## ✅ Fixed

- **macOS: AVI, MKV and WebM play in the trim and preview window.** It could only play what Apple's own player supports, so these files showed a first frame and then would not play, even though they played on the timeline.
- **The media bin's hover hint no longer covers the right-click menu.**

## ✨ Added

- **Audio effects made of pedals.** An audio effect can now be a whole pedalboard: filters, a ladder filter, drive, reverb, convolution reverb, delay, pan and gain, alongside the original effects, run in series or side by side in parallel and frequency-band splits. Build them in Drift Forge and import the `.driftfx`.
- **Modulation for audio effects.** LFOs, envelope followers and step sequencers can move any pedal's knobs over time, in step with the clip, so a wobble lands in the same place after you seek.
- **Convolution reverb.** Put a sound in a real space using an impulse response shipped with the effect: Forge has a room, a plate, a hall and a spring tank, or record your own.
- **Keyframe audio effect parameters.** The sliders of an audio effect now take keyframes on the timeline, like a video effect's.

## 🎨 Improved
