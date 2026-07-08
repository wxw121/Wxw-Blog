# Structured Content: Next.js 第一篇信息图

## Title
什么时候选 Next？和 Vite 差在哪

## Learning Objectives
1. 分清 React、Vite、Next.js 各自职责
2. 对照 Vite SPA 与 Next App Router 六个维度
3. 用五问决策树快速选型

---

## Section 1: 三个名字（顶部横幅）
**Key concept**: 不是升级，是另一种壳
**Content**: React = 演员；Vite = 排练场；Next.js = 剧院整包
**Visual**: 三个卡通图标横排，箭头指向「同一套 React」
**Labels**: React / Vite / Next.js

---

## Section 2: 左右对照（主体）
**Key concept**: Vite SPA vs Next.js
**Content**（左栏 Vite，右栏 Next）:
- 创建: create vite | create-next-app
- 路由: Routes 手写 | 文件即路由 page.js
- 首屏: CSR 空壳 | SSR/SSG 有内容
- 数据: useEffect fetch | 服务端 fetch
- 部署: dist 静态 | Node / Vercel
**Visual**: 左右分栏对比，中间 VS
**Labels**: Vite + React Router / Next App Router

---

## Section 3: 五问决策树（底部）
**Key concept**: 选型决策
**Content**:
1. 要 SEO？→ 是 Next / 否 Vite
2. 首屏能等 JS？→ 能 Vite / 不能 Next
3. 已有 API？→ 都行
4. 熟 React 六篇？→ 否先 Vite
5. 仅静态托管？→ Vite 更简单
**Visual**: 简化流程图，5 个节点
**Labels**: 五问选型

---

## Footer
Next.js 学习系列（一）· 零代码选型篇
