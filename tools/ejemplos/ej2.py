import json, os
S = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
M = S + "/m2"
c = []
def A(t, a, **k):
    c.append(dict(tool=t, args=a, **k))
R = lambda name: "$" + name

A("set_project_setup", {"width": 1920, "height": 1080, "fps": 30})
A("set_metadata", {"title": "Vlog de viaje"})
A("import_media", {"paths": [f"{M}/{n}.mp4" for n in ["costa", "carretera", "cascada", "globos", "lago"]] + [f"{M}/musica.m4a"]}, sleep=2)
clips = [(0, 0, 0.2, 4.2, 1), (1, 4, 0.2, 4.2, 1), (2, 8, 0, 2.0, 0.5), (3, 12, 0.3, 4.3, 1), (4, 16, 0.5, 5.5, 1)]
for i, (a, at, si, so, sp) in enumerate(clips):
    A("place_clip", {"asset": a, "at": at, "track": 0}, remember={f"v{i}": "id"})
    if sp != 1:
        A("set_clip_speed", {"clip": R(f"v{i}"), "speed": sp})
    A("set_trim", {"clip": R(f"v{i}"), "in": si, "out": so})
    A("add_effect", {"clip": R(f"v{i}"), "effect": "cinematic_grade"})
for i in range(4):
    A("add_transition", {"track": 0, "index": i, "kind": "crossfade"})
A("place_clip", {"asset": 5, "at": 0, "new_track": True}, remember={"m": "id"})
A("set_trim", {"clip": R("m"), "in": 0, "out": 21})
A("set_fade", {"clip": R("m"), "in": 1, "out": 2.5})

def lower(at, dur, big, small, tag):
    b, t, s = "b" + tag, "t" + tag, "s" + tag
    A("add_shape", {"shape": "rectangle", "at": at}, remember={b: "id"})
    A("set_duration", {"clip": R(b), "duration": dur})
    A("set_transform", {"clip": R(b), "x": 110, "y": 800, "w": 10, "h": 140})
    A("set_shape_style", {"clip": R(b), "style": {"layer": {"id": "fill", "color": "#2ee6c8"}, "fill": "#2ee6c8"}})
    A("add_text", {"text": big, "at": at + 0.15}, remember={t: "id"})
    A("set_duration", {"clip": R(t), "duration": dur - 0.15})
    A("set_text", {"clip": R(t), "style": {"pixelSize": 72, "fontWeight": 800, "align": "left", "letterSpacing": 4,
                                            "shadowEnabled": True, "shadowBlur": 12, "shadowOpacity": 0.5}})
    A("set_transform", {"clip": R(t), "x": 140, "y": 790, "w": 1200, "h": 90})
    A("set_text_animation", {"clip": R(t), "which": "in", "preset": "slide-right"})
    A("set_text_animation", {"clip": R(t), "which": "out", "preset": "fade"})
    A("add_text", {"text": small, "at": at + 0.4}, remember={s: "id"})
    # Its own text track: on the big line's track it was pushed after it.
    A("add_track", {"type": "text"})
    A("move_to_track", {"clip": R(s), "to_track": 0, "at": at + 0.4})
    A("set_duration", {"clip": R(s), "duration": dur - 0.4})
    A("set_text", {"clip": R(s), "style": {"pixelSize": 40, "fontWeight": 400, "align": "left",
                                            "shadowEnabled": True, "shadowBlur": 10, "shadowOpacity": 0.5}})
    A("set_transform", {"clip": R(s), "x": 142, "y": 880, "w": 1200, "h": 60})
    A("set_text_animation", {"clip": R(s), "which": "in", "preset": "fade-up-char"})
    A("set_text_animation", {"clip": R(s), "which": "out", "preset": "fade"})

lower(0.8, 3.0, "COSTA TURQUESA", "Día 1 de mi viaje", "1")
lower(12.4, 3.1, "GLOBOS AL AMANECER", "Día 3 · antes de que salga el sol", "2")
A("add_text", {"text": "HASTA LA PRÓXIMA", "at": 17.5}, remember={"fin": "id"})
A("set_duration", {"clip": R("fin"), "duration": 3.5})
A("set_text", {"clip": R("fin"), "style": {"pixelSize": 110, "fontWeight": 800, "letterSpacing": 10}})
A("apply_text_look", {"clip": R("fin"), "look": "shadow"})
A("set_text_animation", {"clip": R("fin"), "which": "in", "preset": "fade-up-char"})
A("inspect", {"tracks": True, "clips": True}, save="insp.json")
A("package_project", {"path": f"{S}/ejemplo-2.flip"}, save="pack.json", sleep=8)
A("load_project", {"path": f"{S}/ejemplo-2.flip"}, sleep=3)
A("export_video", {"path": f"{S}/vista2.mp4", "video": "h264", "audio": "aac", "scale": "720p"}, sleep=50)
open(S + "/c_2.jsonl", "w", encoding="utf-8", newline="").write("\n".join(json.dumps(x, ensure_ascii=False) for x in c))
print(len(c))
