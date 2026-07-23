# -*- coding: utf-8 -*-
"""Article bodies for tutorials 128-136."""

SHARED_FOOTER = """
---

*系列：D 框架与架构 · 路线图第 {roadmap} 条 · {tier}*
"""

def article_128():
    return ('''# D 框架与架构（四）：LangChain VectorStore 集成完全指南

> [127 篇](127.langchain-retriever-tutorial.md) 讲 **Retriever 抽象**——`query → list[Document]`；本篇下沉到 **VectorStore（向量存储封装）**：如何把 [76 Chroma](76.chroma-vector-db-tutorial.md)、[75 FAISS](75.faiss-ann-tutorial.md) 的 **入库与相似度搜索** 包成 LangChain 统一接口，并对接 [126 LCEL](126.langchain-lcel-tutorial.md) 与 `as_retriever()`。这是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 主线篇**（路线图第 **145** 条）。前置：[25 Embedding](25.embedding-vector-tutorial.md)、[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[125 核心](125.langchain-core-tutorial.md)、[126 LCEL](126.langchain-lcel-tutorial.md)、[127 Retriever](127.langchain-retriever-tutorial.md)。

---

## 目录

1. [前言：从向量引擎到框架 VectorStore](#1-前言从向量引擎到框架-vectorstore)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [VectorStore 是什么](#3-vectorstore-是什么)
4. [核心概念：Embedding、add_documents、similarity_search](#4-核心概念embeddingadd_documentssimilarity_search)
5. [Chroma 与 FAISS 集成对照](#5-chroma-与-faiss-集成对照)
6. [持久化、collection 与元数据过滤](#6-持久化collection-与元数据过滤)
7. [as_retriever 与 search_kwargs](#7-as_retriever-与-search_kwargs)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：双后端 Mini-RAG](#9-综合实战双后端-mini-rag)
10. [与 C 模块概念映射](#10-与-c-模块概念映射)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：从向量引擎到框架 VectorStore

C 模块你手写 `embed()` + `index.add()` + `search()`；[76 Chroma](76.chroma-vector-db-tutorial.md) 把 **向量+文本+元数据** 收进 Collection；[127 Retriever](127.langchain-retriever-tutorial.md) 再往上抽象 **检索接口**。中间还缺一层：**LangChain VectorStore**——让 `Document` 列表 **一次 add**，`similarity_search(query, k)` **统一返回 Document**，换 Chroma/FAISS **不改 LCEL 链的中间段**。

**读完本文，你应该能做到：**

1. 用 **Chroma / FAISS** 创建 LangChain VectorStore 并完成 ingest。  
2. 配置 **Embedding 类**（与 [25 篇](25.embedding-vector-tutorial.md) 模型一致）。  
3. 写 **`similarity_search` + metadata filter**（ACL）。  
4. **`as_retriever(search_kwargs=...)`** 接入 [126 LCEL](126.langchain-lcel-tutorial.md)。  
5. 口述 **原生 API vs LC 封装** 排障路径。  
6. 识别 §8 四种翻车：混模型、忘 persist、filter 键错、维数不一致。

### 1.1 路线图位置

```text
75 FAISS / 76 Chroma（引擎与向量库）
127 Retriever（检索抽象）
145 VectorStore 集成 ← 本篇（框架封装入库+搜索）
146 Document Loader / 147 Text Splitter
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 向量存储 | VectorStore | Document 的向量索引封装 |
| 嵌入模型 | Embeddings | 文本→向量，ingest 与 query 必须同一套 |
| 相似度搜索 | similarity_search | 返回 Top-K Document |
| 检索器工厂 | as_retriever | VectorStore→Retriever |

### 1.3 读完本篇的最小交付物

1. Chroma `from_documents` + `persist_directory`；  
2. FAISS `save_local` / `load_local`；  
3. 带 `filter` 的 `as_retriever`；  
4. 与 [76] 原生 `collection.query` 对照实验；  
5. §8 先错对对四条口述。

---

## 2. 本文边界与动手路径

**档位：D 主线篇（路线图 145）。**

**本文讲：** LangChain VectorStore 概念、Chroma/FAISS 集成、Embedding 注入、持久化、过滤、接 Retriever/LCEL。  
**本文不讲：** 每一个社区 VectorStore 适配器、Milvus 集群、混合检索细节（见 [93](93.hybrid-search-tutorial.md)）、Embedding 训练（见 [73](73.embedding-finetune-tutorial.md)）。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §3～§4，画 VectorStore 在链中的位置 | 白板能讲 |
| B | `pip install langchain-community langchain-openai chromadb faiss-cpu` | 无 import 错 |
| C | §9 Chroma 端到端 | similarity_search 有结果 |
| D | §9 FAISS 对照 | Top-3 与 Chroma 一致（同向量） |
| E | `as_retriever` + filter | 无权用户无 finance 命中 |
| F | §8 先错对对 | 四种错法 |

**环境：** Python 3.10+；Embedding 可用 `FakeEmbeddings` 或 OpenAI/BGE（需 Key）。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| Document | [125 核心](125.langchain-core-tutorial.md) |
| 向量与 metric | [25](25.embedding-vector-tutorial.md)、[26](26.similarity-metrics-tutorial.md) |
| FAISS | [75](75.faiss-ann-tutorial.md) |
| Chroma | [76](76.chroma-vector-db-tutorial.md) |
| Retriever | [127](127.langchain-retriever-tutorial.md) |
| chunk 元数据 | [50-53](51.metadata-chunk-id-tutorial.md) |

---

## 3. VectorStore 是什么

读下图：VectorStore 在 RAG ingest 与 query 两侧各做什么。

![LangChain VectorStore 是什么](image/langchain-vectorstore/01-vectorstore-idea.png)

对照上图：

- **左侧 ingest**：`list[Document]` + `Embeddings.embed_documents` → 写入底层引擎；  
- **右侧 query**：`Embeddings.embed_query` → ANN 搜索 → `list[Document]`；  
- **对上层**：与 [127 Retriever](127.langchain-retriever-tutorial.md) 通过 `as_retriever()` 衔接；  
- **对下层**：Chroma Collection 或 FAISS Index + docstore。

通俗说：**VectorStore = Embedding 函数 + 向量引擎 + Document 序列化胶水**。

### 3.1 为什么需要这一层

| 痛点 | VectorStore 做法 |
|------|------------------|
| 换 Chroma→FAISS 改一堆脚本 | 换构造类，链不变 |
| ingest 忘写 metadata | `from_documents` 强制走 Document |
| 检索返回裸 dict | 统一 `Document` 类型 |
| 评测与 LCEL 不一致 | 同一 `as_retriever` |

### 3.2 VectorStore 不是 Retriever

- **VectorStore**：偏 **存储与相似度**（`add_documents`、`similarity_search_by_vector`）；  
- **Retriever**：偏 **检索策略**（`invoke(query)`，可包装 VectorStore 或 BM25、混合等）。  
精排 [96 BGE](96.bge-reranker-tutorial.md) 在两者 **之后**。

---

## 4. 核心概念：Embedding、add_documents、similarity_search

### 4.1 Embeddings 接口

LangChain 的 `Embeddings` 协议：

```python
class Embeddings(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
```

**铁律**（[25 篇](25.embedding-vector-tutorial.md)）：ingest 与 query **同一模型、同一维度、同一归一化策略**（[66 L2](66.l2-normalization-tutorial.md)）。

### 4.2 最小 Chroma VectorStore（代码不裸奔）

```python
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings

docs = [
    Document(
        page_content="员工差旅报销上限为每人每天 600 元。",
        metadata={"doc_id": "handbook-v3", "chunk_id": "hb:v3:c001", "acl_group": "all_staff"},
    ),
    Document(
        page_content="财务专用：预算审批需 CFO 签字。",
        metadata={"doc_id": "finance-v1", "chunk_id": "fin:v1:c001", "acl_group": "finance_only"},
    ),
]

embedding = FakeEmbeddings(size=1536)
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embedding,
    persist_directory="./chroma_lc_db",
    collection_name="handbook_bge_fake_v1",
)

hits = vectorstore.similarity_search("差旅报销标准", k=2)
for d in hits:
    print(d.metadata.get("chunk_id"), d.page_content[:40])
```

### 4.3 similarity_search 变体

| 方法 | 场景 |
|------|------|
| `similarity_search` | 文本 query，内部 embed_query |
| `similarity_search_by_vector` | 已有 query 向量 |
| `similarity_search_with_score` | 需要距离/分数阈值 [99](99.score-threshold-tutorial.md) |
| `max_marginal_relevance_search` | 需要多样性 [105 MMR](105.mmr-diversity-tutorial.md) |

### 4.4 add_documents 与 upsert

增量场景（[49 增量](49.incremental-update-tutorial.md)）：

```python
new_docs = [Document(page_content="...", metadata={"chunk_id": "hb:v3:c099"})]
vectorstore.add_documents(new_docs, ids=["hb:v3:c099"])
```

Chroma 底层走 upsert；FAISS 需留意 **id 与 docstore** 一致性——删改常 **重建索引** 或维护 sidecar（[75 篇](75.faiss-ann-tutorial.md)）。

---

## 5. Chroma 与 FAISS 集成对照

![Chroma vs FAISS VectorStore](image/langchain-vectorstore/02-chroma-vs-faiss.png)

### 5.1 Chroma 路径

```python
from langchain_community.vectorstores import Chroma

vs = Chroma(
    persist_directory="./chroma_lc_db",
    embedding_function=embedding,
    collection_name="handbook_bge_fake_v1",
)
# 已存在则加载；新 ingest 用 from_documents
```

**优势**：`persist_directory`、[76 篇](76.chroma-vector-db-tutorial.md) 原生 `where` 过滤、documents 字段自带原文。

### 5.2 FAISS 路径

```python
from langchain_community.vectorstores import FAISS

vs = FAISS.from_documents(docs, embedding)
vs.save_local("./faiss_lc_index")
vs2 = FAISS.load_local("./faiss_lc_index", embedding, allow_dangerous_deserialization=True)
```

**优势**：纯 ANN 性能、教学对齐 [75 篇](75.faiss-ann-tutorial.md)；**劣势**：元数据过滤常需 **后滤** 或自建 docstore 映射。

### 5.3 选型速查

| 维度 | LC Chroma | LC FAISS |
|------|-----------|----------|
| 持久化 | 内置 | save_local |
| metadata 过滤 | 较好 | 视版本/配置 |
| 大规模 | 中等 | 引擎强、存储自理 |
| 排障 | 可落原生 Chroma API | 看 index + pkl |

---

## 6. 持久化、collection 与元数据过滤

### 6.1 collection 命名

建议：`{知识库}_{embed模型简写}_{schema版本}`。换 Embedding **必须新 collection**（[76 §8](76.chroma-vector-db-tutorial.md) 先错对对）。

### 6.2 metadata filter（ACL）

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5,
        "filter": {"acl_group": "all_staff"},
    },
)
docs = retriever.invoke("报销流程")
```

与 [53 ACL](53.metadata-acl-tutorial.md)、[121 无权过滤](121.unauthorized-doc-filter-tutorial.md) 一致：**过滤在检索侧**，不是生成后掩码。

### 6.3 距离阈值

```python
docs_and_scores = vectorstore.similarity_search_with_score("预算审批", k=10)
filtered = [(d, s) for d, s in docs_and_scores if s < 0.35]
```

阈值需用金标集调（[99 篇](99.score-threshold-tutorial.md)）。

---

## 7. as_retriever 与 search_kwargs

![VectorStore 到 Retriever](image/langchain-vectorstore/03-to-retriever.png)

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_messages([
    ("system", "仅根据上下文回答。\\n\\n{context}"),
    ("human", "{question}"),
])

def format_docs(ds):
    return "\\n\\n".join(f"[{i+1}] {d.page_content}" for i, d in enumerate(ds))

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)
# answer = chain.invoke("差旅每天多少钱？")
```

详见 [126 LCEL](126.langchain-lcel-tutorial.md)、[127 Retriever](127.langchain-retriever-tutorial.md)。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：ingest 与 query 用了不同 Embedding

```python
# 错：入库 OpenAI，查询换成本地 BGE
```

**现象**：相似度随机，Recall@3 崩塌。  
**对**：`embedding` 构造器全局单例；collection 名含模型版本。

### 8.2 错：FAISS load_local 时 embedding 为 None

**现象**：`embed_query` 报错或维数 0。  
**对**：`load_local(path, embeddings, allow_dangerous_deserialization=True)` 传入 **同一 Embeddings 类**。

### 8.3 错：filter 字段类型与 Chroma 不一致

```python
filter={"version": 1}  # 若入库写成 "1" 字符串则永远滤空
```

**对**：metadata 类型在 [50-54](54.metadata-timestamp-version-tutorial.md) 规范中 **写死 schema**。

### 8.4 错：把精排塞进 VectorStore

**现象**：`similarity_search` 里调 cross-encoder，延迟爆炸。  
**对**：宽召回 k=50 → [96 精排](96.bge-reranker-tutorial.md) → top5 → [107 预算](107.context-budget-tutorial.md)。

---

## 9. 综合实战：双后端 Mini-RAG

**目标**：同一 `DOCS` 列表，Chroma 与 FAISS 各建 VectorStore，对比 Top-3；再接入 `as_retriever` + 最小 LCEL。

```python
"""mini_rag_vectorstore.py — 路线图 145 综合实战"""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma, FAISS

DOCS = [
    Document("公司年假：工龄满一年享 10 天。", {"doc_id": "hr-v1", "chunk_id": "hr:c1", "acl_group": "all_staff"}),
    Document("研发部弹性工时：核心 10:00-16:00。", {"doc_id": "eng-v1", "chunk_id": "eng:c1", "acl_group": "engineering"}),
    Document("财务报表季度锁账期为次月第 5 个工作日。", {"doc_id": "fin-v1", "chunk_id": "fin:c1", "acl_group": "finance_only"}),
]

def build_stores(embed_size: int = 128):
    emb = FakeEmbeddings(size=embed_size)
    chroma = Chroma.from_documents(DOCS, emb, persist_directory="./demo_chroma", collection_name="demo_v1")
    faiss = FAISS.from_documents(DOCS, emb)
    return chroma, faiss, emb

def compare(query: str, k: int = 3):
    chroma, faiss, _ = build_stores()
    c_hits = chroma.similarity_search(query, k=k)
    f_hits = faiss.similarity_search(query, k=k)
    print("Chroma:", [d.metadata["chunk_id"] for d in c_hits])
    print("FAISS:", [d.metadata["chunk_id"] for d in f_hits])

def acl_demo():
    chroma, _, _ = build_stores()
    r = chroma.as_retriever(search_kwargs={"k": 5, "filter": {"acl_group": "all_staff"}})
    ids = [d.metadata["chunk_id"] for d in r.invoke("财务锁账")]
    assert "fin:c1" not in ids, "ACL 过滤失败"
    print("ACL OK:", ids)

if __name__ == "__main__":
    compare("年假有多少天")
    acl_demo()
```

**验收**：Chroma/FAISS Top-3 `chunk_id` 一致；`acl_demo` 不泄露 `fin:c1`。

---

## 10. 与 C 模块概念映射

| C 模块手写 | LangChain VectorStore |
|------------|----------------------|
| `embed_texts()` | `Embeddings.embed_documents` |
| `collection.add` | `add_documents` / `from_documents` |
| `collection.query` | `similarity_search` |
| `where` 过滤 | `search_kwargs["filter"]` |
| `as_retriever` 手写包装 | `vectorstore.as_retriever()` |

**原则**：能手写 [76](76.chroma-vector-db-tutorial.md) 原生 API，再用 LC 封装 **省胶水**；出问题 **下沉到原生层** 查 count/where/embed。

---

## 11. 综合概念地图

![VectorStore 概念地图](image/langchain-vectorstore/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| Embeddings | ingest/query 对称 |
| from_documents | 批量入库 |
| similarity_search | Top-K Document |
| as_retriever | 接 LCEL |
| Chroma vs FAISS | 库 vs 引擎 |
| 下一步 | [129 Loader](129.langchain-document-loader-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：VectorStore 和 Retriever 必须先学哪个？**  
A：先本篇 VectorStore（存与搜），再 [127 Retriever](127.langchain-retriever-tutorial.md)（策略与组合）。

**Q：能否混用 LangChain Chroma 与原生 chromadb Client？**  
A：可以，同一 `persist_directory`；注意 **collection 名** 与 **embedding 函数** 一致。

**Q：`from_documents` 很慢怎么办？**  
A：[67 批处理](67.embedding-batching-tutorial.md)、异步 ingest 队列（路线图 159+）、先写 JSONL 再批量 embed。

**Q：FAISS 如何做 ACL？**  
A：宽召回后 Python 过滤 metadata，或 [88 元数据过滤](88.metadata-filter-retrieval-tutorial.md) 引擎；Chroma `where` 更省事。

**Q：MMR 与 similarity 何时切换？**  
A：同一 doc 多 chunk 霸占 Top-K 时用 [105 MMR](105.mmr-diversity-tutorial.md)。

**Q：和 [65 Parent Document](65.parent-document-retriever-tutorial.md)？**  
A：child chunk 入 VectorStore；parent 存 SQL/另一 collection；Retriever 层扩展。

**Q：生产如何版本化索引？**  
A：新 collection + 双写 + 切流量（[48 版本](48.doc-versioning-tutorial.md)、[152 自研 vs 框架](135.pipeline-vs-framework-tutorial.md)）。

**Q：OpenAI Embedding 维度变了怎么办？**  
A：新 collection 全量重建；旧库只读；绝不在同索引混维。

### 12.1 读路径自检

1. `embed_documents` 与 `embed_query` 区别？  
2. 为何换模型要新 collection？  
3. `as_retriever` 的 filter 解决什么？  
4. FAISS save/load 必传什么？  
5. VectorStore 与 [93 混合检索](93.hybrid-search-tutorial.md) 如何衔接？  
6. 排障第一步查什么？

---

## 13. 总结与系列下一步

LangChain **VectorStore** 把 [76 Chroma](76.chroma-vector-db-tutorial.md)、[75 FAISS](75.faiss-ann-tutorial.md) 的 **入库与相似度搜索** 统一成 `Document` 流，是 [127 Retriever](127.langchain-retriever-tutorial.md) 与 [126 LCEL](126.langchain-lcel-tutorial.md) 的 **地基**。

**本篇交付物**：Chroma/FAISS 双后端、ACL filter、`as_retriever`、§8 先错对对、与 C 模块映射表。

**建议下一步**：

1. [129 Document Loader](129.langchain-document-loader-tutorial.md)——文件→Document；  
2. [130 Text Splitter](130.langchain-text-splitter-tutorial.md)——长文→chunk；  
3. 复习 [76 Chroma](76.chroma-vector-db-tutorial.md) 原生 `where`；  
4. [135 自研 vs 框架](135.pipeline-vs-framework-tutorial.md)——哪层坚持原生 API。

''' + SHARED_FOOTER.format(roadmap="145", tier="主线篇"))

