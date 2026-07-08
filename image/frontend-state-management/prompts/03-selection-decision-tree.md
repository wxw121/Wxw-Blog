---
layout: tree-branching
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: tree-branching — decision tree top to bottom, root at top, branches to 5 terminal outcomes.

Style: hand-drawn-edu — macaron pastel nodes on warm cream (#F5F0E8), wavy connecting lines, stick figure at root, hand-lettered Simplified Chinese, coral red for recommended paths.

Title (top center): Zustand / Redux / Pinia 选型决策树

Tree structure (top to bottom):
ROOT: 你的框架是 Vue 3？
├─ 是 → 需要全局客户端状态？→ Pinia [mint green highlight]
└─ 否（React）→ 痛点主要是接口缓存/轮询？
    ├─ 是 → TanStack Query（+ 可选 Zustand 管 UI） [blue highlight]
    └─ 否 → 状态复杂且团队要严格 action 追溯？
        ├─ 是 → Redux Toolkit [coral highlight]
        └─ 否 → 想要最少代码？→ Zustand [peach highlight]
            └─ 状态很少、仅主题/用户？→ Context 也许够

Terminal leaves in rounded macaron cards with small icons (Vue logo style, React, database, shield, feather).

Bottom takeaway: 先分类，再选库
Footer: 前端状态管理完全指南 · §9

All Simplified Chinese. Clear hierarchy, legible branch labels.
