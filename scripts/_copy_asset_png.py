#!/usr/bin/env python3
"""Copy generated PNG from Cursor assets to image/{slug}/."""
import shutil
import sys
from pathlib import Path

ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
ROOT = Path(__file__).resolve().parents[1]


def copy(slug: str, png: str, src_name: str | None = None) -> bool:
    src = ASSETS / (src_name or png)
    dst = ROOT / "image" / slug / png
    if not src.exists():
        print(f"MISSING {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"OK {dst.relative_to(ROOT)}")
    return True


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        parts = arg.split(":")
        if len(parts) == 2:
            copy(parts[0], parts[1])
        elif len(parts) == 3:
            copy(parts[0], parts[1], parts[2])
        else:
            print(f"BAD ARG {arg}")
