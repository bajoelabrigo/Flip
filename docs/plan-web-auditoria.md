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
- [ ] Auditoría del código (revisores en paralelo por zona) → lista de fallos y de cosas por ordenar.
- [ ] Arreglos de la auditoría.
- [ ] 15 proyectos en modo celular.
- [ ] 15 proyectos en navegador de escritorio.
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
