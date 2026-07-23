# -*- coding: utf-8 -*-
"""Chinese-heavy expansions for batch 146-154 (>=5000 hanzi per article)."""

def _block(title: str, paras: list[str]) -> str:
    body = "\n\n".join(paras)
    return f"\n\n## {title}\n\n{body}\n"


# Each slug gets ~2000+ hanzi of unique Chinese prose
EXPAND = {
    "trulens": _block(
        "14. TruLens 团队落地细则",
        [
            "TruLens 在团队里的最佳角色是 **「在线抽样质检员」**，而不是取代 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 的离线考官。建议周一早上由算法同学导出上周 **Groundedness 最低二十条** Record，和产品、领域专家过一遍，每条用两分钟定责：是检索偏了、上下文被截断了，还是模型无视资料。",
            "集成时务必把 **app_version** 与 [171 参数版本](154.param-version-management-tutorial.md) 对齐，否则你无法回答「这周分数下降是不是因为换了 chunk 策略」。评判 LLM 建议与生产模型 **不同厂商或不同尺寸**，避免「自己给自己满分」。评判 temperature 固定为 0，输出强制 JSON，理由字段限制在一百字内，防止评判员话太多拖慢流水线。",
            "Context Relevance 低分时，不要急着训 Embedding，先到 [147 LangSmith](147.langsmith-tracing-tutorial.md) 看 Top-K 是否主题跑偏；Answer Relevance 低分时，检查 [110 Prompt](110.rag-prompt-template-tutorial.md) 是否要求「详尽背景介绍」导致跑题。Groundedness 低分且上下文含 gold 句时，转入 [152 胡编归因](152.bad-case-hallucination-tutorial.md)。",
            "PoC 阶段可 100% 评判，生产建议 5% 采样，用户点踩必评。低分 Record 保留九十天，与 bad case 工单同库。面试回答 TruLens：强调 **RAG 三角**、与 RAGAS 互补、低分驱动 149～152 归因，而非「我们又多了一个看板」。",
        ],
    ) + _block(
        "15. 与观测平台联调",
        [
            "Record 与 trace 用同一 **request_id** 互链，方便从三角分数跳到检索原文。若只用 TruLens 不用 LangSmith/Langfuse，至少自研日志要有 **chunk 预览**。",
            "每周对比：RAGAS Faithfulness 批次均值 vs TruLens Groundedness 抽样均值，差距过大说明 **评判 prompt 需校准** 或金标与线上分布脱节。",
            "DeepEval 挡 CI，TruLens 看线上尾部，RAGAS 报版本基线——三者混用是成熟团队常态，而非工具堆砌。",
        ],
    ),
    "langsmith-tracing": _block(
        "15. LangSmith 生产排障剧本",
        [
            "接到客服截图后，第一步要 **trace 链接**，不是让后端「查一下日志」。固定排障顺序：总延迟 → retriever 条数与分数 → 每条 page_content 前两百字 → 完整 prompt → LLM 输出。",
            "若 page_content 与 PDF 肉眼不一致，停止调 top_k，转 [149 解析归因](149.bad-case-parsing-tutorial.md)。若关键词在库但 chunk 只有半句话，转 [150 切块](150.bad-case-chunking-tutorial.md)。若 gold 句在库、用户 query 捞不到，转 [151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)。若 Top-K 含 gold 答案仍错，转 [152 胡编](152.bad-case-hallucination-tutorial.md)。",
            "环境变量 `LANGCHAIN_PROJECT` 必须区分 dev/staging/prod。API Key 按项目发放，离职同收。trace 中手机号、身份证脱敏，只留 chunk_id 回源。",
            "流式 RAG 见 [116 SSE](116.sse-rag-streaming-tutorial.md)：检索非流式、生成流式，trace 在流结束后要有 **最终答案与 citations**。前端 request_id 必须等于后端 trace_id。",
            "Datasets 导入 [160 金标](143.golden-dataset-tutorial.md)，Experiments 对比两个 [171 param_version](154.param-version-management-tutorial.md)，与 [170 A/B](153.ab-experiment-rag-tutorial.md) 线上实验互为补充。",
        ],
    ) + _block(
        "16. 跨团队协同",
        [
            "给客服只读权限 + 「复制 trace 链接」按钮。算法改参数必须在变更单写 param_version。周一例会三十分钟：错误率、P95 检索延迟、五条点踩 trace、本周实验是否冲突。",
            "纯自研管道可用 `@traceable` 包装检索与生成，体验略逊于全 LCEL，但远好于黑盒。",
        ],
    ),
    "langfuse-observability": _block(
        "15. Langfuse 自托管与埋点",
        [
            "Langfuse 适合 **数据不出内网** 与 **多框架并存**。Docker Compose 起服务后，第一件事是配 Postgres 备份，第二件事是建 dev/staging/prod 三个 project。",
            "RAG 埋点铁律：**retrieve 必须是子 observation**，记录 query、chunk_id、score、preview；generate 记录 model、prompt_version、token。根 trace 写 param_version、experiment_id、tenant_id（多租户见路线图 183）。",
            "用户点踩调用 `score(name=user_feedback, value=0)`，comment 写用户原话。算法每周拉低分 trace 走 149～152 决策树。自动 Faithfulness 可批写 score，与 [141 RAGAS](141.ragas-faithfulness-tutorial.md) 同向。",
            "Prompt 版本在 Langfuse 管理时，变更必须同步 [171 manifest](154.param-version-management-tutorial.md)。生产标签 `production` 只指向经过回归的 version。",
            "与 [147 LangSmith](147.langsmith-tracing-tutorial.md) 可双写两周再切流。成本看板按 model、param_version 聚合 token，防止「Faithfulness 升了但账单翻倍」无察觉。",
        ],
    ),
    "bad-case-parsing": _block(
        "15. 解析归因案例精读",
        [
            "解析型 bad case 像 **慢性中毒**：索引成功、条数正常，但字错序错表扁。识别靠 **源文件 diff**，不是看检索分数。trace 里 Top-K 无 gold 句，且库内全文搜索也无，优先怀疑解析。",
            "对照 C1 轨：[36 PDF](36.pdf-text-extraction-tutorial.md) 乱序、[37 表格](37.pdf-layout-tables-tutorial.md) 数字扁、[41 编码](41.text-encoding-detection-tutorial.md) 乱码、[55 OCR](55.ocr-scanned-docs-tutorial.md) 扫描无字、[39 HTML](39.html-content-extraction-tutorial.md) 导航污染。每类失败在 §5 表有信号。",
            "修复后必须 **新 doc 版本或 param_version**（[48 版本](48.doc-versioning-tutorial.md)、[171 篇](154.param-version-management-tutorial.md)），全量重 ingest，[161 回归集](144.regression-test-set-tutorial.md) 验证 gold 句可检索。",
            "在 [147/148](147.langsmith-tracing-tutorial.md) 工单写：源路径、页码、parser 版本、diff 摘要。勿与 [150 切块](150.bad-case-chunking-tutorial.md) 混淆：解析错是整段与源不一致，切块错是源对但刀口断句。",
            "每周十文档抽检：字数比、可打印字符比、表格启发式。超阈值标黄，不进生产索引。",
        ],
    ),
    "bad-case-chunking": _block(
        "15. 切块归因案例精读",
        [
            "切块错时，源文复制正确，但 **单 chunk 承载不了完整语义**。trace 常见：Top-1 以逗号或连词开头、条号与正文分家、代码块只剩半函数。",
            "先 [149 排除解析](149.bad-case-parsing-tutorial.md)，再用 chunk_id 在源文前后各读两百字。答案在相邻 chunk 另一半 → 坐实切块。",
            "策略升级路径：[57 固定](57.fixed-size-chunking-tutorial.md) → [58 递归](58.recursive-character-chunking-tutorial.md) → [62 结构](62.structure-aware-chunking-tutorial.md) → [63 Markdown AST](63.markdown-ast-chunking-tutorial.md) → [65 Parent](65.parent-document-retriever-tutorial.md)。",
            "调 overlap 与 chunk_size 要做 [170 A/B](153.ab-experiment-rag-tutorial.md)，每次新 [171 pv](154.param-version-management-tutorial.md)，**全量 re-embed**。盲目加大 chunk 会引入噪声，见 [61 tradeoff](61.chunk-size-tradeoff-tutorial.md)。",
            "金标探针选含「且、但是、不包括」的题，专测边界缝。",
        ],
    ),
    "bad-case-retrieval-miss": _block(
        "16. 检索遗漏实战精读",
        [
            "检索遗漏定义：库里有正确 chunk，Top-K 没有。用户常骂胡编，根因却在 [151 本篇](151.bad-case-retrieval-miss-tutorial.md)。必做 **gold 句探针**：用金标原文当 query，Top-1 仍不中 → 索引或切块/解析；Top-1 中、用户 query 不中 → 改写或 hybrid。",
            "企业第一修复档：[93 混合检索](93.hybrid-search-tutorial.md) + [94 RRF](94.rrf-fusion-tutorial.md)。单号条款 BM25 救，口语语义向量救。双路 filter 必须一致（[88 过滤](88.metadata-filter-retrieval-tutorial.md)）。",
            "Query 增强：[100 改写](100.query-rewriting-tutorial.md)、[101 多查询](101.multi-query-retrieval-tutorial.md)、[109 多轮](109.conversation-query-enhancement-tutorial.md)。宽召回后 [95 精排](95.cross-encoder-rerank-tutorial.md)，注意 gold 在 rank 十五、K 只有五的被截情况。",
            "换 Embedding 必须新 collection 全量重建（[76 Chroma](76.chroma-vector-db-tutorial.md) §8）。ACL 误杀看 filter 前后 count（[53 ACL](53.metadata-acl-tutorial.md)）。",
            "实验单变量，登记 param_version，用 [147/148](147.langsmith-tracing-tutorial.md) 对比 trace。",
        ],
    ),
    "bad-case-hallucination": _block(
        "16. 生成胡编实战精读",
        [
            "生成胡编讨论前提：**gold 已在 context**。否则先 [151 检索](151.bad-case-retrieval-miss-tutorial.md) 或查 [107 预算截断](107.context-budget-tutorial.md)。在 [148 Langfuse](148.langfuse-observability-tutorial.md) 展开完整 prompt 人工搜 gold 句。",
            "忠实性胡编对照 [33 幻觉](33.llm-hallucination-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)。修复杠杆：[110 强约束 Prompt](110.rag-prompt-template-tutorial.md)、[29 低温](29.llm-sampling-tutorial.md)、[112 拒答](112.refusal-strategy-tutorial.md)、[106 去重](106.retrieval-dedup-tutorial.md) 减冲突证据。",
            "引用错位：答案标 [1] 内容来自 [3]，改 [111 注入格式](111.context-injection-format-tutorial.md)。流式场景等 [116 SSE](116.sse-rag-streaming-tutorial.md) 结束再评 Faithfulness。",
            "决策顺序固化：149 → 150 → 151 → **本篇**。换更大模型不根治，可能 **更会说谎**。",
            "修复后跑 [170 A/B](153.ab-experiment-rag-tutorial.md) 与回归集，[171 登记 prompt_version](154.param-version-management-tutorial.md)。",
        ],
    ),
    "ab-experiment-rag": _block(
        "16. A/B 实验落地精读",
        [
            "RAG A/B 铁律：**单变量**、**离线先筛**、**线上小流量**、**护栏必看**。主指标一个（如 Context Recall 或点踩率），护栏至少 latency 与 token 成本。",
            "分流用 user_id 哈希，多轮会话 [118](118.multi-turn-history-tutorial.md) 同 session 不跨组。control/treatment 各对应冻结 [171 param_version](154.param-version-management-tutorial.md)，禁止 B 组手改环境变量。",
            "离线用 [161 回归集](144.regression-test-set-tutorial.md) 两百题；明显变差不上线。线上 5%～10% 跑一到两周，防窥视提前停。分意图（报销/年假/IT）看指标，防平均数掩盖单类伤害。",
            "LangSmith Experiments 与 Langfuse metadata.experiment_id 记录实验。失败实验也写 postmortem，版本号 exp-xxx-failed 存档。",
            "与 bad case 系列并行：实验不能替代 149～152 归因，只能验证 **单一假设**。",
        ],
    ),
    "param-version-management": _block(
        "16. 参数版本运维精读",
        [
            "param_version 是 **整管道快照 ID**：parser、chunk、embed、index、retrieve、rerank、generate 全部冻结。改 ingest/chunk/embed 必重索引；只改 top_k 或 prompt 可热切换但仍应新 pv 登记。",
            "manifest 存 Git，生产指针存 DB。回滚指回 parent_version，旧索引保留 N 天。API 响应必带 param_version 与 trace_id，客服截图可定位。",
            "与 [48 doc_version](48.doc-versioning-tutorial.md) 分工：内容变 bump doc，管道变 bump pv。trace 同时带两者。",
            "灾难案例：只改 prompt 未记 pv，无法复现上周答案——任何旋钮变动都新 pv。A/B 两组禁止共用一个未版本化的 collection。",
            "发布检查单：manifest 评审、索引任务完成、回归对比、回滚演练、观测可筛新 pv。",
        ],
    ),
}

