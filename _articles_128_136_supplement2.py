# -*- coding: utf-8 -*-
"""Second clean supplement for slugs still under 5000 hanzi."""

SUPPLEMENT2 = {
    "langchain-text-splitter": """

## 15. Splitter 与检索去重、MMR 的联动

[60 overlap](60.chunk-overlap-tutorial.md) 提高 Recall 的同时，Top-K 常出现 **相邻重复 chunk**（同一条款被 overlap 复制到两块）。检索侧应配合 [106 去重](106.retrieval-dedup-tutorial.md)（按 `chunk_id` 或 `section` 去重）或 [105 MMR](105.mmr-diversity-tutorial.md)（`VectorStore.as_retriever(search_type="mmr")` 见 [128](128.langchain-vectorstore-tutorial.md)）。

调参流程建议：**先固定 splitter 参数跑金标 Recall@5 → 再调 overlap → 最后调 MMR lambda**。不要把三件事同时改，否则无法归因 [150 切块 bad case](150.bad-case-chunking-tutorial.md) 还是检索策略问题。

**代码块与表格**：技术文档在 Splitter 前用 [62 结构感知](62.structure-aware-chunking-tutorial.md) 识别 fenced code 与 markdown 表格，避免 API 示例从中间切断——这是制度库切块之外，研发文档最常见的 Recall 损失来源。

**交付检查**：改 splitter 配置后必须重建向量索引并更新 manifest；仅改在线 `top_k` 不能替代切块版本升级。
""",

    "llamaindex-index-types": """

## 15. StorageContext 与持久化（了解即可）

读 LlamaIndex 项目时常见 `StorageContext.from_defaults(vector_store=...)`。**了解即可** 的三件套：

- **vector_store**：向量与相似度（≈ [76 Chroma](76.chroma-vector-db-tutorial.md) / [75 FAISS](75.faiss-ann-tutorial.md)）；  
- **docstore**：原文或 Node 持久化（Parent 模式见 [65](65.parent-document-retriever-tutorial.md)）；  
- **index_store**：索引结构元数据。

与 LangChain [128 VectorStore](128.langchain-vectorstore-tutorial.md) 对照：**LI 把「建索引」动作更多封装在 `from_documents`；LC 把「写库」显式放在 `add_documents`**。排障时都要问：embed 在哪一步发生？用的哪个模型 [25](25.embedding-vector-tutorial.md)？

**双栈纪律**（[135](135.pipeline-vs-framework-tutorial.md)）：同一业务请求 **不要** 既走 LI Index 又走 LC VectorStore 写同一目录；`chunk_id` 契约统一，但 **编排只选一条栈**。
""",

    "llamaindex-query-engine": """

## 15. Postprocessor 与 LCEL 显式步骤（了解即可）

LlamaIndex 可在 Query Engine 上挂 **NodePostprocessor**（相似度阈值、关键词过滤等）——概念类似你在 LCEL 里 Retriever 之后的 Lambda：[99 阈值](99.score-threshold-tutorial.md)、[106 去重](106.retrieval-dedup-tutorial.md)、[96 精排](96.bge-reranker-tutorial.md)。

**SubQuestionQueryEngine**（了解即可）：把复杂问题拆成子问句多次检索，思想接近 [103 查询分解](103.query-decomposition-tutorial.md) 与 [104 多跳](104.multi-hop-retrieval-tutorial.md)，但由框架驱动。生产若需多跳，常先评估 **固定分解管道** 是否足够，再考虑黑盒分解。

**ChatEngine** 与 [118 多轮历史](118.multi-turn-history-tutorial.md)：多轮是否 **每轮重检索** 是产品 PRD 项，与 LI/LC 无关。历史占用 [28 窗口](28.context-window-tutorial.md) 时，应用 [109 查询增强](109.conversation-query-enhancement-tutorial.md) 改写 standalone query，再进 Retriever。

**迁移清单（LI → LCEL）**：① 导出 `source_nodes` 字段映射；② 对齐 Prompt [110](110.rag-prompt-template-tutorial.md)；③ 接 [147 trace](147.langsmith-tracing-tutorial.md)；④ 金标 [143](143.golden-dataset-tutorial.md) 对比 Faithfulness [141](141.ragas-faithfulness-tutorial.md)；⑤ 切换 feature flag [154](154.param-version-management-tutorial.md)。
""",

    "llamaindex-agent": """

## 15. OpenAI Tool Loop 与 QueryEngineTool 对照（了解即可）

| 概念 | LlamaIndex | OpenAI + LC [124] |
|------|------------|-------------------|
| 工具定义 | QueryEngineTool | `@tool` / JSON schema |
| 循环 | ReActAgent | tool_calls loop |
| 停止条件 | max_iterations | max_iterations |
| ACL | 工具内 Retriever | 工具内 search_kb |

**演练（了解即可，≤2h）**：单工具 `handbook` + 三问：「年假」「差旅」「今天天气」——第三问应 **不调用** 知识库工具。验收：日志可见 tool 选择与 `chunk_ids`；越权问法不返回 finance 块 [121](121.unauthorized-doc-filter-tutorial.md)。

**与 [133] 路线图交付**：能画 `user → Agent → (tool)* → answer`；列出三风险；声明生产默认 [126 固定 RAG](126.langchain-lcel-tutorial.md)。阅读 [ENTERPRISE_RAG_ROADMAP](ENTERPRISE_RAG_ROADMAP.md) D 轨时，Agent 条目标 **了解即可**，不占用主 sprint。
""",

    "haystack-pipeline": """

## 15. 自研 pipeline.json 草图（借鉴 Haystack，不引依赖）

```json
{
  "components": {
    "retriever": {"type": "HybridRetriever", "top_k": 50},
    "reranker": {"type": "BGEReranker", "top_n": 5},
    "prompt": {"template": "rag_v3"},
    "llm": {"model": "gpt-4o-mini", "temperature": 0}
  },
  "connections": [
    ["query", "retriever.query"],
    ["retriever.documents", "reranker.documents"],
    ["reranker.documents", "prompt.context"],
    ["prompt.messages", "llm.messages"]
  ]
}
```

动机同 Haystack **显式 connect**；实现可用 [138 配置驱动](138.config-driven-pipeline-tutorial.md) + [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md)。评审时 **一张图胜过千行 LC**，但运行时仍可 `lcel` 执行。

**ingest 支路** 同理：`loader → splitter → embedder → writer`，对齐 [129-130-128](128.langchain-vectorstore-tutorial.md)。混合检索双路在 JSON 里画清 [93 BM25](93.hybrid-search-tutorial.md) 与 [76 稠密](76.chroma-vector-db-tutorial.md) 的 Joiner [94 RRF](94.rrf-fusion-tutorial.md)。

**4 小时学习包**：Haystack 2 官方 Pipeline 文档 2h + 手绘 ingest/query 图 1h + 写等价 LCEL 伪代码 1h = 路线图 [151] 条完成。
""",

    "pipeline-vs-framework": """

## 15. 案例 C：从「LC 一把梭」到「可插拔六接口」

**背景**：6 个月前 PoC 用 [126 LCEL](126.langchain-lcel-tutorial.md) 两周上线；PDF 版式增多后 Parser 改动波及全链，升级 `langchain-community` 曾断链。

**演进**：  
1. 抽出 [136](136.pluggable-parser-splitter-embedder-tutorial.md) 三协议 + [137](137.pluggable-store-retriever-generator-tutorial.md) 三协议；  
2. 检索换自研 Hybrid（[93](93.hybrid-search-tutorial.md)），编排仍 LCEL；  
3. [76 Chroma](76.chroma-vector-db-tutorial.md) 原生 API on-call 培训；  
4. [143 金标](143.golden-dataset-tutorial.md) 每次发布必跑；  
5. [147 LangSmith](147.langsmith-tracing-tutorial.md) 记录 `hit_chunk_ids`。

**教训**：框架加速 PoC；**契约 + 金标** 才能规模化。ARCHITECTURE.md 应写 **「LC 编排层可替换，Parser/ACL 不可外包给黑盒」**。
""",

    "pluggable-parser-splitter-embedder": """

## 15. 六接口全景与 ingest 任务状态机

本篇完成 **入口三接口**；与 [137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md) 合并为六接口，对应 [ENTERPRISE_RAG_ROADMAP](ENTERPRISE_RAG_ROADMAP.md) 数据层 + 索引层 + 生成层可替换边界。

```text
parse → split → embed → store.write
              (query) → retrieve.search → generate.stream
```

ingest 任务建议对齐 [161 索引状态机](161.index-task-state-machine-tutorial.md)：`pending → parsing → splitting → embedding → writing → done | failed`。失败进 [163 死信](163.retry-dead-letter-tutorial.md)；幂等重建见 [162](162.idempotent-reindex-tutorial.md)。

**OpenAI 兼容 Embedder 适配器**：实现 `Embedder` 协议，内部调 [35 API](35.openai-compatible-api-tutorial.md)，对外 dimension 固定；换模型升 `embedder` major + 新 collection [48](48.doc-versioning-tutorial.md)。

**团队分工**：数据工程维护 Parser/Splitter 注册表；算法维护 Embedder 与评测 [139-142 RAGAS](139.ragas-context-precision-tutorial.md)；后端维护 Store/Retriever/Generator 与 [121 ACL](121.unauthorized-doc-filter-tutorial.md)；全栈用 [128-130 LC](128.langchain-vectorstore-tutorial.md) 做集成测试适配器。
""",
}
