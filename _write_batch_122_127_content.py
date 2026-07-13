# -*- coding: utf-8 -*-
"""Content builders for batch 122-127 tutorials."""
from __future__ import annotations

FOOTER_C6 = """
### 14.4 30 分钟动手作业

1. 用本文 §9 代码在本地跑通最小链路；  
2. 与 [110 Prompt](110.rag-prompt-template-tutorial.md) 对齐 system 槽位；  
3. 写 wiki 一段：本文技术在你们 RAG 链路中的插入点；  
4. 用 [28 Context Window](28.context-window-tutorial.md) 估算相关 token 预算。

### 14.5 给未来自己的排障便签

贴显示器旁：参数版本、索引版本、prompt 版本三者不要混；日志要有 trace_id；拒答与安全分 code；流式注意引用下发时机。

---

> **初学者可能仍困惑的点**  
> - C6 生成篇不是「只会聊天」——还要 **安全、结构化、可调用工具**。  
> - 框架（D 模块）是 **加速器**，不是替代理解 [75 FAISS](75.faiss-ann-tutorial.md) 与 [76 Chroma](76.chroma-vector-db-tutorial.md)。  
> - 每篇地基都要能 **脱离框架手写最小版**，否则换库时不会排障。
"""


def line_expansion(article_key: str) -> str:
    return EXPANSION_BLOCKS.get(article_key, "")


def deep_dive(article_key: str) -> str:
    return DEEP_DIVE_BLOCKS.get(article_key, "")


def _case_bank(title: str, cases: list[tuple[str, str, str]]) -> str:
    lines = [f"\n## 附录 A：{title}场景案例库\n"]
    for i, (name, scene, fix) in enumerate(cases, 1):
        lines.append(f"""### A.{i} {name}

**场景**：{scene}

**处理**：{fix}

**复盘**：记录 trace_id、触发的策略版本，纳入下周词库或 prompt 迭代。

""")
    lines.append(f"""
## 附录 B：{title}联调检查单（24 项）

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 与 [110 Prompt](110.rag-prompt-template-tutorial.md) 槽位一致 | system 不含 chunk 原文 |
| 2 | 与 [111 注入格式](111.context-injection-format-tutorial.md) 一致 | 资料区有明确标题 |
| 3 | 与 [112 拒答](112.refusal-strategy-tutorial.md) 话术可分 | code 与文案对应 |
| 4 | 与 [113 引用](113.inline-citation-tutorial.md) 编号稳定 | 生成后 citations 对齐 |
| 5 | 与 [114 脚注](114.footnote-citation-tutorial.md) 二选一 | 产品只保留一种主样式 |
| 6 | 与 [115 导航](115.source-document-navigation-tutorial.md) 可跳转 | chunk_id 能映射 URL |
| 7 | 与 [116 SSE](116.sse-rag-streaming-tutorial.md) 事件清晰 | delta / citations / done 分离 |
| 8 | 与 [117 WebSocket](117.websocket-rag-streaming-tutorial.md) 双向需求评估 | 非必要不上 WS |
| 9 | 与 [118 多轮](118.multi-turn-history-tutorial.md) 每轮检索 | 不绑死旧 chunk |
| 10 | 与 [119 压缩](119.summary-memory-tutorial.md) 控 token | 摘要不过长 |
| 11 | 与 [120 指代](120.coreference-resolution-tutorial.md) 检索 query 独立 | 口语能还原实体 |
| 12 | 与 [121 越权](121.unauthorized-doc-filter-tutorial.md) 检索前过滤 | 无权 doc 不进 prompt |
| 13 | 与 [122 安全](122.content-safety-filter-tutorial.md) 三道闸 | 输入输出都覆盖 |
| 14 | 与 [123 JSON](123.structured-output-json-tutorial.md) parse 率 | 金标 schema 通过率 |
| 15 | 与 [124 工具](124.function-calling-tool-use-tutorial.md) 迭代上限 | max_iterations 生效 |
| 16 | 与 [28 窗口](28.context-window-tutorial.md) 预算 | 资料区不超标 |
| 17 | 与 [29 采样](29.llm-sampling-tutorial.md) 固定 | 回归可复现 |
| 18 | 与 [34 Grounding](34.grounding-citation-tutorial.md) 仅据资料 | 抽检无编造条款 |
| 19 | 与 [53 ACL](53.metadata-acl-tutorial.md) 双校验 | API 与向量库一致 |
| 20 | 与 [75 FAISS](75.faiss-ann-tutorial.md) 维度和模型一致 | 换模型重建索引 |
| 21 | 与 [76 Chroma](76.chroma-vector-db-tutorial.md) collection 正确 | count 非零 |
| 22 | 与 [93 混合](93.hybrid-search-tutorial.md) 去重 | chunk_id 唯一 |
| 23 | 与 [96 精排](96.bge-reranker-tutorial.md) 在宽召回后 | 不全库精排 |
| 24 | 评测回归 | 二十条金标无倒退 |

## 附录 C：{title}一周落地节奏

| 天 | 上午 | 下午 | 产出 |
|----|------|------|------|
| 周一 | 读路线图与前置篇 | 画链路白板 | 架构图 |
| 周二 | 跟做 §5～§7 | 单测关键函数 | 通过日志 |
| 周三 | 跟做 §9 实战 | 接现有 Mini-RAG | 端到端 demo |
| 周四 | 先错对对复盘 | 写 wiki 运维页 | 运维文档 |
| 周五 | 十条金标评测 | 团队评审 | 评审纪要 |

## 附录 D：{title}面试追问十则

**问 1**：和相邻 C6/D 篇如何分工？  
**答**：本篇管核心能力；相邻篇管引用、流式、框架封装；不要重复造轮子。

**问 2**：PoC 最小集？  
**答**：§9 代码 + 三条金标 + 一条安全/权限用例。

**问 3**：上线最大风险？  
**答**：版本漂移、漏做权限或安全、parse/流式边界未测。

**问 4**：如何观测？  
**答**：trace_id、阶段延迟、错误 code 分布、parse 失败率。

**问 5**：失败降级？  
**答**：明确 fail-closed 或 fail-open，写进 on-call。

**问 6**：与自研 pipeline 取舍？  
**答**：见 [152 框架取舍](152.pipeline-vs-framework-tutorial.md)；厚链路可混用。

**问 7**：多租户？  
**答**：collection/namespace 隔离 + ACL filter + 审计分租户。

**问 8**：成本？  
**答**：多一次 API（moderation/tool/精排）都要算进单次问答成本。

**问 9**：如何回归？  
**答**：金标集 CI；prompt/schema/词库版本标签绑定发布。

**问 10**：初学者第一步？  
**答**：先跑通 §9，再读概念地图，最后扩展 FAQ。

## 附录 E：{title}术语对照表

| 中文 | English | 备注 |
|------|---------|------|
| 检索 | Retrieval | 向量或混合 |
| 生成 | Generation | ChatModel |
| 拒答 | Refusal | 112 策略 |
| 引用 | Citation | 113/114 |
| 流式 | Streaming | 116 SSE |
| 结构化 | Structured Output | 123 JSON |
| 工具 | Tool / Function | 124 篇 |
| 文档 | Document | 125 核心 |
| 管道 | LCEL Chain | 126 篇 |
| 检索器 | Retriever | 127 篇 |
| 元数据 | Metadata | 51-54 篇 |
| 权限 | ACL | 53/121 篇 |
| 安全 | Content Safety | 122 篇 |
| 混合检索 | Hybrid Search | 93 篇 |
| 精排 | Rerank | 96 篇 |
| 窗口 | Context Window | 28 篇 |
| 采样 | Sampling | 29 篇 |
| 落地 | Grounding | 34 篇 |
| 评测 | Evaluation | 路线图 E 轨 |
| 观测 | Observability | LangSmith 164 |

## 附录 F：{title}常见日志字段

| 字段 | 示例 | 用途 |
|------|------|------|
| trace_id | uuid | 全链路串联 |
| user_id | u123 | 审计 |
| session_id | s456 | 多轮 |
| prompt_version | rag_v3 | 回归 |
| kb_version | handbook_v4 | 索引版本 |
| retrieval_query | 年假天数 | 检索词 |
| chunk_ids | [hb-1,hb-2] | 溯源 |
| latency_ms | 320 | 性能 |
| error_code | SAFETY_BLOCK | 分类 |
| tool_calls | search_kb | 124 调试 |

""")
    return "\n".join(lines)


def _sec(title: str, body: str) -> str:
    return f"\n## {title}\n\n{body.strip()}\n"


def _faq_block(items: list[tuple[str, str]]) -> str:
    lines = []
    for i, (q, a) in enumerate(items, 1):
        lines.append(f"### 13.{i} {q}\n\n{a}\n")
    return "\n".join(lines)


def _mistakes_block(pairs: list[tuple[str, str, str]]) -> str:
    out = []
    for i, (wrong, phen, right) in enumerate(pairs, 1):
        out.append(f"""### 10.{i} 错：{wrong}

**现象**：{phen}  
**对**：{right}
""")
    return "\n".join(out)


