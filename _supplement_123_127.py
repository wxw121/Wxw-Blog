#!/usr/bin/env python3
"""Add large Chinese prose blocks to reach >=5000 hanzi per tutorial."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# Large supplemental paragraphs keyed by file prefix, inserted before ## N+1
SUPPLEMENTS = {
    "123": {
        3: """
### 3.5 企业落地中的「两类消费者」

结构化 JSON 的消费者通常分 **人** 与 **机**。人通过前端读 `answer` 字段，机通过工单系统读 `severity`、`intent` 或 `cited_chunk_ids`。若只服务人，纯文本加 [113 行内引用](113.inline-citation-tutorial.md) 往往够用；一旦 **审核台、SLA 报表、自动评测** 上线，没有 schema 就会被迫写脆弱正则。PoC 阶段可以推迟 JSON，但 **产品 PRD 里只要出现「字段」「枚举」「对接 OA」**，就应在本篇阶段引入 Pydantic 模型，而不是等到接口联调周才发现模型输出不可 parse。

### 3.6 与 [35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md) 的契约

同一套 `messages` 可同时服务 **纯文本** 与 **json_schema** 两种调用——差别仅在 `response_format` 与 `temperature`。建议团队维护 **一个** `build_rag_messages()`（[110 模板](110.rag-prompt-template-tutorial.md)），生成侧用参数开关结构化，避免 fork 两套 prompt 导致 Grounding 规则漂移。
""",
        6: """
### 6.4 system 输出契约完整范例

```text
【身份】你是企业内部知识库助手。
【Grounding】仅根据用户消息中【参考资料】回答；不得编造。
【输出格式】你必须输出单一 JSON 对象，字段：answer, refusal, refusal_reason, confidence, citations。
禁止 markdown 代码块，禁止 JSON 前后的解释文字。
【拒答】资料不足时 refusal=true，refusal_reason=INSUFFICIENT_EVIDENCE，answer 用一句话说明。
【引用】citations 每项含 chunk_id 与 quote（quote 不超过 200 字）。
```

把 **输出格式** 与 **Grounding** 写在同一 system，减少模型「说得对但格式错」的概率。user 侧仍用 [111 注入格式](111.context-injection-format-tutorial.md)，不要把 chunk 改成 JSON 塞进 system。

### 6.5 A/B 测试：要不要 Few-shot JSON 行？

对照组 A：仅 schema + response_format；对照组 B：加 §6.2 单行示例。指标：**parse 一次通过率** 与 **citation_recall**。若 A 已 ≥98%，Few-shot 可删以省 [28 窗口](28.context-window-tutorial.md) token；若 B 显著优，保留单行即可，切忌堆多个示例。
""",
        10: """
### 10.9 场景：工单系统读 severity 但模型常漏

**现象**：合规队列依赖 `severity` 枚举，模型经常不给或给字符串。  
**对**：`required` 含 severity；strict schema；金标含高/中/低边界问法；漏字段走 §7 修复或拒答。

### 10.10 场景：国内网关无 strict

**现象**：仅 `json_object`，枚举经常越界。  
**对**：Pydantic 校验 + 业务层映射非法枚举到默认值；runbook 写明与 OpenAI strict 的行为差异，避免测试环境绿、生产环境红。
""",
        12: """
### 12.21 为何「几乎 JSON」比纯文本更危险？

纯文本 parse 失败一眼可见；「几乎 JSON」会 **静默丢字段**，前端用默认值渲染，造成 **假置信**。因此 production 必须 **fail closed**：校验失败走拒答 JSON，而不是部分字段硬展示。

### 12.22 与 [124 工具](124.function-calling-tool-use-tutorial.md) 的终答分工

工具循环中间步骤不需要 RagAnswer schema；**最后一轮** 无 tool_calls 时再要求 json_schema。中间 tool_result 保持精简 hits 列表即可，避免模型在工具参数里塞答案 JSON。
""",
    },
    "124": {
        1: """
### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 工具声明 | tools / functions | JSON Schema 描述可调用能力 |
| 工具循环 | tool loop | LLM 与执行器多轮直到终答 |
| 工具结果 | tool message | role=tool 回灌检索片段 |
| 迭代上限 | max_iterations | 防无限循环烧 token |

