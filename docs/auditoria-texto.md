# Auditoría del sistema de texto (2026-10-24, rama `flip/v0.22.0`)

Pedido de Jorge: auditar todo lo que se puede crear, editar, animar y personalizar con texto en el escritorio,
comparado con CapCut Desktop y Filmora Desktop, **sin reconstruir nada** y sin tocar código antes del informe.

**Cómo se hizo.** Tres revisiones del código en paralelo (motor y estilo; animación y fotogramas clave; interfaz,
plantillas, subtítulos y composición), cada función seguida desde el control de la interfaz hasta el modelo, el
dibujo (vista previa **y** exportación), el guardado y el deshacer. Además, lo que se vio en ventana el mismo día con
el portable de la 0.22.0 (galerías de animación de texto y de clip, voces, Stock en cada panel, fotogramas clave,
Mi cuenta). Lo que solo se leyó en el código dice «código»; lo visto en ventana dice «ventana». **No se exportó
ningún video para esta auditoría**: lo de exportación está seguido en el código, no medido.

Estados: IMPLEMENTADA · PARCIAL · DEFECTUOSA · AUSENTE · NO VERIFICADA · NO APLICABLE.

---

## A. Resumen

- **Funciones auditadas: 106** (las filas de la matriz de abajo).
- IMPLEMENTADA: **49** · PARCIAL: **31** · DEFECTUOSA: **5** · AUSENTE: **18** · NO VERIFICADA: **3** · NO APLICABLE: 0.
- Además, **14 defectos concretos** (sección D): algunos están dentro de funciones marcadas PARCIAL o IMPLEMENTADA
  porque fallan solo en un caso.
- **Lo más importante:**
  1. Hay **un solo sistema de texto** (`drift::TextStyle`) para títulos, subtítulos, plantillas, estilos rápidos,
     burbujas, looks, Mis estilos y Stock, y **un solo camino de dibujo** (`FrameCompositor::fillTextLayer`) para la
     vista previa y la exportación. No hay motores duplicados que unir.
  2. El sistema es más completo de lo que parece: pila de capas (varios rellenos, contornos, sombras, resplandor,
     extrusión), degradados lineal/radial/cónico, texturas, shaders animados, fondo por bloque/línea/palabra, texto
     en arco, giro 3D por letra y del bloque, 349 animaciones con partículas y cursor, fotogramas clave estilo After
     Effects, karaoke, seguimiento.
  3. **Catorce defectos concretos** (sección D). Los más visibles para el usuario: aplicar una plantilla **borra la
     animación** del texto; cortar un texto **repite su animación** en el corte; el contorno «Dentro» **no se ve**;
     borrar una animación propia deja sin animación los proyectos que la usan; tres animaciones «bloque» escalan
     mal.
  4. Lo que más falta frente a CapCut/Filmora: texto sobre un trazo Bézier, deformar por esquinas, 3D real con bisel,
     tachado y justificado, copiar y pegar fotogramas clave, búsqueda en las galerías de texto, VTT/ASS, y que el
     texto tenga a la vista las pestañas Efectos y Ajustar.

---

## B. Matriz por categoría

Rutas relativas al repo. AC = `src/models/AppController.cpp`, TI = `src/qml/components/properties/TextInspector.qml`,
FC = `src/engine/FrameCompositor.cpp`, TS = `src/core/TextStyle.cpp`, TL = `src/engine/TextLayout.cpp`,
TP = `src/engine/SkiaTextPainter.cpp`, TA = `src/core/TextAnimator.cpp`.

