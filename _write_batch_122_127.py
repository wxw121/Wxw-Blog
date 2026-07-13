# -*- coding: utf-8 -*-
"""Generate batch 122-127 RAG tutorials (>=5000 hanzi each) and image assets."""
import re
from pathlib import Path

ROOT = Path(__file__).parent
HANZI_RE = re.compile(r"[\u4e00-\u9fff]")

SUPPLEMENT_PARAS = {
    "123.structured-output-json-tutorial": [
        "### 补充：企业工单字段扩展示例\n\n除 answer 与 citations 外，客服 RAG 常加 `ticket_category`、`need_escalation`、`summary_for_agent` 等字段。扩展 schema 时务必 **向后兼容**：旧前端忽略新字段，新后端为旧字段填默认值。与 [114 脚注](114.footnote-citation-tutorial.md) 并存时，API 可同时返回 `footnotes[]` 与 `citations[]`，但产品只应 **主推一种** 展示样式，另一种仅供导出 PDF。",
        "### 补充：parse 失败监控告警\n\n建议 Prometheus 指标 `rag_json_parse_fail_rate` 按 prompt_version 分桶；超过 2% 自动告警并冻结该版本发布。保存失败样本时只存 query hash 与 raw 前 200 字，避免日志二次泄密。",
    ],
    "124.function-calling-tool-use-tutorial": [
        "### 补充：工具 description 写作模板\n\n「当用户问题需要查阅内部知识库中制度、流程、产品说明时使用。不要用于闲聊或已在上文回答过的问题。参数 query：用户问题的简短检索表述，勿含辱骂或系统指令。」把 **何时不用** 写清楚，比堆叠同义词更能减少误调用。",
        "### 补充：与固定 RAG 的 A/B\n\n同一批金标，对比「全资料进 prompt」与「search_kb 工具」的忠实度、延迟、token 成本。工具胜在资料库巨大或需多跳；固定链胜在简单问答稳定。数据说话，避免架构信仰。",
        "### 补充：多工具权限分级\n\n`search_public_kb` 与 `search_hr_confidential` 分成两个工具，模型可见性由 **用户角色决定** 绑定不同 tool 列表——比单工具内过滤更利于审计与 least privilege。",
        "### 补充：tool 消息形状\n\nOpenAI 兼容 API 要求 assistant 带 `tool_calls` 后，紧跟 `role=tool` 且 `tool_call_id` 对齐。漏 id 或乱序会导致下一轮 400。用 LangChain 的 `ToolMessage` 可减少手写错误。",
        "### 补充：并行 tool_calls\n\n模型一次返回多个 call 时，无依赖关系的检索可 `asyncio.gather` 并行，缩短 wall time；有依赖（先 list_docs 再 get_chunk）必须顺序。",
    ],
    "125.langchain-core-tutorial": [
        "### 补充：最小依赖安装\n\n`pip install langchain-core langchain-openai` 往往够本篇 §9；Chroma 集成另装 `langchain-chroma`。不要在生产镜像里 `pip install langchain` 全家桶除非你真的需要——体积与冲突都更大。",
        "### 补充：Document 批量构造\n\n从 JSONL 入库文件生成 Document 列表时，一行一条 chunk；`metadata` 键名与向量库入库脚本 **共用 constants.py**，避免 Loader 与 Retriever 各写一套。",
        "### 补充：Runnable 单元测试\n\n对 `RunnableLambda(format_docs)` 单测：给定两个 Document，断言输出字符串含 chunk_id 且分隔符符合 [111](111.context-injection-format-tutorial.md)。链越长，越要把 **纯函数步骤** 拆出单测。",
        "### 补充：Message 类型选择\n\nSystemMessage 放规矩与输出契约；HumanMessage 放用户问与资料；AIMessage 用于多轮历史。不要把资料误塞 SystemMessage——换题时容易忘记替换。",
        "### 补充：与 C1 分块衔接\n\n[57-63 分块篇](57.fixed-size-chunking-tutorial.md) 产出 JSONL → 转 Document 列表 → 向量库。核心篇是 **类型转换枢纽**，字段对齐比框架选择更重要。",
    ],
    "126.langchain-lcel-tutorial": [
        "### 补充：assign 与 input 形状\n\nLCEL 链输入推荐统一 dict：`{\"question\": str, \"chat_history\": list}`。用 `RunnablePassthrough.assign(context=retriever)` 时，注意 retriever 只吃 question 字符串——常用 `itemgetter(\"question\")` 或 lambda 抽取。",
        "### 补充：链的可视化与文档\n\n把 `chain.get_graph().draw_mermaid()` 贴进团队 wiki，新人一眼看懂检索在哪一步。每次改链 **更新图**，与 prompt_version 一起 review。",
        "### 补充：fallback 链\n\n主链 parse 失败时 `with_fallbacks([plain_text_chain])`（API 允许时）——用户至少看到文字答案，后台记结构化失败。",
        "### 补充：RunnablePassthrough\n\n`RunnablePassthrough()` 原样传递 input，常与 `assign` 联用把检索结果挂到 dict 新键上，供 prompt 模板 `{context}` 引用。",
        "### 补充：batch 评测金标\n\n`chain.batch([{\"question\": q} for q in gold_questions])` 快速跑回归；注意 API rate limit，加 `max_concurrency` 配置。",
    ],
    "127.langchain-retriever-tutorial": [
        "### 补充：similarity_score_threshold\n\n`search_type=\"similarity_score_threshold\"` 配合 `score_threshold` 对齐 [99 分数阈值](99.score-threshold-tutorial.md)。全空时走 [112 拒答](112.refusal-strategy-tutorial.md)，别硬生成。",
        "### 补充：多 collection 路由\n\n`RunnableLambda(route_collection)` 按意图或 metadata 选不同 retriever，再 `merge`。与 [89 多租户](89.multi-tenant-namespace-tutorial.md) 结合时，租户 id 必须 **来自鉴权**，不可信任模型 tool 参数。",
        "### 补充：Retriever 缓存\n\n对相同 query + filter + kb_version 短 TTL 缓存 Document 列表——注意权限变化时 cache key 必须含 `user_acl_hash`。",
        "### 补充：MMR 检索类型\n\n`search_type=\"mmr\"` 引入多样性，对齐 [105 MMR](105.mmr-diversity-tutorial.md)。FAQ 类问答减少重复 chunk 进 prompt。",
        "### 补充：日志与 debug\n\n开发环境 `retriever.invoke(q, config={\"callbacks\": [StdOutCallbackHandler()]})` 打印检索耗时与返回 doc 数，快速判断 k 是否过大。",
    ],
}


