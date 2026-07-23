# -*- coding: utf-8 -*-
"""Generate tutorials 137-145 (roadmap 154-162) with >=5000 hanzi each."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent

PROMPT_TEMPLATE = """---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

{body}

Footer: {footer}

All text Simplified Chinese.
"""


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def section_count(text: str) -> int:
    return len(re.findall(r"^## ", text, re.MULTILINE))


def write_image_assets(slug: str, title: str, items: list[tuple[str, str, str]], prompts: list[tuple[str, str, str, str, str]]):
    img_dir = ROOT / "image" / slug
    prompts_dir = img_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}信息图\n\n", "| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"]
    for fname, layout, section in items:
        lines.append(f"| `{fname}` | {layout} | {section} |\n")
    lines += [
        "\n风格：hand-drawn-edu · 16:9 · 中文\n\nPrompt 见 `prompts/`。\n\n",
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
    ]
    (img_dir / "README.md").write_text("".join(lines), encoding="utf-8")
    for fname, layout, ptitle, body, footer in prompts:
        (prompts_dir / fname).write_text(
            PROMPT_TEMPLATE.format(layout=layout, title=ptitle, body=body, footer=footer),
            encoding="utf-8",
        )


from _batch_137_145_common import COMMON_RAG_LINKS, _faq, _mistakes


from _articles_137_145_expand import EXPAND
from _articles_137_145_expand3 import EXPAND3
from _articles_137_145_expand4 import EXPAND4
from _articles_137_145_expand5 import EXPAND5
from _articles_137_145_expand6 import EXPAND6
from _articles_137_145_expand7 import EXPAND7
from _articles_137_145_expand8 import EXPAND8


def pad_article(content: str, slug: str, min_h: int = 5000) -> str:
    pads = PAD_BLOCKS.get(slug, []) + EXPAND.get(slug, [])
    if slug in EXPAND3:
        pads.append(EXPAND3[slug])
    if slug in EXPAND4:
        pads.append(EXPAND4[slug])
    if slug in EXPAND5:
        pads.append(EXPAND5[slug])
    if slug in EXPAND6:
        pads.append(EXPAND6[slug])
    if slug in EXPAND7:
        pads.append(EXPAND7[slug])
    if slug in EXPAND8:
        pads.append(EXPAND8[slug])
    out = content
    for pad in pads:
        out += "\n\n" + pad
    if hanzi_count(out) < min_h:
        raise ValueError(f"{slug}: only {hanzi_count(out)} hanzi, need {min_h}")
    return out


PAD_BLOCKS: dict[str, list[str]] = {
    "pluggable-store-retriever-generator": [
        """### 14.6 与 LangChain 封装的边界

[127 Retriever](127.langchain-retriever-tutorial.md) 的 `as_retriever()` 是 **框架适配器**，不是业务接口。自研 `Retriever` 协议应 **更窄**：只暴露 `search(query, filters) -> list[Chunk]`，LangChain 包装放在 `adapters/langchain.py`。这样换框架时 **核心域模型不动**。

### 14.7 多租户下的 Store 隔离

每个 `tenant_id` 对应 **独立 collection 或 namespace**（见 [89 多租户](89.multi-tenant-namespace-tutorial.md)）。`VectorStore` 构造时注入 `tenant_id`，禁止运行时从 query 字符串拼 collection 名——防注入。

### 14.8 Generator 温度与 Faithfulness

[29 采样](29.llm-sampling-tutorial.md)：`temperature=0` 利于 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 回归稳定；创意 Bot 可单独 `Generator` 配置。评测与生产 **参数表分开版本化**。

### 14.9 面试追问

**问**：为什么 Store 和 Retriever 分开？  
**答**：Store 管 CRUD 与持久化；Retriever 管召回策略（混合、过滤、重排）。同一 Store 可挂 HybridRetriever 与 DenseOnlyRetriever。

**问**：Mock 测试从哪层切？  
**答**：Retriever 与 Generator 用 Fake；Store 集成测用临时目录 Chroma。""",
    ],
    "config-driven-pipeline": [
        """### 14.6 配置 schema 演进

用 **JSON Schema** 或 **Pydantic Settings** 校验 `pipeline.yaml`：`retriever.k` 必须是正整数、`generator.model` 非空。CI 里 `validate_config()` 失败则阻断发布。

### 14.7 与 Docker/K8s 注入

生产用 **环境变量覆盖** YAML 默认值：`RAG__GENERATOR__MODEL=deepseek-chat`（双下划线嵌套）。敏感 Key 只走 Secret，不进 Git。

### 14.8 Feature Flag 与配置

灰度「新 Hybrid 配置」：`flags.use_hybrid_v2: true` 与 `pipeline_v2.yaml` 并存；[144 回归集](144.regression-test-set-tutorial.md) 对比后再切默认。

### 14.9 配置审计

