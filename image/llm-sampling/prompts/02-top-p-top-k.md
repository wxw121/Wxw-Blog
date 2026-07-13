---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: binary-comparison left vs right.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: Top-k vs Top-p：两种缩小抽签箱的方式

Left — Top-k:
- 词表按概率排序
- 只留前 k 名进箱子
- 示意：k=5 的小名单
- 一句话：按名次裁

Right — Top-p（核采样）:
- 从高到低累加概率
- 凑满 p（如 0.9）的核心集
- 分布尖时人少，分布平时人多
- 一句话：按概率质量裁

Bottom bridge: 都是先裁候选再采样；调参时一次只拧一个旋钮

Footer: Temperature / Top-p / Top-k 完全指南 · §5
