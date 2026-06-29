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
                ┌──────────────┐
                │  可等待对象    │
                │  (Awaitable) │
                └──────┬───────┘
           ┌───────────┼───────────┐
           │           │           │
           ▼           ▼           ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐
     │  协程    │ │  Task   │ │  Future │
     │coroutine│ │ (任务)   │ │ (未来值) │
     └─────────┘ └─────────┘ └─────────┘
          │           │           │
          │           │           │
    你写的 async   协程的包装   低级原语
    def 函数的      可并发调度    一般不同
    返回值                        await