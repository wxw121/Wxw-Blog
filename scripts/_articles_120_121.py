# -*- coding: utf-8 -*-
"""Article bodies 120 and 121 for _gen_119_121.py"""

ARTICLE_120 = r'''# C6 生成与 Grounding（十一）：指代消解 Coreference Resolution 完全指南

> 用户第三轮只说：「**它** 和去年修订版比有什么变化？」——向量检索若把「它」当字面词，会召回 **IT 部门**、**它国政策** 等噪声。[120 指代消解](120.coreference-resolution-tutorial.md) 在 **会话级检索** 前，把 **「它」「那个政策」「前者」** 绑回 **具体实体**，生成 **可独立检索的 standalone query**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 了解篇**（路线图第 **137** 条），讲清 **规则、LLM 改写、与 [118 多轮历史](118.multi-turn-history-tutorial.md)、[109 会话增强](109.conversation-query-enhancement-tutorial.md)、[100 Query Rewriting](100.query-rewriting-tutorial.md) 的分工**。前置：[118 多轮历史](118.multi-turn-history-tutorial.md)、[109 会话查询增强](109.conversation-query-enhancement-tutorial.md)、[100 Query Rewriting](100.query-rewriting-tutorial.md)、[119 Summary Memory](119.summary-memory-tutorial.md)。

---

## 目录

1. [前言：「它」是检索杀手](#1-前言它是检索杀手)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [指代消解是什么](#3-指代消解是什么)
4. [会话级 vs 文档级指代](#4-会话级-vs-文档级指代)
5. [典型指代表与中文难点](#5-典型指代表与中文难点)
6. [三种实现路径：规则、检索增强、LLM](#6-三种实现路径规则检索增强llm)
7. [与 Query Rewriting、会话增强的关系](#7-与-query-rewriting会话增强的关系)
8. [Pipeline 位置：在 embed 之前](#8-pipeline-位置在-embed-之前)
9. [综合实战：指代展开 Mini-RAG](#9-综合实战指代展开-mini-rag)
10. [先错对对：五种典型翻车](#10-先错对对五种典型翻车)
11. [评测集与 bad case](#11-评测集与-bad-case)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：「它」是检索杀手

单轮问答里，用户问「差旅住宿一线城市上限」——检索简单。  
多轮里：

| 轮次 | 用户说 | 若不消解 |
|------|--------|----------|
| 1 | 介绍一下新的差旅政策 | 正常 |
| 2 | 一线住宿多少？ | 正常 |
| 3 | **它** 和旧版比改了什么？ | 搜「它」→ 噪声 |
| 4 | **那个** 审批流程呢？ | 缺实体 → 空召回 |

**Coreference Resolution**（指代消解）：在文本中找出 **代词/指示词** 所指的 **先行实体（antecedent）**，恢复 **完整语义**。  
通俗说：把「它」翻译回 **「2024 差旅住宿标准」** 再拿去搜。

**Session-level retrieval**（会话级检索）：检索 query 的构造 **依赖当前 session 上下文**，不是只看最后一句 user。  
**Standalone query**（独立查询）：脱离对话历史仍能 **自解释** 的检索句，例如「2024 差旅政策与 2023 版差异」。

**读完本文，你应该能做到：**

1. 区分 **会话指代** 与 **文档内指代**（本篇聚焦前者）。  
2. 画出 **指代消解在 RAG 链路** 的位置（检索前、embed 前）。  
3. 实现 §9 **规则 + LLM 可选** 的 query 展开。  
4. 说明与 [100 Rewriting](100.query-rewriting-tutorial.md)、[109 增强](109.conversation-query-enhancement-tutorial.md) **不重复** 的分工。  
5. 构建 **10+ 条中文指代金标** 做回归。  
6. 识别 §10 五种翻车。

### 1.1 C6 轨位置

```text
118 多轮历史
119 Summary Memory（压体积）
137 指代消解 ← 本篇（了解）
138 越权文档过滤
```

**学习顺序**：先 [118](118.multi-turn-history-tutorial.md) 与 [119](119.summary-memory-tutorial.md)，再本篇——摘要保留 entities，消解 **消费 entities**。

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 指代 | Coreference | 代词指向哪个实体 |
| 先行词 | Antecedent | 被指的对象 |
| 零指代 | Zero anaphora | 中文省略主语 |
| 展开 query | Query expansion / resolution | 替换成实体后再检索 |
| 会话级 | Session-level | 依赖对话上下文 |

---

## 2. 本文边界与动手路径

**档位：C6 了解篇（路线图 137）。**

**本文讲：** 会话指代直觉、中文现象、规则与 LLM 展开、pipeline 位置、Mini-RAG、FAQ。  
**本文不讲：** 文档级共指标注、SpanBERT 训练、完整 OntoNotes 评测、跨语言指代 SOTA 论文推导。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 读 §3～§5，列 10 个中文指代词 | 表可默写 |
| B | 读 §7 分工表 | 不与 100/109 混 |
| C | 跑 §9 | 「它」→ 实体 query |
| D | 写 5 条金标 | 回归 JSON |
| E | §10 先错对对 | 五种错 |

**环境：** Python 3.10+；§9 无 API；LLM 路径需 [35 OpenAI 兼容](35.openai-compatible-api-tutorial.md)。

### 2.2 沿用前文

| 概念 | 来自 |
|------|------|
| 多轮 messages | [118 多轮历史](118.multi-turn-history-tutorial.md) |
| 历史压缩 | [119 Summary Memory](119.summary-memory-tutorial.md) |
| 查询改写 | [100 Query Rewriting](100.query-rewriting-tutorial.md) |
| 会话 query 增强 | [109 会话增强](109.conversation-query-enhancement-tutorial.md) |
| Multi-Query | [101 Multi-Query](101.multi-query-retrieval-tutorial.md) |

---

## 3. 指代消解是什么

读下图：指代消解模块 **只改检索 query**，不改向量库。

![指代消解在检索前](image/coreference-resolution/01-coref-idea.png)

```text
用户本轮：「那个政策审批要几天？」
     ↓
[119 摘要] + [最近轮] → 候选实体：{2024差旅政策, 住宿标准, 审批流程}
     ↓
指代消解：「那个政策」→ 2024差旅政策（最近讨论主题）
     ↓
standalone query：「2024差旅政策 审批流程 需要几天」
     ↓
embed → 向量检索
```

**关键**：消解目标是 **检索用的 query 字符串**，不是替用户重写礼貌用语。

### 3.1 为何向量检索对指代特别敏感

Embedding 对 **短句 + 代词** 的语义 **不完整**——「它改了什么」与「差旅政策改了什么」在向量空间 **距离可能很远**。  
因此 **必须在 embed 前** 展开（§8）。

### 3.2 与摘要 memory 的配合

[119 篇](119.summary-memory-tutorial.md) 的 `entities` 与 `confirmed_facts` 是消解的 **候选池**；最近一轮 assistant 提到的 **文档名/政策名** 优先级最高。

---

## 4. 会话级 vs 文档级指代

| 类型 | 例子 | 本篇 |
|------|------|------|
| 会话级 | 「它」指上一轮说的政策 | ✓ 重点 |
| 文档级 | 手册内「该条款」指 §3.2 | 分块时可保留标题前缀 |
| 跨文档 | 「如上文所述」 | 靠 metadata 与 parent chunk |

企业 RAG **bad case 的大头** 是会话级——用户 **越聊越短**，代词越来越多。

---

## 5. 典型指代表与中文难点

| 指代形式 | 例子 | 消解线索 |
|----------|------|----------|
| 人称代词 | 它、他们 | 最近中性/复数实体 |
| 指示词 | 这个、那个、前者 | 距离 + 话题延续 |
| 名词省略 | 「审批呢？」 | 继承上轮主题 |
| 定语省略 | 「二线呢？」 | 继承「住宿上限」框架 |

**中文零指代**：「能不能再高一点？」——缺主语，需继承 **「住宿上限」**。  
规则：若本轮 **无名词** 且 **含比较/疑问词**，从 **摘要 open_questions 或上轮 assistant 关键词** 补全。

读下图：候选实体评分。

![候选实体评分](image/coreference-resolution/02-entity-scoring.png)

**评分因子（启发式）**：

1. **Recency**——越近提到的实体分越高；  
2. **Role**——用户明确询问的对象 > 背景提及；  
3. **Type match**——「政策」类指代优先匹配含「政策」「制度」的实体；  
4. **Salience in summary**——[119](119.summary-memory-tutorial.md) 的 `user_goal` 加权。

---

## 6. 三种实现路径：规则、检索增强、LLM

| 路径 | 做法 | 适用 |
|------|------|------|
| 规则 | 代词表 + 最近实体栈 | PoC、延迟敏感 |
| 检索增强 | 用上一轮实体 **再搜一次** 验证 | 中等 |
| LLM | 给定 history 输出 standalone query | 复杂指代 |

**PoC 推荐**：规则栈 + **可选 LLM 兜底**（仅当检测到指代词且规则置信度低）。

### 6.1 LLM 展开 Prompt（与 100 篇区别）

[100 Query Rewriting](100.query-rewriting-tutorial.md) 偏 **同义扩展、纠错**；本篇 prompt **强制替换指代**：

```text
根据对话，将「本轮用户问题」改写为可独立检索的一句话。
要求：
1. 将所有代词、指示词替换为具体实体名称。
2. 不要回答问题，只输出改写后的问题。
3. 保留用户意图，不添加新事实。

对话摘要：
{summary}

最近对话：
{recent}

本轮用户问题：
{query}

独立检索问题：
```

---

## 7. 与 Query Rewriting、会话增强的关系

| 模块 | 输入 | 输出 | 目的 |
|------|------|------|------|
| 指代消解（本篇） | 含「它」的短句 | 实体显式 query | 消除代词 |
| [100 Rewriting](100.query-rewriting-tutorial.md) | 完整问句 | 扩展/纠错 query | 提升召回 |
| [109 增强](109.conversation-query-enhancement-tutorial.md) | history + query | 上下文化 query | 会话意图 |

**推荐串联**：

```text
user_query → 指代消解 → Query Rewriting（可选）→ embed → 检索
```

**不要** 三个 LLM 串三次——延迟爆炸。可 **合并为一个 prompt**（109 已含部分能力），但 **评测时要能 ablation** 指代项。

---

## 8. Pipeline 位置：在 embed 之前

```text
❌ query → embed → 检索 → 用 LLM 看结果再猜指代
✓  history + query → 指代消解 → standalone query → embed → 检索
```

读下图：错误 vs 正确 pipeline。

![Pipeline 位置](image/coreference-resolution/03-pipeline-position.png)

**与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md)**：消解后可 **生成 2～3 个实体变体** 做多路检索，再 RRF 融合——适合「它」对应 **多个可能实体** 时。

---

## 9. 综合实战：指代展开 Mini-RAG

```python
"""coref_resolve_demo.py — 规则指代展开 + 假检索 query"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

PRONOUNS = re.compile(r"(它|他们|这个|那个|前者|后者|该政策|这份)")
COMPARATIVE = re.compile(r"(呢|吗|多少|怎么|什么|哪)")


@dataclass
class DialogState:
    entity_stack: list[str] = field(default_factory=list)
    summary_entities: list[str] = field(default_factory=list)
    last_topic: str = ""

    def push_entity(self, text: str) -> None:
        for kw in ("差旅政策", "住宿标准", "审批流程", "报销制度", "员工手册"):
            if kw in text:
                if kw not in self.entity_stack:
                    self.entity_stack.insert(0, kw)
                self.last_topic = kw


def detect_coref(query: str) -> bool:
    if PRONOUNS.search(query):
        return True
    if len(query) < 12 and COMPARATIVE.search(query):
        return True
    return False


def resolve_query(query: str, state: DialogState) -> tuple[str, float]:
    """返回 (standalone_query, confidence)"""
    if not detect_coref(query):
        return query, 1.0
    candidates = state.entity_stack + state.summary_entities
    if not candidates:
        return query, 0.2
    antecedent = candidates[0]
    q = query
    for p in ("它", "这个", "那个", "该政策", "这份"):
        q = q.replace(p, antecedent)
    if q == query and state.last_topic:
        q = f"{state.last_topic} {query}"
    return q, 0.85 if q != query else 0.4


def simulate_turns():
    state = DialogState(summary_entities=["2024差旅政策"])
    turns = [
        ("user", "介绍一下新的差旅政策"),
        ("assistant", "2024差旅政策已更新，涵盖住宿与餐饮。"),
        ("user", "一线住宿多少？"),
        ("assistant", "一线城市住宿上限500元每晚。"),
        ("user", "它和旧版比改了什么？"),
        ("user", "那个审批流程呢？"),
        ("user", "二线呢？"),
    ]
    for role, text in turns:
        if role == "assistant":
            state.push_entity(text)
        if role == "user":
            sq, conf = resolve_query(text, state)
            print(f"原始: {text}")
            print(f"展开: {sq} (conf={conf})")
            print("---")


if __name__ == "__main__":
    simulate_turns()
```

预期输出要点：

- 「它和旧版…」→ 「**2024差旅政策** 和旧版…」  
- 「那个审批流程」→ 「**2024差旅政策** 审批流程」或栈顶 **审批流程**（按 recency 调参）  
- 「二线呢？」→ 「**住宿标准** 二线呢？」类补全

### 9.1 低置信度走 LLM

```python
def build_retrieval_query(user_query: str, state: DialogState, llm=None) -> str:
    sq, conf = resolve_query(user_query, state)
    if conf >= 0.7 or llm is None:
        return sq
    # 调用 §6.1 prompt
    return llm_expand(user_query, state, llm)
```

### 9.2 与 Chroma 检索衔接

展开后的 `standalone_query` 传入 [76 Chroma](76.chroma-vector-db-tutorial.md) 的 `query_texts`——**不要** 把未消解的「它」 embed。

---

## 10. 先错对对：五种典型翻车

### 10.1 错：检索时不看 history，只 embed 最后一句

**对**：§8——**指代消解在 embed 前**。

### 10.2 错：把「它」替换成 **错误实体**（IT 部 vs 政策）

**对**：实体栈 + 摘要 + **类型匹配**；低置信 **Multi-Query 多实体** 或 **澄清问用户**。

### 10.3 错：指代消解与 Query Rewriting 混成一个黑盒，无法评测

**对**：**分模块日志** `raw_query / resolved_query / rewritten_query`。

### 10.4 错：对 **无指代** 的完整句也强行 LLM 改写

**对**：`detect_coref` 为 false 时 **直通**，省延迟与改写漂移。

### 10.5 错：消解后不再 [119 摘要] 更新 entities

**对**：展开用的实体应 **回写 summary.entities** 供下轮使用。

---

## 11. 评测集与 bad case

**金标 JSONL 字段**：

```json
{"history": [...], "query": "它和旧版比呢？", "resolved": "2024差旅政策与2023版差异", "notes": "它→政策"}
```

**指标**：

| 指标 | 定义 |
|------|------|
| Resolution Acc | 展开句是否含正确实体 |
| Recall@5 变化 | 消解前后检索命中 |
| 澄清率 | 低置信转问用户的比例 |

**常见 bad case**：用户 **切换话题** 后仍用「那个」——需检测 **topic shift**（与上轮 embedding 相似度低于阈值则 **清空 entity_stack**）。

---

## 12. 综合概念地图

![指代消解概念速记](image/coreference-resolution/04-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| 会话指代 | 代词依赖对话上下文 |
| standalone query | embed 前必须自解释 |
| 实体栈 | 最近提到的候选实体 |
| 与 100/109 | 消解→改写→检索 可串联 |
| 了解篇 | 规则 PoC 够用，LLM 兜底 |

---

## 13. 常见陷阱与 FAQ

**Q：指代消解和 [109 会话增强](109.conversation-query-enhancement-tutorial.md) 重复吗？**  
A：109 更宽；本篇 **专注代词/指示词/省略**——可合并实现，评测应 **可 ablation**。

**Q：英文 them/it 一样吗？**  
A：思路相同；英文 **显式代词** 多，中文 **零指代** 更多——规则要分语言。

**Q：要训练共指模型吗？**  
A：企业 PoC **不必**；规则 + LLM 覆盖大部分客服场景；文档级共指靠 **分块带标题**（[62 结构分块](62.structure-aware-chunking-tutorial.md)）。

**Q：Multi-Query 能替代消解吗？**  
A：不能——[101](101.multi-query-retrieval-tutorial.md) 扩 **问法**，不保证 **「它」→ 实体**。

**Q：消解错了怎么办？**  
A：检索差 → [112 拒答](112.refusal-strategy-tutorial.md) 或 **「您指的是 A 还是 B？」** 澄清。

**Q：和 [119 摘要](119.summary-memory-tutorial.md) 谁先做？**  
A：先摘要压体积，再 **从摘要取 entities** 做消解——顺序可同请求内 **先读 summary 再 resolve**。

**Q：日志会泄密吗？**  
A：`resolved_query` 可能含 **敏感实体名**——日志 **同 ACL** 脱敏。

**Q：能否用 NER 代替？**  
A：NER 抽 **当前句实体**；指代要 **跨句链接**——可 NER + 栈 **组合**。

**Q：语音输入「嗯那个」怎么办？**  
A：ASR 噪声 + 口语指代更狠——**低置信澄清** 优于瞎猜。

**Q：评测要多少条？**  
A：PoC **30 条** 指代 follow-up；上线 **100+** 分 topic。

**Q：指代消解算 C5 还是 C6？**  
A：路线图放 **C6 会话理解**；实现上贴 **检索前**（C5 边界），本篇按路线图 **C6**。

**Q：和 HyDE 冲突吗？**  
A：[102 HyDE](102.hyde-tutorial.md) 生成 **假答案** embed；指代展开 **改 query 字面**——可 **先 resolve 再 HyDE**。

### 13.1 读路径自检

1. 为何 embed 前消解？  
2. 「二线呢」缺什么？  
3. entity_stack 何时清空？  
4. 与 100 篇分工？  
5. 低置信怎么办？  
6. 了解篇为何不上共指模型？

### 13.2 动手作业

1. 跑 §9，改 entity_stack 顺序看输出；  
2. 写 5 条 **话题切换** 负例；  
3. 对接 [76 Chroma](76.chroma-vector-db-tutorial.md) 对比 resolve 前后 hits。

---

## 14. 总结与系列下一步

1. **多轮 RAG 的短 follow-up 几乎必有指代**——不能只 embed 最后一句。  
2. **指代消解产出 standalone query**，位置在 **embed 之前**。  
3. **规则栈 + 摘要 entities** 覆盖 PoC；LLM **低置信兜底**。  
4. 与 [100](100.query-rewriting-tutorial.md)、[109](109.conversation-query-enhancement-tutorial.md) **串联但可分测**。  
5. 下一篇 [121 越权过滤](121.unauthorized-doc-filter-tutorial.md) 保 **检索安全**。

### 14.1 系列下一步

| 目标 | 阅读 |
|------|------|
| 历史压缩 | [119 Summary Memory](119.summary-memory-tutorial.md) |
| 越权防护 | [121 越权文档过滤](121.unauthorized-doc-filter-tutorial.md) |
| Query 改写 | [100 Query Rewriting](100.query-rewriting-tutorial.md) |

### 14.2 面试 30 秒版

「会话里用户说『它和旧版比呢』，向量检索不能直接用『它』。指代消解在 embed 前把代词绑回实体，输出 standalone query。用实体栈、摘要 entities、recency 评分；低置信 LLM 或澄清。与 query rewriting 分工：先消解再扩展。了解篇，PoC 规则够用。」

---

> **初学者可能仍困惑的点**  
> - 指代消解 **不是** 让回答更礼貌——只服务 **检索 query**。  
> - **109 可包含部分能力**，但 **指代 bad case** 要单独金标。  
> - 中文 **省略主语** 也算指代——规则要覆盖 **短句 follow-up**。

### 14.3 话题切换（Topic Shift）检测

用户从「差旅政策」突然问「打印机怎么报修」——entity_stack 若不清空，「它」会 **错绑差旅**。

**启发式**：

1. 本轮 query 与 **栈顶实体** 的 embedding 相似度 **低于 τ** → 清空栈；  
2. 出现 **新领域关键词**（打印机、VPN、食堂）且与 summary.user_goal **无关** → 清空；  
3. 用户显式「换个话题」→ 清空 summary 或 **fork session**。

### 14.4 与 101 Multi-Query 组合示例

低置信指代时生成 **2 个候选实体 query**，各检索 k=3，**RRF 融合**（[94 RRF](94.rrf-fusion-tutorial.md)）——比赌一个 antecedent 更稳，代价是 **延迟与成本**。

### 14.5 故障排查速查

| 现象 | 原因 | 处理 |
|------|------|------|
| 搜到 IT 部 | 「它」未消解 | §9 detect_coref |
| 检索空 | 展开过窄 | Multi-Query |
| 错实体 | 栈未清空 | topic shift |
| 延迟高 | 每句 LLM | 规则优先 |

### 14.6 给新人的白板图

画一条线：`history → resolve → (rewrite) → embed → retrieve → generate`。在 **resolve** 旁标注：**没有这一步，多轮 RAG 第三轮起 recall 断崖**。

### 14.7 中文指代金标集模板（JSONL）

```json
{"id":"cr-001","turns":[{"role":"user","content":"2024差旅政策有哪些变化"},{"role":"assistant","content":"主要变化在住宿标准..."}],"query":"它和旧版比呢","resolved":"2024差旅政策与旧版差异","entity":"2024差旅政策"}
{"id":"cr-002","turns":[...],"query":"二线呢","resolved":"二线城市住宿标准上限","entity":"住宿标准"}
{"id":"cr-003","turns":[...],"query":"那个审批要几天","resolved":"2024差旅政策审批流程需要几天","entity":"2024差旅政策"}
```

每月从生产 **采样脱敏** 追加 10 条，**禁止** 只有工程师手写脱离业务的假句。

### 14.8 与 [100 Query Rewriting](100.query-rewriting-tutorial.md) 合并 prompt 示例

若 latency 预算只允许 **一次 LLM**：

```text
任务1：将代词替换为具体实体。
任务2：扩展同义词提高召回（可选，最多1个扩展短语）。
输出 JSON：{"standalone": "...", "rewrites": ["..."]}
```

合并后 **无法单独 ablation**——仅在中等规模后采用；早期 **分模块** 更利于排障。

### 14.9 团队 Review 清单（指代 PR）

- [ ] 日志：`raw_query`、`resolved_query`、`confidence`  
- [ ] `detect_coref` **短路** 无指代句  
- [ ] topic shift **清空栈** 单测  
- [ ] 与 [119 summary.entities](119.summary-memory-tutorial.md) **字段契约**  
- [ ] 低置信 **澄清话术** 或 Multi-Query，**不静默瞎猜**  
- [ ] 金标 JSONL **CI 回归** resolve 准确率

### 14.10 案例：错误消解 vs 正确消解

| 用户句 | 错误展开 | 正确展开 |
|--------|----------|----------|
| 它和旧版比 | IT部门与旧版 | 2024差旅政策与旧版 |
| 那个呢 | 那个 | 住宿标准（二线） |
| 审批呢 | 审批呢 | 2024差旅政策审批流程 |

### 14.11 了解篇边界再强调

**不必** 为 PoC 训练 SpanBERT；**必须** 在 embed 前 **显式实体化**。若产品 80% 会话 ≤3 轮，指代模块仍要有——**第 4 轮 follow-up** 往往是满意度分水岭。

### 14.12 观测指标

| 指标 | 说明 |
|------|------|
| coref_trigger_rate | 含指代问句占比 |
| resolve_confidence_p50 | 规则置信度 |
| recall_delta | resolve 前后 Recall@5 差 |
| clarify_rate | 转澄清比例 |
'''

