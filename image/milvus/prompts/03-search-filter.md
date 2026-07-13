---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — two columns before/after.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Milvus 检索：无过滤 vs expr 过滤

Left column: 无过滤
- 全库 ANN Top-k
- 可能越权命中
- 噪音多

Right column: expr 过滤
- doc_id == handbook
- acl_group in [...]
- 检索前缩小候选

Bottom: 与 Chroma where、Qdrant filter 同一原则

Footer: Milvus 分布式向量库完全指南 · §8

All text Simplified Chinese.