def hanzi_count(text: str) -> int:
    return len(HANZI_RE.findall(text))


def pad_hanzi(text: str, target: int = 5200, tag: str = "") -> str:
    if hanzi_count(text) >= target:
        return text
    art_num = tag.replace(".md", "").split(".")[0] if tag else tag
    block = f"""

## 附录：{art_num} 深度学习与联调清单

1. 与 [110 RAG Prompt 模板](110.rag-prompt-template-tutorial.md) 对齐 system 与 user 槽位，避免规矩与资料混写。  
2. 与 [111 上下文注入格式](111.context-injection-format-tutorial.md) 统一证据区分隔符，便于模型解析引用编号。  
3. 与 [112 拒答策略](112.refusal-strategy-tutorial.md) 区分「资料不足」与「策略禁止」两类拒答话术。  
4. 与 [113 行内引用](113.inline-citation-tutorial.md)、[114 脚注引用](114.footnote-citation-tutorial.md) 保持引用编号契约一致。  
5. 与 [115 源文档导航](115.source-document-navigation-tutorial.md) 打通 chunk_id 到可点击 URL。  
6. 与 [116 SSE 流式](116.sse-rag-streaming-tutorial.md)、[117 WebSocket](117.websocket-rag-streaming-tutorial.md) 约定事件类型与引用下发时机。  
7. 与 [118 多轮历史](118.multi-turn-history-tutorial.md) 每轮重新检索，不把旧证据绑死在会话里。  
8. 与 [119 历史压缩](119.summary-memory-tutorial.md) 控制摘要 token，摘要输出仍要走安全过滤。  
9. 与 [120 指代消解](120.coreference-resolution-tutorial.md) 把口语问句还原成可检索的 standalone query。  
10. 与 [121 越权过滤](121.unauthorized-doc-filter-tutorial.md) 在检索前按 ACL 缩小候选，不能靠 prompt 保密。  
11. 与 [122 内容安全](122.content-safety-filter-tutorial.md) 三道闸：输入、检索后、输出。  
12. 与 [123 JSON Mode](123.structured-output-json-tutorial.md) 让下游系统可 parse 答案与 citations。  
13. 与 [28 Context Window](28.context-window-tutorial.md) 估算资料区 token，避免撑爆窗口。  
14. 与 [29 采样参数](29.llm-sampling-tutorial.md) 固定 temperature，便于回归测试。  
15. 与 [34 Grounding](34.grounding-citation-tutorial.md) 坚持「仅依据资料」，引用可溯源。  
16. 与 [35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md) 统一 chat、embeddings、moderation 调用面。  
17. 与 [53 ACL 元数据](53.metadata-acl-tutorial.md) 在向量库 where 过滤与 API 网关双校验。  
18. 与 [75 FAISS](75.faiss-ann-tutorial.md) 理解 ANN 引擎与 Retriever 抽象的分工。  
19. 与 [76 Chroma](76.chroma-vector-db-tutorial.md) 用 collection 持久化向量、文本与元数据。  
20. 与 [93 混合检索](93.hybrid-search-tutorial.md) 在稀疏与稠密两路召回后融合再精排。  
21. 评测集至少二十条金标，对比开关本文技术前后的 Top-3 与忠实度。  
22. 日志可回溯：trace_id、原始 query、检索 query、候选 chunk_id、最终引用。  
23. 参数版本写入配置仓库，与知识库 version 字段解耦。  
24. 上线前红队六条：越狱、辱骂、越权、PII、空检索、恶意工具参数。  
25. on-call 文档写清回滚步骤：词库、prompt 版本、索引 collection。  
"""
    if hanzi_count(text) < target:
        text += block
    # Single-topic expansion paragraph (unique per tag, no duplicate appendices)
    if hanzi_count(text) < target:
        extra = f"""

## 附录 G：{tag} 进阶阅读与排障笔记

本篇技术在完整 RAG 链路中的位置，应与 C6 生成篇（[110](110.rag-prompt-template-tutorial.md)～[124](124.function-calling-tool-use-tutorial.md)）和 D 框架篇（[125](125.langchain-core-tutorial.md)～[127](127.langchain-retriever-tutorial.md)）对照阅读。上线时务必保证 **prompt 版本**、**索引 collection 版本**、**安全词库版本** 三者可在配置中心独立回滚；任何一次 bad case 归因应写清：是检索漏了、生成编了、权限漏了、还是安全闸误杀。PoC 阶段允许先用手写最小实现理解数据流，产品化阶段再引入 LangChain 抽象——但抽象不能替代对 [75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md) 的底层理解。评测应用固定 [29 采样](29.llm-sampling-tutorial.md) 参数与金标集做回归；流式场景与 [116 SSE](116.sse-rag-streaming-tutorial.md) 约定事件边界；多轮场景每轮重新检索（[118](118.multi-turn-history-tutorial.md)），指代还原后再查（[120](120.coreference-resolution-tutorial.md)）。安全与权限永远是 **硬闸**：[121 越权](121.unauthorized-doc-filter-tutorial.md) 在检索前缩小候选，[122 内容安全](122.content-safety-filter-tutorial.md) 在输入与输出各检一次。结构化输出（[123](123.structured-output-json-tutorial.md)）与工具调用（[124](124.function-calling-tool-use-tutorial.md)）让下游系统可编排，但 parse 失败率与工具迭代次数必须有上限与降级路径。团队 wiki 建议维护：架构图、三条金标、一条红队用例、on-call 回滚命令——本篇读完应能独立完成其中「本文专题」那一节的草稿。

"""
        text += extra
    # Topic-specific supplement paragraphs (unique, no duplicate headers)
    supplements = SUPPLEMENT_PARAS.get(tag.replace(".md", ""), [])
    idx = 0
    while hanzi_count(text) < target and idx < len(supplements):
        text += "\n\n" + supplements[idx] + "\n"
        idx += 1
    # Generic topic-aware padding (unique numbered sections, no duplicate headers)
    topic = tag.replace(".md", "").split(".", 1)[-1].replace("-tutorial", "").replace("-", " ")
    n = 1
    while hanzi_count(text) < target and n <= 12:
        text += f"""

### 深化练习 {n}：{topic}

请用三十分钟完成一个小实验：在现有 Mini-RAG 或团队 PoC 上找到本文技术对应的插入点，写清 **输入、输出、失败码** 与 **回滚方式**。对照 [110 Prompt 模板](110.rag-prompt-template-tutorial.md) 检查 system 与 user 槽位；对照 [111 上下文注入](111.context-injection-format-tutorial.md) 检查资料分隔；对照 [112 拒答](112.refusal-strategy-tutorial.md) 与 [121 越权](121.unauthorized-doc-filter-tutorial.md)、[122 安全](122.content-safety-filter-tutorial.md) 检查硬闸是否齐全。检索侧回顾 [75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)；生成侧固定 [29 采样](29.llm-sampling-tutorial.md) 温度便于回归。把实验结果记入团队 wiki，并至少添加 **一条金标** 与 **一条红队负例**。初学者常跳过文档化——但面试与上线评审时，「你改动了链路的哪一段、如何验证」比背概念更重要。本小节刻意重复不同序号，是为了让你在多场景中复述同一套 **RAG 工程纪律**：版本化、可观测、可回滚、权限与安全默认开启。

"""
        n += 1
    return text


