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
┌──────────────────────────────────────────────────────────┐
│                  指数退避重连策略                           │
│                                                          │
│  第 1 次断开: 等 1 秒后重连                                │
│  第 2 次断开: 等 2 秒后重连                                │
│  第 3 次断开: 等 4 秒后重连                                │
│  第 4 次断开: 等 8 秒后重连                                │
│  第 5 次断开: 等 16 秒后重连                               │
│  ...                                                     │
│  达到最大延迟 (如 30 秒) 后不再增加                         │
│  达到最大次数 (如 10 次) 后放弃，通知用户                   │
│                                                          │
│  为什么用指数退避而不是固定间隔？                            │
│  → 如果服务器正在重启，立即重连只会增加压力，延长恢复时间     │
│  → 逐步增加等待时间，给服务器喘息空间                       │
└──────────────────────────────────────────────────────────┘