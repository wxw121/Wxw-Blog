# 企业级 AI Agent 工程师 — 知识点清单与学习路线

> 这是 `ENTERPRISE_RAG_ROADMAP.md` 的进阶路线。RAG 解决“如何让模型基于知识回答问题”，Agent 解决“如何让模型基于知识、工具和流程完成任务”。

## 使用方式

按模块学习；每学完一个模块，回到项目实战章节，把能力接入同一个企业知识库 Agent。

这条路线不以某个框架为中心，而是先建立工具、状态、记忆、工作流、审批、观测和安全等通用工程能力，再用主流框架完成实现案例。

## 前置基础

开始本路线前，建议已经掌握：

1. Python、类型注解、异步编程和包管理。
2. REST API、SSE、WebSocket、后台任务和状态机基础。
3. React 或 Next.js、TypeScript 和流式 UI。
4. 文档解析、分块、Embedding、向量库、混合检索和重排序。
5. RAG 引用、评测、可观测、权限、多租户和部署基础。

对应内容已经在 `ENTERPRISE_RAG_ROADMAP.md` 与 1–213 篇教程中覆盖。

## 目标系统

学完第一阶段后，你应该能独立设计并实现：

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

## 学习原则

1. 先判断是否真的需要 Agent，固定流程优先使用普通 Workflow。
2. 先讲模式，再讲框架，避免知识绑定到某个 SDK 版本。
3. 工具调用必须结构化、可校验、可重试、可审计。
4. 高风险动作必须有权限边界和人工确认。
5. 每条 Agent 轨迹必须可观测、可复盘、可评测。
6. 自主性不是越高越好，生产系统优先追求可靠和可控。

## 第一阶段：从 RAG 到可靠 Agent（214–254）

### Part 1：从 RAG 走向 Agent（214–217）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 214 | `214.rag-to-agent-transition-tutorial.md` | 理解 RAG 如何成为 Agent 的知识能力组件 |
| 215 | `215.agent-vs-rag-vs-workflow-tutorial.md` | 区分 Chatbot、RAG、Workflow 与 Agent |
| 216 | `216.when-not-to-use-agent-tutorial.md` | 判断哪些场景不应该使用 Agent |
| 217 | `217.enterprise-agent-architecture-overview-tutorial.md` | 建立企业级 Agent 系统总览 |

完成本模块后，你应该能根据任务确定使用普通 API、Workflow、RAG 还是 Agent。

### Part 2：Tool Calling 工程化（218–225）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 218 | `218.tool-calling-basics-tutorial.md` | 理解工具调用是 Agent 执行动作的核心 |
| 219 | `219.tool-schema-design-tutorial.md` | 设计清晰、稳定、可维护的工具 schema |
| 220 | `220.tool-parameter-validation-tutorial.md` | 使用结构化校验减少错误参数 |
| 221 | `221.tool-result-normalization-tutorial.md` | 统一工具返回格式 |
| 222 | `222.tool-error-timeout-retry-tutorial.md` | 处理失败、超时、重试与降级 |
| 223 | `223.idempotent-agent-tools-tutorial.md` | 设计可安全重试的幂等工具 |
| 224 | `224.human-in-the-loop-agent-tutorial.md` | 为高风险操作加入人工确认 |
| 225 | `225.agent-tool-permission-boundary-tutorial.md` | 建立最小权限和审计边界 |

完成本模块后，你应该能把一个普通业务 API 包装成 Agent 可以安全调用的工具。

### Part 3：Agent Loop 与 Planning（226–231）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 226 | `226.agent-loop-observe-think-act-tutorial.md` | 理解 Observe / Decide / Act 循环 |
| 227 | `227.react-agent-pattern-tutorial.md` | 学习 ReAct 模式及其边界 |
| 228 | `228.plan-and-execute-agent-tutorial.md` | 学习先规划后执行 |
| 229 | `229.reflection-agent-pattern-tutorial.md` | 引入受控反思与自检 |
| 230 | `230.task-decomposition-agent-tutorial.md` | 把复杂任务拆成可执行步骤 |
| 231 | `231.agent-stop-condition-tutorial.md` | 防止无限循环与过度执行 |

完成本模块后，你应该能设计一个有最大步数、失败阈值和明确停止条件的 Agent Loop。

### Part 4：Memory 与上下文（232–237）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 232 | `232.agent-memory-types-tutorial.md` | 区分短期、长期、语义和事件记忆 |
| 233 | `233.short-term-agent-memory-tutorial.md` | 设计会话状态和短期上下文 |
| 234 | `234.long-term-agent-memory-tutorial.md` | 设计长期记忆与用户偏好 |
| 235 | `235.memory-write-policy-tutorial.md` | 决定什么信息应该写入记忆 |
| 236 | `236.memory-retrieval-policy-tutorial.md` | 决定何时取回哪些记忆 |
| 237 | `237.memory-privacy-deletion-tutorial.md` | 处理隐私、删除和可追溯问题 |

完成本模块后，你应该能解释“模型上下文、会话状态、长期记忆和 RAG 知识库”之间的区别。

### Part 5：Agentic RAG（238–243）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 238 | `238.agentic-rag-architecture-tutorial.md` | 设计 Agentic RAG 总体架构 |
| 239 | `239.query-planning-rag-agent-tutorial.md` | 先规划查询再执行检索 |
| 240 | `240.multi-step-retrieval-agent-tutorial.md` | 支持多步检索和上下文补全 |
| 241 | `241.tool-augmented-rag-tutorial.md` | 同时使用检索和业务工具 |
| 242 | `242.rag-agent-citation-verification-tutorial.md` | 验证引用来源与回答一致性 |
| 243 | `243.rag-agent-bad-case-debugging-tutorial.md` | 调试检索失败、幻觉和引用错误 |

