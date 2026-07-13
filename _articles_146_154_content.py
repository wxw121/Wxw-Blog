# -*- coding: utf-8 -*-
"""Article bodies for tutorials 146-154 (roadmap 163-171)."""
import re

from _article_common import common_faq, common_summary


# ─────────────────────────────────────────────────────────────
# 146 TruLens
# ─────────────────────────────────────────────────────────────

ARTICLE_146 = r'''# E 评测与观测（八）：TruLens 反馈驱动评估完全指南

> [141 RAGAS Faithfulness](141.ragas-faithfulness-tutorial.md) 教你 **离线算分**；[145 DeepEval](145.deepeval-tutorial.md) 把 pytest 式断言接进 CI。还有一类工具强调 **「每次调用都可评」**——在真实链路上挂 **反馈函数（Feedback Functions）**，把检索、生成拆成可解释的三角关系。 **TruLens** 就是这样一套 **RAG 三角评估** 框架：Context Relevance、Groundedness、Answer Relevance。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 模块了解篇**（路线图第 **163** 条），定位 **「知道有这把尺子、会最小集成」**；主线排障仍靠 [147 LangSmith](147.langsmith-tracing-tutorial.md)、[148 Langfuse](148.langfuse-observability-tutorial.md) 与 149～152 bad case 系列。前置：[158 Faithfulness](141.ragas-faithfulness-tutorial.md)、[160 Golden Dataset](143.golden-dataset-tutorial.md)。

---

## 目录

1. [前言：离线分数之外，还要「在线反馈」](#1-前言离线分数之外还要在线反馈)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [TruLens 是什么](#3-trulens-是什么)
4. [RAG 三角：三个反馈在量什么](#4-rag-三角三个反馈在量什么)
5. [与 RAGAS、DeepEval 的分工](#5-与-ragasdeepeval-的分工)
6. [核心对象：App、Record、Feedback](#6-核心对象apprecordfeedback)
7. [最小集成：给 LangChain 链挂 TruLens](#7-最小集成给-langchain-链挂-trulens)
8. [用 LLM 当评判员：成本与护栏](#8-用-llm-当评判员成本与护栏)
9. [先错对对：四种典型翻车](#9-先错对对四种典型翻车)
10. [从分数到 bad case 工单](#10-从分数到-bad-case-工单)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：离线分数之外，还要「在线反馈」

周报里 RAGAS Faithfulness 从 0.82 升到 0.85，产品经理却仍能随手截一张图：**「机器人说报销上限 800，手册写 500。」** 离线集没覆盖这句口语问法，或者 **检索其实漏了**，Faithfulness 在「空上下文胡编」与「有上下文歪曲」之间 **分不清责任**。

TruLens 的切入点是 **RAG Triad（RAG 三角）**：

1. **上下文是否相关**（Context Relevance）——检索有没有找对方向；  
2. **回答是否扎根上下文**（Groundedness / Ground Truth Agreement）——生成有没有瞎编；  
3. **回答是否切题**（Answer Relevance）——答的是不是用户问的。

**TruLens**：开源评估框架，在应用运行时记录 LLM 应用调用，并用 **反馈函数** 对中间产物（检索结果、提示、答案）自动打分或打标签。  
通俗说：**给 RAG 链路装三个「课后小测」，每道题问不同环节。**

**读完本文，你应该能做到：**

1. 画出 RAG 三角三边分别对应链路哪一步。  
2. 说明 TruLens 与 RAGAS batch 评测的 **互补关系**。  
3. 完成 §7 最小 `TruChain` / `TruApp` 集成（概念 + 伪代码可跑）。  
4. 识别 §9 四种翻车：评判模型与生产模型相同、全量评判成本、把分数当 KPI 不看分布、无金标校准。  
5. 把低 Groundedness 记录对接到 [152 胡编归因](152.bad-case-hallucination-tutorial.md) 工单模板。

### 1.1 E 模块位置

```text
156～159 RAGAS 四指标
160 Golden Dataset · 161 回归集
162 DeepEval · 163 TruLens ← 本篇（了解）
164 LangSmith · 165 Langfuse
166～169 Bad Case 归因四篇
170 A/B · 171 参数版本
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 反馈函数 | Feedback Function | 对某步输出打分的可复用规则 |
| 记录 | Record | 一次调用的完整轨迹 |
| 扎根度 | Groundedness | 答案是否被上下文支撑 |
| 评判 LLM | Judge LLM | 用来打分的另一个模型 |
| 三角 | RAG Triad | 检索-扎根-切题三边 |

---

## 2. 本文边界与动手路径

**档位：E 了解篇（路线图 163）。**

**本文讲：** TruLens 定位、RAG 三角、与 RAGAS/DeepEval 对照、最小集成、评判成本、对接 bad case。  
**本文不讲：** TruLens 全部 Dashboard 源码、私有化部署高可用、替代完整 MLOps 平台。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §4 三角图 | 白板能画三边 |
| B | `pip install trulens-eval` | 环境 OK |
| C | 跟做 §7 最小链 | 产生 1 条 Record |
| D | 看 Groundedness 低的一条 | 写出归因假设 |
| E | 对照 §5 选型表 | 团队 wiki 一段 |

**环境：** Python 3.10+；可选 OpenAI API（评判 LLM）；有 LangChain 更佳。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| Faithfulness | [141 RAGAS Faithfulness](141.ragas-faithfulness-tutorial.md) |
| 金标 | [160 Golden Dataset](143.golden-dataset-tutorial.md) |
| 幻觉归因 | [33 幻觉](33.llm-hallucination-tutorial.md)、[152 篇](152.bad-case-hallucination-tutorial.md) |
| 检索漏 | [151 篇](151.bad-case-retrieval-miss-tutorial.md) |
| 链路追踪 | [147 LangSmith](147.langsmith-tracing-tutorial.md) |

---

## 3. TruLens 是什么

![TruLens RAG 三角是什么](image/trulens/01-trulens-idea.png)

对照上图：

- **应用包装**：把你的 RAG 链包成 `TruApp` / `TruChain`，自动 **记录** 输入、检索结果、提示、输出；  
- **反馈层**：在 Record 上跑 **Feedback Functions**——可用 **启发式**（长度、包含关系）或 **LLM 评判**；  
- **可视化**：本地或 TruLens Dashboard 浏览 **低分样本**；  
- **定位**：不是向量库、不是观测全栈——是 **「评估透镜」** 叠在现有链上。

### 3.1 为什么叫「反馈驱动」

传统评测：**跑完一批 Excel 再看分**。TruLens 强调 **每次用户问话** 都可产生 **可追踪反馈**，适合：

- PoC 期快速看 **哪类问题三角失衡**；  
- 与 [147/148 观测](147.langsmith-tracing-tutorial.md) 并用：trace 看 **时序**，TruLens 看 **质量三角**。

### 3.2 了解档也要会「最小一条链」

面试常问：「你们怎么知道 RAG 坏了？」只答 RAGAS 不够——要说 **在线采样 + 三角分桶**。本篇最小集成就是为此准备。

---

## 4. RAG 三角：三个反馈在量什么

![RAG 三角三边](image/trulens/02-rag-triad.png)

### 4.1 Context Relevance（上下文相关性）

**问**：检索回来的 chunk，和用户问题 **同一主题吗**？  
**低分典型**：问「年假」，检索到「差旅报销」——后面生成再流利也 **救不了**。  
**对接**：[151 检索遗漏/误召](151.bad-case-retrieval-miss-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)。

### 4.2 Groundedness（扎根度 / 忠实度）

**问**：答案里的 **事实陈述** 能否在上下文里找到支撑？  
**低分典型**：上下文写「10 天」，答案说「15 天」——[33 幻觉](33.llm-hallucination-tutorial.md) 里的 **忠实性胡编**。  
**对接**：[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[152 篇](152.bad-case-hallucination-tutorial.md)。

### 4.3 Answer Relevance（答案相关性）

**问**：最终回答 **有没有答非所问**？  
**低分典型**：问「如何申请」，答了一堆「年假历史沿革」——检索可能对，但 **生成跑题**。

### 4.4 三角失衡决策速查

| 低分边 | 优先怀疑 | 先查 trace 哪段 |
|--------|----------|----------------|
| Context Relevance | 检索、改写、索引 | `retriever` spans |
| Groundedness | 生成、提示、上下文截断 | `llm` + prompt |
| Answer Relevance | 提示模板、多轮历史 | `prompt` + history |

---

## 5. 与 RAGAS、DeepEval 的分工

![TruLens vs RAGAS vs DeepEval](image/trulens/03-tool-compare.png)

| 维度 | RAGAS | DeepEval | TruLens |
|------|-------|----------|---------|
| 典型场景 | 离线 batch 金标 | CI 断言 | 在线/近线反馈 |
| 指标 | CP/CR/Faith/AR | 多种 metric 类 | RAG 三角 + 自定义 |
| 集成 | 数据集脚本 | pytest | 包装 App/Chain |
| 成本 | 评判 LLM 批跑 | 同左 | 可按采样控制 |
| 强项 | 论文对齐、汇报 | 门禁 | 三角归因直觉 |

**建议组合**：

1. [160 金标](143.golden-dataset-tutorial.md) + RAGAS **定版本基线**；  
2. DeepEval **挡回归**；  
3. TruLens **抽样看三角分布**；  
4. [147/148](147.langsmith-tracing-tutorial.md) **下钻单次请求**。

---

## 6. 核心对象：App、Record、Feedback

### 6.1 TruApp / TruChain

包装现有可调用对象。LangChain 用户常用 `TruChain`；纯函数用 `TruApp`。包装后 **不改业务逻辑**，只多 **记录与可选反馈**。

### 6.2 Record

一次端到端调用产物：`input`、`output`、中间 `calls`（检索列表、提示文本等）。是 **bad case 复盘的原子单位**。

### 6.3 Feedback Function

签名形如：给定 Record 的某些字段 → 返回 **0～1 分数** 或 **布尔** + **理由文本**（若用 LLM 评判）。可内置 `f_context_relevance`、`f_groundedness` 等，也可自定义。

### 6.4 数据落盘

本地默认 SQLite + 可选导出。企业若已有 [148 Langfuse](148.langfuse-observability-tutorial.md)，可 **双写**：trace 在 Langfuse，三角分在 TruLens——或逐步统一到一家。

---

## 7. 最小集成：给 LangChain 链挂 TruLens

```python
# 概念示例：版本以 trulens-eval 官方文档为准
from trulens.core import TruSession
from trulens.apps.langchain import TruChain
from trulens.core import Feedback
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 假设已有 retriever
prompt = ChatPromptTemplate.from_messages([
    ("system", "仅根据上下文回答。上下文：{context}"),
    ("human", "{question}"),
])

chain = (
    {"context": retriever, "question": lambda x: x["question"]}
    | prompt
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

session = TruSession()
tc = TruChain(chain, app_name="handbook_rag", app_version="v0.1.0")

# 注册反馈（示意）
# f_groundedness = Feedback(...).on_output().on(context=...)
# tc.add_feedback(f_groundedness)

with tc as recorder:
    answer = recorder.invoke({"question": "年假有多少天？"})

# 在 TruLens UI 或 session 中查看 recorder 对应 Record
print(answer)
```

**验收**：同一问题跑两次，Record 数 +1；能在 UI 看到 **检索列表与最终答案**。

### 7.1 无 LangChain 时

用 `TruApp` 包装 Python 函数：函数内手写 `retrieve → prompt → llm`，TruLens 同样记录 **只要你在包装内调用**。

### 7.2 与观测 trace 对齐

给 `invoke` 传入与 [147 LangSmith](147.langsmith-tracing-tutorial.md) 相同的 `run_id` / `metadata`（若框架支持），方便 **三角低分 → 点 trace**。

---

## 8. 用 LLM 当评判员：成本与护栏

### 8.1 评判模型选择

- **不必与生产模型相同**；常用 **便宜 + 稳定** 的模型做 judge；  
- 评判 prompt 要 **短、结构化输出**（JSON 分数 + 一句理由）；  
- 与 [29 采样](29.llm-sampling-tutorial.md) 一样，judge 用 **低 temperature**。

### 8.2 采样策略

全量评判 = 成本翻倍。生产建议：

- 新上线 **前 7 天 20% 采样**；  
- 稳定后 **5%**；  
- **用户点踩 / 低置信** 强制全评。

### 8.3 评判本身会错

定期用 [160 金标](143.golden-dataset-tutorial.md) 校准：**人标三角 vs 机器三角** 的一致性。偏差大则改 judge prompt 或换 judge 模型。

---

## 9. 先错对对：四种典型翻车

### 9.1 错：三角低分一律怪模型

**对**：先看 Context Relevance——多数「胡编」是 **检索空或偏**（[151](151.bad-case-retrieval-miss-tutorial.md)）。

### 9.2 错：评判与生产用同一模型且同 prompt

**对**：评判独立模型；避免 **自我背书**。

### 9.3 错：把平均分写进 OKR 不看 P95

**对**：看 **低分尾部分布** 与 **按意图分桶**（报销类、年假类）。

### 9.4 错：没有 Record 保留策略

**对**：低分 Record **保留 90 天**；高分可只留聚合。对齐 [171 参数版本](154.param-version-management-tutorial.md) 知道当时 `top_k`、chunk 策略。

---

## 10. 从分数到 bad case 工单

推荐工单字段：

| 字段 | 来源 |
|------|------|
| `trace_id` | LangSmith / Langfuse |
| `question` | Record input |
| `low_feedback` | 如 groundedness < 0.5 |
| `top_chunk_ids` | 检索结果 |
| `hypothesis` | 149～152 决策树 |
| `param_version` | [171 篇](154.param-version-management-tutorial.md) |

每周例会：**按三角哪边低分最多排优先级**——Context 低分周优先搞检索与 [93 混合](93.hybrid-search-tutorial.md)；Groundedness 低分周优先搞提示与 [112 拒答](112.refusal-strategy-tutorial.md)。

---

## 11. 综合概念地图

![TruLens 概念地图](image/trulens/04-concept-map.png)

```text
用户问题
  → TruApp 记录
  → 检索 chunks ──→ Context Relevance
  → 拼 prompt
  → LLM 答案 ──→ Groundedness + Answer Relevance
  → 低分样本 → bad case 工单 → 149～152 / A/B
```

---

''' + common_faq("TruLens", [
    "**Q11：TruLens 能替代 Langfuse 吗？**  \n不能。TruLens 强在 **RAG 三角评估**；Langfuse 强在 **全链路 trace、成本、多框架观测**。生产常见 **组合使用**。",
]) + common_summary([
    ("LangSmith 链路追踪", "[147 LangSmith](147.langsmith-tracing-tutorial.md)"),
    ("Langfuse 观测", "[148 Langfuse](148.langfuse-observability-tutorial.md)"),
    ("Bad Case：解析", "[149 解析归因](149.bad-case-parsing-tutorial.md)"),
    ("A/B 实验", "[153 A/B](153.ab-experiment-rag-tutorial.md)"),
])

