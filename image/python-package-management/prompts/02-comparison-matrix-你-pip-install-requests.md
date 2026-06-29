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
你:  pip install requests
         │
         ▼
┌────────────────────┐
│  1. 解析包名         │  "requests" 是要装的包
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│  2. 查询 PyPI        │  向 https://pypi.org/simple/requests/ 发请求
│     (Python 包索引)   │  获取所有可用版本列表
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│  3. 选择版本         │  如果没有指定版本，选最新的稳定版
│     并解析依赖       │  requests 依赖: urllib3, certifi, idna, charset-normalizer
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│  4. 递归解析         │  urllib3 没有更多依赖 ✓
│     所有依赖的依赖    │  certifi 没有更多依赖 ✓
│                     │  ... 继续解析所有间接依赖
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│  5. 下载 wheel 包    │  从 PyPI 或其他镜像源下载 .whl 文件
└───────┬────────────┘
        │
        ▼
┌────────────────────┐
│  6. 安装到 site-      │  解压到 Python 的 site-packages 目录
│     packages        │
└────────────────────┘