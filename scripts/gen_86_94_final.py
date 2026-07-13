#!/usr/bin/env python3
"""Generate tutorials 86-94 with image scaffolding. Run from blog/scripts/."""
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


def hz(t: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def mk_faq(n: int, items: list[tuple[str, str]], sec: str = "12") -> str:
    return "\n".join(f"### {sec}.{i} {a}\n\n{b}\n" for i, (a, b) in enumerate(items, 1))


def write_img(slug: str, title_short: str, roadmap: int, tier: str,
              img1: tuple, img2: tuple, p1: str, p2: str) -> None:
    base = ROOT / "image" / slug
    (base / "prompts").mkdir(parents=True, exist_ok=True)
    i1, l1, s1 = img1
    i2, l2, s2 = img2
    (base / "README.md").write_text(
        f"# {title_short}信息图（路线图 {roadmap}）\n\n\n"
        f"| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"
        f"| `{i1}` | {l1} | {s1} |\n| `{i2}` | {l2} | {s2} |\n"
        f"| `03-concept-map.png` | bento-grid | §概念地图 |\n\n\n"
        f"风格：hand-drawn-edu · 16:9 · 中文  \nPrompt 见 `prompts/`。\n\n\n"
        f"说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
        encoding="utf-8",
    )
    for stem, layout, sec, pt in [
        (i1.replace(".png", ""), l1, s1, p1),
        (i2.replace(".png", ""), l2, s2, p2),
    ]:
        (base / "prompts" / f"{stem}.md").write_text(
            f"---\nlayout: {layout}\nstyle: hand-drawn-edu\naspect_ratio: 16:9\nlanguage: zh\n---\n\n"
            f"Create a professional educational infographic, 16:9 landscape.\nLayout: {layout}.\n"
            f"Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.\n\n"
            f"Title: {pt}\n\nFooter: {title_short} · {sec}\n\nAll text Simplified Chinese.\n",
            encoding="utf-8",
        )
    (base / "prompts" / "03-concept-map.md").write_text(
        f"---\nlayout: bento-grid\nstyle: hand-drawn-edu\naspect_ratio: 16:9\nlanguage: zh\n---\n\n"
        f"bento-grid concept map for {title_short}, roadmap {roadmap}, tier {tier}. Simplified Chinese.\n",
        encoding="utf-8",
    )


# Load article 86 base from part1
_part1 = (Path(__file__).parent / "articles_86_94_content_part1.py").read_text(encoding="utf-8")
_s = _part1.index("ARTICLE_86 = r'''") + len("ARTICLE_86 = r'''")
_e = _part1.rindex("'''")
A86 = _part1[_s:_e].replace("{preds}", PREDS)

HNSW_PAD = mk_faq(20, [
    ("生产如何默认 efSearch", "用金标集扫参找拐点后写入配置中心；不同 collection 可有不同默认值。切忌开发机「能跑」就原样上线。"),
    ("与 IVF 联合索引", "超大库可用 IVF 分桶后桶内 HNSW；调参复杂，需专人维护。"),
    ("写入风暴", "批量入库时暂停查询或读写分离；避免建图与查询抢 CPU。"),
    ("图索引碎片", "长期增量后重建索引可降延迟波动。"),
    ("维数 768 vs 1536", "无通用 M 表；以 recall 曲线为准。"),
    ("Windows 上 FAISS", "faiss-cpu 轮子可用；失败用 WSL 与 Linux 对齐。"),
    ("容器内存 limit", "K8s limit 过小会 OOM kill；HNSW 全量在内存。"),
    ("只读副本", "查询副本不接收 insert；写主读从。"),
    ("链路 trace", "OpenTelemetry 标记 search span 含 efSearch。"),
    ("合规", "图结构不匿名化内容；备份加密。"),
    ("教学演示", "二维向量可 t-SNE 可视化图边；高维仅直觉。"),
    ("与 Flat 一致性测试", "每日抽样 100 query 对比 Top-10 Jaccard。"),
    ("参数文档化", "README 记录 M、efConstruction、默认 efSearch 及变更日期。"),
    ("降级策略", "efSearch 提到上限仍不够则触发 Flat 小范围暴力（极小众）。"),
    ("多模态向量", "图像+文本同图需同空间；见 [56 多模态](56.multimodal-image-text-tutorial.md)。"),
    ("Parent chunk", "检索用小向量，返回大 parent 见 [65 篇](65.parent-document-retriever-tutorial.md)。"),
    ("缓存 query 结果", "相同 embedding 可缓存 Top-k id 列表 TTL 5min。"),
    ("限流", "单用户 QPS 限制防刷库。"),
    ("版本回滚", "保留上一版 index 文件一周。"),
    ("团队分工", "算法调 ef；SRE 管内存与备份 [90 篇](90.vector-db-backup-tutorial.md)。"),
], "11")

A86 = A86.replace("### 11.15 延伸阅读", HNSW_PAD + "\n### 11.31 延伸阅读")
