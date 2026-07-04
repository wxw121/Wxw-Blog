"""Compare image section placement: current vs initial commit."""
import re, subprocess, json

INITIAL = "29c4828"  # original; use 7b159aa for polish baseline

def extract(path: str, text: str) -> list[dict]:
    out = []
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", text):
        pos = m.start()
        heading = "?"
        for hm in re.finditer(r"^(#{1,4})\s+(.+)$", text[:pos], re.M):
            heading = hm.group(2).strip()
        out.append({"path": m.group(2), "alt": m.group(1), "heading": heading})
    return out

def git_show(commit: str, path: str) -> str:
    r = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout if r.returncode == 0 else ""

manifest = json.load(open("image/manifest.json", encoding="utf-8"))
files = sorted({m["file"] for m in manifest if re.match(r"^[1-9]", m["file"])})

moved = []
for f in files:
    cur = extract(f, open(f, encoding="utf-8").read())
    old = extract(f, git_show(INITIAL, f))
    old_by = {x["path"]: x for x in old}
    cur_by = {x["path"]: x for x in cur}
    for p, c in cur_by.items():
        o = old_by.get(p)
        if o and o["heading"] != c["heading"]:
            moved.append((f, p.split("/")[-1], o["heading"], c["heading"]))
    for p in old_by:
        if p not in cur_by:
            print(f"REMOVED {f}: {p}")
    for p in cur_by:
        if p not in old_by:
            print(f"ADDED   {f}: {p} -> {cur_by[p]['heading']}")

print("\n=== MOVED (initial -> current heading) ===")
for row in moved:
    print(f"{row[0]}")
    print(f"  {row[1]}")
    print(f"  was: {row[2]}")
    print(f"  now: {row[3]}")
    print()
