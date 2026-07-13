# -*- coding: utf-8 -*-
"""Third-pass bulk Chinese content (~2200+ hanzi per slug)."""

EXPAND3_117 = r'''
## 16. WebSocket RAG 实战周计划与案例库

### 16.1 五天上手路线

周一阅读 6 篇 WebSocket 基础，完成本地 wss 握手 demo，理解 ping 与 close 码。周二阅读 116 篇 SSE 事件契约，画出 message、citations、done 三事件与 WS type 字段映射表。周三实现 8 篇 FastAPI WebSocket 路由，用假 LLM 推送 delta，Postman 或 websocat 验证帧格式。周四加 cancel 与 stream_id，写单测断言取消后不再收到 delta。周五对接前端停止按钮与 regenerate，并写 Nginx Upgrade 配置片段进团队 wiki。

### 16.2 案例：客服工作台双工场景

某保险公司客服工作台需要坐席在模型流式输出时随时插话澄清客户意图。SSE 方案需要额外 HTTP 发澄清句，延迟与状态同步复杂。改 WebSocket 后，clarify 帧与 delta 共用连接，主管旁听通过 join room 广播，平均处理时长下降，但运维增加 Redis 路由与连接数监控。选型结论：仅该工作台走 WS，普通员工 FAQ 仍用 SSE。

### 16.3 案例：误杀上一轮生成

早期实现未带 stream_id，用户快速连点两次提问，第二次 cancel 误杀第一次仍在输出的流，出现答案空白。修复后每次 query 生成 UUID，cancel 只匹配当前 stream_id，并在 done 帧带 finish_reason 区分 stop 与 cancelled，前端据此决定是否保留 partial answer。

### 16.4 消息 JSON 完整样例

客户端发起：`{"type":"query","text":"年假几天","session_id":"s1"}`。服务端推送：`{"type":"delta","stream_id":"u1","text":"年"}` 重复若干次，随后 `{"type":"citations","stream_id":"u1","citations":[...]}`，最后 `{"type":"done","stream_id":"u1","finish_reason":"stop"}`。取消：`{"type":"cancel","stream_id":"u1"}` 对应 `finish_reason":"cancelled"`。

### 16.5 与 118 多轮历史的帧字段

query 帧可只带 session_id 与 text，历史由服务端从 store 读取，减少帧体积。若离线测试无 store，可临时在 body 带 messages 数组，与 116 POST 对齐。生成结束后服务端 append turn，与 SSE 一样在 done 之后写 session，避免失败污染。

### 16.6 安全清单

限制单连接消息频率防刷；限制单帧字节数；校验 JSON schema 防畸形帧；鉴权在 accept 前完成；审计记录 cancel 与 regenerate 行为；生产强制 wss；协作 room join 校验角色；勿在帧内传长期密钥。

### 16.7 性能与容量

单核可支撑连接数受限于事件循环与每流 Task。压测时关注内存：每个流缓存 answer_parts 字符串。连接闲置超时回收，防止僵尸连接占满文件描述符。水平扩展优先 sticky，其次 Redis pubsub cancel。

### 16.8 与 124 Function Calling 的扩展

多工具 Agent 可在同连接推送 status 帧，例如正在调用 search_kb，提升可解释性。工具循环本身仍建议在服务端串行执行，完成后用 delta 流最终答案。不要把工具结果每步都推给最终用户除非产品需要调试模式。

### 16.9 团队分工建议

后端定义帧协议与 cancel 路由；前端实现状态机与停止按钮；运维配置 Ingress 与证书；安全审查 room 旁听权限；QA 编写连点、断网、取消、重生成用例。

### 16.10 背诵与面试

双向刚需场景：中止、澄清、协作。多实例 cancel：stream 映射或粘性。与 SSE 关系：默认 SSE，交互升级 WS。引用仍末尾 citations，与 113、115 一致。
'''

