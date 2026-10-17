# Plan de Stock (acordado con Jorge, 2026-10-16)

Stock va a ser una **pieza central** de Flip Studio. Los pagos siguen para el final del proyecto: todo lo de
aquí es gratis.

**Reglas para todo el plan**
- Solo contenido **hecho por nosotros o con licencia CC0**. Pexels y Pixabay dejan usar su material, pero no armar
  con él un catálogo propio para redistribuirlo.
- **Para el mundo entero:** nada de fiestas ni contenido solo peruano o latino. Fechas, negocios y música que
  sirvan en cualquier país, con los textos de las plantillas en el idioma de cada usuario.
- Sin marcas ni logos en fotos de ejemplo, miniaturas o diseños.

## 1. Contenido nuevo

**Lo que más se usa en reels**
- **Efectos de texto animados:** títulos estilo «youtuber», karaoke palabra por palabra, máquina de escribir, neón
  que parpadea, texto 3D, texto que rebota al ritmo. Generados por código, como las plantillas.
- **Packs de subtítulos virales:** color en la palabra que se dice, emoji automático, contorno grueso.
- **Superposiciones (overlays):** luces filtradas, polvo y rayas de película, grano, bokeh, chispas, confeti, nieve,
  lluvia, humo, fuego, corazones flotando. Videos cortos con fondo transparente o en modo «Pantalla», generados con
  shaders y renderizados con la app.
- **Marcos y bordes:** Polaroid, tira de película, celular, ventana de chat, recuadro de red social (sin logos),
  marcos navideños y de cumpleaños.
- **Fondos animados:** degradados en movimiento, formas líquidas, cuadrícula retro, cielo estrellado.
- **Transiciones en pack:** las 39 de la app más paquetes temáticos (glitch, zoom con golpe, barrido de tinta,
  papel), con vista previa animada en Stock.

**Audio**
- **Efectos de sonido de tendencia:** whoosh, pop, «ding», clic de cámara, riser, impacto, risas, tambores y redoble.
  Fuentes CC0: freesound (filtrando por CC0), Sonniss GDC.
- **Música por ánimo y por duración:** cortes de 15, 30 y 60 s listos para reels, con el golpe marcado (ya está el
  analizador de ritmo).
- **Música del mundo libre:** estilos de distintas regiones, de fuentes CC0 o encargada.

**Color y look**
- **LUTs y filtros en pack:** cine, anime, película analógica, verano, nocturno, comida, piel cálida (generador en
  `tools/luts`).
- **Presets de «Ajustar»:** looks completos de un clic (color, viñeta y grano juntos).

**Gráficos**
- **Más stickers Lottie:** flechas a mano, subrayados, círculos de resaltar, emoji animados propios, iconos de redes
  genéricos (sin marca), «Suscríbete» y «Sígueme», precios y ofertas.
- **Tercios inferiores:** nombre y cargo, ubicación, @usuario.
- **Formas y máscaras:** corazones, estrellas, nubes de diálogo, recortes de papel.

**Fechas y negocios (para todo el mundo)**
- **Calendario internacional:** Navidad, Año Nuevo, San Valentín, Día de la Madre y del Padre, Halloween, Pascua,
  Año Nuevo Lunar, Ramadán y Eid, Diwali, Acción de Gracias, graduaciones, bodas, bautizos, cumpleaños,
  aniversarios, regreso a clases.
- **Negocios de cualquier país:** restaurante, cafetería, tienda de barrio, supermercado, ferretería, escuela,
  academia, inmobiliaria, comunidad religiosa (anuncio de reunión, frase del día), transporte y mudanzas.

**Plantillas por formato**
- Horizontales 16:9 para YouTube (intros, suscríbete, pantalla final), cuadradas para Facebook y carruseles de
  Instagram (fotos fijas).
- Plantillas de historias (15 s), de anuncios (6 s) y miniaturas de YouTube (imagen fija exportable).

