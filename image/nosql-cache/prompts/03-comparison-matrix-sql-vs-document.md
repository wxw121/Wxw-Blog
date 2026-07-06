---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel table cells,
hand-drawn wobble grid lines, stick-figure characters, Chinese text labels, landscape 16:9.
Layout: Comparison matrix table with 3 rows and 5 columns
All visible text in Chinese (简体中文).

Title: 关系型数据库 vs 文档数据库——怎么选？

Header row:
| 对比维度 | PostgreSQL（关系型） | MongoDB（文档型） |

Row 1 - 数据结构:
PostgreSQL: 固定表结构，多表 JOIN
MongoDB: 灵活 JSON 文档，嵌套字段

Row 2 - 一致性:
PostgreSQL: ACID 事务，强一致
MongoDB: 默认最终一致，事务后加强

Row 3 - 查询方式:
PostgreSQL: SQL 标准查询
MongoDB: 自己的查询语法

Row 4 - 典型场景:
PostgreSQL: 订单、支付、库存
MongoDB: 用户画像、日志、内容 CMS

Row 5 - 和缓存配合:
PostgreSQL: 持久化「真相来源」
MongoDB: 也可做持久化，或配合 Redis

Bottom highlight cell:
「初学者建议：核心业务用 PostgreSQL，灵活字段多的内容用文档库，热点数据用 Redis 缓存」
