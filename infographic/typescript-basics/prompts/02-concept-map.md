---
layout: bento-grid
style: hand-drawn-edu
aspect_ratio: 16:9
language: zh
---

Create a professional educational infographic, 16:9 landscape.

Layout: bento-grid — 11 compact module cells in a 3×4 grid (last row 3 cells centered), each cell is one concept card.

Style: hand-drawn-edu — macaron pastel rounded cards on warm cream (#F5F0E8), wavy dashed borders, hand-lettered Chinese, code snippets in doodle monospace boxes, coral red (#E8655A) for code highlights.

Title (top center): 综合概念地图：本章名词一览

Subhead: 类型是你对数据的承诺，不是服务器的承诺

Grid cells (each: code snippet + 正式名称 + 通俗说, compact):
1. `: string` — 类型注解 — 这个变量是字符串
2. `string | number` — 联合类型 — 二选一
3. `"a" | "b"` — 字面量联合 — 只能是这几个值
4. `interface Foo { }` — 接口 — 对象字段清单
5. `type Foo = ...` — 类型别名 — 给类型起名
6. `T[]` / `Array<T>` — 泛型数组 — 同类型列表
7. `[A, B]` — 元组 — 固定列类型
8. `<T>` — 泛型参数 — 类型的占位符
9. `as Type` — 类型断言 — 你保证是这个类型
10. `x is Foo` — 类型守卫 — 判断后收窄
11. `?:` — 可选 — 可以没有

Use distinct macaron colors per row (blue, mint, lavender, peach). Small stick figure with magnifying glass in corner.

Footer: TypeScript 基础完全指南 · §14

All text Simplified Chinese. Dense but organized, each cell readable. Hand-drawn wobble on all lines.
