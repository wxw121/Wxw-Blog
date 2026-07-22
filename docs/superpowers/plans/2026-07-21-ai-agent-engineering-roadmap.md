# AI Agent Engineering Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new AI Agent engineering learning route to Wxw-Blog, connected to the existing enterprise RAG route and prepared for 214–254 article generation.

**Architecture:** The rollout is documentation-first. First create a canonical roadmap, then expose it from `README.md`, then generate article batches that follow one shared template and the existing root-level numbered Markdown convention. Image work stays aligned with the existing `image/rag-to-agent-transition/` style asset directories and `scripts/` maintenance model.

**Tech Stack:** Markdown, PowerShell, Git, existing Wxw-Blog root article layout, existing `image/` asset layout, existing `scripts/` image maintenance workflow.

## Global Constraints

- Continue from the existing article sequence after `213.rlhf-dpo-rag-tutorial.md`.
- First-stage AI Agent article range is `214` through `254`.
- Second-stage reserved range is `255` through `274`.
- Keep root-level numbered tutorial files instead of creating a new `agent/` article directory.
- Keep image directories under explicit slug paths such as `image/rag-to-agent-transition/`, `image/tool-calling-basics/`, and `image/build-knowledge-base-agent/`.
- Add a top-level route document named `AI_AGENT_ENGINEERING_ROADMAP.md`.
- Do not touch the existing untracked `.tmp/` directory.
- Do not bind the first-stage route to one Agent framework; frameworks appear as implementation cases.
- Every article must include a section named `## 什么时候不要这么做`.
- Every article must include engineering boundaries: failure modes, production notes, observability or evaluation, and relation to RAG/backend/frontend.

---

## File Structure

### Create

- `AI_AGENT_ENGINEERING_ROADMAP.md` — canonical AI Agent learning roadmap and new technology stack map.
- `214.rag-to-agent-transition-tutorial.md` through `254.build-admin-ops-agent-tutorial.md` — first-stage article files.
- `image/rag-to-agent-transition/README.md`, `image/agent-vs-rag-vs-workflow/README.md`, `image/tool-calling-basics/README.md`, `image/agent-loop-observe-think-act/README.md`, `image/agentic-rag-architecture/README.md`, `image/agent-workflow-patterns/README.md`, and `image/build-knowledge-base-agent/README.md` when image planning starts.

### Modify

- `README.md` — add an AI Agent engineering series entry after the enterprise RAG route reference.
- `pending-images.txt` — append image needs for new Agent articles only when image requests are planned.
- `image/manifest.json` and `image/_inventory.json` — update only through the existing scripts once image assets are planned or generated.

### Reference

- `docs/superpowers/specs/2026-07-21-ai-agent-engineering-roadmap-design.md` — approved design.
- `ENTERPRISE_RAG_ROADMAP.md` — existing route this new series extends.
- `scripts/README.md` — current image maintenance workflow.

---

### Task 1: Create the AI Agent Roadmap

**Files:**
- Create: `AI_AGENT_ENGINEERING_ROADMAP.md`
- Reference: `docs/superpowers/specs/2026-07-21-ai-agent-engineering-roadmap-design.md`
- Reference: `ENTERPRISE_RAG_ROADMAP.md`

**Interfaces:**
- Consumes: approved design sections 1–12.
- Produces: canonical route document used by README and all article batches.

- [ ] **Step 1: Write the roadmap title and positioning**

  Create `AI_AGENT_ENGINEERING_ROADMAP.md` with this opening:

  ```markdown
  # 企业级 AI Agent 工程师 — 知识点清单与学习路线

  > 这是 `ENTERPRISE_RAG_ROADMAP.md` 的进阶路线。RAG 解决“如何让模型基于知识回答问题”，Agent 解决“如何让模型基于知识、工具和流程完成任务”。

  ## 使用方式

  按模块学习；每学完一个模块，回到项目实战章节，把能力接入同一个企业知识库 Agent。
  ```

- [ ] **Step 2: Add the target system section**

  Add this exact target system flow:

  ````markdown
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
  ````

