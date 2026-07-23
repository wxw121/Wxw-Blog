# -*- coding: utf-8 -*-
"""Articles 149-154 for batch 146-154."""
from _article_common import common_faq, common_summary

ARTICLE_149 = r'''# E 评测与观测（十一）：Bad Case 归因之解析错误完全指南

> 用户问「表格里第三列报销上限是多少」，机器人答「请咨询财务」——你查向量库，发现 **根本没有那条 chunk**。打开源 PDF，肉眼明明有表；再 `get_text()`，表变成 **一行乱序数字**。这不是检索参数问题，是 **ingest 解析错了**。这篇是 [企业 RAG 路线图](ENTERPRISE_RAG_ROADMAP.md) **E 模块地基篇**（路线图第 **166** 条），教你 **从 [147 LangSmith](147.langsmith-tracing-tutorial.md) / [148 Langfuse](148.langfuse-observability-tutorial.md) trace 认出解析型 bad case**，并对照 C1 轨 [36～56 解析系列](36.pdf-text-extraction-tutorial.md) 修。前置：[36 PDF 提取](36.pdf-text-extraction-tutorial.md)、[46 文本清洗](46.text-cleaning-tutorial.md)、[147 追踪](147.langsmith-tracing-tutorial.md)。

---

## 目录

1. [前言：解析错是「无声杀手」](#1-前言解析错是无声杀手)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [解析型 bad case 是什么](#3-解析型-bad-case-是什么)
4. [在 trace 上如何识别](#4-在-trace-上如何识别)
5. [失败模式地图：对照 36～56](#5-失败模式地图对照-3656)
6. [PDF 专项：文本层与扫描件](#6-pdf-专项文本层与扫描件)
7. [Office / HTML / Markdown 专项](#7-office--html--markdown-专项)
8. [编码、清洗与元数据](#8-编码清洗与元数据)
9. [诊断清单与抽样验收](#9-诊断清单与抽样验收)
10. [修复 Playbook](#10-修复-playbook)
11. [先错对对：五种典型误判](#11-先错对对五种典型误判)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：解析错是「无声杀手」

解析错最难缠之处：**索引「成功」了**——任务状态 `done`，chunk 数量正常，向量也入库了，但 **字是错的、顺序是错的、表是扁的**。检索只能在海里捞 **已经变形的鱼**。

与 [151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md) 区分：

| 类型 | 库里有正确文本吗 | trace 里 retrieval 现象 |
|------|------------------|-------------------------|
| 解析错 | **没有**（或只有残缺） | 即使用正确 query 也 **捞不到** 正确表述 |
| 检索漏 | **有** | hits 不含应命中的 chunk |

与 [150 切块错](150.bad-case-chunking-tutorial.md) 区分：解析错是 **入库前** 文本已坏；切块错是 **文本对但刀口切坏**。

**读完本文，你应该能做到：**

1. 用 trace 判断 bad case 是否 **优先怀疑解析**。  
2. 列出 [36](36.pdf-text-extraction-tutorial.md)～[56](56.multimodal-image-text-tutorial.md) 各篇负责的失败模式。  
3. 完成 §9 十文档抽样验收表。  
4. 写一条解析修复工单（换解析器 / OCR / 清洗规则）。  
5. 修复后用 [161 回归集](144.regression-test-set-tutorial.md) 验证 **同一 query 能检索到正确事实**。

---

## 2. 本文边界与动手路径

**档位：E 地基篇（166）。**

**本文讲：** 解析型 bad case 识别、trace 特征、36～56 对照、诊断清单、修复 Playbook。  
**本文不讲：** 单个解析库 API 大全（见 C1 各工具篇）、OCR 模型训练。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 选 1 条真实 bad case | 有 trace 链接 |
| B | 对源文件人工复制 vs 库内 chunk | 记录差异 |
| C | 填 §9 诊断清单 | 归因「解析」 |
| D | 选 C1 一篇工具升级 | 重跑 ingest |
| E | 回归集同题重测 | 检索命中 |

---

## 3. 解析型 bad case 是什么

![解析型 bad case](image/bad-case-parsing/01-parsing-bad-case.png)

**定义**：因 **文档解析 / 提取 / 编码 / 清洗** 阶段错误，导致入库文本与源文档 **语义或结构不一致**，进而使 RAG **无法检索或引用到正确内容**。

常见用户可见症状：

- 答案说「资料未提及」，但 PDF 里 **肉眼可见**；  
- 引用打开后 **空白页** 或 **乱码**；  
- 数字、日期、条款号 **系统性偏差**；  
- 多栏文档 **左右栏串读**。

---

## 4. 在 trace 上如何识别

在 [147 LangSmith](147.langsmith-tracing-tutorial.md) 或 [148 Langfuse](148.langfuse-observability-tutorial.md) 中：

### 4.1 固定三步

1. **复制用户 query**，在 **检索调试台**（路线图 199）或 trace 的 retriever 输出看 Top-K；  
2. **打开** `metadata.source` / `page`（[52 篇](52.metadata-source-page-tutorial.md)）对照源文件；  
3. 若源文件有、库内 **无对应字面或语义** → **优先解析** 而非先调 `top_k`。

### 4.2 trace 指纹

| 指纹 | 含义 |
|------|------|
| 全库无某 doc 关键词 | 可能解析丢段或 [47 去重](47.doc-dedup-tutorial.md) 误删 |
| 有词但数字错 | [37 表格](37.pdf-layout-tables-tutorial.md)、[43 pdfplumber](43.pdfplumber-tutorial.md) |
| 英文正常中文方块 | [41 编码](41.text-encoding-detection-tutorial.md) |
| 页眉页脚插进正文 | [46 清洗](46.text-cleaning-tutorial.md) |
| 扫描件无字 | [55 OCR](55.ocr-scanned-docs-tutorial.md) |

---

## 5. 失败模式地图：对照 36～56

![解析失败模式地图](image/bad-case-parsing/02-failure-mode-map.png)

| 路线图 | 文章 | 典型解析问题 | bad case 信号 |
|--------|------|--------------|---------------|
| 43 | [36 PDF 文本](36.pdf-text-extraction-tutorial.md) | 无文本层、乱序 | 复制 PDF 与 chunk 不一致 |
| 44 | [37 PDF 版面](37.pdf-layout-tables-tutorial.md) | 表变空格 | 报销额、税率全错 |
| 45 | [38 Markdown](38.markdown-parsing-tutorial.md) | 标题层级丢 | 条款挂错章 |
| 46 | [39 HTML](39.html-content-extraction-tutorial.md) | 导航菜单入库 | 答案带「首页登录」 |
| 47 | [40 DOCX](40.docx-office-parsing-tutorial.md) | 列表编号乱 | 政策序号错 |
| 48 | [41 编码](41.text-encoding-detection-tutorial.md) | 乱码 | 中文变 `` |
| 49～52 | [42～45 工具](42.pymupdf-tutorial.md) | 工具特化问题 | 换工具后好转 |
| 53 | [46 清洗](46.text-cleaning-tutorial.md) | 过度清洗 | 数字被删 |
| 54 | [47 去重](47.doc-dedup-tutorial.md) | 近重复误并 | 版本混用 |
| 55～56 | [48～49 版本/增量](48.doc-versioning-tutorial.md) | 旧版覆盖 | 答案过期 |
| 57～61 | [50～54 元数据](50.metadata-doc-id-tutorial.md) | id 错 | 引用张冠李戴 |
| 62 | [55 OCR](55.ocr-scanned-docs-tutorial.md) | 扫描未 OCR | 库内无字 |
| 63 | [56 多模态](56.multimodal-image-text-tutorial.md) | 图内字未抽 | 流程图信息丢失 |

**工程原则**：bad case 先 **定位到上表一行**，再打开对应 C1 教程 **深修**，避免在检索层空转。

---

## 6. PDF 专项：文本层与扫描件

### 6.1 文本层 PDF

用 [36 篇](36.pdf-text-extraction-tutorial.md) pypdf 抽一遍，与 [42 PyMuPDF](42.pymupdf-tutorial.md)、[43 pdfplumber](43.pdfplumber-tutorial.md) 对照。若 **仅某一工具** 顺序正常 → 固定该工具为 **主解析器**（[136 可插拔 Parser](136.pluggable-parser-splitter-embedder-tutorial.md)）。

### 6.2 扫描件

库内字符数极少、图片占比高 → [55 OCR](55.ocr-scanned-docs-tutorial.md)。未 OCR 的扫描 PDF **不应标记 ingest done**（路线图 178 状态机应 **blocked**）。

### 6.3 表格

财务、报销类 bad case **高发表格** → 必读 [37](37.pdf-layout-tables-tutorial.md)。trace 显示 chunk 里 **数字没有列标题对应** 时，优先版面恢复而非 chunk 加大。

---

## 7. Office / HTML / Markdown 专项

- **DOCX**：[40 篇](40.docx-office-parsing-tutorial.md)——合同、制度 Word 多；  
- **HTML 帮助中心**：[39 篇](39.html-content-extraction-tutorial.md)——侧边栏污染是常见 bad case；  
- **Markdown 知识库**：[38 篇](38.markdown-parsing-tutorial.md)——代码块、表格语法影响 [63 AST 切块](63.markdown-ast-chunking-tutorial.md) 前置。

---

## 8. 编码、清洗与元数据

[41 编码检测](41.text-encoding-detection-tutorial.md)：GBK/UTF-8 误读会产生 **形似乱码** 的固定替换字。  
[46 清洗](46.text-cleaning-tutorial.md)：正则删页码时勿删 **条款编号**。  
[50 doc_id](50.metadata-doc-id-tutorial.md) + [48 版本](48.doc-versioning-tutorial.md)：解析修完后 **新 doc_id 或 version**，避免旧向量 **幽灵命中**。

---

## 9. 诊断清单与抽样验收

![解析诊断清单](image/bad-case-parsing/03-diagnosis-checklist.png)

**十文档抽样表**（每周 ingest 质检）：

| # | 文件名 | 人工可读 | 表/图 | 编码 | 入库字数比 | 结论 |
|---|--------|----------|-------|------|------------|------|
| 1 | handbook.pdf | ✓/✗ | | | | |

字数比 = `len(库内正文) / len(人工抽样正文)`，**<0.7 或 >1.3** 标黄。

---

## 10. 修复 Playbook

1. **冻结 bad case**：trace + 源文件 + chunk_id；  
2. **复现提取**：命令行单独跑 Parser，输出 `.txt` diff；  
3. **选型**：按 §5 表换工具或加 OCR；  
4. **重 ingest**：[49 增量](49.incremental-update-tutorial.md) 或 [162 幂等重建](162.idempotent-reindex-tutorial.md)；  
5. **回归**：[161 回归集](144.regression-test-set-tutorial.md) + [141 Faithfulness](141.ragas-faithfulness-tutorial.md)；  
6. **登记**：[171 参数版本](154.param-version-management-tutorial.md) `parser=pymupdf-v2`。

---

## 11. 先错对对：五种典型误判

### 11.1 错：一律加大 chunk_size

**对**：解析乱序时大 chunk **更乱**。

### 11.2 错：先上混合检索

**对**：库内无正确字，[93 Hybrid](93.hybrid-search-tutorial.md) 无效。

### 11.3 错：怪 Embedding 模型

**对**：先 diff 源文与库文。

### 11.4 错：忽略扫描件

**对**：页级检测文本层字符数。

### 11.5 错：修复后不升 doc 版本

**对**：见 [48 版本](48.doc-versioning-tutorial.md)。

---

## 12. 综合概念地图

![解析 bad case 概念地图](image/bad-case-parsing/04-concept-map.png)

---

''' + common_faq("解析归因", [
    "**Q11：解析和切块怎么快速分？**  \n同一 chunk 内 **前半句通后半句断** → 切块；**整段与 PDF 复制不一致** → 解析。",
]) + common_summary([
    ("Bad Case：切块", "[150 切块归因](150.bad-case-chunking-tutorial.md)"),
    ("Bad Case：检索", "[151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)"),
    ("Langfuse 观测", "[148 Langfuse](148.langfuse-observability-tutorial.md)"),
    ("PDF 提取", "[36 PDF 提取](36.pdf-text-extraction-tutorial.md)"),
])

