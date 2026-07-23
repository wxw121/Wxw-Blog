# -*- coding: utf-8 -*-
"""Article bodies for _gen_missing_116_127.py — each base targets ~4500+ hanzi."""

ARTICLE_116_EXTRA = r'''## 14 附录：SSE RAG 生产细节扩展

### 14.1 事件顺序契约（团队 Wiki 可贴）

推荐 **严格顺序**：`retrieval`（可选）→ 若干 `message` → **至多一个** `citations` → `done`。禁止在 `done` 后再发 `message`（前端状态机难维护）。若需 **usage 计费**，在 `citations` 与 `done` 之间插 `usage` 事件。

### 14.2 OpenAI 兼容流与 SSE 事件映射

许多团队直接用 OpenAI `stream=True` 的 chunk，在网关 **转译** 为本篇事件：

| OpenAI chunk | 本篇事件 |
|--------------|----------|
| `delta.content` | `message` |
| `finish_reason=stop` | 触发组 `citations` |
| 自定义 metadata | `citations` 内字段 |

**不要** 把 OpenAI 原始 JSON 直接透传给浏览器——字段版本随厂商变；对外只暴露 **稳定契约**。

### 14.3 检索预览事件 `sources_preview`

产品可在 **首 token 前** 发：

```json
{"sources_preview":[{"title":"员工手册","page":12},{"title":"员工手册","page":8}]}
```

UI 显示「参考 2 份文档」**不可点击**；正式 `citations` 到达后替换为可点 `[n]`。缓解用户 **等字焦虑**，又不提前绑定错误编号。

### 14.4 反压：生成快于渲染

模型 200 tokens/s，React 每字 setState 会卡。策略：**缓冲 50ms 或 requestAnimationFrame 合并 delta**；极端情况服务端 `asyncio.sleep` 轻微节流（慎用，影响 TTFT 指标）。

### 14.5 多 worker 与无状态

SSE 连接粘在 **生成该流的 worker**；水平扩展要 **粘性会话** 或 **把生成放队列单消费者**。检索可无状态，生成流 **不要** 假设本机内存里一定有 `hits`——`stream_id` 对应 Redis 存 `hits` 快照。

### 14.6 安全：SSE 与 CSRF

POST 开流时校验 **CSRF Token** 或 **SameSite Cookie**；`EventSource` GET 方案要把 token 放 **短期 query** 并 **单次有效**。

### 14.7 与 [110 Prompt 模板](110.rag-prompt-template-tutorial.md) 版本

流式与非流式 **共用同一 prompt 模板版本** `prompt_version`；在 `done` 日志记录，便于 bad case 回放。

### 14.8 评测：流式是否更幻觉？

流式 **不降低** 幻觉率；有时用户因 **先看到部分句** 更宽容。faithfulness 评测仍用 **完整答案** 与 citations 校验（[34 Grounding](34.grounding-citation-tutorial.md)）。

### 14.9 压测脚本思路

```python
import asyncio, httpx

async def one_client(i: int):
    async with httpx.AsyncClient() as c:
        async with c.stream("POST", url, json={"query": f"q{i}"}) as r:
            async for line in r.aiter_lines():
                pass  # 统计 TTFB

asyncio.run(asyncio.gather(*[one_client(i) for i in range(50)]))
```

关注 **连接数** 与 **worker 内存**（每流缓存 `answer_parts`）。

### 14.10 给前端的一句人话

「字是 **`message` 事件** 出来的，链接是 **`citations` 事件** 盖章的；章没盖前别让用户点引用。」

### 14.11 与 [115 导航](115.source-document-navigation-tutorial.md) 联调回归

每次改 `navigate_url` 规则，跑 **SSE 端到端测试**：解析 `citations[0].navigate_url` 必须 200 或预期 403（越权）。

### 14.12 故障演练

每月演练：**杀 worker**  midway 流 → 前端应显示中断而非无限 loading；**Nginx 缓冲误开** → 用户应反馈「一次性出字」。

### 14.13 成本提示

流式 **不减少输出 token 费用**（[27 Token 计费](27.token-counting-billing-tutorial.md)）；只改善体验。预算审批时勿声称「流式省钱」。

### 14.14 面试 30 秒版

「RAG SSE：检索同步完成；`text/event-stream` 推 `message` delta；生成结束后推 `citations` 对齐 [n]；最后 `done`。引用放末尾防编号漂移。POST+fetch 流兼容长 query。Nginx 关缓冲。双向中断看 WebSocket 117。」
'''

