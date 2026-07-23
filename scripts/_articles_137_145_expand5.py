# -*- coding: utf-8 -*-
"""Fifth-pass expansions to guarantee >=5000 hanzi for shorter articles."""

EXPAND5: dict[str, str] = {
    "config-driven-pipeline": """
## 附录 E：配置驱动案例库与联调

### E.1 案例：k 从 5 调到 8

**变更**：`pipeline.retriever_k: 5→8`。**回归**：[140 Recall](140.ragas-context-recall-tutorial.md) +0.06，[139 Precision](139.ragas-context-precision-tutorial.md) -0.02。**决策**：接受，因 Recall 优先。**记录**：`pipeline.version: 1.2.0→1.2.1`。

### E.2 案例：切换 Hybrid

**变更**：`retriever.class: DenseRetriever→HybridRetriever`。**配置**增 `dense_k/sparse_k/fusion`。**验证**：十条 [143 金标](143.golden-dataset-tutorial.md) 全跑。**耗时**：+120ms P95。

### E.3 案例：密钥轮换

只改 K8s Secret，yaml 仍 `${{OPENAI_API_KEY}}`。**注意**：滚动重启 pod，避免半集群旧 key。

### E.4 与 [137 工厂](137.pluggable-store-retriever-generator-tutorial.md) 联调清单

validate → build_from_config → pipeline.ask → eval.run → 对比 report。**任一步失败** 不要直接改 prod yaml。

### E.5 配置注释规范（中文）

每个键三行注释：**含义**、**调大影响**、**关联指标篇号**。新人只看 yaml 也能懂副作用。

### E.6 故障：类找不到

`ModuleNotFoundError: myrag.retrievers.HybridRetriever`→检查 PYTHONPATH、包安装、typos。**CI validate** 应 import 干跑。

### E.7 故障：参数类型错

`retriever_k: "8"` 字符串→Pydantic 报错。**教新人** 看 validate 输出。

### E.8 扩展：多 pipeline 配置

`config/pipelines/hr.yaml`、`config/pipelines/it.yaml`——路由层按 bot 类型选文件。

### E.9 面试长答

描述一次你从改配置到回归通过的全流程：改 yaml→本地 validate→跑 [144]→PR→CI→merge→prod 滚动→看 [147] trace 抽样。

### E.10 自测通过标准

能独立写出 `pipeline.yaml` + `build_from_config` 骨架；能解释 overlay；能列举四种 §8 翻车。
""",
    "ragas-context-precision": """
## 附录 E：Precision 案例与联调

### E.1 案例：rerank 前后

| 阶段 | P@5 |
|------|-----|
| ANN | 0.55 |
| +BGE [96] | 0.78 |

写进配置是否默认开 rerank。

### E.2 案例：FAQ 噪声

前排常混入「联系我们」footer chunk——标 relevant 时 **排除** footer 模板 chunk；或 ingest 时 [46 清洗](46.text-cleaning-tutorial.md)。

### E.3 与 [98 k](98.top-k-retrieval-tutorial.md)

k 过大 Precision 降——画 k-Precision 曲线找拐点。

### E.4 与 [106 去重](106.retrieval-dedup-tutorial.md)

重复 chunk 占前排槽位→去重后 Precision 升。

### E.5 评测集分层

按 `tags: faq|policy|table` 出三张 Precision 表——表格类常更低（切块 [37 PDF 表格](37.pdf-layout-tables-tutorial.md)）。

### E.6 人工校准

抽 20 条 RAGAS Precision 与人工判相关对比 Cohen's kappa——<0.6 调 judge prompt。

### E.7 下一步

精读 [140 Recall](140.ragas-context-recall-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)。

### E.8 自测

解释为何 Precision 是排序指标；写 rerank 提升 Precision 的一次实验记录模板。
""",
    "ragas-context-recall": """
## 附录 E：Recall 案例与联调

### E.1 案例：切块过大

整章一个 chunk，向量模糊→Recall 低→改 [62 结构感知](62.structure-aware-chunking-tutorial.md) 按节切→Recall +0.2。

### E.2 案例：BM25 救命

query 含「GDPR 第 17 条」——dense 漏，sparse 命中。

### E.3 案例：filter 误杀

`doc_id: handbook-v2` 金标在 v3→Recall 0→修 filter 或金标。

### E.4 k 扫描记录

贴 wiki：`k=5→0.62, k=10→0.71, k=20→0.78, k=50→0.79`——选 k=20。

### E.5 多跳 [104]

第一跳命中背景，第二跳命中条款——Recall 定义含两跳 relevant 并集。

### E.6 与 [151](151.bad-case-retrieval-miss-tutorial.md)

工单必须附：金标 ids、实际 ids、建议杠杆。

### E.7 自测

默写排查树；完成一次 k 扫描实验。
""",
    "ragas-answer-relevancy": """
## 附录 E：Relevancy 案例

### E.1 啰嗦答案

faithfulness 0.9，relevancy 0.5——删「此外还需要注意…」废话，relevancy 升 0.15。

### E.2 拒答样本

`expect_refusal: true` 不评 relevancy。

### E.3 多意图

问「年假和病假」，只答年假——relevancy 低，faithfulness 可能仍高。

### E.4 四指标同屏

CSV 列全，发版对比雷达图。

### E.5 与 [142] 路线图

本篇即 Answer Relevancy 完整指南。

### E.6 自测

举高 F 低 R 例子；跑四指标 evaluate 一次。
""",
    "golden-dataset": """
## 附录 E：金标案例库

### E.1 冷启动二十条来源表

| 来源 | 条数 |
|------|------|
| 运营 FAQ | 8 |
| 文档标题改写 | 6 |
| 拒答/ACL | 3 |
| 数字敏感 | 3 |

### E.2 争议案例

「试用期」问法口语 vs 法条用语——question 保留口语，ground_truth 写法条。

### E.3 版本 fork

`golden-hr-2026.04.01` major bump 到 `2026.10.01` 因换 handbook v4。

### E.4 validate 规则

chunk_id 存在性、id 唯一、refusal 互斥字段。

### E.5 生长

每周 trace 采纳 ≥3 条；点踩 100% 进审。

### E.6 与 [144](144.regression-test-set-tutorial.md)

从 50 条抽 15 条作 regression core。

### E.7 面试长答

如何建第一条金标？→ 选高频 FAQ→人写 ground_truth→工程绑 chunk_id→跑四指标→入库。

### E.8 自测

写完整 JSON 一行；说明 RACI。
""",
    "regression-test-set": """
## 附录 E：回归案例

### E.1 P0 bug 入库

2026-03 年假数字错→加 `reg-015`→每次 PR 必跑→未再现。

### E.2 flaky 处理

faithfulness 波动→固定 temp=0→三次中位数。

### E.3 baseline 漂移

main 分上升后更新 baseline——避免 PR 永远「负 delta 好看」。

### E.4 smoke 5 条

极速检查，pre-commit 可选。

### E.5 与 [145 DeepEval](145.deepeval-tutorial.md)

`pytest -k regression` 可换 deepeval 入口，数据同源。

### E.6 自测

建 15 条 core.jsonl；写阈值 yaml 片段。
""",
    "deepeval": """
## 附录 E：DeepEval 巩固

### E.1 最小仓库结构

```text
tests/
  test_rag_regression.py
regression/
  core.jsonl
```

### E.2 assert_test 失败输出

读懂 score 与 reason，改 prompt 或检索，不是盲目降 threshold。

### E.3 与 RAGAS 数据复用

同 JSONL 转 `LLMTestCase` 列表。

### E.4 团队决议模板

「主标尺：RAGAS；DeepEval：仅 pytest 包装；理由：…」

### E.5 自测

跑通一个 test；说出与 RAGAS 两点不同。
""",
}