ARTICLE_150 = r'''# E 评测与观测（十二）：Bad Case 归因之切块错误完全指南

> 解析对了，用户问「试用期多久」，检索命中的 chunk 却是 **「试用」和「期考核」被切成两半** 的两段——BM25 勉强命中其中一段，LLM 看到残缺句，答成「试用考核为期三个月」。这是 **切块（Chunking）** 型 bad case。这篇是路线图 **167**，地基篇。前置：[57 固定分块](57.fixed-size-chunking-tutorial.md)、[60 overlap](60.chunk-overlap-tutorial.md)、[62 结构分块](62.structure-aware-chunking-tutorial.md)；用 [147/148](147.langsmith-tracing-tutorial.md) trace 看 **命中 chunk 边界**；与 [149 解析](149.bad-case-parsing-tutorial.md)、[151 检索](151.bad-case-retrieval-miss-tutorial.md) 交叉验证。

---

## 目录

1. [前言：刀口不对，检索全白费](#1-前言刀口不对检索全白费)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [切块型 bad case 是什么](#3-切块型-bad-case-是什么)
4. [trace 上如何识别切块问题](#4-trace-上如何识别切块问题)
5. [C2 切块策略对照 57～65](#5-c2-切块策略对照-5765)
6. [chunk_size 与 overlap 诊断](#6-chunk_size-与-overlap-诊断)
7. [结构感知与 Markdown AST](#7-结构感知与-markdown-ast)
8. [Parent Document 与层次索引](#8-parent-document-与层次索引)
9. [诊断清单与 Golden 探针](#9-诊断清单与-golden-探针)
10. [修复 Playbook](#10-修复-playbook)
11. [先错对对：五种典型误判](#11-先错对对五种典型误判)
12. [综合概念地图](#12-综合概念地图)
13. [常见陷阱与 FAQ](#13-常见陷阱与-faq)
14. [总结与系列下一步](#14-总结与系列下一步)

---

## 1. 前言：刀口不对，检索全白费

[57 固定长度](57.fixed-size-chunking-tutorial.md) §8 先错对对已经演示：**句中断开** 会让关键条件落在两个 chunk 的缝里。上线后这类问题表现为：

- 检索 **分数中等**（命中半个关键词）；  
- 上下文 **缺主语或缺结论**；  
- [152 胡编](152.bad-case-hallucination-tutorial.md) 或 [33 幻觉](33.llm-hallucination-tutorial.md) **忠实性胡编**——模型 **补全** 了残缺句。

**切块型 bad case 定义**：入库文本正确，但 **分块边界不合理**，导致 **单 chunk 无法承载完整语义单元**，使检索或生成失败。

---

## 2. 本文边界与动手路径

**档位：E 地基篇（167）。**

**本文讲：** 识别、C2 策略对照、size/overlap、结构分块、Parent、修复。  
**本文不讲：** 语义分块 LLM 全自动（路线图深入项）。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | trace 中复制命中 chunk 全文 | 是否语义完整 |
| B | 在源文档定位对应段 | 边界是否切断 |
| C | 调 overlap 或改结构分块 | 同 query recall 提升 |
| D | 登记 [171 参数版本](154.param-version-management-tutorial.md) | `chunk_policy` 变更 |

---

## 3. 切块型 bad case 是什么

![切块型 bad case](image/bad-case-chunking/01-chunking-bad-case.png)

### 3.1 与解析错、检索漏区分

| 类型 | 源文 | 单 chunk 语义 |
|------|------|---------------|
| [149 解析](149.bad-case-parsing-tutorial.md) | 已坏 | — |
| **切块** | 对 | **不完整** |
| [151 检索](151.bad-case-retrieval-miss-tutorial.md) | 对 | 完整 chunk 存在但未命中 |

---

## 4. trace 上如何识别切块问题

在 [148 Langfuse](148.langfuse-observability-tutorial.md) retrieve observation：

1. 看 **Top-1 chunk** 是否 **以连词/逗号开头** 或 **突然断句**；  
2. 用 `chunk_id`（[51](51.metadata-chunk-id-tutorial.md)）在源文 **前后各读 200 字**；  
3. 若答案在 **相邻 chunk** 另一半 → 切块问题坐实。

**探针 query**：从 [160 金标](143.golden-dataset-tutorial.md) 取 **必须跨句回答** 的题（含「且」「但是」「不包括」）。

---

## 5. C2 切块策略对照 57～65

![切块策略对照](image/bad-case-chunking/02-chunk-strategies.png)

| 文章 | 策略 | 适用 | 常见 bad case |
|------|------|------|---------------|
| [57](57.fixed-size-chunking-tutorial.md) | 固定长度 | PoC | 句中断 |
| [58](58.recursive-character-chunking-tutorial.md) | 递归分隔 | 通用 | 分隔符选错 |
| [59](59.sentence-boundary-chunking-tutorial.md) | 句子边界 | 制度条文 | 超长单句 |
| [60](60.chunk-overlap-tutorial.md) | 重叠 | 补缝 | overlap 仍不够 |
| [61](61.chunk-size-tradeoff-tutorial.md) | 大小权衡 | 调参 | 过大引入噪声 |
| [62](62.structure-aware-chunking-tutorial.md) | 结构感知 | 手册 | 标题与正文分离 |
| [63](63.markdown-ast-chunking-tutorial.md) | MD AST | 技术 Wiki | 代码块被切 |
| [64](64.html-dom-chunking-tutorial.md) | HTML DOM | 帮助中心 | div 边界 |
| [65](65.parent-document-retriever-tutorial.md) | 父文档 | 长条命中 | 子块太碎 |

---

## 6. chunk_size 与 overlap 诊断

读 [61 篇](61.chunk-size-tradeoff-tutorial.md)：

- **过小**：定义与例外 **分到不同 chunk**；  
- **过大**：多主题混一块，[93 检索](93.hybrid-search-tutorial.md) 精度降；  
- **overlap=0**：[60 篇](60.chunk-overlap-tutorial.md) 缝上关键词 **两边都只有一半**。

**实验**：固定解析器，只改 `chunk_size` / `overlap`，在 [170 A/B](153.ab-experiment-rag-tutorial.md) 框架下跑 [161 回归集](144.regression-test-set-tutorial.md)。

---

## 7. 结构感知与 Markdown AST

员工手册常见 **「第三章 → 3.1 → 3.1.1」**——[62 结构分块](62.structure-aware-chunking-tutorial.md) 按标题切，避免 **条号与正文分离**。  
技术文档用 [63 Markdown AST](63.markdown-ast-chunking-tutorial.md)：**代码块、表格** 保持原子单元。

---

## 8. Parent Document 与层次索引

[65 Parent Document](65.parent-document-retriever-tutorial.md)：检索 **小子块**，生成用 **父段落**。trace 里若小子块语义碎但 **parent 字段完整**，属 **设计如此**；若未实现 parent 却用小碎块 → bad case。

---

## 9. 诊断清单与 Golden 探针

![切块诊断清单](image/bad-case-chunking/03-diagnosis-checklist.png)

| 检查项 | 通过标准 |
|--------|----------|
| 金标句能否在单 chunk 找全 | 是 |
| 条号与内容同块 | 是 |
| overlap ≥ 关键句长度 15% | 建议 |
| 代码块未被切断 | 是 |

---

## 10. 修复 Playbook

1. trace 定位 `chunk_id`；  
2. 判断策略层级（固定 → 递归 → 结构）；  
3. 调参或换 Splitter（[130 LangChain Text Splitter](130.langchain-text-splitter-tutorial.md)、[136 可插拔](136.pluggable-parser-splitter-embedder-tutorial.md)）；  
4. **全量重 embed**（[171 版本](154.param-version-management-tutorial.md) 新 `chunk_policy`）；  
5. [147/148](147.langsmith-tracing-tutorial.md) 对比修复前后 trace。

---

## 11. 先错对对：五种典型误判

### 11.1 错：解析未排除就调 overlap

**对**：先 [149](149.bad-case-parsing-tutorial.md)。

### 11.2 错：chunk 越大越好

**对**：见 [61 tradeoff](61.chunk-size-tradeoff-tutorial.md)。

### 11.3 错：命中了就说检索没问题

**对**：命中 **错块** 也是切块/检索问题。

### 11.4 错：只改 prompt 让模型「联系上下文」

**对**：上下文 **没进 Top-K** 时 prompt 无效。

### 11.5 错：不重跑 embedding

**对**：切块变必须 **重 embed**。

---

## 12. 综合概念地图

![切块 bad case 概念地图](image/bad-case-chunking/04-concept-map.png)

---

''' + common_faq("切块归因") + common_summary([
    ("Bad Case：解析", "[149 解析](149.bad-case-parsing-tutorial.md)"),
    ("Bad Case：检索", "[151 检索](151.bad-case-retrieval-miss-tutorial.md)"),
    ("固定分块", "[57 固定分块](57.fixed-size-chunking-tutorial.md)"),
    ("参数版本", "[154 参数版本](154.param-version-management-tutorial.md)"),
])

