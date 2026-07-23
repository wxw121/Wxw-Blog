# -*- coding: utf-8 -*-
"""Article bodies 87-94 for _gen_batch_85_94.py"""

ARTICLE_87 = """# C4 向量存储（十三）：ANN 召回率与延迟权衡完全指南

> [84 Flat](84.flat-brute-force-search-tutorial.md) 给你 **100% 近邻金标准**；[85 IVF](85.ivf-index-tutorial.md) 用 **nprobe**、[86 HNSW](86.hnsw-index-tutorial.md) 用 **efSearch** 换速度——但「调大一点」到底是 **多快、多准**？**ANN recall–latency 评测** 用 **同一批 query、同一 metric、Flat 当真值**，扫参数画 **recall@k–P95 延迟** 折线，在 **拐点** 定 SLA。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 主线篇**（路线图第 **104** 条）。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、[79 Weaviate](79.weaviate-tutorial.md)、[80 Pinecone](80.pinecone-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md)、[82 Elasticsearch 向量](82.elasticsearch-vector-tutorial.md)、[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)、[84 Flat](84.flat-brute-force-search-tutorial.md)、[85 IVF](85.ivf-index-tutorial.md)、[86 HNSW](86.hnsw-index-tutorial.md)。下一篇 [88 Metadata Filter](88.metadata-filter-retrieval-tutorial.md) 在 **过滤子集** 上也要单独扫曲线。

---

## 目录

1. [前言：没有曲线就没有 SLA](#1-前言没有曲线就没有-sla)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Recall 与延迟分别量什么](#3-recall-与延迟分别量什么)
4. [金标准：为何必须是 Flat](#4-金标准为何必须是-flat)
5. [评测流水线五步法](#5-评测流水线五步法)
6. [画 recall–latency 曲线](#6-画-recalllatency-曲线)
7. [IVF / HNSW 旋钮对照](#7-ivf--hnsw-旋钮对照)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：ANN 扫参 Mini-RAG 评测台](#9-综合实战ann-扫参-mini-rag-评测台)
10. [生产 SLO 与回归策略](#10-生产-slo-与回归策略)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：没有曲线就没有 SLA

上线前同事问：「HNSW 的 efSearch 设 64 够不够？」——若你只能答「感觉够」，P99 延迟超标或用户抱怨「搜不到」时 **无法归因**。

**Recall@k**：ANN 返回的 Top-k 与 Flat 精确 Top-k 的 **交集比例**。**Latency**：单次 search 的 **P50/P95/P99** 毫秒。

通俗说：**Recall 回答漏没漏真邻居；延迟回答等多久**——ANN 就是在两者之间 **找拐点**。

**读完本文，你应该能做到：** 定义 recall@k；用 Flat 作金标；扫 nprobe/efSearch 出曲线；标拐点写 SLO；识别五种翻车。



### 1.1 路线图位置

```text
103 HNSW [86] → 104 ANN 评测 ← 本篇 → 105 Filter [88]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 召回率 | Recall@k | ANN 与 Flat Top-k 重叠比 |
| 延迟分位 | P95 | 95% 查询耗时上限 |
| 金标准 | Ground truth | Flat 精确 Top-k |
| 拐点 | Knee point | 性价比最优区 |

### 1.3 读完本篇的最小交付物

1. recall–latency CSV ≥5 行；2. 推荐参数；3. SLO 段落；4. §8 五种翻车；5. §9 评测台可跑。

---

## 2. 本文边界与动手路径

**档位：C4 主线篇（路线图 104）。** 讲 recall、Flat 金标、扫参、SLO；不讲 RAGAS 全书、GPU 微基准全书。

| 步骤 | 验收 |
|------|------|
| 读 §3～§4 | 能写 recall 公式 |
| 跑 §9 | 有 CSV |
| 画曲线 | 有推荐 ef/nprobe |



### 2.2 沿用前文

| Flat | [84](84.flat-brute-force-search-tutorial.md) |
| IVF nprobe | [85](85.ivf-index-tutorial.md) |
| HNSW efSearch | [86](86.hnsw-index-tutorial.md) |

---

## 3. Recall 与延迟分别量什么

读下图：横轴延迟、纵轴 recall 的帕累托前沿。

![召回率与延迟权衡](image/ann-recall-latency/01-recall-latency.png)

对 query 集 Q：`recall_q = |T_ann ∩ T_flat| / k`，再取平均。**k 要与 RAG 管道一致**——ANN 取 k=50 再 rerank 时应用 k=50 评测。

延迟用 `time.perf_counter()` 单条 search，报告 P50/P95。warm-up 后、固定硬件才有可比性。



---

## 4. 金标准：为何必须是 Flat

[84 篇](84.flat-brute-force-search-tutorial.md)：Flat 与 ANN **同向量、同 metric、同归一化**（[66 L2](66.l2-normalization-tutorial.md)）。人工标注测业务相关；Flat 测 **向量近邻一致性**——调索引参数用后者。

## 5. 评测流水线五步法

1. 固定库向量与 ≥50 条 query；2. 建 Flat + ANN 双索引；3. 扫 nprobe 或 efSearch 网格；4. 记 CSV：`param, recall, p50, p95`；5. 选拐点 **留余量**。

## 6. 画 recall–latency 曲线

![ANN 评测曲线怎么读](image/ann-recall-latency/02-benchmark-curve.png)

**拐点**：recall 增益 <2% 而 P95 涨 >20% → 选拐点前一点。同一图可叠 **IVF 与 HNSW** 两条线。

## 7. IVF / HNSW 旋钮对照

| 索引 | 旋钮 | recall↑ | 延迟↑ |
|------|------|---------|-------|
| IVF [85] | nprobe | 增大 | 增大 |
| HNSW [86] | efSearch | 增大 | 增大 |

[88 过滤](88.metadata-filter-retrieval-tutorial.md) 后有效 N 变小，**全库最优参数不一定适用**——要重扫。

## 10. 生产 SLO 与回归

示例：recall@50≥0.95，P95≤80ms。触发重扫：换 Embedding、N 翻倍、投诉漏检。metrics：`ann_recall_sample`、`ann_p95_ms`。

---

## 8. 先错对对：五种典型翻车

### 1. 错：没有 Flat 看 ANN 分数就上线

**对：** 必须 [84 Flat](84.flat-brute-force-search-tutorial.md) 算 recall@k

分数高不等于 Top-k 集合对。

### 2. 错：只用 3 条 demo query 调参

**对：** ≥50 条覆盖长短问与专有名词

否则过拟合 demo。

### 3. 错：query 归一化、库没归一化

**对：** 全链路统一 [66 归一化](66.l2-normalization-tutorial.md)

metric 不一致 recall 无意义。

### 4. 错：只报 mean recall 不看 P99

**对：** SLA 写 P95/P99

均值会被少数快 query 美化。

### 5. 错：数据涨十倍仍用旧 nprobe

**对：** 季度回归扫参

每桶变大 recall 可能降。



---

## 9. 综合实战：ANN 扫参 Mini-RAG 评测台

### 9.1 验收

| 项 | 标准 |
|----|------|
| 双索引 | Flat + HNSW |
| 扫参 | ≥6 个 efSearch |
| 输出 | benchmark.csv + 推荐值 |

### 9.2 脚本核心

```python
import csv, time, numpy as np, faiss
DIM, K = 768, 50
EF_GRID = [16, 32, 64, 128, 192, 256]
faiss.normalize_L2(db); faiss.normalize_L2(queries)
flat = faiss.IndexFlatIP(DIM); flat.add(db)
index = faiss.IndexHNSWFlat(DIM, 32)
index.hnsw.efConstruction = 100; index.add(db)
def recall_at_k(ann, qmat, k):
    hits = []
    for i in range(len(qmat)):
        _, a = ann.search(qmat[i:i+1], k)
        _, f = flat.search(qmat[i:i+1], k)
        hits.append(len(set(a[0]) & set(f[0])) / k)
    return float(np.mean(hits))
rows = []
for ef in EF_GRID:
    index.hnsw.efSearch = max(ef, K)
    lats = []
    for i in range(len(queries)):
        t0 = time.perf_counter()
        index.search(queries[i:i+1], K)
        lats.append((time.perf_counter()-t0)*1000)
    rec = recall_at_k(index, queries, K)
    p95 = sorted(lats)[int(len(lats)*0.95)]
    rows.append({"efSearch": ef, "recall": rec, "p95_ms": p95})
with open("benchmark.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["efSearch","recall","p95_ms"])
    w.writeheader(); w.writerows(rows)
```

### 9.3 CHUNKS 与 QUERIES

用 [25 Embedding](25.embedding-vector-tutorial.md) 同一模型 embed 数千条手册句；QUERIES ≥50 条脱敏真实问法。

### 9.4 与 RAG 拼接

`embed → ANN(k=50) → [95 rerank] → LLM`。评测台只管 ANN 数字。

### 9.5 Review 清单

- [ ] CSV 进 PR；写明 CPU、N、dim、model
- [ ] 配置中心 `ann.ef_search` 与代码一致
- [ ] 发版 job 跑回归集

---

## 综合概念地图

![ANN 召回延迟概念地图](image/ann-recall-latency/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| recall@k | 与 Flat 重叠比 |
| 拐点 | SLA 参数区 |
| 下一篇 | [88 过滤](88.metadata-filter-retrieval-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：recall@10 和 recall@50 差很多正常吗？**
A：正常；按线上 k 测。

**Q：能否两 ANN 互相比代替 Flat？**
A：不能；无绝对真值。

**Q：GPU 索引怎么评测？**
A：流程相同，注明 GPU 型号。

**Q：并发 100 QPS 还要单线程基准吗？**
A：要；单线程隔离算法，并发是容量规划。

**Q：Milvus search_params 怎么对齐？**
A：见 [77 篇](77.milvus-tutorial.md)；ef/nprobe 同名。

**Q：Chroma 默认 ef 从哪改？**
A：见 [76 篇](76.chroma-vector-db-tutorial.md)，仍要 recall 验证。

**Q：过滤后 recall 变高还要重扫吗？**
A：前滤改变候选空间，租户级宜单独曲线。

**Q：面试 30 秒版？**
A：Flat 算 recall@k，扫 nprobe/efSearch，画 recall–P95 曲线，拐点定生产参数。

**Q：和 RAGAS 冲突吗？**
A：不冲突；本篇索引层，RAGAS 答案层。

**Q：数据只有 2000 条要扫吗？**
A：要；或直接用 Flat，扫参证明 ANN 可接受。



---

## 总结与系列下一步

1. ANN 调参靠曲线；2. Flat 是金标准；3. k、query 数、分位数写进报告；4. 拐点写配置；5. 下一篇 [88 过滤](88.metadata-filter-retrieval-tutorial.md)。

### 系列下一步

| Flat | [84](84.flat-brute-force-search-tutorial.md) |
| HNSW | [86](86.hnsw-index-tutorial.md) |
| 过滤 | [88](88.metadata-filter-retrieval-tutorial.md) |

### 30 分钟作业

1. 跑 §9 存 CSV；2. 写 SLO；3. 口述 §8；4. 勾选路线图 104。

---

> **初学者可能仍困惑的点**
> - Recall 高不等于答案对，但 Recall 低 rerank 救不了。
> - 换 Embedding 必须重建索引并重扫曲线。


## 附录 A：Milvus / Qdrant 扫参对照

**Milvus** [77 篇](77.milvus-tutorial.md)：`search_params={"params": {"ef": 128}}` 或 IVF `nprobe`。导出 CSV 时列名写 `ef` 而非 `efSearch`，避免与 Faiss 混淆。

**Qdrant** [78 篇](78.qdrant-tutorial.md)：`SearchParams(hnsw_ef=128)`。collection 级 `ef_construct` 影响建图，查询扫 `hnsw_ef` 即可画曲线。

**pgvector** [81 篇](81.pgvector-tutorial.md)：`SET ivfflat.probes = 10` 会话变量；benchmark 时固定连接池与 `work_mem`，否则 P95 抖动大。

## 附录 B：回归集 JSON 样例

```json
[
  {"query_id": "q001", "text": "出差住宿标准", "expect_chunk_ids": ["hb:c002"]},
  {"query_id": "q002", "text": "年假几天", "expect_chunk_ids": ["hb:c001"]}
]
```

发版 job：对每条 query 跑 ANN，算 **Hit@50**（金标 chunk 是否在 Top-50）与 **recall@50 vs Flat** 双指标。

## 附录 C：压测与单线程基准分工

| 基准类型 | 目的 | 并发 |
|----------|------|------|
| 单线程延迟 | 选 efSearch/nprobe | 1 |
| 固定 QPS 压测 | 容量规划 | 50～200 |
| 回归 recall | 防回退 | 1，固定种子 |

不要把压测 P95 当作 §9 单线程表的同一列——wiki 应 **分两表** 张贴。


## 专精：FAISS 扫参完整脚本说明

§9 脚本中 `EF_GRID` 建议覆盖 **efSearch 从略大于 k 到 4×k** 区间。若 recall@50 在 ef=128 已达 0.96，ef=256 仅升到 0.97 而 P95 从 40ms 到 85ms，**拐点在 128**。把该值写入 `manifest.json`（[90 备份](90.vector-db-backup-tutorial.md)）与配置中心。

**IVF 分支**：复制同一脚本，把 `index` 换成 `IndexIVFFlat`，扫 `nprobe`。对比时 **N、query 集、metric 必须相同**。常见现象：IVF 在同等 P95 下 recall 略低，但内存更省——选型不是「谁 recall 高」 alone，要叠 **内存、建索引时间、运维复杂度**。

**filtered 子集**：从 id_map 筛 `doc_id=handbook` 的子向量建 **子索引** 对比全库参数。前滤后每桶向量变少，**同样 efSearch recall 常更高**——但后滤场景仍可能 filter_miss（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

**回归 job 伪代码**：

```python
def nightly_ann_regression(index, queries, flat, k=50, threshold=0.95):
    rec = recall_at_k(index, queries, k)
    if rec < threshold:
        alert(f"ANN recall dropped to {rec:.3f}")
    return rec
```

cron 每日跑；发版后手动触发一次。与业务金标 Hit@50 **分开看**——索引 recall 掉 2% 可能用户无感，但连续下降要查 **数据漂移或参数被改**。



## 专精：延迟测量陷阱清单

| 陷阱 | 后果 | 规避 |
|------|------|------|
| 冷启动首轮计入 | P95 虚高 | warm-up 50 次丢弃 |
| search 批大小混用 | 不可比 | 固定 batch=1 报 SLA |
| 并发改 efSearch | 竞态 | 每线程独立 index 或加锁 |
| 未固定 CPU 亲和 | 抖动 | 基准机独占 |
| 把 build 时间算进 query | 误导 | build 单独列 |

**QPS 压测**：单线程表定 **算法参数**；线程池 32 定 **容量**。wiki 两表并列，避免用压测 P95 否定单线程拐点选型。

**跨机房**：副本读延迟含网络；ANN SLA 应 **分地域** 写。主库写、从库读时，注意 **复制滞后** 导致新 chunk 搜不到——属 [49 增量](49.incremental-update-tutorial.md) 一致性问题，不是 ANN 参数问题。



## 专精：与 RAG 管道参数联动

| 管道参数 | 与 ANN 关系 |
|----------|-------------|
| recall_k=50 | 评测用 k=50 |
| rerank 输入 50 | ANN 漏检 rerank 无法补救 |
| [98 Top-K](98.top-k-retrieval-tutorial.md) | final_k=5 与 ANN k 解耦 |
| [28 Context](28.context-window-tutorial.md) | 与 ANN 无关但同 wiki |

**端到端实验**：固定 ANN 参数，只改 rerank——若答案质量仍差，查 chunk 或 prompt；固定 rerank，扫 efSearch——若 Hit@50 升而答案仍差，查 **精排或生成**。分层归因避免「一味加大 ef」。

**面试追问**：「recall@10=0.99 够吗？」——若 rerank 从 50 里挑 5，要看 **金标相关 chunk 在不在 Top-50**，不是 Top-10。答：用业务 k 评测，常用 50。



## 专精：文档模板与团队分工

**评测报告负责人**：检索工程师；**签字**：产品（SLA）、SRE（容量）。报告必含：数据快照 hash、query 集版本、参数网格、推荐值、已知限制（如仅 CPU 测）。

**新人 onboarding**：第一周跑通 §9；第二周用 [84 Flat](84.flat-brute-force-search-tutorial.md) 解释差集；第三周对接 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 子集曲线。

**与 [86 HNSW](86.hnsw-index-tutorial.md) 参数对照表**：

| Faiss | Milvus | Qdrant |
|-------|--------|--------|
| efSearch | ef | hnsw_ef |
| efConstruction | efConstruction | ef_construct |
| M | M | m |

写配置时 **列名映射** 进 manifest，避免恢复后抄错列。



## 专精：差集分析与 bad chunk 归类

当 recall@50=0.88 不达标时，导出 **漏检 query**：

```python
def diff_queries(ann, flat, queries, k=50):
    bad = []
    for i, q in enumerate(queries):
        _, a = ann.search(q.reshape(1,-1), k)
        _, f = flat.search(q.reshape(1,-1), k)
        miss = set(f[0]) - set(a[0])
        if miss:
            bad.append((i, miss))
    return bad
```

对 miss 的 flat 邻居做 **归类**：簇边界（IVF）、图早停（HNSW）、边界向量（正常）。IVF 漏检多 → 增 nprobe；HNSW 多 → 增 efSearch；单条 query 极端 → 可能 embed 差或 query 需 [100 改写](100.query-rewriting-tutorial.md)。

**记录进 wiki**：差集样例脱敏后存档，下版 Embedding 升级时 **重跑对比**。



## 专精：GPU 与量化索引备注

`faiss-gpu` 扫参流程同 CPU，但 **P95 单位不同**，不可与 CPU 表合并。`IndexHNSWPQ` 等量化索引 recall 常低于 HNSWFlat——若上 PQ，**单独一条曲线** 与 Flat 金标对比，不要沿用 HNSWFlat 的 efSearch 推荐值。

**企业建议**：PoC 用 `IndexHNSWFlat` 建立 baseline；内存告急再 PQ，并接受 **独立回归**。


## 附录 A：Milvus / Qdrant 扫参对照

**Milvus** [77 篇](77.milvus-tutorial.md)：`search_params={"params": {"ef": 128}}` 或 IVF `nprobe`。导出 CSV 时列名写 `ef` 而非 `efSearch`，避免与 Faiss 混淆。

**Qdrant** [78 篇](78.qdrant-tutorial.md)：`SearchParams(hnsw_ef=128)`。collection 级 `ef_construct` 影响建图，查询扫 `hnsw_ef` 即可画曲线。

**pgvector** [81 篇](81.pgvector-tutorial.md)：`SET ivfflat.probes = 10` 会话变量；benchmark 时固定连接池与 `work_mem`，否则 P95 抖动大。

## 附录 B：回归集 JSON 样例

```json
[
  {"query_id": "q001", "text": "出差住宿标准", "expect_chunk_ids": ["hb:c002"]},
  {"query_id": "q002", "text": "年假几天", "expect_chunk_ids": ["hb:c001"]}
]
```

发版 job：对每条 query 跑 ANN，算 **Hit@50**（金标 chunk 是否在 Top-50）与 **recall@50 vs Flat** 双指标。

## 附录 C：压测与单线程基准分工

| 基准类型 | 目的 | 并发 |
|----------|------|------|
| 单线程延迟 | 选 efSearch/nprobe | 1 |
| 固定 QPS 压测 | 容量规划 | 50～200 |
| 回归 recall | 防回退 | 1，固定种子 |

不要把压测 P95 当作 §9 单线程表的同一列——wiki 应 **分两表** 张贴。


## 专精：FAISS 扫参完整脚本说明

§9 脚本中 `EF_GRID` 建议覆盖 **efSearch 从略大于 k 到 4×k** 区间。若 recall@50 在 ef=128 已达 0.96，ef=256 仅升到 0.97 而 P95 从 40ms 到 85ms，**拐点在 128**。把该值写入 `manifest.json`（[90 备份](90.vector-db-backup-tutorial.md)）与配置中心。

**IVF 分支**：复制同一脚本，把 `index` 换成 `IndexIVFFlat`，扫 `nprobe`。对比时 **N、query 集、metric 必须相同**。常见现象：IVF 在同等 P95 下 recall 略低，但内存更省——选型不是「谁 recall 高」 alone，要叠 **内存、建索引时间、运维复杂度**。

**filtered 子集**：从 id_map 筛 `doc_id=handbook` 的子向量建 **子索引** 对比全库参数。前滤后每桶向量变少，**同样 efSearch recall 常更高**——但后滤场景仍可能 filter_miss（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

**回归 job 伪代码**：

```python
def nightly_ann_regression(index, queries, flat, k=50, threshold=0.95):
    rec = recall_at_k(index, queries, k)
    if rec < threshold:
        alert(f"ANN recall dropped to {rec:.3f}")
    return rec
```

cron 每日跑；发版后手动触发一次。与业务金标 Hit@50 **分开看**——索引 recall 掉 2% 可能用户无感，但连续下降要查 **数据漂移或参数被改**。



## 专精：延迟测量陷阱清单

| 陷阱 | 后果 | 规避 |
|------|------|------|
| 冷启动首轮计入 | P95 虚高 | warm-up 50 次丢弃 |
| search 批大小混用 | 不可比 | 固定 batch=1 报 SLA |
| 并发改 efSearch | 竞态 | 每线程独立 index 或加锁 |
| 未固定 CPU 亲和 | 抖动 | 基准机独占 |
| 把 build 时间算进 query | 误导 | build 单独列 |

**QPS 压测**：单线程表定 **算法参数**；线程池 32 定 **容量**。wiki 两表并列，避免用压测 P95 否定单线程拐点选型。

**跨机房**：副本读延迟含网络；ANN SLA 应 **分地域** 写。主库写、从库读时，注意 **复制滞后** 导致新 chunk 搜不到——属 [49 增量](49.incremental-update-tutorial.md) 一致性问题，不是 ANN 参数问题。



## 专精：与 RAG 管道参数联动

| 管道参数 | 与 ANN 关系 |
|----------|-------------|
| recall_k=50 | 评测用 k=50 |
| rerank 输入 50 | ANN 漏检 rerank 无法补救 |
| [98 Top-K](98.top-k-retrieval-tutorial.md) | final_k=5 与 ANN k 解耦 |
| [28 Context](28.context-window-tutorial.md) | 与 ANN 无关但同 wiki |

**端到端实验**：固定 ANN 参数，只改 rerank——若答案质量仍差，查 chunk 或 prompt；固定 rerank，扫 efSearch——若 Hit@50 升而答案仍差，查 **精排或生成**。分层归因避免「一味加大 ef」。

**面试追问**：「recall@10=0.99 够吗？」——若 rerank 从 50 里挑 5，要看 **金标相关 chunk 在不在 Top-50**，不是 Top-10。答：用业务 k 评测，常用 50。



## 专精：文档模板与团队分工

**评测报告负责人**：检索工程师；**签字**：产品（SLA）、SRE（容量）。报告必含：数据快照 hash、query 集版本、参数网格、推荐值、已知限制（如仅 CPU 测）。

**新人 onboarding**：第一周跑通 §9；第二周用 [84 Flat](84.flat-brute-force-search-tutorial.md) 解释差集；第三周对接 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 子集曲线。

**与 [86 HNSW](86.hnsw-index-tutorial.md) 参数对照表**：

| Faiss | Milvus | Qdrant |
|-------|--------|--------|
| efSearch | ef | hnsw_ef |
| efConstruction | efConstruction | ef_construct |
| M | M | m |

写配置时 **列名映射** 进 manifest，避免恢复后抄错列。



## 专精：差集分析与 bad chunk 归类

当 recall@50=0.88 不达标时，导出 **漏检 query**：

```python
def diff_queries(ann, flat, queries, k=50):
    bad = []
    for i, q in enumerate(queries):
        _, a = ann.search(q.reshape(1,-1), k)
        _, f = flat.search(q.reshape(1,-1), k)
        miss = set(f[0]) - set(a[0])
        if miss:
            bad.append((i, miss))
    return bad
```

对 miss 的 flat 邻居做 **归类**：簇边界（IVF）、图早停（HNSW）、边界向量（正常）。IVF 漏检多 → 增 nprobe；HNSW 多 → 增 efSearch；单条 query 极端 → 可能 embed 差或 query 需 [100 改写](100.query-rewriting-tutorial.md)。

**记录进 wiki**：差集样例脱敏后存档，下版 Embedding 升级时 **重跑对比**。



## 专精：GPU 与量化索引备注

`faiss-gpu` 扫参流程同 CPU，但 **P95 单位不同**，不可与 CPU 表合并。`IndexHNSWPQ` 等量化索引 recall 常低于 HNSWFlat——若上 PQ，**单独一条曲线** 与 Flat 金标对比，不要沿用 HNSWFlat 的 efSearch 推荐值。

**企业建议**：PoC 用 `IndexHNSWFlat` 建立 baseline；内存告急再 PQ，并接受 **独立回归**。


## 附录 A：Milvus / Qdrant 扫参对照

**Milvus** [77 篇](77.milvus-tutorial.md)：`search_params={"params": {"ef": 128}}` 或 IVF `nprobe`。导出 CSV 时列名写 `ef` 而非 `efSearch`，避免与 Faiss 混淆。

**Qdrant** [78 篇](78.qdrant-tutorial.md)：`SearchParams(hnsw_ef=128)`。collection 级 `ef_construct` 影响建图，查询扫 `hnsw_ef` 即可画曲线。

**pgvector** [81 篇](81.pgvector-tutorial.md)：`SET ivfflat.probes = 10` 会话变量；benchmark 时固定连接池与 `work_mem`，否则 P95 抖动大。

## 附录 B：回归集 JSON 样例

```json
[
  {"query_id": "q001", "text": "出差住宿标准", "expect_chunk_ids": ["hb:c002"]},
  {"query_id": "q002", "text": "年假几天", "expect_chunk_ids": ["hb:c001"]}
]
```

发版 job：对每条 query 跑 ANN，算 **Hit@50**（金标 chunk 是否在 Top-50）与 **recall@50 vs Flat** 双指标。

## 附录 C：压测与单线程基准分工

| 基准类型 | 目的 | 并发 |
|----------|------|------|
| 单线程延迟 | 选 efSearch/nprobe | 1 |
| 固定 QPS 压测 | 容量规划 | 50～200 |
| 回归 recall | 防回退 | 1，固定种子 |

不要把压测 P95 当作 §9 单线程表的同一列——wiki 应 **分两表** 张贴。


## 专精：FAISS 扫参完整脚本说明

§9 脚本中 `EF_GRID` 建议覆盖 **efSearch 从略大于 k 到 4×k** 区间。若 recall@50 在 ef=128 已达 0.96，ef=256 仅升到 0.97 而 P95 从 40ms 到 85ms，**拐点在 128**。把该值写入 `manifest.json`（[90 备份](90.vector-db-backup-tutorial.md)）与配置中心。

**IVF 分支**：复制同一脚本，把 `index` 换成 `IndexIVFFlat`，扫 `nprobe`。对比时 **N、query 集、metric 必须相同**。常见现象：IVF 在同等 P95 下 recall 略低，但内存更省——选型不是「谁 recall 高」 alone，要叠 **内存、建索引时间、运维复杂度**。

**filtered 子集**：从 id_map 筛 `doc_id=handbook` 的子向量建 **子索引** 对比全库参数。前滤后每桶向量变少，**同样 efSearch recall 常更高**——但后滤场景仍可能 filter_miss（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

**回归 job 伪代码**：

```python
def nightly_ann_regression(index, queries, flat, k=50, threshold=0.95):
    rec = recall_at_k(index, queries, k)
    if rec < threshold:
        alert(f"ANN recall dropped to {rec:.3f}")
    return rec
```

cron 每日跑；发版后手动触发一次。与业务金标 Hit@50 **分开看**——索引 recall 掉 2% 可能用户无感，但连续下降要查 **数据漂移或参数被改**。



## 专精：延迟测量陷阱清单

| 陷阱 | 后果 | 规避 |
|------|------|------|
| 冷启动首轮计入 | P95 虚高 | warm-up 50 次丢弃 |
| search 批大小混用 | 不可比 | 固定 batch=1 报 SLA |
| 并发改 efSearch | 竞态 | 每线程独立 index 或加锁 |
| 未固定 CPU 亲和 | 抖动 | 基准机独占 |
| 把 build 时间算进 query | 误导 | build 单独列 |

**QPS 压测**：单线程表定 **算法参数**；线程池 32 定 **容量**。wiki 两表并列，避免用压测 P95 否定单线程拐点选型。

**跨机房**：副本读延迟含网络；ANN SLA 应 **分地域** 写。主库写、从库读时，注意 **复制滞后** 导致新 chunk 搜不到——属 [49 增量](49.incremental-update-tutorial.md) 一致性问题，不是 ANN 参数问题。



## 专精：与 RAG 管道参数联动

| 管道参数 | 与 ANN 关系 |
|----------|-------------|
| recall_k=50 | 评测用 k=50 |
| rerank 输入 50 | ANN 漏检 rerank 无法补救 |
| [98 Top-K](98.top-k-retrieval-tutorial.md) | final_k=5 与 ANN k 解耦 |
| [28 Context](28.context-window-tutorial.md) | 与 ANN 无关但同 wiki |

**端到端实验**：固定 ANN 参数，只改 rerank——若答案质量仍差，查 chunk 或 prompt；固定 rerank，扫 efSearch——若 Hit@50 升而答案仍差，查 **精排或生成**。分层归因避免「一味加大 ef」。

**面试追问**：「recall@10=0.99 够吗？」——若 rerank 从 50 里挑 5，要看 **金标相关 chunk 在不在 Top-50**，不是 Top-10。答：用业务 k 评测，常用 50。



## 专精：文档模板与团队分工

**评测报告负责人**：检索工程师；**签字**：产品（SLA）、SRE（容量）。报告必含：数据快照 hash、query 集版本、参数网格、推荐值、已知限制（如仅 CPU 测）。

**新人 onboarding**：第一周跑通 §9；第二周用 [84 Flat](84.flat-brute-force-search-tutorial.md) 解释差集；第三周对接 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 子集曲线。

**与 [86 HNSW](86.hnsw-index-tutorial.md) 参数对照表**：

| Faiss | Milvus | Qdrant |
|-------|--------|--------|
| efSearch | ef | hnsw_ef |
| efConstruction | efConstruction | ef_construct |
| M | M | m |

写配置时 **列名映射** 进 manifest，避免恢复后抄错列。



## 专精：差集分析与 bad chunk 归类

当 recall@50=0.88 不达标时，导出 **漏检 query**：

```python
def diff_queries(ann, flat, queries, k=50):
    bad = []
    for i, q in enumerate(queries):
        _, a = ann.search(q.reshape(1,-1), k)
        _, f = flat.search(q.reshape(1,-1), k)
        miss = set(f[0]) - set(a[0])
        if miss:
            bad.append((i, miss))
    return bad
```

对 miss 的 flat 邻居做 **归类**：簇边界（IVF）、图早停（HNSW）、边界向量（正常）。IVF 漏检多 → 增 nprobe；HNSW 多 → 增 efSearch；单条 query 极端 → 可能 embed 差或 query 需 [100 改写](100.query-rewriting-tutorial.md)。

**记录进 wiki**：差集样例脱敏后存档，下版 Embedding 升级时 **重跑对比**。



## 专精：GPU 与量化索引备注

`faiss-gpu` 扫参流程同 CPU，但 **P95 单位不同**，不可与 CPU 表合并。`IndexHNSWPQ` 等量化索引 recall 常低于 HNSWFlat——若上 PQ，**单独一条曲线** 与 Flat 金标对比，不要沿用 HNSWFlat 的 efSearch 推荐值。

**企业建议**：PoC 用 `IndexHNSWFlat` 建立 baseline；内存告急再 PQ，并接受 **独立回归**。


## 附录 A：Milvus / Qdrant 扫参对照

**Milvus** [77 篇](77.milvus-tutorial.md)：`search_params={"params": {"ef": 128}}` 或 IVF `nprobe`。导出 CSV 时列名写 `ef` 而非 `efSearch`，避免与 Faiss 混淆。

**Qdrant** [78 篇](78.qdrant-tutorial.md)：`SearchParams(hnsw_ef=128)`。collection 级 `ef_construct` 影响建图，查询扫 `hnsw_ef` 即可画曲线。

**pgvector** [81 篇](81.pgvector-tutorial.md)：`SET ivfflat.probes = 10` 会话变量；benchmark 时固定连接池与 `work_mem`，否则 P95 抖动大。

## 附录 B：回归集 JSON 样例

```json
[
  {"query_id": "q001", "text": "出差住宿标准", "expect_chunk_ids": ["hb:c002"]},
  {"query_id": "q002", "text": "年假几天", "expect_chunk_ids": ["hb:c001"]}
]
```

发版 job：对每条 query 跑 ANN，算 **Hit@50**（金标 chunk 是否在 Top-50）与 **recall@50 vs Flat** 双指标。

## 附录 C：压测与单线程基准分工

| 基准类型 | 目的 | 并发 |
|----------|------|------|
| 单线程延迟 | 选 efSearch/nprobe | 1 |
| 固定 QPS 压测 | 容量规划 | 50～200 |
| 回归 recall | 防回退 | 1，固定种子 |

不要把压测 P95 当作 §9 单线程表的同一列——wiki 应 **分两表** 张贴。


## 专精：FAISS 扫参完整脚本说明

§9 脚本中 `EF_GRID` 建议覆盖 **efSearch 从略大于 k 到 4×k** 区间。若 recall@50 在 ef=128 已达 0.96，ef=256 仅升到 0.97 而 P95 从 40ms 到 85ms，**拐点在 128**。把该值写入 `manifest.json`（[90 备份](90.vector-db-backup-tutorial.md)）与配置中心。

**IVF 分支**：复制同一脚本，把 `index` 换成 `IndexIVFFlat`，扫 `nprobe`。对比时 **N、query 集、metric 必须相同**。常见现象：IVF 在同等 P95 下 recall 略低，但内存更省——选型不是「谁 recall 高」 alone，要叠 **内存、建索引时间、运维复杂度**。

**filtered 子集**：从 id_map 筛 `doc_id=handbook` 的子向量建 **子索引** 对比全库参数。前滤后每桶向量变少，**同样 efSearch recall 常更高**——但后滤场景仍可能 filter_miss（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

**回归 job 伪代码**：

```python
def nightly_ann_regression(index, queries, flat, k=50, threshold=0.95):
    rec = recall_at_k(index, queries, k)
    if rec < threshold:
        alert(f"ANN recall dropped to {rec:.3f}")
    return rec
```

cron 每日跑；发版后手动触发一次。与业务金标 Hit@50 **分开看**——索引 recall 掉 2% 可能用户无感，但连续下降要查 **数据漂移或参数被改**。



## 专精：延迟测量陷阱清单

| 陷阱 | 后果 | 规避 |
|------|------|------|
| 冷启动首轮计入 | P95 虚高 | warm-up 50 次丢弃 |
| search 批大小混用 | 不可比 | 固定 batch=1 报 SLA |
| 并发改 efSearch | 竞态 | 每线程独立 index 或加锁 |
| 未固定 CPU 亲和 | 抖动 | 基准机独占 |
| 把 build 时间算进 query | 误导 | build 单独列 |

**QPS 压测**：单线程表定 **算法参数**；线程池 32 定 **容量**。wiki 两表并列，避免用压测 P95 否定单线程拐点选型。

**跨机房**：副本读延迟含网络；ANN SLA 应 **分地域** 写。主库写、从库读时，注意 **复制滞后** 导致新 chunk 搜不到——属 [49 增量](49.incremental-update-tutorial.md) 一致性问题，不是 ANN 参数问题。



## 专精：与 RAG 管道参数联动

| 管道参数 | 与 ANN 关系 |
|----------|-------------|
| recall_k=50 | 评测用 k=50 |
| rerank 输入 50 | ANN 漏检 rerank 无法补救 |
| [98 Top-K](98.top-k-retrieval-tutorial.md) | final_k=5 与 ANN k 解耦 |
| [28 Context](28.context-window-tutorial.md) | 与 ANN 无关但同 wiki |

**端到端实验**：固定 ANN 参数，只改 rerank——若答案质量仍差，查 chunk 或 prompt；固定 rerank，扫 efSearch——若 Hit@50 升而答案仍差，查 **精排或生成**。分层归因避免「一味加大 ef」。

**面试追问**：「recall@10=0.99 够吗？」——若 rerank 从 50 里挑 5，要看 **金标相关 chunk 在不在 Top-50**，不是 Top-10。答：用业务 k 评测，常用 50。



## 专精：文档模板与团队分工

**评测报告负责人**：检索工程师；**签字**：产品（SLA）、SRE（容量）。报告必含：数据快照 hash、query 集版本、参数网格、推荐值、已知限制（如仅 CPU 测）。

**新人 onboarding**：第一周跑通 §9；第二周用 [84 Flat](84.flat-brute-force-search-tutorial.md) 解释差集；第三周对接 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 子集曲线。

**与 [86 HNSW](86.hnsw-index-tutorial.md) 参数对照表**：

| Faiss | Milvus | Qdrant |
|-------|--------|--------|
| efSearch | ef | hnsw_ef |
| efConstruction | efConstruction | ef_construct |
| M | M | m |

写配置时 **列名映射** 进 manifest，避免恢复后抄错列。



## 专精：差集分析与 bad chunk 归类

当 recall@50=0.88 不达标时，导出 **漏检 query**：

```python
def diff_queries(ann, flat, queries, k=50):
    bad = []
    for i, q in enumerate(queries):
        _, a = ann.search(q.reshape(1,-1), k)
        _, f = flat.search(q.reshape(1,-1), k)
        miss = set(f[0]) - set(a[0])
        if miss:
            bad.append((i, miss))
    return bad
```

对 miss 的 flat 邻居做 **归类**：簇边界（IVF）、图早停（HNSW）、边界向量（正常）。IVF 漏检多 → 增 nprobe；HNSW 多 → 增 efSearch；单条 query 极端 → 可能 embed 差或 query 需 [100 改写](100.query-rewriting-tutorial.md)。

**记录进 wiki**：差集样例脱敏后存档，下版 Embedding 升级时 **重跑对比**。



## 专精：GPU 与量化索引备注

`faiss-gpu` 扫参流程同 CPU，但 **P95 单位不同**，不可与 CPU 表合并。`IndexHNSWPQ` 等量化索引 recall 常低于 HNSWFlat——若上 PQ，**单独一条曲线** 与 Flat 金标对比，不要沿用 HNSWFlat 的 efSearch 推荐值。

**企业建议**：PoC 用 `IndexHNSWFlat` 建立 baseline；内存告急再 PQ，并接受 **独立回归**。


## 附录 A：Milvus / Qdrant 扫参对照

**Milvus** [77 篇](77.milvus-tutorial.md)：`search_params={"params": {"ef": 128}}` 或 IVF `nprobe`。导出 CSV 时列名写 `ef` 而非 `efSearch`，避免与 Faiss 混淆。

**Qdrant** [78 篇](78.qdrant-tutorial.md)：`SearchParams(hnsw_ef=128)`。collection 级 `ef_construct` 影响建图，查询扫 `hnsw_ef` 即可画曲线。

**pgvector** [81 篇](81.pgvector-tutorial.md)：`SET ivfflat.probes = 10` 会话变量；benchmark 时固定连接池与 `work_mem`，否则 P95 抖动大。

## 附录 B：回归集 JSON 样例

```json
[
  {"query_id": "q001", "text": "出差住宿标准", "expect_chunk_ids": ["hb:c002"]},
  {"query_id": "q002", "text": "年假几天", "expect_chunk_ids": ["hb:c001"]}
]
```

发版 job：对每条 query 跑 ANN，算 **Hit@50**（金标 chunk 是否在 Top-50）与 **recall@50 vs Flat** 双指标。

## 附录 C：压测与单线程基准分工

| 基准类型 | 目的 | 并发 |
|----------|------|------|
| 单线程延迟 | 选 efSearch/nprobe | 1 |
| 固定 QPS 压测 | 容量规划 | 50～200 |
| 回归 recall | 防回退 | 1，固定种子 |

不要把压测 P95 当作 §9 单线程表的同一列——wiki 应 **分两表** 张贴。


## 专精：FAISS 扫参完整脚本说明

§9 脚本中 `EF_GRID` 建议覆盖 **efSearch 从略大于 k 到 4×k** 区间。若 recall@50 在 ef=128 已达 0.96，ef=256 仅升到 0.97 而 P95 从 40ms 到 85ms，**拐点在 128**。把该值写入 `manifest.json`（[90 备份](90.vector-db-backup-tutorial.md)）与配置中心。

**IVF 分支**：复制同一脚本，把 `index` 换成 `IndexIVFFlat`，扫 `nprobe`。对比时 **N、query 集、metric 必须相同**。常见现象：IVF 在同等 P95 下 recall 略低，但内存更省——选型不是「谁 recall 高」 alone，要叠 **内存、建索引时间、运维复杂度**。

**filtered 子集**：从 id_map 筛 `doc_id=handbook` 的子向量建 **子索引** 对比全库参数。前滤后每桶向量变少，**同样 efSearch recall 常更高**——但后滤场景仍可能 filter_miss（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

**回归 job 伪代码**：

```python
def nightly_ann_regression(index, queries, flat, k=50, threshold=0.95):
    rec = recall_at_k(index, queries, k)
    if rec < threshold:
        alert(f"ANN recall dropped to {rec:.3f}")
    return rec
```

cron 每日跑；发版后手动触发一次。与业务金标 Hit@50 **分开看**——索引 recall 掉 2% 可能用户无感，但连续下降要查 **数据漂移或参数被改**。



## 专精：延迟测量陷阱清单

| 陷阱 | 后果 | 规避 |
|------|------|------|
| 冷启动首轮计入 | P95 虚高 | warm-up 50 次丢弃 |
| search 批大小混用 | 不可比 | 固定 batch=1 报 SLA |
| 并发改 efSearch | 竞态 | 每线程独立 index 或加锁 |
| 未固定 CPU 亲和 | 抖动 | 基准机独占 |
| 把 build 时间算进 query | 误导 | build 单独列 |

**QPS 压测**：单线程表定 **算法参数**；线程池 32 定 **容量**。wiki 两表并列，避免用压测 P95 否定单线程拐点选型。

**跨机房**：副本读延迟含网络；ANN SLA 应 **分地域** 写。主库写、从库读时，注意 **复制滞后** 导致新 chunk 搜不到——属 [49 增量](49.incremental-update-tutorial.md) 一致性问题，不是 ANN 参数问题。"""