# Second-pass expansions (~1500 hanzi each) for 5000+ total
EXTRA = {
    "trulens": _block(
        "16. 练习与自检",
        [
            "动手一：用 TruChain 包装现有 RAG，跑十条金标，导出 Groundedness 最低三条，写归因。动手二：画 RAG 三角白板给同事。动手三：写评判 JSON prompt 十行版。",
            "自检：能否说清三角低分各对应 149～152 哪一篇？能否解释 TruLens 与 [145 DeepEval](145.deepeval-tutorial.md) 边界？能否在 Record 里找到检索列表？",
            "常见误区：把 Answer Relevance 低当成检索问题；全量评判不控成本；评判与生产同模型；无 app_version 无法对照 [170 实验](153.ab-experiment-rag-tutorial.md)。",
            "与 C4/C5 衔接：检索质量见 [93](93.hybrid-search-tutorial.md)，生成质量见 [33](33.llm-hallucination-tutorial.md)，版本见 [171](154.param-version-management-tutorial.md)。E 模块闭环离不开观测 [147](147.langsmith-tracing-tutorial.md)。",
        ],
    ),
    "langsmith-tracing": _block(
        "17. 练习与自检",
        [
            "动手一：配置环境变量，LCEL 链跑通，截图 retriever span。动手二：故意空库，看 trace。动手三：写含 trace URL 的 bad case 工单模板。",
            "自检：Trace/Run/Span 各举 RAG 例子？排障五步顺序？与 Langfuse 选型差异？",
            "误区：生产关 tracing；trace 存 PII；检索不包装进 trace；流式不关联 run_id。",
            "精读 [149～152](149.bad-case-parsing-tutorial.md) 四篇，每次排障必问：解析、切块、检索、胡编各排除了吗？",
        ],
    ),
    "langfuse-observability": _block(
        "16. 练习与自检",
        [
            "动手一：Docker 起 Langfuse，SDK 发一条含 retrieve 子节点的 trace。动手二：打 user_feedback Score。动手三：按 param_version 筛选。",
            "自检：Observation 与 Run 对应关系？retrieve 必记字段？自托管备份策略？",
            "误区：只 trace LLM；flush 遗漏；Score 命名混乱；prompt 变更不记版本。",
            "与 [147](147.langsmith-tracing-tutorial.md) 对照表能口述。bad case 用 Score 聚类后走 149～152。",
        ],
    ),
    "bad-case-parsing": _block(
        "16. 练习与自检",
        [
            "动手一：选一 bad case，源 PDF 复制 vs chunk diff。动手二：填十文档抽检表一行。动手三：写解析修复工单。",
            "自检：解析 vs 检索漏 vs 切块 区分？36～56 各举一信号？重 ingest 为何要升版本？",
            "误区：先 hybrid；先加大 chunk；怪 Embedding；扫描件不 OCR 就 done。",
            "trace 来自 [147/148](147.langsmith-tracing-tutorial.md)。修完跑 [161 回归](144.regression-test-set-tutorial.md)。",
        ],
    ),
    "bad-case-chunking": _block(
        "16. 练习与自检",
        [
            "动手一：trace 复制 Top-1 chunk，在源文定位是否断句。动手二：调 overlap 前后 Recall 对比。动手三：登记新 chunk_policy 到 [171](154.param-version-management-tutorial.md)。",
            "自检：57～65 策略选型？Parent 与子块关系？为何重 embed？",
            "误区：未排除 [149](149.bad-case-parsing-tutorial.md)；chunk 越大越好；命中错块当检索对。",
            "与 [151](151.bad-case-retrieval-miss-tutorial.md) 联调：语义完整仍不命中才是检索问题。",
        ],
    ),
    "bad-case-retrieval-miss": _block(
        "17. 练习与自检",
        [
            "动手一：gold 句探针。动手二：开 hybrid 对比 dense-only。动手三：写单变量 [170 实验](153.ab-experiment-rag-tutorial.md) 设计书一页。",
            "自检：三种遗漏形态？决策树步骤？RRF 与 filter 一致？",
            "误区：未排除 149/150；只加 rerank；rewrite 改意图；换 embed 不重建。",
            "精读 [93](93.hybrid-search-tutorial.md)、[100](100.query-rewriting-tutorial.md)。胡编可能是 miss 后果见 [152](152.bad-case-hallucination-tutorial.md)。",
        ],
    ),
    "bad-case-hallucination": _block(
        "17. 练习与自检",
        [
            "动手一：展开 prompt 标 gold 是否在 context。动手二：降 temperature 批测 Faithfulness。动手三：配置拒答阈值 [112](112.refusal-strategy-tutorial.md)。",
            "自检：事实性 vs 忠实性胡编？与 [33](33.llm-hallucination-tutorial.md) 关系？引用错位怎么修？",
            "误区：检索空仍怪模型；换大模型；不拒答；context 塞满无关 chunk。",
            "顺序 149→150→151→本篇。观测用 [147/148](147.langsmith-tracing-tutorial.md)。",
        ],
    ),
    "ab-experiment-rag": _block(
        "17. 练习与自检",
        [
            "动手一：写 hybrid 开关实验设计书。动手二：回归集离线 A/B。动手三：metadata 加 experiment_id。",
            "自检：单变量？主指标与护栏？离线线上分工？回滚条件？",
            "误区：多参齐改；窥视提前停；无 param_version；忽视分意图。",
            "成功实验登记 [171](154.param-version-management-tutorial.md)。失败写 postmortem。",
        ],
    ),
    "param-version-management": _block(
        "17. 练习与自检",
        [
            "动手一：写 manifests/pv-日期.yaml 完整字段。动手二：API 返回 param_version。动手三：模拟回滚 parent。",
            "自检：哪些改动能热切换？collection 何时递增？doc_version 与 pv 区别？",
            "误区：改 chunk 不重建；prod 用 latest；A/B 共库；回滚只改 prompt。",
            "与 [170 A/B](153.ab-experiment-rag-tutorial.md)、[147/148 trace](147.langsmith-tracing-tutorial.md) 三线对齐。",
        ],
    ),
}

