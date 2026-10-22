# Animaciones como Filmora (pedido de Jorge, 2026-10-22)

Jorge mandó las capturas de Filmora (en `Downloads`): **Títulos › Animación › Entrada**
(`animacion - Entrada 1.png` y `animacion - Entrada 2.png`, unas 200), **Salida**
(`Animacion - Salida.png`, unas 85) y **Video › Animación › Combinado** (`animacion - Combinado.png`,
unas 60). Quiere esas animaciones en Flip. Versiones propias, no copias (ver memoria «Stock: trends»).

Rama: **`flip/animaciones`** (sale de `main` con la 0.19.0). El editor web va detrás, en
`flipstudio-app` (rama `web/animaciones`), igual al escritorio.

## Lo que ya había

- Texto: motor de animadores tipo After Effects (`core/TextAnimator.*`, presets JSON en
  `presets/text-animations/`, 47 incluidos) y 200 en Stock › Textos animados
  (`tools/text_stock/anims_*.py`). El panel Texto › Animación tiene Entrada/Salida/Bucle con chips y
  tarjetas que se reproducen al pasar el mouse (`TextAnimPresetTile`).
- Clips: `core/ClipAnimation.*`, un `enum` de 11 tipos (deslizar, zoom, girar, rebote), solo Entrada y
  Salida, elegidos en una lista (`AnimationInspector.qml`).

## Qué se hace

### 1. Motor de texto (escritorio)
- **Giro 3D por letra**: `rotationX` / `rotationY` en los animadores (puerta, voltear, rodar en 3D).
- **Emoji o símbolo que acompaña al texto** (cursor de glifo): «ABC⚡», «ABC💎», «ABC★»… El cursor de
  la máquina de escribir puede ser un glifo, con tamaño, giro y rebote.
- **Partículas**: chispas, estrellas, polvo, humo, confeti, anillos y glifos que salen de cada letra
  al aparecer o al irse (explosión, polvo de hadas, humo, chispas, fuegos artificiales…).
- Todo en el preset (`"particles"`, `"caret"` con `"shape": "glyph"`), así que Stock puede traer más.

### 2. Animaciones de texto nuevas (incluidas en la app)
- Chips de Entrada como Filmora: **Tendencias, Movimiento y trayectoria, Máscara y revelado, Fluido,
  Construcción, Estilizado, Partículas**. Salida: **Tendencias, Ocultar y enmascarar, Escalonado,
  Estilizado, Partículas**. Las 47 de antes se reparten en estos chips.
- Meta: ≥ 200 en Entrada y ≥ 85 en Salida (además de las de antes).

### 3. Animaciones de clip con presets (Video › Animación)
- `ClipAnimation` gana `preset` (JSON en `presets/clip-animations/`): curvas de posición, escala,
  giro, giro 3D, opacidad y desenfoque, más efectos del catálogo con parámetros animados
  (desenfoque de zoom, separación RGB, giro, etc.).
- Tercera pestaña **Combinado** (entra y sale en una sola animación, dura todo el clip o lo que se elija).
- Panel con tarjetas y vista previa animada al pasar el mouse, como Filmora.
- Meta: ≥ 60 Combinado, y más Entrada/Salida de clip.

### 4. Editor web
- Mismo formato de presets (se copian del repo de escritorio) y el mismo panel.

### 5. Publicar
- Compilar una vez (`build.yml`), probar en ventana, 0.20.0.

## Estado

- [x] Barra de abajo del celular pegada al final (web, `flipstudio-app` `web/movil`, desplegado
  2026-10-22): `.ph` y `.app.is-touch` usan `position: fixed; inset: 0` en vez de `100dvh`, que en
  el iPhone instalado como app medía menos que la pantalla.
- [ ] 1. Motor de texto
- [ ] 2. Animaciones de texto
- [ ] 3. Animaciones de clip
- [ ] 4. Web
- [ ] 5. Publicar
