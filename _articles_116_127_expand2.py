# -*- coding: utf-8 -*-
"""Second-pass Chinese-heavy expansions (~1500+ hanzi each)."""

def _faq_block(topic: str, pairs: list[tuple[str, str]]) -> str:
    lines = [f"### 附录长 FAQ：{topic}\n"]
    for i, (q, a) in enumerate(pairs, 1):
        lines.append(f"**F{i}：{q}**\n\n{a}\n")
    return "\n".join(lines)

EXPAND2_116 = _faq_block("SSE RAG 流式", [
    ("生产环境为何推荐 POST 而不是 EventSource？", "因为企业 RAG 的请求体常包含会话标识、权限令牌、以及多轮 messages 数组。若把这些塞进 GET 查询参数，容易触发网关 URL 长度限制，也会在访问日志里留下可读问题文本。POST 加 fetch 读取 ReadableStream 已成为主流做法：握手仍是 HTTP，语义与 7 篇 SSE 基础一致，只是客户端从 EventSource 换成更灵活的流解析器。"),
    ("检索结果要不要在流式开始前就给用户看？", "可以给预览，但必须与正式引用编号解耦。推荐可选的 sources_preview 事件，只展示标题与页码，不绑定方括号编号。正式 citations 事件在生成结束后一次性下发，与答案中出现的引用号对齐，这样避免用户点击了尚未稳定的链接，也避免审计系统记录到错误的证据映射关系。"),
    ("流式会不会更容易产生幻觉？", "流式本身不改变模型条件分布，但用户更早看到部分句子，心理上可能误以为系统更可信。工程上仍要执行拒答策略、空检索拦截、以及生成后校验引用号。采样温度建议偏低，事实问答场景尽量稳定输出格式，并在 done 事件记录 finish_reason 以便排查截断。"),
    ("如何与内容安全过滤配合？", "输入侧在检索前做敏感词与注入检测；输出侧可在流式阶段做增量敏感词扫描，命中后发送 error 事件并中止上游生成。注意流式扫描要兼顾误杀与漏杀，高敏行业可在 done 后做一次整句复核，再决定是否展示给用户。"),
    ("多租户同时开流如何限流？", "按租户与用户双层令牌桶限制并发 SSE 连接数，防止单客户拖垮集群。限流响应可返回普通 JSON 错误而非流，避免客户端误等待。监控里区分连接建立失败、生成中断、与正常 done 三类结局，便于容量规划。"),
    ("前端打字机卡顿怎么优化？", "合并高频 delta 到动画帧批量渲染；长答案避免反复解析 HTML；引用链接在 citations 到达前用灰色占位。对移动端弱网增加超时提示与重试按钮，不要依赖浏览器自动重连 POST 流。"),
    ("日志应记哪些字段？", "建议记录 session_id、query_hash、检索耗时、首 token 时间、总 token、hit_ids、citation 校验结果、prompt_version。不要记录完整用户问题明文若含敏感信息，可记哈希与采样片段。"),
    ("与脚注式引用如何兼容？", "正文仍用 message 流式；脚注详情可放在 citations 的扩展字段，或在 done 后由 REST 二次拉取。关键是脚注不要比正文更早到达导致 UI 空白或顺序错乱。"),
])

EXPAND2_117 = _faq_block("WebSocket RAG", [
    ("什么情况下必须从 SSE 升级到 WebSocket？", "当产品明确需要用户中止生成、同连接追问澄清、协作旁听、或输入状态广播时，WebSocket 更合适。若只是标准问答打字机，116 篇 SSE 更简单，运维成本更低，穿透代理更省心。"),
    ("cancel 为什么要带 stream_id？", "同一会话里用户可能快速连续提问，服务端也可能并行预取。没有流标识，cancel 可能误杀新一轮生成，造成答案串台。每次 query 或 regenerate 都应生成新的 stream_id，cancel 只作用于匹配标识。"),
    ("多实例部署 cancel 怎么路由？", "常见做法是把 stream_id 映射到 worker 标识存 Redis，cancel 消息 publish 到对应 worker 频道；或使用粘性会话保证连接与生成在同一实例。无论哪种，都要设置 TTL 清理僵尸映射。"),
    ("WebSocket 是否一定要心跳？", "移动网络与部分负载均衡会对空闲连接断开。除协议层 ping 外，可增加应用层 ping 帧做保活，并记录最后一次收到 delta 的时间，超时则提示用户网络不稳定。"),
    ("与 116 事件同构有什么好处？", "前端只需一套状态机解析 delta、citations、done。灰度期可 SSE 默认、WebSocket 实验，后端 RagStreamService 统一产出事件，降低双栈维护成本。"),
    ("协作旁听如何控权？", "旁听者 join room 时必须校验角色，只读推送 delta，不允许注入 query。敏感行业对旁听连接单独审计，避免内部越权围观。"),
    ("regenerate 是否复用检索？", "产品策略分两种：仅嫌措辞不好可复用 hits 省延迟；用户实质改问法应重新检索保证证据新鲜。要在接口文档写清默认行为，避免测试与生产不一致。"),
    ("wss 证书问题怎么排查？", "企业内网常因自签证书导致握手失败。客户端需信任企业根证书；服务端禁用弱 cipher；Ingress 必须正确配置 Upgrade 头。"),
])

