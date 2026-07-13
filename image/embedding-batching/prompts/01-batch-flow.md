---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression — pipeline from chunks to batched API calls.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 批量 Embedding 数据流（Batch Embedding Flow）

Step 1: 10,000 chunks 待索引
Step 2: 按 batch_size=64 切分 → 156 次 API 调用
Step 3: 合并向量 → 写入向量库
Step 4: 失败 batch 单独重试，不拖垮全量

Footer: 批量 Embedding 完全指南 · §3

All text Simplified Chinese.
