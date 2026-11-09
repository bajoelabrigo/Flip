# Motor: lo que falta (pedido de Jorge, 2026-11-08)

Cada sección: qué hace la referencia, en qué segundos, y qué necesitaría el motor.

## yp0 (38664567) — contador de seguidores lineal — HECHO en el motor (sin compilar)
La barra de seguidores cuenta a ritmo fijo (~1500/s, 120240 → 129704); el contador del motor frenaba al final.
Nuevo `TextStyle::counterCurve` = "easeOut" (por defecto) | "linear" (`counterTextAt(..., linear)`), guardado en el
proyecto y en `AppController` (textStyle map). Prueba en `tst_core` (`counterTextCountsInTheTextsFormat`). Falta: control
en el panel de Texto (si Jorge lo quiere) y compilar; la plantilla `yp0-barra-seguidores` puede pasar `counterCurve:
"linear"` cuando el portable lo tenga.
