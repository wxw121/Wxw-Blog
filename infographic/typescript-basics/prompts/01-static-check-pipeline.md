---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: linear-progression — horizontal left-to-right pipeline with one error branch.

Style: hand-drawn-edu — macaron pastel cards on warm cream paper (#F5F0E8), wavy lines, stick figures, hand-lettered Chinese text, coral red (#E8655A) accents for warnings.

Title (top center, bold hand-drawn): 静态类型与动态类型：两套检查各管什么时候

Main flow (5 nodes, left to right, connected by wavy arrows):
1. .ts 源码
2. TS 编译器 / IDE
3. 类型是否一致? (diamond decision node)
4. 生成 .js
5. 浏览器 / Node 运行

Error branch from node 3 (downward, coral red): 红线 / 编译失败

Warning at node 5 (coral callout): 运行时仍可能因数据不符而崩

Below the pipeline, three macaron cards in a row:
- 编辑时：IDE 标红、补全
- 构建时：tsc / Vite / Webpack
- 运行时：没有 TS 类型警察

Bottom takeaway (bold): 类型只活在源码与检查阶段；运行的是 JS

Footer: TypeScript 基础完全指南 · §3

All text in Simplified Chinese. Legible, not overcrowded. Generous whitespace. One stick figure observing the pipeline.
