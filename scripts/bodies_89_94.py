# Articles 89-94 for build_all_86_94.py
from build_all_86_94 import (
    PREDS,
    TENANT_EXTRA,
    BACKUP_EXTRA,
    DENSE_EXTRA,
    SPARSE_EXTRA,
    HYBRID_EXTRA,
    RRF_EXTRA,
)


def article_89() -> str:
    return f'''# C4 向量存储（十五）：多租户 Namespace 隔离完全指南

> SaaS 知识库最常见事故之一：**A 公司的 query 召回了 B 公司的 chunk**——根因往往不是 HNSW 坏了，而是 **tenant_id 没进过滤** 或 **测试数据污染生产 collection**。[80 Pinecone](80.pinecone-tutorial.md) 的 **namespace**、[76 Chroma](76.chroma-vector-db-tutorial.md) 的 **多 collection**、[78 Qdrant](78.qdrant-tutorial.md) 的 **payload tenant** 都在解决 **多租户隔离**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **106** 条），讲清 **namespace / collection / 共享表+过滤** 三种模式、配额与合规、联调 [88 Metadata Filter](88.metadata-filter-retrieval-tutorial.md)。前置：{PREDS}、[53 ACL](53.metadata-acl-tutorial.md)。

---

## 目录

1. [前言：一套集群，很多客户](#1-前言一套集群很多客户)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [多租户在 RAG 里指什么](#3-多租户在-rag-里指什么)
4. [三种隔离模式对照](#4-三种隔离模式对照)
5. [Namespace 与 Collection 选型](#5-namespace-与-collection-选型)
6. [入库与查询的租户注入](#6-入库与查询的租户注入)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：共享 collection + 强制过滤](#8-实战代码共享-collection--强制过滤)
9. [配额、限流与 noisy neighbor](#9-配额限流与-noisy-neighbor)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：一套集群，很多客户

**多租户**（multi-tenancy）：同一套 RAG 服务实例，为 **多个客户（租户）** 提供隔离的知识库能力。每个租户有自己的文档、用户、配额；**检索与存储必须互不可见**。

向量库侧常见抽象：

| 抽象 | 代表 |
|------|------|
| Namespace | Pinecone、部分托管 API |
| Collection | Chroma、Milvus、Qdrant |
| Database / Schema | pgvector、Weaviate |

**读完本文，你应该能做到：**

1. 对比 **独立 collection vs 共享+tenant_id 过滤** 的安全与成本。  
2. 在 API 网关 **注入 tenant**，禁止客户端自选。  
3. 设计 **租户删除与迁移** 流程（接 [90 备份](90.vector-db-backup-tutorial.md)）。  
4. 写 **跨租户越权** 自动化测试。

### 1.1 路线图

```text
106 多租户 ← 本篇
105 Metadata Filter
107 备份恢复
```

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 106）。**

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A 读 §4 三模式 | 能选型 |
| B 跑 §8 | tenant_a 搜不到 tenant_b |
| C 写删除租户 runbook | 含备份 |

---

## 3. 多租户在 RAG 里指什么

![多租户隔离](image/multi-tenant-namespace/01-tenant-idea.png)

租户边界贯穿：**上传 → 分块 → 向量化 → 索引 → 查询 → 引用**。  
任何一环混用 tenant，后面全错。向量库只是 **存储与检索层** 的最后一道闸。

### 3.1 租户 ID 从哪来

- JWT `org_id` / `tenant_id`  
- API Key 映射表  
- **不要** 用可伪造的 query 参数

---

## 4. 三种隔离模式对照

![隔离模式](image/multi-tenant-namespace/02-isolation-patterns.png)

| 模式 | 隔离强度 | 成本 | 适用 |
|------|----------|------|------|
| 每租户独立 collection | 高 | 高 | 大客户、合规 |
| 每租户 namespace（同 index） | 中高 | 中 | Pinecone 类 SaaS |
| 共享 collection + tenant 字段前滤 | 中（依赖代码） | 低 | 早期 SaaS |

---

## 5. Namespace 与 Collection 选型

**独立 collection**：运维简单（删库=删租户），但 collection 数量上百后管理难。  
**共享+过滤**：collection 少，但 **每次查询必须强制 filter**（[88 篇](88.metadata-filter-retrieval-tutorial.md)），代码审查压力大。

---

## 6. 入库与查询的租户注入

```python
def ingest_chunk(tenant_id: str, chunk: dict, store):
    meta = {{**chunk["meta"], "tenant_id": tenant_id}}
    store.upsert(id=chunk["id"], vector=chunk["vec"], metadata=meta)

def search(tenant_id: str, q_vec, store, k=5):
    return store.search(q_vec, k=k, filter={{"tenant_id": tenant_id}})
```

**服务端**从 session 取 `tenant_id`，不信任请求体。

---

## 7. 先错对对：四种典型翻车

### 7.1 错：开发测试用 default collection

**对：** `test_` 前缀租户 + 独立目录；CI 跑越权测试。

### 7.2 错：客户端传 tenant_id

**对：** 网关从 token 解析。

### 7.3 错：只隔离对象存储不隔离向量

**对：** 向量 hits 仍可能含他户 text（若 metadata 错）。

### 7.4 错：admin 全局搜索无审计

**对：** 独立角色 + 审计日志。

---

## 8. 实战代码：共享 collection + 强制过滤

```python
# 伪代码：两租户各两条 chunk，验证隔离
TENANTS = ("tenant_a", "tenant_b")
for tid in TENANTS:
    for i in range(2):
        upsert(tid, f"{{tid}}_doc_{{i}}", f"机密内容 {{tid}} {{i}}")
hits = search("tenant_a", embed("机密内容"))
assert all(h.metadata["tenant_id"] == "tenant_a" for h in hits)
```

---

## 9. 配额、限流与 noisy neighbor

每租户：**存储上限、QPS、并发索引任务**。大租户冲击 CPU 时 **队列隔离** 或 **专属 replica**。

---

## 10. 综合概念地图

![多租户概念地图](image/multi-tenant-namespace/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{TENANT_EXTRA}

---

## 12. 总结与系列下一步

1. **多租户 = 全链路 tenant_id + 检索强制过滤或物理隔离**。  
2. **共享模式** 省成本但 **泄漏风险** 高。  
3. 删除/迁移见 [90 备份](90.vector-db-backup-tutorial.md)。

### 12.1 系列下一步

| 目标 | 阅读 |
|------|------|
| 过滤 | [88 Metadata Filter](88.metadata-filter-retrieval-tutorial.md) |
| 备份 | [90 向量库备份](90.vector-db-backup-tutorial.md) |

---

> **初学者可能仍困惑的点**  
> - **Namespace 不是** 万能保险——仍要鉴权。  
> - **独立 collection** 也有配错 API 指向同一 collection 的风险。  
> - **租户隔离** 要自动化测试，不能靠人工点点点。
'''


