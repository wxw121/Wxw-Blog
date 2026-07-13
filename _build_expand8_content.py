# -*- coding: utf-8 -*-
"""Build large unique expand8 blocks."""
from pathlib import Path
import re

def sec(n, title, paras):
    return f"## {n}. {title}\n\n" + "\n\n".join(paras) + "\n"

# Per-slug extra paragraphs (unique, substantive)
EXTRA = {
    "langchain-document-loader": [
        "企业 wiki 导出 HTML 时，Loader 前置 BeautifulSoup 提取 article#main，剥离 script/style，再写 TextLoader 可读文本，避免导航链接污染检索。",
        "邮件 eml 解析：提取正文与附件路径，附件按扩展名递归 pick_loader，metadata 写 thread_id 与 message_id 供会话级过滤。",
        "数据库 BLOB 字段：自定义 Loader 写临时文件，parse 后删除，防磁盘占满；doc_id 用表主键而非自增 id 字符串化。",
        "多语言混目录：metadata.lang 由文件名前缀或 CMS 字段写入，供 130 Splitter 选分隔符与 70 混合 embed 路由。",
        "Loader 性能：IO 线程池并行读文件，CPU 密集 Parser 用进程池，embed 才是总耗时大头。",
        "密码 PDF：解密服务前置，Loader 只读已解密路径，解密失败进死信并通知文档 Owner。",
        "增量删除：CMS 下架触发 webhook，索引按 doc_id 删除向量行，manifest 标 deleted_at。",
        "合规：Loader 输出过 DLP 扫描，敏感字段打标或拒载，与 122 内容安全衔接。",
        "测试：fixtures 含 utf-8/gbk/空pdf/扫描件，CI 断言 metadata Schema 与预期 mime。",
        "与 136：ParserLoader 薄包装，parse 逻辑单测不依赖 langchain。",
        "运营 preview：Loader 后展示前 500 字与 metadata，确认后再 Splitter。",
        "统计：每周空文本率、乱码率、缺字段率周报，联动 149 bad case。",
    ],
    "langchain-text-splitter": [
        "制度库中文分隔符加顿号、分号，英文文档加句号空格，混合库按 metadata.lang 切换 REGISTRY 项。",
        "代码块 fence 检测后块内不再切，API 文档问示例代码时可整段命中。",
        "表格 markdown 检测 |---| 作为原子单元，或转 CSV 一行一条 metadata sidecar。",
        "法条编号正则切分保留条款标题与正文同 chunk，避免只有「第一条」无内容。",
        "幻灯片转 md 后按 ## 切，单页过长再 Recursive 细切。",
        "chunk_id 格式 doc_id:cNNNN 零填充，便于排序与增量覆盖。",
        "overlap 80 时观察 Top-8 是否同 section 重复，配合 105 MMR。",
        "Token 切分 tiktoken 模型名与 embed 一致，防 cl100k 与 o200k 混用。",
        "金标网格：size 300-1200 step 100，overlap 0-150 step 40，记录 Recall@5。",
        "改 splitter 版本 bump manifest，通知重建索引与 48 文档版本。",
        "Parent child：child 入 VectorStore，parent 存 docstore，metadata parent_id 必填。",
        "审计：抽 50 chunk 人工看句界，样例存 144 回归集。",
        "与 58 手写递归 diff 首尾边界，差异可接受再切 LC。",
        "拒绝过小 chunk：少于 50 字与下一块合并，减噪声。",
    ],
    "llamaindex-index-types": [
        "VectorStoreIndex 构建消耗 embed 配额，大库分批 insert 并打 job 进度。",
        "Node relationships 用于图索引，向量主路径可忽略，面试提一句即可。",
        "KeywordTableIndex 类似 BM25，LC 用 BM25Retriever 更常见。",
        "TreeIndex 查询从根向下，延迟难控，生产少用。",
        "SummaryIndex 适合总页数少全文摘要 demo，长库撞 28 窗口。",
        "storage_context.vector_store 接 Chroma 时路径与 LC 128 统一。",
        "ComposableGraph 路由错误会答非所问，需金标验证路由质量。",
        "LI 与 LC 不双写同一请求，135 单栈纪律。",
        "读 LI 示例先找 from_documents 与 as_query_engine 两处。",
        "迁移：nodes 导出 jsonl，LC from_documents 重建。",
        "两小时学习：官方 Indexing 章 + 本篇 demo + 映射表。",
        "面试：主线 LC，了解 LI 索引类型与 Node 概念。",
        "备份：向量在后端，策略同 90 向量库备份。",
        "embed 构建期与查询期模型必须一致，与 25 篇同律。",
        "完成 148 条：demo + 映射 + 不双栈声明。",
    ],
    "llamaindex-query-engine": [
        "RetrieverQueryEngine 显式拆 retriever 与 synthesizer，排障先查 retrieve 是否空。",
        "SimilarityPostprocessor 阈值按模型校准，不可抄教程 0.7。",
        "SubQuestionQueryEngine 多路检索合并，成本高于 103 固定分解。",
        "ChatEngine 多轮是否重检索写进产品 PRD，与 118 一致。",
        "streaming_response 迭代 token 对接 116 SSE 事件枚举。",
        "source_nodes score 不可跨 embed 模型比较，只同模型调阈值。",
        "compact 模式控制 source 数量，防 107 预算爆炸。",
        "refine 多轮合成引用易漂移，制度 FAQ 不推荐。",
        "CustomQueryEngine 适合插自定义拒答与 citations 格式。",
        "观测：retrieve_ms、synth_ms、node_ids 写入 147 trace。",
        "金标：LI 与 LC 同题比 Recall 与 Faithfulness。",
        "混合检索：LI 换 retriever 组件，LC 用 EnsembleRetriever。",
        "rerank 插在 retrieve 后 synthesize 前，与 95 篇一致。",
        "空检索：EmptyResponse 模板，不走 LLM 编造。",
        "迁移 LCEL：五步清单见本篇 36 节，wiki 存档。",
        "面试：熟 LCEL，了解 Response 与 source_nodes。",
        "阅读：Query Engine 入门 30 分钟 + 画 LC 等价图 30 分钟。",
        "生产：不默认 Query Engine 黑盒，要可审计链。",
    ],
    "llamaindex-agent": [
        "ReActAgent verbose 仅 dev 开启，prod 脱敏 thought。",
        "max_iterations=3 常见，配合总 deadline 120s。",
        "QueryEngineTool 内 Retriever 必须 filter ACL，与 121 一致。",
        "工具 schema 校验参数，非法返回错误 observation 供重试。",
        "多工具时 description 区分域，防选错财务库。",
        "Agent 成本按 session 汇总，148 看板设预算告警。",
        "对外 API 默认固定 RAG，Agent 灰度内部工具。",
        "与 124 tool loop 治理同构：迭代上限、超时、ACL。",
        "固定 104 多跳管道可控，Agent 探索用。",
        "演练：越权 query 应拒答或空结果，不得泄露 finance chunk。",
        "CI：mock LLM 与 mock tool，不依赖 live API。",
        "trace：每轮 tool_name、args_hash、chunk_ids。",
        "完成 150 条：ReAct demo + checklist + 对比多跳。",
        "时间盒：实验 ≤2h，回 127 固定链。",
        "面试：知道循环与风险，生产固定链优先。",
    ],
    "haystack-pipeline": [
        "Haystack @component 装饰器声明输入输出类型，connect 编译期检查。",
        "FileConverter 链：pdf→text，等价 Loader+Parser。",
        "DocumentCleaner 去空白，等价 46 清洗。",
        "DualRetriever + Joiner 图画给评审，标注 94 RRF。",
        "Ranker 等价 95 cross-encoder，在 Joiner 后。",
        "PromptBuilder 模板版本化，对齐 110 与 154 参数表。",
        "pipeline.dumps YAML 运维改 top_k，动机同 138 配置。",
        "组件单测 run 快照，借鉴到 Parser 契约测试。",
        "on_error skip 仅非关键 enrich，Retriever 失败 fail fast。",
        "不必引入 haystack 包，学拓扑即可。",
        "手绘 ingest/query 两图是本篇交付。",
        "与 135 联读：单栈、评测、回滚。",
        "4h 阅读 Haystack 2 文档 + 手绘。",
        "面试：能画 DAG 并映射 LCEL。",
        "完成 151 条：两图 + 不双栈说明。",
        "ES 双写示例对照 82 与 93 混合检索。",
        "Generator 温度 0 利于 141 Faithfulness 回归。",
    ],
    "pipeline-vs-framework": [
        "10 人团队：LC+Chroma PoC，Parser 尽快 136 协议化。",
        "100 人金融：ACL 审计自研，LLM 走 167 网关。",
        "技术债：升级断链、双栈、无金标——冻结功能还债。",
        "PR 五问：边界、剔框架两周、Schema、回归、trace。",
        "ARCHITECTURE 一页：分层、RACI、回滚、评测门禁。",
        "A/B：纯 LC vs 自研检索+LC，153 设计实验。",
        "并购：chunk 向量金标可导出写进合同。",
        "培训：on-call 会 76 与 128 原生 API。",
        "产品法务：架构表译风险速度成本三列。",
        "完成 152 条：分层表 + 工作坊记录。",
        "下一读 136 Parser 协议落地。",
    ],
    "pluggable-parser-splitter-embedder": [
        "Parser Protocol：parse(path)→RawDocument，schema_version 字段。",
        "Splitter Protocol：split(raw)→list[Chunk]，保留 doc_id acl。",
        "Embedder Protocol：dimension、embed_texts、embed_query 对称。",
        "REGISTRY 三类实现，build_pipeline 从 yaml 组装。",
        "契约测试三件套 fixtures，CI 阻断 merge。",
        "manifest：parser、splitter、embedder、chunk_count、created_at。",
        "FakeEmbedder dimension=128 供 CI 无 GPU。",
        "HTTP Parser Adapter 超时熔断 fallback plain。",
        "LC：Loader/Splitter/Embeddings 适配器各 ≤80 行。",
        "ingest：parse→split→embed→137 Store upsert。",
        "换 embed 新 collection，旧库只读。",
        "失败：Parser 跳过文件进 163 死信。",
        "与 57-65 C 轨映射写 wiki REGISTRY 表。",
        "完成 153 条：REGISTRY+契约+manifest+128 联调。",
        "下游 137 Store Retriever Generator 对称。",
    ],
    "langchain-vectorstore": [
        "本篇已达标，expand8 仅收束提示。",
    ],
}

content = {}
for slug, paras in EXTRA.items():
    blocks = []
    for i in range(0, len(paras), 3):
        chunk = paras[i : i + 3]
        n = 33 + i // 3
        blocks.append(sec(n, f"工程深化（{slug.split('-')[0]}）", chunk))
    content[slug] = "".join(blocks)

lines = ["# -*- coding: utf-8 -*-", '"""Expand8 large unique blocks."""', "", "EXPANSIONS8 = {"]
for k, v in content.items():
    lines.append(f'    "{k}": """{v.strip()}""",')
lines.append("}")
Path("_articles_128_136_expand8.py").write_text("\n".join(lines), encoding="utf-8")
for k, v in content.items():
    print(k, len(re.findall(r"[\u4e00-\u9fff]", v)))
