"""QA 0.18: máscaras, fotogramas clave, estabilizar, escenas, caras, profundidad, reencuadre, ruido y Whisper."""
import json
import time

from qa import Q, Session

s = Session("ai")
M = Q + r"\media"


def ap(tool, args, expect_ok=True, wait=600):
    d = s.call("apply", expect_ok=expect_ok, note=tool, wait=wait, ops=[{"tool": tool, "args": args}])
    done = d.get("done") or []
    return (done[0].get("result") or {}) if done else d


def until(label, probe, ok, limit=600):
    """Llama a probe() cada 2 s hasta que ok(resultado) o se acabe el tiempo."""
    t0 = time.time()
    r = probe()
    while not ok(r) and time.time() - t0 < limit:
        time.sleep(2)
        r = probe()
    n = s.call("inspect").get("notice")
    good = ok(r)
    print(f"  {label:16s} {'OK ' if good else 'NO '} {round(time.time() - t0, 1):6}s {json.dumps(r, ensure_ascii=False)[:220]} notice={n}")
    if not good:
        s.issue(f"{label}: no terminó", reply=r, notice=n)
    return r


def clip_detail(cid):
    return s.call("inspect", clip=cid)


try:
    ap("new_project", {"width": 1920, "height": 1080, "fps": 30})
    names = ["v_face.mp4", "v_shaky.mp4", "v_scenes.mp4", "a_voz.wav"]
    assets = ap("import_media", {"paths": [M + "\\" + n for n in names]})["assets"]
    ids = {n: a["id"] for n, a in zip(names, assets)}
    face = ap("place_clip", {"asset": ids["v_face.mp4"], "at": 0})["id"]
    shaky = ap("place_clip", {"asset": ids["v_shaky.mp4"], "at": 4})["id"]
    scenes = ap("place_clip", {"asset": ids["v_scenes.mp4"], "at": 8})["id"]
    voz = ap("place_clip", {"asset": ids["a_voz.wav"], "at": 0, "new_track": True})["id"]

    ap("set_mask", {"clip": shaky, "mask": {"shape": "ellipse", "feather": 0.1}})
    for t, v in ((4.0, 0.2), (6.0, 1.0)):
        ap("set_keyframe", {"clip": shaky, "prop": "opacity", "at": t, "value": v})
    k = ap("list_keyframes", {"clip": shaky, "prop": "opacity"})
    print("  claves", len(k.get("keys", [])))

    ap("stabilize_clip", {"clip": shaky})
    until("estabilizar", lambda: {k: v for k, v in clip_detail(shaky).items() if "stabil" in k.lower()} or clip_detail(shaky),
          lambda r: any(("ready" in str(k).lower() or "path" in str(k).lower()) and v for k, v in r.items()) or r.get("stabilize") == "done")

    ap("detect_scenes", {"clip": scenes})
    sc = until("escenas", lambda: ap("list_scenes", {"clip": scenes}, expect_ok=False),
               lambda r: bool(r.get("scenes") or r.get("shots")))
    print("  dividir escenas", json.dumps(ap("split_on_scenes", {"clip": scenes}, expect_ok=False))[:160])

    ap("detect_faces", {"clip": face})
    until("caras", lambda: ap("list_face_track", {"clip": face}, expect_ok=False),
          lambda r: bool(r.get("faces") or r.get("frames") or r.get("tracks") or r.get("n")))
    ap("add_effect", {"clip": face, "effect": "face_big_eyes"})

    dj = ap("estimate_depth", {"clip": face}).get("job_id")
    until("profundidad", lambda: ap("get_job", {"id": dj}, expect_ok=False),
          lambda r: r.get("state") in ("done", "finished", "succeeded", "complete") or r.get("progress") == 1)

    print("  reencuadre", json.dumps(ap("auto_reframe", {"clip": face, "aspect": 0.5625}, expect_ok=False))[:200])

    print("  quitar ruido", json.dumps(ap("apply_denoise", {"clip": voz}, expect_ok=False))[:200])
    until("ruido", lambda: ap("denoise_status", {}, expect_ok=False), lambda r: not r.get("busy") and not r.get("running"))

    print("  subtítulos", json.dumps(ap("generate_subtitles", {"clip": voz, "language": "es"}, expect_ok=False))[:200])

    def cues():
        insp = s.call("inspect", clips=True, cues=True)
        return {"cues": [c.get("text", "") for t in insp["tracks"] for x in t.get("items", [])
                         for c in (x.get("subtitleCues") or [])]}
    r = until("whisper", cues, lambda r: bool(r["cues"]), limit=900)
    print("  texto reconocido:", " / ".join(r["cues"]))
finally:
    s.close()