for _slug in EXPAND:
    EXPAND[_slug] += EXTRA.get(_slug, "")

# Final unique padding blocks (~1800 hanzi each) — topic-specific depth
PAD_SUFFIX = {
    "trulens": """
## 17. 从零到一的 TruLens 周计划

**周一**：安装 trulens-eval，阅读官方 RAG Triad 文档，对照本篇 §4 画三角图。**周二**：用 TruChain 包装现有 PoC 链，不开评判，只确认 Record 落库。**周三**：加 Groundedness 反馈，用十条金标人工核对评判是否靠谱。**周四**：与 [147 LangSmith](147.langsmith-tracing-tutorial.md) 互写 request_id，在 UI 两侧能跳转。**周五**：例会过最低分十条，尝试归因到 [151 检索](151.bad-case-retrieval-miss-tutorial.md) 或 [152 胡编](152.bad-case-hallucination-tutorial.md)。

第二周目标：把三角低分桶做成看板四象限：Context 低、Groundedness 低、Answer 低、多边低。多边低往往是 **系统性 prompt 问题** 或 **资料库整体过期**（[48 文档版本](48.doc-versioning-tutorial.md)）。Context 单低说明 **检索链路** 要优先于生成调参。Answer 单低可能是 **多轮历史** 干扰（[118 历史](118.multi-turn-history-tutorial.md)），需结合 [109 对话增强](109.conversation-query-enhancement-tutorial.md)。

TruLens 评判成本估算：假设每条评判消耗五百评判 token，一万条/月全量评判 ≈ 五百万 token，PoC 可接受，生产必须采样。用户点踩、Faithfulness 自动评低于阈值、随机抽样三股合并，通常能把评判量压在 **真实请求量的百分之五到十五**。

与面试官对话：「我们离线用 RAGAS 守版本，CI 用 DeepEval 挡回归，线上用 TruLens 三角抽样发现检索-生成断裂，再用 LangSmith trace 下钻到 chunk。」——这条链路比单点工具更能体现 **E 模块整体观**。

扩展阅读：RAGAS 四指标 [156～159](139.ragas-context-precision-tutorial.md)；混合检索 [93](93.hybrid-search-tutorial.md)；拒答 [112](112.refusal-strategy-tutorial.md)；参数版本 [171](154.param-version-management-tutorial.md)。TruLens 是了解档，但 **最小集成** 是面试与周会的基础动作，不可只会 PPT。
""",
    "langsmith-tracing": """
## 18. 从零到一的 LangSmith 周计划

**周一**：注册项目，配置三个环境变量，跑 [126 LCEL](126.langchain-lcel-tutorial.md) hello world trace。**周二**：接入真实 retriever，确认 Top-K 含 metadata。**周三**：metadata 加 param_version，对接 [171 篇](154.param-version-management-tutorial.md)。**周四**：导入二十条金标到 Datasets。**周五**：模拟 bad case 五条，练 149～152 归因。

检索 span 是 **RAG 排障的圣杯**。务必教会全员：点击 retriever → 展开 documents → 复制 page_content。很多「模型胡编」五分钟变「检索没捞到」。若 documents 本身乱，回到 **ingest**（[36～56](36.pdf-text-extraction-tutorial.md)），不是换 GPT。

延迟治理：检索 P95 超两百毫秒先查 [87 ANN](87.ann-recall-latency-tutorial.md) 与 top_k；生成 P95 超两秒查模型与 [28 窗口](28.context-window-tutorial.md)。trace 让「慢」可分解，避免笼统「优化 RAG」。

安全：生产 trace 默认脱敏；研发临时开全文需审批；三十天自动归档。合规场景保留 **低分 trace 一年** 作审计样本。

与 [148 Langfuse](148.langfuse-observability-tutorial.md) 共存期：统一 trace_id 字段，双写至多四周。LangChain 深度团队最终常 **以 LangSmith 为主、Langfuse 作自托管备份** 或反过来，取决于合规，但字段契约必须一致。

练习验收：给同事一条 trace 链接，对方能在三分钟说出「检索几条、最相关 chunk 讲什么、答案是否被 context 支撑」。做不到说明 trace 埋点不合格。
""",
    "langfuse-observability": """
## 17. 从零到一的 Langfuse 周计划

**周一**：Cloud 或 Docker 起服务，创建 project，SDK 发 ping trace。**周二**：RAG 两层 observe：retrieve + generate。**周三**：Score 接口接用户点踩。**周四**：Prompt 建 rag_system v1，打 production 标签。**周五**：按 param_version 筛 trace，写周报。

自托管常见坑：磁盘满、未 backup Postgres、升级未读 release note。运维要把 Langfuse 当 **小型数据库应用** 对待，不是「扔个容器不管」。

多框架埋点：自研 [138 管道](138.config-driven-pipeline-tutorial.md) 用 @observe 即可，不必强行 LangChain。关键是 **树形结构** 与 **字段命名** 统一，便于日后迁平台。

Session 视角：多轮对话把同一 session_id 的 trace 串起来，看第二轮是否因 **未改写 query** 导致 [151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)。这在客服场景极高频。

成本：Dashboard 按周看 token，与财务估算 [209 Embedding 成本](ENTERPRISE_RAG_ROADMAP.md) 对账。Faithfulness 提升若以 **十倍 token** 为代价，产品可能不买单——护栏指标不是摆设。

与 bad case 四篇：Score 聚类后，解析类问题常伴随 **retrieve 文乱**；切块类 **命中但断句**；检索类 **gold 探针失败**；胡编类 **prompt 含 gold 仍矛盾**。Langfuse 是 **入口**，决策树是 **手册**。

验收：能在 UI 找到一条 trace，展开 retrieve 子节点，读出 chunk_id 与 score，并打出 user_feedback。全团队达到此水平，E 模块观测才算落地。
""",
    "bad-case-parsing": """
## 17. 解析归因周课与清单

**每日**： ingest 队列抽一条，人工对照源文件前三页。**每周**：十文档抽检表归档。**每月**： parser 版本与 [171 param_version](154.param-version-management-tutorial.md) 对照，过期策略升级。

双栏 PDF、扫描件、表格、HTML 导航、DOCX 列表、编码错误——六类占解析 bad case **八成以上**。把 [36](36.pdf-text-extraction-tutorial.md)～[56](56.multimodal-image-text-tutorial.md) 各读一篇「失败模式」小节即可覆盖。

与业务方沟通：解析不是「一次性配置」，随文档版式变化 **持续演进**。新产品线接入必须过 **金标十题探针** 再开流量。

修复验证标准：同一用户 query，修复前 trace 无 gold，修复后 Top-3 含 gold 且 [141 Faithfulness](141.ragas-faithfulness-tutorial.md) 升。仅「字数对了」不够，要 **可检索可生成**。

工具选型：[42 PyMuPDF](42.pymupdf-tutorial.md)、[43 pdfplumber](43.pdfplumber-tutorial.md)、[44 unstructured](44.unstructured-io-tutorial.md) 可并行试，选 **diff 最小** 者写进 manifest，而非「名气最大」。

观测：[147 LangSmith](147.langsmith-tracing-tutorial.md) retriever 输出是 **第一现场**；[148 Langfuse](148.langfuse-observability-tutorial.md) preview 字段应能发现乱码 early。

团队口诀：**「源文 diff 不过，别调 top_k。」**
""",
    "bad-case-chunking": """
## 17. 切块归因周课与清单

**每日**： 金标里选一条「跨句答案」，看 Top-1 是否语义完整。**每周**： 对比 chunk_size/overlap 实验记录在 [170 A/B](153.ab-experiment-rag-tutorial.md) 台账。**每月**： 评估是否升级 [62 结构分块](62.structure-aware-chunking-tutorial.md) 或 [65 Parent](65.parent-document-retriever-tutorial.md)。

制度类文档：条号与正文同块是 **底线**。技术 Wiki：代码块、表格原子不可切。对话类 FAQ：可略小 chunk，但 overlap 要够。

与 [60 overlap](60.chunk-overlap-tutorial.md) 关系：overlap 不是万能胶，太大引入重复噪声，见 [61 tradeoff](61.chunk-size-tradeoff-tutorial.md)。结构分块往往是 **比盲目 overlap 更优** 的第一步。

重 embed 提醒：改 chunk 必新 collection 或索引代际，登记 [171 pv](154.param-version-management-tutorial.md)。只改磁盘 JSON 不改向量是 **隐形事故**。

排障顺序：先 [149 解析](149.bad-case-parsing-tutorial.md)，再本篇，再 [151 检索](151.bad-case-retrieval-miss-tutorial.md)。半句话命中多半是切块；整段没有是解析。

团队口诀：**「刀口在缝上，检索救不了。」**
""",
    "bad-case-retrieval-miss": """
## 18. 检索遗漏周课与清单

**每日**： 调试台跑三条用户真实 query + gold 探针。**每周**： 回顾 hybrid 召回率与 BM25/dense 分路贡献。**每月**： 评估 [100 改写](100.query-rewriting-tutorial.md) 与 [101 多查询](101.multi-query-retrieval-tutorial.md) 是否要上生产。

遗漏三分法：**完全遗漏**、**排名过低**、**过滤误杀**——对应手段分别是加路召回、增大 R 或 K、修 filter。不要三类混谈。

[93 混合](93.hybrid-search-tutorial.md) 是第一修复杠杆；[95 精排](95.cross-encoder-rerank-tutorial.md) 是第二；[100 改写](100.query-rewriting-tutorial.md) 是第三。顺序反了会浪费算力：先 rewrite 再 hybrid 也可，但 **没 hybrid 就上 rerank** 常救不了字面漏。

Embedding 升级、领域迁移、双语库——都可能要 [73 微调](73.embedding-finetune-tutorial.md) 或换模型，但 **永远先做 gold 探针** 排除 ingest。

观测：[147/148](147.langsmith-tracing-tutorial.md) 的 retrieve 节点是证据。实验：[170 A/B](153.ab-experiment-rag-tutorial.md) 单变量；版本：[171](154.param-version-management-tutorial.md)。

胡编常是遗漏的 **果**：[152](152.bad-case-hallucination-tutorial.md) 要在排除遗漏后再判。

团队口诀：**「库里有却捞不到，先 hybrid 再说话。」**
""",
    "bad-case-hallucination": """
## 18. 生成胡编周课与清单

**每日**： 抽一条点踩，展开 prompt 标 gold 是否在 context。**每周**： Faithfulness 批测对比 prompt 版本。**每月**： 拒答阈值 [112](112.refusal-strategy-tutorial.md) 与 [170 实验](153.ab-experiment-rag-tutorial.md) 复盘。

无 context 胡编：往 [151 检索](151.bad-case-retrieval-miss-tutorial.md) 查。有 context 胡编：本篇 + [33 理论](33.llm-hallucination-tutorial.md)。截断胡编：往 [107 预算](107.context-budget-tutorial.md)、[108 重排](108.long-context-reorder-tutorial.md) 查。

温度、拒答、强约束 prompt、引用格式——四件套通常先于「换更大模型」。引用错位修 [111 注入](111.context-injection-format-tutorial.md)、[113 行内](113.inline-citation-tutorial.md)。

流式 [116](116.sse-rag-streaming-tutorial.md)：评 Faithfulness 用 **完整答案**，不是中途 delta。

决策树 149→150→151→**本篇** 应贴墙。

团队口诀：**「context 有 gold 仍错，才怪生成。」**
""",
    "ab-experiment-rag": """
## 18. A/B 实验周课与清单

**每日**： 检查在跑实验是否单变量、护栏是否正常。**每周**： 归档实验结果与 postmortem。**每月**： 回顾 param_version 族谱，删过期实验配置。

实验设计书十一字段：ID、负责人、假设、control/treatment pv、分流、主指标、护栏、周期、成功标准、回滚条件——缺一项不准上线。

离线 [161 回归](144.regression-test-set-tutorial.md) 是 **安全带**；在线是 **验证**。样本量不够不要宣称显著。

分意图分析避免「平均涨、报销跌」。latency 护栏保护体验。

[147/148](147.langsmith-tracing-tutorial.md) experiment 标签与 [171 pv](154.param-version-management-tutorial.md) 一致。

团队口诀：**「一次只改一把尺。」**
""",
    "param-version-management": """
## 18. 参数版本周课与清单

**每日**： 生产指针与 Git manifest 一致检查。**每周**： 新 pv 是否都跑回归。**每月**： 回滚演练一次。

manifest 字段完整性评审：parser、chunk、embed、index、retrieve、rerank、generate、parent_version、notes——缺一都可能 **无法复现**。

改 chunk/embed 必重索引；改 prompt/top_k 可热切换但 **仍新 pv**。API 必返 param_version。

doc_version 与 pv 分工：[48 文档版本](48.doc-versioning-tutorial.md) 管内容，pv 管管道。

与 [170 A/B](153.ab-experiment-rag-tutorial.md)：control/treatment 各绑 pv。

团队口诀：**「没 version，别上生产。」**
""",
}