# ─────────────────────────────────────────────────────────────
# 151 Retrieval Miss
# ─────────────────────────────────────────────────────────────

ARTICLE_151 = r'''# E 评测与观测（十三）：Bad Case 归因之检索遗漏完全指南

> 库里有「一线城市住宿费上限 500 元」，用户问「出差住酒店能报多少」，trace 里 Top-5 **全是差旅交通补贴**——这是 **检索遗漏（Retrieval Miss）**。解析对、切块对，但 **召回没把正确 chunk 捞进候选池**。这篇是路线图 **168**，**主线篇**。前置：[91 Dense](91.dense-retrieval-tutorial.md)、[93 混合检索](93.hybrid-search-tutorial.md)、[100 Query Rewriting](100.query-rewriting-tutorial.md)、[147 LangSmith](147.langsmith-tracing-tutorial.md)。与 [149 解析](149.bad-case-parsing-tutorial.md)、[150 切块](150.bad-case-chunking-tutorial.md)、[152 胡编](152.bad-case-hallucination-tutorial.md) 组成 **归因四部曲**。

---

## 目录

1. [前言：检索漏了，后面全是演戏](#1-前言检索漏了后面全是演戏)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [检索遗漏是什么](#3-检索遗漏是什么)
4. [trace 上的三种遗漏形态](#4-trace-上的三种遗漏形态)
5. [归因决策树](#5-归因决策树)
6. [Dense 路与语义漂移](#6-dense-路与语义漂移)
7. [Sparse 路与字面不匹配](#7-sparse-路与字面不匹配)
8. [混合检索、RRF 与过滤](#8-混合检索rrf-与过滤)
9. [Query 增强与多路召回](#9-query-增强与多路召回)
10. [重排序与 top_k 阈值](#10-重排序与-top_k-阈值)
11. [修复 Playbook 与实验设计](#11-修复-playbook-与实验设计)
12. [先错对对：六种典型翻车](#12-先错对对六种典型翻车)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：检索漏了，后面全是演戏

[33 幻觉](33.llm-hallucination-tutorial.md) 教你：没资料时模型会 **编**。检索遗漏时，上下文 **不含答案**，Faithfulness 再高的 prompt 也只能 **拒答或胡编**——用户看到的是后者，就会骂「胡编」。

**检索遗漏定义**：正确答案存在于索引中，但 **检索阶段未进入 Top-K**（或未进入 rerank 输入），导致生成阶段 **无足够证据**。

**主线篇** 原因：这是企业 RAG **最常见、最值得投入** 的优化点——[93 混合检索](93.hybrid-search-tutorial.md)、[100 改写](100.query-rewriting-tutorial.md)、[95 精排](95.cross-encoder-rerank-tutorial.md) 都服务于此。

---

## 2. 本文边界与动手路径

**档位：E 主线篇（168）。**

**本文讲：** 识别、决策树、dense/sparse/hybrid、改写、rerank、实验。  
**本文不讲：** 新 Embedding 预训练（见 [73 微调](73.embedding-finetune-tutorial.md) 了解）。

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 金标题 + trace 证明应命中 chunk 不在 Top-K | 遗漏复现 |
| B | 调试台用 **库内原句** 查能否 Top-1 | 区分索引/查询 |
| C | 开 BM25 或 hybrid 对比 | Recall 提升 |
| D | [170 A/B](153.ab-experiment-rag-tutorial.md) 记录 | 有 param_version |

---

## 3. 检索遗漏是什么

![检索遗漏是什么](image/bad-case-retrieval-miss/01-retrieval-miss.png)

### 3.1 与近邻概念

| 概念 | 库中有答案 chunk | Top-K 含该 chunk |
|------|------------------|------------------|
| 检索遗漏 | 是 | **否** |
| [152 胡编](152.bad-case-hallucination-tutorial.md)（有上下文） | 是 | **是** |
| [149 解析](149.bad-case-parsing-tutorial.md) | **否**（文本错） | — |

---

## 4. trace 上的三种遗漏形态

在 [148 Langfuse](148.langfuse-observability-tutorial.md) / [147 LangSmith](147.langsmith-tracing-tutorial.md)：

1. **完全遗漏**：Top-K 无一相关；  
2. **排名过低**：相关 chunk 在 rank 15，K=5 被截；  
3. **被过滤误杀**：`where` ACL（[53](53.metadata-acl-tutorial.md)）、`doc_version` 过滤掉正解。

---

## 5. 归因决策树

![检索遗漏决策树](image/bad-case-retrieval-miss/02-decision-tree.png)

```text
用户 bad case
  → trace 看 Top-K
      → 库内搜 gold 句能否命中？
          否 → [149 解析] / [150 切块] / 未索引
          是 → 用 gold 句作 query 能 Top-1？
              否 → 索引/embedding 异常
              是 → 用户 query 问题 → [100 改写] / hybrid / synonym
      → 检查 metadata filter / ACL
      → 检查 top_k、score threshold [99](99.score-threshold-tutorial.md)
```

---

## 6. Dense 路与语义漂移

[91 Dense](91.dense-retrieval-tutorial.md)：「住酒店」与「住宿费」向量距离可能远。  
对策：[100 Query Rewriting](100.query-rewriting-tutorial.md)、[101 Multi-Query](101.multi-query-retrieval-tutorial.md)、领域 Embedding [71](71.domain-embedding-evaluation-tutorial.md)。

---

## 7. Sparse 路与字面不匹配

[92 Sparse](92.sparse-retrieval-rag-tutorial.md)：用户写英文缩写、文档写中文全称。  
对策：BM25 + 同义词表、hybrid。

---

## 8. 混合检索、RRF 与过滤

![混合检索修复路径](image/bad-case-retrieval-miss/03-hybrid-fix.png)

[93 Hybrid](93.hybrid-search-tutorial.md) + [94 RRF](94.rrf-fusion-tutorial.md) 是企业默认 **第一档修复**。  
注意：**双路 filter 必须一致**（[88 元数据过滤](88.metadata-filter-retrieval-tutorial.md)），否则一路有、一路无。

---

## 9. Query 增强与多路召回

| 技术 | 文章 | 作用 |
|------|------|------|
| 改写 | [100](100.query-rewriting-tutorial.md) | 口语→正式 |
| 多查询 | [101](101.multi-query-retrieval-tutorial.md) | 多角度召回 |
| HyDE | [102](102.hyde-tutorial.md) | 假想文档向量 |
| 分解 | [103](103.query-decomposition-tutorial.md) | 多跳 |

[109 对话增强](109.conversation-query-enhancement-tutorial.md) 处理 **多轮指代**。

---

## 10. 重排序与 top_k 阈值

[95 Cross-Encoder](95.cross-encoder-rerank-tutorial.md)、[96 BGE](96.bge-reranker-tutorial.md)：先 **宽召回** `R=50`，再 rerank 到 `K=5`。  
[99 分数阈值](99.score-threshold-tutorial.md) 过高会导致 **有效 chunk 被丢弃**——trace 看 **被 threshold 截掉的候选**。

---

## 11. 修复 Playbook 与实验设计

1. **金标定位** `gold_chunk_id`（[160](143.golden-dataset-tutorial.md)）；  
2. **复现** 在调试台（路线图 199）；  
3. **假设** dense 漏 / sparse 漏 / filter / K 太小；  
4. **单变量实验**（[170 A/B](153.ab-experiment-rag-tutorial.md)）：一次只改 `hybrid` 或 `rewrite`；  
5. **指标**：Context Recall（[157](140.ragas-context-recall-tutorial.md)）、Recall@K；  
6. **登记** [171 参数版本](154.param-version-management-tutorial.md)。

---

## 12. 先错对对：六种典型翻车

### 12.1 错：未排除解析/切块就加 reranker

**对**：gold 句库内都搜不到 → 先 ingest。

### 12.2 错：只加向量不 BM25

**对**：单号、条款号场景 [92](92.sparse-retrieval-rag-tutorial.md) 常救场。

### 12.3 错：rewrite 改写过度改变意图

**对**：[100 篇](100.query-rewriting-tutorial.md) 护栏。

### 12.4 错：ACL filter 写错

**对**：trace 看 **filter 前后 count**。

### 12.5 错：top_k=3 硬编码

**对**：[98 Top-K](98.top-k-retrieval-tutorial.md) 按场景调。

### 12.6 错：换 Embedding 不重建索引

**对**：新模型 **全量 re-embed**。

---

## 13. 综合概念地图

![检索遗漏概念地图](image/bad-case-retrieval-miss/04-concept-map.png)

---

''' + common_faq("检索遗漏", [
    "**Q11：检索遗漏和 Context Recall 低是一回事吗？**  \n本质相关：金标上 Context Recall 量 **批次遗漏率**；单条 trace 是 **个例遗漏**。",
]) + r'''
## 15. 总结与系列下一步

1. **检索遗漏 = 有货没捞到**——先 trace，再决策树。  
2. **hybrid + 改写 + 宽召回 rerank** 是主流修复三板斧。  
3. 与 [149][150] 排除 ingest 问题后再调 C4/C5。  
4. 实验必须 [171 版本化](154.param-version-management-tutorial.md)。  
5. 仍漏 → [152] 看是否其实 **已命中但模型胡编**。

| 目标 | 阅读 |
|------|------|
| 混合检索 | [93 Hybrid](93.hybrid-search-tutorial.md) |
| 胡编归因 | [152 篇](152.bad-case-hallucination-tutorial.md) |
| A/B 实验 | [153 篇](153.ab-experiment-rag-tutorial.md) |

---

*系列：E 评测与观测 · 路线图第 168 条 · 主线篇*
'''

