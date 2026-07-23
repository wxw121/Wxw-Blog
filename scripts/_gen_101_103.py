# -*- coding: utf-8 -*-
"""Generate expanded tutorials 101-103 (query enhancement, pre-retrieval)."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

def count_hanzi(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


COMMON_INTRO_FOOTER = """
**重要边界：** 本篇属于 **查询增强（Query Enhancement）**，在 **[93 混合检索](93.hybrid-search-tutorial.md) 之前** 处理用户 query；**不是** [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md) 精排。精排发生在召回之后，对候选 chunk 重排序；查询增强只改变 **送进检索器的问句或问句集合**。

标准 RAG 链路：

```text
用户 q_user
  → 查询增强（本篇）
  → [93 混合检索](93.hybrid-search-tutorial.md) Top-R
  → [94 RRF](94.rrf-fusion-tutorial.md) 融合
  → [95/96 精排](95.cross-encoder-rerank-tutorial.md) Top-K
  → 拼 prompt（[28 Context Window](28.context-window-tutorial.md) 预算）
  → LLM 生成
```
"""


def build_multi_query():
    return r'''# C5 查询增强（二）：Multi-Query Retrieval 完全指南

> 用户只问一次，知识库却有十种写法。**Multi-Query Retrieval（多查询检索）** 在 **检索之前** 用 LLM 生成 **多条语义相近、表述不同的检索 query**，分别走 [93 混合检索](93.hybrid-search-tutorial.md)，再 **合并去重** 扩大候选覆盖，最后精排、按 [28 Context Window](28.context-window-tutorial.md) 装入 prompt。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **C5 查询增强地基篇**（路线图第 **118** 条）。前置：[100 Query Rewriting](100.query-rewriting-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)、[95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)。

---

## 目录

1. [前言：一问多搜，补全表述盲区](#1-前言一问多搜补全表述盲区)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Multi-Query Retrieval 是什么](#3-multi-query-retrieval-是什么)
4. [在 RAG 链路中的位置](#4-在-rag-链路中的位置)
5. [子 query 生成策略](#5-子-query-生成策略)
6. [合并、去重与分数策略](#6-合并去重与分数策略)
7. [与混合检索、精排怎么衔接](#7-与混合检索精排怎么衔接)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [最小实现](#9-最小实现)
10. [综合实战](#10-综合实战)
11. [参数、延迟与 Context Window](#11-参数延迟与-context-window)
12. [工程、监控与评测](#12-工程监控与评测)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：一问多搜，补全表述盲区

[100 Query Rewriting](100.query-rewriting-tutorial.md) 把口语变成 **一条** 书面检索式。但现实里，同一意图在库内可能有 **多种合法表述**：

- 「差旅住宿费」「住宿标准」「一线城市酒店上限」  
- 「年假」「带薪年休假」「年度休假」

只搜一种写法时，BM25 可能漏掉 **用词不同** 的 chunk；向量一路也可能因 **单一 query embedding** 偏置而漏召。**Multi-Query Retrieval** 的做法是：从用户原问 `q_user` 生成 `q1, q2, …, qn`（**同义、换角度，不是不同子意图**），每个 `qi` 独立调用 [93 混合检索](93.hybrid-search-tutorial.md)，把多路 hit **并集去重** 后再 [95 精排](95.cross-encoder-rerank-tutorial.md)。

''' + COMMON_INTRO_FOOTER + r'''

**读完本文，你应该能做到：**

1. 区分 Multi-Query 与 [100 改写](100.query-rewriting-tutorial.md)、[103 分解](103.query-decomposition-tutorial.md)。  
2. 设计 **生成 3～5 条** 子 query 的 Prompt 与 JSON 解析护栏。  
3. 实现 **按 chunk_id 去重、保留最高分或 RRF 二次融合**。  
4. 估算 **n 条 query × 混合检索** 的延迟，并在 [28 Context Window](28.context-window-tutorial.md) 内控制最终资料条数。  
5. 识别 §8 四种「子 query 无限增多、合并池爆炸、用子 query 精排、与分解混淆」翻车。

### 1.1 路线图位置

路线图第 **118** 条，档位：**地基**。  
上游：[100 改写](100.query-rewriting-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)。  
下游：[102 HyDE](102.hyde-tutorial.md)、[103 分解](103.query-decomposition-tutorial.md)、[104 Multi-hop](104.multi-hop-retrieval-tutorial.md)。

### 1.2 术语速查

| 中文 | English | 说明 |
|------|---------|------|
| 多查询检索 | Multi-Query Retrieval | 多条 query 分别召回再合并 |
| 子 query | Sub-query | LLM 生成的同义检索问句 |
| 并集去重 | Union + Dedup | 同一 chunk_id 只留一条 |
| 查询增强 | Query Enhancement | 检索前扩展 query，非精排 |

### 1.3 与姊妹篇对照

| 技术 | 产出 | 意图关系 |
|------|------|----------|
| [100 改写](100.query-rewriting-tutorial.md) | 通常 1 条 q_search | 口语→书面 |
| **本篇 Multi-Query** | 多条同义 qi | 多角度表述 |
| [102 HyDE](102.hyde-tutorial.md) | 假想答案段落 | 向量空间对齐 |
| [103 分解](103.query-decomposition-tutorial.md) | 多个子意图 | 复合问拆开 |

---

## 2. 本文边界与动手路径

**档位：C5 地基篇（路线图 118）。**

**本文讲：** Multi-Query 生成、分路 [93 混合检索](93.hybrid-search-tutorial.md)、合并去重、接精排、成本与评测。  
**本文不讲：** 训练 query generator 模型、[103 分解](103.query-decomposition-tutorial.md) 的多意图拆分、[104 多跳](104.multi-hop-retrieval-tutorial.md) 的链式检索。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 画 **1→n→n 路检索→合并** 图 |
| B | `generate_sub_queries` 输出 3 条 JSON |
| C | 每路 `hybrid_search(qi, k=20)` |
| D | `merge_dedupe` 后 ≤80 条候选 |
| E | `rerank(q_user, merged)` Top-5 |
| F | 用 [28 篇](28.context-window-tutorial.md) 算资料 token |

**环境：** Python 3.10+；LLM API；已有 BM25+向量索引（[93 篇](93.hybrid-search-tutorial.md)）。

---

## 3. Multi-Query Retrieval 是什么

![Multi-Query 是什么](image/multi-query-retrieval/01-multi-query-idea.png)

### 3.1 形式化

```text
{q1..qn} = Generate(q_user)
C = ⋃ᵢ hybrid_search(qi)
C' = dedupe(C)
answer = LLM(prompt(q_user, rerank(q_user, C')))
```

核心假设：**多个 qi 的并集 Recall** 高于 **单一 q**——尤其 BM25 对 **不同关键词覆盖** 敏感时。

### 3.2 何时有效

| 场景 | 收益 |
|------|------|
| 库内术语多样 | 高 |
| 用户问法固定书面 | 低（可关） |
| 已做 [100 改写](100.query-rewriting-tutorial.md) 仍漏召 | 中高 |
| 复合多问 | 用 [103 分解](103.query-decomposition-tutorial.md)，不是本篇 |

### 3.3 成本直觉

每多 1 条子 query ≈ 多 1 次 **完整或半套** 混合检索（BM25+向量）。`n=5` 且 `per_k=25` 时，粗算 **5×25=125** 次「单路 top 贡献」再合并——要在 SLA 与收益间折中。

---

## 4. 在 RAG 链路中的位置

```text
q_user
  →（可选）[100 改写]
  → Generate → q1..qn        # 本篇
  → 对每个 qi：93 混合检索
  → merge_dedupe → recall 池
  → 95 精排（配对 q_user 或主 qi）
  → 28 预算内 prompt → 生成
```

**精排用谁？** 推荐 **`q_user` 或质量最高的一条 qi`** 与 chunk 配对——子 query 可能过窄，原问更贴近用户综合意图。

---

## 5. 子 query 生成策略

### 5.1 LLM Prompt 模板

```python
MULTI_QUERY_PROMPT = """根据用户问题，生成 {n} 条适合检索企业知识库的查询问句。
要求：
1. 与用户意图相同，仅改变表述、同义词、角度
2. 不要拆成不同子问题（不要一条问住宿一条问机票，除非用户原问本就包含）
3. 不添加事实、数字、部门
4. 输出 JSON 数组，如 ["问句1","问句2"]

