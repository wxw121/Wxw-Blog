# Next.js 学习系列（一）：什么时候选 Next、和 Vite 差在哪

核心内容摘录（配图用）：

## 三个名字
- React = 写组件的库（演员）
- Vite = 构建工具 + 开发服务器（排练场）
- Next.js = 基于 React 的框架（剧院整包：路由 + 渲染 + 部署）

## Vite SPA vs Next.js 对照
| 维度 | Vite + React Router | Next.js App Router |
| 创建 | npm create vite | npx create-next-app |
| 路由 | Routes 手写 | app/users/page.js 文件即路由 |
| 首屏 | CSR，SEO 较弱 | SSR/SSG 更友好 |
| 数据 | useEffect + fetch | 服务端直接 fetch |
| 部署 | dist/ 静态 | Node 或 Vercel |

## 决策树五问
1. 要不要 SEO？否→Vite，是→Next
2. 首屏能否等 JS？能等→Vite，不能→Next
3. 已有独立 API？都行；想 JS 全包→Next
4. 熟悉 React 六篇？否先 Vite，是可开 Next
5. 只有静态托管？Vite 更简单

## 学习路径
React（一）ES6+ → Next 1 选型（零代码）→ Next 2 搭项目 → Next 3 取数
