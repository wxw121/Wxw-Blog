# -*- coding: utf-8 -*-
"""Sixth-pass expansions for remaining short articles."""

EXPAND6: dict[str, str] = {
    "ragas-context-precision": """
## 附录 F：Precision 进阶练习

请独立完成以下练习并写入学习笔记：（1）构造三条 contexts，手算 Precision 排序影响；（2）对同一 question 比较 k=5 与 k=20 的 Precision@k；（3）打开 [96 BGE 重排](96.bge-reranker-tutorial.md) 前后对比截图；（4）从 [143 金标](143.golden-dataset-tutorial.md) 选 5 条标 relevant；（5）用 ragas 跑出 mean 与最差 id；（6）写一段「若 Precision 低先做什么」的运维口诀；（7）对照 [106 去重](106.retrieval-dedup-tutorial.md) 前后分数；（8）阅读 [108 长文重排](108.long-context-reorder-tutorial.md) 与 Precision 关系；（9）在 [138 配置](138.config-driven-pipeline-tutorial.md) 记录 rerank 开关版本；（10）向同事讲解 Precision 与 Recall 区别五分钟。全部完成即达到本篇 Precision 地基合格线。复习时重点看 §8 先错对对与 §9 实战脚本，面试时能白板画「前排噪声」示意图。与系列 [140 Recall](140.ragas-context-recall-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 组成检索—生成评测三角，勿孤立优化 Precision 而忽视 Recall 与忠实度。生产环境请在进 prompt 前的最终 context 列表上评测，并在 trace 中保存 contexts 快照供事后复算。每周选最差 5 条 Precision 样本做 chunk 级复盘，是成本最低的检索优化仪式。
""",
    "ragas-context-recall": """
## 附录 F：Recall 进阶练习与口诀

**口诀**：「id 要对、块要碎、滤要松、k 要够、混合要开、索引要新、ACL 要分身份评」。练习：（1）选一条 Recall=0 的金标，沿 §7 排查树走一遍；（2）对同一数据集做 k=5/10/20/50 扫描表；（3）开启 [93 混合](93.hybrid-search-tutorial.md) 记录 delta；（4）检查 [57-64 切块](57.fixed-size-chunking-tutorial.md) 是否切断关键句；（5）确认 [51 chunk_id](51.metadata-chunk-id-tutorial.md) 与索引一致；（6）用 [100 Query 改写](100.query-rewriting-tutorial.md) 试一条；（7）检查 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 是否误杀；（8）对 [121 ACL](121.unauthorized-doc-filter-tutorial.md) 用有权用户重评；（9）将结果写入 wiki 与 [138 pipeline version](138.config-driven-pipeline-tutorial.md)；（10）讲解「Recall 低 vs Precision 低」排障差异。Recall 是证据到场率，常与业务「答不出来」直接相关，应优先于花哨生成技巧投入。与 [151 检索遗漏 bad case](151.bad-case-retrieval-miss-tutorial.md) 工单联动，形成闭环。增量索引 [49](49.incremental-update-tutorial.md) 事故常表现为 Recall 断崖，第一时间查 ingest 日志。多跳场景 [104](104.multi-hop-retrieval-tutorial.md) 要在金标中标清 relevant 并集。完成练习后应能独立设计一次 k-hybrid 网格实验并汇报结论。

## 附录 G：Recall 专题案例扩展

### G.1 制度编号检索

用户问「员工手册 4.2.1 条罚款规定」——query 含编号 token，[92 BM25](92.sparse-retrieval-rag-tutorial.md) 路往往优于纯向量；若 Recall 低，先开 hybrid 再查切块是否把 4.2.1 与正文拆散。**验收**：relevant_chunk_ids 含 `handbook:sec4.2.1` 对应块。

### G.2 同义词与口语

「带薪年假」对「年休假」——向量路应覆盖；若仅 BM25 可能漏。域内 [71 Embedding 评测](71.domain-embedding-evaluation-tutorial.md) 不过时两路都可能漏。**杠杆**：[100 改写](100.query-rewriting-tutorial.md) 生成多 query 并集检索 [101](101.multi-query-retrieval-tutorial.md)。

### G.3 英文问中文库

问「How many annual leave days?」中文资料——需 [70 混合语言 Embedding](70.mixed-language-embedding-tutorial.md) 或 query 翻译进检索。**评测**：金标 tag `en-query-zh-kb`。

### G.4 表格中的数字

年假天数在 PDF 表格 [37](37.pdf-layout-tables-tutorial.md) 单元格——解析失败则永远 Recall 0。**先修解析** 再调 k。

### G.5 周报模板

| 周 | Recall P50 | 动作 |
|----|------------|------|
| W1 | 0.72 | 基线 |
| W2 | 0.78 | +hybrid |
| W3 | 0.81 | +k20 |

### G.6 与 Precision 联调会议议程

三十分钟：前十分钟 Recall 趋势；中十分钟最差 5 条；后十分钟是否牺牲 Precision 换 Recall（调 k、开 hybrid）。**决策记录**进 [138 配置变更单](138.config-driven-pipeline-tutorial.md)。

### G.7 自测答案要点

Recall 衡量金标 relevant 被 retrieved 覆盖比例；Precision 衡量前排干净；Recall 低先查切块与索引；hybrid 常抬 Recall；评测身份要与 ACL 一致。复习时请对照 [139 Precision](139.ragas-context-precision-tutorial.md) 与 [141 Faithfulness](141.ragas-faithfulness-tutorial.md)，形成检索质量完整图景。
""",
    "ragas-answer-relevancy": """
## 附录 F：Relevancy 进阶练习

（1）构造「高 faithfulness、低 relevancy」答案一条并解释；（2）用 [110 Prompt](110.rag-prompt-template-tutorial.md) 加「仅答所问」前后对比 Relevancy；（3）对拒答样本标 `expect_refusal` 并跳过评测；（4）多轮题用 [120 指代](120.coreference-resolution-tutorial.md) 展开后再评；（5）四指标同表输出 CSV；（6）抽 10 条人工「答非所问」与 Relevancy 对比；（7）阅读 [142] 路线图定位本篇；（8）了解 [145 DeepEval](145.deepeval-tutorial.md) 同族指标；（9）在 PRD 写清 Relevancy 权重；（10）五分钟讲解反向问题直觉。Relevancy 衡量用户视角「有没有答到点子上」，与 Faithfulness 互补：前者对 question，后者对 contexts。冗长礼貌废话常拉低 Relevancy 而不影响 Faithfulness，是 Prompt 简洁槽位的量化证据。创意场景可降低权重但不应忽略。完成本篇后应能跑通四指标 evaluate 并读懂雷达图发版对比。

## 附录 G：Relevancy 场景扩展

### G.1 客服场景权重

制度 Bot PRD 示例：Faithfulness 0.35、Recall 0.25、Precision 0.20、Relevancy 0.20——Relevancy 过低即使用户觉得「文不对题」。**验收**：用户调研「是否答非所问」与 Relevancy Spearman ≥0.6。

### G.2 对比实验记录表

| Prompt 版本 | Faithfulness | Relevancy |
|-------------|--------------|-----------|
| v1 无简洁要求 | 0.88 | 0.62 |
| v2 仅答所问 | 0.87 | 0.79 |

### G.3 多轮 follow-up

「那病假呢？」——评测 question 必须用 [109](109.conversation-query-enhancement-tutorial.md) 或 [120](120.coreference-resolution-tutorial.md) 展开为 standalone，否则 Relevancy 误判。

### G.4 与 [112 拒答](112.refusal-strategy-tutorial.md)

拒答句与原始 question 语义距离大——`expect_refusal: true` 样本跳过 Relevancy，单独统计拒答准确率。

### G.5 系列小结

四指标齐全后进入 [143 金标](143.golden-dataset-tutorial.md) 工程化；Relevancy 是用户体验维度的量化锚点。
""",
    "regression-test-set": """
## 附录 F：回归集进阶练习

（1）从 [143 金标](143.golden-dataset-tutorial.md) 选 15 条建 `core.jsonl`；（2）写 GitHub Actions 或等效 CI 骨架；（3）设 faithfulness 阻断阈值 -0.05；（4）配置失败 artifact 上传；（5）录一条 P0 bug 复现用例；（6）写 flaky 处理策略；（7）区分 smoke 5 条与 core 15 条；（8）main 分支缓存 baseline；（9）与 [154 参数版本](154.param-version-management-tutorial.md) 回滚演练；（10）团队评审回归集选题。回归集的灵魂是「小而硬、每次 PR 必跑、几分钟出结果」，不是金标全集替代品。与 nightly 全量金标评测分工：前者守门，后者探覆盖。失败时必须能定位到 question id 与四指标 delta，并链接 [147 trace](147.langsmith-tracing-tutorial.md)。维护人每 sprint 至少新增一条历史 bug 用例。DeepEval pytest 入口 [145](145.deepeval-tutorial.md) 可复用同一数据。完成练习即具备 E 轨工程门禁落地能力。

## 附录 G：回归门禁扩展

### G.1 阈值调参工作坊

两小时：列出历史五次 PR 的指标 delta，讨论 faithfulness -0.03 是否应告警而非阻断——形成书面共识贴 wiki。

### G.2 artifact 字段

`question, answer, contexts[], deltas{}, pipeline_version, git_sha`——研发可直接复现。

### G.3 与 [141 Faithfulness](141.ragas-faithfulness-tutorial.md)

回归集至少 5 条 `faithfulness-critical`；任一跌破 0.8 阻断。

### G.4 ownership

算法负责选题；工程负责 CI；产品确认阈值；每周 standup 报回归失败率。

### G.5 完成标志

CI 绿 + 团队能解释为何是 15 条而不是 50 条。
""",
    "deepeval": """
## 附录 F：DeepEval 浏览巩固练习

（1）`pip install deepeval`；（2）配置 API Key；（3）跑通 §9 单条 `assert_test`；（4）填 §4 与 RAGAS 对照表；（5）读官方 FaithfulnessMetric 文档；（6）决定团队主标尺（建议 RAGAS [141]）；（7）写一句「何时用 DeepEval」；（8）浏览 G-Eval 不深入；（9）与 [146 TruLens](146.trulens-tutorial.md) 定位区分；（10）标记本篇已读进入 [147 LangSmith](147.langsmith-tracing-tutorial.md)。DeepEval 是 pytest 原生 LLM 评测备选，指标族与 RAGAS 类似但数值不可横比。了解篇目标是避免「听说有两个库却不知差异」。PoC 阶段不必两套并行；已有 RAGAS 报表时仅在有 pytest 强需求时引入。成本同为 LLM-as-judge，计入 [27 Token 计费](27.token-counting-billing-tutorial.md)。完成练习后能向同事解释「主线 RAGAS + 备选 DeepEval」即可。

## 附录 G：DeepEval 扩展阅读与决策

### G.1 官方文档 skim 清单

Metrics 列表、LLMTestCase 字段、pytest 插件、confest 环境变量——各花十分钟，不求精通。

### G.2 与 [144 回归](144.regression-test-set-tutorial.md)

若选 DeepEval，则 `deepeval test run` 替代 `python -m eval.run` 作 PR 门禁；**数据文件仍用同一 JSONL**。

### G.3 不迁移的理由（常见）

已有 RAGAS 看板、数值历史不可比、团队无 pytest 习惯——任一条成立即可暂不引入。

### G.4 迁移的理由（常见）

全仓库 pytest 文化、需要 G-Eval 自定义 rubric、想要在 IDE 里点点跑单测。

### G.5 系列收束

E 轨 139–145 读完：四指标 [139-142]、金标 [143]、回归 [144]、DeepEval 了解 [145]；下一步观测 [147-148] 与 bad case [149-152]。
""",
}
