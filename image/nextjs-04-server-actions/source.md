# Next.js 学习系列（四）：Server Actions、POST 创建与表单

核心摘录：

## 从读到写
GET 列表/详情（第三篇）→ POST 创建（第四篇）
POST /users · 路由 /users/new · createUser

## 创建流程
用户打开 /users/new → 填表单 → 点创建
→ FormData → createUser Server Action
→ fetch POST API → 201 + id
→ revalidatePath('/users') → redirect('/users/:id')

## Client POST vs Server Actions
| | Client | Server Action |
| 触发 | onSubmit + fetch | form action={createUser} |
| 执行 | 浏览器 | Next 服务器 |
| 提交中 | useState submitting | useFormStatus pending |
| 错误 | useState error | useFormState state.error |
| 跳转 | useNavigate | redirect |
| 刷新列表 | 回列表再 GET | revalidatePath |

## Server Action
'use server' · formData.get('name') · input name 属性

## 提交三态
useFormStatus → pending 禁用按钮
useFormState → state.error 显示错误
成功 → revalidatePath + redirect
