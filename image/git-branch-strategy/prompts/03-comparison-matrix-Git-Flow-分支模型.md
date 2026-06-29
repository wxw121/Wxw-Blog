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
                        Git Flow 分支模型

    master   ○──────○──────────────────────────────○──────▶
             │      │                              │
    develop  ├──────○──────○──────○──────○──────○──┤
             │\     │\     │\     │\     │\     │  |
    feature/ │ \    │ \    │ \    │ \    │ \    │  |
             │  ○───┤  ○───┤  ○───┤  ○───┤  ○───┤  |
             │      │      │      │      │      │  |
    release/ │      ├──────○──────┤      │      │  |
             │      │      │\     │      │      │  |
    hotfix/  ├──────┤      │ \────┤──────○──────┤  |
             │      │      │      │      │\     │  |

    ○ = commit / tag
    ── = 分支线

    五类分支:
    main/master —— 生产代码（只接受 release 和 hotfix 的合并）
    develop     —— 开发主线（feature 合并到这里）
    feature/*   —— 新功能（从 develop 分出，合并回 develop）
    release/*   —— 发布准备（从 develop 分出，合并到 main + develop）
    hotfix/*    —— 紧急修复（从 main 分出，合并到 main + develop）