- [ ] **Step 3: Add the learning stages**

  Add these first-stage headings in this order:

  ```markdown
  ## 第一阶段：从 RAG 到可靠 Agent（214–254）

  ### Part 1：从 RAG 走向 Agent（214–217）
  ### Part 2：Tool Calling 工程化（218–225）
  ### Part 3：Agent Loop 与 Planning（226–231）
  ### Part 4：Memory 与上下文（232–237）
  ### Part 5：Agentic RAG（238–243）
  ### Part 6：Workflow 与持久化执行（244–249）
  ### Part 7：项目实战（250–254）

  ## 第二阶段：生产化扩展（255–274）

  ### Multi-Agent（255–260）
  ### Agent Evaluation / Observability / Debugging（261–266）
  ### Agent Security / Permission / Deployment / Cost（267–274）
  ```

- [ ] **Step 4: Add the technology stack map**

  Add a section named `## 新增技术栈与学习顺序` with three subsections:

  ```markdown
  ### 必学
  - Tool Calling / Function Calling
  - JSON Schema / Pydantic / Zod
  - 工具参数校验、返回标准化、错误处理、超时、重试、幂等性
  - Human-in-the-loop
  - Agent Loop、ReAct、Plan-and-Execute、停止条件
  - 短期记忆、长期记忆、记忆写入策略、记忆检索策略
  - Agentic RAG
  - Workflow / State Machine
  - Checkpoint / Resume
  - Durable Execution

  ### 选学
  - OpenAI Agents SDK
  - LangGraph
  - MCP
  - Vercel AI SDK
  - AutoGen / CrewAI
  - Celery / BullMQ / Temporal / Inngest

  ### 了解
  - AutoGPT 类高度自主 Agent
  - 复杂 Multi-Agent Debate
  - Browser-use / Computer-use 自动操作
  - Code Execution Sandbox 深度实现
  - Agent 行为自训练与自我改进
  - Agent Formal Verification
  ```

- [ ] **Step 5: Add the complete article table**

  Copy the 214–254 filenames from the approved spec into one Markdown table with columns `编号`, `文件名`, `模块`, `学习目标`.

- [ ] **Step 6: Verify the roadmap file exists and contains all required ranges**

  Run:

  ```powershell
  Test-Path AI_AGENT_ENGINEERING_ROADMAP.md
  rg -n "214|254|255|274|新增技术栈|什么时候不要这么做" AI_AGENT_ENGINEERING_ROADMAP.md
  ```

  Expected:

  ```text
  True
  ```

  The `rg` command must show at least one match for each searched concept.

- [ ] **Step 7: Commit Task 1**

  Run:

  ```powershell
  git add AI_AGENT_ENGINEERING_ROADMAP.md
  git commit -m "docs: add ai agent engineering roadmap"
  ```

---

### Task 2: Add the AI Agent Entry to README

**Files:**
- Modify: `README.md`
- Reference: `AI_AGENT_ENGINEERING_ROADMAP.md`

**Interfaces:**
- Consumes: Task 1 roadmap path.
- Produces: discoverable top-level entry for readers.

- [ ] **Step 1: Insert the AI Agent route after the existing route references**

  In `README.md`, after the paragraph that references `nextjs/README.md`, `react/README.md`, and `scripts/README.md`, add:

  ```markdown

  ## AI Agent 工程学习路线

  见 [AI_AGENT_ENGINEERING_ROADMAP.md](AI_AGENT_ENGINEERING_ROADMAP.md)。这条路线衔接现有 RAG 全栈内容，重点学习 Tool Calling、Agent Loop、Memory、Agentic RAG、Workflow、人类确认、观测评测与安全边界。
  ```

- [ ] **Step 2: Verify the README link**

  Run:

  ```powershell
  rg -n "AI Agent 工程学习路线|AI_AGENT_ENGINEERING_ROADMAP.md|Tool Calling" README.md
  Test-Path AI_AGENT_ENGINEERING_ROADMAP.md
  ```

  Expected: `rg` prints three matching lines, and `Test-Path` prints `True`.

- [ ] **Step 3: Commit Task 2**

  Run:

  ```powershell
  git add README.md
  git commit -m "docs: link ai agent roadmap from readme"
  ```

---

### Task 3: Generate Bridge Articles 214–217