ARTICLE_88 = """# C4 向量存储（十四）：Metadata Filter 过滤检索完全指南

> 向量 ANN 不懂 **谁有权看哪份文档**——[53 ACL](53.metadata-acl-tutorial.md) 的 `acl_group`、`doc_id` 版本、[89 租户](89.multi-tenant-namespace-tutorial.md) 的 `tenant_id` 必须在 **检索层** 生效。**Metadata Filter** 在 query 时按元数据 **前滤或后滤**，把搜索限制在 **合法子集**。[76 Chroma](76.chroma-vector-db-tutorial.md) 的 `where` 是 PoC 最直观写法。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **105** 条）。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、[79 Weaviate](79.weaviate-tutorial.md)、[80 Pinecone](80.pinecone-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md)、[82 Elasticsearch 向量](82.elasticsearch-vector-tutorial.md)、[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)。下一篇 [89 多租户](89.multi-tenant-namespace-tutorial.md) 讲 namespace 隔离。

---

## 目录

1. [前言：ANN 不懂权限](#1-前言ann-不懂权限)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Metadata Filter 是什么](#3-metadata-filter-是什么)
4. [元数据字段设计](#4-元数据字段设计)
5. [前滤 vs 后滤](#5-前滤-vs-后滤)
6. [前滤实现要点](#6-前滤实现要点)
7. [后滤与 over-fetch](#7-后滤与-over-fetch)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：Chroma where Mini-RAG](#9-综合实战chroma-where-mini-rag)
10. [各向量库过滤对照](#10-各向量库过滤对照)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：ANN 不懂权限

PoC 全库 Top-5 能答出差标准——上线后财务问「为何看到 HR 薪酬 chunk」？根因：**检索未过滤 ACL**。

Prompt 里写「不要引用无权限文档」 **无效**——模型仍会看到 chunk 内容。必须在 **向量库 query** 加 filter。

**读完本文**：设计 metadata schema；写 Chroma `where`；选前滤/后滤；识别五种翻车。



### 1.1 路线图位置

```text
104 ANN [87] → 105 Metadata Filter ← 本篇 → 106 多租户 [89]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 前滤 | Pre-filter | ANN 前缩集合 |
| 后滤 | Post-filter | ANN 后筛 metadata |
| where | where / expr | 声明式过滤 |
| over-fetch | 扩大 k | 后滤凑满条数 |

### 1.3 读完本篇的最小交付物

1. metadata schema 表；2. Chroma where 可运行；3. 前/后滤选型一段；4. §8 五种翻车；5. 带 ACL 的 query 样例。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（105）。** 讲 filter 概念、Chroma/Milvus 对照、Mini-RAG；不讲 ABAC 策略引擎全书。

| 步骤 | 验收 |
|------|------|
| 读 §4 schema | 字段表完整 |
| 跑 §9 | finance 过滤生效 |
| 对照 §10 | 能答三库 API |



### 2.2 沿用前文

| ACL | [53](53.metadata-acl-tutorial.md) |
| Chroma where | [76](76.chroma-vector-db-tutorial.md) |
| 多租户 | [89](89.multi-tenant-namespace-tutorial.md) |

---

## 3. Metadata Filter 是什么

读下图：query 向量 + metadata 条件 → 合法子集上的 ANN。

![元数据过滤检索是什么](image/metadata-filter-retrieval/01-filter-idea.png)

每条 chunk 入库时带 **metadatas**（与 [76 Chroma](76.chroma-vector-db-tutorial.md) 的 `collection.add(metadatas=...)` 一致）。

查询时引擎在 **满足 filter 的记录** 上做近邻——或先 ANN 再滤，见 §5。



---

## 4. 元数据字段设计

企业 RAG 常见过滤字段（衔接 [50 doc_id](50.metadata-doc-id-tutorial.md)、[51 chunk_id](51.metadata-chunk-id-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md)）：

| 字段 | 用途 | 示例 |
|------|------|------|
| doc_id | 限定知识库版本 | handbook-v3 |
| tenant_id | 多租户 | acme-corp |
| acl_group | 权限 | hr, finance_only |
| version | 文档版本 | 3 |
| lang | 语言 | zh |

**原则**：入库管道 **统一 schema**；缺字段 = 过滤漏网。

## 5. 前滤 vs 后滤

![前滤 vs 后滤](image/metadata-filter-retrieval/02-pre-post-filter.png)

| 模式 | 做法 | 优点 | 风险 |
|------|------|------|------|
| 前滤 Pre-filter | ANN 前缩小候选集 | 快、少越权 | 引擎支持不一；子集太小 recall 掉 |
| 后滤 Post-filter | ANN 取大 k 再筛 metadata | 实现简单 | k 不够时 **凑不满**；可能漏 + 越权窗口 |
| 混合 | 粗前滤 + 精后滤 | 平衡 | 复杂度高 |

**Chroma** [76 篇](76.chroma-vector-db-tutorial.md)：`where={"doc_id": "handbook"}` 在 query 里声明。  
**Milvus** [77 篇](77.milvus-tutorial.md)：`expr='doc_id == "handbook"'`。  
**Qdrant** [78 篇](78.qdrant-tutorial.md)：`Filter(must=[...])`。  
**pgvector** [81 篇](81.pgvector-tutorial.md)：`WHERE doc_id = $1 ORDER BY embedding <=> $q`。

## 6. 前滤实现要点

1. **服务端注入 filter**——禁止客户端自选 `tenant_id`（[89 多租户](89.multi-tenant-namespace-tutorial.md)）。  
2. 过滤字段 **建标量索引**（视引擎而定）。  
3. 与 [87 ANN 评测](87.ann-recall-latency-tutorial.md)：**带 filter 的 query 子集** 单独扫 recall 曲线。

## 7. 后滤与 over-fetch

后滤时设 `k_ann = k_final × over_fetch_factor`（常 3～10）。若仍凑不满，返回 **明确空结果** 或拒答（[112 拒答](112.refusal-strategy-tutorial.md)），不要硬塞低分 chunk。

## 10. 各向量库过滤对照

| 库 | API 关键词 | 备注 |
|----|-----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr, partition | partition 可当粗隔离 |
| Qdrant | payload Filter | JSON 路径 |
| Pinecone | metadata filter | [80 篇](80.pinecone-tutorial.md) |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

---

## 8. 先错对对：五种典型翻车

### 1. 错：靠 prompt 禁止越权

**对：** 检索层 filter + [53 ACL](53.metadata-acl-tutorial.md)

模型仍能看到无权限 chunk 文本。

### 2. 错：客户端传 tenant_id 参数

**对：** 网关从 JWT 注入 tenant

可被篡改，严重事故。

### 3. 错：后滤 k=5 无 over-fetch

**对：** k_ann=50 再滤到 5

常凑不满或全被滤掉。

### 4. 错：过滤字段 ingest 时没写

**对：** 管道 schema 校验

where 永远匹配不到。

### 5. 错：全库 ANN 参数用于强前滤子集

**对：** 带 filter 子集重扫 [87](87.ann-recall-latency-tutorial.md)

recall 曲线不同。



---

## 9. 综合实战：Chroma where Mini-RAG

### 9.1 数据

```python
import chromadb
client = chromadb.PersistentClient(path="./chroma_filter_demo")
col = client.get_or_create_collection("handbook")

chunks = [
    {"id": "hb:1", "text": "年假 5 天。", "meta": {"doc_id": "handbook", "acl_group": "all_staff"}},
    {"id": "fin:1", "text": "Q3 预算审批。", "meta": {"doc_id": "finance", "acl_group": "finance_only"}},
]
# embeddings 省略：用同一模型 embed 后 add
col.add(ids=[c["id"] for c in chunks], documents=[c["text"] for c in chunks],
        metadatas=[c["meta"] for c in chunks], embeddings=embeddings)
```

### 9.2 带 ACL 的 query

```python
def search_staff(query_emb, user_groups):
    return col.query(
        query_embeddings=[query_emb],
        n_results=5,
        where={"acl_group": {"$in": list(user_groups) + ["all_staff"]}},
    )
```

### 9.3 验收表

| 检查 | 标准 |
|------|------|
| handbook query | 命中 hb:1 |
| finance_only 用户 | 可见 fin:1 |
| 仅 all_staff 用户 | 不见 fin:1 |
| doc_id 过滤 | where doc_id=handbook 无 finance |

### 9.4 与混合检索

[93 混合](93.hybrid-search-tutorial.md) 双路必须用 **相同 filter**，否则 RRF 掺越权结果。

### 9.5 审计日志

记录 `user_id`、`filter摘要`、`top_ids`——安全复盘必备。

---

## 综合概念地图

![元数据过滤概念地图](image/metadata-filter-retrieval/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| 前滤 | ANN 前缩范围 |
| where | Chroma 声明式过滤 |
| ACL | [53 篇](53.metadata-acl-tutorial.md) |
| 下一篇 | [89 租户](89.multi-tenant-namespace-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：前滤和后滤哪个更好？**
A：能前滤且引擎支持则前滤；否则后滤 + over-fetch。

**Q：Chroma where 支持 $and 吗？**
A：常见版本支持；以本地文档为准。

**Q：Milvus partition 和 expr 区别？**
A：partition 物理粗分；expr 细过滤。

**Q：pgvector 怎么过滤？**
A：SQL WHERE + ORDER BY 向量距离。

**Q：过滤后 recall 怎么测？**
A：[87 篇](87.ann-recall-latency-tutorial.md) 对 filter 子集单独扫。

**Q：OpenSearch 呢？**
A：见 [83 篇](83.opensearch-hybrid-tutorial.md) bool + knn。

**Q：filter_miss 是什么？**
A：后滤后条数不足 k；要监控告警。

**Q：面试 30 秒版？**
A：metadata 在检索层过滤；禁止客户端自选租户；双路混合同 filter。

**Q：能否只建多索引代替 filter？**
A：索引爆炸；metadata + namespace 更常见。

**Q：ingest 漏写 acl 怎么办？**
A：dead letter + 重跑；已入库要 backfill。



---

## 总结与系列下一步

1. 权限在检索层不在 prompt；2. 前滤/后滤各有坑；3. Chroma where 是 PoC 入口；4. 混合检索同 filter；5. 下一篇 [89 多租户](89.multi-tenant-namespace-tutorial.md)。

### 系列下一步

| ACL | [53](53.metadata-acl-tutorial.md) |
| Chroma | [76](76.chroma-vector-db-tutorial.md) |
| 多租户 | [89](89.multi-tenant-namespace-tutorial.md) |

### 30 分钟作业

1. 跑 §9；2. 画 schema 表；3. 写前/后滤选型；4. 勾选 105。

---

> **初学者可能仍困惑的点**
> - 后滤不是「多搜几条再 if」——要 over-fetch 与空结果策略。
> - filter 与 [89 namespace](89.multi-tenant-namespace-tutorial.md) 互补：粗隔离 + 细 ACL。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。



## 专精：后滤 over_fetch 计算器

设目标 `k_final=5`，估计过滤通过率 `p`（历史统计）。粗算 `k_ann ≈ k_final / p`，再加安全系数 2。

示例：ACL 后约 40% 通过 → `k_ann ≈ 5/0.4 ≈ 13`，取 `k_ann=50` 更安全。监控 **filter_miss rate**；若 >10%，调大 k_ann 或收紧前滤。

**空结果策略**：filter_miss 且最高分低于 [99 阈值](99.score-threshold-tutorial.md) → [112 拒答](112.refusal-strategy-tutorial.md)，勿用无关 chunk 凑数。



## 专精：与混合检索同 filter 联调

[93 混合](93.hybrid-search-tutorial.md) 联调 checklist：

1. dense `where` / expr 复制到 BM25 查询（ES 用同一 bool filter）  
2. 单号 query 仅 sparse 命中时，确认 **filter 未把该 doc 滤掉**  
3. 融合后 dedupe 仍带 **同一 chunk 的 metadata** 供引用  
4. 审计日志记录 **filter 摘要** 不含 PII 原文  

**渗透用例**：低权限用户带 `where acl=admin` 篡改请求 → API 网关 **剥离客户端 filter**，只信 JWT。



## 专精：pgvector 过滤 SQL 模式

```sql
SELECT chunk_id, text, embedding <=> $1 AS dist
FROM chunks
WHERE tenant_id = $2 AND acl_group = ANY($3)
ORDER BY dist
LIMIT 50;
```

**索引**：`(tenant_id, acl_group)` btree + `ivfflat(hnsw)` 向量索引。`EXPLAIN ANALYZE` 看是否 **先滤后扫**。与 [81 篇](81.pgvector-tutorial.md)、[87 probes](87.ann-recall-latency-tutorial.md) 联调。



## 专精：filter 回归金标

构建 20 条：`(user_role, query, must_include_chunk, must_exclude_chunk)`。发版全跑。must_exclude 出现即 **P0**。与端到端答案测试互补。



## 深化：Elasticsearch bool + knn 过滤示例 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2],
    "k": 50,
    "num_candidates": 200,
    "filter": {
      "bool": {
        "must": [
          {"term": {"tenant_id": "acme"}},
          {"terms": {"acl_group": ["all_staff", "hr"]}}
        ]
      }
    }
  }
}
```

**num_candidates** 影响 recall 与延迟，见 [87 篇](87.ann-recall-latency-tutorial.md)。filter 与 knn **同一请求** 才是前滤。勿先 knn 全库再 Python 滤。



## 深化：Qdrant Filter 组合 [78 篇](78.qdrant-tutorial.md)

对 `tenant_id`、`acl_group` 建 payload 索引。`should` 扩角色与 [53 ACL](53.metadata-acl-tutorial.md) 对齐。渗透：finance_only 文档对 all_staff 用户 **must_exclude**。


## 附录 A：where 运算符食谱（Chroma）

```python
# 等于
where={"doc_id": "handbook"}
# 在集合内
where={"section": {"$in": ["差旅", "休假"]}}
# 与
where={"$and": [{"version": 3}, {"lang": "zh"}]}
```

运算符以你所用 **chromadb 版本文档** 为准；升级库时跑 **过滤回归集**。

## 附录 B：Milvus expr 示例

```python
expr = 'doc_id == "handbook" && acl_group in ["all_staff", "hr"]'
```

partition_key 可先按 `tenant_id` 粗分，expr 再细过滤 [89 篇](89.multi-tenant-namespace-tutorial.md)。

## 附录 C：filter_miss 监控

定义：后滤后 `len(results) < k_final` 的次数占比。  
告警阈值：>5% 需检查 over_fetch 或 ACL 过严。  
与 `ann_miss`（[87 篇](87.ann-recall-latency-tutorial.md)）分开打点，便于归因。


## 专精：metadata schema 评审表

评审会逐字段问：

| 字段 | 是否必填 | 谁写入 | 过滤用途 |
|------|----------|--------|----------|
| chunk_id | 是 | ingest | 去重、溯源 |
| doc_id | 是 | ingest | 版本切换 |
| tenant_id | 多租户必填 | ingest | [89](89.multi-tenant-namespace-tutorial.md) |
| acl_group | 是 | ingest | [53 ACL](53.metadata-acl-tutorial.md) |
| version | 推荐 | ingest | [48 版本](48.doc-versioning-tutorial.md) |
| source/page | 推荐 | ingest | [52 溯源](52.metadata-source-page-tutorial.md) |

**dead letter**：缺必填字段的 chunk 不入库，进 DLQ 告警。禁止 **事后 SQL 补字段** 留下无 acl 历史数据。

**类型一致**：`version` 勿混用字符串 `"3"` 与整数 `3`，否则 `where version==3` 漏匹配。



## 专精：前滤引擎能力矩阵

| 引擎 | 前滤方式 | 注意 |
|------|----------|------|
| Chroma | where | [76 篇](76.chroma-vector-db-tutorial.md) |
| Milvus | expr + partition | partition 非万能 ACL |
| Qdrant | Filter | payload 索引 |
| pgvector | SQL WHERE | 规划组合索引 |
| FAISS 裸 | 需 IDSelector | 常改向量库 |
| ES | bool filter + knn | [82 篇](82.elasticsearch-vector-tutorial.md) |

**FAISS IDSelector** 适合 **候选 id 集合不大**；百万级 ACL 组合爆炸时，用 **metadata 索引** 或 **分 collection**。

**性能**：前滤过严 → 子集千条级，ANN 毫秒级但 **语义覆盖窄**；前滤过宽 → 接近全库扫。用 **真实角色分布** 压测 P95。"""

