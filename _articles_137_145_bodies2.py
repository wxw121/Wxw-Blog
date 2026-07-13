# -*- coding: utf-8 -*-
"""Article bodies 141-145 for batch 137-145."""
from _batch_137_145_common import COMMON_RAG_LINKS, _faq, _mistakes

BODIES = {}

BODIES["141.ragas-faithfulness-tutorial.md"] = f"""# E 评测与观测（三）：RAGAS Faithfulness 完全指南

> 检索对了、模型仍可能把「10 天年假」说成「15 天」——这就是 [33 幻觉](33.llm-hallucination-tutorial.md) 里的 **忠实性胡编**。**Faithfulness**（忠实度）是 RAG 上线 **最常被业务追问** 的指标：「回答里的每一句，能不能在资料里找到依据？」这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨主线篇**（路线图第 **158** 条），厚实现导向，串联 [34 Grounding](34.grounding-citation-tutorial.md)、[112 拒答](112.refusal-strategy-tutorial.md)、[113 引用](113.inline-citation-tutorial.md) 与全链 [93–112](93.hybrid-search-tutorial.md)。前置：[139 Precision](139.ragas-context-precision-tutorial.md)、[140 Recall](140.ragas-context-recall-tutorial.md)、[110 RAG Prompt](110.rag-prompt-template-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)。

---

## 目录

1. [前言：检索满分也会「编」](#1-前言检索满分也会编)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Faithfulness 是什么](#3-faithfulness-是什么)
4. [Claim 分解与证据对齐](#4-claim-分解与证据对齐)
5. [RAGAS Faithfulness 计算流程](#5-ragas-faithfulness-计算流程)
6. [与 Grounding、引用契约的关系](#6-与-grounding引用契约的关系)
7. [提升 Faithfulness 的杠杆](#7-提升-faithfulness-的杠杆)
8. [先错对对：六种典型翻车](#8-先错对对六种典型翻车)
9. [综合实战：端到端评测与 Claim 审计](#9-综合实战端到端评测与-claim-审计)
10. [阈值、拒答与产品策略](#10-阈值拒答与产品策略)
11. [与 Context 指标、Relevancy 三角](#11-与-context-指标relevancy-三角)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [生产 Runbook 与组织流程](#14-生产-runbook-与组织流程)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：检索满分也会「编」

Bad case 复盘：

| 环节 | 状态 |
|------|------|
| Context Recall | 1.0 |
| Context Precision | 0.9 |
| 用户看到 | 「试用期三个月，年假 15 天」 |
| 资料 | 年假 10 天 |

运营结论：「检索没问题，是模型胡说。」——**Faithfulness 就是为这类事故准备的验收尺**。

**Faithfulness**（忠实度）：生成答案中的 **陈述** 是否能被 **检索上下文** 支持（entail）。  
通俗说：**闭卷变开卷后，学生是否仍偷偷编数字**。

**读完本文，你应该能做到：**

1. 解释 Faithfulness 与 [34 Grounding](34.grounding-citation-tutorial.md) 的异同。  
2. 跑通 RAGAS `faithfulness` 与自定义 **claim 审计脚本**（§9）。  
3. 列出 **六种** faithfulness 翻车模式（§8）。  
4. 设计 **阈值 + 拒答** 联动（§10）。  
5. 把评测接入 [143 金标](143.golden-dataset-tutorial.md) 与 [144 回归](144.regression-test-set-tutorial.md)。

### 1.1 E 轨主线位置

```text
156 Precision [139] ─┐
157 Recall [140] ────┼→ 158 Faithfulness ← 本篇（主线厚）
159 Relevancy [142] ─┘
160 Golden Dataset [143]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 忠实度 | Faithfulness | 答案句是否有上下文依据 |
| 断言 | Claim | 可独立核验的一句话 |
| 蕴含 | Entailment | 上下文是否支持该断言 |
| 落地 | Grounding | 产品与提示词层的约束 |
| 幻觉 | Hallucination | 流畅但不真 [33](33.llm-hallucination-tutorial.md) |

### 1.3 读完本篇的最小交付物

1. 十条金标 `faithfulness` 分数表；  
2. §9 `audit_claims.py` 可运行；  
3. 与 [110 Prompt](110.rag-prompt-template-tutorial.md) 对齐的 system 版本号；  
4. faithfulness < 0.8 时的 **产品策略** 文档一段；  
5. §8 六种先错对对复述。

---

## 2. 本文边界与动手路径

**档位：E 轨主线篇（158，厚实现导向）。**

**本文讲：** Faithfulness 定义、RAGAS 流程、claim 审计、杠杆、阈值、Runbook。  
**本文不讲：** 法律合规认定、医疗器械级验证、完整人工评测平台 [155](155.human-evaluation-rag-tutorial.md)。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §3～§5 | 能画 claim→entail 图 |
| B | `pip install ragas` | 单条 faithfulness 出分 |
| C | 接 [137 Pipeline](137.pluggable-store-retriever-generator-tutorial.md) | 批量 10 条 |
| D | 跑 §9 claim 审计 | 输出 unsupported 列表 |
| E | 调 [29 temperature](29.llm-sampling-tutorial.md) | 0 vs 0.7 对比 |
| F | 写 §10 阈值策略 | 与 [112 拒答](112.refusal-strategy-tutorial.md) 一致 |
| G | §8 六种翻车 | 团队分享 |

**环境：** Python 3.10+；RAGAS + 裁判 LLM API；可选本地小模型（以文档为准）。

### 2.2 沿用前文（全链）

{COMMON_RAG_LINKS}

| 生成与溯源 | [34 Grounding](34.grounding-citation-tutorial.md)、[113 引用](113.inline-citation-tutorial.md) |
| 金标与回归 | [143 Golden](143.golden-dataset-tutorial.md)、[144 回归集](144.regression-test-set-tutorial.md) |
| 可插拔与配置 | [136](136.pluggable-parser-splitter-embedder-tutorial.md)、[137](137.pluggable-store-retriever-generator-tutorial.md)、[138](138.config-driven-pipeline-tutorial.md) |

---

## 3. Faithfulness 是什么

读下图：答案拆成 claim，每条箭头指向「支持 / 不支持 / 无法判断」。

![Faithfulness 是什么](image/ragas-faithfulness/01-faithfulness-idea.png)

对照上图：

- **输入**：`question`、`contexts`（进 prompt 的资料）、`answer`；  
- **过程**：拆 claim → 每条判是否被 contexts **蕴含**；  
- **输出**：支持比例 = Faithfulness 分数（0～1）。

与 **事实正确** 不同：资料本身错时，Faithfulness 仍可能 **高**（模型忠实复述了错库）——那是 **知识库质量** 问题，不是生成忠实度问题。

---

## 4. Claim 分解与证据对齐

**Claim**（断言）：答案中 **可独立核验** 的陈述，通常 **一句一 claim**。

| 答案 | Claims |
|------|--------|
| 「年假 10 天，需工作满一年。」 | C1: 年假10天；C2: 需工作满一年 |

**演示目标**：用 LLM 或规则拆 claim（简化版）。  
**预期**：列表 `["年假10天", "需工作满一年"]`。

```python
SPLIT_PROMPT = \"\"\"将下列答案拆成独立事实断言列表，每行一条，不要编号：
答案：{{answer}}\"\"\"

def split_claims(answer: str, llm) -> list[str]:
    text = llm.generate(SPLIT_PROMPT.format(answer=answer))
    return [ln.strip() for ln in text.splitlines() if ln.strip()]
```

**证据对齐**：对每个 claim，问裁判「上下文是否支持该断言？」——NLP 里常叫 **NLI**（自然语言推理）风格的 entailment。

---

## 5. RAGAS Faithfulness 计算流程

RAGAS 内部（概念级，版本以 [官方文档](https://docs.ragas.io/) 为准）：

```text
answer → statements/claims
for each claim:
    judge(contexts, claim) → supported | unsupported | ambiguous
faithfulness = supported / (supported + unsupported)  # ambiguous 处理见版本说明
```

**演示目标**：`ragas.metrics.faithfulness`。  
**环境**：`pip install ragas datasets`。  
**预期**：打印 0～1。

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness

row = {{
    "question": "年假多少天？",
    "answer": "工作满一年的员工享有10天年假。",
    "contexts": [
        "第三章 休假制度：员工在公司工作满一年后，享受带薪年假10天。",
    ],
}}
ds = Dataset.from_list([row])
result = evaluate(ds, metrics=[faithfulness])
print(result)
```

**解读**：若 answer 写「15 天」，faithfulness 应 **显著下降**——即使语气自信。

---

## 6. 与 Grounding、引用契约的关系

| 层 | 手段 | 度量 |
|----|------|------|
| Prompt | [34 Grounding](34.grounding-citation-tutorial.md) 规矩 | 间接 |
| 输出格式 | [113][n] 引用 | 可解析性 |
| 评测 | Faithfulness | 量化 |

**Citation-Faithfulness**（扩展）：带 [1][2] 的句，要求 **标注 chunk 必须支持该句**。比纯 Faithfulness 更贴 UI；可在 §9 加规则校验。

与 [112 拒答](112.refusal-strategy-tutorial.md)：faithfulness 低 **不一定** 拒答（可能是无关废话）；**unsupported 关键事实** 应拒答或降级。

---

## 7. 提升 Faithfulness 的杠杆

按 **性价比** 排序：

| # | 杠杆 | 关联篇 |
|---|------|--------|
| 1 | system 强制「仅据资料」 | [110](110.rag-prompt-template-tutorial.md) |
| 2 | temperature 0～0.2 | [29](29.llm-sampling-tutorial.md) |
| 3 | 减少无关 context | [139 Precision](139.ragas-context-precision-tutorial.md) |
| 4 | 证据区格式清晰 | [111 注入](111.context-injection-format-tutorial.md) |
| 5 | 长文重排 | [108 Lost in Middle](108.long-context-reorder-tutorial.md) |
| 6 | 控窗口不截断证据 | [28](28.context-window-tutorial.md)、[107](107.context-budget-tutorial.md) |
| 7 | 换更强模型 | [35 API](35.openai-compatible-api-tutorial.md) |

**不要** 只靠「请不要胡说」——没有度量就不知道哪条杠杆有效。

---

## 8. 先错对对：六种典型翻车

### 8.1 错：用 ground_truth 当 contexts 评测

**现象**：分数永远 1.0，上线仍胡编。  
**对**：contexts 必须是 **真实检索进 prompt 的文本**。

### 8.2 错：contexts 用 rerank 前、答案用 rerank 后

**现象**：评测与生产不一致。  
**对**：与线上一致，取 **最终进 [111 注入](111.context-injection-format-tutorial.md) 的列表**。

### 8.3 错：拒答文案当普通答案评

**现象**：「资料不足」被判 unsupported。  
**对**：`expect_refusal: true` 样本 **跳过 faithfulness** 或单独指标。

### 8.4 错：只评 faithfulness 不看不支持 claim

**现象**：均值 0.85 但「天数」全错。  
**对**：落库 **unsupported_claims** 聚类，对接 [152 胡编归因](152.bad-case-hallucination-tutorial.md)。

### 8.5 错：裁判模型与生成模型相同且过弱

**现象**：互相「包庇」，分数虚高。  
**对**：裁判 **≥ 生成能力** 或抽样 **人工复核**。

### 8.6 错：多轮历史拼进 answer 不拼 contexts

**现象**：follow-up 误判 unsupported。  
**对**：多轮评测用 **完整 messages 重建 contexts** [118](118.multi-turn-history-tutorial.md)。

---

## 9. 综合实战：端到端评测与 Claim 审计

**阅读顺序**：§3～§7 + [137 Pipeline](137.pluggable-store-retriever-generator-tutorial.md)。

### 9.1 批量评测

```python
def evaluate_faithfulness(dataset, pipeline):
    rows_out = []
    for ex in dataset:
        out = pipeline.ask(ex["question"])
        contexts = out.get("context_texts", [])
        score = ragas_faithfulness(
            question=ex["question"],
            answer=out["answer"],
            contexts=contexts,
        )
        rows_out.append({{
            "id": ex["id"],
            "faithfulness": score,
            "answer": out["answer"],
        }})
    return rows_out
```

### 9.2 Claim 审计器（可落 trace）

```python
def audit_claims(answer: str, contexts: list[str], judge_llm) -> dict:
    claims = split_claims(answer, judge_llm)
    ctx_block = "\\n---\\n".join(contexts)
    unsupported = []
    for c in claims:
        verdict = judge_llm.generate(
            f"上下文：\\n{{ctx_block}}\\n\\n断言：{{c}}\\n仅回答：支持/不支持"
        )
        if "不支持" in verdict:
            unsupported.append(c)
    return {{
        "claims": claims,
        "unsupported": unsupported,
        "faithfulness": 1 - len(unsupported) / max(len(claims), 1),
    }}
```

**预期输出**：JSON 含 `unsupported` 列表，可写入 [147 LangSmith](147.langsmith-tracing-tutorial.md) metadata。

### 9.3 与 [143 金标](143.golden-dataset-tutorial.md) 联调

金标字段扩展：

```json
{{
  "id": "hr-010",
  "question": "...",
  "ground_truth": "...",
  "relevant_chunk_ids": ["..."],
  "tags": ["faithfulness-critical"],
  "min_faithfulness": 0.85
}}
```

CI：低于 `min_faithfulness` **阻塞合并**（见 [144](144.regression-test-set-tutorial.md)）。

---

## 10. 阈值、拒答与产品策略

| faithfulness | 建议 |
|--------------|------|
| ≥ 0.85 | 正常展示 + 引用 [113] |
| 0.6～0.85 | 展示 + 警示「请核对原文」 |
| < 0.6 | [112 拒答](112.refusal-strategy-tutorial.md) 或仅展示引用片段 |

阈值 **因场景而异**：内规 Bot 从严；创意写作 Bot 可能不评 faithfulness。

与 [28 窗口](28.context-window-tutorial.md)：证据被截断 → faithfulness 假低 → 先查 **预算** 再调阈值。

---

## 11. 与 Context 指标、Relevancy 三角

| 指标 | 问题 |
|------|------|
| Recall [140] | 证据来了吗 |
| Precision [139] | 前排干净吗 |
| Faithfulness | 用了证据吗 |
| Relevancy [142] | 答的是这道题吗 |

**诊断矩阵**：

| Recall | Faithfulness | 猜测 |
|--------|--------------|------|
| 低 | — | 检索 [151](151.bad-case-retrieval-miss-tutorial.md) |
| 高 | 低 | 生成 [152](152.bad-case-hallucination-tutorial.md) |
| 高 | 高 | Relevancy 可能仍低（答非所问） |

---

## 12. 综合概念地图

![Faithfulness 概念地图](image/ragas-faithfulness/03-concept-map.png)

读图：从 [93 检索](93.hybrid-search-tutorial.md) 到 [110 Prompt](110.rag-prompt-template-tutorial.md) 到 **本篇评测**，再到 [144 回归](144.regression-test-set-tutorial.md) 闭环。

---

## 13. 常见陷阱与 FAQ

### 13.1 Faithfulness 与 Accuracy？

Accuracy 对 **标准答案**；Faithfulness 对 **上下文**。资料错时 Accuracy 低、Faithfulness 可高。

### 13.2 需要多少条金标？

起步 **20** 条含 5 条「易胡编」；稳定后 **50+** 分场景。

### 13.3 中文裁判？

选支持中文的 judge 模型；prompt 用中文判 entailment 更稳。

### 13.4 流式答案怎么评？

对 **完整拼接后** 的 answer 评；流式中间态不评。见 [116 SSE](116.sse-rag-streaming-tutorial.md)。

### 13.5 与 [145 DeepEval](145.deepeval-tutorial.md)？

可二选一主标尺；勿混用阈值。DeepEval 亦含 FaithfulnessMetric。

### 13.6 工具调用 [124] 呢？

若答案含工具返回，contexts 应含 **工具结果文本**，否则误判 unsupported。

### 13.7 结构化输出 [123]？

JSON 字段值仍做 claim 审计；不要因格式对了就跳过。

### 13.8 成本？

每条 answer 多次 LLM 调用；用 **回归子集** 全量评 + 生产 **抽样 5%**。

---

## 14. 生产 Runbook 与组织流程

### 14.1 每日巡检

1. 昨日 faithfulness P50/P10；  
2. `unsupported_claims` Top 词；  
3. 与 Recall/Precision 交叉表。

### 14.2 发版门禁

```text
git merge → 跑 [144] 回归集
→ faithfulness 降 >0.05 ? 阻断
→ 否则发布 + 记 pipeline_version
```

### 14.3 与 Bad Case 工单

faithfulness < 阈值 → 自动建 ticket → 标注根因 **检索/生成/资料** → 回流 [143 金标](143.golden-dataset-tutorial.md)。

### 14.4 面试常问

**问**：RAGAS 四指标最该盯哪个？  
**答**：上线 **Faithfulness** 与 **Recall**；体验 **Relevancy**；成本优化看 **Precision**。

---

## 15. 总结与系列下一步

Faithfulness 是 **「开卷仍编」** 的量化刹车，与 [34 Grounding](34.grounding-citation-tutorial.md) 互补：**规矩靠 Prompt，验收靠评测**。

**建议下一步：**

1. [142 Answer Relevancy](142.ragas-answer-relevancy-tutorial.md)；  
2. [143 Golden Dataset](143.golden-dataset-tutorial.md) 建库；  
3. [144 回归集](144.regression-test-set-tutorial.md) 接入 CI；  
4. [152 Bad Case 胡编](152.bad-case-hallucination-tutorial.md) 归因演练。

---

*系列：E 评测与观测 · 路线图第 158 条 · 主线篇*
"""

