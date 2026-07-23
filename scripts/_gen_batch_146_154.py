# -*- coding: utf-8 -*-
"""Generate tutorials 146-154 (roadmap 163-171) with >=5000 hanzi each."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

PROMPT_TEMPLATE = """---
layout: {layout}
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.
Layout: {layout}.
Style: hand-drawn-edu, cream #F5F0E8, macaron pastels, stick figures, Simplified Chinese.

Title: {title}

{body}

Footer: {footer}

All text Simplified Chinese.
"""


def hanzi_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def write_image_assets(slug: str, title: str, items: list[tuple[str, str, str]]):
    img_dir = ROOT / "image" / slug
    prompts_dir = img_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}信息图（教程配图）\n",
        "\n| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n",
    ]
    for fname, layout, section in items:
        lines.append(f"| `{fname}` | {layout} | {section} |\n")
    lines += [
        "\n风格：hand-drawn-edu · 16:9 · 中文\n\nPrompt 见 `prompts/`。\n\n",
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
    ]
    (img_dir / "README.md").write_text("".join(lines), encoding="utf-8")


def write_prompts(slug: str, prompts: list[tuple[str, str, str, str, str]]):
    for fname, layout, title, body, footer in prompts:
        path = ROOT / "image" / slug / "prompts" / fname
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            PROMPT_TEMPLATE.format(layout=layout, title=title, body=body, footer=footer),
            encoding="utf-8",
        )




# Import article bodies from companion module


def main():
    from _articles_146_154_content import ARTICLES  # noqa: E402

    counts = {}
    for fname, slug, title, body, img_items, prompt_items in ARTICLES:
        content = body
        n = hanzi_count(content)
        if n < 5000:
            raise ValueError(f"{fname}: only {n} hanzi, need 5000")
        (ROOT / fname).write_text(content, encoding="utf-8")
        write_image_assets(slug, title, img_items)
        write_prompts(slug, prompt_items)
        counts[fname] = n
    print("| File | Roadmap | Slug | Hanzi | Status |")
    print("|------|---------|------|-------|--------|")
    roadmap = {
        "146.trulens-tutorial.md": (163, "trulens"),
        "147.langsmith-tracing-tutorial.md": (164, "langsmith-tracing"),
        "148.langfuse-observability-tutorial.md": (165, "langfuse-observability"),
        "149.bad-case-parsing-tutorial.md": (166, "bad-case-parsing"),
        "150.bad-case-chunking-tutorial.md": (167, "bad-case-chunking"),
        "151.bad-case-retrieval-miss-tutorial.md": (168, "bad-case-retrieval-miss"),
        "152.bad-case-hallucination-tutorial.md": (169, "bad-case-hallucination"),
        "153.ab-experiment-rag-tutorial.md": (170, "ab-experiment-rag"),
        "154.param-version-management-tutorial.md": (171, "param-version-management"),
    }
    for k, v in sorted(counts.items()):
        rm, slug = roadmap[k]
        status = "OK" if v >= 5000 else "LOW"
        print(f"| {k} | {rm} | {slug} | {v} | {status} |")
    return counts


if __name__ == "__main__":
    main()