ARTICLE_89 = """# C4 向量存储（十五）：多租户 Namespace 隔离完全指南

> SaaS 知识库：**租户 A 绝不能搜到租户 B 的 embedding**。多租户隔离靠 **namespace / collection / 独立库** 等 **逻辑或物理边界**，再叠加 [88 metadata filter](88.metadata-filter-retrieval-tutorial.md) 与 [53 ACL](53.metadata-acl-tutorial.md)。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **106** 条）。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、[79 Weaviate](79.weaviate-tutorial.md)、[80 Pinecone](80.pinecone-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md)、[82 Elasticsearch 向量](82.elasticsearch-vector-tutorial.md)、[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)、[88 过滤](88.metadata-filter-retrieval-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md)。下一篇 [90 备份](90.vector-db-backup-tutorial.md) 要 **按租户** 规划恢复。

---

## 目录

1. [前言：租户串库是 P0 事故](#1-前言租户串库是-p0-事故)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [多租户向量库是什么](#3-多租户向量库是什么)
4. [隔离模式对照](#4-隔离模式对照)
5. [Namespace vs Collection vs 独立库](#5-namespace-vs-collection-vs-独立库)
6. [身份注入与网关](#6-身份注入与网关)
7. [配额与计费](#7-配额与计费)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：双租户 Chroma Mini-RAG](#9-综合实战双租户-chroma-mini-rag)
10. [各托管产品对照](#10-各托管产品对照)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：租户串库是 P0 事故

多租户 RAG：**每个客户** 独立知识库、独立索引空间或强制 `tenant_id` 过滤。串库 = **数据泄露**，合规与法务风险极高。

通俗说：**namespace 像大楼里分房间；metadata filter 像房间里的柜子锁**——最好两层都有。

**读完本文**：四种隔离模式；Chroma/Pinecone/Milvus 对照；网关注入 tenant；五种翻车。



### 1.1 路线图位置

```text
105 Filter [88] → 106 多租户 ← 本篇 → 107 备份 [90]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 租户 | Tenant | SaaS 客户 |
| 命名空间 | Namespace | 逻辑隔离桶 |
| 集合 | Collection | 同空间一批向量 |
| 串库 | Cross-tenant leak | P0 事故 |

### 1.3 读完本篇的最小交付物

1. 隔离模式选型表；2. 双租户 demo；3. 网关注入设计草图；4. §8 翻车；5. 配额字段设计。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（106）。** 讲隔离模式、身份注入、PoC；不讲 K8s 网络策略全书。

| 步骤 | 验收 |
|------|------|
| 读 §4 模式表 | 能选型 |
| 跑 §9 | 租户互不可见 |
| 画网关图 | JWT→tenant |



### 2.2 沿用前文

| Filter | [88](88.metadata-filter-retrieval-tutorial.md) |
| ACL | [53](53.metadata-acl-tutorial.md) |
| 备份 | [90](90.vector-db-backup-tutorial.md) |

---

## 3. 多租户向量库是什么

读下图：请求经网关解析 tenant → 路由到对应 namespace/collection。

![多租户向量库怎么隔离](image/multi-tenant-namespace/01-tenant-idea.png)

**tenant_id** 来自 **认证系统**（JWT、OIDC），不是 query 参数。

入库时每条 chunk metadata 带 `tenant_id`；查询时 **强制 filter** 或 **物理隔离索引**。



---

## 4. 隔离模式对照

![Namespace vs Collection](image/multi-tenant-namespace/02-isolation-patterns.png)

| 模式 | 做法 | 隔离强度 | 运维成本 |
|------|------|----------|----------|
| 独立库/集群 | 每租户一套 | 最强 | 最高 |
| 独立 Collection | 同进程多 collection | 强 | 中 |
| Namespace（Pinecone 等） | 托管命名空间 | 强 | 低（托管） |
| 共享索引 + tenant filter | 单 collection + where | 中（依赖实现） | 最低 |

**合规高** 倾向物理隔离；**长尾小租户** 可共享 + 强 filter。

## 5. Namespace vs Collection

- **Pinecone** [80 篇](80.pinecone-tutorial.md)：`namespace` 参数隔离。  
- **Milvus** [77 篇](77.milvus-tutorial.md)：collection 或 partition。  
- **Chroma** [76 篇](76.chroma-vector-db-tutorial.md)：多 collection 或 metadata `tenant_id`。  
- **Qdrant** [78 篇](78.qdrant-tutorial.md)：collection + payload filter。

## 6. 身份注入与网关

```text
Client → API Gateway (JWT) → 解析 tenant_id
      → Vector DB 客户端强制 collection/namespace/filter
      → 禁止透传客户端 tenant 字段
```

审计：每次 search 记 `tenant_id`、`user_id`、filter 摘要。

## 7. 配额与计费

按租户统计：**向量条数、存储 GB、query QPS**。超限 **限流** 或 **拒服**——见路线图 F 管理后台。

---

## 8. 先错对对：五种典型翻车

### 1. 错：query 参数传 tenant_id

**对：** JWT 解析注入

可被伪造。

### 2. 错：只依赖 prompt 隔离

**对：** 索引层 namespace/filter

模型仍可见文本。

### 3. 错：共享 collection 无 filter 测试

**对：** 互查渗透测试

PoC 常漏。

### 4. 错：备份不分租户

**对：** 按租户 manifest [90](90.vector-db-backup-tutorial.md)

恢复串库。

### 5. 错：小租户与大租户同 shard 无配额

**对：** QPS/存储配额

 noisy neighbor。



---

## 9. 综合实战：双租户 Chroma Mini-RAG

```python
import chromadb
client = chromadb.PersistentClient(path="./multi_tenant_demo")

def get_col(tenant_id: str):
    return client.get_or_create_collection(f"kb_{tenant_id}")

def ingest(tenant_id, ids, docs, embs, metas):
    col = get_col(tenant_id)
    for m in metas:
        m["tenant_id"] = tenant_id
    col.add(ids=ids, documents=docs, embeddings=embs, metadatas=metas)

def search(tenant_id, q_emb, k=5):
    col = get_col(tenant_id)
    return col.query(
        query_embeddings=[q_emb], n_results=k,
        where={"tenant_id": tenant_id},
    )
```

### 9.1 验收

| 测试 | 期望 |
|------|------|
| tenant_a 搜 | 仅 a 的 chunk |
| tenant_b 搜 | 仅 b 的 chunk |
| 伪造 tenant 参数 | 网关层拒绝 |

### 9.2 与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 叠加

`where={"$and": [{"tenant_id": t}, {"acl_group": {"$in": groups}}]}`

### 9.3 渗透 checklist

- [ ] 跨 tenant collection 名猜测  
- [ ] API 未带 token  
- [ ] token 篡改 tenant claim

---

## 综合概念地图

![多租户隔离概念地图](image/multi-tenant-namespace/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| tenant_id | 来自 JWT |
| namespace | 逻辑隔离 |
| 下一篇 | [90 备份](90.vector-db-backup-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：Namespace 和 metadata filter 二选一？**
A：不互斥；高合规可双层。

**Q：Chroma 多租户推荐？**
A：多 collection 或强制 tenant where。

**Q：Milvus 多租户？**
A：collection per tenant 或 partition + expr。

**Q：Pinecone namespace 限制？**
A：见 [80 篇](80.pinecone-tutorial.md) 配额。

**Q：共享索引安全吗？**
A：依赖引擎 filter 正确性 + 渗透测试。

**Q：租户删除怎么做？**
A：delete collection + 备份清理 [90](90.vector-db-backup-tutorial.md)。

**Q：跨租户 admin？**
A：break-glass 角色 + 审计，默认禁止。

**Q：面试 30 秒版？**
A：tenant 从 JWT 注入；物理 namespace 或强 filter；禁止客户端自选。

**Q：与 [89] 和 [88] 关系？**
A：本篇粗隔离，88 细 filter，53 ACL 字段。

**Q：PoC 单租户要设计吗？**
A：要；接口预留 tenant，避免重构。



---

## 总结与系列下一步

1. 串库是 P0；2. tenant 从身份来；3. namespace/collection/filter 选型；4. 渗透测试；5. 下一篇 [90 备份](90.vector-db-backup-tutorial.md)。

### 系列下一步

| 过滤 | [88](88.metadata-filter-retrieval-tutorial.md) |
| 备份 | [90](90.vector-db-backup-tutorial.md) |
| Pinecone | [80](80.pinecone-tutorial.md) |

### 30 分钟作业

1. 跑 §9 双租户；2. 画网关图；3. 写选型表；4. 勾选 106。

---

> **初学者可能仍困惑的点**
> - 多 collection 不等于安全——仍要 verify 路由不会指错 collection。
> - 备份恢复必须按租户验证，见 [90 篇](90.vector-db-backup-tutorial.md)。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。



## 专精：与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双层模型

**L1 namespace/collection**：粗隔离，防跨租户灾难。  
**L2 acl_group filter**：租户内角色。  
两层都 **服务端注入**；客户端只传 query 文本。



## 深化：SaaS 套餐与隔离映射

免费档共享 collection + 强制 filter；企业档独立 collection 或集群。升级时 **snapshot 迁移** [90 备份](90.vector-db-backup-tutorial.md)，非改标签。



## 深化：Chroma 多 collection 路由

collection 名内部 UUID 映射，禁止用户自定义防猜测。删租户 `delete_collection` + 备份归档。


## 附录 A：Pinecone namespace 速查 [80 篇](80.pinecone-tutorial.md)

```python
index.query(vector=q, top_k=5, namespace="tenant_acme", filter={"doc_id": "hb"})
```

namespace 与 metadata filter **叠加**；删除租户 = delete namespace 全量。

## 附录 B：合规检查单

- [ ] 渗透：租户 A token 访问租户 B  
- [ ] 备份恢复不跨租户 [90 篇](90.vector-db-backup-tutorial.md)  
- [ ] 日志含 tenant_id 可审计  
- [ ] 离职员工 token 失效后不可搜旧租户


## 专精：租户生命周期

| 阶段 | 动作 |
|------|------|
| 开通 | 建 namespace/collection + 默认配额 |
| 运行 | JWT 注入 tenant；监控用量 |
| 升级 | 独立备份 [90](90.vector-db-backup-tutorial.md) |
| 停用 | 只读 → 导出 → 删除 |
| 删除 | 合规留存期后 wipe |

**试用转正式**：试用 tenant 数据 **不可** 直接改 id 进生产 tenant——应导出再导入新 namespace，避免 **试用垃圾进生产**。



## 专精：隔离强度决策树

```
合规是否要求物理隔离？
  是 → 独立集群或独立库
  否 → 租户规模是否极大头？
    是 → 大客户独立 collection
    否 → 共享 collection + 强制 tenant_id filter + 渗透测试
```

**金融/医疗** 常要物理隔离；内部部门知识库可 **逻辑隔离 + ACL**（[53](53.metadata-acl-tutorial.md)）。



## 专精：Milvus 多租户模式

[77 篇](77.milvus-tutorial.md)：`collection per tenant` vs `partition_key=tenant_id`。collection 隔离清晰、资源隔离好；partition 省运维但 **误配 expr 风险高**。备份按 collection 导出 manifest 含 `tenant_id`。

**跨 tenant 管理 API**：仅 `super_admin` 角色；所有调用记审计。



## 专精：配额与限流

| 配额 | 告警 |
|------|------|
| 向量条数 | 80% 容量邮件 |
| 存储 GB | 与备份成本联动 |
| QPS | 令牌桶限流 |

超配额 **拒写不拒读** 或 **整体只读**——产品策略写入 SLA。与 [路线图 186 限流](ENTERPRISE_RAG_ROADMAP.md) 一致。



## 专精：渗透测试用例扩展

1. 修改 JWT payload 中 tenant  
2. 猜测相邻 tenant 的 collection 名  
3. 备份文件恢复到错误 tenant 路径  
4. 共享缓存 key 未含 tenant 前缀  
5. 日志 aggregator 跨 tenant 混索引  

每项 **期望失败** 并告警。"""

