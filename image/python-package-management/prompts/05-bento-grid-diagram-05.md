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
│          pip freeze > requirements.txt 的三宗罪          │
│                                                         │
│  罪一：直接依赖和间接依赖混在一起                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 你不知道哪个是你主动装的，哪个是顺便带进来的          │  │
│  │ 三个月后想升级 Django，该不该同时升级 sqlparse？      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  罪二：平台相关包被写死                                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Windows 上 freeze 会包含 pywin32==306              │  │
│  │ Linux 服务器上 pip install 直接报错                  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  罪三：依赖冲突时完全不可读                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │ pip 会自动「解决」冲突，但不会告诉你它做了什么         │  │
│  │ 项目 A 需要 foo>=2.0，项目 B 需要 foo<2.0            │  │
│  │ freeze 出来的结果是谁？不知道                         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