### 1.3 读完本篇的最小交付物

1. `search_kb` schema 与 `execute_fn` 实现；  
2. `run_tool_loop` 含 max_iterations 与日志；  
3. ACL 与 [122 安全](122.content-safety-filter-tutorial.md) 接入 args 与 hits；  
4. 能对比 **固定 RAG** 与 **工具 RAG** 的适用场景；  
5. 能口述与 [127 Retriever](127.langchain-retriever-tutorial.md) 的 `as_tool` 关系。
""",
        3: """
### 3.2 与固定 RAG 管道的对照

| 步骤 | 固定 RAG（[126 LCEL](126.langchain-lcel-tutorial.md)） | 工具 RAG（本篇） |
|------|--------------------------------------------------------|------------------|
| 检索时机 | 链入口固定 retriever | 模型决定何时 `search_kb` |
| 检索次数 | 通常 1 次 | 1～max_iterations 次 |
| query 来源 | 用户原问或 [109 增强](109.conversation-query-enhancement-tutorial.md) | 模型生成的 standalone query |
| 成本 | 一次 LLM | 多轮 LLM + 多次检索 |
| 可解释性 | 日志固定 | 需记每轮 tool_name/args |

**选型建议**：员工 FAQ、单意图制度问答 → 固定 RAG；跨文档对比、先列目录再搜、计算后检索 → 工具 RAG。

### 3.3 消息形态与 [30 角色](30.prompt-roles-tutorial.md)

工具循环中除 system/user 外，还有 **assistant（含 tool_calls）** 与 **tool** 两种角色。它们不是「聊天记忆」，而是 **动作与观测**：assistant 表示模型意图，tool 表示环境反馈。调试时把四轮消息 dump 出来，比只看最终 answer 更容易发现 **该搜未搜** 或 **args 错**。
""",
        5: """
### 5.3 错误回灌格式

工具内部异常不要抛栈到用户；应返回：

```json
{"error": "RETRIEVAL_TIMEOUT", "message": "知识库检索超时，请稍后重试"}
```

模型可能据此缩短答案或建议用户换问法。错误码进日志与 on-call 看板，与 [122](122.content-safety-filter-tutorial.md) 的 `SAFETY_BLOCK` 一样可统计。

### 5.4 与 [118 多轮](118.multi-turn-history-tutorial.md) 的关系

多轮对话时 **每轮用户新消息** 可重新进入工具循环；不要把上一轮 tool_result 当永久资料。历史用于理解指代（[120 指代](120.coreference-resolution-tutorial.md)），检索仍应 **针对当前 standalone query**。
""",
        6: """
### 6.4 list_docs 与 get_chunk 的配合

多库场景先 `list_docs` 让模型选 `doc_id`，再 `search_kb` 带 `doc_id` 过滤——比一次全库搜更准，也更省 [28 窗口](28.context-window-tutorial.md)。`get_chunk` 在 snippet 不够时拉全文，对齐 [65 父文档](65.parent-document-retriever-tutorial.md)「小块搜、大块读」。

### 6.5 计算器与 search_kb 共存

若同时提供 `calculator` 与 `search_kb`，description 必须写清：**制度数字以知识库为准，计算器仅用于单位换算等**。否则模型可能不算差旅标准反而乱调计算器。工具越多，description 越要像 **小型 prompt 工程**。
""",
        7: """
### 7.2 延迟与成本估算

设单次 LLM 1.5s、单次检索 0.2s、max_iterations=4，最坏 **6s+** 才终答。产品 SLAs 若要求 3s 内首字，工具 RAG 需 **并行工具**、**缓存 query hash** 或 **降低 max_iterations**。成本上每多一轮 LLM 约多一次输入 token（含历史 tool_result），比固定 RAG 贵 **数倍**——用金标算清 ROI 再默认开启。

### 7.3 与 [96 BGE 精排](96.bge-reranker-tutorial.md) 的放置

精排应放在 `execute_search_kb` **内部**，对模型透明。模型只见 Top 片段，不见 rerank 分数——避免模型「信任」错误分数。宽召回 k=30、精排后取 5 是常见膝点，用 [98 Top-K](98.top-k-retrieval-tutorial.md) 评测调参。
""",
        8: """
