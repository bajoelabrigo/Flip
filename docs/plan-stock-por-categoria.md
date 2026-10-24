# Lo de Stock también en su categoría, con la llamita (pedido de Jorge, 2026-10-24)

Jorge: «vamos a colocar de stock (sin eliminar Stock) lo que dice efecto en efectos, transiciones en transiciones, así
cada categoría donde corresponde según su tipo y le ponemos el símbolo del fuego; también el símbolo del fuego en todas
las tendencias en todo el stock, animaciones y animaciones de texto, y revisamos que todo coincida en web y escritorio».

## Qué hay que hacer
1. **Cada tipo de Stock también en su panel** (Stock sigue igual): efectos → Efectos, transiciones → Transiciones,
   LUTs → Filtros, looks → Efectos/Mis efectos, estilos de texto → Títulos, animaciones de texto → Texto › Animación,
   formas → Formas, stickers/animaciones Lottie → Stickers, música y sonidos → Audio, plantillas → Plantillas,
   superposiciones y fondos → donde van en cada app. Primero: inventario de qué tipo ya aparece en su panel y dónde
   (escritorio y web), y de qué falta.
2. **Llamita naranja** (`TrendBadge.qml` / `TrendBadge` de la web) en las tarjetas de Stock que son tendencia (el
   servidor ordena las tendencias primero: ver qué marca las define, `uses`/`week` o etiqueta `trending`), en Stock y en
   cada panel donde aparezcan, también en animaciones y animaciones de texto.
3. **Revisar que coincida** web y escritorio, panel por panel, en ventana y en el navegador (con capturas).

## Escritorio (rama `flip/stock-paneles`)

Lo mismo que la web, con el código de siempre de Efectos/Títulos › Tendencias convertido en algo común:
- **`MarketClient`** (C++): `fetchPanelList(tipo, categorías, más)` / `panelList(clave)` — la Tendencia de un tipo
  (los 24 más usados, como `topTrends` de la web: estantería de la semana de `/home`, 3 páginas de `type=all` por usos
  y la primera página del tipo) o lo de Stock de las categorías de un chip, página a página. `stockChips(tipo, chips
  del panel)` reparte con la tabla `chipForCategory` (la `STOCK_CHIP_MAP` de la web con los ids de chip del escritorio:
  efectos → `dreamy`, `impact`, `glitch`, `retro`, `artistic`; transiciones, música, sonidos, stickers y formas con
  los mismos ids que la web; estilos de texto: `titulos` → Básicos y el resto en chips propios). `isTrendingItem` y
  `weeklyTrendingIds` para la llamita; `placedId(item)` dice qué quedó instalado (la instalación devuelve ahora el id
  local: `InstallDone` lleva `localId`). Efectos y Títulos › Tendencias pasan a ser estas listas (24, sin páginas).
- **`StockPanelCards.qml`**: las tarjetas de Stock de un panel (16:9, cuadradas, 9:16 o filas de audio), con llamita,
  estrella, marca de descarga, «Inicia sesión» en Tendencias sin cuenta y un clic que baja, instala y aplica. Va
  sola (Tendencias, chips propios) o como `footer` de la cuadrícula del panel (lo de Stock después de lo propio).
- **`StockThumb.qml`** lleva la llamita y la estrella (solo lo nuestro, `flip:`): también las tarjetas de la pestaña Stock.
- **`addAssetClipWhenReady`**: lo que Stock deja en Medios (música, sonidos, stickers, superposiciones, fondos) va a la
  pista cuando ya se sabe su duración (la trampa de los 5 s de `addSoundEffect`).

| Panel del escritorio | Tendencias | Reparto en chips | Estrellas nuevas |
|---|---|---|---|
| Efectos (`EffectBrowser`) | efectos (y voces) | sí + chip «Superposiciones» | Stock (`effects`, `voices`) |
| Filtros › Efectos de color (`EffectBrowser stockType: "look"`) | looks | chips propios | Stock (`looks`) |
| Filtros (`FiltersTab`) | LUTs | chips propios | LUTs propios y de Stock (`luts`, clave `factory:cinematic` como la web), chip ★ nuevo |
| Transiciones | transiciones | sí | Stock (`transitions`) |
| Títulos (`TextAssetsTab`) | estilos de texto | `titulos` → Básicos, resto chips propios | Stock (`textStyles`) |
| Texto › Animación (`TextInspector`) | «De Stock» bajo Tendencias | no (como la web) | Stock en ★ («Favoritos de Stock») |
| Video › Animación (`AnimationInspector`) | — | — | animaciones de clip (`clipAnimations`), chip Favoritos nuevo |
| Stickers | Lottie | sí + chip «Fondos» | Stock (`stickers`) |
| Formas | formas | sí | Stock (`shapes`) |
| Música / Efectos de sonido (`SoundEffectsTab`) | música / sonidos | sí | Stock (`music`, `sounds`) |
| Plantillas (`SceneTemplateBrowser`) | plantillas | no | Stock (`sceneTemplates`) |
| Máscaras (`MasksTab`) | — | — | máscaras (`masks`, `rectangle`/`bars` se guardan `rect`/`bar` como la web), filtro ★ |

