# -*- coding: utf-8 -*-
"""Article body extensions for batch 137-145."""
from _batch_137_145_common import COMMON_RAG_LINKS, _faq, _mistakes

BODIES = {}

BODIES["138.config-driven-pipeline-tutorial.md"] = f"""# D 框架与架构（十一）：配置驱动管道组装完全指南

> 硬编码 `new ChromaStore()` 在 Demo 很快；团队有三人以上改 RAG，就会出现「我本地能跑、你那边检索 k 不同」的扯皮。**配置驱动管道**（Config-driven Pipeline）把 [137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md) 的 **实现类名与参数** 写进 YAML/JSON，由 **工厂函数** 在启动时组装——换后端改配置，不改 `main.py`。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 轨地基篇**（路线图第 **155** 条）。前置：[137 可插拔下游](137.pluggable-store-retriever-generator-tutorial.md)、[135 框架取舍](135.pipeline-vs-framework-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)。

---

## 目录

1. [前言：改一行代码发版还是改配置？](#1-前言改一行代码发版还是改配置)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [配置驱动是什么](#3-配置驱动是什么)
4. [配置文件结构：分层与版本](#4-配置文件结构分层与版本)
5. [工厂模式：从字符串到对象](#5-工厂模式从字符串到对象)
6. [环境覆盖与密钥注入](#6-环境覆盖与密钥注入)
7. [与检索链参数：k、混合、预算](#7-与检索链参数k混合预算)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：pipeline.yaml 驱动 Mini-RAG](#9-综合实战pipelineyaml-驱动-mini-rag)
10. [校验、测试与发布](#10-校验测试与发布)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：改一行代码发版还是改配置？

典型对话：

- 算法：「把 `k` 从 5 改 8。」  
- 后端：「那我走发版？」  
- 运维：「周五封网。」

若 `k` 写在 Python 里，**小实验也要发版**；若写在 `pipeline.yaml` 且带 `version: rag-pipeline-2026-04-01`，改配置 **走变更单 + 回归** [144](144.regression-test-set-tutorial.md)，不必动二进制。

**配置驱动**不是「不用写代码」——接口实现仍要代码；变的是 **组装关系** 与 **超参** 外置。

**读完本文，你应该能做到：**

1. 设计 **分层 YAML**（store / retriever / generator / pipeline）。  
2. 写 **registry + factory** 按类名构造对象。  
3. 用环境变量覆盖敏感项。  
4. 跑通 §9 读配置启动 Mini-RAG。  
5. 对照 §8 避免 **配置与代码双源真相**。

### 1.1 路线图位置

```text
154 可插拔接口 [137]
155 配置驱动 ← 本篇
156+ RAGAS / 金标
```

---

## 2. 本文边界与动手路径

**档位：D 轨地基篇（155）。**

| 步骤 | 验收 |
|------|------|
| A | 画出 YAML 四层 |
| B | registry 注册两类 Store |
| C | env 覆盖 API Key |
| D | §9 端到端 |
| E | schema 校验失败阻断 |

### 2.2 沿用前文

{COMMON_RAG_LINKS}

---

## 3. 配置驱动是什么

读下图：启动时读配置 → 工厂 → 可运行 Pipeline。

![配置驱动流程](image/config-driven-pipeline/01-config-flow.png)

**配置驱动管道**：将组件 **类路径、构造参数、运行时超参** 从源码分离到可版本化的配置文件。  
通俗说：**乐高说明书在外面的纸盒上**，换造型只换说明书，不换积木模具（接口实现）。

---

## 4. 配置文件结构：分层与版本

推荐 `config/pipeline.yaml`：

```yaml
version: "rag-pipeline-1.2.0"
pipeline:
  retriever_k: 8
  max_context_tokens: 6000  # 对齐 [28 窗口](28.context-window-tutorial.md)

store:
  class: myrag.stores.ChromaVectorStore
  args:
    path: "./chroma_db"
    collection: "handbook_v3"

retriever:
  class: myrag.retrievers.DenseRetriever
  args:
    embedder_class: myrag.embedders.HashEmbedder

generator:
  class: myrag.generators.OpenAICompatibleGenerator
  args:
    model: deepseek-chat
    temperature: 0.1
```

| 字段 | 作用 |
|------|------|
| version | 与 [154 参数版本](154.param-version-management-tutorial.md) 对齐 |
| pipeline.* | 编排层超参 |
| store/retriever/generator | 注入 [137](137.pluggable-store-retriever-generator-tutorial.md) |

---

## 5. 工厂模式：从字符串到对象

**演示目标**：`importlib` 动态加载类并递归构造依赖。  
**环境**：Python 3.10+，`pyyaml`。  
**预期**：打印出 `RagPipeline` 实例类型。

```python
import importlib
import yaml

REGISTRY = {{}}  # 可选：短名 -> 类

def load_class(path: str):
    mod, name = path.rsplit(".", 1)
    return getattr(importlib.import_module(mod), name)

def build_from_config(cfg: dict):
    store = load_class(cfg["store"]["class"])(**cfg["store"].get("args", {{}}))
    embedder_cls = load_class(cfg["retriever"]["args"]["embedder_class"])
    embedder = embedder_cls()
    retriever = load_class(cfg["retriever"]["class"])(store=store, embedder=embedder)
    generator = load_class(cfg["generator"]["class"])(**cfg["generator"].get("args", {{}}))
    return RagPipeline(retriever, generator), cfg["pipeline"]
```

**解读**：`retriever` 依赖 `store` 由工厂 **按序构造**，业务 `main` 不出现具体类名。

---

## 6. 环境覆盖与密钥注入

**先错**：`api_key: sk-xxx` 写进 Git。  
**对**：`OPENAI_API_KEY` 环境变量；YAML 写 `api_key: ${{ENV:OPENAI_API_KEY}}` 或 pydantic-settings。

| 项 | 配置 | 密钥 |
|----|------|------|
| model 名 | YAML | 否 |
| base_url | YAML | 否 |
| api_key | 环境/Secret | 是 |

---

## 7. 与检索链参数：k、混合、预算

配置应能表达 [93 混合](93.hybrid-search-tutorial.md) 而不改代码：

```yaml
retriever:
  class: myrag.retrievers.HybridRetriever
  args:
    dense_k: 20
    sparse_k: 20
    fusion: rrf  # [94 RRF](94.rrf-fusion-tutorial.md)
    rerank_top: 5  # [96 BGE](96.bge-reranker-tutorial.md)
```

`max_context_tokens` 与 [107 预算](107.context-budget-tutorial.md) 联动：超预算时 **截断 chunk 列表** 而非静默截断单 chunk 中间。

---

## 8. 先错对对：四种典型翻车

{_mistakes([
    ("配置与代码各写一套默认值", "YAML 写 k=8，代码里写 k=5，线上行为随机。", "单一真相：仅配置有默认，代码读不到就报错。"),
    ("class 任意字符串无白名单", "YAML 被注入恶意模块路径。", "registry 白名单或包前缀限制。"),
    ("改配置不做回归", "Recall 掉 0.2 未发现。", "绑定 [144 回归集](144.regression-test-set-tutorial.md) CI。"),
    ("版本号装饰", "version 字段从不更新，审计失效。", "每次变更 bump version + changelog。"),
])}

---

## 9. 综合实战：pipeline.yaml 驱动 Mini-RAG

**阅读顺序**：§4～§7。

```python
def main(config_path: str = "config/pipeline.yaml"):
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    pipeline, pcfg = build_from_config(cfg)
    result = pipeline.ask("年假有多少天？", k=pcfg["retriever_k"])
    print(result)

if __name__ == "__main__":
    main()
```

验收：换 `retriever.class` 为 `HybridRetriever` 实现，**main 不变**；跑 [143 金标](143.golden-dataset-tutorial.md) 十条对比分数。

---

## 10. 校验、测试与发布

用 **Pydantic** 校验：

```python
from pydantic import BaseModel, Field

class PipelineConfig(BaseModel):
    version: str
    pipeline: dict
    store: dict
    retriever: dict
    generator: dict
```

CI：`validate_config("config/pipeline.yaml")` + 回归评测。发布清单：`config_hash`、`kb_version`、`prompt_version` 三件套写 trace。

---

## 11. 综合概念地图

![配置驱动概念地图](image/config-driven-pipeline/03-concept-map.png)

137 接口 → 本篇配置 → 138+ 评测与观测 [147](147.langsmith-tracing-tutorial.md)。

---

## 12. 常见陷阱与 FAQ

{_faq([
    ("YAML 还是 JSON？", "YAML 人读友好；JSON 机器严格。团队统一即可，Pydantic 都吃。"),
    ("多环境 dev/staging/prod？", "三份文件或 overlay：`pipeline.yaml` + `pipeline.prod.yaml` merge。"),
    ("和 12-Factor 关系？", "配置进环境；代码进镜像；一致于 [155 本篇] 与运维实践。"),
    ("LangChain 能配置化吗？", "LC 有 YAML chain；自研域仍建议 [137] 接口 + 本篇工厂。"),
    ("配置热更新？", "监听文件变更 reload 工厂；注意 in-flight 请求与连接池重建。"),
])}

---

## 13. 总结与系列下一步

配置驱动让 **实验与发版解耦**，是 E 轨 **可重复评测** 的前提：没有固定 `pipeline_version`，RAGAS 分数无法归因。

**下一步：** [139 Context Precision](139.ragas-context-precision-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[154 参数版本](154.param-version-management-tutorial.md)。

---

*系列：D 框架与架构 · 路线图第 155 条 · 地基篇*
"""

