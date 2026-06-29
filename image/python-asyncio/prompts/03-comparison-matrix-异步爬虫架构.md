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
                   异步爬虫架构

   URL 列表
      │
      ▼
┌─────────────┐
│  Semaphore    │ ← 最多 10 个并发
│  (许可证=10)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           aiohttp.ClientSession          │
│                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐           │
│  │请求 1 │ │请求 2 │ │请求 3 │ ... ×10    │
│  └──┬───┘ └──┬───┘ └──┬───┘           │
│     │        │        │                  │
│     │  [等待服务器……]  │                  │
│     │        │        │                  │
│     ▼        ▼        ▼                  │
│    完成      完成      完成  → 释放许可证   │
│                                          │
│  释放的许可证 → 启动新请求                  │
└─────────────────────────────────────────┘