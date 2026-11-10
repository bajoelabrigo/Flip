"""Renders the other-shape version of templates as the app fits them (layoutfit.fit_doc, the port of
SceneTemplateLayout's fitOverlayLayout): a wide template as a Short (1080x1920) and a tall one as a video
(1920x1080), into <out>/<id>/preview-short.mp4 or preview-horizontal.mp4, to look at before the app is built.

    py short_check.py --only "mod:templates_tit_h,tit6-you" --out E:/... [--work ...] [--exe ...]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import build
import renderlock
import templates
from layoutfit import fit_doc


def main() -> int:
    parser = argparse.ArgumentParser()
    for key, value in build.DEFAULTS.items():
        parser.add_argument(f"--{key}", type=Path, default=value)
    parser.add_argument("--only", default="")
    args = parser.parse_args()
    only = {s for s in args.only.split(",") if s}
    modules = {s[4:] for s in only if s.startswith("mod:")}
    only -= {f"mod:{m}" for m in modules}
    jobs = []
    for make in templates.TEMPLATES:
        if make.__module__ not in modules and not only:
            continue
        t = make()
        if make.__module__ not in modules and t.id not in only:
            continue
        if "kit:transiciones" in t.tags:
            continue
        render_path = build.build_package(t, args.out, args.work, args.samples, args.music)
        doc = json.loads(Path(render_path).read_text(encoding="utf-8"))
        wide = t.w > t.h
        to = (1080, 1920) if wide else (1920, 1080)
        lower = any(tag in t.tags for tag in ("kit:lowerthirds", "kit:tercios", "tercio"))
        fitted = fit_doc(doc, *to, fit="lowerthird" if lower else "keep")
        sid = f"{t.id}-{'short' if wide else 'horizontal'}"
        path = args.work / sid / "project.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(fitted), encoding="utf-8")
        pkg = args.work / sid / "pkg"
        pkg.mkdir(parents=True, exist_ok=True)
        proxy = SimpleNamespace(id=sid, w=to[0], h=to[1], duration=t.duration, thumb_at=t.thumb_at)
        jobs.append((proxy, path, pkg, args.out / t.id, wide))
        print(f"built {sid}", flush=True)
    if jobs:
        with renderlock.exclusive("rendering"):
            build.render_all([(p, path, pkg) for p, path, pkg, _, _ in jobs], args.exe, args.work)
    for proxy, _, pkg, out, wide in jobs:
        src = pkg / ("preview.mp4" if wide else "preview-wide.mp4")
        if src.exists():
            shutil.copy2(src, out / ("preview-short.mp4" if wide else "preview-horizontal.mp4"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
