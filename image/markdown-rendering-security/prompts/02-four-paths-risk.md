---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: comparison-matrix — 4 rows comparing rendering paths, columns: 路径 / XSS风险 / 排版能力 / RAG推荐.

Style: hand-drawn-edu — macaron pastel table cells on warm cream (#F5F0E8), hand-lettered Simplified Chinese, coral red for high risk and ❌, mint green for ✅.

Title (top center): 四种渲染路径与风险对照

Table rows (verbatim):
1. 纯文本 | XSS风险: 很低 | 排版: 低 | 推荐: 流式阶段
2. innerHTML | XSS风险: 很高 | 排版: 高 | 推荐: ❌
3. react-markdown 默认 | XSS风险: 低 | 排版: 中高 | 推荐: ✅
4. raw + sanitize | XSS风险: 中 | 排版: 高 | 推荐: ⚠️ 有需求再做

Warning box (coral): 禁止对不可信内容使用 innerHTML / dangerouslySetInnerHTML

Bottom: 排版能力越大，攻击面往往越大
Footer: Markdown 渲染与安全完全指南 · §7

Legible Chinese matrix layout.
