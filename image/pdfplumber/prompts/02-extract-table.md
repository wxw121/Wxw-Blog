---
layout: flowchart
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: step flowchart with code hint boxes.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: extract_tables 最小路径

Steps:
1. with pdfplumber.open(path) as pdf
2. page = pdf.pages[i]
3. tables = page.extract_tables()
4. for table in tables: 首行当 header
5. 清洗 None → ""，输出 CSV 或 JSON 行

Warning box: 合并单元格、无线表会失败 → 降级纯文本

Bottom: 一张表一个 chunk，别和正文糊在一起

Footer: pdfplumber 完全指南 · §5

All text Simplified Chinese.
