---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — three columns comparing index types.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Flat vs IVF vs HNSW 怎么选？

Column 1: IndexFlat（暴力）
- 100% 召回
- 数据量小 / 评测基线
- 内存全量

Column 2: IVF（倒排聚类）
- 先聚类再搜簇
- 需 train + nprobe 调参
- 百万级常用

Column 3: HNSW（图索引）
- 多层小世界图
- 高召回低延迟
- 内存占用较大

Bottom row: 选型口诀
- <1 万条：Flat
- 10 万～百万：IVF 或 HNSW
- 要磁盘持久化：另存 index 文件

Footer: FAISS 本地 ANN 完全指南 · §5

All text Simplified Chinese.
