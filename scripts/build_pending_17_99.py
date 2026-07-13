#!/usr/bin/env python3
"""Build pending infographic manifest from README + prompts for articles 17-21, 90-99."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.IGNORECASE)
ARTICLE_RE = re.compile(r"^(\d+)\.")

SLUGS_17_21 = [
    "nlp-tokenization-basics",
    "tfidf-principles",
    "bm25-sparse-retrieval",
    "inverted-index",
    "word2vec-static-embeddings",
]
SLUGS_90_99 = [
    "vector-db-backup",
    "dense-retrieval",
    "sparse-retrieval-rag",
    "hybrid-search",
    "rrf-fusion",
    "cross-encoder-rerank",
    "bge-reranker",
    "cohere-rerank",
    "top-k-retrieval",
    "score-threshold",
]


def slug_to_num(slug: str) -> int | None:
    for p in ROOT.glob(f"*.{slug}-tutorial.md"):
        m = ARTICLE_RE.match(p.name)
        if m:
            return int(m.group(1))
    return None


def prompt_body(prompt_path: Path) -> str:
    text = prompt_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].strip()
    return text.strip()


def collect(slugs: list[str]) -> list[dict]:
    items: list[dict] = []
    for slug in slugs:
        img_dir = ROOT / "image" / slug
        readme = img_dir / "README.md"
        if not readme.exists():
            continue
        pngs = README_ROW.findall(readme.read_text(encoding="utf-8"))
        n = slug_to_num(slug)
        for png in pngs:
            dst = img_dir / png
            stem = png.replace(".png", "")
            prompt_path = img_dir / "prompts" / f"{stem}.md"
            if not prompt_path.exists():
                continue
            items.append(
                {
                    "n": n,
                    "slug": slug,
                    "png": png,
                    "prompt": prompt_body(prompt_path),
                    "exists": dst.exists(),
                }
            )
    return items


def main() -> None:
    items = collect(SLUGS_17_21) + collect(SLUGS_90_99)
    pending = [i for i in items if not i["exists"]]
    out = ROOT / "scripts" / "_pending_17_99.json"
    out.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total: {len(items)}, pending: {len(pending)} -> {out}")
    by_slug: dict[str, int] = {}
    for i in pending:
        by_slug[i["slug"]] = by_slug.get(i["slug"], 0) + 1
    for slug, c in sorted(by_slug.items(), key=lambda x: x[0]):
        print(f"  {slug}: {c}")


if __name__ == "__main__":
    main()
