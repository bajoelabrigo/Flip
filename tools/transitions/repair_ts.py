"""Repair any <message> whose opening tag went missing, in any i18n/*.ts.

A regex edit in this session dropped <message> openers. Rather than reconstruct them by hand,
this walks each catalog line by line: whenever a <source> line appears outside a message element,
it inserts the <message> that should have preceded it, and it closes any message left open before
the next <source> or the end of the context.
"""

import glob
import os
import re
import sys

ROOT = r"C:\Users\bajoe\Downloads\Flip\i18n"


def repair(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()

    out = []
    in_message = False
    fixed_inserts = 0
    fixed_closes = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("<message>"):
            # A new message while one is open means the previous one never closed.
            if in_message:
                out.append("    </message>\n")
                fixed_closes += 1
            in_message = True
            out.append(line)
            continue

        if stripped.startswith("<source>"):
            # A source with no open message: the opener was lost.
            if not in_message:
                indent = line[:len(line) - len(line.lstrip())]
                out.append(f"{indent}<message>\n")
                fixed_inserts += 1
                in_message = True
            out.append(line)
            continue

        if stripped.startswith("</message>"):
            out.append(line)
            in_message = False
            continue

        # A context boundary closes anything still open.
        if stripped.startswith("<context>") or stripped.startswith("</context>"):
            if in_message:
                out.append("    </message>\n")
                fixed_closes += 1
                in_message = False
            out.append(line)
            continue

        if stripped.startswith("</TS>"):
            if in_message:
                out.append("    </message>\n")
                fixed_closes += 1
                in_message = False
            out.append(line)
            continue

        out.append(line)

    if in_message:
        out.append("    </message>\n")
        fixed_closes += 1

    text = "".join(out)
    opens = text.count("<message>")
    closes = text.count("</message>")
    changed = fixed_inserts or fixed_closes
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(f"{os.path.basename(path):24} openers+{fixed_inserts} closers+{fixed_closes} "
          f"-> {opens}/{closes} {'OK' if opens == closes else 'DESBALANCE'}")
    return opens == closes


def main():
    ok = True
    for path in sorted(glob.glob(os.path.join(ROOT, "drift*.ts"))):
        ok = repair(path) and ok
    print("todos balanceados" if ok else "QUEDAN DESBALANCES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