ARTICLE_90 = """# C4 向量存储（十六）：向量库备份与恢复完全指南

> 索引文件损坏、误删 collection、区域故障——没有备份就无法 **RTO/RPO** 承诺。向量库备份不仅是 **向量矩阵**，还包括 **索引结构（HNSW 图/IVF 质心）、元数据、manifest（模型名、维度、metric）**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **107** 条）。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、[79 Weaviate](79.weaviate-tutorial.md)、[80 Pinecone](80.pinecone-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md)、[82 Elasticsearch 向量](82.elasticsearch-vector-tutorial.md)、[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)、[48 版本](48.doc-versioning-tutorial.md)、[89 多租户](89.multi-tenant-namespace-tutorial.md)。恢复后要跑 [87 ANN 评测](87.ann-recall-latency-tutorial.md) 与 [88 过滤](88.metadata-filter-retrieval-tutorial.md) 抽样。

---

## 目录

1. [前言：向量库丢了能否一夜恢复](#1-前言向量库丢了能否一夜恢复)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [备份什么](#3-备份什么)
4. [备份策略：全量与增量](#4-备份策略全量与增量)
5. [Manifest 与版本一致](#5-manifest-与版本一致)
6. [恢复流程](#6-恢复流程)
7. [多租户与合规](#7-多租户与合规)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：FAISS + manifest 备份脚本](#9-综合实战faiss--manifest-备份脚本)
10. [各产品备份要点](#10-各产品备份要点)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：向量库丢了能否一夜恢复

Chroma 目录误删、Milvus 磁盘坏、云区域故障——若只有 **可重建的源文档** 而无索引快照，恢复 = **全量 re-embed + 重建**，可能 **数小时到数天**。

**RPO**（恢复点目标）：能接受丢多久数据；**RTO**（恢复时间目标）：多久恢复服务。

**读完本文**：备份清单；manifest 字段；恢复验证步骤；FAISS 备份脚本。



### 1.1 路线图位置

```text
106 多租户 [89] → 107 备份 ← 本篇 → 108 Dense [91]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| RPO | Recovery Point Objective | 可丢数据时间窗 |
| RTO | Recovery Time Objective | 恢复服务时长 |
| manifest | 版本清单 | 模型、维度、metric |
| 冷备 | Cold backup | 对象存储归档 |

### 1.3 读完本篇的最小交付物

1. 备份清单表；2. manifest.json 样例；3. §9 脚本；4. 恢复验证 checklist；5. §8 翻车。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（107）。** 讲备份范围、manifest、恢复验证；不讲跨云 DR 全书。

| 步骤 | 验收 |
|------|------|
| 读 §3 清单 | 能列 5 类资产 |
| 写 manifest | 字段完整 |
| 跑 §9 | 可 restore 搜索 |



### 2.2 沿用前文

| 版本 | [48](48.doc-versioning-tutorial.md) |
| 多租户 | [89](89.multi-tenant-namespace-tutorial.md) |
| ANN 评测 | [87](87.ann-recall-latency-tutorial.md) |

---

## 3. 备份什么

读下图：向量、索引、元数据、manifest 四层。

![向量库要备份什么](image/vector-db-backup/01-backup-idea.png)

1. **向量数据**（或可从原文 re-embed 的 **chunk 文本 + id_map**）；2. **ANN 索引文件**（FAISS `.index`、Chroma 目录、Milvus snapshot）；3. **元数据/原文**；4. **manifest**（embedding 模型、dim、metric、build 时间）。

只备向量不备 manifest → 恢复后 **metric 错、模型错** 仍 silent failure。



---

## 4. 备份策略

| 策略 | 频率 | 适用 |
|------|------|------|
| 全量快照 | 日/周 | 中小库 |
| 增量 | 小时级 | 大库、变更多 |
| 逻辑导出 | 发版前 | 跨环境迁移 |

衔接 [49 增量](49.incremental-update-tutorial.md)：增量 ingest 后备份 **新 segment** 或 **周期全量**。

## 5. Manifest 示例

```json
{
  "collection": "handbook_v3",
  "embedding_model": "bge-m3",
  "dim": 1024,
  "metric": "cosine_ip",
  "index_type": "HNSW",
  "ann_params": {"M": 32, "efSearch": 128},
  "chunk_count": 120450,
  "built_at": "2026-07-01T02:00:00Z",
  "tenant_id": "acme"
}
```

## 6. 恢复流程

![备份恢复流程](image/vector-db-backup/02-restore-flow.png)

1. 停写流量；2. 恢复文件到 **新路径/新 collection**；3. 校验 manifest 与文件 hash；4. **抽样 query** 对比 Top-k 与备份前；5. [87 recall](87.ann-recall-latency-tutorial.md) 快扫；6. [88 ACL](88.metadata-filter-retrieval-tutorial.md) 渗透；7. 切流量。

## 7. 多租户与合规

[89 篇](89.multi-tenant-namespace-tutorial.md)：备份 **按租户分路径**；恢复演练 **不得跨租户**。加密 at-rest、访问审计。

## 10. 各产品要点

| 产品 | 备份方式 |
|------|----------|
| FAISS | write_index + id_map.json |
| Chroma | 复制 persist_directory |
| Milvus | backup/snapshot API [77] |
| pgvector | pg_dump + 索引 |
| Pinecone | 托管方策略 [80] |

---

## 8. 先错对对：五种典型翻车

### 1. 错：只备份 PDF 不备份索引

**对：** 索引+manifest 或 可重建流水线文档

re-embed 太慢。

### 2. 错：恢复后不验证 Top-k

**对：** 抽样 query 对比 + recall 快扫

silent regression。

### 3. 错：manifest 缺 embedding 模型名

**对：** 完整 manifest

换模型空间不一致。

### 4. 错：多租户混在一个备份包

**对：** 分租户路径与恢复权限

恢复串库。

### 5. 错：从不做恢复演练

**对：** 季度 drill

真故障时不会操作。



---

## 9. 综合实战：FAISS + manifest 备份脚本

```python
import json, shutil, hashlib, faiss
from pathlib import Path
from datetime import datetime, timezone

def backup_faiss(index, id_map: dict, out_dir: Path, manifest: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    idx_path = out_dir / "index.faiss"
    faiss.write_index(index, str(idx_path))
    (out_dir / "id_map.json").write_text(json.dumps(id_map, ensure_ascii=False), encoding="utf-8")
    manifest = {**manifest, "built_at": datetime.now(timezone.utc).isoformat()}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    h = hashlib.sha256(idx_path.read_bytes()).hexdigest()
    (out_dir / "index.sha256").write_text(h)

def restore_faiss(backup_dir: Path):
    manifest = json.loads((backup_dir / "manifest.json").read_text(encoding="utf-8"))
    index = faiss.read_index(str(backup_dir / "index.faiss"))
    id_map = json.loads((backup_dir / "id_map.json").read_text(encoding="utf-8"))
    return index, id_map, manifest
```

### 9.1 验收

| 项 | 通过 |
|----|------|
| restore 后 search | Top-k 与备份前一致 |
| manifest 字段 | model/dim/metric 齐 |
| hash 校验 | index.sha256 匹配 |

### 9.2 与 Chroma

`shutil.copytree(persist_directory, backup_path)` + 同结构 manifest。

### 9.3 演练记录表

日期、操作人、RTO 实测、发现问题、跟进项。

---

## 综合概念地图

![向量库备份概念地图](image/vector-db-backup/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| manifest | 版本身份证 |
| RPO/RTO | 恢复承诺 |
| 下一篇 | [91 Dense](91.dense-retrieval-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：能否只依赖源文档重建？**
A：可以但慢；索引快照缩短 RTO。

**Q：HNSW 图要单独备吗？**
A：在 index 文件里，write_index 一并备。

**Q：跨版本 FAISS 恢复？**
A：尽量同版本 read_index；大版本测兼容性。

**Q：Chroma 热备？**
A：复制目录前 pause 写或快照文件系统。

**Q：Milvus 跨集群？**
A：见 [77 篇](77.milvus-tutorial.md) 迁移工具。

**Q：备份加密？**
A：对象存储 SSE + 密钥轮换。

**Q：恢复后 ANN 参数？**
A：manifest 记录 efSearch/nprobe，并 [87 回归](87.ann-recall-latency-tutorial.md)。

**Q：面试 30 秒版？**
A：备向量+索引+元数据+manifest；恢复后抽样 Top-k 与 recall。

**Q：与 [48 版本](48.doc-versioning-tutorial.md)？**
A：manifest 绑 doc 版本与 embedding 版本。

**Q：误删 tenant？**
A：分租户备份 + 权限隔离恢复。



---

## 总结与系列下一步

1. 备索引+manifest 不只 PDF；2. 恢复必验证；3. 多租户分路径；4. 季度演练；5. 下一篇 [91 Dense](91.dense-retrieval-tutorial.md)。

### 系列下一步

| 多租户 | [89](89.multi-tenant-namespace-tutorial.md) |
| Dense | [91](91.dense-retrieval-tutorial.md) |
| ANN 评测 | [87](87.ann-recall-latency-tutorial.md) |

### 30 分钟作业

1. 写 manifest；2. 跑 §9 backup/restore；3. 填演练表；4. 勾选 107。

---

> **初学者可能仍困惑的点**
> - 源文档备份不能替代索引备份——re-embed 成本是小时级。
> - manifest 是恢复时的「对照身份证」，缺了易 metric 错乱。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。



## 专精：manifest 字段完整清单

必填：`embedding_model`, `dim`, `metric`, `index_type`, `chunk_count`, `built_at`, `git_sha`（可选）, `ann_params`, `tenant_id`（多租户）, `doc_corpus_version`。

缺任一字段，恢复脚本 **拒绝 mount** 并告警——防止 **默默用错空间**。



## 专精：灾难场景表

| 场景 | 恢复源 |
|------|--------|
| 单文件坏 | 上一版快照 |
| 整个 region 挂 | 跨区冷备 |
| 误删 collection | 版本化对象存储 |
| 仅 manifest 丢 | 禁止启动；从备份取 manifest |

**仅 PDF 源站**：可重建但 RTO 长；索引快照缩短 **小时级** 恢复。



## 专精：备份加密与权限

备份桶 **IAM 最小权限**；加密密钥与数据分权。恢复权限 **高于** 日常读权限，双人复核。多租户备份 **分前缀** `s3://backup/{tenant_id}/`。



## 深化：蓝绿索引切换

绿环境 restore → 回归 → 别名切换 → 24h 后删蓝。manifest 记 `blue_green`。与 [49 增量](49.incremental-update-tutorial.md) 大版本同套路。



## 深化：增量备份

Milvus 增量 snapshot + 周全量。FAISS 日全量。备份前 flush 记 `consistency_point`。


## 附录 A：RPO/RTO 工作表示例

| 等级 | RPO | RTO | 手段 |
|------|-----|-----|------|
| PoC | 24h | 4h | 日备 persist 目录 |
| 生产 | 1h | 30min | 小时快照 + 热备 |
| 金融 | 15min | 15min | 多 AZ + 自动 failover |

## 附录 B：恢复验证 query 包

备份前导出 30 条 `(query_emb, top10_ids)`；恢复后重跑，**Jaccard@10 ≥ 0.9** 为通过线（允许 ANN 微小抖动）。


## 专精：备份频率与成本

| 库规模 | 全量频率 | 保留 |
|--------|----------|------|
| <10 万向量 | 日 | 7 天 |
| 10～100 万 | 日 + 周冷备 | 30 天 |
| >100 万 | 增量小时 + 周全量 | 90 天 |

对象存储 **版本控制** 防误删；manifest 与索引 **同版本 id** 绑定。



## 专精：恢复演练 Runbook 步骤

1. 公告维护窗口  
2. 新环境 restore（勿覆盖生产路径）  
3. hash 校验 manifest  
4. 跑 30 条回归 query  
5. [87] recall 快扫  
6. [88] ACL 渗透  
7. 产品签字切流  
8. 记录实际 RTO  

**季度未演练 = 无真实 RTO**。表格式记每次演练 **实际分钟数**。



## 专精：Chroma / Milvus 备份命令备忘

**Chroma**：停写 → `copytree(persist_directory)` → 上传 S3。  
**Milvus** [77]：Backup API 生成快照路径。  
**FAISS**：`write_index` + `id_map.json` + `manifest.json`。  
**pgvector**：`pg_dump` 含 schema；大表考虑 `pg_basebackup`。

恢复后 **collection 名** 与线上一致或走 **蓝绿切换**（新 collection 验证后改别名）。"""

