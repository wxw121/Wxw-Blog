---

layout: comparison-matrix

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: comparison-matrix — three domain columns: legal, medical, tech.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 领域语料上对比 Embedding 模型



Column 1 — 法律:

- 长句、引用条款号

- 通用模型易漏「第 X 条」

- 关注 Recall@10 与引用准确率



Column 2 — 医疗:

- 缩写、药品名、中英混排

- 错召回代价高 → 阈值从严

- 需合规脱敏 golden set



Column 3 — 技术文档:

- API 名、版本号、代码块

- bge-m3 / e5 常够用

- 看代码实体是否进 Top-3



Bottom: A/B 同一 golden set，只换 embed 模型，索引维度和 chunk 不变



Footer: 领域专用 Embedding 评估 · §6



All text Simplified Chinese.

