---
layout: tree-branching
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Decision tree branching from root question to leaves
All visible text in Chinese (简体中文).
Content to visualize faithfully:
你需要运行时验证？
  ├── 是 → Pydantic BaseModel
  └── 否 → 数据是字典格式？
            ├── 是 → 需要给 IDE 提供键名提示？
            │       ├── 是 → TypedDict
            │       └── 否 → 普通 dict
            └── 否（是类）→ 需要可变还是不可变？
                          ├── 可变 → dataclass
                          └── 不可变 → 大部分场景: dataclass(frozen=True)
                                      需要哈希: NamedTuple
                                      配置项: Pydantic BaseModel(frozen=True)