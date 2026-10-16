"""Builds Stock's text content (200 text styles, 200 text animations) and renders their cards with the app.

    py tools/text_stock/build.py [--kind styles|anims|all] [--only id,id|prefix*] [--no-render]

<root>/estilos/<id>/<id>.json          the text style file (AppController::importUserTextPreset)
<root>/animaciones/<id>/<id>.json      the text animation preset (AppController::importTextAnimationPreset)
<root>/<kind>/<id>/meta.json           names, category, tags, duration
<root>/<kind>/<id>/thumbnail.png       the card (384 x 384), rendered by the app
<root>/<kind>/<id>/preview.mp4         the hover preview (360 x 360)

<root> is Downloads/FlipStudio/tienda/textos. The render reuses the scene template harness: a portable
build OUTSIDE the repo, headless MCP, the registry backed up first and restored after (keeping the
account key the run may refresh). The animation presets reach the app through DRIFT_TEXT_ANIMATIONS
(a path relative to the exe, since the variable splits on ':'), so nothing is written to AppData.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "e2e"))

import anims_a  # noqa: E402
import anims_b  # noqa: E402
import styles_a  # noqa: E402
import styles_b  # noqa: E402
from kit import ROOT, Style, argb, available_fonts, fill, glow, grad, shadow, stroke  # noqa: E402

OUT = ROOT / "tienda" / "textos"
APPDATA = Path(os.environ["APPDATA"]) / "Flip Studio" / "Flip Studio"
REG_KEY = r"HKCU\Software\Flip Studio"
ACCOUNT_KEY = r"HKCU\Software\Flip Studio\Flip Studio\account"
EXE = ROOT / "pruebas" / "FlipStudio-0.13.0-arreglo" / "Flip Studio" / "flipstudio.exe"
BUILTIN_ANIMS = HERE.parents[1] / "presets" / "text-animations"

CARD = 1080       # the render project is CARD x CARD
THUMB = 384
PREVIEW = 360
US = 1_000_000

STYLES: list[Style] = styles_a.STYLES + styles_b.STYLES
ANIMS = anims_a.ANIMS + anims_b.ANIMS
for _i, _a in enumerate(ANIMS):
    _a.order = _i  # gallery order inside the app: the order of the design files

STYLE_CATEGORIES = {
    "subtitulos": {"es": "Subtítulos virales", "en": "Viral captions"},
    "titulos": {"es": "Títulos", "en": "Titles"},
    "llamadas": {"es": "Llamadas a la acción", "en": "Calls to action"},
    "tercios": {"es": "Tercios inferiores", "en": "Lower thirds"},
    "precios": {"es": "Precios y ofertas", "en": "Prices and offers"},
    "citas": {"es": "Citas y frases", "en": "Quotes"},
    "neon": {"es": "Neón", "en": "Neon"},
    "3d": {"es": "3D y relieve", "en": "3D and emboss"},
    "retro": {"es": "Retro y Y2K", "en": "Retro and Y2K"},
    "elegante": {"es": "Elegante y bodas", "en": "Elegant and weddings"},
    "infantil": {"es": "Infantil y divertido", "en": "Kids and fun"},
    "gaming": {"es": "Gaming y deportes", "en": "Gaming and sports"},
    "terror": {"es": "Terror y Halloween", "en": "Horror and Halloween"},
    "fechas": {"es": "Fechas especiales", "en": "Special days"},
}
ANIM_CATEGORIES = {
    "maquina": {"es": "Máquina de escribir", "en": "Typewriter"},
    "karaoke": {"es": "Karaoke palabra por palabra", "en": "Word-by-word karaoke"},
    "rebote": {"es": "Rebote y ritmo", "en": "Bounce and rhythm"},
    "golpe": {"es": "Escala y golpe", "en": "Scale and punch"},
    "deslizar": {"es": "Deslizar y barrer", "en": "Slides and wipes"},
    "neon": {"es": "Neón y luces", "en": "Neon and lights"},
    "glitch": {"es": "Glitch y digital", "en": "Glitch and digital"},
    "onda": {"es": "Ondas y flotar", "en": "Waves and floating"},
    "caer": {"es": "Caer y subir", "en": "Fall and rise"},
    "desenfoque": {"es": "Desenfoque y fundido", "en": "Blur and fade"},
    "giro": {"es": "Giro y 3D", "en": "Spin and 3D"},
    "brillo": {"es": "Brillo y color", "en": "Shine and colour"},
}

BACKDROPS = {
    "dark": ("#30343f", "#121419"), "light": ("#fbfaf7", "#dcd8cf"), "warm": ("#f8ecda", "#dcc6a6"),
    "night": ("#1c1736", "#06050c"), "chalk": ("#2e4d3e", "#15241c"), "cool": ("#dfe9f3", "#a9bccf"),
}

# The text look an animation card is shown in.
LOOKS = {
    "bold": dict(font="Montserrat", size=104, weight=900,
                 layers=[shadow(dy=0.05, blur=0.14, opacity=0.6), stroke(0.05, "#16181f"), fill("#ffffff")]),
    "caption": dict(font="Montserrat", size=86, weight=900,
                    layers=[shadow(dy=0.05, blur=0.1, opacity=0.6), stroke(0.09), fill("#ffffff")]),
    "mono": dict(font="Special Elite", size=92, weight=400, layers=[fill("#f4efe2")]),
    "tech": dict(font="Orbitron", size=88, weight=800,
                 layers=[glow("#00e5ff", 0.25, 0.55), stroke(0.02, "#00e5ff"), fill("#f2feff")]),
    "gold": dict(font="Cinzel", size=150, weight=900,
                 layers=[shadow(dy=0.05, blur=0.12, opacity=0.6),
                         fill(grad([(0, "#fff4cf"), (0.5, "#d9a93f"), (1, "#9c6b17")], 90))]),
}
ANIM_BACKDROP = ("#2c2f45", "#0f1018")


def mix(hex_a: str, hex_b: str, t: float) -> str:
    a = [int(hex_a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def backdrop(card: str) -> tuple[str, str]:
    if card in BACKDROPS:
        return BACKDROPS[card]
    return mix(card, "#ffffff", 0.14), mix(card, "#000000", 0.35)


def kf(v: float) -> dict:
    return {"keyframes": [{"timeUs": 0, "value": float(v)}]}


def box(x, y, w, h) -> dict:
    return {"x": kf(x), "y": kf(y), "width": kf(w), "height": kf(h)}


def project(text: str, style: dict, seconds: float, colors: tuple[str, str], margin: int = 60) -> dict:
    us = int(round(seconds * US))
    inner, outer = colors
    bg = {"kind": "rectangle", "cornerRadius": 0, "layers": [
        fill(grad([(0, inner), (1, outer)], kind="radial", oklab=True)),
        {"id": "stroke", "kind": "stroke", "enabled": False, "width": 0, "strokeAlign": "inside",
         "paint": {"kind": "solid", "color": "#ffffffff"}}]}
    bg["layers"][0]["paint"]["gradient"]["center"] = [0.5, 0.42]
    bg["layers"][0]["paint"]["gradient"]["scale"] = 0.85
    clip = {"srcInUs": 0, "srcOutUs": us, "timelineStartUs": 0, "timelineDurationUs": us}
    return {
        "version": 14, "projectName": "text-card", "width": CARD, "height": CARD, "fps": 30, "sampleRate": 48000,
        "background": {"kind": "color", "color": argb(outer)}, "assets": [],
        "tracks": [
            {"id": "t2", "type": "text", "name": "Texto", "transitions": [], "clips": [
                {"id": "c2", "type": "text", **clip, "textContent": text, "textStyle": style,
                 **box(margin, margin, CARD - 2 * margin, CARD - 2 * margin)}]},
            {"id": "t1", "type": "shape", "name": "Fondo", "transitions": [], "clips": [
                {"id": "c1", "type": "shape", **clip, "shapeStyle": bg, **box(0, 0, CARD, CARD)}]},
        ],
    }


# --- styles -------------------------------------------------------------------------------------

def style_job(st: Style) -> dict:
    folder = OUT / "estilos" / st.id
    folder.mkdir(parents=True, exist_ok=True)
    doc = st.document()
    (folder / f"{st.id}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    render_style = json.loads(json.dumps(doc["style"]))
    render_style["valign"] = "middle"  # the card centres captions and lower thirds
    seconds = 3.0
    render = folder / "render.json"
    render.write_text(json.dumps(project(st.sample[0], render_style, seconds, backdrop(st.card))), encoding="utf-8")
    meta = {"id": st.id, "names": {"es": st.es, "en": st.en}, "category": st.category, "tags": st.tags,
            "subtitle": st.subtitle, "durationSec": seconds, "font": st.font, "sample": st.sample[0]}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"id": st.id, "folder": folder, "render": render, "seconds": seconds, "at": st.card_at}


# --- animations ---------------------------------------------------------------------------------

def units(text: str, unit: str) -> int:
    if unit == "word":
        return max(1, len(text.split()))
    if unit == "line":
        return max(1, len(text.split("\n")))
    if unit == "block":
        return 1
    return max(1, len(re.sub(r"\s", "", text)))


def reveal_seconds(an, text: str) -> float:
    d = an.param_defaults()
    if "in" not in an.slots and "out" not in an.slots:
        return 0.0
    n = units(text, d.get("unit", "block"))
    order = d.get("order", "forward")
    slots = (n - 1) / 2 if order == "centerOut" else (n - 1)
    return float(d.get("duration", 0.4)) + float(d.get("stagger", 0.06)) * slots


def anim_job(an, presets_dir: Path) -> dict:
    folder = OUT / "animaciones" / an.id
    folder.mkdir(parents=True, exist_ok=True)
    doc = an.document()
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    (folder / f"{an.id}.json").write_text(text, encoding="utf-8")
    (presets_dir / f"{an.id}.json").write_text(text, encoding="utf-8")
    look = LOOKS[an.look]
    style = Style(an.id, "", "", "", an.sample, look["font"], look["size"], look["weight"], look["layers"]).style_json()
    slot = {"preset": an.id}
    if "in" in an.slots:
        style["animation"]["in"] = slot
    if "out" in an.slots:
        style["animation"]["out"] = slot
    if "loop" in an.slots:
        style["animation"]["loop"] = slot
    d = an.param_defaults()
    reveal = reveal_seconds(an, an.sample[0])
    caret_lead = float(d.get("lead", 0.0)) if an.caret else 0.0
    hold = an.hold if an.hold is not None else 1.0
    if an.slots == ["loop"]:
        period = float(d.get("period", 0) or 0)
        seconds = max(3.0, min(6.0, 2 * period)) if period else 3.0
        at = min(seconds * 0.4, 1.3) if not period else period * 0.42 + (period if period < 1.0 else 0)
    elif an.slots == ["out"]:
        seconds = 0.9 + reveal
        at = 0.9 + reveal * 0.45
    elif "in" in an.slots and "out" in an.slots:
        seconds = caret_lead + reveal + hold + reveal
        at = caret_lead + reveal * 0.62
    else:  # in only
        seconds = caret_lead + reveal + hold + 0.6
        at = caret_lead + reveal * 0.62
    seconds = round(max(seconds, 1.6), 2)
    render = folder / "render.json"
    render.write_text(json.dumps(project(an.sample[0], style, seconds, ANIM_BACKDROP)), encoding="utf-8")
    meta = {"id": an.id, "names": {"es": an.es, "en": an.en}, "category": an.category, "tags": an.tags,
            "slots": an.slots, "durationSec": seconds, "sample": an.sample[0]}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"id": an.id, "folder": folder, "render": render, "seconds": seconds, "at": at}


# --- checks -------------------------------------------------------------------------------------

def check() -> list[str]:
    problems = []
    fonts = available_fonts()
    for st in STYLES:
        for f, w, i in st.fonts():
            if f not in fonts:
                problems.append(f"{st.id}: font {f} is not in fonts.basic / fonts.extra")
            elif (w, i) not in fonts[f]:
                problems.append(f"{st.id}: {f} has no weight {w}{' italic' if i else ''}")
        if st.category not in STYLE_CATEGORIES:
            problems.append(f"{st.id}: unknown category {st.category}")
    builtin = {p.stem for p in BUILTIN_ANIMS.glob("*.json")}
    seen = set()
    for an in ANIMS:
        if an.id in builtin:
            problems.append(f"{an.id}: clashes with a built-in preset id")
        if an.id in seen:
            problems.append(f"{an.id}: duplicate id")
        seen.add(an.id)
        if an.category not in ANIM_CATEGORIES:
            problems.append(f"{an.id}: unknown category {an.category}")
        text = json.dumps(an.document())
        declared = set(an.param_defaults())
        for ref in set(re.findall(r'"\{(\w+)\}"', text)) | set(re.findall(r'"\$": "(\w+)"', text)):
            if ref not in declared:
                problems.append(f"{an.id}: references undeclared param {ref}")
    ids = [s.id for s in STYLES]
    for i in {x for x in ids if ids.count(x) > 1}:
        problems.append(f"{i}: duplicate style id")
    names = [a.es for a in ANIMS]
    for n in {x for x in names if names.count(x) > 1}:
        problems.append(f"animation name used twice: {n}")
    return problems


# --- render -------------------------------------------------------------------------------------

def payload(reply) -> dict:
    from mcp_e2e import reply_text
    for text in reply_text(reply):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return {"error": reply.get("error") or reply}


def render(jobs: list[dict], presets_dir: Path, exe: Path, previews: bool) -> None:
    from mcp_e2e import Bridge
    from PIL import Image

    os.environ["DRIFT_TEXT_ANIMATIONS"] = os.path.relpath(presets_dir, exe.parent)
    backup = Path(tempfile.gettempdir()) / f"flip-reg-{os.getpid()}.reg"
    account = Path(tempfile.gettempdir()) / f"flip-account-{os.getpid()}.reg"
    subprocess.run(["reg", "export", REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    projects_before = set((APPDATA / "projects").glob("*")) if (APPDATA / "projects").exists() else set()
    bridge = Bridge(str(exe), "", str(OUT / "_mcp"), str(ROOT / "codigo" / "flip-addons" / "build" / "stage"))
    failed = []
    try:
        time.sleep(3)
        for n, job in enumerate(jobs, 1):
            print(f"[{n}/{len(jobs)}] {job['id']}", flush=True)
            loaded = payload(bridge.call("load_project", {"path": str(job["render"])}, wait=120))
            if loaded.get("error") or loaded.get("ok") is False:
                print(f"  load failed: {loaded}", flush=True)
                failed.append(job["id"])
                continue
            shot = payload(bridge.call("capture", {"at": job["at"], "full": True}, wait=120))
            path = shot.get("path")
            if not path or not Path(path).exists():
                print(f"  capture failed: {shot}", flush=True)
                failed.append(job["id"])
                continue
            with Image.open(path) as im:
                im.convert("RGB").resize((THUMB, THUMB), Image.LANCZOS).save(job["folder"] / "thumbnail.png",
                                                                           optimize=True)
            os.remove(path)
            if not previews:
                continue
            preview = job["folder"] / "preview.mp4"
            preview.unlink(missing_ok=True)
            bridge.call("export_video", {"path": str(preview), "in": 0, "out": job["seconds"], "video": "h264",
                                         "audio": "aac", "rate": "crf", "crf": 28, "fps": 30, "height": PREVIEW},
                        wait=600)
            deadline = time.time() + 600
            while time.time() < deadline:
                status = payload(bridge.call("export_status", {}, wait=30))
                if not status.get("active") and not status.get("busy"):
                    break
                time.sleep(0.3)
            if not preview.exists():
                print(f"  preview failed: {status}", flush=True)
                failed.append(job["id"])
    finally:
        bridge.close()
        subprocess.run(["reg", "export", ACCOUNT_KEY, str(account), "/y"], capture_output=True)
        subprocess.run(["reg", "delete", REG_KEY, "/f"], capture_output=True)
        subprocess.run(["reg", "import", str(backup)], check=True, capture_output=True)
        if account.exists():
            subprocess.run(["reg", "import", str(account)], capture_output=True)
            account.unlink()
        backup.unlink(missing_ok=True)
        if autosave.exists() and not had_autosave:
            autosave.unlink()
        if (APPDATA / "projects").exists():
            for extra in set((APPDATA / "projects").glob("*")) - projects_before:
                shutil.rmtree(extra, ignore_errors=True) if extra.is_dir() else extra.unlink(missing_ok=True)
    if failed:
        print(f"FAILED ({len(failed)}): {','.join(failed)}")


def selected(ids: list[str], only: str) -> set[str]:
    if not only:
        return set(ids)
    out = set()
    for pat in only.split(","):
        out |= {i for i in ids if (i.startswith(pat[:-1]) if pat.endswith("*") else i == pat)}
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["styles", "anims", "all"], default="all")
    parser.add_argument("--only", default="")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--exe", type=Path, default=EXE)
    args = parser.parse_args()

    problems = check()
    for p in problems:
        print("CHECK:", p)
    if problems:
        return 1
    print(f"{len(STYLES)} styles, {len(ANIMS)} animations")

    presets_dir = OUT / "animaciones" / "_presets"
    presets_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    if args.kind in ("styles", "all"):
        keep = selected([s.id for s in STYLES], args.only)
        jobs += [style_job(s) for s in STYLES if s.id in keep]
    if args.kind in ("anims", "all"):
        keep = selected([a.id for a in ANIMS], args.only)
        # Every preset goes to the app's folder, so a partial run still resolves all of them.
        for a in ANIMS:
            (presets_dir / f"{a.id}.json").write_text(json.dumps(a.document(), ensure_ascii=False, indent=1),
                                                      encoding="utf-8")
        jobs += [anim_job(a, presets_dir) for a in ANIMS if a.id in keep]
    print(f"{len(jobs)} cards to render")
    if args.no_render or not jobs:
        return 0
    render(jobs, presets_dir, args.exe, not args.no_preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