def article_90() -> str:
    return f'''# C4 向量存储（十六）：向量库备份与恢复完全指南

> 误删 collection、磁盘坏了、云账号误操作 bucket——向量库一挂，RAG 不是「慢一点」，是 **整库答不上来**。[76 Chroma](76.chroma-vector-db-tutorial.md) 拷目录、[75 FAISS](75.faiss-ann-tutorial.md) 的 `write_index`、[77 Milvus](77.milvus-tutorial.md) 快照——**备什么、怎么一致、怎么演练恢复**，是 C4 运维地基。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **107** 条）。前置：{PREDS}、[49 增量更新](49.incremental-update-tutorial.md)。

---

## 目录

1. [前言：向量库也是数据库](#1-前言向量库也是数据库)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [备份什么：向量、图、元数据、manifest](#3-备份什么向量图元数据manifest)
4. [一致性：flush、停写、快照](#4-一致性flush停写快照)
5. [各库备份方式对照](#5-各库备份方式对照)
6. [恢复流程与验证](#6-恢复流程与验证)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战：FAISS + manifest 模板](#8-实战faiss--manifest-模板)
9. [RPO/RTO 与灾难演练](#9-rporto-与灾难演练)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：向量库也是数据库

向量库保存：**embedding、ANN 索引结构、chunk 文本（或指针）、metadata**。丢任何一块，RAG 无法完整恢复。  
**备份**不是 `cp -r` 就算完——要 **manifest** 记录模型版本、维度、条数、git 版本。

### 1.1 读完能做什么

1. 列出本库 **备份清单**。  
2. 写 **恢复验证**（Top-k hash 对比）。  
3. 季度 **演练** runbook。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 107）。**

---

## 3. 备份什么

![备份什么](image/vector-db-backup/01-backup-idea.png)

| 组件 | 必须？ |
|------|--------|
| 向量 raw | 是 |
| ANN 索引 | 可重建但耗时，建议备 |
| documents 文本 | 是（或可追溯对象存储路径） |
| metadata | 是 |
| manifest | 强烈推荐 |

---

## 4. 一致性

**停写 → flush → 快照**；或接受最终一致但记录时间窗。增量见 [49 篇](49.incremental-update-tutorial.md)。

---

## 5. 各库备份方式对照

- **Chroma**：快照 `persist_directory`  
- **FAISS**：`write_index` + `id_map.json`  
- **Milvus**：Backup API / MinIO snapshot  
- **pgvector**：`pg_dump` + WAL 策略  
- **Pinecone**：托管方负责，但要懂 **恢复 SLA**

---

## 6. 恢复流程

![恢复流程](image/vector-db-backup/02-restore-flow.png)

```text
1. 新环境安装同版本库
2. 恢复文件 / 导入 snapshot
3. load collection / read_index
4. 跑金标 query 对比 Top-10 id
5. 切换流量
```

---

## 7. 先错对对

### 7.1 只备份向量不备份文本

**对：** RAG 需要 documents 或 S3 路径。

### 7.2 从不演练恢复

**对：** 季度演练，RTO 才可信。

### 7.3 manifest 没记 Embedding 模型

**对：** 恢复后 query 向量空间不一致全废。

### 7.4 备份未加密

**对：** 全文敏感，at-rest 加密。

---

## 8. 实战：FAISS + manifest

```yaml
# manifest.yaml
embedding_model: bge-m3
dim: 1024
metric: cosine
chunk_count: 120450
created_at: 2026-07-01T00:00:00Z
files:
  - index.faiss
  - id_map.jsonl
```

---

## 9. RPO/RTO

**RPO**：可接受丢多久增量；**RTO**：多久恢复服务。与业务定数字。

---

## 10. 综合概念地图

![备份概念地图](image/vector-db-backup/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{BACKUP_EXTRA}

---

## 12. 总结与系列下一步

1. **向量库备份 = 向量+索引+文本+manifest**。  
2. **演练**比备份本身更重要。  
3. 多租户恢复见 [89 篇](89.multi-tenant-namespace-tutorial.md)。

---

> **初学者可能仍困惑的点**  
> - **Chroma 拷目录** 不等于云级 DR。  
> - **索引可重建** 但 re-embed 可能要数天。  
> - **恢复后** 要重跑 [87 recall](87.ann-recall-latency-tutorial.md) 抽检。
'''


