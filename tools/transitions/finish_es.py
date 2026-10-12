import re
p = r"C:\Users\bajoe\Downloads\Flip\i18n\drift_es.ts"
t = open(p, encoding="utf-8").read()
# An entry with text but still flagged unfinished is one lupdate could not confirm; the text is
# right, so finish it. Empty unfinished entries are left alone.
new, n = re.subn(r'<translation type="unfinished">([^<]+)</translation>',
                 r'<translation>\1</translation>', t)
open(p, "w", encoding="utf-8").write(new)
left = len(re.findall(r'<translation type="unfinished">\s*</translation>', new))
print(f"marcadas como terminadas: {n}; vacias que quedan: {left}")