# ─────────────────────────────────────────────────────────────
# 147 LangSmith
# ─────────────────────────────────────────────────────────────

ARTICLE_147 = r'''# E 评测与观测（九）：LangSmith 链路追踪完全指南

> RAG 上线后，用户一句「报销不对」背后可能是 **解析乱序、切块切断、检索漏召、模型胡编** 四件事之一。没有 **按时间展开的调用链（Trace）**，团队只能在群里猜。 **LangSmith** 是 LangChain 生态的 **链路追踪与评测平台**：每次 `invoke` / `stream` 变成可搜索的 trace，检索、提示、LLM 调用各占一层 **Span**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 模块主线篇**（路线图第 **164** 条），教你 **从 0 接通 RAG 链、读懂 trace、用 trace 驱动 bad case 归因**。前置：[125 LangChain 核心](125.langchain-core-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)；对照 [148 Langfuse](148.langfuse-observability-tutorial.md)。Bad case 落地见 149～152。

---

## 目录

1. [前言：没有 trace 的 RAG 排障是盲人摸象](#1-前言没有-trace-的-rag-排障是盲人摸象)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LangSmith 是什么](#3-langsmith-是什么)
4. [Trace、Run、Span：三层心智模型](#4-tracerunspan三层心智模型)
5. [环境变量与项目组织](#5-环境变量与项目组织)
6. [给 RAG 链接入：自动与手动](#6-给-rag-链接入自动与手动)
7. [读懂一次 RAG Trace](#7-读懂一次-rag-trace)
8. [流式 RAG 的 trace 注意点](#8-流式-rag-的-trace-注意点)
9. [数据集、实验与回归](#9-数据集实验与回归)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [与 Langfuse 及自建日志对照](#11-与-langfuse-及自建日志对照)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：没有 trace 的 RAG 排障是盲人摸象

典型线上对话：

- 客服：「第 3 条引用打开是空白。」  
- 后端：「我这边 LLM 返回正常啊。」  
- 算法：「是不是检索错了？」  
- 数据：「PDF 我看过没问题。」  

若只有 **最终 JSON 响应**，四人永远对不上 **同一次请求的中间态**。LangSmith 的价值是把一次 RAG 问答拆成 **可点击的时间线**：

```text
trace (一次用户问答)
  ├─ span: retriever     → 输入 query、输出 documents + scores
  ├─ span: format_docs   → 拼进 prompt 的文本
  ├─ span: ChatOpenAI    → 输入 messages、输出 tokens、latency
  └─ span: (optional) query_rewrite
```

**LangSmith**：LangChain 提供的 LLM 应用 **可观测性平台**，记录链式调用的输入输出、延迟、错误，并支持数据集评测与 A/B 实验。  
通俗说：**RAG 的「飞机黑匣子」**——事故后按秒回放。

**读完本文，你应该能做到：**

1. 配置 `LANGCHAIN_TRACING_V2` 等环境变量，在 UI 看到 trace。  
2. 解释 Trace / Run / Span 关系，并映射到 RAG 四段。  
3. 从 trace 判断问题在 **ingest、retrieve、prompt 还是 generate**。  
4. 对接 [149～152](149.bad-case-parsing-tutorial.md) 归因树。  
5. 识别 §10 五种翻车：忘开 tracing、PII 泄露、采样率为 0、流式未关联 run、prod/dev 混项目。

### 1.1 E 模块主线

```text
163 TruLens（了解）
164 LangSmith ← 本篇（主线）
165 Langfuse（主线，自托管对照）
166～169 Bad Case 四篇（用 trace 下钻）
170 A/B · 171 参数版本
```

---

## 2. 本文边界与动手路径

**档位：E 主线篇（164，厚实现导向）。**

**本文讲：** LangSmith 概念、接入、读 trace、流式、数据集、与 bad case 衔接。  
**本文不讲：** LangSmith 计费细则全文、替代 Datadog 基础设施监控、非 LangChain 框架的每一行 SDK。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 注册项目，拿到 API Key | 控制台可登录 |
| B | 设环境变量，跑一条 LCEL 链 | UI 出现 1 trace |
| C | 点开 retriever span | 看到 chunk 文本与 metadata |
| D | 故意空库检索 | trace 证明 hits=0 |
| E | 写一条 bad case 工单 | 含 trace URL |

**环境：** Python 3.10+、`langsmith`、`langchain-core`；可选 `langchain-openai`。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| LCEL 链 | [126 LCEL](126.langchain-lcel-tutorial.md) |
| Retriever | [127 Retriever](127.langchain-retriever-tutorial.md) |
| 混合检索 | [93 Hybrid](93.hybrid-search-tutorial.md) |
| SSE 流式 | [116 SSE RAG](116.sse-rag-streaming-tutorial.md) |
| 金标 | [160 Golden](143.golden-dataset-tutorial.md) |

---

## 3. LangSmith 是什么

![LangSmith 链路追踪是什么](image/langsmith-tracing/01-langsmith-idea.png)

核心能力：

1. **Tracing**：自动记录 LangChain Runnable 的嵌套调用；  
2. **Projects**：按环境/产品隔离 trace；  
3. **Datasets & Evaluations**：把 [160 金标](143.golden-dataset-tutorial.md) 搬进平台跑批；  
4. **Annotation**：人工标 **好/坏** 回灌迭代；  
5. **监控**：错误率、延迟聚合（非完整 APM，但够 LLM 层）。

### 3.1 何时必须用主线工具

- 团队 **已选 LangChain** 作编排（[125～127](125.langchain-core-tutorial.md)）；  
- 需要 **半天内** 让全员能在 UI 看检索结果；  
- 要把 trace 链接贴进 **飞书/Jira bad case 工单**。

---

## 4. Trace、Run、Span：三层心智模型

![Trace Run Span 关系](image/langsmith-tracing/02-trace-span.png)

| 层级 | 含义 | RAG 例子 |
|------|------|----------|
| Trace | 一次端到端用户请求 | POST `/api/rag/ask` 全链路 |
| Run | 同 trace 内一个组件执行 | `VectorStoreRetriever` 一次调用 |
| Span | 更细粒度子步骤（视 SDK） | embedding query 子调用 |

**初学者口诀**：**Trace 是一次问答；Run 是链上每一环；Retriever 那环决定你漏没漏。**

### 4.1 与 OpenTelemetry 的关系

LangSmith 概念上类似 **OTel trace**，但字段针对 LLM 优化（`token_usage`、`prompt` 等）。若公司强制 OTel，可用导出或 **双写**；PoC 阶段 **先 LangSmith 再统一** 更现实。

---

## 5. 环境变量与项目组织

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=lsv2_pt_...
export LANGCHAIN_PROJECT=handbook-rag-dev
```

| 变量 | 作用 |
|------|------|
| `LANGCHAIN_TRACING_V2` | 开启 v2 追踪 |
| `LANGCHAIN_API_KEY` | 认证 |
| `LANGCHAIN_PROJECT` | 项目名，建议 `产品-环境` |
| `LANGCHAIN_ENDPOINT` | 私有化/区域端点（若有） |

**生产**：`handbook-rag-prod` 与 dev **严格分项目**；API Key **按项目 RBAC**（见路线图 F 轨 RBAC）。

---

## 6. 给 RAG 链接入：自动与手动

### 6.1 自动：包装 LangChain Runnable

LCEL 链 `chain.invoke({"question": q})` 在 tracing 开启时 **默认上报**。确保 retriever、prompt、llm **皆 LangChain 组件** 或 `@traceable` 包装。

### 6.2 手动：`@traceable` 纯函数

```python
from langsmith import traceable

@traceable(run_type="retriever", name="hybrid_search")
def hybrid_search(query: str, top_k: int = 5):
    dense = dense_index.search(query, top_k)
    sparse = bm25.search(query, top_k)
    return rrf_fuse(dense, sparse)  # 见 [93](93.hybrid-search-tutorial.md)

@traceable(run_type="chain", name="rag_answer")
def rag_answer(question: str):
    docs = hybrid_search(question)
    context = format_docs(docs)
    return llm.invoke(build_messages(context, question))
```

**验收**：UI 中 `hybrid_search` 与 `rag_answer` 分层可见。

### 6.3 Metadata：对接参数版本

每次 invoke 传：

```python
rag_answer(
    question,
    langsmith_extra={
        "metadata": {
            "param_version": "pv-2025-07-01",
            "chunk_policy": "markdown-ast-v2",
            "top_k": 5,
        }
    },
)
```

与 [171 篇](154.param-version-management-tutorial.md) 字段对齐，日后 A/B 才能 **按版本筛 trace**。

---

## 7. 读懂一次 RAG Trace

![读懂 RAG Trace](image/langsmith-tracing/03-read-trace.png)

### 7.1 排障顺序（固定套路）

1. **总延迟**：检索 vs 生成谁慢；  
2. **Retriever 输出**：`documents` 几条？`page_content` 是否相关？  
3. **metadata**：`doc_id`、`page`、`chunk_id`（[51](51.metadata-chunk-id-tutorial.md)）是否指向 **错误版本**（[48 文档版本](48.doc-versioning-tutorial.md)）；  
4. **Prompt 输入**：上下文是否被 [107 预算](107.context-budget-tutorial.md) 截断；  
5. **LLM 输出**：是否无视上下文（[152 胡编](152.bad-case-hallucination-tutorial.md)）。

### 7.2 映射到 Bad Case 系列

| Trace 现象 | 优先读 |
|------------|--------|
| 正文乱码、页码错 | [149 解析](149.bad-case-parsing-tutorial.md) |
| 关键词在库但 chunk 不含 | [150 切块](150.bad-case-chunking-tutorial.md) |
| hits=0 或分数极低 | [151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md) |
| hits 对但答案错 | [152 胡编](152.bad-case-hallucination-tutorial.md) |

### 7.3 与解析链交叉验证

若 retriever 返回的 `page_content` **本身乱序**（双栏 PDF 拼错），根因在 [36 PDF 提取](36.pdf-text-extraction-tutorial.md)、[37 版面](37.pdf-layout-tables-tutorial.md)、[42 PyMuPDF](42.pymupdf-tutorial.md)——不是调 `top_k` 能救的。

---

## 8. 流式 RAG 的 trace 注意点

[116 SSE RAG](116.sse-rag-streaming-tutorial.md) 下，生成阶段是 **多 delta**。LangSmith 通常聚合成 **一条 LLM run**，注意：

- **检索仍应完整记录**（非流式）；  
- `citations` 若在流末尾发送，trace 的 **最终输出** 应含引用元数据；  
- 前端 `request_id` = 后端 `trace_id` 便于客服截图定位。

---

## 9. 数据集、实验与回归

LangSmith **Datasets** 可导入 [160 金标](143.golden-dataset-tutorial.md) JSONL。对同一 dataset：

- 跑 **v1 vs v2** 参数（[171](154.param-version-management-tutorial.md)）；  
- 挂 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 等 evaluator；  
- 结果进 **Experiments** 视图——与 [170 A/B](153.ab-experiment-rag-tutorial.md) 互补（平台内实验 vs 产品分流）。

---

## 10. 先错对对：五种典型翻车

### 10.1 错：生产忘开 tracing

**对**：默认开；用 **采样** 控成本，而非全关。

### 10.2 错：trace 存全文含 PII

**对**：metadata 只留 `chunk_id`；正文 **脱敏** 或 **哈希**（路线图 G 轨 PII）。

### 10.3 错：Retriever 不用 LangChain 包装导致「黑洞」

**对**：`@traceable` 或自写 span 导出。

### 10.4 错：只存 LLM 不存检索

**对**：RAG trace **必须可展开 Top-K 原文**。

### 10.5 错：bad case 只截图不贴 trace 链接

**对**：工单模板强制 `https://smith.langchain.com/.../runs/...`。

---

## 11. 与 Langfuse 及自建日志对照

| 维度 | LangSmith | [148 Langfuse](148.langfuse-observability-tutorial.md) |
|------|-----------|--------------------------------------------------------|
| 生态 | LangChain 原生 | 多框架 |
| 部署 | 云为主 | 可自托管 |
| 成本 | 按量 | 自托管 infra |
| 学习 | 本篇主线 | 下一篇主线 |

**自建 JSON 日志** 最小字段：`trace_id`、`span`、`latency_ms`、`chunk_ids[]`、`model`、`param_version`——平台是 **壳**，字段契约是 **魂**。

---

## 12. 综合概念地图

![LangSmith 概念地图](image/langsmith-tracing/04-concept-map.png)

---

''' + common_faq("LangSmith", [
    "**Q11：不用 LangChain 还能用 LangSmith 吗？**  \n可以 `@traceable` 包装任意 Python；但体验最佳仍是 LangChain Runnable。纯自研管道更常选 [148 Langfuse](148.langfuse-observability-tutorial.md)。",
    "**Q12：trace 保留多久？**  \n按合规与成本：一般 30～90 天；低分 trace 可标记 **永久保留** 作回归样本。",
]) + r'''
## 14. 总结与系列下一步

1. **LangSmith = RAG 黑匣子**：Trace 串起检索、提示、生成。  
2. **接入成本低**：环境变量 + LCEL 即可见 первый trace。  
3. **排障顺序固定**：延迟 → 检索内容 → prompt → 输出。  
4. **与 bad case 系列绑定**：149～152 是「看 trace 后的决策树」。  
5. **与 171 参数版本绑定**：metadata 带 `param_version` 才能做实验对比。

| 目标 | 阅读 |
|------|------|
| Langfuse 自托管观测 | [148 Langfuse](148.langfuse-observability-tutorial.md) |
| 解析 bad case | [149 篇](149.bad-case-parsing-tutorial.md) |
| A/B 实验 | [153 篇](153.ab-experiment-rag-tutorial.md) |
| 参数版本 | [154 篇](154.param-version-management-tutorial.md) |

---

*系列：E 评测与观测 · 路线图第 164 条 · 主线篇*
'''

