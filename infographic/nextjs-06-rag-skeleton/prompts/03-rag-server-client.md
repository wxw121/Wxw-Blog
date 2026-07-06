---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu bento-grid 6 cards.

Title: RAG 功能 · Server 还是 Client？

Cards with Server=blue / Client=peach labels:
SiteNav → Client (usePathname)
/chat 整页 → Client (useState SSE AbortController)
/documents 上传 → Client (onChange 进度)
/debug/retrieve → Client (表单 结果表)
/users 列表 → Server (第三篇保持)

Big X wrong example: Server page 里 useState 报错
Big check correct: chat/page.js 顶行 'use client'

Bottom rule: 能静态放Server · 要Hook流式放Client
Footer: Next.js 学习系列（六)

Simplified Chinese, doodle icons, cream background.