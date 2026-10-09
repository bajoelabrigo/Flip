<h1 align="center">Flip Studio</h1>

<p align="center">
  <strong>Editor de video gratuito y de código abierto para Windows, Linux, macOS y Android.</strong>
</p>

<p align="center">
  <a href="https://github.com/bajoelabrigo/Flip/releases/latest">Descargar</a> ·
  <a href="https://github.com/bajoelabrigo/Flip/issues">Reportar un problema</a> ·
  <a href="LICENSE">Licencia (GPLv3)</a>
</p>

Flip Studio es un editor de video para Reels, Shorts, tutoriales, clips de juegos y cualquier video que
quieras que se vea terminado. Sin marca de agua y sin cuenta obligatoria.

> **Flip Studio está basado en [Drift](https://github.com/CutWire-Studios/Drift), de CutWire Studios.**
> Es un fork independiente: no está afiliado a CutWire Studios ni cuenta con su respaldo.
> "Drift" y "CutWire" son nombres de sus respectivos dueños.

## Descargar

Los instaladores se publican en la página de
[releases](https://github.com/bajoelabrigo/Flip/releases/latest):

| Plataforma | Paquete |
|------------|---------|
| Windows | `FlipStudio-Setup-<versión>-x64.exe` · `FlipStudio-Portable-<versión>-x64.zip` |

Las demás plataformas llegarán más adelante.

## Funciones

Flip Studio incluye todo lo que trae Drift: timeline multipista, más de 150 transiciones y 40 efectos,
keyframes, texto y subtítulos con estilo, subtítulos automáticos en tu equipo, 3D y animaciones
Lottie, recorte de sujetos, estabilización, mezcla de audio y exportación a MP4, GIF o solo audio.

Las funciones propias de Flip Studio se anotan en el [CHANGELOG](CHANGELOG.md).

## Para desarrolladores

- [Compilar, probar y empaquetar](docs/BUILDING.md) (documentación heredada de Drift)
- [Efectos GPU](docs/gpu-effects.md) · [Transiciones GPU](docs/gpu-transitions.md)
- [Acceso para agentes / MCP](docs/MCP.md)

Para compilar los instaladores de Windows sin instalar nada: pestaña **Actions** → **Build** →
**Run workflow** → plataforma `windows`. Los archivos quedan como artefactos de esa ejecución.

Para traer las novedades de Drift:

```bash
git fetch upstream
git merge upstream/main
```

Los identificadores internos (`drift::`, `DRIFT_*`, el módulo QML `Drift` y las extensiones
`.drift` / `.driftfx`) conservan su nombre a propósito, para que las fusiones con Drift sean
sencillas y Flip Studio abra proyectos y efectos hechos en Drift.

## Licencia

Flip Studio se distribuye bajo la **GNU General Public License v3** — ver [LICENSE](LICENSE). Algunas
dependencias usan otras licencias compatibles; en particular JUCE se usa bajo AGPLv3.

- Copyright © CutWire Studios — código original de Drift.
- Copyright © colaboradores de Flip Studio — modificaciones desde 2026-10-09 (ver historial de git).

El código fuente completo de cada versión está en este repositorio.
