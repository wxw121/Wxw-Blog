# -*- coding: utf-8 -*-
"""Generate batch 85-94 C4 tutorials (≥5000 hanzi each). Run: python _gen_batch_85_94.py"""
import re
from pathlib import Path

ROOT = Path(__file__).parent

COMMON_FOOTER = """
### {last_sec}.4 30 分钟动手作业

1. 跟做 §9 综合实战最小链路；  
2. 完成 §7 四条先错对对口述；  
3. 在团队 wiki 贴 §{concept_sec} 概念地图要点；  
4. 写一段与 [93 混合检索](93.hybrid-search-tutorial.md) 的衔接说明。

### {last_sec}.5 与 C4 检索栈串联背诵

正面问「索引之后还做什么？」背面答「[87 ANN 评测](87.ann-recall-latency-tutorial.md) → [88 过滤](88.metadata-filter-retrieval-tutorial.md) → [91 Dense](91.dense-retrieval-tutorial.md)/[92 Sparse](92.sparse-retrieval-rag-tutorial.md) → [93 Hybrid](93.hybrid-search-tutorial.md)」。  
正面问「多路分数怎么比？」背面答「[94 RRF](94.rrf-fusion-tutorial.md)，不要硬加权 BM25 与 cosine」。  
正面问「谁管权限？」背面答「[53 ACL](53.metadata-acl-tutorial.md) + [88 过滤](88.metadata-filter-retrieval-tutorial.md) + [89 租户](89.multi-tenant-namespace-tutorial.md)」。

---

> **初学者可能仍困惑的点**  
> - {confusion1}  
> - ANN 参数要在 [87 篇](87.ann-recall-latency-tutorial.md) 用金标回归，不能凭感觉。  
> - 混合检索见 [93](93.hybrid-search-tutorial.md)，融合见 [94 RRF](94.rrf-fusion-tutorial.md)。  
> - {confusion2}
"""


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def write_image_readme(slug: str, roadmap: int, title: str, images: list):
    d = ROOT / "image" / slug
    (d / "prompts").mkdir(parents=True, exist_ok=True)
    readme = f"""# {title}信息图（路线图 {roadmap}）


| 文件 | 布局 | 插入位置 |
|------|------|----------|
"""
    for fname, section, layout, _ in images:
        readme += f"| `{fname}` | {layout} | {section} |\n"
    readme += """

风格：hand-drawn-edu · 16:9 · 中文  
Prompt 见 `prompts/`。

说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。
"""
    (d / "README.md").write_text(readme, encoding="utf-8")
    for fname, section, layout, img_title in images:
        prompt = f"""---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {img_title}

{section}

Footer: {title} · {section.split()[0]}

All text Simplified Chinese.
"""
        (d / "prompts" / fname.replace(".png", ".md")).write_text(prompt, encoding="utf-8")


ARTICLES = []  # populated below via exec of article builders


def pad_section(title: str, paragraphs: list[str]) -> str:
    return f"## {title}\n\n" + "\n\n".join(paragraphs) + "\n\n"


def faq_block(qa_pairs: list[tuple[str, str]]) -> str:
    out = "## 常见陷阱与 FAQ\n\n"
    for q, a in qa_pairs:
        out += f"**Q：{q}**\nA：{a}\n\n"
    return out


def wrong_right_block(items: list[tuple[str, str, str]]) -> str:
    out = "## 先错对对：四种典型翻车\n\n"
    for i, (wrong, right, detail) in enumerate(items, 1):
        out += f"### {i}. 错：{wrong}\n\n**对：** {right}\n\n{detail}\n\n"
    return out


