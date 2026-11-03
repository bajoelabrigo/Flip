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

## Acordado con Jorge (2026-11-03)
Fondo, piso y bola se crean con el **panel izquierdo** (Formas, Títulos…) y colores aproximados; la animación, solo
con la línea de tiempo y el mouse.

## Ronda 2 en adelante: la bola da dos saltos más y sale de la escena (Jorge, 2026-11-03)
Después del rebote de la referencia, la bola da **dos saltos hacia un lado y sale del cuadro**, para probar lo que un
usuario de AE hace al repetir movimiento: **copiar y pegar fotogramas clave** (los del salto y los del aplastamiento),
moverlos en bloque, animar Posición X a la vez que Y (trayecto en arco), ajustar las curvas de cada salto y seguir el
gráfico de velocidad a lo largo de varios golpes. Jorge avisa que hay más problemas por encontrar ahí.

## Lista de problemas (se llena durante el ejercicio)
Ronda 1 (2026-11-03, build 71005, con el mouse):
1. El trazo de las formas sale blanco de 20 px y el selector de color del trazo no tiene «sin trazo» (en AE sí); hay
   que saber que el grosor 0 lo quita.
2. El grosor 0 de la barra de la herramienta no se aplica a las formas nuevas (el piso y el fondo salieron con borde
   blanco), y escribir 0 otra vez con la forma elegida no hace nada porque el valor no cambió: hubo que poner 5 y 0.
3. Al empezar un arrastre del Rectángulo justo fuera del lienzo (x = 384, el lienzo empieza en 390) no se dibujó nada y
   apareció una cuadrícula de tercios que no se va; Ver › Guías no sale marcado.
4. Con la herramienta Selección no se ven las opciones de Relleno/Trazo; un clic en ese lugar cae en la regla y las
   teclas («5», «0», Intro) van a atajos: uno pasó a modo Simple y otro arrancó la vista previa en RAM. Averiguar qué
   tecla cambia de modo (no debería ser una cifra suelta).
5. «Posición» es la esquina de arriba a la izquierda de la caja, no el punto de anclaje: con el ancla al centro, la bola
   en x = 958 dice Posición X 893. En AE la posición es donde está el ancla.
6. La «Escala» de una forma dibujada sale 6,8 % × 12,2 % (su tamaño contra el lienzo) en vez de 100 %: aplastar al
   165 % × 47 % obliga a hacer cuentas. (Ancho/Alto en píxeles sí se entienden.)
7. El cronómetro de Posición Y, con el cabezal en el fotograma 6, puso también una clave en el fotograma 0 (con el valor
   viejo): la bola saltaba hacia arriba antes de caer. En AE la clave va solo donde está el cabezal.
8. Con el editor de curvas abierto bajo la pista, el gráfico tapa las filas de las demás propiedades.
9. Una tecla de las que se usan para confirmar valores (Intro fuera de un campo, o una cifra) arranca «Calculando la
   vista previa en memoria». Revisar qué atajos tienen Intro y las cifras sueltas.
10. Tab no confirma un valor de una fila (el foco se va al botón Inicio y el valor se pierde); en AE Tab confirma y pasa
    al campo siguiente.
11. **Grave:** Ancho, Alto y Escala crecen desde la esquina de arriba a la izquierda e **ignoran el punto de anclaje**:
    con el ancla abajo, la bola aplastada (220×62) flotaba ~90 px sobre el piso (base en y = 798 en vez de 890) y el
    borde izquierdo quedaba siempre en x = 894. En AE la escala es alrededor del ancla.
12. En el gráfico de velocidad, un arrastre rápido de un tirador no hace nada; hay que apretar y moverse despacio.
13. Sobre el gráfico de Posición Y se dibujan las claves de las otras propiedades (rombos morados y verdes de Ancho/Alto)
    y se agarran por error al querer tomar un tirador; Ctrl+Z no dejó claro qué deshizo.

Resultado medido de la ronda 1 (exportado a `pruebasebote-r1`, comparado con `pruebasebote-ref\medir.py`): la
caída y el reposo quedan a pocos píxeles; el aplastamiento sale mal por el problema 11 (base hasta 92 px arriba) y la
bola entra un fotograma tarde (falta afinar la influencia de la primera clave en el gráfico de velocidad).
