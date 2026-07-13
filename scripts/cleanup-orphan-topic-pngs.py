#!/usr/bin/env python3
"""Delete orphan PNGs under image/*/ (unreferenced in MD, not in README table)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def all_md_image_paths() -> set[str]:
    paths: set[str] = set()
    for md in ROOT.glob("**/*.md"):
        if "node_modules" in md.parts:
            continue
        for m in IMG_REF.finditer(md.read_text(encoding="utf-8")):
            p = m.group(1).replace("\\", "/")
            if p.startswith("../"):
                p = p[3:]
            if p.startswith("image/"):
                paths.add(p)
    return paths


def find_orphans() -> list[Path]:
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

    for d in sorted(ROOT.glob("image/*")):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if (d / "README.md").exists():
            continue
        for png in sorted(d.glob("*.png")):
            rel = f"image/{d.name}/{png.name}".replace("\\", "/")
            if rel not in refs:
                orphans.append(png)

    return orphans


def main() -> None:
    dry = "--dry-run" in sys.argv
    orphans = find_orphans()
    print(f"{'Would delete' if dry else 'Deleting'} {len(orphans)} orphan PNG(s):\n")
    for p in orphans:
        rel = p.relative_to(ROOT)
        print(f"  {rel}")
        if not dry:
            p.unlink()
    if not dry:
        print(f"\nDone: removed {len(orphans)} file(s)")


if __name__ == "__main__":
    main()
