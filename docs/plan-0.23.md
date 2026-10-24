# Próxima versión (0.23)

## 1. ~~Efectos y LUTs directamente sobre un texto~~ — HECHO en la 0.22.0 (escritorio y web)
Jorge: «¿se pueden aplicar máscaras, efectos, luts a textos?» → «ok, para la próxima sería».

- Hoy: las **máscaras** sí van sobre el texto (pestaña Máscaras, desde la 0.19.0). **Efectos y LUTs no:** un clip de
  texto no tiene la capacidad `adj:videoEffects` (`AppController.cpp`, `case ClipType::Text` en la lista de `caps`),
  así que no salen las pestañas Efectos ni Ajustar. Solo con una capa de ajuste encima («Aplicar a» → enlazada al clip).
- Qué hacer (como CapCut): soltar un efecto, un LUT o un filtro sobre un texto (y elegirlo con el texto seleccionado)
  crea solo la capa de ajuste enlazada a ese texto (`ParentTrack` + `linkedClipId`), y el texto muestra las pestañas
  Efectos y Ajustar que editan esa capa. Lo mismo para subtítulos si tiene sentido.
- Igual en la web. Probar en ventana: efecto, LUT y Ajustar sobre un texto, con animación y máscara a la vez.

## 2. Colorear letras sueltas dentro de un texto (Jorge, 2026-10-24)
Jorge: «¿en un solo texto es posible poner letras de diferentes colores?» → «sí, anótalo».

- Hoy hay: «Resaltar palabra» (reglas, o la palabra entre asteriscos `*así*`), degradado del relleno por bloque,
  línea, palabra o letra (`TextGradientSpace`), o dos textos encima. **No** se puede elegir unas letras con el ratón
  y darles su propio color.
- Qué hacer (como CapCut): en el cuadro de texto del inspector (y al editar sobre la vista previa) seleccionar parte
  del texto y cambiarle **color, tamaño, negrita/cursiva, contorno y fondo** solo a esa parte.
- Cómo, con lo que ya existe: tramos con estilo propio sobre el texto (`TextStyle` gana una lista de
  `{inicio, fin, cambios}` guardada en el proyecto); `TextLayout` ya parte el texto en palabras/letras con su
  estilo (`StyledWord`, el acento usa algo parecido): extenderlo a tramos por caracteres. Las capas (relleno,
  contorno, sombra) aplican el color del tramo; las animaciones por letra siguen funcionando.
- Que sobreviva a: editar el texto (los tramos se mueven con lo escrito), cortar el clip, aplicar un estilo (decidir
  si los conserva: sí, como las animaciones), copiar/pegar atributos, plantillas, `.flip` y la web.
- Igual en el editor web. Probar en ventana: seleccionar «O» de «HOLA», ponerla roja y más grande, exportar.
