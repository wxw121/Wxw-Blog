# -*- coding: utf-8 -*-
"""Semantic audit: image alt vs nearest section heading."""
import re, json

manifest = json.load(open("image/manifest.json", encoding="utf-8"))

def nearest_heading(text, pos):
    h = "?"
    for m in re.finditer(r"^(#{1,4})\s+(.+)$", text[:pos], re.M):
        h = m.group(2).strip()
    return h

def section_chain(text, pos):
    chain = []
    for m in re.finditer(r"^(#{1,4})\s+(.+)$", text[:pos], re.M):
        level = len(m.group(1))
        title = m.group(2).strip()
        while chain and chain[-1][0] >= level:
            chain.pop()
        chain.append((level, title))
    return " > ".join(t for _, t in chain[-3:])

issues = []
for m in manifest:
    f = m["file"]
    if not re.match(r"^[1-9]", f):
        continue
    text = open(f, encoding="utf-8").read()
    path = m["img_path"]
    pos = text.find(path)
    if pos < 0:
        issues.append((f, path, "MISSING", m.get("alt", "")[:40]))
        continue
    chain = section_chain(text, pos)
    alt = (m.get("alt") or m.get("preview") or "").strip()
    # flag if alt keywords completely absent from chain (rough heuristic)
    keywords = re.findall(r"[\u4e00-\u9fffA-Za-z]{2,}", alt)
    keywords = [k for k in keywords if len(k) >= 2 and k not in ("png", "HTTP", "API", "URL")]
    hits = sum(1 for k in keywords[:6] if k.lower() in chain.lower() or k in chain)
    if keywords and hits == 0 and len(keywords) >= 2:
        issues.append((f, path.split("/")[-1], "SEMANTIC?", chain[:80], alt[:50]))

print("=== MISSING ===")
for row in issues:
    if row[2] == "MISSING":
        print(f"{row[0]}: {row[1]}")

print("\n=== POSSIBLE SEMANTIC MISMATCH ===")
for row in issues:
    if row[2] == "SEMANTIC?":
        print(f"{row[0]} | {row[1]}")
        print(f"  section: {row[3]}")
        print(f"  alt: {row[4]}")
        print()
