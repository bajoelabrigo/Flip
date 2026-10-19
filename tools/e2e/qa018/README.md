# Control de calidad de la 0.18 por MCP (sin ventana)

Copia de los scripts de `Downloads\FlipStudio\pruebas\qa018` (donde se corren: la app de prueba está en
`qa018\app`, los archivos en `qa018\media` y los resultados en `qa018\out`). Ver `docs/plan-0.18.1.md`.

- `qa.py`: sesión MCP (`Session.call`, `issue`) sobre `mcp_e2e.Bridge`.
- `qa_media.py`: importar los archivos de `media\`, editar, guardar/reabrir y exportar MP4 y GIF.
- `qa_render.py`: cada efecto y cada transición del catálogo, con captura.
- `qa_misc.py`: texto, stickers, formas, audio, subtítulos y exportar con cada códec.
- `qa_ai.py`: máscara, fotogramas clave, estabilizar, escenas, caras, profundidad, reencuadre, ruido y Whisper.

Antes: `reg export "HKCU\Software\Flip Studio" registro-antes.reg`. Después: restaurarlo (sin tocar la clave
`account` si hubo sesión) y borrar el autoguardado y los proyectos de prueba de
`%APPDATA%\Flip Studio\Flip Studio\projects`.