ARTICLE_152 = r'''# E 评测与观测（十四）：Bad Case 归因之生成胡编完全指南

> trace 显示 Top-3 **明确含有「年假 10 天」**，答案却写「根据规定为 15 天」——这不是 [151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)，是 **生成胡编**。用户截图骂幻觉，你若只会换模型，往往 **下周照旧**。这篇是路线图 **169**，主线篇，承接 [33 幻觉成因](33.llm-hallucination-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[112 拒答](112.refusal-strategy-tutorial.md)。用 [147/148](147.langsmith-tracing-tutorial.md) **对齐上下文与输出**。

---

## 目录

1. [前言：有资料仍胡编，最伤信任](#1-前言有资料仍胡编最伤信任)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [生成胡编在 RAG 中的定义](#3-生成胡编在-rag-中的定义)
4. [先排除：空检索与解析/切块](#4-先排除空检索与解析切块)
5. [trace 对齐：Faithfulness 现场核验](#5-trace-对齐faithfulness-现场核验)
6. [胡编分型：事实性 vs 忠实性](#6-胡编分型事实性-vs-忠实性)
7. [成因与杠杆对照 33 篇](#7-成因与杠杆对照-33-篇)
8. [Prompt、拒答与 Grounding](#8-prompt拒答与-grounding)
9. [采样、温度与长上下文](#9-采样温度与长上下文)
10. [Citation 与可核验输出](#10-citation-与可核验输出)
11. [修复 Playbook 与评测闭环](#11-修复-playbook-与评测闭环)
12. [先错对对：六种典型误判](#12-先错对对六种典型误判)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：有资料仍胡编，最伤信任

[33 篇](33.llm-hallucination-tutorial.md) 从 **模型续写本能** 讲胡编；RAG 工程师更关心 **可操作的子集**：

1. **无上下文胡编**：检索空或无关——根因常在 [151](151.bad-case-retrieval-miss-tutorial.md)；  
2. **有上下文胡编**：资料在 prompt 里，答案仍 **加数字、改条件、张冠李戴**——本篇重点。

**生成胡编（RAG 语境）**：检索提供的上下文中 **已包含** 可支撑答案的信息，但 LLM 输出与之 **矛盾或无法追溯** 的陈述。

---

## 2. 本文边界与动手路径

**档位：E 主线篇（169）。**

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 选一条「有引用仍错」的 trace | 截图归档 |
| B | 人工标注 context 是否含 gold | 是/否 |
| C | 若含 → 调 prompt / 温度 / [112 拒答](112.refusal-strategy-tutorial.md) | Faithfulness↑ |
| D | [141 RAGAS](141.ragas-faithfulness-tutorial.md) 批测 | 可量化 |

---

## 3. 生成胡编在 RAG 中的定义

![生成胡编是什么](image/bad-case-hallucination/01-hallucination-rag.png)

---

## 4. 先排除：空检索与解析/切块

**固定顺序**（避免冤枉模型）：

1. [149 解析](149.bad-case-parsing-tutorial.md)——库内 gold 句是否存在；  
2. [150 切块](150.bad-case-chunking-tutorial.md)——命中 chunk 是否语义完整；  
3. [151 检索](151.bad-case-retrieval-miss-tutorial.md)——gold 是否在 Top-K；  
4. **本篇**——Top-K 含 gold，答案仍错。

---

## 5. trace 对齐：Faithfulness 现场核验

![trace 对齐 Faithfulness](image/bad-case-hallucination/02-faithfulness-check.png)

在 [148 Langfuse](148.langfuse-observability-tutorial.md)：

1. 展开 **GENERATION** observation 的 **完整 prompt**；  
2. 高亮 gold 句是否在 `context` 块；  
3. 若 **被 [107 预算](107.context-budget-tutorial.md) 截断** → 先修预算/排序 [108](108.long-context-reorder-tutorial.md)；  
4. 若 **完整存在** → 生成胡编坐实。

**人工表**：

| 字段 | 值 |
|------|-----|
| gold_in_context | Y/N |
| answer_contradicts | Y/N |
| faithfulness | 0～1 |

---

## 6. 胡编分型：事实性 vs 忠实性

| 类型 | 上下文 | 例子 |
|------|--------|------|
| 事实性 | 无或无关 | 编造不存在的条款 |
| 忠实性 | 有 gold | 10 天答 15 天 |

RAG 坏案例 **忠实性占比更高**——更应用 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 与 [34 Grounding](34.grounding-citation-tutorial.md)。

---

## 7. 成因与杠杆对照 33 篇

![胡编成因杠杆](image/bad-case-hallucination/03-cause-levers.png)

| [33 篇](33.llm-hallucination-tutorial.md) 成因 | RAG 杠杆 |
|----------------|----------|
| 续写本能 | 强约束 prompt [110](110.rag-prompt-template-tutorial.md) |
| 温度高 | [29 采样](29.llm-sampling-tutorial.md) 降 temperature |
| 上下文太长 | [107 预算](107.context-budget-tutorial.md)、[108 重排](108.long-context-reorder-tutorial.md) |
| 冲突证据 | [106 去重](106.retrieval-dedup-tutorial.md)、[105 MMR](105.mmr-diversity-tutorial.md) |
| 过度自信 | [112 拒答](112.refusal-strategy-tutorial.md) |

---

## 8. Prompt、拒答与 Grounding

[110 RAG Prompt](110.rag-prompt-template-tutorial.md) 必备句：**「仅根据上下文回答；无则明确说不知道」**。  
[112 拒答策略](112.refusal-strategy-tutorial.md)：低相关度 hits 时 **拒答** 优于胡编。  
[34 Grounding](34.grounding-citation-tutorial.md) + [113 行内引用](113.inline-citation-tutorial.md)：要求 **每句关键事实带 [n]**，便于审计。

---

## 9. 采样、温度与长上下文

[29 篇](29.llm-sampling-tutorial.md)：RAG 事实问答 **temperature 0～0.3**；创意场景另路由。  
[28 窗口](28.context-window-tutorial.md)：证据被挤掉 → 模型 **靠 parametric 记忆补**。

---

## 10. Citation 与可核验输出

[113 行内](113.inline-citation-tutorial.md)、[114 脚注](114.footnote-citation-tutorial.md)、[115 导航](115.source-document-navigation-tutorial.md)：**UI 层** 让用户点穿核验。  
若模型 **引用 [1] 但内容来自 [3]** → **引用错位胡编**，查 prompt 编号与 chunk 顺序。

---

## 11. 修复 Playbook 与评测闭环

1. trace 核验 `gold_in_context`；  
2. 若否 → 回 [151](151.bad-case-retrieval-miss-tutorial.md)；  
3. 若是 → 调 prompt / 温度 / 拒答阈值；  
4. [141 Faithfulness](141.ragas-faithfulness-tutorial.md) + [163 TruLens](146.trulens-tutorial.md) Groundedness；  
5. [170 A/B](153.ab-experiment-rag-tutorial.md) 对比 `prompt_v2`；  
6. [171 版本](154.param-version-management-tutorial.md) 登记 `prompt_version`。

---

## 12. 先错对对：六种典型误判

### 12.1 错：检索空仍怪模型

**对**：先 [151](151.bad-case-retrieval-miss-tutorial.md)。

### 12.2 错：换更大模型不治本

**对**：强模型 **更会说谎**。

### 12.3 错：不加拒答

**对**：[112](112.refusal-strategy-tutorial.md)。

### 12.4 错：context 塞满无关 chunk

**对**：[105 MMR](105.mmr-diversity-tutorial.md)、精排 [95](95.cross-encoder-rerank-tutorial.md)。

### 12.5 错：流式未等 citations 就验收

**对**：[116 SSE](116.sse-rag-streaming-tutorial.md)。

### 12.6 错：无 Faithfulness 自动评

**对**：[141](141.ragas-faithfulness-tutorial.md) 批测。

---

## 13. 综合概念地图

![胡编 bad case 概念地图](image/bad-case-hallucination/04-concept-map.png)

---

''' + common_faq("生成胡编") + r'''
## 15. 总结与系列下一步

1. **生成胡编** 须在 **gold 已进 context** 前提下讨论。  
2. **决策树**：149 → 150 → 151 → **本篇**。  
3. **Faithfulness + 拒答 + 低温** 是第一修复组合。  
4. **观测**：[147/148](147.langsmith-tracing-tutorial.md) 对齐 prompt 与输出。  
5. 与 [33 幻觉理论](33.llm-hallucination-tutorial.md) 配合，形成 **理论+工单** 双轨。

| 目标 | 阅读 |
|------|------|
| 幻觉理论 | [33 幻觉](33.llm-hallucination-tutorial.md) |
| 检索遗漏 | [151 篇](151.bad-case-retrieval-miss-tutorial.md) |
| A/B | [153 篇](153.ab-experiment-rag-tutorial.md) |

---

*系列：E 评测与观测 · 路线图第 169 条 · 主线篇*
'''

