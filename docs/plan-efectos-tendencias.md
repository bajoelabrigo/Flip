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

## Estado
- [x] Herramientas y piloto probado con la app (carga, `u_time`, tarjeta, video).
- [x] 15 módulos escritos por agentes y revisados en hojas; segunda pasada «todo editable».
- [x] Cambios de la app, servidor y web (ver arriba); traducciones de la app en 15 idiomas.
- [ ] `build.py` completo con la app (tarjetas + videos de los ~370) y revisar `catalogo-*.png`.
- [ ] Nombres en 13 idiomas (`tools/stock_i18n`, claves `flip:effect:<id>`), y volver a correr `build.py --no-render`
      para meterlos en los `names` de cada paquete.
- [ ] Compilar (CI `build.yml`), probar **en ventana**: Efectos › Tendencias con y sin sesión, aplicar uno, editar sus
      controles, uno de profundidad, uno de cara, una voz; Tendencias de animación sin sesión.
- [ ] Desplegar: servidor `stock-efectos` → paquetes `publicar/efectos` → web; luego PR, tag `v0.21.0`, MSIX.

## Trampas
- Un efecto con `requires: "depth"` o `"face"` no va en una capa de ajuste: hace falta un clip seleccionado.
- El motor quita `#version`, pone su preludio y vuelve a poner `#version`: las familias de profundidad **no** declaran
  `driftDepth`/`u_hasDepth`. El arnés hace lo mismo (`engine_source`).
- Las tarjetas se renderizan sin escanear caras ni calcular profundidad: los efectos de IA se ven con su versión
  sin análisis (por eso usan fotos de fondo liso).