## 2. Que se encuentre lo bueno
- **Inicio de Stock tipo tienda:** «Tendencias de la semana», «Nuevo», «Para esta fecha» (lo que viene en el
  calendario) y «Más usadas».
- **Colecciones:** p. ej. «Kit de Navidad» con plantillas, stickers, música y transiciones del mismo estilo.
- **Búsqueda por intención:** «cumpleaños de mi mamá» o «promoción de restaurante» encuentra plantillas, música y
  stickers a la vez (etiquetas con sinónimos, en todos los idiomas de la app).
- **Filtros:** formato (9:16, 16:9, 1:1), cuántas fotos pide, duración, con o sin música.
- **Vista previa al pasar el mouse**, sin abrir nada.
- **Contador de usos** («usada 1.2k veces»).

## 3. Uso más rápido
- **«Usar con mis fotos»:** eliges las fotos primero y la app sugiere plantillas que encajan (número de fotos y
  orientación).
- **Cambiar de plantilla sin perder el relleno:** probar varias plantillas con las mismas fotos.
- **Ajuste automático a la música:** cambias la canción y los cortes se reacomodan al nuevo ritmo.
- **Texto de la plantilla con IA local:** nombre del negocio, teléfono y precio en un solo formulario.
- **Paquete de marca:** logo, colores y tipografía guardados; las plantillas de Negocios los aplican solas.

## 4. Que la gente vuelva
- **Novedades cada semana**, con aviso en la app («12 plantillas nuevas para Navidad»).
- **Favoritos y colecciones propias** sincronizados con la cuenta (la biblioteca ya existe).
- **Pedidos de la comunidad:** botón «Pide una plantilla» con un formulario; se hacen las más votadas.
- **Más adelante, con los pagos:** plantillas de creadores, un «Pro» opcional y tiendas de usuarios.

## 5. Preparar el crecimiento (Jorge, 2026-10-16)
Hacerlo **al llegar a unas 10 000 descargas**, antes de que haga falta (uno o dos días de trabajo). La app corre en
la computadora de cada uno, así que lo que crece son los servidores de Stock, cuentas y extras.
- **Pexels y Pixabay:** pedir límites más altos (la clave gratis de Pexels trae unas 200 búsquedas por hora) y guardar
  en caché del servidor las búsquedas repetidas.
- **CDN para lo pesado:** las plantillas (hoy en el VPS) y los extras de IA (hoy en GitHub) a Cloudflare R2 o Bunny.
  Basta cambiar las URLs del índice.
- **MongoDB Atlas:** revisar el plan del clúster (el gratuito M0 tiene 512 MB) y resumir las estadísticas viejas.
- **Reporte de fallos dentro de la app** y una página de preguntas frecuentes.
- Después: segundo servidor detrás de Cloudflare si el VPS no da abasto, y límites por cuenta contra la descarga
  masiva de Stock.
- Costo estimado con un millón de descargas y todo gratis: unos 100-300 USD al mes.

## Estado
Jorge (2026-10-16): mirar las tendencias de CapCut, Instagram, Premiere, After Effects, Filmora… y hacer **al menos
200 de cada tipo**, con calma y calidad primero.

### Desplegado el 2026-10-17 (contenido y servidor; la app llega con la 0.14.0)
- **Plantillas: 883** (533 + **350 de formatos nuevos**: publicaciones 1:1, historias de 15 s, anuncios de 6 s,
  miniaturas de YouTube, tercios inferiores, presentaciones de fotos, transiciones y separadores), con filtro de
  formato y «Formato» (vertical, horizontal, cuadrado) en todos los tipos.
- **Animaciones (stickers Lottie): 222** en 14 categorías (nuevas: fechas especiales, comida, deportes, iconos).
- **Superposiciones: 400** (200 verticales + 200 horizontales 16:9), WebM con transparencia: luces, partículas,
  celebración, amor, garabatos, clima, película, glitch, cámara, marcos y texturas.
