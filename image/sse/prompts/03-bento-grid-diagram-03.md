---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Multi-panel bento grid overview
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌─────────────────────────────────────────────────────────┐
│              SSE 的六大自然优势（WebSocket 羡慕不来）       │
│                                                         │
│  1. 就是 HTTP——不需要协议升级                             │
│     用普通的 HTTP/1.1 或 HTTP/2 即可                      │
│     Nginx/CDN/代理天然支持，零配置                         │
│                                                         │
│  2. 自动重连——浏览器原生支持                               │
│     连接断开后浏览器自动重连，默认 3 秒间隔                 │
│     不用写一行重连代码                                    │
│                                                         │
│  3. 断点续传——EventSource 内置 Last-Event-ID              │
│     重连时自动带上最后收到的事件 ID                        │
│     服务器可以从断点继续推送                               │
│                                                         │
│  4. HTTP/2 天然支持多路复用                               │
│     一个连接上可以跑多个 SSE 流                            │
│     WebSocket 反而没法享受 HTTP/2 的好处                   │
│                                                         │
│  5. 调试友好——curl 就能测                                 │
│     curl -N http://localhost:8000/events                 │
│     不需要 wscat 之类的专用工具                           │
│                                                         │
│  6. 安全模型简单                                         │
│     和普通 HTTP 请求一样处理 CORS、认证                    │
│     不需要考虑 WebSocket 特有的跨站劫持攻击                │
└─────────────────────────────────────────────────────────┘