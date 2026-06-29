---
layout: linear-progression
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Left-to-right or top-to-bottom process timeline
All visible text in Chinese (简体中文).
Content to visualize faithfully:
# 加依赖
poetry add requests          # 自动选最新兼容版本
poetry add "django==4.2.11"  # 指定精确版本
poetry add "django^4.2"      # 用 caret 约束

# 加开发依赖
poetry add --group dev pytest

# 移除依赖（同时清理 poetry.lock）
poetry remove requests

# 查看依赖树
poetry show --tree
# django 4.2.11
# ├── asgiref >=3.6.0,<4
# │   └── typing-extensions >=4
# └── sqlparse >=0.3.1

# 查看哪些包可以升级
poetry show --outdated

# 升级依赖
poetry update                # 更新所有包（遵守 pyproject.toml 约束）
poetry update django         # 只更新 Django

# 锁定但不安装
poetry lock                  # 只更新 poetry.lock，不安装
poetry lock --no-update      # 刷新 lock 文件的哈希，但不改版本