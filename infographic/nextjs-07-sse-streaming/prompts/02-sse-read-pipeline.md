---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu linear pipeline.

Title: readSSEStream · 从字节到 token

Steps:
① fetch POST /api/chat/stream
② getReader() 读 chunk 字节
③ TextDecoder stream:true 解码
④ buffer 累加 · 按 \n\n 切事件
⑤ 解析 data: {"token":"x"} 行
⑥ onToken → setMessages 追加 content

Side note: 不用 EventSource(仅GET) · 粘包要buffer
Footer: Next.js 学习系列（七)

Simplified Chinese, hand-drawn arrows between steps, doodle server and browser.