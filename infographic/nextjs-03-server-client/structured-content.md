# Structured Content: Next.js 第三篇信息图

## Title
服务端 fetch 与 useEffect 对照

## Learning Objectives
1. 默认 page 是 Server Component
2. async page 里 await fetch
3. 交互拆到 use client 子组件

---

## Section 1: 中心问题（Hub）
**Key concept**: 数据该在服务器拿还是浏览器拿？
**Content**: 不是不用 useEffect，是多一种在服务器取数的选择
**Visual**: 中心大问号或天平
**Labels**: 数据在哪取？

---

## Section 2: Server 分支（左/上）
**Key concept**: 默认在服务器跑
**Content**:
- 无 use client
- async page + await fetch
- 首屏 HTML 已有列表
- loading.js / error.js 三态
**Visual**: 服务器图标 → fetch → HTML
**Labels**: Server Component

---

## Section 3: Client 分支（右/下）
**Key concept**: 交互在浏览器
**Content**:
- 顶行 'use client'
- useState / useEffect / onClick
- 收 props 做筛选选中
- 不能 import Server 组件
**Visual**: 浏览器图标 → 搜索框/按钮
**Labels**: Client Component

---

## Section 4: 自检四问（底部）
**Key concept**: 一分钟判断放哪
**Content**:
- useState? → Client
- onClick? → Client
- window? → Client
- 只 fetch+map? → Server
**Visual**: 四个小卡片
**Labels**: 自检

---

## Footer
Next.js 学习系列（三）· 对照 React（三）