ARTICLE_91 = """# C4 向量存储（十七）：Dense 稠密检索完全指南

> **Dense 稠密检索** = query 与 chunk 各 embed 成向量，用 **ANN** 找语义近邻——RAG 默认主路。本篇把 [25 Embedding](25.embedding-vector-tutorial.md)、[75 FAISS](75.faiss-ann-tutorial.md)、[84～86 索引](84.flat-brute-force-search-tutorial.md) 收成 **可交付流水线**：embed → 归一化 → 入库 → search → Top-k。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **108** 条）。下一篇 [92 Sparse](92.sparse-retrieval-rag-tutorial.md) 补 **关键词**；再 [93 混合](93.hybrid-search-tutorial.md)。

---

## 目录

1. [前言：语义搜的主路](#1-前言语义搜的主路)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Dense 稠密检索是什么](#3-dense-稠密检索是什么)
4. [Bi-Encoder 与双塔](#4-bi-encoder-与双塔)
5. [RAG 稠密流水线](#5-rag-稠密流水线)
6. [metric 与归一化](#6-metric-与归一化)
7. [Top-k 与 rerank 衔接](#7-top-k-与-rerank-衔接)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：Dense Mini-RAG 端到端](#9-综合实战dense-mini-rag-端到端)
10. [评测与 bad case](#10-评测与-bad-case)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：语义搜的主路

用户问「出差住酒店有啥规定」——BM25 可能漏 **住宿标准** 同义表述；Dense 靠 embedding **语义相近** 召回。

**Bi-Encoder**：query 塔、doc 塔 **分开编码**，离线算 doc 向量，在线只 embed query + ANN——RAG 标准架构。

**读完本文**：画 dense 流水线；跑 §9；说明与 sparse 分工；五种翻车。



### 1.1 路线图位置

```text
107 备份 [90] → 108 Dense ← 本篇 → 109 Sparse [92] → 110 Hybrid [93]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 稠密 | Dense | 固定维向量 |
| 双塔 | Bi-Encoder | query/doc 分开 embed |
| ANN | 近似近邻 | [75 FAISS](75.faiss-ann-tutorial.md) |
| 语义召回 | Semantic retrieval | 同义、改写可捞 |

### 1.3 读完本篇的最小交付物

1. 流水线图；2. §9 可运行；3. metric 说明；4. 与 sparse 对比段；5. §8 翻车。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（108）。** 讲 dense 流水线、Mini-RAG；不讲 contrastive 训练全书 [74](74.contrastive-learning-tutorial.md)。

| 步骤 | 验收 |
|------|------|
| 读 §5 流水线 | 能画 |
| 跑 §9 | Top-3 合理 |
| 对照 §6 | cosine/IP 一致 |



### 2.2 沿用前文

| Embedding | [25](25.embedding-vector-tutorial.md) |
| FAISS | [75](75.faiss-ann-tutorial.md) |
| 索引 | [84][85][86] |

---

## 3. Dense 稠密检索是什么

读下图：chunk 离线 embed 入库；query 在线 embed → ANN。

![Dense 稠密检索是什么](image/dense-retrieval/01-dense-idea.png)

与 [19 BM25](19.bm25-sparse-retrieval-tutorial.md) **稀疏** 相对：dense 向量 **维数固定**（如 768/1024），捕获语义。

弱点：**专有名词、单号、罕见 SKU** 可能不如 BM25——故 [93 混合](93.hybrid-search-tutorial.md)。



---

## 4. Bi-Encoder 与双塔

| 类型 | 编码 | 延迟 | RAG 角色 |
|------|------|------|----------|
| Bi-Encoder | query、doc 各一次 forward | 低（doc 离线） | **召回** |
| Cross-Encoder | query+doc 拼接 | 高 | [95 rerank](95.cross-encoder-rerank-tutorial.md) |

入库：**batch embed** chunks（[67 batching](67.embedding-batching-tutorial.md)、[68 cache](68.embedding-cache-tutorial.md)）。

## 5. RAG 稠密流水线

![稠密检索在 RAG 里怎么走](image/dense-retrieval/02-dense-pipeline.png)

```text
文档 → 分块 [57-64] → embed → 向量库 [76-81] → (query embed → ANN → Top-k)
      → (可选 [93 hybrid]) → (可选 [95 rerank]) → LLM
```

## 6. metric 与归一化

[26 相似度](26.similarity-metrics-tutorial.md) + [66 L2 归一化](66.l2-normalization-tutorial.md)：
- **cosine** 常见实现 = L2 normalize + **内积 IP**；  
- 入库与 query **同一策略**；  
- [87 评测](87.ann-recall-latency-tutorial.md) 与线上一致。

## 7. Top-k 与 rerank

Dense 常 `k=30～100` 宽召回 → [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md) 窄到 5。
k 过大噪音多且挤 [28 context](28.context-window-tutorial.md)——见 [98 Top-K](98.top-k-retrieval-tutorial.md)。

## 10. 评测与 bad case

| bad case | 可能原因 | 方向 |
|----------|----------|------|
| 同义词漏 | 仅 dense | [93 混合](93.hybrid-search-tutorial.md) |
| 单号漏 | 语义弱 | [92 BM25](92.sparse-retrieval-rag-tutorial.md) |
| 全无关 | embed 模型/domain | 换模型 [71](71.domain-embedding-evaluation-tutorial.md) |
| 慢 | ANN 参数 | [87](87.ann-recall-latency-tutorial.md) |

---

## 8. 先错对对：五种典型翻车

### 1. 错：query 用 OpenAI embed、库用 BGE

**对：** 全库单模型

空间不一致。

### 2. 错：不归一化却当 cosine

**对：** L2 norm + IP 或明确 L2

[66 篇](66.l2-normalization-tutorial.md)。

### 3. 错：dense Top-3 直接进 LLM

**对：** k=50 + rerank

召回窄易漏。

### 4. 错：chunk 太大一条 embed

**对：** 合理分块 [57-64]

语义稀释。

### 5. 错：无 [84 Flat](84.flat-brute-force-search-tutorial.md) 评测 ANN

**对：** [87 recall](87.ann-recall-latency-tutorial.md)

漏检不知。



---

## 9. 综合实战：Dense Mini-RAG 端到端

```python
import numpy as np
import faiss
# 假设 embed(text)->np.ndarray shape (dim,)

CHUNKS = [
    {"chunk_id": "c1", "text": "一线城市住宿上限 600 元/晚。"},
    {"chunk_id": "c2", "text": "年假最少 5 天。"},
    {"chunk_id": "c3", "text": "报销需增值税发票。"},
]
texts = [c["text"] for c in CHUNKS]
embs = np.stack([embed(t) for t in texts]).astype("float32")
faiss.normalize_L2(embs)

index = faiss.IndexHNSWFlat(embs.shape[1], 16)
index.add(embs)
id_map = {i: c["chunk_id"] for i, c in enumerate(CHUNKS)}

def dense_search(question: str, k=5):
    q = embed(question).astype("float32").reshape(1, -1)
    faiss.normalize_L2(q)
    _, idx = index.search(q, k)
    return [CHUNKS[i] for i in idx[0]]

print(dense_search("出差酒店标准"))
```

### 9.1 验收

| query | 期望 Top-1 |
|-------|------------|
| 出差酒店标准 | c1 |
| 年假几天 | c2 |

### 9.2 接 Chroma

同 embed 写入 [76 Chroma](76.chroma-vector-db-tutorial.md) `collection.add`，对比 Top-k 一致。

### 9.3 接混合

预留 [92 BM25](92.sparse-retrieval-rag-tutorial.md) 一路 → [93](93.hybrid-search-tutorial.md) → [94 RRF](94.rrf-fusion-tutorial.md)。

---

## 综合概念地图

![稠密检索概念地图](image/dense-retrieval/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| Bi-Encoder | 双塔召回 |
| ANN | 在线近邻 |
| 下一篇 | [92 Sparse](92.sparse-retrieval-rag-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：Dense 能替代 BM25 吗？**
A：不能；专名/SKU 常需 [92](92.sparse-retrieval-rag-tutorial.md) 或 [93 混合](93.hybrid-search-tutorial.md)。

**Q：embed 要 GPU 吗？**
A：PoC CPU；批量入库 GPU 更快 [72](72.local-embedding-inference-tutorial.md)。

**Q：多语言？**
A：[70 混合语言](70.mixed-language-embedding-tutorial.md) 选模型。

**Q：维数 768 vs 1024？**
A：与模型绑定；换模型重建索引。

**Q：本地 vs API embed？**
A：[25](25.embedding-vector-tutorial.md)、[35 API](35.openai-compatible-api-tutorial.md)。

**Q：dense 分数能当阈值吗？**
A：见 [99 阈值](99.score-threshold-tutorial.md)；常先排序。

**Q：与 Cross-Encoder 区别？**
A：dense 召回，cross 精排 [95](95.cross-encoder-rerank-tutorial.md)。

**Q：面试 30 秒版？**
A：双塔 embed+ANN 语义召回；宽 k；与 BM25 混合；metric 归一化一致。

**Q：父文档检索？**
A：[65 parent](65.parent-document-retriever-tutorial.md) child embed parent 拼 prompt。

**Q：缓存 embed？**
A：[68 cache](68.embedding-cache-tutorial.md) 省 API 费。



---

## 总结与系列下一步

1. Dense = embed + ANN 语义主路；2. Bi-Encoder 双塔；3. metric 归一化一致；4. 宽 k + rerank；5. 下一篇 [92 Sparse](92.sparse-retrieval-rag-tutorial.md)。

### 系列下一步

| Sparse | [92](92.sparse-retrieval-rag-tutorial.md) |
| Hybrid | [93](93.hybrid-search-tutorial.md) |
| Embedding | [25](25.embedding-vector-tutorial.md) |

### 30 分钟作业

1. 跑 §9；2. 画流水线；3. 写 dense vs sparse 一段；4. 勾选 108。

---

> **初学者可能仍困惑的点**
> - Dense 不是「理解」——是向量空间距离，模型差则全库差。
> - ANN 近似性要用 [87 篇](87.ann-recall-latency-tutorial.md) 量化，不是 100% 精确。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。



## 专精：与 [92 sparse](92.sparse-retrieval-rag-tutorial.md) 入库并行

同一 ingest job：`embed(chunk)` 写向量库 + `tokenize(chunk)` 写倒排。`chunk_id` 一致。失败一路 **整批重试** 或 DLQ，避免 **只有 dense 无 sparse** 的半成品库。



## 专精：Dense 完整数据流九步

解析→清洗→分块→元数据→embed→归一化→入库→ANN 索引→query ANN。任一步错都像「模型不行」，要分层排查。



## 专精：metric 团队约定

BGE 系：L2 normalize + IP。wiki 写死，review 查 normalize 与 METRIC 成对。



## 专精：业务金标 vs Flat 金标

业务金标测语义相关；[87 Flat](87.ann-recall-latency-tutorial.md) 测 ANN 忠实。两者都过管道才稳。



## 专精：Dense 排查树

Top-k 无关？查 metric、库空、语言、ANN recall、分块。逐枝排除。


## 附录 A：Embedding 选型与 dense 质量 [71 篇](71.domain-embedding-evaluation-tutorial.md)

领域语料（法务、医疗）上对比 **MTEB 榜单分** 与 **本库 Hit@10**。  
换模型 = 新 collection + 全量 embed + [87 重扫 ANN](87.ann-recall-latency-tutorial.md)。

## 附录 B：batch embed 伪代码

```python
def embed_batch(texts, batch_size=32):
    out = []
    for i in range(0, len(texts), batch_size):
        out.extend(model.encode(texts[i:i+batch_size]))
    return np.array(out, dtype="float32")
```

配合 [67 batching](67.embedding-batching-tutorial.md)、[69 限流重试](69.embedding-retry-rate-limit-tutorial.md)。


## 专精：Embedding 模型对照（选型起点）

| 模型 | 维数 | 场景 |
|------|------|------|
| bge-m3 | 1024 | 中文企业默认 |
| text-embedding-3-small | 1536 | OpenAI 生态 |
| multilingual-e5 | 1024 | 多语 |

**manifest** 记录模型 revision；[71 领域评测](71.domain-embedding-evaluation-tutorial.md) 用 **本库金标** 而非只看榜单。



## 专精：入库管道 idempotent

```python
def upsert_chunk(store, chunk_id, text, meta, embed_fn):
    emb = embed_fn(text)
    store.upsert(ids=[chunk_id], embeddings=[emb], documents=[text], metadatas=[meta])
```

幂等键 `chunk_id` [51 篇](51.metadata-chunk-id-tutorial.md)。重试不重复条数。与 [49 增量](49.incremental-update-tutorial.md) 衔接。



## 专精：dense 与 parent-child

[65 Parent-Document](65.parent-document-retriever-tutorial.md)：child 做 dense 检索，parent 拼 prompt。metadata 存 `parent_id`；dense 只 embed child 控制 **粒度**。返回卡片可展示 child snippet。



## 专精：相似度方向自检

首次接入打印：

```python
_, idx = index.search(q, 3)
print("top dist/sim:", scores)
```

确认 **越大越好还是越小越好**（[26 篇](26.similarity-metrics-tutorial.md)）。接反则 Top-k 全错——表现像「dense 完全无效」。



## 专精：延迟预算拆分

| 阶段 | 典型 ms |
|------|---------|
| embed query | 20～80 |
| ANN | 10～50 |
| 取文本 | 5～20 |

dense 检索 SLA 常只包 **ANN**；若 API 报「检索 200ms」，要拆 **embed 是否缓存**（[68 cache](68.embedding-cache-tutorial.md)）。"""

