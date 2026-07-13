#!/usr/bin/env python3
"""Build pending infographic manifest for articles 84-120 priority slugs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.IGNORECASE)

SLUGS = [
    "flat-brute-force-search",
    "ivf-index",
    "hnsw-index",
    "ann-recall-latency",
    "metadata-filter-retrieval",
    "multi-tenant-namespace",
    "vector-db-backup",
    "sparse-retrieval-rag",
    "bge-reranker",
    "cohere-rerank",
    "top-k-retrieval",
    "score-threshold",
    "conversation-query-enhancement",
    "rag-prompt-template",
    "context-injection-format",
    "refusal-strategy",
    "inline-citation",
    "footnote-citation",
    "source-document-navigation",
    "sse-rag-streaming",
    "websocket-rag-streaming",
    "multi-turn-history",
    "summary-memory",
]


def prompt_body(prompt_path: Path) -> str:
    text = prompt_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].strip()
    return text.strip()


def main() -> None:
    items: list[dict] = []
    for slug in SLUGS:
        img_dir = ROOT / "image" / slug
        readme = img_dir / "README.md"
        if not readme.exists():
            print(f"NO README {slug}")
            continue
        pngs = README_ROW.findall(readme.read_text(encoding="utf-8"))
        for png in pngs:
            dst = img_dir / png
            stem = png.replace(".png", "")
            prompt_path = img_dir / "prompts" / f"{stem}.md"
            if not prompt_path.exists():
                print(f"NO PROMPT {slug}/{stem}")
                continue
            items.append(
                {
                    "slug": slug,
                    "png": png,
                    "prompt": prompt_body(prompt_path),
                    "exists": dst.exists(),
                }
            )
    pending = [i for i in items if not i["exists"]]
    out = ROOT / "scripts" / "_pending_84_120.json"
    out.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total: {len(items)}, pending: {len(pending)} -> {out}")
    by_slug: dict[str, int] = {}
    for i in pending:
        by_slug[i["slug"]] = by_slug.get(i["slug"], 0) + 1
    for slug, c in sorted(by_slug.items()):
        print(f"  {slug}: {c}")


if __name__ == "__main__":
    main()
