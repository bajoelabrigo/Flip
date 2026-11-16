"""Short clips that show the cartoon VFX engine (docs/plan-vfx.md A–E, H), one per feature, rendered with the app.

    py tools/scene_templates/vfx_demo.py --exe <portable flipstudio.exe> [--out E:\\FlipStudio\\tienda\\vfx-estudio\\motor]

Each clip has the old behaviour on the left and the new one on the right (or the feature alone), 1920×1080, 30 fps:
  A-esquinas.mp4     flame tongues morphing between path keys: rounded (left) / sharp tips kept (right)
  B-posterizar.mp4   the same moving, wobbling blob: every frame (left) / Posterize Time 12 fps (right)
  C-tono-interior.mp4  smoke puff and a liquid drop with the hard-edged second tone
  D-romperse.mp4     smoke that dies by holes (left) and fire that breaks into diagonal strips (right); a hole that
                     opens from its own centre in a morph (middle)
  E-a-saltos.mp4     electricity: jagged zig zag redrawn every frame; a blob boiling on twos
  H-combinar-grupo.mp4  live Merge Paths (subtract) between the parts of a group: a moving hole

The app writes to HKCU\\Software\\Flip Studio even headless: the key is exported first and put back afterwards (and
the Google session kept, as build.py does).
"""

from __future__ import annotations

import argparse
import json
import math
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

import vfx  # noqa: E402
from mcp_e2e import Bridge, reply_text  # noqa: E402
from scene import WIDE, Box, Template, fill, glow, keys, no_stroke, stroke  # noqa: E402

APPDATA = Path(os.environ["APPDATA"]) / "Flip Studio" / "Flip Studio"
REG_KEY = r"HKCU\Software\Flip Studio"
DUR = 3.0


def shape(t, track, box, layers, path, **style):
    clip = t.solid(track, "#ffffff", 0.0, DUR, box=box, kind="custom", layers=layers)
    st = clip["shapeStyle"]
    st["customPath"] = path
    st.update(style)
    return clip


def path_keys(st, svgs, times, ease="smooth"):
    """Path keys: svgs[i] at times[i] seconds (smooth ease between)."""
    st["pathShapes"] = list(svgs)
    st["customPath"] = svgs[0]
    st.setdefault("keyframes", {})["path"] = keys([(times[i], i, ease) for i in range(len(svgs))])


def tongue(sway, height, n):
    """A flame tongue in a 200×400 box: base on the floor, S-shaped sides meeting at a sharp tip (index n)."""
    left, right = [], []
    for i in range(n):
        u = i / n
        y = 400 - u * height
        bend = sway * math.sin(u * math.pi * 0.9) * u
        half = 80 * (1 - u) ** 0.8
        left.append((100 + bend - half, y))
        right.append((100 + bend + half, y))
    tip = (100 + sway * math.sin(math.pi * 0.9), 400 - height)
    pts = left + [tip] + list(reversed(right))
    return pts, n  # the tip's index


def blob(cx, cy, r, n, wob, phase):
    return [(cx + (r + wob * math.sin(3 * a + phase)) * math.cos(a), cy + (r + wob * math.cos(2 * a - phase)) * math.sin(a))
            for a in (2 * math.pi * i / n for i in range(n))]


def demo_a():
    t = Template("vfx-a", "Esquinas", "Corners", "vfx", DUR, size=WIDE, background="#101418")
    tr = t.track("video")
    box = (0, 0, 200, 400)
    keyset = [tongue(-40, 360, 9), tongue(50, 330, 11), tongue(-20, 390, 8), tongue(30, 350, 10)]
    for side, corners in ((0, 0), (1, 40)):
        svgs = [vfx.smooth_path([(pts, True, [tip, 0, len(pts) - 1])], box) for pts, tip in keyset]
        clip = shape(t, tr, Box(420 + side * 760, 280, 320, 640), [fill("#fd1000"), no_stroke(), glow("#ff6a04", 22, 0.7)],
                     svgs[0])
        st = clip["shapeStyle"]
        path_keys(st, svgs, [0.0, 0.9, 1.9, 2.9])
        vfx.smooth_morph(st, corners=corners)
    return t


