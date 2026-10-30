# Ejemplos de la pantalla de inicio (0.27)

Seis videos ya armados que se bajan desde `https://getflipstudio.com/modelos/ejemplo/` (VPS
`/var/www/flipstudio-models/modelos/ejemplo/`, fuera del deploy del sitio). La app lee `ejemplos.json` (archivo,
SHA-256, títulos, «qué enseña» y guía de 3 pasos en es/en) y guarda la última copia para arrancar sin conexión.

1. `buscar2.py` / `fotos.py` buscan en Pexels (clave en `secretos\api-claves.txt`), `hoja.py` hace la hoja de
   contacto, `bajar.py` baja lo elegido (créditos en `creditos.txt`).
2. Recortar con ffmpeg al tramo usado (1080×1920 o 1920×1080, `crf 22`).
3. `ejN.py` escribe la lista de llamadas MCP; se corre con `tools/e2e/mcp_e2e.py` sin ventana: arma el proyecto,
   `package_project` lo empaqueta (`ejemplo-N.flip`) y exporta una vista para revisarla cuadro a cuadro.
4. `ejemplos.py` regenera `ejemplos.json` con los hashes; subir primero los `.flip`/`.jpg` y después el json.

Trampas: dos textos a la vez van en pistas distintas (`add_track` + `move_to_track`, si no el segundo se corre);
colores de forma como `#RRGGBB`; `set_animation` necesita `which: animIn`; la voz del ejemplo 3 se hizo con
Texto a voz (Chatterbox) en ventana y los subtítulos con `generate_subtitles`.
