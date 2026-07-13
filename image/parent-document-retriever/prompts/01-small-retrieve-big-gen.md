---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — two columns: wrong vs right retrieval granularity.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 小块检索、大块生成（Small Retrieve, Big Generate）

Left column (wrong): 大块 embedding
- 检索模糊，关键句淹没
- Top-1 常是整章废话

Right column (right): Parent-Document Retriever
- 子块 child：256 token，精检索
- 命中后取父块 parent：整节 1500 token
- LLM 上下文充足，答案可引用整段

Center arrow: 检索用 child_id → 返回 parent_text

Footer: Parent-Document Retriever 完全指南 · §3

All text Simplified Chinese.