def article_91() -> str:
    return f'''# C4 向量存储（十七）：Dense 稠密检索完全指南

> [25 Embedding](25.embedding-vector-tutorial.md) 把 chunk 变成向量后，**Dense 检索**就是：用 [26 相似度](26.similarity-metrics-tutorial.md) 在向量空间里找 Top-k——背后由 [84 Flat](84.flat-brute-force-search-tutorial.md)、[86 HNSW](86.hnsw-index-tutorial.md) 等 ANN 加速。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **108** 条），把 **Dense 在 RAG 链路的位置、metric、归一化、与稀疏分工** 讲透。前置：{PREDS}、[66 L2 归一化](66.l2-normalization-tutorial.md)。对照 [92 稀疏](92.sparse-retrieval-rag-tutorial.md)、[93 混合](93.hybrid-search-tutorial.md)。

---

## 目录

1. [前言：语义相似怎么算](#1-前言语义相似怎么算)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Dense 稠密检索是什么](#3-dense-稠密检索是什么)
4. [核心概念：Embedding、metric、ANN](#4-核心概念embeddingmetricann)
5. [RAG 中的 Dense 流水线](#5-rag-中的-dense-流水线)
6. [优势、劣势与典型 bad case](#6-优势劣势与典型-bad-case)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：sentence-transformers + FAISS](#8-实战代码sentence-transformers--faiss)
9. [与稀疏、混合的衔接](#9-与稀疏混合的衔接)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：语义相似怎么算

**Dense retrieval**（稠密检索）：查询与文档都表示为 **低维稠密向量**（如 768 维），用 **余弦/内积/L2** 排序。  
相对 **Sparse**（BM25）：dense 强在 ** paraphrase、语义相近**；弱在 **精确词、编号、罕见 SKU**。

```text
用户问题 → Query Embedding → ANN Top-k chunk → 拼 prompt
```

### 1.1 读完能做什么

1. 画 Dense 在 RAG 的数据流。  
2. 选对 **metric 与归一化**。  
3. 说清何时加 [92 BM25](92.sparse-retrieval-rag-tutorial.md)。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 108）。**

---

## 3. Dense 稠密检索是什么

![Dense 稠密检索](image/dense-retrieval/01-dense-idea.png)

每个 chunk 一个向量；库百万即百万点。[86 HNSW](86.hnsw-index-tutorial.md) 负责快搜。

---

## 4. 核心概念

| 环节 | 说明 |
|------|------|
| Embedding | [25 篇](25.embedding-vector-tutorial.md) |
| 相似度 | [26 篇](26.similarity-metrics-tutorial.md) |
| 归一化 | [66 篇](66.l2-normalization-tutorial.md) |
| ANN | [75 FAISS](75.faiss-ann-tutorial.md)、向量库 |

---

## 5. RAG 中的 Dense 流水线

![Dense 流水线](image/dense-retrieval/02-dense-pipeline.png)

入库与查询 **必须用同一模型**；换模型 **全量重建**（[76 Chroma](76.chroma-vector-db-tutorial.md) 新建 collection）。

---

## 6. 优势、劣势

| 优势 | 劣势 |
|------|------|
| 语义泛化 | 专有名词 |
| 跨语言（视模型） | 可解释性弱 |
| 与 ANN 成熟生态 | 依赖 GPU/API 成本 |

---

## 7. 先错对对

### 7.1 错：query 与 doc 用不同 Embedding 模型

**对：** 同一模型同一空间。

### 7.2 错：cosine 但未归一化

**对：** [66 篇](66.l2-normalization-tutorial.md)。

### 7.3 错：k=3 硬编码

**对：** 按任务调 k，评测 [87 recall](87.ann-recall-latency-tutorial.md)。

### 7.4 错：只有 Dense 没有 BM25

**对：** 工单号类问题加 [92 稀疏](92.sparse-retrieval-rag-tutorial.md)。

---

## 8. 实战代码

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
docs = ["年假政策", "报销流程", "IT 密码重置"]
X = model.encode(docs, normalize_embeddings=True)
index = faiss.IndexFlatIP(X.shape[1])
index.add(X.astype("float32"))
q = model.encode(["怎么请假"], normalize_embeddings=True).astype("float32")
D, I = index.search(q, 2)
print([docs[i] for i in I[0]])
```

---

## 9. 与稀疏、混合

Dense 一路在 [93 Hybrid](93.hybrid-search-tutorial.md) 与 BM25 并行，[94 RRF](94.rrf-fusion-tutorial.md) 融合。

---

## 10. 综合概念地图

![Dense 概念地图](image/dense-retrieval/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{DENSE_EXTRA}

---

## 12. 总结与系列下一步

1. **Dense = Embedding + metric + ANN**。  
2. **与稀疏互补**，不是二选一。  
3. 过滤见 [88 篇](88.metadata-filter-retrieval-tutorial.md)。

---

> **初学者可能仍困惑的点**  
> - **Dense 不是** 理解语言——是 **相似度插值**。  
> - **距离小** 不等于 **业务相关**。  
> - **必须评测** recall，不能凭体感。
'''


