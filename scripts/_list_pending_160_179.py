#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)

for n in range(160, 180):
    arts = list(ROOT.glob(f"{n}.*-tutorial.md"))
    if not arts:
        continue
    art = arts[0]
    slug = re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", art.name))
    img_dir = ROOT / "image" / slug
    readme = img_dir / "README.md"
    prompts_dir = img_dir / "prompts"
    if not readme.exists():
        print(f"{n}: NO README")
        continue
    text = readme.read_text(encoding="utf-8")
    pngs = [m.group(1) for m in README_ROW.finditer(text)]
    for png in pngs:
        stem = png.replace(".png", "")
        matches = list(prompts_dir.glob(f"{stem}*.md")) if prompts_dir.exists() else []
        have = (img_dir / png).exists()
        status = "HAVE" if have else "NEED"
        prompt = str(matches[0].relative_to(ROOT)) if matches else "MISSING"
        print(f"{status}\t{n}\t{slug}\t{png}\t{prompt}")