ARTICLE_92 = """# C4 向量存储（十八）：Sparse 稀疏检索（BM25）在 RAG 中完全指南

> 报销单号 **INV-2024-0881**、产品 SKU **XJ-9**——Dense embedding 常 **语义飘**；**BM25 稀疏检索** 靠 **词项匹配** 捞精确命中。基础原理见 [19 BM25](19.bm25-sparse-retrieval-tutorial.md)、[20 倒排](20.inverted-index-tutorial.md)；本篇聚焦 **RAG 里 BM25 站哪、怎么建索引、与 [91 Dense](91.dense-retrieval-tutorial.md) 分工**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **109** 条）。下一篇 [93 混合](93.hybrid-search-tutorial.md) 把两路并起来。

---

## 目录

1. [前言：专名与单号靠 BM25](#1-前言专名与单号靠-bm25)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [稀疏检索在 RAG 中的位置](#3-稀疏检索在-rag-中的位置)
4. [BM25 直觉复习](#4-bm25-直觉复习)
5. [BM25 vs Dense 分工](#5-bm25-vs-dense-分工)
6. [中文分词与索引](#6-中文分词与索引)
7. [与向量库/ES 集成](#7-与向量库es-集成)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：BM25 + Dense 双索引 Mini-RAG](#9-综合实战bm25--dense-双索引-mini-rag)
10. [参数 k1 b 与调优](#10-参数-k1-b-与调优)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：专名与单号靠 BM25

Dense 善 **语义**；BM25 善 **字面与稀有词**——企业手册里的 **制度编号、ERROR 码、人名** 常靠 BM25。

[19 篇](19.bm25-sparse-retrieval-tutorial.md) 已推 BM25 公式；本篇讲 **RAG ingest 建倒排、query 检索、与 dense 并行**。

**读完本文**：BM25 流水线；§9 双索引；分工表；五种翻车。



### 1.1 路线图位置

```text
108 Dense [91] → 109 Sparse ← 本篇 → 110 Hybrid [93]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 稀疏 | Sparse | 高维词项空间 |
| BM25 | Okapi BM25 | 经典 IR 打分 |
| 倒排 | Inverted index | 词→文档列表 [20] |
| 分词 | Tokenization | 中文 jieba 等 |

### 1.3 读完本篇的最小交付物

1. 倒排建库脚本；2. BM25 vs dense 表；3. §9 双路；4. 分词说明；5. §8 翻车。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（109）。** 讲 RAG 中 BM25 落地；不重推 IDF 全书（见 [19](19.bm25-sparse-retrieval-tutorial.md)）。

| 步骤 | 验收 |
|------|------|
| 读 §5 分工 | 能举例 |
| 跑 §9 | 单号 query BM25 赢 |
| 接 [93](93.hybrid-search-tutorial.md) | 双路 list 可合并 |



### 2.2 沿用前文

| BM25 原理 | [19](19.bm25-sparse-retrieval-tutorial.md) |
| 倒排 | [20](20.inverted-index-tutorial.md) |
| Dense | [91](91.dense-retrieval-tutorial.md) |

---

## 3. 稀疏检索在 RAG 中的位置

读下图：与 dense 并行，汇入 [93 混合](93.hybrid-search-tutorial.md) 或 [94 RRF](94.rrf-fusion-tutorial.md)。

![稀疏检索在 RAG 里站哪](image/sparse-retrieval-rag/01-sparse-rag.png)

每条 chunk 入库时：**一路 embed**（dense），**一路进倒排**（sparse）。

query 时：**两路各 Top-k** → 融合 → rerank → LLM。



---

## 4. BM25 直觉复习

见 [19 篇](19.bm25-sparse-retrieval-tutorial.md)：词频饱和、文档长度归一、稀有词加权。
RAG chunk 较短时 **单 chunk 词频低**——BM25 仍靠 **稀有词命中** 区分。

## 5. BM25 vs Dense

![BM25 与 Dense 怎么分工](image/sparse-retrieval-rag/02-bm25-vs-dense.png)

| 场景 | BM25 | Dense |
|------|------|-------|
| 单号/SKU | 强 | 弱 |
| 同义改写 | 弱 | 强 |
| 中英混合专名 | 中 | 中 |
| 长语义问 | 弱 | 强 |

## 6. 中文分词

[路线图 24](ENTERPRISE_RAG_ROADMAP.md) 中文分词：jieba、pkuseg 等；**入库与 query 同一分词器**。
英文可空格；**不要** 入库 ik 分词、query 另一套。

## 7. 集成方式

| 方案 | 说明 |
|------|------|
| rank_bm25 内存 | PoC 万级 |
| Elasticsearch [82] | 同栈 BM25+knn |
| OpenSearch [83] | 混合原生 |
| 外挂倒排 + FAISS | 自研双索引 |

## 10. 参数 k1、b

Lucene 默认 k1=1.2, b=0.75；短 chunk 可略调。**用金标 query 网格搜索**，不要照搬论文。

---

## 8. 先错对对：五种典型翻车

### 1. 错：只有 dense 无 BM25

**对：** 企业 RAG 默认考虑混合 [93]

单号类 bad case 多。

### 2. 错：BM25 与 dense 分数直接相加

**对：** [94 RRF](94.rrf-fusion-tutorial.md)

量纲不同。

### 3. 错：分词不一致

**对：** 统一 tokenizer

索引与 query 词项对不上。

### 4. 错：倒排不更 chunk 版本

**对：** 随 [48 版本](48.doc-versioning-tutorial.md) 重建

删旧留新。

### 5. 错：BM25 全库无 filter

**对：** 同 [88 filter](88.metadata-filter-retrieval-tutorial.md)

越权风险。



---

## 9. 综合实战：BM25 + Dense 双索引 Mini-RAG

```python
from rank_bm25 import BM25Okapi
import jieba
import numpy as np
import faiss

CHUNKS = [
    {"chunk_id": "c1", "text": "发票号 INV-2024-0881 已入账。"},
    {"chunk_id": "c2", "text": "年假申请流程见员工手册第二章。"},
]
tokenized = [list(jieba.cut(c["text"])) for c in CHUNKS]
bm25 = BM25Okapi(tokenized)

embs = np.stack([embed(c["text"]) for c in CHUNKS]).astype("float32")
faiss.normalize_L2(embs)
dense_idx = faiss.IndexFlatIP(embs.shape[1])
dense_idx.add(embs)

def sparse_search(q, k=5):
    tokens = list(jieba.cut(q))
    scores = bm25.get_scores(tokens)
    top = np.argsort(scores)[::-1][:k]
    return [CHUNKS[i] for i in top]

def dense_search(q, k=5):
    qv = embed(q).astype("float32").reshape(1, -1)
    faiss.normalize_L2(qv)
    _, idx = dense_idx.search(qv, k)
    return [CHUNKS[i] for i in idx[0]]

# 单号 query → sparse 应 Top-1 为 c1
print(sparse_search("INV-2024-0881"))
print(dense_search("年假怎么请"))
```

### 9.1 验收

| query | sparse | dense |
|-------|--------|-------|
| INV-2024-0881 | c1 | 不一定 |
| 年假怎么请 | 可能 c2 | c2 |

### 9.2 接 RRF

两路结果送 [94 RRF](94.rrf-fusion-tutorial.md)，不要分数相加。

### 9.3 metadata

倒排文档 id 用 **chunk_id**，与 dense id_map 一致，便于去重。

---

## 综合概念地图

![稀疏检索 RAG 概念地图](image/sparse-retrieval-rag/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| BM25 | 词项匹配 [19] |
| 倒排 | [20 篇](20.inverted-index-tutorial.md) |
| 下一篇 | [93 Hybrid](93.hybrid-search-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：BM25 要分词吗？**
A：中文要；与 query 一致。

**Q：chunk 太短 BM25 有用吗？**
A：稀有词仍有效；极短可降 b。

**Q：ES 里 BM25 字段？**
A：text 类型 + 标准分析器 [82]。

**Q：能否只用 OpenSearch 混合？**
A：见 [83 篇](83.opensearch-hybrid-tutorial.md)，省自研双索引。

**Q：BM25 要 filter 吗？**
A：同 dense，[88 篇](88.metadata-filter-retrieval-tutorial.md)。

**Q：IVF 倒排和 BM25 倒排？**
A：同名不同物 [85 篇](85.ivf-index-tutorial.md)。

**Q：多语言 BM25？**
A：按字段语言选 analyzer。

**Q：面试 30 秒版？**
A：BM25 捞专名字面；dense 捞语义；RRF 融合；分词一致。

**Q：rank_bm25 上限？**
A：万级 PoC；大库 ES/OpenSearch。

**Q：与 [91 dense](91.dense-retrieval-tutorial.md) 谁先做？**
A：入库两路并行。



---

## 总结与系列下一步

1. BM25 补 dense 专名短板；2. 双索引并行；3. 分词一致；4. RRF 融合非加分数；5. 下一篇 [93 混合](93.hybrid-search-tutorial.md)。

### 系列下一步

| BM25 原理 | [19](19.bm25-sparse-retrieval-tutorial.md) |
| Hybrid | [93](93.hybrid-search-tutorial.md) |
| RRF | [94](94.rrf-fusion-tutorial.md) |

### 30 分钟作业

1. 跑 §9；2. 填分工表；3. 单号 case 截图；4. 勾选 109。

---

> **初学者可能仍困惑的点**
> - BM25 不是「旧技术」——企业 RAG 仍常需要。
> - 稀疏与稠密倒排（IVF）名字像，完全不是一回事。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。



## 专精：sparse 路监控

指标：`sparse_hit_rate`（金标 query 中 Top-30 是否含相关）、`sparse_latency_ms`。若 hit_rate 低而 dense 高，仍可能需要混合；若 **单号 query sparse 也低**，查分词/词典/倒排是否含该词。



## 专精：谁赢谁输归因表

维护表格列：`query, winner_channel, reason`。复盘时统计 **BM25 独赢比例**——若 <5%，可能 hybrid 收益有限；若 >30%，混合必要性强。



## 专精：rank_bm25 边界

万级够用；十万级迁 ES [82][83]。迁移保持 **同一分词词典**。



## 专精：BM25 与清洗

[46 清洗](46.text-cleaning-tutorial.md) 后再进倒排；HTML/MD 去标签。表格转文本后 BM25 常优于纯 dense。



## 专精：query 预处理

与入库同分词器；记录 query_tokens 与 posting 交集诊断空结果。


## 附录 A：Elasticsearch BM25 映射片段 [82 篇](82.elasticsearch-vector-tutorial.md)

```json
{"mappings": {"properties": {
  "text": {"type": "text", "analyzer": "ik_max_word"},
  "chunk_id": {"type": "keyword"},
  "embedding": {"type": "dense_vector", "dims": 768}
}}}
```

混合查询同索引 BM25 + knn；filter 走 bool filter。

## 附录 B：停用词与专名

企业 SKU、单号 **不要进停用词表**；否则 BM25 无法命中。


## 专精：倒排更新策略

| 事件 | 动作 |
|------|------|
| 新 chunk | add posting |
| 删 chunk | delete posting |
| 改文本 | delete + add |
| 全量重索引 | 新索引切换 |

与 [48 版本](48.doc-versioning-tutorial.md) 绑定；旧版 chunk 从倒排 **物理删除**，防 BM25 命中过时政策。



## 专精：中文分词选型

| 工具 | 特点 |
|------|------|
| jieba | 快、PoC 够用 |
| pkuseg | 领域模型 |
| ES ik | 生产 ES 栈 |

**自定义词典**：加入公司产品名、内部缩写，提升 BM25 命中。词典 **版本化** 与索引 rebuild 同步。



## 专精：BM25 短 chunk 注意

chunk 50 字以内，IDF 仍有效但 **TF 低**。勿过度增大 `b` 惩罚长度；短 FAQ 块是 RAG 常态。用金标调 `k1,b`，不要照搬 Lucene 默认而不测。



## 专精：OpenSearch 双写

[83 篇](83.opensearch-hybrid-tutorial.md)：单文档含 `text` + `embedding`，省 **双索引同步**。ACL 用同一 filter。PoC 自研双索引（FAISS+rank_bm25）迁移 ES 时 **对比 Top-10 一致性**。"""