ARTICLE_121 = r'''# C6 生成与 Grounding（十二）：越权文档过滤 Unauthorized Doc Filter 完全指南

> 销售访客问「Q4 大客户签约金额」——检索若 **不过滤 ACL**，[53 篇](53.metadata-acl-tutorial.md) 早已说清：**财务 chunk 会进 prompt**，模型会 **礼貌泄密**。[121 越权文档过滤](121.unauthorized-doc-filter-tutorial.md) 把 **Unauthorized Document Filter** 做成 RAG 链路的 **硬闸**：在 **向量检索前/中** 按 **用户身份** 剔除无权 chunk，并与 [76 Chroma where 过滤](76.chroma-vector-db-tutorial.md)、[34 Grounding 拒答](34.grounding-citation-tutorial.md) 分工。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C6 地基篇**（路线图第 **138** 条），**深度对齐 [53 ACL](53.metadata-acl-tutorial.md)**。前置：[53 ACL 元数据](53.metadata-acl-tutorial.md)、[76 Chroma](76.chroma-vector-db-tutorial.md)、[34 Grounding](34.grounding-citation-tutorial.md)、[112 拒答策略](112.refusal-strategy-tutorial.md)。

---

## 目录

1. [前言：越权是检索事故，不是幻觉](#1-前言越权是检索事故不是幻觉)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [越权文档过滤是什么](#3-越权文档过滤是什么)
4. [与 53 篇 ACL 元数据的对齐](#4-与-53-篇-acl-元数据的对齐)
5. [过滤在链路中的三道防线](#5-过滤在链路中的三道防线)
6. [检索前 filter vs 检索后 post-filter](#6-检索前-filter-vs-检索后-post-filter)
7. [Chroma / 向量库 where 实战](#7-chroma--向量库-where-实战)
8. [Namespace 与多租户隔离](#8-namespace-与多租户隔离)
9. [综合实战：ACL Mini-RAG 端到端](#9-综合实战acl-mini-rag-端到端)
10. [先错对对：六种典型翻车](#10-先错对对六种典型翻车)
11. [审计、测试与合规](#11-审计测试与合规)
12. [与 Grounding、拒答、121→122 安全链](#12-与-grounding拒答121122-安全链)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：越权是检索事故，不是幻觉

[53 篇](53.metadata-acl-tutorial.md) 开场那个 **销售访客看到签约金额** 的场景，在本篇 **从 C6 生成轨再钉一次**：  
模型 **没有编造**——它 **忠实总结** 了 prompt 里的财务段落。产品事故标签应是 **Unauthorized Disclosure（越权披露）**，不是 Hallucination。

**Unauthorized Doc Filter**（越权文档过滤）：在 RAG 检索与上下文组装阶段，根据 **当前用户 principal**（身份、角色、租户） **排除无权访问的 chunk/文档**，确保 **机密原文 never enters prompt**。  
通俗说：**进模型之前先验票**——没票的文件 **连摘要都不能拼**。

**Defense in depth**（纵深防御）：网关鉴权 + 检索 filter + 引用链接鉴权 + 审计——**单点失效不致命**。

**读完本文，你应该能做到：**

1. 复述 [53 ACL](53.metadata-acl-tutorial.md) 的 **chunk 级 acl 字段** 如何映射到 filter。  
2. 实现 §9 **Chroma where + 双角色对照查询**。  
3. 说明 **检索前 filter** 与 **post-filter** 的 recall/安全 trade-off。  
4. 画出 **越权泄露链** 并指出 **C6 应截断的位置**。  
5. 写 **权限回归测试** 含 guest/finance/cross-tenant 负例。  
6. 区分 **越权拒答** vs [112 无资料拒答](112.refusal-strategy-tutorial.md) vs [122 内容安全](122.content-safety-filter-tutorial.md)。

### 1.1 C6 轨位置

```text
112 拒答（资料里没有）
121 越权文档过滤 ← 本篇（有权但不该看 / 无权 chunk）
122 内容安全（有害内容）
113/114 引用（无权 chunk 不应出现）
```

### 1.2 术语双轨速查

| 中文 | English | 一句话 |
|------|---------|--------|
| 越权 | Unauthorized access | 无权仍看到内容 |
| 主体 | Principal | 当前用户身份 |
| 检索前过滤 | Pre-filter / index filter | where 缩小候选 |
| 检索后过滤 | Post-filter | top-k 后再滤 |
| 租户隔离 | Tenant isolation | tenant_id 硬边界 |

---

## 2. 本文边界与动手路径

**档位：C6 地基篇（路线图 138）。**

**本文讲：** 越权定义、53 对齐、三道防线、Chroma where、Mini-RAG、测试清单、与 Grounding 分工。  
**本文不讲：** OAuth/OIDC 完整实现、LDAP 同步、密级定标法规全文、零信任网络架构。

### 2.1 动手路径表

| 步骤 | 你做什么 | 验收 |
|------|----------|------|
| A | 精读 [53 ACL](53.metadata-acl-tutorial.md) §3～§7 | 能画泄露链 |
| B | 读 §4 字段映射表 | acl_group 一致 |
| C | 跑 §9 双用户查询 | guest 无 finance |
| D | 写 6 条权限负例 | CI 可跑 |
| E | §10 先错对对 | 六种错 |
| F | 对照 §12 三分拒答 | 话术不混 |

**环境：** Python 3.10+；`pip install chromadb`；复用 [76 篇](76.chroma-vector-db-tutorial.md) 语料。

### 2.2 沿用前文（53 深度链接）

| 概念 | 来自 [53 ACL](53.metadata-acl-tutorial.md) |
|------|---------------------------------------------|
| chunk 上 `allowed_roles` / `acl_group` | §3 ACL 是什么 |
| post-filter vs namespace | §5～§6 |
| 提示词防泄密失败 | §11 先错对对 |
| 向量库 filter 概念 | §10 |
| 泄露链 | §7 |
| 测试清单 | §13 |

---

## 3. 越权文档过滤是什么

读下图：过滤点在 **检索**，不是 **生成后马后炮**。

![越权过滤在 RAG 链路](image/unauthorized-doc-filter/01-filter-gates.png)

[53 篇](53.metadata-acl-tutorial.md) 强调：**泄密发生在 chunk 进 prompt 时**。C6 本篇从 **工程落地** 回答：**filter 写在哪、长什么样、如何测**。

### 3.1 两类「越权」

| 类型 | 例子 | 处理 |
|------|------|------|
| 角色越权 | guest 看 finance_only | acl_group filter |
| 租户越权 | A 公司看 B 公司索引 | tenant_id namespace |
| 文档级撤权 | 用户曾有权现已回收 | 版本 + 实时权限服务 |
| 引用越权 | 答案里链到无权 PDF | 链接鉴权 |

### 3.2 不是越权的情况

- 资料 **公开** 但 **库中没有** → [112 拒答](112.refusal-strategy-tutorial.md)；  
- 用户 **有权** 但内容 **违规** → [122 内容安全](122.content-safety-filter-tutorial.md)；  
- 模型 **编造** 未返回的 chunk_id → [34 Grounding](34.grounding-citation-tutorial.md) 校验。

---

## 4. 与 53 篇 ACL 元数据的对齐

**本篇是 [53 ACL](53.metadata-acl-tutorial.md) 的 C6 执行篇**——字段设计 **不再重复发明**，直接沿用：

### 4.1 推荐 chunk metadata（与 53 一致）

```json
{
  "doc_id": "finance-q4",
  "chunk_id": "fin:v1:c001",
  "tenant_id": "corp_a",
  "acl_group": "finance_only",
  "allowed_roles": ["finance", "cfo"],
  "classification": "internal"
}
```

| 字段 | 53 篇对应 | 过滤用法 |
|------|-----------|----------|
| tenant_id | §4 多租户 | **硬必滤** |
| acl_group | §3 谁能看 | where 主字段 |
| allowed_roles | §8 设计 | 或 `$contains` 角色 |
| classification | 扩展 | 高密级双重校验 |

### 4.2 Principal 对象（请求态）

```python
@dataclass
class Principal:
    user_id: str
    tenant_id: str
    roles: list[str]  # 来自 IdP
    groups: list[str]  # acl_group 映射
```

**每次检索** 从 **已认证 session** 构造 Principal——**不可** 信任客户端传的 `role=guest` 查询参数（[53 §11](53.metadata-acl-tutorial.md)）。

### 4.3 与 53 §5 post-filter 的关系

[53 篇](53.metadata-acl-tutorial.md) §5 说 post-filter **有 recall 泄露风险**（top-k 全是无权块时 **补位不足**）。本篇 **默认推荐检索前 where**（[76 Chroma §7](76.chroma-vector-db-tutorial.md)）；post-filter 仅作 **兜底** 或 **不支持 where 的引擎**。

读下图：53 策略在本篇的选型。

![53 ACL 策略落地](image/unauthorized-doc-filter/02-acl-strategies.png)

---

## 5. 过滤在链路中的三道防线

| 防线 | 位置 | 动作 |
|------|------|------|
| 1 网关 | API 入口 | JWT 校验、tenant 绑定 |
| 2 检索 | vector query | **where / namespace** |
| 3 组装 | 拼 prompt 前 | 再滤 + chunk_id 白名单 |

**C6 主战场是防线 2 和 3**——[53](53.metadata-acl-tutorial.md) 已讲 **为何**；本篇讲 **怎么写代码**。

### 5.1 防线 3 的必要性

即使用了 where，仍要 **对 hits 再校验**——防 **metadata 入库错误**、**索引污染**、**bug 绕过**。  
校验失败：**丢弃 hit + 告警**，不要 **静默进 prompt**。

---

## 6. 检索前 filter vs 检索后 post-filter

| 维度 | 检索前 where | 检索后 filter |
|------|--------------|---------------|
| 安全 | 无权块 **不进候选** | 可能占满 top-k |
| Recall | 在 **有权子集** 内 ANN | 可能 **k 不够** |
| 性能 | 索引支持则优 | 多算距离浪费 |
| 53 篇建议 | **优先** | 兜底 |

**Hybrid**：where 缩 tenant + acl，post-filter **复核** `allowed_roles`。

---

## 7. Chroma / 向量库 where 实战

直接复用 [76 篇 §7](76.chroma-vector-db-tutorial.md) 与 [53 篇 §10](53.metadata-acl-tutorial.md)：

```python
def build_chroma_where(principal: Principal) -> dict:
    """与 53 ACL、76 where 对齐"""
    role_clauses = [{"acl_group": "all_staff"}]
    for g in principal.groups:
        role_clauses.append({"acl_group": g})
    return {
        "$and": [
            {"tenant_id": principal.tenant_id},
            {"$or": role_clauses},
        ]
    }
```

**guest 用户** `groups=[]` → 仅 `all_staff`。**finance** 追加 `finance_only`。

### 7.1 常见 where 翻车（76 §8 + 53 §11）

- metadata 类型错（list 未序列化）→ Chroma 报错或 **静默不匹配**；  
- 忘记 tenant → **跨租户越权**；  
- `$or` 写错括号 → **全员可见 finance**。

---

## 8. Namespace 与多租户隔离

[53 篇 §4](53.metadata-acl-tutorial.md) Multi-tenancy + [89 namespace](89.multi-tenant-namespace-tutorial.md)：

| 模式 | 做法 | 何时 |
|------|------|------|
| 单 collection + tenant_id | where 必带 | 中小规模 |
| 每 tenant 一 collection | 物理隔离 | 强合规 |
| 每 tenant 一 persist 目录 | 76 PersistentClient 分 path | 演示/离线 |

**C6 生成轨提醒**：即使 namespace 隔离，**同 tenant 内仍要 acl_group**——财务与 HR 不能共用一个「内部」标签糊弄。

---

## 9. 综合实战：ACL Mini-RAG 端到端

扩展 [76 §9](76.chroma-vector-db-tutorial.md) 语料，演示 **guest vs finance**：

```python
"""unauthorized_filter_demo.py — 53 ACL + 76 Chroma where"""
import chromadb
import numpy as np
from dataclasses import dataclass

DIM = 64
PERSIST = "./chroma_acl_demo"
COLLECTION = "handbook_acl"


@dataclass
class Principal:
    user_id: str
    tenant_id: str
    groups: list[str]


CHUNKS = [
    {"id": "hb:v1:c001", "text": "一线城市住宿上限500元", "meta": {"tenant_id": "t1", "acl_group": "all_staff", "doc_id": "handbook"}},
    {"id": "hb:v1:c002", "text": "年假最少5天", "meta": {"tenant_id": "t1", "acl_group": "all_staff", "doc_id": "handbook"}},
    {"id": "fin:v1:c001", "text": "Q4大客户签约金额见财务门户", "meta": {"tenant_id": "t1", "acl_group": "finance_only", "doc_id": "finance"}},
    {"id": "fin:v1:c002", "text": "预算审批需CFO签字", "meta": {"tenant_id": "t1", "acl_group": "finance_only", "doc_id": "finance"}},
]


def embed_texts(texts, dim=DIM):
    out = []
    for t in texts:
        rng = np.random.default_rng(abs(hash(t)) % (2**32))
        v = rng.standard_normal(dim).astype("float32")
        v /= np.linalg.norm(v) + 1e-9
        out.append(v.tolist())
    return out


def build_where(p: Principal) -> dict:
    clauses = [{"acl_group": "all_staff"}] + [{"acl_group": g} for g in p.groups]
    return {"$and": [{"tenant_id": p.tenant_id}, {"$or": clauses}]}


def ingest():
    client = chromadb.PersistentClient(path=PERSIST)
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    col.upsert(
        ids=[c["id"] for c in CHUNKS],
        documents=[c["text"] for c in CHUNKS],
        metadatas=[c["meta"] for c in CHUNKS],
        embeddings=embed_texts([c["text"] for c in CHUNKS]),
    )


def retrieve(query: str, principal: Principal, k: int = 3):
    client = chromadb.PersistentClient(path=PERSIST)
    col = client.get_collection(COLLECTION)
    where = build_where(principal)
    res = col.query(
        query_embeddings=[embed_texts([query])[0]],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return post_validate(res, principal)


def post_validate(res, principal: Principal) -> list[dict]:
    """防线 3：再滤 + 53 复核"""
    hits = []
    allowed_groups = {"all_staff"} | set(principal.groups)
    for i in range(len(res["ids"][0])):
        meta = res["metadatas"][0][i]
        if meta.get("tenant_id") != principal.tenant_id:
            continue
        if meta.get("acl_group") not in allowed_groups:
            continue
        hits.append({"id": res["ids"][0][i], "text": res["documents"][0][i], "meta": meta})
    return hits


def rag_answer(query: str, principal: Principal) -> str:
    hits = retrieve(query, principal)
    if not hits:
        return forbidden_message(principal, query)
    ctx = "\n".join(h["text"] for h in hits)
    return f"【基于授权资料】\n{ctx}\n\n（接 LLM + [34 Grounding](34.grounding-citation-tutorial.md)）"


def forbidden_message(p: Principal, query: str) -> str:
    """越权/无命中 — 与 112 拒答区分"""
    return "您当前权限无法访问与该问题相关的内部资料。如需财务信息请联系财务部门。"


if __name__ == "__main__":
    ingest()
    guest = Principal("u1", "t1", [])
    finance = Principal("u2", "t1", ["finance_only"])
    q = "Q4大客户签约金额"
    print("guest hits:", [h["id"] for h in retrieve(q, guest)])
    print("finance hits:", [h["id"] for h in retrieve(q, finance)])
```

**验收**：

- guest 查「签约金额」→ **hits 为空** 或 **无 fin:** chunk；  
- finance → **含 fin:v1:c001**；  
- guest 查「住宿」→ **hb:v1:c001**。

### 9.1 拼 prompt 与 [34 Grounding](34.grounding-citation-tutorial.md)

仅 **post_validate 后** 的 hits 进入 `messages`；引用 `[1]` 的 `chunk_id` 必须来自 hits——[113 行内引用](113.inline-citation-tutorial.md) **不负责保密**（113 已链本篇）。

---

## 10. 先错对对：六种典型翻车

### 10.1 错：只靠 [110 Prompt](110.rag-prompt-template-tutorial.md)「请勿泄露机密」

**对**：[53 §11](53.metadata-acl-tutorial.md)——**检索前 filter**；prompt 不能 **撤销已进窗原文**。

### 10.2 错：检索全库，Python 里 if 过滤但 k 太小

**对**：**where 预滤**；或 **增大 k' 再 post-filter** 并监控 **有效命中数**（53 §5 recall 坑）。

### 10.3 错：metadata 无 tenant_id，只靠 acl_group

**对**：**tenant_id 硬必滤**（53 §4 多租户）。

### 10.4 错：客户端传 `?acl=finance` 决定 filter

**对**：Principal 来自 **服务端 JWT**（53 §8）。

### 10.5 错：越权时仍让 LLM「根据常识回答」

**对**：`forbidden_message`（§9）——**越权拒答** 话术；与 [112 无资料](112.refusal-strategy-tutorial.md) 分 logging code。

### 10.6 错：引用链接不鉴权，正文滤了链接漏

**对**：[115 源文档跳转](115.source-document-navigation-tutorial.md) 打开前 **再验权**。

---

## 11. 审计、测试与合规

### 11.1 审计日志（每条检索）

```json
{"user_id":"u1","tenant_id":"t1","query_hash":"...","filter_where":{...},"hit_ids":[],"denied_reason":"no_authorized_hits"}
```

### 11.2 权限回归矩阵（继承 53 §13）

| 用例 | 用户 | 查询 | 期望 |
|------|------|------|------|
| P1 | guest | 住宿 | hb hit |
| P2 | guest | 签约金额 | 无 fin hit / 越权拒答 |
| P3 | finance | 签约金额 | fin hit |
| P4 | tenant_b | tenant_a doc | 空 |
| P5 | 撤权用户 | 曾有权 doc | 空 + 告警 |

### 11.3 红队

刻意 **改 where 为空** 跑 CI——应 **测试失败**。

---

## 12. 与 Grounding、拒答、121→122 安全链

| 场景 | 模块 | 用户看到 |
|------|------|----------|
| 无权 chunk | **本篇 121** | 权限不足 |
| 有权但库无 | [112 拒答](112.refusal-strategy-tutorial.md) | 资料未提及 |
| 有权有害 | [122 安全](122.content-safety-filter-tutorial.md) | 安全拒答 |
| 编造引用 | [34 Grounding](34.grounding-citation-tutorial.md) | 校验失败 |

读下图：C6 安全分工。

![C6 安全分工](image/unauthorized-doc-filter/03-security-split.png)

---

## 13. 综合概念地图

![越权过滤概念速记](image/unauthorized-doc-filter/04-concept-map.png)

| 概念 | 一句话 |
|------|--------|
| 越权过滤 | 无权 chunk 不进 prompt |
| 53 ACL | 字段与策略真理源 |
| where | 检索前主手段 |
| post_validate | 组装前兜底 |
| vs 112/122 | 三分拒答 |

---

## 14. 常见陷阱与 FAQ

**Q：121 和 53 重复吗？**  
A：53 是 **C1 元数据设计**；121 是 **C6 落地 + Chroma + 测试**——**必读 53**。

**Q：LLM 能否自己判断权限？**  
A：**不能**——模型不知道 IdP；filter 必须 **确定性**。

**Q：RAG 和文档库权限不一致？**  
A：**同步 job** 把 CMS ACL 打到 chunk metadata；**延迟窗口** 要监控（53 §13）。

**Q：admin 能否 bypass？**  
A：** break-glass 账号** 单独审计；不要 **默认不过滤**。

**Q：混合检索 BM25 怎么滤？**  
A：BM25 与向量 **同一 filter 表达式**（[88 metadata filter](88.metadata-filter-retrieval-tutorial.md)）。

**Q：filter 影响延迟？**  
A：metadata 索引良好时常 **降扫描量**；见 [76 §10](76.chroma-vector-db-tutorial.md)。

**Q：用户问「把所有财务文档列给我」？**  
A：**列表型查询** 也要 filter——防 **枚举攻击**。

**Q：embedding 会泄露跨 tenant 吗？**  
A：同索引空间时 **where 必须带 tenant**；极高隔离用 **分 collection**（53 §6）。

**Q：越权 hit 为 0 时检索 broader？**  
A：**禁止** 自动放宽 ACL 搜全库——宁可 [112 式拒答](112.refusal-strategy-tutorial.md) 或 **澄清**。

**Q：和 [121] 自己链接？**  
A：本篇即 121；下游 [122 内容安全](122.content-safety-filter-tutorial.md) 接 **有权内容** 的安全闸。

**Q：日志存 query 全文合规吗？**  
A：query 可能含 PII——**哈希 + 采样**；hits 存 id 不存全文。

**Q：如何向法务解释？**  
A：**「模型没看到无权数据」**——filter 证明 + 审计链（53 §7 泄露链反向说明）。

### 14.1 读路径自检

1. 越权 vs 幻觉？  
2. 53 哪个字段必滤 tenant？  
3. 为何 post-filter 不够？  
4. guest finance 负例期望？  
5. 三道防线各在哪？  
6. 与 112 话术区别？

### 14.2 团队 Review 清单（121 PR）

- [ ] Principal 来自 **服务端认证**  
- [ ] where 含 **tenant_id + acl**（53 对齐）  
- [ ] post_validate 存在  
- [ ] 越权拒答 **独立 error code**  
- [ ] 权限矩阵 CI  
- [ ] 不提交含真实机密的 chroma 目录  

---

## 15. 总结与系列下一步

1. **越权是检索问题**——[53 ACL](53.metadata-acl-tutorial.md) 定字段，本篇 **C6 执行 filter**。  
2. **检索前 where 为主**，post_validate **兜底**——不用 prompt 防泄密。  
3. **[76 Chroma where](76.chroma-vector-db-tutorial.md)** 是 PoC 默认实现；生产可换 Milvus/pgvector **同一 metadata 契约**。  
4. **三分拒答**：121 越权、112 无资料、122 安全——**日志 code 分开**。  
5. **Grounding** 只处理 **已授权 hits**（[34](34.grounding-citation-tutorial.md)）。

### 15.1 系列下一步

| 目标 | 阅读 |
|------|------|
| ACL 元数据真理源 | [53 ACL](53.metadata-acl-tutorial.md) |
| Chroma where | [76 Chroma](76.chroma-vector-db-tutorial.md) |
| 内容安全 | [122 内容安全](122.content-safety-filter-tutorial.md) |
| 行内引用 | [113 行内引用](113.inline-citation-tutorial.md) |

### 15.2 面试 30 秒版

「越权不是幻觉，是无权 chunk 进了 prompt。chunk 上 tenant_id 和 acl_group，检索前 Chroma where 按 JWT principal 过滤，组装前 post_validate。53 篇设计字段，121 落地。guest 搜不到 finance_only。不能靠 prompt 保密。与 112 无资料、122 安全分开拒答。」

---

> **初学者可能仍困惑的点**  
> - **先读 53 再读 121**——字段名保持一致。  
> - **filter 空结果** 不等于 **可以搜全库**。  
> - **Citation 链接** 也要鉴权——正文滤了不算完。

### 15.3 与 53 篇对照背诵卡片

正面问「ACL 字段放哪？」背面答「chunk metadata，入库时从文档 ACL 同步」。  
正面问「泄密发生在哪？」背面答「无权 chunk 进 prompt，不是生成阶段」。  
正面问「121 和 53 分工？」背面答「53 设计字段，121 C6 写 where + 测试」。  
正面问「post-filter 为何不够？」背面答「top-k 可能全是无权块，Recall 在有权子集内耗尽」。  
正面问「guest 搜 finance？」背面答「hits 空 + 越权拒答，禁止放宽 filter」。

### 15.4 迁移到 Milvus / pgvector 时 filter 怎么带？

[53 §10](53.metadata-acl-tutorial.md) 概念 + [76 §10.5](76.chroma-vector-db-tutorial.md) 迁移直觉：

| 引擎 | filter 表达 |
|------|-------------|
| Chroma | `where` JSON |
| Milvus | `expr` 字符串 |
| pgvector | `WHERE tenant_id=$1 AND acl_group = ANY($2)` |

**metadata 字段名不要改**——换引擎只换 **filter 语法**，53 的设计 **直接继承**。

### 15.5 30 分钟动手作业

1. 跑 §9，`guest` 与 `finance` 各查「签约金额」「住宿」；  
2. 故意删掉 `where` 跑对照——理解 **越权危害**；  
3. 读 [53 §11](53.metadata-acl-tutorial.md) 先错对对，写进团队 wiki；  
4. 给 [113 行内引用](113.inline-citation-tutorial.md) 组件加 **hit_ids 白名单** 校验思路。

### 15.6 给安全同事的说明

RAG 越权 **等价于** 把 PDF 段落贴进 HTTP 响应——应走 **同一套 IAM 决策**。filter 逻辑建议 **与文档 CMS 共用** `can_read(user, doc_id)` 函数，避免 **RAG 一套、门户一套** 漂移。

### 15.7 深度对齐 [53 ACL](53.metadata-acl-tutorial.md)：入库同步

[53 §8](53.metadata-acl-tutorial.md) 动手路径要求 chunk 设计 acl 形状。121 执行时 **入库 job** 必须：

```python
def acl_for_chunk(doc_id: str, user_directory) -> dict:
    doc_acl = user_directory.get_document_acl(doc_id)  # 权威源
    return {
        "tenant_id": doc_acl.tenant_id,
        "acl_group": doc_acl.primary_group,
        "allowed_roles": doc_acl.roles,  # 若引擎支持
    }
```

**禁止** 解析 PDF 时 **写死 all_staff**「以后再说」——[53 §3.1](53.metadata-acl-tutorial.md) 强调 MVP 也要预留字段。

### 15.8 [76 Chroma](76.chroma-vector-db-tutorial.md) where 与 53 post-filter 对照实验

建议同一语料跑 **A/B**：

| 实验 | 配置 | 期望 |
|------|------|------|
| A | 仅 where | guest 无 fin |
| B | 无 where + post-filter k=3 | guest **可能漏** fin 若相似度低 |
| C | where + post_validate | 双保险 |

将结果截图贴进 **安全评审**——用数据回答「为何不能只 post-filter」。

### 15.9 越权拒答话术与 [112 拒答](112.refusal-strategy-tutorial.md) 对照

| 类型 | HTTP code 建议 | 话术要点 |
|------|----------------|----------|
| 121 越权 | 403 | 权限不足，不暗示答案存在 |
| 112 无资料 | 200 + 拒答 | 资料未提及，可建议联系部门 |
| 122 安全 | 400/451 | 内容违规，不复述违规句 |

**日志** 必须带 `deny_reason=ACL_DENIED` vs `NO_EVIDENCE`，否则运维 **无法统计** 越权尝试次数。

### 15.10 与 [34 Grounding](34.grounding-citation-tutorial.md) 引用校验

```python
def validate_citations(answer: str, allowed_chunk_ids: set[str]) -> bool:
    cited = extract_chunk_ids(answer)  # 解析 [chunk_id=...]
    return cited.issubset(allowed_chunk_ids)
```

`allowed_chunk_ids` 来自 **post_validate 后 hits**——若模型 cite 了 **未检索到的 fin:** id，**整段答案拒发** 并告警（可能 prompt 注入或模型编造）。

### 15.11 枚举攻击与「列出所有财务文档」

即使用户 **不直问数字**，「把所有 finance 文档标题列给我」也是 **枚举泄露**。处理：

1. filter 后 **hits 为空** → 越权拒答；  
2. 即使 hits 非空，**列表型回答** 需 **额外策略**（最多 N 条、需更高权限 role）；  
3. 审计 **高频列表请求**。

### 15.12 权限变更的实时性

[53 §13](53.metadata-acl-tutorial.md) 测试清单含 **撤权用户**。若 IAM 已撤权但向量 metadata **未更新**：

- **短期**：检索层调 **实时 `can_read`** post_validate；  
- **长期**：CDC 同步 **更新 metadata** 或 **删除 chunk**（[49 增量](49.incremental-update-tutorial.md)）。

### 15.13 给法务与审计的一句话

「我们的 RAG 在检索阶段用与门户相同的 ACL 表达式过滤 chunk；无权用户的 prompt 中 **不会组装** 机密段落；每次拒答有 **ACL_DENIED** 审计记录。」

### 15.14 故障排查速查（121 专用）

| 现象 | 查什么 |
|------|--------|
| guest 看到 finance | where 是否为空 / JWT 伪造 |
| 全员搜不到 public | acl_group 入库全错 |
| 跨 tenant 泄漏 | tenant_id 未滤 |
| 有 hit 但 cite 越权 | 未做 validate_citations |
| finance 也搜不到 | groups 未映射 finance_only |
'''
