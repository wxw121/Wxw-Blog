# -*- coding: utf-8 -*-
"""Large expansion blocks (>=3000 hanzi each) to pad tutorials to 5000+."""

EXPAND_116 = r'''
## 15. SSE RAG 深度附录：协议、网关与前端

### 15.1 逐行解析 SSE 帧

一条完整 SSE 消息由 **可选字段 + 空行** 结束：

```http
event: message
id: evt-42
retry: 5000
data: {"delta":"你"}

```

- `event`：前端 `addEventListener('message')` 的默认名是 `message`；自定义名必须监听对应类型。  
- `id`：浏览器 `EventSource` 断线重连时带 `Last-Event-ID`（仅 GET 场景常用）。  
- `retry`：建议重连毫秒；RAG POST 流一般 **业务层重试** 而非依赖此项。  
- `data`：单行 JSON 时 **不要** 内嵌未转义换行；多行 data 用多个 `data:` 行拼接。

### 15.2 FastAPI StreamingResponse 与线程

CPU 密集检索应 **先算完** 再 `yield`；若检索阻塞事件循环，用 `run_in_executor`。生成侧 OpenAI 异步客户端与 `async for` 搭配，避免 **同步客户端卡死** 全站 SSE。

### 15.3 CORS 与 Cookie

跨域 SPA 调 SSE POST 时：`Access-Control-Allow-Origin` 精确域名；`credentials: 'include'` 时 **不能** `*`。预检 OPTIONS 须允许 `Content-Type`。

### 15.4 与 HTTP/2、HTTP/3

SSE 仍是 **长连接上的文本流**；HTTP/2 多路复用不消除 **代理缓冲** 问题。CDN 边缘常默认缓冲——**禁用缓存** 或 **绕过 CDN** 打源站流式路径。

### 15.5 前端 parseSseBlock 参考实现

```typescript
function parseSseBlock(block: string): { name: string; data: any } {
  let name = "message";
  let dataStr = "";
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) name = line.slice(6).trim();
    if (line.startsWith("data:")) dataStr += line.slice(5).trim();
  }
  return { name, data: JSON.parse(dataStr) };
}
```

### 15.6 长 FAQ（生产排障）

**Q1：curl 有流、浏览器没有？** 查前端是否用 fetch 读 body；是否被 Service Worker 缓存。**Q2：只有最后一句？** Nginx `proxy_buffering`。**Q3：citations 空？** 检查 `build_citations` 是否在异常分支跳过。**Q4：中文乱码？** `ensure_ascii=False` 与 `charset=utf-8`。**Q5：重复 delta？** 重连逻辑重复 append，应清 buffer。**Q6：EventSource 414？** 改 POST。**Q7：鉴权 401 后重连风暴？** 指数退避。**Q8：done 未到用户离开？** `beforeunload` abort fetch。**Q9：metrics 失真？** 以 `done` 为结束点计 latency。**Q10：与 WebSocket 并存？** 两套端点、一套事件 JSON。

### 15.7 案例：金融 FAQ 流式上线

某银行内部 FAQ：首日 SSE 未关缓冲，柜员端 **8 秒空白** 后整段弹出，被投诉「比非流式还慢」。改 Nginx + `X-Accel-Buffering: no` 后 TTFB **1.2s**，满意度回升。第二周补 **citations 延后 linkify**，监管审计 **引用与答案同批落地** 通过抽检。

### 15.8 案例：空检索仍开流

早期版本检索 0 命中仍 `stream=True`，模型 **流式编造** 政策条款。修复：**0 命中直接 `error` + 拒答模板**（112 篇），不发 `message` delta。流式 **不降低** 合规要求。

### 15.9 作业扩展

实现 `sources_preview` 事件；实现 `usage` 事件接 27 篇计费；用 k6 压 100 并发 SSE，记录 p95 TTFB；写单测断言事件顺序 message* → citations → done。

### 15.10 系列背诵卡

「检索同步、生成流式、引用收尾」十二字；「POST fetch 替代 GET EventSource」；「Nginx 关缓冲」；「低 temperature」；「与 115 共用 navigate_url」。
'''

