# -*- coding: utf-8 -*-
"""Third supplement — final gap fill without repetitive spam."""

SUPPLEMENT3 = {
    "langchain-text-splitter": """
## 16. 与 [128 VectorStore](128.langchain-vectorstore-tutorial.md) 联调清单

切块完成后立即检查：每个 chunk 的 `metadata["chunk_id"]` 是否唯一；`page_content` 非空；父级 `doc_id` 是否保留。`Chroma.from_documents(..., ids=[...])` 的 ids 列表必须与 chunk_id 一一对应，否则 [51](51.metadata-chunk-id-tutorial.md) 评测与 [113 引用](113.inline-citation-tutorial.md) 会对不齐。
""",

    "llamaindex-index-types": """
## 16. 动手 demo 验收（了解即可）

安装 `llama-index` 后仅跑通：`VectorStoreIndex.from_documents` → `as_retriever(similarity_top_k=3)` → 打印命中片段。再画一张表：LI `Document/Node/Index` 三词对应 LC `Document/VectorStore/Retriever` [125-128](125.langchain-core-tutorial.md)。**不要求**生产切换；要求 **面试 5 分钟讲清映射**。

## 17. 与 [ENTERPRISE_RAG_ROADMAP](ENTERPRISE_RAG_ROADMAP.md) 阶段 3

D 轨在掌握 LangChain 存储链后，用本篇 **扩展视野**。时间盒内完成：demo + 映射表 + wiki「本公司主栈=LangChain」声明。避免双栈并行写同一知识库。
""",

    "llamaindex-query-engine": """
## 16. synthesizer 与 [110 模板](110.rag-prompt-template-tutorial.md)

Query Engine 内部 prompt 常不可见；LCEL 显式维护 system 五段（角色、任务、上下文、引用规则、拒答）。**了解即可** 对比：制度 FAQ 需要 **拒答 [112](112.refusal-strategy-tutorial.md) 与引用 [34](34.grounding-citation-tutorial.md) 写进模板**——显式链更易 code review。

## 17. 空检索与 [99 阈值](99.score-threshold-tutorial.md)

LI 可配相似度后处理器；LC 在 `similarity_score_threshold` 或 Retriever 后 Lambda 实现。共同原则：**无达标证据不调 LLM**，对齐 [112 拒答](112.refusal-strategy-tutorial.md) 与 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 评测。

## 18. 阅读顺序

[131 Index](131.llamaindex-index-types-tutorial.md) → 本篇 → [133 Agent](133.llamaindex-agent-tutorial.md) → 回 [127 Retriever](127.langchain-retriever-tutorial.md) 深化混合检索 [93](93.hybrid-search-tutorial.md)。总预算 ≤1 工作日。
""",

    "llamaindex-agent": """
## 16. 成本与配额（了解即可）

Agent 每轮可能触发 embed + LLM + 工具内检索。应对 **单用户日配额** [169](169.rate-limiting-api-tutorial.md) 与 **单请求 max_iterations**。账单异常时先查是否 Agent 路径被误设为默认——对比 [126 固定链](126.langchain-lcel-tutorial.md) 的 token 曲线。

## 17. 与 [135 架构取舍](135.pipeline-vs-framework-tutorial.md)

架构表「对外 API」行应写：**默认 fixed RAG**；Agent 仅 internal flag。评审问「为何不用 Agent」时，用 **可审计、延迟、ACL** 三论据，而非「不会用」。
""",

    "haystack-pipeline": """
## 16. 组件单测借鉴

Haystack 强调每个 Component 可单独 `run` 测输入输出。迁移到自研：Parser/Splitter/Embedder [136](136.pluggable-parser-splitter-embedder-tutorial.md) 契约测试；Retriever 用金标 [143](143.golden-dataset-tutorial.md) 测 Recall；Generator 测 [141 Faithfulness](141.ragas-faithfulness-tutorial.md)。

## 17. 与 [135][138] 联读

显式图 → `pipeline.yaml` [138](138.config-driven-pipeline-tutorial.md) → 参数版本 [154](154.param-version-management-tutorial.md) → A/B [153](153.ab-experiment-rag-tutorial.md)。Haystack 是 **教材**；落地是 **自家 DSL + 主栈 LCEL**。
""",

    "pipeline-vs-framework": """
## 16. 面试标准答法（背诵骨架）

「我们 **混合架构**：数据入口 [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md)；索引 [76 Chroma](76.chroma-vector-db-tutorial.md) 原生排障；检索自研 Hybrid [93](93.hybrid-search-tutorial.md)；编排 [126 LCEL](126.langchain-lcel-tutorial.md)；ACL/审计自研 [121](121.unauthorized-doc-filter-tutorial.md)；评测 [143 金标](143.golden-dataset-tutorial.md) 守门；框架升级可回滚 [154](154.param-version-management-tutorial.md)。」
""",

    "pluggable-parser-splitter-embedder": """
## 16. ingest 伪代码（端到端）

```python
def ingest_file(path: str, cfg: dict):
    p, s, e = build_pipeline(cfg)
    raws = p.parse(path)
    chunks = s.split(raws)
    vecs = e.embed_documents([c.text for c in chunks])
    store.write(chunks, vecs)  # 137 篇
    return manifest(p.name, s.name, e.name, len(chunks))
```

**验收**：换 `cfg["splitter"]` 仅改配置；`chunk_id` 仍规范；维数断言通过。

## 17. 与 C 轨 36-40、57-65 的 wiki 映射表

维护一张表：C 模块教程编号 → REGISTRY 键名 → 默认实现类。新人 onboarding 先读 C 模块原理，再读本篇接工程接口，最后读 [128-130 LC](128.langchain-vectorstore-tutorial.md) 适配器。
""",
}
