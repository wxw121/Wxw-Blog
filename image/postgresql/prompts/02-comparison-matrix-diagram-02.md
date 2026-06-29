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
┌───────────────────┬──────────────────┬──────────────────┐
│      特性          │   PostgreSQL     │      MySQL       │
├───────────────────┼──────────────────┼──────────────────┤
│ 许可证             │ PostgreSQL 许可证 │ GPL + 商业版      │
│ JSON 支持          │ ✅ JSONB (二进制) │ ✅ JSON (文本)    │
│ 索引类型           │ B-tree/GIN/GiST/  │ B-tree/全文(GIN) │
│                   │ BRIN/SP-GiST/Hash│ /空间(R-tree)    │
│ 窗口函数           │ ✅ 完整支持       │ ✅ 基本支持       │
│ CTE (WITH)         │ ✅ 递归支持       │ ✅ 基本支持       │
│ 数组类型           │ ✅ 原生支持       │ ❌ 不支持         │
│ 物化视图           │ ✅              │ ❌ 不支持         │
│ 表继承             │ ✅              │ ❌               │
│ 部分索引           │ ✅              │ ❌               │
│ 并发能力           │ MVCC (多版本)    │ MVCC + 锁        │
│ 扩展生态           │ 极丰富           │ 较少             │
└───────────────────┴──────────────────┴──────────────────┘