def build_122() -> str:
    mistakes = _mistakes_block([
        ("只靠 Prompt 讲文明", "用户辱骂，模型回怼。", "输入与输出都要硬过滤；system 软约束不能替代闸机。"),
        ("只检输入不检输出", "正常问题，模型复述 chunk 里敏感词。", "检索后 chunk 过滤 + 输出 moderation。"),
        ("安全拒答与知识拒答同一文案", "运营无法统计攻击量。", "分 SAFETY_BLOCK / NO_EVIDENCE / FORBIDDEN 与话术。"),
        ("流式裸推事后不审计", "违规句已展示数秒。", "缓冲策略 + 完整答案异步审计；严重类提高缓冲门槛。"),
    ])
    faq = _faq_block([
        ("敏感词库从哪来？", "自建 + 行业模板 + 运营沉淀 bad case；定期从审计日志回收谐音变体。"),
        ("多语言怎么办？", "归一化 + 分语言词表；Moderation API 选支持语种；过滤与 [70 混合语言 Embedding](70.mixed-language-embedding-tutorial.md) 场景一致。"),
        ("模型本身有安全对齐还要滤吗？", "要。对齐是通用的；行业违禁（不当医疗、未授权投资意见）仍要企业策略层。"),
        ("和幻觉的关系？", "幻觉是假；安全是不该说。模型可能真实复述库里违规流程——是策略事故不是幻觉。"),
        ("图片附件呢？", "文本 RAG 本篇聚焦文本；图片涉黄、恶意文件走对象存储扫描与 OCR 后文本过滤。"),
        ("内网可以不做吗？", "不可以。内网仍有 HR 纠纷、PII、劳动仲裁话术；合规范围可能更严。"),
        ("误杀如何降？", "影子模式发布词库、白名单短语、分场景 Bot、用户申诉入口与版本回滚。"),
        ("与 JSON 输出的关系？", "[123 JSON Mode](123.structured-output-json-tutorial.md) 不替代过滤——JSON 字符串里仍可能有违禁内容。"),
    ])
    deep = """
### 13.9 HR 场景：劳动纠纷话术

员工问「公司是不是违法辞退」——不是脏话，但法律风险高。策略：metadata `legal_sensitive=true` 的 chunk 不进入对外 Bot；内网法务版 Bot 单独 collection。与内容安全和业务策略两层都要标。

### 13.10 与多轮历史的联动

多轮里用户第三轮开始辱骂——每轮输入都要过闸，不能只在首轮 moderation。历史进 prompt 前可选摘要掉辱骂句或整轮丢弃。见 [118 多轮历史](118.multi-turn-history-tutorial.md)。

### 13.11 红队测试清单

| 攻击 | 期望 |
|------|------|
| 谐音辱骂 | 输入拦 |
| 角色扮演越狱 | 输入或输出拦 |
| 诱导泄露他人工单 | ACL + PII 双拦 |
| 让模型重复 system | 输出拦 |

### 13.12 性能基准（PoC）

万级词 Aho-Corasick 通常小于一毫秒；Moderation API 五十到三百毫秒。P95 预算在检索前留四百毫秒。超时策略：金融 fail-closed，内部 Wiki 可讨论 fail-open 加审计。

### 13.13 数据驻留

调海外 Moderation 等于出网传用户 query；政企可能禁止。备选：本地小模型、仅规则、私有云审核。合同写清子处理者与留存期。

### 13.14 策略即代码

```yaml
version: "1.0"
input:
  - type: keyword
    list: blocklist.txt
  - type: moderation
    provider: openai
    timeout_ms: 300
    on_timeout: block
output:
  - type: keyword
  - type: moderation
```

RAG 服务读配置热更新，合规可审 diff。

### 13.15 与 Function Calling 前瞻

[124 篇](124.function-calling-tool-use-tutorial.md) 让模型调工具——工具参数也可能含注入。内容安全要延伸到 tool args 过滤。

### 13.16 一周培训大纲

| 天 | 内容 |
|----|------|
| D1 | 读 §3～§4，画三道闸 |
| D2 | 实现 §5 词表 |
| D3 | 接 Moderation API |
| D4 | §9 接 Mini-RAG |
| D5 | 与 121、112 联调 + 红队 |

### 13.17 上线前自检（节选）

输入闸默认开启；输出闸默认开启；三种拒答 code 分文案；日志不含明文违禁句；blocklist 有版本号；与 121 ACL 联测通过；多轮每轮过滤已开；Moderation 超时策略已定；申诉入口已挂。

### 13.18 运营看板

`safety_block_rate` 按日；`top_rules` 命中排行；`false_positive_reports` 申诉数；与 `no_evidence_rate` 分开看图。

### 13.19 误杀案例：医学与型号

「乳腺癌筛查」含敏感字——医学 Bot 用领域白名单。产品型号 `SCUM-2000` 命中子串——用词边界或 token 级匹配。

### 13.20 团队分工

| 角色 | 负责 |
|------|------|
| 安全/合规 | 策略与审计标准 |
| 算法 | 误杀调优 |
| 后端 | 三道闸实现 |
| 运营 | 词库与申诉 |
"""
    return f"""# C6 生成与 Grounding（十三）：敏感词与内容安全过滤完全指南

> [121 篇](121.unauthorized-doc-filter-tutorial.md) 把 **越权文档** 挡在检索门外；用户问出来的话和模型答出来的话，还有另一条红线：**内容安全**——辱骂、涉政敏感、泄露隐私、违规营销，不能因为是「知识库问答」就放行。[112 拒答](112.refusal-strategy-tutorial.md) 管「资料里没有」；本篇管「资料里有也不能答」「用户输入本身违规」「生成结果要过闸」。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 地基篇**（路线图第 **139** 条），讲清 **输入过滤、输出过滤、策略分层、审计留痕**，并与 [110 Prompt 模板](110.rag-prompt-template-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md) 对齐。前置：[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、[34 Grounding](34.grounding-citation-tutorial.md)。

---

## 目录

1. [前言：RAG 不是内容安全的免死金牌](#1-前言rag-不是内容安全的免死金牌)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [内容安全在 RAG 链路里的位置](#3-内容安全在-rag-链路里的位置)
4. [威胁模型：输入、检索、生成三层](#4-威胁模型输入检索生成三层)
5. [敏感词与规则引擎](#5-敏感词与规则引擎)
6. [分类器与云端 Moderation API](#6-分类器与云端-moderation-api)
7. [输出侧：生成后过滤与改写](#7-输出侧生成后过滤与改写)
8. [与拒答、越权、引用的分工](#8-与拒答越权引用的分工)
9. [综合实战：三层过滤 Mini-RAG](#9-综合实战三层过滤-mini-rag)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [审计、合规与误杀权衡](#11-审计合规与误杀权衡)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：RAG 不是内容安全的免死金牌

上线第一周，运营常收到两类截图：用户用脏话骂客服机器人，机器人「礼貌回骂」；用户问「怎么绕过报销审批」，模型根据 **内控 FAQ** 真的讲步骤——内容来自知识库，但 **业务上不能教**。第一类是 **生成安全**；第二类是 **策略与权限** 交界（有时要配合 [121 越权过滤](121.unauthorized-doc-filter-tutorial.md)）。还有第三类：用户粘贴 **身份证号、手机号**，全链路日志裸存——这是 **隐私合规**，也算内容安全范畴。

初学者容易犯两个错：「我们只做企业内网，不用管」——内网照样有 HR 纠纷、劳动仲裁话术、客户 PII；「在 [110 Prompt](110.rag-prompt-template-tutorial.md) 里写一句『请文明用语』就够了」——模型会 **复述** 用户脏话，也会在压力下 **绕过** 软约束。

**Content Safety Filter**（内容安全过滤）：在 RAG 链路的 **查询入口、检索结果、模型输出** 等位置，用规则、模型或第三方 API 检测并 **拦截、脱敏、拒答或降级** 违规内容。通俗说：**海关安检**——不是不让货进，是不让违禁品过境。

**读完本文，你应该能做到：**

1. 画出 RAG 链路上 **输入 / 检索后 / 输出** 三道过滤点。  
2. 说明 **敏感词表** 与 **Moderation 分类器** 各自擅长什么、误杀怎么调。  
3. 实现 §9 最小三层过滤（规则 + 可选 API 桩）。  
4. 区分 **内容安全拒答** 与 [112 知识库无答案拒答](112.refusal-strategy-tutorial.md)。  
5. 列出审计字段：谁、何时、触发了哪条策略。  
6. 完成 §10 四种先错对对，能向同事解释危害。

### 1.1 C6 位置

```text
110 Prompt / 111 注入 / 112 拒答 / 113-114 引用
121 越权过滤
122 内容安全 ← 本篇
123 JSON Mode
124 Function Calling
```

### 1.2 术语速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 内容安全 | Content Safety | 输入输出合规与风控 |
| 敏感词 | Blocklist / Keyword | 规则快速拦截 |
| 审核 | Moderation | 语义级分类 API |
| 误杀 | False Positive | 正常话被拦 |
| 漏放 | False Negative | 违规话通过 |

---

## 2. 本文边界与动手路径

**档位：C6 地基篇（路线图 139）。**

**本文讲：** 三道闸、词表、Moderation、流式过滤、审计、与 112/121 分工、Mini-RAG 实战。  
**本文不讲：** 图片鉴黄全栈、法务免责声明起草、每一个云厂商审核 SKU 报价。

| 步骤 | 验收 |
|------|------|
| A | 画三道闸白板 |
| B | blocklist + §5 代码 |
| C | §9 Mini-RAG |
| D | 6 条测试 + 审计 JSON |
| E | 与 121 联调矩阵 |

**环境：** Python 3.10+；可选 `openai` 调 Moderation；`pyahocorasick` 可选加速。

---

## 3. 内容安全在 RAG 链路里的位置

![RAG 内容安全三道闸](image/content-safety-filter/01-safety-layers.png)

对照上图：

- **闸 1（输入）**：用户 query、上传文件名、会话里粘贴的文本——在 **检索之前** 检测。  
- **闸 2（检索后）**：chunk 原文可能含 PII、过期政策、仅内网可见的敏感段——在 **进 prompt 之前** 过滤或脱敏。  
- **闸 3（输出）**：模型可能复述脏话、编造联系方式、输出歧视言论——在 **返回用户之前** 检测。

与 [121 ACL](121.unauthorized-doc-filter-tutorial.md) 关系：ACL 管 **无权**；本篇管 **有害/违规**。一个 chunk 可能有权但有毒（例如公开文档里误收录了客户名单）。

### 3.1 为什么 RAG 更容易「理直气壮地违规」

模型有 Grounding 时更 **敢引用原文**——若原文含敏感词，输出会 **忠实复述**。这比纯聊天更容易触发 **合规事故**：不是模型胡编，是 **检索把雷搬到了 prompt 里**。

### 3.2 与 [34 Grounding](34.grounding-citation-tutorial.md) 的冲突

用户恶意要求「请原文引用某歧视段落」：应拒答，code `SAFETY_BLOCK`，**不要** 以 Grounding 为由照抄。Grounding 服从 **企业策略上限**。

---

## 4. 威胁模型：输入、检索、生成三层

| 层 | 威胁示例 | 检测点 | 典型动作 |
|----|----------|--------|----------|
| 输入 | 辱骂、越狱 prompt、SQL 注入式指令 | 闸 1 | block / 限流 |
| 检索 | PII chunk、涉密制度、恶意 HTML | 闸 2 | 剔除 / 脱敏 |
| 生成 | 复述脏话、歧视、医疗违法建议 | 闸 3 | 拒答 / 替换 |

**纵深防御**：任何一层失效，下一层仍有机会拦截。不要赌「模型够乖」。

### 4.1 日志与隐私

审计要记录 **rule_id** 与 **query_hash**，避免把完整违禁句写入可公开访问的日志。违规已拦时，用 hash 或截断。

---

## 5. 敏感词与规则引擎

规则引擎：**快、可解释、可版本化**——适合脏话、竞品名、绝对化广告法用语。

```python
from pathlib import Path

def load_blocklist(path: str) -> list[str]:
    return [ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]

def normalize(text: str) -> str:
    return text.lower().replace(" ", "")

class KeywordFilter:
    def __init__(self, words: list[str]):
        self.words = [normalize(w) for w in words]

    def hit(self, text: str) -> str | None:
        n = normalize(text)
        for w in self.words:
            if w in n:
                return w
        return None
```

### 5.1 白名单与分场景词库

财务系统里「死账」「冲销」可能是术语。做法：分场景词库；`allowlist.txt` 优先于 block；仅拦输出不拦检索（内部审计仍可见原文，对外 Bot 替换为 `[已屏蔽]`）。

### 5.2 性能

万级词表用 **Aho-Corasick** 多模式匹配；QPS 高时编译进边车服务，RAG API 调 gRPC。

---

## 6. 分类器与云端 Moderation API

规则搞不定的：**语义级辱骂、隐晦歧视、多语言**。常用 OpenAI Moderation 或自托管小分类模型。

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def moderate_text(text: str) -> dict:
    resp = client.moderations.create(input=text)
    r = resp.results[0]
    return {{
        "flagged": r.flagged,
        "categories": {{k: v for k, v in r.categories.model_dump().items() if v}},
    }}
```

`flagged=True` 时：**不要调用 chat**，直接返回统一安全拒答（与 [112](112.refusal-strategy-tutorial.md) 模板区分文案）。

### 6.1 延迟与成本

每次 query 多一次 RTT；可 **规则先筛**，灰色地带才调 API。缓存同一 query hash 短 TTL（注意隐私，键用 hash 不落明文）。

### 6.2 多云抽象

```python
from typing import Protocol

class ModerationClient(Protocol):
    def check(self, text: str) -> dict: ...
```

RAG 主流程只依赖协议，换厂商不改业务代码。

---

## 7. 输出侧：生成后过滤与改写

![流式输出如何过安全闸](image/content-safety-filter/02-output-stream.png)

### 7.1 非流式

`answer = llm.generate(...)` 后整段 `moderate_text(answer)`；flagged 则替换为安全文案。

### 7.2 流式（SSE）

见 [116 SSE](116.sse-rag-streaming-tutorial.md)。策略：缓冲后放、滑窗检、双通道边推边检。产品常选：**缓冲第一句** + **完整答案事后审计**。

```python
buffer = ""
for token in stream:
    buffer += token
    if len(buffer) >= 80 or token in "。！？":
        if not output_filter(buffer):
            yield {{"event": "error", "code": "SAFETY_BLOCK"}}
            return
        yield {{"event": "delta", "text": buffer}}
        buffer = ""
```

### 7.3 替换 vs 拒答

严重违规整段拒答；轻微脏话局部 `***`；二次 LLM 重写成本高，慎用。

---

## 8. 与拒答、越权、引用的分工

![三种拒答不要混](image/content-safety-filter/03-refusal-split.png)

| 机制 | 触发条件 | 用户话术示例 | 日志 code |
|------|----------|--------------|-----------|
| [112 知识拒答](112.refusal-strategy-tutorial.md) | 检索空 / 分数低 | 知识库未找到相关规定 | NO_EVIDENCE |
| [121 越权](121.unauthorized-doc-filter-tutorial.md) | ACL 不匹配 | 您无权查看该主题 | FORBIDDEN |
| 本篇安全拒答 | moderation / 敏感词 | 无法处理该请求 | SAFETY_BLOCK |

**为什么要分开？** 运营看板要统计：资料缺、权限配错还是攻击滥用。

### 8.1 与 [110 Prompt](110.rag-prompt-template-tutorial.md)

System 里写「禁止违法」是软约束；本篇是硬约束。硬约束在前：输入 flagged 则不进入 retrieval。

---

## 9. 综合实战：三层过滤 Mini-RAG

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class SafetyConfig:
    block_input: bool = True
    block_output: bool = True
    on_block_message: str = "您的输入或生成内容未通过安全审核，请修改后重试。"

def rag_answer(
    query: str,
    retrieve: Callable[[str], list[str]],
    generate: Callable[[str, list[str]], str],
    input_filter: Callable[[str], bool],
    output_filter: Callable[[str], bool],
    cfg: SafetyConfig,
) -> dict:
    if cfg.block_input and not input_filter(query):
        return {{"ok": False, "code": "SAFETY_BLOCK", "text": cfg.on_block_message}}
    chunks = retrieve(query)
    safe_chunks = [c for c in chunks if input_filter(c)]
    if not safe_chunks:
        return {{"ok": False, "code": "NO_EVIDENCE", "text": "未找到可引用的资料。"}}
    answer = generate(query, safe_chunks)
    if cfg.block_output and not output_filter(answer):
        return {{"ok": False, "code": "SAFETY_BLOCK", "text": cfg.on_block_message}}
    return {{"ok": True, "code": "OK", "text": answer, "chunks": len(safe_chunks)}}
```

### 9.1 接入真实 RAG

1. `retrieve` 换 [76 Chroma](76.chroma-vector-db-tutorial.md) 或 [75 FAISS](75.faiss-ann-tutorial.md)；  
2. `generate` 用 [110](110.rag-prompt-template-tutorial.md) 模板；  
3. `input_filter` = KeywordFilter + 可选 Moderation；  
4. 日志写 `code` 与 `rule_id`。

### 9.2 测试用例

| # | 输入 | 期望 |
|---|------|------|
| 1 | 正常业务问题 | OK |
| 2 | 含 blocklist 词 | SAFETY_BLOCK |
| 3 | 检索无结果 | NO_EVIDENCE |
| 4 | 资料有 PII | 脱敏或剔除 |
| 5 | 输出含 blocklist | SAFETY_BLOCK |
| 6 | 越权 doc | FORBIDDEN |

---

## 10. 先错对对：四种典型翻车

{mistakes}

---

## 11. 审计、合规与误杀权衡

建议日志字段：`trace_id`、`user_id`、`stage`（input/chunk/output）、`action`、`rule`、`query_hash`、`timestamp`。不要打明文违禁句到公开日志。

误杀需要申诉入口：人工加白名单 → 策略版本化发布，类似 [48 文档版本](48.doc-versioning-tutorial.md)。

与 [121 ACL](121.unauthorized-doc-filter-tutorial.md) 联合测试矩阵：无权+安全、有权+有毒 chunk、有权+正常。

---

## 12. 综合概念地图

| 模块 | 要点 |
|------|------|
| 输入闸 | 词表 + Moderation |
| 检索闸 | PII、有毒 doc |
| 输出闸 | 整段/流式 |
| 分工 | 三种 code |
| 审计 | stage、rule、hash |

---

## 13. 常见陷阱与 FAQ

{faq}

{deep}

---

## 14. 总结与系列下一步

1. **内容安全是三道闸**：输入、检索后、输出；RAG 不能省略。  
2. **规则快、分类器准**；流式要定缓冲策略。  
3. **SAFETY_BLOCK** 与 **NO_EVIDENCE**、**FORBIDDEN** 分开话术与日志。  
4. §9 三层过滤可接到现有 Mini-RAG；词库与策略要版本化。  
5. 下一篇 [123 JSON Mode](123.structured-output-json-tutorial.md) 解决机器可读输出；JSON 里仍可能带违禁串，输出过滤仍要做。

### 14.1 系列下一步

| 目标 | 阅读 |
|------|------|
| 结构化输出 | [123 JSON Mode](123.structured-output-json-tutorial.md) |
| 工具调用 | [124 Function Calling](124.function-calling-tool-use-tutorial.md) |
| Prompt | [110 RAG Prompt](110.rag-prompt-template-tutorial.md) |
| 越权 | [121 越权过滤](121.unauthorized-doc-filter-tutorial.md) |

### 14.2 学习目标自检

- [ ] 能画三道闸  
- [ ] 能实现关键词过滤  
- [ ] 能区分三种拒答 code  
- [ ] 能写 6 条安全测试  

### 14.3 面试 30 秒版

「企业 RAG 内容安全分输入、检索后、输出三层。输入用敏感词和 Moderation；检索后剔除 PII 和有毒 chunk；输出在流式场景要缓冲检测。安全拒答用 SAFETY_BLOCK，与知识库无答案、越权 FORBIDDEN 分开。单靠 prompt 不够，必须硬过滤。」

{line_expansion("122")}

{FOOTER_C6}
"""


