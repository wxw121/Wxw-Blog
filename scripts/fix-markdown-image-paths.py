"""Fix markdown image paths to match image/manifest.json."""
import json
import os
import re

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    with open(os.path.join(BLOG, "image", "_inventory.json"), encoding="utf-8") as f:
        inventory = json.load(f)
    with open(os.path.join(BLOG, "image", "manifest.json"), encoding="utf-8") as f:
        manifest_by_key = {(m["file"], m["start"]): m for m in json.load(f)}

    replacements: dict[str, str] = {}
    for item in inventory:
        key = (item["file"], item["start"])
        if key not in manifest_by_key:
            continue
        m = manifest_by_key[key]
        wrong = item["img_path"]
        right = m["img_path"]
        if wrong != right:
            replacements[wrong] = right
        item["img_path"] = right
        item["alt"] = m.get("alt", item.get("alt", "示意图"))

    with open(os.path.join(BLOG, "image", "_inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    for fname in sorted({i["file"] for i in inventory}):
        path = os.path.join(BLOG, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        original = text
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        # fix generic 示意图 alt using inventory order per file
        for item in inventory:
            if item["file"] != fname:
                continue
            alt = item.get("alt", "示意图")
            # replace first remaining generic 示意图 for this file's path
            generic = f"![示意图]({item['img_path']})"
            specific = f"![{alt}]({item['img_path']})"
            if generic in text:
                text = text.replace(generic, specific, 1)
        if text != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"fixed {fname}")


if __name__ == "__main__":
    main()
