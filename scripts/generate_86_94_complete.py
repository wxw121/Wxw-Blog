#!/usr/bin/env python3
"""Generate all 86-94 tutorials + image assets."""
import importlib.util
import re
import sys
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


def hz(t: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def mk_faq(items, sec="12"):
    return "\n".join(f"### {sec}.{i} {a}\n\n{b}\n" for i, (a, b) in enumerate(items, 1))


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
    for name, layout, sec, pt in [(i1[0], i1[1], i1[2], p1), (i2[0], i2[1], i2[2], p2)]:
        stem = name.replace(".png", "")
        (base / "prompts" / f"{stem}.md").write_text(
            f"---\nlayout: {layout}\nstyle: hand-drawn-edu\naspect_ratio: 16:9\nlanguage: zh\n---\n\n"
            f"Title: {pt}\nFooter: {title_short} · {sec}\nSimplified Chinese hand-drawn-edu infographic 16:9.\n",
            encoding="utf-8",
        )
    (base / "prompts" / "03-concept-map.md").write_text(
        f"---\nlayout: bento-grid\nstyle: hand-drawn-edu\naspect_ratio: 16:9\nlanguage: zh\n---\n\n"
        f"Concept map bento-grid: {title_short}, roadmap {roadmap}, {tier}.\n",
        encoding="utf-8",
    )


# load helpers from build_all
spec = importlib.util.spec_from_file_location(
    "build_all", Path(__file__).parent / "build_all_86_94.py"
)
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)

# load 86
_part1 = (Path(__file__).parent / "articles_86_94_content_part1.py").read_text(encoding="utf-8")
_s = _part1.index("ARTICLE_86 = r'''") + len("ARTICLE_86 = r'''")
_e = _part1.rindex("'''")
A86 = _part1[_s:_e].replace("{preds}", PREDS)
A86 = A86.replace("### 11.15 延伸阅读", ba.HNSW_EXTRA + "\n### 11.15 延伸阅读")

A87 = ba.article_87()
