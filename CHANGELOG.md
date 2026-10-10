# Flip Studio — cambios propios

Flip Studio es un fork de Drift. Esta sección lista lo que Flip Studio cambia respecto a Drift; debajo sigue el
registro heredado de Drift.

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
