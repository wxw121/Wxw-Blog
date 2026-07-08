---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: linear-progression — horizontal 6-node pipeline left to right with wavy arrows.

Style: hand-drawn-edu — macaron pastel cards on warm cream (#F5F0E8), wavy arrows, stick figure developer, hand-lettered Simplified Chinese, coral red (#E8655A) for security callouts.

Title (top center): 渲染管线：从字符串到 DOM

6 nodes connected left to right:
1. Markdown 字符串
2. remark 解析
3. mdast 语法树
4. mdast → hast
5. rehype 插件
6. React 组件 / DOM

Small labels below nodes:
- remark：Markdown 专家
- rehype：HTML 专家 · 消毒/删 script
- react-markdown：输出组件树，非 innerHTML

Bottom takeaway (bold): 安全策略可挂在解析、AST、消毒、CSP 多层
Footer: Markdown 渲染与安全完全指南 · §3

Legible Chinese, generous whitespace.
