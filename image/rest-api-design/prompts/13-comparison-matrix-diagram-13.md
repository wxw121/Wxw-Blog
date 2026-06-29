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
┌──────────┬──────────────┬──────────────┬──────────────┐
│          │    REST      │   GraphQL    │    gRPC      │
├──────────┼──────────────┼──────────────┼──────────────┤
│ 数据格式  │ JSON/XML     │ JSON         │ Protobuf     │
│          │              │              │ (二进制)      │
│ 传输协议  │ HTTP/1.1     │ HTTP/1.1     │ HTTP/2       │
│ URL 模式  │ 多个端点      │ 单一端点      │ 方法调用      │
│ 学习成本  │ 低            │ 中            │ 中高          │
│ 性能      │ 中            │ 中            │ 高            │
│ 缓存      │ HTTP 缓存天然 │ 需自己实现    │ 需自己实现    │
│          │ 支持          │              │              │
│ 前端友好  │ 中            │ 极高          │ 低            │
│ 适合场景  │ 通用 CRUD    │ 复杂数据查询  │ 微服务间调用  │
│ 工具生态  │ 极丰富        │ 丰富          │ 丰富          │
└──────────┴──────────────┴──────────────┴──────────────┘