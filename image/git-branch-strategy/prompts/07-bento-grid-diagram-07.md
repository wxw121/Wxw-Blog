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
│                 PR 大小的黄金法则                          │
│                                                         │
│  理想: 200-400 行改动 (含测试)                           │
│  可以: 400-800 行                                       │
│  预警: 800+ 行——考虑拆分                                 │
│  灾难: 2000+ 行——审查者会跳过细节，bug 趁虚而入            │
│                                                         │
│  为什么小 PR 更好?                                       │
│  • 审查者可以在 20 分钟内完成（不是 2 小时）               │
│  • 差异小→容易发现逻辑错误                               │
│  • 合并快→冲突少                                         │
│  • 出问题→回滚影响范围小                                  │
│                                                         │
│  如何拆大 PR？                                           │
│  大 PR: 「重构订单系统」——改了 8000 行                    │
│  可以拆成:                                                │
│  PR1: 提取 OrderService 接口 (200 行)                   │
│  PR2: 实现新 OrderService (400 行，藏在功能开关后)        │
│  PR3: 迁移调用方——一个一个 controller 改 (5×200 行)     │
│  PR4: 删除旧代码 (300 行)                               │
│  PR5: 移除功能开关 (50 行)                              │
└─────────────────────────────────────────────────────────┘