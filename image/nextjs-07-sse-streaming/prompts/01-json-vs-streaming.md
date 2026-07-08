---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu binary comparison.

Title: 一次性 JSON vs 流式 SSE

LEFT 第三篇 fetchJSON:
GET /api/users
await res.json() 一次
Server Component 常见
关页即结束

RIGHT 本篇聊天流式:
POST /api/chat/stream
res.body.getReader() 循环
必须 Client useState
AbortController 可停止

Center note: 流式优化首字时间TTFT · 不是算更快
Bottom: 列表用Server fetch · 聊天用Client读流
Footer: Next.js 学习系列（七)

Simplified Chinese, macaron pastels, cream paper.