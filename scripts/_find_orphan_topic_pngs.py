#!/usr/bin/env python3
"""Find PNG files under image/*/ not referenced in MD and not in README tables."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def all_md_image_paths() -> set[str]:
    paths: set[str] = set()
    for md in ROOT.glob("**/*.md"):
        if "node_modules" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for m in IMG_REF.finditer(text):
            p = m.group(1).replace("\\", "/")
            if p.startswith("../"):
                p = p[3:]
            if p.startswith("image/"):
                paths.add(p)
    return paths


def main() -> None:
    refs = all_md_image_paths()
    orphans: list[Path] = []

    for readme in sorted(ROOT.glob("image/*/README.md")):
        slug = readme.parent.name
        if slug.startswith("_"):
            continue
        expected = set(README_ROW.findall(readme.read_text(encoding="utf-8")))
        for png in sorted(readme.parent.glob("*.png")):
            rel = f"image/{slug}/{png.name}".replace("\\", "/")
            if rel not in refs and png.name not in expected:
                orphans.append(png)

    # PNGs in topic dirs without README, unreferenced
    for d in sorted(ROOT.glob("image/*")):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if (d / "README.md").exists():
            continue
        for png in sorted(d.glob("*.png")):
            rel = f"image/{d.name}/{png.name}".replace("\\", "/")
            if rel not in refs:
                orphans.append(png)

    print(f"Orphan PNGs (not in any MD, not in README table): {len(orphans)}")
    for p in orphans:
        print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
