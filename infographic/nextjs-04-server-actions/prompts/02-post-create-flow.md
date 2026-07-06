---
layout: linear-progression
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu style. Cream paper, wavy arrows, stick figure user.

Title: POST 创建用户 · 全流程

Steps left to right:
① 打开 /users/new 显示表单
② 用户填写 name email 点创建
③ 浏览器打包 FormData
④ Next 服务器 createUser(formData)
⑤ fetch POST /users → 201 + id
⑥ revalidatePath('/users')
⑦ redirect('/users/新id')

Side note: POST 不幂等 · 提交中要禁用按钮

Footer: Next.js 学习系列（四）

Simplified Chinese hand-lettered text.
