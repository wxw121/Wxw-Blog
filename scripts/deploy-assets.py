#!/usr/bin/env python3
"""Copy generated PNGs from Cursor assets cache into image/{slug}/."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def slug_from_article(p: Path) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", p.name))


def find_asset(expected: str, num: int, slug: str) -> Path | None:
    """Resolve an expected PNG name to a file in ASSETS."""
    candidates: list[Path] = []
    stem = Path(expected).stem
    for name in (expected, f"{num:02d}-{expected}", f"{num}-{expected}"):
        p = ASSETS / name
        if p.exists():
            candidates.append(p)
    # slug-prefixed variants from older runs
    for p in ASSETS.glob(f"{slug}-*{stem}*.png"):
        candidates.append(p)
    for p in ASSETS.glob(f"{slug}__*{stem}*.png"):
        candidates.append(p)
    for p in ASSETS.glob(f"*{stem}*.png"):
        if p.name == expected or stem in p.stem:
            candidates.append(p)
    # de-dup, prefer exact stem match
    seen: set[str] = set()
    ordered: list[Path] = []
    for p in candidates:
        if p.name in seen:
            continue
        seen.add(p.name)
        ordered.append(p)
    if not ordered:
        return None
    # prefer exact filename
    for p in ordered:
        if p.name == expected:
            return p
    for p in ordered:
        if p.stem == stem:
            return p
    return ordered[0]


def main() -> None:
    if not ASSETS.exists():
        print(f"Assets dir not found: {ASSETS}")
        return
    copied = 0
    for article in sorted(ROOT.glob("[0-9]*.md")):
        num = int(article.name.split(".", 1)[0])
        if num < 17 or num > 213:
            continue
        slug = slug_from_article(article)
        img_dir = ROOT / "image" / slug
        readme = img_dir / "README.md"
        if not readme.exists():
            continue
        expected = [m.group(1) for m in README_ROW.finditer(readme.read_text(encoding="utf-8"))]
        img_dir.mkdir(parents=True, exist_ok=True)
        for png in expected:
            dst = img_dir / png
            if dst.exists() and dst.stat().st_size > 0:
                continue
            src = find_asset(png, num, slug)
            if src is None:
                continue
            shutil.copy2(src, dst)
            print(f"COPY {num:3d} {slug}/{png} <- {src.name}")
            copied += 1
    print(f"Deployed {copied} PNGs")


if __name__ == "__main__":
    main()
