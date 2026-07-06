---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: binary-comparison — Server Component vs Client Component.

Style: hand-drawn-edu, cream paper, macaron blue left, macaron peach right.

Title: 服务端组件 vs 客户端组件

Left: Server Component（默认，无 use client）
- 运行在 Next 服务器
- async await fetch ✅
- useState useEffect ❌
- onClick ❌
- 首屏 HTML 已有数据

Right: Client Component（'use client'）
- 运行在浏览器
- useState useEffect ✅
- onClick onChange ✅
- async page ❌
- 搜索框、表单、选中

Center VS divider.

Bottom takeaway: 只展示数据→Server · 要交互→Client

Footer: Next.js 学习系列（三）

Simplified Chinese. Server cloud icon left, browser icon right.
