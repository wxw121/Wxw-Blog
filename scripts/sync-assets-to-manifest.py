"""Copy any asset whose basename matches a manifest img_path basename."""
import json
import os
import shutil

BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 生成图资产目录，默认 <仓库>/assets；也可用环境变量 BLOG_ASSETS_DIR 覆盖
ASSETS = os.environ.get("BLOG_ASSETS_DIR", os.path.join(BLOG, "assets"))


def main():
    with open(os.path.join(BLOG, "image", "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    by_base = {os.path.basename(item["img_path"]): item["img_path"] for item in manifest}
    copied = 0
    if not os.path.isdir(ASSETS):
        print("No assets dir")
        return
    for name in os.listdir(ASSETS):
        if not name.lower().endswith(".png"):
            continue
        if name not in by_base:
            continue
        src = os.path.join(ASSETS, name)
        dst = os.path.join(BLOG, by_base[name])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        print(f"OK {by_base[name]}")
    print(f"Copied {copied} by basename match")


if __name__ == "__main__":
    main()
