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
┌─────────────────────────────────────────────────────────┐
│                    从写信到打电话                          │
│                                                         │
│  1. 短轮询 (Short Polling)                               │
│     ┌─────────────────────────────────────────────┐     │
│     │ 像写信:                                      │     │
│     │ 你每隔一天去邮局问「有我的信吗？」              │     │
│     │ 邮局说「没有」——你回家了                      │     │
│     │ 第二天又去……终于有信了                        │     │
│     │                                             │     │
│     │ 缺点: 大部分时间在路上跑冤枉路                 │     │
│     │ 实现: setInterval + fetch                    │     │
│     └─────────────────────────────────────────────┘     │
│                                                         │
│  2. 长轮询 (Long Polling)                                │
│     ┌─────────────────────────────────────────────┐     │
│     │ 像你在邮局门口蹲着等:                          │     │
│     │ 「有我的信之前我不走」                         │     │
│     │ 邮局收到信后立刻叫你——你拿到信走人              │     │
│     │ 下次想看信再来蹲                               │     │
│     │                                             │     │
│     │ 缺点: 邮局要一直惦记着你这个人                 │     │
│     │ 实现: 服务端 hold 住连接直到有数据             │     │
│     └─────────────────────────────────────────────┘     │
│                                                         │
│  3. Server-Sent Events (SSE)                             │
│     ┌─────────────────────────────────────────────┐     │
│     │ 像你订了报纸:                                 │     │
│     │ 每天早上报纸自动投递到你家                     │     │
│     │ 你不需要出门——但不能给报社回信                  │     │
│     │                                             │     │
│     │ 缺点: 单向——只能服务器→客户端                  │     │
│     │ 实现: EventSource API                        │     │
│     └─────────────────────────────────────────────┘     │
│                                                         │
│  4. WebSocket                                            │
│     ┌─────────────────────────────────────────────┐     │
│     │ 像打电话:                                     │     │
│     │ 拨通后双方随时可以说话                         │     │
│     │ 你说一句我说一句，不用每句话都重新拨号          │     │
│     │ 挂断后通话结束                                │     │
│     │                                             │     │
│     │ 优点: 全双工——双向实时                        │     │
│     │ 实现: WebSocket 协议                          │     │
│     └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