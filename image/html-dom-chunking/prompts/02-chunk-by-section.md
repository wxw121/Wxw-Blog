---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression — main/article DOM sliced by h2/section boundaries.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 去噪后按 section / h2 切分

Flow:
1. 39 篇正文抽取 → 干净 article 子树
2. 找 h2 或 section 边界
3. 每块保留 table / pre 完整
4. 写 metadata: url, section, heading_text

Show three chunk boxes from one help page:
- Chunk A: h2「快速开始」+ p + ul
- Chunk B: h2「配置项」+ table（整表）
- Chunk C: h2「FAQ」+ dl

Warning: 未去噪就切 → 每块都带 nav 文字

Footer: HTML DOM 分块完全指南 · §6

All text Simplified Chinese.
