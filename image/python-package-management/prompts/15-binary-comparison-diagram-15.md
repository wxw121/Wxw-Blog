---
layout: binary-comparison
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Side-by-side A vs B comparison layout with vertical divider
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌──────────────────────────────────────────────────────────┐
│                   哈希校验工作流                            │
│                                                          │
│  生成锁文件时:                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ 下载包    │───▶│ 计算哈希  │───▶│ 写入锁文件 │            │
│  │ django   │    │ SHA-256  │    │ hash=     │            │
│  │ 4.2.11   │    │          │    │ abc123... │            │
│  └──────────┘    └──────────┘    └──────────┘            │
│                                                          │
│  安装时:                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │ 下载包    │───▶│ 计算哈希  │───▶│ 对比锁文件 │           │
│  │ django   │    │ SHA-256  │    │ 中的哈希  │            │
│  │ 4.2.11   │    │          │    │           │            │
│  └──────────┘    └──────────┘    └─────┬─────┘            │
│                                        │                  │
│                               ┌────────┴────────┐        │
│                               │ 匹配？  │ 不匹配？│        │
│                               ▼         ▼        │
│                             安装 ✅   拒绝 ❌      │
│                                      （报警！）    │
└──────────────────────────────────────────────────────────┘