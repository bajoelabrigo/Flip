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

### Arreglos tras la ronda 1 (2026-11-03, rama `flip/subtitulos`)
- **11 (grave):** un tamaño animado crece alrededor del punto de anclaje (`Clip::anchorShift`), y la X/Y guardada se
  refiere al primer tamaño con clave. Si un tamaño empieza a animarse sin ancla, se pone el centro (0,5/0,5); los que ya
  estaban animados (proyectos viejos, plantillas que compensan con X) siguen como antes. La escala de las filas ya no
  escribe claves de Posición para compensar; el recuadro del lienzo dibuja y arrastra igual que el render. Prueba
  `animatedSizeGrowsAroundTheAnchor`.
- **7:** la primera clave puesta a propósito reemplaza la clave de reposo del fotograma 0 (también la del otro eje de
  Posición si van unidos).
- **5:** Posición, en las filas de la línea de tiempo, es donde está el punto de anclaje (esquina guardada + ancla ×
  tamaño de reposo). El inspector de la derecha todavía muestra la esquina.
- **6:** la Escala de una forma dibujada es 100 % con el tamaño con que se dibujó (antes, contra el lienzo); el resumen
  de la fila muestra los dos valores.
- **10:** Tab / Mayús+Tab en un valor de una fila lo confirma y abre el siguiente (anterior); el foco ya no se va a los
  botones de arriba.
- **12:** los tiradores del gráfico toman el clic con su propia zona (más grande que el punto): un arrastre rápido ya
  no lo agarraba el recuadro de selección de debajo.
- **13:** con el gráfico abierto para moldear una curva, solo se agarran las claves de esa curva.
- **1 y 2:** el selector de relleno/trazo dice que el clic derecho lo quita; con una herramienta de dibujo activa, lo que
  se cambia en la forma elegida (color, grosor, sin trazo) vale también para las formas nuevas.
- **3, 4, 8 y 9:** no se reproducen leyendo el código (no hay tecla suelta que pase a Simple; la vista previa en RAM es
  el 0 del teclado numérico, como en AE; la cuadrícula de tercios es la del recorte del lienzo o una guía). Mirarlos
  con calma en la ronda 2 y anotar el paso exacto.

## Ronda 2 (2026-11-03, build dcc85, con el mouse; proyecto y video en `pruebasebote-r2`)
Hecho: fondo, piso y bola con la barra de herramientas; ancla abajo escrita en la fila; Posición Y (5, 13, 19, 24, 31,
37, 43) y las claves 37–43 **copiadas y pegadas** en 49–55; Posición X 962 → 2150 (31 → 55, sale por la derecha); F9 en
las tres cimas; 14 claves de Escala con la cadena suelta, el aplastamiento copiado al segundo golpe; el tirador de la
clave 5 movido en el gráfico de valores y revisado en el de velocidad. Medido: la base se queda en 886 mientras la bola
se aplasta (arreglo 11 bien), cimas en 596 (objetivo 600), X a 50 px por fotograma, fuera de cuadro desde el 52.
Bien en esta ronda: 1, 2, 5, 6, 7, 11, 12 y 13.

Problemas nuevos:
14. El aviso «Arrastra para cambiarlo, clic para escribirlo» de un valor se queda encima y tapa el nombre de la fila.
15. Los avisos dicen «2 fotograma(s) clave pegado(s)» / «copiado(s)»: escribirlo bien según el número.
16. Después de pegar, siguen elegidas las claves copiadas; en AE quedan elegidas las pegadas.
10b. Tab confirma el ancho de Escala pero no abre el alto (lo escrito después se pierde).
17. Punto de anclaje se muestra en píxeles de la caja ya escalada (68/132 pasa a 59/185 con 86 %×140 %); en AE son
    los píxeles de la capa y no cambian con la escala.
