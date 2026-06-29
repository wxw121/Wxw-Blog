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
                    Pull Request 生命周期

    1. 创建分支
       │
       ▼
    2. 开发 + 提交
       │
       ▼
    3. 推送分支 ──────────┐
       │                  │
       ▼                  │ (继续开发)
    4. 创建 PR            │
       │                  │
       ├─ Draft PR（WIP）─┘
       │
       ▼
    5. 转为正式 PR
       │
       ▼
    6. CI 检查 (Lint → Test → Build)
       │
       ├─── 失败 → 修复 → 重新提交 → 返回 6
       │
       ▼
    7. Code Review
       │
       ├─── 需要修改 → 修改 → 返回 7
       │
       ▼
    8. 审查通过 ✓
       │
       ▼
    9. 合并到主干
       │
       ▼
   10. 自动部署（或手动发布）
       │
       ▼
   11. 删除分支

   每个阶段都是团队协作的一个「检查点」