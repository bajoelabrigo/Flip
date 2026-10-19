"""QA 0.18: aplicar cada efecto y cada transición del catálogo y comprobar que se dibujan."""
import json
import os

from PIL import Image, ImageStat

from qa import OUT, Q, Session

s = Session("render")
VID = Q + r"\media\v_h264_1080p30.mp4"


def ap(tool, args, expect_ok=True, note=""):
    d = s.call("apply", expect_ok=expect_ok, note=note, ops=[{"tool": tool, "args": args}])
    done = d.get("done") or []
    return (done[0].get("result") or {}) if done else d


def stats(path):
    im = Image.open(path).convert("L")
    st = ImageStat.Stat(im)
    return round(st.mean[0], 1), round(st.stddev[0], 1)


rows = []
try:
    ap("new_project", {"width": 1280, "height": 720, "fps": 30})
    aid = ap("import_media", {"paths": [VID]})["assets"][0]["id"]
    a = ap("place_clip", {"asset": aid, "at": 0})["id"]
    b = ap("place_clip", {"asset": aid, "at": 6})["id"]
    base = stats(s.call("capture", at=2.0, full=True)["path"])
    print("base", base)

    effects = [dict(e, cat=c) for c, es in ap("list_effects", {}).get("cats", {}).items() for e in es]
    print("efectos", len(effects))
    for e in effects:
        r = ap("add_effect", {"clip": a, "effect": e["id"]}, expect_ok=False)
        if r.get("ok") is False or "index" not in r:
            rows.append({"kind": "effect", "id": e["id"], "add": r})
            s.issue("add_effect falló", effect=e["id"], reply=r)
            continue
        cap = s.call("capture", at=2.0, full=True)
        st = stats(cap["path"]) if cap.get("path") else None
        n = s.call("inspect").get("notice")
        rows.append({"kind": "effect", "id": e["id"], "cat": e.get("cat"), "stats": st, "notice": n})
        if st is None or (st[0] < 3 and st[1] < 2):
            s.issue("efecto deja la imagen negra o sin captura", effect=e["id"], stats=st, notice=n)
        ap("remove_effect", {"clip": a, "index": r["index"]}, expect_ok=False)

    trans = [dict(t, cat=c) for c, ts in ap("list_transitions", {}).get("cats", {}).items() for t in ts]
    print("transiciones", len(trans))
    for t in trans:
        r = ap("add_transition", {"clip": a, "kind": t["id"], "duration": 1.0}, expect_ok=False)
        if r.get("ok") is False:
            rows.append({"kind": "transition", "id": t["id"], "add": r})
            s.issue("add_transition falló", transition=t["id"], reply=r)
            continue
        cap = s.call("capture", at=6.0, full=True)
        st = stats(cap["path"]) if cap.get("path") else None
        rows.append({"kind": "transition", "id": t["id"], "stats": st})
        if st is None or (st[0] < 3 and st[1] < 2):
            s.issue("transición deja la imagen negra o sin captura", transition=t["id"], stats=st)
finally:
    with open(os.path.join(OUT, "render-rows.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    s.close()
