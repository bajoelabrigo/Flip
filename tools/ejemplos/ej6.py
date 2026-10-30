import json, os
S = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
M = S + "/m6"
c = []
def A(t, a, **k):
    c.append(dict(tool=t, args=a, **k))
R = lambda name: "$" + name

def text(name, words, at, dur, size, look=None, anim_in=None, anim_out=None, box=None, weight=900, spacing=8):
    A("add_text", {"text": words, "at": at}, remember={name: "id"})
    A("add_track", {"type": "text"})
    A("move_to_track", {"clip": R(name), "to_track": 0, "at": at})
    A("set_duration", {"clip": R(name), "duration": dur})
    A("set_text", {"clip": R(name), "style": {"pixelSize": size, "fontWeight": weight, "letterSpacing": spacing,
                                               "wordWrap": False}})
    if look:
        A("apply_text_look", {"clip": R(name), "look": look})
    if box:
        A("set_transform", {"clip": R(name), "x": box[0], "y": box[1], "w": box[2], "h": box[3]})
    if anim_in:
        A("set_text_animation", {"clip": R(name), "which": "in", "preset": anim_in})
    if anim_out:
        A("set_text_animation", {"clip": R(name), "which": "out", "preset": anim_out})

def shape(name, kind, at, dur, box, fill, anim, rotation=None, track=None):
    args = {"shape": kind, "at": at}
    A("add_shape", args, remember={name: "id"})
    A("add_track", {"type": "shape"})
    A("move_to_track", {"clip": R(name), "to_track": 0, "at": at})
    A("set_duration", {"clip": R(name), "duration": dur})
    tr = {"clip": R(name), "x": box[0], "y": box[1], "w": box[2], "h": box[3]}
    if rotation is not None:
        tr["rotation"] = rotation
    A("set_transform", tr)
    A("set_shape_style", {"clip": R(name), "style": {"fill": fill, "strokeWidth": 0}})
    A("set_animation", {"clip": R(name), "which": "animIn", "preset": anim})

A("set_project_setup", {"width": 1920, "height": 1080, "fps": 30})
A("set_metadata", {"title": "Intro para YouTube"})
A("import_media", {"paths": [f"{M}/tunel.mp4", f"{M}/whoosh.m4a", f"{M}/golpe.m4a", f"{M}/musica.m4a"]}, sleep=2)
A("place_clip", {"asset": 0, "at": 0, "track": 0}, remember={"fondo": "id"})
A("set_trim", {"clip": R("fondo"), "in": 0, "out": 6.5})
A("set_fade", {"clip": R("fondo"), "in": 0.3, "out": 0.6})
# The logo: a turquoise circle with a white play triangle, spinning in, then the channel's name.
shape("circulo", "circle", 0.4, 6.1, (810, 230, 300, 300), "#2ee6c8", "in-zoom-spin")
shape("play", "triangle", 1.0, 5.5, (905, 315, 130, 130), "#ffffff", "in-pop", rotation=90)
text("canal", "TU CANAL", 1.3, 5.2, 150, look="neon", anim_in="ibs-neon-strike", box=(360, 580, 1200, 190))
text("lema", "Nuevos videos cada semana", 2.2, 4.3, 54, look="shadow", anim_in="fade-up-char", box=(460, 790, 1000, 80),
     weight=500, spacing=4)
A("place_clip", {"asset": 1, "at": 0.25, "new_track": True}, remember={"wh": "id"})
A("place_clip", {"asset": 2, "at": 1.0, "new_track": True}, remember={"gp": "id"})
A("place_clip", {"asset": 3, "at": 0, "new_track": True}, remember={"mu": "id"})
A("set_trim", {"clip": R("mu"), "in": 0, "out": 6.5})
A("set_volume", {"clip": R("mu"), "value": 0.5})
A("set_fade", {"clip": R("mu"), "out": 1.0})
A("inspect", {"tracks": True, "clips": True}, save="insp.json")
A("package_project", {"path": f"{S}/ejemplo-6.flip"}, save="pack.json", sleep=6)
A("load_project", {"path": f"{S}/ejemplo-6.flip"}, sleep=3)
A("export_video", {"path": f"{S}/vista6.mp4", "video": "h264", "audio": "aac", "scale": "720p"}, sleep=35)
open(S + "/c_6.jsonl", "w", encoding="utf-8", newline="").write("\n".join(json.dumps(x, ensure_ascii=False) for x in c))
print(len(c))
