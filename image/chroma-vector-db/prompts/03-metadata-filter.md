---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — two columns: without filter vs with filter.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 元数据过滤：先筛再搜

Left column (无过滤):
- 全库 ANN
- 可能命中无权限文档
- 跨部门噪音

Right column (有过滤):
- where: {"doc_id": "handbook-v3"}
- 或 acl 字段
- 只在子集里算近邻

Center: 与 FAISS 对比
- FAISS 只有 id，过滤要自己实现
- Chroma where 内置

Footer: Chroma 轻量向量库完全指南 · §7

All text Simplified Chinese.
