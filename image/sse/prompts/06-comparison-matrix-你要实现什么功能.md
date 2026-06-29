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
你要实现什么功能？
│
├── 服务器→客户端 单向推送
│   ├── 只需要文本 → SSE ✅ 最佳选择
│   │   (通知、进度、AI流式、股票、日志、动态流)
│   │
│   └── 需要二进制数据 → WebSocket
│       (实时音频、视频帧、protobuf 数据)
│
├── 客户端→服务器 也需要实时发送
│   └── → WebSocket
│       (聊天、游戏、协作编辑、远程控制)
│
├── 兼容性极端重要（IE 也支持）
│   └── → 长轮询（或 Socket.IO 开降级模式）
│
├── 追求极致简单
│   ├── 纯文本推送 → SSE（三行代码）
│   └── 双向 → WebSocket
│
└── 不确定 → 画个消息流向图
    只有 服务器→客户端 的箭头？→ SSE
    有 客户端→服务器 的箭头？→ WebSocket