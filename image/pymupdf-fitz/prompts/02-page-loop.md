---
layout: flowchart
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: loop flowchart with page counter.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 按页循环：page 元数据怎么挂

Loop:
1. page_index = 0
2. page = doc[page_index]
3. text = page.get_text("text")
4. chunk = { text, metadata: { page: page_index+1, source: filename } }
5. page_index += 1 → 直到最后一页

Note box: 页码从 0 索引，展示给用户 +1

Bottom: 引用溯源「见 PDF 第 N 页」靠 page 字段

Footer: PyMuPDF（fitz）完全指南 · §6

All text Simplified Chinese.