Mi cuenta › Favoritos muestra también `looks`, `luts`, `sceneTemplates`, `clipAnimations` y `masks`, y en cada grupo
lo de Stock (bajado o no). Los favoritos se sincronizan con la cuenta grupo por grupo (`assetFavoritesMap`): los
grupos nuevos viajan solos. El grupo `sounds` del escritorio también lo usan los efectos de audio, igual que en la web.

## Estado
- [x] Inventario (web; ver abajo)
- [x] Escritorio (rama `flip/stock-paneles`, CI run 40076950755 en verde; ver abajo) — [ ] en ventana
- [x] Web (rama `web/v022`, desplegada el 2026-10-24)
- [ ] Prueba en ventana y en el navegador, lado a lado

## Inventario (web)

Hecho en `flipstudio-app`, rama `web/stock-categorias` (commit `0a707`, sin desplegar). «Antes» es como estaba en
`web/movil-capcut`.

| Tipo de Stock | Panel de la web | Antes | Ahora |
|---|---|---|---|
| `effect` (efectos y 9 voces) | Efectos | Tendencias = todo el catálogo | Tendencias = los 24 más usados; el resto en Luz, Glitch, Retro, Estilo, Distorsión + chips propios (Desenfoque, Abrir y cerrar, IA, Voz) |
| `overlay` | Efectos › Superposiciones | Solo en Stock (iba a Medios) | Chip propio después de Tendencias; un clic lo pone en una pista nueva arriba |
| `look` | Filtros › Efectos de color | Solo en Stock | Tendencias + un chip por categoría de Stock (Cine, Película analógica…) |
| `lut` | Filtros › LUTs | Solo en Stock (quedaba en Importados) | Tendencias + un chip por categoría de Stock; un clic lo importa y lo pone en el clip |
| `transition` | Transiciones | Solo las instaladas, en «Stock» | Tendencias + repartidas en Básicas, Cine, Geométricas, Glitch, Líquidas + chips propios (Zoom y golpe, 3D y papel, Divertidas, Youtuber) |
| `text-style` | Títulos › Texto | Tendencias = los 590 | Tendencias = los 24 más usados; el resto en Básicos, Redes, Subtítulos virales, Ventas, Frases + chips propios (Neón, 3D y relieve, Tercios inferiores…) |
| `text-animation` | Texto › Animación (inspector) | Solo «De Stock» con las instaladas | Tendencias › «De Stock» con los más usados; un clic la baja y la pone en Entrada/Salida/Bucle si es para esa pestaña. No se reparte por familias: el servidor no dice para qué pestaña es cada una antes de bajarla |
| `animation` (Lottie) | Stickers › Pegatinas | Solo en Stock | Tendencias + repartidas en los chips del paquete (Celebración, Amor y emociones, Naturaleza, Señales) + chips propios |
| `background` | Stickers › Pegatinas › Fondos | Solo en Stock | Chip propio con todos los fondos |
| `shape` | Stickers › Formas | Solo las instaladas, en «Stock» | Tendencias + repartidas en Básico, Flechas, Bocadillos, Divertido + chips propios |
| `music` | Audio › Música | Solo en Stock | Tendencias (filas con «Escuchar» y «+») + repartida por ánimo + chips propios |
| `sound` | Audio › Efectos de sonido | Solo en Stock | Tendencias + repartidos (Transiciones, Botones, Impactos, Comedia, Magia) + chips propios |
| `template` | Plantillas › Mis plantillas | Solo las bajadas, en «De Stock» | Chips ★ · Tendencias · Mis plantillas; un clic hace lo mismo que «Usar» en Stock (abre la plantilla como proyecto nuevo). No se reparte: el panel no tiene subcategorías |

**Cómo se reparte** (`src/stock/stockPanels.ts`, con pruebas):
- `STOCK_CHIP_MAP[tipo][categoría del servidor] = chip del panel`.
- Una categoría sin chip que le corresponda (o cuyo chip no existe en ese panel, por ejemplo otro paquete de
  stickers) va a un chip propio, `stock:<categoría>`, con el nombre que le da el servidor, después de los del panel.
