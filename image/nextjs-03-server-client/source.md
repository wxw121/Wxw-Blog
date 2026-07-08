# Next.js 学习系列（三）：服务端组件、服务端 fetch 与 useEffect 对照

核心内容摘录：

## 两种组件
| | Server Component（默认） | Client Component |
| 运行 | Next 服务器 | 浏览器 |
| useState/useEffect | ❌ | ✅ |
| onClick | ❌ | ✅ |
| async await fetch | ✅ | ❌ |
| 典型 | 读数据、拼结构 | 搜索框、表单 |

## 数据流
Server page: await getUsers() → HTML 带列表
Client: 收 users props → 筛选/选中

## 组合规则
1. page 默认 Server → async + await fetch
2. 要交互 → 单独 'use client' 子组件
3. Server 可 import Client；Client 不能 import Server
4. 数据用 props 传 JSON

## 三态 UI
loading.js / try-catch / error.js

## 对照 React（三）
Vite: useEffect fetch → setState → 重绘
Next: 服务器 fetch → 首屏 HTML 已有数据

## 一分钟自检
useState? onClick? window? → Client
只 fetch + map 展示? → Server
