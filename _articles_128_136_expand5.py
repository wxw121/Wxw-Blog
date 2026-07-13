# -*- coding: utf-8 -*-
"""Fifth-pass expansions for 128-136 — sections 25-27, final top-up."""

EXPANSIONS5 = {
    "langchain-vectorstore": """
## 25. 本篇收束与路线图勾选

完成 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **第 145 条** 时，在团队 wiki 勾选：Chroma/FAISS 双后端、chunk_id 幂等、ACL filter、as_retriever+LCEL、manifest 规范、检索 span 字段、§8 先错对对演示视频或脚本链接。下一步必读 [129 Loader](129.langchain-document-loader-tutorial.md) 与 [130 Splitter](130.langchain-text-splitter-tutorial.md)，把数据入口 metadata 钉死后再扩库。
""",
    "langchain-document-loader": """
## 25. 与 Confluence/Git 的落地清单

Confluence：申请 API token → 按 space 导出 → 落盘 md/html → DirectoryLoader → Schema 校验 → JSONL 审计。Git：CI on push 打 tarball artifact → ingest job 拉 artifact → `doc_id=repo:path:commit` 便于 [48 版本](48.doc-versioning-tutorial.md) 回溯。每周报表：新增/更新/删除文件数、空文本率、平均页数、ingest 耗时 P95。与 [161 状态机](161.index-task-state-machine-tutorial.md) 状态 `loaded` 对齐。

## 26. 团队评审话术与新人 onboarding

新人第一周任务：用 TextLoader/PyPDFLoader/DirectoryLoader 各写 10 行脚本；故意制造 encoding 与扫描件空文本；修复并写 wiki 条目。评审会上用「文件→Document→metadata→Splitter」四格图讲解，强调 Loader **不负责切块与 embed**。对接法务说明：Loader 输出可含 PII，需脱敏字段清单与访问控制。

## 27. 深度场景 FAQ 补充

**Q：邮件 eml 怎么 load？** 先解析 eml 取正文与附件路径，附件递归 Loader。**Q：数据库 BLOB 字段？** 自定义 Loader 读 BLOB 写临时文件再 Parser。**Q：密码保护 PDF？** 解密服务前置，Loader 只读已解密文件。**Q：多语言文件混目录？** metadata.lang + 按语言选 Parser/Splitter（[70](70.mixed-language-embedding-tutorial.md)）。**Q：Loader 性能瓶颈？** IO 并行 + 增量 hash，embed 才是大头（[67](67.embedding-batching-tutorial.md)）。
""",
    "langchain-text-splitter": """
## 25. 企业制度库切块案例 walkthrough

以「员工差旅制度」为例：Loader 得 12 页 PDF 文本 → MarkdownHeader 按「第一章」粗切 → Recursive 500/80 细切 → 每 chunk metadata 含 `section=差旅标准`、`chunk_id=travel:v3:c012` → [128 VectorStore](128.langchain-vectorstore-tutorial.md) 入库。金标问「出差住宿上限」应命中含「住宿」段落的 chunk；若命中页眉「内部资料」chunk，说明 [46 清洗](46.text-cleaning-tutorial.md) 或分隔符要调。把此 walkthrough 存入 [144 回归](144.regression-test-set-tutorial.md)。

## 26. Splitter 参数版本表模板

| version | size | overlap | separators_preset | 生效日 | 备注 |
|---------|------|---------|-------------------|--------|------|
| v1 | 400 | 50 | zh_default | 2026-01 | 初版 |
| v2 | 500 | 80 | zh_default | 2026-04 | 金标+3% Recall |

变更 v2 时新建 collection `handbook_bge_v2`，跑完回归再切指针（[154](154.param-version-management-tutorial.md)）。

## 27. 深度 FAQ 补充

**Q：能否按 token 动态切？** 可以，用 TokenTextSplitter 并设 max_tokens 低于 embed 上限。**Q：标题单独成 chunk 好吗？** 短标题 chunk 检索噪声大，宜与首段合并（[62 结构感知](62.structure-aware-chunking-tutorial.md)）。**Q：Splitter 并行？** 文档级并行可以，单 doc 内顺序切。**Q：如何 diff 两次切块？** 按 chunk_id 或 content_hash 对比集合差异。**Q：与 [150 bad case](150.bad-case-chunking-tutorial.md)？** 断裂样例入库回归集。
""",
    "llamaindex-index-types": """
## 25. 两小时学习检查单（了解即可）

- [ ] 说出 VectorStoreIndex vs SummaryIndex 适用边界  
- [ ] 画出 Document→Node→Index 关系  
- [ ] 跑通 from_documents 小 demo  
- [ ] 填 LC 映射表（§10）  
- [ ] 说明为何不生产双栈  
- [ ] 指出 storage_context 对应 Chroma 哪概念  

## 26. 开源阅读指南

读 LlamaIndex 示例时标色：`VectorStoreIndex`、`StorageContext`、`as_query_engine` 三处。对照 [128](128.langchain-vectorstore-tutorial.md) 与 [132 Query Engine](132.llamaindex-query-engine-tutorial.md) 笔记。不要复制 LI ingest 进生产，只借概念。

## 27. FAQ 补充

**Q：LI 索引构建失败？** 看 embed 模型与 vector_store 维度。**Q：Node 关系边？** 图索引用，向量主路径可忽略。**Q：要装 llama-index-integrations-chroma 吗？** 视版本，以官方 doc 为准。**Q：时间分配？** 主线 LC 70%，LI 了解 30%。**Q：面试陷阱？** 别说「LI 比 LC 强」，说场景与映射。
""",
    "llamaindex-query-engine": """
## 25. Query Engine 最小实验步骤（了解）

1. `pip install llama-index`；2. 三篇 Document；3. `VectorStoreIndex.from_documents`；4. `query_engine = index.as_query_engine(similarity_top_k=3)`；5. `print(response)` 与 `response.source_nodes`；6. 画与 LCEL 等价图。总计 ≤90 分钟，然后回到 [126 LCEL](126.langchain-lcel-tutorial.md) 实现同题。

## 26. 与 RAGAS、观测的接口

评测时不论 LI 还是 LC，**进 prompt 的 contexts** 用于 [139-142 RAGAS](141.ragas-faithfulness-tutorial.md)。Query Engine 的 source_nodes 应能导出为 `chunk_id` 列表写入 trace（[147](147.langsmith-tracing-tutorial.md)）。了解 LI 响应形状即可对接评测管道。

## 27. FAQ 补充

**Q：query_engine 能加 rerank 吗？** 可以 postprocessor 或换 retriever；LC 侧更常见显式 rerank 节点。**Q：异步批量 query？** `aquery` 或任务队列；注意速率 [169](169.rate-limiting-api-tutorial.md)。**Q：自定义 prompt？** 可，但企业常用 [110 模板](110.rag-prompt-template-tutorial.md) 统一。**Q：为何不用 LI 省代码？** 可观测性、ACL、混合检索细粒度在 LC 更直观。**Q：下一步？** [133 Agent](133.llamaindex-agent-tutorial.md) 了解即可。
""",
    "llamaindex-agent": """
## 25. Agent 最小实验（了解）

`ReActAgent.from_tools([QueryEngineTool...], llm=..., verbose=True)` 跑 3 个多跳问题，记录迭代次数与 token。设 `max_iterations=3` 观察截断行为。对比固定 [104 多跳](104.multi-hop-retrieval-tutorial.md) 管道延迟。实验报告一页纸即可，勿上生产。

## 26. 治理 checklist

- [ ] max_iterations 与总 timeout  
- [ ] 每 tool 内 ACL  
- [ ] tool 参数 schema 校验  
- [ ] trace 记 tool_name 与 chunk_ids  
- [ ] 失败走 [112 拒答](112.refusal-strategy-tutorial.md)  
- [ ] 对外 API 禁用 Agent 或单独灰度  

## 27. FAQ 补充

**Q：Agent 与 ChatGPT 插件？** 同构循环，治理要求相同。**Q：多 Agent 协作？** 超纲，了解即可。**Q：如何测 Agent？** 模拟工具 mock，别依赖 live LLM 在 CI。**Q：成本监控？** [148 Langfuse](148.langfuse-observability-tutorial.md) 按 session 汇总。**Q：主线回归？** [127 固定 Retriever](127.langchain-retriever-tutorial.md)。
""",
    "haystack-pipeline": """
## 25. 手绘作业详解（了解）

纸面两张图：ingest（Loader→Preprocessor→Embedder→DocumentStore）与 query（Query→Retriever→Ranker→Prompt→Generator）。旁注 LC 等价组件名。标红 [94 RRF](94.rrf-fusion-tutorial.md) 汇合点与 [121 ACL](121.unauthorized-doc-filter-tutorial.md) 过滤位置。拍照存 wiki，作为 [135](135.pipeline-vs-framework-tutorial.md) 工作坊附件。

## 26. 从 Haystack 迁移到 LCEL 的对照

| Haystack | LangChain |
|----------|-----------|
| Pipeline.connect | LCEL `|` |
| @component | RunnableLambda / 自定义 Runnable |
| DocumentStore | VectorStore |
| Joiner | EnsembleRetriever + fusion |

了解即可，不必真迁移。

## 27. FAQ 补充

**Q：Haystack 许可？** Apache 2.0，但仍要评估维护成本。**Q：与 deepset 云？** 了解即可，自托管对照 [76](76.chroma-vector-db-tutorial.md)。**Q：Pipeline 单元测试？** 每 component 单独 run，值得借鉴。**Q：为何学 Haystack？** 学显式 DAG 与评审图。**Q：时间盒？** 4h 阅读+手绘，不引依赖。
""",
    "pipeline-vs-framework": """
## 25. ARCHITECTURE.md 一页模板

1. **目标与边界**（QPS、合规级别）；2. **分层表**（本篇 §9）；3. **数据契约**（metadata Schema）；4. **索引版本策略**；5. **观测与评测门禁**；6. **回滚预案**；7. **负责人 RACI**。每季度回顾，与 [154 参数版本](154.param-version-management-tutorial.md) 同步。

## 26. 冲突案例复盘模板

记录「升级 LC 断链」「双框架并行导致 hit_ids 不一致」等真实事件：根因、修复、防再发（门禁/培训）。与 [149-152 bad case](149.bad-case-parsing-tutorial.md) 系列放同一 wiki 空间，新人 onboarding 必读。

## 27. FAQ 补充

**Q：老板要最快 demo？** LC+Chroma，并行写 Parser 协议。**Q：被 vendor 绑死？** 导出 chunk+金标+manifest。**Q：开源框架能商用吗？** 看许可与合规审查。**Q：团队争论不休？** 用 [143 金标](143.golden-dataset-tutorial.md) 数据决策。**Q：何时全自研？** 极少；多数混合。
""",
    "pluggable-parser-splitter-embedder": """
## 25. 100 行全栈 demo 讲解稿

面向评审：展示 `build_pipeline(yaml)` → 遍历 fixtures → manifest.json → 一条 query 的 chunk_id 命中。强调 **三协议可单测、LC 仅适配器、manifest 钉版本、换 embed 新 collection**。配合 [137 Store](137.pluggable-store-retriever-generator-tutorial.md) 预告下游三件套。

## 26. REGISTRY 演进时间表（示例）

| 周 | 里程碑 |
|----|--------|
| 1 | pymupdf + recursive + fake embed + 契约测试 |
| 4 | plain + md_header + bge_small + CI 绿 |
| 12 | pdfplumber A/B + HTTP Parser 适配 |
| 24 | 全链 manifest + [144 回归](144.regression-test-set-tutorial.md) 挂钩 |

## 27. FAQ 补充

**Q：Parser 返回多 RawDocument？** 可以，Splitter 逐条切。**Q：Embedder 异步 GPU 队列？** embed_texts 内 RPC 批处理。**Q：Breaking 变更？** schema_version major + 重建通知。**Q：与 [138 配置](138.config-driven-pipeline-tutorial.md)？** yaml 键必须 REGISTRY 存在。**Q：完成 136 后读什么？** [137](137.pluggable-store-retriever-generator-tutorial.md) + [138](138.config-driven-pipeline-tutorial.md)。
""",
}
