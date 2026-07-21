# AI Agent 工程学习路线设计

日期：2026-07-21  
项目：Wxw-Blog  
状态：设计已确认，等待路线文档与文章实施计划

## 1. 背景

当前仓库已经形成一条「企业级 RAG 全栈工程师」学习路线，内容覆盖 Python、后端、前端、文档解析、分块、Embedding、向量库、混合检索、重排序、评测、观测、权限、安全、部署与成本优化。

新的 AI Agent 系列不应另起一条孤立路线，而应作为现有 RAG 路线之后的工程进阶篇：

```text
基础工程能力 → RAG 系统 → Agent 系统 → 多 Agent / 生产化 / 评测治理
```

核心定位：

```text
现有 RAG 路线解决“如何让模型基于知识回答问题”。
新的 Agent 路线解决“如何让模型基于知识、工具和流程完成任务”。
```

## 2. 目标

新增系列要帮助读者从 RAG 工程能力自然过渡到企业级 Agent 工程能力。学习者完成第一期后，应能独立设计并实现一个可控、可调试、可评测的知识库 Agent。

目标系统形态：

```text
用户任务
  → 判断任务类型
  → 规划执行步骤
  → 检索知识库
  → 调用外部工具
  → 必要时请求人工确认
  → 生成带来源的结果
  → 记录执行轨迹
  → 支持评测、复盘与迭代
```

## 3. 设计原则

1. 先讲通用工程能力，再讲具体框架。
2. 以项目主线贯穿知识点，避免单纯堆概念。
3. 保持和当前仓库编号、图片、脚本体系一致。
4. 第一阶段聚焦可靠 Agent，不追求覆盖所有热门框架。
5. 每篇文章都要回答“什么时候不该这么做”。
6. Agent 不是自动化越多越好，生产环境应优先强调边界、权限、观测和人工确认。

## 4. 内容组织方式

沿用当前仓库的根目录编号文章结构，从现有第 213 篇之后继续编号。

建议新增：

```text
AI_AGENT_ENGINEERING_ROADMAP.md
214.rag-to-agent-transition-tutorial.md
215.agent-vs-rag-vs-workflow-tutorial.md
...
```

配图继续沿用现有模式：

```text
image/<article-slug>/
```

不新建复杂的 `agent/` 内容目录，避免破坏当前根目录编号体系。

## 5. 第一阶段文章规划

第一阶段建议覆盖 214–254，共 41 篇左右。重点是从 RAG 到可落地 Agent 的核心工程能力。

### Part 1：从 RAG 走向 Agent

| 编号 | 文件名 | 目标 |
|---|---|---|
| 214 | `214.rag-to-agent-transition-tutorial.md` | 解释 RAG 能力如何成为 Agent 的组成部分 |
| 215 | `215.agent-vs-rag-vs-workflow-tutorial.md` | 区分 Agent、RAG、Workflow、Chatbot |
| 216 | `216.when-not-to-use-agent-tutorial.md` | 说明哪些场景不该使用 Agent |
| 217 | `217.enterprise-agent-architecture-overview-tutorial.md` | 建立企业级 Agent 系统总览 |

### Part 2：Tool Calling 工程化

| 编号 | 文件名 | 目标 |
|---|---|---|
| 218 | `218.tool-calling-basics-tutorial.md` | 理解工具调用是 Agent 执行动作的核心 |
| 219 | `219.tool-schema-design-tutorial.md` | 设计清晰、稳定、可维护的工具 schema |
| 220 | `220.tool-parameter-validation-tutorial.md` | 使用结构化校验减少错误工具调用 |
| 221 | `221.tool-result-normalization-tutorial.md` | 统一工具返回格式，方便 Agent 消费 |
| 222 | `222.tool-error-timeout-retry-tutorial.md` | 处理工具失败、超时、重试与降级 |
| 223 | `223.idempotent-agent-tools-tutorial.md` | 设计可安全重试的工具 |
| 224 | `224.human-in-the-loop-agent-tutorial.md` | 为高风险动作加入人工确认 |
| 225 | `225.agent-tool-permission-boundary-tutorial.md` | 建立工具权限边界 |

### Part 3：Agent Loop 与 Planning

