# Motor: lo que falta (pedido de Jorge, 2026-11-08)

Cada sección: qué hace la referencia, en qué segundos, y qué necesitaría el motor.

## yp0 (38664567) — contador de seguidores lineal — HECHO en el motor (sin compilar)
La barra de seguidores cuenta a ritmo fijo (~1500/s, 120240 → 129704); el contador del motor frenaba al final.
Nuevo `TextStyle::counterCurve` = "easeOut" (por defecto) | "linear" (`counterTextAt(..., linear)`), guardado en el
proyecto y en `AppController` (textStyle map). Prueba en `tst_core` (`counterTextCountsInTheTextsFormat`). Falta: control
en el panel de Texto (si Jorge lo quiere) y compilar; la plantilla `yp0-barra-seguidores` puede pasar `counterCurve:
"linear"` cuando el portable lo tenga.

## yp4 (pack youtube 4, historias)
1. **Texto sobre un círculo que gira** (yp4-mi-plan, 9,9–12,4 s): hoy, un clip por palabra girado; falta texto sobre
   un trazado (círculo) con ángulo animable.
2. **Capas entre el fondo y la persona de la foto del usuario** (yp4-mi-plan, yp4-siguiente): falta que un hueco de foto
   pueda pedir «Quitar fondo» al rellenarse, para poner capas detrás de la persona.
3. **Intersección de dos formas en otro color** (yp4-bienvenida, 5,2–5,8 s): falta intersección entre capas o modo
   «diferencia»; hoy, una lente aproximada.
