#!/usr/bin/env python3
"""Copy PNG from assets to image/{slug}/ and run batch-infographic insert."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
IMG_REF = re.compile(r"!\[[^\]]*\]\(image/[^)]+\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.IGNORECASE)


def slug_from_num(num: int) -> str | None:
    arts = list(ROOT.glob(f"{num}.*-tutorial.md"))
    if not arts:
        return None
    name = arts[0].name
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", name))


def copy_png(slug: str, png: str) -> bool:
    src = ASSETS / png
    if not src.exists():
        print(f"MISSING asset {png}")
        return False
    dst = ROOT / "image" / slug / png
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"COPIED {slug}/{png}")
    return True


def insert_article(num: int) -> int:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "batch-infographic.py"), "insert", str(num), str(num)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print(r.stdout.strip())
    if r.stderr:
        print(r.stderr.strip())
    arts = list(ROOT.glob(f"{num}.*-tutorial.md"))
    if not arts:
        return 0
    return len(IMG_REF.findall(arts[0].read_text(encoding="utf-8")))


def finish_article(num: int, pngs: list[str]) -> dict:
    slug = slug_from_num(num)
    if not slug:
        return {"num": num, "status": "no_article"}
    copied = sum(1 for p in pngs if copy_png(slug, p))
    refs = insert_article(num)
    readme = ROOT / "image" / slug / "README.md"
    expected = len(README_ROW.findall(readme.read_text(encoding="utf-8"))) if readme.exists() else 0
    return {"num": num, "slug": slug, "copied": copied, "refs": refs, "expected": expected}


def read_prompt(slug: str, stem: str) -> str:
    p = ROOT / "image" / slug / "prompts" / f"{stem}.md"
    text = p.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def pending_pngs(num: int) -> list[str]:
    slug = slug_from_num(num)
    if not slug:
        return []
    img_dir = ROOT / "image" / slug
    readme = img_dir / "README.md"
    if not readme.exists():
        return []
    return [p for p in README_ROW.findall(readme.read_text(encoding="utf-8")) if not (img_dir / p).exists()]


if __name__ == "__main__":
    if sys.argv[1] == "finish":
        num = int(sys.argv[2])
        pngs = sys.argv[3:]
        import json
        print(json.dumps(finish_article(num, pngs), ensure_ascii=False))
    elif sys.argv[1] == "pending":
        lo, hi = int(sys.argv[2]), int(sys.argv[3])
        for num in range(lo, hi + 1):
            need = pending_pngs(num)
            if need:
                print(f"{num}|{slug_from_num(num)}|{','.join(need)}")
