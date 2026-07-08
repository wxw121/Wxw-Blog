---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: binary-comparison — left Transport Layer, right Display Layer, with connecting pipeline arrow from left output to right input.

Style: hand-drawn-edu — macaron pastel cards on warm cream (#F5F0E8), wavy lines, stick figures, hand-lettered Simplified Chinese, coral red (#E8655A) accents.

Title (top center): 两层问题：传输流式 vs 界面流式

Left column - 传输层:
Subtitle: 水管里的水一股一股来
Flow (vertical): 服务器生成 → HTTP长连接/SSE → readSSEStream / getReader
Rows:
- 决定什么：多快收到第一块数据
- 典型 API：POST /chat/stream、SSE

Right column - 展示层:
Subtitle: 杯子接到一点倒一点给用户看
Flow (vertical): 更新 messages → ChatBubble 重绘 → 用户看到字变长
Rows:
- 决定什么：多快画到屏幕上
- 典型 API：setState、Vue ref、节流

Center: wavy arrow from R (reader) to 更新 state

Bottom takeaway (bold): R 之后才是本篇重点
Footer: 流式 UI 渲染完全指南 · §2

Legible Chinese, generous whitespace.