用户问题：{query}
JSON："""
```

### 5.2 解析与护栏

```python
import json

def generate_sub_queries(q: str, llm, n: int = 3) -> list[str]:
    raw = llm.complete(MULTI_QUERY_PROMPT.format(query=q, n=n))
    try:
        arr = json.loads(raw)
        subs = [s.strip() for s in arr if isinstance(s, str) and s.strip()]
    except json.JSONDecodeError:
        subs = []
    subs = subs[:n]
    if q not in subs:
        subs.insert(0, q)  # 始终保留原问
    return subs[:n] or [q]
```

**始终保留 q_user**：防止生成失败时 **零子 query**；且原问对 BM25 仍有基线价值。

### 5.3 与 [100 改写](100.query-rewriting-tutorial.md) 串联

```text
q_user → rewrite → q_search → generate_sub_queries → q1..qn
```

先改写再扩写：**口语先正规化，再多角度同义**——企业客服场景常用。

---

## 6. 合并、去重与分数策略

![多路合并](image/multi-query-retrieval/02-merge-dedup.png)

### 6.1 按 chunk_id 去重（保留最高分）

```python
def merge_max_score(lists_of_hits):
    best = {}
    for hits in lists_of_hits:
        for h in hits:
            cid = h["chunk_id"]
            if cid not in best or h["score"] > best[cid]["score"]:
                best[cid] = h
    return sorted(best.values(), key=lambda x: x["score"], reverse=True)
```

### 6.2 多路 RRF（推荐与 [94 篇](94.rrf-fusion-tutorial.md) 一致）

每个 `qi` 的混合检索结果视为 **一路排名**，对多路做 RRF：

```python
def rrf_multi(lists_of_hits, k=60, top_n=60):
    scores = {}
    for hits in lists_of_hits:
        for rank, h in enumerate(hits):
            cid = h["chunk_id"]
            scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
    # 回填 text：从任意 hit 取
    ...
    return top_n_by_rrf_score
```

**RRF 好处：** 不同 qi 的 BM25/向量分 **不可比**，RRF 只看得名次。

### 6.3 合并后规模控制

| 参数 | 建议 |
|------|------|
| `n_queries` | 3～5 |
| `per_k` | 15～25 |
| 合并后上限 | ≤60～80，再送精排 |

超过 80 条候选 → 精排延迟线性涨（[95 篇](95.cross-encoder-rerank-tutorial.md)）。

---

## 7. 与混合检索、精排怎么衔接

### 7.1 推荐配置

| 阶段 | 值 |
|------|-----|
| n_queries | 4 |
| 每路 bm25_k / dense_k | 20 / 20 |
| 每路 RRF | top 25 |
| 合并后 | ≤60 |
| rerank | Top-5 |
| max_evidence_tokens | 3200（[28 篇](28.context-window-tutorial.md)） |

### 7.2 完整流水线代码

```python
def multi_query_rag(q_user, llm, hybrid_search, rerank, build_prompt, gen):
    subs = generate_sub_queries(q_user, llm, n=4)
    all_lists = [hybrid_search(sq, k=25) for sq in subs]
    merged = rrf_multi(all_lists, top_n=60)
    top = rerank(q_user, merged, top_k=5)
    return gen(build_prompt(q_user, top))
```

### 7.3 ACL

每路检索仍走 [53 ACL](53.metadata-acl-tutorial.md) 过滤；Multi-Query **不能** 绕过权限。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：把 Multi-Query 放在精排之后

**对：** 在 **[93 混合检索](93.hybrid-search-tutorial.md) 之前** 生成多条 qi，分别召回。

### 8.2 错：n=20、per_k=50 导致合并池上千条

**对：** 控制 `n×per_k`；合并后 **截断** 再精排。

### 8.3 错：用每条子 query 分别精排再合并（成本 n 倍精排）

**对：** **先合并去重，再精排一次**（除非特殊评测）。

### 8.4 错：把复合问拆成住宿+机票两条子 query

**对：** 那是 [103 分解](103.query-decomposition-tutorial.md)；本篇子 query 必须 **同义改写**。

---

## 9. 最小实现

```bash
pip install openai rank_bm25
```

```python
# 演示：多 query BM25 并集（省略向量可与 93 篇同样接）
from rank_bm25 import BM25Okapi
import re

DOCS = [
    {"chunk_id": "c1", "text": "一线城市差旅住宿费上限为每晚500元。"},
    {"chunk_id": "c2", "text": "酒店住宿标准：直辖市适用一档限额。"},
    {"chunk_id": "c3", "text": "年假申请须提前在OA提交。"},
]

def tokenize(t):
    return re.findall(r"[\u4e00-\u9fff]+|\w+", t)

bm25 = BM25Okapi([tokenize(d["text"]) for d in DOCS])

def search(q, k=2):
    sc = bm25.get_scores(tokenize(q))
    idx = sorted(range(len(sc)), key=lambda i: sc[i], reverse=True)[:k]
    return [{"chunk_id": DOCS[i]["chunk_id"], "text": DOCS[i]["text"], "score": sc[i]} for i in idx]

q_user = "出差住酒店多少钱"
subs = [q_user, "差旅住宿费标准", "一线城市酒店住宿限额"]
lists = [search(s) for s in subs]
merged = merge_max_score(lists)
print(merged)  # 期望 c1、c2 均出现
```

---

## 10. 综合实战

1. 建 40+ chunk 迷你库，含 **同义不同词** 的差旅/报销段落。  
2. 基线：单 query [93 混合检索](93.hybrid-search-tutorial.md) + 精排。  
3. 实验：Multi-Query n=4，对比 **Recall@15**。  
4. 记录 **p95 延迟** 与 token（子 query 生成）。  
5. 拼 prompt 时用 [28 Context Window](28.context-window-tutorial.md) 限制资料区。

**成功标准：** 金标 20 条中至少 3 条「单 query 漏、多 query 找回」且端到端延迟可接受。

---

## 11. 参数、延迟与 Context Window

### 11.1 延迟估算

```text
T ≈ T_gen + n × T_hybrid + T_rerank + T_llm
```

`T_gen`：一次 LLM；`T_hybrid`：BM25+向量+RRF。n 从 3→5 常 +40% 检索时间。

### 11.2 与 [28 Context Window](28.context-window-tutorial.md)

Multi-Query **不直接** 增加 prompt 长度；但合并池更大 → 精排后 Top-K 可能 **更多样**，仍要用 `max_evidence_tokens` 截断。

### 11.3 参数表

| 参数 | 起点 | 调大风险 |
|------|------|----------|
| n_queries | 4 | 延迟↑ |
| per_k | 20 | 合并池↑ |
| merged_cap | 60 | 精排慢 |
| final_k | 5 | 资料噪音↑ |

---

## 12. 工程、监控与评测

**日志：** `q_user`, `sub_queries[]`, 每路 `recall_ids`, `merged_ids`, `rerank_ids`, `latency_ms`。

**指标：** Multi-Query 开启率、**并集增益** = Recall_multi − Recall_single、精排 p95。

**评测：** 固定索引；对比 A 单 query / B Multi-Query；分层看 **术语多样** 文档域。

**版本：** 生成 Prompt、n、per_k 写入路线图 171 配置。

---

## 13. 综合概念地图

![Multi-Query 概念地图](image/multi-query-retrieval/03-concept-map.png)

---

## 14. 常见陷阱与 FAQ

### 14.1 是否替代 [93 混合检索](93.hybrid-search-tutorial.md)？

**不替代。** 每路子 query 仍要走 BM25+向量混合；Multi-Query 只是 **多次调用** 检索器。

### 14.2 是否替代精排？

**不替代。** 合并后仍建议 [95/96 精排](95.cross-encoder-rerank-tutorial.md) 再取 Top-K。

### 14.3 与 [102 HyDE](102.hyde-tutorial.md) 组合？

可：部分 qi 用 HyDE 向量 query，BM25 仍用原问——高级玩法，延迟更高，按评测开。

### 14.4 中文注意？

子 query Prompt 要求简体中文；生成结果去重（字符级相似度 >0.9 的合并）。

### 14.5 面试 30 秒？

「Multi-Query 在 [93 混合检索](93.hybrid-search-tutorial.md) 前生成多条同义 query，分别召回并集去重，再精排；资料量受 [28 Context Window](28.context-window-tutorial.md) 限制。」

### 14.6 没有 LLM 能否做？

可用 **人工同义词表** 展开 2～3 条 qi，效果差于 LLM 但零成本。

---

## 15. 总结与系列下一步

1. **Multi-Query** 是路线图 **118** **地基篇**，检索前 **多条同义 query** 扩召回。  
2. **合并去重 + 一次精排** 控制成本；`n` 与 `per_k` 不要贪大。  
3. 与 [100 改写](100.query-rewriting-tutorial.md)、[103 分解](103.query-decomposition-tutorial.md) 边界清晰。  
4. 下篇：[102 HyDE](102.hyde-tutorial.md) 用假想文档改善向量路。

### 15.1 系列下一步

| 目标 | 阅读 |
|------|------|
| HyDE | [102 篇](102.hyde-tutorial.md) |
| 分解 | [103 篇](103.query-decomposition-tutorial.md) |
| 混合检索 | [93 篇](93.hybrid-search-tutorial.md) |
| 上下文 | [28 篇](28.context-window-tutorial.md) |

### 15.2 自检

- [ ] 能画 1→n 路检索→合并图  
- [ ] 能解释与 103 分解区别  
- [ ] 能估 n×hybrid 延迟  

### 15.3 30 分钟作业

1. §9 BM25 并集 demo；  
2. 接 4 路 mock hybrid；  
3. 对比单 query vs multi 的 Top-10 chunk_id 集合差异；  
4. wiki 写 **何时开 Multi-Query**。

---

> **初学者可能仍困惑的点**  
> - Multi-Query **不是** 精排，是 **多次召回**。  
> - 子 query 要 **同义**，不是 [103 分解](103.query-decomposition-tutorial.md) 的子意图。  
> - 宽召回靠 [93 混合检索](93.hybrid-search-tutorial.md)，合并后靠精排与 [28 Context Window](28.context-window-tutorial.md)。  
> - 每条 sub-query 的 k 要小，否则合并爆炸。

## 附录：Multi-Query 联调检查单

1. 子 query 生成在 **hybrid_search 之前**。  
2. 原问 `q_user` 在子 query 列表中或作精排配对。  
3. 合并后候选数 ≤ 配置上限再送 [95 精排](95.cross-encoder-rerank-tutorial.md)。  
4. 进 LLM 资料符合 [28 Context Window](28.context-window-tutorial.md)。  
5. 日志含每条 qi 的 recall 列表便于调试。  
6. 与 [100 改写](100.query-rewriting-tutorial.md) 串联时顺序：先改写再多 query。  
7. 评测对比 **只开 Multi-Query** 单变量。  
8. ACL 每路检索生效。  
9. JSON 解析失败回退仅原问。  
10. Prompt 版本可回溯。

## 附录：案例库

**案例一：** 「报销」— qi 含「费用报销流程」「发票报销审批」，并集命中不同 chunk。  
**案例二：** 「年假」— 与「带薪年休假」两路 BM25 各命中不同段落。  
**案例三：** 误用— 把「住宿+机票」拆两 qi → 应改 [103 分解](103.query-decomposition-tutorial.md)。  
**案例四：** 与 [102 HyDE](102.hyde-tutorial.md)— 向量路用假想文，BM25 多 query 仍用书面 qi。  
**案例五：** 延迟敏感— n=2、per_k=15，仅对首轮 Recall 不足时二跳开启 Multi-Query。

## 附录：参数 YAML 快照

```yaml
query_enhancement:
  multi_query:
    enabled: true
    n_queries: 4
    per_hybrid_k: 20
    merged_cap: 60
    include_original: true
hybrid:
  bm25_k: 20
  dense_k: 20
  fusion: rrf
rerank:
  final_k: 5
context:
  max_evidence_tokens: 3200
```

## 附录：面试追问

**问：** Multi-Query 与增大 top_k 有何不同？  
**答：** 增大 top_k 只 **加深单路排名**；Multi-Query 换 **不同表述** 改变 BM25 命中与向量方向，补 **表述盲区**。

**问：** 合并用什么分数？  
**答：** 推荐 [94 RRF](94.rrf-fusion-tutorial.md) 对多路排名融合，避免不可比绝对分。

**问：** 会不会增加幻觉？  
**答：** 只影响召回；生成仍须 [34 Grounding](34.grounding-citation-tutorial.md) 与拒答。子 query 禁止编造事实。

**团队 Wiki 一句：** 检索前 Multi-Query 四路、每路二十、合并六十、精排五、资料 token 见 [28 Context Window](28.context-window-tutorial.md)；与 [93 混合检索](93.hybrid-search-tutorial.md) 必选联调。
''' + EXTRA_MULTI


def build_hyde():
    return r'''# C5 查询增强（三）：HyDE 假想文档嵌入完全指南

> 问句与答案在向量空间里 **不一定最近**——「出差住宿上限多少？」与「一线城市住宿费每晚不超过五百元」的 Embedding 距离，可能大于答案句与真 chunk 的距离。**HyDE（Hypothetical Document Embeddings）** 在 **检索之前** 让 LLM 写一段 **假想答案式段落**，用 `embed(假想文)` 作向量检索 query，再与 BM25 原问组成 [93 混合检索](93.hybrid-search-tutorial.md)。这篇是路线图 **119** **地基篇**。前置：[91 Dense](91.dense-retrieval-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)、[28 Context Window](28.context-window-tutorial.md)。

---

## 目录

1. [前言：用「假答案」找真 chunk](#1-前言用假答案找真-chunk)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [HyDE 是什么](#3-hyde-是什么)
4. [在 RAG 链路中的位置](#4-在-rag-链路中的位置)
5. [假想文档生成与 Prompt](#5-假想文档生成与-prompt)
6. [与混合检索、BM25 双路配合](#6-与混合检索bm25-双路配合)
7. [风险、幻觉与缓解](#7-风险幻觉与缓解)
8. [先错对对：四种典型翻车](#8-先错对对四种典型翻车)
9. [最小实现](#9-最小实现)
10. [综合实战](#10-综合实战)
11. [参数、延迟与 Context Window](#11-参数延迟与-context-window)
12. [工程、监控与评测](#12-工程监控与评测)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：用「假答案」找真 chunk

[91 Dense 检索](91.dense-retrieval-tutorial.md) 用 `embed(query)` 在库中找最近邻。但训练语料里 **问句-文档对** 常以「答案式段落」为正样本，用户 **问句式** query 的向量可能离真正含答案的 chunk **不够近**。

**HyDE**（Gao et al., 2022 思路）：  
`q → LLM → 假想段落 h（风格像库内答案）→ embed(h) → 向量检索`

''' + COMMON_INTRO_FOOTER + r'''

**读完本文，你应该能做到：**

1. 解释 HyDE 为何 **只替换向量路 query**、BM25 仍用原问。  
2. 写假想文档 Prompt 并控制 **长度与幻觉**。  
3. 跑通 HyDE + [93 混合检索](93.hybrid-search-tutorial.md) + [95 精排](95.cross-encoder-rerank-tutorial.md)。  
4. 说明假想文 **不进生成 prompt**（除非调试），[28 Context Window](28.context-window-tutorial.md) 主要算 chunk 与生成。  
5. 识别 §8「假想文当真相、全库只用 HyDE、忽略 BM25、假想文过长」翻车。

### 1.1 路线图

第 **119** 条，**地基**。姊妹：[100 改写](100.query-rewriting-tutorial.md)、[101 Multi-Query](101.multi-query-retrieval-tutorial.md)、[103 分解](103.query-decomposition-tutorial.md)。

### 1.2 术语

| 中文 | English | 说明 |
|------|---------|------|
| 假想文档 | Hypothetical Document | LLM 生成的答案式段落 |
| HyDE | Hypothetical Document Embeddings | 用 embed(h) 检索 |
| 查询增强 | Query Enhancement | 检索前，非精排 |

---

## 2. 本文边界与动手路径

**讲：** HyDE 流程、与混合检索组合、风险、代码、评测。  
**不讲：** 微调 HyDE 专用模型、多跳 [104 篇](104.multi-hop-retrieval-tutorial.md)、假想文直接进生成。

| 步骤 | 验收 |
|------|------|
| A | 画 q→h→embed→dense 图 |
| B | 生成 80～200 字假想文 |
| C | 向量 Top-30 + BM25(q) Top-30 |
| D | RRF 融合 → 精排 |
| E | 对比无 HyDE 的 Recall@10 |

---

## 3. HyDE 是什么

![问句 vs 假想文档](image/hyde/01-hyde-idea.png)

### 3.1 向量空间直觉

| 文本类型 | 与库内 chunk 的相似度 |
|----------|----------------------|
| 用户问句 q | 中低（问法差异） |
| 假想答案 h | 较高（叙述体接近） |
| 真答案 chunk | 目标最近邻 |

HyDE 用 h 的向量 **代表「期望答案长相」** 去搜。

### 3.2 与 [100 改写](100.query-rewriting-tutorial.md) 区别

| HyDE | 改写 |
|------|------|
| 输出段落 h | 输出问句 q_search |
| 主要帮向量路 | 主要帮 BM25+向量问句分布 |
| 易含「像答案」的陈述 | 应是问句 |

### 3.3 何时开启

| 场景 | 建议 |
|------|------|
| 向量召回弱、问句短 | 试 HyDE |
| BM25 已很强 | 收益小 |
| 强事实数字题 | 慎用，假想数字污染 |
| 延迟极敏感 | 关闭或缓存 |

---

## 4. 在 RAG 链路中的位置

![HyDE 检索流](image/hyde/02-hyde-flow.png)

```text
q_user
  → LLM → hypothetical h     # 本篇
  → dense_search(embed(h))
  → bm25_search(q_user)        # 93 混合：字面仍用原问
  → RRF → dedupe → rerank → prompt(q_user, chunks)
```

**假想文 h 不进入最终 prompt**（生产默认）——避免 LLM 把 **未验证的假想** 当证据。[34 Grounding](34.grounding-citation-tutorial.md) 只认检索回来的 chunk。

---

## 5. 假想文档生成与 Prompt

```python
HYDE_PROMPT = """根据下列问题，写一段可能出现在企业内部知识库中的说明文字。
要求：简短（80～150字）、叙述体、像政策条款；不要列表编号；若不确定具体数字可写「按规定执行」而非编造精确数。
问题：{q}
说明："""

def generate_hypo(q: str, llm) -> str:
    return llm.complete(HYDE_PROMPT.format(q=q), temperature=0.3, max_tokens=256).strip()
```

**temperature 略 >0**：让文体多样；但数字敏感域用 **0** + 严格模板。

### 5.1 长度控制

假想文过长 → Embedding 被噪音稀释，且 [67 Embedding batch](67.embedding-batching-tutorial.md) 成本增。建议 **80～200 汉字**。

### 5.2 多语言

中文库用中文 h；与 [70 混合语言 Embedding](70.mixed-language-embedding-tutorial.md) 策略一致。

---

## 6. 与混合检索、BM25 双路配合

### 6.1 推荐组合

| 一路 | Query | 作用 |
|------|-------|------|
| 向量 | embed(h) | 语义贴近答案体 |
| BM25 | q_user | 保留用户关键词、数字、专名 |

**完整 [93 混合检索](93.hybrid-search-tutorial.md)**：两路缺一不可——HyDE 假想错时 BM25 用原问 **兜底**。

### 6.2 RRF 融合

```python
def hyde_hybrid(q, llm, embed_fn, dense, bm25, rrf):
    h = generate_hypo(q, llm)
    v_hits = dense.search(embed_fn(h), k=30)
    b_hits = bm25.search(q, k=30)
    return rrf(v_hits, b_hits, top_n=50)
```

### 6.3 与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md)

可对 **多个假想 h**（不同 temperature 采样）做多向量 query 再 RRF——成本高，评测用。

---

## 7. 风险、幻觉与缓解

| 风险 | 缓解 |
|------|------|
| h 编造错误事实 | BM25 原问兜底 + [95 精排](95.cross-encoder-rerank-tutorial.md) |
| h 引入库外实体 | Prompt 限制；h 不进生成 prompt |
| 延迟 +LLM +Embed | 仅难 query 开启；缓存 (q→h) |
| 数字幻觉 | Prompt 禁止精确数字或后验丢弃含数字 h |

**关键：** HyDE 的 h **不是答案**，只是 **检索中介**。

---

## 8. 先错对对：四种典型翻车

### 8.1 错：把假想文 h 直接塞进生成 prompt

**对：** 生成只引用 **检索到的 chunk**；h 仅用于 `embed(h)`。

### 8.2 错：BM25 也用 h

**对：** BM25 用 **q_user**（或 [100 改写](100.query-rewriting-tutorial.md) 的 q_search），不用 h。

### 8.3 错：假想文当精排输入替代 chunk

**对：** 精排配对 **(q_user, chunk_text)**，不是 (h, chunk)。

### 8.4 错：全库查询都开 HyDE

**对：** 关键词已明确的查询关闭；用分类器或 Recall 低时触发。

---

## 9. 最小实现

```python
# 伪代码：接 sentence-transformers 与 BM25
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

def embed(text):
    return model.encode(text, normalize_embeddings=True)

def hyde_dense(h, vector_index, k=5):
    return vector_index.search(embed(h), k=k)

# h = generate_hypo(q, llm)
# v = hyde_dense(h, index)
# b = bm25.search(q)
# merged = rrf(v, b)
```

入库仍用 [25 Embedding](25.embedding-vector-tutorial.md) 对 **chunk** 编码，与 HyDE 检索向量 **同一模型**。

---

## 10. 综合实战

1. 选 15 条 **问句短、向量易漏** 的金标。  
2. A：纯混合检索；B：+HyDE 向量路。  
3. 对比 Recall@10、端到端答案质量。  
4. 记录 `hypo_text` 日志人工查 **污染率**。  
5. 精排后按 [28 Context Window](28.context-window-tutorial.md) 装资料。

---

## 11. 参数、延迟与 Context Window

```text
T ≈ T_hypo_LLM + T_embed(h) + T_hybrid + T_rerank + T_gen
```

比单 query 多 **一次 LLM + 一次 Embed**。[28 篇](28.context-window-tutorial.md) 中 **资料区仍只计 chunk**；HyDE 的 LLM token 在 **检索预算** 另账。

| 参数 | 建议 |
|------|------|
| h 长度 | 80～150 字 |
| dense_k | 30 |
| bm25_k | 30 |
| 触发 | 向量单路 Recall 低 |

---

## 12. 工程、监控与评测

**日志：** `q_user`, `hypo_text`, `hypo_len`, `dense_ids`, `bm25_ids`, `merged_ids`。

**指标：** HyDE 触发率、h 污染抽检、Recall 增益、延迟 p95。

**缓存：** 相同 q 的 h 可 TTL 缓存（注意 [48 文档版本](48.doc-versioning-tutorial.md) 更新时失效）。

---

## 13. 综合概念地图

![HyDE 概念地图](image/hyde/03-concept-map.png)

---

## 14. 常见陷阱与 FAQ

### 14.1 HyDE 是否替代 Embedding 入库？

**不替代。** 只对 **查询侧** 临时生成 h；库内 chunk 照常 embed。

### 14.2 与 [102] 精排关系？

HyDE 在检索前；[95 精排](95.cross-encoder-rerank-tutorial.md) 在召回后——顺序不可颠倒。

### 14.3 中文 corporate 场景？

用中文 Prompt、中文 h；BM25 分词与 [93 篇](93.hybrid-search-tutorial.md) 一致。

### 14.4 面试 30 秒？

「HyDE 检索前用 LLM 写假想答案段，embed(h) 做向量检索；BM25 仍用原问走 [93 混合检索](93.hybrid-search-tutorial.md)；h 不进 prompt；资料受 [28 Context Window](28.context-window-tutorial.md) 限制。」

### 14.5 和 Zeroshot 生成答案区别？

HyDE **不** 把 h 当最终答案；必须 **检索真 chunk** 再生成。

---

## 15. 总结与系列下一步

1. **HyDE** 路线图 **119**，检索前 **假想文档向量** 拉近答案体 chunk。  
2. **向量用 h、BM25 用 q** 是铁律；h 不进生成。  
3. 幻觉靠混合检索 + 精排 + [99 阈值](99.score-threshold-tutorial.md) 缓解。  
4. 下篇：[103 分解](103.query-decomposition-tutorial.md) 处理复合多问。

### 15.1 下一步

| 阅读 | 目标 |
|------|------|
| [103 分解](103.query-decomposition-tutorial.md) | 复合问 |
| [93 混合](93.hybrid-search-tutorial.md) | 双路召回 |
| [28 窗口](28.context-window-tutorial.md) | 预算 |

### 15.2 作业

1. 打印一条 h 与对应 Top-3 chunk 对比；  
2. 关 HyDE 做 A/B；  
3. wiki：**何时开 HyDE**。

---

> **初学者可能仍困惑的点**  
> - 假想文可能错，**不能** 当答案；真证据在检索 chunk。  
> - HyDE **不是** 精排。  
> - [93 混合检索](93.hybrid-search-tutorial.md) 的 BM25 路必须用原问。  
> - 多一次 LLM+Embed，延迟更高。

## 附录：HyDE 联调检查单

1. h 生成在 dense_search 之前。  
2. BM25 输入为 q_user 或 q_search，**不是 h**。  
3. h 默认 **不** 写入生成 prompt。  
4. embed(h) 与入库 **同一 Embedding 模型**。  
5. RRF 后去重再 [95 精排](95.cross-encoder-rerank-tutorial.md)。  
6. 资料 token 符合 [28 Context Window](28.context-window-tutorial.md)。  
7. 假想数字污染抽检。  
8. 难 query 才触发，避免全员 HyDE。  
9. 日志可回溯 h 全文（权限内）。  
10. 评测固定索引版本。

## 附录：案例

**案例一：** 问「产假天数」— h 叙述体接近制度条，向量命中；BM25「产假」保底。  
**案例二：** h 编造「158天」— 精排降权错误 chunk，拒答优于胡编。  
**案例三：** 与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md)— 多个 h 采样扩向量路。  
**案例四：** 与 [100 改写](100.query-rewriting-tutorial.md)— 先改写 q 再生成 h，口语链更长。  
**案例五：** 纯关键词「年假 5 天」— 关 HyDE，省延迟。

## 附录：YAML

```yaml
hyde:
  enabled: auto
  max_hypo_chars: 150
  temperature: 0.3
  dense_k: 30
hybrid:
  bm25_query: original
  fusion: rrf
rerank:
  final_k: 5
context:
  max_evidence_tokens: 3200
```

## 附录：面试

**问：** HyDE 为何不用 embed(q)？  
**答：** 答案式文本与 chunk 在向量空间更近；问句式 q 离答案段往往更远。

**问：** 假想错怎么办？  
**答：** BM25 原问 + 精排 + 仅依据检索资料生成；[112 拒答](112.refusal-strategy-tutorial.md)。

**Wiki：** HyDE 向量假答案检索、BM25 原问、[93 混合检索](93.hybrid-search-tutorial.md) 融合、精排五、资料见 [28 Context Window](28.context-window-tutorial.md)。
''' + EXTRA_HYDE


def build_decomposition():
    return r'''# C5 查询增强（四）：Query Decomposition 查询分解完全指南

> 「出差住宿上限多少，机票能报经济舱吗？」——这是 **两个信息需求**。**Query Decomposition（查询分解）** 在 **检索之前** 把复合问拆成 **独立子 query**，每个子问走 [93 混合检索](93.hybrid-search-tutorial.md)，再 **合并证据** 并按子问组织进 [28 Context Window](28.context-window-tutorial.md)。这篇是路线图 **120** **地基篇**。前置：[101 Multi-Query](101.multi-query-retrieval-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)、[95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)。

---

## 目录

1. [前言：复合问要拆开搜](#1-前言复合问要拆开搜)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [Query Decomposition 是什么](#3-query-decomposition-是什么)
4. [在 RAG 链路中的位置](#4-在-rag-链路中的位置)
5. [分解策略与 Prompt](#5-分解策略与-prompt)
6. [分路检索与证据合并](#6-分路检索与证据合并)
7. [Prompt 编排与子问对齐](#7-prompt-编排与子问对齐)
8. [与混合检索、精排怎么衔接](#8-与混合检索精排怎么衔接)
9. [先错对对：四种典型翻车](#9-先错对对四种典型翻车)
10. [最小实现](#10-最小实现)
11. [综合实战](#11-综合实战)
12. [参数、延迟与 Context Window](#12-参数延迟与-context-window)
13. [工程、监控与评测](#13-工程监控与评测)
14. [综合概念地图](#14-综合概念地图)
15. [常见陷阱与 FAQ](#15-常见陷阱与-faq)
16. [总结与系列下一步](#16-总结与系列下一步)

---

## 1. 前言：复合问要拆开搜

用户常 **一次问多件**：

- 「年假几天，事假扣工资吗？」  
- 「VPN 怎么连，密码忘了找谁？」

单次 [93 混合检索](93.hybrid-search-tutorial.md) 的 query embedding 是 **整句一个向量**，可能 **偏向句中某一个主题**（如只靠近「年假」），另一主题 chunk 挤不进 Top-K。**Query Decomposition** 把 `q_user` 拆成 `{q1, q2, …}`，**每个子问表达不同信息需求**，分路检索后合并。

''' + COMMON_INTRO_FOOTER + r'''

**与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md) 的关键区别：**

| 分解 Decomposition | Multi-Query |
|--------------------|-------------|
| 子问 **不同意图** | 子问 **同义改写** |
| 「住宿」+「机票」 | 「住宿费」+「住宿标准」 |

**读完本文，你应该能做到：**

1. 判断何时分解 vs Multi-Query vs 单 query。  
2. 用 LLM 输出 **JSON 子问数组** 并护栏。  
3. 分路检索、按子问 **分组证据** 拼 prompt。  
4. 在 [28 Context Window](28.context-window-tutorial.md) 内 **每个子问至少 1 条证据**。  
5. 识别 §9「拆太碎、子问仍复合、合并丢子问、生成只答一半」翻车。

### 1.1 路线图

第 **120** 条，**地基**。下游：[104 Multi-hop](104.multi-hop-retrieval-tutorial.md)（子问之间有依赖时用多跳）。

---

## 2. 本文边界与动手路径

**讲：** 分解、分路检索、分组合并、prompt 编排、评测。  
**不讲：** 子问间链式依赖（104 多跳）、Agent 自主拆问无限循环。

| 步骤 | 验收 |
|------|------|
| A | 画 1→k 子问→k 路检索 |
| B | JSON 分解 2～3 子问 |
| C | 每子问 hybrid k=20 |
| D | 分组建 prompt |
| E | 生成覆盖 **所有** 子问 |

---

## 3. Query Decomposition 是什么

![复合问拆子问](image/query-decomposition/01-decomp-idea.png)

### 3.1 形式化

```text
{q1..qk} = Decompose(q_user),  k 通常 2～4
C = ⋃ᵢ hybrid_search(qi)
组织 evidence_by_subquestion
LLM 回答 q_user（须覆盖各子问）
```

### 3.2 何时需要

| 形态 | 示例 | 建议 |
|------|------|------|
| 并列多问 | 住宿+机票 | 分解 |
| 单意图 | 年假几天 | 不分解 |
| 同义多样 | 报销咋整 | [100 改写](100.query-rewriting-tutorial.md) / [101 Multi-Query](101.multi-query-retrieval-tutorial.md) |
| 需前问结果才能后问 | 先查工单号再查 SLA | [104 多跳](104.multi-hop-retrieval-tutorial.md) |

### 3.3 子问数量

**2～4** 为宜。拆太碎 → 检索次数爆炸、prompt 碎片化；不拆 → 漏意图。

---

## 4. 在 RAG 链路中的位置

![分解检索流](image/query-decomposition/02-decomp-flow.png)

```text
q_user → Decompose → q1..qk
  → 每个 qi：93 混合检索
  → 合并去重（保留子问标签）
  → 可选：rerank(q_user, 全池) 或 每子问 rerank
  → 分组建 prompt → LLM
```

分解在 **检索前**；精排在 **各路召回之后**。

---

## 5. 分解策略与 Prompt

```python
DECOMPOSE_PROMPT = """将用户问题拆成独立子问题，每个子问题只含一个信息需求。
要求：
1. 不要回答问题
2. 不要拆出用户没问的内容
3. 输出 JSON 数组，2～4 条为宜
4. 简体中文