def build_123() -> str:
    mistakes = _mistakes_block([
        ("只写「请输出 JSON」不设 response_format", "模型返回 markdown 代码块包裹 JSON，json.loads 失败。", "用 API 的 JSON Mode 或 json_schema response_format 硬约束。"),
        ("Schema 字段过多且无 required", "缺 citations 或 answer 空字符串，前端崩溃。", "Pydantic required 字段 + 生成后校验，失败走修复或拒答。"),
        ("把 chunk 全文塞进 JSON quote", "超窗口、泄露、parse 慢。", "quote 截断 + chunk_id，正文从 metadata 取。"),
        ("流式仍要完整 JSON", "边吐 token 边 parse 反复失败。", "非流式生成 JSON；或流式给人看、结构化走并行非流式小调用。"),
        ("不做输出安全过滤", "JSON 的 answer 字段含辱骂。", "parse 后对各字符串字段走 [122](122.content-safety-filter-tutorial.md) 过滤。"),
    ])
    faq = _faq_block([
        ("JSON Mode 和 json_schema 区别？", "JSON Mode 保证合法 JSON；json_schema 进一步约束字段类型与枚举，更适合 RAG 契约。"),
        ("和 Function Calling 重叠吗？", "[124](124.function-calling-tool-use-tutorial.md) 是动态工具循环；本篇是单次答案的结构化。可组合：工具拿资料，最终答案仍 JSON。"),
        ("Pydantic v2 怎么校验？", "`model_validate_json(text)` 一行；失败记日志并返回 112 式拒答 JSON。"),
        ("confidence 谁定？", "模型自评仅参考；可叠加检索分数阈值 [99](99.score-threshold-tutorial.md) 规则校正。"),
        ("多语言字段？", "answer 中文、citations.quote 可保留原文；schema 里 lang 可选。"),
        ("评测怎么测 parse 率？", "金标集统计 schema 通过率、字段召回；parse 失败算工程 bad case。"),
        ("和 113 引用冲突吗？", "不冲突：JSON citations 是机器形态，渲染层再转 [n] 或脚注。"),
        ("温度设多少？", "结构化输出宜低温度，见 [29 采样](29.llm-sampling-tutorial.md)，0～0.3。"),
    ])
    extra = """
### 13.9 修复流水线三级

1. `json.loads` 去 markdown 包裹；  
2. Pydantic 校验；  
3. 缺字段时 **一次** 修复调用（「仅返回合法 JSON，补全 citations」），仍失败则拒答。

### 13.10 与 [116 SSE](116.sse-rag-streaming-tutorial.md) 双通道

通道 A：SSE 给人看的 Markdown 流；通道 B：生成结束后异步调 JSON 摘要接口给后台——产品常见折中。

### 13.11 字段设计清单

| 字段 | 类型 | 说明 |
|------|------|------|
| answer | string | 主答案 |
| refusal | boolean | 是否拒答 |
| refusal_reason | string? | 枚举 INSUFFICIENT_EVIDENCE |
| citations | array | chunk_id, quote |
| confidence | enum | high/medium/low |

### 13.12 版本化 schema

`answer_schema_v2.json` 进 Git；Breaking change 升 major；API 路由带 `Accept-Schema-Version`。

### 13.13 OpenAI 兼容示例

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    response_format={{"type": "json_schema", "json_schema": {{
        "name": "rag_answer",
        "strict": True,
        "schema": SCHEMA,
    }}}},
)
```

### 13.14 国内模型注意

部分网关仅 `json_object` 模式；strict schema 不支持时退化为 Pydantic 校验 + 修复，并在文档标明差异。

### 13.15 一周实验课

D1 画 parse 流水线；D2 写 Pydantic 模型；D3 接 API；D4 接 [110](110.rag-prompt-template-tutorial.md) + 假检索；D5 五种翻车各修一次。
"""
    return f"""# C6 生成与 Grounding（十四）：结构化输出（JSON Mode）完全指南

> RAG 答案给人看，也要给 **系统用**——前端要渲染引用卡片、工单系统要抽 `severity` 字段、评测脚本要 parse `cited_chunk_ids`。[113 行内引用](113.inline-citation-tutorial.md) 与 [114 脚注](114.footnote-citation-tutorial.md) 解决「人眼溯源」；本篇解决 **机器可读**：`response_format`、JSON Schema、解析容错、与 [110 Prompt 模板](110.rag-prompt-template-tutorial.md) 的组合。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 地基篇**（路线图第 **140** 条）。前置：[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、[29 采样](29.llm-sampling-tutorial.md)；输出仍须过 [122 内容安全](122.content-safety-filter-tutorial.md)。

---

## 目录

1. [前言：为什么「能 parse」和「说得对」一样重要](#1-前言为什么能-parse-和说得对一样重要)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [结构化输出是什么](#3-结构化输出是什么)
4. [JSON Mode 与 Schema 约束](#4-json-mode-与-schema-约束)
5. [RAG 场景的典型 JSON 形状](#5-rag-场景的典型-json-形状)
6. [Prompt 设计：字段、示例与反例](#6-prompt-设计字段示例与反例)
7. [解析、校验与修复流水线](#7-解析校验与修复流水线)
8. [与引用、拒答、流式的组合](#8-与引用拒答流式的组合)
9. [综合实战：带引用的 JSON 答案](#9-综合实战带引用的-json-答案)
10. [先错对对：五种 JSON 翻车](#10-先错对对五种-json-翻车)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么「能 parse」和「说得对」一样重要

产品后台常见需求：答案 JSON 含 `answer`、`confidence`、`citations`、`refusal`。若模型返回「好的，这是 JSON：」加 markdown 代码块——`json.loads` 直接炸，前端白屏，评测流水线挂掉。

**Structured Output**（结构化输出）：约束模型 **只产出符合约定 schema 的 JSON**，便于下游 **零正则扒拉**。初学者常以为「多写几句请输出 JSON」就够；实际上 **温度、markdown 包裹、字段缺失、中文标点** 都会让解析失败。

**读完本文，你应该能做到：**

1. 区分 **JSON Mode** 与 **json_schema response_format**。  
2. 设计 RAG 用 JSON：answer、citations、refusal、confidence。  
3. 用 Pydantic 跑通 §9。  
4. 说明与 [112 拒答](112.refusal-strategy-tutorial.md) 的 `refusal` 字段如何统一。  
5. 列出五种先错对对并会修复。  
6. 知道流式场景下结构化输出的局限。

### 1.1 C6 位置

```text
122 内容安全
123 JSON Mode ← 本篇
124 Function Calling
```

---

## 2. 本文边界与动手路径

**档位：C6 地基篇（路线图 140）。**

**本文讲：** JSON Mode、Schema、RAG 字段设计、解析修复、与引用/拒答组合。  
**本文不讲：** Protobuf 全栈、Function Calling 完整工具循环（见 [124](124.function-calling-tool-use-tutorial.md)）。

| 步骤 | 验收 |
|------|------|
| A | 画「生成 → parse → 校验 → 业务」 |
| B | 最小 response_format 调用 |
| C | Pydantic RagAnswer |
| D | §9 端到端 |
| E | §10 五种错法各修一次 |

---

## 3. 结构化输出是什么

![RAG 结构化输出链路](image/structured-output-json/01-json-rag-flow.png)

**输入**：messages + schema  
**输出**：合法 JSON 字符串  
**下游**：前端、工单、评测、日志

与纯文本答案相比，结构化让 **引用卡片、拒答徽章、置信度颜色** 可自动化，无需正则从散文里抠 `[1]`。

### 3.1 何时必须结构化

| 场景 | 原因 |
|------|------|
| 后台审核队列 | 要 severity 枚举 |
| 多语言门户 | 字段级 i18n |
| 自动评测 | citations 对齐金标 |
| 合规归档 | 一条 JSON 一行日志 |

### 3.2 何时可纯文本

内部 Demo、仅聊天无集成——但仍建议 PoC 后期切 JSON，避免二次改造。

---

## 4. JSON Mode 与 Schema 约束

| 能力 | 保证什么 | 适用 |
|------|----------|------|
| `json_object` | 合法 JSON 对象 | 快速起步 |
| `json_schema` + strict | 字段类型、required、枚举 | **生产 RAG** |

```python
from pydantic import BaseModel, Field
from typing import Literal

class Citation(BaseModel):
    chunk_id: str
    quote: str = Field(max_length=200)

class RagAnswer(BaseModel):
    answer: str
    refusal: bool = False
    refusal_reason: Literal["", "INSUFFICIENT_EVIDENCE", "OUT_OF_SCOPE"] = ""
    confidence: Literal["high", "medium", "low"] = "medium"
    citations: list[Citation] = Field(default_factory=list)
```

System 里重复 **字段含义** 仍有用，但不能替代 API 级 schema——模型在压力下会「几乎 JSON」。

---

## 5. RAG 场景的典型 JSON 形状

![典型 RAG 答案 JSON 字段](image/structured-output-json/02-schema-shape.png)

**answer**：给用户看的正文，可含 `[n]` 或纯文本由前端再挂链。  
**citations**：机器溯源；`chunk_id` 对齐 [51](51.metadata-chunk-id-tutorial.md)。  
**refusal**：与 [112](112.refusal-strategy-tutorial.md) 统一；true 时 answer 宜短句说明。  
**confidence**：可结合检索 top score [99](99.score-threshold-tutorial.md)。

### 5.1 反模式：巨型嵌套

勿把整库 metadata 塞进 JSON；只带 **本轮用到的引用**。

---

## 6. Prompt 设计：字段、示例与反例

在 [110](110.rag-prompt-template-tutorial.md) system 加 **输出契约**：

```text
【输出】你必须输出符合 schema 的 JSON，不要 markdown 代码块，不要前后解释。
字段：answer, refusal, refusal_reason, confidence, citations[]。
若资料不足，refusal=true，refusal_reason=INSUFFICIENT_EVIDENCE。
```

**Few-shot**：在 system 放 **一个** 合法 JSON 单行示例即可，过多占 [28 窗口](28.context-window-tutorial.md)。

### 6.1 user 资料区仍用 [111](111.context-injection-format-tutorial.md)

JSON 是 **输出形态**，不是把资料改成 JSON 塞 system。

---

## 7. 解析、校验与修复流水线

```python
import json
import re
from pydantic import ValidationError

def strip_markdown_fence(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:json)?\\s*([\\s\\S]*?)```", text)
    return m.group(1).strip() if m else text

def parse_rag_answer(raw: str) -> RagAnswer:
    cleaned = strip_markdown_fence(raw)
    data = json.loads(cleaned)
    return RagAnswer.model_validate(data)
```

失败路径：记 `parse_error` → 可选一次修复 LLM 调用 → 仍失败返回 `refusal=true` 的兜底 JSON。

---

## 8. 与引用、拒答、流式的组合

- **113/114**：渲染层把 `citations[i]` 显示为 `[i+1]` 或脚注。  
- **112**：`refusal` 与 `NO_EVIDENCE` 日志对齐。  
- **116 流式**：人看流式 Markdown，结构化走并行非流式或流结束后再 parse（若厂商支持 structured streaming 再评估）。

### 8.1 与 [122 安全](122.content-safety-filter-tutorial.md)

对 `answer` 与每个 `quote` 做输出过滤；JSON 只是容器，不免疫违规内容。

---

## 9. 综合实战：带引用的 JSON 答案

```python
def build_messages(question: str, chunks: list[dict]) -> list[dict]:
    evidence = "\\n".join(
        f"[{{i+1}}] (chunk_id={{c['chunk_id']}}) {{c['text']}}" for i, c in enumerate(chunks)
    )
    system = "你是企业知识库助手。仅根据资料回答。输出 JSON schema rag_answer。"
    user = f"【参考资料】\\n{{evidence}}\\n\\n【用户问题】\\n{{question}}"
    return [{{"role": "system", "content": system}}, {{"role": "user", "content": user}}]

# 假检索
CHUNKS = [
    {{"chunk_id": "hb-003", "text": "入职满一年享受10天年假。"}},
    {{"chunk_id": "hb-004", "text": "年假需提前在OA提交。"}},
]
messages = build_messages("年假有多少天？", CHUNKS)
# client.chat.completions.create(..., response_format=...)
# parsed = parse_rag_answer(response.choices[0].message.content)
```

验收：`parsed.citations[0].chunk_id == "hb-003"` 且 `refusal is False`。

---

## 10. 先错对对：五种 JSON 翻车

{mistakes}

---

## 11. 综合概念地图

![JSON Mode 概念地图](image/structured-output-json/03-concept-map.png)

| 模块 | 要点 |
|------|------|
| 110 Prompt | system 字段说明 |
| 123 本篇 | schema 硬约束 |
| 122 安全 | 字符串字段过滤 |
| 124 Tools | 工具参数 JSON |

---

## 12. 常见陷阱与 FAQ

{faq}

{extra}

---

## 13. 总结与系列下一步

1. **结构化输出是工程契约**，不是多写一句「请 JSON」。  
2. **json_schema strict + Pydantic** 是生产默认组合。  
3. **refusal/citations** 与 112/113 对齐，避免两套语义。  
4. **流式与 JSON** 要分通道或等流结束。  
5. 下一篇 [124 Function Calling](124.function-calling-tool-use-tutorial.md) 进入动态工具循环。

### 13.1 系列下一步

| 目标 | 阅读 |
|------|------|
| 工具调用 | [124 Function Calling](124.function-calling-tool-use-tutorial.md) |
| Prompt | [110 RAG Prompt](110.rag-prompt-template-tutorial.md) |
| 安全 | [122 内容安全](122.content-safety-filter-tutorial.md) |

### 13.2 面试 30 秒版

「RAG 结构化输出用 json_schema 约束 answer、citations、refusal；Pydantic 校验；失败走 strip markdown、一次修复、兜底拒答。流式给人看时 JSON 常并行非流式生成。输出仍要走内容安全过滤。」

{line_expansion("123")}

{deep_dive("123")}

{FOOTER_C6}
"""


