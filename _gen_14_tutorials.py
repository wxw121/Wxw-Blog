# -*- coding: utf-8 -*-
"""Generate 14 F2/G/H tutorials (>=5000 hanzi each). Run: python _gen_14_tutorials.py"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
MIN_HANZI = 5000

from _articles_14_content import ARTICLES_ALL  # noqa: E402

IMAGE_SPECS = {
    "retrieval-debug-console": {
        "roadmap": 199,
        "title": "检索调试台",
        "images": [
            ("01-debug-console-idea.png", "§3 检索调试台是什么", "comparison-matrix", "检索调试台直觉"),
            ("02-debug-ui-layout.png", "§7 前端实现", "hierarchical-tree", "调试台 UI 布局"),
            ("03-concept-map.png", "§12 概念地图", "bento-grid", "检索调试概念地图"),
        ],
    },
    "admin-usage-dashboard": {
        "roadmap": 200,
        "title": "管理后台用量统计",
        "images": [
            ("01-usage-metering-idea.png", "§3 用量统计是什么", "hub-spoke", "用量计量直觉"),
            ("02-dashboard-layout.png", "§7 看板 UI", "hierarchical-tree", "用量看板布局"),
            ("03-concept-map.png", "§12 概念地图", "bento-grid", "用量统计概念地图"),
        ],
    },
    "admin-log-eval-dashboard": {
        "roadmap": 201,
        "title": "管理后台日志与评测看板",
        "images": [
            ("01-log-eval-idea.png", "§3 日志与评测看板是什么", "hub-spoke", "日志评测看板直觉"),
            ("02-eval-dashboard-layout.png", "§8 看板 UI", "hierarchical-tree", "评测看板布局"),
            ("03-concept-map.png", "§12 概念地图", "bento-grid", "日志评测概念地图"),
        ],
    },
    "china-compliance-rag": {
        "roadmap": 215,
        "title": "国内合规与 RAG",
        "images": [
            ("01-compliance-map.png", "§3 合规地图", "hub-spoke", "国内合规与 RAG 地图"),
            ("02-data-zones.png", "§5 数据分区", "comparison-matrix", "数据分区与出境"),
            ("03-concept-map.png", "§12 概念地图", "bento-grid", "合规概念地图"),
        ],
    },
    "graph-rag": {
        "roadmap": 216,
        "title": "Graph RAG",
        "images": [
            ("01-graph-rag-idea.png", "§3 Graph RAG 是什么", "hub-spoke", "Graph RAG 直觉"),
            ("02-index-pipeline.png", "§6 索引流水线", "flow-left-right", "GraphRAG 索引流水线"),
            ("03-dual-path-architecture.png", "§9 双路检索", "comparison-matrix", "局部与全局双路检索"),
        ],
    },
    "crag-corrective-rag": {
        "roadmap": 222,
        "title": "CRAG 纠错式 RAG",
        "images": [
            ("01-crag-idea.png", "§3 CRAG 是什么", "hub-spoke", "CRAG 纠错式 RAG 直觉"),
            ("02-evaluator-router.png", "§5 评估与路由", "flow-left-right", "检索评估与动作路由"),
            ("03-concept-map.png", "§12 概念地图", "bento-grid", "CRAG 概念地图"),
        ],
    },
    "adaptive-rag": {
        "roadmap": 223,
        "title": "Adaptive RAG",
        "images": [
            ("01-adaptive-idea.png", "§3 Adaptive RAG 是什么", "hub-spoke", "Adaptive RAG 自适应路由"),
            ("02-query-router.png", "§6 查询路由", "flow-left-right", "查询分类与检索策略"),
            ("03-concept-map.png", "§12 概念地图", "bento-grid", "Adaptive RAG 概念地图"),
        ],
    },
}


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def write_image_assets(slug: str, spec: dict) -> None:
    d = ROOT / "image" / slug
    prompts_dir = d / "prompts"
    readme_path = d / "README.md"
    if readme_path.exists() and all((prompts_dir / f.replace(".png", ".md")).exists() for f, *_ in spec["images"]):
        return
    prompts_dir.mkdir(parents=True, exist_ok=True)
    title = spec["title"]
    roadmap = spec["roadmap"]
    readme = f"# {title}信息图（路线图 {roadmap}）\n\n\n\n| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"
    for fname, section, layout, _ in spec["images"]:
        readme += f"| `{fname}` | {layout} | {section} |\n"
    readme += (
        "\n\n风格：hand-drawn-edu · 16:9 · 中文  \n"
        "Prompt 见 `prompts/`。\n\n\n"
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n"
    )
    readme_path.write_text(readme, encoding="utf-8")
    for fname, section, layout, img_title in spec["images"]:
        prompt_path = prompts_dir / fname.replace(".png", ".md")
        if prompt_path.exists():
            continue
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

{section}

Footer: {title} · {section.split()[0]}

All text Simplified Chinese.
"""
        prompt_path.write_text(prompt, encoding="utf-8")


def print_table(results: list[tuple[str, int, str]]) -> None:
    print("\n| 文件 | 汉字数 | 状态 |")
    print("|------|--------|------|")
    for filename, count, status in results:
        print(f"| {filename} | {count} | {status} |")


def main() -> int:
    results: list[tuple[str, int, str]] = []
    for filename, content, image_slug in ARTICLES_ALL:
        path = ROOT / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        count = hanzi_count(content)
        status = "PASS" if count >= MIN_HANZI else "FAIL"
        results.append((filename, count, status))
        if image_slug and image_slug in IMAGE_SPECS:
            write_image_assets(image_slug, IMAGE_SPECS[image_slug])
    print_table(results)
    failed = [f for f, c, s in results if s == "FAIL"]
    if failed:
        print(f"\nFAILED (< {MIN_HANZI} hanzi): {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"\nAll {len(results)} articles OK (>= {MIN_HANZI} hanzi).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
