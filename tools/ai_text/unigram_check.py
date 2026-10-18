"""Checks the simple Unigram tokenizer the app will use (NFKC, whitespace split, "▁" prefix,
Viterbi over the vocab scores, <s> ... </s>) against the HF tokenizer, and writes vocab.txt (one
"piece<TAB>score" a line, id = line number) for the extra."""
import json
import sys
import unicodedata
from pathlib import Path

from tokenizers import Tokenizer

here = Path(sys.argv[1])
tj = json.loads((here / "tokenizer.json").read_text(encoding="utf-8"))
vocab = tj["model"]["vocab"]
unk_id = tj["model"]["unk_id"]
pieces = {p: (i, s) for i, (p, s) in enumerate(vocab)}
max_len = max(len(p) for p, _ in vocab)
min_score = min(s for _, s in vocab)
UNK_SCORE = min_score - 10.0


def encode(text):
    text = unicodedata.normalize("NFKC", text)
    ids = [0]
    for word in text.split():
        w = "▁" + word
        n = len(w)
        best = [-1e30] * (n + 1)
        back = [None] * (n + 1)
        best[0] = 0.0
        for i in range(1, n + 1):
            for j in range(max(0, i - max_len), i):
                if best[j] <= -1e29:
                    continue
                piece = w[j:i]
                hit = pieces.get(piece)
                if hit is not None:
                    sc = best[j] + hit[1]
                    if sc > best[i]:
                        best[i], back[i] = sc, (j, hit[0])
                elif i - j == 1:
                    sc = best[j] + UNK_SCORE
                    if sc > best[i]:
                        best[i], back[i] = sc, (j, unk_id)
        out = []
        i = n
        while i > 0:
            j, pid = back[i]
            out.append(pid)
            i = j
        out.reverse()
        # Consecutive unknowns collapse into one, as SentencePiece does.
        merged = []
        for pid in out:
            if pid == unk_id and merged and merged[-1] == unk_id:
                continue
            merged.append(pid)
        ids.extend(merged)
    ids.append(2)
    return ids


hf = Tokenizer.from_file(str(here / "tokenizer.json"))
tests = ["mi rutina en el gimnasio", "Feliz Navidad familia", "título de terror", "GRAN OFERTA neón",
         "日本旅行の思い出", "Bonne année à tous", "Hochzeit im Sommer", "¡Suscríbete ya!", "estilo youtuber 100%",
         "fiesta de cumpleaños 🎉", "Réduction -50%", "Lo-fi chill vibes"]
bad = 0
for t in tests:
    a = encode(t)
    b = hf.encode(t).ids
    ok = a == b
    bad += not ok
    print("OK " if ok else "XX ", t, a if not ok else "", b if not ok else "")
print("mismatches:", bad)
with open(here / "vocab.txt", "w", encoding="utf-8", newline="\n") as f:
    for p, s in vocab:
        f.write(p.replace("\t", " ").replace("\n", " ") + "\t" + repr(float(s)) + "\n")
print("vocab.txt written", (here / "vocab.txt").stat().st_size)
