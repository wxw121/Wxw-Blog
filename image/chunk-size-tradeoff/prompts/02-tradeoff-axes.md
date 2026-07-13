---
layout: quadrant
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: four-axis / quadrant diagram showing trade-off dimensions.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Chunk Size 多维 Trade-off 轴

Four axes radiating from center「chunk_size」:
1. 检索精度 — 小块更准，大块更糊
2. Embedding 窗口 — 模型 max tokens 上限
3. Context 预算 — top-k × chunk_size ≤ 窗口
4. 存储/成本 — 小块 → 块数多 → embed 贵

Quadrant hints:
- 政策 FAQ → 偏小
- 长叙事报告 → 偏大 + overlap
- 技术 MD → 结构感知优先

Bottom: 调参要同时看四维，不能只盯一个数

Footer: Chunk Size 调参 trade-off · §5

All text Simplified Chinese.