- **Sonidos: 200** (sintetizados): transiciones, impactos, botones, juegos, magia, comedia, suspenso, ritmo.
- **Fondos animados: 400** (200 verticales + 200 horizontales) en bucle: degradados, geométricos, luces, texturas
  y fechas especiales.
- **Música: 328 cortes** por ánimo (15, 30 y 60 s; 9 pistas FMA en espera de oírlas para descartar voces), con la
  duración nominal en la tarjeta.
- **LUTs: 200** (`.cube` de 33 puntos, tarjeta con la foto de muestra partida antes/después), **looks de Ajustar:
  209**, **estilos de texto: 200**, **textos animados: 200**, **transiciones: 200** y **formas: 200**.
- **i18n:** los 13 idiomas de `tools/stock_i18n` cubren **3.642 elementos y 145 categorías** (`build.py --strict`).
- **Servidor (`flipstudio-api`, rama `stock-0.14`):** cada tipo con su `delivery`, búsqueda en todo Stock a la vez
  con sinónimos, inicio tipo tienda (`/v1/market/home` con estantes y colecciones), novedades (`/v1/market/news`),
  pedidos con votos (`/v1/market/requests`) y favoritos en la cuenta (`/v1/me/favorites`).
- Todo subido con `flipstudio-api/deploy/plantillas.ps1` (swap de la carpeta entera) y `deploy/deploy.ps1`.

### Lo que llega con la 0.14.0 de la app (rama `flip/v0.14.0`)
Instalación de los tipos nuevos (LUT, look, estilo y texto animado, transición y forma), inicio de Stock tipo
tienda, tarjetas con la forma de cada elemento y **tarjetas anchas** (`thumbWide`/`previewWide`), elegir variante
por el filtro «Formato», vista previa de audio al pasar el mouse, contador de usos, favoritos y novedades de la
cuenta, «Usar con mis fotos», «Cambiar plantilla», cortes al ritmo, formulario de textos y «Mi marca».

### Pendiente para después de la 0.14.0
- **Pagos** (Jorge: al final del proyecto), tiendas de los usuarios y todo lo de cobrar.
- Ideas del plan que no entraron: caché de búsquedas de Pexels/Pixabay y CDN para lo pesado (a las 10.000 descargas,
  punto 5 del plan).


---

## 0.15.0: más Stock (Jorge, 2026-10-16, para empezar el 2026-10-17)
Rama `flip/v0.15.0` (sale de `main` en `0f015`). Jorge: «vamos a hacer todo eso». **Nada de nombres de youtubers**
en títulos, etiquetas ni sinónimos (MrBeast es marca registrada): el estilo, con nombres propios («Reto extremo»).

### A. Cambios en la app y en el contenido que ya está
1. **Menú de Stock:** arriba solo **Todos, Videos y Fotos** (en `MarketTab.qml`; SFX si está disponible). El resto
   de los tipos (Plantillas, Animaciones, Superposiciones, Fondos, Música, Sonidos, LUTs, Looks, Estilos de texto,
   Textos animados, Transiciones, Formas) va **abajo en botones (chips)**, como en Texto (`TextAssetsTab.qml`), con
   `CategoryScrollOn`: al llegar al final de un tipo, la rueda abre el siguiente. En Stock hay paginación
   (`Market.hasMore` / `loadMore` en `atYEnd`): el paso al siguiente tipo solo cuando ya no hay más páginas y no se
   está buscando. Idea de diseño: los chips cuelgan de «Todos» (primer chip «Inicio» = los estantes); Videos y Fotos
   son Pexels/Pixabay.