def demo_b():
    t = Template("vfx-b", "Posterizar", "Posterize", "vfx", DUR, size=WIDE, background="#101418")
    tr = t.track("video")
    for side in (0, 1):
        x0 = 200 + side * 960
        clip = t.solid(tr, "#48a8a8", 0.0, DUR, box=Box(x0, 380, 260, 260), kind="ellipse",
                       motion=[(0.0, {"dx": 0}), (1.5, {"dx": 400, "s": 1.25}, "smooth"), (3.0, {"dx": 0})])
        clip["rotation"] = keys([(0.0, 0.0), (3.0, 360.0)])
        st = clip["shapeStyle"]
        st.update(wiggleSize=14.0, wiggleDetail=30.0, wiggleSpeed=2.0, wiggleSeed=4.0)
        if side:
            vfx.posterize(clip, 12)
    return t


def demo_c():
    t = Template("vfx-c", "Tono interior", "Inner tone", "vfx", DUR, size=WIDE, background="#1b2330")
    tr = t.track("video")
    box = (0, 0, 400, 300)
    puffs = [[(200 + (110 + 18 * math.sin(5 * a + k)) * math.cos(a), 160 + (95 + 14 * math.cos(4 * a - k)) * math.sin(a))
              for a in (2 * math.pi * i / (20 + k) for i in range(20 + k))] for k in range(4)]
    svgs = [vfx.smooth_path([(p, True)], box) for p in puffs]
    smoke = shape(t, tr, Box(220, 330, 640, 480), [fill("#dcdcdc"), no_stroke(), vfx.inner_tone("#a8a8a8", dy=-34)],
                  svgs[0])
    path_keys(smoke["shapeStyle"], svgs, [0.0, 1.0, 2.0, 3.0])
    vfx.smooth_morph(smoke["shapeStyle"])
    vfx.posterize(smoke, 12)
    drops = [[(200 + 90 * math.cos(a) * (1 - 0.25 * math.sin(a) * s), 150 + 120 * math.sin(a) * (1 + 0.2 * s))
              for a in (2 * math.pi * i / (18 + k) for i in range(18 + k))] for k, s in enumerate((0.0, 0.8, -0.4, 0.5))]
    dsvgs = [vfx.smooth_path([(p, True)], box) for p in drops]
    drop = shape(t, tr, Box(1080, 300, 560, 480),
                 [fill("#48a8a8"), no_stroke(), vfx.inner_tone("#186060", dx=-30, dy=-26, scale=96),
                  vfx.inner_tone("#ffffff", dx=40, dy=46, scale=60, invert=True, lid="shine")], dsvgs[0])
    path_keys(drop["shapeStyle"], dsvgs, [0.0, 1.0, 2.0, 3.0])
    vfx.smooth_morph(drop["shapeStyle"])
    vfx.posterize(drop, 12)
    return t