### B1. Creación y edición

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Añadir texto desde Títulos | IMPLEMENTADA | `TextAssetsTab.qml:460` → AC:8732 | Texto de 5 s en el cabezal, caja ajustada. **Clic siempre crea uno nuevo**: no re-estiliza el texto elegido | código + ventana |
| Varias líneas | IMPLEMENTADA | TI:891, `InlineTextEditor.qml:236` | Enter = salto. `commitTextEdit` hace `trimmed()` (AC:12378): se pierden saltos al principio/final | código |
| Editar en la vista previa | IMPLEMENTADA | `TransformOverlay.qml:434` → AC:12536 | Doble clic, un paso de deshacer. No para subtítulos ni textos dentro de una composición cerrada | código |
| Editar en el inspector (+ «Aplicar») | IMPLEMENTADA | TI:222, 891-960 | Aplica al perder el foco; el botón sobra en parte | ventana |
| Duplicar / copiar / pegar | PARCIAL | AC:24051 | Copia estilo, animación, seguimiento y máscaras; **no** las capas de efectos enlazadas | código |
| Pegar atributos (estilo de texto) | AUSENTE | AC:21843 | Solo transform, velocidad, volumen, efectos, transiciones | código |
| Duración, mover, recortar, cortar | IMPLEMENTADA | genérico | — (ver defecto D3 al cortar) | código |
| Deshacer / rehacer | IMPLEMENTADA | AC:6518 `pushProjectEdit` | Copia completa del proyecto; arrastres en un paso. Encender una sección de Básico deja 2 pasos (TI:361-374) | código (script sobre ~45 funciones) |
| Guardar y abrir | IMPLEMENTADA | TS:1143-1214, `Project.cpp:266-432` | Mismas claves al escribir y leer. Las animaciones `user:`/Stock se guardan solo por id (D4) | código |

### B2. Tipografía

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Familia, peso 100-900, cursiva | IMPLEMENTADA | TL:246-249 | Sin negrita/cursiva sintética: si la fuente no trae cursiva sale recta sin aviso | código |
| Fuentes incluidas (fonts.basic/extra) | IMPLEMENTADA | `FontCatalog.cpp:398` | Cuentan como extra requerido del proyecto | código |
| Fuentes del sistema | IMPLEMENTADA | `SkiaFontCollection.cpp:112` | No viajan en el `.flip` | código |
| Fuentes importadas | PARCIAL | AC:13478 | Se registran en Qt y Skia; **no viajan en el `.flip`** ni avisan en otro equipo | código |
| Aviso de fuente que falta | PARCIAL | TL:482 | Solo las plantillas avisan; un `.flip` abierto en otra PC cambia de fuente en silencio | código |
| Fuentes variables (ejes) | NO VERIFICADA | TL:246 | Solo peso/cursiva; sin ejes ni ancho | código |
| Tamaño | PARCIAL | TS:86 (`int`), TS:1104 | **Entero**: una animación de tamaño va a saltos | código |
| Escalar con la esquina | DEFECTUOSA | `TransformOverlay.qml:727`, AC:13507-13545 | Solo cambia `pixelSize` (no contorno, sombra ni fondo); no hace nada si el tamaño tiene claves (D7) | código |
| Color | IMPLEMENTADA | TS `primaryColor` | — | ventana |
| Alineación H y V | PARCIAL | TL:390 | Izq/Centro/Der y Arriba/Medio/Abajo; **sin justificado** | código |
| Interlineado, espaciado entre letras | IMPLEMENTADA | TS:104-105 | Con claves | código |
| Espaciado entre palabras | AUSENTE | — | — | código |
| Mayúsculas / minúsculas / título | IMPLEMENTADA | TS:1422 | — | código |
| Versalitas / OpenType | AUSENTE | — | — | código |
| Subrayado | PARCIAL | TP:1047 | Color sólido; se apaga con texto en arco | código |
| Tachado | AUSENTE | — | — | código |
| Ajuste de línea y ancho de caja | IMPLEMENTADA | TL:414 | Sin máximo de líneas ni «…» | código |
| Ajuste automático (`textAutoFit`) | PARCIAL | AC:3715-3905 | La caja se ajusta al texto; **no achica la letra para que quepa** | código |
| Tildes, grafemas, emoji | IMPLEMENTADA | TL:205-229, 420-436 | Emoji a color con el extra `emoji-font` | código |
| Chino/japonés por palabra | PARCIAL | TL:76-104 | Sin espacios, una frase cuenta como una palabra (animación y karaoke) | código |
| Derecha a izquierda | PARCIAL | TL:253 | Automática por la primera letra; no se elige a mano | código |
| Escritura vertical | AUSENTE | — | — | código |
| Vista previa = exportación (fuentes y posición) | PARCIAL | TL:339, `CompositorService.cpp:156` | Mismo código, pero el tamaño se redondea a la escala de render y la vista previa cambia de escala sola: **los saltos de línea pueden diferir** (D8, sin medir) | código |

