# Plan 0.27 — Auditoría del código y app fácil hasta para un niño

Pedido de Jorge (2026-10-30): «hazle una auditoría profunda al código, busca errores y mejóralo sin romper nada;
y un plan de mejoras como si fueras un usuario: que sea fácil hasta para un niño. Lo que haya que añadir, quitar o
mejorar lo hacemos de una vez». Rama: `flip/v0.27-auditoria`.

Si otro asistente sigue este trabajo: `[x]` hecho, `[~]` a medias, `[ ]` falta. Cada punto dice dónde está.
La auditoría la hicieron 7 revisores en paralelo (solo lectura); cada hallazgo se vuelve a comprobar en el código
antes de tocarlo. Los arreglos se verifican con `g++ -fsyntax-only` y headers reales (script en el scratchpad de la
sesión: Qt 6.10.3 de `.qtmingw`, FFmpeg 7.1, ORT 1.27, Skia); al final, un build de CI y prueba en ventana.

## Parte 1 — Auditoría del código

### AppController (2.ª mitad) y McpController
- [x] A2-1 Trabajos en segundo plano con `this` crudo (congelar, transición IA, cámara lenta suave, texto IA):
      al cerrar la app a mitad podían escribir sobre un objeto destruido. Ahora `QPointer self`.
- [x] A2-2 «Normalizar a −14 LUFS» multiplicaba el volumen dos veces (y otra vez en cada clic). Ahora la clave más
      fuerte queda en la ganancia medida.
- [x] A2-3 «Quitar silencios» se enganchaba con un `static` compartido entre instancias (`m_silenceCutHooked`).
- [ ] A2-4 Dos instalaciones de Stock (efectos/transiciones) a la vez se cruzan (`AddonManager` stage único).
- [x] A2-5 Una tarjeta de Retoque = 1+N pasos de deshacer → uno solo.
- [x] A2-6 Suavizado de clave a 17–33 ms de la clave cambiaba sin paso de deshacer.
- [x] A2-7 Borrar pistas desde la cabecera ignoraba el candado.
- [x] A2-8 «Mejorar voz» decía «listo» aunque el clip no tuviera sonido.
- [x] A2-9 Quitar el relleno de canal inexistente dejaba un paso de deshacer vacío.
- [ ] A2-10…13 Avisos que faltan (normalizar sobre clip borrado, cámara lenta, línea líquida, ruta de salida IA).
- [x] A2-14 Textos en inglés sin `tr()` («Getting ready…», «Done», «Freeze frame», errores de `keepRanges`).
- [x] A2-15 Estelas de Morph heredan `linkId/parentId/matteClipId`.
- [ ] A2-16 Aplicar estilo de texto a subtítulos copia los colores por letra del origen.
- [x] A2-17 `clipAnimationCategories` con `static` congela el idioma.
- [ ] A2-18 Bucles de espera anidados de 15 s (sonido/recurso).
- [ ] A2-19 Herramientas (Doblar, Líquido) cierran la sesión de Texto avanzado abierta.

### AppController (1.ª mitad)
- [x] A1-1 `m_undoStack.clear()` con una sesión abierta: el siguiente `endEditSession` deshacía un paso ajeno
      (podía borrar el clip recién añadido). `resetEditSession()` + puntero al macro.
- [x] A1-2 Texto con la herramienta Texto: deshacer/rehacer lo devuelve al centro.
- [ ] A1-3 Texto sobre forma: el trazado se actualiza después de la foto de deshacer.
- [x] A1-4/5 «Secuencia» empieza mal si una capa está en 0 s y desincroniza el audio enlazado.
- [x] A1-6/7 Comportamientos en filas de efectos/máscaras; los ajustes de Rebote se pierden.
- [x] A1-8 «Subtitles generated» en inglés.
- [x] A1-9 Centrar mueve también el audio enlazado.
- [x] A1-10 Mate de seguimiento en ciclo (A usa B y B usa A): desaparecen los dos.
- [x] A1-11/12 Candado ignorado en mover a pista nueva, reemplazar en subtítulos y emojis.
- [ ] A1-13 Mensajes que nunca se ven (`finishEdit(msg)` ignora el texto).
- [ ] A1-14 Guardar curvas sin `QSaveFile`.
- [ ] A1-15 Niveles de deshacer no se reaplican al abrir proyecto.
- [ ] A1-16 Pin de marioneta = 3 pasos de deshacer.
- [ ] A1-17 Pasos de deshacer vacíos en suavizar/asentar.
- [ ] A1-18 Gráficos esenciales: texto nuevo con colores por letra viejos.
- [ ] A1-19/20 Sólidos: carpeta buscada por nombre traducido; recolorear dentro de composiciones.
- [ ] A1-21 Textos en inglés en animaciones propias.
- [ ] A1-22 Subtítulos automáticos: trabajo con `this` crudo al cerrar.

