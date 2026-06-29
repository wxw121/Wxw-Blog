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
┌──────────────────────────────────────────────────────┐
│                  包源的层次结构                        │
│                                                      │
│   第一层: 本地/内网缓存                                │
│   ┌──────────────────────────────────────────────┐  │
│   │  DevPI / Artifactory / Nexus                │  │
│   │  • 闪电般的安装速度                            │  │
│   │  • 不依赖外网的可靠性                          │  │
│   │  • 可以托管私有包                              │  │
│   └──────────────────┬───────────────────────────┘  │
│                      │ 缓存未命中时回退              │
│                      ▼                              │
│   第二层: 镜像                                        │
│   ┌──────────────────────────────────────────────┐  │
│   │  阿里云 / 清华 TUNA / 中科大 USTC             │  │
│   │  • 国内网络环境下的加速                        │  │
│   │  • PyPI 的完整镜像                            │  │
│   └──────────────────┬───────────────────────────┘  │
│                      │                              │
│                      ▼                              │
│   第三层: 官方源                                      │
│   ┌──────────────────────────────────────────────┐  │
│   │  pypi.org                                   │  │
│   │  • 所有公开 Python 包的源头                   │  │
│   └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