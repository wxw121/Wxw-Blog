#!/usr/bin/env python3
"""Remove duplicate ![alt](image/...) lines in tutorial markdown (keep longer alt)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_LINE = re.compile(r"^(!\[[^\]]*\]\((image/[^)]+)\))\s*$")


def dedupe_file(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    # path -> list of (index, alt, full_line_without_newline)
    by_path: dict[str, list[tuple[int, str, str]]] = {}

    for i, line in enumerate(lines):
        m = IMG_LINE.match(line.rstrip("\n\r"))
        if not m:
            continue
        full, img_path = m.group(1), m.group(2)
        alt_m = re.match(r"!\[([^\]]*)\]", full)
        alt = alt_m.group(1) if alt_m else ""
        by_path.setdefault(img_path, []).append((i, alt, line))

    remove_indices: set[int] = set()
    for img_path, occurrences in by_path.items():
        if len(occurrences) < 2:
            continue
        # Keep the occurrence with the longest alt; tie-break: last wins
        keep = max(occurrences, key=lambda x: (len(x[1]), x[0]))
        for idx, alt, _ in occurrences:
            if idx != keep[0]:
                remove_indices.add(idx)
                # If a blank line follows a removed image line, remove trailing blank
                # only when it was between two duplicate image blocks — handled below

    if not remove_indices:
        return 0

    out: list[str] = []
    for i, line in enumerate(lines):
        if i in remove_indices:
            continue
        out.append(line)

    # Collapse runs of 3+ newlines to 2 (optional cleanup after removing dup + blank)
    text = "".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    path.write_text(text, encoding="utf-8")
    return len(remove_indices)


def main() -> None:
    total_removed = 0
    files_changed = 0

    for art in sorted(ROOT.glob("[0-9]*.md")):
        n = dedupe_file(art)
        if n:
            files_changed += 1
            total_removed += n
            print(f"{art.name}: removed {n} duplicate image line(s)")

    print(f"\nDone: {files_changed} files, {total_removed} lines removed")


if __name__ == "__main__":
    main()
