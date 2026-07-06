# Next.js 学习系列（二）：create-next-app 与第一个 page

核心内容摘录：

## 创建命令
npx create-next-app@latest my-next-app
推荐：JS、ESLint、No Tailwind、src/、App Router
npm run dev → http://localhost:3000

## 目录对照 Vite
| Vite | Next App Router |
| index.html + #root | 框架生成 |
| main.jsx | layout.js |
| App.jsx | app/page.js = / |
| react-router | 文件夹 + page.js |
| :5173 | :3000 |

## 核心文件
- layout.js：整站外壳，{children} 插当前 page
- page.js：一个 URL 一页
- src/app/about/page.js → /about
- next/link：客户端跳转

## use client
要 useState / onClick → 文件顶加 'use client'

## 动手路径
创建项目 → 认 layout/page → 改首页 → 加 /about + Link
