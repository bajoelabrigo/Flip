"""Unfinished UI strings of one or more .ts catalogs, for translating in batches (agents or people).

    py tools/i18n/ui_todo.py export <lang> [<lang> ...]   -> work/ui_i18n/todo/<lang>.json
    py tools/i18n/ui_todo.py apply  <lang> [<lang> ...]   <- work/ui_i18n/done/<lang>.json

A todo file is a list of {"key", "context", "source", "comment", "es"}: "es" is the Spanish
translation, as a reference for meaning and tone. A done file maps each "key" to its translation.
`apply` checks that every %1/%2… placeholder and every \\n survives, writes only finished entries,
and leaves the rest unfinished. Run lupdate afterwards (and again, to check it changes nothing):
see CLAUDE.md, «Comprobar los catálogos».
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "i18n"
WORK = ROOT / "work" / "ui_i18n"

MSG = re.compile(r"<message>(.*?)</message>", re.S)
CTX = re.compile(r"<context>\s*<name>(.*?)</name>(.*?)</context>", re.S)


def unxml(t):
    return (t.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")
            .replace("&amp;", "&"))


def xml(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def key_of(ctx, src, comment):
    return hashlib.sha1(f"{ctx}\x00{src}\x00{comment}".encode("utf-8")).hexdigest()[:12]


def entries(ts_text):
    for name, body in CTX.findall(ts_text):
        for m in MSG.finditer(body):
            msg = m.group(1)
            src = re.search(r"<source>(.*?)</source>", msg, re.S)
            if not src:
                continue
            com = re.search(r"<comment>(.*?)</comment>", msg, re.S)
            tr = re.search(r"<translation([^>]*)>(.*?)</translation>", msg, re.S)
            yield name, unxml(src.group(1)), unxml(com.group(1)) if com else "", tr


def spanish():
    out = {}
    for ctx, src, com, tr in entries((I18N / "drift_es.ts").read_text(encoding="utf-8")):
        if tr and "unfinished" not in tr.group(1):
            out[key_of(ctx, src, com)] = unxml(tr.group(2))
    return out


def export(lang):
    es = spanish()
    todo = []
    for ctx, src, com, tr in entries((I18N / f"drift_{lang}.ts").read_text(encoding="utf-8")):
        if tr and "unfinished" in tr.group(1):
            k = key_of(ctx, src, com)
            todo.append({"key": k, "context": ctx, "source": src, "comment": com, "es": es.get(k, "")})
    (WORK / "todo").mkdir(parents=True, exist_ok=True)
    (WORK / "todo" / f"{lang}.json").write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(lang, len(todo), "to translate")


PLACE = re.compile(r"%L?\d+|\\n|\n")


def apply(lang):
    done = json.loads((WORK / "done" / f"{lang}.json").read_text(encoding="utf-8"))
    path = I18N / f"drift_{lang}.ts"
    text = path.read_text(encoding="utf-8")
    applied = rejected = 0

    def fix_ctx(cm):
        nonlocal applied, rejected
        name, body = cm.group(1), cm.group(2)

        def fix_msg(mm):
            nonlocal applied, rejected
            msg = mm.group(0)
            if 'type="unfinished"' not in msg:
                return msg
            src = unxml(re.search(r"<source>(.*?)</source>", msg, re.S).group(1))
            com = re.search(r"<comment>(.*?)</comment>", msg, re.S)
            k = key_of(name, src, unxml(com.group(1)) if com else "")
            t = done.get(k)
            if not t:
                return msg
            if sorted(PLACE.findall(src)) != sorted(PLACE.findall(t)):
                rejected += 1
                print("placeholders differ:", lang, k, repr(src)[:60])
                return msg
            applied += 1
            tr = re.search(r"<translation[^>]*>.*?</translation>", msg, re.S).group(0)
            return msg.replace(tr, "<translation>" + xml(t) + "</translation>")

        return cm.group(0).replace(body, MSG.sub(fix_msg, body))

    text = CTX.sub(fix_ctx, text)
    path.write_text(text, encoding="utf-8", newline="")
    print(lang, "applied", applied, "rejected", rejected, "left", text.count('type="unfinished"'))


if __name__ == "__main__":
    cmd, langs = sys.argv[1], sys.argv[2:]
    for lang in langs:
        export(lang) if cmd == "export" else apply(lang)