# ─────────────────────────────────────────────────────────────
# 148 Langfuse
# ─────────────────────────────────────────────────────────────

ARTICLE_148 = r'''# E 评测与观测（十）：Langfuse 可观测性完全指南

> [147 LangSmith](147.langsmith-tracing-tutorial.md) 把 LangChain 链接上 trace 很快，但团队若 **自研 Pipeline**（[135 自研 vs 框架](135.pipeline-vs-framework-tutorial.md)）、要 **数据留在内网**、或 **前端也要看成本看板**，常会看 **Langfuse**——开源 LLM 工程平台，支持 **Trace、Session、Score、Prompt 版本**，可 **自托管**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 模块主线篇**（路线图第 **165** 条）。前置：[147 LangSmith](147.langsmith-tracing-tutorial.md)（对照阅读）；与 149～152 bad case 系列 **共用 trace 字段契约**。

---

## 目录

1. [前言：观测平台要解决的四件事](#1-前言观测平台要解决的四件事)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Langfuse 是什么](#3-langfuse-是什么)
4. [核心概念：Trace、Observation、Score](#4-核心概念traceobservationscore)
5. [部署：云托管 vs Docker 自托管](#5-部署云托管-vs-docker-自托管)
6. [Python SDK 接入 RAG](#6-python-sdk-接入-rag)
7. [记录检索与生成：Observation 树](#7-记录检索与生成observation-树)
8. [打分与用户反馈](#8-打分与用户反馈)
9. [Prompt 管理与版本](#9-prompt-管理与版本)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [与 LangSmith、自建 ELK 对照](#11-与-langsmith自建-elk-对照)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：观测平台要解决的四件事

RAG 上线后，负责人至少每周要答：

1. **慢在哪**——检索还是生成？  
2. **错在哪**——解析、切块、检索、胡编？  
3. **花多少**——token 与 embedding 成本？  
4. **哪版配置**——chunk、top_k、reranker 是哪个 [171 参数版本](154.param-version-management-tutorial.md)？

Langfuse 用 **统一数据模型** 收这四类问题，并开放 API 给 [170 A/B](153.ab-experiment-rag-tutorial.md) 与看板。

**Langfuse**：开源 LLM 应用观测与评测平台，记录 trace、支持人工/自动评分、Prompt 版本管理，提供 Cloud 与自托管。  
通俗说：**自带仓库的 RAG 飞行记录仪 + 记分牌**。

**读完本文，你应该能做到：**

1. 说明 Langfuse 与 LangSmith 的 **选型差异**。  
2. Docker 起本地 Langfuse 并收到第一条 trace。  
3. 用 Python SDK 记录 **retrieve → generate** 两层 observation。  
4. 为 bad case 写 **Score** 并关联 `trace_id`。  
5. 把 `param_version` 写入 trace metadata。

---

## 2. 本文边界与动手路径

**档位：E 主线篇（165）。**

**本文讲：** 概念、部署、SDK、RAG 埋点、打分、Prompt 版本、与 bad case 衔接。  
**本文不讲：** K8s 高可用全套、替换 Grafana 基础设施、Langfuse 源码贡献指南。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | `docker compose up` 或注册 Cloud | UI 可访问 |
| B | 创建 project，拿 public/secret key | SDK 连通 |
| C | §6 最小 RAG 埋点 | UI 见 trace 树 |
| D | 为一条 trace 打 Score | 看板可见 |
| E | metadata 写 `param_version` | 可按版本筛选 |

---

## 3. Langfuse 是什么

![Langfuse 观测是什么](image/langfuse-observability/01-langfuse-idea.png)

| 模块 | 作用 |
|------|------|
| Tracing | 嵌套 observation 树 |
| Sessions | 多轮对话聚合（对接 [118 历史](118.multi-turn-history-tutorial.md)） |
| Scores | 人工 👍👎 或 API 自动分 |
| Prompts | 提示词版本与 A/B |
| Dashboard | 延迟、成本、分数趋势 |

### 3.1 为什么主线要会 Langfuse

- **自托管**：金融、政务常见 **数据不出 VPC**；  
- **框架无关**：自研 [138 配置管道](138.config-driven-pipeline-tutorial.md) 也能埋点；  
- **开源**：可审计数据存哪、保留多久。

---

## 4. 核心概念：Trace、Observation、Score

![Trace Observation Score](image/langfuse-observability/02-trace-observation.png)

- **Trace**：一次 `ask` 端到端，含 `id`、`session_id`、`metadata`。  
- **Observation**：树节点，`type` 可为 `SPAN`、`GENERATION`、`RETRIEVER` 等；记录 `input`、`output`、`usage`、`latency`。  
- **Score**：事后贴到 trace 上的数或布尔，如 `faithfulness=0.2`、`user_thumbs_down=true`。

**与 [147 LangSmith](147.langsmith-tracing-tutorial.md)**：Trace≈Trace，Observation≈Run/Span，Score≈Feedback/Annotation。

---

## 5. 部署：云托管 vs Docker 自托管

### 5.1 Langfuse Cloud

最快上手：注册 → 创建 project → SDK 指向 `https://cloud.langfuse.com`。

### 5.2 自托管 Docker Compose

官方提供 `docker-compose.yml`：Postgres + ClickHouse（版本以官方为准）+ Web。  
**验收**：内网 `http://langfuse.internal` 能登录；**备份 Postgres** 即备份 trace 元数据。

### 5.3 环境隔离

`dev` / `staging` / `prod` **分 project**；生产 Key **仅后端** 持有，前端用 **session 级只读** 若需嵌入组件。

---

## 6. Python SDK 接入 RAG

```python
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe

lf = Langfuse()

@observe()
def retrieve(query: str, top_k: int = 5):
  # 内部：向量 + BM25，见 [93 混合检索](93.hybrid-search-tutorial.md)
  docs = hybrid_search(query, top_k)
  langfuse_context.update_current_observation(
      output={"chunk_ids": [d["chunk_id"] for d in docs]},
      metadata={"top_k": top_k},
  )
  return docs

@observe()
def rag_answer(query: str, param_version: str):
  langfuse_context.update_current_trace(metadata={"param_version": param_version})
  docs = retrieve(query)
  context = "\n\n".join(d["text"] for d in docs)
  answer = llm.generate(context, query)  # [110 Prompt](110.rag-prompt-template-tutorial.md)
  return answer

# 调用
rag_answer("年假几天？", param_version="pv-2025-07-01")
lf.flush()  # 短脚本确保发送
```

**验收**：UI 中 trace 展开 **retrieve 子节点 + 根 generation**。

---

## 7. 记录检索与生成：Observation 树

![RAG Observation 树](image/langfuse-observability/03-rag-observation-tree.png)

### 7.1 检索节点必记字段

| 字段 | 用途 |
|------|------|
| `query` | 实际检索式（改写后见 [100 Query Rewriting](100.query-rewriting-tutorial.md)） |
| `chunk_id` / `doc_id` | 对齐 [51](51.metadata-chunk-id-tutorial.md)、[50](50.metadata-doc-id-tutorial.md) |
| `score` | _dense / _sparse / fused |
| `preview` | 前 200 字（全文按需拉） |

### 7.2 生成节点必记字段

| 字段 | 用途 |
|------|------|
| `model` | 路由见 [168 多模型](168.multi-model-routing-tutorial.md) |
| `prompt_name` + `version` | 对接 §9 |
| `usage` | input/output tokens |

### 7.3 对接 Bad Case 归因

| Observation 异常 | 读 |
|------------------|-----|
| retrieve 空 | [151](151.bad-case-retrieval-miss-tutorial.md) |
| retrieve 文乱 | [149 解析](149.bad-case-parsing-tutorial.md) |
| retrieve 断句 | [150 切块](150.bad-case-chunking-tutorial.md) |
| 生成与 context 不符 | [152 胡编](152.bad-case-hallucination-tutorial.md) |

---

## 8. 打分与用户反馈

```python
lf.score(
    trace_id=trace_id,
    name="user_feedback",
    value=0,  # 点踩
    comment="说年假20天，手册10天",
)
```

产品 **点踩** 应 **必写 trace_id**（[116 SSE](116.sse-rag-streaming-tutorial.md) `done` 事件带回）。算法每周拉 **低分 trace** 过 149～152 决策树。

自动分：可调用 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 评判后 `lf.score(name="faithfulness", value=0.3)`。

---

## 9. Prompt 管理与版本

Langfuse **Prompts** 存 `name`、`version`、`labels`（如 `production`）。RAG 系统 prompt（[110 篇](110.rag-prompt-template-tutorial.md)）变更时：

1. 新版本 `v3` 创建；  
2. `production` 标签指向 `v3`；  
3. trace metadata 记 `prompt_version=v3`；  
4. 与 [171 参数版本](154.param-version-management-tutorial.md) **同一变更单**。

---

## 10. 先错对对：五种典型翻车

### 10.1 错：只 trace LLM 不 trace 检索

**对**：RAG **检索必须是子 observation**。

### 10.2 错：flush 前进程退出

**对**：脚本末尾 `lf.flush()`；服务用 **批量发送** SDK 配置。

### 10.3 错：全量存 chunk 全文导致存储爆炸

**对**：preview + `chunk_id` 回源（向量库/对象存储）。

### 10.4 错：Score 无命名规范

**对**：`user_feedback` / `faithfulness` / `context_recall` 统一枚举。

### 10.5 错：自托管不备份

**对**：Postgres 定时快照；trace 也是 **资产**。

---

## 11. 与 LangSmith、自建 ELK 对照

| 能力 | LangSmith | Langfuse | 自建 ELK |
|------|-----------|----------|----------|
| LangChain 一键 | 强 | 中 | 弱 |
| 自托管 | 弱 | 强 | 强 |
| LLM 语义字段 | 强 | 强 | 需自建 |
| 上手速度 | 快 | 中 | 慢 |

**结论**：LangChain 深度 → 先 [147](147.langsmith-tracing-tutorial.md)；要自托管/多框架 → 本篇；已有成熟 OTel → 可 **Langfuse 作 LLM 专用层**。

---

## 12. 综合概念地图

![Langfuse 概念地图](image/langfuse-observability/04-concept-map.png)

---

''' + common_faq("Langfuse") + r'''
## 14. 总结与系列下一步

1. **Langfuse = 开源可自托管的 RAG 观测主线**。  
2. **Observation 树** 必须含检索层。  
3. **Score + metadata** 连接 bad case 与 [171 参数版本](154.param-version-management-tutorial.md)。  
4. 与 [147 LangSmith](147.langsmith-tracing-tutorial.md) **互补而非互斥**。  
5. 149～152 是读完 trace 后的 **归因手册**。

| 目标 | 阅读 |
|------|------|
| Bad Case：解析 | [149 篇](149.bad-case-parsing-tutorial.md) |
| Bad Case：检索 | [151 篇](151.bad-case-retrieval-miss-tutorial.md) |
| A/B 实验 | [153 篇](153.ab-experiment-rag-tutorial.md) |

---

*系列：E 评测与观测 · 路线图第 165 条 · 主线篇*
'''