### B3. Relleno, contorno, sombra, brillo, fondo

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Relleno sólido y opacidad | IMPLEMENTADA | `TextShading.cpp:93`, `SkiaShading.cpp:55` | 8 modos de fusión por capa | código |
| Degradado lineal / radial / cónico, varias paradas | IMPLEMENTADA | `SkiaTextEffects.cpp:182`, `GradientStopEditor.qml` | Ángulo, centro, escala, repetir, OKLab; por bloque, línea, palabra o letra. «Bloque» usa medidas viejas (D5) | código |
| Textura / imagen | PARCIAL | `SkiaTextEffects.cpp:226`, `PaintEditor.qml:62` | Viaja en el `.flip`; **la ruta puede quedar `/C:/…` en Windows** (D9, sin probar) | código |
| Rellenos animados (shine, shimmer, neón, glitch, cromo, disolver) | IMPLEMENTADA | `SkiaTextEffects.cpp:269` | Si el shader no compila sale color sólido sin aviso | código |
| Contorno (varios, degradado, punteado) | PARCIAL | TP:916-951 | Varios contornos, trazo, punteado, boceto | código |
| Contorno «Dentro» | DEFECTUOSA | TP:939-948, AC:1724 | Queda **debajo** del relleno: con relleno opaco no se ve (D2) | código |
| Sombra (color, opacidad, X/Y, desenfoque, extensión, varias) | PARCIAL | TP:953-976 | Sin ángulo/distancia (solo X/Y); crece con el **primer** contorno | código |
| Sombra interior | AUSENTE | — | — | código |
| Resplandor exterior / neón | PARCIAL | TP:953, `TextLook.cpp:124` | Es una sombra sin desplazamiento; sin resplandor interior | código |
| Fondo por bloque o por línea, burbujas | IMPLEMENTADA | TP:1006-1045, `TextQuickStyles.cpp` | Relleno X/Y, radio, borde; 32 burbujas. No sigue a las letras animadas | código + ventana |
| Fondo por palabra (píldoras) | IMPLEMENTADA | TP:645-661 | Se apaga con texto en arco | código |
| Estilos rápidos (42) y looks | IMPLEMENTADA | `TextQuickStyles.cpp:90-238`, `TextLook.cpp` | Recetas que reescriben el estilo. El elegido no queda marcado al volver al clip | código |

### B4. Transformaciones, arco, perspectiva, 3D, trazo

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Posición, giro, opacidad (con claves) | IMPLEMENTADA | FC:907, 1478 | Giro sobre el centro | ventana |
| Punto de anclaje | AUSENTE | — | — | código |
| Escala X/Y separadas del texto | AUSENTE | — | Solo `pixelSize` | código |
| Inclinación (skew) del clip | PARCIAL | TP:748 | Solo por letra dentro de una animación | código |
| Recorte de un texto | NO VERIFICADA | — | `Clip.h` no tiene recorte para texto | código |
| Giro 3D del bloque (X/Y, Z, perspectiva) | IMPLEMENTADA | FC:1486-1494 | Con claves | código |
| Perspectiva por letra | IMPLEMENTADA | TP:383, 749 | Desde las animaciones (0.20) | código |
| Deformar por cuatro esquinas | AUSENTE | — | — | código |
| Texto en arco | PARCIAL | TS:99, TP:143-173 | −100 a 100 con claves; **una sola línea**, sin píldoras ni subrayado | código |
| Texto en círculo completo / sobre un trazo Bézier | AUSENTE | — | — | código |
| Extrusión «3D» | PARCIAL | TP:978-995 | Copias apiladas (2,5D); sin luz ni bisel | código |
| 3D real (bisel, material, luz) | AUSENTE | — | `Model3d` es otro tipo de clip (GLB) | código |

