#!/usr/bin/env python3
"""Generate blog articles 86-94 and image asset scaffolding."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COMMON_PREDECESSORS = (
    "[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、"
    "[77 Milvus](77.milvus-tutorial.md)、[78 Qdrant](78.qdrant-tutorial.md)、"
    "[79 Weaviate](79.weaviate-tutorial.md)、[80 Pinecone](80.pinecone-tutorial.md)、"
    "[81 pgvector](81.pgvector-tutorial.md)、[82 Elasticsearch 向量](82.elasticsearch-vector-tutorial.md)、"
    "[83 OpenSearch 混合](83.opensearch-hybrid-tutorial.md)、[84 Flat 暴力检索](84.flat-brute-force-search-tutorial.md)、"
    "[85 IVF 倒排文件](85.ivf-index-tutorial.md)"
)

IMAGE_SPECS = {
    "hnsw-index": {
        "file": "86.hnsw-index-tutorial.md",
        "title": "C4 向量存储（十二）：HNSW 图索引完全指南",
        "roadmap": 103,
        "tier": "地基",
        "slug": "hnsw-index",
        "img1": ("01-hnsw-idea.png", "hub-spoke", "§3 HNSW 是什么"),
        "img2": ("02-hnsw-params.png", "comparison-matrix", "§5 核心参数"),
        "img1_prompt": "HNSW 图索引是什么？",
        "img2_prompt": "HNSW 三大参数怎么调？",
    },
    "ann-recall-latency": {
        "file": "87.ann-recall-latency-tutorial.md",
        "title": "C4 向量存储（十三）：ANN 召回率与延迟权衡完全指南",
        "roadmap": 104,
        "tier": "主线",
        "slug": "ann-recall-latency",
        "img1": ("01-recall-latency.png", "hub-spoke", "§3 权衡直觉"),
        "img2": ("02-benchmark-curve.png", "comparison-matrix", "§6 评测曲线"),
        "img1_prompt": "召回率与延迟怎么权衡？",
        "img2_prompt": "ANN 评测曲线怎么读？",
    },
    "metadata-filter-retrieval": {
        "file": "88.metadata-filter-retrieval-tutorial.md",
        "title": "C4 向量存储（十四）：Metadata Filter 过滤检索完全指南",
        "roadmap": 105,
        "tier": "地基",
        "slug": "metadata-filter-retrieval",
        "img1": ("01-filter-idea.png", "hub-spoke", "§3 过滤检索"),
        "img2": ("02-pre-post-filter.png", "comparison-matrix", "§5 前滤后滤"),
        "img1_prompt": "元数据过滤检索是什么？",
        "img2_prompt": "前滤 vs 后滤怎么选？",
    },
    "multi-tenant-namespace": {
        "file": "89.multi-tenant-namespace-tutorial.md",
        "title": "C4 向量存储（十五）：多租户 Namespace 隔离完全指南",
        "roadmap": 106,
        "tier": "地基",
        "slug": "multi-tenant-namespace",
        "img1": ("01-tenant-idea.png", "hub-spoke", "§3 多租户"),
        "img2": ("02-isolation-patterns.png", "comparison-matrix", "§5 隔离模式"),
        "img1_prompt": "多租户向量库怎么隔离？",
        "img2_prompt": "Namespace vs Collection 怎么选？",
    },
    "vector-db-backup": {
        "file": "90.vector-db-backup-tutorial.md",
        "title": "C4 向量存储（十六）：向量库备份与恢复完全指南",
        "roadmap": 107,
        "tier": "地基",
        "slug": "vector-db-backup",
        "img1": ("01-backup-idea.png", "hub-spoke", "§3 备份什么"),
        "img2": ("02-restore-flow.png", "comparison-matrix", "§6 恢复流程"),
        "img1_prompt": "向量库要备份什么？",
        "img2_prompt": "备份恢复流程怎么走？",
    },
    "dense-retrieval": {
        "file": "91.dense-retrieval-tutorial.md",
        "title": "C4 向量存储（十七）：Dense 稠密检索完全指南",
        "roadmap": 108,
        "tier": "地基",
        "slug": "dense-retrieval",
        "img1": ("01-dense-idea.png", "hub-spoke", "§3 稠密检索"),
        "img2": ("02-dense-pipeline.png", "comparison-matrix", "§5 RAG 流水线"),
        "img1_prompt": "Dense 稠密检索是什么？",
        "img2_prompt": "稠密检索在 RAG 里怎么走？",
    },
    "sparse-retrieval-rag": {
        "file": "92.sparse-retrieval-rag-tutorial.md",
        "title": "C4 向量存储（十八）：Sparse 稀疏检索（BM25）在 RAG 中完全指南",
        "roadmap": 109,
        "tier": "地基",
        "slug": "sparse-retrieval-rag",
        "img1": ("01-sparse-rag.png", "hub-spoke", "§3 稀疏在 RAG"),
        "img2": ("02-bm25-vs-dense.png", "comparison-matrix", "§5 BM25 vs Dense"),
        "img1_prompt": "稀疏检索在 RAG 里站哪？",
        "img2_prompt": "BM25 与 Dense 怎么分工？",
    },
    "hybrid-search": {
        "file": "93.hybrid-search-tutorial.md",
        "title": "C4 向量存储（十九）：混合检索 Hybrid Search 完全指南",
        "roadmap": 110,
        "tier": "主线",
        "slug": "hybrid-search",
        "img1": ("01-hybrid-idea.png", "hub-spoke", "§3 混合检索"),
        "img2": ("02-hybrid-arch.png", "comparison-matrix", "§6 架构模式"),
        "img1_prompt": "混合检索是什么？",
        "img2_prompt": "混合检索有哪些架构？",
    },
    "rrf-fusion": {
        "file": "94.rrf-fusion-tutorial.md",
        "title": "C4 向量存储（二十）：RRF 倒数排名融合完全指南",
        "roadmap": 111,
        "tier": "地基",
        "slug": "rrf-fusion",
        "img1": ("01-rrf-idea.png", "hub-spoke", "§3 RRF 直觉"),
        "img2": ("02-rrf-formula.png", "comparison-matrix", "§5 RRF 公式"),
        "img1_prompt": "RRF 融合是什么？",
        "img2_prompt": "RRF 公式怎么算？",
    },
}


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def faq_block(topic: str, items: list[str]) -> str:
    lines = [f"### 12.{i} {title}\n\n{body}\n" for i, (title, body) in enumerate(items, 1)]
    return "\n".join(lines)


def write_image_assets(spec: dict) -> None:
    slug = spec["slug"]
    base = ROOT / "image" / slug
    prompts = base / "prompts"
    base.mkdir(parents=True, exist_ok=True)
    prompts.mkdir(parents=True, exist_ok=True)

    img1_name, img1_layout, img1_sec = spec["img1"]
    img2_name, img2_layout, img2_sec = spec["img2"]

    readme = f"""# {spec['title'].split('：', 1)[-1]}信息图（路线图 {spec['roadmap']}）