2. **Quitar todo Halloween** (Jorge no lo quiere). Ya ubicado (2026-10-16): el kit `kit-halloween` de
   `tienda\plantillas\publicar\colecciones.json`, la fecha `halloween` de `flipstudio-api/src/services/seasons.ts`
   (línea ~147), y elementos en los índices de `publicar`: plantillas (`index.json`, p. ej. `halloween-photo-dump`,
   `halloween-revelacion-disfraz`, `halloween-truco-o-trato`, `h-fecha-halloween`), fondos, estilos de texto,
   música, LUTs, looks, stickers y superposiciones (contar por id/título/etiquetas, no por la palabra suelta). Quitar
   también de los generadores (`tools/*/designs*.py`, `templates_*.py`, `music/catalog.py`, `BRIEF.md`) para que no
   vuelva al regenerar, y de `tools/stock_i18n`. **Día de Muertos no es Halloween**: se queda. Subir con
   `deploy/plantillas.ps1` (swap de la carpeta entera, 4,6 GB).
3. **Animación al pasar el mouse en todas las tarjetas** (Stock, plantillas, efectos y el resto de pestañas): el
   patrón es el de `TextAssetsTab.qml` (`scale` 1.02 al pasar, 0.97 al presionar, `Behavior` con
   `Theme.durationFast`). Revisar `StockThumb`, `StockHome`, `SceneTemplateBrowser` y cada pestaña de recursos.

**Estado de A (2026-10-17): hecho, sin desplegar.**
- App (`6bfff`): pestañas Todos/Videos/Fotos; los tipos propios en chips bajo «Todos» (`MarketTab.qml`, primero
  «Inicio» = estantes); `CategoryScrollOn` en `StockBrowser.qml` (solo sin búsqueda y sin más páginas). Animación al
  pasar el mouse en Stock, Plantillas, Máscaras, Stickers, Transiciones, Subtítulos, LUT, looks de texto, voces,
  accesorios de cara, formas de máscara y favoritos de la cuenta. «Inicio» traducido en los 17 catálogos.
- Halloween fuera (`6e6e3`): 16 elementos borrados de `publicar` (6 plantillas, 4 fondos, 3 stickers, el look, el
  LUT y el estilo «Calabaza»; los archivos quedan en `tienda\plantillas\quitado-halloween`), el kit, y de los
  generadores. Lo genérico se queda sin la etiqueta: la música de miedo pasa a «Misterio y suspenso» y los estilos
  «Terror y Halloween» a «Terror y misterio» (sirven para el estilo true crime). i18n: 3.626 elementos, `--strict`
  sin faltantes, `publicar\i18n` regenerado. Servidor: rama `stock-0.15` (`a4a75`, 30 pruebas) sin la temporada.
- **Falta:** desplegar `publicar` (con `deploy/plantillas.ps1`) y el servidor junto con el contenido nuevo.

### B. 300 plantillas al estilo de youtubers famosos
Repartidas entre los 16 estilos (unas 18–20 por estilo), en vertical y 16:9 donde tenga sentido:
1. **Reto extremo:** contador de dinero gigante, «$1 vs $1.000.000», «Último en salir gana», «Día 1 / Día 100»,
   temporizador en pantalla, textos enormes con borde grueso.
2. **Miniaturas que se hacen clic:** cara sorprendida, flecha roja, círculo, texto de 3 palabras, fondo saturado
   (16:9).
3. **Subtítulos que saltan palabra por palabra:** palabra resaltada en color, emoji y zoom al golpe.
4. **Vlog de ciudad:** títulos sobre la calle, timelapse, mapa con la ruta.
5. **Explicador:** resaltador sobre el texto, recortes de periódico, mapa con zoom, datos que aparecen.
6. **Reseña de tecnología:** unboxing limpio, ficha técnica, comparación lado a lado.
7. **Gaming y streamer:** marco para la cámara de la cara, alerta de suscriptor, «GG», marcador, momentos destacados.
8. **Reacción:** video en grande y la cara en una esquina, con zoom en las reacciones.
9. **Top 10 / ranking:** cuenta regresiva con números grandes y la revelación del primero.
10. **Podcast en video:** dos cámaras con nombres, cortes cortos, onda de audio.
11. **Entrevista en la calle:** micrófono, pregunta arriba, respuestas.
12. **Misterio / true crime:** expediente, fotos con chinches e hilo rojo, máquina de escribir.
13. **«Un día en mi vida» y «Arréglate conmigo»:** hora en pantalla, lista de pasos.
14. **Cocina:** ingredientes que aparecen, pasos numerados, plato final.
15. **Fitness:** contador de repeticiones, temporizador por serie, antes y después.
16. **Intros de canal (5 s) y pantallas finales de YouTube (20 s)** con huecos para «el siguiente video» y
    «suscríbete».

