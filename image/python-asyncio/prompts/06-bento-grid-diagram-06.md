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
┌─────────────────────────────────────────────────────────────┐
│                    异步编程四大核心                            │
│                                                             │
│  1. async def     → 定义协程函数                              │
│  2. await         → 等待一个协程/可等待对象                    │
│  3. asyncio.run() → 启动事件循环，运行顶层协程                  │
│  4. gather/task   → 并发执行多个协程                           │
│                                                             │
│  记住：                                                      │
│  • 协程 ≠ 并行   （asyncio 是单线程的）                        │
│  • 协程 = 协作式  （在 await 处主动交出控制权）                 │
│  • 异步的优势     （把 I/O 等待时间「重叠」起来）               │
│  • 异步的代价     （需要 async/await 语法改造，不是免费午餐）    │
└─────────────────────────────────────────────────────────────┘