---
layout: hub-spoke
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Central hub with connected spokes/nodes
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌─────────────────────────────────────────────┐
│            协程函数的生命周期                  │
│                                             │
│  async def func():  ← 定义协程函数            │
│       │                                     │
│       ▼                                     │
│  func()              ← 调用=创建协程对象（不执行）│
│       │                                     │
│       ▼                                     │
│  await coro          ← 等待协程执行           │
│       │                                     │
│       ▼                                     │
│  asyncio.run(coro)   ← 顶层入口，启动事件循环   │
│                                             │
│  ⚠️ 同一个 asyncio.run() 调用里只运行一个      │
│     事件循环。不要嵌套 asyncio.run()！         │
└─────────────────────────────────────────────┘