- Dentro de un chip se ve primero lo del panel y después lo de Stock (con su marca de descarga y la llamita si es
  tendencia). Las categorías salen del filtro `category` de `/v1/market/catalog`.
- Sin sesión no se ven los chips de Stock (el servidor pide cuenta para buscar). Tendencias muestra «Inicia sesión».

**Tendencias = lo más usado** (`topTrends`): primero lo de la estantería «Tendencias de la semana» de
`/v1/market/home` (lo más bajado en 7 días), después lo más usado de «Todo» (`type=all`, que el servidor ordena por
usos; 3 páginas, compartidas por todos los tipos) y, para completar, la primera página del tipo. Son 24 como mucho.
El buscador de un tipo concreto **no** ordena por usos: si el servidor sumara `sort=uses` o `trending: true` por
elemento, alcanzaría con una sola petición.

**Llamita** (`isTrendingStock`): el servidor la marca (`trending: true`, todavía no existe), está en la estantería de
la semana, su categoría es `tendencias`/`trending` (estilos de texto), o es un efecto de Stock (todos llevan la
etiqueta `trending`).

**Favoritos.** Clave de un elemento de Stock: `stock:<tipo>:<id>`, por ejemplo `stock:transition:glitch-destello`.
Se guarda en el grupo del panel; el escritorio tiene que usar las mismas claves y grupos:

| Grupo | Qué guarda | Ya tenía estrella | Nuevo |
|---|---|---|---|
| `effects` | efectos propios, efectos de Stock, superposiciones | sí | Stock |
| `voices` | voces (AudioTab) y voces de Stock | sí | Stock |
| `looks` | looks de Stock | — | nuevo |
| `luts` | LUTs (clave del LUT) y LUTs de Stock | — | nuevo, con chip ★ |
| `transitions` | transiciones y de Stock | sí | Stock |
| `textStyles` | estilos de texto y de Stock | sí | Stock |
| `textAnimations` | animaciones de texto (id del preajuste) y de Stock | — | nuevo, chip «★ Favoritos» |
| `clipAnimations` | animaciones de clip (id del preajuste) | — | nuevo, chip «★ Favoritos» |
| `stickers` | stickers, Lottie y fondos de Stock | sí | Stock |
| `shapes` | formas y de Stock | sí | Stock |
| `masks` | formas de máscara (id) | — | nuevo, con chip ★ |
| `music`, `sounds` | música y sonidos; `sounds` también lo usan los efectos de audio | sí | Stock |
| `sceneTemplates` | plantillas propias (id) y de Stock | — | nuevo, chip ★ |
| `templates`, `textBubbles`, `textEffects`, `retouch` | sin cambios | sí | — |

Un favorito de Stock se ve en el ★ del panel antes de bajarlo: al marcarlo se guarda cómo se ve
(`flip.stockFavoriteItems`); uno que viene de otro equipo se dibuja desde la clave (título desde el id, miniatura en
`/plantillas/<carpeta>/<id>/thumbnail.png`). Mi cuenta › Favoritos cuenta también `voices`, `looks`, `luts`,
`sceneTemplates` y `textAnimations`. Sin estrella todavía: los estilos de Subtítulos (es elegir un estilo, no
añadir algo) y Mis efectos.

**Comprobado en el navegador** (Playwright, con una sesión de prueba y el servidor imitado con los `index.json` reales
de `tienda\plantillas\publicar`; capturas en el scratchpad de la sesión, `stock\dentro2`, `stock\fuera`, `stock\movil2`):
sin sesión, cada panel abre en Tendencias con «Inicia sesión»; con sesión, chips repartidos en todos los paneles, un clic
añade forma, música, sticker Lottie, transición, LUT y animación de texto; estrella → aparece en ★; en el celular,
Música, Stickers, Transiciones y Efectos igual. **No** se probó contra el servidor real con una cuenta de Google.

## Escritorio, para replicar
Por panel: chips `★ · Tendencias · <los del panel> · <categorías de Stock sin chip>`; en Tendencias, tarjetas de Stock
(16:9 efectos/transiciones/LUTs/looks/superposiciones/fondos/animaciones de texto, cuadradas stickers y formas, 9:16
plantillas, filas con «Escuchar» y «+» música y sonidos) con llamita arriba a la izquierda, estrella arriba a la
derecha y marca de descarga abajo a la derecha; en los demás chips, lo propio y debajo lo de Stock de esas categorías.
