# -*- coding: utf-8 -*-
"""Sixth-pass expansions — final substantive top-up to >=5000 hanzi."""

EXPANSIONS6 = {
    "langchain-vectorstore": """
## 26. 收束

本篇 VectorStore 集成是 D 轨存储插头：统一 Chroma/FAISS 入库与相似度搜索，对接 Retriever 与 LCEL，换引擎少改链。务必完成双后端冒烟与 ACL 用例，再进入 Loader 与 Splitter 系列。
""",
    "langchain-document-loader": """
## 28. 实战：ingest 编排伪代码

```python
def ingest_root(root: Path, cfg: dict) -> list[Document]:
    manifest = load_manifest()
    docs_out = []
    for path in iter_files(root, cfg["glob"]):
        h = file_hash(path)
        if manifest.get(str(path)) == h:
            continue
        loader = pick_loader(path, cfg)
        for doc in loader.lazy_load():
            validate_metadata(doc.metadata)
            doc.metadata["content_hash"] = h
            doc.metadata.setdefault("doc_id", stable_doc_id(path))
            docs_out.append(doc)
        manifest[str(path)] = h
    save_manifest(manifest)
    return docs_out
```

`validate_metadata` 用 JSON Schema 拒绝缺 `source`/`acl_group`。`pick_loader` 走 REGISTRY（[136](136.pluggable-parser-splitter-embedder-tutorial.md)）。输出接 [130 Splitter](130.langchain-text-splitter-tutorial.md) 而非直接 embed。

## 29. 与观测、bad case 的衔接

每次 load 批任务打 span：`files_scanned, files_loaded, files_skipped, empty_text_count, duration_ms`。空文本率周环比上升触发 [149 解析](149.bad-case-parsing-tutorial.md) 工单。metadata 缺字段率在 PR 门禁拦截，不许进 Splitter。

## 30. 场景附录（制度库/客服/研发文档）

制度库：PDF 为主，PyMuPDFLoader，强调 page metadata。客服：HTML 导出，DOM 抽正文。研发文档：Git md + 代码块保护（交 [130](130.langchain-text-splitter-tutorial.md)）。各场景 loader_map 写在 [138 配置](138.config-driven-pipeline-tutorial.md)，勿硬编码在业务服务里。
""",
    "langchain-text-splitter": """
## 28. 实战：split 流水线

```python
def split_docs(docs: list[Document], cfg: dict) -> list[Document]:
    header = MarkdownHeaderTextSplitter(headers_to_split_on=[("#","h1"),("##","h2")])
    recursive = RecursiveCharacterTextSplitter(chunk_size=cfg["size"], chunk_overlap=cfg["overlap"],
        separators=["\\n\\n","\\n","。","！","？"," ",""])
    out = []
    for doc in docs:
        sections = header.split_text(doc.page_content) if doc.metadata.get("mime") == "text/markdown" else [doc]
        for sec in sections:
            sec.metadata.update(doc.metadata)
            for i, chunk in enumerate(recursive.split_documents([sec])):
                chunk.metadata["chunk_id"] = f\"{doc.metadata['doc_id']}:c{i:04d}\"
                out.append(chunk)
    return out
```

入库前断言 chunk_id 唯一。参数来自 [154 版本表](154.param-version-management-tutorial.md)。

## 29. 评测记录表示例

金标 twenty 条：记录每个 (size,overlap) 的 Recall@5、MRR、平均 chunk 数。选 sweet spot 写入 wiki，不是个人笔记本。改 overlap 触发 [48 文档版本](48.doc-versioning-tutorial.md) 与索引重建通知。

## 30. 与检索、生成的联动说明

切块过大 → embed 截断 → 检索分数虚高但语义不全。过小 → k 增大 → [107 预算](107.context-budget-tutorial.md) 爆。与 [105 MMR](105.mmr-diversity-tutorial.md) 联调时同时记录 Top-8 唯一 section 数。生成侧 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 下降时先查检索 chunk 是否断裂（[150](150.bad-case-chunking-tutorial.md)）。
""",
    "llamaindex-index-types": """
## 28. 对照学习：LI 与 LC 索引构建

| 步骤 | LlamaIndex | LangChain |
|------|------------|-----------|
| 载入 | SimpleDirectoryReader | Document Loader [129] |
| 切分 | NodeParser | TextSplitter [130] |
| 嵌入 | 构建 Index 时 embed | Embeddings + VectorStore [128] |
| 查询 | as_query_engine | as_retriever + LCEL [126] |

用此表做笔记即可，不必两套都部署。时间投入建议 70% LC / 30% LI 阅读。

## 29. 案例：何时不该用 TreeIndex

十层嵌套产品手册听起来适合 TreeIndex，但维护树关系成本高、查询延迟难控。更稳做法：Markdown 标题切块（[63](63.markdown-ast-chunking-tutorial.md)）+ 向量检索 + 必要时 [104 多跳](104.multi-hop-retrieval-tutorial.md)。TreeIndex 留在 lab。

## 30. 了解档 FAQ 收束

LI 索引类型篇的定位是 **扩大视野、避免面试露怯、读开源不迷路**。生产默认 VectorStoreIndex 等价路径在 LC 已覆盖。完成 §5 demo + 本表 + [135 单栈](135.pipeline-vs-framework-tutorial.md) 纪律即可勾选路线图 148 条。
""",
    "llamaindex-query-engine": """
## 28. 分步拆解 Query Engine 内部

逻辑四步：① `embed_query`；② `retriever.retrieve` 得 nodes；③ `response_synthesizer` 把 nodes 压进 prompt；④ LLM 生成 `Response`。LC 等价：`retriever.invoke` → `format_docs` → `prompt | llm`。插桩点：② 后记 hit_ids，③ 前记 prompt token（[27](27.token-counting-billing-tutorial.md)），④ 后记 latency。

## 29. 与 rerank、拒答的插入点

若 LI 项目有 rerank，发生在 ②③ 之间。LC 显式加 `retriever | reranker | format`。拒答 [112](112.refusal-strategy-tutorial.md) 在 ② 后判断：无 nodes 或 top1_score 低于阈值则不走 LLM。Query Engine 黑盒时找 `EmptyResponse` 或自定义 `CustomQueryEngine` 钩子。

## 30. 了解档实战 FAQ 收束

**Q：生产推荐 Query Engine 吗？** 团队已标准化 LCEL 时不推荐另起炉灶。**Q：如何 debug source_nodes 空？** 查 index 是否空、top_k、embed 模型。**Q：多语言 query？** 与 LC 相同，靠 embed 模型 [70](70.mixed-language-embedding-tutorial.md)。**Q：streaming 产品化？** 见 [116][174]。**Q：本篇学完？** 回 [127 Retriever](127.langchain-retriever-tutorial.md) 深化策略。
""",
    "llamaindex-agent": """
## 28. Agent 循环逐步（了解）

轮次1：LLM 输出 thought + 选 tool_A；执行 tool_A 得 observation；轮次2：LLM 再推理…直到 final answer 或达 max_iterations。与 [124](124.function-calling-tool-use-tutorial.md) 相同。trace 每轮记 `tool_name, args_hash, latency, chunk_ids`。

## 29. 工具设计 anti-pattern

勿把「整个数据库」包成一个 tool；应拆「查手册」「查工单」「查财务」且各带 ACL。勿用自然语言描述替代 filter 参数。tool 返回 JSON 结构化，便于 Agent 解析与日志审计。

## 30. 了解档收束

Agent 篇定位：知道循环与风险，生产默认固定 RAG。实验 ≤2h，治理 checklist 合并到 [135 架构](135.pipeline-vs-framework-tutorial.md)。路线图 150 条勾选：能画 Agent 循环图 + 说清为何对外不用。
""",
    "haystack-pipeline": """
## 28. ingest/query 两图文字版（了解）

**Ingest 图**：File → FileConverter → Preprocessor → DocumentCleaner → Embedder → DocumentWriter → DocumentStore。**Query 图**：Query → QueryClassifier（可选）→ Retriever(s) → Joiner → Ranker → PromptBuilder → Generator → Answer。LC 等价：Loader→Splitter→Embeddings→VectorStore；query 侧 retriever→(rerank)→prompt→llm。

## 29. 借 Haystack 写自家 pipeline.yaml

字段示例：`retriever.dense.k`、`retriever.sparse.top_k`、`joiner.method=rrf`、`generator.model`。与 [138 配置驱动](138.config-driven-pipeline-tutorial.md) 同构。Haystack 不必引入，YAML schema 可内部定义。

## 30. 了解档收束

Haystack 篇价值在 **显式 DAG 与评审沟通**。4h 阅读+手绘+对照 LCEL 即可。路线图 151 条勾选：两张图 + 说明为何不双栈引入 Haystack。
""",
    "pipeline-vs-framework": """
## 28. 决策工作坊详细议程（60min）

0-10min：现状白板（模块×技术×痛点）；10-25min：填 §9 分层表；25-40min：选 3 个高风险模块定自研/框架；40-50min：写回滚与评测门禁；50-60min：RACI 签名。产出拍照上传 wiki，与 [ARCHITECTURE.md] 链接。

## 29. 常见争论裁决规则

「框架更快」→ 用两周 PoC 验证，金标十条。[「自研更可控」→ 用 ACL 事故案例说明边界。「LI 更先进」→ 对照 [135] 单栈与映射表。无数据不上会。

## 30. 主线收束

框架取舍不是宗教：PoC 快、核心稳、评测守门、可回滚。完成 §9 表 + 工作坊记录 + [153 A/B](153.ab-experiment-rag-tutorial.md) 计划即勾选路线图 152 条。下一篇 [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md) 落地 Parser 协议。
""",
    "pluggable-parser-splitter-embedder": """
## 28. 契约测试完整示例

```python
def test_parser_contract(parser, fixture_pdf):
    raw = parser.parse(fixture_pdf)
    assert raw.metadata.get("doc_id")
    assert len(raw.text.strip()) > 100

def test_splitter_contract(splitter, raw):
    chunks = splitter.split(raw)
    assert 1 <= len(chunks) <= 500
    ids = [c.metadata["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))

def test_embedder_contract(embedder):
    v = embedder.embed_texts(["测试句"])[0]
    assert len(v) == embedder.dimension
```

CI 对每个 REGISTRY 项跑一遍。失败阻断 merge。

## 29. manifest 与运维看板

看板展示：当前 `parser/splitter/embedder` 版本、chunk 总数、最近 job 耗时、失败文件数。与 [161 状态机](161.index-task-state-machine-tutorial.md) 联动。on-call 根据 manifest_id 回放问题索引。

## 30. 地基篇收束

Parser/Splitter/Embedder 三协议是数据入口地基，REGISTRY+契约+manifest 是工程化核心。LC 适配器保持薄。完成 REGISTRY≥2、CI 绿、与 [128](128.langchain-vectorstore-tutorial.md) 联调、wiki ADR 即勾选路线图 153 条。下一读 [137](137.pluggable-store-retriever-generator-tutorial.md)。
""",
}
