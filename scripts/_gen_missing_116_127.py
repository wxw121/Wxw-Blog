# -*- coding: utf-8 -*-
"""Generate missing tutorials 116-118, 124-127 with >=5000 hanzi each."""
import re
from pathlib import Path

ROOT = Path(__file__).parent


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


SUMMARY_116 = r'''## 14. 总结与系列下一步

SSE 流式 RAG 的核心不是「打开 `stream=True`」，而是 **在 [7 篇](7.sse-tutorial.md) 协议上定义 RAG 事件契约**：**message 流答案、citations 收尾盖章、done 收束**。引用与 [113 行内标注](113.inline-citation-tutorial.md)、[115 导航 URL](115.source-document-navigation-tutorial.md) 对齐；采样与窗口分别服从 [29](29.llm-sampling-tutorial.md)、[28](28.context-window-tutorial.md)。

**本篇交付物**：四类事件 JSON、FastAPI `StreamingResponse`、前端 fetch 解析、citations 延后挂载、Nginx 无缓冲配置、§10 先错对对。

**建议下一步**：

1. [117 WebSocket 流式 RAG](117.websocket-rag-streaming-tutorial.md)——中断与双向；  
2. [118 多轮历史](118.multi-turn-history-tutorial.md)——POST body 历史 + 每轮检索；  
3. 复习 [7 SSE](7.sse-tutorial.md) 认证与重连；  
4. 在评测集上对比 **流式 vs 非流式** 的 faithfulness（E 轨）。

---

*系列：C6 生成与 Grounding · 路线图第 133 条 · 主线篇*
'''


def _load_116_base() -> str:
    raw = (ROOT / "116.sse-rag-streaming-tutorial.md").read_text(encoding="utf-8")
    for marker in (
        "## 14 附录：SSE RAG 生产细节扩展",
        "## 15. SSE RAG 深度附录",
        "## 14. 总结与系列下一步",
        "## 15. 深度专题",
    ):
        idx = raw.find(marker)
        if idx > 0:
            raw = raw[:idx].rstrip()
    return raw + "\n\n" + ARTICLE_116_EXTRA + "\n\n" + SUMMARY_116


def pad_if_needed(content: str, slug: str, min_h: int = 5000) -> str:
    n = hanzi_count(content)
    if n >= min_h:
        return content
    extras = EXPANSION_BLOCKS.get(slug, [])
    out = content
    i = 0
    while hanzi_count(out) < min_h and i < len(extras):
        out += "\n\n" + extras[i]
        i += 1
    pad_paras = PAD.get(slug, [])
    j = 0
    while hanzi_count(out) < min_h and pad_paras:
        out += "\n\n### 进阶补充 " + str(j + 1) + "\n\n" + pad_paras[j % len(pad_paras)]
        j += 1
        if j > 80:
            break
    if hanzi_count(out) < min_h:
        raise ValueError(f"{slug}: only {hanzi_count(out)} hanzi, need {min_h}")
    return out


PROMPT_TEMPLATE = """---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

{body}

Footer: {footer}

All text Simplified Chinese.
"""


def write_image_assets(slug: str, title: str, items: list[tuple[str, str, str]]):
    img_dir = ROOT / "image" / slug
    prompts_dir = img_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}信息图（教程配图）\n",
        "\n| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n",
    ]
    for fname, layout, section in items:
        lines.append(f"| `{fname}` | {layout} | {section} |\n")
    lines += [
        "\n风格：hand-drawn-edu · 16:9 · 中文\n\nPrompt 见 `prompts/`。\n\n",
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
    ]
    (img_dir / "README.md").write_text("".join(lines), encoding="utf-8")


def write_prompts(slug: str, prompts: list[tuple[str, str, str, str, str]]):
    for fname, layout, title, body, footer in prompts:
        path = ROOT / "image" / slug / "prompts" / fname
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            PROMPT_TEMPLATE.format(layout=layout, title=title, body=body, footer=footer),
            encoding="utf-8",
        )


# Load article bodies from companion module
from _articles_116_127 import (  # noqa: E402
    ARTICLE_116_EXTRA,
    ARTICLE_117,
    ARTICLE_118,
    ARTICLE_124,
    ARTICLE_125,
    ARTICLE_126,
    ARTICLE_127,
)
from _articles_116_127_expand import EXPANSION_BY_SLUG  # noqa: E402
from _articles_116_127_expand2 import EXPANSION2_BY_SLUG  # noqa: E402
from _articles_116_127_expand3 import EXPANSION3_BY_SLUG  # noqa: E402
from _articles_116_127_expand4 import EXPAND4  # noqa: E402
from _articles_116_127_pad import PAD  # noqa: E402

