---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — two columns: without L2 normalize vs with L2 normalize.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 为什么要 L2 归一化（Why L2 Normalize）

Left column (wrong): 未归一化向量
- 点积被「向量长度」抬高
- 长 chunk 可能压过更贴题的短句
- cosine 与 ip 排序不一致

Right column (right): L2 归一化后
- 只保留方向，长度统一为 1
- 余弦与点积排序可对齐
- 向量库 metric 配置更清晰

Center arrow: 入库前 normalize → 查询前 normalize

Footer: L2 归一化完全指南 · §3

All text Simplified Chinese.
