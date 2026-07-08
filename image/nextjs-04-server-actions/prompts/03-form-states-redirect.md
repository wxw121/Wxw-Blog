---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu bento-grid. 4 macaron cards, cream background.

Title: 提交三态与成功后跳转

Card 1 mint - useFormStatus:
pending → 按钮显示「提交中…」并 disabled
必须在 form 子组件里

Card 2 peach - useFormState:
state.error → role=alert 显示错误
form action={formAction}

Card 3 blue - 成功 redirect:
redirect(`/users/${id}`)
Server Action 里用，不用 useRouter

Card 4 lavender - revalidatePath:
revalidatePath('/users')
先失效缓存再 redirect

Center note: 'use server' + input name + formData.get()

Footer: Next.js 学习系列（四）

Simplified Chinese, doodle icons, legible labels.