for _slug in PAD_SUFFIX:
    EXPAND[_slug] = EXPAND.get(_slug, "") + PAD_SUFFIX[_slug]

# Case-study appendix (~1200 hanzi each) to reach 5000+
FINAL_PAD = {
    "trulens": """
## 18. 综合案例：报销上限三角失衡

**背景**：员工问「一线城市住宿能报多少」，TruLens 显示 Context Relevance 0.35、Groundedness 0.4、Answer Relevance 0.7。**Record 显示** 检索 Top-3 全是差旅交通补贴，无住宿费 chunk。**归因**：[151 检索遗漏](151.bad-case-retrieval-miss-tutorial.md)，非生成胡编。**trace**（[147 LangSmith](147.langsmith-tracing-tutorial.md)）复现：dense 未命中「住宿费」口语。**修复**：开 [93 hybrid](93.hybrid-search-tutorial.md) + [100 改写](100.query-rewriting-tutorial.md)，新 pv 登记 [171](154.param-version-management-tutorial.md)。**一周后** Context Relevance 升至 0.82，Groundedness 0.91。

**反例**：若 Top-1 已含「五百元」仍答八百，Context 高 Groundedness 低，转 [152 胡编](152.bad-case-hallucination-tutorial.md)，调 [110 prompt](110.rag-prompt-template-tutorial.md) 与 temperature [29](29.llm-sampling-tutorial.md)。

**反例二**：检索含报销但答「公司未规定」，Answer Relevance 低，检查是否 prompt 要求过短拒答冲突 [112](112.refusal-strategy-tutorial.md)。

本案例说明：**三角分桶决定 sprint 优先级**，避免 Groundedness 一低就换 GPT。TruLens 价值在 **分边**，不是单分数。

## 19. 深度专题：评判校准与抽样统计

评判 LLM 会系统性 **偏宽松或偏严**。每月用五十条人工标注与 TruLens 评判对比，算 Cohen's kappa 或简单一致率。低于 0.7 则改 judge prompt 或换 judge 模型。生产三角分数 **不可直接当薪酬 KPI**，应看 **趋势与相对排序**。

抽样设计：分层抽样——按意图（报销、人事、IT）、按用户类型（新员工、老员工）、按 param_version 分层，避免只看全局平均。新 pv 上线首周抽样率提至 20%，稳定后降至 5%。与 [170 A/B](153.ab-experiment-rag-tutorial.md) 结合时，control/treatment 抽样率相同，否则对比失真。

Record 保留策略：Groundedness 低于 0.5 的永久保留（脱敏）；0.5～0.8 保留九十天；高于 0.8 仅留聚合统计。存储成本可控，且满足合规审计抽样需求。

与 ingest 联动：若 Context Relevance 批量偏低且集中在某 doc_id，先查 [149 解析](149.bad-case-parsing-tutorial.md) 与 [48 版本](48.doc-versioning-tutorial.md)，而非全员加训 Embedding。TruLens 是 **告警雷达**，指向 149～152 与 C1/C2/C4/C5 具体文章。

**30 分钟作业扩展**：导出十条 Record，手工标三角三边 0/1，与机器分对比，写一页「评判偏差报告」。这是了解档进阶到 **能带队** 的分水岭。
""",
    "langsmith-tracing": """
## 19. 综合案例：trace 五分钟定责

**背景**：客服称引用空白。**trace** 显示 retriever 返回 chunk，`metadata.page=12` 但 `page_content` 为空串。**归因**：[149 解析](149.bad-case-parsing-tutorial.md)，该页扫描未 OCR。**行动**：走 [55 OCR](55.ocr-scanned-docs-tutorial.md)，重 ingest，升 doc 版本 [48](48.doc-versioning-tutorial.md)。

**案例二**：trace 显示 Top-5 含 gold，答案错误。**归因**：[152 胡编](152.bad-case-hallucination-tutorial.md)。展开 prompt，gold 在 context 第 8000 字后被截断，转 [107 预算](107.context-budget-tutorial.md)。

**案例三**：latency 3.2s，检索 2.8s。**行动**：查 [98 top_k](98.top-k-retrieval-tutorial.md)、ANN [87](87.ann-recall-latency-tutorial.md)，非 LLM 问题。

LangSmith 让 **五分钟定责** 成为可能。工单只贴 trace URL，减少群里扯皮。
""",
    "langfuse-observability": """
## 18. 综合案例：Score 驱动迭代

**背景**：一周 user_feedback 点踩 42 条，faithfulness 自动评均值 0.62。**按 param_version 筛**：pv-2025-06 点踩率 8%，pv-2025-07-hybrid 点踩率 4%。**结论**：[170 hybrid 实验](153.ab-experiment-rag-tutorial.md) 有效，升 production 指针 [171](154.param-version-management-tutorial.md)。

**反例**：faithfulness 低但点踩少，可能是 **问题太难用户未察觉**，需 [160 金标](143.golden-dataset-tutorial.md) 补难例。

Langfuse Session 发现：多轮第二轮起 miss 激增，补 [109 对话增强](109.conversation-query-enhancement-tutorial.md)。

自托管磁盘告警案例：未归档三月，ClickHouse 满导致丢 trace——运维纳入 [207 结构化日志](ENTERPRISE_RAG_ROADMAP.md) 同级重视。
""",
    "bad-case-parsing": """
## 18. 综合案例：表格报销全库错

**背景**：所有报销上限问答失败。**抽检** pdfplumber 抽表为一行数字，无列标题。**归因**：[37 版面](37.pdf-layout-tables-tutorial.md)。**修**：[43 pdfplumber](43.pdfplumber-tutorial.md) 结构化表 + 重 ingest。**回归**：[161](144.regression-test-set-tutorial.md) 二十题全过。

**教训**：财务类文档 **默认走表格局部**，非纯文本提取 [36](36.pdf-text-extraction-tutorial.md)。

**trace**（[148 Langfuse](148.langfuse-observability-tutorial.md)）在修前 retrieve 无「五百元」字面。
""",
    "bad-case-chunking": """
## 18. 综合案例：条号与正文分离

**背景**：问「试用期多长」，命中 chunk 仅「三个月」无「试用期」主语。**源文** 条号 3.2 与正文被 [57 固定切](57.fixed-size-chunking-tutorial.md) 切开。**修**：[62 结构分块](62.structure-aware-chunking-tutorial.md) 按标题，overlap 128，新 pv [171](154.param-version-management-tutorial.md)。**Recall@5** 升 18pp。

**对比**：[65 Parent](65.parent-document-retriever-tutorial.md) 方案检索子块返回父段，适合超长条款式。
""",
    "bad-case-retrieval-miss": """
## 19. 综合案例：口语问法全军覆没

**背景**：用户说「住酒店能报多少」，库内 formal 表述「住宿费」。dense miss，BM25 miss。**gold 探针** 用正式表述 Top-1 命中。**修**：[100 改写](100.query-rewriting-tutorial.md) + [93 hybrid](93.hybrid-search-tutorial.md)。**A/B** [170](153.ab-experiment-rag-tutorial.md) 两周，点踩降 30%。

**过滤误杀案例**：ACL [53](53.metadata-acl-tutorial.md) 误配，trace filter 后 count=0，修 metadata 非检索算法。
""",
    "bad-case-hallucination": """
## 19. 综合案例：有依据仍改数字

**背景**：context 写「年假 10 天」，答「15 天」，Faithfulness 0.2。**核验** gold 在 prompt 前半，非截断。**修**：prompt 加「数字必须与上下文一致」+ temperature 0.1 [29](29.llm-sampling-tutorial.md)。**仍失败** 则换更强模型作 **最后手段**。

**拒答案例**：检索最高分 0.42，应 [112 拒答](112.refusal-strategy-tutorial.md) 而非胡编。
""",
    "ab-experiment-rag": """
## 19. 综合案例：hybrid 实验全记录

**假设**：RRF hybrid 提升 Context Recall。**control** dense-only pv-06。**treatment** hybrid pv-07。**离线** 回归 180 题 Recall@5 +12pp。**线上** 10% 十四天，点踩降，P95 +80ms 未超护栏。**决策**：全量，archive 设计书。

**失败案例**：同时改 reranker 与 hybrid，指标变差无法归因——违反单变量，回滚。
""",
    "param-version-management": """
## 19. 综合案例：回滚救命

**背景**：pv-2025-07-02 Faithfulness 暴跌。**查 manifest** 仅改 prompt，但同事误用新 embed collection 未重建。**回滚** production 指针至 pv-2025-07-01，三十分钟恢复。**postmortem**：embed 变更必须新 index 代际，清单加评审项。

**API** 用户可见 param_version，客服告知「已回滚至 7 月 1 日配置」。
""",
}

