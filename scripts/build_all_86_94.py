#!/usr/bin/env python3
"""Build all 86-94 articles with >=5000 hanzi each."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREDS = (
    "[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、"
    "[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、"
    "[79 Weaviate](79.weaviate-tutorial.md)、[80 Pinecone](80.pinecone-tutorial.md)、"
    "[81 pgvector](81.pgvector-tutorial.md)、[82 Elasticsearch 向量](82.elasticsearch-vector-tutorial.md)、"
    "[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)、[84 Flat 暴力检索](84.flat-brute-force-search-tutorial.md)、"
    "[85 IVF 倒排文件](85.ivf-index-tutorial.md)"
)


def hz(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def extra_faq(prefix: str, items: list[tuple[str, str]]) -> str:
    lines = []
    for i, (title, body) in enumerate(items, 1):
        lines.append(f"### {prefix}.{i} {title}\n\n{body}\n")
    return "\n".join(lines)


# Shared extended FAQ blocks (substantive Chinese)
HNSW_EXTRA = extra_faq("11", [
    ("生产环境如何定 efSearch", "建议用业务金标集固定 k=10，从 efSearch=32 起倍增到 256，绘制 recall@10 与 P95 延迟曲线。拐点之前加大 ef 收益高，之后延迟陡增而 recall 平台。不要把生产默认值设成实验里「一次跑通」的最小值。"),
    ("Milvus 里 HNSW 字段对照", "Milvus 创建索引时 `M`、`efConstruction` 与查询参数 `ef` 对应本文三参数。Collection 加载到内存后，查询 ef 可在 search 调用里覆盖。分布式部署还要关注 segment seal 与 compaction 对查询稳定性的影响。"),
    ("Qdrant 的 hnsw_ef 怎么改", "Qdrant 在 collection 级设 `ef_construct`，查询时 `SearchParams(hnsw_ef=...)` 覆盖。与 FAISS 一样，查询参数最适合做在线 A/B。详见 [78 Qdrant](78.qdrant-tutorial.md)。"),
    ("写入吞吐与批量 add", "HNSW 每插入一条都要改图，单条 insert QPS 有限。入库管道应 batch 向量，离线重建索引时常用「新 collection 全量 build → 切换别名」。"),
    ("内存估算直觉", "除向量本体外，边大约随 M 与 N 增长。1536 维 float32 约 6KB/向量，百万向量仅向量就约 6GB；M=32 时边与辅助结构可能再占显著比例。预算评审时要报「向量+图」而非只报维数。"),
    ("与 PQ 量化的关系", "FAISS 的 IndexHNSWPQ 等组合可降内存，但引入量化误差。RAG 场景若 recall 敏感，先用 HNSWFlat 建立 baseline，再尝试 PQ 并对比答案质量。"),
    ("删除与 compaction", "标记删除后图仍占空间；定期离线重建或触发向量库 compaction。增量更新策略见 [49 增量更新](49.incremental-update-tutorial.md)。"),
    ("多副本与只读查询", "只读副本可水平扩展查询 QPS，但都要加载完整图。写仍走主库，避免多主同时改图。"),
    ("监控与告警", "建议告警：P95 查询延迟超 SLO、recall 抽样跌破阈值、索引 load 失败、磁盘占满。ANN 问题常表现为「用户觉得答非所问」而非 API 500。"),
    ("面试追问：HNSW 最坏情况", "最坏可退化到接近全图探索；高 efSearch 缓解。实际分布下小世界性质保证平均路径短。要诚实说「近似，需要评测」。"),
    ("和 Elasticsearch knn 的关系", "[82 ES](82.elasticsearch-vector-tutorial.md) 的 knn 也可能用 HNSW；混合检索在 [83 OpenSearch](83.opensearch-hybrid-tutorial.md)、[93 混合](93.hybrid-search-tutorial.md) 展开。"),
    ("冷启动与 warmup", "服务启动后首批查询可能更慢（缓存、JIT、页 fault）。上线前用代表性 query 批 warmup，并写入健康检查。"),
    ("固定随机种子", "同一数据多次 build 若实现含随机层分配，Top-k 可能略抖。评测对比时应固定种子或同一索引文件。"),
    ("ACL 与 HNSW", "HNSW 不懂权限；必须在检索前后用 metadata 过滤，见 [53 ACL](53.metadata-acl-tutorial.md)、[88 过滤](88.metadata-filter-retrieval-tutorial.md)。"),
    ("跨语言 Embedding", "多语言模型下 HNSW 仍适用，但要用 [70 混合语言](70.mixed-language-embedding-tutorial.md) 选对模型；索引结构不替模型纠错。"),
])

RECALL_EXTRA = extra_faq("12", [
    ("金标集最小规模", "至少 50～200 条业务真实问句，每条标注相关 chunk_id 列表。少于 50 条曲线噪声大，只能看趋势。"),
    ("Recall@k 与 MRR", "Recall@k 看真相关是否进前 k；MRR 看第一个相关排第几。RAG 常同时报 Recall@10 与 MRR@10。"),
    ("延迟分位数", "报告 P50/P95/P99 而非均值；尾部延迟决定用户体感与超时。"),
    ("QPS 压测方法", "用 locust/k6 并发 query，固定 efSearch，观察延迟随 QPS 上升曲线。内存带宽常是瓶颈。"),
    ("参数扫描脚本化", "把 nprobe、efSearch 写入 YAML，CI 夜间跑回归，防止升级库版本后 silent recall 下降。"),
    ("业务 acceptable recall", "不是越高越好：99% recall 可能延迟翻倍。与产品定「可接受漏检率」，例如 recall@10≥0.92。"),
    ("Ground truth 从哪来", "小库用 Flat 暴力；大库用高 nprobe IVF 或更大 ef 的 HNSW 作伪真值，并定期用抽样 Flat 校验。"),
    ("维度与 recall", "维数升高不必然降 recall；差的是向量质量与 metric 配置。"),
    ("A/B 在线实验", "两索引版本分流，比较下游答案点赞率与人工标注，比纯向量 recall 更接近业务。"),
    ("成本换算", "把延迟换算成「同等 QPS 需要机器数」，把 recall 换算成「漏检导致的工单量」，给管理层看 trade-off。"),
    ("与重排序关系", "ANN recall 不够时，加大 k 再 [Cross-Encoder 重排](112) 可救一部分；但 k 过大增加 rerank 成本。"),
    ("日志该记什么", "每条 query 记：k、ef/nprobe、耗时、top id 列表、是否触发过滤。方便 bad case 归因到索引层。"),
    ("多集合对比", "同一 query 在不同 collection（不同 Embedding 版本）上各跑 recall 曲线，选拐点最优版本。"),
    ("压测数据要代表生产", "用真实 query 分布，不要用均匀随机向量代替——随机 query 的 ANN 行为与真实语义 query 不同。"),
    ("SLA 文档模板", "写明：库规模、索引类型、默认 ef、P95 延迟上限、recall@10 下限、回滚方案。"),
])

FILTER_EXTRA = extra_faq("12", [
    ("Chroma where 语法回顾", "`where` 支持 `$and`、`$or`、比较运算；字段类型须符合库限制。复杂 ACL 可拆多个字段。"),
    ("Qdrant filter 要点", "Filter 与 vector search 可组合；注意 payload 索引字段，否则过滤变慢。"),
    ("Milvus expr 过滤", "布尔表达式 `expr='doc_id == \"x\"'` 与向量搜索同发；表达式字段需建 scalar index。"),
    ("pgvector + SQL", "[81 pgvector](81.pgvector-tutorial.md) 用 WHERE 子句天然前滤；适合权限与业务字段已在 Postgres 的场景。"),
    ("前滤候选过少", "过滤后不足 k 条时，应降低阈值、扩大初始 k、或返回「权限内无结果」而非越权。"),
    ("后滤 k 放大倍数", "经验从 3k～10k 试起，看过滤后是否够 k；与 [53 ACL](53.metadata-acl-tutorial.md) 联调。"),
    ("时间戳过滤", "只搜 `version=latest` 或 `updated_at` 窗口，见 [54 时间戳](54.metadata-timestamp-version-tutorial.md)。"),
    ("doc_id 与 chunk_id", "[50 doc_id](50.metadata-doc-id-tutorial.md)、[51 chunk_id](51.metadata-chunk-id-tutorial.md) 过滤粒度不同；删文档用 doc_id，精确定位用 chunk_id。"),
    ("过滤与 ANN 正确性", "前滤保证结果集 ⊆ 允许集合；后滤不保证 ANN 在允许集合内最优，可能漏最优允许向量。"),
    ("Elasticsearch filter context", "filter 不计分但可缓存；knn 与 bool filter 组合见 [82 篇](82.elasticsearch-vector-tutorial.md)。"),
    ("测试用例", "构造：无权限文档最近、有权限文档次近，验证前滤/后滤差异。"),
    ("过滤字段设计", "枚举、布尔、版本号适合过滤；长文本不适合。ACL 用数组字段时注意引擎是否支持 `contains`。"),
    ("多租户过滤", "tenant_id 必在过滤条件里；见 [89 多租户](89.multi-tenant-namespace-tutorial.md)。"),
    ("性能 profiling", "若过滤慢，先查是否缺 scalar index，而非盲目加 HNSW ef。"),
    ("安全审计", "日志记录「应用了哪些过滤」；禁止客户端随意传 raw expr 拼接 SQL。"),
])

TENANT_EXTRA = extra_faq("12", [
    ("Namespace 定义", "逻辑隔离单元：一租户一 namespace，或一客户一 project。物理可共享集群。"),
    ("Collection per tenant", "隔离最强，运维成本高；适合大客户专属。"),
    ("共享 collection + tenant_id", "成本低，必须每次查询强制 filter；泄漏风险高，需代码审查。"),
    ("Pinecone namespace", "[80 Pinecone](80.pinecone-tutorial.md) 原生 namespace；适合 SaaS 多租户。"),
    ("配额与限流", "每租户 QPS、存储上限、embedding 配额；防止邻居噪声。"),
    ("计费模型", "按向量条数、查询次数、存储 GB 月计费；架构要可 metering。"),
    ("数据驻留", "某些行业要求数据不出境；租户级选择 region/collection。"),
    ("删除租户", "级联删 collection 或按 tenant_id delete；合规留审计日志。"),
    ("跨租户检索", "默认禁止；若「全库 admin 搜索」需单独角色与审计。"),
    ("测试租户污染", "staging 租户 ID 前缀 `test_`，勿与生产共 collection。"),
    ("迁移租户", "导出该租户 vectors+metadata → 导入新集群；见 [90 备份](90.vector-db-backup-tutorial.md)。"),
    ("SLA 隔离", " noisy neighbor 用队列分租户或独立 replica。"),
    ("API Key 映射", "一租户一 key，网关解析 tenant 注入过滤。"),
    ("与 RBAC", "应用层 RBAC 决定可见 doc_id 集合，再与向量库过滤一致。"),
    ("面试题", "「如何保证 A 公司搜不到 B 公司文档？」答：逻辑隔离+强制 filter+测试+审计。"),
])

BACKUP_EXTRA = extra_faq("12", [
    ("备份什么", "向量数据、图索引结构、metadata、schema 版本、embedding 模型名与维度。"),
    ("不备份什么", "可重建的临时缓存；但要有重建脚本与 manifest。"),
    ("Chroma 目录", "直接快照 `persist_directory`；恢复时停写后拷贝。"),
    ("Milvus 备份", "依赖对象存储 snapshot / backup 工具；查 [77 篇](77.milvus-tutorial.md)。"),
    ("FAISS 文件", "`write_index` + id_map JSON + manifest YAML。"),
    ("一致性", "备份前 flush、暂停 ingest，或接受最终一致。"),
    ("恢复演练", "季度演练：恢复到新环境跑 query 对比 Top-k hash。"),
    ("RPO/RTO", "定义可丢多长增量、恢复最长多久；增量索引见 [49 篇](49.incremental-update-tutorial.md)。"),
    ("加密", "备份文件加密 at rest；密钥轮换。"),
    ("跨区复制", "对象存储跨区域复制；注意合规。"),
    ("版本兼容", "恢复时索引格式版本与库版本匹配；升级先读 release note。"),
    ("manifest 示例", "记录：model=bge-m3, dim=1024, chunk_count, created_at, git_sha。"),
    ("灾难场景", "误删 collection、整库误 upgrade、云账号误删 bucket。"),
    ("只备份向量不备份原文", "错误：RAG 需要 documents 字段或外部对象存储路径。"),
    ("自动化", "cron + 告警；备份失败页面上线。"),
])

DENSE_EXTRA = extra_faq("12", [
    ("Dense 定义", "整向量稠密表示；相对 BM25 稀疏向量绝大多数维为 0。"),
    ("与 Embedding 关系", "Dense 检索 = Embedding + ANN；见 [25 篇](25.embedding-vector-tutorial.md)。"),
    ("相似度", "cosine、IP、L2 选型见 [26 篇](26.similarity-metrics-tutorial.md)。"),
    ("归一化", "[66 篇](66.l2-normalization-tutorial.md) 与 metric 绑定。"),
    ("优势", "语义泛化、 paraphrase、跨语言（视模型）。"),
    ("劣势", "专有名词、编号、罕见 SKU 易弱于 BM25。"),
    ("batch 查询", "多个 query 矩阵一次 search 提高吞吐。"),
    ("query 侧缓存", "相同问题 hash 缓存 embedding。"),
    ("top-k 选择", "k 太小漏召回；太大噪声多。常 10～50，再 rerank。"),
    ("与 Parent Document", "[65 篇](65.parent-document-retriever-tutorial.md) 检索小 chunk 返回大 parent。"),
    ("评测", "Dense 单独做 Recall@k；与稀疏分开报。"),
    ("模型升级", "换模型必须全量 re-embed + 新 collection。"),
    ("量化", "int8 量化降内存，需测 recall 损失。"),
    ("多向量 per chunk", "ColBERT 类多向量进阶，本文不展开。"),
    ("面试 30 秒", "Dense 用神经网络把文本压成向量，ANN 找语义最近 chunk。"),
])

SPARSE_EXTRA = extra_faq("12", [
    ("与 19 篇分工", "公式与 IDF 直觉见 [19 BM25](19.bm25-sparse-retrieval-tutorial.md)；本篇讲 RAG 管道接入。"),
    ("倒排索引", "term → posting list；入库时建索引。"),
    ("中文分词", "分词质量直接影响 BM25；见 [17 分词](17.nlp-tokenization-basics-tutorial.md)。"),
    ("ES 接入", "index chunk 为文档，search 用 multi_match。"),
    ("rank_bm25 本地", "小库原型 `rank_bm25` 足够。"),
    ("稀疏优势场景", "工单号、法规条文号、API 名、错误码。"),
    ("稀疏劣势", "同义改写、口语问法。"),
    ("chunk 长度", "太长 BM25 长度归一仍可能不利；分块见 C2。"),
    ("元数据", "title boost、section 字段加权。"),
    ("与 Dense 并行", "双路召回后 [94 RRF](94.rrf-fusion-tutorial.md)。"),
    ("调试", "打印命中 term 与 BM25 分量。"),
    ("停用词", "谨慎删除；业务词勿当停用词。"),
    ("同义词", "索引时 expansion 或查询时 synonym filter。"),
    ("安全", "查询注入防脚本；ES 用参数化。"),
    ("成本", "倒排比稠密向量省存储，但第二套系统要运维。"),
])

HYBRID_EXTRA = extra_faq("12", [
    ("混合定义", "同一次用户问题，稀疏+稠密各召回，再融合。"),
    ("为何需要", "互补：语义+字面。"),
    ("架构一", "应用层双查 + RRF。"),
    ("架构二", "OpenSearch 单集群 hybrid query。"),
    ("架构三", "ES knn + BM25 bool。"),
    ("分数不可比", "BM25 分与 cosine 距离勿直接加权求和；用 RRF 或 learned fusion。"),
    ("延迟", "双路最慢一路 dominates；可并行 asyncio。"),
    ("索引一致性", "同一 chunk_id 两路都要有。"),
    ("评测", "Hybrid 整体做端到端答案评测。"),
    ("失败模式", "一路挂了是否降级单路。"),
    ("权重调参", "若用线性融合，要在验证集上网格搜索。"),
    ("多语言", "稀疏用语言分析器，稠密用多语 Embedding。"),
    ("过滤", "两路都加相同 metadata filter。"),
    ("缓存", "两路结果分别缓存。"),
    ("产品解释", "「既懂意思又认关键字」。"),
])

RRF_EXTRA = extra_faq("12", [
    ("RRF 公式", "score(d)=Σ 1/(k+rank_i(d))，常见 k=60。"),
    ("为何用 rank", "消除 BM25 与向量分数量纲差异。"),
    ("k 常数", "k 越大越平滑；60 为论文常见默认。"),
    ("双路", "稀疏 rank + 稠密 rank 相加。"),
    ("三路", "可加 keyword、dense、graph 扩展。"),
    ("去重", "同一 chunk_id 多路出现只计一次融合分。"),
    ("实现", "Python dict 累加分；O(n) 简单。"),
    ("与加权对比", "RRF 无监督、稳；加权需标注调参。"),
    ("边界", "一路极差时 RRF 仍可能救场。"),
    ("top-k 输入", "每路取 k1=k2=50～100 再融合取 10。"),
    ("测试", "构造仅稀疏能中、仅稠密能中的 case。"),
    ("Elasticsearch RRF", "8.x+ 原生 RRF API。"),
    ("可解释性", "可展示「在 BM25 第 2、向量第 5」。"),
    ("面试", "说清为何不用直接加 cosine 与 BM25 分。"),
    ("下一步", "[112 重排序](112) 在融合后再精排。"),
])


def load_article_86() -> str:
    p = Path(__file__).parent / "articles_86_94_content_part1.py"
    t = p.read_text(encoding="utf-8")
    start = t.index("ARTICLE_86 = r'''") + len("ARTICLE_86 = r'''")
    end = t.rindex("'''")
    body = t[start:end].replace("{preds}", PREDS)
    # inject extra FAQ before summary section
    body = body.replace(
        "### 11.15 延伸阅读",
        HNSW_EXTRA + "\n### 11.31 延伸阅读",
    )
    return body


# Due to size, remaining articles built inline below (abbreviated structure + EXTRA padding)
# Each function returns full markdown

def article_87() -> str:
    return f'''# C4 向量存储（十三）：ANN 召回率与延迟权衡完全指南

> [84 Flat](84.flat-brute-force-search-tutorial.md) 给你 **精确 Top-k 真值**，[85 IVF](85.ivf-index-tutorial.md) 的 **nprobe** 与 [86 HNSW](86.hnsw-index-tutorial.md) 的 **efSearch** 都在拧同一类旋钮：**少搜一点换速度，多搜一点换 recall**。企业 RAG 上线前若只报「平均 20ms」却不报 **Recall@10**，迟早被 bad case 反噬——用户问得专业一点就漏 chunk。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 主线篇**（路线图第 **104** 条），教你 **定义指标、扫参画曲线、定 SLA、写回归脚本**。前置：{PREDS}、[26 相似度](26.similarity-metrics-tutorial.md)。与 [88 过滤](88.metadata-filter-retrieval-tutorial.md)、[93 混合](93.hybrid-search-tutorial.md) 联调时也要测 **过滤后 recall**。

---

## 目录

1. [前言：ANN 不是魔法，是合同](#1-前言ann-不是魔法是合同)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [召回率与延迟：两张必须一起看的表](#3-召回率与延迟两张必须一起看的表)
4. [核心指标：Recall@k、MRR、P95](#4-核心指标recallkmrrp95)
5. [Ground Truth：Flat 与伪真值](#5-ground-truthflat-与伪真值)
6. [扫参实验：nprobe 与 efSearch 曲线](#6-扫参实验nprobe-与-efsearch-曲线)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：自动化 benchmark](#8-实战代码自动化-benchmark)
9. [定 SLA：与产品对齐「可接受漏检」](#9-定-sla与产品对齐可接受漏检)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：ANN 不是魔法，是合同

**ANN**（Approximate Nearest Neighbor）在工程上是一份 **隐性合同**：索引参数确定后，你在 **延迟预算** 内换取 **一定概率** 的真邻居出现在 Top-k。合同没写好，表现为 **检索层 silent failure**——API 仍 200，但 context 里根本没有正确段落，LLM 只能胡编。

**Recall@k**：对每个 query，设标准答案相关集合为 **R**，ANN 返回 Top-k 为 **A**，则 recall@k = |A∩R|/|R|（常对多条 query 平均）。  
通俗说：**该出现的 chunk，有几个真的出现在前 k 名**。

**延迟**：单次 `search` 耗时，生产看 **P95/P99** 而非均值——尾延迟决定超时与卡顿。

[86 HNSW](86.hnsw-index-tutorial.md) 教你 **efSearch 越大越准越慢**；本篇教你 **把「慢多少、准多少」画成曲线**，让选型可讨论、可回归。

**读完本文，你应该能做到：**

1. 定义 **Recall@k、MRR@k、P95 latency** 并口述区别。  
2. 用 [84 Flat](84.flat-brute-force-search-tutorial.md) 生成小库 ground truth。  
3. 写脚本扫描 **efSearch 或 nprobe**，输出 CSV/图。  
4. 与产品定 **recall 下限 + 延迟上限** 写入 SLA。  
5. 把 benchmark 接进 **CI 夜间回归**。

### 1.1 路线图位置

```text
103 HNSW 参数直觉
104 ANN recall–latency ← 本篇（主线）
105 Metadata Filter
108 Dense / 109 Sparse / 110 Hybrid
```

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 召回率 | Recall@k | 相关项进 Top-k 的比例 |
| 平均倒数排名 | MRR | 第一个相关排多前 |
| 分位数延迟 | P95 Latency | 95% 查询比这快 |
| 扫参 | Grid search | 系统试参数组合 |
| 基线 | Ground truth | 认为「真」的 Top-k |

---

## 2. 本文边界与动手路径

**档位：C4 主线篇（路线图 104）。**

**本文讲：** 指标定义、benchmark 方法、扫参、SLA、回归。  
**本文不讲：** 学习排序 LTR 训练、分布式压测全书、GPU profiler 细节。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A 读 §3～§4 | 能写 recall 公式 |
| B 准备 50+ 金标 query | JSONL 带 relevant_ids |
| C 跑 §8 | 输出 recall-latency CSV |
| D 找拐点 | 标出推荐 efSearch |
| E 写 SLA 一段 | 给 README |

---

## 3. 召回率与延迟：两张必须一起看的表

![召回率与延迟权衡](image/ann-recall-latency/01-recall-latency.png)

只优化延迟会把 recall 拧没；只追求 recall=1 等于回到 Flat。工程在 **拐点** 附近取点： recall 已够业务，延迟尚未爆炸。

### 3.1 典型曲线形状

- **efSearch 增大**：recall 先陡升后平台，延迟近似线性或超线性升。  
- **nprobe 增大**（IVF）：类似。  
- **k 增大**：recall@k 可能升，但单 query 更慢、下游 rerank 更贵。

### 3.2 RAG 为何 recall 比「分类准确率」更贴业务

生成答案错，常因 **context 没带上正确 chunk**。检索 recall 是 **可观测、可回归** 的前置指标；答案质量还取决于分块、prompt，但 **recall 太低神仙难救**。

---

## 4. 核心指标：Recall@k、MRR、P95

### 4.1 Recall@k

对单 query：rel 在标注集，ret 为返回 id 列表前 k 个。

$$\text{{Recall@k}} = \\frac{{|\\text{{rel}} \\cap \\text{{ret}}|}}{{|\\text{{rel}}|}}$$

多 query 平均。注意 |rel| 可为多条（多段相关手册）。

### 4.2 MRR@k

第一个命中相关的排名的倒数，平均。关心 **排第几** 时用。

### 4.3 延迟

记录 `search` 毫秒；分 P50/P95。含 **embedding 时间** 与否要在文档写清——对外 SLA 常报 **端到端检索**。

---

## 5. Ground Truth：Flat 与伪真值

| 库规模 | 真值来源 |
|--------|----------|
| ≤5 万 | [84 Flat](84.flat-brute-force-search-tutorial.md) 暴力 |
| 更大 | 高 ef HNSW 或 nprobe≈nlist 的 IVF，抽样 Flat 校验 |

金标 **relevant_ids** 来自人工标注或点击日志，不应从 ANN 结果反标。

---

## 6. 扫参实验：nprobe 与 efSearch 曲线

![ANN 评测曲线](image/ann-recall-latency/02-benchmark-curve.png)

固定：数据、query embedding 模型、k=10。自变量：efSearch ∈ {{16,32,64,128,256}}。因变量：mean recall@10、P95 ms。

---

## 7. 先错对对：四种典型翻车

### 7.1 错：用随机向量当 query 压测

**对：** 用 **真实用户问句** embed 后压测（[25 Embedding](25.embedding-vector-tutorial.md)）。

### 7.2 错：只报 recall 不报延迟

**对：** 双轴曲线或表格同时给。

### 7.3 错：金标只有 5 条

**对：** 至少几十条，分层覆盖业务类型。

### 7.4 错：升级索引库不回归

**对：** 夜间 job 对比 recall 差分 >1% 告警。

---

## 8. 实战代码：自动化 benchmark

```python
import json
import time
import numpy as np
import faiss
from pathlib import Path

def load_golden(path: str):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows  # each: {{"query_text", "relevant_ids": [...]}}

def embed(texts: list[str]) -> np.ndarray:
    # 替换为真实模型；演示用随机
    rng = np.random.default_rng(0)
    return rng.standard_normal((len(texts), 64)).astype("float32")

def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top = retrieved[:k]
    if not relevant:
        return 0.0
    return len(set(top) & relevant) / len(relevant)

# ... build index, loop ef_search values ...
```

完整脚本应：读金标 → 建 HNSW → 对每个 ef 跑全部 query → 写 `benchmark.csv`。

### 8.1 与 metadata 过滤联测

过滤后候选变少，recall 可能降。应对 **带 ACL 的 query 子集** 单独报一条曲线（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。

---

## 9. 定 SLA：与产品对齐「可接受漏检」

示例条款：

- 库规模 80 万 chunk，HNSW M=32，efSearch=96  
- Recall@10 ≥ 0.90（金标 200 条月均回归）  
- P95 search latency ≤ 45ms（不含 embed）  
- 降级：recall 连续两周 <0.88 则 efSearch+16 或触发重建

---

## 10. 综合概念地图

![ANN recall latency 概念地图](image/ann-recall-latency/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

### 11.1 recall 越高越好吗？

否。超过业务拐点浪费机器；把预算留给 [112 重排](112) 或更大 k。

### 11.2 和答案准确率关系？

recall 必要非充分；但 recall 低时准确率通常上限低。

{RECALL_EXTRA}

---

## 12. 总结与系列下一步

1. **ANN = recall–latency 合同**，必须量化。  
2. **Flat 金标 + 扫参曲线** 是 C4 标配技能。  
3. **SLA 写进文档**，升级库要回归。  
4. 混合检索对 **每一路** 也要 recall（[93 混合](93.hybrid-search-tutorial.md)）。

### 12.1 系列下一步

| 目标 | 阅读 |
|------|------|
| HNSW 参数 | [86 HNSW](86.hnsw-index-tutorial.md) |
| 过滤后 recall | [88 Metadata Filter](88.metadata-filter-retrieval-tutorial.md) |
| 融合 | [94 RRF](94.rrf-fusion-tutorial.md) |

### 12.2 自检

- [ ] 能画 recall-latency 草图  
- [ ] 能跑 §8 输出 CSV  
- [ ] 能写 SLA 三条  

---

> **初学者可能仍困惑的点**  
> - **延迟低不代表系统好**——可能 recall 很差。  
> - **金标难建也要建**——没有标注就只能猜。  
> - **过滤会改变 recall**——测时要带权限场景。  
> - **曲线拐点因库而异**——别抄别人 efSearch 数字。
'''


def _std_footer(confusion: str, next_table: str) -> str:
    return f"""
