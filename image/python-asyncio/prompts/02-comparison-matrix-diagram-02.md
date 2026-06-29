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
┌──────────────────────────────────────────────────────┐
│                     事件循环                          │
│                                                      │
│   待执行队列:                                         │
│   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐             │
│   │任务 A │  │任务 B │  │任务 C │  │任务 D │  ...       │
│   └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘             │
│      │         │         │         │                  │
│      ▼         ▼         ▼         ▼                  │
│   ┌────────────────────────────────────┐             │
│   │          事件循环调度器              │             │
│   │                                    │             │
│   │  "A，轮到你执行了"                   │             │
│   │  A: await asyncio.sleep(1)         │             │
│   │  调度器: "A 在等 sleep，暂停 A。B 你来" │             │
│   │  B: await socket.recv()            │             │
│   │  调度器: "B 在等网络，暂停 B。C 你来"   │             │
│   │  C: print('hello')  ← 执行完毕       │             │
│   │  调度器: "检查一下，A 的 sleep 到了没？"  │             │
│   │  "到了！A，回来！"                    │             │
│   └────────────────────────────────────┘             │
└──────────────────────────────────────────────────────┘