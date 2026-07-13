---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression — left-to-right pipeline with 5 steps.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: FAISS 入库与查询流水线

Step 1: numpy 向量矩阵
- shape = (N, dim)
- float32

Step 2: 选索引类型
- Flat / IVF / HNSW

Step 3: index.add(vectors)
- 内存索引

Step 4: index.search(q, k)
- 返回 distances + ids

Step 5: 持久化
- faiss.write_index
- faiss.read_index 加载

Side note: id → 原文 chunk 存在你自己的 dict / DB

Footer: FAISS 本地 ANN 完全指南 · §8

All text Simplified Chinese.
