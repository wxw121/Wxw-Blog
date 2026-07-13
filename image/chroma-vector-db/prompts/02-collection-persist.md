---
layout: hierarchical-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hierarchical-tree — top-down structure.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Collection 与持久化目录

Root: Chroma Client
- PersistentClient(path="./chroma_db")

Branch 1: Collection "handbook"
- ids: chunk_id 列表
- embeddings: 向量
- documents: 原文 chunk 文本
- metadatas: doc_id, section, page...

Branch 2: Collection "faq"
- 另一知识库隔离

Leaf note: 一个目录可多个 Collection；换 Embedding 模型建议新建 Collection

Footer: Chroma 轻量向量库完全指南 · §5

All text Simplified Chinese.
