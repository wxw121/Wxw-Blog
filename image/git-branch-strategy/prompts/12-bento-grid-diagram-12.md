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
│                    分支策略选择指南                         │
│                                                          │
│  你的团队是什么样的？                                      │
│                                                          │
│  • 3-10 人的 Web 创业团队，每天部署                        │
│    → GitHub Flow + Trunk-Based                           │
│    → 简单、快、合并就部署                                  │
│                                                          │
│  • 10-50 人的产品团队，每两周发布一个版本                   │
│    → Git Flow (简化版)                                    │
│    → 有 release 分支做发布前缓冲                           │
│                                                          │
│  • 要同时维护 v3.x (生产) 和 v4.x (开发) 两个大版本        │
│    → Git Flow                                             │
│    → 多版本支持是这个模型的核心优势                         │
│                                                          │
│  • 2-3 人的小团队，快速迭代                                │
│    → GitHub Flow + Squash Merge                          │
│    → 别搞太复杂，分支策略不应该比代码还重                   │
│                                                          │
│  底层规则（无论什么策略都通用）:                            │
│  1. main 永远可部署                                       │
│  2. 所有改动走 PR                                         │
│  3. 合并前 CI 全绿 + 有人审查                              │
│  4. 小步提交、频繁合并、合并后删分支                        │
│  5. 写好 commit message                                  │
└──────────────────────────────────────────────────────────┘