EXPAND2_118 = _faq_block("多轮历史", [
    ("多轮对话历史存在哪里？", "PoC 可内存字典；生产推荐 Redis 热存储加 Postgres 冷存储。向量库只存企业文档 chunk，不应把聊天记录塞进 embedding 索引，除非你做长期记忆产品且另有合规设计。"),
    ("历史会不会挤掉检索证据？", "会，这是最常见翻车。必须为 system、历史、证据、输出预留预算桶。历史建议不超过总预算四分之一，超出则滑动裁剪或触发 119 摘要，而不是让证据块被静默截断。"),
    ("每轮都要重新检索吗？", "要。用户后续追问常针对新事实或新实体，复用首轮 hits 会导致答非所问。仅澄清子句且在 117 策略允许时，可在已有 hits 子集上二次生成，但仍要记录 hit_ids 变化。"),
    ("展示历史与模型历史能否不同？", "能，且常常应该不同。前端可分页展示全量聊天记录供用户翻页；送入模型的是裁剪后的最近轮次加可选摘要。两者混淆会导致要么浪费 token，要么用户看不到完整对话。"),
    ("如何与 109 会话查询增强配合？", "109 负责把口语追问改写成可独立检索的 search_query；本篇负责 session 结构与预算。顺序上先裁剪出用于改写的历史，再调用增强器，再用改写结果做向量检索，最后用另一套可能更长的历史拼生成 messages。"),
    ("assistant 历史要不要保留引用号？", "存储建议保留，便于审计与质检。生成下一轮时可选择去掉方括号数字减少 token，但保留事实句本身。不要存储模型胡编的引用号而不校验。"),
    ("session 如何防越权？", "session_id 用不可猜测 UUID，服务端用 JWT 的 user_id 校验所有权。禁止客户端仅凭 session_id 读取他人会话。删除接口要级联 Redis 与数据库。"),
    ("fork 新话题怎么做？", "分配新 session_id，旧会话归档而非覆盖，方便客服质检。若在同会话清空历史，要有明确 UI 提示上下文已重置。"),
])

EXPAND2_124 = _faq_block("Function Calling", [
    ("企业 FAQ 为什么还要了解 Function Calling？", "因为真实产品常有闲聊、查库、调业务 API 混合意图。硬编码管线对所有问题一律检索，会浪费延迟与 token，也可能把无关文档塞进 prompt。工具调用让模型先分诊，再决定是否 search_kb。"),
    ("search_kb 工具里必须做什么？", "必须强制执行 ACL 过滤与 top_k 截断，principal 从服务端 JWT 来，不要信任模型传的租户字段。返回 JSON 字符串给 tool message，控制体积，避免一次塞五十个 chunk。"),
    ("最多允许多少轮工具？", "建议上限三轮，并对相同 query 去重。否则模型可能循环检索烧费。日志记录每轮 tool_name 与参数哈希，便于发现异常模式。"),
    ("与 JSON Mode 如何分工？", "JSON Mode 约束最终答案结构；工具调用约束中间步骤结构。可以最后一跳要求 JSON 答案含 citations 字段，但工具阶段仍用 tool message 回填。"),
    ("流式场景怎么做？", "工具循环通常非流式，UI 应显示正在查资料。最终答案步可以接 116 SSE 流式输出。不要试图让模型边流式边输出合法工具 JSON。"),
    ("工具描述怎么写？", "写清何时调用、何时不调用、输入字段含义、反例。坏描述会导致该搜不搜或不该搜乱搜。改名要版本化，避免线上新旧描述混用。"),
    ("与 LangChain 怎么接？", "llm.bind_tools 与 create_retriever_tool 是 D 轨延伸。本篇理解协议后，125 至 127 更易上手。"),
    ("安全红线有哪些？", "不要开放任意代码执行工具；SQL 要参数化；工具白名单；工具返回也要过内容安全。"),
])