| 编号 | 文件名 | 目标 |
|---|---|---|
| 226 | `226.agent-loop-observe-think-act-tutorial.md` | 理解 Observe / Decide / Act 循环 |
| 227 | `227.react-agent-pattern-tutorial.md` | 学习 ReAct 模式 |
| 228 | `228.plan-and-execute-agent-tutorial.md` | 学习先规划后执行的模式 |
| 229 | `229.reflection-agent-pattern-tutorial.md` | 引入反思与自检，但控制使用边界 |
| 230 | `230.task-decomposition-agent-tutorial.md` | 把复杂任务拆成可执行步骤 |
| 231 | `231.agent-stop-condition-tutorial.md` | 防止 Agent 无限循环或过度执行 |

### Part 4：Memory 与上下文

| 编号 | 文件名 | 目标 |
|---|---|---|
| 232 | `232.agent-memory-types-tutorial.md` | 区分短期、长期、语义、事件记忆 |
| 233 | `233.short-term-agent-memory-tutorial.md` | 设计短期上下文与会话状态 |
| 234 | `234.long-term-agent-memory-tutorial.md` | 设计长期记忆与用户偏好 |
| 235 | `235.memory-write-policy-tutorial.md` | 决定什么信息应该写入记忆 |
| 236 | `236.memory-retrieval-policy-tutorial.md` | 决定什么时候取回哪些记忆 |
| 237 | `237.memory-privacy-deletion-tutorial.md` | 处理隐私、删除、可追溯问题 |

### Part 5：Agentic RAG

| 编号 | 文件名 | 目标 |
|---|---|---|
| 238 | `238.agentic-rag-architecture-tutorial.md` | 设计 Agentic RAG 总体架构 |
| 239 | `239.query-planning-rag-agent-tutorial.md` | 让 Agent 先规划查询再检索 |
| 240 | `240.multi-step-retrieval-agent-tutorial.md` | 支持多步检索与逐步补充上下文 |
| 241 | `241.tool-augmented-rag-tutorial.md` | 让 RAG Agent 同时使用检索与工具 |
| 242 | `242.rag-agent-citation-verification-tutorial.md` | 验证引用来源与回答一致性 |
| 243 | `243.rag-agent-bad-case-debugging-tutorial.md` | 调试检索失败、幻觉和引用错误 |

### Part 6：Workflow 与持久化执行

| 编号 | 文件名 | 目标 |
|---|---|---|
| 244 | `244.agent-workflow-patterns-tutorial.md` | 区分自由 Agent 与受控 Workflow |
| 245 | `245.state-machine-agent-tutorial.md` | 用状态机约束 Agent 行为 |
| 246 | `246.agent-checkpoint-resume-tutorial.md` | 支持长任务保存与恢复 |
| 247 | `247.durable-agent-execution-tutorial.md` | 理解可靠执行、重试和恢复 |
| 248 | `248.agent-background-job-tutorial.md` | 把长耗时任务放入后台执行 |
| 249 | `249.agent-event-driven-architecture-tutorial.md` | 使用事件驱动连接 Agent 与系统 |

### Part 7：项目实战

| 编号 | 文件名 | 目标 |
|---|---|---|
| 250 | `250.build-knowledge-base-agent-tutorial.md` | 从零实现企业知识库 Agent |
| 251 | `251.build-research-agent-tutorial.md` | 实现研究/资料整理 Agent |
| 252 | `252.build-customer-support-agent-tutorial.md` | 实现客服 Agent |
| 253 | `253.build-code-review-agent-tutorial.md` | 实现代码审查 Agent |
| 254 | `254.build-admin-ops-agent-tutorial.md` | 实现后台运营/管理 Agent |

## 6. 第二阶段扩展规划

第二阶段不作为第一期交付范围，但应在路线图中预留。

```text
255–260 Multi-Agent
261–266 Agent Evaluation / Observability / Debugging
267–274 Agent Security / Permission / Deployment / Cost
```

第二阶段重点：

1. Supervisor / Worker / Reviewer 等多 Agent 模式。
2. Agent 轨迹评测、工具调用准确率、任务完成率。
3. Trace、日志、成本、延迟、失败率监控。
4. Prompt Injection、Tool Injection、权限最小化。
5. 沙箱、Secret 管理、审计日志、灰度发布。

## 7. 新增技术栈与学习顺序

### 7.1 必学

这些技术进入第一阶段主线：

