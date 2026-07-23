# 企业级 RAG 全栈工程师 — 知识点清单与学习路线

> 目标岗位：全栈 AI 工程师（前后端 + RAG 一体化）  
> 使用方式：按模块勾选已掌握项；按阶段推进项目；用面试自检表自测

---

## 一、岗位能力画像

企业级全栈 RAG 工程师需要能独立交付：

**上传文档 → 解析分块 → 向量化索引 → 检索问答 → 来源引用 → 可观测可迭代**

能力覆盖五层：

| 层级 | 职责 |
|------|------|
| 数据层 | 文档解析、分块策略、元数据治理 |
| 索引层 | 向量化、向量库、混合检索、重排序 |
| 服务层 | RAG API、流式输出、权限与多租户 |
| 应用层 | 对话前端、引用溯源、知识库管理后台 |
| 工程化 | 评测观测、部署运维、成本与安全 |

面试区分度：能否讲清 trade-off、定位 bad case、交付可演示的完整产品（而非仅会调框架 demo）。

---

## 二、知识点总清单

以下仅列关键词，不展开细节。建议按 A→H 顺序学习，C 为核心。

### A. 基础前置（面试必问，无 RAG 标签）

1. Python 3.10+ 语法与工程化
2. 虚拟环境（venv / poetry / uv）
3. 类型注解（typing / pydantic）
4. 异步编程（asyncio / async-await）
5. 包管理与依赖锁定
6. HTTP 协议基础（方法、状态码、Header）
7. REST API 设计原则
8. WebSocket 与长连接
9. SSE（Server-Sent Events）流式协议
10. SQL 基础（JOIN、索引、事务）
11. PostgreSQL 常用特性
12. NoSQL 概念（Redis、文档库）
13. Redis 缓存模式（Cache-Aside、TTL）
14. Git 分支策略与 PR 流程
15. Docker 镜像与容器
16. Docker Compose 多服务编排
17. Linux 基础命令与日志排查
18. 环境变量与配置分离（12-Factor）
19. React 或 Vue 选一精通
20. TypeScript 基础
21. 前端状态管理（Zustand / Redux / Pinia）
22. 流式 UI 渲染（逐字显示、中断）
23. Markdown 渲染与安全（XSS）

### B. NLP / IR / LLM 基础

24. 中文分词与英文 tokenization
25. TF-IDF 原理
26. BM25 稀疏检索原理
27. 倒排索引概念
28. Word2Vec / 静态词向量
29. Transformer 架构
30. Self-Attention 机制
31. 预训练与微调概念
32. Embedding 向量表示
33. Cosine Similarity / 内积相似度
34. Token 计数与计费
35. Context Window 限制
36. Temperature / Top-p / Top-k 采样
37. System / User / Assistant Prompt 结构
38. Few-shot Prompting
39. Chain-of-Thought（了解）
40. 幻觉（Hallucination）成因
41. Grounding 与引用归因
42. 闭源 LLM API 调用模式（OpenAI 兼容）

### C. RAG 核心链路

#### C1 数据采集与解析

43. PDF 文本提取
44. PDF 表格与版面（Layout）挑战
45. Markdown 解析
46. HTML 正文抽取
47. DOCX / Office 文档解析
48. 纯文本与编码检测（UTF-8 / GBK）
49. PyMuPDF（fitz）
50. pdfplumber
51. Unstructured.io
52. Apache Tika
53. 文本清洗（空白、乱码、页眉页脚）
54. 文档去重（hash / simhash）
55. 文档版本管理
56. 增量更新与变更检测
57. 元数据字段：`doc_id`
58. 元数据字段：`chunk_id`
59. 元数据字段：`source` / `page` / `section`
60. 元数据字段：`acl`（访问控制）
61. 元数据字段：`timestamp` / `version`
62. OCR 与扫描件（加分）
63. 图片内文字（多模态，了解）

#### C2 分块（Chunking）