# Due to file size, remaining articles are built by functions imported from part 2
from _articles_128_136_content_part2 import (  # noqa: E402
    article_129,
    article_130,
    article_131,
    article_132,
    article_133,
    article_134,
    article_135,
    article_136,
)

ARTICLE_SPECS = [
    (
        "128.langchain-vectorstore-tutorial.md",
        "langchain-vectorstore",
        article_128(),
        [
            ("01-vectorstore-idea.png", "hub-spoke", "§3 VectorStore 是什么"),
            ("02-chroma-vs-faiss.png", "comparison-matrix", "§5 Chroma 与 FAISS"),
            ("03-to-retriever.png", "flowchart", "§7 as_retriever"),
            ("03-concept-map.png", "bento-grid", "§11 概念地图"),
        ],
        [
            ("01-vectorstore-idea.md", "hub-spoke", "LangChain VectorStore 是什么？",
             "Center: Document + Embedding + 引擎\nSpoke 1: add_documents\nSpoke 2: similarity_search\nSpoke 3: as_retriever\nSpoke 4: vs 原生 Chroma/FAISS",
             "VectorStore 集成 · §3"),
            ("02-chroma-vs-faiss.md", "comparison-matrix", "Chroma vs FAISS VectorStore",
             "Compare 持久化 / 过滤 / 性能 / 排障路径",
             "VectorStore 集成 · §5"),
            ("03-to-retriever.md", "flowchart", "VectorStore → Retriever → LCEL",
             "Flow: from_documents → as_retriever → LCEL chain",
             "VectorStore 集成 · §7"),
            ("03-concept-map.md", "bento-grid", "VectorStore 概念地图",
             "Tiles: Embeddings, from_documents, similarity_search, as_retriever, Chroma/FAISS, 下一步 Loader",
             "VectorStore 集成 · §11"),
        ],
    ),
]

# Append specs from part2 builder
ARTICLE_SPECS.extend(
    __import__("_articles_128_136_content_part2").build_specs()
)
