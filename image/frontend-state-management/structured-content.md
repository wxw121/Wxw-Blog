# Structured Content: 前端状态管理完全指南信息图

## Title
前端状态管理：从 useState 到 Zustand、Redux 与 Pinia

## Learning Objectives
1. 区分客户端状态与服务端状态，知道 Query 与 Store 分工
2. 理解单向数据流：视图 → action → reducer → 新 state → 视图
3. 用决策树选择 Zustand / Redux / Pinia / Context / Query

---

## 图1: 客户端 vs 服务端状态（§2）

**Key Concept**: 先按来源切状态，别把接口数据全塞 Redux

**Content**:
| 维度 | 客户端状态 | 服务端状态 |
| 权威来源 | 当前页面 / 用户操作 | 后端 API |
| 是否「过期」 | 一般不过期 | 会过期，需刷新、轮询、失效 |
| 多组件共享 | 常需全局库或 Context | 更宜用 Query/SWR 等请求缓存库 |
| 典型例子 | 主题、侧栏折叠、tab、聊天草稿 | 用户列表、文档索引状态、分页结果 |

左边：主题/侧栏/草稿 ↔ Zustand/Redux/Pinia
右边：列表/详情/任务进度 ↔ TanStack Query ↔ 后端 API

**Visual Element**: binary-comparison, left client state, right server state, center divider

**Text Labels**:
- Headline: "先分清两类状态：客户端 vs 服务端"
- Left: 客户端状态 · Zustand / Redux / Pinia
- Right: 服务端状态 · TanStack Query
- Footer: "先问数据权威在谁那儿"

---

## 图2: 单向数据流（§5.2 / §6）

**Key Concept**: 改状态走固定路径，视图不直接乱改 Store

**Content**:
- 视图 / 组件 → 用户操作 / 发 Action → 按规则更新 Store → 视图 / 组件
- Redux 四件套：Store（唯一大对象）、Action（描述发生了什么）、Reducer（纯函数算新状态）、Dispatch（派发 action）
- 面试叙事：**UI → dispatch(action) → reducer → 新 state → UI 重渲染**

**Visual Element**: linear-progression circular or linear 4-node flow

**Text Labels**:
- Headline: "单向数据流：Redux 核心叙事"
- Nodes: 视图 UI / dispatch(action) / reducer / 新 state
- Footer: "改总账必须走审批流，不能谁都在账本上乱涂"

---

## 图3: 选型决策树（§9.2）

**Key Concept**: 先定框架，再分 Query 痛点与 Store 复杂度

**Content**:
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

**Visual Element**: tree-branching top-down, 4 terminal leaves

**Text Labels**:
- Headline: "Zustand / Redux / Pinia 选型决策树"
- Leaves: Pinia / TanStack Query / Redux Toolkit / Zustand / Context
- Footer: "先分类，再选库"

---

## Design Instructions
- hand-drawn-edu, landscape 16:9, Simplified Chinese
- Macaron pastels, warm cream background, stick figures
