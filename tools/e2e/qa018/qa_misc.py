"""QA 0.18: exportar con cada códec, audio, texto, stickers, formas, subtítulos y paquete."""
import json
import os
import subprocess
import time

from qa import OUT, Q, Session

s = Session("misc")
M = Q + r"\media"


def ap(tool, args, expect_ok=True, note="", wait=180):
    d = s.call("apply", expect_ok=expect_ok, note=note or tool, wait=wait, ops=[{"tool": tool, "args": args}])
    done = d.get("done") or []
    return (done[0].get("result") or {}) if done else d


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"err": r.stderr[:300]}


def wait_export():
    t0 = time.time()
    r = {}
    while time.time() - t0 < 600:
        r = ap("export_status", {})
        if not r.get("busy"):
            break
        time.sleep(1)
    return r, round(time.time() - t0, 1)


try:
    ap("new_project", {"width": 1920, "height": 1080, "fps": 30})
    ids = {os.path.basename(p): a["id"] for p, a in zip(
        [M + r"\v_h264_1080p30.mp4", M + r"\a_mp3.mp3"],
        ap("import_media", {"paths": [M + r"\v_h264_1080p30.mp4", M + r"\a_mp3.mp3"]})["assets"])}
    v = ap("place_clip", {"asset": ids["v_h264_1080p30.mp4"], "at": 0})["id"]
    a = ap("place_clip", {"asset": ids["a_mp3.mp3"], "at": 0, "new_track": True})["id"]

    # Texto, stickers, formas.
    txt = ap("add_text", {"text": "Hola QA", "at": 0, "preset": "title"})
    looks = ap("list_text_looks", {}).get("looks", [])
    for lk in looks:
        ap("apply_text_look", {"clip": txt.get("id"), "look": lk["id"]}, expect_ok=False, note="look " + lk["id"])
    anims = ap("list_text_animations", {}).get("presets", [])
    bad = 0
    for an in anims[:48]:
        r = ap("set_text_animation", {"clip": txt.get("id"), "which": "in", "preset": an["id"]}, expect_ok=False)
        if r.get("ok") is False:
            bad += 1
    print("animaciones de texto", len(anims), "fallidas", bad)
    st = ap("list_stickers", {}).get("stickers", [])
    for x in st[:: max(1, len(st) // 12)]:
        ap("add_sticker", {"sticker": x["id"], "at": 1}, note="sticker " + x["id"])
    for x in ap("list_shapes", {}).get("shapes", [])[:6]:
        ap("add_shape", {"shape": x["id"], "at": 2}, note="forma " + x["id"])
    cap = s.call("capture", at=2.5, full=True)
    print("captura con capas", cap.get("path"))

    # Audio.
    for tool, args in [("detect_beats", {"start": 0, "duration": 8}), ("detect_silence", {"clip": a}),
                       ("analyze_loudness", {"clip": a}), ("normalize_volume", {"clip": a}),
                       ("set_volume", {"clip": a, "value": 0.5}), ("audio_summary", {}),
                       ("get_waveform", {"clip": a, "buckets": 16})]:
        r = ap(tool, args, expect_ok=False, wait=300)
        print(" ", tool, json.dumps(r, ensure_ascii=False)[:200])

    # Subtítulos: crear, exportar SRT y volver a importar.
    sub = ap("add_subtitle_clip", {"at": 0}, expect_ok=False)
    print("  subtítulo", json.dumps(sub)[:200])
    if sub.get("id"):
        ap("set_subtitle_cues", {"clip": sub["id"], "cues": [
            {"start": 0.2, "end": 1.5, "text": "Primera línea ñ á"}, {"start": 1.6, "end": 3.0, "text": "Segunda"}]},
            expect_ok=False)
        srt = os.path.join(OUT, "qa.srt")
        r = ap("export_subtitle_file", {"clip": sub["id"], "path": srt}, expect_ok=False)
        print("  srt", r, open(srt, encoding="utf-8").read()[:120] if os.path.exists(srt) else "SIN ARCHIVO")
        if os.path.exists(srt):
            print("  import srt", json.dumps(ap("import_subtitle_file", {"path": srt}, expect_ok=False))[:200])

    # Exportar con cada combinación de video/audio que ofrece la app (2 s cada una).
    opts = ap("list_export_options", {})
    with open(os.path.join(OUT, "export-options.json"), "w", encoding="utf-8") as f:
        json.dump(opts, f, ensure_ascii=False, indent=1)
    vids = opts.get("video", [])
    print("códecs de video", [x.get("id") for x in vids])
    for vc in vids:
        ext = vc.get("ext") or vc.get("container") or "mp4"
        path = os.path.join(OUT, f"exp-{vc['id']}.{ext}")
        if os.path.exists(path):
            os.remove(path)
        r = ap("export_video", {"path": path, "video": vc["id"], "in": 0, "out": 2}, expect_ok=False, note=vc["id"])
        if r.get("ok") is False:
            s.issue("export_video rechazado", codec=vc["id"], reply=r)
            continue
        st_, secs = wait_export()
        info = probe(path) if os.path.exists(path) else None
        print(f"  {vc['id']:20s} {secs:6}s {st_.get('message')} {json.dumps(info)[:160] if info else 'SIN ARCHIVO'}")
        if not info or "streams" not in info:
            s.issue("exportación sin archivo válido", codec=vc["id"], status=st_)
    for ac in opts.get("audio", []):
        path = os.path.join(OUT, f"exp-audio-{ac['id']}")
        r = ap("export_video", {"path": path + ".m4a" if ac["id"] == "aac" else path + "." + {"opus": "ogg", "mp3": "mp3", "ac3": "ac3", "flac": "flac"}.get(ac["id"], "mka"),
                                "audio_only": True, "audio": ac["id"], "in": 0, "out": 2}, expect_ok=False, note="audio " + ac["id"])
        if r.get("ok") is False:
            print("  audio", ac["id"], "rechazado", json.dumps(r)[:200])
            continue
        st_, secs = wait_export()
        print("  audio", ac["id"], secs, st_.get("message"), r.get("path"))
    for preset in ("2160p", "4320p"):
        path = os.path.join(OUT, f"exp-{preset}.mp4")
        r = ap("export_video", {"path": path, "scale": preset, "in": 0, "out": 1}, expect_ok=False)
        st_, secs = wait_export()
        info = probe(path) if os.path.exists(path) else None
        print(f"  {preset} {secs}s {st_.get('message')} {json.dumps(info)[:220] if info else json.dumps(r)[:200]}")
finally:
    s.close()
