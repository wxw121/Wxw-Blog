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
│                    轮询的隐藏代价                          │
│                                                         │
│  500 个用户 × 每 2 秒一次 × 持续 8 小时                    │
│  = 500 × 30/分钟 × 60 × 8                               │
│  = 7,200,000 次 HTTP 请求                                 │
│                                                         │
│  其中真正有数据的请求: 约 12,000 次                         │
│  空轮询浪费: 7,188,000 次 (99.8%)                         │
│                                                         │
│  每次请求的开销:                                          │
│  ┌─────────────────────────────────────┐                │
│  │ TCP 三次握手        ~1.5 RTT        │                │
│  │ TLS 握手            ~2 RTT          │ × 720 万次      │
│  │ HTTP 请求头          ~500 bytes      │                │
│  │ HTTP 响应头          ~300 bytes      │                │
│  │ 数据库查询            ~5ms           │                │
│  └─────────────────────────────────────┘                │
│                                                         │
│  浪费的带宽: 720万 × 800 bytes ≈ 5.5 GB                  │
│  浪费的数据库查询: 719万 × 5ms ≈ 10 小时                  │
│  用户新消息延迟: 最长 2 秒                                │
└─────────────────────────────────────────────────────────┘