完成本模块后，你应该能把固定 RAG 链路升级成受控的查询规划与多步检索系统。

### Part 6：Workflow 与持久化执行（244–249）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 244 | `244.agent-workflow-patterns-tutorial.md` | 区分自由 Agent 与受控 Workflow |
| 245 | `245.state-machine-agent-tutorial.md` | 使用状态机约束 Agent 行为 |
| 246 | `246.agent-checkpoint-resume-tutorial.md` | 支持长任务保存与恢复 |
| 247 | `247.durable-agent-execution-tutorial.md` | 理解可靠执行、重试和故障恢复 |
| 248 | `248.agent-background-job-tutorial.md` | 把耗时任务放入后台队列 |
| 249 | `249.agent-event-driven-architecture-tutorial.md` | 使用事件驱动连接 Agent 与业务系统 |

完成本模块后，你应该能实现支持暂停、人工确认、恢复和失败重试的长任务 Agent。

### Part 7：项目实战（250–254）

| 编号 | 文件名 | 学习目标 |
|---|---|---|
| 250 | `250.build-knowledge-base-agent-tutorial.md` | 构建企业知识库 Agent |
| 251 | `251.build-research-agent-tutorial.md` | 构建资料研究与整理 Agent |
| 252 | `252.build-customer-support-agent-tutorial.md` | 构建客服 Agent |
| 253 | `253.build-code-review-agent-tutorial.md` | 构建代码审查 Agent |
| 254 | `254.build-admin-ops-agent-tutorial.md` | 构建后台运营和管理 Agent |

五个项目共享前六个模块的工程约束，但分别强调知识检索、长任务、业务权限、审查轨迹和高风险确认。

## 第二阶段：生产化扩展（255–274）

### Multi-Agent（255–260）

学习 Supervisor / Worker、Router、Reviewer、共享状态、冲突解决和成本控制。重点判断何时 Multi-Agent 真正优于单 Agent + Workflow。

### Agent Evaluation / Observability / Debugging（261–266）

学习任务完成率、工具调用准确率、轨迹评测、回归测试、Trace、成本、延迟和失败率监控。

### Agent Security / Permission / Deployment / Cost（267–274）

学习 Prompt Injection、Tool Injection、最小权限、沙箱、Secret 管理、审计日志、灰度发布和预算控制。

## 新增技术栈与学习顺序

### 必学

- Tool Calling / Function Calling
- JSON Schema / Pydantic / Zod
- 工具参数校验、返回标准化、错误处理、超时、重试和幂等性
- Human-in-the-loop
- Agent Loop、ReAct、Plan-and-Execute 和停止条件
- 短期记忆、长期记忆、记忆写入策略和记忆检索策略
- Agentic RAG
- Workflow / State Machine
- Checkpoint / Resume
- Durable Execution

### 选学

- OpenAI Agents SDK：Python Agent 实现案例
- LangGraph：Workflow、状态机和持久化执行案例
- MCP：工具、资源和上下文接入协议
- Vercel AI SDK：Next.js Agent UI、工具流式状态和审批 UI
- AutoGen / CrewAI：Multi-Agent 对比案例
- Celery / BullMQ / Temporal / Inngest：长任务和可靠后台执行案例

### 了解

- AutoGPT 类高度自主 Agent
- 复杂 Multi-Agent Debate
- Browser-use / Computer-use 自动操作
- Code Execution Sandbox 深度实现
- Agent 行为自训练与自我改进
- Agent Formal Verification

## 贯穿式项目：企业知识库 Agent

建议读者在学习每个模块后，把能力接入同一个项目：

| 阶段 | 项目增量 |
|---|---|
| Part 1 | 明确 RAG、Workflow 和 Agent 的职责边界 |
| Part 2 | 建立工具注册、参数校验、统一返回和人工确认 |
| Part 3 | 加入规划、执行循环、失败阈值和停止条件 |
| Part 4 | 加入会话状态和受控长期记忆 |
| Part 5 | 加入查询规划、多步检索和引用验证 |
| Part 6 | 加入状态机、Checkpoint、Resume 和后台任务 |
| Part 7 | 完成可运行项目并补齐观测、评测和权限 |

## 单篇文章统一要求

每篇文章必须包含：

```text
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

文章不能只介绍概念。最小示例负责讲清机制，工程化版本负责加入校验、状态、错误处理、权限和可观测性。

## 推荐学习节奏

1. 第一周：214–225，完成边界判断和 Tool Calling。
2. 第二周：226–237，完成 Agent Loop、Planning 和 Memory。
3. 第三周：238–249，完成 Agentic RAG 和持久化 Workflow。
4. 第四周：250–254，完成至少一个项目并复盘失败轨迹。

学习时优先完成 250 的企业知识库 Agent；其他项目用于验证同一套模式能否迁移到不同业务。

## 第一阶段验收标准

完成 214–254 后，学习者应能：

1. 判断一个需求是否需要 Agent。
2. 设计结构化、幂等、可审计的工具。
3. 实现有边界、有停止条件的 Agent Loop。
4. 区分上下文、状态、记忆和知识库。
5. 实现多步 Agentic RAG 并验证引用。
6. 使用状态机、Checkpoint 和后台任务承载长流程。
7. 为高风险动作加入权限校验和人工确认。
8. 记录并评测完整 Agent 执行轨迹。
