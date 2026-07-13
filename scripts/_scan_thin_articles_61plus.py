#!/usr/bin/env python3
"""Scan tutorials 61+ for thin/sparse chapter content."""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_NUM = 61
HANZI = re.compile(r"[\u4e00-\u9fff]")
HEADING = re.compile(r"^(#{2,4})\s+(.+)$")
FENCE = re.compile(r"^```")


def strip_code_blocks(text: str) -> str:
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def count_hanzi(text: str) -> int:
    return len(HANZI.findall(text))


@dataclass
class Section:
    level: int
    title: str
    body: str

    @property
    def hanzi(self) -> int:
        return count_hanzi(self.body)


@dataclass
class ArticleReport:
    num: int
    path: Path
    hanzi_no_code: int
    h2_count: int
    sections: list[Section] = field(default_factory=list)
    thin_h2: list[tuple[str, int]] = field(default_factory=list)
    sparse_h2: list[tuple[str, int]] = field(default_factory=list)

    @property
    def avg_h2_hanzi(self) -> float:
        h2s = [s for s in self.sections if s.level == 2]
        return statistics.mean(s.hanzi for s in h2s) if h2s else 0.0


def parse_sections(text: str) -> list[Section]:
    lines = text.splitlines()
    sections: list[Section] = []
    current_level = 0
    current_title = ""
    current_body: list[str] = []

    def flush() -> None:
        nonlocal current_body, current_title, current_level
        if current_level >= 2 and current_title and current_title.strip() != "目录":
            sections.append(
                Section(current_level, current_title.strip(), "\n".join(current_body).strip())
            )
        current_body = []

    for line in lines:
        m = HEADING.match(line)
        if m:
            flush()
            current_level = len(m.group(1))
            current_title = m.group(2)
            continue
        if current_level >= 2:
            current_body.append(line)
    flush()
    return sections


def score_article(rep: ArticleReport, median_hanzi: float) -> float:
    score = 0.0
    if rep.hanzi_no_code < 1800:
        score += 3
    elif rep.hanzi_no_code < 2200:
        score += 2
    elif rep.hanzi_no_code < median_hanzi * 0.75:
        score += 1
    if rep.h2_count:
        thin_ratio = len(rep.thin_h2) / rep.h2_count
        if thin_ratio >= 0.5:
            score += 2
        elif thin_ratio >= 0.35:
            score += 1
    if len(rep.sparse_h2) >= 3:
        score += 1.5
    elif len(rep.sparse_h2) >= 2:
        score += 1
    if rep.avg_h2_hanzi < 160:
        score += 1
    return score


def analyze(path: Path) -> ArticleReport | None:
    m = re.match(r"^(\d+)\.", path.name)
    if not m:
        return None
    num = int(m.group(1))
    if num < MIN_NUM:
        return None

    raw = path.read_text(encoding="utf-8")
    no_code = strip_code_blocks(raw)
    sections = parse_sections(raw)
    h2s = [s for s in sections if s.level == 2]

    rep = ArticleReport(
        num=num,
        path=path,
        hanzi_no_code=count_hanzi(no_code),
        h2_count=len(h2s),
        sections=sections,
    )

    for s in sections:
        if s.level == 2 and s.hanzi < 150:
            rep.thin_h2.append((s.title, s.hanzi))
        if s.level == 2 and s.hanzi < 80:
            rep.sparse_h2.append((s.title, s.hanzi))

    return rep


def main() -> None:
    reports: list[ArticleReport] = []
    for p in sorted(ROOT.glob("[0-9]*.md")):
        r = analyze(p)
        if r:
            reports.append(r)

    reports.sort(key=lambda x: x.num)
    hanzi_vals = [r.hanzi_no_code for r in reports]
    median_hanzi = statistics.median(hanzi_vals)

    print("=" * 72)
    print(f"教程 {MIN_NUM}+ 内容厚度扫描（共 {len(reports)} 篇）")
    print(
        f"汉字中位数(去代码块): {median_hanzi:.0f}  |  "
        f"范围: {min(hanzi_vals)}–{max(hanzi_vals)}"
    )
    print("=" * 72)
    print(f"<1800字: {sum(1 for r in reports if r.hanzi_no_code < 1800)}")
    print(f"1800–2200字: {sum(1 for r in reports if 1800 <= r.hanzi_no_code < 2200)}")
    print(f"2200–3000字: {sum(1 for r in reports if 2200 <= r.hanzi_no_code < 3000)}")
    print(f">=3000字: {sum(1 for r in reports if r.hanzi_no_code >= 3000)}")

    scored = [(score_article(r, median_hanzi), r) for r in reports]
    scored.sort(key=lambda x: (-x[0], x[1].hanzi_no_code))

    flagged = [r for sc, r in scored if sc >= 2.5]
    print(f"\n【重点关注】寡淡/偏薄 ({len(flagged)} 篇, 评分≥2.5):\n")
    for r in flagged:
        sc = score_article(r, median_hanzi)
        flags: list[str] = []
        if r.hanzi_no_code < 1800:
            flags.append(f"总字偏少({r.hanzi_no_code})")
        elif r.hanzi_no_code < 2200:
            flags.append(f"总字略少({r.hanzi_no_code})")
        if r.h2_count and len(r.thin_h2) / r.h2_count >= 0.4:
            flags.append(f"薄H2多({len(r.thin_h2)}/{r.h2_count}个<150字)")
        if len(r.sparse_h2) >= 2:
            flags.append(f"极短H2({len(r.sparse_h2)}个<80字)")
        if r.avg_h2_hanzi < 180:
            flags.append(f"H2均字低({r.avg_h2_hanzi:.0f})")
        print(f"  {r.num:3d} {r.path.name}")
        print(
            f"       汉字={r.hanzi_no_code}  H2={r.h2_count}  "
            f"H2均={r.avg_h2_hanzi:.0f}  评分={sc:.1f}"
        )
        print(f"       问题: {'; '.join(flags) if flags else '章节结构偏表格式'}")
        if r.sparse_h2:
            titles = ", ".join(f"「{t[:24]}」({n}字)" for t, n in r.sparse_h2[:4])
            if len(r.sparse_h2) > 4:
                titles += f" 等{len(r.sparse_h2)}节"
            print(f"       极短H2: {titles}")
        print()

    moderate = [r for sc, r in scored if 1.5 <= sc < 2.5]
    print(f"【次要关注】略薄 ({len(moderate)} 篇, 评分1.5–2.5):\n")
    for r in moderate:
        sc = score_article(r, median_hanzi)
        print(
            f"  {r.num:3d} {r.hanzi_no_code:5d}字  "
            f"薄H2={len(r.thin_h2)}/{r.h2_count}  评分={sc:.1f}  {r.path.name}"
        )

    print(f"\n【总汉字最少 Top 20】({MIN_NUM}+):\n")
    for r in sorted(reports, key=lambda x: x.hanzi_no_code)[:20]:
        print(
            f"  {r.num:3d} {r.hanzi_no_code:5d}字  "
            f"H2均={r.avg_h2_hanzi:.0f}  薄H2={len(r.thin_h2)}/{r.h2_count}  {r.path.name}"
        )


if __name__ == "__main__":
    main()
