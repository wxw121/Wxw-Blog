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
WebSocket 实例有四个 readyState:

0 — CONNECTING   正在握手
1 — OPEN         已连接，可以收发数据
2 — CLOSING      正在关闭
3 — CLOSED       已关闭

     ┌──────────┐
     │ CONNECTING│
     └────┬─────┘
          │ 握手成功
          ▼
     ┌──────────┐
     │   OPEN   │ ← 可以收发消息
     └────┬─────┘
          │ close()
          ▼
     ┌──────────┐
     │ CLOSING  │
     └────┬─────┘
          │ 关闭帧确认
          ▼
     ┌──────────┐
     │  CLOSED  │
     └──────────┘