64. 固定长度分块（Fixed-size）
65. 递归字符分块（Recursive Character）
66. 句子边界分块
67. Overlap（重叠窗口）策略
68. Chunk size 调参 trade-off
69. 结构感知分块（标题层级）
70. Markdown AST 分块
71. HTML DOM 分块
72. Parent-Document Retriever
73. Small-to-Big 检索
74. 多粒度索引（chunk + document）
75. 表格单独成块
76. 代码块保留完整性
77. 列表与编号段落处理

#### C3 向量化（Embedding）

78. OpenAI `text-embedding-3-small/large`
79. BGE 系列（bge-small / bge-m3）
80. E5 系列（e5-base / multilingual-e5）
81. GTE 系列
82. 向量维度与存储成本
83. L2 归一化
84. 批量 Embedding（batching）
85. Embedding 缓存策略
86. API 重试与限流
87. 中英混合语料选型
88. 领域专用 Embedding 评估
89. 本地 Embedding 推理（sentence-transformers）
90. Embedding 微调概念（进阶）
91. 对比学习（Contrastive Learning，了解）

#### C4 向量存储与检索

92. FAISS（本地 ANN）
93. Chroma（轻量向量库）
94. Milvus
95. Qdrant
96. Weaviate
97. Pinecone（托管）
98. pgvector（PostgreSQL 扩展）
99. Elasticsearch 向量检索
100. OpenSearch 混合检索
101. Flat 暴力检索
102. IVF 倒排文件索引
103. HNSW 图索引
104. ANN 召回率与延迟权衡
105. Metadata Filter 过滤检索
106. 多租户 namespace / collection 隔离
107. 向量库备份与恢复
108. Dense 稠密检索
109. Sparse 稀疏检索（BM25）
110. 混合检索（Hybrid Search）
111. RRF（Reciprocal Rank Fusion）融合
112. Cross-Encoder 重排序
113. BGE-Reranker
114. Cohere Rerank API
115. Top-K 召回数量调参
116. Score Threshold 阈值过滤

#### C5 查询侧优化

117. Query Rewriting（查询改写）
118. Multi-Query Retrieval
119. HyDE（Hypothetical Document Embeddings）
120. 查询分解（Query Decomposition）
121. Multi-hop 检索前置
122. MMR（最大边际相关性）多样性
123. 检索结果去重
124. Context 预算分配（Token 裁剪）
125. LongContextReorder（相关片段排序）
126. 会话历史与查询增强

#### C6 生成与 Grounding

127. RAG Prompt 模板设计
128. 上下文注入格式（XML / Markdown 分隔）
129. 拒答策略（知识库无答案时）
130. 行内引用标注
131. 脚注式引用
132. 跳转源文档 / 页码定位
133. SSE 流式生成（后端）
134. WebSocket 流式生成
135. 多轮对话历史管理
136. 历史压缩（Summary Memory）
137. 指代消解（会话级检索）
138. 越权文档过滤
139. 敏感词与内容安全
140. 结构化输出（JSON Mode）
141. Function Calling / Tool Use（与 Agent 衔接）

### D. 框架与架构

142. LangChain 核心概念
143. LangChain LCEL（Runnable 链）
144. LangChain Retriever 抽象
145. LangChain VectorStore 集成
146. LangChain Document Loader
147. LangChain Text Splitter
148. LlamaIndex Index 类型
149. LlamaIndex Query Engine
150. LlamaIndex Agent
151. Haystack Pipeline 思想
152. 自研 Pipeline vs 框架取舍
153. 可插拔抽象：Parser / Splitter / Embedder
154. 可插拔抽象：Store / Retriever / Generator
155. 配置驱动（YAML / env）管道组装

### E. 评测、观测与迭代

