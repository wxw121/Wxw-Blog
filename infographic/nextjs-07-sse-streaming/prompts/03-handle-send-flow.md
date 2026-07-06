---
layout: circular-flow
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu circular/state flow.

Title: handleSend · 聊天状态机

Flow nodes:
用户点发送
→ 插入 user + 空 assistant
→ new AbortController + fetch signal
→ readSSEStream 每 token map 更新 assistantId
→ 流结束 isStreaming=false
→ (可选) 点停止 abort() → AbortError 忽略

State boxes:
messages[] · isStreaming · abortController · bottomRef滚底

Wrong X: 每次发送共用一个 controller
Right check: 每次发送 new 一个 · 流中禁再发

Footer: Next.js 学习系列（七)

Simplified Chinese, macaron colors, stick figure chatting.