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
│                 WebSocket 握手过程                        │
│                                                         │
│  客户端                             服务器               │
│     │                                  │                 │
│     │  GET /chat HTTP/1.1              │                 │
│     │  Host: example.com               │                 │
│     │  Upgrade: websocket              │ ← 「我要升级」   │
│     │  Connection: Upgrade             │                 │
│     │  Sec-WebSocket-Key: dGhlIH...    │ ← 随机密钥      │
│     │  Sec-WebSocket-Version: 13       │                 │
│     ├─────────────────────────────────►│                 │
│     │                                  │                 │
│     │  HTTP/1.1 101 Switching Protocols│                 │
│     │  Upgrade: websocket              │ ← 「好，升级了」 │
│     │  Connection: Upgrade             │                 │
│     │  Sec-WebSocket-Accept: s3pPL...  │ ← 密钥的响应    │
│     │◄─────────────────────────────────┤                 │
│     │                                  │                 │
│     │   === 握手完成，连接升级 ===       │                 │
│     │                                  │                 │
│     │  双向 WebSocket 数据帧            │                 │
│     │◄═══════════════════════════════►│                 │
│     │      全双工通信开始               │                 │
└─────────────────────────────────────────────────────────┘