每次发布存 **config_hash** 到 trace；[147 LangSmith](147.langsmith-tracing-tutorial.md) metadata 挂 `pipeline_version`，方便 bad case 回放。""",
    ],
    "ragas-context-precision": [
        """### 14.6 Precision 与业务「废话 chunk」

客服场景：检索到 **正确但冗长** 的整章制度，Precision@k 可能仍高（条目相关），但 [107 预算](107.context-budget-tutorial.md) 爆掉、生成质量降。要同时看 **chunk 长度分布** 与 **MMR** [105](105.mmr-diversity-tutorial.md)。

### 14.7 子问题 Precision

[103 Query 分解](103.query-decomposition-tutorial.md) 后 **每个子 query 单独算 Precision**，再 macro 平均——避免「主问题对了、子问题全偏」被掩盖。

### 14.8 人工标注成本

金标 `relevant_chunk_ids` 十条即可起步；扩到五十条再调 [98 k](98.top-k-retrieval-tutorial.md)。标注指南写清：**相关 = 能单独支撑答案的一句证据**。

### 14.9 与 Rerank 的关系

精排后顺序变，RAGAS Context Precision 用 **最终进 prompt 的 contexts** 算，不是 ANN 原始 Top-k。""",
    ],
    "ragas-context-recall": [
        """### 14.6 Recall 低时的杠杆顺序

1. 查 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 是否过严；  
2. 升 [98 k](98.top-k-retrieval-tutorial.md) 或加 [93 混合](93.hybrid-search-tutorial.md)；  
3. 查切块 [57-64](57.fixed-size-chunking-tutorial.md) 是否切断证据；  
4. 查 [100 改写](100.query-rewriting-tutorial.md)。

### 14.7 多跳 Recall

[104 多跳检索](104.multi-hop-retrieval-tutorial.md)：金标 `relevant_ids` 可能跨两跳才齐——Recall 定义要写 **并集是否算命中**。

### 14.8 负样本库

故意加入 **应检索不到** 的 query，Recall 不适用，改用 **拒答率** [112](112.refusal-strategy-tutorial.md) 与 **空上下文 Precision**。

### 14.9 版本对比

索引 v3→v4：固定 [143 金标集](143.golden-dataset-tutorial.md)，只比 Recall delta，避免同时改 prompt 混淆归因。""",
    ],
    "ragas-faithfulness": [
        """### 15.6 Claim 粒度消融实验

对比 **句级 vs 子句级** claim 切分对 Faithfulness 分数的影响：句级快但易漏复合断言；子句级准但 LLM 调用翻倍。PoC 用句级，上线质检用子句级抽检 10%。

### 15.7 多语言 Faithfulness

资料中文、用户英文提问：claim 检测语言应 **与答案一致**；证据仍中文——NLL 或 cross-lingual entailment 要单独验证，不能照搬英文 benchmark 分数。

### 15.8 与引用 [113] 的联合指标

定义 **Citation-Faithfulness**：每个 [n] 标注的 chunk 是否支撑对应句。比纯 Faithfulness 更贴产品；实现可在 §9 解析器上加规则。

### 15.9 组织流程

| 角色 | 职责 |
|------|------|
| 算法 | 指标定义、评测脚本 |
| 标注 | 金标答案与证据 |
| 后端 | trace 落库 claim 结果 |
| 产品 | 阈值与拒答联动 |

### 15.10 周会看板

`faithfulness_p50` 按周；`top_unsupported_claims` 聚类；与 [152 胡编归因](152.bad-case-hallucination-tutorial.md) 工单打通。""",
    ],
    "ragas-answer-relevancy": [
        """### 14.6 Relevancy 与 Refusal

拒答「资料不足」时 Relevancy 可能低——评测集要标 `expect_refusal: true`，此类 **单独统计** 或跳过 Relevancy。

### 14.7 多轮 Relevancy

[118 多轮](118.multi-turn-history-tutorial.md)：用 **完整用户意图**（含指代消解 [120](120.coreference-resolution-tutorial.md)）生成反向问题，否则「它呢？」会被判不相关。

### 14.8 与人工评分对齐

抽 20 条让人打 1-5 分「答非所问」，与 Relevancy 算 Spearman——相关系数 <0.6 要调反向问题 prompt。

### 14.9 创意场景

营销文案 Bot Relevancy 权重可降、Faithfulness 仍高——**指标权重因产品而异**，勿迷信单一排行榜。""",
    ],
    "golden-dataset": [
        """### 15.6 金标生命周期

| 阶段 | 动作 |
|------|------|
| 冷启动 | 20 条手工 + 5 条边界 |
| 成长期 | 每周从生产采样 5 条入库 |
| 稳定期 | 月度审计删除过时题 |
| 大改版 | 冻结旧集、 fork 新集 v2 |

### 15.7 敏感与脱敏