# ── 85 IVF ──────────────────────────────────────────────────────────
ARTICLE_85 = """# C4 向量存储（十一）：IVF 倒排文件索引完全指南

> [84 Flat](84.flat-brute-force-search-tutorial.md) 教会你用 **暴力检索当金标准**；数据到 **十万、百万** 时，全库扫描延迟爆炸。**IVF**（Inverted File Index，倒排文件索引）用 **K-means 聚类** 把向量空间切成 **nlist 个簇**：查询时只搜 **最近的 nprobe 个簇**，把扫描量从 **O(N)** 降到 **约 O(N/nlist × nprobe)**，用 **可控 recall 损失** 换速度。[75 FAISS](75.faiss-ann-tutorial.md) §5、§10 提过 `IndexIVFFlat`——本篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **102** 条），**加厚** 训练、add、search、nlist/nprobe 调参、recall 评测，并对接 [77 Milvus](77.milvus-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md) 的 IVF 索引。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[84 Flat](84.flat-brute-force-search-tutorial.md)、[25 Embedding](25.embedding-vector-tutorial.md)、[26 相似度](26.similarity-metrics-tutorial.md)、[66 L2 归一化](66.l2-normalization-tutorial.md)。下一篇 [86 HNSW](86.hnsw-index-tutorial.md) 走图索引另一条路；[87 ANN 评测](87.ann-recall-latency-tutorial.md) 教你量化 nprobe 旋钮。

---

## 目录

1. [前言：分簇再搜，少算九成距离](#1-前言分簇再搜少算九成距离)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [IVF 是什么](#3-ivf-是什么)
4. [训练阶段：K-means 与 nlist](#4-训练阶段k-means-与-nlist)
5. [查询阶段：nprobe 与倒排列表](#5-查询阶段nprobe-与倒排列表)
6. [FAISS IndexIVFFlat 实战](#6-faiss-indexivfflat-实战)
7. [nlist 与 nprobe 调参指南](#7-nlist-与-nprobe-调参指南)
8. [recall@k 评测流水线](#8-recallk-评测流水线)
9. [先错对对：六种典型翻车](#9-先错对对六种典型翻车)
10. [综合实战：Flat vs IVF 对照实验](#10-综合实战flat-vs-ivf-对照实验)
11. [Milvus / pgvector 中的 IVF](#11-milvus--pgvector-中的-ivf)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：分簇再搜，少算九成距离

[84 Flat](84.flat-brute-force-search-tutorial.md) 的计时实验告诉你：当 N 从一万涨到五十万，**单次 query 从毫秒变秒**。[75 FAISS](75.faiss-ann-tutorial.md) 索引族谱里，**IVF** 是 **最常用的大规模 ANN 结构之一**——Milvus 的 `IVF_FLAT`、pgvector 的 `ivfflat`、Faiss `IndexIVFFlat` **同一思想**，只是参数名略有差异。

**IVF**（Inverted File Index，倒排文件索引）分三阶段：

1. **训练（train）**：对训练集做 K-means，得到 **nlist 个质心**（簇中心）；  
2. **入库（add）**：每条向量分配到 **最近质心** 的倒排列表（inverted list）；  
3. **查询（search）**：找 query 最近的 **nprobe 个质心**，**只在这些列表里** 做精确距离（列表内常用 Flat，故称 **IVF_FLAT**）。

通俗说：**先把书分到 nlist 个书架（按主题聚类）；找书时只去最相关的 nprobe 个书架翻，而不是全馆**——偶尔书放错架，或你只去了一个架，会 **漏检**。

企业 RAG 里 IVF 常见位置：

| 场景 | 为何考虑 IVF |
|------|-------------|
| 百万～亿级 chunk | 全库 Flat 不可接受 |
| 内存预算紧 | 相对 HNSW 边结构，IVF 有时更省 |
| 已有 Faiss/Milvus 运维经验 | IVF 文档成熟、参数直觉清晰 |
| 离线批量建库 | train 可接受分钟级 job |

**读完本文，你应该能做到：**

1. 画 **train→add→search** 三阶段数据流。  
2. 用 FAISS 跑通 **IndexIVFFlat**（train、add、search、nprobe）。  
3. 调 **nlist、nprobe** 并输出 **recall–latency 表**。  
4. 用 [84 Flat](84.flat-brute-force-search-tutorial.md) 算 **recall@k** 金标准。  
5. 在 Milvus/pgvector 写出 **lists/probes** 对应配置。  
6. 识别 §9 六种翻车并口述修复。

### 1.1 C4 索引家族在路线图中的位置

```text
101 Flat（精确基线）[84]
102 IVF（倒排文件 + 聚类）← 本篇
103 HNSW（图索引）[86]
104 ANN recall–latency 评测 [87]
```

**学习顺序**：先 Flat 懂 ground truth，再 IVF 懂「分桶缩范围」，再 HNSW 懂「图导航」——否则调 nprobe 只有玄学。

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 倒排文件 | IVF | 按簇建倒排列表 |
| 簇数 | nlist / lists | 质心个数 |
| 探测簇数 | nprobe / probes | 查询时搜几个簇 |
| 质心 | centroid | K-means 中心 |
| 倒排列表 | inverted list | 簇内向量集合 |
| 量化器 | quantizer | 质心间距离的索引 |

### 1.3 读完本篇的最小交付物

1. 一张 **train→add→search** 手绘示意图；  
2. 一份 **FAISS IndexIVFFlat** 可运行脚本（§6、§10）；  
3. **nprobe 扫描表**（至少 5 个 nprobe 的 recall@10 + ms）；  
4. 与 [84 Flat](84.flat-brute-force-search-tutorial.md) 对照的一句话；  
5. Milvus `IVF_FLAT` 或 pgvector `ivfflat` 配置片段各一条。

### 1.4 与 [75 FAISS](75.faiss-ann-tutorial.md) §10 的加深关系

75 篇 §10 已给 **IVF 代码片段**——本篇把它 **展开成可上线流程**：train 样本策略、nlist/nprobe 表、recall 流水线、Milvus/pg 对照、Mini-RAG 综合实战。若你 **只跑过 Flat**，请先做 [84 篇](84.flat-brute-force-search-tutorial.md) 计时实验，再读本篇；否则无法理解「recall 掉了 8%」算不算事故。

### 1.5 企业案例叙事（虚构 composite）

某公司内部手册 RAG：**80 万 chunk**、BGE 768 维。PoC 用 Flat，P95 检索 **1.2s** 不可接受。切 `IndexIVFFlat`，nlist=1024，扫 nprobe 得 **recall@10=0.94 @ P95=38ms**。产品接受 6% 漏检由 **混合检索 + rerank** 兜底（[93][95]）。上线 manifest 写明 nprobe=24，**季度回归** [87 篇](87.ann-recall-latency-tutorial.md)。——这不是唯一答案，但是 **可复述的决策链**。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 102，概念 + 厚实战）。**

**本文讲：** IVF 原理、FAISS IndexIVFFlat、nlist/nprobe 调参、recall 评测、Milvus/pgvector 对应、与 Flat/HNSW 对照。  
**本文不讲：** IVF_PQ 乘积量化 bit 细节、GPU IVF 专用 kernel 全书、分布式 Milvus 分片内部路由、乘积量化与 OPQ 组合调参。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §3～§5，画三阶段 | 白板 3 分钟讲清 |
| B | 跑 §6 FAISS IVF | search 有 Top-k |
| C | §8 recall@10 | 对 Flat 有百分比 |
| D | 扫 nprobe 1→16 | 有 recall-latency 表 |
| E | 做 §10 综合实战 | Mini-RAG 对照 Flat |
| F | §9 先错对对 | 六种错法 |

**环境：** Python 3.10+；`pip install faiss-cpu numpy`。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| Flat 金标准 | [84 Flat](84.flat-brute-force-search-tutorial.md) |
| FAISS 全景 | [75 FAISS](75.faiss-ann-tutorial.md) |
| metric / cosine | [26 相似度](26.similarity-metrics-tutorial.md)、[66 归一化](66.l2-normalization-tutorial.md) |
| 向量库 IVF | [77 Milvus](77.milvus-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md) |
| ANN 评测 | [87 recall–latency](87.ann-recall-latency-tutorial.md) |

### 2.3 常见误解澄清

| 误解 | 事实 |
|------|------|
| IVF 一定比 HNSW 快 | 取决于 nprobe、数据规模、硬件；要评测 |
| train 一次永久有效 | 数据漂移后要 retrain 或重建 |
| nlist 越大越好 | 桶过多会导致空桶与训练不稳 |
| IVF 保证语义分桶 | K-means 按几何距离分，不是按 doc_id |
| 有 IVF 就不需要混合检索 | 专有名词仍靠 [92 BM25](92.sparse-retrieval-rag-tutorial.md) |

### 2.4 环境与版本说明

本文 FAISS API 以 **faiss-cpu 1.7+** 常见写法为准。`IndexIVFFlat` 构造函数第四参数 `metric` 在部分版本可省略（跟随 quantizer）。Windows 建议 `pip install faiss-cpu numpy`；若装不上，用 WSL 或查官方 wheel。GPU 版把 `faiss-cpu` 换 `faiss-gpu`，**train/add/search 流程相同**。

---

## 3. IVF 是什么

![IVF 倒排文件直觉](image/ivf-index/01-ivf-idea.png)

对照上图：

- **空间划分**：nlist 个质心覆盖向量空间（K-means 结果）；  
- **入库**：向量 → 最近质心 ID → 进入该 **倒排列表**；  
- **查询**：query → 最近 **nprobe** 个质心 → 合并这些列表 → 列表内 **精确算距离** → Top-k。

**列表内** 常用 Flat（[84 篇](84.flat-brute-force-search-tutorial.md)）存 **完整向量**——所以叫 **IVF_FLAT**；若列表内用 PQ 压缩向量，则是 **IVF_PQ**（路线图进阶，本篇点到为止）。

### 3.1 与 Flat 对比

| 维度 | Flat [84] | IVF 本篇 |
|------|-----------|----------|
| 训练 | 无 | 需要 K-means train |
| 查询扫描量 | N 条全扫 | ≈ (N/nlist)×nprobe |
| Recall@k | 100%（同 metric） | <100%，调 nprobe 提升 |
| 适用 N | 小～中（<1 万常够用） | 中大～大 |
| 运维 | 简单 | 需关注 train 分布、重训 |

### 3.2 与 HNSW 粗对比（预习 [86 篇](86.hnsw-index-tutorial.md)）

| 维度 | IVF | HNSW |
|------|-----|------|
| 结构 | 聚类分桶 | 多层图 |
| 调参 | nlist, nprobe | M, efConstruction, efSearch |
| 训练 | 需要 K-means | 一般不需要全局 train |
| 内存 | 向量 + 质心 | 向量 + 边（常更大） |
| 漏检原因 | 真邻居在「未探测的簇」 | 图导航早停 |

很多生产默认 **HNSW**（Qdrant、Milvus 文档常推荐）；**IVF 在超大规模、内存紧、可接受离线 train** 时仍常见。选型 **必须评测**，不能凭口号。

### 3.3 IVF 与 BM25「倒排」同名不同物

[19 BM25](19.bm25-sparse-retrieval-tutorial.md)、[20 倒排索引](20.inverted-index-tutorial.md) 的倒排是 **词项 → 文档列表**；IVF 的倒排是 **质心 ID → 向量列表**。都叫 inverted file，**面试时要说清维度**：稀疏 vs 稠密、词 vs 向量簇。

---

## 4. 训练阶段：K-means 与 nlist

### 4.1 为什么要 train

IVF 需要 **质心位置**——对 **代表性向量样本** 跑 K-means（Faiss 内部高度优化实现）。没有 train，**不知道桶在哪**，`add` 会失败或行为未定义。

```python
import faiss
import numpy as np

dim = 64
nlist = 100  # 簇数，即桶数
n_train = 10000

rng = np.random.default_rng(0)
train_vectors = rng.standard_normal((n_train, dim)).astype("float32")
faiss.normalize_L2(train_vectors)  # 余弦常见：归一化 + IP

quantizer = faiss.IndexFlatIP(dim)  # 质心距离用 IP（归一化后≈cosine）
index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)

assert not index.is_trained
index.train(train_vectors)  # 必须 train 后才能 add
assert index.is_trained
```

**训练样本从哪来？** 理想情况：**与线上一致的 Embedding 向量**，或从中抽样。用随机高斯向量 train、库却是 BGE 语义向量——质心 **不代表真实分布**，recall 会莫名其妙地差。

### 4.2 nlist 怎么选

| 经验法则 | 说明 |
|----------|------|
| sqrt(N)～4√N | 常见起点，如 N=100 万 → nlist 约 1000～4000 |
| 每桶向量数 N/nlist | 目标常 100～10000；太小桶内扫太贵，太大 nprobe 要增 |
| 太小 nlist | 每桶太大，失去分桶意义 |
| 太大 nlist | 训练慢、空桶多、小数据不稳定 |

**Milvus** 创建索引参数 `nlist`、[81 pgvector](81.pgvector-tutorial.md) `lists` **同类**。

读下图：nlist 与每桶大小的关系。

![IVF nlist 与倒排列表](image/ivf-index/02-nlist-nprobe.png)

### 4.3 train 样本量要多少

Faiss 文档常见建议：**训练向量数 ≥ nlist**（越多越好，至少 **数十倍 nlist** 更稳）。若只有 500 条向量却设 nlist=1000，K-means **欠定**，质心质量差。

**企业实践**：全量入库前，用 **本批 Embedding 的子集**（如 10% 或上限 100 万条）做 train；全量 add 进同一索引。数据 **大版本漂移** 时 **retrain + 重建**（衔接 [48 版本](48.doc-versioning-tutorial.md)、[49 增量](49.incremental-update-tutorial.md)）。

### 4.5 K-means 在 IVF 里的角色（不必手推公式）

训练阶段 Faiss 用 **K-means** 把训练向量分成 **nlist 组**，每组一个质心。目标：组内向量尽量靠近质心，组间质心尽量分开。你不需要自己实现 K-means——`index.train()` 封装好了——但要理解：**质心质量决定桶边界**，边界糊则 **nprobe 要更大** 才能补救。

**冷知识**：若数据有 **明显聚类**（如按部门的手册），IVF 桶有时会 **近似按主题分**——这是好事；若数据 **均匀混在一起**，桶边界更随机，漏检更依赖 nprobe。

### 4.6 训练数据不足时的降级策略

| 情况 | 建议 |
|------|------|
| N < 5000 | 优先 [84 Flat](84.flat-brute-force-search-tutorial.md) |
| N 中等但不够 train | 减小 nlist 至 4√N 下限 |
| 必须先上 IVF | 用全库向量 train，接受更长 train 时间 |
| 多语言混库 | train 样本 **按语言分层抽样**，避免某语言只占一个桶 |

### 4.7 重复 train 与覆盖

对 **同一 IndexIVFFlat 实例** 一般 **只 train 一次**。要换 nlist 或换 train 集 → **新建 index 对象** 或新文件，不要指望「再 train 一次」增量修正质心——Faiss 行为以版本文档为准，工程上 **全量重建最省心**。

---

## 5. 查询阶段：nprobe 与倒排列表

### 5.1 nprobe 是什么

```python
index.add(database_vectors)  # shape (N, dim)
index.nprobe = 10  # 搜 10 个最近质心对应的倒排列表

q = query_vector.reshape(1, -1).astype("float32")
faiss.normalize_L2(q)
sim, idx = index.search(q, k=10)
```

**nprobe ↑** → 合并更多列表、扫更多向量 → **recall ↑、延迟 ↑**。  
**nprobe = nlist** → 接近 **全库扫描**（仍可能有 train 边界效应，但不等于 Flat 的 100% 保证）。  
**nprobe = 1** → 最快，**漏检风险最大**——PoC 常犯此错。

### 5.2 漏检何时发生

1. **真邻居所在簇** 不在 query 最近的 nprobe 个质心之一（边界效应）；  
2. **训练分布与线上数据漂移**（新领域文档未参与 train）；  
3. **nlist 过大 + nprobe 过小**（只探 1～2 个簇在百万库上很危险）；  
4. **metric 不一致**（train 用 IP、查询向量未归一化却当 cosine 用）。

**工程铁律**：用 [84 Flat](84.flat-brute-force-search-tutorial.md) **算 recall@k**，扫 nprobe 找 **拐点**（详见 [87 篇](87.ann-recall-latency-tutorial.md)）。

### 5.3 与业务 k 的关系

RAG 常 **ANN 取 k=50**，再 [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md) 精排到 5。评测 IVF 时应用 **recall@50**，不是只测 recall@3——否则「精排前已漏真相关」仍会发生。

### 5.5 列表内扫描的复杂度

设库大小 N、nlist 个簇、探测 nprobe 个簇。理想均匀时每桶约 N/nlist 条，总扫描量约 **nprobe × (N/nlist)**。若 nlist=100、nprobe=10、N=100 万，约扫 **10 万条** 而非 100 万——**10× 加速**（常数因子忽略）。不均匀时某些桶极大，**最坏桶** 决定尾延迟——这也是为何要监控 **每桶大小分布**。

### 5.6 质心可视化（教学直觉）

二维向量可在散点图上 **画出质心** 与 query 到质心的连线：query 只进入 **连线最短的 nprobe 个质心** 所管辖的着色区域。高维无法画图，但 **「选最近几个簇中心」** 直觉不变。真邻居若在 **第八近** 的簇里而 nprobe=4，就会漏——这就是 ANN 合同要写的 **可接受漏检**。

---

## 6. FAISS IndexIVFFlat 实战

### 6.1 完整可运行脚本

```python
import time
import faiss
import numpy as np

DIM = 64
NLIST = 50
N_DB = 5000
K = 10

rng = np.random.default_rng(42)
n_train = max(N_DB, NLIST * 40)
train = rng.standard_normal((n_train, DIM)).astype("float32")
db = rng.standard_normal((N_DB, DIM)).astype("float32")
queries = rng.standard_normal((20, DIM)).astype("float32")

for x in (train, db, queries):
    faiss.normalize_L2(x)

quantizer = faiss.IndexFlatIP(DIM)
ivf = faiss.IndexIVFFlat(quantizer, DIM, NLIST, faiss.METRIC_INNER_PRODUCT)
ivf.train(train)
ivf.add(db)

flat = faiss.IndexFlatIP(DIM)
flat.add(db)

print("nprobe | recall@10 | ms/query")
for nprobe in [1, 2, 4, 8, 16, 32]:
    ivf.nprobe = nprobe
    t0 = time.perf_counter()
  # 对多条 query 取平均
    recalls = []
    for qi in range(len(queries)):
        _, idx_i = ivf.search(queries[qi : qi + 1], K)
        _, idx_f = flat.search(queries[qi : qi + 1], K)
        recalls.append(len(set(idx_i[0]) & set(idx_f[0])) / K)
    ms = (time.perf_counter() - t0) / len(queries) * 1000
    print(f"{nprobe:6d} | {np.mean(recalls):.3f}    | {ms:.3f}")
```

### 6.2 add 前未 train

`index.add` 在 **未 train** 时会 **报错**——§9 翻车之一。检查 `index.is_trained`。

### 6.3 IndexIDMap2 与业务 chunk_id

与 [75 篇](75.faiss-ann-tutorial.md) 相同：字符串 `chunk_id` 需映射 `int64`，或直接用 [76 Chroma](76.chroma-vector-db-tutorial.md) 存 string ids。

### 6.4 write_index / read_index

```python
faiss.write_index(ivf, "ivf_handbook.index")
ivf2 = faiss.read_index("ivf_handbook.index")
ivf2.nprobe = 8
```

**注意**：换 Embedding 模型 → **维度和空间全变** → 必须 **重建**（[25 篇](25.embedding-vector-tutorial.md)）。

---

## 7. nlist 与 nprobe 调参指南

### 7.1 推荐流程（与 [87 篇](87.ann-recall-latency-tutorial.md) 衔接）

1. 固定 metric（归一化 + IP 或明确 L2）；  
2. 选 nlist ≈ **4√N** 起步，结合每桶大小微调；  
3. nprobe 从 **1** 扫到 **nlist/4** 或 recall 达标；  
4. 记录 **P50/P95 延迟** 与 **mean recall@k**；  
5. 上线留 **10～20% 余量**——数据增长桶变大，同样 nprobe recall 可能缓降。

### 7.2 数据漂移与重训

新 ingest 向量分布变了（如新产品线文档）→ **定期重 train** 或 **大版本重建索引**。Milvus 的 segment 合并、[49 增量](49.incremental-update-tutorial.md) 策略要写在 runbook 里。

### 7.3 nlist 与 nprobe 联动直觉

| nlist | 每桶大小 | nprobe 建议起点 |
|-------|----------|-----------------|
| 小 | 大 | 较小 nprobe 也可能够 |
| 大 | 小 | 需较大 nprobe 才稳 |

没有万能表——**只有你的库上的 recall 曲线**。

### 7.4 GPU IndexIVFFlat

`faiss-gpu` 可把 IVF 放 GPU，接口类似；train 仍在 CPU 或 GPU 依版本。RAG PoC **CPU 足够**；QPS 高再考虑 GPU。

---

## 8. recall@k 评测流水线

![IVF recall 与 nprobe](image/ivf-index/03-recall-latency.png)

```python
def recall_at_k(ann_idx, flat_idx, queries, k=10):
    hits = []
    for i in range(len(queries)):
        _, ann_ids = ann_idx.search(queries[i : i + 1], k)
        _, flat_ids = flat_idx.search(queries[i : i + 1], k)
        hits.append(len(set(ann_ids[0]) & set(flat_ids[0])) / k)
    return float(np.mean(hits))
```

**金标准** 必须 [84 Flat](84.flat-brute-force-search-tutorial.md) **同 metric、同向量、同归一化**。  
**不要** 用人工标注集 **代替** Flat 来调 nprobe——那是 **端到端质量** 的另一层；索引层先用 Flat 对齐 ANN 行为。

### 8.1 与 metadata 过滤联测

[88 篇](88.metadata-filter-retrieval-tutorial.md) 前滤后，有效 N 变小，**同样 nprobe 可能更够**；也可能 **后滤凑不满 k**。应对 **带 ACL 的 query 子集** 单独扫一条曲线。

---

## 9. 先错对对：六种典型翻车

### 9.1 错：未 train 就 add

**对**：`index.train()` 后再 `add`；训练样本 **≥ nlist**，建议 **数十倍 nlist**。

### 9.2 错：nprobe=1 上线，用户抱怨「搜不到」

**对**：扫 recall–latency 曲线；生产 nprobe **压测达标**，写入配置与 [87 SLA](87.ann-recall-latency-tutorial.md)。

### 9.3 错：nlist=10000，数据只有两千条

**对**：空桶多、K-means 不稳；小数据用 [84 Flat](84.flat-brute-force-search-tutorial.md) 或减小 nlist。

### 9.4 错：训练用随机向量、库是真实 Embedding

**对**：train 样本应 **来自或代表** 真实库分布（同模型 embed 的向量）。

### 9.5 错：IVF 与 Flat metric 不一致

**对**：quantizer、列表内距离、query **同一 METRIC**；向量 **同一归一化策略**（[66 篇](66.l2-normalization-tutorial.md)）。

### 9.6 错：只加新向量从不重建，质心过时

**对**：大版本 **retrain + 新索引文件切换**；监控 recall 回归（[87 篇](87.ann-recall-latency-tutorial.md)）。

---

## 10. 综合实战：Flat vs IVF 对照实验

本节把 [75 §9](75.faiss-ann-tutorial.md)、[76 §9](76.chroma-vector-db-tutorial.md) 的 Mini-RAG 思想搬到 **IVF 选型** 上——**同一批 chunk、同一 Embedding、两索引对照**。

### 10.1 实验设计

| 变量 | 取值 |
|------|------|
| N | 10k（可扩 50k） |
| nlist | 50, 100 |
| nprobe | 1, 4, 8, 16 |
| k | 10（另测 k=50 模拟 rerank 前召回） |
| 指标 | recall@k vs Flat、P95 ms/query |

### 10.2 语料与 CHUNKS（示意）

```python
CHUNKS = [
    {"chunk_id": "hb:v1:c001", "text": "年假：入职满一年享有带薪年假 5 天。", "doc_id": "handbook-v1"},
    {"chunk_id": "hb:v1:c002", "text": "出差住宿：一线城市上限 600 元/晚。", "doc_id": "handbook-v1"},
    {"chunk_id": "fin:v1:c001", "text": "Q3 预算审批流程见财务制度第三章。", "doc_id": "finance-v1"},
    # ... 扩充到数千条真实或合成手册句
]
```

用 [25 Embedding](25.embedding-vector-tutorial.md) 同一模型 embed 成 `(N, dim)`；**禁止** 随机向量冒充语义实验结论。

### 10.3 端到端步骤

1. **建 Flat 索引** + `id_map.json`（[84 篇](84.flat-brute-force-search-tutorial.md)）；  
2. **建 IVF**：train 用全库或子集 → add → 扫 nprobe；  
3. 准备 **20+ 业务问句**（如「出差住酒店标准」「年假几天」）；  
4. 对每个问句：Flat Top-10 vs IVF Top-10，算 **recall@10**、打印 **chunk_id 差集**；  
5. nprobe 调到 **mean recall@10 ≥ 0.95**（或团队 SLA）再接入 RAG API；  
6. （可选）接 [76 Chroma](76.chroma-vector-db-tutorial.md) 同一数据，确认 **where 过滤** 与 IVF 索引可并存。

### 10.4 验收清单

| 检查项 | 通过标准 |
|--------|----------|
| train | `is_trained` 为真，add 无错 |
| recall 表 | ≥5 个 nprobe 数据点 |
| 延迟 | 记录 P95 ms |
| 漏检解释 | 能指出「未探测簇」案例 |
| 文档 | wiki 记录推荐 nlist/nprobe |

### 10.5 与 RAG 管道拼接

```text
question → embed → IVF search(k=50) → chunk texts
         → [93 混合] 时还有 BM25 路 → [94 RRF] → rerank → LLM
```

IVF 只负责 **稠密路的 ANN**；权限用 [88 过滤](88.metadata-filter-retrieval-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md)。

### 10.7 完整 Mini-RAG 脚本骨架（可粘贴运行）

```python
# ivf_mini_rag.py — 演示 Flat vs IVF 同一语料
import json
import time
import faiss
import numpy as np
from pathlib import Path

CHUNKS = [
    {"chunk_id": "hb:v1:c001", "text": "年假：入职满一年享有带薪年假 5 天。", "doc_id": "handbook-v1"},
    {"chunk_id": "hb:v1:c002", "text": "出差住宿：一线城市上限 600 元/晚。", "doc_id": "handbook-v1"},
    {"chunk_id": "hb:v1:c003", "text": "病假需提供二级以上医院证明。", "doc_id": "handbook-v1"},
    {"chunk_id": "fin:v1:c001", "text": "Q3 预算审批流程见财务制度第三章。", "doc_id": "finance-v1"},
    {"chunk_id": "it:v1:c001", "text": "VPN 申请请走 IT 工单系统 EXP-TICKET。", "doc_id": "it-v1"},
]
QUERIES = ["年假有几天", "出差酒店多少钱", "预算怎么批"]

def fake_embed(texts: list[str], dim: int = 64) -> np.ndarray:
    # PoC: hash-seeded vectors; production use sentence-transformers / API
    out = np.zeros((len(texts), dim), dtype="float32")
    for i, t in enumerate(texts):
        rng = np.random.default_rng(abs(hash(t)) % (2**32))
        out[i] = rng.standard_normal(dim)
    faiss.normalize_L2(out)
    return out

def build_indexes(vectors: np.ndarray, nlist: int):
    dim = vectors.shape[1]
    flat = faiss.IndexFlatIP(dim)
    flat.add(vectors)
    n_train = max(len(vectors), nlist * 40)
    train = fake_embed([c["text"] for c in CHUNKS] * (n_train // len(CHUNKS) + 1), dim)[:n_train]
    quantizer = faiss.IndexFlatIP(dim)
    ivf = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
    ivf.train(train)
    ivf.add(vectors)
    return flat, ivf

def search_rag(index, qvec, k, id_map):
    _, ids = index.search(qvec, k)
    return [{"chunk_id": id_map[i], "text": CHUNKS[i]["text"]} for i in ids[0]]

def main():
    texts = [c["text"] for c in CHUNKS]
    vecs = fake_embed(texts)
    id_map = list(range(len(CHUNKS)))
    flat, ivf = build_indexes(vecs, nlist=min(4, len(CHUNKS)))
    report = []
    for q in QUERIES:
        qv = fake_embed([q])
        flat_hits = search_rag(flat, qv, 3, id_map)
        for nprobe in [1, 2, 4]:
            ivf.nprobe = nprobe
            ivf_hits = search_rag(ivf, qv, 3, id_map)
            overlap = len({h["chunk_id"] for h in flat_hits} & {h["chunk_id"] for h in ivf_hits}) / 3
            report.append({"q": q, "nprobe": nprobe, "recall@3": overlap, "ivf_top": ivf_hits})
    Path("ivf_mini_rag_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote ivf_mini_rag_report.json")

if __name__ == "__main__":
    main()
```

运行后打开 `ivf_mini_rag_report.json`：对每个业务问句比较 **Flat Top-3** 与 **IVF Top-3** 的 `chunk_id` 差集。PoC 语料小，nlist 不要超过 chunk 数；扩到 **数千 chunk** 后 nlist 才能取 50～100 做有意义的曲线。

### 10.8 对照实验记录表（模板）

| 日期 | N | nlist | nprobe | recall@10 | P95 ms | 备注 |
|------|---|-------|--------|-----------|--------|------|
| | | | 1 | | | |
| | | | 4 | | | |
| | | | 8 | | | |
| | | | 16 | | | |

把此表贴进团队 wiki，与 [87 SLA](87.ann-recall-latency-tutorial.md) 绑定。每次 **Embedding 模型升级** 或 **大版本 ingest** 后重填。

### 10.9 与 Chroma 同数据对照（可选）

同一 CHUNKS 写入 [76 Chroma](76.chroma-vector-db-tutorial.md) `PersistentClient` 与 FAISS IVF 各一份：**query 文本相同** 时 Top-3 应 **高度重叠**（若 metric、归一化、embed 函数一致）。不一致时先查 **hnsw:space** 与 Faiss metric，不要先怪 IVF。

---

## 11. Milvus / pgvector 中的 IVF

### 11.1 Milvus IVF_FLAT（[77 篇](77.milvus-tutorial.md)）

创建索引时 `index_type=IVF_FLAT`，参数 `nlist`；查询传 `nprobe`（或 search param `params={"nprobe": 16}`，以版本文档为准）。  
**flush、segment** 与单机 FAISS 文件不同，但 **nlist/nprobe 直觉相同**。

### 11.2 pgvector ivfflat（[81 篇](81.pgvector-tutorial.md)）

```sql
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

SET ivfflat.probes = 10;  -- 会话级，类似 nprobe
SELECT chunk_id, text FROM chunks
ORDER BY embedding <=> $query_vec
LIMIT 10;
```

**lists** = nlist；**probes** = nprobe。SQL 层还可加 **WHERE doc_id = ...**（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

### 11.4 Milvus 创建 IVF 索引示例（示意）

```python
# 示意：pymilvus 2.x 风格，以你环境文档为准
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType

fields = [
    FieldSchema("chunk_id", DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=768),
]
schema = CollectionSchema(fields)
col = Collection("handbook", schema)
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "IP",
    "params": {"nlist": 128},
}
col.create_index("embedding", index_params)
# 查询时 search_params={"params": {"nprobe": 16}}
```

与本文 FAISS 参数 **一一对应**：`nlist`↔`nlist`，`nprobe`↔search `nprobe`。Collection **加载到内存** 后才能 search；运维流程见 [77 篇](77.milvus-tutorial.md)。

### 11.5 pgvector 与 SQL 事务

pgvector 的 ivfflat 索引在 **PostgreSQL 事务** 里与业务表共存：chunk 文本、`doc_id`、ACL 字段可 **同表 JOIN**（[81 篇](81.pgvector-tutorial.md)）。这是选 pgvector 的常见理由——**过滤 + 向量** 一条 SQL，但 **probes 仍要调**（本篇 nprobe 直觉）。

### 11.6 FAISS 与向量库选型一句话

| 需求 | 倾向 |
|------|------|
| 本地文件、最小依赖 | FAISS IVF 文件 |
| 分布式、亿级 | Milvus IVF |
| 已有 Postgres | pgvector ivfflat |
| 要内置 metadata DSL | [76 Chroma](76.chroma-vector-db-tutorial.md) / Qdrant |

IVF **思想不变**；变的是 **谁帮你管持久化、权限、HA**。

---

## 12. 综合概念地图

![IVF 概念地图](image/ivf-index/03-recall-latency.png)

| 概念 | 一句话 |
|------|--------|
| train | K-means 学质心 |
| nlist | 桶/簇个数 |
| nprobe | 查几个桶 |
| IVF_FLAT | 桶内全精度向量 |
| recall | 对 Flat 金标准 |
| Milvus/pg | lists / probes |
| 下一篇 | [86 HNSW](86.hnsw-index-tutorial.md)、[87 评测](87.ann-recall-latency-tutorial.md) |

**背诵版**：train 定桶 → add 入桶 → search 探 nprobe 桶 → 桶内 Flat 精排 → 用 84 算 recall → 上线写 manifest。

若你只能记住一张图：中心写 **IVF**，左支 **train(nlist)**，右支 **search(nprobe)**，底 **IVF_FLAT 桶内暴力**，顶 **RAG query embed**。与 [86 HNSW](86.hnsw-index-tutorial.md) 图索引对照时，IVF 是 **分柜**，HNSW 是 **路网**。面试被追问「IVF 漏检怎么办」：答 **加大 nprobe、改善 train 分布、上混合检索与 rerank、用 87 回归**。上线前务必把推荐 nprobe 与 recall 曲线 **贴进 PR 描述**，方便后人维护。本篇与 [84 Flat](84.flat-brute-force-search-tutorial.md) 配套阅读效果最佳。祝调参顺利。

---

## 13. 常见陷阱与 FAQ

**Q：IVF 和 BM25 倒排是一回事吗？**  
A：**不是**。BM25 是 **词→文档**（[19 篇](19.bm25-sparse-retrieval-tutorial.md)）；IVF 是 **质心→向量**。仅英文名相似。

**Q：训练要多久？**  
A：视 N、nlist、dim；百万级可能 **分钟～小时**；应作 **离线 job**，不要阻塞在线 API。

**Q：能否增量 add？**  
A：可 add 进已有列表；分布大变建议 **retrain** 或新索引切换。

**Q：nprobe 默认值能信吗？**  
A：Faiss 默认常 **偏小**；**必须按库评测**。

**Q：IVF 能 100% recall 吗？**  
A：nprobe=nlist 接近全扫，仍受 train 影响；要 **保证 100%** 用 [84 Flat](84.flat-brute-force-search-tutorial.md)。

**Q：和 [86 HNSW](86.hnsw-index-tutorial.md) 怎么选？**  
A：用 [87 篇](87.ann-recall-latency-tutorial.md) 在同一数据上画两条曲线；没有绝对赢家。

**Q：OpenSearch [83](83.opensearch-hybrid-tutorial.md) 用 IVF 吗？**  
A：常见 knn 用 HNSW；底层引擎选项因版本而异，以运维文档为准。

**Q：多租户 IVF 怎么隔离？**  
A：见 [89 篇](89.multi-tenant-namespace-tutorial.md)：逻辑 **namespace + 强制 filter**，不是靠 IVF 结构自动隔离。

**Q：GPU 值得吗？**  
A：QPS 高、延迟敏感再考虑；PoC **faiss-cpu** 即可。

**Q：面试 30 秒版？**  
A：「IVF 用 K-means 训练 nlist 个质心，向量入最近簇的倒排列表；查询只搜 nprobe 个最近簇内向量做精确距离。必须先 train 再 add。评测用 Flat 算 recall@k。Milvus IVF_FLAT 与 pgvector ivfflat 的 lists/probes 对应 nlist/nprobe。」

**Q：索引文件有多大？**  
A：IVF_FLAT 约 **向量矩阵 + 质心 + 少量元数据**；N×dim×4 字节是主项。百万×768 维仅向量约 **3GB** 量级，规划磁盘要留 **重建双份** 空间（[90 备份](90.vector-db-backup-tutorial.md)）。

**Q：能否用 Chroma 内置 IVF？**  
A：[76 Chroma](76.chroma-vector-db-tutorial.md) 底层 ANN 因版本而异，常见 HNSW；理解 IVF 有助于 **读任何库的 ANN 文档** 与 **Faiss 导出迁移**。

**Q：查询 embedding 要归一化吗？**  
A：若入库时 `normalize_L2` 且用 IP，**query 也必须同样归一化**（[66 篇](66.l2-normalization-tutorial.md)），否则最近簇选择都会偏。

**Q：IVF 适合实时频繁 insert 吗？**  
A：可 add，但 **分布漂移** 后 recall 掉；高频写场景要计划 **定期 retrain** 或 [49 增量](49.incremental-update-tutorial.md) 的大版本切换策略。

### 13.1 读路径自检（8 题）

1. 为何 IVF 必须先 train？  
2. nlist 过大过小各有什么问题？  
3. 漏检的四种原因？  
4. recall@k 金标准从哪来？  
5. pgvector probes 对应 Faiss 什么参数？  
6. IVF 与 BM25 倒排有何不同？  
7. 换 BGE 模型后 IVF 索引能否复用？  
8. 与 [86 HNSW](86.hnsw-index-tutorial.md) 选型比什么指标？

### 13.2 LangChain / LlamaIndex 用户注意

框架封装的 vector store **隐藏了 nprobe**。排障时要 **下沉到原生 API**（Faiss `index.nprobe`、Milvus search params、pg `ivfflat.probes`）。否则默认 nprobe 可能导致 **线上 recall 与本地实验不一致**。

### 13.3 与 [87 ANN 评测](87.ann-recall-latency-tutorial.md) 的交接

本篇给出 **nprobe 旋钮**；87 篇给出 **金标集、SLA、CI 回归** 模板。合起来才是可上线的 ANN 合同：「本库 nlist=100、nprobe=16、Recall@10≥0.92、P95≤30ms」。

---

## 14. 总结与系列下一步

1. **IVF = 聚类分桶 + 查 nprobe 桶 + 桶内 Flat**。  
2. **train、nlist、nprobe** 决定 recall–latency；**必须评测**。  
3. **金标准** 永远是 [84 Flat](84.flat-brute-force-search-tutorial.md)（同 metric）。  
4. Milvus、pgvector **参数名不同、直觉相同**。  
5. 下一篇 **[86 HNSW](86.hnsw-index-tutorial.md)** 图索引；**[87](87.ann-recall-latency-tutorial.md)** 把旋钮变成 SLA。

### 14.1 系列下一步

| 目标 | 阅读 |
|------|------|
| Flat 金标准 | [84](84.flat-brute-force-search-tutorial.md) |
| FAISS 全景 | [75](75.faiss-ann-tutorial.md) |
| HNSW | [86](86.hnsw-index-tutorial.md) |
| ANN 评测 | [87](87.ann-recall-latency-tutorial.md) |
| 元数据过滤 | [88](88.metadata-filter-retrieval-tutorial.md) |

### 14.2 给产品经理的一句话

「IVF 像图书馆按主题分架：找书时只去最相关的几个架子，比全馆逐本比较快很多，但偶尔书放错架子会漏——我们用数据测试调『去几个架子』的旋钮。」

### 14.3 读路径自检（6 题）

1. IVF 三阶段是什么？  
2. train 样本从哪来？  
3. nprobe 增大对 recall 和延迟的影响？  
4. 为何要对 Flat 算 recall@k？  
5. pgvector 的 lists/probes 对应什么？  
6. IVF 与 BM25 倒排有何不同？

### 14.4 30 分钟动手作业

1. 跑通 §6 脚本，保存 recall 表；  
2. 做 §10 至少 3 个问句的 Flat vs IVF 差集分析；  
3. 写 wiki：**本库推荐 nlist/nprobe** 及依据；  
4. 口述 §9 六种翻车各一条。

### 14.5 与混合检索串联

稠密路 IVF 常与 [92 BM25](92.sparse-retrieval-rag-tutorial.md) 并行 → [93 混合](93.hybrid-search-tutorial.md) → [94 RRF](94.rrf-fusion-tutorial.md)。IVF 只优化 **向量近邻**，不替代关键词路。

### 14.6 故障排查速查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| add 报错 | 未 train | 先 `train()` |
| recall 极低 | nprobe=1 或 train 分布错 | 扫 nprobe；换 train 样本 |
| 比 Flat 还慢 | nprobe 接近 nlist | 降 nprobe 或减 nlist |
| 结果每次略不同 | train 随机性 | 固定种子或保存索引文件 |
| 与 Chroma 结果不一致 | metric/归一化不同 | 对齐 [26][66] 配置 |

### 14.7 IVF_PQ 预习（不进本篇代码）

**IVF_PQ** 在列表内用 **乘积量化** 压缩向量，内存可再降一个数量级，但引入 **量化误差**。企业若在亿级库上内存告急，可在 **IVF_FLAT baseline 达标** 后再试 PQ，并用 [87 篇](87.ann-recall-latency-tutorial.md) 对比 **答案质量** 而非只看向量 recall。

### 14.8 与 Parent-Document（65 篇）拼接

若采用 [65 Parent-Document](65.parent-document-retriever-tutorial.md)：**只有 child 向量进入 IVF**；`id_map` 存 `child_chunk_id` 与 `parent_chunk_id`；search 命中 child 后 **查 parent store 取更长上下文** 拼 prompt。IVF 层无感知，但 **train/add 的向量必须全是 child**——不要把 parent 与 child 混进同一索引。

### 14.9 监控指标建议

生产建议采集：`ivf_search_latency_ms`（P50/P95）、`ivf_recall_sample`（夜间对 Flat 子集）、`index_vectors_total`、`nprobe` 配置版本。recall 抽样下跌 **>2%** 应告警并触发 [87 回归](87.ann-recall-latency-tutorial.md)。

### 14.10 一周学习计划

| 天 | 任务 |
|----|------|
| Mon | [84 Flat](84.flat-brute-force-search-tutorial.md) 计时 + 本篇 §3～§5 |
| Tue | 跑 §6，理解 train/add |
| Wed | 扫 nprobe，填 recall 表 |
| Thu | §10 综合实战 Mini-RAG |
| Fri | 读 [77 Milvus](77.milvus-tutorial.md) IVF 配置，团队分享 |

### 14.11 与 Elasticsearch / OpenSearch 的关系

[82 ES 向量](82.elasticsearch-vector-tutorial.md)、[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 的 **dense knn** 底层常是 HNSW；若运维提供 **Faiss IVF** 类引擎选项，**lists/probes 直觉仍适用本篇**。混合检索时 IVF 只管稠密 leg，BM25 leg 见 [92][93]。

### 14.12 安全与多租户

IVF **不理解** [53 ACL](53.metadata-acl-tutorial.md)。必须在 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 层 **前滤或后滤**；多租户逻辑隔离见 [89 篇](89.multi-tenant-namespace-tutorial.md)。**禁止** 靠「不同 nlist 桶」做权限——桶是语义聚类，不是安全边界。

### 14.13 磁盘与备份

`write_index` 产物需与 `id_map`、manifest **同版本备份**（[90 篇](90.vector-db-backup-tutorial.md)）。恢复后 **nprobe 配置** 要在 manifest 里，避免恢复旧索引却用新 nprobe 误以为 regression。

### 14.14 给实习生的检查清单

- [ ] 能白板画 train→add→search  
- [ ] 能解释 nlist 与 nprobe 各管什么  
- [ ] 能跑通 §6 并读出 recall 表  
- [ ] 能说出 IVF 与 HNSW 一个区别  
- [ ] 知道换 Embedding 要重建

---

> **初学者可能仍困惑的点**  
> - IVF **不是** 免费午餐——train 运维 + 漏检风险要算进总成本。  
> - **nlist 不是越大越好**；要与 N 和每桶大小平衡。  
> - 换 Embedding 模型要 **重建索引**，旧质心完全失效（[25 篇](25.embedding-vector-tutorial.md)）。
"""

