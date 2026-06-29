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
┌─────────────────┬──────────┬──────────┬──────────┐
│      特性        │ pip-tools│  Poetry  │    uv    │
├─────────────────┼──────────┼──────────┼──────────┤
│ 依赖声明文件      │ .in 文件  │pyproj.toml│pyproj.toml│
│ 锁文件           │ .txt 文件 │poetry.  │ uv.lock  │
│                 │          │ lock     │          │
│ 虚拟环境管理      │ ❌ 需手动 │ ✅ 自动   │ ✅ 自动   │
│ 依赖解析器        │ pip      │ Poetry   │ 自研(Rust) │
│ 解析速度          │ ★★      │ ★★★     │ ★★★★★   │
│ 跨平台锁文件      │ ❌       │ ❌       │ ✅       │
│ 哈希校验          │ ✅ 可选   │ ✅ 默认   │ ✅ 默认   │
│ 打包/发布         │ ❌       │ ✅       │ ❌(开发中)│
│ 与 pip 兼容       │ ✅ 100%  │ ❌ 自己的 │ ✅ 兼容   │
│ Python版本管理    │ ❌       │ ❌       │ ✅       │
│ 学习成本          │ ★       │ ★★★     │ ★★      │
│ 社区成熟度        │ ★★★★★   │ ★★★★    │ ★★★     │
│ 安装速度          │ ★★      │ ★★★     │ ★★★★★   │
└─────────────────┴──────────┴──────────┴──────────┘