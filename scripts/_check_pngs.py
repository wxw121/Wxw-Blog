from pathlib import Path

root = Path(__file__).resolve().parents[1] / "image"
for d in sorted(root.iterdir()):
    if not d.is_dir():
        continue
    pngs = list(d.glob("*.png"))
    prompts = d / "prompts"
    if pngs and prompts.exists():
        n_md = len(list(prompts.glob("*.md")))
        print(f"{d.name}: {len(pngs)} pngs, {n_md} prompts")
