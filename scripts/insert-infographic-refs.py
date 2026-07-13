#!/usr/bin/env python3
"""Insert infographic image references into tutorial markdown (articles 51-79)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# article_file -> (slug, [(anchor_substring, png_file, alt_text), ...])
INSERTIONS: dict[str, tuple[str, list[tuple[str, str, str]]]] = {
    "51.metadata-chunk-id-tutorial.md": (
        "metadata-chunk-id",
        [
            ("读下图，看 chunk_id 在 doc 之下的位置。", "01-chunk-id-role.png", "chunk_id 在文档-版本-块层级中的角色"),
            ("读下图，对比序号型与结构型在重切块时的行为。", "02-stable-ids.png", "chunk_id 稳定生成策略：序号型 vs 结构型 vs 偏移型"),
            ("读下图时，先看「chunk_id 元数据概念速记」", "03-concept-map.png", "chunk_id 元数据概念速记"),
        ],
    ),
    "52.metadata-source-page-tutorial.md": (
        "metadata-source-page",
        [
            ("读下图，分清「给人看的名字」", "01-source-fields.png", "source 字段族：显示名、存储键与稳定 ID"),
            ("读下图，看 page 与 section 如何并行", "02-page-section.png", "page 与 section 并行溯源坐标"),
            ("读下图时，先看「Source / Page / Section 概念地图」", "03-concept-map.png", "Source / Page / Section 概念地图"),
        ],
    ),
    "53.metadata-acl-tutorial.md": (
        "metadata-acl",
        [
            ("读下图，建立「权限跟 chunk 走」的习惯。", "01-acl-idea.png", "ACL：chunk 上的「谁能看」"),
            ("读下图，理解两种工程路径的本质差别。", "02-filter-vs-namespace.png", "检索后过滤 vs 索引时隔离"),
            ("读下图，把事故路径记牢", "03-overreach-risk.png", "越权风险：从索引到 prompt 的泄露链"),
            ("读下图时，先看「ACL 概念地图」", "04-concept-map.png", "ACL 概念地图"),
        ],
    ),
    "54.metadata-timestamp-version-tutorial.md": (
        "metadata-timestamp-version",
        [
            ("读下图，避免「所有时间都叫 timestamp」", "01-time-fields.png", "时间字段族：各管哪段生命周期"),
            ("读下图，理解「语义像」不等于「还能用」。", "02-stale-knowledge.png", "过期知识：相似度不救你"),
            ("读下图时，先看「Timestamp Version 概念地图」", "03-concept-map.png", "Timestamp / Version 概念地图"),
        ],
    ),
    "55.ocr-scanned-docs-tutorial.md": (
        "ocr-scanned-docs",
        [
            ("读下图：同一份「看起来是 PDF」", "01-scan-vs-text.png", "扫描件 vs 文本层：先分类再动手"),
            ("读下图：从上传到 chunk", "02-ocr-pipeline.png", "OCR 流水线在 RAG 解析阶段的位置"),
            ("读下图，把本篇与前后篇挂到一张 mental map。", "03-concept-map.png", "OCR 与扫描件概念地图"),
        ],
    ),
    "56.multimodal-image-text-tutorial.md": (
        "multimodal-image-text",
        [
            ("读下图：按 **信息载体** 分档", "01-image-text-need.png", "企业 RAG 何时需要「看图」"),
            ("读下图：左 **字串路线**，右 **语义路线**", "02-ocr-vs-vlm.png", "OCR vs VLM：两条路线的分工"),
            ("读下图，把 OCR、VLM、文本 RAG、分块串起来。", "03-concept-map.png", "多模态图+文概念地图"),
        ],
    ),
    "57.fixed-size-chunking-tutorial.md": (
        "fixed-size-chunking",
        [
            ("读下图：长文像一根香肠", "01-fixed-size-idea.png", "固定长度分块：按窗口切片"),
            ("读下图：代码流水线从 **读入 → 计数 → 滑窗 → 写 JSONL**。", "03-code-pipeline.png", "固定长度分块代码流水线"),
            ("读下图：固定长度 **看不见** 句号", "02-cut-mid-sentence.png", "固定长度从中间切断句子"),
            ("读下图，固定长度在 C2 分块族中的位置。", "04-concept-map.png", "固定长度分块概念地图"),
        ],
    ),
    "58.recursive-character-chunking-tutorial.md": (
        "recursive-character-chunking",
        [
            ("**递归字符分块**：给定一组分隔符", "02-recursive-flow.png", "递归字符分块流程"),
            ("顺序很重要：`\"\\n\\n\"` 代表段落", "01-separator-ladder.png", "递归分块分隔符阶梯"),
            ("**错：不清洗文档就分块。**", "03-concept-map.png", "递归字符分块概念速记"),
        ],
    ),
    "59.sentence-boundary-chunking-tutorial.md": (
        "sentence-boundary-chunking",
        [
            ("读下图，对照同一段制度正文", "01-sentence-cut.png", "硬切 vs 句子边界分块"),
            ("读下图：句子像珠子", "02-pack-sentences.png", "句子打包：累加到 chunk 预算"),
            ("读下图，把本篇放进 C2 分块策略族谱。", "03-concept-map.png", "句子边界分块概念地图"),
        ],
    ),
    "60.chunk-overlap-tutorial.md": (
        "chunk-overlap",
        [
            ("读下图：同一段报销流程", "01-no-overlap-loss.png", "无 Overlap 时边界信息丢失"),
            ("读下图：文档条带被切成带 **重叠区** 的滑动窗口。", "02-overlap-window.png", "重叠窗口：滑窗怎么叠"),
            ("读下图时，先看「Overlap 概念地图」", "03-concept-map.png", "Overlap 概念地图"),
        ],
    ),
    "61.chunk-size-tradeoff-tutorial.md": (
        "chunk-size-tradeoff",
        [
            ("读下图：左侧 chunk 过大", "01-too-big-too-small.png", "Chunk 太大 vs 太小各伤什么"),
            ("读下图：chunk_size 位于中心", "02-tradeoff-axes.png", "Chunk size 四维 trade-off 轴"),
            ("读下图：调参不是一次性", "03-tuning-loop.png", "Chunk size 调参闭环"),
            ("读下图时，先看「Chunk Size Trade-off 概念地图」", "04-concept-map.png", "Chunk Size Trade-off 概念地图"),
        ],
    ),
    "62.structure-aware-chunking-tutorial.md": (
        "structure-aware-chunking",
        [
            ("读下图：典型制度文档的标题树", "01-heading-tree.png", "标题树：H1 / H2 / H3 怎么读"),
            ("读下图：同一 MD 按 H2 切成", "02-by-section.png", "按 Section 切：边界规则"),
            ("读下图：左固定 500 字，右按 H2 结构切。", "03-vs-fixed.png", "结构感知 vs 固定长度分块"),
            ("读下图时，先看「结构感知分块概念地图」", "04-concept-map.png", "结构感知分块概念地图"),
        ],
    ),
    "63.markdown-ast-chunking-tutorial.md": (
        "markdown-ast-chunking",
        [
            ("读下图：从源 Markdown 到 AST", "01-md-ast.png", "Markdown AST 解析树与块级节点"),
            ("读下图：同一 AST 节点流", "02-chunk-by-heading-node.png", "按标题节点切分 chunk"),
            ("读下图时，先看「Markdown AST 分块概念速记」", "03-concept-map.png", "Markdown AST 分块概念速记"),
        ],
    ),
    "64.html-dom-chunking-tutorial.md": (
        "html-dom-chunking",
        [
            ("读下图：典型帮助页 DOM", "01-dom-tree.png", "HTML DOM 树与语义标签"),
            ("读下图：去噪后的 article", "02-chunk-by-section.png", "按 section 与标题切分 HTML"),
            ("读下图时，先看「HTML DOM 分块概念速记」", "03-concept-map.png", "HTML DOM 分块概念速记"),
        ],
    ),
    "65.parent-document-retriever-tutorial.md": (
        "parent-document-retriever",
        [
            ("读下图：错误「只大块索引」", "01-small-retrieve-big-gen.png", "小块检索、大块生成"),
            ("读下图：一个 parent 拆多个 child", "02-parent-child.png", "父子块关系与存储模型"),
            ("读下图：从 ingest 到 answer 的完整路径。", "03-pipeline.png", "Parent-Document 入库与查询流水线"),
            ("读下图时，先看「Parent-Document Retriever 概念速记」", "04-concept-map.png", "Parent-Document Retriever 概念速记"),
        ],
    ),
    "66.l2-normalization-tutorial.md": (
        "l2-normalization",
        [
            ("读下图前，先想：两段 **语义同样相关**", "01-why-normalize.png", "为什么要 L2 归一化"),
            ("读下图：从原始向量到单位向量", "02-cosine-equals-dot.png", "归一化后余弦 = 点积"),
            ("读下图前，用一句话串起", "03-concept-map.png", "L2 归一化概念速记"),
        ],
    ),
    "67.embedding-batching-tutorial.md": (
        "embedding-batching",
        [
            ("读下图：一万 chunk 如何切成多批", "01-batch-flow.png", "批量 Embedding 数据流"),
            ("读下图：batch 很小 vs 很大时", "02-throughput-latency.png", "批量 Embedding：吞吐 vs 延迟"),
            ("读下图时，先看「批量 Embedding 概念速记」", "03-concept-map.png", "批量 Embedding 概念速记"),
        ],
    ),
    "68.embedding-cache-tutorial.md": (
        "embedding-cache",
        [
            ("读下图：一根 cache_key 上应挂哪些字段。", "01-cache-key.png", "Embedding 缓存键设计"),
            ("读下图：三种介质的典型分工。", "02-storage-options.png", "Redis / SQLite / 磁盘缓存选型"),
            ("读下图时，先看「Embedding 缓存概念速记」", "03-concept-map.png", "Embedding 缓存概念速记"),
        ],
    ),
    "69.embedding-retry-rate-limit-tutorial.md": (
        "embedding-retry-rate-limit",
        [
            ("下面这张图说明指数退避的节奏。", "01-backoff-retry.png", "指数退避重试节奏"),
            ("下面这张图说明遇到 429 时应该读哪些信号。", "02-429-headers.png", "429 与限流响应头怎么读"),
            ("读下图时，先看「Embedding API 韧性概念地图」", "03-concept-map.png", "Embedding API 韧性概念地图"),
        ],
    ),
    "70.mixed-language-embedding-tutorial.md": (
        "mixed-language-embedding",
        [
            ("读下图，盯住「混合语料」行", "01-multilingual-models.png", "多语言 Embedding 模型对照"),
            ("读决策图前，记住：**code-switching 比例 > 15%**", "02-split-vs-unified.png", "分语言索引 vs 统一多语索引"),
            ("读下图时，先看「中英混合语料概念地图」", "03-concept-map.png", "中英混合语料概念地图"),
        ],
    ),
    "71.domain-embedding-evaluation-tutorial.md": (
        "domain-embedding-evaluation",
        [
            ("读下图，盯住「第一个相关排第几」", "01-golden-set-recall.png", "Golden Set 与 Recall@k / MRR"),
            ("读下图时，先看「领域语料模型对比」", "02-domain-compare.png", "领域语料 Embedding 模型对比"),
            ("读下图时，先看「领域 Embedding 评估概念地图」", "03-concept-map.png", "领域 Embedding 评估概念地图"),
        ],
    ),
    "72.local-embedding-inference-tutorial.md": (
        "local-embedding-inference",
        [
            ("读下图：不是「本地永远更好」", "01-local-vs-cloud.png", "本地推理 vs 云端 API"),
            ("读下图时，先看「推理技术栈」", "02-inference-stack.png", "本地 Embedding 推理技术栈"),
            ("读下图时，先看「概念地图」", "03-concept-map.png", "本地 Embedding 概念地图"),
        ],
    ),
    "73.embedding-finetune-tutorial.md": (
        "embedding-finetune",
        [
            ("读下图，从「Recall 不达标」出发", "01-swap-vs-finetune.png", "换模型 vs 微调：决策树"),
            ("读下图时，先看「Triplet Loss」", "02-triplet-loss.png", "Triplet Loss 直觉"),
            ("读下图时，先看「概念地图」", "03-concept-map.png", "Embedding 微调概念地图"),
        ],
    ),
    "74.contrastive-learning-tutorial.md": (
        "contrastive-learning",
        [
            ("读下图时，先看「正例与负例」", "01-pos-neg-pairs.png", "对比学习：正例对与负例对"),
            ("读下图时，先看「InfoNCE 直觉」", "02-infonce-intuition.png", "InfoNCE 直觉"),
            ("读下图时，先看「概念地图」", "03-concept-map.png", "对比学习概念地图"),
        ],
    ),
    "75.faiss-ann-tutorial.md": (
        "faiss-ann",
        [
            ("读下图：暴力最近邻与 ANN", "01-ann-idea.png", "ANN：精确 vs 近似最近邻"),
            ("读下图三列对比", "02-flat-vs-ivf-hnsw.png", "Flat vs IVF vs HNSW"),
            ("读下图时，先看「FAISS 入库与查询流水线」", "03-save-load-pipeline.png", "FAISS 入库与查询流水线"),
            ("读下图时，先看「FAISS 概念速记」", "04-concept-map.png", "FAISS 概念速记"),
        ],
    ),
    "76.chroma-vector-db-tutorial.md": (
        "chroma-vector-db",
        [
            ("打包到一个易用接口里。", "01-chroma-idea.png", "Chroma 是什么"),
            ("RAG 不应只按相似度召回", "03-metadata-filter.png", "Chroma metadata 过滤"),
            ('本地实验建议用 `PersistentClient(path="./chroma_db")`。', "02-collection-persist.png", "Collection 与持久化"),
            ("Chroma 是理解向量库的好入口", "04-concept-map.png", "Chroma 概念地图"),
        ],
    ),
    "77.milvus-tutorial.md": (
        "milvus",
        [
            ("Milvus 把向量和标量字段存在 collection 中", "01-milvus-idea.png", "Milvus 分布式向量库是什么"),
            ("**Collection** 类似一张表，包含 schema。", "02-schema-partition.png", "Collection Schema 与 Partition"),
            ("Milvus 常见检索流程如下：", "03-search-filter.png", "Milvus 查询与 expr 过滤"),
        ],
    ),
    "78.qdrant-tutorial.md": (
        "qdrant",
        [
            ("读下图时，注意 payload 不是可有可无的备注", "01-qdrant-idea.png", "Qdrant 向量库是什么"),
            ("**Payload**：业务字段", "02-point-payload.png", "Point 与 Payload"),
            ("不要把所有 metadata 都塞进 payload 后不加选择。", "03-search-filter.png", "Qdrant search 与 filter"),
        ],
    ),
    "79.weaviate-tutorial.md": (
        "weaviate",
        [
            ("Weaviate 把对象属性、向量和查询放在一个 schema 化系统里。", "01-weaviate-idea.png", "Weaviate 图式向量库"),
            ("**Class**：对象类型，类似表或集合。", "02-class-object.png", "Class 与 Object"),
            ("查询结果应返回证据文本和 doc_id", "03-near-vector.png", "nearVector 与 where 过滤"),
        ],
    ),
}

IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")


def insert_after_anchor(content: str, anchor: str, slug: str, png: str, alt: str) -> str:
    img_line = f"![{alt}](image/{slug}/{png})"
    if img_line in content:
        return content
    idx = content.find(anchor)
    if idx == -1:
        raise ValueError(f"Anchor not found: {anchor!r}")
    line_end = content.find("\n", idx)
    if line_end == -1:
        line_end = len(content)
    insert_at = line_end + 1
    block = f"\n{img_line}\n"
    return content[:insert_at] + block + content[insert_at:]


def main() -> None:
    updated = 0
    skipped = 0
    for article, (slug, items) in INSERTIONS.items():
        path = ROOT / article
        if not path.exists():
            print(f"SKIP missing: {article}")
            skipped += 1
            continue
        content = path.read_text(encoding="utf-8")
        existing_refs = len(IMG_REF.findall(content))
        if existing_refs >= len(items):
            print(f"SKIP already has images: {article} ({existing_refs} refs)")
            skipped += 1
            continue
        for anchor, png, alt in items:
            content = insert_after_anchor(content, anchor, slug, png, alt)
        path.write_text(content, encoding="utf-8")
        print(f"OK {article}: inserted {len(items)} images")
        updated += 1
    print(f"\nDone: {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    main()
