# -*- coding: utf-8 -*-
"""Articles 129-136 for batch 128-136."""

SHARED_FOOTER = """
---

*系列：D 框架与架构 · 路线图第 {roadmap} 条 · {tier}*
"""

def article_129():
    return ('''# D 框架与架构（五）：LangChain Document Loader 完全指南

> RAG 第一步不是 Embedding，而是 **把磁盘上的文件变成 `Document`**。[125 篇](125.langchain-core-tutorial.md) 定义了 `page_content + metadata`；本篇讲 **LangChain Document Loader（文档加载器）**：`PyPDFLoader`、`TextLoader`、`DirectoryLoader` 等如何把 PDF、Markdown、HTML 读入统一列表，并对接 [130 Text Splitter](130.langchain-text-splitter-tutorial.md) 与 [128 VectorStore](128.langchain-vectorstore-tutorial.md)。这是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 主线篇**（路线图第 **146** 条）。前置：[36 PDF 提取](36.pdf-text-extraction-tutorial.md)、[38 Markdown](38.markdown-parsing-tutorial.md)、[50 doc_id](50.metadata-doc-id-tutorial.md)、[125 核心](125.langchain-core-tutorial.md)。

---

## 目录

1. [前言：Loader 在 RAG 链路最前端](#1-前言loader-在-rag-链路最前端)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Document Loader 是什么](#3-document-loader-是什么)
4. [核心概念：load、lazy_load、metadata](#4-核心概念loadlazy_loadmetadata)
5. [常用 Loader 选型](#5-常用-loader-选型)
6. [目录批量与增量加载](#6-目录批量与增量加载)
7. [编码、MIME 与解析边界](#7-编码mime-与解析边界)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：多格式知识库 ingest](#9-综合实战多格式知识库-ingest)
10. [与 C 模块 Parser 对照](#10-与-c-模块-parser-对照)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：Loader 在 RAG 链路最前端

企业知识库有 PDF 制度、Markdown 技术文档、Confluence 导出 HTML、SharePoint docx。C 模块你用 [42 PyMuPDF](42.pymupdf-tutorial.md)、[38 Markdown AST](38.markdown-parsing-tutorial.md) 手写解析；D 模块用 **Loader** 统一 **「路径/句柄 → list[Document]」**，让后续 [130 Splitter](130.langchain-text-splitter-tutorial.md)、[128 VectorStore](128.langchain-vectorstore-tutorial.md) **只认 Document**。

**读完本文，你应该能做到：**

1. 用 **TextLoader / PyPDFLoader / Unstructured** 加载样例文件。  
2. 写 **`DirectoryLoader` 批量 glob**。  
3. 在 metadata 写入 **doc_id、source、page**（[50-52](52.metadata-source-page-tutorial.md)）。  
4. 区分 **Loader vs Parser** 职责（衔接 [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md)）。  
5. 完成 §8 四种先错对对。

### 1.1 路线图位置

```text
125 Document 原子
146 Document Loader ← 本篇
147 Text Splitter
128 VectorStore ingest
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 文档加载器 | Document Loader | 文件→list[Document] |
| 惰性加载 | lazy_load | 大目录逐条产出，省内存 |
| 来源元数据 | source metadata | 溯源与增量键 |
| 批量加载 | DirectoryLoader | glob 多文件 |

### 1.3 最小交付物

1. 三种格式各 load 成功；  
2. metadata 含 `source` 与 `doc_id`；  
3. `lazy_load` 演示；  
4. 与手写 Parser 输出 diff 一份。

---

## 2. 本文边界与动手路径

**档位：D 主线篇（路线图 146）。**

**本文讲：** Loader 概念、常用实现、metadata 规范、批量与增量、与 Parser 边界。  
**本文不讲：** OCR 全流程（[55](55.ocr-scanned-docs-tutorial.md)）、复杂表格（[37](37.pdf-layout-tables-tutorial.md)）、Splitter 参数（[130](130.langchain-text-splitter-tutorial.md)）。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 白板：文件→Loader→Document |
| B | TextLoader UTF-8 |
| C | PyPDFLoader 带 page |
| D | DirectoryLoader glob |
| E | §9 综合脚本 |
| F | §8 先错对对 |

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| Document | [125](125.langchain-core-tutorial.md) |
| PDF | [36](36.pdf-text-extraction-tutorial.md)、[42](42.pymupdf-tutorial.md) |
| Markdown | [38](38.markdown-parsing-tutorial.md) |
| doc_id | [50](50.metadata-doc-id-tutorial.md) |
| 编码 | [41](41.text-encoding-detection-tutorial.md) |

---

## 3. Document Loader 是什么

![Document Loader 是什么](image/langchain-document-loader/01-loader-idea.png)

Loader 契约（概念上）：

```python
class BaseLoader:
    def load(self) -> list[Document]: ...
    def lazy_load(self) -> Iterator[Document]: ...
```

**输入**：文件路径、URL、数据库游标等；**输出**：`Document(page_content=str, metadata=dict)`。

### 3.1 在 RAG 管道中的位置

```text
[146 Loader] → [147 Splitter] → [25 Embed] → [128 VectorStore]
     ↑
[136 可插拔 Parser 接口]
```

Loader **不负责切块**（那是 Splitter），**不负责向量化**（那是 Embeddings）。

### 3.2 为什么不用裸 `open().read()`

| 裸读 | Loader |
|------|--------|
| 无统一 metadata | 自动 `source` |
| PDF 当文本乱码 | 调专用解析 |
| 难接 DirectoryLoader | glob 一键 |
| 评测不可复现 | 版本化 loader 类名 |

---

## 4. 核心概念：load、lazy_load、metadata

### 4.1 TextLoader（代码不裸奔）

```python
from langchain_community.document_loaders import TextLoader
from pathlib import Path

path = Path("data/handbook/差旅制度.txt")
loader = TextLoader(str(path), encoding="utf-8")
docs = loader.load()
assert len(docs) >= 1
doc = docs[0]
doc.metadata["doc_id"] = "handbook-travel-v3"
doc.metadata["mime"] = "text/plain"
print(doc.page_content[:80], doc.metadata)
```

### 4.2 PyPDFLoader 与页码

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/policies/员工手册.pdf")
pages = loader.load()
for p in pages[:3]:
    print(p.metadata.get("page"), p.page_content[:60])
```

`metadata["page"]` 对接 [52 source/page](52.metadata-source-page-tutorial.md) 与 [115 导航](115.source-document-navigation-tutorial.md)。

### 4.3 lazy_load 与大目录

```python
def ingest_lazy(loader):
    for doc in loader.lazy_load():
        yield doc  # 下游 splitter 可流式处理
```

十 GB 级目录 **禁止** 一次性 `load()` 进内存。

### 4.4 metadata 最小集

| 字段 | 用途 |
|------|------|
| source | 文件路径或 URL |
| doc_id | 业务主键 [50] |
| page | PDF 页码 |
| loaded_at | 增量同步 |
| loader | 审计：用的哪个 Loader |

---

## 5. 常用 Loader 选型

![常用 Loader 对比](image/langchain-document-loader/02-loader-types.png)

| Loader | 格式 | 备注 |
|--------|------|------|
| TextLoader | txt, md | 指定 encoding [41] |
| PyPDFLoader | pdf | 简单 PDF；扫描件需 [55 OCR] |
| UnstructuredFileLoader | 多格式 | 依赖 unstructured [44] |
| BSHTMLLoader | html | 配 [39 HTML 提取](39.html-content-extraction-tutorial.md) |
| Docx2txtLoader | docx | 轻量 word |
| CSVLoader | csv | 行级 Document |
| JSONLoader | json | jq schema 抽字段 |
| DirectoryLoader | 目录 | glob + 子 Loader |

### 5.1 DirectoryLoader 模式

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    "data/kb/",
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
    show_progress=True,
)
docs = loader.load()
print(f"loaded {len(docs)} markdown files")
```

### 5.2 选型决策树

1. 纯 Markdown/文本 → TextLoader；  
2. 电子版 PDF → PyPDFLoader 或 [42 PyMuPDF](42.pymupdf-tutorial.md) 自研再转 Document；  
3. 混合格式企业盘 → Unstructured / [45 Tika](45.apache-tika-tutorial.md)；  
4. 扫描 PDF → OCR 预处理再 Loader。

---

## 6. 目录批量与增量加载

### 6.1 增量键

配合 [49 增量更新](49.incremental-update-tutorial.md)：

```python
import hashlib
from datetime import datetime, timezone

def enrich_metadata(doc: "Document", path: str) -> "Document":
    text = Path(path).read_bytes()
    doc.metadata["content_hash"] = hashlib.sha256(text).hexdigest()[:16]
    doc.metadata["mtime"] = Path(path).stat().st_mtime
    doc.metadata["loaded_at"] = datetime.now(timezone.utc).isoformat()
    return doc
```

索引层对比 hash，**未变文件跳过**。

### 6.2 并发注意

DirectoryLoader 默认多进程可选；PDF 解析 CPU 重，**控制 worker 数**，避免打爆内存。

### 6.3 与任务队列

生产 ingest 常进 Celery（路线图 159）：Loader 在 worker 内执行，产出 Document 序列化进队列下一步 Splitter。

---

## 7. 编码、MIME 与解析边界

### 7.1 编码检测

Windows 上 txt 常见 GBK；未指定 encoding 时乱码（§8）。用 [41 编码检测](41.text-encoding-detection-tutorial.md) 或 `charset-normalizer`。

### 7.2 Loader 不是万能 Parser

复杂表格、多栏 PDF、内嵌图片：**Loader 只保证「能读出入库文本」**，精细结构在 C 模块或 [136 可插拔 Parser](136.pluggable-parser-splitter-embedder-tutorial.md)。

### 7.3 清洗钩子

```python
from langchain_core.documents import Document

def load_and_clean(loader) -> list[Document]:
    out = []
    for d in loader.load():
        text = d.page_content.replace("\\x00", "")
        text = "\\n".join(line.strip() for line in text.splitlines() if line.strip())
        out.append(Document(page_content=text, metadata=dict(d.metadata)))
    return out
```

衔接 [46 文本清洗](46.text-cleaning-tutorial.md)。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：TextLoader 不指定 encoding

**现象**：中文变 ``。  
**对**：`encoding="utf-8"` 或检测后传入。

### 8.2 错：PDF 当纯文本 open

**现象**：`%PDF-1.4` 进索引。  
**对**：必须用 PDF Loader 或 PyMuPDF。

### 8.3 错：忘记写 doc_id

**现象**：增量更新无法对齐 [48 版本](48.doc-versioning-tutorial.md)。  
**对**：load 后立即 `metadata["doc_id"] = 规范字符串`。

### 8.4 错：整本书一个 Document 不切块

**现象**：超出 [28 窗口](28.context-window-tutorial.md)，检索精度差。  
**对**：Loader 只负责 **页或文件级**；长文交 [130 Splitter](130.langchain-text-splitter-tutorial.md)。

---

## 9. 综合实战：多格式知识库 ingest

```python
"""ingest_loaders.py — 路线图 146 综合实战"""
from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document

DATA = Path("data/demo_kb")
DATA.mkdir(parents=True, exist_ok=True)

def seed_files():
  (DATA / "faq.md").write_text("# 年假\\n工龄满一年 10 天。", encoding="utf-8")
  # PDF 需自备 sample.pdf 放入 demo_kb

def load_markdown() -> list[Document]:
    loader = DirectoryLoader(
        str(DATA),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    for d in docs:
        d.metadata["doc_id"] = "kb-faq-v1"
        d.metadata["format"] = "markdown"
    return docs

def load_pdfs() -> list[Document]:
    pdfs = list(DATA.glob("**/*.pdf"))
    all_docs: list[Document] = []
    for p in pdfs:
        for d in PyPDFLoader(str(p)).load():
            d.metadata["doc_id"] = f"pdf-{p.stem}-v1"
            all_docs.append(d)
    return all_docs

def main():
    seed_files()
    docs = load_markdown() + load_pdfs()
    print(f"total documents: {len(docs)}")
    for d in docs[:5]:
        print(d.metadata.get("doc_id"), d.metadata.get("source", "")[-30:])

if __name__ == "__main__":
    main()
```

**下游**：`docs` 传入 [130](130.langchain-text-splitter-tutorial.md) → [128 VectorStore](128.langchain-vectorstore-tutorial.md)。

---

## 10. 与 C 模块 Parser 对照

| C 模块 | LangChain Loader |
|--------|------------------|
| 自研 `parse_pdf()` | PyPDFLoader / 自定义 BaseLoader |
| JSONL 中间态 | 可先写 JSONL 再 `JSONLoader` |
| 清洗管道 | load 后 Lambda 清洗 |
| 可插拔 | [136](136.pluggable-parser-splitter-embedder-tutorial.md) 定义 `Parser` 协议，Loader 可薄封装 |

---

## 11. 综合概念地图

![Loader 概念地图](image/langchain-document-loader/03-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| load | 一次读完 |
| lazy_load | 流式 |
| metadata | 溯源与 ACL |
| DirectoryLoader | 批量 |
| 下一步 | [130 Splitter](130.langchain-text-splitter-tutorial.md) |

---

## 12. 常见陷阱与 FAQ

**Q：Loader 与 Unstructured 关系？**  
A：Unstructured 是解析引擎；`UnstructuredFileLoader` 是其 LC 封装（[44](44.unstructured-io-tutorial.md)）。

**Q：网页 URL 怎么加载？**  
A：`WebBaseLoader` / `RecursiveUrlLoader`；注意 robots 与 [39 HTML](39.html-content-extraction-tutorial.md)。

**Q：metadata 能嵌套 dict 吗？**  
A：Chroma 等向量库常 **扁平键值**；嵌套请 JSON 字符串化。

**Q：如何测试 Loader？**  
A：金标文件 + 断言 `page_content` 片段与 metadata 字段。

**Q：多语言文件？**  
A：编码 + [70 混合语言 Embedding](70.mixed-language-embedding-tutorial.md) 分别处理。

**Q：Loader 要异步吗？**  
A：I/O 重时 `async` 变体或任务队列；小 PoC 同步即可。

**Q：和 [47 去重](47.doc-dedup-tutorial.md)？**  
A：load 后按 `content_hash` 去重再索引。

**Q：生产权限？**  
A：Loader 阶段就打 `acl_group`（[53](53.metadata-acl-tutorial.md)），别等检索才滤。

---

## 13. 总结与系列下一步

**Document Loader** 把多格式文件统一成 [125 Document](125.langchain-core-tutorial.md)，是 RAG **数据入口**。掌握 Loader + metadata 规范，后续 Splitter、VectorStore 才能 **可溯源、可增量**。

**建议下一步**：[130 Text Splitter](130.langchain-text-splitter-tutorial.md)、[128 VectorStore](128.langchain-vectorstore-tutorial.md)、[136 可插拔 Parser](136.pluggable-parser-splitter-embedder-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="146", tier="主线篇"))

def article_130():
    return ('''# D 框架与架构（六）：LangChain Text Splitter 完全指南

> Loader 读出长文后，必须 **切块（Chunking）** 才能 Embedding 与检索。C 模块学过 [57 固定长度](57.fixed-size-chunking-tutorial.md)、[58 递归字符](58.recursive-character-chunking-tutorial.md)、[60 重叠](60.chunk-overlap-tutorial.md)；本篇讲 **LangChain Text Splitter（文本分割器）** 如何把 `Document` 切成带 `start_index` 的子 Document，并对接 [128 VectorStore](128.langchain-vectorstore-tutorial.md)。这是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 地基篇**（路线图第 **147** 条）。前置：[57-65 切块系列](58.recursive-character-chunking-tutorial.md)、[51 chunk_id](51.metadata-chunk-id-tutorial.md)、[129 Loader](129.langchain-document-loader-tutorial.md)。

---

## 目录

1. [前言：切块决定检索上限](#1-前言切块决定检索上限)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Text Splitter 是什么](#3-text-splitter-是什么)
4. [核心概念：chunk_size、chunk_overlap、separators](#4-核心概念chunk_sizechunk_overlapseparators)
5. [RecursiveCharacterTextSplitter 详解](#5-recursivecharactertextsplitter-详解)
6. [结构感知：Markdown 与 HTML](#6-结构感知markdown-与-html)
7. [metadata 与 chunk_id 继承](#7-metadata-与-chunk_id-继承)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：制度文档切块入库](#9-综合实战制度文档切块入库)
10. [与 C 模块切块对照](#10-与-c-模块切块对照)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：切块决定检索上限

检索 **不会魔法**：模型只能看到 Top-K **chunk**。[61 篇](61.chunk-size-tradeoff-tutorial.md) 说太大稀释语义、太小丢上下文；[60 篇](60.chunk-overlap-tutorial.md) 说重叠防句界断裂。LangChain **Text Splitter** 把切块策略 **参数化、可复现**，输出仍是 `Document`，无缝接 [25 Embedding](25.embedding-vector-tutorial.md) 与 [128 VectorStore](128.langchain-vectorstore-tutorial.md)。

**读完本文，你应该能做到：**

1. 配置 **RecursiveCharacterTextSplitter** 的 size/overlap。  
2. 使用 **MarkdownHeaderTextSplitter** 保标题层级。  
3. 为每个 chunk 生成 **chunk_id**（[51](51.metadata-chunk-id-tutorial.md)）。  
4. 对照 C 模块手写切块 **diff 边界**。  
5. §8 四种先错对对。

### 1.1 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 文本分割器 | Text Splitter | 长文→多个 Document |
| 块大小 | chunk_size | 最大字符/token 数 |
| 块重叠 | chunk_overlap | 相邻块重复字符 |
| 分隔符 | separators | 递归切分优先级 |

### 1.2 路线图

```text
129 Loader → 147 Text Splitter ← 本篇 → 128 VectorStore
```

---

## 2. 本文边界与动手路径

**档位：D 地基篇（路线图 147）。**

**本文讲：** Splitter 类型、参数调优、结构感知、metadata 继承、实战。  
**本文不讲：** Parent-Document 架构细节（[65](65.parent-document-retriever-tutorial.md)）、Token 计费（[27](27.token-counting-billing-tutorial.md)）精确到模型 tokenizer（可用 `tiktoken` 变体）。

| 步骤 | 验收 |
|------|------|
| A | 解释 size/overlap 权衡 |
| B | 递归 Splitter 跑通 |
| C | Markdown 标题切块 |
| D | chunk_id 规范 |
| E | §9 实战 |
| F | §8 先错对对 |

---

## 3. Text Splitter 是什么

![Text Splitter 是什么](image/langchain-text-splitter/01-splitter-idea.png)

核心 API：

```python
class TextSplitter:
    def split_text(self, text: str) -> list[str]: ...
    def create_documents(self, texts: list[str], metadatas: list[dict] | None = None) -> list[Document]: ...
    def split_documents(self, documents: list[Document]) -> list[Document]: ...
```

**split_documents** 最常用：输入 Loader 的 Document 列表，输出 **更多小 Document**。

### 3.1 在链路中的位置

```text
Loader → [本篇 Splitter] → Embeddings → VectorStore
              ↑
    [136 可插拔 Splitter 接口]
```

---

## 4. 核心概念：chunk_size、chunk_overlap、separators

### 4.1 参数含义

- **chunk_size**：单块最大长度（字符或 token，取决于 Splitter 类）；  
- **chunk_overlap**：块尾与下一块头重复字数（[60](60.chunk-overlap-tutorial.md)）；  
- **separators**：递归切分顺序，如 `["\\n\\n", "\\n", "。", " ", ""]`。

### 4.2 代码不裸奔

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
    separators=["\\n\\n", "\\n", "。", "！", "？", " ", ""],
    length_function=len,
)

long_doc = Document(
    page_content="第一章 总则\\n公司为员工提供年假。\\n\\n第二章 天数\\n工龄满一年者享有 10 个工作日年假。",
    metadata={"doc_id": "handbook-v3", "source": "handbook.md"},
)
chunks = splitter.split_documents([long_doc])
print(len(chunks), chunks[0].page_content[:50])
```

### 4.3 起步参数（中文制度文档）

| 场景 | chunk_size | overlap |
|------|------------|---------|
| FAQ 短答 | 300-500 | 50-80 |
| 技术 Markdown | 800-1200 | 100-200 |
| 法律合同 | 1000+ | 150+ |

用金标集调 [61](61.chunk-size-tradeoff-tutorial.md)。

---

## 5. RecursiveCharacterTextSplitter 详解

![递归切分示意](image/langchain-text-splitter/02-recursive-split.png)

算法直觉（[58](58.recursive-character-chunking-tutorial.md)）：

1. 用第一分隔符切；  
2. 若片段仍 > chunk_size，用下一分隔符 **递归**；  
3. 合并过小片段，直到满足 size；  
4. 应用 overlap。

### 5.1 与固定长度对比

| 固定 [57] | 递归 [58] |
|-----------|-----------|
| 可能句中切断 | 优先段/句界 |
| 实现简单 | 中文友好 |
| 代码注释易碎 | 制度/技术文档首选 |

### 5.2 Token 级 Splitter

```python
from langchain_text_splitters import TokenTextSplitter
splitter = TokenTextSplitter(chunk_size=256, chunk_overlap=32)
```

对接 [27 Token 计数](27.token-counting-billing-tutorial.md) 与模型窗口 [28](28.context-window-tutorial.md)。

---

## 6. 结构感知：Markdown 与 HTML

### 6.1 MarkdownHeaderTextSplitter

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_docs = md_splitter.split_text(open("data/guide.md", encoding="utf-8").read())
```

衔接 [63 Markdown AST 切块](63.markdown-ast-chunking-tutorial.md)、[62 结构感知](62.structure-aware-chunking-tutorial.md)。

### 6.2 HTMLHeaderTextSplitter

用于 [64 HTML DOM 切块](64.html-dom-chunking-tutorial.md) 导出的 HTML。

### 6.3 二级流水线

常见模式：**先按标题粗切，再 RecursiveCharacter 细切**。

```python
def pipeline_split(md_text: str) -> list[Document]:
    coarse = md_splitter.split_text(md_text)
    fine = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    return fine.split_documents(coarse)
```

---

## 7. metadata 与 chunk_id 继承

### 7.1 继承规则

`split_documents` 默认 **复制父 metadata** 到每个子 chunk；应追加：

```python
def assign_chunk_ids(chunks: list[Document], doc_id: str) -> list[Document]:
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = f"{doc_id}:c{{i:04d}}"
        c.metadata["chunk_index"] = i
    return chunks
```

规范见 [51 chunk_id](51.metadata-chunk-id-tutorial.md)。

### 7.2 start_index

部分 Splitter 写入 `metadata["start_index"]`，便于 [115 原文定位](115.source-document-navigation-tutorial.md)。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：chunk_size=10000

**现象**：检索像「整书匹配」，精度差。  
**对**：降到 500-1200 并评测。

### 8.2 错：overlap=0 且分隔符只有空格

**现象**：关键词跨块断裂。  
**对**：overlap 15%-20%；加中文句号分隔符。

### 8.3 错：split 后 chunk_id 重复

**现象**：upsert 覆盖、引用错乱。  
**对**：全局唯一 `chunk_id`。

### 8.4 错：在 Splitter 里调 Embedding

**现象**：职责混乱、难测。  
**对**：切块纯文本；向量在 [128](128.langchain-vectorstore-tutorial.md)。

---

## 9. 综合实战：制度文档切块入库

```python
"""split_and_preview.py — 路线图 147 综合实战"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

TEXT = "\\n\\n".join([
    "员工手册 v3",
    "## 年假",
    "工龄满一年：10 天。",
    "## 差旅",
    "每日报销上限 600 元。",
])

def main():
    doc = Document(page_content=TEXT, metadata={"doc_id": "hb-v3", "source": "inline"})
    splitter = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=24)
    chunks = splitter.split_documents([doc])
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = f"hb-v3:c{i:04d}"
        print(c.metadata["chunk_id"], "=>", c.page_content.replace("\\n", " "))
    # 下游: Chroma.from_documents(chunks, embeddings)

if __name__ == "__main__":
    main()
```

---

## 10. 与 C 模块切块对照

| C 模块 | LangChain |
|--------|-----------|
| 手写递归 | RecursiveCharacterTextSplitter |
| AST 切块 | MarkdownHeaderTextSplitter + 细切 |
| overlap 策略 | chunk_overlap 参数 |
| 可插拔 | [136](136.pluggable-parser-splitter-embedder-tutorial.md) |

---

## 11. 综合概念地图

![Splitter 概念地图](image/langchain-text-splitter/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：字符 vs token？**  
A：中文常 **1 字≈1-2 token**；严肃场景用 `TokenTextSplitter`。

**Q：代码块会被切断吗？**  
A：会；技术文档用 Markdown 结构切分或 [62 结构感知](62.structure-aware-chunking-tutorial.md)。

**Q：和 [65 Parent Document](65.parent-document-retriever-tutorial.md)？**  
A：child 小块入索引；parent 大块存旁路。

**Q：如何评测切块？**  
A：金标问句看答案是否跨块丢失（[151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)）。

**Q：Splitter 可配置化吗？**  
A：见 [138 配置驱动管道](138.config-driven-pipeline-tutorial.md)。

**Q：多语言混合？**  
A：分隔符加英文句号；Embedding 用 [70](70.mixed-language-embedding-tutorial.md)。

**Q：表格怎么办？**  
A：[37 表格](37.pdf-layout-tables-tutorial.md) 单独策略，避免按行切碎。

**Q：切块要去重吗？**  
A：overlap 可能产生近似重复；检索侧 [106 去重](106.retrieval-dedup-tutorial.md)。

---

## 13. 总结与系列下一步

**Text Splitter** 把 C 模块切块经验 **封装成可配置组件**，是与 [129 Loader](129.langchain-document-loader-tutorial.md)、[128 VectorStore](128.langchain-vectorstore-tutorial.md) 的 **必经枢纽**。

**下一步**：[128 VectorStore](128.langchain-vectorstore-tutorial.md)、[136 可插拔抽象](136.pluggable-parser-splitter-embedder-tutorial.md)、[61 权衡](61.chunk-size-tradeoff-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="147", tier="地基篇"))


def article_131():
    return ('''# D 框架与架构（七）：LlamaIndex Index 类型导读

> **了解即可**：团队主栈若是 LangChain（[125-130](125.langchain-core-tutorial.md)），本篇帮你 **面试不怯场**——知道 LlamaIndex 如何用不同 **Index（索引）** 组织节点与向量，并与 [128 VectorStore](128.langchain-vectorstore-tutorial.md) 概念对照。这是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 了解篇**（路线图第 **148** 条）。前置：[25 Embedding](25.embedding-vector-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[127 Retriever](127.langchain-retriever-tutorial.md)。

---

## 目录

1. [前言：为什么了解 LlamaIndex Index](#1-前言为什么了解-llamaindex-index)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LlamaIndex 与 LangChain 分工](#3-llamaindex-与-langchain-分工)
4. [核心概念：Document、Node、Index](#4-核心概念documentnodeindex)
5. [VectorStoreIndex 详解](#5-vectorstoreindex-详解)
6. [其他 Index 类型一览](#6-其他-index-类型一览)
7. [构建时机：insert vs from_documents](#7-构建时机insert-vs-from_documents)
8. [先错对对：三种典型误解](#8-先错对对三种典型误解)
9. [综合实战：最小 VectorStoreIndex](#9-综合实战最小-vectorstoreindex)
10. [与 LangChain 概念映射](#10-与-langchain-概念映射)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么了解 LlamaIndex Index

RAG 框架不止 LangChain。**LlamaIndex** 早期以 **「索引优先」** 著称：把文本变成 **Node**，再装入不同 **Index** 结构（向量、关键词、知识图谱等）。你不需要立刻迁移技术栈，但应能回答：**VectorStoreIndex 和 LC VectorStore 有何异同？TreeIndex 解决什么问题？**

**了解即可目标：**

1. 说出 **Node vs Document** 区别。  
2. 跑通 **VectorStoreIndex.from_documents** 最小示例。  
3. 列举 **3 种 Index 类型** 及场景。  
4. 知道何时 **读文档即可、不必深钻**。

### 1.1 标注

| 档位 | 建议 |
|------|------|
| 了解即可 | 面试对照、读官方示例 |
| 主栈 LangChain | 生产默认继续 LC |
| 数据 Agent 重 | 再评估 LlamaIndex 深度使用 |

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 节点 | Node | 带关系的文本单元 |
| 索引 | Index | 可查询的数据结构 |
| 向量索引 | VectorStoreIndex | 向量检索主索引 |
| 存储上下文 | StorageContext | 向量库与 docstore 绑定 |

---

## 2. 本文边界与动手路径

**档位：D 了解篇（路线图 148）。**

**本文讲：** Index 类型概念、VectorStoreIndex 最小实战、与 LC 映射。  
**本文不讲：** 生产级 LlamaIndex 部署、全量 Agent、细调每个 Index 参数。

| 步骤 | 验收 |
|------|------|
| A | 画 Node/Index 关系 |
| B | `pip install llama-index` |
| C | §9 最小示例 |
| D | 口述 3 种 Index |
| E | §8 先错对对 |

---

## 3. LlamaIndex 与 LangChain 分工

![LlamaIndex Index 概览](image/llamaindex-index-types/01-index-idea.png)

| 维度 | LangChain | LlamaIndex |
|------|-----------|------------|
| 心智模型 | Runnable 管道 | Index + QueryEngine |
| 数据原子 | Document | Node（可含关系） |
| 检索 | Retriever | Index + Retriever 模式 |
| 适合 | 通用 LLM 链 | 数据密集 Q&A |

**了解即可**：两者可共存；别 **为框架而框架**（见 [135](135.pipeline-vs-framework-tutorial.md)）。

---

## 4. 核心概念：Document、Node、Index

### 4.1 转化链

```text
Loader 文本 → Document → NodeParser → Node[] → Index 构建
```

Node 可带 `relationships`（父子、引用），衔接 [65 Parent Document](65.parent-document-retriever-tutorial.md) 思想。

### 4.2 Index 共性

- **insert / from_documents**：写入；  
- **as_retriever**：检索接口；  
- **as_query_engine**：更高层问答（[132](132.llamaindex-query-engine-tutorial.md)）。

---

## 5. VectorStoreIndex 详解

最常用：**向量检索索引**，底层对接 Chroma、FAISS、Postgres 等（[76](76.chroma-vector-db-tutorial.md)、[75](75.faiss-ann-tutorial.md)）。

```python
# 了解即可 — 最小 VectorStoreIndex（需 llama-index 与 embedding 配置）
from llama_index.core import VectorStoreIndex, Document

docs = [
    Document(text="年假：工龄满一年 10 天。", metadata={"doc_id": "hr-v1"}),
    Document(text="差旅：每日报销上限 600 元。", metadata={"doc_id": "hr-v2"}),
]
index = VectorStoreIndex.from_documents(docs)
retriever = index.as_retriever(similarity_top_k=3)
nodes = retriever.retrieve("年假几天")
for n in nodes:
    print(n.text[:40], n.score)
```

与 [128 LC VectorStore](128.langchain-vectorstore-tutorial.md) 对照：**构建时自动 embed + 写入向量库**。

---

## 6. 其他 Index 类型一览

![Index 类型对比](image/llamaindex-index-types/02-index-types.png)

| Index | 用途 | 了解深度 |
|-------|------|----------|
| VectorStoreIndex | 语义检索 | 必知 |
| SummaryIndex | 顺序总结全文 | 了解 |
| TreeIndex | 层次摘要树 | 了解 |
| KeywordTableIndex | 关键词表 | 了解 |
| KnowledgeGraphIndex | 三元组图谱 | 选修 |
| ComposableGraph | 多 Index 组合 | 选修 |

**SummaryIndex**：适合 **短库全文概括**；长库会爆 [28 窗口](28.context-window-tutorial.md)。  
**TreeIndex**：自底向上摘要，适合 **层次化手册**；构建成本高。  
**KeywordTableIndex**：稀疏检索，类似 [92 稀疏](92.sparse-retrieval-rag-tutorial.md)。

---

## 7. 构建时机：insert vs from_documents

- **from_documents**：PoC 一次性构建；  
- **insert**：增量 [49](49.incremental-update-tutorial.md)；  
- **refresh**：部分版本支持 doc 级更新。

生产应 **显式记录 embed 模型版本**（[25](25.embedding-vector-tutorial.md)），与 LC 相同铁律。

---

## 8. 先错对对：三种典型误解

### 8.1 误解：Index 等于向量库

**正解**：Index 是 **逻辑层**；向量库是 **存储后端**（StorageContext）。

### 8.2 误解：必须精通所有 Index

**正解**：**了解即可**；90% 场景 VectorStoreIndex 够用。

### 8.3 误解：LlamaIndex 与 LangChain 互斥

**正解**：可 LC 做服务层、LlamaIndex 做实验；或选用其一。

---

## 9. 综合实战：最小 VectorStoreIndex

见 §5 代码。验收：`retrieve("年假")` 命中含「10 天」的节点。

扩展：换 `Settings.embed_model` 对接 OpenAI/BGE（[35 API](35.openai-compatible-api-tutorial.md)）。

---

## 10. 与 LangChain 概念映射

| LlamaIndex | LangChain |
|------------|-----------|
| Document | Document |
| Node | Document（细分后） |
| VectorStoreIndex | VectorStore + from_documents |
| as_retriever | as_retriever |
| QueryEngine | LCEL 链 + LLM |

---

## 11. 综合概念地图

![Index 概念地图](image/llamaindex-index-types/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：要不要转 LlamaIndex？**  
A：无强制；**主栈 LC 则本篇了解即可**。

**Q：Index 构建慢？**  
A：embed 瓶颈；[67 批处理](67.embedding-batching-tutorial.md)。

**Q：与 [76 Chroma](76.chroma-vector-db-tutorial.md) 共用目录？**  
A：注意 **不同框架 metadata schema**；生产勿混用目录。

**Q：ComposableGraph 何时用？**  
A：多知识库合并查询；复杂度高，PoC 慎用。

**Q：和 [93 混合检索](93.hybrid-search-tutorial.md)？**  
A：LI 可组合向量+关键词 Retriever；细节读官方 cookbook。

**Q：面试怎么答？**  
A：「熟 LC VectorStore/Retriever；了解 LI VectorStoreIndex 与 QueryEngine 定位。」

---

## 13. 总结与系列下一步

**了解即可** 掌握 LlamaIndex **Index 类型全景** 与 **VectorStoreIndex 最小实践**，与 [128-130 LangChain](128.langchain-vectorstore-tutorial.md) 对照，避免框架宗教战争。

**下一步**：[132 Query Engine](132.llamaindex-query-engine-tutorial.md)、[133 Agent](133.llamaindex-agent-tutorial.md)、[135 自研 vs 框架](135.pipeline-vs-framework-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="148", tier="了解篇"))


def article_132():
    return ('''# D 框架与架构（八）：LlamaIndex Query Engine 导读

> **了解即可**：如果说 [131 Index](131.llamaindex-index-types-tutorial.md) 是「数据怎么组织」，**Query Engine（查询引擎）** 就是「问题怎么问、答案怎么出」——封装 **检索 + 合成** 的一站式 `query()`。本篇帮助 LangChain 开发者 **对照 LCEL**（[126](126.langchain-lcel-tutorial.md)），面试能讲清差异。路线图第 **149** 条。前置：[131 Index](131.llamaindex-index-types-tutorial.md)、[110 RAG 模板](110.rag-prompt-template-tutorial.md)、[34 Grounding](34.grounding-citation-tutorial.md)。

---

## 目录

1. [前言：Query Engine 解决什么](#1-前言query-engine-解决什么)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Query Engine 是什么](#3-query-engine-是什么)
4. [核心概念：query、response、synthesizer](#4-核心概念queryresponsesynthesizer)
5. [从 Index 创建 Query Engine](#5-从-index-创建-query-engine)
6. [RetrieverQueryEngine 与自定义](#6-retrieverqueryengine-与自定义)
7. [流式与引用](#7-流式与引用)
8. [先错对对：三种典型误解](#8-先错对对三种典型误解)
9. [综合实战：最小问答](#9-综合实战最小问答)
10. [与 LCEL 对照](#10-与-lcel-对照)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：Query Engine 解决什么

LangChain 你把链写成 `retriever | format | prompt | llm`（[126 LCEL](126.langchain-lcel-tutorial.md)）。LlamaIndex 用 **`query_engine.query("...")`** 一次调用，内部完成 **检索、上下文拼装、LLM 合成**。了解这一层，便于 **读 LlamaIndex 官方教程** 和 **选型讨论**（[135](135.pipeline-vs-framework-tutorial.md)）。

**了解即可目标：**

1. 创建 `index.as_query_engine()` 并打印 `response`。  
2. 说明 **synthesizer** 角色。  
3. 对照 LCEL **分步 vs 一站式** 利弊。

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 查询引擎 | Query Engine | query 进、Response 出 |
| 响应合成器 | Response Synthesizer | 上下文+问句→答案 |
| 检索模式 | RetrieverQueryEngine | 基于 Retriever 的引擎 |

---

## 2. 本文边界与动手路径

**档位：D 了解篇（路线图 149）。**

| 步骤 | 验收 |
|------|------|
| A | 画 query 内部步骤 |
| B | §9 跑通 query |
| C | 对照 LCEL 链 |
| D | §8 先错对对 |

---

## 3. Query Engine 是什么

![Query Engine 流程](image/llamaindex-query-engine/01-query-engine-flow.png)

```text
用户 query → Retriever 召回 Node → Synthesizer 拼 prompt → LLM → Response
```

**Response** 常含 `response` 文本、`source_nodes` 引用（对接 [34 Grounding](34.grounding-citation-tutorial.md)）。

---

## 4. 核心概念：query、response、synthesizer

### 4.1 最小调用

```python
from llama_index.core import VectorStoreIndex, Document

index = VectorStoreIndex.from_documents([
    Document(text="报销上限每日 600 元。"),
])
query_engine = index.as_query_engine(similarity_top_k=3)
response = query_engine.query("差旅报销多少？")
print(str(response))
# 了解即可：查看引用
for sn in response.source_nodes:
    print(sn.node.metadata, sn.score)
```

### 4.2 Synthesizer 模式（了解）

| 模式 | 行为 |
|------|------|
| compact | 压缩上下文进单次 LLM |
| tree_summarize | 分块摘要再合并 |
| refine | 迭代 refine 答案 |

长上下文策略见 [107 预算](107.context-budget-tutorial.md)、[108 重排](108.long-context-reorder-tutorial.md)。

---

## 5. 从 Index 创建 Query Engine

```python
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact",
)
```

参数映射 [98 top-k](98.top-k-retrieval-tutorial.md)、[110 模板](110.rag-prompt-template-tutorial.md) 思想。

---

## 6. RetrieverQueryEngine 与自定义

高级：**自定义 Retriever** + `RetrieverQueryEngine.from_args`，类似 LC 只换中间 Retriever（[127](127.langchain-retriever-tutorial.md)）。

了解即可：知道 **可拆可合**，不必死记 API。

---

## 7. 流式与引用

- **streaming**：`query_engine.query(..., streaming=True)` 类似 [116 SSE](116.sse-rag-streaming-tutorial.md)；  
- **source_nodes**：做 [113 行内引用](113.inline-citation-tutorial.md)、[115 导航](115.source-document-navigation-tutorial.md)。

---

## 8. 先错对对：三种典型误解

### 8.1 误解：Query Engine 包含索引构建

**正解**：构建在 Index；Engine 只 **查询**。

### 8.2 误解：不用配 Retriever 参数

**正解**：`similarity_top_k`、metadata 过滤仍需调（[88](88.metadata-filter-retrieval-tutorial.md)）。

### 8.3 误解：source_nodes 等于合法引用

**正解**：仍需 [34 Grounding](34.grounding-citation-tutorial.md) 校验，防 LLM 漂引用。

---

## 9. 综合实战：最小问答

§4 代码扩展：对同一问题打印 **LCEL 链**（[126](126.langchain-lcel-tutorial.md)）与 **query_engine** 延迟对比——了解即可，不必统一技术栈。

---

## 10. 与 LCEL 对照

![LCEL vs Query Engine](image/llamaindex-query-engine/02-vs-lcel.png)

| LCEL | Query Engine |
|------|--------------|
| 显式管道 | 封装管道 |
| 易插 Lambda | 用 callback/自定义类 |
| 与 LangSmith 熟 | LlamaIndex observability |
| 团队已熟 LC | 继续 LC |

---

## 11. 综合概念地图

![Query Engine 概念地图](image/llamaindex-query-engine/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：生产用 Query Engine 还是 LCEL？**  
A：看主栈；**了解即可** 不强制迁移。

**Q：如何做 ACL？**  
A：Retriever 层 metadata 过滤（[121](121.unauthorized-doc-filter-tutorial.md)）。

**Q：多轮对话？**  
A：`ChatEngine` 变体；对照 [118 多轮](118.multi-turn-history-tutorial.md)。

**Q：与 [96 精排](96.bge-reranker-tutorial.md)？**  
A：postprocessor 钩子；或检索后自写 rerank。

**Q：幻觉怎么控？**  
A：[112 拒答](112.refusal-strategy-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md) 评测。

**Q：能否只用 Retriever 不用 Engine？**  
A：可以，等同 LC 只用 `as_retriever`。

---

## 13. 总结与系列下一步

**Query Engine** 是 LlamaIndex 的 **问答一站式 API**；LangChain 用户 **了解即可**，用 LCEL 实现同等语义。

**下一步**：[133 Agent](133.llamaindex-agent-tutorial.md)、[135 框架取舍](135.pipeline-vs-framework-tutorial.md)、[110 模板](110.rag-prompt-template-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="149", tier="了解篇"))


def article_133():
    return ('''# D 框架与架构（九）：LlamaIndex Agent 导读

> **了解即可**：固定 RAG 管道（检索→生成）能覆盖大部分企业场景；当需要 **多步推理、选工具、查多源** 时，**Agent（智能体）** 进入视野。LlamaIndex Agent 与 [124 Function Calling](124.function-calling-tool-use-tutorial.md) 同源。路线图第 **150** 条。前置：[132 Query Engine](132.llamaindex-query-engine-tutorial.md)、[124 工具调用](124.function-calling-tool-use-tutorial.md)。

---

## 目录

1. [前言：Agent 在 RAG 中的位置](#1-前言agent-在-rag-中的位置)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LlamaIndex Agent 是什么](#3-llamaindex-agent-是什么)
4. [核心概念：Tool、AgentRunner、ReAct](#4-核心概念toolagentrunnerreact)
5. [QueryEngineTool 包装 RAG](#5-queryenginetool-包装-rag)
6. [多工具路由与风险](#6-多工具路由与风险)
7. [与 OpenAI Tool Loop 对照](#7-与-openai-tool-loop-对照)
8. [先错对对：三种典型翻车](#8-先错对对三种典型翻车)
9. [综合实战：单工具 Agent](#9-综合实战单工具-agent)
10. [何时不用 Agent](#10-何时不用-agent)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：Agent 在 RAG 中的位置

**Agent** = LLM + **工具调用循环**：模型决定「先搜知识库还是先查天气」，执行工具，再决定下一步。LlamaIndex 提供 `AgentRunner`、`ReActAgent` 等。**了解即可**：多数工单系统 **固定管道 + 可选工具**（[124](124.function-calling-tool-use-tutorial.md)）更可控。

**目标：**

1. 理解 **QueryEngine 包成 Tool** 的模式。  
2. 说出 Agent **延迟、成本、失控** 三风险。  
3. 对照 LC Tool Agent。

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 智能体 | Agent | 规划+工具循环 |
| 工具 | Tool | 可调用外部能力 |
| ReAct | ReAct | 推理+行动交替 |

---

## 2. 本文边界与动手路径

**档位：D 了解篇（路线图 150）。**

| 步骤 | 验收 |
|------|------|
| A | 画 Agent 循环 |
| B | §9 单工具示例 |
| C | 列三风险 |
| D | §8 先错对对 |

---

## 3. LlamaIndex Agent 是什么

![LlamaIndex Agent](image/llamaindex-agent/01-agent-loop.png)

```text
user → Agent → (thought → tool_call → observation)* → final answer
```

与 [104 多跳检索](104.multi-hop-retrieval-tutorial.md) 相关，但 Agent **由模型决定跳数**，需 **max_iterations** 护栏。

---

## 4. 核心概念：Tool、AgentRunner、ReAct

### 4.1 QueryEngineTool（了解即可）

```python
from llama_index.core.tools import QueryEngineTool, ToolMetadata
# query_engine 来自 132 篇
# tool = QueryEngineTool(
#     query_engine=query_engine,
#     metadata=ToolMetadata(name="handbook", description="公司员工制度知识库"),
# )
```

把 [132 Query Engine](132.llamaindex-query-engine-tutorial.md) 变成 Agent 可调工具。

### 4.2 ReAct 提示

模型输出 **Thought / Action / Action Input / Observation** 循环；读官方示例即可，不必生产硬上。

---

## 5. QueryEngineTool 包装 RAG

**模式**：每个知识库一个 QueryEngineTool → Agent 路由到正确库（[89 多租户](89.multi-tenant-namespace-tutorial.md) 需谨慎）。

**好处**：用户问题 **模糊时** 自动选库。  
**坏处**：多一次 LLM 路由，**错误选库** 难排查。

---

## 6. 多工具路由与风险

| 风险 | 缓解 |
|------|------|
| 无限循环 | max_iterations |
| 成本爆炸 | 工具白名单、缓存 |
| ACL 穿透 | 工具内强制 [121](121.unauthorized-doc-filter-tutorial.md) |
| 幻觉工具参数 | schema 校验 [123 JSON](123.structured-output-json-tutorial.md) |

---

## 7. 与 OpenAI Tool Loop 对照

| LlamaIndex Agent | LC + OpenAI Tools |
|------------------|-------------------|
| QueryEngineTool | retriever tool |
| AgentRunner | AgentExecutor 等 |
| 内置 ReAct | 自定义 prompt |

**了解即可**：思想一致，API 不同。

---

## 8. 先错对对：三种典型翻车

### 8.1 错：简单 FAQ 硬上 Agent

**对**：固定 RAG 链（[126 LCEL](126.langchain-lcel-tutorial.md)）更简单。

### 8.2 错：无 max_iterations

**对**：3-5 次上限 + 超时。

### 8.3 错：工具描述含糊

**对**：`description` 写清 **何时调用、何时不调用**（[124](124.function-calling-tool-use-tutorial.md)）。

---

## 9. 综合实战：单工具 Agent

伪代码流程（了解即可，API 随版本演进）：

```python
# 1. 构建 index + query_engine（132 篇）
# 2. 包装 QueryEngineTool
# 3. agent = ReActAgent.from_tools([tool], llm=..., verbose=True)
# 4. response = agent.chat("年假和差旅报销分别怎么算？")
```

验收：能 **口述** 步骤即可；不强制本地跑通全部 Agent 依赖。

---

## 10. 何时不用 Agent

- 单库制度问答；  
- 强合规 **固定检索路径**；  
- 延迟敏感（[87 ANN 延迟](87.ann-recall-latency-tutorial.md) + 多轮 LLM）。

用 [135 框架取舍](135.pipeline-vs-framework-tutorial.md) 写决策记录。

---

## 11. 综合概念地图

![Agent 概念地图](image/llamaindex-agent/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：Agent vs Query Engine？**  
A：Engine **单步问答**；Agent **多步工具**。

**Q：和 [124 LC 工具](124.function-calling-tool-use-tutorial.md)？**  
A：同级概念；栈不同。

**Q：观测怎么做？**  
A：[147 LangSmith](147.langsmith-tracing-tutorial.md)、[148 Langfuse](148.langfuse-observability-tutorial.md)。

**Q：生产比例？**  
A：多数团队 **80% 固定 RAG + 20% 工具/Agent**。

**Q：多跳检索呢？**  
A：[104 多跳](104.multi-hop-retrieval-tutorial.md) 可固定管道；Agent 是动态版。

**Q：面试答案？**  
A：「了解 LI Agent 与 QueryEngineTool；生产优先可控管道。」

---

## 13. 总结与系列下一步

**了解即可** LlamaIndex Agent：**工具循环、QueryEngineTool、风险护栏**。

**下一步**：[134 Haystack Pipeline](134.haystack-pipeline-tutorial.md)、[135 自研 vs 框架](135.pipeline-vs-framework-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="150", tier="了解篇"))


def article_134():
    return ('''# D 框架与架构（十）：Haystack Pipeline 思想导读

> **了解即可**：[deepset Haystack](https://haystack.deepset.ai/) 以 **显式 Pipeline（管道图）** 著称——组件用 **有向图** 连接，适合 **可审计、可序列化** 的 RAG 服务。本篇不学全 API，而学 **Pipeline 思想**：与 [126 LCEL](126.langchain-lcel-tutorial.md)、自研 DAG（[135](135.pipeline-vs-framework-tutorial.md)）对照。路线图第 **151** 条。前置：[125-128 LangChain](125.langchain-core-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)。

---

## 目录

1. [前言：为什么学 Pipeline 思想](#1-前言为什么学-pipeline-思想)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Haystack Pipeline 是什么](#3-haystack-pipeline-是什么)
4. [核心概念：Component、Connection、SuperComponent](#4-核心概念componentconnectionsupercomponent)
5. [典型 RAG 图结构](#5-典型-rag-图结构)
6. [与 LCEL 管道对照](#6-与-lcel-管道对照)
7. [序列化与部署](#7-序列化与部署)
8. [先错对对：三种误解](#8-先错对对三种误解)
9. [综合实战：伪代码构图](#9-综合实战伪代码构图)
10. [何时借鉴 Haystack](#10-何时借鉴-haystack)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么学 Pipeline 思想

LangChain LCEL 用 `|` **隐式** 连接；Haystack 2.x 用 **`Pipeline.add_component` + `connect`** **显式** 连。自研服务（[156 FastAPI](156.fastapi-project-structure-tutorial.md)）也常画 **ingest DAG**。了解 Haystack **图式思维**，有助于 **设计可观测、可配置** 的 RAG（[138 配置驱动](138.config-driven-pipeline-tutorial.md)）。

**了解即可目标：**

1. 画出 **Retriever → Prompt → Generator** 三节点图。  
2. 说明 **显式图 vs LCEL** 各适合谁。  
3. 知道 Haystack **不必作为主栈** 也能借鉴。

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 管道 | Pipeline | 组件有向图 |
| 组件 | Component | 带类型端口的处理单元 |
| 连接 | Connection | 输出端口→输入端口 |

---

## 2. 本文边界与动手路径

**档位：D 了解篇（路线图 151）。**

| 步骤 | 验收 |
|------|------|
| A | 手绘 RAG Pipeline |
| B | 读官方 RAG 图示例 |
| C | 写与 LCEL 对照表 |
| D | §8 先错对对 |

---

## 3. Haystack Pipeline 是什么

![Haystack Pipeline](image/haystack-pipeline/01-pipeline-idea.png)

```text
[FileConverter] → [Splitter] → [Embedder] → [DocumentWriter]
[Query] → [Embedder] → [Retriever] → [PromptBuilder] → [Generator]
```

**特点**：端口类型检查、图可 **YAML 序列化**、组件可单测。

---

## 4. 核心概念：Component、Connection、SuperComponent

### 4.1 组件边界

每个 Component **输入/输出 schema 明确**，类似 [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md) 接口的 **图化版本**。

### 4.2 SuperComponent

把子图封装成 **一个大组件**，便于复用（如「标准 RAG 检索段」）。

---

## 5. 典型 RAG 图结构

![RAG 图结构](image/haystack-pipeline/02-rag-graph.png)

| 阶段 | 组件示例 |
|------|----------|
| Ingest | converters, preprocessors, embedders, writers |
| Query | text embedder, retriever, ranker（[96](96.bge-reranker-tutorial.md)） |
| Generate | prompt_builder, generator |

**混合检索**：[93](93.hybrid-search-tutorial.md) 在 Retriever 组件内或 **双 Retriever + Joiner**（[94 RRF](94.rrf-fusion-tutorial.md)）。

---

## 6. 与 LCEL 管道对照

| Haystack Pipeline | LangChain LCEL |
|-------------------|----------------|
| 显式 connect | 隐式 `|` |
| YAML 导出 | 代码即配置 |
| 强类型端口 | Runnable 泛型 |
| 偏服务化 | 偏原型 |

**了解即可**：选型见 [135](135.pipeline-vs-framework-tutorial.md)。

---

## 7. 序列化与部署

Pipeline 可导出 **JSON/YAML**，适合 **运维改参数不改代码**（衔接 [138](138.config-driven-pipeline-tutorial.md)、[154 参数版本](154.param-version-management-tutorial.md)）。

---

## 8. 先错对对：三种误解

### 8.1 误解：必须用 Haystack 才能做 Pipeline

**正解**：自研 DAG + [136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md) 即可。

### 8.2 误解：图越复杂越好

**正解**：PoC **3-5 节点** 足够；复杂图难排障（[149-152 Bad Case](149.bad-case-parsing-tutorial.md)）。

### 8.3 误解：Haystack 与 LC 完全对立

**正解**：部分组件可互操作；思想可交叉借鉴。

---

## 9. 综合实战：伪代码构图

```python
# 了解即可 — Haystack 2.x 风格伪代码
# pipeline = Pipeline()
# pipeline.add_component("retriever", retriever)
# pipeline.add_component("prompt", prompt_builder)
# pipeline.add_component("llm", generator)
# pipeline.connect("retriever.documents", "prompt.documents")
# pipeline.connect("prompt.prompt", "llm.prompt")
# result = pipeline.run({"retriever": {"query": "年假几天？"}})
```

验收：**能画等价 LCEL 链**（[126](126.langchain-lcel-tutorial.md)）。

---

## 10. 何时借鉴 Haystack

- 需要 **可视化管道** 给运维/合规；  
- 多团队 **共享组件库**；  
- **强类型** 接口减少接错线。

不必全员转 Haystack。

---

## 11. 综合概念地图

![Haystack 概念地图](image/haystack-pipeline/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：Haystack 1.x 与 2.x？**  
A：2.x 全新 Pipeline；读文档注意版本。

**Q：和 [134](134.haystack-pipeline-tutorial.md) 系列重复？**  
A：本篇仅 **思想**；深度用官方文档。

**Q：组件能否换 [128 VectorStore](128.langchain-vectorstore-tutorial.md)？**  
A：Haystack 自有 DocumentStore；概念类似 [76 Chroma](76.chroma-vector-db-tutorial.md)。

**Q：评测？**  
A：[139-142 RAGAS](139.ragas-context-precision-tutorial.md) 与框架无关。

**Q：流式？**  
A：Generator 组件支持 stream；对照 [116 SSE](116.sse-rag-streaming-tutorial.md)。

**Q：面试？**  
A：「熟 LCEL；了解 Haystack 显式 Pipeline 与可序列化优势。」

---

## 13. 总结与系列下一步

**了解即可** Haystack **Pipeline 图式 RAG**，借鉴 **显式连接与可配置**，不必替换主栈。

**下一步**：[135 自研 vs 框架](135.pipeline-vs-framework-tutorial.md)、[138 配置驱动](138.config-driven-pipeline-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="151", tier="了解篇"))


def article_135():
    return ('''# D 框架与架构（十一）：自研 Pipeline vs 框架取舍完全指南

> C 模块你 **手写** 了 RAG 全链路；D 模块见了 **LangChain**（[125-130](125.langchain-core-tutorial.md)）、**LlamaIndex**（[131-133](131.llamaindex-index-types-tutorial.md)）、**Haystack 思想**（[134](134.haystack-pipeline-tutorial.md)）。路线图第 **152** 条问：**哪层自研、哪层用框架？** 这篇是 **架构主线**，给你 **决策表、迁移路径、团队分工**。前置：C 模块全链路、[125 核心](125.langchain-core-tutorial.md)、[128 VectorStore](128.langchain-vectorstore-tutorial.md)、[136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md)。

---

## 目录

1. [前言：框架不是信仰](#1-前言框架不是信仰)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [三种构建方式光谱](#3-三种构建方式光谱)
4. [核心概念：边界、契约、回滚](#4-核心概念边界契约回滚)
5. [分层取舍表](#5-分层取舍表)
6. [LangChain 适用场景](#6-langchain-适用场景)
7. [自研适用场景](#7-自研适用场景)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：决策工作坊](#9-综合实战决策工作坊)
10. [迁移与双轨策略](#10-迁移与双轨策略)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：框架不是信仰

面试问「用 LangChain 吗？」——高分回答不是 Yes/No，而是：

- **数据层**（Parser/Splitter）为何自研或可插拔（[136](136.pluggable-parser-splitter-embedder-tutorial.md)）；  
- **索引层** 是否坚持 [76 Chroma](76.chroma-vector-db-tutorial.md)/[75 FAISS](75.faiss-ann-tutorial.md) 原生 API；  
- **编排层** 用 [126 LCEL](126.langchain-lcel-tutorial.md) 还是自研 DAG（[134 Haystack 思想](134.haystack-pipeline-tutorial.md)）；  
- **观测与评测** 必须自研接入（[147-148](147.langsmith-tracing-tutorial.md)）。

**读完本文，你应该能做到：**

1. 填 **分层取舍表** 并辩护。  
2. 设计 **双轨迁移**（框架 Prototype → 自研核心）。  
3. 识别 §8 四种组织级翻车。  
4. 主持 60 分钟 **决策工作坊**（§9）。

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 自研管道 | Custom Pipeline | 手写 DAG 与接口 |
| 框架编排 | Framework Orchestration | LC/LI/Haystack |
| 混合架构 | Hybrid | 核心自研+外围框架 |
| 供应商锁定 | Vendor Lock-in | 深绑单一框架 |

---

## 2. 本文边界与动手路径

**档位：D 主线篇（路线图 152）。**

| 步骤 | 验收 |
|------|------|
| A | 画三层架构 |
| B | 填 §5 表 |
| C | §9 工作坊产出 |
| D | §8 先错对对 |

---

## 3. 三种构建方式光谱

![自研 vs 框架光谱](image/pipeline-vs-framework/01-spectrum.png)

```text
纯自研 ←———— 混合 ————→ 框架一把梭
```

| 方式 | 优点 | 缺点 |
|------|------|------|
| 纯自研 | 可控、无锁定 | 人力、重复造轮 |
| 混合 | 平衡 | 边界要治理 |
| 框架梭 | 快 | 黑盒、升级痛 |

---

## 4. 核心概念：边界、契约、回滚

### 4.1 契约优先

[136 Parser/Splitter/Embedder](136.pluggable-parser-splitter-embedder-tutorial.md)、[137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md) 定义 **协议**，框架实现 **适配器**。

### 4.2 可回滚

任何框架层必须 **2 周内可剔回自研**（feature flag + 并行链）。

### 4.3 金标守门

换框架前后 **RAGAS / 金标**（[139-143](143.golden-dataset-tutorial.md)）不能退步。

---

## 5. 分层取舍表

![分层取舍](image/pipeline-vs-framework/02-layer-table.png)

| 层级 | 建议倾向 | 理由 |
|------|----------|------|
| Parser/Splitter | 自研或可插拔 | 领域格式多 [36-40] |
| Embedder | 薄封装 | 锁模型 [25](25.embedding-vector-tutorial.md) |
| VectorStore | 原生 API + 薄适配 | 排障 [76][75] |
| Retriever | 框架或自研 | 混合检索 [93] 常定制 |
| Prompt/LLM | 框架省心 | [110](110.rag-prompt-template-tutorial.md) |
| API/ACL | 自研 | [121](121.unauthorized-doc-filter-tutorial.md) |
| 观测 | 自研接入 | [147-148](147.langsmith-tracing-tutorial.md) |

---

## 6. LangChain 适用场景

- 团队 Python 熟、PoC 紧；  
- 需要 **LCEL 快速试链**（[126](126.langchain-lcel-tutorial.md)）；  
- Retriever/Tool 生态（[127][124](127.langchain-retriever-tutorial.md)）；  
- 愿 pin 版本并做 **回归**（[143 金标](143.golden-dataset-tutorial.md)）。

**不宜**：核心知识产权在 **检索算法**、需 **毫秒级定制** 时仍 100% LC 黑盒。

---

## 7. 自研适用场景

- 强合规 **审计每一跳**；  
- 已有 **Java/Go** 服务主体；  
- 向量库 **运维团队** 只认 Milvus/pgvector API；  
- 框架升级 **曾导致 P0**。

自研不是「排斥框架」，是 **关键路径自控**。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：初级工程师只会 LC，不懂 Chroma 原生

**对**：强制 [76](76.chroma-vector-db-tutorial.md) 培训 + on-call 手册。

### 8.2 错：自研一切，三年还在写 Parser

**对**：用 [129 Loader](129.langchain-document-loader-tutorial.md) 或 [44 Unstructured](44.unstructured-io-tutorial.md) 加速。

### 8.3 错：双框架并存（LC+LI）无边界

**对**：**一条请求只走一条栈**（[135 本篇]）。

### 8.4 错：无金标就换框架

**对**：[143 Golden Dataset](143.golden-dataset-tutorial.md) 守门。

---

## 9. 综合实战：决策工作坊

**60 分钟议程**：

1. 白板画当前 RAG 链路（ingest + query）；  
2. 每人填 **分层取舍表**（§5）；  
3. 标红 **P0 必须自研** 模块；  
4. 选 **混合方案**：如「LC LCEL + 自研 Retriever + Chroma 原生」；  
5. 写 **回滚条件**：Faithfulness 降 5% 即回退；  
6. 产出 wiki 一页。

**模板**：

```markdown
## RAG 架构决策 v1
- 编排：LangChain LCEL
- 检索：自研 HybridRetriever（BM25+[76 Chroma]）
- 数据：自研 Parser + LC Splitter
- 观测：Langfuse
- 回滚：feature_flag=legacy_pipeline
```

---

## 10. 迁移与双轨策略

```text
Phase 1: LC 原型验证业务
Phase 2: 抽取可插拔接口（136-137）
Phase 3: 替换热点路径为自研
Phase 4: 框架仅留 Prompt/Tool 便利层
```

并行运行时用 **request_id 双写对比**（[153 A/B](153.ab-experiment-rag-tutorial.md)）。

---

## 11. 综合概念地图

![取舍概念地图](image/pipeline-vs-framework/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：小公司也要自研吗？**  
A：PoC 可框架；**契约** 先留接口，别写死。

**Q：LlamaIndex 算自研吗？**  
A：算框架；[131-133](131.llamaindex-index-types-tutorial.md) 了解即可。

**Q：Haystack？**  
A：[134](134.haystack-pipeline-tutorial.md) 借鉴图思想，不必全盘迁移。

**Q：如何说服管理层？**  
A：用 **成本、延迟、故障复盘** 数据，非技术喜好。

**Q：框架版本升级？**  
A：锁版本 + 月度升级窗 + 金标回归。

**Q：多租户？**  
A：[89](89.multi-tenant-namespace-tutorial.md)、[166](166.tenant-isolation-backend-tutorial.md) 常需自研。

**Q：和 [138 配置驱动](138.config-driven-pipeline-tutorial.md)？**  
A：配置化降低框架/自研切换成本。

**Q：面试标准答案？**  
A：「混合：核心检索与 ACL 自研，编排可用 LC，坚持原生向量库排障能力。」

---

## 13. 总结与系列下一步

**自研 vs 框架** 是 **分层取舍**，不是站队。用 **契约、金标、回滚** 治理混合架构。

**下一步**：[136 可插拔 Parser/Splitter/Embedder](136.pluggable-parser-splitter-embedder-tutorial.md)、[137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md)、[138 配置驱动](138.config-driven-pipeline-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="152", tier="主线篇"))


def article_136():
    return ('''# D 框架与架构（十二）：可插拔 Parser / Splitter / Embedder 完全指南

> [135 篇](135.pipeline-vs-framework-tutorial.md) 说 **混合架构**；契约从 **数据入口三件套** 开始：**Parser（解析器）、Splitter（分割器）、Embedder（嵌入器）**。无论用 [129 LC Loader](129.langchain-document-loader-tutorial.md) 还是自研，都应能 **替换实现而不推翻管道**。路线图第 **153** 条，**D 地基篇**。前置：[36-40 解析](36.pdf-text-extraction-tutorial.md)、[57-65 切块](58.recursive-character-chunking-tutorial.md)、[25 Embedding](25.embedding-vector-tutorial.md)、[128 VectorStore](128.langchain-vectorstore-tutorial.md)。

---

## 目录

1. [前言：可插拔是迁移的前提](#1-前言可插拔是迁移的前提)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [三接口总览](#3-三接口总览)
4. [核心概念：Protocol、适配器、版本](#4-核心概念protocol适配器版本)
5. [Parser 接口与实现](#5-parser-接口与实现)
6. [Splitter 接口与实现](#6-splitter-接口与实现)
7. [Embedder 接口与实现](#7-embedder-接口与实现)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [综合实战：注册表 + 管道](#9-综合实战注册表--管道)
10. [与 LangChain 适配](#10-与-langchain-适配)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：可插拔是迁移的前提

硬编码 `parse_pdf_with_pymupdf`  everywhere，换 [44 Unstructured](44.unstructured-io-tutorial.md) 时要改二十个文件。可插拔用 **统一协议**：

```text
bytes/path → Parser → RawDocument[]
RawDocument → Splitter → Chunk[]
Chunk.text → Embedder → vector[]
```

**读完本文，你应该能做到：**

1. 定义 **三个 Protocol**（或 ABC）。  
2. 写 **注册表** 按配置选实现。  
3. 为 LC Loader/Splitter/Embeddings 写 **适配器**。  
4. §8 四种翻车修复。  
5. §9 端到端 ingest。

### 1.2 术语双轨

| 中文 | English | 一句话 |
|------|---------|--------|
| 解析器 | Parser | 文件→结构化文本 |
| 分割器 | Splitter | 长文→块 |
| 嵌入器 | Embedder | 文本→向量 |
| 适配器 | Adapter | 框架实现→协议 |

---

## 2. 本文边界与动手路径

**档位：D 地基篇（路线图 153）。**

| 步骤 | 验收 |
|------|------|
| A | 画三接口数据流 |
| B | 实现 §9 注册表 |
| C | LC 适配器 |
| D | §8 先错对对 |

---

## 3. 三接口总览

![可插拔三件套](image/pluggable-parser-splitter-embedder/01-three-plugins.png)

衔接 [137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md) 构成完整可插拔 RAG。

---

## 4. 核心概念：Protocol、适配器、版本

### 4.1 Protocol 示例（代码不裸奔）

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

@dataclass
class RawDocument:
    text: str
    metadata: dict = field(default_factory=dict)

@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)

@runtime_checkable
class Parser(Protocol):
    name: str
    def parse(self, source: str) -> list[RawDocument]: ...

@runtime_checkable
class Splitter(Protocol):
    name: str
    def split(self, docs: list[RawDocument]) -> list[Chunk]: ...

@runtime_checkable
class Embedder(Protocol):
    name: str
    dimension: int
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
```

### 4.2 schema_version

每个实现带 `schema_version: str`，索引任务写入 **manifest**（[48 版本](48.doc-versioning-tutorial.md)）。

---

## 5. Parser 接口与实现

### 5.1 实现矩阵

| 实现 | 场景 |
|------|------|
| PlainTextParser | txt/md [38] |
| PyMuPDFParser | 电子版 PDF [42] |
| UnstructuredParser | 混合格式 [44] |
| TikaParser | JVM 生态 [45] |

### 5.2 输出契约

- `metadata` 必含 `doc_id` [50]、`source` [52]；  
- 扫描 PDF 走 [55 OCR](55.ocr-scanned-docs-tutorial.md) 预处理 Parser。

### 5.3 示例

```python
class PlainTextParser:
    name = "plain_text"
    def parse(self, source: str) -> list[RawDocument]:
        from pathlib import Path
        p = Path(source)
        text = p.read_text(encoding="utf-8")
        return [RawDocument(text=text, metadata={"source": str(p), "doc_id": p.stem})]
```

---

## 6. Splitter 接口与实现

### 6.1 RecursiveSplitter 包装

```python
class RecursiveSplitter:
    name = "recursive"
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, docs: list[RawDocument]) -> list[Chunk]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        lc_docs = [Document(page_content=d.text, metadata=dict(d.metadata)) for d in docs]
        out = []
        for i, c in enumerate(splitter.split_documents(lc_docs)):
            md = dict(c.metadata)
            md["chunk_id"] = f"{{md.get('doc_id', 'doc')}}:c{{i:04d}}"
            out.append(Chunk(text=c.page_content, metadata=md))
        return out
```

对齐 [130 LC Splitter](130.langchain-text-splitter-tutorial.md) 与 [51 chunk_id](51.metadata-chunk-id-tutorial.md)。

### 6.2 结构感知

可注册 `markdown_ast` 实现（[63](63.markdown-ast-chunking-tutorial.md)）。

---

## 7. Embedder 接口与实现

### 7.1 铁律

ingest 与 query **同一实现**（[25](25.embedding-vector-tutorial.md)、[66 L2](66.l2-normalization-tutorial.md)）。

### 7.2 实现

| 名称 | 说明 |
|------|------|
| fake | 单测 [75][76] |
| openai | [35 API](35.openai-compatible-api-tutorial.md) |
| bge_local | [72 本地](72.local-embedding-inference-tutorial.md) |

```python
class FakeEmbedder:
    name = "fake"
    dimension = 128
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        import hashlib
        def one(t: str) -> list[float]:
            h = hashlib.sha256(t.encode()).digest()
            return [((h[i % len(h)] / 255.0) - 0.5) for i in range(self.dimension)]
        return [one(t) for t in texts]
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
```

### 7.3 批处理与缓存

生产加 [67 batch](67.embedding-batching-tutorial.md)、[68 cache](68.embedding-cache-tutorial.md)、[69 重试](69.embedding-retry-rate-limit-tutorial.md)。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：Parser 直接返回 Chunk

**对**：Parser 只出 **RawDocument**；切块专责 Splitter。

### 8.2 错：Embedder 维数与向量库不一致

**对**：建库前断言 `len(vector)==embedder.dimension`。

### 8.3 错：换 Splitter 不重建索引

**对**：chunk 边界变 → **全量重建** [48](48.doc-versioning-tutorial.md)。

### 8.4 错：无注册表，if/else 散落

**对**：`REGISTRY["parser"]["plain_text"]` 统一工厂（§9）。

---

## 9. 综合实战：注册表 + 管道

```python
"""pluggable_ingest.py — 路线图 153 综合实战"""
from __future__ import annotations

REGISTRY: dict[str, dict] = {"parser": {}, "splitter": {}, "embedder": {}}

def register(kind: str, impl):
    REGISTRY[kind][impl.name] = impl

def run_ingest(source: str, parser_name: str, splitter_name: str, embedder_name: str):
    parser = REGISTRY["parser"][parser_name]
    splitter = REGISTRY["splitter"][splitter_name]
    embedder = REGISTRY["embedder"][embedder_name]
    raws = parser.parse(source)
    chunks = splitter.split(raws)
    vectors = embedder.embed_documents([c.text for c in chunks])
    return chunks, vectors

# 注册后:
# register("parser", PlainTextParser())
# register("splitter", RecursiveSplitter())
# register("embedder", FakeEmbedder())
# chunks, vecs = run_ingest("data/faq.md", "plain_text", "recursive", "fake")
# → 写入 [128 VectorStore](128.langchain-vectorstore-tutorial.md) 或 [76 Chroma](76.chroma-vector-db-tutorial.md)
```

**验收**：换 `splitter_name` 仅改配置；chunk_id 仍规范。

---

## 10. 与 LangChain 适配

| 协议 | LC 适配 |
|------|---------|
| Parser | BaseLoader → RawDocument |
| Splitter | TextSplitter.split_documents |
| Embedder | Embeddings 类 |

框架是 **适配器之一**，不是协议本身（[135](135.pipeline-vs-framework-tutorial.md)）。

---

## 11. 综合概念地图

![可插拔概念地图](image/pluggable-parser-splitter-embedder/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

**Q：要用 ABC 还是 Protocol？**  
A：Python 3.10+ 推荐 **Protocol** + `runtime_checkable`。

**Q：配置放哪？**  
A：[138 配置驱动](138.config-driven-pipeline-tutorial.md) YAML。

**Q：与 [129-130 LC](129.langchain-document-loader-tutorial.md)？**  
A：LC 作默认适配器实现，保留换自研 Parser 能力。

**Q：多语言 Embedder？**  
A：[70](70.mixed-language-embedding-tutorial.md) 单独实现注册。

**Q：如何测试？**  
A：各实现 **契约测试** + 金标文件 golden parse/split。

**Q：性能？**  
A：Parser/Splitter 常 CPU 瓶颈；Embedder 走 GPU 批处理。

**Q：和 C 模块关系？**  
A：C 教原理；本篇教 **工程接口**。

**Q：下一步接口？**  
A：[137 Store/Retriever/Generator](137.pluggable-store-retriever-generator-tutorial.md)。

---

## 13. 总结与系列下一步

**可插拔 Parser/Splitter/Embedder** 是 **混合架构的地基**，让 [135 取舍](135.pipeline-vs-framework-tutorial.md) 能落地，让 [128 VectorStore](128.langchain-vectorstore-tutorial.md) 只关心 **标准 Chunk+向量**。

**下一步**：[137 下游三件套](137.pluggable-store-retriever-generator-tutorial.md)、[138 配置驱动](138.config-driven-pipeline-tutorial.md)、[139 RAGAS](139.ragas-context-precision-tutorial.md)。

''' + SHARED_FOOTER.format(roadmap="153", tier="地基篇"))


def build_specs():
    return [
        (
            "129.langchain-document-loader-tutorial.md",
            "langchain-document-loader",
            article_129(),
            [
                ("01-loader-idea.png", "hub-spoke", "§3 Loader 是什么"),
                ("02-loader-types.png", "comparison-matrix", "§5 常用 Loader"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-loader-idea.md", "hub-spoke", "Document Loader 是什么？",
                 "Center: 文件→Document\nSpokes: load/lazy_load/metadata/下游Splitter",
                 "Document Loader · §3"),
                ("02-loader-types.md", "comparison-matrix", "常用 Loader 对比",
                 "Text/PDF/Unstructured/Directory",
                 "Document Loader · §5"),
                ("03-concept-map.md", "bento-grid", "Loader 概念速记",
                 "Tiles: load, metadata, DirectoryLoader, 增量, Splitter",
                 "Document Loader · §11"),
            ],
        ),
        (
            "130.langchain-text-splitter-tutorial.md",
            "langchain-text-splitter",
            article_130(),
            [
                ("01-splitter-idea.png", "hub-spoke", "§3 Splitter 是什么"),
                ("02-recursive-split.png", "flowchart", "§5 递归切分"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-splitter-idea.md", "hub-spoke", "Text Splitter 是什么？",
                 "chunk_size/overlap/separators",
                 "Text Splitter · §3"),
                ("02-recursive-split.md", "flowchart", "递归字符切分",
                 "分隔符优先级与 overlap",
                 "Text Splitter · §5"),
                ("03-concept-map.md", "bento-grid", "Splitter 概念地图",
                 "recursive, markdown, chunk_id, VectorStore",
                 "Text Splitter · §11"),
            ],
        ),
        (
            "131.llamaindex-index-types-tutorial.md",
            "llamaindex-index-types",
            article_131(),
            [
                ("01-index-idea.png", "hub-spoke", "§3 Index 概览"),
                ("02-index-types.png", "comparison-matrix", "§6 Index 类型"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-index-idea.md", "hub-spoke", "LlamaIndex Index 是什么",
                 "Document→Node→Index",
                 "Index 类型 · §3"),
                ("02-index-types.md", "comparison-matrix", "Index 类型对比",
                 "Vector/Summary/Tree/Keyword",
                 "Index 类型 · §6"),
                ("03-concept-map.md", "bento-grid", "Index 概念地图",
                 "了解即可, VectorStoreIndex, LC 映射",
                 "Index 类型 · §11"),
            ],
        ),
        (
            "132.llamaindex-query-engine-tutorial.md",
            "llamaindex-query-engine",
            article_132(),
            [
                ("01-query-engine-flow.png", "flowchart", "§3 Query Engine"),
                ("02-vs-lcel.png", "comparison-matrix", "§10 vs LCEL"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-query-engine-flow.md", "flowchart", "Query Engine 流程",
                 "query→retrieve→synthesize→response",
                 "Query Engine · §3"),
                ("02-vs-lcel.md", "comparison-matrix", "Query Engine vs LCEL",
                 "一站式 vs 显式管道",
                 "Query Engine · §10"),
                ("03-concept-map.md", "bento-grid", "Query Engine 概念地图",
                 "了解即可, synthesizer, source_nodes",
                 "Query Engine · §11"),
            ],
        ),
        (
            "133.llamaindex-agent-tutorial.md",
            "llamaindex-agent",
            article_133(),
            [
                ("01-agent-loop.png", "flowchart", "§3 Agent 循环"),
                ("02-query-tool.png", "hub-spoke", "§5 QueryEngineTool"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-agent-loop.md", "flowchart", "Agent 工具循环",
                 "thought→tool→observation",
                 "LlamaIndex Agent · §3"),
                ("02-query-tool.md", "hub-spoke", "QueryEngine 作工具",
                 "多知识库路由",
                 "LlamaIndex Agent · §5"),
                ("03-concept-map.md", "bento-grid", "Agent 概念地图",
                 "了解即可, ReAct, 风险",
                 "LlamaIndex Agent · §11"),
            ],
        ),
        (
            "134.haystack-pipeline-tutorial.md",
            "haystack-pipeline",
            article_134(),
            [
                ("01-pipeline-idea.png", "hub-spoke", "§3 Pipeline"),
                ("02-rag-graph.png", "flowchart", "§5 RAG 图"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-pipeline-idea.md", "hub-spoke", "Haystack Pipeline 思想",
                 "Component+Connection",
                 "Haystack Pipeline · §3"),
                ("02-rag-graph.md", "flowchart", "典型 RAG 管道图",
                 "ingest与query两支",
                 "Haystack Pipeline · §5"),
                ("03-concept-map.md", "bento-grid", "Pipeline 概念地图",
                 "了解即可, 序列化, LCEL对照",
                 "Haystack Pipeline · §11"),
            ],
        ),
        (
            "135.pipeline-vs-framework-tutorial.md",
            "pipeline-vs-framework",
            article_135(),
            [
                ("01-spectrum.png", "comparison-matrix", "§3 光谱"),
                ("02-layer-table.png", "comparison-matrix", "§5 分层表"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-spectrum.md", "comparison-matrix", "自研 vs 框架光谱",
                 "纯自研—混合—框架梭",
                 "Pipeline vs 框架 · §3"),
                ("02-layer-table.md", "comparison-matrix", "分层取舍表",
                 "Parser/Store/Prompt/ACL",
                 "Pipeline vs 框架 · §5"),
                ("03-concept-map.md", "bento-grid", "架构取舍概念地图",
                 "契约, 金标, 回滚",
                 "Pipeline vs 框架 · §11"),
            ],
        ),
        (
            "136.pluggable-parser-splitter-embedder-tutorial.md",
            "pluggable-parser-splitter-embedder",
            article_136(),
            [
                ("01-three-plugins.png", "hub-spoke", "§3 三接口"),
                ("02-registry.png", "flowchart", "§9 注册表"),
                ("03-concept-map.png", "bento-grid", "§11 概念地图"),
            ],
            [
                ("01-three-plugins.md", "hub-spoke", "Parser/Splitter/Embedder",
                 "数据入口三件套",
                 "可插拔三件套 · §3"),
                ("02-registry.md", "flowchart", "注册表工厂",
                 "配置→实现→ingest",
                 "可插拔三件套 · §9"),
                ("03-concept-map.md", "bento-grid", "可插拔概念地图",
                 "Protocol, 适配器, 137衔接",
                 "可插拔三件套 · §11"),
            ],
        ),
    ]