ARTICLE_117 = r'''# C6 生成与 Grounding（八）：WebSocket 流式 RAG 完全指南

> [116 SSE 流式 RAG](116.sse-rag-streaming-tutorial.md) 覆盖了 **80% 企业问答**：问一次、答案单向流出。但用户点 **「停止生成」**、同连接里 **追问澄清**、客服 **协作旁听**——需要 **全双工**。[第 6 篇 WebSocket 基础](6.websocket-tutorial.md) 讲握手、心跳、重连；本篇在同样长连接上定义 **RAG 双向消息契约**、**cancel/regenerate**、与 SSE 的选型边界。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 轨第八篇**（路线图第 **134** 条），**地基篇**。前置：[6 WebSocket](6.websocket-tutorial.md)、[116 SSE RAG](116.sse-rag-streaming-tutorial.md)、[113 行内引用](113.inline-citation-tutorial.md)、[115 源文档导航](115.source-document-navigation-tutorial.md)。

---

## 目录

1. [前言：什么时候 SSE 不够](#1-前言什么时候-sse-不够)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [何时用 WebSocket 做 RAG 流式](#3-何时用-websocket-做-rag-流式)
4. [与第 6 篇 WebSocket 基础的关系](#4-与第-6-篇-websocket-基础的关系)
5. [双向消息流设计](#5-双向消息流设计)
6. [与 116 SSE 的事件同构](#6-与-116-sse-的事件同构)
7. [中断、重生成与澄清](#7-中断重生成与澄清)
8. [后端实现：FastAPI WebSocket](#8-后端实现fastapi-websocket)
9. [前端状态机与协作场景](#9-前端状态机与协作场景)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [生产部署、心跳与多实例](#11-生产部署心跳与多实例)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：什么时候 SSE 不够

上线第一周，产品用 [116 篇](116.sse-rag-streaming-tutorial.md) 的 SSE 方案，体验良好。第二周需求来了：

| 需求 | SSE 能否优雅满足 |
|------|------------------|
| 逐字显示答案 | ✅ |
| 末尾挂引用 | ✅ |
| 用户点「停止」立刻停 LLM | ⚠️ 需另开 HTTP cancel 或断连接 |
| 同屏「改问法」不重新握手 | ⚠️ |
| 输入框「对方正在输入」 | ❌ 需第二条通道 |
| 多人围观同一会话 | ❌ |

**WebSocket RAG Streaming**：在持久双向连接上，用 **JSON 文本帧** 承载与 SSE 同形的 `delta/citations/done`，并增加 **`cancel`、`regenerate`、`clarify`** 等客户端→服务端控制消息。  
通俗说：**SSE 像广播喇叭只往下喊；WebSocket 像对讲机，用户随时能插话喊停。**

**读完本文，你应该能做到：**

1. 对照 [6 篇](6.websocket-tutorial.md) 说明 WS 握手与 RAG 业务帧分层。  
2. 画出 **client→server / server→client** 消息表。  
3. 实现 §8 **可 cancel 的假 LLM 流**。  
4. 说明 **80% 场景仍应用 SSE**（[116 篇](116.sse-rag-streaming-tutorial.md)）的理由。  
5. 处理 **多实例下 cancel 路由** 的基本思路。  
6. 识别 §10 五种翻车。

### 1.1 C6 轨位置

```text
133 SSE 流式 RAG（默认单向）
134 WebSocket 流式 RAG ← 本篇（地基）
135 多轮历史
```

**学习顺序**：先 [7 SSE](7.sse-tutorial.md) 与 [116](116.sse-rag-streaming-tutorial.md)，再 [6 WebSocket](6.websocket-tutorial.md)，最后本篇——避免 **无双向需求却上 WS**。

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 全双工 | full-duplex | 同一连接双向发帧 |
| 控制帧 | control message | cancel / ping 类 |
| 流 ID | stream_id | 区分同会话多次生成 |
| 中止 | abort / cancel | 停止 LLM token 生成 |
| 重生成 | regenerate | 同上下文重新答 |

---

## 2. 本文边界与动手路径

**档位：C6 地基篇（路线图 134）。**

**本文讲：** WS vs SSE 选型、双向消息契约、cancel、FastAPI 示例、多实例注意、FAQ。  
**本文不讲：** Socket.IO 全家桶、游戏级同步、完整 Agent 工具循环（[124 篇](124.function-calling-tool-use-tutorial.md)）、K8s Ingress WS 全矩阵。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 [6 篇 §3](6.websocket-tutorial.md) 握手 | 理解 Upgrade |
| B | 读 §5 消息表 | 能默写 cancel |
| C | 跑 §8 | 点停止后 delta 停止 |
| D | 对照 116 事件 JSON | 字段一致 |
| E | §10 先错对对 | 五种错 |

**环境：** Python 3.10+、`fastapi`、`uvicorn[standard]`；现代浏览器。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| WebSocket 协议 | [6 WebSocket](6.websocket-tutorial.md) |
| SSE RAG 事件 | [116 SSE RAG](116.sse-rag-streaming-tutorial.md) |
| 引用 `[n]` | [113 行内引用](113.inline-citation-tutorial.md) |
| navigate_url | [115 源文档导航](115.source-document-navigation-tutorial.md) |
| 多轮 body | [118 多轮历史](118.multi-turn-history-tutorial.md) |

---

## 3. 何时用 WebSocket 做 RAG 流式

![WebSocket vs SSE for RAG](image/websocket-rag-streaming/01-ws-vs-sse.png)

### 3.1 选型矩阵

| 维度 | SSE [116] | WebSocket 本篇 |
|------|-----------|----------------|
| 通信方向 | 服务器→客户端 | 双向 |
| 协议栈 | 纯 HTTP | Upgrade 长连接 |
| 穿透代理 | 通常更省心 | 需正确配置 |
| 用户中断 | 需额外设计 | **原生 cancel 帧** |
| 实现复杂度 | 低 | 中高 |
| 默认推荐 | **标准 FAQ** | 强交互 |

### 3.2 典型必须用 WS 的产品信号

- 答案流式过程中 **频繁改口、澄清**（同一连接连发多条 query）；  
- **协作客服**：主管旁听、抢接、同步输入状态；  
- **长会话 Agent** 多步工具（与 [124 篇](124.function-calling-tool-use-tutorial.md) 衔接）；  
- 移动端 **前后台切换** 需双向心跳保活（见 [6 篇 §8](6.websocket-tutorial.md)）。

### 3.3 不必用 WS 的信号

- 单次问答、无停止按钮、引用末尾盖章——**坚持 SSE**；  
- 仅为了「听起来更实时」——SSE 同样低 TTFT；  
- 团队无人维护 **粘性会话 / Redis 路由**——WS 多实例痛苦。

---

## 4. 与第 6 篇 WebSocket 基础的关系

### 4.1 协议层复习

[6 篇](6.websocket-tutorial.md) 已讲：`ws://` / `wss://`、`Sec-WebSocket-Key` 握手、文本帧与 ping/pong。本篇 **全部假设 wss + 鉴权后** 才进入 RAG 业务。

### 4.2 业务层在基础之上的增量

| 6 篇 demo | 本篇 RAG |
|-----------|----------|
|  echo 聊天 | 检索 + LLM 流 |
| 任意字符串 | **JSON 类型字段** `type` |
| 无状态 | `session_id` / `stream_id` |
| 无取消 | `cancel` 中止 Task |

### 4.3 连接生命周期

```text
1. 客户端 wss 连接 + JWT
2. 服务端 accept，发 {type:"ready"}
3. 客户端 {type:"query", ...}
4. 服务端检索 → 推 {type:"delta",...} 若干
5. 客户端可选 {type:"cancel"}
6. 服务端 {type:"citations"} → {type:"done"}
```

---

## 5. 双向消息流设计

![WebSocket RAG 消息流](image/websocket-rag-streaming/02-bidir-flow.png)

### 5.1 客户端 → 服务端

| type | 字段 | 说明 |
|------|------|------|
| `query` | `text`, `session_id?`, `messages?` | 发起 RAG（见 [118](118.multi-turn-history-tutorial.md)） |
| `cancel` | `stream_id` | 中止当前生成 |
| `regenerate` | `stream_id` 或上一轮 id | 同上下文重答 |
| `clarify` | `text` | 短追问，可复用 hits |
| `ping` | `ts` | 应用层心跳（可选，协议层另有 ping） |

### 5.2 服务端 → 客户端

| type | 说明 |
|------|------|
| `ready` | 连接就绪 |
| `retrieval` | 可选，检索统计 |
| `delta` | 答案增量（同 116 `message`） |
| `citations` | 引用数组 |
| `done` | `finish_reason`, `stream_id` |
| `error` | `code`, `message` |
| `typing` | 协作场景：他人输入中 |

### 5.3 stream_id 规则

每次 `query` 或 `regenerate` 生成 **新 stream_id**（UUID）。`cancel` 必须带 **正在生成的 stream_id**，避免误杀新一轮。

---

## 6. 与 116 SSE 的事件同构

**团队前端应维护一套解析器**：

```typescript
type RagEvent =
  | { kind: "delta"; text: string }
  | { kind: "citations"; citations: Citation[] }
  | { kind: "done"; finishReason: string };
```

SSE 从 `event:` 行映射；WS 从 `type` 字段映射。`Citation` 形状与 [115 篇](115.source-document-navigation-tutorial.md) 一致。

### 6.1 迁移策略

灰度期 **SSE 默认**；设置页「实验：双向连接」切 WS。后端 **同一 `RagStreamService`** 产出事件，仅 **传输层** 分 SSE/WS。

---

## 7. 中断、重生成与澄清

![流式中断与重生成](image/websocket-rag-streaming/03-cancel-regen.png)

### 7.1 cancel 实现要点

```python
import asyncio

class StreamTask:
    def __init__(self):
        self.task: asyncio.Task | None = None
        self.cancelled = False

    async def run_llm(self, prompt: str, send_delta):
        for ch in fake_chars(prompt):
            if self.cancelled:
                break
            await send_delta(ch)
            await asyncio.sleep(0.02)

    def cancel(self):
        self.cancelled = True
        if self.task and not self.task.done():
            self.task.cancel()
```

**OpenAI 真流**：客户端 abort 后，服务端应 **关闭上游 async iterator**，避免白烧 token（[27 计费](27.token-counting-billing-tutorial.md)）。

### 7.2 regenerate

复用 **同一检索 hits** 或 **强制重检索**——产品策略：

| 策略 | 何时 |
|------|------|
| 复用 hits | 用户只是嫌表述不好 |
| 重检索 | 用户改了问题实质 |

### 7.3 clarify 短追问

「你说的一线城市包括深圳吗？」——可 **不重新 embed 全库**，在 **已有 hits 子集** 上二次生成；仍要更新 [113 引用](113.inline-citation-tutorial.md) 若证据变。

---

## 8. 后端实现：FastAPI WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json, uuid, asyncio

app = FastAPI()
streams: dict[str, StreamTask] = {}

@app.websocket("/ws/rag")
async def rag_ws(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "ready"})
    current = StreamTask()
    try:
        while True:
            msg = await ws.receive_json()
            t = msg.get("type")
            if t == "query":
                stream_id = str(uuid.uuid4())
                hits = mock_retrieve(msg["text"])
                prompt = build_rag_prompt(msg["text"], hits)
                current = StreamTask()
                streams[stream_id] = current

                async def send_delta(ch: str):
                    await ws.send_json({"type": "delta", "stream_id": stream_id, "text": ch})

                async def runner():
                    await current.run_llm(prompt, send_delta)
                    if not current.cancelled:
                        cits = build_citations(hits)
                        await ws.send_json({"type": "citations", "stream_id": stream_id, "citations": cits})
                        await ws.send_json({"type": "done", "stream_id": stream_id, "finish_reason": "stop"})

                current.task = asyncio.create_task(runner())

            elif t == "cancel":
                sid = msg.get("stream_id")
                if sid in streams:
                    streams[sid].cancel()
                await ws.send_json({"type": "done", "stream_id": sid, "finish_reason": "cancelled"})
    except WebSocketDisconnect:
        current.cancel()
```

### 8.1 鉴权

在 `accept` 前校验 **Query token** 或 **首帧 auth**（[6 篇 §11](6.websocket-tutorial.md)）。勿在每条 delta 里带 JWT。

### 8.2 与检索同步

与 [116 篇](116.sse-rag-streaming-tutorial.md) 相同：**先 retrieve 再 delta**；空命中走 `error` + 拒答 [112](112.refusal-strategy-tutorial.md)。

---

## 9. 前端状态机与协作场景

### 9.1 状态机

```text
idle → loading_retrieval → streaming → finalizing_citations → idle
         ↑ cancel anywhere → cancelled
```

### 9.2 协作旁听

多客户端 join `room:{session_id}`（需房间服务）；服务端 **广播 delta** 给旁听者；**写权限** 仍只属于提问者 JWT 角色。

### 9.3 与 [22 流式 UI](ENTERPRISE_RAG_ROADMAP.md) 一致

停止按钮在 `streaming` 态 enabled；`cancel` 后保留 **已渲染 partial answer**，标「已停止」。

---

## 10. 先错对对：五种典型翻车

### 10.1 错：无 stream_id，cancel 误杀下一轮

**对**：每轮 UUID；cancel 只作用于匹配 id。

### 10.2 错：cancel 只停前端，服务端继续烧 token

**对**：abort 上游 LLM 流；记录 `cancelled` 计费。

### 10.3 错：WS 传巨型 citations 每帧

**对**：citations **一次**；超大 excerpt 走 REST。

### 10.4 错：没心跳，移动网络静默断连

**对**：协议 ping + 应用 `ping`/`pong`（[6 篇 §8](6.websocket-tutorial.md)）。

### 10.5 错：所有 FAQ 都上 WS「因为高级」

**对**：默认 SSE [116]；WS 只给 **双向清单** 内的产品。

---

## 11. 生产部署、心跳与多实例

### 11.1 Nginx

```nginx
location /ws/rag {
    proxy_pass http://rag_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}
```

### 11.2 多实例 cancel

`stream_id → worker_id` 存 Redis；cancel 消息 **pub 到对应 worker** 或 **sticky session**。

### 11.3 wss 强制

生产 **禁止 ws 明文**；与 [6 篇 §11](6.websocket-tutorial.md) 一致。

---

## 12. 综合概念地图

```text
[6 WS 协议] → 握手/心跳
       ↓
[116 事件同构] → delta / citations / done
       ↓
双向：cancel / regenerate / clarify
       ↓
[113][115] 引用与导航
       ↓
[118] 多轮 messages
```

---

## 13. 常见陷阱与 FAQ

### 13.1 FAQ：WS 是否比 SSE 更快？

**首字延迟相近**；WS 优势在 **交互**，不在物理速度。

### 13.2 FAQ：能否 WS 下行、HTTP 上行？

可行但 **前端复杂**；除非防火墙只封 WS 上行，不推荐。

### 13.3 FAQ：Socket.IO 可以吗？

可以，但 **多一层协议**；团队已标准化原生 WS 时别引入两套。

### 13.4 故障排查

| 现象 | 处理 |
|------|------|
| 握手 404 | Nginx Upgrade |
| cancel 无效 | stream_id / worker 路由 |
| 断连 | 心跳 / 超时 |

---

## 14. 总结与系列下一步

WebSocket 流式 RAG 解决的是 **双向控制**：**cancel、重生成、澄清、协作**——不是替代 [116 SSE](116.sse-rag-streaming-tutorial.md) 的默认地位。消息 JSON **与 SSE 事件同构**，降低双栈成本；生产务必 **wss、鉴权、多实例 cancel 路由**。

**建议下一步**：[118 多轮历史](118.multi-turn-history-tutorial.md)、复习 [6 WebSocket](6.websocket-tutorial.md)、[124 Function Calling](124.function-calling-tool-use-tutorial.md)。

---

*系列：C6 生成与 Grounding · 路线图第 134 条 · 地基篇*
'''

