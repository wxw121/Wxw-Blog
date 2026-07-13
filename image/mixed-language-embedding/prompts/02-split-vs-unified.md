---

layout: decision-tree

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: decision-tree — when to split index by language vs use unified multilingual index.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 分语言索引 vs 统一多语索引



Decision root: 语料是否大量 code-switching（中英同段）？



Branch A — 是 → 统一索引 + 多语模型（bge-m3）

- 同 chunk 中英混排不丢语义

- 查询语言与文档语言可不同



Branch B — 否，文档按语言分目录 → 可分 collection

- zh 库用中文优化模型

- en 库用英文优化模型

- 查询时 detect language 路由



Bottom warning: 分库后跨语言问法需 Multi-Query 或统一模型兜底



Footer: 中英混合语料 Embedding 选型 · §6



All text Simplified Chinese.

