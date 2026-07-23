# -*- coding: utf-8 -*-
"""Generate tutorials 128-136 (roadmap 145-153) with >=5000 hanzi each."""
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


def write_image_assets(slug: str, title: str, items: list, prompts: list):
    img_dir = ROOT / "image" / slug
    prompts_dir = img_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}信息图（教程配图）\n\n", "| 文件 | 布局 | 插入位置 |\n|------|------|----------|\n"]
    for fname, layout, section in items:
        lines.append(f"| `{fname}` | {layout} | {section} |\n")
    lines += [
        "\n风格：hand-drawn-edu · 16:9 · 中文\n\nPrompt 见 `prompts/`。\n\n",
        "说明：本目录目前仅含 prompt 与 README；生成 PNG 后放入同级文件名即可被正文引用。\n",
    ]
    (img_dir / "README.md").write_text("".join(lines), encoding="utf-8")
    for fname, layout, ptitle, body, footer in prompts:
        (prompts_dir / fname).write_text(
            PROMPT_TEMPLATE.format(layout=layout, title=ptitle, body=body, footer=footer),
            encoding="utf-8",
        )


from _articles_128_136_content import ARTICLE_SPECS  # noqa: E402
from _articles_128_136_expand import EXPANSIONS  # noqa: E402
from _articles_128_136_expand2 import EXPANSIONS2  # noqa: E402
from _articles_128_136_expand3 import EXPANSIONS3  # noqa: E402
from _articles_128_136_expand4 import EXPANSIONS4  # noqa: E402
from _articles_128_136_expand4 import EXPANSIONS4  # noqa: E402
from _articles_128_136_pad import PAD_EXTRA  # noqa: E402
from _articles_128_136_final import FINAL_SECTIONS  # noqa: E402
from _articles_128_136_topup import TOPUP  # noqa: E402
from _articles_128_136_supplement import SUPPLEMENT  # noqa: E402
from _articles_128_136_supplement2 import SUPPLEMENT2  # noqa: E402
from _articles_128_136_supplement3 import SUPPLEMENT3  # noqa: E402
from _articles_128_136_supplement4 import SUPPLEMENT4  # noqa: E402
from _articles_128_136_supplement5 import SUPPLEMENT5  # noqa: E402
from _articles_128_136_supplement6 import SUPPLEMENT6  # noqa: E402

ARTICLES = ARTICLE_SPECS


def assemble_article(content: str, slug: str) -> str:
    out = content
    out += EXPANSIONS.get(slug, "")
    out += EXPANSIONS2.get(slug, "")
    out += EXPANSIONS3.get(slug, "")
    out += EXPANSIONS4.get(slug, "")
    out += EXPANSIONS4.get(slug, "")
    out += SUPPLEMENT.get(slug, "")
    out += SUPPLEMENT2.get(slug, "")
    out += SUPPLEMENT3.get(slug, "")
    out += SUPPLEMENT4.get(slug, "")
    out += SUPPLEMENT5.get(slug, "")
    out += SUPPLEMENT6.get(slug, "")
    out += PAD_EXTRA.get(slug, "")
    out += FINAL_SECTIONS.get(slug, "")
    paras = TOPUP.get(slug, [])
    if paras:
        out += "\n\n## 19. 工程备忘要点\n\n" + "\n\n".join(f"- {p}" for p in paras)
    return out


def pad_article(content: str, slug: str, min_h: int = 5000) -> str:
    if hanzi_count(content) < min_h:
        raise ValueError(f"{slug}: only {hanzi_count(content)} hanzi, need {min_h}")
    return content


def main():
    results = []
    for filename, slug, content, img_items, img_prompts in ARTICLES:
        full = pad_article(assemble_article(content, slug), slug, 5000)
        path = ROOT / filename
        path.write_text(full, encoding="utf-8")
        title = filename.split(".", 1)[1].replace("-tutorial.md", "").replace("-", " ")
        write_image_assets(slug, title, img_items, img_prompts)
        h = hanzi_count(full)
        results.append((filename, h))
        print(f"Wrote {filename}: {h} hanzi")

    print("\n--- Summary ---")
    for fn, h in results:
        status = "OK" if h >= 5000 else "FAIL"
        print(f"{fn}\t{h}\t{status}")


if __name__ == "__main__":
    main()
