---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression left-to-right, 4 steps.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 表格（Table）挑战：从格子到行列

Steps:
1. 视觉表格 — 有线框、合并单元格、跨页续表
2. 坐标聚类 — 按 x/y 把字符归到格子（pdfplumber 思路）
3. 行列还原 — header 行、数据行、空单元格
4. 输出形态 — CSV / Markdown 表 / 单独 chunk 进索引

Failure callouts between steps:
- 无线框表只靠空白对齐
- 扫描件需 OCR + 版面模型
- 合并格导致列错位

Bottom decision fork:
- 简单有线表 → pdfplumber
- 复杂版面 / 扫描 → 布局模型或专用管线

Footer: PDF 表格与版面挑战完全指南 · §6

All text Simplified Chinese.
