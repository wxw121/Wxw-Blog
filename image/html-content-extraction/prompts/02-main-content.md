---
layout: funnel
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: funnel / pipeline top-down.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 正文抽取流水线

Funnel stages:
1. 获取 HTML — HTTP + 编码检测（UTF-8 / GBK）
2. 解析 DOM — BeautifulSoup / lxml
3. 去噪 — 删 script/style/nav/footer；或启发式打分
4. 主区域 — article, main, .post-content 或 Readability 类算法
5. 输出 — 纯文本 / 简化 Markdown + title/url 元数据

Side branch: 动态站（JS 渲染）需 Playwright 先拿 HTML

Bottom: 最小可用 = BS4 + 语义标签；复杂站用 trafilatura/readability

Footer: HTML 正文抽取完全指南 · §6

All text Simplified Chinese.
