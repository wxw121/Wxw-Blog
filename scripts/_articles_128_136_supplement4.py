# -*- coding: utf-8 -*-
"""Fourth supplement — final gap to >=5000 hanzi."""

SUPPLEMENT4 = {
    "llamaindex-index-types": """

## 18. KeywordTable 与稀疏检索（了解即可）

`KeywordTableIndex` 维护关键词到 Node 的映射，思想接近 [92 稀疏检索](92.sparse-retrieval-rag-tutorial.md) 与 BM25。LangChain 侧更常见 `BM25Retriever` + [93 混合](93.hybrid-search-tutorial.md)。**了解即可**：读到 LI 文档时知道它在补「字面匹配」短板，不必在生产 LI 栈里默认启用。

## 19. 备份与 embed 一致性

LI 向量在后端（Chroma/Qdrant 等），备份策略同 [90 向量库备份](90.vector-db-backup-tutorial.md)。**构建期与查询期 embed 模型必须一致**（[25 Embedding](25.embedding-vector-tutorial.md)），换模型 = 新 Index/Collection，与 [128 LC](128.langchain-vectorstore-tutorial.md) 铁律相同。
""",

    "llamaindex-query-engine": """

## 19. 流式与 [116 SSE](116.sse-rag-streaming-tutorial.md)

LI `streaming=True` 产出 token 迭代器；生产 FastAPI 更常标准化 SSE 事件：`message` / `citations` / `done`（[116](116.sse-rag-streaming-tutorial.md)）。**了解即可**：无论 LI 还是 LC，**前后端契约** 优先于框架 API。`source_nodes` 通常在流结束后一次性返回，对齐 [113 引用](113.inline-citation-tutorial.md) 时机。

## 20. 精排插入点

Cross-encoder [96 BGE](96.bge-reranker-tutorial.md) 应在「检索后、进 synthesizer 前」。LCEL 显式 `retriever | rerank | format`；LI 用 postprocessor。**企业选型**：显式链更易插 [107 预算](107.context-budget-tutorial.md) 与 [108 重排](108.long-context-reorder-tutorial.md)。
""",

    "llamaindex-agent": """

## 18. trace 字段规范（了解即可）

每轮 Agent 记录：`session_id, iteration, tool_name, args_hash, retrieve_ms, llm_ms, hit_chunk_ids, user_acl`。对接 [147 LangSmith](147.langsmith-tracing-tutorial.md) 或 [148 Langfuse](148.langfuse-observability-tutorial.md)。**禁止** 把完整用户 PII 写入 thought 日志。

## 19. 与 [104 多跳](104.multi-hop-retrieval-tutorial.md) 产品对比

固定多跳：分解 query → 多次检索 → 合并 → 一次生成；路径确定、易评测。Agent 多跳：模型决定跳数与工具；灵活但难回归 [144](144.regression-test-set-tutorial.md)。**默认** 固定管道；Agent 作 research spike。
""",

    "haystack-pipeline": """

## 18. Ranker 与 Joiner 在 RAG 中的位置

Haystack 教程常画：`Retriever(dense) + Retriever(bm25) → Joiner(RRF)` → `Ranker` → `PromptBuilder` → `Generator`。映射本系列：[93-94](94.rrf-fusion-tutorial.md) → [96](96.bge-reranker-tutorial.md) → [110](110.rag-prompt-template-tutorial.md) → LCEL [126](126.langchain-lcel-tutorial.md)。**了解即可** 能临摹此图即可通过路线图 [151] 条。

## 19. on_error 策略

Haystack Pipeline 可配置节点失败跳过或失败停止。RAG 生产建议：**Retriever 失败 fail-fast**（无证据不生成）；非关键 enrich（如摘要标签）可 skip。写入自研 DSL 的运维手册。
""",

    "pipeline-vs-framework": """

## 17. 数据可导出与并购尽调

架构决策表应含一行：**chunk、向量、金标是否可导出**。并购或下云时，深绑不可导出 SaaS 框架是风险。契约化 [136-137](136.pluggable-parser-splitter-embedder-tutorial.md) 降低锁定，与 [ENTERPRISE_RAG_ROADMAP](ENTERPRISE_RAG_ROADMAP.md) 工程化层一致。
""",

    "pluggable-parser-splitter-embedder": """

## 18. 错误分类与运维

| 错误 | 处理 |
|------|------|
| Parser 单文件失败 | 跳过 + 死信 [163] |
| Splitter 产出 0 chunk | warn + 人工复核 |
| Embedder 429 | 退避 [69](69.embedding-retry-rate-limit-tutorial.md) |
| 维数不匹配 | 阻断 ingest，修配置 |

on-call 手册链接 [76 Chroma count](76.chroma-vector-db-tutorial.md) 与 manifest 路径，快速判断是 **入口三件套** 还是 **Store** 层问题（[137](137.pluggable-store-retriever-generator-tutorial.md)）。
""",
}
