---
layout: structural-breakdown
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: structural-breakdown.
Style: hand-drawn-edu — macaron pastel cards on warm cream (#F5F0E8), wavy lines, stick figures, hand-lettered Simplified Chinese.

All text Simplified Chinese. Legible, generous whitespace.

Title: 倒排索引三块积木

1. 词典 (Dictionary) — term → posting 指针
2. Posting List — doc_id + tf (+ 位置可选)
3. 全局统计 — N, df, avgdl — BM25 用

Build: chunk 分词 → 累加 tf → 写 posting
Query: 查 term → 取 posting → 交集/并集 → 打分
