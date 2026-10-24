# Efectos › Tendencias (0.21.0) — plan y estado

Pedido de Jorge (2026-10-23): crear todos los efectos de 16 capturas (`Downloads\efectos 1.png` = CapCut,
`Downloads\efectos filmora 1..15.png` = Filmora), con fotos que coincidan, animados, en **Efectos › Tendencias** y en
**Stock**; que **todas las Tendencias** (texto, efectos, transiciones…) pidan la cuenta, en la app y en la web; y que
**todos los efectos sean editables** («si les falta alguna función la creas»).

## Cómo está hecho
- **Herramientas:** `tools/effects_trends/` (léase `BRIEF.md` y `CATALOG.md`).
  - `kit.py` (Family/Variant/Param, fotos), `glsl.py` (uniforms y ayudantes), `fx_*.py` (un módulo por tema, ~370
    efectos), `voices.py` (9 voces = preajustes de audio), `harness.py` (render sin la app con moderngl; añade el
    preludio de profundidad del motor; `unused_params` encuentra los controles que no cambian nada), `build.py`
    (paquetes + tarjeta y video de 3 s renderizados **por la app** portable 0.20.1 con `DRIFT_EFFECTS_DIR`),
    `publish.py` (→ `tienda\plantillas\publicar\efectos\index.json`).
  - Cada efecto es un paquete GPU propio (`effect.json` + `main.frag`, shader nuestro, no de Drift) en un `.driftfx`
    de tipo `effects`; id `stockfx_<slug>`, `category: "trending"`, `names` por idioma.
  - Los controles que no hacen nada en una variante van a `fixedParams` (llegan al shader, no salen en el panel).
- **App:** `EffectBrowser.qml` (chip «Tendencias» primero; tarjetas 16:9 con video al pasar el mouse; clic = baja y
  aplica), `MarketClient::fetchEffectTrends` (tipo `effect`), entrega `effect` en `installStockFile` y en las listas
  de Stock, nombres por idioma en `EffectPackageLoader`/`TransitionPackageLoader`, Tendencias de animación con
  sesión (`AnimationInspector.qml`, `TextInspector.qml`).
- **Servidor:** `flipstudio-api` rama `stock-efectos` (tipo `effect`, carpeta `efectos`, 15 idiomas). **Sin desplegar.**
- **Web:** `flipstudio-app` rama `web/tendencias-login` (las Tendencias de animación piden sesión). **Sin desplegar.**
  Los efectos de Tendencias en el editor web quedan para después (la web tendría que correr los `.driftfx` de efecto
  en WebGL2, como ya hace con las transiciones).

## Estado (2026-10-23, noche)
- [x] Herramientas y piloto probado con la app (carga, `u_time`, tarjeta, video).
- [x] 16 módulos (364 efectos en 121 familias) + 9 voces; todos con controles editables (los que no hacen nada en
      una variante van a `fixedParams`); familias con profundidad para lo que va detrás de la persona.
- [x] **Motor:** los efectos reciben el avance del clip en `u_progress` (antes siempre 0: aperturas y cierres).
- [x] Tarjetas y videos renderizados por la app 0.21 (CI run 40035973172), revisados en `tienda\efectos\catalogo-*.png`.
- [x] Nombres en 13 idiomas (`tools/stock_i18n`, claves `effect:<id>`) dentro de cada paquete y en `publicar\i18n`.
- [x] `publicar\efectos` armado (373 elementos, 30 MB).
- [x] **Probado en ventana** (portable 0.21 contra `flipstudio-api` local con `DRIFT_MARKET_API_URL`): Efectos ›
      Tendencias carga página a página, un clic baja e instala «Nieve realista» y la aplica; su panel en español
      (Intensidad, Velocidad, Densidad, Tamaño, Color, Ángulo) cambia la vista previa y crea fotogramas clave;
      «Ardilla listada» se aplica como efecto de voz al clip.
- [x] Web: Texto › Animación › Tendencias sin sesión muestra el aviso (rama `web/tendencias-login`, local).
- [x] Arreglos encontrados en la prueba: la ventana de Descargas decía «en la biblioteca de medios» para todo lo que
      se instala (ahora dice dónde quedó); el servidor mandaba `effect` también para las voces (ahora cada elemento
      puede llevar su `delivery`).
- [ ] App sin sesión en ventana (Efectos › Tendencias y Tendencias de animación): probar quitando la clave
      `account` del registro con copia, **sin** cerrar sesión (cerrar sesión revoca la familia de tokens).
- [ ] Desplegar: servidor `stock-efectos` → `publicar\efectos` + `publicar\i18n` → web `web/tendencias-login`
      (unir antes con lo último desplegado) → PR, tag `v0.21.0`, MSIX, novedades en la web.

## Trampas
- Un efecto con `requires: "depth"` o `"face"` no va en una capa de ajuste: hace falta un clip seleccionado.
- El motor quita `#version`, pone su preludio y vuelve a poner `#version`: las familias de profundidad **no** declaran
  `driftDepth`/`u_hasDepth`. El arnés hace lo mismo (`engine_source`).
- Las tarjetas se renderizan sin escanear caras ni calcular profundidad: los efectos de IA se ven con su versión
  sin análisis (por eso usan fotos de fondo liso).