**Files:**
- Create: `214.rag-to-agent-transition-tutorial.md`
- Create: `215.agent-vs-rag-vs-workflow-tutorial.md`
- Create: `216.when-not-to-use-agent-tutorial.md`
- Create: `217.enterprise-agent-architecture-overview-tutorial.md`
- Reference: `AI_AGENT_ENGINEERING_ROADMAP.md`
- Reference: `ENTERPRISE_RAG_ROADMAP.md`

**Interfaces:**
- Consumes: Task 1 roadmap and existing RAG route.
- Produces: conceptual bridge from RAG to Agent used by all later articles.

- [ ] **Step 1: Apply the shared article template to all four files**

  Each file must contain these headings in this order:

  ```markdown
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

- [ ] **Step 2: Draft `214.rag-to-agent-transition-tutorial.md`**

  Required thesis:

  ```text
  RAG 是 Agent 的知识获取能力之一；Agent 在 RAG 之上增加任务判断、工具调用、流程控制、人类确认和执行轨迹。
  ```

  Required minimal example:

  ```python
  def answer_with_rag(question: str) -> str:
      docs = retrieve(question)
      return generate_answer(question, docs)

  def agent_answer(task: str) -> str:
      if needs_retrieval(task):
          docs = retrieve(task)
      if needs_tool(task):
          tool_result = call_tool(task)
      return generate_final(task, docs, tool_result)
  ```

- [ ] **Step 3: Draft `215.agent-vs-rag-vs-workflow-tutorial.md`**

  Required comparison table rows:

  ```markdown
  | 形态 | 核心能力 | 适合场景 | 主要风险 |
  |---|---|---|---|
  | Chatbot | 对话生成 | FAQ、陪伴式问答 | 无法稳定执行动作 |
  | RAG | 基于知识回答 | 企业知识库、文档问答 | 检索失败和引用错误 |
  | Workflow | 固定流程执行 | 审批、工单、批处理 | 灵活性低 |
  | Agent | 动态规划与工具调用 | 多步骤任务、半结构化任务 | 不可控、成本高、权限风险 |
  ```

- [ ] **Step 4: Draft `216.when-not-to-use-agent-tutorial.md`**

  Required list:

  ```markdown
  ## 不该使用 Agent 的场景

  1. 规则稳定、流程固定，用普通 Workflow 更清晰。
  2. 输入输出完全结构化，用普通 API 更可靠。
  3. 操作风险高但没有人工确认机制。
  4. 无法记录工具调用和中间步骤。
  5. 成本或延迟预算很紧。
  ```

- [ ] **Step 5: Draft `217.enterprise-agent-architecture-overview-tutorial.md`**

  Required architecture components:

  ```text
  User Interface
  Agent Orchestrator
  Planner
  Tool Registry
  RAG Retriever
  Memory Store
  Human Approval
  Trace / Evaluation
  Permission Boundary
  ```

- [ ] **Step 6: Verify bridge article structure**

  Run:

  ```powershell
  rg -n "## 什么时候不要这么做" 214.rag-to-agent-transition-tutorial.md 215.agent-vs-rag-vs-workflow-tutorial.md 216.when-not-to-use-agent-tutorial.md 217.enterprise-agent-architecture-overview-tutorial.md
  rg -n "RAG|Agent|Workflow|Human|Tool" 214.rag-to-agent-transition-tutorial.md 215.agent-vs-rag-vs-workflow-tutorial.md 216.when-not-to-use-agent-tutorial.md 217.enterprise-agent-architecture-overview-tutorial.md
  ```

  Expected: first command prints four matches. Second command prints matches in all four files.

- [ ] **Step 7: Commit Task 3**

  Run:

  ```powershell
  git add 214.rag-to-agent-transition-tutorial.md 215.agent-vs-rag-vs-workflow-tutorial.md 216.when-not-to-use-agent-tutorial.md 217.enterprise-agent-architecture-overview-tutorial.md
  git commit -m "docs: add rag to agent bridge articles"
  ```

---

### Task 4: Generate Tool Calling Articles 218–225

**Files:**
- Create: `218.tool-calling-basics-tutorial.md`
- Create: `219.tool-schema-design-tutorial.md`
- Create: `220.tool-parameter-validation-tutorial.md`
- Create: `221.tool-result-normalization-tutorial.md`
- Create: `222.tool-error-timeout-retry-tutorial.md`
- Create: `223.idempotent-agent-tools-tutorial.md`
- Create: `224.human-in-the-loop-agent-tutorial.md`
- Create: `225.agent-tool-permission-boundary-tutorial.md`

**Interfaces:**
- Consumes: bridge concepts from Task 3.
- Produces: tool design rules used by Agent Loop, Agentic RAG, and project articles.

- [ ] **Step 1: Apply the shared article template to all eight files**

  Use the exact heading list from Task 3 Step 1.

- [ ] **Step 2: Include required code examples**

  Each file must include at least one fenced code block. Use these minimum examples:

  ```python
  from pydantic import BaseModel, Field

  class SearchToolInput(BaseModel):
      query: str = Field(min_length=1, max_length=200)
      top_k: int = Field(default=5, ge=1, le=20)
  ```

  ```json
  {
    "ok": true,
    "data": {"items": []},
    "error": null,
    "trace_id": "tool-call-001"
  }
  ```

- [ ] **Step 3: Include permission boundary language in `225`**

  Required sentence:

  ```text
  Agent 能看到工具，不代表 Agent 应该拥有工具背后的全部权限。
  ```

- [ ] **Step 4: Verify Tool Calling coverage**

  Run:

  ```powershell
  rg -n "Tool Calling|schema|Pydantic|幂等|人工确认|权限" 218.*.md 219.*.md 220.*.md 221.*.md 222.*.md 223.*.md 224.*.md 225.*.md
  rg -n "## 什么时候不要这么做" 218.*.md 219.*.md 220.*.md 221.*.md 222.*.md 223.*.md 224.*.md 225.*.md
  ```

  Expected: the second command prints eight matches.

- [ ] **Step 5: Commit Task 4**

  Run:

  ```powershell
  git add 218.tool-calling-basics-tutorial.md 219.tool-schema-design-tutorial.md 220.tool-parameter-validation-tutorial.md 221.tool-result-normalization-tutorial.md 222.tool-error-timeout-retry-tutorial.md 223.idempotent-agent-tools-tutorial.md 224.human-in-the-loop-agent-tutorial.md 225.agent-tool-permission-boundary-tutorial.md
  git commit -m "docs: add agent tool calling articles"
  ```

---

### Task 5: Generate Agent Loop and Planning Articles 226–231

**Files:**
- Create: `226.agent-loop-observe-think-act-tutorial.md`
- Create: `227.react-agent-pattern-tutorial.md`
- Create: `228.plan-and-execute-agent-tutorial.md`
- Create: `229.reflection-agent-pattern-tutorial.md`
- Create: `230.task-decomposition-agent-tutorial.md`
- Create: `231.agent-stop-condition-tutorial.md`

**Interfaces:**
- Consumes: Tool Calling rules from Task 4.
- Produces: execution patterns used by Memory, Agentic RAG, Workflow, and project articles.

- [ ] **Step 1: Apply the shared article template to all six files**

  Use the exact heading list from Task 3 Step 1.

- [ ] **Step 2: Include the core loop diagram text**

  At least one article must contain:

  ```text
  Observe → Decide → Act → Observe
  ```

- [ ] **Step 3: Include the stop condition checklist in `231`**

  Required checklist:

  ```markdown
  ## 停止条件清单

  - 达到最大步骤数。
  - 工具连续失败超过阈值。
  - 已经得到可验证答案。
  - 需要人工确认。
  - 当前任务超出权限边界。
  ```

- [ ] **Step 4: Verify planning coverage**

  Run:

  ```powershell
  rg -n "Observe|Decide|Act|ReAct|Plan|Reflection|停止条件|人工确认" 226.*.md 227.*.md 228.*.md 229.*.md 230.*.md 231.*.md
  rg -n "## 什么时候不要这么做" 226.*.md 227.*.md 228.*.md 229.*.md 230.*.md 231.*.md
  ```

  Expected: the second command prints six matches.

- [ ] **Step 5: Commit Task 5**

  Run:

  ```powershell
  git add 226.agent-loop-observe-think-act-tutorial.md 227.react-agent-pattern-tutorial.md 228.plan-and-execute-agent-tutorial.md 229.reflection-agent-pattern-tutorial.md 230.task-decomposition-agent-tutorial.md 231.agent-stop-condition-tutorial.md
  git commit -m "docs: add agent loop and planning articles"
  ```

---

### Task 6: Generate Memory and Agentic RAG Articles 232–243

**Files:**
- Create: `232.agent-memory-types-tutorial.md`
- Create: `233.short-term-agent-memory-tutorial.md`
- Create: `234.long-term-agent-memory-tutorial.md`
- Create: `235.memory-write-policy-tutorial.md`
- Create: `236.memory-retrieval-policy-tutorial.md`
- Create: `237.memory-privacy-deletion-tutorial.md`
- Create: `238.agentic-rag-architecture-tutorial.md`
- Create: `239.query-planning-rag-agent-tutorial.md`
- Create: `240.multi-step-retrieval-agent-tutorial.md`
- Create: `241.tool-augmented-rag-tutorial.md`
- Create: `242.rag-agent-citation-verification-tutorial.md`
- Create: `243.rag-agent-bad-case-debugging-tutorial.md`

**Interfaces:**
- Consumes: existing RAG articles 91–154 and Agent Loop articles 226–231.
- Produces: advanced RAG-Agent integration patterns.

- [ ] **Step 1: Apply the shared article template to all twelve files**

  Use the exact heading list from Task 3 Step 1.

- [ ] **Step 2: Include memory policy table in memory articles**

  Each memory article must include a table with these columns:

  ```markdown
  | 信息类型 | 是否写入记忆 | 原因 | 删除策略 |
  |---|---|---|---|
  ```

- [ ] **Step 3: Include Agentic RAG architecture terms in 238–243**

  Each Agentic RAG article must mention:

  ```text
  Query Planning
  Retrieval Tool
  Citation Verification
  Bad Case Debugging
  ```

- [ ] **Step 4: Verify Memory and Agentic RAG coverage**

  Run:

  ```powershell
  rg -n "记忆|Memory|写入策略|删除策略|Query Planning|Citation Verification|Bad Case" 232.*.md 233.*.md 234.*.md 235.*.md 236.*.md 237.*.md 238.*.md 239.*.md 240.*.md 241.*.md 242.*.md 243.*.md
  rg -n "## 什么时候不要这么做" 232.*.md 233.*.md 234.*.md 235.*.md 236.*.md 237.*.md 238.*.md 239.*.md 240.*.md 241.*.md 242.*.md 243.*.md
  ```

  Expected: the second command prints twelve matches.

- [ ] **Step 5: Commit Task 6**

  Run:

  ```powershell
  git add 232.agent-memory-types-tutorial.md 233.short-term-agent-memory-tutorial.md 234.long-term-agent-memory-tutorial.md 235.memory-write-policy-tutorial.md 236.memory-retrieval-policy-tutorial.md 237.memory-privacy-deletion-tutorial.md 238.agentic-rag-architecture-tutorial.md 239.query-planning-rag-agent-tutorial.md 240.multi-step-retrieval-agent-tutorial.md 241.tool-augmented-rag-tutorial.md 242.rag-agent-citation-verification-tutorial.md 243.rag-agent-bad-case-debugging-tutorial.md
  git commit -m "docs: add memory and agentic rag articles"
  ```

---

### Task 7: Generate Workflow and Project Articles 244–254

**Files:**
- Create: `244.agent-workflow-patterns-tutorial.md`
- Create: `245.state-machine-agent-tutorial.md`
- Create: `246.agent-checkpoint-resume-tutorial.md`
- Create: `247.durable-agent-execution-tutorial.md`
- Create: `248.agent-background-job-tutorial.md`
- Create: `249.agent-event-driven-architecture-tutorial.md`
- Create: `250.build-knowledge-base-agent-tutorial.md`
- Create: `251.build-research-agent-tutorial.md`
- Create: `252.build-customer-support-agent-tutorial.md`
- Create: `253.build-code-review-agent-tutorial.md`
- Create: `254.build-admin-ops-agent-tutorial.md`

**Interfaces:**
- Consumes: all earlier Agent articles.
- Produces: production-shaped examples and project-based learning outcomes.

- [ ] **Step 1: Apply the shared article template to all eleven files**

  Use the exact heading list from Task 3 Step 1.

- [ ] **Step 2: Include workflow control vocabulary in 244–249**

  Each workflow article must mention:

  ```text
  State
  Transition
  Checkpoint
  Resume
  Human Approval
  ```

- [ ] **Step 3: Include project architecture sections in 250–254**

  Each project article must include these headings:

  ```markdown
  ## 项目目标
  ## 系统架构
  ## 数据流
  ## 工具设计
  ## 权限与确认
  ## 评测与观测
  ```

- [ ] **Step 4: Verify Workflow and project coverage**

  Run:

  ```powershell
  rg -n "State|Transition|Checkpoint|Resume|Human Approval|项目目标|系统架构|权限与确认" 244.*.md 245.*.md 246.*.md 247.*.md 248.*.md 249.*.md 250.*.md 251.*.md 252.*.md 253.*.md 254.*.md
  rg -n "## 什么时候不要这么做" 244.*.md 245.*.md 246.*.md 247.*.md 248.*.md 249.*.md 250.*.md 251.*.md 252.*.md 253.*.md 254.*.md
  ```

  Expected: the second command prints eleven matches.

- [ ] **Step 5: Commit Task 7**

  Run:

  ```powershell
  git add 244.agent-workflow-patterns-tutorial.md 245.state-machine-agent-tutorial.md 246.agent-checkpoint-resume-tutorial.md 247.durable-agent-execution-tutorial.md 248.agent-background-job-tutorial.md 249.agent-event-driven-architecture-tutorial.md 250.build-knowledge-base-agent-tutorial.md 251.build-research-agent-tutorial.md 252.build-customer-support-agent-tutorial.md 253.build-code-review-agent-tutorial.md 254.build-admin-ops-agent-tutorial.md
  git commit -m "docs: add agent workflow and project articles"
  ```

---

### Task 8: Plan Image Directories and Pending Image Requests

**Files:**
- Create: `image/rag-to-agent-transition/README.md`
- Create: `image/agent-vs-rag-vs-workflow/README.md`
- Create: `image/tool-calling-basics/README.md`
- Create: `image/agent-loop-observe-think-act/README.md`
- Create: `image/agentic-rag-architecture/README.md`
- Create: `image/agent-workflow-patterns/README.md`
- Create: `image/build-knowledge-base-agent/README.md`
- Modify: `pending-images.txt`

**Interfaces:**
- Consumes: generated articles from Tasks 3–7.
- Produces: initial image request plan compatible with existing image workflow.

- [ ] **Step 1: Create seven initial image README files**

  Use these exact README contents:

  ```markdown
  # rag-to-agent-transition image plan

  Purpose: one core teaching visual for 214.rag-to-agent-transition-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/rag-to-agent-transition/rag-to-agent-transition.png
  ```

  ```markdown
  # agent-vs-rag-vs-workflow image plan

  Purpose: one core teaching visual for 215.agent-vs-rag-vs-workflow-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/agent-vs-rag-vs-workflow/agent-vs-rag-vs-workflow.png
  ```

  ```markdown
  # tool-calling-basics image plan

  Purpose: one core teaching visual for 218.tool-calling-basics-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/tool-calling-basics/tool-calling-basics.png
  ```

  ```markdown
  # agent-loop-observe-think-act image plan

  Purpose: one core teaching visual for 226.agent-loop-observe-think-act-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/agent-loop-observe-think-act/agent-loop-observe-think-act.png
  ```

  ```markdown
  # agentic-rag-architecture image plan

  Purpose: one core teaching visual for 238.agentic-rag-architecture-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/agentic-rag-architecture/agentic-rag-architecture.png
  ```

  ```markdown
  # agent-workflow-patterns image plan

  Purpose: one core teaching visual for 244.agent-workflow-patterns-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/agent-workflow-patterns/agent-workflow-patterns.png
  ```

  ```markdown
  # build-knowledge-base-agent image plan

  Purpose: one core teaching visual for 250.build-knowledge-base-agent-tutorial.md.

  Required visual:
  - Type: architecture or flow diagram
  - Style: consistent with existing Wxw-Blog tutorial images
  - Text language: Chinese
  - Output path: image/build-knowledge-base-agent/build-knowledge-base-agent.png
  ```

- [ ] **Step 2: Append image requests to `pending-images.txt`**

  Append seven lines, one per initial image:

  ```text
  image/rag-to-agent-transition/rag-to-agent-transition.png
  image/agent-vs-rag-vs-workflow/agent-vs-rag-vs-workflow.png
  image/tool-calling-basics/tool-calling-basics.png
  image/agent-loop-observe-think-act/agent-loop-observe-think-act.png
  image/agentic-rag-architecture/agentic-rag-architecture.png
  image/agent-workflow-patterns/agent-workflow-patterns.png
  image/build-knowledge-base-agent/build-knowledge-base-agent.png
  ```

- [ ] **Step 3: Verify image planning files**

  Run:

  ```powershell
  Test-Path image/rag-to-agent-transition/README.md
  rg -n "image/rag-to-agent-transition|image/build-knowledge-base-agent" pending-images.txt
  ```

  Expected: `Test-Path` prints `True`, and `rg` prints both pending image lines.

- [ ] **Step 4: Commit Task 8**

  Run:

  ```powershell
  git add pending-images.txt image/rag-to-agent-transition/README.md image/agent-vs-rag-vs-workflow/README.md image/tool-calling-basics/README.md image/agent-loop-observe-think-act/README.md image/agentic-rag-architecture/README.md image/agent-workflow-patterns/README.md image/build-knowledge-base-agent/README.md
  git commit -m "docs: plan ai agent tutorial images"
  ```

---

### Task 9: Final Route Audit

**Files:**
- Verify: `AI_AGENT_ENGINEERING_ROADMAP.md`
- Verify: `README.md`
- Verify: `214.*.md` through `254.*.md`
- Verify: `pending-images.txt`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: final confirmation that the AI Agent first-stage route is discoverable and structurally complete.

- [ ] **Step 1: Verify article count**

  Run:

  ```powershell
  $files = Get-ChildItem -File | Where-Object { $_.Name -match '^(21[4-9]|22[0-9]|23[0-9]|24[0-9]|25[0-4])\..*\.md$' }
  $files.Count
  ```

  Expected:

  ```text
  41
  ```

- [ ] **Step 2: Verify required article heading coverage**

  Run:

  ```powershell
  rg -l "## 什么时候不要这么做" 214.*.md 215.*.md 216.*.md 217.*.md 218.*.md 219.*.md 220.*.md 221.*.md 222.*.md 223.*.md 224.*.md 225.*.md 226.*.md 227.*.md 228.*.md 229.*.md 230.*.md 231.*.md 232.*.md 233.*.md 234.*.md 235.*.md 236.*.md 237.*.md 238.*.md 239.*.md 240.*.md 241.*.md 242.*.md 243.*.md 244.*.md 245.*.md 246.*.md 247.*.md 248.*.md 249.*.md 250.*.md 251.*.md 252.*.md 253.*.md 254.*.md | Measure-Object
  ```

  Expected count: `41`.

- [ ] **Step 3: Verify route discoverability**

  Run:

  ```powershell
  rg -n "AI_AGENT_ENGINEERING_ROADMAP.md|AI Agent 工程学习路线" README.md
  rg -n "214|254|第二阶段|必学|选学|了解" AI_AGENT_ENGINEERING_ROADMAP.md
  ```

  Expected: both commands print matching lines.

- [ ] **Step 4: Verify Git status before handoff**

  Run:

  ```powershell
  git status --short --branch
  ```

  Expected: the first line contains `## main...origin/main [ahead `, and the output includes `?? .tmp/`. The only untracked path should be the pre-existing `.tmp/` directory.

- [ ] **Step 5: Commit final audit notes if a report file is created**

  If a final audit report is saved at `audit-ai-agent-roadmap-report.md`, use:

  ```powershell
  git add audit-ai-agent-roadmap-report.md
  git commit -m "docs: add ai agent roadmap audit"
  ```

  If no audit report file is saved, do not create an empty commit.
