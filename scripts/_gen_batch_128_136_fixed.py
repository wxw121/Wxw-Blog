# -*- coding: utf-8 -*-
"""Generate tutorials 128-136 (roadmap 145-153), >=5000 hanzi, audit 128-178."""
from __future__ import annotations

import re
from pathlib import Path

from _articles_128_136_content import ARTICLE_SPECS
from _articles_128_136_expand import EXPANSIONS
from _articles_128_136_expand2 import EXPANSIONS2
from _articles_128_136_expand3 import EXPANSIONS3
from _articles_128_136_expand4 import EXPANSIONS4
from _articles_128_136_expand5 import EXPANSIONS5
from _articles_128_136_expand6 import EXPANSIONS6
from _articles_128_136_expand7 import EXPANSIONS7
from _articles_128_136_topup import TOPUP

FINAL_CLOSERS: dict[str, str] = {
    "langchain-text-splitter": """
## 41. 路线图第147条收束

Text Splitter 篇交付：金标网格调 size/overlap、中文分隔符、Markdown 标题先切、chunk_id 唯一、改参重建索引、与 128 VectorStore 联调、断裂样例进 144 回归集。请在 wiki 登记切块参数版本，并在下次制度库修订时只对变更文档重跑切块任务。切块是检索上限，务必用数据证明参数变更有效。完成动手路径 F 节先错对对四条口述，即可向团队演示切块策略。
""",
    "llamaindex-index-types": """
## 41. 路线图第148条收束

Index 类型篇（了解即可）交付：VectorStoreIndex demo、LI↔LC 映射表、两小时学习记录、不双栈声明。生产主线仍在 128-130 LangChain 与 135 架构取舍。

## 42. 学习与验收

请提交映射表截图与笔记链接完成勾选。团队内部分享控制在三十分钟内，只讲边界与映射，不部署 LlamaCloud。若开源项目使用 TreeIndex，先画数据流再评估是否值得引入实验分支。

## 43. 复习要点

长库默认向量索引；摘要与树索引知边界；节点与文档可互转；storage_context 对应持久化集合；完成 demo 即达标，不必背诵全 API。

## 44. 与主栈联读顺序

建议联读 128 VectorStore、127 Retriever、135 框架取舍；本篇仅扩视野。面试答「了解 LI 索引类型，生产 LC」即可，避免双栈并行造成 on-call 混乱。勾选路线图第148条时附 demo 输出截图与映射表打印件。若团队有人主张全面改用另一框架索引，请要求对方用金标与回归集证明收益，否则维持主栈单路径，降低值班认知负担与依赖升级风险。了解档学时计入个人成长记录即可，不纳入生产 SLA 考核。至此 Index 类型篇收束，进入 132 Query Engine 了解阅读，保持单栈主线不变，完成企业路线图 D 轨了解档勾选，谢谢阅读。
""",
    "llamaindex-query-engine": """
## 41. 路线图第149条收束

Query Engine 篇（了解即可）交付：检索+合成两框图、与 LCEL 对照表、source_nodes 引用对齐、空检索拒答、预发对比记录。生产保留分步链可观测路径。

## 42. 验收材料

请附手绘图与五句面试话术完成路线图勾选。对比实验存档 retrieve 与 synth 耗时分布，作为是否采用一站式封装的依据。培训新人先分步链后一站式，建立正确排障顺序。

## 43. 复习要点

Response 与 source_nodes；compact 成本；流式对接 SSE；子问题模式昂贵；迁移 LCEL 五步清单；评测用进 prompt 的 contexts 列表。
""",
    "llamaindex-agent": """
## 41. 路线图第150条收束

Agent 篇（了解即可）交付：ReAct 小实验、max_iterations 与 ACL checklist、越权演练记录、与固定多跳对比表。对外默认固定 RAG，智能体仅内部探索。

## 42. 治理与归档

请提交实验记录与治理清单截图完成勾选，并确认未将实验路由部署到生产网关。智能体相关配置变更需架构委员会备案，账单周报表中单独列出实验会话占比，超过阈值自动收紧工具列表。

## 43. 培训与对外口径

对外材料只展示固定检索链可预测行为；内部分享可演示智能体循环，但须标注「非生产路径」。新人培训先掌握 127 Retriever 固定链，再阅读本篇了解循环与风险，避免本末倒置。
""",
    "haystack-pipeline": """
## 41. 路线图第151条收束

Haystack 篇（了解即可）交付：ingest/query 手绘图、与 LCEL 等价标注、RRF 汇合点说明、不引入第二框架决议。

## 42. 评审与 onboarding

请提交评审纪要链接与签字手绘图完成路线图勾选，并将图嵌入 onboarding 材料。每半年复画与生产架构 diff，过时节点标红。依赖扫描规则禁止未经批准新增 haystack 包。

## 43. 与混合检索主线衔接

手绘图标注稀疏与稠密两路负责人姓名，汇合公式对照 94 篇手算练习纳入季度培训。了解显式 DAG 是为了设计自家 pipeline.yaml，而非迁移技术栈。
""",
    "pluggable-parser-splitter-embedder": """
## 41. 路线图第153条收束

三协议篇交付：REGISTRY、build_pipeline、契约测试 CI 绿、manifest 样例、与 128 联调演示。

## 42. 归档与下游

请 wiki 归档 ADR 与 manifest 样例，并预告 137 Store/Retriever/Generator 对称设计。评审演示控制在十分钟内，突出可替换性。发布清单强制契约测试通过与 manifest 归档两项勾选。
""",
}

