---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression — ingest and query pipeline for Parent-Document Retriever.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Parent-Document 入库与查询流水线

Ingest (left to right):
1. 结构分块（63/64 篇）→ Parent chunks
2. 每 Parent 再切 Child（小 overlap）
3. Embed 仅 Child → 向量库
4. Parent 全文 → KV / metadata / 第二索引

Query (left to right):
1. 用户 question → embed
2. Top-k Child 命中
3. 去重 parent_chunk_id
4. 取 Parent 文本拼 context
5. LLM 生成 + 引用 parent section

Footer: Parent-Document Retriever 完全指南 · §8

All text Simplified Chinese.
