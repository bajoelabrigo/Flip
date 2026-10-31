import json, sys
d = json.load(open(f"lt_ref/{sys.argv[1]}.json"))
bands = sys.argv[2].split(",")
kinds = sys.argv[3].split(",") if len(sys.argv) > 3 else ["warm", "white"]
prev = None
for i, f in enumerate(d["frames"]):
    row = " | ".join(f"{b}:" + " ".join(f"{k[0]}{f[b][k]}" for k in kinds) for b in bands)
    if row != prev:
        print(i, row)
    prev = row
