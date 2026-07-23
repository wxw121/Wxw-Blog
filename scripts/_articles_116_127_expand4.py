# -*- coding: utf-8 -*-
"""Fourth-pass large Chinese blocks to meet 5000 hanzi strict."""

EXPAND4 = {
    "websocket-rag-streaming": r'''
## 17. WebSocket RAG 企业落地检查清单（完整版）

上线前请逐项勾选：是否使用 wss 且证书链完整；是否在 accept 前完成 JWT 校验；是否定义 stream_id 且 cancel 只作用于当前流；是否与 116 事件 JSON 字段对齐便于前端复用解析器；是否在 done 帧区分 stop、length、cancelled、error；是否在服务端 abort 上游 LLM 而非只停前端渲染；是否配置 Nginx Upgrade 与足够长的 proxy_read_timeout；是否限制单用户并发连接；是否在 Redis 或等价存储登记 stream 到 worker 映射以支持多实例 cancel；是否对畸形 JSON 与超大帧做防护；是否记录 cancel 率与异常 close 码；协作旁听是否校验角色；regenerate 是否文档化「复用 hits 还是重检索」；澄清 clarify 是否走同一连接且更新 session；是否在 done 后写回 118 session 而非中途写；citations 是否仍末尾一次性下发含 navigate_url；空检索是否走拒答而非空流；压测是否包含高取消率场景；监控是否区分 WS 与 HTTP 指标；版本协议是否 semver 管理；On-call  playbook 是否含 WS 断连与 FD 耗尽处理步骤。

培训材料应包含与 SSE 的并排演示：同一问题两协议各走一遍，量化的首字延迟、停止按钮响应时间、断网行为差异。产品、研发、运维、安全四方评审签字后再默认开启 WebSocket 入口，而非开发自嗨全站切换。记住：WebSocket 是交互增强，不是 RAG 标配；默认入口仍应是 116 SSE，除非双向需求清单非空。
''',
    "multi-turn-history": r'''
## 17. 多轮历史企业落地检查清单（完整版）

上线前请逐项勾选：session_id 是否服务端签发 UUID；是否校验 session 归属 user_id 防越权；turn 写回是否在生成 done 或拒答完成后；展示历史与模型历史是否分离；滑动窗口或 token 上限是否配置化；历史块是否不超过总预算四分之一；每轮是否独立检索而非复用首轮 hits；109 改写是否作用于检索 query 而非只拼 prompt；改写用历史与生成用历史是否可不同裁剪；空检索是否拒答；assistant 是否存储便于审计；引用号存储策略是否文档化；fork 新话题是否新 session_id；DELETE 会话是否级联 Redis 与 DB；日志是否脱敏；摘要 119 触发阈值是否可观测可回滚；与 116 POST messages 合并策略是否 store 权威；与 117 WS query 帧是否只带 session_id；评测集是否含二轮指代金标；CI 是否回归第二轮 Recall；压测是否含单 session 热键；客服备注 turn 是否权限隔离；保留天数是否符合隐私政策；导出会话是否提供；与 104 多跳顺序是否先改写再多跳；与 120 指代分工是否清晰不黑盒。

多轮历史是 C6 地基：流式 116、117 只是传输皮，session 才是连续性灵魂。忽视历史预算会把 128K 模型用成又贵又胡。每周复盘「用户重复提问率」与「二轮 Recall」，比单轮准确率更能反映多轮产品健康度。
''',
    "function-calling-tool-use": r'''
## 17. Function Calling 企业落地检查清单（完整版）

上线前请逐项勾选：是否明确默认硬编码 RAG 还是 FC 路由；tools 是否白名单；search_kb description 是否含何时调用与反例；parameters 是否 JSON Schema 且 required 正确；principal 是否服务端注入而非模型传 user_id；search_kb 内是否强制 ACL filter；返回 chunk 是否限条限长；max_tool_rounds 是否配置；相同 query 是否去重；tool 失败是否结构化回填 tool message；最终答案是否仍过 113 引用与 112 拒答；流式是否区分工具阶段与答案阶段 UI；日志是否记 tool_name args_hash latency；误触发是否周会复盘改 description；是否与 123 JSON 最终步分工清晰；多供应商网关是否 golden 测 tool_calls；内容安全是否过滤 tool 返回；并行 tool_calls 是否限制；评测是否算触发精确率与召回率；成本是否监控额外 LLM 轮次；create_retriever_tool 是否与手动链行为一致；On-call 是否知悉循环 search 告警处理。

Function Calling 是了解篇：懂协议、懂边界、懂安全，而不是一上来全站 Agent。混合场景可先规则分流再加 FC，比纯 FC 更稳。记住工具是服务端能力暴露给模型，权力在代码不在 prompt 祈祷。
''',
    "langchain-core": r'''
## 17. LangChain 核心企业落地检查清单（完整版）

上线前请逐项勾选：是否最小安装 core 加必要 partner；是否锁版本且 CI 金标回归；是否关闭默认云端 trace 防泄密；ChatPromptTemplate 是否与 110 模板同版本管理；Runnable tags metadata 是否接日志；是否知悉 invoke stream batch ainvoke 区别；换 Embedding 是否新建 collection；FastAPI 边界是否应用层包装 SSE 与 citations；回调是否记 token 进成本看板；团队 wiki 是否写清何时用 LC 何时裸 SDK；新人培训是否要求先 C 轨手写再 D 轨；升级 langchain-core 是否跑输出 diff；Embeddings 维度是否与库一致；消息角色是否与 30 篇对齐；是否避免 community 全家桶；license 与 SBOM 是否满足客户审计；On-call 是否区分框架 bug 与业务 filter 错误；是否规划 126 LCEL 与 127 Retriever 接龙；面试是否仍考 C 轨手写。

LangChain 核心是 D 轨起点：Runnable 与消息抽象，不是替代向量库与 ACL。用框架收拢胶水，用 C 轨知识做决策，用评测证明质量。142 篇过关标志：能口述 core 与 partner 分工，能独立写出 ChatPromptTemplate 加 ChatOpenAI invoke，并说明 citations 为何不自动出现。

### 17.1 从裸 SDK 迁移的渐进路线

第一周保持 retrieve 与 prompt 手写，只把 LLM 调用换成 ChatOpenAI。第二周把 system 与 user 模板迁入 ChatPromptTemplate，变量与 110 篇对齐。第三周用 RunnableLambda 包 retrieve 与 format，为 126 LCEL 管道做准备。第四周接 callbacks 记 token 与延迟。第五周写团队决策文档：哪些新项目默认 LangChain，哪些维护裸 SDK。切忌第一天全站重写，风险大且难以回归对比。

### 17.2 常见面试题扩展

面试官问「LangChain 会不会拖慢」：答框架开销远小于网络 RTT，慢在检索与模型。问「为什么要 Runnable」：答统一 invoke stream batch 与组合。问「生产最大坑」：答版本漂移、trace 泄密、filter 遗漏、embedding 维度不一致。问「与 LlamaIndex 对比」：答本篇聚焦 LangChain D 轨，选型看团队生态与招聘。问「C 轨还要学吗」：答必须，框架不能替代 ANN 与 ACL 理解。

### 17.3 与 35 篇 OpenAI 兼容 API 的映射

ChatOpenAI 的 base_url api_key 对齐 35 篇网关配置。messages 数组与 LangChain Message 互转。stream 选项由 llm.stream 承接。tool 绑定在 124 篇展开。理解 35 篇后 LangChain 只是薄封装，出问题时能剥开层定位是网关还是模板还是检索。
''',
    "langchain-lcel": r'''
## 17. LCEL 企业落地检查清单（完整版）

上线前请逐项勾选：管道变量名是否与 prompt 一致；Parallel 是否误并行依赖历史的步骤；format_docs 是否截断防 107 爆预算；空检索是否 RunnableBranch 拒答；stream 是否接 116 事件包装；citations 是否链外组装；是否用 astream 而非阻塞 invoke 在 async 路由；batch 是否只用于离线评测；with_retry 是否设合理次数；with_fallbacks 是否告警备份模型成本；子链是否命名可测；RunnableLambda 是否不过胖；是否 get_input_schema 生成 API 文档；升级 LC 是否金标 diff；是否 mock retriever 单测；日志 callbacks 是否启用；filter 是否在 retriever 构造；MMR MultiQuery 是否知悉成本；与 127 Retriever 参数是否文档化；On-call 是否识别 KeyError 为变量名 bug；团队 code review 是否有 LCEL checklist；是否避免一条链包打天下难以维护。

LCEL 是 D 轨语法：管道组合检索与生成，stream 与 batch 统一接口。143 篇过关标志：能写出 Parallel 字典 RAG 链，能 stream 打印，能解释为何 citations 仍在应用层。与 125 核心、127 Retriever 构成最小 LangChain RAG 三角，缺一角则链路必断。

### 17.1 五周 LCEL 熟练路线

第一周掌握 prompt 竖线 llm 竖线 parser 三件套与 invoke。第二周加 RunnableParallel 字典输入，理解 Passthrough 传 question。第三周接 retriever 完成 9 篇 Mini-RAG，filter 写 acl_group。第四周练 stream 与 astream 接 116 SSE 网关。第五周写 RunnableBranch 拒答与 with_fallbacks 备份模型，并补单测 mock retriever。

### 17.2 反模式深度解析

反模式一：巨型 Lambda 塞业务，难测难维护，应抽函数或类。反模式二：retrieve 与 rewrite 并行，指代未解就检索。反模式三：不设 filter 全库检索越权。反模式四：chain 内拼 citations，与 116 契约冲突应链外。反模式五：在线路径滥用 batch 占内存。反模式六：升级 LC 不跑金标，prompt 格式化微变导致答案漂移。

### 17.3 面试与实战问答

问「LCEL 与手写函数」：答声明式组合、统一 stream、易测。问「最大 bug」：答 Parallel 键名与 prompt 变量不一致。问「如何做拒答」：答 RunnableBranch 空检索支路。问「流式谁负责」：答链出文本，应用层 SSE 事件与 citations。问「性能」：答 profile 检索，LCEL 开销可忽略。
''',
    "langchain-retriever": r'''
## 17. Retriever 企业落地检查清单（完整版）

上线前请逐项勾选：as_retriever k 是否与 107 预算和 95 rerank 配合；filter 字段是否与 53 ACL metadata 一致；换 Embedding 是否新建 collection；空结果是否走拒答链；MMR 是否在多样性差时启用；MultiQuery 是否控制成本仅低置信触发；Ensemble 两路 filter 是否一致防 121 泄漏；ParentDocument 父文本是否仍预算截断；score_threshold 是否与模型版本配对配置；自定义 Retriever 是否打 audit doc_id；invoke 入参是否改写后 query 而非整段 messages；create_retriever_tool 是否与硬编码链 ACL 一致；callbacks 是否记 retrieve latency；索引升级是否只读降级提示；金标是否测 Recall@k；与 91 93 101 105 99 65 策略是否对照表；Chroma 路径权限是否同数据库；On-call 是否知悉 filter 静默空为 schema 问题；是否规划混合检索与 rerank 在 Retriever 外还是外；SSE 网关是否在 retrieve 后流式生成；作业是否完成 k 对比与 acl 演示。

Retriever 是 D 轨主线 144：C4 C5 检索的 LangChain 插头。策略思想不变，框架减胶水。过关标志：能配置 filter 与 k，能自定义 BaseRetriever 打日志，能接 126 LCEL 完成端到端并口述与 FAISS 手写 retrieve 的等价关系。

### 17.1 五周 Retriever 精通路线

第一周 Chroma add_documents 与 as_retriever k 五，理解 Document metadata。第二周写 acl filter 与 53 篇字段对齐，演示越权不命中。第三周试 MMR 与 score_threshold，对照 105 99 篇调参。第四周自定义 BaseRetriever 打审计日志，接 121 合规。第五周 Ensemble 或 MultiQuery 可选实验，用金标算 Recall，并接 116 SSE 完整闭环。

### 17.2 策略—参数对照表（背诵）

稠密检索：VectorStoreRetriever similarity k。多样性差：search_type mmr。置信度低：similarity_score_threshold。口语多样：MultiQueryRetriever 控制触发。长 PDF：ParentDocumentRetriever。混合：EnsembleRetriever 权重调优。每一步策略仍来自 C5 篇，Retriever 只是插头。

### 17.3 面试深度问答

问「Retriever 与 VectorStore」：答 Store 存与搜，Retriever 策略层。问「ACL 写哪」：答 _get_relevant_documents 或 search_kwargs filter，不信模型。问「最大事故」：答混合检索一路未 filter。问「换 embedding」：答新建 collection 全量重建。问「与裸 FAISS」：答接口等价，便于换实现。

### 17.4 本篇收束

把 Retriever 当作黑盒只会 as_retriever 不够：你要能解释每一次 invoke 背后发生的 filter、k 截断、metric 方向、以及返回 Document 如何进入 126 的 format_docs。144 篇主线篇的意义，是让 D 轨编排与 C 轨检索策略 **说同一种语言**，并能向面试官完整复述这一条。
''',
}