def article_92() -> str:
    return f'''# C4 向量存储（十八）：Sparse 稀疏检索（BM25）在 RAG 中完全指南

> [19 BM25](19.bm25-sparse-retrieval-tutorial.md) 把 **公式、k1/b、倒排直觉** 讲透了——本篇专注 **BM25 在 RAG 管道里怎么接入**：分块入库、查询分词、与 Dense 并行、调试 score。企业问「报销单号 EXP-2024-001」时，**稀疏一路** 往往比纯向量更稳。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **109** 条）。前置：{PREDS}、**[19 BM25 原理](19.bm25-sparse-retrieval-tutorial.md)**、[17 分词](17.nlp-tokenization-basics-tutorial.md)。下一篇 [93 混合](93.hybrid-search-tutorial.md)、[94 RRF](94.rrf-fusion-tutorial.md)。

---

## 目录

1. [前言：关键字还没过时](#1-前言关键字还没过时)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [稀疏检索在 RAG 链路的位置](#3-稀疏检索在-rag-链路的位置)
4. [与 [19 篇](19.bm25-sparse-retrieval-tutorial.md) 的分工](#4-与-19-篇的分工)
5. [BM25 vs Dense：何时谁赢](#5-bm25-vs-dense何时谁赢)
6. [入库：倒排索引与 chunk 设计](#6-入库倒排索引与-chunk-设计)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：rank_bm25 与 ES 片段](#8-实战代码rank_bm25-与-es-片段)
9. [与混合检索、RRF 衔接](#9-与混合检索rrf-衔接)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：关键字还没过时

RAG 流行 Dense 后，有人以为 **不用 BM25**——直到 bad case：**错误码 E4041**、**条款 3.2.1**、**产品 SKU** 在向量空间里并不「语义最近」。

**稀疏检索**在 RAG 中负责：**字面匹配 + 经典 IR 排序**。  
公式细节见 **[19 BM25 稀疏检索原理完全指南](19.bm25-sparse-retrieval-tutorial.md)**；本篇讲 **工程接入**。

### 1.1 数据流

```text
chunk 文本 → 分词 → 倒排索引
用户 query → 分词 → BM25 Top-k
→（可选）与 Dense 融合 → prompt
```

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 109）。**

---

## 3. 稀疏检索在 RAG 链路的位置

![稀疏在 RAG](image/sparse-retrieval-rag/01-sparse-rag.png)

BM25 **不生成答案**；只产 **候选 chunk 列表**。与 [34 Grounding](34.grounding-citation-tutorial.md) 一样，要有 **chunk_id** 溯源。

---

## 4. 与 19 篇的分工

| 19 篇 | 本篇 |
|------|------|
| TF-IDF vs BM25 公式 | RAG ingest/query 管道 |
| k1、b 直觉 | chunk、元数据 boost |
| 倒排概念 | ES / rank_bm25 代码 |
| 与向量分工概述 | Hybrid、RRF 落地 |

**请务必先读 [19 篇](19.bm25-sparse-retrieval-tutorial.md)**，再读本篇代码节。

---

## 5. BM25 vs Dense

![BM25 vs Dense](image/sparse-retrieval-rag/02-bm25-vs-dense.png)

| 场景 | 更优 |
|------|------|
| 编号、代码、法规号 | BM25 |
| 口语 paraphrase | Dense [91 篇](91.dense-retrieval-tutorial.md) |
| 中英混合专有词 | 常需 Hybrid [93 篇](93.hybrid-search-tutorial.md) |

---

## 6. 入库与 chunk

- 中文分词质量决定上限（[17 篇](17.nlp-tokenization-basics-tutorial.md)）  
- title/section 字段 **boost**  
- 与 [51 chunk_id](51.metadata-chunk-id-tutorial.md) 对齐

---

## 7. 先错对对

### 7.1 错：把 BM25 分数当概率

**对：** 分数量纲与向量距离不可比；融合用 [94 RRF](94.rrf-fusion-tutorial.md)。

### 7.2 错：整篇手册一个 chunk

**对：** C2 分块；见路线图 64～72。

### 7.3 错：停用词把 SKU 删了

**对：** 领域词典保护。

### 7.4 错：稀疏索引不更新

**对：** 增量与 [49 篇](49.incremental-update-tutorial.md) 一致。

---

## 8. 实战代码

```python
from rank_bm25 import BM25Okapi
import jieba

corpus = ["员工年假不少于十天", "报销需填写 EXP 单号", "IT 重置密码找服务台"]
tokenized = [list(jieba.cut(d)) for d in corpus]
bm25 = BM25Okapi(tokenized)
q = list(jieba.cut("EXP 单号 报销"))
scores = bm25.get_scores(q)
top = sorted(range(len(corpus)), key=lambda i: scores[i], reverse=True)[:2]
print([corpus[i] for i in top])
```

Elasticsearch 侧：`match` on `content` field，默认 BM25（[82 篇](82.elasticsearch-vector-tutorial.md)）。

---

## 9. 与混合、RRF

双路各取 k=50 → [94 RRF](94.rrf-fusion-tutorial.md) → Top-10 → 可选 rerank。

---

## 10. 综合概念地图

![稀疏 RAG 概念地图](image/sparse-retrieval-rag/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{SPARSE_EXTRA}

---

## 12. 总结与系列下一步

1. **BM25 在 RAG 仍不可替代**（字面场景）。  
2. **原理读 19，工程读本篇**。  
3. 与 Dense 组合见 [93][94]。

### 12.1 系列下一步

| 目标 | 阅读 |
|------|------|
| BM25 公式 | [19 BM25](19.bm25-sparse-retrieval-tutorial.md) |
| 混合 | [93 Hybrid](93.hybrid-search-tutorial.md) |
| RRF | [94 RRF](94.rrf-fusion-tutorial.md) |

---

> **初学者可能仍困惑的点**  
> - **稀疏不是** 过时技术——是 **互补路**。  
> - **分数不能** 与 cosine 直接加。  
> - **分词** 错了 BM25 全错。
'''