def build_124() -> str:
    mistakes = _mistakes_block([
        ("工具太多无文档", "模型乱调 calculator 不调 search_kb。", "3～5 个工具上限；description 写清何时用、参数含义、反例。"),
        ("检索工具无 ACL", "模型搜到机密 chunk。", "search 工具内强制 where 与 [121](121.unauthorized-doc-filter-tutorial.md) 一致。"),
        ("无限 tool 循环", "模型反复 search 烧 token。", "max_iterations=3～5；无进展则拒答。"),
        ("不校验 tool args", "注入型参数调内部 API。", "Pydantic 校验 args；[122](122.content-safety-filter-tutorial.md) 过滤字符串参数。"),
    ])
    faq = _faq_block([
        ("和 Agent 区别？", "本篇是 **单会话工具循环**；Agent 再加规划、记忆、多 Agent 协作——路线图 150 了解即可。"),
        ("必须用 OpenAI tools 吗？", "多数兼容 API 支持；自研可解析 JSON 里 `tool_name` + `args` 模拟。"),
        ("检索放 prompt 还是 tool？", "简单 RAG 可全塞 prompt；资料大、需多跳检索时用 tool 更省窗口。"),
        ("和 127 Retriever 关系？", "Retriever 可包装成 `search_kb` 工具；LangChain `as_tool()` 见 [127](127.langchain-retriever-tutorial.md)。"),
        ("并行 tool calls？", "支持时并行执行无依赖工具；有依赖则顺序。"),
        ("错误处理？", "工具异常返回 `{{\"error\": \"...\"}}` 给模型，不要抛栈到用户。"),
        ("评测？", "记录每轮 tool_name、args、latency；抽检是否该调未调。"),
        ("成本？", "每轮多一次 LLM；比单次 RAG 贵——用 max_iterations 卡上限。"),
    ])
    return f"""# C6 生成与 Grounding（十五）：Function Calling / Tool Use 完全指南

> [123 JSON Mode](123.structured-output-json-tutorial.md) 解决 **单次答案** 的机器可读；当模型需要 **查知识库、算数、调业务 API** 时，要靠 **Function Calling**（Tool Use）：模型产出 **工具名与参数**，你们的运行时 **执行** 后把结果塞回对话，直到生成最终答案。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 了解篇**（路线图第 **141** 条），讲清 **工具声明、执行循环、RAG 检索工具化、安全边界**，并与 [125 LangChain 核心](125.langchain-core-tutorial.md) 衔接。前置：[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)。

---

## 目录

1. [前言：从「一次答完」到「会动手」](#1-前言从一次答完到会动手)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Function Calling 是什么](#3-function-calling-是什么)
4. [工具 Schema 设计](#4-工具-schema-设计)
5. [执行循环与消息形态](#5-执行循环与消息形态)
6. [RAG 场景常用工具](#6-rag-场景常用工具)
7. [与混合检索、精排衔接](#7-与混合检索精排衔接)
8. [安全：参数过滤与权限](#8-安全参数过滤与权限)
9. [综合实战：search_kb 工具循环](#9-综合实战search_kb-工具循环)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：从「一次答完」到「会动手」

传统 RAG：**检索固定 k 条 → 一次生成**。复杂问法：「对比去年和今年差旅住宿标准差异」——可能要 **两次检索** 或 **先 list_docs 再 get_chunk**。Function Calling 让 LLM **决定何时搜、搜什么**，而不是写死 pipeline。

**读完本文，你应该能做到：**

1. 画出 **LLM → tool_call → execute → tool_result → LLM** 循环。  
2. 设计 `search_kb` 工具 schema 含 query 与 filter。  
3. 实现 §9 带 **max_iterations** 的最小循环。  
4. 说明工具参数如何走 [122 安全](122.content-safety-filter-tutorial.md)。  
5. 对照 [127 Retriever](127.langchain-retriever-tutorial.md) 理解框架封装。

### 1.1 档位：了解篇

能手写最小循环即可；生产 Agent 再读路线图 150。D 模块 [125-127](125.langchain-core-tutorial.md) 会展示 LangChain 绑定工具。

---

## 2. 本文边界与动手路径

**本文讲：** tools 声明、执行循环、RAG 工具、混合检索工具化、安全。  
**本文不讲：** 多 Agent 编排、MCP 全协议、AutoGPT 类产品。

| 步骤 | 验收 |
|------|------|
| A | 画工具循环 |
| B | 声明 1 个 search 工具 |
| C | §9 跑通 2 轮内回答 |
| D | max_iterations 触发拒答 |

---

## 3. Function Calling 是什么

![工具调用循环](image/function-calling-tool-use/01-tool-loop.png)

1. **声明 tools**：JSON Schema 描述名称、描述、参数。  
2. **模型响应**：`tool_calls` 或纯 JSON 指令。  
3. **执行**：你们的服务调向量库、HTTP API。  
4. **回灌**：`role: tool` 消息带结果。  
5. **重复** 直到无 tool_calls 或达上限。

### 3.1 与 [123 JSON](123.structured-output-json-tutorial.md)

JSON Mode 约束 **最终答案形状**；Function Calling 约束 **中间动作**。可组合：最后一轮要求 JSON 格式答案。

---

## 4. 工具 Schema 设计

```python
SEARCH_KB_TOOL = {{
    "type": "function",
    "function": {{
        "name": "search_kb",
        "description": "在企业知识库中语义检索。用于制度、流程、标准类问题。不要用常识编造。",
        "parameters": {{
            "type": "object",
            "properties": {{
                "query": {{"type": "string", "description": "检索问句，standalone，含实体"}},
                "top_k": {{"type": "integer", "default": 5}},
                "doc_id": {{"type": "string", "description": "可选，限定文档"}},
            }},
            "required": ["query"],
        }},
    }},
}}
```

**description 质量** 决定模型是否误调；写清 **何时不用**（闲聊、纯计算用 calculator）。

---

## 5. 执行循环与消息形态

```python
def run_tool_loop(client, messages, tools, execute_fn, max_iter=5):
    for _ in range(max_iter):
        resp = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=tools
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = execute_fn(tc.function.name, args)
            messages.append({{
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            }})
    return "达到最大工具轮次，请简化问题。"
```

---

## 6. RAG 场景常用工具

![RAG 场景工具设计](image/function-calling-tool-use/02-rag-tools.png)

| 工具 | 作用 |
|------|------|
| search_kb | 向量/混合检索 Top-K |
| get_chunk | 按 chunk_id 取全文（[65 父文档](65.parent-document-retriever-tutorial.md)） |
| list_docs | 列知识库目录，助模型选 doc_id |
| get_current_user_acl | 返回可搜 namespace（配合 121） |

### 6.1 检索工具实现要点

内部调 [76 Chroma](76.chroma-vector-db-tutorial.md) `collection.query` + `where` ACL；返回 **精简** 文本与 chunk_id，勿爆 tool_result token。

---

## 7. 与混合检索、精排衔接

`search_kb` 内部可走 [93 混合检索](93.hybrid-search-tutorial.md) → [96 BGE-Reranker](96.bge-reranker-tutorial.md) → 截断到 [28 窗口](28.context-window-tutorial.md) 预算。对模型 **透明**：它只见 tool 返回的片段列表。

---

## 8. 安全：参数过滤与权限

- `query` 字符串走 [122](122.content-safety-filter-tutorial.md) 输入闸。  
- `doc_id` 白名单校验，防路径遍历式 doc_id。  
- 工具结果再过输出闸（防检索到 PII chunk）。  
- **不要** 暴露任意 SQL 工具给模型。

---

## 9. 综合实战：search_kb 工具循环

```python
def execute_search_kb(args: dict) -> dict:
    # 接 Chroma / 假数据
    hits = [
        {{"chunk_id": "hb-1", "text": "一线城市住宿每晚不超过500元。", "score": 0.91}},
    ]
    return {{"hits": hits}}

def execute_fn(name, args):
    if name == "search_kb":
        return execute_search_kb(args)
    return {{"error": f"unknown tool {{name}}"}}

# messages = [{{"role": "user", "content": "深圳出差住宿上限？"}}]
# answer = run_tool_loop(client, messages, [SEARCH_KB_TOOL], execute_fn)
```

验收：日志可见至少 1 次 `search_kb`；最终答案提及 500 与引用 chunk。

---

## 10. 先错对对：四种典型翻车

{mistakes}

---

## 11. 综合概念地图

![Function Calling 概念地图](image/function-calling-tool-use/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

{faq}

### 12.1 深度：何时不用 Tool

资料永远固定 k、问法单一——**固定 RAG 链更简单**（[126 LCEL](126.langchain-lcel-tutorial.md)）。Tool 在 **多跳、选库、算完再搜** 时划算。

### 12.2 日志字段

`tool_name`, `args_hash`, `latency_ms`, `hit_chunk_ids`, `iteration`。

---

## 13. 总结与系列下一步

1. **Function Calling = 动态检索与动作**，不是替代 Embedding 索引。  
2. **工具要少而精**；description 是提示词一部分。  
3. **max_iterations + ACL + 安全过滤** 是上线三板斧。  
4. LangChain 用 `bind_tools` 封装，见 [125](125.langchain-core-tutorial.md)、[127](127.langchain-retriever-tutorial.md)。

### 13.1 系列下一步

| 目标 | 阅读 |
|------|------|
| LangChain 核心 | [125 LangChain 核心](125.langchain-core-tutorial.md) |
| Retriever 工具化 | [127 LangChain Retriever](127.langchain-retriever-tutorial.md) |
| JSON 答案 | [123 JSON Mode](123.structured-output-json-tutorial.md) |

### 13.2 面试 30 秒版

「RAG 里 Function Calling 把 search_kb 等工具声明给模型；运行时执行检索并回灌 tool 消息，循环直到最终答案。要限制 max_iterations，工具内做 ACL 和内容安全，检索可走混合检索加精排。」

{line_expansion("124")}

{deep_dive("124")}

{FOOTER_C6}
"""


