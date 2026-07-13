---
layout: hub-spoke
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: hub-spoke — center hub with four spokes.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 近似最近邻 ANN 是什么？

Center hub: 查询向量 q → 在百万向量里找 Top-k 邻居

Spoke 1: 暴力穷举（Flat）
- 每条都算距离
- 准但慢

Spoke 2: ANN 近似
- 牺牲少量召回换速度
- 本地 FAISS 常用

Spoke 3: 召回 vs 延迟
- recall@k 越高越慢
- 工程要调参

Spoke 4: RAG 场景
- chunk 向量入库
- query 向量近邻 → 取原文

Footer: FAISS 本地 ANN 完全指南 · §3

All text Simplified Chinese.
