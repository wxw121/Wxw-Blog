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
EventSource 的两个已知限制:

限制 1: 不支持自定义请求头
┌────────────────────────────────────────────────────┐
│ fetch() 和 WebSocket 都支持自定义 header，           │
│ 但 EventSource 不支持——它只能发 GET 请求。            │
│                                                    │
│ 解决方案:                                           │
│ 1. 用查询参数传 token: /events?token=xxx            │
│ 2. 用 cookie: 同源的 EventSource 会自动带 cookie     │
│ 3. 用第三方库封装 (如 fetch-event-source)           │
│ 4. 手写 fetch + ReadableStream 模拟 SSE             │
└────────────────────────────────────────────────────┘

限制 2: 只能发 GET 请求
┌────────────────────────────────────────────────────┐
│ 如果需要用 POST 传递复杂的订阅条件:                   │
│                                                    │
│ 方案一: 先 POST 创建订阅 → 返回 channel_id           │
│         再用 GET /events?channel=xxx 连接 SSE       │
│                                                    │
│ 方案二: 用 @microsoft/fetch-event-source 这个库      │
│         它用 fetch 实现了 EventSource 的功能，        │
│         同时支持 POST、自定义 header                 │
└────────────────────────────────────────────────────┘