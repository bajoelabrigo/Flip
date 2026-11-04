# El curso de fotogramas clave de After Effects, punto por punto en Flip (0.30)

Jorge (2026-11-04): «confirmar que todo lo que se hace en el video es posible hacer en nuestra aplicación, los atajos
de teclado, herramientas y trucos… solo cuando puedes confirmar que es así subiremos la 0.30.0».
Video: `Videos\aTubeCatcher\🔷 CURSO de AFTER EFFECTS： Domina los Keyframes y Mejora tus Animaciones.mkv` (1:49:22).
Transcripción (Whisper de la app) en `E:\FlipStudio\pruebas\tutorial-ae\transcripcion.txt`; fotogramas cada 15 s y hojas
en la misma carpeta.

**Juego de atajos:** lo de abajo vale con Preferencias › Atajos › «After Effects». Con el juego «Flip», entre paréntesis.
Estado: ✅ ya estaba · 🆕 hecho para esto (commit `752a6`) · ≈ equivalente (se hace de otra forma) · ⏳ falta verlo en ventana.

| Min | Lo que hace el tutorial | En Flip | Estado |
|---|---|---|---|
| 0:01 | Capa de forma con el cuadrado; Mayús = cuadrado perfecto | Herramienta Forma (Q / Mayús+Q), Mayús proporcional, Alt desde el centro | ✅ |
| 0:01 | Intro sobre la capa para renombrarla | Intro con la capa elegida abre Renombrar | 🆕 ⏳ |
| 0:01 | Capa de texto (T), imagen arrastrada | Herramienta Texto, arrastrar medios | ✅ |
| 0:02 | Transformar: Anclaje, Posición, Escala, Rotación, Opacidad | Filas de la línea de tiempo | ✅ |
| 0:03 | Arrastrar los números azules, escribir 500 | ScrubValue (arrastrar o clic y escribir, con cuentas) | ✅ |
| 0:04 | Escala negativa = voltea | Un valor negativo voltea la capa en ese eje (y se lee negativo) | 🆕 ⏳ |
| 0:04 | Rotación «1x+30°» (vueltas + grados) | Se muestra así; se puede escribir «1x+30» | 🆕 ⏳ |
| 0:05 | Mover el anclaje con su herramienta; Ctrl lo pega al centro | Herramienta Anclaje (Y); Ctrl lo pega al centro, esquinas y medios de lado | 🆕 ⏳ |
| 0:06 | Coordenadas 0,0 arriba a la izquierda, 1920×1080 | Igual | ✅ |
| 0:08 | Cronómetro: primera clave; cambiar = clave nueva | Cronómetro de cada fila | ✅ |
| 0:10 | Mover claves en el tiempo, borrarlas, varias juntas | Arrastrar, Supr, recuadro | ✅ |
| 0:11 | Mitad clara/oscura del rombo según haya clave al lado | El lado sin clave vecina se pinta oscuro | 🆕 ⏳ |
| 0:13 | Animar Escala, Rotación, Opacidad a la vez | Igual | ✅ |
| 0:13 | Efecto Relleno (Fill) y animar su Color | Efecto nuevo «Relleno» (Generar); el color tiene cronómetro | 🆕 ⏳ |
| 0:14 | Clic en el cronómetro borra todas las claves | Igual | ✅ |
| 0:16 | Alt + arrastrar la primera o última clave = estirar/encoger | Igual (y «Estirar claves…») | ✅ |
| 0:16 | Flechas ◀ ▶ del navegador; se apagan al final | Flechas en cada fila; ahora se apagan sin más claves | 🆕 ⏳ |
| 0:16 | J / K | J / K (Mayús+J / Mayús+K) | ✅ |
| 0:17 | U y UU | U y UU | ✅ |
| 0:19 | Puntos del trayecto = fotogramas | Un punto por fotograma en el trayecto de la vista previa | 🆕 ⏳ |
| 0:19 | Ctrl+flecha = un fotograma | Ctrl+Izquierda/Derecha (Izquierda/Derecha) | 🆕 ⏳ |
| 0:21 | Efecto Eco para ver el rastro | «Time Echo / Trail» | ✅ |
| 0:22 | F9 Suave; Asistente de claves | F9, clic derecho › Suave | ✅ |
| 0:24 | Editor de gráficos de velocidad, manipular la curva | Gráfico de velocidad | ✅ |
| 0:26 | Alternar clave de mantener | Ctrl+Alt+H, clic derecho › Mantener | ✅ |
| 0:31 | Mayús+F9 / Ctrl+Mayús+F9 (llegada / salida) | Igual | ✅ |
| 0:39 | Formas del rombo por tipo (lineal, reloj de arena, medias, mantener, círculo) | KeyframeGlyph; «Redondeada» = círculo | ✅ / 🆕 |
| 0:42 | Bajar o subir el tirador de velocidad, influencia | Tiradores del gráfico; ahora muestra velocidad /s e influencia % al arrastrar | 🆕 ⏳ |
| 0:44 | Ctrl+clic sobre una clave = lineal (y lineal → Bezier automático) | Ctrl+clic en filas y gráfico; Mayús suma a la elección | 🆕 ⏳ |
| 0:45 | Gráfico de valor, X rojo e Y verde | Gráfico de valor | ✅ |
| 0:46 | Separar dimensiones (clic derecho) para tener tiradores | Igual | ✅ |
| 0:48 | Mayús al mover la capa = en línea recta | Mayús deja el arrastre en un eje | 🆕 ⏳ |
| 0:50 | Tiradores del trayecto | Igual | ✅ |
| 0:52 | Convertir vértice: clic en un vértice saca o quita tiradores; con todos elegidos, todos | Alt+clic (o la pluma) sobre el rombo del trayecto | 🆕 ⏳ |
| 0:53 | Interpolación de fotogramas clave (temporal, espacial, desplazar) | Diálogo nuevo (Ctrl+Alt+K, clic derecho › Interpolación…) | 🆕 ⏳ |
| 0:58 | Desplazar en el tiempo; luego suavizar la última clave reparte las del medio | Queda activo (✓ en el menú) y sigue el suavizado de los extremos | 🆕 ⏳ |
| 1:03 | Pelota que rebota: Ctrl+C / Ctrl+V de claves | Igual (con el Rebote conservado, `a229f`) | ✅ ⏳ |
| 1:07 | Alt + arrastrar la última = más rápido | Igual | ✅ |
| 1:08 | Ctrl+D duplica la capa | Igual | ✅ |
| 1:08 | Todas las claves de Posición elegidas + arrastrar = mueve todo el trayecto | Igual | 🆕 ⏳ |
| 1:10 | Borrar solo las claves de X | Separar dimensiones y Supr | ✅ |
| 1:11 | Alt sobre un tirador del gráfico = separarlo; con todas elegidas, todas | Igual | 🆕 ⏳ |
| 1:11 | Caja de transformación: botón para mostrarla, estirar | Botón nuevo; lados y esquinas | 🆕 ⏳ |
| 1:12 | Alt + rueda acerca; claves entre fotogramas | Alt+rueda en la línea de tiempo y el gráfico; claves pegadas a fotogramas | 🆕 ⏳ |
| 1:13 | Barra espaciadora + arrastrar para moverse | Botón del medio del ratón (Espacio reproduce) | ≈ |
| 1:13 | Ver el gráfico de otra capa como referencia | Botón «capas» del gráfico (curvas de las otras capas elegidas) | ✅ |
| 1:15 | Caja: tirar hacia arriba = rebotes más altos | Lado de arriba de la caja | ✅ |
| 1:20 | Alt + esquina de la caja = solo esa esquina (rebotes que se apagan) | Igual | 🆕 ⏳ |
| 1:22 | Velocidad del fotograma clave: doble clic sobre la clave en el gráfico | Doble clic (con los atajos de AE) o Ctrl+Mayús+K o clic derecho | 🆕 ⏳ |
| 1:26 | Copiar los números para sincronizar dos capas | Mismo diálogo | ✅ |
| 1:32 | Continuo (unir llegada y salida) | Casilla «Continuo» | ✅ |
| 1:42 | Objeto que entra de fuera: la primera clave no a 0 | Velocidad del fotograma clave | ✅ |
| 1:42 | P, S, T, R | P, S, T, R (Mayús+…) | ✅ |
| 1:43 | L: niveles y onda del audio | L muestra solo Volumen (de la pista de audio enlazada también); onda en el clip | 🆕 ⏳ |
| 1:43 | E: los efectos de la capa | E muestra solo las líneas de efectos | 🆕 ⏳ |
| 1:44 | Invertir claves (Time-Reverse) | Clic derecho › Invertir claves | ✅ |
| 1:45 | Supr borra claves | Igual | ✅ |
| 1:46 | Alt+Izquierda/Derecha mueve la clave un fotograma | Igual (sin claves elegidas sigue moviendo el clip) | 🆕 ⏳ |
| 1:47 | Ctrl+clic: lineal ↔ redondeada (continua) | Igual | 🆕 ⏳ |

## Lo que queda distinto a propósito
- **Espacio + arrastrar:** en Flip Espacio reproduce al apretarlo; moverse es con el botón del medio o la rueda.
- **Ctrl+clic y Mayús+clic** cambian solo con los atajos de After Effects; con los de Flip, Ctrl suma claves y Mayús
  elige un tramo, como hasta ahora.
- **Doble clic en el gráfico** abre la velocidad con los atajos de AE; con los de Flip sigue borrando la clave.
- **Escala negativa** voltea la capa entera en ese eje (Voltear); no se puede animar de positivo a negativo pasando
  por cero.