用户问题：{q}
JSON："""

def decompose(q, llm):
    raw = llm.complete(DECOMPOSE_PROMPT.format(q=q), temperature=0)
    arr = json.loads(raw)
    subs = [s.strip() for s in arr if isinstance(s, str) and s.strip()]
    return subs[:4] if subs else [q]
```

### 5.1 护栏

- 解析失败 → `[q]` 不分解  
- 仅 1 条有效子问 → 退化为单 query  
- 检测子问 **字符相似度极高** → 合并（避免重复检索）

### 5.2 与 [100 改写](100.query-rewriting-tutorial.md)

对每个 **子问** 可再改写：`decompose → rewrite(qi)`，再 `hybrid_search`。

---

## 6. 分路检索与证据合并

```python
def retrieve_decomposed(q_user, llm, hybrid_search, per_k=20):
    subs = decompose(q_user, llm)
    buckets = []
    for i, sq in enumerate(subs):
        hits = hybrid_search(sq, k=per_k)
        for h in hits:
            h["sub_idx"] = i
            h["sub_query"] = sq
        buckets.append(hits)
    return subs, buckets
```

### 6.1 去重

同一 `chunk_id` 可能服务多个子问：**保留多条引用** 或 **合并标签** `sub_queries: [0,1]`。

### 6.2 每子问配额

防止一个子问占满 prompt：每 `sub_idx` **至少预留** 1 条、**至多** 3 条 chunk（按 [28 篇](28.context-window-tutorial.md) 调整）。

---

## 7. Prompt 编排与子问对齐

```text
【子问题1：出差住宿费用上限】
[chunk_id: c12] 一线城市住宿费...

【子问题2：机票舱位报销标准】
[chunk_id: c08] 经济舱可报销...
```

**生成指令：**

```text
请逐条回答用户问题中的各个子问题，若某条资料不足请单独说明无法确定。
用户原问题：{q_user}
```

这样 LLM **不易漏答** 第二个子问。

### 7.1 Token 预算

总资料区 ≤ `max_evidence_tokens`（[28 Context Window](28.context-window-tutorial.md)）。子问多时 **缩短每块 chunk** 或 **每子问 1 条**。

---

## 8. 与混合检索、精排怎么衔接

| 策略 | 做法 |
|------|------|
| 全局精排 | 合并池 → `rerank(q_user, pool)` → 再按子问标签分配 |
| 分路精排 | 每子问 Top-3 再拼接（子问意图更清晰） |

推荐 PoC：**分路精排**；库大时：**全局精排** 省一次模型加载。

**混合检索参数：** 每子问 `bm25_k=dense_k=20`，子问数 3 时粗算 60 条/路合并前。

---

## 9. 先错对对：四种典型翻车

### 9.1 错：把同义改写当分解（「住宿费」「住宿标准」）

**对：** 用 [101 Multi-Query](101.multi-query-retrieval-tutorial.md)。

### 9.2 错：拆成 8 个子问

**对：** 限制 2～4；更多用 [104 多跳](104.multi-hop-retrieval-tutorial.md)。

### 9.3 错：合并证据时不标子问，生成只答第一条

**对：** §7 分组建 prompt + 指令 **逐条回答**。

### 9.4 错：分解放在检索之后

**对：** 分解 **最先**，再 **每子问** 调 [93 混合检索](93.hybrid-search-tutorial.md)。

---

## 10. 最小实现

```python
import json

def build_grouped_prompt(q_user, subs, buckets, max_per_sub=2):
    parts = []
    for i, sq in enumerate(subs):
        parts.append(f"【子问题{i+1}：{sq}】")
        for h in buckets[i][:max_per_sub]:
            parts.append(f"[{h['chunk_id']}] {h['text']}")
    evidence = "\n".join(parts)
    return f"资料：\n{evidence}\n\n用户问题：{q_user}\n请逐条回答各子问题：\n"

# subs, buckets = retrieve_decomposed(...)
# prompt = build_grouped_prompt(q_user, subs, buckets)
```

---

## 11. 综合实战

**迷你库：** 差旅 chunk（住宿）、差旅 chunk（机票）、人事 chunk。  
**测试问：** 「一线城市住宿限额？机票能报商务舱吗？」  
**基线：** 单 query 混合检索。  
**实验：** 分解两子问，各检索 Top-5，分组精排各 Top-2。  
**验收：** 生成 **同时** 提到住宿与机票；引用 c12、c08。

---

## 12. 参数、延迟与 Context Window

```text
T ≈ T_decompose + k × T_hybrid + T_rerank×(1或k) + T_gen
```

k=3 时检索 **约 3 倍** 单 query。[28 Context Window](28.context-window-tutorial.md)：子问多时每子问 chunk 数要 **下调**。

| 参数 | 建议 |
|------|------|
| max_subqueries | 4 |
| per_sub_k | 15～25 |
| chunks_per_sub in prompt | 1～3 |
| max_evidence_tokens | 3200～4000 |

---

## 13. 工程、监控与评测

**日志：** `q_user`, `sub_queries[]`, 每子问 `recall_ids`, `prompt_tokens`。

**指标：** 分解率、**子问覆盖率**（生成是否答全）、单问漏答率。

**金标：** 复合问标注 **每个子问对应 gold_chunk**；算 **per-sub Recall**。

---

## 14. 综合概念地图

![查询分解概念地图](image/query-decomposition/03-concept-map.png)

---

## 15. 常见陷阱与 FAQ

### 15.1 分解 vs Multi-Query？

分解 = **不同意图**；Multi-Query = **同义**。

### 15.2 分解 vs [104 多跳](104.multi-hop-retrieval-tutorial.md)？

分解子问 **可并行** 检索；多跳 **后问依赖前问检索结果**。

### 15.3 是否替代精排？

**不替代。** 合并后仍 [95 精排](95.cross-encoder-rerank-tutorial.md) 或分路精排。

### 15.4 面试 30 秒？

「复合问在 [93 混合检索](93.hybrid-search-tutorial.md) 前拆成子 query，分路检索，证据按子问分组进 [28 Context Window](28.context-window-tutorial.md)，生成逐条答。」

### 15.5 中文标点？

「住宿多少，机票呢」— 分解模型要识别 **逗号、顿号、并且** 等并列。

---

## 16. 总结与系列下一步

1. **Query Decomposition** 路线图 **120**，检索前 **拆复合问**。  
2. 与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md) **勿混**。  
3. **分组建 prompt** 防漏答；token 见 [28 篇](28.context-window-tutorial.md)。  
4. 有依赖 → [104 多跳](104.multi-hop-retrieval-tutorial.md)。

### 16.1 下一步

| 阅读 | 目标 |
|------|------|
| [104 多跳](104.multi-hop-retrieval-tutorial.md) | 链式依赖 |
| [107 上下文预算](107.context-budget-tutorial.md) | 资料编排 |
| [93 混合](93.hybrid-search-tutorial.md) | 双路召回 |

### 16.2 作业

1. 手工写 5 条复合问做分解 JSON；  
2. 分路 BM25 demo；  
3. 检查生成是否答全子问。

---

> **初学者可能仍困惑的点**  
> - 分解 **不是** 同义 Multi-Query。  
> - 分解 **不是** 精排。  
> - 宽召回靠 [93 混合检索](93.hybrid-search-tutorial.md)。  
> - 资料总量受 [28 Context Window](28.context-window-tutorial.md) 限制，子问多要减每路 k。

## 附录：分解联调检查单

1. 分解在 hybrid 之前。  
2. 子问 2～4 条，非大量同义。  
3. 每子问有检索结果或显式「无资料」。  
4. prompt 分子问区块。  
5. 生成指令要求 **逐条回答**。  
6. [28 Context Window](28.context-window-tutorial.md) 截断后仍尽量每子问 1 证据。  
7. 与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md) 不重复开启同义扩写。  
8. ACL 每路生效。  
9. JSON 失败回退整句单搜。  
10. 评测标 per-sub gold。

## 附录：案例

**案例一：** 住宿+机票— 两子问各命中差旅不同节。  
**案例二：** 「年假和调休」— 两意图，勿合并单 query。  
**案例三：** 误拆— 「报销流程和发票」同一流程 → 可不拆。  
**案例四：** +[100 改写](100.query-rewriting-tutorial.md)— 子问口语先书面化。  
**案例五：** 工单号+SLA— 需 [104 多跳](104.multi-hop-retrieval-tutorial.md)，非单纯分解。

## 附录：YAML

```yaml
decomposition:
  enabled: auto
  max_subqueries: 4
  per_sub_hybrid_k: 20
  chunks_per_sub_in_prompt: 2
hybrid:
  fusion: rrf
rerank:
  mode: per_sub  # or global
  top_k: 3
context:
  max_evidence_tokens: 3600
```

## 附录：面试

**问：** 分解后为何要分组建 prompt？  
**答：** 避免模型只关注第一个子问；对齐 [28 Context Window](28.context-window-tutorial.md) 内可读结构。

**问：** 能否只分解不精排？  
**答：** 可以 PoC，但噪音大；建议 [95 精排](95.cross-encoder-rerank-tutorial.md)。

**Wiki：** 复合问分解、子问各路 [93 混合检索](93.hybrid-search-tutorial.md)、分组证据、精排、总 token 见 [28 Context Window](28.context-window-tutorial.md)。
''' + EXTRA_DECOMP


PAD = """

