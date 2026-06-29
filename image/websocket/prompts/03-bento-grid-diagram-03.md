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
│                  轮询 vs WebSocket                        │
│                                                         │
│  轮询（短连接）:                                          │
│  客户端: [有没有?][有没有?][有没有?][有没有?][有没有?]...   │
│  服务器: [没有] [没有] [没有] [有!]  [没有] ...           │
│          ↑ 每个 [有没有?] 都是一次完整的 HTTP 请求         │
│                                                         │
│  WebSocket（长连接）:                                     │
│  客户端: [我来了，有事告诉我]                              │
│  服务器:            [有新消息!]   [又有新消息!]  [还有!]   │
│          ↑ 一次连接，持续通信，服务器主动推送              │
└─────────────────────────────────────────────────────────┘