### Núcleo (proyecto, claves, plantillas)
- [x] C-1 Expresiones JavaScript sin límite de tiempo: `while(true){}` congela la app.
- [x] C-2 Copias de pistas de claves pierden comportamiento y cronómetro (escala, plantillas, velocidad…).
- [x] C-3 Cortar un clip con reasignación de tiempo rompe su reproducción.
- [x] C-4 `kCurrentVersion` del proyecto sin subir desde la 0.24 (una app vieja borra lo nuevo al guardar).
- [x] C-5 Cortar no mueve las máscaras extra ni sus trazados animados.
- [ ] C-6 Comportamientos reinician en la mitad cortada (salto visible).
- [ ] C-7 Cortar a mitad de un morph de trazado lo hace saltar.
- [ ] C-8 «Continuar» después de una clave Mantener se dispara.
- [ ] C-9/10 Zip: entradas sin comprimir sin límite; plantilla borrada antes de reemplazarla.
- [x] C-11/12 Valores de archivo sin límites (resolución 0, comportamientos).
- [ ] C-13 Trazado abierto que vuelve al inicio se cierra solo.
- [ ] C-14…20 Menores (detach, expresiones en otras secuencias, operadores de forma al escalar, partículas,
      capas vacías, caché de poses, zip deflate).

### Red, cuenta y archivos
- [x] N-1 Dos copias de la app refrescan el mismo token y el servidor cierra la sesión (candado entre procesos).
- [x] N-2 El instalador se ejecuta elevado sin volver a comprobar su hash.
- [x] N-3/4 Recuperación: un solo archivo para todas las copias; escritura sin comprobar.
- [ ] N-5/6 Borrar una plantilla propia o cambiar el logo deja medios perdidos en proyectos.
- [x] N-7 Cerrar sesión mientras se refresca la vuelve a abrir.
- [x] N-8/9 Extras: descargas sin tiempo límite; `.part` completo que nunca se instala.
- [ ] N-10/11 Stock: descarga a carpeta sin permiso sigue bajando; 401 simultáneos.
- [ ] N-12 Fuentes de un `.flip` solo se instalan con el mismo usuario de Windows.
- [x] N-13 Mismo id de flujo en cuerpo, recorte y seguimiento.
- [ ] N-14…23 Menores (token en macOS, límites de preferencias, actualizaciones, textos sin traducir…).

### Motor de render y exportación
- [x] R-1 Expresiones sin límite (= C-1).
- [x] R-2/3 Máscaras animadas: una textura nueva por fotograma sin liberar (fuga de memoria de video en
      exportaciones largas) → caché propio con tope; la clave incluye el trazado de la máscara.
- [x] R-4 Audio de un clip con reasignación de tiempo y transición: desfasado todo el clip.
- [x] R-5 Los clips apagados se seguían oyendo.
- [x] R-6 Vista previa en RAM seguía renderizando al cerrar la app.
- [ ] R-7 Desenfoque de movimiento acumula en 8 bits (bandas, capa 1 % transparente).
- [ ] R-8 Mate que parpadea si su fotograma no está listo.
- [x] R-9 Una pista de mate oculta apagaba el mate (y escondía la capa).
- [ ] R-10/11 Texturas de 8K que quedan en el pool; tope fijo de 3 GiB de la vista previa en RAM.
- [ ] R-12 Audio con reasignación en congelados / más de 8×.
- [ ] R-14…21 Región de interés, estilos de capa con máscaras de carril, pin de esquinas, texturas enormes,
      operadores de forma recortados, repetidor con escala 0, luces sin padre, expresiones en el audio.
- [ ] R-22/23 H.264 por software hasta 8192; GIF con presets de 2K/4K/8K.
- [x] R-25 Mates mutuos (= A1-10). R-26 [x] Vista previa en RAM sin el recuadro de edición de texto.
### Interfaz (QML)
- [x] Q-1 Línea de volumen: el punto arrastrado dejaba de seguir al ratón. Q-7 [x] el nivel quedaba fijo tras deshacer.
- [x] Q-2 Deslizadores de Rebote/Elástico se cortaban a mitad (y un paso de deshacer por movimiento).
- [x] Q-3 Bosquejo de movimiento: el temporizador seguía moviendo el cabezal para siempre.
- [x] Q-4/5/6 Pluma: vértices elegidos tras deshacer, gesto cancelado, escribir en la forma equivocada.
- [ ] Q-8…12 Ctrl+clic en el volumen pasa al clip; claves tras soltar; menú de formas; tamaños de paneles.
- [x] Q-13 `Theme.fontSizeLg` no existe; «MOTION TOOLS» sin traducir. Q-15 [x] cierra solo su sesión.
- [ ] Q-14, Q-16…30 Menores (ver informe).
- [ ] Textos armados por concatenación (unidades, plurales) y botones de solo ícono sin nombre.

## Parte 2 — Fácil hasta para un niño (plan de UX)

Prioridad: P1 = confunde o bloquea al que empieza, P2 = roce, P3 = pulido. Detalle de cada punto en el informe de
UX (sesión 2026-10-30); aquí el resumen y el estado.

