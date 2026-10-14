import json, os, glob
root = r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip\transitions"
bad = []
ids = {}
for d in sorted(os.listdir(root)):
    j = os.path.join(root, d, "transition.json")
    f = os.path.join(root, d, "main.frag")
    if not os.path.isfile(j):
        bad.append(f"{d}: no transition.json"); continue
    if not os.path.isfile(f):
        bad.append(f"{d}: no main.frag"); continue
    try:
        m = json.load(open(j, encoding="utf-8"))
    except Exception as e:
        bad.append(f"{d}: {e}"); continue
    for k in ("id", "displayName", "category", "order", "pipeline"):
        if k not in m: bad.append(f"{d}: missing {k}")
    if m["id"] in ids: bad.append(f"duplicate id {m['id']} ({d} and {ids[m['id']]})")
    ids[m["id"]] = d
    # every declared parameter must be a uniform in the shader
    shader = open(f, encoding="utf-8").read()
    for p in m.get("parameters", []):
        if f"uniform float {p['identifier']}" not in shader and f"uniform int {p['identifier']}" not in shader:
            bad.append(f"{d}: parameter {p['identifier']} is not a uniform in main.frag")
print(f"{len(ids)} transitions")
cats = {}
for d in os.listdir(root):
    j = os.path.join(root, d, "transition.json")
    if os.path.isfile(j):
        c = json.load(open(j, encoding="utf-8"))["category"]
        cats[c] = cats.get(c, 0) + 1
print("por categoria:", dict(sorted(cats.items())))
if bad:
    print("PROBLEMAS:")
    for b in bad: print("  ", b)
else:
    print("todo OK")
