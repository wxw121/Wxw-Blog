#!/usr/bin/env python3
"""Copy slug__filename.png assets to image/{slug}/{filename}.png"""
import shutil
import sys
from pathlib import Path

ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
ROOT = Path(__file__).resolve().parents[1]


def copy_slug_asset(slug: str, png: str) -> bool:
    src = ASSETS / f"{slug}__{png}"
    if not src.exists():
        src = ASSETS / png
    dst = ROOT / "image" / slug / png
    if not src.exists():
        print(f"MISSING {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"OK {slug}/{png}")
    return True


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        slug, png = arg.split(":", 1)
        copy_slug_asset(slug, png)
