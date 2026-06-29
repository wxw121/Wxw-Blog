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
┌──────────────────────────────────────────────────────────┐
│                pip-tools 工作流                            │
│                                                          │
│   ① 手写 requirements.in                                  │
│   ┌────────────────────────────┐                         │
│   │ django                     │  ← 只写包名，版本可选     │
│   │ requests                   │                         │
│   └────────┬───────────────────┘                         │
│            │                                             │
│   ② pip-compile requirements.in                           │
│            │                                             │
│            ▼                                             │
│   ┌────────────────────────────┐                         │
│   │ requirements.txt           │  ← 自动生成，提交到 Git   │
│   │ django==4.2.11             │                         │
│   │   asgiref==3.7.2           │                         │
│   │ requests==2.31.0           │                         │
│   │   urllib3==2.2.1           │                         │
│   └────────┬───────────────────┘                         │
│            │                                             │
│   ③ pip-sync requirements.txt                             │
│            │                                             │
│            ▼                                             │
│   ┌────────────────────────────┐                         │
│   │ 虚拟环境（精确匹配锁文件）    │                         │
│   │ ✓ 所有依赖的精确版本         │                         │
│   │ ✓ 同时卸载不在锁文件中的包   │                         │
│   └────────────────────────────┘                         │
│                                                          │
│   日常使用:                                               │
│   • 加依赖: 编辑 .in → pip-compile → pip-sync             │
│   • 升级:   pip-compile --upgrade → pip-sync              │
│   • 新同事: git clone → pip-sync (一步到位)               │
└──────────────────────────────────────────────────────────┘