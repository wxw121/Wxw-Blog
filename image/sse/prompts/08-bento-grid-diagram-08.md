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
┌──────────────────────────────────────────────────────────┐
│                  SSE 五大核心认知                           │
│                                                          │
│  1. SSE 就是 HTTP——不需要协议升级                          │
│     Content-Type: text/event-stream，剩下的就是普通 HTTP   │
│                                                          │
│  2. 自动重连是内置的——不用写重连逻辑                        │
│     EventSource 断开后自动重连，3 秒默认间隔                │
│                                                          │
│  3. 断点续传是内置的——Last-Event-ID 是天然设计              │
│     服务端读取这个头，从断点开始补发                        │
│                                                          │
│  4. 用 event 字段区分消息类型——像事件总线一样                │
│     不同的事件名 → 不同的 addEventListener                  │
│                                                          │
│  5. SSE + HTTP/2 是王炸组合                                │
│     一个连接上无限多个 SSE 流，没有 6 连接上限               │
└──────────────────────────────────────────────────────────┘