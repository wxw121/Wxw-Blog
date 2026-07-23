# -*- coding: utf-8 -*-
"""Third-pass expansions for batch 137-145 (>=5000 hanzi guarantee)."""

EXPAND3: dict[str, str] = {
    "pluggable-store-retriever-generator": """
## 附录 C：端到端联调手册（与 93–112 全链）

### C.1 链路白板（必读）

从用户 query 到 answer，标注每一步 **接口归属**：

```text
用户 query
  → [109 可选 Query 增强]
  → Retriever.retrieve  ← 本篇
      内：Embedder [136]、Store.search、可选 Hybrid [93]、Rerank [96]、Dedup [106]
  → 编排：Budget [107]、Reorder [108]
  → build_messages [110][111]
  → Generator.generate  ← 本篇
  → 引用 [113]、流式 [116]、安全 [122]
```

在白板旁贴三条便利贴：**版本号**、**trace_id**、**tenant_id**。

### C.2 十条手测用例模板

| id | question | 期望 |
|----|----------|------|
| T1 | 制度 FAQ | 有引用 |
| T2 | 资料外问题 | 拒答 [112] |
| T3 | 无权 doc | 空/拒答 [121] |
| T4 | 含 SKU | 混合检索命中 [93] |
| T5 | 长问题 | 预算内 [107] |
| T6 | 英文问中文库 | [70] |
| T7 | 多轮 follow-up | 需 pipeline 支持 history |
| T8 | 敏感词 | [122] |
| T9 | 数字题 | 对齐原文 |
| T10 | 重复 chunk | 去重后 [106] |

每条记录 `chunk_ids`、`latency`、`pipeline_version`。

### C.3 Store 批量 upsert 与幂等

```python
def ingest_chunks(store: VectorStore, chunks: list[Chunk], batch: int = 64):
    for i in range(0, len(chunks), batch):
        store.upsert(chunks[i : i + batch])
```

`chunk_id` 稳定则 upsert 幂等——对齐 [51 chunk_id](51.metadata-chunk-id-tutorial.md) 与 [162 幂等索引](162.idempotent-reindex-tutorial.md)（路线图 F 轨）。

### C.4 Retriever 装饰器栈

```text
LoggedRetriever(
  BudgetRetriever(
    RerankRetriever(
      HybridRetriever(dense, sparse)
    )
  )
)
```

外层记日志 [147]；Budget 控 [28]；Rerank 用 [96]；Hybrid 用 [93][94]。**组装顺序** 影响延迟与指标，写入配置 [138]。

### C.5 Generator 多模型路由（前瞻）

```python
class RoutingGenerator:
    def __init__(self, cheap: Generator, strong: Generator, router):
        self.cheap, self.strong, self.router = cheap, strong, router

    def generate(self, messages, **params):
        g = self.strong if self.router.is_hard(messages) else self.cheap
        return g.generate(messages, **params)
```

与 [168 多模型路由](168.multi-model-routing-tutorial.md) 思路一致；配置里写两个 `generator` 槽扩展。

### C.6 错误码约定

| code | 含义 | 用户文案 |
|------|------|----------|
| RETRIEVAL_EMPTY | 无 chunk | [112] 资料不足 |
| GENERATION_TIMEOUT | 超时 | 请稍后重试 |
| STORE_UNAVAILABLE | 库不可用 | 维护中 |
| SAFETY_BLOCK | 安全 | [122] |

### C.7 性能预算（PoC 参考）

| 阶段 | P95 ms |
|------|--------|
| retrieve | 200–800 |
| generate | 1500–8000 |
| 总计 | <10s 可接受交互 |

### C.8 文档交付清单

- interfaces.py 三 Protocol  
- chroma_store.py / dense_retriever.py / openai_generator.py  
- pipeline.py 编排  
- config/pipeline.yaml 示例  
- tests/test_pipeline_fake.py  
- wiki：插入点与版本策略  
- 十条手测表  

### C.9 系列小结

本篇与 [136](136.pluggable-parser-splitter-embedder-tutorial.md) 成对：**上游三件套 + 下游三插头**，中间 [138 配置](138.config-driven-pipeline-tutorial.md) 拧紧，后面 [139–145](139.ragas-context-precision-tutorial.md) 验收。初学者勿跳过 [75][76] 直接抄接口——不懂 ANN 与 collection，接口背后排障会盲。

### C.10 自测题

1. 画出三接口数据流。  
2. 为何 Generator 不能调 Store？  
3. Hybrid 放在哪一层？  
4. Fake Retriever 测什么？  
5. 与 127 如何共存？  
答案见正文 §4、§6、§8、§9、§10。
""",
    "config-driven-pipeline": """
## 附录 C：企业配置治理

### C.1 配置仓库布局

```text
config/
  pipeline.schema.json
  pipeline.yaml
  pipeline.staging.yaml
  pipeline.prod.yaml
  components/   # 可复用片段
    chroma-store.yaml
    hybrid-retriever.yaml
```

### C.2 JSON Schema 片段

定义 `store.class` 枚举白名单：`myrag.stores.ChromaVectorStore`、`myrag.stores.PgVectorStore`……禁止任意 import 路径。

### C.3 GitOps 流程

PR 改 yaml → CI validate + [144 回归](144.regression-test-set-tutorial.md) → merge → ArgoCD/脚本推送 prod → 记 `config_hash` 到 [147 trace](147.langsmith-tracing-tutorial.md)。

### C.4 秘密管理

| 项 | 存储 |
|----|------|
| api_key | Vault / K8s Secret |
| chroma path | ConfigMap |
| model 名 | yaml |

### C.5 与全链参数对照表

| yaml 键 | 影响指标 | 关联篇 |
|---------|----------|--------|
| retriever_k | Recall/Precision | 98,140,139 |
| hybrid.enabled | Recall | 93 |
| rerank.top | Precision | 96 |
| generator.temperature | Faithfulness | 29,141 |
| max_context_tokens | Faithfulness | 28,107 |

### C.6 回滚演练

每季度演练：prod 配置回滚上一 `version`；验证 [144] 恢复；记录 RTO。

### C.7 配置文档化

每个键在 `pipeline.yaml.example` 旁用中文注释 **调大/调小的副作用**——比 wiki 更不易漂移。

### C.8 面试扩展

**问**：配置驱动 vs 代码驱动 A/B？  
**答**：配置适合参数与类切换；复杂逻辑仍代码，用 feature flag 选配置路径 [153]。

### C.9 自测

写出 dev→prod overlay merge 伪代码；列出 validate 失败三种原因。
""",
    "ragas-context-precision": """
## 附录 C：Precision 实验笔记本

### C.1 实验登记模板

| 日期 | 变更 | Precision Δ | Recall Δ | 备注 |
|------|------|-------------|----------|------|
| | rerank on | | | |

### C.2 与 MMR [105] 联调

MMR 降相似重复 → 前排多样性升 → Precision 可能升而 Recall 微降——记录 trade-off 曲线。

### C.3 与 Long Context [108]

重排后 Precision 升；测 faithfulness [141] 是否同步升。

### C.4 分 doc_type 报表

`handbook` vs `faq` vs `ticket` 分表——避免均值掩盖单类崩溃。

### C.5 标注质量回流

低 Precision 样本回流 [143 金标](143.golden-dataset-tutorial.md) 修正 relevant 标错。

### C.6 工具链

`python -m eval.precision --dataset golden/hr.jsonl --config config/pipeline.yaml -o reports/precision.json`

### C.7 系列位置

Precision 是 **检索排序质量** 尺；别用它衡量生成——那是 [141](141.ragas-faithfulness-tutorial.md)。

### C.8 自测

手算 3 条排序的 Precision 直觉；解释 rerank 为何常升 Precision。
""",
    "ragas-context-recall": """
## 附录 C：Recall 攻坚手册

### C.1 周会 agenda

1. Recall P50 趋势；2. 新增低 Recall 题；3. 切块/索引/action items。

### C.2 Embedding 域适配

[71 域评测](71.domain-embedding-evaluation-tutorial.md) 不过则 Recall 上限低——考虑微调 [73](73.embedding-finetune-tutorial.md)。

### C.3 Query 侧杠杆

[100 改写](100.query-rewriting-tutorial.md)、[101 多 query](101.multi-query-retrieval-tutorial.md)、[102 HyDE](102.hyde-tutorial.md) 逐个 ablation，记录 Recall delta。

### C.4 多跳 [104]

金标 relevant 跨跳时，Recall 定义写进标注手册；评测 pipeline 需支持多跳检索器。

### C.5 与 [151 bad case](151.bad-case-retrieval-miss-tutorial.md)

每条 retrieval miss 工单附 Recall 评测截图与建议 k。

### C.6 自测

画 Recall 低排查树默写；举 BM25 救 Recall 的一例。
""",
    "ragas-faithfulness": """
## 附录 C：Faithfulness 主线厚补充

### C.1 产品需求映射

| PRD 条目 | 技术实现 | 指标 |
|----------|----------|------|
| 不能瞎编数字 | Grounding [34] + 低 temperature | faithfulness |
| 必须给出处 | [113] 引用 | Citation-Faithfulness |
| 资料没有要说不知道 | [112] 拒答 | 拒答率 |

### C.2 判例库（节选）

**判例 1**：资料「10天」，答「10个工作日」——unsupported 或弱支持？团队 rubric 定死，写入标注手册。

**判例 2**：资料有矛盾两 chunk，模型合并——faithfulness 可能高但业务错，需资料治理 [48]。

**判例 3**：模型补充常识「年假一般需申请」——资料无此句——应 unsupported。

### C.3 采样评测 SOP

1. 每日 1% 流量落库；2. 异步 faithfulness；3. <0.7 进人工；4. 聚类 unsupported；5. 周会改 prompt/检索。

### C.4 与观测栈

[147 LangSmith](147.langsmith-tracing-tutorial.md) span：`retrieve`/`generate`/`faithfulness_audit`；[148 Langfuse](148.langfuse-observability-tutorial.md) 成本看 faithfulness 调用占比。

### C.5 训练侧（了解）

不要用 faithfulness 低样本 **直接微调** 而不修检索——会学会更自信地编 [33]。

### C.6 跨语言 faithfulness

用户英问、资料中、答英：claim 语言与 answer 一致；contexts 中文；选多语 judge 或中文 judge+翻译对照。

### C.7 法规免责

faithfulness 评测 **不构成** 法律合规认证；对外 Bot 仍要免责声明与人工复核流程 [155](155.human-evaluation-rag-tutorial.md)。

### C.8 里程碑

- M1：十条金标 faithfulness 基线  
- M2：§9 claim 审计上 trace  
- M3：[144] 回归 faithfulness 门禁  
- M4：生产 1% 采样  
- M5：与 [152] 工单闭环  

### C.9 自测十题

1. Faithfulness 定义？2. 与 Accuracy？3. contexts 从哪来？4. 拒答怎么评？5. claim 粒度？6. 最重要杠杆？7. 与 Recall 关系？8. Citation-Faithfulness？9. 成本？10. 下一步读哪篇？  
答案散见 §3–§15。

### C.10 系列锚点

本篇是 E 轨 **主线厚文**；[139][140] 管检索；[142] 管答非所问；[143] 供弹；[144] 守门；[145] 了解备选。
""",
    "ragas-answer-relevancy": """
## 附录 C：Relevancy 与体验

### C.1 用户调研对齐

问卷「是否回答了你的问题」1–5 分，与 Relevancy 做 Spearman；每年复测一次。

### C.2 多模态（了解）

若 [56 多模态](56.multimodal-image-text-tutorial.md) 进 RAG，Relevancy 仍对 **文本 answer**；图片描述偏题会拉低分。

### C.3 与流式 [116]

评完整 answer；首 token 快但答偏无助于 Relevancy。

### C.4 写作场景降权

创意写作 Bot Relevancy 权重可低于 Faithfulness——PRD 写清。

### C.5 自测

举「高 Faithfulness 低 Relevancy」一例；说明反向问题直觉。
""",
    "golden-dataset": """
## 附录 C：金标主线厚补充

### C.1 组织 RACI

| 活动 | R | A | C | I |
|------|---|---|---|---|
| Schema | 工程 | 算法 | 业务 | 运维 |
| 标注 | 业务 | 领域专家 | 算法 | 法务 |
| CI 评测 | 工程 | 算法 | — | 全员 |
| 版本 bump | 算法 | 工程 | 业务 | — |

### C.2 数据契约

下游 [144 回归](144.regression-test-set-tutorial.md)、[141 RAGAS](141.ragas-faithfulness-tutorial.md) 脚本 **只读** `schema_version` 兼容的 JSONL；破坏性变更升 major 并迁移脚本。

### C.3 从 0 到 50 条日历

| 周 | 目标 |
|----|------|
| W1 | Schema + 10 条 |
| W2 | +10 条 + validate CLI |
| W3 | +15 条 + 四指标报告 |
| W4 | +15 条 + 抽 [144] 15 条 |

### C.4 与 A/B [153]

金标固定时对比 `pipeline_v1` vs `v2` 四指标 delta——实验可信。

### C.5 失败案例入库

[149-152](149.bad-case-parsing-tutorial.md) 结案 → 转金标或回归 → **防止再现**。

### C.6 自测

写出 JSONL 一行完整字段；说明 golden vs regression 区别。
""",
    "regression-test-set": """
## 附录 C：回归门禁深化

### C.1 PR 注释 bot

CI 失败自动评论：`faithfulness 0.82→0.76 (-0.06)` + 最差 question 链接。

### C.2 本地 pre-push

`make regression` 跑 15 条，<3min，鼓励开发自测。

### C.3 与 monorepo

RAG 子服务变更才触发 regression workflow——path filter `config/**` `myrag/**`。

### C.4 版本冻结

发布分支只接受 regression 通过的 cherry-pick；hotfix 也要跑 smoke。

### C.5 自测

列出回归集必含的五类题；写 PR 阻断阈值一行 yaml。
""",
    "deepeval": """
## 附录 C：了解篇收束

### C.1 团队决策树

```text
需要 pytest 原生？
  是 → 评估 DeepEval
  否 → RAGAS [141] 主线
已有 RAGAS 投入？
  是 → 不迁移除非痛点明确
```

### C.2 推荐阅读顺序

[141 Faithfulness](141.ragas-faithfulness-tutorial.md) → [143 金标](143.golden-dataset-tutorial.md) → [144 回归](144.regression-test-set-tutorial.md) → 本篇 DeepEval 浏览 → [147 追踪](147.langsmith-tracing-tutorial.md)。

### C.3 一句收束

DeepEval 是 **工具箱多一把螺丝刀**；先把 RAGAS 四指标与金标跑通，再决定是否换握法。

### C.4 自测

说出 DeepEval 与 RAGAS 两点差异；何时不必学 DeepEval。
""",
}
