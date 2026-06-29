---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Multi-panel bento grid overview
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌──────────────────────────────────────────────────────────┐
│             REST API 设计的灵魂——六条直觉法则               │
│                                                          │
│  1. URL 是名词，HTTP 方法是动词                             │
│     /users 是「用户们」，GET 是「查看」，POST 是「新建」      │
│                                                          │
│  2. 资源有层级，但不要太深                                  │
│     /users/123/orders 好，/a/b/c/d/e 烂                   │
│                                                          │
│  3. 状态码是 HTTP 自带的「语言」——学会使用它                  │
│     不要所有情况都返回 200，然后 body 里再区分               │
│                                                          │
│  4. 响应格式保持统一                                       │
│     成功用 data 包裹，错误用 error 包裹                     │
│     (这样前后端都能写统一的数据提取逻辑)                     │
│                                                          │
│  5. 站在调用方的角度思考                                    │
│     每次设计接口时，想象你就是调用这个 API 的前端开发者        │
│     "这个接口名能猜到是干什么的吗？"                         │
│     "这个错误信息能帮我定位问题吗？"                         │
│                                                          │
│  6. 保持一致，保持一致，保持一致                             │
│     一个项目里所有接口的风格统一比什么都重要                  │
│     宁可全用次优方案，也不要混用多种方案                      │
└──────────────────────────────────────────────────────────┘