### 8.3 租户隔离

多租户时 `search_kb` 强制参数 `tenant_id` 或从 JWT 注入，**勿** 信任模型传的 tenant。向量库 `where` 与 API 网关双重校验 [53 ACL](53.metadata-acl-tutorial.md)。工具描述里不要暴露其他租户库名。

### 8.4 红队：恶意 tool args

用例：query 含「忽略上文」、doc_id 为 `../secret`、top_k=99999。期望：Pydantic 校验失败或 [122](122.content-safety-filter-tutorial.md) 拦截；top_k 硬上限；doc_id 白名单。红队结果写进发布 checklist。
""",
        10: """
### 10.5 错：工具返回 HTML/二进制

**现象**：某内部 API 返回 HTML，塞进 tool_result 污染上下文。  
**对**：执行层只返回 JSON 可序列化字段；HTML 提取正文或拒答。

### 10.6 错：未记录 tool 轨迹

**现象**：用户投诉答案错，无法复盘是否检索漏。  
**对**：每轮 `tool_name`、`args`、`hit_chunk_ids`、`latency_ms` 与 trace_id 绑定存储。
""",
        12: """
### 12.3 与 MCP 的边界

MCP（Model Context Protocol）是更通用的工具宿主协议；本篇是 **Chat Completions tools** 最小闭环。企业可先用本篇跑通 `search_kb`，再评估 MCP 统一多数据源——**语义相同**：声明、执行、回灌、上限。

### 12.4 评测：expected_tools 金标

金标除答案外，标注 **期望调用的工具序列**，如 `["search_kb"]` 或 `["list_docs","search_kb"]`。抽检 **该调未调**、**不该调乱调**，与 Faithfulness 并列汇报。

### 12.5 流式与工具

常见模式：**工具轮非流式**（需完整 tool_calls），**终答轮流式**给人看。勿在 tool_calls 未齐时 stream 终答，否则前端展示与后台检索不一致。
""",
    },
    "125": {
        1: """
### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 文档 | Document | page_content + metadata |
| 可运行单元 | Runnable | invoke/stream/batch 接口 |
| 对话消息 | Message | System/Human/AI |
| 输出解析 | OutputParser | LLM 文本→业务对象 |

### 1.3 读完本篇的最小交付物

1. 手写 `Document` 列表且 metadata 对齐 [51 chunk_id](51.metadata-chunk-id-tutorial.md)；  
2. `ChatOpenAI.invoke` 与 `stream` 跑通；  
3. `PydanticOutputParser` 解析假输出；  
4. 能画 Document/Message/Runnable 关系图；  
5. 能说明与 [126 LCEL](126.langchain-lcel-tutorial.md) 的衔接点。
""",
        3: """
### 3.3 包结构：core 与集成包

```text
langchain-core        # Document, Runnable, Message, Prompt 基类
langchain-openai      # ChatOpenAI, OpenAIEmbeddings
langchain-chroma      # Chroma VectorStore
langchain-community   # FAISS 等社区集成
```

生产 **显式依赖** 需要的集成包，避免 `pip install langchain` 大杂烩导致版本冲突。锁版本后 CI 跑 §9 最小链，升级先过回归。

### 3.4 与 C 模块概念一一映射

| C 模块手写 | langchain-core |
|------------|----------------|
| `{"role":"system","content":...}` | `SystemMessage` |
| chunk dict | `Document` |
| `openai.chat.completions.create` | `ChatOpenAI.invoke` |
| 管道函数组合 | `Runnable` / 下篇 LCEL `|` |

先手写再 core 复刻，你会知道 **框架替你做的是什么**——主要是类型与胶水，不是魔法。
""",
        4: """
### 4.4 Document 批量与 [67 批处理](67.embedding-batching-tutorial.md)

入库时把 `list[Document]` 按批送 Embedding，避免逐条 API。`page_content` 参与向量化；`metadata` 不参与但进向量库过滤。空 `page_content` 的 Document 应跳过，否则污染索引。

### 4.5 与 [52 source/page](52.metadata-source-page-tutorial.md) 溯源