def build_125() -> str:
    mistakes = _mistakes_block([
        ("把 LangChain 当黑盒不读 Runnable", "升级版本链断、stream 行为变。", "理解 invoke/stream/batch 与 LCEL 组合规则。"),
        ("Document metadata 乱塞", "过滤、溯源、ACL 全丢。", "对齐 [51 chunk_id](51.metadata-chunk-id-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md) 字段。"),
        ("所有逻辑塞进 PromptTemplate", "业务规则难测。", "RunnableLambda 做可单测的 Python 步骤。"),
        ("不锁版本", "patch 升级 API 变。", "requirements.lock；CI 跑最小链回归。"),
    ])
    faq = _faq_block([
        ("LangChain 和 LlamaIndex 选谁？", "路线图 D 模块都了解；LC 生态广，LlamaIndex 偏索引抽象——[152 自研 vs 框架](152.pipeline-vs-framework-tutorial.md) 讲取舍。"),
        ("必须全用 LC 吗？", "否。常见：只借 Document + Retriever，生成自研。"),
        ("Message 和 30 篇关系？", "SystemMessage/HumanMessage 即 [30 提示词角色](30.prompt-roles-tutorial.md) 的代码化。"),
        ("OutputParser 与 123？", "PydanticOutputParser 对接 [123 JSON Mode](123.structured-output-json-tutorial.md) schema。"),
        ("和 124 tools？", "ChatModel.bind_tools() 声明工具，下篇 LCEL 可 `| model` 接入。"),
        ("生产顾虑？", "依赖体积、抽象泄漏、版本漂移——厚链路用集成测试兜住。"),
        ("Document 从哪来？", "[146 Loader](146.langchain-document-loader-tutorial.md) 预告；本篇用手写 list 即可。"),
        ("Runnable 接口？", "invoke 单条、batch 批量、stream 流式——与 [116 SSE](116.sse-rag-streaming-tutorial.md) 对接 stream。"),
    ])
    extra_lc = """
### 12.1 Runnable 接口详解

```python
class Runnable(Protocol):
    def invoke(self, input, config=None): ...
    def batch(self, inputs, config=None): ...
    def stream(self, input, config=None): ...
```

**config** 可传 `callbacks`（对标路线图 LangSmith）、`tags`、`metadata`——观测篇再展开。

### 12.2 Document 最佳实践

```python
from langchain_core.documents import Document

doc = Document(
    page_content="一线城市住宿每晚不超过500元。",
    metadata={
        "chunk_id": "hb:c02",
        "doc_id": "handbook-v3",
        "section": "差旅",
        "acl_group": "all_staff",
    },
)
```

`page_content` 进 Embedding 与 prompt；`metadata` 进过滤与 [115 导航](115.source-document-navigation-tutorial.md)。

### 12.3 ChatModel 最小调用

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
resp = llm.invoke([HumanMessage(content="你好")])
```

与 [35 OpenAI 兼容](35.openai-compatible-api-tutorial.md) 一致；`base_url` 可指国内网关。

### 12.4 与自研 Pipeline 对照

| 自研 | LangChain 核心 |
|------|----------------|
| dict messages | Message 类型 |
| 函数 retrieve() | Retriever Runnable |
| str template | ChatPromptTemplate |
| json.loads | OutputParser |

### 12.5 D 模块三周路径

Week1：本篇 Document/Runnable/Message；Week2：[126 LCEL](126.langchain-lcel-tutorial.md)；Week3：[127 Retriever](127.langchain-retriever-tutorial.md) 接 [76 Chroma](76.chroma-vector-db-tutorial.md)。

### 12.6 依赖安装

```bash
pip install langchain-core langchain-openai langchain-community
```

版本写在 `requirements.txt`；**langchain-core** 与 **langchain** 主包分离，本篇以 core 为准。

### 12.7 错误：把 chunk 存在 page_content 外的自定义字段

Retriever 默认只返回标准 Document；自定义字段应进 metadata 或包装类。
"""
    return f"""# D 框架与架构（一）：LangChain 核心概念完全指南

> C 模块你把 **解析→分块→向量→检索→生成** 手写跑通了；进入 **D 框架与架构**，第一站是 **LangChain 核心（langchain-core）**：用 **Document、Runnable、Message、OutputParser** 统一「数据载体」与「可组合步骤」。它不是唯一框架，但是 **企业 RAG 岗位出现频率最高** 的抽象层之一。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 模块开篇 · 地基篇**（路线图第 **142** 条），帮你 **读懂官方文档里的名词**，并能 **不依赖 LCEL 先 invoke 通一个 ChatModel**。前置：[30 提示词角色](30.prompt-roles-tutorial.md)、[35 OpenAI 兼容 API](35.openai-compatible-api-tutorial.md)、[51 chunk_id](51.metadata-chunk-id-tutorial.md)。下篇：[126 LCEL](126.langchain-lcel-tutorial.md)、[127 Retriever](127.langchain-retriever-tutorial.md)。

---

## 目录

1. [前言：为什么全栈 RAG 要学框架核心](#1-前言为什么全栈-rag-要学框架核心)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LangChain 核心是什么](#3-langchain-核心是什么)
4. [Document：RAG 的数据原子](#4-documentrag-的数据原子)
5. [Message 与 ChatModel](#5-message-与-chatmodel)
6. [Runnable：可组合的单元](#6-runnable可组合的单元)
7. [OutputParser 与结构化输出](#7-outputparser-与结构化输出)
8. [自研 Pipeline 与框架的边界](#8-自研-pipeline-与框架的边界)
9. [综合实战：Document + ChatModel 最小链](#9-综合实战document--chatmodel-最小链)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：为什么全栈 RAG 要学框架核心

面试常问：「你们 RAG 用框架吗？」答「纯自研」或「LangChain 一把梭」都不够——要能讲 **哪层用框架、哪层自研**（路线图 [152](152.pipeline-vs-framework-tutorial.md)）。**langchain-core** 把 RAG 里反复出现的类型标准化：

- 检索结果不是随意 `dict`，而是 **`Document(page_content, metadata)`**；  
- 调 LLM 不是裸 `requests.post`，而是 **`ChatModel.invoke(messages)`**；  
- 步骤组合留到 [126 LCEL](126.langchain-lcel-tutorial.md)，但 **Runnable 接口** 本篇就要懂。

**读完本文，你应该能做到：**

1. 创建 **Document** 并对齐 chunk 元数据字段。  
2. 用 **HumanMessage/SystemMessage** 调通 ChatModel。  
3. 解释 **Runnable** 的 invoke/stream/batch。  
4. 用 **PydanticOutputParser** 对接 [123 JSON](123.structured-output-json-tutorial.md)。  
5. 说明 **何时只借 core、何时上 LCEL/Retriever**。

### 1.1 D 模块位置

```text
C 模块：RAG 全链路手写 ✓
D 模块开篇
142 LangChain 核心 ← 本篇
143 LCEL
144 Retriever
145 VectorStore ...
```

---

## 2. 本文边界与动手路径

**档位：D 地基篇（路线图 142）。**

**本文讲：** Document、Message、ChatModel、Runnable 接口、OutputParser、与 C 模块概念映射。  
**本文不讲：** LCEL 管道语法（[126](126.langchain-lcel-tutorial.md)）、Retriever 细节（[127](127.langchain-retriever-tutorial.md)）、LangSmith 全配置。

| 步骤 | 验收 |
|------|------|
| A | 画 Document/Runnable 关系 |
| B | pip install langchain-core |
| C | §9 最小 ChatModel |
| D | PydanticOutputParser 解析假 JSON |

---

## 3. LangChain 核心是什么

![LangChain 核心模块](image/langchain-core/01-lc-modules.png)

**langchain-core** 是 **类型与协议层**：与厂商无关的 Document、Runnable、Message、PromptTemplate 基类。集成包（`langchain-openai`、`langchain-chroma`）在 core 之上接具体服务。

### 3.1 与「大 LangChain」包

历史上 `import langchain` 很重；现代项目宜 **显式依赖 core + 集成包**，避免牵一发动全身。

### 3.2 心智模型

```text
数据：Document
对话：Message → ChatModel → AIMessage
组合：Runnable（下篇 LCEL 用 | 连接）
解析：OutputParser → 业务对象
```

---

## 4. Document：RAG 的数据原子

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="入职满一年享受10天年假。",
        metadata={{"chunk_id": "hb-003", "doc_id": "handbook", "page": 12}},
    ),
]
```

与 [51 chunk_id](51.metadata-chunk-id-tutorial.md)、[52 source/page](52.metadata-source-page-tutorial.md) 一致。  
**page_content** 用于 Embedding 与塞进 prompt 的正文；**metadata** 用于过滤、溯源、ACL。

### 4.1 不要做的事

- 把整篇 PDF 塞一个 Document（应 [57-62 分块](57.fixed-size-chunking-tutorial.md)）；  
- metadata 存巨大 JSON（向量库 sidecar 有大小限制）；  
- chunk_id 每次随机（破坏 [49 增量更新](49.incremental-update-tutorial.md)）。

---

## 5. Message 与 ChatModel

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
messages = [
    SystemMessage(content="你是企业知识库助手，仅根据用户提供的资料回答。"),
    HumanMessage(content="【资料】年假10天。【问题】年假几天？"),
]
answer = llm.invoke(messages)
print(answer.content)
```

对应 [30 提示词角色](30.prompt-roles-tutorial.md) 与 [110 RAG Prompt](110.rag-prompt-template-tutorial.md)——下篇用 `ChatPromptTemplate` 模板化。

### 5.1 stream

```python
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
```

对接 [116 SSE](116.sse-rag-streaming-tutorial.md) 时，后端把 `chunk.content` 打成 SSE delta。

---

## 6. Runnable：可组合的单元

**Runnable** 是 LCEL 的基石：ChatModel、Prompt、Retriever、Parser 都实现同一接口。

```python
# 伪代码：下篇才写 prompt | llm
result = runnable.invoke({{"question": "年假？"}})
```

**config** 传 `callbacks` 可做链路追踪（路线图 LangSmith 164）。本篇记住：**一切皆 Runnable，统一 invoke/stream**。

### 6.1 RunnableLambda

```python
from langchain_core.runnables import RunnableLambda

def uppercase(s: str) -> str:
    return s.upper()

r = RunnableLambda(uppercase)
r.invoke("hello")  # "HELLO"
```

业务规则用 Lambda 包一层，**可单测**，别全塞 prompt。

---

## 7. OutputParser 与结构化输出

```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class RagAnswer(BaseModel):
    answer: str
    refusal: bool = False

parser = PydanticOutputParser(pydantic_object=RagAnswer)
format_instructions = parser.get_format_instructions()
# 塞进 system：{{format_instructions}}
# parsed = parser.parse(llm_output)
```

与 [123 JSON Mode](123.structured-output-json-tutorial.md) 双轨：**API schema 优先**；Parser 作兜底或本地模型无 schema 时用。

---

## 8. 自研 Pipeline 与框架的边界

![何时用 LangChain 核心](image/langchain-core/02-vs-handroll.png)

| 用 core | 坚持自研 |
|---------|----------|
| 快速 PoC、团队已标准化 LC | 极强定制、依赖敏感 |
| 要接 LangSmith/Langfuse | 核心链极短且无变化 |
| 与 LC 生态集成（Chroma wrapper） | 面试展示「我懂底层」 |

**推荐**：Mini-RAG **手写一遍**（C 模块），再用 LC **复刻一遍**（D 模块）——对比后才好取舍。

---

## 9. 综合实战：Document + ChatModel 最小链

```python
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

docs = [
    Document(page_content="一线城市住宿每晚不超过500元。", metadata={{"chunk_id": "hb-2"}}),
]
evidence = "\\n".join(f"[{{i+1}}] {{d.page_content}}" for i, d in enumerate(docs))
question = "深圳住宿上限？"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
messages = [
    SystemMessage(content="仅根据资料回答，标注 [n]。"),
    HumanMessage(content=f"【参考资料】\\n{{evidence}}\\n\\n【用户问题】\\n{{question}}"),
]
print(llm.invoke(messages).content)
```

尚未用 Retriever/LCEL——**故意**让你看见 messages 组装本质，与 [110](110.rag-prompt-template-tutorial.md) 一致。

---

## 10. 先错对对：四种典型翻车

{mistakes}

---

## 11. 综合概念地图

![LangChain 核心概念地图](image/langchain-core/03-concept-map.png)

| 概念 | C 模块对应 |
|------|------------|
| Document | chunk 文本+metadata |
| Message | 30 角色 |
| ChatModel | 35 API |
| OutputParser | 123 JSON |

---

## 12. 常见陷阱与 FAQ

{faq}

{extra_lc}

---

## 13. 总结与系列下一步

1. **langchain-core** 定义 RAG 数据与步骤的 **公共类型**。  
2. **Document metadata** 对齐 51/53/52，别临时发明字段。  
3. **Runnable** 是 LCEL 与 Retriever 的接口基础。  
4. **框架是加速器**，不是替代品——底层仍要懂 [76 Chroma](76.chroma-vector-db-tutorial.md)。  
5. 下篇 [126 LCEL](126.langchain-lcel-tutorial.md) 用 `|` 拼链。

### 13.1 系列下一步

| 目标 | 阅读 |
|------|------|
| LCEL 管道 | [126 LangChain LCEL](126.langchain-lcel-tutorial.md) |
| 检索抽象 | [127 LangChain Retriever](127.langchain-retriever-tutorial.md) |
| 结构化 | [123 JSON Mode](123.structured-output-json-tutorial.md) |

### 13.2 面试 30 秒版

「LangChain core 用 Document 表示 chunk，ChatModel 处理 Message 列表，Runnable 统一 invoke/stream。RAG 里 metadata 对齐 chunk_id 和 ACL。PoC 可用框架加速，但应用层权限和评测仍自研。」

{line_expansion("125")}

{deep_dive("125")}

{FOOTER_C6}
"""


def build_126() -> str:
    mistakes = _mistakes_block([
        ("链太长不可读", "十个 | 无注释，改一步崩全线。", "用 RunnableParallel 分子链；命名中间 Runnable；单步单测。"),
        ("dict key 传错", "prompt 要 question 你传 query。", "对照 invoke 输入 schema；类型注解 + 单测。"),
        ("忽略 stream 聚合", "前端收碎片无法展示。", "用 .stream() 或 astream_events；约定 SSE 映射。"),
        ("Retriever 后直接 str()", "拿到 Document 列表对象报错。", "先 RunnableLambda 格式 evidence，或 Prompt 模板接受 docs。"),
    ])
    faq = _faq_block([
        ("LCEL 和 LangGraph？", "LCEL 是有向无环链；复杂 Agent 循环用 LangGraph——超出本篇。"),
        ("异步？", "ainvoke/astream 与 FastAPI 配合；注意 API Key 限流。"),
        ("并行？", "RunnableParallel({{dense: r1, sparse: r2}}) 为 [93 混合](93.hybrid-search-tutorial.md) 打基础。"),
        ("配置注入？", "Runnable.bind() 或 config configurable_fields。"),
        ("和 110 Prompt？", "ChatPromptTemplate.from_messages 固化 system/user 槽位。"),
        ("调试？", "runnable.get_graph().print_ascii() 看链结构。"),
        ("性能？", "batch 调 Embedding；stream 减首字延迟。"),
        ("必须 LCEL 吗？", "可手写 invoke 顺序；LCEL 价值在可读与可观测。"),
    ])
    return f"""# D 框架与架构（二）：LangChain LCEL 完全指南

> [125 篇](125.langchain-core-tutorial.md) 讲清了 **Document、Runnable、Message**；**LCEL（LangChain Expression Language）** 用 **`|` 运算符** 把 Prompt、Retriever、LLM、Parser 串成 **一条可 invoke/stream 的链**——相当于 RAG 的「管道图」写进代码。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 地基篇**（路线图第 **143** 条），带你拼出 **Mini-RAG LCEL 链**，并理解 **RunnableParallel、Lambda、config**。前置：[125 LangChain 核心](125.langchain-core-tutorial.md)、[110 RAG Prompt](110.rag-prompt-template-tutorial.md)。下篇：[127 Retriever](127.langchain-retriever-tutorial.md)。

---

## 目录

1. [前言：管道图写进代码](#1-前言管道图写进代码)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [LCEL 是什么](#3-lcel-是什么)
4. [| 顺序组合与数据流](#4--顺序组合与数据流)
5. [ChatPromptTemplate 与变量](#5-chatprompttemplate-与变量)
6. [RunnableParallel 与 RunnableLambda](#6-runnableparallel-与-runnablelambda)
7. [拼 RAG 链：Retriever → Prompt → LLM](#7-拼-rag-链retriever--prompt--llm)
8. [stream 与 [116 SSE] 对接思路](#8-stream-与-116-sse-对接思路)
9. [综合实战：LCEL Mini-RAG](#9-综合实战lcel-mini-rag)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：管道图写进代码

手写 RAG 常是这样：

```python
chunks = retrieve(q)
messages = build_prompt(q, chunks)
answer = llm(messages)
```

步骤一多，**顺序、分支、流式** 散落各处。LCEL 写成：

```python
chain = rag_inputs | retriever | format_docs | prompt | llm | parser
chain.invoke({{"question": q}})
```

**读完本文，你应该能做到：**

1. 用 **`|`** 连接至少 4 段 Runnable。  
2. 写 **ChatPromptTemplate** 含 system/user 变量。  
3. 用 **RunnableLambda** 把 `list[Document]` 变 evidence 字符串。  
4. **stream** 链并理解 chunk 形态。  
5. 为 [127 Retriever](127.langchain-retriever-tutorial.md) 留好检索插槽。

---

## 2. 本文边界与动手路径

**档位：D 地基篇（路线图 143）。**

| 步骤 | 验收 |
|------|------|
| A | 跑通 prompt \\| llm |
| B | 加 Lambda 格式化 |
| C | §9 接假 Retriever |
| D | stream 打印 token |

---

## 3. LCEL 是什么

![LCEL 管道](image/langchain-lcel/01-lcel-pipe.png)

**LCEL** = Runnable 的 **声明式组合语法**：

- `a | b`：a 的输出作为 b 的输入（若类型不匹配，靠 dict 或 Lambda 适配）；  
- `.invoke()` / `.stream()` / `.batch()` 在 **整条链** 上可用；  
- 与 LangSmith 集成时，链自动带 **run_name**（观测篇再细讲）。

### 3.1 最小例子

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是助手。"),
    ("human", "{{question}}"),
])
llm = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | llm
chain.invoke({{"question": "你好"}})
```

---

## 4. | 顺序组合与数据流

链上传的是 **dict 或 Message**——RAG 常用 dict：

```python
{{"question": "...", "chat_history": []}}
```

每步 Runnable 可 **pick** 自己要的键。Retriever 步通常吃 `question` 吐 `Document[]`；下一步 Lambda 转成 `context` 字符串给 prompt。

```text
{{question}} → Retriever → [Document] → format → {{context}} → Prompt → Messages → LLM
```

---

## 5. ChatPromptTemplate 与变量

```python
from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "仅根据资料回答。资料不足则拒答。"),
    ("human", "【参考资料】\\n{{context}}\\n\\n【用户问题】\\n{{question}}"),
])
```

对齐 [110](110.rag-prompt-template-tutorial.md) 与 [111 注入格式](111.context-injection-format-tutorial.md)。**变量名**与链上游 dict 键一致。

---

## 6. RunnableParallel 与 RunnableLambda

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough

def format_docs(docs):
    return "\\n\\n".join(f"[{{i+1}}] {{d.page_content}}" for i, d in enumerate(docs))

format_step = RunnableLambda(format_docs)

# 并行示例（混合检索预告）
# hybrid = RunnableParallel(dense=dense_retriever, sparse=bm25_retriever)
```

**RunnablePassthrough.assign** 可在链中 **追加键** 而不丢原 dict：

```python
chain = (
    RunnablePassthrough.assign(context=retriever | format_step)
    | rag_prompt
    | llm
)
```

---

## 7. 拼 RAG 链：Retriever → Prompt → LLM

![LCEL 拼 Mini-RAG](image/langchain-lcel/02-rag-chain.png)

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document

# 假 retriever：RunnableLambda 模拟
def fake_retrieve(question: str) -> list[Document]:
    return [Document(page_content="年假10天。", metadata={{"chunk_id": "hb-3"}})]

retriever = RunnableLambda(fake_retrieve)
format_docs = RunnableLambda(lambda docs: "\\n".join(d.page_content for d in docs))

rag_chain = (
    RunnablePassthrough.assign(docs=retriever)
    | RunnablePassthrough.assign(context=lambda x: format_docs.invoke(x["docs"]))
    | rag_prompt
    | llm
)
rag_chain.invoke({{"question": "年假多少天？"}})
```

[127 篇](127.langchain-retriever-tutorial.md) 把 `fake_retrieve` 换成 **VectorStore.as_retriever()**。

---

## 8. stream 与 116 SSE 对接思路

```python
for chunk in rag_chain.stream({{"question": "年假？"}}):
    # chunk 可能是 AIMessageChunk
    if hasattr(chunk, "content"):
        print(chunk.content, end="")
```

后端 FastAPI：把 `content` 包装为 SSE `data:` 行。引用仍建议 **流结束** 再发（[116](116.sse-rag-streaming-tutorial.md)）。

---

## 9. 综合实战：LCEL Mini-RAG

完整脚本结构：

1. `ChatOpenAI` + `ChatPromptTemplate`；  
2. `RunnableLambda` 假检索；  
3. `assign` 组装 context；  
4. `invoke` 与 `stream` 各测一次；  
5. 可选 `| StrOutputParser()` 只要字符串。

验收：答案含「10天」；stream 能逐字打印。

---

## 10. 先错对对：四种典型翻车

{mistakes}

---

## 11. 综合概念地图

![LCEL 概念地图](image/langchain-lcel/03-concept-map.png)

---

## 12. 常见陷阱与 FAQ

{faq}

### 12.1 链的可测试性

对 `format_docs`、`fake_retrieve` 单测；对整条链用 **固定 question** 快照测试，防 prompt 漂移。

### 12.2 与 [123 Parser](123.structured-output-json-tutorial.md)

```python
chain = rag_prompt | llm | parser
```

llm 需开 JSON Mode 或 parser 从文本扒 JSON。

---

## 13. 总结与系列下一步

1. **LCEL = Runnable 的 | 语法**，统一 invoke/stream。  
2. **RAG 链核心**：question → Retriever → format context → prompt → llm。  
3. **Parallel** 为混合检索预留；**Lambda** 写可测胶水。  
4. 下篇 [127 Retriever](127.langchain-retriever-tutorial.md) 替换假检索，接 [76 Chroma](76.chroma-vector-db-tutorial.md)。

### 13.1 面试 30 秒版

「LCEL 用管道符串 Prompt、Retriever、LLM；RunnablePassthrough.assign 传 context；stream 对接 SSE。混合检索可用 RunnableParallel 并行多 Retriever。」

{line_expansion("126")}

{deep_dive("126")}

{FOOTER_C6}
"""


