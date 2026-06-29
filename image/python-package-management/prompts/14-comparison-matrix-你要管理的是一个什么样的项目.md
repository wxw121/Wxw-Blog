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
你要管理的是一个什么样的项目？
│
├── 已经有了 requirements.txt，工作流不想改
│   └── → pip-tools（最小改动，最大收益）
│
├── 简单脚本 / 个人项目 / 只想写代码
│   └── → uv（最快最省心）
│
├── 要发布到 PyPI 的库 / 需要完整生命周期管理
│   └── → Poetry（打包、发布、依赖管理全包）
│
├── 大型团队 / 多平台开发 / CI 速度敏感
│   └── → uv（跨平台锁文件 + 极速安装）
│
└── 企业内网 / 严格合规要求
    └── → pip-tools（最透明，审计友好）+ --generate-hashes