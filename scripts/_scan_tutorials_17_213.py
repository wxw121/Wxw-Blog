#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[([^\]]*)\]\((image/[^)]+)\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def slug_from_article(name: str) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", name))


def main() -> None:
    issues: list[tuple[str, int, str, str, str]] = []

    for art in sorted(ROOT.glob("[0-9]*.md")):
        num = int(art.name.split(".", 1)[0])
        if num < 17 or num > 213:
            continue
        slug = slug_from_article(art.name)
        text = art.read_text(encoding="utf-8")
        refs = IMG_REF.findall(text)
        ref_paths = [p for _, p in refs]

        for alt, path in refs:
            if not (ROOT / path).exists():
                issues.append(("REF_MISSING_FILE", num, slug, path, alt[:30]))

        readme = ROOT / "image" / slug / "README.md"
        if readme.exists():
            expected = README_ROW.findall(readme.read_text(encoding="utf-8"))
            img_dir = ROOT / "image" / slug
            have = {p.name for p in img_dir.glob("*.png")}

            for png in expected:
                full = f"image/{slug}/{png}"
                if png in have and full not in ref_paths:
                    issues.append(("PNG_NOT_REFERENCED", num, slug, full, png))

            for png in expected:
                if png not in have:
                    issues.append(("PNG_NOT_GENERATED", num, slug, f"image/{slug}/{png}", png))

            if expected and not ref_paths:
                issues.append(
                    ("ARTICLE_NO_REFS", num, slug, "", f"expected {len(expected)}")
                )
        elif ref_paths:
            issues.append(
                ("REFS_NO_README", num, slug, ref_paths[0], f"{len(ref_paths)} refs")
            )

    cats = Counter(i[0] for i in issues)
    print("ISSUES BY TYPE (articles 17-213):")
    for k, v in sorted(cats.items()):
        print(f"  {k}: {v}")

    for cat in [
        "PNG_NOT_GENERATED",
        "REF_MISSING_FILE",
        "PNG_NOT_REFERENCED",
        "ARTICLE_NO_REFS",
    ]:
        rows = [i for i in issues if i[0] == cat]
        if rows:
            print(f"\n=== {cat} ({len(rows)}) ===")
            for row in rows:
                print(f"  {row[1]:3d} {row[2]}: {row[3]}")

    print("\n=== DUPLICATE REFS IN ARTICLE ===")
    dup_count = 0
    for art in sorted(ROOT.glob("[0-9]*.md")):
        num = int(art.name.split(".", 1)[0])
        if num < 17 or num > 213:
            continue
        text = art.read_text(encoding="utf-8")
        paths = [m.group(2) for m in IMG_REF.finditer(text)]
        seen: set[str] = set()
        dups: list[str] = []
        for p in paths:
            if p in seen:
                dups.append(p)
            seen.add(p)
        if dups:
            dup_count += 1
            print(
                f"  {num} {slug_from_article(art.name)}: "
                f"{len(paths)} refs, {len(set(paths))} unique"
            )
    print(f"Total articles with duplicate refs: {dup_count}")


if __name__ == "__main__":
    main()