### B5. Animaciones de texto

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Motor (letra, palabra, línea, bloque; selectores de rango) | IMPLEMENTADA | TA:874-949, FC:1226 | Vista previa y exportación por el mismo código | código |
| Entrada (245), Salida (114), Bucle (13) | IMPLEMENTADA | `presets/text-animations/` | Aparecer, deslizar, zoom, giro, rebote, máquina de escribir, revelar, desintegrar… (ids en el informe de la sección G) | código + ventana |
| Entrada + Salida + Bucle a la vez | IMPLEMENTADA | TA:925, 326-367 | Se componen sin pisarse; si Entrada+Salida > clip se pisan sin aviso | código |
| Duración, escalonado, orden, curva, unidad | IMPLEMENTADA | TA:865, `TextAnimationPreset.cpp:124` | — | código + ventana |
| Retraso de la casilla | PARCIAL | TA:340 | Funciona y se guarda; **sin control en la interfaz** | código |
| Partículas (137) y cursor (44) | IMPLEMENTADA | TA:666-790, TP:1076-1118 | Deterministas | código |
| Animar color de relleno/contorno, grosor, desenfoque, borrado | IMPLEMENTADA | TA:423-457 | El color es un destino, no una curva propia | código |
| Animar contorno cuando el texto no tiene | PARCIAL | TP:835, 916 | 7 animaciones pierden su parte de contorno | código |
| Animar sombra / resplandor en una animación | AUSENTE | `TextAnimator.h:127` | Solo con fotogramas clave del estilo | código |
| Escala no uniforme en animaciones «bloque» | DEFECTUOSA | TA:468 | Ignora `scaleY` (D6) | código |
| Controles de Bucle (Período, Por, Curva) | DEFECTUOSA | TI:2739, 2796, 2875 | No hacen nada en 10–13 de las 13 (D10) | código |
| Bucle: giro continuo y resplandor | AUSENTE | — | — | código |
| Mis animaciones: guardar, renombrar, borrar, exportar | PARCIAL | AC:26721-26842 | Al guardar se pierden retraso/período; **no hay botón Importar**; importar dos veces duplica | código |
| Animación a medida | PARCIAL | TI («Custom animator») | Solo por MCP, sin editor | código |
| Animación de clip sobre un texto | IMPLEMENTADA | FC:1047-1088 | Se suma a la de texto (un «Fundido» de clip + «fade» de texto = doble) | código + ventana |
| Llamita y cuenta en todas las animaciones | IMPLEMENTADA | TI `wearsFlame`, `AnimationInspector.qml` | Pedido de Jorge 0.22 | ventana |
| Búsqueda en la galería de animaciones | AUSENTE | — | — | código |

### B6. Fotogramas clave

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Posición, escala, giro, giro 3D, opacidad | IMPLEMENTADA | FC:1322, 1486 | — | ventana |
| Tamaño, espaciados, relleno de caja, curvatura | IMPLEMENTADA | TS:1001-1138 | El tamaño se redondea | código |
| Capas del estilo (opacidad, grosor, desenfoque, desplazamiento) | PARCIAL | `TextShading.cpp:643` | En la interfaz solo algunas filas | código |
| Color con fotogramas clave | PARCIAL | `TextShading.cpp` (r/g/b/a) | El motor lo acepta; **en la interfaz no hay** (solo MCP) | código |
| Tipos AE (recto, suave, salto, Bézier), menú, atajos, 17 curvas | IMPLEMENTADA | `KeyframeKeyTools.qml`, AC:17824-18047 | Sin pruebas automáticas | ventana |
| Elegir varias y moverlas | IMPLEMENTADA | `KeyframeKeyTools.qml:54-160` | Sin selección con recuadro ni de dos pistas a la vez | código |
| Gráfica de valor | IMPLEMENTADA | `KeyframeGraph.qml` | — | ventana |
| Gráfica de velocidad | AUSENTE | — | — | código |
| Copiar / pegar fotogramas clave | AUSENTE | — | — | código |
| Trayectoria de posición en la vista previa | AUSENTE | — | x e y son pistas sueltas | código |

