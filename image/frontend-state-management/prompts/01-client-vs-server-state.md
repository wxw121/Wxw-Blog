---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: binary-comparison — left column Client State, right column Server State, vertical divider in center.

Style: hand-drawn-edu — macaron pastel cards on warm cream paper (#F5F0E8), wavy lines, stick figures, hand-lettered Simplified Chinese, coral red (#E8655A) accents.

Title (top center, bold hand-drawn): 先分清两类状态：客户端 vs 服务端

Left side label: 客户端状态
Left subtitle: Zustand / Redux / Pinia
Left comparison rows:
- 权威来源：当前页面 / 用户操作
- 是否过期：一般不过期
- 多组件共享：全局库或 Context
- 典型例子：主题、侧栏折叠、tab、聊天草稿

Right side label: 服务端状态
Right subtitle: TanStack Query
Right comparison rows:
- 权威来源：后端 API
- 是否过期：会过期，需刷新轮询
- 多组件共享：Query / SWR 请求缓存库
- 典型例子：用户列表、文档索引、分页结果

Center divider with bidirectional arrows showing:
Left loop: UI ↔ Store
Right loop: UI ↔ Query ↔ API

Bottom takeaway (bold): 先问数据权威在谁那儿
Footer: 前端状态管理完全指南 · §2

Legible Chinese, generous whitespace, one stick figure on each side.
