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
│                    心跳保活原理                           │
│                                                         │
│  WebSocket 协议内置了 Ping/Pong 帧，但很多网络中间件        │
│  （代理、负载均衡、NAT 网关、防火墙）会主动断开空闲连接。     │
│                                                         │
│  典型的心跳流程:                                          │
│                                                         │
│  客户端                        服务器                     │
│    │                             │                       │
│    ├──── ping ─────────────────►│  (每 30 秒)             │
│    │◄─── pong ──────────────────┤  (服务器应立即回复)      │
│    │                             │                       │
│    ├──── ping ─────────────────►│                        │
│    │         (无响应...)         │  ← 连接可能断了         │
│    │         (等待 10 秒)        │                       │
│    │                             │                       │
│    ├──── 主动断开 + 开始重连 ────┤                       │
│                                                         │
│  关键参数:                                               │
│  • 心跳间隔: 通常 15-30 秒（比 NAT 超时短）               │
│  • 心跳超时: 通常 5-10 秒（超过此时间没收到 pong→断开）    │
└─────────────────────────────────────────────────────────┘