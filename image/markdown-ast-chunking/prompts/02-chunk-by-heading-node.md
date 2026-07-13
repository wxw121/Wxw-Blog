---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression — AST nodes sliced into chunks at heading boundaries.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 按标题节点切分：Heading 触发新 Chunk

Show AST node stream left to right:
heading H2「安装」→ paragraph → block_code（整段保留）→ list → heading H2「配置」→ ...

Chunk boxes colored:
- Chunk 1: H2 安装 + 下属 nodes（代码块完整）
- Chunk 2: H2 配置 + 下属 nodes

Rules callouts:
- 遇到 level=2 heading → flush 当前 chunk
- block_code 原子：永不拦腰切
- 超长 H2 内 → 按 H3 或段落二次切

Metadata tags: section, heading_level, parent_h1

Footer: Markdown AST 分块完全指南 · §6

All text Simplified Chinese.
