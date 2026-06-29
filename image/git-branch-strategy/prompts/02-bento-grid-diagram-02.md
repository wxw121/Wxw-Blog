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
│              为什么不直接 push master                     │
│                                                         │
│  1. master = 信任的锚                                    │
│     master 上的代码应该是「随时可以部署到生产环境」的状态   │
│     任何 push 到 master 的提交都应该是经过测试和审查的     │
│                                                         │
│  2. 隔离实验                                             │
│     在分支上失败的成本 = 0（删掉分支就行）                 │
│     在 master 上失败的成本 = 无限大（影响所有人）          │
│                                                         │
│  3. 并发开发                                             │
│     如果三个人同时在 master 上改同一个文件 → 冲突地狱       │
│     三个分支分别开发 → 各管各的，互不干扰                  │
│                                                         │
│  4. 代码审查                                             │
│     分支 + PR = 天然的审查机制                            │
│     「改了什么」一目了然——diff 只在分支和 master 之间     │
│     直接 push master → 改了什么混在所有人的提交里          │
└─────────────────────────────────────────────────────────┘