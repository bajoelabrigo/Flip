# Próxima versión (0.23)

## 1. Efectos y LUTs directamente sobre un texto (Jorge, 2026-10-24)
Jorge: «¿se pueden aplicar máscaras, efectos, luts a textos?» → «ok, para la próxima sería».

- Hoy: las **máscaras** sí van sobre el texto (pestaña Máscaras, desde la 0.19.0). **Efectos y LUTs no:** un clip de
  texto no tiene la capacidad `adj:videoEffects` (`AppController.cpp`, `case ClipType::Text` en la lista de `caps`),
  así que no salen las pestañas Efectos ni Ajustar. Solo con una capa de ajuste encima («Aplicar a» → enlazada al clip).
- Qué hacer (como CapCut): soltar un efecto, un LUT o un filtro sobre un texto (y elegirlo con el texto seleccionado)
  crea solo la capa de ajuste enlazada a ese texto (`ParentTrack` + `linkedClipId`), y el texto muestra las pestañas
  Efectos y Ajustar que editan esa capa. Lo mismo para subtítulos si tiene sentido.
- Igual en la web. Probar en ventana: efecto, LUT y Ajustar sobre un texto, con animación y máscara a la vez.
