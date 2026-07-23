# -*- coding: utf-8 -*-
"""Fifth supplement — close remaining hanzi gaps."""

SUPPLEMENT5 = {
    "llamaindex-index-types": """
## 22. 收束（了解即可）

路线图 [148] 条交付：VectorStoreIndex demo、§10 映射表、声明主栈 [125-128 LangChain](125.langchain-core-tutorial.md)、两小时内完成阅读。下一篇 [132 Query Engine](132.llamaindex-query-engine-tutorial.md) 同样了解即可，然后进入 [135 架构取舍](135.pipeline-vs-framework-tutorial.md) 与 LangChain 主线深化。
""",

    "llamaindex-query-engine": """
## 22. CustomQueryEngine 与拒答（了解即可）

了解 `CustomQueryEngine` 存在即可：在检索为空时返回固定拒答模板（[112](112.refusal-strategy-tutorial.md)），不调用 LLM。LCEL 侧用 `RunnableBranch` 实现同等逻辑——**显式分支** 更易单测。金标 [143](143.golden-dataset-tutorial.md) 应含「无证据」样例，验证两条路径均拒答。

## 23. 与 [135] 单栈纪律

wiki 写死：**生产 RAG = LangChain LCEL + 自研检索（可选）**；LlamaIndex 仅读源码与面试。同一 `request_id` 禁止双栈各跑一遍浪费成本。新人 onboarding：先 [126](126.langchain-lcel-tutorial.md) 全链，再速览本篇对照表。
""",

    "llamaindex-agent": """
## 22. 工具白名单与描述模板（了解即可）

生产 Agent 工具 ≤3 个。`description` 模板：「当用户询问公司员工制度且需查内部知识库时调用；输入为完整中文问句；禁止用于天气、股价、闲聊」。与 [124](124.function-calling-tool-use-tutorial.md) 相同纪律。每次发布检查 description 是否被 prompt 注入篡改。

## 23. 收束

路线图 [150]：ReAct 流程图 + 治理清单 + 声明默认固定 RAG。时间回 [127](127.langchain-retriever-tutorial.md) 与 [93 混合](93.hybrid-search-tutorial.md)。
""",

    "haystack-pipeline": """
## 22. DocumentJoiner 与 RRF（了解即可）

Haystack `DocumentJoiner` 用 RRF 融合多路检索，对照 [94](94.rrf-fusion-tutorial.md)。LangChain 用 `EnsembleRetriever` 或自研 `rrf_merge` Lambda（[127](127.langchain-retriever-tutorial.md)）。**评审价值**：画 Joiner 节点即说明 hybrid 已设计，而非口头「我们会混合检索」。

## 23. 收束

路线图 [151]：手绘 ingest/query 图 + LCEL 等价伪代码 + 不引入 Haystack 依赖的声明。下一篇 [135](135.pipeline-vs-framework-tutorial.md) 写清团队选型。
""",

    "pipeline-vs-framework": """
## 18. 收束

路线图 [152]：ARCHITECTURE 一页、分层表、回滚预案、PR 五问。下一篇落地 [136 三协议](136.pluggable-parser-splitter-embedder-tutorial.md)，把本篇决策变成可执行接口。
""",

    "pluggable-parser-splitter-embedder": """
## 22. ADR 模板（Architecture Decision Record）

```markdown
# ADR-00X: Parser/Splitter/Embedder 协议 v2
- 状态：accepted
- 背景：换 PDF 引擎 / 换 embed 模型
- 决策：三 Protocol + REGISTRY + manifest
- 后果：LC 仅适配器；换 embed 新 collection
- 链接：136 教程、137 下游、138 配置
```

评审通过后入库，与 [154 参数版本](154.param-version-management-tutorial.md) 同步。路线图 [153] 完成：REGISTRY≥2 实现 + CI 契约绿 + [128](128.langchain-vectorstore-tutorial.md) 联调 + ADR 存档。
""",
}