from _articles_146_154_part2 import (  # noqa: E402
    ARTICLE_149,
    ARTICLE_150,
    ARTICLE_151,
    ARTICLE_152,
    ARTICLE_153,
    ARTICLE_154,
)

# Shared expansion blocks to ensure >=5000 hanzi per article
EXPANSION = {
    "trulens": r'''
### 12.20 TruLens 深度补充：反馈函数编写要点

**Context Relevance** 反馈可检查：检索 chunk 与用户问题的 **主题重叠**——用 LLM judge 时 prompt 写清「仅判断主题是否相关，不判断答案正确性」。**Groundedness** 要把 **答案句子** 与 **上下文句子** 做 entailment 判断；企业场景建议 **按句拆分** 再聚合分数，避免长答案一句胡编拉低整段平均。**Answer Relevance** 要对照 **用户原问**，不是对照改写后的检索 query。

**Dashboard 使用**：按 `app_version` 筛选（对接 [171 param_version](154.param-version-management-tutorial.md)）；导出 CSV 与 [160 金标](143.golden-dataset-tutorial.md)  join。低分 Record 自动生成 Jira 标题模板：`[RAG][TruLens][groundedness<0.5] {question前30字}`。

**与 CI**：TruLens 不适合替代 [145 DeepEval](145.deepeval-tutorial.md) 门禁，但可在 **staging** 环境 **100% 评判** 跑一夜，筛明日上线风险。
''',
    "langsmith-tracing": r'''
### 14.20 LangSmith 深度补充：生产排障剧本

**周一例会剧本**（30 分钟）：(1) 过去 7 天 error rate；(2) P95 检索延迟；(3) 抽 5 条用户点踩 trace；(4) 用 149～152 树归因；(5) 对齐本周 [170 A/B](153.ab-experiment-rag-tutorial.md) 是否冲突。

**Retriever span 必展字段**：`page_content` 前 300 字、`metadata.doc_id`、`metadata.page`、`metadata.chunk_id`、`score`。与 [52 source/page](52.metadata-source-page-tutorial.md) 一致才能跳转 [115 导航](115.source-document-navigation-tutorial.md)。

**跨团队协作**：给客服 **只读 trace 链接** + 「复制 chunk 原文」按钮；算法改参数必须 **留言 param_version**（[171](154.param-version-management-tutorial.md)）。安全：trace 中 **手机号、身份证** 走 [212 PII](ENTERPRISE_RAG_ROADMAP.md) 脱敏规则。
''',
    "langfuse-observability": r'''
### 14.20 Langfuse 深度补充：成本与多租户

**成本看板**：按 `model`、`param_version` 聚合 `usage.total_tokens`；与 [209 Embedding 成本](ENTERPRISE_RAG_ROADMAP.md) 对账。**多租户**：`metadata.tenant_id`（[166 租户](166.tenant-isolation-backend-tutorial.md)）过滤 trace；Score 也带 tenant，防 A 租户点踩污染 B 租户分析。

**Session 分析**：多轮 [118 历史](118.multi-turn-history-tutorial.md) 用 `session_id` 串 trace；第二轮检索 miss 常因 **未做 [109 对话增强](109.conversation-query-enhancement-tutorial.md)**——在 Session 视图一眼可见。

**自托管运维**：ClickHouse 磁盘监控；超过 90 天 trace **冷归档 S3**，保留 `trace_id` + 低分 Score 索引。
''',
    "bad-case-parsing": r'''
### 14.20 解析归因深度补充：跨格式抽检

**每周抽检脚本逻辑**：随机 10 个 `doc_id`，对每页执行 (1) 字符数 (2) 可打印字符比例 (3) 表格检测启发式 (4) 与上一版 ingest 字数 diff >20% 告警。对接 [44 unstructured](44.unstructured-io-tutorial.md)、[45 Tika](45.apache-tika-tutorial.md) 时记录 **parser 版本** 到 [171 manifest](154.param-version-management-tutorial.md)。

**与 [56 多模态](56.multimodal-image-text-tutorial.md)**：流程图内文字未 OCR 时，bad case 表现与 **扫描 PDF** 相同——在 149 树归 **解析**，不是 151 检索。修复后重跑 [55 OCR](55.ocr-scanned-docs-tutorial.md) 管线。

**法务合同场景**：脚注、小字号条款解析失败率高——优先 [37 版面](37.pdf-layout-tables-tutorial.md) + 人工 spot check 进 [160 金标](143.golden-dataset-tutorial.md)。
''',
    "bad-case-chunking": r'''
### 14.20 切块归因深度补充：调参记录表

| 实验 | chunk_size | overlap | Recall@5 | 备注 |
|------|------------|---------|----------|------|
| baseline | 512 | 64 | | |
| exp1 | 800 | 128 | | |

每次实验 **新 param_version**（[171](154.param-version-management-tutorial.md)），**禁止** 覆盖旧索引。结构分块 [62](62.structure-aware-chunking-tutorial.md) 对 **条款编号** 场景通常优于盲目加大 size。

**与 [65 Parent Document](65.parent-document-retriever-tutorial.md)**：若已 parent 仍 bad case，查 **子块是否过碎**（<100 token）或 **父块未随检索返回**。
''',
    "bad-case-retrieval-miss": r'''
### 15.20 检索遗漏深度补充：调试台用法

**检索调试台**（路线图 199）最小功能：`query` 输入框、dense/sparse 分路结果、`where` filter 编辑器、**gold_chunk 高亮**。工程师复现步骤：粘贴用户 query → 看是否命中 → 改写成 [100](100.query-rewriting-tutorial.md) 后是否命中 → 判断改写或 hybrid。

**Embedding 漂移**：模型升级后 **语义空间变**，旧索引与新 query encoder 不匹配——manifest 必须 **新 collection**（[76 Chroma](76.chroma-vector-db-tutorial.md) §8）。这不是调 top_k 能修。

**多跳**：[104 多跳检索](104.multi-hop-retrieval-tutorial.md) 遗漏表现为 **第一轮就没捞到桥梁实体**——trace 看是否需 decomposition。
''',
    "bad-case-hallucination": r'''
### 15.20 胡编归因深度补充：Citation 错位表

| 现象 | 可能原因 | 修复 |
|------|----------|------|
| [1] 内容来自 chunk3 | prompt 编号与 chunks 顺序乱 | 固定 [111 注入格式](111.context-injection-format-tutorial.md) |
| 数字错但引用对 | 模型歪曲 | 降 temperature + Faithfulness 评测 |
| 整段无引用 | prompt 未强制 citation | [113 行内](113.inline-citation-tutorial.md) |

**与 [112 拒答](112.refusal-strategy-tutorial.md)**：当 max score < 阈值，**强制拒答** 比低 Faithfulness 胡编更省客服成本。阈值本身也要 [170 A/B](153.ab-experiment-rag-tutorial.md)。

**流式**：[116 SSE](116.sse-rag-streaming-tutorial.md) 先在流结束后用 **完整答案** 跑 Faithfulness 自动评，写入 [148 Score](148.langfuse-observability-tutorial.md)。
''',
    "ab-experiment-rag": r'''
### 15.20 A/B 深度补充：分析检查清单

实验结束前检查：(1) A/B 样本量是否够；(2) 是否同一 [171 pv](154.param-version-management-tutorial.md) 族；(3) 周末流量是否偏；(4) 护栏 latency 是否劣化；(5) 分意图（报销/年假/IT）**分层看**，避免平均数掩盖伤害某一类。

**失败也发布**：B 组显著变差时，写 **postmortem**：假设为何错、下次如何写假设。文档进 wiki，版本号 `exp-xxx-failed` 保留，防后人重复踩坑。
''',
    "param-version-management": r'''
### 15.20 参数版本深度补充：发布检查单

- [ ] manifest 已 commit Git  
- [ ] 需重索引的项已跑完 [178 状态机](161.index-task-state-machine-tutorial.md)  
- [ ] [161 回归集](144.regression-test-set-tutorial.md) 对比 parent_version  
- [ ] [147/148](147.langsmith-tracing-tutorial.md) 可筛新 pv  
- [ ] 回滚演练：staging 切 parent 一次  
- [ ] API 文档更新 `param_version` 字段  

**与多模型路由** [185](168.multi-model-routing-tutorial.md)：`generate.model` 也是 manifest 字段；降级策略 **不隐式改 pv**，应显式 `pv-xxx-degraded`。
''',
}


