#!/usr/bin/env python3
"""Batch-generate infographics: read prompts JSON, call image API via subprocess if available."""
import json
import shutil
import sys
from pathlib import Path

ASSETS = Path(r"C:\Users\Wxw\.cursor\projects\d-software-cld-project-blog\assets")
ROOT = Path(__file__).resolve().parents[1]


def copy_asset(slug: str, png: str, asset_name: str | None = None) -> bool:
    src = ASSETS / (asset_name or png)
    dst = ROOT / "image" / slug / png
    if not src.exists():
        print(f"MISSING {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"OK {slug}/{png}")
    return True


def status(min_n: int = 160, max_n: int = 179) -> dict:
    data = json.loads((ROOT / "scripts" / "_pending_160_179.json").read_text(encoding="utf-8"))
    total = len(data) + 1  # +1 for already done 01-three-way-compare
    done = 0
    for item in data:
        if (ROOT / "image" / item["slug"] / item["png"]).exists():
            done += 1
    # count 01-three-way-compare
    if (ROOT / "image" / "bull-arq-node-queue" / "01-three-way-compare.png").exists():
        done += 1
    return {"total": 64, "done": done, "remaining": 64 - done}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        s = status()
        print(json.dumps(s))
    elif len(sys.argv) > 2 and sys.argv[1] == "copy":
        # copy slug:png[:asset_name] ...
        for arg in sys.argv[2:]:
            parts = arg.split(":")
            slug, png = parts[0], parts[1]
            asset = parts[2] if len(parts) > 2 else None
            copy_asset(slug, png, asset)
