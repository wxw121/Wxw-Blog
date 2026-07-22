# AI Agent 重点文章 Mermaid 临时配图设计

## 背景

AI Agent 工程学习路线已经新增 214～254 共 41 篇文章。其中 7 篇重点文章规划了 PNG 配图，但当前尚未生成位图。仓库已有大量内嵌 Mermaid 图，因此本轮先以 Mermaid 作为可维护、可直接渲染的临时配图，PNG 继续保留为后续视觉升级任务。

## 目标

- 让 7 篇重点文章各有一张与教学目标一致的核心 Mermaid 图。
- 优先修正现有 Mermaid 与配图规划不一致的内容，不做无收益的全量重绘。
- 保持 GitHub Markdown 可直接阅读，不依赖本地图片文件或外部服务。
- 明确 Mermaid 已完成、PNG 延后，避免配图状态混乱。

## 非目标

- 本轮不生成 PNG、SVG 或其他位图文件。
- 不给其余 34 篇 Agent 文章批量补图。
- 不引入 Mermaid CLI、Node.js 依赖或新的构建流程。
- 不统一改造仓库内历史 Mermaid 的配色和样式。

## 方案选择

采用“针对性完善”方案：保留已经符合教学目标的图，只修改信息缺失或与原图计划不一致的图。

未采用的方案：

- 仅更新待办状态：改动最小，但会保留 214、238、244 与规划不一致的问题。
- 全部统一重绘：视觉更统一，但会制造不必要的内容改动和 Mermaid 兼容风险。

## 修改范围

### 214：RAG 到 Agent 的能力跃迁

文件：`214.rag-to-agent-transition-tutorial.md`

将现有单一路由流程改为左右对照架构：

- RAG 路径：用户问题 → 检索 → 证据 → 生成答案。
- Agent 路径：用户任务 → Orchestrator → Policy → Tool Registry → Observation → 停止判断。
- 高风险动作进入 Human Confirmation，普通结果直接返回。

图的核心结论是：RAG 主要产生有依据的回答，Agent 在受控循环中推进任务并可能产生外部副作用。

### 215：API、RAG、Workflow 与 Agent 选型

文件：`215.agent-vs-rag-vs-workflow-tutorial.md`

保留现有决策树。它已经覆盖结构化规则、知识回答、固定步骤和动态工具选择四个判断维度。只做必要的中文标签一致性检查，不调整结构。

### 218：Tool Calling 基础

文件：`218.tool-calling-basics-tutorial.md`

保留现有时序图。调用顺序继续为：模型提出工具调用 → Orchestrator 做 Schema Validation → Policy 做权限检查 → Tool 执行 → 结果归一化与脱敏 → Observation 返回模型。

### 226：Agent Loop

文件：`226.agent-loop-observe-think-act-tutorial.md`

保留现有循环图。它已经包含 Load State、Check Budget、Decide、Validate、Act、Record Observation、Complete 和 Finalize，能够表达预算约束与停止条件。

### 238：Agentic RAG 架构

文件：`238.agentic-rag-architecture-tutorial.md`

在现有架构上补全失败闭环：

- Citation Verification 通过后进入 Final Answer。
- 验证失败进入 Bad Case Debugging。
- 调试结果携带诊断信息回到 Query Planning，触发受限重试。
- 图中保留 Retrieval Tool、Evidence Store 和证据充分性判断。

重试必须表达为有边界的回路，文章正文继续负责说明预算和停止条件。

### 244：Agent Workflow 模式

文件：`244.agent-workflow-patterns-tutorial.md`

将现有路由图扩展为可恢复工作流：

- 输入首先进入确定性 Workflow。
- Agent Node 只负责受限分类或决策。
- RAG Branch 和 Ticket Branch 汇合后写入 Checkpoint。
- 高风险动作进入 Human Approval 并暂停。
- 批准后通过 Resume 返回工作流；拒绝或低风险路径进入 Finalize。

