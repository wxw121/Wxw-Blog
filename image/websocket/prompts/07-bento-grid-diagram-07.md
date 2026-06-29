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
│                   WebSocket 帧结构                        │
│                                                         │
│  0                   1                   2                │
│  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 ...  │
│ +-+-+-+-+-------+-+-------------+-----------------------+  │
│ |F|R|R|R| opcode|M| Payload len | Extended payload...  │  │
│ |I|S|S|S|  (4)  |A|     (7)     | (16/64 bit, if ...)  │  │
│ |N|V|V|V|       |S|             |  needed)             │  │
│ | |1|2|3|       |K|             |                      │  │
│ +-+-+-+-+-------+-+-------------+-----------------------+  │
│ | Masking-key (4 bytes, if MASK=1)                      │  │
│ +-------------------------------------------------------+  │
│ | Payload Data ( masked )                               │  │
│ +-------------------------------------------------------+  │
│                                                         │
│  FIN:    1 bit  — 这是消息的最后一帧吗？                   │
│  opcode: 4 bits — 帧类型:                               │
│           0x1 = 文本帧                                   │
│           0x2 = 二进制帧                                  │
│           0x8 = 关闭帧                                   │
│           0x9 = Ping 帧（心跳）                          │
│           0xA = Pong 帧（心跳响应）                       │
│  MASK:   1 bit  — 是否需要掩码（客户端→服务器必须 mask）   │
│  Payload len: 7/16/64 bits — 数据长度                    │
│  Masking-key: 4 bytes — 掩码密钥（客户端发送时必须）      │
│  Payload Data: 实际数据                                  │
└─────────────────────────────────────────────────────────┘