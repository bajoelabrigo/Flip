# Cómo escribir un módulo de Efectos › Tendencias

Lee primero `glsl.py` (uniforms y ayudantes), `kit.py` (Family, Variant, Param, PHOTOS, PARAM_LABELS),
`fx_ejemplo.py` (el modelo) y tu sección de `CATALOG.md`. Mira las capturas de tus tarjetas (Read sobre
`C:\Users\bajoe\Downloads\efectos filmora N.png` o `efectos 1.png`): el efecto tiene que **parecerse a lo que se ve en
la tarjeta**, pero el shader es nuestro.

## Reglas
- Escribes **solo** `tools/effects_trends/fx_<tema>.py` (te lo dicen). Nada más del repo. Sin commits. **No** corras
  `build.py` (usa la app y el registro: lo corre quien coordina). Prueba con `harness.py --mod fx_<tema>`.
- `FAMILIES = [...]` al final. Una familia = un cuerpo de shader con `main()`; sus variantes cambian `defines` y
  `params` (valores por defecto). Agrupa: si diez tarjetas son «partículas que caen» con otra forma o color, es una
  familia con diez variantes, no diez shaders.
- Una variante por tarjeta del catálogo. `id` = slug del nombre en español, sin tildes (`luz-del-sol-05`), único.
  `es` = el nombre del catálogo (el que va después de «→» si lo hay). `en` = buena traducción. `tags` en es y en.
- **Animado y en bucle sobre `u_time`** (segundos del clip): funciona en un clip de cualquier largo. `u_progress`
  (0..1 del clip) solo para abrir/cerrar; la duración del clip es `u_time / max(u_progress, 1e-4)`. Lo que en
  Filmora sigue el audio («detector de audio», «al ritmo») va a un ritmo fijo de 120 BPM (`beat(u_time, 0.5, …)`).
- Parámetros: siempre `intensity` (Intensity, 0–1.5, 1.0); `speed` (Speed) si se mueve; color con
  `Param("color", "Colour", default="#rrggbb")` (llega como `vec3`) cuando el color es lo que uno querría cambiar.
  Los nombres (`en`) **solo** de `kit.PARAM_LABELS` (la app los traduce). Lo demás, `#define`.
- Movimientos de cámara: `cam()` / `Sm()` (espejo en el borde): **nunca** se ve un borde negro ni la foto repetida
  de forma evidente; usa un poco de zoom (1.05–1.15) para que el espejo no se note. Piezas/tarjetas que se mueven:
  `Sc()` (transparente fuera) sobre un fondo (oscuro, desenfocado o la propia foto) según la tarjeta.
- Superposiciones (partículas, luces, marcos): se dibujan **sobre** la foto con `addLight`/`screen`/`over`, con
  profundidad (2–3 capas de tamaño y velocidad), bordes suaves y brillo creíble. Nada de puntos duros de 1 px ni de
  cuadrícula evidente (las partículas en celdas tienen que verse al azar: desplaza cada una dentro de su celda).
- Tiempo real: un solo pase, `#version 330 core`, bucles cortos (≤ 24 muestras por desenfoque, ≤ 4 capas de
  partículas), nada de `for` con límites que no sean constantes.
- Foto (`photo` de la familia o la variante): el tema de `kit.PHOTOS` que más se parezca a la foto de la tarjeta de
  Filmora (mujer con fondo de color → `woman`, skater → `skater`, auto → `car`, faro → `lighthouse`, bailarina con
  neón → `dancer`/`cyber`, ciudad de noche → `citynight`, superposiciones sobre fondo oscuro → `dark`, cara de cerca →
  `face`, cuerpo entero sobre fondo liso → `figure`). Puedes poner una muestra concreta (`"fx-woman-04"`). Sin marcas.
- `thumb` = segundo del clip (vista previa de 3 s) en el que la tarjeta se ve mejor.

## Revisar (obligatorio)
1. `py tools/effects_trends/harness.py --mod fx_<tema> --sheet <scratchpad>/<tema>.png` → «N ok, 0 failed».
2. Mira **todas** las hojas con Read (cada fila = 5 momentos del efecto). Compara con la captura de Filmora: ¿se
   reconoce el efecto? ¿se mueve entre columnas? ¿se ve profesional y no lava la foto? Corrige y repite hasta que
   todas estén bien. Si una tarjeta es imposible (necesita algo que el motor no tiene), haz la mejor versión posible y
   dilo en el informe.
3. Informe final (corto, en español): cuántas variantes y familias, la lista `id — nombre`, y lo que no quedó igual.