### B7. Editor de títulos, plantillas, WordArt

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Pila de capas (WordArt) | IMPLEMENTADA | TI:1880-1900, AC:26151 | Orden, duplicar, borrar; escondida en «Avanzado» | código |
| Plantillas de texto (Efectos › Plantillas, Avanzado › Preajuste) | DEFECTUOSA | AC:13132 | `clip.textStyle = *preset`: **borra animación, claves y contador** (D1) | código |
| Plantillas de varias partes | PARCIAL | AC:8806 | Crea N textos en N pistas, **sin agrupar** | código |
| Mis estilos (guardar, renombrar, borrar, importar, exportar) | IMPLEMENTADA | `TextAssetsTab.qml:720-812` | 3 botones «Guardar estilo» distintos; Títulos oculta los de Stock y Efectos los muestra | código |
| Estilos de Stock en Títulos | IMPLEMENTADA | `TextAssetsTab.qml:53-180` | Con cuenta; chips repetidos arreglados el 2026-10-24 | ventana |
| Búsqueda en galerías de texto | PARCIAL | TI:2413 | Solo en Texto › Efectos | código |
| Varios textos + formas + imagen en un elemento | IMPLEMENTADA | AC:14432, 23017, 15187 | Composición anidada (un nivel); para editar hay que abrirla | código |
| Plantillas de escena con textos editables | PARCIAL | `TemplateFillPanel.qml:216` | Campo de **una línea** | código |
| Texto con IA | PARCIAL | AC:23929 | **Elige un estilo**, no escribe el texto; el nombre confunde | código |

### B8. Subtítulos

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Generar (Whisper) con alineación por palabra | IMPLEMENTADA | AC:9100-9460 | Asíncrono, deshacible | código |
| Manuales, editar texto y tiempos, buscar y reemplazar | IMPLEMENTADA | `SubtitleEditor.qml`, `SubtitleCueLane.qml` | — | código |
| SRT importar/exportar | IMPLEMENTADA | `core/SrtIO.cpp` | — | código |
| VTT / ASS | AUSENTE | `SrtIO.cpp:33` | — | código |
| Mismo estilo y motor que los títulos | IMPLEMENTADA | AC:26078, FC:1383 | Un estilo por clip, «Aplicar a todos» | código |
| Karaoke por palabra | PARCIAL | `SubtitleCue.h:21`, FC:1028 | Los tiempos por palabra **no se guardan**: avanza proporcional (D11) | código |
| Animación de subtítulos | PARCIAL | FC:1053 | Animación de texto sí; de clip no | código |
| Traducir | PARCIAL | AC:9068 | Solo al inglés | código |
| Voz desde subtítulos | IMPLEMENTADA | `VoiceoverDialog.qml:118` | Para un texto normal no hay «leer en voz alta» | código |

### B9. Seguimiento y composición

| Función | Estado | Dónde | Qué hace / límites | Prueba |
|---|---|---|---|---|
| Texto que sigue un objeto o una cara | IMPLEMENTADA | `MotionTrackController.cpp:1282` | Lo convierte en claves de posición (y tamaño). **Volver a seguir borra las claves del usuario sin avisar** (D12) | código |
| Orden de capas, opacidad, modos de fusión | IMPLEMENTADA | FC:1832 | Mezcla está dos veces (Básico y pestaña Blending) | código |
| Máscaras en texto y subtítulos | IMPLEMENTADA | AC:16437, FC:1477 | — | código |
| Efectos y LUT sobre un texto | PARCIAL | AC:11588, 18685, FC:1507 | **Soltar un efecto sobre el texto ya funciona** (capa de ajuste enlazada); faltan las pestañas Efectos/Ajustar en el texto (plan 0.23) | código |
| Texto detrás de una persona | NO VERIFICADA | `EffectsInspector.qml:1441` (`depth.occlude`) | Existe el efecto «Detrás del sujeto» por profundidad; no seguido sobre un texto | código |