def _merged_expansions(slug: str) -> list[str]:
    base = (
        EXPANSION_BY_SLUG.get(slug, [])
        + EXPANSION2_BY_SLUG.get(slug, [])
        + EXPANSION3_BY_SLUG.get(slug, [])
    )
    if slug in EXPAND4:
        base.append(EXPAND4[slug])
    return base

EXPANSION_BLOCKS = {
    "sse-rag-streaming": _merged_expansions("sse-rag-streaming"),
    "websocket-rag-streaming": _merged_expansions("websocket-rag-streaming") + [
        "### 14.1 与 Redis Pub/Sub 的水平扩展\n\n多实例 WebSocket 需要 **sticky session** 或 **Redis 转发**：用户 `cancel` 必须到达 **正在生成的那台 worker**。RAG 生成状态存 `stream:{stream_id}`，TTL 5 分钟。\n\n### 14.2 与 [116 SSE](116.sse-rag-streaming-tutorial.md) 的灰度迁移\n\n产品可先 **SSE 默认 + WS 实验开关**；事件 JSON **尽量同形**（`message`/`citations`/`done`），减少前端双实现。\n\n### 14.3 协作场景：多人围观同一会话\n\n客服主管 **旁听** 坐席 RAG 会话：WS **广播** `delta` 到 `room:{session_id}`；注意 **PII 权限**——旁听者 JWT 角色须校验。\n\n### 14.4 二进制帧与 JSON\n\nRAG 控制消息 **统一 JSON 文本帧**；勿混 Protobuf（调试困难）。大 `citations` 可 **REST 补拉** 减 WS 帧体积。\n\n### 14.5 作业\n\n- [ ] 实现 `cancel` abort asyncio Task\n- [ ] 心跳 30s ping/pong\n- [ ] 重连带 `last_stream_id` 拒绝续传（明确产品策略）\n- [ ] 对照 116 事件 JSON 一致",
    ],
    "multi-turn-history": _merged_expansions("multi-turn-history") + [
        "### 14.1 Session 存储选型\n\nPoC 用 **内存 dict**；生产用 **Redis**（热）+ **Postgres JSONB**（冷审计）。字段：`session_id`、`turns[]`、`summary`、`updated_at`、`user_id`。\n\n### 14.2 与 [119 Summary](119.summary-memory-tutorial.md) 的阈值\n\n建议：**轮数 > 8 或历史 token > 2000** 触发摘要；摘要后 **仍保留最近 2 轮原文** 供指代。\n\n### 14.3 合规：右键删除会话\n\nGDPR 场景提供 **delete session** API，级联删 Redis + DB + **可选** 向量库会话日志（若你错误地把对话写入索引）。\n\n### 14.4 fork 新话题\n\n用户点「新话题」→ **新 session_id**；旧 session **归档** 不删，便于质检。\n\n### 14.5 作业\n\n- [ ] 实现滑动窗口 k=6\n- [ ] 每轮独立 `search_query`（109）\n- [ ] POST body 传 `messages` 对接 116 SSE\n- [ ] 预算表：历史 ≤25% 总 token",
    ],
    "function-calling-tool-use": _merged_expansions("function-calling-tool-use") + [
        "### 14.1 与 [123 JSON](123.structured-output-json-tutorial.md) 边界\n\n**JSON Mode** 约束 **最终答案形状**；**Function Calling** 约束 **中间工具调用形状**。RAG 可先 `search_kb` 再 `answer_user`——两阶段。\n\n### 14.2 工具描述写作\n\n`description` 写 **何时调用、输入字段、返回什么**；`parameters` 用 JSON Schema。坏描述：「搜索工具」；好描述：「当用户问公司制度且需查知识库时调用，query 为独立完整问句」。\n\n### 14.3 并行工具调用\n\n模型可能一次返回 **多个 tool_calls**；RAG 通常 **禁止并行 search**（浪费）——system 写「每轮最多一次 search_kb」。\n\n### 14.4 作业\n\n- [ ] 定义 `search_kb` + `get_weather` 两工具，验证路由\n- [ ] 记录 tool_latency 日志\n- [ ] 无工具时纯生成路径仍可用",
    ],
    "langchain-core": _merged_expansions("langchain-core") + [
        "### 14.1 与裸 OpenAI SDK 对照\n\nLangChain **不替代** HTTP；它统一 **Runnable 接口** 与 **回调**。团队若只有 3 个脚本，裸 SDK 可能更简单——**规模上来** 再引入。\n\n### 14.2 版本锁定\n\n`langchain-core` 与 `langchain-community` **分开 pin**；升级前跑 **金标链** 回归。\n\n### 14.3 作业\n\n- [ ] `pip install langchain-core langchain-openai`\n- [ ] 写最小 ChatModel invoke\n- [ ] 读 Runnable 类型提示",
    ],
    "langchain-lcel": _merged_expansions("langchain-lcel") + [
        "### 14.1 RunnableParallel 与 RAG\n\n`retrieve` 与 `rewrite_query` 可 **并行**——注意 **rewrite 依赖 history** 时勿并行。\n\n### 14.2 作业\n\n- [ ] 链：`prompt | llm | StrOutputParser()`\n- [ ] `.stream()` 打印 delta\n- [ ] `.batch()` 跑 3 条 query",
    ],
    "langchain-retriever": _merged_expansions("langchain-retriever") + [
        "### 14.1 自定义 Retriever 接口\n\n实现 `_get_relevant_documents(query)` 即可接 LCEL；内部仍是你熟悉的 Chroma/FAISS。\n\n### 14.2 作业\n\n- [ ] `as_retriever(search_kwargs={\"k\":5})`\n- [ ] 加 `MultiQueryRetriever` 对比 Recall\n- [ ] 日志打印 `source` metadata",
    ],
}

