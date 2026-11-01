# Editor web: auditoría y 30 proyectos de prueba (Jorge, 2026-11-01)

Pedido de Jorge: «15 proyectos en web modo móvil y 15 en modo web y corriges los errores que encuentres, como lo
hicimos ayer, haces una auditoría al código primero y ordenas lo que no se entienda y sea necesario, ya no agregas
nada nuevo, solo lo que sea necesario para darle facilidad de uso al usuario con las funciones que ya tenemos…
porque lo nuevo lo vamos a dejar en la app de escritorio. Actualiza la guía para que esto se sepa y en la app de
escritorio también lo pones.»

Repo `codigo\flipstudio-app`, rama `web/auditoria` (sale de `web/v0221-texto`, que ya une todas las demás).
Despliegue: `deploy/deploy.sh` (antes, `git log origin/<rama desplegada> ^HEAD` vacío).

## Reglas
- Nada nuevo: solo arreglos y facilidad de uso con lo que ya existe. Lo nuevo va a la app de escritorio.
- Ordenar el código solo donde haga falta para entenderlo o arreglarlo (sin reescrituras grandes).
- Cada arreglo se prueba en el navegador (Chrome del panel, modo celular 375×812 y escritorio).

## Línea base (2026-11-01)
- `npx tsc -b` limpio; `npx vitest run`: 1039 bien, 4 mal (restoreTiles y regionTracker fallan solo con toda la
  batería en marcha y además Vitest corre las copias de `.claude/worktrees`); `oxlint`: avisos de hooks en App.tsx.

## Estado
- [x] Auditoría del código (revisores en paralelo por zona) → lista de fallos y de cosas por ordenar.
- [x] Arreglos de la auditoría.
- [ ] 15 proyectos en modo celular.
- [x] 15 proyectos en navegador de escritorio (2026-11-01, ver abajo).
- [ ] Guía (`getflipstudio.com/guia.html`): el editor en línea no recibe novedades; lo nuevo, en la app.
- [ ] App de escritorio: el mismo aviso donde aparece «Editar en línea».
- [ ] Desplegar el editor web y la web.

## Auditoría (2026-11-01, cuatro revisores; ~54 hallazgos)
Núcleo (A): 1 archivos creados por la app sin sus bytes (voz, IA, mejorar, ruido) → `keep: true` [x]; 2 «Guardar copia
.flip» usaba `exporting` y abría/cerraba la exportación [x]; 3 medios con error borrados al guardar [x]; 4 dos archivos
con el mismo nombre se funden en el .flip; 5 autoguardado que no llega con progreso continuo, sin guardar al salir [x];
6 «Faltan archivos» falso con Stock descargándose [x]; 7 marcadores, rango, autor y descripción se pierden en el .flip;
8 error de lectura tratado como proyecto vacío y sobrescrito; 9 proyecto borrado que vuelve vacío [x]; 10 descarga .flip
en Safari y nombre sin acentos [x]; 11 carrera en el índice de proyectos; 12 repetir tramo pasado el final [x];
13 fallo de guardado invisible; 14 abrir .flip sin progreso y errores en inglés; deshacer vacío en composiciones.
Línea de tiempo (B): imán que salta 8 px al recortar/mover; cortar no corre claves de volumen, máscara y plantillas;
mitades enlazadas pegadas; Q/W sin rebasar claves; Combinar pierde claves; transiciones al corte equivocado con audio;
selección múltiple que pisa clips; Supr borra claves de otro clip; pegar/duplicar crea pistas vacías y enlaza; soltar
fuera de las pistas deja vecinos empujados; pistas con candado editables; clips cortos imposibles de mover; borrar
varios ignora el modo ondulado.
Celular (C): recortar junto a un corte abre Transiciones; horizontal inutilizable; muesca tapa botones; atrás de Android
no cierra nada; tocar el mismo corte no abre; «+ Agregar audio» muerto con clip elegido; fila de panel que sigue en otro
clip; previas de Stock imposibles con el dedo; menú ⋯ no se cierra fuera; asa de la hoja pequeña; recorte con proporción
fija; deslizadores que dejan pasos vacíos; deshacer con dos dedos sin historia; etiquetas confusas.
Paneles y exportar (D): **no se puede exportar con una forma o un sticker Lottie**; stickers rápidos que se pierden;
colores de texto rompen deshacer; cuadros negros en huecos de menos de un cuadro; exportar sin sonido sin aviso; fuentes
de escritorio sin cargar al exportar; controles que cambian de inspector sin avisar; Lottie .json invisible; error de
importación sin motivo; GIF que corre rápido; enlace de escala que pasa al otro clip; flechas que llenan el deshacer.

## 15 proyectos en el navegador de escritorio (2026-11-01, Chrome 1440×900 y 1920)
1 fotos + música + «+» en secuencia; 2 transición + título + GIF (600 cuadros × 0,10 s = 60 s); 3 forma + sticker
animado → MP4; 4 cortar + 2× + LUT + título + música recortada con W → MP4 con sonido; 5 MP4 fragmentado de 120 fps
a 0,5× con máscara de corazón → 60 fps; 6 superposición en otra pista, escala 40 %, claves de posición, fusión Trama;
7 separar audio, volumen −6 dB, fundidos 2/3 s → WAV; 8 deshacer/rehacer ×4, Inicio y reabrir; 9 plantilla de
efectos «Caída del ritmo» → MP4; 10 transiciones Reloj/Fundido/Barrido + efecto «Líneas de TV»; 11 composición
(agrupar, entrar, 2×, salir); 12 textos con burbuja y neón; 13 ProRes .mov + video sin sonido; 14 congelar, espejo,
girar 90°; 15 duplicar, marcador, «Guardar copia para compartir» (.flip de 12 MB).

Arreglado en `web/auditoria` por estas pruebas:
- **Stickers animados**: no se veían ni en la vista previa ni al exportar, y exportar con uno se colgaba sin poder
  cancelar (`render/lottie.ts`: `DOMLoaded` ya había pasado; con `container` lottie dibujaba en un lienzo 0×0). Los
  4 Lottie de la web estaban mal hechos: cambiados por los nuestros (`Flip/tools/animations`). Tarjetas con un cuadro
  del medio. Al terminar con «mantener» quedaba vacío: se queda en el último cuadro.
- **Miniaturas** de clips con pocos cuadros clave (stock: uno cada 10 s) repetían una imagen: se sacan del reproductor.
- **MP4 fragmentado** (cámaras, grabadoras) entraba con 0:00: duración del reproductor y fps de las muestras.
- **Regla**: ya no quita la selección del clip (poner claves: mover cabezal → cambiar valor); sí suelta un corte
  elegido, para que la transición vaya al corte del cabezal.
- **Aviso al añadir** un medio: dice dónde quedó de verdad.
- **Video que el navegador no puede mostrar** (ProRes): aviso con qué hacer (15 idiomas).

Visto y dejado como está (decisiones de Jorge o normal): Tendencias, Stock y animaciones de texto piden sesión;
el proyecto toma los fps del primer clip (119,88 con un clip de 120 fps); los archivos subidos con el `<input>` en
Chrome no se reabren (la app usa el selector del sistema); cambiar la velocidad con «Cerrar huecos» apagado deja hueco.