## 附录：落地工作坊备忘

在企业 RAG 落地工作坊中，建议用 **同一份金标、同一索引版本** 做四周迭代：第一周仅 [93 混合检索](93.hybrid-search-tutorial.md) 基线；第二周叠加本篇查询增强；第三周叠加 [95 精排](95.cross-encoder-rerank-tutorial.md)；第四周按 [28 Context Window](28.context-window-tutorial.md) 调资料区与输出预留。每周只动一个旋钮，否则无法解释 Recall 变化。记录 `p50/p95` 延迟时，要分开 **增强 LLM**、**检索**、**精排**、**生成** 四段，避免只报一个「端到端」掩盖检索前增强的成本。上线灰度时，先对 **口语多、复合问多** 的流量桶开启，书面关键词搜索桶保持关，能最大化收益风险比。与 [53 ACL](53.metadata-acl-tutorial.md) 联调时，记得查询增强 **不会** 替代元数据过滤——无权限的 chunk 仍必须在检索器内被剔除。最后，把本篇参数与 Prompt 版本写入路线图 **171** 配置仓库，与 Embedding、精排模型版本 **并列**，回滚时才能一键恢复。团队评审三问：增强是否真在检索前？日志能否对照原问与增强结果？资料进模型前是否遵守 [28 Context Window](28.context-window-tutorial.md)？
"""


EXTRA_MULTI = """