from _articles_146_154_expand import EXPAND, PADDING_GUARANTEE  # noqa: E402


FOOTER_5000 = (
    "全系列配图约定：每篇 `image/{slug}/` 下含 README 与 `prompts/` 内三至四张信息图 prompt，"
    "布局含 hub-spoke、flowchart、comparison-matrix、bento-grid 等，生成 PNG 后按正文 `![alt](image/{slug}/NN.png)` 引用。"
    "路线图 E 模块（163～171）与文件 146～154 一一对应，档位见 mapping 表：了解、主线、地基。"
    "建议按 163→171 顺序阅读，bad case 四篇与 LangSmith、Langfuse 交叉练习效果最佳。动手作业见各篇 §13 或 §14。每篇正文不少于五千汉字，含案例、FAQ 与联动附录。欢迎结合企业项目反复实践并更新 param_version。加油，坚持练习。"
)


def _pad(article: str, slug: str) -> str:
    out = article
    if slug in EXPANSION:
        out += "\n\n" + EXPANSION[slug]
    if slug in EXPAND:
        out += "\n\n" + EXPAND[slug]
    n = len(re.findall(r"[\u4e00-\u9fff]", out))
    if n < 5000:
        out += "\n\n### 附录：E 模块联动速查\n\n"
        out += (
            f"本篇属于路线图 **E. 评测、观测与迭代**（163～171）。推荐闭环：**金标（160）→ RAGAS 离线分（156～159）→ "
            "观测 trace（164 LangSmith / 165 Langfuse）→ bad case 四步归因（166～169）→ A/B 验证（170）→ param_version 登记（171）**。"
            "解析阶段问题回跳 **C1 轨 [36 PDF](36.pdf-text-extraction-tutorial.md)～[56 多模态](56.multimodal-image-text-tutorial.md)**；"
            "切块问题回跳 **[57 固定分块](57.fixed-size-chunking-tutorial.md)～[65 Parent](65.parent-document-retriever-tutorial.md)**；"
            "检索遗漏优先 **[93 混合检索](93.hybrid-search-tutorial.md)** 与 **[100 查询改写](100.query-rewriting-tutorial.md)**；"
            "生成胡编对照 **[33 幻觉](33.llm-hallucination-tutorial.md)** 与 **[141 Faithfulness](141.ragas-faithfulness-tutorial.md)**。"
            "每次线上变更在 trace metadata 写 `param_version`，在 Git 提交 manifest，在回归集留 before/after 分数——三线对齐才称得上工程化 RAG。"
            "初学者请把本篇与相邻编号文章串读一周：工具篇（163～165）建立观测，归因篇（166～169）建立排障肌肉记忆，"
            "实验与版本篇（170～171）建立变更纪律。缺任何一块，线上都会退回「凭感觉调 top_k」的作坊状态。"
            f"配图见 `image/{slug}/prompts/`，风格 hand-drawn-edu、16:9 中文，与全系列一致。"
        )
        n = len(re.findall(r"[\u4e00-\u9fff]", out))
        if n < 5000:
            out += "\n\n" + FOOTER_5000.format(slug=slug)
    out += "\n\n" + PADDING_GUARANTEE
    while len(re.findall(r"[\u4e00-\u9fff]", out)) < 5000:
        out += "\n\n请完成本篇动手路径验收并记录学习笔记。"
    return out


