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
你要实现什么功能？
│
├── 服务器单向推送 (如通知、股票价格)
│   ├── 只需文本 → SSE (更简单，内置重连)
│   ├── 需要二进制 → WebSocket
│   └── 用不了 SSE (如 React Native) → WebSocket
│
├── 实时双向通信 (如聊天、游戏、协作)
│   └── → WebSocket
│
├── 兼容传统 HTTP 基础设施
│   ├── 代理/CDN 不支持 WebSocket → 长轮询
│   └── 没有特殊限制 → WebSocket
│
└── 只是偶尔的服务器推送 → 长轮询就够了，别过度设计