### Lo primero (P1)
- [ ] A1 Formato con tarjetas grandes («YouTube 16:9», «TikTok 9:16», «Cuadrado», «Como mi video»).
- [x] A2 Con «Automático» no preguntar ancho/alto/fps al soltar el primer clip.
- [ ] A3 Proyecto de ejemplo («Prueba con un ejemplo»).
- [ ] A4 Recorrido guiado de 4 globos (saltable, se repite desde Ayuda).
- [x] A5 El atajo «Plantillas» del inicio lleva a una lista vacía.
- [x] B1 Instalar los extras básicos (stickers, fuentes, sonidos) sin que el usuario tenga que buscarlos.
- [x] B2 Línea de tiempo vacía: botón principal «Importar medios».
- [ ] B3 Importar con el proyecto vacío pone los clips en la línea de tiempo (como CapCut).
- [x] C1 Títulos/Filtros/Efectos sin sesión abren en «Tendencias» (muro de «Inicia sesión»).
- [ ] C2 Clic en un filtro/efecto sin clip elegido: aplicarlo al clip bajo el cabezal.
- [x] C3 «Escenas» significa dos cosas distintas.
- [x] D1 Barra de pestañas de propiedades: 13 íconos sin nombre.
- [ ] D2 Video › Básico repite Transformar y Fusión.
- [ ] D3 Motion Tools y Curvas salen en todos los clips.
- [x] D4 Lo primero al elegir un clip es la explicación de fotogramas clave.
- [x] E1 «Dividir» corta todas las pistas aunque haya un clip elegido.
- [x] E2 Menú de clic derecho de ~45 entradas: lo básico arriba, «Avanzado» en submenú.
- [x] E3 Barra de la línea de tiempo: nombres en Dividir/Eliminar.
- [ ] F1 Barra de herramientas de After Effects sobre la vista previa siempre visible.
- [x] G1 Botón «Actualizar» siempre visible.
- [x] H1 Al terminar de exportar: «Abrir carpeta», «Reproducir».
- [x] H2 Destinos de exportación («TikTok/Reels», «YouTube», «WhatsApp», «Mejor calidad»).
- [ ] H3 Mostrar dónde se guarda dentro del diálogo.
- [x] I1 Recuperación: «Nueva sesión» descarta el trabajo sin decirlo.
- [ ] J1 Modo simple / Pro (simple por defecto).
- [x] K1–K4 Textos: «Same as project», «Seguir a (primario)», «Cortar (para mover)», «Imán», «Recortar el inicio».

### Después (P2/P3)
B4–B7, C4–C10, D5–D10, E4–E9, F2–F4, G2–G5, H4–H6, I2–I5, J2–J5, K5–K15 (ver informe de UX).

## Hecho además (2026-10-30)
- Nombres claros en español: «Imán», «Cortar (para mover)», «Recortar el inicio/final», «Seguir a (primario)»,
  «Stickers» (una sola palabra), «Detectar cortes», «Efectos de voz», «Sonidos», «Volumen igual que en redes»,
  «Agrupar», «Convertir el grupo en un video», «Hacer que vaya más fluido al editar», «Qué tapa este clip…»,
  «Velocidad con fotogramas clave».
- Extras básicos: la oferta de instalar al arrancar apuntaba a ids de Drift (`effects.core`…) que el índice de Flip
  no tiene; ahora `fonts.basic`, `stickers.emoji`, `stickers.emoji-animados`, `sonidos.efectos` (≈ 18 MB). Sigue sin
  abrirse sola: el ícono de Extras late.
- Ayuda › «Guía de uso» abre getflipstudio.com/guia.html.

## Decisiones para Jorge (no hechas a propósito)
- **Modo simple / Pro (J1)**: esconder por defecto lo de After Effects (barra de herramientas sobre la vista
  previa, Motion Tools, Curvas, cronómetros). Lo pediste en la 0.26, así que no lo escondo sin tu OK.
- **Exportar sin cuenta (A6)**: un niño muchas veces no tiene Google. ¿Las primeras exportaciones o 720p sin cuenta?
- **Proyecto de ejemplo (A3)**: necesita medios propios dentro del instalador (o en Stock).
- **Dos copias de la app (N-3)**: la recuperación sigue siendo un solo archivo; lo más simple sería no permitir dos
  copias abiertas a la vez.

## Cómo se probó
- Cada archivo C++ tocado: `g++ -fsyntax-only` con los headers reales; cada QML: `qmlformat` y `qmllint`.
- `lupdate` dos pasadas iguales; español 0 sin terminar.
- Prueba nueva `splitCutsOnlyThePickedClips` (tst_editorstate).
- **Falta:** CI en verde y probar en ventana (Dividir con selección, menú de clic derecho con Avanzado, Exportar con
  destinos y «Mostrar en la carpeta», formato Automático sin preguntar, línea de tiempo vacía, nombres en la barra de
  propiedades, línea de volumen, deslizadores de Rebote, máscara animada en exportación larga).
