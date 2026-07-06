---
layout: binary-comparison
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Educational infographic 16:9 landscape, hand-drawn-edu style. Cream paper, macaron pastels, Simplified Chinese.

Title: 两条路线：Client POST vs Server Actions

LEFT Client路线 (React五 / Next Client):
- onSubmit + preventDefault
- 浏览器 fetch POST
- useState submitting
- useState error
- useNavigate 跳转
- 回列表再 GET

RIGHT Server Actions (本篇主推):
- form action={createUser}
- Next 服务器执行 POST
- useFormStatus pending
- useFormState state.error
- redirect() 跳转
- revalidatePath 刷新列表

Center VS divider.

Bottom: 默认创建表单→Server Actions · 复杂校验/上传→Client fetch

Footer: Next.js 学习系列（四）
