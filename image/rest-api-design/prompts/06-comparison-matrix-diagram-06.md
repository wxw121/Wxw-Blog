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
┌─────────┬──────────┬─────────────┬──────────────────┐
│  方法    │  作用     │  幂等性     │  安全性            │
├─────────┼──────────┼─────────────┼──────────────────┤
│  GET    │ 获取      │ ✅ 是       │ ✅ 是（只读）      │
│  POST   │ 创建      │ ❌ 否       │ ❌ 否             │
│  PUT    │ 全量替换  │ ✅ 是       │ ❌ 否             │
│  PATCH  │ 部分更新  │ ❌ 否†      │ ❌ 否             │
│  DELETE │ 删除      │ ✅ 是       │ ❌ 否             │
└─────────┴──────────┴─────────────┴──────────────────┘

幂等性：同样的请求执行 1 次还是 100 次，结果相同
       PUT /users/123 {"name": "张三"}
       执行 1 次→张三，执行 100 次→还是张三
       这就是幂等

安全性：请求会不会修改服务器数据
        GET 是安全的（不应该改数据）
        POST/PUT/PATCH/DELETE 是不安全的

† PATCH 可以实现为幂等的（如 replace 操作），
  但不是所有 PATCH 操作都天然幂等