BODIES["139.ragas-context-precision-tutorial.md"] = f"""# E 评测与观测（一）：RAGAS Context Precision 完全指南

> 检索召回了五条 chunk，三条相关、两条凑数——模型还可能被废话带偏。**Context Precision**（上下文精确率）量的是：**排在前面的是不是真有用**。这篇开启 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨 RAGAS 系列**（路线图第 **156** 条），与 [140 Recall](140.ragas-context-recall-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 组成三角。前置：[93–98 检索链](93.hybrid-search-tutorial.md)、[143 金标集](143.golden-dataset-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)。

---

## 目录

1. [前言：召回了不等于召对了](#1-前言召回了不等于召对了)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Context Precision 是什么](#3-context-precision-是什么)
4. [公式直觉与排序敏感](#4-公式直觉与排序敏感)
5. [金标：哪些 chunk 算相关](#5-金标哪些-chunk-算相关)
6. [用 RAGAS 跑分](#6-用-ragas-跑分)
7. [与 Top-k、重排、预算的关系](#7-与-top-k重排预算的关系)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：评测脚本与看板](#9-综合实战评测脚本与看板)
10. [与 Context Recall 分工](#10-与-context-recall-分工)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：召回了不等于召对了

[98 Top-k](98.top-k-retrieval-tutorial.md) 调到 20 后，Recall 好看，但 **前 3 条里混进无关 FAQ**——[107 预算](107.context-budget-tutorial.md) 把三条都塞进 [28 窗口](28.context-window-tutorial.md)，模型浪费注意力在无关段上。

**Context Precision**（上下文精确率）：衡量 **检索结果列表中，相关文档是否排在靠前**，且 **无关项是否少**。  
通俗说：**考试成绩单里，错题是否都排在后面**——靠前的应是加分项。

**读完本文，你应该能做到：**

1. 口述 Precision 与 Recall 差异。  
2. 准备含 `reference` chunk id 的金标行。  
3. 用 `ragas` 跑出 `context_precision`。  
4. 解释 **重排** 如何提升 Precision。  
5. 对照 §8 四种 **评测集与生产不一致** 翻车。

### 1.1 E 轨位置

```text
156 Context Precision ← 本篇
157 Context Recall [140]
158 Faithfulness [141] 主线
159 Answer Relevancy [142]
```

---

## 2. 本文边界与动手路径

**档位：E 轨地基篇（156）。**

| 步骤 | 验收 |
|------|------|
| A | 画 Precision vs Recall 表 |
| B | 标 10 条金标 relevant ids |
| C | `pip install ragas` 跑通 |
| D | 调 rerank 看 Precision↑ |

### 2.2 沿用前文

{COMMON_RAG_LINKS}

---

## 3. Context Precision 是什么

读下图：横轴是检索排名，绿=相关、红=无关，Precision 惩罚「前排红线」。

![Context Precision 直觉](image/ragas-context-precision/01-precision-idea.png)

**RAGAS**（Retrieval Augmented Generation Assessment）：开源 RAG 评测框架，用 **LLM 或规则** 对检索与生成打分。  
**Context Precision**：针对 **retrieved_contexts** 与 **reference**（或 LLM 判相关）计算 **排序加权精确率**。

---

## 4. 公式直觉与排序敏感

简化直觉（非严格公式）：

| 排名 | 是否相关 | 对 Precision 影响 |
|------|----------|-------------------|
| 1 | 相关 | 强正 |
| 2 | 无关 | 强负（占前排） |
| 3 | 相关 | 部分挽回 |

因此 **[96 重排](96.bge-reranker-tutorial.md)** 常 **升 Precision 不明显升 Recall**——把相关块从第 8 拉到第 2。

与 [105 MMR](105.mmr-diversity-tutorial.md)：MMR 降冗余，也可能 **升 Precision**（少重复无关）。

---

## 5. 金标：哪些 chunk 算相关

见 [143 Golden Dataset](143.golden-dataset-tutorial.md)。每条样本：

```json
{{
  "question": "年假几天？",
  "ground_truth": "工作满一年享10天年假。",
  "relevant_chunk_ids": ["hb-sec3-p2", "hb-sec3-p3"]
}}
```

标注原则：**能独立支撑 ground_truth 的 chunk 算相关**；仅提到「假期」但无天数的 **不算**。

---

## 6. 用 RAGAS 跑分

**演示目标**：对已有 `question / contexts / ground_truth` 计算 context_precision。  
**环境**：`pip install ragas datasets`；需 **裁判 LLM API**（与 RAGAS 文档一致）。  
**预期**：输出 0～1 分数。

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_precision

rows = [{{
    "question": "年假几天？",
    "ground_truth": "10天",
    "contexts": [
        "第三章：工作满一年者年假10天。",
        "食堂开放时间：11:30-13:00。",
    ],
}}]
ds = Dataset.from_list(rows)
result = evaluate(ds, metrics=[context_precision])
print(result)
```

**解读**：第二条无关且靠前会 **拉低** Precision；应用 [96 重排](96.bge-reranker-tutorial.md) 或提高无关项惩罚。

---

## 7. 与 Top-k、重排、预算的关系

| 杠杆 | Precision | Recall |
|------|-----------|--------|
| 增大 k | 可能降 | 可能升 |
| Rerank | 常升 | 中性 |
| 混合检索 [93] | 视噪声 | 常升 |
| 预算截断 [107] | 截掉尾部噪声 | 可能降 |

调参顺序：**先保证 Recall [140]**，再 **重排提 Precision**，最后 **预算裁尾**。

---

## 8. 先错对对：四种典型翻车

{_mistakes([
    ("用生产日志无金标 relevant", "RAGAS 自动判相关漂移。", "核心集人工标 relevant_chunk_ids。"),
    ("评测 ANN 结果但生产用 rerank 后", "分数与线上脱节。", "评测 **进 prompt 前** 的 contexts。"),
    ("把重复 chunk 当多条相关", "Precision 虚高。", "先去重 [106](106.retrieval-dedup-tutorial.md)。"),
    ("只看平均分不看最差 10 条", "均值 0.85 但客服场景全挂。", "分场景 + 最差个案复盘。"),
])}

---

## 9. 综合实战：评测脚本与看板

```python
def eval_precision(dataset_path: str, pipeline) -> dict:
  rows = load_jsonl(dataset_path)
  scored = []
  for row in rows:
    chunks = pipeline.retriever.retrieve(row["question"], k=8)
    contexts = [c.text for c in chunks]
    score = run_ragas_precision(row["question"], contexts, row["ground_truth"])
    scored.append({{"id": row["id"], "context_precision": score}})
  return {{"mean": mean(s["context_precision"] for s in scored), "details": scored}}
```

看板：`precision_p50`、按 `doc_type` 分组、与 `k` 联动曲线。

---

## 10. 与 Context Recall 分工

| 指标 | 问的问题 |
|------|----------|
| Precision | 前排干净吗？ |
| Recall [140] | 该来的来了吗？ |

两者都低：先查 **索引/切块**；Recall 高 Precision 低：上 **重排与去重**。

---

## 11. 综合概念地图

![RAGAS Precision 概念地图](image/ragas-context-precision/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

{_faq([
    ("Precision 多少算合格？", "视场景；对内 Bot 建议 baseline 后追求 +0.05 delta，勿抄论文绝对值。"),
    ("无 API 能跑吗？", "部分指标可用本地模型；以 RAGAS 文档为准，PoC 可用小样本人工判。"),
    ("与 NDCG 关系？", "同属排序质量；RAGAS 与 RAG 金标字段更贴。"),
    ("多跳检索怎么标？", "见 [104](104.multi-hop-retrieval-tutorial.md)；相关集用并集。"),
    ("Precision 高但答案仍错？", "看 [141 Faithfulness](141.ragas-faithfulness-tutorial.md)——检索对但生成胡编。"),
])}

---

## 13. 总结与系列下一步

Context Precision 管 **前排干净**；下一篇 [140 Recall](140.ragas-context-recall-tutorial.md) 管 **该来没来**；[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 管 **生成是否胡说**。

---

*系列：E 评测与观测 · 路线图第 156 条 · 地基篇*
"""

