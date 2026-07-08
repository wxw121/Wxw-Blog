---
layout: tree-branching
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: tree-branching — security decision tree top to bottom.

Style: hand-drawn-edu — macaron pastel nodes on warm cream (#F5F0E8), wavy lines, stick figure, hand-lettered Simplified Chinese, mint green for safe path, coral for raw HTML path.

Title (top center): Markdown 渲染安全决策树

Tree:
ROOT: 要渲染助手 Markdown？
├─ 否 → 纯文本，流式/历史皆然
└─ 是 → 能用 react-markdown 默认？
    ├─ 是 → remark-gfm + 链接/图片自定义 + 流式结束后再渲染 [mint highlight ✅]
    └─ 必须支持内联 HTML？
        ├─ 是 → rehype-raw + rehype-sanitize + CSP [coral warning]
        └─ 否 → 不要加 raw [mint]

Bottom takeaway: 模型输出不可信 · 能不 raw 就不 raw
Footer: Markdown 渲染与安全完全指南 · §13

Legible Chinese hierarchy.
