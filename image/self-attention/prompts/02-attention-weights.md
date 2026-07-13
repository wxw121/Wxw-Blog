---
layout: structural-breakdown
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: structural-breakdown / linear flow with callouts.
Style: hand-drawn-edu, cream paper, macaron cards, stick figure, Simplified Chinese.

Title: 注意力权重：先打分，再按比例混合

Horizontal 4-step flow:
1. 每个词算出 Q、K、V
2. 用当前词的 Q 去和所有词的 K 打分（分数条高低不同）
3. 分数变成权重（饼图或百分比：0.1 / 0.7 / 0.2）— 标注「加起来约等于 1」
4. 按权重混合各词的 V → 得到当前词的新表示

Callout: Softmax 把分数变成「占比」；本篇不推公式

Example sentence chips: 银行 / 河岸 / 开户 — 说明「银行」在金融句里会更看「开户」

Bottom: 权重高 = 这次多看谁；不是永久同义词表

Footer: Self-Attention 完全指南 · §4

All text Simplified Chinese.
