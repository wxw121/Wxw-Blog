---
layout: circular-flow
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: circular-flow / state diagram — 5 state nodes with directional arrows showing transitions, idle at center or top.

Style: hand-drawn-edu — macaron pastel rounded nodes on warm cream (#F5F0E8), wavy arrows, stick figure user, hand-lettered Simplified Chinese, coral red for streaming state, mint for done, peach for aborted.

Title (top center): 聊天 UI 状态机

State nodes (macaron cards):
- idle（空闲）- center/top, gray-blue
- streaming（生成中）- coral red highlight, show 停止按钮 icon
- done（完成）- mint green
- aborted（已停止）- peach
- error（出错）- coral warning

Transitions with labeled arrows:
- idle → streaming: 用户发送
- streaming → done: 流正常结束
- streaming → aborted: 用户点停止
- streaming → error: 网络/服务端错误
- done → idle: 可再次发送
- aborted → idle: 可再次发送
- error → idle: 可重试

Callout near streaming: 显示停止按钮 · 禁用输入

Bottom takeaway: 中断是正常路径，不是异常
Footer: 流式 UI 渲染完全指南 · §12

Legible Chinese, clear state hierarchy.
