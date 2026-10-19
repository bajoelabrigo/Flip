"""QA 0.18: importar los 15 archivos de media/, armar una línea de tiempo, editar y exportar."""
import glob
import json
import os
import time

from qa import OUT, Q, Session

MEDIA = sorted(glob.glob(Q + r"\media\*"))
s = Session("media")


def apply(*ops, expect_ok=True, note=""):
    return s.call("apply", expect_ok=expect_ok, note=note,
                  ops=[{"tool": t, "args": a} for t, a in ops])


def res(d, i=0):
    done = d.get("done") or []
    return (done[i].get("result") or {}) if len(done) > i else {}


def brightness(png):
    try:
        from PIL import Image, ImageStat
        im = Image.open(png).convert("L")
        st = ImageStat.Stat(im)
        return round(st.mean[0], 1), round(st.stddev[0], 1)
    except Exception as e:  # noqa: BLE001
        return str(e)


try:
    apply(("new_project", {"width": 1920, "height": 1080, "fps": 30}))

    # 1. Importar cada archivo por separado: así un fallo dice cuál.
    assets = {}
    for p in MEDIA:
        d = s.call("apply", ops=[{"tool": "import_media", "args": {"paths": [p]}}], note=os.path.basename(p))
        got = res(d).get("assets") or []
        if not got:
            s.issue("import sin asset", file=p, reply=d)
            continue
        a = got[0]
        assets[os.path.basename(p)] = a
        if a.get("pending") or not a.get("kind") or a.get("index", 0) < 0 or (not a.get("dur") and a.get("kind") != "image"):
            s.issue("import sin duración", file=p, asset=a)
    print("importados", len(assets), "de", len(MEDIA))
    la = s.call("apply", ops=[{"tool": "list_assets", "args": {}}])
    rows = res(la).get("assets", [])
    for r in rows:
        if r.get("kind") in ("video", "image") and not (r.get("w") and r.get("h")):
            s.issue("asset sin tamaño", asset=r)

    # 2. Videos seguidos en la pista de video; audio aparte.
    t = 0.0
    placed = []
    for name, a in assets.items():
        if not name.startswith(("v_", "img_")):
            continue
        d = apply(("place_clip", {"asset": a["id"], "at": t}), note=name)
        r = res(d)
        if r.get("clip") or r.get("id"):
            placed.append((name, r.get("clip") or r.get("id"), t))
        insp = s.call("inspect")
        t = float(insp.get("dur") or t)
    for name, a in assets.items():
        if name.startswith("a_"):
            apply(("place_clip", {"asset": a["id"], "at": 0, "new_track": True}), note=name)

    insp = s.call("inspect", clips=True)
    print("duración", insp.get("dur"), "pistas", len(insp.get("tracks", [])), "clips", insp.get("clips"))
    with open(os.path.join(OUT, "media-timeline.json"), "w", encoding="utf-8") as f:
        json.dump(insp, f, ensure_ascii=False, indent=1)

    # 3. Captura a mitad de cada video: que no salga negra.
    clips = []
    for tr in insp.get("tracks", []):
        for it in tr.get("items", []):
            clips.append(it)
    vids = [c for c in clips if c.get("kind") in ("video", "image")]
    for c in vids:
        mid = float(c.get("start", 0)) + float(c.get("duration", 1)) / 2
        d = s.call("capture", at=mid, full=True)
        png = d.get("path")
        b = brightness(png) if png else None
        print("  captura", c.get("name"), mid, b)
        if not png or (isinstance(b, tuple) and b[1] < 2):
            s.issue("captura vacía o plana", clip=c.get("name"), at=mid, bright=b, reply=d)

    # 4. Edición sobre el primer video.
    first = next(c for c in vids if c.get("kind") == "video")
    cid = first["id"]
    st, du = float(first["start"]), float(first["duration"])
    apply(("split_clip", {"clip": cid, "at": st + du / 2}), note="cortar")
    apply(("add_effect", {"clip": cid, "effect": "blur"}), expect_ok=False)
    eff = s.call("apply", ops=[{"tool": "list_effects", "args": {"limit": 5, "q": "bright"}}])
    print("  list_effects q=bright", json.dumps(eff)[:300])
    apply(("add_transition", {"clip": cid, "kind": "crossfade", "duration": 0.5}), note="transición")
    apply(("set_clip_speed", {"clip": cid, "speed": 0.5}), note="velocidad")
    apply(("add_text", {"text": "Prueba QA 0.18", "at": 0.5}), note="texto")
    apply(("select_clip", {"clip": cid}), expect_ok=False)
    apply(("freeze_frame", {}), expect_ok=False, note="congelar")
    before = s.call("inspect").get("undo", {})
    apply(("undo", {}))
    apply(("redo", {}))
    after = s.call("inspect").get("undo", {})
    if before.get("hash") != after.get("hash"):
        s.issue("deshacer+rehacer no vuelve al mismo estado", before=before, after=after)
    n = s.call("inspect").get("notice")
    print("  notice", n)

    # 5. Guardar y volver a abrir.
    proj = os.path.join(OUT, "qa-media.drift")
    apply(("save_project", {"path": proj}))
    if not os.path.exists(proj):
        s.issue("save_project no dejó archivo", path=proj)
    clips_before = s.call("inspect").get("clips")
    apply(("load_project", {"path": proj}))
    clips_after = s.call("inspect").get("clips")
    if clips_before != clips_after:
        s.issue("al reabrir cambia el número de clips", before=clips_before, after=clips_after)

    # 6. Exportar los primeros 8 s en MP4 y en GIF, y reimportar el MP4.
    for kind, args in (("mp4", {"in": 0, "out": 8}), ("gif", {"in": 0, "out": 3, "gif": True})):
        path = os.path.join(OUT, f"qa-export.{kind}")
        if os.path.exists(path):
            os.remove(path)
        apply(("export_video", {"path": path, **args}), note=kind)
        t0 = time.time()
        while time.time() - t0 < 600:
            es = s.call("apply", ops=[{"tool": "export_status", "args": {}}])
            r = res(es)
            if not r.get("busy"):
                break
            time.sleep(2)
        print("  export", kind, round(time.time() - t0, 1), "s", json.dumps(r)[:300])
        if not os.path.exists(path) or os.path.getsize(path) < 1000:
            s.issue("exportación sin archivo", kind=kind, status=r, notice=s.call("inspect").get("notice"))
    mp4 = os.path.join(OUT, "qa-export.mp4")
    if os.path.exists(mp4):
        d = s.call("apply", ops=[{"tool": "import_media", "args": {"paths": [mp4]}}])
        a = (res(d).get("assets") or [{}])[0]
        print("  reimportado", a)
        if abs(float(a.get("dur") or 0) - 8) > 0.5:
            s.issue("el MP4 exportado no dura 8 s", asset=a)
finally:
    s.close()
