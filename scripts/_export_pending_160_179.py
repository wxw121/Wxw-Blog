#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def read_prompt(p: Path) -> str:
    text = p.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].strip()
    return text.strip()


def main() -> None:
    items = []
    for n in range(160, 180):
        arts = list(ROOT.glob(f"{n}.*-tutorial.md"))
        if not arts:
            continue
        slug = re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", arts[0].name))
        img_dir = ROOT / "image" / slug
        readme = img_dir / "README.md"
        if not readme.exists():
            continue
        for png in [m.group(1) for m in README_ROW.finditer(readme.read_text(encoding="utf-8"))]:
            if (img_dir / png).exists():
                continue
            stem = png.replace(".png", "")
            matches = list((img_dir / "prompts").glob(f"{stem}*.md"))
            if not matches:
                continue
            items.append(
                {"n": n, "slug": slug, "png": png, "prompt": read_prompt(matches[0])}
            )
    out = ROOT / "scripts" / "_pending_160_179.json"
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} items to {out}")


if __name__ == "__main__":
    main()
