# Kit de YouTube en Stock (2026-10-30)

Pedido de Jorge: replicar lo que trae un kit de After Effects comprado (VideoHive 19446027, «Youtube Promo Kit»,
en `F:\AFFTER EFECTS\After Effects\youtube kit\`) **adaptado a Flip**: diseños, colores y textos propios (nunca sus
archivos ni su aspecto exacto), todo 100 % editable, en **Stock › Kit de YouTube** con subcategorías.

## Estado
- **PUBLICADO (2026-10-30): 158 piezas en Stock › Kit de YouTube** (11 prototipos aprobados por Jorge + 147 de cinco
  tandas en paralelo, `templates_ytkit_a…e.py`, guía para las tandas en `tools/scene_templates/BRIEF-ytkit.md`).
  Cada tanda renderizó, revisó en hojas y corrigió; después el coordinador revisó todo (tamaños de los 16:9, que la
  placa salga con su texto) y se volvió a renderizar. Nombres en 13 idiomas (`tools/stock_i18n`).
- Servidor `flipstudio-api` rama `stock-ytkit` **desplegada**: tipo `ytkit` («Kit de YouTube», 15 idiomas) con las
  secciones como categorías (etiqueta `kit:<sección>`); las piezas son plantillas normales (`flip:template:<id>`),
  fuera de Plantillas salvo en «Mis plantillas». `minAppVersion` 0.26.0 (usan formas propias y recortar trazados).
- Contenido subido como delta (solo `ytk-*`, el índice raíz y `i18n`). El `publicar` local tenía además las 382
  animaciones «Extremas» (`ex-*`) que se bajaron de Stock el 2026-10-29; se movieron (Jorge, 2026-10-30) a
  `tienda\animaciones\descartadas-extremas-v1\publicar-sobrantes` y el índice local quedó igual al del servidor
  (219). `publish_delta.py` da 0 elementos distintos.
- **Trampa del motor (arreglada en 0.27, `TextAnimator.cpp`):** un texto tenía un solo ángulo de barrido: el de la
  salida pisaba el de la entrada. Las piezas del kit ya usan el mismo ángulo en las dos (o salida con fundido).

## Secciones (subcategorías)
| Clave | Nombre | Prototipo |
|---|---|---|
| aperturas | Aperturas de canal | `ytk-apertura-hexagono` |
| tipografia | Tipografía | `ytk-tipografia-bloque` |
| titulos-estilo | Títulos con estilo | `ytk-titulo-barras` |
| titulos-cineticos | Títulos cinéticos | `ytk-titulo-cinetico` |
| tercios | Tercios inferiores | `ytk-tercio-doble` |
| frases | Frases | `ytk-frase-comillas` |
| transiciones | Transiciones de formas | `ytk-transicion-paneles` |
| barras-info | Barras de información | `ytk-barra-info` |
| pantallas-finales | Pantallas finales | `ytk-pantalla-final` |
| redes | Redes sociales | `ytk-redes-lista` |
| elementos | Elementos | `ytk-elementos-set` |

Paleta: azul noche `#0B1A2E`, turquesa `#2EE6C8`, coral `#FF5D73`, sol `#FFD23F`. Sin logos de plataformas ni
el rojo de YouTube. El fondo de cada pieza es su propia pista «Fondo»: se borra y la pieza queda sobre el video.

## Reglas de diseño (Jorge)
- Un texto que sale de una línea o barra **nace de la línea**, nunca la cruza: revelado `wipe` con `angle=0`
  (de izquierda a derecha; el valor por defecto, −90, revela de abajo arriba), no `slide-right`.

## Para publicar más piezas
1. Tanda grande en `templates_ytkit*.py`; `build.py --only mod:templates_ytkit` (a `paquetes\`).
2. Subcategorías en Stock: hoy las categorías son planas (`publish.py` `CATEGORY_NAMES`). Hace falta
   `ytkit` en `CATEGORY_NAMES` y que el servidor/app agrupen por la etiqueta `kit:<sección>` (o un campo
   `subcategory` en el manifiesto) para el árbol «Kit de YouTube › …».
3. `publish.py` → `flipstudio-api/deploy/plantillas.ps1`, y traducciones en `tools/stock_i18n`.
