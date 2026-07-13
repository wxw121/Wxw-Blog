---
layout: decision-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: decision-tree with 4 branches.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 何时优先 PyMuPDF？

Root: 你要从 PDF 拿什么？

Branch A — 纯文本按页 → PyMuPDF ✓
Branch B — 表格结构 → pdfplumber / Camelot
Branch C — 只要合并全文、极简 → pypdf 可试
Branch D — 扫描件图片 → OCR（Tesseract / 云 OCR）

Bottom: 没有银弹；正文 PyMuPDF，表格另选

Footer: PyMuPDF（fitz）完全指南 · §8

All text Simplified Chinese.
