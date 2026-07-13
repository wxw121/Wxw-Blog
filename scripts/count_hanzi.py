import re, sys
from pathlib import Path
t = Path(sys.argv[1]).read_text(encoding="utf-8")
print(len(re.findall(r"[\u4e00-\u9fff]", t)))
