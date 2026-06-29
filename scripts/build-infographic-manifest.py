"""Build manifest of unique infographic images from _inventory.json."""
import json
import os
import re

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOPIC_DIR = {
    "python-virtual-env-tutorial": "python-virtual-env",
    "python-type-annotation-tutorial": "python-type-annotation",
    "python-asyncio-tutorial": "python-asyncio",
    "python-package-management-tutorial": "python-package-management",
    "rest-api-design-tutorial": "rest-api-design",
    "websocket-tutorial": "websocket",
    "sse-tutorial": "sse",
    "postgresql-tutorial": "postgresql",
    "git-branch-strategy-tutorial": "git-branch-strategy",
}

EXISTING = {
    ("3.python-asyncio-tutorial.md", 53): "image/python-asyncio/01-binary-comparison-sync-async.png",
    ("3.python-asyncio-tutorial.md", 70): "image/python-asyncio/01-binary-comparison-sync-async.png",
    ("3.python-asyncio-tutorial.md", 106): "image/python-asyncio/02-bento-grid-kitchen-analogy.png",
    ("3.python-asyncio-tutorial.md", 117): "image/python-asyncio/02-bento-grid-kitchen-analogy.png",
    ("3.python-asyncio-tutorial.md", 129): "image/python-asyncio/02-bento-grid-kitchen-analogy.png",
    ("3.python-asyncio-tutorial.md", 154): "image/python-asyncio/03-tree-branching-when-async.png",
    ("3.python-asyncio-tutorial.md", 203): "image/python-asyncio/04-linear-progression-coroutine-lifecycle.png",
    ("3.python-asyncio-tutorial.md", 375): "image/python-asyncio/05-hub-spoke-event-loop.png",
    ("2.python-type-annotation-tutorial.md", 1219): "image/python-type-annotation/06-framework-data-model-choice.png",
}

STYLE = """hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace."""


def alt_text(content: str) -> str:
    for line in content.splitlines():
        s = line.strip().strip("┌┐└┘│─ ")
        if s and not s.startswith("│"):
            return s[:80]
    return "示意图"


def build_prompt(item: dict) -> str:
    layout = item["layout"]
    layout_hints = {
        "binary-comparison": "Side-by-side A vs B comparison layout with vertical divider",
        "tree-branching": "Decision tree branching from root question to leaves",
        "linear-progression": "Left-to-right or top-to-bottom process timeline",
        "hub-spoke": "Central hub with connected spokes/nodes",
        "bento-grid": "Multi-panel bento grid overview",
        "comparison-matrix": "Table or matrix comparison layout",
    }
    hint = layout_hints.get(layout, "Educational infographic layout")
    return (
        f"Educational infographic in {STYLE}\n"
        f"Layout: {hint}\n"
        f"All visible text in Chinese (简体中文).\n"
        f"Content to visualize faithfully:\n{item['content']}"
    )


def main():
    inv_path = os.path.join(BLOG, "image", "_inventory.json")
    with open(inv_path, encoding="utf-8") as f:
        items = json.load(f)

    counters: dict[str, int] = {}
    unique: dict[str, dict] = {}

    for item in items:
        key = (item["file"], item["start"])
        if key in EXISTING:
            item["img_path"] = EXISTING[key]
        else:
            d = TOPIC_DIR.get(item["topic"], item["topic"])
            counters[d] = counters.get(d, 0) + 1
            n = counters[d]
            slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", item["preview"][:25]).strip("-")[:30]
            slug = slug or f"diagram-{n:02d}"
            item["img_path"] = f"image/{d}/{n:02d}-{item['layout']}-{slug}.png"

        path = item["img_path"]
        if path not in unique:
            item["alt"] = alt_text(item["content"])
            item["prompt"] = build_prompt(item)
            unique[path] = item

    manifest = sorted(unique.values(), key=lambda x: x["img_path"])
    out = os.path.join(BLOG, "image", "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    for item in manifest:
        d = os.path.dirname(os.path.join(BLOG, item["img_path"]))
        os.makedirs(d, exist_ok=True)
        prompt_dir = os.path.join(d, "prompts")
        os.makedirs(prompt_dir, exist_ok=True)
        base = os.path.basename(item["img_path"]).replace(".png", ".md")
        with open(os.path.join(prompt_dir, base), "w", encoding="utf-8") as f:
            f.write(f"---\nlayout: {item['layout']}\nstyle: hand-drawn-edu\naspect: 16:9\nlanguage: zh\n---\n\n")
            f.write(item["prompt"])

    print(f"Manifest: {len(manifest)} unique images -> {out}")


if __name__ == "__main__":
    main()