18. **Copiar claves de Escala:** al sumar rombos con Ctrl o Mayús solo entra el ancho; se pegó 165×140 en vez de
    165×47. Con Mayús entró una sola clave. El aviso contó «4» para tres rombos de dos valores.
19. «Editar curva…» en una clave de Posición Y abre el gráfico enfocado en Posición X.
20. (menor) La escala de valores del gráfico pone 842 arriba cuando las claves llegan a 890.
21. En el gráfico de velocidad las claves y los tiradores siguen donde están en el de valores; en AE se dibujan sobre la
    curva de velocidad y se arrastran ahí (alto = velocidad, ancho = influencia).
22. (Jorge) En el gráfico de valores, un recuadro sobre las claves de Posición elige también las de Escala, aunque
    casi no se ven. En AE solo se ven y se eligen las de la curva que se edita.

### Arreglos tras la ronda 2
- 18: Ctrl y Mayús sobre un rombo unido (Escala, Posición) toman todas sus claves; el clic simple marca desde dónde
  corre Mayús.
- 15: plurales bien escritos (es, pt-BR, pt-PT, fr-CA, it).
- 16: tras pegar quedan elegidas las claves pegadas (`lastPastedKeyframes`).
- 10b: Tab abre el valor siguiente aunque la fila se rehaga al confirmar (`pendingHotEdit` en la columna).
- 17: el anclaje se mide en el tamaño propio de la capa (el de reposo si el tamaño está animado).
- 19: «Editar curva…» abre la curva de la propiedad de esa clave.
- 20: la escala del gráfico de Posición suma el ancla, como las filas.
- 21: en el gráfico de velocidad las claves y los tiradores van sobre la curva de velocidad; un tirador se arrastra en
  alto (velocidad) y en ancho (influencia), con la escala congelada mientras dura el arrastre; una clave solo se mueve
  en el tiempo.
- 14: el aviso del valor no vuelve hasta que el puntero sale.
- 22: el gráfico muestra y deja elegir (clic o recuadro) solo las claves de la curva enfocada; se cambia de curva con
  el nombre de la fila o los botones de arriba.

## Ronda 3: guion (Jorge, 2026-11-03: «quiero que la línea de tiempo funcione como after effects»)
Desde cero, con el mouse, lo mismo de la ronda 2 pero dejando la bola en el piso los fotogramas que la referencia
(13–15 y 43–45, con «Salto» o dos claves iguales). Además, lo que todavía no se probó:
1. Ver los arreglos 10b, 14–22 (Tab al alto, aviso, plurales, pegadas elegidas, anclaje, «Editar curva…», escala
   del gráfico, gráfico de velocidad con tiradores, recuadro solo de la curva enfocada).
2. Zona de trabajo: barras de inicio y fin (B/N en AE); que la vista previa y la exportación la respeten.
3. Atajos de AE: RePág/AvPág (fotograma), J/K, P/S/R/T/A, U y UU, Alt+[ / Alt+], [ / ], Ctrl+D, Ctrl+Mayús+D.
4. Dos capas a la vez: elegir dos y poner, copiar y pegar claves en las dos.
5. «Velocidad del fotograma clave…»: escribir velocidad e influencia en números.
6. Interpolación espacial y temporal (menú de la clave), claves itinerantes.
7. Valores con cuentas: «+50», «*2».
8. Emparentar a un nulo y una expresión sencilla (wiggle o loopOut) dentro de la animación.

Lo grande que ya se sabe que falta (se hace en una tanda, después de esta ronda):
- **Editor de gráficos como el de AE:** ocupa toda la zona de las barras, muestra las propiedades elegidas de varias
  capas, con «ajustar a la vista», «acercar a lo elegido», elegir el tipo de gráfico, acercar y mover con la rueda y el
  recuadro que escala claves en bloque.
- **Posición unida (X e Y en una propiedad)** con trayecto curvo por defecto (bezier automático espacial), y separar
  dimensiones como opción.
