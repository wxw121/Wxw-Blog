---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create educational infographic 16:9, hand-drawn-edu, Simplified Chinese.

Title: 检索后过滤 vs 索引时隔离

LEFT gray「检索后过滤 Post-filter」:
- 先 ANN 取 top-k，再按 acl 筛
- 实现简单，易漏检空结果
- 可能短暂把无权限向量载入内存

RIGHT mint「索引时隔离 Namespace / Partition」:
- 按 tenant_id 分集合或带过滤索引
- 检索天然不越界
- 运维成本略高，企业首选

Bottom coral: 小 demo 用 post-filter；生产建议索引隔离 + 检索过滤双保险

Footer: ACL 访问控制元数据 · §5

All text Simplified Chinese.
