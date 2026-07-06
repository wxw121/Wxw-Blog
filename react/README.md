# React 学习系列

前端 React 教程（中文 Markdown + 配图），建议按序号阅读。完整路线：**基础 1～2 → 数据与 CRUD 3～6 → RAG 演示 7～10 → 工程化 11～12 → 排障 13**。

## 主线目录（1～13）

| 序号 | 主题 | 线 | 下一篇 |
|------|------|-----|--------|
| 1 | [JavaScript ES6+ 快速入门](01.javascript-es6-quickstart.md) | 基础 | → [2](02.vite-jsx-first-component.md) |
| 2 | [Vite + JSX + 第一个组件与 useState](02.vite-jsx-first-component.md) | 基础 | → [3](03.use-effect-data-fetching.md) |
| 3 | [useEffect 与接口请求、加载态与数据流](03.use-effect-data-fetching.md) | 数据 | → [4](04.react-router-list-detail.md) |
| 4 | [React Router：列表与 `/users/:id` 详情](04.react-router-list-detail.md) | CRUD | → [5](05.forms-post-create-user.md) |
| 5 | [受控表单与 POST：创建用户](05.forms-post-create-user.md) | CRUD | → [6](06.fullstack-vite-fastapi.md) |
| 6 | [全栈对接：Vite + FastAPI](06.fullstack-vite-fastapi.md) | CRUD | → [7](07.sse-streaming-chat.md) |
| 7 | [SSE 流式对话与 AbortController](07.sse-streaming-chat.md) | RAG | → [8](08.markdown-message-render.md) |
| 8 | [Markdown 消息渲染](08.markdown-message-render.md) | RAG | → [9](09.citation-source-ui.md) |
| 9 | [引用溯源 UI](09.citation-source-ui.md) | RAG | → [10](10.file-upload-index-progress.md) |
| 10 | [文件上传与索引进度](10.file-upload-index-progress.md) | RAG | → [11](11.typescript-migration.md) |
| 11 | [TypeScript 迁移：类型与 RAG 模型](11.typescript-migration.md) | 工程化 | → [12](12.tanstack-query.md) |
| 12 | [TanStack Query：请求缓存与轮询](12.tanstack-query.md) | 工程化 | → [13](13.retrieval-debug-console.md) |
| 13 | [检索调试台：top-k 与 score](13.retrieval-debug-console.md) | RAG 排障 | 系列收束 |

配图目录：`image/react-javascript/`（仅第一篇）。第二篇起以 mermaid / 表格为主。

---

## 系列状态

| 阶段 | 篇章 | 状态 | 你能交付什么 |
|------|------|------|--------------|
| **基础** | 1～2 | ✅ | ES6+ 语法、Vite 组件与 `useState` |
| **数据 + CRUD** | 3～6 | ✅ | `useEffect` 三态、路由、POST 创建、FastAPI 联调 |
| **RAG 演示闭环** | 7～10 | ✅ | 流式聊天、Markdown、引用侧栏、上传与索引进度 |
| **工程化** | 11～12 | ✅ | TS 类型、`useQuery` / `useMutation` 替代手写轮询 |
| **RAG 排障** | 13 | ✅ | 检索调试台看 top-k / score |

**收官标准**：按 1→13 练完，能搭可演示的「知识库助手」前端，并对齐 [企业 RAG 路线图](../ENTERPRISE_RAG_ROADMAP.md) 阶段 4 的应用层。

---

## 阅读路线

```text
初学者全栈：     1 → 2 → 3 → 4 → 5 → 6
冲 RAG 产品：      1～6 可速览 → 7 → 8 → 9 → 10 → 11 → 12 → 13
已有 JS 基础：    2 起读；会 Vue 可从 3 起
只做 CRUD 不做 RAG：1 → 6 即可停，7 起按需
```

