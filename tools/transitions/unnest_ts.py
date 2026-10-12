"""Remove the nested <message> tags a previous repair inserted.

The catalog format is:

    <message numerus="yes">
        <source>...</source>
        <translation>...</translation>
    </message>

A bad repair put a bare <message> between the opener (with its attributes) and the <source>.
This deletes any <message> line that directly follows an opening message tag, leaving the
attributed opener intact.
"""

import glob
import os
import re
import sys

ROOT = r"C:\Users\bajoe\Downloads\Flip\i18n"

# An opening message tag, with or without attributes.
OPENER = re.compile(r"^\s*<message(\s[^>]*)?>\s*$")


def repair(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()

    out = []
    removed = 0
    previous_was_opener = False

    for line in lines:
        is_plain_message = line.strip() == "<message>"
        if is_plain_message and previous_was_opener:
            removed += 1
            continue
        out.append(line)
        previous_was_opener = bool(OPENER.match(line))

    text = "".join(out)
    opens = len(re.findall(r"<message(\s[^>]*)?>", text))
    closes = text.count("</message>")
    if removed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    status = "OK" if opens == closes else "DESBALANCE"
    print(f"{os.path.basename(path):24} removed {removed:3} -> {opens}/{closes} {status}")
    return opens == closes


def main():
    ok = True
    for path in sorted(glob.glob(os.path.join(ROOT, "drift*.ts"))):
        ok = repair(path) and ok
    print("todos balanceados" if ok else "QUEDAN DESBALANCES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