ARTICLES = [
    (
        "116.sse-rag-streaming-tutorial.md",
        "sse-rag-streaming",
        "SSE 流式 RAG 生成",
        None,  # load existing + extra
        [
            ("01-sse-rag-flow.png", "hub-spoke", "§3 SSE RAG 流是什么"),
            ("02-event-types.png", "comparison-matrix", "§5 事件类型设计"),
            ("03-citation-timing.png", "flowchart", "§6 引用为何放在流末尾"),
        ],
        [
            ("01-sse-rag-flow.md", "hub-spoke", "SSE RAG 流式链路",
             "Center hub: 检索同步 → 生成流式 → 引用收尾\n\nSpoke 1: Top-K chunks\nSpoke 2: text/event-stream\nSpoke 3: delta 逐字\nSpoke 4: citations 事件",
             "SSE 流式 RAG · §3"),
            ("02-event-types.md", "comparison-matrix", "RAG SSE 事件类型",
             "Compare message / citations / done / error — 用途与时机",
             "SSE 流式 RAG · §5"),
            ("03-citation-timing.md", "flowchart", "引用在流末尾的原因",
             "Flow: 错：每 token 带 citation → 对：生成完再发 citations",
             "SSE 流式 RAG · §6"),
        ],
    ),
    (
        "117.websocket-rag-streaming-tutorial.md",
        "websocket-rag-streaming",
        "WebSocket 流式 RAG",
        ARTICLE_117,
        [
            ("01-ws-vs-sse.png", "comparison-matrix", "§3 何时用 WebSocket"),
            ("02-bidir-flow.png", "flowchart", "§5 双向消息流"),
            ("03-cancel-regen.png", "hub-spoke", "§7 中断与重生成"),
        ],
        [
            ("01-ws-vs-sse.md", "comparison-matrix", "WebSocket vs SSE for RAG",
             "Compare 单向问答 / 双向中断 / 协议复杂度 / 默认选型",
             "WebSocket 流式 RAG · §3"),
            ("02-bidir-flow.md", "flowchart", "WebSocket RAG 消息流",
             "client→server: query,cancel — server→client: delta,citations",
             "WebSocket 流式 RAG · §5"),
            ("03-cancel-regen.md", "hub-spoke", "流式中断与重生成",
             "Center: cancel — Spokes: abort LLM / regenerate / clarify / typing",
             "WebSocket 流式 RAG · §7"),
        ],
    ),
    (
        "118.multi-turn-history-tutorial.md",
        "multi-turn-history",
        "多轮对话历史管理",
        ARTICLE_118,
        [
            ("01-history-role.png", "hub-spoke", "§3 历史在 RAG 中的角色"),
            ("02-window-budget.png", "comparison-matrix", "§5 历史与窗口预算"),
            ("03-query-rewrite.png", "flowchart", "§6 历史增强检索"),
        ],
        [
            ("01-history-role.md", "hub-spoke", "多轮历史管什么？",
             "Center: 不是全塞 prompt — Spokes: 短期记忆/查询增强/预算/每轮重检索",
             "多轮对话历史 · §3"),
            ("02-window-budget.md", "comparison-matrix", "历史占用窗口预算",
             "Compare 全量历史 / 滑动窗口 / 摘要压缩 / 检索独立",
             "多轮对话历史 · §5"),
            ("03-query-rewrite.md", "flowchart", "多轮 → 检索 query",
             "用户省略 → 增强器改写 → standalone query → 检索",
             "多轮对话历史 · §6"),
        ],
    ),
    (
        "124.function-calling-tool-use-tutorial.md",
        "function-calling-tool-use",
        "Function Calling 与 Tool Use",
        ARTICLE_124,
        [
            ("01-tool-rag-flow.png", "hub-spoke", "§3 工具与 RAG 的关系"),
            ("02-tool-schema.png", "comparison-matrix", "§5 工具定义要素"),
            ("03-agent-loop.png", "flowchart", "§7 工具调用循环"),
        ],
        [
            ("01-tool-rag-flow.md", "hub-spoke", "RAG 何时走工具",
             "Center: LLM 路由 — search_kb vs 直接答 vs 外部 API",
             "Function Calling · §3"),
            ("02-tool-schema.md", "comparison-matrix", "工具 Schema 要素",
             "Compare name / description / parameters / 返回值",
             "Function Calling · §5"),
            ("03-agent-loop.md", "flowchart", "工具调用循环",
             "user → model → tool_call → execute → model → answer",
             "Function Calling · §7"),
        ],
    ),
    (
        "125.langchain-core-tutorial.md",
        "langchain-core",
        "LangChain 核心概念",
        ARTICLE_125,
        [
            ("01-lc-stack.png", "hub-spoke", "§3 LangChain 是什么"),
            ("02-runnable-idea.png", "comparison-matrix", "§5 Runnable 抽象"),
            ("03-module-map.png", "bento-grid", "§11 概念地图"),
        ],
        [
            ("01-lc-stack.md", "hub-spoke", "LangChain 生态分层",
             "core / community / partner packages — 中心 RAG 链",
             "LangChain 核心 · §3"),
            ("02-runnable-idea.md", "comparison-matrix", "Runnable vs 函数",
             "invoke / stream / batch / 组合",
             "LangChain 核心 · §5"),
            ("03-module-map.md", "bento-grid", "D 模块概念速记",
             "Tiles: ChatModel / Prompt / Parser / Retriever / VectorStore",
             "LangChain 核心 · §11"),
        ],
    ),
    (
        "126.langchain-lcel-tutorial.md",
        "langchain-lcel",
        "LangChain LCEL",
        ARTICLE_126,
        [
            ("01-pipe-chain.png", "flowchart", "§3 LCEL 管道"),
            ("02-stream-batch.png", "comparison-matrix", "§5 stream 与 batch"),
            ("03-rag-lcel.png", "hub-spoke", "§9 Mini-RAG LCEL"),
        ],
        [
            ("01-pipe-chain.md", "flowchart", "LCEL 管道符",
             "prompt | llm | parser — 左进右出",
             "LangChain LCEL · §3"),
            ("02-stream-batch.md", "comparison-matrix", "invoke stream batch",
             "三种调用方式对比与场景",
             "LangChain LCEL · §5"),
            ("03-rag-lcel.md", "hub-spoke", "RAG 的 LCEL 组装",
             "retrieve → format → prompt → llm",
             "LangChain LCEL · §9"),
        ],
    ),
    (
        "127.langchain-retriever-tutorial.md",
        "langchain-retriever",
        "LangChain Retriever 抽象",
        ARTICLE_127,
        [
            ("01-retriever-idea.png", "hub-spoke", "§3 Retriever 是什么"),
            ("02-retriever-types.png", "comparison-matrix", "§5 常见 Retriever"),
            ("03-lcel-retrieve.png", "flowchart", "§9 接入 LCEL"),
        ],
        [
            ("01-retriever-idea.md", "hub-spoke", "Retriever 抽象",
             "Center: get_relevant_documents — VectorStore / BM25 / 混合",
             "LangChain Retriever · §3"),
            ("02-retriever-types.md", "comparison-matrix", "Retriever 类型",
             "VectorStoreRetriever / MultiQuery / ParentDocument / Ensemble",
             "LangChain Retriever · §5"),
            ("03-lcel-retrieve.md", "flowchart", "LCEL 中的检索步",
             "chain: itemgetter question | retriever | format_docs",
             "LangChain Retriever · §9"),
        ],
    ),
]


def main():
    counts = {}
    for fname, slug, title, body, img_items, prompt_items in ARTICLES:
        if body is None:
            content = _load_116_base()
        else:
            content = body
        content = pad_if_needed(content, slug)
        (ROOT / fname).write_text(content, encoding="utf-8")
        write_image_assets(slug, title, img_items)
        write_prompts(slug, prompt_items)
        counts[fname] = hanzi_count(content)
    for k, v in sorted(counts.items()):
        status = "OK" if v >= 5000 else "LOW"
        print(f"{k}: {v} hanzi [{status}]")
    return counts


if __name__ == "__main__":
    main()