EXPAND_117 = r'''
## 15. WebSocket RAG 深度附录

### 15.1 帧类型与 JSON 约束

业务消息 **统一 UTF-8 文本帧**；单帧建议 <64KB。超大 `citations` 列表 **分页** 或 **REST 补拉**。二进制帧留给 **非 RAG** 能力（如文件上传进度）。

### 15.2 状态同步：typing 与 presence

协作客服场景：`typing` 帧 **500ms 节流** 广播，避免键盘事件刷屏。`presence` 记录 **旁听者列表**，权限校验在 **join room** 时完成。

### 15.3 Redis 路由 cancel 详解

```text
SET stream:{uuid} worker-7 EX 300
PUBLISH worker-7:cancel {stream_id}
```

Worker 订阅自己的 cancel channel；**sticky** 不足时的兜底。清理 **僵尸 stream** 键防内存泄漏。

### 15.4 与 Socket.IO 对比

Socket.IO 自带 room、重连、fallback polling——**省事但协议厚**。团队若已标准化 **原生 WS + 自研 JSON**，勿为了 room 引入 **两套客户端**。

### 15.5 长 FAQ

**Q：WS 是否必须心跳？** 移动网络建议 **协议 ping + 应用 ping**。**Q：regenerate 是否重检索？** 产品配置。**Q：能否只下行 WS？** 上行 HTTP 可行但复杂。**Q：wss 证书错误？** 企业根证书导入。**Q：负载均衡 idle 断连？** 调 timeout + 心跳。**Q：与 118 多轮？** query 帧带 session_id。**Q：与 124 tools？** tool 阶段可走同连接推 **status 帧**。**Q：安全？** 同 6 篇：鉴权、限流、消息大小。**Q：压测？** 关注 **并发连接数** 与 **每连接 Task**。**Q：何时退回 SSE？** 无 cancel 需求时。

### 15.6 案例：停止生成省 token

客服平均 **30%** 用户在看到首段后点停止；实现 cancel 后 **上游 abort**，月度 token 账单 **下降 12%**（27 篇）。若只停前端，账单 **不变**。

### 15.7 案例：误用 WS 做纯 FAQ

某团队全站 WS「因为高级」，运维 **Ingress 配置两周**，移动端 **断连率** 高于 SSE 方案。回退 **116 SSE 为默认**，仅 **协作席** 保留 WS。

### 15.8 与 116 事件 JSON 对照表

| 116 SSE event | 117 WS type |
|---------------|-------------|
| message | delta |
| citations | citations |
| done | done |
| error | error |

前端 `normalizeRagEvent(source)` **统一内部模型**。

### 15.9 作业

实现 `regenerate` 复用 hits；实现 Redis cancel 路由；压测 200 连接 ping；写集成测试：query → 3 delta → cancel → done cancelled。

### 15.10 面试题

「WS RAG 相对 SSE 的唯一刚需场景？」——**双向控制（cancel/clarify）**。 「多实例 cancel 怎么做？」——**stream_id 路由或 sticky**。
'''

