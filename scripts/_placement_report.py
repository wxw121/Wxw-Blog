# -*- coding: utf-8 -*-
import re, glob
from pathlib import Path

out = Path("_placement_report.txt")
lines = []
for f in sorted(glob.glob("[1-9]*.md")):
    if not re.match(r"^[1-9]", f):
        continue
    text = open(f, encoding="utf-8").read()
    lines.append(f"\n======== {f} ========\n")
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", text):
        pos = m.start()
        chain = []
        for hm in re.finditer(r"^(#{1,4})\s+(.+)$", text[:pos], re.M):
            lvl = len(hm.group(1))
            t = hm.group(2).strip()
            while chain and chain[-1][0] >= lvl:
                chain.pop()
            chain.append((lvl, t))
        sec = " > ".join(t for _, t in chain)
        fname = m.group(2).split("/")[-1]
        lines.append(f"{fname}\n  alt: {m.group(1)[:70]}\n  section: {sec}\n\n")
out.write_text("".join(lines), encoding="utf-8")
print("wrote", out)
