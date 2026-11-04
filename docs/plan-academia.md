# Academia Flip Studio (pedido de Jorge, 2026-11-04) — PENDIENTE

**Empezar solo después de cerrar los cursos de nulos y formas** (`docs/tutorial-nulos-formas-ae.md`), probados en
ventana. Sin publicar nada de la app hasta que Jorge lo diga.

## Qué pidió
- Ampliar **Guía** de getflipstudio.com (`codigo\flipstudio-web`, sitio estático: `guia.html`, `styles.css`,
  `main.js`; capturas con `flipstudio-web/tools/guia`) en una **Academia**: «ACADEMIA FLIP STUDIO — Aprende a
  editar como un profesional».
- Tres cursos: **Básico, Intermedio, Avanzado**. En los tres, seis temas que crecen de nivel: Keyframes, Formas,
  Nulos, Subtítulos, Texto a voz, Texto y animaciones de texto.
- Cada lección con la misma estructura: título, introducción, objetivo, explicación, paso a paso, **capturas
  reales** de Flip, controles y parámetros, ejemplo práctico, consejos y errores frecuentes, resultado esperado,
  ejercicio.
- Capturas **reales** de la app (nunca IA ni recreaciones). Lista de capturas por lección antes de capturar;
  recortadas y optimizadas; organizadas por nivel/tema/lección. Si algo no se puede capturar, anotarlo, no inventar.
  **Originales guardadas fuera del proyecto web** (p. ej. `E:\FlipStudio\academia\capturas`) para rehacerlas cuando
  cambie la app.
- Portada de la Academia con tres tarjetas (ícono, cantidad de lecciones, qué se aprende, botón Comenzar). Página del
  curso: descripción, índice, módulos y lecciones, imágenes, progreso. Lección: imágenes grandes con ampliación,
  anterior/siguiente, volver al índice y a la Academia.
- Responsive (PC, portátil, tableta, celular), carga optimizada, recordar la última lección (localStorage), gratis,
  sin registro ni pagos.
- Misma tecnología y estilos del sitio; sin segunda aplicación ni dependencias nuevas; contenido en **datos aparte**
  (cursos, niveles, módulos, lecciones, imágenes, ejercicios, recursos) para sumar cursos sin rehacer la sección.
- Verificar: tres niveles, seis temas, enlaces, imágenes, móvil y escritorio, consola sin errores, rutas actuales y la
  Guía original siguen funcionando, pruebas del proyecto. Nada de lecciones ficticias ni marcadas como hechas sin
  contenido y capturas.
- Entrega: resumen, cursos y lecciones, cuántas capturas reales, pendientes, cómo agregar cursos, resultados de pruebas.

## Estado
**2026-11-04 (noche): las 18 lecciones escritas, en `flipstudio-web` rama `academia` (SIN desplegar).**

- Código: `flipstudio-web/tools/academia/`. `build.py` arma `academia/` desde `cursos.json` (niveles y temas) y
  `lecciones/<nivel>/<tema>.json` (las 11 partes). Una lección se publica solo con `estado: "completa"`, todas sus
  partes y todas sus imágenes; si no, sale «En preparación». `academia/academia.js` guarda en `localStorage`
  (`flip-academia`) las hechas y la última; `styles.css` lleva los estilos `.acad-*`.
- Capturas: originales en `E:\FlipStudio\academia\capturas\<nivel>\<tema>\NN.png` (ventana entera, por mensajes);
  `tools/academia/capturas.json` dice el recorte y los números de cada una y `anot.py` hace el `.webp` en
  `assets/academia/`. Rehacer una: capturar encima de la original y `py tools/academia/anot.py <nivel>/<tema>/NN`.
  Ojo: el panel General de un clip de audio muestra la ruta con el usuario de Windows; recortarlo siempre.
- Agregar un curso o una lección: el nivel o tema en `cursos.json`, su JSON en `lecciones/`, las capturas y su
  entrada en `capturas.json`, después `anot.py` y `build.py`, y la página en `sitemap.xml`.
- Enlaces: nota en `guia.html` y las páginas en `sitemap.xml`. Probado en el navegador: 0 enlaces rotos, 51+
  imágenes cargan, escritorio y celular, consola limpia.
- Errores de la app encontrados al capturar y arreglados en `flip/subtitulos` (`release-notes/0.30.0.md` › Arreglos):
  Opacidad en % en expresiones, Escala por expresión desde el centro también en el dibujo, Dividir en letras movía
  las letras, Formas desde texto quedaba en la pista de texto, «Renombrar…» frente a «Cambiar nombre…».