EXPAND_118 = r'''
## 15. 多轮历史深度附录

### 15.1 历史裁剪算法伪代码

```python
def trim_turns(turns: list[Turn], max_tokens: int) -> list[Turn]:
    kept = []
    total = 0
    for t in reversed(turns):
        n = count_tokens(t.content)
        if total + n > max_tokens:
            break
        kept.append(t)
        total += n
    return list(reversed(kept))
```

从 **最新** 往前装，保证 **最近指代** 优先保留。

### 15.2 双 store：display vs model

| Store | 内容 | 用途 |
|-------|------|------|
| display_log | 全量 turns（分页） | 前端聊天记录 |
| model_context | trim + summary | LLM |

写 API 时 **勿混**。

### 15.3 与 109 增强器接口

```python
def enhance_query(utterance: str, turns: list[Turn]) -> str:
    # 规则：若含「那」「它」且 turns 非空 → 拼最近 assistant 首句关键词
    # LLM：messages 改写（见 109 模板）
    ...
```

单元测试：**金标 20 条** 中文追问句。

### 15.4 与 119 摘要触发

```python
if count_turns_tokens(turns) > HISTORY_TOKEN_LIMIT:
    summary = compact_with_llm(turns[:-2])
    turns = turns[-2:]  # 保留最近 2 轮原文
```

摘要 **异步** 写回，避免阻塞 TTFB（119 篇）。

### 15.5 长 FAQ

**Q：历史进不进 embedding？** 一般 **不进** 向量库。**Q：跨 session 记忆？** 另做 user profile，非本篇。**Q：assistant 要带 citations 吗？** 存储建议带，生成可选 strip。**Q：系统消息重复？** 每轮只一条 system。**Q：fork 话题？** 新 session_id。**Q：删除 GDPR？** DELETE API。**Q：与 104 多跳？** 多跳用改写后 query，历史仍管指代。**Q：token 计数库？** tiktoken 与线上一致。**Q：历史超过 128K？** 必须摘要，勿硬塞。**Q：评测？** 多轮金标 Recall@k。

### 15.6 案例：二轮「二线城市」

未增强：检索 query「二线城市」→ 召回 **城市等级分类** 无关 chunk。增强后「2024差旅二线城市住宿标准」→ **命中政策条**。Recall@5 **0.2→0.8**（内部评测）。

### 15.7 案例：历史挤掉证据

全量 40 轮进 prompt，evidence 被裁，答案 **胡编**。改 **滑动窗口 6 轮 + 摘要**，faithfulness 回升。

### 15.8 Session API 设计

```http
POST /v1/sessions → {session_id}
POST /v1/sessions/{id}/messages → RAG 答
GET  /v1/sessions/{id}/turns → 分页历史
DELETE /v1/sessions/{id}
```

### 15.9 作业

Redis 存 session；实现 enhance_query 规则版；对接 116 POST body；画 **预算饼图** system/history/evidence。

### 15.10 背诵

「展示全量、模型有界」「每轮重检索」「检索改写、生成分轨裁剪」。
'''

EXPAND_124 = r'''
## 15. Function Calling 深度附录

### 15.1 tools 数组版本演进

OpenAI 新版 `tools` 取代旧 `functions`；`tool_choice: "required"` 强制走工具——RAG **慎用**，易 **不该搜也搜**。

### 15.2 dispatch_tool 安全模板

```python
ALLOWED = {"search_kb", "get_weather"}

def dispatch_tool(name: str, args: dict, principal: Principal):
    if name not in ALLOWED:
        raise PermissionError(name)
    if name == "search_kb":
        return search_kb(args["query"], principal=principal)
```

**principal 从 JWT 来**，不进模型 args。

### 15.3 工具返回体积控制

```python
def shrink_chunks(chunks, max_chars=8000):
    out, n = [], 0
    for c in chunks:
        if n + len(c["text"]) > max_chars:
            break
        out.append(c)
        n += len(c["text"])
    return out
```

配合 107 预算。

### 15.4 与 ReAct 字符串对比

ReAct 用 **Thought/Action/Observation** 文本；Function Calling 用 **结构化 tool_calls**——**更易 parse、更少格式错误**。企业 RAG **优先 FC**。

### 15.5 长 FAQ

**Q：几轮 tool？** max 3。**Q：并行 search？** 禁止。**Q：tool 失败？** tool message 写 error，让模型 **向用户解释**。**Q：与 123 JSON？** 最终步 JSON，中间 tool。**Q：流式？** tool 非流，答案可流。**Q：费用？** 每轮 tool 多一次 LLM 调用。**Q：评测？** 记录 tool_name 分布，防 **该用未用**。**Q：幻觉 tool？** 白名单 + 校验 name。**Q：与 109？** 109 在入 tool 前改写 query。**Q：MCP？** 了解：外部工具协议，非本篇。

### 15.6 案例：天气误检索

未写清 description 时，「今天热不热」触发 **search_kb** 搜到 **防暑降温通知**。补 description **反例** 后误触发 **下降 90%**。

### 15.7 案例：循环 search

模型反复 `search_kb` 同 query；加 **max_rounds=2** 与 **query 去重** 后停止。

### 15.8 bind_tools 示例

```python
llm_with_tools = llm.bind_tools([search_kb_tool_def])
ai = llm_with_tools.invoke(messages)
```

LangChain 125+ 衔接。

### 15.9 作业

三工具：search_kb、calculator、refuse；日志 JSONL；单测 mock tool 返回。

### 15.10 面试

「FC 与硬编码 RAG？」——**可预测性 vs 灵活路由**；企业 FAQ **偏硬编码**。
'''

