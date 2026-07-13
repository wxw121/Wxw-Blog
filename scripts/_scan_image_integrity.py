#!/usr/bin/env python3
"""Scan all docs for missing images or unreferenced generated PNGs."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_REF = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)


def main() -> None:
    all_pngs = {
        str(p.relative_to(ROOT)).replace("\\", "/"): p
        for p in ROOT.glob("image/**/*.png")
    }

    md_refs: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for md in ROOT.glob("**/*.md"):
        if "node_modules" in md.parts:
            continue
        rel_md = str(md.relative_to(ROOT)).replace("\\", "/")
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for m in IMG_REF.finditer(line):
                path = m.group(2)
                if path.startswith("image/"):
                    md_refs[path].append((rel_md, m.group(1), i))

    manifest = json.loads((ROOT / "image/manifest.json").read_text(encoding="utf-8"))
    manifest_paths = {m["img_path"] for m in manifest}

    readme_expected: dict[str, list[str]] = defaultdict(list)
    for readme in ROOT.glob("image/*/README.md"):
        slug = readme.parent.name
        if slug.startswith("_"):
            continue
        for png in README_ROW.findall(readme.read_text(encoding="utf-8")):
            readme_expected[slug].append(png)

    print("=" * 60)
    print("SCAN REPORT: Blog image integrity")
    print("=" * 60)

    missing_files = [
        (path, refs)
        for path, refs in sorted(md_refs.items())
        if not (ROOT / path).exists()
    ]
    print(f"\n[A] 文章引用了但文件不存在: {len(missing_files)}")
    for path, refs in missing_files:
        for f, alt, ln in refs[:2]:
            print(f"  {path} <- {f}:{ln} alt={alt[:40]}")

    referenced_paths = set(md_refs.keys())
    orphan_pngs = [p for p in sorted(all_pngs) if p not in referenced_paths]
    print(f"\n[B] 已生成 PNG 但无任何文章引用: {len(orphan_pngs)}")
    for p in orphan_pngs:
        print(f"  {p}")

    manifest_missing_disk = [
        p for p in sorted(manifest_paths) if not (ROOT / p).exists()
    ]
    print(f"\n[C] manifest 登记但磁盘无 PNG: {len(manifest_missing_disk)}")
    for p in manifest_missing_disk:
        print(f"  {p}")

    manifest_not_in_md = []
    for m in manifest:
        path = m["img_path"]
        f = m["file"]
        if not (ROOT / f).exists():
            continue
        text = (ROOT / f).read_text(encoding="utf-8")
        if path not in text:
            manifest_not_in_md.append((f, path, m.get("alt", "")[:50]))

    print(f"\n[D] manifest 有图路径但文章未引用: {len(manifest_not_in_md)}")
    for f, path, alt in manifest_not_in_md:
        print(f"  {f}: {path} ({alt})")

    readme_missing = []
    for slug, pngs in sorted(readme_expected.items()):
        img_dir = ROOT / "image" / slug
        have = {p.name for p in img_dir.glob("*.png")} if img_dir.exists() else set()
        missing = [p for p in pngs if p not in have]
        if missing:
            arts = list(ROOT.glob(f"*.{slug}-tutorial.md"))
            art = arts[0].name if arts else "?"
            refs = 0
            if arts:
                refs = len(IMG_REF.findall(arts[0].read_text(encoding="utf-8")))
            readme_missing.append((slug, art, missing, refs, len(pngs)))

    print(f"\n[E] image/*/README 登记应生成但缺 PNG: {len(readme_missing)} 个主题")
    for slug, art, missing, refs, total in readme_missing:
        print(f"  {art}: 缺 {missing} (已有引用 {refs}, README共{total}张)")

    no_refs = []
    for slug in readme_expected:
        arts = list(ROOT.glob(f"*.{slug}-tutorial.md"))
        if not arts:
            continue
        art = arts[0]
        num_m = re.match(r"^(\d+)\.", art.name)
        if not num_m or int(num_m.group(1)) < 17:
            continue
        text = art.read_text(encoding="utf-8")
        refs = [
            m.group(2)
            for m in IMG_REF.finditer(text)
            if m.group(2).startswith("image/")
        ]
        if not refs:
            img_dir = ROOT / "image" / slug
            have = list(img_dir.glob("*.png")) if img_dir.exists() else []
            no_refs.append((art.name, slug, len(have), len(readme_expected[slug])))

    print(f"\n[F] 有配图目录但文章完全无 image/ 引用: {len(no_refs)}")
    for art, slug, have, exp in no_refs:
        print(f"  {art}: 磁盘{have}张, README应{exp}张")

    count_mismatch = []
    for slug, pngs in readme_expected.items():
        arts = list(ROOT.glob(f"*.{slug}-tutorial.md"))
        if not arts:
            continue
        art = arts[0]
        num_m = re.match(r"^(\d+)\.", art.name)
        if not num_m or int(num_m.group(1)) < 17:
            continue
        text = art.read_text(encoding="utf-8")
        refs = [
            m.group(2)
            for m in IMG_REF.finditer(text)
            if m.group(2).startswith(f"image/{slug}/")
        ]
        if len(refs) != len(pngs):
            img_dir = ROOT / "image" / slug
            have = (
                {p.name for p in img_dir.glob("*.png")}
                if img_dir.exists()
                else set()
            )
            ref_names = {Path(r).name for r in refs}
            count_mismatch.append(
                (
                    art.name,
                    len(refs),
                    len(pngs),
                    len(have),
                    sorted(set(pngs) - have),
                    sorted(ref_names - set(pngs)),
                )
            )

    print(f"\n[G] 文章引用数 vs README 登记数不一致: {len(count_mismatch)}")
    for art, refs, exp, have, miss_png, extra_ref in count_mismatch:
        print(f"  {art}: refs={refs} readme={exp} disk={have}")
        if miss_png:
            print(f"    缺PNG: {miss_png}")
        if extra_ref:
            print(f"    多引用(非README名): {extra_ref}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"  磁盘 PNG 总数: {len(all_pngs)}")
    print(f"  MD 引用路径数(去重): {len(referenced_paths)}")
    print(f"  manifest 路径数: {len(manifest_paths)}")
    print(f"  [A] 引用缺文件: {len(missing_files)}")
    print(f"  [B] 孤儿 PNG: {len(orphan_pngs)}")
    print(f"  [C] manifest缺磁盘: {len(manifest_missing_disk)}")
    print(f"  [D] manifest未写入MD: {len(manifest_not_in_md)}")
    print(f"  [E] README缺PNG主题: {len(readme_missing)}")
    print(f"  [F] 文章零引用: {len(no_refs)}")
    print(f"  [G] 引用数不一致: {len(count_mismatch)}")


if __name__ == "__main__":
    main()