ARTICLE_118 = r'''# C6 生成与 Grounding（九）：多轮对话历史管理完全指南

> 单轮 RAG 像 **闭卷一题**；真实产品里用户会连问五轮，「那二线城市呢」「刚才那个能报销吗」——若你把 **整段聊天记录** 无差别塞进 prompt，[28 上下文窗口](28.context-window-tutorial.md) 爆掉、[107 Context 预算](107.context-budget-tutorial.md) 挤掉证据；若 **只取最后一句** 去检索，又会 **丢指代**。**多轮对话历史管理**（Multi-turn History）解决 **存什么、拼什么、占多少 token、检索是否每轮重做**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 轨第九篇**（路线图第 **135** 条），**地基篇**。前置：[30 提示词角色](30.prompt-roles-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)、[109 会话查询增强](109.conversation-query-enhancement-tutorial.md)、[116 SSE RAG](116.sse-rag-streaming-tutorial.md)。

---

## 目录

1. [前言：历史不是免费上下文](#1-前言历史不是免费上下文)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [历史在 RAG 中的角色](#3-历史在-rag-中的角色)
4. [Session 数据模型](#4-session-数据模型)
5. [历史与窗口预算](#5-历史与窗口预算)
6. [历史增强检索：每轮独立 search_query](#6-历史增强检索每轮独立-search_query)
7. [拼 messages：展示历史 vs 生成历史](#7-拼-messages展示历史-vs-生成历史)
8. [与流式接口的传参](#8-与流式接口的传参)
9. [综合实战：Session Store + Mini-RAG](#9-综合实战session-store--mini-rag)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [观测、合规与删除](#11-观测合规与删除)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：历史不是免费上下文

用户与知识库助手对话：

| 轮次 | 用户 | 若错误处理 |
|------|------|------------|
| 1 | 2024 差旅一线住宿标准？ | — |
| 2 | 那二线城市呢？ | 只搜「二线城市」→ 偏 |
| 3 | 试用期有吗？ | 丢「住宿/差旅」 |
| 4 | 和去年比改了什么？ | 需绑定「2024 政策」 |

**多轮对话历史管理**：在服务端维护 **session 级对话状态**，按策略把 **最近 N 轮、摘要、实体栈** 用于 **(a) 检索 query 增强** [109](109.conversation-query-enhancement-tutorial.md)、**(b) 生成 prompt 拼 messages**；并受 **token 预算** 约束。  
通俗说：**秘书的会议记录**——不是把录音全文塞给领导，而是 **记要点 + 最近几句原话**。

**Conversation Buffer**（全量缓冲）：每轮 user/assistant 原文都进 store——简单，**不可扩展**。  
**Sliding Window**（滑动窗口）：只保留最近 `k` 轮或 `m` token。  
**Summary Memory**（摘要记忆）：远古轮次压缩，见 [119 篇](119.summary-memory-tutorial.md)。

**读完本文，你应该能做到：**

1. 设计 **session 表结构**（`session_id`、`turns`、`user_id`）。  
2. 实现 **滑动窗口** 与 **历史 token 计数**（[28 篇](28.context-window-tutorial.md)）。  
3. 每轮用 [109](109.conversation-query-enhancement-tutorial.md) 产出 **standalone search_query** 再检索。  
4. POST [116 SSE](116.sse-rag-streaming-tutorial.md) / [117 WS](117.websocket-rag-streaming-tutorial.md) 时传 `messages[]`。  
5. 识别 §10 五种翻车。  
6. 说明 **历史不替代向量库证据**（每轮仍检索）。

### 1.1 C6 轨位置

```text
133 SSE / 134 WebSocket
135 多轮历史 ← 本篇
136 Summary Memory
137 指代消解
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 会话 | session / thread | 多轮对话容器 |
| 轮次 | turn | 一对 user+assistant |
| 滑动窗口 | sliding window | 只留最近 k 轮 |
| 独立检索 | per-turn retrieval | 每问重新搜库 |
| 展示历史 | display history | 前端看到的记录 |

---

## 2. 本文边界与动手路径

**档位：C6 地基篇（路线图 135）。**

**本文讲：** session 模型、预算、检索增强分工、拼 messages、与流式传参、实战。  
**本文不讲：** 完整指代模型（[120 篇](120.coreference-resolution-tutorial.md)）、摘要算法细节（[119 篇](119.summary-memory-tutorial.md)）、合规律师意见全文。

### 2.1 动手路径表

| 步骤 | 验收 |
|------|------|
| A | 画 session 字段 |
| B | 滑动窗口 k=6 |
| C | 109 改写二轮 query |
| D | §9 端到端 |
| E | §10 五种错 |

**环境：** Python 3.10+；内存或 Redis session；可选 OpenAI。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| messages 角色 | [30 提示词角色](30.prompt-roles-tutorial.md) |
| 窗口与 token | [28 Context Window](28.context-window-tutorial.md)、[27 Token 计数](27.token-counting-billing-tutorial.md) |
| 会话 query 增强 | [109 会话查询增强](109.conversation-query-enhancement-tutorial.md) |
| Context 预算 | [107 Context 预算](107.context-budget-tutorial.md) |
| Prompt 模板 | [110 RAG Prompt](110.rag-prompt-template-tutorial.md) |

---

## 3. 历史在 RAG 中的角色

![多轮历史管什么？](image/multi-turn-history/01-history-role.png)

### 3.1 历史管三件事，不管一件事

| 管 | 不管 |
|----|------|
| 用户意图延续 | **代替知识库** |
| 指代/省略补全（配合 109） | 把旧答案当永久事实 |
| 生成语气连贯 | 只检索一次用到底 |

**铁律**：每轮用户新问题 → **重新 retrieve**（除非产品明确「仅闲聊续写」）。

### 3.2 两条链路

```text
链路 A（检索）：history → standalone search_query → embed/BM25
链路 B（生成）：system + history + 新 evidence + 当前 user → LLM
```

链路 A 与 B **可用不同历史裁剪**（见 §7）。

### 3.3 与纯 ChatGPT 的差异

纯聊天 **无外部证据**，历史是全部「知识」。RAG 里 **证据每轮更新**；历史只帮 **理解用户在问什么**。

---

## 4. Session 数据模型

### 4.1 最小字段

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class Turn:
    role: str  # user | assistant
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    meta: dict[str, Any] = field(default_factory=dict)  # hit_ids, prompt_version

@dataclass
class Session:
    session_id: str
    user_id: str
    turns: list[Turn] = field(default_factory=list)
    summary: str | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)
```

### 4.2 存储选型

| 阶段 | 方案 |
|------|------|
| PoC | 进程内 `dict` |
| 生产 | Redis 热 + Postgres 冷 |
| 审计 | 只追加日志表 |

### 4.3 与 user_id 绑定

**禁止** 客户端自报 `session_id` 就读他人会话——服务端用 **JWT user_id** 校验所有权。

---

## 5. 历史与窗口预算

![历史占用窗口预算](image/multi-turn-history/02-window-budget.png)

### 5.1 预算分桶（配合 [107 篇](107.context-budget-tutorial.md)）

| 桶 | 建议占比（可调） |
|----|------------------|
| system + 模板 | 5～15% |
| 历史 | ≤25% |
| 检索 evidence | 50～70% |
| 用户问题 + 输出预留 | 余量 |

### 5.2 滑动窗口参数

| 参数 | 典型值 |
|------|--------|
| `max_turns` | 6～10 轮 |
| `max_history_tokens` | 1500～3000 |
| 超出 | 触发 [119 摘要](119.summary-memory-tutorial.md) 或裁最老 turn |

### 5.3 计数实现

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def count_turns_tokens(turns: list[Turn]) -> int:
    return sum(len(enc.encode(t.content)) for t in turns)
```

---

## 6. 历史增强检索：每轮独立 search_query

![多轮 → 检索 query](image/multi-turn-history/03-query-rewrite.png)

### 6.1 流程

```text
用户 utterance + 最近 N 轮 → [109 增强器] → search_query → 向量库
```

示例：

| 用户说 | standalone search_query |
|--------|-------------------------|
| 那二线城市呢？ | 2024 差旅政策二线城市住宿标准 |
| 刚才那个能报销吗？ | 差旅住宿费用报销规定 |

### 6.2 与 [100 Query Rewriting](100.query-rewriting-tutorial.md) 串联

先 **109 跨轮补全**，再 **100 同轮扩展同义词**——顺序不要反。

### 6.3 检索仍带 ACL

多轮不改变 [121 越权过滤](121.unauthorized-doc-filter-tutorial.md)：`where` 仍按当前用户 Principal。

---

## 7. 拼 messages：展示历史 vs 生成历史

### 7.1 前端展示

前端 **可展示全量 turns**（分页加载），与 **送入模型的历史** 分离。

### 7.2 生成用 messages 形状

```python
def build_generation_messages(session: Session, evidence: str, query: str) -> list[dict]:
    msgs = [{"role": "system", "content": SYSTEM_RAG}]
    if session.summary:
        msgs.append({"role": "system", "content": f"对话摘要：{session.summary}"})
    for t in trim_turns(session.turns, max_tokens=2000):
        msgs.append({"role": t.role, "content": t.content})
    msgs.append({"role": "user", "content": f"证据：\n{evidence}\n\n问题：{query}"})
    return msgs
```

与 [110 模板](110.rag-prompt-template-tutorial.md)、[111 注入格式](111.context-injection-format-tutorial.md) 对齐。

### 7.3 assistant 历史要不要带引用？

建议 **存储 assistant 原文（含 [n]）** 便于审计；下一轮生成时 **可 strip 引用标** 减 token，但保留 **事实句**。

---

## 8. 与流式接口的传参

### 8.1 SSE POST body（[116 篇](116.sse-rag-streaming-tutorial.md)）

```json
{
  "session_id": "sess_abc",
  "query": "那二线城市呢？",
  "messages": [
    {"role": "user", "content": "一线住宿标准？"},
    {"role": "assistant", "content": "一线500元/晚[1]。"}
  ]
}
```

服务端：**合并 session store 与 body**（以 store 为准，body 仅增量）。

### 8.2 WebSocket（[117 篇](117.websocket-rag-streaming-tutorial.md)）

`query` 帧带 `session_id`；历史从 store 读，**减少每帧体积**。

### 8.3 生成结束后写回 session

**在 `done` 后** append user turn + assistant 完整答案——勿在首 token 前写，避免失败会话污染。

---

## 9. 综合实战：Session Store + Mini-RAG

```python
class InMemorySessionStore:
    def __init__(self):
        self._data: dict[str, Session] = {}

    def get(self, sid: str) -> Session | None:
        return self._data.get(sid)

    def append_turn(self, sid: str, turn: Turn):
        s = self._data.setdefault(sid, Session(session_id=sid, user_id="demo"))
        s.turns.append(turn)
        s.updated_at = datetime.utcnow()

store = InMemorySessionStore()

def rag_turn(session_id: str, user_text: str) -> str:
    sess = store.get(session_id) or Session(session_id=session_id, user_id="demo")
    search_q = enhance_query(user_text, sess.turns[-6:])  # 109
    hits = mock_retrieve(search_q)
    evidence = format_evidence(hits)
    msgs = build_generation_messages(sess, evidence, user_text)
    answer = fake_llm(msgs)
    store.append_turn(session_id, Turn("user", user_text))
    store.append_turn(session_id, Turn("assistant", answer, meta={"hit_ids": [h["id"] for h in hits]}))
    return answer
```

### 9.1 验收清单

- [ ] 第二轮「二线城市」检索 query 含「住宿」  
- [ ] 历史超阈值触发 trim  
- [ ] 每轮 `hit_ids` 可不同  
- [ ] session 按 user 隔离  

---

## 10. 先错对对：五种典型翻车

### 10.1 错：把第一轮检索 chunks 缓存到底，后面轮轮复用

**对**：每轮 **新 retrieve**（除非 clarify 子集策略 [117 篇](117.websocket-rag-streaming-tutorial.md)）。

### 10.2 错：历史无限增长塞 prompt

**对**：滑动窗口 + [119 摘要](119.summary-memory-tutorial.md)。

### 10.3 错：检索用最后一句，生成却塞 50 轮

**对**：两链路 **分别裁剪**（§7）。

### 10.4 错：不存 assistant，下一轮模型「失忆」

**对**：至少存 **最近 N 轮 assistant**。

### 10.5 错：session_id 可枚举读他人会话

**对**：UUID + **user_id 校验**。

---

## 11. 观测、合规与删除

### 11.1 埋点

`session_id`、`turn_index`、`history_tokens`、`search_query`、`hit_count`、`latency_retrieval`。

### 11.2 GDPR 删除

提供 **DELETE /sessions/{id}**；级联 Redis + DB；日志 **匿名化**。

### 11.3 与 [119 摘要](119.summary-memory-tutorial.md) 衔接

`summary_version` 变更打 audit；压缩失败 **回滚** 全量 recent turns。

---

## 12. 综合概念地图

```text
[28 窗口] + [107 预算]
       ↓
[118 session] → turns / summary
       ↓
[109 增强] → search_query → 检索
       ↓
[110][111] → messages + evidence
       ↓
[116][117] 流式输出 → 写回 turn
```

---

## 13. 常见陷阱与 FAQ

### 13.1 FAQ：历史要进向量库吗？

**一般不要**——对话是 **session 存储**；知识在 **文档索引**。例外：长期记忆产品（超出本篇）。

### 13.2 FAQ：多轮是否要多跳检索？

复杂对比题可能需要 [104 多跳](104.multi-hop-retrieval-tutorial.md)——与历史管理 **正交**。

### 13.3 FAQ：system 里放历史还是 user？

**摘要可放 system**；**逐轮对话** 用 user/assistant 角色（[30 篇](30.prompt-roles-tutorial.md)）。

---

## 14. 总结与系列下一步

多轮历史管理的核心：**session 有界存储**、**检索 query 每轮增强**、**生成 messages 受预算约束**、**证据每轮刷新**。与 [109](109.conversation-query-enhancement-tutorial.md) 分工：本篇管 **状态与预算**，109 管 **改写算法**。

**下一步**：[119 Summary Memory](119.summary-memory-tutorial.md)、[120 指代消解](120.coreference-resolution-tutorial.md)、[116 SSE](116.sse-rag-streaming-tutorial.md)。

---

*系列：C6 生成与 Grounding · 路线图第 135 条 · 地基篇*
'''

