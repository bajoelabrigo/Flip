# Plan de la 0.14.0: Stock completo (acordado con Jorge, 2026-10-16)

Orden de Jorge: primero todo lo de Stock que no necesita versión nueva (servidor y contenido), al final la 0.14.0
con **todo** lo que sí, y al terminar: compilar una vez, probar en ventana y publicar todo.

## Ya sin versión nueva (servidor y contenido)
- Formato vertical/horizontal/cuadrado en todos los tipos, versiones 16:9 de superposiciones y fondos.
- Plantillas 1:1, historias de 15 s, anuncios de 6 s, miniaturas de YouTube. Música por ánimo (200).
- Stock en los 15 idiomas de la app (`flipstudio-api/src/services/i18n.ts` + `publicar/i18n/<lang>.json`).
- Filtros de plantillas que la 0.13.0 ya dibuja (enum): duración, cuántas fotos pide, con o sin música.
- `uses` (veces descargado) en cada elemento, para que la 0.14.0 lo muestre.

## 0.14.0: lo que necesita la app
Mapa del código (2026-10-16): `MarketClient::applyCatalog` (tipos de entrega aceptados), `importReadyFile` (a dónde va
lo descargado), `StockBrowser.qml` (`tileAspect`, filtros, lista de audio), `StockThumb.qml` (vista previa solo video),
`MarketTab.qml` (`DriftAssetsHome` sirve de modelo para un inicio por estantes).

### Tipos nuevos de Stock (entrega + contenido de 200 cada uno)
| Tipo | Entrega en la app | Contenido |
|---|---|---|
| LUTs y looks de color | `delivery: "lut"` → `AppController::importLut` (AppData/luts) | 200 `.cube` con `tools/luts` |
| Looks de «Ajustar» (color + viñeta + grano) | `delivery: "effect-preset"` → `importUserEffectPreset` | 200 |
| Estilos de texto y subtítulos virales | `delivery: "text-style"` → `importUserTextPreset` (Mis estilos) | 200 (incluye packs de subtítulos) |
| Textos animados (youtuber, karaoke, máquina de escribir, neón, rebote…) | `delivery: "text-animation"` → `importTextAnimationPreset` | 200 |
| Transiciones en pack | `delivery: "transition"` → paquete de usuario (`installUserPackage`) | nuevas, con vista previa animada |
| Formas y máscaras | catálogo de formas extensible (hoy fijo en `ShapeStyle::buildCatalog`) + `delivery: "shape"` | 200 |

### Que se encuentre lo bueno
- Inicio de Stock tipo tienda: estantes «Tendencias de la semana», «Nuevo», «Para esta fecha», «Más usadas» y
  colecciones («Kit de Navidad»…) desde un `GET /v1/market/home` nuevo.
- Búsqueda en todo Stock a la vez («cumpleaños de mi mamá» trae plantillas, música y stickers), con sinónimos.
- Tarjetas con la forma de cada elemento (9:16, 16:9, 1:1), vista previa de audio al pasar el mouse, «usada 1,2 k veces».

### Uso más rápido
- «Usar con mis fotos»: eliges fotos y sugiere plantillas por cantidad y orientación (`fillTemplateSlotsFromUrls`).
- Cambiar de plantilla sin perder el relleno (leer `sceneTemplateInfo`, volver a llenar por número de hueco).
- Ajuste automático a la música: al cambiar la canción, los cortes se reacomodan a los golpes (`analyzeBeats`).
- Formulario de textos de la plantilla (nombre del negocio, teléfono, precio) de una vez.
- Paquete de marca: logo, colores y tipografía guardados; las plantillas de Negocios los aplican.

### Que la gente vuelva
- Aviso de novedades en la app («12 plantillas nuevas») desde `GET /v1/market/news`.
- Favoritos sincronizados con la cuenta (hoy en QSettings `assetFavorites`).
- «Pide una plantilla»: formulario y votos (servidor).

### Además
- Las 3 categorías nuevas de plantillas (`slideshow`, `lowerthird`, `transition`) y las que vengan (`story15`, `ad6`,
  `thumbnail`…), con traducciones.
- Al final: CI de Windows, prueba en ventana con `mcp_e2e.py --window`, PR, tag, release, MSIX, novedades en la web.
