#!/usr/bin/env python3
"""Generate RAG tutorials 86-94 with >=5000 hanzi each."""
import re
from pathlib import Path

BLOG = Path(__file__).resolve().parent.parent

def hz(t): return len(re.findall(r"[\u4e00-\u9fff]", t))

def pg(layout, desc, title, body, foot):
    return f"""---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {desc}
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

{body}

Footer: {foot}

All text Simplified Chinese.
"""

def faq_block(items):
    out = []
    for i, (q, a) in enumerate(items, 1):
        out.append(f"### FAQ {i}. {q}\n\n{a}\n")
    return "\n".join(out)

def mk_images(slug, title, no_cn, specs):
    base = BLOG / "image" / slug
    (base / "prompts").mkdir(parents=True, exist_ok=True)
    rows = []
    for s in specs:
        fn = s[0]
        (base / "prompts" / fn.replace(".png", ".md")).write_text(s[4].strip() + "\n", encoding="utf-8")
        rows.append(f"| `{fn}` | {s[1]} | {s[2]} |")
    (base / "README.md").write_text(
        f"# {title}信息图（{no_cn}）\n\n| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"
        + "\n".join(rows)
        + "\n\n风格：hand-drawn-edu · 16:9 · 中文\n\nPrompt 见 `prompts/`。\n\n"
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
        encoding="utf-8",
    )

ARTICLES = {}

