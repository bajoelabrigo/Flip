"""Builds the scene template packages and renders their thumbnails and previews with the app.

    <venv python> tools/scene_templates/build.py [--only id,id] [--no-render]

For every template in templates.py:
  <out>/<id>/template.json, project.json (slots empty), media/ (music cut, fixed pictures)
  <work>/<id>/render.json      the same edit with the sample photos in the slots, absolute paths
then, with --exe (a portable build OUTSIDE the repo), one headless app session loads each render
copy, captures the thumbnail frame and exports a small preview:
  <out>/<id>/thumbnail.png (432x768), preview.mp4 (360x640)

The app writes to HKCU\\Software\\Flip Studio even headless (recent projects, preferences): the key
is exported first and put back afterwards, and a leftover autosave is removed (CLAUDE.md).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "e2e"))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import kit  # noqa: E402
import templates  # noqa: E402
from mcp_e2e import Bridge, reply_text  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio"
APPDATA = Path(os.environ["APPDATA"]) / "Flip Studio" / "Flip Studio"
DEFAULTS = {
    "out": ROOT / "tienda" / "plantillas" / "paquetes",
    "work": ROOT / "tienda" / "plantillas" / "trabajo",
    "samples": ROOT / "tienda" / "plantillas" / "muestras",
    "music": APPDATA / "addons" / "musica.libre" / "sound-effects" / "musica",
    "exe": ROOT / "pruebas" / "FlipStudio-0.13.0-arreglo" / "Flip Studio" / "flipstudio.exe",
}
REG_KEY = r"HKCU\Software\Flip Studio"


def photo_size_from(samples: Path, media: Path):
    cache: dict[str, tuple[int, int]] = {}

    def size(name: str) -> tuple[int, int]:
        if name not in cache:
            path = sample_file(samples, name)
            if not path.exists():
                path = media / name
            with Image.open(path) as im:
                cache[name] = im.size
        return cache[name]
    return size


def sample_file(samples: Path, name: str) -> Path:
    """A sample is <name>.jpg, or <name>.png for pictures with transparency (the sample logos)."""
    png = samples / f"{name}.png"
    return png if png.exists() else samples / f"{name}.jpg"


def cut_music(music_dir: Path, music_id: str, start: float, duration: float, target: Path) -> None:
    source = music_dir / f"{music_id}.m4a"
    if not source.exists():
        raise SystemExit(f"music {music_id} not found in {music_dir}")
    fade = min(1.2, duration / 4)
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}",
                    "-i", str(source), "-af", f"afade=t=in:d=0.15,afade=t=out:st={duration - fade:.3f}:d={fade:.3f}",
                    "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", str(target)], check=True)


def build_package(t, out: Path, work: Path, samples: Path, music_dir: Path) -> Path:
    pkg = out / t.id
    if pkg.exists():
        shutil.rmtree(pkg)
    (pkg / "media").mkdir(parents=True)
    if t.music:
        cut_music(music_dir, t.music[0], t.music[1], t.duration, pkg / "media" / "music.m4a")
    blocked = sorted({c["_sample"] for track in t.tracks for c in track.clips if c.get("_sample") in kit.BLOCKED})
    if blocked:
        raise SystemExit(f"{t.id}: sample photos with brands or logos: {', '.join(blocked)}")
    size = photo_size_from(samples, HERE / "media")
    for clip in (c for track in t.tracks for c in track.clips):
        if "_media" in clip:
            shutil.copy2(HERE / "media" / clip["_media"], pkg / "media" / clip["_media"])
    package_doc = t.document(render=False, photo_size=size, sample_path=lambda n: sample_file(samples, n), media_root=None)
    render_doc = t.document(render=True, photo_size=size, sample_path=lambda n: sample_file(samples, n),
                            media_root=pkg / "media")
    (pkg / "project.json").write_text(json.dumps(package_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (pkg / "template.json").write_text(json.dumps(t.manifest(), ensure_ascii=False, indent=2), encoding="utf-8")
    (work / t.id).mkdir(parents=True, exist_ok=True)
    render_path = work / t.id / "render.json"
    render_path.write_text(json.dumps(render_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return render_path


CARD = (432, 768)


def story_times(t) -> list[float]:
    """Two more moments for the storyboard card, away from the thumbnail moment."""
    d = t.duration
    picks = [x * d for x in (0.22, 0.5, 0.8, 0.95) if abs(x * d - t.thumb_at) > 0.18 * d]
    return sorted(picks[:2])


def wide_card(frames: list[Image.Image]) -> Image.Image:
    """A 16:9 template on the 9:16 card the Stock and Templates grids draw: a storyboard of three moments
    stacked edge to edge (the thumbnail moment on top), with a «16:9» chip on it so the grid tells the
    formats apart."""
    w, h = CARD
    card = Image.new("RGB", CARD, (14, 14, 18))
    fh = round(w * 9 / 16)
    gap = (h - 3 * fh) // 2
    for i, frame in enumerate(frames[:3]):
        shot = frame.convert("RGB").resize((w, fh), Image.LANCZOS)
        card.paste(shot, (0, i * (fh + gap)))
    chip = ImageDraw.Draw(card)
    x1, y1 = w - 12, fh - 12
    chip.rounded_rectangle([x1 - 70, y1 - 28, x1, y1], 14, fill=(255, 255, 255))
    chip.text((x1 - 35, y1 - 14), "16:9", fill=(20, 20, 24), anchor="mm")
    return card


def square_card(frame: Image.Image) -> Image.Image:
    """A 1:1 template on the 9:16 grid card: the square edge to edge in the middle, over a blurred, darkened
    copy of itself, with a «1:1» chip under it."""
    w, h = CARD
    bg = frame.convert("RGB").resize((h, h), Image.LANCZOS)
    bg = bg.crop(((h - w) // 2, 0, (h - w) // 2 + w, h)).filter(ImageFilter.GaussianBlur(24))
    bg = Image.blend(bg, Image.new("RGB", CARD, (8, 8, 12)), 0.45)
    y = (h - w) // 2
    bg.paste(frame.convert("RGB").resize((w, w), Image.LANCZOS), (0, y))
    chip = ImageDraw.Draw(bg)
    cx, cy = w // 2, y + w + 34
    chip.rounded_rectangle([cx - 34, cy - 13, cx + 34, cy + 13], 13, fill=(255, 255, 255))
    chip.text((cx, cy), "1:1", fill=(20, 20, 24), anchor="mm")
    return bg


def square_preview(source: Path, target: Path) -> None:
    """The 640x640 export laid on a 360x640 card like the thumbnail: the square over a blurred copy."""
    graph = ("[0:v]split[a][b];[a]scale=-2:640,crop=360:640,boxblur=20:2,eq=brightness=-0.2[bg];"
             "[b]scale=360:360[fg];[bg][fg]overlay=0:140[p]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(source), "-filter_complex", graph, "-map", "[p]",
                    "-map", "0:a?", "-c:v", "libx264", "-crf", "28", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", str(target)], check=True)


def wide_preview(source: Path, target: Path, duration: float) -> None:
    """The 640x360 export as a moving storyboard: three copies a third of the loop apart, stacked on the
    360x640 card like the thumbnail."""
    fh = 202
    gap = (640 - 3 * fh) // 2
    inputs = []
    for k in range(3):
        inputs += ["-stream_loop", "-1", "-ss", f"{duration * k / 3:.3f}", "-i", str(source)]
    # Rows 1 and 2 carry the gap below them as padding, so vstack spaces them.
    graph =(";".join(f"[{k}:v]scale=360:{fh},setsar=1,pad=360:{fh + (gap if k < 2 else 0)}:0:0:color=0x0e0e12[v{k}]"
                      for k in range(3)) + ";[v0][v1][v2]vstack=inputs=3,pad=360:640:0:0:color=0x0e0e12[p]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[p]",
                    "-map", "0:a?", "-t", f"{duration:.3f}", "-c:v", "libx264", "-crf", "28", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(target)],
                   check=True)


def payload(reply) -> dict:
    for text in reply_text(reply):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return {"error": reply.get("error") or reply}


def render_all(jobs, exe: Path, work: Path) -> None:
    backup = Path(tempfile.gettempdir()) / f"flip-reg-{os.getpid()}.reg"
    subprocess.run(["reg", "export", REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    projects_before = set(os.listdir(APPDATA / "projects")) if (APPDATA / "projects").exists() else set()
    bridge = Bridge(str(exe), "", str(work / "_mcp"), str(ROOT / "codigo" / "flip-addons" / "build" / "stage"))
    try:
        time.sleep(3)
        for t, render_path, pkg in jobs:
            print(f"render {t.id}", flush=True)
            loaded = payload(bridge.call("load_project", {"path": str(render_path)}, wait=120))
            if loaded.get("error") or loaded.get("ok") is False:
                print(f"  load failed: {loaded}", flush=True)
                continue
            shot = payload(bridge.call("capture", {"at": t.thumb_at, "full": True}, wait=120))
            path = shot.get("path")
            if not path or not Path(path).exists():
                print(f"  capture failed: {shot}", flush=True)
                continue
            wide = t.w > t.h
            square = t.w == t.h
            with Image.open(path) as im:
                if square:
                    sq = im.convert("RGB")
                    sq.resize((768, 768), Image.LANCZOS).save(pkg / "thumbnail-square.png", optimize=True)
                    square_card(sq).save(pkg / "thumbnail.png", optimize=True)
                elif wide:
                    hero = im.convert("RGB")
                    hero.resize((768, 432), Image.LANCZOS).save(pkg / "thumbnail-wide.png", optimize=True)
                    frames = [hero]
                    for at in story_times(t):
                        extra = payload(bridge.call("capture", {"at": at, "full": True}, wait=120)).get("path")
                        if extra and Path(extra).exists():
                            with Image.open(extra) as ex:
                                frames.append(ex.convert("RGB").resize((768, 432), Image.LANCZOS))
                            os.remove(extra)
                    while len(frames) < 3:
                        frames.append(hero)
                    wide_card(frames).save(pkg / "thumbnail.png", optimize=True)
                else:
                    im.convert("RGB").resize((432, 768), Image.LANCZOS).save(pkg / "thumbnail.png", optimize=True)
            shutil.copy2(path, work / t.id / "frame.png")
            os.remove(path)
            preview = pkg / ("preview-wide.mp4" if wide else "preview-square.mp4" if square else "preview.mp4")
            exported = payload(bridge.call("export_video", {
                "path": str(preview), "in": 0, "out": t.duration, "video": "h264", "audio": "aac", "rate": "crf",
                "crf": 30, "fps": 30, "height": 360 if wide else 640}, wait=900))  # a square exports 640x640
            # Older builds return as soon as the encode starts.
            deadline = time.time() + 900
            while time.time() < deadline:
                status = payload(bridge.call("export_status", {}, wait=30))
                if not status.get("active") and not status.get("busy"):
                    break
                time.sleep(1.0)
            if not preview.exists() or preview.stat().st_size < 10_000:
                print(f"  export failed: {exported}", flush=True)
            elif wide:
                wide_preview(preview, pkg / "preview.mp4", t.duration)
            elif square:
                square_preview(preview, pkg / "preview.mp4")
    finally:
        bridge.close()
        subprocess.run(["reg", "delete", REG_KEY, "/f"], capture_output=True)
        subprocess.run(["reg", "import", str(backup)], check=True, capture_output=True)
        backup.unlink(missing_ok=True)
        if autosave.exists() and not had_autosave:
            autosave.unlink()
        if (APPDATA / "projects").exists():
            for name in set(os.listdir(APPDATA / "projects")) - projects_before:
                shutil.rmtree(APPDATA / "projects" / name, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    for key, value in DEFAULTS.items():
        parser.add_argument(f"--{key}", type=Path, default=value)
    parser.add_argument("--only", default="")
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()
    if HERE in args.exe.resolve().parents or Path.cwd() in args.exe.resolve().parents and ".e2e-app" in str(args.exe):
        raise SystemExit("the app must live outside the repo, or it cannot write files")
    only = {s for s in args.only.split(",") if s}
    # "mod:templates_h1" picks a whole batch; plain ids add single templates.
    modules = {s[4:] for s in only if s.startswith("mod:")}
    only -= {f"mod:{m}" for m in modules}
    jobs = []
    for make in templates.TEMPLATES:
        if modules or only:
            if make.__module__ not in modules and not only:
                continue
        t = make()
        if (modules or only) and make.__module__ not in modules and t.id not in only:
            continue
        render_path = build_package(t, args.out, args.work, args.samples, args.music)
        print(f"built {t.id}: {len(t.slots)} slots, {t.texts} texts, {t.duration:g} s", flush=True)
        jobs.append((t, render_path, args.out / t.id))
    if not args.no_render and jobs:
        render_all(jobs, args.exe, args.work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
