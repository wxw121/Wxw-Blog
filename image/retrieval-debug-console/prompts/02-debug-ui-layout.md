---
layout: hierarchical-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hierarchical-tree — top-down UI wireframe.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: /debug/retrieve 页面结构

Root: 检索调试台页面

Branch 1: DebugRetrieveForm
- query 输入框
- bm25_k / dense_k / recall_k
- 身份模拟下拉

Branch 2: RetrieveHitTable
- 列：rank | score↑ | 文档 | 摘录 | chunk_id
- 可选 dense_score / sparse_score

Branch 3: HitDetailDrawer
- 全文 + metadata JSON

Footer: 检索调试台完全指南 · §7

All text Simplified Chinese.
