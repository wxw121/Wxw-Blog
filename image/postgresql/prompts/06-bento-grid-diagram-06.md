---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Multi-panel bento grid overview
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌──────────────────────────────────────────────────────────┐
│              PostgreSQL 六大超级特性                        │
│                                                          │
│  1. JSONB —— 存 JSON、查 JSON、索引 JSON                  │
│     不需要 MongoDB、不需要单独的文档数据库                   │
│                                                          │
│  2. 数组 —— `tags TEXT[]` 一行替代关联表 + JOIN            │
│     标签、爱好、权限……用数组简单又高效                      │
│                                                          │
│  3. CTE —— 用 WITH 把复杂查询拆成可读步骤                  │
│     递归 CTE 处理树形结构（组织架构、分类、评论）            │
│                                                          │
│  4. 窗口函数 —— RANK / ROW_NUMBER / LAG / 累计求和        │
│     报表、排名、同比环比计算，一行 SQL 搞定                 │
│                                                          │
│  5. 全文搜索 —— tsvector + tsquery + 触发器自动维护        │
│     博客搜索、产品搜索，不需要 Elasticsearch               │
│                                                          │
│  6. GIN 索引 —— JSONB、数组、全文搜索的涡轮加速器           │
│     你只管写 @> 查询，剩下的交给 GIN                         │
└──────────────────────────────────────────────────────────┘