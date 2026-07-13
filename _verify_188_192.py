import re
from pathlib import Path

HANZI = re.compile(r"[\u4e00-\u9fff]")
FORBIDDEN = re.compile(
    r"实践要点|<!--\s*topup-batch|附录深化|复习打卡|工程备忘\s*\d+"
)
IMG = re.compile(r"image/([a-z0-9-]+)/")

FILES = [
    "188.secrets-management-rag-tutorial.md",
    "189.health-readiness-rag-tutorial.md",
    "190.structured-logging-rag-tutorial.md",
    "191.prometheus-metrics-rag-tutorial.md",
    "192.embedding-batch-cost-tutorial.md",
]
SLUGS = {
    "188.secrets-management-rag-tutorial.md": "secrets-management-rag",
    "189.health-readiness-rag-tutorial.md": "health-readiness-rag",
    "190.structured-logging-rag-tutorial.md": "structured-logging-rag",
    "191.prometheus-metrics-rag-tutorial.md": "prometheus-metrics-rag",
    "192.embedding-batch-cost-tutorial.md": "embedding-batch-cost",
}

print("| File | RM# | Hanzi | Images | Prompts | Padding | PASS |")
print("|------|-----|-------|--------|---------|---------|------|")
for fn in FILES:
    p = Path(fn)
    t = p.read_text(encoding="utf-8")
    rm = fn.split(".")[0]
    hz = len(HANZI.findall(t))
    slug = SLUGS[fn]
    imgs = len(re.findall(rf"image/{slug}/", t))
    prompts = len(list(Path(f"image/{slug}/prompts").glob("*.md")))
    pad = bool(FORBIDDEN.search(t))
    ok = hz >= 5000 and imgs == 3 and prompts == 3 and not pad
    print(f"| {fn} | {rm} | {hz} | {imgs} | {prompts} | {pad} | {'PASS' if ok else 'FAIL'} |")
