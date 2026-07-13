# -*- coding: utf-8 -*-
"""Large expansion blocks for batch 137-145 to reach >=5000 hanzi."""

EXPAND: dict[str, list[str]] = {
    "pluggable-store-retriever-generator": [
        """
## 附录 A：接口演进与版本策略

### A.1 从单体函数到三接口

早期 Mini-RAG 常见 `def rag(q): chunks=search(q); return llm(chunks,q)`。当团队引入 [93 混合检索](93.hybrid-search-tutorial.md) 与 [96 精排](96.bge-reranker-tutorial.md) 后，`search` 膨胀为三百行。三接口拆分的 **验收标准** 是：任意一个实现类 **单测不超过 150 行**，且 **构造注入** 可 Mock。

### A.2 接口版本号 semver

在 `myrag/interfaces.py` 顶行维护 `INTERFACE_VERSION = "1.0.0"`。破坏性变更（如 `retrieve` 增必填参数）升 major；新增可选参数升 minor。 [138 配置](138.config-driven-pipeline-tutorial.md) 的 `pipeline.version` 应 **依赖** 接口版本，避免「配置是新接口、代码是旧实现」。

### A.3 Fake 实现清单（单测必备）

| Fake | 行为 | 用于 |
|------|------|------|
| InMemoryStore | dict 存 Chunk | Store 单测 |
| FixedRetriever | 返回预设列表 | Generator 集成测 |
| EchoGenerator | 回显 messages 长度 | Pipeline 编排测 |

### A.4 与 C4 向量库选型对照

| 场景 | Store 实现 | 备注 |
|------|------------|------|
| PoC | [76 Chroma](76.chroma-vector-db-tutorial.md) | 本篇 §5 |
| 大规模 | [77 Milvus](77.milvus-tutorial.md) | 同接口不同后端 |
| SQL 栈 | [81 pgvector](81.pgvector-tutorial.md) | 事务友好 |
| 纯引擎 | [75 FAISS](75.faiss-ann-tutorial.md) | 自管 sidecar |

### A.5 HybridRetriever 装饰器草图

```python
class HybridRetriever:
    def __init__(self, dense: Retriever, sparse: Retriever, fusion_k: int = 10):
        self.dense, self.sparse, self.fusion_k = dense, sparse, fusion_k

    def retrieve(self, query: str, k: int = 5, filters=None) -> list[Chunk]:
        d = self.dense.retrieve(query, k=k * 2, filters=filters)
        s = self.sparse.retrieve(query, k=k * 2, filters=filters)
        return rrf_fuse(d, s, k=self.fusion_k)[:k]
```

**阅读顺序**：先 [93 Hybrid](93.hybrid-search-tutorial.md)，再 [94 RRF](94.rrf-fusion-tutorial.md)。工厂里 `retriever.class` 指向此类即可，**main 不改**。

### A.6 生成侧流式扩展

```python
class Generator(Protocol):
    def generate(self, messages: list[dict], **params) -> str: ...
    def generate_stream(self, messages: list[dict], **params): ...  # 可选
```

流式与 [116 SSE](116.sse-rag-streaming-tutorial.md) 对齐：`generate_stream` yield delta，**citations 仍由编排层** 在检索完成后下发，不要塞进 Generator。

### A.7 一周落地节奏

| 天 | 上午 | 下午 | 产出 |
|----|------|------|------|
| 周一 | 读 136+137 画三框 | 定义 Protocol | interfaces.py |
| 周二 | ChromaStore | Store 单测 | 绿色 CI |
| 周三 | DenseRetriever | 接 136 Embedder | retrieve 通 |
| 周四 | OpenAIGenerator | 接 110 模板 | 答案通 |
| 周五 | RagPipeline + DI | 十条手测 | wiki 一段 |

### A.8 面试追问十则

**问 1**：Store 与 VectorStore 在 LangChain 里是一回事吗？  
**答**：LC VectorStore 偏框架；本篇 Store 是 **你的域端口**，可用 LC 做适配器。

**问 2**：Retriever 能否调两个 Store？  
**答**：可以，Hybrid 常见；注意 filter 一致 [88](88.metadata-filter-retrieval-tutorial.md)。

**问 3**：Generator 要不要缓存？  
**答**：一般不缓存生成；可缓存 **检索结果** [68](68.embedding-cache-tutorial.md)。

**问 4**：如何做链路 trace？  
**答**：在 `RagPipeline.ask` 打 `trace_id`，分阶段记 latency——见 [147 LangSmith](147.langsmith-tracing-tutorial.md)。

**问 5**：多租户注入点？  
**答**：Store 构造注入 `tenant_id`；Retriever 透传 filters [89](89.multi-tenant-namespace-tutorial.md)。

**问 6**：错误处理谁负责？  
**答**：Store 抛存储异常；Retriever 可返回空列表；Generator 抛 API 异常；编排层转用户文案 [112](112.refusal-strategy-tutorial.md)。

**问 7**：和 135 框架取舍？  
**答**：[135](135.pipeline-vs-framework-tutorial.md) 讲何时用 LC；本篇讲 **自研芯**。

**问 8**：评测挂哪？  
**答**：对 `pipeline.ask` 输出跑 RAGAS [139-142](139.ragas-context-precision-tutorial.md)。

**问 9**：chunk 预算谁截？  
**答**：编排层或 `BudgetRetriever` 装饰器 [107](107.context-budget-tutorial.md)。

**问 10**：最小 PoC 交付？  
**答**：三接口 + §9 Pipeline + 三条 FAQ 手测 + 一种 filter。
""",
        """
## 附录 B：生产检查单与术语对照

### B.1 上线前 24 项检查（节选）

| # | 项 | 通过标准 |
|---|-----|----------|
| 1 | Store 持久化 | 重启后 count 不变 |
| 2 | Embedding 维度 | 与 [25](25.embedding-vector-tutorial.md) 一致 |
| 3 | collection 版本 | 换模型新 collection |
| 4 | Retriever filter | 与 [121 ACL](121.unauthorized-doc-filter-tutorial.md) 一致 |
| 5 | Generator temperature | 评测 0.1 生产可配置 |
| 6 | Prompt 版本 | 与 [110](110.rag-prompt-template-tutorial.md) 对齐 |
| 7 | 上下文预算 | 不超 [28](28.context-window-tutorial.md) |
| 8 | 空检索 | 走 [112 拒答](112.refusal-strategy-tutorial.md) |
| 9 | 引用 chunk_id | 与 [113](113.inline-citation-tutorial.md) 一致 |
| 10 | 单测 Fake | 核心路径覆盖 |
| 11 | 配置外置 | [138](138.config-driven-pipeline-tutorial.md) 就绪 |
| 12 | 日志 trace_id | 可串联 |
| 13 | 混合检索去重 | [106](106.retrieval-dedup-tutorial.md) |
| 14 | 精排延迟 | P95 可接受 |
| 15 | API 重试 | [69](69.embedding-retry-rate-limit-tutorial.md) |
| 16 | 多租户隔离 | 跨 tenant 搜不到 |
| 17 | 流式（若有） | [116 SSE](116.sse-rag-streaming-tutorial.md) |
| 18 | 安全过滤 | [122](122.content-safety-filter-tutorial.md) |
| 19 | 结构化输出（若有） | [123](123.structured-output-json-tutorial.md) |
| 20 | 工具调用（若有） | [124](124.function-calling-tool-use-tutorial.md) |
| 21 | 金标抽检 | [143](143.golden-dataset-tutorial.md) 十条 |
| 22 | faithfulness | [141](141.ragas-faithfulness-tutorial.md) 基线 |
| 23 | 文档 | wiki 插入点 |
| 24 | 回滚 | 旧配置可切回 |

### B.2 术语对照（扩展）

| 中文 | English | 备注 |
|------|---------|------|
| 装饰器检索器 | Decorator Retriever | Rerank/Budget 包装 |
| 工厂 | Factory | 读配置 new 对象 |
| 编排 | Orchestration | RagPipeline |
| 端口 | Port | 三接口 |
| 适配器 | Adapter | LC/Haystack 桥 |

### B.3 常见日志字段

`store.collection`、`retriever.class`、`generator.model`、`retrieval_k`、`chunk_ids[]`、`latency_ms.retrieve`、`latency_ms.generate`、`pipeline_version`。

### B.4 给未来自己的排障便签

**先查版本三元组**：索引版本、prompt 版本、pipeline 配置版本。Retriever 空结果优先查 filter 与 ACL，再查 k 与混合开关。Generator 胡编优先查 [141 faithfulness](141.ragas-faithfulness-tutorial.md) 与 temperature，不要先换模型。
""",
    ],
    "config-driven-pipeline": [
        """
## 附录 A：配置合并与多环境

### A.1 Overlay 合并示例

```python
def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

cfg = deep_merge(load_yaml("pipeline.yaml"), load_yaml("pipeline.prod.yaml"))
```

### A.2 环境矩阵

| 环境 | 文件 | k | 模型 |
|------|------|---|------|
| dev | pipeline.yaml | 5 | 便宜模型 |
| staging | +staging overlay | 8 | 与 prod 同 |
| prod | +prod overlay | 8 | 生产模型 |

### A.3 配置变更评审模板

1. 变更动机（算法/成本/bug）；2. diff 片段；3. [144 回归](144.regression-test-set-tutorial.md) 结果；4. 回滚命令；5. 负责人签字。

### A.4 与 [154 参数版本](154.param-version-management-tutorial.md) 联动

`pipeline.version` 进入 Git tag；Docker 镜像 label `RAG_PIPELINE_VERSION`；Langfuse metadata 同名。

### A.5 动态 reload 风险

热更新配置时 **in-flight 请求** 完成旧配置；新请求用新配置；连接池（Chroma client）可能需重建——PoC 可重启进程代替热更。

### A.6 配置即文档

在 YAML 旁写 `pipeline.yaml.example` 进仓库；敏感项用 `CHANGEME` 占位；README 链到 [137 接口](137.pluggable-store-retriever-generator-tutorial.md) 类名表。

### A.7 面试题

**问**：配置驱动最大坑？  
**答**：双源默认值；解决：代码无默认，缺字段校验失败。

**问**：如何做 A/B？  
**答**：两套 yaml + [153 实验](153.ab-experiment-rag-tutorial.md) 分流，或 feature flag 选 `retriever.class`。
""",
        """
## 附录 B：Schema 与 CLI

### B.1 Pydantic 全模型示例

```python
class ComponentCfg(BaseModel):
    class_: str = Field(alias="class")
    args: dict = Field(default_factory=dict)

class RootCfg(BaseModel):
    version: str
    pipeline: dict
    store: ComponentCfg
    retriever: ComponentCfg
    generator: ComponentCfg
```

### B.2 CLI 子命令

`rag pipeline validate` / `rag pipeline print` / `rag ask -c config/prod.yaml -q "..."`  
统一入口降低 **运维记错配置文件** 概率。

### B.3 与 Docker Compose

```yaml
services:
  rag-api:
    environment:
      - RAG_CONFIG=/app/config/pipeline.prod.yaml
    volumes:
      - ./config:/app/config:ro
```

### B.4 配置漂移检测

每日 cron：hash 线上生效配置 vs Git main；不一致告警——常见于 **手工改 prod 未回写**。

### B.5 一周节奏

周一 Schema；周二工厂；周三 overlay；周四 CI validate；周五 接 [143 金标](143.golden-dataset-tutorial.md) 评测绑定 version。
""",
    ],
    "ragas-context-precision": [
        """
## 附录 A：Precision 深度

### A.1 手工估算练习

三条 contexts：R1 相关、R2 无关、R3 相关。若顺序 R2,R1,R3，Precision@3 应低于 R1,R3,R2。团队白板算一次，再跑 RAGAS 对照。

### A.2 分场景 baseline 表（示例）

| 场景 | 目标 Precision@5 |
|------|------------------|
| HR 制度 | ≥0.75 |
| IT FAQ | ≥0.70 |
| 法务 | ≥0.80 |

### A.3 与 [99 阈值](99.score-threshold-tutorial.md)

向量分低但 Precision 高——可能 **相关但置信度低**；阈值过严会丢相关项，拉低 Recall [140](140.ragas-context-recall-tutorial.md)。

### A.4 去重对 Precision 的影响

[106 去重](106.retrieval-dedup-tutorial.md) 去掉重复 FAQ 后，前排槽位让给不同相关段，Precision 常 **升**。

### A.5 评测报告模板

`mean`、`p10`、`by_tag`、`worst_5_ids` 附 contexts 快照——方便对接 [151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md) 工单。

### A.6 面试

**问**：Precision 高 Recall 低？  
**答**：收紧前排或 k 太小；升 k + rerank 再压噪声。
""",
        """
## 附录 B：与全链联调

### B.1 检索链检查顺序

[100 改写](100.query-rewriting-tutorial.md) → [93 混合](93.hybrid-search-tutorial.md) → [94 RRF](94.rrf-fusion-tutorial.md) → [96 精排](96.bge-reranker-tutorial.md) → [106 去重](106.retrieval-dedup-tutorial.md) → [107 预算](107.context-budget-tutorial.md) → 进 [111 注入](111.context-injection-format-tutorial.md)。Precision 在 **精排后** 量才贴用户所见。

### B.2 多语言

[70 混合语言](70.mixed-language-embedding-tutorial.md) 场景：无关项可能是 **语言不匹配** 的 chunk，而非语义无关——标注时分开 tag。

### B.3 成本

RAGAS Precision 调 LLM 判相关；批量用 [143](143.golden-dataset-tutorial.md) 子集 + 生产抽样。

### B.4 作业

手标 10 条 → 跑分 → 调 rerank → 再跑 → 写 delta wiki。
""",
    ],
    "ragas-context-recall": [
        """
## 附录 A：Recall 深度

### A.1 部分命中算例

金标需要 chunk A、B；检索到 A 未到 B → Recall 约 0.5。不要与 Hit@1 混淆。

### A.2 k 扫描实验记录表

| k | Recall@k | Precision@k | P95 延迟 |
|---|----------|-------------|----------|
| 5 | | | |
| 10 | | | |
| 20 | | | |

拐点写入 [138 配置](138.config-driven-pipeline-tutorial.md) 的 `retriever_k`。

### A.3 切块实验

同一文档用 [57 固定](57.fixed-size-chunking-tutorial.md) vs [62 结构](62.structure-aware-chunking-tutorial.md) 切块，Recall 可差 0.15+——Recall 低 **先查切块** 再查模型。

### A.4 增量索引

[49 增量](49.incremental-update-tutorial.md) 漏同步会导致 **新段搜不到**——Recall 断崖式下跌且只影响新 FAQ。

### A.5 与 Bad Case

[151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md) 工单应附 Recall 评测截图与 `relevant_chunk_ids`。

### A.6 面试

**问**：Recall 满分能上线吗？  
**答**：不能；还要看 Precision 与 [141 Faithfulness](141.ragas-faithfulness-tutorial.md)。
""",
        """
## 附录 B：混合与过滤

### B.1 BM25 救 Recall 的典型 query

含 **内部代号、SKU、条款编号**——[92 Sparse](92.sparse-retrieval-rag-tutorial.md) 强项。

### B.2 filter 误杀案例

`doc_id=handbook-v2` 但金标在 v3——Recall 0；对齐 [48 文档版本](48.doc-versioning-tutorial.md)。

### B.3 ACL

[121 越权](121.unauthorized-doc-filter-tutorial.md) 正确时 Recall 对 **无权用户** 低是 **预期**——评测要用 **有权身份** 金标集。

### B.4 一周作业

建 10 条 Recall 敏感题；扫 k；扫 hybrid；写推荐配置进 yaml。
""",
    ],
    "ragas-faithfulness": [
        """
## 附录 A：Faithfulness 工程深化

### A.1 判据 rubric 示例（人工）

| 等级 | 定义 |
|------|------|
| 支持 | 上下文直接蕴含 |
| 弱支持 | 需简单推理 |
| 不支持 | 无依据或矛盾 |
| 拒答 | 不算 claim |

与 RAGAS 自动分对齐时，抽 30 条人工标定 **校准阈值**。

### A.2 数字与日期敏感题

年假天数、税率、截止日期——**faithfulness-critical** 标签进 [143 金标](143.golden-dataset-tutorial.md)；回归集 **必含** [144](144.regression-test-set-tutorial.md)。

### A.3 多文档冲突

两 chunk 说法矛盾——faithfulness 对 **模型择一** 可能仍高（忠实于其一），但 **业务错**。需 [48 版本](48.doc-versioning-tutorial.md) 清掉旧版 + 资料冲突检测。

### A.4 Prompt 消融

| 版本 | system 要点 | faithfulness |
|------|-------------|--------------|
| v1 | 无约束 | 基线 |
| v2 | 仅据资料 | +Δ |
| v3 | v2+引用格式 [113] | +Δ2 |
| v4 | v3+拒答 [112] | 拒答率↑ |

### A.5 与 [152 胡编归因](152.bad-case-hallucination-tutorial.md)

unsupported claim 聚类 → 改 prompt / 降 temperature / 加 rerank / 补金标。

### A.6 长上下文

[108 重排](108.long-context-reorder-tutorial.md) 把最相关放首尾，减少 **中间遗忘** 导致的假 unsupported。

### A.7 工具与 JSON

[124 工具](124.function-calling-tool-use-tutorial.md) 返回写入 contexts 再评；[123 JSON](123.structured-output-json-tutorial.md) 字段值仍逐字段 claim 审计。

### A.8 组织 KPI

`faithfulness_p50 ≥ 0.85`（制度 Bot 示例）；周环比下降 >0.03 触发复盘。

### A.9 面试十则（节选）

**问**：Faithfulness vs Accuracy？  
**答**：前者对上下文，后者对真理；错库可以高 faithfulness。

**问**：最贵环节？  
**答**：claim 拆分 + NLI 多次 LLM 调用；用回归集全量 + 生产抽样。
""",
        """
## 附录 B：Runbook 扩展与案例库

### B.1 案例 1：检索对、数字错

Recall 1.0，faithfulness 0.4，答案写 15 天实际 10 天 → [152 生成胡编](152.bad-case-hallucination-tutorial.md)；杠杆：temperature、强调数字原文引用。

### B.2 案例 2：拒答被判低分

配置 `expect_refusal` 跳过 faithfulness；统计 **拒答准确率** 单独指标。

### B.3 案例 3：多轮指代

「那病假呢？」——用 [120](120.coreference-resolution-tutorial.md) 展开问题再评。

### B.4 生产采样 pipeline

```text
1% 流量 → 存 contexts+answer → 异步 faithfulness → 低分告警
```

### B.5 与 [147 LangSmith](147.langsmith-tracing-tutorial.md)

span `faithfulness_audit` 存 `unsupported[]`；点击 trace 跳到原文 chunk。

### B.6 30 分钟作业

跑 §9；改坏一条 prompt；看 faithfulness delta；写一段 Runbook。

### B.7 术语扩展

Entailment、NLI、Claim、Grounding、Hallucination、Citation-Faithfulness。

### B.8 合规提示

faithfulness 高 **不等于** 法律意见正确；对外法务 Bot 仍要人工免责与 [112 拒答](112.refusal-strategy-tutorial.md)。
""",
    ],
    "ragas-answer-relevancy": [
        """
## 附录 A：Relevancy 深化

### A.1 冗长答案实验

同一 faithfulness 下，删废话前后 Relevancy 对比——证明 [110 Prompt](110.rag-prompt-template-tutorial.md)「简洁」槽位的价值。

### A.2 权重模板

制度 Bot：Faithfulness 0.35 / Recall 0.25 / Precision 0.20 / Relevancy 0.20。写作 Bot 可调 Relevancy。

### A.3 与满意度

抽 20 条让人打「是否答非所问」，与 Relevancy 算相关；<0.6 换 Embedding 或改反向问题 prompt。

### A.4 多意图 query

「年假和病假各多少？」——Relevancy 要求 **两点都答**；单点 faithfulness 不够。

### A.5 面试

**问**：四指标最重要？  
**答**：制度场景 Faithfulness+Recall；客服体验加 Relevancy。
""",
        """
## 附录 B：四指标同表

### B.1 CSV 列

`id, context_precision, context_recall, faithfulness, answer_relevancy, pipeline_version, ts`

### B.2 可视化

雷达图四轴；发版叠加对比 **勿跨 dataset_version**。

### B.3 与 [145 DeepEval](145.deepeval-tutorial.md)

Relevancy 思想同；数值不比。

### B.4 作业

同一 10 条跑四指标；找「高 F 低 R」一条分析。
""",
    ],
    "golden-dataset": [
        """
## 附录 A：金标工程

### A.1 标注员手册摘要

1. question 用用户口语；2. ground_truth 只含资料可支持内容；3. relevant_chunk_ids 最小充分；4. 不确定标 `needs_review`；5. 冲突送法务。

### A.2 难度分级

easy：单 chunk；medium：2 chunk 或需推理；hard：多跳 [104]、多轮 [118]、ACL [121]。

### A.3 标签体系

`hr`、`it`、`legal`、`refusal`、`acl`、`multihop`、`faithfulness-critical`。

### A.4 合成数据

无真实日志时，从 [62 结构切块](62.structure-aware-chunking-tutorial.md) 标题生成 question——**仍需人审**。

### A.5 与索引版本绑定

`dataset_version` + `kb_version` 二元组写入每次评测报告；换索引 **major bump**。

### A.6 泄漏防范

金标 **不进** 训练微调集；仓库私有；CI 用脱敏子集。

### A.7 生长 OKR

Q1：50 条；Q2：150 条；每周从 trace 采纳 ≥3 条。

### A.8 面试

**问**：金标谁拥有？  
**答**：算法+业务共管；工程维护 schema 与 CI。
""",
        """
## 附录 B：CLI 与治理扩展

### B.1 validate 子命令

检查 chunk_id 在索引存在；`expect_refusal` 与 `ground_truth` 互斥；id 唯一。

### B.2 报告 HTML

四指标表 + 最差 10 条可点击 trace（若有 [148 Langfuse](148.langfuse-observability-tutorial.md)）。

### B.3 季度审计

删过时题标 `deprecated`；合并重复；更新 ground_truth 跟 [48 版本](48.doc-versioning-tutorial.md)。

### B.4 与人工评测 [155](155.human-evaluation-rag-tutorial.md)

金标是自动评测地基；人工评测是 **校准与抽验**。

### B.5 30 分钟作业

建 repo `golden/`；写 5 条；跑 eval CLI；贴报告截图 wiki。
""",
    ],
    "regression-test-set": [
        """
## 附录 A：回归集工程

### A.1 文件布局

```text
regression/
  core.jsonl      # PR 必跑
  smoke.jsonl     # 5 条极速
golden/
  hr-full.jsonl   # nightly
```

### A.2 baseline 缓存

main 分支 CI 成功后上传 `baseline-scores.json`；PR 算 delta。

### A.3 flaky 登记

`regression/flaky.md` 记录题 id、原因、临时 waiver 到期日。

### A.4 P0 bug 入库流程

工单关闭 → 加 regression 用例 → 链 commit id → 永不删（除非功能废弃）。

### A.5 通知

CI 失败 Slack 带 `worst_question` 与 `delta_faithfulness`。

### A.6 面试

**问**：回归集多大？  
**答**：15～30，<5 分钟；不是金标全集。
""",
        """
## 附录 B：阈值调参

### B.1 初次上线

宽阈值防误杀；稳定后收紧；每次收紧要 **changelog**。

### B.2 分指标阻断

faithfulness 与 recall **可不同阈值**；产品定哪条阻断 merge。

### B.3 nightly 全量

不阻断 PR；跌超 0.1 建 incident。

### B.4 与 [154 版本](154.param-version-management-tutorial.md)

回归失败回滚 **配置版本** 优先于回滚代码。

### B.5 作业

从 [143](143.golden-dataset-tutorial.md) 挑 15 条建 `core.jsonl`；写 GitHub Actions 骨架。
""",
    ],
    "deepeval": [
        """
## 附录 A：DeepEval 补充

### A.1 安装与初始化

`pip install deepeval`；配置 `OPENAI_API_KEY` 或 DeepEval 支持的 provider；阅读官方 confest 文档。

### A.2 G-Eval 了解

自定义 rubric 评「礼貌度」等——**了解即可**；制度 Bot 优先 RAGAS 四指标 [139-142](139.ragas-context-precision-tutorial.md)。

### A.3 与 CI 缓存

pytest 并行时注意 API 限流 [69](69.embedding-retry-rate-limit-tutorial.md)；`deepeval test run -n 2`。

### A.4 迁移路径

已有 RAGAS 报表 → 保持 RAGAS 主；仅 **新 pytest 用例** 用 DeepEval 断言。

### A.5 面试

**问**：为何了解篇？  
**答**：知道 pytest 派备选；主线仍是 [141 RAGAS](141.ragas-faithfulness-tutorial.md)。
""",
        """
## 附录 B：对照与选型

### B.1 功能矩阵

| 能力 | RAGAS | DeepEval |
|------|-------|----------|
| 数据集 evaluate | 强 | 有 |
| pytest | 需封装 | 原生 |
| 社区示例 | RAG 多 | LLM 泛 |

### B.2 成本同一量级

均 LLM-as-judge；计入 [27 计费](27.token-counting-billing-tutorial.md)。

### B.3 下一步

[146 TruLens](146.trulens-tutorial.md)、[147 LangSmith](147.langsmith-tracing-tutorial.md) 观测；[148 Langfuse](148.langfuse-observability-tutorial.md)。

### B.4 作业

安装 → 跑 §9 单测 → 填 §4 对照表 → 团队决定主标尺。
""",
    ],
}
