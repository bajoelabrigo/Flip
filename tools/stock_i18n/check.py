"""Quality report of tools/stock_i18n/<lang>.json: names duplicated where English differs, tag counts outside 3-6,
names identical to English, names without the language's script, brand words, upper-case tags.

    py tools/stock_i18n/check.py
"""
import collections
import re
import sys

from common import LANGS, load_sources, load_translations
sys.stdout.reconfigure(encoding="utf-8")
items, cats = load_sources()
src = {i["key"]: i for i in items}
SCRIPT = {"ar": r"[\u0600-\u06FF]", "bn": r"[\u0980-\u09FF]", "ja": r"[\u3040-\u30FF\u4E00-\u9FFF]",
          "ko": r"[\uAC00-\uD7AF]", "ru": r"[\u0400-\u04FF]", "si": r"[\u0D80-\u0DFF]", "zh": r"[\u4E00-\u9FFF]"}
BRANDS = re.compile(r"polaroid|tiktok|instagram|whatsapp|youtube|nike|adidas|converse|coca|disney|marvel|lego|netflix|iphone|spotify", re.I)
for lang in LANGS:
    tr = load_translations(lang)["items"]
    dup = collections.defaultdict(list)
    for k, v in tr.items():
        dup[(k.split(":")[0], v["name"].lower())].append(k)
    dups = [(n, ks) for (t, n), ks in dup.items() if len(ks) > 1]
    # duplicates also duplicated in English are fine
    real = [(n, ks) for n, ks in dups if len({src[k]["en"].lower() for k in ks}) > 1]
    badtags = [k for k, v in tr.items() if not 3 <= len(v["tags"]) <= 6]
    same_en = [k for k, v in tr.items() if v["name"].lower() == src[k]["en"].lower() and len(v["name"]) > 4]
    noscript = [k for k, v in tr.items() if lang in SCRIPT and not re.search(SCRIPT[lang], v["name"])]
    brands = [(k, v["name"], v["tags"]) for k, v in tr.items() if BRANDS.search(v["name"] + " " + " ".join(v["tags"]))]
    upper = [k for k, v in tr.items() if any(t != t.lower() for t in v["tags"])]
    print(f"== {lang}: dups {len(real)} badtags {len(badtags)} same-as-en {len(same_en)} wrong-script {len(noscript)} brands {len(brands)} upper {len(upper)}")
    for n, ks in real[:8]: print("   dup", n, ks)
    for k in same_en[:8]: print("   en", k, tr[k]["name"])
    for k in noscript[:8]: print("   script", k, tr[k]["name"])
    for b in brands[:6]: print("   brand", b)
    for k in badtags[:4]: print("   tags", k, tr[k]["tags"])