def demo_d():
    t = Template("vfx-d", "Romperse", "Break apart", "vfx", DUR, size=WIDE, background="#101418")
    tr = t.track("video")
    box = (0, 0, 400, 300)
    puff = [(200 + (120 + 16 * math.sin(5 * a)) * math.cos(a), 150 + (100 + 12 * math.cos(4 * a)) * math.sin(a))
            for a in (2 * math.pi * i / 24 for i in range(24))]
    smoke = shape(t, tr, Box(80, 340, 560, 420), [fill("#dcdcdc"), no_stroke(), vfx.inner_tone("#a8a8a8", dy=-30)],
                  vfx.smooth_path([(puff, True)], box))
    vfx.break_apart(smoke["shapeStyle"], [(0.3, 0.0, "smooth"), (2.6, 100.0)], size=46, seed=2)
    vfx.posterize(smoke, 12)
    # Middle: a hole that opens from its own centre while the blob morphs (smooth morph + from_centre).
    outer = [(200 + 130 * math.cos(a), 150 + 120 * math.sin(a)) for a in (2 * math.pi * i / 20 for i in range(20))]
    outer2 = [(200 + 125 * math.cos(a), 150 + 128 * math.sin(a)) for a in (2 * math.pi * i / 22 for i in range(22))]
    hole = [(215 + 60 * math.cos(a), 140 - 50 * math.sin(a)) for a in (2 * math.pi * i / 14 for i in range(14))]
    k0 = vfx.smooth_path([(outer, True)], box)
    k1 = vfx.smooth_path([(outer2, True), (hole, True)], box)
    mid = shape(t, tr, Box(700, 360, 520, 400), [fill("#dcdcdc"), no_stroke()], k0, customEvenOdd=True)
    path_keys(mid["shapeStyle"], [k0, k1], [0.4, 2.4])
    vfx.smooth_morph(mid["shapeStyle"], corners=0, from_centre=True)
    # Right: fire breaking into diagonal strips.
    fbox = (0, 0, 200, 400)
    pts, tip = tongue(30, 370, 10)
    fire = shape(t, tr, Box(1400, 260, 320, 640), [fill("#fd1000"), no_stroke(), glow("#ff6a04", 20, 0.6)],
                 vfx.smooth_path([(pts, True, [tip, 0, len(pts) - 1])], fbox))
    vfx.break_apart(fire["shapeStyle"], [(0.3, 0.0, "smooth"), (2.6, 100.0)], size=26, seed=7, angle=-60, stretch=4)
    vfx.posterize(fire, 12)
    return t


def demo_e():
    t = Template("vfx-e", "A saltos", "On twos", "vfx", DUR, size=WIDE, background="#0a0e1a")
    tr = t.track("video")
    line = "M 0 50 L 100 50"
    band = stroke(26, "#3048c0")
    band.update(strokeAlign="center", cap="round")
    core = stroke(7, "#d8f0f0", id="core")
    core.update(strokeAlign="center", cap="round")
    bolt = shape(t, tr, Box(160, 240, 1600, 200),
                 [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
                  glow("#3078f0", 30, 0.9), band, core], line)
    vfx.jagged_zigzag(bolt["shapeStyle"], size=40, ridges=11, jitter=85, rate=30, seed=3)
    # On twos at 30 fps = 15 drawings a second.
    boil = t.solid(tr, "#dcdcdc", 0.0, DUR, box=Box(760, 620, 400, 320), kind="ellipse")
    vfx.stepped_wiggle(boil["shapeStyle"], size=16, detail=34, rate=15, seed=2)
    return t


def demo_h():
    t = Template("vfx-h", "Combinar grupo", "Group merge", "vfx", DUR, size=WIDE, background="#101418")
    tr = t.track("video")
    clip = t.solid(tr, "#ffffff", 0.0, DUR, box=Box(560, 240, 800, 600), kind="rectangle")
    base = {"id": "p2", "name": "Base", "width": 520, "height": 520,
            "shape": {"kind": "ellipse", "layers": [fill("#ffe066"), no_stroke()]}}
    cutter = {"id": "p1", "name": "Hueco", "width": 220, "height": 220,
              "shape": {"kind": "ellipse", "layers": [fill("#ff0000"), no_stroke()]},
              "transform": {"x": -200}, "keyframes": {"x": keys([(0.0, -260.0, "smooth"), (3.0, 260.0)]),
                                                     "y": keys([(0.0, -60.0, "smooth"), (1.5, 80.0, "smooth"), (3.0, -60.0)])}}
    clip["shapeStyle"]["parts"] = [{"id": "g1", "name": "Grupo", "group": True, "merge": vfx.MERGE["subtract"],
                                    "children": [cutter, base]}]
    clip["shapeStyle"]["partsRef"] = [800, 600]
    return t