ARTICLE_93 = """# C4 向量存储（十九）：混合检索 Hybrid Search 完全指南

> 单靠 [91 Dense](91.dense-retrieval-tutorial.md) 漏单号，单靠 [92 BM25](92.sparse-retrieval-rag-tutorial.md) 漏同义——**混合检索 Hybrid Search** 让 **稠密路 + 稀疏路** 各出 Top-k，再用 **[94 RRF](94.rrf-fusion-tutorial.md)** 或引擎原生融合。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 主线篇**（路线图第 **110** 条）。前置：[91 Dense](91.dense-retrieval-tutorial.md)、[92 Sparse](92.sparse-retrieval-rag-tutorial.md)、[83 OpenSearch](83.opensearch-hybrid-tutorial.md)。

---

## 目录

1. [前言：为什么要两路召回](#1-前言为什么要两路召回)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [混合检索是什么](#3-混合检索是什么)
4. [架构模式](#4-架构模式)
5. [双路 pipeline 设计](#5-双路-pipeline-设计)
6. [融合层：RRF 与替代](#6-融合层rrf-与替代)
7. [过滤与去重](#7-过滤与去重)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：Hybrid Mini-RAG 端到端](#9-综合实战hybrid-mini-rag-端到端)
10. [OpenSearch/ES 原生混合](#10-opensearches-原生混合)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么要两路召回

真实 bad case：**一半** 靠 BM25 救，**一半** 靠向量救——混合是 **企业 RAG 默认架构**（在算力允许下）。

Hybrid ≠ 把两分数相加；**量纲不同**，用 **RRF 按名次融合** 或 **learned rerank** [95](95.cross-encoder-rerank-tutorial.md)。

**读完本文**：三种架构；§9 端到端；同 filter 双路；五种翻车。



### 1.1 路线图位置

```text
109 Sparse [92] → 110 Hybrid ← 本篇 → 111 RRF [94]
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 混合检索 | Hybrid Search | 多路召回 |
| 稠密路 | Dense channel | 向量 ANN |
| 稀疏路 | Sparse channel | BM25 |
| 融合 | Fusion | RRF 等 |

### 1.3 读完本篇的最小交付物

1. 架构图；2. §9 可运行 hybrid；3. bm25_k/dense_k 配置；4. 去重逻辑；5. §8 翻车。

---

## 2. 本文边界与动手路径

**档位：C4 主线篇（110）。** 讲双路+融合衔接；不讲 learning-to-rank 训练全书。

| 步骤 | 验收 |
|------|------|
| 读 §4 架构 | 能选型 |
| 跑 §9 | 融合 Top-5 |
| 同 filter | 双路 where 一致 |



### 2.2 沿用前文

| Dense | [91](91.dense-retrieval-tutorial.md) |
| Sparse | [92](92.sparse-retrieval-rag-tutorial.md) |
| RRF | [94](94.rrf-fusion-tutorial.md) |

---

## 3. 混合检索是什么

读下图：query 分叉 → dense + sparse → fusion → 候选池。

![混合检索是什么](image/hybrid-search/01-hybrid-idea.png)

**目标**：同一条 user query，**最大化**「任一路能捞到真相关 chunk」的概率。

典型配置：`bm25_k=30`, `dense_k=30`, 融合后 `recall_k=50` → [95 rerank](95.cross-encoder-rerank-tutorial.md) → 5。



---

## 4. 架构模式

![混合检索有哪些架构](image/hybrid-search/02-hybrid-arch.png)

| 模式 | 描述 | 适用 |
|------|------|------|
| 双索引自研 | FAISS + BM25 内存/ES | 灵活、PoC→中小 |
| ES/OpenSearch 原生 | 单集群 knn+BM25 [82][83] | 运维已有 ES |
| 向量库 + 外挂 BM25 | Milvus + ES | 大规模拆分 |
| 多查询增强 | [101 多查询](101.multi-query-retrieval-tutorial.md) 再混合 | 难 query |

## 5. 双路 pipeline

```text
query → (可选 [100 改写])
      ├→ dense: embed → ANN(k=30) → list_D
      └→ sparse: tokenize → BM25(k=30) → list_S
      → [94 RRF](94.rrf-fusion-tutorial.md)(list_D, list_S) → dedupe → Top-50
      → [95 rerank](95.cross-encoder-rerank-tutorial.md) → Top-5 → LLM
```

## 6. 融合层

默认 **[94 RRF](94.rrf-fusion-tutorial.md)**；加权平均仅当 **分数已校准**（少见）。
ES hybrid 可能内置 RRF——见 [83 篇](83.opensearch-hybrid-tutorial.md)。

## 7. 过滤与去重

- **同 filter**：[88 篇](88.metadata-filter-retrieval-tutorial.md) 双路必须一致。  
- **dedupe**：同一 `chunk_id` 只留 **RRF 分最高** 一条。  
- **parent-child**：[65 篇](65.parent-document-retriever-tutorial.md) 去重策略。

## 10. OpenSearch/ES

[83 OpenSearch](83.opensearch-hybrid-tutorial.md)：单请求 hybrid query，省自研 orchestration。
仍要 **ACL filter** 与 **评测金标**。

---

## 8. 先错对对：五种典型翻车

### 1. 错：BM25 分 + cosine 分加权

**对：** [94 RRF](94.rrf-fusion-tutorial.md)

量纲不可比。

### 2. 错：两路 filter 不一致

**对：** 同一 where/expr

融合掺越权。

### 3. 错：融合不去重

**对：** 按 chunk_id dedupe

同一 chunk 占多槽。

### 4. 错：recall_k=3 做 hybrid

**对：** 各路 30 融合到 50

窄召回失去混合意义。

### 5. 错：只 hybrid 不 rerank

**对：** 宽融合 + cross 精排

顺序仍可能差。



---

## 9. 综合实战：Hybrid Mini-RAG 端到端

```python
def rrf_merge(lists, k=60, top_n=50):
    scores = {}
    for lst in lists:
        for rank, item in enumerate(lst, start=1):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank)
    id_to = {c["chunk_id"]: c for lst in lists for c in lst}
    merged = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
    return [id_to[cid] for cid, _ in merged]

def hybrid_search(query, bm25_k=30, dense_k=30):
    d = dense_search(query, dense_k)
    s = sparse_search(query, bm25_k)
    return rrf_merge([d, s], top_n=50)

QUERY = "INV-2024-0881 入账规则"
candidates = hybrid_search(QUERY)
# → rerank → prompt
```

### 9.1 配置表

| 参数 | 建议起点 |
|------|----------|
| bm25_k | 30 |
| dense_k | 30 |
| rrf_k | 60 |
| recall_k | 50 |
| final_k | 5 |

### 9.2 验收

| query 类型 | 期望 |
|------------|------|
| 单号 | sparse 路贡献 |
| 口语语义 | dense 路贡献 |
| 复合 | 两路皆有 |

### 9.3 日志

记录 `list_D_ids`, `list_S_ids`, `merged_ids`——bad case 归因。

### 9.4 与 [28 context](28.context-window-tutorial.md)

final_k 条进 prompt 前算 token 预算。

---

## 综合概念地图

![混合检索概念地图](image/hybrid-search/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| 双路 | dense+sparse |
| RRF | [94 篇](94.rrf-fusion-tutorial.md) |
| 下一篇 | [95 rerank](95.cross-encoder-rerank-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：混合一定比单路好吗？**
A：金标上测；小库/simple domain 可能不必。

**Q：一路失败另一路补？**
A：是设计目标；仍要单路监控。

**Q：三路呢？**
A：可加 [102 HyDE](102.hyde-tutorial.md) 等，多路 RRF。

**Q：延迟翻倍怎么办？**
A：并行两路；降 k；用原生 ES hybrid。

**Q：Chroma 能 BM25 吗？**
A：原生弱；外挂 ES 或 rank_bm25。

**Q：Milvus 混合？**
A：常 Milvus dense + ES BM25。

**Q：融合后能再阈值吗？**
A：[99 篇](99.score-threshold-tutorial.md) 对 rerank 分。

**Q：面试 30 秒版？**
A：dense 语义+BM25 专名；并行召回；RRF 融合；同 filter；dedupe；rerank。

**Q：与 [83](83.opensearch-hybrid-tutorial.md)？**
A：托管混合省自研 orchestration。

**Q：评测指标？**
A：Recall@k/MRR 金标 + 分路命中归因。



---

## 总结与系列下一步

1. Hybrid = 双路各宽召回；2. RRF 融合非加分数；3. 同 filter + dedupe；4. 再 rerank；5. 下一篇详 [94 RRF](94.rrf-fusion-tutorial.md)。

### 系列下一步

| RRF | [94](94.rrf-fusion-tutorial.md) |
| Rerank | [95](95.cross-encoder-rerank-tutorial.md) |
| OpenSearch | [83](83.opensearch-hybrid-tutorial.md) |

### 30 分钟作业

1. 跑 §9；2. 配 YAML 参数；3. 两例 bad case 归因；4. 勾选 110。

---

> **初学者可能仍困惑的点**
> - 混合是召回层宽，精排层仍要 [95](95.cross-encoder-rerank-tutorial.md)。
> - 两路 k 太小则混合失去意义——先宽再窄。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。



## 专精：并行与超时

```python
def hybrid_with_timeout(q, timeout_s=2.0):
    ...
```

任一路超时 **降级为单路** 并 metrics 打点 `hybrid_degraded`。产品决定降 dense 还是 sparse——通常 **保留 BM25** 保单号，语义问保留 dense。写进 runbook。



## 专精：多查询 + Hybrid

[101 多查询](101.multi-query-retrieval-tutorial.md) 生成 q1,q2,q3，每 query 跑 hybrid，再 **多路 RRF**（[94](94.rrf-fusion-tutorial.md)）。注意 **总延迟** 与 [28 context](28.context-window-tutorial.md) 预算；不是 query 越多越好。



## 专精：评测：分路贡献率

金标 50 条，标 `relevant_chunk`。统计：

- 仅 dense Top-50 命中  
- 仅 sparse Top-50 命中  
- 两路都命中  
- 都未命中（需 query 增强或 chunk 问题）  

**都未命中** >10% 先修召回，勿先加 rerank。



## 专精：去重与分数保留

dedupe 时保留 **较高 RRF 分** 的路信息 `source_channels: ["dense","sparse"]`，方便前端展示「关键词+语义」双命中徽章——产品可选。进 rerank 只传 **text + chunk_id**。



## 专精：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 串联契约

接口：`List[ChunkCandidate]` 字段统一 `chunk_id, text, metadata, fusion_rank`。rerank 不改 chunk_id 集合，只改序。契约测试防 **融合后字段丢失** 导致引用断裂。



## 专精：Hybrid 一周计划

Mon dense 金标 → Tue sparse → Wed RRF → Thu filter → Fri rerank。每日固定 20 条看 MRR 增量。



## 专精：延迟优化顺序

并行双路 → 降 k → embed 缓存 → ES 原生 hybrid → GPU ANN。先修 recall 再大 rerank。



## 专精：法务场景

条款号 BM25 + 语义 dense；filter doc_type；引用 [34 grounding](34.grounding-citation-tutorial.md)。


## 附录 A：并行双路伪代码

```python
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(2) as ex:
    fd = ex.submit(dense_search, q, 30)
    fs = ex.submit(sparse_search, q, 30)
    return rrf_merge([fd.result(), fs.result()])
```

IO 型 BM25 与 CPU/GPU embed 可并行降延迟。

## 附录 B：Hybrid 参数 YAML

```yaml
hybrid:
  bm25_k: 30
  dense_k: 30
  rrf_k: 60
  recall_k: 50
rerank:
  final_k: 5
```


## 专精：Hybrid 架构选型工作坊

问团队四个问题：1) 是否已有 ES？2) 数据量级？3) 运维人数？4) 延迟 SLO？  
有 ES 且 <500 万文档 → [83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md) 优先。无 ES、快速 PoC → FAISS+rank_bm25。>千万、QPS 高 → Milvus+Qdrant dense + ES sparse 分拆。

**记录 ADR**（Architecture Decision Record）一页纸存档。"""

