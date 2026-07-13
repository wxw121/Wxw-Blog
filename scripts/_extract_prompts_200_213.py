#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.IGNORECASE)


def slug_from_article(path: Path) -> str:
    name = path.name
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", name))


def main() -> None:
    jobs: list[tuple[str, str, str]] = []
    for n in range(200, 214):
        arts = sorted(ROOT.glob(f"{n}.*-tutorial.md"))
        if not arts:
            continue
        article = arts[0]
        if IMG_REF.search(article.read_text(encoding="utf-8")):
            continue
        slug = slug_from_article(article)
        readme = ROOT / "image" / slug / "README.md"
        if not readme.exists():
            continue
        for m in README_ROW.finditer(readme.read_text(encoding="utf-8")):
            png = m.group(1)
            stem = Path(png).stem
            prompt = ROOT / "image" / slug / "prompts" / f"{stem}.md"
            if not prompt.exists():
                print(f"MISSING {slug} {png}")
                continue
            text = prompt.read_text(encoding="utf-8")
            body = text.split("---", 2)[-1].strip() if text.startswith("---") else text
            jobs.append((slug, png, body))
    print(f"Total jobs: {len(jobs)}")
    for slug, png, body in jobs:
        print(f"---JOB---{slug}|{png}")
        print(body)


if __name__ == "__main__":
    main()