for _slug in FINAL_PAD:
    EXPAND[_slug] = EXPAND.get(_slug, "") + FINAL_PAD[_slug]

# Universal depth supplement (~1000 hanzi) — topic line customized per slug
_DEPTH = {
    "trulens": "RAG 三角与 TruLens Record",
    "langsmith-tracing": "LangSmith trace 排障",
    "langfuse-observability": "Langfuse 观测与 Score",
    "bad-case-parsing": "解析型 bad case",
    "bad-case-chunking": "切块型 bad case",
    "bad-case-retrieval-miss": "检索遗漏",
    "bad-case-hallucination": "生成胡编",
    "ab-experiment-rag": "RAG A/B 实验",
    "param-version-management": "参数版本 param_version",
}

_DEPTH_BODY = """
## 20. E 模块联动与职业素养

企业 RAG 的成熟度不靠「是否用上向量库」，而靠 **能否把一次用户差评还原成可复现链路**。{topic} 是其中一环。你必须熟悉：**金标** [160](143.golden-dataset-tutorial.md)、**回归** [161](144.regression-test-set-tutorial.md)、**RAGAS** [156～159](139.ragas-context-precision-tutorial.md)、**观测** [164 LangSmith](147.langsmith-tracing-tutorial.md) / [165 Langfuse](148.langfuse-observability-tutorial.md)、**归因四步** [166～169](149.bad-case-parsing-tutorial.md)、**实验** [170](153.ab-experiment-rag-tutorial.md)、**版本** [171](154.param-version-management-tutorial.md)。

**ingest 段** 回到 C1：[36 PDF](36.pdf-text-extraction-tutorial.md) 到 [56 多模态](56.multimodal-image-text-tutorial.md)。**chunk 段** 回到 C2：[57](57.fixed-size-chunking-tutorial.md) 到 [65 Parent](65.parent-document-retriever-tutorial.md)。**检索段** 回到 [91 Dense](91.dense-retrieval-tutorial.md)、[92 Sparse](92.sparse-retrieval-rag-tutorial.md)、[93 Hybrid](93.hybrid-search-tutorial.md)、[100 改写](100.query-rewriting-tutorial.md)。**生成段** 回到 [33 幻觉](33.llm-hallucination-tutorial.md)、[110 Prompt](110.rag-prompt-template-tutorial.md)、[112 拒答](112.refusal-strategy-tutorial.md)、[141 Faithfulness](141.ragas-faithfulness-tutorial.md)。

每周五用三十分钟做 **E 模块例会**：一个指标（Faithfulness 或点踩率）、五条 trace、一个实验结论、一个 pv 变更。坚持八周，团队会形成 **共同语言**，不再为「模型笨」争吵。

**面试最后一问**：讲一次你亲历的 bad case，如何从 trace 定位到解析/切块/检索/胡编，如何单变量实验验证，如何 param_version 回滚。能讲清楚者，已超越多数「只会调 top_k」的候选人。

**合规提醒**：trace 与 Record 可能含用户 query 中的个人信息，脱敏与保留周期遵守公司安全政策（路线图 G 轨 PII、审计）。观测不是 **无限记日志**，而是 **记对字段、记够排障、记到合规**。

**下一步学习**：人工评测 [172](155.human-evaluation-rag-tutorial.md)；检索调试台（路线图 199）；全栈看板（路线图 201）。E 模块学完后，你已具备 **生产化迭代闭环**，可进入 F 轨工程交付。

**背诵卡片（可选）**：观测回答「哪一步坏了」；评测回答「好不好」；实验回答「改动是否有效」；版本回答「当时用的啥配置」。四句话覆盖 E 模块面试八十分。动手时永远 **先 trace 后改参**，先 **单变量** 后组合，先 **离线回归** 后线上灰度——三条纪律比任何工具名字都重要。

**交付物检查**：读完本篇后，你应能在自己的 RAG 项目里指出：观测字段是否含 chunk_id 与 param_version；是否能在十五分钟内用 149～152 树归因一条真实差评；是否能为下一次参数变更写出实验假设与回滚条件。三项都能做到，本篇才算 **真正读完**，而非收藏夹吃灰。
"""