### C. Otro contenido para Stock
- **Sonidos de youtuber** propios: whoosh, ding, boom, redoble, «error».
- **Superposiciones de youtuber:** botones de suscribirse y campana, flechas, círculos, «Me gusta», emojis 3D.
- **Marcos para la cámara de la cara** (gaming y podcast).
- **Contadores animados** de dinero, seguidores y días.
- **Transiciones de youtuber:** paneo rápido, zoom de golpe, glitch, cambio de escena con sonido.
- **Tercios inferiores con tus redes:** @usuario con el logo de cada red.

**Estado de C (2026-10-17): hecho y publicado en `publicar`, sin desplegar** (`e3193`). 43 sonidos «Youtuber»
(`tools/sounds`), 40 superposiciones «Youtuber» ×2 (vertical y `-h`) y 24 «Marcos para la cámara» con su propio
tamaño (1080×1080 / 1280×720, hueco transparente; `tools/overlays/designs_f.py`, `designs_g.py`, `kit.py`), 23
transiciones «Youtuber» (`fam_youtuber.py`, cada una dice qué sonido le va), 20 «Contadores» (categoría nueva
`counter` también en `SceneTemplateCatalog.cpp`; cuentan con cortes rápidos, el número final es editable) y 24
tercios inferiores de redes (`templates_c1.py`, `templates_c2.py`). Fuera `yt-boton-play` (era el logo de YouTube como
adorno; en `tienda\superposiciones\descartado`). i18n: 3.840 elementos y 150 categorías, `--strict` sin faltantes.
Límite: si el usuario cambia el número final de un contador, el conteo sigue con los valores de ejemplo (haría
falta una animación de contador en el motor).

### D. Kits nuevos (Jorge: «esa sección me gusta»)
Cada kit junta plantillas, música, sonidos, stickers, superposiciones y fondos del mismo tema y sale en el inicio de
Stock (`colecciones.json`; los de fecha con `from`/`to`).
- **Por tipo de creador:** YouTuber principiante, Reto extremo, Podcast, Gaming, Cocina, Fitness, Viajes, Tecnología.
- **Para negocios:** Negocio local, Lanzamiento de producto, Inmobiliaria, Clases y cursos.
- **Por fecha, para todo el mundo:** San Valentín, Día de la Madre, Día del Padre, Graduación, Verano, Vuelta a
  clases, Año Nuevo, Bodas, Cumpleaños.

**Estado de D (2026-10-17): hecho, sin desplegar.** Los kits viven ahora en el repo: `tools/stock_kits/kits.py`
(fuente de `publicar/colecciones.json`, valida que cada elemento exista, nombres en los 15 idiomas). 29 kits y 389
elementos: los 8 de antes (sin Halloween, traducidos y con lo nuevo) + 21 nuevos. Por fecha: Año Nuevo (12-20 a
01-07), graduación, Día del Padre, verano y vuelta a clases. Para creadores: empezar en YouTube, identidad del canal,
retos, rankings, podcast, reacciones y entrevistas, gaming, cocina, fitness, tecnología, vlog, explicativos y misterio.
Para negocios: lanzamiento, inmobiliaria, clases y cursos. Las fechas siguen el calendario del hemisferio norte
(un solo rango por kit).

### Orden sugerido
A (app y limpieza) → C y B (contenido, con hojas de contacto para revisar) → D (kits, cuando exista el contenido) →
i18n de todo lo nuevo en los 13 idiomas → desplegar contenido → compilar una vez, probar en ventana y publicar.