ARTICLE_124 = r'''# C6 生成与 Grounding（十五）：Function Calling 与 Tool Use 完全指南

> RAG 的「工具」本质上是 **让模型决定何时查知识库、何时调外部 API**——而不是把所有函数写死在 prompt 里。**Function Calling**（OpenAI 术语）/ **Tool Use**（Anthropic 等术语）用 **结构化 schema** 描述工具，模型返回 **`tool_calls`**，由应用执行后再 **把结果塞回 messages** 继续生成。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 了解篇**（路线图第 **141** 条），讲清 **RAG 场景下的 search 工具、调用循环、与 [123 JSON Mode](123.structured-output-json-tutorial.md) 的边界**。前置：[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、[30 提示词角色](30.prompt-roles-tutorial.md)、[91 稠密检索](91.dense-retrieval-tutorial.md)、[110 RAG Prompt](110.rag-prompt-template-tutorial.md)。

---

## 目录

1. [前言：从「硬编码检索」到「模型路由」](#1-前言从硬编码检索到模型路由)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [工具与 RAG 的关系](#3-工具与-rag-的关系)
4. [Function Calling 协议复习](#4-function-calling-协议复习)
5. [工具定义要素：name、description、parameters](#5-工具定义要素namedescriptionparameters)
6. [RAG 典型工具：search_kb、get_document](#6-rag-典型工具search_kbget_document)
7. [工具调用循环](#7-工具调用循环)
8. [与硬编码 Pipeline 的对照](#8-与硬编码-pipeline-的对照)
9. [综合实战：两工具 Mini Agent](#9-综合实战两工具-mini-agent)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [安全、权限与观测](#11-安全权限与观测)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：从「硬编码检索」到「模型路由」

传统 RAG 流水线：

```text
用户问题 → 必定 retrieve → 必定 generate
```

产品演进后常见问题：

| 用户说 | 硬编码 RAG | 理想行为 |
|--------|------------|----------|
| 今天上海天气？ | 仍搜员工手册 | **调天气 API** |
| 年假几天？ | 检索手册 | search_kb |
| 你好 | 空检索胡答 | **直接闲聊** |

**Tool Use**：模型先看问题，再选 **search_kb** / **get_weather** / **直接回复**。  
通俗说：**前台分诊**——不是每个来客都拉进档案室。

**读完本文，你应该能做到：**

1. 写 **OpenAI 兼容 tools[]** 定义。  
2. 跑通 **tool_call → execute → tool message → 最终答案** 循环。  
3. 把 **search_kb** 接到你的 Chroma/FAISS（[76](76.chroma-vector-db-tutorial.md)、[75](75.faiss-ann-tutorial.md)）。  
4. 说明 **何时仍用硬编码 RAG**（合规、成本、可预测性）。  
5. 识别 §10 五种翻车。

### 1.1 C6 位置

```text
123 JSON Mode（答案形状）
141 Function Calling ← 本篇（了解）
D 轨 LangChain 125+
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 工具 | tool / function | 模型可调用的外部能力 |
| 工具调用 | tool_call | 模型输出的调用请求 |
| 工具结果 | tool result / tool message | 执行后回填 |
| 路由 | routing | 选哪个工具 |
| Agent 循环 | agent loop | 多轮 tool 直到停 |

---

## 2. 本文边界与动手路径

**档位：C6 了解篇（路线图 141）。**

**本文讲：** 工具 schema、RAG 工具、调用循环、安全、Mini 实战。  
**本文不讲：** 完整 ReAct 论文、LangGraph 状态机（D 轨深入）、任意 MCP 全生态。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 读懂 tools JSON |
| B | 单工具 search_kb |
| C | §9 两工具循环 |
| D | §10 五种错 |

**环境：** Python 3.10+、`openai`；可选本地向量库。

---

## 3. 工具与 RAG 的关系

![RAG 何时走工具](image/function-calling-tool-use/01-tool-rag-flow.png)

### 3.1 三种路径

```text
路径 1：硬编码 RAG（C1～C5 主线）— 可预测、易审计
路径 2：单工具 search_kb — 模型决定「要不要查」
路径 3：多工具 Agent — 查库 + 算数 + 调业务 API
```

### 3.2 企业落地建议

| 场景 | 建议 |
|------|------|
| 合规 FAQ | **硬编码 RAG** + 固定 ACL |
| 混合闲聊+知识 | search_kb 工具 |
| 复杂办事流程 | 多工具 + 人工审批 |

**了解篇定位**：你要知道 **工具是什么**；生产 **默认仍硬编码**，除非产品明确要路由。

---

## 4. Function Calling 协议复习

### 4.1 请求形状（OpenAI 兼容）

```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_kb",
        "description": "当需要公司制度、政策、手册事实时调用；输入为独立完整问句。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索用问句"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
}]
```

### 4.2 响应中的 tool_calls

```json
{
  "role": "assistant",
  "tool_calls": [{
    "id": "call_abc",
    "type": "function",
    "function": {"name": "search_kb", "arguments": "{\"query\":\"年假天数\"}"}
  }]
}
```

### 4.3 回填 tool message

```python
messages.append({
    "role": "tool",
    "tool_call_id": "call_abc",
    "content": json.dumps({"chunks": [...]}, ensure_ascii=False),
})
```

再 **第二次** `chat.completions.create` 得最终自然语言答案。

---

## 5. 工具定义要素

![工具 Schema 要素](image/function-calling-tool-use/02-tool-schema.png)

| 要素 | 要点 |
|------|------|
| `name` | 蛇形命名，稳定不改 |
| `description` | **何时调用**比「是什么」更重要 |
| `parameters` | JSON Schema；必填列 `required` |
| 返回值 | 应用自定；建议 JSON 字符串 |

**坏 description**：「搜索工具」。  
**好 description**：「仅当用户问公司内部文档且需事实依据时调用；不要用于天气、新闻。」

---

## 6. RAG 典型工具

### 6.1 search_kb

```python
def search_kb(query: str, top_k: int = 5) -> dict:
    hits = collection.query(query_texts=[query], n_results=top_k)  # [76 Chroma]
    return {
        "chunks": [
            {"id": id_, "text": doc, "metadata": meta}
            for id_, doc, meta in zip(...)
        ]
    }
```

### 6.2 get_document（可选）

用户指定 `doc_id` 时 **拉全文或目录**——适合 [65 Parent Document](65.parent-document-retriever-tutorial.md) 场景。

### 6.3 工具内 ACL

search_kb **必须** 带 `user_principal`，内部 `where` 过滤（[53 ACL](53.metadata-acl-tutorial.md)、[121 越权](121.unauthorized-doc-filter-tutorial.md)）——**勿信模型** 传的 tenant。

---

## 7. 工具调用循环

![工具调用循环](image/function-calling-tool-use/03-agent-loop.png)

```python
def run_agent(user_query: str, messages: list):
    messages = messages + [{"role": "user", "content": user_query}]
    while True:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            result = dispatch_tool(name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })
```

### 7.1 最大步数

设 `max_tool_rounds=3`，防 **无限查库** 烧 token（[27 计费](27.token-counting-billing-tutorial.md)）。

### 7.2 parallel_tool_calls

OpenAI 可并行多个 call；RAG **建议关闭或限制**——一次一问一检索。

---

## 8. 与硬编码 Pipeline 的对照

| 维度 | 硬编码 RAG | Tool RAG |
|------|------------|----------|
| 可预测性 | 高 | 中 |
| 闲聊误检索 | 低（可加分类器） | 依赖模型 |
| 审计 | 固定步骤 | 需 log 每步 tool |
| 延迟 | 一次检索 | 可能多轮 |
| 适合 | 企业 FAQ | 混合助手 |

**务实组合**：**规则先分流**——明显闲聊不走 LLM 路由；边界 case 才 tools。

---

## 9. 综合实战：两工具 Mini Agent

```python
TOOLS = [search_kb_tool_def, get_weather_tool_def()]

def dispatch_tool(name: str, args: dict):
    if name == "search_kb":
        return search_kb(args["query"], args.get("top_k", 5))
    if name == "get_weather":
        return {"city": args["city"], "temp_c": 28, "source": "mock"}
    raise ValueError(name)

# 用户：「上海今天热吗？顺便年假几天？」
# 模型可能：先 weather，再 search_kb，再综合答
```

### 9.1 与 [110 Prompt](110.rag-prompt-template-tutorial.md)

system 仍写 **引用规则**：search_kb 返回后 **最终答案须带 [n]**（若你走 citation 流程）。

### 9.2 与 [123 JSON](123.structured-output-json-tutorial.md)

最终步可同时 `response_format` JSON **answer+citations**；tool 阶段仍用 **tool message**。

---

## 10. 先错对对：五种典型翻车

### 10.1 错：工具 description 含糊，该搜不搜

**对**：描述 **触发条件 + 反例**。

### 10.2 错：tool 结果塞全文 50  chunk

**对**：截断 + top_k；大文本 [107 预算](107.context-budget-tutorial.md)。

### 10.3 错：无 max_rounds，模型循环 search

**对**：上限 + 相同 query 去重。

### 10.4 错：工具执行无 ACL

**对**：服务端强制 filter。

### 10.5 错：把 SQL 执行交给模型 tool

**对**：参数化、白名单表（安全）；RAG 篇不展开。

---

## 11. 安全、权限与观测

### 11.1 工具白名单

只注册 **业务需要的工具**；勿开放任意 `run_python`。

### 11.2 日志

`tool_name`、`args_hash`、`latency`、`chunk_ids`、`user_id`。

### 11.3 与 [122 内容安全](122.content-safety-filter-tutorial.md)

tool 返回内容 **同样过滤** 再进下一轮 messages。

---

## 12. 综合概念地图

```text
[35 API] → tools / tool_calls
       ↓
search_kb → [76][91] 向量库
       ↓
tool message 回填
       ↓
最终答案 + [113] 引用
```

---

## 13. 常见陷阱与 FAQ

### 13.1 FAQ：Function Calling 等于 Agent 吗？

**Agent 通常 = 多步 tool 循环 + 规划**；单工具 search_kb 只是 **入门**。

### 13.2 FAQ：和 [109 查询增强](109.conversation-query-enhancement-tutorial.md)？

109 在 **检索前改写**；tool 是 **模型决定是否检索**——可并存。

### 13.3 FAQ：流式 [116](116.sse-rag-streaming-tutorial.md)？

tool 循环 **通常非流式**；最终答案步可流式。UX 需 **「正在查资料…」** 状态。

---

## 14. 总结与系列下一步

Function Calling 让 RAG **从固定管线变成可选能力**——适合 **混合场景**；企业 FAQ **默认硬编码** 更稳。掌握 **schema、循环、ACL、max_rounds** 即可与 D 轨 LangChain 衔接。

**下一步**：[125 LangChain 核心](125.langchain-core-tutorial.md)、[127 Retriever](127.langchain-retriever-tutorial.md)、[120 指代](120.coreference-resolution-tutorial.md) 里 Agent 实体栈。

---

*系列：C6 生成与 Grounding · 路线图第 141 条 · 了解篇*
'''

