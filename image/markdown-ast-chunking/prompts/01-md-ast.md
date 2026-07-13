---
layout: hierarchical-tree
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hierarchical-tree — Markdown source string transforms into AST tree.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Markdown 解析树（AST）：从字符串到节点

Left side: raw MD snippet with # ## ``` fenced code
Right side: AST tree nodes:
- document
  - heading (level=1)
  - heading (level=2)
  - paragraph
  - block_code (info=bash)
  - list (ordered)
  - heading (level=2)

Annotations:
- 解析 ≠ 删 # 的纯文本
- 块级节点：heading / paragraph / block_code / list
- 分块器遍历顶层 block，不是字符下标

Arrow label: mistune / markdown-it-py → AST

Footer: Markdown AST 分块完全指南 · §4

All text Simplified Chinese.
