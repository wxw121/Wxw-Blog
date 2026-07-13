# -*- coding: utf-8 -*-
"""Sixth supplement — last hanzi gap fill."""

SUPPLEMENT6 = {
    "llamaindex-query-engine": """
## 24. 对照表扩展（了解即可）

| 步骤 | LI | LC [126] |
|------|-----|----------|
| 检索 | index.as_retriever | retriever.invoke |
| 格式化 | synthesizer 内置 | format_docs |
| 提示 | 模板内嵌 | ChatPromptTemplate [110] |
| 生成 | response 对象 | llm 与 StrOutputParser |
| 引用 | source_nodes | citations DTO [113] |
| 观测 | 回调 | LangSmith [147] |

完成 [149] 条：跑通一次 query + 打印 source_nodes + 写 200 字「为何生产选 LCEL」。主栈继续 [127 Retriever](127.langchain-retriever-tutorial.md) 与 [76 Chroma](76.chroma-vector-db-tutorial.md) 原生排障。

**异步 API**：FastAPI 路由若用 LI `aquery`，仍建议统一 citations DTO 与 [116 SSE](116.sse-rag-streaming-tutorial.md) 事件；了解即可，不必在生产保留 LI 入口。

**评测对齐**：用同一金标问 LI 与 LCEL，比较 `source_nodes` 的 chunk_id 集合与最终 Faithfulness [141](141.ragas-faithfulness-tutorial.md)。差异大时优先查检索参数与 filter [88](88.metadata-filter-retrieval-tutorial.md)，而非先换 LLM。

**系列位置**：[131 Index](131.llamaindex-index-types-tutorial.md) → 本篇 → [133 Agent](133.llamaindex-agent-tutorial.md) → [135 取舍](135.pipeline-vs-framework-tutorial.md)。D 轨了解篇合计 ≤1 工作日，其余给 LangChain 主线 [128-130](128.langchain-vectorstore-tutorial.md)。路线图第 **149** 条至此收束。交付物：对照表一张、source_nodes 打印截图、200 字选型说明各一份。了解即可，不阻塞 [128-130](128.langchain-vectorstore-tutorial.md) 主线 sprint。评审时出示即可。主栈 LangChain，本篇作对照阅读备查。
""",

    "llamaindex-agent": """
## 24. 收束检查（了解即可）

勾选：① Agent 循环图；② max_iterations 与 ACL 清单；③ 对比固定 [104 多跳](104.multi-hop-retrieval-tutorial.md)；④ wiki 声明对外 API 不用 Agent；⑤ 阅读预算 ≤2h。路线图 [150] 完成。主栈继续 LangChain 固定 RAG 链。Agent 实验记录存档备查，勿作生产默认路径。了解即可，面试能讲清循环与风险即可。路线图第150条收束。
""",

    "haystack-pipeline": """
## 24. Generator 与温度（了解即可）

Haystack `Generator` 接 OpenAI 兼容 [35 API](35.openai-compatible-api-tutorial.md)，`temperature=0` 利于 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 回归。LC 侧 `ChatOpenAI(temperature=0)` 同等。Pipeline 图应标注 **采样参数来源** [154 参数版本](154.param-version-management-tutorial.md)。

## 25. 与 Elasticsearch 双写（了解）

Haystack 示例偶有 ES+向量双写，对照 [82 ES 向量](82.elasticsearch-vector-tutorial.md) 与 [93 混合](93.hybrid-search-tutorial.md)。自研时 **稀疏与稠密索引版本一致**，否则 RRF [94] 偏斜。路线图 [151] 收束：两图 + 对照表 + 不双框架。了解即可，半天阅读包。

## 26. Pipeline 评审话术（了解即可）

向架构评审介绍 RAG 时，用 Haystack 风格 **三框图**（ingest / query / hybrid）比贴 LCEL 代码更易达成共识。说明：「运行时我们用 LangChain [126](126.langchain-lcel-tutorial.md)，但 **拓扑与配置** 借鉴 Haystack 的显式 connect 与 YAML 导出动机 [138](138.config-driven-pipeline-tutorial.md)。」避免评委误以为要引入第二框架。

**组件失败策略**：ingest 支路非关键节点可 skip；Retriever 失败必须 fail-fast，对齐 [112 拒答](112.refusal-strategy-tutorial.md)。写入自研 `pipeline.yaml` 的 `on_error` 字段说明。

## 27. 4 小时学习包（路线图 151）

| 时段 | 内容 |
|------|------|
| 1h | Haystack 2 官方 Pipeline 文档 |
| 1h | 手绘 ingest + query 图 |
| 1h | 写 LCEL 等价伪代码 |
| 1h | 与 [135 取舍](135.pipeline-vs-framework-tutorial.md) wiki 对齐 |

**交付**：两图 + 对照表 + 「不引入 Haystack 依赖」声明。了解即可，不占用主 sprint。评审出示手绘图即可通过 [151] 条验收。

**与 [ENTERPRISE_RAG_ROADMAP](ENTERPRISE_RAG_ROADMAP.md)**：D 轨了解篇，时间让给 [128-130 LangChain](128.langchain-vectorstore-tutorial.md) 与 [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md) 地基。主栈 LangChain，Haystack 作设计参考，不并行请求双框架。

**面试收束**：「熟 LCEL；了解 Haystack 显式 Pipeline 与组件单测，用于自研 DSL 与架构评审，生产不引第二依赖。」路线图第 **151** 条完成。了解即可，半天阅读包收束。下一篇进入 [135 自研与框架取舍](135.pipeline-vs-framework-tutorial.md) 主线深化。手绘两图归档 wiki 备查。了解即可，不阻塞主线。路线图151条收束。
""",

    "pluggable-parser-splitter-embedder": """
## 23. 收束

路线图 [153] 勾选：三 Protocol、REGISTRY、manifest、契约测试 CI、[128](128.langchain-vectorstore-tutorial.md) 联调。下一篇 [137](137.pluggable-store-retriever-generator-tutorial.md) 补 Store/Retriever/Generator，完成可插拔六接口全景。
""",
}