推荐 metadata 最小集：`chunk_id`, `doc_id`, `source`, `page`, `section`, `acl_group`。与 [115 导航](115.source-document-navigation-tutorial.md) 对接时，`source`+`page` 映射 PDF URL，**不要** 把 URL 塞进 `page_content` 重复占 token。
""",
        5: """
### 5.4 AIMessage 与 tool_calls 预告

`llm.invoke` 返回 `AIMessage`，除 `content` 外可能有 `tool_calls` 字段——供 [124 工具](124.function-calling-tool-use-tutorial.md) 使用。RAG 纯问答通常只读 `content`；Agent 链要整消息 append 回历史。

### 5.5 多模态（了解）

部分 ChatModel 支持图片 Message；企业制度 RAG 仍以文本 Document 为主。图片 chunk 见 [56 多模态](56.multimodal-image-text-tutorial.md)，超出本篇边界。
""",
        6: """
### 6.4 RunnableConfig 与观测

```python
chain.invoke(
    {"question": "年假？"},
    config={"tags": ["rag", "handbook"], "metadata": {"user_id": "u1"}},
)
```

`tags`/`metadata` 供 LangSmith 164 过滤 trace。即使暂未接 LangSmith，也应 **预留 config**，避免日后改所有 invoke 签名。

### 6.5 RunnableBinding

`llm.bind(temperature=0)` 或 `bind_tools([...])` 返回新 Runnable，原 llm 不变——便于同一 model 实例派生 **JSON 链** 与 **工具链** 两条配置。
""",
        7: """
### 7.2 JsonOutputParser 与 Pydantic 选型

| Parser | 特点 |
|--------|------|
| `StrOutputParser` | 只要字符串 |
| `JsonOutputParser` | 解析 JSON 为 dict |
| `PydanticOutputParser` | dict → 验证后模型 |

与 [123 JSON Mode](123.structured-output-json-tutorial.md) 配合时，优先 API `response_format`，Parser 作兼容层。

### 7.3 解析失败处理

Parser 抛错时，捕获后返回 [112 拒答](112.refusal-strategy-tutorial.md) 话术或走修复 LLM——逻辑同 123 篇 §7，不要直接把异常栈返回用户。
""",
        8: """
### 8.2 团队分工建议

| 小组 | 用 LC core？ | 原因 |
|------|-------------|------|
| 算法 PoC | 是 | 快速接 OpenAI/Chroma |
| 平台检索 | 部分 | Document 类型统一，检索核心自研 |
| 安全合规 | 否 | 自研闸，不信框架默认 |
| 前端 | 否 | 消费 API JSON（123） |

面试答「我们用 LangChain」时，应补充 **用到哪一层**，而不是二元是/否。
""",
        10: """
### 10.5 错：混用 0.x 与 1.x 文档

**现象**：网上旧例 `from langchain import X` 报错。  
**对**：以 **langchain-core** 官方文档为准；旧 import 对照迁移表。

### 10.6 错：在 Document 上挂非标准属性

**现象**：`doc.foo = 1` 下游 Retriever 丢失。  
**对**：一切进 `metadata` 字典。
""",
        12: """
### 12.8 LangChain 与 LlamaIndex 何时提？

LlamaIndex 偏 **索引与查询引擎** 抽象；LangChain 偏 **Composable Runnable**。路线图 D 模块两篇都「了解」即可，选型看团队已有资产与招聘栈，见 [152 取舍](152.pipeline-vs-framework-tutorial.md)。

### 12.9 如何单测 ChatModel？

用 `FakeListChatModel` 或 mock `invoke` 返回固定 `AIMessage`，避免单测打真 API。集成测试再打真链，金标三条即可。
""",
    },
    "126": {
        1: """
### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| LCEL | LangChain Expression Language | Runnable 的 `|` 组合语法 |
| 管道 | Chain | 多 Runnable 顺序连接 |
| 并行 | RunnableParallel | 多路同输入并行 |
| 透传 | RunnablePassthrough | 保留 dict 并 assign 新键 |

### 1.3 读完本篇的最小交付物

1. `prompt | llm` 最小链 invoke 成功；  
2. `RunnablePassthrough.assign` 组装 context 的 RAG 链；  
3. `stream` 与 `invoke` 各测一次；  
4. `format_docs` 有单测；  
5. 能把 `fake_retrieve` 换成 [127](127.langchain-retriever-tutorial.md) retriever。
""",
        3: """
