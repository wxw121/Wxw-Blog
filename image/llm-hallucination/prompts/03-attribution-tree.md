---
layout: tree-branching
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: 看见胡编：怎么归因

Root: 答案里有一句可疑事实

Branch A: 资料里根本没有 → 生成侧胡编 / 拒答失效
Branch B: 资料有但答错/拼错 → 提示词弱、未要求引用、或读错 chunk
Branch C: 检索就没召回对的 → 分块/向量/查询问题（不是「再把温度调低」能根治）

Bottom: RAG bad case：解析→切块→检索→生成 分段查

Footer: 幻觉成因完全指南 · §6
