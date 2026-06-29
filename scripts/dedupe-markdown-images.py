"""Deduplicate markdown image lines and drop stale tutorial-folder paths."""
import os
import re

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clean_file(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    out: list[str] = []
    seen_paths: set[str] = set()
    removed = 0
    img_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

    for line in lines:
        m = img_re.search(line)
        if m:
            img_path = m.group(1)
            if "-tutorial/" in img_path or img_path.count("/image/") > 0:
                removed += 1
                continue
            if img_path in seen_paths:
                removed += 1
                continue
            seen_paths.add(img_path)
        out.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out)
    return removed


def main():
    for name in os.listdir(BLOG):
        if re.match(r"^[1-9].*\.md$", name):
            n = clean_file(os.path.join(BLOG, name))
            if n:
                print(f"{name}: removed {n} duplicate/stale image lines")


if __name__ == "__main__":
    main()