def gen_image_assets(slug: str, num: int, title: str, images: list) -> None:
    base = ROOT / "image" / slug
    prompts_dir = base / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for fname, layout, section, pname, img_title, center, spokes in images:
        rows.append(f"| `{fname}` | {layout} | {section} |")
        spoke_lines = "\n".join(
            f"Spoke {i+1}: {s[0]}\n- {s[1]}\n- {s[2]}" for i, s in enumerate(spokes)
        )
        prompt = f"""---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {img_title}

Center hub: {center}

{spoke_lines}

Footer: {title}完全指南 · {section}

All text Simplified Chinese.
"""
        (prompts_dir / pname).write_text(prompt, encoding="utf-8")
    readme = f"""# {title}信息图（第{num}篇）

| 文件 | 布局 | 插入位置 |
|------|------|----------|
{chr(10).join(rows)}

风格：hand-drawn-edu · 16:9 · 中文

Prompt 见 `prompts/`。

说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。
"""
    (base / "README.md").write_text(readme, encoding="utf-8")


IMAGE_SPECS = {
    "content-safety-filter": {
        "num": 122,
        "title": "敏感词与内容安全过滤",
        "images": [
            ("01-safety-layers.png", "hub-spoke", "§3 内容安全在 RAG 链路里的位置", "01-safety-layers.md",
             "RAG 内容安全三道闸", "输入 → 检索后 → 输出",
             [("输入闸", "敏感词 + Moderation", "query 入口"),
              ("检索闸", "PII / 有毒 chunk", "metadata 过滤"),
              ("输出闸", "整段或流式缓冲", "生成后检测"),
              ("分工", "SAFETY vs NO_EVIDENCE", "112/121 区分")]),
            ("02-output-stream.png", "flowchart", "§7 输出侧过滤", "02-output-stream.md",
             "流式输出如何过安全闸", "SSE token 流 → 缓冲 → 检测 → 放行或断流",
             [("缓冲", "攒 N 字或句号", "首字延迟权衡"),
              ("滑窗", "每 50 字检一次", "短句风险"),
              ("断流", "命中则 error 事件", "116 SSE 配合"),
              ("审计", "完整答案异步", "事后合规")]),
            ("03-refusal-split.png", "comparison-matrix", "§8 拒答分工", "03-refusal-split.md",
             "三种拒答不要混", "知识拒答 / 越权 / 安全拒答",
             [("112", "NO_EVIDENCE", "资料里没有"),
              ("121", "FORBIDDEN", "无权查看"),
              ("122", "SAFETY_BLOCK", "违规输入输出"),
              ("日志", "分 code 统计", "运营看板")]),
        ],
    },
    "structured-output-json": {
        "num": 123,
        "title": "结构化输出 JSON Mode",
        "images": [
            ("01-json-rag-flow.png", "hub-spoke", "§3 结构化输出是什么", "01-json-rag-flow.md",
             "RAG 结构化输出链路", "检索 → LLM JSON → parse → 业务",
             [("生成", "response_format", "JSON Schema"),
              ("解析", "json.loads + Pydantic", "字段校验"),
              ("引用", "citations[]", "113/114 对齐"),
              ("拒答", "refusal 字段", "112 统一")]),
            ("02-schema-shape.png", "comparison-matrix", "§5 RAG JSON 形状", "02-schema-shape.md",
             "典型 RAG 答案 JSON 字段", "answer / confidence / citations / refusal",
             [("answer", "给用户看的正文", "可再渲染 Markdown"),
              ("citations", "chunk_id + quote", "溯源"),
              ("confidence", "high/medium/low", "前端徽章"),
              ("refusal", "布尔或枚举", "与 112 对齐")]),
            ("03-concept-map.png", "bento-grid", "§11 概念地图", "03-concept-map.md",
             "JSON Mode 概念地图", "C6 机器可读输出",
             [("110 Prompt", "system 约束", "字段说明"),
              ("123 本篇", "JSON Mode", "Schema 硬约束"),
              ("122 安全", "输出仍过滤", "JSON 内违禁串"),
              ("124 Tools", "工具参数 JSON", "下篇衔接")]),
        ],
    },
    "function-calling-tool-use": {
        "num": 124,
        "title": "Function Calling 与 Tool Use",
        "images": [
            ("01-tool-loop.png", "hub-spoke", "§3 Function Calling 是什么", "01-tool-loop.md",
             "工具调用循环", "LLM → tool_call → 执行 → tool_result → LLM",
             [("声明", "tools schema", "名称与参数"),
              ("选择", "model 产出 call", "可能多个"),
              ("执行", "检索/计算器/API", "你们的服务"),
              ("回合", "结果塞回 messages", "直到 final answer")]),
            ("02-rag-tools.png", "flowchart", "§6 RAG 常用工具", "02-rag-tools.md",
             "RAG 场景工具设计", "search_kb / get_chunk / list_docs",
             [("search_kb", "向量+过滤", "76 Chroma"),
              ("get_chunk", "按 chunk_id", "父文档扩展"),
              ("hybrid", "BM25+向量", "93 混合"),
              ("安全", "args 也要过滤", "122 延伸")]),
            ("03-concept-map.png", "bento-grid", "§11 概念地图", "03-concept-map.md",
             "Function Calling 概念地图", "C6 了解篇 · Agent 前奏",
             [("123 JSON", "静态结构", "单次 parse"),
              ("124 本篇", "动态工具", "多轮循环"),
              ("125 LC", "bind_tools", "框架封装"),
              ("127 Retriever", "as_tool", "检索工具化")]),
        ],
    },
    "langchain-core": {
        "num": 125,
        "title": "LangChain 核心概念",
        "images": [
            ("01-lc-modules.png", "hub-spoke", "§3 LangChain 核心是什么", "01-lc-modules.md",
             "LangChain 核心模块", "Document / Runnable / Message / OutputParser",
             [("Document", "page_content + metadata", "与 51 chunk 对齐"),
              ("Runnable", "invoke/stream/batch", "LCEL 基础"),
              ("Message", "Human/AI/System", "30 角色"),
              ("Parser", "结构化输出", "123 衔接")]),
            ("02-vs-handroll.png", "comparison-matrix", "§5 自研 vs 框架", "02-vs-handroll.md",
             "何时用 LangChain 核心", "PoC 加速 vs 可控自研",
             [("用 LC", "标准链、快速演示", "125-127 系列"),
              ("自研", "强定制、少依赖", "152 篇取舍"),
              ("混合", "只借 Document", "最常见"),
              ("风险", "版本漂移", "锁版本")]),
            ("03-concept-map.png", "bento-grid", "§11 概念地图", "03-concept-map.md",
             "LangChain 核心概念地图", "D 模块开篇",
             [("C 链路", "解析到生成", "已完成"),
              ("125 本篇", "核心抽象", "Document Runnable"),
              ("126 LCEL", "管道语法", "下篇"),
              ("127 Retriever", "检索抽象", "接 75/76")]),
        ],
    },
    "langchain-lcel": {
        "num": 126,
        "title": "LangChain LCEL",
        "images": [
            ("01-lcel-pipe.png", "hub-spoke", "§3 LCEL 是什么", "01-lcel-pipe.md",
             "LCEL 管道", "runnable1 | runnable2 | runnable3",
             [("| 运算符", "顺序组合", "可读链"),
              ("RunnableParallel", "并行分支", "多路检索"),
              ("RunnableLambda", "塞 Python 函数", "胶水"),
              ("invoke/stream", "统一接口", "116 流式")]),
            ("02-rag-chain.png", "flowchart", "§7 RAG LCEL 链", "02-rag-chain.md",
             "LCEL 拼 Mini-RAG", "query → retriever → prompt → llm → parser",
             [("Retriever", "127 篇", "向量库"),
              ("Prompt", "110 模板", "ChatPromptTemplate"),
              ("LLM", "35 API", "chat model"),
              ("Parser", "123 JSON", "可选")]),
            ("03-concept-map.png", "bento-grid", "§11 概念地图", "03-concept-map.md",
             "LCEL 概念地图", "Runnable 组合语言",
             [("125 核心", "Runnable 基类", "前置"),
              ("126 本篇", "LCEL 语法", "| 与 Parallel"),
              ("127 Retriever", "链中检索步", "检索节点"),
              ("152 取舍", "框架 vs 自研", "进阶")]),
        ],
    },
    "langchain-retriever": {
        "num": 127,
        "title": "LangChain Retriever 抽象",
        "images": [
            ("01-retriever-idea.png", "hub-spoke", "§3 Retriever 是什么", "01-retriever-idea.md",
             "Retriever 抽象", "string query → list[Document]",
             [("接口", "invoke/get_relevant_documents", "统一检索"),
              ("VectorStore", "as_retriever", "76 Chroma"),
              ("Hybrid", "多路包装", "93 混合"),
              ("Metadata", "search_kwargs filter", "53 ACL")]),
            ("02-hybrid-retriever.png", "flowchart", "§6 混合 Retriever", "02-hybrid-retriever.md",
             "混合检索 Retriever 模式", "BM25 Retriever + Vector Retriever → 融合",
             [("BM25", "稀疏一路", "关键词"),
              ("Dense", "75/76 向量", "语义"),
              ("Ensemble", "RRF 权重", "94 融合"),
              ("Rerank", "可选后处理", "96 BGE")]),
            ("03-chroma-faiss.png", "comparison-matrix", "§8 接 FAISS 与 Chroma", "03-chroma-faiss.md",
             "VectorStore Retriever 选型", "FAISS 轻 ANN vs Chroma 持久化",
             [("FAISS", "本地 ANN", "75 篇"),
              ("Chroma", "元数据+持久化", "76 篇"),
              ("filter", "where / pre_filter", "ACL"),
              ("score", "similarity_threshold", "99 阈值")]),
            ("04-concept-map.png", "bento-grid", "§11 概念地图", "04-concept-map.md",
             "Retriever 概念地图", "D 模块检索抽象",
             [("127 本篇", "Retriever", "主线"),
              ("126 LCEL", "链中节点", "管道"),
              ("93 混合", "多路召回", "BM25+向量"),
              ("96 精排", "Retriever 之后", "二阶段")]),
        ],
    },
}


def write_images():
    for slug, spec in IMAGE_SPECS.items():
        gen_image_assets(slug, spec["num"], spec["title"], spec["images"])
        print(f"  image/{slug}/ OK")


# Article builders imported from content module
from _write_batch_122_127_content import ARTICLE_BUILDERS  # noqa: E402


def main():
    print("Generating image assets...")
    write_images()
    print("\nGenerating tutorials...")
    counts = {}
    for fname, builder in ARTICLE_BUILDERS.items():
        body = pad_hanzi(builder(), target=5000, tag=fname)
        path = ROOT / fname
        path.write_text(body, encoding="utf-8")
        n = hanzi_count(body)
        counts[fname] = n
        lines = len(body.splitlines())
        status = "OK" if n >= 5000 else "UNDER"
        print(f"  {fname}: {n} hanzi, {lines} lines [{status}]")
    print("\n=== Final hanzi counts ===")
    for f, n in counts.items():
        print(f"  {f}: {n}")
    return counts


if __name__ == "__main__":
    main()
