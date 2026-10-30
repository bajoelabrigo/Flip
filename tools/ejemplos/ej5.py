import json, os
S = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
M = S + "/m5"
c = []
def A(t, a, **k):
    c.append(dict(tool=t, args=a, **k))
R = lambda name: "$" + name

def text(name, words, at, dur, size, look=None, anim_in=None, anim_out=None, loop=None, box=None, weight=900):
    A("add_text", {"text": words, "at": at}, remember={name: "id"})
    A("add_track", {"type": "text"})
    A("move_to_track", {"clip": R(name), "to_track": 0, "at": at})
    A("set_duration", {"clip": R(name), "duration": dur})
    A("set_text", {"clip": R(name), "style": {"pixelSize": size, "fontWeight": weight, "letterSpacing": 4,
                                               "wordWrap": chr(10) in words or len(words) > 14}})
    if look:
        A("apply_text_look", {"clip": R(name), "look": look})
    if box:
        A("set_transform", {"clip": R(name), "x": box[0], "y": box[1], "w": box[2], "h": box[3]})
    if anim_in:
        A("set_text_animation", {"clip": R(name), "which": "in", "preset": anim_in})
    if anim_out:
        A("set_text_animation", {"clip": R(name), "which": "out", "preset": anim_out})
    if loop:
        A("set_text_animation", {"clip": R(name), "which": "loop", "preset": loop})

A("set_project_setup", {"width": 1080, "height": 1920, "fps": 30})
A("set_metadata", {"title": "Anuncio de producto"})
A("import_media", {"paths": [f"{M}/{n}.mp4" for n in ["granos", "hielo", "leche", "latte", "salpicon"]] + [f"{M}/musica.m4a"]}, sleep=2)
clips = [(0, 0.0, 0.1, 2.3), (1, 2.2, 0.2, 2.2), (2, 4.2, 0.2, 2.8), (3, 6.8, 0.2, 3.7), (4, 10.3, 0.2, 2.4)]
for i, (a, at, si, so) in enumerate(clips):
    A("place_clip", {"asset": a, "at": at, "track": 0}, remember={f"v{i}": "id"})
    A("set_trim", {"clip": R(f"v{i}"), "in": si, "out": so})
A("add_transition", {"track": 0, "index": 0, "kind": "slide_up"})
A("add_transition", {"track": 0, "index": 2, "kind": "radial_zoom_blur"})
A("place_clip", {"asset": 5, "at": 0, "new_track": True}, remember={"m": "id"})
A("set_trim", {"clip": R("m"), "in": 0, "out": 12.5})
A("set_fade", {"clip": R("m"), "out": 1.0})

text("nuevo", "NUEVO", 0.2, 3.8, 80, look="background", anim_in="pop", box=(340, 470, 400, 140))
text("nombre", "CAFÉ\nHELADO", 0.5, 3.7, 190, look="shadow", anim_in="ibs-slam-from-lens", anim_out="fade", box=(90, 640, 900, 470))
text("frase", "Frío, cremoso, recién hecho", 4.4, 2.4, 70, look="shadow", anim_in="typewriter", anim_out="fade",
     box=(90, 1500, 900, 120), weight=700)
# The offer: a red circle with -30% on the hero shot.
A("add_shape", {"shape": "circle", "at": 7.0}, remember={"oferta": "id"})
A("set_duration", {"clip": R("oferta"), "duration": 3.3})
A("set_transform", {"clip": R("oferta"), "x": 690, "y": 300, "w": 300, "h": 300})
A("set_shape_style", {"clip": R("oferta"), "style": {"fill": "#ff3b5c"}})
A("set_animation", {"clip": R("oferta"), "which": "animIn", "preset": "in-bounce"})
text("pct", "-30%", 7.15, 3.15, 96, anim_in="pop", box=(680, 385, 320, 130), weight=900)
text("hoy", "SOLO HOY", 7.4, 2.9, 90, look="outline", anim_in="slide-up", box=(90, 1450, 900, 130))
text("cta", "PIDE EL TUYO", 10.4, 2.1, 120, look="background", anim_in="pop", loop="pulse", box=(90, 880, 900, 170))
A("inspect", {"tracks": True, "clips": True}, save="insp.json")
A("package_project", {"path": f"{S}/ejemplo-5.flip"}, save="pack.json", sleep=6)
A("load_project", {"path": f"{S}/ejemplo-5.flip"}, sleep=3)
A("export_video", {"path": f"{S}/vista5.mp4", "video": "h264", "audio": "aac", "scale": "720p"}, sleep=40)
open(S + "/c_5.jsonl", "w", encoding="utf-8", newline="").write("\n".join(json.dumps(x, ensure_ascii=False) for x in c))
print(len(c))