# Due to script size limits, import remaining articles from companion module
from _articles_85_94_content import ARTICLES_REST  # noqa: E402

ARTICLES_ALL = [("85.ivf-index-tutorial.md", ARTICLE_85, {
    "slug": "ivf-index", "roadmap": 102, "title": "IVF 倒排文件索引完全指南",
    "images": [
        ("01-ivf-idea.png", "§3 IVF 是什么", "hub-spoke", "IVF 倒排文件直觉"),
        ("02-nlist-nprobe.png", "§4 nlist 与倒排列表", "comparison-matrix", "nlist 与 nprobe"),
        ("03-recall-latency.png", "§8 recall 评测", "flow-left-right", "IVF recall 与 nprobe"),
    ],
})] + ARTICLES_REST


def main():
    results = []
    for filename, content, meta in ARTICLES_ALL:
        path = ROOT / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        h = hanzi_count(content)
        write_image_readme(meta["slug"], meta["roadmap"], meta["title"], meta["images"])
        results.append((filename, h))
        status = "OK" if h >= 5000 else "LOW"
        print(f"{filename}: {h} hanzi [{status}]")
    low = [f for f, h in results if h < 5000]
    if low:
        raise SystemExit(f"Below 5000 hanzi: {low}")
    print("All articles OK.")


if __name__ == "__main__":
    main()
