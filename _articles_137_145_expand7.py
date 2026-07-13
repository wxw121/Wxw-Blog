# -*- coding: utf-8 -*-
"""Seventh-pass expansions for 142, 144, 145."""

EXPAND7: dict[str, str] = {
    "ragas-context-recall": """
## 附录 H：Recall 达标备忘

本篇与 [139 Precision](139.ragas-context-precision-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 构成 RAG 检索与生成评测基础。Recall 低时务必先查金标 chunk_id 是否与索引一致，再查切块、过滤、k 与混合检索。每周固定 k 扫描与 hybrid ablation 是成本最低的 Recall 优化仪式。完成 §9 网格实验并写入 wiki 即达本篇合格线。
""",
    "ragas-answer-relevancy": """
## 附录 H：Relevancy 长案例与复盘

### H.1 三步复盘会

每周选 Relevancy 最低三条：读 question、读 answer、标「偏题句」——是 Prompt 冗长、检索噪声、还是 multi-intent 漏答。动作写入下周 sprint。

### H.2 与 [110 RAG Prompt](110.rag-prompt-template-tutorial.md) 槽位

在 system 增加：「只回答用户问题涉及的部分；不要主动扩展未问政策。」A/B 十条看 Relevancy delta。

### H.3 与 [107 预算](107.context-budget-tutorial.md)

无关 chunk 占预算→模型易跑题→Relevancy 降。先 Precision [139] 再 Relevancy。

### H.4 面试答法

「Relevancy 用反向问题/embed 相似度衡量答案是否对准问题；与 Faithfulness 正交。」

### H.5 交付

四指标 CSV 一份；Relevancy 最低三条复盘纪要一份。

### H.6 十日巩固计划

每日一练：D1 反向问题；D2 四指标；D3 Prompt 简洁；D4 拒答样本；D5 多轮展开；D6 人工对比；D7 权重表；D8 [145] 对照；D9 雷达图；D10 试讲。巩固后应能独立解释 Relevancy 与 Faithfulness 差异并指导 Prompt 迭代。

### H.7 团队共识

产品、算法、工程共同确认 Relevancy 在 PRD 中的权重；避免「只看 faithfulness 上线」导致用户仍觉答非所问。
""",
    "regression-test-set": """
## 附录 H：回归集运维手册

### H.1 on-call 见回归失败

1. 下载 artifact；2. 本地 `eval.run` 复现；3. 判断 flaky 或真倒退；4. 真倒退 revert 或 hotfix；5. 更新 baseline。

### H.2 季度审计

删过时题、加新 P0、检查 chunk_id 仍有效 [51](51.metadata-chunk-id-tutorial.md)。

### H.3 与 [153 A/B](153.ab-experiment-rag-tutorial.md)

实验分支可暂不调回归阈值，但 main 必须守阈值。

### H.4 文档模板

`docs/regression-policy.md`：规模、阈值、flaky、ownership、升级路径。

### H.5 完成标准

新人能根据文档在 30 分钟内修一条回归失败 PR。

### H.6 十日搭建计划

D1 选 15 条；D2 validate JSONL；D3 本地 eval；D4 CI yaml；D5 baseline；D6 artifact；D7 flaky 文档；D8 阈值评审；D9 on-call 演练；D10 团队 sign-off。完成后回归门禁即视为 E 轨工程化落地。

### H.7 与金标关系再强调

回归集不是第二套金标——它是金标的高优先级子集加固历史 bug；全量评测仍用 [143 Golden Dataset](143.golden-dataset-tutorial.md)。坚持每次 PR 跑回归，是 RAG 团队从「能跑」到「敢发版」的分水岭。
""",
    "deepeval": """
## 附录 H：DeepEval 一页纸备忘

| 项 | 内容 |
|----|------|
| 定位 | pytest 派 LLM 评测 |
| 主标尺 | 建议仍用 RAGAS [141] |
| 入口 | `assert_test` + `LLMTestCase` |
| 成本 | LLM-as-judge |
| 下一步 | [147 LangSmith](147.langsmith-tracing-tutorial.md) |

**何时回来深读**：团队统一 pytest、需要 G-Eval 自定义、RAGAS 无法满足 CI 粒度。

**何时不必读**：RAGAS + [143 金标](143.golden-dataset-tutorial.md) + [144 回归](144.regression-test-set-tutorial.md) 已跑顺。

阅读本篇后请在路线图 E 轨勾选 162 完成。

### H.2 半日工作坊议程

上午：RAGAS 四指标复习 [139-142]；下午：安装 DeepEval、跑 assert_test、填对照表、团队投票主标尺。结论写入 `docs/eval-tooling.md` 一页。

### H.3 与观测栈衔接

评测工具选定后，接入 [147 LangSmith](147.langsmith-tracing-tutorial.md) 或 [148 Langfuse](148.langfuse-observability-tutorial.md) 存分数与 trace，避免「本地 CSV 散落」。

### H.4 了解篇合格线

能回答：DeepEval 是什么、与 RAGAS 两点差异、为何本篇标「了解」、团队主标尺选哪个。合格即可进入 F 轨 bad case 与观测篇。
""",
}
