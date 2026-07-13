#!/usr/bin/env python3
from __future__ import annotations

import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANZI = re.compile(r"[\u4e00-\u9fff]")
HEADING = re.compile(r"^(#{2,4})\s+(.+)$")
FENCE = re.compile(r"^```")


def strip_code(text: str) -> str:
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


def parse_h2(raw: str) -> list[tuple[str, int]]:
    secs: list[tuple[str, int]] = []
    cur_title = ""
    cur_body: list[str] = []
    in_sec = False
    for line in raw.splitlines():
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2:
            if cur_title and cur_title != "目录":
                secs.append((cur_title, count_hanzi("\n".join(cur_body))))
            cur_title = m.group(2).strip()
            cur_body = []
            in_sec = True
        elif in_sec:
            cur_body.append(line)
    if cur_title and cur_title != "目录":
        secs.append((cur_title, count_hanzi("\n".join(cur_body))))
    return secs


def main() -> None:
    rows = []
    for p in sorted(ROOT.glob("[0-9]*.md")):
        m = re.match(r"^(\d+)\.", p.name)
        if not m or int(m.group(1)) <= 80:
            continue
        n = int(m.group(1))
        raw = p.read_text(encoding="utf-8")
        h = count_hanzi(strip_code(raw))
        h2s = parse_h2(raw)
        thin = sum(1 for _, c in h2s if c < 120)
        very_thin = sum(1 for _, c in h2s if c < 60)
        avg = statistics.mean(c for _, c in h2s) if h2s else 0.0
        rows.append(
            {
                "n": n,
                "name": p.name,
                "h": h,
                "h2": len(h2s),
                "thin": thin,
                "very_thin": very_thin,
                "avg": avg,
            }
        )

    med = statistics.median(r["h"] for r in rows)
    print(f"中位数(去代码块汉字): {int(med)}")
    print(f"<1200字: {sum(1 for r in rows if r['h'] < 1200)}")
    print(f"1200-2000字: {sum(1 for r in rows if 1200 <= r['h'] < 2000)}")
    print(f"2000-3000字: {sum(1 for r in rows if 2000 <= r['h'] < 3000)}")
    print(f">=3000字: {sum(1 for r in rows if r['h'] >= 3000)}")

    print("\n## 极薄 <1200字")
    for r in sorted((x for x in rows if x["h"] < 1200), key=lambda x: x["h"]):
        print(
            f"  {r['n']:3d} {r['h']:4d}字 H2均{r['avg']:.0f} "
            f"极短节{r['very_thin']}/{r['h2']}  {r['name']}"
        )

    print("\n## 偏薄 1200-1800字")
    for r in sorted((x for x in rows if 1200 <= r["h"] < 1800), key=lambda x: x["h"]):
        print(
            f"  {r['n']:3d} {r['h']:4d}字 H2均{r['avg']:.0f} "
            f"薄节{r['thin']}/{r['h2']}  {r['name']}"
        )

    print("\n## 总字尚可但章节寡淡(>=1800字且>=50% H2<120字)")
    flagged = [
        r
        for r in rows
        if r["h"] >= 1800 and r["h2"] >= 8 and r["thin"] / r["h2"] >= 0.5
    ]
    for r in sorted(flagged, key=lambda x: (-x["thin"] / x["h2"], x["h"])):
        print(
            f"  {r['n']:3d} {r['h']:4d}字 薄节{r['thin']}/{r['h2']} "
            f"H2均{r['avg']:.0f}  {r['name']}"
        )


if __name__ == "__main__":
    main()
