#!/usr/bin/env python3
"""Final audit report for user."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[([^\]]*)\]\((image/[^)]+)\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def article_num(name: str) -> int | None:
    m = re.match(r"^(\d+)\.", name)
    return int(m.group(1)) if m else None


def slug_from_article(name: str) -> str:
    return re.sub(r"-tutorial\.md$", "", re.sub(r"^\d+\.", "", name))


def collect_refs(md: Path) -> list[str]:
    return [p for _, p in IMG_REF.findall(md.read_text(encoding="utf-8"))]


def main() -> None:
    # --- 1. Missing files referenced in articles ---
    missing_by_article: dict[str, list[str]] = defaultdict(list)
    all_articles = sorted(ROOT.glob("**/*.md"), key=lambda p: str(p))
    skip_parts = {"node_modules", ".baoyu-skills", "infographic"}

    for md in all_articles:
        if any(s in md.parts for s in skip_parts):
            continue
        if md.name == "README.md" and "image" in md.parts:
            continue
        for path in collect_refs(md):
            if not (ROOT / path).exists():
                missing_by_article[str(md.relative_to(ROOT))].append(path)

    print("=" * 70)
    print("1. 文章引用了但磁盘上不存在（真实问题）")
    print("=" * 70)
    real_missing = {
        k: v
        for k, v in missing_by_article.items()
        if not any("README" in k or ".batch-" in k or "EXTEND" in k for _ in [0])
    }
    if not real_missing:
        print("  无（教程正文全部命中）")
    else:
        for art, paths in sorted(real_missing.items()):
            print(f"  {art}")
            for p in paths:
                print(f"    - {p}")

    # --- 2. PNG exists under image/<slug> but not referenced in its tutorial ---
    print("\n" + "=" * 70)
    print("2. 已生成 PNG 但对应教程未引用")
    print("=" * 70)
    orphan_in_topic: list[str] = []
    for readme in sorted(ROOT.glob("image/*/README.md")):
        slug = readme.parent.name
        if slug.startswith("_"):
            continue
        expected = README_ROW.findall(readme.read_text(encoding="utf-8"))
        arts = list(ROOT.glob(f"*.{slug}-tutorial.md"))
        if not arts:
            continue
        art = arts[0]
        ref_paths = set(collect_refs(art))
        for png in sorted(readme.parent.glob("*.png")):
            full = f"image/{slug}/{png.name}"
            if full not in ref_paths:
                orphan_in_topic.append(f"  {art.name}: {png.name} (README登记={png.name in expected})")

    # also PNGs not in README at all
    extra_orphans = [x for x in orphan_in_topic if "README登记=False" in x]
    readme_orphans = [x for x in orphan_in_topic if "README登记=True" in x]
    if readme_orphans:
        print("  README 登记但未引用:")
        for x in readme_orphans:
            print(x)
    if extra_orphans:
        print("  磁盘有图但 README 未登记、文章也未引用（多余/旧版）:")
        for x in extra_orphans:
            print(x)
    if not orphan_in_topic:
        print("  无")

    # --- 3. Tutorials 17-213 summary ---
    print("\n" + "=" * 70)
    print("3. 教程 17–213 专项")
    print("=" * 70)
    no_png = no_ref = dup = 0
    dup_list = []
    for art in sorted(ROOT.glob("[0-9]*.md")):
        n = article_num(art.name)
        if n is None or n < 17 or n > 213:
            continue
        slug = slug_from_article(art.name)
        refs = collect_refs(art)
        img_dir = ROOT / "image" / slug
        pngs = list(img_dir.glob("*.png")) if img_dir.exists() else []
        readme = img_dir / "README.md"
        if readme.exists() and not pngs:
            no_png += 1
        if readme.exists() and pngs and not refs:
            no_ref += 1
        paths = refs
        if len(paths) != len(set(paths)):
            dup += 1
            dup_list.append(f"  {n} {slug}: {len(paths)} 处引用, {len(set(paths))} 张唯一图（每张重复 2 次）")

    print(f"  缺 PNG（有 README 无文件）: {no_png}")
    print(f"  有图但文章零引用: {no_ref}")
    print(f"  引用路径缺文件: {sum(1 for a,p in real_missing.items() if article_num(Path(a).name) and 17<=article_num(Path(a).name)<=213)}")
    print(f"  重复引用（同图两行）: {dup} 篇")
    if dup_list:
        print("  重复引用列表（前 5 篇示例）:")
        for line in dup_list[:5]:
            print(line)
        if len(dup_list) > 5:
            print(f"  ... 共 {len(dup_list)} 篇")

    # --- 4. Early tutorials & side series ---
    print("\n" + "=" * 70)
    print("4. 其他系列（1–16 / nextjs / react / skill）")
    print("=" * 70)

    def series_report(label: str, paths: list[Path]) -> None:
        no_img = []
        missing = []
        ascii_left = []
        for md in paths:
            text = md.read_text(encoding="utf-8")
            refs = collect_refs(md)
            miss = [p for p in refs if not (ROOT / p).exists()]
            if miss:
                missing.append((md.name, miss))
            if not refs:
                no_img.append(md.name)
            if ("┌─" in text or "┌──" in text) and len(refs) < 2:
                ascii_left.append(md.name)
        print(f"\n  [{label}]")
        print(f"    无 image/ 引用: {len(no_img)} 篇")
        if no_img:
            for x in no_img:
                print(f"      - {x}")
        print(f"    引用缺文件: {len(missing)} 篇")
        for name, miss in missing:
            print(f"      - {name}: {miss}")
        print(f"    仍有 ASCII 框未替换: {len(ascii_left)} 篇")
        for x in ascii_left:
            print(f"      - {x}")

    early = [p for p in ROOT.glob("[0-9]*.md") if (n := article_num(p.name)) and 1 <= n <= 16]
    series_report("1-16", sorted(early, key=lambda p: article_num(p.name) or 0))
    series_report("nextjs", sorted((ROOT / "nextjs").glob("*.md")))
    series_report("react", sorted((ROOT / "react").glob("*.md")))
    series_report("skill", sorted((ROOT / "skill").glob("*.md")))

    # nextjs/react generated PNG dirs
    print("\n  [nextjs/react 已生成图但未写入文章]")
    for prefix in ["nextjs-", "react-"]:
        dirs = [d for d in (ROOT / "image").iterdir() if d.is_dir() and d.name.startswith(prefix)]
        if dirs:
            total = sum(len(list(d.glob("*.png"))) for d in dirs)
            print(f"    image/{prefix}*: {len(dirs)} 个目录, {total} 张 PNG, 文章引用数=0")

    # --- 5. Legacy orphan PNGs in image/ root ---
    print("\n" + "=" * 70)
    print("5. 其他孤儿图（有 PNG、无文章引用）")
    print("=" * 70)
    all_refs = set()
    for md in ROOT.glob("**/*.md"):
        if any(s in md.parts for s in skip_parts):
            continue
        all_refs.update(collect_refs(md))

    legacy_groups = []
    for p in sorted(ROOT.glob("image/**/*.png")):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if rel not in all_refs:
            legacy_groups.append(rel)

    # group by directory
    by_dir: dict[str, int] = defaultdict(int)
    for p in legacy_groups:
        by_dir[str(Path(p).parent)] += 1
    for d, c in sorted(by_dir.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c} 张未引用")


if __name__ == "__main__":
    main()
