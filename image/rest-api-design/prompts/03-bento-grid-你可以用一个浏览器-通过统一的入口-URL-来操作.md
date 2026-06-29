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
你可以用一个浏览器，通过统一的入口（URL）来操作所有资源。

资源 = 图书馆中的东西
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   图书    │  │   读者    │  │   借阅记录 │  │   书架    │
│  /books  │  │ /readers │  │ /loans   │  │ /shelves │
└──────────┘  └──────────┘  └──────────┘  └──────────┘

操作 = 你对这些东西能做什么
GET     /books        → 查看所有图书
GET     /books/42     → 查看第 42 号书
POST    /books        → 新书上架
PUT     /books/42     → 更新第 42 号书的信息
DELETE  /books/42     → 下架第 42 号书

统一性 = 任何资源都用同一套操作方式
GET     /readers/5    → 查看第 5 号读者（和查图书的格式一样！）
POST    /readers      → 新增读者
DELETE  /readers/5    → 注销读者

一旦你知道怎么做，你能举一反三操作任何资源。
这就是 REST 的「可预测性」。