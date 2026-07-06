---
layout: hub-spoke
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards,
hand-drawn wobble lines, stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9.
Layout: Hub-spoke with central Redis hub and 6 spokes
All visible text in Chinese (简体中文).

Title: Redis 是什么？—— 内存里的超快字典

Central hub (large circle):
Redis
「数据主要在内存里」
「读写毫秒级」

Spoke 1 - 缓存:
热门商品信息
减轻数据库压力

Spoke 2 - 会话 Session:
用户登录状态
key: session:abc123

Spoke 3 - 计数器:
文章阅读量 +1
INCR page:views:42

Spoke 4 - 排行榜:
Sorted Set 有序集合
游戏积分榜

Spoke 5 - 消息队列:
Pub/Sub 发布订阅
多服务器广播

Spoke 6 - 分布式锁:
同一时刻只允许一个操作
SET key NX EX 10

Bottom note:
「Redis 是 NoSQL 里最常见的键值数据库，但常和 PostgreSQL 配合使用」
