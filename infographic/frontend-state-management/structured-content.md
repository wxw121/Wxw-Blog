# Structured Content: 前端状态管理完全指南信息图

## Title
前端状态管理：从 useState 到 Zustand、Redux 与 Pinia

## Learning Objectives
The viewer will understand:
1. 客户端状态与服务端状态的区别及各自归宿
2. 遇到问题该用 useState、Context、全局库还是 TanStack Query
3. 按框架与痛点选型：Pinia / Redux / Zustand / Query

---

## 图1: 客户端 vs 服务端状态分工（§2）

**Key Concept**: 先问数据权威在谁那儿——左边 Zustand/Redux/Pinia，右边 TanStack Query

**Content**:
- **客户端状态**：由浏览器端产生、主要服务于 UI 交互；权威来源：当前页面/用户操作；一般不过期；典型：主题/侧栏/当前会话草稿
- **服务端状态**：权威数据在服务器，前端取副本展示，会过期；典型：用户列表、文档索引状态、分页搜索结果
- 左边：UI ↔ Zustand / Redux / Pinia
- 右边：UI ↔ TanStack Query ↔ 后端 API
- 企业 RAG：`documents` 列表走 Query，`currentThreadId` 或 UI 布局走 Zustand

**Visual Element**:
- Type: hub-spoke with two side-by-side hubs
- Subject: 客户端状态圈 vs 服务端状态圈
- Treatment: 中心标语「先问：权威在谁那儿？」，左右两圈各连 UI 与工具

**Text Labels**:
- Headline: "两类状态：客户端 vs 服务端"
- Left hub: "客户端状态" / "Zustand · Redux · Pinia"
- Right hub: "服务端状态" / "TanStack Query → API"
- Footer: "左边管 UI 会话；右边管接口缓存与轮询"

---

## 图2: 综合概念地图（§11）

**Key Concept**: 把「状态放在哪」串成一张表

**Content**（表格 verbatim）:
| 你遇到的问题 | 概念 / 工具 | 记住一句 |
| 只有一个组件用 | `useState` | 别过度设计 |
| 兄弟组件联动 | 提升状态 | 共同父组件记账 |
| 深层只读配置 | Context / provide-inject | 读多写少 |
| 多页面共享 UI 状态 | Zustand / Pinia / Redux | 单一数据源 |
| 接口列表与缓存 | TanStack Query | 服务端状态专家 |
| 可分享、可刷新保留 | URL 路由参数 | 书签即状态 |
| 改状态要走流程 | Action → Reducer | Redux 核心叙事 |
| 从 store 取一片 | Selector / getter | 少重渲染 |

**Visual Element**:
- Type: bento-grid with 8 compact module cells
- Subject: 2×4 grid, each cell = 问题 + 工具 + 一句口诀
- Treatment: macaron pastel cards, code in doodle monospace

**Text Labels**:
- Headline: "综合概念地图：状态放在哪"
- Subhead: "先分类，再选库"
- Footer: "前端状态管理完全指南 · §11"

---

## 图3: 选型决策树（§9.2）

**Key Concept**: 按框架与痛点选型，可组合不必单选

**Content**（决策树 verbatim）:
```
你的框架是 Vue 3？
├─ 是 → 需要全局客户端状态？→ Pinia
└─ 否（React）→ 痛点主要是接口缓存/轮询？
    ├─ 是 → TanStack Query（+ 可选 Zustand 管 UI）
    └─ 否 → 状态复杂且团队要严格 action 追溯？
        ├─ 是 → Redux Toolkit
        └─ 否 → 想要最少代码？→ Zustand
            └─ 状态很少、仅主题/用户？→ Context 也许够
```

**Visual Element**:
- Type: tree-branching decision tree top to bottom
- Subject: Vue 分支 vs React 分支
- Treatment: coral highlight on recommended paths (Query + Zustand combo)

**Text Labels**:
- Headline: "选型决策树：该用哪个库"
- Bottom note: "React 常见组合：Query 管 documents + Zustand 管 UI"
- Footer: "前端状态管理完全指南 · §9"
