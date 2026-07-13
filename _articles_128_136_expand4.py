# -*- coding: utf-8 -*-
"""Fourth-pass expansions for 128-136 — sections 21-24, fill to >=5000 hanzi."""

EXPANSIONS4 = {
    "langchain-vectorstore": """
## 21. 读写分离与索引副本策略

生产环境常把 **ingest 写入** 与 **在线查询** 分到不同进程甚至不同机器：夜间 Celery worker 批量 `add_documents`，白天 API 只读 `similarity_search`。Chroma `PersistentClient` 在部分版本下多写者需串行化——用 [159 Celery](159.celery-async-queue-tutorial.md) 单 writer 队列，读者可水平扩展只读副本（文件系统快照或对象存储同步）。FAISS 更适合 **整库替换**：构建新 `save_local` 目录，校验后原子切换 symlink，旧目录只读保留七天，与 [162 幂等重索引](162.idempotent-reindex-tutorial.md) 一致。

读写分离还要统一 **配置指针**：`ACTIVE_COLLECTION=handbook_bge_v3` 存在配置中心，ingest 完成 manifest 校验后才 bump 指针。避免「写了一半的 collection」被 query 读到。回滚即把指针指回 `v2` 并记录 [154 参数版本](154.param-version-management-tutorial.md)。

## 22. 与混合检索、精排的衔接顺序

标准在线链：`embed_query` → VectorStore 宽召回 `k=50` → [88 元数据过滤](88.metadata-filter-retrieval-tutorial.md)（若未下推）→ [94 RRF](94.rrf-fusion-tutorial.md) 或 BM25 合并 → [96 BGE 精排](96.bge-reranker-tutorial.md) top5 → [107 上下文预算](107.context-budget-tutorial.md) → LLM。VectorStore 只承担 **稠密宽召回** 一步；把 cross-encoder 塞进 `similarity_search` 是 §8.4 典型翻车。团队白板应标清每步输入输出类型：`list[Document]` 与 `list[tuple[Document,float]]` 在 LCEL 里用 NamedRunnable 区分。

## 23. 深度 FAQ 与读路径

**Q：Chroma 与 pgvector 何时切换？** 当需要 SQL 事务、与业务库 JOIN、或 DBA 统一备份时看 [81 pgvector](81.pgvector-tutorial.md)；PoC 与单机仍 Chroma。**Q：ids 用 UUID 还是 chunk_id？** 企业一律 chunk_id，UUID 仅 demo。**Q：如何验证 filter 生效？** 用无权 principal 跑 [144 回归](144.regression-test-set-tutorial.md) 用例，断言 `fin:*` chunk 不在 hit_ids。**Q：VectorStore 与 [65 Parent](65.parent-document-retriever-tutorial.md)？** child 入 store，parent 在 docstore，Retriever 层扩展。**Q：线上 collection 能热删吗？** 用版本指针切换，避免白天 `delete_collection` 误操作。

读路径自检：① embed_documents vs embed_query；② 换模型为何新 collection；③ FAISS load 必传 Embeddings；④ MMR 与 similarity 选型；⑤ 排障先 count 还是先改 prompt——应选 count。
""",

    "langchain-document-loader": """
## 21. 文件类型嗅探与 loader_map 实现

混合目录不要只靠扩展名：`.pdf` 可能是误命名 txt。推荐 `python-magic` 或 `filetype` 嗅探 MIME，再查 `LOADER_MAP`：

```python
LOADER_MAP = {
    "application/pdf": PyMuPDFLoader,
    "text/plain": TextLoader,
    "text/markdown": TextLoader,
}
```

未知 MIME **进死信** 并告警，不要默认 TextLoader 硬读二进制。与 [41 编码](41.text-encoding-detection-tutorial.md) 组合：文本类先检测 charset 再构造 Loader。manifest 记录 `detected_mime` 与 `declared_ext`，方便 [149 解析 bad case](149.bad-case-parsing-tutorial.md) 归因。

## 22. 大文件分片与流式 parse

万页 PDF 禁止 `load()` 一次进内存。模式：Parser 流式写临时 `.txt.part`，Loader `lazy_load` 按页 yield Document；或按 **章节文件** 预切分再 DirectoryLoader。单文件大小上限（如 200MB）在 ingest 入口拒绝，并返回可理解错误码给 CMS。与 [161 索引状态机](161.index-task-state-machine-tutorial.md) 结合：大文件任务状态 `parsing` → `splitting` → `embedding`，失败可 resume 从上次页码继续。

## 23. 数据契约评审与跨团队协作

数据组、法务、研发三方评审 **Loader 输出 JSONL 样例**：字段是否够溯源（[52 source/page](52.metadata-source-page-tutorial.md)）、是否含 PII（需脱敏字段清单）、是否含过期制度版本（[48 版本](48.doc-versioning-tutorial.md) 与 `effective_to`）。评审通过才开放生产 ingest 队列。Parser 由别的团队维护时，HTTP 边界返回 RawDocument JSON（见 [136 协议](136.pluggable-parser-splitter-embedder-tutorial.md)），Loader 层变薄为 HTTP 客户端 + 重试。

## 24. 深度 FAQ

**Q：PyPDFLoader 与 PyMuPDFLoader？** 简单可选 PyPDF；中文版式优先 PyMuPDF（[42](42.pymupdf-tutorial.md)）。**Q：Confluence 导出 HTML 能直接 load 吗？** 应先抽正文 DOM，否则噪声淹没检索。**Q：Loader 要写单元测试吗？** 要，用 fixtures 小文件断言 metadata 必填字段。**Q：增量如何发现删除？** CMS webhook `deleted` 事件或全量 manifest diff。**Q：与 [47 去重](47.doc-dedup-tutorial.md)？** load 后 hash 去重再 Splitter。
""",

    "langchain-text-splitter": """
## 21. LangChain Splitter 类选型对照

| 类 | 适用 | 注意 |
|----|------|------|
| CharacterTextSplitter | 固定长度 demo | 易断句 |
| RecursiveCharacterTextSplitter | 通用制度/说明 | 调 separators |
| MarkdownHeaderTextSplitter | 有标题的 md | 先粗后细 |
| TokenTextSplitter | API token 上限 | tiktoken 模型一致 |
| PythonCodeTextSplitter | 代码库 | 保语法结构 |

与 C 轨 [57-65](57.fixed-size-chunking-tutorial.md) 一一对照写在 wiki，新人改 REGISTRY 时不迷路。HTML 用 [64 DOM 切块](64.html-dom-chunking-tutorial.md) 思路，可先 BeautifulSoup 再 Recursive。

## 22. 特殊内容：表格、列表、代码块

表格行不宜从中间切开——检索到半行无法理解。策略：检测 markdown 表格块 `|---|` 作为原子单元；或表格转 CSV 一句一行入 metadata sidecar。列表项 similarly 保持 `1.` 开头段落完整。代码块用 fence 检测，**fence 内不再递归切**。Bad case [150](150.bad-case-chunking-tutorial.md) 里「半段代码」多由此引起。金标问「配置示例是什么」时，Recall 依赖代码块完整。

## 23. 与 embed 上限、检索的三角关系

chunk 过大：超 embed 模型长度（[27 Token](27.token-counting-billing-tutorial.md)）被截断，语义丢一半。chunk 过小：上下文碎片化，需更大 k 与 [107 预算](107.context-budget-tutorial.md) 压力。用金标画 **Recall@k vs 平均 chunk token** 曲线找拐点。overlap 不是越大越好：[60 overlap](60.chunk-overlap-tutorial.md) 与 [106 去重](106.retrieval-dedup-tutorial.md) 联合看 Top-8 唯一段落数。

## 24. 深度 FAQ

**Q：splitter 改 overlap 要重建索引吗？** 必须，chunk 边界变了。**Q：如何保留 Loader 的 page？** `split_documents` 继承 metadata，只追加 `start_index`。**Q：中文需要 jieba 吗？** 递归分隔符通常够；除非词级特殊需求。**Q：与 [130] 自研 Splitter 协议？** LC 类包一层 `protocol.split`（[136](136.pluggable-parser-splitter-embedder-tutorial.md)）。**Q：如何测切块质量？** 金标 + 人工抽 50 chunk + [144 回归](144.regression-test-set-tutorial.md)。
""",

    "llamaindex-index-types": """
## 21. StorageContext 与 vector_store 参数（了解）

`VectorStoreIndex(nodes, storage_context=storage_context)` 中 `storage_context.vector_store` 可指向 Chroma、Qdrant、Milvus 等。概念上等价于：指定 **向量写到哪里**。LangChain 侧你在 `Chroma.from_documents` 里写 `persist_directory`；LI 用 storage_context 绑定。了解即可：**读 LI 项目时看到 storage_context，想到 [76 Chroma](76.chroma-vector-db-tutorial.md) 或 [78 Qdrant](78.qdrant-tutorial.md)**，不必为此引入第二套存储。

## 22. 构建模式：batch insert vs 流式

大库构建用 `index.insert_nodes(batch)` 循环，配合 [67 批处理](67.embedding-batching-tutorial.md)。`from_documents` 适合教程与小库。失败重试按 batch 粒度，避免整库重跑。manifest 记录 `index_build_mode=batch|stream` 与 `node_count`。

## 23. ComposableGraph 与多知识库（了解）

多子公司手册可每库一 `VectorStoreIndex`，`ComposableGraph` 路由子问题到子 index。复杂度高、延迟难估，与 [89 多租户](89.multi-tenant-namespace-tutorial.md) 的 collection 策略比较后再选。面试：**知道名词，生产默认单库 + metadata filter**。

## 24. 深度 FAQ（了解档）

**Q：SummaryIndex 能替代 VectorStoreIndex 吗？** 不能作企业主路径。**Q：LI 索引要单独备份吗？** 向量在后端，备份策略跟 [76][90 备份](90.vector-db-backup-tutorial.md)。**Q：Node 和 Document 怎么转？** `Document(page_content=node.get_content(), metadata=node.metadata)`。**Q：要学 TreeIndex 吗？** 了解即可，时间给 [128-130](128.langchain-vectorstore-tutorial.md)。**Q：LI 与 LC 双栈？** 禁止同一请求双路径（[135](135.pipeline-vs-framework-tutorial.md)）。
""",

    "llamaindex-query-engine": """
## 21. CustomQueryEngine 扩展点（了解）

LI 允许继承 `CustomQueryEngine` 手写 `custom_query`——等价于 LC 里自定义 `Runnable`。了解即可：说明 Query Engine 不是魔法，**可下钻到 retriever + synthesizer**。读源码排障时找 `retrieve` 与 `synthesize` 两函数。

## 22. 与 citations、faithfulness 的衔接

`response.source_nodes` 提供引用素材，映射 [34 Grounding](34.grounding-citation-tutorial.md)、[113 行内引用](113.inline-citation-tutorial.md)。LC 侧你从 `retriever.invoke` 拿 docs 自写 citations。评测 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 时，**进 prompt 的 context 列表** 要与 source_nodes 一致，不论框架。

## 23. 多模态与结构化输出（了解）

LI 新版本有图片、表格节点类型——与 [56 多模态](56.multimodal-image-text-tutorial.md) 路线图衔接。企业文本 RAG 主路径仍纯文本。`response_mode` 选 `compact` 时注意 [28 窗口](28.context-window-tutorial.md) 与 [107 预算](107.context-budget-tutorial.md)。

## 24. 深度 FAQ

**Q：Query Engine 能直接接 FastAPI 吗？** 可以但不推荐黑盒包一切；LC+LCEL 更易插 [147 trace](147.langsmith-tracing-tutorial.md)。**Q：sub_question 模式贵吗？** 贵，多次 LLM+检索。**Q：streaming 与 [116 SSE](116.sse-rag-streaming-tutorial.md)？** 协议层统一，框架只产 token 迭代器。**Q：为何了解档仍要写实战？** 面试要能画两框图。**Q：与 [132] 下一步？** 回 [127 Retriever](127.langchain-retriever-tutorial.md) 深化。
""",

    "llamaindex-agent": """
## 21. 工具注册与描述工程（了解）

`QueryEngineTool.from_defaults(query_engine, name="handbook", description="...")` 的 description 决定 Agent 是否调用。写清：**查什么、不查什么、需要哪些参数**。过宽描述导致乱调工具；过窄导致该用不用。与 [124 Function Calling](124.function-calling-tool-use-tutorial.md) 的工具描述规范相同。

## 22. 记忆与状态（了解）

Agent 会话状态可能累积 tool output，撞 [28 上下文窗口](28.context-window-tutorial.md)。要截断历史 tool 结果或摘要（[119 摘要记忆](119.summary-memory-tutorial.md)）。多轮是否每轮重检索见 [118 多轮](118.multi-turn-history-tutorial.md)——与 Agent 框架无关的产品决策。

## 23. 与固定管道、合规的边界

对外客服、金融问答：**固定 RAG + [112 拒答](112.refusal-strategy-tutorial.md) + ACL**。Agent 仅内部研究或运维 copilot。审计要求可回放时，Agent 的「思考链」是否存、存多久需法务定（[148 Langfuse](148.langfuse-observability-tutorial.md) 配置采样与脱敏）。

## 24. 深度 FAQ

**Q：ReActAgent 与 OpenAIAgent？** API 不同，治理相同：迭代上限、工具 ACL。**Q：Agent 能替代 [104 多跳](104.multi-hop-retrieval-tutorial.md)？** 探索可以，生产多跳常手写更可控。**Q：tool 返回空检索怎么办？** 返回结构化「无结果」，让 Agent 走 [112 拒答](112.refusal-strategy-tutorial.md) 路径。**Q：要投入多少学时？** ≤2h demo，然后回主线。**Q：面试怎么说？** 知道工具循环与风险，生产固定链。
""",

    "haystack-pipeline": """
## 21. Pipeline 可视化与文档化（了解）

Haystack 可导出 pipeline 图，适合 **架构评审 PPT**。你们可用 Mermaid 画 LC 等价图：ingest 支路与 query 支路分色，标 [94 RRF](94.rrf-fusion-tutorial.md) 汇合点。图的价值是让产品/法务理解数据流，而非引入 Haystack 依赖。

## 22. 错误传播与组件边界（了解）

Haystack Component 抛错时 pipeline 中断；LC LCEL 可用 `fallback` Runnable。自研 DAG 应定义 **每组件错误策略**：Parser 跳过单文件 vs 整批失败。借鉴 Haystack 的显式边，在自家 `pipeline.yaml` 写 `on_error: skip|fail`。

## 23. 与 Elasticsearch 混合教程对照（了解）

Haystack 官方常演示 ES + embedding；对照 [82 ES 向量](82.elasticsearch-vector-tutorial.md)、[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)。LangChain 用 `ElasticsearchStore` + BM25Retriever。学 Haystack **学拓扑**，不必换栈。

## 24. 深度 FAQ

**Q：Haystack 2 还要学 1 吗？** 只看 2.x。**Q：能部分采用吗？** 可以只借鉴图与单测，不引包。**Q：与 [134] 和 [135] 关系？** 本篇了解思想，135 做取舍。**Q：面试？** 能画 Haystack 式 DAG 并映射 LCEL。**Q：作业？** 手绘两张图对比 ingest/query。
""",

    "pipeline-vs-framework": """
## 21. 成本模型：框架许可 vs 工程人力

框架本身多开源，成本在 **升级断链、招聘熟悉度、观测集成**。自研成本在 **初期慢、长期可控**。用表格估算：未来 12 个月预计多少次切块/检索/模型变更——变更越多，越值得 [136-138 可插拔+配置](138.config-driven-pipeline-tutorial.md)。不要为「酷」全自研，也不要为「快」把 ACL 交给 prompt。

## 22. 并购、外包与知识转移

供应商交付的 RAG 常基于 LC demo。收购或交接时问：**能否导出 chunk、向量、金标？** 协议在 [136-137](137.pluggable-store-retriever-generator-tutorial.md)，合同里写数据可迁移。外包代码要有 Parser/Splitter 单测，避免黑盒交付。

## 23. 与 E 模块评测门禁

任何「换框架」或「抽自研」必须过 [143 金标](143.golden-dataset-tutorial.md)、[144 回归](144.regression-test-set-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 门槛。架构会没有评测会吵架。[153 A/B](153.ab-experiment-rag-tutorial.md) 给产品看数据，不是研发信仰战。

## 24. 深度 FAQ

**Q：10 人团队推荐？** LC + Chroma PoC，Parser 尽快协议化。**Q：100 人金融？** ACL/审计自研，编排可配置。**Q：何时引入 Haystack/LI？** 作阅读参考，不默认生产。**Q：如何防双栈？** 架构门禁 + 单 request 单路径 lint。**Q：文档放哪？** `ARCHITECTURE.md` 与代码同库。
""",

    "pluggable-parser-splitter-embedder": """
## 21. 端到端 ingest 脚本详解

```python
def ingest_path(path: str, cfg: dict, store):
    parser, splitter, embedder = build_pipeline(cfg)
    raw = parser.parse(path)
    chunks = splitter.split(raw)
    if not chunks:
        log.warn("empty_chunks", path=path)
        return
  texts = [c.text for c in chunks]
    vecs = embedder.embed_texts(texts)
    ids = [c.metadata["chunk_id"] for c in chunks]
    store.upsert(ids=ids, texts=texts, vectors=vecs, metadatas=[c.metadata for c in chunks])
```

`store` 实现 [137](137.pluggable-store-retriever-generator-tutorial.md) 协议，内部可委托 [128 LC VectorStore](128.langchain-vectorstore-tutorial.md) 或原生 [76 Chroma](76.chroma-vector-db-tutorial.md)。**禁止**在脚本里散落 `Chroma.from_documents` 与自研 embed 两套逻辑。

## 22. 版本演进与 ADR 模板

每个 Parser/Splitter/Embedder 实现附 ADR：背景、决策、替代方案、manifest 字段、弃用条件。`schema_version` major 变更触发全量重建通知。与 [154 参数版本](154.param-version-management-tutorial.md) 表合并展示：业务方可查「当前生产用哪套 recursive_600_80」。

## 23. 与 C 轨 36-44、57-65、25-73 的完整映射

Parser 线：[36 PDF](36.pdf-text-extraction-tutorial.md)→[42 PyMuPDF](42.pymupdf-tutorial.md)→[44 Unstructured](44.unstructured-io-tutorial.md)。Splitter 线：[57 固定](57.fixed-size-chunking-tutorial.md)→[58 递归](58.recursive-character-chunking-tutorial.md)→[63 MD AST](63.markdown-ast-chunking-tutorial.md)。Embedder 线：[25 向量](25.embedding-vector-tutorial.md)→[66 归一化](66.l2-normalization-tutorial.md)→[67 批处理](67.embedding-batching-tutorial.md)→[73 微调](73.embedding-finetune-tutorial.md)。REGISTRY 的 key 名与教程编号对应写在 wiki，新人培训按图索骥。

## 24. 故障注入与季度演练

季度演练：Parser 返回空、Splitter 零 chunk、Embedder 超时、manifest 缺字段、用旧 embedder 查新 collection。验证 [163 死信](163.retry-dead-letter-tutorial.md) 与 query [112 拒答](112.refusal-strategy-tutorial.md)。记录 playbook 给 on-call。比背 Protocol 更能建立信心。

## 25. 深度 FAQ

**Q：Protocol 用 typing 还是 abc？** `Protocol` 便于 struct 适配；`abc.ABC` 便于强制子类。**Q：Chunk 要多大 dataclass？** text + metadata + chunk_id 即可。**Q：HTTP Parser 如何测？** 契约测试 mock HTTP 返回 JSON。**Q：与 LangChain 谁先？** 先 Protocol 单测，再薄适配 LC。**Q：完成标志？** REGISTRY≥2 实现、CI 契约绿、manifest 落盘、与 128 联调。
""",
}