### 3.2 LCEL 与手写 invoke 等价性

手写：

```python
x = {"question": q}
docs = retriever.invoke(x["question"])
x["context"] = format_docs(docs)
msgs = rag_prompt.invoke(x)
out = llm.invoke(msgs)
```

LCEL：`chain.invoke({"question": q})`。二者 **无性能魔法**，LCEL 价值在 **可读、可观测、可组合**。复杂分支（空检索拒答）可用 `RunnableBranch` 或链外 if。

### 3.3 与 LangGraph 的边界

LCEL 适合 **DAG 管道**；需要 **循环 Agent**（工具多轮）时用 LangGraph（路线图 150 了解）。RAG 问答主链通常 LCEL 足够；Agent 是超集。
""",
        4: """
### 4.3 调试：print 中间 dict

开发期在 `assign` 之间插 `RunnableLambda(lambda x: (print(x.keys()), x)[1])` 看键流转——粗暴但有效。生产删除。

### 4.4 输入 schema 文档化

在团队 wiki 写清链入口 dict：`question: str` 必填，`chat_history: list` 可选，`user_id: str` 给 ACL Lambda。键名与 [110 模板](110.rag-prompt-template-tutorial.md) 变量表一致。
""",
        5: """
### 5.3 MessagesPlaceholder 与多轮

```python
ChatPromptTemplate.from_messages([
    ("system", "..."),
    MessagesPlaceholder("chat_history"),
    ("human", "【参考资料】\\n{context}\\n\\n【用户问题】\\n{question}"),
])
```

多轮时 `chat_history` 放 Human/AI 对，**资料区仍每轮刷新**（[118 多轮](118.multi-turn-history-tutorial.md)），勿复用旧 context。

### 5.4 System 长度与 [107 预算](107.context-budget-tutorial.md)

`ChatPromptTemplate` 渲染后计 token；system 过长挤压 evidence。模板版本变更后 **重算预算**，见 110 篇。
""",
        6: """
### 6.3 RunnableLambda 的错误处理

```python
def safe_format(docs):
    if not docs:
        return ""
    return format_docs(docs)

RunnableLambda(safe_format)
```

空列表返回空串，配合链外拒答，避免 prompt 出现「【参考资料】\\n\\n」空白区仍调 LLM 幻觉。

### 6.4 子链命名

```python
retrieval = RunnablePassthrough.assign(docs=retriever) | RunnablePassthrough.assign(context=format_docs)
generation = rag_prompt | llm | StrOutputParser()
chain = retrieval | generation  # 若类型匹配需适配
```

实际常把 retrieval 与 generation **包成两个 invoke**，中间插入 rerank——见 127 篇。
""",
        7: """
### 7.3 接 [96 精排](96.bge-reranker-tutorial.md) Lambda

```python
def rerank_step(x: dict) -> dict:
    x["docs"] = bge_rerank(x["question"], x["docs"])[:5]
    return x

chain = (
    RunnablePassthrough.assign(docs=retriever)
    | RunnableLambda(rerank_step)
    | RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))
    | rag_prompt | llm
)
```

精排在 assign context **之前**，保证进 prompt 的是 rerank 后顺序。

### 7.4 与 [123 JSON](123.structured-output-json-tutorial.md) 链尾

```python
chain = ... | llm.with_structured_output(RagAnswer)  # 若集成支持
# 或
chain = ... | llm | PydanticOutputParser(pydantic_object=RagAnswer)
```
""",
        8: """
### 8.3 SSE 事件映射表

| LCEL stream chunk | SSE event |
|-------------------|-----------|
| 首 token | `delta` |
| 流结束 | `done` |
| 引用列表 | `citations`（建议在 done 前单独事件） |

与 [116 SSE](116.sse-rag-streaming-tutorial.md) 团队约定一致，前端才好做渐进式引用。

### 8.4 首字延迟优化

`stream` 不减少总 token，但 **首 token 提前**。若 retriever 慢，可先返回「检索中」SSE 状态事件，再开始 llm stream——产品体验层优化，与 LCEL 正交。
""",
        10: """
