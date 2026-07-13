---

layout: linear-progression

style: hand-drawn-edu

aspect_ratio: 16:9

language: zh

---



Create a professional educational infographic, 16:9 landscape.

Layout: linear-progression left to right, 7 steps.

Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.



Title: 增量重索引流程



Steps:

1. Scheduler 对账

2. diff → added / changed / removed

3. mark processing

4. 解析 → 清洗 → 分块

5. delete 旧 chunk（按 doc_id）

6. embed → insert 向量

7. catalog success + flip is_latest



Branches below: removed → delete_vectors + tombstone



Bottom: 先删后插，幂等可重试



Footer: 增量更新与变更检测完全指南 · §7



All text Simplified Chinese.

