import json, os
S = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
M = S + "/m3"
c = []
def A(t, a, **k):
    c.append(dict(tool=t, args=a, **k))
R = lambda name: "$" + name

A("set_project_setup", {"width": 1080, "height": 1920, "fps": 30})
A("set_metadata", {"title": "Voz y subtítulos"})
A("import_media", {"paths": [f"{M}/{n}.mp4" for n in ["pulpo", "medusas", "arrecife", "rosa", "cardumen"]]
                   + [f"{M}/voz.m4a", f"{M}/musica.m4a"]}, sleep=2)
# (asset, at, in, out, speed): each shot follows what the voice says.
clips = [(0, 0.0, 0.0, 2.5, 1), (1, 2.5, 0.5, 2.4, 1), (2, 4.4, 0.2, 2.6, 1), (3, 6.8, 0.0, 6.0, 3), (4, 8.8, 0.0, 2.7, 1)]
for i, (a, at, si, so, sp) in enumerate(clips):
    A("place_clip", {"asset": a, "at": at, "track": 0}, remember={f"v{i}": "id"})
    if sp != 1:
        A("set_clip_speed", {"clip": R(f"v{i}"), "speed": sp})
    A("set_trim", {"clip": R(f"v{i}"), "in": si, "out": so})
A("add_transition", {"track": 0, "index": 3, "kind": "crossfade"})
A("place_clip", {"asset": 5, "at": 0.15, "new_track": True}, remember={"voz": "id"})
A("place_clip", {"asset": 6, "at": 0, "new_track": True}, remember={"mus": "id"})
A("set_trim", {"clip": R("mus"), "in": 0, "out": 11.5})
A("set_volume", {"clip": R("mus"), "value": 0.18})
A("set_fade", {"clip": R("mus"), "in": 0.5, "out": 1.5})
A("add_text", {"text": "DATO CURIOSO", "at": 0}, remember={"tit": "id"})
A("set_duration", {"clip": R("tit"), "duration": 11.5})
A("set_text", {"clip": R("tit"), "style": {"pixelSize": 70, "fontWeight": 900, "letterSpacing": 6}})
A("apply_text_look", {"clip": R("tit"), "look": "background"})
A("set_transform", {"clip": R("tit"), "x": 240, "y": 220, "w": 600, "h": 110})
A("set_text_animation", {"clip": R("tit"), "which": "in", "preset": "pop"})
A("generate_subtitles", {"clips": [R("voz")], "language": "es", "max_words_per_cue": 3}, sleep=70)
A("apply_text_preset", {"track": 0, "index": 0, "preset": "karaoke-pop"})
A("set_text", {"track": 0, "index": 0, "style": {"pixelSize": 96}})
A("inspect", {"tracks": True, "clips": True}, save="insp.json")
A("package_project", {"path": f"{S}/ejemplo-3.flip"}, save="pack.json", sleep=8)
A("load_project", {"path": f"{S}/ejemplo-3.flip"}, sleep=3)
A("export_video", {"path": f"{S}/vista3.mp4", "video": "h264", "audio": "aac", "scale": "720p"}, sleep=45)
open(S + "/c_3a.jsonl", "w", encoding="utf-8", newline="").write("\n".join(json.dumps(x, ensure_ascii=False) for x in c))
print(len(c))
