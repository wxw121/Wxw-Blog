#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.IGNORECASE)

total_imgs = 0
articles = []
for num in range(122, 214):
    arts = list(ROOT.glob(f"{num}.*-tutorial.md"))
    if not arts:
        continue
    art = arts[0]
    if IMG_REF.search(art.read_text(encoding="utf-8")):
        continue
    slug = re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", art.name))
    img_dir = ROOT / "image" / slug
    readme = img_dir / "README.md"
    if not readme.exists():
        continue
    rows = README_ROW.findall(readme.read_text(encoding="utf-8"))
    need = len([r for r in rows if not (img_dir / r).exists()])
    total_imgs += need
    articles.append((num, slug, need, len(rows)))

print(f"Articles pending: {len(articles)}, images to gen: {total_imgs}")
for a in articles:
    print(f"{a[0]}|{a[1]}|need={a[2]}/{a[3]}")