EXPAND2_125 = _faq_block("LangChain 核心", [
    ("LangChain 会不会很重？", "拆包安装只引 core 与用到的 partner，避免旧单体包。运行时开销相对 LLM 网络延迟可忽略。重的是错误集成与过度抽象，不是 Runnable 本身。"),
    ("什么时候不必上 LangChain？", "单人脚本、链路单一、团队无共识时，裸 OpenAI SDK 加 76 Chroma 足够。出现多条链重复胶水、频繁换模型换库、需要统一 stream 与 batch 时再引入。"),
    ("ChatModel 与 30 篇角色关系？", "SystemMessage HumanMessage AIMessage 与 system user assistant 一一对应。模板用 ChatPromptTemplate 管理变量，便于与 110 篇 RAG 模板对齐版本。"),
    ("Runnable 为什么重要？", "它是 LCEL 管道的基础类型，统一 invoke stream batch ainvoke。理解 Runnable 后，126 的管道符只是语法糖。"),
    ("Tracing 要不要默认开？", "不要。开发可本地 stdout 回调；生产用结构化日志。避免机密 chunk 进第三方 trace。"),
    ("如何与 FastAPI 集成？", "路由里 chain.ainvoke 或 astream，外层仍由你实现 116 SSE 事件包装与 citations 收尾。LangChain 不负责企业引用契约。"),
    ("Embeddings 与向量库注意什么？", "换 embedding 模型要新建 collection 全量重建，与 76 篇一致。维度不匹配是最常见检索空或分数异常原因。"),
    ("D 轨学完去哪？", "126 LCEL 组合，127 Retriever 接检索，再按需 LangGraph 编排。C 轨手写能力仍是底层功底。"),
])

EXPAND2_126 = _faq_block("LCEL", [
    ("管道符左侧输出不匹配右侧怎么办？", "用 RunnableLambda 做适配，或检查 prompt 变量名与 Parallel 字典键是否一致。get_input_schema 可帮助调试类型。"),
    ("并行支路何时用 RunnableParallel？", "检索格式化与问题透传是经典模式。注意依赖历史的改写不能与检索并行，否则检索吃到未改写 query。"),
    ("stream 与 invoke 选哪个？", "产品要打字机用 stream；批处理评测用 batch。同一链两种模式，减少重复代码。"),
    ("如何做拒答分支？", "用 RunnableBranch 在检索为空时走拒答模板链，非空走正常 RAG。不要静默让 LLM 无证据编造。"),
    ("fallback 怎么用？", "with_fallbacks 可挂备份模型，注意成本与延迟。生产要明确主备模型引用格式一致。"),
    ("与 116 SSE 如何衔接？", "astream 或 astream_events 取 delta，应用层 sse_pack。citations 仍在生成结束后由你的服务组装，LCEL 默认只流文本。"),
    ("怎么单测链？", "mock retriever 为 RunnableLambda 返回固定 Document，断言最终字符串含预期事实。比 mock 全局 openai 更稳。"),
    ("LCEL 与旧 Chain 类？", "新项目优先 LCEL，旧 LLMChain 仅维护遗留。文档与招聘市场也在向 LCEL 收敛。"),
])

EXPAND2_127 = _faq_block("Retriever", [
    ("Retriever 与 VectorStore 区别？", "VectorStore 管存储与相似度搜索；Retriever 管策略如 k、filter、MMR、多查询。RAG 链应依赖 Retriever 接口，便于换库与加策略。"),
    ("as_retriever 参数怎么设？", "k 结合 107 预算与 95 rerank；filter 写 acl_group doc_id 等 metadata，与 53 53 篇一致；MMR 在列表多样性差时启用，见 105 篇。"),
    ("自定义 Retriever 何时需要？", "当你要统一 ACL、写审计日志、或接自研 FAISS 封装时。实现 _get_relevant_documents 即可接入 LCEL。"),
    ("MultiQueryRetriever 值不值？", "Recall 差且口语多样时可试，注意额外 LLM 与 embed 成本。高 QPS 时对低置信才触发更省。"),
    ("ParentDocumentRetriever 解决什么？", "小块检索大块阅读，避免断章取义，与 65 篇思路一致。适合长 PDF 政策。"),
    ("混合检索怎么接？", "EnsembleRetriever 组合稠密与稀疏，权重参考 93 篇。两路 filter 必须一致，否则 121 篇越权漏洞。"),
    ("与 124 tools 关系？", "create_retriever_tool 把检索暴露给模型路由。硬编码 RAG 仍可直接 chain 内 retriever。"),
    ("评测怎么做？", "用 C5 金标算 Recall@k，改 k 或 filter 后回归。日志 callbacks 记录 doc_id 分布。"),
])

EXPANSION2_BY_SLUG = {
    "sse-rag-streaming": [EXPAND2_116],
    "websocket-rag-streaming": [EXPAND2_117],
    "multi-turn-history": [EXPAND2_118],
    "function-calling-tool-use": [EXPAND2_124],
    "langchain-core": [EXPAND2_125],
    "langchain-lcel": [EXPAND2_126],
    "langchain-retriever": [EXPAND2_127],
}
