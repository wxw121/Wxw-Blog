from pathlib import Path
import json
import re

ROOT = Path(".")
NUM_RE = re.compile(r"^(\d+)\.")
MARKER_RE = re.compile(
    r"<!-- topup-batch|TODO|TBD|待补|待重制|placeholder|占位|图片 prompt|替换正文占位|"
    r"等待生成 PNG|生成 PNG 后|全系列配图约定|系列配图 prompts 已就绪|请完成本篇|"
    r"配图 prompts 已就绪|build residue|topup",
    re.I,
)
HEADING_RE = re.compile(r"^(#{2,6})\s+(.+)$")
PROSE_EXCLUDE_RE = re.compile(
    r"^(#{1,6})\s+|^\|.*\|\s*$|^-\s+|^\d+\.\s+|^!\[|^>|^---$"
)


def article_number(path: Path) -> int:
    return int(NUM_RE.match(path.name).group(1))


def is_prose_line(text: str) -> bool:
    return bool(text) and not PROSE_EXCLUDE_RE.match(text)


def scan_file(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    in_fence = False
    headings = []
    markers = []
    code_starts = []
    images = []
    mermaid = 0
    code_fences = 0
    tables = sum(1 for line in lines if re.match(r"^\|.+\|\s*$", line.strip()))

    for idx, line in enumerate(lines, start=1):
        if line.startswith("```"):
            if line.strip() == "```mermaid":
                mermaid += 1
            if not in_fence:
                code_starts.append(idx)
            in_fence = not in_fence
            code_fences += 1
            continue
        if in_fence:
            continue
        if MARKER_RE.search(line):
            markers.append(f"L{idx}: {line.strip()}")
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                {"line": idx, "level": len(match.group(1)), "text": match.group(2).strip()}
            )
        if re.match(r"^!\[.*?\]\(.*?\)", line):
            images.append(idx)

    weak = []
    empty = []
    for heading in headings:
        if heading["text"] == "目录":
            continue
        next_heading = next(
            (
                item
                for item in headings
                if item["line"] > heading["line"] and item["level"] <= heading["level"]
            ),
            None,
        )
        end = next_heading["line"] - 1 if next_heading else len(lines)
        has_prose = False
        content_count = 0
        in_section_fence = False
        for line_no in range(heading["line"], end):
            current = lines[line_no].strip()
            if current.startswith("```"):
                in_section_fence = not in_section_fence
                continue
            if in_section_fence or not current:
                continue
            content_count += 1
            if is_prose_line(current):
                has_prose = True
        if content_count == 0:
            empty.append(f"L{heading['line']}: {heading['text']}")
        elif not has_prose:
            weak.append(f"L{heading['line']}: {heading['text']}")

    seen = {}
    for heading in headings:
        if heading["text"] != "目录":
            seen.setdefault(heading["text"], []).append(heading["line"])
    duplicate_headings = [
        f"{text} x{len(lines_)} @ {','.join(map(str, lines_[:4]))}"
        for text, lines_ in seen.items()
        if len(lines_) > 1
    ]

    numbers = {}
    for heading in headings:
        match = re.match(r"^(\d+)(?:\.|\s)", heading["text"])
        if match:
            numbers.setdefault(match.group(1), []).append(heading["line"])
    duplicate_numbers = [
        f"§{number} x{len(lines_)} @ {','.join(map(str, lines_[:4]))}"
        for number, lines_ in numbers.items()
        if len(lines_) > 1
    ]

    paragraphs = []
    buffer = []
    in_para_fence = False
    for line in lines:
        current = line.strip()
        if current.startswith("```"):
            in_para_fence = not in_para_fence
            continue
        if in_para_fence:
            continue
        if not current or PROSE_EXCLUDE_RE.match(current):
            if buffer:
                paragraph = " ".join(buffer).strip()
                if len(paragraph) >= 45:
                    paragraphs.append(paragraph)
                buffer = []
        else:
            buffer.append(current)
    if buffer:
        paragraph = " ".join(buffer).strip()
        if len(paragraph) >= 45:
            paragraphs.append(paragraph)

    paragraph_counts = {}
    for paragraph in paragraphs:
        paragraph_counts[paragraph] = paragraph_counts.get(paragraph, 0) + 1
    duplicate_paragraphs = [
        f"{count}x {paragraph[:100]}"
        for paragraph, count in sorted(paragraph_counts.items(), key=lambda item: -item[1])
        if count > 1
    ][:3]

    code_no_intro = []
    code_no_after = []
    for start in code_starts:
        if lines[start - 1].strip() == "```mermaid":
            continue
        previous_lines = []
        for line_no in range(start - 2, max(-1, start - 8), -1):
            current = lines[line_no].strip()
            if not current:
                continue
            previous_lines.append(current)
            if len(previous_lines) >= 4:
                break
        if not any(is_prose_line(item) and not item.startswith("```") for item in previous_lines):
            code_no_intro.append(f"L{start}")

        close = None
        for line_no in range(start, len(lines)):
            if lines[line_no].startswith("```"):
                close = line_no + 1
                break
        if close:
            following_lines = []
            for line_no in range(close, min(len(lines), close + 7)):
                current = lines[line_no].strip()
                if not current:
                    continue
                following_lines.append(current)
                if len(following_lines) >= 4:
                    break
            if not any(is_prose_line(item) and not item.startswith("```") for item in following_lines):
                code_no_after.append(f"L{start}")

    number = article_number(path)
    hanzi = len(re.sub(r"[^\u4e00-\u9fff]", "", text))
    code_blocks = max(0, (code_fences // 2) - mermaid)
    flags = []
    score = 0
    if markers:
        flags.append("marker")
        score += 6
    if code_fences % 2:
        flags.append("odd-fence")
        score += 6
    if empty:
        flags.append("empty-section")
        score += 5
    if weak:
        flags.append("weak-heading")
        score += min(5, len(weak))
    if duplicate_paragraphs:
        flags.append("dupe-paragraph")
        score += 4
    if duplicate_headings:
        flags.append("dupe-heading")
        score += 2
    if duplicate_numbers:
        flags.append("dupe-section-number")
        score += 2
    if code_no_intro:
        flags.append("code-no-intro")
        score += min(3, len(code_no_intro))
    if code_no_after:
        flags.append("code-no-after")
        score += min(2, len(code_no_after))
    if number >= 137 and hanzi < 2800:
        flags.append("thin-late-article")
        score += 2
    if number >= 156 and code_blocks == 0:
        flags.append("no-code-late-practical")
        score += 1
    if number >= 179 and mermaid == 0 and tables < 8 and not images:
        flags.append("low-visual-structure")
        score += 1

    if not score:
        return None
    return {
        "file": path.name,
        "score": score,
        "flags": flags,
        "hanzi": hanzi,
        "codeBlocks": code_blocks,
        "mermaid": mermaid,
        "images": len(images),
        "tables": tables,
        "markers": markers[:4],
        "emptySections": empty[:6],
        "weakHeadings": weak[:8],
        "duplicateHeadings": duplicate_headings[:5],
        "duplicateNumbers": duplicate_numbers[:5],
        "duplicateParagraphs": duplicate_paragraphs,
        "codeNoIntro": code_no_intro[:8],
        "codeNoAfter": code_no_after[:8],
    }


def main() -> None:
    files = sorted(
        [
            path
            for path in ROOT.glob("*.md")
            if NUM_RE.match(path.name) and article_number(path) >= 50
        ],
        key=article_number,
    )
    rows = [row for path in files if (row := scan_file(path))]
    rows.sort(key=lambda row: (-row["score"], row["file"]))
    print(
        json.dumps(
            {"file_count": len(files), "issue_count": len(rows), "top": rows[:80]},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