图必须明确 State、Transition、Checkpoint、Human Approval 和 Resume 的关系。

### 250：知识库 Agent 项目架构

文件：`250.build-knowledge-base-agent-tutorial.md`

保留现有总体架构，拆分 `Checkpoint / Trace` 组合节点：

- Checkpoint 表达可恢复状态。
- Trace 表达调用链、指标和审计记录。
- Orchestrator 分别写入两者，避免把恢复机制和观测机制混为一个职责。

## 配图状态管理

更新以下 7 份文件：

- `image/rag-to-agent-transition/README.md`
- `image/agent-vs-rag-vs-workflow/README.md`
- `image/tool-calling-basics/README.md`
- `image/agent-loop-observe-think-act/README.md`
- `image/agentic-rag-architecture/README.md`
- `image/agent-workflow-patterns/README.md`
- `image/build-knowledge-base-agent/README.md`

每份 README 增加统一状态：内嵌 Mermaid 临时图已经完成；目标 PNG 仍未生成，未来替换时不得删除文章中的结构说明。

`pending-images.txt` 中 7 条 PNG 待办继续保留，仍使用现有 UTF-16LE BOM 编码。Mermaid 是临时交付，不等价于 PNG 已完成。

## 兼容性约束

- 使用 GitHub 支持的 `flowchart` 或 `sequenceDiagram` 基础语法。
- 不依赖外部图标、HTML 标签、自定义字体或实验性 Mermaid 特性。
- 节点标识使用 ASCII；显示文本可以使用中文或现有英文术语。
- 节点文本保持短句，复杂解释留在正文，避免移动端渲染过宽。
- 每篇重点文章只保留一张承担核心教学任务的主图。

## 数据与内容流

Mermaid 代码直接存放在对应 Markdown 文章中，由 GitHub 或兼容 Markdown 渲染器读取。`image/*/README.md` 只记录未来 PNG 的视觉目标和当前临时图状态，不复制 Mermaid 源码，避免出现双份真相。

## 异常处理

- 若 Mermaid 语法无法通过结构检查，必须在提交前修正，不能退化为无法渲染的普通代码块。
- 若图与正文描述冲突，以已确认的本设计为准同步修改图；不扩大正文主题。
- 若某个渲染器不支持中文标点或特殊标签，优先简化标签，不引入构建依赖。
- `pending-images.txt` 更新时必须显式按 Unicode 方式读取，并验证 BOM 仍为 `FF FE`。

## 验证标准

- 7 篇重点文章每篇至少包含一个 `mermaid` 代码块。
- 所有 Markdown 代码围栏数量为偶数。
- Mermaid 块均以 `flowchart` 或 `sequenceDiagram` 开头并正常闭合。
- 214 同时出现 RAG 路径与 Agent 路径。
- 218 的时序图包含 Schema Validation、Permission Check、Tool Execution 和 Observation。
- 226 包含预算检查、循环回边和停止判断。
- 238 包含 Query Planning、Retrieval Tool、Citation Verification、Bad Case Debugging 及失败回路。
- 244 包含 Agent Node、Checkpoint、Human Approval 和 Resume。
- 250 将 Checkpoint 与 Trace 表达为独立节点。
- 7 份图片 README 都标记 Mermaid 已完成、PNG 延后。
- `pending-images.txt` 的 7 条 PNG 待办仍存在，编码保持 UTF-16LE BOM。
- `git diff --check` 通过，除原有 `.tmp/` 外工作区没有意外文件。

## 交付顺序

1. 修改 214、238、244、250 的 Mermaid 图。
2. 复核但不无谓重写 215、218、226。
3. 更新 7 份图片 README 的临时状态。
4. 验证 Mermaid 结构、Markdown 围栏和图片待办编码。
5. 提交 Mermaid 配图改进。
6. 完成全部验证后，将本地 `main` 推送到 `origin/main`。
