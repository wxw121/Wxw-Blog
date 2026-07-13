#!/usr/bin/env python3
import runpy
import statistics
from pathlib import Path

m = runpy.run_path("scripts/_scan_thin_articles_61plus.py")
analyze = m["analyze"]
score_article = m["score_article"]

reports = [analyze(p) for p in sorted(Path(".").glob("[0-9]*.md"))]
reports = [r for r in reports if r]
med = statistics.median(r.hanzi_no_code for r in reports)

t1 = sorted([r for r in reports if r.hanzi_no_code < 1500], key=lambda x: x.hanzi_no_code)
t2 = sorted(
    [r for r in reports if 1500 <= r.hanzi_no_code < 1800], key=lambda x: x.hanzi_no_code
)
t3 = sorted(
    [
        r
        for r in reports
        if 1800 <= r.hanzi_no_code < 2200 and score_article(r, med) >= 2.5
    ],
    key=lambda x: x.hanzi_no_code,
)

print(f"TOTAL={len(reports)} MEDIAN={int(med)}")
print(f"TIER1_<1500={len(t1)}")
for r in t1:
    sc = score_article(r, med)
    print(f"  {r.num:3d} {r.hanzi_no_code:4d} sc={sc:.1f} thin={len(r.thin_h2)}/{r.h2_count} {r.path.name}")

print(f"TIER2_1500_1799={len(t2)}")
for r in t2:
    sc = score_article(r, med)
    print(f"  {r.num:3d} {r.hanzi_no_code:4d} sc={sc:.1f} thin={len(r.thin_h2)}/{r.h2_count} {r.path.name}")

print(f"TIER3_1800_2199_FLAGGED={len(t3)}")
for r in t3:
    sc = score_article(r, med)
    print(f"  {r.num:3d} {r.hanzi_no_code:4d} sc={sc:.1f} thin={len(r.thin_h2)}/{r.h2_count} {r.path.name}")

print("RANGE_81_99_181_200")
for r in sorted(reports, key=lambda x: x.num):
    if 81 <= r.num <= 99 or 181 <= r.num <= 200:
        sc = score_article(r, med)
        if r.hanzi_no_code >= 2200 and sc < 3:
            flag = "OK"
        elif sc >= 4:
            flag = "THIN"
        else:
            flag = "MED"
        print(
            f"  {r.num:3d} {r.hanzi_no_code:4d} thin={len(r.thin_h2)}/{r.h2_count} sc={sc:.1f} {flag}"
        )
