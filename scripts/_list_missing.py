#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
README_ROW = re.compile(r"\|\s*`([^`]+\.png)`\s*\|", re.I)
slugs = [
    "coreference-resolution", "unauthorized-doc-filter", "content-safety-filter",
    "structured-output-json", "function-calling-tool-use", "langchain-core",
    "langchain-lcel", "langchain-retriever", "langchain-vectorstore",
    "langchain-document-loader", "langchain-text-splitter", "llamaindex-index-types",
    "llamaindex-query-engine", "llamaindex-agent", "haystack-pipeline",
    "pipeline-vs-framework", "pluggable-parser-splitter-embedder",
    "pluggable-store-retriever-generator", "config-driven-pipeline",
    "ragas-context-precision",
]
for slug in slugs:
    d = ROOT / "image" / slug
    readme = d / "README.md"
    if not readme.exists():
        print(f"MISSING README {slug}")
        continue
    text = readme.read_text(encoding="utf-8")
    pngs = [m.group(1) for m in README_ROW.finditer(text)]
    for png in pngs:
        p = d / png
        status = "HAVE" if p.exists() else "NEED"
        # map png to prompt
        stem = png.replace(".png", "")
        pr_dir = d / "prompts"
        prompt = None
        if pr_dir.exists():
            for f in sorted(pr_dir.glob("*.md")):
                if stem.split("-", 1)[-1] in f.stem or f.stem.endswith(stem):
                    prompt = f
                    break
            if not prompt:
                num = stem.split("-")[0]
                for f in sorted(pr_dir.glob(f"{num}-*.md")):
                    prompt = f
                    break
        print(f"{status}\t{slug}\t{png}\t{prompt}")
