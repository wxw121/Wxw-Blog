---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu linear progression.

Title: 两个终端 · CRUD 联调闭环

Two terminal boxes at top:
终端1 backend: uvicorn main:app --reload --port 8000
终端2 frontend: npm run dev

Steps below:
① .env.local API_BASE_URL=127.0.0.1:8000
② next.config.js rewrites 改后重启
③ /users 列表 2人 小明小红
④ /users/new 创建张三
⑤ revalidatePath + redirect
⑥ 回 /users 列表 3人

Graduation check: docs绿勾 · 2人 · 新建后3人

Footer: Next.js 学习系列（五)

Simplified Chinese, numbered steps, stick figures at terminals.