---

## C. Funciones que faltan (y si importan)

| Falta | Qué aporta | ¿Relevante? |
|---|---|---|
| Texto sobre un trazo / círculo completo | Logos circulares, texto que sigue una curva dibujada (Filmora lo tiene en su editor de títulos avanzado) | Sí, media |
| Deformar por esquinas / perspectiva libre | Pegar texto sobre una pared o pantalla | Sí, media |
| 3D real con bisel y luz | Títulos de cine | Baja: CapCut tampoco tiene 3D real; Filmora tiene «3D Titles» como plantillas |
| Tachado, justificado, espaciado entre palabras | Tipografía básica | Sí, alta (barato) |
| Copiar y pegar fotogramas clave | Flujo de trabajo de animación | Sí, alta |
| Pegar el estilo de texto (pegar atributos) | Aplicar el mismo look a muchos textos (CapCut lo tiene) | Sí, alta |
| Aplicar un estilo de Títulos al texto elegido | CapCut cambia el estilo del texto seleccionado | Sí, alta |
| Búsqueda en galerías de texto y animación | 349 animaciones sin buscador | Sí, alta |
| VTT / ASS | Subtítulos para web y plataformas | Media |
| Tiempos por palabra guardados en el subtítulo | Karaoke exacto (CapCut lo hace con su transcripción) | Sí, alta: el dato ya se calcula |
| Sombra interior, resplandor interior | Estilos WordArt | Baja |
| Escritura vertical | Idiomas asiáticos | Baja |
| Bucle de giro continuo y de resplandor | Animaciones de bucle de CapCut | Media |
| Gráfica de velocidad, trayectoria de posición | Animación avanzada estilo AE | Baja–media |

---

## D. Funciones defectuosas (con archivo y arreglo)

| # | Defecto | Dónde | Qué ve el usuario | Arreglo |
|---|---|---|---|---|
| D1 | Aplicar una plantilla reemplaza el estilo entero | AC:13132-13153 (`applyTextPreset`) | Se pierden Entrada/Salida/Bucle, fotogramas clave, contador y mayúsculas | Copiar la plantilla sin tocar `animation`, claves, contador y `textCase` |
| D2 | Contorno «Dentro» invisible; «Fuera» no se recorta | TP:939-948, AC:1724-1746 | Elegir «Dentro» no cambia nada | Recortar como `SkiaShapePainter.cpp:136` (`kDifference`) o pintarlo encima del relleno |
| D3 | Cortar un texto repite su animación | `TimelineOps.cpp:1254-1263` | En el corte, la primera mitad hace su Salida y la segunda su Entrada; el Bucle reinicia | Al cortar, quitar la Salida de la primera mitad y la Entrada de la segunda (como ya se hace con la animación de clip) |
| D4 | Borrar una animación propia/de Stock rompe los proyectos | TA:1465, `TextAnimationPreset.cpp:470`, TI:2981 | El texto queda quieto; el aviso dice lo contrario | Guardar la receta dentro del proyecto (como los LUT) o corregir el aviso |
| D5 | Medidas viejas en caché (fondo, degradado «Bloque», barrido) | TL:63-72, 1102, 1138 | Al cambiar solo el grosor del contorno, el fondo queda del tamaño anterior; afecta también a otro clip con el mismo texto | Meter el grosor del contorno y los rellenos en `layoutKey`, o no guardar `ink` en caché |
| D6 | Escala de las animaciones «bloque» ignora `scaleY` | TA:468 | `im-jump-squash`, `ibs-hologram-boot`, `imf-jello-skew` se ven al revés | `BlockProps.scaleX/scaleY` |
| D7 | Escalar con la esquina | AC:13507-13545 | Solo crece la letra; con claves de tamaño no hace nada | Escalar todo el estilo (como `scaleTemplateLayout` debería) o escribir la clave |
| D8 | Saltos de línea vista previa ≠ exportación (riesgo) | TL:339 | Un texto de ancho fijo puede cortar distinto al exportar | Maquetar a escala 1 y escalar el dibujo; **medirlo primero** |
| D9 | Ruta de textura en Windows (riesgo) | `PaintEditor.qml:62` | La textura podría no cargar | `toLocalFile()`; probar en ventana |
| D10 | Controles de Bucle que no hacen nada | TI:2739, 2796, 2875 | Mover Período/Por/Curva no cambia la animación | Mostrar solo los parámetros que declara la animación |
| D11 | Karaoke aproximado | `SubtitleCue.h:12-16` | El resaltado no va con la voz dentro de la frase | Guardar los tiempos por palabra que ya calcula la alineación |
| D12 | Volver a seguir borra claves | `MotionTrackController.cpp:111-120` | Se pierden las claves de posición sin aviso | Avisar o guardarlas aparte |
| D13 | `EditorState.sizeLinked` no existe | TI:1765, `VideoInspector.qml:165` | El candado de tamaño no guarda su estado (aviso en el registro) | Usar `inspectorUi.sizeLinked` como la pestaña Transform |
| D14 | Plantillas escaladas a otro lienzo | `SceneTemplateLayout.cpp:59-62` | El contorno, la sombra y el fondo quedan finos/gruesos | Escalar todas las medidas del estilo |

