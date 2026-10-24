# Próxima versión (0.22): fotogramas clave como After Effects, Mi cuenta que aplica, Stock en cada panel

Pedido de Jorge (2026-10-24). Orden acordado: **primero la web** (se ve el cambio enseguida), después el escritorio.

## 1. Fotogramas clave como After Effects
Jorge: «cuando se pone el keyframe siempre sale el rombo; quiero los tipos de After Effects, imán cuando me poso sobre un
key con la barra de tiempo, seleccionar uno o varios y poner recto, suave, salto o abrir las curvas como en móviles;
al pasar sobre los keys, clic derecho con las opciones».

- Icono por mitades (izquierda = cómo llega, derecha = cómo sale): rombo = recto, muesca = suave, cuadrado = salto,
  redondo = curva propia. Mismas figuras en web (`keyTypes.ts › keyIconPaths`) y escritorio (`KeyframeGlyph.qml`).
- Menú: Recto (Ctrl+Alt+K), Suave (F9), Suave al llegar (Mayús+F9), Suave al salir (Ctrl+Mayús+F9), Salto
  (Ctrl+Alt+H), Curvas… (las 17 del celular), Eliminar. «Suave al llegar/salir» y no «Entrada/Salida suave»: esos
  nombres ya los usan las curvas de CapCut con el sentido contrario.
- **Web** (`flipstudio-app` rama `web/keyframes-ae`, commit `b8f34`): `src/timeline/keyTypes.ts` (+ pruebas),
  `components/KeyframeTools.tsx`, `Timeline.tsx` (clic/Ctrl/Mayús, arrastrar juntos, Supr, menú, imán con los
  fotogramas clave), `KeyedSlider.tsx` (Recto/Suave/Salto por fotograma, con icono), `desktopTransform.ts` (lo suave
  de un solo lado va y vuelve del escritorio). Probado en el navegador: `scripts/check-key-types.mjs`.
- **Escritorio** (rama `flip/v0.21.1`, commit `84337`): `TrackKeyframeRows.qml` (las filas del triángulo de la pista),
  `KeyframeGlyph.qml`, `KeyframeCurvesPopup.qml`, `AppController::setKeyframesEasing / setKeyframesCurve /
  removeKeyframes`, imán con fotogramas clave en `AppController::snapTime`. Textos en 12 idiomas.
  CI de prueba: run 40072114035. **Falta: probar en ventana.**
- Pendiente menor: en el escritorio Supr no borra los fotogramas elegidos (Supr es de los clips en `Main.qml`); se
  borran desde el menú. Arrastrar varios a la vez: solo en la web.

## 2. Mi cuenta › Descargas: que se pueda usar
Jorge: «al darle clic a algo de esa lista no lo aplica; deberían salir 2 opciones: poner en medios o aplicar en la pista».
- **Web** (rama `web/cuenta-usar`, `dcda0` + `6525e`): «Añadir a Medios» / «Guardar en <panel>» y «Añadir a la pista»
  / «Aplicar» (clic en la fila = aplicar). Tabla por tipo en `src/stock/libraryActions.ts`. Probado con servidor
  simulado (`scripts/check-account-downloads.mjs`); falta con la cuenta real.
- **Escritorio**: en curso (rama `flip/cuenta-usar`).

## 3. Stock también en cada panel, Tendencias primero
Ver `docs/plan-stock-por-categoria.md`. Jorge (2026-10-24): Tendencias reúne **solo lo más usado**; además cada
elemento de Stock va en la subcategoría de su panel según su tipo (un texto neón en Títulos › Neón, etc.).
- **Web**: en curso (rama `web/stock-categorias`).
- **Escritorio** (rama `flip/stock-paneles`, desde `flip/v0.21.1`): hecho en código, ver
  `docs/plan-stock-por-categoria.md` › «Escritorio». **Falta: probar en ventana** con la cuenta.

## 4. Lo que ya estaba pendiente
- 0.21.1: medios ocultos de la web también ocultos en Medios (`webHidden`), probar en ventana con un `.flip` de la web
  que tenga un recorte de persona.
