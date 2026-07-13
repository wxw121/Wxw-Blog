#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[([^\]]*)\]\((image/[^)]+)\)")


def slug_from_article(name: str) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", name))


def scan_group(label: str, articles: list[Path]) -> None:
    print(f"\n--- {label} ---")
    for art in articles:
        text = art.read_text(encoding="utf-8")
        refs = [p for _, p in IMG_REF.findall(text)]
        missing = [p for p in refs if not (ROOT / p).exists()]
        ascii_boxes = text.count("┌─") + text.count("┌──")
        line = f"{art.name}: img_refs={len(refs)}"
        if missing:
            line += f" MISSING_ON_DISK={missing}"
        if ascii_boxes:
            line += f" ascii_boxes~={ascii_boxes}"
        if not refs and ascii_boxes:
            line += " [ASCII_NOT_REPLACED]"
        print(line)


def main() -> None:
    for art in sorted(ROOT.glob("[0-9]*.md")):
        num = int(art.name.split(".", 1)[0])
        if 17 <= num <= 213:
            slug = slug_from_article(art.name)
            readme = ROOT / "image" / slug / "README.md"
            refs = IMG_REF.findall(art.read_text(encoding="utf-8"))
            if refs and not readme.exists():
                print(f"REFS_NO_README: {num} {slug} refs={len(refs)}")

    scan_group("Articles 1-16", sorted(ROOT.glob("[0-9]*.md"))[:16])
    scan_group("nextjs", sorted((ROOT / "nextjs").glob("*.md")))
    scan_group("react", sorted((ROOT / "react").glob("*.md")))
    scan_group("skill", sorted((ROOT / "skill").glob("*.md")))

    # orphan PNGs for early series
    print("\n--- Orphan PNG groups (generated but unreferenced) ---")
    groups = [
        "python-virtual-env",
        "python-type-annotation",
        "python-asyncio",
        "python-asyncio-tutorial",
        "react-javascript",
        "superpowers-frontend-design",
        "sparse-retrieval-rag",
    ]
    for g in groups:
        d = ROOT / "image" / g
        if not d.exists():
            continue
        pngs = list(d.glob("*.png"))
        if not pngs:
            continue
        # check if any md references this dir
        ref_count = 0
        for md in ROOT.glob("**/*.md"):
            if g in md.read_text(encoding="utf-8"):
                ref_count += 1
        print(f"  image/{g}: {len(pngs)} PNGs, referenced by {ref_count} md files")


if __name__ == "__main__":
    main()
