---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Table or matrix comparison layout
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌─────────────────────────────────────────────────────────┐
│                SSE 的本质 = HTTP 长连接 + 特殊格式         │
│                                                         │
│  客户端                             服务器               │
│    │                                  │                 │
│    │  GET /events HTTP/1.1            │                 │
│    │  Accept: text/event-stream       │ ← 告诉服务器     │
│    │  Cache-Control: no-cache         │   「我要 SSE」   │
│    ├─────────────────────────────────►│                 │
│    │                                  │                 │
│    │  HTTP/1.1 200 OK                 │                 │
│    │  Content-Type: text/event-stream │ ← 服务器确认    │
│    │  Cache-Control: no-cache         │                 │
│    │  Connection: keep-alive          │                 │
│    │◄─────────────────────────────────┤                 │
│    │                                  │                 │
│    │  data: {"price": 150.25}\n\n     │ ← 推送数据     │
│    │◄─────────────────────────────────┤                 │
│    │                                  │                 │
│    │  data: {"price": 150.30}\n\n     │ ← 继续推送     │
│    │◄─────────────────────────────────┤                 │
│    │                                  │                 │
│    │  data: {"price": 150.28}\n\n     │ ← 再推送       │
│    │◄─────────────────────────────────┤                 │
│    │                                  │                 │
│    │       ……持续推送……               │                 │
│    │                                  │                 │
│    │  [连接断开]                       │                 │
│    │──── 3 秒后自动重连 ──────────────►│ ← 浏览器自动！  │
│    │  Last-Event-ID: 42               │   带着上次 ID   │
│    │                                  │                 │
└─────────────────────────────────────────────────────────┘