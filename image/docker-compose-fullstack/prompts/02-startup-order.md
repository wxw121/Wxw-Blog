---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: linear-progression left-to-right with arrows and health gates.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: 依赖启动顺序与健康门闩

Steps:
1. postgres + redis 先 healthy
2. chroma 数据卷就绪
3. api 通过 /ready
4. worker 消费队列
5. frontend 代理到 api

Callout: depends_on + healthcheck 避免「假启动」

Footer: Docker Compose 全栈部署 · §6
