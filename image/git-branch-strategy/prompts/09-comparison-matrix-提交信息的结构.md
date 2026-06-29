---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Table or matrix comparison layout
All visible text in Chinese (简体中文).
Content to visualize faithfully:
提交信息的结构:
<type>(<scope>): <subject>

[optional body]

[optional footer]


例如:
feat(auth): add OAuth 2.0 login support

Implemented Google and GitHub OAuth login.
Users can now sign in with their existing accounts.

Closes #123
BREAKING CHANGE: removed old password-based login endpoint


类型速查:
┌──────────┬──────────────────────────────────┐
│ feat     │ 新功能                            │
│ fix      │ bug 修复                          │
│ docs     │ 文档变更                          │
│ style    │ 格式变更（空格、分号等——不影响代码) │
│ refactor │ 重构（不修 bug、不加功能）          │
│ perf     │ 性能优化                          │
│ test     │ 添加或修改测试                     │
│ chore    │ 构建/工具/依赖变更                 │
│ ci       │ CI 配置变更                       │
│ revert   │ 回滚之前的提交                     │
└──────────┴──────────────────────────────────┘

常见 scope 示例:
feat(api): add user export endpoint
fix(db): resolve connection pool exhaustion
refactor(core): simplify event processing pipeline
docs(readme): add setup instructions