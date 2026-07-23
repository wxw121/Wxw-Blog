# -*- coding: utf-8 -*-
"""Shared FAQ/summary blocks for batch article generators."""


def common_faq(topic: str, extra: list[str] | None = None) -> str:
    base = f"""
## 12. 常见陷阱与 FAQ

### 12.1 初学者最常踩的三坑

1. **只看最终答案，不看链路**——{topic} 的价值在 **可复现的中间态**。  
2. **没有金标就调参**——没有 [160 Golden Dataset](143.golden-dataset-tutorial.md) 时，A/B 只是 **主观吵架**。  
3. **工具买了不用**——装了 LangSmith/Langfuse 却不给每次请求打 `trace_id`，等于 **黑盒上线**。

### 12.2 FAQ 精选

**Q1：PoC 阶段要不要上观测？**  
要。**最小集**：`request_id` + 检索 Top-5 `chunk_id` + 模型名 + 延迟。完整平台可后补，但 **字段契约** 第一天就定。

**Q2：和 RAGAS 指标怎么配合？**  
RAGAS 回答 **「好不好」**；观测平台回答 **「哪一步坏了」**。建议：金标跑 RAGAS 批次，线上 bad case 用 trace 下钻。

**Q3：成本会不会爆？**  
Trace 存全文 context 很贵。生产用 **采样**（如 5%）+ **摘要字段**（chunk_id、score、前 200 字预览），全文按需拉取。

**Q4：多环境怎么隔离？**  
`project` / `environment` 标签：`dev` / `staging` / `prod` 分开；**禁止** 把 prod trace 当训练数据未经脱敏。

**Q5：谁负责看板？**  
工程搭管道，**产品 + 领域专家** 每周过 bad case；研发负责 **归因到模块**（解析/切块/检索/生成）。

**Q6：失败请求要不要记 trace？**  
**更要记**。超时、空检索、解析异常——没有失败 trace，你永远在猜。

**Q7：和 [147 LangSmith](147.langsmith-tracing-tutorial.md) / [148 Langfuse](148.langfuse-observability-tutorial.md) 二选一？**  
LangChain 深度用 LangSmith 顺手；要 **自托管、开源、多框架** 看 Langfuse。也可 **双写** 过渡期，但统一 `trace_id`。

**Q8：如何证明一次修复有效？**  
回归集 [161](144.regression-test-set-tutorial.md) 上 **同题同参** 对比；再看线上 **7 日 bad case 率**。

**Q9：实习生能维护吗？**  
把 **归因决策树** 贴在 wiki（本篇系列 149～152）；观测 UI 只读权限给全员，写权限限研发。

**Q10：面试怎么讲？**  
30 秒：**「RAG 上线后我用 trace 把 bad case 分到 ingest/retrieve/generate，用金标 + A/B 验证改动，参数版本可回滚。」**
"""
    if extra:
        base += "\n" + "\n".join(extra)
    return base


def common_summary(next_links: list[tuple[str, str]]) -> str:
    rows = "\n".join(f"| {label} | {link} |" for label, link in next_links)
    return f"""
## 13. 总结与系列下一步

### 13.1 本篇要点回顾

本篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 模块** 的一环。E 模块主线是：**先有金标与指标 → 再有观测 → 再会归因 bad case → 再用实验与版本管理迭代**。

### 13.2 系列下一步

| 目标 | 阅读 |
|------|------|
{rows}

### 13.2 学习目标自检

- [ ] 能口述本篇在 E 模块中的位置  
- [ ] 能列出至少三个与前序文章的衔接点  
- [ ] 能完成一篇中的「动手路径」验收  
- [ ] 能在观测 UI 或日志里找到一次完整 RAG trace  
- [ ] 能把一个真实 bad case 写到归因树的一叶子上  

### 13.3 面试 30 秒版

见 §12 FAQ Q10。

### 13.4 30 分钟作业

1. 选一条你项目里的 **真实用户问题**；  
2. 在 LangSmith 或 Langfuse（或最小 JSON 日志）里拉出 **完整 trace**；  
3. 用 149～152 决策树写 **归因假设**；  
4. 写一条 **可验证的修复实验**（对接 [170 A/B](153.ab-experiment-rag-tutorial.md)）；  
5. 在 [171 参数版本](154.param-version-management-tutorial.md) 表里登记本次改动的参数。

---

> **初学者可能仍困惑的点**  
> - **观测 ≠ 评测**：前者定位，后者打分。  
> - **了解档** 也要会 **最小集成**，否则面试说不清。  
> - Bad case 系列要 **交叉验证**：解析错会像检索漏，生成胡编有时是检索空。  
> - 任何改动 **必须可回滚**——见参数版本篇。
"""
