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
│                    资源命名六大铁律                         │
│                                                          │
│  铁律一：用复数名词                                       │
│  ✅ /api/users        ❌ /api/user                       │
│  ✅ /api/articles     ❌ /api/article                    │
│  ✅ /api/orders       ❌ /api/order                      │
│                                                          │
│  铁律二：用小写字母 + 连字符                               │
│  ✅ /api/order-items      ❌ /api/OrderItems              │
│  ✅ /api/shipping-address ❌ /api/shipping_address        │
│  ✅ /api/daily-reports    ❌ /api/dailyReports            │
│                                                          │
│  铁律三：不用动词                                         │
│  ✅ DELETE /api/orders/5   ❌ GET /api/orders/5/delete    │
│  ✅ POST /api/users        ❌ POST /api/users/create      │
│                                                          │
│  铁律四：集合在最前面                                      │
│  ✅ /api/users/123/orders          ❌ /api/orders/user/123│
│  ✅ /api/articles/42/comments      ❌ /api/comments/42    │
│                                                          │
│  铁律五：层级不宜超过三级                                  │
│  ✅ /api/users/123/orders          ← 三级，可以接受        │
│  ❌ /api/users/123/orders/5/items/7 ← 太深了，拆开        │
│                                                          │
│  铁律六：文件名/扩展名不出现在 URL 中                       │
│  ✅ /api/users/123               ❌ /api/users/123.json   │
│  ✅ /api/reports/sales           ❌ /api/reports/sales.pdf│
│  （格式通过 Accept 请求头控制，不是 URL）                   │
└──────────────────────────────────────────────────────────┘