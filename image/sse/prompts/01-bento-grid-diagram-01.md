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
│                    杀鸡用牛刀                              │
│                                                         │
│  需求: 服务器→客户端 单向推送通知                          │
│                                                         │
│  小王选的方案: WebSocket                                  │
│  ┌──────────────────────────────────────────────┐       │
│  │ • 需要 ws → wss 升级 (WebSocket 握手)         │       │
│  │ • 需要自己实现心跳 (协议级 ping/pong)          │       │
│  │ • 需要自己实现重连 (指数退避)                  │       │
│  │ • 需要改 Nginx 配置 (Upgrade/Connection 头)   │       │
│  │ • 需要处理水平扩展 (Redis Pub/Sub 中转)        │       │
│  │ • 需要处理连接状态 (readyState)               │       │
│  └──────────────────────────────────────────────┘       │
│                                                         │
│  实际上只需要: SSE                                        │
│  ┌──────────────────────────────────────────────┐       │
│  │ • 标准 HTTP 协议——不需要升级                    │       │
│  │ • 内置自动重连——断了自己重连                    │       │
│  │ • 内置事件 ID——断点续传自动处理                │       │
│  │ • 普通 HTTP 代理/CDN 天然支持                 │       │
│  │ • 一行代码: const es = new EventSource(url)   │       │
│  └──────────────────────────────────────────────┘       │
│                                                         │
│  结果: 代码量少 80%，坑少 90%，效果一模一样               │
└─────────────────────────────────────────────────────────┘