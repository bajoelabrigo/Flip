# Kit de YouTube en Stock (2026-10-30)

Pedido de Jorge: replicar lo que trae un kit de After Effects comprado (VideoHive 19446027, «Youtube Promo Kit»,
en `F:\AFFTER EFECTS\After Effects\youtube kit\`) **adaptado a Flip**: diseños, colores y textos propios (nunca sus
archivos ni su aspecto exacto), todo 100 % editable, en **Stock › Kit de YouTube** con subcategorías.

## Estado
- **Prototipos (11, uno por sección)**: `tools/scene_templates/templates_ytkit.py`, ids `ytk-*`, categoría `ytkit`,
  orden 7000–7099, la sección va en la primera etiqueta (`kit:<sección>`). Renderizados con el portable 0.27 en
  `tienda\plantillas\prototipos-ytkit` (fuera de `paquetes\`, así no se publican por error).
- **Falta el OK de Jorge** a los prototipos antes de hacer la tanda grande (~150: ~12–15 por sección, también 9:16).

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

## Para publicar (después del OK)
1. Tanda grande en `templates_ytkit*.py`; `build.py --only mod:templates_ytkit` (a `paquetes\`).
2. Subcategorías en Stock: hoy las categorías son planas (`publish.py` `CATEGORY_NAMES`). Hace falta
   `ytkit` en `CATEGORY_NAMES` y que el servidor/app agrupen por la etiqueta `kit:<sección>` (o un campo
   `subcategory` en el manifiesto) para el árbol «Kit de YouTube › …».
3. `publish.py` → `flipstudio-api/deploy/plantillas.ps1`, y traducciones en `tools/stock_i18n`.
