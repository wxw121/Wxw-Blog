---

layout: funnel

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: funnel — query flows through retrieval to measure Recall@k and MRR.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: Golden Set 与 Recall@k / MRR



Top: Golden Set 表格示意

- query: 「差旅住宿上限？」

- relevant_chunk_ids: [chunk_42, chunk_43]



Funnel stages:

1. Embedding 检索 Top-k（k=5, 10, 20）

2. Recall@k = 命中 relevant 的比例

3. MRR = 第一个 relevant 排名的倒数均值



Side note: 领域评测不用公开 MTEB 代替，要用自家 chunk



Footer: 领域专用 Embedding 评估 · §4



All text Simplified Chinese.

