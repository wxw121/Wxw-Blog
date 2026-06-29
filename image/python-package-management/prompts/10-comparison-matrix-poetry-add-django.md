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
poetry add django
        │
        ▼
┌───────────────────────────────────────────┐
│  1. 读取 pyproject.toml                    │
│     "django": 已存在什么约束？              │
│     其他已安装的包有什么约束？               │
└───────────────────┬───────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────┐
│  2. 从 PyPI 获取 Django 所有可用版本        │
│     符合 ^4.2 的版本: 4.2.0 ~ 4.2.11       │
└───────────────────┬───────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────┐
│  3. 从最新版开始尝试（4.2.11）              │
│     解析它的依赖: asgiref>=3.6,<4           │
│                  sqlparse>=0.3.1            │
└───────────────────┬───────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────┐
│  4. 检查这些依赖是否与已有依赖冲突           │
│     asgiref 需要 >=3.6,<4                  │
│     已有包有没有要求 asgiref<3.6 的？        │
│     → 没有冲突 ✓                           │
└───────────────────┬───────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────┐
│  5. 全部通过 → 写入 poetry.lock            │
│     有冲突 → 尝试上一个版本，重复步骤 3       │
│     所有版本都冲突 → 报错，告诉你具体原因     │
└───────────────────────────────────────────┘