| 技术/能力 | 放入模块 |
|---|---|
| Tool Calling / Function Calling | Part 2 |
| JSON Schema / Pydantic / Zod | Part 2 |
| 参数校验与工具返回标准化 | Part 2 |
| 工具错误处理、超时、重试、幂等性 | Part 2 |
| Human-in-the-loop | Part 2、Part 6 |
| Agent Loop | Part 3 |
| ReAct | Part 3 |
| Plan-and-Execute | Part 3 |
| 停止条件与防无限循环 | Part 3 |
| 短期记忆、长期记忆、记忆写入策略 | Part 4 |
| Agentic RAG | Part 5 |
| Workflow / State Machine | Part 6 |
| Checkpoint / Resume | Part 6 |
| Durable Execution | Part 6 |

### 7.2 选学

这些技术作为实现案例或扩展阅读，不作为第一阶段主干：

| 技术 | 定位 |
|---|---|
| OpenAI Agents SDK | Python Agent 实战案例 |
| LangGraph | Workflow、状态机、持久化执行案例 |
| MCP | 工具、资源、上下文接入协议 |
| Vercel AI SDK | Next.js Agent UI、tool streaming、approval UI |
| AutoGen / CrewAI | Multi-Agent 对比案例 |
| Celery / BullMQ / Temporal / Inngest | 长任务与可靠后台执行案例 |

### 7.3 了解

这些内容适合第二阶段或扩展篇：

1. AutoGPT 类高度自主 Agent。
2. 复杂 Multi-Agent Debate。
3. Browser-use / Computer-use 自动操作。
4. Code Execution Sandbox 深度实现。
5. Agent 行为自训练与自我改进。
6. Agent Formal Verification。

## 8. 单篇文章模板

Agent 系列每篇建议保持统一结构：

```text
# 标题

## 你会学到什么
## 它解决什么问题
## 最小示例
## 工程化版本
## 常见失败模式
## 什么时候不要这么做
## 生产环境注意事项
## 如何观测和评测
## 和 RAG / 后端 / 前端的关系
## 面试怎么讲
## 下一步
```

模板重点是避免文章停留在概念介绍。每篇文章都要把能力落到工程边界、失败模式和生产可控性上。

## 9. 图片与素材规划

图片仍使用当前仓库的 `image/<slug>/` 结构。每篇至少规划 1 张核心图，优先使用架构图、流程图、状态图和对比图。

建议常见图型：

1. RAG vs Agent vs Workflow 对比图。
2. Tool Calling 生命周期图。
3. Agent Loop 状态图。
4. Human-in-the-loop 决策流程图。
5. Memory 写入与检索流程图。
6. Agentic RAG 多步检索图。
7. Workflow / State Machine 执行图。
8. Checkpoint / Resume 时序图。
9. 知识库 Agent 项目架构图。

## 10. 交付边界

本设计只确认路线与内容架构，不直接生成 41 篇文章正文。

下一步应先创建或更新：

```text
AI_AGENT_ENGINEERING_ROADMAP.md
README.md 中的 Agent 系列入口
```

然后再按批次生成文章：

1. 第一批：214–217，建立 RAG 到 Agent 的过渡。
2. 第二批：218–225，完成 Tool Calling 工程化。
3. 第三批：226–231，完成 Agent Loop 与 Planning。
4. 第四批：232–243，完成 Memory 与 Agentic RAG。
5. 第五批：244–254，完成 Workflow 与项目实战。

## 11. 风险与控制

| 风险 | 控制方式 |
|---|---|
| 内容变成框架教程 | 先讲模式，再讲框架案例 |
| 文章数量过大导致质量下降 | 分批交付，先完成第一阶段 |
| Agent 概念过玄 | 每篇必须包含最小示例与工程化版本 |
| 忽略生产问题 | 每篇固定包含失败模式、观测、评测和“什么时候不要这么做” |
| 和现有 RAG 路线割裂 | 开头加入 RAG 到 Agent 的桥接章节 |
| 新技术变化太快 | 框架作为案例，不作为主干 |

## 12. 验收标准

设计进入实施前，应满足：

1. 路线定位清楚：RAG 解决基于知识回答，Agent 解决基于知识、工具和流程完成任务。
2. 第一阶段范围明确：214–254。
3. 第二阶段扩展方向明确：255–274。
4. 必学、选学、了解三类技术边界明确。
5. 每篇文章模板统一。
6. 文章编号和素材目录遵循现有仓库习惯。
7. 不在第一阶段强行绑定某个 Agent 框架。

## 13. 后续步骤

用户审核本设计文档后，如确认继续，应进入实施计划阶段：

1. 制定路线文档更新计划。
2. 制定 README 入口更新计划。
3. 制定 214–254 分批生成计划。
4. 制定配图 manifest 与图片占位规划。
5. 按批次生成、审计并修正文稿。