| 路线 | 篇章 | 交付物 |
|------|------|--------|
| CRUD 最小产品 | 1～6 | 用户列表 / 详情 / 创建 + 真 API |
| RAG 演示 UI | 7～10 | 流式问答 + Markdown + 引用 + 上传 |
| 可维护 + 排障 | 11～13 | 类型安全、Query 缓存、检索调试台 |

**RAG 前端闭环**（七～十）：流式对话 → Markdown → 引用溯源 → 文件上传。

### Next.js 主栈读者（推荐）

若以 **Next 为 RAG 全栈前端主栈**，不必走完本系列 Vite 路线：

```text
React（一）ES6+  →  Next 1～12（见 nextjs/README.md）
```

| 本系列 | Next 主栈是否必读 | 说明 |
|--------|-------------------|------|
| 1 ES6+ | ✅ 必读 | `fetch`、模块、解构 |
| 2～6 Vite CRUD | ⏭ 可跳过 | 由 Next 1～5 覆盖 |
| 7～13 RAG UI | 📖 概念对照 | 交互相同；实现见 [Next 6～12](../nextjs/README.md) |

**对照参考**：[Next.js 学习系列](../nextjs/README.md)（RAG 主栈；1～5 CRUD + 6～12 RAG 前端）。

---

## 推荐工程目录（第六篇起累积，第十篇 §8.0 详述）

第七～十篇默认在**同一** Vite `frontend/` 与 FastAPI `backend/` 上迭代，而非每篇新建项目：

```text
my-fullstack/
├── backend/
│   └── main.py          # 用户 API + 聊天流 + 上传 + 调试检索（逐篇合并）
└── frontend/
    └── src/
        ├── utils/       # fetchJSON, readSSEStream
        ├── hooks/       # useDocumentPoll（第十篇）；Query hooks（第十二篇）
        ├── components/  # Chat*, Markdown*, Citation*, Upload*, Document*
        ├── pages/       # ChatPage, DocumentsPage, RetrieveDebugPage
        └── types/       # rag.ts（第十一篇）
```

路由建议：`/users`、`/users/new`、`/users/:id`（第四～六篇）→ `/chat`（第七篇）→ `/documents`（第十篇）→ `/debug/retrieve`（第十三篇）。

---

## 与仓库其他教程的衔接

| 本系列篇章 | 可对照的后端 / 专题教程 |
|------------|-------------------------|
| 1 §10 `fetch` | [REST API 设计](../5.rest-api-design-tutorial.md)、[asyncio](../3.python-asyncio-tutorial.md) |
| 3～6 CRUD | [REST API](../5.rest-api-design-tutorial.md)、第六篇 FastAPI |
| 10 上传索引 | [Docker Compose](../11.docker-compose-tutorial.md)、[PostgreSQL](../8.postgresql-tutorial.md)（持久化延伸） |
| 7～13 RAG UI | [企业 RAG 路线图](../ENTERPRISE_RAG_ROADMAP.md) |

---

## 进阶可选（未单独成篇）

以下在多篇「可选延伸」里提过，需要时再查其他教程或自行扩展：

| 主题 | 说明 | 可参考 |
|------|------|--------|
| JWT 登录 | `Authorization` 头、登录页 | 路线图 F1 #181；[第六篇 §12.5](06.fullstack-vite-fastapi.md) |
| Zustand 全局状态 | 多会话、跨路由共享 | 路线图 A#21；[第七篇 §12.5](07.sse-streaming-chat.md) |
| PATCH / DELETE 用户 | CRUD 补全 | [第五篇 §12.5](05.forms-post-create-user.md) |
| 重建索引按钮 | 文档管理台 | [第十篇](10.file-upload-index-progress.md) + 后端任务 API |
| 管理台 / 用量统计 | 阶段 5 | 路线图 F2 #200～201 |
| PDF 页内高亮 | 加分项 | 路线图 F2 #195 |
| 前端生产部署 | `build`、Nginx | [Docker Compose 教程](../11.docker-compose-tutorial.md) |
| Next.js 全栈 | SSR、Server Actions | [nextjs/README.md](../nextjs/README.md) |