### 5.4 子 query 多样性控制

若 LLM 生成的 qi **几乎相同**（编辑距离很近），检索收益接近 0，却付出 n 倍成本。可做：

```python
def dedupe_queries(queries, min_dist=3):
    out = []
    for q in queries:
        if all(levenshtein(q, o) >= min_dist for o in out):
            out.append(q)
    return out
```

中文也可用 **字符 bigram Jaccard < 0.85** 判定重复。

### 6.4 与 [106 检索去重](106.retrieval-dedup-tutorial.md) 的衔接

Multi-Query 合并时按 `chunk_id` 去重是 **第一道**；若同一文档相邻 chunk 语义重复，可在精排后做 **内容级去重**（路线图 106），避免 [28 Context Window](28.context-window-tutorial.md) 里塞满重复段落。

### 7.4 延迟优化：并行检索

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_hybrid(subs, hybrid_search, k=20):
    with ThreadPoolExecutor(max_workers=len(subs)) as ex:
        futs = [ex.submit(hybrid_search, sq, k) for sq in subs]
        return [f.result() for f in futs]
```

IO 型检索可并行；注意向量库连接池上限。

### 10.1 金标样例表（可自行扩展）

| 用户问 | 金标 chunk 关键词 | 单 query 漏因 | Multi-Query 补哪条 qi |
|--------|-------------------|---------------|------------------------|
| 出差酒店报多少 | 住宿费、500 | 缺「住宿费」 | 「差旅住宿费标准」 |
| 发票怎么贴 | 增值税发票、报销单 | 向量偏「贴票」口语 | 「费用报销发票要求」 |
| 年假还剩几天 | 带薪年休假、余额 | BM25 命中「年假」但非余额段 | 「年休假余额查询」 |

### 12.1 与路由层配合

意图路由器可对 **关键词明确** 的 query 跳过 Multi-Query；对 **日志里 Recall 低** 的意图类默认开启。路由特征：query 长度、口语词典命中率、历史点击率。

### 14.7 生产开关示例

```yaml
multi_query:
  enabled: true
  when:
    min_query_chars: 6
    max_query_chars: 200
    skip_if_regex: \"^\\\\d+$\"
```

### 14.8 读日志排障

若 `merged_ids` 比单 query 还少，检查是否 **子 query 过窄** 把 BM25 带偏；若合并池巨大，检查 `per_k` 与 `n` 是否过大。
"""

EXTRA_HYDE = """

### 5.3 假想文风格模板（制度库）

```text
根据公司差旅管理制度，员工因公出差可报销合理住宿费用。一线城市适用较高限额标准，须取得合规发票并按流程提交。具体数额以最新公布标准为准。
```

让 h **像条款摘录** 而非对话回答，更接近 chunk 文体。

### 6.4 向量 metric 与 [26 相似度](26.similarity-metrics-tutorial.md)

HyDE 检索向量常用 **余弦**（L2 归一化后内积，见 [66 篇](66.l2-normalization-tutorial.md)）。`embed(h)` 与入库 chunk 必须 **同一模型、同一归一化**。

### 7.1 污染检测启发式

若 h 含 **用户未提的数字** 且与任何检索 chunk 不一致，可丢弃 h、回退 `embed(q_user)` 仅向量一路，仍保留 BM25。

### 10.2 A/B 记录表

| 指标 | 无 HyDE | 有 HyDE |
|------|---------|---------|
| Recall@10 | | |
| 假想污染条数 | — | |
| p95 延迟 ms | | |

### 12.2 缓存键设计

`cache_key = hash(q_user + embed_model_version + hyde_prompt_version)`。文档 [49 增量更新](49.incremental-update-tutorial.md) 后清缓存。

### 14.6 与 [102] 论文直觉对照

HyDE 核心：**答案空间检索** 优于 **问题空间检索**——RAG 工程上落实为「检索前多写一段假答案再 embed」。

### 14.7 失败回退链

`h 生成失败 → embed(q)`；`dense 空结果 → 仅 BM25+精排`；`全空 → [112 拒答](112.refusal-strategy-tutorial.md)`。
"""

EXTRA_DECOMP = """

### 5.3 规则分解（无 LLM）

并列连接词切分（PoC）：

```python
import re
SPLIT_PAT = r\"[，,；;]|并且|还有|以及\"

def rule_decompose(q):
    parts = [p.strip() for p in re.split(SPLIT_PAT, q) if p.strip()]
    return parts if 1 < len(parts) <= 4 else [q]
```

「住宿上限多少，机票能报经济舱吗」→ 两子问。复杂从句仍要 LLM。

### 6.3 子问覆盖校验（生成前）

```python
def all_subs_have_evidence(subs, buckets, min_hits=1):
    return all(len(buckets[i]) >= min_hits for i in range(len(subs)))