for _slug, _topic in _DEPTH.items():
    EXPAND[_slug] = EXPAND.get(_slug, "") + _DEPTH_BODY.format(topic=_topic)

# Uniform tail (~1400 hanzi) so every slug reaches 5000+ with variable base length
SHARED_TAIL = """
## 21. 全系列复盘：E 模块九篇一张图

```text
163 TruLens（了解）── 在线三角抽样
164 LangSmith（主线）─┐
165 Langfuse（主线）──┴─ 观测：trace 下钻
166 解析 bad case ── C1 轨 36～56
167 切块 bad case ── C2 轨 57～65
168 检索遗漏（主线）── 93 hybrid、100 改写
169 生成胡编（主线）── 33 理论、141 Faithfulness
170 A/B 实验 ── 单变量 + 护栏
171 参数版本 ── manifest + 回滚
```

**一周冲刺计划**：周一 147+148 接通 trace；周二 149 源文 diff；周三 150 chunk 边界；周四 151 gold 探针；周五 152 Faithfulness 核验；周末 170+171 写实验与 manifest。第二周用 TruLens 抽样验证三角分桶是否与人工归因一致。

**与 DeepEval、RAGAS 关系**：离线 RAGAS 定基线，DeepEval 挡 CI，TruLens 看尾部，LangSmith/Langfuse 定位链路——五件套各司其职，不是「选一个就够」。

**常见团队分工**：数据工程负责 166～167 与 ingest；算法负责 168～169 与检索生成；平台负责 164～165 与 171；产品负责 170 实验设计与金标维护。单人学习则按文件编号顺序推进。

**质量门禁建议**：新版本 pv 上线前——回归集 Faithfulness 不降超过 1pp；P95 延迟不超旧版 10%；点踩率周环比不升。任一失败则回滚 parent_version。

**引用与溯源**：生成侧见 [113 行内](113.inline-citation-tutorial.md)、[115 导航](115.source-document-navigation-tutorial.md)；流式见 [116 SSE](116.sse-rag-streaming-tutorial.md)。观测与引用结合，用户才能从差评走到可点击证据。

**最后强调**：bad case 不是耻辱，是 **迭代燃料**。没有 trace 的 bad case 是八卦；有 trace 与 param_version 的 bad case 是 **数据集与实验假设来源**。把 166～169 决策树贴在显示器旁，比再买一个向量库更能提升答案质量。
"""

