# Plan 0.26 — Motion graphics como After Effects (todo en una versión)

Pedido de Jorge (2026-10-28): tras la comparación con After Effects, hacer **las cuatro etapas en una sola
versión** («si lo hacemos en partes se me acaba la suscripción»). Misma metodología de siempre: cada cambio
probado al hacerlo, el trabajo a medias subido a la rama, una compilación de CI al final y **todo probado en
ventana** antes de publicar.
Rama: `flip/v0.26.0`.

Si otro asistente sigue este trabajo: este archivo dice qué está hecho (`[x]`), a medias (`[~]`) y qué falta
(`[ ]`), y dónde vive cada cosa.

## Etapa A — Emparentar capas, Nulo y desenfoque de movimiento
- [ ] A1. **Emparentar** (columna «Primario» / látigo de AE): `Clip::parentId` + pose de reposo del padre al
      enlazar (`Clip::parentRest`). La capa hija sigue el movimiento, giro y escala del padre **desde** que se enlaza
      (como AE, que convierte los valores al espacio del padre: aquí se guarda el reposo y la hija conserva sus
      números). Cadenas de padres, sin ciclos. La opacidad no se hereda (como AE).
- [ ] A2. **Objeto nulo**: capa de forma que no se dibuja (`Clip::isNull`), solo su marco en la vista previa.
- [ ] A3. **Desenfoque de movimiento** por capa (interruptor) + ángulo de obturación y muestras del proyecto.

## Etapa B — Capas de forma como AE
- [ ] B1. Pluma: dibujar el trazado en la vista previa; trazado animable (claves de trazado, transformar una forma
      en otra).
- [ ] B2. Recortar trazados (inicio, fin, desplazamiento), animables.
- [ ] B3. Repetidor (copias, desplazamiento, posición/escala/rotación por copia, opacidad inicio/fin).
- [ ] B4. Desplazar trazado, sacudir trazado, retorcer, redondear esquinas (los que quepan).

## Etapa C — Comportamientos (expresiones) y mates de seguimiento
- [ ] C1. Comportamientos por propiedad: Temblor (`wiggle`), Repetir (`loopOut` ciclo / ida y vuelta / continuar),
      Velocidad constante (`time * n`), Enlazar a otra propiedad (con multiplicador y desfase).
- [ ] C2. Mate de seguimiento: la capa de arriba como mate alfa / alfa invertido / luminancia / luminancia invertida.

## Etapa D — Curvas, tiempo, vista previa y 3D
- [ ] D1. Editor de curvas: velocidad de las claves escrita a mano (influencia %), auto-orientar al trazado.
- [ ] D2. Reasignación de tiempo con claves.
- [ ] D3. Vista previa: resolución ½/¼, fondo a cuadros, zonas seguras (lo que falte).
- [ ] D4. 3D: luces (si cabe).

## Dónde vive cada cosa
- Matriz de los padres: `src/engine/TransformLayer.*` (`transformParentsAt` = capas de transformación por pista;
  ahora también el padre de cada clip). El compositor la aplica en `buildGpuScene` (`applyParent`) y la vista
  previa dibuja los controles a través de ella (`PreviewController::clipsAtPlayhead`).

## Cómo se probó / qué falta probar
- (se va llenando)
