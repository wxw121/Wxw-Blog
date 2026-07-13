#!/usr/bin/env python3
"""Scan tutorials 81+ for thin/sparse chapter content."""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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

    @property
    def prose_lines(self) -> int:
        n = 0
        for line in self.body.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("|") or s.startswith("!["):
                continue
            if s.startswith("```") or s.startswith(">"):
                continue
            if s.startswith("- ") or re.match(r"^\d+\.\s", s):
                continue
            if HANZI.search(s):
                n += 1
        return n


@dataclass
class ArticleReport:
    num: int
    path: Path
    hanzi_total: int
    hanzi_no_code: int
    h2_count: int
    sections: list[Section] = field(default_factory=list)
    thin_h2: list[tuple[str, int]] = field(default_factory=list)
    thin_h3: list[tuple[str, int]] = field(default_factory=list)
    sparse_h2: list[tuple[str, int]] = field(default_factory=list)  # <80 hanzi
    flags: list[str] = field(default_factory=list)

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
        if current_level >= 2 and current_title:
            body = "\n".join(current_body).strip()
            if current_title.strip() != "目录":
                sections.append(Section(current_level, current_title.strip(), body))
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


def analyze(path: Path) -> ArticleReport | None:
    m = re.match(r"^(\d+)\.", path.name)
    if not m:
        return None
    num = int(m.group(1))
    if num <= 80:
        return None

    raw = path.read_text(encoding="utf-8")
    no_code = strip_code_blocks(raw)
    sections = parse_sections(raw)
    h2s = [s for s in sections if s.level == 2]

    rep = ArticleReport(
        num=num,
        path=path,
        hanzi_total=count_hanzi(raw),
        hanzi_no_code=count_hanzi(no_code),
        h2_count=len(h2s),
        sections=sections,
    )

    for s in sections:
        if s.level == 2 and s.hanzi < 150:
            rep.thin_h2.append((s.title, s.hanzi))
        if s.level == 3 and s.hanzi < 80:
            rep.thin_h3.append((s.title, s.hanzi))
        if s.level == 2 and s.hanzi < 80:
            rep.sparse_h2.append((s.title, s.hanzi))

    return rep


def score_article(rep: ArticleReport, median_hanzi: float) -> float:
    """Higher = more likely thin/sparse."""
    score = 0.0
    if rep.hanzi_no_code < 2000:
        score += 3
    elif rep.hanzi_no_code < 2800:
        score += 2
    elif rep.hanzi_no_code < median_hanzi * 0.65:
        score += 1.5
    if rep.h2_count <= 6:
        score += 1
    if rep.h2_count > 0:
        thin_ratio = len(rep.thin_h2) / rep.h2_count
        if thin_ratio >= 0.5:
            score += 2
        elif thin_ratio >= 0.35:
            score += 1
    if len(rep.sparse_h2) >= 3:
        score += 1.5
    if rep.avg_h2_hanzi < 180:
        score += 1
    return score


def main() -> None:
    reports: list[ArticleReport] = []
    for p in sorted(ROOT.glob("[0-9]*.md")):
        r = analyze(p)
        if r:
            reports.append(r)

    reports.sort(key=lambda x: x.num)
    hanzi_vals = [r.hanzi_no_code for r in reports]
    median_hanzi = statistics.median(hanzi_vals)

    for r in reports:
        r.flags = []
        if r.hanzi_no_code < 2000:
            r.flags.append(f"总汉字偏少({r.hanzi_no_code})")
        elif r.hanzi_no_code < 2800:
            r.flags.append(f"总汉字略少({r.hanzi_no_code})")
        elif r.hanzi_no_code < median_hanzi * 0.65:
            r.flags.append(f"低于中位数65%({r.hanzi_no_code}/{int(median_hanzi)})")
        if r.h2_count <= 6:
            r.flags.append(f"章节少({r.h2_count}个H2)")
        if r.h2_count and len(r.thin_h2) / r.h2_count >= 0.4:
            r.flags.append(f"薄章节多({len(r.thin_h2)}/{r.h2_count}个H2<150字)")
        if len(r.sparse_h2) >= 2:
            r.flags.append(f"极短章节({len(r.sparse_h2)}个H2<80字)")
        if r.avg_h2_hanzi < 160:
            r.flags.append(f"H2均值偏低({r.avg_h2_hanzi:.0f}字)")

    scored = [(score_article(r, median_hanzi), r) for r in reports]
    scored.sort(key=lambda x: (-x[0], x[1].hanzi_no_code))

    print("=" * 72)
    print(f"教程 81–213 内容厚度扫描（共 {len(reports)} 篇）")
    print(f"汉字中位数(去代码块): {median_hanzi:.0f}  |  范围: {min(hanzi_vals)}–{max(hanzi_vals)}")
    print("=" * 72)

    flagged = [r for _, r in scored if r.flags and score_article(r, median_hanzi) >= 2.5]
    print(f"\n【重点关注】寡淡/偏薄文章 ({len(flagged)} 篇, 评分≥2.5):\n")
    for r in flagged:
        sc = score_article(r, median_hanzi)
        print(f"  {r.num:3d} {r.path.name}")
        print(f"       汉字(去代码)={r.hanzi_no_code}  H2={r.h2_count}  H2均字={r.avg_h2_hanzi:.0f}  评分={sc:.1f}")
        print(f"       问题: {'; '.join(r.flags)}")
        if r.sparse_h2:
            titles = ", ".join(f"「{t}」({n}字)" for t, n in r.sparse_h2[:4])
            if len(r.sparse_h2) > 4:
                titles += f" 等{len(r.sparse_h2)}节"
            print(f"       极短H2: {titles}")
        print()

    moderate = [
        r for sc, r in scored if 1.5 <= sc < 2.5 and r.flags
    ]
    print(f"\n【次要关注】略薄 ({len(moderate)} 篇, 评分1.5–2.5):\n")
    for r in moderate:
        sc = score_article(r, median_hanzi)
        print(f"  {r.num:3d} {r.path.name}  汉字={r.hanzi_no_code}  {'; '.join(r.flags)}")

    print(f"\n\n【总汉字最少 Top 15】:\n")
    for r in sorted(reports, key=lambda x: x.hanzi_no_code)[:15]:
        print(f"  {r.num:3d} {r.hanzi_no_code:5d}字  H2={r.h2_count:2d}  {r.path.name}")


if __name__ == "__main__":
    main()
