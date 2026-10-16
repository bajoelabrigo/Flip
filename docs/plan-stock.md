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

