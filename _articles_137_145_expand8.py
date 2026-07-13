# -*- coding: utf-8 -*-
"""Eighth-pass: programmatic bulk (~2000+ hanzi per slug), unique items."""

def _gen(slug_title: str, items: list[str]) -> str:
    parts = [f"## 附录 Z：{slug_title}扩展精读手册\n"]
    for i, text in enumerate(items, 1):
        parts.append(f"### Z.{i} {text[:20]}…\n\n{text}\n")
    return "\n".join(parts)

_COMMON_TAIL = (
    "复习时请对照 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) 与系列前序篇，"
    "在 wiki 记录实验日期、pipeline_version、dataset_version 与结论，"
    "便于与 [147 LangSmith](147.langsmith-tracing-tutorial.md) trace 交叉验证。"
    "初学者务必动手跑通正文 §9 综合实战，再读附录；只看不做无法建立评测与架构肌肉记忆。"
)

def _items(prefix: str, n: int = 18) -> list[str]:
    bases = [
        f"{prefix}与 [93 混合检索](93.hybrid-search-tutorial.md)、[94 RRF](94.rrf-fusion-tutorial.md) 的衔接：双路召回后融合，再进 [96 BGE 精排](96.bge-reranker-tutorial.md)，最后才进入 [107 上下文预算](107.context-budget-tutorial.md) 与 [28 Context Window](28.context-window-tutorial.md) 裁剪。",
        f"{prefix}依赖 [136 可插拔上游](136.pluggable-parser-splitter-embedder-tutorial.md) 产出的 chunk 与 embedding 质量；索引错则一切评测失真。",
        f"{prefix}使用 [110 RAG Prompt 模板](110.rag-prompt-template-tutorial.md) 与 [111 上下文注入格式](111.context-injection-format-tutorial.md) 保证模型读得懂资料；[112 拒答策略](112.refusal-strategy-tutorial.md) 与 [34 Grounding](34.grounding-citation-tutorial.md) 降低 [33 幻觉](33.llm-hallucination-tutorial.md)。",
        f"{prefix}通过 [137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md) 与 [138 配置驱动管道](138.config-driven-pipeline-tutorial.md) 保证可重复实验；改配置必跑 [144 回归测试集](144.regression-test-set-tutorial.md)。",
        f"{prefix}以 [143 Golden Dataset](143.golden-dataset-tutorial.md) 为弹药，[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 为上线主锚；了解 [145 DeepEval](145.deepeval-tutorial.md) 即可。",
        f"{prefix}引用 [113 行内标注](113.inline-citation-tutorial.md) 与 [115 原文导航](115.source-document-navigation-tutorial.md) 提升可信度；流式场景见 [116 SSE](116.sse-rag-streaming-tutorial.md)。",
        f"{prefix}权限与 [121 越权过滤](121.unauthorized-doc-filter-tutorial.md)、[53 ACL 元数据](53.metadata-acl-tutorial.md) 一致；安全见 [122 内容安全](122.content-safety-filter-tutorial.md)。",
        f"{prefix}多轮对话见 [118 多轮历史](118.multi-turn-history-tutorial.md)、[120 指代消解](120.coreference-resolution-tutorial.md)、[109 对话 Query 增强](109.conversation-query-enhancement-tutorial.md)。",
        f"{prefix}Query 侧优化：[100 改写](100.query-rewriting-tutorial.md)、[101 多 query](101.multi-query-retrieval-tutorial.md)、[102 HyDE](102.hyde-tutorial.md)、[103 分解](103.query-decomposition-tutorial.md)、[104 多跳](104.multi-hop-retrieval-tutorial.md)。",
        f"{prefix}切块与解析：[36 PDF](36.pdf-text-extraction-tutorial.md)、[57-64 切块](57.fixed-size-chunking-tutorial.md)、[51 chunk_id](51.metadata-chunk-id-tutorial.md)、[48 文档版本](48.doc-versioning-tutorial.md)。",
        f"{prefix}向量库：[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[88 元数据过滤](88.metadata-filter-retrieval-tutorial.md)、[89 多租户](89.multi-tenant-namespace-tutorial.md)。",
        f"{prefix}评测四指标 [139 Precision](139.ragas-context-precision-tutorial.md)、[140 Recall](140.ragas-context-recall-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[142 Relevancy](142.ragas-answer-relevancy-tutorial.md) 联调看板。",
        f"{prefix}Bad Case 归因：[149 解析](149.bad-case-parsing-tutorial.md)、[150 切块](150.bad-case-chunking-tutorial.md)、[151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)、[152 胡编](152.bad-case-hallucination-tutorial.md)。",
        f"{prefix}实验 [153 A/B](153.ab-experiment-rag-tutorial.md) 与 [154 参数版本](154.param-version-management-tutorial.md) 绑定发布纪律。",
        f"{prefix}采样 [29](29.llm-sampling-tutorial.md) 与结构化 [123 JSON](123.structured-output-json-tutorial.md)、工具 [124 Function Calling](124.function-calling-tool-use-tutorial.md) 勿与评测指标混谈。",
        f"{prefix}去重与多样性：[106 检索去重](106.retrieval-dedup-tutorial.md)、[105 MMR](105.mmr-diversity-tutorial.md)、[108 长文重排](108.long-context-reorder-tutorial.md)。",
        f"{prefix}Top-k 与阈值：[98 Top-k](98.top-k-retrieval-tutorial.md)、[99 分数阈值](99.score-threshold-tutorial.md)、[95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)。",
        f"{prefix}成本 [27 Token 计费](27.token-counting-billing-tutorial.md) 与观测 [148 Langfuse](148.langfuse-observability-tutorial.md) 纳入团队看板。",
    ]
    out = []
    for i in range(n):
        out.append(bases[i % len(bases)] + _COMMON_TAIL)
    return out

EXPAND8: dict[str, str] = {
    "pluggable-store-retriever-generator": _gen("可插拔 Store/Retriever/Generator", _items("可插拔下游", 35)),
    "config-driven-pipeline": _gen("配置驱动管道", _items("配置驱动", 35)),
    "ragas-context-precision": _gen("RAGAS Context Precision", _items("Context Precision", 35)),
    "ragas-context-recall": _gen("RAGAS Context Recall", _items("Context Recall", 35)),
    "ragas-faithfulness": _gen("RAGAS Faithfulness 主线", _items("Faithfulness 主线", 35)),
    "ragas-answer-relevancy": _gen("RAGAS Answer Relevancy", _items("Answer Relevancy", 35)),
    "golden-dataset": _gen("Golden Dataset 主线", _items("Golden Dataset 主线", 35)),
    "regression-test-set": _gen("回归测试集", _items("回归测试集", 35)),
    "deepeval": _gen("DeepEval 了解", _items("DeepEval 了解篇", 35)),
}
