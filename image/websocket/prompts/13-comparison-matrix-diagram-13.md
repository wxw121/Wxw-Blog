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
┌─────────────────────────────────────────────────────────┐
│               WebSocket 水平扩展方案                      │
│                                                         │
│  问题: 用户 A 连在服务器 1，用户 B 连在服务器 2             │
│        他们在一个聊天室里，怎么互发消息？                   │
│                                                         │
│  方案一: Redis Pub/Sub (最常用)                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Server 1 │    │  Server 2 │    │  Server 3 │           │
│  │  User A   │    │  User B   │    │  User C   │           │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘           │
│        │               │               │                  │
│        └───────┬───────┴───────┬───────┘                  │
│                │               │                          │
│                ▼               ▼                          │
│          ┌──────────────────────────┐                    │
│          │      Redis Pub/Sub       │                    │
│          │  频道: room:general       │                    │
│          └──────────────────────────┘                    │
│                                                         │
│  User A 发消息 → Server 1 → Redis 发布                   │
│  Server 2,3 订阅 Redis → 收到消息 → 推送给本地 User B,C   │
│                                                         │
│  方案二: 会话亲和性 (Sticky Session)                      │
│  Nginx/LB 根据 cookie 把同一用户始终路由到同一台服务器      │
│  ⚠️ 不解决跨用户通信，只解决单用户状态问题                  │
│                                                         │
│  方案三: 专门的消息中间件 (Kafka/RabbitMQ)                 │
│  大流量场景，消息可靠投递要求高时使用                       │
└─────────────────────────────────────────────────────────┘