def article_93() -> str:
    return f'''# C4 向量存储（十九）：混合检索 Hybrid Search 完全指南

> 只用 [91 Dense](91.dense-retrieval-tutorial.md)：**「年假怎么请」** 能中；只用 [92 BM25](92.sparse-retrieval-rag-tutorial.md)：**「EXP-2024-001」** 能中——**Hybrid Search** 让两路 **同一次提问各搜一遍**，再融合。OpenSearch [83 篇](83.opensearch-hybrid-tutorial.md)、ES [82 篇](82.elasticsearch-vector-tutorial.md) 都在推 **单集群混合查询**；自建也常 **应用层双查 + [94 RRF](94.rrf-fusion-tutorial.md)**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 主线篇**（路线图第 **110** 条）。前置：{PREDS}、[19 BM25](19.bm25-sparse-retrieval-tutorial.md)、[91 Dense](91.dense-retrieval-tutorial.md)、[88 过滤](88.metadata-filter-retrieval-tutorial.md)。

---

## 目录

1. [前言：两路召回，一路答案](#1-前言两路召回一路答案)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [混合检索是什么](#3-混合检索是什么)
4. [核心架构模式](#4-核心架构模式)
5. [分数为何不能直接相加](#5-分数为何不能直接相加)
6. [与 Metadata Filter 联用](#6-与-metadata-filter-联用)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：双路并行 + RRF](#8-实战代码双路并行--rrf)
9. [评测与延迟](#9-评测与延迟)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：两路召回，一路答案

**Hybrid Search**（混合检索）：对同一 query，**稀疏（BM25）+ 稠密（向量）** 同时检索，再 **融合** 候选列表。  
动机：**互补**——语义与字面各擅胜场（见 [91][92]）。

### 1.1 读完能做什么

1. 画三种架构图（应用双查、ES/OpenSearch、多库）。  
2. 说明为何用 **RRF** 而非分数加权。  
3. 跑通 §8 最小 Hybrid。

---

## 2. 本文边界与动手路径

**档位：C4 主线篇（路线图 110）。**

---

## 3. 混合检索是什么

![混合检索](image/hybrid-search/01-hybrid-idea.png)

```mermaid
flowchart LR
  Q[Query]
  B[BM25]
  D[Dense ANN]
  F[RRF 融合]
  R[Top-k for RAG]
  Q --> B --> F
  Q --> D --> F
  F --> R
```

---

## 4. 核心架构模式

![混合架构](image/hybrid-search/02-hybrid-arch.png)

| 模式 | 说明 |
|------|------|
| 应用层双查 | 最灵活；两库或同一 ES |
| OpenSearch hybrid | [83 篇](83.opensearch-hybrid-tutorial.md) |
| ES knn + bool | [82 篇](82.elasticsearch-vector-tutorial.md) |

---

## 5. 分数为何不能直接相加

BM25 分无界，cosine 在 [0,1] 或距离 —— **量纲不同**。用 **[94 RRF](94.rrf-fusion-tutorial.md)** 或验证集上学权重。

---

## 6. 与 Metadata Filter

**两路必须同一 filter**（[88 篇](88.metadata-filter-retrieval-tutorial.md)），否则融合进越权 chunk。

---

## 7. 先错对对

### 7.1 错：一路挂了仍融合

**对：** 降级策略：单路或拒答。

### 7.2 错：chunk_id 不一致

**对：** 同一 chunk 两路同一 id（[51 篇](51.metadata-chunk-id-tutorial.md)）。

### 7.3 错：串行双查翻倍延迟

**对：** `asyncio.gather` 并行。

### 7.4 错：不做端到端评测

**对：** 答案级金标 + 检索 recall。

---

## 8. 实战代码：双路并行 + RRF

```python
import asyncio

async def search_bm25(q): ...
async def search_dense(q): ...

async def hybrid(q, k=10):
    sparse_hits, dense_hits = await asyncio.gather(search_bm25(q), search_dense(q))
    from rrf import rrf_merge  # 见 94 篇
    return rrf_merge([sparse_hits, dense_hits], k=k)
```

---

## 9. 评测与延迟

延迟 ≈ **max(两路)** + 融合；QPS 压测要 **并行**。每路单独 recall + 融合后 recall。

---

## 10. 综合概念地图

![Hybrid 概念地图](image/hybrid-search/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{HYBRID_EXTRA}

---

## 12. 总结与系列下一步

1. **Hybrid = 稀疏 + 稠密 + 融合**。  
2. **RRF** 是默认友好融合（[94 篇](94.rrf-fusion-tutorial.md)）。  
3. **过滤与 chunk_id** 两路一致。

---

> **初学者可能仍困惑的点**  
> - **混合不是** 简单把两个分数相加。  
> - **两路都要** 维护索引一致性。  
> - **延迟** 看最慢一路。
'''


