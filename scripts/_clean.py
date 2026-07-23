import re
for fname in ["190.structured-logging-rag-tutorial.md", "191.prometheus-metrics-rag-tutorial.md", "192.embedding-batch-cost-tutorial.md"]:
    lines = open(fname, encoding="utf-8").read().splitlines()
    new = [ln for ln in lines if not re.match(r"^\s*实践要点\s*\d+\s*：", ln) and not re.match(r"^### 深读\s*\d+", ln)]
    text = "\n".join(new) + "\n"
    open(fname, "w", encoding="utf-8").write(text)
    h = len(re.findall(r"[\u4e00-\u9fff]", text))
    pad = bool(re.search(r"实践要点|### 深读", text))
    print(fname, h, pad, "PASS" if h >= 5000 and not pad else "FAIL")
