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
                生产者-消费者 流水线

                   ┌──────────┐
                   │ Producer │  发现 URL
                   └────┬─────┘
                        │
                  queue.put(url)
                        │
                        ▼
               ┌─────────────────┐
               │   asyncio.Queue  │
               │   (maxsize=10)   │  ← 缓冲区
               └───┬───┬───┬─────┘
                   │   │   │
          queue.get()  │   │
               │       │   │
        ┌──────┘  ┌────┘   └──────┐
        ▼         ▼               ▼
   ┌─────────┐┌─────────┐   ┌─────────┐
   │Worker 1 ││Worker 2 │...│Worker 5 │  消费者
   └─────────┘└─────────┘   └─────────┘

   队列大小限制 = 背压机制：生产者太快时自动减速