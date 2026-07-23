# -*- coding: utf-8 -*-
"""Remove 实践要点 spam from topup module and affected articles."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent


def strip_practice_lines(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not re.match(r"^\s*实践要点\s*\d+", ln)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def clean_topup_py() -> None:
    path = ROOT / "_articles_179_213_topup.py"
    src = path.read_text(encoding="utf-8")
    # Remove string-literal lines containing 实践要点
    src = re.sub(r"\n\s+' 实践要点 \d+[^']*',?\n", "\n", src)
    src = re.sub(r"\n\s+' 实践要点 \d+[^']*'\n", "\n", src)
    src = re.sub(r"\n\s+' 实践要点 \d+[^']*(?:\\n')?\s*\+?\s*\n", "\n", src)
    path.write_text(src, encoding="utf-8")
    print("topup 实践要点 count:", src.count("实践要点"))


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def remove_topup_block(text: str) -> str:
    marker = "<!-- topup-batch-179-213 -->"
    if marker not in text:
        return text
    start = text.find("\n---\n\n" + marker)
    if start == -1:
        return text
    anchor = None
    for m in re.finditer(r"^## (\d+)\. (.+)$", text, re.MULTILINE):
        if "总结" in m.group(2):
            anchor = m
    if anchor and anchor.start() > start:
        return text[:start].rstrip() + "\n\n" + text[anchor.start() :].lstrip()
    return re.sub(r"\n---\n\n<!-- topup-batch-179-213 -->.*", "", text, flags=re.S).rstrip() + "\n"


def main() -> None:
    clean_topup_py()
    for n in range(179, 214):
        files = list(ROOT.glob(f"{n}.*.md"))
        if not files:
            continue
        path = files[0]
        text = strip_practice_lines(path.read_text(encoding="utf-8"))
        text = remove_topup_block(text)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
