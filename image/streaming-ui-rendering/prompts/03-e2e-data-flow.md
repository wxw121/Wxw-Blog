---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: linear-progression — horizontal sequence diagram style, 6 steps left to right with optional branch for abort.

Style: hand-drawn-edu — macaron pastel cards on warm cream (#F5F0E8), wavy arrows, stick figures for 用户 and 聊天UI, hand-lettered Simplified Chinese, coral red for abort branch.

Title (top center): 端到端：从发送到停止

Main flow (6 steps):
1. 用户点击发送
2. UI 追加 user + 空 assistant
3. fetch + AbortController.signal
4. loop 每个 chunk: API 返回文本片段
5. content += chunk（同一条气泡变长）
6. 流结束 → status=done → idle

Abort branch (downward from step 4-5, coral):
用户点停止 → controller.abort() → status=aborted → idle

Key note box: 一条 assistant = 一个气泡 · 追加而非覆盖

Bottom takeaway: content_new = content_old + chunk
Footer: 流式 UI 渲染完全指南 · §12

Legible Chinese, sequence arrows between steps.
