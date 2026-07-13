#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.IGNORECASE)
asset_names = {p.name for p in ASSETS.glob("*.png")}

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
    for png in rows:
        if not (img_dir / png).exists():
            print(f"{num}|{slug}|{png}|assets={png in asset_names}")
