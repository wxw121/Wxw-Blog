---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Table or matrix comparison layout
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌───────┬──────────────────────────────────────────────────┐
│ 状态码 │ 含义                 │ 何时使用                    │
├───────┼──────────────────────┼───────────────────────────┤
│ 200   │ OK                   │ GET/PUT/PATCH 成功         │
│ 201   │ Created              │ POST 创建成功              │
│ 202   │ Accepted             │ 异步任务已接受，结果稍后出  │
│ 204   │ No Content           │ DELETE 成功，无响应体      │
│       │                      │                           │
│ 301   │ 永久重定向           │ URL 永久迁移               │
│ 302   │ 临时重定向           │ URL 临时迁移               │
│       │                      │                           │
│ 400   │ Bad Request          │ 请求格式不对/参数校验失败  │
│ 401   │ Unauthorized         │ 没登录/没提供 token       │
│ 403   │ Forbidden            │ 登录了但没有权限            │
│ 404   │ Not Found            │ 资源不存在                  │
│ 405   │ Method Not Allowed   │ 用 POST 调了只支持 GET 的   │
│ 409   │ Conflict             │ 冲突（如并发修改/重复创建） │
│ 422   │ Unprocessable Entity │ 参数格式对但语义不对        │
│ 429   │ Too Many Requests    │ 触发限流                    │
│       │                      │                           │
│ 500   │ Internal Server Error│ 服务器未知错误              │
│ 502   │ Bad Gateway          │ 上游服务返回了错误          │
│ 503   │ Service Unavailable  │ 服务在维护/过载             │
└───────┴──────────────────────┴───────────────────────────┘