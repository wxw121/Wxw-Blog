---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — left "人眼看到的版面" vs right "朴素提取的字符串".
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 版面（Layout）混乱：字有了，顺序没了

Left panel — 双栏 PDF 人眼阅读:
- 左栏正文 → 右栏续接
- 页眉页脚小字在边缘
- 表格格子对齐
- 火柴人按 Z 字或栏序阅读

Right panel — page.get_text() 朴素提取:
- 字符串按绘制顺序拼接
- 左栏末行与右栏首行交错
- 页眉重复插入正文中间
- 表格数字连成一行无分隔

Center callout: 提取到字 ≠ 结构对

Bottom: RAG 坏案例：检索命中乱序片段，模型胡编表格关系

Footer: PDF 表格与版面挑战完全指南 · §4

All text Simplified Chinese.
