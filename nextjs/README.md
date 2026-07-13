# Next.js 学习系列（RAG 全栈主栈）

**定位**：以 Next.js App Router 为主线，从 CRUD 底座一路搭到可演示的「知识库助手」前端。**系列 1～12 已全部成篇**；TypeScript、TanStack Query、JWT 等见下方「进阶可选」。

**前置**：至少读完 [React（一）ES6+](../react/01.javascript-es6-quickstart.md)（`fetch`、`async/await`、模块）。不必练 Vite SPA——CRUD 与 RAG 交互均在 Next 系列完成。

**篇幅**：**1～12 篇**正文每篇不少于 **5000 汉字**（不含代码块内的英文标识符）；统计口径为 Unicode 汉字 `[\u4e00-\u9fff]`。

### 篇幅与阅读时长（1～12 篇）

| 篇 | 汉字约 | 仅阅读 | 含动手（建议） | 备注 |
|----|--------|--------|----------------|------|
| [1 选型](01.when-next-vs-vite.md) | 5000+ | 40～60 min | 半天 | 零代码 |
| [2 搭项目](02.create-next-app-first-page.md) | 5000+ | 40～60 min | 1.5～2 h | 两页 |
| [3 数据](03.server-client-fetch.md) | 7800+ | 60～90 min | **4～6 h** | 最厚 |
| [4 POST](04.server-actions-post-create.md) | 5000+ | 40～60 min | 半天 | Actions |
| [5 联调](05.fullstack-next-fastapi.md) | 5000+ | 40～60 min | 半天～1 天 | 双终端 |
| [6 RAG 骨架](06.rag-frontend-skeleton.md) | 5000+ | 40～60 min | 2～3 h | 空壳 |
| [7 流式](07.sse-streaming-chat.md) | 5000+ | 50～70 min | 3～5 h | curl 优先 |
| [8 Markdown](08.markdown-message-render.md) | 5000+ | 45～60 min | 2.5～4 h | layout CSS |
| [9 引用](09.citation-source-ui.md) | 5000+ | 50～70 min | 3～5 h | 双栏 |
| [10 上传](10.file-upload-index-progress.md) | 5000+ | 45～60 min | 3～4.5 h | FormData |
| [11 调试](11.retrieval-debug-console.md) | 5000+ | 40～55 min | 2.5～4 h | 排障 |
| [12 收官](12.ship-rag-frontend.md) | 5000+ | 35～50 min | 2～3.5 h | 演示+build |

「仅阅读」按约 **350 字/分钟**；**含动手**含敲代码、排错、自检与口述练习。

---

## 主线目录（1～12）

| 序号 | 主题 | 线 | 状态 |
|------|------|-----|------|
| 1 | [什么时候选 Next、和 Vite 差在哪](01.when-next-vs-vite.md) | 选型 | ✅ |
| 2 | [create-next-app 与第一个 page](02.create-next-app-first-page.md) | 基础 | ✅ |
| 3 | [服务端组件、服务端 fetch 与 useEffect 对照](03.server-client-fetch.md) | 数据 | ✅ |
| 4 | [Server Actions、POST 创建与表单](04.server-actions-post-create.md) | CRUD | ✅ |
| 5 | [全栈对接：Next + FastAPI](05.fullstack-next-fastapi.md) | CRUD | ✅ |
| 6 | [RAG 前端地图与工程骨架](06.rag-frontend-skeleton.md) | RAG | ✅ |
| 7 | [SSE 流式对话与 AbortController](07.sse-streaming-chat.md) | RAG | ✅ |
| 8 | [Markdown 消息渲染](08.markdown-message-render.md) | RAG | ✅ |
| 9 | [引用溯源 UI](09.citation-source-ui.md) | RAG | ✅ |
| 10 | [文件上传与索引进度](10.file-upload-index-progress.md) | RAG | ✅ |
| 11 | [检索调试台：top-k 与 score](11.retrieval-debug-console.md) | RAG 排障 | ✅ |
| 12 | [收官：路由串联与部署概念](12.ship-rag-frontend.md) | 收束 | ✅ |

配图：`image/nextjs-01-vite-vs-next/` ～ `image/nextjs-09-citation-ui/`（第 1～9 篇，路径 `../image/...`）。第 10～12 篇以 mermaid / 表格为主。

**前置分档**（详见 [第一篇 §8.3](01.when-next-vs-vite.md)）：

| 档位 | 篇章 | 适合 |
|------|------|------|
| 最小 | React（一）ES6+ | Next 主栈跟读 |
| 推荐 | + 粗读 React（三）三态、（四）路由 | 3～5 篇少踩坑 |
| 可选 | React（五）（六）POST / 全栈 | 4～5 篇对照更快 |

