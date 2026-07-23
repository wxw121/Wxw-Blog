# -*- coding: utf-8 -*-
import re
from pathlib import Path

files = [
    "95.cross-encoder-rerank-tutorial.md",
    "96.bge-reranker-tutorial.md",
    "97.cohere-rerank-tutorial.md",
    "98.top-k-retrieval-tutorial.md",
    "99.score-threshold-tutorial.md",
    "100.query-rewriting-tutorial.md",
    "101.multi-query-retrieval-tutorial.md",
    "102.hyde-tutorial.md",
    "103.query-decomposition-tutorial.md",
    "105.mmr-diversity-tutorial.md",
    "106.retrieval-dedup-tutorial.md",
    "107.context-budget-tutorial.md",
    "108.long-context-reorder-tutorial.md",
    "109.conversation-query-enhancement-tutorial.md",
    "110.rag-prompt-template-tutorial.md",
    "111.context-injection-format-tutorial.md",
    "112.refusal-strategy-tutorial.md",
    "113.inline-citation-tutorial.md",
    "114.footnote-citation-tutorial.md",
    "115.source-document-navigation-tutorial.md",
]

for f in files:
    t = Path(f).read_text(encoding="utf-8")
    h = len(re.findall(r"[\u4e00-\u9fff]", t))
    status = "OK" if h >= 5000 else "SHORT"
    print(f"{f}: {h} {status}")
