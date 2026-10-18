"""Reemplaza la sección «0.15.0 EN CURSO» de CLAUDE.md por la de la versión publicada."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip")
path = ROOT / "CLAUDE.md"
text = path.read_text(encoding="utf-8")

start = text.index("### 0.15.0 EN CURSO")
end = text.index("### 0.14.0 PUBLICADA")

new = """### 0.15.0 PUBLICADA (2026-10-18) — Stock para creadores: 300 plantillas youtuber, contadores y kits
- Rama `flip/v0.15.0` → **PR #22** → `main`; **tag `v0.15.0`**. Release publicado (run 39094220184) con instalador,
  portable y `SHA256SUMS`; copia en `versiones\\FlipStudio-0.15.0`. **MSIX** en
  `tienda\\FlipStudio-Store\\paquete-0.15.0\\FlipStudio-0.15.0.0-x64.msix` (run 39094247870). Novedades de la web
  desplegadas (`flipstudio-web` commit `248aa`).
- **CI:** dos ensayos en verde sobre la rama (39082599750 y 39093137986: compilación + 16 suites + instalador y
  portable). **Ojo:** el run del tag tardó más de una hora en el paso `Build` (caché de dependencias fría); no es un
  fallo, pero no asustarse.
- A: menú de Stock con chips bajo «Todos» (`MarketTab.qml`, `CategoryScrollOn` en `StockBrowser.qml`), hover en
  todas las tarjetas, **Halloween fuera** (índices, generadores, kit, temporada del servidor; lo borrado está en
  `tienda\\plantillas\\quitado-halloween`; Día de Muertos se queda). Categorías nuevas `youtuber` y `counter` con su
  nombre en `SceneTemplateCatalog.cpp` y su traducción.
- B: **300 plantillas de estilo youtuber** (categoría `youtuber`; miniaturas en `thumbnail`, intros y finales en
  `intro`/`outro`). C: 43 sonidos, 40 superposiciones ×2 y 24 marcos para la cámara, 23 transiciones, 20 contadores
  y 24 tercios de redes. D: 29 kits en `tools/stock_kits/kits.py` (los 390 elementos existen en el índice final).
- **Auditoría de marcas de las fotos de muestra: TERMINADA.** 781 fotos revisadas una por una entre 19 tandas de
  agentes, **46 fotos más bloqueadas** en `kit.BLOCKED` (Costa, Toyota, Apple, Dell, Disney/Mickey, Adidas, Schwinn,
  SHUA, Ibanez, Gretsch, Shure, Puma, THRASHER, Ruffino, matrículas…) y **177 cambios de foto** en los módulos con
  `fix_blocked_samples.py`; tarjetas rehechas (`stale_renders.py` da 0 desactualizadas) y `check_blocked.py` prueba
  que ninguna plantilla usa una foto bloqueada. `merge_audit.py --apply` vuelca los informes en `kit.py`.
  - **Un solo `BLOCKED`:** `templates_y2.py` tenía su propia lista y se desincronizaba; ahora es `kit.BLOCKED`.
  - **12 muestras eran PNG con extensión `.jpg`** (`friends-03` y `y6-h-hands-06` con alfa): las dos renombradas a
    `.png` (`sample_file()` prueba `.png` antes de `.jpg`) y diez reencodadas a JPEG. `read_image` se negaba a
    abrirlas y los agentes las saltaban.
  - Decisión de Jorge: kits de fecha **solo con calendario del hemisferio norte**; contadores **con cortes** (animar
    los números en el motor queda para otra versión).
- **i18n:** los 13 idiomas cubren 4.140 elementos y 151 categorías (`build.py --strict` sin faltantes), con la
  categoría `youtuber` y las 300 plantillas nuevas.
- **Contenido desplegado en el VPS** (`api.getflipstudio.com/plantillas/`, 5,5 GB): solo se subieron **1,6 GB
  (2.837 archivos cambiados)** con `tools/scene_templates/publish_delta.py` + `apply_delta.sh` (clon por enlaces
  duros, `tar --unlink-first` y swap de la carpeta entera). Comprobado en vivo con `verify_published.py`: 1.221
  plantillas (300 `yt-*`), zips y miniaturas idénticos byte a byte, packs al día, 29 kits, i18n 4.140 y cero
  elementos de Halloween.
- **Servidor `stock-0.15` DESPLEGADO** (PM2, health `{"ok":true}`): sin Halloween (temporada y sinónimo).
- **Trampa nueva:** `scp` a un **nombre que ya existe** en `/tmp` se queda escribiendo sin que el tamaño avance (el
  archivo viejo conserva tamaño y fecha). Subir con un nombre nuevo.
- **Falta (Jorge):** el TXT `version` del DNS a 0.15.0 y subir el MSIX a Partner Center con las notas de
  `docs/store-listing.md` (811/1500).
- **Aviso:** la sesión de Google de la app se cayó durante las pruebas (el servidor revoca la familia cuando llega un
  `refresh_token` ya usado, y las pruebas de ventana restauran el registro). Hay que **volver a iniciar sesión** con
  Google la primera vez que se abra la 0.15.0; no afecta a nada más.

"""

path.write_text(text[:start] + new + text[end:], encoding="utf-8", newline="")
print("bytes:", len(path.read_text(encoding="utf-8").encode("utf-8")))
