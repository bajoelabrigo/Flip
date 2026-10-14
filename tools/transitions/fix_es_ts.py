"""Repair the four new MasksInspector entries in i18n/drift_es.ts.

An edit dropped the <message> opening tags around the two count strings and left the Cutout
entry unfinished. Rather than patch text by hand again, this finds each source string, ensures
it sits inside a well-formed <message> element with the wanted translation, and reports what it
changed. lupdate is run afterwards to normalise the file.
"""

import re
import sys

PATH = r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip\i18n\drift_es.ts"

WANTED = [
    ("1 mask on this clip", "1 máscara en este clip"),
    ("%1 masks on this clip", "%1 máscaras en este clip"),
    ("Cutout", "Recorte"),
    ("Edit this mask", "Editar esta máscara"),
    ("This clip has no mask yet. Add one from the Masks tab in the assets panel, "
     "or drop a mask onto the clip on the timeline.",
     "Este clip todavía no tiene máscara. Agrega una desde la pestaña Máscaras del panel de "
     "recursos, o arrastra una máscara sobre el clip en la línea de tiempo."),
]


def main():
    with open(PATH, encoding="utf-8") as fh:
        text = fh.read()

    for source, translation in WANTED:
        # Whatever mangled shape the entry is in, replace from the <source> line through the
        # closing </message> (or the <translation> if a </message> is missing) with a clean one.
        pattern = re.compile(
            r"(?s)(?:<message>\s*)?<source>" + re.escape(source) + r"</source>\s*"
            r"<translation[^>]*>.*?</translation>\s*(?:</message>)?")
        clean = (f"<message>\n        <source>{source}</source>\n"
                 f"        <translation>{translation}</translation>\n    </message>")
        new_text, n = pattern.subn(clean, text, count=1)
        if n == 0:
            print(f"NOT FOUND: {source[:50]}")
        else:
            text = new_text
            print(f"fixed: {source[:50]}")

    with open(PATH, "w", encoding="utf-8") as fh:
        fh.write(text)

    # A cheap structural check: every <message> must close.
    opens = text.count("<message>")
    closes = text.count("</message>")
    print(f"<message> {opens} / </message> {closes} -> {'OK' if opens == closes else 'DESBALANCE'}")
    return 0 if opens == closes else 1


if __name__ == "__main__":
    sys.exit(main())