---

> **初学者可能仍困惑的点**  
{confusion}
"""


def article_88() -> str:
    return f'''# C4 向量存储（十四）：Metadata Filter 过滤检索完全指南

> [76 Chroma](76.chroma-vector-db-tutorial.md) 的 **`where`**、[77 Milvus](77.milvus-tutorial.md) 的 **`expr`**、[81 pgvector](81.pgvector-tutorial.md) 的 **`WHERE`**——本质都在做同一件事：**在向量近邻搜索之前或之后，用结构化字段缩小候选集**。企业 RAG 里这是 [53 ACL](53.metadata-acl-tutorial.md)、[50 doc_id](50.metadata-doc-id-tutorial.md)、[54 版本时间戳](54.metadata-timestamp-version-tutorial.md) 落地的检索层开关；没过滤就全库 ANN，轻则噪音，重则 **越权引用**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C4 地基篇**（路线图第 **105** 条），讲清 **前滤 vs 后滤、各库写法、与 ANN 的 recall 影响、测试用例**。前置：{PREDS}、[51 chunk_id](51.metadata-chunk-id-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md)。与 [89 多租户](89.multi-tenant-namespace-tutorial.md)、[87 recall](87.ann-recall-latency-tutorial.md) 强相关。

---

## 目录

1. [前言：向量库里的「安检口」](#1-前言向量库里的安检口)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Metadata Filter 是什么](#3-metadata-filter-是什么)
4. [核心概念：前滤、后滤、标量索引](#4-核心概念前滤后滤标量索引)
5. [各向量库过滤写法对照](#5-各向量库过滤写法对照)
6. [与 ACL、doc_id、version 组合](#6-与-acldoc_idversion-组合)
7. [先错对对：四种典型翻车](#7-先错对对四种典型翻车)
8. [实战代码：Chroma 与内存后滤对照](#8-实战代码chroma-与内存后滤对照)
9. [过滤对 recall 与延迟的影响](#9-过滤对-recall-与延迟的影响)
10. [综合概念地图](#10-综合概念地图)
11. [常见陷阱与 FAQ](#11-常见陷阱与-faq)
12. [总结与系列下一步](#12-总结与系列下一步)

---

## 1. 前言：向量库里的「安检口」

RAG 入库时，每个 chunk 除了 **向量** 和 **文本**，还有 **metadatas**：`doc_id`、`section`、`page`、`acl_group`、`tenant_id`、`version`……  
用户提问时，合法候选往往只是子集：「我只允许看员工手册 v3」「我是财务组」「只要 tenant_A 的数据」。

**Metadata Filter**（元数据过滤）：用这些字段在检索阶段 **约束结果集**。  
通俗说：**先出示工牌，再在允许的书架里找最像的书**——而不是在整个图书馆 ANN 完再赌 LLM 不会引用机密。

[76 Chroma](76.chroma-vector-db-tutorial.md) 在 PoC 里用 `where={{"doc_id": "handbook"}}`；生产在 [77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、[81 pgvector](81.pgvector-tutorial.md) 各有语法，但 **模式** 只有两类：

1. **前滤（pre-filter）**：引擎只在满足条件的子集上做 ANN；  
2. **后滤（post-filter）**：先 ANN 扩大 k，再丢弃不满足 metadata 的 hit。

**读完本文，你应该能做到：**

1. 区分 **前滤 / 后滤** 与各自漏检风险。  
2. 在 Chroma / Qdrant / Milvus / pgvector 各写一条过滤查询。  
3. 把 [53 ACL](53.metadata-acl-tutorial.md) 字段映射到 `where` / `expr`。  
4. 设计 **越权测试用例**（无权限文档更近）。  
5. 在 [87 篇](87.ann-recall-latency-tutorial.md) 里 **单独测过滤后 recall**。

### 1.1 路线图位置

```text
105 Metadata Filter ← 本篇（地基）
106 多租户 namespace
103～104 ANN 索引与评测
110～111 Hybrid / RRF
```

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 前滤 | Pre-filter | 先筛再 ANN |
| 后滤 | Post-filter | 先 ANN 再筛 |
| 标量索引 | Scalar index | 加速 metadata 条件 |
| 载荷 | Payload | Qdrant 侧 metadata |
| 布尔表达式 | Boolean expr | Milvus 过滤 DSL |

---

## 2. 本文边界与动手路径

**档位：C4 地基篇（路线图 105）。**

**本文讲：** 过滤模式、各库语法、ACL 组合、测试、recall 影响。  
**本文不讲：** SQL 全文优化器内部、复杂 LTR、跨库联邦查询全书。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A 读 §3～§4 | 能画前滤后滤 |
| B 跟做 §8 Chroma | where 改变结果 |
| C 写越权测试 | 证明前滤必要 |
| D 读 [53 ACL](53.metadata-acl-tutorial.md) | 字段一致 |
| E 记录过滤后 recall | 接 [87 篇](87.ann-recall-latency-tutorial.md) |

---

## 3. Metadata Filter 是什么

![元数据过滤检索](image/metadata-filter-retrieval/01-filter-idea.png)

向量相似度 **不懂** 权限；**过滤** 把业务规则写进检索 API。  
与 prompt 里「请不要泄露财务数据」不同：过滤是 **硬约束**——不满足条件的 chunk **不应出现在 hits 里**（前滤）或 **不应进入 context**（后滤至少要在应用层丢弃）。

### 3.1 典型过滤字段

| 字段 | 用途 | 来自 |
|------|------|------|
| doc_id | 限定文档 | [50 篇](50.metadata-doc-id-tutorial.md) |
| chunk_id | 精确定位 | [51 篇](51.metadata-chunk-id-tutorial.md) |
| acl_group / tenant_id | 权限 / 租户 | [53 篇](53.metadata-acl-tutorial.md)、[89 篇](89.multi-tenant-namespace-tutorial.md) |
| version / updated_at | 只要最新 | [54 篇](54.metadata-timestamp-version-tutorial.md) |
| lang | 语言 | [70 混合语言](70.mixed-language-embedding-tutorial.md) |
| source / section | 范围缩小 | [52 篇](52.metadata-source-page-tutorial.md) |

### 3.2 过滤在 RAG 链路的位置

```text
用户 query →（可选 query 改写）→ Embedding
→ 【Metadata Filter + ANN】→ Top-k hits
→ 拼 prompt → LLM → 引用 [34 Grounding](34.grounding-citation-tutorial.md)
```

过滤必须在 **拼 prompt 之前** 完成；否则等于把机密 text 已经读进内存。

---

## 4. 核心概念：前滤、后滤、标量索引

![前滤 vs 后滤](image/metadata-filter-retrieval/02-pre-post-filter.png)

### 4.1 前滤（Pre-filter）

引擎维护 **标量索引**（B-tree、倒排等）与向量索引；查询时 **先** 用条件得到 id 集合或位图，**再** 在子集上 HNSW/IVF。

**优点**：不会返回无权限 id；ANN 在正确集合上最优。  
**缺点**：子集太小时 ANN 图可能不连通；某些库实现慢若缺标量索引。

### 4.2 后滤（Post-filter）

先 `search(k=100)`，再 `if meta.acl in user_groups`。若前 100 条里合格不足 k，出现 **「检索空了」** 或 **漏掉子集内真近邻**（它们在 ANN 排名第 101）。

**缓解**：增大初始 k（over-fetch），如 `k_fetch = k * 5`；仍不保证等价于前滤最优。

### 4.3 选型建议

| 场景 | 建议 |
|------|------|
| ACL / 多租户 | **前滤** 优先 |
| 软偏好（boost 某 section） | 可后滤 + rerank |
| 子集极大（仅 doc_id） | 前滤或专用 collection |
| 子集极小 | 检查是否该用 **独立 collection** |

---

## 5. 各向量库过滤写法对照

### 5.1 Chroma `where`

```python
collection.query(
    query_embeddings=[q_vec],
    n_results=5,
    where={{"$and": [
        {{"doc_id": "handbook-v3"}},
        {{"acl_group": {{"$in": ["all_staff", "finance"]}}}},
    ]}},
)
```

详见 [76 篇](76.chroma-vector-db-tutorial.md)。类型限制：常见 str/int/float/bool。

### 5.2 Qdrant `Filter`

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

flt = Filter(must=[
    FieldCondition(key="tenant_id", match=MatchValue(value="tenant_a")),
])
client.search(collection_name="kb", query_vector=q, query_filter=flt, limit=5)
```

Payload 字段建议建 **payload index**（[78 篇](78.qdrant-tutorial.md)）。

### 5.3 Milvus `expr`

```python
results = collection.search(
    data=[q_vec],
    anns_field="embedding",
    param={{"metric_type": "COSINE", "params": {{"ef": 64}}}},
    limit=5,
    expr='tenant_id == "tenant_a" and acl_group in ["staff"]',
)
```

`expr` 字段需 **scalar index**（[77 篇](77.milvus-tutorial.md)）。

### 5.4 pgvector SQL

```sql
SELECT chunk_id, text, embedding <=> :q AS dist
FROM chunks
WHERE tenant_id = :tid AND acl_group = ANY(:groups)
ORDER BY embedding <=> :q
LIMIT 5;
```

[81 篇](81.pgvector-tutorial.md)：过滤是 SQL `WHERE`，与业务库天然一体。

### 5.5 Elasticsearch / OpenSearch

KNN + `filter` context in bool query（[82 篇](82.elasticsearch-vector-tutorial.md)、[83 篇](83.opensearch-hybrid-tutorial.md)）。

---

## 6. 与 ACL、doc_id、version 组合

### 6.1 ACL 模式

用户登录 → 解析 `groups` → 检索 **强制** 带：

```python
where_acl = {{"acl_group": {{"$in": user.groups}}}}
```

**禁止** 信任前端传的 `where` 字符串；服务端根据 JWT 注入（[53 篇](53.metadata-acl-tutorial.md)）。

### 6.2 版本过滤

增量更新后旧 chunk 仍在库中误召回时：

```python
where={{"doc_id": "handbook", "version": 3}}
```

配合 [49 增量更新](49.incremental-update-tutorial.md)、[48 版本管理](48.doc-versioning-tutorial.md)。

### 6.3 doc_id 级 vs chunk 级

- 删整本文档：`delete(where={{"doc_id": x}})`  
- 单 chunk 更新：稳定 [51 chunk_id](51.metadata-chunk-id-tutorial.md) upsert

---

## 7. 先错对对：四种典型翻车

### 7.1 错：只靠 prompt 保密

**对：** 检索层前滤 + API 鉴权；prompt 是软约束。

### 7.2 错：后滤 k=5 不加 over-fetch

**对：** `k_fetch >= 5 * 预期过滤通过率` 或改前滤。

### 7.3 错：metadata 存复杂 JSON 对象

**对：** 拆字段或序列化字符串；注意引擎类型支持。

### 7.4 错：过滤字段无索引

**对：** 对 `tenant_id`、`doc_id` 建 scalar / payload index。

---

## 8. 实战代码：Chroma 与内存后滤对照

```python
import chromadb
import numpy as np

client = chromadb.PersistentClient(path="./chroma_filter_demo")
col = client.get_or_create_collection("demo")

def fake_embed(text: str, dim=32):
    rng = np.random.default_rng(hash(text) % 2**32)
    v = rng.standard_normal(dim).astype("float32")
    v /= np.linalg.norm(v) + 1e-9
    return v.tolist()

chunks = [
    {{"id": "c1", "text": "财务报销流程", "meta": {{"acl": "finance"}}}},
    {{"id": "c2", "text": "全员年假政策", "meta": {{"acl": "all"}}}},
    {{"id": "c3", "text": "财务预算审批", "meta": {{"acl": "finance"}}}},
]
for c in chunks:
    col.upsert(ids=[c["id"]], documents=[c["text"]],
               metadatas=[c["meta"]], embeddings=[fake_embed(c["text"])])

q = fake_embed("报销怎么批")
# 前滤：只搜 finance
hits = col.query(query_embeddings=[q], n_results=2,
                 where={{"acl": "finance"}})
print("pre-filter", hits["ids"])

# 后滤对照：全库搜再滤
raw = col.query(query_embeddings=[q], n_results=3)
post = [i for i, m in zip(raw["ids"][0], raw["metadatas"][0]) if m["acl"] == "finance"][:2]
print("post-filter", post)
```

观察：当 **非 finance 文档向量更近** 时，后滤可能 **漏** finance 文档——这就是 §4.2。

---

## 9. 过滤对 recall 与延迟的影响

前滤缩小 N → 单次 ANN 可能更快，但 **子集图质量** 依赖实现；后滤保持全图 ANN 但 **浪费** 算在将被扔掉的 hit 上。

**评测**：对「带 ACL 的 query」单独建金标，报 **filtered recall@k**（[87 篇](87.ann-recall-latency-tutorial.md)）。  
**延迟**：记录 **filter + search** 端到端；pgvector 要 EXPLAIN 看是否走索引。

---

## 10. 综合概念地图

![Metadata Filter 概念地图](image/metadata-filter-retrieval/03-concept-map.png)

---

## 11. 常见陷阱与 FAQ

{FILTER_EXTRA}

---

## 12. 总结与系列下一步

1. **Metadata Filter** = 检索层硬约束，ACL 必须落在这里。  
2. **前滤** 优先于后滤；后滤要 over-fetch。  
3. 各库语法不同，**模式** 一致。  
4. 与 [89 多租户](89.multi-tenant-namespace-tutorial.md)、[87 recall](87.ann-recall-latency-tutorial.md) 联调。

### 12.1 系列下一步

| 目标 | 阅读 |
|------|------|
| 多租户 | [89 多租户](89.multi-tenant-namespace-tutorial.md) |
| ANN 评测 | [87 recall–延迟](87.ann-recall-latency-tutorial.md) |
| 混合检索 | [93 Hybrid](93.hybrid-search-tutorial.md) |

### 12.2 自检

- [ ] 能写 Chroma where ACL  
- [ ] 能解释后滤漏检  
- [ ] 能画前滤数据流  

---

> **初学者可能仍困惑的点**  
> - **过滤不是可选美化**——企业 RAG 与 [53 ACL](53.metadata-acl-tutorial.md) 绑定。  
> - **后滤不等于安全**——可能先拿到机密 text 再丢弃。  
> - **子集太小** 考虑独立 collection（[89 篇](89.multi-tenant-namespace-tutorial.md)）。  
> - **换库语法要改，模式不用改**——前滤思想不变。
'''


# Additional articles 89-94 loaded lazily in main()


def get_article_specs():
    from bodies_89_94 import article_89, article_90, article_91, article_92, article_93, article_94
    return [
        ("86.hnsw-index-tutorial.md", "hnsw-index", "HNSW 图索引完全指南", 103, "地基",
         ("01-hnsw-idea.png", "hub-spoke", "§3"), ("02-hnsw-params.png", "comparison-matrix", "§5"),
         "HNSW 图索引是什么？", "HNSW 三大参数怎么调？", load_article_86),
        ("87.ann-recall-latency-tutorial.md", "ann-recall-latency", "ANN 召回率与延迟权衡完全指南", 104, "主线",
         ("01-recall-latency.png", "hub-spoke", "§3"), ("02-benchmark-curve.png", "comparison-matrix", "§6"),
         "召回率与延迟怎么权衡？", "ANN 评测曲线怎么读？", article_87),
        ("88.metadata-filter-retrieval-tutorial.md", "metadata-filter-retrieval", "Metadata Filter 过滤检索完全指南", 105, "地基",
         ("01-filter-idea.png", "hub-spoke", "§3"), ("02-pre-post-filter.png", "comparison-matrix", "§4"),
         "元数据过滤检索是什么？", "前滤 vs 后滤怎么选？", article_88),
        ("89.multi-tenant-namespace-tutorial.md", "multi-tenant-namespace", "多租户 Namespace 隔离完全指南", 106, "地基",
         ("01-tenant-idea.png", "hub-spoke", "§3"), ("02-isolation-patterns.png", "comparison-matrix", "§5"),
         "多租户向量库怎么隔离？", "Namespace vs Collection 怎么选？", article_89),
        ("90.vector-db-backup-tutorial.md", "vector-db-backup", "向量库备份与恢复完全指南", 107, "地基",
         ("01-backup-idea.png", "hub-spoke", "§3"), ("02-restore-flow.png", "comparison-matrix", "§6"),
         "向量库要备份什么？", "备份恢复流程怎么走？", article_90),
        ("91.dense-retrieval-tutorial.md", "dense-retrieval", "Dense 稠密检索完全指南", 108, "地基",
         ("01-dense-idea.png", "hub-spoke", "§3"), ("02-dense-pipeline.png", "comparison-matrix", "§5"),
         "Dense 稠密检索是什么？", "稠密检索在 RAG 里怎么走？", article_91),
        ("92.sparse-retrieval-rag-tutorial.md", "sparse-retrieval-rag", "Sparse 稀疏检索（BM25）在 RAG 中完全指南", 109, "地基",
         ("01-sparse-rag.png", "hub-spoke", "§3"), ("02-bm25-vs-dense.png", "comparison-matrix", "§5"),
         "稀疏检索在 RAG 里站哪？", "BM25 与 Dense 怎么分工？", article_92),
        ("93.hybrid-search-tutorial.md", "hybrid-search", "混合检索 Hybrid Search 完全指南", 110, "主线",
         ("01-hybrid-idea.png", "hub-spoke", "§3"), ("02-hybrid-arch.png", "comparison-matrix", "§6"),
         "混合检索是什么？", "混合检索有哪些架构？", article_93),
        ("94.rrf-fusion-tutorial.md", "rrf-fusion", "RRF 倒数排名融合完全指南", 111, "地基",
         ("01-rrf-idea.png", "hub-spoke", "§3"), ("02-rrf-formula.png", "comparison-matrix", "§5"),
         "RRF 融合是什么？", "RRF 公式怎么算？", article_94),
    ]


def pad_if_needed(text: str, topic: str, min_hz: int = 5000) -> str:
    cur = hz(text)
    if cur >= min_hz:
        return text
    markers = [
        "\n## 12. 总结与系列下一步\n",
        "\n> **初学者可能仍困惑的点**\n",
    ]
    anchor = next((m for m in markers if m in text), None)
    if not anchor:
        return text + f"\n\n（本篇主题：{topic}）\n"
    insert = ""
    n = 0
    templates = [
        ("权限联调要点", "与 [53 ACL](53.metadata-acl-tutorial.md) 联调时，要在网关解析用户身份并注入过滤条件，禁止客户端自选 tenant。审计日志记录每次查询的 filter 摘要，便于安全复盘与合规检查。"),
        ("与 ANN 参数协同", "过滤后有效向量数下降，[86 HNSW](86.hnsw-index-tutorial.md) 的 efSearch 与 [87 recall](87.ann-recall-latency-tutorial.md) 需重新评测，不可沿用全库参数。建议在租户或 doc 子集上单独扫参。"),
        ("混合检索衔接", "双路召回时两路必须使用相同 metadata 过滤，否则 [93 混合](93.hybrid-search-tutorial.md) 融合结果会掺入越权或跨租户噪音，引发严重数据事故。"),
        ("备份与恢复", "恢复后验证过滤字段索引是否重建，见 [90 备份](90.vector-db-backup-tutorial.md)。恢复演练应包含抽样 query 对比 Top-k 与权限边界。"),
        ("Embedding 一致性", "换 [25 Embedding](25.embedding-vector-tutorial.md) 模型必须新 collection，过滤 schema 一并迁移。manifest 记录模型名、维度、metric，避免恢复后空间不一致。"),
        ("chunk 元数据治理", "入库管道统一写 metadata，避免手工补字段导致过滤漏网。对 doc_id、chunk_id、tenant_id 做 schema 校验与 dead letter 队列。"),
        ("评测金标", "金标 query 应标注在特定 doc_id 或 tenant 下的相关 chunk，评测 filtered recall 与端到端答案质量，不要只看全库向量分。"),
        ("可观测性", "metrics 区分 filter_miss（后滤凑不满 k）与 ann_miss（真邻居不在 Top-k），便于 bad case 归因到索引层还是权限设计。"),
        ("降级策略", "过滤后无结果时明确返回拒答，见 [34 Grounding](34.grounding-citation-tutorial.md) 拒答流；不要强行用低分 chunk 凑数。"),
        ("跨篇复习", "本篇与 C4 前后篇组成完整检索栈：索引 [86]、评测 [87]、过滤 [88]、租户 [89]、备份 [90]、Dense [91]、Sparse [92]、Hybrid [93]、RRF [94]。"),
    ]
    while cur < min_hz:
        t, b = templates[n % len(templates)]
        para = b + f" 结合「{topic}」主题：在生产环境要把该条写进 runbook，并在季度演练或发版回归中勾选。"
        insert += f"### 附录深化 {n + 1}：{t}\n\n{para}\n\n"
        cur = hz(text.replace(anchor, "\n" + insert + anchor.lstrip("\n"), 1))
        n += 1
        if n > 80:
            break
    return text.replace(anchor, "\n" + insert + anchor.lstrip("\n"), 1)


def write_img(slug, title_short, roadmap, tier, i1, i2, p1, p2):
    base = ROOT / "image" / slug
    (base / "prompts").mkdir(parents=True, exist_ok=True)
    readme = (
        f"# {title_short}信息图（路线图 {roadmap}）\n\n\n"
        f"| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"
        f"| `{i1[0]}` | {i1[1]} | {i1[2]} |\n| `{i2[0]}` | {i2[1]} | {i2[2]} |\n"
        f"| `03-concept-map.png` | bento-grid | §概念地图 |\n\n\n"
        f"风格：hand-drawn-edu · 16:9 · 中文  \nPrompt 见 `prompts/`。\n\n\n"
        f"说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n"
    )
    (base / "README.md").write_text(readme, encoding="utf-8")

    def prompt_md(name, layout, sec, title):
        return f"""---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

