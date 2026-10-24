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
- [ ] Inventario
- [x] Escritorio (rama `flip/stock-paneles`, código; ver abajo) — [ ] en ventana
- [ ] Web
- [ ] Prueba en ventana y en el navegador, lado a lado
