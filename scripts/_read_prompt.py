#!/usr/bin/env python3
"""Print prompt body (after YAML frontmatter) for a prompt file."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_prompt(rel_path: str) -> str:
    text = (ROOT / rel_path).read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].strip()
    return text.strip()


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"=== {p} ===")
        print(read_prompt(p))
