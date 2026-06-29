---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Table or matrix comparison layout
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌──────────────┬──────────────────────────────────────────────┐
│  索引类型     │  适用场景                                      │
├──────────────┼──────────────────────────────────────────────┤
│  B-tree      │ 默认索引——适合 =, <, >, BETWEEN, ORDER BY      │
│  Hash        │ 只适合 =（比 B-tree 稍快但少用）                │
│  GIN         │ JSONB、数组、全文搜索、trgm——「包含」类查询     │
│  GiST        │ 空间数据(PostGIS)、范围查询、全文搜索           │
│  BRIN        │ 超大规模顺序数据(日志、时序)——极小且够用        │
│  SP-GiST     │ 电话号、IP 路由、非平衡结构                     │
└──────────────┴──────────────────────────────────────────────┘