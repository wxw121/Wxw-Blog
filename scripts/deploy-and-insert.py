#!/usr/bin/env python3
"""Copy numbered assets (NN-filename.png) to image/{slug}/ and run insert."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def slug_from_article(p: Path) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", p.name))


def deploy_article(num: int) -> int:
    article = next(ROOT.glob(f"{num}.*.md"), None)
    if not article:
        return 0
    slug = slug_from_article(article)
    img_dir = ROOT / "image" / slug
    readme = img_dir / "README.md"
    if not readme.exists():
        return 0
    expected = [m.group(1) for m in README_ROW.finditer(readme.read_text(encoding="utf-8"))]
    n = 0
    for png in expected:
        dst = img_dir / png
        if dst.exists() and dst.stat().st_size > 0:
            continue
        for src_name in (f"{num}-{png}", f"{num:02d}-{png}", png):
            src = ASSETS / src_name
            if src.exists():
                shutil.copy2(src, dst)
                print(f"COPY {num} {png} <- {src.name}")
                n += 1
                break
    if n:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "batch-infographic.py"), "insert", str(num), str(num)],
            check=False,
        )
    return n


def main() -> None:
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
    total = 0
    for num in range(lo, hi + 1):
        total += deploy_article(num)
    print(f"Deployed {total} PNGs for articles {lo}-{hi}")


if __name__ == "__main__":
    main()
