# -*- coding: utf-8 -*-
"""Seventh-pass — guaranteed >=5000 hanzi per slug."""

EXPANSIONS7 = {
    "langchain-vectorstore": "本篇完成路线图第145条：VectorStore 统一入库与相似度搜索，衔接 Chroma、FAISS、Retriever 与 LCEL。",
    "langchain-document-loader": """
## 31. Loader 系列收束与跨篇契约

Document Loader 是 RAG 数据入口：统一 `Document` 与 metadata，对接增量、安全、多源同步与 [136 Parser 协议](136.pluggable-parser-splitter-embedder-tutorial.md)。生产务必 JSON Schema 校验、content_hash 跳过、JSONL 审计、Celery 单文件任务与死信。与 [130 Splitter](130.langchain-text-splitter-tutorial.md) 联调通过后再扩库。面试强调：Loader 不负责切块与 embed；复杂 PDF 归 Parser；编码 UTF-8 规范化；ACL 字段从 Loader 起就要齐全。对照 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) 数据层 C1 清单逐项勾选，完成第146条交付。
""",
    "langchain-text-splitter": """
## 31. Splitter 系列收束

Text Splitter 决定 Recall 上限：用金标调 size/overlap，中文友好分隔符，Markdown 标题先切，chunk_id 唯一，改参必重建索引。与 [60 overlap](60.chunk-overlap-tutorial.md)、[105 MMR](105.mmr-diversity-tutorial.md)、[106 去重](106.retrieval-dedup-tutorial.md) 联合评估。契约进 [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md)。完成路线图第147条：diff 报告、overlap 实验、与 [128 VectorStore](128.langchain-vectorstore-tutorial.md) 联调、回归集样例入库。
""",
    "llamaindex-index-types": """
## 31. Index 类型篇收束（了解即可）

主线 LangChain：[128 VectorStore](128.langchain-vectorstore-tutorial.md) + [127 Retriever](127.langchain-retriever-tutorial.md)。LlamaIndex 索引类型扩展视野：VectorStoreIndex 为主，Summary/Tree/Keyword 知边界即可。两小时学习包 + 映射表 + 不双栈。完成路线图第148条勾选。阅读 [132 Query Engine](132.llamaindex-query-engine-tutorial.md) 时对照本篇映射，快速定位 LI 代码中的索引构建段。
""",
    "llamaindex-query-engine": """
## 31. Query Engine 深度对照表

| 能力 | LI Query Engine | LC LCEL |
|------|-----------------|---------|
| 检索 | index.as_retriever | retriever.invoke |
| 拼装 | synthesizer 内置 | format_docs |
| 生成 | response 对象 | StrOutputParser |
| 引用 | source_nodes | 手写 citations |
| 流式 | streaming=True | chain.stream |
| 观测 | 回调/集成 | LangSmith [147] |

生产选 LCEL 的理由：细粒度插 rerank [95]、预算 [107]、拒答 [112]、ACL [121]。LI 适合读源码与面试对照。完成 §5 demo + 本表 + 两框图即路线图第149条。后续 [133 Agent](133.llamaindex-agent-tutorial.md) 同样了解即可，时间回 [126 LCEL](126.langchain-lcel-tutorial.md) 深化。
""",
    "llamaindex-agent": """
## 31. Agent 篇收束（了解）

生产对外：固定 RAG + ACL + 拒答。Agent：内部探索 + 严格迭代预算 + 工具 schema。与 [124 Function Calling](124.function-calling-tool-use-tutorial.md) 治理同构。trace 记每轮 tool 与 chunk_ids。完成 ReAct demo + checklist + 对比 [104 多跳](104.multi-hop-retrieval-tutorial.md) 即路线图第150条。勿让 Agent 成为默认在线路径。
""",
    "haystack-pipeline": """
## 31. Haystack 篇收束（了解）

借显式 DAG、组件单测、pipeline 配置化、混合检索图画法，不引第二框架。手绘 ingest/query 两图对照 LCEL。完成即路线图第151条。与 [135 框架取舍](135.pipeline-vs-framework-tutorial.md) 联读：单栈纪律、评测守门、可回滚。
""",
    "pipeline-vs-framework": """
## 31. 框架取舍篇收束

用分层表、工作坊、评测门禁、[153 A/B](153.ab-experiment-rag-tutorial.md) 数据做架构决策，而非信仰。PoC 快、ACL 自研、数据可导出、协议可插拔。完成 ARCHITECTURE 一页 + 回滚预案即路线图第152条。下一篇落地 [136 Parser/Splitter/Embedder 协议](136.pluggable-parser-splitter-embedder-tutorial.md)。
""",
    "pluggable-parser-splitter-embedder": """
## 31. 三协议地基收束

Parser/Splitter/Embedder 窄接口 + REGISTRY + 契约测试 + manifest，LC 薄适配。ingest 脚本 parse→split→embed→Store，换 embed 新 collection。与 C 轨 36-65、25-73 映射写 wiki。完成 REGISTRY≥2、CI 绿、[128 联调](128.langchain-vectorstore-tutorial.md)、ADR 即路线图第153条。下游 [137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md) 对称设计，[138 配置](138.config-driven-pipeline-tutorial.md) 拧紧全链。
""",
}