---

## E. Funciones avanzadas posibles con la arquitectura actual

| Función | Qué hace falta | Tipo de cambio |
|---|---|---|
| Pestañas Efectos/Ajustar en el texto | `adj:videoEffects` en `case ClipType::Text` (AC:1069) y probar | Cambio menor (plan 0.23) |
| Pegar estilo de texto / aplicar estilo al texto elegido | Opción en `pasteAttributes` y en el clic de Títulos | Cambio menor C++ + QML |
| Tachado, justificado, espaciado entre palabras | Campos en `TextStyle`, SkParagraph ya los soporta | Cambio menor en el renderizador |
| Copiar/pegar fotogramas clave | Portapapeles en `KeyframeKeyTools` + `AppController` | Nuevo componente C++/QML pequeño |
| Búsqueda en galerías | Filtro por nombre traducido | QML |
| Karaoke exacto | Campo de tiempos en `SubtitleCue` + guardado | C++ |
| VTT/ASS | Lector/escritor junto a `SrtIO` | C++ |
| Texto sobre un trazo y en círculo completo | Generalizar el arco (TP:143) a un `SkPath` con `SkContourMeasure` | Cambio en el renderizador |
| Deformar por esquinas | Matriz de perspectiva en la capa GPU (ya hay pose 3D) | Cambio en el motor de composición |
| Sombra/resplandor interior | Nuevas capas en `TextShading` | Renderizador |
| 3D real con bisel | Mallas o SDF | Arquitectura adicional (no recomendado ahora) |

---

## F. Prioridades

**PRIORIDAD 1 — lo que existe y está mal** (el usuario pierde trabajo o ve algo distinto a lo que eligió):
D1 plantilla que borra la animación · D3 cortar repite la animación · D4 animaciones borradas · D2 contorno «Dentro» ·
D5 medidas viejas · D6 escala «bloque» · D10 controles de Bucle · D13 candado de tamaño · D12 seguimiento que borra
claves. Todas son cambios acotados en el código existente.

**PRIORIDAD 2 — básicos que faltan:** pestañas Efectos/Ajustar en el texto (0.23) · aplicar estilo al texto elegido
y pegar estilo · tachado, justificado, espaciado entre palabras · búsqueda en las galerías · karaoke exacto · copiar y
pegar fotogramas clave · aviso de fuentes que faltan y fuentes importadas dentro del `.flip`. Son lo que un usuario de
CapCut espera encontrar.

**PRIORIDAD 3 — avanzadas con valor profesional:** texto sobre un trazo y círculo completo · deformar por esquinas ·
D7/D14 escalado completo del estilo · tamaño con decimales · VTT/ASS · Bucle de giro continuo y resplandor · editor
visual de animaciones propias · medir y arreglar D8.

