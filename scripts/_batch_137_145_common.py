# -*- coding: utf-8 -*-
"""Shared helpers for batch 137-145 article generation."""

COMMON_RAG_LINKS = """
| 概念 | 来自 |
|------|------|
| 混合检索 | [93 Hybrid](93.hybrid-search-tutorial.md)、[94 RRF](94.rrf-fusion-tutorial.md) |
| 精排 | [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)、[96 BGE](96.bge-reranker-tutorial.md) |
| Top-k / 阈值 | [98 Top-k](98.top-k-retrieval-tutorial.md)、[99 阈值](99.score-threshold-tutorial.md) |
| Query 改写 | [100 Query Rewriting](100.query-rewriting-tutorial.md) |
| 上下文预算 | [107 Context 预算](107.context-budget-tutorial.md)、[28 窗口](28.context-window-tutorial.md) |
| Prompt 模板 | [110 RAG Prompt](110.rag-prompt-template-tutorial.md) |
| 注入格式 | [111 上下文注入](111.context-injection-format-tutorial.md) |
| 拒答 | [112 拒答策略](112.refusal-strategy-tutorial.md) |
| Grounding | [34 Grounding](34.grounding-citation-tutorial.md)、[33 幻觉](33.llm-hallucination-tutorial.md) |
| 可插拔上游 | [136 Parser/Splitter/Embedder](136.pluggable-parser-splitter-embedder-tutorial.md) |
"""


def _mistakes(pairs: list[tuple[str, str, str]]) -> str:
    out = []
    for i, (wrong, phen, right) in enumerate(pairs, 1):
        out.append(f"""### 8.{i} 错：{wrong}

**现象**：{phen}  
**对**：{right}
""")
    return "\n".join(out)


def _faq(items: list[tuple[str, str]], start: int = 1) -> str:
    lines = []
    for i, (q, a) in enumerate(items, start):
        lines.append(f"### 12.{i} {q}\n\n{a}\n")
    return "\n".join(lines)