BODIES["142.ragas-answer-relevancy-tutorial.md"] = f"""# E 评测与观测（四）：RAGAS Answer Relevancy 完全指南

> 答案句句有据（[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 高），但用户问「年假几天」，模型大谈「食堂开放时间」——**答非所问**。**Answer Relevancy**（答案相关性）用 **反向问题** 等技巧衡量：**回答是否对准用户意图**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨地基篇**（路线图第 **159** 条）。前置：[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[109 对话 Query 增强](109.conversation-query-enhancement-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)。

---

## 目录

1. [前言：忠实但不相关](#1-前言忠实但不相关)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Answer Relevancy 是什么](#3-answer-relevancy-是什么)
4. [反向问题直觉](#4-反向问题直觉)
5. [RAGAS 实现要点](#5-ragas-实现要点)
6. [与多轮、指代消解](#6-与多轮指代消解)
7. [与 Faithfulness 分工](#7-与-faithfulness-分工)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：四指标一起跑](#9-综合实战四指标一起跑)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [指标权重与产品场景](#12-指标权重与产品场景)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：忠实但不相关

| 用户问 | 答案（全有据） | Faithfulness | Relevancy |
|--------|----------------|--------------|-----------|
| 年假几天？ | 食堂 11:30 开门… | 高 | 低 |
| 年假几天？ | 10 天，另：病假… | 高 | 中 |

**Answer Relevancy**：生成答案与用户 **问题意图** 的匹配度。  
通俗说：**考生答案每句都能在原书里找到，但答的是另一道题**。

---

## 2. 本文边界与动手路径

**档位：E 轨地基（159）。**

| 步骤 | 验收 |
|------|------|
| A | 解释反向问题 |
| B | ragas answer_relevancy |
| C | 与 faithfulness 同表 |

### 2.2 沿用前文

{COMMON_RAG_LINKS}

---

## 3. Answer Relevancy 是什么

![Answer Relevancy](image/ragas-answer-relevancy/01-relevancy-idea.png)

读图：从 answer 生成「可能的问题」，与原 question 比语义相似度。

---

## 4. 反向问题直觉

```text
原问题 Q: 年假有多少天？
答案 A: ...（可能冗长）
生成 Q': 这个答案像在回答什么问题？（×n 次平均）
Relevancy ≈ sim(Q, Q')
```

**演示**：

```python
from ragas.metrics import answer_relevancy
# 与 faithfulness 等同属 evaluate() 指标族
```

---

## 5. RAGAS 实现要点

- 通常 **不需** ground_truth，只需 `question` + `answer`；  
- 依赖 **Embedding** 算 sim；与 [25](25.embedding-vector-tutorial.md) 同族；  
- 多轮时 question 用 **增强后检索 query** [109](109.conversation-query-enhancement-tutorial.md) 或完整用户意图。

---

## 6. 与多轮、指代消解

用户：「试用期呢？」（上一轮谈劳动合同）  
评测 question 若只用最后一轮 → Relevancy 误判。  
**对**：用 [120 指代](120.coreference-resolution-tutorial.md) 或 [109](109.conversation-query-enhancement-tutorial.md) 展开为 **standalone question** 再评。

---

## 7. 与 Faithfulness 分工

| 指标 | 锚点 |
|------|------|
| Faithfulness | contexts |
| Relevancy | question |

两者都高才是 **理想答案**；一高一低指导不同改法（Prompt vs 检索噪声）。

---

## 8. 先错对对：四种典型翻车

{_mistakes([
    ("冗长答案不惩罚", "Faithfulness 高、Relevancy 被废话拉低。", "Prompt 要求「仅答所问」[110]。"),
    ("拒答当低 Relevancy", "「资料不足」语义上与问句不相似。", "拒答样本跳过或单独指标。"),
    ("用英文 Embedding 评中文", "分数噪声大。", "换多语 Embedding [70]。"),
    ("只评 Relevancy 不看 Faithfulness", "答得很贴但全编。", "四指标同看 [139-142]。"),
])}

---

## 9. 综合实战：四指标一起跑

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision, context_recall, faithfulness, answer_relevancy,
)

metrics = [context_precision, context_recall, faithfulness, answer_relevancy]
result = evaluate(dataset, metrics=metrics)
```

输出 CSV 进看板；绑定 [138 pipeline version](138.config-driven-pipeline-tutorial.md)。

---

## 10. 综合概念地图

![Relevancy 概念地图](image/ragas-answer-relevancy/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{_faq([
    ("Relevancy 最低多少？", "无万能线；对比发版 delta。"),
    ("与人工「满意度」？", "抽样算相关；Relevancy 作筛子。"),
    ("创意 Bot 要低 Relevancy？", "可降权重，不能不看。"),
    ("与 [142] 重复？", "本篇即 142 号路线图 Answer Relevancy。"),
    ("DeepEval 对应？", "见 [145](145.deepeval-tutorial.md) AnswerRelevancyMetric。"),
])}

---

## 12. 指标权重与产品场景

| 场景 | Faithfulness | Relevancy |
|------|--------------|-----------|
| 制度问答 | 0.4 | 0.3 |
| 检索摘要 | 0.35 | 0.35 |
| 闲聊混合 | 0.3 | 0.4 |

权重写进 PRD，避免算法与产品各说各话。

---

## 13. 总结与系列下一步

四指标齐活后，进入 [143 金标](143.golden-dataset-tutorial.md) **工程化** 与 [144 回归](144.regression-test-set-tutorial.md)。

---

*系列：E 评测与观测 · 路线图第 159 条 · 地基篇*
"""

