#!/usr/bin/env python3
"""Insert image refs for any article that has at least one PNG in image/{slug}/."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")


def slug_from_article(path: Path) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", path.name))


def main() -> None:
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 213
    for article in sorted(ROOT.glob("[0-9]*.md")):
        num = int(article.name.split(".", 1)[0])
        if num < lo or num > hi:
            continue
        if IMG_REF.search(article.read_text(encoding="utf-8")):
            continue
        slug = slug_from_article(article)
        pngs = list((ROOT / "image" / slug).glob("*.png"))
        if not pngs:
            continue
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "batch-infographic.py"), "insert", str(num), str(num)],
            check=False,
        )


if __name__ == "__main__":
    main()