---

## 阅读路线

```text
Next 主栈（推荐）：
  React（一）ES6+  →  Next 1～5（CRUD）  →  Next 6～12（RAG 前端闭环）

已有 React/Vite 经验：
  React 1～6 可速览对照  →  Next 1～5 补 App Router  →  Next 6～12

只做 CRUD、不做 RAG：
  Next 1～5 即可停
```

| 路线 | 篇章 | 交付物 |
|------|------|--------|
| CRUD 底座 | 1～5 | 用户列表 / 详情 / Server Action 创建 + FastAPI |
| RAG 演示 UI | 6～10 | 工程骨架 + 流式问答 + Markdown + 引用 + 上传 |
| 可排障 + 可演示 | 11～12 | 检索调试台 + 全路由串联 + 部署心智 |

**收官标准**：按 1→12 练完，能在**同一** `my-fullstack-next/` 项目上交付可演示的 RAG 前端，并对齐 [企业 RAG 路线图](../ENTERPRISE_RAG_ROADMAP.md) 阶段 4 应用层（F2 #188～199）。

---

## 推荐工程目录（第五篇起累积，第六篇定稿）

第六篇起在第五篇的 `frontend/` + `backend/` 上迭代，不每篇新建项目：

```text
my-fullstack-next/
├── backend/
│   └── main.py              # 用户 API → 聊天流 → 上传 → 调试检索（逐篇合并）
└── frontend/                # create-next-app 项目
    └── src/
        ├── lib/             # fetchJSON, sse (readSSEStream)
        ├── components/      # ChatMessage, ChatInput, …
        └── app/
            ├── users/...    # 第三～五篇
            ├── chat/        # 第七篇
            ├── documents/   # 第十篇
            └── debug/
                └── retrieve/  # 第十一篇
```

路由建议：`/users`…（CRUD）→ `/chat` → `/documents` → `/debug/retrieve`。

---

## 与 React 系列的关系

| 能力 | Next 主栈 | React 系列（参考实现） |
|------|-----------|------------------------|
| ES6 / fetch | [React（一）](../react/01.javascript-es6-quickstart.md) | 必读 |
| Vite SPA / Router | 跳过 | 2～6 |
| RAG 交互模式 | **Next 6～11** | 7～13（概念对照，栈不同） |
| TS / TanStack Query | 第十二篇延伸提及 | 11～12 独立成篇 |

React 7～13 保留为 **Vite 栈参考**；Next 读者只需在概念卡住时跳转对照，不必两套都练。

---

## 系列状态

| 阶段 | 篇章 | 状态 | 你能交付什么 |
|------|------|------|--------------|
| **选型 + 基础** | 1～2 | ✅ | 选型、App Router、`'use client'` |
| **CRUD 全栈** | 3～5 | ✅ | RSC 取数、Server Actions、FastAPI 联调 |
| **RAG 骨架** | 6 | ✅ | Server/Client 边界、路由与目录规划 |
| **RAG 演示闭环** | 7～10 | ✅ | 流式 + MD + 引用 + 上传 |
| **排障 + 收束** | 11～12 | ✅ | 调试台 + 演示脚本 + build/部署概念 |

---

## 与仓库其他教程的衔接

| 本系列篇章 | 可对照教程 |
|------------|------------|
| 5、7 SSE | [SSE 教程](../7.sse-tutorial.md)、[REST API](../5.rest-api-design-tutorial.md) |
| 10 上传 | [Docker Compose](../11.docker-compose-tutorial.md)（持久化延伸） |
| 6～12 RAG UI | [企业 RAG 路线图](../ENTERPRISE_RAG_ROADMAP.md) |
| 12 部署 | [Docker Compose](../11.docker-compose-tutorial.md)、[Linux 日志](../12.linux-commands-log-tutorial.md) |

---

## 进阶可选（本系列不单独成篇）

| 主题 | 说明 | 可参考 |
|------|------|--------|
| TypeScript 迁移 | 类型与 `rag.ts` | [React（十一）](../react/11.typescript-migration.md) |
| TanStack Query | 替代手写轮询 | [React（十二）](../react/12.tanstack-query.md) |
| JWT + middleware | 多租户路由 | 路线图 F1 #181；第五篇边界外 |
| Route Handler BFF | `app/api/chat/route.ts` | 第六篇概念 + 第七篇可选 |
| PATCH / 文档管理台 | CRUD 补全 | 第五篇 §12.5 可选续篇 |
