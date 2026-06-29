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
│                 三种合并策略                              │
│                                                         │
│  初始状态: main 有两个提交, feature 分支从 main 分出      │
│            并提交了 3 个 commit                          │
│                                                         │
│  main:    A───B                                         │
│                 \                                       │
│  feature:        C───D───E                              │
│                                                         │
│  ═══════════════════════════════════════                 │
│                                                         │
│  策略 1: Merge Commit (--no-ff)                          │
│                                                         │
│  main:    A───B───────────M   ← M 是合并提交             │
│                 \         /                             │
│  feature:        C───D───E                              │
│                                                         │
│  结果: 保留了完整的「分支」历史                           │
│  git log: A → B → C → D → E → M                        │
│                                                         │
│  ✅ 优点: 完整历史、不会丢失任何信息                       │
│  ❌ 缺点: 日志复杂、合并提交多了后 git log 像蜘蛛网        │
│  适合: 多人协作的 feature 分支、需要完整审计的项目         │
│                                                         │
│  ═══════════════════════════════════════                 │
│                                                         │
│  策略 2: Squash Merge                                   │
│                                                         │
│  main:    A───B───────S   ← S 包含了 C+D+E 的改动        │
│                 \                                        │
│  feature:        C───D───E  (分支被删除)                 │
│                                                         │
│  结果: 分支上所有提交被「压缩」为一个干净的提交            │
│  git log: A → B → S                                    │
│                                                         │
│  ✅ 优点: 主干历史干净、一条线、每个 commit 都是完整功能   │
│  ❌ 缺点: 丢失了细分提交历史、无法知道功能是怎么演变的       │
│  适合: 个人 feature 分支、PR 内提交过多或随意的场景         │
│                                                         │
│  ═══════════════════════════════════════                 │
│                                                         │
│  策略 3: Rebase Merge                                   │
│                                                         │
│  main:    A───B───C'──D'──E'   ← commit 被「重放」到 B 后 │
│                                                         │
│  结果: 分支的提交被放到 main 最新提交之后                 │
│  git log: A → B → C'→ D'→ E' (一条线，无合并提交)       │
│                                                         │
│  ✅ 优点: 历史完全线性、无合并提交                        │
│  ❌ 缺点: C'/D'/E' 的 hash 变了、需要 force push          │
│  适合: 追求线性历史的团队、PR 合并前先 rebase              │
└─────────────────────────────────────────────────────────┘