EXPAND3_118 = r'''
## 16. 多轮历史实战周计划与案例库

### 16.1 五天上手路线

周一理解 session 与 turn 数据模型，画出 Redis 键结构。周二实现滑动窗口 trim 与 token 计数，对照 28 篇窗口限制做单元测试。周三接 109 改写器，准备二十条中文追问金标。周四把 session 接入 116 POST body 或 117 query 帧，验证二轮召回提升。周五补 DELETE 会话与观测字段，写预算饼图文案给产品。

### 16.2 案例：差旅助手十二轮对话

用户从住宿标准问到报销比例再问到审批人邮箱模板。若全量历史塞 prompt，证据块被裁，模型胡编邮箱。改滑动六轮加摘要后，历史块稳定在一千八百 token 内，证据保留五条政策 chunk，faithfulness 评分回升。教训：历史与证据抢预算时，优先保证证据完整。

### 16.3 案例：检索未改写导致偏题

二轮用户说「那二线城市呢」，检索直接用原句，召回城市等级介绍而非差旅标准。接入规则改写后，search_query 变为「2024差旅政策二线城市住宿标准」，Recall 明显提升。团队将金标纳入 CI，防止改写回归。

### 16.4 Session API 错误设计反思

曾允许客户端任意指定 session_id 导致串会话。修复为服务端签发 UUID，且 get 时校验 user_id。曾把 assistant 不存库导致第三轮指代失忆。修复为 done 后写回 assistant 全文。

### 16.5 预算表模板

假设模型上下文 16K，system 占 800，输出预留 1024，安全余量 500，历史上限 2500，则证据约 11K token 量级。表格写入 107 篇运维手册，换模型时只改一行上限重新计算。

### 16.6 与 119 摘要的衔接

当历史 token 超 2000 触发异步摘要，摘要块放 system 之后、证据之前。摘要失败回滚上一版 summary_version，临时加大滑动窗口保留更多原文。压缩频率过高会丢指代，过低则费 token，需 A/B。

### 16.7 与 120 指代消解分工

118 管存与预算，109 管改写，120 管更复杂的指代解析与实体栈。不要三篇混成一个黑盒，否则 bad case 无法定位是存丢了、改错了、还是指代错了。

### 16.8 合规要点

提供导出与删除会话；日志脱敏；禁止跨租户 session 复用；敏感行业限制历史保留天数；审计谁看过哪段对话。

### 16.9 观测指标

每会话轮数、历史 token、改写前后 query 相似度、每轮 hit 数变化、用户重复提问率。重复提问高可能指代或摘要失败。

### 16.10 作业与面试

作业：Redis session、规则改写、预算表、对接 SSE。面试：为何每轮重检索？历史与证据预算如何分？session 如何防越权？
'''

EXPAND3_124 = r'''
## 16. Function Calling 实战周计划与案例库

### 16.1 五天上手路线

周一读 OpenAI tools 文档，写一个 get_weather 假工具。周二写 search_kb 接 Chroma，内嵌 ACL filter。周三跑通 tool_call 循环与 max_rounds。周四与 123 JSON 组合最终答案结构。周五评测工具触发准确率，记录误触发样本。

### 16.2 案例：混合助手分诊

员工问「明天上海天气和公司年假」模型先调 weather 再 search_kb，最后综合回答。若 description 含糊，天气问题也 search_kb 搜到防暑通知。优化描述后误触发下降。团队保留每周工具调用分布报表。

### 16.3 案例：循环 search 烧费

模型对相似 query 连续 search_kb 五次，token 账单异常。加 max_rounds 与 query 去重后恢复正常。告警规则：单会话 tool 次数超阈值自动截断。

### 16.4 硬编码 RAG 与 FC 共存架构

网关层规则先分流：明显闲聊直接短答；明显企业制度走硬编码 retrieve；边界问题走 bind_tools 让模型选。这样兼顾合规与灵活，而不是全站一刀切 FC。

### 16.5 tool message 体积与 107 预算

返回 chunk 列表限制条数与总字符，超长截断并标注 truncated。模型仍可能啰嗦，最终答案阶段还要做引用校验。

### 16.6 与 113 引用契约

即使走工具，最终答案仍应带可点击引用。可在最后一跳 prompt 强制 evidence 来自 tool 返回的 chunk 编号。流式场景工具非流，答案可流。

### 16.7 安全与权限

工具白名单；principal 服务端注入；禁止任意 SQL；工具返回过内容安全；日志记 tool_name 与 args_hash。

### 16.8 评测指标

工具精确率与召回率；该搜未搜；不该搜误搜；平均轮数；额外延迟。用金标意图集回归。

### 16.9 LangChain 衔接预览

bind_tools 与 create_retriever_tool 在 125 至 127 展开。本篇理解协议即可参与 D 轨设计评审。

### 16.10 面试要点

FC 解决路由灵活性；硬编码解决可预测与合规；企业 FAQ 默认硬编码；max_rounds 与 ACL 必答。
'''

EXPAND3_125 = r'''
## 16. LangChain 核心实战周计划与案例库

### 16.1 五天上手路线

周一安装 langchain-core 与 langchain-openai，跑通 ChatOpenAI invoke。周二把 110 篇 system 模板改成 ChatPromptTemplate。周三理解 Runnable invoke stream batch。周四加 StdOutCallbackHandler 看 token。周五写文档说明团队何时用 LC 何时裸 SDK。

### 16.2 案例：换模型只改一行

从 gpt-4o-mini 切到兼容网关另一模型，只改 ChatOpenAI 构造参数，prompt 与链路边界不变，节省一次 sprint。若裸 SDK 散落多处 construct，改动面更大。

### 16.3 案例：trace 泄密整改

开发环境误开云端 trace，手册片段外泄。整改关 trace、本地回调、敏感字段脱敏，纳入 onboarding 检查表。

### 16.4 包依赖治理

requirements 只列 core openai chroma 三个 partner，禁止无差别 community 全家桶。升级前跑金标 invoke 对比输出。

### 16.5 消息与 30 篇角色

System Human Assistant 与 LangChain 消息类一一对应。避免把 system 规则塞 user 里导致模型轻视规矩。

### 16.6 RunnableConfig 实践

用 tags 区分 prod staging；metadata 带 session_id 便于日志关联；callbacks 接结构化 logger 而非 print。

### 16.7 与 FastAPI 边界

LangChain 不管 SSE 事件与 citations 收尾，这些仍在应用层实现 116 契约。chain 只负责产出文本流或完整字符串。

### 16.8 Embeddings 与 76 Chroma

OpenAIEmbeddings 维度与 collection 一致；换模型新建 collection；persist_directory 权限同数据库。

### 16.9 团队共识文档建议

写明引入 LC 的门槛：至少三条链、需要统一 stream、需要换供应商。写明不引入场景：单人脚本 PoC。

### 16.10 D 轨下一步

126 LCEL 管道组合；127 Retriever 接检索；再 LangGraph。C 轨手写功底仍是面试重点。
'''

