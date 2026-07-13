#!/usr/bin/env python3
"""Create image/{slug}/README.md and prompts/ for articles 17-20."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STYLE_FOOTER = """Style: hand-drawn-edu — macaron pastel cards on warm cream (#F5F0E8), wavy lines, stick figures, hand-lettered Simplified Chinese.

All text Simplified Chinese. Legible, generous whitespace."""

ARTICLES = [
    {
        "slug": "nlp-tokenization-basics",
        "title": "中文分词与 Tokenization",
        "roadmap": "B轨第一篇",
        "images": [
            ("01-three-granularity.png", "comparison-matrix", "§3 粒度字符词子词", "hub-spoke", """Title: 三种粒度：字符、词、子词

Matrix rows:
- 字符 → 无歧义、序列长、语义弱 → 例：自/然/语/言
- 词 → 符合直觉，中文需猜边界 → 例：自然语言/处理
- 子词 → 词表有限、可组合新词 → 例：自然/语言/处理

Bottom: RAG 里三种粒度分别服务倒排、BM25、LLM token"""),
            ("02-nlp-ir-llm-flow.png", "linear-progression", "§2 NLP IR LLM", "linear-progression", """Title: 同一问句，三条链路

Flow left to right:
1. 用户问题
2. 分词 / tokenize（Seg）
3a. 倒排索引 IR（BM25）
3b. 向量检索（可选）
4. 大模型生成（LLM）

Note: 给倒排的分词 ≠ 给 GPT 的 token，不必强行统一"""),
            ("03-concept-map.png", "bento-grid", "§11 综合概念地图", "bento-grid", """Title: 综合概念地图：分词与 Token 一览

Cells (2×4):
1. 分词 → 中文加隐形空格 → jieba / IK
2. Tokenization → 模型吃的碎片 → BPE / SentencePiece
3. Token → 计费与上下文单位 → max_tokens
4. 词表 → 认字表 → OOV 靠子词
5. OOV → 表外词 → 子词切分缓解
6. IR term → 倒排词项 → 先分词再索引
7. LLM token → API 长度 → 与 Word 字数不同
8. RAG 影响 → chunk/索引/计费 → 三套系统各用各的"""),
        ],
    },
    {
        "slug": "tfidf-principles",
        "title": "TF-IDF 原理",
        "roadmap": "B轨第二篇",
        "images": [
            ("01-bow-matrix.png", "comparison-matrix", "§2 词袋到矩阵", "comparison-matrix", """Title: 从词袋到词项–文档矩阵

LEFT: 词袋模型 — 抖进袋子只数词频，丢掉词序
RIGHT: 矩阵示意 — 行=term，列=doc，格=出现次数
Example terms: 报销/年假/公司
Insight: 「公司」每篇都有 → 不能区分主题 → 需要 IDF"""),
            ("02-tf-idf-formula.png", "structural-breakdown", "§5 TF-IDF 合在一起", "structural-breakdown", """Title: TF × IDF = 词项权重

Three panels:
1. TF — 词在这篇多显眼 — 计数或归一化
2. IDF — 全库越罕见越值钱 — log(N/df)
3. TF-IDF — 两者相乘 — 本篇主题词浮上来

Bottom: 稀有词命中一次 > 常见词命中三次"""),
            ("03-concept-map.png", "bento-grid", "§12 综合概念地图", "bento-grid", """Title: 综合概念地图：TF-IDF 名词一览

Cells:
1. 词袋 BoW → 丢词序数词频
2. TF → 本篇词频
3. IDF → 逆文档频率
4. 停用词 → 公司/规定 → 删或降权
5. 余弦相似度 → 查询与文档比夹角
6. 稀疏矩阵 → 倒排 posting 存储
7. 局限 → 无语义/同义词
8. RAG 位置 → 基线或 Hybrid 稀疏翼"""),
        ],
    },
    {
        "slug": "bm25-sparse-retrieval",
        "title": "BM25 稀疏检索",
        "roadmap": "B轨第三篇",
        "images": [
            ("01-sparse-rag-flow.png", "linear-progression", "§2 稀疏检索在 RAG", "linear-progression", """Title: BM25 在 RAG 里站哪一步

Flow:
用户问题 → 分词 → BM25 倒排检索 → (可选)向量检索 → 融合 top-k → 拼 prompt 生成

Note: BM25 只捞候选，不生成答案
Output: score、rank、snippet"""),
            ("02-bm25-formula.png", "structural-breakdown", "§5 BM25 公式", "structural-breakdown", """Title: BM25 公式拆开读

Panels:
1. IDF 项 — 稀有词加分 — 与 TF-IDF 同族
2. TF 饱和项 — f/(f+k1) — 同一词多出现收益递减
3. 长度归一 — |d|/avgdl — 长文不能自动赢

Knobs: k1 控制饱和速度，b 控制长度惩罚
Footer note: Elasticsearch 默认 similarity: BM25"""),
            ("03-concept-map.png", "bento-grid", "§13 综合概念地图", "bento-grid", """Title: 综合概念地图：BM25 名词一览

Cells:
1. 稀疏检索 → 词项匹配 → 相对稠密向量
2. BM25 → 工业默认打分 → Lucene/ES
3. k1 → 词频饱和旋钮
4. b → 文档长度归一
5. posting list → 倒排承载打分
6. 多词查询 → 共有 term 分数累加
7. rank_bm25 → Python 试验库
8. Hybrid → 稀疏 + 稠密 → RRF/重排"""),
        ],
    },
    {
        "slug": "inverted-index",
        "title": "倒排索引概念",
        "roadmap": "B轨第四篇",
        "images": [
            ("01-forward-vs-inverted.png", "binary-comparison", "§2 正排 vs 倒排", "binary-comparison", """Title: 正排 vs 倒排

LEFT 正排 (coral):
- doc_id → 正文/分词/元数据
- 按书架每一本书记录
- 适合读全文，不适合全库找词

RIGHT 倒排 (mint):
- term → [(doc_id, tf), ...]
- 书末关键词索引
- 查「报销」立刻得 chunk 列表

Center: 2 万 chunk 不能每次全库扫描"""),
            ("02-index-blocks.png", "structural-breakdown", "§3 三块积木", "structural-breakdown", """Title: 倒排索引三块积木

1. 词典 (Dictionary) — term → posting 指针
2. Posting List — doc_id + tf (+ 位置可选)
3. 全局统计 — N, df, avgdl — BM25 用

Build: chunk 分词 → 累加 tf → 写 posting
Query: 查 term → 取 posting → 交集/并集 → 打分"""),
            ("03-concept-map.png", "bento-grid", "§10 综合概念地图", "bento-grid", """Title: 综合概念地图：倒排索引一览

Cells:
1. 倒排索引 → term 找 doc → 毫秒级检索
2. 正排 → doc 找内容 → snippet 原文
3. 词典 → term 入口
4. Posting → 含该词的 doc 列表
5. tf → posting 里出现次数
6. 交集查询 → 多 term AND
7. BM25 → 在 posting 上算分
8. vs 向量库 → 稀疏/稠密并存"""),
        ],
    },
]


def write_prompt(path: Path, layout: str, body: str) -> None:
    path.write_text(
        f"---\nlayout: {layout}\nstyle: hand-drawn-edu\naspect_ratio: 16:9\nlanguage: zh\n---\n\n"
        f"Create a professional educational infographic, 16:9 landscape.\n"
        f"Layout: {layout}.\n"
        f"{STYLE_FOOTER}\n\n"
        f"{body.strip()}\n",
        encoding="utf-8",
    )


def main() -> None:
    for art in ARTICLES:
        base = ROOT / "image" / art["slug"]
        prompts = base / "prompts"
        prompts.mkdir(parents=True, exist_ok=True)
        rows = []
        for png, layout, sec, layout2, body in art["images"]:
            stem = png.replace(".png", "")
            write_prompt(prompts / f"{stem}.md", layout2, body)
            rows.append(f"| `{png}` | {layout} | {sec} |")
        readme = (
            f"# {art['title']}信息图（{art['roadmap']}）\n\n\n"
            "| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"
            + "\n".join(rows)
            + "\n\n\n风格：hand-drawn-edu · 16:9 · 中文  \nPrompt 见 `prompts/`。\n"
        )
        (base / "README.md").write_text(readme, encoding="utf-8")
        print(f"OK {art['slug']}")


if __name__ == "__main__":
    main()