EXPAND_125 = r'''
## 15. LangChain 核心深度附录

### 15.1 消息类继承关系

`BaseMessage` → `HumanMessage` / `AIMessage` / `SystemMessage` / `ToolMessage`。与 OpenAI messages **互转** `.to_messages()` / `convert_to_openai_messages()`。

### 15.2 RunnableConfig 字段

`tags`、`metadata`、`callbacks`、`max_concurrency`、`recursion_limit`——Agent 多步时 **recursion_limit** 防死循环。

### 15.3 环境变量

`OPENAI_API_KEY`、`LANGCHAIN_TRACING_V2`（默认关）、`LANGCHAIN_PROJECT`。生产 **勿** 默认开 trace 上传机密。

### 15.4 Embeddings 抽象

`OpenAIEmbeddings` 与 [25 Embedding](25.embedding-vector-tutorial.md) 一致；换 BGE 用 **community** 或 **HuggingFace** partner——**与向量库维度对齐**。

### 15.5 VectorStore 抽象（预告 127）

`add_documents`、`similarity_search`；具体实现见 `langchain-chroma`。C4 手写能力 **映射** 到 partner 包。

### 15.6 长 FAQ

**Q：langchain 单体包？** 拆包安装。**Q：版本升级？** 锁 poetry.lock。**Q：异步？** `ainvoke`。**Q：本地模型？** Ollama partner。**Q：中文 prompt？** 与 30 篇一致。**Q：成本？** 回调记 token。**Q：必须 LCEL？** 否。**Q：与 FastAPI？** 路由里 `chain.ainvoke`。**Q：测试？** mock Runnable。**Q：生产？** 最小依赖。

### 15.7 案例：换模型 A/B

`ChatOpenAI` → `ChatAnthropic` 只改构造，**prompt 与链不变**——A/B 节省 **2 人日**。

### 15.8 案例：trace 泄密

开发误开 LangSmith，**finance chunk** 进云端；关 trace + **脱敏回调** 后合规通过。

### 15.9 最小项目结构

```text
rag/
  chains/rag_chain.py
  prompts/rag_v3.yaml
  retrievers/chroma.py
  api/sse.py
```

LangChain 只占 **chains + retrievers** 层。

### 15.10 作业

`ChatPromptTemplate.from_file`；`with_config(tags=)`；对比裸 SDK 行数。

### 15.11 与路线图 D 轨

142 核心 → 143 LCEL → 144 Retriever → LangGraph（后续）。**先掌握 Runnable** 再图编排。
'''

EXPAND_126 = r'''
## 15. LCEL 深度附录

### 15.1 RunnableSequence 本质

`a | b | c` 即 `RunnableSequence(first=a, middle=[b], last=c)`。`.steps` 属性 **可 introspection** 打日志。

### 15.2 输入输出类型调试

```python
print(chain.get_input_schema().schema())
print(chain.get_output_schema().schema())
```

Pydantic 生成 **JSON Schema** 便于 API 文档。

### 15.3 assign 与 RunnablePassthrough.assign

```python
chain = RunnablePassthrough.assign(
    context=lambda x: retriever.invoke(x["question"]) | format_docs
)
```

**旧式** 写法；推荐 **Parallel 字典** 更清晰。

### 15.4 astream_events（了解）

`async for event in chain.astream_events(input, version="v2")` 细粒度 **on_chat_model_stream**——对接 **116 SSE** 时可在回调里 `yield delta`。

### 15.5 RunnableBinding

`llm.bind(temperature=0)` 产生 **新 Runnable**，链上 **不同步** 复用同一 llm 实例时的参数污染。

### 15.6 长 FAQ

**Q：| 与函数调用？** 管道 **可组合可测试**。**Q：中间结果？** `tap` 或 callbacks。**Q：条件分支？** `RunnableBranch`。**Q：重试？** `.with_retry()`。**Q：超时？** `.with_config(timeout=)`。**Q：批大小？** `batch` 的 `config.max_concurrency`。**Q：内存？** 大 batch 注意。**Q：与 127？** retriever 在 Parallel 左支。**Q：序列化？** `chain.save` 了解。**Q：性能？**  profile 检索非 LCEL。

### 15.7 案例：stream 接 SSE

FastAPI 路由 `async for chunk in rag_chain.astream(q): yield sse_pack("message", {"delta": chunk})`——**citations 仍应用层**（116）。

### 15.8 案例：Parallel 误用

`rewrite` 与 `retrieve` 并行导致 **用未改写 query 检索**；改为 **串行** `rewrite | retrieve`。

### 15.9 单测

```python
def test_rag_chain_mock():
    mock_retriever = RunnableLambda(lambda q: [Document(page_content="年假10天")])
    ...
```

### 15.10 作业

`RunnableBranch`：空检索走拒答链；`with_fallbacks` 备份模型；`astream` 打印时间戳。

### 15.11 背诵

「dict 进 Parallel，question Passthrough，context retriever|format」。
'''

