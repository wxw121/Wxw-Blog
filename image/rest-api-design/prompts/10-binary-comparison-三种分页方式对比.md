---
layout: binary-comparison
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Side-by-side A vs B comparison layout with vertical divider
All visible text in Chinese (简体中文).
Content to visualize faithfully:
        三种分页方式对比

┌──────────┬────────────┬────────────┬────────────┐
│          │  页码式     │  游标式     │  偏移量式   │
├──────────┼────────────┼────────────┼────────────┤
│ 实现难度  │ 简单        │ 中          │ 简单        │
│ 跳页      │ ✅ 可跳到   │ ❌ 只能     │ ✅ 可跳     │
│          │   第 N 页   │   下一页     │             │
│ 实时数据  │ ❌ 新增数据  │ ✅ 不受影响  │ ❌ 会重复    │
│          │   导致重复   │             │             │
│ 性能      │ 大页码慢    │ 很快         │ 大偏移慢    │
│ 适用场景  │ 管理后台    │ 信息流/时间线 │ 简单列表    │
└──────────┴────────────┴────────────┴────────────┘