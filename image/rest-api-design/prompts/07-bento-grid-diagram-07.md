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
│              PUT vs PATCH 决策指南                        │
│                                                         │
│  用 PUT 当你:                                            │
│  • 客户端持有资源的完整表示                               │
│  • 要替换整个资源                                        │
│  • 需要幂等保证（网络重试安全）                            │
│                                                         │
│  用 PATCH 当你:                                          │
│  • 只需要更新一两个字段                                   │
│  • 资源很大，发送整个资源不现实                            │
│  • 并发更新友好（只修改指定字段，不会误覆盖他人的修改）     │
│                                                         │
│  现实建议：大多数更新场景用 PATCH 就够了                   │
│  不确定的时候——用 PATCH                                   │
└─────────────────────────────────────────────────────────┘