- Cuando la Store apruebe la 0.21.0: TXT `version` = 0.21.0 (Jorge).

## Estado (2026-10-24, mañana)
- [x] Fotogramas clave: web, **desplegada** (rama `web/v022`, comprobada en getflipstudio.com/editor con
      `scripts/check-key-types.mjs`).
- [x] Fotogramas clave: escritorio, **probado en ventana** (portable de `84337`, run 40072114035): figuras, menú,
      Suave al salir, Curvas › Salida de cubo, imán del cabezal. Arreglado después: «Salto» (decía «Mantener»),
      Curvas ya no se sale de la ventana (`a1438`, sin compilar).
- [x] Mi cuenta: web desplegada — [ ] escritorio (rama `flip/cuenta-usar`, en CI)
- [x] Stock en cada panel + estrellas en todo: web desplegada (`web/stock-categorias` unida en `web/v022`; probada
      con servidor simulado, falta con la cuenta real) — [ ] escritorio (rama `flip/stock-paneles`, en CI)
- [x] Favoritos también en Mis efectos y estilos de subtítulos (web).
- [x] Textos nuevos de la web en 15 idiomas (`f6a72`).
- [x] Unidas `flip/stock-paneles`, `flip/v0.21.1` y `flip/cuenta-usar` en la rama **`flip/v0.22.0`** (`d24b1`).
      Conflicto resuelto: el aviso de instalación de Stock lleva `(…, error, localId)` (orden de Stock); en Mi cuenta
      un LUT se aplica por su archivo (su id es `user:<archivo>`).
- [x] Fotogramas clave (Jorge, 2026-10-24, tarde): la elegida **roja y más grande** (17 px; el resto 13), el cabezal
      ya no ilumina las claves de ese instante (parecían dos elegidas, X e Y), y la **ventana de curvas de arriba**
      (`KeyframeGraph.qml`) comparte todo con las filas de la pista: misma selección, mismas figuras, clic derecho con
      el mismo menú y Curvas, mismos atajos (`components/timeline/KeyframeKeyTools.qml`, uno por línea de tiempo en
      `TimelinePanel`). **Supr** borra las claves elegidas antes que el clip (`Main.qml › dispatchAction`).
- [x] Arrastrar varias claves elegidas a la vez en el escritorio, abajo y en la ventana de curvas
      (`KeyframeKeyTools.beginShift/shiftTo/endShift`, `AppController::previewShiftKeyframes`).
- [x] **Tendencias como antes, completas (Jorge, 2026-10-24, tarde):** la sesión anterior las había dejado en «los 24
      más usados»; Jorge: «no quería que modifiques nada ahí, solo la llamita y repartirlas en las subcategorías».
      Ahora cada Tendencias es **todo su tipo, página a página** (web `stockTrends.ts › trendsFor = allOf`, escritorio
      `MarketClient::fetchPanelList` sin categorías), y **todo lo nuestro de Stock lleva la llamita** (Pexels y Pixabay
      no). En los audios de Stock la llamita va junto a la estrella, siempre visible. Web desplegada (rama
      `web/v022-tendencias`, comprobada contra getflipstudio.com con `scripts/check-trends-full.mjs`,
      `check-stock-flames.mjs` y `check-stock-audio-marks.mjs`).
- [ ] Compilación de `flip/v0.22.0` (run 40083533988), probar en ventana (fotogramas clave arriba y abajo, Mi
      cuenta › Descargas, Stock en cada panel, `webHidden`), versión 0.22.0 en `CMakeLists.txt`,
      `release-notes/0.22.0.md`, publicar.
- Ojo: el 2026-10-24 había otra sesión («Tipos de keyframe y stock») tocando `flip/v0.21.1`; no se pudo hablar con
  ella. Antes de publicar, mirar que no haya commits nuevos en `flip/v0.21.1` sin unir.
- Nota de traducción: en la web «Salto» es la misma clave que la animación «Salto» (en inglés sale «Pop»).
