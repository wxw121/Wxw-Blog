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
│                  包管理三要素                               │
│                                                          │
│  1. 声明文件 (requirements.in / pyproject.toml)            │
│     → 「我需要这些包，版本大概在这个范围」                   │
│     → 人类编写、人类维护                                   │
│                                                          │
│  2. 锁文件 (requirements.txt / poetry.lock / uv.lock)      │
│     → 「这些是确切安装的版本，包括所有间接依赖」              │
│     → 工具生成、提交到 Git                                 │
│                                                          │
│  3. 虚拟环境 (.venv/)                                      │
│     → 「这些是实际安装在你电脑上的文件」                     │
│     → 从锁文件安装、可随时重建                              │
│                                                          │
│  铁律：                                                   │
│  • 声明文件是源，锁文件是生成物——提交生成物                  │
│  • 生产环境永远用锁文件安装，不用声明文件                    │
│  • 依赖变了，锁文件也要变——在代码审查中关注锁文件的 diff     │
└──────────────────────────────────────────────────────────┘