---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: bento-grid.
Style: hand-drawn-edu — macaron pastel cards on warm cream (#F5F0E8), wavy lines, stick figures, hand-lettered Simplified Chinese.

All text Simplified Chinese. Legible, generous whitespace.

Title: 综合概念地图：分词与 Token 一览

Cells (2×4):
1. 分词 → 中文加隐形空格 → jieba / IK
2. Tokenization → 模型吃的碎片 → BPE / SentencePiece
3. Token → 计费与上下文单位 → max_tokens
4. 词表 → 认字表 → OOV 靠子词
5. OOV → 表外词 → 子词切分缓解
6. IR term → 倒排词项 → 先分词再索引
7. LLM token → API 长度 → 与 Word 字数不同
8. RAG 影响 → chunk/索引/计费 → 三套系统各用各的