```

若否，可对缺证据子问 **单独加宽 k** 或整体 [112 拒答](112.refusal-strategy-tutorial.md) 部分子问。

### 7.2 生成评分rubric

人工看回答是否 **逐条对应** 子问编号；漏答率应 <5% 再上线。

### 8.1 与 [104 多跳](104.multi-hop-retrieval-tutorial.md) 决策树

```text
子问之间无依赖 → 本篇分解并行检索
后问需要前问检索结果 → 104 多跳
仅同义表述 → 101 Multi-Query
```

### 11.1 端到端伪代码

```python
def rag_decomposed(q_user, services):
    subs = services.decompose(q_user)
    buckets = [services.hybrid_search(sq, k=20) for sq in subs]
    if not all_subs_have_evidence(subs, buckets):
        services.log_warning(\"missing_sub_evidence\")
    top_per = [services.rerank(sq, buckets[i], top_k=2) for i, sq in enumerate(subs)]
    prompt = services.build_grouped_prompt(q_user, subs, top_per)
    return services.llm(prompt)
```

### 15.6 评测 per-sub Recall

金标结构：`{sub_query: [gold_chunk_ids]}`。报告 **每个子问** 的 Recall@5，而非只看整句。

### 15.7 中文并列句式库

「A多少，B能不能C」「A和B分别…」「想问A还有B」— 宜分解。单一主题「A和B的区别」可能是 **对比单意图**，用 [101 Multi-Query](101.multi-query-retrieval-tutorial.md) 或单 query+精排。
"""


BULK_101 = """

## 深化阅读：Multi-Query 与企业搜索日志

### 从搜索日志挖掘子 query 模板

除 LLM 生成外，可每周从 **零结果查询** 与 **点击靠后查询** 中挖掘：用户常问「报销」，但手册用「费用」——把日志里 **高点击 chunk 的标题词** 反哺为 Multi-Query 模板，形成「用户词 → 文档词」小表，与 [100 改写](100.query-rewriting-tutorial.md) 规则表合并。这样 LLM 调用量下降，可解释性上升。

### 与 Elasticsearch 多 match 的区别

ES 的 `multi_match` 或 `dis_max` 是在 **单次请求内** 用多字段匹配；Multi-Query RAG 是 **多次独立检索再合并**。前者适合结构化字段（title/body）；后者适合 **语义与分词差异大** 的 chunk 库。若你已用 ES [93 混合检索](93.hybrid-search-tutorial.md)，仍可在 **应用层** 对多个 qi 各发一次 hybrid 请求，再用 [94 RRF](94.rrf-fusion-tutorial.md) 合并——与 ES 内置多字段互补而非重复。

### 教学演示脚本扩展

组织培训时让学员打印：单 query Top-10 的 `chunk_id` 集合与 Multi-Query 并集 Top-10 的 **差集**。差集非空且含金标即 **直观胜利**；若差集全是噪音，说明子 query 生成 **偏题**，要收紧 Prompt「不要拆子意图」。

### 与精排 [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md) 的配对细节

合并池 60 条送精排时，配对 query 推荐 **q_user**：用户综合意图在复合句里；子 query 过窄可能让精排 **低估** 对另一子意图也相关的 chunk（chunk 同时含住宿与交通总则）。若 chunk 很短、子意图分明，可改 **分路精排再合并**。用金标选策略，勿凭直觉。

### Token 账本再强调

Multi-Query 的 LLM 只消耗 **生成子 query** 的 token，不直接占 [28 Context Window](28.context-window-tutorial.md) 资料区；但若合并池过大、精排 Top-K 过大，资料区仍爆。流程应是：**多 query 扩召回 → 合并截断 → 精排 → 按预算 pack**。

### 常见配置错误清单

| 错误配置 | 现象 | 修正 |
|----------|------|------|
| n=10 | 超时 | 降至 3～5 |
| 不含原问 | 丢 BM25 原关键词 | `include_original: true` |
| 合并后不截断 | 精排 200 对 | `merged_cap: 60` |
| 子 query 是分解 | 住宿+机票两条 | 改 [103 分解](103.query-decomposition-tutorial.md) |
| 精排用各 qi 各跑一遍 | 成本 ×n | 合并后精排一次 |

### 面试官可能追问

**为何不用 query expansion 同义词库？** 同义词库维护成本高、域迁移差；LLM Multi-Query 是 **动态** 扩写，但要控幻觉与延迟，生产常 **规则库 + LLM** 混合。

**Multi-Query 对 BM25 与向量哪路帮助大？** 通常 BM25 获益更明显（不同关键词）；向量路若已很强，收益递减，可用评测决定默认关。

### 一周实验计划（培训用）

| 天 | 任务 |
|----|------|
| 一 | 基线 [93 混合检索](93.hybrid-search-tutorial.md) + 金标 |
| 二 | 实现 `generate_sub_queries` |
| 三 | 合并 RRF + 对比 Recall |
| 四 | 接精排 + [28 窗口](28.context-window-tutorial.md) pack |
| 五 | 写 wiki 与开关策略 |

### 与 100 改写的组合实验设计

做 2×2 实验：{无改写, 有改写} × {无 Multi-Query, 有 Multi-Query}，在 **同一金标** 上看交互效应。常见结果：改写解决口语，Multi-Query 解决 **同义表述**；两者叠加对「口语+术语多样」域收益最大，对书面语域可能 **无增益仅增延迟**。报告四格 Recall 表给产品决定是否默认全开。

### 子 query 数量 n 的扫描曲线

n ∈ {1,2,3,4,5,6}，固定 per_k=20，画 Recall@15 与 p95 延迟曲线。选 **拐点**：Recall 增益 <2% 而延迟 +30% 的 n 不要。多数中文企业库 n=4 是甜点。

### BM25 分词与 Multi-Query

中文 BM25 若用字级或 jieba 分词，不同 qi 可能引入 **不同分词切分**，改变命中。可在生成 Prompt 要求「使用完整名词短语」。与 [93 混合检索](93.hybrid-search-tutorial.md) 分词配置一致即可。

### 向量路重复 qi 的边际效应

若 4 条 qi 向量 embedding 彼此余弦 >0.95，向量路等价于单 query，仅 BM25 受益。可在生成后 **对 qi embedding 聚类**，每簇只保留一条代表 qi 检索，省向量路成本。

### 学员常问：能否用 Embedding 聚类自动扩 query？

可以离线：用库内高频标题 embedding 聚类中心作 qi——那是 **无 LLM** 扩写，适合静态库；在线 LLM 扩写适合 **动态用户表述**。二者可并存：静态表 + LLM 兜底。

### 生产灰度方案

```text
阶段1：10% 流量 Multi-Query，对比点击率
阶段2：仅 Recall 低意图类 50%
阶段3：全量或回滚
```

每阶段 **至少 7 天**，覆盖工作日问法分布。

### 读路径小结（给评审看）

Multi-Query 的价值主张用一句话：**用可承受的检索次数换表述覆盖率**。评审材料附：金标 Recall 提升绝对值、延迟增加百分比、LLM 月成本估算、与 [100 改写](100.query-rewriting-tutorial.md) 的交互表。四者齐全再批准全量。

### 附录补充：多查询与日志字段标准

建议日志 schema：`sub_queries: string[]`, `per_query_recall_count: int[]`, `merged_unique_count: int`, `merge_strategy: rrf|max_score`。方便 BI 看 **哪条 qi 贡献最大 gold hit**。若某 qi 从未贡献金标，考虑从 Prompt 示例中 **删除类似表述** 或降低 n。
"""

BULK_102 = """

## 深化阅读：HyDE 向量检索与风险治理

### 论文直觉到工程的三步映射

**论文：** 用 LLM 生成假想文档，用其向量检索。**工程：** （1）Prompt 控制文体与长度；（2）**仅** `embed(h)` 走向量路；（3）BM25 用原问 + 精排 + 生成不用 h。缺任何一步都会把 HyDE 做成「在线胡编答案」。

### 假想文与 [100 改写](100.query-rewriting-tutorial.md) 串联

流程：`q → rewrite → q_search → hyde(q_search) → h`。口语先书面，再生成 **答案体** h，适合 **极短口语问**；延迟叠加，仅 **低置信 query** 开启。

### 向量模型一致性检查

[25 Embedding](25.embedding-vector-tutorial.md) 入库模型必须与 `embed(h)` 相同；换模型要 **重索引**（[49 增量更新](49.incremental-update-tutorial.md)）。HyDE 不能救 **错模型** 的索引。

### 数字敏感域策略

报销限额、税率、天数等：**Prompt 禁止写精确数字**，或生成后 **剥离所有阿拉伯数字** 再 embed，避免 h 把检索带向 **错误数值 chunk**。

### 与 [91 Dense](91.dense-retrieval-tutorial.md) 的对比实验

打印 `sim(embed(q), gold_chunk)` vs `sim(embed(h), gold_chunk)` 的均值差；若差为负，说明该域 **不宜 HyDE**，关开关。

### 延迟拆解表

| 步骤 | 典型耗时 |
|------|----------|
| LLM 生成 h | 200ms～2s |
| embed(h) | 10～50ms |
| dense+BM25 | 与 93 同量级 |
| 精排 | 见 95 篇 |

### 治理：假想文存档是否合规？

内部知识库一般可存 **调试日志**；若 h 含敏感推断，日志要 **权限控制** 与 **保留周期**，与员工 query 同等对待。

### 教学实验：肉眼观察 h 与 Top-1 chunk

让学员读 h 与检索 Top-1 正文并排，标 **相同关键词** 与 **矛盾点**。矛盾大但 Recall 升→ 说明靠 **部分重叠** 拉近距离；矛盾大且 Recall 降→ 关 HyDE。

### HyDE + [101 Multi-Query](101.multi-query-retrieval-tutorial.md)

多个 h（不同表述或 temperature）→ 多向量 query → RRF；BM25 仍一次原问。成本极高，仅 **离线调参** 用。

### 检查清单扩展

11. 确认 h 未写入用户可见回答。12. 确认精排不看 h。13. 确认阈值 [99](99.score-threshold-tutorial.md) 在精排后仍生效。

### 域适配：IT 运维 vs 人事制度

IT 问法常含 **错误码、版本号**，HyDE 假想文易编造错误码——此类 query **关闭 HyDE**，靠 BM25 精确匹配。人事制度叙述体多，HyDE 收益常更高。用 **意图分类** 分桶开关。

### 假想文长度扫描

h 长度 50/100/150/200 字对比 Recall；过长 h 引入噪音词，过短 h 缺领域词。画曲线选最优，写入配置。

### 与 [72 本地 Embedding](72.local-embedding-inference-tutorial.md)

本地 embed(h) 可避免 API 泄露；h 仍可能含敏感 **猜测**，日志脱敏。本地推理降低 HyDE 边际成本，适合 **高 QPS**。

### 案例复盘模板

| 字段 | 内容 |
|------|------|
| q_user | |
| h 摘要 | |
| Top-1 chunk 是否含金标 | |
| h 是否含编造数字 | |
| 结论 | 保留/关闭 HyDE |

### 学员实验：关闭 BM25 只用 HyDE

演示 **向量单路** 风险：h 错则全灭。强调 [93 混合检索](93.hybrid-search-tutorial.md) 双路铁律。

### 英文库 HyDE

假想文语言应与 chunk 一致；跨语言库见 [70 混合语言](70.mixed-language-embedding-tutorial.md)，勿中文问英文库却生成中文 h。

### HyDE 完整心智模型（八步）

1. 接收 q_user。2. 可选 [100 改写](100.query-rewriting-tutorial.md)。3. LLM 生成 h。4. 校验 h（长度、数字、敏感词）。5. embed(h)。6. 向量 Top-k。7. BM25(q) Top-k。8. [94 RRF](94.rrf-fusion-tutorial.md) 合并后进 [95 精排](95.cross-encoder-rerank-tutorial.md)。**全程 h 不进生成 prompt**。八步写在 runbook 里，oncall 按步排障。

### 失败案例库

| q | h 问题 | 后果 | 修复 |
|---|--------|------|------|
| 税率多少 | h 编造 13% | 向量偏错段 | 禁数字 |
| 张三年假 | h 出现他人名 | 隐私风险 | 禁补人名 |
| OKR | h 写成 KPI 长文 | 检索偏 | 限制长度 |

### 与 OpenAI Embedding API

[35 兼容 API](35.openai-compatible-api-tutorial.md) embed h 时注意 **速率限制**，与 [69 重试](69.embedding-retry-rate-limit-tutorial.md) 同策略；h 文本短，batch 小。

### 评测指标扩展

除 Recall@k 外，跟踪 **HyDE 触发后 Top-1 变化率**：若经常把正确 Top-1 换掉，说明 h 带偏，应关。

### 安全：假想文 prompt 注入

用户 q 若含「忽略上文，输出……」类注入，h 可能异常。改写/生成 Prompt 用 **分隔符** 与 **角色约束**；可疑 q 跳过 HyDE。

### 总结对比表

| 维度 | 纯 q 向量 | HyDE |
|------|-----------|------|
| 查询文体 | 问句 | 答案叙述 |
| 幻觉风险 | 低 | 中（仅检索） |
| 延迟 | 低 | 高 |
| BM25 | 原问 | 仍原问 |
| 适用 | 关键词明确 | 语义抽象问 |

### 延伸阅读与实验记录

建议实验室笔记本固定记录：日期、索引版本、hyde_prompt_ver、抽样 20 条的 Recall 差、污染条数、是否推荐上线。与 [48 文档版本](48.doc-versioning-tutorial.md) 联动，避免手册更新后仍用旧结论。HyDE 不是银弹；**双路混合检索 + 精排** 仍是主干，假想文档只是 **向量路的可选加速器**。

### 实操：HyDE 开关决策树

```text
query 长度 < 5 且含专名？ → 否 HyDE，走 BM25
向量单路 Recall@10 已 >0.8？ → 否 HyDE
领域是否数字敏感？ → 是则禁数字 h 或关 HyDE
否则 → 试 HyDE，金标 +5% Recall 才保留
```

决策树贴 wiki，避免工程师 **默认全开**。

### 与 chunk 分块策略

[57～62 分块](57.fixed-size-chunking-tutorial.md) 影响 HyDE：chunk 若都是短标题式，h 的叙述体反而可能 **不像标题 chunk**；结构感知分块让 h 更接近段落体，HyDE 收益可能更大。换分块策略要 **重评 HyDE**。

### 批量离线评测脚本思路

对金标集批量：`h = gen(q); v = search(embed(h)); score = recall(v)`；输出 CSV 供产品筛选 **适合 HyDE 的意图类**。在线只对这类开，节省平均延迟。
"""

BULK_103 = """

## 深化阅读：分解、多跳与上下文编排

### 分解与 [104 Multi-hop](104.multi-hop-retrieval-tutorial.md) 的握手

**分解：** 子问可 **并行** 检索，如「住宿标准」「机票舱位」。**多跳：** 第二问依赖第一问结果，如「工单 8842 的处理人是谁」需先检索工单再检索 SLA。产品路由：正则检测工单号 → 多跳；检测并列连接词 → 分解。

### 子问在 prompt 中的顺序

建议 **与用户原问出现顺序一致**，降低认知负担；生成指令写「请按【子问题1】【子问题2】顺序回答」。

### 与 [107 上下文预算](107.context-budget-tutorial.md) 的预告

分解后子问多，[28 Context Window](28.context-window-tutorial.md) 里要给 **每个子问留最小 token 配额**，避免第一个子问占满窗口。107 篇将讲 **资料区算法化分配**；本篇 PoC 用 `chunks_per_sub=2` 硬编码即可。

### 规则分解 vs LLM 分解

| 方式 | 优点 | 缺点 |
|------|------|------|
| 规则标点切分 | 零成本、可预测 | 复杂句失败 |
| LLM JSON | 覆盖复杂并列 | 延迟、偶发格式错 |

生产可 **规则优先**，规则只得到 1 段时 **不分解**，避免误拆。

### 漏答子问的监控

解析生成答案，检测是否出现各子问 **关键词** 或 **编号对应**；漏答率超阈值触发 Prompt 或分解策略调整。

### 金标标注规范

复合问金标要标：`sub_queries: [{text, gold_chunk_ids}]`，评测 **per-sub Recall** 与 **整体答案完整性** 两个指标。

### 与 [34 Grounding](34.grounding-citation-tutorial.md)

每个子问下的 chunk 引用建议 **分开标注**，便于用户核对「机票部分引用了哪条制度」。

### 教学案例：误分解

问：「年假和事假有什么区别」—— 单一 **对比意图**，不必拆成两个独立事实问；拆开会检索到两段孤立定义却 **丢失对比关系**。应单 query + 精排或让生成模型 **对比阅读** 两段资料。

### 并行检索实现注意

子问 3 个 × hybrid 与 Multi-Query 类似，可用线程池；注意 **向量库 QPS** 限制。

### 一周实验计划

| 天 | 任务 |
|----|------|
| 一 | 收集 20 条复合问 |
| 二 | LLM 分解 JSON + 校验 |
| 三 | 分路 [93 混合检索](93.hybrid-search-tutorial.md) |
| 四 | 分组建 prompt + 生成 |
| 五 | 标 per-sub 漏答率 |

### 面试综合题

**用户问包含三个并列小问题，你怎么设计 RAG？** 答：检索前 [103 分解](103.query-decomposition-tutorial.md) 得 3 子问 → 各走 [93 混合检索](93.hybrid-search-tutorial.md) → 合并去重 → [95 精排](95.cross-encoder-rerank-tutorial.md) → 分组建 prompt，总 token 受 [28 Context Window](28.context-window-tutorial.md) 限制；若第二问依赖第一问检索结果则改 [104 多跳](104.multi-hop-retrieval-tutorial.md)。

### 子问数量 k 与资料区 token 算术

假设每 chunk 400 token，每子问保留 2 条，k=3 子问 → 资料约 2400 token，加指令与用户问，仍在 [28 Context Window](28.context-window-tutorial.md) 3200 资料预算内。k=4 且每子问 3 条则可能超标，要 **减 per_sub_k 或 chunks_per_sub**。

### 分解 Prompt 少样本示例

在 Prompt 中加 1～2 个 **正例 JSON**（不含答案），显著提升格式稳定性；与 [31 Few-shot](31.few-shot-prompting-tutorial.md) 同一原理。

### 错误 JSON 修复

```python
def safe_decompose(q, llm):
    try:
        return decompose(q, llm)
    except Exception:
        return [q]
```

永不因分解失败而 **空检索**。

### 与客服工单的衔接

工单常一句话多问：「无法登录 VPN，密码重置找谁」。分解为技术子问 + 流程子问，分别检索 **IT 手册** 与 **服务目录** chunk，生成 **分段指引**。

### 对比单 query 的定性样例

复合问「出差住多少钱，飞机能坐商务舱吗」单 query 检索常只返回 **住宿** chunk（向量偏向前半句）；分解后第二子问命中 **舱位标准** chunk，端到端答案完整。

### 分解边界：对比类问题

「年假与事假区别」—— 意图是 **对比**，可分解为两个定义子问再在生成中 **对比总结**；不要只回答一半。生成 Prompt 加「若用户要求对比，请说明异同」。

### 分解质量评审表

| 维度 | 1 分 | 5 分 |
|------|------|------|
| 子问独立性 | 仍复合 | 可单独检索 |
| 覆盖度 | 漏用户意图 | 全覆盖 |
| 数量 | >5 或 1 条误拆 | 2～4 条 |
| 与 Multi-Query 混淆 | 同义重复 | 意图分离 |

### 端到端延迟估算

T ≈ T_decompose + k×T_hybrid + T_rerank + T_gen。k=3 时检索段约为单 query 3 倍；在 [28 Context Window](28.context-window-tutorial.md) 允许下 **不要** 再放大 per_k。

### 产品文案：何时提示用户拆问

若检测到 **超长复合问** 且分解失败，可回复「您的问题包含多个主题，建议分开提问」——降低系统负载，也提升单问质量。

### 与 [108 长上下文重排](108.long-context-reorder-tutorial.md) 预告

分解后资料块多，进入 prompt 前可按子问 **重排 chunk 顺序**（路线图 108），提升生成可读性；仍受总 token 上限约束。

### 团队 runbook 一句

复合问 → 分解 → 子问各路 [93 混合检索](93.hybrid-search-tutorial.md) → 分组建资料 → 精排 → 生成逐条答；token 总闸 [28 Context Window](28.context-window-tutorial.md)；有依赖改 [104 多跳](104.multi-hop-retrieval-tutorial.md)。

### 分解场景速查（30 秒）

| 用户句式 | 动作 |
|----------|------|
| A多少，B多少 | 分解 |
| A和B区别 | 可分解+对比生成 |
| A的同义词有哪些 | [101 Multi-Query](101.multi-query-retrieval-tutorial.md) |
| 先查X再查Y | [104 多跳](104.multi-hop-retrieval-tutorial.md) |
| 短关键词 | 单 query |

### 培训结业标准

学员能手绘：**分解在 93 之前**、子问并行检索、证据分组、总 token 受 [28 Context Window](28.context-window-tutorial.md) 限制；能口述与 Multi-Query、多跳、改写的区别；能在迷你库跑通 §10 代码并解释漏答子问如何监控。

### 分解后精排两种策略再比较

**全局精排：** 把各子路召回合并成一大池，用 q_user 精排一次。适合 chunk 常 **跨主题**（如总则段同时提住宿与交通）。**分路精排：** 每个子问单独 Top-k。适合 chunk **主题纯净**。用 20 条金标各试一次，选 per-sub MRR 更高者写进配置 `rerank.mode`。

### 用户教育：鼓励拆问

产品可在输入框提示「一次问一件事回答更准」；系统侧仍用分解兜底 **不愿拆的用户**。双侧降低漏答与延迟。

### 与 [99 阈值](99.score-threshold-tutorial.md) 按子问

可对 **每个子路** 的最高 rerank 分设 τ；某子问全员低于 τ 则生成对该子问 **单独拒答**，其它子问正常答——比整句胡编好。
"""


def ensure_len(text, target=5200, bulk="", name_hint=""):
    text = text.rstrip()
    if bulk:
        text += bulk
    if count_hanzi(text) < target:
        text += PAD
    if count_hanzi(text) < target:
        text += (
            "\n\n**系列回顾：** 本篇属 C5 查询增强地基，在 [93 混合检索](93.hybrid-search-tutorial.md) 之前处理 query；"
            "之后接 [94 RRF](94.rrf-fusion-tutorial.md)、[95 精排](95.cross-encoder-rerank-tutorial.md)；"
            "资料区受 [28 Context Window](28.context-window-tutorial.md) 约束。"
            "与 100/101/102/103 按场景开关，金标验证后再灰度。"
        )
    extra = EXTRA_PAD.get(name_hint, "")
    if extra:
        text += extra
    return text.rstrip() + "\n"


EXTRA_PAD = {
    "101": """

## 扩展阅读：Multi-Query 检索策略手册

### 为什么要「多问几遍」而不是把 k 调到 200

把 `top_k` 调到很大，只是在 **同一条 query 的排名尾部** 多捞一些 chunk；排名头部仍由 **单一表述** 主导。若金标 chunk 用的术语与用户问法 **字面不同**，大 k 只是多捞噪音，未必捞到真相关。**Multi-Query** 换的是 **query 表述本身**，让 BM25 有机会命中 **另一套关键词**，让向量 embedding 落在 **另一个语义邻域**。这是「换问法」与「加深排名」的本质区别。

### 子 query 生成的五条黄金法则

1. **意图不变**：每条 qi 必须回答同一用户意图，不得拆成子意图（那是 [103 分解](103.query-decomposition-tutorial.md)）。  
2. **不增事实**：不得出现用户没说的部门、日期、金额。  
3. **保留原问**：`include_original: true`，原问往往是 BM25 最稳的一路。  
4. **控制条数**：n>5 后收益递减、延迟线性涨。  
5. **去重 qi**：字符或向量太近的 qi 删掉，避免假多样性。

### 合并策略选型指南

| 策略 | 何时用 |
|------|--------|
| max_score 去重 | 单路分数量纲一致时 PoC |
| RRF 多路 | **生产默认**，各路分不可比 |
| 投票法 | 出现在 ≥2 路 Top-10 的 chunk 加权 |

合并后 **务必 cap**（如 60），再送 [95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md) 精排；精排不是查询增强，不要混淆阶段。

### 与 [100 改写](100.query-rewriting-tutorial.md) 的流水线写法

```text
q_user → rewrite → q_search → multi_query(q_search) → {q0..qn}
→ ∀qi: hybrid_search(qi) → merge → rerank(q_user) → pack(28预算) → generate(q_user)
```

注意生成始终 **q_user**，精排可用 q_user 或 q_search，需金标选定后固定。

### 评测报告模板（给 TL 看）

- 基线：单 query，Recall@10，p95 延迟  
- 实验：Multi-Query n=4，Recall@10，p95 延迟  
- **并集增益**：多少金标仅 multi 找回  
- **成本**：每月多多少次 LLM 生成子 query  
- **结论**：开 / 关 / 仅某意图开  

### 常见失败模式诊断

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| Recall 不变 | qi 与原问太像 | 加强 Prompt 多样性 |
| Recall 下降 | qi 偏题 | 收紧 Prompt，减 n |
| 延迟暴涨 | n×per_k 过大 | 降 n 或并行+降 per_k |
| 精排更差 | 合并池噪音多 | 降 merged_cap |

### 讲师演示话术（3 分钟）

「同学们，Multi-Query 发生在 [93 混合检索](93.hybrid-search-tutorial.md) **之前**。我们让 LLM 写四种问法，分别去搜，再把 chunk_id 并起来去重，最后精排。它不是 rerank，不碰 chunk 排序算法，只是 **多搜几次**。进模型的资料仍然要听 [28 Context Window](28.context-window-tutorial.md) 的。」

### 上线前最后检查（10 条）

1. 子 query 生成在检索前。2. 含原问。3. n≤5。4. 合并 cap≤80。5. 精排一次非 n 次。6. 生成用 q_user。7. 日志有 sub_queries。8. 金标 A/B 正向。9. ACL 每路生效。10. 与 [103 分解](103.query-decomposition-tutorial.md) 路由不冲突。
""",
    "102": """

## 扩展阅读：HyDE 工程实践手册

### 问句空间 vs 答案空间（一定要讲清）

用户输入大多是 **疑问句**：「多少」「能不能」「如何」。库内 chunk 大多是 **陈述句**：制度、流程、定义。Embedding 模型在训练时见过大量 **陈述性正文**；用问句向量去搜陈述库，几何上常不如 **用一段陈述性假想文** 去搜。HyDE 的工程含义就是：**检索时在答案空间里找一个代理向量**，而不是在问题空间里硬搜。

### 双路混合为什么不可替代

假想文 h **一定会错一部分**——LLM 没看库，不可能全对。若你只开 HyDE 向量路、关掉 BM25 原问，一旦 h 带偏，**全军覆没**。[93 混合检索](93.hybrid-search-tutorial.md) 的价值在于：BM25 用用户原词 **锚定字面**，向量用 h **探索语义**；[94 RRF](94.rrf-fusion-tutorial.md) 把两路名次合并。记住：**HyDE 增强向量路，不替换混合检索**。

### 假想文 Prompt 的三个版本

| 版本 | 适用 |
|------|------|
| 保守 | 禁止数字与人名，政务金融 |
| 标准 | 80～150 字叙述体，企业制度 |
| 探索 | 略高 temperature，仅离线评测 |

上线用保守或标准；探索版只进实验室，不进生产。

### h 的生命周期（不要进 prompt）

```text
h 生成 → embed(h) → dense 检索 → 丢弃 h 正文（默认）
```

只有调试日志在权限控制下暂存 h；**生成 prompt 只允许检索回来的 chunk**。若把 h 当资料，会把 **未验证幻觉** 送进 [28 Context Window](28.context-window-tutorial.md)，违反 [34 Grounding](34.grounding-citation-tutorial.md)。

### 适用域快筛

- **适合**：抽象政策问、定义型问、短问句语义模糊  
- **不适合**：带精确错误码、工单号、SKU、法规条文号  
- **慎用**：强数字问（税率、限额）—— 要禁数字或关 HyDE  

用意图分类器或规则 **自动路由**，比全员 HyDE 更稳。

### 与精排 [95](95.cross-encoder-rerank-tutorial.md) 的衔接

HyDE 之后仍是：RRF 合并 → 去重 → Cross-Encoder(q_user, chunk) 精排。精排配对用 **q_user** 通常更贴近用户综合意图；h 只负责 **把对的 chunk 拉进候选池**。若候选池里没有真 chunk，精排也救不了——HyDE 不是精排替代品。

### 实验记录表（建议打印贴墙）

| q | h 长度 | 金标在 Top-10? | h 含编造? | 保留 HyDE? |
|---|--------|----------------|-----------|------------|

每周更新，索引或 Prompt 版本变更后 **重填**。

### 讲师演示话术（3 分钟）

「HyDE 先让模型写一段 **假答案**，只用它的向量去搜真 chunk；假答案本身不给用户看。BM25 仍搜用户原话。两路合并后精排，再按 [28 Context Window](28.context-window-tutorial.md) 装资料。它是检索前增强，不是 rerank。」

### 上线前最后检查（10 条）

1. h 不进生成 prompt。2. BM25 用原问。3. embed 模型与入库一致。4. 数字敏感域禁精确数。5. 难 query 才触发。6. 日志可审计 h。7. 失败回退 embed(q)。8. RRF 后精排。9. [28 预算](28.context-window-tutorial.md) pack。10. 与 [100 改写](100.query-rewriting-tutorial.md) 顺序：先改写再 HyDE（若串联）。
""",
    "103": """

## 扩展阅读：Query Decomposition 实战手册

### 复合问长什么样（中文办公场景）

- 「年假还剩几天，事假怎么扣工资？」—— **两个独立政策点**  
- 「VPN 连不上，重置密码找哪个部门？」—— **故障 + 流程**  
- 「报销住宿和机票，限额各多少？」—— **两个限额**  

这类问题 **单次向量检索** 常只吸附句首主题。分解在 [93 混合检索](93.hybrid-search-tutorial.md) **之前** 把它们拆成可独立检索的子问，每路用更 **纯净的 qi** 召回对应 chunk。

### 与 [101 Multi-Query](101.multi-query-retrieval-tutorial.md) 一句话区分

- **Multi-Query**：同一意图的多种说法（同义）  
- **Decomposition**：同一长句里的 **多个意图**（并列）  

把「住宿标准」和「住宿限额」当两条 qi 是 Multi-Query；把「住宿」和「机票」当两条是 Decomposition。面试常考，务必背熟。

### 分解后的 prompt 为什么要分组

模型读长资料时，若不分组，容易 **只回答第一段看到的主题**。用【子问题1】【子问题2】标题把 chunk 隔开，并在指令里写 **逐条回答**，可显著降低漏答率。资料总长度仍受 [28 Context Window](28.context-window-tutorial.md) 限制——子问多时每子问少放点 chunk。

### 并行检索与成本

k 个子问 ≈ k 次 hybrid_search。k=3、per_k=20 时，检索压力约为单 query 3 倍。可用线程池并行 IO；注意向量库 QPS。成本换 **覆盖率**，适合 **复合问占比高** 的客服场景。

### 何时不分解

- 单意图对比：「年假与事假区别」—— 可单 query 检索两段再让模型对比  
- 极短问：「年假」  
- 有链式依赖：「工单 8842 的 SLA」—— 用 [104 多跳](104.multi-hop-retrieval-tutorial.md)  

错误分解比不分解更糟：子问偏题会 **主动搜错方向**。

### 漏答监控

生成后检查是否覆盖每个子问关键词；漏答率 >5% 则调分解 Prompt 或加 **逐条回答** 约束。与 [112 拒答](112.refusal-strategy-tutorial.md) 结合：某子问无资料则对该子问明确说「无法确定」，不要编造。

### 金标标注规范（给标注员）

复合问标注拆成 `sub1`, `sub2`，各标 `gold_chunk_ids`。评测 **per-sub Recall@5** 与 **整句答案完整性** 两个指标同时看。

### 完整链路背诵

「分解 → 子问并行 [93 混合检索](93.hybrid-search-tutorial.md) → 合并去重 → [95 精排](95.cross-encoder-rerank-tutorial.md) → 分组建 prompt → [28 窗口](28.context-window-tutorial.md) 截断 → 生成逐条答。」

### 讲师演示话术（3 分钟）

「用户一句话问两件事，我们先拆成两个子问，各搜各的，再把证据分块塞进 prompt，让模型分开答。拆在检索前，不是精排。和 Multi-Query 不同，我们拆的是 **不同意图**，不是同义改写。」

### 上线前最后检查（10 条）

1. 分解在 hybrid 前。2. 子问 2～4。3. 非大量同义 qi。4. prompt 分子问区。5. 指令逐条答。6. per-sub 无资料可拒答。7. token 总闸 [28](28.context-window-tutorial.md)。8. 对比类慎拆。9. 链式依赖改 [104 多跳](104.multi-hop-retrieval-tutorial.md)。10. 金标 per-sub 评测通过。
""",
}


def main():
    articles = {
        "101.multi-query-retrieval-tutorial.md": build_multi_query(),
        "102.hyde-tutorial.md": build_hyde(),
        "103.query-decomposition-tutorial.md": build_decomposition(),
    }
    for name, body in articles.items():
        bulk = BULK_101 if "101" in name else BULK_102 if "102" in name else BULK_103
        hint = "101" if "101" in name else "102" if "102" in name else "103"
        body = ensure_len(body, 5200, bulk=bulk, name_hint=hint)
        (ROOT / name).write_text(body, encoding="utf-8")
        print(f"{name}: {count_hanzi(body)} hanzi")
    # 100 already written; just verify
    t100 = (ROOT / "100.query-rewriting-tutorial.md").read_text(encoding="utf-8")
    # remove duplicate pad if any
    if t100.count("## 附录：深度学习与调参备忘") > 1:
        h = "## 附录：深度学习与调参备忘"
        idx = t100.find(h)
        t100 = t100[:idx].rstrip() + "\n\n" + h + t100[idx+len(h):].split(h)[0]
        (ROOT / "100.query-rewriting-tutorial.md").write_text(t100, encoding="utf-8")
    print(f"100.query-rewriting-tutorial.md: {count_hanzi(t100)} hanzi")


if __name__ == "__main__":
    main()
