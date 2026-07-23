# -*- coding: utf-8 -*-
"""Insert TOPUP blocks before summary section for tutorials 179-213."""
from __future__ import annotations

import re
from pathlib import Path

from _articles_179_213_topup import TOPUP

ROOT = Path(__file__).parent

FILES = list(TOPUP.keys())


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def find_summary_anchor(text: str) -> re.Match[str] | None:
    """Return match for the summary section heading (last ## N. ...总结...)."""
    candidates = [
        m
        for m in re.finditer(r"^## (\d+)\. (.+)$", text, re.MULTILINE)
        if "总结" in m.group(2)
    ]
    return candidates[-1] if candidates else None


def find_insert_pos(text: str) -> int:
    anchor = find_summary_anchor(text)
    if anchor:
        return anchor.start()
    m = re.search(r"\n>\s*\*\*初学者可能仍困惑", text)
    if m:
        return m.start()
    m = re.search(r"\n---\s*\n\s*\n>\s*\*\*初学者", text)
    if m:
        return m.start()
    return len(text.rstrip())


def apply_topup(text: str, topup: str) -> str:
    pos = find_insert_pos(text)
    return text[:pos].rstrip() + "\n\n---\n\n" + topup.strip() + "\n\n---\n\n" + text[pos:].lstrip()



def remove_existing_topup(text: str) -> str:
    """Strip prior topup block if re-expansion needed."""
    marker = "<!-- topup-batch-179-213 -->"
    if marker not in text:
        return text
    start = text.find("\n---\n\n" + marker)
    if start == -1:
        start = text.find(marker)
        if start == -1:
            return text
    else:
        start += 1  # keep leading structure before ---
    anchor = find_summary_anchor(text[:start])
    if anchor:
        end = anchor.start()
        return text[:end].rstrip() + "\n\n" + text[anchor.start():].lstrip()
    return re.sub(r"\n---\n\n" + re.escape(marker) + r".*", "", text, flags=re.S).rstrip() + "\n"


def main() -> None:
    print("| filename | before | after | status |")
    print("|----------|--------|-------|--------|")
    for fname in sorted(FILES, key=lambda x: int(x.split(".")[0])):
        path = ROOT / fname
        if not path.exists():
            print(f"| {fname} | - | - | MISSING |")
            continue
        text = path.read_text(encoding="utf-8")
        before = hanzi_count(text)
        if fname not in TOPUP:
            print(f"| {fname} | {before} | {before} | NO_TOPUP |")
            continue
        topup = TOPUP[fname]
        if "<!-- topup-batch-179-213 -->" in text and before >= 5200:
            print(f"| {fname} | {before} | {before} | ALREADY |")
            continue
        if before >= 5200:
            print(f"| {fname} | {before} | {before} | SKIP_OK |")
            continue
        if "<!-- topup-batch-179-213 -->" in text:
            text = remove_existing_topup(text)
            before = hanzi_count(text)
        new_text = apply_topup(text, topup)
        path.write_text(new_text, encoding="utf-8")
        after = hanzi_count(new_text)
        status = "OK" if after >= 5200 else "LOW"
        print(f"| {fname} | {before} | {after} | {status} |")


if __name__ == "__main__":
    main()