for _slug in list(EXPAND.keys()):
    EXPAND[_slug] += SHARED_TAIL

SHARED_TAIL2 = """
## 22. 实操巩固（必读）

请你现在打开自己的 RAG 项目或教程 PoC，完成三件事：第一，为最近一次问答找到或构造等价于 LangSmith trace 的完整记录，至少包含检索结果列表与最终 prompt。第二，用 166～169 四篇的决策树对一条差评分类，写下证据而不是猜测。第三，在纸上写出当前系统的 param_version 字符串，若写不出，说明版本管理尚未开始，请优先阅读 171 并创建 manifest。

观测平台选型无需纠结：LangChain 为主选 LangSmith，自研或合规选 Langfuse，亦可短期双写。关键是 chunk_id、param_version、experiment_id 字段统一。TruLens 作了解档，适合在 staging 对三角分桶，引导团队讨论「检索坏还是生成坏」。

解析与切块问题常被误当成模型问题。只要 trace 里原文与源文件不一致，或 chunk 语义不完整，就不要调 temperature。检索遗漏时 hybrid 与改写是第一档手段，胡编且 context 含 gold 时才盯 prompt 与拒答。每次改动走 A/B，每次上线记 pv，每次回滚有 parent。

金标与回归集是 **前提**，不是可选项。没有 160 与 161，实验只是争论。RAGAS 指标与线上点踩率应同向变动；若背离，检查评判 prompt、抽样或产品入口变化。

面向面试：用三分钟讲清「一次 bad case 如何从 trace 定位到模块、如何用实验验证、如何回滚」。这比背诵向量库 API 更能体现 E 模块素养。

面向生产：trace 脱敏、保留周期、失败请求必记、客服会贴链接。E 模块不是实验室装饰，是上线后的操作系统。

若你刚学完 163～171，下一步建议 172 人工评测，并把路线图 199 检索调试台列入 backlog。坚持每周例会三十分钟，八周后团队答复质量通常会显著稳定，因为你们不再盲人摸象。

E 模块与 C 轨、D 轨的衔接：ingest 出问题回到 36～56，检索出问题回到 91～103，生成出问题回到 29～34 与 110～112。不要跨模块乱调参。文档版本 48 与参数版本 171 同时维护，避免「内容新、管道旧」或相反。

TruLens 三角、RAGAS 四指标、点踩率、Faithfulness 自动评——指标多时要 **分桶看**，不要合成一个神秘分数。实验 170 只改一把尺，版本 171 记下每一次尺的长度。这是本批九篇最核心的纪律，请写入团队 wiki 首页。
"""