BODIES["143.golden-dataset-tutorial.md"] = f"""# E 评测与观测（五）：Golden Dataset 构建完全指南

> RAGAS 四指标跑起来了，没有 **稳定、可版本化、带金标准答案与证据 id** 的数据集，分数只是 **一次性实验**。**Golden Dataset**（金标数据集）是 E 轨 **数据地基**：让 [139–142](139.ragas-context-precision-tutorial.md) 每次发版可对比、让 [144 回归](144.regression-test-set-tutorial.md) 有源头。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨主线篇**（路线图第 **160** 条），厚流程导向。前置：全链 [93–112](93.hybrid-search-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[136–138 可插拔与配置](136.pluggable-parser-splitter-embedder-tutorial.md)。

---

## 目录

1. [前言：没有金标就没有工程](#1-前言没有金标就没有工程)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Golden Dataset 是什么](#3-golden-dataset-是什么)
4. [字段 Schema 与版本](#4-字段-schema-与版本)
5. [冷启动：二十条从哪来](#5-冷启动二十条从哪来)
6. [标注流程与质量](#6-标注流程与质量)
7. [与 RAGAS 四指标对齐](#7-与-ragas-四指标对齐)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：JSONL 仓库与评测 CLI](#9-综合实战jsonl-仓库与评测-cli)
10. [生长策略：从日志采样](#10-生长策略从日志采样)
11. [治理：脱敏、权限、生命周期](#11-治理脱敏权限生命周期)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [与回归集、CI 的分工](#14-与回归集ci-的分工)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：没有金标就没有工程

面试第 8 题：「RAGAS 四指标含义？」——能背还不够。追问：「你们金标谁标、多少条、怎么更新？」答不上来，等于 **没做过评测闭环**。

**Golden Dataset**（金标数据集）：每条含 **问题、标准答案、相关 chunk id、标签与难度** 的 **版本化** 评测集。  
通俗说：**带标准答案的模拟考卷库**，不是生产日志随便抓几行。

**读完本文，你应该能做到：**

1. 设计 §4 **JSONL Schema**。  
2. 完成 **20 条冷启动** 标注（§5～§6）。  
3. 用 §9 CLI 跑四指标并出报告。  
4. 写 **生长与治理** 规则（§10～§11）。  
5. 区分 [144 回归集](144.regression-test-set-tutorial.md)（§14）。

### 1.1 主线位置

```text
139-142 RAGAS 指标
160 Golden Dataset ← 本篇（主线）
161 Regression Set [144]
162 DeepEval [145]（了解）
```

---

## 2. 本文边界与动手路径

**档位：E 轨主线（160，厚流程）。**

| 步骤 | 验收 |
|------|------|
| A | Schema 定稿 |
| B | 标 20 条 |
| C | CLI 出四指标 |
| D | version bump 规则 |
| E | 脱敏检查 |

---

## 3. Golden Dataset 是什么

![Golden Dataset](image/golden-dataset/01-golden-idea.png)

读图：左侧生产日志噪声，右侧金标 **结构化 + 人审 + 版本**。

---

## 4. 字段 Schema 与版本

```json
{{
  "schema_version": "1.0",
  "dataset_version": "golden-hr-2026.04.01",
  "items": [
    {{
      "id": "hr-001",
      "question": "工作满一年年假几天？",
      "ground_truth": "10天带薪年假。",
      "relevant_chunk_ids": ["handbook-v3:sec3:c2"],
      "tags": ["hr", "annual-leave", "faithfulness-critical"],
      "difficulty": "easy",
      "expect_refusal": false,
      "metadata": {{"locale": "zh-CN"}}
    }}
  ]
}}
```

| 字段 | 必填 | 用途 |
|------|------|------|
| id | 是 | 追溯 |
| question | 是 | 输入 |
| ground_truth | 是 | Recall/Precision 判据 |
| relevant_chunk_ids | 是 | 检索金标 |
| expect_refusal | 否 | [112](112.refusal-strategy-tutorial.md) |
| tags | 否 | 分场景报表 |

**dataset_version**：改题 bump minor；换业务域 bump major（见 [154 参数版本](154.param-version-management-tutorial.md)）。

---

## 5. 冷启动：二十条从哪来

| 来源 | 条数建议 | 说明 |
|------|----------|------|
| 产品/运营 FAQ | 8 | 高频刚需 |
| 文档章节标题改写 | 6 | 覆盖 [62 结构切块](62.structure-aware-chunking-tutorial.md) |
| 边界：拒答/越权 | 3 | [112][121] |
| 易胡编数字题 | 3 | 盯 [141](141.ragas-faithfulness-tutorial.md) |

**不要** 等「一千条再开始」——二十条足够 первый baseline。

---

## 6. 标注流程与质量

```text
起草（业务）→ 法务/领域审 → 绑定 chunk_id（工程）→ 双人抽检 10%
```

**chunk_id** 必须来自 **当前索引** [51](51.metadata-chunk-id-tutorial.md)；标了找不到的 id，Recall 评测作废。

---

## 7. 与 RAGAS 四指标对齐

| 字段 | 指标 |
|------|------|
| relevant_chunk_ids | Precision, Recall |
| ground_truth | Precision/Recall 辅助 |
| 跑 pipeline 得 answer+contexts | Faithfulness, Relevancy |

评测时固定 [138 config](138.config-driven-pipeline-tutorial.md) 与 [29 temperature=0](29.llm-sampling-tutorial.md)。

---

## 8. 先错对对：五种典型翻车

### 8.1 金标答案抄模型输出

**对**：人读 **原文** 写 ground_truth。

### 8.2 relevant 标整章

**对**：**最小充分** chunk 集。

### 8.3 永不更新

**对**：季度审计；制度变更同步 [48 版本](48.doc-versioning-tutorial.md)。

### 8.4 含 PII 进 Git

**对**：加密桶 + CI 用合成子集。

### 8.5 只有简单句

**对**：加 [104 多跳](104.multi-hop-retrieval-tutorial.md)、[109 多轮](109.conversation-query-enhancement-tutorial.md) 样例。

---

## 9. 综合实战：JSONL 仓库与评测 CLI

**演示目标**：`python -m eval.run --dataset golden/hr.jsonl --config config/pipeline.yaml`  
**预期**：`report.json` 含四指标均值与逐条明细。

```python
# eval/run.py 骨架
import json, argparse
from pathlib import Path

def load_items(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["items"], data.get("dataset_version")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--config", default="config/pipeline.yaml")
    args = ap.parse_args()
    items, ver = load_items(Path(args.dataset))
    pipeline = build_pipeline_from_config(args.config)
    report = run_ragas_all(items, pipeline)
    report["dataset_version"] = ver
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

报告进 wiki；发版对比 **同一 dataset_version** 下的 delta。

---

## 10. 生长策略：从日志采样

每周从 [147 trace](147.langsmith-tracing-tutorial.md)：

1. faithfulness 低分；  
2. 用户点踩；  
3. 人工升级工单 [149-152](149.bad-case-parsing-tutorial.md)。

**去重** [47](47.doc-dedup-tutorial.md) 后 **人审** 入库；不是自动进金标。

---

## 11. 治理：脱敏、权限、生命周期

| 风险 | 措施 |
|------|------|
| PII | 脱敏/哈希 |
| 机密制度 | 内网桶 ACL |
| 过时 | `deprecated: true` 不删历史 |

---

## 12. 综合概念地图

![Golden 概念地图](image/golden-dataset/03-concept-map.png)

---

## 13. 常见陷阱与 FAQ

{_faq([
    ("多少条够？", "20 起步，50 稳，200+ 分场景。"),
    ("谁标注？", "业务写问题，领域专家写答案，工程绑 id。"),
    ("多语言？", "分 dataset 或 items 标 locale。"),
    ("与训练微调？", "金标可作数据；勿与评测集泄漏。"),
    ("开源合规？", "勿上传客户真实数据。"),
])}

---

## 14. 与回归集、CI 的分工

| | Golden | Regression [144] |
|---|--------|------------------|
| 规模 | 50～500 | 10～30 |
| 频率 | 周/月全量 | 每次 PR |
| 内容 | 全覆盖 | 关键路径+历史 bug |

回归集 = 金标 **子集** + **必现 bug 复现**。

---

## 15. 总结与系列下一步

金标是 **可重复科学** 的前提；没有 version，就没有 [153 A/B](153.ab-experiment-rag-tutorial.md)。

**下一步：** [144 回归](144.regression-test-set-tutorial.md)、[145 DeepEval](145.deepeval-tutorial.md)、[155 人工评测](155.human-evaluation-rag-tutorial.md)。

---

*系列：E 评测与观测 · 路线图第 160 条 · 主线篇*
"""

