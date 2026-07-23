# -*- coding: utf-8 -*-
"""Fourth-pass large expansions (~2500+ hanzi each) for batch 137-145."""

EXPAND4: dict[str, str] = {
    "pluggable-store-retriever-generator": """
## 附录 D：Store/Retriever/Generator 深度问答与复盘

### D.1 二十条扩展 FAQ

**D.1.1** 三接口是否对应 Clean Architecture 的端口？——是常见映射：Store/Retriever 像仓储与领域服务，Generator 像外部网关。

**D.1.2** 一个进程多个 Pipeline 实例？——可以，共享 Store 连接池，注意线程安全与 collection 隔离。

**D.1.3** 异步 retrieve？——IO 密集可 `async def retrieve`；向量库 SDK 若同步，用线程池包一层，别阻塞事件循环。

**D.1.4** 批问 batch ask？——编排层循环或 batch API；Generator 批处理看厂商是否支持。

**D.1.5** 缓存 retrieve 结果？——短 TTL 缓存 key=`hash(query+filters+kb_version)`；索引更新时 bump kb_version 失效缓存。

**D.1.6** 日志打什么？——`trace_id, retrieval_k, chunk_ids, scores[], retrieve_ms, generate_ms, model, prompt_version`。

**D.1.7** 如何做 canary？——配置 5% 流量走 `HybridRetriever`，95% 走 `DenseRetriever`，对比 [141 faithfulness](141.ragas-faithfulness-tutorial.md)。

**D.1.8** Store 迁移 Chroma→Milvus？——实现新 Store 类，ingest 重跑，接口不变，[138 配置](138.config-driven-pipeline-tutorial.md) 改 class。

**D.1.9** 单元测试覆盖率目标？——接口实现 80%+；Pipeline 编排 90%+ 路径有 Fake 测试。

**D.1.10** Haystack 对照？——[134 Haystack](134.haystack-pipeline-tutorial.md) 用组件图；本篇用三接口，可写 Haystack 适配器。

**D.1.11** LlamaIndex 对照？——[132 Query Engine](132.llamaindex-query-engine-tutorial.md) 类似 Retriever+Generator 合体；拆开会更清晰评测。

**D.1.12** 为何不用一个大 Interface？——违反接口隔离；Store 变更不应迫使 Generator 重编译。

**D.1.13** metaclass 动态注册？——registry `{"chroma": ChromaVectorStore}` 优于 import 任意字符串。

**D.1.14** 链式 LCEL 还能用吗？——能，作为适配层；域核心仍建议本篇三接口。

**D.1.15** 本地模型 Generator？——`LlamaCppGenerator` 实现同一 Protocol；配置切换 model 路径。

**D.1.16** 多集合 Store？——`MultiCollectionStore` 内路由 `collection_for(tenant)`。

**D.1.17** 删除文档联动？——Store.delete by doc_id filter；ingest 管道 [136](136.pluggable-parser-splitter-embedder-tutorial.md) 发删除事件。

**D.1.18** 评测挂接点？——`pipeline.ask` 返回 `context_texts` 供 RAGAS [139-142](139.ragas-context-precision-tutorial.md)。

**D.1.19** 超时策略？——retrieve 2s、generate 30s 可配置；超时走降级拒答 [112](112.refusal-strategy-tutorial.md)。

**D.1.20** 初学者第一天？——读 §4 画三框 + 抄 §9 骨架 + 一条 Chroma 查询通。

### D.2 代码阅读顺序

`interfaces.py` → `chroma_store.py` → `dense_retriever.py` → `openai_generator.py` → `pipeline.py` → `config/factory.py` [138]。

### D.3 与路线图 D/E 模块衔接

D：136–138 架构；E：139–145 评测。本篇是 **D 轨收束下游可插拔**，紧接 E 轨量化验收。

### D.4 复盘模板

本周改动：___；Retrieve P95：___；Faithfulness：___；下步：___。贴 wiki 每周五。
""",
    "config-driven-pipeline": """
## 附录 D：配置驱动二十问与演练

### D.1 配置键全表（示例）

| 键 | 类型 | 默认 | 说明 |
|----|------|------|------|
| version | str | 必填 | 发版追踪 |
| pipeline.retriever_k | int | 8 | [98 Top-k](98.top-k-retrieval-tutorial.md) |
| pipeline.max_context_tokens | int | 6000 | [28 窗口](28.context-window-tutorial.md) |
| store.class | str | 必填 | [137 Store](137.pluggable-store-retriever-generator-tutorial.md) |
| store.args.path | str | ./chroma_db | 持久化 |
| retriever.class | str | 必填 | Dense/Hybrid |
| retriever.args.embedder_class | str | 必填 | [136](136.pluggable-parser-splitter-embedder-tutorial.md) |
| generator.class | str | 必填 | OpenAI 兼容 |
| generator.args.model | str | 必填 | [35 API](35.openai-compatible-api-tutorial.md) |
| generator.args.temperature | float | 0.1 | [29](29.llm-sampling-tutorial.md) |

### D.2 二十问简答

1. 为何 YAML？——人读友好。2. 秘密放哪？——环境变量。3. 如何校验？——Pydantic/JSON Schema。4. 多环境？——overlay merge。5. 热更新？——谨慎，常重启。6. 与 Docker？——挂载 config 卷。7. 版本谁 bump？——改配置人。8. CI 做什么？——validate+regression。9. 回滚？——Git revert yaml。10. A/B？——两套 yaml 或 flag。11. 与 137 关系？——配置注入三实现。12. 与 154 关系？——参数版本治理。13. 缺字段？——启动失败优于静默默认。14. class 白名单？——防注入。15. 文档？——example yaml 注释。16. 调试？——`rag pipeline print` 展开最终配置。17. 测试？——fixture 用小 yaml。18. 国际化？——配置不含文案，文案在 prompt 模板 [110]。19. 监控？——config_hash 指标。20. 第一天？——写 schema+工厂+validate 通。

### D.3 演练：故意改坏配置

把 `retriever_k` 改成字符串，观察 validate 报错信息与 CI 红灯——团队每个人都练一次。

### D.4 复盘

配置变更是 RAG 最常见变更类型；务必与 [144 回归](144.regression-test-set-tutorial.md) 绑定。
""",
    "ragas-context-precision": """
## 附录 D：Precision 专题训练营

### D.1 五日计划

**D1** 读 §3–§5，手算排序案例。**D2** 标 10 条 relevant。**D3** `pip install ragas` 跑通。**D4** 开 rerank [96] 对比。**D5** 写 wiki 报告含 Precision@5 曲线。

### D.2 与全链对照背诵

混合 [93]、RRF [94]、Rerank [96]、Dedup [106]、Budget [107]、Reorder [108]、Inject [111]——Precision 在 **Inject 前** 的最终列表上量。

### D.3 误判分析

| 现象 | 可能原因 |
|------|----------|
| Precision 突然降 | rerank 挂了回退 ANN |
| 某类 doc 低 | 该类 chunk 过长噪声 |
| 评测高生产低 | 评测用 rerank 生产没用 |

### D.4 扩展阅读

[151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md) 看 Recall；本篇 Precision 看噪声；[141](141.ragas-faithfulness-tutorial.md) 看生成。

### D.5 二十条简答

Precision 定义、与 Recall、为何排序敏感、rerank 作用、MMR 作用、k 对 Precision、金标 relevant、RAGAS API、阈值、分场景 baseline、与 NDCG、去重影响、多语言、成本、报告字段、CI 用法、与 faithfulness、下一步 140、作业、自测 pass 标准——见正文各节。
""",
    "ragas-context-recall": """
## 附录 D：Recall 专题训练营

### D.1 五日计划

**D1** 公式与金标。**D2** k 扫描。**D3** 开 hybrid [93]。**D4** 查切块 [57-64]。**D5** 报告 Recall delta。

### D.2 排查口诀

「先 id 后块，先滤后 k，先稀疏后向量，先索引后模型」——对应 chunk_id、切块、filter、[92 BM25]、重建索引。

### D.3 案例

问「第 7.2 节违约金比例」——BM25 救 Recall；纯向量可能漏「7.2」数字 token。

### D.4 与增量索引

[49 增量](49.incremental-update-tutorial.md) 漏文档→Recall 降→查 ingest 日志。

### D.5 二十问

见正文 §7 排查树扩展；每条用 [143 金标](143.golden-dataset-tutorial.md) 验证一项杠杆。
""",
    "ragas-faithfulness": """
## 附录 D：Faithfulness 主线训练营（厚）

### D.1 七日强化计划

**D1** 定义+§3 图。**D2** RAGAS 单条。**D3** 接 [137 Pipeline](137.pluggable-store-retriever-generator-tutorial.md)。**D4** §9 claim 审计。**D5** 调 [110 Prompt](110.rag-prompt-template-tutorial.md)+[29 temp](29.llm-sampling-tutorial.md)。**D6** 接 [143 金标](143.golden-dataset-tutorial.md) 十条。**D7** 写 Runbook+讲评。

### D.2 _UNSUPPORTED 聚类表示例

| 聚类 | 占比 | 动作 |
|------|------|------|
| 数字篡改 | 40% | 强调原文引用 |
| 无关扩展 | 30% | 简洁+Relevancy |
| 张冠李戴 | 20% | 重排 [108] |
| 其他 | 10% | 个案 |

### D.3 与 Grounding 联合验收

产品验收清单：faithfulness≥阈值、引用可点 [113]、拒答正确 [112]、trace 可查 [147]。

### D.4 判例十则（练习）

自行判断 supported/unsupported：合并两 chunk 矛盾说法、添加「通常而言」、正确拒答、翻译同义、单位换算错误、日期格式差异、主语偷换、范围扩大、引用错 chunk、工具结果未进 contexts。答案写入团队 rubric。

### D.5 代码清单

`eval/faithfulness.py`、`audit_claims.py`、CI 门禁、[144 regression](144.regression-test-set-tutorial.md) 含 5 条 faithfulness-critical。

### D.6 跨模块背诵

33 幻觉、34 Grounding、110 Prompt、111 注入、112 拒答、113 引用、28 窗口、107 预算、141 本篇、143 金标、144 回归、152 胡编归因——构成 **防胡编闭环**。

### D.7 面试模拟

用 3 分钟解释 Faithfulness 流程；用 1 分钟说与 Recall 区别；用 1 分钟说最大成本点。

### D.8 交付物检查

- [ ] 十条分数表  
- [ ] claim 审计 JSON 样例  
- [ ] 阈值策略  
- [ ] Runbook 一页  
- [ ] 团队 rubric 一页  

### D.9 常见数字错误根因

temperature 高、证据被截断 [28]、Lost in the Middle [108]、prompt 未禁止 extrapolation、检索到相似但非同一制度 chunk。

### D.10 系列宣言

**Faithfulness 是 E 轨主线锚点**——老板听得懂「有没有瞎编」，技术能落到 claim 审计与 CI 门禁。
""",
    "ragas-answer-relevancy": """
## 附录 D：Relevancy 训练营

### D.1 三日计划

**D1** 反向问题。**D2** 四指标同跑。**D3** 调 prompt 简洁槽 [110] 看 Relevancy 变化。

### D.2 对照表

| 答案类型 | Faithfulness | Relevancy |
|----------|--------------|-----------|
| 忠实但啰嗦 | 高 | 低 |
| 简洁且对题 | 高 | 高 |
| 瞎编短答 | 低 | 可能高 |

### D.3 多轮注意

[118 多轮](118.multi-turn-history-tutorial.md)+[120 指代](120.coreference-resolution-tutorial.md) 后再评。

### D.4 二十问简答

见 §3–§12；重点：与 Faithfulness 分工、拒答处理、权重、DeepEval 对照 [145]。
""",
    "golden-dataset": """
## 附录 D：金标主线训练营（厚）

### D.1 十四日上线计划

**W1**：Schema、validate CLI、20 条冷启动、首次四指标报告。**W2**：+20 条、抽 [144] 15 条、CI 集成、治理文档。

### D.2 Schema 字段详解

`id` 全局唯一；`question` 用户视角；`ground_truth` 评测判据；`relevant_chunk_ids` 检索金标准；`tags` 分层报表；`difficulty` 采样权重；`expect_refusal` 拒答题；`min_faithfulness` 门禁；`metadata` 扩展。

### D.3 标注争议仲裁

业务与法务不一致→升级产品负责人；engineering 不单方面改 ground_truth。

### D.4 与文档版本 [48]

`handbook-v3` 换 `v4`→金标 bulk 更新 relevant ids 或 fork `dataset_version` major。

### D.5 采样策略

生产 1% 随机+100% 低 faithfulness+100% 点踩——去重后人工审核入库。

### D.6 成本

标注人力为主；自动评测 API 为辅；ROI 在 **少一次生产事故**。

### D.7 面试十问

金标定义、与回归区别、多少条、谁标注、如何更新、schema 版本、PII、多语言、与 RAGAS、失败案例回流——见 §4–§14。

### D.8 交付物

`golden/*.jsonl`、`eval/run.py`、首次 `report.html`、RACI 表、标注手册 PDF。

### D.9 系列宣言

**没有金标，RAGAS 只是玩具分数**；本篇是 E 轨 **数据主线**。
""",
    "regression-test-set": """
## 附录 D：回归集训练营

### D.1 三日搭建

**D1** 从 [143](143.golden-dataset-tutorial.md) 选 15 条。**D2** GitHub Actions。**D3** baseline 缓存与失败 artifact。

### D.2 选题打分卡

| 因素 | 权重 |
|------|------|
| 业务核心 | 高 |
| 历史 P0 bug | 高 |
| faithfulness 敏感 | 中 |
| 边缘拒答 | 中 |
| 罕见语言 | 低 |

### D.3 与 nightly

PR 跑 regression；每晚跑 golden 全量；分工明确。

### D.4 二十问

规模、时间、阈值、flaky、baseline、artifact、谁维护、与 DeepEval、回滚、smoke 子集——见正文。

### D.5 宣言

**回归集是工程纪律**——让评测真正挡住烂合并。
""",
    "deepeval": """
## 附录 D：DeepEval 浏览巩固

### D.1 两小时路径

0:00 读 §3–§4；0:30 `pip install`；1:00 跑 §9 pytest；1:30 填对照表；2:00 团队决定主标尺。

### D.2 不必深潜的场景

纯 RAGAS 已满足、无 pytest 文化、PoC 阶段——本篇 **标记已读即可**。

### D.3 与 TruLens [146]

TruLens 偏追踪反馈；DeepEval 偏断言；RAGAS 偏数据集 evaluate——三工具 **定位不同**，勿混。

### D.4 二十问简答

是什么、与 RAGAS、pytest、成本、中文、何时选、G-Eval、迁移、CI、下一步 147——见 §3–§13。

### D.5 宣言

**了解篇完成标志**：能说出「pytest 派备选，RAGAS 主线」并跑通一个 assert_test。
""",
}
