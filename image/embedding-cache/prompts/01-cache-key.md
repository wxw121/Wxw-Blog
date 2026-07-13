---
layout: hierarchical-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hierarchical-tree — cache key anatomy from text to hash lookup.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Embedding 缓存键设计（Cache Key Design）

Root: cache_key = hash(text + model + version + normalize_flag)

Branches:
- text：chunk 原文（或规范化后文本）
- model：text-embedding-3-small
- version：模型版本 / 预处理版本
- normalize_flag：是否 L2 归一化

Leaf: 命中 → 直接取向量；未命中 → API embed → 写回

Footer: Embedding 缓存策略完全指南 · §4

All text Simplified Chinese.
