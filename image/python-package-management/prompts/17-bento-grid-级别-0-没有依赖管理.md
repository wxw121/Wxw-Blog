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
  级别 0: 没有依赖管理
  ┌─────────────────────────────────────┐
  │ pip install 随手装，不记录依赖      │
  │ "在我电脑上运行就行"                 │
  └─────────────────────────────────────┘

  级别 1: requirements.txt
  ┌─────────────────────────────────────┐
  │ pip freeze > requirements.txt       │
  │ 版本锁定了，但依赖来源不清楚         │
  └─────────────────────────────────────┘

  级别 2: 分离直接/间接依赖
  ┌─────────────────────────────────────┐
  │ requirements.in + pip-compile       │
  │ 知道谁引进了谁，开始有锁文件概念     │
  └─────────────────────────────────────┘

  级别 3: 锁文件 + 校验
  ┌─────────────────────────────────────┐
  │ Poetry / uv + lock 文件             │
  │ 版本 + 哈希双重锁定，可复现         │
  └─────────────────────────────────────┘

  级别 4: 全方位供应链安全
  ┌─────────────────────────────────────┐
  │ 级别 3 + pip-audit + 私有源 +       │
  │ SBOM 生成 + 依赖审查策略            │
  │ 知道每个依赖是干什么的，信任但验证    │
  └─────────────────────────────────────┘