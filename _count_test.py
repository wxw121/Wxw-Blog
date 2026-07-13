import re
from pathlib import Path
HANZI = re.compile(r"[\u4e00-\u9fff]")
for n in range(188, 193):
    p = next(Path(".").glob(f"{n}.*.md"))
    t = p.read_text(encoding="utf-8")
    print(p.name, len(HANZI.findall(t)))
