---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix or strategy cards grid.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 提示词超长时：先选策略再截断

Grid of strategy cards (6–8):
1. 降 top-k — 少塞几段
2. 按分数阈值 — 丢掉低分
3. 保高分段 — 重排后前 N
4. 单段截断 — 过长 chunk 砍尾/保句
5. 摘要压缩 — 改塞读书笔记
6. 多轮拆分 — 多次问再汇总
7. 尾部硬切 — 紧急防爆（标风险）
8. 历史裁剪 — 多轮只留近 N 轮

Highlight order arrow: 降噪/保高分 → 截断 → 摘要 → 硬切（最后）

Bottom: 任何截断都要记下丢掉的 chunk_id

Footer: Context Window 完全指南 · §8
