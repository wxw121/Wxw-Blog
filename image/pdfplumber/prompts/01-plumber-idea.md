---
layout: flowchart
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: flowchart with table highlight.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: pdfplumber：盯着线条与单元格

Flow:
1. pdfplumber.open(pdf)
2. 逐页 page.extract_text() — 可选
3. page.extract_tables() — 核心
4. 表格 → list[list[str]] → DataFrame / Markdown
5. 表格单独 chunk，带 page 元数据

Contrast small box: PyMuPDF 把表格当普通文本流

Bottom: 有线框的报表 PDF 优先试 pdfplumber

Footer: pdfplumber 完全指南 · §3

All text Simplified Chinese.
