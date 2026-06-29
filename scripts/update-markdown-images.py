"""Remove ASCII diagram code blocks and insert image references."""
import json
import os
import re

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX_CHARS = "┌┐└┘├┤┬┴┼─│╔╗╚╝╠╣╦╩╬═║"

EXISTING = {
    ("3.python-asyncio-tutorial.md", 53): ("image/python-asyncio/01-binary-comparison-sync-async.png", "同步 vs 异步下载：487 秒 vs ~10 秒"),
    ("3.python-asyncio-tutorial.md", 70): None,
    ("3.python-asyncio-tutorial.md", 106): ("image/python-asyncio/02-bento-grid-kitchen-analogy.png", "三种做菜方式：同步阻塞 vs 多线程 vs 异步"),
    ("3.python-asyncio-tutorial.md", 117): None,
    ("3.python-asyncio-tutorial.md", 129): None,
    ("3.python-asyncio-tutorial.md", 154): ("image/python-asyncio/03-tree-branching-when-async.png", "什么时候该用 asyncio：CPU 密集 vs I/O 密集"),
    ("3.python-asyncio-tutorial.md", 203): ("image/python-asyncio/04-linear-progression-coroutine-lifecycle.png", "协程函数生命周期：async def → coro → await → asyncio.run"),
    ("3.python-asyncio-tutorial.md", 375): ("image/python-asyncio/05-hub-spoke-event-loop.png", "事件循环：单线程协作式调度器"),
    ("2.python-type-annotation-tutorial.md", 1219): ("image/python-type-annotation/06-framework-data-model-choice.png", "dataclass vs TypedDict vs Pydantic 决策树"),
}

# Extra ASCII blocks not caught by box-char detector
EXTRA_BLOCKS = {
    ("3.python-asyncio-tutorial.md", 309): ("image/python-asyncio/08-linear-gather-timeline.png", "asyncio.gather() 并发时间线"),
    ("3.python-asyncio-tutorial.md", 429): ("image/python-asyncio/09-linear-semaphore-timeline.png", "信号量 Semaphore 控制并发下载"),
}


def is_diagram_block(lines: list[str], start_line: int, fname: str) -> bool:
    if (fname, start_line) in EXTRA_BLOCKS:
        return True
    content = "".join(lines)
    has_box = any(c in content for c in BOX_CHARS)
    has_flow = bool(re.search(r"[├└│].*→", content))
    has_timeline = bool(re.search(r"──▶|○───|\[={3,}\]", content))
    is_dir_tree = bool(re.search(r"^├── [\w.]", content, re.M)) and "┌" not in content
    if is_dir_tree and not has_flow and not has_timeline:
        return False
    return has_box or has_flow or has_timeline


def load_manifest() -> dict[tuple[str, int], dict]:
    with open(os.path.join(BLOG, "image", "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(os.path.join(BLOG, "image", "_inventory.json"), encoding="utf-8") as f:
        items = json.load(f)
    mapping = {}
    for item in items:
        mapping[(item["file"], item["start"])] = item
    return mapping


def process_file(fname: str, mapping: dict) -> int:
    path = os.path.join(BLOG, fname)
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    out: list[str] = []
    i = 0
    removed = 0
    inserted_paths: set[str] = set()

    while i < len(lines):
        if lines[i].rstrip() == "```":
            j = i + 1
            block_lines = []
            while j < len(lines) and lines[j].rstrip() != "```":
                block_lines.append(lines[j])
                j += 1
            start_line = i + 1
            if j < len(lines) and is_diagram_block(block_lines, start_line, fname):
                key = (fname, start_line)
                existing = EXISTING.get(key)
                extra = EXTRA_BLOCKS.get(key)
                item = mapping.get(key)
                img_ref = None
                if existing:
                    img_ref = existing
                elif extra:
                    img_ref = extra
                elif item:
                    img_ref = (item["img_path"], item.get("alt", "示意图"))
                if img_ref and img_ref[0] not in inserted_paths:
                    out.append(f"![{img_ref[1]}]({img_ref[0]})\n\n")
                    inserted_paths.add(img_ref[0])
                removed += 1
                i = j + 1
                continue
        out.append(lines[i])
        i += 1

    # Drop duplicate consecutive image lines
    cleaned: list[str] = []
    prev_img = None
    for line in out:
        if line.startswith("![") and line == prev_img:
            continue
        if line.startswith("!["):
            prev_img = line
        else:
            prev_img = None
        cleaned.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(cleaned)
    return removed


def main():
    mapping = load_manifest()
    files = sorted({k[0] for k in mapping})
    total = 0
    for fname in files:
        n = process_file(fname, mapping)
        print(f"{fname}: removed {n} ASCII blocks")
        total += n
    print(f"Total removed: {total}")


if __name__ == "__main__":
    main()
