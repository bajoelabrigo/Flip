# Stock en 13 idiomas

El servidor (`flipstudio-api/src/services/i18n.ts`) elige el idioma por `Accept-Language` y lee los
nombres, etiquetas y categorías de `tienda\plantillas\publicar\i18n\<idioma>.json`. Español e inglés
ya están en los `index.json`; aquí viven los otros 13: `ar bn fr it ja ko pl pt ru si tl vi zh`.

| Archivo | Qué es |
|---|---|
| `<idioma>.json` | Las traducciones (fuente, en el repo): `{"items": {"<tipo>:<id>": {"name", "tags"}}, "categories": {"<tipo>:<categoría>": "..."}}`, **sin** las variantes `-h` |
| `common.py` | Carpetas por tipo, idiomas y sufijos de variante («(horizontal)» en cada idioma) |
| `collect.py` | Lee todos los índices y escribe lo que falta por idioma en tandas: `work/todo/<idioma>-NN.json` |
| `merge.py` | Pasa las tandas traducidas (`work/done/<idioma>-NN.json`) a `<idioma>.json` |
| `build.py` | Deriva las `-h`, valida y escribe `publicar\i18n\<idioma>.json`; informa cuántos faltan |

`work/` no se commitea. La carpeta `publicar` se puede cambiar con `FLIP_STOCK_PUBLICAR`.

Tipos y carpetas: `template` (raíz), `animation` (`animaciones`), `overlay` (`superposiciones`),
`background` (`fondos`), `sound` (`sonidos`), `music` (`musica`, si existe).

**Variantes:** un id que termina en `-h` y cuyo id base existe es la versión horizontal: su nombre es
el nombre traducido del base + « (horizontal)» en ese idioma y sus etiquetas son las del base. No se
traduce a mano. Si el nombre base ya termina en paréntesis, el sufijo entra dentro: «Aquarelle
(chaud, horizontal)», «水彩（暖色・横）». Para otro sufijo (p. ej. cuadradas), añadirlo a `VARIANTS` en `common.py`.

## Segunda pasada (cuando Stock tenga elementos nuevos)

1. Publicar primero los índices nuevos en `publicar\` (plantillas, música, lo que sea).
2. `py tools/stock_i18n/build.py --check` — dice por idioma cuántos elementos y categorías faltan.
3. `py tools/stock_i18n/collect.py` — crea `work/todo/<idioma>-NN.json` solo con lo que falta
   (`--lang fr` para uno, `--size 100` para tandas más chicas).
4. Traducir cada tanda a `work/done/<idioma>-NN.json`, con la misma forma que el archivo final:
   nombre corto y natural de tienda, 3–6 etiquetas de búsqueda en minúsculas, categorías nuevas en
   la tanda 01. Lo traduce Claude (un agente por idioma en paralelo funciona bien), sin servicios externos.
5. `py tools/stock_i18n/merge.py` — las pasa a `<idioma>.json` (y mueve las tandas a `work/merged/`).
6. `py tools/stock_i18n/check.py` — revisión rápida: nombres iguales al inglés (normal en préstamos
   como Halloween o Bokeh, raro si son muchos: el tagalo salió con 458 en la primera pasada y se
   rehízo), duplicados, etiquetas fuera de 3–6, nombres sin el alfabeto del idioma. Las palabras
   «youtube»/«tiktok» en etiquetas vienen de las etiquetas originales y están bien; en nombres, no.
   Para corregir algo ya fusionado, dejar un `work/done/<idioma>-fix-NN.json` con solo esas claves y
   volver a correr `merge.py`.
7. `py tools/stock_i18n/build.py --strict` — escribe `publicar\i18n\` y falla si queda algo sin traducir.
8. Commit de los `<idioma>.json` y subir `publicar\i18n\` al servidor con los paquetes (no hace falta
   desplegar el servidor: relee el archivo cuando cambia).

Lo que falta en un idioma no rompe nada: el servidor usa el inglés para ese elemento.
