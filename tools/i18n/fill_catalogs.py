"""Bulk translation of the .ts catalogs: export what is unfinished, import what came back.

    python tools/i18n/fill_catalogs.py export <workdir> [--chunk 400]
    python tools/i18n/fill_catalogs.py import <workdir>

export writes <workdir>/<lang>/chunk_NN.json: [{id, context, source, es, numerus, forms}] for every
unfinished message (source and es unescaped), with the Spanish translation as a reference for the
meaning. Whoever translates writes <workdir>/<lang>/out_NN.json: {"<id>": "text" | ["form", ...]}.
import puts every answer back into i18n/drift_<lang>.ts (XML-escaped, unfinished mark removed) and
leaves anything missing as it was. Run lupdate twice afterwards: the files must come back unchanged.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
I18N = REPO / "i18n"

# Plural forms Qt uses per language (QLocale plural rules in Qt Linguist).
FORMS = {"ar": 6, "bn": 2, "fr_CA": 2, "it": 2, "ja": 1, "ko_KR": 1, "pl": 3, "pt_BR": 2, "pt_PT": 2,
         "ru": 3, "si": 2, "tl": 2, "vi": 1, "zh_Hans": 1, "es": 2, "es_CO": 2}

MESSAGE = re.compile(r'(<message(?: numerus="yes")?>)(.*?)(</message>)', re.S)
CONTEXT = re.compile(r'<context>\s*<name>(.*?)</name>(.*?)</context>', re.S)


def unescape(text: str) -> str:
    return html.unescape(text)


def escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def spanish_map() -> dict[tuple[str, str], str | list[str]]:
    s = (I18N / "drift_es.ts").read_text(encoding="utf-8")
    out = {}
    for ctx in CONTEXT.finditer(s):
        for m in MESSAGE.finditer(ctx.group(2)):
            body = m.group(2)
            src = re.search(r"<source>(.*?)</source>", body, re.S)
            if not src:
                continue
            forms = re.findall(r"<numerusform>(.*?)</numerusform>", body, re.S)
            tr = re.search(r"<translation[^>]*>(.*?)</translation>", body, re.S)
            value = [unescape(f) for f in forms] if forms else (unescape(tr.group(1)) if tr else "")
            out[(ctx.group(1), src.group(1))] = value
    return out


def export(work: Path, chunk: int) -> None:
    es = spanish_map()
    for ts in sorted(I18N.glob("drift_*.ts")):
        lang = ts.stem[len("drift_"):]
        if lang == "es":
            continue
        s = ts.read_text(encoding="utf-8")
        entries = []
        for ctx in CONTEXT.finditer(s):
            for m in MESSAGE.finditer(ctx.group(2)):
                body = m.group(2)
                if 'type="unfinished"' not in body:
                    continue
                src = re.search(r"<source>(.*?)</source>", body, re.S).group(1)
                comment = re.search(r"<comment>(.*?)</comment>", body, re.S)
                numerus = "numerus" in m.group(1)
                entries.append({"id": len(entries), "context": ctx.group(1), "source": unescape(src),
                                "comment": unescape(comment.group(1)) if comment else "",
                                "es": es.get((ctx.group(1), src), ""), "numerus": numerus,
                                "forms": FORMS.get(lang, 2) if numerus else 0})
        folder = work / lang
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("chunk_*.json"):
            old.unlink()
        for n in range(0, len(entries), chunk):
            (folder / f"chunk_{n // chunk:02d}.json").write_text(
                json.dumps(entries[n:n + chunk], ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"{lang}: {len(entries)} unfinished in {(len(entries) + chunk - 1) // chunk} chunks")


def placeholders(text: str) -> list[str]:
    return sorted(re.findall(r"%(?:n|L?\d+)", text))


def import_(work: Path) -> None:
    for folder in sorted(p for p in work.iterdir() if p.is_dir()):
        lang = folder.name
        ts = I18N / f"drift_{lang}.ts"
        if not ts.exists():
            continue
        answers: dict[int, str | list[str]] = {}
        for out in sorted(folder.glob("out_*.json")):
            chunk_no = out.stem.split("_")[1]
            entries = json.loads((folder / f"chunk_{chunk_no}.json").read_text(encoding="utf-8"))
            got = json.loads(out.read_text(encoding="utf-8"))
            for e in entries:
                v = got.get(str(e["id"]))
                if v is None:
                    continue
                answers[e["id"]] = (e, v)
        s = ts.read_text(encoding="utf-8")
        counter = {"i": 0, "done": 0, "bad": 0}

        def ctx_sub(cm):
            def msg_sub(m):
                body = m.group(2)
                if 'type="unfinished"' not in body:
                    return m.group(0)
                i = counter["i"]
                counter["i"] += 1
                if i not in answers:
                    return m.group(0)
                e, v = answers[i]
                if e["numerus"]:
                    forms = v if isinstance(v, list) else [v]
                    forms = (forms + [forms[-1]] * e["forms"])[:e["forms"]]
                    if any(placeholders(f) and "%n" not in f and "%n" in e["source"] for f in forms):
                        pass
                    new = "<translation>" + "".join(f"\n            <numerusform>{escape(f)}</numerusform>" for f in forms) + "\n        </translation>"
                else:
                    text = v[0] if isinstance(v, list) else v
                    if placeholders(text) != placeholders(e["source"]) or not text.strip():
                        counter["bad"] += 1
                        return m.group(0)
                    new = f"<translation>{escape(text)}</translation>"
                body = re.sub(r"<translation[^>]*>.*?</translation>", lambda _: new, body, count=1, flags=re.S)
                counter["done"] += 1
                return m.group(1) + body + m.group(3)
            return MESSAGE.sub(msg_sub, cm.group(0))

        s = CONTEXT.sub(ctx_sub, s)
        ts.write_text(s, encoding="utf-8", newline="")
        print(f"{lang}: {counter['done']} translated, {counter['bad']} rejected (placeholders), "
              f"{counter['i'] - counter['done']} left")


if __name__ == "__main__":
    work = Path(sys.argv[2])
    if sys.argv[1] == "export":
        export(work, int(sys.argv[sys.argv.index("--chunk") + 1]) if "--chunk" in sys.argv else 400)
    else:
        import_(work)