金标含真实用户问法须 **脱敏**；含薪资、病历的 **不进 Git**，放加密桶，CI 用合成子集。

### 15.8 与 [144 回归集](144.regression-test-set-tutorial.md) 分工

金标 **全面覆盖** 能力；回归集 **最小关键路径**（<30 条）每次 PR 必跑。回归集是金标的 **高优先级子集 + 历史 bug 复现**。

### 15.9 标注工具选型

表格起步 → Label Studio / 自研 UI；字段：`question`、`gold_answer`、`gold_chunk_ids`、`tags`、`difficulty`。

### 15.10 数据版本 bump 规则

改 `gold_answer` 文本 → **patch**；增删题 → **minor**；换业务域（HR→财务）→ **major**，旧指标不可横比。""",
    ],
    "regression-test-set": [
        """### 14.6 CI 超时策略

全量金标跑 RAGAS 可能要十分钟；回归集目标 **<3 分钟**。超时则只跑 smoke 10 条 + nightly 全量。

### 14.7 Flaky 测试

LLM 评测有随机性：同一题跑三次 Faithfulness 波动 >0.1 标 `flaky`；固定 [29](29.llm-sampling-tutorial.md) seed 与 `temperature=0`。

### 14.8 阻塞 vs 告警

| 指标 | PR 阻塞 | 告警 |
|------|---------|------|
| 回归 Faithfulness | 降 >0.05 | 降 >0.02 |
| 回归 Recall | 降 >0.1 | 降 >0.05 |
| 延迟 P95 | +50% | +20% |

### 14.9 失败 artifact

CI 失败上传：question、answer、contexts、diff JSON，链接到 [147 trace](147.langsmith-tracing-tutorial.md) 方便修。""",
    ],
    "deepeval": [
        """### 13.6 DeepEval 与 RAGAS 指标对照

| DeepEval 指标 | 近似 RAGAS |
|---------------|------------|
| FaithfulnessMetric | faithfulness |
| ContextualPrecision | context_precision |
| ContextualRecall | context_recall |
| AnswerRelevancy | answer_relevancy |

数值 **不可直接横比**——裁判模型与 prompt 不同；团队选 **主标尺** 即可。

### 13.7 pytest 集成

```python
# pip install deepeval
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric

@pytest.mark.parametrize("row", load_regression_rows())
def test_faithfulness(row):
    case = LLMTestCase(
        input=row["question"],
        actual_output=row["answer"],
        retrieval_context=row["contexts"],
    )
    assert_test(case, [FaithfulnessMetric(threshold=0.8)])
```

### 13.8 何时值得上 DeepEval

已有 [141 RAGAS](141.ragas-faithfulness-tutorial.md) 脚本、需要 **pytest 原生**、或要用 **G-Eval 自定义 rubric** 时；小 PoC 不必两套并行。

### 13.9 成本

DeepEval 默认也调 LLM 当裁判；与 RAGAS 一样计入 [27 Token 计费](27.token-counting-billing-tutorial.md) 预算。""",
    ],
}


ARTICLES: dict[str, dict] = {}

ARTICLES["137.pluggable-store-retriever-generator-tutorial.md"] = {
    "slug": "pluggable-store-retriever-generator",
    "images": [
        ("01-pluggable-idea.png", "hub-spoke", "§3 可插拔是什么"),
        ("02-three-interfaces.png", "comparison-matrix", "§4 三接口"),
        ("03-concept-map.png", "bento-grid", "§11 概念地图"),
    ],
    "prompts": [
        ("01-pluggable-idea.md", "hub-spoke", "可插拔 Store/Retriever/Generator", """Center hub: 业务只依赖接口

Spoke 1: VectorStore 存取
Spoke 2: Retriever 召回
Spoke 3: Generator 生成
Spoke 4: 配置注入实现类""", "可插拔下游 · §3"),
        ("02-three-interfaces.md", "comparison-matrix", "三接口职责对照", """Row 1: Store — upsert/search/delete
Row 2: Retriever — query→chunks+scores
Row 3: Generator — messages→answer
Footer: 不互相越权""", "三接口 · §4"),
        ("03-concept-map.md", "bento-grid", "概念地图", """Box1: 136 上游可插拔
Box2: 93-112 链路
Box3: 依赖注入
Box4: 评测 E 轨""", "概念地图 · §11"),
    ],
    "body": f"""# D 框架与架构（十）：可插拔 Store / Retriever / Generator 完全指南

