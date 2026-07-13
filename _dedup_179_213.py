# -*- coding: utf-8 -*-
"""Remove duplicate paragraphs and repeated topup blocks in tutorials 179-213."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent

GENERIC_SNIPPETS = [
    "发布前请与相邻教程交叉链接做一次死链检查",
    "与全栈 Compose 联调时，先确认 worker",
    "安全评审关注：管理接口是否默认 admin",
    "性能评审关注：P95 延迟",
    "文档债管理：API 字段变更必须同步",
    "可访问性与国际化虽非 MVP",
    "面试准备：用三十秒讲清本篇",
    "成本意识：任何重复 embed",
    "### 4.3 RLHF 三阶段再述",
    "### 9.2 H 模块 216～230 回顾表",
]


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def dedupe_paragraphs(text: str) -> str:
    parts = re.split(r"\n\n+", text)
    seen: set[str] = set()
    out: list[str] = []
    for part in parts:
        key = part.strip()
        if not key:
            continue
        # drop exact duplicate paragraphs
        if key in seen:
            continue
        # drop repeated generic boilerplate (keep first only)
        if any(s in key for s in GENERIC_SNIPPETS):
            norm = key[:80]
            if norm in seen:
                continue
            seen.add(norm)
        seen.add(key)
        out.append(part)
    return "\n\n".join(out) + "\n"


def truncate_garbage(text: str) -> str:
    if "<!-- TRUNCATE_MARKER -->" in text:
        text = text.split("<!-- TRUNCATE_MARKER -->")[0]
    # remove orphan fragments between --- and ## N if they look like misplaced topup
    text = re.sub(
        r"\n---\n\n---\n\n(?:### \d+\.\d+ .+\n\n)+(?=\n## \d+\.)",
        "\n\n",
        text,
        flags=re.S,
    )
    return text.rstrip() + "\n"


def main() -> None:
    print("| file | before | after | removed_dup |")
    print("|------|--------|-------|-------------|")
    for n in range(179, 214):
        files = list(ROOT.glob(f"{n}.*.md"))
        if not files:
            continue
        path = files[0]
        before = path.read_text(encoding="utf-8")
        b_hz = hanzi_count(before)
        after = truncate_garbage(dedupe_paragraphs(before))
        a_hz = hanzi_count(after)
        removed = b_hz - a_hz
        path.write_text(after, encoding="utf-8")
        print(f"| {path.name} | {b_hz} | {a_hz} | {removed} |")


if __name__ == "__main__":
    main()