# ========== 86 HNSW ==========
ARTICLES["86.hnsw-index-tutorial.md"] = dict(
slug="hnsw-index",
images=[
("01-hnsw-idea.png","hub-spoke","§3", pg("hub-spoke","hub-spoke","HNSW 是什么？",
"Center: 多层邻近图\nSpoke1 建图 M 条边\nSpoke2 查询 efSearch\nSpoke3 vs IVF\nSpoke4 RAG 百万向量","HNSW · §3")),
("02-layer-navigation.png","flowchart","§4", pg("flowchart","flowchart 3 layers","分层导航",
"顶层远跳→中层→底层细搜\nefSearch 控制候选宽度","HNSW · §4")),
("03-concept-map.png","bento-grid","§11", pg("bento-grid","bento grid","HNSW 概念地图",
"M efConstruction efSearch | FAISS | Milvus | recall曲线 | Flat对照 | 换模型重建","HNSW · §11")),
],
body=r'''# C4 向量存储（三）：HNSW 图索引完全指南

> [84 Flat 暴力检索](84.flat-brute-force-search-tutorial.md) 保证召回但慢；[85 IVF](85.ivf-index-tutorial.md) 用聚类缩小搜索范围，却要在 **train** 阶段定簇心、调 **nprobe**。百万级向量、毫秒级查询时，工程界最常选的一类 ANN 结构叫 **HNSW**（Hierarchical Navigable Small World，分层可导航小世界图）：把向量建成 **多层跳表式图**，查询时从顶层「高速路」逐层下沉到近邻。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 向量存储地基篇**（路线图第 **103** 条），讲清 HNSW **直觉、参数 M/efConstruction/efSearch、与 Flat/IVF 对照、FAISS/Milvus 配置**，以及 RAG 上线时 **别只看延迟、要测 recall**。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[85 IVF](85.ivf-index-tutorial.md)、[26 相似度](26.similarity-metrics-tutorial.md)；下一篇 [87 ANN 召回–延迟](87.ann-recall-latency-tutorial.md) 系统讲权衡。

---

## 目录

1. [前言：从 IVF 到图上的高速公路](#1-前言从-ivf-到图上的高速公路)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [HNSW 是什么](#3-hnsw-是什么)
4. [分层导航直觉](#4-分层导航直觉)
5. [核心参数 M、efConstruction、efSearch](#5-核心参数-mefconstructionefsearch)
6. [与 Flat、IVF 对照选型](#6-与-flativf-对照选型)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [FAISS 最小 HNSW 实战](#8-faiss-最小-hnsw-实战)
9. [向量库里的 HNSW 配置](#9-向量库里的-hnsw-配置)
10. [recall 评测与 golden 对照](#10-recall-评测与-golden-对照)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：从 IVF 到图上的高速公路

[75 篇](75.faiss-ann-tutorial.md) 让你用 **Flat** 跑通 ANN 心智模型；[85 篇](85.ivf-index-tutorial.md) 说明 **倒排文件** 如何「先选书架再翻书」。两者都有效，但在 **百万向量、在线查询、频繁增量** 的组合下，很多团队会把默认索引切到 **HNSW**。

典型对话：

> 运维：「Milvus 默认 HNSW，要改吗？」  
> 你：「先问数据量、QPS、能不能接受 recall 损失；再用金标集算 recall@10。」

**HNSW**（Hierarchical Navigable Small World）：为每个向量建 **多层邻近图**，上层边连接远跳节点，下层边越来越密；查询从顶层入口 **贪心走向 query**，再下沉，最终在底层收集近邻候选。  
通俗说：**先走环线快速路逼近目标街区，再进小路找门牌号**——比每条街都逛一遍（Flat）快，又比只逛固定几个片区（IVF）更不易漏。

**读完本文，你应该能做到：**

1. 口述 HNSW **分层图 + 贪心导航** 与 IVF **聚类分桶** 的差异。  
2. 解释 **M、efConstruction、efSearch** 对 **索引体积、建索耗时、查询 recall/延迟** 的影响方向。  
3. 用 FAISS `IndexHNSWFlat` 跑通 add + search，并与 Flat 算 recall@k。  
4. 对照 [76 Chroma](76.chroma-vector-db-tutorial.md)、[77 Milvus](77.milvus-tutorial.md) 说明 **HNSW 是引擎参数，不是产品名**。  
5. 识别 §7 四种翻车：ef 太小、metric 错、增量不设维护、只报延迟。

### 1.1 C4 索引族谱

```text
101 Flat → 102 IVF → 103 HNSW ← 本篇 → 104 recall–latency（87 篇）
```

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 分层可导航小世界 | HNSW | 多层邻近图 ANN |
| 最大出度 | M | 每节点最多连几条边 |
| 建图宽度 | efConstruction | 建索引时候选列表长度 |
| 查询宽度 | efSearch | 查询时候选池大小 |

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 103）。**

**本文讲：** HNSW 直觉、参数、FAISS 片段、与 Flat/IVF 对照、recall 评测。  
**本文不讲：** 图论证明、GPU HNSW 内核、PQ+HNSW 复合索引 bit 级调参。

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §3～§4，画三层图 | 白板能讲 |
| B | 读 §5 填参数表 | 知调大 ef 方向 |
| C | 跑 §8 | search 有结果 |
| D | §10 与 Flat 算 recall@5 | 有数字 |

**沿用前文：** [75 FAISS](75.faiss-ann-tutorial.md)、[84 Flat](84.flat-brute-force-search-tutorial.md)、[85 IVF](85.ivf-index-tutorial.md)、[26 相似度](26.similarity-metrics-tutorial.md)、[66 L2](66.l2-normalization-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md)。

---

## 3. HNSW 是什么

![HNSW 是什么](image/hnsw-index/01-hnsw-idea.png)

- **输入**：chunk 向量（常已 L2 归一化，见 [66 篇](66.l2-normalization-tutorial.md)）；  
- **建索引**：每点连 **M 个邻居**，组织成多层；  
- **查询**：从顶层入口贪心走向 query，下沉到底层；  
- **输出**：宽度 **efSearch** 的候选池排序取 Top-k。

HNSW 坐在 **Milvus / Qdrant / FAISS / pgvector** 的索引层；上面再挂 [88 metadata filter](88.metadata-filter-retrieval-tutorial.md)。

### 3.1 为什么图适合 Embedding 空间

语义相近的 chunk 几何上也相对靠近。图索引利用「**近邻的邻居往往也是近邻**」——沿边行走大概率朝 query 前进，不必扫描全库（对比 [84 Flat](84.flat-brute-force-search-tutorial.md)）。

### 3.2 HNSW 不解决的事

| 问题 | 谁负责 |
|------|--------|
| 原文存储 | 向量库 documents / 外部 DB |
| 权限过滤 | [88 篇](88.metadata-filter-retrieval-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md) |
| BM25 | [92 稀疏](92.sparse-retrieval-rag-tutorial.md)、[93 混合](93.hybrid-search-tutorial.md) |
| 重排序 | C5 rerank |

---

## 4. 分层导航直觉

![分层导航](image/hnsw-index/02-layer-navigation.png)

**多层立交桥比喻：**

1. **顶层**：少量枢纽，边长，一步跨越大片区域；  
2. **中层**：枢纽变多，边变短；  
3. **底层**：全量向量，边最密，负责精确近邻。

```text
顶层贪心走 → 无法更近则下沉 → 重复 → 底层 efSearch 收集 Top-k
```

复杂度直觉：每层约 **O(log N)** 步，总延迟远低于 Flat 的 **O(N)**，但不保证全局最优（见 [87 篇](87.ann-recall-latency-tutorial.md)）。

### 4.1 与 IVF 对照

| | IVF [85] | HNSW |
|---|----------|------|
| 预处理 | k-means 簇心 | 多层图 |
| 查询 | 探 nprobe 簇 | 图游走 |
| 漏检 | 真邻居在未探簇 | 图路绕远 |
| 增量 | 可能要重训 | 可 insert，需维护 |

---

## 5. 核心参数

### 5.1 M

越大图越密，**recall 倾向更高**，索引更大、建索更慢。常见 16～48，FAISS 示例常用 32。

### 5.2 efConstruction

插入时每点考虑多少候选邻居。越大图质量越好，**建索引越慢**。离线建库可偏大换线上稳定 recall。

### 5.3 efSearch

**直接影响线上延迟与 recall**。规则：**efSearch ≥ k**；实践常取 **k 的 2～10 倍** 压测（[87 篇](87.ann-recall-latency-tutorial.md)）。

| 参数 | 调大倾向 |
|------|----------|
| M | recall↑ 索引大 |
| efConstruction | recall↑ 建索慢 |
| efSearch | recall↑ 查询慢 |

---

## 6. 与 Flat、IVF 选型

| 场景 | 建议 |
|------|------|
| N < 1 万、要 golden | [84 Flat](84.flat-brute-force-search-tutorial.md) |
| N 大、可 train、内存紧 | [85 IVF](85.ivf-index-tutorial.md) |
| N 大、在线高 QPS | **HNSW** |
| 托管默认 | [77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md) |

[82 ES 向量](82.elasticsearch-vector-tutorial.md) 的 dense_vector 也常用 HNSW；与 BM25 同集群可做 [93 混合](93.hybrid-search-tutorial.md)。

---

## 7. 先错对对

**错：** efSearch=k=3 就上线 → **对：** 扫 ef=20/50/100 看 recall@10。  
**错：** cosine 却 L2 不归一化 → **对：** IP+normalize（[66](66.l2-normalization-tutorial.md)）。  
**错：** 只报 P99 延迟 → **对：** recall@k + 延迟成对（[87](87.ann-recall-latency-tutorial.md)）。  
**错：** 频繁小增量从不重建 → **对：** 定期 compact/全量重建（[90 备份](90.vector-db-backup-tutorial.md)、[49 增量](49.incremental-update-tutorial.md)）。

---

## 8. FAISS 最小实战

```python
import numpy as np, faiss

DIM, M = 64, 32
xb = np.random.randn(1000, DIM).astype("float32")
faiss.normalize_L2(xb)

index = faiss.IndexHNSWFlat(DIM, M, faiss.METRIC_INNER_PRODUCT)
index.hnsw.efConstruction = 200
index.hnsw.efSearch = 64
index.add(xb)

q = xb[:1].copy()
D, I = index.search(q, 5)
```

教学数据太少看不出 recall 差异——**万级以上** 再与 Flat 对比。业务 id 映射见 [75 篇](75.faiss-ann-tutorial.md) IndexIDMap2。

---

## 9. 向量库配置

- **Milvus / Qdrant**：[77](77.milvus-tutorial.md)、[78](78.qdrant-tutorial.md) 创建索引时 `index_type: HNSW`。  
- **Chroma**：默认常内置 HNSW 相关 metadata（[76](76.chroma-vector-db-tutorial.md)）。  
- **pgvector**：`USING hnsw (m, ef_construction)`（[81](81.pgvector-tutorial.md)）。  
- **OpenSearch**：[83 混合](83.opensearch-hybrid-tutorial.md) 场景可向量+BM25。

---

## 10. recall 评测

```python
def recall_at_k(approx, exact, k):
    return len(set(approx[:k]) & set(exact[:k])) / k
```

1. 金标 query 50～200 条（[71 评测](71.domain-embedding-evaluation-tutorial.md)）；  
2. Flat 算 exact Top-10；  
3. HNSW 同 query 算 recall@10；  
4. 扫 efSearch 画曲线 → [87 篇](87.ann-recall-latency-tutorial.md)。

---

## 11. 综合概念地图

![概念地图](image/hnsw-index/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

''' + faq_block([
("HNSW 和六度分隔有什么关系？", "灵感来自小世界网络：少量长边加大量短边使平均路径变短。HNSW 是 **可导航** 变体，保证贪心 walk 不易卡死。工程上记住 **调 ef 换 recall** 即可，不必先啃证明。"),
("建索引要多久？", "与 N、dim、M、efConstruction、CPU 相关。百万 768 维 **分钟到小时** 都常见。索引文件要纳入 [90 备份](90.vector-db-backup-tutorial.md) 策略。"),
("删除向量后图会怎样？", "多为软删或 tombstone；大量删除后图质量下降，需 **compact 或全量重建**（[49 增量](49.incremental-update-tutorial.md)）。"),
("GPU 版值得吗？", "极大库、极高 QPS 时评估 faiss-gpu 或托管；PoC **CPU HNSW 足够**。"),
("与 DiskANN？", "内存放不下时考虑磁盘图索引；HNSW 仍是 **内存 ANN 入门默认**。"),
("多租户共享一个 HNSW？", "逻辑上每租户独立 collection（[89 篇](89.multi-tenant-namespace-tutorial.md)）；权限不靠图结构。"),
("efSearch 能动态调吗？", "可按查询类型分档：简单 FAQ ef 小，复杂分析 ef 大——要监控 recall 回归。"),
("换 Embedding 模型？", "**整库重建**——图在旧空间无意义（[25](25.embedding-vector-tutorial.md)）。"),
("HNSW 能跟 IVF 组合吗？", "FAISS 有组合索引；初学者 **先掌握单一 HNSW**。"),
("和 [80 Pinecone](80.pinecone-tutorial.md) 关系？", "托管服务底层也常是 HNSW 类图索引；你买的是 **SLA+运维**，原理仍本篇。"),
("RAG 里 HNSW 漏检会怎样？", "真相关 chunk 进不了 Top-k → prompt 缺证据 → 幻觉或拒答。要用 [87 权衡](87.ann-recall-latency-tutorial.md) 定 ef。"),
("M 设 4 可以吗？", "过小图稀疏，recall 易崩。除非极小库实验，**别低于常见默认**。"),
("同一库混中英 chunk？", "可以，但 Embedding 与分块策略要一致（[70 混合语言](70.mixed-language-embedding-tutorial.md)）；索引层无特殊。"),
("HNSW 查询线程安全吗？", "FAISS 读并发通常可行；写并发要查具体实现。生产 **读写分离或队列化建索**。"),
("如何向非技术解释 HNSW？", "「像地图：先高速公路到城区，再街道找门牌，比全城逐户敲门快，偶尔会漏一户。」"),
]) + r'''

---

## 13. 总结与系列下一步

1. **HNSW = 多层图 + 贪心导航**，百万向量 RAG 常见默认。  
2. **调 efSearch** 是线上最常用的 recall–延迟旋钮。  
3. **与 Flat golden 对照** 是工程伦理。  
4. 向量库 ([76](76.chroma-vector-db-tutorial.md)～[81](81.pgvector-tutorial.md)) 把 HNSW 包在配置里。

| 目标 | 阅读 |
|------|------|
| recall–latency | [87](87.ann-recall-latency-tutorial.md) |
| metadata 过滤 | [88](88.metadata-filter-retrieval-tutorial.md) |
| 混合检索 | [93](93.hybrid-search-tutorial.md) |

> **初学者困惑**  
> - HNSW **不是** 向量库名字，是 **索引算法**。  
> - ef 越大越慢是常态。  
> - 增量插入后要计划 **重建**。
''')

# Continue with 87-94 in next part - file too long, append via exec
print("Part 1 loaded: 86")