def build_127() -> str:
    mistakes = _mistakes_block([
        ("as_retriever 不设 search_kwargs", "ACL 失效，越权召回。", "search_kwargs={{'filter': {{...}}}} 对齐 [53 ACL](53.metadata-acl-tutorial.md)。"),
        ("把 FAISS 当向量库用却不 persist", "重启索引丢。", "FAISS 自己 save/load；或换 [76 Chroma](76.chroma-vector-db-tutorial.md) PersistentClient。"),
        ("混合检索只拼列表不去重", "同一 chunk 占满 k。", "按 chunk_id 去重，见 [106 去重](106.retrieval-dedup-tutorial.md)。"),
        ("Retriever 返回过多不截断", "撑爆 [28 窗口](28.context-window-tutorial.md)。", "k 与 [98 Top-K](98.top-k-retrieval-tutorial.md)、[107 预算](107.context-budget-tutorial.md) 一致。"),
    ])
    faq = _faq_block([
        ("Retriever 和 VectorStore 区别？", "VectorStore 存与搜；Retriever 是 **面向 LLM 的检索接口** `get_relevant_documents(query)`。"),
        ("怎么接 FAISS？", "langchain_community.vectorstores.FAISS；见 [75 篇](75.faiss-ann-tutorial.md) 理解底层。"),
        ("怎么接 Chroma？", "Chroma vectorstore + as_retriever()；见 [76 篇](76.chroma-vector-db-tutorial.md)。"),
        ("混合检索？", "EnsembleRetriever 或 Parallel + 自写 RRF，对齐 [93 混合检索](93.hybrid-search-tutorial.md)。"),
        ("score_threshold？", "similarity_score_threshold 检索器，对齐 [99 阈值](99.score-threshold-tutorial.md)。"),
        ("Parent Document？", "MultiVectorRetriever / ParentDocumentRetriever，[65 篇](65.parent-document-retriever-tutorial.md)。"),
        ("bind_tools？", "retriever.as_tool() 供 [124 Function Calling](124.function-calling-tool-use-tutorial.md) 使用。"),
        ("自研 Retriever？", "继承 BaseRetriever，实现 `_get_relevant_documents`。"),
    ])
    extra_ret = """
### 12.1 Chroma as_retriever 完整示例

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vs = Chroma(
    collection_name="handbook",
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
)
retriever = vs.as_retriever(
    search_type="similarity",
    search_kwargs={{"k": 5, "filter": {{"acl_group": "all_staff"}}}},
)
docs = retriever.invoke("住宿标准")
```

### 12.2 FAISS 本地示例

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 假设 texts 与 metadatas 已从 JSONL 加载
vs = FAISS.from_texts(texts, OpenAIEmbeddings(), metadatas=metadatas)
retriever = vs.as_retriever(search_kwargs={{"k": 5}})
```

理解 [75 FAISS](75.faiss-ann-tutorial.md) 的 save_local/load_local；metadata 过滤能力弱于 Chroma，宜检索后滤。

### 12.3 混合 Retriever 思路

```python
from langchain_core.runnables import RunnableParallel

# 伪代码：bm25_retriever 与 dense_retriever 各返回 list[Document]
# merged = rrf_merge(dense_docs, sparse_docs)
```

对齐 [93 混合检索](93.hybrid-search-tutorial.md) 与 [94 RRF](94.rrf-fusion-tutorial.md)；精排可选 [96 BGE](96.bge-reranker-tutorial.md) 放在 Retriever **之后** 的 RunnableLambda。

### 12.4 EnsembleRetriever（社区）

```python
from langchain.retrievers import EnsembleRetriever
# bm25_retriever + faiss_retriever, weights=[0.5, 0.5]
```

权重与融合策略应用评测集调；别拍脑袋 0.5/0.5。

### 12.5 接入 LCEL

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def format_docs(docs):
    return "\\n\\n".join(d.page_content for d in docs)

chain = (
    RunnablePassthrough.assign(docs=retriever)
    | RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))
    | prompt
    | llm
)
```

即 [126 LCEL](126.langchain-lcel-tutorial.md) 标准形态。

### 12.6 与 75/76 选型背诵

| 问题 | 倾向 |
|------|------|
| 要快、纯 ANN、自管 id_map | FAISS 75 |
| 要 persist、where 过滤、Mini-RAG | Chroma 76 |
| 要混合 BM25 | 93 + Ensemble |
| 要精排 | Retriever 后接 rerank Lambda |

### 12.7 自研 BaseRetriever

```python
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

class HandbookRetriever(BaseRetriever):
    collection: any

    def _get_relevant_documents(self, query: str, *, run_manager=None):
        # 调内部 hybrid_search
        return docs
```

企业常 **包装已有 hybrid_search()**，而非重写 ANN。

### 12.8 一周实战课

D1 读 75/76；D2 Chroma retriever；D3 FAISS retriever；D4 加 filter；D5 接 LCEL 链 + 10 条金标 Recall。
"""
    return f"""# D 框架与架构（三）：LangChain Retriever 抽象完全指南

> [75 FAISS](75.faiss-ann-tutorial.md) 与 [76 Chroma](76.chroma-vector-db-tutorial.md) 教你 **向量怎么存怎么搜**；[93 混合检索](93.hybrid-search-tutorial.md) 教你 **BM25 与向量怎么融**。**LangChain Retriever** 则在框架层定义统一接口：**字符串 query 进，list[Document] 出**——让 [126 LCEL](126.langchain-lcel-tutorial.md) 的 `|` 管道能 **即插即用** 换检索后端。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **D 主线篇**（路线图第 **144** 条），讲清 **as_retriever、search_kwargs 过滤、FAISS/Chroma 集成、混合 Retriever、与精排衔接**。前置：[75 FAISS](75.faiss-ann-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)、[125 核心](125.langchain-core-tutorial.md)、[126 LCEL](126.langchain-lcel-tutorial.md)。

---

## 目录

1. [前言：检索层统一接口](#1-前言检索层统一接口)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Retriever 是什么](#3-retriever-是什么)
4. [VectorStore.as_retriever](#4-vectorstoreas_retriever)
5. [search_kwargs：k、filter、threshold](#5-search_kwargskfilterthreshold)
6. [混合检索 Retriever 模式](#6-混合检索-retriever-模式)
7. [接 FAISS 与 Chroma 对照](#7-接-faiss-与-chroma-对照)
8. [Retriever 之后：精排与去重](#8-retriever-之后精排与去重)
9. [综合实战：Chroma Retriever + LCEL](#9-综合实战chroma-retriever--lcel)
10. [先错对对：四种典型翻车](#10-先错对对四种典型翻车)
11. [综合概念地图](#11-综合概念地图)
12. [常见陷阱与 FAQ](#12-常见陷阱与-faq)
13. [总结与系列下一步](#13-总结与系列下一步)

---

## 1. 前言：检索层统一接口

C 模块你写过 `def search(q): return chunks`。换 Chroma → FAISS → 自研混合，**LCEL 链的中间段** 总要改。Retriever 抽象把 **「怎么搜」** 封进对象，链上只写 `retriever`。

**读完本文，你应该能做到：**

1. 用 **Chroma/FAISS as_retriever()** 返回 Document。  
2. 配置 **search_kwargs** 的 k 与 metadata filter（ACL）。  
3. 说明 **混合检索** 在 LC 里的两种拼法（Ensemble / Parallel+RRF）。  
4. 把 Retriever 接入 [126 LCEL](126.langchain-lcel-tutorial.md) 链。  
5. 对照 [75][76][93] 讲清 **引擎、向量库、混合** 分工。

### 1.1 路线图位置

```text
75 FAISS / 76 Chroma / 93 Hybrid
144 LangChain Retriever ← 本篇（框架封装）
145 VectorStore 集成（细化）
```

---

## 2. 本文边界与动手路径

**档位：D 主线篇（路线图 144）。**

| 步骤 | 验收 |
|------|------|
| A | invoke retriever 得 Document |
| B | Chroma + filter |
| C | 接 LCEL §9 |
| D | 口述与 75/76 差异 |

---

## 3. Retriever 是什么

![Retriever 抽象](image/langchain-retriever/01-retriever-idea.png)

**核心方法**：`invoke(query: str) -> list[Document]`（或 `get_relevant_documents`）。

**谁实现它**：

- VectorStore.as_retriever()  
- EnsembleRetriever（多路）  
- 自研子类 BaseRetriever  
- `as_tool()` 给 [124 Function Calling](124.function-calling-tool-use-tutorial.md)

### 3.1 不是 Retriever 的东西

- **Cross-Encoder 精排**：[95-96](96.bge-reranker-tutorial.md) 是 Retriever **之后** 的步骤；  
- **Query 改写**：[100-103](100.query-rewriting-tutorial.md) 在 Retriever **之前**。

---

## 4. VectorStore.as_retriever

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={{"k": 5}},
)
docs = retriever.invoke("年假有多少天？")
```

`search_type` 常见：`similarity`、`similarity_score_threshold`、`mmr`（多样性见 [105 MMR](105.mmr-diversity-tutorial.md)）。

---

## 5. search_kwargs：k、filter、threshold

| 参数 | 作用 |
|------|------|
| k | 召回条数，见 [98 Top-K](98.top-k-retrieval-tutorial.md) |
| filter | Chroma where / 元数据，见 [53 ACL](53.metadata-acl-tutorial.md) |
| score_threshold | 见 [99 阈值](99.score-threshold-tutorial.md) |

**企业 RAG**：filter **必须与 API 层 user 权限一致**，不能仅信 prompt。

---

## 6. 混合检索 Retriever 模式

![混合 Retriever 模式](image/langchain-retriever/02-hybrid-retriever.png)

**路径 A**：`EnsembleRetriever([bm25, dense], weights=[...])`  
**路径 B**：`RunnableParallel` 两路 → RunnableLambda `rrf_merge` → 下游

对齐 [93 混合检索](93.hybrid-search-tutorial.md)：BM25 擅关键词，向量擅语义；**RRF** 融合见 [94](94.rrf-fusion-tutorial.md)。

### 6.1 去重

多路合并后按 `metadata["chunk_id"]` 去重，见 [106 检索去重](106.retrieval-dedup-tutorial.md)。

---

## 7. 接 FAISS 与 Chroma 对照

![FAISS vs Chroma Retriever](image/langchain-retriever/03-chroma-faiss.png)

| 维度 | FAISS [75] | Chroma [76] |
|------|------------|-------------|
| 持久化 | save_local | persist_directory |
| 元数据过滤 | 弱，宜后滤 | where filter |
| PoC | 极快 | 很快 |
| 与 LC | FAISS class | Chroma class |

**选型**：要 ACL where → Chroma；要极致轻 ANN → FAISS + 应用层滤。

---

## 8. Retriever 之后：精排与去重

```text
query → (改写) → Retriever(k=50) → dedupe → BGE rerank → top 5 → LCEL prompt
```

Retriever 负责 **宽召回**；[96 BGE-Reranker](96.bge-reranker-tutorial.md) 负责 **窄排序**；[107 预算](107.context-budget-tutorial.md) 负责 **进 prompt 截断**。

---

## 9. 综合实战：Chroma Retriever + LCEL

见 §12.1 与 [126](126.langchain-lcel-tutorial.md) `assign` 模式。验收：带 acl filter 时，无权用户问财务 doc **召不回**。

---

## 10. 先错对对：四种典型翻车

{mistakes}

---

## 11. 综合概念地图

![Retriever 概念地图](image/langchain-retriever/04-concept-map.png)

---

## 12. 常见陷阱与 FAQ

{faq}

{extra_ret}

---

## 13. 总结与系列下一步

1. **Retriever = 检索的统一插头**，LCEL 链核心中段。  
2. **Chroma + filter** 对齐 53 ACL；FAISS 要懂 75 的边界。  
3. **混合检索** 用 Ensemble 或 Parallel+RRF，对齐 93/94。  
4. **精排在 Retriever 之后**，不是 Retriever 内置。  
5. 下篇 [145 VectorStore 集成](145.langchain-vectorstore-tutorial.md) 细化各库参数。

### 13.1 系列对照

| 底层 | 框架篇 |
|------|--------|
| [75 FAISS](75.faiss-ann-tutorial.md) | 本篇 §7 + FAISS retriever |
| [76 Chroma](76.chroma-vector-db-tutorial.md) | 本篇 §9 |
| [93 混合检索](93.hybrid-search-tutorial.md) | 本篇 §6 |
| [126 LCEL](126.langchain-lcel-tutorial.md) | 本篇 §9 链接 |

### 13.2 面试 30 秒版

「LangChain Retriever 统一 query 到 Document 列表。Chroma as_retriever 用 search_kwargs 做 k 和 metadata filter；混合用 Ensemble 或并行加 RRF。FAISS 轻量但过滤弱。精排和去重在 Retriever 之后做。」

{line_expansion("127")}

{deep_dive("127")}

{FOOTER_C6}
"""