### 10.5 错：在链里做重 IO 无超时

**现象**：Retriever 卡死，整链 hang。  
**对**：Retriever 外包超时；失败返回空 docs 走拒答。

### 10.6 错：batch 误用

**现象**：对用户实时问答误 `batch`。  
**对**：batch 用于离线评测；在线用 invoke/stream。
""",
        12: """
### 12.9 ainvoke 与 FastAPI

```python
@app.post("/rag")
async def rag(q: str):
    return await rag_chain.ainvoke({"question": q})
```

全异步需 retriever、llm 均支持 async；否则线程池包装同步 retriever。

### 12.10 链版本与 prompt 版本

链对象打 `metadata={"chain_version": "rag_v4"}`，与 [110](110.rag-prompt-template-tutorial.md) `prompt_v3` 分开管理——回滚时各滚各的。
""",
    },
    "127": {
        1: """
### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 检索器 | Retriever | query→list[Document] |
| 搜索参数 | search_kwargs | k、filter、threshold |
| 向量库 | VectorStore | [76 Chroma](76.chroma-vector-db-tutorial.md) 等 |
| 集成检索 | EnsembleRetriever | 多路融合 |

### 1.3 读完本篇的最小交付物

1. Chroma `as_retriever` + ACL filter；  
2. 接入 [126 LCEL](126.langchain-lcel-tutorial.md) 全链；  
3. 口述 FAISS vs Chroma Retriever 差异；  
4. 画出混合检索 + RRF 位置；  
5. 十条金标 Recall@3 记录。
""",
        3: """
### 3.2 BaseRetriever 契约

实现 `_get_relevant_documents(query, *, run_manager)` 返回 `list[Document]`。`invoke` 是对外统一入口。自定义 Retriever 时 **不要** 绕过 invoke 直接调内部 API——否则 LCEL、回调、评测钩子会失效。

### 3.3 检索在 RAG 管道中的前后邻

```text
[100-103 查询增强] → [本篇 Retriever 宽召回] → [106 去重] → [96 精排]
→ [107 预算] → [108 重排] → [111 格式] → [110 模板] → LLM
```

Retriever 只负责 **宽召回**；把精排塞进 Retriever 类里会导致接口臃肿，宜用 LCEL Lambda 分步。
""",
        4: """
### 4.3 相似度与距离

Chroma 默认返回 **距离**（越小越近）；部分封装转成 **score**（越大越近）。日志里应 **注明方向**，避免 on-call 误判「分数低=差」实际是距离 metric。换 metric 见 [26 相似度](26.similarity-metrics-tutorial.md)、[75 FAISS](75.faiss-ann-tutorial.md)。

### 4.4 持久化与 [49 增量](49.incremental-update-tutorial.md)

`persist_directory` 变更后 Retriever 无需改代码，但 **Embedding 模型变更** 必须新 collection 全量重建。增量 upsert 后 Retriever 立即可见新 chunk，无需重启进程（Chroma 持久化客户端）。
""",
        5: """
### 5.3 score_threshold 与拒答联动

`similarity_score_threshold` 检索器在 **无达标结果** 时返回空列表——应对齐 [112 拒答](112.refusal-strategy-tutorial.md) 短路，不调 LLM。阈值用 [99](99.score-threshold-tutorial.md) 在金标上校准，勿拍脑袋 0.7。

### 5.4 多条件 filter 组合

Chroma `$and` / `$or` 组合部门与文档类型过滤。filter 表达式 **与 metadata 入库一致**；入库漏字段等于 filter 失效，见 [53 ACL](53.metadata-acl-tutorial.md)。
""",
        6: """
### 6.4 BM25 Retriever 来源

稀疏路可用 `BM25Retriever.from_documents`（需分词与中文适配）或外部 Elasticsearch。与稠密路 **文档集版本一致**；一路更新一路不更新会导致 RRF 偏斜。

### 6.5 权重调参方法

准备二十条金标，网格搜索 `weights=[0.3,0.7]` 等组合，看 Recall@3。**记录最优权重进配置中心**，与 prompt 版本同样管理。
""",
        7: """
### 7.3 FAISS save/load 与 Retriever

