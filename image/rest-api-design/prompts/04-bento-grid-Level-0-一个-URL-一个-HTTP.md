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
Level 0: 一个 URL + 一个 HTTP 方法（通常是 POST）
┌─────────────────────────────────────────────┐
│ POST /api/service                           │
│                                             │
│ {"action": "createUser", "data": {...}}     │
│ {"action": "deleteUser", "data": {...}}     │
│ {"action": "getUser", "data": {...}}        │
│                                             │
│ 所有操作挤在一个地址，像在寄信——              │
│ 信封地址一样，信纸里写你要干什么               │
└─────────────────────────────────────────────┘

Level 1: 每种资源有独立的 URL
┌─────────────────────────────────────────────┐
│ POST /api/users/create                      │
│ POST /api/users/delete                      │
│ POST /api/users/get                         │
│                                             │
│ URL 开始有结构了，但还没用对 HTTP 方法         │
└─────────────────────────────────────────────┘

Level 2: 正确使用 HTTP 方法 ← 多数 API 的目标
┌─────────────────────────────────────────────┐
│ GET    /api/users        # 查               │
│ GET    /api/users/123    # 查单个            │
│ POST   /api/users        # 增               │
│ PUT    /api/users/123    # 改               │
│ DELETE /api/users/123    # 删               │
│                                             │
│ URL 定位资源，HTTP 方法表示操作               │
└─────────────────────────────────────────────┘

Level 3: HATEOAS（超媒体即应用状态引擎）
┌─────────────────────────────────────────────┐
│ GET /api/users/123                          │
│ {                                           │
│   "id": 123,                                │
│   "name": "张三",                            │
│   "_links": {                               │
│     "self": "/api/users/123",               │
│     "orders": "/api/users/123/orders",      │
│     "deactivate": "/api/users/123/deactivate"│
│   }                                         │
│ }                                           │
│                                             │
│ 响应里包含了「接下来可以做什么」的链接          │
│ 理想很丰满，现实中使用很少                     │
└─────────────────────────────────────────────┘