EXPAND3_126 = r'''
## 16. LCEL 实战周计划与案例库

### 16.1 五天上手路线

周一写 prompt 竖线 llm 竖线 StrOutputParser 最小链。周二加 RunnableParallel 做 RAG 字典输入。周三对链 stream 打印打字机。周四接 Chroma retriever 跑通 9 篇实战。周五写单测 mock retriever 与 RunnableBranch 拒答。

### 16.2 案例：键名不一致导致空 context

prompt 要 context 与 question，Parallel 写成 ctx 与 q，invoke 后 evidence 空，模型胡编。代码审查 checklist 增加变量名对照表。

### 16.3 案例：并行改写与检索竞态

rewrite 与 retrieve 并行，检索吃到未改写 query，二轮 Recall 差。改为串行 rewrite 后 retrieve，延迟略升但正确性恢复。

### 16.4 stream 接 SSE 网关

rag_chain.astream 每个字符串片段包装为 116 message 事件；citations 仍在链外用 hits 组装。不要在链内假设自动出引用。

### 16.5 batch 评测

金标问题列表 chain.batch，批量跑 Recall 与答案质量评测，比 for 循环 invoke 更省连接开销。

### 16.6 RunnableBranch 拒答

检索空走拒答模板链，非空走正常 RAG。比 if else 包函数更清晰，且可单独测试分支。

### 16.7 with_fallbacks 备份模型

主模型超时切备份，注意备份模型引用格式一致与成本告警。

### 16.8 与 127 retriever 关系

context 支路永远是 retriever 竖线 format_docs；换 MMR 或 filter 只改 retriever 构造。

### 16.9 反模式清单

巨型 RunnableLambda 塞业务；全库无 filter；retrieve 结果不 format 直接进 prompt；stream 与 invoke 混用同一 UI 状态不刷新。

### 16.10 面试与作业

面试：LCEL 优势是统一 stream batch 与可组合。作业：Branch fallback batch stream 四件套跑通。
'''

EXPAND3_127 = r'''
## 16. Retriever 实战周计划与案例库

### 16.1 五天上手路线

周一 Chroma add_documents 与 as_retriever k 五。周二加 acl_group filter 演示越权不命中。周三换 search_type mmr 对比多样性。周四写自定义 BaseRetriever 打审计日志。周五完整 LCEL RAG 链接 116 SSE 流式网关。

### 16.2 案例：k 过大挤爆预算

k 五十条塞 prompt，费用暴涨且 lost in the middle。改 k 八加 95 rerank 到五，质量升成本降。

### 16.3 案例：混合检索 filter 不一致

稠密路 filter finance 块，BM25 路未 filter，机密从稀疏路泄漏。Ensemble 两路统一 Principal 到 filter 表达式，121 篇单测 golden。

### 16.4 ParentDocument 减少断章

小块命中住宿标准一句话，父文档Retriever 拉回整节，答案完整提到审批例外条款。

### 16.5 MultiQuery 成本意识

对口语多样 query 提升 Recall，但 QPS 高时仅低置信触发，避免人人付出双倍 embed 成本。

### 16.6 score_threshold 校准

用 99 篇方法在验证集扫阈值曲线，选 F1 平衡点写进配置中心，勿拍脑袋零点三五。

### 16.7 create_retriever_tool 接 124

把 retriever 暴露为 search_kb 工具，模型决定是否检索。硬编码链仍可直接 invoke retriever。

### 16.8 观测 callbacks

记录 retrieve latency、doc_id 列表、filter 表达式哈希，bad case 回放可复现。

### 16.9 与 C5 策略对照背诵

91 稠密 93 混合 101 多查询 105 MMR 99 阈值 65 父文档，Retriever 是这些策略的 LangChain 插头，策略思想不变。

### 16.10 作业与面试

作业：mmr threshold filter 自定义 retriever SSE 五件套。面试：Retriever 与 VectorStore 区别；filter 与 ACL 放哪层。
'''

EXPANSION3_BY_SLUG = {
    "websocket-rag-streaming": [EXPAND3_117],
    "multi-turn-history": [EXPAND3_118],
    "function-calling-tool-use": [EXPAND3_124],
    "langchain-core": [EXPAND3_125],
    "langchain-lcel": [EXPAND3_126],
    "langchain-retriever": [EXPAND3_127],
}