def article_94() -> str:
    return f'''# C4 向量存储（二十）：RRF 倒数排名融合完全指南

> [93 混合检索](93.hybrid-search-tutorial.md) 双路各给一列 **rank**，BM25 第 2 名与向量第 5 名 **分数量纲不同**——**RRF**（Reciprocal Rank Fusion，倒数排名融合）用 $\\sum 1/(k+rank)$ 把多路排序合成 **一路**，无监督、稳、好实现。Elasticsearch 8.x+、OpenSearch 均提供 RRF API。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **111** 条）。前置：{PREDS}、[93 Hybrid](93.hybrid-search-tutorial.md)、[92 稀疏](92.sparse-retrieval-rag-tutorial.md)、[91 Dense](91.dense-retrieval-tutorial.md)。

---

## 目录

1. [前言：融合看排名，不看分数](#1-前言融合看排名不看分数)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [RRF 是什么](#3-rrf-是什么)
4. [公式与常数 k](#4-公式与常数-k)
5. [双路与多路融合](#5-双路与多路融合)
6. [与加权融合、重排序分工](#6-与加权融合重排序分工)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：纯 Python RRF](#8-实战代码纯-python-rrf)
9. [Elasticsearch RRF 片段](#9-elasticsearch-rrf-片段)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：融合看排名，不看分数

两路检索：

| chunk | BM25 rank | Dense rank |
|-------|-----------|------------|
| A | 1 | 20 |
| B | 15 | 1 |
| C | 2 | 3 |

**线性加权分数** 要先归一化各路人马，调参费劲。**RRF** 只问：**排第几**。

**RRF score**（对文档 d）：

$$\\text{{RRF}}(d) = \\sum_i \\frac{{1}}{{k + \\text{{rank}}_i(d)}}$$

常见 **k=60**（Cormack et al.）。  
通俗说：**名次越前，贡献越大；两路都靠前则叠加更高**。

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 111）。**

---

## 3. RRF 是什么

![RRF 直觉](image/rrf-fusion/01-rrf-idea.png)

输入：多路 **已排序 id 列表**。输出：融合排序。  
**不要求** 原始 score。

---

## 4. 公式与常数 k

![RRF 公式](image/rrf-fusion/02-rrf-formula.png)

- **k 大**：各路前几名差距缩小，更平滑。  
- **k 小**：更强调 rank 1。  
- 默认 **60** 多数场景够用；可网格试 **30～100**。

---

## 5. 双路与多路

```python
def rrf(rank_lists, k=60):
    scores = {{}}
    for ranks in rank_lists:
        for rank, doc_id in enumerate(ranks, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

三路可加：BM25、Dense、标题 keyword。

---

## 6. 与加权、重排序

| 方法 | 特点 |
|------|------|
| RRF | 无监督、稳 |
| 加权 | 需标注调权重 |
| Cross-Encoder | 融合后再精排（112+） |

---

## 7. 先错对对

### 7.1 错：用原始 BM25 分 + cosine 相加

**对：** RRF 或 learned fusion。

### 7.2 错：每路只取 k=5 再融合

**对：** 每路 **over-fetch** k=50～100，融合后取 10。

### 7.3 错：重复 chunk 不同 id

**对：** 统一 [51 chunk_id](51.metadata-chunk-id-tutorial.md)。

### 7.4 错：不做消融

**对：** 报告 sparse-only、dense-only、RRF 三路指标。

---

## 8. 实战代码

```python
bm25_ids = ["c3", "c1", "c5", "c2"]
dense_ids = ["c1", "c5", "c3", "c9"]
merged = rrf([bm25_ids, dense_ids], k=60)[:5]
print(merged)
```

---

## 9. Elasticsearch

```json
{{
  "retriever": {{
    "rrf": {{
      "retrievers": [
        {{ "standard": {{ "query": {{ "match": {{ "text": "query" }} }} }} }},
        {{ "knn": {{ "field": "embedding", "query_vector": [...], "k": 50 }} }}
      ],
      "rank_constant": 60
    }}
  }}
}}
```

---

## 10. 综合概念地图

![RRF 概念地图](image/rrf-fusion/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{RRF_EXTRA}

---

## 12. 总结与系列下一步

1. **RRF = 按 rank 融合，k 常用 60**。  
2. **Hybrid 的默认融合器**（接 [93 篇](93.hybrid-search-tutorial.md)）。  
3. 之后 **重排序** 进一步提升（路线图 112+）。

---

> **初学者可能仍困惑的点**  
> - **RRF 不用** 原始分数。  
> - **每路要多召回** 再融合。  
> - **k=60 不是** 宇宙常数——可 tune。
'''