BODIES["144.regression-test-set-tutorial.md"] = f"""# E 评测与观测（六）：回归测试集维护完全指南

> [143 金标](143.golden-dataset-tutorial.md) 可以很大、跑很久；每次改 [138 配置](138.config-driven-pipeline-tutorial.md) 或 [110 Prompt](110.rag-prompt-template-tutorial.md) 若全量跑一小时，团队会放弃评测。**回归测试集**（Regression Test Set）是 **小而硬** 的子集：**每次合并必跑、几分钟出结果、任一核心题倒退就阻断**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨地基篇**（路线图第 **161** 条）。前置：[143 Golden](143.golden-dataset-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)。

---

## 目录

1. [前言：全量金标与 PR 门禁](#1-前言全量金标与-pr-门禁)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [回归测试集是什么](#3-回归测试集是什么)
4. [选题：必须覆盖什么](#4-选题必须覆盖什么)
5. [阈值与 Flaky 处理](#5-阈值与-flaky-处理)
6. [CI 集成骨架](#6-ci-集成骨架)
7. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
8. [综合实战：GitHub Actions 示例](#9-综合实战github-actions-示例)
9. [与 nightly 全量分工](#10-与-nightly-全量分工)
10. [综合概念地图](#11-综合概念地图)
11. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
12. [维护节奏与所有权](#13-维护节奏与所有权)
13. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：全量金标与 PR 门禁

**回归测试集**：从金标与历史 bug **精选的固定小题库**，用于 **高频自动评测**。  
通俗说：**每次交卷前先做的十道必考题**，不是五百题模拟卷。

---

## 2. 本文边界与动手路径

| 步骤 | 验收 |
|------|------|
| A | 选 15～30 条 |
| B | CI workflow |
| C | 失败 artifact |

---

## 3. 回归测试集是什么

![回归集](image/regression-test-set/01-regression-idea.png)

---

## 4. 选题：必须覆盖什么

| 类型 | 条数 | 示例 |
|------|------|------|
| 核心 FAQ | 5 | 年假 |
| faithfulness 敏感 | 3 | 数字/日期 |
| 拒答 | 2 | [112](112.refusal-strategy-tutorial.md) |
| ACL | 2 | [121](121.unauthorized-doc-filter-tutorial.md) |
| 历史 P0 bug | 每 bug 1 | 工单链接 |

---

## 5. 阈值与 Flaky 处理

| 指标 | PR 阻断 | 告警 |
|------|---------|------|
| faithfulness 均值 | -0.05 | -0.02 |
| recall 均值 | -0.08 | -0.03 |

固定 [29 temperature=0](29.llm-sampling-tutorial.md)；波动大标 flaky 重跑 3 次取中位数。

---

## 6. CI 集成骨架

```yaml
# .github/workflows/rag-regression.yml
name: rag-regression
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {{ python-version: "3.11" }}
      - run: pip install -r requirements-eval.txt
      - run: python -m eval.run --dataset regression/core.jsonl --config config/pipeline.yaml --fail-on-regression
```

---

## 7. 先错对对：四种典型翻车

{_mistakes([
    ("回归集过大", "CI 15 分钟没人等。", "≤30 条 + nightly 全量。"),
    ("阈值过严误杀", "随机波动阻断正常 PR。", "delta 阈值 + flaky 策略。"),
    ("失败无 artifact", "不知哪题挂。", "上传 report.json + answer diff。"),
    ("与金标不同步", "题还在、chunk 已删。", "每月对齐 [51 chunk_id](51.metadata-chunk-id-tutorial.md)。"),
])}

---

## 8. 综合实战：GitHub Actions 示例

`--fail-on-regression` 对比 `baseline/report.json`（main 分支缓存）。

---

## 9. 与 nightly 全量分工

| | PR 回归 | Nightly |
|---|---------|---------|
| 数据 | regression/ | golden/ 全量 |
| 时间 | <5min | <60min |
| 阻断 | 是 | 告警 |

---

## 10. 综合概念地图

![回归概念地图](image/regression-test-set/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{_faq([
    ("回归集谁维护？", "算法+QA共管；bug 必须加例。"),
    ("能否只用规则不用 RAGAS？", "可；faithfulness 建议保留 LLM 判。"),
    ("多分支 baseline？", "每 release 分支缓存 baseline。"),
    ("与 [145 DeepEval](145.deepeval-tutorial.md)？", "可 `deepeval test run` 作替代入口。"),
    ("无 GPU？", "评测调 API，不需 GPU。"),
])}

---

## 12. 维护节奏与所有权

- **每周**：检查 flaky；  
- **每 sprint**：从新 bug 加 1 例；  
- **每季**：删过时题。

---

## 13. 总结与系列下一步

回归集让 **评测真正挡住烂 PR**；全量金标保证 **覆盖度**。

**下一步：** [145 DeepEval](145.deepeval-tutorial.md)、[147 LangSmith](147.langsmith-tracing-tutorial.md)。

---

*系列：E 评测与观测 · 路线图第 161 条 · 地基篇*
"""