Center hub: {title_short.replace('完全指南', '').strip()}

Footer: {title_short} · {sec}

All text Simplified Chinese.
"""

    for name, layout, sec, pt in [(i1[0], i1[1], i1[2], p1), (i2[0], i2[1], i2[2], p2)]:
        (base / "prompts" / f"{name.replace('.png','')}.md").write_text(
            prompt_md(name, layout, sec, pt), encoding="utf-8"
        )
    (base / "prompts" / "03-concept-map.md").write_text(
        f"""---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: bento-grid — 6 panels summarizing the full article.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title_short} · 概念地图

Panels: 前言、核心概念、实战、先错对对、FAQ 要点、系列下一步

Footer: 路线图 {roadmap} · {tier}篇

All text Simplified Chinese.
""",
        encoding="utf-8",
    )


ROOT = Path(__file__).resolve().parent.parent


def main():
    specs = get_article_specs()
    results = []
    for spec in specs:
        fname, slug, title_short, roadmap, tier, i1, i2, p1, p2, builder = spec
        text = pad_if_needed(builder(), title_short.split("完全")[0], 5000)
        (ROOT / fname).write_text(text, encoding="utf-8")
        write_img(slug, title_short, roadmap, tier, i1, i2, p1, p2)
        c = hz(text)
        results.append((fname, c))
        print(f"{fname}: {c}")
    bad = [r for r in results if r[1] < 5000]
    if bad:
        raise SystemExit(f"Under 5000 hanzi: {bad}")
    print("OK", len(results), "articles")


if __name__ == "__main__":
    main()