```python
vs.save_local("faiss_handbook")
vs = FAISS.load_local("faiss_handbook", embeddings, allow_dangerous_deserialization=True)
retriever = vs.as_retriever(search_kwargs={"k": 5})
```

`allow_dangerous_deserialization` 仅信任自有目录。生产更推荐 Chroma persist 或 Milvus。

### 7.4 何时自研 Retriever 包装 hybrid_search

企业已有 **成熟 hybrid_search()**（C 模块）时，继承 `BaseRetriever` 包装一行 `return hybrid_search(query)`，LCEL 链 **零改动** 切换——这是 D 模块最常见落地方式。
""",
        8: """
### 8.3 MMR 与多样性

FAQ 高度重复 chunk 占满 Top-K 时用 MMR（[105](105.mmr-diversity-tutorial.md)）。`fetch_k` 大于 `k`，`lambda_mult` 权衡相关与多样。制度问答有时 **不需要** MMR——用金标对比开启前后 Faithfulness。

### 8.4 ParentDocumentRetriever 简述

小块 embedding 检索，返回大块 `page_content` 给 LLM——适合 **法条+细则** 结构。见 [65 父文档](65.parent-document-retriever-tutorial.md)；实现可用 MultiVector 或检索后 expand。
""",
        9: """
### 9.3 权限验收用例

| 用户 | filter | 问财务制度 | 期望 |
|------|--------|------------|------|
| staff | acl_group=all_staff | 年假 | 有结果 |
| staff | acl_group=all_staff | 未公开并购案 | 空或拒答 |
| finance | acl_group=finance | 并购案 | 有结果 |

自动化测试应覆盖 **正向召回** 与 **负向不越权**。

### 9.4 延迟分解

日志分段：`retriever_ms`、`rerank_ms`、`llm_ms`。Retriever 慢时先查 Embedding 批大小 [67](67.embedding-batching-tutorial.md)、Chroma 索引规模，再考虑换 [77 Milvus](77.milvus-tutorial.md)。
""",
        10: """
### 10.5 错：Retriever 当 VectorStore 用

**现象**：直接 `vectorstore.query` 绕过 Retriever，链上回调丢失。  
**对**：统一 `retriever.invoke`。

### 10.6 错：混合后未截断就进 prompt

**现象**：RRF 合并 30 条全塞 prompt。  
**对**：rerank 后 Top-5 + [107 预算](107.context-budget-tutorial.md)。
""",
        12: """
### 12.9 MultiQueryRetriever（了解）

[101 多查询](101.multi-query-retrieval-tutorial.md) 可用 `MultiQueryRetriever` 包装基 retriever，自动生成多 query 合并结果——评测有效再开，注意 latency 与成本。

### 12.10 与 [124 工具](124.function-calling-tool-use-tutorial.md) 的 as_tool

```python
tool = retriever.as_tool(
    name="search_kb",
    description="检索企业知识库制度与流程。",
)
```

Agent 与 LCEL 共用同一 retriever 实例，ACL filter 只写一处。
""",
    },
}


def insert_supplements(text: str, num: str) -> str:
    sup = SUPPLEMENTS.get(num, {})
    for sec in sorted(sup.keys(), reverse=True):
        block = sup[sec]
        pattern = rf"(## {sec}\.[^\n]*\n[\s\S]*?)(?=\n## {sec + 1}\.|\n## 附录|\Z)"
        m = re.search(pattern, text)
        if m:
            text = text[: m.end(1)] + block + text[m.end(1) :]
    return text


def count_hz(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def main():
    files = [
        "123.structured-output-json-tutorial.md",
        "124.function-calling-tool-use-tutorial.md",
        "125.langchain-core-tutorial.md",
        "126.langchain-lcel-tutorial.md",
        "127.langchain-retriever-tutorial.md",
    ]
    print("| filename | hanzi |")
    print("|----------|-------|")
    for f in files:
        p = ROOT / f
        num = f.split(".")[0]
        text = p.read_text(encoding="utf-8")
        text = insert_supplements(text, num)
        p.write_text(text, encoding="utf-8")
        hz = count_hz(text)
        print(f"| {f} | {hz} |")


if __name__ == "__main__":
    main()
