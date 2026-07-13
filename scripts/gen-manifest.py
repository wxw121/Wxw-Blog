#!/usr/bin/env python3
"""Print generation manifest for articles missing image refs."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|[^|]*\|\s*§(\d+)", re.I)


def slug_from_article(path: Path) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", path.name))


def main() -> None:
    lo = int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 17
    hi = int(__import__("sys").argv[2]) if len(__import__("sys").argv) > 2 else 213
    for article in sorted(ROOT.glob("[0-9]*.md")):
        num = int(article.name.split(".", 1)[0])
        if num < lo or num > hi:
            continue
        if IMG_REF.search(article.read_text(encoding="utf-8")):
            continue
        slug = slug_from_article(article)
        img_dir = ROOT / "image" / slug
        readme = img_dir / "README.md"
        if not readme.exists():
            print(f"SKIP {num} {slug} no README")
            continue
        for m in README_ROW.finditer(readme.read_text(encoding="utf-8")):
            png = m.group(1)
            if not (img_dir / png).exists():
                prompt = img_dir / "prompts" / png.replace(".png", ".md")
                if not prompt.exists():
                    # try numbered prompts
                    candidates = sorted((img_dir / "prompts").glob("*.md"))
                    prompt = candidates[0] if candidates else None
                print(f"GEN {num}|{slug}|{png}|{prompt}")


if __name__ == "__main__":
    main()
