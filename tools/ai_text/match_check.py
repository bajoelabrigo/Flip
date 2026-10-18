"""How the AI text would pick among the app's real text presets (labels from list_text_presets),
with the same description the app builds (label — category — sample) and the same model."""
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

here = Path(sys.argv[1])
reply = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
presets = json.loads(reply["result"]["content"][0]["text"])["presets"]
tok = Tokenizer.from_file(str(here / "tokenizer.json"))
sess = ort.InferenceSession(str(here / "model.onnx"), providers=["CPUExecutionProvider"])
names = [i.name for i in sess.get_inputs()]


def embed(text):
    ids = tok.encode(text).ids
    feed = {}
    for n in names:
        if n == "attention_mask":
            feed[n] = np.ones((1, len(ids)), np.int64)
        elif n == "token_type_ids":
            feed[n] = np.zeros((1, len(ids)), np.int64)
        else:
            feed[n] = np.array([ids], np.int64)
    out = sess.run(None, feed)[0][0].mean(axis=0)
    return out / np.linalg.norm(out)


hints = json.loads((here.parent / "hints.json").read_text(encoding="utf-8"))
descs = []
for p in presets:
    parts = [p.get("label", ""), hints.get(p["id"], ""), p.get("category", "")]
    descs.append(" — ".join(x for x in parts if x))
vecs = [embed(d) for d in descs]
print(len(presets), "presets:", ", ".join(p["label"] for p in presets))
for idea in ["título de terror", "gran oferta neón", "boda elegante", "subtítulos para tiktok", "horror movie title",
             "cumpleaños divertido", "youtube intro épica", "precio de producto", "cita bíblica", "minimalista"]:
    q = embed(idea)
    scores = [float(q @ v) for v in vecs]
    best = int(np.argmax(scores))
    print(f"{idea!r:28} -> {presets[best]['label']} ({scores[best]:.2f})")