ARTICLE_153 = r'''# E 评测与观测（十五）：RAG A/B 实验设计完全指南

> 「我把 top_k 从 5 改成 8，Faithfulness 好了！」——下周你发现 **延迟涨了 40%**，客服却说 **报销类反而更差**。没有 **对照、分流、显著性**，调参全靠感觉。这篇是路线图 **170**，地基篇，教你 **在 RAG 场景设计可信赖的 A/B 实验**：指标选什么、样本量 roughly 多少、如何与 [171 参数版本](154.param-version-management-tutorial.md)、[160 金标](143.golden-dataset-tutorial.md)、[147/148 观测](147.langsmith-tracing-tutorial.md) 联动。前置：[141 Faithfulness](141.ragas-faithfulness-tutorial.md)、[161 回归集](144.regression-test-set-tutorial.md)。

---

## 目录

1. [前言：没有对照的优化都是故事](#1-前言没有对照的优化都是故事)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [RAG A/B 实验是什么](#3-rag-ab-实验是什么)
4. [实验单元：请求、用户还是会话](#4-实验单元请求用户还是会话)
5. [指标金字塔](#5-指标金字塔)
6. [离线实验 vs 在线实验](#6-离线实验-vs-在线实验)
7. [单变量与参数隔离](#7-单变量与参数隔离)
8. [样本量与实验周期](#8-样本量与实验周期)
9. [分流、灰度与回滚](#9-分流灰度与回滚)
10. [与 LangSmith / Langfuse Experiments 衔接](#10-与-langsmith--langfuse-experiments-衔接)
11. [先错对对：七种实验谬误](#11-先错对对七种实验谬误)
12. [综合实战：hybrid 开关 A/B 设计书](#12-综合实战hybrid-开关-ab-设计书)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：没有对照的优化都是故事

RAG 可调旋钮太多：`chunk_size`、`top_k`、hybrid 权重、reranker、prompt 版本、temperature……  
**A/B 实验**：将流量 **随机分** 到控制组 A 与实验组 B，**除待测因子外其余配置锁定**，用 **预先定义的指标** 判断 B 是否优于 A。

**读完本文，你应该能做到：**

1. 写一份 **单变量** RAG A/B 设计书（§12 模板）。  
2. 选择 **主指标 + 护栏指标** 各至少一个。  
3. 说明离线金标实验与在线分流的 **分工**。  
4. 把实验组映射到 [171 param_version](154.param-version-management-tutorial.md)。  
5. 识别 §11 七种谬误（偷改多参、窥视提前停、忽略延迟等）。

---

## 2. 本文边界与动手路径

**档位：E 地基篇（170）。**

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 选一个旋钮（如 `use_hybrid`） | 单变量 |
| B | 写假设与指标 | 设计书 1 页 |
| C | 离线 [161 回归集](144.regression-test-set-tutorial.md) 跑 A/B | 表格式结果 |
| D | 在线 5% 灰度 7 天 | trace 带 `experiment` 标签 |

---

## 3. RAG A/B 实验是什么

![RAG A/B 实验是什么](image/ab-experiment-rag/01-ab-idea.png)

```text
请求 → 分流器（hash user_id）
  ├─ A: param_version=control
  └─ B: param_version=treatment_hybrid
→ 同一条 RAG 链路
→ 记录 trace + 指标
→ 分析显著性 / 业务决策
```

---

## 4. 实验单元：请求、用户还是会话

| 单元 | 适用 | 注意 |
|------|------|------|
| 请求 | 默认、简单 | 同一用户可能两边都体验 |
| 用户 | 体验一致 | hash `user_id` |
| 会话 | 多轮 [118](118.multi-turn-history-tutorial.md) | 同 session 不切换组 |

---

## 5. 指标金字塔

![RAG 指标金字塔](image/ab-experiment-rag/02-metrics-pyramid.png)

| 层级 | 指标 | 来源 |
|------|------|------|
| 北极星 | 用户满意度、点踩率 | [148 Score](148.langfuse-observability-tutorial.md) |
| 质量 | Faithfulness、Context Recall | [141](141.ragas-faithfulness-tutorial.md)、[157](140.ragas-context-recall-tutorial.md) |
| 检索 | Recall@K、MRR | 金标 |
| 护栏 | P95 延迟、token 成本 | trace |
| 安全 | 拒答率、越权 | [121](121.unauthorized-doc-filter-tutorial.md) |

**主指标一个**，护栏 **延迟和成本必看**——否则 Faithfulness 升 **业务不可用**。

---

## 6. 离线实验 vs 在线实验

| 类型 | 数据 | 优点 | 缺点 |
|------|------|------|------|
| 离线 | [160 金标](143.golden-dataset-tutorial.md)、[161 回归](144.regression-test-set-tutorial.md) | 快、便宜 | 覆盖有限 |
| 在线 | 真实流量 | 真实 | 慢、有风险 |

**推荐**：离线 **筛掉明显变差** → 在线 **小流量验证**。

---

## 7. 单变量与参数隔离

[171 篇](154.param-version-management-tutorial.md) 为 A/B **提供命名**：

```yaml
experiments:
  exp-2025-07-hybrid:
    control: pv-2025-06-01
    treatment: pv-2025-07-hybrid-on
```

**禁止**：B 组同时改 `top_k` + prompt + reranker——归因不可能。

---

## 8. 样本量与实验周期

粗略：若点踩率 5%→4%（绝对 1pp），常需 **数千～上万请求** 才稳定（视基线方差）。  
PoC：**离线 50～200 金标** + 在线 **5% 一周** 是务实起点。  
**不要** 第一天看赢就全量—— **窥视偏差**（§11）。

---

## 9. 分流、灰度与回滚

```python
import hashlib

def assign_group(user_id: str, exp: str) -> str:
    h = hashlib.sha256(f"{exp}:{user_id}".encode()).hexdigest()
    return "B" if int(h[:8], 16) % 100 < 10 else "A"  # 10% B
```

**回滚**：`treatment` 的 `param_version` **一键指回 control**；向量索引 **不删**，只切配置。

---

## 10. 与 LangSmith / Langfuse Experiments 衔接

[147 LangSmith](147.langsmith-tracing-tutorial.md) Datasets + Experiments：同一金标跑两 `param_version`。  
[148 Langfuse](148.langfuse-observability-tutorial.md)：trace `metadata.experiment=exp-hybrid`。  
与 [149～152 bad case](149.bad-case-parsing-tutorial.md)：**实验后** 低分 trace 仍走归因树。

---

## 11. 先错对对：七种实验谬误

1. **多变量齐改**  
2. **无护栏看延迟**  
3. **金标过拟合调参**  
4. **偷看中期结果提前停**  
5. **忽略星期/活动流量偏**  
6. **A/B 期间偷偷改 B**  
7. **不登记 param_version**

---

## 12. 综合实战：hybrid 开关 A/B 设计书

![A/B 设计书模板](image/ab-experiment-rag/03-experiment-doc.png)

| 字段 | 示例 |
|------|------|
| 假设 | hybrid 提升 Context Recall |
| 控制 A | `dense_only`, pv-2025-06-01 |
| 实验 B | `hybrid_rrf`, pv-2025-07-hybrid |
| 主指标 | Context Recall@5 |
| 护栏 | P95 latency < 3s |
| 流量 | 10% × 14 天 |
| 成功 | Recall +5pp 且延迟不超 |

---

## 13. 综合概念地图

![A/B 实验概念地图](image/ab-experiment-rag/04-concept-map.png)

---

''' + common_faq("A/B 实验") + r'''
## 15. 总结与系列下一步

1. **单变量 + 双环境指标** 是 RAG A/B 铁律。  
2. **离线筛 + 在线验** 节省成本。  
3. **param_version** 是实验的语言（[171](154.param-version-management-tutorial.md)）。  
4. **观测平台** 记录 `experiment` 标签。  
5. bad case 归因 **不因做实验而跳过**。

| 目标 | 阅读 |
|------|------|
| 参数版本 | [154 篇](154.param-version-management-tutorial.md) |
| 回归集 | [161 篇](144.regression-test-set-tutorial.md) |
| 检索遗漏 | [151 篇](151.bad-case-retrieval-miss-tutorial.md) |

---

*系列：E 评测与观测 · 路线图第 170 条 · 地基篇*
'''