156. RAGAS：Context Precision
157. RAGAS：Context Recall
158. RAGAS：Faithfulness（忠实度）
159. RAGAS：Answer Relevancy
160. Golden Dataset 构建
161. 回归测试集维护
162. DeepEval
163. TruLens
164. LangSmith 链路追踪
165. Langfuse 观测
166. Bad Case 归因：解析错误
167. Bad Case 归因：切块错误
168. Bad Case 归因：检索遗漏
169. Bad Case 归因：生成胡编
170. A/B 实验设计
171. 参数版本管理（chunk / top-k / reranker）
172. 人工评测流程

### F. 全栈产品能力

#### F1 后端

173. FastAPI 项目结构
174. 文件上传（multipart）
175. 后台任务（BackgroundTasks）
176. Celery 异步任务队列
177. Bull / ARQ（Node 备选）
178. 索引任务状态机（pending / running / done / failed）
179. 幂等重建索引
180. 失败重试与死信
181. JWT 认证
182. RBAC 角色权限
183. 多租户数据隔离（tenant_id）
184. OpenAI 兼容 API 封装
185. 多模型路由与降级
186. 速率限制（Rate Limiting）
187. API 文档（OpenAPI / Swagger）

#### F2 前端

188. 聊天消息列表组件
189. Markdown 渲染（react-markdown 等）
190. 代码高亮（highlight.js / shiki）
191. 流式打字机效果
192. 中断生成（AbortController）
193. 引用卡片 UI
194. 侧边栏原文预览
195. PDF 高亮定位（加分）
196. 知识库文档上传界面
197. 解析 / 索引进度展示
198. 重建索引操作
199. 检索调试台（输入 query 看 top-k）
200. 管理后台：用量统计
201. 管理后台：日志与评测看板

### G. 生产与云原生

202. Docker 多阶段构建
203. Docker Compose 全栈本地部署
204. Kubernetes 基本概念（Pod / Service / Ingress）
205. 密钥管理（不硬编码 API Key）
206. 健康检查（/health /ready）
207. 结构化日志（JSON log）
208. Prometheus 指标
209. Embedding 批次成本估算
210. 向量库存储成本
211. LLM Token 成本优化
212. PII 脱敏
213. 审计日志
214. GDPR / 数据驻留（了解）
215. 等保与合规语境（了解）

### H. 进阶方向（Senior / 大厂加分）

216. Graph RAG
217. 知识图谱增强检索
218. Agentic RAG
219. ReAct 推理框架
220. Tool Calling 多步检索
221. Self-RAG
222. CRAG（Corrective RAG）
223. Adaptive RAG
224. Map-Reduce 长文档摘要
225. Refine 迭代精炼
226. RAPTOR 层次检索
227. 多模态 RAG（图文检索）
228. ColPali 类方案（了解）
229. LoRA 微调用于领域问答
230. RLHF / DPO（了解）

**合计：230 条知识点**

---

## 三、分阶段学习计划

按阶段验收推进，不设固定周数。每阶段完成里程碑项目 + 验收标准后进入下一阶段。

### 阶段 0：基础补齐

| 项 | 内容 |
|----|------|
| 目标 | 能写可维护的 Python API + 简单前端；熟悉流式 LLM 调用 |
| 项目 | 复现 SpeakEasy 式流式对话（非 RAG） |
| 目录 | [`projects/00-llm-streaming/`](projects/00-llm-streaming/) |
| 验收 | 流式对话 API 可运行；前端页面可演示逐字输出与中断 |

### 阶段 1：RAG 最小闭环

| 项 | 内容 |
|----|------|
| 目标 | 理解并手写 ingest → retrieve → generate 全链路 |
| 项目 | **Mini-RAG**：本地 PDF → Chroma → 问答 |
| 目录 | [`projects/01-mini-rag/`](projects/01-mini-rag/) |
| 验收 | 不依赖 LangChain 完成端到端；能解释每步数据结构 |

### 阶段 2：检索质量

