---
layout: flowchart
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: left-to-right pipeline flowchart.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: PyMuPDF 解析流水线

Flow:
1. import fitz → open PDF path
2. doc = fitz.open() → Document 对象
3. for page in doc: page.get_text()
4. 可选：page.get_images() / 元数据 doc.metadata
5. 输出：按页文本 + page 号 → chunk 元数据

Side: fitz 是 PyMuPDF 的 Python 绑定名

Bottom: 快、全功能；RAG 正文提取主力之一

Footer: PyMuPDF（fitz）完全指南 · §3

All text Simplified Chinese.
