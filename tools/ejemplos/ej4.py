import json, os, glob
S = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
M = S + "/m4"
c = []
def A(t, a, **k):
    c.append(dict(tool=t, args=a, **k))
R = lambda name: "$" + name

photos = sorted(glob.glob(M + "/*.jpg"))
# Every 4 beats of the song (129 BPM): the photos change on the beat.
cuts = [0.0, 1.985, 3.843, 5.7, 7.558, 9.416, 11.273, 13.131, 14.988]
W, H = 1080, 1920
A("set_project_setup", {"width": W, "height": H, "fps": 30})
A("set_metadata", {"title": "Fotos con música"})
A("import_media", {"paths": [p.replace('\\', '/') for p in photos] + [M + "/musica.m4a"]}, sleep=2)
for i in range(8):
    at, end = cuts[i], cuts[i + 1]
    A("place_clip", {"asset": i, "at": at, "track": 0}, remember={f"p{i}": "id"})
    A("set_duration", {"clip": R(f"p{i}"), "duration": round(end - at, 3)})
    # A slow zoom, in on one photo and out on the next.
    big = (1.18 * W, 1.18 * H)
    a, b = ((W, H), big) if i % 2 == 0 else (big, (W, H))
    for t, (w, h) in ((at, a), (end - 0.02, b)):
        A("set_keyframe", {"clip": R(f"p{i}"), "prop": "width", "at": t, "value": w})
        A("set_keyframe", {"clip": R(f"p{i}"), "prop": "height", "at": t, "value": h})
        A("set_keyframe", {"clip": R(f"p{i}"), "prop": "x", "at": t, "value": (W - w) / 2})
        A("set_keyframe", {"clip": R(f"p{i}"), "prop": "y", "at": t, "value": (H - h) / 2})
A("add_transition", {"track": 0, "index": 3, "kind": "zoom_in"})
A("place_clip", {"asset": 8, "at": 0, "new_track": True}, remember={"m": "id"})
A("set_trim", {"clip": R("m"), "in": 0, "out": 15.2})
A("set_fade", {"clip": R("m"), "out": 1.2})
A("add_text", {"text": "¡FELIZ CUMPLE!", "at": 0.2}, remember={"t1": "id"})
A("set_duration", {"clip": R("t1"), "duration": 3.4})
A("set_text", {"clip": R("t1"), "style": {"pixelSize": 150, "fontWeight": 900}})
A("apply_text_look", {"clip": R("t1"), "look": "outline"})
A("set_text_animation", {"clip": R("t1"), "which": "in", "preset": "ibs-comic-pop"})
A("set_text_animation", {"clip": R("t1"), "which": "out", "preset": "zoom-out"})
A("add_text", {"text": "¡QUE CUMPLAS\nMUCHOS MÁS!", "at": 11.4}, remember={"t2": "id"})
A("set_duration", {"clip": R("t2"), "duration": 3.6})
A("set_text", {"clip": R("t2"), "style": {"pixelSize": 120, "fontWeight": 900}})
A("apply_text_look", {"clip": R("t2"), "look": "outline"})
A("set_text_animation", {"clip": R("t2"), "which": "in", "preset": "ibs-pancake-pop"})
A("set_text_animation", {"clip": R("t2"), "which": "loop", "preset": "pulse"})
# Shapes of the app (stars and hearts in party colours) that pop in on the beat.
for shape, colour, at, x, y in (("star", "#ffd23f", 2.0, 110, 250), ("heart", "#ff4d8d", 5.7, 760, 1480),
                                ("star", "#2ee6c8", 9.4, 110, 1480), ("heart", "#ffd23f", 13.1, 770, 250)):
    A("add_shape", {"shape": shape, "at": at}, remember={"e": "id"})
    A("set_duration", {"clip": R("e"), "duration": 1.85})
    A("set_transform", {"clip": R("e"), "x": x, "y": y, "w": 200, "h": 200})
    A("set_shape_style", {"clip": R("e"), "style": {"fill": colour}})
    A("set_animation", {"clip": R("e"), "which": "animIn", "preset": "in-pop"})
A("inspect", {"tracks": True, "clips": True}, save="insp.json")
A("package_project", {"path": f"{S}/ejemplo-4.flip"}, save="pack.json", sleep=6)
A("load_project", {"path": f"{S}/ejemplo-4.flip"}, sleep=3)
A("export_video", {"path": f"{S}/vista4.mp4", "video": "h264", "audio": "aac", "scale": "720p"}, sleep=45)
open(S + "/c_4.jsonl", "w", encoding="utf-8", newline="").write("\n".join(json.dumps(x, ensure_ascii=False) for x in c))
print(len(c))