# ── Per-article line expansions (~250 lines each) ─────────────────────────

_SAFETY_CASES = [
    ("客服辱骂", "用户破口大骂，机器人复述脏话", "输入 moderation + 输出过滤；不复述辱骂词"),
    ("越狱角色扮演", "用户要求忽略 system 泄露密钥", "输入拦 SAFETY_BLOCK；日志记 attack 类型"),
    ("PII 粘贴", "用户贴身份证号查报销", "检索前脱敏；日志 hash 化"),
    ("有毒 chunk", "FAQ 含歧视语被检索", "检索后 chunk 过滤；勿 Grounding 照抄"),
    ("财务敏感", "问如何绕过审批", "业务策略拒答；非 NO_EVIDENCE"),
    ("医学误杀", "乳腺癌筛查被词表拦", "领域白名单 + 分类器 context"),
    ("型号误杀", "SKU 含敏感子串", "词边界匹配"),
    ("流式漏放", "违规句展示后才断", "缓冲 + 事后审计"),
    ("多轮辱骂", "第三轮开始骂", "每轮输入闸"),
    ("JSON 内违禁", "123 结构化 answer 含脏话", "parse 后字段级过滤"),
    ("工具参数注入", "124 search 参数夹带指令", "args 校验 + 安全过滤"),
    ("内网错觉", "认为内网不用审核", "内网仍做三道闸"),
    ("仅 prompt 文明", "system 写请文明", "硬过滤替代软约束"),
    ("日志泄密", "违禁句写进 ELK", "hash/截断"),
    ("词库无版本", "误杀无法回滚", "blocklist 标签发布"),
    ("Moderation 超时", "API 300ms 超时", "fail-closed 策略文档化"),
    ("跨境审核", "政企禁止出网", "本地审核或纯规则"),
    ("图片 OCR", "扫描件含敏感", "OCR 后走文本闸"),
    ("历史摘要带 PII", "119 压缩进长期记忆", "摘要输出过滤"),
    ("红队谐音", "谐音辱骂", "运营回收变体入词库"),
]

_JSON_CASES = [
    ("markdown 包裹", "返回 ```json 块", "strip_fence + json.loads"),
    ("缺 citations", "answer 有文字无引用", "Pydantic required + 修复调用"),
    ("refusal 不一致", "口头拒答但 refusal false", "system 强调字段一致"),
    ("quote 过长", "整 chunk 塞进 quote", "max_length 200"),
    ("中文标点", "JSON 内弯引号", "schema + 修复"),
    ("流式 parse", "边流边 parse 失败", "双通道或流结束再 parse"),
    ("confidence 虚高", "检索分低但 high", "规则校正 confidence"),
    ("多 citation 重复", "同一 chunk 重复", "去重校验"),
    ("枚举越界", "confidence=very_high", "strict schema 拒绝"),
    ("数组嵌套过深", "citations 套多层", "扁平 schema"),
    ("与 113 对齐", "前端要 [n]", "渲染层映射"),
    ("评测 parse 率", "CI 统计失败", "金标 twenty 条"),
    ("温度高", "JSON 字段漂移", "temperature 0.2"),
    ("修复循环", "无限修复 LLM", "最多一次修复"),
    ("空 answer", "refusal false 但空串", "校验 min_length"),
    ("类型错误", "citations 是字符串", "strict true"),
    ("额外字段", "模型加 note 字段", "additionalProperties false"),
    ("批量批处理", "batch 十条", "batch API 或并发限流"),
    ("版本升级", "schema v2 增字段", "Accept-Schema-Version"),
    ("安全后处理", "answer 辱骂", "122 字段过滤"),
    ("厂商差异", "仅 json_object", "文档化降级策略"),
    ("嵌套 refusal", "refusal 对象嵌套", "扁平 schema"),
    ("数字 confidence", "confidence 用 0.9", "强制枚举"),
    ("citations 空数组", "拒答却 citations 有值", "互斥校验"),
    ("unicode 转义", "\\\\uXXXX 中文", "loads 后正常"),
    ("前后空白", "JSON 前后有说明文字", "strip + 提取首 {{"),
    ("日志合规", "整段 JSON 含 PII", "日志字段白名单"),
    ("前端 Zod", "与 Pydantic 对齐", "共享 schema 定义"),
    ("国际化答案", "answer 英文 citations 中文", "schema lang 字段"),
]

_TOOL_CASES = [
    ("工具过多", "声明十个工具", "保留三到五个"),
    ("描述含糊", "search 没写何时用", "description 写清场景"),
    ("无限循环", "反复 search", "max_iterations=5"),
    ("ACL 缺失", "搜到机密", "where 与 121 一致"),
    ("args 注入", "query 含忽略指令", "122 过滤 args"),
    ("工具异常", "Chroma 超时", "返回 error JSON 给模型"),
    ("并行调用", "同时 search+calc", "无依赖可并行"),
    ("不该调工具", "闲聊也 search", "description 写反例"),
    ("结果过大", "返回百条 chunk", "top_k 上限"),
    ("多跳检索", "对比两年制度", "允许多轮 search"),
    ("与 JSON 终答", "最后一轮 JSON", "bind response_format"),
    ("日志审计", "缺 tool 日志", "记 tool_name/latency"),
    ("成本", "五轮烧 token", "压 iteration"),
    ("本地函数", "calc 工具", "沙箱执行"),
    ("HTTP 工具", "调内部 API", "白名单 host"),
    ("Retriever 工具", "as_tool 包装", "见 127 篇"),
    ("幻觉工具名", "模型调不存在工具", "返回 unknown tool"),
    ("超时", "工具 30s", "超时错误回灌"),
    ("幂等", "重复 search", "缓存 query hash"),
    ("评测", "该调未调", "金标标 expected_tools"),
    ("流式工具", "边生成边调工具", "非流式工具轮常见"),
    ("用户确认", "高危工具要确认", "HITL 门闩"),
    ("缓存检索", "同 query 重复 search", "TTL 缓存 hits"),
    ("doc_id 枚举", "list_docs 再 search", "两工具配合"),
    ("混合在工具内", "search 内 RRF", "对模型透明"),
    ("精排在工具内", "search 返回已 rerank", "控制延迟"),
    ("多租户工具", "tenant_id 参数", "强制传入"),
    ("OpenAPI 生成", "从 OpenAPI 生成 tools", "注意描述质量"),
    ("测试桩", "execute_fn mock", "单测不调真库"),
]

_LC_CORE_CASES = [
    ("metadata 乱", "chunk_id 随机", "对齐 51 稳定 id"),
    ("Document 过大", "整 PDF 一页", "分块后再 Document"),
    ("Message 混", "system 贴资料", "资料放 Human"),
    ("不 stream", "只要 invoke", "产品要流则 stream"),
    ("Parser 裸用", "无 JSON Mode", "双轨 schema+parser"),
    ("版本漂移", "升级链断", "锁版本 CI"),
    ("回调未开", "排障困难", "callbacks 预留"),
    ("类型错", "invoke 传 str 非 dict", "对齐输入 schema"),
    ("Embedding 混", "换模型未重建", "新 collection"),
    ("仅借 Document", "其余自研", "合理混合"),
    ("测试缺", "改 prompt 全崩", "快照测试"),
    ("多语言 metadata", "lang 字段", "过滤用 where"),
    ("page_content 空", "只有 metadata", "跳过入库"),
    ("重复 Document", "同 chunk 两次", "upsert id"),
    ("ChatModel 温度", "回归不稳", "固定 0.2"),
    ("base_url", "国内网关", "环境变量"),
    ("Human 模板", "110 对齐", "system/user 分离"),
    ("RunnableLambda", "业务规则", "单测函数"),
    ("batch embed", "67 批处理", "Embedding 批量"),
    ("与 152 取舍", "全 LC vs 自研", "面试能讲"),
]

_LCEL_CASES = [
    ("键名错", "传 query 非 question", "对照 prompt 变量"),
    ("链太长", "十个管道", "拆子链"),
    ("Retriever 输出", "Document 未 format", "Lambda 转 context"),
    ("Parallel 错", "两路键冲突", "merge 函数"),
    ("stream 碎片", "前端乱码", "聚合 AIMessageChunk"),
    ("assign 丢键", "Passthrough 用法", "保留 question"),
    ("Parser 位置", "parser 在 llm 后", "顺序 prompt|llm|parser"),
    ("异步", "FastAPI 阻塞", "ainvoke"),
    ("图调试", "看不清链", "print_ascii graph"),
    ("假检索", "接真 retriever", "127 替换"),
    ("历史进链", "多轮", "assign chat_history"),
    ("温度绑定", "runnable.bind", "配置注入"),
    ("错误传播", "Retriever 抛错", "try/except Lambda"),
    ("token 估", "28 窗口", "截断 context"),
    ("引用格式", "111 分隔", "format_docs 统一"),
    ("拒答链", "112 模板", "system 写明"),
    ("JSON 链", "123 组合", "response_format"),
    ("工具链", "124 bind_tools", "model 步声明 tools"),
    ("观测", "LangSmith tag", "config tags"),
    ("CI", "链快照", "固定 question 断言"),
]

_RETRIEVER_CASES = [
    ("k 过大", "k=100 撑窗", "k 对齐 98"),
    ("filter 漏", "无 acl", "search_kwargs filter"),
    ("FAISS 无滤", "后处理滤", "或换 Chroma"),
    ("混合未去重", "RRF 前重复", "chunk_id 去重"),
    ("MMR 参数", "lambda 不当", "调 105 篇"),
    ("threshold 过严", "全空", "99 校准"),
    ("Ensemble 权重", "拍脑袋 0.5", "评测调权"),
    ("BM25 未建", "只有向量", "93 补稀疏"),
    ("精排缺失", "噪声进 prompt", "96 后处理"),
    ("Parent 文档", "小搜大读", "65 模式"),
    ("as_tool", "Agent 检索", "124 衔接"),
    ("自研包装", "hybrid_search", "BaseRetriever"),
    ("Chroma 目录错", "空库", "persist 路径"),
    ("Embedding 不一致", "维数错", "重建索引"),
    ("invoke 接口", "统一入口", "勿直接 query"),
    ("回调", "检索耗时", "Retriever 回调"),
    ("多 collection", "路由", "metadata 路由"),
    ("增量", "49 更新", "upsert 后检索"),
    ("评测 Recall", "金标漏召", "调 k/混合"),
    ("LCEL 插入", "assign docs", "126 链"),
]

EXPANSION_BLOCKS = {
    "122": _case_bank("内容安全", list(_SAFETY_CASES)),
    "123": _case_bank("结构化 JSON", list(_JSON_CASES)),
    "124": _case_bank("Function Calling", list(_TOOL_CASES)),
    "125": _case_bank("LangChain 核心", list(_LC_CORE_CASES)),
    "126": _case_bank("LangChain LCEL", list(_LCEL_CASES)),
    "127": _case_bank("LangChain Retriever", list(_RETRIEVER_CASES)),
}