ARTICLE_125 = r'''# D 框架与编排（一）：LangChain 核心概念完全指南

> 你已经用裸 Python 跑通了 **retrieve → prompt → OpenAI**（[35 篇](35.openai-compatible-api-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[110 Prompt](110.rag-prompt-template-tutorial.md)）。代码一多，开始出现 **三套 prompt 字符串、五种检索调用、日志各写各的**。**LangChain** 不是替代你的向量库，而是提供 **可组合的抽象层**：`ChatModel`、`PromptTemplate`、`Runnable`、回调与配置。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 轨第一篇**（路线图第 **142** 条），**地基篇**——**D 模块起点**。前置：[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、[30 提示词角色](30.prompt-roles-tutorial.md)、[91 稠密检索](91.dense-retrieval-tutorial.md)。

---

## 目录

1. [前言：为什么要多一层框架](#1-前言为什么要多一层框架)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LangChain 是什么、不是什么](#3-langchain-是什么不是什么)
4. [包结构：core、community、partner](#4-包结构corecommunitypartner)
5. [Runnable 统一接口](#5-runnable-统一接口)
6. [ChatModel 与消息类型](#6-chatmodel-与消息类型)
7. [PromptTemplate 与变量](#7-prompttemplate-与变量)
8. [OutputParser 入门](#8-outputparser-入门)
9. [回调、配置与调试](#9-回调配置与调试)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [与裸 SDK 对照](#11-与裸-sdk-对照)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：为什么要多一层框架

Mini-RAG 脚本 80 行很香；十个脚本以后：

| 痛点 | LangChain 思路 |
|------|----------------|
| `openai.ChatCompletion` 与新版 SDK 混用 | 统一 `ChatOpenAI` |
| prompt 字符串散落 | `ChatPromptTemplate` 版本化 |
| 想换 Claude 要改一片 | 换 `ChatModel` 构造 |
| 想 `.stream()` 每处重写 | `Runnable` 统一 stream |

**LangChain Core**（`langchain-core`）：**与供应商无关** 的抽象与 LCEL 管道（[126 篇](126.langchain-lcel-tutorial.md)）。  
通俗说：**电源插座标准**——电器（RAG 链）不关心墙上是国标还是欧标，只要 **插头匹配 Runnable**。

**读完本文，你应该能做到：**

1. 说清 **core vs community** 分工。  
2. 用 `ChatOpenAI` + `ChatPromptTemplate` 完成一次 invoke。  
3. 理解 **Runnable** 的 `invoke` / `stream` / `batch`。  
4. 知道 **何时不必上 LangChain**（脚本少、团队无共识）。  
5. 为 [126 LCEL](126.langchain-lcel-tutorial.md)、[127 Retriever](127.langchain-retriever-tutorial.md) 打地基。

### 1.1 D 轨位置

```text
C 轨：手写 RAG 全链路
D 轨起点：
142 LangChain 核心 ← 本篇
143 LCEL
144 Retriever
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 可运行体 | Runnable | 统一调用接口 |
| 聊天模型 | ChatModel | 吃 messages 出 AIMessage |
| 提示模板 | PromptTemplate | 变量填空 |
| 输出解析 | OutputParser | 字符串→结构 |
| 伙伴包 | partner package | 各厂商集成 |

---

## 2. 本文边界与动手路径

**档位：D 轨地基篇（路线图 142）。**

**本文讲：** 生态分层、Runnable、ChatModel、Prompt、Parser 入门、回调。  
**本文不讲：** 每一个 community 集成、LangGraph 多 Agent、生产部署全家桶。

### 2.1 动手路径

```bash
pip install langchain-core langchain-openai langchain-community
```

| 步骤 | 验收 |
|------|------|
| A | import 成功 |
| B | 单次 invoke |
| C | `.stream()` 打印 |
| D | §10 四种错 |

需 `OPENAI_API_KEY` 或兼容网关（[35 篇](35.openai-compatible-api-tutorial.md)）。

---

## 3. LangChain 是什么、不是什么

![LangChain 生态分层](image/langchain-core/01-lc-stack.png)

### 3.1 是什么

- **抽象层**：统一 LLM、Embedding、VectorStore、Retriever 的 **调用形状**；  
- **组合层**：LCEL `|` 管道（下篇）；  
- **集成层**：`langchain-chroma`、`langchain-openai` 等。

### 3.2 不是什么

- **不是** 新向量数据库；  
- **不是** 必需中间件——[76 Chroma](76.chroma-vector-db-tutorial.md) 仍可直接 `collection.query`；  
- **不是** 银弹——复杂业务仍需 **你自己的 ACL、评测、流式契约**（[116 SSE](116.sse-rag-streaming-tutorial.md)）。

### 3.3 何时引入

| 信号 | 建议 |
|------|------|
| ≥3 条 RAG 链重复 60% 代码 | 考虑 |
| 要换模型/换库 A/B | 考虑 |
| 单人脚本 PoC | 可裸写 |

---

## 4. 包结构

| 包 | 职责 |
|----|------|
| `langchain-core` | Runnable、messages、基础接口 |
| `langchain-openai` | OpenAI Chat、Embeddings |
| `langchain-community` | 大量第三方集成（选装） |
| `langchain-chroma` 等 | 单库 partner |

**生产建议**：**最小依赖**——只装用到的 partner，避免 `community` 全家桶膨胀。

---

## 5. Runnable 统一接口

![Runnable 抽象](image/langchain-core/02-runnable-idea.png)

```python
from langchain_core.runnables import RunnableLambda

def add_exclaim(text: str) -> str:
    return text + "!"

r = RunnableLambda(add_exclaim)
print(r.invoke("hello"))   # hello!
print(list(r.stream("hi")))  # 流式同样接口
print(r.batch(["a", "b"]))   # ['a!', 'b!']
```

**ChatModel、Prompt、Parser、Retriever** 全是 Runnable——故可 `|` 组合（[126 篇](126.langchain-lcel-tutorial.md)）。

### 5.1 Config 与 tags

```python
model.invoke(messages, config={"tags": ["rag", "prod"], "metadata": {"session_id": "x"}})
```

对接 LangSmith 等观测（了解即可）。

---

## 6. ChatModel 与消息类型

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
messages = [
    SystemMessage(content="你是企业知识库助手。"),
    HumanMessage(content="年假几天？"),
]
resp = llm.invoke(messages)
print(resp.content)
```

与 [30 篇](30.prompt-roles-tutorial.md) 角色对应：`SystemMessage`、`HumanMessage`、`AIMessage`。

### 6.1 流式

```python
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
```

对接 [116 SSE](116.sse-rag-streaming-tutorial.md) 时，在 **FastAPI 层** 把 chunk 转成 SSE 事件，LangChain 只负责 **产出 delta**。

---

## 7. PromptTemplate 与变量

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "仅根据证据回答，句末 [n] 引用。"),
    ("human", "证据：\n{context}\n\n问题：{question}"),
])
values = {"context": "[1] 年假10天", "question": "年假？"}
msgs = prompt.invoke(values).to_messages()
```

与 [110 RAG Prompt 模板](110.rag-prompt-template-tutorial.md) **一一映射**——把团队 wiki 模板 **搬进 ChatPromptTemplate** 便于版本管理。

---

## 8. OutputParser 入门

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
answer = chain.invoke({"context": "...", "question": "..."})
```

结构化 JSON 用 `JsonOutputParser` 或 Pydantic（配合 [123 JSON Mode](123.structured-output-json-tutorial.md)）。

---

## 9. 回调、配置与调试

```python
from langchain_core.callbacks import StdOutCallbackHandler

llm.invoke(messages, config={"callbacks": [StdOutCallbackHandler()]})
```

开发期看 **token 与延迟**；生产换 **结构化日志回调**。

---

## 10. 先错对对：四种典型翻车

### 10.1 错：pip install langchain 旧单体包，版本地狱

**对**：拆包 **`langchain-core` + partner**，pin 版本。

### 10.2 错：把机密 chunk 打进 LangSmith 默认上传

**对**：关 trace 或 **脱敏**（合规）。

### 10.3 错：以为上了 LangChain 就不用写 ACL

**对**：[121 越权](121.unauthorized-doc-filter-tutorial.md) 仍在 **Retriever 内**。

### 10.4 错：PoC 堆满 community 集成

**对**：**YAGNI**，用到再装。

---

## 11. 与裸 SDK 对照

| 任务 | 裸 OpenAI SDK | LangChain |
|------|---------------|-----------|
| 一次问答 | 10 行 | 15 行（初期略多） |
| 换模型 | 改 import+类 | 改构造器 |
| 流式 | 手写 async for | `llm.stream` |
| 组合检索+生成 | 自写函数 | LCEL `|` |

---

## 12. 综合概念地图

![D 模块概念速记](image/langchain-core/03-module-map.png)

```text
[35 API] → ChatOpenAI (Runnable)
[110 模板] → ChatPromptTemplate
[126 LCEL] → |
[127 Retriever] → 检索 Runnable
[76 Chroma] → VectorStore partner
```

---

## 13. 常见陷阱与 FAQ

### 13.1 FAQ：LangChain 很慢吗？

框架开销 **通常远小于 LLM RTT**；慢在 **模型与检索**，不在 `|`。

### 13.2 FAQ：必须用 LangSmith 吗？

不必；自建日志即可。

### 13.3 FAQ：与 [124 Function Calling](124.function-calling-tool-use-tutorial.md)？

`llm.bind_tools(tools)` 绑定工具——D 轨后续可展开。

---

## 14. 总结与系列下一步

LangChain 核心是 **Runnable 抽象** + **消息/模板/模型** 统一形状——**不替代** 你的 RAG 业务规则。D 轨下一步 **[126 LCEL](126.langchain-lcel-tutorial.md)** 用 `|` 组装链，**[127 Retriever](127.langchain-retriever-tutorial.md)** 接向量库。

**作业**：把 [110 篇](110.rag-prompt-template-tutorial.md) 的 system 模板改成 `ChatPromptTemplate` 并 invoke 一次。

---

*系列：D 框架与编排 · 路线图第 142 条 · 地基篇 · D 模块起点*
'''

