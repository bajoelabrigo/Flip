# Ejercicio: bola que cae y rebota, como en After Effects (Jorge, 2026-11-03)

Pedido de Jorge: hacer la animación como un usuario de After Effects, **solo con las herramientas de la línea de
tiempo** (filas de fotogramas clave, curvas, gráfico de velocidad), **sin la barra de la derecha**, y **con el mouse
de verdad**. Cada error o herramienta que falte se anota aquí; se corrige todo al final, se compila una vez y se repite
el ejercicio desde cero hasta que salga 100 % bien.

## La referencia (`Downloads\proyecto base.mp4`, copia de los fotogramas en `pruebas\rebote-ref`)
Medida fotograma a fotograma (bbox de los píxeles de la bola):

- 1920×1080, 30 fps, 69 fotogramas (2,3 s). Sin sonido.
- Fondo: degradado vertical de #ffffff (arriba) a ~#7cc9fe (abajo). Piso: franja #392de3 de y = 893 a 928, todo el ancho.
- Bola: #ff4b6c, círculo de ~133 px, centro x = 958. En reposo: centro y = 824 (abajo en 890, sobre el piso).
- Tiempos (fotograma → centro y, ancho × alto):
  - 0–6: fuera de cuadro, arriba.
  - 7: entra (centro ≈ −44). 8: ≈ 70. 9: 187 (118×168). 10: 318 (118×174). 11: 461 (116×180). 12: 620 (114×186).
    Cae acelerando y **se estira** en vertical.
  - 13: 842 (174×98), 14: 860 (220×62), 15: 859 (218×64): **toca y se aplasta**; la base queda en y = 890.
  - 16: 813 (178×96), 17: 769 (130×136), 18: 738 (120×170), 19: 726 (114×186) — sube estirada; **pico** en 19–20
    (≈ 100 px sobre el reposo).
  - 21: 737, 22: 757 (124×160), 23: 785 (128×148): vuelve a caer.
  - 24: 826 (138×130), 25: 830 (146×122), 26: 831 (146×120): **segundo golpe**, aplastamiento chico.
  - 27–30: se asienta (142×124 → 130×138, un pequeño rebote de forma). 31 en adelante: reposo, 132×134.

## Cómo lo haría un usuario de After Effects
- Capas: fondo (degradado), piso (rectángulo), bola (círculo de Formas) con el **ancla abajo** (para que se aplaste
  sobre el piso).
- Posición Y: claves en ~5 (arriba, fuera), 13 (piso), 19/20 (pico), 24 (piso), 31 (reposo). Facilidades: caída con
  *ease in* (acelera), salida del piso con *ease out*, el pico con *easy ease*; en el gráfico de velocidad, el típico
  dibujo de rebote (velocidad máxima en el golpe).
- Escala (separar ancho y alto): estirar en la caída (~87 % × 137 %), aplastar al tocar (~165 % × 47 %), estirar al
  subir (~86 % × 140 %), aplastar poco en el 2.º golpe (~110 % × 90 %), asentarse (~98 % × 104 %) y reposo 100 %.

## Lista de problemas (se llena durante el ejercicio)
_(vacía todavía)_