> [136 篇](136.pluggable-parser-splitter-embedder-tutorial.md) 把 **解析、切块、向量化** 做成可替换零件；用户问一句话时，后半段同样不能只绑死 Chroma 或某一个 Chat API。**可插拔**（Pluggable）在这里指：**向量库、检索策略、生成后端** 都通过 **窄接口 + 配置** 注入，换实现不改编排代码。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 轨地基篇**（路线图第 **154** 条），承接 C 模块 [93–112 检索与生成链路](93.hybrid-search-tutorial.md)，为 [138 配置驱动管道](138.config-driven-pipeline-tutorial.md) 与 E 轨评测打底。前置：[76 Chroma](76.chroma-vector-db-tutorial.md)、[127 LangChain Retriever](127.langchain-retriever-tutorial.md)、[110 RAG Prompt](110.rag-prompt-template-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)。

---

## 目录

1. [前言：上游可插拔了，下游还在写 if/else？](#1-前言上游可插拔了下游还在写-ifelse)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [可插拔下游是什么](#3-可插拔下游是什么)
4. [三个核心接口：Store、Retriever、Generator](#4-三个核心接口storeretrievergenerator)
5. [VectorStore：持久化与元数据](#5-vectorstore持久化与元数据)
6. [Retriever：召回策略可组合](#6-retriever召回策略可组合)
7. [Generator：Prompt 与采样参数外置](#7-generatorprompt-与采样参数外置)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：依赖注入 Mini-RAG](#9-综合实战依赖注入-mini-rag)
10. [与 LangChain / 自研 Pipeline 的边界](#10-与-langchain--自研-pipeline-的边界)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：上游可插拔了，下游还在写 if/else？

[136 篇](136.pluggable-parser-splitter-embedder-tutorial.md) 结束时，你的 ingest 可能是：

```text
Parser → Splitter → Embedder → ???
```

很多初学者在 `???` 处直接写：

```python
if backend == "chroma":
    ...
elif backend == "faiss":
    ...
```

问一句、答一句的路径同样混乱：`search` 与 `chat` 耦在一个 400 行文件里。结果是：**换向量库要改三处；做 A/B 检索策略要复制粘贴整条链**。

**可插拔 Store / Retriever / Generator** 要解决的问题是：把 [93 混合检索](93.hybrid-search-tutorial.md)、[98 Top-k](98.top-k-retrieval-tutorial.md)、[110 Prompt 模板](110.rag-prompt-template-tutorial.md)、[29 采样](29.llm-sampling-tutorial.md) 这些 **已经学过的能力**，收进 **三个稳定接口**，由 **工厂或配置** 组装。

**读完本文，你应该能做到：**

1. 画出 **Store / Retriever / Generator** 的职责边界。  
2. 用 **Protocol 或 ABC** 定义接口，提供 Chroma + OpenAI 兼容实现。  
3. 跑通 §9 **依赖注入** 的 Mini-RAG，不换业务代码换后端。  
4. 说明与 [127 Retriever](127.langchain-retriever-tutorial.md) 包装层的关系。  
5. 对照 §8 识别 **四种耦合翻车**。

### 1.1 路线图位置

```text
136 上游可插拔（Parser/Splitter/Embedder）
154 Store/Retriever/Generator ← 本篇
155 配置驱动管道 [138]
156+ RAGAS 评测
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 向量存储 | VectorStore / Store | 向量的增删查与元数据 |
| 检索器 | Retriever | query → 相关 chunk 列表 |
| 生成器 | Generator | messages → 模型答案 |
| 依赖注入 | Dependency Injection | 构造时传入实现，非硬编码 |
| 协议 | Protocol | 结构化类型，描述最小方法集 |

---

## 2. 本文边界与动手路径

**档位：D 轨地基篇（路线图 154）。**

**本文讲：** 三接口定义、Chroma Store、Hybrid Retriever 组合思路、Generator 封装、DI 实战。  
**本文不讲：** 完整 DI 框架（Spring 级）、K8s 服务发现、每一个云厂商 SDK。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §4 画三框图 | 能口述职责 |
| B | 实现 `ChromaStore` | upsert + search |
| C | 实现 `DenseRetriever` | 调 Store，带 filter |
| D | 实现 `OpenAIGenerator` | messages → text |
| E | §9 `RagPipeline` 注入 | 换 Fake 实现可单测 |
| F | §8 先错对对 | 四种错 |

**环境：** Python 3.10+；`pip install chromadb openai`；API Key 可选（Generator 可 Mock）。

### 2.2 沿用前文（检索与生成链）

{COMMON_RAG_LINKS}

---

## 3. 可插拔下游是什么

读下图：业务编排层只看见三个插槽，底下可换具体实现。

![可插拔下游架构](image/pluggable-store-retriever-generator/01-pluggable-idea.png)

对照上图：

- **Store** 回答「向量与原文存在哪、怎么按 id 查」；  
- **Retriever** 回答「这个问题召哪些 chunk、是否混合、是否重排」——内部可调 [93](93.hybrid-search-tutorial.md)、[96](96.bge-reranker-tutorial.md)；  
- **Generator** 回答「怎么调模型、用什么 [110 Prompt](110.rag-prompt-template-tutorial.md) 与 [29 采样](29.llm-sampling-tutorial.md)」；  
- 编排层（未来将见 [138 配置驱动](138.config-driven-pipeline-tutorial.md)）**只调三个接口**。

通俗说：**电源插头标准化**——主机不关心墙上是国标还是欧标，只要接口形状一致。

---

## 4. 三个核心接口：Store、Retriever、Generator

读下图：三列对照，避免 Store 里写生成逻辑。

![三接口职责](image/pluggable-store-retriever-generator/02-three-interfaces.png)

下面用 **typing.Protocol** 定义最小面（演示接口形状；运行前需 `from typing import Protocol`）。

**演示目标**：三个 Protocol 的最小方法签名。  
**环境**：Python 3.10+。  
**预期**：类型检查通过；实现类只需实现列出的方法。

```python
from typing import Protocol
from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict
    score: float | None = None

class VectorStore(Protocol):
    def upsert(self, chunks: list[Chunk]) -> None: ...
    def search(self, query_embedding: list[float], k: int, filters: dict | None) -> list[Chunk]: ...
    def delete(self, chunk_ids: list[str]) -> None: ...

class Retriever(Protocol):
    def retrieve(self, query: str, k: int = 5, filters: dict | None = None) -> list[Chunk]: ...

class Generator(Protocol):
    def generate(self, messages: list[dict], **params) -> str: ...
```

**解读**：`Retriever` **不继承** Store——它 **持有** Store 和 Embedder（来自 [136](136.pluggable-parser-splitter-embedder-tutorial.md)），对外只暴露 `retrieve`。

---

## 5. VectorStore：持久化与元数据

**VectorStore**（向量存储）：封装 [76 Chroma](76.chroma-vector-db-tutorial.md) 或 [75 FAISS](75.faiss-ann-tutorial.md) + sidecar。

| 方法 | 职责 | 不应做 |
|------|------|--------|
| upsert | 写入向量+文本+metadata | 调 LLM |
| search | ANN + filter | Query 改写 |
| delete | 按 chunk_id 删 | 重排序 |

**演示目标**：Chroma 持久化 Store。  
**前置**：`pip install chromadb`；本地 `./chroma_db` 目录。  
**预期**：`upsert` 后 `search` 能返回带 `doc_id` 的 Chunk。

```python
import chromadb
from chromadb.config import Settings

class ChromaVectorStore:
    def __init__(self, path: str = "./chroma_db", collection: str = "kb"):
        self._client = chromadb.PersistentClient(path=path)
        self._col = self._client.get_or_create_collection(collection)

    def upsert(self, chunks: list[Chunk]) -> None:
        self._col.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
            embeddings=None,  # 若已算好向量则传入
        )

    def search(self, query_embedding: list[float], k: int, filters: dict | None) -> list[Chunk]:
        res = self._col.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filters or None,
        )
        out = []
        for i, cid in enumerate(res["ids"][0]):
            out.append(Chunk(
                chunk_id=cid,
                text=res["documents"][0][i],
                metadata=res["metadatas"][0][i] or {{}},
                score=res["distances"][0][i] if res.get("distances") else None,
            ))
        return out
```

与 [53 ACL](53.metadata-acl-tutorial.md) 联调时，`filters={{"acl_group": "staff"}}` 在 **Store 层或 Retriever 层** 二选一，团队定一处为准，避免双滤漏网。

---

## 6. Retriever：召回策略可组合

**Retriever** 是可组合层：  
- `DenseRetriever`：Embed query → Store.search；  
- `HybridRetriever`：BM25 + Dense → [94 RRF](94.rrf-fusion-tutorial.md)；  
- `RerankRetriever`：装饰器，先宽召回再 [96 BGE](96.bge-reranker-tutorial.md)。

```python
class DenseRetriever:
    def __init__(self, store: VectorStore, embedder):
        self.store = store
        self.embedder = embedder

    def retrieve(self, query: str, k: int = 5, filters: dict | None = None) -> list[Chunk]:
        vec = self.embedder.embed_query(query)
        return self.store.search(vec, k=k, filters=filters)
```

**先错**：在 Retriever 里 `openai.ChatCompletion.create` 生成答案——**生成越权**。  
**对**：答案只出现在 `Generator.generate`。

与 [107 预算](107.context-budget-tutorial.md)、[28 窗口](28.context-window-tutorial.md)：Retriever 返回条数与单 chunk 长度由 **编排层** 或 **_BudgetAwareRetriever 装饰器** 截断，接口仍返回 `list[Chunk]`。

---

## 7. Generator：Prompt 与采样参数外置

**Generator** 封装 [35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)，读取 [110](110.rag-prompt-template-tutorial.md) 组好的 `messages`。

```python
from openai import OpenAI

class OpenAICompatibleGenerator:
    def __init__(self, model: str = "deepseek-chat", base_url: str | None = None):
        self.client = OpenAI(base_url=base_url) if base_url else OpenAI()
        self.model = model

    def generate(self, messages: list[dict], **params) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=params.get("temperature", 0.1),
        )
        return resp.choices[0].message.content or ""
```

| 参数 | 建议 | 关联 |
|------|------|------|
| temperature | 评测 0～0.2 | [29 采样](29.llm-sampling-tutorial.md) |
| max_tokens | 留足引用区 | [28 窗口](28.context-window-tutorial.md) |
| model | 配置项 | [138 配置驱动](138.config-driven-pipeline-tutorial.md) |

---

## 8. 先错对对：四种典型翻车

{_mistakes([
    ("Store 里写 RAG 全流程", "Chroma 类 800 行，无法单测检索。", "Store 只做 CRUD+ANN；编排进 Pipeline。"),
    ("Retriever 返回 str 不给 Chunk", "生成层无法引用 [113]。", "返回带 chunk_id、metadata 的结构体。"),
    ("Generator 里偷偷 search", "换模型就要改检索，A/B 不可能。", "Generator 只吃 messages，上下文由上层组装。"),
    ("接口背后直接 import chromadb", "单元测试必须起真库。", "构造函数注入实现；测试用 InMemoryStore。"),
])}

---

## 9. 综合实战：依赖注入 Mini-RAG

**阅读顺序**：先读完 §4～§7。

**演示目标**：`RagPipeline` 类组合三接口，main 里换配置即可换后端。  
**预期**：打印 answer + 引用 chunk_id 列表。

```python
def build_messages(question: str, chunks: list[Chunk]) -> list[dict]:
    ctx = "\\n".join(f"[{{i+1}}] {{c.text}}" for i, c in enumerate(chunks))
    return [
        {{"role": "system", "content": "仅根据参考资料回答；不足则拒答。"}},
        {{"role": "user", "content": f"参考资料：\\n{{ctx}}\\n\\n问题：{{question}}"}},
    ]

class RagPipeline:
    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    def ask(self, question: str, k: int = 5) -> dict:
        chunks = self.retriever.retrieve(question, k=k)
        messages = build_messages(question, chunks)
        answer = self.generator.generate(messages, temperature=0.1)
        return {{"answer": answer, "chunks": [c.chunk_id for c in chunks]}}

# main：从配置或工厂组装
# pipeline = RagPipeline(DenseRetriever(store, embedder), OpenAICompatibleGenerator(...))
```

端到端对齐 [93–112](93.hybrid-search-tutorial.md)：**检索 → 预算 → Prompt → 生成 → 引用**。下一篇 [138](138.config-driven-pipeline-tutorial.md) 把 `main` 里的 `new` 换成 YAML。

---

## 10. 与 LangChain / 自研 Pipeline 的边界

| 层 | 自研接口 | LangChain |
|----|----------|-----------|
| 域核心 | `Retriever.retrieve` | 可选包装 |
| 实验 | LCEL 快速试 | [126 LCEL](126.langchain-lcel-tutorial.md) |
| 评测 | 对 `RagPipeline.ask` 打 RAGAS | 同上 |

[135 框架取舍](135.pipeline-vs-framework-tutorial.md)：厚接口 + 薄适配器，而非反过来。

---

## 11. 综合概念地图

![概念地图](image/pluggable-store-retriever-generator/03-concept-map.png)

对照上图：**136 上游** → **本篇三接口** → **138 配置** → **139–145 评测**。

---

## 12. 常见陷阱与 FAQ

{_faq([
    ("三个接口能合并成两个吗？", "PoC 可将 Retriever+Store 合并；但一旦上 Hybrid/Rerank，拆分更省重构成本。"),
    ("FAISS 如何实现 Store？", "封装 index + id_map；filter 需预筛 id 列表，见 [75](75.faiss-ann-tutorial.md) 与 [88](88.metadata-filter-retrieval-tutorial.md)。"),
    ("Generator 要不要流式？", "接口可加 `generate_stream`；与 [116 SSE](116.sse-rag-streaming-tutorial.md) 对齐返回迭代器。"),
    ("如何做 A/B？", "工厂注册两个 Retriever 实现，配置 `retriever_class` 切换，见 [153 A/B](153.ab-experiment-rag-tutorial.md)。"),
    ("和 127 冲突吗？", "不冲突：127 是 LC 生态；本篇是 **你的** 域接口。可写 `LangChainRetrieverAdapter`。"),
])}

---

## 13. 总结与系列下一步

本篇把 RAG **下游** 收成 **Store / Retriever / Generator** 三插头，与 [136](136.pluggable-parser-splitter-embedder-tutorial.md) 上游对称，才能做 [138 配置驱动](138.config-driven-pipeline-tutorial.md) 与 E 轨 **可重复评测**。

**建议下一步：**

1. [138 配置驱动管道](138.config-driven-pipeline-tutorial.md)；  
2. [141 RAGAS Faithfulness](141.ragas-faithfulness-tutorial.md)；  
3. 用 Fake Retriever 给 `RagPipeline` 写单元测试；  
4. 对照 [93–112](93.hybrid-search-tutorial.md) 查缺补漏。

---

*系列：D 框架与架构 · 路线图第 154 条 · 地基篇*
""",
}

# Continue with remaining articles - import extended bodies
from _articles_137_145_bodies import BODIES as BODIES_138_140
from _articles_137_145_bodies2 import BODIES as BODIES_141_145

IMAGE_META = {
    "138.config-driven-pipeline-tutorial.md": {
        "slug": "config-driven-pipeline",
        "title": "配置驱动管道",
        "images": [
            ("01-config-flow.png", "linear-flow", "§3 配置驱动"),
            ("02-yaml-layers.png", "hierarchical-tree", "§4 分层"),
            ("03-concept-map.png", "bento-grid", "§11 概念地图"),
        ],
        "prompts": [
            ("01-config-flow.md", "linear-flow", "配置驱动启动流程", "Step1: 读 pipeline.yaml\nStep2: 工厂构造 Store\nStep3: 构造 Retriever\nStep4: 构造 Generator\nStep5: RagPipeline 运行", "配置驱动 · §3"),
            ("02-yaml-layers.md", "hierarchical-tree", "YAML 四层结构", "Root: version\nBranch: pipeline/store/retriever/generator\nLeaf: class + args", "YAML 分层 · §4"),
            ("03-concept-map.md", "bento-grid", "概念地图", "137 接口\n155 配置\n143 金标\n144 回归", "概念地图 · §11"),
        ],
    },
    "139.ragas-context-precision-tutorial.md": {
        "slug": "ragas-context-precision",
        "title": "RAGAS Context Precision",
        "images": [
            ("01-precision-idea.png", "comparison-matrix", "§3 Precision"),
            ("02-ranking-impact.png", "linear-flow", "§4 排序"),
            ("03-concept-map.png", "bento-grid", "§11 概念地图"),
        ],
        "prompts": [
            ("01-precision-idea.md", "comparison-matrix", "Context Precision 直觉", "绿=相关 红=无关\n前排红线拉低分数\n后排绿线部分挽回", "Precision · §3"),
            ("02-ranking-impact.md", "linear-flow", "重排提升 Precision", "ANN Top-k → Rerank → 进 Prompt", "重排 · §4"),
            ("03-concept-map.md", "bento-grid", "概念地图", "139 Precision\n140 Recall\n141 Faithfulness\n143 金标", "概念地图 · §11"),
        ],
    },
    "140.ragas-context-recall-tutorial.md": {
        "slug": "ragas-context-recall",
        "title": "RAGAS Context Recall",
        "images": [
            ("01-recall-idea.png", "hub-spoke", "§3 Recall"),
            ("02-recall-debug-tree.png", "flowchart", "§7 排查树"),
            ("03-concept-map.png", "bento-grid", "§11 概念地图"),
        ],
        "prompts": [
            ("01-recall-idea.md", "hub-spoke", "Context Recall 直觉", "Center: 金标需要 A+B\nSpoke: 只召回 A → 50%", "Recall · §3"),
            ("02-recall-debug-tree.md", "flowchart", "Recall 低排查树", "切块/索引/k/混合/filter/ACL", "排查 · §7"),
            ("03-concept-map.md", "bento-grid", "概念地图", "Recall vs Precision\n93 检索链", "概念地图 · §11"),
        ],
    },
    "141.ragas-faithfulness-tutorial.md": {
        "slug": "ragas-faithfulness",
        "title": "RAGAS Faithfulness",
        "images": [
            ("01-faithfulness-idea.png", "hub-spoke", "§3 Faithfulness"),
            ("02-claim-audit.png", "linear-flow", "§9 Claim 审计"),
            ("03-concept-map.png", "bento-grid", "§12 概念地图"),
        ],
        "prompts": [
            ("01-faithfulness-idea.md", "hub-spoke", "Faithfulness 是什么", "Center: Answer\nSpoke: Claim 分解\nSpoke: Entailment 判据\nSpoke: 支持比例", "Faithfulness · §3"),
            ("02-claim-audit.md", "linear-flow", "Claim 审计流程", "Answer → Claims → Judge → unsupported 列表", "审计 · §9"),
            ("03-concept-map.md", "bento-grid", "概念地图", "34 Grounding\n141 Faithfulness\n143 金标\n144 回归", "概念地图 · §12"),
        ],
    },
    "142.ragas-answer-relevancy-tutorial.md": {
        "slug": "ragas-answer-relevancy",
        "title": "RAGAS Answer Relevancy",
        "images": [
            ("01-relevancy-idea.png", "comparison-matrix", "§3 Relevancy"),
            ("02-reverse-question.png", "linear-flow", "§4 反向问题"),
            ("03-concept-map.png", "bento-grid", "§10 概念地图"),
        ],
        "prompts": [
            ("01-relevancy-idea.md", "comparison-matrix", "Answer Relevancy", "Q 与 Q' 相似度\n忠实但答非所问", "Relevancy · §3"),
            ("02-reverse-question.md", "linear-flow", "反向问题", "Answer → 生成 Q' → sim(Q,Q')", "反向问题 · §4"),
            ("03-concept-map.md", "bento-grid", "概念地图", "四指标三角\n141 Faithfulness", "概念地图 · §10"),
        ],
    },
    "143.golden-dataset-tutorial.md": {
        "slug": "golden-dataset",
        "title": "Golden Dataset",
        "images": [
            ("01-golden-idea.png", "comparison-matrix", "§3 金标"),
            ("02-annotation-flow.png", "linear-flow", "§6 标注流程"),
            ("03-concept-map.png", "bento-grid", "§12 概念地图"),
        ],
        "prompts": [
            ("01-golden-idea.md", "comparison-matrix", "Golden Dataset", "左: 噪声日志\n右: 结构化金标+版本", "金标 · §3"),
            ("02-annotation-flow.md", "linear-flow", "标注流程", "起草→审校→绑 chunk_id→抽检", "标注 · §6"),
            ("03-concept-map.md", "bento-grid", "概念地图", "143 金标\n144 回归\n141 评测", "概念地图 · §12"),
        ],
    },
    "144.regression-test-set-tutorial.md": {
        "slug": "regression-test-set",
        "title": "回归测试集",
        "images": [
            ("01-regression-idea.png", "hub-spoke", "§3 回归集"),
            ("02-ci-gate.png", "linear-flow", "§6 CI"),
            ("03-concept-map.png", "bento-grid", "§10 概念地图"),
        ],
        "prompts": [
            ("01-regression-idea.md", "hub-spoke", "回归测试集", "Center: 小而硬\nSpoke: PR 必跑\nSpoke: 金标子集", "回归 · §3"),
            ("02-ci-gate.md", "linear-flow", "CI 门禁", "PR → eval → 阈值 → pass/fail", "CI · §6"),
            ("03-concept-map.md", "bento-grid", "概念地图", "143 金标\n144 回归\n141 阈值", "概念地图 · §10"),
        ],
    },
    "145.deepeval-tutorial.md": {
        "slug": "deepeval",
        "title": "DeepEval",
        "images": [
            ("01-deepeval-idea.png", "hub-spoke", "§3 DeepEval"),
            ("02-vs-ragas.png", "comparison-matrix", "§4 对照"),
            ("03-concept-map.png", "bento-grid", "§11 概念地图"),
        ],
        "prompts": [
            ("01-deepeval-idea.md", "hub-spoke", "DeepEval 定位", "Center: pytest\nSpoke: LLMTestCase\nSpoke: Metrics", "DeepEval · §3"),
            ("02-vs-ragas.md", "comparison-matrix", "DeepEval vs RAGAS", "入口/CI/数值不可横比", "对照 · §4"),
            ("03-concept-map.md", "bento-grid", "概念地图", "141 RAGAS 主线\n145 了解", "概念地图 · §11"),
        ],
    },
}


def all_articles() -> dict[str, str]:
    out = {}
    for fname, meta in ARTICLES.items():
        out[fname] = meta["body"]
    out.update(BODIES_138_140)
    out.update(BODIES_141_145)
    return out


def main():
    articles = all_articles()
    rows = []
    for fname in sorted(articles.keys()):
        meta = IMAGE_META.get(fname) or ARTICLES.get(fname, {})
        slug = meta.get("slug", fname.split(".", 1)[1].replace("-tutorial.md", ""))
        body = pad_article(articles[fname], slug)
        path = ROOT / fname
        path.write_text(body, encoding="utf-8")
        h = hanzi_count(body)
        sec = section_count(body)
        if h < 5000:
            raise ValueError(f"{fname}: {h} hanzi < 5000")
        if sec < 13:
            raise ValueError(f"{fname}: {sec} sections < 13")
        # images
        if fname in ARTICLES:
            im = ARTICLES[fname]
            write_image_assets(im["slug"], fname, im["images"], im["prompts"])
        elif fname in IMAGE_META:
            im = IMAGE_META[fname]
            write_image_assets(im["slug"], im["title"], im["images"], im["prompts"])
        rows.append((fname, h, sec, "OK"))
    print("| 文件 | 汉字数 | 节数 | 状态 |")
    print("|------|--------|------|------|")
    for fname, h, sec, st in rows:
        print(f"| {fname} | {h} | {sec} | {st} |")


if __name__ == "__main__":
    main()
