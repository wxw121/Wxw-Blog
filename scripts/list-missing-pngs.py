#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/([^)]+)\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)

def slug_from_article(p: Path) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", p.name))

for article in sorted(ROOT.glob("[0-9]*.md")):
    num = int(article.name.split(".", 1)[0])
    if num < 17 or num > 213:
        continue
    slug = slug_from_article(article)
    readme = ROOT / "image" / slug / "README.md"
    if not readme.exists():
        continue
    expected = [m.group(1) for m in README_ROW.finditer(readme.read_text(encoding="utf-8"))]
    have = {p.name for p in (ROOT / "image" / slug).glob("*.png")}
    missing = [e for e in expected if e not in have]
    if missing:
        refs = len(IMG_REF.findall(article.read_text(encoding="utf-8")))
        print(f"{num:3d} {slug} refs={refs} need={missing}")