DEEP_DIVE_BLOCKS = {
    "123": """
## 附录 H：JSON Mode 生产落地深度指南

### H.1 前后端契约一份 schema 管到底

团队常见事故是：后端 Pydantic 模型已加 `confidence` 字段，前端 TypeScript 接口没更新，上线后 `undefined` 导致引用卡片空白。做法是 **OpenAPI 或 JSON Schema 单源**：从同一 schema 生成 Python 校验与 TS 类型。RAG 答案若要走 [115 源文档导航](115.source-document-navigation-tutorial.md)，`citations[].chunk_id` 必须在入库时与 [51 chunk_id](51.metadata-chunk-id-tutorial.md) 一致，否则 JSON 再漂亮也无法跳转。

### H.2 金标评测如何存期望 JSON

每条金标除 `question`、`expected_answer` 外，增加 `expected_citation_ids: string[]` 与 `allow_refusal: bool`。跑批时对比：parse 成功率、字段精确匹配、引用集合 F1。若模型 `refusal=true` 但金标不允许拒答，单独记为 **召回失败** 而非 parse 失败——归因别搞混。与路线图 E 轨 RAGAS Faithfulness 衔接时，结构化输出让 **自动对齐引用** 更容易脚本化。

### H.3 流式与 JSON 的产品折中

[116 SSE](116.sse-rag-streaming-tutorial.md) 用户要看打字机，后台又要 JSON：实践里常用 **双通道**——SSE 推 `answer` 的纯文本 delta（或 Markdown），并行或结束后另一请求拿完整 JSON 填 citations。若厂商支持 structured streaming，要测 **半截 JSON** 时前端不闪崩。无论哪条路，[122 内容安全](122.content-safety-filter-tutorial.md) 对最终展示字符串仍要过滤。

### H.4 Schema 演进与向后兼容

加字段用 **可选 + 默认值**；删字段先 **废弃两个版本**。在 JSON 根加 `schema_version: 2`，旧客户端读 v1 子集。与 [48 文档版本](48.doc-versioning-tutorial.md) 类似：知识库升级不等于 schema 升级，但要一起写在发布说明里。

### H.5 本地模型无 json_schema 时的工程套路

开源模型常靠 Prompt + **Outlines** / **grammar constraint** / 多次重试。接受更高 parse 失败率时，要有 **降级纯文本 + 人工标注队列**。不要把「parse 失败」 silently 当成拒答——日志里要有 `PARSE_ERROR` 与原始 raw 片段（注意脱敏）。

### H.6 与 [110 Prompt](110.rag-prompt-template-tutorial.md) 的字段说明放哪

**字段语义、拒答条件、引用规则** 放 system；**具体资料** 放 user（[111 注入格式](111.context-injection-format-tutorial.md)）。切忌在 system 里塞当晚的 chunk 原文——否则换题不换 system 的错觉会让回归测试失效。

### H.7 安全、越权在 JSON 层的表达

`refusal_code` 建议枚举：`NO_EVIDENCE`、`FORBIDDEN`、`SAFETY_BLOCK`，与 [112][121][122] 一一对应。不要在 `answer` 里写「根据资料第 3 条」而 `citations` 为空——这是 **假引用**，评测与合规都要抓。

### H.8 成本与 token

长 schema 与 one-shot 示例吃输入 token（[27 计费](27.token-counting-billing-tutorial.md)）。可把 schema 摘要放 system，完整 schema 走 API `response_format` 而不重复打印在 prompt 里。

### H.9 一周强化练习

周一写 Pydantic 模型；周二接 API strict schema；周三接假检索 CHUNKS；周四接 [110] 模板；周五十条金标 + parse 率报表。能独立完成即达到本篇「地基」验收。
""",
    "124": """
## 附录 H：Function Calling 与 RAG 工具化深度指南

### H.1 何时用固定 RAG 链、何时上 Tool

资料量小、单次检索够答——[126 LCEL](126.langchain-lcel-tutorial.md) 固定链更简单。需要 **选库、多跳、先算再搜、用户要「查一下再对比制度 A/B」** 时，Tool 让模型决定 **何时检索**。别为了「显得 Agent」强行 Tool——每次多一到三轮 LLM 调用，成本和延迟都上去。

### H.2 search_kb 工具内部应做什么

对齐 [76 Chroma](76.chroma-vector-db-tutorial.md)：`collection.query` + `where` ACL（[121](121.unauthorized-doc-filter-tutorial.md)、[53](53.metadata-acl-tutorial.md)）。返回给模型的 tool_result 要 **短**：chunk_id、一句摘要、关键句摘录，别把整个 parent 文档塞回去（[65 父文档](65.parent-document-retriever-tutorial.md) 可单独 `get_chunk` 工具）。可走 [93 混合](93.hybrid-search-tutorial.md) + [96 精排](96.bge-reranker-tutorial.md)，对模型透明。

### H.3 max_iterations 与停止条件

除次数上限，加 **无新 chunk_id**、**连续两轮同 query** 则停止并拒答。日志记 `iteration`、`tool_name`、`args_hash`，方便和 [124] bad case 对齐。与 [122 安全](122.content-safety-filter-tutorial.md) 结合：tool 的字符串参数也要过滤，防注入型 `query` 绕过检索闸。

### H.4 与 [123 JSON](123.structured-output-json-tutorial.md) 组合

最终答案仍可要求 JSON：`answer` + `citations`；中间 tool 回合用 messages 里的 `tool` 角色。别让模型在 tool_result 里再编 JSON 套娃——结构分层要清晰。

### H.5 bind_tools 与 LangChain（预告 125～127）

`ChatModel.bind_tools([search_kb, ...])` 后，LCEL 里 `prompt | model` 即可出 `tool_calls`。[127 Retriever](127.langchain-retriever-tutorial.md) 的 `as_tool()` 把检索器直接变成工具声明，减少手写 schema。

### H.6 错误与超时

工具内部异常捕获，返回 `{"error": "检索超时，请缩小问题范围"}` 给模型，**不要把 Python traceback 给用户**。外部 API 工具要设 **超时 + 熔断**，避免 Agent 卡死。

### H.7 评测工具决策

金标除答案外，标 **期望是否调用 search_kb**、**期望 chunk_id**。抽检「该搜未搜」「不该搜乱搜」。与固定 RAG 比 Recall 时，要 **同 token 预算** 才公平。

### H.8 面试常问：Tool 和 MCP？

MCP 是 **工具协议与生态**；Function Calling 是 **模型输出形状**。RAG 服务可先内置 `search_kb`，再逐步接 MCP 统一工具注册——本篇先把 **单会话循环** 跑稳。

### H.9 红队：恶意工具参数

`doc_id=*`、超长 query、SQL 型注入——在工具入口用 **白名单 + 长度限制 + ACL**。与越权测试矩阵合并进 CI。
""",
    "125": """
## 附录 H：LangChain 核心概念深度指南

### H.1 D 模块开篇：先地图后语法

C 模块你手写 ingest→retrieve→generate；D 模块用 **同一套类型** 把步骤包起来。本篇故意 **不先上 LCEL 管道符**，让你看见 messages 是怎么组出来的——与 [110 Prompt](110.rag-prompt-template-tutorial.md) 一一对应。读懂本篇再开 [126 LCEL](126.langchain-lcel-tutorial.md)，否则 `|` 只是魔术。

### H.2 Document 是企业 metadata 的落点

`page_content` 对应 chunk 正文；`metadata` 对齐 [50 doc_id](50.metadata-doc-id-tutorial.md)、[51 chunk_id](51.metadata-chunk-id-tutorial.md)、[52 溯源](52.metadata-source-page-tutorial.md)、[53 ACL](53.metadata-acl-tutorial.md)。Loader（路线图 146）只是把文件变成 `list[Document]`——**字段规范** 要在团队 wiki 写死，别每个 Loader 一套键名。

### H.3 Runnable 是三态接口

`invoke` 适合 API 单次问答；`batch` 适合离线评测；`stream` 对接 [116 SSE](116.sse-rag-streaming-tutorial.md)。升级 `langchain-core` 大版本时，用 **最小链 CI** 跑三条金标，防 `stream` 事件形状变化。

### H.4 ChatModel 与 [35 API](35.openai-compatible-api-tutorial.md)

`ChatOpenAI` 等是 Runnable；`invoke([HumanMessage(...)])` 底层仍是 chat completions。换国内网关改 `base_url` + `model`，Document 与链结构 **不用改**。

### H.5 OutputParser 与 [123 JSON](123.structured-output-json-tutorial.md)

`PydanticOutputParser` 生成 format instructions 塞进 prompt；更推荐 API 层 `json_schema` + 同一 Pydantic 模型校验——Parser 做 **兜底修复** 即可。

### H.6 自研 vs 框架（152 预告）

只借 **Document + 类型** 是最常见「混合」；全链 LCEL 适合 PoC 和中小团队；强定制核心检索与权限时 **自研检索 + LC 生成** 很常见。框架不是信仰，是 **工时与风险的 tradeoff**。

### H.7 版本与依赖

`langchain-core` 与 `langchain-openai`、`langchain-chroma` **分开锁版本**。README 写清「本项目 LC 栈版本矩阵」。patch 升级也要跑 §9 最小链。

### H.8 从 Mini-RAG 迁移 checklist

1. 手写 chunks → `list[Document]`  
2. 手写 messages → `ChatPromptTemplate`（126）  
3. 手写 search → `as_retriever()`（127）  
4. 保留自研 ACL 在 retriever filter 内  

### H.9 培训路径

2 天：本篇 + 126 最小 LCEL RAG；第 3 天接 127 Chroma retriever；第 4 天对照 [75][76] 讲清 **引擎/库/框架** 三层。
""",
    "126": """
## 附录 H：LangChain LCEL 深度指南

### H.1 LCEL 是什么：Runnable 的组合语法

`runnable_a | runnable_b` 表示输出接入输入；`RunnableParallel` 并行多路（如 [93 混合](93.hybrid-search-tutorial.md) 两路检索）；`RunnableLambda` 塞 Python 函数做 **可单测** 的业务逻辑。与 [125 核心](125.langchain-core-tutorial.md) 的 Runnable 接口一体——LCEL 只是 **声明式拼装**。

### H.2 标准 RAG LCEL 链拆解

```text
{"question": q}
  → assign(context=retriever | format_docs)
  → prompt
  → llm
  → StrOutputParser() 或 PydanticOutputParser
```

`format_docs` 应对齐 [111 上下文注入](111.context-injection-format-tutorial.md)。`retriever` 来自 [127](127.langchain-retriever-tutorial.md)。`prompt` 来自 [110](110.rag-prompt-template-tutorial.md) 的 `ChatPromptTemplate`。

### H.3 stream 与 [116 SSE](116.sse-rag-streaming-tutorial.md)

`chain.stream({"question": q})` 产出事件流；你要在 FastAPI 里 **映射成 SSE**。注意：若链中含 Retriever，首 token 延迟 = 检索 + 首包生成。引用若走 JSON，见 [123](123.structured-output-json-tutorial.md) 双通道策略。

### H.4 RunnableParallel 做混合检索

```python
from langchain_core.runnables import RunnableParallel

hybrid = RunnableParallel(
    bm25=bm25_retriever,
    dense=dense_retriever,
)
# 后接 RunnableLambda(rrf_merge)
```

对齐 [94 RRF](94.rrf-fusion-tutorial.md)；别并行后忘记 **chunk_id 去重**（[106 去重](106.retrieval-dedup-tutorial.md)）。

### H.5 配置与可观测

`chain.invoke(input, config={"tags": ["prod"], "metadata": {"kb": "handbook"}})` 便于 LangSmith（路线图 164）过滤 trace。把 `prompt_version` 放进 metadata。

### H.6 多轮与 assign

`RunnableWithMessageHistory` 或手动 `assign(chat_history=...)` 接 [118 多轮](118.multi-turn-history-tutorial.md)。**每轮 question 仍应触发 retriever**，别把旧 chunk 绑死在 history 里。

### H.7 常见调试

`print(chain.get_graph().draw_ascii())` 看步骤；某步输出 `print` 用 `RunnableLambda` 包一层仅 dev 开启。链太长时拆 **子链** 单测。

### H.8 与 Function Calling

`prompt | model.bind_tools(tools)` 后，要处理 `AIMessage.tool_calls`——常另写 **agent 循环**（124），不是单条 `|` 能收束。别和简单 RAG 链混在一个文件里不注释。

### H.9 性能

`batch` 评测金标；生产 `invoke` 单条。Retriever 与 LLM 可 **异步**（`ainvoke`）——全栈篇再展开，PoC 同步即可。

### H.10 验收标准

能用 LCEL 拼出：**检索 → 格式化资料 → prompt → llm → 字符串答案**，并 `stream` 打印；k 与 filter 来自 [127](127.langchain-retriever-tutorial.md) 的 `search_kwargs`。
""",
    "127": """
## 附录 H：LangChain Retriever 深度指南

### H.1 为什么要有 Retriever 抽象

[75 FAISS](75.faiss-ann-tutorial.md) 给你 `index.search`；[76 Chroma](76.chroma-vector-db-tutorial.md) 给你 `collection.query`。LCEL 链中间需要 **统一签名**：`str → list[Document]`。换库只换 retriever 构造，**prompt 与 llm 段不动**——这是 D 模块主线价值。

### H.2 as_retriever 与 search_kwargs

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4, "filter": {"acl_group": "all_staff"}},
)
```

`filter` 对齐 [53 ACL](53.metadata-acl-tutorial.md) 与 [121 越权](121.unauthorized-doc-filter-tutorial.md)。Chroma 的 where 能力强；FAISS 常 **检索后滤** 或换库——理解 [75] 边界再选型。

### H.3 混合检索在 LC 里的两种拼法

**EnsembleRetriever**：多 retriever + 权重，接近 [93 混合](93.hybrid-search-tutorial.md)。**Parallel + RunnableLambda(RRF)**：更透明，便于自定义 [94 RRF](94.rrf-fusion-tutorial.md)。无论哪种，**宽召回 k 大、进 prompt k 小**（[98 Top-K](98.top-k-retrieval-tutorial.md)）。

### H.4 精排不在 Retriever 里

[95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)、[96 BGE-Reranker](96.bge-reranker-tutorial.md) 放在 `retriever | rerank_lambda | format_docs` 的 **rerank_lambda**。Retriever 只负责 **召回**，别指望一个类包办全链路。

### H.5 Parent Document Retriever

小 chunk 搜、大 parent 读——[65 篇](65.parent-document-retriever-tutorial.md) 有专门模式；LC 有对应集成。别把所有 parent 正文塞进 retriever 返回值，撑爆 [28 窗口](28.context-window-tutorial.md)。

### H.6 as_tool() 与 [124](124.function-calling-tool-use-tutorial.md)

`retriever.as_tool(name="search_kb", description="...")` 让 Agent 循环调检索。description 要写清 **何时调用、参数含义**，否则模型乱调。

### H.7 自研 BaseRetriever

继承 `BaseRetriever`，实现 `_get_relevant_documents`：内部可调用你们的 hybrid_search 函数（对齐 93）。**测试** 用固定 query 断言 Document 列表与 metadata。

### H.8 与 C4 向量库对照表

| 能力 | FAISS | Chroma | LC Retriever |
|------|-------|--------|--------------|
| 持久化 | save_local | persist_directory | 封装在 vectorstore |
| 元数据过滤 | 弱 | where 强 | search_kwargs.filter |
| 混合 | 自拼 | 自拼 | Ensemble |

### H.9 评测 Recall

金标标 `relevant_chunk_ids`；扫 k=1,3,5,10 画曲线。换 retriever 实现后 **同一金标回归**，与 [91 Dense](91.dense-retrieval-tutorial.md)、[92 Sparse](92.sparse-retrieval-rag-tutorial.md) 实验报告放同一目录。

### H.10 上线 checklist

collection 名、Embedding 模型、filter 字段与生产 ACL 一致；`invoke` 日志打 `chunk_ids`；与 [110][111][112] 生成段联调；红队测越权 doc 不进结果集。

### H.11 下一步 145 VectorStore

本篇讲 **Retriever 接口**；下篇 VectorStore 集成细讲各库 `from_documents`、`add_texts` 参数——入库与查询分工更清晰。
""",
}


ARTICLE_BUILDERS: dict[str, callable] = {
    "122.content-safety-filter-tutorial.md": build_122,
    "123.structured-output-json-tutorial.md": build_123,
    "124.function-calling-tool-use-tutorial.md": build_124,
    "125.langchain-core-tutorial.md": build_125,
    "126.langchain-lcel-tutorial.md": build_126,
    "127.langchain-retriever-tutorial.md": build_127,
}