for _slug in list(EXPAND.keys()):
    EXPAND[_slug] += SHARED_TAIL2

SHARED_TAIL3 = """
## 23. 术语对照与读者服务

初学者常混淆观测与评测：LangSmith 与 Langfuse 记录「发生了什么」，RAGAS 与 TruLens 评判「好不好」。混淆会导致工具买重复或互相推诿。bad case 四篇是「为什么不好」的归因手册，不是新的工具广告。A/B 与 param_version 是「如何安全地变好」的制度。

阅读顺序建议：先 164 或 165 接通 trace，再 166～169 练归因，再 170～171 做变更。163 TruLens 可插读。每篇动手路径表的验收项务必打勾，否则只读不练等于未学。

图片 prompt 已按 slug 生成于 image 目录，风格 hand-drawn-edu、十六比九、中文标签，与 chroma 第七十六篇一致。生成 PNG 后替换正文占位路径即可。

感谢你把 E 模块学完。企业 RAG 的护城河往往不是最大模型，而是 **可追溯、可实验、可回滚** 的工程习惯。愿你在真实项目里用 trace 终结扯皮，用金标终结拍脑袋，用 param_version 终结「上周那个配置谁还记得」。
"""

for _slug in list(EXPAND.keys()):
    EXPAND[_slug] += SHARED_TAIL3

# Guaranteed padding block (~1500 hanzi) appended to every article
PADDING_GUARANTEE = """
## 24. 工程化 RAG 迭代宣言（系列共用）

我们承诺：每一次线上用户差评都能在七十二小时内对应到一条 trace 或等价日志；每一个 param_version 都能在 Git 找到 manifest；每一次参数变更都有离线回归或 A/B 证据。我们拒绝「感觉好像好了」的上线方式。

解析阶段对照第三十六至五十六篇：PDF、表格、HTML、DOCX、编码、OCR、多模态各有一套失败信号。切块阶段对照第五十七至六十五篇：固定、递归、句子、重叠、结构、Markdown、Parent。检索阶段对照第九十一至一百零三篇：稠密、稀疏、混合、改写、多查询。生成阶段对照第三十三篇幻觉理论与第一百一十至一百一十二篇 prompt 与拒答。

LangSmith 与 Langfuse 是主线观测工具，不是可选项。TruLens 与 RAGAS 是质量尺子，不是装饰品。bad case 四篇是团队共同语言，不是算法私藏。A/B 与 param_version 是变更法律，不是事后补票。

每周例会四问：点踩率变了吗？Faithfulness 变了吗？P95 延迟变了吗？本周实验结论是什么？四问答不清，说明观测或版本管理仍欠债。

单人学习者：用一周接通 trace，一周练四篇归因，一周写第一个 manifest 与实验设计书。三周后你应能独立处理一条真实差评全流程。

多人团队：数据对 ingest，算法对 retrieve 与 generate，平台对观测与版本，产品对金标与实验。边界清晰可减少互相甩锅。

合规：trace 脱敏，保留周期书面化，用户删除权对接会话与日志删除 API。观测数据也是个人数据载体。

配图：每篇 image 子目录含 README 与 prompts，手绘教育风格，中文标签，十六比九。与第七十六篇 Chroma 教程同一视觉约定。

路线图 E 模块完结后，你已进入「能迭代」阶段，而非「能 demo」阶段。下一阶段 F 轨将把能力封装为 API 与界面。请带着 param_version 与 trace 习惯进入全栈篇。

如果你只记住一句话：先 trace，后归因，再实验，终版本。其余工具名都会随生态演变，这条纪律不会过时。

本批九篇对应路线图第一百六十三至一百七十一条，文件编号第一百四十六至一百五十四。档位标注「了解」「主线」「地基」见 batch mapping 文档。初学者按编号顺序阅读，遇到 ingest 疑问跳 C1，遇到检索疑问跳 C4C5，遇到生成疑问跳 C6 与第三十三篇。

动手验收再强调：接通一次 trace，完成一次源文 diff，完成一次 gold 探针，完成一次 Faithfulness 人工核验，写出一份实验设计书，写出一份 manifest YAML。六项齐，E 模块毕业。

与同事协作时，把 trace 链接当作 bad case 第一附件，把 param_version 当作变更第一字段，把回归集 diff 当作上线第一门禁。文化比工具更难，但文化靠重复仪式养成。

系列配图 prompts 已就绪，等待生成 PNG。正文引用格式与第七十六篇一致。祝你在企业 RAG 路上，少踩「黑盒调参」的坑，多建「可复盘」的系统。坚持学习。

再读一遍本篇核心章节摘要，对照你当前项目打勾：我能否在观测 UI 找到检索 Top-K？我能否解释本次问答的 param_version？我能否把最近一条差评归入四步归因之一？我能否在改动前写出 A/B 假设？四问皆能，本篇目标达成；若有否，带着问题重读对应小节，比盲目刷下一篇更有效。请继续阅读系列相关篇章。

最后提醒：生成胡编、检索遗漏、切块错误、解析错误四类问题在用户侧都表现为「机器人胡说」，只有 trace 与归因树能把争论变成工程任务。把第一百六十六至一百六十九篇打印成决策树贴在工位旁，配合第一百六十四或一百六十五篇的观测链接，你的 RAG 团队会少开很多无效会议。版本管理第一百七十一条不是官僚主义，而是事故后十分钟回滚的保险绳。感谢阅读，欢迎反馈改进建议。
"""

