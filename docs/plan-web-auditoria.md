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
