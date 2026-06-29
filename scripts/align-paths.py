"""Align _inventory img_path with manifest and fix markdown image references."""
import json
import os
import re

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    inv_path = os.path.join(BLOG, "image", "_inventory.json")
    man_path = os.path.join(BLOG, "image", "manifest.json")
    with open(inv_path, encoding="utf-8") as f:
        inventory = json.load(f)
    with open(man_path, encoding="utf-8") as f:
        manifest = {item["img_path"]: item for item in json.load(f)}

  # map inventory start -> manifest path by matching file+content
    man_by_key = {}
    for item in json.load(open(man_path, encoding="utf-8")):
        man_by_key[(item["file"], item["start"])] = item

    for item in inventory:
        key = (item["file"], item["start"])
        if key in man_by_key:
            item["img_path"] = man_by_key[key]["img_path"]
            item["alt"] = man_by_key[key].get("alt", item.get("alt", "示意图"))

    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    # Fix markdown: replace wrong tutorial paths with manifest paths
    files = sorted({i["file"] for i in inventory})
    for fname in files:
        path = os.path.join(BLOG, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for item in inventory:
            if item["file"] != fname:
                continue
            old_patterns = [
                f"image/{item['topic']}/",
                f"image/{item['topic'].replace('-tutorial', '')}/",
            ]
            new = item["img_path"]
            for old_prefix in old_patterns:
                # replace any image under wrong prefix that was inserted as 示意图
                pass
        # replace generic tutorial folder refs for this file's items
        topic = inventory[0]["topic"]
        for item in inventory:
            if item["file"] != fname:
                continue
            wrong_prefix = f"image/{item['topic']}/"
            if wrong_prefix in text:
                text = text.replace(wrong_prefix, os.path.dirname(item["img_path"]) + "/")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Updated {fname}")


if __name__ == "__main__":
    main()
