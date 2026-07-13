---
layout: tree-branching
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: tree-branching — decision tree flowing top to bottom, root at top center, branches to terminal leaf outcomes.

Style: hand-drawn-edu — macaron pastel nodes on warm cream (#F5F0E8), wavy connecting lines, stick figure at root, hand-lettered Chinese, coral red (#E8655A) for recommended path highlight, mint green for TanStack Query branch.

Title (top center): 选型决策树：该用哪个库

Tree structure (top to bottom):
ROOT: 你的框架是 Vue 3？
├─ 是 → 需要全局客户端状态？→ Pinia [Vue badge leaf]
└─ 否（React）→ 痛点主要是接口缓存/轮询？
    ├─ 是 → TanStack Query（+ 可选 Zustand 管 UI） [highlight in mint green]
    └─ 否 → 状态复杂且团队要严格 action 追溯？
        ├─ 是 → Redux Toolkit
        └─ 否 → 想要最少代码？→ Zustand
            └─ 状态很少、仅主题/用户？→ Context 也许够

Terminal leaves in rounded macaron cards with small icons: Vue logo, Query icon, Redux box, Zustand lightning, Context bubble.

Bottom note: React 常见组合：Query 管 documents + Zustand 管 UI

Footer: 前端状态管理完全指南 · §9

All text Simplified Chinese. Clear branch labels, legible hierarchy. Generous whitespace between levels.
