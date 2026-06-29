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
┌───────────────────┬──────────────┬──────────────┬──────────────┐
│      特性          │   长轮询      │     SSE      │  WebSocket   │
│                   │ (Long Poll)  │              │              │
├───────────────────┼──────────────┼──────────────┼──────────────┤
│ 通信方向           │ 双向（模拟）  │ 单向          │ 全双工        │
│                   │              │ (服务器→客户端)│              │
│ 底层协议           │ HTTP         │ HTTP         │ WebSocket    │
│                   │              │              │ (独立协议)    │
│ 浏览器支持         │ 全部         │ 除 IE 外全部   │ 全部(IE10+)  │
│ 自动重连           │ ❌ 需手写    │ ✅ 内置       │ ❌ 需手写     │
│ 断点续传           │ ❌ 需手写    │ ✅ 内置(ID)   │ ❌ 需手写     │
│ 二进制数据         │ ✅           │ ❌ 纯文本     │ ✅ 文本+二进制│
│ 自定义请求头        │ ✅           │ ❌(仅查询参数) │ ✅           │
│ HTTP/2 多路复用    │ ✅           │ ✅ 天然支持   │ ⚠️ 需额外处理 │
│ 代理/CDN 兼容      │ ✅           │ ✅ 完全兼容   │ ⚠️ 需升级支持  │
│ curl 调试          │ ✅           │ ✅ curl -N    │ ❌ 需专用工具  │
│ 连接恢复           │ 重新请求     │ 自动重连      │ 需手写重连    │
│ 消息格式           │ 任意         │ 纯文本        │ 文本+二进制帧 │
│ 服务端推送          │ 被动（客→     │ ✅ 主动推送   │ ✅ 主动推送   │
│                   │   服请求后)   │              │              │
│ 浏览器连接数限制    │ 同 HTTP      │ HTTP/1:6个   │ 无硬限制       │
│                   │              │ HTTP/2:无限制 │              │
│ 实现复杂度          │ 中           │ 低            │ 中高          │
└───────────────────┴──────────────┴──────────────┴──────────────┘