---
layout: hierarchical-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hierarchical-tree — one parent chunk splits into multiple child chunks.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 父子块关系（Parent-Child Chunks）

Tree:
Parent P1: H2「安装」整节（1200 token）
├── Child c1: 安装 · 段落 1（200 token）
├── Child c2: 安装 · 代码块（180 token）
└── Child c3: 安装 · 列表步骤（220 token）

Metadata on each child:
- parent_chunk_id: P1
- parent_text: （冗余或 KV 查表）
- section: 快速开始 › 安装

Note: 向量库只索引 child；parent 存 doc store 或 metadata

Footer: Parent-Document Retriever 完全指南 · §5

All text Simplified Chinese.
