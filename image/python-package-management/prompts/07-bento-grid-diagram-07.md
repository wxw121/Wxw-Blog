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
│                      锁文件的本质                          │
│                                                          │
│  声明文件 (pyproject.toml / requirements.in)               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ "我要 Django 4.x 版本、requests 2.x 版本……"          │  │
│  │ 这是「意图声明」——告诉解析器你想要什么                  │  │
│  └────────────────────────────────────────────────────┘  │
│                        │                                 │
│                   依赖解析器                               │
│                        │                                 │
│                        ▼                                 │
│  锁文件 (requirements.txt / poetry.lock / uv.lock)        │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Django==4.2.11                                      │  │
│  │   asgiref==3.7.2                                    │  │
│  │     typing-extensions==4.10.0                       │  │
│  │   sqlparse==0.4.4                                   │  │
│  │ requests==2.31.0                                    │  │
│  │   urllib3==2.2.1                                    │  │
│  │   certifi==2024.2.2                                 │  │
│  │   idna==3.6                                         │  │
│  │   charset-normalizer==3.3.2                         │  │
│  │                                                     │  │
│  │ 这是「事实快照」——精确到每个包的每个依赖               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  关键区别：                                               │
│  • 声明文件 = 你的愿望    → 提交到 Git（人类维护）         │
│  • 锁文件   = 现实快照    → 提交到 Git（工具生成）         │
└──────────────────────────────────────────────────────────┘