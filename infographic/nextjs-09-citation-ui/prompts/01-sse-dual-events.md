---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu SSE protocol timeline.

Title: SSE 双事件 · token 与 citations 分两路

Timeline:
① handleSend 创建 assistant content:'' citations:[]
② 多个 data:{"token":"x"} → onToken 拼 content
③ 流末尾 data:{"citations":[...]} → onCitations
④ data:[DONE] → isStreaming=false
⑤ CitationList 可点 · Markdown 排版

Wrong X: citations当token拼正文
Right: 分支 token→content citations→message.citations

Footer: Next.js 学习系列（九)

Simplified Chinese, macaron pastels.