| 项 | 内容 |
|----|------|
| 目标 | 混合检索、重排序、基础评测 |
| 项目 | 在 Mini-RAG 上加入 BM25 混合、BGE-Reranker、RAGAS |
| 目录 | [`projects/02-hybrid-retrieval/`](projects/02-hybrid-retrieval/) |
| 验收 | 提交对比实验报告：baseline vs 优化版指标 |

### 阶段 3：框架与工程化

| 项 | 内容 |
|----|------|
| 目标 | LangChain/LlamaIndex 重构 + 异步索引 |
| 项目 | **知识库 SaaS 后端**：上传 / 任务 / 多 collection |
| 目录 | [`projects/03-kb-backend/`](projects/03-kb-backend/) |
| 验收 | REST API 文档齐全；索引任务可重试、状态可查询 |

### 阶段 4：全栈产品

| 项 | 内容 |
|----|------|
| 目标 | 交付完整用户产品 |
| 项目 | **企业知识库助手**：聊天 + 引用溯源 + 管理台 |
| 目录 | [`projects/04-fullstack-assistant/`](projects/04-fullstack-assistant/) |
| 验收 | 多用户隔离；可演示完整业务流（上传→问答→看引用） |

### 阶段 5：生产化

| 项 | 内容 |
|----|------|
| 目标 | 观测、成本、部署 |
| 项目 | Docker 部署 + Langfuse 追踪 + 基础监控 |
| 目录 | 在 `04-fullstack-assistant` 上扩展 |
| 验收 | 能根据 trace 定位一次 bad case 的全链路 |

### 阶段 6：进阶与面试

| 项 | 内容 |
|----|------|
| 目标 | 论文视野 + 简历项目包装 |
| 项目 | 选做 Graph RAG 或 Agentic RAG 子模块 |
| 验收 | 完成 30 分钟技术演讲；自答面试自检 50 题 |

### 每周节奏建议（业余学习）

- **输入 40%**：本清单模块 + 官方文档 + 每周 1 篇论文 skim
- **输出 60%**：代码实现 + [`experiments/`](experiments/) 实验记录

### 推荐技术栈

| 类别 | 选型 |
|------|------|
| 后端 | Python FastAPI + PostgreSQL + pgvector 或 Qdrant |
| 任务队列 | Celery + Redis |
| 前端 | **Next.js App Router**（主教程：[nextjs/README.md](../nextjs/README.md)）或 React + Vite（对照：[react/README.md](../react/README.md)） |
| LLM | OpenAI 兼容 API（DeepSeek 等） |
| 框架 | 先手写 → 再 LangChain；LlamaIndex 对比阅读 |

---

## 四、学习资源与面试自检

### 官方文档

- [LangChain Docs](https://python.langchain.com/docs/)
- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [RAGAS](https://docs.ragas.io/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### 推荐阅读

- 论文：*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*（RAG 原始论文）
- 论文：*Self-RAG*、*Corrective RAG*（进阶 skim）
- 书籍：《动手学深度学习》Embedding 章节；《信息检索》BM25 章节

### 开源参考

- [langchain-ai/rag-from-scratch](https://github.com/langchain-ai/rag-from-scratch)
- [microsoft/graphrag](https://github.com/microsoft/graphrag)（Graph RAG）
- [chroma-core/chroma](https://github.com/chroma-core/chroma)

### 面试自检

完整 50 题见 [`docs/interview-checklist.md`](docs/interview-checklist.md)。

核心 10 题速查：

1. 能否在白板画出 RAG 全链路？
2. chunk size 变大/变小的 trade-off？
3. 检索漏了怎么办？生成胡编怎么查？
4. 混合检索为什么比纯向量好？RRF 是什么？
5. 多租户如何做数据隔离？
6. 如何做增量索引而不全量重建？
7. 流式输出前后端如何实现？
8. RAGAS 四个核心指标含义？
9. LangChain Retriever 与 VectorStore 的边界？
10. 什么场景不适合 RAG？

---

## 进度追踪

在 [`README.md`](../README.md) 中勾选阶段完成状态；实验记录写入 [`experiments/`](experiments/)。
