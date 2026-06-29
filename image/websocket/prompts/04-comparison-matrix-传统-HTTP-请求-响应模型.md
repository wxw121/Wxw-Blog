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
          传统 HTTP 请求-响应模型

     客户端                          服务器
        │                              │
        ├──── 1. 建立 TCP 连接 ────────┤
        ├──── 2. 发送 HTTP 请求 ──────►│
        │                              │ 处理请求
        │◄──── 3. 返回 HTTP 响应 ──────┤
        ├──── 4. 关闭 TCP 连接 ────────┤
        │                              │
        │         （沉默……）            │
        │                              │
        ├──── 5. 重新建立连接 ──────────┤  ← 下次请求重新来
        ├──── 6. 发送 HTTP 请求 ──────►│
        │◄──── 7. 返回 HTTP 响应 ──────┤
        ├──── 8. 关闭连接 ─────────────┤
        │                              │
        │    每个请求都是一次独立的「交易」  │
        │    服务器永远不能主动联系客户端    │