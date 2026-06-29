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
│           HTTP/1.1 vs HTTP/2 下的 SSE                     │
│                                                         │
│  HTTP/1.1:                                              │
│  一个域名最多 6 个并发连接                                 │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐              │
│  │流 1│ │流 2│ │流 3│ │流 4│ │流 5│ │流 6│              │
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘              │
│  第 7 个 SSE 流 → 排队！                                 │
│                                                         │
│  HTTP/2:                                                │
│  一个连接上无限多个流                                     │
│  ┌──────────────────────────────────────────┐           │
│  │              单个 TCP 连接                 │           │
│  │  ┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐... │           │
│  │  │流 1││流 2││流 3││流 4││流 5││流 6│    │           │
│  │  └────┘└────┘└────┘└────┘└────┘└────┘    │           │
│  └──────────────────────────────────────────┘           │
│  第 100 个 SSE 流也毫无压力！                             │
│                                                         │
│  结论: 部署 SSE 时务必启用 HTTP/2 (Nginx 配 ssl http2)    │
└─────────────────────────────────────────────────────────┘