ARTICLE_126 = r'''# D 框架与编排（二）：LangChain LCEL 完全指南

> [125 篇](125.langchain-core-tutorial.md) 认识了 **Runnable**；如何把 `prompt`、`llm`、`parser`、**检索** 串成 **一条可流式、可批处理、可观测** 的链？**LCEL**（LangChain Expression Language）用 **管道符 `|`** 表达数据流，是 LangChain 1.x 的 **推荐组合方式**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 轨第二篇**（路线图第 **143** 条），**地基篇**。前置：[125 LangChain 核心](125.langchain-core-tutorial.md)、[110 RAG Prompt](110.rag-prompt-template-tutorial.md)、[91 稠密检索](91.dense-retrieval-tutorial.md)。

---

## 目录

1. [前言：从函数胶水到管道](#1-前言从函数胶水到管道)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LCEL 是什么](#3-lcel-是什么)
4. [管道符与类型流转](#4-管道符与类型流转)
5. [invoke、stream、batch 三件套](#5-invokestreambatch-三件套)
6. [RunnableParallel 与 RunnablePassthrough](#6-runnableparallel-与-runnablepassthrough)
7. [RunnableLambda 与自定义步](#7-runnablelambda-与自定义步)
8. [错误处理与回退](#8-错误处理与回退)
9. [综合实战：最小 RAG LCEL 链](#9-综合实战最小-rag-lcel-链)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [与手写 async 流式对照](#11-与手写-async-流式对照)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：从函数胶水到管道

手写 RAG：

```python
def rag(q):
    hits = retrieve(q)
    ctx = format(hits)
    msgs = build_prompt(ctx, q)
    return llm(msgs)
```

加流式、加 batch、加「并行检索+改写」后函数 **膨胀**。LCEL：

```python
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

**LCEL**：用 **声明式管道** 组合 Runnable；运行时自动处理 **stream 传播**（若各步支持）。  
通俗说：**Unix 管道** `cat file | grep x | wc`，只不过对象是 **messages / 字符串 / 文档列表**。

**读完本文，你应该能做到：**

1. 写 **`a | b | c`** 链并 `invoke`。  
2. 对链 `.stream()` 出打字机。  
3. 用 **RunnableParallel** 并行两路。  
4. 跑通 §9 **检索+生成** LCEL。  
5. 知道链 **如何接 [127 Retriever](127.langchain-retriever-tutorial.md)**。

---

## 2. 本文边界与动手路径

**档位：D 轨地基篇（路线图 143）。**

```bash
pip install langchain-core langchain-openai langchain-chroma
```

| 步骤 | 验收 |
|------|------|
| A | `prompt \| llm \| parser` |
| B | `.stream()` |
| C | §9 RAG 链 |
| D | §10 四种错 |

---

## 3. LCEL 是什么

![LCEL 管道](image/langchain-lcel/01-pipe-chain.png)

### 3.1 核心规则

- `|` 左输出 **尽量匹配** 右输入；  
- 整链是 **一个 Runnable**；  
- 支持 **`.invoke` / `.stream` / `.batch` / `.ainvoke`**。

### 3.2 与 LangChain 0.x Chain 类

旧版 `LLMChain`、`RetrievalQA` **仍可见**；新项目 **优先 LCEL**——更透明、易测。

---

## 4. 管道符与类型流转

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("用一句话解释：{topic}")
llm = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | llm | StrOutputParser()

chain.invoke({"topic": "RAG"})
```

数据流：`dict` → `ChatPromptValue` → `AIMessage` → `str`。

---

## 5. invoke、stream、batch

![stream 与 batch](image/langchain-lcel/02-stream-batch.png)

```python
for chunk in chain.stream({"topic": "SSE"}):
    print(chunk, end="", flush=True)

chain.batch([{"topic": "a"}, {"topic": "b"}])
```

**stream 注意**：`StrOutputParser` 后 stream 的是 **字符串片段**；接 [116 SSE](116.sse-rag-streaming-tutorial.md) 网关时 **逐 chunk 包装事件**。

---

## 6. RunnableParallel 与 RunnablePassthrough

```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

chain = RunnableParallel(
    context=retriever | format_docs,
    question=RunnablePassthrough(),
) | prompt | llm | StrOutputParser()
```

`RunnablePassthrough()` 把 **输入原样** 传到 `question` 键——RAG 常见模式。

### 6.1 勿盲目并行

`rewrite_query` 依赖 `history` 时 **不能** 与 `retrieve` 并行——先改写再检索（[109 篇](109.conversation-query-enhancement-tutorial.md)）。

---

## 7. RunnableLambda

```python
from langchain_core.runnables import RunnableLambda

def format_docs(docs):
    return "\n\n".join(f"[{i+1}] {d.page_content}" for i, d in enumerate(docs))

format_step = RunnableLambda(format_docs)
```

与 [111 注入格式](111.context-injection-format-tutorial.md) 一致。

---

## 8. 错误处理

```python
chain_with_fallback = chain.with_fallbacks([backup_llm | StrOutputParser()])
```

检索空：在 `format_docs` 前 **if not docs: raise** 或走 [112 拒答](112.refusal-strategy-tutorial.md) 分支。

---

## 9. 综合实战：最小 RAG LCEL 链

![RAG 的 LCEL 组装](image/langchain-lcel/03-rag-lcel.png)

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_messages([
    ("system", "仅根据证据回答，引用 [n]。"),
    ("human", "证据：\n{context}\n\n问题：{question}"),
])

def format_docs(docs):
    return "\n\n".join(f"[{i+1}] {d.page_content}" for i, d in enumerate(docs))

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(rag_chain.invoke("年假几天？"))
```

细节见 [127 Retriever 篇](127.langchain-retriever-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)。

### 9.1 流式 RAG

```python
for t in rag_chain.stream("年假？"):
    print(t, end="", flush=True)
```

**citations 收尾** 仍建议 **应用层** 做（[116 篇](116.sse-rag-streaming-tutorial.md)）——LCEL 默认只流 **文本**。

---

## 10. 先错对对

### 10.1 错：dict 键名与 prompt 变量不一致

**对**：`{context}` `{question}` **对齐**。

### 10.2 错：retrieve 输出 Document 直接塞 prompt

**对**：**format_docs** 转字符串。

### 10.3 错：stream 时代码仍 `invoke`

**对**：产品流式用 **`.stream`**。

### 10.4 错：链里无 ACL，Chroma 全库

**对**：`search_kwargs={"filter": {...}}`（[53 ACL](53.metadata-acl-tutorial.md)）。

---

## 11. 与手写 async 对照

| 能力 | 手写 | LCEL |
|------|------|------|
| 可读性 | 函数嵌套 | 管道直观 |
| 单测 | mock 函数 | mock Runnable |
| 流式 | 自己桥接 | `.stream` |
| 调试 | print | callbacks |

---

## 12. 综合概念地图

```text
[125 Runnable] → |
[127 retriever] → context 支路
[110 prompt] → 模板
[116 SSE] → 外层包装 stream
```

---

## 13. FAQ

### 13.1 LCEL 性能？

组合开销 **可忽略**；优化 **检索与模型**。

### 13.2 能否不用 LCEL？

可以 **直接 invoke ChatModel**——链长时再引入。

---

## 14. 总结与系列下一步

LCEL 用 **`|`** 把 RAG 五步收成 **一个 Runnable**，统一 **invoke/stream/batch**。下篇 **[127 Retriever](127.langchain-retriever-tutorial.md)** 专讲检索抽象与 `as_retriever`。

---

*系列：D 框架与编排 · 路线图第 143 条 · 地基篇*
'''