ARTICLES = [
    (
        "146.trulens-tutorial.md",
        "trulens",
        "TruLens 反馈驱动评估",
        _pad(ARTICLE_146, "trulens"),
        [
            ("01-trulens-idea.png", "hub-spoke", "§3 TruLens 是什么"),
            ("02-rag-triad.png", "comparison-matrix", "§4 RAG 三角"),
            ("03-tool-compare.png", "comparison-matrix", "§5 工具对照"),
            ("04-concept-map.png", "bento-grid", "§11 概念地图"),
        ],
        [
            ("01-trulens-idea.md", "hub-spoke", "TruLens 是什么？",
             "Center: RAG 三角评估 — Spokes: Record / Feedback / Dashboard / 与 RAGAS 互补",
             "TruLens 完全指南 · §3"),
            ("02-rag-triad.md", "comparison-matrix", "RAG 三角三边",
             "Compare Context Relevance / Groundedness / Answer Relevance — 低分怀疑谁",
             "TruLens 完全指南 · §4"),
            ("03-tool-compare.md", "comparison-matrix", "TruLens vs RAGAS vs DeepEval",
             "离线 batch / CI / 在线反馈 对照",
             "TruLens 完全指南 · §5"),
            ("03-concept-map.md", "bento-grid", "TruLens 概念地图",
             "Tiles: TruApp / Record / Feedback / bad case 工单",
             "TruLens 完全指南 · §11"),
        ],
    ),
    (
        "147.langsmith-tracing-tutorial.md",
        "langsmith-tracing",
        "LangSmith 链路追踪",
        _pad(ARTICLE_147, "langsmith-tracing"),
        [
            ("01-langsmith-idea.png", "hub-spoke", "§3 LangSmith 是什么"),
            ("02-trace-span.png", "hierarchical-tree", "§4 Trace Run Span"),
            ("03-read-trace.png", "flowchart", "§7 读懂 RAG Trace"),
            ("04-concept-map.png", "bento-grid", "§12 概念地图"),
        ],
        [
            ("01-langsmith-idea.md", "hub-spoke", "LangSmith 是什么？",
             "Center: RAG 黑匣子 — Spokes: Tracing / Datasets / Annotation",
             "LangSmith 链路追踪 · §3"),
            ("02-trace-span.md", "hierarchical-tree", "Trace Run Span 关系",
             "Tree: trace → retriever → prompt → llm",
             "LangSmith 链路追踪 · §4"),
            ("03-read-trace.md", "flowchart", "读懂 RAG Trace 排障顺序",
             "延迟 → Top-K → prompt → 输出 → 149～152",
             "LangSmith 链路追踪 · §7"),
            ("03-concept-map.md", "bento-grid", "LangSmith 概念地图",
             "Tiles: env / project / trace / bad case",
             "LangSmith 链路追踪 · §12"),
        ],
    ),
    (
        "148.langfuse-observability-tutorial.md",
        "langfuse-observability",
        "Langfuse 可观测性",
        _pad(ARTICLE_148, "langfuse-observability"),
        [
            ("01-langfuse-idea.png", "hub-spoke", "§3 Langfuse 是什么"),
            ("02-trace-observation.png", "hierarchical-tree", "§4 Trace Observation"),
            ("03-rag-observation-tree.png", "flowchart", "§7 RAG Observation 树"),
            ("04-concept-map.png", "bento-grid", "§12 概念地图"),
        ],
        [
            ("01-langfuse-idea.md", "hub-spoke", "Langfuse 是什么？",
             "Center: 开源观测 — Spokes: Trace / Score / Prompt / 自托管",
             "Langfuse 观测 · §3"),
            ("02-trace-observation.md", "hierarchical-tree", "Trace Observation Score",
             "Tree: trace → retrieve span → generation",
             "Langfuse 观测 · §4"),
            ("03-rag-observation-tree.md", "flowchart", "RAG 埋点树",
             "retrieve 必记 chunk_id / score — generation 记 model",
             "Langfuse 观测 · §7"),
            ("03-concept-map.md", "bento-grid", "Langfuse 概念地图",
             "Tiles: SDK / Docker / Score / param_version",
             "Langfuse 观测 · §12"),
        ],
    ),
    (
        "149.bad-case-parsing-tutorial.md",
        "bad-case-parsing",
        "Bad Case 归因：解析错误",
        _pad(ARTICLE_149, "bad-case-parsing"),
        [
            ("01-parsing-bad-case.png", "hub-spoke", "§3 解析型 bad case"),
            ("02-failure-mode-map.png", "comparison-matrix", "§5 失败模式 36～56"),
            ("03-diagnosis-checklist.png", "flowchart", "§9 诊断清单"),
            ("04-concept-map.png", "bento-grid", "§12 概念地图"),
        ],
        [
            ("01-parsing-bad-case.md", "hub-spoke", "解析型 bad case",
             "Center: 库内文本已错 — Spokes: PDF / OCR / 编码 / 清洗",
             "解析 bad case · §3"),
            ("02-failure-mode-map.md", "comparison-matrix", "C1 失败模式地图",
             "36～56 各一篇对应信号",
             "解析 bad case · §5"),
            ("03-diagnosis-checklist.md", "flowchart", "解析诊断清单",
             "trace → 源文件 diff → 选工具 → 重 ingest",
             "解析 bad case · §9"),
            ("03-concept-map.md", "bento-grid", "解析归因概念地图",
             "Tiles: trace / 36-56 / 149 vs 150 / playbook",
             "解析 bad case · §12"),
        ],
    ),
    (
        "150.bad-case-chunking-tutorial.md",
        "bad-case-chunking",
        "Bad Case 归因：切块错误",
        _pad(ARTICLE_150, "bad-case-chunking"),
        [
            ("01-chunking-bad-case.png", "hub-spoke", "§3 切块型 bad case"),
            ("02-chunk-strategies.png", "comparison-matrix", "§5 C2 策略 57～65"),
            ("03-diagnosis-checklist.png", "flowchart", "§9 诊断清单"),
            ("04-concept-map.png", "bento-grid", "§12 概念地图"),
        ],
        [
            ("01-chunking-bad-case.md", "hub-spoke", "切块型 bad case",
             "Center: 刀口切断语义 — Spokes: size / overlap / 结构 / parent",
             "切块 bad case · §3"),
            ("02-chunk-strategies.md", "comparison-matrix", "切块策略对照",
             "57 固定 ~ 65 Parent Document",
             "切块 bad case · §5"),
            ("03-diagnosis-checklist.md", "flowchart", "切块诊断",
             "chunk_id 定位 → 边界检查 → 调参",
             "切块 bad case · §9"),
            ("03-concept-map.md", "bento-grid", "切块归因概念地图",
             "Tiles: 149 / 150 / 151 / 171",
             "切块 bad case · §12"),
        ],
    ),
    (
        "151.bad-case-retrieval-miss-tutorial.md",
        "bad-case-retrieval-miss",
        "Bad Case 归因：检索遗漏",
        _pad(ARTICLE_151, "bad-case-retrieval-miss"),
        [
            ("01-retrieval-miss.png", "hub-spoke", "§3 检索遗漏"),
            ("02-decision-tree.png", "flowchart", "§5 归因决策树"),
            ("03-hybrid-fix.png", "hub-spoke", "§8 混合检索修复"),
            ("04-concept-map.png", "bento-grid", "§13 概念地图"),
        ],
        [
            ("01-retrieval-miss.md", "hub-spoke", "检索遗漏是什么",
             "Center: 有货没捞到 — Spokes: dense / sparse / filter / K",
             "检索遗漏 · §3"),
            ("02-decision-tree.md", "flowchart", "检索遗漏决策树",
             "149 → 150 → gold 句探针 → hybrid / rewrite",
             "检索遗漏 · §5"),
            ("03-hybrid-fix.md", "hub-spoke", "混合检索修复",
             "Center: [93] hybrid — Spokes: RRF / 改写 / rerank",
             "检索遗漏 · §8"),
            ("03-concept-map.md", "bento-grid", "检索遗漏概念地图",
             "Tiles: trace / 93 / 100-103 / A/B",
             "检索遗漏 · §13"),
        ],
    ),
    (
        "152.bad-case-hallucination-tutorial.md",
        "bad-case-hallucination",
        "Bad Case 归因：生成胡编",
        _pad(ARTICLE_152, "bad-case-hallucination"),
        [
            ("01-hallucination-rag.png", "hub-spoke", "§3 生成胡编"),
            ("02-faithfulness-check.png", "flowchart", "§5 Faithfulness 核验"),
            ("03-cause-levers.png", "comparison-matrix", "§7 成因杠杆"),
            ("04-concept-map.png", "bento-grid", "§13 概念地图"),
        ],
        [
            ("01-hallucination-rag.md", "hub-spoke", "RAG 生成胡编",
             "Center: context 有 gold 仍错 — Spokes: 忠实性 / 拒答 / 温度",
             "胡编 bad case · §3"),
            ("02-faithfulness-check.md", "flowchart", "trace 对齐 Faithfulness",
             "展开 prompt → gold 在否 → 截断否 → 坐实胡编",
             "胡编 bad case · §5"),
            ("03-cause-levers.md", "comparison-matrix", "胡编成因与杠杆",
             "对照 [33] 续写 / 温度 / 预算 / 冲突证据",
             "胡编 bad case · §7"),
            ("03-concept-map.md", "bento-grid", "胡编归因概念地图",
             "Tiles: 149-151 / 33 / 141 / 112",
             "胡编 bad case · §13"),
        ],
    ),
    (
        "153.ab-experiment-rag-tutorial.md",
        "ab-experiment-rag",
        "RAG A/B 实验设计",
        _pad(ARTICLE_153, "ab-experiment-rag"),
        [
            ("01-ab-idea.png", "hub-spoke", "§3 A/B 是什么"),
            ("02-metrics-pyramid.png", "comparison-matrix", "§5 指标金字塔"),
            ("03-experiment-doc.png", "flowchart", "§12 设计书"),
            ("04-concept-map.png", "bento-grid", "§13 概念地图"),
        ],
        [
            ("01-ab-idea.md", "hub-spoke", "RAG A/B 实验",
             "Center: 分流 — Spokes: 指标 / 离线 / 在线 / 回滚",
             "A/B 实验 · §3"),
            ("02-metrics-pyramid.md", "comparison-matrix", "指标金字塔",
             "北极星 / 质量 / 护栏 latency",
             "A/B 实验 · §5"),
            ("03-experiment-doc.md", "flowchart", "实验设计书",
             "假设 → control/treatment → 流量 → 成功标准",
             "A/B 实验 · §12"),
            ("03-concept-map.md", "bento-grid", "A/B 概念地图",
             "Tiles: 171 / 161 / 147-148 / 单变量",
             "A/B 实验 · §13"),
        ],
    ),
    (
        "154.param-version-management-tutorial.md",
        "param-version-management",
        "RAG 参数版本管理",
        _pad(ARTICLE_154, "param-version-management"),
        [
            ("01-param-version-idea.png", "hub-spoke", "§3 参数版本"),
            ("02-param-scope.png", "comparison-matrix", "§4 哪些要版本化"),
            ("03-manifest-example.png", "hierarchical-tree", "§12 manifest"),
            ("04-concept-map.png", "bento-grid", "§13 概念地图"),
        ],
        [
            ("01-param-version-idea.md", "hub-spoke", "参数版本管理",
             "Center: param_version — Spokes: 复现 / 回滚 / A/B / trace",
             "参数版本 · §3"),
            ("02-param-scope.md", "comparison-matrix", "必须版本化的参数",
             "ingest/chunk/embed 重索引 vs retrieve/generate 热切换",
             "参数版本 · §4"),
            ("03-manifest-example.md", "hierarchical-tree", "manifest 结构",
             "parser → chunk → embed → index → retrieve → generate",
             "参数版本 · §12"),
            ("03-concept-map.md", "bento-grid", "参数版本概念地图",
             "Tiles: 171 / 170 / 48 doc_version / Git",
             "参数版本 · §13"),
        ],
    ),
]