| 文件 | 布局 | 插入位置 |

|------|------|----------|

| `{img1_name}` | {img1_layout} | {img1_sec} |

| `{img2_name}` | {img2_layout} | {img2_sec} |

| `03-concept-map.png` | bento-grid | §概念地图 |



风格：hand-drawn-edu · 16:9 · 中文  

Prompt 见 `prompts/`。



说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。
"""
    (base / "README.md").write_text(readme, encoding="utf-8")

    for idx, (name, layout, sec, title) in [
        (1, img1_name, img1_layout, img1_sec, spec["img1_prompt"]),
        (2, img2_name, img2_layout, img2_sec, spec["img2_prompt"]),
    ]:
        stem = name.replace(".png", "")
        prompt = f"""---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

Center hub: {spec['title'].split('：', 1)[-1].replace('完全指南', '')}

Footer: {spec['title'].split('：', 1)[-1]} · {sec}

All text Simplified Chinese.
"""
        (prompts / f"{stem.split('-')[0]}-{stem.split('-', 1)[1]}.md").write_text(prompt, encoding="utf-8")

    concept = f"""---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: bento-grid — 6 panels summarizing the full article.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {spec['title'].split('：', 1)[-1]} · 概念地图

Panels: 前言、核心概念、实战、先错对对、FAQ 要点、系列下一步

Footer: 路线图 {spec['roadmap']} · {spec['tier']}篇

All text Simplified Chinese.
"""
    (prompts / "03-concept-map.md").write_text(concept, encoding="utf-8")


# Article bodies imported from separate module for maintainability
from articles_86_94_content import ARTICLES  # noqa: E402


def main() -> None:
    results = []
    for key, spec in IMAGE_SPECS.items():
        body = ARTICLES[key]
        path = ROOT / spec["file"]
        path.write_text(body, encoding="utf-8")
        write_image_assets(spec)
        cnt = hanzi_count(body)
        results.append((spec["file"], cnt, cnt >= 5000))
        print(f"{spec['file']}: hanzi={cnt} ok={cnt >= 5000}")

    failed = [r for r in results if not r[2]]
    if failed:
        raise SystemExit(f"Articles below 5000 hanzi: {failed}")
    print("All articles OK.")


if __name__ == "__main__":
    main()
