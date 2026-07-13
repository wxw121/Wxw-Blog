---
layout: comparison-matrix
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: comparison-matrix — three columns: Redis vs SQLite vs Disk.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 缓存存储选型（Redis / SQLite / Disk）

Column 1 Redis:
- 快，多实例共享
- 适合在线查询 embed 缓存
- 需 TTL 与内存预算

Column 2 SQLite:
- 单机持久化，零运维
- 适合索引任务断点续跑
- 并发写有限

Column 3 磁盘 / Parquet:
- 海量向量冷缓存
- 重建索引时复用
- 读慢于内存

Footer: Embedding 缓存策略完全指南 · §6

All text Simplified Chinese.