DEMOS = {"A-esquinas": demo_a, "B-posterizar": demo_b, "C-tono-interior": demo_c, "D-romperse": demo_d,
         "E-a-saltos": demo_e, "H-combinar-grupo": demo_h}


def payload(reply) -> dict:
    for text in reply_text(reply):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return {"error": reply.get("error") or reply}


def render(jobs, exe, out: Path, capture_at: float = 1.4) -> None:
    """jobs: [(name, project json path, duration s)] → <out>/<name>.mp4 and <name>.png (a frame at capture_at), with
    one headless app session; the registry, the Google session and the app's project folders are put back."""
    work = out / "_proyectos"
    work.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.gettempdir()) / f"flip-reg-vfx-{os.getpid()}.reg"
    subprocess.run(["reg", "export", REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    projects_before = set(os.listdir(APPDATA / "projects")) if (APPDATA / "projects").exists() else set()
    stage = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "codigo" / "flip-addons" / "build" / "stage"
    bridge = Bridge(str(exe), "", str(work / "_mcp"), str(stage))
    try:
        time.sleep(3)
        for name, path, dur in jobs:
            print("render", name, flush=True)
            loaded = payload(bridge.call("load_project", {"path": str(path)}, wait=120))
            if loaded.get("error") or loaded.get("ok") is False:
                print("  load failed:", loaded, flush=True)
                continue
            shot = payload(bridge.call("capture", {"at": min(capture_at, dur * 0.5), "full": True}, wait=120))
            if shot.get("path") and Path(shot["path"]).exists():
                shutil.move(shot["path"], out / f"{name}.png")
            target = out / f"{name}.mp4"
            exported = payload(bridge.call("export_video", {
                "path": str(target), "in": 0, "out": dur, "video": "h264", "audio": "aac", "rate": "crf",
                "crf": 20, "fps": 30, "height": 720}, wait=900))
            deadline = time.time() + 900
            while time.time() < deadline:
                status = payload(bridge.call("export_status", {}, wait=30))
                if not status.get("active") and not status.get("busy"):
                    break
                time.sleep(1.0)
            ok = target.exists() and target.stat().st_size > 5_000
            print("  ok" if ok else f"  export failed: {exported}", flush=True)
    finally:
        bridge.close()
        account = backup.with_name(backup.stem + "-account.reg")
        kept = subprocess.run(["reg", "export", REG_KEY + r"\Flip Studio\account", str(account), "/y"],
                              capture_output=True).returncode == 0
        subprocess.run(["reg", "delete", REG_KEY, "/f"], capture_output=True)
        subprocess.run(["reg", "import", str(backup)], check=True, capture_output=True)
        if kept:
            subprocess.run(["reg", "import", str(account)], capture_output=True)
        account.unlink(missing_ok=True)
        backup.unlink(missing_ok=True)
        if autosave.exists() and not had_autosave:
            autosave.unlink()
        if (APPDATA / "projects").exists():
            for n in set(os.listdir(APPDATA / "projects")) - projects_before:
                shutil.rmtree(APPDATA / "projects" / n, ignore_errors=True)


def write_doc(template, work: Path, name: str) -> Path:
    doc = template.document(render=True, photo_size=lambda s: (1, 1), sample_path=lambda s: s, media_root=None)
    path = work / f"{name}.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=r"E:\FlipStudio\tienda\vfx-estudio\motor")
    ap.add_argument("--only", default="")
    ap.add_argument("--also", nargs="*", default=[], help="other project .json files to render as they are (NAME=PATH:SECONDS)")
    args = ap.parse_args()
    out = Path(args.out)
    work = out / "_proyectos"
    work.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name, fn in DEMOS.items():
        if args.only and name not in args.only.split(","):
            continue
        jobs.append((name, write_doc(fn(), work, name), DUR))
    for spec in args.also:
        name, rest = spec.split("=", 1)
        path, secs = rest.rsplit(":", 1)
        jobs.append((name, Path(path), float(secs)))
    render(jobs, args.exe, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
