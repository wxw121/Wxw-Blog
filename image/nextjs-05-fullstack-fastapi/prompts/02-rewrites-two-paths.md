---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu binary comparison.

Title: rewrites 与两条请求路径

TOP half - 配置对照:
LEFT Vite React六: vite.config server.proxy
RIGHT Next 本篇: next.config rewrites
共同: fetch('/api/users') 浏览器打 3000

BOTTOM half - 路径 A vs 路径 B:
LEFT 路径A Server fetch:
谁发起: Next 服务器
URL: getApiBase() → 127.0.0.1:8000/api/users
CORS: 不涉及

RIGHT 路径B 浏览器 fetch:
谁发起: 浏览器
URL: /api/users → rewrite
CORS: 同源 3000

Footer: Next.js 学习系列（五)

Simplified Chinese, VS divider, macaron colors.
