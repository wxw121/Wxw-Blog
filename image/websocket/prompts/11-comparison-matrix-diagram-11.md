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
┌─────────────┬──────────────┬──────────────┬──────────────┐
│             │  长轮询       │     SSE      │  WebSocket   │
│             │ (Long Poll)  │              │              │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ 方向        │ 双向（模拟）  │ 单向         │ 全双工        │
│             │              │ (服务器→客户端)│             │
│ 协议        │ HTTP         │ HTTP         │ WebSocket    │
│ 连接        │ 每次请求建立  │ 长连接        │ 长连接        │
│ 浏览器支持  │ 全部          │ 除 IE 外全部  │ 全部(IE10+)  │
│ 自动重连    │ 需自己写      │ ✅ 内置       │ 需自己写      │
│ 二进制数据  │ ✅           │ ❌ 仅文本     │ ✅ 文本+二进制 │
│ 自定义头    │ ✅           │ ❌ 浏览器限制  │ ✅ 握手时可带  │
│ HTTP/2 优化 │ ✅           │ ❌            │ 需额外处理    │
│ 代理友好    │ ✅           │ ⚠️ 需注意     │ ⚠️ 需升级支持  │
│ 实现复杂度  │ 中            │ 低            │ 中高          │
└─────────────┴──────────────┴──────────────┴──────────────┘