BODIES["140.ragas-context-recall-tutorial.md"] = f"""# E 评测与观测（二）：RAGAS Context Recall 完全指南

> [139 Precision](139.ragas-context-precision-tutorial.md) 问「前排干净吗」；**Context Recall**（上下文召回率）问：**该来的证据来了吗？** 检索漏了，后面 [110 Prompt](110.rag-prompt-template-tutorial.md) 写得再好也只能 [112 拒答](112.refusal-strategy-tutorial.md) 或 [33 幻觉](33.llm-hallucination-tutorial.md)。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 轨地基篇**（路线图第 **157** 条）。前置：[139 Precision](139.ragas-context-precision-tutorial.md)、[91–94 检索](91.dense-retrieval-tutorial.md)、[143 金标](143.golden-dataset-tutorial.md)。

---

## 目录

1. [前言：漏检比噪声更致命](#1-前言漏检比噪声更致命)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Context Recall 是什么](#3-context-recall-是什么)
4. [公式直觉与分母分子](#4-公式直觉与分母分子)
5. [金标 relevant 集合怎么标](#5-金标-relevant-集合怎么标)
6. [RAGAS 实战跑分](#6-ragas-实战跑分)
7. [Recall 低时的排查树](#7-recall-低时的排查树)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：对比 k 与混合检索](#9-综合实战对比-k-与混合检索)
10. [与 Precision、Faithfulness 联动](#10-与-precisionfaithfulness-联动)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：漏检比噪声更致命

用户问「试用期多久」，金标 chunk 在 `hr-policy-sec2`，ANN 只回了食堂菜单——Precision 可能还行（前排都「像人事」），**Recall 为 0**：关键证据根本没进 [28 窗口](28.context-window-tutorial.md)。

**Context Recall**：检索到的上下文中，**覆盖了多少 ground truth 所需的相关 chunk**。  
通俗说：**开卷考试，该带的那页书有没有带进考场**。

**读完本文，你应该能做到：**

1. 区分 Recall 与 Precision。  
2. 标 `relevant_chunk_ids` 并跑 RAGAS `context_recall`。  
3. 按 §7 排查树定位 **切块/索引/查询** 问题。  
4. 用 §9 对比 **调 k vs 上混合 [93]** 的 Recall delta。

---

## 2. 本文边界与动手路径

**档位：E 轨地基篇（157）。**

| 步骤 | 验收 |
|------|------|
| A | 口述 Recall 分子分母 |
| B | 10 条金标 |
| C | ragas evaluate |
| D | k=5→20 Recall 曲线 |

### 2.2 沿用前文

{COMMON_RAG_LINKS}

---

## 3. Context Recall 是什么

![Context Recall 直觉](image/ragas-context-recall/01-recall-idea.png)

读上图：金标需要 A、B 两块，检索只带回 A → Recall 约 50%。

---

## 4. 公式直觉与分母分子

| 符号 | 含义 |
|------|------|
| 分母 | 金标 relevant chunk 集合大小 |
| 分子 | 被 retrieved_contexts **覆盖** 的相关条数 |

**多证据题**：问「年假与病假累计规则」，可能需 2～3 chunk 才完整——Recall 要 **集合覆盖**，不是单条命中。

---

## 5. 金标 relevant 集合怎么标

与 [143](143.golden-dataset-tutorial.md) 字段一致：

```json
{{
  "id": "hr-001",
  "question": "试用期最长多久？",
  "ground_truth": "劳动合同期限三个月以上不满一年的，试用期不得超过一个月。",
  "relevant_chunk_ids": ["labor-sec19-para1"]
}}
```

标注会：法务确认 **最小充分证据集**；避免把整章 PDF 标成 relevant（Recall 虚高无判别力）。

---

## 6. RAGAS 实战跑分

**演示**：`context_recall` 指标。  
**环境**：`pip install ragas datasets`。  
**预期**：0～1。

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_recall

rows = [{{
    "question": "试用期最长多久？",
    "ground_truth": "试用期不得超过一个月（特定合同期限下）。",
    "contexts": ["劳动合同期限三个月以上不满一年的，试用期不得超过一个月。"],
    "reference": "劳动合同期限三个月以上不满一年的，试用期不得超过一个月。",
}}]
ds = Dataset.from_list(rows)
print(evaluate(ds, metrics=[context_recall]))
```

---

## 7. Recall 低时的排查树

```text
Recall 低
├─ 金标标错？ → 重标 [143]
├─ 切块切断？ → [57-64 切块](57.fixed-size-chunking-tutorial.md)
├─ 向量模型域外？ → [71 域评测](71.domain-embedding-evaluation-tutorial.md)
├─ k 太小？ → [98 Top-k](98.top-k-retrieval-tutorial.md)
├─ 缺 BM25？ → [93 Hybrid](93.hybrid-search-tutorial.md)
├─ filter 过严？ → [88 元数据过滤](88.metadata-filter-retrieval-tutorial.md)
└─ ACL 误杀？ → [121 越权过滤](121.unauthorized-doc-filter-tutorial.md)
```

---

## 8. 先错对对：四种典型翻车

{_mistakes([
    ("只测 Recall 不看 Precision", "k=100 Recall 满分，前排全噪声。", "Recall 达标后再压 k + rerank。"),
    ("用摘要 chunk 标 relevant 却搜原文", "id 对不上永远 Recall 0。", "索引与金标同一 chunk 规范 [51](51.metadata-chunk-id-tutorial.md)。"),
    ("评测集只有简单 FAQ", "多跳题上线即崩。", "加入 [104 多跳](104.multi-hop-retrieval-tutorial.md) 样例。"),
    ("换 Embedding 不重建索引", "Recall 断崖。", "新 collection [76 Chroma](76.chroma-vector-db-tutorial.md)。"),
])}

---

## 9. 综合实战：对比 k 与混合检索

对 [137 Pipeline](137.pluggable-store-retriever-generator-tutorial.md) 跑网格：

| 配置 | Recall@8 | Precision@8 |
|------|----------|---------------|
| dense k=5 | 0.62 | 0.71 |
| dense k=20 | 0.78 | 0.55 |
| hybrid+rrf k=20→rerank5 | 0.81 | 0.83 |

记录进 wiki，绑定 `pipeline_version`。

---

## 10. 与 Precision、Faithfulness 联动

| 现象 | 优先查 |
|------|--------|
| Recall↓ Precision↑ | k 太小 |
| Recall↓ Precision↓ | 索引/切块 |
| Recall↑ Faithfulness↓ | [141 生成胡编](141.ragas-faithfulness-tutorial.md) |

---

## 11. 综合概念地图

![Recall 概念地图](image/ragas-context-recall/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

{_faq([
    ("Recall 1.0 够吗？", "不够；还要看 Precision 与 Faithfulness。"),
    ("生成式评测能否代替金标？", "可作补充；核心集仍要人标 relevant id。"),
    ("多 chunk 部分命中怎么算？", "RAGAS 用覆盖比例；自定义可设阈值。"),
    ("与 Hit Rate 区别？", "Hit Rate 常指至少一条相关；Recall 看覆盖比例。"),
    ("增量索引后 Recall 掉？", "查 [49 增量](49.incremental-update-tutorial.md) 漏同步。"),
])}

---

## 13. 总结与系列下一步

Recall 保 **证据到场**；下一篇 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 保 **到场后不乱说**。

---

*系列：E 评测与观测 · 路线图第 157 条 · 地基篇*
"""


def get_body(key: str) -> str:
    return BODIES[key]