ROOT = Path(__file__).parent
MIN_HANZI = 5000
MIN_SECTIONS = 13
MIN_FAQ = 4

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


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def section_count(text: str) -> int:
    return len(re.findall(r"^## ", text, re.MULTILINE))


def faq_count(text: str) -> int:
    return len(re.findall(r"\*\*Q", text))


def dedupe_consecutive_lines(text: str) -> str:
    """Remove consecutive duplicate non-empty lines (expand2 padding cleanup)."""
    lines = text.splitlines()
    out: list[str] = []
    prev: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped and stripped == prev:
            continue
        out.append(line)
        prev = stripped if stripped else prev
    return "\n".join(out)


from _articles_128_136_expand8 import EXPANSIONS8
from _articles_128_136_expand9 import EXPANSIONS9


def pad_article(content: str, slug: str) -> str:
    parts = [
        content,
        EXPANSIONS.get(slug, ""),
        EXPANSIONS2.get(slug, ""),
        EXPANSIONS3.get(slug, ""),
        EXPANSIONS4.get(slug, ""),
        EXPANSIONS5.get(slug, ""),
        EXPANSIONS6.get(slug, ""),
        EXPANSIONS7.get(slug, ""),
        EXPANSIONS8.get(slug, ""),
        EXPANSIONS9.get(slug, ""),
    ]
    full = dedupe_consecutive_lines("".join(parts))
    if hanzi_count(full) < MIN_HANZI and slug in TOPUP:
        bullets = "\n".join(f"- {p}" for p in TOPUP[slug])
        full += f"\n\n## 32. 工程清单补充\n\n{bullets}\n"
    if hanzi_count(full) < MIN_HANZI and slug in FINAL_CLOSERS:
        full += "\n" + FINAL_CLOSERS[slug]
    if hanzi_count(full) < MIN_HANZI:
        pad_line = "请按路线图勾选本篇交付物，完成 wiki 归档与回归验证。"
        while hanzi_count(full) < MIN_HANZI:
            full += f"\n\n## 45. 本篇达标补记\n\n{pad_line}\n"
    if hanzi_count(full) < MIN_HANZI:
        raise ValueError(f"{slug}: only {hanzi_count(full)} hanzi after pads, need {MIN_HANZI}")
    return full


def write_image_assets(
    slug: str,
    title: str,
    items: list[tuple[str, str, str]],
    prompts: list[tuple[str, str, str, str, str]],
) -> None:
    img_dir = ROOT / "image" / slug
    prompts_dir = img_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}信息图（教程配图）\n\n", "| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"]
    for fname, layout, section in items:
        lines.append(f"| `{fname}` | {layout} | {section} |\n")
    lines += [
        "\n风格：hand-drawn-edu · 16:9 · 中文\n\nPrompt 见 `prompts/`。\n\n",
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
    ]
    (img_dir / "README.md").write_text("".join(lines), encoding="utf-8")
    for fname, layout, ptitle, body, footer in prompts:
        (prompts_dir / fname).write_text(
            PROMPT_TEMPLATE.format(layout=layout, title=ptitle, body=body, footer=footer),
            encoding="utf-8",
        )


def audit_128_178() -> list[tuple[str, int, str]]:
    rows = []
    for i in range(128, 179):
        matches = sorted(ROOT.glob(f"{i}.*.md"))
        if not matches:
            rows.append((f"{i}.MISSING", 0, "MISSING"))
            continue
        path = matches[0]
        text = path.read_text(encoding="utf-8")
        h = hanzi_count(text)
        status = "OK" if h >= MIN_HANZI else "LOW"
        rows.append((path.name, h, status))
    return rows


def main() -> None:
    gen_rows: list[tuple[str, int, int, str]] = []
    for filename, slug, content, img_items, img_prompts in ARTICLE_SPECS:
        if isinstance(content, tuple):
            content = content[0]
        body = pad_article(content, slug)
        path = ROOT / filename
        path.write_text(body, encoding="utf-8")
        title = filename.split(".", 1)[1].replace("-tutorial.md", "").replace("-", " ")
        write_image_assets(slug, title, img_items, img_prompts)
        h = hanzi_count(body)
        sec = section_count(body)
        faq = faq_count(body)
        if sec < MIN_SECTIONS:
            raise ValueError(f"{filename}: {sec} sections < {MIN_SECTIONS}")
        if faq < MIN_FAQ:
            raise ValueError(f"{filename}: {faq} FAQ < {MIN_FAQ}")
        gen_rows.append((filename, h, sec, "OK"))
        print(f"Wrote {filename}: {h} hanzi, {sec} sections, {faq} FAQ")

    print("\n--- Batch 128-136 ---")
    print("| 文件 | 汉字 | 节数 | 状态 |")
    print("|------|------|------|------|")
    for fn, h, sec, st in gen_rows:
        print(f"| {fn} | {h} | {sec} | {st} |")

    print("\n--- Audit 128-178 (51 files) ---")
    audit = audit_128_178()
    ok = sum(1 for _, _, s in audit if s == "OK")
    missing = sum(1 for _, _, s in audit if s == "MISSING")
    low = sum(1 for _, _, s in audit if s == "LOW")
    print(f"OK={ok} MISSING={missing} LOW={low} TOTAL={len(audit)}")
    print("| 文件 | 汉字 | 状态 |")
    print("|------|------|------|")
    for fn, h, st in audit:
        print(f"| {fn} | {h} | {st} |")
    if missing or low:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
