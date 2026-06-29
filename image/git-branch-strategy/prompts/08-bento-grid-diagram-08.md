---
layout: bento-grid
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Multi-panel bento grid overview
All visible text in Chinese (简体中文).
Content to visualize faithfully:
┌─────────────────────────────────────────────────────────┐
│                  Code Review 评论速查                     │
│                                                         │
│  🔴 blocking (必须修):                                   │
│  • 逻辑错误——边界条件处理不对                            │
│  • 安全漏洞——SQL 注入、XSS、未验证的输入                  │
│  • 数据丢失风险——缺少迁移、删除而非软删除                 │
│  • 阻塞性——合并后会破坏已有功能                           │
│                                                         │
│  🟡 important (应该修):                                  │
│  • N+1 查询、内存泄漏等性能问题                           │
│  • 复杂难懂的逻辑——6 个月后没人看得懂                    │
│  • 缺少关键测试                                         │
│  • 硬编码的魔法数字                                     │
│                                                         │
│  🟢 suggestion (建议修):                                │
│  • 变量名可以更好                                       │
│  • 代码可以更简洁（但不影响功能）                         │
│  • 可以复用已有的工具函数                                │
│  • 注释可以更清晰                                       │
│                                                         │
│  💬 question (讨论):                                    │
│  • 「为什么选择方案 A 而非方案 B？」                     │
│  • 「这里考虑过用缓存吗？」                             │
│  • 纯探讨——没有对错                                      │
│                                                         │
│  审查者守则: 一个 PR 的 blocking 评论不超过 3 条          │
│  如果超过了→说明这个 PR 可能需要重新设计                  │
│                                                         │
│  提交者守则: blocking 评论 → 必须修复                    │
│             suggestion 评论 → 可以回复解释为什么不改       │
│             但至少读过并思考过                             │
└─────────────────────────────────────────────────────────┘