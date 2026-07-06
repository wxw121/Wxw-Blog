# Structured Content: Next.js 第二篇信息图

## Title
create-next-app 与第一个 page

## Learning Objectives
1. 用推荐选项创建项目
2. 理解 layout 与 page 分工
3. 新建 /about 并用 Link 跳转

---

## Section 1: 创建与启动（步骤 1-2）
**Key concept**: 从命令到 localhost:3000
**Content**:
- npx create-next-app@latest my-next-app
- 推荐: JS · ESLint · src/ · App Router
- npm run dev → :3000
**Visual**: 终端 + 浏览器，步骤 ①②
**Labels**: 创建 / 启动

---

## Section 2: 目录对照（步骤 3）
**Key concept**: 和 Vite 对照认路
**Content**:
- main.jsx → layout.js（外壳）
- App.jsx → page.js（首页 /）
- Routes → about/page.js（/about）
- :5173 → :3000
**Visual**: 简化目录树 my-next-app/src/app/
**Labels**: layout.js / page.js / about/page.js

---

## Section 3: 核心分工（步骤 4-5）
**Key concept**: layout 包 page
**Content**:
- layout: html body {children} 共用导航
- page: 每个 URL 独有内容
- Link: 无刷新跳转
- use client: useState 时需要
**Visual**: layout 大框套两个小 page 框，Link 箭头
**Labels**: 外壳 / 页面 / Link / use client

---

## Footer
Next.js 学习系列（二）· 第一个 localhost 页面
