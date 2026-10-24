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
- **Escritorio**: después de la web.

## 4. Lo que ya estaba pendiente
- 0.21.1: medios ocultos de la web también ocultos en Medios (`webHidden`), probar en ventana con un `.flip` de la web
  que tenga un recorte de persona.
- Cuando la Store apruebe la 0.21.0: TXT `version` = 0.21.0 (Jorge).

## Estado
- [x] Fotogramas clave: web
- [x] Fotogramas clave: escritorio (código) — [ ] en ventana
- [x] Mi cuenta: web — [ ] escritorio
- [ ] Stock por panel: web — [ ] escritorio
- [ ] Traducir los textos nuevos de la web (16 idiomas) al unir las ramas
- [ ] Unir las ramas web, desplegar
- [ ] Una compilación del escritorio con todo, prueba en ventana, versión, publicar