**PRIORIDAD 4 — experimentales:** 3D real con bisel y luz · escritura vertical · gráfica de velocidad y trayectoria
espacial · sombra/resplandor interior · fuentes variables con ejes.

---

## G. Archivos y arquitectura

- **Modelo:** `src/core/TextStyle.*` (estilo + pila de capas `TextShadingLayer`), `src/core/TextShading.*`,
  `src/core/Clip.h:131-137` (`textContent`, `textStyle`, `textAutoFit`), `src/core/SubtitleCue.h`.
- **Recetas que producen un `TextStyle`:** `TextQuickStyles` (estilos rápidos y burbujas), `TextLook` (looks),
  `TextPresetStore` (Mis estilos), `TextStyleCatalog` (extras `pack:`), Stock (`text-style`), textos de plantillas
  de escena (`placeholderId`).
- **Animación:** `src/core/TextAnimator.*`, `TextAnimationPreset.*`, `presets/text-animations/*.json`,
  `ClipAnimationPreset.*`.
- **Dibujo:** `FrameCompositor::buildGpuLayer` → `fillTextLayer` (FC:1196) → `TextLayout::fragmentsFor`
  (SkParagraph, caché de 64) → `evaluateTextAnimation` → `SkiaTextPainter` (`makeTextPainter`, TP:1336); el
  movimiento del bloque va en la capa GPU. Vista previa (`CompositorService`) y exportación (`Exporter`) usan el
  mismo `FrameCompositor`; solo cambia `renderScale`.
- **Interfaz:** `TextAssetsTab.qml` (Títulos), `TextInspector.qml` (Básico, Burbuja, Efectos, Animación),
  `TextParamSlots.qml`, `TextLookPicker.qml`, `PaintEditor.qml`, `GradientStopEditor.qml`, `AnimationInspector.qml`,
  `KeyframeKeyTools.qml`, `KeyframeGraph.qml`, `TrackKeyframeRows.qml`, `SubtitleEditor.qml`,
  `TemplateFillPanel.qml`, `TrackingInspector.qml`, `MasksInspector.qml`. Pestañas por capacidades
  (`AppController::inspectorCaps`, AC:1002).
- **Sistemas aparte, sin conectar al estilo:** texto dentro de Lottie/SVG (Skottie), importadores de MOGRT,
  Kdenlive y Resolve. No duplican el motor; solo no comparten estilo.
- **Problemas de uso:** Transform y Mezcla dos veces (Básico y pestañas propias) · looks y plantillas dos veces
  (Efectos y Avanzado) · tres botones de «Guardar estilo» · dos sistemas de animación en un texto (pestaña Animación
  de clip y Texto › Animación) sin explicación · la pila de capas escondida en «Avanzado» · «Texto con IA» no
  escribe texto.
- **Pruebas:** hay pruebas del motor de animación, de animaciones de clip y de interpolación (`tests/tst_core.cpp`,
  `tst_engine.cpp`, `tst_skia.cpp`); **ninguna** de las operaciones de fotogramas clave de la 0.22.

## H. Plan de implementación (propuesta, no empezado)

1. **0.22.x — arreglos (Prioridad 1).** Uno por commit, cada uno con su prueba en `tests/` y visto en ventana:
   D1, D3, D4 (primero el aviso, después guardar la receta), D2, D5, D6, D10, D13, D12.
2. **0.23 — texto como CapCut (Prioridad 2).** Pestañas Efectos/Ajustar en el texto (ya en `docs/plan-0.23.md`),
   aplicar estilo al texto elegido y pegar estilo, tachado/justificado/espaciado de palabras, buscadores, karaoke
   exacto, copiar y pegar claves, fuentes dentro del `.flip`. Igual en la web.
3. **0.24 — avanzadas (Prioridad 3).** Texto sobre un trazo (reutiliza el arco), deformar por esquinas (reutiliza
   la pose 3D de la capa), escalado completo del estilo, VTT/ASS, Bucles nuevos. Antes, medir D8 exportando.
4. **Después — Prioridad 4,** solo si hay demanda.
