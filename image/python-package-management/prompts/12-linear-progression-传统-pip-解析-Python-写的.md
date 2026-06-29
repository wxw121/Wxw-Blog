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
        传统 pip 解析（Python 写的）

    PyPI ──HTTP请求──▶ pip ──Python解析──▶ 安装
              慢             慢

        借助 uv 解析（Rust 写的）

    PyPI ──HTTP请求──▶ uv (Rust核心) ──▶ 安装
              快             极快

    关键优化：
    1. Rust 实现的核心解析逻辑——比 Python 快 10-100 倍
    2. 增量解析——只重新解析变化的部分
    3. 全局缓存——不同项目共享同一个包缓存
    4. 并发下载——同时从多个源拉取包
    5. 使用 PubGrub 算法——比 pip 的回溯算法更高效