ARTICLE_154 = r'''# E 评测与观测（十六）：RAG 参数版本管理完全指南

> 线上 Faithfulness 突然崩了，你翻 git 发现：上周有人改了 `chunk_overlap`、换了 Embedding 模型、还顺手调了 prompt——但 **索引没重建**、**没登记版本**、**A/B 还在跑旧配置**。这篇是路线图 **171**，地基篇，教你 **把 chunk、top_k、reranker、prompt、解析器策略** 收成 **可回滚的 param_version**，并与 [170 A/B](153.ab-experiment-rag-tutorial.md)、[147/148 trace](147.langsmith-tracing-tutorial.md)、[161 回归集](144.regression-test-set-tutorial.md) 对齐。前置：[138 配置驱动管道](138.config-driven-pipeline-tutorial.md)、[48 文档版本](48.doc-versioning-tutorial.md)。

---

## 目录

1. [前言：参数散落等于没有版本](#1-前言参数散落等于没有版本)
2. [本文边界与动手路径](#2-本文边界与动手路径)
3. [参数版本管理是什么](#3-参数版本管理是什么)
4. [哪些参数必须版本化](#4-哪些参数必须版本化)
5. [param_version 命名与清单](#5-param_version-命名与清单)
6. [与索引、Embedding 生命周期](#6-与索引embedding-生命周期)
7. [配置存储：YAML、DB 与 Git](#7-配置存储yamldb-与-git)
8. [trace 与评测绑定](#8-trace-与评测绑定)
9. [发布、灰度与回滚](#9-发布灰度与回滚)
10. [与文档版本 doc_version 的关系](#10-与文档版本-doc_version-的关系)
11. [先错对对：六种版本灾难](#11-先错对对六种版本灾难)
12. [综合实战：param manifest 示例](#12-综合实战param-manifest-示例)
13. [综合概念地图](#13-综合概念地图)
14. [常见陷阱与 FAQ](#14-常见陷阱与-faq)
15. [总结与系列下一步](#15-总结与系列下一步)

---

## 1. 前言：参数散落等于没有版本

RAG 不是「一个模型文件」，而是 **参数笛卡尔积**：

- Parser：`pymupdf` vs `pdfplumber`（[149 解析 bad case](149.bad-case-parsing-tutorial.md)）  
- Splitter：`chunk_size=512, overlap=64`（[150 切块](150.bad-case-chunking-tutorial.md)）  
- Embedder：`bge-m3` vs `text-embedding-3-small`（[25 Embedding](25.embedding-vector-tutorial.md)）  
- Retriever：`top_k=5`, `hybrid=true`（[151 检索](151.bad-case-retrieval-miss-tutorial.md)）  
- Reranker：`bge-reranker-v2`（[96 篇](96.bge-reranker-tutorial.md)）  
- Generator：`prompt_v3`, `temperature=0.1`（[152 胡编](152.bad-case-hallucination-tutorial.md)）

**param_version**：一条 **不可变** 的配置快照 ID，指向上述旋钮的 **完整组合** + **对应索引代数**。  
通俗说：**菜谱版本号**——不是只记「盐多了」，而是 **整道菜配方冻结**。

---

## 2. 本文边界与动手路径

**档位：E 地基篇（171）。**

### 2.1 动手路径

| 步骤 | 验收 |
|------|------|
| A | 写 `manifests/pv-2025-07-01.yaml` | 字段齐全 |
| B | API 响应带 `param_version` | 前端可展示 |
| C | trace metadata 同步 | 可筛选 |
| D | 模拟回滚 | 指回上一 pv |

---

## 3. 参数版本管理是什么

![参数版本管理是什么](image/param-version-management/01-param-version-idea.png)

**目标**：

1. **可复现**：任意历史问答知道 **当时用的哪套参**；  
2. **可对比**：[170 A/B](153.ab-experiment-rag-tutorial.md) 的 control/treatment 有名字；  
3. **可回滚**：新版本变差 **一键切回**；  
4. **可审计**：谁、何时、改了什么。

---

## 4. 哪些参数必须版本化

![必须版本化的参数](image/param-version-management/02-param-scope.png)

| 类别 | 参数 | 变更是否重索引 |
|------|------|----------------|
| Ingest | parser, ocr | 是 |
| Chunk | size, overlap, strategy | 是 |
| Embed | model, dim | 是 |
| Index | collection, metric | 常是 |
| Retrieve | top_k, hybrid, filter | 否 |
| Rerank | model, cutoff | 否 |
| Generate | prompt, temperature | 否 |

**铁律**：改左列 **必须新 pv + 重建**；只改右列可 **热切换**（仍应新 pv 登记）。

---

## 5. param_version 命名与清单

推荐：`pv-YYYY-MM-DD` 或 `pv-YYYY-MM-DD-hybrid`。**禁止** `latest` 作生产 tag。

**manifest 最小字段**：

```yaml
param_version: pv-2025-07-01
created_at: 2025-07-01T10:00:00Z
author: team-rag
parser: pymupdf-v1.24
chunk:
  policy: markdown-ast-v2
  size: 800
  overlap: 120
embedding:
  model: BAAI/bge-m3
  dimension: 1024
index:
  store: qdrant
  collection: handbook_v7
retrieve:
  top_k: 8
  hybrid: true
  rrf_k: 60
rerank:
  model: bge-reranker-v2-m3
  top_n: 5
generate:
  prompt_name: rag_v3
  temperature: 0.1
notes: "开启 hybrid，修复报销类检索遗漏"
parent_version: pv-2025-06-15
```

---

## 6. 与索引、Embedding 生命周期

换 Embedding 不换 collection 名 = **灾难**（[76 Chroma](76.chroma-vector-db-tutorial.md) §8）。  
**做法**：`collection` 或 `index_generation` 随 pv 递增；旧索引 **保留 N 天** 便于回滚。  
对接 [162 幂等重建](162.idempotent-reindex-tutorial.md)、[178 状态机](161.index-task-state-machine-tutorial.md)。

---

## 7. 配置存储：YAML、DB 与 Git

[138 配置驱动](138.config-driven-pipeline-tutorial.md)：Git 存 manifest **真源**；运行时 DB **当前 production 指针**。  
**环境**：`dev` 可浮动；`prod` **仅通过发布流程改指针**。

---

## 8. trace 与评测绑定

[147 LangSmith](147.langsmith-tracing-tutorial.md) / [148 Langfuse](148.langfuse-observability-tutorial.md)：

```json
{"metadata": {"param_version": "pv-2025-07-01"}}
```

[161 回归集](144.regression-test-set-tutorial.md) 跑分报告 **表头必含 pv**。  
bad case 工单（[149～152](149.bad-case-parsing-tutorial.md)）字段 **`param_version`**。

---

## 9. 发布、灰度与回滚

```text
draft manifest → 离线回归通过 → 灰度 5%（见 170 A/B）
  → 全量 → 标记 production
回滚：production 指针 ← parent_version（索引仍在）
```

---

## 10. 与文档版本 doc_version 的关系

[48 文档版本](48.doc-versioning-tutorial.md) 管 **内容**；`param_version` 管 **怎么切与怎么搜**。  
一条 trace 应同时有：`doc_version`（命中 chunk）、`param_version`（管道配置）。

---

## 11. 先错对对：六种版本灾难

1. **改 chunk 未重 embed**  
2. **prod 用 latest 标签**  
3. **A/B 两组共用一个 collection**  
4. **manifest 缺 rerank 字段**  
5. **回滚只改 prompt 未改索引指针**  
6. **trace 无 param_version**

---

## 12. 综合实战：param manifest 示例

见 §5 YAML。验收：从 API `/api/rag/ask` 响应读 `param_version`，在 Langfuse **按 pv 筛选** 上周 bad case。

---

## 13. 综合概念地图

![参数版本概念地图](image/param-version-management/04-concept-map.png)

---

''' + common_faq("参数版本") + r'''
## 15. 总结与系列下一步

1. **param_version = 全管道快照 + 索引代数**。  
2. **改 ingest/chunk/embed 必重建**。  
3. **trace / 回归 / A/B** 共用同一版本 ID。  
4. **doc_version** 与 **param_version** 分工明确。  
5. E 模块闭环：**金标 → 观测 → bad case → 实验 → 版本**。

| 目标 | 阅读 |
|------|------|
| A/B 实验 | [153 篇](153.ab-experiment-rag-tutorial.md) |
| 配置驱动 | [138 篇](138.config-driven-pipeline-tutorial.md) |
| 人工评测 | [155 篇](155.human-evaluation-rag-tutorial.md) |

---

*系列：E 评测与观测 · 路线图第 171 条 · 地基篇*
'''


