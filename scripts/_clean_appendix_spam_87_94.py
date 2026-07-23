# -*- coding: utf-8 -*-
"""Remove duplicate ## 附录 / ## 专精 / misplaced ### 1.2 blocks after summary."""
import re
from pathlib import Path

FILES = [
    "87.ann-recall-latency-tutorial.md",
    "88.metadata-filter-retrieval-tutorial.md",
    "89.multi-tenant-namespace-tutorial.md",
    "90.vector-db-backup-tutorial.md",
    "91.dense-retrieval-tutorial.md",
    "92.sparse-retrieval-rag-tutorial.md",
    "93.hybrid-search-tutorial.md",
    "94.rrf-fusion-tutorial.md",
]

SPAM_START = re.compile(
    r"^(## (附录|专精)|### 1\.2 术语双轨速查|### 1\.2 读完本篇的最小交付物)",
    re.MULTILINE,
)


def clean(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    # Only trim after 总结 section
    marker = "## 总结与系列下一步"
    idx = text.find(marker)
    if idx < 0:
        return False
    head = text[:idx]
    tail = text[idx:]
    m = SPAM_START.search(tail)
    if not m:
        return False
    # Keep tail up to spam start, strip trailing whitespace
    new_tail = tail[: m.start()].rstrip() + "\n"
    new_text = head + new_tail
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    root = Path(__file__).parent
    for fname in FILES:
        p = root / fname
        changed = clean(p)
        t = p.read_text(encoding="utf-8")
        hz = len(re.findall(r"[\u4e00-\u9fff]", t))
        print(f"{'CLEANED' if changed else 'ok'}: {fname} -> {hz} hanzi, {len(t.splitlines())} lines")


if __name__ == "__main__":
    main()
