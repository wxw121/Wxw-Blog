# Part 1: articles 86-88 - merged into articles_86_94_content.py

ARTICLE_86 = r'''# C4 向量存储（十二）：HNSW 图索引完全指南

> [84 Flat](84.flat-brute-force-search-tutorial.md) 把「每条都比一遍」讲透了，[85 IVF](85.ivf-index-tutorial.md) 用聚类把搜索缩到少数 **nprobe** 个桶里——但高维空间里「桶边界」仍可能切错邻居。**HNSW**（Hierarchical Navigable Small World，分层可导航小世界图）用 **多层图** 做近似最近邻：入库时连边建图，查询时从顶层 **贪心下山** 到近邻，在 **百万级向量** 上常能拿到 **亚毫秒～毫秒** 延迟与 **较高 recall**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **103** 条），讲清 HNSW **直觉、参数 M/efConstruction/efSearch、与 Flat/IVF 对照、FAISS/Qdrant/Milvus 常见配置**。前置：{preds}、[25 Embedding](25.embedding-vector-tutorial.md)、[26 相似度](26.similarity-metrics-tutorial.md)、[66 L2 归一化](66.l2-normalization-tutorial.md)。下一篇 [87 ANN 召回–延迟](87.ann-recall-latency-tutorial.md) 用评测曲线把参数旋钮量化。

---

## 目录

1. [前言：从 IVF 的「桶」到 HNSW 的「图」](#1-前言从-ivf-的桶到-hnsw-的图)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [HNSW 是什么](#3-hnsw-是什么)
4. [核心概念：层、边、贪心搜索](#4-核心概念层边贪心搜索)
5. [三大参数：M、efConstruction、efSearch](#5-三大参数mefconstructionefsearch)
6. [入库与查询在引擎里发生什么](#6-入库与查询在引擎里发生什么)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：FAISS IndexHNSWFlat](#8-实战代码faiss-indexhnswflat)
9. [与 Flat、IVF 选型对照](#9-与-flativf-选型对照)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：从 IVF 的「桶」到 HNSW 的「图」

你在 [85 篇](85.ivf-index-tutorial.md) 已经理解：**IVF** 先 k-means 聚类，查询只搜 **nprobe** 个簇中心最近的桶。好处是结构简单、内存可控；代价是 **簇边界** 附近的真邻居可能被分到隔壁簇，**recall 对 nprobe 很敏感**。

**HNSW** 换了一条路：把每个向量看成图上的 **节点**，按距离连 **边**，并叠 **多层**——上层边稀疏、跨度大，用于快速「跳到 query 附近」；下层边密、用于精细找 Top-k。查询像 **从高速公路下匝道到街道**：先在高层贪心，再逐层下沉。

通俗说：**IVF 像按邮编分柜；HNSW 像在城市路网里导航，层越高路越直、站越少**。

企业 RAG 里 HNSW 常见位置：

| 场景 | 为何选 HNSW |
|------|-------------|
| Qdrant / Milvus 默认 ANN | 单机百万 chunk、延迟稳定 |
| FAISS `IndexHNSWFlat` | 本地原型、与 IVF 对比实验 |
| Chroma 底层（部分版本） | 嵌入式库默认图索引 |
| 在线更新较多 | 支持增量 insert（实现因库而异） |

**读完本文，你应该能做到：**

1. 口述 HNSW **分层图 + 贪心搜索** 直觉，不背证明。  
2. 解释 **M、efConstruction、efSearch** 调大调小的方向（延迟、recall、内存）。  
3. 用 FAISS 跑通 **建索引 → search → recall 粗测**。  
4. 对照 [84 Flat](84.flat-brute-force-search-tutorial.md)、[85 IVF](85.ivf-index-tutorial.md) 写选型表。  
5. 识别 §7 四种翻车：ef 太小、M 过小、metric 不一致、把 HNSW 当精确检索。

### 1.1 C4 索引家族在路线图中的位置

```text
101 Flat（精确基线）
102 IVF（倒排文件 + 聚类）
103 HNSW（图索引）← 本篇
104 ANN recall–latency 评测
105 Metadata Filter …
```

**学习顺序**：先 Flat 懂 ground truth，再 IVF 懂「缩范围」，再 HNSW 懂「图导航」——否则调参只有玄学。

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 分层图 | Hierarchical Graph | 多层节点与边 |
| 入度上限 | M | 每节点最多连几条边 |
| 建图候选集 | efConstruction | 插入时考虑的邻居数 |
| 查询候选集 | efSearch / ef | 搜索时维护的候选池大小 |
| 可导航小世界 | NSW / NSW graph | 稀疏图仍能短路径到达 |

### 1.3 读完本篇的最小交付物

1. 一张 **query 从顶层下沉到底层** 的手绘示意图；  
2. 一份 **FAISS HNSW** 可运行脚本（§8）；  
3. 参数表：**M=16/32、efSearch=64/128** 各跑一次延迟；  
4. 与 IVF 的一句话对比（桶 vs 图）；  
5. 三条 §7 先错对对。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 103，概念 + 最小实战）。**

**本文讲：** HNSW 直觉、核心参数、FAISS 片段、与 Flat/IVF 对照、工程注意点。  
**本文不讲：** HNSW 论文完整证明、GPU 专用实现细节、乘积量化 PQ 与 HNSW 组合全书、分布式分片内部路由。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §3～§4，画三层图 | 白板 3 分钟讲清 |
| B | 读 §5，抄参数表到笔记 | 能答面试三参数 |
| C | 跑 §8 FAISS 脚本 | 打印 Top-5 与耗时 |
| D | 把 efSearch 从 16 调到 128 | 延迟与结果变化可感知 |
| E | 填 §9 选型表 | 团队 wiki 一段 |
| F | §7 先错对对 | 四种错法 |

**环境：** Python 3.10+；`pip install faiss-cpu numpy`。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| 向量与 metric | [25](25.embedding-vector-tutorial.md)、[26](26.similarity-metrics-tutorial.md) |
| L2 归一化与 IP | [66 L2 归一化](66.l2-normalization-tutorial.md) |
| Flat 基线 | [84 Flat](84.flat-brute-force-search-tutorial.md) |
| IVF 与 nprobe | [85 IVF](85.ivf-index-tutorial.md) |
| ANN 评测 | [87 召回–延迟](87.ann-recall-latency-tutorial.md)（下一篇） |

---

## 3. HNSW 是什么

![HNSW 图索引是什么](image/hnsw-index/01-hnsw-idea.png)

对照上图：

- **节点** = 一条 chunk 的 embedding；  
- **边** = 「这两个向量够近，可以互相指路」；  
- **多层** = 上层节点少、边长，下层节点全、边短；  
- **查询** = 从入口节点出发，每层找更近邻居，直到底层凑满 Top-k。

与 [84 Flat](84.flat-brute-force-search-tutorial.md) 比：**不再全库扫描**；与 [85 IVF](85.ivf-index-tutorial.md) 比：**不按固定簇分桶，而是图上的连续导航**。

### 3.1 为什么 RAG 工程爱 HNSW

| 需求 | HNSW 表现 |
|------|-----------|
| 百万级 chunk、P99 延迟 | 常见毫秒内（视维数、硬件） |
| recall 要明显高于低 nprobe IVF | efSearch 加大通常有效 |
| 向量库默认索引 | Qdrant、Milvus 文档默认推荐 |
| 教学与原型 | FAISS `IndexHNSWFlat` 几行代码 |

### 3.2 代价与边界

| 代价 | 说明 |
|------|------|
| 内存 | 存边比纯 Flat 多，M 越大越肥 |
| 建索引慢 | efConstruction 大时 insert 贵 |
| 非精确 | 必须做 recall 评测，见 [87 篇](87.ann-recall-latency-tutorial.md) |
| 极高维 + 极差分布 | 任何 ANN 都痛苦，先查 Embedding 质量 |

---

## 4. 核心概念：层、边、贪心搜索

### 4.1 分层结构直觉

设库里有 **N** 条向量。HNSW 随机给部分节点 **升级** 到更高层，层数约 **log N**。

- **第 0 层**：几乎所有节点，边最密，做 **精细搜索**；  
- **更高层**：节点子集，边连接 **长距离跳跃**，做 **粗定位**。

新节点插入时：从顶层入口开始，每层 **贪心** 找局部最近，再下沉到下一层重复，最后在底层连 **M** 条边（并可能修剪旧边）。

### 4.2 查询时的贪心下山

给定 query 向量 **q**：

1. 从 **顶层** 固定入口（或若干入口）开始；  
2. 在当前层沿边走向 **更接近 q** 的邻居，直到无法改进；  
3. **下沉** 到下一层，以当前点为起点重复；  
4. 在最底层维护大小为 **efSearch** 的 **候选优先队列**，扩展邻居直到收敛；  
5. 从候选集取 **Top-k** 返回。

通俗说：**每层只问「谁离我更近」，不回溯全图**——因此是 **近似**。

### 4.3 与 NSW 的关系

**NSW**（Navigable Small World）是单层图；**HNSW** 加 **分层** 解决单层图入口敏感、长链问题。面试时说「HNSW = 分层的可导航小世界图」即可。

---

## 5. 三大参数：M、efConstruction、efSearch

![HNSW 三大参数](image/hnsw-index/02-hnsw-params.png)

### 5.1 M（每节点最大边数）

- **调大**：连通性更好，**recall↑**，**内存↑**，建索引更慢。  
- **调小**：省内存，但容易 **断路网**， recall 掉。  
- **常见起点**：16 或 32（FAISS 默认常在此量级）。

### 5.2 efConstruction（建图宽度）

- 插入新点时，在候选池里选 **M** 个最佳邻居连边。  
- **调大**：图质量更好，**建索引慢**，查询 recall 通常更好。  
- **经验**：至少 **> M**，常见 **100～200** 做质量索引；快速试验可 **40～80**。

### 5.3 efSearch（查询宽度）

- 查询时底层候选池大小；必须 **≥ k**（你要的 Top-k）。  
- **调大**：**recall↑**，**延迟↑**。  
- **在线调参主力**：建索引一次，**efSearch 可查询时改**（FAISS 用 `index.hnsw.efSearch = ...`）。

| 参数 | 主要影响 | 查询时可改？ |
|------|----------|--------------|
| M | 内存、图结构 | 否（需重建） |
| efConstruction | 建索引时间、图质量 | 否 |
| efSearch | 延迟、recall | 是 |

---

## 6. 入库与查询在引擎里发生什么

### 6.1 入库流水线（概念）

```text
chunk 文本 → Embedding（[25 篇](25.embedding-vector-tutorial.md)）
→ float32 向量 → index.add
→ 对每个新向量：随机层数 → 每层贪心找近邻 → 连边 + 修剪
→ 持久化（依库：write_index / snapshot）
```

**chunk_id** 仍建议用外部映射或向量库主键（[51 chunk_id](51.metadata-chunk-id-tutorial.md)），HNSW 内部只有 **整数 id**。

### 6.2 查询流水线

```text
用户问题 → query Embedding → index.search(q, k)
→ 内部 HNSW 贪心 + 候选扩展 → 返回 (distances, ids)
→ 映射 chunk 文本 / metadata → 拼 RAG prompt
```

**metric** 必须与训练 Embedding 一致：L2 还是内积，是否 [66 归一化](66.l2-normalization-tutorial.md)——与 [84][85] 同一铁律。

---

## 7. 先错对对：四种典型翻车

### 7.1 错：efSearch = k = 5

**对：** efSearch 应 **明显大于 k**（如 k=10，efSearch=64）。候选池太窄会 **早停**，漏真邻居。

### 7.2 错：M=4 省内存

**对：** M 过小图太稀，recall 崩盘。先 **16/32**  baseline，再压测内存。

### 7.3 错：用 L2 索引搜未归一化向量，却以为在做 cosine

**对：** cosine 常见做法：**归一化 + IndexFlatIP / 对应 HNSW 配置**（[66 篇](66.l2-normalization-tutorial.md)）。

### 7.4 错：不做 recall 评测就上线

**对：** 用 [84 Flat](84.flat-brute-force-search-tutorial.md) 作 ground truth，算 recall@k（详见 [87 篇](87.ann-recall-latency-tutorial.md)）。

---

## 8. 实战代码：FAISS IndexHNSWFlat

```python
import time
import numpy as np
import faiss

dim = 64
n_base = 50_000
n_query = 200
k = 10

rng = np.random.default_rng(42)
xb = rng.standard_normal((n_base, dim)).astype("float32")
xq = rng.standard_normal((n_query, dim)).astype("float32")

# 余弦常见：L2 归一化 + 内积等价；此处演示用 FlatL2 型 HNSW
faiss.normalize_L2(xb)
faiss.normalize_L2(xq)

M = 32
index = faiss.IndexHNSWFlat(dim, M)
index.hnsw.efConstruction = 80
index.hnsw.efSearch = 64

t0 = time.perf_counter()
index.add(xb)
build_s = time.perf_counter() - t0

t1 = time.perf_counter()
D, I = index.search(xq, k)
search_ms = (time.perf_counter() - t1) / n_query * 1000

# 与 Flat 对照 recall@k
flat = faiss.IndexFlatL2(dim)
flat.add(xb)
_, I_true = flat.search(xq, k)
hits = np.mean([len(set(I[i]) & set(I_true[i])) / k for i in range(n_query)])

print(f"build={build_s:.2f}s  per_query={search_ms:.3f}ms  recall@{k}={hits:.3f}")
```

**实验建议：** 固定数据，只改 `efSearch` 为 16/64/128，画 **延迟–recall** 折线（交给 [87 篇](87.ann-recall-latency-tutorial.md) 模板）。

### 8.1 Qdrant 侧参数名对照

```python
# 创建 collection 时（示意）
# vectors_config=VectorParams(size=768, distance=Distance.COSINE)
# hnsw_config=HnswConfigDiff(m=16, ef_construct=100)
# 查询时 search_params=SearchParams(hnsw_ef=128)
```

具体 API 以 [78 Qdrant](78.qdrant-tutorial.md) 文档为准；**语义与本文三参数一一对应**。

---

## 9. 与 Flat、IVF 选型对照

| 维度 | Flat [84] | IVF [85] | HNSW 本篇 |
|------|-----------|----------|-----------|
| 精确性 | 精确 | 近似 | 近似 |
| 内存 | 向量矩阵 | 向量 + 簇中心 | 向量 + 边 |
| 查询延迟（百万级） | 高 | 中（看 nprobe） | 低～中 |
| 调参旋钮 | 无 | nlist, nprobe | M, efConstruction, efSearch |
| 适合 | 评测基线、小库 | 超大库、可接受训练 k-means | 默认在线 ANN、中高 recall |

**RAG PoC：** 万级 chunk 三种都能跑；**十万级以上** 多数团队 **HNSW 或 IVF**，Flat 只当 **评测真值**。

---

## 10. 综合概念地图

![HNSW 概念地图](image/hnsw-index/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

### 11.1 HNSW 和 IVF 能一起用吗？

可以。FAISS 有 **IVF + HNSW 量化** 等组合索引：IVF 先选桶，桶内 HNSW。超大库常见；调参复杂度 **↑↑**，建议有 SRE 再玩。

### 11.2 删除与更新怎么办？

纯 HNSW **硬删** 可能留空洞；生产用 **标记删除 + 定期重建**，或向量库提供的 **tombstone / compaction**（[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)）。

### 11.3 维度 1536 要特殊 M 吗？

没有万能表；**用评测集扫 efSearch**。维数高时 **更依赖 Embedding 质量** 与 **归一化**。

### 11.4 Chroma 底层是 HNSW 吗？

部分部署默认 **HNSW + cosine**；以你版本 metadata `hnsw:*` 为准（[76 Chroma](76.chroma-vector-db-tutorial.md)）。

### 11.5 图索引为何怕「分布极偏」？

若 Embedding 把无关文本都挤成一团，任何 ANN 都在 **一团迷雾** 里导航——先修 **分块与模型**（C2/C3），再怪索引。

### 11.6 efConstruction 和 efSearch 能设一样吗？

可以但 **角色不同**：建图宽、查询窄常浪费建索引成本；建图窄、查询宽 recall 可能永远上不去。

### 11.7 多租户要每个租户一张图吗？

见 [89 多租户](89.multi-tenant-namespace-tutorial.md)：逻辑隔离用 **collection / namespace**，物理上可共享或分片。

### 11.8 备份要存 HNSW 图吗？

要。图与向量一起备份，见 [90 备份](90.vector-db-backup-tutorial.md)。

### 11.9 Metadata 过滤和 HNSW 谁先谁后？

见 [88 Metadata Filter](88.metadata-filter-retrieval-tutorial.md)：**前滤** 缩小子集再 ANN，或 **后滤** 扩 k 再筛——各有坑。

### 11.10 面试 30 秒版

「HNSW 用分层图做 ANN：M 控每点边数，efConstruction 控建图质量，efSearch 控查询 recall 与延迟。查询从顶层贪心下沉到底层取 Top-k。RAG 里常作默认 ANN，但必须用 Flat 算 recall@k。」

### 11.11 与混合检索的关系

HNSW 只管 **稠密路**；关键词还要 [92 稀疏](92.sparse-retrieval-rag-tutorial.md)、[93 混合](93.hybrid-search-tutorial.md)、[94 RRF](94.rrf-fusion-tutorial.md)。

### 11.12 故障排查速查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| recall 低 | efSearch 太小 | 加大 efSearch |
| 建索引极慢 | efConstruction 过大 | 略降或分批 build |
| 内存爆 | M 太大 + 维数高 | 降 M 或 PQ（进阶） |
| 结果随机飘 | 未固定随机种子 / 并发写 | 重建、加锁 |
| 与 Flat Top-k 差很多 | metric 错 | 查归一化与 IP/L2 |

### 11.13 给产品经理的一句话

「HNSW 像智能导航：不扫全库，沿『相似度路网』找最近资料；调 efSearch 像调『搜索仔细程度』，越仔细越慢但越不容易漏。」

### 11.14 一周学习计划

| 天 | 任务 |
|----|------|
| Mon | [84 Flat](84.flat-brute-force-search-tutorial.md) + 本篇 §3～§5 |
| Tue | 跑 §8，记延迟 |
| Wed | 扫 efSearch，画曲线（接 [87](87.ann-recall-latency-tutorial.md)） |
| Thu | 读 [78 Qdrant](78.qdrant-tutorial.md) HNSW 配置 |
| Fri | 团队分享：桶 vs 图 |

### 11.15 延伸阅读

- 论文：Malkov & Yashunin, *Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs*  
- FAISS wiki：HNSW 索引类说明  
- [87 ANN 召回–延迟](87.ann-recall-latency-tutorial.md)

---

## 12. 总结与系列下一步

1. **HNSW** = 分层图 + 贪心近似最近邻；企业 RAG **默认 ANN** 之一。  
2. **M / efConstruction / efSearch** 分别管 **内存与连通、建图质量、查询 recall–延迟**。  
3. **必须用 Flat 评测 recall**，参数不是越大越好。  
4. 与 **IVF** 互补：超大库可 IVF+HNSW 或分片多图。  
5. 检索只是 C4 一环；**过滤、多租户、混合** 见 88～94。

### 12.1 系列下一步

| 目标 | 阅读 |
|------|------|
| 量化 recall–延迟 | [87 ANN 召回–延迟](87.ann-recall-latency-tutorial.md) |
| 元数据过滤 | [88 Metadata Filter](88.metadata-filter-retrieval-tutorial.md) |
| 向量库选型 | [77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md) |
| 混合检索 | [93 Hybrid](93.hybrid-search-tutorial.md) |

### 12.2 学习目标自检

- [ ] 能画三层 HNSW 示意图  
- [ ] 能解释三参数  
- [ ] 能跑 §8 并对照 Flat recall  
- [ ] 能写 Flat/IVF/HNSW 选型表  

### 12.3 30 分钟作业

1. 把 §8 的 `n_base` 改为 10_000，efSearch 取 16 与 128 各跑一次；  
2. 用一句话向同事解释 **为何 efSearch 要大于 k**；  
3. 在 [ENTERPRISE_RAG_ROADMAP](ENTERPRISE_RAG_ROADMAP.md) 勾选 103。

---

> **初学者可能仍困惑的点**  
> - HNSW **不是** 比 Flat「更聪明」——是 **允许漏检换速度**。  
> - **efSearch 不是越大越好**——要在 [87 篇](87.ann-recall-latency-tutorial.md) 找拐点。  
> - **换 Embedding 必须重建图**，不能原地换向量维数。  
> - 图索引 **不解决** 关键词精确匹配——报销单号还要靠 [92 稀疏](92.sparse-retrieval-rag-tutorial.md)。
'''