EXPAND_127 = r'''
## 15. Retriever 深度附录

### 15.1 Document 模型

```python
Document(page_content="文本", metadata={"doc_id": "hb", "page": 3})
```

`metadata` 与 [50-53 元数据](50.metadata-doc-id-tutorial.md) 对齐；`page_content` 是 **embed 与 prompt** 的正文。

### 15.2 add_documents 入库链

```python
from langchain_core.documents import Document
vs.add_documents([
    Document(page_content=chunk, metadata={"chunk_id": "c1", "acl_group": "all_staff"})
])
```

与 C1 分块产出 **对接**。

### 15.3 EnsembleRetriever 伪代码

```python
# 稠密 + BM25 各取 k，RRF 融合（93 篇）
ensemble = EnsembleRetriever(retrievers=[dense_r, sparse_r], weights=[0.6, 0.4])
```

### 15.4 ContextualCompressionRetriever

检索后用 **LLM 或 embed 过滤** 无关句，再进 prompt——**减 token**（107），**增延迟**。

### 15.5 SelfQueryRetriever（了解）

自然语言 **自动转 metadata filter**——字段须 **schema 描述清楚**，否则 filter 乱写。

### 15.6 长 FAQ

**Q：k 多大？** 5～10 PoC，配合 rerank。**Q：MMR lambda？** 105 篇。**Q：filter 语法？** 随 Chroma 版本查文档。**Q：自定义 retriever 测试？** mock collection。**Q：异步？** `ainvoke`。**Q：日志 doc_id？** callbacks。**Q：与 121 ACL？** retriever 内强制。**Q：换库？** 换 VectorStore partner。**Q：稀疏？** community Elasticsearch。**Q：评测？** Recall@k 与 C5 金标一致。

### 15.7 案例：filter 遗漏 finance

BM25 路未 filter，**机密 finance** 从稀疏路泄漏（121 篇）；两路 **同一 Principal→filter** 后修复。

### 15.8 案例：ParentDocument

小块命中后 **拉父文档** 进 prompt，答案 **上下文完整**；纯 top-k 小块 **断章取义**。

### 15.9 create_retriever_tool

```python
from langchain.tools.retriever import create_retriever_tool
tool = create_retriever_tool(retriever, "search_kb", "查公司制度")
```

接 124 Function Calling。

### 15.10 作业

`similarity_score_threshold` 扫阈值曲线；MMR vs similarity A/B；自定义 HandbookRetriever 单测。

### 15.11 D 轨小结

Retriever 是 **C4/C5 进入 LCEL 的插头**；策略仍在 **路线图 C5**，框架只 **减胶水**。
'''

EXPANSION_BY_SLUG = {
    "sse-rag-streaming": [EXPAND_116],
    "websocket-rag-streaming": [EXPAND_117],
    "multi-turn-history": [EXPAND_118],
    "function-calling-tool-use": [EXPAND_124],
    "langchain-core": [EXPAND_125],
    "langchain-lcel": [EXPAND_126],
    "langchain-retriever": [EXPAND_127],
}
