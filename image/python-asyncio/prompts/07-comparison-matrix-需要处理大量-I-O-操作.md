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
需要处理大量 I/O 操作？
  │
  ├── 否 → 同步就够了，别折腾
  │
  └── 是 → I/O 是瓶颈吗（而非 CPU）？
            │
            ├── 否（CPU 密集）→ 用多进程（multiprocessing）
            │
            └── 是 → 团队熟悉异步吗？
                      │
                      ├── 否 → 用多线程（threading）也行
                      │       （对 I/O 密集，多线程也有效）
                      │
                      └── 是 → 用 asyncio！
                              享受高性能和优雅代码