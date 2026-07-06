---
layout: linear-progression
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel step cards,
hand-drawn wobble arrows, stick-figure developer character, Chinese text labels, landscape 16:9.
Layout: Horizontal linear progression with numbered steps, left to right
All visible text in Chinese (简体中文).

Title: Cache-Aside 缓存旁路模式——读写的标准流程

Subtitle: 应用代码自己管缓存，最常见、最好理解的缓存模式

READ path (读数据) - blue arrow flow:

Step 1: 用户请求商品详情
Step 2: 应用先查 Redis —— key: product:1001
Step 3a (命中): 缓存有数据 → 直接返回（快！）
Step 3b (未命中): 缓存没有 → 查 PostgreSQL
Step 4: 从数据库读到后，写入 Redis
Step 5: 返回给用户

WRITE path (写数据) - peach arrow flow below:

Step W1: 更新商品信息
Step W2: 先更新 PostgreSQL（数据库是真相来源）
Step W3: 删除 Redis 中的 key（不是更新缓存！）
Step W4: 下次读取时自动回填缓存

Bottom takeaway in bold:
「读：先缓存后库；写：先库后删缓存」