ARTICLE_127 = r'''# D 框架与编排（三）：LangChain Retriever 抽象完全指南

> 向量库会 `query`（[76 Chroma](76.chroma-vector-db-tutorial.md)），但 RAG 链想要的是：**给我字符串问题，还我 `Document` 列表**——与底层是 Chroma、FAISS 还是 BM25 **无关**。**Retriever** 是 LangChain 的 **检索抽象**；`VectorStore.as_retriever()` 是最常见实现。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 轨第三篇**（路线图第 **144** 条），**主线篇**——把 C4/C5 检索能力 **接入 LCEL**。前置：[125 核心](125.langchain-core-tutorial.md)、[126 LCEL](126.langchain-lcel-tutorial.md)、[91 稠密检索](91.dense-retrieval-tutorial.md)、[88 元数据过滤](88.metadata-filter-retrieval-tutorial.md)。

---

## 目录

1. [前言：检索一行接入管道](#1-前言检索一行接入管道)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Retriever 是什么](#3-retriever-是什么)
4. [VectorStoreRetriever 与 as_retriever](#4-vectorstoreretriever-与-as_retriever)
5. [常见 Retriever 类型](#5-常见-retriever-类型)
6. [search_kwargs：k、filter、score_threshold](#6-search_kwargskfilterscore_threshold)
7. [自定义 Retriever](#7-自定义-retriever)
8. [与 LCEL 组装模式](#8-与-lcel-组装模式)
9. [综合实战：过滤 + MultiQuery + RAG 链](#9-综合实战过滤--multiquery--rag-链)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [与 C5 检索策略对照](#11-与-c5-检索策略对照)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：检索一行接入管道

[126 篇](126.langchain-lcel-tutorial.md) 的 RAG 链里有：

```python
{"context": retriever | format_docs, "question": RunnablePassthrough()}
```

`retriever` 从哪来？**不是** 魔法——是实现了 **`invoke(query) -> list[Document]`** 的对象。  
**LangChain Retriever**：检索逻辑的 **可替换插头**；换库、加 MMR、加 MultiQuery **尽量只改 retriever 构造**。

**读完本文，你应该能做到：**

1. `Chroma.as_retriever(search_kwargs={...})` 跑通。  
2. 写 **metadata filter**（[88 篇](88.metadata-filter-retrieval-tutorial.md)）。  
3. 了解 **MultiQueryRetriever**、**ParentDocumentRetriever**（[65 篇](65.parent-document-retriever-tutorial.md)）。  
4. 实现 **自定义 BaseRetriever**。  
5. 把 retriever 接入 **完整 LCEL** 并对照 C5 策略表。

### 1.1 D 轨位置

```text
142 核心 → 143 LCEL → 144 Retriever ← 本篇（主线）
```

---

## 2. 本文边界与动手路径

**档位：D 轨主线篇（路线图 144）。**

```bash
pip install langchain-chroma langchain-openai langchain-community
```

| 步骤 | 验收 |
|------|------|
| A | as_retriever k=5 |
| B | filter doc_id |
| C | §9 完整链 |
| D | §10 五种错 |

---

## 3. Retriever 是什么

![Retriever 抽象](image/langchain-retriever/01-retriever-idea.png)

### 3.1 接口直觉

```python
docs = retriever.invoke("年假几天？")
# [Document(page_content="...", metadata={...}), ...]
```

底层可调 Chroma、FAISS、[75 篇](75.faiss-ann-tutorial.md) 自建、Elasticsearch（[82 篇](82.elasticsearch-vector-tutorial.md)）。

### 3.2 与 VectorStore 分工

| 层 | 职责 |
|----|------|
| VectorStore | add、相似度 search |
| Retriever | **策略**：k、filter、压缩、多查询 |

---

## 4. VectorStoreRetriever

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vs = Chroma(persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings())
retriever = vs.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)
docs = retriever.invoke("差旅住宿")
```

### 4.1 search_type

| 值 | 说明 |
|----|------|
| `similarity` | 默认 top-k |
| `mmr` | 多样性（[105 MMR](105.mmr-diversity-tutorial.md)） |
| `similarity_score_threshold` | 阈值（[99 篇](99.score-threshold-tutorial.md)） |

---

## 5. 常见 Retriever 类型

![Retriever 类型](image/langchain-retriever/02-retriever-types.png)

| 类型 | 场景 |
|------|------|
| VectorStoreRetriever | 标准稠密检索 [91](91.dense-retrieval-tutorial.md) |
| MultiQueryRetriever | LLM 生成多 query 融合 [101](101.multi-query-retrieval-tutorial.md) |
| ParentDocumentRetriever | 小块检索大块阅读 [65](65.parent-document-retriever-tutorial.md) |
| EnsembleRetriever | 稠密+稀疏 [93 混合](93.hybrid-search-tutorial.md) |
| ContextualCompressionRetriever | 检索后压缩 [107 预算](107.context-budget-tutorial.md) |

**了解即可**：先掌握 **VectorStoreRetriever**，再按 bad case **叠加**。

### 5.1 MultiQuery 示例

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

mq = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)
```

**成本**：多次 embed + LLM 改写——对齐 [101 篇](101.multi-query-retrieval-tutorial.md) 延迟账。

---

## 6. search_kwargs

```python
retriever = vs.as_retriever(search_kwargs={
    "k": 8,
    "filter": {"doc_id": "handbook-2024", "acl_group": "all_staff"},
})
```

与 [53 ACL](53.metadata-acl-tutorial.md)、[88 filter](88.metadata-filter-retrieval-tutorial.md) **同一 metadata 字段**。

### 6.1 score_threshold

```python
retriever = vs.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.35, "k": 10},
)
```

见 [99 篇](99.score-threshold-tutorial.md)——**阈值需按模型校准**。

---

## 7. 自定义 Retriever

```python
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun

class HandbookRetriever(BaseRetriever):
    collection: any

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun):
        rows = self.collection.query(query_texts=[query], n_results=5)
        return [
            Document(page_content=txt, metadata=meta)
            for txt, meta in zip(rows["documents"][0], rows["metadatas"][0])
        ]
```

**企业**：在 `_get_relevant_documents` 内 **强制 ACL**（[121 篇](121.unauthorized-doc-filter-tutorial.md)）。

---

## 8. 与 LCEL 组装

![LCEL 中的检索步](image/langchain-retriever/03-lcel-retrieve.png)

```python
from langchain_core.runnables import RunnablePassthrough

rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

### 8.1 itemgetter 变体

```python
from operator import itemgetter

rag = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

输入 **dict** `{"question": "..."}` 时使用。

---

## 9. 综合实战

```python
# 假设 vs、llm、prompt、format_docs 已定义
retriever = vs.as_retriever(search_kwargs={
    "k": 5,
    "filter": {"acl_group": {"$in": ["all_staff"]}},  # 视 Chroma 版本语法调整
})

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("一线住宿标准？")
```

### 9.1 接 [116 SSE](116.sse-rag-streaming-tutorial.md)

```python
async def sse_rag(question: str):
    hits_docs = retriever.invoke(question)
    citations = build_citations(hits_docs)  # 115 篇
    async for text in rag_chain.astream(question):
        yield sse_pack("message", {"delta": text})
    yield sse_pack("citations", {"citations": citations})
```

**检索在流前同步完成**——与 116 契约一致。

### 9.2 接 [118 多轮](118.multi-turn-history-tutorial.md)

```python
def rag_with_history(question: str, history: list):
    search_q = enhance_query(question, history)  # 109
    return rag_chain.invoke(search_q)
```

Retriever 吃 **改写后 query**，不是裸最后一句。

---

## 10. 先错对对

### 10.1 错：换 Embedding 未重建 collection

**对**：[76 篇](76.chroma-vector-db-tutorial.md) 换模型 **新 collection**。

### 10.2 错：k=50 塞爆 [107 预算](107.context-budget-tutorial.md)

**对**：k 配合 **rerank** [95](95.cross-encoder-rerank-tutorial.md)。

### 10.3 错：filter 字段入库不存在

**对**：与 [51 chunk_id](51.metadata-chunk-id-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md) schema 对齐。

### 10.4 错：Retriever 里调 LLM 无超时

**对**：MultiQuery **设超时与 max_queries**。

### 10.5 错：以为 Retriever 等于 Reranker

**对**：Rerank 是 **检索后** 另一步（C5）。

---

## 11. 与 C5 检索策略对照

| C5 篇 | LangChain 落点 |
|-------|----------------|
| [91 稠密](91.dense-retrieval-tutorial.md) | VectorStoreRetriever |
| [93 混合](93.hybrid-search-tutorial.md) | EnsembleRetriever |
| [101 Multi-Query](101.multi-query-retrieval-tutorial.md) | MultiQueryRetriever |
| [105 MMR](105.mmr-diversity-tutorial.md) | search_type=mmr |
| [99 阈值](99.score-threshold-tutorial.md) | similarity_score_threshold |
| [65 Parent](65.parent-document-retriever-tutorial.md) | ParentDocumentRetriever |

**框架是皮**，**策略仍是 C5 灵魂**。

---

## 12. 综合概念地图

```text
[76 Chroma] → VectorStore
       ↓
as_retriever + filter/k/mmr
       ↓
[126 LCEL] context 支路
       ↓
[110][111] prompt
       ↓
[116] 流式 + citations
```

---

## 13. FAQ

### 13.1 不用 LangChain 能否 RAG？

能——[76](76.chroma-vector-db-tutorial.md)+[110](110.rag-prompt-template-tutorial.md) 足够；Retriever 是 **工程化复用**。

### 13.2 Retriever 观测？

`retriever.invoke(q, config={"callbacks": [...]})` 记录 **latency、doc_ids**。

### 13.3 与 [124 tools](124.function-calling-tool-use-tutorial.md)？

`create_retriever_tool(retriever, ...)` 把检索 **暴露给 Agent**。

---

## 14. 总结与系列下一步

LangChain Retriever 把 **C4/C5 检索** 封装成 LCEL 的 **一行插头**：`as_retriever`、**filter**、**MMR/MultiQuery** 按 bad case 叠加。D 轨主线本篇后，继续 **LangGraph、评测编排**（路线图 D 后续）或 **回到 C6 流式** [116](116.sse-rag-streaming-tutorial.md) 做端到端产品。

**作业**：同一问题对比 **k=3 vs k=10** 的答案与 token；加 `acl_group` filter 演示越权不命中。

---

*系列：D 框架与编排 · 路线图第 144 条 · 主线篇*
'''
