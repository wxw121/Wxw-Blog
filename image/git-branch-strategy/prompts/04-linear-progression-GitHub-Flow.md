---
layout: linear-progression
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Left-to-right or top-to-bottom process timeline
All visible text in Chinese (简体中文).
Content to visualize faithfully:
                      GitHub Flow

    main    ○────○────○────○────○────○────○────▶
            │\   │\   │\   │\   │\   │\   │
            │ \  │ \  │ \  │ \  │ \  │ \  │
    branch  │  ○─┤  ○─┤  ○─┤  ○─┤  ○─┤  ○─┤
            │    │    │    │    │    │    │
            │ featureA │ featureB │ hotfix  │
            │    │     │    │     │    │    │
            部署  审查  部署  审查  审查  部署

    每条规则:
    1. main 的任何东西都可以部署（main = 生产就绪）
    2. 新工作从 main 分出描述性分支
    3. 本地提交，定期 push 到同名远程分支
    4. 需要反馈/审查/合并时，开 Pull Request
    5. PR 审查通过、CI 全绿后合并到 main
    6. 合并后立即部署（或至少保证可以部署）