BODIES["145.deepeval-tutorial.md"] = f"""# E 评测与观测（七）：DeepEval 了解完全指南

> [139–142](139.ragas-context-precision-tutorial.md) 用 **RAGAS** 讲清四指标；工程团队若已深度使用 **pytest**，可能更想要 **测试框架原生** 的 LLM 评测。**DeepEval** 是开源 LLM 评测库，提供 **Faithfulness、Contextual Precision/Recall、Answer Relevancy** 等与 RAGAS 同族的指标，并能 `pytest` 断言。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨了解篇**（路线图第 **162** 条）——**知道即可、与 RAGAS 二选一主标尺**，不必两套并行。前置：[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[144 回归](144.regression-test-set-tutorial.md)。

---

## 目录

1. [前言：为什么还有一个评测库](#1-前言为什么还有一个评测库)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [DeepEval 是什么](#3-deepeval-是什么)
4. [与 RAGAS 对照](#4-与-ragas-对照)
5. [核心 Metric 一览](#5-核心-metric-一览)
6. [LLMTestCase 与 assert_test](#6-llmtestcase-与-assert_test)
7. [pytest 集成](#7-pytest-集成)
8. [先错对对：三种典型翻车](#8-先错对对三种典型翻车)
9. [综合实战：最小 pytest 文件](#9-综合实战最小-pytest-文件)
10. [何时选 DeepEval vs RAGAS](#10-何时选-deepeval-vs-ragas)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么还有一个评测库

RAGAS 偏 **数据集 evaluate()**；DeepEval 偏 **单测 assert**。团队文化不同，工具不同——**指标思想一致**（Faithfulness 等），**数值不可横比**。

**DeepEval**：面向 LLM 应用的 Python 评测框架，支持 RAG 指标与 G-Eval 自定义 rubric。  
通俗说：**给 LLM 应用写的单元测试库**。

**档位：了解篇**——能跑通 §9 即可；生产主标尺仍推荐 [141 RAGAS](141.ragas-faithfulness-tutorial.md) + [143 金标](143.golden-dataset-tutorial.md)。

---

## 2. 本文边界与动手路径

| 步骤 | 验收 |
|------|------|
| A | `pip install deepeval` |
| B | 跑通 §9 一个 test |
| C | 填对照表 §4 |

---

## 3. DeepEval 是什么

![DeepEval 定位](image/deepeval/01-deepeval-idea.png)

读图：pytest → DeepEval Metric → 裁判 LLM → pass/fail。

---

## 4. 与 RAGAS 对照

| 维度 | RAGAS | DeepEval |
|------|-------|----------|
| 入口 | `evaluate(dataset)` | `assert_test(case, metrics)` |
| CI | 脚本 | pytest 原生 |
| 指标族 | 四指标 | 同名类似 |
| 数值 | — | **不可与 RAGAS 直接比** |

---

## 5. 核心 Metric 一览

| DeepEval | 对应 RAGAS |
|----------|------------|
| FaithfulnessMetric | faithfulness |
| ContextualPrecisionMetric | context_precision |
| ContextualRecallMetric | context_recall |
| AnswerRelevancyMetric | answer_relevancy |

均需 **裁判模型** 成本，见 [27 Token 计费](27.token-counting-billing-tutorial.md)。

---

## 6. LLMTestCase 与 assert_test

```python
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric
from deepeval import assert_test

case = LLMTestCase(
    input="年假几天？",
    actual_output="10天年假。",
    retrieval_context=["工作满一年享受10天年假。"],
)
assert_test(case, [FaithfulnessMetric(threshold=0.8)])
```

**演示**：单条 faithfulness 断言。  
**环境**：`pip install deepeval` + API Key。  
**预期**：pytest 通过或失败可见分数。

---

## 7. pytest 集成

```python
# tests/test_rag_regression.py
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric

@pytest.mark.parametrize("row", load_regression_rows())
def test_faithfulness(row):
    case = LLMTestCase(
        input=row["question"],
        actual_output=run_pipeline(row["question"]),
        retrieval_context=row["contexts"],
    )
    assert_test(case, [FaithfulnessMetric(threshold=0.8)])
```

与 [144 回归集](144.regression-test-set-tutorial.md) JSONL 共用数据。

---

## 8. 先错对对：三种典型翻车

### 8.1 两套标尺混用阈值

**对**：选定 RAGAS **或** DeepEval 作主标尺。

### 8.2 把 production 日志当 retrieval_context

**对**：与线上一致，用真实进 prompt 的 contexts。

### 8.3 了解篇当主线大投入

**对**：PoC 用 RAGAS [141] 跑通再评估是否迁 pytest。

---

## 9. 综合实战：最小 pytest 文件

见 §7；`deepeval test run` 或 `pytest tests/test_rag_regression.py`。

---

## 10. 何时选 DeepEval vs RAGAS

| 选 DeepEval | 选 RAGAS |
|-------------|----------|
| 团队 pytest 文化浓 | 已有 ragas 报表 |
| 要 G-Eval 自定义 rubric | 与 HF Dataset 生态 |
| 单测粒度细 | 批量 evaluate 为主 |

**了解篇结论**：两套都知；**先精通 RAGAS 主线 [141]**。

---

## 11. 综合概念地图

![DeepEval 概念地图](image/deepeval/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

{_faq([
    ("DeepEval 替代 RAGAS？", "二选一主标尺，不必并行。"),
    ("成本？", "与 RAGAS 同属 LLM-as-judge。"),
    ("与 [146 TruLens](146.trulens-tutorial.md)？", "TruLens 偏追踪+反馈；本篇仅评测断言。"),
    ("无网络？", "需调裁判 API 或配本地模型。"),
    ("中文？", "选支持中文的 judge model。"),
])}

---

## 13. 总结与系列下一步

DeepEval 是 **pytest 派的 RAG 评测备选**；掌握 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 与 [143 金标](143.golden-dataset-tutorial.md) 后按需选用。

**下一步：** [146 TruLens](146.trulens-tutorial.md)、[147 LangSmith](147.langsmith-tracing-tutorial.md)、[148 Langfuse](148.langfuse-observability-tutorial.md)。

---

*系列：E 评测与观测 · 路线图第 162 条 · 了解篇*
"""