ARTICLE_94 = """# C4 向量存储（二十）：RRF 倒数排名融合完全指南

> [93 混合检索](93.hybrid-search-tutorial.md) 双路各出一串 **chunk_id**——BM25 分 12.3、cosine 0.87 **不能直接加**。**RRF**（Reciprocal Rank Fusion，倒数排名融合）只看得分 **名次**：`RRF(d) = Σ 1/(k + rank_i(d))`，无参、稳健，是 **多路召回合并的默认首选**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **111** 条）。前置：[93 Hybrid](93.hybrid-search-tutorial.md)、[91 Dense](91.dense-retrieval-tutorial.md)、[92 Sparse](92.sparse-retrieval-rag-tutorial.md)。精排仍用 [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)，RRF **不替代** rerank。

---

## 目录

1. [前言：为什么不能加分数](#1-前言为什么不能加分数)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [RRF 直觉](#3-rrf-直觉)
4. [RRF 公式与参数 k](#4-rrf-公式与参数-k)
5. [多路列表合并实现](#5-多路列表合并实现)
6. [与加权、CombSUM 对照](#6-与加权combsum-对照)
7. [去重与 tie-break](#7-去重与-tie-break)
8. [先错对对：五种典型翻车](#8-先错对对五种典型翻车)
9. [综合实战：RRF + Hybrid Mini-RAG](#9-综合实战rrf--hybrid-mini-rag)
10. [ES/OpenSearch 中的 RRF](#10-esopensearch-中的-rrf)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么不能加分数

BM25 无界、cosine 在 0～1——加权 `0.5*bm25 + 0.5*cosine` **权重难调、域间不稳**。

RRF 只看 **排名第几**：两路都认为靠前的 doc **累加倒数分**，只出现在一路的也能进榜。

**读完本文**：手写 RRF；调 k；三路融合；五种翻车。



### 1.1 路线图位置

```text
110 Hybrid [93] → 111 RRF ← 本篇 → 112+ 生成与 Grounding
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 倒数排名融合 | RRF | Reciprocal Rank Fusion |
| 平滑常数 | k (RRF) | 常取 60 |
| 名次 | Rank | 1-based 排名 |
| CombSUM | 分数相加 | 需归一化 |

### 1.3 读完本篇的最小交付物

1. RRF 函数；2. k=60 实验记录；3. 与加权和对比表；4. §9 端到端；5. §8 翻车。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（111）。** 讲 RRF 公式与实现；不讲 LTR 训练。

| 步骤 | 验收 |
|------|------|
| 读 §4 公式 | 能手算 2 路 |
| 跑 §9 | 融合序合理 |
| 调 k | 有对比 |



### 2.2 沿用前文

| Hybrid | [93](93.hybrid-search-tutorial.md) |
| BM25 | [92](92.sparse-retrieval-rag-tutorial.md) |
| Rerank | [95](95.cross-encoder-rerank-tutorial.md) |

---

## 3. RRF 直觉

读下图：两路排名榜合并为 RRF 总分榜。

![RRF 融合是什么](image/rrf-fusion/01-rrf-idea.png)

doc A：dense 第 1、sparse 第 8 → 两路都贡献。

doc B：仅 BM25 第 1、dense 未进 Top-30 → 仍可能靠 sparse 名次进融合榜。



---

## 4. RRF 公式与参数 k

![RRF 公式怎么算](image/rrf-fusion/02-rrf-formula.png)

对文档 d，路 i 中名次 rank_i(d)（未出现则跳过）：

`RRF_score(d) = Σ_i 1 / (k + rank_i(d))`

**k** 常用 **60**（论文/ES 默认量级）；k 大 → 名次靠后仍有分；k 小 → 只重 Top。

```python
def rrf_score(ranks: list[int], k: int = 60) -> float:
    return sum(1.0 / (k + r) for r in ranks)
```

## 5. 多路实现

```python
def rrf_fuse(ranked_lists: list[list[str]], k=60, top_n=50):
    scores = {}
    for lst in ranked_lists:
        for rank, doc_id in enumerate(lst, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])[:top_n]
```

输入为 **chunk_id 列表**（每路已按该路分数排好）。

## 6. 与加权对照

| 方法 | 优点 | 缺点 |
|------|------|------|
| RRF | 无参、稳健 | 不利用绝对分 |
| 加权和 | 可用分差距 | 要归一化+调权 |
| CombMNZ | 多路命中奖励 | 仍要分数量纲 |

企业 PoC **默认 RRF**；有大规模标注再考虑 learned fusion。

## 7. 去重与 tie-break

同 chunk 只计 **一路最高名次** 或 **累加多路**——标准 RRF **累加各路人选**。
tie-break：RRF 分相同比 **最佳单路名次** 或 **dense 分**。

## 10. ES/OpenSearch

[83 篇](83.opensearch-hybrid-tutorial.md) hybrid 查询可内置 RRF；自研栈用 §5 函数即可。

---

## 8. 先错对对：五种典型翻车

### 1. 错：BM25 与 cosine 直接加权

**对：** RRF 按名次

量纲不可比。

### 2. 错：rank 从 0 开始

**对：** 1-based rank

公式分母错。

### 3. 错：未排序列表就 RRF

**对：** 每路先按该路分数降序

名次无意义。

### 4. 错：RRF 后不再 rerank

**对：** RRF→recall_k→cross 精排

RRF 只合并召回。

### 5. 错：三路 k 不同不记录

**对：** 日志每路 Top 名单

无法归因。



---

## 9. 综合实战：RRF + Hybrid Mini-RAG

```python
def hybrid_rrf(query, bm25_k=30, dense_k=30, rrf_k=60, out_k=50):
    dense_list = dense_search(query, dense_k)   # 已按相似度排序
    sparse_list = sparse_search(query, bm25_k)
    def ids(lst):
        return [c["chunk_id"] for c in lst]
    fused = rrf_fuse([ids(dense_list), ids(sparse_list)], k=rrf_k, top_n=out_k)
    id_map = {c["chunk_id"]: c for c in dense_list + sparse_list}
    return [id_map[cid] for cid, _ in fused if cid in id_map]

# 验收：单号 query 中 sparse-only 的 chunk 应进 fused Top-50
# 验收：语义 query 中 dense-only 的 chunk 应进 fused Top-50
```

### 9.1 k 敏感性

| rrf_k | 现象 |
|-------|------|
| 10 | 偏 Top-heavy |
| 60 | 默认平衡 |
| 120 | 后路名次权重更大 |

用 **20 条金标** 比 MRR@10 选 k。

### 9.2 三路 RRF

可加 [101 多查询](101.multi-query-retrieval-tutorial.md) 第三路 list。

### 9.3 接 rerank

`candidates = hybrid_rrf(q)` → `bge_rerank(q, candidates)[:5]`

### 9.4 Review

- [ ] 每路输入已排序  
- [ ] chunk_id 去重策略文档化  
- [ ] 与 [88 filter](88.metadata-filter-retrieval-tutorial.md) 双路一致

---

## 综合概念地图

![RRF 融合概念地图](image/rrf-fusion/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| RRF | 倒数名次和 |
| k=60 | 常用平滑 |
| 下一篇 | [95 rerank](95.cross-encoder-rerank-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：RRF 的 k 和 ANN 的 k 一样吗？**
A：完全不同；RRF k 是平滑常数 60。

**Q：一路只有 5 条能 RRF 吗？**
A：能；另一路可 30 条。

**Q：同 doc 两路名次都差？**
A：RRF 分低，可能仍被 rerank 救或拒答。

**Q：RRF 能代替 hybrid 吗？**
A：不能；RRF 是融合，hybrid 是双路架构 [93]。

**Q：ES RRF 参数？**
A：见 [83 篇](83.opensearch-hybrid-tutorial.md)。

**Q：要保存 RRF 分吗？**
A：日志可选；下游以 rerank 为准。

**Q：多语言三路？**
A：每路同 filter；RRF 无语言假设。

**Q：面试 30 秒版？**
A：多路按名次算 1/(k+rank) 求和；k≈60；替代不可比分数相加。

**Q：与 CombSUM？**
A：RRF 更省心；CombSUM 要归一化。

**Q：零结果一路？**
A：另一路仍可贡献文档。



---

## 总结与系列下一步

1. RRF = 名次融合，不加原始分；2. k≈60 起点；3. 每路先排序；4. 后接 rerank；5. 下一篇 [95 精排](95.cross-encoder-rerank-tutorial.md)。

### 系列下一步

| Hybrid | [93](93.hybrid-search-tutorial.md) |
| Rerank | [95](95.cross-encoder-rerank-tutorial.md) |
| OpenSearch | [83](83.opensearch-hybrid-tutorial.md) |

### 30 分钟作业

1. 实现 §5 rrf_fuse；2. 扫 k=10/60/120；3. 接 §9 hybrid；4. 勾选 111。

---

> **初学者可能仍困惑的点**
> - RRF 分不要和 BM25 分比大小——只用于融合排序。
> - 融合宽（50）与进 LLM 窄（5）是两档 k。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。



## 专精：三路 RRF 示例

```python
lists = [dense_ids, sparse_ids, hyde_dense_ids]
fused = rrf_fuse(lists, k=60, top_n=50)
```

[102 HyDE](102.hyde-tutorial.md) 路可能与 dense 重叠多——RRF 自然 **奖励多路共识**。



## 专精：RRF vs 加权 实验记录模板

| 方法 | MRR@10 | NDCG@10 | 调参成本 |
|------|--------|---------|----------|
| RRF k=60 | | | 低 |
| 0.5 BM25 + 0.5 cos | | | 高（归一化） |

PoC 填表一次即可说服团队 **默认 RRF**。



## 专精：名次并列处理

同一路内 BM25 分数相同 → 按 `chunk_id` 字典序稳定排序，再赋 rank。避免 **随机序** 导致 RRF 抖动与 A/B 不可复现。



## 专精：ES RRF 参数

[83 OpenSearch](83.opensearch-hybrid-tutorial.md) hybrid 查询 `rank_constant` 对应 RRF k。自研与 ES **同一 k** 时结果应近似（索引相同前提下）。



## 专精：融合后空池

两路都未返结果 → 直接拒答或触发 [100 改写](100.query-rewriting-tutorial.md)，勿 RRF 空列表。监控 `fusion_empty_count`。



## 专精：RRF 变体

加权 RRF、CombSUM 对比；PoC 默认标准 RRF。与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分工：RRF 并路，rerank 精语义。



## 专精：RRF 日志 JSON

记 dense_rank、sparse_rank、rrf_score、final_order 脱敏复盘。GDPR 注意 query 保留策略。



## 专精：RRF 单测

```python
def test_rrf():
    out = rrf_fuse([["c1","c2"], ["c3","c1"]], k=60, top_n=2)
    assert out[0][0] in ("c1",)
```

CI 防 rank off-by-one。


## 附录 A：手算 RRF 两路例子

k=60。doc X：dense 第1、sparse 第3 → `1/61 + 1/63 ≈ 0.0323`。  
doc Y：仅 dense 第2 → `1/62 ≈ 0.0161`。X 排前。

## 附录 B：与 [95 rerank](95.cross-encoder-rerank-tutorial.md) 分数分工

| 阶段 | 输出 | 用途 |
|------|------|------|
| RRF | 融合序 recall_k=50 | 宽候选 |
| Cross-Encoder | rerank_score | 窄 Top-5 进 LLM |

不要把 RRF 分送入 LLM 当「置信度」——未校准。


## 专精：RRF k 网格实验

| rrf_k | MRR@10 变化 | 备注 |
|-------|-------------|------|
| 10 | 偏榜首 | 忽略后路深排 |
| 60 | 基线 | 文献常见 |
| 120 | 后路权重升 | 稀疏独赢 doc 受益 |

用 **本库金标** 选 k，不要迷信 60。记录进参数 YAML（[93 hybrid](93.hybrid-search-tutorial.md) 配置旁）。"""

ARTICLES_REST = [
    ('87.ann-recall-latency-tutorial.md', ARTICLE_87, {'slug': 'ann-recall-latency', 'roadmap': 104, 'title': 'ANN 召回率与延迟权衡完全指南', 'images': [('01-recall-latency.png', '§3 Recall 与延迟', 'hub-spoke', '召回率与延迟怎么权衡'), ('02-benchmark-curve.png', '§6 评测曲线', 'comparison-matrix', 'ANN 评测曲线怎么读'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', 'ANN 召回延迟概念地图')]}),
    ('88.metadata-filter-retrieval-tutorial.md', ARTICLE_88, {'slug': 'metadata-filter-retrieval', 'roadmap': 105, 'title': 'Metadata Filter 过滤检索完全指南', 'images': [('01-filter-idea.png', '§3 过滤检索', 'hub-spoke', '元数据过滤检索是什么'), ('02-pre-post-filter.png', '§5 前滤后滤', 'comparison-matrix', '前滤 vs 后滤怎么选'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', '元数据过滤概念地图')]}),
    ('89.multi-tenant-namespace-tutorial.md', ARTICLE_89, {'slug': 'multi-tenant-namespace', 'roadmap': 106, 'title': '多租户 Namespace 隔离完全指南', 'images': [('01-tenant-idea.png', '§3 多租户', 'hub-spoke', '多租户向量库怎么隔离'), ('02-isolation-patterns.png', '§5 隔离模式', 'comparison-matrix', 'Namespace vs Collection 怎么选'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', '多租户隔离概念地图')]}),
    ('90.vector-db-backup-tutorial.md', ARTICLE_90, {'slug': 'vector-db-backup', 'roadmap': 107, 'title': '向量库备份与恢复完全指南', 'images': [('01-backup-idea.png', '§3 备份什么', 'hub-spoke', '向量库要备份什么'), ('02-restore-flow.png', '§6 恢复流程', 'comparison-matrix', '备份恢复流程怎么走'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', '向量库备份概念地图')]}),
    ('91.dense-retrieval-tutorial.md', ARTICLE_91, {'slug': 'dense-retrieval', 'roadmap': 108, 'title': 'Dense 稠密检索完全指南', 'images': [('01-dense-idea.png', '§3 稠密检索', 'hub-spoke', 'Dense 稠密检索是什么'), ('02-dense-pipeline.png', '§5 RAG 流水线', 'comparison-matrix', '稠密检索在 RAG 里怎么走'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', '稠密检索概念地图')]}),
    ('92.sparse-retrieval-rag-tutorial.md', ARTICLE_92, {'slug': 'sparse-retrieval-rag', 'roadmap': 109, 'title': 'Sparse 稀疏检索（BM25）在 RAG 中完全指南', 'images': [('01-sparse-rag.png', '§3 稀疏在 RAG', 'hub-spoke', '稀疏检索在 RAG 里站哪'), ('02-bm25-vs-dense.png', '§5 BM25 vs Dense', 'comparison-matrix', 'BM25 与 Dense 怎么分工'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', '稀疏检索 RAG 概念地图')]}),
    ('93.hybrid-search-tutorial.md', ARTICLE_93, {'slug': 'hybrid-search', 'roadmap': 110, 'title': '混合检索 Hybrid Search 完全指南', 'images': [('01-hybrid-idea.png', '§3 混合检索', 'hub-spoke', '混合检索是什么'), ('02-hybrid-arch.png', '§6 架构模式', 'comparison-matrix', '混合检索有哪些架构'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', '混合检索概念地图')]}),
    ('94.rrf-fusion-tutorial.md', ARTICLE_94, {'slug': 'rrf-fusion', 'roadmap': 111, 'title': 'RRF 倒数排名融合完全指南', 'images': [('01-rrf-idea.png', '§3 RRF 直觉', 'hub-spoke', 'RRF 融合是什么'), ('02-rrf-formula.png', '§5 RRF 公式', 'comparison-matrix', 'RRF 公式怎么算'), ('03-concept-map.png', '§11 综合概念地图', 'bento-grid', 'RRF 融合概念地图')]}),
]
